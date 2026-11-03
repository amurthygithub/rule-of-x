# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Labor law, talent and jurisdiction (part2/theory_labor.tex, sec:labor; notes/labor_notes.md; spec 24.5, 24.6).

Builds the per-site table of statutory terms (collective-procedure triggers, legal leads, technology consultation,
severance floors and notice), data-residency restrictions by function, the location wage index, and the program
checks the people plan and roadmap report: survivor quits and backfills, the redeployment bound, engineering
capacity, hire-or-contract, the pace bound (cor:labor-pace) and the cutover streams. The statutory rules are model
constraints as read at their primary sources on 29 October 2026, not legal advice; rules that could not be
confirmed at a primary source are flagged as unverified in every output that uses them."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from . import formulas as F

COUNTRY_NAMES = {"UNITED STATES": "US", "USA": "US", "U.S.": "US", "AMERICA": "US", "UNITED KINGDOM": "UK", "GREAT BRITAIN": "UK",
                 "GB": "UK", "ENGLAND": "UK", "SCOTLAND": "UK", "WALES": "UK", "GERMANY": "DE", "DEUTSCHLAND": "DE", "FRANCE": "FR",
                 "INDIA": "IN", "CHINA": "CN", "JAPAN": "JP", "POLAND": "PL", "MEXICO": "MX", "IRELAND": "IE", "NETHERLANDS": "NL",
                 "SPAIN": "ES", "ITALY": "IT", "CANADA": "CA", "BRAZIL": "BR", "PHILIPPINES": "PH", "SWITZERLAND": "CH"}
REGION_CODE = {"EU": "EU", "UK": "UK", "US": "US", "IN": "IN", "PH": "PH", "CA": "CA", "LATAM": "MX"}
# EU adequacy decisions (Commission adequacy page, 29 Oct 2026: 17 entries; the U.S. only for DPF participants).
# Only long-standing country decisions are encoded; other destinations need a mechanism.
ADEQUATE_FOR_EU = {"UK", "CH", "JP", "KR", "CA", "NZ", "IL", "AR", "UY", "AD", "FO", "GG", "IM", "JE"}


def country_code(country, site="", region="") -> str:
    c = str(country or "").strip().upper()
    if c in ("", "NAN", "NONE"):
        c = str(region or "").strip().upper()
        return REGION_CODE.get(c, c or "US")
    if c in COUNTRY_NAMES:
        return COUNTRY_NAMES[c]
    if c == "GB":
        return "UK"
    return c[:2] if len(c) > 3 else c


def zone(code: str) -> str:
    """Data-protection zone of a country code: EU (EEA), UK, US, CN, IN or other."""
    if code in F.EU_EEA or code == "EU":
        return "EU"
    return code if code in ("UK", "US", "CN", "IN") else "other"


def _get(row, k, default=None):
    v = row.get(k, default) if isinstance(row, dict) else getattr(row, k, default)
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return default
    return v


