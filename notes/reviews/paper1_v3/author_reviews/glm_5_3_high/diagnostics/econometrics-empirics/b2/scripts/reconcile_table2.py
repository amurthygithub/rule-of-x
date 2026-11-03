#!/usr/bin/env python3
"""B2 reconciliation: paper Table 2 / §5 printed numbers vs author's committed
baseline outputs (empirics_v3.json, frontier_slope_v3.json, etc.).

Paper: "The Rule of 40 as a Price Line..." (Murthy, Nov 2026), printed pp. 40-47.
Every paper value is transcribed from the supplied PDF page extractions
(p040.txt-p047.txt) into PAPER below. Units: paper reports points (x100) for
levels; slopes and ratios are unit-free. JSON stores fractions.
"""
import json, sys

BASE = "/root/tmp/ruleof40/diagnostics/econometrics-empirics/baseline"
E = json.load(open(f"{BASE}/empirics_v3.json"))
EST = E["estimates"]
SAMP = E["samples"]

VIEWS = ["E1", "E2", "E2imp4", "E2imp8"]

# (label, json stat name, paper values per view, scale factor, kind)
# kind: 'pt' = points (x100), 'raw' = as-is, 'ratio' = as-is
# Each paper value: (point_est, se) or (point_est, [lo, hi]) or point_est
ROWS = [
    # --- A. Model-facing statistics (Table 2 p.40) ---
    ("Psi0.90 slope 2010-25, 0-60% GAAP", "cone_op_slope_c90_w60", "raw",
     [(-0.22,0.11), (-0.29,0.14), (-0.39,0.11), (-0.36,0.10)]),
    ("Psi0.90 slope 2010-25, 0-60% cash", "cone_cash_slope_c90_w60", "raw",
     [(-0.16,0.10), (-0.22,0.11), (-0.25,0.08), (-0.26,0.08)]),
    ("Psi0.90 slope 2010-25, 0-40% GAAP", "cone_op_slope_c90_w40", "raw",
     [(-0.31,0.10), (-0.49,0.14), (-0.44,0.12), (-0.40,0.12)]),
    ("Psi0.90 slope 2010-25, 0-40% cash", "cone_cash_slope_c90_w40", "raw",
     [(-0.27,0.10), (-0.37,0.11), (-0.39,0.09), (-0.37,0.08)]),
    ("Psi0.90 slope 2010-19, 0-40% GAAP", "cone_op_slope_c90_w40_2010_19", "raw",
     [(-0.22,0.10), (-0.28,0.17), (-0.29,0.13), (-0.28,0.12)]),
    ("Psi0.90 slope 2010-19, 0-40% cash", "cone_cash_slope_c90_w40_2010_19", "raw",
     [(-0.16,0.13), (-0.39,0.18), (-0.37,0.15), (-0.38,0.13)]),
    ("Psi0.90 slope 2020-25, 0-40% GAAP", "cone_op_slope_c90_w40_2020_25", "raw",
     [(-0.60,0.11), (-0.66,0.12), (-0.60,0.10), (-0.58,0.11)]),
    ("Psi0.90 slope 2020-25, 0-40% cash", "cone_cash_slope_c90_w40_2020_25", "raw",
     [(-0.35,0.08), (-0.34,0.11), (-0.35,0.08), (-0.33,0.08)]),
    ("Steepening 2020-25 minus 2010-19 GAAP", "cone_op_slope_c90_w40_2020_25_minus_2010_19", "raw",
     [(-0.38,0.13), (-0.37,0.21), (-0.31,0.16), (-0.30,0.15)]),
    ("Steepening 2020-25 minus 2010-19 cash", "cone_cash_slope_c90_w40_2020_25_minus_2010_19", "raw",
     [(-0.19,0.14), (0.05,0.20), (0.02,0.16), (0.05,0.15)]),
    ("Local Q0.90 slope 2010-25 GAAP", "slope_op_t90_w60", "raw",
     [(-0.41,0.14), (-0.61,0.17), (-0.51,0.15), (-0.46,0.14)]),
    ("Local Q0.90 slope 2010-25 cash", "slope_cash_t90_w60", "raw",
     [(-0.35,0.11), (-0.43,0.12), (-0.42,0.09), (-0.39,0.09)]),
    ("Local Q0.90 slope 2010-19 GAAP", "slope_op_2010_19", "raw",
     [(-0.29,0.14), (-0.43,0.21), (-0.41,0.17), (-0.34,0.16)]),
    ("Local Q0.90 slope 2010-19 cash", "slope_cash_2010_19", "raw",
     [(-0.20,0.15), (-0.48,0.19), (-0.48,0.16), (-0.42,0.16)]),
    ("Local Q0.90 slope 2020-25 GAAP", "slope_op_2020_25", "raw",
     [(-0.71,0.15), (-0.79,0.15), (-0.68,0.15), (-0.70,0.14)]),
    ("Local Q0.90 slope 2020-25 cash", "slope_cash_2020_25", "raw",
     [(-0.40,0.10), (-0.42,0.13), (-0.37,0.09), (-0.41,0.09)]),
    ("Spend-to-excess-growth ratio (median)", "spend_ratio", "raw",
     [(3.02,0.19), (3.47,0.25), (3.34,0.22), (3.15,0.23)]),
    ("P95 of R per tenfold revenue GAAP", "scale_tenfold_op", "pt",
     [(2.4,2.8), (4.0,3.0), (3.4,2.9), (3.2,2.9)]),
    ("P95 of R per tenfold revenue cash", "scale_tenfold_cash", "pt",
     [(-4.1,3.4), (-1.1,3.9), (-2.5,3.3), (-2.8,3.1)]),
    ("Capital-intensity gap P95 R 2023-25 GAAP", "capint_gap_op_2023_25", "pt",
     [(-1.8,[-9.5,4.5]), (-0.7,[-7.9,5.4]), (-0.8,[-8.3,5.7]), (-1.2,[-8.8,5.3])]),
    ("Capital-intensity gap P95 R 2023-25 cash", "capint_gap_cash_2023_25", "pt",
     [(-12.5,[-20.1,-3.9]), (-7.4,[-18.3,-2.5]), (-8.3,[-17.1,-2.6]), (-12.3,[-17.9,-3.1])]),
    ("Cap-int gap capex added back", "capint_gap_cashadd_2023_25", "pt",
     [(-4.6,[-14.6,6.0]), (-0.2,[-12.3,9.0]), (0.1,[-10.6,8.5]), (-4.2,[-11.9,7.0])]),
    ("Change in T(0%), GAAP", "T_op_g00_change", "pt",
     [(0.8,[-4.7,4.5]), (0.4,[-4.9,5.4]), (0.4,[-4.9,4.9]), (0.8,[-4.8,4.9])]),
    ("Change in T(0%), cash", "T_cash_g00_change", "pt",
     [(-3.3,[-6.4,-0.2]), (-2.5,[-6.5,1.2]), (-3.3,[-6.4,-0.4]), (-3.2,[-6.2,0.1])]),
    ("Change in T(20%), GAAP", "T_op_g20_change", "pt",
     [(-10.2,[-15.1,1.1]), (-9.7,[-15.1,3.0]), (-7.2,[-12.8,4.2]), (-6.3,[-12.0,3.7])]),
    ("Change in T(20%), cash", "T_cash_g20_change", "pt",
     [(-3.0,[-10.9,3.4]), (-1.1,[-7.7,13.0]), (-1.3,[-8.7,8.6]), (-1.8,[-8.7,5.8])]),
    ("Change in T(40%), GAAP (dagger)", "T_op_g40_change", "pt",
     [(-9.9,None), (None,None), (1.0,None), (-2.0,None)]),
    ("Change in T(40%), cash (dagger)", "T_cash_g40_change", "pt",
     [(1.6,None), (None,None), (7.6,None), (7.2,None)]),
    ("Near-frontier margin gap, avg of bands", "gap_avg", "pt",
     [(34.5,[28.6,37.7]), (32.7,[26.6,35.8]), (33.5,[28.0,36.6]), (34.7,[28.9,38.0])]),
    ("  of which selling and marketing", "gap_sm", "pt",
     [(16.0,[12.4,20.0]), (16.8,[12.6,20.3]), (17.1,[12.3,19.9]), (16.1,[12.5,20.0])]),
    ("  of which R&D", "gap_rd", "pt",
     [(7.1,[4.6,8.8]), (6.9,[4.0,8.5]), (6.5,[4.2,8.1]), (7.1,[4.6,8.5])]),
    ("  of which gross margin", "gap_gm", "pt",
     [(5.7,[-1.4,9.4]), (2.9,[-1.7,7.8]), (4.0,[-0.7,8.7]), (4.9,[-0.7,9.2])]),
    ("  of which G&A", "gap_ga", "pt",
     [(5.5,[3.4,7.5]), (6.2,[3.3,7.6]), (5.7,[3.4,7.4]), (5.8,[3.4,7.4])]),
    # --- Anchor rows (Table 2 p.41) ---
    ("Anchor: median Pi, all S&M buys growth", "anchor_p95_Pi_ub_med", "pt",
     [(-1.3,[-18.2,16.4]), (-7.0,[-17.0,15.4]), (-0.5,[-13.6,14.5]), (-0.7,[-13.7,15.9])]),
    ("Anchor: median Pi, no S&M buys growth", "anchor_p95_Pi_lb_med", "pt",
     [(19.5,[8.1,26.5]), (18.5,[6.8,26.0]), (20.0,[11.3,26.9]), (20.2,[12.2,27.1])]),
    ("Anchor: median Pi, maintenance-netted", "anchor_p95_Pi_net_med", "pt",
     [(12.4,[0.3,25.7]), (12.2,[0.5,24.7]), (13.2,[3.5,26.1]), (13.2,[3.7,26.5])]),
    # --- B. Distribution of reported scores (E1 primary; other views for change only) ---
    ("P95 of R, 2016-19, GAAP", "p95_op_2016_19", "pt",
     [(55.9,[51.1,63.7]), (54.3,[46.6,61.5]), (51.1,[46.9,56.8]), (51.8,[47.8,57.1])]),
    ("P95 of R, 2016-19, cash", "p95_cash_2016_19", "pt",
     [(57.3,[51.1,67.3]), (53.9,[46.6,60.6]), (51.7,[46.7,57.3]), (53.1,[48.1,57.4])]),
    ("P95 of R, 2023-25, GAAP", "p95_op_2023_25", "pt",
     [(43.9,[41.5,47.2]), (42.8,[40.4,45.1]), (43.2,[40.7,45.7]), (43.5,[41.1,46.0])]),
    ("P95 of R, 2023-25, cash", "p95_cash_2023_25", "pt",
     [(44.6,[41.5,50.6]), (43.1,[39.4,49.1]), (43.4,[40.2,48.8]), (43.9,[40.6,50.6])]),
    ("Change in P95 of R, GAAP", "p95_change_op", "pt",
     [(-11.9,[-20.3,-6.4]), (-11.4,[-18.7,-3.0]), (-7.8,[-14.6,-2.7]), (-8.3,[-15.1,-3.7])]),
    ("Change in P95 of R, cash", "p95_change_cash", "pt",
     [(-12.7,[-21.6,-4.2]), (-10.9,[-17.7,-2.1]), (-8.3,[-15.2,-1.9]), (-9.3,[-15.1,-1.3])]),
]

