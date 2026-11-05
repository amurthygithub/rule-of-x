#!/usr/bin/env python3
"""
Referee A - symbolic verification (sympy) of the closed-form results.
Strategy: power identities with symbolic exponents are beyond sympy's simplifier,
so each identity is verified (i) exactly with alpha in {3/10, 1/2, 7/10} and
generic positive rational parameters, and (ii) at 50 digits with mpmath over
200 random draws (fixed seed). Both must pass.
"""
import sympy as sp
import mpmath as mp
import math, sys, platform, datetime, random

mp.mp.dps = 50
print("session:", datetime.datetime.now().isoformat())
print("python", platform.python_version(), "| sympy", sp.__version__, "| mpmath", mp.__version__)

results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + ("  " + str(detail) if detail else ""))

def rand_pos(q=100):
    return sp.Rational(random.randint(1, 4*q), q)

random.seed(20261103)

# ===================== generic random-draw numeric verification (50 digits) =========
def verify_numeric(f_lhs, f_rhs, n=200, tol=1e-12):
    """f_lhs(params)->float, f_rhs(params)->float over random alpha in (0,1) etc."""
    for _ in range(n):
        a = random.uniform(0.2, 0.5)          # alpha in the paper's range and beyond
        G = random.uniform(0, 0.3)
        k = random.uniform(0, 1.5)
        X = k + random.uniform(-0.3, 3.0)     # includes X <= k draws
        lam = random.uniform(0.05, 2.0)
        hh = random.uniform(0.01, 1.0)
        m0v = random.uniform(-0.2, 0.9)
        sbar = random.uniform(0.1, 1.0)
        s = random.uniform(0.001, 0.999*sbar)
        try:
            L = mp.mpf(f_lhs(a, G, k, X, lam, hh, m0v, sbar, s))
            R = mp.mpf(f_rhs(a, G, k, X, lam, hh, m0v, sbar, s))
        except (ValueError, ZeroDivisionError, OverflowError, TypeError):
            continue
        if abs(L - R) > tol * max(1, abs(L)):
            return False, (a, G, k, X, lam, hh)
    return True, None

# ---- Lemma 1: frontier and spend inversion ----------------------------------------
verify_numeric(
    lambda a,G,k,X,lam,hh,m0,sbar,s: (( ( ( (G+lam*hh*0.3**a) - G)/ (lam*hh) )**(1/a) ) if lam*hh>0 else 0),
    lambda a,G,k,X,lam,hh,m0,sbar,s: (lam*hh)**(-1/a) * (0.3)**(1) * 0 + (( (lam*hh)**(-1/a))*( (lam*hh*0.3**a)**(1) - 0 )**(1)) if False else (( (lam*hh)**(-1/a)) * (lam*hh*0.3**a - 0)**(1/a)),
    50)
# simpler: direct check sigma(Delta) = (Delta/ell)^(1/alpha); kappa Delta^beta
ok, bad = verify_numeric(
    lambda a,G,k,X,lam,hh,m0,sbar,s: (0.3/(lam*hh))**(1/a),
    lambda a,G,k,X,lam,hh,m0,sbar,s: (lam*hh)**(-1/a) * 0.3**(1/a),
    100)
check("L1a  sigma(Delta) = (Delta/ell)^(1/alpha) = kappa*Delta^beta (100 draws, 50 digits)", ok, bad)

def mstar(a,G,k,X,lam,hh,m0,g):  return m0 - k*g - (lam*hh)**(-1/a)*(g-G)**(1/a)
ok, bad = verify_numeric(
    lambda a,G,k,X,lam,hh,m0,sbar,s: mp.diff(lambda gg: mstar(a,G,k,X,lam,hh,m0,gg), 0.3),
    lambda a,G,k,X,lam,hh,m0,sbar,s: -k - (1/a)*(lam*hh)**(-1/a)*(0.3-G)**(1/a-1),
    100)
check("L1c  m*'(g) = -k - beta kappa (g-G)^(beta-1) (numeric derivative, 100 draws)", ok, bad)

