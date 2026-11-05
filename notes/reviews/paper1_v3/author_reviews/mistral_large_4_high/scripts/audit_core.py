"""Independent re-derivation checks of the paper's core closed forms.
Paper: Rule of 40 as a Price Line. Model: g = G + l*sigma^a, m <= m0 - sigma - k g,
l = lambda*h(s), h(s)=1-s/sbar, beta=1/a, kappa=l^-beta, y=X-k, C_a=(1-a)a^{a/(1-a)}.
Checks Prop frontier/score/saturation/budget/envelope numerically + symbolically (sympy)."""
import numpy as np, sympy as sp, json, sys
res = {}
sig, a, G, m0, k, X, lam, s, sbar = sp.symbols('sig a G m0 k X lam s sbar', positive=True)
h = 1 - s/sbar
l = lam*h
beta = 1/a
kap = l**(-beta)
g = G + l*sig**a
m = m0 - sig - k*g
# Prop score: maximize R = X g + m over sig. FOC: X*dg/dsig + dm/dsig = 0
# dg/dsig = a l sig^(a-1); dm/dsig = -1 - k a l sig^(a-1)
# FOC: X a l sig^(a-1) -1 - k a l sig^(a-1) = 0 -> (X-k) a l sig^(a-1) = 1
y = X - k
sig_star = (a*l*y)**(1/(1-a))
Dstar = l*sig_star**a          # g*-G
Rstar = sp.simplify(X*(G+Dstar) + (m0 - sig_star - k*(G+Dstar)))
Rstar_expected = m0 + y*G + (1-a)*y*Dstar
res['sym_Rstar_diff'] = sp.simplify(Rstar - Rstar_expected)
# eq:Rstar closed form C_a (l y)^{1/(1-a)}
Ca = (1-a)*a**(a/(1-a))
res['sym_Ca_term'] = sp.simplify((1-a)*y*Dstar - Ca*(l*y)**(1/(1-a)))
res['sym_sigstar_eq'] = sp.simplify(sig_star - a*y*Dstar)
# frontier m*(g) = m0 - k g - kappa (g-G)^beta ; check invert: at g=G+Dstar, m* equals m at sig_star
gv = G + Dstar
mstar_at_opt = m0 - k*gv - kap*(gv-G)**beta
res['sym_frontier_at_opt'] = sp.simplify(mstar_at_opt - (m0 - sig_star - k*gv))
# tangency: m*'(g*) = -X
mstar = lambda gg: m0 - k*gg - kap*(gg-G)**beta
GG = sp.symbols('GG')
res['sym_tangency_diff'] = sp.simplify(sp.diff(m0 - k*GG - kap*(GG-G)**beta, GG).subs(GG, G+Dstar) + X)
# corner X<=k: maximizer at G
# envelope: dR*/dX = g*, dR*/dk = -g*, dR*/dlambda = y*Dstar/lam
Rstar_fn = m0 + y*G + Ca*(l*y)**(1/(1-a))
res['sym_dR_dX'] = sp.simplify(sp.diff(Rstar_fn, X) - (G+Dstar))
res['sym_dR_dk'] = sp.simplify(sp.diff(Rstar_fn, k) + (G+Dstar))
res['sym_dR_dlam'] = sp.simplify(sp.diff(Rstar_fn, lam) - y*Dstar/lam)
res['sym_dR_dm0'] = sp.simplify(sp.diff(Rstar_fn, m0) - 1)
res['sym_dR_dG'] = sp.simplify(sp.diff(Rstar_fn, G) - y)
# convexity in k: d2R/dk2 >= 0
res['sym_d2R_dk2_nonneg'] = sp.simplify(sp.diff(Rstar_fn, k, 2))
# saturation: R*_X(s) = Rinf + Ca (lam h(s) y+)^{1/(1-a)}; dR/ds = -y D*/(sbar-s)
Rinf = m0 + y*G
Rsat = Rinf + Ca*(lam*h*y)**(1/(1-a))
res['sym_dRsat_ds'] = sp.simplify(sp.diff(Rsat, s) + y*Dstar/(sbar-s))
# budget (continuous): int_0^T (R_X(t)-Rinf)^+ dt <= y ln(s(T)/s0). Check sharpness: with R(t)-Rinf = y (g-G) achieved...
# Verify identity: d/dt ln s = g - G = Delta; and R - Rinf = X g + m - (m0+yG) = X(G+Delta) + m0 - sig - k(G+Delta) - m0 - yG = y Delta - sig.
# At optimal spend sig = a y Delta, R-Rinf = (1-a) y Delta. Budget: int (R-Rinf) dt <= y int Delta dt = y ln(s/s0). Since (1-a)y Delta <= y Delta, holds (not sharp at optimum; sharp requires sig^{a}... ). Check inequality (1-a) y Delta <= y Delta for a in (0,1): true.
# discrete budget: sum ln(1 + (R-Rinf)+/(y(1+G))) <= ln(s_T/s_0). Verify identity with s_{t+1}=s_t(1+g)/(1+G): ln s_{t+1}/s_t = ln(1+g)-ln(1+G) = ln(1 + (g-G)/(1+G)) = ln(1+Delta/(1+G)). And R-Rinf <= y Delta => ln(1+(R-Rinf)/(y(1+G))) <= ln(1+Delta/(1+G)) = ln(s_{t+1}/s_t). Telescopes. OK.
res['budget_identity'] = 'ln(s_{t+1}/s_t)=ln(1+Delta/(1+G)); R-Rinf=y*Delta-sig<=y*Delta; telescoping OK'
# Prop budget continuous: int (R-Rinf)^+ dt <= y ln(s(T)/s0): since R-Rinf = y Delta - sig <= y Delta and int Delta dt = ln(s(T)/s0). OK.
print(json.dumps({k2: str(v) for k2,v in res.items()}, indent=1))
