# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Imputation (spec Section 9): fill missing tiers from priors and build the firm model the optimizer
uses: activity units (process steps, residual work by function and GWA, outsourced work), processes,
edges, readiness, organizational inputs and Part I's baseline parameters. Uncertainty is propagated by
Monte Carlo: `build_firm(..., rng=None)` gives the point estimate (deterministic), and
`build_firm(..., rng=Generator, structure=point)` gives a draw on the same unit structure."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from . import formulas as F
from .config import Params
from .ingest import IngestResult
from .priors import Priors

UNKNOWN_SHARE = 0.5  # share of an activity pool claimed by library steps with unknown hours (assumed)
COVERAGE_MAX = 0.9  # largest share of a function's hours of one activity that processes can claim (assumed)
SIGNOFF_GWAS = {"4.A.4.a.1", "4.A.2.b.1", "4.A.2.a.3", "4.A.4.b.6"}  # interpret, decide, evaluate compliance, advise
HIGH_REL_GWAS = {"4.A.2.a.2", "4.A.2.a.3", "4.A.3.b.6", "4.A.2.a.4"}
HR_HIGH_RISK_GWAS = {"4.A.4.c.2", "4.A.2.a.1"}  # staffing, judging people: EU AI Act Annex III employment area
ICFR_PROCESS_WORDS = ("record to report", "procure to pay", "order to cash", "payroll", "month-end close", "period close",
                      "financial close", "invoice", "billing", "expense to reimburse", "tax compliance")


# Strictness of regulated classes, most demanding first: a tie in a unit's activity classes goes to the stricter one
REGULATED_STRICTNESS = ("prohibited", "licensed", "high_risk_eu", "icfr")


def class_strictness(c: str) -> int:
    """Rank of a regulated class: prohibited 0, licensed sign-off 1, EU AI Act high-risk 2, ICFR 3, any other
    regulated class 4, none 5."""
    c = str(c or "none")
    if c in REGULATED_STRICTNESS:
        return REGULATED_STRICTNESS.index(c)
    return 5 if c == "none" else 4


def modal_regulated_class(classes, eu_nexus: bool = True) -> str:
    """The most frequent regulated class among a unit's activities; ties go to the most demanding class (licensed
    sign-off, then EU AI Act high-risk with an EU nexus, then ICFR, then any other regulated class, then none), never
    to set or alphabetical order. Without an EU nexus high_risk_eu counts as none."""
    cl = [("none" if (c == "high_risk_eu" and not eu_nexus) else str(c or "none")) for c in classes] or ["none"]
    counts = {c: cl.count(c) for c in set(cl)}
    top = max(counts.values())
    return min((c for c, n in counts.items() if n == top), key=lambda c: (class_strictness(c), c))


def eu_ai_act_nexus(ing, hc: pd.DataFrame | None) -> bool:
    """EU AI Act territorial scope (Art. 2): the deployer has an establishment in the EU, the system is placed on the
    EU market, or its output is used in the EU. From the firm's sites (tier3_jurisdictions), roster regions and the
    tier3_org eu_market input; a firm with none of them is outside the Act's high-risk obligations."""
    o = ing.org
    if getattr(o, "eu_market", None) is not None:
        return bool(float(o.eu_market) >= 0.5)
    from .formulas import EU_EEA
    j = getattr(ing, "jurisdictions", None)
    if j is not None and len(j):
        from .labor import country_code
        if any(country_code(c, s) in EU_EEA for c, s in zip(j.country.fillna(""), j.site.fillna(""))):
            return True
    if hc is not None and len(hc) and "region" in hc.columns and (hc.region.astype(str) == "EU").any():
        return True
    return False


def _year_fraction(date_text: str) -> float:
    """A calendar date 'YYYY-MM-DD' as a decimal year (2027-12-02 -> 2027.92)."""
    import datetime as _dt
    d = _dt.date.fromisoformat(str(date_text))
    start = _dt.date(d.year, 1, 1)
    return d.year + (d - start).days / ((_dt.date(d.year + 1, 1, 1) - start).days)


def eu_ai_act_high_risk_applies(eu_nexus: bool, base_year: int, horizon_years: float, p: Params) -> dict:
    """Whether the AI Act's high-risk obligations for Annex III areas reach the plan: an EU nexus (Art. 2) and a plan
    that runs past the date they apply from, 2 December 2027 under Regulation (EU) 2026/1744
    (permissibility.eu_ai_act_annex_iii_from). theory_ext.tex Assumption (ii): a plan whose horizon runs past that
    date treats such use cases as high risk (class 2; ass:ext-theta(ii))."""
    when = str(p.permissibility.eu_ai_act_annex_iii_from)
    end = float(base_year) + float(horizon_years)
    past = end > _year_fraction(when)
    return {"applies": bool(eu_nexus and past), "eu_nexus": bool(eu_nexus), "annex_iii_from": when,
            "annex_i_from": str(p.permissibility.eu_ai_act_annex_i_from), "plan_ends": end, "plan_runs_past_date": bool(past),
            "source": "Regulation (EU) 2026/1744 (recitals 40 and 46)"}


ROLE_SOCS = {"ai_engineer": "15-1252", "data_engineer": "15-1242", "data_scientist": "15-2051",
             "process_owner": "13-1111", "change_manager": "13-1111", "risk_governance": "13-1041",
             "security_reviewer": "15-1212", "program_manager": "11-9199"}


def occupation_wage_fallback(occ: pd.DataFrame) -> float:
    """Annual wage for an occupation missing from the table: the employment-weighted median of the table's medians
    (OEWS in data/tasks/occupations.csv), never a constant."""
    w = pd.to_numeric(occ.wage_median, errors="coerce")
    e = pd.to_numeric(occ.employment, errors="coerce") if "employment" in occ.columns else None
    ok = w.notna() & (e.notna() & (e > 0) if e is not None else w.notna())
    if e is not None and ok.sum() > 0:
        order = np.argsort(w[ok].values)
        cw = np.cumsum(e[ok].values[order])
        return float(w[ok].values[order][np.searchsorted(cw, cw[-1] / 2.0)])
    return float(w.median())


def role_wages(occ: pd.DataFrame, p: Params) -> tuple[dict, str]:
    """Median annual wages of the transformation roles (spec 7) from the occupations table, with its OEWS vintage;
    the AI engineer falls back to build.ai_engineer_base_wage and other roles to the table's employment-weighted
    median when their SOC is missing."""
    vint = ""
    if "oews_vintage" in occ.columns:
        v = occ.oews_vintage.dropna().astype(str).unique()
        vint = ", ".join(sorted(v))
    out, missing = {}, []
    for r, soc in ROLE_SOCS.items():
        val = occ.wage_median.get(soc) if soc in occ.index else None
        if val is None or not np.isfinite(float(val)):
            missing.append(soc)
            val = p.build.ai_engineer_base_wage if r == "ai_engineer" else occupation_wage_fallback(occ)
        out[r] = float(val)
    src = f"occupations table medians (OEWS {vint or 'vintage not recorded'})"
    if missing:
        src += f"; {', '.join(sorted(set(missing)))} missing: build.ai_engineer_base_wage or the table's employment-weighted median"
    return out, src


def _is_software(naics) -> bool:
    from .industry import is_software
    return is_software(naics)


# Conditions on in-scope steps (data contract icfr_condition) and the firm input that decides each; with no input
# the step is "assumed in scope" (flagged)
ICFR_CONDITIONS = (
    (("inventory", "scrap", "costing"), "holds_inventory", "the firm holds inventory"),
    (("crm-to-billing",), "crm_billing_integration", "a CRM-to-billing integration exists"),
    (("refund", "service credit", "credit or billing adjustment", "billing adjustment"), "issues_refunds_credits",
     "support or account teams issue refunds, credits or billing adjustments"),
    (("renewal", "subscription"), "subscription_billing", "renewals amend billing subscriptions"),
    (("new-hire", "pay rate"), "hris_feeds_payroll", "the HRIS feeds payroll"),
    (("in-scope system",), "incident_fixes_in_scope_systems", "incident fixes change data or configuration of financial systems"),
    (("percent-complete", "progress entries"), "percent_complete_revenue", "revenue is recognized over time from progress entries"),
    (("loss-contingency", "settlement"), "legal_settlements_accrued", "settlements or claims feed a loss-contingency accrual"),
)
CHANNEL_NAMES = {"process": "a: transaction or estimate", "system": "b: reads or writes an in-scope system",
                 "integration": "c: integration feeding an in-scope system", "policy": "d: ICFR-relevant policy"}


def icfr_condition_input(condition: str, fin_in, org_in) -> tuple[str, bool | None, str]:
    """The firm input that decides an ICFR condition: (key, value or None if not given, description)."""
    c = str(condition or "").lower()
    if not c:
        return "", True, ""
    for words, key, desc in ICFR_CONDITIONS:
        if any(w in c for w in words):
            if key == "holds_inventory":
                v = getattr(org_in, "holds_inventory", None)
                if v is None and getattr(fin_in, "inventory", None) is not None:
                    v = float(fin_in.inventory) > 0
            else:
                v = getattr(org_in, key, None)
            return key, (None if v is None else bool(float(v) >= 0.5)), desc
    return "other", None, c


