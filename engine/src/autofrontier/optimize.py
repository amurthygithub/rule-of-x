# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Program selection (spec Sections 9, 13.2, 14, 16): choose at most one plan (column) per process so as to
maximize the owner's risk-adjusted value, subject to the one-time budget, the dual-running budget, change
capacity, decision bandwidth, security-review capacity and, for leveraged owners, the debt covenant.

The objective of a selection X (one column c per chosen process):
  V(X) = sum_c [ PV0_c e^{-r ell(x_s)} + varpi_c(E) q(x_s) e^{-r_d ell(x_s)} f_sec(nu_y) PV1_c ]
         - sum_s O_w 1{launch in s} - sum_s d2 n_s^2 - compliance fixed costs - myopia penalty,
with x_s the decision load ratio of start year s (ext ass:ext-bandwidth), nu_y the security reviews of
adoption year y (core prop:tasks-secreview), varpi_c raised by experience E with decay and transfer
(ext ass:ext-portfolio) and n_s the processes launched in year s (ext eq:ext-progcost).

Two solvers share it: a greedy outer loop with local search (spec 9: process-level enumeration with a greedy
outer loop), and a MILP over columns (pulp/CBC) with load bands, used for small instances and as a check.
A MILP failure or timeout falls back to the heuristic."""
from __future__ import annotations

import math
import shutil
import tempfile
import time
from dataclasses import dataclass, field

import numpy as np
from scipy.special import expit

from . import formulas as F
from .plans import Columns, QPY


# -------------------------------------------------------------------------------------------------
# Regime valuation of columns
# -------------------------------------------------------------------------------------------------
@dataclass
class Regime:
    name: str
    r: float
    horizon: float | None        # years; None = going concern
    terminal: str                # going_concern, ebitda_multiple
    M_exit: float | None
    myopia: float
    myopia_years: int
    covenant: float | None
    leverage: float | None
    latency_mult: float
    budget_mult: float
    employment_pref: float       # owner value per job kept, share of the wage
    g_tv: float
    tv_cap: float
    info: dict = field(default_factory=dict)


def valuation(cols: Columns, reg: Regime, T: int, wage_by_col: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """PV0 and PV1 of every column under the regime: discount at r_own, cut at the hold period, terminal value by
    the regime's rule (going-concern multiple of the steady-state flow, or the exit EBITDA multiple), and the
    owner's employment preference as a cost per FTE removed."""
    Q = T * QPY
    tq = (np.arange(Q) + 0.5) / QPY
    H = T if reg.horizon is None else min(float(reg.horizon), T)
    keep = (tq <= H).astype(float)
    D = np.exp(-reg.r * tq) * keep
    pv0 = cols.cf0 @ D
    pv1 = cols.cf1 @ D
    if reg.terminal == "going_concern":
        g = min(reg.g_tv, reg.r - 0.01)
        mult = min(1.0 / (reg.r - g), reg.tv_cap)
        pv1 = pv1 + cols.tv1 * mult * math.exp(-reg.r * H)
    elif reg.terminal == "ebitda_multiple" and reg.M_exit:
        # exit rule (prop:reg-value): the buyer capitalizes the share h_x of the run-rate seasoned T_sea before exit;
        # a column whose cutover plus seasoning runs past the exit gets no terminal term
        hx = float(reg.info.get("h_x", 1.0))
        Tsea = float(reg.info.get("T_sea", 0.0))
        y = int(min(max(math.ceil(H - Tsea) - 1, 0), T - 1))
        Tpar = np.array([d["T_par"] for d in cols.detail]) if cols.detail else np.zeros(len(cols))
        seasoned = (cols.tau0 + Tpar + Tsea <= H).astype(float)
        mult = hx * reg.M_exit * math.exp(-reg.r * H) * seasoned
        pv0 = pv0 + mult * cols.ebitda0[:, y]
        pv1 = pv1 + mult * cols.ebitda1[:, y]
    if reg.employment_pref > 0 and wage_by_col is not None:
        yrs = np.arange(T) + 0.5
        Dy = np.exp(-reg.r * yrs) * (yrs <= H)
        pv1 = pv1 - reg.employment_pref * (cols.fte_removed * wage_by_col[:, None]) @ Dy
    return pv0, pv1