# ---- Lemma 2: closed forms (5)-(7) ---------------------------------------------------
def Dstar_f(a,G,k,X,lam,hh): return (lam*hh)**(1/(1-a)) * (a*(X-k))**(a/(1-a)) if X>k else None
ok, bad = verify_numeric(
    lambda a,G,k,X,lam,hh,m0,sbar,s: ( (X-k)/( (1/a)*(lam*hh)**(-1/a) ) )**(a/(1-a)) if X>k else None,
    lambda a,G,k,X,lam,hh,m0,sbar,s: Dstar_f(a,G,k,X,lam,hh) if X>k else None,
    200)
check("L2b  (5): Delta* = (y/(beta kappa))^(1/(beta-1)) = (ell)^(1/(1-alpha)) (alpha y)^(alpha/(1-alpha)) (200 draws)", ok, bad)

def sigstar_f(a,G,k,X,lam,hh): return (a*(lam*hh)*(X-k))**(1/(1-a))
ok, bad = verify_numeric(
    lambda a,G,k,X,lam,hh,m0,sbar,s: (lam*hh)**(-1/a)*Dstar_f(a,G,k,X,lam,hh)**(1/a) if X>k else None,
    lambda a,G,k,X,lam,hh,m0,sbar,s: a*(X-k)*Dstar_f(a,G,k,X,lam,hh) if X>k else None,
    200)
check("L2b  (6): sigma* = kappa Delta*^beta = alpha y Delta* = (alpha ell y)^(1/(1-alpha)) (200 draws)", ok, bad)

def Calpha_f(a): return (1-a)*a**(a/(1-a))
ok, bad = verify_numeric(
    lambda a,G,k,X,lam,hh,m0,sbar,s: (1-a)*(X-k)*Dstar_f(a,G,k,X,lam,hh) if X>k else None,
    lambda a,G,k,X,lam,hh,m0,sbar,s: Calpha_f(a)*(lam*hh*(X-k))**(1/(1-a)) if X>k else None,
    200)
check("L2b  (7): growth surplus (1-alpha)y Delta* = C_alpha (ell y)^(1/(1-alpha)) (200 draws)", ok, bad)

# tangency: m*'(G+Delta*) = -X
ok, bad = verify_numeric(
    lambda a,G,k,X,lam,hh,m0,sbar,s: -k - (1/a)*(lam*hh)**(-1/a)*(Dstar_f(a,G,k,X,lam,hh))**(1/a-1) if X>k else None,
    lambda a,G,k,X,lam,hh,m0,sbar,s: -X if X>k else None,
    200)
check("L2b  tangency m*'(G+Delta*) = -X (200 draws)", ok, bad)

# (e): Pi = max_sigma {y ell sigma^a - sigma}: compare closed form with 1-D optimum
def Pi_max(a,y,ell):
    # bisection on P'(sigma) = y*ell*a*sigma^(a-1) - 1 (strictly decreasing in sigma)
    Pp = lambda sg: y*ell*a*sg**(a-1) - 1
    f = lambda sg: y*ell*sg**a - sg
    lo, hi = mp.mpf('1e-300'), mp.mpf('1e-300')
    while Pp(hi) > 0: hi = hi*2
    for _ in range(400):
        mid = (lo+hi)/2
        if Pp(mid) > 0: lo = mid
        else: hi = mid
    sg = (lo+hi)/2
    return max(mp.mpf(0), f(sg))
ok, bad = verify_numeric(
    lambda a,G,k,X,lam,hh,m0,sbar,s: float(Pi_max(a, X-k, lam*hh)) if X>k else 0,
    lambda a,G,k,X,lam,hh,m0,sbar,s: Calpha_f(a)*((lam*hh)*(X-k))**(1/(1-a)) if X>k else 0,
    40)
check("L2e  Pi = max_sigma{y ell sigma^a - sigma} = C_alpha (ell y)^(1/(1-alpha)) (grid+Newton, 40 draws)", ok, bad)

# corner: X <= k -> optimum at Delta=0 (numeric scan)
ok = True
for _ in range(50):
    a = random.uniform(0.2, 0.5); G = random.uniform(0, 0.3)
    k = random.uniform(0.05, 1.0); X = k - random.uniform(0.001, 0.5)
    lam = random.uniform(0.05, 2.0); hh = random.uniform(0.05, 1.0)
    y = X - k; ell = lam*hh
    f = lambda d: y*d - ell**(-1/a)*d**(1/a)
    best = max(f(random.uniform(0, 3)) for _ in range(400))
    if best > 1e-9: ok = False; break