def site_table(sites: pd.DataFrame, p, org: dict, employer_headcount: float, roster_tenure: float | None = None) -> pd.DataFrame:
    """Statutory terms per site (tab:labor-rules) with the trigger test at the prior program dismissal share (the
    people plan re-tests with planned separations), the severance per displaced FTE max(floor, plan) plus pay in
    lieu of notice when staff are released early, and the residency attributes."""
    lb, jd = p.labor, p.jurisdiction
    rows = []
    sev_plan_prior = {"US": p.transition.severance_months_US, "UK": p.transition.severance_months_UK,
                      "EU": p.transition.severance_months_EU}
    release = bool(org.get("release_early") if org.get("release_early") is not None else lb.release_early)
    for r in sites.to_dict("records"):
        code = country_code(r.get("country"), r.get("site"), r.get("region"))
        z = zone(code)
        hc = float(_get(r, "headcount", 0.0))
        emp = float(_get(r, "employer_country_headcount", 0.0) or 0.0) or float(
            sites[[country_code(c, s, g) == code for c, s, g in zip(sites.get("country", ""), sites.site, sites.get("region", ""))]].headcount.sum())
        emp = max(emp, hc)
        if code == "US":
            emp = max(emp, float(employer_headcount or 0.0) * (hc / max(float(sites.headcount.sum()), 1e-9)))
        tenure = float(_get(r, "tenure_mean", None) or roster_tenure or lb.tenure_default)
        age = float(_get(r, "age_mean", None) or lb.age_default)
        wc = float(_get(r, "works_council", 0.0) or 0.0) >= 0.5
        n_dis = hc * float(lb.dismissal_share_prior)
        st = F.statutory_terms(code if code != "EU" else "EU_GENERIC", _get(r, "subnational", "") or "", hc, emp, n_dis, tenure, age, wc,
                               lb.T_proc_DE, lb.T_tech_DE, lb.T_tech_FR, False, lb.eu_option,
                               str(_get(r, "india_site_type", "") or "") in ("factory", "mine", "plantation"))
        if code == "EU":                    # region known, member state not: the Directive minimum plus a works-council prior
            trig = F.eu_collective(hc, n_dis, n_dis, lb.eu_option)
            st.update(triggered=trig, T_leg=(30.0 / 365.0 if trig else 0.0) + float(_get(r, "works_council", jd.eu_works_council_prior)) * jd.works_council_months / 12.0,
                      contemplation_zero=True, rule="Directive 98/59/EC minimum; member state unknown (works-council prior)",
                      unverified=["EU site without a member state: national rules not modeled"])
        union = float(_get(r, "union_coverage", 0.0) or 0.0)
        if z not in ("EU", "UK") and union > 0:      # effects bargaining where a union covers the roles (class d)
            st["T_leg"] += union * jd.union_months / 12.0
        plan_m = _get(r, "severance_plan_months", None)
        plan_m = float(plan_m) if plan_m is not None else float(sev_plan_prior.get(z if z in ("US", "UK", "EU") else "", p.transition.severance_months_other))
        sev = max(float(st["floor_months"]), plan_m) + (float(st["notice_months"]) if release else 0.0)
        rows.append({"site": r.get("site"), "country": code, "zone": z, "region": r.get("region", z), "headcount": hc,
                     "function_id": r.get("function_id"), "employer_headcount": emp, "tenure": tenure, "age": age,
                     "works_council": float(wc), "union_coverage": union,
                     "data_residency": str(_get(r, "data_residency", "none") or "none"),
                     "transfer_mechanism": str(_get(r, "transfer_mechanism", "") or ""),
                     "cn_subjects_per_year": _get(r, "cn_subjects_per_year", None), "ciio": float(_get(r, "ciio", 0.0) or 0.0),
                     "wage_index": _get(r, "wage_index", None),
                     "triggered_prior": bool(st["triggered"]), "T_leg": float(st["T_leg"]), "T_tech": float(st["T_tech"]),
                     "floor_months": float(st["floor_months"]), "notice_months": float(st["notice_months"]),
                     "plan_months": plan_m, "severance_months": sev, "contemplation_zero": bool(st["contemplation_zero"]),
                     "rule": st["rule"], "unverified": " | ".join(st["unverified"]),
                     "sozialplan_enforceable": st.get("sozialplan_enforceable")})
    df = pd.DataFrame(rows)
    df["share"] = df.headcount / max(float(df.headcount.sum()), 1e-9)
    return df


