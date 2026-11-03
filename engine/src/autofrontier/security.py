# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Security, maintenance, compliance and AI failure modes for the report (spec 18, 20.2, 23; core 4.12, 4.13).

Per selected process: full-cost run lines (maintenance, revalidation, integrations, technical debt), the exposure
score, expected incident loss, the optimal security spend and residual risk cost (prop:tasks-security), build
versus buy (prop:tasks-buildbuy), scope exclusions by data class and loss tolerance; the security-review queue
(prop:tasks-secreview); and the failure-mode table: recommended autonomy level, review share, undetected error
rate, expected and tail (event CVaR) misbehavior loss, required controls, pipeline length against its maximum,
the automation-bias flag and provider concentration (common-mode risk)."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from . import formulas as F

H, O, U, A, N = F.H, F.O, F.U, F.A, F.N
LEVEL_NAME = {0: "read", 1: "draft", 2: "act with approval", 3: "act autonomously"}


def security_table(econ, prog, sol, p) -> pd.DataFrame:
    sec = p.security
    rows = []
    a_crf = econ.info["a_crf"]
    for c in sol.sel.values():
        pidx = int(prog.cols.proc[c])
        us = np.flatnonzero(econ.unit_proc == pidx)
        md = np.asarray(prog.cols.modes[c])
        isA = md == A
        d = prog.cols.detail[c]
        y = int(min(d["y0"] + 1, econ.T - 1))
        v = econ.firm.units.v.values[us] * econ.vf[y]
        FA = float(econ.F_build[us, y, A][isA].sum()) if isA.any() else 0.0
        pi_n = float(np.sum(econ.inference[us, int(prog.cols.level[c]), y, A][isA] * v[isA]) / max(np.sum(v[isA]), 1e-9)) if isA.any() else 0.0
        vA = float(np.sum(v[isA])) if isA.any() else 0.0
        bb = F.build_or_buy(FA, p.build.T_A, sec.delta_M, sec.reval_share * FA, sec.T_up, d["tdebt"], pi_n, sec.buy_markup,
                            FA * (1 + sec.buy_pooled_share), sec.reval_share * FA, max(vA * 5, 1.0), sec.buy_integration_share * FA,
                            sec.switching_cost_share * FA / max(sec.contract_years, 1e-9), vA) if isA.any() else None
        Cinc = d["Cinc"]
        dclass = str(econ.firm.processes.data_class.iat[pidx]) if "data_class" in econ.firm.processes else "internal"
        L_inc = float(np.max(econ.info["L_inc"][us])) if len(us) else 0.0
        L_max = float((econ.firm.security or {}).get("max_tolerable_loss") or sec.L_max)
        rows.append({"process_id": econ.firm.processes.process_id.iat[pidx], "process_name": econ.firm.processes.process_name.iat[pidx],
                     "data_class": dclass, "exposure_score": d["Om_max"], "expected_incident_loss": Cinc,
                     "security_spend": d["sec_spend"], "residual_risk_cost": d["risk"],
                     "maintenance_per_year": sec.delta_M * FA, "revalidation_per_year": sec.reval_share * FA * econ.info["reval_f"],
                     "technical_debt_per_year": d["tdebt"], "controls_per_year": d["controls"],
                     "build_or_buy": None if bb is None else bb["choice"],
                     "build_buy_volume_threshold": None if bb is None else bb["v_BB"],
                     "loss_per_incident": L_inc, "within_loss_tolerance": bool(L_inc * sec.tail_multiple <= L_max),
                     "security_reviews": d["reviews"],
                     "icfr_steps_automated": int(d.get("icfr_units_automated", 0)),
                     "itgc_per_year": float(d.get("itgc_annual", 0.0)), "itgc_setup": float(d.get("itgc_setup", 0.0)),
                     "new_interfaces_in_scope": int(d.get("interfaces", 0)),
                     "timeliness_cost_per_year": float(d.get("tml", 0.0)), "fallback_pays": bool(d.get("fallback_pays", False)),
                     "close_wait_cost_per_year": float(d.get("close_delay_no_fallback", 0.0))})
    return pd.DataFrame(rows)


