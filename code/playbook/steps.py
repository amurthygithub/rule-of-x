"""Step- and activity-level playbook records (notes/playbook_engine_spec.md, Section 4; part2/theory_playbook.tex,
Section sec:playbook-steps).

Decide at the activity level (the engine's activity units: an O*NET detailed work activity in a process step or in a
function's residual work), execute at the process-step level (data/tasks/process_activities.csv). Every value is
read from the engine's run (autofrontier.pipeline.run) or computed with autofrontier.formulas; this module assembles
them into rows. Where the engine does not yet produce a field, the field is left empty and its name is listed in
MISSING (the engine spec says what to add).
"""
from __future__ import annotations

import copy
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODES = ("H", "O", "U", "A", "N")
H, O, U, A, N = range(5)
MISSING = ["kpi_cycle_time", "kpi_nrr", "kpi_seat_exposure", "ev_aei_augmentation_pct", "pilot_band_unselected",
           "process_readiness_threshold_iota_star_p", "close_fallback_cost_step"]

# class-d parameters tested for the confidence tier (both ends of each engine range). Engine-level keys rebuild the
# economics; impute-level keys (unit attributes set when the firm is built) rebuild the firm as well.
IMPUTE_KEYS = ["review.r_bar_high", "review.L_mult", "review.L_mult_regulated", "readiness.iota_min_regulated_add"]
ECON_SECTIONS = ["build", "review", "augment", "outsourcing", "eliminate", "reliability", "prices"]


# -------------------------------------------------------------------------------------------------
# Inputs written in the engine's input format (engine/src/autofrontier/schema.py)
# -------------------------------------------------------------------------------------------------
def systems_value_for(iota: float, p) -> tuple[float, float]:
    """Proxy value x (API, master-data quality, identity resolution; unstructured share 1 - x; one system of record)
    at which the engine's readiness index F.readiness_index equals iota, with the engine's default number of systems
    per function. Returns (x, n_systems)."""
    from autofrontier import formulas as F
    w, nref, ns = p.readiness.weights, p.readiness.n_systems_ref, p.readiness.default_n_systems
    f = lambda x: float(F.readiness_index(1.0, x, x, x, ns, 1 - x, w, nref)) - iota
    lo, hi = 0.0, 1.0
    if f(lo) > 0 or f(hi) < 0:
        raise ValueError(f"readiness {iota} is outside the index's range at {ns} systems")
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return 0.5 * (lo + hi), ns


def write_inputs(folder: Path, arch, st: dict, iota: float, p, priors) -> dict:
    """Tier 0 from the archetype's cell medians (panel), with the Part I calibration of archetypes.py: market growth =
    the firm's zero-spend growth G_i, capital intensity k, and the EV/revenue multiple = the revealed weight X_hat
    (impute.part1_baseline uses it as X). Tier 3 systems set every function's readiness to iota."""
    folder.mkdir(parents=True, exist_ok=True)
    S = float(arch.revenue)
    fin = {"company_name": f"Archetype {arch.code} (constructed from cell medians)", "fiscal_year": 2025, "currency": "USD",
           "revenue": round(S, 2), "cogs": round((1 - arch.gm) * S, 2), "rnd": round(arch.rd * S, 2),
           "sm": round(arch.sm * S, 2), "ga": round(arch.ga * S, 2),
           "capex": round((arch.capint if np.isfinite(arch.capint) else 0.0) * S, 2), "naics": "513210",
           "revenue_growth": round(float(st["g"]), 12), "market_growth": round(float(st["G_i"]), 12),
           "capital_intensity_k": round(float(st["k"]), 12), "ev_revenue_multiple": round(float(st["X_hat"]), 12),
           # the revealed weight of a public filer is already net of earnings pressure (spec W14; prop:reg-weight(b))
           "multiple_is_net_of_pressure": 1,
           # the cell's median FCF-after-SBC margin, Paper 1's m: m0 = m + sigma + k g (spec W17); the gap from the
           # median cost lines goes to the engine's other-operating line a_other
           "fcf_margin": round(float(arch.m), 12),
           "ownership_regime": "public"}
    pd.DataFrame({"field": list(fin), "value": list(fin.values())}).to_csv(folder / "tier0_financials.csv", index=False)
    x, ns = systems_value_for(iota, p)
    rows = []
    for f in priors.functions.itertuples():
        for k in range(int(ns)):
            rows.append({"system": f"{f.function_id} system {k + 1}", "function_id": f.function_id,
                         "system_of_record": 1.0 if k == 0 else 0.0, "api_available": x, "data_quality": x,
                         "identity_resolution": x, "unstructured_share": 1 - x})
    sysdf = pd.DataFrame(rows)
    # one system of record per function: sor enters the index as the function maximum (impute.py)
    sysdf.to_csv(folder / "tier3_systems.csv", index=False)
    return {"tier0": fin, "systems_proxy": x, "n_systems": ns}


