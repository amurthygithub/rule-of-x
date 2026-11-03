# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""End-to-end run: inputs -> firm -> economics -> plan columns -> optimized program for every ownership regime ->
scenarios and regret -> Monte Carlo over data, class b and d parameters and outcomes -> roadmap, people, product,
security and failure modes, sensitivity, breakpoints -> report. Deterministic for a given seed. Runs locally: no
network calls, no telemetry; files are written only through safeio.OutputDir into the chosen output folder."""
from __future__ import annotations

import os
import platform
import time
from pathlib import Path

import numpy as np
import pandas as pd

from . import REQUIRED_NOTICE, __version__
from . import economics as E
from . import formulas as F
from . import impute, industry, ingest, levers, optimize as O, people, product, regimes, risk, roadmap, scenarios, security
from .config import ConfigError, find_data_dir, load_params, parse_override, source_hashes
from .plans import PlanBuilder
from .priors import load_priors


class RunLog:
    """Progress messages with timings. Messages never contain input values (only counts and stage names)."""

    def __init__(self, echo=None):
        self.lines: list[str] = []
        self.t0 = time.time()
        self.c0 = time.process_time()
        self.echo = echo

    def __call__(self, msg: str):
        line = f"[{time.time() - self.t0:7.1f}s wall, {time.process_time() - self.c0:7.1f}s cpu] {msg}"
        self.lines.append(line)
        if self.echo:
            self.echo(line)


def build_params(data_dir, overrides: list[str] | None, scenario: str | None, firm=None):
    p = load_params(data_dir)
    for o in overrides or []:
        k, v = parse_override(o)
        p.set(k, v, origin="command line")
    return p


def frontier_shift(econ, sol, prog, p) -> dict:
    """Part I mapping at the end of the plan (core prop:tasks-aggregate; spec 1, 9): changes in c_h, c_c, a, k and
    the growth spend, the first-order change of R*_X at X = 1 (Rule of 40) and at the firm's own weight, and the
    exact score before and after."""
    f = econ.firm
    pt = f.part1
    T = econ.T
    y = T - 1
    S = float(pt["S"] * econ.vf[y])
    Ut = f.units
    bucket = Ut.cost_bucket.values
    d = {"cogs_labor": 0.0, "cogs_compute": 0.0, "opex": 0.0, "opex_ga": 0.0, "opex_rnd": 0.0, "opex_sm_maint": 0.0, "grow": 0.0,
         "grow_base": 0.0, "capital": 0.0}
    # S&M basis (Paper 1 round 2, decisions 4 and 7): on the netted basis only the S&M above the maintenance base is growth
    # spend; savings on S&M activities are split in proportion (the units do not say which S&M work maintains the base),
    # the maintenance part entering a as a cost saving
    sm_sh = float(f.fin["sm"]) / float(pt["S"]) if float(pt["S"]) > 0 else 0.0
    grow_frac = (sm_sh - float(pt.get("sm_maint", 0.0))) / sm_sh if sm_sh > 0 else 1.0
    for c in sol.sel.values():
        us = np.flatnonzero(econ.unit_proc == prog.cols.proc[c])
        md = np.asarray(prog.cols.modes[c])
        l = int(prog.cols.level[c])
        v = Ut.v.values[us] * econ.vf[y]
        base = econ.cash[us, l, y, :][np.arange(len(us)), econ.base_mode[us]]
        new = econ.cash[us, l, y, :][np.arange(len(us)), md]
        inf_new = econ.inference[us, l, y, :][np.arange(len(us)), md]
        ok = np.isfinite(base) & np.isfinite(new)
        sav = np.where(ok, (base - new) * v, 0.0) * float(sol.varpi[c]) * float(prog.cols.bbar[c])
        infl = np.where(ok, inf_new * v, 0.0) * float(sol.varpi[c])
        K = econ.K[us, l, y, :][np.arange(len(us)), md] * v
        b = bucket[us]
        d["cogs_labor"] += float(np.sum((sav + infl)[b == "cogs"]))
        d["cogs_compute"] += float(np.sum(infl[b == "cogs"]))
        sm_sav = float(np.sum(sav[b == "sm"]))
        d["opex"] += float(np.sum(sav[b == "ga"])) + float(np.sum(sav[b == "rnd"])) * (1 - p.finance.rd_expansion_share) \
            + sm_sav * (1 - grow_frac)
        d["opex_ga"] += float(np.sum(sav[b == "ga"]))
        d["opex_rnd"] += float(np.sum(sav[b == "rnd"])) * (1 - p.finance.rd_expansion_share)
        d["opex_sm_maint"] += sm_sav * (1 - grow_frac)
        d["grow"] += sm_sav * grow_frac + float(np.sum(sav[b == "rnd"])) * p.finance.rd_expansion_share
        d["capital"] += float(np.sum(np.where(np.isfinite(K), K, 0.0)))
    grow_spend = pt["sigma"] * S
    d_ch = -d["cogs_labor"] / S
    d_cc = d["cogs_compute"] / S
    d_a = -d["opex"] / S
    d_k = d["capital"] / S
    d_sig = d["grow"] / max(grow_spend, 1e-9)
    # pass-through, Part I round 2 (B1): the industry rate phi applies to every unit-cost saving the rivals make
    # (cost of revenue and overhead, prop:entry(d)), and the margin is computed at the post-cut price; the dollar share
    # dur (cor:ext-game-engine(a)) is reported beside it but does not enter the score
    ptr = econ.info["pass_through"]
    phi = float(ptr["phi"])
    S_unit = -(d_ch + d_cc + d_a)
    g_star = float(pt["g"])
    out = {"delta_c_h": d_ch, "delta_c_c": d_cc, "delta_a": d_a, "delta_a_GA": -d["opex_ga"] / S, "delta_a_RD": -d["opex_rnd"] / S,
           "delta_a_SM_maint": -d["opex_sm_maint"] / S, "sm_basis": pt.get("sm_basis"),
           "delta_k": d_k, "delta_sigma": d_sig, "phi": phi, "phi_elasticity": float(ptr["elasticity"]), "C0": float(ptr["C0"]),
           "unit_cost_saving": S_unit, "price_cut": phi * S_unit,
           "durable_dollar_share": float(econ.info["durable_share"]) * (1 - float(p.finance.pass_through_phi)),
           "pass_through_rule": "Part I round 2: rate phi on all unit-cost savings, margin at the post-cut price; dur is the dollar share"}
    # growth-activity savings valued as score (prop:tasks-aggregate(b)), next to their cash value (spec W3, W4)
    y_own = max(float(pt["X"]) - float(pt["k"]), 0.0)
    out["growth_saving_score_first_order"] = float(pt["sigma_star"]) * d_sig
    out["growth_saving_score_exact"] = float(F.R_star(pt["m0"], pt["G"], F.lambda_after_savings(pt["ell"], d_sig, pt["alpha"]), pt["X"], pt["k"], pt["alpha"])
                                             - F.R_star(pt["m0"], pt["G"], pt["ell"], pt["X"], pt["k"], pt["alpha"])) if y_own > 0 else 0.0
    out["growth_saving_cash"] = d["grow"] / S
    for name, X in (("rule_of_40", 1.0), ("own_weight", float(pt["X"]))):
        out[f"delta_R_{name}"] = float(F.part1_delta_R(d_ch, d_cc, d_a, d_k, g_star, p.capital.delta_K_compute,
                                                     float(pt["sigma_star"]), d_sig, X, float(pt["k"]), 0.0, float(ptr["elasticity"])))
    m0_new = (F.margin_after_passthrough(float(pt["m0"]), float(pt.get("f") or 0.0), S_unit, phi)["m0_new"]
              - p.capital.delta_K_compute * d_k)
    ell_new = float(F.lambda_after_savings(pt["ell"], d_sig, pt["alpha"]))
    out["R_star_before"] = float(F.R_star(pt["m0"], pt["G"], pt["ell"], 1.0, pt["k"], pt["alpha"]))
    out["R_star_after"] = float(F.R_star(m0_new, pt["G"], ell_new, 1.0, pt["k"] + d_k, pt["alpha"]))
    out["v0_before"] = F.gordon_v0(pt["m0"], pt["G"], pt["k"], pt["ell"], p.finance.r, pt["alpha"])
    out["v0_after"] = F.gordon_v0(m0_new, pt["G"], pt["k"] + d_k, ell_new, p.finance.r, pt["alpha"])
    out["R40_cash_before"] = float(pt["R40_cash"])
    return out


def run(input_folder, out_folder=None, regime: str | None = None, scenario: str | None = None, seed: int | None = None,
        overrides: list[str] | None = None, data_dir=None, quick: bool = False, echo=None, write: bool = True,
        n_imp: int | None = None, n_out: int | None = None, scenario_list: list[str] | None = None) -> dict:
    """Run the engine on an input folder and (if write) write the report to out_folder. Returns the result dict."""
    log = RunLog(echo)
    dd = Path(data_dir) if data_dir else find_data_dir()
    p = build_params(dd, overrides, scenario)
    seed = int(p.mc.seed if seed is None else seed)
    rng_master = np.random.default_rng(seed)
    seeds = {k: int(rng_master.integers(0, 2 ** 31 - 1)) for k in ("mc", "gsa", "spare")}
    priors = load_priors(dd)
    log("parameters and priors loaded")
    ing = ingest.ingest_folder(input_folder, priors)
    log(f"inputs read: tier {ing.tier_reached}, {len(ing.errors)} errors, {len(ing.warnings)} warnings")
    ind = industry.industry_prior(priors, ing.financials.naics)
    rate_keys = industry.apply_rates(p, ind)
    log("industry prior matched" + ("; discount rate set to the industry cost of capital" if rate_keys else ""))
    firm = impute.build_firm(ing, priors, p)
    log(f"firm built: {len(firm.units)} activity units, {len(firm.processes)} processes and workstreams")
    if scenario and scenario != "central":
        sc = scenarios.scenario_set(p, firm)
        if scenario not in sc:
            raise ConfigError(f"unknown scenario '{scenario}'; choose one of {', '.join(sc)}")
        p = scenarios.apply(p, sc[scenario]["set"], f"scenario {scenario}")
    reg_name = regime or regimes.firm_regime_name(p, firm)
    if reg_name not in regimes.REGIMES:
        raise ConfigError(f"unknown regime '{reg_name}'; choose one of {', '.join(regimes.REGIMES)}")
    econ = E.build_econ(firm, p)
    builder = PlanBuilder(econ)
    cols = builder.build()
    log(f"economics and {len(cols)} candidate plans built")
    reg = regimes.make_regime(reg_name, p, firm)
    prog = O.make_program(cols, econ, reg, p)
    sol = O.solve(prog, method="heuristic")
    log(f"plan optimized for the {reg_name} regime: {len(sol.sel)} processes")

    # scenarios, regret and multi-start polish of the plan
    workers = 1 if quick else min(2, os.cpu_count() or 1)
    names = ["central", "capability_slow", "capability_fast", "capability_plateau", "constant_hazard", "ai_native_entrant",
             "regulation_strict", "energy_shock", "quantum"] if quick else None
    if scenario_list is not None:
        names = list(scenario_list)
    scen = scenarios.run_scenarios(firm, p, reg, sol, prog, names=names, quick=True, log=log, workers=workers)
    starts = [v for k, v in scen["specs"].items() if k != "central"]
    sol2, n_better = O.improve_with_starts(prog, sol, starts)
    if n_better:
        sol = sol2
        # re-value the improved central plan in every scenario
        from .plans import column_specs
        specs = column_specs(prog.cols, sorted(sol.sel.values()))
        for nm, pg in scen["programs"].items():
            scen["values"].loc["central", nm] = O.value_of_plan(pg, specs)["value"] if nm != "central" else sol.value
        best = scen["values"].max(axis=0)
        scen["regret"] = pd.DataFrame(best.values[None, :] - scen["values"].values, index=scen["values"].index,
                                      columns=scen["values"].columns)
        scen["max_regret"] = scen["regret"].max(axis=1)
        scen["minimax_plan"] = str(scen["max_regret"].idxmin())
        scen["recommended_max_regret"] = float(scen["max_regret"]["central"])
        scen["recommended_is_minimax"] = bool(scen["minimax_plan"] == "central")
    scen["multi_start_improvements"] = n_better
    log(f"scenarios: {len(scen['values'].columns)} solved; plan improved by {n_better} multi-start runs")

    # ownership regimes side by side (the chosen regime's plan is the recommendation)
    side = {}
    for nm in regimes.REGIMES:
        r_i = regimes.make_regime(nm, p, firm)
        pg = prog if nm == reg_name else O.make_program(cols, econ, r_i, p)
        so = sol if nm == reg_name else O.solve(pg, method="heuristic", fixed_point=2)
        sp = roadmap.score_path(so, pg, econ)
        side[nm] = {"regime": r_i, "prog": pg, "sol": so, "path": sp}
    log("ownership regimes compared")

    # Monte Carlo
    mc = risk.run_monte_carlo(firm, ing, priors, p, sol, prog, econ, reg, seed=seeds["mc"], n_imp=n_imp or (12 if quick else None),
                              n_out=n_out or (100 if quick else None))
    log(f"Monte Carlo: {mc['draws']['total']} draws over data, {mc['parameters_drawn']} class b and d parameters and outcomes")
    voi = risk.value_of_information(mc["posterior"], p, ing.tier_reached)
    pilots = risk.pilot_decisions(sol, prog, econ, p)
    plan = roadmap.plan_frame(sol, prog, econ)
    w0 = roadmap.wave0(firm, p, voi)
    wv = roadmap.waves(plan, prog, econ, w0)
    util = roadmap.utilization(sol, prog)
    prod = product.analyze(firm, p, econ, reg, dd, ops_cogs_saving_share=0.0)
    S = firm.part1["S"] * econ.vf
    path_ops = roadmap.score_path(sol, prog, econ)
    rev_d = prod["revenue_delta"]["central"]
    gp_d = prod["gross_profit_delta"]["central"]
    path = roadmap.score_path(sol, prog, econ, extra_cash=gp_d - w0["cost"] * (np.arange(econ.T) == 0),
                              extra_gaap=gp_d - w0["cost"] * (np.arange(econ.T) == 0), revenue_delta=rev_d,
                              growth_delta=np.concatenate([[rev_d[0] / S[0]], np.diff(rev_d) / S[1:]]))
    path["pqc_costs"] = prog.info["pqc"]
    tco = roadmap.tco_by_wave(plan, prog, econ)
    log("roadmap, product strategy and score path built")
    ppl = people.people_plan(econ, sol, prog, p, ing)
    sec_tab = security.security_table(econ, prog, sol, p)
    queue = security.review_queue(prog, sol, p)
    fails = security.failure_modes(econ, prog, sol, p)
    icfr_tab = security.icfr_steps(econ, prog, sol)
    ceil = security.ceiling_terms(econ, prog, sol, p, fails, sec_tab)
    log("people plan, security and failure modes built")
    tornado = scenarios.theta_tornado(firm, p)
    gsa = scenarios.global_sensitivity(firm, p, sol, prog, econ, seed=seeds["gsa"], log=log) if not quick else None
    book = roadmap.playbook(econ, prog, sol, plan, wv, ppl, mc, p, ing, priors, gsa=gsa, regime_name=reg_name)
    log(f"playbook: {book['summary'].get('activity_units', 0)} activity units, {book['summary'].get('steps', 0)} steps, "
        f"{book['summary'].get('flip_keys_tested', 0)} class d keys tested one at a time")
    bps = scenarios.breakpoints(econ, prog, sol, mc["posterior"])
    svc = scenarios.should_vs_could(econ, prog, sol, p)
    front = frontier_shift(econ, sol, prog, p)
    uni_now = E.universe(econ, year=0, level=0)
    uni_3 = E.universe(econ)
    log("sensitivity, breakpoints and frontier shift computed")

    # regime-specific outputs
    reg_view = {}
    for nm, sd in side.items():
        sp = sd["path"]
        out_r = {"value": float(sd["sol"].value), "processes": len(sd["sol"].sel), "r": sd["regime"].r,
                 "horizon": sd["regime"].horizon, "terminal": sd["regime"].terminal,
                 "dip_gaap_points": sp["dip_gaap_points"], "final_uplift_cash_points": sp["final_uplift_cash_points"],
                 "first_year_launches": int(np.sum(np.asarray([sd["prog"].cols.start[c] for c in sd["sol"].sel.values()]) == 0))}
        out_r["annual_rate"] = sd["regime"].info.get("annual_rate")
        out_r["growth_weight"] = regimes.growth_weight(firm, sd["regime"], p)
        out_r["dip_budget"] = regimes.dip_ramp(sd["sol"], sd["prog"], econ, sd["regime"], p)
        out_r["capital_hurdle"] = regimes.capital_hurdle(sd["sol"], sd["prog"], econ, sd["regime"], p)
        if nm == "pe":
            out_r["returns"] = regimes.pe_returns(firm, sd["regime"], sp)
        if nm == "permanent_capital":
            out_r["returns"] = regimes.pc_returns(firm, sd["regime"], sp, p)
        if nm in ("public", "hybrid"):
            out_r["public_path"] = regimes.public_path(firm, sp, p, sd["regime"])
        reg_view[nm] = out_r
    # h_x at 0.5 as well as 1 for the PE regime (rankings can flip between them)
    if "pe" in side:
        r5 = regimes.make_regime("pe", p, firm)
        r5.info["h_x"] = 0.5
        pg5 = O.make_program(cols, econ, r5, p)
        so5 = O.solve(pg5, method="heuristic", fixed_point=2)
        reg_view["pe"]["value_hx0.5"] = float(so5.value)
        reg_view["pe"]["processes_hx0.5"] = len(so5.sel)
        reg_view["pe"]["plan_overlap_hx0.5"] = len(set(so5.sel) & set(side["pe"]["sol"].sel))
    reg_extra = {"lbo": regimes.lbo(firm, econ, side, p), "hybrids": regimes.hybrids(firm, p, side),
                 "process_ranks": regimes.process_ranks(side, econ)}
    if "permanent_capital" in side:
        reg_extra["limits"] = regimes.limits_check(firm, p, side["permanent_capital"]["regime"],
                                                   reg_view["permanent_capital"].get("returns"))
    lmap = levers.lever_map(firm, p, econ, reg_view, util, book, prod)
    det = _stakeholder_detail(econ, sol, prog, p, path)
    stake = regimes.stakeholder_values(firm, econ, det, p, reg)

    result = {
        "version": version_stamp(dd, seed, p),
        "inputs": {"tier_reached": ing.tier_reached, "tiers": ing.tiers, "issues": ing.issues, "gaps": firm.gaps},
        "firm": {"name": firm.name, "base_year": firm.base_year, "revenue": float(firm.part1["S"]), "part1": firm.part1,
                 "headcount": firm.fin.get("headcount"), "units": len(firm.units), "processes": len(firm.processes)},
        "regime": reg_name, "scenario": scenario or "central", "plan": plan, "solution": {"value": float(sol.value), "method": sol.method,
                                                                                        "history": sol.history},
        "waves": wv, "wave0": w0, "playbook": book, "lever_map": lmap, "utilization": util, "score_path": path, "score_path_operations_only": path_ops, "tco": tco,
        "universe_now": uni_now, "universe_year3": uni_3, "frontier": front, "people": ppl, "product": prod,
        "security": {"table": sec_tab, "review_queue": queue, "compliance_first_year": prog.info["first_year_compliance"],
                     "compliance_annual": prog.info["annual_compliance"], "pqc": {"cost_by_year": prog.info["pqc"],
                                                                                  "deadline": prog.info["pqc_deadline"],
                                                                                  "it_spend": prog.info["pqc_it_spend"]},
                     "ceiling": ceil, "icfr_steps": icfr_tab},
        "failure_modes": fails, "mc": mc, "voi": voi, "pilots": pilots, "scenarios": scen, "regimes": reg_view,
        "regimes_extra": reg_extra,
        "stakeholders": stake, "tornado": tornado, "gsa": gsa, "breakpoints": bps, "should_vs_could": svc,
        "params": p, "econ": econ, "prog": prog, "sol": sol, "firm_obj": firm, "ingest": ing, "priors": priors,
        "log": log,
    }
    if write and out_folder is not None:
        from .report import write_outputs
        write_outputs(result, out_folder)
        log("report written")
    result["seconds_wall"] = time.time() - log.t0
    result["seconds_cpu"] = time.process_time() - log.c0
    return result


def _stakeholder_detail(econ, sol, prog, p, path) -> dict:
    T = econ.T
    cols = prog.cols
    fte = np.zeros(T)
    sev = np.zeros(T)
    cogs = np.zeros(T)
    vend = np.zeros(T)
    for c in sol.sel.values():
        w = float(sol.varpi[c])
        fte += np.diff(np.concatenate([[0.0], cols.fte_removed[c]])) * w
        d = cols.detail[c]
        y = int(min(d["y0"], T - 1))
        sev[y] += d["C_str"] * w
        us = np.flatnonzero(econ.unit_proc == cols.proc[c])
        share = float(np.mean(econ.info["cogs"][us])) if len(us) else 0.0
        cogs += np.maximum(d["W"], 0) * share * w
        vend += float(econ.firm.units.vendor_spend.values[us].sum()) * (np.asarray(cols.modes[c]) != F.O).any() * w * \
            (np.arange(T) >= y)
    return {"fte_removed": np.maximum(fte, 0), "avg_wage_removed": float(np.median(econ.info["w"])) * p.labor.hours_per_fte,
            "severance": sev, "cogs_savings": cogs, "gaap_delta": path["gaap_delta"], "vendor_spend_removed": vend,
            "value": float(sol.value)}


def version_stamp(dd, seed: int, p) -> dict:
    """Engine version, hashes of the theory notes and parameter files, seed and platform (spec 19.1)."""
    import numpy
    import scipy
    return {"engine": "autofrontier", "engine_version": __version__, "seed": seed, "hashes": source_hashes(dd),
            "python": platform.python_version(), "numpy": numpy.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
            "params_linked": sum(1 for l in p.params_log if l.get("status") == "applied"),
            "overrides": p.overrides, "notice": REQUIRED_NOTICE}
