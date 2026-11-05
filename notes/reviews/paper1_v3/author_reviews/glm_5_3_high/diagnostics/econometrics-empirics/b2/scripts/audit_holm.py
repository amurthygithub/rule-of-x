#!/usr/bin/env python3
"""B2: familywise-correction audit. Paper claims (main §5.1 printed p.42, §5.2 p.43,
§5.3 pp.43-44, §5.7 p.46, §5.8 p.47) vs the headline14B family in empirics_v3.json."""
import json

BASE = "/root/tmp/ruleof40/diagnostics/econometrics-empirics/baseline"
E = json.load(open(f"{BASE}/empirics_v3.json"))
F = E["families"]

print("Families present:", list(F.keys()))
fam = F["headline14B"]["contrasts"]
print(f"headline14B members: {len(fam)}\n")
def fmt_p(x):
    return "None" if x is None else f"{x:.4g}"

for c in fam:
    print(f"- {c['key']:<45} {c['label'][:60]}")
    print(f"    h0={c['h0']} est={c['est']:.4f}  p(n/p/b)={fmt_p(c['p_normal'])}/{fmt_p(c['p_percentile'])}/{fmt_p(c['p_basic'])}"
          f"  Holm={fmt_p(c['holm_normal'])}/{fmt_p(c['holm_percentile'])}/{fmt_p(c['holm_basic'])}  RW={fmt_p(c['romano_wolf'])}")

def get(key):
    for c in fam:
        if c["key"] == key:
            return c
    raise KeyError(key)

print("\n--- Claim-by-claim checks ---")
checks = [
    # (claim text, stat key, claimed Holm range or survival pattern)
    ("GAAP P95 decline survives 10% under normal+percentile+RW, not basic; "
     "Holm p 0.054-0.208; RW 0.097; not at 5% under any",
     "p95_change_op", lambda c: (c["holm_normal"], c["holm_percentile"], c["holm_basic"], c["romano_wolf"])),
    ("Cash P95 decline survives no procedure, even at 10%",
     "p95_change_cash", lambda c: (c["holm_normal"], c["holm_percentile"], c["holm_basic"], c["romano_wolf"])),
    ("Steepening (GAAP 2020-25 minus 2010-19 slope diff): Holm p 0.037-0.060, RW 0.064; "
     "survives 10% under every procedure, 5% under two of four",
     "steep", None),
    ("Psi slope negative (GAAP): Holm p 0.26-0.45",
     "psi_op_E1_vs_0", lambda c: (c["holm_normal"], c["holm_percentile"], c["holm_basic"])),
    ("Psi slope negative (cash): Holm p 0.35-0.62",
     "psi_cash_E1_vs_0", lambda c: (c["holm_normal"], c["holm_percentile"], c["holm_basic"])),
    ("Psi slope above -1 survives Holm at 5% on both bases",
     "psi_op_E1_vs_m1", lambda c: (c["holm_normal"], c["holm_percentile"], c["holm_basic"])),
]
for text, key, fn in checks:
    if key == "steep":
        # find the steepening member
        cands = [c for c in fam if "minus" in c["statistic"] and "cone" in c["statistic"]]
        print(f"\nSTEEPENING: candidates {[c['statistic'] for c in cands]}")
        for c in cands:
            print(f"  {c['key']}: est={c['est']:.4f} p={c['p_normal']:.4g}/{c['p_percentile']}/{c['p_basic']}"
                  f" Holm={c['holm_normal']:.4g}/{c['holm_percentile']}/{c['holm_basic']} RW={c['romano_wolf']}")
        continue
    try:
        c = get(key)
        print(f"\n{text}")
        print(f"  -> {fn(c)}")
    except KeyError:
        print(f"\n{text}\n  !! key {key} not found in headline14B")

# Also: how many members test slopes against -1 and margin gap positive-by-construction?
print("\n--- §5.1 disclosure check: members that 'say little' ---")
for c in fam:
    if c["h0"] == -1.0 or "gap" in c["statistic"]:
        print(f"  {c['key']}: h0={c['h0']}  Holm(n/p/b)={c['holm_normal']:.3g}/{c['holm_percentile']}/{c['holm_basic']}")