# -------------------------------------------------------------------------------------------------
# Grounding classes of engine parameters (notes/assumptions_register.md: a sourced, b precedent, c own data, d free)
# -------------------------------------------------------------------------------------------------
_PY = {}


def _yaml(name):
    if name not in _PY:
        import yaml
        _PY[name] = yaml.safe_load(open(ROOT / "data" / "tasks" / name))
    return _PY[name]


def grounding_of(p, key: str) -> tuple[str, str]:
    """(class, source key) of an engine parameter: its own grounding field, else the linked params.yaml or
    params_reliability.yaml block's grounding."""
    try:
        m = p.meta(key)
    except Exception:
        return "unresolved", key
    if m.get("grounding"):
        return str(m["grounding"]), key
    for fld, fname in (("params", "params.yaml"), ("params_rel", "params_reliability.yaml")):
        path = m.get(fld)
        if path:
            node = _yaml(fname)
            for part in str(path).split("|")[0].split("."):
                node = node.get(part, {}) if isinstance(node, dict) else {}
            g = node.get("grounding") if isinstance(node, dict) else None
            return (str(g) if g else "linked"), f"{fname}:{path}"
    if m.get("source"):
        return "a", key
    return ("d" if m.get("assumed") else "unresolved"), key


def class_d_keys(p) -> list[str]:
    keys = []
    for k in p.keys():
        s = k.split(".")[0]
        if s not in ECON_SECTIONS and k not in IMPUTE_KEYS:
            continue
        m = p.meta(k)
        v, rng = m.get("value"), m.get("range")
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not isinstance(rng, list) or len(rng) != 2:
            continue
        if not all(isinstance(r, (int, float)) for r in rng) or rng[0] == rng[1]:
            continue
        if grounding_of(p, k)[0] == "d":
            keys.append(k)
    return sorted(set(keys))


