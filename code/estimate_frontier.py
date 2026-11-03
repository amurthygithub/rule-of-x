"""Estimate the empirical growth-margin frontier for public software firms (SEC XBRL, 2010-2025).

Methods
  1. Descriptives and Rule-of-40 pass rates by period and margin definition.
  2. Robust Pareto (output-output) partial frontiers: order-alpha and order-m frontiers of margin
     conditional on growth >= g (Cazals, Florens & Simar 2002; Aragon, Daouia & Thomas-Agnan 2005),
     with firm-cluster bootstrap confidence intervals. Frontier score = max_g [g + phi(g)].
  3. Upper-quantile regressions (tau = 0.90) of margin on growth with period interactions.
  4. Structural fit of the model frontier m = m0 - kappa * max(g - G, 0)^beta by check-loss minimization,
     and implied tangency (score-maximizing) points for X = 1 and X = 2.5.
  5. Scale (saturation) and capital-intensity tests.
  6. Stochastic frontier (normal / half-normal) by period.
Outputs: sections/tables/*.tex, figures/*.pdf, notes/empirics_results.json, notes/empirics_log.txt
"""
import os
import json, os, warnings
import numpy as np
import pandas as pd
from scipy import optimize, stats
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # replication-package root
os.makedirs(f'{BASE}/sections/tables', exist_ok=True)
rng = np.random.default_rng(20261028)
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
                     'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})

df = pd.read_csv(f'{BASE}/data/panel.csv')
PERIODS = ['2010-15', '2016-19', '2020-22', '2023-25']
MEAS = {'m_op': 'GAAP operating', 'm_adj': 'Adjusted operating (SBC added back)',
        'm_fcf': 'Free cash flow', 'm_fcf_sbc': 'FCF after SBC'}
res = {}
log = []

# ---------------------------------------------------------------- 1. descriptives
def desc(d, m):
    R = d['g'] + d[m]
    R = R.dropna()
    return dict(N=int(len(R)), firms=int(d.loc[R.index, 'cik'].nunique()), med_g=float(d.loc[R.index, 'g'].median()),
                med_m=float(d.loc[R.index, m].median()), med_R=float(R.median()), p90_R=float(R.quantile(.9)),
                p99_R=float(R.quantile(.99)), pass40=float((R >= .40).mean()), pass60=float((R >= .60).mean()),
                pass100=float((R >= 1.0).mean()))
res['desc'] = {m: {p: desc(df[df.period == p], m) for p in PERIODS + ['all']} for m in MEAS}
for m in MEAS:
    res['desc'][m]['all'] = desc(df, m)

rows = []
for p in PERIODS + ['all']:
    d1 = res['desc']['m_op'][p if p != 'all' else 'all']; d2 = res['desc']['m_fcf_sbc'][p]
    rows.append(f"{(p if p!='all' else '2010-25').replace('-', '--')} & {d1['N']:,} & {d1['firms']:,} & {100*d1['med_g']:.1f} & "
                f"{100*d1['med_m']:.1f} & {100*d1['med_R']:.1f} & {100*d1['p90_R']:.1f} & {100*d1['pass40']:.1f} & "
                f"{100*d2['med_R']:.1f} & {100*d2['p90_R']:.1f} & {100*d2['pass40']:.1f} \\\\")
