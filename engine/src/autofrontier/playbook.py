# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""The executable playbook (spec 29; notes/playbook_engine_spec.md Sections 4 and 5).

Decisions are made per activity unit (an O*NET detailed work activity in a process step, or in a function's
residual work) and executed per process step. playbook_activities.csv has one row per activity unit and
playbook_steps.csv one row per process step; playbook_data_dictionary.csv defines every field. The theory supplies
the mode choice (prop:tasks-modes), the gates (prop:tasks-review(d), prop:tasks-halluc(b), prop:tasks-pilot(c)),
the thresholds (prop:tasks-breakpoints), the waves (prop:ext-waves) and the controls (prop:acct-itgc); the tier rule
is def:playbook-tier as the coordinator decided it. Fields the engine cannot compute are listed in NOT_COMPUTED."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from . import economics as E
from . import formulas as F
from .economics import A, H, N, O, U

VERSION = "1.0"
MODE = {H: "H", O: "O", U: "U", A: "A", N: "N"}
MODE_NAME = {H: "in-house", O: "outsourced", U: "augmented", A: "automated", N: "eliminated"}
AI = (U, A, N)
# impute-level keys change the firm's units (targets, loss multiples, readiness floors), not only its economics:
# the flip test recomputes those unit attributes (impute.retarget_units) before rebuilding the economics
IMPUTE_LEVEL = ("review.r_bar_high", "review.L_mult_regulated", "review.r_bar_licensed", "readiness.iota_min_regulated_add")
CYCLE_TIME_DEFAULT = "measure in Wave 0: event logs or process mining, or a time study"

NOT_COMPUTED = {
    "cross_process_dependencies": "dependencies between processes are not modeled (handoffs are within a process); "
                                  "depends_on lists Wave 0, data integration and the preceding step",
    "aei_augmentation_pct": "not in data/tasks/activities.csv yet (spec W6); the field is empty",
    "kpi_nrr_seat_exposure": "product KPIs are reported per product line in the product strategy section, not per step",
    "iota_star_process": "the readiness threshold iota*_p per process (spec W8) is not computed yet",
    "owner_capability": "owner capability inputs for permanent capital (spec W12) are not read yet; a permanent "
                        "owner's run values the target's own transformation at the owner's hurdle",
}


def _argmin_mode(ct_row, fallback):
    f = np.isfinite(ct_row)
    return int(np.argmin(np.where(f, ct_row, np.inf))) if f.any() else int(fallback)


def decisions(econ, l: int, y: int) -> np.ndarray:
    """Cheapest feasible mode of every unit at readiness level l and plan year y (prop:tasks-modes)."""
    ct = econ.ct[:, l, y, :]
    fin = np.isfinite(ct)
    m = np.argmin(np.where(fin, ct, np.inf), axis=1)
    return np.where(fin.any(1), m, econ.base_mode)


def flip_test(firm, p, econ, keys, priors=None) -> dict:
    """One class d input at a time at both range ends, the others at their defaults (def:playbook-tier): for each
    unit, the keys that change the automation decision (A or not) or the AI decision (U, A or N against H or O), now
    (level 0, plan year 0) and at target readiness (highest level, plan year 0), and the keys that only swap the mode
    within a class."""
    L = econ.L
    base = {w: decisions(econ, l, 0) for w, l in (("now", 0), ("target", L - 1))}
    nU = econ.nU
    flips = {w: [[] for _ in range(nU)] for w in base}
    swaps = [[] for _ in range(nU)]
    q = p.copy()
    tested = []
    import dataclasses
    from . import impute as IM
    for key in keys:
        if key in IMPUTE_LEVEL and priors is None:
            continue
        v0, rng = q.get(key), q.range(key)
        if not (isinstance(rng, (list, tuple)) and len(rng) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in rng)):
            continue
        tested.append(key)
        for end in rng:
            if end == v0:
                continue
            q.set(key, end, origin="playbook flip test")
            try:
                f2 = dataclasses.replace(firm, units=IM.retarget_units(firm, priors, q)) if key in IMPUTE_LEVEL else firm
                e2 = E.build_econ(f2, q, horizon=1)
            except Exception:                                   # a range end the economics cannot take: not a flip
                continue
            finally:
                q.set(key, v0, origin="playbook flip test")
            for w, l in (("now", 0), ("target", L - 1)):
                d2 = decisions(e2, l, 0)
                d1 = base[w]
                chA = (d1 == A) != (d2 == A)
                chAI = np.isin(d1, AI) != np.isin(d2, AI)
                for u in np.flatnonzero(chA | chAI):
                    if key not in flips[w][u]:
                        flips[w][u].append(key)
                if w == "now":
                    for u in np.flatnonzero((d1 != d2) & ~(chA | chAI)):
                        if key not in swaps[u]:
                            swaps[u].append(key)
    return {"flips": flips, "swaps": swaps, "tested": tested}


def flip_keys(p, gsa=None) -> list[str]:
    """The class d keys of the sections that can move a step's mode choice, plus the Sobol set when there is one."""
    secs = set(p.playbook.flip_sections)
    keys = [k for k in p.scenario_parameters(("d",)) if k.split(".")[0] in secs or k in IMPUTE_LEVEL]
    if gsa is not None and gsa.get("sobol") is not None:
        for k in gsa["sobol"]["indices"].parameter:
            if k not in keys and k in p.keys():
                keys.append(k)
    return keys


