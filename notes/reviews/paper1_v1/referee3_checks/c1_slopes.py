import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd, lib, json
import statsmodels.formula.api as smf
V = lib.V
out = {}
print('Check 1: IRLS (statsmodels) vs exact LP, tau=0.9, g in [0,0.6]')
for vn in ['E1', 'E2', 'E2x25']:
    for m in ['m_op', 'm_fcf_sbc']:
        d = V[vn][['cik', 'period', 'g', m]].dropna(); d = d[(d.g >= 0) & (d.g <= 0.6)]
        b_sm = smf.quantreg(f'{m} ~ g', d).fit(q=0.9, max_iter=5000).params['g']
        b_lp = lib.qr_lp(d[m], d.g, 0.9)[1]
        print(vn, m, len(d), round(b_sm, 4), round(b_lp, 4))
print('\nCheck 2: sensitivity to tau and window (exact LP)')
taus = [0.75, 0.80, 0.85, 0.90, 0.95]
wins = [(0, 0.4), (0, 0.6), (0, 0.8), (0, 1.0), (-0.1, 0.6), (0.05, 0.6)]
res = {}
for vn in ['E1', 'E2']:
    for m in ['m_op', 'm_fcf_sbc']:
        d0 = V[vn][['cik', 'period', 'g', m]].dropna()
        row = {}
        for (lo, hi) in wins:
            d = d0[(d0.g >= lo) & (d0.g <= hi)]
            row[f'{lo}-{hi}'] = [round(lib.qr_lp(d[m], d.g, t)[1], 2) for t in taus]
        res[f'{vn}|{m}'] = row
        print(vn, m)
        for k, v in row.items(): print('   window', k, 'taus', taus, '->', v)
json.dump(res, open('c1_results.json', 'w'), indent=1)
