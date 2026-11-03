"""Revised empirical analysis after referee review (sample-size-invariant statistics).

Replaces the max-over-grid 'frontier score' as headline statistic with:
  (1) upper quantiles of the score R = g + m by period, with firm-cluster bootstrap intervals;
  (2) fixed-threshold frontier points T(g0) = g0 + phi_0.95(g0);
  (3) local upper quantiles of margin by growth bin and upper-quantile slopes on g in [0, 0.6];
  (4) robustness: one observation per firm-period, excluding SIC 7370, excluding non-U.S. filers,
      excluding acquisition-driven or unverified hypergrowth firm-years;
  (5) scale and capital intensity on N-invariant statistics;
  (6) stochastic frontier mean shortfall by entry cohort;
  (7) the spend-to-excess-growth ratio implied by the model's first-order condition;
  (8) transparency: the edge 'frontier score' as a function of the minimum cell size.
Outputs: sections/tables/tab_top.tex, tab_threshold.tex, tab_local.tex, tab_scale.tex (overwrites),
tab_robust.tex, tab_edge.tex; figures/fig_empirical_frontier.pdf, fig_scale.pdf (overwrite);
notes/empirics_revised.json
"""
import os
import json, warnings
import numpy as np
import pandas as pd
from scipy import optimize, stats
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # replication-package root
B = 500
rng = np.random.default_rng(20261029)
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
                     'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})
PERIODS = ['2010-15', '2016-19', '2020-22', '2023-25']
df = pd.read_csv(f'{BASE}/data/panel.csv')
uni = json.load(open(f'{BASE}/data/sic_universe.json'))
loc = {int(r[1]): r[3] for r in uni}
US = set('AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR'.split())
df['us'] = df.cik.map(lambda c: loc.get(c, '') in US).astype(int)
df['R_op'] = df.g + df.m_op
df['R_cash'] = df.g + df.m_fcf_sbc
df['acq_or_unverified'] = ((df.acq_flag == 1) | ((df.g >= 1.0) & df.acq_pay.isna() & df.gw_jump.isna())).astype(int)
first_year = df.groupby('cik')['year'].min()
df['entry_cohort'] = np.where(df.cik.map(first_year) >= 2019, '2019+', 'pre-2019')
res = {}
MB = {'op': ('m_op', 'R_op', 'GAAP operating'), 'cash': ('m_fcf_sbc', 'R_cash', 'FCF after SBC')}


def cl_idx(cik):
    firms, inv = np.unique(cik, return_inverse=True)
    order = np.argsort(inv, kind='stable')
    bounds = np.r_[0, np.cumsum(np.bincount(inv))]
    return [order[bounds[j]:bounds[j + 1]] for j in range(len(firms))]


def boot_stat(d, fn, B=B):
    idx = cl_idx(d['cik'].values)
    out = []
    for _ in range(B):
        dr = rng.integers(0, len(idx), len(idx))
        ii = np.concatenate([idx[j] for j in dr])
        out.append(fn(d.iloc[ii]))
    return np.array(out, dtype=float)


def ci(a):
    return [float(np.nanquantile(a, .05)), float(np.nanquantile(a, .95))]


def diff_test(d, fn, p_new='2023-25', p_old='2016-19'):
    sub = d[d.period.isin([p_new, p_old])]
    stat = lambda x: fn(x[x.period == p_new]) - fn(x[x.period == p_old])
    bs = boot_stat(sub, stat)
    return dict(diff=float(stat(sub)), ci90=ci(bs))


# ---------------------------------------------------------------- (1) upper quantiles of R
res['top'] = {}
for key, (m, R, lab) in MB.items():
    d = df[['cik', 'period', R]].dropna()
    out = {}
    for p in PERIODS:
        x = d[d.period == p]
        for q in [0.5, 0.9, 0.95]:
            f = (lambda z, q=q: np.quantile(z[R], q))
            out[f'{p}|q{int(q*100)}'] = dict(est=float(f(x)), ci90=ci(boot_stat(x, f, B=300)))
    for q in [0.5, 0.9, 0.95]:
        f = (lambda z, q=q: np.quantile(z[R], q))
        out[f'diff_1619|q{int(q*100)}'] = diff_test(d, f)
        out[f'diff_1015|q{int(q*100)}'] = diff_test(d, f, p_old='2010-15')
    res['top'][key] = out


