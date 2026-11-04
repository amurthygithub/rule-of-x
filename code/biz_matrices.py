#!/usr/bin/env python3
"""Two-way grids for the business dashboard's heatmaps (3 November 2026).

  score_cap_growth   median 2036 score (central basis) by change capacity x market growth, all 1,000,000 draws of
                     the stress test (notes/mc_results_2026-11-03_1m/draws_lhs.csv.gz), six equal-width bins each
  payback_cap_win    median payback (years, whole box) by change capacity x share of attempts that create value
  gstar_cc_k         Paper 1's Rule-of-100 growth threshold by compute share x capital intensity (from
                     notes/open_questions/paths.json, computed with the paper's G100_central; psi = 0)
  gap_phi_pace       2036 score of a company automating at the central pace less one doing nothing, by pass-through x
                     rivals' pace (new analysis, paths.json)
  mult_g_m           median public float over revenue by quintile of growth x quintile of margin (free cash flow after
                     SBC), Paper 1's core sample matched as in code/biz_valuation.py (new analysis)
Writes notes/mc_results_2026-11-03_1m/dashboard/matrices.csv (long form: one row per cell) and
notes/open_questions/matrices_meta.json (whole-box medians; boom-year share and year-relative multiples for the valuation grid).
Run after code/biz_open_questions.py and code/biz_valuation.py:  python3 code/biz_matrices.py
"""
import csv
import importlib.util
import json
import os

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MC = os.path.join(BASE, 'notes', 'mc_results_2026-11-03_1m')
OUT = os.path.join(MC, 'dashboard', 'matrices.csv')
rows = []


def add(mid, ri, rl, ci, cl, value, disp, n=''):
    rows.append({'id': f'{mid}|{ri}|{ci}', 'matrix': mid, 'row': ri, 'row_label': rl, 'col': ci, 'col_label': cl,
                 'value': f'{value:.4f}' if np.isfinite(value) else '', 'display': disp, 'n': n})


def pct_bins(lo, hi, k):
    e = np.linspace(lo, hi, k + 1)
    return e, [f'{100 * e[i]:.1f}–{100 * e[i + 1]:.1f}%' for i in range(k)]


D = pd.read_csv(os.path.join(MC, 'draws_lhs.csv.gz'), usecols=['kappa_abs', 'varpi', 'G', 'R2036_net', 'payback_years'])
META = {'box_median_R2036': float(D.R2036_net.median()), 'box_median_payback': float(D.payback_years.median())}
J = json.load(open(os.path.join(MC, 'mc_claims.json')))
dim = {d['name']: d for d in J['dims']}


def grid(mid, ycol, xcol, ytitle_bins, xtitle_bins, val, fmt):
    ey, ly = ytitle_bins
    ex, lx = xtitle_bins
    iy = np.clip(np.searchsorted(ey, D[ycol].to_numpy(), side='right') - 1, 0, len(ly) - 1)
    ix = np.clip(np.searchsorted(ex, D[xcol].to_numpy(), side='right') - 1, 0, len(lx) - 1)
    v = D[val].to_numpy(float)
    bad = int((~np.isfinite(v)).sum())          # e.g. a world that never pays back is written as inf
    META[f'{mid}_nonfinite'] = bad
    assert bad == 0, f'{mid}: {bad} non-finite values would be dropped from the medians; report them before using the grid'
    for a in range(len(ly)):
        for b in range(len(lx)):
            sel = (iy == a) & (ix == b) & np.isfinite(v)
            med = float(np.median(v[sel])) if sel.sum() else float('nan')
            add(mid, a, ly[a], b, lx[b], med, fmt(med) if np.isfinite(med) else '', int(sel.sum()))


cap = pct_bins(dim['kappa_abs']['lo'], dim['kappa_abs']['hi'], 6)
grow = pct_bins(dim['G']['lo'], dim['G']['hi'], 6)
win = pct_bins(dim['varpi']['lo'], dim['varpi']['hi'], 6)
grid('score_cap_growth', 'kappa_abs', 'G', cap, grow, 'R2036_net', lambda x: f'{x:.0f}')
grid('payback_cap_win', 'kappa_abs', 'varpi', cap, win, 'payback_years', lambda x: f'{x:.1f}')

PJ = json.load(open(os.path.join(BASE, 'notes', 'open_questions', 'paths.json')))
gk = PJ['grids']['gstar_cc_k']
for a, cc in enumerate(gk['cc']):
    for b, k in enumerate(gk['k']):
        v = 100 * gk['G'][a][b]
        add('gstar_cc_k', a, f'{100 * cc:g}%', b, f'{k:+.2f}'.replace('+0.00', '0').replace('-', '\u2212'), v, f'{v:.0f}%')
