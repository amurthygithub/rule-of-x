"""GPT-1: local HJB asymptotic near (s=0, v0). Own code."""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
Calpha = lambda a: (1-a)*a**(a/(1-a))
# --- A1: alpha=.5, lambda=.2, r=.1, G=0, m0=.1, k=0
a_, lam, r, G, m0, k = 0.5, 0.2, 0.1, 0.0, 0.1, 0.0
rho, b = r-G, m0-k*G
H = lambda v: rho*v - b - Calpha(a_)*(lam*(v-k))**(1/(1-a_))
v0 = brentq(H, 0.5, 3)
sig = (a_*lam*(v0-k))**(1/(1-a_)); D0 = lam*sig**a_
aexp = rho/D0 - 1
print(f'A1: v0={v0:.10f}, Delta0={D0:.10f}, a=(r-G)/Delta0-1={aexp:.8f}, forced linear coeff (v0-k)/(1-a)={(v0-k)/(1-aexp):.9f} (per unit z=s/sbar)')
# numerical: integrate s u' = Phi(u,s) - u from small z toward 0 along a solution, check (u-v0)/z
def Phi(u, z):
    ell = lam*(1-z)
    return k + (1/ell)*max((rho*u-b)/Calpha(a_), 0)**(1-a_)
z0 = 1e-3; u_start = v0 + (v0-k)/(1-aexp)*z0 + 5.0*z0**aexp     # arbitrary C
sol = solve_ivp(lambda z, u: [(Phi(u[0], z)-u[0])/z], [z0, 1e-7], [u_start], rtol=1e-12, atol=1e-15, method='LSODA')
zf, uf = sol.t[-1], sol.y[0, -1]
print(f'   integrated to z={zf:.1e}: (u-v0)/z = {(uf-v0)/zf:.6f}  (forced coeff {(v0-k)/(1-aexp):.6f}); claimed homogeneous mode (u-v0)/z^a = {(uf-v0)/zf**aexp:.3e}')
