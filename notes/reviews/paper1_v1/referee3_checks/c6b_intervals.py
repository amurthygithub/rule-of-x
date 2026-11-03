"""Paired E1-E2 bootstrap for the scale gradient (cash) and T(20%) change (cash): percentile vs basic vs bias-corrected intervals."""
import sys, json; sys.path.insert(0, '.')
import numpy as np, pandas as pd, lib, statsmodels.formula.api as smf
from scipy import stats
V = lib.V; E1, E2 = V['E1'], V['E2']
firms = np.unique(E1.cik.values); idx1 = lib.cl_idx(E1.cik.values)
pos2 = pd.Series(np.arange(len(E2))).groupby(E2.cik.values).apply(lambda s: s.values).to_dict()
idx2 = [pos2.get(f, np.array([], int)) for f in firms]
def scale_cash(z):
    z = z[['lsize', 'R_cash']].dropna(); return float(smf.quantreg('R_cash ~ lsize', z).fit(q=0.95, max_iter=2000).params['lsize']) * np.log(10)
def T20_cash(z):
    z = z[['period', 'g', 'm_fcf_sbc']].dropna()
    f = lambda w: 0.2 + np.quantile(w.loc[w.g >= .2, 'm_fcf_sbc'], .95)
    return f(z[z.period == '2023-25']) - f(z[z.period == '2016-19'])
def p95chg_cash(z):
    z = z[['period', 'R_cash']].dropna(); return np.quantile(z.loc[z.period == '2023-25', 'R_cash'], .95) - np.quantile(z.loc[z.period == '2016-19', 'R_cash'], .95)
out = {}
for nm, fn, B in [('T20_cash', T20_cash, 2000), ('p95chg_cash', p95chg_cash, 2000), ('scale_cash', scale_cash, 800)]:
    rng = np.random.default_rng(99)
    est = fn(E1) - fn(E2); dd = []
    for _ in range(B):
        dr = rng.integers(0, len(firms), len(firms))
        dd.append(fn(E1.iloc[np.concatenate([idx1[j] for j in dr])]) - fn(E2.iloc[np.concatenate([idx2[j] for j in dr]).astype(int)]))
    dd = np.array(dd)
    pc = np.quantile(dd, [.05, .95]); basic = [2 * est - pc[1], 2 * est - pc[0]]
    z0 = stats.norm.ppf((dd < est).mean()); bc = np.quantile(dd, [stats.norm.cdf(2 * z0 - 1.645), stats.norm.cdf(2 * z0 + 1.645)])
    out[nm] = dict(est=est, mean=dd.mean(), median=float(np.median(dd)), se=dd.std(), percentile=pc.tolist(), basic=basic, bias_corrected=bc.tolist(), share_draws_below_est=float((dd < est).mean()))
    print(nm, {k: (np.round(v, 4).tolist() if isinstance(v, (list, np.ndarray)) else round(float(v), 4)) for k, v in out[nm].items()}, flush=True)
json.dump(out, open('c6b_results.json', 'w'), indent=1, default=float)
