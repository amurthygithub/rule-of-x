# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Process plans ("columns"): for every process, readiness level, start year, variant and pilot choice, the
mode vector that maximizes the process value W(Z) (core 4.6 and 4.12) and the transition's expected cash flows
(core 4.9), resource use and score-path components.

A column's expected cash flow is affine in its success probability varpi:  CF = CF0 + varpi CF1  (core 4.9):
  CF0  flows on every branch (integration, build, capex, J-curve dip, dual running) and the failure branch
       (stranded costs and the rollback loss, weighted by p_u),
  CF1  the success branch less the failure branch (ramped savings, replacement capex, rebuilds, ...).
The program optimizer scales varpi by learning and congestion and discounts CF0 and CF1 by regime.

Time: quarterly grid of the plan horizon, t = 0 at the start of plan year 0 (calendar base_year)."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.special import expit, logit

from . import formulas as F
from . import economics as EC
from .economics import Econ, H, O, U, A, N, NM

QPY = 4  # quarters a year
VARIANTS = ("full", "augment")


@dataclass
class Columns:
    """Arrays over C candidate plans. Quarterly arrays have Q = 4 T entries, annual arrays T."""
    proc: np.ndarray
    level: np.ndarray
    start: np.ndarray
    variant: np.ndarray
    pilot: np.ndarray
    tau0: np.ndarray
    modes: list
    autonomy: list
    cf0: np.ndarray            # (C, Q) after-tax expected flows at varpi = 0
    cf1: np.ndarray            # (C, Q) slope in varpi
    tv1: np.ndarray            # (C,) after-tax steady-state annual flow on success at the horizon
    cash0: np.ndarray          # (C, T) pre-tax cash delta by year (for the score path)
    cash1: np.ndarray
    gaap0: np.ndarray          # (C, T) pre-tax GAAP operating delta
    gaap1: np.ndarray
    ebitda0: np.ndarray        # (C, T) EBITDA delta (covenants)
    ebitda1: np.ndarray
    logit0: np.ndarray         # (C,) logit of varpi before learning and congestion
    budget: np.ndarray         # (C, T) one-time cash spend
    dual: np.ndarray           # (C, T) dual-running cost
    affected: np.ndarray       # (C, T) affected FTE
    load: np.ndarray           # (C, T) decision units
    reviews: np.ndarray        # (C, T) security reviews
    fte_removed: np.ndarray    # (C, T) expected FTE removed (success path)
    platform: np.ndarray
    has_ai: np.ndarray
    regulated: np.ndarray
    detail: list = field(default_factory=list)   # per-column dict of transition terms (reporting)
    # branch components for the Monte Carlo (after-tax quarterly, pre-tax annual)
    sr_q: np.ndarray | None = None       # stranded cost plus rollback loss at cut-over
    sav_q: np.ndarray | None = None      # ramped savings at the mean benefit fraction
    bld_q: np.ndarray | None = None      # build, integration and pilot spend (overrun base)
    sr_cash: np.ndarray | None = None
    sav_cash: np.ndarray | None = None
    bld_cash: np.ndarray | None = None
    sr_gaap: np.ndarray | None = None
    T_emb: np.ndarray | None = None
    V_rec: np.ndarray | None = None
    p_u: np.ndarray | None = None
    bbar: np.ndarray | None = None       # (C,) mean benefit-realization share (lower for augmentation-led plans)
    J_auto: np.ndarray | None = None     # (C,) automated steps on the process chain
    keep: list | None = None             # reprice: positions of the specs that are still feasible

    def __len__(self):
        return len(self.proc)

    @staticmethod
    def empty(T: int, Q: int) -> "Columns":
        z = lambda *sh: np.zeros((0,) + sh)
        return Columns(proc=np.zeros(0, int), level=np.zeros(0, int), start=np.zeros(0, int), variant=np.zeros(0, object),
                       pilot=np.zeros(0, int), tau0=z(), modes=[], autonomy=[], cf0=z(Q), cf1=z(Q), tv1=z(), cash0=z(T),
                       cash1=z(T), gaap0=z(T), gaap1=z(T), ebitda0=z(T), ebitda1=z(T), logit0=z(), budget=z(T), dual=z(T),
                       affected=z(T), load=z(T), reviews=z(T), fte_removed=z(T), platform=np.zeros(0, object),
                       has_ai=np.zeros(0, bool), regulated=np.zeros(0, bool))

    def take(self, idx) -> "Columns":
        idx = np.asarray(idx, dtype=int)
        kw = {}
        for k, v in self.__dict__.items():
            if k == "keep":
                kw[k] = None
            elif isinstance(v, np.ndarray):
                kw[k] = v[idx]
            elif isinstance(v, list):
                kw[k] = [v[i] for i in idx]
            else:
                kw[k] = v
        return Columns(**kw)


# -------------------------------------------------------------------------------------------------
# Mode choice within a process (core 4.6, 4.12)
# -------------------------------------------------------------------------------------------------
def _process_arrays(econ: Econ, pidx: int, variant: str):
    """Per-step inputs of the W(Z) enumeration for all (level, year) at once."""
    us = np.flatnonzero(econ.unit_proc == pidx)
    L, T = econ.L, econ.T
    ct = econ.ct[us]                                   # (J, L, T, NM)
    bm = econ.base_mode[us]
    allowed = np.ones(NM, bool)
    if variant == "augment":
        allowed[[A, N]] = False
    nonA = ct.copy()
    nonA[..., A] = np.inf
    nonA[..., ~allowed] = np.inf
    for i, b in enumerate(bm):
        nonA[i, :, :, b] = ct[i, :, :, b]             # the baseline is always available
    m_M = nonA.argmin(-1)                              # (J, L, T)
    c_M = np.take_along_axis(nonA, m_M[..., None], -1)[..., 0]
    c_A = ct[..., A] if allowed[A] else np.full(c_M.shape, np.inf)
    return us, bm, m_M, c_M, c_A