def residency_by_site(df: pd.DataFrame, p, org: dict) -> pd.DataFrame:
    """Data-residency status of each site's personal data for the AI vendor's regions (prop:labor-residency; labor
    notes 3.6): in-region (usable at the regional premium), transfer under a mechanism (usable; mechanism cost and
    invalidation hazard), free, or restricted (unusable for AI). Firm-declared residency (region or country) is
    usable only in-region."""
    rs = p.residency
    vend = org.get("vendor_regions")
    regions = {x.strip().upper() for x in (str(vend).replace(",", ";").split(";") if vend else rs.vendor_regions) if str(x).strip()}
    dpf = bool(org.get("vendor_dpf_certified") if org.get("vendor_dpf_certified") is not None else rs.vendor_dpf_certified)
    status, nu, cost, notes = [], [], [], []
    for r in df.itertuples(index=False):
        z, mech = r.zone, (r.transfer_mechanism or rs.transfer_mechanism or "none").lower()
        in_region = (z in regions) or (z == "EU" and "EU" in regions)
        declared = r.data_residency in ("region", "country")
        if in_region:
            status.append("in_region"); nu.append(0.0); cost.append(0.0); notes.append("")
            continue
        if declared:
            status.append("restricted"); nu.append(0.0); cost.append(0.0)
            notes.append("firm requires in-region processing; vendor has no region here")
            continue
        if z in ("EU", "UK"):
            vz = sorted(regions)
            adequate = any(v in ADEQUATE_FOR_EU for v in vz) or (z == "UK" and "EU" in regions)
            if adequate:
                status.append("free"); nu.append(0.0); cost.append(0.0); notes.append("adequacy decision")
            elif "US" in regions and (dpf or mech == "dpf"):
                status.append("mechanism"); nu.append(rs.nu_inv_EU_US); cost.append(0.0); notes.append("EU-U.S. Data Privacy Framework (invalidation hazard)")
            elif mech in ("scc", "bcr"):
                status.append("mechanism"); nu.append(rs.nu_inv_SCC); cost.append(float(org.get("transfer_cost") or rs.F_tr))
                notes.append(f"{mech.upper()} with a transfer impact assessment")
            else:
                status.append("restricted"); nu.append(0.0); cost.append(0.0)
                notes.append("GDPR Chapter V: no adequacy, framework or safeguard for the vendor's region (Art. 49 derogations are not a basis)")
            continue
        if z == "CN":
            subj = r.cn_subjects_per_year
            if r.ciio >= 0.5:
                status.append("restricted"); nu.append(0.0); cost.append(0.0); notes.append("PIPL: a CIIO must store personal information in China")
            elif subj is not None and float(subj) < rs.cn_threshold_exempt:
                status.append("free"); nu.append(0.0); cost.append(0.0); notes.append("PIPL: below 100,000 non-sensitive subjects, exempt")
            elif mech in ("cn_contract", "cn_assessment"):
                status.append("mechanism"); nu.append(0.0); cost.append(float(org.get("transfer_cost") or rs.F_tr)); notes.append(f"PIPL {mech}")
            else:
                status.append("restricted"); nu.append(0.0); cost.append(0.0)
                notes.append("PIPL: standard contract, certification or security assessment needed")
            continue
        if z == "IN":
            status.append("free"); nu.append(0.0); cost.append(0.0)
            notes.append("DPDP Act s.16: no country notified; sectoral localization (payments) not modeled (unverified)")
            continue
        status.append("free"); nu.append(0.0); cost.append(0.0); notes.append("")
    out = df[["site", "country", "zone", "headcount", "share", "function_id"]].copy()
    out["residency_status"], out["nu_inv"], out["F_tr"], out["residency_note"] = status, nu, cost, notes
    return out


def function_view(df: pd.DataFrame, res: pd.DataFrame, function_ids) -> dict:
    """Per function: site shares (sites serving the function, else all), with lead times, severance and the
    restricted share of personal data (omega^res) and the in-region share."""
    out = {}
    for f in function_ids:
        m = (df.function_id.astype(str) == str(f)).values if "function_id" in df.columns else np.zeros(len(df), bool)
        if not m.any():
            m = df.function_id.isna().values | (df.function_id.astype(str).isin(["", "None", "nan"])).values
        if not m.any():
            m = np.ones(len(df), bool)
        w = df.headcount.values * m
        w = w / max(w.sum(), 1e-9)
        st = res.residency_status.values
        out[str(f)] = {"share": w, "T_leg": df.T_leg.values, "T_tech": df.T_tech.values, "cont0": df.contemplation_zero.values,
                       "severance_months": float(np.sum(w * df.severance_months.values)),
                       "omega_res": float(np.sum(w * (st == "restricted"))), "in_region": float(np.sum(w * (st == "in_region"))),
                       "zone": df.zone.values}
    return out


