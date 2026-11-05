"""Independent reproduction of GPT-M1 (cone slope vs common-frontier slope). Own code; no reviewer code reused."""
import numpy as np
from scipy import optimize, integrate

alpha = 0.3; beta = 1/alpha; m0 = 0.8; ell = 0.721826999314566; W = 0.6; chi = 0.9
p = 14.833990914027952
grid = np.round(np.arange(0, 0.6001, 0.05), 10)
mstar = lambda g: m0 - (np.maximum(g, 0)/ell)**beta
dmstar = lambda g: -beta*np.maximum(g, 0)**(beta-1)/ell**beta

def ls_slope(x, y):
    x = np.asarray(x); y = np.asarray(y)
    return float(((x-x.mean())*(y-y.mean())).sum()/((x-x.mean())**2).sum())

# 1. the constructed choices: weight X(g) = -m*'(g); check each g is the unique optimum of X g + m over spend sigma in [0,1]
gs = np.linspace(0.006, 0.6, 100)
maxdisc = 0; maxspend = 0
for g in gs:
    X = -dmstar(g)
    f = lambda s: -(X*ell*s**alpha + m0 - s)        # k=0, G=0: g = ell*s^alpha, m = m0 - s
    r = optimize.minimize_scalar(f, bounds=(0, 1), method='bounded', options=dict(xatol=1e-14))
    s_star = (g/ell)**beta
    maxdisc = max(maxdisc, abs(r.x - s_star)); maxspend = max(maxspend, s_star)
print('optimality: max |argmax spend - implied spend| =', maxdisc, '; max spend =', maxspend, '; max weight X(W)=', -dmstar(W), '; margin at W =', mstar(W))

# 2. exact population cone: Psi(g0) = m*(q(g0)), q = F^{-1}(1-chi+chi F(g0))
def cone_slope(Finv, F):
    q = np.array([Finv(1-chi+chi*F(g)) for g in grid])
    return ls_slope(grid, mstar(q)), q
F = lambda g: (g/W)**p; Finv = lambda u: W*u**(1/p)
cs, q = cone_slope(Finv, F)
print('cone LS slope (reviewer F):', cs)
print('frontier own LS slope on grid:', ls_slope(grid, mstar(grid)), '; steepest frontier slope at W:', dmstar(W))
mult = (beta+1)*(beta+2)/6
Sb = ls_slope(grid, grid**beta)
print('paper approx multiplier (b+1)(b+2)/6 =', mult, '-> implied steepest slope', mult*cs, ' ratio true/implied', dmstar(W)/(mult*cs))
print('paper exact-LS mapping: ell_hat=(S_b/b)^alpha =', (Sb/abs(cs))**alpha, ' steepest=beta W^(b-1) b/S_b =', beta*W**(beta-1)*abs(cs)/Sb)
# Monte Carlo with a dense sample: does sampling density remove the gap?
rng = np.random.default_rng(1)
for n in [10**3, 10**4, 10**5, 10**6]:
    g_s = Finv(rng.uniform(size=n)); m_s = mstar(g_s)
    keep = [g0 for g0 in grid if (g_s >= g0).sum() >= 30]
    psi = [np.quantile(m_s[g_s >= g0], chi) for g0 in keep]
    qpop = [Finv(1-chi+chi*F(g0)) for g0 in keep]
    print(f'  sampled n={n}: {len(keep)} grid pts with >=30 obs; cone LS slope = {ls_slope(keep, psi):.4f} (population on same pts {ls_slope(keep, mstar(np.array(qpop))):.4f})')

# 3. other growth distributions on [0,W] with the SAME frontier
print('\nsame frontier (steepest slope 3, own LS slope %.4f), other growth laws:' % ls_slope(grid, mstar(grid)))
cs_u, _ = cone_slope(lambda u: W*u, lambda g: g/W)
print('  uniform on [0,.6]: cone slope %.4f ; paper-implied steepest %.3f (true 3)' % (cs_u, mult*abs(cs_u)))
for lam in [3, 6, 10]:
    Fe = lambda g, l=lam: (1-np.exp(-l*g))/(1-np.exp(-l*W)); Fei = lambda u, l=lam: -np.log(1-u*(1-np.exp(-l*W)))/l
    c, _ = cone_slope(Fei, Fe)
    print('  truncated exponential rate %d (right-skewed): cone slope %.4f ; paper-implied steepest %.3f (true 3)' % (lam, c, mult*abs(c)))
# 4. chi -> 1 recovers the frontier's LS slope
for c in [0.9, 0.99, 0.999]:
    qq = [W*(1-c+c*(g/W)**p)**(1/p) for g in grid]
    print('  reviewer F, chi=%.3f: cone slope %.4f' % (c, ls_slope(grid, mstar(np.array(qq)))))
