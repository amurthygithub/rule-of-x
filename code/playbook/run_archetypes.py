#!/usr/bin/env python3
"""Archetype runner for the AI-transformation playbook.

    python3 code/playbook/run_archetypes.py            # every archetype, both readiness cases (about 25 minutes)
    python3 code/playbook/run_archetypes.py --jobs 2   # two worker processes
    python3 code/playbook/run_archetypes.py --only A2  # one archetype (both readiness cases)

Writes
  part2/tables/playbook_table.tex        main playbook table (Table tab:playbook)
  part2/tables/playbook_grid.tex         owner x archetype lever grid (appendix Table tab:playbook-grid)
  part2/tables/playbook_functions.tex    summary by function (Table tab:playbook-functions)
  part2/tables/playbook_processes.tex    summary by process (appendix Table tab:playbook-processes)
  part2/tables/playbook_steps_full.tex   one archetype at step level (appendix Table tab:playbook-steps)
  part2/tables/playbook_macros.tex       every number quoted in part2/theory_playbook.tex
  sections/tables/levers_position_macros.tex   numbers quoted in sections/levers_by_position.tex (Paper 1)
  data/playbook/playbook_steps.csv       process step x archetype x readiness case
  data/playbook/playbook_activities.csv  activity unit (O*NET DWA in a step or residual work) x archetype x case
  data/playbook/playbook_dwa.csv         O*NET DWA x archetype x case (aggregated over the DWA's activity units)
  data/playbook/archetypes.csv           archetype positions, Part I states and lever maps
  data/playbook/data_dictionary.csv      one row per column of the two playbook files
  notes/playbook_results.json            everything above in one file, for code/verify_part2_playbook.py

Engine use (public API only; engine/ is not edited): autofrontier.pipeline.run on input folders written in the engine's
format (Tier 0 financials from the archetype's cell medians, Tier 3 systems that set readiness), the run's result
dictionary (part1, econ, prog, sol, plan, waves, regimes, frontier, utilization), autofrontier.formulas for every
formula, autofrontier.impute and autofrontier.economics for the confidence-tier rebuilds. Overrides: the expansion
R&D share is set to zero so that growth spend sigma is the S&M share, Paper 1's convention (Section sec:data).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
if str(ROOT / "engine" / "src") not in sys.path:
    sys.path.insert(1, str(ROOT / "engine" / "src"))

import archetypes as AR  # noqa: E402
import levers as LV      # noqa: E402
import steps as ST       # noqa: E402

OVERRIDES = ["finance.rd_expansion_share=0"]
CASES = {"low": 0.4, "high": 0.9}       # core example cases (data/examples/invoice_chain.yaml: iota_low, iota_high)
REGIME_ORDER = ["public", "hybrid", "private_family", "pe", "vc", "permanent_capital"]
REGIME_LABEL = {"public": "Public (preset pressure)", "hybrid": "Dual class", "private_family": "Family",
                "pe": "PE, entry of a 6-year hold", "vc": "VC, 7-year horizon", "permanent_capital": "Permanent acquirer"}
FULL_STEP_ARCHETYPE = "A2"
N_IMP, N_OUT = 4, 20
ROBUST_SHARE = 0.8          # a setting (Definition def:playbook-tier; notes/playbook_engine_spec.md, Section 5)


def engine_params():
    from autofrontier.config import find_data_dir, load_params, parse_override
    dd = find_data_dir()
    p = load_params(dd)
    for o in OVERRIDES:
        k, v = parse_override(o)
        p.set(k, v, origin="playbook runner")
    return p, dd


# -------------------------------------------------------------------------------------------------
# One configuration: archetype x readiness case
# -------------------------------------------------------------------------------------------------
def run_config(arch_dict: dict, case: str, workdir: str) -> dict:
    from autofrontier import pipeline, formulas as F
    from autofrontier.priors import load_priors
    arch = AR.Archetype(**{k: v for k, v in arch_dict.items() if k in AR.Archetype.__dataclass_fields__})
    p, dd = engine_params()
    priors = load_priors(dd)
    st0 = arch.state(alpha=p.finance.alpha)
    folder = Path(workdir) / f"{arch.code}_{case}"
    meta = ST.write_inputs(folder, arch, st0, CASES[case], p, priors)
    t0 = time.time()
    try:
        from autofrontier import api
        res = api.run(str(folder), None, regime="public", quick=True, n_imp=N_IMP, n_out=N_OUT,
                      scenario_list=["central"], overrides=OVERRIDES)
        book = api.playbook(res)
    except ImportError:                       # engine without the public API module (before 0.2)
        res = pipeline.run(str(folder), None, regime="public", quick=True, write=False, n_imp=N_IMP, n_out=N_OUT,
                           scenario_list=["central"], overrides=OVERRIDES)
        book = res.get("playbook") or {}
    secs = time.time() - t0
    pe = res["params"]
    pt = dict(res["firm"]["part1"])
    econ = res["econ"]
    # Part I state from the engine's part1 (engine-generated), with the line split the engine does not report
    # m0: Part I's identity m = m0 - sigma - k g at the cell's median FCF-after-SBC margin (Paper 1's m); the engine's
    # m0 is built from the median cost lines, whose sum differs from the median margin (no other-operating line in
    # Tier 0), and is kept as m0_engine. m0 enters only the owner weights (m_hat) and score levels, not lever values.
    # S&M basis (author decision of 2 Nov 2026): the engine's part1 is on the netted basis (finance.sm_basis), as the
    # archetype state that wrote its inputs; with no growth spend above the maintenance base there is no demand pull
    st = {"sigma": float(pt["sigma"]), "a_GA": float(arch.ga), "a_SM": float(pt.get("sm_maint", 0.0)), "sm": float(arch.sm),
          "sm_basis": pt.get("sm_basis"), "rd": float(arch.rd), "gamma": float(pt["gamma"]),
          "k": float(pt["k"]), "Delta": float(pt["g"]) - float(pt["G"]), "G_i": float(pt["G"]),
          "ell": float(pt["ell"]) if float(pt["sigma"]) > 1e-6 else 0.0,
          "X_hat": float(pt["X"]), "m0": float(st0["m0"]), "m0_engine": float(pt["m0"]), "g": float(pt["g"]),
          "m": float(arch.m), "m_cash_engine": float(pt["m_cash"]),
          "alpha": float(pt["alpha"]), "c_h": float(pt["c_h"]), "c_c": float(pt["c_c"]),
          "sigma_star_engine": float(pt["sigma_star"]), "Delta_star_engine": float(pt["Delta_star"])}
    dur = float(econ.info["durable_share"])            # dollar share (cor:ext-game-engine(a)); reported, not in the score
    ptr = econ.info["pass_through"]                    # Part I round 2 (B1): rate on the unit-cost saving, post-cut price
    keep = float(ptr["keep_replicable"])
    W = LV.regime_weights(st, pe)
    rates = {"public": pe.regime.public_r, "hybrid": pe.regime.public_r,
             "private_family": pe.regime.public_r + pe.regime.family_r_spread, "pe": pe.regime.pe_irr_target,
             "vc": pe.regime.vc_r, "permanent_capital": getattr(pe.regime, "pc_irr_unlevered", math.log(1.25))}
    lev = {}
    for nm in REGIME_ORDER + ["revealed"]:
        X = W[nm] if nm in W and W[nm] is not None else None
        if X is None:
            continue
        lev[nm] = LV.lever_values(st, float(X), st["c_h"], keep, pe.capital.delta_K_compute,
                                  rates.get(nm, pe.regime.public_r))
    # confidence-tier flips (class-d ranges); impute-level keys rebuild the firm
    keys = ST.class_d_keys(pe)
    flips = ST.flip_params(res, pe, keys, 0, econ.L - 1, dd)
    # labor lead: U.S. federal rules at the firm's size (no jurisdiction file for an archetype)
    hc = float(res["firm"].get("headcount") or 0.0)
    sel_fte = float(res["plan"].fte_removed.max()) if len(res["plan"]) else 0.0
    lt = F.statutory_terms("US", "", site_headcount=hc, employer_headcount=hc, n_dis=sel_fte)
    lead_days = 365.0 * float(lt.get("T_leg", 0.0))
    units, steps = ST.build_records(arch.code, arch.name, case, CASES[case], res, pe, flips, lead_days)
    units, steps, dwa = merge_engine_book(units, steps, book, arch.code, arch.name, case)
    reg_view = {}
    for nm, v in (res.get("regimes") or {}).items():
        gw = v.get("growth_weight") or {}
        reg_view[nm] = {"value": v.get("value"), "processes": v.get("processes"), "X_o_engine": gw.get("X_o"),
                        "dip_gaap_points": v.get("dip_gaap_points"), "final_uplift_cash_points": v.get("final_uplift_cash_points"),
                        "first_year_launches": v.get("first_year_launches")}
    waves = []
    for wv in res.get("waves") or []:
        if wv.get("wave", 0) == 0:
            waves.append({"wave": 0, "cost": wv.get("cost"), "items": len(wv.get("items", []))})
            continue
        names = [res["plan"].set_index("process_id").process_name.get(x, x) for x in wv.get("processes", [])]
        waves.append({"wave": wv["wave"], "start_year": wv.get("start_year"), "processes": wv.get("processes"),
                      "names": names, "integration_first": wv.get("integration_first"), "npv": wv.get("npv"),
                      "one_time_cost": wv.get("one_time_cost"), "fte_affected": wv.get("fte_affected"),
                      "mean_success_probability": wv.get("mean_success_probability")})
    ut = res["utilization"]
    binding_cap = None
    if len(ut):
        r0 = ut.iloc[0]
        shares = {"change capacity": r0.change_capacity_used / max(r0.change_capacity, 1e-9),
                  "decision bandwidth": r0.load_ratio / max(r0.load_breakpoint, 1e-9),
                  "security review": r0.security_reviews / max(r0.review_capacity, 1e-9),
                  "transformation budget": r0.budget_used / max(r0.budget, 1e-9),
                  "dual-running budget": r0.dual_running_used / max(r0.dual_running_budget, 1e-9)}
        binding_cap = max(shares, key=shares.get)
        shares = {k: float(v) for k, v in shares.items()}
    else:
        shares = {}
    uni = res.get("universe_now") or {}
    out = {"code": arch.code, "case": case, "iota0": CASES[case], "seconds": secs, "inputs": meta, "part1": {k: (float(v) if isinstance(v, (int, float, np.floating)) and v is not None else v) for k, v in pt.items()},
           "state": st, "weights": W, "levers": lev, "dur": dur, "keep": keep, "pass_through": {k: float(v) for k, v in ptr.items()},
           "regimes_engine": reg_view, "waves": waves,
           "frontier": {k: float(v) if isinstance(v, (int, float, np.floating)) and v is not None else v for k, v in (res.get("frontier") or {}).items()},
           "capacity_use_year0": shares, "binding_capacity_year0": binding_cap, "class_d_tested": keys,
           "n_flips_now": len(flips["now"]), "n_flips_target": len(flips["target"]),
           "universe_now": {k: (float(v) if isinstance(v, (int, float, np.floating)) else None) for k, v in uni.items() if not isinstance(v, (dict, list, pd.DataFrame, np.ndarray))},
           "labor_lead_days_US": lead_days, "engine_version": res["version"]["engine_version"],
           "hashes": res["version"].get("hashes"), "engine_playbook_version": book.get("version"),
           "agreement_with_engine": units.attrs.get("agreement", {}), "engine_lever_map": _engine_levers(res),
           "engine_playbook_summary": book.get("summary"), "engine_not_computed": book.get("not_computed")}
    return {"summary": out, "units": units, "steps": steps, "activities": dwa}


# Engine playbook (playbook.build, version 1.0, through api.playbook): its activity-unit rows are joined to the runner's
# by unit_key and its step rows by (process_id, step); every engine column gets the prefix eng_. Identity columns are
# not repeated.
ENGINE_ID_COLS = {"regime", "unit_key", "kind", "function_id", "process_id", "process_name", "step", "step_name", "dwa_id",
                  "dwa_title", "gwa_id", "critical_path", "volume_per_year", "hours_per_unit", "fte_in_house", "unit_id",
                  "typical_systems", "icfr_status", "icfr_channel", "icfr_condition", "regulated_class"}
# fields compared between the runner and the engine (agreement shares go to the run summary)
AGREE_FIELDS = ["mode_activity_now", "mode_activity_target", "mode_step_now", "tier_now", "tier_target"]


def _cat(s: pd.Series) -> pd.Series:
    return s.astype(str).str.split(":").str[0].str.strip()


def _engine_levers(res) -> dict:
    """The engine's own lever map (api.lever_map, W13), reduced to JSON: per regime X_o and the lever values."""
    lm = res.get("lever_map") if isinstance(res, dict) else None
    if not lm:
        return {}
    out = {"state": {k: (float(v) if isinstance(v, (int, float, np.floating)) else v) for k, v in (lm.get("state") or {}).items()
                     if not isinstance(v, (dict, list, pd.DataFrame))},
           "check_calibration": lm.get("check_calibration"), "regimes": {}}
    for nm, r in (lm.get("regimes") or {}).items():
        out["regimes"][nm] = {"X_o": r.get("X_o"), "applicable": r.get("applicable"),
                              "levers": {k: float(v) for k, v in (r.get("levers") or {}).items() if isinstance(v, (int, float, np.floating))},
                              "X_dagger_0_overhead": ((r.get("thresholds") or {}).get("overhead") or {}).get("X_dagger_0")}
    return out


