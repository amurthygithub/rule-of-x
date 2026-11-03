import sys; sys.path.insert(0, '.')
import warnings, numpy as np, lib
import statsmodels.formula.api as smf
V = lib.V
def obj(y, x, b, tau):
    u = y - b[0] - b[1] * x
    return np.sum(u * (tau - (u < 0)))
for vn in ['E1', 'E2', 'E2x25']:
    for m in ['m_op', 'm_fcf_sbc']:
        for per, nm in [(['2010-15','2016-19','2020-22','2023-25'],'pooled'), (['2010-15','2016-19'],'2010-19'), (['2020-22','2023-25'],'2020-25')]:
            d = V[vn][['cik', 'period', 'g', m]].dropna(); d = d[(d.g >= 0) & (d.g <= 0.6) & d.period.isin(per)]
            res = []
            for it in [2000, 5000, 50000]:
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter('always')
                    f = smf.quantreg(f'{m} ~ g', d).fit(q=0.9, max_iter=it)
                    conv = not any('Iteration' in str(x.category.__name__) or 'iteration' in str(x.message) for x in w)
                res.append((it, round(f.params['g'], 4), conv))
            blp = lib.qr_lp(d[m].values, d.g.values, 0.9)
            print(vn, m, nm, res, 'LP', round(blp[1], 4), 'obj IRLS5000-LP', round(obj(d[m].values, d.g.values, [f.params.iloc[0], f.params.iloc[1]], .9) - obj(d[m].values, d.g.values, blp, .9), 6))
