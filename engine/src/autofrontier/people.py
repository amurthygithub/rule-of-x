# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""The people plan (spec 7, 9, 24.5, 24.6; ext def:ext-org, lem:ext-staffing, prop:ext-team, prop:ext-hierarchy).

- Residual organization at the end of the plan: hours left by function and occupation (from the chosen modes),
  FTE by seniority, review and sign-off at an expertise wage, managers at the AI-widened span, layers, and an
  apprenticeship-gap flag when junior production work disappears faster than senior work (modern map change 6).
- Transformation team by year with the sizing rules of lem:ext-staffing (data and integration engineers, AI
  engineers in build and run mode, process owners, change managers, risk and governance, domain experts,
  security reviewers, program managers), using the firm's own team ratios when given. Hiring needs net of
  redeployment, with lead times and the AI talent premium.
- Separations by year and site with notice and consultation timing (WARN, EU collective redundancy, works councils,
  unions), severance by region, survivor attrition and the jurisdictions where a notice is triggered.
Class d sizing ratios are reported as scenario values with their ranges."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from . import formulas as F

H, O, U, A, N = F.H, F.O, F.U, F.A, F.N
SENIORITY = ("junior", "mid", "senior", "manager", "director", "executive")
DEFAULT_MIX = {"junior": 0.2, "mid": 0.45, "senior": 0.2, "manager": 0.1, "director": 0.03, "executive": 0.02}


def _seniority_mix(ing, firm) -> dict:
    """Seniority mix by function from the roster (Tier 2), else a default mix (assumed)."""
    out = {}
    r = getattr(ing, "roster", None)
    if r is not None and len(r) and "seniority" in r:
        for f, g in r.groupby("function_id"):
            tot = float(g.fte.sum())
            out[f] = {s: float(g.fte[g.seniority == s].sum()) / tot for s in SENIORITY} if tot > 0 else dict(DEFAULT_MIX)
    for f in firm.functions.function_id:
        out.setdefault(f, dict(DEFAULT_MIX))
    return out