def pilot_bands(econ, prog, sol, p) -> dict:
    """Pilot band and gate (prop:tasks-pilot(c), eq:tasks-pilotband) for every process with a positive best column,
    in the plan or not (spec W7)."""
    from .risk import _pv_matrix
    cols = prog.cols
    D = _pv_matrix(econ.T, prog.regime.r, prog.regime.horizon)
    d = math.exp(-prog.regime.r * p.pilot.T_pil)
    out = {}
    for pr, cs in prog.by_proc.items():
        c = sol.sel.get(pr)
        if c is None:
            vals = [(float(prog.pv0[k] + cols.detail[k]["varpi"] * prog.pv1[k]), k) for k in cs if cols.has_ai[k]]
            if not vals or max(vals)[0] <= 0:
                continue
            c = max(vals)[1]
        varpi = float(sol.varpi[c]) if pr in sol.sel else float(cols.detail[c]["varpi"])
        Ys = float((cols.cf0[c] + cols.cf1[c]) @ D)
        Yf = float(cols.cf0[c] @ D + (cols.p_u[c] * cols.sr_q[c]) @ D) if cols.pilot[c] == 0 else float(cols.cf0[c] @ D)
        Fp = p.pilot.cost_share * cols.detail[c]["F_build"] + p.pilot.fixed_cost
        lo, hi, gate = F.pilot_band(Ys, min(Yf, -1e-9), Fp, d)
        out[pr] = {"pilot_band_low": lo, "pilot_band_high": hi, "gate_threshold": gate, "success_probability": varpi,
                   "value_of_pilot": F.pilot_value(varpi, Ys, min(Yf, -1e-9), Fp, d), "column": int(c)}
    return out


def _best_columns(prog, pr, L):
    """The process's best columns (prop:tasks-transition): at level 0 starting now, at the highest level starting
    now, and overall; None where no column has positive value."""
    cols = prog.cols
    cs = prog.by_proc.get(pr, [])
    val = {c: float(prog.pv0[c] + cols.detail[c]["varpi"] * prog.pv1[c]) for c in cs}
    def best(filt):
        cand = [(v, c) for c, v in val.items() if filt(c) and v > 0]
        return max(cand)[1] if cand else None
    lmax = max((int(cols.level[c]) for c in cs), default=0)
    return (best(lambda c: int(cols.level[c]) == 0 and int(cols.start[c]) == 0),
            best(lambda c: int(cols.level[c]) == lmax and int(cols.start[c]) == 0), best(lambda c: True), val)


def _binding(econ, u, l, y, v_star):
    """First failing test for automating unit u at (level l, year y), in the spec's order: permissibility,
    feasibility (physical, capability horizon), readiness, reliability (detection; residual or appetite), volume
    threshold, cost; none if A is the cheapest feasible mode. Returns (category, detail)."""
    i = econ.info
    if not econ.perm[u, A]:
        if i["excluded"][u]:
            return "permissibility", "ethics exclusion"
        if i["licensed"][u]:
            return "permissibility", "licensed sign-off"
        if not econ.data_allowed[u]:
            return "permissibility", "data class above the risk appetite"
        return "permissibility", "prohibited use"
    T_F = econ.T_F[u, l]
    if not np.isfinite(T_F) or econ.years[y] < T_F:
        phys = float(econ.firm.units.physical.iat[u]) >= float(econ.p.capability.physical_threshold)
        when = f"feasible from {T_F:.1f}" if np.isfinite(T_F) else "beyond the horizon"
        return ("feasibility: physical", f"physical work, {when}") if phys else ("feasibility: capability horizon", when)
    if not i["read_ok"][u, l]:
        return "readiness", "effective readiness below the step's floor"
    rel = i.get("reliability")
    if rel is not None and not bool(rel["ok"][u, l, y]):
        if not bool(rel["review_feasible"][u, l, y]):
            return "reliability: detection", "review cannot reach the quality target"
        return "reliability: residual or appetite", "tail loss above the appetite" if not bool(rel["appetite_ok"][u]) else "autonomy not allowed"
    if not econ.tech[u, l, y, A]:
        return "reliability: residual or appetite", "residual error above the quality target"
    ct = econ.ct[u, l, y]
    best = _argmin_mode(ct, econ.base_mode[u])
    if best == A:
        return "none", "automation is the cheapest feasible mode"
    v = float(econ.firm.units.v.iat[u])
    if v_star is not None and np.isfinite(v_star) and v < v_star:
        return "volume threshold", f"volume {v:,.0f} below v* {v_star:,.0f}"
    return "cost", f"{MODE_NAME[best]} is cheaper"


def task_index(priors) -> dict | None:
    """O*NET task statements by DWA (task_statements.csv through xw_task_dwa.csv) as arrays, cached on the priors
    object; None without the files."""
    if priors is None:
        return None
    cached = getattr(priors, "_task_index", None)
    if cached is not None:
        return cached
    ts, xw = getattr(priors, "task_statements", None), getattr(priors, "xw_task_dwa", None)
    if ts is None or xw is None:
        return None
    t = xw.merge(ts[["task_id", "task", "incumbents_responding"]], on="task_id", how="left").drop_duplicates(["dwa_id", "task_id"])
    out = {}
    for k, idx in t.groupby("dwa_id").indices.items():
        g = t.iloc[idx]
        out[k] = (g.task_id.to_numpy(), [str(x).split(";") for x in g.soc], g.task.to_numpy(), g.incumbents_responding.fillna(-1).to_numpy())
    try:
        object.__setattr__(priors, "_task_index", out)
    except Exception:
        pass
    return out