# -------------------------------------------------------------------------------------------------
# Activity decisions (static mode choice at a readiness level and year)
# -------------------------------------------------------------------------------------------------
def unit_decisions(econ, l: int, y: int) -> dict:
    """Best mode by the engine's choice cost among feasible modes, and the binding constraint on automation (mode A),
    in the order of Proposition prop:tasks-breakpoints and prop:playbook-gates: permissibility, physical work,
    capability horizon, readiness, reliability (detection, then residual error or risk appetite), then cost
    (cheaper alternative or volume threshold)."""
    from autofrontier import formulas as F
    Ut = econ.firm.units.reset_index(drop=True)
    info, rel = econ.info, econ.info.get("reliability")
    ct = econ.ct[:, l, y, :]
    cash = econ.cash[:, l, y, :]
    best = np.argmin(np.where(np.isfinite(ct), ct, np.inf), axis=1)
    best = np.where(np.isfinite(ct).any(axis=1), best, econ.base_mode)
    nU = len(Ut)
    cat, det = np.empty(nU, dtype=object), np.empty(nU, dtype=object)
    phys = Ut.physical.values >= econ.p.capability.physical_threshold
    capA = info["capA"][:, l, y]
    read_ok = info["read_ok"][:, l]
    rev_ok = rel["review_feasible"][:, l, y] if rel is not None else ~info["not_automatable_review"][:, l, y]
    rel_ok = rel["ok"][:, l, y] if rel is not None else econ.tech[:, l, y, A]
    licensed, excluded = info["licensed"], info["excluded"]
    permA = econ.perm[:, A]
    ebar = (rel["e_o"][:, l, y] + rel["h"][:, l, y]) if rel is not None else econ.e_raw[:, l, y]
    d_now = rel["d_o"][:, l, y] if rel is not None else np.full(nU, econ.p.reliability.d_e)
    qbar = Ut.r_bar.values.astype(float)
    dstar = np.asarray(F.detection_threshold(ebar, qbar), float)
    alt = np.min(np.where(np.arange(5)[None, :] != A, np.where(np.isfinite(cash), cash, np.inf), np.inf), axis=1)
    Fb = econ.F_build[:, y, A] * info["a_crf"] + econ.run[:, y, A]
    v = Ut.v.values * econ.vf[y]
    gap = alt - cash[:, A]
    with np.errstate(divide="ignore", invalid="ignore"):
        vstar = np.where(gap > 0, Fb / gap, np.inf)
        cost_gap = (ct[:, A] - ct[np.arange(nU), best]) / np.maximum(np.abs(ct[np.arange(nU), best]), 1e-9)
    for i in range(nU):
        if best[i] == A:
            cat[i], det[i] = "none: automation optimal", ""
        elif not permA[i]:
            why = "licensed sign-off" if licensed[i] else ("ethics exclusion" if excluded[i] else
                                                         ("data class above risk appetite" if not econ.data_allowed[i] else "prohibited class"))
            cat[i], det[i] = "permissibility", why
        elif phys[i] and not capA[i]:
            cat[i], det[i] = "feasibility: physical", f"world-model lag; capability date {econ.T_F[i, l]:.1f}"
        elif not capA[i]:
            cat[i], det[i] = "feasibility: capability horizon", f"capability date {econ.T_F[i, l]:.1f}"
        elif not read_ok[i]:
            cat[i], det[i] = "readiness", f"iota {econ.iota_u[i, l]:.2f} below floor {Ut.iota_min.values[i]:.2f}"
        elif not rev_ok[i]:
            cat[i], det[i] = "reliability: detection", f"catch rate {d_now[i]:.2f} below threshold {dstar[i]:.2f}"
        elif not rel_ok[i]:
            cat[i], det[i] = "reliability: residual error or risk appetite", ""
        elif np.isfinite(vstar[i]) and v[i] < vstar[i]:
            cat[i], det[i] = "volume threshold (build or buy)", f"volume {v[i]:,.0f} below {vstar[i]:,.0f}"
        else:
            cat[i], det[i] = f"cost: {MODES[best[i]]} cheaper", f"automation costs {100 * cost_gap[i]:.0f}% more"
    return {"best": best, "cat": cat, "det": det, "dstar": dstar, "d_now": d_now, "ebar": ebar, "vstar": vstar,
            "v": v, "cost_gap": cost_gap, "cash_best": cash[np.arange(nU), best], "eps_A": econ.eps[:, l, y],
            "xi_A": econ.xi[:, l, y], "capA": capA, "read_ok": read_ok, "rev_ok": rev_ok, "T_F": econ.T_F[:, l],
            "log_margin": econ.log_margin[:, l, y], "feasA": econ.feas[:, l, y, A]}


