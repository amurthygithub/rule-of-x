"""Check 1: behaviour of the frontier score max_g[g+phi_0.95(g)].
(a) reproduce; (b) where the argmax sits; (c) sensitivity to MIN_N and grid; (d) bootstrap distribution of the edge;
(e) better-behaved alternatives: fixed thresholds, sample-share edge, upper quantiles of R; differences 2023-25 vs 2016-19.
"""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/paper/notes/referee3')
from r3lib import *

df = load()
out = {}
M = ['m_op', 'm_fcf_sbc']

# (a)-(c)
rows = []
for m in M:
    for p in PERIODS:
        d = df[(df.period == p)][['cik', 'g', m]].dropna()
        gv, mv = d.g.values, d[m].values
        rec = dict(m=m, p=p, n=len(d))
        for mn in [15, 30, 50, 75, 100]:
            s, ga, edge = frontier_score(gv, mv, min_n=mn)
            rec[f'score_n{mn}'] = round(100 * s, 1); rec[f'gmax_n{mn}'] = ga; rec[f'edge_n{mn}'] = edge
        s, ga, edge = frontier_score(gv, mv, min_n=30, grid=np.round(np.arange(0, 1.501, 0.01), 2))
        rec['score_fine'] = round(100 * s, 1); rec['gmax_fine'] = ga
        # distinct firms at the edge, and effective order statistic
        e = rec['edge_n30']; sub = d[d.g >= e]
        rec['edge_obs'] = len(sub); rec['edge_firms'] = sub.cik.nunique()
        rows.append(rec)
t = pd.DataFrame(rows)
print(t.to_string())
out['minn_sensitivity'] = rows

# (d) bootstrap distribution of argmax/edge and bias for the paper's statistic
bd = []
for m in M:
    for p in PERIODS:
        d = df[(df.period == p)][['cik', 'g', m]].dropna().reset_index(drop=True)
        est = frontier_score(d.g.values, d[m].values)[0]
        rng = np.random.default_rng(7); idx = cluster_index(d.cik.values)
        sc, ed = [], []
        for _ in range(500):
            ii = cluster_draw(idx, rng)
            s, ga, edge = frontier_score(d.g.values[ii], d[m].values[ii])
            sc.append(s); ed.append(ga == edge)
        sc = np.array(sc)
        bd.append(dict(m=m, p=p, est=round(100 * est, 1), boot_mean=round(100 * sc.mean(), 1),
                       boot_median=round(100 * np.median(sc), 1), ci90=[round(100 * x, 1) for x in ci(sc)],
                       share_boot_ge_est=round(float((sc >= est).mean()), 3), share_argmax_at_edge=round(float(np.mean(ed)), 3)))
print(pd.DataFrame(bd).to_string())
out['boot_diag'] = bd

# (e) alternatives with firm-cluster bootstrap, per period and difference 2023-25 minus 2016-19
def stats_for(d, m):
    gv, mv = d.g.values, d[m].values
    R = gv + mv
    return np.array([
        fixed_threshold_score(gv, mv, 0.20), fixed_threshold_score(gv, mv, 0.30), fixed_threshold_score(gv, mv, 0.40),
        top_share_score(gv, mv, 0.05), top_share_score(gv, mv, 0.10),
        np.quantile(R, 0.90), np.quantile(R, 0.95), np.quantile(R, 0.99),
        frontier_score(gv, mv)[0]])
NAMES = ['T20: 0.2+phi95(0.2)', 'T30: 0.3+phi95(0.3)', 'T40: 0.4+phi95(0.4)', 'Top5%: edge=g p95', 'Top10%: edge=g p90',
         'P90 R', 'P95 R', 'P99 R', 'Paper frontier score']
alt = {}
for m in M:
    dd = df[['cik', 'g', m, 'period']].dropna().reset_index(drop=True)
    pts = {p: stats_for(dd[dd.period == p], m) for p in PERIODS}
    rng = np.random.default_rng(11); idx = cluster_index(dd.cik.values)
    B = 1000
    bs = {p: [] for p in PERIODS}; bdiff = []
    for _ in range(B):
        ii = cluster_draw(idx, rng); x = dd.iloc[ii]
        v = {p: stats_for(x[x.period == p], m) for p in PERIODS}
        for p in PERIODS: bs[p].append(v[p])
        bdiff.append(v['2023-25'] - v['2016-19'])
    bdiff = np.array(bdiff)
    tab = []
    for j, nm in enumerate(NAMES):
        r = dict(stat=nm)
        for p in PERIODS:
            b = np.array(bs[p])[:, j]
            r[p] = f"{100*pts[p][j]:.0f} [{100*np.quantile(b,.05):.0f},{100*np.quantile(b,.95):.0f}]"
        dj = pts['2023-25'][j] - pts['2016-19'][j]; b = bdiff[:, j]
        r['diff 23-25 vs 16-19'] = f"{100*dj:+.0f} [{100*np.quantile(b,.05):+.0f},{100*np.quantile(b,.95):+.0f}]"
        # also 2023-25 vs 2010-15 pooled-early
        tab.append(r)
    alt[m] = tab
    print('\n', m); print(pd.DataFrame(tab).to_string())
out['alternatives'] = alt
json.dump(out, open('/home/claude/paper/notes/referee3/check1_results.json', 'w'), indent=1, default=float)