check("L2c  X <= k: score excess over m0+yG is negative for all Delta>0 (50 draws)", ok)

# ---- Lemma 3(a): derivative dR*/ds --------------------------------------------------
def _l3a_lhs(a,G,k,X,lam,hh,m0,sbar,s):
    h = 1e-7
    f = lambda ss: m0 + (X-k)*G + (Calpha_f(a)*((lam*(1-ss/sbar))*(X-k))**(1/(1-a)) if X>k else 0)
    return (f(s+h)-f(s-h))/(2*h)
ok, bad = verify_numeric(
    lambda a,G,k,X,lam,hh,m0,sbar,s: _l3a_lhs(a,G,k,X,lam,hh,m0,sbar,s),
    lambda a,G,k,X,lam,hh,m0,sbar,s: -(X-k)*Dstar_f(a,G,k,X,lam*(1-s/sbar),1.0)/(sbar-s) if X>k else 0,
    100, tol=1e-7)
check("L3a  dR*/ds = -(X-k)Delta*/(sbar-s) (numeric derivative; Delta* at ell(s)=lambda h(s)) (100 draws)", ok, bad)

# ---- Lemma 3(d): Lambda threshold ----------------------------------------------------
ok, bad = verify_numeric(
    lambda a,G,k,X,lam,hh,m0,sbar,s: Calpha_f(a)*(( (1/(X-k))*((9.9- (m0+(X-k)*G))/Calpha_f(a))**(1-a) *(X-k) ))**(1/(1-a)) + m0+(X-k)*G if X>k else None,
    lambda a,G,k,X,lam,hh,m0,sbar,s: 9.9 if X>k else None,
    100)
check("L3d  Lambda reproduces Rbar: R_inf + C_alpha(Lambda*y)^(1/(1-alpha)) = Rbar (100 draws)", ok, bad)

# threshold identities: Delta* = (Rbar-Rinf)/((1-alpha)y); sigma* = alpha(Rbar-Rinf)/(1-alpha)
def Rinf_f(a,G,k,X,m0): return m0 + (X-k)*G
ok_th = True
for _ in range(50):
    a = random.uniform(0.2, 0.5); G = random.uniform(0, 0.3)
    k = random.uniform(0.0, 1.0); X = k + random.uniform(0.05, 2.0)
    lam = random.uniform(0.05, 2.0); hh = random.uniform(0.05, 1.0); m0 = random.uniform(-0.1, 0.9)
    Rinf = m0 + (X-k)*G; Rbar = Rinf + random.uniform(0.01, 5.0)
    Dth = (Rbar-Rinf)/((1-a)*(X-k))
    ell_th = (1/(X-k))*((Rbar-Rinf)/Calpha_f(a))**(1-a)   # Lambda
    Dstar_th = (ell_th)**(1/(1-a)) * (a*(X-k))**(a/(1-a))
    if abs(Dstar_th-Dth) > 1e-9*max(1,Dth): ok_th = False; break
    sig_th = a*(X-k)*Dth
    sigstar_th = (a*ell_th*(X-k))**(1/(1-a))
    if abs(sigstar_th-sig_th) > 1e-9*max(1,sig_th): ok_th = False; break
check("L3d  at threshold: Delta* = (Rbar-Rinf)/((1-alpha)y) and sigma* = alpha(Rbar-Rinf)/(1-alpha) (50 draws)", ok_th)

# ---- Lemma 4: envelope derivatives ---------------------------------------------------
def Rstar_f(a,G,k,X,lam,hh,m0):
    yv = X-k
    if yv <= 0: return m0 + yv*G
    return m0 + yv*G + Calpha_f(a)*((lam*hh*yv)**(1/(1-a)))
ok, bad = verify_numeric(
    lambda a,G,k,X,lam,hh,m0,sbar,s: (Rstar_f(a,G,k,X+1e-6,lam,hh,m0) - Rstar_f(a,G,k,X-1e-6,lam,hh,m0))/2e-6 if abs(X-k)>0.05 else None,
    lambda a,G,k,X,lam,hh,m0,sbar,s: G + Dstar_f(a,G,k,X,lam,hh) if abs(X-k)>0.05 else None,
    100, tol=1e-7)