tab1 = r"""\begin{table}[t]\centering\small
\caption{Growth, margin and Rule-of-40 scores, public software firms (SIC 7372), fiscal years 2010--2025}\label{tab:desc}
\begin{tabular}{lrrrrrrrrrr}\toprule
 & & & \multicolumn{5}{c}{GAAP operating margin basis} & \multicolumn{3}{c}{FCF after SBC basis}\\
\cmidrule(lr){4-8}\cmidrule(lr){9-11}
Period & Obs. & Firms & Med.\ $g$ & Med.\ $m$ & Med.\ $R$ & P90 $R$ & \% $R\geq40$ & Med.\ $R$ & P90 $R$ & \% $R\geq40$\\\midrule
""" + '\n'.join(rows) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: Firm-years with prior-year revenue of at least \$100 million and a reported GAAP operating margin; statistics on the FCF-after-SBC basis use the firm-years for which that margin is available. $g$ is year-over-year revenue growth; $m$ is the margin; $R=g+m$ in percentage points. FCF after SBC is operating cash flow minus capital expenditure and capitalized software, minus stock-based compensation, divided by revenue.
\end{table}"""
open(f'{BASE}/sections/tables/tab_desc.tex', 'w').write(tab1)

# ---------------------------------------------------------------- 2. robust Pareto frontiers
GRID = np.round(np.arange(0.0, 1.01, 0.05), 2)
MIN_N = 30

def order_alpha(gv, mv, alpha):
    out = np.full(len(GRID), np.nan)
    for k, g0 in enumerate(GRID):
        s = mv[gv >= g0]
        if len(s) >= MIN_N:
            out[k] = np.quantile(s, alpha)
    return out

def order_m(gv, mv, M):
    out = np.full(len(GRID), np.nan)
    for k, g0 in enumerate(GRID):
        s = np.sort(mv[gv >= g0]); n = len(s)
        if n >= MIN_N:
            j = np.arange(1, n + 1)
            w = (j / n) ** M - ((j - 1) / n) ** M
            out[k] = float((w * s).sum())
    return out

def frontier_score(phi):
    v = GRID + phi
    if np.all(np.isnan(v)):
        return np.nan, np.nan
    k = int(np.nanargmax(v))
    return float(v[k]), float(GRID[k])

def cluster_boot(d, fn, B=300):
    firms = d['cik'].unique()
    idx = {c: np.where(d['cik'].values == c)[0] for c in firms}
    vals = []
    for _ in range(B):
        draw = rng.choice(firms, size=len(firms), replace=True)
        ii = np.concatenate([idx[c] for c in draw])
        vals.append(fn(d.iloc[ii]))
    return np.array(vals)

res['frontier'] = {}
for m in MEAS:
    res['frontier'][m] = {}
    for p in PERIODS:
        d = df[(df.period == p) & df[m].notna()][['cik', 'g', m]].dropna()
        gv, mv = d['g'].values, d[m].values
        fa = order_alpha(gv, mv, 0.95); fm = order_m(gv, mv, 25); fdh = order_alpha(gv, mv, 1.0)
        sa, ga = frontier_score(fa); sm_, gm_ = frontier_score(fm)
        boot = cluster_boot(d, lambda x: frontier_score(order_alpha(x['g'].values, x[m].values, 0.95))[0], B=300)
        res['frontier'][m][p] = dict(n=int(len(d)), order_alpha=[None if np.isnan(x) else float(x) for x in fa],
                                     order_m=[None if np.isnan(x) else float(x) for x in fm],
                                     fdh=[None if np.isnan(x) else float(x) for x in fdh],
                                     score_alpha=sa, g_at_max_alpha=ga, score_m=sm_, g_at_max_m=gm_,
                                     score_alpha_ci=[float(np.nanquantile(boot, .05)), float(np.nanquantile(boot, .95))],
                                     intercept_alpha=float(fa[0]) if not np.isnan(fa[0]) else None)
res['grid'] = GRID.tolist()

# frontier-shift test: difference in order-alpha frontier score, 2023-25 minus 2016-19, cluster bootstrap
def shift_test(m, p_new='2023-25', p_old='2016-19', B=400):
    d = df[df.period.isin([p_new, p_old]) & df[m].notna()][['cik', 'g', m, 'period']].dropna()
    def stat(x):
        a = x[x.period == p_new]; b = x[x.period == p_old]
        return (frontier_score(order_alpha(a['g'].values, a[m].values, .95))[0]
                - frontier_score(order_alpha(b['g'].values, b[m].values, .95))[0])
    obs = stat(d)
    bs = cluster_boot(d, stat, B=B)
    return dict(diff=float(obs), ci90=[float(np.nanquantile(bs, .05)), float(np.nanquantile(bs, .95))],
                p_two_sided=float(2 * min(np.nanmean(bs <= 0), np.nanmean(bs >= 0))))
res['shift'] = {m: shift_test(m) for m in MEAS}

rows = []
for m, lab in MEAS.items():
    cells = []
    for p in PERIODS:
        f = res['frontier'][m][p]
        cells.append(f"{100*f['score_alpha']:.0f} [{100*f['score_alpha_ci'][0]:.0f}, {100*f['score_alpha_ci'][1]:.0f}]")
    s = res['shift'][m]
    rows.append(f"{lab} & " + ' & '.join(cells) + f" & {100*s['diff']:+.0f} [{100*s['ci90'][0]:+.0f}, {100*s['ci90'][1]:+.0f}] \\\\")
tab2 = r"""\begin{table}[t]\centering\small
\caption{Frontier Rule-of-40 score by period: maximum of $g+\phi_{0.95}(g)$ on the order-$\alpha$ Pareto frontier}\label{tab:frontier}
\resizebox{\textwidth}{!}{\begin{tabular}{lccccc}\toprule
Margin definition & 2010--15 & 2016--19 & 2020--22 & 2023--25 & $\Delta$ 2023--25 vs 2016--19\\\midrule
""" + '\n'.join(rows) + r"""
\bottomrule\end{tabular}}
\par\vspace{2pt}\footnotesize\raggedright Notes: $\phi_{0.95}(g)$ is the 95th percentile of margin among firm-years with growth of at least $g$ (order-$\alpha$ frontier, $\alpha=0.95$), evaluated on a grid $g\in\{0,0.05,\dots,1\}$ with at least 30 observations per point. Entries are $\max_g[g+\phi_{0.95}(g)]$ in percentage points with 90\% firm-cluster bootstrap intervals (300 replications; 400 for the difference).
\end{table}"""
open(f'{BASE}/sections/tables/tab_frontier.tex', 'w').write(tab2)

# ---------------------------------------------------------------- 3. upper-quantile regressions
df['post'] = (df.year >= 2023).astype(int)
df['g2'] = df['g'] ** 2
df['lsize'] = np.log(df['rev_lag'] / 1e9)
res['qreg'] = {}
qrows = []
for m, lab in MEAS.items():
    d = df[df.year >= 2016][['cik', 'g', 'g2', 'post', 'lsize', m]].dropna()
    d = d[(d.g <= 1.5)]
    form = f'{m} ~ g + g2 + post + post:g + lsize'
    fit = smf.quantreg(form, d).fit(q=0.90, max_iter=5000)
    firms = d.cik.unique(); idx = {c: np.where(d.cik.values == c)[0] for c in firms}
    bs = []
    for _ in range(200):
        draw = rng.choice(firms, size=len(firms), replace=True)
        ii = np.concatenate([idx[c] for c in draw])
        try:
            bs.append(smf.quantreg(form, d.iloc[ii]).fit(q=0.90, max_iter=2000).params.values)
        except Exception:
            pass
    bs = np.array(bs); se = bs.std(axis=0)
    out = {k: dict(b=float(v), se=float(s)) for k, v, s in zip(fit.params.index, fit.params.values, se)}
    out['n'] = int(len(d))
    res['qreg'][m] = out
    def cell(k):
        b, s = out[k]['b'], out[k]['se']; z = abs(b / s) if s > 0 else 0
        star = '***' if z > 2.576 else '**' if z > 1.96 else '*' if z > 1.645 else ''
        return f"{b:.3f}{star} ({s:.3f})"
    qrows.append(f"{lab} & {cell('g')} & {cell('g2')} & {cell('post')} & {cell('post:g')} & {cell('lsize')} & {out['n']:,} \\\\")
tab3 = r"""\begin{table}[t]\centering\small
\caption{Upper-quantile ($\tau=0.90$) regressions of margin on growth, fiscal years 2016--2025}\label{tab:qreg}
\resizebox{\textwidth}{!}{\begin{tabular}{lcccccr}\toprule
Margin definition & $g$ & $g^2$ & Post-2022 & Post-2022 $\times g$ & $\log$ size & Obs.\\\midrule
""" + '\n'.join(qrows) + r"""
\bottomrule\end{tabular}}
\par\vspace{2pt}\footnotesize\raggedright Notes: Linear quantile regressions at $\tau=0.90$ with an intercept (not shown). Post-2022 equals one for fiscal years 2023--2025. $\log$ size is the log of prior-year revenue in billions of dollars. Firm-cluster bootstrap standard errors in parentheses (200 replications). *, **, *** denote significance at 10\%, 5\%, 1\%. Observations with growth above 150\% are excluded.
\end{table}"""
open(f'{BASE}/sections/tables/tab_qreg.tex', 'w').write(tab3)

# ---------------------------------------------------------------- 4. envelope diagnostics, within-firm trade-off, growth-spend elasticity
# (a) envelope: growth support and average frontier slope over the support
res['envelope'] = {}
erows = []
for m, lab in [('m_op', 'GAAP operating'), ('m_fcf_sbc', 'FCF after SBC')]:
    res['envelope'][m] = {}
    for p in PERIODS:
        d = df[(df.period == p)][['g', m]].dropna()
        fa = np.array(res['frontier'][m][p]['order_alpha'], dtype=float)
        ok = ~np.isnan(fa)
        gsup = float(GRID[ok].max())
        slope = float(np.polyfit(GRID[ok], fa[ok], 1)[0])
        g95 = float(d['g'].quantile(.95))
        res['envelope'][m][p] = dict(g_support=gsup, g_p95=g95, slope=slope, phi0=float(fa[0]), phi_sup=float(fa[ok][-1]),
                                     n_g40=int((d['g'] >= .40).sum()))
        erows.append(f"{lab} & {p.replace('-', '--')} & {100*fa[0]:.0f} & {slope:+.2f} & {100*gsup:.0f} & {100*fa[ok][-1]:.0f} & {int((d['g']>=.40).sum())} \\\\")
tab4 = r"""\begin{table}[t]\centering\small
\caption{Shape of the empirical Pareto frontier: intercept, slope and growth support}\label{tab:envelope}
\begin{tabular}{llrrrrr}\toprule
Margin & Period & $\phi_{0.95}(0)$ & Avg.\ slope & Growth support & $\phi_{0.95}$ at support & Obs.\ with $g\geq 40\%$\\\midrule
""" + '\n'.join(erows) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: $\phi_{0.95}(0)$ is the frontier margin with no growth requirement (pp). Avg.\ slope is the least-squares slope of $\phi_{0.95}(g)$ on $g$ over the grid points with at least 30 observations; a slope of $-1$ would mean each point of growth costs one point of margin. Growth support is the largest grid value of $g$ with at least 30 firm-years growing at least that fast (pp).
\end{table}"""
open(f'{BASE}/sections/tables/tab_envelope.tex', 'w').write(tab4)

