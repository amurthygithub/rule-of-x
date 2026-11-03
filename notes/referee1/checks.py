"""Referee 1 scratch checks (independent of verify_theory.py)."""
import numpy as np
from scipy.optimize import brentq, minimize_scalar
from scipy.integrate import solve_ivp

def Dstar(l, y, a): return l**(1/(1-a)) * (a*y)**(a/(1-a))
def Rstar(m0, G, l, a, k=0.0, X=1.0):
    y = X-k
    if y <= 0: return m0 + y*G, G
    D = Dstar(l, y, a); return m0 + y*G + (1-a)*y*D, G + D
C = lambda a: (1-a)*a**(a/(1-a))

print("== 1. Numerical maximization vs closed form (Prop score)")
rng = np.random.default_rng(0); bad = 0
for _ in range(2000):
    a = rng.uniform(0.1, 0.9); l = rng.uniform(0.05, 3); m0 = rng.uniform(0, .8)
    G = rng.uniform(-.1, .4); k = rng.uniform(0, 2); X = rng.uniform(0, 4)
    f = lambda s: -(X*(G + l*s**a) + m0 - s - k*(G + l*s**a))
    res = minimize_scalar(f, bounds=(0, 200), method='bounded', options={'xatol': 1e-12})
    num = max(-res.fun, -f(0.0)); cf = Rstar(m0, G, l, a, k, X)[0]
    bad += abs(num - cf) > 1e-6
print("violations:", bad)

print("\n== 2. Calibration (Table calib) vs location of the empirical frontier (FCF after SBC)")
a = 0.25
for lh in (1.0, 1.5):
    R, g = Rstar(0.28, 0.10, lh, a); D = g - 0.10
    print(f"  model 2025, lam_h={lh}: g*={g:.3f}, sigma*={a*D:.3f}, m*={0.28 - a*D:.3f}, R*={R:.3f}")
# back out top firm's (m0, lam_h) from its chosen point (g_supp, phi_supp), G = period median growth (Table desc)
for per, gs, ph, G in [("2010-15", .80, .41, .136), ("2016-19", .65, .31, .145),
                       ("2020-22", .75, .36, .175), ("2023-25", .40, .45, .096)]:
    D = gs - G; m0 = ph + a*D; lh = (D / a**(a/(1-a)))**(1-a)
    print(f"  {per}: chosen (g,m)=({gs},{ph}) -> implied m0={m0:.3f}, lam_h={lh:.3f}, R*={Rstar(m0,G,lh,a)[0]:.3f}")

print("\n== 3. Rule-of-1000 threshold Lambda sensitivity to alpha (m0=.5, G=.2, X=1, k=0)")
for a_ in (0.20, 0.25, 0.30, 0.43):
    Lam = ((10 - 0.7)/C(a_))**(1-a_)
    print(f"  alpha={a_}: Lambda={Lam:.2f}")

print("\n== 4. Competitive limit (Prop entry): R = G + (r-G)k + rho")
for G, r, k in [(0.10, 0.09, 0.5), (0.05, 0.10, 0.5)]:
    base = G + (r - G)*k
    print(f"  G={G}, r={r} (r>G? {r>G}), k={k}: base={base:.4f}; rho needed for R=1: {1-base:.3f}")
for G in (0.2, 0.3, 0.4):
    print(f"  G={G}, r=.10, k=.5: rho needed for R=1: {1-(G+(0.10-G)*0.5):.3f}")

print("\n== 5. Ceiling: market growth needed for R_max >= 1 (k=0, psi=0)")
for name, tau, cc, f, am in [("fav", .15, .15, .02, .04), ("cen", .18, .20, .025, .07), ("con", .21, .25, .03, .10)]:
    base = (1-tau)*(1-cc-f-am); print(f"  {name}: base={base:.4f}, G needed={1-base:.3f}; k=1.5 penalty at G=.3 psi=0: {1.5*.3:.3f}, psi=1: {(1-tau)*1.5*.3:.3f}")
# classic low-compute SaaS
base = 0.85*(1-0.05-0.0-0.03); print(f"  low-compute SaaS (tau=.15, cc=.05, f=0, amin=.03): base={base:.3f}, G needed={1-base:.3f}")

