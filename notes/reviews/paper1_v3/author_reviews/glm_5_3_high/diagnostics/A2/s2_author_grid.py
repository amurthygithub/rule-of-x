#!/usr/bin/env python3
"""A2: run the AUTHOR's own solve_hjb (copied verbatim from repo code/verify_theory.py)
and evaluate v'(s) = Phi(u,s) near the cap. Confirms/denies the U-turn on the author's
own discretization, independent of my shooting method."""
import numpy as np
from scipy.optimize import minimize_scalar

r_, G_, k_, a_, m0_ = 0.10, 0.04, 0.0, 0.3, 0.35
Ca = (1 - a_) * a_ ** (a_ / (1 - a_))
lam_for = lambda v0: (((r_ - G_) * v0 - (m0_ - k_ * G_)) / Ca) ** (1 - a_) / (v0 - k_)
lam10 = lam_for(10.0)
sbar_ = 0.5

def solve_hjb(m0_, k_, G_, r_, lam_, a_, sbar_, N=4000, smin=1e-9):
    half = N // 2
    u = np.concatenate([np.geomspace(smin, 0.5, half, endpoint=False), 1 - np.geomspace(0.5, 1e-9, N - half)])
    s = sbar_ * u
    v = np.zeros(N); sig = np.zeros(N)
    v[-1] = s[-1] * (m0_ - k_ * G_) / (r_ - G_)
    grid = np.concatenate([[0.0], np.geomspace(1e-10, 50, 240)])
    for i in range(N - 2, -1, -1):
        ell_i = lam_ * (1 - s[i] / sbar_)
        ds = s[i + 1] - s[i]
        def val(sg):
            D_ = ell_i * sg**a_
            ai = s[i] * D_ / ds
            return (s[i] * (m0_ - sg - k_ * (G_ + D_)) + ai * v[i + 1]) / ((r_ - G_) + ai)
        vals = np.array([val(x) for x in grid])
        j = int(np.argmax(vals))
        lo, hi = grid[max(j - 1, 0)], grid[min(j + 1, len(grid) - 1)]
        res = minimize_scalar(lambda x: -val(x), bounds=(lo, hi), method="bounded", options={"xatol": 1e-13})
        if -res.fun >= vals[j]:
            v[i], sig[i] = -res.fun, res.x
        else:
            v[i], sig[i] = vals[j], grid[j]
    return s, v, sig

s_h, v_h, sig_h = solve_hjb(m0_, k_, G_, r_, lam10, a_, sbar_, N=4000)
u_h = v_h / s_h
def Phi(u, s):
    w = (r_ - G_) * u - (m0_ - k_ * G_)
    if w <= 0: return k_
    return k_ + (w / Ca) ** (1 - a_) / (lam10 * (1 - s / sbar_))
vp_h = np.array([Phi(u_h[i], s_h[i]) for i in range(len(s_h))])
ubar = (m0_ - k_ * G_) / (r_ - G_)
print("author's upwind DP grid (N=4000), worked example; v' via exact Phi:")
for f in [0.01, 0.10, 0.50, 0.75, 0.80, 0.85, 0.90, 0.95, 0.98, 0.99, 0.995, 0.999, 0.9999]:
    i = np.searchsorted(s_h, f * sbar_)
    print(f"  s={100*f:6.2f}% of cap: v'={vp_h[i]:.4f}  v/s={u_h[i]:.4f}  gap v'-v/s={vp_h[i]-u_h[i]:+.4f}")
i_min = int(np.argmin(vp_h))
print(f"argmin v' = {vp_h[i_min]:.4f} at s = {s_h[i_min]/sbar_*100:.2f}% of cap;  ubar = {ubar:.4f}")
print(f"v' at last grid point (s={s_h[-1]/sbar_*100:.5f}% of cap): {vp_h[-1]:.4f}")
print(f"max(v'-v/s) over grid (s in (1e-4, 0.98) of cap): ",
      vp_h[(s_h>1e-4)&(s_h<0.98*sbar_)] .__sub__(u_h[(s_h>1e-4)&(s_h<0.98*sbar_)]).max())