# (b) within-firm trade-off: margin on growth with firm and year fixed effects (OLS, clustered by firm)
res['within'] = {}
for m in ['m_op', 'm_fcf_sbc']:
    d = df[['cik', 'year', 'g', m]].dropna(); d = d[d.g <= 1.5]
    pooled = smf.ols(f'{m} ~ g + C(year)', d).fit(cov_type='cluster', cov_kwds={'groups': d['cik']})
    fe = smf.ols(f'{m} ~ g + C(year) + C(cik)', d).fit(cov_type='cluster', cov_kwds={'groups': d['cik']})
    res['within'][m] = dict(pooled_b=float(pooled.params['g']), pooled_se=float(pooled.bse['g']),
                            fe_b=float(fe.params['g']), fe_se=float(fe.bse['g']), n=int(len(d)), firms=int(d.cik.nunique()))

# (c) growth-spend elasticity alpha: log(g - G_t) on log(S&M share_{t-1}), firm FE, firm-years with g > G_t
df['G_t'] = df.groupby('year')['g'].transform('median')
d = df[['cik', 'year', 'g', 'G_t', 'sm_lag_share', 'acq_flag']].dropna()
d = d[(d.g > d.G_t) & (d.sm_lag_share > 0.01) & (d.sm_lag_share < 1.5) & (d.acq_flag == 0)]
d['ly'] = np.log(d.g - d.G_t); d['lx'] = np.log(d.sm_lag_share)
e_pool = smf.ols('ly ~ lx + C(year)', d).fit(cov_type='cluster', cov_kwds={'groups': d['cik']})
e_fe = smf.ols('ly ~ lx + C(year) + C(cik)', d).fit(cov_type='cluster', cov_kwds={'groups': d['cik']})
res['alpha_est'] = dict(pooled=float(e_pool.params['lx']), pooled_se=float(e_pool.bse['lx']),
                        fe=float(e_fe.params['lx']), fe_se=float(e_fe.bse['lx']), n=int(len(d)), firms=int(d.cik.nunique()))