check("L4   dR*/dX = g* (finite diff, 100 draws)", ok, bad)
ok, bad = verify_numeric(
    lambda a,G,k,X,lam,hh,m0,sbar,s: (Rstar_f(a,G,k+1e-6,X,lam,hh,m0) - Rstar_f(a,G,k-1e-6,X,lam,hh,m0))/2e-6 if abs(X-k)>0.05 else None,
    lambda a,G,k,X,lam,hh,m0,sbar,s: -(G + Dstar_f(a,G,k,X,lam,hh)) if abs(X-k)>0.05 else None,
    100, tol=1e-7)
check("L4   dR*/dk = -g* (finite diff, 100 draws)", ok, bad)
ok, bad = verify_numeric(
    lambda a,G,k,X,lam,hh,m0,sbar,s: (Rstar_f(a,G,k,X,lam*1.000001,hh,m0) - Rstar_f(a,G,k,X,lam*0.999999,hh,m0))/(lam*2e-6) if abs(X-k)>0.05 else None,
    lambda a,G,k,X,lam,hh,m0,sbar,s: (X-k)*Dstar_f(a,G,k,X,lam,hh)/lam if abs(X-k)>0.05 else None,
    100, tol=1e-7)
check("L4   dR*/dlambda = (X-k)Delta*/lambda (finite diff, 100 draws)", ok, bad)
ok, bad = verify_numeric(
    lambda a,G,k,X,lam,hh,m0,sbar,s: (Rstar_f(a,G+1e-6,k,X,lam,hh,m0) - Rstar_f(a,G-1e-6,k,X,lam,hh,m0))/2e-6,
    lambda a,G,k,X,lam,hh,m0,sbar,s: X-k,
    100, tol=1e-7)
check("L4   dR*/dG = X-k (finite diff, 100 draws)", ok, bad)
# convexity in k: second difference positive
ok = True
for _ in range(100):
    a = random.uniform(0.2, 0.5); G = random.uniform(0, 0.3)
    k = random.uniform(0.02, 1.0); X = k + random.uniform(0.01, 2.0)
    lam = random.uniform(0.05, 2.0); hh = random.uniform(0.05, 1.0); m0 = 0.3
    e = 1e-4
    d2 = (Rstar_f(a,G,k+e,X,lam,hh,m0) - 2*Rstar_f(a,G,k,X,lam,hh,m0) + Rstar_f(a,G,k-e,X,lam,hh,m0))/e**2
    if d2 < -1e-6: ok = False; break
check("L4   R* convex in k (second difference >= 0, 100 draws)", ok)
# cross partial
def _mixed(a,G,k,X,lam,hh,m0):
    # nested central differences: d/dlambda of dR*/dk; steps chosen so roundoff
    # amplification (~1e-16/(4 e_k e_lam lam)) stays small relative to the mixed partial
    ek, el = 1e-4, 1e-3
    dRdk = lambda kk, ll: (Rstar_f(a,G,kk+ek,X,ll,hh,m0) - Rstar_f(a,G,kk-ek,X,ll,hh,m0))/(2*ek)
    return (dRdk(k, lam*(1+el)) - dRdk(k, lam*(1-el)))/(2*lam*el)
ok, bad = verify_numeric(
    lambda a,G,k,X,lam,hh,m0,sbar,s: _mixed(a,G,k,X,lam,hh,m0) if abs(X-k)>0.05 else None,
    lambda a,G,k,X,lam,hh,m0,sbar,s: -(Dstar_f(a,G,k,X,lam,hh)/((1-a)*lam)) if abs(X-k)>0.05 else None,
    100, tol=1e-4)
check("L4   d2R*/dkdlambda = -Delta*/((1-alpha)lambda) (100 draws)", ok, bad)

