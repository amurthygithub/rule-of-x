"""
Independent re-derivation of Lemma 1 and Lemma 2 (Rule-of-X frontier and max score).
Symbolic with sympy.  NOT using the author's verify_theory.py.
"""
import sympy as sp

# Symbols
m0, k, X = sp.symbols('m0 k X', real=True)
lam, s, sbar = sp.symbols('lambda s sbar', positive=True)
alpha = sp.symbols('alpha', positive=True)
G = sp.symbols('G', real=True)
Delta = sp.symbols('Delta', positive=True)  # excess growth g - G

beta = 1/alpha
h = 1 - s/sbar
ell = lam * h                     # effective growth opportunity
kappa = ell**(-beta)              # = (lam h)^(-1/alpha)
y = X - k

# --- Lemma 1 frontier m*(g) = m0 - k g - kappa (g-G)^beta ---
g = G + Delta
mstar = m0 - k*g - kappa*(g-G)**beta
mstar_simplified = m0 - k*g - kappa*Delta**beta

# slope and curvature
dmg = sp.diff(mstar_simplified, Delta)      # dm*/dDelta = dm*/dg
ddmg = sp.diff(dmg, Delta)

print("m*(g) =", sp.simplify(mstar_simplified))
print("dm*/dg =", sp.simplify(dmg), "  (expect -k - beta*kappa*Delta^(beta-1))")
print("d2m*/dg2 =", sp.simplify(ddmg), "  (expect -beta*(beta-1)*kappa*Delta^(beta-2))")

# --- Lemma 2: score along frontier, maximize over Delta ---
S = y*Delta - kappa*Delta**beta       # R_X - m0 - yG
dS = sp.diff(S, Delta)
d2S = sp.diff(dS, Delta)
print("\nS(Delta) = y*Delta - kappa*Delta^beta")
print("S'(Delta) =", sp.simplify(dS))
print("S''(Delta) =", sp.simplify(d2S), " (expect <0 for y>0 => strictly concave)")

# FOC: beta*kappa*Delta^(beta-1) = y
Delta_star = (y/(beta*kappa))**(1/(beta-1))
# simplify using kappa = ell^-beta, beta=1/alpha
Delta_star_simp = sp.simplify(sp.powsimp(Delta_star, force=True))
print("\nDelta* (FOC) raw =", Delta_star)
# manual target: ell^(1/(1-alpha)) * (alpha*(X-k))^(alpha/(1-alpha))
target_Delta = ell**(1/(1-alpha)) * (alpha*y)**(alpha/(1-alpha))

# sigma* = alpha y Delta*
sigma_star = alpha*y*Delta_star
# also (alpha*ell*y)^(1/(1-alpha))
sigma_star_target = (alpha*ell*y)**(1/(1-alpha))

# R* = m0 + y G + (1-alpha) y Delta*
Rstar_plus_surplus = (1-alpha)*y*Delta_star
Rstar = m0 + y*G + Rstar_plus_surplus

# second form: m0 + yG + C_alpha (ell y)^(1/(1-alpha))
Calpha = (1-alpha)*alpha**(alpha/(1-alpha))
Rstar_2 = m0 + y*G + Calpha*(ell*y)**(1/(1-alpha))

print("\n--- Numerical check with concrete numbers (m0=.45,G=.10,k=.10,alpha=.3,lam*h=.6, X=1 and X=2) ---")
vals = {m0: 0.45, G: 0.10, k: 0.10, alpha: sp.Rational(3,10), lam: 0.6, s: sp.Rational(1,100), sbar: 0.5, X: 1.0}
# override ell with lam*h at s -> h = 1 - s/sbar
ell_val = 0.6*(1 - 0.01/0.5)
print("ell =", ell_val)

def num(expr):
    return float(expr.subs({m0:0.45, G:0.10, k:0.10, alpha:0.3, y:1.0-0.10, ell:ell_val}))

# compute Delta*, sigma*, R* numerically for X=1 and X=2
for Xv in (1.0, 2.0):
    yv = Xv - 0.10
    D = ell_val**(1/(1-0.3)) * (0.3*yv)**(0.3/(1-0.3))
    sg = 0.3*yv*D
    R = 0.45 + yv*0.10 + (1-0.3)*yv*D
    gv = 0.10 + D
    m_at = 0.45 - 0.10*gv - sg
    print(f"X={Xv}: Delta*={D:.4f}, g*={gv:.4f}, sigma*={sg:.4f}, R*={R:.4f}, m(g*)={m_at:.4f}")
    # tangency check: m*'(g*) should be -X
    slope = -0.10 - beta.subs(alpha,0.3)*(ell_val**(-beta.subs(alpha,0.3)))*(D**(beta.subs(alpha,0.3)-1))
    print(f"   dm*/dg at g* = {slope:.4f} (expect {-Xv})")

print("\n--- Duality X(g) = -m*'(g) = k + beta*kappa (g-G)^(beta-1) ---")
Xg = k + beta*kappa*(Delta)**(beta-1)
print("X(g) =", sp.simplify(Xg))