def merge_engine_book(units: pd.DataFrame, steps: pd.DataFrame, book: dict, code: str, name: str, case: str):
    """Join the engine's playbook rows to the runner's, apply the Monte Carlo clause of the tier rule with the engine's
    robustness share, record runner-engine agreement, and build the DWA x configuration table."""
    agree = {}
    ea = book.get("activities") if isinstance(book, dict) else None
    if ea is not None and len(ea) and "unit_key" in ea:
        keep = [c for c in ea.columns if c not in ENGINE_ID_COLS]
        e = ea[["unit_key"] + keep].rename(columns={c: f"eng_{c}" for c in keep}).drop_duplicates("unit_key")
        units = units.merge(e, on="unit_key", how="left")
        for f in AGREE_FIELDS:
            if f in units and f"eng_{f}" in units:
                both = units[[f, f"eng_{f}"]].dropna()
                agree[f] = float((both[f].astype(str) == both[f"eng_{f}"].astype(str)).mean()) if len(both) else None
        if "binding_now" in units and "eng_binding_now" in units:
            agree["binding_now_category"] = float((_cat(units.binding_now) == _cat(units.eng_binding_now)).mean())
        # Definition def:playbook-tier, second clause: Tier C if the share of the engine's Monte Carlo draws with a
        # positive process value is below ROBUST_SHARE (computed by the engine for processes in its plan)
        if "eng_robustness_share_positive" in units:
            rb = pd.to_numeric(units.eng_robustness_share_positive, errors="coerce")
            m = rb.notna() & (rb < ROBUST_SHARE) & units.tier_now.isin(["A", "B"])
            units.loc[m, "tier_now_reason"] = [f"Monte Carlo share of draws with positive process value {v:.2f} < {ROBUST_SHARE}" for v in rb[m]]
            units.loc[m, "tier_now"] = "C"
            agree["tier_now_after_mc"] = float((units.tier_now.astype(str) == units.eng_tier_now.astype(str)).mean()) if "eng_tier_now" in units else None
        # carry the unit-level tier back to the step rows
        tmap = units[units.kind == "step"].set_index("unit_key")[["tier_now", "tier_now_reason"]]
        if "unit_key" in steps:
            hit = steps.unit_key.isin(tmap.index)
            steps.loc[hit, "tier_now"] = tmap.loc[steps.loc[hit, "unit_key"], "tier_now"].values
            steps.loc[hit, "tier_now_reason"] = tmap.loc[steps.loc[hit, "unit_key"], "tier_now_reason"].values
    es = book.get("steps") if isinstance(book, dict) else None
    if es is not None and len(es) and {"process_id", "step"} <= set(es.columns):
        es2 = es[es.step.notna()].copy()
        es2["step"] = es2.step.astype(float)
        keep = [c for c in es2.columns if c not in ENGINE_ID_COLS]
        e = es2[["process_id", "step"] + keep].rename(columns={c: f"eng_{c}" for c in keep}).drop_duplicates(["process_id", "step"])
        steps["step"] = steps.step.astype(float)
        steps = steps.merge(e, on=["process_id", "step"], how="left")
    g = units.groupby("dwa_id", sort=True)
    rows = []
    for dwa, grp in g:
        w = grp.fte_in_house.fillna(0).clip(lower=1e-9)
        sh = lambda col, m: float(w[grp[col] == m].sum() / w.sum())
        bn = grp.groupby("binding_now").fte_in_house.sum()
        rows.append({"archetype": code, "archetype_name": name, "readiness_case": case, "dwa_id": dwa,
                     "dwa_title": grp.dwa_title.iat[0], "gwa_id": grp.gwa_id.iat[0], "units": int(len(grp)),
                     "steps": int((grp.kind == "step").sum()), "processes": int(grp.process_id.nunique()),
                     "functions": "; ".join(sorted(set(map(str, grp.function_id)))),
                     "fte_in_house": float(grp.fte_in_house.sum()),
                     "share_automated_now": sh("mode_activity_now", "A"), "share_augmented_now": sh("mode_activity_now", "U"),
                     "share_automated_target": sh("mode_activity_target", "A"), "share_augmented_target": sh("mode_activity_target", "U"),
                     "binding_now": bn.idxmax() if len(bn) else "",
                     "regulated_any": bool((grp.icfr_status.astype(str).isin(["in scope", "assumed in scope"])).any()),
                     "tier_now_worst": max([t for t in grp.tier_now.astype(str) if t in ("A", "B", "C")] or [""]),
                     "tier_target_worst": max([t for t in grp.tier_target.astype(str) if t in ("A", "B", "C")] or [""]),
                     "ev_exposure_llm": grp.ev_exposure_llm.iat[0], "ev_aei_usage_share": grp.ev_aei_usage_share.iat[0],
                     "ev_aei_automation_pct": grp.ev_aei_automation_pct.iat[0], "ev_aei_augmentation_pct": None,
                     "ev_physical_share": grp.ev_physical_share.iat[0], "ev_licensed_share": grp.ev_licensed_share.iat[0],
                     "ev_metr_feasibility_date_min": grp.ev_metr_feasibility_date.min(),
                     "ev_onet_task_links": grp.ev_onet_task_links.iat[0], "ev_task_ids": grp.ev_task_ids.iat[0],
                     "ev_task_examples": grp.ev_task_examples.iat[0]})
    dwa_df = pd.DataFrame(rows)
    units.attrs["agreement"] = agree
    return units, steps, dwa_df


def _job(args):
    arch_dict, case, workdir = args
    return run_config(arch_dict, case, workdir)


# -------------------------------------------------------------------------------------------------
# Position-only map for the compounder (no engine run: acquisitions are not in the engine's firm model)
# -------------------------------------------------------------------------------------------------
def compounder_map(a: AR.Archetype, p) -> dict:
    from autofrontier import formulas as F
    al = p.finance.alpha
    e = a.extra
    # S&M basis (decision 7): netted, as the panel archetypes. The compounder's S&M share is below the maintenance base, so
    # it has no growth spend on that basis: no demand pull, the maintenance S&M is a cost line, and X_hat takes the common
    # weight of ass:playbook-calib (k + r_sigma/alpha) instead of the organic-spend implied one (all-S&M basis, reported)
    sm_all, g_org, G_i = a.sm, e["g_organic_q2_2026"], e["G_i_2025"]
    sigma, a_sm = AR.growth_spend(sm_all)
    Delta = g_org - G_i
    k = 0.0
    X_hat_all = k + sm_all / (al * Delta)         # all-S&M basis: revealed by organic spend (Proposition prop:score(b))
    X_hat = X_hat_all if sigma > 0 and AR.BASIS == "all" else k + AR.spend_ratio() / al
    ell = Delta / sigma ** al if sigma > 0 else 0.0
    m0 = a.m_op + sigma                           # GAAP basis; capital spending is not separated in the extract
    st = {"sigma": sigma, "a_GA": a.ga, "a_SM": a_sm, "sm": sm_all, "rd": a.rd, "gamma": a.gm, "k": k, "Delta": Delta,
          "G_i": G_i, "ell": ell, "X_hat": X_hat, "X_hat_all_sm": X_hat_all, "m0": m0, "m0_all_sm": a.m_op + sm_all,
          "g": g_org, "m": a.m_op, "alpha": al, "c_h": float("nan"), "sm_basis": AR.BASIS}
    W = LV.regime_weights(st, p)
    lev = {nm: LV.lever_values(st, float(W[nm]), 0.0, 0.0, p.capital.delta_K_compute, math.log(1.25))
           for nm in ("public", "permanent_capital", "revealed") if W.get(nm) is not None}
    prices = e["acq_price_to_revenue"]
    return {"code": a.code, "state": st, "weights": W, "levers": lev,
            "acquisition_score_effect_per_point": {deal: W["permanent_capital"] - kp for deal, kp in prices.items()},
            "acquisition_r40_effect_per_point": {deal: 1.0 - kp for deal, kp in prices.items()}, "extra": e}


# -------------------------------------------------------------------------------------------------
# Output helpers
# -------------------------------------------------------------------------------------------------
def _num(x, d=1, pct=False, sign=False):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "n.a."
    v = 100 * x if pct else x
    s = f"{v:+.{d}f}" if sign else f"{v:.{d}f}"
    # \ensuremath works in text and in math, so a macro holding a negative number can sit inside $...$
    return s.replace("-", "\\ensuremath{-}") if not sign else s.replace("-", "\\ensuremath{-}").replace("+", "\\ensuremath{+}")


def _macro_name(*parts) -> str:
    words = {"1": "One", "2": "Two", "3": "Three", "4": "Four", "5": "Five", "6": "Six", "7": "Seven", "0": "Zero"}
    out = []
    for p in parts:
        for ch in str(p):
            out.append(words.get(ch, ch) if ch.isdigit() else (ch if ch.isalpha() else ""))
    return "pb" + "".join(out)