# -------------------------------------------------------------------------------------------------
# The program problem
# -------------------------------------------------------------------------------------------------
@dataclass
class Program:
    cols: Columns
    regime: Regime
    T: int
    pv0: np.ndarray
    pv1: np.ndarray
    budget: np.ndarray
    dual_budget: np.ndarray
    capacity: np.ndarray
    Phi: np.ndarray
    Phi_sec: np.ndarray
    load0: np.ndarray
    ell0: float
    r_d: float
    eta_q: float
    x_cap: float
    O_w: float
    d2: float
    compliance: np.ndarray         # (T,) PV of the firm-level compliance cost if AI is deployed from year y on
    gaap_base: np.ndarray          # (T,) baseline GAAP operating income (myopia)
    ebitda_base: np.ndarray        # (T,) baseline EBITDA (covenant)
    fcf_base: np.ndarray           # (T,) baseline free cash flow (covenant)
    net_debt0: float
    upsilon: float
    delta_E: float
    eta_tr: float
    platforms: np.ndarray          # (C,) platform index
    n_platforms: int
    by_proc: dict                  # process -> column indices
    info: dict = field(default_factory=dict)

    @property
    def C(self) -> int:
        return len(self.pv0)


def make_program(cols: Columns, econ, reg: Regime, p) -> Program:
    """Assemble the constraints and coefficients for one regime."""
    f = econ.firm
    T = econ.T
    S = f.part1["S"] * econ.vf
    org = f.org
    sh, d, cons, sec = p.shocks, p.decisions, p.constraints, p.security
    avail = F.freeze_availability(sh.nu_R, sh.T_frz) if sh.enabled else 1.0
    reorg_years = set(org.get("planned_reorgs") or [])
    planned = np.array([(f.base_year + y) in reorg_years for y in range(T)], float)
    freeze = 1.0 - planned * sh.T_frz
    budget = cons.budget_share * S * reg.budget_mult
    dual_budget = cons.dual_budget_share * S * reg.budget_mult
    fte_base = float(f.units.fte.values[(f.units.baseline == "H").values].sum())
    cap0 = float(org["change_capacity_fte"]) if org.get("change_capacity_fte") else F.change_capacity(cons.kappa_abs, fte_base)
    capacity = cap0 * avail * freeze * np.ones(T)
    gain = F.ai_bandwidth_gain(d.e_appr_share, 1 - d.e_appr_share, d.A_Phi)
    deleg = float(org.get("delegation", d.delegation))
    Phi0 = (d.Phi_base + d.phi_per_TO_fte * float(org.get("to_fte", d.transformation_office_fte))
            + d.phi_per_sponsor * float(org.get("sponsors", d.sponsors))) * (1 + d.delegation_uplift * deleg)
    if org.get("decisions_per_year"):
        Phi0 = float(org["decisions_per_year"]) * d.e_launch          # the firm's own bandwidth, in decision units
    Phi = Phi0 * avail * freeze * np.ones(T) * (1 + 0.0 * gain)
    load0 = np.zeros(T)
    conc = float(org.get("concurrent", d.concurrent_initiatives)) * d.e_launch
    load0[: max(int(math.ceil(d.existing_load_years)), 1)] = conc
    # security review capacity: input, or team FTE x reviews per FTE, or a prior per employee
    s_in = f.security or {}
    if s_in.get("reviews_per_year"):
        Phi_sec = float(s_in["reviews_per_year"])
    else:
        fte_sec = s_in.get("security_team_fte") or sec.reviewer_share * max(float(f.fin.get("headcount") or fte_base), 1.0)
        Phi_sec = float(fte_sec) * sec.reviews_per_fte
    Phi_sec = max(Phi_sec, 1.0) * np.ones(T)
    layers = float(org.get("layers", d.governance_layers))
    ell0 = (d.ell0_base_weeks + d.ell0_weeks_per_layer * layers) / 52.0 * reg.latency_mult
    r_d = reg.r + d.delta_V
    # firm-level compliance (spec 18.2): first-year and annual costs once any AI is deployed; certifications already
    # held are not counted again
    certs = str(s_in.get("certifications") or "").lower()
    rates = econ.rates
    first = ((0.0 if ("soc2" in certs or "soc 2" in certs) else sec.soc2_first_year)
             + (0.0 if "42001" in certs else sec.iso42001_readiness + sec.iso42001_audit)
             + sec.nist_rmf_initial_fte_months * rates["risk_governance_month"])
    annual = ((0.0 if ("soc2" in certs or "soc 2" in certs) else sec.soc2_annual)
              + (0.0 if "42001" in certs else sec.iso42001_annual)
              + sec.nist_rmf_ongoing_fte * rates["risk_governance_year"] + sec.ir_retainer
              + sec.cyber_insurance_share * float(S[0]) * 0.25          # AI share of the cyber premium (assumed a quarter)
              + float((org.get("jurisdiction") or {}).get("mechanism_annual_cost", 0.0)))   # nu^inv C^sw (prop:labor-residency(c))
    first = first + float((org.get("jurisdiction") or {}).get("mechanism_first_year_cost", 0.0))      # F^tr
    yrs = np.arange(T) + 0.5
    disc = np.exp(-reg.r * yrs) * (yrs <= (reg.horizon or T))
    tau = econ.info["tau"]
    compliance = np.array([(first * disc[y] + annual * disc[y + 1:].sum()) * (1 - tau) for y in range(T)])
    # post-quantum migration (spec 20.2): mandatory, dated, independent of the AI plan; it uses the same budget
    pq = p.pqc
    it_spend = float(org.get("it_spend") or 0.0) or pq.it_share_revenue * float(S[0])
    fed = bool(org.get("sells_to_us_government") or 0)
    deadline = (pq.federal_year if fed else pq.disallow_year) + 1.0
    mult = 1.0
    if pq.quantum_scenario:
        deadline, mult = min(deadline, pq.quantum_deadline + 1.0), pq.quantum_cost_mult
    pqc = F.pqc_cost_path(f.base_year + yrs, it_spend, pq.cost_share_it * mult, f.base_year, deadline, pq.inventory_years)
    budget = np.maximum(budget - pqc, 0.2 * budget)
    # baselines for myopia and covenants
    part1 = f.part1
    gaap_base = part1["m_op"] * S
    ebitda_base = (part1["m_op"] + (f.fin.get("da") or 0.0) / part1["S"]) * S
    fcf_base = part1["m_cash"] * S
    nd = f.fin.get("net_debt")
    if nd is None and reg.leverage:
        nd = reg.leverage * max(ebitda_base[0], 1.0)
    pv0, pv1 = valuation(cols, reg, T, wage_by_col=_wage_by_col(cols, econ))
    plats = {k: i for i, k in enumerate(sorted(set(cols.platform)))}
    by_proc: dict = {}
    for i, pr in enumerate(cols.proc):
        by_proc.setdefault(int(pr), []).append(i)
    mean_sav = float(np.median([dd["W"][min(dd["y0"] + 1, T - 1)] for dd in cols.detail])) if len(cols) else 0.0
    O_w = p.program.O_w_share * float(budget.mean())
    # survivor charge per announced wave (prop:labor-survivor(b)): O_s = w N^sv T_s (c^rep eta_0 + delta_0), with
    # N^sv the staff of the function a wave touches (mean over the functions with candidate plans)
    lb = p.labor
    Ut = f.units
    fte_f = Ut.groupby("function_id").fte.sum()
    funcs = {str(f.processes.function_id.iat[int(i)]) for i in set(cols.proc.tolist())} if len(cols) else set()
    inh = Ut[Ut.baseline == "H"] if "baseline" in Ut.columns else Ut       # survivors are in-house employees
    fte_f = inh.groupby("function_id").fte.sum()
    n_sv = float(fte_f[fte_f.index.astype(str).isin(funcs)].mean()) if funcs else 0.0
    w_year = float(np.median(econ.info["w"])) * p.labor.hours_per_fte
    O_s = float(F.survivor_wave_charge(n_sv if np.isfinite(n_sv) else 0.0, w_year, lb.T_s, lb.c_rep,
                                       lb.survivor_excess_quits / max(lb.T_s, 1e-9), lb.delta_eff))
    O_w = O_w + O_s
    d2 = p.program.d2_share * mean_sav * float(np.median([dd["T_par"] for dd in cols.detail])) if len(cols) else 0.0
    return Program(cols=cols, regime=reg, T=T, pv0=pv0, pv1=pv1, budget=budget, dual_budget=dual_budget, capacity=capacity,
                   Phi=Phi, Phi_sec=Phi_sec, load0=load0, ell0=ell0, r_d=r_d, eta_q=d.eta_q, x_cap=d.x_cap,
                   O_w=O_w * (1 - tau), d2=d2 * (1 - tau), compliance=compliance, gaap_base=gaap_base,
                   ebitda_base=ebitda_base, fcf_base=fcf_base, net_debt0=float(nd or 0.0),
                   upsilon=p.success.upsilon_L, delta_E=p.success.delta_E, eta_tr=p.success.eta_tr,
                   platforms=np.array([plats[x] for x in cols.platform], int), n_platforms=len(plats), by_proc=by_proc,
                   info={"S": S, "Phi0": Phi0, "avail": avail, "fte_base": fte_base, "annual_compliance": annual,
                         "first_year_compliance": first, "pqc": pqc, "pqc_deadline": deadline, "pqc_it_spend": it_spend,
                         "O_s": O_s, "O_w_base": O_w - O_s,
                         "x_hat": F.load_breakpoint(d.eta_q, ell0, r_d, d.x_cap)})


