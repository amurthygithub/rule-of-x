import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd, lib, statsmodels.formula.api as smf
V = lib.V
for vn in ['E1', 'E2', 'E2x25']:
    for m in ['m_op', 'm_fcf_sbc']:
        d = V[vn][['cik', 'year', 'g', m]].dropna(); d = d[d.g <= 1.5]
        po = smf.ols(f'{m} ~ g + C(year)', d).fit(cov_type='cluster', cov_kwds={'groups': d['cik']})
        fe = smf.ols(f'{m} ~ g + C(year) + C(cik)', d).fit(cov_type='cluster', cov_kwds={'groups': d['cik']})
        d2 = d.sort_values(['cik', 'year']).copy(); d2['gl'] = d2.groupby('cik').g.shift(1); d2['yl'] = d2.groupby('cik').year.shift(1)
        d2 = d2[d2.yl == d2.year - 1].dropna()
        fe2 = smf.ols(f'{m} ~ g + gl + C(year) + C(cik)', d2).fit(cov_type='cluster', cov_kwds={'groups': d2['cik']})
        # IV: instrument g_t with g_{t-1} within firm (lagged growth as instrument for current growth, demeaned): manual 2SLS via FE first stage
        print(f"{vn} {m}: pooled {po.params['g']:+.3f} ({po.bse['g']:.3f}); FE {fe.params['g']:+.3f} ({fe.bse['g']:.3f}) n={len(d)}; FE with lagged g: g {fe2.params['g']:+.3f} ({fe2.bse['g']:.3f}), g_lag {fe2.params['gl']:+.3f} ({fe2.bse['gl']:.3f})")
# within-firm R^2 of growth: share of growth variance that is within firm
d = V['E1'][['cik', 'g']].dropna(); d = d[d.g <= 1.5]
w = d.g - d.groupby('cik').g.transform('mean')
print('E1 within-firm share of growth variance: %.2f' % (w.var() / d.g.var()))
