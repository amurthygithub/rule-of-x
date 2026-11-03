# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Report writer: report.json (every number, with provenance) and report.md (plain language), plus CSV tables.
All files go through safeio.OutputDir. Every result that depends on a class d parameter is shown as a range
(P10 to P90 over the Monte Carlo, the low and high ends of the parameter, or Sobol bounds), never as a point alone.
Tables of the plan show the planning case (class d parameters at their central scenario values) and say so."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from . import REQUIRED_NOTICE, __version__
from . import formulas as F
from .safeio import OutputDir, clean_json

DECISION_SUPPORT = ("This report is decision support, not a decision. It is produced by a model whose limits, validation "
                    "record and the decisions it leaves to people are described in MODEL_RISK.md of the engine.")

AFFECTS = {"capability": "feasibility dates, automation share, plan value", "prices": "inference spend, automation share, plan value",
           "build": "build and integration costs, payback, plan value", "readiness": "readiness levels and integration costs",
           "outsourcing": "outsourced-mode costs", "augment": "augmentation savings and quality", "review": "review costs, error rates",
           "handoff": "process value through handoffs", "eliminate": "eliminated work", "permissibility": "available universe",
           "org": "people plan: team sizes, spans, managers", "competition": "durable share of cost-of-revenue savings, should-versus-could",
           "transition": "parallel runs, stranded costs, payback, score-path dip", "program": "wave overheads and congestion",
           "success": "success probabilities and risk-adjusted value", "pilot": "pilot decisions", "decisions": "decision bandwidth and pace",
           "overrun": "cost overruns in the outcome distribution", "shocks": "leadership, vision and reorganization shocks",
           "security": "run, security and compliance costs, ceiling terms", "product": "product strategy: seat revenue at risk, migration, pricing",
           "capital": "capital charges", "regime": "regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt",
           "limits": "limits to buying growth (treadmill, deal size, series review, consumer law)", "reliability": "failure modes, autonomy, tail losses",
           "measurement": "Wave 0 scope and cost", "accounting": "GAAP path, ICFR timing, accountability floor",
           "jurisdiction": "works-council and union priors, effects bargaining", "pqc": "post-quantum migration cost",
           "finance": "valuation and the Part I mapping", "labor": "legal leads, severance floors, survivor quits, redeployment, training and change costs",
           "talent": "AI engineer wage, hiring lead and ramp, hire or contract", "location": "site wage index, O*NET transfer",
           "residency": "data-residency mechanisms, in-region premium", "constraints": "program constraints",
           "measurement_": ""}

O_NET_NOTICE = ("This report uses information from the O*NET 31.0 Database by the U.S. Department of Labor, Employment and "
                "Training Administration (USDOL/ETA), used under the CC BY 4.0 license. The engine modified it: occupations "
                "and activities were converted, aggregated to standard units of work and linked to other sources. USDOL/ETA "
                "has not approved, endorsed or tested these modifications. O*NET is a trademark of USDOL/ETA.")

MODE_LONG = {"H": "in-house", "O": "outsourced", "U": "augmented", "A": "automated", "N": "eliminated"}

DATA_SOURCES = [
    O_NET_NOTICE,
    "BLS Occupational Employment and Wage Statistics, May 2025 (U.S. Bureau of Labor Statistics; public domain): wages and staffing.",
    "SEC EDGAR XBRL filings (public): the Part I panel behind the accountability floor and margins.",
    "Anthropic Economic Index (Anthropic; data under CC BY): automation and augmentation patterns of activities.",
    "Eloundou, Manning, Mishkin and Rock, GPTs are GPTs (MIT License, copyright 2024 OpenAI): LLM exposure of occupations.",
    "Tomlinson, Jaffe, Wang, Counts and Suri, Working with AI (CC BY 4.0): AI applicability of occupations.",
    "Kwa et al. (2025), Measuring AI Ability to Complete Long Tasks, METR, arXiv:2503.14499: only fitted parameters (the 50 percent "
    "horizon, its doubling time and the logistic slope) are used, with citation. METR's run-level data has no license and is not "
    "bundled or redistributed.",
    "APQC Process Classification Framework: process category names only, with attribution to APQC (PCF is a trademark of APQC).",
    "Bending Spoons S.p.A., Form F-1 (SEC, 8 June 2026) and Form 6-K (28 October 2026), public filings: the permanent-capital "
    "presets (IRR hurdles and window, debt policy, covenant, cost of new debt). Used as one owner's disclosed policy, not as a "
    "benchmark for other owners.",
]

FAILURE_CITATIONS = [
    "Hallucination rates: Vectara (2026), Hallucination Leaderboard; Tamber et al. (2025), EMNLP Industry Track; Magesh et al. (2025), "
    "Journal of Empirical Legal Studies 22(2); Dahl et al. (2024), Journal of Legal Analysis 16(1).",
    "Reviewer catch rates and automation bias: Agarwal et al. (2023), NBER w31422; Panko (1999), JMIS 16(2); Goddard, Roudsari and Wyatt "
    "(2012), JAMIA 19(1); Parasuraman and Manzey (2010), Human Factors 52(3); Si et al. (2024), NAACL.",
    "Agentic misbehavior: Lynch et al. (2025), arXiv:2510.05179; Meinke et al. (2024), arXiv:2412.04984; Von Arx, Chan and Barnes (2025), "
    "METR; Baker et al. (2025), arXiv:2503.11926; Ruan et al. (2024), ICLR.",
    "Prompt injection: Zhan et al. (2024), Findings of ACL; Debenedetti et al. (2024), NeurIPS Datasets and Benchmarks; Zou et al. (2025), NeurIPS.",
    "Agent pipelines: Yao et al. (2025), tau-bench; Cemri et al. (2025), multi-agent failure taxonomy; Kwa et al. (2025).",
    "Common-mode failure: Chen, Zaharia and Zou (2024), Harvard Data Science Review 6(2); OpenAI (2025), Expanding on what we missed with "
    "sycophancy; Anthropic (2026), An update on recent Claude Code quality reports.",
    "Loss severity: de Fontnouvelle, Rosengren and Jordan (2007), in The Risks of Financial Institutions; IBM and Ponemon (2026), Cost of a Data Breach.",
]


# -------------------------------------------------------------------------------------------------
# Formatting (plain language; no em-dashes)
# -------------------------------------------------------------------------------------------------
def money(x, digits=1) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "n/a"
    a = abs(float(x))
    sign = "-" if x < 0 else ""
    if a >= 1e9:
        return f"{sign}${a / 1e9:,.{digits}f}B"
    if a >= 1e6:
        return f"{sign}${a / 1e6:,.{digits}f}M"
    if a >= 1e3:
        return f"{sign}${a / 1e3:,.0f}k"
    if a >= 100:
        return f"{sign}${a:,.0f}"
    return f"{sign}${a:,.2f}"


def pct(x, digits=1) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "n/a"
    return f"{100 * float(x):.{digits}f}%"


def num(x, digits=1) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "n/a"
    return f"{float(x):,.{digits}f}"


def rng(lo, hi, f=money) -> str:
    return f"{f(lo)} to {f(hi)}"


def md_table(df: pd.DataFrame, cols: list[tuple[str, str, callable]], max_rows: int = 40) -> str:
    if df is None or len(df) == 0:
        return "(none)\n"
    head = "| " + " | ".join(c[1] for c in cols) + " |"
    sep = "|" + "|".join("---" for _ in cols) + "|"
    rows = []
    for _, r in df.head(max_rows).iterrows():
        cells = []
        for key, _, f in cols:
            v = r.get(key)
            try:
                cells.append(f(v) if f else ("" if v is None else str(v)))
            except (TypeError, ValueError):
                cells.append(str(v))
        rows.append("| " + " | ".join(cells) + " |")
    more = f"\n({len(df) - max_rows} more rows in the CSV)\n" if len(df) > max_rows else ""
    return "\n".join([head, sep] + rows) + "\n" + more


def _clean_text(s: str) -> str:
    return s.replace("—", ", ").replace("–", " to ")


# -------------------------------------------------------------------------------------------------
# Recommendations
# -------------------------------------------------------------------------------------------------
def recommendations(R: dict) -> list[dict]:
    """The top recommendations, ranked by value, each with its robustness (share of the Monte Carlo draws over data
    and class b and d parameters in which it keeps a positive value) and the scenario regret of the plan."""
    plan = R["plan"]
    rob = R["mc"].get("robustness")
    out = []
    w0 = R["wave0"]
    n_meas = sum(1 for i in w0["items"] if i["item"].startswith("process mining"))
    out.append({"title": "Start with Wave 0: measure before you automate",
                "text": f"Inventory and classify the data of every system, and run process mining and time studies on {n_meas} processes where "
                        f"better data is worth more than it costs. Wave 0 costs about {money(w0['cost'])} and takes about "
                        f"{num(12 * w0['duration_years'], 0)} months.",
                "robustness": None, "source": "core prop:tasks-granularity; spec 24.9"})
    if len(plan):
        top = plan.sort_values("value", ascending=False).head(5)
        share = {}
        if rob is not None and len(rob):
            share = dict(zip(rob.process_id, rob.share_of_draws_value_positive))
        names = ", ".join(f"{r.process_name} ({money(r.value)})" for r in top.itertuples())
        robs = [share.get(r.process_id) for r in top.itertuples() if share.get(r.process_id) is not None]
        out.append({"title": "Automate the highest-value processes first, integrating their data before automating",
                    "text": f"The five largest are {names}, planning case values. "
                            f"{sum(top.integration_first)} of them raise data readiness first.",
                    "robustness": float(np.mean(robs)) if robs else None,
                    "source": "core prop:tasks-transition, prop:tasks-readiness; ext prop:ext-waves"})
    prod = R["product"]
    best = None
    for ln in prod["lines"]:
        mg = ln.get("migration", {})
        if mg.get("applicable"):
            t = mg["targets"][mg["best_target"]]
            if best is None or (t["central"]["value"] or 0) > (best[1]["central"]["value"] or 0):
                best = (ln["product_line"], t, mg["best_target"])
    if best is not None:
        line, t, k = best
        out.append({"title": f"Move {line} toward a {k.replace('_', '-')} tariff as seats compress",
                    "text": f"Migration value {rng(t['value_min'], t['value_max'])} across the scenario values of the concession, "
                            f"cost, success and seat elasticity; it pays in {pct(t['share_of_scenarios_paying'], 0)} of those scenarios.",
                    "robustness": t["share_of_scenarios_paying"], "source": "prop:prod-migrate; prop:prod-seats"})
    ppl = R["people"]["residual"]
    if ppl["apprenticeship_gap_functions"]:
        out.append({"title": "Protect the path from junior to senior work",
                    "text": f"Junior production work falls by more than half in {len(ppl['apprenticeship_gap_functions'])} functions while "
                            "review and sign-off stay senior. Keep junior roles in review rotations and training.",
                    "robustness": None, "source": "notes/modern_theory_map.md change 6"})
    return out