def _wage_by_col(cols: Columns, econ) -> np.ndarray:
    """Average annual loaded wage of the FTE a column removes (for the employment preference)."""
    w = econ.info["w"] * econ.p.labor.hours_per_fte
    nP = int(econ.unit_proc.max()) + 1 if econ.nU else 0
    tot = np.bincount(econ.unit_proc, weights=w, minlength=nP)
    cnt = np.maximum(np.bincount(econ.unit_proc, minlength=nP), 1)
    return (tot / cnt)[cols.proc] if len(cols) else np.zeros(0)


# -------------------------------------------------------------------------------------------------
# Objective
# -------------------------------------------------------------------------------------------------
@dataclass
class State:
    """Aggregates of a selection, for fast evaluation of one process's alternatives."""
    sel: dict                       # process -> column index
    varpi: np.ndarray               # (C,) success probabilities given experience


def experience(prog: Program, sel: dict, varpi: np.ndarray) -> np.ndarray:
    """Experience stock by platform and start year: expected successes of earlier launches, decaying at delta_E a
    year, with full credit on the same platform and eta_tr across platforms (ext ass:ext-portfolio)."""
    T, nP = prog.T, prog.n_platforms
    succ = np.zeros((nP, T))
    for c in sel.values():
        succ[prog.platforms[c], prog.cols.start[c]] += varpi[c]
    E = np.zeros((nP, T))
    cur = np.zeros(nP)
    for y in range(T):
        E[:, y] = cur + prog.eta_tr * (cur.sum() - cur)
        cur = (1 - prog.delta_E) * cur + succ[:, y]
    return E


