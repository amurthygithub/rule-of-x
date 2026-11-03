"""GPT-2: worked dynamic-weight profile (r=.1, G=.04, k=0, alpha=.3, m0=.35, v0=10) by shooting from the small-share singular point. Own code."""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
Calpha = lambda a: (1-a)*a**(a/(1-a))
a_, r, G, m0, k = 0.3, 0.10, 0.04, 0.35, 0.0
rho, b = r-G, m0-k*G
lam = brentq(lambda L: rho*10 - b - Calpha(a_)*(L*10)**(1/(1-a_)), 0.01, 0.5)
v0 = 10.0
sig = (a_*lam*(v0-k))**(1/(1-a_)); D0 = lam*sig**a_; aexp = rho/D0-1
c1 = (v0-k)/(1-aexp) if abs(1-aexp) > 1e-9 else 0
print(f'lambda={lam:.10f} Delta0={D0:.6f} a={aexp:.4f}')
def du(z, u):            # s u' = Phi(u,s) - u, u = v/s
    w = max((rho*u[0]-b)/Calpha(a_), 0.0)
    return [((k + w**(1-a_)/(lam*(1-z))) - u[0])/z]
lo_ev = lambda z, u: u[0] - b/rho - 1e-12; lo_ev.terminal = True
hi_ev = lambda z, u: u[0] - 60; hi_ev.terminal = True
z0 = 1e-5
def shoot(C):
    u0 = v0 + c1*z0 + C*z0**aexp
    s = solve_ivp(du, [z0, 1-1e-10], [u0], events=[lo_ev, hi_ev], rtol=1e-11, atol=1e-13, method='LSODA', dense_output=True)
    if s.t_events[0].size: return -1, s
    if s.t_events[1].size: return 1, s
    return 0, s
lo, hi = -1e6, 1e6
for C in [-1e3, -1e2, -10, -1, 0, 1, 10, 1e2, 1e3]:
    print(' C', C, shoot(C)[0])
# bisection on C between a 'too low' and a 'too high' value
L, Hh = None, None
for C in np.linspace(-200, 200, 81):
    f = shoot(C)[0]
    if f == -1: L = C
    elif f == 1 and L is not None: Hh = C; break
for _ in range(80):
    M = 0.5*(L+Hh); f = shoot(M)[0]
    if f == -1: L = M
    else: Hh = M
f, s = shoot(0.5*(L+Hh))
print('C*', 0.5*(L+Hh), 'reached z =', s.t[-1])
for z in [0.01, 0.1, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99]:
    if z > s.t[-1]: break
    u = s.sol(z)[0]; v = u*z
    w = max((rho*u-b)/Calpha(a_), 0.0); vp = k + w**(1-a_)/(lam*(1-z))
    print(f'  z={z:<5} weight v\'(s)={vp:.4f}  v/s={u:.4f}')
print('  saturation slope b/rho =', round(b/rho, 4))
