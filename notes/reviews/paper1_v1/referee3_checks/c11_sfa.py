import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd, lib
from scipy import optimize, stats
df = pd.read_csv('/home/claude/paper/data/panel.csv')
first_year = df.groupby('cik')['year'].min()
df['coh'] = np.where(df.cik.map(first_year) >= 2019, '2019+', 'pre-2019')
def sfa_fit(y, X):
    k = X.shape[1]; b0 = np.linalg.lstsq(X, y, rcond=None)[0]
    def nll(th):
        b = th[:k]; su, sv = np.exp(th[k]), np.exp(th[k + 1])
        e = y - X @ b; s = np.sqrt(su ** 2 + sv ** 2); lam = su / sv
        return -(np.log(2) - np.log(s) + stats.norm.logpdf(e / s) + stats.norm.logcdf(-e * lam / s)).sum()
    r = optimize.minimize(nll, np.r_[b0, np.log(0.2), np.log(0.1)], method='BFGS')
    b = r.x[:k]; su, sv = np.exp(r.x[k]), np.exp(r.x[k + 1])
    e = y - X @ b; s2 = su**2 + sv**2; mus = -e * su**2 / s2; ss = su * sv / np.sqrt(s2)
    jlms = mus + ss * stats.norm.pdf(mus / ss) / stats.norm.cdf(mus / ss)      # E[u | e]
    return su * np.sqrt(2 / np.pi), jlms, e
rng = np.random.default_rng(11)
for m in ['m_op', 'm_fcf_sbc']:
    for p in ['2016-19', '2023-25']:
        d = df[df.period == p][['cik', 'g', m, 'coh']].dropna(); d = d[(d.g <= 1.5) & (d[m] > -1.5)].reset_index(drop=True)
        X = np.c_[np.ones(len(d)), d.g, d.g ** 2]
        mu, j, e = sfa_fit(d[m].values, X)
        ols = d[m].values - X @ np.linalg.lstsq(X, d[m].values, rcond=None)[0]
        sk = stats.skew(ols)
        by = pd.Series(j).groupby(d.coh).mean()
        line = f'{m} {p}: OLS-residual skew {sk:+.2f}; common frontier mean shortfall {100*mu:.1f}; JLMS mean by cohort ' + ', '.join(f'{k} {100*v:.1f}' for k, v in by.items())
        if p == '2023-25':
            def st(z):
                Xz = np.c_[np.ones(len(z)), z.g, z.g ** 2]; _, jj, _ = sfa_fit(z[m].values, Xz)
                s = pd.Series(jj, index=z.index).groupby(z.coh).mean(); return s.get('2019+', np.nan) - s.get('pre-2019', np.nan)
            bs = lib.boot(d, st, 150, rng)
            line += f'; gap 2019+ minus pre-2019 {100*st(d):.1f} [90% {100*np.nanquantile(bs,.05):.1f}, {100*np.nanquantile(bs,.95):.1f}]'
            # separate-frontier version (the paper's)
            sep = {c: 100 * sfa_fit(z[m].values, np.c_[np.ones(len(z)), z.g, z.g**2])[0] for c, z in d.groupby('coh')}
            line += f'; separate frontiers (paper) {sep}'
            def st_mu(z): return sfa_fit(z[m].values, np.c_[np.ones(len(z)), z.g, z.g ** 2])[0]
            bsm = lib.boot(d, st_mu, 150, rng)
            line += f'; period mean shortfall 90% CI [{100*np.nanquantile(bsm,.05):.1f}, {100*np.nanquantile(bsm,.95):.1f}]'
        print(line, flush=True)
# survivorship: pre-2019 entrants observed in 2023-25 versus all pre-2019 entrants in 2016-19
x = df[df.coh == 'pre-2019']
s16 = set(x[x.period == '2016-19'].cik); s23 = set(x[x.period == '2023-25'].cik)
print('pre-2019 firms in 2016-19:', len(s16), '; still in sample in 2023-25:', len(s16 & s23))
for m in ['m_op', 'm_fcf_sbc']:
    a = x[(x.period == '2016-19') & x.cik.isin(s16 & s23)][m].median(); b = x[(x.period == '2016-19') & ~x.cik.isin(s23)][m].median()
    print(m, '2016-19 median margin: survivors to 2023-25 %.3f, non-survivors %.3f' % (a, b))