def varpi_given(prog: Program, E: np.ndarray) -> np.ndarray:
    cols = prog.cols
    return expit(F.learning_logit(cols.logit0, prog.upsilon, E[prog.platforms, cols.start]))


def evaluate(prog: Program, sel: dict, varpi: np.ndarray, detail: bool = False) -> dict:
    """Exact objective and constraint check of a selection."""
    idx = np.array(sorted(sel.values()), int)
    return _eval_many(prog, idx, varpi, cand=None, detail=detail)


def _eval_many(prog: Program, base_idx: np.ndarray, varpi: np.ndarray, cand: np.ndarray | None, detail=False):
    """Objective of base_idx plus each candidate column (or of base_idx alone if cand is None). Vectorized over
    candidates: returns arrays over candidates."""
    cols, T = prog.cols, prog.T
    k = 1 if cand is None else len(cand)
    single = cand is None

    def agg(arr):
        base = arr[base_idx].sum(0) if len(base_idx) else np.zeros(arr.shape[1:])
        if single:
            return base[None]
        return base[None] + arr[cand]

    load = prog.load0[None] + agg(cols.load)                                # (k, T)
    nu = agg(cols.reviews)
    bud = agg(cols.budget)
    dual = agg(cols.dual)
    cap = agg(cols.affected)
    x = load / prog.Phi[None]
    ell = F.decision_latency(x, prog.ell0, prog.x_cap)
    fd0 = np.exp(-prog.regime.r * ell)
    fd1 = F.congestion_q(x, prog.eta_q) * np.exp(-prog.r_d * ell)
    fsec = F.review_retained_share(prog.Phi_sec[None], nu, prog.r_d)
    s_all = cols.start
    ya_all = np.minimum(cols.tau0.astype(int), T - 1)

    # value of the base columns under each candidate's latency and review congestion, vectorized: the base enters
    # through its start-year sums (P0) and its (start, adoption-year) sums (M1)
    vals = np.zeros(k)
    if len(base_idx):
        sb, yb = s_all[base_idx], ya_all[base_idx]
        P0 = np.bincount(sb, weights=prog.pv0[base_idx], minlength=T)
        M1 = np.zeros((T, T))
        np.add.at(M1, (sb, yb), varpi[base_idx] * prog.pv1[base_idx])
        vals += fd0 @ P0
        vals += np.einsum("st,ks,kt->k", M1, fd1, fsec)
    if not single:
        sc_, yc = s_all[cand], ya_all[cand]
        rows_ = np.arange(k)
        vals += prog.pv0[cand] * fd0[rows_, sc_] + varpi[cand] * prog.pv1[cand] * fd1[rows_, sc_] * fsec[rows_, yc]
    launches = np.zeros((k, T))
    if len(base_idx):
        np.add.at(launches, (slice(None), s_all[base_idx]), 1.0)
    if not single:
        launches[np.arange(k), s_all[cand]] += 1.0
    D = np.exp(-prog.regime.r * (np.arange(T) + 0.5))
    waves = (launches > 0).astype(float)
    vals -= (waves * prog.O_w * D[None]).sum(1)
    vals -= (prog.d2 * launches ** 2 * D[None]).sum(1)
    # compliance: from the first year any AI is deployed
    has_ai = cols.has_ai
    first = np.full(k, T)
    if len(base_idx):
        b_ai = base_idx[has_ai[base_idx]]
        if len(b_ai):
            first[:] = int(ya_all[b_ai].min())
    if not single:
        c_ai = has_ai[cand]
        first = np.where(c_ai, np.minimum(first, ya_all[cand]), first)
    vals -= np.where(first < T, prog.compliance[np.minimum(first, T - 1)], 0.0)
    # myopia penalty on expected GAAP earnings dips (spec 16.1)
    reg = prog.regime
    g_exp = cols.gaap0 + varpi[:, None] * cols.gaap1
    G = agg(g_exp)
    pen = np.zeros(k)
    if reg.myopia > 0:                       # prop:reg-value(a): dips beyond the guided slack in the first Y_m years
        yrs = np.arange(min(reg.myopia_years, T))
        slack = float(reg.info.get("g_slack", 0.0)) * prog.info.get("S", np.zeros(T))[yrs]
        pen = reg.myopia * (np.exp(-reg.r * (yrs + 1.0))[None] * np.maximum(-G[:, yrs] - slack[None], 0.0)).sum(1)
        vals -= pen
    # constraints
    ok = (bud <= prog.budget[None] * (1 + 1e-9) + 1e-6).all(1) & (dual <= prog.dual_budget[None] * (1 + 1e-9) + 1e-6).all(1) \
        & (cap <= prog.capacity[None] * (1 + 1e-9) + 1e-6).all(1) & (x <= prog.x_cap + 1e-12).all(1) \
        & (nu <= prog.x_cap * prog.Phi_sec[None] + 1e-9).all(1)
    if reg.covenant:
        e_exp = cols.ebitda0 + varpi[:, None] * cols.ebitda1
        c_exp = cols.cash0 + varpi[:, None] * cols.cash1
        EB = prog.ebitda_base[None] + agg(e_exp)
        ND = prog.net_debt0 - np.cumsum(prog.fcf_base[None] + agg(c_exp), axis=1)
        ok &= (ND <= reg.covenant * np.maximum(EB, 1e-9) + 1e-6).all(1)
    out = {"value": vals if not single else float(vals[0]), "feasible": ok if not single else bool(ok[0])}
    if detail and single:
        out.update({"load": load[0], "x": x[0], "nu": nu[0], "budget_use": bud[0], "dual_use": dual[0], "cap_use": cap[0],
                    "fd0": fd0[0], "fd1": fd1[0], "fsec": fsec[0], "launches": launches[0], "myopia_penalty": float(pen[0]),
                    "compliance_first_year": int(first[0]), "gaap_delta": G[0]})
        if reg.covenant:
            out.update({"ebitda": EB[0], "net_debt": ND[0], "leverage": ND[0] / np.maximum(EB[0], 1e-9)})
    return out


