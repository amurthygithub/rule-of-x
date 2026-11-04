#!/usr/bin/env python3
"""Does the market pay for a higher Rule-of-40 score? New analysis for the business dashboard (3 November 2026).
Not part of Paper 1, which states that it does not test whether any version of the score predicts valuation (Section 8.6).

Data: Paper 1's core sample (data/panel_v3.csv: SEC-registered software firm-years 2010-25 after the paper's sample
rules) and public float from the 10-K cover pages (data/v3_inputs/public_float.csv, retrieved 3 Nov 2026; see
data/v3_inputs/README_retrieval.md). Public float is the market value of equity held by non-affiliates at the end of
the second fiscal quarter. Each firm-year t is matched to the float instant 120 to 260 days after its fiscal year end
(the second quarter of year t+1, by which time year t's annual report is public), the instant nearest 182 days.

Measure: log(public float / revenue of year t), an equity-value-to-sales multiple on non-affiliate equity. It
understates equity value where insiders hold much of it, ignores debt and cash, and is measured once a year.

Tests, on the GAAP operating margin and on free cash flow after SBC (the paper's basis):
  (a) log multiple on growth and margin with year fixed effects, standard errors clustered by firm; the market's
      implied weight on growth is the ratio of the two coefficients (points of margin worth one point of growth), with a
      firm-cluster bootstrap interval; and a test of the Rule-of-40 restriction (equal coefficients);
  (b) how much of the variation the score alone explains, against growth and margin entered separately;
  (c) the same by period (2010-19, 2020-25) and among firm-years scoring at least 40;
  (d) median multiple by score decile, for the dashboard.
Growth and margins are winsorized (capped, not dropped) at the 1st and 99th percentiles. Associations across firms, not causal effects.

Writes notes/open_questions/valuation.json and notes/mc_results_2026-11-03_1m/dashboard/valuation_deciles.csv,
valuation_weights.csv.  Run from anywhere:  python3 code/biz_valuation.py
"""
import csv
import json
import os

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_N = os.path.join(BASE, 'notes', 'open_questions')
OUT_D = os.path.join(BASE, 'notes', 'mc_results_2026-11-03_1m', 'dashboard')
os.makedirs(OUT_N, exist_ok=True)
rng = np.random.default_rng(20261103)

P = pd.read_csv(os.path.join(BASE, 'data', 'panel_v3.csv'), parse_dates=['fy_end'])
F = pd.read_csv(os.path.join(BASE, 'data', 'v3_inputs', 'public_float.csv'), parse_dates=['float_date'])
F = F[F.public_float_usd_thousands > 0]

m = P.merge(F, on='cik', how='left')
m['lag'] = (m.float_date - m.fy_end).dt.days
m = m[(m.lag >= 120) & (m.lag <= 260)].copy()
m['dist'] = (m.lag - 182).abs()
m = m.sort_values('dist').drop_duplicates(['cik', 'fy_end']).sort_values(['cik', 'fy_end'])
m = m[m.rev > 0].copy()
m['mult'] = m.public_float_usd_thousands * 1000.0 / m.rev
m['lm'] = np.log(m.mult)
for c in ('g', 'm_op', 'm_fcf_sbc'):
    lo, hi = m[c].quantile([0.01, 0.99])
    m[c + '_w'] = m[c].clip(lo, hi)
m['R_op_w'] = m.g_w + m.m_op_w
m['R_fcf_sbc_w'] = m.g_w + m.m_fcf_sbc_w
m['period'] = np.where(m.year <= 2019, '2010-19', '2020-25')
N_PANEL, N_MATCH = len(P), len(m)
_um = P.merge(m[['cik', 'fy_end']].assign(hit=1), on=['cik', 'fy_end'], how='left')
_um = _um[_um.hit.isna()]
_pos = set(F.cik)
UNMATCHED = dict(total=int(len(_um)), registrant_without_float=int((~_um.cik.isin(_pos)).sum()),
                 fy2025=int((_um.year == 2025).sum()))

BASES = {'gaap': ('m_op_w', 'R_op_w', 'GAAP operating margin'), 'cash': ('m_fcf_sbc_w', 'R_fcf_sbc_w', 'Free cash flow after SBC')}


def fit(df, f):
    return smf.ols(f, data=df).fit(cov_type='cluster', cov_kwds={'groups': df.cik.astype('category').cat.codes})


def weight_ci(df, mcol, B=999):
    """Firm-cluster bootstrap of the ratio beta_g / beta_m (year fixed effects)."""
    firms = df.cik.unique()
    idx = {c: df.index[df.cik == c].to_numpy() for c in firms}
    out = []
    X = pd.get_dummies(df.year.astype(str), drop_first=True, dtype=float)
    Z = np.column_stack([np.ones(len(df)), df.g_w.to_numpy(), df[mcol].to_numpy(), X.to_numpy()])
    y = df.lm.to_numpy()
    pos = {k: i for i, k in enumerate(df.index)}
    for _ in range(B):
        pick = rng.choice(firms, len(firms), replace=True)
        rows = np.concatenate([[pos[i] for i in idx[c]] for c in pick])
        b, *_ = np.linalg.lstsq(Z[rows], y[rows], rcond=None)
        if b[2] > 0:
            out.append(b[1] / b[2])
        else:
            out.append(np.inf)
    out = np.array(out)
    return float(np.quantile(out, 0.05)), float(np.quantile(out, 0.95)), float(np.mean(out <= 0) + np.mean(~np.isfinite(out)))


