"""Check 2: (a) one observation per firm: firm-period means, medians, random single draw; frontier shape and score.
(b) sample-size artefact in period and size-class comparisons: equal-N subsampling.
(c) local (binned) conditional upper quantiles vs upper-set quantiles; simulated power of the upper-set slope.
(d) capital-intensity split in 2023-25: bootstrap CI of the difference; missing capex_int handling.
"""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/paper/notes/referee3')
from r3lib import *

df = load(); out = {}
M = ['m_op', 'm_fcf_sbc']

def slope_and_score(gv, mv, min_n=30):
    phi = order_alpha(gv, mv, 0.95, min_n)
    ok = ~np.isnan(phi)
    sl = np.polyfit(GRID[ok], phi[ok], 1)[0] if ok.sum() >= 2 else np.nan
    v = GRID + phi; k = int(np.nanargmax(v))
    return dict(phi0=round(100 * phi[0], 1), slope=round(sl, 3), edge=float(GRID[ok].max()),
                score=round(100 * v[k], 1), gmax=float(GRID[k]))

# (a) one observation per firm-period
print('=== (a) one observation per firm within period ===')
res_a = []
for m in M:
    for p in PERIODS:
        d = df[df.period == p][['cik', 'g', m]].dropna()
        base = slope_and_score(d.g.values, d[m].values)
        fmean = d.groupby('cik')[['g', m]].mean(); fmed = d.groupby('cik')[['g', m]].median()
        r_mean = slope_and_score(fmean.g.values, fmean[m].values)
        r_med = slope_and_score(fmed.g.values, fmed[m].values)
        # min_n scaled to the same share of the sample as 30/N_firmyears
        mn_scaled = max(10, int(round(30 * len(fmean) / len(d))))
        r_mean_sc = slope_and_score(fmean.g.values, fmean[m].values, min_n=mn_scaled)
        # random single firm-year per firm, 200 draws
        rng = np.random.default_rng(3); sc, sl = [], []
        g_ = d.groupby('cik')
        arr = [grp[['g', m]].values for _, grp in g_]
        for _ in range(200):
            pick = np.array([a[rng.integers(len(a))] for a in arr])
            rr = slope_and_score(pick[:, 0], pick[:, 1])
            sc.append(rr['score']); sl.append(rr['slope'])
        rec = dict(m=m, p=p, n_fy=len(d), n_firms=len(fmean), base_score=base['score'], base_slope=base['slope'],
                   mean_score=r_mean['score'], mean_slope=r_mean['slope'], mean_edge=r_mean['edge'],
                   med_score=r_med['score'], med_slope=r_med['slope'],
                   mean_score_scaledMinN=r_mean_sc['score'], scaled_min_n=mn_scaled,
                   single_draw_score_med=float(np.median(sc)), single_draw_score_5_95=[float(np.quantile(sc, .05)), float(np.quantile(sc, .95))],
                   single_draw_slope_med=float(np.median(sl)), single_draw_slope_5_95=[float(np.quantile(sl, .05)), float(np.quantile(sl, .95))])
        res_a.append(rec)
ta = pd.DataFrame(res_a); print(ta.to_string()); out['one_per_firm'] = res_a

# firm-mean P95 of R difference 2023-25 vs 2016-19 with bootstrap over firms
print('\n=== (a2) firm-mean upper quantiles of R, diff 2023-25 minus 2016-19 ===')
res_a2 = {}
for m in M:
    d = df[['cik', 'g', m, 'period']].dropna()
    fm = d.groupby(['period', 'cik'])[['g', m]].mean().reset_index(); fm['R'] = fm.g + fm[m]
    def st(x):
        a = x[x.period == '2023-25'].R.values; b = x[x.period == '2016-19'].R.values
        return np.array([np.quantile(a, .9) - np.quantile(b, .9), np.quantile(a, .95) - np.quantile(b, .95)])
    pt = st(fm); rng = np.random.default_rng(5); idx = cluster_index(fm.cik.values)
    bs = np.array([st(fm.iloc[cluster_draw(idx, rng)]) for _ in range(1000)])
    res_a2[m] = dict(p90_diff=round(100 * pt[0], 1), p90_ci=[round(100 * x, 1) for x in np.quantile(bs[:, 0], [.05, .95])],
                     p95_diff=round(100 * pt[1], 1), p95_ci=[round(100 * x, 1) for x in np.quantile(bs[:, 1], [.05, .95])])
print(res_a2); out['firm_mean_R_diff'] = res_a2

# (b) equal-N subsampling: periods and size classes
print('\n=== (b) equal-N subsampling (frontier score, MIN_N=30) ===')
bins = [100e6, 500e6, 2e9, 10e9, 1e13]; labs = ['0.1-0.5B', '0.5-2B', '2-10B', '>10B']
df['size_bin'] = pd.cut(df['rev_lag'], bins, labels=labs, right=False)
res_b = {}
for m in M:
    res_b[m] = {}
    for key, groups, col in [('size', labs, 'size_bin'), ('period', PERIODS, 'period')]:
        sub = {gname: df[df[col] == gname][['cik', 'g', m]].dropna() for gname in groups}
        nmin = min(len(v) for v in sub.values())
        rng = np.random.default_rng(9)
        rec = {}
        for gname, d in sub.items():
            full = frontier_score(d.g.values, d[m].values)[0]
            # subsample firm clusters until ~nmin firm-years (draw firms without replacement)
            idx = cluster_index(d.cik.values); vals = []
            for _ in range(300):
                perm = rng.permutation(len(idx)); take = []; cnt = 0
                for j in perm:
                    take.append(idx[j]); cnt += len(idx[j])
                    if cnt >= nmin: break
                ii = np.concatenate(take)
                vals.append(frontier_score(d.g.values[ii], d[m].values[ii])[0])
            vals = np.array(vals)
            R = d.g.values + d[m].values
            rec[gname] = dict(n=len(d), full=round(100 * full, 1), equalN_median=round(100 * np.nanmedian(vals), 1),
                              equalN_5_95=[round(100 * x, 1) for x in np.nanquantile(vals, [.05, .95])],
                              top5share=round(100 * top_share_score(d.g.values, d[m].values, .05), 1),
                              p95R=round(100 * np.quantile(R, .95), 1))
        res_b[m][key] = dict(nmin=nmin, groups=rec)
        print(m, key, 'nmin=', nmin); print(pd.DataFrame(rec).T.to_string())