# -------------------------------------------------------------------------------------------------
# Solvers
# -------------------------------------------------------------------------------------------------
@dataclass
class Solution:
    sel: dict
    varpi: np.ndarray
    value: float
    method: str
    seconds: float
    history: list
    evaluation: dict


def solve_heuristic(prog: Program, varpi: np.ndarray, sel0: dict | None = None, sweeps: int = 8) -> dict:
    """Greedy outer loop (best feasible marginal value per process) then local search: for each process try every
    one of its columns or none, keep the best feasible; repeat until no change."""
    sel = dict(sel0 or {})
    procs = sorted(prog.by_proc)

    def best_for(pr):
        others = np.array([c for q, c in sel.items() if q != pr], int)
        cand = np.array(prog.by_proc[pr], int)
        res = _eval_many(prog, others, varpi, cand)
        base = _eval_many(prog, others, varpi, None)
        vals = np.where(res["feasible"], res["value"], -np.inf)
        j = int(np.argmax(vals))
        none_val = base["value"] if base["feasible"] else -np.inf
        return (int(cand[j]), vals[j]) if vals[j] > none_val + 1e-6 else (None, none_val)

    if not sel:
        # greedy: rank processes by their best stand-alone value and add in that order
        scores = []
        for pr in procs:
            c, v = best_for(pr)
            if c is not None:
                scores.append((v, pr))
        for _, pr in sorted(scores, reverse=True):
            c, v = best_for(pr)
            cur = evaluate(prog, sel, varpi)
            if c is not None and v > (cur["value"] if cur["feasible"] else -np.inf) + 1e-6:
                sel[pr] = c
    for _ in range(sweeps):
        changed = False
        for pr in procs:
            c, v = best_for(pr)
            if c != sel.get(pr):
                if c is None:
                    sel.pop(pr, None)
                else:
                    sel[pr] = c
                changed = True
        if not changed:
            break
    return sel