print("\n== 6. Capital-for-labor (Cor capital) with depreciation delta of owned compute")
for g, d in [(0.5, 0), (0.1, 0), (0.1, 0.25), (0.5, 0.25)]:
    print(f"  g*={g}, delta={d}: opex cut needed per dk=0.10: {(g+d)*0.10*100:.1f} pts")

print("\n== 7. Rule-of-X weight: permanent MRS (Lemma) vs one-period (co-state) MRS")
r, g, m = 0.10, 0.25, 0.25
q = (1+g)/(1+r)
for T in (10, 15):
    t = np.arange(1, T+1); A = (q**t).sum(); S1 = (t*q**t).sum()
    Xperm = m*S1/((1+g)*A); Xone = m*A/((1+g)*q)
    print(f"  T={T}: D={S1/A:.2f}, X_perm=mD/(1+g)={Xperm:.2f}, X_one-period=mA/((1+g)q)={Xone:.2f}, V/S0={m*A:.2f}")
# with terminal value, theta=1 (Lemma 2b), T=10, Ginf=.03
T=10; Ginf=.03; Gam=(1+Ginf)/(r-Ginf); t=np.arange(1,T+1); A=(q**t).sum(); S1=(t*q**t).sum()
B = A + q**T*Gam
print(f"  T=10 + TV: X_perm={m*(S1+T*q**T*Gam)/((1+g)*B):.2f}, X_one-period={m*B/((1+g)*q):.2f}, V/S0={m*B:.2f}")
# verify one-period MRS numerically: perturb year-1 growth and year-1 margin only
def V(g1, m1, g=g, m=m, T=T):
    S = 1.0; v = 0.0
    for tt in range(1, T+1):
        S *= (1+g1) if tt == 1 else (1+g)
        v += (m1 if tt == 1 else m)*S/(1+r)**tt
    return v + m*S*(1+Ginf)/(r-Ginf)/(1+r)**T
e = 1e-6
print(f"  numeric one-period MRS: {((V(g+e,m)-V(g-e,m))/(2*e))/((V(g,m+e)-V(g,m-e))/(2*e)):.2f}")

print("\n== 8. Model-implied slope of log(excess growth) on log(spend share) across optimizing firms")
a = 0.25; ls = np.exp(rng.normal(np.log(0.4), 0.5, 5000)); y = 1.0
D = Dstar(ls, y, a); sig = a*y*D
print(f"  heterogeneous lam_h, common X: slope={np.polyfit(np.log(sig), np.log(D), 1)[0]:.3f} (alpha={a})")
ys = np.exp(rng.normal(0, 0.5, 5000)); D = Dstar(0.4, ys, a); sig = a*ys*D
print(f"  heterogeneous X, common lam_h: slope={np.polyfit(np.log(sig), np.log(D), 1)[0]:.3f}")

print("\n== 9. Myopic path bound (Prop saturation e), alpha=.3, lam=1.2, X=1,k=0")
a, lam, y, sb, s0 = 0.3, 1.2, 1.0, 0.5, 0.01
p = 1/(1-a); nu = lam**p*(a*y)**(a*p)
sol = solve_ivp(lambda t, s: [s[0]*nu*(1-s[0]/sb)**p], (0, 40), [s0], dense_output=True, rtol=1e-10, atol=1e-14)
ok = True
for t in np.linspace(0.01, 40, 400):
    h = 1 - sol.sol(t)[0]/sb; ex = C(a)*(lam*h*y)**p
    bound = C(a)*(lam*y)**p*((1-s0/sb)**(-a/(1-a)) + a/(1-a)*nu*(s0/sb)*t)**(-1/a)
    ok &= ex <= bound*(1+1e-8)
print("  bound holds on grid:", ok)

print("\n== 10. Discrete budget: max periods with R>=10 (m0=.6,G=.2,X=1,k=0)")
for s0 in (0.01, 0.001, 1e-5):
    print(f"  s0={s0}, sbar=.5: N <= {np.log(0.5/s0)/np.log(1+9.2/1.2):.2f}")

print("\n== 11. Timing example (Lemma timing c)")
f = lambda g: g + 0.5 - 1.25*g/(1+g) - 0.5*(g-0.1)**(10/3)
gg = np.linspace(0.1, 1.2, 200001); v = f(gg); i = v.argmax(); print(f"  argmax g={gg[i]:.4f}, value={v[i]:.4f}, corner={f(0.1):.4f}")
