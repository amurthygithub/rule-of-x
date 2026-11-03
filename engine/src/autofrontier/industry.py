# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Industry priors beyond software (spec 24.10; notes/data_sources_nonsoftware.md).

The firm's NAICS code is matched to a Damodaran industry group (January 2026 data) through the data agent's
crosswalk (xw_damodaran_naics.csv, longest prefix). The group supplies Part I's capital intensity k (invested
capital per dollar of revenue, unadjusted basis) and the cost of capital used as the discount rate. Software codes
are not in the crosswalk (they use the SEC panel rows for function shares) and map to Damodaran's software groups
here. Firms with no match use the Total Market (without financials) row. Firm inputs override all of this."""
from __future__ import annotations

import math

SOFTWARE_NAICS = ("5132", "5112", "5182", "5191", "5415")
SOFTWARE_GROUP = {"5132": "Software (System & Application)", "5112": "Software (System & Application)",
                  "5182": "Software (System & Application)", "5191": "Software (System & Application)",
                  "5415": "Computer Services"}
GENERIC_GROUP = "Total Market (without financials)"
# The five largest employment groups the priors cover: mostly private or public employers, while the ratios come
# from listed firms (coordinator, 29 Oct 2026)
WEAK_PRIOR_GROUPS = {"Hospitals/Healthcare Facilities", "Education", "Restaurant/Dining", "Business & Consumer Services",
                     "Engineering/Construction"}
K_RANGE_DEFAULT = (0.22, 2.03)          # P10 and P90 of the unadjusted k across non-financial groups


def is_software(naics) -> bool:
    n = str(naics or "")
    return any(n.startswith(c) for c in SOFTWARE_NAICS)


def _num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if not math.isfinite(v) else v


def industry_prior(priors, naics) -> dict:
    """The Damodaran group for a NAICS code, with k (unadjusted basis where available), the cost of capital, the
    match, its confidence and the flags that make the prior weak. Returns {"group": None, ...} without the data."""
    b, xw = getattr(priors, "industry_benchmarks", None), getattr(priors, "xw_damodaran", None)
    out = {"group": None, "naics": str(naics or ""), "match": "", "confidence": "", "software": is_software(naics),
           "k": None, "k_variant": None, "k_range": K_RANGE_DEFAULT, "cost_of_capital": None, "flags": [],
           "weak_prior": False, "prior_basis": "sec_panel" if is_software(naics) else "damodaran_oews"}
    if b is None or xw is None:
        out["flags"].append("industry benchmarks not available: finance defaults apply")
        return out
    n = str(naics or "")
    group, match, conf = None, "", ""
    for pre, g in sorted(SOFTWARE_GROUP.items(), key=lambda kv: -len(kv[0])):
        if n.startswith(pre):
            group, match, conf = g, pre, "high (engine mapping of software codes)"
            break
    if group is None and n:
        best = -1
        for row in xw.itertuples(index=False):
            for pre in str(getattr(row, "naics_match", "") or "").split("/"):
                pre = pre.strip()
                if pre and pre != "nan" and n.startswith(pre) and len(pre) > best:
                    best, group, match, conf = len(pre), row.damodaran_industry, pre, str(row.confidence)
    if group is None:
        group, match, conf = GENERIC_GROUP, "", "generic (no NAICS match)"
        out["flags"].append("no industry match: Total Market (without financials) prior")
        out["prior_basis"] = "damodaran_generic"
    row = b[b.damodaran_industry == group]
    if not len(row):
        out["flags"].append(f"group {group} not in industry_benchmarks.csv")
        return out
    r = row.iloc[0]
    out.update(group=group, match=match, confidence=conf)
    k = _num(r.get("k_ic_per_sales"))
    flag = str(r.get("k_flag") or "")
    if k is not None and flag.startswith("ok"):
        out["k"], out["k_variant"] = k, str(r.get("k_variant") or "")
        variants = [_num(r.get(c)) for c in ("k_ic_per_sales_unadj", "k_ic_per_sales_lease", "k_ic_per_sales_lease_rnd")]
        variants = [v for v in variants if v is not None]
        out["k_variants"] = variants
        if out["k_variant"] not in ("unadj", "unadjusted"):
            out["flags"].append(f"k on the {out['k_variant']} basis (includes capitalized R&D and lease debt; about twice Part I's k in software)")
    else:
        out["flags"].append(f"k not usable for {group} ({flag or 'missing'}): finance default")
    out["cost_of_capital"] = _num(r.get("cost_of_capital"))
    if int(_num(r.get("small_sample")) or 0):
        out["flags"].append(f"small sample ({int(_num(r.get('n_firms')) or 0)} listed firms)")
    if int(_num(r.get("financial_group")) or 0):
        out["flags"].append("financial group: invested capital and cost structure are not operating measures")
    if conf.startswith("low"):
        out["flags"].append("low-confidence crosswalk from NAICS to the Damodaran group")
    if group in WEAK_PRIOR_GROUPS:
        out["weak_prior"] = True
        out["flags"].append("weak prior: most employers in this industry are private or public, while the ratios come from listed firms")
    if not out["software"]:
        out["flags"].append("people costs are low confidence: labor share per function is not industry-specific (software values)")
    return out


def apply_rates(p, ind: dict) -> list[str]:
    """Set the discount rate to the industry's cost of capital, ln(1 + WACC) (to_continuous), unless the user set
    finance.r or the firm is a software firm (whose group is the default). The range keeps the default's spread in
    percentage points. regime.public_r follows. Returns the keys changed."""
    coc = ind.get("cost_of_capital")
    changed = []
    if coc is None or coc <= -0.99:
        return changed
    for key in ("finance.r", "regime.public_r"):
        if p.last_origin(key) is not None:          # the user, a scenario or a test set it: keep
            continue
        lo_c, hi_c = p.range(key)
        cen = float(p.get(key))
        lo_a, hi_a, cen_a = math.expm1(lo_c), math.expm1(hi_c), math.expm1(cen)
        new = math.log1p(coc)
        rng = [math.log1p(max(coc - (cen_a - lo_a), 0.0)), math.log1p(coc + (hi_a - cen_a))]
        if abs(new - cen) < 1e-4:        # same group as the default (software): keep the default and its source
            continue
        org = f"industry cost of capital ({ind['group']}, Damodaran January 2026; ln(1 + {coc:.4f}))"
        p.set(key, new, origin=org)
        p.set_range(key, rng, origin=org)
        changed.append(key)
    return changed


def k_default(ind: dict, p) -> tuple[float, tuple[float, float], str]:
    """Part I's k for the firm: the industry's invested capital per dollar of revenue when usable, else the finance
    default. Returns (k, range, source)."""
    if ind.get("k") is not None:
        k = float(ind["k"])
        return k, (min(K_RANGE_DEFAULT[0], k), max(K_RANGE_DEFAULT[1], k)), \
            f"industry k ({ind['group']}, {ind['k_variant']} basis, Damodaran January 2026)"
    return float(p.finance.capital_intensity_k), tuple(p.range("finance.capital_intensity_k")), "finance default"


def summary(ind: dict) -> str:
    if not ind.get("group"):
        return "no industry benchmark"
    s = f"{ind['group']} (NAICS {ind['match'] or 'none'}, {ind['confidence']})"
    if ind.get("weak_prior"):
        s += ", weak prior"
    return s


__all__ = ["industry_prior", "apply_rates", "k_default", "is_software", "summary", "WEAK_PRIOR_GROUPS", "GENERIC_GROUP"]