def analyse(df, key):
    mcol, rcol, label = BASES[key]
    df = df.dropna(subset=['lm', 'g_w', mcol]).copy()
    r = {}
    full = fit(df, f'lm ~ g_w + {mcol} + C(year)')
    score = fit(df, f'lm ~ {rcol} + C(year)')
    years = fit(df, 'lm ~ C(year)')
    bg, bm = full.params['g_w'], full.params[mcol]
    t = full.t_test(f'g_w - {mcol} = 0')
    r.update(n=int(full.nobs), firms=int(df.cik.nunique()), beta_g=float(bg), beta_g_se=float(full.bse['g_w']),
             beta_m=float(bm), beta_m_se=float(full.bse[mcol]), weight=float(bg / bm) if bm > 0 else None,
             equal_weights_p=float(t.pvalue), r2_full=float(full.rsquared), r2_score=float(score.rsquared),
             r2_years=float(years.rsquared), beta_score=float(score.params[rcol]), beta_score_se=float(score.bse[rcol]))
    r['r2_within_full'] = (r['r2_full'] - r['r2_years']) / (1 - r['r2_years'])
    r['r2_within_score'] = (r['r2_score'] - r['r2_years']) / (1 - r['r2_years'])
    if bm > 0:
        lo, hi, bad = weight_ci(df, mcol)
        r.update(weight_ci90=[lo, hi], weight_share_nonpositive=bad)
    return r


RES = {'n_panel': N_PANEL, 'n_matched': N_MATCH, 'firms': int(m.cik.nunique()), 'unmatched': UNMATCHED,
       'median_multiple': float(m.mult.median()), 'years': [int(m.year.min()), int(m.year.max())]}
for key in BASES:
    RES[key] = {'all': analyse(m, key)}
    for per in ('2010-19', '2020-25'):
        RES[key][per] = analyse(m[m.period == per].copy(), key)
    top = m[m[BASES[key][1]] >= 0.40].copy()
    RES[key]['top40'] = analyse(top, key) if len(top) > 60 else None
    noacq = m[m.acq_flag_v3.fillna(False).astype(bool) == False].copy() if 'acq_flag_v3' in m else m
    RES[key]['no_acq'] = analyse(noacq, key)

# deciles of the score: median multiple and share of firm-years, both bases
dec = []
for key in BASES:
    rcol = BASES[key][1]
    mm = m.dropna(subset=[rcol])
    q = pd.qcut(mm[rcol], 10, labels=False, duplicates='drop')
    for d_, grp in mm.groupby(q):
        dec.append({'id': f'{key}|{int(d_) + 1}', 'basis': BASES[key][2], 'decile': int(d_) + 1,
                    'score_lo': f'{100 * grp[rcol].min():.1f}', 'score_hi': f'{100 * grp[rcol].max():.1f}',
                    'score_median': f'{100 * grp[rcol].median():.1f}', 'multiple_median': f'{grp.mult.median():.2f}',
                    'multiple_p25': f'{grp.mult.quantile(.25):.2f}', 'multiple_p75': f'{grp.mult.quantile(.75):.2f}',
                    'n': int(len(grp))})
with open(os.path.join(OUT_D, 'valuation_deciles.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(dec[0].keys()), lineterminator='\n'); w.writeheader(); w.writerows(dec)

wrows = []
for key in BASES:
    for samp, lab in (('all', 'All firm-years'), ('2010-19', '2010-19'), ('2020-25', '2020-25'), ('top40', 'Score of 40 or more'),
                      ('no_acq', 'Without acquisition-affected years')):
        r = RES[key].get(samp)
        if not r:
            continue
        ci = r.get('weight_ci90', [None, None])
        wrows.append({'id': f'{key}|{samp}', 'basis': BASES[key][2], 'sample': lab, 'n': r['n'], 'firms': r['firms'],
                      'weight': '' if r['weight'] is None else f"{r['weight']:.2f}",
                      'weight_lo': '' if ci[0] is None or not np.isfinite(ci[0]) else f'{ci[0]:.2f}',
                      'weight_hi': '' if ci[1] is None or not np.isfinite(ci[1]) else f'{ci[1]:.2f}',
                      'beta_g': f"{r['beta_g']:.2f}", 'beta_m': f"{r['beta_m']:.2f}", 'equal_weights_p': f"{r['equal_weights_p']:.3f}",
                      'r2_within_full': f"{r['r2_within_full']:.3f}", 'r2_within_score': f"{r['r2_within_score']:.3f}"})
with open(os.path.join(OUT_D, 'valuation_weights.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(wrows[0].keys()), lineterminator='\n'); w.writeheader(); w.writerows(wrows)
json.dump(RES, open(os.path.join(OUT_N, 'valuation.json'), 'w'), indent=1, default=float)

print(f"panel {N_PANEL}, matched {N_MATCH} firm-years of {RES['firms']} firms, years {RES['years']}, median multiple {RES['median_multiple']:.2f}")
for r in wrows:
    print(r)