# (d) organic-growth robustness: exclude acquisition-flagged firm-years
res['organic'] = {}
for m in ['m_op', 'm_fcf_sbc']:
    res['organic'][m] = {}
    for p in PERIODS:
        d = df[(df.period == p) & (df.acq_flag == 0)][['g', m]].dropna()
        fa = order_alpha(d['g'].values, d[m].values, .95)
        s, g_ = frontier_score(fa)
        R = d['g'] + d[m]
        res['organic'][m][p] = dict(n=int(len(d)), score=s, g_at_max=g_, med_R=float(R.median()), pass40=float((R >= .4).mean()))
orow = []
for p in PERIODS:
    a = res['organic']['m_op'][p]; b = res['organic']['m_fcf_sbc'][p]
    orow.append(f"{p.replace('-', '--')} & {a['n']:,} & {100*a['med_R']:.1f} & {100*a['pass40']:.1f} & {100*a['score']:.0f} & {100*b['med_R']:.1f} & {100*b['pass40']:.1f} & {100*b['score']:.0f} \\\\")
tab_org = r"""\begin{table}[t]\centering\small
\caption{Robustness: excluding acquisition-driven growth}\label{tab:organic}
\begin{tabular}{lrrrrrrr}\toprule
 & & \multicolumn{3}{c}{GAAP operating} & \multicolumn{3}{c}{FCF after SBC}\\\cmidrule(lr){3-5}\cmidrule(lr){6-8}
Period & Obs. & Med.\ $R$ & \% $R\geq40$ & Frontier $R$ & Med.\ $R$ & \% $R\geq40$ & Frontier $R$\\\midrule
""" + '\n'.join(orow) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: Excludes firm-years in which cash paid for acquisitions, or the increase in goodwill, is at least 25\% of prior-year revenue. Frontier $R$ is $\max_g[g+\phi_{0.95}(g)]$.
\end{table}"""
open(f'{BASE}/sections/tables/tab_organic.tex', 'w').write(tab_org)

# ---------------------------------------------------------------- 5. scale and capital intensity
bins = [100e6, 500e6, 2e9, 10e9, 1e13]
labs = ['\\$0.1--0.5B', '\\$0.5--2B', '\\$2--10B', '$>$\\$10B']
df['size_bin'] = pd.cut(df['rev_lag'], bins, labels=labs, right=False)
res['scale'] = {}
crow = []
for m in ['m_op', 'm_fcf_sbc']:
    res['scale'][m] = {}
    for lb in labs:
        d = df[(df.size_bin == lb)][['cik', 'g', m]].dropna()
        R = d['g'] + d[m]
        fa = order_alpha(d['g'].values, d[m].values, .95)
        s, g_ = frontier_score(fa)
        res['scale'][m][lb] = dict(n=int(len(d)), p95_R=float(R.quantile(.95)), p99_R=float(R.quantile(.99)),
                                   frontier_score=s, med_g=float(d['g'].median()))
for lb in labs:
    a = res['scale']['m_op'][lb]; b = res['scale']['m_fcf_sbc'][lb]
    crow.append(f"{lb} & {a['n']:,} & {100*a['med_g']:.1f} & {100*a['p95_R']:.0f} & {100*a['frontier_score']:.0f} & {100*b['p95_R']:.0f} & {100*b['frontier_score']:.0f} \\\\")
# spearman between log size and R at upper tail: quantile reg of R on log size
qs = {}
for m in ['m_op', 'm_fcf_sbc']:
    d = df[['g', m, 'lsize']].dropna(); d['R'] = d['g'] + d[m]
    f = smf.quantreg('R ~ lsize', d).fit(q=0.95)
    qs[m] = dict(b=float(f.params['lsize']), se=float(f.bse['lsize']))
res['scale_qreg'] = qs
tab5 = r"""\begin{table}[t]\centering\small
\caption{Scale and the attainable Rule-of-40 score, fiscal years 2010--2025}\label{tab:scale}
\begin{tabular}{lrrrrrr}\toprule
 & & & \multicolumn{2}{c}{GAAP operating} & \multicolumn{2}{c}{FCF after SBC}\\\cmidrule(lr){4-5}\cmidrule(lr){6-7}
