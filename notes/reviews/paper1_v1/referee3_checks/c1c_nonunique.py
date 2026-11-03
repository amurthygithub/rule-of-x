import sys; sys.path.insert(0, '.')
import numpy as np, lib
from scipy.optimize import linprog
V = lib.V
def qr_range(y, x, tau):
    y = np.asarray(y, float); x = np.asarray(x, float); n = len(y); k = 2
    X = np.c_[np.ones(n), x]
    c = np.r_[np.zeros(2 * k), tau * np.ones(n), (1 - tau) * np.ones(n)]
    A = np.c_[X, -X, np.eye(n), -np.eye(n)]
    bnd = [(0, None)] * (2 * k + 2 * n)
    r = linprog(c, A_eq=A, b_eq=y, bounds=bnd, method='highs'); fmin = r.fun
    out = []
    for s in [1, -1]:
        cs = np.zeros(2 * k + 2 * n); cs[1] = s; cs[3] = -s           # minimise (or maximise) slope b1 = u1 - v1
        rr = linprog(cs, A_ub=c[None, :], b_ub=[fmin * (1 + 1e-10) + 1e-12], A_eq=A, b_eq=y, bounds=bnd, method='highs')
        out.append(rr.x[1] - rr.x[3])
    return fmin, out
for vn in ['E1', 'E2', 'E2x25', 'E2add', 'E2max']:
    for m in ['m_op', 'm_fcf_sbc']:
        d = V[vn][['g', m]].dropna(); d = d[(d.g >= 0) & (d.g <= 0.6)]
        f, (lo, hi) = qr_range(d[m].values, d.g.values, 0.9)
        print(vn, m, len(d), 'set of minimising slopes [%.4f, %.4f]' % (lo, hi))
