#!/usr/bin/env python3
"""B2 task 5: verify the Holm implementation and quantify the post-hoc family choice.

(1) Recompute Holm adjusted p-values from the 14 stored unadjusted p-values of
    headline14B (normal / percentile / basic) and compare with the stored holm_*.
(2) Verify the paper's §5.8 disclosed counterfactual: anchor Pi_lb added to the
    family gives Holm p = 0.006 (normal), 0.084 (percentile), 0.028 (basic).
(3) Counterfactual families that include other headline §5 statistics the
    published family excludes (T(20%) changes, T(0%) cash, spend ratio) and the
    effect on the two substantive survivors (steepening; GAAP p95 decline).
"""
import json
import numpy as np

BASE = "/root/tmp/ruleof40/diagnostics/econometrics-empirics/baseline"
E = json.load(open(f"{BASE}/empirics_v3.json"))
EST, FAM = E["estimates"], E["families"]
OUT = "/root/tmp/ruleof40/diagnostics/econometrics-empirics/b2/outputs/holm_counterfactual.txt"

lines = []
def log(*a):
    s = " ".join(str(x) for x in a); print(s); lines.append(s)

def holm(pvals):
    """Holm step-down adjusted p-values, same convention as stored (monotone max)."""
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    adj = np.empty(n)
    running = 0.0
    for i, idx in enumerate(order):
        running = max(running, (n - i) * p[idx])
        adj[idx] = min(1.0, running)
    return adj

fam = FAM["headline14B"]["contrasts"]
types = ["normal", "percentile", "basic"]

# (1) verify stored Holm on the 14-member family
log("=== (1) Holm recomputation on headline14B ===")
for t in types:
    ps = np.array([c.get(f"p_{t}") if c.get(f"p_{t}") is not None else 1.0 for c in fam])
    adj = holm(ps)
    stored = np.array([c[f"holm_{t}"] for c in fam])
    md = np.max(np.abs(adj - stored))
    log(f"  {t}: max |recomputed - stored| = {md:.6g}  -> {'MATCH' if md < 1e-9 else 'MISMATCH'}")

# keys of members for reference
keys = [c["key"] for c in fam]
log("  family members:", ", ".join(keys))

# unadjusted p fetch helper from estimates
def get_p(stat, view, t):
    r = EST[stat][view]
    v = r.get(f"p_{t}")
    return 1.0 if v is None else v

# (2) paper's disclosed counterfactual: + anchor Pi_lb (E1)
log("\n=== (2) §5.8 claim: anchor Pi_lb added to the family ===")
for t in types:
    ps14 = [get_p(c["statistic"], c["estimand"], t) if c["estimand"] != "E1_minus_E2" else None for c in fam]
    # E1-E2 contrasts: p from families table? use stored p_* in the contrast record
    ps14 = np.array([c.get(f"p_{t}") if c.get(f"p_{t}") is not None else 1.0 for c in fam])
    pa = get_p("anchor_p95_Pi_lb_med", "E1", t)
    adj = holm(np.append(ps14, pa))
    log(f"  {t}: anchor Pi_lb Holm p = {adj[-1]:.3f}  (paper: 0.006 normal / 0.084 percentile / 0.028 basic)")

# (3) bigger counterfactual families
log("\n=== (3) Counterfactual families: what if all §5 headline claims were members? ===")
extra = {
    "T20_GAAP": ("T_op_g20_change", "E1"),
    "T20_cash": ("T_cash_g20_change", "E1"),
    "T0_cash": ("T_cash_g00_change", "E1"),
    "spend_ratio": ("spend_ratio", "E1"),
    "anchorPi_lb": ("anchor_p95_Pi_lb_med", "E1"),
    "gap_slow_gm": ("gap_slow_gm", "E1"),
}
scenarios = {
    "published (14)": [],
    "+anchorPi_lb (15, paper's §5.8)": ["anchorPi_lb"],
    "+anchor +T20 both bases +T0_cash (18)": ["anchorPi_lb", "T20_GAAP", "T20_cash", "T0_cash"],
    "+ all extras (20)": list(extra.keys()),
}
steep_idx = keys.index("psi_op_E1_2020_25_minus_2010_19")
p95_idx = keys.index("p95chg_op_E1")
anchor_new_idx = 14  # position of anchorPi_lb in the appended vector
log("  base unadjusted p (normal): steepening "
    f"{get_p('cone_op_slope_c90_w40_2020_25_minus_2010_19', 'E1', 'normal'):.4g}, "
    f"p95chg_op {get_p('p95_change_op', 'E1', 'normal'):.4g}, "
    f"anchorPi_lb {get_p('anchor_p95_Pi_lb_med', 'E1', 'normal'):.4g}, "
    f"T20_GAAP {get_p('T_op_g20_change', 'E1', 'normal'):.4g}, "
    f"T20_cash {get_p('T_cash_g20_change', 'E1', 'normal'):.4g}")
for name, extras in scenarios.items():
    log(f"\n  Family: {name}")
    for t in types:
        ps14 = np.array([c.get(f"p_{t}") if c.get(f"p_{t}") is not None else 1.0 for c in fam])
        add = [get_p(extra[k][0], extra[k][1], t) for k in extras]
        allp = np.append(ps14, add)
        adj = holm(allp)
        s = adj[steep_idx]
        p95 = adj[p95_idx]
        a = adj[anchor_new_idx] if "anchorPi_lb" in extras else None
        log(f"    {t}: Holm steepening = {s:.3f}  p95chg_op = {p95:.3f}"
            + (f"  anchorPi_lb = {a:.3f}" if a is not None else ""))

with open(OUT, "w") as f:
    f.write("\n".join(lines) + "\n")
print("\n[wrote", OUT, "]")