def _cbc(time_limit: float):
    import pulp
    s = pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit)
    return s


def milp_available() -> bool:
    try:
        import pulp
        return bool(pulp.PULP_CBC_CMD(msg=0).available())
    except Exception:
        return False


def solve_milp(prog: Program, varpi: np.ndarray, time_limit: float = 30.0) -> dict | None:
    """MILP over columns: binary z_c with at most one column per process; decision congestion and latency by
    load bands (factors at each band's upper edge, so the MILP is conservative); security reviews, budgets,
    capacity and covenants as linear constraints; wave overhead and congestion by binaries and tangent cuts;
    myopia by dip variables. Returns None if the solver fails (the caller falls back to the heuristic)."""
    try:
        import pulp
    except ImportError:
        return None
    cols, T = prog.cols, prog.T
    C = prog.C
    reg = prog.regime
    bands = np.array([0.25, 0.5, 0.7, 0.85, prog.x_cap])
    ellb = F.decision_latency(bands, prog.ell0, prog.x_cap)
    f0 = np.exp(-reg.r * ellb)
    f1 = F.congestion_q(bands, prog.eta_q) * np.exp(-prog.r_d * ellb)
    mdl = pulp.LpProblem("program", pulp.LpMaximize)
    z = [pulp.LpVariable(f"z{i}", cat="Binary") for i in range(C)]
    for ids in prog.by_proc.values():
        mdl += pulp.lpSum(z[i] for i in ids) <= 1
    obj = []
    s_all = cols.start
    ya_all = np.minimum(cols.tau0.astype(int), T - 1)
    D = np.exp(-reg.r * (np.arange(T) + 0.5))
    M = float(np.sum(np.abs(prog.pv0)) + np.sum(np.abs(varpi * prog.pv1))) + 1.0
    for y in range(T):
        ids = np.flatnonzero(s_all == y)
        beta = [pulp.LpVariable(f"b{y}_{b}", cat="Binary") for b in range(len(bands))]
        mdl += pulp.lpSum(beta) == 1
        mdl += prog.load0[y] + pulp.lpSum(cols.load[i, y] * z[i] for i in range(C) if cols.load[i, y]) <= \
            pulp.lpSum(beta[b] * bands[b] * prog.Phi[y] for b in range(len(bands)))
        if len(ids):
            w0 = [pulp.LpVariable(f"w0_{y}_{b}", lowBound=-M, upBound=M) for b in range(len(bands))]
            w1 = [pulp.LpVariable(f"w1_{y}_{b}", lowBound=-M, upBound=M) for b in range(len(bands))]
            mdl += pulp.lpSum(w0) == pulp.lpSum(prog.pv0[i] * z[i] for i in ids)
            mdl += pulp.lpSum(w1) == pulp.lpSum(varpi[i] * prog.pv1[i] * z[i] for i in ids)
            for b in range(len(bands)):
                for wv in (w0[b], w1[b]):
                    mdl += wv <= M * beta[b]
                    mdl += wv >= -M * beta[b]
                obj += [f0[b] * w0[b], f1[b] * w1[b]]
            om = pulp.LpVariable(f"wave{y}", cat="Binary")
            for i in ids:
                mdl += om >= z[i]
            obj.append(-prog.O_w * D[y] * om)
            n_y = pulp.lpSum(z[i] for i in ids)
            ex = pulp.LpVariable(f"cong{y}", lowBound=0)
            for kk in range(1, len(ids) + 1):
                mdl += ex >= (2 * kk - 1) * n_y - kk * (kk - 1)          # tangent cuts of n^2 at integers
            obj.append(-prog.d2 * D[y] * ex)
        mdl += pulp.lpSum(cols.budget[i, y] * z[i] for i in range(C) if cols.budget[i, y]) <= prog.budget[y]
        mdl += pulp.lpSum(cols.dual[i, y] * z[i] for i in range(C) if cols.dual[i, y]) <= prog.dual_budget[y]
        mdl += pulp.lpSum(cols.affected[i, y] * z[i] for i in range(C) if cols.affected[i, y]) <= prog.capacity[y]
        mdl += pulp.lpSum(cols.reviews[i, y] * z[i] for i in range(C) if cols.reviews[i, y]) <= prog.x_cap * prog.Phi_sec[y]
    # compliance from the first AI year
    a = [pulp.LpVariable(f"ai{y}", cat="Binary") for y in range(T)]
    for i in np.flatnonzero(cols.has_ai):
        mdl += a[ya_all[i]] >= z[i]
    first = [pulp.LpVariable(f"first{y}", lowBound=0, upBound=1) for y in range(T)]
    for y in range(T):
        mdl += first[y] >= a[y] - pulp.lpSum(a[yy] for yy in range(y))
    obj += [-prog.compliance[y] * first[y] for y in range(T)]
    if reg.myopia > 0:
        g_exp = cols.gaap0 + varpi[:, None] * cols.gaap1
        for y in range(min(reg.myopia_years, T)):
            dip = pulp.LpVariable(f"dip{y}", lowBound=0)
            mdl += dip >= -pulp.lpSum(g_exp[i, y] * z[i] for i in range(C))
            obj.append(-reg.myopia * math.exp(-reg.r * (y + 0.5)) * dip)
    if reg.covenant:
        e_exp = cols.ebitda0 + varpi[:, None] * cols.ebitda1
        c_exp = cols.cash0 + varpi[:, None] * cols.cash1
        for y in range(T):
            nd = prog.net_debt0 - float(prog.fcf_base[: y + 1].sum()) - pulp.lpSum(c_exp[i, : y + 1].sum() * z[i] for i in range(C))
            mdl += nd <= reg.covenant * (float(prog.ebitda_base[y]) + pulp.lpSum(e_exp[i, y] * z[i] for i in range(C)))
    mdl += pulp.lpSum(obj)
    try:
        status = mdl.solve(_cbc(time_limit))
    except Exception:
        return None
    if pulp.LpStatus.get(status) not in ("Optimal", "Not Solved") and pulp.LpStatus.get(status) != "Optimal":
        if pulp.LpStatus.get(status) in ("Infeasible", "Undefined", "Unbounded"):
            return None
    sel = {}
    for i in range(C):
        if z[i].value() is not None and z[i].value() > 0.5:
            sel[int(cols.proc[i])] = i
    return sel