def icfr_steps(econ, prog, sol) -> pd.DataFrame:
    """In-scope ICFR steps (spec 24.4) of every process, with channel, condition, status and whether the plan
    automates them (the agent then becomes an in-scope application)."""
    U = econ.firm.units
    if "icfr_status" not in U.columns:
        return pd.DataFrame()
    auto = set()
    for c in sol.sel.values():
        us = np.flatnonzero(econ.unit_proc == int(prog.cols.proc[c]))
        md = np.asarray(prog.cols.modes[c])
        auto |= set(U.unit_id.values[us][md == A].tolist())
    m = U.icfr_status.astype(str).isin(["in scope", "assumed in scope", "out (firm input)"])
    out = U.loc[m, ["process_id", "step", "title", "icfr_status", "icfr_channel", "icfr_condition", "icfr_decided_by",
                    "financial_system_written"]].copy()
    out["process_name"] = out.process_id.map(econ.firm.processes.set_index("process_id").process_name)
    out["channel"] = out.icfr_channel.map(lambda c: "; ".join(_CH.get(x.strip(), x.strip()) for x in str(c).split(";") if x.strip()))
    out["automated_in_plan"] = U.loc[m, "unit_id"].isin(auto).values
    return out.sort_values(["process_id", "step"]).reset_index(drop=True)


_CH = {"process": "a: transaction or estimate", "system": "b: in-scope system", "integration": "c: integration feeding an in-scope system",
       "policy": "d: ICFR-relevant policy"}


def review_queue(prog, sol, p) -> dict:
    """Security-review queue (prop:tasks-secreview): load nu against capacity Phi_sec, latency, value lost and the
    optimal capacity at the price p_sec."""
    ev = sol.evaluation
    nu = np.asarray(ev["nu"], float)
    Phi = prog.Phi_sec
    y = int(np.argmax(nu)) if len(nu) else 0
    nu_y, Phi_y = float(nu[y]), float(Phi[y])
    vals = [float(prog.pv1[c]) for c in sol.sel.values()]
    V_dep = float(np.median(vals)) if vals else 0.0
    per, yr, marg = F.review_value_lost(Phi_y, nu_y, V_dep, prog.r_d) if Phi_y > nu_y else (math.inf, math.inf, math.inf)
    opt = F.optimal_review_capacity(nu_y, V_dep, prog.r_d, p.security.p_sec) if nu_y > 0 else 0.0
    return {"peak_year_index": y, "reviews_peak": nu_y, "capacity": Phi_y, "latency_years": float(F.review_latency(Phi_y, nu_y)),
            "value_lost_per_deployment": per, "value_lost_per_year": yr, "marginal_value_of_capacity": marg,
            "optimal_capacity": float(opt), "binding": bool(nu_y >= 0.95 * p.decisions.x_cap * Phi_y)}


def ai_review_chi(p) -> float:
    """Common-mode share of an AI reviewer on another provider (prop:tasks-cerr(c)): rho^cm = P(the reviewing model
    also errs | the producing model errs) x P(same wrong answer | both wrong). Only the second factor is measured (Kim,
    Garg, Peng and Garg 2025: 0.60 on HELM); the first is a scenario value (reliability.ai_review_joint_error)."""
    rl = p.reliability
    return float(rl.ai_review_joint_error) * float(rl.ai_review_agreement)


def change_controls_share(econ, p) -> float:
    """Share q_chg of model, prompt and tool regressions that change-management controls stop (pinned versions,
    testing before promotion, rollback): the firm's input (tier3_security change_controls_share) or the default."""
    sec_in = econ.firm.security or {}
    v = sec_in.get("change_controls_share")
    return float(p.reliability.q_chg if v is None else v)


def nu_cm_effective(econ, p) -> float:
    """Provider common-mode events a year after change controls (ass:ext-commonmode; Part I lem:fullcost(e)):
    nu_cm = nu_out + (1 - q_chg) nu_reg, with nu_reg = reliability.regression_share x reliability.nu_cm (the measured
    rate, outages plus disclosed regressions, is taken as the rate without change controls)."""
    rl = p.reliability
    s = float(rl.regression_share)
    return F.nu_common_mode((1 - s) * rl.nu_cm, s * rl.nu_cm, change_controls_share(econ, p))


