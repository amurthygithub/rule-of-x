import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd, lib
exec(open('c7_impute.py').read().split("fl = E1[")[0])      # reuse variant() from c7_impute.py
def more(v):
    o = {}
    for m in ['m_op', 'm_fcf_sbc']:
        for nm, per in [('10_19', ['2010-15', '2016-19']), ('20_25', ['2020-22', '2023-25'])]:
            d = v[['g', m, 'period']].dropna(); d = d[(d.g >= 0) & (d.g <= 0.6) & d.period.isin(per)]
            o[f'slope_{m}_{nm}'] = lib.qr_lp(d[m].values, d.g.values, 0.9)[1]
    d = v[v.period == '2023-25']
    for R in ['R_op', 'R_cash']:
        z = d[['hi_k', R]].dropna(); o['capgap_' + R] = 100 * (np.quantile(z.loc[z.hi_k == 1, R], .95) - np.quantile(z.loc[z.hi_k == 0, R], .95))
    # spend ratio with E1 benchmark G_t
    x = v[(v.g > v.G_t) & v.sm_lag_share.between(0.01, 1.5)]
    o['spend_ratio'] = float((x.sm_lag_share / (x.g - x.G_t)).median())
    return o
rows = {'E1': more(V['E1']), 'E2 (paper)': more(V['E2']), 'E2x25': more(V['E2x25'])}
for M in [2, 4, 8]:
    v = variant(M)
    v['hi_k'] = v.groupby('period')['capex_int'].transform(lambda x: (x > x.median()).astype(float))
    rows[f'Imputed M={M}'] = more(v)
print(pd.DataFrame(rows).T.round(2).to_string())