out['equalN'] = res_b

# (b2) cluster-bootstrap CI of the P95(R) slope on log size (paper uses iid asymptotic SE)
import statsmodels.formula.api as smf
print('\n=== (b2) tau=0.95 QR of R on log size: iid vs firm-cluster bootstrap SE ===')
df['lsize'] = np.log(df['rev_lag'] / 1e9)
res_b2 = {}
for m in M:
    d = df[['cik', 'g', m, 'lsize']].dropna().reset_index(drop=True); d['R'] = d.g + d[m]
    f = smf.quantreg('R ~ lsize', d).fit(q=0.95)
    rng = np.random.default_rng(13); idx = cluster_index(d.cik.values); bs = []
    for _ in range(300):
        x = d.iloc[cluster_draw(idx, rng)]
        bs.append(smf.quantreg('R ~ lsize', x).fit(q=0.95, max_iter=2000).params['lsize'])
    res_b2[m] = dict(b=float(f.params['lsize']), se_iid=float(f.bse['lsize']), se_cluster=float(np.std(bs)),
                     ci90=[float(x) for x in np.quantile(bs, [.05, .95])])
print(res_b2); out['size_qr'] = res_b2

# (c) local binned conditional quantiles of margin (not upper sets)
print('\n=== (c) local binned 90th/95th pct of margin by growth bin, pooled 2010-25 and 2023-25 ===')
edges = [-0.9, 0, 0.1, 0.2, 0.3, 0.4, 0.6, 5]
res_c = {}
for m in M:
    for p in ['all', '2016-19', '2023-25']:
        d = df if p == 'all' else df[df.period == p]
        d = d[['g', m]].dropna(); d['bin'] = pd.cut(d.g, edges)
        t = d.groupby('bin', observed=True)[m].agg(n='size', q90=lambda x: x.quantile(.9), q95=lambda x: x.quantile(.95))
        res_c[f'{m}_{p}'] = {str(k): v for k, v in t.round(3).to_dict(orient='index').items()}
        print(m, p); print(t.round(3).to_string())
out['local_bins'] = res_c

# (c2) power: does the upper-set order-alpha slope recover a known slope of -1 / -0.5?
print('\n=== (c2) simulation: upper-set phi_0.95 slope when the true local 95th pct frontier slope is s ===')
rng = np.random.default_rng(21)
d = df[df.period == '2016-19'][['g', 'm_fcf_sbc']].dropna()
gv = d.g.values; resid_pool = d.m_fcf_sbc.values - np.quantile(d.m_fcf_sbc.values, .5)
sim = {}
for s_true in [-1.0, -0.5, 0.0]:
    sl = []
    for _ in range(200):
        mv = 0.1 + s_true * gv + rng.choice(resid_pool, size=len(gv))
        phi = order_alpha(gv, mv); ok = ~np.isnan(phi)
        sl.append(np.polyfit(GRID[ok], phi[ok], 1)[0])
    sim[s_true] = dict(mean=round(float(np.mean(sl)), 3), p5_95=[round(float(x), 3) for x in np.quantile(sl, [.05, .95])])
print(sim); out['slope_power_sim'] = {str(k): v for k, v in sim.items()}

# (d) capital intensity split 2023-25
print('\n=== (d) capital-intensity split ===')
print('capex_int missing share:', df.capex_int.isna().mean())
df['hi_k'] = df.groupby('period', observed=True)['capex_int'].transform(lambda x: (x > x.median()).astype(float))
res_d = {}
for m in ['m_fcf_sbc', 'm_op']:
    for p in ['2016-19', '2020-22', '2023-25']:
        d = df[df.period == p][['cik', 'g', m, 'hi_k']].dropna().reset_index(drop=True)
        def st(x):
            lo = x[x.hi_k == 0]; hi = x[x.hi_k == 1]
            a = frontier_score(lo.g.values, lo[m].values)[0]; b = frontier_score(hi.g.values, hi[m].values)[0]
            Rl = lo.g + lo[m]; Rh = hi.g + hi[m]
            return np.array([b - a, np.quantile(Rh, .95) - np.quantile(Rl, .95), (hi.g >= .4).sum(), (lo.g >= .4).sum()])
        pt = st(d); rng = np.random.default_rng(17); idx = cluster_index(d.cik.values)
        bs = np.array([st(d.iloc[cluster_draw(idx, rng)]) for _ in range(500)])
        res_d[f'{m}_{p}'] = dict(frontier_diff_hi_minus_lo=round(100 * pt[0], 1), ci90=[round(100 * x, 1) for x in np.nanquantile(bs[:, 0], [.05, .95])],
                                 p95R_diff=round(100 * pt[1], 1), p95R_ci90=[round(100 * x, 1) for x in np.nanquantile(bs[:, 1], [.05, .95])],
                                 n_g40_hi=int(pt[2]), n_g40_lo=int(pt[3]))
        print(m, p, res_d[f'{m}_{p}'])
out['capint'] = res_d
json.dump(out, open('/home/claude/paper/notes/referee3/check2_results.json', 'w'), indent=1, default=float)
