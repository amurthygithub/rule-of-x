#!/usr/bin/env python3
"""B2 reduced firm-cluster bootstrap — MY OWN implementation (task 4).

Seed 20261103, B = 199 draws (99-draw subset also reported). Firms drawn with
replacement from the 292 E1 firms; every estimand evaluated on its own rows of
the drawn firms, with multiplicity (paired across estimands by construction).

Statistics per draw:
  p95_chg_{op,cash}  : P95(R) 2023-25 minus P95(R) 2016-19, E1 rows.
  psi_{op,cash}      : Psi_0.90 slope, 0-60% window, E1 rows. Undefined-draw
                       rule: every grid point g0=0,0.05,...,0.60 needs >=10
                       firm-years in-draw; ANY cell <10 => draw is NaN.
  T40_chg_{op,cash}  : T(40%) change; per-period cell needs >=10, NaN if
                       either period cell fails.
  E2 versions of psi and the 60%-cell counts (for the cell-thinness claim):
                       cell60_{op,cash} counts E2 rows with g>=0.60 and finite
                       margin; the >=30 "sample rule" check flags draws with
                       cell60 < 30.

Sample-level point estimates use the >=30 rule (grid) and are recomputed here
as a further independent check.

The E1/E2 frames come from the author's frame-construction code
(code/estimate_organic.py up to the END OF FRAME CONSTRUCTION marker) because
the E2 estimand (organic growth) is the author's definition; ALL bootstrap
logic below is written independently for this referee report.
"""
import os, sys, json
import numpy as np
import pandas as pd

BASE = "/root/tmp/ruleof40/diagnostics/econometrics-empirics/rerun"
OUT = "/root/tmp/ruleof40/diagnostics/econometrics-empirics/b2/outputs/b2_bootstrap.txt"
SEED = 20261103
B = 199

# ---------- frames (author's data prep, deterministic; no estimation logic) ----------
os.environ["ORGANIC_PANEL"] = "v3"
SRC = f"{BASE}/code/estimate_organic.py"
src = open(SRC).read()
cut = src.index("# ==== END OF FRAME CONSTRUCTION")
_G = {"__file__": SRC, "__name__": "b2_frames"}
exec(compile(src[:cut], SRC, "exec"), _G)
V, core = _G["V"], _G["core"]
print("frames: E1 n=%d, E2 n=%d" % (len(V["E1"]), len(V["E2"])), flush=True)

def frame_arrays(v, label):
    f = v[["cik", "year", "period", "g", "m_op", "m_fcf_sbc"]].copy()
    f["per"] = f["period"].map({"2010-15": 0, "2016-19": 1, "2020-22": 2, "2023-25": 3})
    assert f["per"].notna().all(), label
    return f

E1 = frame_arrays(V["E1"], "E1")
E2 = frame_arrays(V["E2"], "E2")
FIRMS = np.sort(E1["cik"].unique())
NF = len(FIRMS)
fid = {c: i for i, c in enumerate(FIRMS)}
print("firm universe:", NF, flush=True)

# per-firm row blocks
def blocks(df):
    idx = df["cik"].map(fid).to_numpy()
    out = [[] for _ in range(NF)]
    g = df["g"].to_numpy(); yr = df["year"].to_numpy(); per = df["per"].to_numpy()
    mo = df["m_op"].to_numpy(); mc = df["m_fcf_sbc"].to_numpy()
    for i in range(len(df)):
        out[idx[i]].append((g[i], yr[i], per[i], mo[i], mc[i]))
    return [np.array(b).reshape(-1, 5) for b in out]

B1 = blocks(E1)
B2 = blocks(E2)

GRID = np.round(np.arange(0.0, 0.6001, 0.05), 2)

def psi_slope(g, m, min_n, window=0.60, chi=0.90):
    """chi-quantile cone slope over GRID; NaN if any cell < min_n."""
    ok = np.isfinite(g) & np.isfinite(m)
    g, m = g[ok], m[ok]
    o = np.argsort(-g, kind="stable")
    ms, mg = m[o], -g[o]
    phi = []
    for g0 in GRID:
        n = np.searchsorted(mg, -g0, side="right")
        if n < min_n:
            return np.nan, n
        phi.append(np.quantile(ms[:n], chi))
    x = GRID; y = np.array(phi)
    return float(((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()) ** 2).sum()), None

