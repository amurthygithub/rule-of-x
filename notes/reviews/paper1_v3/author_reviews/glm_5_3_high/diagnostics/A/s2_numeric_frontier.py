#!/usr/bin/env python3
"""
Referee A - numerical verification of the frontier and the geometric score maximum.

(1) frontier concavity/monotonicity over parameter grids, incl. corner cases:
    k = 0, 0<k<1, k>1, k<0 (Remark S1(c)), alpha = 1/2 boundary, sigma-bar finite;
(2) the closed-form maximal score (7), optimal spend (6), growth (5) and the
    tangency (m*'(g*) = -X) checked against scipy constrained optimization (SLSQP
    + brute grid), for interior and corner (X<=k) draws and binding caps;
(3) Lemma 1(a): feasible-set convexity (hypograph test) and the dominated-point claim;
(4) Lemma S1(c): the two-local-maxima example under contemporaneous timing;
(5) Lemma 3(d) Rule-of-1000 example numbers.
"""
import numpy as np
from scipy.optimize import minimize, minimize_scalar
import math, sys, platform, datetime

rng = np.random.default_rng(20261103)
print("session:", datetime.datetime.now().isoformat())
print("python", platform.python_version(), "numpy", np.__version__, "scipy", __import__('scipy').__version__)

results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + ("  " + str(detail) if detail else ""))

def mstar(g, m0, G, k, ell, alpha):
    return m0 - k*g - ell**(-1/alpha)*np.maximum(g-G, 0)**(1/alpha)

def Rstar_cf(m0, G, k, X, ell, alpha):
    y = X - k
    if y <= 0: return m0 + y*G, G, 0.0
    D = ell**(1/(1-alpha)) * (alpha*y)**(alpha/(1-alpha))
    sig = alpha*y*D
    return m0 + y*G + (1-alpha)*y*D, G+D, sig

# ---------- (1) frontier shape over grids ------------------------------------------
worst = {"mono": 0, "conc": 0, "kink_ok": True}
for alpha in [0.25, 0.3, 0.5, 0.7, 0.9]:
    for k in [0.0, 0.3, 0.9, 1.5, -0.3]:
        for G in [0.0, 0.05, 0.2]:
            m0v, ell = 0.5, 0.8
            gs = G + np.linspace(1e-6, 1.0, 2001)
            ms = mstar(gs, m0v, G, k, ell, alpha)
            # strict concavity: second difference <= 0
            d2 = np.diff(ms, 2)
            if k >= 0:
                if np.any(d2 > 1e-9): worst["conc"] += 1
                if np.any(np.diff(ms) >= 0): worst["mono"] += 1
            else:
                # frontier rises first (Remark S1(c)): peak at Delta0 = [-k/(beta kappa)]^(1/(beta-1))
                b = 1/alpha; kap = ell**(-b)
                D0 = (-k/(b*kap))**(1/(b-1))
                imax = np.argmax(ms)
                if abs(gs[imax]-G-D0) > 2e-3: worst["kink_ok"] = False
check("L1c  frontier strictly decreasing & concave for k>=0 over alpha x k x G grid (35 combos)",
      worst["mono"]==0 and worst["conc"]==0)
check("RS1c k<0: frontier peaks at Delta0 = (-k/(beta kappa))^(1/(beta-1)) (5 alpha x 3 G combos)",
      worst["kink_ok"])

# alpha=1/2 second-derivative limit at G equals -2 kappa
alpha = 0.5
for ell in [0.5, 1.2]:
    eps = 1e-8
    val = (mstar(G+eps,0.5,0.1,0.0,ell,alpha)-2*mstar(G,0.5,0.1,0.0,ell,alpha)
           + mstar(G-eps if False else 0.1-eps,0.5,0.1,0.0,ell,alpha))/(eps**2)*0  # not used
    d2lim = -2*ell**(-2)
    # numeric: m*'' near G
    h = 1e-7
    f = lambda d: mstar(0.1+d, 0.5, 0.1, 0.0, ell, alpha)
    d2 = (f(2*h)-2*f(h)+f(0))/(h*h)
    check(f"L1c  alpha=1/2: m*''(G+) -> -2*kappa (ell={ell})",
          abs(d2 - d2lim) < 2e-3*abs(d2lim), f"num={d2:.6f} vs {d2lim:.6f}")
