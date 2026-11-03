# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Roadmap (spec Sections 9, 13.2, 14, 24.9): Wave 0 (measurement), then phased waves with dependencies (data
integration before the automation it gates), timing from the capability path, constraint utilization by year,
NPV, payback, risk and total cost of ownership per wave, and the firm's Rule-of-40 path on cash and GAAP bases
through the transition dip (core prop:tasks-scorepath; ext prop:ext-waves(f))."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from . import formulas as F
from .economics import A, H, N, O, U
from .plans import QPY

MODE_NAME = {H: "in-house", O: "outsourced", U: "augmented", A: "automated", N: "eliminated"}


def plan_frame(sol, prog, econ) -> pd.DataFrame:
    """One row per selected process: the plan as the roadmap reports it."""
    cols, f = prog.cols, econ.firm
    P = f.processes.reset_index(drop=True)
    rows = []
    for pr, c in sorted(sol.sel.items(), key=lambda kv: (prog.cols.start[kv[1]], -prog.pv1[kv[1]])):
        d = cols.detail[c]
        md = cols.modes[c]
        us = np.flatnonzero(econ.unit_proc == pr)
        bm = econ.base_mode[us]
        ch = md != bm
        mix = {MODE_NAME[m]: int(np.sum(md[ch] == m)) for m in (A, U, O, N) if np.sum(md[ch] == m)}
        crit = f.units.critical.values[us].astype(bool) & (md == A)
        tf = econ.T_F[us, cols.level[c]]
        perc = float(np.max(tf[crit])) if crit.any() else (float(np.max(tf[md == A])) if (md == A).any() else float("nan"))
        val = float(prog.pv0[c] + sol.varpi[c] * prog.pv1[c])
        rows.append({"process_id": P.process_id.iat[pr], "process_name": P.process_name.iat[pr], "function_id": P.function_id.iat[pr],
                     "kind": P.kind.iat[pr], "column": int(c), "start_year": int(f.base_year + cols.start[c]),
                     "start_index": int(cols.start[c]), "adoption_time": float(cols.tau0[c]),
                     "readiness_from": float(econ.iota[pr, 0]), "readiness_to": float(econ.iota[pr, cols.level[c]]),
                     "integration_first": bool(cols.level[c] > 0), "pilot": bool(cols.pilot[c]), "variant": cols.variant[c],
                     "modes_changed": mix, "steps": int(len(us)), "fte_affected": d["affected"], "fte_removed": d["fte_removed"],
                     "saving_full_year": float(d["W"][min(d["y0"] + 1, econ.T - 1)]), "legacy_cost": d["C0"],
                     "one_time_cost": d["F"] + d["I"] + d["K"] + d["C_J"], "build_cost": d["F_build"], "integration_cost": d["I"],
                     "parallel_run_years": d["T_par"], "dual_running_per_year": d["C_par"], "stranded_cost": d["C_str"],
                     "success_probability": float(sol.varpi[c]), "success_probability_base": d["varpi"],
                     "payback_years": d["payback"], "value": val, "feasibility_date": perc,
                     "run_costs": float(np.mean(d["W"]) * 0 + d["risk"] + d["controls"]),
                     "security_spend": d["sec_spend"], "incident_risk_cost": d["risk"], "reviews": d["reviews"]})
    return pd.DataFrame(rows)


def waves(plan: pd.DataFrame, prog, econ, wave0: dict | None = None) -> list[dict]:
    """Group the plan into waves by start year. A process that raises readiness first appears in its wave as a
    data-integration item, and its automation follows T_int later (spec 9: data integration first)."""
    T = econ.T
    out = []
    if wave0:
        out.append({"wave": 0, "name": "Wave 0: measurement", "start_year": int(econ.firm.base_year), "items": wave0["items"],
                    "cost": wave0["cost"], "duration_years": wave0["duration_years"], "npv": -wave0["cost"],
                    "purpose": "process mining or event logs, time studies, a systems and data inventory and data classification"})
    if plan.empty:
        return out
    cols = prog.cols
    for k, (y, grp) in enumerate(plan.groupby("start_index"), start=1):
        idx = grp.column.values.astype(int)
        npv = float(grp.value.sum())
        flow = (cols.cash0[idx] + prog.cols.cash1[idx] * grp.success_probability.values[:, None]).sum(0)[int(y):]
        cum = np.cumsum(flow)
        neg = np.flatnonzero(cum < 0)
        if not neg.size:
            payback = 1.0
        else:
            pos = np.flatnonzero((cum >= 0) & (np.arange(len(cum)) > neg[0]))
            payback = float(pos[0] + 1) if pos.size else math.inf
        out.append({"wave": k, "name": f"Wave {k}", "start_year": int(econ.firm.base_year + y),
                    "processes": list(grp.process_id), "integration_first": list(grp.process_id[grp.integration_first]),
                    "pilots": list(grp.process_id[grp.pilot]), "fte_affected": float(grp.fte_affected.sum()),
                    "fte_removed": float(grp.fte_removed.sum()), "one_time_cost": float(grp.one_time_cost.sum()),
                    "dual_running_per_year": float(grp.dual_running_per_year.sum()), "npv": npv,
                    "payback_years_from_start": payback, "mean_success_probability": float(grp.success_probability.mean()),
                    "saving_full_year": float(grp.saving_full_year.sum()),
                    "depends_on": ["Wave 0"] + [f"data integration of {p}" for p in grp.process_id[grp.integration_first]]})
    return out