def cell(e, c=None, sign=False):
    fmt = '{:+.0f}' if sign else '{:.0f}'
    s = fmt.format(100 * e)
    if c:
        s += ' [' + fmt.format(100 * c[0]) + ', ' + fmt.format(100 * c[1]) + ']'
    return s

rows = []
for key, (m, R, lab) in MB.items():
    t = res['top'][key]
    for q in [50, 90, 95]:
        name = {50: 'Median', 90: '90th percentile', 95: '95th percentile'}[q]
        rows.append(f"{lab} & {name} & " + ' & '.join(cell(t[f'{p}|q{q}']['est']) for p in PERIODS) +
                    f" & {cell(t[f'diff_1619|q{q}']['diff'], t[f'diff_1619|q{q}']['ci90'], True)} \\\\")
    if key == 'op':
        rows.append('\\addlinespace')
tab = r"""\begin{table}[t]\centering\small
\caption{The top of the score distribution fell after 2022}\label{tab:top}
\resizebox{\textwidth}{!}{\begin{tabular}{llrrrrc}\toprule
Margin basis & Statistic of $R=g+m$ & 2010--15 & 2016--19 & 2020--22 & 2023--25 & Change, 2016--19 to 2023--25\\\midrule
""" + '\n'.join(rows) + r"""
\bottomrule\end{tabular}}
\par\vspace{2pt}\footnotesize\raggedright Notes: Scores in percentage points. Brackets give 90\% firm-cluster bootstrap intervals (500 replications) for the change between periods; changes are computed before rounding.
\end{table}"""
open(f'{BASE}/sections/tables/tab_top.tex', 'w').write(tab)

# ---------------------------------------------------------------- (2) fixed-threshold frontier points
TH = [0.0, 0.1, 0.2, 0.3, 0.4]
res['threshold'] = {}
for key, (m, R, lab) in MB.items():
    d = df[['cik', 'period', 'g', m]].dropna()
    out = {}
    for g0 in TH:
        f = (lambda z, g0=g0: g0 + np.quantile(z.loc[z.g >= g0, m], .95) if (z.g >= g0).sum() >= 10 else np.nan)
        for p in PERIODS:
            x = d[d.period == p]
            out[f'{g0}|{p}'] = dict(est=float(f(x)), n=int((x.g >= g0).sum()))
        out[f'{g0}|diff'] = diff_test(d, f)
    res['threshold'][key] = out
rows = []
for key, (m, R, lab) in MB.items():
    t = res['threshold'][key]
    for g0 in [0.0, 0.2, 0.4]:
        rows.append(f"{lab} & {int(100*g0)} & " + ' & '.join(f"{cell(t[f'{g0}|{p}']['est'])} ({t[f'{g0}|{p}']['n']})" for p in PERIODS) +
                    f" & {cell(t[f'{g0}|diff']['diff'], t[f'{g0}|diff']['ci90'], True)} \\\\")
    if key == 'op':
        rows.append('\\addlinespace')
tab = r"""\begin{table}[t]\centering\small
\caption{Frontier points at fixed growth thresholds, $T(g_0)=g_0+\phi_{0.95}(g_0)$}\label{tab:threshold}
\resizebox{\textwidth}{!}{\begin{tabular}{lcrrrrc}\toprule
Margin basis & $g_0$ (\%) & 2010--15 & 2016--19 & 2020--22 & 2023--25 & Change, 2016--19 to 2023--25\\\midrule
""" + '\n'.join(rows) + r"""
\bottomrule\end{tabular}}
\par\vspace{2pt}\footnotesize\raggedright Notes: $\phi_{0.95}(g_0)$ is the 95th percentile of margin among firm-years with growth of at least $g_0$. Entries are $g_0+\phi_{0.95}(g_0)$ in percentage points, with the number of firm-years with growth of at least $g_0$ in parentheses; with fewer than 30 firm-years the 95th percentile is close to the sample maximum. Brackets give 90\% firm-cluster bootstrap intervals for the change, which is computed before rounding.
\end{table}"""
open(f'{BASE}/sections/tables/tab_threshold.tex', 'w').write(tab)