def build(ing, hc: pd.DataFrame, p, priors, org: dict, employer_headcount: float, function_ids) -> tuple[dict, pd.DataFrame]:
    """Site table, residency and the per-function view used by plans.py. Uses tier3_jurisdictions when given;
    otherwise one pseudo-site per region of the roster (works-council and union priors, class d)."""
    from .impute import _region_of
    j = p.jurisdiction
    if getattr(ing, "jurisdictions", None) is not None:
        sites = ing.jurisdictions.copy()
        sites["region"] = [_region_of(c, s, priors) for c, s in zip(sites.country.fillna(""), sites.site)]
        src = "tier3_jurisdictions"
    else:
        reg = hc.groupby("region").fte.sum() if len(hc) else pd.Series({"US": 1.0})
        sites = pd.DataFrame({"site": [f"all {r} staff" for r in reg.index], "country": [""] * len(reg),
                              "headcount": reg.values.astype(float), "region": list(reg.index)})
        sites["works_council"] = np.where(sites.region == "EU", j.eu_works_council_prior, 0.0)
        sites["union_coverage"] = [float(j.union_prior.get(r, j.union_prior.get("other", 0.1))) for r in sites.region]
        sites["data_residency"] = "none"
        src = "prior: regions of the roster (class d works-council and union priors)"
    df = site_table(sites, p, org, employer_headcount)
    res = residency_by_site(df, p, org)
    df = df.merge(res[["site", "residency_status", "nu_inv", "F_tr", "residency_note"]], on="site", how="left")
    wi = p.location.wage_index_default
    from .ingest import wage_index as _loc_index
    used, srcs = [], []
    for x, c, site in zip(df.wage_index, df.country, df.site):
        if x is not None and np.isfinite(float(x)):
            used.append(float(x)); srcs.append("input")
        elif c in wi:
            used.append(float(wi[c])); srcs.append("OECD average wage")
        else:
            used.append(float(_loc_index(f"{c} {site}", priors.locations)[0])); srcs.append("engine location prior")
    df["wage_index_used"], df["wage_index_source"] = used, srcs
    w = df.share.values
    fv = function_view(df, df, function_ids)
    unver = sorted({u for s in df.unverified for u in str(s).split(" | ") if u})
    out = {"notice_years": float(np.sum(w * df.T_leg.values)), "notice_years_max": float(df.T_leg.max()) if len(df) else 0.0,
           "T_tech_mean": float(np.sum(w * df.T_tech.values)),
           "works_council_share": float(np.sum(df.works_council.values * w)), "union_share": float(np.sum(df.union_coverage.values * w)),
           "residency_share": float(np.sum(w * (df.residency_status.values == "restricted"))),
           "in_region_share": float(np.sum(w * (df.residency_status.values == "in_region"))),
           "mechanism_annual_cost": float(np.sum(df.nu_inv.values * p.residency.C_sw)),
           "mechanism_first_year_cost": float(df.F_tr.sum()),
           "severance_months": float(np.sum(w * df.severance_months.values)), "source": src, "unverified": unver,
           "rules_as_of": str(p.labor.rules_as_of), "by_function": fv,
           "non_us_share": float(np.sum(w * (df.zone.values != "US")))}
    return out, df


# -------------------------------------------------------------------------------------------------
# Program checks for the people plan and the roadmap
# -------------------------------------------------------------------------------------------------
def retest_triggers(sites: pd.DataFrame, separations_by_year: np.ndarray, p) -> pd.DataFrame:
    """Re-run the trigger tests with planned separations by year, allocated to sites by headcount share (all
    program dismissals at an establishment in a window are counted together unless sub-threshold pacing is on)."""
    rows = []
    for y, n in enumerate(np.asarray(separations_by_year, float)):
        if n <= 0:
            continue
        for r in sites.itertuples(index=False):
            nd = float(n) * float(r.share)
            if nd < 0.5:
                continue
            st = F.statutory_terms(r.country if r.country != "EU" else "EU_GENERIC", "", r.headcount, r.employer_headcount, nd, r.tenure,
                                   r.age, r.works_council >= 0.5, p.labor.T_proc_DE, p.labor.T_tech_DE, p.labor.T_tech_FR,
                                   False, p.labor.eu_option)
            if r.country == "EU":
                st["triggered"] = F.eu_collective(r.headcount, nd, nd, p.labor.eu_option)
            rows.append({"plan_year": y, "site": r.site, "country": r.country, "separations": nd, "triggered": bool(st["triggered"]),
                         "triggered_prior": bool(r.triggered_prior), "rule": r.rule, "lead_years": float(r.T_leg),
                         "severance_months": float(r.severance_months), "unverified": r.unverified})
    return pd.DataFrame(rows)


def pacing_span(n_dis: float, country: str, p) -> float | None:
    """Days of sub-threshold pacing needed to stay below the collective threshold (prop:labor-lead(c)); None where
    no window rule is modeled."""
    thr = {"UK": (20, 90), "DE": (30, 30), "US": (50, 30)}.get(country)
    if thr is None or n_dis <= 0:
        return None
    return float(F.min_pacing_span(n_dis, thr[0], thr[1]))