Prior-year revenue & Obs. & Med.\ $g$ & P95 $R$ & Frontier $R$ & P95 $R$ & Frontier $R$\\\midrule
""" + '\n'.join(crow) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: Frontier $R$ is $\max_g[g+\phi_{0.95}(g)]$ within the size class. A $\tau=0.95$ quantile regression of $R$ on log prior-year revenue gives slopes of """ + f"{qs['m_op']['b']:.3f} ({qs['m_op']['se']:.3f})" + r""" on the GAAP basis and """ + f"{qs['m_fcf_sbc']['b']:.3f} ({qs['m_fcf_sbc']['se']:.3f})" + r""" on the FCF-after-SBC basis.
\end{table}"""
open(f'{BASE}/sections/tables/tab_scale.tex', 'w').write(tab5)

# capital intensity: FCF-after-SBC frontier for high vs low capex intensity (within-period median split)
df['hi_k'] = df.groupby('period', observed=True)['capex_int'].transform(lambda x: (x > x.median()).astype(float))
res['capint'] = {}
for p in PERIODS + ['all']:
    sub = df if p == 'all' else df[df.period == p]
    out = {}
    for hk in [0.0, 1.0]:
        d = sub[sub.hi_k == hk][['g', 'm_fcf_sbc', 'm_op']].dropna()
        out['hi' if hk else 'lo'] = dict(
            n=int(len(d)),
            fcf_score=frontier_score(order_alpha(d['g'].values, d['m_fcf_sbc'].values, .95))[0],
            op_score=frontier_score(order_alpha(d['g'].values, d['m_op'].values, .95))[0])
    res['capint'][p] = out
