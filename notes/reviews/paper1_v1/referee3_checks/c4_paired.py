"""Paired E1-E2 bootstrap for the pooled upper-decile slopes: exact LP vs IRLS, more replications, several seeds."""
import sys, json, time; sys.path.insert(0, '.')
import numpy as np, pandas as pd, lib, statsmodels.formula.api as smf
V = lib.V
E1, E2 = V['E1'], V['E2']
def frame(z, m): 
    z = z[['cik', 'g', m]].dropna(); return z[(z.g >= 0) & (z.g <= 0.6)]
def slope_irls(z, m): return float(smf.quantreg(f'{m} ~ g', z).fit(q=0.9, max_iter=2000).params['g'])
def slope_lp(z, m): return float(lib.qr_lp(z[m].values, z.g.values, 0.9)[1])
firms = np.unique(E1.cik.values)
idx1 = lib.cl_idx(E1.cik.values)
pos2 = pd.Series(np.arange(len(E2))).groupby(E2.cik.values).apply(lambda s: s.values).to_dict()
idx2 = [pos2.get(f, np.array([], int)) for f in firms]
res = {}
for m in ['m_op', 'm_fcf_sbc']:
    for seed, B, which in [(1, 2000, 'irls'), (2, 2000, 'irls'), (3, 600, 'lp')]:
        rng = np.random.default_rng(seed); out = []
        t = time.time()
        for _ in range(B):
            dr = rng.integers(0, len(firms), len(firms))
            a = frame(E1.iloc[np.concatenate([idx1[j] for j in dr])], m)
            b = frame(E2.iloc[np.concatenate([idx2[j] for j in dr]).astype(int)], m)
            f = slope_irls if which == 'irls' else slope_lp
            out.append((f(a, m), f(b, m)))
        o = np.array(out); dd = o[:, 0] - o[:, 1]
        res[f'{m}|{which}|seed{seed}|B{B}'] = dict(
            se_E1=float(o[:, 0].std()), se_E2=float(o[:, 1].std()), se_diff=float(dd.std()),
            ci90_diff=[float(np.quantile(dd, .05)), float(np.quantile(dd, .95))],
            ci95_diff=[float(np.quantile(dd, .025)), float(np.quantile(dd, .975))],
            share_diff_le0=float((dd <= 0).mean()), mean_diff=float(dd.mean()), median_diff=float(np.median(dd)),
            secs=time.time() - t)
        print(m, which, seed, B, json.dumps(res[f'{m}|{which}|seed{seed}|B{B}']), flush=True)
json.dump(res, open('c4_results.json', 'w'), indent=1)