# -------------------------------------------------------------------------------------------------
# Assumptions: class d parameters with ranges and the outputs they affect
# -------------------------------------------------------------------------------------------------
def assumptions_table(p) -> pd.DataFrame:
    rows = []
    for r in p.table():
        if r.get("limit") and r.get("range") is None:
            neutral = p.meta(r["key"]).get("neutral_value")
            r = {**r, "range": ("off: neutral value (no limit)" if r["value"] == neutral else "set by a scenario or override")
                 + "; no sensitivity range"}
        rows.append({**r, "affects": AFFECTS.get(r["key"].split(".")[0], "")})
    return pd.DataFrame(rows)


def class_d_rows(p, gsa=None, mc=None) -> pd.DataFrame:
    t = assumptions_table(p)
    d = t[t.grounding == "d"].copy()
    corr = (mc or {}).get("param_rank_correlation", {})
    d["rank_correlation_with_value"] = d.key.map(corr)
    st = {}
    if gsa is not None and gsa.get("sobol") is not None:
        for r in gsa["sobol"]["indices"].itertuples():
            st[r.parameter] = (r.ST_plan_saving, r.ST_plan_npv5)
    d["sobol_total_index_plan_saving"] = d.key.map(lambda k: st.get(k, (None, None))[0])
    d["sobol_total_index_plan_npv5"] = d.key.map(lambda k: st.get(k, (None, None))[1])
    return d


# -------------------------------------------------------------------------------------------------
# JSON
# -------------------------------------------------------------------------------------------------
def data_quality(R: dict) -> dict:
    """How wide the plan-value range is relative to its median, and what the input tier implies (spec 2, 13)."""
    v = R["mc"]["value"]
    width = float((v["P90"] - v["P10"]) / max(abs(v["P50"]), 1e-9))
    tier = int(R["inputs"]["tier_reached"])
    if tier <= 0:
        txt = (f"only Tier 0 inputs (financial statements and a headcount) were supplied, so occupations, wages, volumes and "
               f"systems come from industry priors. Ranges are wide: the P10 to P90 range of plan value is {width:.1f} times its "
               f"median. Supplying the Tier 1 operating-cost split and the Tier 2 roster narrows them most; see the value of "
               f"information table.")
        label = "wide"
    elif tier == 1:
        txt = (f"Tier 0 and Tier 1 inputs were supplied; occupations and wages come from priors. The P10 to P90 range of plan "
               f"value is {width:.1f} times its median. The Tier 2 roster narrows it most.")
        label = "wide" if width > 1.5 else "moderate"
    else:
        txt = (f"inputs reached Tier {tier}. The P10 to P90 range of plan value is {width:.1f} times its median; the remaining "
               f"spread comes mainly from class d scenario parameters, which more firm data cannot remove.")
        label = "moderate" if width > 1.0 else "narrow"
    return {"tier": tier, "relative_width": width, "label": label, "text": txt}


def to_json(R: dict) -> dict:
    mc = R["mc"]
    p = R["params"]
    pr = R["product"]
    out = {
        "notice": REQUIRED_NOTICE, "decision_support": DECISION_SUPPORT, "version": R["version"],
        "firm": R["firm"], "regime": R["regime"], "scenario": R["scenario"], "inputs": R["inputs"],
        "data_quality": data_quality(R),
        "recommendations": recommendations(R),
        "lever_map": R.get("lever_map"),
        "playbook": {"version": (R.get("playbook") or {}).get("version"), "summary": (R.get("playbook") or {}).get("summary"),
                     "files": ["playbook_steps.csv", "playbook_activities.csv", "playbook_data_dictionary.csv"],
                     "not_computed": (R.get("playbook") or {}).get("not_computed")},
        "headline": {
            "plan_value_P10_P50_P90": [mc["value"]["P10"], mc["value"]["P50"], mc["value"]["P90"]],
            "plan_value_planning_case": R["solution"]["value"], "value_cvar95": mc["value_cvar95"],
            "prob_meet_value_target": mc["prob_meet_value_target"], "prob_loss": mc["prob_loss"],
            "processes": int(len(R["plan"])),
            "r40_cash_final_P10_P50_P90": [float(mc["r40_cash"]["P10"][-1]), float(mc["r40_cash"]["P50"][-1]), float(mc["r40_cash"]["P90"][-1])],
            "r40_gaap_final_P10_P50_P90": [float(mc["r40_gaap"]["P10"][-1]), float(mc["r40_gaap"]["P50"][-1]), float(mc["r40_gaap"]["P90"][-1])],
        },
        "plan": R["plan"], "waves": R["waves"], "utilization": R["utilization"], "score_path": R["score_path"],
        "score_path_operations_only": R["score_path_operations_only"], "tco_by_wave": R["tco"],
        "universe": {"now": {k: R["universe_now"][k] for k in ("year", "level", "shares", "V_eco", "spend_total")},
                     "year3": {k: R["universe_year3"][k] for k in ("year", "level", "shares", "V_eco", "spend_total")}},
        "frontier": R["frontier"], "people": {k: v for k, v in R["people"].items()},
        "industry_prior": R["firm_obj"].fin.get("_industry"),
        "product": {k: v for k, v in pr.items() if k not in ("revenue_delta", "gross_profit_delta")} | {
            "revenue_delta": pr["revenue_delta"], "gross_profit_delta": pr["gross_profit_delta"]},
        "security": R["security"], "failure_modes": R["failure_modes"],
        "failure_modes_common_mode": R["failure_modes"].attrs.get("common_mode") if hasattr(R["failure_modes"], "attrs") else None,
        "risk": {k: v for k, v in mc.items() if k not in ("posterior",)} | {"posterior": mc["posterior"]},
        "value_of_information": R["voi"], "pilots": R["pilots"],
        "scenarios": {k: v for k, v in R["scenarios"].items() if k not in ("programs", "solutions", "specs")},
        "regimes": R["regimes"], "regimes_extra": R.get("regimes_extra"), "stakeholders": R["stakeholders"],
        "sensitivity": {"theta_tornado": R["tornado"],
                        "global": None if R["gsa"] is None else {k: v for k, v in R["gsa"].items()}},
        "breakpoints": R["breakpoints"], "should_vs_could": R["should_vs_could"],
        "should_vs_could_game": R["should_vs_could"].attrs.get("game") if hasattr(R["should_vs_could"], "attrs") else None,
        "assumptions": {"class_d": class_d_rows(p, R["gsa"], mc), "all": assumptions_table(p),
                        "params_yaml_links": p.params_log, "overrides": p.overrides},
        "data_sources": DATA_SOURCES, "failure_mode_citations": FAILURE_CITATIONS,
        "trace": trace(R),
    }
    return clean_json(out)


def trace(R: dict) -> list[dict]:
    """Where the headline numbers come from: inputs, priors or formulas (spec: every number traceable)."""
    t = [
        {"number": "plan value P10 to P90", "source": "formula", "ref": "risk.run_monte_carlo over imputation, class b and d parameters "
         "and outcomes; core prop:tasks-transition outcome tree; ext sec:ext-shocks", "inputs": "all tiers present"},
        {"number": "plan value, planning case", "source": "formula", "ref": "optimize.solve: core eq:tasks-npv per process, ext "
         "prop:ext-waves, prop:ext-bandwidth, core prop:tasks-secreview; regime prop:reg-value"},
        {"number": "Rule-of-40 path", "source": "formula", "ref": "core prop:tasks-scorepath; prop:acct-path; product prop:prod-aggregate"},
        {"number": "unit costs by mode", "source": "formula", "ref": "core 4.1, 4.2, 4.12, 4.13 (economics.build_econ)",
         "inputs": "tier0 financials, tier1 opex, tier2 roster, tier3 systems and volumes; priors otherwise"},
        {"number": "feasibility dates", "source": "formula and prior", "ref": "ext prop:ext-feasible; METR fitted horizon (params.yaml capability_path)"},
        {"number": "people plan", "source": "formula", "ref": "ext def:ext-org, lem:ext-staffing, prop:ext-hierarchy; tier2 roster"},
        {"number": "product strategy", "source": "formula", "ref": "theory_product.tex prop:prod-price, prop:prod-seats, prop:prod-migrate, "
         "prop:prod-portfolio, prop:prod-model, prop:prod-margin, prop:prod-cannibal", "inputs": "tier3 products"},
        {"number": "failure modes", "source": "formula and prior", "ref": "core prop:tasks-halluc, prop:tasks-bias, prop:tasks-autonomy, "
         "prop:tasks-pipeline; params_reliability.yaml"},
        {"number": "regime metrics", "source": "formula", "ref": "theory_regimes.tex prop:reg-metrics, lem:reg-waterfall, prop:reg-dip, prop:reg-lbo"},
        {"number": "should versus could", "source": "formula", "ref": "cor:ext-game-engine, prop:ext-game-pd, prop:ext-game-entry"},
    ]
    return t