def common_mode_cost(econ, prog, sol, p) -> dict:
    """Expected annual common-mode cost of the plan (prop:ext-commonmode(a), in the engine's event model of the Monte
    Carlo, risk.outcome_draws): each provider event degrades the share cm_days/365 x cm_burst + downtime/(8760 nu_cm)
    of a year of the exposed savings, of every process on the provider with probability rho and of one otherwise.
    Reported next to c_err in the full-automation ceiling (ext notes 4.8)."""
    rl = p.reliability
    T = econ.T
    W = np.array([max(float(prog.cols.detail[c]["W"][min(prog.cols.detail[c]["y0"] + 1, T - 1)]), 0.0) for c in sol.sel.values()])
    if not len(W) or not rl.enabled:
        return {"mean": 0.0, "nu_cm": nu_cm_effective(econ, p), "exposure": 0.0}
    k = int(econ.firm.org.get("providers") or rl.providers)
    prov = np.arange(len(W)) % max(k, 1)
    share_ev = rl.cm_days / 365.0 * rl.cm_burst + rl.downtime_hours / 8760.0 / max(rl.nu_cm, 1e-9)
    rho = float(rl.provider_correlation)
    nu = nu_cm_effective(econ, p)
    tot = sum(rho * W[prov == m].sum() + (1 - rho) * W[prov == m].mean() for m in np.unique(prov))
    return {"mean": float(nu * share_ev * tot), "nu_cm": nu, "share_per_event": share_ev, "exposure": float(W.sum()), "providers": k}


def failure_modes(econ, prog, sol, p) -> pd.DataFrame:
    """AI failure modes and controls by process (spec 23.1; core 4.13)."""
    rel = econ.info.get("reliability")
    rl = p.reliability
    rows = []
    prov = int(econ.firm.org.get("providers") or rl.providers)
    hhi = F.concentration_hhi(np.ones(max(prov, 1)))
    for c in sol.sel.values():
        pidx = int(prog.cols.proc[c])
        us = np.flatnonzero(econ.unit_proc == pidx)
        md = np.asarray(prog.cols.modes[c])
        isA = md == A
        isU = md == U
        y = int(min(max(prog.cols.tau0[c], 0) + 1, econ.T - 1))
        l = int(prog.cols.level[c])
        v = econ.firm.units.v.values[us] * econ.vf[y]
        row = {"process_id": econ.firm.processes.process_id.iat[pidx], "process_name": econ.firm.processes.process_name.iat[pidx],
               "automated_steps": int(isA.sum()), "augmented_steps": int(isU.sum())}
        if rel is not None and isA.any():
            ua = us[isA]
            lev = rel["autonomy"][ua, l, y]
            row["recommended_autonomy"] = LEVEL_NAME[int(np.max(lev))]
            row["steps_act_with_approval"] = int(np.sum(lev == 2))
            row["steps_act_autonomously"] = int(np.sum(lev == 3))
            row["review_share"] = float(np.average(rel["xi"][ua, l, y], weights=np.maximum(v[isA], 1e-9)))
            row["undetected_error_rate"] = float(np.average(rel["resid"][ua, l, y], weights=np.maximum(v[isA], 1e-9)))
            row["hallucination_rate"] = float(np.average(rel["h"][ua, l, y], weights=np.maximum(v[isA], 1e-9)))
            el = float(np.sum(rel["c_m"][ua, l, y] * v[isA]))
            row["expected_misbehavior_loss_per_year"] = el
            row["event_cvar"] = float(np.max(rel["cvar_event"][ua]))
            row["error_floor_cost_per_year"] = float(np.sum(rel["c_err"][ua, l, y] * v[isA]))
            # the same floor at full automation, at the review that remains (prop:tasks-cerr(c); Part I lem:fullcost(c)):
            # no review (the ceiling's convention: the measured catch rates are human reviewers'), and one AI review
            # layer on another provider that shares the producing model's error with probability chi
            eo_, eh_ = rel["e_o"][ua, l, y], rel["h"][ua, l, y]
            L_ = np.asarray(econ.info["L_err"])[ua]
            cm_ = rel["c_m"][ua, l, y]
            row["error_floor_no_review_per_year"] = float(np.sum(F.cerr_remaining_review(eo_, eh_, L_, cm_) * v[isA]))
            row["error_floor_ai_review_per_year"] = float(np.sum(F.cerr_remaining_review(
                eo_, eh_, L_, cm_, rel["d_o"][ua, l, y], rel["d_h"][ua, l, y], ai_review_chi(p), int(rl.ai_review_layers)) * v[isA]))
            row["automation_bias_irony"] = bool(np.any(rel["irony"][ua, l, y]))
            row["irreversible_steps"] = int(np.sum(rel["irreversible"][ua]))
            ctrl = ["monitoring with detection lag", "kill switch and rollback"]
            if (econ.info["writes"][ua] > 0).any():
                ctrl.insert(0, "least privilege on write and transaction rights")
            if np.any(rel["irreversible"][ua]) or np.any(lev == 2):
                ctrl.append("mandatory human approval for irreversible actions")
            if np.any(econ.info["ext_in"][ua] > 0.3):
                ctrl.append("prompt-injection defenses on external inputs")
            row["required_controls"] = "; ".join(ctrl)
            J = int(prog.cols.J_auto[c]) if prog.cols.J_auto is not None else int(isA.sum())
            eps = float(np.mean(np.clip(rel["resid"][ua, l, y], 1e-6, 0.5)))
            qbar = float(np.min(econ.firm.units.r_bar.values[ua]))
            row["pipeline_length"] = J
            row["pipeline_max_length"] = float(F.max_pipeline_length(eps, qbar, 1, rl.J_s, rl.d_c)) if J >= 2 else None
            row["pipeline_success"] = float(F.pipeline_success(eps, max(J, 1))) if J >= 1 else None
            # decomposition (prop:tasks-pipeline(d)): success from the steps' human hours at the capability horizon
            if J >= 2 and "Hc" in econ.info:
                Hc = float(np.asarray(econ.info["Hc"])[min(y, len(np.asarray(econ.info["Hc"])) - 1)])
                d_k = econ.info["d_eff"][ua] if "d_eff" in econ.info else econ.firm.units.d.values[ua]
                row["pipeline_success_horizon"] = F.pipeline_success_decomposed(d_k, max(Hc, 1e-9), econ.p.capability.chi_form,
                                                                                econ.p.capability.eta_r)
            # detection threshold under automation bias (prop:tasks-bias(d)), with the catch rate measured at the AI's
            # own error rate (reliability.bias_prevalence_ratio times it); scenario parameter eps_d
            e_ua = np.clip(econ.e_raw[ua, l, y], 1e-6, 1.0)
            eb = np.maximum(1 - econ.firm.units.r_bar.values[ua], 1e-6)
            row["bias_target_attainable"] = bool(np.all(F.bias_target_attainable(rl.d_e, e_ua, rl.eps_d, np.minimum(eb, e_ua),
                                                                                  rl.bias_prevalence_ratio * e_ua)))
        elif isU.any():
            row["recommended_autonomy"] = "draft"
            row["required_controls"] = "human review of every output (augmentation)"
        row["providers"] = prov
        row["provider_hhi"] = hhi
        rows.append(row)
    df = pd.DataFrame(rows)
    df.attrs["common_mode"] = {"providers": prov, "hhi": hhi, "provider_events_per_year": nu_cm_effective(econ, p),
                               "provider_events_per_year_without_change_controls": rl.nu_cm,
                               "change_controls_share": change_controls_share(econ, p),
                               "regression_days": rl.cm_days, "share_of_requests_degraded": rl.cm_burst,
                               "correlation": rl.provider_correlation, "diversity_cost_per_process": rl.diversity_cost}
    return df


