#!/usr/bin/env python3
"""A2 FAST genericity sweep. Lighter tolerances than s1_vprime_profile.py
(rtol 1e-9, atol 1e-11, max_step sbar/500, shot from t0=1e-5*sbar, integrate to
sbar*1e-5). Purpose: confirm the analytic genericity argument (terminal balance
forces v'(sbar-) = ubar from below) across parameter draws. Prints per draw
IMMEDIATELY (unbuffered)."""
import numpy as np
from scipy.integrate import solve_ivp
import math, sys, platform, datetime
print("session:", datetime.datetime.now().isoformat())
print("python", platform.python_version(), "numpy", np.__version__, "scipy", __import__('scipy').__version__)

def solve_draw(r, G, k, alpha, m0, sbar, lam, rtol=1e-9, atol=1e-11, ms_div=500):
    Calpha = (1-alpha)*alpha**(alpha/(1-alpha)); qq = 1/(1-alpha)
    ubar = (m0-k*G)/(r-G)
    assert ubar > k
    def Phi(u, s):
        w = (r-G)*u - (m0-k*G)
        if w <= 0: return k
        return k + (w/Calpha)**(1-alpha)/(lam*(1-s/sbar))
    a = Calpha*((lam/sbar)*(ubar-k))**qq/(r-G)
    t0 = 1e-5*sbar
    s_start = sbar - t0; u_start = ubar + a*t0**qq
    def rhs(s, u): return (Phi(u[0], s) - u[0])/s
    s_min = sbar*1e-5
    sol = solve_ivp(rhs, [s_start, s_min], [u_start], rtol=rtol, atol=atol,
                    dense_output=True, max_step=sbar/ms_div)
    assert sol.success, sol.message
    sA = np.exp(np.linspace(math.log(s_min), math.log(sbar-1.01e-5*sbar), 3000))
    tB = sbar*np.exp(np.linspace(math.log(1e-5), math.log(0.3), 1500))
    ss = np.unique(np.concatenate([sA, sbar-tB]))
    uu = sol.sol(ss)[0]
    vp = np.array([Phi(uu[i], ss[i]) for i in range(len(ss))])
    return ss, uu, vp, ubar, sol, s_min

def lam_for_v0(v0, r, G, k, alpha, m0):
    Calpha = (1-alpha)*alpha**(alpha/(1-alpha))
    return (((r-G)*v0 - (m0 - k*G))/Calpha)**(1-alpha)/(v0-k)

draws = [
    ("worked example (v0=10)",  0.10, 0.04, 0.0, 0.30, 0.35, 0.5, 10.0),
    ("v0=15 calibration",      0.10, 0.04, 0.0, 0.30, 0.35, 0.5, 15.0),
    ("low multiple v0=6",       0.10, 0.04, 0.0, 0.30, 0.35, 0.5, 6.0),
    ("high r=22% (v0~2.1)",     0.22, 0.04, 0.0, 0.30, 0.35, 0.5, 2.1),
    ("alpha=0.25",              0.10, 0.04, 0.0, 0.25, 0.35, 0.5, 10.0),
    ("alpha=0.45",              0.10, 0.04, 0.0, 0.45, 0.35, 0.5, 10.0),
    ("alpha=0.7",               0.10, 0.04, 0.0, 0.70, 0.35, 0.5, 10.0),
    ("k=0.05 capital",          0.10, 0.04, 0.05, 0.30, 0.35, 0.5, 10.0),
    ("m0=0.25",                 0.10, 0.04, 0.0, 0.30, 0.25, 0.5, 10.0),
    ("G=0.08 fast market",      0.15, 0.08, 0.0, 0.30, 0.35, 0.5, 10.0),
    ("sbar=0.25 tight cap",     0.10, 0.04, 0.0, 0.30, 0.35, 0.25, 10.0),
    ("r=0.0934 (v0~14.6)",      0.0934, 0.04, 0.0, 0.30, 0.35, 0.5, 14.57),
]
allU = allRise = allBelow = allShot = True
for (name, rr, GG, kk, al, mm, sb, v0t) in draws:
    ub = (mm-kk*GG)/(rr-GG)
    if v0t <= ub or ub <= kk:
        print(f"  {name}: infeasible (ubar={ub:.3f} >= v0), skipped"); continue
    lm = lam_for_v0(v0t, rr, GG, kk, al, mm)
    ss, uu, vp, ub, sol, s_min = solve_draw(rr, GG, kk, al, mm, sb, lm)
    i2 = int(np.argmin(vp))
    dv = np.diff(vp)
    rising = bool(np.any(dv > 0)) and int(np.where(dv>0)[0][-1]) == len(dv)-1
    below = bool(np.max(vp-uu) <= 1e-9)
    shot_ok = abs(sol.sol(s_min)[0]-v0t) < 0.05*v0t
    allU &= bool(vp[i2] < ub-1e-9); allRise &= rising; allBelow &= below; allShot &= shot_ok
    print(f"  {name}: v0={v0t:5.2f} ubar={ub:7.3f} min v'={vp[i2]:7.3f} at {100*ss[i2]/sb:5.1f}% cap "
          f"| v'(0.99sb)={vp[np.searchsorted(ss,0.99*sb)]:6.3f} v'(smax)={vp[-1]:7.4f} "
          f"| rising-tail={rising} v'<=v/s={below} shot-v0={shot_ok} (u(smin)={sol.sol(s_min)[0]:.4f})")
print("SWEEP VERDICTS: min v' < ubar in all draws:", allU,
      "| rising terminal tail in all draws:", allRise,
      "| v' <= v/s in all draws:", allBelow,
      "| shot matches v0 in all draws:", allShot)