# ---------------------------------------------------------------- (3) local upper quantiles and slopes
BINS = [0, 0.1, 0.2, 0.3, 0.4, 0.6, 5]
BL = ['0--10', '10--20', '20--30', '30--40', '40--60', '$\\geq$60']
res['local'] = {}
for key, (m, R, lab) in MB.items():
    d = df[['cik', 'period', 'g', m]].dropna()
    d = d[d.g >= 0]
    d['bin'] = pd.cut(d.g, BINS, right=False, labels=BL)
    loc_q = d.groupby('bin', observed=True)[m].quantile(.9)
    loc_n = d.groupby('bin', observed=True).size()
    # quantile-regression slopes, tau=0.90, no size control, g in [0, 0.6]
    sl = {}
    for nm, sub in [('pooled', d), ('2010-19', d[d.period.isin(['2010-15', '2016-19'])]), ('2020-25', d[d.period.isin(['2020-22', '2023-25'])])]:
        s6 = sub[sub.g <= 0.6]
        fit = smf.quantreg(f'{m} ~ g', s6).fit(q=0.9, max_iter=5000)
        bs = boot_stat(s6, lambda z: smf.quantreg(f'{m} ~ g', z).fit(q=0.9, max_iter=2000).params['g'], B=200)
        sl[nm] = dict(b=float(fit.params['g']), se=float(np.nanstd(bs)), n=int(len(s6)))
    # firm-period means
    fm = d.groupby(['cik', 'period'])[['g', m]].mean().reset_index()
    fm6 = fm[(fm.g >= 0) & (fm.g <= 0.6)]
    f2 = smf.quantreg(f'{m} ~ g', fm6).fit(q=0.9, max_iter=5000)
    sl['firm_means'] = dict(b=float(f2.params['g']), se=float(f2.bse['g']), n=int(len(fm6)))
    res['local'][key] = dict(q90=[float(x) for x in loc_q.values], n=[int(x) for x in loc_n.values], slopes=sl)
rows = []
for key, (m, R, lab) in MB.items():
    L = res['local'][key]
    rows.append(f"{lab} & " + ' & '.join(cell(v) for v in L['q90']) +
                f" & {L['slopes']['pooled']['b']:.2f} ({L['slopes']['pooled']['se']:.2f}) \\\\")
rows.append('Firm-years & ' + ' & '.join(f"{n:,}" for n in res['local']['op']['n']) + ' & \\\\')
tab = r"""\begin{table}[t]\centering\small
\caption{Upper-decile margin by growth band, fiscal years 2010--2025}\label{tab:local}
\resizebox{\textwidth}{!}{\begin{tabular}{lrrrrrrc}\toprule
 & \multicolumn{6}{c}{Revenue growth band (\%)} & Slope on $g\in[0,0.6]$\\\cmidrule(lr){2-7}
Margin basis & """ + ' & '.join(BL) + r""" & ($\tau=0.90$)\\\midrule
""" + '\n'.join(rows) + r"""
\bottomrule\end{tabular}}
\par\vspace{2pt}\footnotesize\raggedright Notes: Entries are the 90th percentile of margin (percentage points) within each growth band, firm-years with non-negative growth. The last column is the slope of a $\tau=0.90$ linear quantile regression of margin on growth for $0\leq g\leq0.6$, with a firm-cluster bootstrap standard error in parentheses; a slope of $-1$ would mean each point of growth costs a point of margin.
\end{table}"""
open(f'{BASE}/sections/tables/tab_local.tex', 'w').write(tab)

# ---------------------------------------------------------------- (4) robustness on N-invariant statistics
def robust_row(d, key):
    m, R, _ = MB[key]
    d = d[['cik', 'period', 'g', m]].dropna(); d = d.assign(R=d.g + d[m])
    p95 = {p: float(np.quantile(d[d.period == p].R, .95)) for p in PERIODS}
    s6 = d[(d.g >= 0) & (d.g <= 0.6)]
    b = float(smf.quantreg(f'{m} ~ g', s6).fit(q=0.9, max_iter=5000).params['g'])
    dif = diff_test(d, lambda z: np.quantile(z.R, .95))
    return dict(p95=p95, slope=b, diff=dif, n=int(len(d)))

fmeans = df.groupby(['cik', 'period']).agg(g=('g', 'mean'), m_op=('m_op', 'mean'), m_fcf_sbc=('m_fcf_sbc', 'mean')).reset_index()
broad = pd.read_csv(f'{BASE}/data/panel_broad.csv')
lease = df.assign(m_fcf_sbc=df.m_fcf_sbc_lease)
VARS = [('Baseline (SIC 7372)', df), ('One observation per firm and period (means)', fmeans),
        ('U.S.-located filers only', df[df.us == 1]),
        ('Excluding acquisition-affected years and unverified hypergrowth', df[df.acq_or_unverified == 0]),
        ('Excluding years with discontinued operations', df[df.disc_flag == 0]),
        ('Cash margin also net of finance-lease additions', lease),
        ('Broad sample (SIC 7370--7374)', broad)]