def solve(prog: Program, method: str = "auto", fixed_point: int = 3, time_limit: float = 30.0,
          max_columns_milp: int = 400) -> Solution:
    """Solve with the learning fixed point: experience from the current selection sets varpi, then re-solve."""
    t0 = time.time()
    if method == "auto":
        method = "milp" if (prog.C <= max_columns_milp and milp_available()) else "heuristic"
    varpi = expit(prog.cols.logit0)
    sel: dict = {}
    history = []
    used = method
    for it in range(fixed_point):
        if used == "milp":
            s2 = solve_milp(prog, varpi, time_limit)
            if s2 is None:
                used = "heuristic (MILP failed)"
                s2 = solve_heuristic(prog, varpi)
            else:
                s2 = solve_heuristic(prog, varpi, sel0=s2, sweeps=2)     # polish on the exact objective
        else:
            s2 = solve_heuristic(prog, varpi, sel0=sel if it else None)
        E = experience(prog, s2, varpi)
        new_varpi = varpi_given(prog, E)
        ev = evaluate(prog, s2, new_varpi)
        history.append({"iteration": it, "value": ev["value"], "n_processes": len(s2), "feasible": ev["feasible"]})
        converged = s2 == sel and np.allclose(new_varpi, varpi, atol=1e-4)
        sel, varpi = s2, new_varpi
        if converged:
            break
    ev = evaluate(prog, sel, varpi, detail=True)
    return Solution(sel=sel, varpi=varpi, value=ev["value"], method=used, seconds=time.time() - t0, history=history,
                    evaluation=ev)