gp = PJ['grids']['gap_phi_pace']
PL = {0.0: 'None (prices fixed)', 0.25: 'A quarter', 0.5: 'Half', 0.7: 'Seven tenths'}
for a, ph in enumerate(gp['phi']):
    for b, rp in enumerate(gp['pace']):
        v = 100 * gp['gap'][a][b]
        add('gap_phi_pace', a, PL[ph], b, {'slow': 'Slow', 'central': 'Central', 'fast': 'Fast'}[rp], v, f'{v:.1f}')

# valuation grid: same matching as code/biz_valuation.py
spec = importlib.util.spec_from_file_location('bv_src', os.path.join(BASE, 'code', 'biz_valuation.py'))
P = pd.read_csv(os.path.join(BASE, 'data', 'panel_v3.csv'), parse_dates=['fy_end'])
F = pd.read_csv(os.path.join(BASE, 'data', 'v3_inputs', 'public_float.csv'), parse_dates=['float_date'])
F = F[F.public_float_usd_thousands > 0]
m = P.merge(F, on='cik', how='left')
m['lag'] = (m.float_date - m.fy_end).dt.days
m = m[(m.lag >= 120) & (m.lag <= 260)].copy()
m['dist'] = (m.lag - 182).abs()
m = m.sort_values('dist').drop_duplicates(['cik', 'fy_end'])
m = m[(m.rev > 0)].dropna(subset=['g', 'm_fcf_sbc']).copy()
m['mult'] = m.public_float_usd_thousands * 1000.0 / m.rev
VJ = json.load(open(os.path.join(BASE, 'notes', 'open_questions', 'valuation.json')))
assert len(m) == VJ['cash']['all']['n'], (len(m), VJ['cash']['all']['n'])
qg, eg = pd.qcut(m.g, 5, labels=False, retbins=True)
qm, em = pd.qcut(m.m_fcf_sbc, 5, labels=False, retbins=True)
lab = lambda e, i: (f'below {100 * e[1]:.0f}%' if i == 0 else f'{100 * e[4]:.0f}% or more' if i == 4
                   else f'{100 * e[i]:.0f} to {100 * e[i + 1]:.0f}%').replace('-', '\u2212')   # true minus sign
for a in range(5):            # rows: margin, highest first
    mi = 4 - a
    for b in range(5):
        sel = (qm == mi) & (qg == b)
        med = float(m.mult[sel].median()) if sel.sum() else float('nan')
        add('mult_g_m', a, lab(em, mi), b, lab(eg, b), med, f'{med:.1f}×' if np.isfinite(med) else '', int(sel.sum()))

# context for the valuation grid: cells pool 2010-25, so report the boom years' share and the grid on multiples relative to
# each year's median multiple (the regressions in biz_valuation.py remove year effects; this grid does not)
m['rel'] = m.mult / m.groupby('year').mult.transform('median')
boom = m.year.isin([2020, 2021])
hglm = (qm == 0) & (qg == 4); lghm = (qm == 4) & (qg == 0); hghm = (qm == 4) & (qg == 4); lglm = (qm == 0) & (qg == 0)
META.update(boom_share_all=float(boom.mean()), boom_share_hglm=float(boom[hglm].mean()),
            rel_hglm=float(m.rel[hglm].median()), rel_lghm=float(m.rel[lghm].median()), rel_hghm=float(m.rel[hghm].median()),
            rel_lglm=float(m.rel[lglm].median()),
            margin_up_columns=int(sum(np.log(m.mult[(qm == 4) & (qg == b)].median()) > np.log(m.mult[(qm == 0) & (qg == b)].median())
                                      for b in range(5))))
json.dump(META, open(os.path.join(BASE, 'notes', 'open_questions', 'matrices_meta.json'), 'w'), indent=1)
print('meta', {k: round(v, 3) if isinstance(v, float) else v for k, v in META.items()})

with open(OUT, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=['id', 'matrix', 'row', 'row_label', 'col', 'col_label', 'value', 'display', 'n'], lineterminator='\n')
    w.writeheader(); w.writerows(rows)
print(f'wrote {OUT}: {len(rows)} cells')
for mid in dict.fromkeys(r['matrix'] for r in rows):
    sub = [r for r in rows if r['matrix'] == mid]
    nr, nc = 1 + max(r['row'] for r in sub), 1 + max(r['col'] for r in sub)
    print(mid, f'{nr}x{nc}')
    for a in range(nr):
        print('  ', sub[a * nc]['row_label'].ljust(20), ' '.join(r['display'].rjust(7) for r in sub if r['row'] == a))
