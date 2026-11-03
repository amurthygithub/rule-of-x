#!/usr/bin/env python3
"""
Referee A - Proposition 2 worked example (supp S2.2) solved independently.

Method: backward shooting of the HJB in u = v/s from the terminal singular point
s = sbar, using the local expansion u ~ ubar + A (sbar-s)^(1/(1-alpha)), then RK45
integration down to small s. Cross-checks:
  - the small-share root v0 (eq 19) at several r; lambda for v0 = 10 and 15;
  - the static optimum (g0, sigma0, m0) and the Gordon identity;
  - the claimed growth weights v'(s) = 9.1, 7.2, 5.4 at 1%, 10%, 50% of the cap
    and revenue multiples v(s)/s = 9.4, 8.1, 6.5;
  - the bounds (m0-kG)s/(r-G) <= v(s) <= v0 s;
  - the HJB identity R*_{v'(s)}(s) = (r-G)v(s)/s + G v'(s).
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
import math, sys, platform, datetime

print("session:", datetime.datetime.now().isoformat())
print("python", platform.python_version(), "numpy", np.__version__, "scipy", __import__('scipy').__version__)

results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + ("  " + str(detail) if detail else ""))

r, G, k, alpha, m0, sbar = 0.10, 0.04, 0.0, 0.3, 0.35, 0.5
Calpha = (1-alpha)*alpha**(alpha/(1-alpha))
q = 1/(1-alpha)

def lam_for_v0(v0):
    return ((r-G)*v0 - m0)/Calpha if False else \
        (((r-G)*v0 - m0)/Calpha)**(1-alpha)/v0

lam10 = lam_for_v0(10.0)
lam15 = lam_for_v0(15.0)
check("S2.2 lambda ~ 0.070 gives v0=10; lambda ~ 0.081 gives v0=15",
      abs(lam10-0.070) < 5e-4 and abs(lam15-0.081) < 5e-4, f"lam10={lam10:.4f} lam15={lam15:.4f}")

# static optimum at v0 = 10 (X = v0): g0 = G+Delta*, sigma0, m0circ
v0 = 10.0; lam = lam10
def Dstar(ell, X): return ell**q*(alpha*(X-k))**(alpha/(1-alpha)) if X > k else 0.0
D0 = Dstar(lam, v0); sig0 = alpha*(v0-k)*D0
g0 = G + D0; mcirc = m0 - k*g0 - sig0
check("S2.2 static optimum at v0=10: g0 = 7.6%, sigma0 = 10.7%, m0circ = 24.3%, v0 = m0circ/(r-g0) = 10",
      abs(g0-0.076) < 5e-4 and abs(sig0-0.107) < 5e-4 and abs(mcirc-0.243) < 5e-4
      and abs(mcirc/(r-g0) - 10.0) < 1e-9, f"g0={g0:.4f} sig0={sig0:.4f} m0={mcirc:.4f}")

# smaller root of (19) across discount rates: 14.6, 10.0, 5.8, 3.7, 2.1, 1.35
def v0_root(rr):
    f = lambda v: (rr-G)*v - m0 - Calpha*(lam*v)**q
    # find smallest positive root: f(0) = -m0 < 0; f grows then... find first sign change
    xs = np.linspace(0.01, 60, 6000)
    vals = [f(x) for x in xs]
    for i in range(1, len(xs)):
        if vals[i-1] < 0 <= vals[i]:
            return brentq(f, xs[i-1], xs[i])
    return None
claims = {0.0934: 14.6, 0.10: 10.0, 0.12: 5.8, 0.15: 3.7, 0.22: 2.1, 0.31: 1.35}
ok = True; det = []
for rr, cl in claims.items():
    root = v0_root(rr)
    det.append(f"r={rr}: {root:.2f} vs {cl}")
    if abs(root - cl) > 0.06: ok = False
check("S2.2 smaller root of (19) across r: 14.6, 10.0, 5.8, 3.7, 2.1, 1.35", ok, "; ".join(det))

# ---------------- backward shooting of the HJB --------------------------------------
lam = lam10
v0 = 10.0
def ell(s): return lam*(1-s/sbar)
def Dstar_ell(es, X): return es**q*(alpha*(X-k))**(alpha/(1-alpha)) if X > k else 0.0

# terminal point: u(sbar) = (m0-kG)/(r-G); local expansion u = ubar + A t^q, t = sbar - s
def Phi_(u_, s_):
    w_ = (r-G)*u_ - (m0-k*G)
    if w_ <= 0: return k
    return k + (w_/Calpha)**(1-alpha)/ell(s_)
ubar = (m0-k*G)/(r-G)
Aterm = Calpha*((lam/sbar)*(ubar-k))**q/(r-G)
t0 = 1e-9
s_start = sbar - t0
u_start = ubar + Aterm*t0**q

# ODE: s u' = Phi(u,s) - u ; integrate from s_start down to s_min
def Phi(u, s):
    w = (r-G)*u - (m0-k*G)
    if w <= 0: return k
    return k + (w/Calpha)**(1-alpha)/ell(s)
Phi = Phi_
def rhs(s, u):
    return (Phi(u[0], s) - u[0])/s
s_min = sbar*1e-7
sol = solve_ivp(rhs, [s_start, s_min], [u_start], rtol=1e-11, atol=1e-13,
                dense_output=True, max_step=sbar/2000)
ss = np.exp(np.linspace(math.log(s_min), math.log(sbar - 1e-9), 20000))
uu = sol.sol(ss)[0]
vv = ss*uu
# v'(s) = u + s u' and s u' = Phi - u  =>  v'(s) = Phi(u(s), s) exactly
vprime = np.array([Phi(uu[i], ss[i]) for i in range(len(ss))])
# check HJB residual: R*_{v'(s)}(s) = (r-G)v/s + G v'(s)
def Rstar(s, X):
    es = ell(s)
    y = X - k
    if y <= 0: return m0 + y*G
    return m0 + y*G + (1-alpha)*y*es**q*(alpha*y)**(alpha/(1-alpha))
resid = np.array([Rstar(s, xp) - ((r-G)*v/s + G*xp)
                  for s, v, xp in zip(ss[::200], vv[::200], vprime[::200])])
check("P2    HJB identity R*_{v'(s)}(s) = (r-G)v(s)/s + G v'(s) along the shot (max |resid| < 5e-3)",
      np.max(np.abs(resid)) < 5e-3, f"max|resid|={np.max(np.abs(resid)):.2e}")
check("P2    bounds (m0-kG)s/(r-G) <= v(s) <= v0 s hold on the grid",
      np.all(uu >= ubar - 1e-9) and np.all(uu <= v0 + 1e-8))
check("P2    small-share limit u(s) -> v0 as s -> 0 (within 0.01 for s < 1e-6*sbar)",
      abs(sol.sol(sbar*1e-7)[0] - v0) < 0.01, f"u(smin)={sol.sol(sbar*1e-7)[0]:.4f}")

# claimed weights and multiples at 1%, 10%, 50% of the cap
det = []
ok_w = True
for frac, wclaim, mclaim in [(0.01, 9.1, 9.4), (0.10, 7.2, 8.1), (0.50, 5.4, 6.5)]:
    s0 = frac*sbar
    u0 = sol.sol(s0)[0]
    # v'(s) by central difference of v
    vp = Phi(sol.sol(s0)[0], s0)
    det.append(f"s={frac:.0%}sbar: v'={vp:.2f} (claim {wclaim}), v/s={u0:.2f} (claim {mclaim})")
    if abs(vp-wclaim) > 0.25 or abs(u0-mclaim) > 0.25: ok_w = False
check("S2.2/P2  growth weight v'(s) = 9.1, 7.2, 5.4 and multiple v(s)/s = 9.4, 8.1, 6.5 at 1%, 10%, 50% of cap",
      ok_w, "; ".join(det))

# weight below the multiple at every share, and falling in s
interior = (ss > sbar*1e-4) & (ss < sbar*0.98)
check("P2/S2.2  v'(s) <= v(s)/s on the interior, and v' falling with s (v' = Phi(u,s) exact)",
      np.all(vprime[interior] <= uu[interior] + 1e-9) and np.all(np.diff(vprime[interior]) < 1e-9))

print()
nf = sum(1 for _, ok in results if not ok)
print(f"TOTAL {len(results)} checks, {nf} failures")
sys.exit(1 if nf else 0)