def residual_organization(econ, sol, prog, p, ing=None, year: int | None = None) -> dict:
    """Hours and FTE left by function, occupation and seniority at plan year `year` (default: last), managers at the
    widened span, and the apprenticeship-gap flag."""
    T = econ.T
    y = T - 1 if year is None else year
    firm = econ.firm
    Ut = firm.units
    hpf = p.labor.hours_per_fte
    modes = econ.base_mode.copy()
    level = np.zeros(econ.nU, int)
    live = np.zeros(econ.nU, bool)
    for c in sol.sel.values():
        us = np.flatnonzero(econ.unit_proc == prog.cols.proc[c])
        if prog.cols.tau0[c] <= y + 1:
            modes[us] = np.asarray(prog.cols.modes[c])
            level[us] = int(prog.cols.level[c])
            live[us] = True
    v = Ut.v.values.astype(float)                        # today's volume, so FTE compare with today's headcount
    res_new = econ.res_hours[np.arange(econ.nU), level, y, modes] * v
    res_old = econ.res_hours[np.arange(econ.nU), 0, y, econ.base_mode] * v
    inhouse = econ.base_mode == H
    res_new = np.where(np.isfinite(res_new), res_new, res_old)
    # review and sign-off hours under automation are senior work (expertise-adjusted review wage, w^R >= w)
    review_h = np.where(modes == A, res_new, 0.0)
    uo = firm.unit_occ
    pos = {uid: i for i, uid in enumerate(Ut.unit_id.values)}
    by_soc = []
    for uid, g in uo.groupby("unit_id"):
        tot = float(g.hours.sum())
        if tot <= 0 or uid not in pos:
            continue
        sh = g.hours.values / tot
        for s, w_ in zip(g.soc.values, sh):
            by_soc.append((pos[uid], s, w_))
    occ = pd.DataFrame(by_soc, columns=["unit", "soc", "share"])
    occ["function_id"] = Ut.function_id.values[occ.unit.values]
    occ["fte_before"] = res_old[occ.unit.values] * inhouse[occ.unit.values] * occ.share / hpf
    occ["fte_after"] = res_new[occ.unit.values] * inhouse[occ.unit.values] * occ.share / hpf
    occ["review_fte_after"] = review_h[occ.unit.values] * inhouse[occ.unit.values] * occ.share / hpf
    by_occ = occ.groupby(["function_id", "soc"], as_index=False)[["fte_before", "fte_after", "review_fte_after"]].sum()
    mix = _seniority_mix(ing, firm)
    rows = []
    org = p.org
    gaps = []
    for f, g in by_occ.groupby("function_id"):
        before, after, rev = float(g.fte_before.sum()), float(g.fte_after.sum()), float(g.review_fte_after.sum())
        m = mix.get(f, DEFAULT_MIX)
        # removed work is production work, mostly junior and mid; review and sign-off stay senior
        prod_before = {s: before * m[s] for s in SENIORITY}
        cut = max(before - after, 0.0)
        prod_share = {"junior": 0.45, "mid": 0.4, "senior": 0.15}
        tot_prod = sum(prod_before[s] for s in prod_share)
        after_s = dict(prod_before)
        for s, w_ in prod_share.items():
            take = min(prod_before[s], cut * w_ / max(sum(prod_share.values()), 1e-9))
            after_s[s] = prod_before[s] - take
        share_auto = cut / max(before, 1e-9)
        span = org.span_base * (1.0 + org.span_ai_uplift * share_auto)
        ics = sum(after_s[s] for s in ("junior", "mid", "senior"))
        mgr = F.managers_for(ics, span)
        mgr_before = F.managers_for(tot_prod, org.span_base)
        junior_loss = 1 - after_s["junior"] / max(prod_before["junior"], 1e-9) if prod_before["junior"] > 0 else 0.0
        senior_loss = 1 - after_s["senior"] / max(prod_before["senior"], 1e-9) if prod_before["senior"] > 0 else 0.0
        gap = bool(junior_loss > 0.5 and junior_loss > senior_loss + 0.25)
        if gap:
            gaps.append(f)
        rows.append({"function_id": f, "function_name": firm.functions.set_index("function_id").function_name.get(f, f),
                     "fte_before": before, "fte_after": after, "fte_change": after - before, "review_and_signoff_fte": rev,
                     **{f"{s}_after": after_s[s] for s in ("junior", "mid", "senior")},
                     "span_before": org.span_base, "span_after": span, "managers_before": mgr_before, "managers_after": mgr,
                     "layers_after": F.hierarchy_layers(ics, span), "junior_loss_share": junior_loss,
                     "apprenticeship_gap": gap})
    fn = pd.DataFrame(rows).sort_values("fte_change").reset_index(drop=True) if rows else pd.DataFrame()
    top_occ = by_occ.assign(change=by_occ.fte_after - by_occ.fte_before).sort_values("change").head(15)
    return {"by_function": fn, "by_occupation": top_occ, "year": int(firm.base_year + y), "volume_basis": "today's volumes",
            "apprenticeship_gap_functions": gaps,
            "totals": {"fte_before": float(fn.fte_before.sum()) if len(fn) else 0.0,
                       "fte_after": float(fn.fte_after.sum()) if len(fn) else 0.0},
            "note": "seniority split of removed work is an assumption (production work is mostly junior and mid); spans and "
                    "the AI uplift are class d (org.span_ai_uplift)"}