def survivors(econ, sol, prog, p) -> dict:
    """Extra quits among survivors per announced wave (prop:labor-survivor(a,b)) and their backfill hires."""
    lb = p.labor
    cols = prog.cols
    T = econ.T
    fte_tot = float(econ.firm.units.fte.sum())
    waves = sorted({int(cols.start[c]) for c in sol.sel.values()})
    nu_s = float(lb.survivor_excess_quits) / max(float(lb.T_s), 1e-9)
    quits = np.zeros(T)
    for y in waves:
        procs = [c for c in sol.sel.values() if int(cols.start[c]) == y]
        funcs = {str(econ.firm.processes.function_id.iat[int(cols.proc[c])]) for c in procs}
        Uf = econ.firm.units[econ.firm.units.function_id.astype(str).isin(funcs) & (econ.firm.units.baseline == "H")]
        removed = float(sum(cols.detail[c]["fte_removed"] * float(sol.varpi[c]) for c in procs))
        _, n_sv, _ = F.survivor_base(float(Uf.fte.sum()), removed)          # in-house staff of the touched functions
        quits[y] += float(F.survivor_quits(float(n_sv), lb.nu_q, nu_s, lb.T_s))
    return {"extra_quits_by_year": quits, "backfill_hires_by_year": quits.copy(), "waves": waves,
            "baseline_quits_per_year": fte_tot * float(lb.nu_q)}


def redeployment_check(econ, sol, prog, p, sep_by_year: np.ndarray, u_d: float, T_w: float) -> dict:
    """Program-level redeployment bound u_d <= min{1, varpi^rd nu^q N^oth T^w / N^dis} (prop:labor-survivor(e))."""
    lb = p.labor
    n_dis = float(np.sum(sep_by_year))
    n_oth = max(float(econ.firm.units.fte.sum()) - n_dis, 0.0)
    cap = float(F.redeployment_cap(lb.varpi_rd, lb.nu_q, n_oth, max(T_w, 0.25) * max(len([y for y in sep_by_year if y > 0]), 1), max(n_dis, 1e-9))) \
        if n_dis > 0 else 1.0
    return {"u_d": u_d, "cap": cap, "binds": bool(u_d > cap + 1e-9), "attrition_years_to_shed_10pct": math.log(1 / 0.9) / lb.nu_q}


def talent(econ, sol, prog, p, team: pd.DataFrame, hc: pd.DataFrame | None, org: dict) -> dict:
    """Engineering talent (prop:labor-talent): loaded AI engineer wage, maintenance ceiling Gamma/e_mnt, time to
    bring the plan's automated processes into run mode, the hiring path with its lead, and hire or contract."""
    tl, o = p.talent, p.org
    hpf = p.labor.hours_per_fte
    w_ai = float(econ.rates.get("ai_engineer_year") or F.ai_engineer_wage(p.build.ai_engineer_base_wage, tl.premium, p.labor.tau_L))
    soc_ai = {"15-1252", "15-2051", "15-1221", "15-2041"}
    g0 = org.get("ai_engineers_in_house")
    if g0 is None and hc is not None and len(hc):
        g0 = float(hc[hc.soc.astype(str).str[:7].isin(soc_ai)].fte.sum()) * float(tl.ai_share_of_developers)
    g0 = float(g0 or 0.0)
    h = org.get("ai_engineer_hires_per_year")
    head = float(econ.firm.fin.get("headcount") or econ.firm.units.fte.sum())
    h = float(h) if h is not None else float(tl.hires_per_1000) * head / 1000.0
    need = team["ai_agent_engineers"].values if "ai_agent_engineers" in team.columns else np.zeros(econ.T)
    N_auto = int(team["automated_processes_running"].max()) if len(team) else 0
    e_mnt = float(org.get("ai_engineers_per_process") or o.e_mnt)
    gamma_max = g0 + h * max(econ.T - tl.T_lead, 0.0)
    T_gamma = F.time_to_scope(N_auto, max(gamma_max, 1e-9), o.e_bld, e_mnt) if N_auto else 0.0
    avail = np.array([g0 + h * max(y + 1 - tl.T_lead, 0.0) for y in range(econ.T)])
    gap = np.maximum(need - avail, 0.0)
    dG = float(gap.max()) if len(gap) else 0.0
    T_need = float(np.sum(gap > 0))
    W_hat = float(np.median([prog.cols.detail[c]["W"][-1] for c in sol.sel.values()])) if sol.sel else 0.0
    thr = F.contract_threshold(tl.delta_rp, tl.T_rp, tl.c_hire_weeks / 52.0, W_hat, tl.T_lead, tl.T_ct_months / 12.0,
                               max(dG, 1.0), w_ai, tl.u_ct)
    return {"w_AI": w_ai, "w_SE": float(p.build.ai_engineer_base_wage), "premium": float(tl.premium), "Gamma0": g0,
            "hires_per_year": h, "hiring_lead_years": float(tl.T_lead), "need_by_year": need, "available_by_year": avail,
            "gap_by_year": gap, "ceiling_processes": (gamma_max / e_mnt) if e_mnt > 0 else math.inf,
            "processes_automated": N_auto, "time_to_scope_years": T_gamma, "contract_threshold_years": thr,
            "gap_years": T_need, "contract": bool(dG > 0 and T_need < thr),
            "e_bld": float(o.e_bld), "e_mnt": e_mnt}