def first_year_A(econ, l: int) -> np.ndarray:
    """First plan year in which automation is the best mode at readiness level l (NaN if never in the horizon)."""
    ct = np.where(np.isfinite(econ.ct[:, l, :, :]), econ.ct[:, l, :, :], np.inf)
    best = np.argmin(ct, axis=2)                       # (U, T)
    out = np.full(best.shape[0], np.nan)
    for i in range(best.shape[0]):
        ys = np.flatnonzero(best[i] == A)
        if len(ys):
            out[i] = econ.years[ys[0]] - 0.5
    return out


def flip_params(res, p, keys: list[str], l_now: int, l_tgt: int, data_dir) -> dict:
    """One-at-a-time test at both ends of each class-d range. For each unit it records the keys that change the
    automation decision (automate or not) or the AI decision (an AI mode U, A or N, or a non-AI mode H or O): these
    decide Tier C. Keys that only swap modes within those classes (for example outsourcing against in-house work) are
    recorded separately and do not change the tier."""
    from autofrontier import economics as E, impute
    econ0, firm0 = res["econ"], res["firm_obj"]
    b_now = unit_decisions(econ0, l_now, 0)["best"]
    b_tgt = unit_decisions(econ0, l_tgt, 0)["best"]
    ai = lambda b: np.isin(b, [U, A, N])
    out = {"now": {}, "target": {}, "now_any": {}, "target_any": {}}
    ing, priors = res["ingest"], res["priors"]
    for key in keys:
        lo, hi = p.meta(key)["range"]
        for val in (lo, hi):
            p2 = copy.deepcopy(p)
            p2.set(key, val, origin="playbook confidence test")
            try:
                firm = impute.build_firm(ing, priors, p2) if key in IMPUTE_KEYS else firm0
                e2 = E.build_econ(firm, p2)
            except Exception:
                continue
            if e2.ct.shape[0] != econ0.ct.shape[0]:
                continue
            for tag, base, l in (("now", b_now, l_now), ("target", b_tgt, l_tgt)):
                b2 = unit_decisions(e2, min(l, e2.L - 1), 0)["best"]
                sign = ((b2 == A) != (base == A)) | (ai(b2) != ai(base))
                for i in np.flatnonzero(sign):
                    out[tag].setdefault(int(i), set()).add(key)
                for i in np.flatnonzero((b2 != base) & ~sign):
                    out[tag + "_any"].setdefault(int(i), set()).add(key)
    return {k: {i: sorted(v) for i, v in d.items()} for k, d in out.items()}


def confidence_tier(cat: str, flips: list[str]) -> tuple[str, str]:
    """Tier A: the recommendation rests on feasibility filters the backtest supports (non-physical, permissible,
    capability horizon; part2/validation_backtest.tex) with sourced costs; Tier B: on the cost crossover with no
    class-d range end flipping it; Tier C: some class-d range end flips it (named)."""
    if flips:
        return "C", "flips at an end of: " + "; ".join(flips)
    if cat.startswith("feasibility") or cat == "permissibility":
        return "A", "feasibility or permissibility filter (backtest-supported)"
    return "B", "cost crossover or reliability gate, robust to the tested class-d ranges"


# -------------------------------------------------------------------------------------------------
# Process plans (the engine's columns): mode vectors, readiness level, start year, value
# -------------------------------------------------------------------------------------------------
def process_plans(res) -> dict:
    """Best column per process overall, at today's readiness starting now, and at the highest readiness level starting
    now, valued as the engine's optimizer values them (pv0 + varpi pv1, varpi from the column's logit)."""
    from scipy.special import expit
    prog, econ, sol = res["prog"], res["econ"], res["sol"]
    cols = prog.cols
    L = econ.L
    out = {}
    for i in range(len(cols.proc)):
        pr = int(cols.proc[i])
        val = float(prog.pv0[i] + expit(cols.logit0[i]) * prog.pv1[i])
        d = out.setdefault(pr, {"best": None, "now": None, "target": None})
        if d["best"] is None or val > d["best"][0]:
            d["best"] = (val, i)
        if int(cols.level[i]) == 0 and int(cols.start[i]) == 0 and (d["now"] is None or val > d["now"][0]):
            d["now"] = (val, i)
        if int(cols.level[i]) == L - 1 and int(cols.start[i]) == 0 and (d["target"] is None or val > d["target"][0]):
            d["target"] = (val, i)
    sel = {int(k): int(c) for k, c in sol.sel.items()}
    return {"by_process": out, "selected": sel}


