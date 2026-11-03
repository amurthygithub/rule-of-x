# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Synthetic enterprise generator: a mid-market software firm of about 2,000 to 5,000 employees, built
from the priors and written in the input-tier format, so the whole pipeline can be exercised end to end.
All company, vendor and system names are fictional."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .config import find_data_dir, load_params
from .priors import Priors, load_priors

TITLE_VARIANTS = {
    "15-1252": ["Software Engineer", "Senior Software Engineer", "Staff Engineer", "Backend Engineer", "Software Engineer II", "Frontend Developer"],
    "15-1253": ["QA Engineer", "Senior QA Analyst", "Test Engineer"],
    "15-1255": ["UX Designer", "Senior Product Designer"],
    "15-2051": ["Data Scientist", "Senior Data Scientist"],
    "11-3021": ["Engineering Manager", "Director of Engineering", "IT Manager"],
    "15-1299": ["Site Reliability Engineer", "DevOps Engineer", "Platform Engineer"],
    "11-9199": ["Product Manager", "Senior Product Manager", "Program Manager"],
    "27-3042": ["Technical Writer"],
    "15-1212": ["Security Engineer", "Information Security Analyst"],
    "43-4051": ["Customer Support Representative", "Support Specialist", "Tier 1 Support Agent", "Customer Care Associate"],
    "15-1232": ["Technical Support Engineer", "Tier 2 Support Engineer", "IT Support Technician", "Help Desk Analyst"],
    "43-1011": ["Support Team Lead", "Support Supervisor"],
    "13-1151": ["Learning and Development Specialist", "Customer Enablement Trainer"],
    "43-9061": ["Office Clerk", "Data Entry Clerk"],
    "41-3091": ["Account Executive", "Sales Development Representative", "Senior Account Executive", "Renewals Manager"],
    "13-1199": ["Customer Success Manager", "Senior Customer Success Manager", "Revenue Operations Analyst", "Business Operations Analyst"],
    "11-2022": ["Sales Manager", "Regional Sales Director", "VP Sales"],
    "15-1211": ["Implementation Consultant", "Solution Consultant", "Business Analyst"],
    "13-1111": ["Management Consultant", "Strategy Manager"],
    "13-1082": ["Project Manager", "Delivery Manager"],
    "41-4011": ["Enterprise Account Executive", "Channel Sales Manager"],
    "41-9031": ["Sales Engineer", "Solutions Engineer"],
    "13-1161": ["Marketing Specialist", "Content Marketing Manager", "Demand Generation Specialist", "Product Marketing Manager"],
    "43-6014": ["Administrative Assistant"],
    "11-2021": ["Marketing Manager", "Head of Marketing"],
    "27-1024": ["Graphic Designer", "Visual Designer"],
    "27-3031": ["Communications Specialist", "PR Manager"],
    "27-3043": ["Copywriter", "Content Writer"],
    "11-2032": ["Director of Communications"],
    "13-1121": ["Events Manager"],
    "13-2011": ["Staff Accountant", "Senior Accountant", "Revenue Accountant", "Internal Auditor", "Tax Manager"],
    "43-3031": ["Accounts Payable Specialist", "AP Clerk", "Accounting Clerk"],
    "13-2051": ["FP&A Analyst", "Senior Financial Analyst", "Treasury Analyst"],
    "11-3031": ["Controller", "VP Finance", "Chief Financial Officer"],
    "43-3011": ["Collections Specialist"],
    "43-3051": ["Payroll Specialist"],
    "43-3021": ["Billing Specialist"],
    "13-2041": ["Credit Analyst"],
    "43-6011": ["Executive Assistant"],
    "13-1071": ["Recruiter", "HR Generalist", "Talent Acquisition Partner", "People Operations Specialist"],
    "11-3121": ["HR Business Partner", "Head of People"],
    "13-1141": ["Compensation Analyst", "Benefits Specialist"],
    "43-4161": ["HR Coordinator"],
    "11-3111": ["Total Rewards Manager"],
    "11-3131": ["Learning Manager"],
    "23-1011": ["Corporate Counsel", "Senior Counsel", "General Counsel"],
    "23-2011": ["Paralegal", "Contracts Manager"],
    "13-1041": ["Compliance Analyst", "Privacy Manager", "Compliance Manager"],
    "43-6012": ["Legal Assistant"],
    "15-1244": ["Systems Administrator", "Network Engineer"],
    "15-1211b": [],
    "15-1242": ["Database Administrator", "Data Engineer"],
    "15-1241": ["Solutions Architect", "Cloud Architect"],
    "13-1023": ["Buyer", "Procurement Specialist", "Sourcing Manager"],
    "11-3061": ["Procurement Manager"],
    "13-1081": ["Logistics Analyst"],
    "11-3013": ["Facilities Manager", "Workplace Manager"],
    "37-2011": ["Janitor", "Custodian"],
    "49-9071": ["Maintenance Technician"],
    "33-9032": ["Security Officer"],
    "43-4171": ["Receptionist"],
    "13-2054": ["Risk Analyst", "Enterprise Risk Manager"],
    "11-1011": ["Chief Executive Officer"],
    "11-1021": ["Chief Operating Officer", "General Manager", "Chief of Staff"],
}
LOCATIONS = [("San Francisco, CA", 0.22), ("Austin, TX", 0.25), ("Remote US", 0.20), ("Dublin, Ireland", 0.10),
             ("Bangalore, India", 0.13), ("Krakow, Poland", 0.06), ("Manila, Philippines", 0.04)]
