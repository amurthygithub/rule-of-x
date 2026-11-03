"""Referee 3 helper: rebuild E1/E2 variants exactly as code/estimate_organic.py does (lines 1-232), no bootstrap."""
import numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
SRC = '/home/claude/paper/code/estimate_organic.py'
lines = open(SRC).read().split('\n')
end = next(i for i, l in enumerate(lines) if l.startswith('def clean('))
g = {'__file__': SRC, '__name__': 'r3lib'}
exec(compile('\n'.join(lines[:end]), SRC, 'exec'), g)
V = g['V']; core = g['core']; P = g['P']
import statsmodels.formula.api as smf
from scipy.optimize import linprog
def qr_lp(y, x, tau):
    """Exact linear quantile regression (intercept + slope) by LP (HiGHS)."""
    y = np.asarray(y, float); x = np.asarray(x, float); n = len(y)
    X = np.c_[np.ones(n), x]; k = 2
    c = np.r_[np.zeros(2 * k), tau * np.ones(n), (1 - tau) * np.ones(n)]
    A = np.c_[X, -X, np.eye(n), -np.eye(n)]
    r = linprog(c, A_eq=A, b_eq=y, bounds=[(0, None)] * (2 * k + 2 * n), method='highs')
    b = r.x[:k] - r.x[k:2 * k]
    return b
def cl_idx(cik):
    firms, inv = np.unique(cik, return_inverse=True)
    order = np.argsort(inv, kind='stable')
    bounds = np.r_[0, np.cumsum(np.bincount(inv))]
    return [order[bounds[j]:bounds[j + 1]] for j in range(len(firms))]
def boot(d, fn, B, rng):
    idx = cl_idx(d['cik'].values); out = []
    for _ in range(B):
        dr = rng.integers(0, len(idx), len(idx))
        out.append(fn(d.iloc[np.concatenate([idx[j] for j in dr])]))
    return np.array(out, float)
