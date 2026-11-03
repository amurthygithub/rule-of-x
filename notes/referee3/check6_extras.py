"""Check 6: extra numbers for the report.
(a) S&M share of firm-years that define the frontier intercept phi_0.95(0) (calibration m0 mapping);
(b) implied distribution of lambda*h from the elasticity-regression residuals (basis for 'exceptional' pull);
(c) P95 of R by capital-intensity half in 2023-25; (d) acquisition flag coverage among fast growers;
(e) implied X from the FOC at the calibrated technology and observed spend."""
import sys
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
sys.path.insert(0, '/home/claude/paper/notes/referee3')
from r3lib import *

df = load()
# (a)
for p in ['2023-25', 'all']:
    d = df if p == 'all' else df[df.period == p]
    d = d[(d.g >= 0)][['m_fcf_sbc', 'm_op', 'sm_share']].dropna()
    for m in ['m_op', 'm_fcf_sbc']:
        q = d[m].quantile(.95); top = d[d[m] >= d[m].quantile(.90)]
        print(f'(a) {p} {m}: phi95(0)={q:.3f}; median S&M share of top-decile-margin firm-years (g>=0) = {top.sm_share.median():.3f} (n={len(top)})')
# (b)
df['G_t'] = df.groupby('year')['g'].transform('median')
d = df[['cik', 'year', 'g', 'G_t', 'sm_lag_share', 'acq_flag']].dropna()
d = d[(d.g > d.G_t) & (d.sm_lag_share > 0.01) & (d.sm_lag_share < 1.5) & (d.acq_flag == 0)].copy()
d['ly'] = np.log(d.g - d.G_t); d['lx'] = np.log(d.sm_lag_share)
f = smf.ols('ly ~ lx', d).fit(); a_ = f.params['lx']
u = d.ly - a_ * d.lx
qs = np.quantile(np.exp(u), [.5, .75, .9, .95, .99])
print(f'(b) alpha(no FE)={a_:.3f}; implied lambda*h quantiles p50,p75,p90,p95,p99 =', np.round(qs, 3))
u25 = d.ly - 0.25 * d.lx
print('    at alpha=0.25:', np.round(np.quantile(np.exp(u25), [.5, .75, .9, .95, .99]), 3), ' mean=', round(float(np.exp(u25).mean()), 3))
# (c)
df['hi_k'] = df.groupby('period', observed=True)['capex_int'].transform(lambda x: (x > x.median()).astype(float))
for m in ['m_fcf_sbc', 'm_op']:
    x = df[df.period == '2023-25'][['g', m, 'hi_k']].dropna(); x['R'] = x.g + x[m]
    print(f'(c) 2023-25 {m}: P95 R lo-k={x[x.hi_k==0].R.quantile(.95):.3f}, hi-k={x[x.hi_k==1].R.quantile(.95):.3f}; '
          f'P90 lo={x[x.hi_k==0].R.quantile(.9):.3f} hi={x[x.hi_k==1].R.quantile(.9):.3f}; edge lo={frontier_score(x[x.hi_k==0].g.values, x[x.hi_k==0][m].values)[2]}, '
          f'hi={frontier_score(x[x.hi_k==1].g.values, x[x.hi_k==1][m].values)[2]}')
print('    capex reported missing (set to zero) share by hi_k in 2023-25:', df[df.period == '2023-25'].groupby('hi_k').capex_missing.mean().round(3).to_dict())
# (d)
fast = df[df.g >= 0.5]
print(f'(d) g>=50%: n={len(fast)}, acq_pay and gw_jump both missing: {(fast.acq_pay.isna() & fast.gw_jump.isna()).mean():.3f}; flagged={fast.acq_flag.mean():.3f}')
# (e)
for a_, lh in [(0.25, 0.25), (0.25, 0.15), (0.20, 0.24), (0.43, 0.33)]:
    sig = 0.34
    mg = a_ * lh * sig ** (a_ - 1)
    print(f'(e) alpha={a_}, lh={lh}: marginal growth per point of spend at sigma=0.34: {mg:.3f}; implied X=1/mg={1/mg:.1f}; '
          f'optimal sigma at X=1: {(a_*lh)**(1/(1-a_)):.4f}')
