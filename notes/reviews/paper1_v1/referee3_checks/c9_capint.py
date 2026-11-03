import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd, lib
V = lib.V
rng = np.random.default_rng(7)
q95 = lambda s: float(np.quantile(s.dropna(), .95))
for vn in ['E1', 'E2']:
    v = V[vn].copy()
    v['R_cash_pre'] = v.R_cash + v.capex_int            # cash score before deducting capex: OCF - SBC basis
    d = v[v.period == '2023-25']
    print(vn, '2023-25: capex_int missing', int(d.capex_int.isna().sum()), 'of', len(d), '; of those coded hi_k=0:', int((d.capex_int.isna() & (d.hi_k == 0)).sum()),
          '; with R_op available:', int((d.capex_int.isna() & d.R_op.notna()).sum()))
    med = d.capex_int.median()
    hi, lo = d[d.hi_k == 1], d[d.hi_k == 0]
    print('   median capex_int %.3f; mean capex_int hi %.3f lo %.3f; median hi %.3f lo %.3f' % (med, hi.capex_int.mean(), lo.capex_int.mean(), hi.capex_int.median(), lo.capex_int.median()))
    for R in ['R_op', 'R_cash', 'R_cash_pre']:
        dd = d[['cik', 'hi_k', R, 'capex_int']].dropna()
        st = lambda z: q95(z.loc[z.hi_k == 1, R]) - q95(z.loc[z.hi_k == 0, R])
        bs = lib.boot(dd, st, 400, rng)
        print('   %-11s gap %+.1f [%+.1f, %+.1f]  (hi %.1f, lo %.1f)' % (R, 100 * st(dd), 100 * np.quantile(bs, .05), 100 * np.quantile(bs, .95), 100*q95(dd.loc[dd.hi_k==1,R]), 100*q95(dd.loc[dd.hi_k==0,R])))
    # top-tail composition: capex_int among firm-years at or above P95 of R_cash in each half
    dd = d[['hi_k', 'R_cash', 'capex_int', 'g']].dropna()
    for h in [0, 1]:
        z = dd[dd.hi_k == h]; t = z[z.R_cash >= z.R_cash.quantile(.95)]
        print('   half', h, 'top-5%% firm-years n=%d, mean capex_int %.3f, mean g %.3f' % (len(t), t.capex_int.mean(), t.g.mean()))
    # all periods, cash and pre-capex
    for p in ['2010-15', '2016-19', '2020-22', '2023-25']:
        z = v[v.period == p]
        r = []
        for R in ['R_op', 'R_cash', 'R_cash_pre']:
            zz = z[['hi_k', R, 'capex_int']].dropna()
            r.append(100 * (q95(zz.loc[zz.hi_k == 1, R]) - q95(zz.loc[zz.hi_k == 0, R])))
        print('   %s gaps: op %+.1f cash %+.1f cash-before-capex %+.1f' % (p, *r))
# proportional-to-growth prediction: does the cash gap rise with growth?  tau=0.9 QR of m_fcf_sbc on g, hi_k, g:hi_k (E2, 2010-25, g in [0,0.6])
import statsmodels.formula.api as smf
for vn in ['E1', 'E2']:
    for m in ['m_fcf_sbc', 'm_op']:
        d = V[vn][['cik', 'g', 'hi_k', m, 'capex_int']].dropna(); d = d[(d.g >= 0) & (d.g <= 0.6)]
        f = smf.quantreg(f'{m} ~ g * hi_k', d).fit(q=0.9, max_iter=5000)
        bs = lib.boot(d, lambda z: smf.quantreg(f'{m} ~ g * hi_k', z).fit(q=0.9, max_iter=2000).params['g:hi_k'], 200, rng)
        print(vn, m, 'tau=.9: hi_k %.3f, g:hi_k %.3f (cluster-boot se %.3f)' % (f.params['hi_k'], f.params['g:hi_k'], np.std(bs)))