OFFSHORE_OK = {"43-4051", "15-1232", "15-1252", "15-1253", "43-3031", "13-2011", "15-1211", "43-9061"}
LEVEL_MULT = {"junior": 0.8, "mid": 1.0, "senior": 1.3, "manager": 1.45, "director": 1.8, "executive": 2.6}


def _level_of(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ("chief", "vp ", "head of", "general counsel", "general manager")):
        return "executive"
    if "director" in t:
        return "director"
    if any(k in t for k in ("manager", "lead", "supervisor", "controller")):
        return "manager"
    if any(k in t for k in ("senior", "staff", "principal", "ii")):
        return "senior"
    if any(k in t for k in ("associate", "tier 1", "clerk", "coordinator", "junior")):
        return "junior"
    return "mid"


def generate(folder: str | Path, employees: int = 3200, seed: int = 0, priors: Priors | None = None,
             revenue_per_employee: float = 270_000.0, tiers: tuple[int, ...] = (0, 1, 2, 3, 4),
             data_dir: str | None = None, regime: str = "public", products: bool = True) -> dict:
    """Write a synthetic firm's input files to `folder` (100 to 100,000 employees). Returns a summary with the ground
    truth. `regime` sets the ownership inputs (public, pe, private_family, vc, hybrid)."""
    if not 50 <= employees <= 200_000:
        raise ValueError("employees must be between 50 and 200,000")
    rng = np.random.default_rng(seed)
    dd = Path(data_dir) if data_dir else find_data_dir()
    pri = priors or load_priors(dd)
    par = load_params(dd)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    fn = pri.functions.copy()
    occ = pri.occupations.set_index("soc")
    fo, _ = pri.function_occ_for("513210")
    revenue = employees * revenue_per_employee

    # Function sizes from the industry prior (software), then headcount by occupation.
    ifs = pri.industry_function_shares
    # the SEC software panel rows (prior_basis sec_panel); a substring test on "51" would also catch the
    # Damodaran-based rows of other industries (3251, 5131, 5161, 517)
    sw = ifs[ifs.prior_basis.astype(str) == "sec_panel"] if "prior_basis" in ifs.columns else ifs[ifs.industry != "generic"]
    if not len(sw):
        sw = ifs
    if "size_band" in sw.columns and (sw.size_band.astype(str) == "100M-1B").any():
        sw = sw[sw.size_band.astype(str) == "100M-1B"]
    sw = sw.groupby("function_id").share_mean.mean()
    shares = fn.function_id.map(sw).fillna(0.004).values * np.exp(rng.normal(0, 0.1, len(fn)))
    people_cost = shares * fn.labor_share.values * revenue
    tau_L = par.labor.tau_L
    rows, truth_titles = [], {}
    fte_total = 0.0
    for f_idx, f in enumerate(fn.itertuples()):
        mix = fo[fo.function_id == f.function_id]
        if mix.empty:
            continue
        mix = mix[mix.soc.isin(occ.index)]
        avg = float((mix.weight * occ.loc[mix.soc, "wage_median"].values).sum() / mix.weight.sum()) * 1.05 * (1 + tau_L)
        n_f = people_cost[f_idx] / avg
        for m in mix.itertuples():
            n = n_f * m.weight
            if n < 0.5:
                continue
            t0 = str(occ.loc[m.soc, "title"])
            t0 = t0[:-1] if t0.endswith("s") and not t0.endswith("ss") else t0
            titles = TITLE_VARIANTS.get(m.soc) or [t0]
            k = min(len(titles), max(1, int(np.ceil(n / 25))))
            split = rng.dirichlet(np.ones(k) * 2.0) * n
            for title, nn in zip(rng.permutation(titles)[:k], split):
                locs = LOCATIONS if m.soc in OFFSHORE_OK else LOCATIONS[:4]
                lw = np.array([w for _, w in locs]); lw /= lw.sum()
                parts = rng.multinomial(max(int(round(nn)), 1), lw)
                lvl = _level_of(title)
                for (loc, _), cnt in zip(locs, parts):
                    if cnt == 0:
                        continue
                    from .ingest import wage_index
                    wi, region = wage_index(loc, pri.locations)
                    contractor = (m.soc in {"15-1253", "43-4051", "15-1232"} and region in ("IN", "PH") and rng.random() < 0.5)
                    base = float(occ.loc[m.soc, "wage_median"]) * wi * LEVEL_MULT[lvl] * float(np.exp(rng.normal(0, 0.06)))
                    cc = f"CC-{1000 + 100 * f_idx + (0 if region == 'US' else 10 if region in ('EU', 'UK') else 20)}"
                    rows.append({"role_id": f"R{len(rows) + 1:04d}", "title": title, "cost_center": cc,
                                 "fte": float(cnt), "annual_base_comp": round(base, -2),
                                 "location": loc, "worker_type": "contractor" if contractor else "employee",
                                 "level": lvl, "_function": f.function_id, "_soc": m.soc, "_region": region})
                    truth_titles[title] = m.soc
                    fte_total += cnt
    roster = pd.DataFrame(rows)
    # Rescale to the target headcount.
    scale = employees / max(roster.fte.sum(), 1)
    roster["fte"] = np.maximum(np.round(roster.fte * scale), 1.0)

    # Cost centers and opex.
    cc_names = {}
    for f_idx, f in enumerate(fn.itertuples()):
        for off, reg in ((0, "Americas"), (10, "EMEA"), (20, "APAC")):
            cc_names[f"CC-{1000 + 100 * f_idx + off}"] = f"{f.function_name} {reg}"
    roster["loaded"] = roster.fte * roster.annual_base_comp * np.where(roster.worker_type == "contractor", 1 + par.labor.tau_L_contractor, 1 + tau_L)
    opex_rows = []
    labor_by_f = roster.groupby("_function").loaded.sum()
    fshare = dict(zip(fn.function_id, fn.labor_share))
    comp = dict(zip(fn.function_id, fn.get("compute_share_of_nonlabor", pd.Series(0.0, index=fn.index))))
    for cc, grp in roster.groupby("cost_center"):
        f_id = grp._function.iloc[0]
        emp = grp[grp.worker_type == "employee"]
        con = grp[grp.worker_type == "contractor"]
        base = float((emp.fte * emp.annual_base_comp).sum())
        lines = [("6000", "Salaries and wages", base * 0.92), ("6010", "Bonus and commissions", base * 0.08),
                 ("6100", "Payroll taxes and benefits", base * tau_L * 0.85), ("6150", "Stock-based compensation", base * tau_L * 0.15)]
        if len(con):
            lines.append(("6200", "Contractors and temporary labor", float((con.fte * con.annual_base_comp).sum()) * (1 + par.labor.tau_L_contractor)))
        lab = sum(a for _, _, a in lines)
        ls = max(fshare.get(f_id, 0.7), 0.15)
        nonlab = lab * (1 - ls) / ls
        cshare = float(comp.get(f_id, 0.0) or 0.0)
        lines += [("6300", "Software subscriptions", nonlab * (1 - cshare) * 0.35),
                  ("6400", "Cloud hosting", nonlab * cshare), ("6500", "Rent and facilities", nonlab * (1 - cshare) * 0.25),
                  ("6600", "Travel and entertainment", nonlab * (1 - cshare) * 0.15),
                  ("6800", "Professional fees", nonlab * (1 - cshare) * 0.25)]
        for gl, nm, amt in lines:
            if amt > 0:
                opex_rows.append({"cost_center": cc, "cost_center_name": cc_names.get(cc, cc), "gl_account": gl, "gl_name": nm,
                                  "amount": round(amt * float(np.exp(rng.normal(0, 0.02))), -2)})
    opex = pd.DataFrame(opex_rows)
    opex["_function"] = opex.cost_center.map(roster.groupby("cost_center")._function.first())
    bucket = dict(zip(fn.function_id, fn.cost_bucket))
    by_bucket = opex.groupby(opex._function.map(bucket)).amount.sum()

    # Tier 0, consistent with the opex by construction.
    fin = {"company_name": "Synthetic Software Co (fictional)", "fiscal_year": 2026, "currency": "USD",
           "revenue": round(revenue, -3), "cogs": round(float(by_bucket.get("cogs", 0)), -3), "rnd": round(float(by_bucket.get("rnd", 0)), -3),
           "sm": round(float(by_bucket.get("sm", 0)), -3), "ga": round(float(by_bucket.get("ga", 0)), -3),
           "sbc": round(float(opex[opex.gl_account == "6150"].amount.sum()), -3), "da": round(0.035 * revenue, -3),
           "capex": round(0.03 * revenue, -3), "headcount": float(roster[roster.worker_type == "employee"].fte.sum()),
           "naics": "513210", "revenue_growth": 0.17, "market_growth": 0.10, "tax_rate": 0.18,
           "owned_compute_share": 0.2, "context_engine": 0, "shares_outstanding": round(employees * 40_000, -3),
           "ownership_regime": regime}
    ebitda0 = fin["revenue"] - fin["cogs"] - fin["rnd"] - fin["sm"] - fin["ga"] + fin["sbc"] + fin["da"]
    fin["ebitda"] = round(ebitda0, -3)
    fin["net_debt"] = round(5.2 * max(ebitda0, 0.05 * revenue), -3) if regime == "pe" else round(-0.15 * revenue, -3)
    written = []

    def w(df, name):
        p = folder / f"{name}.csv"
        df.to_csv(p, index=False)
        written.append(p)

    w(pd.DataFrame({"field": list(fin), "value": list(fin.values())}), "tier0_financials")
    if 1 in tiers:
        w(opex.drop(columns=["_function"]), "tier1_opex")
    if 2 in tiers:
        w(roster.drop(columns=["_function", "_soc", "_region", "loaded"]), "tier2_roster")
    if 3 in tiers:
        vendors = [("Northwind Support Partners", "Tier 1 contact center BPO services", 0.010),
                   ("Tailspin Offshore Development", "Offshore software development services and staff augmentation", 0.012),
                   ("Fabrikam Payroll Services", "Payroll services and benefits administration", 0.0012),
                   ("Woodgrove LLP", "Outside counsel, commercial contracts", 0.004),
                   ("Proseware Cloud Hosting", "Cloud hosting and compute infrastructure", 0.060),
                   ("Litware SaaS Suite", "Software subscriptions, CRM and HR platforms", 0.020),
                   ("Adventure Works Creative Agency", "Marketing agency, media buying and creative", 0.006),
                   ("Contoso Facility Services", "Janitorial and security services", 0.003),
                   ("Margie's Search Partners", "Recruiting and executive search", 0.002),
                   ("Lucerne Audit and Tax", "External audit fees and tax advisory", 0.0018),
                   ("Wingtip Managed IT", "Managed IT services and service desk services", 0.003),
                   ("Fourth Coffee Travel", "Travel management", 0.004)]
        w(pd.DataFrame([{"vendor": v, "description": d, "annual_spend": round(s * revenue, -3)} for v, d, s in vendors]), "tier3_vendors")
        sys_rows = []
        for f in fn.itertuples():
            for k in range(int(rng.integers(1, 4))):
                i0 = float(np.clip(f.iota_prior + rng.normal(0, 0.1), 0.05, 0.95))
                sys_rows.append({"system": f"{f.function_name.split(',')[0]} system {k + 1}", "function_id": f.function_id,
                                 "system_of_record": int(k == 0), "api_available": round(float(np.clip(i0 + rng.normal(0, 0.1), 0, 1)), 2),
                                 "data_quality": round(float(np.clip(i0 + rng.normal(0, 0.1), 0, 1)), 2),
                                 "identity_resolution": round(float(np.clip(i0 - 0.1 + rng.normal(0, 0.1), 0, 1)), 2),
                                 "unstructured_share": round(float(np.clip(1 - i0 + rng.normal(0, 0.1), 0, 1)), 2),
                                 "annual_license_cost": round(float(rng.uniform(30e3, 250e3)), -3)})
        sysdf = pd.DataFrame(sys_rows)
        with pd.ExcelWriter(folder / "tier3_systems.xlsx", engine="openpyxl") as xw:
            sysdf.to_excel(xw, sheet_name="data", index=False)
        written.append(folder / "tier3_systems.xlsx")
        pr = pri.processes
        vol_rows = []
        for p in pr.itertuples():
            if rng.random() < 0.6:
                fixed = getattr(p, "fixed_volume_per_year", np.nan)
                base_v = fixed if pd.notna(fixed) else (p.typical_volume_per_musd_revenue or 1.0) * revenue / 1e6
                if pd.notna(base_v) and base_v > 0:
                    vol_rows.append({"process_id": p.process_id, "annual_volume": round(float(base_v * np.exp(rng.normal(0, 0.3))), 1),
                                     "unit": p.output_unit})
        w(pd.DataFrame(vol_rows), "tier3_volumes")
        org = {"governance_layers": 3, "approval_steps_small": 2, "approval_steps_medium": 4, "approval_steps_large": 6,
               "concurrent_initiatives": 5, "past_transformations_attempted": 4, "past_transformations_succeeded": 2,
               "transformation_office_fte": 3, "team_capability": 0.5, "experienced_share": 0.3, "delegation": 0.2,
               "decisions_per_year": 10, "benefit_realization_past": 0.7, "sells_to_us_government": 0,
               # ICFR conditions of a subscription software firm (spec 24.4); P11, P14, P15 conditions left unknown
               "holds_inventory": 0, "issues_refunds_credits": 1, "crm_billing_integration": 1, "subscription_billing": 1,
               "hris_feeds_payroll": 1}
        w(pd.DataFrame({"field": list(org), "value": list(org.values())}), "tier3_org")
        spons = [{"function_id": f.function_id, "sponsor_title": "Function head", "engaged": float(rng.choice([1.0, 1.0, 0.5, 0.0]))}
                 for f in fn.itertuples() if rng.random() < 0.6]
        w(pd.DataFrame(spons), "tier3_sponsors")
    if 3 in tiers:
        _write_tier3_extras(w, folder, roster, revenue, regime, rng, products, float(par.product.seat_price_default))
    if 4 in tiers:
        pa = pri.process_activities
        ts = []
        for pid in list(pri.processes.process_id[:2]):
            for r in pa[pa.process_id == pid].itertuples():
                if pd.notna(r.hours_per_unit):
                    ts.append({"process_id": pid, "step": r.step, "dwa_id": r.dwa_id,
                               "hours_per_unit": round(float(r.hours_per_unit * np.exp(rng.normal(0, 0.2))), 3), "sample_size": 200})
        if ts:
            w(pd.DataFrame(ts), "tier4_time_study")
    truth = {"seed": seed, "employees": employees, "revenue": revenue, "titles": truth_titles,
             "cost_centers": {cc: f for cc, f in roster.groupby("cost_center")._function.first().items()},
             "priors_source": pri.provenance.get("functions")}
    (folder / "_truth").mkdir(exist_ok=True)
    (folder / "_truth" / "synthetic_truth.json").write_text(json.dumps(truth, indent=1))
    return {"folder": str(folder), "files": [str(p) for p in written], "financials": fin, "fte": float(roster.fte.sum())}