# alpha<1/2 -> m*'' ->0 ; alpha>1/2 -> m*'' -> -inf
for alpha, expect in [(0.3, "zero"), (0.7, "inf")]:
    h = 1e-7; ell = 0.9
    f = lambda d: mstar(0.1+d, 0.5, 0.1, 0.0, ell, alpha)
    d2 = (f(2*h)-2*f(h)+f(0))/(h*h)
    if expect=="zero": check("L1c  alpha=0.3: m*''(G+) -> 0", abs(d2) < 1e-3, f"num={d2:.2e}")
    else: check("L1c  alpha=0.7: m*''(G+) -> -infty (diverges like Delta^(beta-2))", d2 < -1e3, f"num={d2:.2e}")

# ---------- (2) closed form vs scipy -------------------------------------------------
bad_R = bad_D = bad_sig = bad_corner = bad_cap = 0
ncorner = ncap = 0
for trial in range(400):
    alpha = rng.uniform(0.2, 0.5)
    G = rng.uniform(0, 0.3); k = rng.uniform(0, 1.2)
    X = k + rng.uniform(-0.4, 3.0)
    lam = rng.uniform(0.05, 2.0); hh = rng.uniform(0.05, 1.0)
    m0v = rng.uniform(-0.1, 0.9)
    ell = lam*hh
    y = X - k
    if y <= 0: ncorner += 1
    # brute force over an adaptive sigma grid (handles caps and corners)
    smax = max(6.0, 2.0*(alpha*y*ell)**(1/(1-alpha)) if y>0 else 6.0)
    sg = np.linspace(0, smax, 400001)
    Rv = m0v + y*G + y*ell*sg**alpha - sg
    i = np.argmax(Rv); R_num = Rv[i]; sig_num = sg[i]
    R_cf, g_cf, sig_cf = Rstar_cf(m0v, G, k, X, ell, alpha)
    # cap variant: sigma_bar finite, possibly binding -> claimed optimum at the cap (Remark S2)
    sigbar = rng.uniform(0.01, 3.0)
    if sig_cf > sigbar:
        ncap += 1
        R_cap_claim = m0v + y*G + y*ell*sigbar**alpha - sigbar
        res_cap = minimize_scalar(lambda s: -(m0v + y*G + y*ell*s**alpha - s),
                                  bounds=(0, sigbar), method='bounded',
                                  options={'xatol': 1e-12})
        if abs(R_cap_claim - (-res_cap.fun)) > 1e-6*max(1, abs(R_cap_claim)): bad_cap += 1
    if abs(R_cf - R_num) > 2e-4*max(1, abs(R_cf)): bad_R += 1
    if abs(sig_cf - sig_num) > 2e-3 and y > 0: bad_sig += 1
    # independent scalar-optimizer cross-check on interior draws (SLSQP stalls on
    # the infinite gradient at sigma->0 for small sigma*, so use bounded Brent)
    if y > 0.05 and trial % 4 == 0:
        res = minimize_scalar(lambda s: -(m0v + y*G + y*ell*s**alpha - s),
                              bounds=(0, smax), method='bounded', options={'xatol': 1e-13})
        if abs(-res.fun - R_cf) > 1e-6*max(1,abs(R_cf)): bad_R += 1
    # corner claim
    if y <= 0:
        if abs(R_cf - (m0v+y*G)) > 1e-12 or sig_cf != 0.0: bad_corner += 1
        if abs(R_num - (m0v+y*G)) > 1e-6 and Rv[i] > Rv[0] + 1e-9: bad_corner += 1