res['robust'] = {}
rows = []
for nm, d in VARS:
    r = {k: robust_row(d, k) for k in MB}
    res['robust'][nm] = r
    rows.append(f"{nm} & " + ' & '.join(cell(r[k]['p95'][p]) for k in MB for p in ['2016-19', '2023-25']) +
                ' & ' + ' & '.join(f"{r[k]['slope']:.2f}" for k in MB) + ' \\\\')
tab = r"""\begin{table}[t]\centering\small
\caption{Robustness of the main empirical findings}\label{tab:robust}
\resizebox{\textwidth}{!}{\begin{tabular}{lrrrrrr}\toprule
 & \multicolumn{4}{c}{95th percentile of $R$} & \multicolumn{2}{c}{Upper-decile slope on $g\in[0,0.6]$}\\\cmidrule(lr){2-5}\cmidrule(lr){6-7}
 & \multicolumn{2}{c}{GAAP operating} & \multicolumn{2}{c}{FCF after SBC} & GAAP & FCF after SBC\\\cmidrule(lr){2-3}\cmidrule(lr){4-5}
Sample & 2016--19 & 2023--25 & 2016--19 & 2023--25 & & \\\midrule
""" + '\n'.join(rows) + r"""
\bottomrule\end{tabular}}
\par\vspace{2pt}\footnotesize\raggedright Notes: Scores in percentage points. Slopes from $\tau=0.90$ linear quantile regressions of margin on growth for $0\leq g\leq0.6$, pooling 2010--2025. Unverified hypergrowth: growth of at least 100\% with neither acquisition payments nor goodwill reported. Non-U.S.\ filers are registrants whose EDGAR business address is outside the United States. Acquisition-affected years are flagged in the year of a material acquisition and the following year.
\end{table}"""
open(f'{BASE}/sections/tables/tab_robust.tex', 'w').write(tab)

# leave-one-firm-out: range of the 2016-19 to 2023-25 change in P95 of R when each firm is dropped
res['loo'] = {}
for key, (m, R, lab) in MB.items():
    d = df[df.period.isin(['2016-19', '2023-25'])][['cik', 'period', R]].dropna()
    base = np.quantile(d[d.period == '2023-25'][R], .95) - np.quantile(d[d.period == '2016-19'][R], .95)
    vals = []
    for c in d.cik.unique():
        x = d[d.cik != c]
        vals.append(np.quantile(x[x.period == '2023-25'][R], .95) - np.quantile(x[x.period == '2016-19'][R], .95))
    res['loo'][key] = dict(base=float(base), min=float(np.min(vals)), max=float(np.max(vals)))

# ---------------------------------------------------------------- (5) scale and capital intensity (N-invariant)
bins = [100e6, 500e6, 2e9, 10e9, 1e13]
labs = ['\\$0.1--0.5B', '\\$0.5--2B', '\\$2--10B', '$>$\\$10B']
df['size_bin'] = pd.cut(df['rev_lag'], bins, labels=labs, right=False)
df['lsize'] = np.log(df.rev_lag / 1e9)
res['scale'] = {}
for key, (m, R, lab) in MB.items():
    d = df[['cik', 'size_bin', 'lsize', 'g', R]].dropna()
    out = {}
    for lb in labs:
        x = d[d.size_bin == lb]
        out[lb] = dict(n=int(len(x)), p90=float(np.quantile(x[R], .9)), p95=float(np.quantile(x[R], .95)),
                       p95_ci=ci(boot_stat(x, lambda z: np.quantile(z[R], .95), B=300)), med_g=float(x.g.median()))
    fit = smf.quantreg(f'{R} ~ lsize', d).fit(q=0.95, max_iter=5000)
    bs = boot_stat(d, lambda z: smf.quantreg(f'{R} ~ lsize', z).fit(q=0.95, max_iter=2000).params['lsize'], B=200)
    out['slope'] = dict(b=float(fit.params['lsize']), se=float(np.nanstd(bs)))
    res['scale'][key] = out
