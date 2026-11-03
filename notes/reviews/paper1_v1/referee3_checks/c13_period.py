import sys, json; sys.path.insert(0, '.')
import numpy as np, lib, statsmodels.formula.api as smf
V = lib.V
rng = np.random.default_rng(13)
J = json.load(open('/home/claude/paper/notes/empirics_organic.json'))['estimates']
for k in ['slope_op_2020_25', 'slope_cash_2020_25', 'slope_op_pooled', 'slope_cash_pooled']:
    print(k, 'E2 est %.3f se %.3f ci90 %s' % (J[k]['E2']['est'], J[k]['E2']['se'], np.round(J[k]['E2']['ci90'], 3).tolist()))
def sl(z, m):
    return float(smf.quantreg(f'{m} ~ g', z).fit(q=0.9, max_iter=2000).params['g'])
for vn in ['E1', 'E2']:
    for m in ['m_op', 'm_fcf_sbc']:
        d = V[vn][['cik', 'period', 'g', m]].dropna(); d = d[(d.g >= 0) & (d.g <= 0.6)]
        early, late = ['2010-15', '2016-19'], ['2020-22', '2023-25']
        st = lambda z: sl(z[z.period.isin(late)], m) - sl(z[z.period.isin(early)], m)
        bs = lib.boot(d, st, 400, rng)
        e = st(d)
        print(f'{vn} {m}: slope 2020-25 minus 2010-19 = {e:+.3f}; cluster-boot se {bs.std():.3f}; 90% pct CI [{np.quantile(bs,.05):+.3f}, {np.quantile(bs,.95):+.3f}]', flush=True)