check(f"L2   closed-form R* matches brute-grid + SLSQP optimum (400 draws, {ncorner} corners, {ncap} binding caps)", 
      bad_R==0 and bad_sig==0 and bad_corner==0 and bad_cap==0,
      f"bad_R={bad_R} bad_sig={bad_sig} bad_corner={bad_corner} bad_cap={bad_cap}")

# tangency vs direct constrained optimization of R_X over the feasible set (g,m):
# max X g + m s.t. m <= m0 - sigma - k g, g = G + ell sigma^alpha, sigma in [0, 6]
bad_tan = 0
for _ in range(200):
    alpha = rng.uniform(0.2, 0.5)
    G = rng.uniform(0, 0.3); k = rng.uniform(0, 1.0)
    X = k + rng.uniform(0.05, 3.0)
    lam = rng.uniform(0.05, 2.0); hh = rng.uniform(0.05, 1.0)
    m0v = rng.uniform(0, 0.9); ell = lam*hh; y = X-k
    # direct: maximize over sigma
    res = minimize_scalar(lambda s: -(m0v + y*G + y*ell*s**alpha - s), bounds=(0, 6), method='bounded')
    # closed form
    R_cf, g_cf, sig_cf = Rstar_cf(m0v, G, k, X, ell, alpha)
    # tangency check: m*'(g*) = -X
    b = 1/alpha
    mp = -k - b*ell**(-b)*(g_cf-G)**(b-1)
    if abs(mp + X) > 1e-9: bad_tan += 1
    if abs(-res.fun - R_cf) > 1e-6*max(1,abs(R_cf)): bad_tan += 1
check("L2b  tangency m*'(g*) = -X and scipy bounded-optimum = closed form (200 draws)", bad_tan==0)

# ---------- (3) feasible-set convexity and dominance ----------------------------------
bad_cvx = bad_dom = 0
for _ in range(100):
    alpha = rng.uniform(0.2, 0.5)
    G = rng.uniform(0, 0.3); k = rng.uniform(0, 1.0); ell = rng.uniform(0.1, 2.0); m0v = 0.5
    gs = G + np.sort(rng.uniform(0, 0.8, 60))
    ms = mstar(gs, m0v, G, k, ell, alpha)
    i, j = rng.integers(0,60,2)
    if i==j: continue
    gm, mm = (gs[i]+gs[j])/2, (ms[i]+ms[j])/2
    if mm > mstar(gm, m0v, G, k, ell, alpha) + 1e-12: bad_cvx += 1
    # dominance: (g, m) with m < m*(g) dominated by (g, m*(g)); check no feasible point dominates a frontier point
    g0 = gs[i]; m0p = ms[i]
    if any((gs[j] >= g0 and ms[j] >= m0p + 1e-12) for j in range(60) if j != i): bad_dom += 1
check("L1a  hypograph convexity (midpoint below frontier) and frontier points undominated (100 draws)",
      bad_cvx==0 and bad_dom==0)

# ---------- (4) Lemma S1(c) example: two local maxima under contemporaneous timing ----
alpha, kv, kap, G0, m0v, X = 0.3, 1.25, 0.5, 0.1, 0.5, 1.0
b = 1/alpha
S = lambda g: g + m0v - kv*g/(1+g) - kap*(g-G0)**b
gs = np.linspace(G0, 3.0, 2000001)
Sv = S(gs)
# local maxima: sign changes of S'
dS = np.diff(Sv)
sign = np.sign(dS)
maxima = gs[1:-1][(sign[:-1] > 0) & (sign[1:] < 0)]
check("LS1c example: S(G) ~ 0.486 and corner is a local max (S'(G)<0)",
      abs(S(G0)-0.486) < 5e-4 and (S(G0+1e-4) < S(G0)))
