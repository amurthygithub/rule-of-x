"""Check 5: (a) which firm-years pin the frontier score; (b) identification of alpha when spend is chosen optimally;
(c) firm-cluster bootstrap CIs for SFA sigma_u by period and 2023-25 minus 2010-15; (d) acquisition flag on mega-mergers."""
import json, sys
import numpy as np, pandas as pd
from scipy import stats, optimize
sys.path.insert(0, '/home/claude/paper/notes/referee3')
from r3lib import *

df = load(); out = {}
# (a) pivotal observations
piv = []
for m in ['m_op', 'm_fcf_sbc']:
    for p in PERIODS:
        d = df[df.period == p][['name', 'year', 'g', m]].dropna()
        s, ga, edge = frontier_score(d.g.values, d[m].values)
        sub = d[d.g >= ga].sort_values(m, ascending=False)
        n = len(sub); pos = 0.95 * (n - 1); lo = int(np.floor(pos)); w = pos - lo
        asc = sub.sort_values(m)
        a, b = asc.iloc[lo], asc.iloc[min(lo + 1, n - 1)]
        piv.append(dict(m=m, p=p, score=round(100 * s, 1), g_edge=ga, n_upper=n,
                        pivot=f"{(1-w):.2f}*{a['name'][:22]} {int(a.year)} ({a[m]:.3f}) + {w:.2f}*{b['name'][:22]} {int(b.year)} ({b[m]:.3f})"))
pt = pd.DataFrame(piv); print(pt.to_string()); out['pivots'] = piv

# (b) alpha identification under optimizing firms (X=1, k=0), with and without the paper's selection
rng = np.random.default_rng(41); res = []
for true_alpha in [0.25, 0.45]:
    for sel in ['none', 'g>median, log(g-median)']:
        for me in [0.0, 0.5]:
            bb = []
            for _ in range(200):
                n = 3000; G = 0.05
                ell = np.exp(rng.normal(np.log(0.3), 0.6, n))
                sig = (true_alpha * ell) ** (1 / (1 - true_alpha))
                D = ell * sig ** true_alpha * np.exp(rng.normal(0, 0.3, n))
                g = G + D; so = sig * np.exp(rng.normal(0, me, n))
                if sel == 'none':
                    y, x = np.log(g - G), np.log(so)
                else:
                    med = np.median(g); k = g > med; y, x = np.log(g[k] - med), np.log(so[k])
                bb.append(np.polyfit(x, y, 1)[0])
            res.append(dict(true_alpha=true_alpha, selection=sel, meas_err_sd=me, mean_slope=round(float(np.mean(bb)), 3)))
print(pd.DataFrame(res).to_string()); out['alpha_ident_sim'] = res

# (c) SFA bootstrap
def sfa_su(y, X):
    n, k = X.shape; b0 = np.linalg.lstsq(X, y, rcond=None)[0]
    def nll(th):
        b = th[:k]; su, sv = np.exp(th[k]), np.exp(th[k + 1]); e = y - X @ b; s = np.sqrt(su ** 2 + sv ** 2); lam = su / sv
        return -(np.log(2) - np.log(s) + stats.norm.logpdf(e / s) + stats.norm.logcdf(-e * lam / s)).sum()
    r = optimize.minimize(nll, np.r_[b0, np.log(0.2), np.log(0.1)], method='BFGS')
    return float(np.exp(r.x[k]) * np.sqrt(2 / np.pi))
sf = {}
for m in ['m_op', 'm_fcf_sbc']:
    d = df[['cik', 'g', m, 'period']].dropna(); d = d[(d.g <= 1.5) & (d[m] > -1.5)].reset_index(drop=True)
    def st(x):
        v = {}
        for p in ['2010-15', '2023-25']:
            z = x[x.period == p]; X = np.c_[np.ones(len(z)), z.g, z.g ** 2]; v[p] = sfa_su(z[m].values, X)
        return np.array([v['2010-15'], v['2023-25'], v['2023-25'] - v['2010-15']])
    ptv = st(d); rng = np.random.default_rng(55); idx = cluster_index(d.cik.values)
    bs = np.array([st(d.iloc[cluster_draw(idx, rng)]) for _ in range(150)])
    sf[m] = dict(mean_ineff_2010_15=round(100 * ptv[0], 1), ci=[round(100 * x, 1) for x in np.quantile(bs[:, 0], [.05, .95])],
                 mean_ineff_2023_25=round(100 * ptv[1], 1), ci2=[round(100 * x, 1) for x in np.quantile(bs[:, 1], [.05, .95])],
                 diff=round(100 * ptv[2], 1), diff_ci90=[round(100 * x, 1) for x in np.quantile(bs[:, 2], [.05, .95])])
    print(m, sf[m])
out['sfa_boot'] = sf
# composition: share of firm-years from firms that IPO'd / entered sample after 2019 among m<-20%
first = df.groupby('cik').year.min(); df['entry'] = df.cik.map(first)
for p in ['2020-22', '2023-25']:
    d = df[df.period == p]
    print(p, 'share of firm-years with m_op<-0.2 from firms entering sample >=2019:',
          round(float((d[d.m_op < -0.2].entry >= 2019).mean()), 2), ' share overall:', round(float((d.entry >= 2019).mean()), 2))
# (d) acquisition flag on large-growth firm-years
big = df[df.g >= 1.0][['name', 'year', 'g', 'acq_flag', 'acq_pay', 'gw_jump', 'rev_lag']].sort_values('g', ascending=False)
print(big.head(15).to_string())
out['g_ge_100pct_acqflag_share'] = float(big.acq_flag.mean())
json.dump(out, open('/home/claude/paper/notes/referee3/check5_results.json', 'w'), indent=1, default=float)