def utilization(sol, prog) -> pd.DataFrame:
    """Use of each constraint by plan year (spec 13.2, 14.2, 18.2)."""
    ev = sol.evaluation
    T = prog.T
    rows = []
    for y in range(T):
        rows.append({"year_index": y, "change_capacity_used": ev["cap_use"][y], "change_capacity": prog.capacity[y],
                     "decision_load": ev["load"][y], "decision_bandwidth": prog.Phi[y], "load_ratio": ev["x"][y],
                     "load_breakpoint": prog.info["x_hat"], "security_reviews": ev["nu"][y], "review_capacity": prog.Phi_sec[y],
                     "review_latency_years": float(F.review_latency(prog.Phi_sec[y], ev["nu"][y])),
                     "budget_used": ev["budget_use"][y], "budget": prog.budget[y], "dual_running_used": ev["dual_use"][y],
                     "dual_running_budget": prog.dual_budget[y], "launches": ev["launches"][y]})
    return pd.DataFrame(rows)


def score_path(sol, prog, econ, extra_cash: np.ndarray | None = None, extra_gaap: np.ndarray | None = None,
               revenue_delta: np.ndarray | None = None, growth_delta: np.ndarray | None = None) -> dict:
    """Rule-of-40 path on cash and GAAP bases (core prop:tasks-scorepath, ext prop:ext-waves(f)): baseline
    g + m each year, plus the plan's expected margin change: realized savings less dual running, one-time costs
    (cash: when paid; GAAP: expensed shares, amortization, depreciation, write-offs), program overheads and
    compliance, and the product side's revenue and margin effects."""
    f = econ.firm
    T = econ.T
    part1 = f.part1
    S = part1["S"] * econ.vf
    cols = prog.cols
    idx = np.array(sorted(sol.sel.values()), int)
    v = sol.varpi[idx] if len(idx) else np.zeros(0)
    cash = (cols.cash0[idx] + v[:, None] * cols.cash1[idx]).sum(0) if len(idx) else np.zeros(T)
    gaap = (cols.gaap0[idx] + v[:, None] * cols.gaap1[idx]).sum(0) if len(idx) else np.zeros(T)
    ebitda = (cols.ebitda0[idx] + v[:, None] * cols.ebitda1[idx]).sum(0) if len(idx) else np.zeros(T)
    # program-level costs (pre-tax): wave overheads, congestion, compliance once AI is deployed
    ev = sol.evaluation
    tau = econ.info["tau"]
    prog_cost = ev["launches"].clip(0, 1) * prog.O_w / (1 - tau) + prog.d2 / (1 - tau) * ev["launches"] ** 2
    first = ev.get("compliance_first_year", T)
    comp = np.where(np.arange(T) >= first, prog.info["annual_compliance"], 0.0)
    cash = cash - prog_cost - comp
    gaap = gaap - prog_cost - comp
    ebitda = ebitda - prog_cost - comp
    if extra_cash is not None:
        cash = cash + extra_cash
    if extra_gaap is not None:
        gaap = gaap + extra_gaap
        ebitda = ebitda + extra_gaap
    S_plan = S + (revenue_delta if revenue_delta is not None else 0.0)
    g = float(part1["g"])
    g_path = np.full(T, g) + (growth_delta if growth_delta is not None else 0.0)
    m_cash0, m_op0 = float(part1["m_cash"]), float(part1["m_op"])
    r40_cash_base = g + m_cash0
    r40_gaap_base = g + m_op0
    r40_cash = g_path + (m_cash0 * S + cash) / S_plan
    r40_gaap = g_path + (m_op0 * S + gaap) / S_plan
    d_cash = r40_cash - r40_cash_base
    d_gaap = r40_gaap - r40_gaap_base
    below_cash = np.flatnonzero(d_cash < 0)
    below_gaap = np.flatnonzero(d_gaap < 0)
    return {"years": [int(f.base_year + y) for y in range(T)], "revenue": S_plan, "r40_cash": r40_cash, "r40_gaap": r40_gaap,
            "r40_cash_base": np.full(T, r40_cash_base), "r40_gaap_base": np.full(T, r40_gaap_base),
            "delta_cash_points": 100 * d_cash, "delta_gaap_points": 100 * d_gaap,
            "dip_cash_points": float(100 * min(0.0, d_cash.min())), "dip_gaap_points": float(100 * min(0.0, d_gaap.min())),
            "dip_cash_years": int(len(below_cash)), "dip_gaap_years": int(len(below_gaap)),
            "final_uplift_cash_points": float(100 * d_cash[-1]), "final_uplift_gaap_points": float(100 * d_gaap[-1]),
            "cash_delta": cash, "gaap_delta": gaap, "ebitda_delta": ebitda, "gaap_base": m_op0 * S,
            "ebitda_base": prog.ebitda_base, "fcf_base": prog.fcf_base, "program_costs": prog_cost, "compliance_costs": comp}