def _top_tasks(tix, dwa, socs_w: dict, n_ids=12, n_text=2):
    """Task ids and the top statements of a DWA, ranked by the step's occupation weight, then incumbents responding."""
    if tix is None:
        return None, None, None
    e = tix.get(dwa)
    if e is None or not len(e[0]):
        return 0, "", ""
    ids, socs, text, inc = e
    w = np.array([max((socs_w.get(x.strip(), 0.0) for x in sl), default=0.0) for sl in socs])
    order = np.lexsort((-inc, -w))
    return int(len(ids)), ";".join(str(int(ids[i])) for i in order[:n_ids]), " | ".join(str(text[i]) for i in order[:n_text] if pd.notna(text[i]))


def build(econ, prog, sol, plan, waves_, people_, mc, p, ing, priors, gsa=None, regime_name: str = "") -> dict:
    """The playbook of one firm: activity units, process steps, the data dictionary and a summary."""
    f = econ.firm
    Ut = f.units.reset_index(drop=True)
    P = f.processes.reset_index(drop=True)
    cols = prog.cols
    T, L = econ.T, econ.L
    base_year = int(f.base_year)
    rel = econ.info.get("reliability")
    pol = (ing.policy.model_dump() if getattr(ing, "policy", None) is not None else {}) if ing is not None else {}
    tier_c = float(p.playbook.tier_c_prob)
    wave_of, wave_start = {}, {}
    for w in waves_ or []:
        for pid in w.get("processes", []) or []:
            wave_of[pid], wave_start[pid] = int(w["wave"]), int(w["start_year"])
    plan_i = plan.set_index("process_id") if len(plan) else pd.DataFrame()
    rob = {}
    if mc and mc.get("robustness") is not None and len(mc["robustness"]):
        rob = dict(zip(mc["robustness"].process_id, mc["robustness"].share_of_draws_value_positive))
    sites = (people_ or {}).get("sites")
    T_leg = float(sites.T_leg.max()) if sites is not None and len(sites) and "T_leg" in sites else 0.0
    w_AI = float(((people_ or {}).get("talent") or {}).get("w_AI") or 0.0)
    ut = sol.evaluation
    bands = pilot_bands(econ, prog, sol, p)
    fl = flip_test(f, p, econ, flip_keys(p, gsa), priors)
    act = priors.activities.drop_duplicates("dwa_id").set_index("dwa_id")[["ai_usage", "aei_automation_pct", "n_tasks"]].to_dict("index") \
        if priors is not None else None
    pa = priors.process_activities if priors is not None else None
    sysmap = pa.groupby(["process_id", "step"]).typical_systems.first().to_dict() if pa is not None and "typical_systems" in pa else {}
    stepname = pa.groupby(["process_id", "step"]).step_name.first().to_dict() if pa is not None and "step_name" in pa else {}
    uo = f.unit_occ
    occ_t = priors.occupations.set_index("soc").title.to_dict() if priors is not None else {}
    occ_src = "Tier 2 roster" if ing is not None and getattr(ing, "roster", None) is not None and len(ing.roster) else "prior (occ_activity and function_occ)"
    uo_g = {k: g.groupby("soc").hours.sum().sort_values(ascending=False) for k, g in uo.groupby("unit_id")} if uo is not None else {}
    acc = p.accounting
    hpf = p.labor.hours_per_fte
    recs = list(Ut.itertuples(index=False))
    fname = f.functions.drop_duplicates("function_id").set_index("function_id").function_name.to_dict()
    tix = task_index(priors) if priors is not None else None
    d_o = np.asarray(rel["d_o"], float) if rel is not None and "d_o" in rel else None
    rows = []
    for pr in range(len(P)):
        us = np.flatnonzero(econ.unit_proc == pr)
        if not len(us):
            continue
        pid = P.process_id.iat[pr]
        c = sol.sel.get(pr)
        selected = c is not None
        c_now, c_tgt, c_best, _ = _best_columns(prog, pr, L)
        md = {k: (np.asarray(cols.modes[cc]) if cc is not None else econ.base_mode[us]) for k, cc in
              (("plan", c), ("now", c_now), ("target", c_tgt), ("best", c_best))}
        l_p = int(cols.level[c]) if selected else 0
        y_p = int(min(cols.start[c], T - 1)) if selected else 0
        d = cols.detail[c] if selected else {}
        prow = plan_i.loc[pid] if selected and pid in plan_i.index else None
        # program constraint for a positive process left out of the plan (prop:ext-waves(d))
        prog_bind = ""
        if not selected and c_best is not None:
            ratios = {"change capacity": max(ut["cap_use"][y] / max(prog.capacity[y], 1e-9) for y in range(T)),
                      "decision bandwidth": max(ut["x"][y] / max(prog.info.get("x_hat", 1.0), 1e-9) for y in range(T)),
                      "budget": max(ut["budget_use"][y] / max(prog.budget[y], 1e-9) for y in range(T)),
                      "security review capacity": max(ut["nu"][y] / max(prog.Phi_sec[y], 1e-9) for y in range(T))}
            k, v = max(ratios.items(), key=lambda kv: kv[1])
            prog_bind = f"{k} ({v:.0%} used at its peak)" if v >= 0.9 else "the regime's hurdle: other processes are worth more"
        n_icfr_auto = int(d.get("icfr_units_automated", 0) or 0)
        itgc_line = float(d.get("itgc_annual", 0.0) or 0.0)
        n_if, if_line = int(d.get("interfaces", 0) or 0), float(d.get("interface_annual", 0.0) or 0.0)
        changed = sorted({int(Ut.step.iat[x]) for k2, x in enumerate(us) if selected and int(md["plan"][k2]) != int(econ.base_mode[x])
                          and pd.notna(Ut.step.iat[x])})
        band = bands.get(pr, {})
        rb = rob.get(pid)
        for k_loc, u in enumerate(us):
            r = recs[u]
            m_now0 = int(econ.base_mode[u])
            m_act_now, m_act_tgt = (_argmin_mode(econ.ct[u, l, 0], m_now0) for l in (0, L - 1))
            first_A = next((base_year + y for y in range(T) if _argmin_mode(econ.ct[u, L - 1, y], m_now0) == A), None)
            m_plan = int(md["plan"][k_loc])
            # gates and thresholds at the target (highest level, plan year 0) and in the plan
            lt, yt = L - 1, 0
            qbar = float(r.r_bar)
            e_raw = float(econ.e_raw[u, lt, yt])
            d_now = (float(d_o[u, lt, yt]) if d_o.ndim == 3 else float(d_o[u]) if d_o.ndim == 1 else float(d_o)) \
                if d_o is not None else float(p.reliability.d_e)
            d_star = 1 - (1 - qbar) / e_raw if e_raw > 0 else 0.0
            resid = float(rel["resid"][u, lt, yt]) if rel is not None else float(econ.eps[u, lt, yt])
            ctT = econ.ct[u, lt, yt]
            c_alt = float(min(ctT[H], ctT[O]))
            cA, cA_var = float(ctT[A]), float(econ.cash[u, lt, yt, A])
            v = float(r.v)
            v_star = (v * (cA - cA_var) / (c_alt - cA_var)) if np.isfinite(cA) and np.isfinite(c_alt) and c_alt > cA_var else None
            b_now = _binding(econ, u, 0, 0, None)
            b_tgt = _binding(econ, u, lt, yt, v_star)
            # FTE, roles and controls in the plan
            tt = float(r.t) if float(r.t) > 0 else 1.0
            rh = float(econ.res_hours[u, l_p, y_p, m_plan])
            fte_after = float(r.fte) * rh / tt if np.isfinite(rh) else float(r.fte)
            icfr_on = str(getattr(r, "icfr_status", "")) in ("in scope", "assumed in scope")
            fsw = str(getattr(r, "financial_system_written", "") or "")
            occs = uo_g.get(int(r.unit_id))
            top_occ = "; ".join(f"{occ_t.get(s, s)} ({s})" for s in occs.index[:3]) if occs is not None and len(occs) else ""
            socs_w = (occs / occs.sum()).to_dict() if occs is not None and occs.sum() > 0 else {}
            n_t, t_ids, t_ex = _top_tasks(tix, r.activity_id, socs_w)
            ar = act.get(r.activity_id) if act is not None else None
            # gates: model thresholds by default, the firm's tier3_policy values where given
            g_err = pol.get("residual_error_tolerance")
            g_pil = pol.get("min_pilot_success")
            g_pay = pol.get("payback_limit_years")
            gates = []
            if m_plan in (A, U, N):
                gates.append(f"residual error at most {(g_err if g_err else 1 - qbar):.2%} through the parallel run "
                             f"({float(d.get('T_par', 0)):.2f} years) [{'firm policy' if g_err else 'model: 1 - quality target'}]")
                gates.append(f"reviewer catch rate at least {max(d_star, 0):.2f} [model: d* = 1 - (1 - qbar)/e]")
            if icfr_on and m_plan == A:
                gates.append(f"redesigned control runs through a quarter-end close (at least {float(acc.icfr_min_parallel):.2f} years) [model]")
            if band and selected:
                gates.append(f"pilot: scale if success probability at least {(g_pil if g_pil else band['gate_threshold']):.2f} "
                             f"[{'firm policy' if g_pil else 'model: pilot gate'}]")
            if g_pay and prow is not None and np.isfinite(float(prow.payback_years)):
                gates.append(f"cash payback at most {g_pay:.1f} years (plan {float(prow.payback_years):.1f}) [firm policy]")
            if fte_after < float(r.fte) - 1e-9 and m_plan in (A, N, O):
                gates.append(f"consultation and notice complete before dismissal (longest legal lead {365 * T_leg:.0f} days) [law]")
            pre = []
            if not int(r.tier4):
                pre.append("Wave 0: time study or process mining of the step")
            if selected and cols.level[c] > 0:
                pre.append(f"data integration to readiness {econ.iota[pr, cols.level[c]]:.2f} (from {econ.iota[pr, 0]:.2f})")
            if m_plan in (A, U):
                pre.append("evaluation set of the step's cases with known answers")
            # evidence keys with grounding class (a sourced, b precedent, c derived, d scenario)
            gk = lambda key: p.grounding(key) if p.has(key) else "d"
            vol_src = str(P.volume_source.iat[pr]) if "volume_source" in P and pd.notna(P.volume_source.iat[pr]) else "prior"
            # tier (def:playbook-tier)
            reasons = {}
            for w, b in (("now", b_now), ("target", b_tgt)):
                fk = fl["flips"][w][u]
                if fk or (rb is not None and rb < tier_c):
                    tier = "C"
                    why = (f"flips with {', '.join(fk[:6])}{' and more' if len(fk) > 6 else ''}" if fk else "") + \
                          ("; " if fk and rb is not None and rb < tier_c else "") + \
                          (f"value positive in {rb:.0%} of Monte Carlo draws (below {tier_c:.0%})" if rb is not None and rb < tier_c else "")
                elif b[0] in ("permissibility", "feasibility: physical", "feasibility: capability horizon"):
                    tier, why = "A", f"bound by {b[0]}, a filter the backtest supports"
                else:
                    tier, why = "B", f"rests on {b[0] if b[0] not in ('none',) else 'the cost crossover'} with sourced inputs (not validated by the backtest)"
                reasons[w] = (tier, why)
            gap = (cA - c_alt) / c_alt if np.isfinite(cA) and np.isfinite(c_alt) and c_alt > 0 else None
            T_F = float(econ.T_F[u, lt])
            sw = [f"catch rate d* {max(d_star, 0):.2f} vs now {d_now:.2f}",
                  f"readiness floor {float(r.iota_min):.2f} vs now {float(econ.iota_u[u, 0]):.2f} (target {float(econ.iota_u[u, lt]):.2f})",
                  f"capability date {T_F:.1f}" if np.isfinite(T_F) else "capability beyond the horizon",
                  f"volume v* {v_star:,.0f} vs {v:,.0f}" if v_star is not None else "volume: no threshold (automation never cheaper on run cost)",
                  f"cost gap {gap:+.0%}" if gap is not None else "cost gap: automation infeasible",
                  f"first year A is cheapest {first_A}" if first_A else "A is not cheapest within the horizon"]
            if fl["flips"]["target"][u]:
                sw.append("class d keys that flip it: " + ", ".join(fl["flips"]["target"][u][:6]))
            rows.append({
                "regime": regime_name, "unit_key": r.unit_key, "kind": r.kind, "function_id": r.function_id, "process_id": pid,
                "process_name": P.process_name.iat[pr], "step": r.step,
                "step_name": stepname.get((pid, float(r.step)), "") if pd.notna(r.step) else "residual work",
                "dwa_id": r.activity_id, "dwa_title": r.title, "gwa_id": r.gwa_id, "critical_path": int(r.critical),
                "iota0": float(econ.iota[pr, 0]), "volume_per_year": v, "hours_per_unit": float(r.t), "fte_in_house": float(r.fte),
                # 1 mode
                "mode_now": MODE[m_now0], "mode_activity_now": MODE[m_act_now], "mode_activity_target": MODE[m_act_tgt],
                "mode_step_now": MODE[int(md["now"][k_loc])], "mode_step_target": MODE[int(md["target"][k_loc])],
                "mode_plan_best": MODE[int(md["best"][k_loc])], "mode_plan": MODE[m_plan], "in_plan": selected,
                "first_year_A_at_target": first_A,
                # 2 binding
                "binding_now": b_now[0], "binding_now_detail": b_now[1], "binding_target": b_tgt[0], "binding_target_detail": b_tgt[1],
                "program_constraint": prog_bind, "icfr_status": getattr(r, "icfr_status", None), "icfr_channel": getattr(r, "icfr_channel", None),
                "icfr_condition": getattr(r, "icfr_condition", None), "regulated_class": r.regulated_class,
                # 3 preconditions
                "pre_readiness_floor": float(r.iota_min), "pre_readiness_now": float(econ.iota_u[u, 0]),
                "pre_readiness_target": float(econ.iota_u[u, lt]), "pre_review_share_target": float(econ.xi[u, lt, yt]),
                "pre_eval_set": m_plan in (A, U), "pre_itgc_lines": 1 if (icfr_on and m_plan == A) else 0,
                "typical_systems": sysmap.get((pid, float(r.step)), "") if pd.notna(r.step) else "", "preconditions": "; ".join(pre),
                # 4 gates
                "gate_min_detection": max(d_star, 0.0), "gate_detection_now": d_now,
                "gate_max_residual_error": float(g_err) if g_err else 1 - qbar, "residual_error_A_target": resid,
                "gate_min_volume": v_star, "pilot_band_low": band.get("pilot_band_low"), "pilot_band_high": band.get("pilot_band_high"),
                "gate_threshold": float(g_pil) if g_pil else band.get("gate_threshold"), "gates": "; ".join(gates),
                # 5 wave
                "wave": wave_of.get(pid) if selected else None, "wave_start_year": wave_start.get(pid) if selected else None,
                "depends_on": "; ".join(["Wave 0"] + ([f"data integration of {pid}"] if selected and cols.level[c] > 0 else [])
                                        + ([f"step {int(r.step) - 1} of {pid}"] if pd.notna(r.step) and int(r.step) > 1 and m_plan == A else [])),
                "moves_with_steps": ", ".join(map(str, changed)) if selected and m_plan != m_now0 and len(changed) > 1 else "",
                "integration_first": bool(selected and cols.level[c] > 0),
                # 6 roles
                "role_process_owner": f"head of {fname.get(r.function_id, r.function_id)}",
                "role_occupations": top_occ, "role_occupations_source": occ_src if top_occ else "",
                "role_ai_engineer_months": (float(econ.F_build[u, y_p, m_plan]) / (w_AI / 12.0)) if (w_AI > 0 and m_plan in (A, U)
                                            and np.isfinite(econ.F_build[u, y_p, m_plan])) else 0.0,
                "role_control_owner": "control owner (ICFR) in the step's function" if icfr_on else "",
                "role_reviewer_fte_target": float(econ.xi[u, lt, yt] * p.review.rho_rev * r.t * v / hpf) if m_plan == A else 0.0,
                "fte_after": fte_after, "fte_effect_target": fte_after - float(r.fte),
                "labor_lead_days": 365 * T_leg if fte_after < float(r.fte) - 1e-9 and m_plan in (A, N, O) else 0.0,
                # 7 KPIs
                "kpi_unit_cost_now": float(econ.ct[u, 0, 0, m_now0]), "kpi_unit_cost_plan": float(econ.ct[u, l_p, y_p, m_plan]),
                "kpi_residual_error": resid if m_plan == A else None, "kpi_review_share": float(econ.xi[u, lt, yt]) if m_plan == A else None,
                "kpi_cycle_time": (f"{float(r.cycle_time_days):.2f} days (Tier 4)" if pd.notna(getattr(r, "cycle_time_days", np.nan))
                                   else CYCLE_TIME_DEFAULT),
                "saving_per_year": v * float(econ.vf[y_p]) * (float(econ.ct[u, 0, 0, m_now0]) - float(econ.ct[u, l_p, y_p, m_plan]))
                if np.isfinite(econ.ct[u, l_p, y_p, m_plan]) else 0.0,
                # 8 controls
                "ctl_icfr": f"{getattr(r, 'icfr_status', None)}; channel {getattr(r, 'icfr_channel', None)}; {getattr(r, 'icfr_condition', None)}" if icfr_on else str(getattr(r, "icfr_status", None)),
                "ctl_itgc_line_usd": (itgc_line / max(n_icfr_auto, 1)) if (icfr_on and m_plan == A) else 0.0,
                "ctl_interface_line": float(acc.itgc_c_ifc) if (fsw and m_plan == A) else 0.0,
                "interface_lines_process": n_if if selected else 0, "interface_line_per_year_process": if_line if selected else 0.0,
                "fallback": ("manual close fallback pays" if d.get("fallback_pays") else "wait for the provider") if (icfr_on and m_plan == A) else "none needed",
                # 9 evidence (value plus grounding class)
                "ev_exposure_llm": float(r.exposure), "ev_exposure_llm_class": "a",
                "ev_aei_usage_share": float(ar["ai_usage"]) if ar is not None and pd.notna(ar.get("ai_usage")) else None,
                "ev_aei_automation_pct": float(ar["aei_automation_pct"]) if ar is not None and pd.notna(ar.get("aei_automation_pct")) else None,
                "ev_aei_class": "a", "ev_aei_augmentation_pct": None,
                "ev_task_hours": float(r.est_task_hours), "ev_task_hours_class": "a" if int(r.tier4) else "c",
                "ev_physical_share": float(r.physical), "ev_licensed_share": float(r.licensed_share),
                "ev_metr_feasibility_date": T_F if np.isfinite(T_F) else None,
                "ev_capability_margin_log": float(econ.log_margin[u, lt, yt]), "ev_capability_class": "a",
                "ev_detection_src": f"reliability.d_e={gk('reliability.d_e')}", "ev_target_src": "gwa_attributes r_bar=b",
                "ev_build_src": f"build.em_base={gk('build.em_base')}", "ev_review_time_src": f"review.rho_rev={gk('review.rho_rev')}",
                "ev_volume_src": f"{vol_src}=" + ("a" if "Tier" in vol_src else "d"),
                "ev_onet_task_links": n_t if n_t is not None else (int(ar["n_tasks"]) if ar is not None and pd.notna(ar.get("n_tasks")) else None),
                "ev_task_ids": t_ids, "ev_task_examples": t_ex,
                # 10 tier
                "tier_now": reasons["now"][0], "tier_now_reason": reasons["now"][1],
                "tier_target": reasons["target"][0], "tier_target_reason": reasons["target"][1],
                "mode_swap_params_now": ", ".join(fl["swaps"][u][:8]), "robustness_share_positive": rb,
                # 11 switches
                "switch_conditions": "; ".join(sw),
                "threshold_cost_gap_share": gap, "distance_capability_years": max(T_F - float(econ.years[0]), 0.0) if np.isfinite(T_F) else None,
                "distance_readiness": float(econ.iota_u[u, lt] - r.iota_min), "distance_reliability": (1 - qbar) - resid,
                "distance_detection": d_now - max(d_star, 0.0), "distance_volume": (v / v_star - 1) if v_star else None,
            })
    acts = pd.DataFrame(rows)
    steps = _steps(acts)
    summary = {} if acts.empty else {
        "activity_units": int(len(acts)), "steps": int(len(steps)),
        "mode_plan": acts.mode_plan.value_counts().to_dict(), "binding_target": acts.binding_target.value_counts().to_dict(),
        "tier_target": acts.tier_target.value_counts().to_dict(), "tier_now": acts.tier_now.value_counts().to_dict(),
        "fte_now": float(acts.fte_in_house.sum()), "fte_after": float(acts.fte_after.sum()),
        "flip_keys_tested": len(fl["tested"]), "firm_policy_gates": sorted(k for k, v in pol.items() if v is not None),
        "tasks_mapped": None if f.task_map is None else int((f.task_map.method != "unmapped").sum()),
        "tasks_unmapped": None if f.task_map is None else int(f.task_map.method.str.startswith("unmapped").sum())}
    return {"version": VERSION, "activities": acts, "steps": steps, "summary": summary, "not_computed": NOT_COMPUTED,
            "dictionary": dictionary(priors), "task_map": f.task_map, "flip_keys": fl["tested"]}