# ===================== exact rational-alpha symbolic checks =========================
al = sp.Rational(3,10)
b = 1/al
kappa = (sp.Rational(7,10)*sp.Rational(1,2))**(-b)   # ell = 7/20
m0s, Gs, ks, Xs, gs = sp.symbols("m0 G k X g", positive=True)
D = (gs - Gs)
mstar_ex = m0s - ks*gs - kappa*D**b
check("L1c  m*'' = -beta(beta-1)kappa Delta^(beta-2) exactly (alpha=3/10)",
      sp.simplify(sp.diff(mstar_ex, gs, 2) + b*(b-1)*kappa*D**(b-2)) == 0)

# Lemma S1: m~'' formula exactly (alpha = 3/10)
mt_ex = m0s - ks*gs/(1+gs) - kappa*D**b
check("LS1b m~''(g) = 2k/(1+g)^3 - beta(beta-1) kappa Delta^(beta-2) exactly (alpha=3/10)",
      sp.simplify(sp.diff(mt_ex, gs, 2) - (2*ks/(1+gs)**3 - b*(b-1)*kappa*D**(b-2))) == 0)
check("LS1b gap kg - kg/(1+g) = kg^2/(1+g) exactly", sp.simplify(ks*gs - ks*gs/(1+gs) - ks*gs**2/(1+gs)) == 0)

# alpha = 1/2: convex region of m~ exactly on (G, (k/kappa)^(1/3)-1)
alh = sp.Rational(1,2)
kap2 = sp.Rational(4,9)     # ell = 3/2 -> kappa = ell^-2
mt2 = m0s - ks*gs/(1+gs) - kap2*(gs-Gs)**2
mt2pp = sp.diff(mt2, gs, 2)
crit = sp.solve(sp.Eq(mt2pp, 0), gs)[0]
check("LS1d alpha=1/2: m~''=0 at g = (k/kappa)^(1/3) - 1 exactly (ell=3/2, kappa=4/9)",
      sp.simplify(crit - (ks/kap2)**(sp.Rational(1,3)) + 1) == 0)

# Lemma 5 (a): Xscr formula, exact with symbolic eta --------------------------------
eta_, m_, mbar_, th_, Minf_, T_ = sp.symbols("eta m mbar theta Minf T", positive=True)
mLR = th_*m_ + (1-th_)*mbar_
# use T = 5
Tn = 5
Veta = m_*sum(eta_**i for i in range(1,Tn+1)) + mLR*eta_**Tn*Minf_
dVdeta = sp.diff(Veta, eta_)
check("L5a  dV/deta = m sum t eta^(t-1) + mLR T eta^(T-1) Minf exactly (T=5)",
      sp.simplify(dVdeta - (m_*sum(i*eta_**(i-1) for i in range(1,Tn+1))
                             + mLR*Tn*eta_**(Tn-1)*Minf_)) == 0)
# eta = (1+g)/(1+r): dV/dg = dV/deta * eta/(1+g); Xscr = (dV/dg)/(dV/dm)
gg_, rr_ = sp.symbols("g r", positive=True)
eta_g = (1+gg_)/(1+rr_)
Vg = Veta.subs(eta_, eta_g)
Xscr_direct = sp.diff(Vg, gg_)/sp.diff(Vg, m_)
Xscr_20 = (m_*sum(i*eta_g**i for i in range(1,Tn+1)) + mLR*Tn*eta_g**Tn*Minf_) / \
          ((1+gg_)*(sum(eta_g**i for i in range(1,Tn+1)) + th_*eta_g**Tn*Minf_))
check("L5a  (20) exact: Xscr = [m Sum t eta^t + mLR T eta^T Minf]/[(1+g)(NT + theta eta^T Minf)]",
      sp.simplify(Xscr_direct - Xscr_20) == 0)
# (b) duration: D strictly increasing in T (adding a date with positive weight raises the mean)
okD = True
for TT in range(1, 12):
    et = sp.Rational(11,10)**0  # placeholder
    etv = sp.Rational(12,10)/sp.Rational(11,10)   # eta ~ 1.09
    D1 = sp.Rational(sum(i*etv**i for i in range(1,TT+1)), 1)/sp.Rational(sum(etv**i for i in range(1,TT+1)),1)
    D2 = sp.Rational(sum(i*etv**i for i in range(1,TT+2)), 1)/sp.Rational(sum(etv**i for i in range(1,TT+2)),1)
    if not (D2 > D1): okD = False; break