rows = []
for lb in labs:
    a, c = res['scale']['op'][lb], res['scale']['cash'][lb]
    rows.append(f"{lb} & {a['n']:,} & {100*a['med_g']:.1f} & {cell(a['p95'], a['p95_ci'])} & {cell(c['p95'], c['p95_ci'])} \\\\")
so, sc = res['scale']['op']['slope'], res['scale']['cash']['slope']
tab = r"""\begin{table}[t]\centering\small
\caption{Scale and the upper tail of the score, fiscal years 2010--2025}\label{tab:scale}
\begin{tabular}{lrrcc}\toprule
Prior-year revenue & Obs. & Median $g$ (\%) & P95 of $R$, GAAP & P95 of $R$, FCF after SBC\\\midrule
""" + '\n'.join(rows) + r"""
\midrule
Slope on log revenue ($\tau=0.95$) & & & """ + f"{100*so['b']:.1f} ({100*so['se']:.1f})" + ' & ' + f"{100*sc['b']:.1f} ({100*sc['se']:.1f})" + r""" \\
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: P95 of $R$ in percentage points with 90\% firm-cluster bootstrap intervals. The last row is the coefficient (points per log unit of prior-year revenue) from a $\tau=0.95$ quantile regression of $R$ on log prior-year revenue, with a firm-cluster bootstrap standard error.
\end{table}"""
open(f'{BASE}/sections/tables/tab_scale.tex', 'w').write(tab)

df['hi_k'] = df.groupby('period', observed=True)['capex_int'].transform(lambda x: (x > x.median()).astype(float))
res['capint'] = {}
for key, (m, R, lab) in MB.items():
    out = {}
    for p in PERIODS:
        d = df[df.period == p][['cik', 'hi_k', R]].dropna()
        stat = lambda z: np.quantile(z.loc[z.hi_k == 1, R], .95) - np.quantile(z.loc[z.hi_k == 0, R], .95)
        out[p] = dict(gap=float(stat(d)), ci90=ci(boot_stat(d, stat, B=400)),
                      hi=float(np.quantile(d.loc[d.hi_k == 1, R], .95)), lo=float(np.quantile(d.loc[d.hi_k == 0, R], .95)))
    res['capint'][key] = out

# ---------------------------------------------------------------- (6) stochastic frontier by cohort
def sfa(y, X):
    k = X.shape[1]
    b0 = np.linalg.lstsq(X, y, rcond=None)[0]
    def nll(th):
        b = th[:k]; su, sv = np.exp(th[k]), np.exp(th[k + 1])
        e = y - X @ b; s = np.sqrt(su ** 2 + sv ** 2); lam = su / sv
        return -(np.log(2) - np.log(s) + stats.norm.logpdf(e / s) + stats.norm.logcdf(-e * lam / s)).sum()
    r = optimize.minimize(nll, np.r_[b0, np.log(0.2), np.log(0.1)], method='BFGS')
    su = float(np.exp(r.x[k]))
    return su * np.sqrt(2 / np.pi)
res['sfa'] = {}
for key, (m, R, lab) in MB.items():
    out = {}
    for p in PERIODS:
        for coh in ['all', 'pre-2019', '2019+']:
            d = df[df.period == p][['g', m, 'entry_cohort']].dropna()
            d = d[(d.g <= 1.5) & (d[m] > -1.5)]
            if coh != 'all':
                d = d[d.entry_cohort == coh]
            if len(d) < 60:
                continue
            X = np.c_[np.ones(len(d)), d.g, d.g ** 2]
            out[f'{p}|{coh}'] = dict(shortfall=float(sfa(d[m].values, X)), n=int(len(d)))
    res['sfa'][key] = out

# ---------------------------------------------------------------- (7) spend-to-excess-growth ratio
df['G_t'] = df.groupby('year')['g'].transform('median')
x = df[(df.g > df.G_t) & df.sm_lag_share.between(0.01, 1.5) & (df.acq_or_unverified == 0)].copy()
x['ratio'] = x.sm_lag_share / (x.g - x.G_t)
res['spend_ratio'] = dict(median=float(x.ratio.median()), iqr=[float(x.ratio.quantile(.25)), float(x.ratio.quantile(.75))],
                          med_sm=float(x.sm_lag_share.median()), med_excess=float((x.g - x.G_t).median()), n=int(len(x)))