def _steps(acts: pd.DataFrame) -> pd.DataFrame:
    """One row per process step (execution level): the activity units of the step, weighted by in-house FTE."""
    if acts.empty:
        return acts
    a = acts.assign(step_key=acts.process_id + "|" + acts.step.map(lambda s: "" if pd.isna(s) else str(int(s))) + "|" +
                    np.where(acts.step.isna(), acts.dwa_id, ""), w=acts.fte_in_house.clip(lower=1e-9))
    g = a.groupby("step_key", sort=False)
    first = ["regime", "process_id", "process_name", "function_id", "step", "step_name", "program_constraint", "icfr_status",
             "icfr_channel", "icfr_condition", "wave", "wave_start_year", "depends_on", "moves_with_steps", "typical_systems",
             "role_process_owner", "role_occupations", "kpi_cycle_time", "fallback", "pilot_band_low", "pilot_band_high", "gate_threshold"]
    out = g[first].first()
    out["dwa_ids"] = g.dwa_id.agg(lambda x: ";".join(map(str, x)))
    out["activity_units"] = g.size()
    out["critical_path"] = g.critical_path.max()
    out["volume_per_year"] = g.volume_per_year.max()
    for c in ("hours_per_unit", "fte_in_house", "fte_after", "role_ai_engineer_months", "role_reviewer_fte_target", "saving_per_year",
              "ctl_itgc_line_usd", "ctl_interface_line"):
        out[c] = g[c].sum()
    out["labor_lead_days"] = g.labor_lead_days.max()
    out["in_plan"] = g.in_plan.first().astype(bool)
    out["integration_first"] = g.integration_first.first().astype(bool)
    for c in ("mode_now", "mode_step_now", "mode_step_target", "mode_plan_best", "mode_plan", "binding_target"):
        s_ = a.groupby(["step_key", c], sort=False).w.sum()
        out[c] = s_.groupby(level=0).idxmax().map(lambda t: t[1])
    out["share_automated_plan"] = a.assign(wa=np.where(a.mode_plan == "A", a.w, 0.0)).groupby("step_key", sort=False).wa.sum() / g.w.sum()
    rank = {"A": 1, "B": 2, "C": 3}
    inv = {v: k for k, v in rank.items()}
    for c in ("tier_now", "tier_target"):
        out[c] = a[c].map(rank).groupby(a.step_key, sort=False).max().map(inv)
    def union(col):
        return g[col].agg(lambda x: "; ".join(dict.fromkeys(y for v in x for y in str(v).split("; ") if y)))
    out["preconditions"] = union("preconditions")
    out["gates"] = union("gates")
    return out.reset_index(drop=True)