d = df[['g', 'm_fcf_sbc', 'capex_int', 'cik']].dropna(); d = d[(d.g <= 1.5) & (d.capex_int < 1)]
fk = smf.quantreg('m_fcf_sbc ~ g + capex_int + g:capex_int', d).fit(q=0.90)
res['capint_qreg'] = {k: dict(b=float(fk.params[k]), se=float(fk.bse[k])) for k in fk.params.index}

# ---------------------------------------------------------------- 6. stochastic frontier (normal/half-normal)
def sfa(y, X):
    n, k = X.shape
    b0 = np.linalg.lstsq(X, y, rcond=None)[0]
    def nll(th):
        b = th[:k]; su, sv = np.exp(th[k]), np.exp(th[k + 1])
        e = y - X @ b; s = np.sqrt(su ** 2 + sv ** 2); lam = su / sv
        ll = np.log(2) - np.log(s) + stats.norm.logpdf(e / s) + stats.norm.logcdf(-e * lam / s)
        return -ll.sum()
    r = optimize.minimize(nll, np.r_[b0, np.log(0.2), np.log(0.1)], method='BFGS')
    b = r.x[:k]; su, sv = np.exp(r.x[k]), np.exp(r.x[k + 1])
    return dict(beta=b.tolist(), sigma_u=float(su), sigma_v=float(sv), mean_ineff=float(su * np.sqrt(2 / np.pi)), ll=float(-r.fun))
res['sfa'] = {}
for m in ['m_op', 'm_fcf_sbc']:
    res['sfa'][m] = {}
    for p in PERIODS:
        d = df[df.period == p][['g', m]].dropna(); d = d[(d.g <= 1.5) & (d[m] > -1.5)]
        X = np.c_[np.ones(len(d)), d['g'], d['g'] ** 2]
        res['sfa'][m][p] = sfa(d[m].values, X)

