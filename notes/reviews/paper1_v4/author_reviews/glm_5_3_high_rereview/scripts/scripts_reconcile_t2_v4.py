#!/usr/bin/env python3
"""R2 C4a: reconcile the NEW PDF's Table 2 (printed pp. 42-43) + §5 text against the
committed outputs (scratch/notes/empirics_v3.json) at repo_v4 @ eb7537b."""
import json

BASE = "/root/tmp/rereview/diag/rereview-empirics/scratch"
E = json.load(open(f"{BASE}/notes/empirics_v3.json"))
EST, SAMP = E["estimates"], E["samples"]
VIEWS = ["E1", "E2", "E2imp4", "E2imp8"]

ROWS = [
    ("Psi0.90 slope 2010-25 0-60% GAAP", "cone_op_slope_c90_w60", "raw",
     [(-0.20,0.11), (-0.27,0.14), (-0.37,0.11), (-0.34,0.10)]),
    ("Psi0.90 slope 2010-25 0-60% cash", "cone_cash_slope_c90_w60", "raw",
     [(-0.17,0.09), (-0.22,0.12), (-0.24,0.08), (-0.24,0.08)]),
    ("Psi0.90 slope 0-40% GAAP", "cone_op_slope_c90_w40", "raw",
     [(-0.32,0.11), (-0.48,0.14), (-0.42,0.13), (-0.39,0.12)]),
    ("Psi0.90 slope 0-40% cash", "cone_cash_slope_c90_w40", "raw",
     [(-0.31,0.09), (-0.36,0.12), (-0.38,0.09), (-0.37,0.09)]),
    ("Psi0.90 slope 2010-19 GAAP", "cone_op_slope_c90_w40_2010_19", "raw",
     [(-0.20,0.11), (-0.26,0.18), (-0.27,0.14), (-0.26,0.13)]),
    ("Psi0.90 slope 2010-19 cash", "cone_cash_slope_c90_w40_2010_19", "raw",
     [(-0.19,0.13), (-0.38,0.19), (-0.36,0.15), (-0.39,0.13)]),
    ("Psi0.90 slope 2020-25 GAAP", "cone_op_slope_c90_w40_2020_25", "raw",
     [(-0.60,0.11), (-0.68,0.12), (-0.61,0.10), (-0.58,0.11)]),
    ("Psi0.90 slope 2020-25 cash", "cone_cash_slope_c90_w40_2020_25", "raw",
     [(-0.34,0.08), (-0.32,0.12), (-0.34,0.08), (-0.32,0.09)]),
    ("Steepening GAAP", "cone_op_slope_c90_w40_2020_25_minus_2010_19", "raw",
     [(-0.41,0.14), (-0.41,0.22), (-0.35,0.17), (-0.32,0.16)]),
    ("Steepening cash", "cone_cash_slope_c90_w40_2020_25_minus_2010_19", "raw",
     [(-0.15,0.14), (0.06,0.20), (0.03,0.16), (0.06,0.15)]),
    ("Local Q0.90 2010-25 GAAP", "slope_op_t90_w60", "raw",
     [(-0.47,0.16), (-0.71,0.16), (-0.55,0.15), (-0.52,0.16)]),
    ("Local Q0.90 2010-25 cash", "slope_cash_t90_w60", "raw",
     [(-0.37,0.12), (-0.44,0.13), (-0.42,0.10), (-0.41,0.10)]),
    ("Local Q0.90 2010-19 GAAP", "slope_op_2010_19", "raw",
     [(-0.34,0.17), (-0.49,0.22), (-0.43,0.19), (-0.41,0.19)]),
    ("Local Q0.90 2010-19 cash", "slope_cash_2010_19", "raw",
     [(-0.37,0.17), (-0.50,0.21), (-0.48,0.16), (-0.46,0.17)]),
    ("Local Q0.90 2020-25 GAAP", "slope_op_2020_25", "raw",
     [(-0.72,0.15), (-0.79,0.15), (-0.68,0.14), (-0.71,0.14)]),
    ("Local Q0.90 2020-25 cash", "slope_cash_2020_25", "raw",
     [(-0.40,0.11), (-0.42,0.14), (-0.38,0.10), (-0.41,0.10)]),
    ("Spend ratio", "spend_ratio", "raw",
     [(3.07,0.19), (3.51,0.24), (3.42,0.21), (3.29,0.23)]),
    ("P95 per tenfold rev GAAP", "scale_tenfold_op", "pt",
     [(2.7,2.8), (4.2,3.3), (3.8,3.0), (3.2,2.9)]),
    ("P95 per tenfold rev cash", "scale_tenfold_cash", "pt",
     [(-4.0,3.3), (-0.2,4.2), (-2.0,3.5), (-2.7,3.2)]),
    ("Capint gap 2023-25 GAAP", "capint_gap_op_2023_25", "pt",
     [(-1.5,[-8.9,5.0]), (-0.7,[-7.9,5.3]), (-0.4,[-7.7,6.2]), (-0.8,[-8.1,5.7])]),
    ("Capint gap 2023-25 cash", "capint_gap_cash_2023_25", "pt",
     [(-12.7,[-19.1,-3.6]), (-10.3,[-19.0,-3.0]), (-8.5,[-16.9,-2.6]), (-12.1,[-17.7,-3.1])]),
    ("Capint gap capex-added-back", "capint_gap_cashadd_2023_25", "pt",
     [(-4.7,[-13.0,5.8]), (-3.6,[-13.2,8.2]), (-1.3,[-10.1,8.2]), (-4.1,[-11.0,7.0])]),
    ("T(0%) change GAAP", "T_op_g00_change", "pt",
     [(0.6,[-4.1,4.6]), (0.1,[-4.4,5.3]), (0.1,[-4.4,5.1]), (0.4,[-4.0,5.3])]),
    ("T(0%) change cash", "T_cash_g00_change", "pt",
     [(-3.2,[-6.5,-0.1]), (-2.4,[-6.4,1.2]), (-3.3,[-6.3,-0.1]), (-3.2,[-6.3,0.3])]),
    ("T(20%) change GAAP", "T_op_g20_change", "pt",
     [(-10.2,[-14.8,0.7]), (-9.7,[-15.0,2.5]), (-7.1,[-12.7,4.0]), (-6.3,[-11.9,3.4])]),
    ("T(20%) change cash", "T_cash_g20_change", "pt",
     [(-2.9,[-10.9,3.6]), (-1.1,[-7.8,11.8]), (-0.9,[-7.9,9.3]), (-0.9,[-7.9,6.5])]),
    ("T(40%) change GAAP", "T_op_g40_change", "pt",
     [(-8.7,None), (None,None), (2.2,None), (-0.9,None)]),
    ("T(40%) change cash", "T_cash_g40_change", "pt",
     [(4.3,None), (None,None), (7.9,None), (7.4,None)]),
    ("Margin gap avg", "gap_avg", "pt",
     [(33.6,[28.1,36.2]), (32.6,[26.9,35.7]), (32.9,[27.8,35.8]), (33.7,[28.4,36.4])]),
    ("  S&M part", "gap_sm", "pt",
     [(15.8,[12.1,19.8]), (16.9,[12.3,19.8]), (16.9,[12.1,19.4]), (16.1,[12.1,19.6])]),
    ("  R&D part", "gap_rd", "pt",
     [(6.7,[4.5,8.8]), (6.8,[4.2,8.6]), (6.5,[4.1,8.0]), (7.0,[4.5,8.5])]),
    ("  gross margin part", "gap_gm", "pt",
     [(5.5,[-1.3,9.0]), (2.9,[-1.4,7.6]), (3.7,[-0.6,8.6]), (4.4,[-0.9,8.8])]),
    ("  G&A part", "gap_ga", "pt",
     [(5.2,[3.3,7.3]), (6.0,[3.6,7.6]), (5.6,[3.5,7.2]), (5.6,[3.4,7.2])]),
    ("Anchor Pi all-S&M", "anchor_p95_Pi_ub_med", "pt",
     [(-1.6,[-18.6,15.8]), (-7.3,[-16.8,15.4]), (-4.1,[-14.6,13.4]), (-4.1,[-15.2,15.0])]),
    ("Anchor Pi no-S&M", "anchor_p95_Pi_lb_med", "pt",
     [(19.2,[9.3,26.2]), (18.1,[7.8,25.9]), (18.8,[11.1,26.1]), (19.5,[11.7,26.5])]),
    ("Anchor Pi netted", "anchor_p95_Pi_net_med", "pt",
     [(12.3,[0.7,25.3]), (12.5,[1.2,24.8]), (12.5,[3.1,25.3]), (12.8,[3.3,25.8])]),
    ("P95 R 2016-19 GAAP", "p95_op_2016_19", "pt",
     [(55.7,[51.1,64.1]), (54.8,[47.7,62.0]), (51.2,[47.1,60.9]), (51.2,[48.0,60.9])]),
    ("P95 R 2016-19 cash", "p95_cash_2016_19", "pt",
     [(57.0,[51.2,63.8]), (54.8,[47.2,62.3]), (51.3,[46.8,57.4]), (53.0,[47.7,57.4])]),
    ("P95 R 2023-25 GAAP", "p95_op_2023_25", "pt",
     [(43.8,[41.4,46.6]), (43.0,[40.6,45.1]), (43.0,[40.8,45.2]), (43.4,[41.1,45.8])]),
    ("P95 R 2023-25 cash", "p95_cash_2023_25", "pt",
     [(44.4,[41.0,50.3]), (43.2,[39.9,49.6]), (43.2,[40.0,47.2]), (43.8,[40.5,50.3])]),
    ("P95 change GAAP", "p95_change_op", "pt",
     [(-11.9,[-20.2,-6.6]), (-11.9,[-19.3,-3.8]), (-8.2,[-16.1,-3.1]), (-7.8,[-16.1,-4.1])]),
    ("P95 change cash", "p95_change_cash", "pt",
     [(-12.6,[-20.7,-4.1]), (-11.6,[-19.1,-2.8]), (-8.0,[-14.8,-2.2]), (-9.2,[-14.7,-1.4])]),
]