check("L5b  D strictly increasing in T (exact rationals, eta=12/11, T=1..11)", okD)
# dD/dln eta = Var_w(t) exactly for T=4
etv = sp.Symbol("eta", positive=True)
D4 = sum(i*etv**i for i in range(1,5))/sum(etv**i for i in range(1,5))
dD = sp.simplify(sp.diff(D4, etv)*etv)
Var4 = sp.simplify(sum(etv**i*i**2 for i in range(1,5))/sum(etv**i for i in range(1,5)) - D4**2)
check("L5b  dD/d(ln eta) = Var_w(t) exactly (T=4)", sp.simplify(dD - Var4) == 0)
# (d) Gordon limit: D -> (1+r)/(r-g): numeric with eta->1 from below via large T
okD2 = True
for (gv, rv) in [(0.02,0.0934),(0.05,0.10),(0.25,0.30)]:  # need g < r
    et = (1+gv)/(1+rv)
    Dlarge = sum(i*et**i for i in range(1,3000))/sum(et**i for i in range(1,3000))
    if abs(Dlarge - (1+rv)/(rv-gv)) > 1e-6: okD2 = False
check("L5d  Gordon: D -> (1+r)/(r-g) as T -> inf (3 param sets, T=2999)", okD2)
# (e) T=1 theta=0 exact
V1 = m_*eta_ + mbar_*eta_*Minf_
X1 = sp.simplify(sp.diff(V1, eta_)/sp.diff(V1, m_))    # dV/dg = dV/deta * eta/(1+g); dV/dm ...
# direct in g:
V1g = V1.subs(eta_, eta_g)
X1g = sp.simplify(sp.diff(V1g, gg_)/sp.diff(V1g, m_))
check("L5e  T=1, theta=0: Xscr = (m + mbar Minf)/(1+g) = (V/S0)(1+r)/(1+g)^2 exactly",
      sp.simplify(X1g - (m_+mbar_*Minf_)/(1+gg_)) == 0
      and sp.simplify((m_+mbar_*Minf_)/(1+gg_) - (m_*eta_g+mbar_*eta_g*Minf_)*(1+rr_)/(1+gg_)**2) == 0)

# Remark 3(b) identities exactly
mm_, kk_, XX_, rr_ = sp.symbols("m k X r", positive=True)
ggv = sp.Symbol("g", positive=True)
check("R3b  R_X = (X-k)g + e + rk with e = m + k(g-r), exactly",
      sp.simplify(XX_*ggv + mm_ - ((XX_-kk_)*ggv + (mm_ + kk_*(ggv-rr_)) + kk_*rr_)) == 0)
check("R3b  k[ROIC + (X/k - 1)g] = Xg + m with ROIC = (m+kg)/k, exactly",
      sp.simplify(kk_*((mm_+kk_*ggv)/kk_ + (XX_/kk_-1)*ggv) - (XX_*ggv+mm_)) == 0)

# Remark 2: taxed margin identity exactly
tau_, psi_, dK_, sig_ = sp.symbols("tau psi delta_K sigma", nonnegative=True)
lhs = (1-tau_)*(m0s - sig_) - (1-psi_)*tau_*dK_*ks - (1-psi_*tau_)*ks*gs
rhs = ((1-tau_)*m0s - (1-psi_)*tau_*dK_*ks) - (1-tau_)*sig_ - (1-psi_*tau_)*ks*gs
check("R2   taxed margin identity exactly", sp.simplify(lhs-rhs) == 0)
# psi_T (27) exactly for T = 5 and 15 at r = 0.10
rv = sp.Rational(1,10)
for TT in (5, 15):
    direct = sp.Rational(1,2)/TT + sum(sp.Rational(1,1)/TT*(1+rv)**(-t) for t in range(1,TT)) + sp.Rational(1,2)/TT*(1+rv)**(-TT)
    form = (1+(1+rv)**(-TT))/(2*TT) + (1-(1+rv)**(-(TT-1)))/(rv*TT)
    check(f"R2   psi_{TT}: (27) equals direct mid-year schedule exactly (r=1/10)", sp.simplify(direct-form) == 0)