def transformation_team(econ, sol, prog, p) -> pd.DataFrame:
    """Team by plan year (lem:ext-staffing), with the firm's own ratios where given."""
    T = econ.T
    org_in = econ.firm.org
    o = p.org
    rates = econ.rates
    hpf = p.labor.hours_per_fte
    e_PO = float(org_in.get("process_owners_per_process") or o.e_PO)
    e_SME = float(org_in.get("sme_fte_per_process") or o.e_SME)
    e_mnt = float(org_in.get("ai_engineers_per_process") or o.e_mnt)
    N_CM = float(org_in.get("affected_fte_per_change_manager") or o.N_CM)
    rows = []
    cols = prog.cols
    sel = list(sol.sel.values())
    for y in range(T):
        I_k = F_k = A_aff = 0.0
        n_red = n_reg = n_build = n_live = 0
        for c in sel:
            d = cols.detail[c]
            s, t0 = int(cols.start[c]), float(cols.tau0[c])
            end = t0 + d["T_par"]
            if s <= y < max(math.ceil(end), s + 1):
                I_k += d["I"] / max(math.ceil(end) - s, 1)
                F_k += d["F_build"] / max(math.ceil(end) - s, 1)
                A_aff += d["affected"] / max(math.ceil(end) - s, 1)
                n_red += 1
                n_reg += int(bool(cols.regulated[c]))
                n_build += 1
            if end <= y + 1 and (np.asarray(cols.modes[c]) == A).any():
                n_live += 1
        team = F.transformation_team(I_k, F_k, 1.0, n_live, n_red, A_aff, n_reg, n_build, rates["data_engineer_hour"],
                                     rates["ai_engineer_hour"], hpf, o.l_DI, o.l_AI, e_mnt, e_PO, N_CM, o.e_RG, e_SME)
        team = {k: float(v) for k, v in team.items()}
        team["security_reviewers"] = float(np.sum(cols.reviews[sel, y]) / max(p.security.reviews_per_fte, 1e-9)) if sel else 0.0
        team["program_managers"] = float(max(1.0, n_red / 6.0)) if n_red else 0.0
        team["year"] = int(econ.firm.base_year + y)
        team["processes_in_transition"] = n_red
        team["automated_processes_running"] = n_live
        rows.append(team)
    df = pd.DataFrame(rows)
    roles = [c for c in df.columns if c not in ("year", "processes_in_transition", "automated_processes_running")]
    df["total"] = df[roles].sum(axis=1)
    df.attrs["ratios"] = {"process_owners_per_process": e_PO, "smes_per_process": e_SME, "ai_engineers_per_running_process": e_mnt,
                          "affected_fte_per_change_manager": N_CM, "l_DI": o.l_DI, "l_AI": o.l_AI, "e_RG": o.e_RG,
                          "source": {k: ("firm input" if org_in.get(k2) else "default (class d)") for k, k2 in
                                     (("process_owners", "process_owners_per_process"), ("smes", "sme_fte_per_process"),
                                      ("ai_engineers", "ai_engineers_per_process"), ("change_managers", "affected_fte_per_change_manager"))}}
    return df


def hiring_plan(team: pd.DataFrame, separations: pd.DataFrame, p, econ, backfills: np.ndarray | None = None) -> pd.DataFrame:
    """Hires by year and role: the increase in each role's team size, net of redeployed staff (a share u_d of
    separations can fill process-owner, SME and change roles), started T^lead ahead (prop:labor-talent(c)), plus
    backfills for the survivors' extra quits (prop:labor-survivor(a)); AI and data engineers carry the talent
    premium."""
    lead = float(p.talent.T_lead)
    u_d = float(econ.firm.org.get("redeployment_share") or p.transition.u_d)
    roles = ["data_integration_engineers", "ai_agent_engineers", "process_owners", "change_managers", "risk_governance_audit",
             "domain_smes", "security_reviewers", "program_managers"]
    rows = []
    prev = {r: 0.0 for r in roles}
    for i, row in team.iterrows():
        year = int(row["year"])
        redeploy = float(separations.loc[separations.year == year, "separations"].sum()) * u_d / max(1 - u_d, 1e-9) if len(separations) else 0.0
        pool = redeploy
        for r in roles:
            need = max(float(row[r]) - prev[r], 0.0)
            from_inside = min(need, pool) if r in ("process_owners", "domain_smes", "change_managers") else 0.0
            pool -= from_inside
            rows.append({"year": year, "role": r, "added": need, "redeployed": from_inside, "external_hires": need - from_inside,
                         "start_hiring_by": year - lead,
                         "wage_premium": p.build.ai_engineer_premium if r in ("ai_agent_engineers", "data_integration_engineers") else 1.0})
            prev[r] = float(row[r])
        if backfills is not None:
            y = year - int(econ.firm.base_year)
            if 0 <= y < len(backfills) and backfills[y] > 0:
                rows.append({"year": year, "role": "survivor_backfills", "added": float(backfills[y]), "redeployed": 0.0,
                             "external_hires": float(backfills[y]), "start_hiring_by": year - lead, "wage_premium": 1.0})
    return pd.DataFrame(rows)


