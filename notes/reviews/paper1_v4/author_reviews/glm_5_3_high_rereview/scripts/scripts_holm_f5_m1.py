#!/usr/bin/env python3
"""R2 (re-review): GLM-F5 and GLM-M1 rows. Recompute Holm adjusted p-values from the
stored (re-estimated, v4 build) p-values in notes/empirics_v3.json.

F5: 18-test family = headline14B (14 members) + T(20%) GAAP + T(20%) cash + T(0%) cash
    + anchor Pi_lb. Paper (M 5.1, printed p. 43) claims: steepening 0.037/0.132/0.036,
    GAAP p95 decline 0.061/0.104/0.270, anchor 0.004/0.120/0.036 (normal/percentile/basic).
M1: §5.8 anchor Holm "over 14 tests (the family's estimable members and the anchor)":
    13 estimable family-B tests + anchor. Also compute the 15-test count (adding the
    non-estimable T(40%) cash at p = 1) for comparison (response says 0.006/0.096/0.030).
"""
import json
import numpy as np

BASE = "/root/tmp/rereview/diag/rereview-empirics/scratch"
E = json.load(open(f"{BASE}/notes/empirics_v3.json"))
EST, FAM = E["estimates"], E["families"]
OUT = "/root/tmp/rereview/diag/rereview-empirics/holm_f5_m1.txt"

lines = []
def log(*a):
    s = " ".join(str(x) for x in a); print(s); lines.append(s)

def holm(pvals):
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    adj = np.empty(n)
    running = 0.0
    for i, idx in enumerate(order):
        running = max(running, (n - i) * p[idx])
        adj[idx] = min(1.0, running)
    return adj

types = ["normal", "percentile", "basic"]
fam = FAM["headline14B"]["contrasts"]
log("headline14B members:", len(fam))
log("keys:", [c["key"] for c in fam])

def get_p(stat, view, t):
    r = EST[stat][view]
    v = r.get(f"p_{t}")
    return 1.0 if v is None else v

# which members are estimable?
log("\nmember estimability:")
for c in fam:
    log(f"  {c['key']}: p_normal={c.get('p_normal')} p_percentile={c.get('p_percentile')} p_basic={c.get('p_basic')}")

# --- F5: 18-test family ---
log("\n=== F5: 18-test family (14 + T20 GAAP + T20 cash + T0 cash + anchor) ===")
extras = [("T20_GAAP", "T_op_g20_change"), ("T20_cash", "T_cash_g20_change"),
          ("T0_cash", "T_cash_g00_change"), ("anchor", "anchor_p95_Pi_lb_med")]
steep_key = "psi_op_E1_2020_25_minus_2010_19"
p95_key = "p95chg_op_E1"
for t in types:
    ps14 = [c.get(f"p_{t}") if c.get(f"p_{t}") is not None else 1.0 for c in fam]
    add = [get_p(s, "E1", t) for _, s in extras]
    allp = np.array(ps14 + add)
    adj = holm(allp)
    i_st = ps14 and list(fam[i]["key"] for i in range(len(fam))).index(steep_key)
    kidx = [c["key"] for c in fam]
    log(f"  {t}: steepening Holm = {adj[kidx.index(steep_key)]:.3f}, "
        f"p95chg_op = {adj[kidx.index(p95_key)]:.3f}, anchor = {adj[14 + 3]:.3f} "
        f"(unadj: steep {allp[kidx.index(steep_key)]:.4g}, p95 {allp[kidx.index(p95_key)]:.4g}, "
        f"anchor {allp[17]:.4g})")
log("  paper M 5.1 claims: steepening 0.037/0.132/0.036; p95 0.061/0.104/0.270; anchor 0.004/0.120/0.036")

# --- M1: 14-test (13 estimable + anchor) and 15-test ---
log("\n=== M1: §5.8 anchor count ===")
for t in types:
    # 14 estimable members minus non-estimable T40_cash (p=1, no interval) => 13 estimable
    est14 = [c for c in fam if c.get(f"p_{t}") is not None]
    ps13 = [c[f"p_{t}"] for c in est14]
    pa = get_p("anchor_p95_Pi_lb_med", "E1", t)
    adj14 = holm(np.append(ps13, pa))
    # 15-test: all 14 members (incl. non-estimable at p=1) + anchor
    ps14 = [c.get(f"p_{t}") if c.get(f"p_{t}") is not None else 1.0 for c in fam]
    adj15 = holm(np.append(ps14, pa))
    log(f"  {t}: anchor unadj p = {pa:.4g}; Holm 14-test (13 estimable + anchor) = {adj14[-1]:.3f}; "
        f"15-test (all 14 + anchor) = {adj15[-1]:.3f}")
log("  paper M 5.8 should print the 14-test values with the count sentence; response says 15-test = 0.006/0.096/0.030")

with open(OUT, "w") as f:
    f.write("\n".join(lines) + "\n")
print("\n[wrote", OUT, "]")