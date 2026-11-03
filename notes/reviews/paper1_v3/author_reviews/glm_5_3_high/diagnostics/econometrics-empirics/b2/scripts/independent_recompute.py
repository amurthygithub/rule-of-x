#!/usr/bin/env python3
"""B2 INDEPENDENT recomputation from data/panel_v3.csv (my own code, no author code).

Computes, on the E1 (all firm-years) basis:
 (a) Psi_0.90 partial-frontier slope on GAAP op margin and FCF-after-SBC margin:
     phi_chi(g0) = chi-quantile of margin among firm-years with g >= g0,
     grid g0 = 0, 0.05, ..., 0.60, grid point needs >= 30 firm-years;
     slope = OLS of phi over kept grid points. Windows 0-60% and 0-40%;
     pooled 2010-25 and period windows 2010-19, 2020-25.
 (b) P95 of R = g + m by period (2016-19, 2023-25) and the change, both bases.
 (c) T(g0) = g0 + phi_0.95(g0) for g0 in {0, 0.20}, per period, and changes.
 (d) Median spend ratio: median over firm-years with g > year-median g of
     sm_lag_share / (g - year-median g).
 (e) Margin-gap decomposition: within growth bands, top decile of m_op vs 40-60th
     pctile, gaps in S&M/R&D/G&A/gross-margin/other parts; average across bands
     and the 40-60% growers' band.

Also verifies the panel's internal consistency (g == rev/rev_lag - 1) and reports
which margin bases exist.
"""
import numpy as np
import pandas as pd

PANEL = "/root/tmp/ruleof40/repo/data/panel_v3.csv"
OUT = "/root/tmp/ruleof40/diagnostics/econometrics-empirics/b2/outputs/independent_recompute.txt"

df = pd.read_csv(PANEL)
log_lines = []
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s); log_lines.append(s)

log("=== Column discovery ===")
log("margin bases present:", [c for c in df.columns if c.startswith("m_")])
log("scores present:", [c for c in df.columns if c.startswith("R_")])
log("rows:", len(df), "firms:", df["cik"].nunique())

# --- internal consistency: g == rev/rev_lag - 1 (same-filing past-year growth) ---
gg = df["rev"] / df["rev_lag"] - 1.0
bad = (~np.isclose(gg, df["g"], rtol=0, atol=1e-9)) & df["rev_lag"].notna()
log(f"\ng == rev/rev_lag - 1 for all rows: {bad.sum()==0} (violations: {bad.sum()})")
log(f"rev_lag missing rows: {df['rev_lag'].isna().sum()}")

# sm_lag_share = previous-year S&M share? verify by construction within firm
d2 = df.sort_values(["cik", "year"])
prev_sm = d2.groupby("cik")["sm"].shift(1)
prev_rev = d2.groupby("cik")["rev"].shift(1)
lag_share = (prev_sm / prev_rev)
ok = np.isclose(lag_share, d2["sm_lag_share"], atol=1e-9, rtol=0) | (lag_share.isna() & d2["sm_lag_share"].isna())
log(f"sm_lag_share == prev-year sm/rev within firm: {ok.sum()==len(d2)} (mismatches: {(~ok).sum()}, "
    f"prev within-firm unavailable: {lag_share.isna().sum() - d2['sm_lag_share'].isna().sum()})")

PERIODS = {"2016-19": (2016, 2019), "2023-25": (2023, 2025)}
BASES = {"GAAP": "m_op", "cash": "m_fcf_sbc"}

def phi(sub, mcol, chi, g0, min_n=30):
    """chi-quantile of margin among firm-years with g >= g0; None if < min_n obs."""
    sel = sub[(sub["g"] >= g0) & sub[mcol].notna()]
    if len(sel) < min_n:
        return None, len(sel)
    return float(np.quantile(sel[mcol], chi)), len(sel)

def psi_slope(sub, mcol, chi=0.90, window=0.60, min_n=30):
    grid = np.arange(0.0, window + 1e-9, 0.05)
    pts, ns = [], []
    for g0 in grid:
        v, n = phi(sub, mcol, chi, g0, min_n)
        if v is not None:
            pts.append((g0, v)); ns.append((g0, n))
    if len(pts) < 2:
        return None, ns
    x = np.array([p[0] for p in pts]); y = np.array([p[1] for p in pts])
    b, a = np.polyfit(x, y, 1)
    return b, ns

log("\n=== (a) Psi_0.90 slopes (E1, all firm-years) ===")
for bname, mcol in BASES.items():
    for window in (0.60, 0.40):
        s, ns = psi_slope(df, mcol, 0.90, window)
        log(f"{bname:<6} 2010-25 window 0-{int(window*100)}%: slope = {s:.4f}  (kept cells: {len(ns)})")
# period slopes on 0-40 window
for bname, mcol in BASES.items():
    for plabel, (y0, y1) in [("2010-19", (2010, 2019)), ("2020-25", (2020, 2025))]:
        sub = df[(df["year"] >= y0) & (df["year"] <= y1)]
        s, ns = psi_slope(sub, mcol, 0.90, 0.40)
        log(f"{bname:<6} {plabel} window 0-40%: slope = {s:.4f}")
log("(paper: GAAP -0.22 (0-60), -0.31 (0-40), -0.22 (2010-19), -0.60 (2020-25); "
    "cash -0.16, -0.27, -0.16, -0.35)")