def icfr_scope_table(pdf: pd.DataFrame, priors, ing) -> tuple[dict, dict, dict]:
    """ICFR scope by process and step (spec 24.4; class b, PCAOB AS 2201 significant accounts and relevant
    assertions, ITGCs, common SOX scoping). A step is in scope through any channel of the data contract
    (icfr_channel): a transaction or estimate (process lists), an in-scope system it reads or writes, an integration
    feeding one, or an ICFR-relevant policy. A conditional step counts only when the firm's inputs meet its condition;
    with no input it is "assumed in scope". Firm overrides win: tier3_volumes icfr_scope for a process,
    tier3_systems in_scope_system and tier3_integrations feeds_in_scope for the system and integration channels.
    Returns (scope by process, basis by process, steps by (process, activity) -> dict)."""
    sc = priors.icfr_scope if getattr(priors, "icfr_scope", None) is not None else pd.DataFrame(columns=["process_id", "icfr_scope"])
    st = priors.icfr_steps if getattr(priors, "icfr_steps", None) is not None else pd.DataFrame(columns=["process_id", "dwa_id", "icfr_step"])
    scope = dict(zip(sc.process_id.astype(str), sc.icfr_scope.astype(str)))
    basis = dict(zip(sc.process_id.astype(str), sc.icfr_basis.astype(str))) if "icfr_basis" in sc.columns else {}
    for r in pdf.itertuples(index=False):
        if str(r.process_id) not in scope and r.kind == "process":
            hit = any(k in str(r.process_name or "").lower() for k in ICFR_PROCESS_WORDS)
            scope[str(r.process_id)] = "full" if hit else "none"
            basis[str(r.process_id)] = "name match (process not in the data contract)" if hit else ""
    vols = ing.volumes if ing.volumes is not None and len(ing.volumes) else None
    if vols is not None and "icfr_scope" in vols.columns:
        for pid, v in vols.dropna(subset=["icfr_scope"]).groupby("process_id").icfr_scope.first().items():
            scope[str(pid)], basis[str(pid)] = str(v), "firm input"
    # firm system and integration flags by process
    sys_flag, int_flag = {}, {}
    if getattr(ing, "systems", None) is not None and len(ing.systems) and "in_scope_system" in ing.systems.columns:
        for r in ing.systems.dropna(subset=["in_scope_system"]).itertuples(index=False):
            if getattr(r, "process_id", None):
                sys_flag[str(r.process_id)] = sys_flag.get(str(r.process_id), False) or bool(r.in_scope_system)
    if getattr(ing, "integrations", None) is not None and len(ing.integrations):
        for r in ing.integrations.dropna(subset=["feeds_in_scope"]).itertuples(index=False):
            if getattr(r, "process_id", None):
                int_flag[str(r.process_id)] = int_flag.get(str(r.process_id), False) or bool(r.feeds_in_scope)
    steps: dict = {}
    for r in st.itertuples(index=False):
        pid, dw = str(r.process_id), str(r.dwa_id)
        ch = str(getattr(r, "icfr_channel", "") or "")
        cond = str(getattr(r, "icfr_condition", "") or "")
        on = bool(r.icfr_step)
        status, decided_by = ("in scope" if on else "out"), ""
        if scope.get(pid) == "none" and basis.get(pid) == "firm input":
            on, status, decided_by = False, "out (firm input)", "tier3_volumes icfr_scope"
        elif scope.get(pid) == "full" and basis.get(pid) == "firm input":
            on, status, decided_by = True, "in scope", "tier3_volumes icfr_scope"
        elif on and cond:
            key, val, desc = icfr_condition_input(cond, ing.financials, ing.org)
            if "system" in ch and pid in sys_flag:
                val, desc, key = sys_flag[pid], "the firm flags the process's systems", "tier3_systems in_scope_system"
            if "integration" in ch and pid in int_flag:
                val, desc, key = int_flag[pid], "the firm flags the process's integrations", "tier3_integrations feeds_in_scope"
            if val is None:
                status, decided_by = "assumed in scope", f"no input on: {desc}"
            elif val:
                status, decided_by = "in scope", f"firm input ({key})"
            else:
                on, status, decided_by = False, "out (firm input)", f"firm input ({key})"
        prev = steps.get((pid, dw))
        rec = {"on": on, "status": status, "channel": ch or ("process" if on else ""), "condition": cond,
               "decided_by": decided_by, "basis": str(getattr(r, "icfr_basis", "") or ""),
               "systems_written": str(getattr(r, "financial_system_written", "") or "")}
        if prev is None or (on and not prev["on"]):
            steps[(pid, dw)] = rec
    return scope, basis, steps


def icfr_scope(function_id: str, process_name: str, p: Params) -> bool:
    """Name-based fallback for a process absent from the ICFR scope lists (ICFR_PROCESS_WORDS). The engine's scope
    is process- and step-level (icfr_scope_table); this is used only for processes the lists do not cover."""
    nm = str(process_name or "").lower()
    return any(k in nm for k in ICFR_PROCESS_WORDS)


def severance_months(region: str, p: Params) -> float:
    """Severance months by region (params.yaml transition.severance_s_w_months; EU is the mean of the DE and FR
    anchors; other regions use transition.severance_months_other)."""
    t = p.transition
    return {"US": t.severance_months_US, "UK": t.severance_months_UK, "EU": t.severance_months_EU}.get(region, t.severance_months_other)


@dataclass
class Firm:
    name: str
    base_year: int
    fin: dict[str, Any]
    part1: dict[str, Any]
    functions: pd.DataFrame
    units: pd.DataFrame
    unit_occ: pd.DataFrame
    processes: pd.DataFrame
    edges: pd.DataFrame
    org: dict[str, Any]
    provenance: dict[str, str] = field(default_factory=dict)
    gaps: list[str] = field(default_factory=list)
    tiers: dict[str, Any] = field(default_factory=dict)
    is_draw: bool = False
    products: pd.DataFrame | None = None
    product_occupations: pd.DataFrame | None = None
    ai_features: pd.DataFrame | None = None
    security: dict[str, Any] = field(default_factory=dict)
    regime: dict[str, Any] = field(default_factory=dict)
    jurisdictions: pd.DataFrame | None = None
    staffing: pd.DataFrame | None = None        # headcount by function, occupation and region (roster or prior)
    task_map: pd.DataFrame | None = None        # firm tasks (tier3_tasks) mapped to O*NET activities


ISO_REGION = {"US": "US", "USA": "US", "GB": "UK", "UK": "UK", "IN": "IN", "PH": "PH", "CA": "CA", "MX": "LATAM", "BR": "LATAM"}
EU_CODES = {"AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT",
            "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE", "NO", "IS", "LI", "CH"}


def _region_of(country: str, site: str, priors) -> str:
    c = str(country or "").strip().upper()
    if c in ISO_REGION:
        return ISO_REGION[c]
    if c in EU_CODES:
        return "EU"
    from .ingest import wage_index
    return wage_index(f"{country} {site}", priors.locations)[1]


def jurisdiction_summary(ing, hc: pd.DataFrame, p: Params, priors, org: dict | None = None,
                         employer_headcount: float = 0.0, function_ids=()) -> tuple[dict, pd.DataFrame]:
    """Statutory terms, residency and wage index by site (labor.build; theory_labor, spec 24.5, 24.6)."""
    from . import labor as LAB
    return LAB.build(ing, hc, p, priors, org or {}, employer_headcount, list(function_ids))


def _industry_shares(priors: Priors, naics: str | None, revenue: float) -> pd.DataFrame:
    """Function shares of revenue for the firm's industry: the longest NAICS prefix match among the SEC panel rows
    (software) and the Damodaran-based rows (other industries). The pooled SEC row "51/54 software and IT services"
    serves software codes only, so legal, accounting or consulting firms (NAICS 54) do not get a software prior.
    Without a match, the Total Market (without financials) rows, then the built-in generic rows."""
    from .industry import GENERIC_GROUP, is_software
    ifs = priors.industry_function_shares.copy()
    ifs["naics_prefix"] = ifs["naics_prefix"].fillna("").astype(str)
    if "prior_basis" not in ifs.columns:
        ifs["prior_basis"], ifs["damodaran_industry"] = "builtin", ""
    band = "<100M" if revenue < 1e8 else "100M-1B" if revenue < 1e9 else "1B-10B" if revenue < 1e10 else ">10B"
    best, best_len = None, -1
    soft = is_software(naics)
    if naics:
        for key, grp in ifs.groupby(["industry", "naics_prefix"]):
            pooled = (grp.prior_basis.iat[0] == "sec_panel") and all(len(x) <= 2 for x in str(key[1]).split("/") if x)
            if pooled and not soft:
                continue
            for pre in str(key[1]).split("/"):
                if pre and str(naics).startswith(pre) and len(pre) > best_len:
                    best, best_len = key, len(pre)
    if best is None:
        g = ifs[ifs.damodaran_industry == GENERIC_GROUP]
        if len(g):
            sel, src = g, f"generic prior ({GENERIC_GROUP}, Damodaran January 2026)"
        else:
            g = ifs[ifs.industry == "generic"]
            sel = g if len(g) else ifs
            src = "generic prior (built-in)"
        out = sel.groupby("function_id", as_index=False).agg(share_mean=("share_mean", "mean"), share_sd=("share_sd", "mean"))
        out.attrs["source"] = src
        out.attrs["prior_basis"] = "generic"
        return out
    else:
        sel = ifs[(ifs.industry == best[0]) & (ifs.naics_prefix == best[1])]
        src = f"industry {best[0]} (NAICS {best[1]})"
    if "size_band" in sel.columns and (sel.size_band.astype(str) == band).any():
        sel = sel[sel.size_band.astype(str) == band]
    elif "size_band" in sel.columns and sel.size_band.astype(str).isin(["all", "any"]).any():
        sel = sel[sel.size_band.astype(str).isin(["all", "any"])]
    out = sel.groupby("function_id", as_index=False).agg(share_mean=("share_mean", "mean"), share_sd=("share_sd", "mean"))
    out.attrs["source"] = src + f", size band {band}"
    out.attrs["prior_basis"] = str(sel.prior_basis.iat[0]) if len(sel) else "builtin"
    return out


def _org_inputs(ing: IngestResult, p: Params, rng, n_functions: int) -> tuple[dict, list[str]]:
    o = ing.org
    gaps = []
    def val(name, prior, lo=None, hi=None, draw_sd=None):
        v = getattr(o, name, None)
        if v is not None:
            return float(v), "input"
        gaps.append(name)
        if rng is not None and lo is not None:
            return float(rng.uniform(lo, hi)), "prior draw"
        return float(prior), "prior"
    d = p.decisions
    layers, s1 = val("governance_layers", d.governance_layers, 2, 5)
    steps, s2 = val("approval_steps_medium", 4.0, 2, 8)
    conc, s3 = val("concurrent_initiatives", d.concurrent_initiatives, 1, 10)
    to_fte, s4 = val("transformation_office_fte", d.transformation_office_fte, 0, 6)
    team, s5 = val("team_capability", p.success.team_prior, 0.25, 0.75)
    exp_share = o.experienced_share if o.experienced_share is not None else None
    if exp_share is not None:
        team = 0.5 * team + 0.5 * float(exp_share)
    deleg, s6 = val("delegation", d.delegation, 0.0, 0.4)
    a0, b0 = p.success.past_prior_a, p.success.past_prior_b
    if o.past_transformations_attempted is not None and o.past_transformations_succeeded is not None:
        a, b = a0 + o.past_transformations_succeeded, b0 + o.past_transformations_attempted - o.past_transformations_succeeded
        past_src = "input (Beta posterior)"
    else:
        a, b = a0, b0
        gaps.append("past_transformations")
        past_src = "prior"
    past = float(rng.beta(a, b)) if rng is not None and past_src == "prior" else a / (a + b)
    sp = {}
    if ing.sponsors is not None and len(ing.sponsors):
        sp = dict(zip(ing.sponsors.function_id, ing.sponsors.engaged.astype(float)))
        sponsors = float(sum(v for v in sp.values()))
        sp_src = "input"
    else:
        sponsors = d.sponsors
        gaps.append("sponsors")
        sp_src = "prior"
    sh = p.shocks
    ten, s7 = val("sponsor_tenure_years", 2.0, 0.0, 6.0)
    kp = o.key_persons
    if kp is None:
        gaps.append("key_persons")
        kp_per_f = sh.key_persons_per_function
        kp_src = "prior"
    else:
        kp_per_f = float(kp) / max(n_functions, 1)
        kp_src = "input"
    docc = o.documentation_coverage
    cec = o.context_engine_coverage
    if docc is None and cec is None:
        gaps.append("documentation_coverage")
        cov = float(np.clip(sh.kappa_doc + rng.normal(0, 0.15), 0.0, 0.95)) if rng is not None else sh.kappa_doc
        cov_src = "prior"
    else:
        cov = max(docc or 0.0, cec or 0.0)
        cov_src = "input"
    reorgs = []
    if o.planned_reorg_years:
        for tok in str(o.planned_reorg_years).replace(",", ";").split(";"):
            tok = tok.strip()
            if tok.isdigit():
                reorgs.append(int(tok))
    return ({"layers": layers, "approval_steps": steps, "concurrent": conc, "to_fte": to_fte, "team": team,
             "sponsor_tenure": ten, "key_persons_per_function": kp_per_f, "coverage": cov, "planned_reorgs": reorgs,
             "delegation": deleg, "past_rate": past, "past_prior_mean": a0 / (a0 + b0), "sponsor_by_function": sp,
             "sponsor_prior": p.success.sponsor_prior, "sponsors": sponsors, "context_engine_coverage": cec,
             "documentation_coverage": docc,
             "sources": {"layers": s1, "approval_steps": s2, "concurrent": s3, "to_fte": s4, "team": s5,
                         "delegation": s6, "past_rate": past_src, "sponsors": sp_src, "sponsor_tenure": s7,
                         "key_persons": kp_src, "coverage": cov_src}}, gaps)