# -------------------------------------------------------------------------------------------------
# Markdown
# -------------------------------------------------------------------------------------------------
def to_markdown(R: dict) -> str:
    p = R["params"]
    mc = R["mc"]
    f = R["firm"]
    plan = R["plan"]
    sp = R["score_path"]
    ppl = R["people"]
    pr = R["product"]
    reg = R["regime"]
    L = []
    A = L.append
    A(f"# AI transformation plan: {f['name']}")
    A("")
    A(f"Engine autofrontier {__version__}. Ownership regime: {reg.replace('_', ' ')}. Scenario: {R['scenario']}. "
      f"Seed {R['version']['seed']}. Input tier reached: {R['inputs']['tier_reached']}.")
    A("")
    A(f"> {DECISION_SUPPORT}")
    A("")
    A("How to read the numbers. Results that depend on scenario parameters (grounding class d: no measurement exists) are given "
      "as ranges: P10 to P90 over the Monte Carlo, which draws the firm's uncertain data and every class b and d parameter over "
      "its range, or the low and high ends of the parameter. Tables of individual processes show the planning case, in which "
      "those parameters sit at their central scenario values. The assumptions section lists every class d parameter.")
    A("")
    dq = data_quality(R)
    A(f"Data quality: {dq['text']}")
    A("")
    # 1. Executive summary
    A("## 1. Executive summary")
    A("")
    v = mc["value"]
    A(f"- **Value of the plan**: {rng(v['P10'], v['P90'])} (P10 to P90; median {money(v['P50'])}). The expected value in the worst "
      f"5 percent of outcomes is {money(mc['value_cvar95'])}. Chance of a loss: {pct(mc['prob_loss'], 0)}. Chance of reaching "
      f"{pct(p.success.target_share, 0)} of the planning-case value: {pct(mc['prob_meet_value_target'], 0)}.")
    A(f"- **Scope**: {len(plan)} processes and workstreams change mode over {len(R['waves']) - 1} waves after Wave 0, affecting "
      f"about {num(plan.fte_affected.sum(), 0)} FTE and removing about {num(plan.fte_removed.sum(), 0)} FTE of work by the final "
      f"year (planning case, at today's volumes the residual organization has {num(ppl['residual']['totals']['fte_after'], 0)} FTE "
      f"of {num(ppl['residual']['totals']['fte_before'], 0)}).")
    r40c = mc["r40_cash"]
    A(f"- **Rule of 40 (cash)**: today {pct(f['part1']['R40_cash'])}; in the final plan year {rng(r40c['P10'][-1], r40c['P90'][-1], pct)} "
      f"(P10 to P90). The transition dip in the planning case is {num(sp['dip_cash_points'])} points on a cash basis and "
      f"{num(sp['dip_gaap_points'])} points on a GAAP basis, lasting {sp['dip_cash_years']} and {sp['dip_gaap_years']} years.")
    sc = R["scenarios"]
    A(f"- **Robustness**: across {len(sc['values'].columns)} scenarios the recommended plan's largest regret is "
      f"{money(sc['recommended_max_regret'])}; the minimax-regret plan is the {sc['minimax_plan'].replace('_', ' ')} plan.")
    A("")
    A("Top recommendations:")
    A("")
    for i, rcm in enumerate(recommendations(R), 1):
        rb = f" Robustness: positive in {pct(rcm['robustness'], 0)} of draws." if rcm.get("robustness") is not None else ""
        A(f"{i}. **{rcm['title']}.** {rcm['text']}{rb} (Source: {rcm['source']}.)")
    A("")
    # 2. Vision
    A("## 2. Vision: target operating model and frontier shift")
    A("")
    u0, u3 = R["universe_now"]["shares"], R["universe_year3"]["shares"]
    A(f"Share of spend that is technically feasible, permissible, preferred and economical to move to AI modes: today "
      f"{pct(u0['feasible'], 0)}, {pct(u0['permissible'], 0)}, {pct(u0['preferred'], 0)}, {pct(u0['economical'], 0)}; in plan "
      f"year 3 at the best readiness {pct(u3['feasible'], 0)}, {pct(u3['permissible'], 0)}, {pct(u3['preferred'], 0)}, "
      f"{pct(u3['economical'], 0)}. The economical universe is worth {money(R['universe_year3']['V_eco'])} a year in plan year 3 "
      f"(ext prop:ext-universe; planning case).")
    A("")
    fr = R["frontier"]
    A(f"Part I frontier shift at the end of the plan (planning case, first order, core prop:tasks-aggregate): change in "
      f"cost-of-revenue labor {pct(fr['delta_c_h'], 2)} of revenue, compute {pct(fr['delta_c_c'], 2)}, other operating cost "
      f"{pct(fr['delta_a'], 2)} (G&A {pct(fr.get('delta_a_GA', 0), 2)}, maintenance R&D {pct(fr.get('delta_a_RD', 0), 2)}, maintenance S&M {pct(fr.get('delta_a_SM_maint', 0), 2)}), capital "
      f"intensity {pct(fr['delta_k'], 2)}, growth-spend saving {pct(fr['delta_sigma'], 1)} (worth {num(100 * fr.get('growth_saving_score_exact', 0), 2)} "
      f"points of score at the firm's weight, exact, against {pct(fr.get('growth_saving_cash', 0), 2)} of revenue in cash); "
      f"industry pass-through rate {pct(fr['phi'], 0)} on every unit-cost saving the rivals make, margins at the post-cut price "
      f"(Part I round 2: elasticity {num(fr.get('phi_elasticity', float('nan')), 2)} at today's unit cost of {pct(fr.get('C0', float('nan')), 0)} "
      f"of price; the firm's dollar share of a replicated saving, {pct(fr.get('durable_dollar_share', float('nan')), 0)}, "
      f"cor:ext-game-engine(a), values the plan in dollars and does not enter the score). Change in the Rule-of-40 "
      f"score R*: {num(100 * fr['delta_R_rule_of_40'])} points; at the firm's own growth weight: {num(100 * fr['delta_R_own_weight'])} points. "
      f"R* moves from {pct(fr['R_star_before'])} to {pct(fr['R_star_after'])}.")
    A("")
    ceil = R["security"]["ceiling"]
    A(f"Full-automation ceiling with run costs (spec 22): maintenance {pct(ceil['c_mnt'], 2)}, security {pct(ceil['c_sec'], 2)}, "
      f"ancillary {pct(ceil['c_anc'], 2)} and the error floor {pct(ceil['c_err'], 2)} of revenue; accountability floor a_min "
      f"{pct(ceil['a_min_used'], 2)} (prop:acct-amin for financial-reporting processes). Ceiling R_max "
      f"{pct(ceil['R_max_rule_of_40_basis'])} without and {pct(ceil['R_max_with_run_costs'])} with these terms, at the firm's "
      f"current compute share. At Part I's compute share at full automation for {int(ceil.get('c_c_year', 0))} "
      f"({pct(ceil.get('c_c_full_automation', float('nan')), 1)} of revenue, a scenario path) the ceiling is "
      f"{pct(ceil.get('R_max_full_automation_compute_rule_of_40_basis', float('nan')))} without and "
      f"{pct(ceil.get('R_max_full_automation_compute_with_run_costs', float('nan')))} with these terms.")
    if "c_err_no_review" in ceil:
        A(f"Without people the error floor is evaluated at the review that remains (prop:tasks-cerr(c); Part I lem:fullcost(c)): "
          f"{pct(ceil['c_err_no_review'], 2)} of revenue with no review, the ceiling's convention because the measured catch rates "
          f"are human reviewers', and {pct(ceil['c_err_ai_review'], 2)} with one AI review layer on another provider that shares the "
          f"producing model's errors with probability {num(ceil['ai_review_chi'], 2)} (a scenario value: P(the second model also "
          f"errs) is not measured; only the agreement given a joint error, 0.60, is). The expected common-mode cost of provider "
          f"events adds {pct(ceil['c_cm'], 2)} ({num(ceil['common_mode']['nu_cm'], 2)} events a year after change controls; ext "
          f"notes 4.8). With both, the ceiling without people is {pct(ceil['R_max_without_people'])} at the current compute share "
          f"and {pct(ceil['R_max_without_people_full_automation_compute'])} at Part I's.")
    am = ceil.get("accountability") or {}
    if am:
        def _dz(d):
            return ", ".join(f"{v} {k}" for k, v in (d or {}).items() if v) or "none"
        be = am.get("by_eps_bar") or {}
        dc = am.get("direct_cost") or {}

        def _be(v):
            b = v.get("breakeven") or {}
            parts = []
            if b.get("p_cc") is not None:
                parts.append(f"it stays admissible up to a cross-type common mode p_cc of {num(b['p_cc'], 5)} per opportunity")
            if b.get("human_miss") is not None:
                parts.append(f"a human miss rate on AI-missed items of {pct(b['human_miss'], 1)}")
            return (" (" + " and ".join(parts) + ")") if parts else ""
        A(f"Accountability floor as an ICFR constraint (prop:acct-amin, def:acct-admissible; Part I prop:amin): a control design is "
          f"admissible only if no in-scope objective is left with more than a remote chance a year of a material misstatement that "
          f"is not prevented or detected ({num(am['N_o'], 0)} opportunities a year). No standard sets the remote threshold, and it "
          f"has no central value here: the floor is shown at 1% and at 5% a year. "
          + " ".join((f"At {pct(float(e), 0)} the cheapest admissible design is {_dz(v.get('design'))} layers"
                      + f" ({pct(v['annual_miss_probability'], 1)} a year){_be(v)}"
                      + (f"; human layers alone: {_dz(v.get('human_only_design'))}" if v.get("human_only_admissible")
                         else "; no human-only design is admissible")
                      + (f"; residual expected consequence {money(v['residual_expected_consequence'])} a year"
                         if v.get("residual_expected_consequence") is not None else "") + ".") if v.get("admissible") else
                     (f"At {pct(float(e), 0)} no design with the available layer types is admissible: each type's common-mode "
                      f"floor alone exceeds the threshold, so only another layer type or better ITGCs would help (with the "
                      f"illustrative layer parameters; the firm's own control-testing evidence replaces them).")
                     for e, v in be.items())
          + (f" The designs are conditional on the illustrative layer parameters. The direct cost common to every design is "
             f"{money(dc.get('central'))} a year ({pct(dc.get('central_share'), 2)} of revenue: the KPMG 2025 SOX program budget of "
             f"the firm's revenue class, {money(dc.get('sox_program'))}, plus the accelerated-filer average audit fee, "
             f"{money(dc.get('audit_fee'))}); {pct(dc.get('low_share'), 2)} with the S&P 500 fee ratio and "
             f"{pct(dc.get('high_share'), 2)} with the large-accelerated-filer fee." if dc else "")
          + f" The single-number ceiling below uses the {pct(am['eps_bar'], 0)} design (a setting, not a central value)."
          + " The residual expected consequence of a material misstatement is reported, not traded against cost; a cheaper "
            "inadmissible design is a material weakness, not an option.")
    A("")
    lm = R.get("lever_map") or {}
    if lm.get("regimes"):
        st = lm["state"]
        A("### Levers by position and setup")
        A("")
        A(f"Position (lem:playbook-calib, {st['source']}): growth {pct(st['g'])}, growth spend {pct(st['sigma'])} "
          f"({st.get('sm_basis', 'netted')} S&M basis; maintenance S&M {pct(st.get('a_SM', 0.0))}), G&A "
          f"{pct(st['a_GA'])}, maintenance R&D {pct(st['a_RD'])}, cost-of-revenue labor {pct(st['c_h'])}; calibrated weight "
          f"X_hat {num(st['X_hat'], 1)}, zero-spend growth G_i {pct(st['G_i'])}, demand pull ell {num(st['ell'], 3)}. Each lever is "
          f"valued at a common {pct(lm['proportion'], 0)} change in its line (prop:playbook-rank(a)), in points of the owner's score:")
        A("")
        A("| regime | X_o | growth engine | demand pull | G&A | maintenance R&D | cost of revenue | 1 point of retention (other scale) | X_dagger_0 vs G&A (distance) | levers excluded |")
        A("|---|---|---|---|---|---|---|---|---|---|")
        for nm, o in lm["regimes"].items():
            if not o.get("applicable"):
                A(f"| {nm.replace('_', ' ')} | {num(o['X_o'], 2)} | | | | | | | | {o.get('note', '')} |")
                continue
            lv, th = o["levers"], o["thresholds"]["overhead"]
            A(f"| {nm.replace('_', ' ')} | {num(o['X_o'], 2)} | {num(100 * lv['growth_automation_exact'], 2)} | "
              f"{num(100 * lv['demand_pull_exact'], 2)} | {num(100 * lv['overhead'], 2)} | {num(100 * lv['engineering'], 2)} | "
              f"{num(100 * lv['cost_of_revenue_replicable'], 2)} | {num(100 * lv['retention_point'], 2)} | {num(th['X_dagger_0'], 2)} "
              f"({num(th['distance_X_dagger_0'], 2)}) | {len(o['excluded'])} |")
        A("")
        sb = lm.get("sm_basis_bounds") or {}
        if sb:
            yn = lambda b: "ahead of" if sb[b]["growth_engine_ahead_of_overhead_at_revealed_weight"] else "not ahead of"
            A(f"Growth-spend basis (Paper 1, author decisions 4 and 7): {sb.get('central', 'netted')} is central. On the "
              f"maintenance-netted basis only S&M above a maintenance base of {pct(sb['maint_base'])} buys growth: growth spend "
              f"is {pct(sb['netted']['sigma'])} of revenue and the maintenance share of S&M, {pct(sb['maintenance_sm'])}, is a cost "
              f"line like overhead. At the weight the firm's own spending reveals the growth engine is {yn('netted')} G&A on "
              f"that basis; on the bounds it is {yn('all')} G&A if all S&M buys growth ({pct(sb['all']['sigma'])}) and "
              f"{yn('none')} it if none does.")
            A("")
        bp, bs = lm["binding_position"], lm["binding_setup"]
        A(f"Binding constraint. Position: {bp.get('line') or bp.get('note')}"
          + (f", the line with the largest gap to the top decile of operating margin among firms growing {bp['band']} (Paper 1 Table tab:gap)" if bp.get("line") else "")
          + f". Setup: {bs.get('capacity') or 'no capacity'} is the scarcest capacity in the first plan year"
          + (f" ({pct(bs['capacity_use'], 0)} used)" if bs.get("capacity_use") is not None else "")
          + (f", and {bs['gate']} is the gate that binds automation across the most in-house hours." if bs.get("gate") else "."))
        A("")
        A("The ranking compares only the four levers valued at the same proportion (growth engine, G&A, maintenance R&D, cost of "
          "revenue; prop:playbook-rank(b)); demand pull values the growth engine another way, and a point of retention is on "
          "another scale. Durability: G&A, maintenance R&D, retention and cost of revenue at given demand raise the long-run score; both growth-engine "
          "values vanish as the firm's share approaches its ceiling. The excluded levers and their rules are in report.json (lever_map).")
        A("")
        oc = lm.get("own_compute") or {}
        if oc:
            A(f"Owning compute rather than renting it (Part I rem:owncompute) raises the cash ceiling only if the vendor's markup "
              f"exceeds {pct(oc['markup_threshold'], 1)} at market growth {pct(oc['G'])} (capital {num(oc['k_c'], 1)} per dollar a year "
              f"of compute, servers' tax deductibility psi {num(oc['psi'], 2)}); at psi = 0 the bar would be {pct(oc['markup_threshold_psi0'], 1)}.")
            A("")
        xl = lm.get("x_levels") or {}
        if xl.get("rows"):
            A(f"The weight on growth is not identified by the data (Paper 1 decision D-1), so recommendations that depend on its level "
              f"are shown at X = {', '.join(num(v, 1) for v in xl['points'])} ({xl['basis']}):")
            A("")
            A("| X | top lever | growth engine above G&A | largest price per $ of acquired revenue (full charge / annuity / user cost) |"
              + (" firm's acquisition price raises the score |" if xl.get("k_acq") is not None else ""))
            A("|---|---|---|---|" + ("---|" if xl.get("k_acq") is not None else ""))
            for rw in xl["rows"]:
                ab = rw["acquisition_price_bounds"]
                A(f"| {num(rw['X'], 1)} | {str(rw['top_lever']).replace('_', ' ')} | {'yes' if rw['growth_engine_beats_overhead'] else 'no'} | "
                  f"{num(ab['full_charge'], 2)} / {num(ab['annuity'], 2)} / {num(ab['user_cost'], 2)} |"
                  + (f" {'yes' if rw.get('acquisition_raises_score_full_charge') else 'no'} (full charge) |" if xl.get("k_acq") is not None else ""))
            A("")
            A(("Sign flips between the points: " + "; ".join(f"{f['rule']} changes between X = {num(x['between'][0], 1)} and "
                                                            f"{num(x['between'][1], 1)}" for f in xl["flips"] for x in f["flips"]) + "."
               if xl["flips"] else "No recommendation in this table changes sign between the points.")
              + (" Outside the points: " + "; ".join(f"{t['rule']} flips at X = {num(t['threshold_X'], 2)}, {t['side']}"
                                                    for t in xl["thresholds_outside_points"]) + "." if xl.get("thresholds_outside_points") else "")
              + " Ratio tests against the revealed spend weight ((X_o - k)/(X_hat - k)) do not depend on the level.")
            A("")
    # 3. Product strategy
    A("## 3. Product strategy")
    A("")
    if not pr["has_product_data"]:
        A("No product data was given (tier3_products). The band below is illustrative: one aggregate seat-priced line with the "
          "default customer exposure.")
        A("")
    for ln in pr["lines"]:
        s = ln["seats"]
        rr = s["revenue_at_risk_full"]
        A(f"**{ln['product_line']}** ({money(ln['revenue'])}, {ln['pricing_model']} pricing). Seat revenue at risk when customers "
          f"automate the seat holders' work: {rng(rr['low'], rr['high'])} at full adoption over seat elasticity "
          f"{num(s['eps_seat']['low'], 2)} to {num(s['eps_seat']['high'], 2)} and exposure {pct(s['xbar_h']['low'], 0)} to "
          f"{pct(s['xbar_h']['high'], 0)} ({s['xbar_source']}). Seat losses peak about {num(s['cases']['durables']['central']['t_peak'])} "
          f"years out with consumer-durables diffusion and {num(s['cases']['fast']['central']['t_peak'])} years with fast diffusion "
          f"(prop:prod-seats).")
        if "pricing" in ln:
            pc = ln["pricing"]
            if pc["viable"]:
                cap = "capped by AI-native entrants" if pc["capped"] else "at the monopoly capture share"
                A(f"An agent that does the work prices at {money(pc['p'], 2)} per outcome, {pct(pc['kap'], 0)} of the customer's net "
                  f"saving and {pct(pc['kap_of_cH'], 1)} of in-house cost, {cap} (prop:prod-price). Rent per outcome "
                  f"{money(pc['rent'], 2)}: data {money(pc['rent_parts']['data'], 2)}, workflow {money(pc['rent_parts']['workflow'], 2)}, "
                  f"switching {money(pc['rent_parts']['switching'], 2)}. Agent gross margin {pct(pc['agent_gross_margin'], 0)}. Under "
                  f"concentrated model supply the price is {money(ln['pricing_concentrated']['p'], 2)}.")
                if "list_price_check" in ln:
                    lc = ln["list_price_check"]
                    A(f"Vendor list prices per outcome range from {money(lc['vendor_low'], 2)} to {money(lc['vendor_high'], 2)} "
                      f"(params.yaml, list prices).")
            else:
                A("An agent for this line is not viable at the entrants' price plus rent.")
            if "cannibalization" in ln:
                cn = ln["cannibalization"]
                A(f"Cannibalization: the seat margin per unit of work is {money(cn['m_seat'], 2)}; launching now "
                  f"{'pays' if cn['launch_now'] else 'does not pay'} against an entry hazard; replacement cost "
                  f"{pct(cn['replacement_share'], 1)} of the launch gain (prop:prod-cannibal).")
            if "sourcing" in ln:
                so = ln["sourcing"]
                A(f"Model sourcing at {num(so['volume'] / 1e6, 1)}M outcomes a year: {so['choice'].replace('_', ' ')}; the own-model "
                  f"test {'passes' if so['own_model_pays_long_run'] else 'fails'} in the long run (prop:prod-model).")
        mg = ln.get("migration", {})
        if mg.get("applicable"):
            parts = []
            for k, t in mg["targets"].items():
                c = t["central"]
                when = "now" if c["T1"] == 0 else ("never" if c["T1"] is None else f"in {num(c['T1'])} years")
                parts.append(f"{k.replace('_', '-')}: threshold seat-loss rate {pct(c['nu_star'], 2)}, migrate {when}, value "
                             f"{rng(t['value_min'], t['value_max'])} (pays in {pct(t['share_of_scenarios_paying'], 0)} of scenarios)")
            A("Pricing migration (prop:prod-migrate; conditional on scenario costs): " + "; ".join(parts) + ".")
        A("")
    fe = pr["features"]
    if len(fe["features"]):
        ch = fe["features"][fe["features"].chosen]
        A(f"Feature portfolio within {num(fe['engineer_capacity'], 0)} engineer-years (prop:prod-portfolio): "
          + ", ".join(f"{r.feature} ({money(r.npv_own_weight)} at the firm's weight, {money(r.npv_screening_weight)} at the screening weight)"
                      for r in ch.itertuples()) + ".")
        if fe.get("at_eval_points"):
            A("At the growth-weight evaluation points (" + fe.get("eval_points_basis", "") + "): "
              + "; ".join(f"X = {num(a['X'], 1)}: {', '.join(a['chosen']) or 'none'}" for a in fe["at_eval_points"])
              + (". The chosen set changes between points, so the portfolio depends on the level of X." if fe.get("chosen_set_flips")
                 else ". The chosen set is the same at every point.")
              + (" The ranking of features changes between points." if fe.get("rank_flips") else ""))
    mgn = pr["margins"]
    A(f"AI product gross margins cross the subscription margin of {pct(mgn['gamma_sub'], 0)} around {int(round(mgn['crossover_fit1']))} "
      f"(fit without a cost floor) or {int(round(mgn['crossover_fit2'])) if mgn['crossover_fit2'] else 'never'} (fit with a floor); "
      "the data do not identify the pass-through (prop:prod-margin).")
    A("")
    # 4. Roadmap
    A("## 4. Roadmap and score path")
    A("")
    for w in R["waves"]:
        if w.get("wave") == 0:
            A(f"**{w['name']}** ({w['start_year']}): cost {money(w['cost'])}, {num(12 * w['duration_years'], 0)} months. "
              + "; ".join(f"{i['item']} ({i['scope']})" for i in w["items"][:6]) + (" and more" if len(w["items"]) > 6 else "") + ".")
        else:
            A(f"**{w['name']}** ({w['start_year']}): {len(w.get('processes', []))} processes ({len(w.get('integration_first', []))} "
              f"integrate data first, {len(w.get('pilots', []))} pilot first), one-time cost {money(w.get('one_time_cost'))}, dual "
              f"running {money(w.get('dual_running_per_year'))} a year while it lasts, NPV {money(w.get('npv'))}, cash payback "
              f"{num(w.get('payback_years_from_start'))} years from the wave's start, mean probability that an attempt creates some value "
              f"{pct(w.get('mean_success_probability'), 0)}. Depends on: {', '.join(w.get('depends_on', [])[:4])}"
              f"{' and more' if len(w.get('depends_on', [])) > 4 else ''}.")
    A("")
    A("Processes in the plan (planning case):")
    A("")
    A(md_table(plan, [("start_year", "start", lambda v: str(int(v))), ("process_name", "process", None),
                      ("modes_changed", "modes", lambda d: ", ".join(f"{k} {v}" for k, v in d.items())),
                      ("integration_first", "data first", lambda b: "yes" if b else "no"),
                      ("fte_removed", "FTE removed", lambda x: num(x, 0)), ("one_time_cost", "one-time cost", money),
                      ("saving_full_year", "saving a year", money), ("parallel_run_years", "parallel run (yr)", lambda x: num(x, 2)),
                      ("success_probability", "success", lambda x: pct(x, 0)), ("value", "value", money)], 30))
    A("")
    yrs = sp["years"]
    A("Rule-of-40 path (percent of revenue). Cash and GAAP, planning case, and the P10 to P90 band on a cash basis:")
    A("")
    A("| year | baseline | plan, cash | plan, GAAP | cash P10 to P90 |")
    A("|---|---|---|---|---|")
    for i, y in enumerate(yrs):
        A(f"| {y} | {pct(sp['r40_cash_base'][i])} | {pct(sp['r40_cash'][i])} | {pct(sp['r40_gaap'][i])} | "
          f"{pct(mc['r40_cash']['P10'][i])} to {pct(mc['r40_cash']['P90'][i])} |")
    A("")
    ut = R["utilization"]
    bind = [c for c, k in (("change capacity", "change_capacity_used"), ("decision bandwidth", "load_ratio")) if len(ut)]
    A(f"Constraints: change capacity is used up to {pct((ut.change_capacity_used / ut.change_capacity.replace(0, np.nan)).max(), 0)} "
      f"in its peak year; the decision load reaches {num(ut.load_ratio.max(), 2)} of bandwidth (breakpoint {num(ut.load_breakpoint.iat[0], 2)}); "
      f"security reviews peak at {num(ut.security_reviews.max(), 1)} against capacity {num(ut.review_capacity.max(), 0)} a year.")
    A("")
    bk = R.get("playbook") or {}
    if bk.get("summary"):
        sm = bk["summary"]
        A("### Playbook by process step")
        A("")
        A(f"Decisions are made per activity unit (an O*NET detailed work activity in a process step) and executed per process step: "
          f"{sm['activity_units']} activity units in {sm['steps']} steps, {num(sm['fte_now'], 0)} FTE now and {num(sm['fte_after'], 0)} "
          f"after the plan. Each row carries the mode now, in the plan and at target readiness, the binding constraint, preconditions, "
          f"go/no-go gates with their source, wave and dependencies, roles and FTE, KPIs, controls (ICFR channel and condition, ITGC "
          f"and interface lines, fallback), evidence keys with their grounding class, O*NET task statements, a confidence tier and "
          f"the firm's distance to each switch threshold (playbook_activities.csv, playbook_steps.csv; playbook_data_dictionary.csv "
          f"defines every field).")
        A("")
        A("Activity units by mode in the plan: " + ", ".join(f"{MODE_LONG.get(k, k)} {v}" for k, v in sm["mode_plan"].items())
          + ". What binds automation at target readiness: " + ", ".join(f"{k} {v}" for k, v in sm["binding_target"].items())
          + ". Confidence at target: " + ", ".join(f"tier {k} {v}" for k, v in sorted(sm["tier_target"].items()))
          + f" (def:playbook-tier. A: bound by capability, physical work or permissibility, filters the backtest supports. B: rests on "
            f"the cost crossover or a reliability gate with sourced inputs, not validated by the backtest. C: the decision to automate, "
            f"or to use AI at all, changes when one of {sm['flip_keys_tested']} class d inputs moves to an end of its range, or the "
            f"process's value is positive in fewer than {pct(p.playbook.tier_c_prob, 0)} of the Monte Carlo draws).")
        if sm.get("firm_policy_gates"):
            A("Gates use the firm's acceptance values for: " + ", ".join(sm["firm_policy_gates"]).replace("_", " ") + " (tier3_policy).")
        if sm.get("tasks_mapped") is not None:
            A(f"Firm tasks (tier3_tasks): {sm['tasks_mapped']} mapped to O*NET activities, {sm['tasks_unmapped']} not mapped "
              f"(firm_tasks_mapping.csv).")
        A("")
        st_ = bk["steps"]
        top = st_[st_.in_plan].sort_values("saving_per_year", ascending=False)
        A(md_table(top, [("process_name", "process", None), ("step", "step", lambda x: str(int(x)) if pd.notna(x) else ""),
                         ("step_name", "step name", lambda x: str(x)[:40]), ("mode_now", "now", None), ("mode_plan", "plan", None),
                         ("wave", "wave", lambda x: "" if pd.isna(x) else str(int(x))), ("binding_target", "binds today at target readiness", None),
                         ("fte_in_house", "FTE now", lambda x: num(x, 1)), ("fte_after", "FTE after", lambda x: num(x, 1)),
                         ("saving_per_year", "saving a year", money), ("tier_target", "tier", None)], 15))
        A("")
        A("Modes: H in-house, O outsourced, U augmented, A automated, N eliminated. The binding column is the first gate that "
          "fails today at the highest readiness; a step the plan automates in a later wave waits for that gate to clear "
          "(first_year_A_at_target). Cycle time is not modeled; each step's KPI says to measure it in Wave 0 (event logs or "
          "process mining, or a time study) unless a Tier 4 study gives it.")
        A("")
    # 5. People
    A("## 5. People")
    A("")
    rf = ppl["residual"]["by_function"]
    A(f"Residual organization at today's volumes (planning case): {num(ppl['residual']['totals']['fte_after'], 0)} FTE of "
      f"{num(ppl['residual']['totals']['fte_before'], 0)}. Spans widen with automation (Garicano); manager counts are shown at the "
      f"central AI span uplift of {num(p.org.span_ai_uplift, 2)} (range {num(p.range('org.span_ai_uplift')[0], 1)} to "
      f"{num(p.range('org.span_ai_uplift')[1], 1)}).")
    A("")
    A(md_table(rf, [("function_name", "function", None), ("fte_before", "FTE today", lambda x: num(x, 0)),
                    ("fte_after", "FTE after", lambda x: num(x, 0)), ("junior_after", "junior", lambda x: num(x, 0)),
                    ("senior_after", "senior", lambda x: num(x, 0)), ("review_and_signoff_fte", "review and sign-off", lambda x: num(x, 0)),
                    ("managers_before", "managers today", lambda x: num(x, 0)), ("managers_after", "managers after", lambda x: num(x, 0)),
                    ("apprenticeship_gap", "apprenticeship gap", lambda b: "yes" if b else "")], 20))
    A("")
    tm = ppl["team"]
    ratios = tm.attrs.get("ratios", {})
    lo_hi = []
    for key in ("org.e_PO", "org.e_SME", "org.l_DI", "org.l_AI", "org.N_CM", "org.e_RG"):
        r_ = p.range(key)
        lo_hi.append(f"{key.split('.')[1]} {num(r_[0], 2)} to {num(r_[1], 2)}")
    A(f"Transformation team by year (lem:ext-staffing), peak {num(tm.total.max(), 0)} FTE in {int(tm.year[tm.total.idxmax()])}. "
      f"The sizing ratios are scenario values unless the firm gave its own ({', '.join(lo_hi)}); a firm's own ratios in tier3_org "
      "replace them.")
    A("")
    A(md_table(tm, [("year", "year", lambda v: str(int(v))), ("ai_agent_engineers", "AI engineers", lambda x: num(x, 1)),
                    ("data_integration_engineers", "data engineers", lambda x: num(x, 1)), ("process_owners", "process owners", lambda x: num(x, 1)),
                    ("change_managers", "change managers", lambda x: num(x, 1)), ("domain_smes", "domain experts", lambda x: num(x, 1)),
                    ("risk_governance_audit", "risk and audit", lambda x: num(x, 1)), ("security_reviewers", "security", lambda x: num(x, 1)),
                    ("total", "total", lambda x: num(x, 1))], 12))
    A("")
    sep = ppl["separations"]
    js = ppl["jurisdiction"]
    A("### Labor law, survivors and talent (theory_labor)")
    A("")
    A(f"Separations net of redeployment total {num(sep.separations.sum(), 0)} over the plan, with severance of {money(sep.severance.sum())} "
      f"at {num(js.get('severance_months', 0), 1)} months of pay per displaced employee on average: at each site the larger of the "
      f"statutory floor (tab:labor-rules, at the site's tenure and age) and the negotiated plan. Legal leads (procedure start to the "
      f"earliest effective dismissal) average {num(12 * js.get('notice_years', 0), 1)} months and reach {num(12 * js.get('notice_years_max', 0), 1)} "
      f"at the slowest site; the engine starts the procedure at the decision where the law requires it (EU and UK) or where the success "
      f"probability clears the cutoff of prop:labor-lead(d), and extends the parallel run to the earliest dismissal date when that is "
      f"cheaper than idling (prop:labor-lead(e)). Rules as of {js.get('rules_as_of', 'n/a')}; source of site data: {js.get('source', 'n/a')}. "
      "These are model constraints, not legal advice.")
    eu = (R.get("firm_obj").org.get("eu_ai_act") if R.get("firm_obj") is not None else None) or {}
    if eu:
        A("")
        A(f"EU AI Act: high-risk obligations apply from {eu['annex_iii_from']} for the Annex III areas and from {eu['annex_i_from']} "
          f"for systems under Annex I ({eu['source']}). "
          + ("The firm has an EU nexus and the plan runs past the Annex III date, so staffing and other Annex III activities on "
             "personal data are treated as high risk (oversight floor and regulated build effort)." if eu.get("applies") else
             ("The firm has an EU nexus but the plan ends before the Annex III date, so no activity is treated as high risk."
              if eu.get("eu_nexus") else "The firm has no EU establishment, market or use of output in the inputs (Art. 2), so no "
              "activity is treated as high risk.")))
    A("")
    sites = ppl.get("sites")
    if sites is not None and len(sites):
        A(md_table(sites, [("site", "site", None), ("country", "country", None), ("headcount", "headcount", lambda x: num(x, 0)),
                           ("rule", "rule", None), ("T_leg", "lead (months)", lambda x: num(12 * x, 1)),
                           ("T_tech", "technology consultation (months)", lambda x: num(12 * x, 1)),
                           ("floor_months", "statutory floor (months)", lambda x: num(x, 2)),
                           ("severance_months", "severance used (months)", lambda x: num(x, 2)),
                           ("residency_status", "personal data for AI", None)], 30))
        A("")
    nts = ppl.get("notices") or []
    n_coll = sum(1 for n in nts if n.get("collective_procedure"))
    diff = sum(1 for n in nts if n.get("prior_test_differs"))
    A(f"With the planned separations, a collective procedure is triggered at {n_coll} site-years (all program dismissals at a site in "
      f"a window counted together; sub-threshold pacing is {'on' if p.labor.sub_threshold_pacing else 'off'}). "
      + (f"At {diff} site-years the trigger test differs from the prior test used while the plan was built; the leads there are "
         "approximate." if diff else ""))
    A("")
    unv = ppl.get("unverified_rules") or []
    if unv:
        A("Rules used here that could not be confirmed at a primary source (flagged as unverified): " + "; ".join(unv) + ".")
        A("")
    sv = ppl.get("survivors") or {}
    if sv:
        A(f"Survivors (prop:labor-survivor): each announced wave adds about {pct(p.labor.survivor_excess_quits, 2)} quits among the "
          f"remaining staff of the functions it touches (Sajjadiani et al. 2023, class b), {num(float(np.sum(sv['extra_quits_by_year'])), 1)} "
          f"extra quits over the plan, each costing {num(p.labor.c_rep, 2)} years of wages; they are backfilled in the hiring plan, and the "
          f"per-wave charge O_s = {money(R['prog'].info.get('O_s', 0.0))} enters the wave optimizer. "
          + (f"The redeployment share {pct(ppl['redeployment']['u_d'], 0)} exceeds the vacancy bound of prop:labor-survivor(e) "
             f"({pct(ppl['redeployment']['cap'], 0)}), so fewer people can be redeployed than assumed." if ppl.get("redeployment", {}).get("binds")
             else f"The redeployment share {pct(ppl.get('redeployment', {}).get('u_d', 0), 0)} is within the vacancy bound "
                  f"({pct(min(ppl.get('redeployment', {}).get('cap', 1), 1), 0)})."))
        A("")
    tal = ppl.get("talent") or {}
    if tal:
        ceil = tal["ceiling_processes"]
        A(f"Engineering talent (prop:labor-talent): loaded AI engineer cost {money(tal['w_AI'])} a year (OEWS median for software developers "
          f"with the {pct(tal['premium'], 0)} AI premium of Alekseeva et al. 2021 and payroll loading). With {num(tal['Gamma0'], 0)} engineers "
          f"today and {num(tal['hires_per_year'], 1)} hires a year after a {num(12 * tal['hiring_lead_years'], 0)}-month lead, the firm can "
          f"sustain at most {num(ceil, 0) if np.isfinite(ceil) else 'unbounded'} automated processes in run mode at "
          f"{num(tal['e_mnt'], 2)} engineers each (assumptions register row 14, class b); bringing the plan's {tal['processes_automated']} "
          f"automated processes into run mode takes {num(tal['time_to_scope_years'], 1) if np.isfinite(tal['time_to_scope_years']) else 'longer than the plan allows'} "
          f"years. " + (f"The largest staffing gap, {num(float(np.max(tal['gap_by_year'])), 1)} FTE, lasts {num(tal['gap_years'], 0)} years: "
                        f"{'contract' if tal['contract'] else 'hire'} (contracting pays for gaps shorter than {num(tal['contract_threshold_years'], 1)} years)."
                        if float(np.max(tal['gap_by_year'])) > 0 else "Hiring keeps pace with the team plan."))
        A("")
    pc = ppl.get("pace") or {}
    if pc.get("bounds"):
        A("Pace (cor:labor-pace): the program cannot finish faster than " + ", ".join(
            f"{k} {num(v, 1) if np.isfinite(v) else 'unbounded'} years" for k, v in pc["bounds"].items())
          + f"; the binding constraint is {pc['binding']}.")
        A("")
    st = ppl.get("streams") or []
    split = [x for x in st if len(x["streams"]) > 1]
    if split:
        A("Cutover streams (prop:labor-lead(b)): " + "; ".join(
            f"wave {x['plan_year'] + 1}: " + " then ".join("(" + ", ".join(g) + f") at {num(12 * t, 1)} months" for g, t in zip(x["streams"], x["cutover_years"]))
            for x in split) + ". Faster jurisdictions cut over in their own stream when their forgone savings exceed the wave overhead.")
        A("")
    loc = ppl.get("location")
    if loc is not None and len(loc) and (loc.wage_index < 0.999).any():
        A("Location (lem:labor-location): at a site with wage index w, automation pays at least ln(1/w)/delta_pi years later than in the "
          "U.S.: " + ", ".join(f"{r.site} {num(r.adoption_lag_lower_bound_years, 1)} years (w {num(r.wage_index, 2)}, {r.wage_index_source})"
                               for r in loc.itertuples() if r.wage_index < 0.999) + ".")
        A("")
    if js.get("residency_share", 0) > 0:
        A(f"Data residency (prop:labor-residency): {pct(js['residency_share'], 0)} of staff sit where personal data cannot be sent to the "
          f"AI vendor's regions ({', '.join(p.residency.vendor_regions) if not R['firm_obj'].org.get('vendor_regions') else R['firm_obj'].org['vendor_regions']}) "
          "without a mechanism; readiness for personal-data activities there is capped at (1 - omega^res) iota. An in-region deployment, the "
          "EU-U.S. Data Privacy Framework or standard contractual clauses (tier3_org vendor_regions, vendor_dpf_certified; "
          "tier3_jurisdictions transfer_mechanism) remove the cap.")
        A("")
    if ppl.get("people_cost_confidence") == "low":
        A("People costs are low confidence for this firm: the labor share of each function's spend is the software prior, not "
          "industry-specific (notes/data_sources_nonsoftware.md Section 6). Tier 1 opex with labor lines replaces it.")
        A("")
    A(f"Hiring for AI and data roles starts {num(12 * p.talent.T_lead, 0)} months ahead (vacancy duration plus candidate notice, class b, "
      f"{num(12 * p.range('talent.T_lead')[0], 0)} to {num(12 * p.range('talent.T_lead')[1], 0)} months).")
    A("")
    # 6. Risk
    A("## 6. Risk and outcome distribution")
    A("")
    A(f"Monte Carlo: {mc['draws']['imputation']} draws of the firm's data and of {mc['parameters_drawn']} class b and d parameters, "
      f"each with {mc['draws']['outcome_per_imputation']} outcome draws (success or partial realization, correlated platform failure, "
      f"heavy-tailed overruns with tail index {num(p.overrun.tail_alpha, 1)}, leadership, vision and reorganization shocks, "
      f"misbehavior and provider events). Value P10 {money(v['P10'])}, P50 {money(v['P50'])}, P90 {money(v['P90'])}; CVaR at 95 "
      f"percent {money(mc['value_cvar95'])}. Misbehavior losses over the plan {rng(mc['misbehavior_loss']['P10'], mc['misbehavior_loss']['P90'])}; "
      f"provider (common-mode) losses {rng(mc['common_mode_loss']['P10'], mc['common_mode_loss']['P90'])}. Convergence: the mean "
      f"moved {pct(mc['convergence']['relative_change'], 1)} between half and full sample.")
    A("")
    pil = R["pilots"]
    if len(pil):
        n_pilot = int((pil.value_of_pilot > 0).sum())
        A(f"Stage gates (core prop:tasks-pilot): a revealing pilot pays for {n_pilot} of {len(pil)} processes.")
    rc = mc.get("param_rank_correlation", {})
    if rc:
        A("Parameters most associated with the plan's value across draws (rank correlation): "
          + ", ".join(f"{k} ({num(v, 2)})" for k, v in list(rc.items())[:6]) + ".")
    A("")
    # 7. Failure modes
    A("## 7. AI failure modes and controls")
    A("")
    fm = R["failure_modes"]
    cm = fm.attrs.get("common_mode", {}) if hasattr(fm, "attrs") else {}
    A("By process, planning case (core prop:tasks-halluc, prop:tasks-bias, prop:tasks-autonomy, prop:tasks-pipeline). Hallucination, "
      "catch rates and misbehavior rates come from data/tasks/params_reliability.yaml; scenario-only reliability parameters are "
      "drawn over their ranges in the risk section.")
    A("")
    A(md_table(fm, [("process_name", "process", None), ("recommended_autonomy", "autonomy", None),
                    ("review_share", "review share", lambda x: pct(x, 0)), ("undetected_error_rate", "undetected errors", lambda x: pct(x, 2)),
                    ("expected_misbehavior_loss_per_year", "expected misbehavior loss a year", money),
                    ("event_cvar", "tail loss per event (CVaR)", money), ("required_controls", "required controls", None)], 25))
    A("")
    A(f"Provider concentration: {cm.get('providers', 1)} model provider(s), HHI {num(cm.get('hhi', 1), 2)}. A provider event "
      f"(about {num(cm.get('provider_events_per_year', 0), 1)} a year) degrades about {pct(cm.get('share_of_requests_degraded', 0), 0)} "
      f"of requests for about {num(cm.get('regression_days', 0), 0)} days in every process on that provider at once; a second "
      f"provider costs about {money(cm.get('diversity_cost_per_process', 0))} a process a year and narrows the loss distribution.")
    A("")
    A("Sources: " + " ".join(FAILURE_CITATIONS))
    A("")
    # 8. Regimes
    A("## 8. Ownership-regime view")
    A("")
    A("Each regime values the same candidate plans with its own rate (continuous), horizon, terminal rule and constraints "
      "(theory_regimes.tex). Side by side:")
    A("")
    rv = R["regimes"]
    A("| regime | rate (annual) | horizon | plan value | processes | first-year launches | GAAP dip (points) | growth weight X |")
    A("|---|---|---|---|---|---|---|---|")
    for nm, o in rv.items():
        hz = "going concern" if o["horizon"] is None else f"{num(o['horizon'], 0)} years"
        A(f"| {nm.replace('_', ' ')} | {pct(o.get('annual_rate'))} | {hz} | {money(o['value'])} | {o['processes']} | "
          f"{o['first_year_launches']} | {num(o['dip_gaap_points'])} | {num(o['growth_weight'].get('X_o'), 1)} |")
    A("")
    if "pe" in rv and "returns" in rv["pe"]:
        rt = rv["pe"]["returns"]
        for hx in (0.5, 1.0):
            w_ = rt[f"with_plan_hx{hx:g}"]
            wo = rt[f"without_plan_hx{hx:g}"]
            A(f"PE at h_x = {hx:g} (share of seasoned run-rate the buyer capitalizes): MOIC {num(wo['moic'], 2)} without the plan and "
              f"{num(w_['moic'], 2)} with it; gross IRR {pct(wo['gross_irr'])} and {pct(w_['gross_irr'])}; net IRR to LPs "
              f"{pct(wo['net_irr'])} and {pct(w_['net_irr'])}.")
        A(f"Entry at {num(rt['entry_multiple'], 1)} times EBITDA (equal to the exit multiple unless the firm gave both). Peak "
          f"leverage with the plan {num(rt['max_leverage_with_plan'], 1)} times against a covenant of {num(rt['covenant'], 1)}"
          f"{' (breach)' if rt['covenant_breach'] else ''}. With h_x = 0.5 the PE plan is worth {money(rv['pe'].get('value_hx0.5'))} "
          f"({rv['pe'].get('processes_hx0.5')} processes).")
    if "public" in rv and "public_path" in rv["public"]:
        pp_ = rv["public"]["public_path"]
        A(f"Public: operating income turns accretive in {pp_.get('accretion_year') or 'no plan year'}; the largest GAAP dip is "
          f"{num(pp_['max_gaap_dip_points'])} points"
          + (f"; Rule of 40 below guidance in {', '.join(map(str, pp_['years_below_r40_guidance_gaap']))} (GAAP)" if pp_.get("years_below_r40_guidance_gaap") else "")
          + ".")
    ex = R.get("regimes_extra") or {}
    lb = ex.get("lbo", {})
    if lb.get("applicable"):
        A(f"Take-private (prop:reg-lbo): the largest premium a sponsor could pay is {pct(lb['hx1']['p_max'], 0)} at h_x = 1 and "
          f"{pct(lb['hx0.5']['p_max'], 0)} at h_x = 0.5, against a required control premium of {pct(lb['hx1']['premium_required'], 0)}.")
    pcv = (rv.get("permanent_capital") or {}).get("returns") or {}
    if pcv.get("applicable"):
        w_, wo = pcv["with_plan"], pcv["without_plan"]
        irr = lambda x: "no root" if x is None else pct(math.expm1(x))
        A("")
        A("### Permanent capital")
        A("")
        A(f"A permanent-capital owner never sells and holds internal decisions to its unlevered hurdle as a going concern "
          f"(prop:acq-pc(d)); it buys only if the method IRR (five years of free cash flow, then a terminal value at "
          f"{pct(math.expm1(pcv['r_tv']))}) clears {pct(math.expm1(pcv['hurdle_unlevered']), 0)} unlevered and "
          f"{pct(math.expm1(pcv['hurdle_levered']), 0)} levered (annual; presets from the case firm's F-1, class a). At a price of "
          f"{money(pcv['price'])} ({pcv['price_basis']}), the unlevered method IRR is {irr(wo['method_irr'])} without the plan and "
          f"{irr(w_['method_irr'])} with it; levered under the debt policy, {irr(wo['levered_irr'])} and {irr(w_['levered_irr'])}.")
        A(f"The most it can pay at the unlevered hurdle (P^max, eq:acq-pmaxbound) is {money(w_['P_max'])} with the plan, "
          f"{num(w_['P_max_ebitda_multiple'], 1)} times EBITDA and {pct(w_['P_max_share_of_V_tv'], 0)} of the value at the terminal rate "
          f"(bound {pct(w_['bound_share'], 0)}); without the plan {money(wo['P_max'])}. Debt at entry is the lower of "
          f"{pct(pcv['ltv_cap'], 0)} of the price and the debt five years of free cash flow repay at {pct(math.expm1(pcv['r_debt']))} "
          f"({money(w_['ND_0'])}, {w_['debt_binding']} binds; {num(w_['entry_leverage'], 1)} times EBITDA against a covenant of "
          f"{num(pcv['covenant'], 1)}{', breached' if w_['covenant_breach_at_entry'] else ''}). The hurdle holds if the program raises value "
          f"at the terminal rate by at least {pct(pcv['program_uplift_needed']['sufficient'], 0)} and only if by at least "
          f"{pct(pcv['program_uplift_needed']['necessary'], 0)} (the control premium); this plan raises it by {pct(pcv['program_uplift'], 0)}.")
    lim = ex.get("limits") or {}
    if lim:
        tr = lim["treadmill"]
        A("")
        A(f"Limits to buying growth (prop:acq-limits), in continuously compounded rates. Holding growth of {pct(lim['g'])} "
          f"({pct(lim.get('g_annual', lim['g']))} a year) needs acquired growth of {pct(tr['acquired_growth'])} a year, "
          + (f"growth plus organic decay {pct(tr['organic_decay'])}" if tr["organic_decay"] > 0 else
             f"growth less organic growth {pct(-tr['organic_decay'])}")
          + (f", at a cash cost of {pct(tr['cash_share_of_revenue'], 1)} of revenue" if tr.get("cash_share_of_revenue") is not None else "")
          + f"; standing still needs {pct(tr['standstill_acquired_growth'])}. Organic growth {pct(lim['g_org'])} is taken from "
          f"{lim['g_org_basis']}"
          + "".join(f"; {nm.replace('_', ' ')}: organic {pct(c['g_org'])}, acquired growth needed {pct(c['acquired_growth'])}"
                    for nm, c in (tr.get("cases") or {}).items())
          + (f"; self-financing growth without new equity is at most {pct(tr['g_max'])} against {pct(lim['g'])} wanted"
             if tr.get("g_max") is not None else "; g^max needs the price paid per dollar of acquired revenue (tier3_regime acquisition_price_to_revenue)")
          + ". Deal-size, series-review, foreign-investment and consumer-law limits "
          + (f"switched on: {', '.join(lim['limits_on'])}." if lim["limits_on"] else
             "are off: their class d parameters have no value, so each takes its neutral value until a scenario or --set gives one "
             "(the verified domain of the reference script is not used as a range)."))
        A("")
        ag = lim.get("acquired_growth") or {}
        ri_ = R["firm_obj"].regime if R.get("firm_obj") is not None else {}
        buys = any((ri_ or {}).get(k) is not None for k in ("nrr", "acquisition_price_to_revenue", "operating_cash_flow",
                                                            "acquisition_outlays", "organic_growth_reported"))
        if ag and buys:
            sc_ = ag.get("scores") or {}
            lab = {"gaap_before_interest": "GAAP, before interest", "gaap_after_interest": "GAAP, after interest",
                   "cash_after_interest": "cash, after interest paid (operating cash flow as reported)",
                   "cash_before_interest": f"cash, before interest (tax rate {pct(ag['tau'], 0)}, {ag['tau_basis']})",
                   "organic_gaap_before_interest": "organic (company-defined), GAAP, before interest",
                   "organic_gaap_after_interest": "organic (company-defined), GAAP, after interest"}
            A("Growth quality when growth is bought (Part I rem:acquired-bounds). Rule-of-40 scores computed here from the inputs; the "
              "company does not report them: " + "; ".join(f"{lab.get(k, k)} {num(100 * v, 1)}" for k, v in sc_.items()) + ".")
            if ag.get("applicable"):
                A(f"Warning: {ag['warning']}. The charged scores below are set against the margin before financing.")
                gr = ag.get("charging_grid")
                if gr:
                    nm_ = {"annuity_full_year": "level annuity, every outlay for the full year",
                           "user_cost_year_end": "user cost (r + d) on year-end decayed capital",
                           "user_cost_time_weighted": "user cost on time-weighted decayed capital",
                           "annuity_from_dates": "level annuity from each outlay's date"}
                    A(f"Charging conventions at NRR (d = -ln NRR = {pct(gr['d'], 1)}, life {num(gr['life'], 1)} years, r {pct(gr['r'], 2)}): "
                      + "; ".join(f"{nm_[k]} {num(100 * v, 1)} (double-charged against OCF after interest: "
                                  f"{num(100 * gr['scores_after_interest_double_charged'][k], 1)})" for k, v in gr["scores_before_interest"].items())
                      + f". Bounds: fully charged {num(100 * gr['fully_charged_before_interest'], 1)}, uncharged "
                      f"{num(100 * gr['uncharged_before_interest'], 1)} (before interest). Return on time-weighted acquisition capital "
                      f"before interest {pct(gr['return_on_acquisition_capital'], 1)}, after economic depreciation at d "
                      f"{pct(gr['return_after_depreciation'], 1)}, against a cost of capital of {pct(gr['r'], 2)}.")
                else:
                    A(ag.get("grid_note", ""))
            else:
                A(ag.get("note", ""))
            A("")
    st = R["stakeholders"]
    A(f"Value by stakeholder (PV over the plan): owners {money(st['owners'])}, customers {money(st['customers'])}, government "
      f"{money(st['government'])}, displaced employees {money(st['employees'])}, vendors {money(st['vendors'])}.")
    A("")
    # 9. Security
    A("## 9. Security and compliance")
    A("")
    sec = R["security"]
    q = sec["review_queue"]
    A(f"Firm-level compliance once AI is deployed: {money(sec['compliance_first_year'])} in the first year and "
      f"{money(sec['compliance_annual'])} a year after (SOC 2, ISO/IEC 42001, NIST AI RMF alignment, incident response, the AI "
      f"share of cyber insurance; certifications already held are not counted). Security-review queue at its peak: "
      f"{num(q['reviews_peak'], 1)} reviews a year against capacity {num(q['capacity'], 0)}, latency {num(365 * q['latency_years'], 0)} days "
      f"(prop:tasks-secreview).")
    pq = sec["pqc"]
    A(f"Post-quantum cryptography: migration of about {money(float(np.sum(pq['cost_by_year'])))} by {int(pq['deadline']) - 1} (NIST IR 8547: "
      "quantum-vulnerable algorithms deprecated after 2030 and disallowed after 2035); the cost is a scenario range scaled by IT spend, "
      "and it uses the same budget as the AI program.")
    A("")
    A(md_table(sec["table"], [("process_name", "process", None), ("data_class", "data class", None),
                              ("exposure_score", "exposure", lambda x: num(x, 2)), ("expected_incident_loss", "incident loss a year", money),
                              ("security_spend", "security spend", money), ("maintenance_per_year", "maintenance", money),
                              ("build_or_buy", "build or buy", None)], 20))
    A("")
    st = sec["table"]
    it = sec.get("icfr_steps")
    A("### Financial reporting (ICFR) scope and controls")
    A("")
    if it is not None and len(it):
        n_in = int((it.icfr_status == "in scope").sum())
        n_as = int((it.icfr_status == "assumed in scope").sum())
        n_out = int((it.icfr_status == "out (firm input)").sum())
        A(f"A step is in scope for internal control over financial reporting if it initiates, authorizes, records, processes or "
          f"reports a transaction or estimate that reaches the financial statements (a), reads or writes an in-scope system (b), "
          f"creates or changes an integration feeding one (c), or executes an ICFR-relevant policy (d); scope and channels come "
          f"from the data contract (class b: PCAOB AS 2201, common SOX scoping). {n_in} steps are in scope, {n_as} are assumed in "
          f"scope because no input says whether their condition holds, and {n_out} are out because the firm's inputs say the "
          "condition does not hold. Answering the conditions in tier3_org (refunds issued, CRM-to-billing integration, inventory "
          "held and so on) replaces the assumptions.")
        A("")
        show = it[it.automated_in_plan | (it.icfr_status == "assumed in scope")]
        if len(show):
            A("In-scope steps that the plan automates, and steps assumed in scope:")
            A("")
            A(md_table(show, [("process_name", "process", None), ("step", "step", lambda x: str(int(x)) if x == x else ""),
                              ("title", "activity", None), ("channel", "channel", None), ("icfr_condition", "condition", None),
                              ("icfr_status", "status", None), ("automated_in_plan", "automated", lambda b: "yes" if b else "")], 60))
            A("")
    if len(st) and "itgc_per_year" in st.columns and (st.icfr_steps_automated > 0).any():
        n_ag = int((st.icfr_steps_automated > 0).sum())
        n_fb = int(st.fallback_pays.sum())
        amin = sec.get("ceiling", {}).get("a_min_design", {}) if isinstance(sec.get("ceiling"), dict) else {}
        A(f"Where an AI agent performs in-scope steps it becomes an in-scope application ({n_ag} processes). Each carries an IT "
          f"general controls line (eq:acct-itgc): logical access for its service identities and tool permissions, change "
          f"management for model, prompt, tool and configuration changes, an ICFR retest at each forced model upgrade (every "
          f"{num(p.security.T_up, 1)} years, separate from the functional revalidation in the run costs), IT operations, and "
          f"interface controls for each integration feeding an in-scope system. Together {money(st.itgc_per_year.sum())} a year, "
          f"plus {money(st.itgc_setup.sum())} once and the design of {int(st.new_interfaces_in_scope.sum())} new interfaces. Provider "
          f"outages during the close cost {money(st.timeliness_cost_per_year.sum())} a year at the cheaper of waiting them out and a "
          f"manual fallback (prop:acct-itgc(d)); a fallback pays for {n_fb} of them. These lines also enter the accountability "
          "floor a_min, and nowhere else in the ceiling. All unit costs are class d (accounting section of the assumptions).")
        A("")
    # 10. Sensitivity
    A("## 10. Sensitivity")
    A("")
    sv = sc["values"]
    A("Scenarios (plan value of each scenario's own plan and of the recommended plan):")
    A("")
    A("| scenario | what changes | own plan | recommended plan | regret of recommended |")
    A("|---|---|---|---|---|")
    for nm in sv.columns:
        desc = sc["scenarios"].get(nm, {}).get("desc", "")
        A(f"| {nm.replace('_', ' ')} | {desc} | {money(sv.loc[nm, nm] if nm in sv.index else np.nan)} | {money(sv.loc['central', nm])} | "
          f"{money(sc['regret'].loc['central', nm])} |")
    A("")
    tor = R["tornado"]
    if len(tor):
        A("Spec 5 tornado: share of spend economical to move to AI modes at the low and high end of each tax, regulation and "
          "preference parameter: " + "; ".join(f"{r.meaning} {pct(r.share_at_low, 0)} to {pct(r.share_at_high, 0)}" for r in tor.head(6).itertuples()) + ".")
    g = R["gsa"]
    if g is not None:
        mg = g["morris_groups"]
        A("")
        A(f"Global sensitivity (spec 24.2), Morris screening over {g['parameters_screened']} class b and d parameters in "
          f"{len(mg)} groups; top groups: " + ", ".join(f"{r.factor} ({num(r.score, 2)})" for r in mg.head(4).itertuples()) + ".")
        if g.get("sobol") is not None:
            sb = g["sobol"]
            A("Sobol indices (first order and total) for the annual saving of the recommended plan and for its five-year net value "
              "after one-time build and integration costs: "
              + "; ".join(f"{r.parameter} {num(r.S1_plan_saving, 2)} and {num(r.ST_plan_saving, 2)} (net value {num(r.S1_plan_npv5, 2)} and "
                          f"{num(r.ST_plan_npv5, 2)})" for r in sb["indices"].itertuples()) + ".")
            b = sb["bounds"]["plan_saving"]
            b2 = sb["bounds"]["plan_npv5"]
            A(f"Sobol bounds over the sample (P10 to P90): annual saving {rng(b['P10'], b['P90'])}; five-year net value {rng(b2['P10'], b2['P90'])}. "
              "The integration cost per system and the convexity of the integration cost in readiness are always in this set, because "
              "they decide the sign of the paper's core transition example.")
    A("")
    # 11. Breakpoints
    A("## 11. Breakpoints")
    A("")
    bp = R["breakpoints"]
    A("Distance to the breakpoints of each automated process (core prop:tasks-breakpoints): how far the inference price could rise "
      "(as a share), how far volume could fall, the slack in reviewer detection rate before the reliability target fails, the "
      "readiness slack and the years of capability slack.")
    A("")
    A(md_table(bp, [("process_name", "process", None), ("price_breakpoint_distance", "price headroom", lambda x: pct(x, 0)),
                    ("volume_threshold_distance", "volume headroom", lambda x: pct(x, 0)),
                    ("detection_rate_slack", "detection slack", lambda x: num(x, 2)), ("readiness_slack", "readiness slack", lambda x: num(x, 2)),
                    ("capability_slack_years", "capability slack (yr)", lambda x: num(x, 1)), ("z_value", "value z-score", lambda x: num(x, 1))], 25))
    A("")
    svc = R["should_vs_could"]
    game = svc.attrs.get("game", {}) if hasattr(svc, "attrs") else {}
    A(f"Should versus could (cor:ext-game-engine): with market concentration HHI {num(game.get('hhi'), 2)} and industry pass-through "
      f"{num(game.get('phi_ind'), 2)} ({game.get('phi_ind_source', 'n/a')}), the firm keeps {pct(game.get('dur_rep'), 0)} of the dollar "
      f"value of a replicable cost-of-revenue saving, its volume gain counted (the margin share is lower than the price cut alone "
      f"implies and does not depend on HHI; the homogeneous-Cournot benchmark, pass-through {num((game.get('cournot') or {}).get('phi_ind'), 2)}, "
      f"would leave {pct((game.get('cournot') or {}).get('dur_rep'), 0)}; scenarios pass_through_0, _50 and _70 span the anchors). Labels: "
      + ", ".join(f"{k} {v}" for k, v in svc.label.value_counts().items()) + ". "
      f"Adoption is a dominant strategy for {int(svc.dominant_strategy.fillna(False).astype(bool).sum())} processes, falls in the "
      f"automation dilemma window for {int(svc.dilemma.fillna(False).astype(bool).sum())}, and is defensive against AI-native entry for "
      f"{int(svc.entry_defensive.fillna(False).astype(bool).sum())}.")
    A("")
    # 12. Confidence
    A("## 12. Confidence and data gaps")
    A("")
    tiers = R["inputs"]["tiers"]
    A(f"Input tier reached: {R['inputs']['tier_reached']}. Files used: {', '.join(tiers.get('files_present', []))}.")
    gaps = R["inputs"]["gaps"]
    if gaps:
        A(f"Gaps filled from priors ({len(gaps)}): " + "; ".join(gaps[:12]) + ("; and more (see report.json)" if len(gaps) > 12 else "") + ".")
    issues = [i for i in R["inputs"]["issues"] if i["severity"] in ("error", "warning")]
    if issues:
        A(f"Input issues ({len(issues)}): " + "; ".join(f"{i['file']}: {i['message']}" for i in issues[:8]) + ".")
    voi = R["voi"]
    if len(voi):
        A(f"Value of better data (core prop:tasks-granularity): measurement pays for {int(voi.measure.sum())} of {len(voi)} processes in the plan.")
    A(f"The width of the value range (P90 minus P10: {money(v['P90'] - v['P10'])}) reflects data gaps and scenario parameters together.")
    ind = R["firm_obj"].fin.get("_industry") or {}
    if ind.get("group"):
        A(f"Industry prior (spec 24.10): {ind['group']} (Damodaran, January 2026; crosswalk confidence {ind['confidence']}); Part I's k "
          f"{num(R['firm_obj'].fin.get('k', 0), 3)} ({R['firm_obj'].provenance.get('fin.k', 'n/a')}); discount rate "
          f"{pct(p.finance.r, 2)} continuous." + (" Flags: " + "; ".join(ind["flags"]) + "." if ind.get("flags") else ""))
    A("")
    # 13. Assumptions
    A("## 13. Assumptions")
    A("")
    d = class_d_rows(p, R["gsa"], mc)
    A(f"{len(d)} parameters are class d (free scenario parameters: no measurement exists). Every result that depends on them is "
      "reported over their range. The full list, with sources, ranges and grounding classes of all parameters, is in "
      "assumptions.csv and report.json. Class d parameters with numeric ranges:")
    A("")
    dn = d[d.range.map(lambda r: isinstance(r, (list, tuple)) and len(r) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in r))]
    A(md_table(dn, [("key", "parameter", None), ("value", "central", lambda x: num(x, 4) if isinstance(x, (int, float)) else str(x)),
                    ("range", "range", lambda r: f"{num(r[0], 4)} to {num(r[1], 4)}"), ("affects", "outputs affected", None)], 400))
    A("")
    A(f"Parameters linked to data/tasks/params.yaml: {sum(1 for l in p.params_log if l.get('status') == 'applied')}. Command-line "
      f"or scenario overrides: {len(p.overrides)}.")
    A("")
    # 14. Data sources
    A("## 14. Data sources and attributions")
    A("")
    for s_ in DATA_SOURCES:
        A(f"- {s_}")
    A("")
    A("---")
    A("")
    A(DECISION_SUPPORT)
    A("")
    A(REQUIRED_NOTICE)
    A("")
    att = getattr(R.get("priors"), "task_attribution", None)
    A(f"O*NET task statements in the playbook: {att}" if att else O_NET_NOTICE)
    A("")
    return _clean_text("\n".join(L))