def tex_escape(s: str) -> str:
    return (str(s).replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#"))


def first_two(lev: dict) -> list[tuple[str, float]]:
    vals = lev["ranking_values"]
    return [(k, vals[k]) for k in lev["ranking"][:2]]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--only", default=None)
    ap.add_argument("--workdir", default=None)
    ap.add_argument("--tables-only", action="store_true",
                    help="rewrite the tables and macros from notes/playbook_results.json and data/playbook/*.csv")
    args = ap.parse_args(argv)
    t_start = time.time()
    p, dd = engine_params()
    core = AR.load_core_panel()
    archs, cuts = AR.build_archetypes(core)
    if args.tables_only:
        R = json.load(open(ROOT / "notes" / "playbook_results.json"))
        R["sm_basis_check"] = AR.sm_basis_check(archs, float(p.finance.alpha))
        outdir = ROOT / "data" / "playbook"
        steps = pd.read_csv(outdir / "playbook_steps.csv", low_memory=False)
        units = pd.read_csv(outdir / "playbook_activities.csv", low_memory=False)
        write_tables(R, archs, steps, units)
        json.dump(R, open(ROOT / "notes" / "playbook_results.json", "w"), indent=1, default=_json_default)
        print(f"tables rewritten in {time.time() - t_start:.0f}s")
        return
    workdir = args.workdir or tempfile.mkdtemp(prefix="playbook_inputs_")
    todo = [(a.__dict__, c, workdir) for a in archs if a.code != "A7" and (not args.only or a.code == args.only) for c in CASES]
    results = []
    if args.jobs > 1:
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            results = list(ex.map(_job, todo))
    else:
        for t in todo:
            print(f"running {t[0]['code']} {t[1]} ...", flush=True)
            results.append(_job(t))
            print(f"  done in {results[-1]['summary']['seconds']:.0f}s", flush=True)
    comp = compounder_map([a for a in archs if a.code == "A7"][0], p)
    summ = {(r["summary"]["code"], r["summary"]["case"]): r["summary"] for r in results}
    acts = pd.concat([r["units"] for r in results], ignore_index=True)
    steps = pd.concat([r["steps"] for r in results], ignore_index=True)
    dwa = pd.concat([r["activities"] for r in results], ignore_index=True)
    outdir = ROOT / "data" / "playbook"
    outdir.mkdir(parents=True, exist_ok=True)
    steps.to_csv(outdir / "playbook_steps.csv", index=False)
    acts.to_csv(outdir / "playbook_activities.csv", index=False)
    dwa.to_csv(outdir / "playbook_dwa.csv", index=False)
    old = outdir / "playbook_units.csv"
    if old.exists():
        old.unlink()          # earlier name of playbook_activities.csv (renamed to the engine's file names)
    write_dictionary(outdir / "data_dictionary.csv", {"playbook_steps.csv": steps, "playbook_activities.csv": acts,
                                                       "playbook_dwa.csv": dwa})
    arch_rows = []
    for a in archs:
        r = {"code": a.code, "name": a.name, "rule": a.rule, "n": a.n, "n_firms": a.n_firms, "g": a.g, "m": a.m, "R": a.R,
             "m_op": a.m_op, "sm": a.sm, "ga": a.ga, "rd": a.rd, "gm": a.gm, "capint": a.capint, "revenue": a.revenue,
             "q_g": a.q_g, "q_m": a.q_m, "q_R": a.q_R, "largest_gap_line": a.band_gap.get("largest", ""),
             "largest_gap_points": a.band_gap.get(a.band_gap.get("largest", ""), float("nan")) if a.band_gap else float("nan")}
        s = summ.get((a.code, "low"))
        if s:
            for nm in REGIME_ORDER:
                if nm in s["levers"]:
                    L = s["levers"][nm]
                    r[f"X_{nm}"] = L["X"]
                    r[f"top_lever_{nm}"] = L["ranking"][0]
        arch_rows.append(r)
    pd.DataFrame(arch_rows).to_csv(outdir / "archetypes.csv", index=False)
    results_json = {"generated": time.strftime("%Y-%m-%d %H:%M"), "seconds": time.time() - t_start, "overrides": OVERRIDES,
                    "cases": CASES, "cuts": cuts, "archetypes": AR.archetype_table_rows(archs),
                    "configs": {f"{k[0]}_{k[1]}": v for k, v in summ.items()}, "compounder": comp,
                    "coverage": coverage(steps, acts), "sm_basis_check": AR.sm_basis_check(archs, float(p.finance.alpha))}
    write_tables(results_json, archs, steps, acts)
    json.dump(results_json, open(ROOT / "notes" / "playbook_results.json", "w"), indent=1, default=_json_default)
    print(f"done in {time.time() - t_start:.0f}s")


def _json_default(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (set, tuple)):
        return list(o)
    if isinstance(o, (pd.DataFrame,)):
        return o.to_dict(orient="records")
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def coverage(steps: pd.DataFrame, acts: pd.DataFrame) -> dict:
    s = steps[steps.binding_now != "not in the firm's activity map (engine priors)"]
    cfg = steps.groupby(["archetype", "readiness_case"]).size()
    pa = pd.read_csv(ROOT / "data" / "tasks" / "process_activities.csv")
    return {"steps_in_map": int(len(pa)), "steps_populated_per_config": int(s.groupby(["archetype", "readiness_case"]).size().min()) if len(s) else 0,
            "steps_rows": int(len(steps)), "configs": int(len(cfg)), "activity_rows": int(len(acts)),
            "dwa_populated": int(acts.dwa_id.nunique()),
            "dwa_in_onet": int(pd.read_csv(ROOT / "data" / "tasks" / "activities.csv").dwa_id.nunique()),
            "activity_units_per_config": int(acts.groupby(["archetype", "readiness_case"]).size().min()) if len(acts) else 0,
            "processes": int(pa.process_id.nunique()), "functions": int(acts.function_id.nunique()),
            "missing_fields": ST.MISSING}


def write_dictionary(path: Path, frames: dict):
    """One row per column of the playbook files: description, unit, source, and the files that carry it. Engine
    columns (eng_) take the engine's own field descriptions (roadmap.PLAYBOOK_FIELDS)."""
    EF, attribution = {}, []
    try:
        from autofrontier import playbook as EPB
        d = EPB.dictionary()
        EF = dict(zip(d["field"].astype(str), d["definition"].astype(str)))
        attribution = [a for a in d.get("attribution", pd.Series(dtype=str)).dropna().astype(str) if a.strip()]
    except Exception:  # pragma: no cover
        try:
            from autofrontier.roadmap import PLAYBOOK_FIELDS as EF
        except Exception:
            EF = {}
    cols = sorted(set().union(*[set(f.columns) for f in frames.values()]))
    rows = []
    for c in cols:
        d = DICTIONARY.get(c)
        if d is None and c.startswith("eng_"):
            d = ("engine: " + (EF.get(c[4:], "") or c[4:].replace("_", " ")), "", "engine playbook.build (api.playbook)")
        d = d or ("", "", "")
        r = {"column": c, "description": d[0], "unit": d[1], "source": d[2],
             "attribution": "O*NET 31.0 Database (USDOL/ETA), CC BY 4.0" if c.startswith(("dwa", "gwa", "ev_task", "ev_onet")) else ""}
        for fn, f in frames.items():
            r["in_" + fn.replace("playbook_", "").replace(".csv", "")] = c in f.columns
        rows.append(r)
    if attribution:
        rows.insert(0, {"column": "(all)", "description": attribution[0], "unit": "", "source": "engine playbook.dictionary",
                        "attribution": attribution[0]})
    pd.DataFrame(rows).to_csv(path, index=False)


DICTIONARY = {
    "archetype": ("archetype code (Definition def:playbook-archetypes)", "", "code/playbook/archetypes.py"),
    "archetype_name": ("archetype name", "", "code/playbook/archetypes.py"),
    "readiness_case": ("readiness case: low (0.4) or high (0.9), set through the engine's systems inventory", "", "data/examples/invoice_chain.yaml"),
    "iota0": ("today's data readiness of every function", "share", "engine readiness index"),
    "regime": ("ownership regime of the run", "", "engine regimes.py"),
    "unit_key": ("engine activity unit: process|DWA or function residual|DWA", "", "engine impute.build_firm"),
    "kind": ("step (a process step of process_activities.csv) or residual (a function's other work)", "", "engine"),
    "function_id": ("function", "", "data/tasks/functions.csv"), "function_name": ("function name", "", "data/tasks/functions.csv"),
    "process_id": ("process (P01 to P24) or residual work stream", "", "data/tasks/processes.csv"),
    "process_name": ("process name", "", "data/tasks/processes.csv"), "step": ("step number in the process", "", "data/tasks/process_activities.csv"),
    "step_name": ("step name", "", "data/tasks/process_activities.csv"), "typical_systems": ("systems the step reads or writes", "", "data/tasks/process_activities.csv"),
    "dwa_id": ("O*NET 31.0 detailed work activity", "", "onet2026database"), "dwa_title": ("DWA title", "", "onet2026database"),
    "gwa_id": ("O*NET generalized work activity", "", "onet2026database"), "critical_path": ("1 if every unit of the process passes through the step", "", "data/tasks/process_activities.csv"),
    "volume_per_year": ("units of output a year in year 0", "units", "engine"), "hours_per_unit": ("in-house hours per unit", "hours", "engine"),
    "fte_in_house": ("in-house FTE on the unit", "FTE", "engine"),
    "mode_activity_now": ("activity decision: cheapest feasible mode by the engine's choice cost, today's readiness, 2026", "H/O/U/A/N", "prop:tasks-modes"),
    "mode_activity_target": ("activity decision at readiness 0.9, 2026", "H/O/U/A/N", "prop:tasks-augment"),
    "mode_step_now": ("step decision: mode in the engine's best process column at today's readiness starting now (baseline if no column has positive value)", "H/O/U/A/N", "prop:tasks-transition, prop:tasks-aon"),
    "mode_step_target": ("step decision at the highest readiness level starting now", "H/O/U/A/N", "prop:tasks-readiness"),
    "mode_plan_best": ("mode in the process's best column over readiness levels and start years", "H/O/U/A/N", "engine plans.py"),
    "process_value_now": ("value of the best column at today's readiness starting now", "$", "engine optimizer (public regime)"),
    "process_value_target": ("value of the best column at readiness 0.9 starting now", "$", "engine optimizer"),
    "process_value_best": ("value of the best column overall", "$", "engine optimizer"),
    "process_in_plan": ("process selected in the engine's program", "bool", "engine optimizer"),
    "first_year_A_at_target": ("first plan year in which automation is the cheapest mode at readiness 0.9", "year", "ext prop:ext-feasible"),
    "unit_cost_now": ("cash cost per unit in the activity's mode now", "$", "engine"), "unit_cost_target": ("cash cost per unit at target", "$", "engine"),
    "unit_cost_baseline": ("cash cost per unit in the baseline mode", "$", "engine"),
    "binding_now": ("binding constraint on automation now (prop:playbook-gates order)", "", "prop:tasks-breakpoints"),
    "binding_now_detail": ("distance or reason", "", "engine"), "binding_target": ("binding constraint at readiness 0.9", "", "prop:tasks-breakpoints"),
    "binding_target_detail": ("distance or reason", "", "engine"),
    "regulated_class": ("regulatory class", "", "engine impute"), "icfr_status": ("ICFR scope status", "", "def:acct-scope"),
    "icfr_channel": ("ICFR channel: process, system, integration, policy", "", "def:acct-scope"), "icfr_condition": ("condition for scope", "", "def:acct-scope"),
    "pre_readiness_floor": ("readiness floor of automation", "share", "prop:tasks-review(d)"), "pre_readiness_now": ("effective readiness now", "share", "engine"),
    "pre_readiness_target": ("effective readiness at target", "share", "engine"), "pre_review_share_target": ("review share under automation at target", "share", "prop:tasks-review"),
    "pre_eval_set": ("an evaluation set must be built (target mode A or U)", "bool", "prop:tasks-fullcost"),
    "pre_itgc_lines": ("ITGC lines needed (in scope and automated at target)", "bool", "prop:acct-itgc"),
    "gate_min_detection": ("minimum reviewer catch rate at which review can meet the target", "share", "prop:tasks-review(d), prop:tasks-halluc(b)"),
    "gate_detection_now": ("engine catch rate", "share", "params_reliability review.catch_rate_ordinary"),
    "gate_max_residual_error": ("tolerated residual error, 1 - target reliability", "share", "engine review rule"),
    "residual_error_A_target": ("residual error under automation at target", "share", "engine"),
    "gate_min_volume": ("volume above which building automation beats the best alternative", "units a year", "prop:tasks-modes(e), prop:tasks-buildbuy"),
    "wave": ("wave of the engine's roadmap (blank: not in the plan)", "", "engine roadmap"), "wave_start_year": ("start year of the wave", "year", "engine roadmap"),
    "depends_on": ("dependencies of the wave", "", "engine roadmap"), "moves_with_steps": ("steps whose mode changes in the same column (complementary set)", "", "prop:tasks-complement"),
    "role_process_owner": ("process owner", "", ""), "role_ai_engineer_months": ("AI engineering months of the automation build", "months", "engine build rule"),
    "role_control_owner": ("ICFR control owner needed", "", "prop:acct-itgc"), "role_reviewer_fte_target": ("reviewer FTE under automation at target", "FTE", "engine"),
    "fte_effect_target": ("change in in-house FTE at target mode", "FTE", "engine"), "labor_lead_days_US": ("U.S. legal lead before dismissals take effect", "days", "prop:labor-lead"),
    "kpi_unit_cost": ("unit cost KPI at target", "$", "engine"), "kpi_residual_error": ("residual error KPI under automation", "share", "engine"),
    "kpi_cycle_time": ("cycle time (not produced by the engine yet)", "", "engine spec P7"), "kpi_nrr": ("net revenue retention of a product step (not produced yet)", "", "engine spec P7"),
    "kpi_seat_exposure": ("seat exposure of a product step (not produced yet)", "", "engine spec P7"),
    "ctl_icfr": ("step in ICFR scope", "bool", "def:acct-scope"), "ctl_itgc_line_usd": ("ITGC line of the AI application a year", "$", "eq:acct-itgc"),
    "ctl_interface_line": ("interface control needed (writes a financial system)", "bool", "prop:acct-itgc"),
    "ev_exposure_llm": ("LLM exposure of the DWA", "share", "eloundou2024gpts"), "ev_exposure_src": ("source and class", "", ""),
    "ev_aei_usage_share": ("Anthropic Economic Index share of conversations", "share", "appel2026anthropic"),
    "ev_aei_automation_pct": ("AEI automation share of collaboration", "percent", "appel2026anthropic"),
    "ev_aei_augmentation_pct": ("AEI augmentation share (not in activities.csv yet)", "percent", "data agent request"),
    "ev_aei_src": ("AEI release", "", ""), "ev_task_hours": ("task length in human hours", "hours", "AEI human_only_time_mean"),
    "ev_physical_share": ("physical task share", "share", "tomlinson2025working"),
    "ev_metr_feasibility_date": ("date at which automation is capability-feasible at today's readiness", "year", "kwa2025measuring (refit)"),
    "ev_capability_margin_log": ("log capability margin ln(H kappa / (d chi))", "", "ass:ext-capability"),
    "ev_metr_src": ("capability source", "", ""), "ev_detection_src": ("catch-rate source and class", "", ""),
    "ev_target_src": ("reliability-target source and class", "", ""), "ev_build_src": ("build-effort source and class", "", ""),
    "ev_review_time_src": ("review-time source and class", "", ""), "ev_wage_src": ("wage source", "", ""),
    "ev_onet_task_links": ("O*NET task statements linked to the DWA", "count", "xw_task_dwa.csv"),
    "ev_task_ids": ("up to 12 O*NET task ids (evidence keys)", "", "onet2026database"), "ev_task_examples": ("two task statements", "", "onet2026database"),
    "tier_now": ("confidence tier of the activity decision now", "A/B/C", "Definition def:playbook-tier"), "tier_now_reason": ("reason", "", ""),
    "tier_target": ("confidence tier at target", "A/B/C", ""), "tier_target_reason": ("reason", "", ""),
    "switch_conditions": ("what would change the recommendation, with distances", "", "prop:tasks-breakpoints"),
    "mode_swap_params_now": ("class-d range ends that change the mode within the AI or the non-AI modes only (not tier-deciding)", "", "Definition def:playbook-tier"),
    "ev_licensed_share": ("licensed time share of the DWA (permissibility)", "share", "data/tasks/activities.csv"),
    "unit_id": ("engine activity unit id (join key to the engine's playbook rows)", "", "engine impute.build_firm"),
    "units": ("activity units of the DWA in the configuration (steps and residual work)", "count", "engine"),
    "steps": ("process steps among them", "count", "data/tasks/process_activities.csv"),
    "processes": ("processes and residual work streams in which the DWA is performed", "count", "engine"),
    "functions": ("functions performing the DWA", "", "data/tasks/functions.csv"),
    "share_automated_now": ("share of the DWA's in-house FTE whose activity decision is A at today's readiness", "share", "prop:tasks-modes"),
    "share_augmented_now": ("share of the DWA's in-house FTE whose activity decision is U at today's readiness", "share", "prop:tasks-augment"),
    "share_automated_target": ("share automated at readiness 0.9", "share", "prop:tasks-modes"),
    "share_augmented_target": ("share augmented at readiness 0.9", "share", "prop:tasks-augment"),
    "regulated_any": ("the DWA is performed in at least one in-scope ICFR step", "bool", "def:acct-scope"),
    "tier_now_worst": ("lowest confidence tier among the DWA's units now (C below B below A)", "A/B/C", "Definition def:playbook-tier"),
    "tier_target_worst": ("lowest confidence tier among the DWA's units at readiness 0.9", "A/B/C", "Definition def:playbook-tier"),
    "ev_metr_feasibility_date_min": ("earliest capability date among the DWA's units", "year", "kwa2025measuring (refit)"),
}


# -------------------------------------------------------------------------------------------------
# Tables and macros
# -------------------------------------------------------------------------------------------------
LEVER_SHORT = {"growth engine": "growth engine", "overhead (G&A)": "overhead (G\\&A)", "engineering (R&D)": "engineering (R\\&D)",
               "cost of revenue": "cost of revenue"}


WORDS = {0: "none", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}
PANEL = ["A1", "A2", "A3", "A4", "A5", "A6"]
FINANCE_FUNCTIONS = ("F10", "F11")   # procurement, finance and accounting (data/tasks/functions.csv)


def ranking_by_basis(R: dict) -> dict:
    """Decision 7: the ranking of the four proportional levers (prop:playbook-rank(a)) at the weight each position's own
    spending reveals (the public owner's), on the central maintenance-netted basis and on the all-S&M and no-S&M bounds.
    At that weight sigma* equals the basis's growth spend, so the values per 10% are x sigma, x a_GA, x a_RD and
    x (1 - phi C0) c_h with C0 = 1 - f - m0 on the basis (the intercept m0 adds back the basis's growth spend)."""
    out = {"positions": {}, "rule": "first of growth engine, overhead (G&A), engineering (R&D), cost of revenue at X = X_hat"}
    for c in PANEL:
        s = R["configs"][f"{c}_low"]
        st, pt = s["state"], s["pass_through"]
        f_fee = 1.0 - float(pt["C0"]) - float(s["part1"]["m0"])       # the engine's fee share (C0 = 1 - f - m0)
        row = {}
        for basis in AR.BASES:
            sig, a_sm = AR.growth_spend(st["sm"], basis)
            m0_b = float(s["part1"]["m0"]) + (sig - st["sigma"])          # m0 = m + sigma + k g on the basis
            keep = 1.0 - float(pt["phi"]) * max(1.0 - f_fee - m0_b, 0.0)
            vals = {"growth engine": 0.1 * sig, "overhead (G&A)": 0.1 * st["a_GA"], "engineering (R&D)": 0.1 * st["rd"],
                    "cost of revenue": 0.1 * keep * st["c_h"]}
            rk = sorted(vals, key=lambda kk: -vals[kk])
            row[basis] = {"ranking": rk, "values": vals, "sm_maint_line": 0.1 * a_sm,
                          "ge_ahead_of_ga": vals["growth engine"] > vals["overhead (G&A)"]}
        out["positions"][c] = row
    for basis in AR.BASES:
        out[f"n_ge_first_{basis}"] = sum(r[basis]["ranking"][0] == "growth engine" for r in out["positions"].values())
        out[f"n_eng_first_{basis}"] = sum(r[basis]["ranking"][0] == "engineering (R&D)" for r in out["positions"].values())
        out[f"n_ga_first_{basis}"] = sum(r[basis]["ranking"][0] == "overhead (G&A)" for r in out["positions"].values())
        out[f"n_ge_ahead_of_ga_{basis}"] = sum(r[basis]["ge_ahead_of_ga"] for r in out["positions"].values())
    out["n_sm_maint_above_ga"] = sum(r["netted"]["sm_maint_line"] > r["netted"]["values"]["overhead (G&A)"]
                                     for r in out["positions"].values())
    return out


def ge_first_count(R: dict, regime: str) -> tuple[int, int]:
    """Number of panel archetypes whose first lever at the owner's weight is the growth engine, and the number at
    which the owner's weight is defined."""
    n, d = 0, 0
    for c in PANEL:
        s = R["configs"].get(f"{c}_low")
        if not s or regime not in s["levers"]:
            continue
        d += 1
        n += s["levers"][regime]["ranking"][0] == "growth engine"
    return n, d


def reference_steps(steps: pd.DataFrame) -> pd.DataFrame:
    """Step decisions of the reference runs (every panel archetype, readiness 0.4) that are in the activity map."""
    return steps[(steps.readiness_case == "low") & steps.tier_now.isin(["A", "B", "C"])]


def explicit_macros(R: dict, archs, steps: pd.DataFrame, acts: pd.DataFrame) -> dict:
    """Every number quoted in part2/theory_playbook.tex, by the name the text uses."""
    M = {}
    cuts = R["cuts"]
    pc = lambda v, d=1: _num(v, d, pct=True)
    M["SpendRatioPB"] = _num(AR.spend_ratio(), 2)          # central (netted) spend ratio, Paper 1's AlphaNet (decision 7)
    M["SpendRatioPBAll"] = _num(AR.SPEND_RATIO, 1)         # all-S&M bound, 3.3
    # Lemma lem:playbook-calib(c): X_hat - k = r_sigma/alpha for alpha in [0.25, 0.45] (proofs_playbook.tex)
    for nm, r in (("Net", AR.spend_ratio()), ("All", AR.SPEND_RATIO)):
        M[f"pbXhatK{nm}Lo"], M[f"pbXhatK{nm}Hi"] = _num(r / 0.45, 1), _num(r / 0.25, 1)
    M["pbCutNpop"] = str(cuts["n_population"])
    M["pbCutNEtwo"] = str(cuts["n_E2"])
    M["pbCutGtwentyfive"], M["pbCutGmed"], M["pbCutGseventyfive"] = pc(cuts["g25"]), pc(cuts["g50"]), pc(cuts["g75"])
    M["pbCutMtwentyfive"], M["pbCutMmed"], M["pbCutMseventyfive"] = pc(cuts["m25"]), pc(cuts["m50"]), pc(cuts["m75"])
    M["pbCutRseventyfive"], M["pbCutRninetyfive"] = pc(cuts["R75"]), pc(cuts["R95"])
    M["pbCutNpassforty"] = WORDS.get(cuts["n_pass40_non_elite_balanced"], str(cuts["n_pass40_non_elite_balanced"]))
    A = {a.code: a for a in archs}
    cfg = lambda c: R["configs"][f"{c}_low"]
    M["pbASixGi"] = pc(cfg("A6")["state"]["G_i"])
    M["pbAOneSM"] = pc(A["A1"].sm, 0)
    # S&M basis re-check (Paper 1 round 2, author decision 4; archetypes.sm_basis_check)
    sb = R.get("sm_basis_check") or AR.sm_basis_check(archs, 0.3)
    M["pbMaintBase"] = pc(sb["b_M"])
    M["pbSpendRatioNet"] = _num(sb["spend_ratio_netted"], 2)
    for basis, nm in (("all", "All"), ("netted", "Net"), ("none", "None")):
        M[f"pbNGEAheadGA{nm}"] = WORDS.get(sb["n_ahead"][basis], str(sb["n_ahead"][basis]))
    net_yes = [c for c, r in sb["positions"].items() if r["netted"]["growth_engine_ahead_of_ga"]]
    M["pbGEAheadNetList"] = ", ".join(net_yes) if net_yes else "none"
    zero = [c for c, r in sb["positions"].items() if r["netted"]["sigma"] <= 0]
    M["pbSMNetZeroList"] = ", ".join(zero) if zero else "none"
    M["pbNSMAutoAheadGA"] = WORDS.get(sb["n_sm_automation_ahead"], str(sb["n_sm_automation_ahead"]))
    # decision 7: growth spend above the base against overhead at the two positions well above the base
    for c, nm in (("A1", "One"), ("A4", "Four")):
        M[f"pbA{nm}Sigma"] = pc(sb["positions"][c]["netted"]["sigma"], 0)
        M[f"pbA{nm}GA"] = pc(sb["positions"][c]["ga"], 0)
    # four-lever ranking at the revealed weight by basis (decision 7): central netted, bounds all and none
    rb = R.get("ranking_by_basis") or ranking_by_basis(R)
    R["ranking_by_basis"] = rb
    for basis, nm in (("netted", "Net"), ("all", "All"), ("none", "None")):
        M[f"pbNGEFirstRev{nm}"] = WORDS.get(rb[f"n_ge_first_{basis}"], str(rb[f"n_ge_first_{basis}"]))
        M[f"pbNEngFirstRev{nm}"] = WORDS.get(rb[f"n_eng_first_{basis}"], str(rb[f"n_eng_first_{basis}"]))
        M[f"pbNGAFirstRev{nm}"] = WORDS.get(rb[f"n_ga_first_{basis}"], str(rb[f"n_ga_first_{basis}"]))
    M["pbNGAAheadGENet"] = WORDS.get(len(PANEL) - rb["n_ge_ahead_of_ga_netted"], str(len(PANEL) - rb["n_ge_ahead_of_ga_netted"]))
    M["pbNSMMaintAboveGA"] = WORDS.get(rb["n_sm_maint_above_ga"], str(rb["n_sm_maint_above_ga"]))
    M["pbAFiveGi"] = pc(cfg("A5")["state"]["G_i"])
    M["pbAThreeGap"] = tex_escape(A["A3"].band_gap["largest_label"])
    M["pbAFiveGap"] = tex_escape(A["A5"].band_gap["largest_label"])
    M["pbAFivePubCaph"] = _num(cfg("A5")["levers"]["public"]["cap_hurdle_score"], 2)
    M["pbASixPubCaph"] = _num(cfg("A6")["levers"]["public"]["cap_hurdle_score"], 2)
    M["pbAOneDur"] = _num(cfg("A1")["dur"], 2)      # dollar share (cor:ext-game-engine(a)), kept for the text's comparison
    durs = sorted({round(cfg(c)["dur"], 6) for c in PANEL})
    M["pbDurAll"] = "yes" if len(durs) == 1 else "no"
    # Part I round 2 (B1): margin keep factor of a replicated cost-of-revenue cut, 1 - phi C0, by archetype
    keeps = [cfg(c)["keep"] for c in PANEL]
    M["pbKeepMin"], M["pbKeepMax"] = _num(min(keeps), 2), _num(max(keeps), 2)
    els = [cfg(c)["pass_through"]["elasticity"] for c in PANEL]
    M["pbPtElasMin"], M["pbPtElasMax"] = _num(min(els), 2), _num(max(els), 2)
    M["pbPtRate"] = _num(cfg("A1")["pass_through"]["phi"], 2)
    # growth engine first, by owner
    for reg, nm in (("public", "Pub"), ("private_family", "Fam"), ("hybrid", "Hyb"), ("pe", "PE"), ("vc", "VC"),
                    ("permanent_capital", "PC")):
        n, d = ge_first_count(R, reg)
        M[f"pbNGEFirst{nm}"] = WORDS.get(n, str(n))
        M[f"pbNDefined{nm}"] = WORDS.get(d, str(d))
    M["pbNGEFirstRevealed"] = M["pbNGEFirstPub"]
    fam_ge = [c for c in PANEL if "private_family" in cfg(c)["levers"]
              and cfg(c)["levers"]["private_family"]["ranking"][0] == "growth engine"]
    M["pbGEFirstFamList"] = ", ".join(fam_ge) if fam_ge else "none"
    undefined_pc = [c for c in PANEL if "permanent_capital" not in cfg(c)["levers"]]
    M["pbPCUndefined"] = ", ".join(undefined_pc) if undefined_pc else "none"
    # owner weights: range across the panel
    for reg, nm in (("pe", "PE"), ("permanent_capital", "PC"), ("private_family", "Fam"), ("vc", "VC")):
        xs = [cfg(c)["levers"][reg]["X"] for c in PANEL if reg in cfg(c)["levers"]]
        M[f"pbX{nm}Min"], M[f"pbX{nm}Max"] = _num(min(xs), 1), _num(max(xs), 1)
    xd = [cfg(c)["levers"]["public"]["X_dagger0_oh"] for c in PANEL]
    xd = [v for v in xd if math.isfinite(v)]      # infinite where there is no growth spend (netted basis)
    M["pbXdagMin"], M["pbXdagMax"] = _num(min(xd), 1), _num(max(xd), 1)
    xh = [cfg(c)["state"]["X_hat"] for c in PANEL]
    M["pbXhatMin"], M["pbXhatMax"] = _num(min(xh), 1), _num(max(xh), 1)
    # engine regime runs: processes that pay under the sponsor
    pe_none = [c for c in PANEL if ((cfg(c)["regimes_engine"].get("pe") or {}).get("processes") or 0) == 0]
    M["pbPENonePay"] = ", ".join(pe_none) if pe_none else "none"
    M["pbNPENonePay"] = WORDS.get(len(pe_none), str(len(pe_none)))
    # cost of revenue: never among the first two at the public weight?
    nb = sum(cfg(c)["binding_capacity_year0"] == "decision bandwidth" for c in PANEL)
    M["pbNBindBandwidth"] = WORDS.get(nb, str(nb))
    bw = [cfg(c)["capacity_use_year0"].get("decision bandwidth") for c in PANEL]
    M["pbBandwidthUseMin"] = _num(min(bw), 2)
    M["pbBandwidthUseMax"] = _num(max(bw), 2)
    ge_eng = [c for c in PANEL if cfg(c)["levers"]["public"]["ranking"][:2] == ["growth engine", "engineering (R&D)"]]
    M["pbNGEThenEng"] = WORDS.get(len(ge_eng), str(len(ge_eng)))
    a6 = cfg("A6")["levers"]
    M["pbASixXPE"] = _num(a6["pe"]["X"], 1) if "pe" in a6 else "n.a."
    M["pbASixXVC"] = _num(a6["vc"]["X"], 1) if "vc" in a6 else "n.a."
    M["pbASixXhat"] = _num(cfg("A6")["state"]["X_hat"], 1)
    pp, _ = engine_params()
    M["pbPERate"] = _num(pp.regime.pe_irr_target, 1, pct=True)
    M["pbVCRate"] = _num(pp.regime.vc_r, 1, pct=True)
    M["pbPCRate"] = _num(pp.regime.pc_irr_unlevered, 1, pct=True)
    cor_top2 = [c for c in PANEL if "cost of revenue" in cfg(c)["levers"]["public"]["ranking"][:2]]
    M["pbNCoRTopTwo"] = WORDS.get(len(cor_top2), str(len(cor_top2)))
    # compounder
    c = R["compounder"]
    e = c["extra"]
    M["pbASevenGrep"] = _num(e["g_reported_q2_2026"], 0, pct=True)
    M["pbASevenGorg"] = _num(e["g_organic_q2_2026"], 0, pct=True)
    M["pbASevenRrep"] = _num(e["R_reported_q2_2026"], 0, pct=True)
    M["pbASevenRorg"] = _num(e["R_organic_q2_2026"], 0, pct=True)
    M["pbASevenXpc"] = _num(c["weights"]["permanent_capital"], 2)
    M["pbASevenGi"] = _num(e["G_i_2025"], 1, pct=True)
    M["pbASevenAOL"] = _num(c["acquisition_score_effect_per_point"]["AOL"], 2)
    M["pbASevenAOLprice"] = _num(e["acq_price_to_revenue"]["AOL"], 2)
    M["pbASevenReorg"] = _num(e["reorg_expense_share_2025"], 1, pct=True)
    # coverage and tiers
    cv = R["coverage"]
    M["pbCovSteps"] = str(cv["steps_in_map"])
    M["pbCovStepsPop"] = str(cv["steps_populated_per_config"])
    M["pbCovUnits"] = str(cv["activity_units_per_config"])
    M["pbCovDWA"] = str(cv["dwa_populated"])
    M["pbCovDWAAll"] = f"{int(cv['dwa_in_onet']):,}".replace(",", "{,}")
    s_ok = steps[steps.tier_now.isin(["A", "B", "C"])]
    for t in "ABC":
        M[f"pbTierStep{t}"] = _num((s_ok.tier_now == t).mean(), 0, pct=True)
        M[f"pbTierUnit{t}"] = _num((acts.tier_now == t).mean(), 0, pct=True)
    # step-level findings in the reference runs
    ref = reference_steps(steps)
    fin = ref[ref.function_id.isin(FINANCE_FUNCTIONS)]
    phys = fin[fin.binding_now.str.startswith("feasibility: physical")]
    nconf = ref.groupby(["archetype"]).ngroups
    allc = phys.groupby(["process_id", "step"]).archetype.nunique()
    every = sorted(f"{p}.{int(s_)}" for (p, s_), n in allc.items() if n == nconf)
    some = sorted(f"{p}.{int(s_)}" for (p, s_), n in allc.items() if n < nconf)
    M["pbStepsPhysicalFinance"] = WORDS.get(len(every), str(len(every)))
    M["pbStepsPhysicalFinanceList"] = ", ".join(every)
    M["pbStepsPhysicalFinanceSome"] = ", ".join(some) if some else "none"
    M["pbStepsPhysicalAll"] = str(int(ref[ref.binding_now.str.startswith("feasibility: physical")][["process_id", "step"]].drop_duplicates().shape[0]))
    icfr = ref[ref.ctl_icfr == True]  # noqa: E712
    M["pbICFRReadShare"] = _num(icfr.binding_now.str.startswith("readiness").mean(), 0, pct=True)
    M["pbICFRRelShareNow"] = _num(icfr.binding_now.str.startswith("reliability").mean(), 0, pct=True)
    hi = steps[(steps.readiness_case == "high") & steps.tier_now.isin(["A", "B", "C"]) & (steps.ctl_icfr == True)]  # noqa: E712
    M["pbICFRRelShare"] = _num(hi.binding_now.str.startswith("reliability").mean(), 0, pct=True)
    for mode, nm in (("O", "Out"), ("H", "House"), ("U", "Aug"), ("A", "Auto")):
        M[f"pbICFR{nm}High"] = _num((hi.mode_activity_now == mode).mean(), 0, pct=True)
    allhi = steps[(steps.readiness_case == "high") & steps.tier_now.isin(["A", "B", "C"])]
    M["pbRelShareHigh"] = _num(allhi.binding_now.str.startswith("reliability").mean(), 0, pct=True)
    M["pbReadShareLow"] = _num(ref.binding_now.str.startswith("readiness").mean(), 0, pct=True)
    M["pbCapShareLow"] = _num(ref.binding_now.str.startswith("feasibility: capability").mean(), 0, pct=True)
    M["pbAutoStepsHigh"] = str(int((allhi.mode_activity_now == "A").sum()))
    M["pbAutoStepsHighShare"] = _num((allhi.mode_activity_now == "A").mean(), 0, pct=True)
    M["pbAugStepsLow"] = _num((ref.mode_activity_now == "U").mean(), 0, pct=True)
    # invoice chain, matching step (P02 step 5) at A2 and A5
    for code, nm in (("A2", "Two"), ("A5", "Five")):
        for case, cn in (("low", "Low"), ("high", "High")):
            g = steps[(steps.archetype == code) & (steps.readiness_case == case) & (steps.process_id == "P02") & (steps.step == 5)]
            if not len(g):
                continue
            r = g.iloc[0]
            M[f"pbInv{nm}{cn}Mode"] = str(r.mode_activity_now)
            M[f"pbInv{nm}{cn}Bind"] = tex_escape(r.binding_now)
            M[f"pbInv{nm}{cn}Dstar"] = _num(r.gate_min_detection, 2)
            M[f"pbInv{nm}{cn}Dnow"] = _num(r.gate_detection_now, 2)
            M[f"pbInv{nm}{cn}Vol"] = f"{float(r.volume_per_year):,.0f}".replace(",", "{,}")
            M[f"pbInv{nm}{cn}Tier"] = str(r.tier_now)
            M[f"pbInv{nm}{cn}Read"] = _num(r.pre_readiness_now, 2)
            M[f"pbInv{nm}{cn}Floor"] = _num(r.pre_readiness_floor, 2)
            M[f"pbInv{nm}{cn}Resid"] = pc(r.residual_error_A_target, 1)
    M["pbInvGate"] = pc(float(steps[(steps.process_id == "P02") & (steps.step == 5)].gate_max_residual_error.dropna().iloc[0]), 0)
    return M


def write_tables(R: dict, archs, steps: pd.DataFrame, acts: pd.DataFrame):
    T = ROOT / "part2" / "tables"
    T.mkdir(exist_ok=True)
    M = explicit_macros(R, archs, steps, acts)
    with open(T / "playbook_macros.tex", "w") as fh:
        fh.write("% Generated by code/playbook/run_archetypes.py. Do not edit by hand.\n")
        for k in sorted(M):
            fh.write(f"\\newcommand{{\\{k}}}{{{M[k]}}}\n")
    R["macros"] = M
    write_archetype_table(R, archs, T)
    write_main_table(R, archs, steps, T)
    write_grid(R, T)
    write_function_summary(acts, T)
    write_process_summary(steps, T)
    write_full_steps(steps, T)
    write_paper1_macros(R, archs)


def write_archetype_table(R, archs, T):
    rows = []
    for a in archs:
        if a.code == "A7":
            c = R["compounder"]
            e, st = c["extra"], c["state"]
            rows.append(f"A7 {tex_escape(a.name)} & 1 & {_num(a.g, 0, pct=True)}$^\\dagger$ & {_num(a.m, 0, pct=True)}$^\\dagger$ & "
                        f"{_num(a.sm, 0, pct=True)} & {_num(st['sigma'], 0, pct=True)} & {_num(a.ga, 0, pct=True)} & {_num(a.rd, 0, pct=True)} & {_num(a.gm, 0, pct=True)} & -- & "
                        f"{_num(st['G_i'], 1, pct=True)} & {_num(st['X_hat'], 1)} & F-1, 6-K \\\\")
            continue
        s = R["configs"].get(f"{a.code}_low")
        st = s["state"] if s else a.state(alpha=0.3)
        rows.append(f"{a.code} {tex_escape(a.name)} & {a.n} ({a.n_firms}) & {_num(a.g, 1, pct=True)} & {_num(a.m, 1, pct=True)} & "
                    f"{_num(a.sm, 0, pct=True)} & {_num(st['sigma'], 0, pct=True)} & {_num(a.ga, 0, pct=True)} & {_num(a.rd, 0, pct=True)} & {_num(a.gm, 0, pct=True)} & "
                    f"{_num(st['k'], 2)} & {_num(st['G_i'], 1, pct=True)} & {_num(st['X_hat'], 1)} & "
                    f"p{100 * a.q_g:.0f}/p{100 * a.q_m:.0f}/p{100 * a.q_R:.0f} \\\\")
    tex = r"""\begin{table}[t]
\centering
\caption{Archetypes: cell medians of 2023--25 non-acquisition core firm-years and their calibrated Part~I states (Assumption~\ref{ass:playbook-calib}, $\alpha$ the engine's default)}\label{tab:playbook-archetypes}
\scriptsize
\setlength{\tabcolsep}{3pt}
\resizebox{\textwidth}{!}{\begin{tabular}{@{}lrrrrrrrrrrrl@{}}
\toprule
 & $n$ (firms) & $g$ & $m$ & S\&M & $\sigma$ & G\&A & R\&D & GM & $k$ & $G_i$ & $\hat X$ & Ranks $g/m/R$\\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}}

\smallskip
\begin{minipage}{0.98\linewidth}\scriptsize
Notes: percent of revenue except $n$, $k$ and $\hat X$; $m$ is the free-cash-flow margin after stock-based compensation; GM gross margin. $\sigma$ is growth spend on the maintenance-netted basis, S\&M less a maintenance base of """ + _num(AR.MAINT_BASE, 1, pct=True) + r"""\% of revenue (zero below it; Part~I's central basis), the rest of S\&M being a cost line; $\mathsf r_\sigma=""" + _num(AR.SPEND_RATIO_NET, 2) + r"""$, the median ratio of S\&M above the base to excess growth. $k$ is capital spending and capitalized software over revenue divided by $g$; $G_i=g-\sigma/\mathsf r_\sigma$; $\hat X=k+\mathsf r_\sigma/\alpha$. $^\dagger$A7: fiscal 2025 reported growth and the fully charged cash margin (operating cash flow plus investing cash flow, which includes acquisitions) from the F-1; its $G_i$ is $\ln$ of its 2025 net revenue retention; its S\&M is below the base, so it has no growth spend on this basis and $\hat X$ is the common weight. Generated by \texttt{code/playbook/run\_archetypes.py}.
\end{minipage}
\end{table}
"""
    (T / "playbook_archetypes.tex").write_text(tex)


LINE_SHORT = {"gm": "gross margin", "sms": "S\\&M", "rds": "R\\&D", "gas": "G\\&A"}
LEVER_TINY = {"growth engine": "growth engine", "overhead (G&A)": "G\\&A", "engineering (R&D)": "R\\&D",
              "cost of revenue": "cost of revenue"}
CAP_SHORT = {"decision bandwidth": "bandwidth", "change capacity": "change capacity", "security review": "security review",
             "transformation budget": "budget", "dual-running budget": "dual running"}


def _avoid(s: dict, steps_cfg: pd.DataFrame, steps_hi: pd.DataFrame | None = None) -> list[str]:
    """Levers to avoid at the reference setup (Corollary cor:playbook-nopay; item numbers in parentheses)."""
    L = s["levers"]["public"]
    out = [f"(iii) owned compute below {L['cap_hurdle_score']:.2f} of opex per \\$ of capital"]
    if L["cor"] < L["oh"]:
        out.append(f"(ii) cost of revenue as a margin lever (keeps {s['keep']:.2f} of the cut)")
    pe = s["levers"].get("pe")
    if s["state"].get("sigma", 1.0) <= 0:
        out.append("(i) growth engine: no S\\&M above the maintenance base")
    elif pe and pe["ranking"][0] != "growth engine":
        eng_first = pe["ranking"][0] == "engineering (R&D)"
        xd = pe["X_dagger0_eng"] if eng_first else pe["X_dagger0_oh"]
        out.append(f"(i) growth engine under a sponsor ($X={pe['X']:.1f}<{xd:.1f}$)")
    hi = steps_hi if steps_hi is not None else steps_cfg
    if len(hi):
        ok = hi[hi.tier_now.isin(["A", "B", "C"])]
        det = ok[(ok.ctl_icfr == True) & ok.binding_now.str.startswith("reliability")]  # noqa: E712
        if len(det):
            out.append(f"(iv) automating {len(det)} ICFR steps that fail the catch-rate gate at $\\iota=0.9$")
    return out


def write_main_table(R, archs, steps, T):
    rows = []
    for a in archs:
        if a.code == "A7":
            c = R["compounder"]
            e = c["extra"]
            rows.append(
                f"A7 {tex_escape(a.name)} & reported $g={100 * e['g_reported_q2_2026']:.0f}\\%$, organic {100 * e['g_organic_q2_2026']:.0f}\\%; "
                f"$m_{{op}}={100 * e['m_op_q2_2026']:.0f}\\%$ (Q2 2026) & base shrinks ($G_i={100 * e['G_i_2025']:.1f}\\%$): the treadmill "
                f"& 1. owner capability (platform, rebuild); 2. G\\&A and R\\&D cost-out "
                f"& (viii) acquisitions above $X^G={c['weights']['permanent_capital']:.2f}$ times revenue; (i) growth spend "
                f"& \\emph{{not generated: the engine models no acquisitions or platform owner (W12)}} \\\\")
            continue
        s = R["configs"].get(f"{a.code}_low")
        if not s:
            continue
        L = s["levers"]["public"]
        two = first_two(L)
        lv = "; ".join(f"{i + 1}. {LEVER_TINY[k]} {100 * v:.1f}" for i, (k, v) in enumerate(two))
        sc = steps[(steps.archetype == a.code) & (steps.readiness_case == "low")]
        sh = steps[(steps.archetype == a.code) & (steps.readiness_case == "high")]
        av = "; ".join(_avoid(s, sc, sh))
        w1 = [w for w in s["waves"] if w.get("wave") == 1]
        if w1:
            w = w1[0]
            seen = []
            for x in w["names"]:
                x2 = x.split(":")[0] + " (other work)" if "other work" in x else x
                if x2 not in seen:
                    seen.append(x2)
            nm = ", ".join(tex_escape(x) for x in seen[:3])
            wave = f"{nm} ({w['start_year']}; NPV \\${w['npv'] / 1e6:.0f}M)"
        else:
            wave = "none (no process pays)"
        pos = (f"$g={100 * a.g:.0f}\\%$ (p{100 * a.q_g:.0f}), $m={100 * a.m:.0f}\\%$ (p{100 * a.q_m:.0f}); $n={a.n}$")
        bind = (f"{LINE_SHORT[a.band_gap['largest']]} {100 * a.band_gap[a.band_gap['largest']]:.0f} pts; "
                f"{CAP_SHORT.get(s['binding_capacity_year0'], s['binding_capacity_year0'])}")
        rows.append(f"{a.code} {tex_escape(a.name)} & {pos} & {bind} & {lv} & {av} & {wave} \\\\")
    body = "\n\\addlinespace\n".join(rows)
    M_ = R["macros"]
    durs = sorted({round(R["configs"][f"{c}_low"]["dur"], 3) for c in PANEL})
    dur_txt = (f"{durs[0]:g}" if len(durs) == 1 else f"{durs[0]:g} to {durs[-1]:g}")
    tex = r"""\begin{table}[p]
\centering
\caption{The playbook by archetype at the reference setup (public owner, today's readiness 0.4, standalone firm). Lever values are points of the maximal score per 10\% of a line automated, at the owner's weight (Proposition~\ref{prop:playbook-rank}(a)); levers to avoid cite the items of Corollary~\ref{cor:playbook-nopay}; the first wave is the engine's (Section~\ref{sec:playbook-table})}\label{tab:playbook}
\scriptsize
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.1}
\newcolumntype{Q}[1]{>{\raggedright\arraybackslash}p{#1}}
\begin{tabular}{@{}Q{1.8cm}Q{2.1cm}Q{1.9cm}Q{2.4cm}Q{4.0cm}Q{2.9cm}@{}}
\toprule
Archetype & Position (panel) & Binding: largest gap; scarcest capacity & First two levers (points) & Levers to avoid & First wave (engine)\\
\midrule
""" + body + r"""
\bottomrule
\end{tabular}

\smallskip
\begin{minipage}{0.98\linewidth}\scriptsize
Notes: positions are cell medians of 2023--25 non-acquisition core firm-years of the audited v3 sample (Definition~\ref{def:playbook-archetypes}); p$q$ is the population quantile rank. Binding: the cost line with the largest gap of the archetype's median to the top decile of operating margin in its growth band (bands with edges at 0, 10, 20, 30, 40 and 60\% and the sample of \texttt{code/decompose\_gap.py}), in points of revenue, and the engine's most used capacity in the first plan year. Lever values at the public owner's weight, the revealed weight $\hat X$ (the panel's firms are public, so their spending reveals a public owner's net weight $X^{\rm my}$ of eq.~\eqref{eq:reg-Xmy}); the growth engine is automation of the selling and marketing that buys growth, S\&M above a maintenance base of """ + M_["pbMaintBase"] + r"""\% of revenue (first order $x\sigma^*$; Part~I's central, maintenance-netted basis, with S\&M up to the base a cost line); R\&D treats all R\&D as maintenance, an upper bound; cost of revenue at the margin share a replicated cut keeps, $1-\bar\varphi^{\rm ind}C_0$, at the engine's central pass-through rate of """ + M_["pbPtRate"] + r""" and the archetype's unit cost per dollar of price $C_0$ (Part~I's round-2 mapping: the rate applies to the unit-cost saving and the margin is computed at the lower price; the durable share """ + dur_txt + r""", a dollar share, does not enter the score). With all S\&M as growth spend, Part~I's upper bound, the growth engine would be the first lever at """ + M_["pbNGEFirstRevAll"] + r""" archetypes, and with none of it at """ + M_["pbNGEFirstRevNone"] + r""" (Section~\ref{sec:playbook-limits}). Levers to avoid: owned compute below its score hurdle $g^*+\delta_K$ (after tax with domestic servers fully expensed, $\psi=1$; times $(1-\psi\tau)/(1-\tau)$ for servers abroad); growth engine under a sponsor when the sponsor's weight is below $X^\ddagger_0$ for the line that ranks first; ICFR steps counted at readiness 0.9. Waves from the engine's roadmap; residual work streams are named by function. Generated by \texttt{code/playbook/run\_archetypes.py}.
\end{minipage}
\end{table}
"""
    (T / "playbook_table.tex").write_text(tex)


def _ev(v: dict) -> str:
    """Engine program value of a regime run in $M ('--' if the run reports none)."""
    x = v.get("value") if v else None
    return "--" if x is None else _num(float(x) / 1e6, 0)


def _xd(v: float) -> str:
    return f"{v:.1f}" if math.isfinite(v) else r"$\infty$"


def write_grid(R, T):
    rows = []
    for key in sorted(R["configs"]):
        code, case = key.split("_")
        if case != "low":
            continue
        s = R["configs"][key]
        hi = R["configs"].get(f"{code}_high", {})
        for nm in REGIME_ORDER:
            L = s["levers"].get(nm)
            if not L:
                why = (s["weights"].get("permanent_capital_undefined") if nm == "permanent_capital" else None) or "weight not defined"
                rows.append(f"{code} & {REGIME_LABEL[nm]} & \\multicolumn{{10}}{{l}}{{{tex_escape(why)}}} \\\\")
                continue
            ve = (s["regimes_engine"].get(nm) or {})
            vh = ((hi.get("regimes_engine") or {}).get(nm) or {})
            top = LEVER_SHORT[L["ranking"][0]]
            rows.append(f"{code} & {REGIME_LABEL[nm]} & {L['X']:.1f} & {100 * L['sigma_star']:.1f} & {100 * L['ge_cost_first']:.1f} & "
                        f"{100 * L['oh']:.1f} & {100 * L['eng']:.1f} & {100 * L['cor']:.1f} & {100 * L['ret_point']:.1f} & "
                        f"{_xd(L['X_dagger0_oh'])} & {top} & {_ev(ve)} / {_ev(vh)} \\\\")
        rows.append(r"\addlinespace")
    tex = r"""\begin{table}[p]
\centering
\caption{Lever values by archetype and owner (points of the maximal score; the growth engine, overhead, engineering and cost of revenue per 10\% of the line, retention per point of zero-spend growth) and the engine's program value at readiness 0.4 and 0.9}\label{tab:playbook-grid}
\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}llrrrrrrrrlr@{}}
\toprule
 & Owner & $X_{\mathsf o}$ & $\sigma^*$ & Growth & G\&A & R\&D & CoR & Retention & $X^\ddagger_0$ & First lever & Engine value (\$M) \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}

\smallskip
\begin{minipage}{0.98\linewidth}\scriptsize
Notes: $X_{\mathsf o}$ at the archetype's state from Proposition~\ref{prop:reg-weight} and Proposition~\ref{prop:acq-pc}(d), evaluated with the engine's formulas and regime presets: public, the revealed weight $\hat X$; dual class, $X^{\rm my}$ at the dual-class pressure from the going-concern weight $k+(1+\mathfrak w)(\hat X-k)$; family, that weight scaled by $v_0(r_{\rm fam})/v_0(r_w)$; sponsor and VC, eq.~\eqref{eq:reg-Xexit} at entry with $\hat m=m_0-kG_i$ and, for the sponsor, the EBITDA rule at the marginal EBITDA margin $m_0$; permanent acquirer, $X^G=\hat m/(\bar{\mathfrak i}_{\rm U}-G_i)$, defined only for $G_i<\bar{\mathfrak i}_{\rm U}$; $\sigma^*$ is the owner's optimal growth spend (\% of revenue). Growth spend on Part~I's central, maintenance-netted basis (Assumption~\ref{ass:playbook-calib}). $X^\ddagger_0$ is the weight above which the growth engine outranks overhead (Proposition~\ref{prop:playbook-rank}(b)), infinite where S\&M is below the maintenance base and there is no growth spend. Engine value: the program value of the engine's own run for that regime (its presets) at readiness 0.4 / 0.9; its public, dual-class, sponsor and acquirer weights equal the $X_{\mathsf o}$ shown (\texttt{notes/playbook\_engine\_spec.md}, items W1, W14, W15, W17), while its VC weight uses its own exit rule; its sponsor and acquirer runs select no process for A1, A4 and A5; the engine has no permanent-acquirer platform, so that row values the firm's own transformation at the acquirer's hurdle. Generated by \texttt{code/playbook/run\_archetypes.py}.
\end{minipage}
\end{table}
"""
    (T / "playbook_grid.tex").write_text(tex)


def write_function_summary(acts: pd.DataFrame, T):
    a = acts[(acts.archetype == FULL_STEP_ARCHETYPE)].copy()
    a["h"] = a.fte_in_house.astype(float)
    rows = []
    for (fid, fname), g in a[a.readiness_case == "low"].groupby(["function_id", "function_name"]):
        gh = a[(a.readiness_case == "high") & (a.function_id == fid)]
        tot = g.h.sum()
        if tot <= 0:
            continue
        sh = lambda df, col, m: df.loc[df[col] == m, "h"].sum() / max(df.h.sum(), 1e-9)
        bind = g.groupby("binding_now").h.sum().sort_values(ascending=False)
        top = bind.index[0] if len(bind) else ""
        tiers = g.groupby("tier_now").h.sum() / tot
        rows.append(f"{tex_escape(fname)} & {tot:.0f} & {100 * sh(g, 'mode_activity_now', 'A'):.0f} & {100 * sh(g, 'mode_activity_now', 'U'):.0f} & "
                    f"{100 * sh(gh, 'mode_activity_now', 'A'):.0f} & {100 * sh(gh, 'mode_activity_now', 'U'):.0f} & {tex_escape(top)} & "
                    f"{100 * tiers.get('A', 0):.0f}/{100 * tiers.get('B', 0):.0f}/{100 * tiers.get('C', 0):.0f} \\\\")
    tex = r"""\begin{table}[t]
\centering
\caption{Activity decisions by function for archetype """ + FULL_STEP_ARCHETYPE + r""" (shares of in-house FTE): automated and augmented now, at readiness 0.4 and 0.9, the most common binding constraint at 0.4, and the confidence tiers}\label{tab:playbook-functions}
\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}lrrrrrp{4.2cm}r@{}}
\toprule
 & & \multicolumn{2}{c}{$\iota=0.4$ (\%)} & \multicolumn{2}{c}{$\iota=0.9$ (\%)} & & Tier A/B/C\\
\cmidrule(lr){3-4}\cmidrule(lr){5-6}
Function & FTE & A & U & A & U & Binding constraint (most FTE) & (\% FTE)\\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}

\smallskip
\begin{minipage}{0.98\linewidth}\scriptsize
Notes: activity decisions of the engine (cheapest feasible mode by its choice cost, 2026); tiers of Definition~\ref{def:playbook-tier}. Generated by \texttt{code/playbook/run\_archetypes.py}; rows in \texttt{data/playbook/playbook\_activities.csv}.
\end{minipage}
\end{table}
"""
    (T / "playbook_functions.tex").write_text(tex)


def write_process_summary(steps: pd.DataFrame, T):
    s = steps[(steps.archetype == FULL_STEP_ARCHETYPE) & (steps.readiness_case == "low") & steps.tier_now.isin(["A", "B", "C"])].copy()
    sh = steps[(steps.archetype == FULL_STEP_ARCHETYPE) & (steps.readiness_case == "high") & steps.tier_now.isin(["A", "B", "C"])]
    rows = []
    for (pid, pname), g in s.groupby(["process_id", "process_name"]):
        gh = sh[sh.process_id == pid]
        cnt = lambda df, col: "".join(f"{m}{int((df[col] == m).sum())}" if (df[col] == m).sum() else "" for m in "HOUAN")
        bind = g.binding_now.value_counts()
        wave = g.wave.dropna()
        rows.append(f"{pid} {tex_escape(pname)} & {len(g)} & {cnt(g, 'mode_step_now')} & {cnt(gh, 'mode_step_now')} & "
                    f"{tex_escape(bind.index[0]) if len(bind) else ''} & {int(g.ctl_icfr.sum())} & "
                    f"{int(wave.iloc[0]) if len(wave) else '--'} & {''.join(sorted(set(g.tier_now)))} \\\\")
    tex = r"""\begin{table}[p]
\centering
\caption{Step decisions by process for archetype """ + FULL_STEP_ARCHETYPE + r""": modes of the steps in the engine's best process plan starting now (counts by mode) at readiness 0.4 and 0.9, the most common binding constraint on automation, ICFR steps, the wave and the tiers}\label{tab:playbook-processes}
\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}p{4.0cm}rllp{4.0cm}rrl@{}}
\toprule
Process & Steps & Modes, 0.4 & Modes, 0.9 & Binding constraint (most steps) & ICFR & Wave & Tiers\\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}

\smallskip
\begin{minipage}{0.98\linewidth}\scriptsize
Notes: H in house, O outsourced, U augmented, A automated, N eliminated; a step keeps its baseline mode when no column of its process has positive value. Generated by \texttt{code/playbook/run\_archetypes.py}; rows in \texttt{data/playbook/playbook\_steps.csv}.
\end{minipage}
\end{table}
"""
    (T / "playbook_processes.tex").write_text(tex)


def write_full_steps(steps: pd.DataFrame, T):
    s = steps[(steps.archetype == FULL_STEP_ARCHETYPE) & (steps.readiness_case == "low")].copy()
    sh = steps[(steps.archetype == FULL_STEP_ARCHETYPE) & (steps.readiness_case == "high")].set_index(["process_id", "step"])
    rows = []
    for r in s.itertuples():
        if not isinstance(r.tier_now, str) or r.tier_now not in "ABC" or not r.tier_now:
            rows.append(f"{r.process_id}.{int(r.step)} & {tex_escape(r.step_name)} & \\multicolumn{{6}}{{l}}{{not in the activity map of this firm}} \\\\")
            continue
        try:
            h = sh.loc[(r.process_id, r.step)]
            mh = h.mode_activity_now
        except KeyError:
            mh = "--"
        gate = f"{r.gate_min_detection:.2f}" if r.binding_now.startswith("reliability") else ""
        rows.append(f"{r.process_id}.{int(r.step)} & {tex_escape(r.step_name)} & {r.mode_activity_now}/{r.mode_step_now} & {mh} & "
                    f"{tex_escape(r.binding_now)} & {gate} & {'yes' if r.ctl_icfr else ''} & {r.tier_now} \\\\")
    tex = r"""\begingroup\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{longtable}{@{}lp{4.4cm}llp{4.2cm}rll@{}}
\caption{Archetype """ + FULL_STEP_ARCHETYPE + r""" at step level, readiness 0.4: activity and step decisions, the mode at readiness 0.9, the binding constraint on automation, the detection gate where reliability binds, ICFR scope and the confidence tier}\label{tab:playbook-steps}\\
\toprule
Step & Name & Now (act./step) & 0.9 & Binding constraint & $d^*$ & ICFR & Tier\\
\midrule
\endfirsthead
\toprule
Step & Name & Now (act./step) & 0.9 & Binding constraint & $d^*$ & ICFR & Tier\\
\midrule
\endhead
\bottomrule
\endfoot
""" + "\n".join(rows) + r"""
\end{longtable}
\endgroup
"""
    (T / "playbook_steps_full.tex").write_text(tex)


PAPER1_ALPHA = 0.3            # Paper 1's examples (Section sec:model-statics)
PAPER1_DELTA = 0.25           # Paper 1, Corollary cor:capital intuition and Remark rem:assumptions(c)
PAPER1_SCREEN = (2.0, 3.0)    # Paper 1, Section sec:model-valuation: investors' screening weights


def paper1_positions(archs) -> list[dict]:
    """Part I objects at the six panel positions (Paper 1 notation only), on the central maintenance-netted basis of growth
    spend (author decision of 2 Nov 2026, decision 7) with the all-S&M and no-S&M bounds: growth spend sigma, the
    growth-engine and overhead values per 10 percent, the ratio (a/sigma)^(1-alpha) (infinite with no growth spend), the
    switch weight X^ddagger_0, the lever that ranks first at the position's own weight on each basis, and the capital
    hurdle."""
    al = PAPER1_ALPHA
    lead = lambda sig, ga: "growth engine" if sig > ga else "G&A cut"
    out = []
    for a in archs:
        if a.code == "A7":
            continue
        st = a.state(alpha=al)                    # central basis (netted)
        sig = st["sigma"]
        ratio = (a.ga / sig) ** (1 - al) if sig > 0 else math.inf
        xd = st["k"] + (st["X_hat"] - st["k"]) * ratio if sig > 0 else math.inf
        if sig > 0:
            assert abs(xd - LV.x_dagger0(a.ga, st["ell"], st["k"], al)) < 1e-9
        sig_all = AR.growth_spend(a.sm, "all")[0]
        out.append({"code": a.code, "name": a.name, "n": a.n, "g": a.g, "m": a.m, "sm": a.sm, "sigma": sig, "a_SM": st["a_SM"],
                    "ga": a.ga, "rd": a.rd, "k": st["k"], "G_i": st["G_i"], "X_hat": st["X_hat"], "ge": LV.PROP * sig,
                    "pull": LV.PROP * sig / al, "oh": LV.PROP * a.ga, "ratio": ratio, "X_dagger0": xd,
                    "ratio_all_sm": (a.ga / sig_all) ** (1 - al), "lead": lead(sig, a.ga), "lead_all_sm": lead(sig_all, a.ga),
                    "lead_no_sm": "G&A cut", "cap_hurdle": a.g + PAPER1_DELTA,
                    "gap_line": a.band_gap.get("largest_label", "") if a.band_gap else "",
                    "gap_pts": a.band_gap.get(a.band_gap.get("largest", ""), float("nan")) if a.band_gap else float("nan")})
    return out


def write_paper1_macros(R, archs):
    """Numbers and the table for sections/levers_by_position.tex: Part I objects only (Paper 1's notation), at the
    archetype states computed from the panel with Paper 1's conventions (archetypes.py) and alpha = 0.3. Central basis of
    growth spend: maintenance-netted (author decision of 2 Nov 2026); all S&M and no S&M are bounds."""
    P = paper1_positions(archs)
    R["paper1_positions"] = P
    M = {}
    al = PAPER1_ALPHA
    fin = [p for p in P if p["sigma"] > 0]
    # central basis (netted). WITHDRAWN UNDER D-1, kept defined: lpXhat, lpXdagMin, lpXdagMax, lpScreenBelowAll
    M["lpXhat"] = _num(AR.spend_ratio() / al, 0)
    M["lpRatio"] = _num(AR.spend_ratio(), 2)
    M["lpRatioMin"] = _num(min(p["ratio"] for p in fin), 2) if fin else "n.a."
    M["lpRatioMax"] = _num(max(p["ratio"] for p in fin), 2) if fin else "n.a."
    M["lpXdagMin"] = _num(min(p["X_dagger0"] for p in fin), 1) if fin else "n.a."
    M["lpXdagMax"] = _num(max(p["X_dagger0"] for p in fin), 1) if fin else "n.a."
    M["lpScreenBelowAll"] = "yes" if max(PAPER1_SCREEN) < min(p["X_dagger0"] for p in P) else "no"
    M["lpGEFirstAll"] = "yes" if all(p["ge"] > p["oh"] for p in P) else "no"
    M["lpBasis"] = "maintenance-netted"
    M["lpMaintBase"] = _num(AR.MAINT_BASE, 1, pct=True)
    M["lpNPositions"] = str(len(P))
    M["lpNGEFirstNet"] = str(sum(p["lead"] == "growth engine" for p in P))
    M["lpNGACutFirstNet"] = str(sum(p["lead"] == "G&A cut" for p in P))
    M["lpNGEFirstAllSM"] = str(sum(p["lead_all_sm"] == "growth engine" for p in P))
    M["lpNGEFirstNoSM"] = str(sum(p["lead_no_sm"] == "growth engine" for p in P))
    M["lpNNoGrowthSpend"] = str(sum(p["sigma"] <= 0 for p in P))
    M["lpGEFirstNetList"] = ", ".join(p["name"] for p in P if p["lead"] == "growth engine") or "none"
    M["lpNoGrowthSpendList"] = ", ".join(p["name"] for p in P if p["sigma"] <= 0) or "none"
    M["lpGEFirstAllSM"] = "yes" if all(p["lead_all_sm"] == "growth engine" for p in P) else "no"
    M["lpRatioAllSMMin"] = _num(min(p["ratio_all_sm"] for p in P), 2)
    M["lpRatioAllSMMax"] = _num(max(p["ratio_all_sm"] for p in P), 2)
    for p in P:
        if p["code"] == "A5":
            M["lpAFivecaph"] = _num(p["cap_hurdle"], 2)
        if p["code"] == "A6":
            M["lpASixcaph"] = _num(p["cap_hurdle"], 2)
    d = Path(ROOT / "sections" / "tables")
    d.mkdir(exist_ok=True)
    with open(d / "levers_position_macros.tex", "w") as fh:
        fh.write("% Generated by code/playbook/run_archetypes.py from data/panel_v3.csv (audited v3 core sample, acq_flag_v3). Do not edit by hand.\n")
        for k in sorted(M):
            fh.write(f"\\newcommand{{\\{k}}}{{{M[k]}}}\n")
    rows = []
    short = lambda x: "G\\&A cut" if x == "G&A cut" else "growth engine"
    for p in P:   # round 2 (IB2-N4, X2-N3, D-1): weight-free columns only; decision 7: netted central, all-S&M lead beside it
        ratio = _num(p["ratio"], 2) if math.isfinite(p["ratio"]) else "--"
        rows.append(f"{tex_escape(p['name'])} & {p['n']} & {_num(p['g'], 0, pct=True)} & {_num(p['m'], 0, pct=True)} & "
                    f"{_num(p['sm'], 0, pct=True)} & {_num(p['sigma'], 0, pct=True)} & {_num(p['ga'], 0, pct=True)} & {_num(p['k'], 2)} & "
                    f"{ratio} & {short(p['lead'])} & {short(p['lead_all_sm'])} & {_num(p['cap_hurdle'], 2)} \\\\")
    tex = r"""\begin{table}[t]
\centering
\caption{Levers at six positions of the 2023--25 core sample: the ratio test of Proposition~\ref{prop:levers-position}(b), which needs no growth weight}\label{tab:levers-position}
\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}lrrrrrrrrllr@{}}
\toprule
 & & & & & & & & & \multicolumn{2}{c}{First at own weight} & \\
\cmidrule(lr){10-11}
Position & $n$ & $g$ & $m$ & S\&M & $\hat\sigma$ & G\&A & $k$ & $(a/\hat\sigma)^{1-\alpha}$ & central & all S\&M & $g+\delta$\\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}

\smallskip
\begin{minipage}{0.98\linewidth}\scriptsize
Notes: cell medians of non-acquisition core firm-years, fiscal 2023--25, in percent of revenue except $n$, $k$ and the ratio; $m$ is the free-cash-flow margin after stock-based compensation; $\alpha=0.3$. $\hat\sigma$ is growth spend on the central maintenance-netted basis: the selling-and-marketing share less a maintenance base of """ + M["lpMaintBase"] + r"""\% of revenue, the median S\&M share, in the previous year, of firm-years growing at or below the year's median, and zero below it (the rest of S\&M is a cost line); $a$ is the general and administrative share. $k$ is capital spending and capitalized software over revenue divided by $g$. The ratio $(a/\hat\sigma)^{1-\alpha}$ equals $(X^\ddagger_0-k)/(X-k)$ at the weight $X$ at which the position's spending is optimal: a 10\% cut in general and administrative cost outranks a 10\% saving in the cost of growth at every weight whose distance from $k$ is below the ratio times that $X-k$, and at the position's own weight the cut ranks first if and only if the ratio exceeds one; with no growth spend (--) the cut ranks first at every weight. ``Central'' is the lever that ranks first at the position's own weight on that basis; ``all S\&M'' is the same test with all selling and marketing counted as growth spend, a bound under which the ratio lies between """ + M["lpRatioAllSMMin"] + r""" and """ + M["lpRatioAllSMMax"] + r"""; with no S\&M counted as growth spend, the other bound, the cut ranks first at every position. No weight is estimated (Section~\ref{sec:empirics}). $g+\delta$ is the opex saved per dollar of compute capital needed to raise the score at $\delta=0.25$. Generated by \texttt{code/playbook/run\_archetypes.py}.
\end{minipage}
\end{table}
"""
    (d / "tab_levers_position.tex").write_text(tex)


if __name__ == "__main__":
    main()