def separations(econ, sol, prog, p) -> tuple[pd.DataFrame, list[dict], pd.DataFrame]:
    """Separations by year (success path, expected FTE removed net of redeployment), severance per site at
    max(statutory floor, plan) (tab:labor-rules), survivor quits, and the collective procedures the planned
    separations trigger by site and year (all program dismissals at a site in a window counted together)."""
    from . import labor as LAB
    cols = prog.cols
    T = econ.T
    firm = econ.firm
    u_d = float(firm.org.get("redeployment_share") or p.transition.u_d)
    removed = np.zeros(T)
    for c in sol.sel.values():
        removed += cols.fte_removed[c] * float(sol.varpi[c])
    inc = np.diff(np.concatenate([[0.0], removed]))
    sep = np.maximum(inc, 0.0) * (1 - u_d)
    sites = firm.jurisdictions
    tests = LAB.retest_triggers(sites, sep, p) if sites is not None and len(sites) else pd.DataFrame()
    notices = []
    for r in tests.itertuples(index=False) if len(tests) else []:
        if r.triggered or r.lead_years > 0:
            notices.append({"year": int(firm.base_year + r.plan_year), "site": r.site, "country": r.country,
                            "separations": float(r.separations), "collective_procedure": bool(r.triggered),
                            "lead_years": float(r.lead_years), "rule": r.rule, "unverified": r.unverified,
                            "prior_test_differs": bool(r.triggered != r.triggered_prior)})
    wage = float(np.median(econ.info["w"])) * p.labor.hours_per_fte
    sev_m = float(firm.org.get("severance_months", p.transition.severance_months_US))
    sv = LAB.survivors(econ, sol, prog, p)
    df = pd.DataFrame({"year": firm.base_year + np.arange(T), "fte_removed_cumulative": removed, "separations": sep,
                       "redeployed": np.maximum(inc, 0.0) * u_d, "severance": sep * wage * sev_m / 12.0,
                       "survivor_extra_quits": sv["extra_quits_by_year"]})
    return df, notices, tests


def people_plan(econ, sol, prog, p, ing=None) -> dict:
    from . import labor as LAB
    team = transformation_team(econ, sol, prog, p)
    sep, notices, tests = separations(econ, sol, prog, p)
    sv = LAB.survivors(econ, sol, prog, p)
    hires = hiring_plan(team, sep, p, econ, backfills=sv["backfill_hires_by_year"])
    resid = residual_organization(econ, sol, prog, p, ing)
    jsum = dict(econ.firm.org.get("jurisdiction", {}))
    jsum.pop("by_function", None)
    sites = econ.firm.jurisdictions
    tal = LAB.talent(econ, sol, prog, p, team, econ.firm.staffing, econ.firm.org)
    pace = LAB.pace(econ, sol, prog, p, tal)
    u_d = float(econ.firm.org.get("redeployment_share") or p.transition.u_d)
    redeploy = LAB.redeployment_check(econ, sol, prog, p, sep.separations.values, u_d, jsum.get("notice_years", 0.0))
    strm = LAB.streams(econ, sol, prog, sites, p) if sites is not None and len(sites) else []
    loc = LAB.location(sites, p) if sites is not None and len(sites) else pd.DataFrame()
    ind = econ.firm.fin.get("_industry") or {}
    confidence = "low" if (ind and not ind.get("software", True)) else "standard"
    return {"residual": resid, "team": team, "hiring": hires, "separations": sep, "notices": notices, "trigger_tests": tests,
            "jurisdiction": jsum, "sites": sites, "survivors": sv, "talent": tal, "pace": pace, "redeployment": redeploy,
            "streams": strm, "location": loc, "people_cost_confidence": confidence,
            "unverified_rules": jsum.get("unverified", []),
            "class_d": ["org.e_PO", "org.e_RG", "org.e_SME", "org.l_DI", "org.l_AI", "org.N_CM", "org.e_bld",
                        "org.span_ai_uplift", "org.chi_h", "labor.delta_eff", "labor.nu_x", "labor.kappa_doc", "labor.varpi_rd",
                        "labor.c_ann_share", "labor.C_wd_share", "labor.T_proc_DE", "labor.T_tech_DE", "talent.delta_rp",
                        "talent.u_ct", "talent.hires_per_1000", "transition.u_d"]}