# -------------------------------------------------------------------------------------------------
# Write everything
# -------------------------------------------------------------------------------------------------
def write_outputs(R: dict, out_folder) -> list[str]:
    out = OutputDir(out_folder)
    out.write_json("report.json", to_json(R))
    out.write_text("report.md", to_markdown(R))
    out.write_csv("plan.csv", R["plan"].assign(modes_changed=R["plan"].modes_changed.map(lambda d: "; ".join(f"{k} {v}" for k, v in d.items()))))
    out.write_csv("waves.csv", pd.DataFrame([{k: v for k, v in w.items() if not isinstance(v, (list, dict))} for w in R["waves"]]))
    bk = R.get("playbook") or {}
    if bk.get("steps") is not None and len(bk["steps"]):
        out.write_csv("playbook_steps.csv", bk["steps"])
        out.write_csv("playbook_activities.csv", bk["activities"])
        out.write_csv("playbook_data_dictionary.csv", bk["dictionary"])
        if bk.get("task_map") is not None and len(bk["task_map"]):
            out.write_csv("firm_tasks_mapping.csv", bk["task_map"])
    out.write_csv("utilization.csv", R["utilization"])
    sp = R["score_path"]
    out.write_csv("score_path.csv", pd.DataFrame({"year": sp["years"], "r40_cash_base": sp["r40_cash_base"], "r40_cash": sp["r40_cash"],
                                                  "r40_gaap": sp["r40_gaap"], "cash_P10": R["mc"]["r40_cash"]["P10"],
                                                  "cash_P90": R["mc"]["r40_cash"]["P90"], "gaap_P10": R["mc"]["r40_gaap"]["P10"],
                                                  "gaap_P90": R["mc"]["r40_gaap"]["P90"]}))
    out.write_csv("people_residual_by_function.csv", R["people"]["residual"]["by_function"])
    out.write_csv("people_team_by_year.csv", R["people"]["team"])
    out.write_csv("people_hiring.csv", R["people"]["hiring"])
    out.write_csv("people_separations.csv", R["people"]["separations"])
    if R["people"].get("sites") is not None and len(R["people"]["sites"]):
        out.write_csv("labor_sites.csv", R["people"]["sites"])
    if R["people"].get("trigger_tests") is not None and len(R["people"]["trigger_tests"]):
        out.write_csv("labor_trigger_tests.csv", R["people"]["trigger_tests"])
    out.write_csv("failure_modes.csv", R["failure_modes"])
    out.write_csv("security.csv", R["security"]["table"])
    if R["security"].get("icfr_steps") is not None and len(R["security"]["icfr_steps"]):
        out.write_csv("icfr_scope_steps.csv", R["security"]["icfr_steps"])
    out.write_csv("breakpoints.csv", R["breakpoints"])
    out.write_csv("should_vs_could.csv", R["should_vs_could"])
    out.write_csv("scenario_values.csv", R["scenarios"]["values"].reset_index().rename(columns={"index": "plan"}))
    out.write_csv("scenario_regret.csv", R["scenarios"]["regret"].reset_index().rename(columns={"index": "plan"}))
    out.write_csv("theta_tornado.csv", R["tornado"])
    if R["gsa"] is not None:
        out.write_csv("morris_groups.csv", R["gsa"]["morris_groups"].drop(columns=["keys"]))
        if len(R["gsa"]["morris_parameters"]):
            out.write_csv("morris_parameters.csv", R["gsa"]["morris_parameters"].drop(columns=["keys"]))
        if R["gsa"]["sobol"] is not None:
            out.write_csv("sobol.csv", R["gsa"]["sobol"]["indices"])
    out.write_csv("value_of_information.csv", R["voi"])
    out.write_csv("pilots.csv", R["pilots"])
    out.write_csv("robustness.csv", R["mc"]["robustness"])
    out.write_csv("assumptions.csv", assumptions_table(R["params"]))
    out.write_csv("class_d_parameters.csv", class_d_rows(R["params"], R["gsa"], R["mc"]))
    out.write_csv("product_features.csv", R["product"]["features"]["features"])
    from .ingest import mapping_review
    out.write_csv("mapping_review.csv", mapping_review(R["ingest"], R["priors"]))
    out.write_json("validation.json", {"issues": R["inputs"]["issues"], "tier_reached": R["inputs"]["tier_reached"]})
    out.write_text("run_log.txt", "\n".join(R["log"].lines) + "\n")
    return out.written