def accountability_floor(econ, prog, sol, p) -> dict:
    """a_min for financial-reporting processes as an ICFR constraint (prop:acct-amin, def:acct-admissible; Part I
    prop:amin): the cheapest control design that leaves no in-scope objective with a reasonable possibility (annual
    probability above accounting.eps_bar) of an undetected material misstatement, with AI layers allowed when the plan
    automates an ICFR-scope process; reported against the cheapest admissible human-only design, at eps_bar 1 and 5
    percent side by side (a scenario value with no central value, Paper 1 round 2 C1; accounting.eps_bar only selects
    the one the single-number ceiling uses), with the break-evens of each design in p_cc and in the human miss rate on
    AI-missed items (C2), and with the residual expected consequence outside a_min. C_acct is the KPMG 2025 SOX program
    budget of the firm's revenue class plus the accelerated-filer average audit fee (C3); the low bound uses the S&P 500
    fee ratio and the high case the large-accelerated-filer fee."""
    ac = p.accounting
    S = float(econ.firm.part1["S"] * econ.vf[-1])
    icfr_ai = any(bool(prog.cols.detail[c].get("icfr")) for c in sol.sel.values())
    dc = F.amin_direct_cost(S, ac.audit_fee, ac.sox_program_by_size, ac.audit_fee_per_musd, ac.audit_fee_high)
    C_acct = dc["central"]
    N_nm = ac.N_nm * S / 1e9
    # the plan's in-scope AI applications each carry an ITGC line (eq:acct-itgc) and a timeliness cost C^tml
    # (prop:acct-itgc(b), (d)); they enter a_min here and nowhere else in the ceiling (c_anc excludes them)
    det = [prog.cols.detail[c] for c in sol.sel.values()]
    lines = [float(d.get("itgc_annual", 0.0)) for d in det if d.get("icfr_units_automated", 0) > 0]
    C_tml = float(sum(float(d.get("tml", 0.0)) for d in det if d.get("icfr_units_automated", 0) > 0))
    run = lambda eps: F.amin_design(S, C_acct, icfr_ai or bool(lines), ac.C_itgc, ac.C_val, p.security.T_up, ac.control_types,
                                    ac.N_o, eps, ac.p_cc, N_nm, ac.L_nm, ac.L_mm, itgc_lines=lines, C_tml=C_tml, separate=False)
    des = run(float(ac.eps_bar))
    des["by_eps_bar"] = {f"{e:g}": {k: v for k, v in run(e).items() if k in ("design", "a_min", "admissible", "annual_miss_probability",
                                                                               "a_min_human_only", "human_only_admissible",
                                                                               "human_only_design", "residual_expected_consequence",
                                                                               "breakeven", "human_only_breakeven")}
                         for e in (0.01, 0.05)}
    des["eps_bar_note"] = ("no central value: the floor is reported at 1 and 5 percent; accounting.eps_bar "
                           f"({float(ac.eps_bar):g}) only selects the value the single-number ceiling uses")
    des["direct_cost"] = dc
    des["a_min_direct_cost_low"] = des["a_min"] + (dc["low"] - dc["central"]) / S if np.isfinite(des["a_min"]) else math.inf
    des["a_min_direct_cost_high"] = des["a_min"] + (dc["high"] - dc["central"]) / S if np.isfinite(des["a_min"]) else math.inf
    des["icfr_processes_automated"] = icfr_ai
    des["in_scope_ai_applications"] = len(lines)
    des["a_min_default"] = p.finance.a_min_fixed
    des["note"] = ("admissibility is pass/fail; the consequence of a material misstatement is reported, not traded against cost; "
                   "errors below materiality enter as N_nm L_nm P and are not added to c_err (no double count)")
    return des