_TASK_MAP_CACHE: dict = {}
_STOP = set("a an and are as at be by for from in into is of on or the to with within using use their its".split())


def _tokens(text) -> set:
    return {w for w in re.findall(r"[a-z]+", str(text).lower()) if len(w) > 2 and w not in _STOP}


def map_firm_tasks(tasks: pd.DataFrame, priors: Priors, step_dwas: dict | None = None, min_score: float = 0.25) -> pd.DataFrame:
    """Map each firm task to an O*NET DWA (spec 29; coordinator decision 29 Oct): the dwa_id given, else the O*NET
    task statement with the highest word overlap (Jaccard on content words, at least min_score) through
    xw_task_dwa.csv, preferring the step's own activities. Unmapped tasks are flagged."""
    act_ids = set(priors.activities.dwa_id)
    ts, xw = getattr(priors, "task_statements", None), getattr(priors, "xw_task_dwa", None)
    cand = None
    if ts is not None and xw is not None:
        cand = [(int(t), _tokens(x)) for t, x in zip(ts.task_id, ts.task) if pd.notna(t)]
        t2d = xw.groupby("task_id").dwa_id.apply(list).to_dict()
        ttext = dict(zip(ts.task_id, ts.task))
    rows = []
    for r in tasks.itertuples():
        given = str(r.dwa_id).strip() if isinstance(r.dwa_id, str) and r.dwa_id.strip() else None
        out = {"firm_task": r.firm_task, "process_id": r.process_id, "step": r.step, "dwa_id_given": given, "dwa_id": None,
               "method": "unmapped", "match_score": None, "matched_task_id": None, "matched_task": None}
        if given and given in act_ids:
            out.update(dwa_id=given, method="given")
        elif cand:
            tok = _tokens(r.firm_task)
            best, bscore = None, 0.0
            for tid, tt in cand:
                if not tok or not tt:
                    continue
                sc = len(tok & tt) / len(tok | tt)
                if sc > bscore:
                    best, bscore = tid, sc
            if best is not None and bscore >= min_score:
                dws = [d for d in t2d.get(best, []) if d in act_ids]
                own = [d for d in dws if step_dwas and d in step_dwas.get((r.process_id, float(r.step)), set())]
                if dws:
                    out.update(dwa_id=(own or dws)[0], method="text match", match_score=round(bscore, 3), matched_task_id=best,
                               matched_task=ttext.get(best))
        rows.append(out)
    return pd.DataFrame(rows)


