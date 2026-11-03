import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd, lib
from scipy.optimize import linprog
V = lib.V
def qr_lp_X(y, X, tau):
    y = np.asarray(y, float); X = np.asarray(X, float); n, k = X.shape
    c = np.r_[np.zeros(2 * k), tau * np.ones(n), (1 - tau) * np.ones(n)]
    A = np.c_[X, -X, np.eye(n), -np.eye(n)]
    r = linprog(c, A_eq=A, b_eq=y, bounds=[(0, None)] * (2 * k + 2 * n), method='highs')
    return r.x[:k] - r.x[k:2 * k]
print('median prior-year revenue ($M) by period, E1:', V['E1'].groupby('period', observed=True).rev_lag.median().div(1e6).round(0).to_dict())
for vn in ['E1', 'E2']:
    for R in ['R_op', 'R_cash']:
        d = V[vn][['cik', 'period', 'lsize', 'g', R]].dropna()
        X0 = np.c_[np.ones(len(d)), d.lsize]
        b0 = qr_lp_X(d[R], X0, .95)[1]
        D = pd.get_dummies(d.period, drop_first=True).astype(float).values
        b1 = qr_lp_X(d[R], np.c_[X0, D], .95)[1]
        dd = d[d.g <= 1.5]
        b2 = qr_lp_X(dd[R], np.c_[np.ones(len(dd)), dd.lsize], .95)[1]
        print(vn, R, 'per tenfold: pooled %.1f | with period FE %.1f | g<=1.5 %.1f' % (100*b0*np.log(10), 100*b1*np.log(10), 100*b2*np.log(10)))
