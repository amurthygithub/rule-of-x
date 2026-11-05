#!/usr/bin/env python3
"""R2 C4b: verify the new S11 Table S19 numbers from the stored spec-curve data
(notes/spec_curve/specs.csv.gz), plus the S11 narrative shares and the forward-pairing
claims (specs_forward.csv.gz) for GLM-M9."""
import pandas as pd
import numpy as np

BASE = "/root/tmp/rereview/diag/rereview-empirics/scratch"
OUT = "/root/tmp/rereview/diag/rereview-empirics/spec_curve_check.txt"
lines = []
def log(*a):
    s = " ".join(str(x) for x in a); print(s); lines.append(s)

df = pd.read_csv(f"{BASE}/notes/spec_curve/specs.csv.gz")
log("total spec rows:", len(df))

def summarise(claim, testcol, paper, bootcol="boot_holds", val_col="value"):
    d = df[(df.claim == claim) & df[val_col].notna()]
    pt = d[testcol].mean()
    bs = d[d.boot_ok == True]
    iv = bs[bootcol].mean()
    log(f"{claim}: n_defined={len(d)} point={100*pt:.1f}% interval={100*iv:.1f}% "
        f"baseline={d.loc[d.baseline, val_col].iloc[0] if d.baseline.any() else None} "
        f"median={d[val_col].median():.2f} min={d[val_col].min():.2f} max={d[val_col].max():.2f}")
    log(f"   paper S19: {paper}")

log("=== Table S19 checks ===")
summarise("C1", "holds_a", "n=5740? 94.3% point, 29.0% interval, baseline -11.9, median -4.9, -14.4 to +2.6", "boot_holds")
summarise("C2", "holds_a", "100% point, 42.2% interval, baseline -12.6, median -7.2, -13.6 to -1.0", "boot_holds")
summarise("C3", "holds_a", "GAAP above -1: 100%/100%", "boot_holds")
log(f"   C3 below zero: {100*df[(df.claim=='C3') & df.value.notna()].holds_b.mean():.1f}% point, "
    f"{100*df[(df.claim=='C3') & df.value.notna() & (df.boot_ok==True)].boot_holds_b.mean():.1f}% interval (paper 100%/96.1%)")
log(f"   C3 above -0.5: {100*df[(df.claim=='C3') & df.value.notna()].holds_c.mean():.1f}% (paper 65.5%)")
summarise("C4", "holds_a", "cash above -1: 100%/100%", "boot_holds")
log(f"   C4 below zero: {100*df[(df.claim=='C4') & df.value.notna()].holds_b.mean():.1f}% point, "
    f"{100*df[(df.claim=='C4') & df.value.notna() & (df.boot_ok==True)].boot_holds_b.mean():.1f}% interval (paper 100%/99.2%)")
log(f"   C4 above -0.5: {100*df[(df.claim=='C4') & df.value.notna()].holds_c.mean():.1f}% (paper 87.9%)")
summarise("C5", "holds_a", "steepening GAAP: 91.9% point, 18.4% interval, baseline -0.41, median -0.24, -0.49 to +0.20", "boot_holds")
c6 = df[(df.claim == "C6") & df.value.notna()]
log(f"C6: n_defined={len(c6)} point(non-negative)={100*(c6.value>=0).mean():.1f}% (paper 74.4%) "
    f"interval(not below zero)={100*c6[c6.boot_ok==True].boot_holds.mean():.1f}% (paper 99.0%) "
    f"baseline={c6.loc[c6.baseline,'value'].iloc[0]:.2f} median={c6.value.median():.2f}")
summarise("C7", "holds_a", "spend ratio 3.0-3.5: 960 samples, 32.5%, baseline 3.07, median 3.65, 3.05-3.80")
c7s = df[(df.claim == "C7s") & df.value.notna()]
log(f"C7s: n={len(c7s)} holds={100*c7s.holds_a.mean():.1f}% (paper 31.0%) median={c7s.value.median():.2f} range {c7s.value.min():.2f} to {c7s.value.max():.2f}")
summarise("C8a", "holds_a", "anchor Pi_lb > 0: 100%/99.2%, baseline +19.2, median +16.4, +6.3 to +28.1", "boot_holds")
summarise("C8b", "holds_a", "Pi_net > 0: 99.7%/38.4%, baseline +12.3, median +9.8, -0.2 to +27.1", "boot_holds")
c8c = df[(df.claim == "C8c") & df.value.notna()]
log(f"C8c: n={len(c8c)} above zero={100*(c8c.value>0).mean():.1f}% (paper 22.3%) baseline={c8c.loc[c8c.baseline,'value'].iloc[0]:.2f} "
    f"median={c8c.value.median():.2f} range {c8c.value.min():.2f} to {c8c.value.max():.2f}")

# Baseline spec count: 155,328 total? Paper says "155,328 specifications"
log(f"\ntotal defined specifications: {int(df.value.notna().sum())} of {len(df)} rows; paper §5.9 says 155,328 specifications")

# === forward pairing (M9) ===
log("\n=== Forward pairing (GLM-M9, S11) ===")
fw = pd.read_csv(f"{BASE}/notes/spec_curve/specs_forward.csv.gz")
log("forward rows:", len(fw), "claims:", sorted(fw.claim.unique()))
log(fw.columns.tolist())
fwd_base = fw[fw.baseline == True] if "baseline" in fw.columns else None
if fwd_base is not None and len(fwd_base):
    for _, r in fwd_base.iterrows():
        log(f"  claim={r.claim} value={r.get('value')} boot=({r.get('boot_lo')},{r.get('boot_hi')})")

with open(OUT, "w") as f:
    f.write("\n".join(lines) + "\n")
print("\n[wrote", OUT, "]")