log("\n=== (b) P95 of R = g + m by period and change (E1) ===")
p95 = {}
for bname, mcol in BASES.items():
    R = df["g"] + df[mcol]
    for plabel, (y0, y1) in PERIODS.items():
        mask = (df["year"] >= y0) & (df["year"] <= y1)
        v = float(np.quantile(R[mask].dropna(), 0.95))
        p95[(bname, plabel)] = v
        log(f"{bname:<6} P95 of R {plabel}: {100*v:.1f} pts")
    ch = 100 * (p95[(bname, '2023-25')] - p95[(bname, '2016-19')])
    log(f"{bname:<6} change 2016-19 -> 2023-25: {ch:.1f} pts")
log("(paper: GAAP 55.9 -> 43.9, change -11.9; cash 57.3 -> 44.6, change -12.7)")

log("\n=== (c) T(g0) = g0 + phi_0.95(g0), per period; changes ===")
for g0 in (0.0, 0.20):
    for bname, mcol in BASES.items():
        vals = {}
        for plabel, (y0, y1) in PERIODS.items():
            sub = df[(df["year"] >= y0) & (df["year"] <= y1)]
            v, n = phi(sub, mcol, 0.95, g0, min_n=1)
            vals[plabel] = (100 * (g0 + v) if v is not None else None, n)
        ch = vals["2023-25"][0] - vals["2016-19"][0]
        log(f"T({int(g0*100)}%) {bname:<6}: 2016-19 = {vals['2016-19'][0]:.1f} (n={vals['2016-19'][1]}), "
            f"2023-25 = {vals['2023-25'][0]:.1f} (n={vals['2023-25'][1]}), change = {ch:.1f}")
log("(paper: T(0%) GAAP +0.8, cash -3.3; T(20%) GAAP -10.2, cash -3.0)")

log("\n=== (d) Median spend ratio (E1) ===")
# previous year's S&M share over current-year excess growth, among g > year median
med_g = df.groupby("year")["g"].transform("median")
sel = df[(df["g"] > med_g) & df["sm_lag_share"].notna()]
ratio = sel["sm_lag_share"] / (sel["g"] - med_g[sel.index])
log(f"n = {len(sel)}; median spend ratio = {ratio.median():.3f}")
log(f"  (paper: 3.02 (0.19), E1)")
# variants: with current-year S&M share instead of lag
if "sm" in df:
    cur = sel["sm"] / sel["rev"]
    ratio_cur = cur / (sel["g"] - med_g[sel.index])
    log(f"  [variant] current-year S&M share ratio = {ratio_cur.median():.3f}")

log("\n=== (e) Margin-gap decomposition (E1) ===")
# firm-years with growth 0-60% reporting all four lines; sm/rd/ga/gp are dollars -> shares
need = ["m_op", "sm", "rd", "ga", "gp"]
dd = df[(df["g"] >= 0) & (df["g"] <= 0.60) & df[need].notna().all(axis=1)].copy()
for c in ["sm", "rd", "ga", "gp"]:
    dd[c + "_sh"] = dd[c] / dd["rev"]
log(f"n with 0<=g<=60% and all four lines: {len(dd)}")
dd["oth_sh"] = dd["gp_sh"] - dd["sm_sh"] - dd["rd_sh"] - dd["ga_sh"] - dd["m_op"]
BANDS = [(0.0, 0.10), (0.10, 0.20), (0.20, 0.30), (0.30, 0.40), (0.40, 0.60)]
gaps, parts = [], {"d_sm": [], "d_rd": [], "d_ga": [], "d_gm": [], "d_oth": []}
for lo, hi in BANDS:
    band = dd[(dd["g"] >= lo) & (dd["g"] < hi)] if hi < 0.60 else dd[(dd["g"] >= lo) & (dd["g"] <= hi)]
    if len(band) == 0:
        continue
    q90 = np.quantile(band["m_op"], 0.90)
    q40, q60 = np.quantile(band["m_op"], 0.40), np.quantile(band["m_op"], 0.60)
    top = band[band["m_op"] >= q90]
    mid = band[(band["m_op"] >= q40) & (band["m_op"] <= q60)]
    gap = top["m_op"].mean() - mid["m_op"].mean()
    gaps.append(gap)
    log(f"band {lo:.0%}-{hi:.0%}: n_top={len(top)} n_mid={len(mid)} gap={100*gap:.1f} pts")
    for k, col in [("d_sm","sm_sh"), ("d_rd","rd_sh"), ("d_ga","ga_sh"), ("d_gm","gp_sh"), ("d_oth","oth_sh")]:
        p = top[col].mean() - mid[col].mean()
        parts[k].append(p)
        log(f"    {k}: {100*p:.1f}")
log(f"average gap across bands: {100*np.mean(gaps):.1f} pts  (paper: 34.5 [28.6, 37.7])")
for k in parts:
    log(f"  avg {k}: {100*np.mean(parts[k]):.1f}  (paper: sm 16.0, rd 7.1, gm 5.7, ga 5.5)")
log(f"identity check (gap - [d_gm - d_sm - d_rd - d_ga - d_oth]) avg: "
    f"{100*(np.mean(gaps) - (np.mean(parts['d_gm']) - np.mean(parts['d_sm']) - np.mean(parts['d_rd']) - np.mean(parts['d_ga']) - np.mean(parts['d_oth']))):.4f} pts")

with open(OUT, "w") as f:
    f.write("\n".join(log_lines) + "\n")
print("\n[wrote", OUT, "]")