FIELDS = {
    "regime": "ownership regime of the run", "unit_key": "engine key of the activity unit (process|DWA)", "kind": "process step or residual work",
    "function_id": "owning function", "process_id": "process or workstream id", "process_name": "process name", "step": "step number (empty for residual work)",
    "step_name": "step name (process_activities.csv)", "dwa_id": "O*NET detailed work activity (the decision level)", "dwa_title": "DWA title",
    "gwa_id": "O*NET generalized work activity", "critical_path": "1 if the step is on the process's critical path", "iota0": "process readiness today",
    "volume_per_year": "output units a year", "hours_per_unit": "in-house hours per output unit", "fte_in_house": "FTE on the activity unit today",
    "mode_now": "mode today (H in-house, O outsourced)", "mode_activity_now": "cheapest feasible mode of the activity at readiness level 0, plan year 0 (prop:tasks-modes)",
    "mode_activity_target": "the same at the highest readiness level", "mode_step_now": "mode in the process's best column at level 0 starting now (prop:tasks-aon)",
    "mode_step_target": "mode in the best column at the highest level starting now", "mode_plan_best": "mode in the process's best column overall (baseline if none pays)",
    "mode_plan": "mode in the recommended plan", "in_plan": "the process is in the plan", "first_year_A_at_target": "first plan year in which A is cheapest at the highest level (prop:ext-feasible)",
    "binding_now": "first failing test for automation now: permissibility, feasibility (physical, capability horizon), readiness, reliability (detection; residual or appetite), volume threshold, cost; none if A is cheapest",
    "binding_now_detail": "detail of binding_now", "binding_target": "the same at the highest readiness level", "binding_target_detail": "detail of binding_target",
    "program_constraint": "for a positive process left out of the plan: the binding program capacity or the regime's hurdle (prop:ext-waves(d))",
    "icfr_status": "ICFR scope of the step", "icfr_channel": "scope channel (process, system, integration, policy)", "icfr_condition": "condition that puts it in scope",
    "regulated_class": "regulated class of the activity", "pre_readiness_floor": "readiness floor of the step", "pre_readiness_now": "effective readiness now",
    "pre_readiness_target": "effective readiness at the highest level", "pre_review_share_target": "review share xi at target (prop:tasks-review)",
    "pre_eval_set": "an evaluation set is needed (A or U)", "pre_itgc_lines": "ITGC lines added (in-scope automated step)", "typical_systems": "the step's systems",
    "preconditions": "conditions to meet before the switch", "gate_min_detection": "least reviewer catch rate d* = 1 - (1 - qbar)/e (prop:tasks-review(d))",
    "gate_detection_now": "reviewer catch rate at the defaults", "gate_max_residual_error": "largest residual error accepted (1 - qbar, or tier3_policy)",
    "residual_error_A_target": "residual error under A at target", "gate_min_volume": "least volume at which A beats the best non-AI mode, v* (prop:tasks-modes(e))",
    "pilot_band_low": "pilot band, lower success probability (eq:tasks-pilotband)", "pilot_band_high": "pilot band, upper", "gate_threshold": "pilot gate (or tier3_policy)",
    "gates": "go/no-go gates with their source in brackets", "wave": "roadmap wave", "wave_start_year": "first year of the wave",
    "depends_on": "what must finish first", "moves_with_steps": "steps of the process that cut over together (complementary set)", "integration_first": "data integration precedes automation",
    "role_process_owner": "process owner", "role_occupations": "typical occupations on the step, top three by hours", "role_occupations_source": "roster or prior",
    "role_ai_engineer_months": "AI engineer months to build (F_A / monthly AI engineer cost)", "role_control_owner": "ICFR control owner",
    "role_reviewer_fte_target": "reviewer FTE at target (xi rho_rev t v / hours per FTE)", "fte_after": "FTE left in the plan's mode",
    "fte_effect_target": "change in FTE", "labor_lead_days": "longest legal lead before dismissal (prop:labor-lead)",
    "kpi_unit_cost_now": "cost per output unit now ($)", "kpi_unit_cost_plan": "cost per output unit in the plan ($)", "kpi_residual_error": "residual error (A)",
    "kpi_review_share": "review share (A)", "kpi_cycle_time": "cycle time: measured (Tier 4) or to measure in Wave 0", "saving_per_year": "saving a year at the start year's volume ($)",
    "ctl_icfr": "ICFR control summary", "ctl_itgc_line_usd": "ITGC line per automated in-scope step a year (eq:acct-itgc)", "ctl_interface_line": "interface control a year when the step writes a financial system",
    "interface_lines_process": "integrations feeding in-scope systems in the process", "interface_line_per_year_process": "interface controls a year for the process",
    "fallback": "close-window fallback (prop:acct-itgc(d))", "ev_exposure_llm": "LLM exposure (Eloundou et al. 2024)", "ev_exposure_llm_class": "grounding class",
    "ev_aei_usage_share": "Anthropic Economic Index usage share of the DWA", "ev_aei_automation_pct": "AEI automation-pattern share", "ev_aei_class": "grounding class",
    "ev_aei_augmentation_pct": "AEI augmentation share (not yet in the data contract)", "ev_task_hours": "estimated hours per task instance",
    "ev_task_hours_class": "grounding class", "ev_physical_share": "physical share", "ev_licensed_share": "licensed time share",
    "ev_metr_feasibility_date": "date the task horizon reaches the step (METR fitted path)", "ev_capability_margin_log": "log capability margin at target",
    "ev_capability_class": "grounding class", "ev_detection_src": "detection source=class", "ev_target_src": "quality target source=class",
    "ev_build_src": "build cost source=class", "ev_review_time_src": "review time source=class", "ev_volume_src": "volume source=class",
    "ev_onet_task_links": "O*NET task statements linked to the DWA", "ev_task_ids": "up to 12 O*NET task ids, by occupation weight then incumbents responding",
    "ev_task_examples": "the top two O*NET task statements (text unchanged)", "tier_now": "confidence tier now (def:playbook-tier)", "tier_now_reason": "why",
    "tier_target": "confidence tier at target", "tier_target_reason": "why", "mode_swap_params_now": "class d keys that swap the mode within a class",
    "robustness_share_positive": "share of Monte Carlo draws with positive process value", "switch_conditions": "each threshold with the firm's distance",
    "threshold_cost_gap_share": "A cost minus the best non-AI cost, share of the latter", "distance_capability_years": "years to the capability date",
    "distance_readiness": "readiness at target minus the floor", "distance_reliability": "error allowance minus residual error", "distance_detection": "catch rate now minus d*",
    "distance_volume": "volume over v*, minus one", "dwa_ids": "DWAs of the step", "activity_units": "activity units in the step",
    "share_automated_plan": "share of the step's FTE automated in the plan",
}


def dictionary(priors=None) -> pd.DataFrame:
    """playbook_data_dictionary.csv: every field, plus the file-level O*NET attribution and a pointer to the shared
    data dictionary (data/tasks/data_dictionary.csv)."""
    att = getattr(priors, "task_attribution", None) if priors is not None else None
    rows = [{"file": "(all)", "field": "(file)", "definition": "playbook outputs of autofrontier; inputs are defined in data/tasks/data_dictionary.csv",
             "attribution": att or "O*NET 31.0 Database (USDOL/ETA), CC BY 4.0, modified by the author; USDOL/ETA has not approved, endorsed or tested the modifications"}]
    rows += [{"file": "playbook_activities.csv; playbook_steps.csv", "field": k, "definition": v, "attribution": ""} for k, v in FIELDS.items()]
    return pd.DataFrame(rows)