def column_index(cols: Columns) -> dict:
    """(process, level, start, variant, pilot) -> column index."""
    return {(int(cols.proc[i]), int(cols.level[i]), int(cols.start[i]), str(cols.variant[i]), int(cols.pilot[i])): i
            for i in range(len(cols))}


def value_of_plan(prog: Program, specs: list[tuple], index: dict | None = None, fixed_point: int = 2) -> dict:
    """Value of a plan given as column specs (from plans.column_specs) inside another program, for regret across
    scenarios: specs whose column does not exist there (infeasible in that scenario) are dropped and counted."""
    index = index if index is not None else column_index(prog.cols)
    sel = {}
    for sp in specs:
        key = (int(sp[0]), int(sp[1]), int(sp[2]), str(sp[3]), int(sp[4]))
        if key in index:
            sel[key[0]] = index[key]
    varpi = expit(prog.cols.logit0)
    for _ in range(fixed_point):
        varpi = varpi_given(prog, experience(prog, sel, varpi))
    ev = evaluate(prog, sel, varpi)
    return {"value": float(ev["value"]) if sel else 0.0, "feasible": bool(ev["feasible"]) if sel else True,
            "kept": len(sel), "dropped": len(specs) - len(sel)}


def improve_with_starts(prog: Program, sol: Solution, starts: list[list[tuple]], sweeps: int = 4) -> tuple[Solution, int]:
    """Multi-start polish: run the local search from each alternative plan (column specs, e.g. the scenario plans
    mapped into this program) and keep the best feasible result. Returns the solution and how many starts improved
    on it."""
    idx = column_index(prog.cols)
    best, n_better = sol, 0
    for specs in starts:
        sel0 = {}
        for sp in specs:
            key = (int(sp[0]), int(sp[1]), int(sp[2]), str(sp[3]), int(sp[4]))
            if key in idx:
                sel0[key[0]] = idx[key]
        if not sel0:
            continue
        varpi = best.varpi
        s2 = solve_heuristic(prog, varpi, sel0=sel0, sweeps=sweeps)
        for _ in range(2):
            varpi = varpi_given(prog, experience(prog, s2, varpi))
            s2 = solve_heuristic(prog, varpi, sel0=s2, sweeps=2)
        ev = evaluate(prog, s2, varpi, detail=True)
        if ev["feasible"] and ev["value"] > best.value + 1e-6 * max(abs(best.value), 1.0):
            best = Solution(sel=s2, varpi=varpi, value=ev["value"], method=sol.method + " + multi-start", seconds=sol.seconds,
                            history=sol.history + [{"iteration": "multi-start", "value": ev["value"], "n_processes": len(s2),
                                                    "feasible": True}], evaluation=ev)
            n_better += 1
    return best, n_better