def cell_count(g, m, g0):
    return int((np.isfinite(g) & np.isfinite(m) & (g >= g0)).sum())

def p95_change(g, m, per):
    ok = np.isfinite(g) & np.isfinite(m)
    R = g + m
    a = R[ok & (per == 1)]; c = R[ok & (per == 3)]
    return np.quantile(c, 0.95) - np.quantile(a, 0.95)

def T40_change(g, m, per, g0=0.40):
    vals = []
    for p in (1, 3):
        s = m[(per == p) & np.isfinite(g) & np.isfinite(m) & (g >= g0)]
        if len(s) < 10:
            return np.nan
        vals.append(g0 + np.quantile(s, 0.95))
    return vals[1] - vals[0]

# ---------- sample-level point estimates (independent check, >= 30 rule) ----------
samp = {}
for bname, mcol in (("op", "m_op"), ("cash", "m_fcf_sbc")):
    s, _ = psi_slope(E1["g"].to_numpy(), E1[mcol].to_numpy(), 30)
    samp[f"psi_{bname}"] = s
    samp[f"p95_chg_{bname}"] = 100 * p95_change(E1["g"].to_numpy(), E1[mcol].to_numpy(), E1["per"].to_numpy())
    samp[f"T40_chg_{bname}"] = 100 * T40_change(E1["g"].to_numpy(), E1[mcol].to_numpy(), E1["per"].to_numpy())
    s2, _ = psi_slope(E2["g"].to_numpy(), E2[mcol].to_numpy(), 30)
    samp[f"psi_{bname}_E2"] = s2
    samp[f"cell60_{bname}_E2"] = cell_count(E2["g"].to_numpy(), E2[mcol].to_numpy(), 0.60)
print("sample point estimates:", json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in samp.items()}), flush=True)

# ---------- my bootstrap ----------
rng = np.random.default_rng(SEED)
res = {k: [] for k in ["p95_chg_op", "p95_chg_cash", "psi_op", "psi_cash",
                       "T40_chg_op", "T40_chg_cash", "psi_op_E2", "psi_cash_E2"]}
cell60_draws = {"op": [], "cash": []}

for b in range(B):
    draw = rng.integers(0, NF, NF)
    counts = np.bincount(draw, minlength=NF)
    # E1 rows with multiplicity
    parts = [np.tile(B1[f], (counts[f], 1)) for f in range(NF) if counts[f]]
    A = np.concatenate(parts) if parts else np.zeros((0, 5))
    g, yr, per, mo, mc = A[:, 0], A[:, 1], A[:, 2], A[:, 3], A[:, 4]
    res["p95_chg_op"].append(100 * p95_change(g, mo, per))
    res["p95_chg_cash"].append(100 * p95_change(g, mc, per))
    res["psi_op"].append(psi_slope(g, mo, 10)[0])
    res["psi_cash"].append(psi_slope(g, mc, 10)[0])
    res["T40_chg_op"].append(100 * T40_change(g, mo, per))
    res["T40_chg_cash"].append(100 * T40_change(g, mc, per))
    parts2 = [np.tile(B2[f], (counts[f], 1)) for f in range(NF) if counts[f]]
    A2 = np.concatenate(parts2) if parts2 else np.zeros((0, 5))
    g2, yr2, per2, mo2, mc2 = A2[:, 0], A2[:, 1], A2[:, 2], A2[:, 3], A2[:, 4]
    res["psi_op_E2"].append(psi_slope(g2, mo2, 10)[0])
    res["psi_cash_E2"].append(psi_slope(g2, mc2, 10)[0])
    cell60_draws["op"].append(cell_count(g2, mo2, 0.60))
    cell60_draws["cash"].append(cell_count(g2, mc2, 0.60))
    if (b + 1) % 50 == 0:
        print(f"draw {b+1}/{B}", flush=True)

