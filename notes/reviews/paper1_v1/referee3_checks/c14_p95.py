import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd, lib
V = lib.V
def wq(x, w, q):
    o = np.argsort(x); x, w = x[o], w[o]; c = (np.cumsum(w) - 0.5 * w) / w.sum(); return float(np.interp(q, c, x))
for vn in ['E1', 'E2']:
    v = V[vn]
    for R in ['R_op', 'R_cash']:
        a = v[(v.period == '2016-19')][['g', R, 'rev_lag', 'year']].dropna(); b = v[(v.period == '2023-25')][['g', R, 'rev_lag', 'year']].dropna()
        base = np.quantile(b[R], .95) - np.quantile(a[R], .95)
        # real threshold: 2016-19 dollars, CPI-U ratio 2024/2017 about 1.27 (BLS annual averages 313.7 / 245.1)
        b2 = b[b.rev_lag >= 100e6 * 313.7 / 245.1]
        real = np.quantile(b2[R], .95) - np.quantile(a[R], .95)
        # reweight 2023-25 to the 2016-19 growth distribution (10 bins on pooled deciles)
        edges = np.quantile(pd.concat([a.g, b.g]), np.linspace(0, 1, 11)); edges[0] -= 1; edges[-1] += 1
        ca = pd.cut(a.g, edges, labels=False); cb = pd.cut(b.g, edges, labels=False)
        w = (ca.value_counts(normalize=True) / cb.value_counts(normalize=True)).reindex(cb).values
        cf = wq(b[R].values, w, .95) - wq(a[R].values, np.ones(len(a)), .95)
        # also reweight on size bins
        sb = [100e6, 500e6, 2e9, 10e9, 1e13]
        sa = pd.cut(a.rev_lag, sb, labels=False); sbb = pd.cut(b.rev_lag, sb, labels=False)
        ws = (sa.value_counts(normalize=True) / sbb.value_counts(normalize=True)).reindex(sbb).values
        cs = wq(b[R].values, ws, .95) - wq(a[R].values, np.ones(len(a)), .95)
        print(f'{vn} {R}: change in P95 {100*base:+.1f}; real $100M (2016-19 $) threshold in 2023-25 {100*real:+.1f} (n {len(b)}->{len(b2)}); '
              f'2023-25 reweighted to 2016-19 growth distribution {100*cf:+.1f}; reweighted to 2016-19 size distribution {100*cs:+.1f}')
