# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Scenarios, sensitivity and robustness (spec 5, 8, 20.2, 24.2, 24.7).

- Named scenarios: capability speed (slow, fast, plateau, AGI, constant-hazard reliability), an AI-native entrant,
  concentrated model supply, energy prices (fusion, shock), regulation (strict, light), the quantum flag and the
  industry pass-through set of competition.phi_ind_scenarios (pass_through_0 = fixed prices, _50, _70). Each is
  a set of parameter overrides; the engine re-optimizes under each and values every scenario's plan in every other
  scenario, which gives the regret matrix and the minimax-regret plan.
- The theta tornado of spec 5: the spend share of the available universe at the low and high end of each tax,
  regulation, ethics and preference parameter.
- Global sensitivity (spec 24.2): Morris screening over parameter groups, then within the top groups, then Sobol
  indices (Saltelli and Jansen estimators, own implementation) for the top parameters over their grounded ranges.
- Breakpoint distances per process (spec 8; core prop:tasks-breakpoints) and should-versus-could labels from the
  competitive-adoption logic (ext prop:ext-should; spec 24.7, notes/competition_notes.md pending).
No network access; all randomness comes from the seed passed in."""
from __future__ import annotations

import math
import time

import numpy as np
import pandas as pd

from . import economics as E
from . import formulas as F
from . import optimize as O
from .plans import PlanBuilder, column_specs

A, U, N, H, Om = F.A, F.U, F.N, F.H, F.O


def scenario_set(p, firm) -> dict:
    """Named scenarios: overrides of parameters (dotted keys), with a plain description."""
    cap = p.capability
    lo_td, hi_td = p.range("capability.Td_years")
    by = int(firm.base_year)
    rivals = p.competition.n_rivals
    M = p.competition.replication_share * (rivals - 1)
    phi_entrant = 1.0 - float(F.retained_share(rivals, M))
    # industry pass-through as a scenario dimension (params commit 29 Oct 2026; competition.phi_ind_scenarios). Part I
    # round 2: phi is the rate at which unit-cost savings the rivals make reach the price (all savings in the score,
    # margins at the post-cut price); the firm keeps dur = 1 - phi (1 - HHI) of the DOLLAR saving of a replicated
    # cost-of-revenue cut (cor:ext-game-engine(a)); phi = 0 is the fixed-prices case. The central scenario uses
    # competition.phi_ind = 0.5 unless the firm gives one (pass_through_50 then equals the central case); the derived
    # Cournot value is reported as a benchmark.
    hhi = float((getattr(firm, "fin", None) or {}).get("market_hhi") or p.competition.hhi)
    pass_through = {}
    for phi in p.competition.phi_ind_scenarios or []:
        phi = float(phi)
        nm = f"pass_through_{int(round(100 * phi))}"
        what = "fixed prices: no cost-of-revenue saving is passed to customers" if phi == 0 else \
            f"industry pass-through rate {phi:g} on unit-cost savings the rivals make (margins at the post-cut price); the firm keeps {1 - phi * (1 - hhi):.0%} of the dollar value of a replicated cost-of-revenue saving"
        pass_through[nm] = {"desc": what, "set": {"competition.phi_ind": phi}}
    return {
        "central": {"desc": "defaults and the firm's inputs", "set": {}},
        "capability_slow": {"desc": f"task horizons double every {hi_td * 365:.0f} days", "set": {"capability.Td_years": hi_td}},
        "capability_fast": {"desc": f"task horizons double every {lo_td * 365:.0f} days", "set": {"capability.Td_years": lo_td}},
        "capability_plateau": {"desc": f"task horizons stop growing after {by + 1}", "set": {"capability.plateau_year": float(by + 1)}},
        "agi_2030": {"desc": "cognitive tasks of any length become feasible in 2030", "set": {"capability.agi_year": 2030.0}},
        "constant_hazard": {"desc": "agent reliability follows a constant hazard (chi(0.8) = 3.1) instead of METR's logistic",
                            "set": {"capability.chi_form": "constant_hazard"}},
        "ai_native_entrant": {"desc": f"AI-native entrants force a further {phi_entrant:.0%} of unit-cost savings to customers",
                              "set": {"finance.pass_through_phi": phi_entrant}},
        "concentrated_supply": {"desc": "concentrated model supply: inference prices fall 5 times a year, not 10, and entrants keep a markup",
                                "set": {"prices.delta_pi": math.log(5.0), "product.ups_E": 1.0}},
        "energy_fusion": {"desc": "energy price falls to a tenth (fusion)", "set": {"prices.energy_index": 0.1}},
        "energy_shock": {"desc": "energy price triples", "set": {"prices.energy_index": 3.0}},
        "regulation_strict": {"desc": "human review of 30 percent of AI output everywhere, full review in high-risk uses, approval of irreversible actions",
                              "set": {"review.xi_min_none": 0.3, "review.xi_min_high_risk": 1.0}},
        "regulation_light": {"desc": "no oversight floor outside licensed work", "set": {"review.xi_min_high_risk": 0.0}},
        "quantum": {"desc": "early quantum risk: post-quantum migration by 2030 at higher cost (changes only that cost)",
                    "set": {"pqc.quantum_scenario": True}},
        "disruption_shocks": {"desc": "leadership changes and vision overhauls cancel work in flight on top of the survey-based "
                                      "realized share (counts disruption twice unless the firm's realized share excludes it)",
                              "set": {"shocks.disruption_haircut": True}},
        **pass_through,
    }


def apply(p, overrides: dict, origin: str):
    q = p.copy()
    for k, v in overrides.items():
        if q.has(k):
            q.set(k, v, origin=origin)
    return q


# -------------------------------------------------------------------------------------------------
# Scenarios with re-optimization and regret
# -------------------------------------------------------------------------------------------------
_WORK: dict = {}


def _scenario_job(nm: str):
    """Solve one scenario (runs in a worker after fork, reading the shared inputs from _WORK)."""
    firm, p, regime, quick, sc = _WORK["firm"], _WORK["p"], _WORK["regime"], _WORK["quick"], _WORK["sc"]
    q = apply(p, sc[nm]["set"], f"scenario {nm}")
    ec = E.build_econ(firm, q)
    cols = PlanBuilder(ec).build(pilots=(0,) if quick else (0, 1))
    prog = O.make_program(cols, ec, regime, q)
    sol = O.solve(prog, method="heuristic", fixed_point=2) if quick else O.solve(prog)
    uni = E.universe(ec)
    y = min(2, ec.T - 1)
    sA = float(np.sum(uni["spend"] * (np.argmin(ec.ct[:, -1, y, :], 1) == A)) / max(uni["spend_total"], 1e-9))
    tf = ec.T_F[:, -1]
    info = {"desc": sc[nm]["desc"], "overrides": sc[nm]["set"], "plan_value": float(sol.value), "processes": len(sol.sel),
            "V_eco": uni["V_eco"], "economical_share": uni["shares"]["economical"], "automation_share": sA,
            "feasibility_median": float(np.median(tf[np.isfinite(tf)])) if np.isfinite(tf).any() else None,
            "pqc_cost": float(prog.info["pqc"].sum())}
    return nm, prog, sol, info


def run_scenarios(firm, p, regime, central_sol, central_prog, names=None, quick: bool = True, log=None,
                  workers: int = 1) -> dict:
    """Re-optimize under each scenario (with a reduced column set when quick), value each scenario's plan in every
    scenario, and report the regret matrix and the minimax-regret plan. The central scenario reuses the main run."""
    t0 = time.process_time()
    sc = scenario_set(p, firm)
    names = list(sc) if names is None else names
    progs, sols, info = {}, {}, {}
    todo = [nm for nm in names if nm != "central"]
    _WORK.update(firm=firm, p=p, regime=regime, quick=quick, sc=sc)
    results = []
    if workers > 1 and len(todo) > 1:
        import multiprocessing as mp
        try:
            with mp.get_context("fork").Pool(min(workers, len(todo))) as pool:
                results = pool.map(_scenario_job, todo)
        except (OSError, ValueError):
            results = [_scenario_job(nm) for nm in todo]
    else:
        results = [_scenario_job(nm) for nm in todo]
    _WORK.clear()
    for nm, prog, sol, inf in results:
        progs[nm], sols[nm], info[nm] = prog, sol, inf
        if log:
            log(f"scenario {nm}: value {sol.value / 1e6:,.0f}M, {len(sol.sel)} processes")
    if "central" in names:
        progs["central"], sols["central"] = central_prog, central_sol
        info["central"] = {"desc": sc["central"]["desc"], "overrides": {}, "plan_value": float(central_sol.value),
                           "processes": len(central_sol.sel)}
    plans = {nm: column_specs(progs[nm].cols, sorted(sols[nm].sel.values())) for nm in names}
    if "central" not in plans:
        plans["recommended"] = column_specs(central_prog.cols, sorted(central_sol.sel.values()))
    idx = {nm: O.column_index(progs[nm].cols) for nm in names}
    V = pd.DataFrame(index=list(plans), columns=names, dtype=float)
    for pl, specs in plans.items():
        for nm in names:
            V.loc[pl, nm] = O.value_of_plan(progs[nm], specs, idx[nm])["value"]
    best = V.max(axis=0)
    regret = best.values[None, :] - V.values
    R = pd.DataFrame(regret, index=V.index, columns=V.columns)
    max_regret = R.max(axis=1)
    mm = str(max_regret.idxmin())
    rec = "central" if "central" in plans else "recommended"
    return {"scenarios": info, "values": V, "regret": R, "max_regret": max_regret, "minimax_plan": mm,
            "recommended_max_regret": float(max_regret.get(rec, np.nan)),
            "recommended_is_minimax": bool(mm == rec or abs(max_regret.get(rec, np.inf) - max_regret.min()) < 1e-6 * max(abs(best.max()), 1.0)),
            "specs": plans, "programs": progs, "solutions": sols,
            "plans": {k: [s[0] for s in v] for k, v in plans.items()}, "seconds": time.process_time() - t0}


# -------------------------------------------------------------------------------------------------
# Spec 5: theta tornado of the available universe
# -------------------------------------------------------------------------------------------------
THETA = [("labor.tau_L", "payroll taxes and benefits"), ("finance.tau", "profit tax"), ("finance.psi", "deductibility of AI capital"),
         ("prices.tau_A", "automation tax on AI spend"), ("review.xi_min_high_risk", "oversight floor, high-risk uses"),
         ("review.xi_min_none", "oversight floor, other uses"), ("permissibility.licensed_share_threshold", "licensing threshold"),
         ("readiness.personal_data_cap", "data-protection cap on readiness"), ("permissibility.omega", "ethics penalty per automated unit"),
         ("permissibility.omega_h", "owner's value of a retained job"), ("permissibility.delta_G", "customer preference for human service"),
         ("permissibility.delta_lambda", "customer pull lost to automation")]


def theta_tornado(firm, p, year: int = 2) -> pd.DataFrame:
    """Spend share of the available universe S_A (optimal mode A, U or N) at the low and high end of each theta
    parameter (spec 5), sorted by swing."""
    def share(q):
        ec = E.build_econ(firm, q, horizon=year + 1)
        uni = E.universe(ec, year=year)
        return float(uni["shares"]["economical"])
    base = share(p)
    rows = []
    for key, label in THETA:
        if not p.has(key):
            continue
        rng = p.range(key)
        if not (isinstance(rng, (list, tuple)) and len(rng) == 2 and all(isinstance(x, (int, float)) for x in rng)):
            continue
        lo, hi = float(rng[0]), float(rng[1])
        if hi - lo <= 0:
            continue
        s_lo = share(apply(p, {key: lo}, "tornado"))
        s_hi = share(apply(p, {key: hi}, "tornado"))
        rows.append({"parameter": key, "meaning": label, "low": lo, "high": hi, "share_at_low": s_lo, "share_at_high": s_hi,
                     "base": base, "swing": abs(s_hi - s_lo), "grounding": p.grounding(key)})
    return pd.DataFrame(rows).sort_values("swing", ascending=False).reset_index(drop=True)


# -------------------------------------------------------------------------------------------------
# Spec 24.2: Morris screening, then Sobol indices
# -------------------------------------------------------------------------------------------------
ECON_SECTIONS = ("capability", "prices", "build", "readiness", "outsourcing", "augment", "review", "handoff", "eliminate",
                 "security", "reliability", "labor", "capital", "jurisdiction")


def _plan_units(econ, sol, prog) -> list[tuple]:
    """(process, readiness level, units, modes) of each process in the recommended plan, for the fast outputs."""
    out = []
    for c in sol.sel.values():
        pidx = int(prog.cols.proc[c])
        out.append((pidx, int(prog.cols.level[c]), np.flatnonzero(econ.unit_proc == pidx), np.asarray(prog.cols.modes[c])))
    return out


def fast_outputs(firm, q, plan, plan_modes=None, year: int = 3) -> np.ndarray:
    """Outputs for the sensitivity analysis from the economics alone (no re-optimization): economical universe value
    a year, automation spend share, the annual saving of the recommended plan's modes at plan year `year`, and that
    plan's five-year net value after its one-time build and integration costs (so the integration cost per system and
    the convexity of f(iota) = iota/(1 - iota)^kappa enter the indices)."""
    ec = E.build_econ(firm, q, horizon=year + 1)
    uni = E.universe(ec, year=year)
    lv = ec.L - 1
    ct = ec.ct[:, lv, year, :]
    sA = float(np.sum(uni["spend"] * (np.argmin(ct, 1) == A)) / max(uni["spend_total"], 1e-9))
    sav, one = 0.0, 0.0
    bd = q.build
    for pidx, l, us, md in plan:
        cash = ec.cash[us, l, year, :]
        base = cash[np.arange(len(us)), ec.base_mode[us]]
        new = cash[np.arange(len(us)), md]
        v = firm.units.v.values[us] * ec.vf[year]
        ok = np.isfinite(base) & np.isfinite(new)
        sav += float(np.sum(np.where(ok, (base - new) * v, 0.0)))
        ch = md != ec.base_mode[us]
        one += float(np.sum(ec.F_build[us[ch], 0, md[ch]]))
        if l > 0:
            one += float(F.integration_cost(ec.iota[pidx, 0], ec.iota[pidx, l], firm.processes.n_systems_p.iat[pidx],
                                            bd.int_cost_per_system, bd.int_convexity))
    r = q.finance.r
    npv5 = sav * (1 - math.exp(-5 * r)) / r - one
    return np.array([uni["V_eco"], sA, sav, npv5])


OUTPUT_NAMES = ("economical universe value a year", "automation spend share", "annual saving of the recommended plan",
                "five-year net value of the recommended plan after one-time costs")
OUT_KEYS = ("V_eco", "S_A", "plan_saving", "plan_npv5")


def _unit_to_value(p, key, u):
    lo, hi = (float(x) for x in p.range(key))
    v = lo + float(u) * (hi - lo)
    d = p.get(key)
    return int(round(v)) if isinstance(d, int) and not isinstance(d, bool) else v


def _eval_point(firm, p, keys_by_factor, u_vec, plan, _unused=None):
    ov = {}
    for f, u in zip(keys_by_factor, u_vec):
        for k in f:
            ov[k] = _unit_to_value(p, k, u)
    return fast_outputs(firm, apply(p, ov, "gsa"), plan)


def morris(firm, p, factors: list[list[str]], r: int, levels: int, rng, plan) -> pd.DataFrame:
    """Morris elementary effects (trajectory design, levels-grid, step Delta = levels/(2(levels - 1))) for factors
    that are single parameters or groups moved together. Returns mu*, mu and sigma per factor and output."""
    k = len(factors)
    delta = levels / (2.0 * (levels - 1))
    grid = np.arange(0, levels // 2) / (levels - 1)
    EE = np.zeros((r, k, len(OUT_KEYS)))
    for t in range(r):
        x = rng.choice(grid, k)
        y0 = _eval_point(firm, p, factors, x, plan)
        for i in rng.permutation(k):
            x2 = x.copy()
            x2[i] = x[i] + delta
            y1 = _eval_point(firm, p, factors, x2, plan)
            EE[t, i] = (y1 - y0) / delta
            x, y0 = x2, y1
    rows = []
    for i, f in enumerate(factors):
        row = {"factor": f[0] if len(f) == 1 else f"group {f[0].split('.')[0]} ({len(f)})", "keys": f}
        for o, name in enumerate(OUT_KEYS):
            row[f"mu_star_{name}"] = float(np.mean(np.abs(EE[:, i, o])))
            row[f"mu_{name}"] = float(np.mean(EE[:, i, o]))
            row[f"sigma_{name}"] = float(np.std(EE[:, i, o]))
        rows.append(row)
    df = pd.DataFrame(rows)
    # normalized score: mu* relative to the largest, averaged over outputs
    score = np.zeros(len(df))
    for name in OUT_KEYS:
        m = df[f"mu_star_{name}"].values
        score += m / max(m.max(), 1e-30)
    df["score"] = score / len(OUT_KEYS)
    return df.sort_values("score", ascending=False).reset_index(drop=True)


def sobol(firm, p, keys: list[str], N: int, rng, plan, n_boot: int = 100) -> dict:
    """First-order and total Sobol indices (Saltelli 2010 first-order, Jansen total) with bootstrap intervals, and
    the P10 to P90 bounds of each output over the sample (the 'Sobol bounds' for class d dependent outputs)."""
    from scipy.stats import qmc
    k = len(keys)
    seed = int(rng.integers(0, 2 ** 31 - 1))
    base = qmc.Sobol(d=2 * k, scramble=True, seed=seed).random(N)
    Am, Bm = base[:, :k], base[:, k:]
    facs = [[kk] for kk in keys]
    fA = np.array([_eval_point(firm, p, facs, a, plan) for a in Am])
    fB = np.array([_eval_point(firm, p, facs, b, plan) for b in Bm])
    fAB = np.zeros((k, N, len(OUT_KEYS)))
    for i in range(k):
        ABi = Am.copy()
        ABi[:, i] = Bm[:, i]
        fAB[i] = np.array([_eval_point(firm, p, facs, x, plan) for x in ABi])
    allf = np.concatenate([fA, fB])
    var = allf.var(axis=0)
    no = len(OUT_KEYS)
    S1 = np.zeros((k, no))
    ST = np.zeros((k, no))
    S1_ci = np.zeros((k, no, 2))
    for i in range(k):
        S1[i] = np.mean(fB * (fAB[i] - fA), axis=0) / np.maximum(var, 1e-30)
        ST[i] = 0.5 * np.mean((fA - fAB[i]) ** 2, axis=0) / np.maximum(var, 1e-30)
        bs = []
        for _ in range(n_boot):
            j = rng.integers(0, N, N)
            v_b = np.concatenate([fA[j], fB[j]]).var(axis=0)
            bs.append(np.mean(fB[j] * (fAB[i][j] - fA[j]), axis=0) / np.maximum(v_b, 1e-30))
        bs = np.array(bs)
        S1_ci[i] = np.stack([np.quantile(bs, 0.05, axis=0), np.quantile(bs, 0.95, axis=0)], axis=-1)
    rows = []
    for i, kk in enumerate(keys):
        row = {"parameter": kk, "grounding": p.grounding(kk), "range": p.range(kk)}
        for o, name in enumerate(OUT_KEYS):
            row[f"S1_{name}"] = float(S1[i, o])
            row[f"ST_{name}"] = float(ST[i, o])
            row[f"S1_{name}_ci"] = [float(S1_ci[i, o, 0]), float(S1_ci[i, o, 1])]
        rows.append(row)
    bounds = {name: {"P10": float(np.quantile(allf[:, o], 0.1)), "P50": float(np.quantile(allf[:, o], 0.5)),
                     "P90": float(np.quantile(allf[:, o], 0.9))} for o, name in enumerate(OUT_KEYS)}
    return {"indices": pd.DataFrame(rows), "bounds": bounds, "N": N, "evaluations": int(N * (k + 2))}


SOBOL_ALWAYS = ("build.int_cost_per_system", "build.int_convexity", "build.regulated_mult")


def global_sensitivity(firm, p, sol, prog, econ, seed: int, log=None) -> dict:
    """Morris over parameter groups (sections), Morris over the parameters of the top groups, then Sobol on the top
    parameters (spec 24.2). Class b and d parameters with numeric ranges only."""
    t0 = time.process_time()
    g = p.gsa
    rng = np.random.default_rng(seed)
    keys = [k for k in p.scenario_parameters(("b", "d")) if k.split(".")[0] in ECON_SECTIONS]
    groups: dict = {}
    for k in keys:
        groups.setdefault(k.split(".")[0], []).append(k)
    plan = _plan_units(econ, sol, prog)
    gfac = list(groups.values())
    m1 = morris(firm, p, gfac, int(g.morris_trajectories), int(g.morris_levels), rng, plan)
    top_groups = [row.keys for row in m1.head(2).itertuples()]
    inner = [[k] for grp in top_groups for k in grp]
    m2 = morris(firm, p, inner, max(int(g.morris_trajectories) - 1, 2), int(g.morris_levels), rng, plan) if inner else pd.DataFrame()
    top = [row.keys[0] for row in m2.head(int(g.sobol_top_k)).itertuples()] if len(m2) else []
    # the integration cost per system, the convexity of f(iota) and the regulated build multiplier decide the sign of
    # the core example (invoice chain): always in the Sobol set
    for k in SOBOL_ALWAYS:
        if k in keys and k not in top:
            top.append(k)
    sb = sobol(firm, p, top, int(g.sobol_n), rng, plan) if top else None
    if log:
        log(f"sensitivity: Morris over {len(gfac)} groups and {len(inner)} parameters, Sobol over {len(top)}")
    return {"morris_groups": m1, "morris_parameters": m2, "sobol": sb, "outputs": OUTPUT_NAMES,
            "parameters_screened": len(keys), "seconds": time.process_time() - t0}


# -------------------------------------------------------------------------------------------------
# Spec 8: breakpoint distances per process, and should-versus-could labels (spec 24.7)
# -------------------------------------------------------------------------------------------------
def breakpoints(econ, prog, sol, posterior: pd.DataFrame | None = None, year: int | None = None) -> pd.DataFrame:
    """Per selected process at its adoption year: distance to the inference-price breakpoint (pi*/pi - 1), the volume
    threshold (v/v* - 1), the review-floor detection threshold (d - d*), the readiness threshold (iota - iota_min),
    the capability feasibility date and years of slack, and the z-score of the value (core prop:tasks-breakpoints,
    prop:tasks-granularity)."""
    rows = []
    rl = econ.p.reliability
    rel = econ.info.get("reliability")
    for c in sol.sel.values():
        pidx = int(prog.cols.proc[c])
        us = np.flatnonzero(econ.unit_proc == pidx)
        md = np.asarray(prog.cols.modes[c])
        y = int(min(max(prog.cols.tau0[c], 0), econ.T - 1))
        l = int(prog.cols.level[c])
        isA = md == A
        v = econ.firm.units.v.values[us] * econ.vf[y]
        row = {"process_id": econ.firm.processes.process_id.iat[pidx], "process_name": econ.firm.processes.process_name.iat[pidx],
               "adoption_year": int(econ.firm.base_year + y)}
        if isA.any():
            ua = us[isA]
            cash = econ.cash[ua, l, y, :]
            alt = np.min(np.where(np.arange(5)[None, :] != A, cash, np.inf), axis=1)
            infA = econ.inference[ua, l, y, A]
            nonInf = cash[:, A] - infA
            ratio = np.where(infA > 0, (alt - nonInf) / np.maximum(infA, 1e-12), np.inf)
            wts = v[isA] * np.maximum(alt - cash[:, A], 0)
            row["price_breakpoint_distance"] = float(np.average(np.minimum(ratio, 1e6), weights=np.maximum(wts, 1e-12)) - 1)
            Fb = econ.F_build[ua, y, A] * econ.info["a_crf"] + econ.run[ua, y, A]
            gap = np.maximum(alt - cash[:, A], 1e-12)
            vstar = Fb / gap
            row["volume_threshold_distance"] = float(np.sum(v[isA]) / max(np.sum(vstar), 1e-12) - 1)
            if rel is not None:
                ebar = rel["e_o"][ua, l, y] + rel["h"][ua, l, y]
                eps_bar = 1 - econ.firm.units.r_bar.values[ua]
                dstar = F.detection_threshold(ebar, 1 - eps_bar)
                row["detection_rate_slack"] = float(np.min(rel["d_o"][ua, l, y] - dstar))
                row["autonomy_level"] = int(np.max(rel["autonomy"][ua, l, y]))
            iu = econ.iota_u[ua, l]
            row["readiness_slack"] = float(np.min(iu - econ.firm.units.iota_min.values[ua]))
            tf = econ.T_F[ua, l]
            row["feasibility_date"] = float(np.max(tf)) if np.isfinite(tf).all() else None
            row["capability_slack_years"] = float(econ.years[y] - np.max(tf)) if np.isfinite(tf).all() else None
        else:
            row["price_breakpoint_distance"] = None
        if posterior is not None and len(posterior):
            m = posterior[posterior.process_id == row["process_id"]]
            if len(m):
                row["z_value"] = float(m.z.iat[0])
        rows.append(row)
    return pd.DataFrame(rows)


def should_vs_could(econ, prog, sol, p) -> pd.DataFrame:
    """Should-versus-could labels with the adoption game (cor:ext-game-engine(b); spec 24.7). For each process, the
    best column's annual saving W splits into cost-of-revenue savings, which rivals replicate (durable share dur and
    private share priv of the HHI), and other savings. NPV^dur and NPV^priv use the success probability and the
    transition cost; flags: the dominant-strategy test (annualized adoption cost K < E^priv(n_c - 1)), the
    automation prisoner's dilemma (E^eq <= K < E^priv(n_c - 1)) and the AI-native-entry defensive and viability
    conditions (prop:ext-game-entry(c)); the market flip year when an entrant's limit price undercuts the firm's."""
    cols = prog.cols
    game = econ.info["game"]
    comp = p.competition
    r, G = prog.regime.r, float(econ.firm.part1["g"])
    rg = max(r - min(G, r - 0.01), 0.01)
    gam = float(econ.firm.part1["gamma"])
    a_crf = econ.info["a_crf"]
    best: dict = {}
    for i in range(len(cols)):
        pr = int(cols.proc[i])
        val = float(prog.pv0[i] + expit_(cols.logit0[i]) * prog.pv1[i])
        if pr not in best or val > best[pr][0]:
            best[pr] = (val, i)
    rows = []
    Ut = econ.firm.units
    n_c = max(int(round(game["n_c"])), 1)
    for pidx in range(len(econ.firm.processes)):
        us = np.flatnonzero(econ.unit_proc == pidx)
        feas = bool(econ.feas[us][:, -1, :, :][:, :, [U, A, N]].any())
        row = {"process_id": econ.firm.processes.process_id.iat[pidx], "process_name": econ.firm.processes.process_name.iat[pidx],
               "selected": pidx in sol.sel}
        if pidx not in best:
            row.update(label="not feasible" if not feas else "could-not-should", dominant_strategy=None, dilemma=None,
                       entry_defensive=None, entry_needed_for_viability=None)
            rows.append(row)
            continue
        val, i = best[pidx]
        d = cols.detail[i]
        y = int(min(d["y0"] + 1, econ.T - 1))
        W = float(max(d["W"][y], 0.0))
        cogs = econ.info["cogs"][us]
        v = Ut.v.values[us] * econ.vf[y]
        base = econ.cash[us, -1, y, :][np.arange(len(us)), econ.base_mode[us]]
        base = np.where(np.isfinite(base), base, 0.0)
        cogs_cost = float(np.sum(base[cogs] * v[cogs]))
        share_cogs = min(cogs_cost / max(float(np.sum(base * v)), 1e-9), 1.0)
        W_c, W_o = W * share_cogs, W * (1 - share_cogs)
        varpi = float(expit_(cols.logit0[i]))
        T_trans = d["F"] + d["I"] + d["C_J"] + d["C_str"] + d["C_par"] * d["T_par"]
        npv_dur = varpi * (game["dur_rep"] * W_c + W_o) / rg - T_trans
        npv_priv = varpi * (game["priv"] * W_c + W_o) / rg - T_trans
        K = (d["F"] + d["I"]) * a_crf + (r + 0.2) * d["K"]
        flags = {"dominant_strategy": None, "dilemma": None, "entry_defensive": None, "entry_needed_for_viability": None,
                 "market_flip_year": None}
        viability = False
        if W_c > 0 and cogs.any():
            Y = float(np.sum(v[cogs]))
            c0 = cogs_cost / max(Y, 1e-9)
            dd = W_c / max(Y, 1e-9)
            mg = c0 * gam / max(1 - gam, 1e-6)
            P0 = c0 + mg
            Epriv, Eeq = F.game_gains(mg, dd, Y, n_c)
            ds = F.dominant_strategy(K, Epriv[-1], Eeq)
            cA = econ.cash[us[cogs], -1, :, A]
            fin_ = np.isfinite(cA)
            cnt = fin_.sum(0)
            ent = np.where(cnt > 0, np.where(fin_, cA, 0.0).sum(0) / np.maximum(cnt, 1), np.inf) * (1 + comp.entrant_markup)
            PE = ent + comp.p_sw * P0
            PE_inf = float(PE[-1]) if np.isfinite(PE[-1]) else math.inf
            en = F.entry_defensive(PE_inf, P0, c0, dd, Y, K)
            viability = en["needed_for_viability"] and en["secures_viability"]
            flags.update(dominant_strategy=ds["dominant"], dilemma=ds["dilemma"], entry_defensive=en["defensive"],
                         entry_needed_for_viability=en["needed_for_viability"],
                         market_flip_year=F.flip_date(econ.years, np.where(np.isfinite(PE), PE, np.inf), np.full(econ.T, P0), 0.0))
        row.update(label=F.game_label(npv_dur, npv_priv, feas, viability), npv_durable=npv_dur, npv_private=npv_priv,
                   cogs_share_of_saving=share_cogs, annualized_cost=K, **flags)
        rows.append(row)
    out = pd.DataFrame(rows)
    out.attrs["game"] = game
    return out


def expit_(x):
    return 1.0 / (1.0 + np.exp(-x))