# ---------------------------------------------------------------- figures
def fig_frontiers():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=False)
    for ax, m, lab in [(axes[0], 'm_op', 'GAAP operating margin'), (axes[1], 'm_fcf_sbc', 'FCF margin after SBC')]:
        d = df[df.period.isin(['2016-19', '2023-25'])][['g', m, 'period']].dropna()
        d = d[(d.g <= 1.2) & (d[m] > -1)]
        for p, c, mk in [('2016-19', '0.65', 'o'), ('2023-25', '0.15', '^')]:
            s = d[d.period == p]
            ax.scatter(s['g'], s[m], s=3, c=c, alpha=0.35, marker=mk, linewidths=0, label=f'{p} firm-years')
            fa = np.array(res['frontier'][m][p]['order_alpha'], dtype=float)
            ax.plot(GRID, fa, color=c, lw=1.8, ls='-' if p == '2023-25' else '--', label=f'{p} frontier ($\\phi_{{0.95}}$)')
        x = np.linspace(-0.1, 1.2, 50)
        ax.plot(x, 0.40 - x, color='k', lw=0.8, ls=':', label='Rule of 40 ($g+m=0.4$)')
        ax.axhline(0, color='0.8', lw=0.5)
        ax.set_xlim(-0.3, 1.2); ax.set_ylim(-1.0, 0.8)
        ax.set_xlabel('Revenue growth $g$'); ax.set_ylabel(lab)
    axes[0].legend(fontsize=6.5, frameon=False, loc='lower left')
    fig.tight_layout(); fig.savefig(f'{BASE}/figures/fig_empirical_frontier.pdf'); plt.close(fig)

def fig_scores_over_time():
    fig, ax = plt.subplots(figsize=(6.0, 2.8))
    yrs = sorted(df.year.unique())
    for m, c, lab in [('m_op', '0.1', 'GAAP operating'), ('m_fcf_sbc', '0.55', 'FCF after SBC')]:
        R = df.assign(R=df['g'] + df[m]).groupby('year')['R']
        ax.plot(yrs, 100 * R.median(), color=c, lw=1.5, label=f'Median, {lab}')
        ax.plot(yrs, 100 * R.quantile(.9), color=c, lw=1.0, ls='--', label=f'90th pct, {lab}')
        ax.plot(yrs, 100 * R.quantile(.99), color=c, lw=0.8, ls=':', label=f'99th pct, {lab}')
    ax.axhline(40, color='k', lw=0.6)
    ax.set_xlabel('Fiscal year'); ax.set_ylabel('Score $R=g+m$ (pp)')
    ax.legend(fontsize=6.3, frameon=False, ncol=2, loc='upper left')
    fig.tight_layout(); fig.savefig(f'{BASE}/figures/fig_scores_time.pdf'); plt.close(fig)

def fig_scale():
    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    x = np.arange(len(labs)); w = 0.38
    a = [100 * res['scale']['m_op'][l]['frontier_score'] for l in labs]
    b = [100 * res['scale']['m_fcf_sbc'][l]['frontier_score'] for l in labs]
    ax.bar(x - w/2, a, w, color='0.25', label='GAAP operating')
    ax.bar(x + w/2, b, w, color='0.65', label='FCF after SBC')
    ax.set_xticks(x); ax.set_xticklabels(['$0.1–0.5B', '$0.5–2B', '$2–10B', '>$10B'])
    ax.set_xlabel('Prior-year revenue'); ax.set_ylabel('Frontier score (pp)')
    ax.axhline(40, color='k', lw=0.6, ls=':')
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout(); fig.savefig(f'{BASE}/figures/fig_scale.pdf'); plt.close(fig)

fig_frontiers(); fig_scores_over_time(); fig_scale()

# pass-rate series and top performers (for text)
yr = df.assign(R=df['g'] + df['m_op'], Rf=df['g'] + df['m_fcf_sbc']).groupby('year').agg(
    n=('R', 'size'), med_R=('R', 'median'), p90_R=('R', lambda x: x.quantile(.9)), pass40=('R', lambda x: (x >= .4).mean()),
    med_Rf=('Rf', 'median'), pass40_f=('Rf', lambda x: (x >= .4).mean()))
res['by_year'] = json.loads(yr.to_json(orient='index'))
top = df.assign(R=df['g'] + df['m_op']).query('rev_lag >= 1e9').nlargest(15, 'R')[['name', 'year', 'rev', 'g', 'm_op', 'm_fcf_sbc', 'R']]
res['top_ge1B'] = json.loads(top.to_json(orient='records'))

json.dump(res, open(f'{BASE}/notes/empirics_results.json', 'w'), indent=1, default=float)
print('done')
