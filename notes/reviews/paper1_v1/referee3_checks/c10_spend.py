import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd, lib
V = lib.V
E1 = V['E1']
# alternative benchmarks for market growth G
Gmed = E1.groupby('year').g.median()
Gmean = E1.groupby('year').g.mean()
Gvw = E1.groupby('year').apply(lambda z: z.rev.sum() / z.rev_lag.sum() - 1)   # revenue-weighted (aggregate) growth of the core sample
print('benchmarks (2016, 2020, 2024): median', Gmed.loc[[2016, 2020, 2024]].round(3).tolist(), 'mean', Gmean.loc[[2016, 2020, 2024]].round(3).tolist(), 'aggregate', Gvw.loc[[2016, 2020, 2024]].round(3).tolist())
for vn in ['E2', 'E1']:
    v = V[vn].copy()
    for nm, G in [('median (paper)', v.year.map(Gmed)), ('aggregate revenue growth', v.year.map(Gvw)), ('median + 5pp', v.year.map(Gmed) + 0.05), ('median - 5pp', v.year.map(Gmed) - 0.05)]:
        for thr in [0.0, 0.05]:
            x = v[(v.g > G + thr) & v.sm_lag_share.between(0.01, 1.5)]
            r = x.sm_lag_share / (x.g - G[x.index])
            print('%-3s G=%-25s sel g>G+%.2f: n=%4d median ratio %.2f -> weight %.1f to %.1f' % (vn, nm, thr, len(x), r.median(), r.median() / .45, r.median() / .25))
    # median of S&M share / median excess growth (ratio of medians) vs median of ratios
    x = v[(v.g > v.year.map(Gmed)) & v.sm_lag_share.between(0.01, 1.5)]
    print(vn, 'ratio of medians %.2f; share of ratios > 10: %.2f' % (x.sm_lag_share.median() / (x.g - x.year.map(Gmed)).median(), ((x.sm_lag_share / (x.g - x.year.map(Gmed))) > 10).mean()))
    # S&M share of slow growers (below median): maintenance spend proxy
    y = v[(v.g <= v.year.map(Gmed)) & v.sm_lag_share.between(0.01, 1.5)]
    print(vn, 'median S&M share among firm-years at or below the median growth: %.3f (above: %.3f)' % (y.sm_lag_share.median(), x.sm_lag_share.median()))
    xx = x.copy(); xx['net'] = xx.sm_lag_share - y.sm_lag_share.median()
    print(vn, 'median of (S&M share - slow-grower median S&M) / excess growth: %.2f' % ((xx.net / (xx.g - xx.year.map(Gmed))).median()))