SAMPLE_ROWS = [
    ("Firm-years (E1/E2/imp4/imp8)", [(1788,292),(1378,277),(1786,291),(1786,291)]),
    ("of which acquisition-affected", [466,58,466,466]),
    ("Firm-years with g>50%", [106,62,89,92]),
]

def fmt(x, nd=2):
    if x is None: return "—"
    return f"{x:.{nd}f}"

mismatches, checked = [], 0
print(f"{'statistic':<44} {'view':<7} {'paper':>18} {'json':>18} {'ok?':>5}")
for label, name, kind, paper_vals in ROWS:
    if name not in EST:
        print(f"!! MISSING json key: {name} ({label})")
        continue
    for vi, view in enumerate(VIEWS):
        if view not in EST[name]:
            continue
        rec = EST[name][view]
        pv = paper_vals[vi]
        scale = 100.0 if kind == "pt" else 1.0
        jest = rec.get("est")
        jse = rec.get("se")
        jci = rec.get("ci90")
        p_est, p_aux = pv
        checked += 1
        # point estimate
        dev = None
        if p_est is not None and jest is not None:
            dev = abs(p_est - jest*scale)
        ok_pt = dev is None or dev <= max(0.051, abs(p_est)*0.004)  # rounding to 1dp = 0.05 tolerance
        ok_aux = True
        aux_dev = ""
        if isinstance(p_aux, list) and jci is not None:
            jlo, jhi = jci[0]*scale, jci[1]*scale
            dlo, dhi = abs(p_aux[0]-jlo), abs(p_aux[1]-jhi)
            ok_aux = dlo <= 0.051 and dhi <= 0.051
            aux_dev = f"ci dev=({dlo:.3f},{dhi:.3f})"
        elif isinstance(p_aux, (int,float)) and jse is not None:
            dse = abs(p_aux - jse*scale)
            ok_aux = dse <= max(0.051, p_aux*0.02)
            aux_dev = f"se dev={dse:.3f}"
        status = "OK" if (ok_pt and ok_aux) else "MISMATCH"
        if status == "MISMATCH":
            mismatches.append((label, view, pv, jest*scale if jest is not None else None,
                               (jse*scale if jse is not None else None),
                               (jci and [jci[0]*scale, jci[1]*scale]), aux_dev))
        print(f"{label:<44} {view:<7} {str(p_est):>18} {fmt(jest*scale if jest is not None else None):>18} {status:>5} {aux_dev}")

print("\n--- Sample counts ---")
for label, vals in SAMPLE_ROWS:
    js = [SAMP[v]["n"] if isinstance(vals[0], tuple) else SAMP[v].get("n_affected_kept" if "acquisition" in label else "n_g_above_50", SAMP[v].get("n")) for v in VIEWS]
    print(f"{label}: paper={vals} json={js}")

print(f"\nTotal cells checked (point est): {checked}")
print(f"Mismatches: {len(mismatches)}")
for m in mismatches:
    print(" MISMATCH:", m)