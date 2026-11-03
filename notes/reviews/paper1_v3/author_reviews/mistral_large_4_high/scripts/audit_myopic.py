"""Check prop:myopic: myopic policy excess decays at least as t^{-1/alpha}. Simulate logistic share path
sdot = s*lam*(1-s/sbar)*sig*^a with sig = sig*(l(s), X) static optimum; R*(s(t)) - Rinf ~ t^{-1/a}."""
import numpy as np
from scipy.integrate import solve_ivp
a=0.3; X=1.0; k=0.0; m0=0.6; G=0.2; lam=1.2; sbar=0.5; s0=0.005
y=X-k; Ca=(1-a)*a**(a/(1-a))
def sig_star(s):
    l = lam*(1-s/sbar)
    return (a*l*y)**(1/(1-a))
def Rstar(s):
    l = lam*(1-s/sbar)
    return m0 + y*G + Ca*(l*y)**(1/(1-a))
Rinf = m0 + y*G
def rhs(t, z):
    s = z[0]
    sg = sig_star(s)
    D = lam*(1-s/sbar)*sg**a
    return [s*D]
sol = solve_ivp(rhs, (0, 60), [s0], rtol=1e-10, atol=1e-13, max_step=0.05, dense_output=True)
ts = np.linspace(0, 60, 1201)
s = sol.sol(ts)[0]
excess = np.array([Rstar(max(si,1e-12)) - Rinf for si in s])
mask = excess > 1e-9
# fit power law on large t
tt = ts[mask & (ts>10)]; ee = excess[mask & (ts>10)]
coef = np.polyfit(np.log(tt), np.log(ee), 1)
print('fitted decay exponent: %.3f (theory -1/alpha = %.3f)' % (coef[0], -1/a))
# also bound form: Ca [lam y]^{1/(1-a)} [h0^{-a/(1-a)} + a/(1-a) D0 s0/sbar t]^{-1/a}
h0 = 1 - s0/sbar
D0 = lam*sig_star(s0)**a
bound = Ca*(lam*y)**(1/(1-a)) * (h0**(-a/(1-a)) + (a/(1-a))*D0*(s0/sbar)*ts)**(-1/a)
print('max(excess - bound) over t:', np.max(excess - bound))