def ceiling_terms(econ, prog, sol, p, fails: pd.DataFrame, sec_tab: pd.DataFrame) -> dict:
    """Full-cost terms for the Part I ceiling (spec 22; core 4.13): maintenance c_mnt, security c_sec, ancillary
    c_anc and the error floor c_err as shares of revenue in the final plan year, and the ceiling with them. For
    financial-reporting processes a_min comes from the control-design minimum (prop:acct-amin) and their error
    floor is excluded from c_err."""
    S = float(econ.firm.part1["S"] * econ.vf[-1])
    c_mnt = float((sec_tab.maintenance_per_year + sec_tab.revalidation_per_year + sec_tab.technical_debt_per_year).sum()) / S if len(sec_tab) else 0.0
    c_sec = float((sec_tab.security_spend + sec_tab.residual_risk_cost).sum()) / S if len(sec_tab) else 0.0
    c_anc = float(sec_tab.controls_per_year.sum() + prog.info.get("annual_compliance", 0.0)) / S if len(sec_tab) else 0.0
    icfr_ids = {econ.firm.processes.process_id.iat[int(prog.cols.proc[c])] for c in sol.sel.values()
                if prog.cols.detail[c].get("icfr")}
    if len(fails) and "error_floor_cost_per_year" in fails:
        c_err = float(fails.loc[~fails.process_id.isin(icfr_ids), "error_floor_cost_per_year"].fillna(0).sum()) / S
    else:
        c_err = 0.0
    amin = accountability_floor(econ, prog, sol, p)
    pt = econ.firm.part1
    # Part I's floor assumes human-only financial controls: the best layered design lowers it by the difference
    # (with the constrained floor both are cheapest admissible designs; if no human-only design is admissible, Part I's
    # human-only floor is itself not admissible at eps_bar and no gain is credited: the report says so)
    gain = max(amin["a_min_human_only"] - amin["a_min"], 0.0) if (amin["icfr_processes_automated"] and np.isfinite(amin["a_min_human_only"])
                                                                   and np.isfinite(amin["a_min"])) else 0.0
    # the design gain lowers Part I's default floor; the plan's in-scope AI applications add their ITGC lines and
    # timeliness costs on top (prop:acct-itgc(b); accounting notes 4.7)
    S_y = float(econ.firm.part1["S"] * econ.vf[-1])
    a_min = max(p.finance.a_min_fixed - gain, 0.0) + (amin.get("itgc_lines_total", 0.0) + amin.get("C_tml", 0.0)) / S_y
    base = F.R_max(pt["tau"], pt["c_c"], pt["f"], p.finance.a_min_fixed, 1.0, pt["k"], pt["G"])
    full = F.R_max(pt["tau"], pt["c_c"], pt["f"], a_min, 1.0, pt["k"], pt["G"]) - (1 - pt["tau"]) * (c_mnt + c_sec + c_anc + c_err)
    # the same ceilings at Part I's compute share at full automation in the plan's last year (finance.c_c_full_automation,
    # by horizon; params commit 29 Oct 2026), next to the firm's current compute share
    year = float(econ.firm.base_year + econ.T - 1)
    cc_H = compute_share_at(year, p.finance.c_c_full_automation)
    base_H = F.R_max(pt["tau"], cc_H, pt["f"], p.finance.a_min_fixed, 1.0, pt["k"], pt["G"])
    full_H = F.R_max(pt["tau"], cc_H, pt["f"], a_min, 1.0, pt["k"], pt["G"]) - (1 - pt["tau"]) * (c_mnt + c_sec + c_anc + c_err)
    # full automation without people (prop:tasks-cerr(c), ext notes 4.8; Part I lem:fullcost(c), (e)): c_err at the review
    # that remains (no review, the ceiling's convention; one AI layer on another provider as a sensitivity) and the
    # expected common-mode cost, both of the plan's automated processes
    c_err_nr = c_err_ai = 0.0
    if len(fails) and "error_floor_no_review_per_year" in fails:
        keep = ~fails.process_id.isin(icfr_ids)
        c_err_nr = float(fails.loc[keep, "error_floor_no_review_per_year"].fillna(0).sum()) / S
        c_err_ai = float(fails.loc[keep, "error_floor_ai_review_per_year"].fillna(0).sum()) / S
    cmc = common_mode_cost(econ, prog, sol, p)
    c_cm = cmc["mean"] / S
    full_np = F.R_max(pt["tau"], pt["c_c"], pt["f"], a_min, 1.0, pt["k"], pt["G"]) - (1 - pt["tau"]) * (c_mnt + c_sec + c_anc + c_err_nr + c_cm)
    full_np_H = F.R_max(pt["tau"], cc_H, pt["f"], a_min, 1.0, pt["k"], pt["G"]) - (1 - pt["tau"]) * (c_mnt + c_sec + c_anc + c_err_nr + c_cm)
    return {"c_mnt": c_mnt, "c_sec": c_sec, "c_anc": c_anc, "c_err": c_err, "a_min_used": a_min, "accountability": amin,
            "c_err_no_review": c_err_nr, "c_err_ai_review": c_err_ai, "ai_review_chi": ai_review_chi(p), "c_cm": c_cm,
            "common_mode": cmc, "R_max_without_people": full_np, "R_max_without_people_full_automation_compute": full_np_H,
            "R_max_rule_of_40_basis": base, "R_max_with_run_costs": full,
            "c_c_full_automation": cc_H, "c_c_year": year, "R_max_full_automation_compute_rule_of_40_basis": base_H,
            "R_max_full_automation_compute_with_run_costs": full_H,
            "note": "shares of revenue at the plan's scale; the Part I ceiling uses full automation, so these are lower bounds; "
                    "the *_full_automation_compute values use Part I's compute share at full automation for the plan's last year"}


def compute_share_at(year: float, path: dict) -> float:
    """Part I's compute share at full automation in a calendar year: linear between the knots of
    finance.c_c_full_automation ({year: share}), flat before the first and after the last."""
    pts = sorted((float(k), float(v)) for k, v in (path or {}).items())
    if not pts:
        return float("nan")
    xs, ys = [x for x, _ in pts], [y for _, y in pts]
    return float(np.interp(float(year), xs, ys))