# ---------- report ----------
lines = []
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s); lines.append(s)

PUB = {  # published E1 values: point, ci90 (percentile), Table 2 pp. 40-41
    "p95_chg_op": (-11.9, (-20.3, -6.4)), "p95_chg_cash": (-12.7, (-21.6, -4.2)),
    "psi_op": (-0.2154, (-0.417, -0.048)), "psi_cash": (-0.1613, (-0.310, 0.010)),
    "T40_chg_op": (-9.9, None), "T40_chg_cash": (1.6, None),
}
log("=== B2 own reduced bootstrap (seed %d, B=%d) vs published (B=999) ===" % (SEED, B))
for k in ["p95_chg_op", "p95_chg_cash", "psi_op", "psi_cash", "T40_chg_op", "T40_chg_cash"]:
    v = np.array([x if x is not None else np.nan for x in res[k]], float)
    nan_share = np.mean(~np.isfinite(v))
    est = samp[k.replace("_E2", "")]
    pub_est, pub_ci = PUB[k]
    fin = v[np.isfinite(v)]
    if len(fin) >= 10 and nan_share <= 0.05:
        lo, hi = np.quantile(fin, [0.05, 0.95])
        my_ci = (round(lo, 3), round(hi, 3))
    else:
        my_ci = None
    log(f"\n{k}:")
    log(f"  my point est = {est:.4f}" + (f"  (published {pub_est})" if pub_est is not None else ""))
    log(f"  my 90% percentile interval (B={len(fin)} finite draws) = {my_ci}"
        + (f"  (published {pub_ci})" if pub_ci else ""))
    log(f"  my NaN-draw share = {nan_share:.3f} (rule: >5% => no interval)")
    if k in ("T40_chg_op", "T40_chg_cash"):
        log(f"  published: E1 T(40%) undefined in 5.8% of draws => dagger (no interval)")

log("\n=== E2 cell-thinness claim (16.8% GAAP / 13.0% cash draws below 30 at the 60% cell) ===")
for b in ("op", "cash"):
    c = np.array(cell60_draws[b])
    share30 = np.mean(c < 30)
    log(f"E2 cell60 ({b}): sample n = {samp[f'cell60_{b}_E2']}; my draws with cell60 < 30: {share30:.3f}")
log("\n=== conditional E2 primary-slope interval on draws meeting the >=30 rule ===")
for b in ("op", "cash"):
    v = np.array([x if x is not None else np.nan for x in res[f"psi_{b}_E2"]], float)
    c = np.array(cell60_draws[b])
    sel = v[np.isfinite(v) & (c >= 30)]
    if len(sel):
        lo, hi = np.quantile(sel, [0.05, 0.95])
        log(f"psi_{b}_E2 on cell60>=30 draws (n={len(sel)}): 90% interval [{lo:.3f}, {hi:.3f}]"
            f"  (published: {'[-0.505, -0.080]' if b=='op' else '[-0.413, -0.046]'})")
    log(f"psi_{b}_E2 full-sample point est (mine) = {samp[f'psi_{b}_E2']:.4f}")

# 99-draw subset stability
log("\n=== 99-draw subset (first 99 of the same stream) ===")
for k in ["p95_chg_op", "p95_chg_cash", "psi_op", "psi_cash"]:
    v = np.array([x if x is not None else np.nan for x in res[k][:99]], float)
    fin = v[np.isfinite(v)]
    if len(fin):
        lo, hi = np.quantile(fin, [0.05, 0.95])
        log(f"{k}: 90% interval [{lo:.3f}, {hi:.3f}] (n={len(fin)} finite)")

with open(OUT, "w") as f:
    f.write("\n".join(lines) + "\n")
np.savez_compressed(OUT.replace(".txt", ".npz"),
                    **{k: np.array([x if x is not None else np.nan for x in v], float) for k, v in res.items()},
                    cell60_op=np.array(cell60_draws["op"]), cell60_cash=np.array(cell60_draws["cash"]))
print("\n[wrote", OUT, "and .npz]")