def _modes_of(res, pr: int, col: int | None, positive: bool) -> np.ndarray:
    econ = res["econ"]
    us = np.flatnonzero(econ.unit_proc == pr)
    if col is None or not positive:
        return econ.base_mode[us]
    return np.asarray(res["prog"].cols.modes[col])


# -------------------------------------------------------------------------------------------------
# Records
# -------------------------------------------------------------------------------------------------
def _wave_of(res) -> dict:
    w = {}
    for wv in res.get("waves") or []:
        for pid in wv.get("processes", []) or []:
            w[pid] = (int(wv["wave"]), int(wv.get("start_year", 0)), list(wv.get("depends_on", []) or []))
    return w


def _task_examples() -> tuple[dict, dict]:
    t2d = pd.read_csv(ROOT / "data" / "tasks" / "xw_task_dwa.csv", usecols=["onet_soc", "task_id", "dwa_id", "soc"])
    ts = pd.read_csv(ROOT / "data" / "raw" / "onet_31_0" / "task_statements.csv", usecols=["task_id", "task", "task_type"])
    t = t2d.merge(ts, on="task_id", how="left")
    count = t.groupby("dwa_id").task_id.nunique().to_dict()
    return count, {k: g for k, g in t.groupby("dwa_id")}


def build_records(code: str, name: str, case: str, iota0: float, res, p, flips: dict, labor_lead_days: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Rows for every activity unit (playbook_activities) and every process step (playbook_steps)."""
    from autofrontier import formulas as F
    econ, firm = res["econ"], res["firm_obj"]
    Ut = firm.units.reset_index(drop=True)
    Pr = firm.processes.reset_index(drop=True)
    L = econ.L
    now, tgt = unit_decisions(econ, 0, 0), unit_decisions(econ, L - 1, 0)
    fyA = first_year_A(econ, L - 1)
    plans = process_plans(res)
    waves = _wave_of(res)
    hpf = p.labor.hours_per_fte
    rates = econ.rates
    acts = pd.read_csv(ROOT / "data" / "tasks" / "activities.csv").set_index("dwa_id")
    pa = pd.read_csv(ROOT / "data" / "tasks" / "process_activities.csv")
    fnames = dict(zip(firm.functions.function_id, firm.functions.function_name)) if "function_name" in firm.functions else {}
    tcount, tgroups = _task_examples()
    g_d, s_d = grounding_of(p, "reliability.d_e")
    g_q, s_q = grounding_of(p, "review.r_bar_high")
    g_b, s_b = grounding_of(p, "build.em_base")
    g_rr, s_rr = grounding_of(p, "review.rho_rev")
    plan_mode = {}
    for pr, d in plans["by_process"].items():
        bestv, bestc = d["best"] if d["best"] else (None, None)
        nowv, nowc = d["now"] if d["now"] else (None, None)
        tv, tc = d["target"] if d["target"] else (None, None)
        us = np.flatnonzero(econ.unit_proc == pr)
        mn = _modes_of(res, pr, nowc, nowv is not None and nowv > 0)
        mt = _modes_of(res, pr, tc, tv is not None and tv > 0)
        mb = _modes_of(res, pr, bestc, bestv is not None and bestv > 0)
        for j, u in enumerate(us):
            plan_mode[int(u)] = (mn[j], mt[j], mb[j], nowv, tv, bestv, bestc)
    rows = []
    sel = plans["selected"]
    pid_of = Pr.process_id.values
    for i in range(len(Ut)):
        u = Ut.iloc[i]
        pr = int(econ.unit_proc[i])
        pid = pid_of[pr]
        mn, mt, mb, nowv, tv, bestv, bestc = plan_mode.get(i, (econ.base_mode[i],) * 3 + (None,) * 4)
        dwa = str(u.activity_id)
        ar = acts.loc[dwa] if dwa in acts.index else None
        us = np.flatnonzero(econ.unit_proc == pr)
        moved = []
        if bestc is not None and bestv is not None and bestv > 0:
            md = np.asarray(res["prog"].cols.modes[bestc])
            moved = [str(Ut.step.values[x]) if pd.notna(Ut.step.values[x]) else str(Ut.unit_key.values[x])
                     for k_, x in enumerate(us) if md[k_] != econ.base_mode[x]]
        fl_now = flips["now"].get(i, [])
        fl_tgt = flips["target"].get(i, [])
        sw_now = flips.get("now_any", {}).get(i, [])
        tier_now, why_now = confidence_tier(now["cat"][i], fl_now)
        tier_tgt, why_tgt = confidence_tier(tgt["cat"][i], fl_tgt)
        icfr_in = str(u.get("icfr_status", "")) in ("in scope", "assumed in scope")
        A_tgt = int(tgt["best"][i]) == A or int(mt) == A
        itgc = None
        if icfr_in and A_tgt:
            ac = p.accounting
            itgc = F.itgc_line(ac.itgc_n_id, ac.itgc_perm_per_step, ac.itgc_c_acc, ac.itgc_n_chg, ac.itgc_c_chg, ac.C_val,
                               p.security.T_up, ac.itgc_c_ops, 1.0 if str(u.get("financial_system_written") or "").strip() else 0.0,
                               ac.itgc_c_ifc)
            itgc = float(itgc["total"] if isinstance(itgc, dict) and "total" in itgc else
                         (sum(v for v in itgc.values() if isinstance(v, (int, float))) if isinstance(itgc, dict) else itgc))
        v_now = float(now["v"][i])
        res_now = econ.res_hours[i, 0, 0, int(now["best"][i])]
        res_tgt = econ.res_hours[i, L - 1, 0, int(tgt["best"][i])]
        res_base = econ.res_hours[i, 0, 0, int(econ.base_mode[i])]
        sw = []
        if now["cat"][i].startswith("reliability: detection"):
            sw.append(f"automate if the catch rate reaches {now['dstar'][i]:.2f} (now {now['d_now'][i]:.2f})")
        if now["cat"][i] == "readiness":
            sw.append(f"automate at readiness {Ut.iota_min.values[i]:.2f} (now {econ.iota_u[i, 0]:.2f})")
        if now["cat"][i].startswith("feasibility: capability"):
            sw.append(f"automation capability-feasible from {now['T_F'][i]:.1f}")
        if now["cat"][i].startswith("volume"):
            sw.append(f"build pays above {now['vstar'][i]:,.0f} units a year (now {v_now:,.0f}); buy below")
        if now["cat"][i].startswith("cost"):
            sw.append(f"automate if its cost falls {100 * now['cost_gap'][i] / (1 + now['cost_gap'][i]):.0f}% relative to {now['cat'][i][6:7]}")
        if np.isfinite(fyA[i]) and int(now["best"][i]) != A:
            sw.append(f"automation becomes the cheapest mode at target readiness in {int(fyA[i])}")
        if fl_now:
            sw.append("recommendation flips at a range end of " + ", ".join(fl_now))
        row = {
            "archetype": code, "archetype_name": name, "readiness_case": case, "iota0": iota0, "regime": res["regime"],
            "unit_id": int(u.unit_id), "unit_key": u.unit_key, "kind": "step" if u.kind == "process" else "residual",
            "function_id": u.function_id, "function_name": fnames.get(u.function_id, ""), "process_id": pid,
            "process_name": Pr.process_name.values[pr], "step": (int(u.step) if pd.notna(u.step) else None),
            "dwa_id": dwa, "dwa_title": (ar["dwa_title"] if ar is not None else u.title), "gwa_id": u.gwa_id,
            "critical_path": int(u.critical) if pd.notna(u.critical) else None,
            "volume_per_year": v_now, "hours_per_unit": float(u.t), "fte_in_house": float(u.fte),
            # 1. modes
            "mode_activity_now": MODES[int(now["best"][i])], "mode_activity_target": MODES[int(tgt["best"][i])],
            "mode_step_now": MODES[int(mn)], "mode_step_target": MODES[int(mt)], "mode_plan_best": MODES[int(mb)],
            "process_value_now": nowv, "process_value_target": tv, "process_value_best": bestv,
            "process_in_plan": pr in sel, "first_year_A_at_target": fyA[i],
            "unit_cost_now": float(now["cash_best"][i]), "unit_cost_target": float(tgt["cash_best"][i]),
            "unit_cost_baseline": float(econ.cash[i, 0, 0, int(econ.base_mode[i])]),
            # 2. binding constraint on automation
            "binding_now": now["cat"][i], "binding_now_detail": now["det"][i],
            "binding_target": tgt["cat"][i], "binding_target_detail": tgt["det"][i],
            "regulated_class": u.regulated_class, "icfr_status": u.get("icfr_status", ""),
            "icfr_channel": u.get("icfr_channel", ""), "icfr_condition": u.get("icfr_condition", ""),
            # 3. preconditions
            "pre_readiness_floor": float(Ut.iota_min.values[i]), "pre_readiness_now": float(econ.iota_u[i, 0]),
            "pre_readiness_target": float(econ.iota_u[i, L - 1]), "pre_review_share_target": float(tgt["xi_A"][i]),
            "pre_eval_set": bool(int(tgt["best"][i]) in (A, U)), "pre_itgc_lines": bool(itgc is not None),
            # 4. gates
            "gate_min_detection": float(now["dstar"][i]), "gate_detection_now": float(now["d_now"][i]),
            "gate_max_residual_error": float(1 - Ut.r_bar.values[i]), "residual_error_A_target": float(tgt["eps_A"][i]),
            "gate_min_volume": float(now["vstar"][i]) if np.isfinite(now["vstar"][i]) else None,
            # 5. wave and dependencies
            "wave": waves.get(pid, (None, None, None))[0], "wave_start_year": waves.get(pid, (None, None, None))[1],
            "depends_on": "; ".join(waves.get(pid, (None, None, []))[2] or []), "moves_with_steps": "; ".join(moved),
            # 6. roles and people
            "role_process_owner": f"{fnames.get(u.function_id, u.function_id)} process owner",
            "role_ai_engineer_months": float(econ.info["FA0"][i] / max(rates["ai_engineer_month"], 1e-9)),
            "role_control_owner": "ICFR control owner" if icfr_in else "",
            "role_reviewer_fte_target": float(econ.res_hours[i, L - 1, 0, A] * v_now / hpf) if int(tgt["best"][i]) == A else 0.0,
            "fte_effect_target": float((res_tgt - res_base) * v_now / hpf),
            "labor_lead_days_US": labor_lead_days,
            # 7. KPIs
            "kpi_unit_cost": float(tgt["cash_best"][i]), "kpi_residual_error": float(tgt["eps_A"][i]) if int(tgt["best"][i]) == A else None,
            "kpi_cycle_time": None, "kpi_nrr": None, "kpi_seat_exposure": None,
            # 8. controls
            "ctl_icfr": icfr_in, "ctl_itgc_line_usd": itgc,
            "ctl_interface_line": bool(str(u.get("financial_system_written") or "").strip()) and icfr_in,
            # 9. evidence
            "ev_exposure_llm": (float(ar["exposure_llm"]) if ar is not None and pd.notna(ar["exposure_llm"]) else None),
            "ev_exposure_src": (str(ar["exposure_measure"]) if ar is not None else "") + " (eloundou2024gpts; a)",
            "ev_aei_usage_share": (float(ar["ai_usage"]) if ar is not None and pd.notna(ar["ai_usage"]) else None),
            "ev_aei_automation_pct": (float(ar["aei_automation_pct"]) if ar is not None and pd.notna(ar["aei_automation_pct"]) else None),
            "ev_aei_augmentation_pct": None,
            "ev_aei_src": (str(ar["ai_usage_source"]) if ar is not None else "") + " (appel2026anthropic; a)",
            "ev_task_hours": (float(ar["est_task_hours"]) if ar is not None and pd.notna(ar["est_task_hours"]) else None),
            "ev_physical_share": (float(ar["physical_task_share"]) if ar is not None and pd.notna(ar["physical_task_share"]) else None),
            "ev_licensed_share": (float(ar["licensed_time_share"]) if ar is not None and pd.notna(ar["licensed_time_share"]) else None),
            "ev_metr_feasibility_date": float(now["T_F"][i]) if np.isfinite(now["T_F"][i]) else None,
            "ev_capability_margin_log": float(now["log_margin"][i]),
            "ev_metr_src": "capability.H0_hours, capability.Td_years (kwa2025measuring; a, refit)",
            "ev_detection_src": f"{s_d} ({g_d})", "ev_target_src": f"{s_q} ({g_q})", "ev_build_src": f"{s_b} ({g_b})",
            "ev_review_time_src": f"{s_rr} ({g_rr})", "ev_wage_src": "OEWS May 2025 (bls2026oews; a)",
            "ev_onet_task_links": int(tcount.get(dwa, 0)),
            # 10. confidence
            "tier_now": tier_now, "tier_now_reason": why_now, "tier_target": tier_tgt, "tier_target_reason": why_tgt,
            # 11. switch conditions
            "switch_conditions": " | ".join(sw),
            "mode_swap_params_now": "; ".join(sw_now),
        }
        g = tgroups.get(dwa)
        if g is not None and len(g):
            ex = g.drop_duplicates("task").sort_values(["task_type", "task_id"]).head(2)
            row["ev_task_ids"] = ";".join(str(int(t)) for t in g.task_id.unique()[:12])
            row["ev_task_examples"] = " || ".join(ex.task.astype(str).tolist())
        else:
            row["ev_task_ids"], row["ev_task_examples"] = "", ""
        rows.append(row)
    acts_df = pd.DataFrame(rows)
    steps = acts_df[acts_df.kind == "step"].copy()
    # steps of the 136-step map absent from this firm's activity units (engine priors drop them): kept, flagged
    have = set(zip(steps.process_id, steps.step))
    miss = pa[[(r.process_id, int(r.step)) not in have for r in pa.itertuples()]]
    extra = [{"archetype": code, "archetype_name": name, "readiness_case": case, "iota0": iota0, "regime": res["regime"],
              "kind": "step", "process_id": r.process_id, "step": int(r.step), "dwa_id": r.dwa_id, "dwa_title": r.dwa_title,
              "binding_now": "not in the firm's activity map (engine priors)", "icfr_status": "", "tier_now": ""}
             for r in miss.itertuples()]
    if extra:
        steps = pd.concat([steps, pd.DataFrame(extra)], ignore_index=True)
    smap = pa.set_index(["process_id", "step"])
    steps["step_name"] = [smap.step_name.get((a_, int(b_)), "") if pd.notna(b_) else "" for a_, b_ in zip(steps.process_id, steps.step)]
    steps["typical_systems"] = [smap.typical_systems.get((a_, int(b_)), "") if pd.notna(b_) else "" for a_, b_ in zip(steps.process_id, steps.step)]
    steps = steps.sort_values(["process_id", "step"]).reset_index(drop=True)
    return acts_df, steps
