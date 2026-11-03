"""GLM-F1: profile of the decision weight v'(s) in the worked example of Proposition 2.

Uses the author's own solver: smallest_root and solve_hjb are extracted verbatim (by AST) from
code/verify_theory.py and executed here, so nothing else in that script runs. Worked example of
sections/supp_model.tex:9: r=0.10, G=0.04, k=0, alpha=0.3, m0=0.35, v0=10, share cap 0.5.
v'(s) is computed two ways on the solver's grid: np.gradient(v, s) (as verify_theory.py check 15g
does) and Phi(u, s) = k + [((r-G)u - (m0-kG))/C_alpha]^(1-alpha) / ell(s), u = v/s (the ODE form, which
avoids differencing). Run from the repository root: python3 notes/reviews/.../f1_vprime.py
"""
import ast, sys
import numpy as np
from scipy.optimize import minimize_scalar

src = open('code/verify_theory.py').read()
tree = ast.parse(src)
ns = {'np': np, 'minimize_scalar': minimize_scalar}
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in ('smallest_root', 'solve_hjb'):
        exec(compile(ast.Module([node], []), 'verify_theory.py', 'exec'), ns)
smallest_root, solve_hjb = ns['smallest_root'], ns['solve_hjb']

r_, G_, k_, a_, m0_, sbar = 0.10, 0.04, 0.0, 0.3, 0.35, 0.5
Ca = (1 - a_) * a_ ** (a_ / (1 - a_))
lam = (((r_ - G_) * 10.0 - (m0_ - k_ * G_)) / Ca) ** (1 - a_) / (10.0 - k_)   # verify_theory.py lam_for(10)
v0, _ = smallest_root(m0_, k_, G_, r_, lam, a_)
ubar = (m0_ - k_ * G_) / (r_ - G_)
print(f"lambda = {lam:.6f}, v0 = {v0:.6f}, never-spend multiple (m0-kG)/(r-G) = {ubar:.4f}")

s, v, sig = solve_hjb(m0_, k_, G_, r_, lam, a_, sbar, N=4000)
vp_grad = np.gradient(v, s)
u = v / s
ell = lam * (1 - s / sbar)
with np.errstate(divide='ignore', invalid='ignore'):
    vp_phi = k_ + np.maximum((r_ - G_) * u - (m0_ - k_ * G_), 0.0) ** (1 - a_) / Ca ** (1 - a_) / ell
z = s / sbar
at = lambda arr, zz: float(np.interp(zz, z, arr))
print("share of cap   v'(gradient)  v'(Phi)   v/s")
for zz in [0.01, 0.10, 0.25, 0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.98, 0.99, 0.999]:
    print(f"  {zz:6.3f}      {at(vp_grad, zz):8.4f}   {at(vp_phi, zz):8.4f}  {at(u, zz):7.4f}")
mask = (z > 0.02) & (z < 0.9999)
i = np.argmin(np.where(mask, vp_phi, np.inf))
print(f"interior minimum of v'(Phi): {vp_phi[i]:.4f} at {z[i]:.3f} of the cap")
print(f"v'(Phi) at 0.9999 of the cap: {at(vp_phi, 0.9999):.4f}; gap to ubar {abs(at(vp_phi, 0.9999)-ubar)/ubar:.2%}")
gap = np.max((vp_phi - u)[mask])
print(f"max over (0.02, 0.9999) of v'(s) - v(s)/s: {gap:.4f} (negative = weight below revenue multiple)")
# acceptance tests proposed by the reviewer (A section 2.3, item 8)
t1 = at(vp_phi, 0.95) > at(vp_phi, 0.50)
t2 = abs(at(vp_phi, 0.99) - ubar) / ubar < 0.01
t3 = 0.02 < z[i] < 0.999 and vp_phi[i] < ubar
print(f"reviewer test (i) v'(0.95)>v'(0.50): {t1};  (ii) v'(0.99) within 1% of ubar: {t2};  (iii) interior argmin below ubar: {t3}")
# retention lever (Cor. 3(iii), Prop. 9(a)): gain per point of G_i is (X-k); at the firm's own weight X = v'(s)
print("retention gain per point of G_i at X = v'(s): "
      + ", ".join(f"{zz:.2f}: {at(vp_phi, zz)-k_:.2f}" for zz in [0.01, 0.10, 0.50, 0.80, 0.95, 0.999]))
# growth-engine gain x*sigma*(s) (Prop. 9(a)) vanishes at the cap
print("optimal spend sigma*(s): " + ", ".join(f"{zz:.2f}: {at(sig, zz):.4f}" for zz in [0.01, 0.10, 0.50, 0.80, 0.95, 0.999]))