def choose_modes(econ: Econ, pidx: int, variant: str, edges_idx: list | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Best mode vector of process pidx for every (level, year): (J, L, T) mode indices and (L, T) value W*.
    Enumerates all subsets of automated steps when the process has edges and at most 15 automatable steps
    (exact: core 4.6); otherwise a greedy pass that respects the concave risk cost (core 4.12)."""
    p = econ.p
    us, bm, m_M, c_M, c_A = _process_arrays(econ, pidx, variant)
    J, L, T = len(us), econ.L, econ.T
    vfy = econ.vf[None, :]
    v = econ.firm.units.v.values[us][:, None, None] * vfy[None]                    # (J, 1, T)
    u = v * (c_M - c_A)                                                            # (J, L, T)
    feasA = np.isfinite(c_A)
    u = np.where(feasA, u, -1e18)
    run = econ.run[us][:, :, A]                                                    # (J, T)
    Cinc = econ.C_inc[us, A]
    sec, rl = p.security, p.reliability
    writes = econ.info["writes"][us]
    rel = econ.info.get("reliability")
    auto = rel["autonomy"][us] if rel is not None else np.full((J, L, T), 3)
    if edges_idx is None:
        edges = econ.firm.edges
        pid = econ.firm.processes.process_id.iat[pidx]
        E = edges[edges.process_id == pid]
        pos = {uid: i for i, uid in enumerate(econ.firm.units.unit_id.values[us])}
        edges_idx = [(pos[a], pos[b]) for a, b in zip(E.u_from, E.u_to) if a in pos and b in pos]
    ed = edges_idx
    w = econ.info["w"][us]
    t = econ.info["t"][us]
    iota_p = econ.iota[pidx]                                                       # (L,)
    hd = p.handoff
    crit = econ.firm.units.critical.values[us].astype(bool)
    vproc = econ.firm.units.v.values[us]
    vp = float(np.median(vproc)) if J else 0.0
    proc_lab = float(np.sum(w * t))                                                # $ per process output unit
    Xi = hd.Xi_share * float(np.sum(vproc * w * t))
    N_int = econ.info["N_int"][us]

    def risk_cost(x):
        return F.risk_cost(x, sec.C_s)

    def controls(mask_any_A, mask_any_write, mask_any_auto):
        return (rl.mon_cost * mask_any_A + rl.lp_cost * mask_any_write + rl.kill_cost * mask_any_auto) if rl.enabled else 0.0

    if J == 0:
        return np.zeros((0, L, T), int), np.zeros((L, T))
    n_auto = int(feasA.any(axis=(1, 2)).sum())
    best_val = np.zeros((L, T))
    best_mask = np.zeros((J, L, T), bool)
    if ed and n_auto <= 15:
        cand = np.flatnonzero(feasA.any(axis=(1, 2)))
        masks_c = F.subsets_mask(len(cand))                                        # (M, Jc)
        M = masks_c.shape[0]
        masks = np.zeros((M, J), bool)
        masks[:, cand] = masks_c
        uval = np.einsum("mj,jlt->ltm", masks.astype(float), np.where(masks.any(0)[:, None, None], u, 0.0))
        bad = np.einsum("mj,jlt->ltm", masks.astype(float), (u <= -1e17).astype(float)) > 0
        val = uval
        for (i, j) in ed:
            wb = 0.5 * (w[i] + w[j])
            ve = vproc[i] * econ.vf                                                # (T,)
            eMM = hd.h_MM * wb
            eAM = hd.h_AM * wb
            eAA = hd.h_AA0 * (1 - iota_p) * wb                                     # (L,)
            zi, zj = masks[:, i], masks[:, j]
            both, one = zi & zj, zi ^ zj
            eta = np.where(both[None, :], eAA[:, None], np.where(one[None, :], eAM, eMM))   # (L, M)
            val = val + ve[None, :, None] * (eMM - eta)[:, None, :]
            val = val - (sec.c_cpl * N_int[i] * N_int[j] * both)[None, None, :]
        # O-ring term (lem:tasks-oring): v_p L_p [Q(Z) - Q(empty)]
        qA = 1.0 - np.clip(econ.eps[us], 0, 1)                                     # (J, L, T)
        qM = p.review.q_M
        logQ = np.einsum("mj,jlt->ltm", masks.astype(float), np.log(np.maximum(qA, 1e-12))) + \
            np.einsum("mj->m", (~masks).astype(float))[None, None, :] * math.log(qM)
        vL = vp * econ.vf * p.review.lambda_out * proc_lab                         # (T,)
        val = val + vL[None, :, None] * (np.exp(logQ) - qM ** J)
        if crit.any():
            allc = masks[:, crit].all(1)
            val = val + (Xi * econ.vf)[None, :, None] * allc[None, None, :]
        val = val - np.einsum("mj,jt->tm", masks.astype(float), run)[None, :, :]
        rk = risk_cost(masks.astype(float) @ Cinc)                                 # (M,)
        anyA = masks.any(1).astype(float)
        anyW = (masks & (writes > 0)[None, :]).any(1).astype(float)
        val = val - rk[None, None, :] - controls(anyA, anyW, anyA)[None, None, :]
        val = np.where(bad, -np.inf, val)
        k = val.argmax(-1)                                                         # (L, T)
        best_val = np.take_along_axis(val, k[..., None], -1)[..., 0]
        best_mask = np.transpose(masks[k], (2, 0, 1))                              # (J, L, T)
    else:
        # greedy: activities with positive stand-alone net value, then pooled risk and fixed controls
        net = u - run[:, None, :]
        Z = (net > 0) & feasA
        for _ in range(2):
            tot_inc = np.einsum("jlt,j->lt", Z.astype(float), Cinc)
            marg = risk_cost(tot_inc[None] + Cinc[:, None, None]) - risk_cost(tot_inc)[None]
            marg_out = risk_cost(tot_inc)[None] - risk_cost(np.maximum(tot_inc[None] - Cinc[:, None, None], 0))
            Z = np.where(Z, net - marg_out > 0, net - marg > 0) & feasA
        anyA = Z.any(0)
        anyW = (Z & (writes > 0)[:, None, None]).any(0)
        val = np.where(Z, net, 0.0).sum(0) - risk_cost(np.einsum("jlt,j->lt", Z.astype(float), Cinc)) - \
            controls(anyA.astype(float), anyW.astype(float), anyA.astype(float))
        keep = val > 0
        best_mask = Z & keep[None]
        best_val = np.where(keep, val, 0.0)
    modes = np.where(best_mask, A, m_M)
    return modes, best_val


# -------------------------------------------------------------------------------------------------
# Transition terms and flows (core 4.9; ext 3.3; ext sec:ext-shocks)
# -------------------------------------------------------------------------------------------------
def _overlap(a, b, lo, hi):
    """Years of [a, b) inside each period [lo, hi): a, b (C,), lo, hi (Q,) -> (C, Q)."""
    return np.clip(np.minimum(hi[None, :], b[:, None]) - np.maximum(lo[None, :], a[:, None]), 0.0, None)


def _ramp_avg(tau0, T_par, lo, hi):
    """Average of the linear ramp rho(t - tau0) over each quarter (0 before tau0, 1 after tau0 + T_par)."""
    Tp = np.maximum(T_par, 1e-9)[:, None]

    def Fx(x):
        z = np.clip(x[None, :] - tau0[:, None], 0, None)
        return np.where(z <= Tp, z * z / (2 * Tp), Tp / 2 + (z - Tp))
    return (Fx(hi) - Fx(lo)) * QPY


def _at(time, Q):
    """One-hot (C, Q): the quarter in which each column's event happens (none if beyond the horizon)."""
    q = np.floor(np.asarray(time) * QPY + 1e-9).astype(int)
    return (np.arange(Q)[None, :] == q[:, None]).astype(float)


def _years(qarr: np.ndarray, T: int) -> np.ndarray:
    return qarr.reshape(qarr.shape[0], T, QPY).sum(-1)


class PlanBuilder:
    """Builds the candidate columns of every process."""

    def __init__(self, econ: Econ):
        self.econ = econ
        p = econ.p
        self.p = p
        self.T = econ.T
        self.Q = econ.T * QPY
        self.tau = econ.info["tau"]
        self.psi = float(econ.info.get("psi_tax", 1.0))
        self.r = p.finance.r
        f = econ.firm
        self.U = f.units.reset_index(drop=True)
        self.P = f.processes.reset_index(drop=True)
        self.S = f.part1["S"] * econ.vf
        self.org = f.org
        self.mode_cache: dict = {}
        self.term_cache: dict = {}
        ed = f.edges
        self._edges = {pid: (g.u_from.values, g.u_to.values) for pid, g in ed.groupby("process_id")} if len(ed) else {}
        self._pinfo = [self._make_pinfo(i) for i in range(len(self.P))]
        sc = p.success
        past = float(np.clip(self.org.get("past_rate", 0.5), 0.02, 0.98))
        prior = float(np.clip(self.org.get("past_prior_mean", 0.5), 0.02, 0.98))
        self.past_shift = sc.c_past * (logit(past) - logit(prior))
        self.team = float(self.org.get("team", sc.team_prior))
        self.fte_total = float(self.U.fte.sum())
        sh = p.shocks
        # disruptions cancel work in flight only when the haircut is on (off in the base case: the realized share and the
        # success logit come from outcome surveys that include them; shocks.disruption_haircut, QA/ISSUES.md 9)
        self.nu_D = F.disruption_rate(sh.nu_L, sh.kappa_keep, sh.nu_V) if (sh.enabled and sh.disruption_haircut) else 0.0
        d = p.decisions
        self.e_mult = F.ai_bandwidth_gain(d.e_appr_share, 1 - d.e_appr_share, 0.0) / \
            F.ai_bandwidth_gain(d.e_appr_share, 1 - d.e_appr_share, d.A_Phi)            # load per initiative after AI prep

    def _make_pinfo(self, pidx: int) -> dict:
        e = self.econ
        us = np.flatnonzero(e.unit_proc == pidx)
        Ut = self.U.iloc[us]
        pid = self.P.process_id.iat[pidx]
        E = self._edges.get(pid)
        pos = {uid: i for i, uid in enumerate(Ut.unit_id.values)}
        ed = [] if E is None else [(pos[a], pos[b]) for a, b in zip(E[0], E[1]) if a in pos and b in pos]
        regs = EC.unit_regulated(Ut)       # explicit attribute, decoupled from the reliability target
        sponsor = self.P.sponsor.iat[pidx]
        return dict(us=us, bm=e.base_mode[us], v=Ut.v.values.astype(float), w=e.info["w"][us], t=e.info["t"][us],
                    edges=ed, crit=Ut.critical.values.astype(bool), regs=np.asarray(regs, bool),
                    regclass=np.asarray(Ut.regulated_class.astype(str).values, dtype=object),
                    exposure=Ut.exposure.values.astype(float), hours=Ut.hours.values.astype(float),
                    fte=Ut.fte.values.astype(float), personal=bool(Ut.personal_data.values.max()) if len(Ut) else False,
                    vendor=Ut.vendor_spend.values.astype(float), N_int=e.info["N_int"][us], writes=e.info["writes"][us],
                    kind=str(self.P.kind.iat[pidx]), n_sys=float(self.P.n_systems_p.iat[pidx]),
                    lic=float(self.P.license_cost.iat[pidx]), function=str(self.P.function_id.iat[pidx]),
                    sponsor=float(sponsor) if pd.notna(sponsor) else float(self.org.get("sponsor_prior", self.p.success.sponsor_prior)),
                    dK=np.broadcast_to(e.info["dK_A"], (e.nU, 1, 1))[us, 0, 0],
                    icfr=self._icfr(pidx, Ut), rbar=Ut.r_bar.values.astype(float),
                    icfr_units=(Ut.icfr_step.values.astype(bool) if "icfr_step" in Ut.columns else np.full(len(Ut), self._icfr(pidx, Ut))),
                    fsw=(Ut.financial_system_written.fillna("").astype(str).values if "financial_system_written" in Ut.columns
                         else np.full(len(Ut), "")))

    def _mw_cost(self) -> float:
        """Expected material-weakness loss of an ICFR-scope cutover (cor:acct-npv), at an assessment one fiscal year
        less the close after go-live."""
        ac = self.p.accounting
        return ac.L_mw * F.mw_probability(1.0 - ac.T_cl, ac.p_def, ac.p_mw, ac.T_rem, ac.T_op, ac.T_dc)

    def _icfr(self, pidx: int, Ut) -> bool:
        """Process in ICFR scope (full or partial, spec 24.4; impute.icfr_scope_table), or one of its activities is
        in accounting.icfr_gwas."""
        from .impute import icfr_scope
        ac = self.p.accounting
        if "icfr" in self.P.columns:
            in_p = bool(self.P.icfr.iat[pidx])
        else:
            in_p = icfr_scope("", str(self.P.process_name.iat[pidx]) if "process_name" in self.P else "", self.p)
        in_gwa = bool(set(Ut.gwa_id.astype(str)) & set(ac.icfr_gwas)) if len(ac.icfr_gwas) else False
        return bool(in_p or in_gwa)

    def modes(self, pidx: int, variant: str):
        key = (pidx, variant)
        if key not in self.mode_cache:
            self.mode_cache[key] = choose_modes(self.econ, pidx, variant, self._pinfo[pidx]["edges"])
        return self.mode_cache[key]

    # ---------------------------------------------------------------------------------------------
    def terms(self, pidx: int, level: int, md: np.ndarray) -> dict | None:
        """Transition terms (core ass:tasks-transition) of moving process pidx to the mode vector md at readiness
        `level`. Quantities that depend on the adoption year are arrays over y0 = 0..T-1."""
        key = (pidx, level, md.tobytes())
        if key in self.term_cache:
            return self.term_cache[key]
        e, p, pi = self.econ, self.p, self._pinfo[pidx]
        us, bm = pi["us"], pi["bm"]
        ch = md != bm
        if not ch.any():
            self.term_cache[key] = None
            return None
        T = self.T
        v, w, t = pi["v"], pi["w"], pi["t"]
        rows = np.arange(len(us))
        cash = e.cash[us, level]                                     # (J, T, NM)
        c_base, c_new = cash[rows, :, bm], cash[rows, :, md]
        ok_y = np.all(np.isfinite(c_new[ch]), axis=0)                # (T,) new modes feasible in year y
        vT = v[:, None] * e.vf[None, :]
        c_new_f = np.where(np.isfinite(c_new), c_new, 0.0)
        c_base_f = np.where(np.isfinite(c_base), c_base, 0.0)
        sav_unit = np.where(ch[:, None] & np.isfinite(c_new) & np.isfinite(c_base), (c_base_f - c_new_f) * vT, 0.0)
        # competitive dilution in DOLLARS (cor:ext-game-engine(a)): rivals replicate cost-of-revenue savings, so the firm
        # keeps the durable share dur_rep of the dollar saving, its volume gain counted (Part I round 2: this is the dollar
        # share; the score uses the rate on the unit-cost saving at the post-cut price, economics info pass_through); an
        # AI-native entrant scenario passes a further share through. Overhead is a fixed cost in the incumbents' game
        keep_cogs = e.info["durable_share"] * (1.0 - float(p.finance.pass_through_phi))
        if keep_cogs != 1.0:
            sav_unit = sav_unit * np.where(e.info["cogs"][us], keep_cogs, 1.0)[:, None]
        isA = md == A
        sec, rl, tr, bd, sc = p.security, p.reliability, p.transition, p.build, p.success
        run = (e.run[us][:, :, A] * isA[:, None]).sum(0)                       # (T,) run costs (core 4.12)
        Cinc = float((e.C_inc[us, A] * isA).sum())
        risk = float(F.risk_cost(Cinc, sec.C_s)) if isA.any() else 0.0
        sec_spend = float(F.security_spend(Cinc, sec.C_s)) if isA.any() else 0.0
        rel = e.info.get("reliability")
        auto = rel["autonomy"][us, level] if rel is not None else np.full((len(us), T), 3)   # (J, T)
        ctrl = 0.0
        if isA.any() and rl.enabled:
            ctrl = rl.mon_cost + rl.lp_cost * float((pi["writes"][isA] > 0).any()) + rl.kill_cost * float((auto[isA] == 3).any())
        Om_max = float(e.exposure_sec[us][isA, A].max()) if isA.any() else 0.0
        redteam = sec.redteam_cost if Om_max > 0.6 else 0.0
        hd = p.handoff
        hand, tdebt = np.zeros(T), 0.0
        for i, j in pi["edges"]:
            wb = 0.5 * (w[i] + w[j])
            eta = hd.h_AA0 * (1 - e.iota[pidx, level]) * wb if (isA[i] and isA[j]) else (hd.h_AM * wb if (isA[i] or isA[j]) else hd.h_MM * wb)
            hand += v[i] * e.vf * (hd.h_MM * wb - eta)
            if isA[i] and isA[j]:
                tdebt += sec.c_cpl * pi["N_int"][i] * pi["N_int"][j]
        oring, Xi = np.zeros(T), 0.0
        if pi["edges"]:
            qA = 1 - np.clip(e.eps[us, level, :], 0, 1)
            qM = p.review.q_M
            Qn = np.prod(np.where(isA[:, None], qA, qM), axis=0)
            oring = float(np.median(v)) * e.vf * p.review.lambda_out * float(np.sum(w * t)) * (Qn - qM ** len(us))
            if pi["crit"].any() and isA[pi["crit"]].all():
                Xi = hd.Xi_share * float(np.sum(v * w * t))
        W = sav_unit.sum(0) + hand + oring + Xi * e.vf - run - tdebt - risk - ctrl - redteam   # (T,)
        # ICFR consequences (spec 24.4): an agent that performs an in-scope unit is an in-scope application with its
        # own ITGCs (logical access for service identities and tool permissions; change management for model,
        # prompt, tool and configuration changes with retesting at each forced upgrade; IT operations); each new
        # integration feeding an in-scope system needs interface controls; in-scope automated steps keep a manual
        # fallback for provider outages at period-end (availability, distinct from the error floor c_err)
        ac = p.accounting
        icfr_A = isA & pi["icfr_units"]
        sys_new = set()
        for j in np.flatnonzero(ch & pi["icfr_units"]):
            for part in str(pi["fsw"][j]).replace(" and ", ";").split(";"):
                if part.strip():
                    sys_new.add(part.strip().split(" (")[0].lower())
        n_if = min(len(sys_new), max(int(round(pi["n_sys"])), 1)) if (sys_new and level > 0) else 0   # new interfaces
        itgc_annual = itgc_setup = close_delay = 0.0
        tml = {"C_tml": 0.0, "fallback_pays": False, "wait": 0.0, "nu_star": math.inf}
        if icfr_A.any():
            # the application's ITGC line (eq:acct-itgc): access, change, ICFR retest at each forced upgrade (separate
            # from the functional revalidation in the run costs), operations and its interfaces to in-scope systems
            n_ifc = min(len(sys_new), max(int(round(pi["n_sys"])), 1))
            line = F.itgc_line(ac.itgc_n_id, ac.itgc_perm_per_step * int(icfr_A.sum()), ac.itgc_c_acc, ac.itgc_n_chg,
                               ac.itgc_c_chg, ac.C_val, max(float(sec.T_up), 1e-9), ac.itgc_c_ops, n_ifc, ac.itgc_c_ifc)
            itgc_annual = float(sum(line.values()))
            itgc_setup = ac.itgc_setup
            nu_out = rl.downtime_hours / 24.0 / max(ac.D_bar, 1e-9)       # incidents a year from provider downtime
            tml = F.timeliness_cost(ac.n_cl, nu_out, ac.T_cw, ac.D_bar, ac.T_sl, ac.c_del, ac.L_late, ac.C_fb, ac.c_fb, ac.t_sw)
            close_delay = tml["wait"]
        if_annual = 0.0                                   # interface controls are inside the ITGC line (c_ifc n_ifc)
        fallback = np.full(T, tml["C_tml"])               # C^tml: the cheaper of waiting outages out and a fallback
        W = W - itgc_annual - if_annual - fallback
        # legacy and labor bases by adoption year
        C0 = (c_base_f * vT * ch[:, None]).sum(0)
        E_p = (w * t)[:, None] * vT
        E_p = (E_p * ch[:, None]).sum(0)
        res_b = e.res_hours[us, level][rows, :, bm]                            # (J, T)
        res_n = e.res_hours[us, level][rows, :, md]
        inhouse = bm == H
        dh = np.maximum(res_b - res_n, 0) * vT * (ch & inhouse)[:, None]
        fte_removed = dh.sum(0) / p.labor.hours_per_fte
        C_disp = (dh * w[:, None]).sum(0)
        affected = (pi["fte"] * (ch & inhouse)).sum() * e.vf + 0.25 * (pi["fte"] * (ch & ~inhouse)).sum() * e.vf
        # labor law by site (theory_labor): severance max(statutory floor, plan) per displaced FTE, legal leads
        lb = p.labor
        fv = ((self.org.get("jurisdiction") or {}).get("by_function") or {}).get(pi["function"])
        sev_m = fv["severance_months"] if fv is not None else self.org.get("severance_months", tr.severance_months_US)
        u_d = float(self.org.get("redeployment_share", tr.u_d))
        # redeployment bound (prop:labor-survivor(e)): vacancies from quits among other staff over the window
        T_leg_m = float(np.sum(fv["share"] * fv["T_leg"])) if fv is not None else 0.0
        N_oth = max(self.fte_total - float(pi["fte"].sum()), 0.0)
        ud_cap = F.redeployment_cap(lb.varpi_rd, lb.nu_q, N_oth, max(T_leg_m, tr.T_par_default), fte_removed)
        u_d = np.minimum(u_d, ud_cap)                                            # (T,)
        anyAN = bool(np.isin(md[ch], [A, N]).any())
        icfr_c = bool(pi["icfr"] and anyAN and (pi["icfr_units"] & ch & np.isin(md, [A, N])).any())   # an ICFR step changes
        leave_O = (bm == O) & (md != O)
        C_brk = tr.break_months_O / 12.0 * float((pi["vendor"] * leave_O).sum()) * e.vf + \
            (tr.break_months_license / 12.0 * tr.retire_fraction * pi["n_sys"] * pi["lic"] if anyAN else 0.0)
        # survivors (prop:labor-survivor(a)): the part of the excess quits that grows with the displacement share,
        # here; the announcement jump (eta_0, delta_0) is the per-wave charge O_s in the optimizer (part (b))
        N_hc, remaining, x_share = F.survivor_base((pi["fte"] * (ch & inhouse)).sum() * e.vf, fte_removed)   # in-house staff only
        C_attr = F.survivor_cost(remaining, float(np.mean(w)) * p.labor.hours_per_fte, lb.nu_q,
                                 lb.survivor_quits_per_share * x_share / max(lb.T_s, 1e-9), lb.T_s, lb.c_rep, 0.0) * (fte_removed > 0)
        C_sev = (1 - u_d) * sev_m / 12.0 * C_disp
        C_str = C_sev + C_brk + u_d * tr.redeploy_months / 12.0 * C_disp + C_attr
        C_wo = tr.retire_fraction * pi["n_sys"] * tr.legacy_book_value_per_system if anyAN else 0.0
        only_U = bool(np.all(md[ch] == U))
        only_O = bool(np.all(md[ch] == O))
        C_dup = tr.retire_fraction * pi["n_sys"] * pi["lic"] if anyAN else 0.0
        C_par = np.zeros(T) if only_U else tr.omega_par * C0 + tr.nu_rec * E_p + C_dup
        rates = e.rates
        chi = np.flatnonzero(ch)
        Fb = e.F_build[us[chi], :, md[chi]].sum(0) if len(chi) else np.zeros(T)
        reg = bool(pi["regs"][ch].any())
        anc = (sec.legal_review_cost + (sec.eval_data_cost if isA.any() else 0.0)
               + (sec.pia_cost if pi["personal"] and (isA.any() or (md == U).any()) else 0.0)
               + affected * p.labor.change_mgmt_cost_per_fte
               + p.labor.training_hours_per_fte * float(np.sum(pi["fte"] * (w + p.labor.training_cost_per_hour) * ch)) * e.vf
               + (rates["risk_governance_month"] if reg else 0.0)
               + (p.accounting.icfr_redesign_cost if icfr_c else 0.0)
               + (self._mw_cost() if icfr_c else 0.0))
        F_tot = Fb + bd.redesign_months * rates["process_owner_month"] + anc + itgc_setup + n_if * ac.interface_control_setup
        I = float(F.integration_cost(e.iota[pidx, 0], e.iota[pidx, level], pi["n_sys"], bd.int_cost_per_system,
                                     bd.int_convexity)) if level > 0 else 0.0
        K_unit = e.K[us, level][rows, :, md]                                   # (J, T)
        K = (K_unit * vT).sum(0)
        dK = float(np.average(pi["dK"], weights=np.maximum(K_unit[:, -1] * v, 1e-12))) if K.max() > 0 else p.capital.delta_K_compute
        C_J = tr.dip_share * C0 * tr.dip_years
        # success probability (core lem:tasks-success)
        mig = ch & (pi["crit"] if (pi["crit"] & ch).any() else np.ones(len(us), bool))
        lm = np.clip(e.log_margin[us, level, :], -5, 5)                         # (J, T)
        act = sc.a0 + sc.a_iota * e.iota_u[us, level][:, None] + sc.a_H * np.where((md == A)[:, None], lm, 3.0) \
            - sc.a_R * pi["regs"][:, None] + np.where((md == A)[:, None], 0.0, sc.U_bonus)
        if rel is not None:
            fm = rel["h"][us, level] + rel["m_esc"][us, level]
            act = act - np.where((md == A)[:, None], rl.a_fm * np.log1p(100 * fm), 0.0)
        # agent pipelines (core prop:tasks-pipeline): driver ln(J_max/J) on automated chains
        J_auto = int(isA.sum()) if pi["kind"] == "process" else 0
        if J_auto >= 2 and rl.enabled:
            eps_s = np.clip(e.eps[us, level][isA], 1e-6, 0.5).mean(0)                      # (T,)
            qbar_p = float(np.min(pi["rbar"][isA]))
            J_max = F.max_pipeline_length(eps_s, qbar_p, 1, rl.J_s, rl.d_c)
            pipe = sc.a_J * np.clip(np.log(np.maximum(J_max, 0.5) / J_auto), -2.0, 2.0)
        else:
            pipe = np.zeros(T)
        exc = 1.0 - float(np.average(pi["exposure"][ch], weights=np.maximum(pi["hours"][ch], 1e-9)))
        hr = float((pi["regclass"][ch] == "high_risk_eu").any())
        proc = (sc.c0 - sc.c_exc * exc - sc.c_fte * np.log1p(affected / 50.0) + sc.c_team * (self.team - 0.5)
                + sc.c_sponsor * (pi["sponsor"] - 0.5) + self.past_shift
                - p.decisions.delegation_risk * float(self.org.get("delegation", 0.0)) * hr + pipe)    # (T,)
        if pi["kind"] == "process":
            varpi = expit(proc) * np.prod(expit(act[mig]), axis=0)
        else:   # a workstream of independent activities, not a chain: expected share that succeeds
            wts = np.maximum(sav_unit[mig], 1e-9)
            varpi = expit(proc) * (expit(act[mig]) * wts).sum(0) / wts.sum(0)
        varpi = np.clip(varpi, 1e-4, 0.9999)
        Wpos = np.maximum(W, 1e-9)
        # benefit realization (modern map change 7): lower when augmentation carries most of the saving
        U_share = float(sav_unit[(md == U)].sum() / max(sav_unit[ch].sum(), 1e-9)) if ch.any() else 0.0
        b_p = sc.b_bar_U if U_share >= 0.5 else sc.b_bar
        if self.org.get("benefit_realization_past") is not None:
            b_p = float(np.clip(b_p * float(self.org["benefit_realization_past"]) / sc.b_bar, 0.2, 1.0))
        L_roll = tr.L_roll_mult * C0
        if only_U:
            T_par = np.full(T, tr.T_learn_U)
        elif only_O:
            T_par = np.full(T, tr.T_par_O)
        elif tr.policy == "optimal":
            T_par = F.optimal_parallel_run(C_par, varpi, b_p, Wpos, C_str, L_roll, tr.T_det)
            T_par = np.clip(T_par, tr.T_par_min_regulated if reg else tr.T_par_min, tr.T_par_max)
        else:
            T_par = np.full(T, max(tr.T_par_default, tr.T_par_min_regulated if reg else tr.T_par_min))
        T_st = np.zeros(T)
        tau_ann = np.zeros(T)
        if not only_U:
            if icfr_c:                                     # a redesigned control must run through a quarter-end close,
                ac = p.accounting                          # and the cutover waits for the open window (prop:acct-cutover)
                T_par = np.maximum(T_par, ac.icfr_min_parallel) + F.cutover_delay(ac.T_op, ac.T_cl)
            if fv is not None and (fte_removed > 0).any():
                T_par, C_par, T_st, tau_ann = self._legal_timing(fv, T_par, C_par, varpi, b_p, Wpos, C_str, L_roll, E_p, C_dup,
                                                                 fte_removed > 0, tr.policy == "optimal")
        # critical knowledge holders over the announced period (prop:labor-survivor(c), eq:labor-success)
        n_K = float(self.org.get("knowledge_holders_per_process") or lb.knowledge_holders_per_process)
        if n_K > 0 and not only_U:
            disp = float(self.org.get("knowledge_holders_displaced", 1.0) or 0.0) >= 0.5
            nu_x = lb.nu_x if disp else float(lb.survivor_excess_quits) / max(lb.T_s, 1e-9)
            varpi = np.clip(varpi * F.knowledge_holder_factor(n_K, lb.kappa_doc, 0.0, nu_x, tau_ann), 1e-4, 0.9999)
        p_u = np.zeros(T) if only_U else F.undetected_failure_prob(T_par, tr.T_det)
        payback = (F_tot + I + C_J + C_str) / Wpos + T_par * (0.5 + C_par / Wpos)
        out = dict(W=W, ok_y=ok_y, C0=C0, E_p=E_p, C_par=C_par, C_dup=C_dup, C_disp=C_disp, C_str=C_str, C_brk=C_brk, C_sev=C_sev,
                   C_wo=C_wo, F=F_tot, F_build=Fb, F_anc=anc, I=I, K=K, dK=dK, C_J=C_J, varpi=varpi, T_par=T_par, p_u=p_u,
                   L_roll=L_roll, payback=payback, fte_removed=fte_removed, affected=affected, regulated=reg,
                   only_U=only_U, isA=isA, md=md, risk=risk, sec_spend=sec_spend, run=run, controls=ctrl + redteam,
                   tdebt=tdebt, Cinc=Cinc, Om_max=Om_max, autonomy=np.where(isA[:, None], auto, np.where((md == U)[:, None], 1, -1)),
                   reviews=(1.0 + Om_max) if (isA.any() or (md == U).any()) else 0.0, process_logit=proc,
                   b_bar=b_p, J_auto=J_auto, icfr=icfr_c, C_attr=C_attr, U_share=U_share,
                   T_st=T_st, tau_ann=tau_ann, u_d=u_d, itgc_annual=itgc_annual, itgc_setup=itgc_setup, interfaces=n_if,
                   interface_annual=if_annual, fallback_annual=fallback, close_delay_no_fallback=close_delay,
                   icfr_units_automated=int(icfr_A.sum()), tml=float(tml["C_tml"]), fallback_pays=bool(tml["fallback_pays"]))
        self.term_cache[key] = out
        return out

    def _legal_timing(self, fv, T_par, C_par, varpi, b_p, W, C_str, L_roll, E_p, C_dup, dismiss, optimal):
        """Legal leads by site (prop:labor-lead): the run starts after any technology consultation that outlasts the
        build (T^st); the procedure starts early when varpi >= varpi^A, or by the contemplation date (EU, UK: the
        decision); dismissals wait until t^A + T^leg, so the parallel run extends to T_opt = min{T**, max{T^hold, T*}}
        (eq:labor-freerun) and the run cost before the hold ends is c-hat' = nu_rec E_p + C^dup. Sites are averaged
        by headcount share (each site cuts over in its own stream; the roadmap reports the streams). Returns the
        effective T_par, C_par, the run-start delay T^st and the announced period tau^ann, by adoption year."""
        lb, tr = self.p.labor, self.p.transition
        sh, Tl, Tt, c0 = fv["share"], fv["T_leg"], fv["T_tech"], fv["cont0"]
        T = len(T_par)
        Tst = F.run_start_delay(Tt, lb.T_bld_default)                          # (S,)
        chat1 = tr.nu_rec * E_p + C_dup                                         # (T,)
        Tp_eff, Cp_eff, Tst_eff, tau = np.zeros(T), np.zeros(T), np.zeros(T), np.zeros(T)
        for y in range(T):
            gate = Tst + T_par[y]
            vA = F.announcement_cutoff(gate, Tl, W[y], lb.c_ann_share * W[y], lb.C_wd_share * W[y])
            tA = np.where(c0 | (varpi[y] >= vA), np.maximum(gate - Tl, 0.0) * (~c0), gate)
            hold = np.maximum(tA + Tl - Tst, 0.0)
            if optimal:
                Topt = F.free_parallel_run(hold, C_par[y], varpi[y], b_p, W[y], C_str[y], L_roll[y], tr.T_det, chat1[y])
                Topt = np.clip(np.maximum(Topt, T_par[y]), T_par[y], max(tr.T_par_max, float(np.max(hold))))
            else:
                Topt = np.maximum(T_par[y], hold)
            tdis = F.cutover_date(Tst, Topt, tA, Tl)
            run = np.maximum(tdis - Tst, 1e-9)
            if not dismiss[y]:
                run, Tst_y = np.full_like(run, T_par[y]), np.zeros_like(Tst)
            else:
                Tst_y = Tst
            h = np.minimum(hold, run) if dismiss[y] else np.zeros_like(run)
            Tp_eff[y] = float(np.sum(sh * run))
            Cp_eff[y] = float(np.sum(sh * (chat1[y] * h + C_par[y] * (run - h)) / run))
            Tst_eff[y] = float(np.sum(sh * Tst_y))
            tau[y] = float(np.sum(sh * np.maximum(Tst_y + run - np.maximum(tA, Tst_y), 0.0)))
        return Tp_eff, Cp_eff, Tst_eff, tau

    # ---------------------------------------------------------------------------------------------
    def build(self, processes=None, starts=None, pilots=(0, 1), variants=VARIANTS) -> "Columns":
        """All candidate columns: process x variant x readiness level x start year x pilot."""
        e, p = self.econ, self.p
        T = self.T
        S = int(min(p.constraints.launch_years, T - 1))
        starts = list(range(S)) if starts is None else list(starts)
        processes = range(len(self.P)) if processes is None else processes
        recs = []
        for pidx in processes:
            seen = set()
            for variant in variants:
                modes, _ = self.modes(pidx, variant)
                if modes.shape[0] == 0:
                    continue
                for level in range(e.L):
                    if not e.level_ok[pidx, level]:
                        continue
                    for s in starts:
                        for pilot in pilots:
                            tau0 = s + (p.build.T_int if level > 0 else 0.0) + (p.pilot.T_pil if pilot else 0.0)
                            if tau0 >= T - 1:
                                continue
                            y0 = int(math.floor(tau0))
                            md = modes[:, level, y0]
                            d = self.terms(pidx, level, md)
                            if d is None or not d["ok_y"][y0] or d["W"][y0] <= 0 or (pilot and d["only_U"]):
                                continue
                            key = (level, s, pilot, md.tobytes())
                            if key in seen:            # the augment variant can coincide with the full one
                                continue
                            seen.add(key)
                            recs.append((pidx, level, s, variant, pilot, y0, tau0, d))
        return self.pack(recs)

    def pack(self, recs) -> "Columns":
        """Batch the flows of all columns (core 4.9 outcome tree on a quarterly grid)."""
        p, T, Q = self.p, self.T, self.Q
        C = len(recs)
        tr, bd, sh = p.transition, p.build, p.shocks
        tau, psi, op = self.tau, self.psi, 1 - self.tau
        if C == 0:
            return Columns.empty(T, Q)
        g = lambda k: np.array([r[7][k][r[5]] if np.ndim(r[7][k]) else r[7][k] for r in recs], dtype=float)
        pidx = np.array([r[0] for r in recs]); level = np.array([r[1] for r in recs]); s = np.array([r[2] for r in recs], float)
        variant = np.array([r[3] for r in recs], dtype=object); pilot = np.array([r[4] for r in recs]); y0 = np.array([r[5] for r in recs])
        tau0 = np.array([r[6] for r in recs]) + np.array([r[7]["T_st"][r[5]] if np.ndim(r[7]["T_st"]) else r[7]["T_st"] for r in recs], float)
        W = np.stack([r[7]["W"] for r in recs])                                   # (C, T)
        Fv, Fb, K, CJ, Cpar, Cstr, Lroll, Tpar, pu = (g(k) for k in ("F", "F_build", "K", "C_J", "C_par", "C_str", "L_roll", "T_par", "p_u"))
        I, Cwo, dK, varpi, payback = g("I"), g("C_wo"), g("dK"), g("varpi"), g("payback")
        aff, fte_rm = g("affected"), g("fte_removed")
        reviews = g("reviews"); reg = np.array([r[7]["regulated"] for r in recs])
        has_int = level > 0
        T_int = np.where(has_int, bd.T_int, 0.0)
        T_pil = np.where(pilot > 0, p.pilot.T_pil, 0.0)
        lo = np.arange(Q) / QPY
        hi = lo + 1.0 / QPY
        tq = lo
        Wq = np.repeat(W, QPY, axis=1) / QPY
        ramp = _ramp_avg(tau0, Tpar, lo, hi)
        par = _overlap(tau0, tau0 + Tpar, lo, hi) * Cpar[:, None]
        at0, atP = _at(tau0, Q), _at(tau0 + Tpar, Q)
        intq = np.where(has_int[:, None], _overlap(s, s + np.maximum(T_int, 1e-9), lo, hi) / np.maximum(T_int, 1e-9)[:, None] * I[:, None], 0.0)
        # tax (prop:acct-tax): development is deducted (domestic, sec. 174A) or amortized over 15 years (foreign)
        # whatever the book treatment; equipment gets the bonus allowance. Book capitalization affects GAAP only.
        ac = p.accounting
        aF = 1 - tau * psi
        aI = 1 - tau * psi
        aK = 1 - tau * float(self.econ.info.get("psi_equipment", {}).get("psi", p.finance.psi_equipment))
        adopt = float(self.org.get("asu_2025_06_adoption_year") or ac.asu_2025_06_year)
        cap_F = np.where(self.econ.firm.base_year + s >= adopt, F.capitalized_share_asu(ac.u_novel, ac.dc_share), bd.capitalized_share_F)
        cap_I = bd.capitalized_share_I
        T_B = float(ac.T_B or bd.T_A)
        t_go = tau0 + (Tpar if ac.go_live == "after_parallel" else 0.0)
        reb = np.zeros((C, Q))
        for k in range(1, int(T / bd.T_A) + 2):
            tk = tau0 + k * bd.T_A
            reb += _at(np.where(tk < T, tk, 1e9), Q) * (Fb * (1 - bd.delta_F) ** (k * bd.T_A))[:, None]
        after = tq[None, :] >= (tau0 + Tpar)[:, None]
        repl = np.where(after, (dK * K)[:, None] / QPY, 0.0)
        b = np.array([r[7]["b_bar"] for r in recs], float)
        sav = b[:, None] * ramp * Wq
        strand, roll = atP * Cstr[:, None], atP * Lroll[:, None]
        F_pil = np.where(pilot > 0, p.pilot.cost_share * Fb + p.pilot.fixed_cost, 0.0)
        pil = _at(s + T_int, Q) * F_pil[:, None]
        one = at0 * (Fv + K + CJ)[:, None]
        pm = (pilot > 0)[:, None]
        pu_ = pu[:, None]
        # pre-tax cash
        c0 = np.where(pm, -(intq + pil), -(intq + one + par) - pu_ * (strand + roll))
        c1 = np.where(pm, -(one + par) + sav - repl - reb - strand, sav - repl - reb - (1 - pu_) * strand + pu_ * roll)
        # after tax
        a_one = at0 * (Fv * aF + K * aK + CJ * op)[:, None]
        a_succ = sav * op - repl * aK - reb * aF
        a0 = np.where(pm, -(intq * aI + pil * op), -(intq * aI + a_one + par * op) - pu_ * (strand + roll) * op)
        a1 = np.where(pm, -(a_one + par * op) + a_succ - strand * op, a_succ - (1 - pu_) * strand * op + pu_ * roll * op)
        # GAAP (pre-tax)
        # GAAP (prop:acct-path): capitalized builds amortize from go-live over the book life; the legacy write-off is
        # depreciated over the shortened life from commitment to cease-use; severance follows ASC 712 or 420
        amortF = _overlap(t_go, t_go + T_B, lo, hi) / T_B * (cap_F * Fv)[:, None]
        tI = s + T_int
        amortI = np.where(has_int[:, None], _overlap(tI, tI + T_B, lo, hi) / T_B * (cap_I * I)[:, None], 0.0)
        dep = np.where(tq[None] >= tau0[:, None], (K / p.capital.server_life_years / QPY)[:, None], 0.0)
        g_exp = at0 * (Fv * (1 - cap_F) + CJ)[:, None] + amortF + par + dep
        wo = _overlap(tau0, tau0 + np.maximum(Tpar, 1.0 / QPY), lo, hi) / np.maximum(Tpar, 1.0 / QPY)[:, None] * Cwo[:, None]
        Csev = g("C_sev")
        std = str(self.org.get("severance_standard") or ac.severance_standard)
        notice = float(self.org.get("jurisdiction", {}).get("notice_years", 0.0))
        t_com = np.maximum(tau0, tau0 + Tpar - notice)
        if std == "asc712":
            sev_g = _at(s, Q) * Csev[:, None]
        else:
            ratable = (tau0 + Tpar - t_com) * 365.0 > ac.retention_days
            span = np.maximum(tau0 + Tpar - t_com, 1.0 / QPY)
            sev_g = np.where(ratable[:, None], _overlap(t_com, t_com + span, lo, hi) / span[:, None] * Csev[:, None],
                             _at(t_com, Q) * Csev[:, None])
        strand_g = atP * (Cstr - Csev)[:, None] + sev_g                      # GAAP timing of the stranded costs
        capF_ = cap_F[:, None]
        g0 = np.where(pm, -(amortI + intq * (1 - cap_I) + pil), -(intq * (1 - cap_I) + amortI + g_exp) - pu_ * (strand_g + wo + roll))
        g1 = np.where(pm, -g_exp + sav - reb * (1 - capF_) - strand_g - wo, sav - reb * (1 - capF_) - (1 - pu_) * (strand_g + wo) + pu_ * roll)
        e0 = g0 + amortI + np.where(pm, 0.0, amortF + dep)
        e1 = g1 + np.where(pm, amortF + dep, 0.0)
        # regime shocks: a disruption in flight stops the remaining flows; the reusable part V_rec is recovered
        if sh.enabled and self.nu_D > 0:
            T_emb = np.minimum(np.where(np.isfinite(payback), payback, T), T) + (tau0 - s)
            rel_t = tq[None, :] + 0.5 / QPY - s[:, None]
            surv = np.exp(-self.nu_D * np.clip(rel_t, 0, T_emb[:, None]))
            V_rec = sh.s_reuse_platform * I + sh.s_reuse_on_platform * Fb - sh.C_rep_share * (Fv + I)
            rec = self.nu_D * surv / QPY * ((rel_t >= 0) & (rel_t <= T_emb[:, None])) * V_rec[:, None]
            a0, a1 = a0 * surv + rec, a1 * surv
            c0, c1 = c0 * surv + rec, c1 * surv
            g0, g1, e0, e1 = g0 * surv, g1 * surv, e0 * surv, e1 * surv
            surv_T = np.exp(-self.nu_D * np.minimum(np.maximum(T - s, 0), T_emb))
        else:
            surv_T = np.ones(C)
        a_crf = float(F.capital_recovery_factor(self.r, bd.T_A))
        tv1 = surv_T * (b * W[:, -1] * op - Fb * a_crf * aF - dK * K * aK)
        nopil = (pilot == 0)[:, None]
        sr_q = np.where(nopil, (strand + roll) * op, 0.0)
        sr_cash = _years(np.where(nopil, strand + roll, 0.0), T)
        sr_gaap = _years(np.where(nopil, strand + wo + roll, 0.0), T)
        bld = intq + pil + at0 * Fv[:, None]
        bld_q = intq * aI + pil * op + at0 * (Fv * aF)[:, None]
        T_emb_all = np.minimum(np.where(np.isfinite(payback), payback, T), T) + (tau0 - s)
        V_rec_all = sh.s_reuse_platform * I + sh.s_reuse_on_platform * Fb - sh.C_rep_share * (Fv + I)
        budget = _years(intq + pil + one, T)
        dual = _years(par, T)
        ya = np.minimum(tau0.astype(int), T - 1)
        yrs = np.arange(T)[None, :]
        affected = np.where(yrs == ya[:, None], aff[:, None], 0.0)
        e_unit = p.decisions.e_launch * (1 + p.decisions.e_regulated * reg) * self.e_mult
        load = np.where(yrs == np.minimum(s, T - 1)[:, None], e_unit[:, None], 0.0)
        gate_y = np.minimum((s + T_int + T_pil).astype(int), T - 1)
        load = load + np.where((yrs == gate_y[:, None]) & pm, p.decisions.e_gate * self.e_mult, 0.0)
        rev = np.where(yrs == ya[:, None], reviews[:, None], 0.0)
        frac = np.clip(yrs + 1 - tau0[:, None], 0, 1)
        fte = fte_rm[:, None] * frac
        detail = []
        for r in recs:
            d, y = r[7], r[5]
            detail.append({k: (float(d[k][y]) if np.ndim(d[k]) else d[k]) for k in
                           ("C0", "E_p", "C_par", "C_str", "C_wo", "F", "F_build", "F_anc", "I", "K", "C_J", "varpi", "T_par",
                            "p_u", "L_roll", "payback", "fte_removed", "affected", "risk", "sec_spend", "controls", "Cinc",
                            "Om_max", "C_disp", "C_brk", "only_U", "reviews", "tdebt", "b_bar", "J_auto", "icfr", "C_attr",
                            "U_share", "dK", "C_sev", "T_st", "tau_ann", "u_d", "itgc_annual", "itgc_setup", "interfaces",
                            "interface_annual", "fallback_annual", "close_delay_no_fallback", "icfr_units_automated", "tml",
                            "fallback_pays")} | {"W": d["W"], "y0": y})
        return Columns(proc=pidx, level=level, start=s.astype(int), variant=variant, pilot=pilot, tau0=tau0,
                       modes=[r[7]["md"] for r in recs], autonomy=[r[7]["autonomy"][:, r[5]] for r in recs],
                       cf0=a0, cf1=a1, tv1=tv1, cash0=_years(c0, T), cash1=_years(c1, T), gaap0=_years(g0, T),
                       gaap1=_years(g1, T), ebitda0=_years(e0, T), ebitda1=_years(e1, T),
                       logit0=logit(np.clip(varpi, 1e-6, 1 - 1e-6)), budget=budget, dual=dual, affected=affected,
                       load=load, reviews=rev, fte_removed=fte, platform=np.array([self._pinfo[i]["function"] for i in pidx], dtype=object),
                       has_ai=np.array([bool(r[7]["isA"].any() or (r[7]["md"] == U).any()) for r in recs]),
                       regulated=reg, detail=detail, sr_q=sr_q, sav_q=sav * op, bld_q=bld_q, sr_cash=sr_cash,
                       sav_cash=_years(sav, T), bld_cash=_years(bld, T), sr_gaap=sr_gaap, T_emb=T_emb_all, V_rec=V_rec_all,
                       p_u=np.where(pilot > 0, 0.0, pu), bbar=b, J_auto=np.array([r[7]["J_auto"] for r in recs], int))


def column_specs(cols: Columns, idx) -> list[tuple]:
    """(process, level, start, variant, pilot, modes) of the columns idx: enough to re-price them on another firm draw
    or scenario with PlanBuilder.reprice."""
    return [(int(cols.proc[i]), int(cols.level[i]), int(cols.start[i]), str(cols.variant[i]), int(cols.pilot[i]),
             np.asarray(cols.modes[i])) for i in idx]


def reprice(builder: "PlanBuilder", specs: list[tuple]) -> Columns:
    """Rebuild fixed plans (same modes, readiness and timing) on the builder's economics. Columns whose modes have
    become infeasible keep their slot with zero flows, so indices stay aligned."""
    p, T = builder.p, builder.T
    recs, keep = [], []
    for k, (pidx, level, s, variant, pilot, md) in enumerate(specs):
        tau0 = s + (p.build.T_int if level > 0 else 0.0) + (p.pilot.T_pil if pilot else 0.0)
        y0 = int(min(math.floor(tau0), T - 1))
        d = builder.terms(pidx, level, md)
        if d is None or not d["ok_y"][y0]:
            continue
        recs.append((pidx, level, s, variant, pilot, y0, tau0, d))
        keep.append(k)
    packed = builder.pack(recs)
    packed.keep = keep
    return packed