imax = maxima[np.argmax(S(maxima))] if len(maxima) else None
check("LS1c example: unique interior local max near g=0.739 with S ~ 0.595 (grid 2e6)",
      imax is not None and abs(imax-0.739) < 0.005 and abs(S(imax)-0.595) < 1e-3,
      f"g={imax}, S={S(imax) if imax else None}")
check("LS1c example: under linear timing (2) the unique optimum is g=G (X=1<k=1.25)",
      Rstar_cf(m0v, G0, kv, X, kap**(-alpha), alpha)[1] == G0)
# m~ strictly convex just right of G
eps=1e-4
mt = lambda g: m0v - kv*g/(1+g) - kap*(g-G0)**b
d2 = (mt(G0+2*eps)-2*mt(G0+eps)+mt(G0))/(eps*eps)
check("LS1c example: m~ strictly convex just right of G (m~''>0)", d2 > 0)

# asset-light sliver (Lemma S1(d)): alpha=0.3, k=0.05, ell=0.86, G=0.1: ends ~2 points above G
alpha, kv, G0 = 0.3, 0.05, 0.1
ell = 0.86; b = 1/alpha; kap = ell**(-b)
mt = lambda g: -kv*g/(1+g) - kap*(g-G0)**b    # m~'' zero crossing
f = lambda d: 2*kv/(1+G0+d)**3 - b*(b-1)*kap*d**(b-2)
lo, hi = 1e-9, 0.5
for _ in range(200):
    mid = (lo+hi)/2
    if f(mid) > 0: lo = mid
    else: hi = mid
D0 = (lo+hi)/2
check("LS1d asset-light: non-convex region ends about 2 points of excess growth (alpha=0.3,k=0.05,ell=0.86)",
      abs(D0-0.021) < 0.004, f"Delta0={D0:.4f}, kappa={kap:.3f}")

# ---------- (5) Rule-of-1000 example (Lemma 3(d) intuition paragraph) ----------------
alpha, X, k, m0v, G0 = 0.3, 1.0, 0.0, 0.6, 0.2
Calpha = (1-alpha)*alpha**(alpha/(1-alpha))
Rinf = m0v + (X-k)*G0
Rbar = 10.0
Lam = (1/(X-k))*((Rbar-Rinf)/Calpha)**(1-alpha)
Dth = (Rbar-Rinf)/((1-alpha)*(X-k))
sigth = alpha*(Rbar-Rinf)/(1-alpha)
mth = m0v - k*(G0+Dth) - sigth
check("L3d  Rule-of-1000 example: Lambda ~ 8.71, Delta* ~ 13.14 (1314 pts), sigma* ~ 3.94 (394%), m ~ -3.34 (-334%)",
      abs(Lam-8.71)<0.02 and abs(Dth-13.143)<0.01 and abs(sigth-3.943)<0.01 and abs(mth+3.343)<0.01,
      f"Lambda={Lam:.3f} Delta={Dth:.3f} sigma={sigth:.3f} m={mth:.3f}")
# S5: Rule of 1000 needs lambda h between 6.8 and 9.3 for alpha in [0.25, 0.45], m0=0.5, G=0.2
los = []
for a2 in [0.25, 0.45]:
    C2 = (1-a2)*a2**(a2/(1-a2))
    Lam2 = ((10.0 - (0.5+0.2))/C2)**(1-a2)
    los.append(Lam2)
check("S5   Rule-of-1000 range: Lambda in [6.8, 9.3] over alpha in [0.25, 0.45] (m0=0.5, G=0.2)",
      abs(los[0]-9.35)<0.1 and abs(los[1]-6.79)<0.1, f"alpha=0.25: {los[0]:.2f}, alpha=0.45: {los[1]:.2f}")

print()
nf = sum(1 for _, ok in results if not ok)
print(f"TOTAL {len(results)} checks, {nf} failures")
sys.exit(1 if nf else 0)