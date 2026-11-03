import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd, lib
V = lib.V
rng = np.random.default_rng(5)
def T(z, g0, m):
    s = z.loc[z.g >= g0, m]
    return g0 + float(np.quantile(s, .95)) if len(s) >= 10 else np.nan
for vn in ['E1', 'E2']:
    for m in ['m_op', 'm_fcf_sbc']:
        d = V[vn][['cik', 'period', 'g', m]].dropna(); d = d[d.period.isin(['2016-19', '2023-25'])]
        n23 = int(((d.period == '2023-25') & (d.g >= .4)).sum()); n16 = int(((d.period == '2016-19') & (d.g >= .4)).sum())
        st = lambda z: T(z[z.period == '2023-25'], .4, m) - T(z[z.period == '2016-19'], .4, m)
        bs = lib.boot(d, st, 1000, rng)
        top = d[(d.period == '2023-25') & (d.g >= .4)].sort_values(m, ascending=False)
        print(f'{vn} {m}: n(g>=40%) 2023-25 = {n23}, 2016-19 = {n16}; est {100*st(d):+.1f}; NaN draws {np.isnan(bs).mean():.3f}; '
              f'percentile CI [{100*np.nanquantile(bs,.05):+.1f}, {100*np.nanquantile(bs,.95):+.1f}]; distinct values in draws {len(np.unique(np.round(bs[~np.isnan(bs)],8)))}; '
              f'top-3 margins 2023-25: {[round(100*x,1) for x in top[m].head(3)]}')
# small-sample bias of the 95th percentile: draw n obs from the 2016-19 g>=40% cell (E1) and compare with the cell's own P95
for m in ['m_op', 'm_fcf_sbc']:
    for vn in ['E1', 'E2']:
        cell = V[vn][(V[vn].period.isin(['2010-15', '2016-19', '2020-22'])) & (V[vn].g >= .4)][m].dropna().values
        full = np.quantile(cell, .95)
        for n in [12, 18, 30, 80]:
            sims = [np.quantile(rng.choice(cell, n, replace=False), .95) for _ in range(4000)]
            print(f'{vn} {m}: pooled 2010-22 cell (n={len(cell)}) P95 {100*full:.1f}; mean P95 from n={n} draws {100*np.mean(sims):.1f} (bias {100*(np.mean(sims)-full):+.1f}), sd {100*np.std(sims):.1f}')