# ---------------------------------------------------------------- (8) edge score vs minimum cell size (transparency)
GRID = np.round(np.arange(0.0, 1.01, 0.05), 2)
def edge_score(gv, mv, min_n):
    best = -np.inf
    for g0 in GRID:
        s = mv[gv >= g0]
        if len(s) >= min_n:
            best = max(best, g0 + np.quantile(s, .95))
    return best
res['edge'] = {}
rows = []
for key, (m, R, lab) in MB.items():
    out = {}
    for p in PERIODS:
        d = df[df.period == p][['g', m]].dropna()
        out[p] = {n: float(edge_score(d.g.values, d[m].values, n)) for n in [15, 30, 50, 100]}
    res['edge'][key] = out
    for n in [15, 30, 50, 100]:
        rows.append(f"{lab} & {n} & " + ' & '.join(cell(out[p][n]) for p in PERIODS) + ' \\\\')
    if key == 'op':
        rows.append('\\addlinespace')
tab = r"""\begin{table}[t]\centering\small
\caption{The edge score $\max_g[g+\phi_{0.95}(g)]$ depends on the minimum cell size}\label{tab:edge}
\begin{tabular}{lrrrrr}\toprule
Margin basis & Min.\ firm-years & 2010--15 & 2016--19 & 2020--22 & 2023--25\\\midrule
""" + '\n'.join(rows) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: The maximum is taken over growth thresholds $g\in\{0,0.05,\dots,1\}$ at which at least the stated number of firm-years grew at least $g$. Because the observed frontier falls by less than one point of margin per point of growth, the maximum sits at the edge of the growth support, so the statistic is governed by a handful of firm-years and falls as the minimum cell size rises.
\end{table}"""
open(f'{BASE}/sections/tables/tab_edge.tex', 'w').write(tab)

# ---------------------------------------------------------------- figures
def fig_local():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))
    mids = [0.05, 0.15, 0.25, 0.35, 0.5, 0.75]
    for ax, key in zip(axes, ['op', 'cash']):
        m, R, lab = MB[key]
        d = df[['g', m, 'period']].dropna(); d = d[(d.g <= 1.2) & (d[m] > -1)]
        ax.scatter(d.g, d[m], s=2.5, c='0.6', alpha=0.35, linewidths=0, label='Firm-years, 2010--2025')
        ax.plot(mids, res['local'][key]['q90'], color='0.1', marker='o', ms=3.5, lw=1.5, label='90th percentile of margin by growth band')
        x = np.linspace(-0.3, 1.2, 50)
        ax.plot(x, 0.40 - x, color='k', lw=0.8, ls=':', label='Rule of 40 ($g+m=0.4$)')
        ax.axhline(0, color='0.85', lw=0.5)
        ax.set_xlim(-0.3, 1.2); ax.set_ylim(-1.0, 0.8)
        ax.set_xlabel('Revenue growth $g$'); ax.set_ylabel(lab + ' margin')
    axes[0].legend(fontsize=6.5, frameon=False, loc='lower left')
    fig.tight_layout(); fig.savefig(f'{BASE}/figures/fig_empirical_frontier.pdf'); plt.close(fig)

def fig_scale():
    fig, ax = plt.subplots(figsize=(4.8, 2.7))
    x = np.arange(len(labs)); w = 0.36
    for off, key, col in [(-w / 2, 'op', '0.25'), (w / 2, 'cash', '0.65')]:
        v = [100 * res['scale'][key][l]['p95'] for l in labs]
        lo = [100 * res['scale'][key][l]['p95_ci'][0] for l in labs]
        hi = [100 * res['scale'][key][l]['p95_ci'][1] for l in labs]
        ax.bar(x + off, v, w, color=col, label=MB[key][2],
               yerr=[np.array(v) - np.array(lo), np.array(hi) - np.array(v)], capsize=2, error_kw=dict(lw=0.7))
    ax.set_xticks(x); ax.set_xticklabels(['$0.1–0.5B', '$0.5–2B', '$2–10B', '>$10B'])
    ax.set_xlabel('Prior-year revenue'); ax.set_ylabel('95th percentile of score (pp)')
    ax.axhline(40, color='k', lw=0.6, ls=':')
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout(); fig.savefig(f'{BASE}/figures/fig_scale.pdf'); plt.close(fig)

fig_local(); fig_scale()
json.dump(res, open(f'{BASE}/notes/empirics_revised.json', 'w'), indent=1, default=float)
print('done')