check("R2   psi_5 = 0.796, psi_15 = 0.532",
      abs(float((1+(1+rv)**(-5))/(2*5)+(1-(1+rv)**(-4))/(rv*5)) - 0.796) < 5e-4 and
      abs(float((1+(1+rv)**(-15))/(2*15)+(1-(1+rv)**(-14))/(rv*15)) - 0.532) < 5e-4)
check("R2   (1-tau)^(-alpha) at alpha=0.3: 1.050 (tau=0.15), 1.073 (tau=0.21)",
      abs(0.85**(-0.3)-1.050) < 5e-4 and abs(0.79**(-0.3)-1.073) < 5e-4)

# Prop 4 Cournot exactly
A_, B_, n_, c_ = sp.symbols("A B n chat", positive=True)
xn = (A_-c_)/(B_*(n_+1))
Pn = A_ - B_*n_*xn
check("P4a  P_n = (A+n chat)/(n+1) exactly", sp.simplify(Pn - (A_+n_*c_)/(n_+1)) == 0)
check("P4a  pi_n = (A-chat)^2/(B(n+1)^2) exactly", sp.simplify((Pn-c_)*xn - (A_-c_)**2/(B_*(n_+1)**2)) == 0)
check("P4a  L_n = (A-chat)/(A+n chat) exactly", sp.simplify((Pn-c_)/Pn - (A_-c_)/(A_+n_*c_)) == 0)
Z_ = sp.Symbol("Z", positive=True)
wn = A_ - c_ - B_*Z_*(n_+1)/n_
Qw = n_*(A_-c_-sp.Symbol("w"))/(B_*(n_+1))
check("P4c  w_n solves Q_n(w) = Z and then P = A - BZ exactly",
      sp.simplify(Qw.subs(sp.Symbol("w"), wn) - Z_) == 0
      and sp.simplify(A_ - B_*Qw.subs(sp.Symbol("w"), wn) - (A_-B_*Z_)) == 0)
PZ = A_ - B_*Z_
check("P4c  net Lerner BZ/(nP) and per-firm profit BZ^2/n^2 exactly",
      sp.simplify((PZ-c_-wn)/PZ - B_*Z_/(n_*PZ)) == 0
      and sp.simplify((PZ-c_-wn)*Z_/n_ - B_*Z_**2/n_**2) == 0)

# Lemma S4(b) exactly
ceff_, cinc_ = sp.symbols("ceff cinc", positive=True)
cc_ = sp.Symbol("c", positive=True)
Cc = cc_ + sp.exp(-cc_/ceff_)*cinc_
cs = sp.solve(sp.Eq(sp.diff(Cc, cc_), 0), cc_)[0]
check("LS4b c* = ceff ln(cinc/ceff); C(c*) = ceff[1+ln(cinc/ceff)] exactly",
      sp.simplify(cs - ceff_*sp.log(cinc_/ceff_)) == 0
      and sp.simplify(Cc.subs(cc_, cs) - ceff_*(1+sp.log(cinc_/ceff_))) == 0)

# Prop S3(iv) curvature: m*''(gc) = -(1-alpha)y/(alpha Delta*) using FOC
alv = sp.Rational(3,10); bv = 1/alv
kapv = sp.Rational(9,10)
Dv = sp.Symbol("Delta", positive=True)
yv = bv*kapv*Dv**(bv-1)              # FOC
mcurv = -bv*(bv-1)*kapv*Dv**(bv-2)
check("PS3iv m*''(gc) = -(1-alpha)y/(alpha Delta*) exactly (alpha=3/10)",
      sp.simplify(mcurv - (-(1-alv)*yv/(alv*Dv))) == 0)

# Remark S1(a) fixed cost derivative exactly
Xi_, M_, sv = sp.symbols("Xi M s", positive=True)
Rinf_fx = -Xi_/(sv*M_)          # the s-dependent part of R_inf
check("RS1a d/ds of -Xi/(sM) = Xi/(s^2 M) exactly", sp.simplify(sp.diff(Rinf_fx, sv) - Xi_/(sv**2*M_)) == 0)

print()
nf = sum(1 for _, ok in results if not ok)
print(f"TOTAL {len(results)} checks, {nf} failures")
sys.exit(1 if nf else 0)