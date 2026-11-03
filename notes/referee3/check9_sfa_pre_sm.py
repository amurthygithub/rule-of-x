"""Check 9: SFA on margin before S&M (m + S&M share): does 'rising inefficiency' survive once deliberate growth spend is added back?
Also: SFA restricted to firms in the sample before 2019 (excludes 2019+ IPO cohorts)."""
import numpy as np, pandas as pd
from scipy import stats, optimize
df = pd.read_csv('/home/claude/paper/data/panel.csv')
first = df.groupby('cik').year.min(); df['entry'] = df.cik.map(first)
def sfa(y, X):
    n, k = X.shape; b0 = np.linalg.lstsq(X, y, rcond=None)[0]
    def nll(th):
        b = th[:k]; su, sv = np.exp(th[k]), np.exp(th[k + 1]); e = y - X @ b; s = np.sqrt(su ** 2 + sv ** 2); lam = su / sv
        return -(np.log(2) - np.log(s) + stats.norm.logpdf(e / s) + stats.norm.logcdf(-e * lam / s)).sum()
    r = optimize.minimize(nll, np.r_[b0, np.log(0.2), np.log(0.1)], method='BFGS')
    return np.exp(r.x[k]) * np.sqrt(2 / np.pi)
rows = []
for p in ['2010-15', '2016-19', '2020-22', '2023-25']:
    d = df[df.period == p][['g', 'm_op', 'm_fcf_sbc', 'sm_share', 'entry']].dropna(); d = d[(d.g <= 1.5) & (d.m_op > -1.5) & (d.m_fcf_sbc > -1.5)]
    X = np.c_[np.ones(len(d)), d.g, d.g ** 2]
    e = d[d.entry < 2019]; Xe = np.c_[np.ones(len(e)), e.g, e.g ** 2]
    rows.append(dict(period=p, n=len(d), op=round(100 * sfa(d.m_op.values, X), 1), op_pre_sm=round(100 * sfa((d.m_op + d.sm_share).values, X), 1),
                     fcfsbc=round(100 * sfa(d.m_fcf_sbc.values, X), 1), fcfsbc_pre_sm=round(100 * sfa((d.m_fcf_sbc + d.sm_share).values, X), 1),
                     n_pre2019_entrants=len(e), op_pre2019_entrants=round(100 * sfa(e.m_op.values, Xe), 1), fcfsbc_pre2019_entrants=round(100 * sfa(e.m_fcf_sbc.values, Xe), 1)))
print('Mean inefficiency E[u] (margin points), S&M-reporting subsample'); print(pd.DataFrame(rows).to_string())