def wave0(firm, p, voi: pd.DataFrame | None) -> dict:
    """Wave 0, measurement (spec 24.9): a firm-level systems and data inventory and data classification, plus
    process mining or event logs and time studies for the processes whose value of finer data (core
    prop:tasks-granularity) exceeds the cost of measuring them."""
    ms = p.measurement
    n_sys = int(firm.tiers.get("tier3", {}).get("systems_count") or 0) or \
        int(round(len(firm.functions) * p.readiness.default_n_systems))
    items = [{"item": "systems and data inventory", "scope": f"firm ({n_sys} systems)", "cost": ms.inventory_cost_per_system * n_sys,
              "duration_years": ms.inventory_years},
             {"item": "data classification (public, internal, confidential, restricted)", "scope": f"firm ({n_sys} systems)",
              "cost": ms.classification_cost_per_system * n_sys, "duration_years": ms.inventory_years}]
    if voi is not None and len(voi):
        for r in voi.itertuples():
            if r.measure:
                items.append({"item": "process mining or event logs and time study", "scope": r.process_id,
                              "cost": r.measurement_cost, "duration_years": ms.process_years, "value_of_information": r.value_of_tier})
    cost = float(sum(i["cost"] for i in items))
    dur = float(max(i["duration_years"] for i in items))
    return {"items": items, "cost": cost, "duration_years": dur}


def tco_by_wave(plan: pd.DataFrame, prog, econ) -> list[dict]:
    """Total cost of ownership per wave over the plan horizon (spec 18.5): one-time costs plus run, security,
    control and dual-running costs, undiscounted."""
    out = []
    T = econ.T
    for y, grp in plan.groupby("start_index"):
        run = 0.0
        for c in grp.column.values.astype(int):
            d = prog.cols.detail[c]
            years_running = max(T - prog.cols.tau0[c], 0)
            run += (d["risk"] + d["controls"]) * years_running + d["C_par"] * d["T_par"]
            run += float(np.sum(econ.run[np.flatnonzero(econ.unit_proc == prog.cols.proc[c])][:, :, A].sum(0)[int(prog.cols.tau0[c]):]
                                * (prog.cols.modes[c] == A).any()))
        out.append({"start_year": int(econ.firm.base_year + y), "one_time": float(grp.one_time_cost.sum()), "run_and_risk": run,
                    "total": float(grp.one_time_cost.sum()) + run})
    return out


# -------------------------------------------------------------------------------------------------
# Playbook (spec 29; notes/playbook_engine_spec.md): the generator lives in playbook.py
# -------------------------------------------------------------------------------------------------
def playbook(econ, prog, sol, plan: pd.DataFrame, waves_: list[dict], people_: dict, mc: dict | None, p, ing=None,
             priors=None, gsa=None, regime_name: str = "") -> dict:
    """The executable playbook of the firm (playbook.build): activity units (decisions per DWA in a step), process
    steps (execution), the data dictionary, the firm-task mapping and a summary."""
    from . import playbook as PB
    return PB.build(econ, prog, sol, plan, waves_, people_, mc, p, ing, priors, gsa=gsa, regime_name=regime_name)
