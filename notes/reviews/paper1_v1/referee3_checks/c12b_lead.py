"""Within-firm slope with the model's timing: margin at t on growth at t+1 (firm and year fixed effects, firm-clustered SE)."""
import sys; sys.path.insert(0, '.')
import lib, statsmodels.formula.api as smf
P = lib.P[['cik', 'year', 'g']].copy().sort_values(['cik', 'year'])
P['g_lead'] = P.groupby('cik').g.shift(-1); P['y_lead'] = P.groupby('cik').year.shift(-1); P = P[P.y_lead == P.year + 1]
for vn in ['E1', 'E2']:
    v = lib.V[vn].merge(P[['cik', 'year', 'g_lead']], on=['cik', 'year'], how='left')
    for m in ['m_op', 'm_fcf_sbc']:
        d = v[['cik', 'year', 'g', 'g_lead', m]].dropna(); d = d[(d.g <= 1.5) & (d.g_lead <= 1.5) & (d.g_lead > -0.9)]
        a = smf.ols(f'{m} ~ g_lead + C(year) + C(cik)', d).fit(cov_type='cluster', cov_kwds={'groups': d['cik']})
        b = smf.ols(f'{m} ~ g + g_lead + C(year) + C(cik)', d).fit(cov_type='cluster', cov_kwds={'groups': d['cik']})
        print(f"{vn} {m} n={len(d)}: g_t+1 {a.params['g_lead']:+.3f} ({a.bse['g_lead']:.3f}); joint g_t {b.params['g']:+.3f} ({b.bse['g']:.3f}), g_t+1 {b.params['g_lead']:+.3f} ({b.bse['g_lead']:.3f})")