COUNTRY = {"San Francisco, CA": "US", "Austin, TX": "US", "Remote US": "US", "Dublin, Ireland": "IE",
           "Bangalore, India": "IN", "Krakow, Poland": "PL", "Manila, Philippines": "PH"}


def _write_tier3_extras(w, folder: Path, roster: pd.DataFrame, revenue: float, regime: str, rng, products: bool,
                        seat_price: float | None = None) -> None:
    """Product, security, ownership and jurisdiction inputs of the synthetic firm (fictional). The service-desk line
    is priced at the engine's professional-tier seat price (product.seat_price_default)."""
    if products:
        seat_price = float(seat_price if seat_price is not None else load_params().product.seat_price_default)
        lines = [("Service desk", 0.55, "seat", seat_price, 0.80, 1.0, 0.6, 0.588, 0.40, 1.08, 0.90),
                 ("IT asset management", 0.27, "seat", 900.0, 0.78, 0.3, 0.5, 1.0, None, 1.05, 0.92),
                 ("Analytics add-on", 0.18, "usage", None, 0.70, 0.0, 0.4, None, None, 1.12, 0.88)]
        rows = []
        for name, sh, pm, price, gm, ls, pdata, hrs, chat, nrr, grr in lines:
            rv = round(sh * revenue, -3)
            rows.append({"product_line": name, "revenue": rv, "pricing_model": pm,
                         "seats": round(rv / price) if price else None, "price_per_seat": price,
                         "usage_units": None if price else round(rv / 0.05), "price_per_unit": None if price else 0.05,
                         "nrr": nrr, "grr": grr, "gross_margin": gm, "labor_substituting": ls, "proprietary_data": pdata,
                         "competitor_price": 1.5 if ls >= 0.5 else None, "customer_hours_per_outcome": hrs,
                         "seat_share_of_bill": 1.0 if pm == "seat" else 0.0, "billing_in_advance": 1,
                         "agent_unit_cost": chat, "entrant_unit_cost": chat, "entry_hazard": 0.25 if ls >= 0.5 else None})
        w(pd.DataFrame(rows), "tier3_products")
        occ = [("Service desk", "43-4051", 0.7), ("Service desk", "15-1232", 0.3),
               ("IT asset management", "15-1232", 0.6), ("IT asset management", "15-1244", 0.4),
               ("Analytics add-on", "13-1111", 0.5), ("Analytics add-on", "15-2051", 0.5)]
        w(pd.DataFrame(occ, columns=["product_line", "soc", "seat_share"]), "tier3_product_occupations")
        feats = [("Resolution agent", "Service desk", "agent", 6.0e6, 0.05, 0.001, 0.08, 0.6),
                 ("Agent copilot", "Service desk", "copilot", 2.5e6, 0.005, 0.002, 0.10, 0.8),
                 ("Asset discovery agent", "IT asset management", "agent", 3.0e6, 0.02, 0.0005, 0.03, 0.4),
                 ("Natural-language analytics", "Analytics add-on", "copilot", 2.0e6, 0.02, 0.001, 0.05, 0.5)]
        w(pd.DataFrame([{"feature": f, "product_line": l, "kind": k, "dev_cost": round(c * revenue / 8.64e8, -3),
                         "price_uplift_share": u, "retention_gain": rg, "bass_p": bp, "bass_q": bq} for f, l, k, c, u, rg, bp, bq in feats]),
          "tier3_ai_features")
    sec = {"security_team_fte": max(2, round(len(roster) and roster.fte.sum() * 0.004)), "certifications": "soc2; iso27001",
           "risk_appetite_max_class": "confidential", "vendor_preference": "either", "incidents_last_3_years": 2,
           "max_tolerable_loss": round(0.03 * revenue, -3)}
    w(pd.DataFrame({"field": list(sec), "value": list(sec.values())}), "tier3_security")
    if regime == "pe":
        reg = {"ownership_regime": "pe", "hold_years_elapsed": 1, "hold_years_total": 5, "exit_multiple": 14,
               "covenant_max_leverage": 7.0, "target_irr": 0.22}
    else:
        reg = {"ownership_regime": regime, "guidance_r40": 0.30, "guidance_eps_growth": 0.10, "dividend_payout": 0.0}
    w(pd.DataFrame({"field": list(reg), "value": list(reg.values())}), "tier3_regime")
    sites = roster.groupby("location").fte.sum()
    jr = []
    for loc, n in sites.items():
        c = COUNTRY.get(loc, "US")
        jr.append({"site": loc, "country": c, "headcount": float(n), "works_council": 1 if c == "PL" else 0,
                   "union_coverage": 0.0 if c in ("US", "IN", "PH") else 0.1,
                   "data_residency": "region" if c in ("IE", "PL") else "none"})
    w(pd.DataFrame(jr), "tier3_jurisdictions")


def generate_variants(root: str | Path, seed: int = 0, data_dir: str | None = None) -> dict:
    """The three firms of the golden tests: the synthetic mid-market firm (public), a small firm with Tier 0 and
    Tier 2 only, and a PE-owned firm."""
    root = Path(root)
    return {"synthetic": generate(root / "synthetic", employees=3200, seed=seed, data_dir=data_dir),
            "small": generate(root / "small", employees=250, seed=seed + 1, tiers=(0, 2), data_dir=data_dir, products=False),
            "pe": generate(root / "pe", employees=1800, seed=seed + 2, data_dir=data_dir, regime="pe")}