def pace(econ, sol, prog, p, tal: dict) -> dict:
    """Pace bound on the program (cor:labor-pace): T_prog >= max{N a/K_chg, N e T^eff/(x-hat Phi), T_Gamma(N)},
    with T^eff the mean cutover time of a wave including legal leads."""
    cols = prog.cols
    sel = list(sol.sel.values())
    N = len(sel)
    if N == 0:
        return {"bounds": {}, "binding": None, "T_eff": 0.0, "N": 0}
    a = float(np.mean([cols.detail[c]["affected"] for c in sel]))
    K_chg = float(np.mean(prog.capacity)) if np.ndim(prog.capacity) else float(prog.capacity)
    e = float(p.decisions.e_launch)
    T_eff = float(np.mean([cols.detail[c]["T_par"] for c in sel]))
    Phi = float(np.mean(prog.Phi)) if np.ndim(prog.Phi) else float(prog.Phi)
    x_hat = float(prog.info.get("x_hat", 1.0))
    b, bind = F.pace_bound(N, a, K_chg, e, T_eff, x_hat, Phi, tal.get("time_to_scope_years", 0.0))
    return {"bounds": b, "binding": bind, "T_eff": T_eff, "N": N, "affected_per_process": a}


def streams(econ, sol, prog, sites: pd.DataFrame, p) -> list[dict]:
    """Cutover streams per wave (prop:labor-lead(b)): jurisdictions sorted by t^dis = max{t^gate, T^leg} (procedure
    started at the decision), grouped by dynamic programming against the wave overhead O_w."""
    cols = prog.cols
    out = []
    for y in sorted({int(cols.start[c]) for c in sol.sel.values()}):
        procs = [c for c in sol.sel.values() if int(cols.start[c]) == y]
        Tp = float(np.mean([cols.detail[c]["T_par"] for c in procs]))
        Wsum = float(sum(max(cols.detail[c]["W"][-1], 0.0) for c in procs))
        tD = np.maximum(Tp + sites.T_tech.values, sites.T_leg.values)
        groups, cost = F.stream_partition(tD, sites.share.values * Wsum, float(prog.O_w))
        out.append({"plan_year": y, "streams": [[str(sites.site.iat[i]) for i in g] for g in groups],
                    "cutover_years": [float(max(tD[i] for i in g)) for g in groups], "waiting_cost": cost})
    return out


def location(sites: pd.DataFrame, p) -> pd.DataFrame:
    """Site wage index and the lower bound on the adoption lag relative to the U.S., ln(1/w)/delta_pi
    (lem:labor-location with c^fx = 0)."""
    dpi = float(p.prices.delta_pi)
    w = sites.wage_index_used.values.astype(float)
    lag = np.where(w < 1, np.log(1 / np.maximum(w, 1e-9)) / dpi, 0.0)
    return pd.DataFrame({"site": sites.site, "country": sites.country, "wage_index": w, "wage_index_source": sites.wage_index_source,
                         "adoption_lag_lower_bound_years": lag})
