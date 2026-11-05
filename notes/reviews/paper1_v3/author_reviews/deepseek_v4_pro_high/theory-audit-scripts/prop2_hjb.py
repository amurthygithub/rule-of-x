"""
Independent verification of Proposition 2 (dynamic optimality): HJB, root equation (19),
ODE singularity (dPhi/du = (r-G)/Delta_o > 1), Gordon identity, and the no-root case (e).
Not the author's script.
"""
import numpy as np
from scipy.optimize import brentq

alpha = 0.3
beta = 1/alpha
Calpha = (1-alpha)*alpha**(alpha/(1-alpha))

def Delta_star(lam, y):
    return lam**(1/(1-alpha)) * (alpha*np.maximum(y,0))**(alpha/(1-alpha))

def sigma_star(lam, y):
    return (alpha*lam*np.maximum(y,0))**(1/(1-alpha))

def Pi_lam(lam, v, k):
    return Calpha*(lam*np.maximum(v-k,0))**(1/(1-alpha))

def H(v, lam, k, m0, G, r):
    return (r-G)*v - (m0-k*G) - Pi_lam(lam, v, k)

# --- Case with a root v0 ~ 10 (revenue multiple ~ 10, as in the worked example) ---
r, G, m0, k, lam = 0.10, 0.05, 0.30, 0.0, 0.06
print(f"r={r}, G={G}, m0={m0}, k={k}, lam={lam};  m0-kG={m0-k*G}, (m0-kG)/(r-G)={(m0-k*G)/(r-G)}")

vs = np.linspace(0, 30, 300001)
Hv = H(vs, lam, k, m0, G, r)
sgn = np.sign(Hv)
roots = [brentq(lambda v: H(v, lam, k, m0, G, r), vs[i], vs[i+1])
         for i in range(len(vs)-1) if sgn[i]*sgn[i+1] < 0]
print("Roots of (19):", [round(r_,4) for r_ in roots])
v0 = roots[0]

Delta_o = Delta_star(lam, v0)
sigma_o = sigma_star(lam, v0)
g_o = G + Delta_o
m_o = m0 - k*g_o - sigma_o
print(f"Delta_o={Delta_o:.4f}, g_o={g_o:.4f}, sigma_o={sigma_o:.4f}, m_o={m_o:.4f}")
print(f"Gordon identity v0 = m_o/(r-g_o): {v0:.6f} vs {m_o/(r-g_o):.6f}  (match: {abs(v0-m_o/(r-g_o))<1e-6})")
print(f"g_o < r ? {g_o < r}")
print(f"H'(v0) = (r-G) - Delta_o = {r-G - Delta_o:.4f} (>0 at smallest simple root)")

# --- ODE singularity at (s=0, u=v0): dPhi/du = (r-G)/Delta_o > 1 ---
# Phi(u,s) = k + ell(s)^-1 {[(r-G)u - (m0-kG)]/Calpha}^(1-alpha);  ell(s)=lam*(1-s/sbar), sbar=1
def Phi_u(u, s):
    ell = lam*(1 - s)
    return k + (1/ell)*(((r-G)*u - (m0-k*G))/Calpha)**(1-alpha)

eps = 1e-5
dPhi_du = (Phi_u(v0+eps, 0.0) - Phi_u(v0-eps, 0.0))/(2*eps)
print(f"\nPhi(v0,0) = {Phi_u(v0,0.0):.6f}  (should equal v0={v0:.6f})")
print(f"dPhi/du at (0,v0) = {dPhi_du:.4f}  (expect (r-G)/Delta_o = {(r-G)/Delta_o:.4f} > 1)")
print(f"=> u - v0 ~ s^((r-G)/Delta_o - 1) = s^{((r-G)/Delta_o - 1):.4f} : boundary condition does NOT select a unique solution")

# --- Identity H(v) = (r-g(v))v - m(v) ---
for v_test in [2.0, v0]:
    gv = G + Delta_star(lam, v_test)
    mv = m0 - k*gv - sigma_star(lam, v_test)
    print(f"v={v_test}: H={H(v_test,lam,k,m0,G,r):.6f} vs (r-g)v-m={((r-gv)*v_test-mv):.6f}")

# --- Part (e): no positive root -> v(s)/s -> infinity ---
print("\n--- Part (e): no positive root (value diverges at small share) ---")
for lam_test in [0.06, 0.3, 1.2, 3.0]:
    vs2 = np.linspace(0, 500, 500001)
    Hv2 = H(vs2, lam_test, k, m0, G, r)
    has_root = np.any(np.diff(np.sign(Hv2)) != 0)
    # v1 with Delta*(lam,v1)=r-G:  lam^(1/(1-a)) (a(v1-k))^(a/(1-a)) = r-G
    v1 = k + (r-G)**((1-alpha)/alpha) / (alpha * lam_test**(1/alpha))
    g_v1 = G + Delta_star(lam_test, v1)
    m_v1 = m0 - k*g_v1 - sigma_star(lam_test, v1)
    # Gordon multiple blows up as v -> v1 from below; take v = v1 - eps
    v_close = v1 - 1e-6 if v1 > k + 1e-4 else v1
    gv = G + Delta_star(lam_test, v_close)
    mv = m0 - k*gv - sigma_star(lam_test, v_close)
    gordon = mv/(r - gv) if gv < r else np.inf
    verdict = 'm(v1)<0 => root exists' if m_v1 < 0 else 'm(v1)>0 => no root, v/s->inf'
    print(f"  lam={lam_test:>4}: any positive root? {has_root},  m(v1)={m_v1:.5f} ({verdict}),  "
          f"Gordon mult near v1 = {gordon:.3f}")