mismatches, checked = [], 0
for label, name, kind, paper_vals in ROWS:
    if name not in EST:
        print(f"!! MISSING key {name} ({label})"); continue
    for vi, view in enumerate(VIEWS):
        if view not in EST[name]: continue
        rec = EST[name][view]
        p_est, p_aux = paper_vals[vi]
        scale = 100.0 if kind == "pt" else 1.0
        jest, jse, jci = rec.get("est"), rec.get("se"), rec.get("ci90")
        checked += 1
        dev = abs(p_est - jest*scale) if (p_est is not None and jest is not None) else None
        ok = dev is None or dev <= max(0.051, abs(p_est)*0.004)
        aux = ""
        if isinstance(p_aux, list) and jci is not None:
            dlo, dhi = abs(p_aux[0]-jci[0]*scale), abs(p_aux[1]-jci[1]*scale)
            ok &= dlo <= 0.051 and dhi <= 0.051
            aux = f"ci dev=({dlo:.3f},{dhi:.3f})"
        elif isinstance(p_aux, (int, float)) and jse is not None:
            dse = abs(p_aux - jse*scale)
            ok &= dse <= max(0.051, p_aux*0.02)
            aux = f"se dev={dse:.3f}"
        if not ok:
            mismatches.append((label, view, p_est, jest*scale if jest is not None else None, aux))
        if not ok:
            print(f"MISMATCH {label} {view}: paper={p_est} json={jest*scale if jest is not None else None} {aux}")

print(f"\ncells checked: {checked}, mismatches: {len(mismatches)}")
# samples
for v, n, f in [("E1",1732,284), ("E2",1330,270), ("E2imp4",1730,283), ("E2imp8",1730,283)]:
    print(v, "n:", SAMP[v]["n"], "firms:", SAMP[v]["firms"], "paper:", n, f)
for lbl, key, vals in [("acq-affected","n_affected_kept",[457,57,457,457]), ("g>50%","n_g_above_50",[105,62,88,91])]:
    print(lbl, [SAMP[v][key] for v in VIEWS], "paper:", vals)