def apply_firm_tasks(pa: pd.DataFrame, tasks: pd.DataFrame, priors: Priors, proc_volume: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Replace the activity mix and hours of each process step that has mapped firm tasks: one row per mapped DWA,
    hours per unit = the sum of its tasks' hours (scaled by task volume / process volume when a volume is given)."""
    step_dwas = pa.groupby(["process_id", "step"]).dwa_id.apply(set).to_dict()
    ck = (id(tasks), id(priors))
    if ck not in _TASK_MAP_CACHE:                 # Monte Carlo draws rebuild the firm: map the tasks once
        _TASK_MAP_CACHE.clear()
        _TASK_MAP_CACHE[ck] = map_firm_tasks(tasks, priors, step_dwas)
    m = _TASK_MAP_CACHE[ck].copy()
    tk = tasks.reset_index(drop=True).assign(dwa_mapped=m.dwa_id.values)
    keep, add = pa, []
    act = priors.activities.set_index("dwa_id")
    for (pid, stp), grp in tk[tk.dwa_mapped.notna()].groupby(["process_id", "step"]):
        cur = keep[(keep.process_id == pid) & (keep.step == stp)]
        if not len(cur):
            m.loc[(m.process_id == pid) & (m.step == stp), "method"] = "unmapped (step not in the process library)"
            continue
        tmpl = cur.iloc[0].copy()
        keep = keep.drop(cur.index)
        pv = float(proc_volume.get(pid, np.nan))
        for dwa, g2 in grp.groupby("dwa_mapped"):
            scale = np.where(g2.volume.notna() & np.isfinite(pv) & (pv > 0), g2.volume / pv, 1.0) if "volume" in g2 else 1.0
            row = tmpl.copy()
            row["dwa_id"] = dwa
            if "dwa_title" in row.index:
                row["dwa_title"] = act.dwa_title.get(dwa, "")
            row["hours_per_unit"] = float(np.sum(g2.hours.values * scale))
            row["tier4"] = 1
            row["firm_tasks"] = "; ".join(map(str, g2.firm_task))
            add.append(row)
    if add:
        keep = pd.concat([keep, pd.DataFrame(add)], ignore_index=True)
    return keep, m


def retarget_units(firm, priors: Priors, p: Params) -> pd.DataFrame:
    """The units' quality target r_bar, loss multiple L_mult and readiness floor iota_min recomputed at the parameters
    p, with the same rules as build_firm (for the playbook's one-at-a-time test of the impute-level keys
    review.r_bar_high, review.L_mult_regulated, review.r_bar_licensed and readiness.iota_min_regulated_add)."""
    gattr = priors.gwa_attributes().set_index("gwa_id")
    G_ATTR = {g: r._asdict() for g, r in zip(gattr.index, gattr.itertuples(index=False))}
    G_DEFAULT = next(iter(G_ATTR.values()))
    hr = firm.functions.set_index("function_id").high_reliability.to_dict()
    U = firm.units.copy()
    rb, lm, im = [], [], []
    for gwa, fid, rc in zip(U.gwa_id, U.function_id, U.regulated_class):
        ga = G_ATTR.get(gwa, G_DEFAULT)
        r_bar, L_mult = float(ga["r_bar"]), float(ga["L_mult"])
        if hr.get(fid) and gwa in HIGH_REL_GWAS:
            r_bar = max(r_bar, p.review.r_bar_high)
            L_mult = max(L_mult, p.review.L_mult_regulated)
        if rc == "licensed":
            r_bar = max(r_bar, p.review.r_bar_licensed)
        rb.append(r_bar)
        lm.append(L_mult)
        im.append(float(ga["iota_star"]) + (p.readiness.iota_min_regulated_add if rc != "none" else 0.0))
    U["r_bar"], U["L_mult"], U["iota_min"] = rb, lm, im
    return U


def _num_or_none(x):
    """A numeric step-level override, or None when blank."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if np.isfinite(v) else None


def part1_baseline(fin: dict, p: Params, compute_cost_cogs: float, labor_cogs: float) -> dict:
    """Part I parameters from Tier 0 (spec Section 1): gamma, a, sigma, k, g, G, ell, X, and the cash
    and GAAP margins. The FCF-basis a includes maintenance capex and excludes D&A."""
    S = fin["revenue"]
    th = p.finance.rd_expansion_share
    gamma = 1.0 - fin["cogs"] / S
    # growth spend on the S&M basis (Paper 1 round 2, decisions 4 and 7: maintenance-netted central); the maintenance
    # share of S&M is a non-discretionary cost line inside a (m_cash is unchanged by the basis)
    gs = F.growth_spend_split(fin["sm"] / S, fin["rnd"] / S, th, p.finance.sm_basis, p.finance.sm_maint_base)
    sigma = gs["sigma"]
    a_gaap = (fin["ga"] + (1.0 - th) * fin["rnd"]) / S + gs["sm_maint"]
    m_op = 1.0 - (fin["cogs"] + fin["rnd"] + fin["sm"] + fin["ga"]) / S
    g = fin["g"]
    G = fin["G"]
    k = fin["k"]
    da = fin.get("da") or 0.0
    capex = fin.get("capex") or 0.0
    maint = max(capex - k * max(g, 0.0) * S, 0.0)
    a = a_gaap - da / S + maint / S
    m0 = gamma - a
    m_cash = m0 - sigma - k * g
    a_other = 0.0
    if fin.get("fcf_margin") is not None:
        # Part I's identity m0 = m + sigma + k g at the firm's reported FCF margin (synthesis theorist W17); the
        # difference from the line items is an other-operating line inside a
        m_cash = float(fin["fcf_margin"])
        m0_fcf = m_cash + sigma + k * g
        a_other = m0 - m0_fcf
        a = a + a_other
        m0 = m0_fcf
    alpha = p.finance.alpha
    # with no growth spend on the basis (netted S&M at or below the maintenance base), growth above market is not
    # explained by spend: demand pull is set at its floor rather than inverted from a zero spend
    ell = F.ell_from_growth(g, G, sigma, alpha) if sigma > 1e-6 else F.ell_from_growth(G, G, 1.0, alpha)
    X_src = "input EV/revenue multiple (revenue multiple ~ v0 at small share, Part I Prop dynamic (d))"
    X = fin.get("ev_revenue_multiple")
    v0 = F.gordon_v0(m0, G, k, ell, p.finance.r, alpha)
    if X is None:
        if v0 is not None:
            X, X_src = v0, "Part I Prop dynamic (d): small-share Gordon root v0"
        else:
            X, X_src = p.finance.X_default, ("evaluation point finance.X_default (the Gordon equation has no root at these inputs "
                                             "and no multiple was given; not an estimate: X-dependent outputs are reported at "
                                             "finance.X_eval_points)")
    tau = fin.get("tax_rate") or p.finance.tau
    c_c = compute_cost_cogs / S
    f = p.finance.fees_f
    R40_cash = g + m_cash
    R40_gaap = g + m_op
    Rs = float(F.R_star(m0, G, ell, X, k, alpha))
    return {"S": S, "gamma": gamma, "sigma": sigma, "sm_maint": gs["sm_maint"], "sm_basis": gs["basis"], "a": a, "a_gaap": a_gaap, "a_other": a_other,
            "m0_basis": "fcf_margin + sigma + k g (Part I identity)" if fin.get("fcf_margin") is not None else "line items",
            "m0": m0, "m_op": m_op, "m_cash": m_cash,
            "g": g, "G": G, "k": k, "ell": ell, "X": float(X), "X_source": X_src, "v0": v0, "tau": tau, "c_c": c_c,
            "c_h": labor_cogs / S, "f": f, "alpha": alpha, "R40_cash": R40_cash, "R40_gaap": R40_gaap, "R_star": Rs,
            "Delta_star": float(F.delta_star(ell, X - k, alpha)), "sigma_star": float(F.sigma_star(ell, X - k, alpha))}


def build_firm(ing: IngestResult, priors: Priors, p: Params, rng: np.random.Generator | None = None,
               structure: Firm | None = None) -> Firm:
    fin_in = ing.financials
    S = fin_in.revenue
    gaps: list[str] = []
    prov: dict[str, str] = {}
    mc = p.mc
    fin = fin_in.model_dump()
    fin["g"] = fin_in.revenue_growth if fin_in.revenue_growth is not None else p.finance.revenue_growth_g
    fin["G"] = fin_in.market_growth if fin_in.market_growth is not None else p.finance.market_growth_G
    from . import industry as IND
    ind = IND.industry_prior(priors, fin_in.naics)
    k_ind, k_rng, k_src = IND.k_default(ind, p)
    fin["k"] = fin_in.capital_intensity_k if fin_in.capital_intensity_k is not None else k_ind
    fin["_k_range"] = k_rng
    fin["_industry"] = ind
    for kname, src in (("g", fin_in.revenue_growth), ("G", fin_in.market_growth), ("k", fin_in.capital_intensity_k)):
        prov[f"fin.{kname}"] = "input" if src is not None else ("default (defaults.yaml finance)" if kname != "k" else k_src)
        if src is None:
            gaps.append(f"tier0.{ {'g': 'revenue_growth', 'G': 'market_growth', 'k': 'capital_intensity_k'}[kname] }")
    fin["owned_compute_share"] = fin_in.owned_compute_share if fin_in.owned_compute_share is not None else p.capital.owned_compute_share
    fin["context_engine"] = fin_in.context_engine if fin_in.context_engine is not None else p.capability.context_coverage
    fin["tax_rate"] = fin_in.tax_rate if fin_in.tax_rate is not None else p.finance.tau
    hpf = p.labor.hours_per_fte
    tau_L = p.labor.tau_L

    fn = priors.functions[["function_id", "function_name", "cost_bucket", "customer_facing", "labor_share", "iota_prior",
                           "rho_O", "personal_data", "high_reliability", "compute_share_of_nonlabor"]].copy()
    fn = fn.drop_duplicates("function_id").reset_index(drop=True)
    buckets = {"cogs": fin_in.cogs, "rnd": fin_in.rnd, "sm": fin_in.sm, "ga": fin_in.ga}

    # ---- 1. function spend and labor ---------------------------------------------------------
    if ing.opex is not None and len(ing.opex):
        ox = ing.opex.copy()
        unm = ox.function_id.isna()
        if unm.any():
            gaps.append(f"tier1: {unm.sum()} opex rows with unmapped cost centers allocated by prior")
        by_f = ox[~unm].groupby("function_id").amount.sum()
        lab_types = {"labor", "contractor"}
        lab_f = ox[~unm & ox.cost_type.isin(lab_types)].groupby("function_id").amount.sum()
        cmp_f = ox[~unm & (ox.cost_type == "compute")].groupby("function_id").amount.sum()
        fn["spend"] = fn.function_id.map(by_f).fillna(0.0)
        fn["labor_cost"] = fn.function_id.map(lab_f).fillna(0.0)
        fn["compute_cost"] = fn.function_id.map(cmp_f).fillna(0.0)
        total1 = float(ox.amount.sum())
        total0 = float(sum(buckets.values()))
        if total1 > 0 and abs(total1 / max(total0, 1e-9) - 1) > 0.1:
            # documented fallback (ingest issue inconsistent_totals): scale Tier 1 to the Tier 0 cost buckets
            for b, tot in buckets.items():
                m = (fn.cost_bucket == b).values
                cur = float(fn.loc[m, "spend"].sum())
                if cur > 0 and tot > 0:
                    k_ = tot / cur
                    for c in ("spend", "labor_cost", "compute_cost"):
                        fn.loc[m, c] = fn.loc[m, c] * k_
            prov["function_spend_scaling"] = "Tier 1 scaled to Tier 0 cost buckets (totals differed by more than 10 percent)"
        if unm.any():
            add = ox[unm].amount.sum()
            w = fn.spend / max(fn.spend.sum(), 1.0)
            fn["spend"] += add * w
            fn["labor_cost"] += add * w * fn.labor_share
        if rng is not None:
            noise = np.exp(rng.normal(0, mc.sd_function_share_tier1, len(fn)))
            fn["spend"] *= noise
            fn["labor_cost"] *= noise * np.exp(rng.normal(0, mc.sd_labor_share_tier1, len(fn)))
        prov["function_spend"] = "Tier 1 opex (mapped cost centers)"
        if not (ox.cost_type == "labor").any():
            fn["labor_cost"] = fn.spend * fn.labor_share
            gaps.append("tier1: no labor GL lines identified; labor share prior used")
    else:
        sh = _industry_shares(priors, fin_in.naics, S)
        fn = fn.merge(sh, on="function_id", how="left")
        fn["share_mean"] = fn.share_mean.fillna(0.003)
        fn["share_sd"] = fn.share_sd.fillna(fn.share_mean * mc.sd_function_share_prior)
        raw = fn.share_mean.values.copy()
        if rng is not None:
            rel = np.clip(fn.share_sd.values / np.maximum(raw, 1e-9), 0.05, 1.5)
            raw = raw * np.exp(rng.normal(0, rel) - rel ** 2 / 2)
        fn["spend"] = 0.0
        for b, tot in buckets.items():
            m = (fn.cost_bucket == b).values
            if m.any() and raw[m].sum() > 0:
                fn.loc[m, "spend"] = tot * raw[m] / raw[m].sum()
            elif tot > 0:
                gaps.append(f"no function in cost bucket {b}; {tot:,.0f} not allocated")
        ls = fn.labor_share.values.copy()
        if rng is not None:
            ls = np.clip(ls * np.exp(rng.normal(0, mc.sd_labor_share_prior, len(ls))), 0.05, 0.98)
        fn["labor_cost"] = fn.spend * ls
        fn["compute_cost"] = (fn.spend - fn.labor_cost) * fn.compute_share_of_nonlabor.fillna(0.0)
        prov["function_spend"] = f"prior function shares ({sh.attrs.get('source', '')}), normalized to Tier 0 cost buckets"
        gaps.append("tier1 missing: function spend imputed from industry priors")
        fn = fn.drop(columns=["share_mean", "share_sd"])
    fn["nonlabor"] = (fn.spend - fn.labor_cost).clip(lower=0.0)

    # ---- 2. headcount and wages by function and occupation -----------------------------------
    occ = priors.occupations.set_index("soc")
    fo, fo_src = priors.function_occ_for(fin_in.naics)
    prov["occupation_mix"] = fo_src
    rows = []
    if ing.roster is not None and len(ing.roster):
        r = ing.roster.copy()
        r["function_id"] = r.function_id.fillna(fn.function_id.iloc[int(np.argmax(fn.spend.values))])
        load = np.where(r.worker_type == "contractor", 1 + p.labor.tau_L_contractor, 1 + tau_L)
        comp = r.annual_total_comp.where(r.annual_total_comp.notna(), r.annual_base_comp) if "annual_total_comp" in r else r.annual_base_comp
        r["loaded_annual"] = comp * load
        if rng is not None:
            r["loaded_annual"] *= np.exp(rng.normal(0, mc.sd_wage_tier2, len(r)))
        known = r[r.soc.notna()]
        for x in known.itertuples():
            rows.append((x.function_id, x.soc, x.fte, x.loaded_annual, x.seniority, x.region, x.worker_type))
        for x in r[r.soc.isna()].itertuples():
            mix = fo[fo.function_id == x.function_id]
            for m in mix.itertuples():
                rows.append((x.function_id, m.soc, x.fte * m.weight, x.loaded_annual, x.seniority, x.region, x.worker_type))
        prov["headcount"] = "Tier 2 roster"
        prov["wages"] = "Tier 2 roster compensation x (1 + tau_L)"
        hc = pd.DataFrame(rows, columns=["function_id", "soc", "fte", "loaded_annual", "seniority", "region", "worker_type"])
        # Functions with spend but no roster rows: impute from the prior mix.
        missing = [f for f in fn.function_id if f not in set(hc.function_id) and float(fn.set_index("function_id").loc[f, "labor_cost"]) > 0]
        if missing:
            gaps.append(f"tier2: {len(missing)} functions with spend but no roster rows imputed from priors")
    else:
        missing = list(fn.function_id)
        hc = pd.DataFrame(columns=["function_id", "soc", "fte", "loaded_annual", "seniority", "region", "worker_type"])
        prov["headcount"] = "imputed: function labor cost / loaded wage of the prior occupation mix"
        prov["wages"] = "occupation median wages (" + priors.provenance.get("occupations", "") + ") x (1 + tau_L)"
        gaps.append("tier2 missing: headcount and wages imputed from occupation priors")
    imp = []
    lab = fn.set_index("function_id").labor_cost
    for f in missing:
        mix = fo[fo.function_id == f]
        if mix.empty or lab.get(f, 0) <= 0:
            continue
        w = mix.weight.values
        if rng is not None:
            w = rng.dirichlet(np.maximum(w * mc.conc_occ_prior, 0.05))
        wages = occ.loc[mix.soc, "wage_median"].values.astype(float) * (1 + tau_L)
        if rng is not None:
            wages = wages * np.exp(rng.normal(0, mc.sd_wage_prior, len(wages)))
        per = lab[f] / float((w * wages).sum())
        for soc, ww, wg in zip(mix.soc, w, wages):
            imp.append((f, soc, per * ww, wg, "mid", "US", "employee"))
    if imp:
        hc = pd.concat([hc, pd.DataFrame(imp, columns=hc.columns)], ignore_index=True)
    if (ing.roster is None or not len(ing.roster)) and fin_in.headcount:
        tot = hc.fte.sum()
        if tot > 0:
            s = fin_in.headcount / tot
            hc["fte"] *= s
            hc["loaded_annual"] /= s  # keep labor cost; implied pay adjusts
            prov["headcount"] += "; rescaled to Tier 0 headcount"
    hc = hc[hc.fte > 0].copy()
    hc["fte"] = hc.fte.astype(float)
    hc["loaded_annual"] = hc.loaded_annual.astype(float)
    hc["wage_h"] = hc.loaded_annual / hpf
    fn["fte"] = fn.function_id.map(hc.groupby("function_id").fte.sum()).fillna(0.0)
    fn["labor_cost_roster"] = fn.function_id.map(hc.assign(c=hc.fte * hc.loaded_annual).groupby("function_id").c.sum()).fillna(0.0)
    # Severance months from the regional mix (data agent's statutory anchors; see defaults transition.s_w_months).
    reg = hc.groupby("region").fte.sum()
    sev_months = float(sum(severance_months(k, p) * v for k, v in reg.items()) / max(reg.sum(), 1e-9)) \
        if len(reg) else p.transition.severance_months_US

    # ---- 3. hours by function, occupation and activity ---------------------------------------
    oa = priors.occupation_activity_for(set(hc.soc)) if hasattr(priors, "occupation_activity_for") else priors.occ_activity
    oa = oa[oa.soc.isin(set(hc.soc))]
    hc_g = hc.groupby(["function_id", "soc"], as_index=False).agg(fte=("fte", "sum"), wage_h=("wage_h", "mean"))
    hc_g["hours"] = hc_g.fte * hpf
    if rng is not None:
        parts = []
        for soc, grp in oa.groupby("soc"):
            ts = grp.time_share.values
            g2 = grp.copy()
            g2["time_share"] = rng.dirichlet(np.maximum(ts * mc.conc_activity_prior, 0.02)) if len(ts) > 1 else ts
            parts.append(g2)
        oa = pd.concat(parts, ignore_index=True) if parts else oa
    pool = hc_g.merge(oa, on="soc", how="inner")
    pool["h"] = pool.hours * pool.time_share
    act = priors.activities.set_index("dwa_id")
    pool["gwa_id"] = pool.dwa_id.map(act.gwa_id)
    pool = pool[pool.h > 0]

    # ---- 4. process volumes and step demand --------------------------------------------------
    pr = priors.processes.copy()
    pr = pr[pr.function_id.isin(set(fn.function_id))]
    vols = {}
    if ing.volumes is not None and len(ing.volumes):
        vols = ing.volumes.groupby("process_id").annual_volume.sum().to_dict()
    fixed = pr["fixed_volume_per_year"] if "fixed_volume_per_year" in pr.columns else pd.Series(np.nan, index=pr.index)
    prior_v = np.where(fixed.notna(), fixed, pr.typical_volume_per_musd_revenue.fillna(1.0) * S / 1e6)
    if rng is not None:
        prior_v = prior_v * np.exp(rng.normal(0, mc.sd_volume_prior, len(prior_v)) - mc.sd_volume_prior ** 2 / 2)
    v_in = pr.process_id.map(vols)
    vin = v_in.values.astype(float)
    if rng is not None:
        vin = vin * np.exp(rng.normal(0, mc.sd_volume_tier3, len(vin)))
    pr["volume"] = np.where(np.isfinite(vin), vin, prior_v)
    pr["volume_source"] = np.where(v_in.notna(), "Tier 3 volumes", pr.get("volume_source", "prior").fillna("prior"))
    if not vols:
        gaps.append("tier3 volumes missing: process volumes from per-revenue priors")
    pa = priors.process_activities.copy()
    pa = pa[pa.process_id.isin(set(pr.process_id))]
    pa["tier4"] = 0
    pa["cycle_time_days"] = np.nan
    task_map = None
    if getattr(ing, "firm_tasks", None) is not None and len(ing.firm_tasks):
        pa, task_map = apply_firm_tasks(pa, ing.firm_tasks, priors, pr.set_index("process_id").volume)
        prov["firm_tasks"] = "tier3_tasks: mapped tasks replace their step's activity mix and hours"
        n_un = int((task_map.method == "unmapped").sum())
        if n_un:
            gaps.append(f"tier3_tasks: {n_un} firm tasks could not be mapped to an O*NET activity (firm_tasks_mapping.csv)")
    if ing.time_study is not None and len(ing.time_study):
        ts = ing.time_study
        for r_ in ts.itertuples():
            m = (pa.process_id == r_.process_id) & ((pa.step == r_.step) if pd.notna(r_.step) else (pa.dwa_id == r_.dwa_id))
            pa.loc[m, "hours_per_unit"] = r_.hours_per_unit
            pa.loc[m, "tier4"] = 1
            ct_ = getattr(r_, "cycle_time_days", None)
            if ct_ is not None and pd.notna(ct_):
                pa.loc[m, "cycle_time_days"] = float(ct_)
        prov["step_hours"] = "Tier 4 time study where given; process library elsewhere"
    pa["known_hours"] = pa.hours_per_unit.notna()
    pa = pa.merge(pr[["process_id", "function_id", "volume"]], on="process_id")
    pa["gwa_id"] = pa.dwa_id.map(act.gwa_id)
    pa["demand"] = pa.volume * pa.hours_per_unit.fillna(0.0)
    # Steps without hours per unit in the library claim a share of the function's hours of that
    # activity (or of its GWA), split among such claimants (UNKNOWN_SHARE, assumed).
    if (~pa.known_hours).any():
        fa_h = pool.groupby(["function_id", "dwa_id"]).h.sum()
        fg_h = pool.groupby(["function_id", "gwa_id"]).h.sum()
        unk = pa[~pa.known_hours]
        n_a = unk.groupby(["function_id", "dwa_id"]).size()
        n_g = unk.groupby(["function_id", "gwa_id"]).size()
        ka = list(zip(unk.function_id, unk.dwa_id))
        kg = list(zip(unk.function_id, unk.gwa_id))
        da = np.array([fa_h.get(k, 0.0) / n_a.get(k, 1) for k in ka])
        dg = np.array([fg_h.get(k, 0.0) / n_g.get(k, 1) for k in kg])
        pa.loc[~pa.known_hours, "demand"] = UNKNOWN_SHARE * np.where(da > 0, da, dg)
        pa.loc[~pa.known_hours, "hours_per_unit"] = pa.loc[~pa.known_hours, "demand"] / pa.loc[~pa.known_hours, "volume"].clip(lower=1e-9)
        gaps.append(f"process library: {int((~pa.known_hours).sum())} steps without hours per unit claim a share of their activity pool")

    # ---- 5. allocate pool hours to process steps (activity pool first, then the GWA pool) -----
    pool_fa = pool.groupby(["function_id", "dwa_id"]).h.sum()
    claim1 = pa.groupby(["function_id", "dwa_id"]).demand.sum()
    avail1 = (pool_fa * COVERAGE_MAX).reindex(claim1.index).fillna(0.0)
    scale1 = (avail1 / claim1.replace(0, np.nan)).clip(upper=1.0).fillna(0.0)
    pa["alloc1"] = pa.demand * pa.set_index(["function_id", "dwa_id"]).index.map(scale1).values
    used1 = pa.groupby(["function_id", "dwa_id"]).alloc1.sum()
    rem = pool.groupby(["function_id", "dwa_id", "gwa_id"]).h.sum().reset_index()
    rem["used"] = rem.set_index(["function_id", "dwa_id"]).index.map(used1).fillna(0.0).values if len(rem) else []
    rem["left"] = (rem.h - rem.used).clip(lower=0.0)
    pool_fg = rem.groupby(["function_id", "gwa_id"]).left.sum()
    pa["unmet"] = (pa.demand - pa.alloc1).clip(lower=0.0)
    claim2 = pa.groupby(["function_id", "gwa_id"]).unmet.sum()
    avail2 = (pool_fg * COVERAGE_MAX).reindex(claim2.index).fillna(0.0)
    scale2 = (avail2 / claim2.replace(0, np.nan)).clip(upper=1.0).fillna(0.0)
    pa["alloc2"] = pa.unmet * pa.set_index(["function_id", "gwa_id"]).index.map(scale2).values
    pa["hours"] = pa.alloc1 + pa.alloc2
    used2 = pa.groupby(["function_id", "gwa_id"]).alloc2.sum()
    # occupation composition of each allocation: from the activity pool (alloc1) and GWA pool (alloc2)
    pool_soc_a = pool.groupby(["function_id", "dwa_id", "soc"]).h.sum()
    pool_soc_a = pool_soc_a / pool_soc_a.groupby(level=[0, 1]).transform("sum")
    pool_g = pool.merge(rem[["function_id", "dwa_id", "h", "left"]].rename(columns={"h": "h_tot"}), on=["function_id", "dwa_id"])
    pool_g["left_soc"] = pool_g.h * (pool_g.left / pool_g.h_tot.replace(0, np.nan)).fillna(0.0)
    pool_soc_g = pool_g.groupby(["function_id", "gwa_id", "soc"]).left_soc.sum()
    pool_soc_g = pool_soc_g / pool_soc_g.groupby(level=[0, 1]).transform("sum").replace(0, np.nan)

    # ---- 6. build units -----------------------------------------------------------------------
    gattr = priors.gwa_attributes().set_index("gwa_id")
    G_ATTR = {g: r._asdict() for g, r in zip(gattr.index, gattr.itertuples(index=False))}
    G_DEFAULT = next(iter(G_ATTR.values()))
    wage_fs = hc_g.set_index(["function_id", "soc"]).wage_h.to_dict()
    licensed_soc = set(occ.index[occ.licensed_signoff == 1])
    PHYS = occ.physical_share.astype(float).to_dict()
    WMED = occ.wage_median.astype(float).to_dict()
    W_ALL = occupation_wage_fallback(occ)
    lts = pd.to_numeric(act["licensed_time_share"], errors="coerce").fillna(0.0) if "licensed_time_share" in act.columns else pd.Series(0.0, index=act.index)
    ACT = {a: (float(e), float(h), float(ph), str(rc), str(tt), g, float(l)) for a, e, h, ph, rc, tt, g, l in zip(
        act.index, act.exposure_llm.fillna(0.5), act.est_task_hours.fillna(1.0), act.physical.fillna(0.0),
        act.regulated_class.fillna("none"), act.dwa_title.fillna(""), act.gwa_id, lts)}
    FN = {r.function_id: r for r in fn.itertuples(index=False)}
    units, uocc = [], []
    icfr_g = set(p.accounting.icfr_gwas)
    # EU AI Act high-risk status (Annex III) needs an EU nexus and a plan that runs past the date the obligations apply
    # from (Regulation (EU) 2026/1744: 2 December 2027); otherwise such units are not high risk
    eu_act = eu_ai_act_high_risk_applies(eu_ai_act_nexus(ing, hc), int(ing.financials.fiscal_year) + 1,
                                         float(p.constraints.horizon_years), p)
    eu_nexus = eu_act["applies"]

    def add_unit(key, process_id, function_id, activity_ids, gwa_id, hours, occ_hours: dict, kind, step=None,
                 critical=1, override=None, volume=None, baseline="H", vendor_spend=0.0, title=None,
                 physical_override=None, licensed_override=None, tier4=0, cycle_time_days=None):
        if hours <= 1e-6:
            return
        socs = list(occ_hours)
        hs = np.array([occ_hours[x] for x in socs], dtype=float)
        if hs.sum() <= 0:
            return
        hs = hs * hours / hs.sum()
        wages = np.array([wage_fs.get((function_id, x), WMED.get(x, W_ALL) * (1 + tau_L) / hpf) for x in socs], dtype=float)
        wage_h = float((hs * wages).sum() / hs.sum())
        aids = [a for a in activity_ids if a in ACT]
        if aids:
            ex = float(np.mean([ACT[a][0] for a in aids]))
            est = float(np.mean([ACT[a][1] for a in aids]))
            ph_a = float(np.mean([ACT[a][2] for a in aids]))
            rcs = [ACT[a][3] for a in aids]
            rc0 = modal_regulated_class(rcs, eu_nexus)     # ties go to the most demanding class (MODEL_RISK.md 3)
            ttl = ACT[aids[0]][4]
        else:
            ex, est, ph_a, rc0, ttl = 0.5, 1.0, 0.0, "none", ""
        physical = max(ph_a, float(np.average([PHYS.get(x, 0.0) for x in socs], weights=hs)))
        if physical_override is not None and np.isfinite(physical_override):   # step-level value (W5) beats the DWA's
            physical = float(physical_override)
        rc = override if isinstance(override, str) and override else rc0
        lic_share = float(hs[[x in licensed_soc for x in socs]].sum() / hs.sum()) if gwa_id in SIGNOFF_GWAS else 0.0
        if aids:
            lic_share = max(lic_share, float(np.mean([ACT[a][6] for a in aids])))
        if licensed_override is not None and np.isfinite(licensed_override):   # step-level value (W5)
            lic_share = float(licensed_override)
            if lic_share < p.permissibility.licensed_share_threshold and rc == "licensed" and not override:
                rc = "none"
        if rc == "licensed":
            lic_share = 1.0
        fnr = FN[function_id]
        if rc == "none" and fnr.personal_data and gwa_id in HR_HIGH_RISK_GWAS:
            rc = "high_risk_eu"
        if rc == "high_risk_eu" and not eu_nexus:          # Art. 2 nexus and the Annex III date (Reg. (EU) 2026/1744)
            rc = "none"
        if lic_share >= p.permissibility.licensed_share_threshold and rc == "none":
            rc = "licensed"
        ga = G_ATTR.get(gwa_id, G_DEFAULT)
        r_bar = float(ga["r_bar"])
        L_mult = float(ga["L_mult"])
        if fnr.high_reliability and gwa_id in HIGH_REL_GWAS:
            r_bar = max(r_bar, p.review.r_bar_high)
            L_mult = max(L_mult, p.review.L_mult_regulated)
        if rc == "licensed":
            r_bar = max(r_bar, p.review.r_bar_licensed)
        # regulated status is an explicit attribute from the activity's class and its function's financial-reporting
        # scope, never from the reliability target (a lower target does not make a step unregulated)
        basis = []
        if rc != "none":
            basis.append(f"regulated_class:{rc}")
        if gwa_id in icfr_g:                    # activity classes that touch financial reporting (firm setting)
            basis.append("icfr activity class")
        if kind == "process":
            v = float(volume)
            t = hours / max(v, 1e-9)
            d = t                     # spec 3: task length = human hours to complete one instance (one output unit)
        else:
            d = est
            t = est
            v = hours / max(t, 1e-9)
        uid = len(units)
        units.append({"unit_id": uid, "unit_key": key, "process_id": process_id, "function_id": function_id, "kind": kind,
                      "activity_id": activity_ids[0] if len(activity_ids) == 1 else gwa_id, "gwa_id": gwa_id,
                      "title": title or (ttl or str(ga.get("key", gwa_id))),
                      "step": step, "critical": int(critical), "hours": hours, "wage_h": wage_h, "v": v, "t": t, "d": d,
                      "est_task_hours": est, "baseline": baseline, "vendor_spend": vendor_spend, "exposure": ex,
                      "physical": physical, "regulated_class": rc, "regulated": int(bool(basis)), "regulated_basis": ";".join(basis),
                      "licensed_share": lic_share, "r_bar": r_bar, "L_mult": L_mult,
                      "separable": float(ga["separable"]), "eliminable": int(ga["eliminable"]),
                      "customer_facing": int(bool(fnr.customer_facing) and bool(ga["customer_facing"])),
                      "personal_data": int(bool(fnr.personal_data) or bool(ga["personal_data"])),
                      "ethics_sensitive": int(ga["ethics_sensitive"]),
                      "iota_min": float(ga["iota_star"]) + (p.readiness.iota_min_regulated_add if rc != "none" else 0.0),
                      "sen_junior": float(ga["sen_junior"]), "sen_mid": float(ga["sen_mid"]), "sen_senior": float(ga["sen_senior"]),
                      "cost_bucket": fnr.cost_bucket, "tier4": int(tier4),
                      "cycle_time_days": np.nan if cycle_time_days is None else float(cycle_time_days)})
        for s, h in zip(socs, hs):
            uocc.append((uid, s, float(h), float(wage_fs.get((function_id, s), np.nan))))

    fnx = fn.set_index("function_id")
    # process steps (merge repeated activities within a process)
    pa_g = pa.groupby(["process_id", "dwa_id"], as_index=False).agg(
        function_id=("function_id", "first"), gwa_id=("gwa_id", "first"), step=("step", "min"), hours=("hours", "sum"),
        alloc1=("alloc1", "sum"), alloc2=("alloc2", "sum"), critical=("critical_path", "max"), volume=("volume", "first"),
        override=("regulated_class_override", "first") if "regulated_class_override" in pa.columns else ("dwa_id", lambda x: None),
        phys_o=("physical_override", "max") if "physical_override" in pa.columns else ("dwa_id", lambda x: np.nan),
        lic_o=("licensed_override", "max") if "licensed_override" in pa.columns else ("dwa_id", lambda x: np.nan),
        tier4=("tier4", "max"), cycle_time_days=("cycle_time_days", "max"))
    PSA: dict = {}
    for (f, a, x), sh in pool_soc_a.items():
        PSA.setdefault((f, a), []).append((x, sh))
    PSG: dict = {}
    for (f, g, x), sh in pool_soc_g.dropna().items():
        PSG.setdefault((f, g), []).append((x, sh))
    for r_ in pa_g.sort_values(["process_id", "step"]).itertuples():
        oh: dict[str, float] = {}
        if r_.alloc1 > 0:
            for x, sh in PSA.get((r_.function_id, r_.dwa_id), []):
                oh[x] = oh.get(x, 0.0) + r_.alloc1 * sh
        if r_.alloc2 > 0:
            for x, sh in PSG.get((r_.function_id, r_.gwa_id), []):
                oh[x] = oh.get(x, 0.0) + r_.alloc2 * sh
        add_unit(f"{r_.process_id}|{r_.dwa_id}", r_.process_id, r_.function_id, [r_.dwa_id], r_.gwa_id, r_.hours, oh,
                 "process", step=r_.step, critical=r_.critical, override=r_.override if isinstance(r_.override, str) else None,
                 volume=r_.volume, physical_override=_num_or_none(r_.phys_o), licensed_override=_num_or_none(r_.lic_o),
                 tier4=int(r_.tier4 or 0), cycle_time_days=_num_or_none(r_.cycle_time_days))
    # residual work by function and GWA
    left = rem.copy()
    left["left2"] = left.left - left.set_index(["function_id", "gwa_id"]).index.map(used2).fillna(0.0).values * (
        left.left / left.groupby(["function_id", "gwa_id"]).left.transform("sum").replace(0, np.nan)).fillna(0.0).values
    left = left[left.left2 > 1e-6]
    soc_left = pool.merge(left[["function_id", "dwa_id", "h", "left2"]].rename(columns={"h": "h_tot"}), on=["function_id", "dwa_id"])
    soc_left["hh"] = soc_left.h * soc_left.left2 / soc_left.h_tot
    by_soc = soc_left.groupby(["function_id", "gwa_id", "soc"]).hh.sum()
    by_act = soc_left.groupby(["function_id", "gwa_id", "dwa_id"]).hh.sum()
    soc_d: dict = {}
    for (f, g, x), h in by_soc.items():
        soc_d.setdefault((f, g), {})[x] = h
    act_d: dict = {}
    for (f, g, a), h in by_act.items():
        act_d.setdefault((f, g), []).append((h, a))
    for (f, g), oh in soc_d.items():
        aid = [a for _, a in sorted(act_d[(f, g)], reverse=True)]
        add_unit(f"{f}::residual|{g}", f"{f}::residual", f, aid, g, float(sum(oh.values())), oh, "residual",
                 title=f"Other: {G_ATTR.get(g, {}).get('key', g)}")
    # outsourced work (Tier 3 vendor labor outsourcing)
    if ing.vendors is not None and len(ing.vendors):
        prof = priors_profiles(priors)
        for vrow in ing.vendors[ing.vendors.labor_outsourcing == 1].itertuples():
            f = vrow.function_id
            if f not in fnx.index:
                continue
            fam = vrow.family if isinstance(vrow.family, str) else "clerical"
            shares = prof.get(fam, prof["clerical"])
            mix = fo[fo.function_id == f]
            w_all = occupation_wage_fallback(occ)
            wref = float((mix.weight * occ.reindex(mix.soc).wage_median.fillna(w_all).values).sum()) * (1 + tau_L) / hpf if len(mix) \
                else w_all * (1 + tau_L) / hpf
            rho = fnx.loc[f, "rho_O"] if pd.notna(fnx.loc[f, "rho_O"]) else p.outsourcing.rho_O_default
            per_hour = wref * (rho + p.outsourcing.zeta_O)
            spend = vrow.annual_spend * (float(np.exp(rng.normal(0, 0.03))) if rng is not None else 1.0)
            hrs_tot = spend / max(per_hour, 1e-9)
            top_soc = mix.sort_values("weight").soc.iloc[-1] if len(mix) else hc.soc.iloc[0]
            for g, sh in shares.items():
                add_unit(f"{f}::outsourced|{vrow.category}|{g}", f"{f}::outsourced", f, [g], g, hrs_tot * sh,
                         {top_soc: 1.0}, "outsourced", baseline="O", vendor_spend=spend * sh,
                         title=f"Outsourced ({vrow.category}): {G_ATTR.get(g, {}).get('key', g)}")
        prov["outsourced_work"] = "Tier 3 vendor spend with labor-outsourcing categories"
    U = pd.DataFrame(units)
    UO = pd.DataFrame(uocc, columns=["unit_id", "soc", "hours", "wage_h"])
    # Split each function's residual work into workstreams of at most chunk FTE (by GWA order), so that one
    # initiative is sized like a real program: chunk = max(residual_chunk_fte, total residual FTE / max chunks).
    res = U.kind == "residual"
    if res.any():
        tot_fte = float(U.loc[res, "hours"].sum()) / hpf
        chunk = max(p.org.residual_chunk_fte, tot_fte / max(p.org.max_residual_streams, 1))
        new_pid = U.process_id.copy()
        for f, grp in U[res].sort_values(["function_id", "gwa_id"]).groupby("function_id"):
            cum, k = 0.0, 1
            for i, h in zip(grp.index, grp.hours):
                fte_i = h / hpf
                if cum > 0 and cum + fte_i > chunk:
                    k += 1
                    cum = 0.0
                new_pid.at[i] = f"{f}::residual{k}"
                cum += fte_i
        U["process_id"] = new_pid

    # ---- 7. readiness by function and process ------------------------------------------------
    w = p.readiness.weights
    if ing.systems is not None and len(ing.systems):
        sy = ing.systems.copy()
        n_sys = sy.groupby("function_id").size()
        agg = sy.groupby("function_id").agg(sor=("system_of_record", "max"), api=("api_available", "mean"),
                                            mdq=("data_quality", "mean"), idr=("identity_resolution", "mean"),
                                            uns=("unstructured_share", "mean"))
        io = F.readiness_index(agg.sor, agg.api, agg.mdq, agg.idr, n_sys.reindex(agg.index), agg.uns, w, p.readiness.n_systems_ref)
        iota_f = pd.Series(np.asarray(io), index=agg.index)
        if rng is not None:
            iota_f = (iota_f + rng.normal(0, mc.sd_iota_tier3, len(iota_f))).clip(0.02, 0.98)
        lic = sy.groupby("function_id").annual_license_cost.mean() if "annual_license_cost" in sy else pd.Series(dtype=float)
        if "data_classification" in sy.columns and sy.data_classification.notna().any():
            rank = sy.data_classification.map({c: i for i, c in enumerate(DATA_CLASSES)})
            fn["data_class"] = fn.function_id.map(rank.groupby(sy.function_id).max()).map(
                lambda x: DATA_CLASSES[int(x)] if pd.notna(x) else None)
        if "write_access" in sy.columns:
            fn["write_access"] = fn.function_id.map(sy.groupby("function_id").write_access.max())
        if "external_inputs" in sy.columns:
            fn["external_inputs"] = fn.function_id.map(sy.groupby("function_id").external_inputs.mean())
        fn["iota0"] = fn.function_id.map(iota_f)
        fn["n_systems"] = fn.function_id.map(n_sys)
        fn["license_cost"] = fn.function_id.map(lic)
        miss = fn.iota0.isna()
        if miss.any():
            gaps.append(f"tier3 systems: {miss.sum()} functions without systems use the readiness prior")
        prov["readiness"] = "Tier 3 systems inventory (readiness index, spec Section 4)"
    else:
        fn["iota0"] = np.nan
        fn["n_systems"] = np.nan
        fn["license_cost"] = np.nan
        gaps.append("tier3 systems missing: data readiness from function priors")
        prov["readiness"] = "function readiness priors (assumed)"
    miss = fn.iota0.isna()
    prior_i = fn.iota_prior.astype(float).values
    if rng is not None:
        prior_i = np.clip(prior_i + rng.normal(0, mc.sd_iota_prior, len(prior_i)), 0.02, 0.98)
    fn.loc[miss, "iota0"] = prior_i[miss.values]
    fn["n_systems"] = fn.n_systems.fillna(p.readiness.default_n_systems)
    fn["license_cost"] = fn.license_cost.fillna(p.transition.license_cost_per_system)
    sp = ing.sponsors.groupby("function_id").engaged.max().to_dict() if ing.sponsors is not None and len(ing.sponsors) else {}
    fn["sponsor"] = fn.function_id.map(sp)
    # security attributes (spec 18.5): data class of the systems, write access, external inputs. Defaults:
    # functions with personal data hold confidential data, others internal; agents can write; customer-facing
    # functions take external inputs. All are documented fallbacks listed as data gaps.
    for c in ("data_class", "write_access", "external_inputs"):
        if c not in fn.columns:
            fn[c] = np.nan
    if fn.data_class.isna().any():
        gaps.append("tier3 systems: data classification missing for some functions (defaults: confidential with personal data, else internal)")
    fn["data_class"] = [d if isinstance(d, str) else ("confidential" if pd_ else "internal")
                        for d, pd_ in zip(fn.data_class, fn.personal_data.fillna(0).astype(bool))]
    fn["write_access"] = fn.write_access.astype(float).fillna(1.0)
    fn["external_inputs"] = fn.external_inputs.astype(float).fillna(
        pd.Series(np.where(fn.customer_facing.astype(float) > 0, 0.6, 0.15), index=fn.index))

    # ---- 8. processes and edges ---------------------------------------------------------------
    if len(U) == 0:
        raise ValueError("no activity units could be built; check the inputs")
    pids = U.drop_duplicates("process_id")[["process_id", "function_id", "kind"]]
    pdf = pids.merge(pr[["process_id", "process_name", "output_unit", "volume", "volume_source"]], on="process_id", how="left")
    fname = fnx.function_name
    pdf["process_name"] = pdf.process_name.fillna(pdf.apply(
        lambda r: f"{fname[r.function_id]}: {'other work, stream ' + r.process_id.split('residual')[-1] if r.kind == 'residual' else 'outsourced work'}", axis=1))
    pdf = pdf.merge(fn[["function_id", "iota0", "n_systems", "license_cost", "sponsor", "cost_bucket", "data_class",
                        "write_access", "external_inputs"]], on="function_id")
    g_u = U.groupby("process_id")
    pdf["n_units"] = pdf.process_id.map(g_u.size())
    pdf["hours"] = pdf.process_id.map(g_u.hours.sum())
    pdf["fte"] = pdf.hours / hpf
    # explicit regulated attribute (spec 5, 24.4): a process is regulated if any unit is (regulated class, EU AI Act
    # high-risk, licensed sign-off, ICFR function or activity) or the process is in ICFR scope by name; a Tier 3
    # volumes row can set it explicitly. The reliability target plays no part.
    scope, scope_basis, step_tab = icfr_scope_table(pdf, priors, ing)
    pdf["icfr_scope"] = pdf.process_id.map(scope).fillna("none")
    pdf["icfr_basis"] = pdf.process_id.map(scope_basis).fillna("")
    # step-level scope from the data contract's channels and conditions (process steps); residual workstreams are
    # outside ICFR unless an activity class is listed in accounting.icfr_gwas
    recs = [step_tab.get((str(pid), str(aid))) for pid, aid in zip(U.process_id, U.activity_id)]
    U["icfr_step"] = [int(bool(r and r["on"])) for r in recs]
    U["icfr_status"] = [(r["status"] if r else "out") for r in recs]
    U["icfr_channel"] = [(r["channel"] if r and r["on"] else "") for r in recs]
    U["icfr_condition"] = [(r["condition"] if r and r["on"] else "") for r in recs]
    U["icfr_decided_by"] = [(r["decided_by"] if r else "") for r in recs]
    U["financial_system_written"] = [(r["systems_written"] if r else "") for r in recs]
    full = U.process_id.map(pdf.set_index("process_id").icfr_scope).fillna("none").values == "full"
    U.loc[full & (U.icfr_step.values == 0) & (U.kind.values == "process"), ["icfr_step", "icfr_status", "icfr_channel"]] = [1, "in scope", "process"]
    pdf["icfr"] = pdf.process_id.map(U.groupby("process_id").icfr_step.max()).fillna(0).astype(bool) | (pdf.icfr_scope == "full")
    tag = (U.icfr_step == 1).values
    U.loc[tag, "regulated_basis"] = [";".join(sorted(set(filter(None, (b + ";icfr").split(";"))))) for b in U.loc[tag, "regulated_basis"]]
    U.loc[tag, "regulated"] = 1
    ovr = {}
    if ing.volumes is not None and len(ing.volumes) and "regulated" in ing.volumes.columns:
        ovr = {k: bool(v) for k, v in ing.volumes.dropna(subset=["regulated"]).groupby("process_id").regulated.first().items()}
    for pid, val in ovr.items():
        m = (U.process_id == pid).values
        U.loc[m, "regulated"] = int(val)
        U.loc[m, "regulated_basis"] = "firm input"
    pdf["regulated"] = pdf.process_id.map(U.groupby("process_id").regulated.max()).astype(float)
    pdf["regulated_basis"] = pdf.process_id.map(U.groupby("process_id").regulated_basis.agg(
        lambda x: ";".join(sorted(set(";".join(x).split(";")) - {""}))))
    pdf["high_risk"] = pdf.process_id.map(g_u.apply(lambda g: float((g.regulated_class == "high_risk_eu").any()), include_groups=False))
    pdf["platform"] = pdf.function_id
    # process-level systems share the function's systems
    sys_share = pdf.hours / pdf.groupby("function_id").hours.transform("sum")
    pdf["n_systems_p"] = np.maximum(1.0, pdf.n_systems * np.sqrt(sys_share))
    edges = []
    for pid, grp in U[U.kind == "process"].groupby("process_id"):
        steps = sorted(grp.step.dropna().unique())
        by_step = {s: list(grp[grp.step == s].unit_id) for s in steps}
        for s0, s1 in zip(steps[:-1], steps[1:]):
            for a in by_step[s0]:
                for b in by_step[s1]:
                    if a != b:
                        edges.append((pid, a, b))
    E = pd.DataFrame(edges, columns=["process_id", "u_from", "u_to"])
    pdf["n_edges"] = pdf.process_id.map(E.groupby("process_id").size()).fillna(0).astype(int)
    pdf = pdf.reset_index(drop=True)
    # integrations a unit uses (spec 18.1 technical debt): its process's systems spread over its steps, at least one
    nsp = dict(zip(pdf.process_id, pdf.n_systems_p))
    nun = U.groupby("process_id").size().to_dict()
    U["N_int"] = [float(np.clip(round(nsp[pid]), 1, 4)) for pid in U.process_id]

    org, ogaps = _org_inputs(ing, p, rng, len(fn))
    gaps += [f"tier3 org: {g} from prior" for g in ogaps]
    org["severance_months"] = sev_months
    o_in = ing.org
    for k in ("decisions_per_year", "change_capacity_fte", "ai_engineers_per_process", "process_owners_per_process",
              "sme_fte_per_process", "affected_fte_per_change_manager", "benefit_realization_past",
              "pilots_to_production_past", "redeployment_share", "sells_to_us_government", "it_spend", "severance_standard",
              "domestic_dev_share", "asu_2025_06_adoption_year", "ai_engineers_in_house", "ai_engineer_hires_per_year",
              "knowledge_holders_per_process", "knowledge_holders_displaced", "contemplation_date_years", "release_early",
              "sub_threshold_pacing", "vendor_regions", "vendor_region_premium", "vendor_dpf_certified", "transfer_cost",
              "contractor_access"):
        val = getattr(o_in, k, None)
        if val is not None:
            org[k] = val
        else:
            gaps.append(f"tier3 org: {k} not given; class d scenario range used")
    # labor law, talent and residency by site (theory_labor; spec 24.5, 24.6)
    from . import labor as LAB
    jsum, jdf = LAB.build(ing, hc, p, priors, org, float(fin.get("headcount") or hc.fte.sum() if len(hc) else 0.0),
                          list(fn.function_id))
    org["jurisdiction"] = jsum
    org["eu_ai_act"] = eu_act                                # nexus, Annex III / Annex I dates (Reg. (EU) 2026/1744)
    org["severance_months"] = jsum["severance_months"]      # max(statutory floor, plan) by site, headcount-weighted
    fin["_residency_share"] = jsum["residency_share"]

    # median wages of the transformation roles (spec 7), for build, integration and team costs
    if ing.product_occupations is not None and len(ing.product_occupations):
        fin["_occ_wages"] = {s: float(occ.wage_median.get(s)) for s in set(ing.product_occupations.soc)
                             if s in occ.index and pd.notna(occ.wage_median.get(s))}
    fin["_role_wages"], prov["role_wages"] = role_wages(occ, p)
    compute_cogs = float(fn[fn.cost_bucket == "cogs"].compute_cost.sum())
    labor_cogs = float(U[(U.cost_bucket == "cogs") & (U.baseline == "H")].eval("hours * wage_h").sum())
    part1 = part1_baseline(fin, p, compute_cogs, labor_cogs)
    U["base_cost"] = np.where(U.baseline == "O", U.vendor_spend, U.hours * U.wage_h)
    U["fte"] = U.hours / hpf

    firm = Firm(name=fin_in.company_name, base_year=int(fin_in.fiscal_year) + 1, fin=fin, part1=part1, functions=fn,
                units=U, unit_occ=UO, processes=pdf, edges=E, org=org, task_map=task_map,
                provenance={**prov, **{f"prior.{k}": v for k, v in priors.provenance.items()}},
                gaps=gaps, tiers=ing.tiers, is_draw=rng is not None, products=ing.products,
                product_occupations=ing.product_occupations, ai_features=ing.ai_features,
                security=ing.security.model_dump(), regime=ing.regime.model_dump(), jurisdictions=jdf,
                staffing=hc[["function_id", "soc", "fte", "region"]].copy() if len(hc) else None)
    if structure is not None:
        firm = align_to(firm, structure)
    return firm


def priors_profiles(priors: Priors) -> dict[str, dict[str, float]]:
    """Family activity profiles keyed by GWA id (used for outsourced work)."""
    from .config import PRIORS_DIR
    prof = pd.read_csv(PRIORS_DIR / "activity_profiles.csv")
    keymap = dict(zip(priors.gwa_attributes().key, priors.gwa_attributes().gwa_id))
    prof["gwa_id"] = prof.gwa_key.map(keymap)
    return {f: dict(zip(g.gwa_id, g.share)) for f, g in prof.groupby("family")}


def align_to(draw: Firm, point: Firm) -> Firm:
    """Put a Monte Carlo draw on the point estimate's unit and process structure (same order); units
    the draw lacks get zero hours, extra draw units are dropped."""
    num = ["hours", "wage_h", "v", "t", "d", "vendor_spend", "exposure", "physical", "base_cost", "fte"]
    d = draw.units.set_index("unit_key")
    pu = point.units.copy()
    idx = pu.unit_key
    for c in num:
        vals = d[c].reindex(idx).values
        pu[c] = np.where(np.isfinite(vals.astype(float)), vals, 0.0 if c in ("hours", "v", "vendor_spend", "base_cost", "fte") else pu[c].values)
    # keep a positive time per unit so costs stay defined
    pu["t"] = np.where(pu.t > 0, pu.t, point.units.t)
    pu["d"] = np.where(pu.d > 0, pu.d, point.units.d)
    pu["v"] = np.where(pu.hours > 0, pu.hours / pu.t, 0.0)
    pp = point.processes.copy()
    dp = draw.processes.set_index("process_id")
    for c in ("iota0", "volume", "hours", "fte"):
        vals = dp[c].reindex(pp.process_id).values.astype(float)
        pp[c] = np.where(np.isfinite(vals), vals, pp[c].values)
    draw.units, draw.processes, draw.edges = pu, pp, point.edges
    uo = draw.unit_occ.merge(draw.units[["unit_id"]], on="unit_id", how="inner")
    draw.unit_occ = point.unit_occ  # occupation shares from the point estimate
    return draw


def perturb_firm(point: Firm, ing: IngestResult, priors: Priors, p: Params, rng: np.random.Generator) -> Firm:
    """Fast Monte Carlo draw on the point estimate's structure (spec Section 9, confidence intervals
    from imputation uncertainty). Each input that was imputed gets the prior's uncertainty; each input
    that was observed gets a small measurement uncertainty:
      function labor dollars   Tier 1 present: sd_function_share_tier1; else prior share sd, renormalized
                               within Tier 0 cost buckets, times labor-share noise;
      occupation mix, wages    Tier 2 present: sd_wage_tier2 on wages; else a Dirichlet mix and sd_wage_prior;
      activity time shares     Dirichlet with conc_activity_prior (Tier 4 steps: conc_activity_tier4);
      process volumes          sd_volume_tier3 where given, else sd_volume_prior;
      readiness                sd_iota_tier3 with a systems inventory, else sd_iota_prior;
      organizational inputs    wide prior draws for fields not given.
    Function hours are conserved within each function when Tier 2 fixes headcount."""
    mc = p.mc
    U = point.units.copy()
    P = point.processes.copy()
    fn = point.functions
    t1 = ing.opex is not None and len(ing.opex) > 0
    t2 = ing.roster is not None and len(ing.roster) > 0
    t3v = ing.volumes is not None and len(ing.volumes) > 0
    t3s = ing.systems is not None and len(ing.systems) > 0
    fids = list(fn.function_id)
    fidx = {f: i for i, f in enumerate(fids)}
    nf = len(fids)
    # function-level labor factor
    if t2:
        lab_f = np.ones(nf)
    elif t1:
        lab_f = np.exp(rng.normal(0, mc.sd_function_share_tier1, nf) + rng.normal(0, mc.sd_labor_share_tier1, nf))
    else:
        sh = _industry_shares(priors, ing.financials.naics, ing.financials.revenue).set_index("function_id")
        rel = np.clip((sh.share_sd / sh.share_mean.clip(lower=1e-9)).reindex(fids).fillna(mc.sd_function_share_prior).values, 0.05, 1.5)
        raw = np.exp(rng.normal(0, rel) - rel ** 2 / 2)
        b = fn.cost_bucket.values
        spend = fn.spend.values
        new = spend * raw
        for bk in sorted(set(b)):
            m = b == bk
            if new[m].sum() > 0:
                new[m] *= spend[m].sum() / new[m].sum()
        lab_f = new / np.maximum(spend, 1e-9) * np.exp(rng.normal(0, mc.sd_labor_share_prior, nf))
    # occupation mix and wage factors per (function, soc)
    uo = point.unit_occ.merge(U[["unit_id", "function_id"]], on="unit_id")
    keys = pd.MultiIndex.from_frame(uo[["function_id", "soc"]].drop_duplicates())
    n = len(keys)
    if t2:
        wf = np.exp(rng.normal(0, mc.sd_wage_tier2, n))
        mixf = np.ones(n)
    else:
        wf = np.exp(rng.normal(0, mc.sd_wage_prior, n))
        base_w = uo.groupby(["function_id", "soc"]).hours.sum().reindex(keys).values
        share = base_w / pd.Series(base_w, index=keys).groupby(level=0).transform("sum").values
        mixf = rng.gamma(np.maximum(share * mc.conc_occ_prior, 0.05)) / np.maximum(share * mc.conc_occ_prior, 0.05)
        mixf = mixf / pd.Series(mixf * share, index=keys).groupby(level=0).transform("sum").values
    kpos = {k: i for i, k in enumerate(keys)}
    pos = np.array([kpos[(f, s)] for f, s in zip(uo.function_id, uo.soc)])
    lab = lab_f[[fidx[f] for f in uo.function_id]]
    # dollars by (unit, soc) scale with lab x mix; hours scale with dollars / wage factor
    hours_new = uo.hours.values * lab * mixf[pos] / wf[pos]
    wfb = U.set_index("unit_id").wage_h.reindex(uo.unit_id).values
    wage_new = np.where(np.isfinite(uo.wage_h.values.astype(float)), uo.wage_h.values.astype(float), wfb) * wf[pos]
    uo2 = pd.DataFrame({"unit_id": uo.unit_id, "h": hours_new, "c": hours_new * wage_new})
    agg = uo2.groupby("unit_id").agg(h=("h", "sum"), c=("c", "sum"))
    hours = agg.h.reindex(U.unit_id).fillna(0.0).values
    cost = agg.c.reindex(U.unit_id).fillna(0.0).values
    # activity time-share noise (Dirichlet-like, renormalized within each function)
    fh = U.groupby("function_id").hours.transform("sum").values
    conc = np.where(U.tier4.values > 0, mc.conc_activity_tier4, mc.conc_activity_prior)
    # O*NET task content transfers imperfectly outside the U.S. (labor notes 3.5): widen the dispersion of the
    # time shares by onet_widening in proportion to the non-U.S. share of staff (prior shares only)
    non_us = float((point.org.get("jurisdiction") or {}).get("non_us_share", 0.0))
    kw = 1.0 + (float(p.location.onet_widening) - 1.0) * non_us
    conc = np.where(U.tier4.values > 0, conc, conc / kw ** 2)
    alpha_ = np.maximum(conc * U.hours.values / np.maximum(fh, 1e-9), 0.02)
    act = rng.gamma(alpha_) / alpha_
    ins = (U.baseline == "H").values
    ah = hours * np.where(ins, act, 1.0)
    for f in fids:
        m = (U.function_id.values == f) & ins
        if m.any() and ah[m].sum() > 0:
            ah[m] *= hours[m].sum() / ah[m].sum()
    wage = np.where(hours > 0, cost / np.maximum(hours, 1e-12), U.wage_h.values)
    # process volumes: process steps scale with volume; the function's residual work absorbs the change
    vol_given = set(ing.volumes.process_id) if t3v else set()
    pf = {pid: float(np.exp(rng.normal(0, mc.sd_volume_tier3 if pid in vol_given else mc.sd_volume_prior)))
          for pid in P.process_id}
    vfac = U.process_id.map(pf).fillna(1.0).values
    is_proc = (U.kind == "process").values
    new_h = ah.copy()
    new_h[is_proc] = ah[is_proc] * np.minimum(vfac[is_proc], 1.6)
    for f in fids:
        m_f = U.function_id.values == f
        d = (new_h[m_f & is_proc] - ah[m_f & is_proc]).sum()
        r = m_f & (U.kind == "residual").values
        if r.any() and new_h[r].sum() > 0:
            new_h[r] = np.maximum(new_h[r] - d * new_h[r] / new_h[r].sum(), 0.0)
    if (not t2) and ing.financials.headcount:
        s = U.hours[ins].sum() / max(new_h[ins].sum(), 1e-9)
        new_h[ins] *= s
        wage[ins] /= s
    out = U.copy()
    out["hours"] = new_h
    out["wage_h"] = wage
    out["v"] = np.where(is_proc, U.v.values * vfac, new_h / np.maximum(U.t.values, 1e-9))
    out["t"] = np.where(is_proc & (out.v > 0), new_h / np.maximum(out.v.values, 1e-9), U.t.values)
    out["d"] = np.where(is_proc, out.t.values, U.d.values)
    if (U.baseline == "O").any():
        o = (U.baseline == "O").values
        out.loc[o, "vendor_spend"] = U.vendor_spend.values[o] * np.exp(rng.normal(0, 0.03, o.sum()))
    out["base_cost"] = np.where(out.baseline == "O", out.vendor_spend, out.hours * out.wage_h)
    out["fte"] = out.hours / p.labor.hours_per_fte
    sd_i = mc.sd_iota_tier3 if t3s else mc.sd_iota_prior
    inoise = dict(zip(fids, rng.normal(0, sd_i, nf)))
    P["iota0"] = np.clip(P.iota0 + P.function_id.map(inoise).fillna(0.0), 0.02, 0.98)
    P["volume"] = P.volume * P.process_id.map(pf).fillna(1.0)
    P["hours"] = P.process_id.map(out.groupby("process_id").hours.sum())
    P["fte"] = P.hours / p.labor.hours_per_fte
    org, _ = _org_inputs(ing, p, rng, nf)
    for k, v in point.org.items():          # inputs and derived terms that are not drawn
        if k not in org or k in ("severance_months", "jurisdiction"):
            org[k] = v
    f2 = Firm(name=point.name, base_year=point.base_year, fin=point.fin, part1=point.part1, functions=point.functions,
              units=out, unit_occ=point.unit_occ, processes=P, edges=point.edges, org=org, provenance=point.provenance,
              gaps=point.gaps, tiers=point.tiers, is_draw=True, products=point.products,
              product_occupations=point.product_occupations, ai_features=point.ai_features,
              security=point.security, regime=point.regime, jurisdictions=point.jurisdictions, staffing=point.staffing)
    return f2
