#!/usr/bin/env python3
"""Lead independent diagnostics for the referee review of
"The Rule of 40 as a Price Line" (Murthy, Nov 2026).

These are INDEPENDENT checks of consequential formulas, implemented from the
paper's stated equations only (not from the author's verify_theory.py).
Labels: [NUM] numerical evidence, [HAND] hand derivation reproduced numerically,
[MC] randomized checks (fixed seeds). sympy not used here (agents A/D do symbolic).
"""
import numpy as np
from scipy.optimize import minimize_scalar
import sys

np.random.seed(20261103)
results = []

def rec(label, status, detail):
    results.append((label, status, detail))
    print(f"[{status}] {label}\n    {detail}")

# ------------------------------------------------------------------
# 1. Lemma 1 frontier closed form: m*(g) = m0 - k g - kappa (g-G)^beta
# [MC] random parameter draws: for each draw, pick sigma, compute
# g = G + l*sigma^alpha, m = m0 - sigma - k*g  and compare with (4).
# kappa = l^{-beta} with beta = 1/alpha.
# ------------------------------------------------------------------
ok = True
worst = 0.0
for _ in range(20000):
    m0 = np.random.uniform(0.0, 0.8)
    k  = np.random.uniform(0.0, 2.0)
    G  = np.random.uniform(0.0, 0.4)
    a  = np.random.uniform(0.25, 0.45)   # alpha
    lam = np.random.uniform(0.05, 2.0)
    sbar = 1.0; s = np.random.uniform(0.01, 0.99)  # share only affects h
    h = 1 - s/sbar
    l = lam*h
    beta = 1/a
    kappa = l**(-beta)
    sig = np.random.uniform(0.0, 3.0)
    g = G + l*sig**a
    m_direct = m0 - sig - k*g
    m_star = m0 - k*g - kappa*(g-G)**beta
    err = abs(m_direct - m_star)
    worst = max(worst, err)
    if err > 1e-9: ok = False
rec("Lemma 1 frontier identity m0-sigma-kg == (4)", "PASS" if ok else "FAIL",
    f"20000 random draws; max |diff| = {worst:.2e}")

# ------------------------------------------------------------------
# 2. Lemma 2 max-score closed form vs direct numerical maximization
# [MC] X > k interior case: R*_X = m0 + (X-k)G + C_a * (l*(X-k))^(1/(1-a))
# ------------------------------------------------------------------
ok = True; worst = 0.0
C = lambda a: (1-a)*(a**(a/(1-a)))
for _ in range(5000):
    m0 = np.random.uniform(0.0, 0.8)
    k  = np.random.uniform(0.0, 1.5)
    G  = np.random.uniform(0.0, 0.4)
    a  = np.random.uniform(0.25, 0.45)
    lam = np.random.uniform(0.05, 2.0)
    X  = k + np.random.uniform(0.05, 10.0)   # X > k
    h = 1.0; l = lam                          # share irrelevant, take h=1
    beta = 1/a; kappa = l**(-beta)
    # closed form (7)
    Dstar = (l**(1/(1-a))) * (a*(X-k))**(a/(1-a))
    Rstar_cf = m0 + (X-k)*G + (1-a)*(X-k)*Dstar
    # numerical: maximize X*g + m*(g) over g in [G, G+ big]
    f = lambda g: -(X*g + (m0 - k*g - kappa*(g-G)**beta))
    res = minimize_scalar(f, bounds=(G, G + 50), method="bounded",
                          options={"xatol": 1e-12})
    Rstar_num = -res.fun
    err = abs(Rstar_cf - Rstar_num)
    worst = max(worst, err)
    if err > 1e-6: ok = False
rec("Lemma 2 closed-form max score (7) vs numerical tangency", "PASS" if ok else "FAIL",
    f"5000 draws; max |diff| = {worst:.2e}")

# corner case X <= k: optimum at g=G
ok = True
for _ in range(3000):
    m0 = np.random.uniform(0.0, 0.8); k = np.random.uniform(0.3, 2.0)
    G = np.random.uniform(0.0, 0.4); a = np.random.uniform(0.25, 0.45)
    lam = np.random.uniform(0.05, 2.0); X = np.random.uniform(0.0, k*0.99)
    beta = 1/a; kappa = lam**(-beta)
    f = lambda g: -(X*g + (m0 - k*g - kappa*(g-G)**beta))
    res = minimize_scalar(f, bounds=(G, G+50), method="bounded")
    R_cf = m0 + (X-k)*G           # corner value
    R_G  = X*G + (m0 - k*G)        # same
    if abs(res.x - G) > 1e-6 and (-res.fun) > R_G + 1e-9: ok = False
rec("Lemma 2(c) corner optimum at g=G when X<=k", "PASS" if ok else "FAIL",
    "numerical optimizer never prefers interior when X<k (3000 draws)")

# duality: X(g) = k + beta*kappa*(g-G)^(beta-1) equals -m*'(g)  [HAND]
a=0.3; lam=0.6; beta=1/a; kappa=lam**(-beta); k=0.1; G=0.1; m0=0.45
g=0.3
X_pred = k + beta*kappa*(g-G)**(beta-1)
eps=1e-7
X_fd = -((m0-k*(g+eps)-kappa*(g+eps-G)**beta)-(m0-k*(g-eps)-kappa*(g-eps-G)**beta))/(2*eps)
rec("Lemma 2(d) duality X(g) = -m*'(g)", "PASS" if abs(X_pred-X_fd)<1e-6 else "FAIL",
    f"at g=0.3: predicted {X_pred:.6f}, finite-diff {X_fd:.6f}")

# ------------------------------------------------------------------
# 3. Corollary 1 / score-budget example numbers (main p.18)
# X=1,k=0,m0=0.6,G=0.2 => R_inf=0.8; sbar=0.5
# ------------------------------------------------------------------
X,k,m0,G,sbar = 1.0,0.0,0.6,0.2,0.5
Rinf = m0 + (X-k)*G
# (a) period rates: T <= ln(sbar/s0)/ln(1+(Rbar-Rinf)/((X-k)(1+G)))
def Tbound(s0, Rbar):
    return np.log(sbar/s0)/np.log(1+(Rbar-Rinf)/((X-k)*(1+G)))
b1000_s1 = Tbound(0.01, 10.0)   # Rbar=1000 points = 10.0
b140_s1  = Tbound(0.01, 1.4)    # 140 points
b1000_s5 = Tbound(1e-5, 10.0)
rec("Corollary 1(a) bounds: 1.8 / 9.6 / 5.0", "PASS" if
    (abs(b1000_s1-1.81)<0.05 and abs(b140_s1-9.65)<0.1 and abs(b1000_s5-5.01)<0.1) else "FAIL",
    f"computed {b1000_s1:.2f} (paper: 1.8), {b140_s1:.2f} (paper: 9.6), {b1000_s5:.2f} (paper: 5.0)")
# (b) continuous: (X-k)ln(sbar/s0)/(Rbar-Rinf); at static optimum x (1-alpha)
tc = (X-k)*np.log(sbar/0.01)/(10.0-Rinf)
rec("Corollary 1(b) continuous bounds: 0.43 / 0.30", "PASS" if
    (abs(tc-0.425)<0.01 and abs(0.7*tc-0.298)<0.01) else "FAIL",
    f"computed {tc:.3f} (paper: 0.43), {0.7*tc:.3f} (paper: 0.30)")

# ------------------------------------------------------------------
# 4. Table 4 full-cost ceiling arithmetic, eq (29) with psi=0, deltaK=0:
# Rmax = (1-tau)(1-cc-f-amin-cfull) + (1-k)G     [points]
# ------------------------------------------------------------------
cases = {
 "favorable":    dict(cc=0.03, f=0.020, amin=0.015, cfull=2.1, tau=0.15),
 "central":      dict(cc=0.06, f=0.025, amin=0.030, cfull=6.2, tau=0.18),
 "conservative": dict(cc=0.12, f=0.030, amin=0.046, cfull=16.5, tau=0.21),
 "high-compute": dict(cc=0.40, f=0.025, amin=0.030, cfull=7.2, tau=0.18),
}
Gk = [(0.05,0.0),(0.15,0.0),(0.30,0.0),(0.15,0.5),(0.05,1.5),(0.30,1.5)]
paper_tbl = {
 "favorable":    [77.7,82.7,92.7,107.7,85.2,75.2,62.7,22.3],
 "central":      [67.5,72.5,82.5,97.5,75.0,65.0,52.5,32.5],
 "conservative": [50.5,55.5,65.5,80.5,58.0,48.0,35.5,49.5],
 "high-compute": [38.7,43.7,53.7,68.7,46.2,36.2,23.7,61.3],
}
allok = True; msgs=[]
for cname, p in cases.items():
    base = (1-p["tau"])*(1-p["cc"]-p["f"]-p["amin"]-p["cfull"]/100)
    row = [100*base] + [100*(base + (1-kk)*Gg) for (Gg,kk) in Gk]
    # G* where ceiling hits 100 at k=0: G* = 1 - base
    Gstar = 100*(1-base)
    paper = paper_tbl[cname]
    for i,(mine,pap) in enumerate(zip(row+[Gstar], paper)):
        if abs(mine-pap) > 0.15:
            allok=False; msgs.append(f"{cname} col{i}: computed {mine:.1f} vs paper {pap}")
rec("Table 4 ceiling values (all cases/cells + G*)", "PASS" if allok else "FAIL",
    "; ".join(msgs) if msgs else "all 32 cells + 4 G* reproduce within 0.15pt")

# threshold decomposition (main p.56): tau + (1-tau)(cc+f+amin+cfull) = 32.5%
p = cases["central"]
dec = 100*(p["tau"] + (1-p["tau"])*(p["cc"]+p["f"]+p["amin"]+p["cfull"]/100))
rec("Central threshold decomposition = 32.5", "PASS" if abs(dec-32.48)<0.05 else "FAIL",
    f"computed {dec:.2f} (paper: 32.5; components 18.0+4.9+2.1+2.5+5.1)")

# ------------------------------------------------------------------
# 5. Lemma 5 duration / screening weight and Table S3 multiples
# ------------------------------------------------------------------
# (b): X_scr = m*D/(1+g), D = PV-weighted avg date, persistent margin, no TV
# Paper's example (supp S2.2): "a duration of 10 years at g = 0.25 requires
# about 15 years of 25% growth (D = 10.25 at T = 15)". So evaluate at T=15
# (D~10) -> X_scr ~ 2. My first run used T=10 (D=6.5) and wrongly 'failed'.
def Xscr(m,g,r,T):
    eta=(1+g)/(1+r)
    t=np.arange(1,T+1)
    N=sum(eta**t)
    D=sum(t*eta**t)/N
    return m*D/(1+g), D
v,D15 = Xscr(0.25,0.25,0.10,15)
_,D10 = Xscr(0.25,0.25,0.10,10)
rec("Lemma 5(b) example Xscr ~ 2 at D~10 (T=15)", "PASS" if
    (abs(D15-10.25)<0.05 and abs(v-2.05)<0.05 and abs(D10-6.5)<0.05) else "FAIL",
    f"T=15: D={D15:.2f} (paper 10.25) -> Xscr={v:.3f} (paper ~2); "
    f"T=10: D={D10:.2f} (paper 6.5, consistent with paper's own note)")
# Table S3: V/S0 = m*N(eta) + m*eta^T*M_inf, T=10, then G_inf=3%, r=9.34%
def mult(m,g,r=0.0934,T=10,Ginf=0.03):
    eta=(1+g)/(1+r)
    t=np.arange(1,T+1)
    N=sum(eta**t)
    Minf=(1+Ginf)/(r-Ginf)
    return m*(N + eta**T*Minf)
paper_S3 = {30:12.1, 20:11.7, 10:8.3, 0:5.2}
ok=True; det=[]
for g,m in [(30,0.10),(20,0.20),(10,0.30),(0,0.40)]:
    V = mult(m,g/100)
    det.append(f"g={g}%: {V:.2f} vs paper {paper_S3[g]}")
    if abs(V-paper_S3[g])>0.15: ok=False
rec("Table S3 equal-score unequal-value multiples", "PASS" if ok else "FAIL", "; ".join(det))

# ------------------------------------------------------------------
# 6. Bending Spoons Table 3 score arithmetic (from stated filing shares)
# ------------------------------------------------------------------
rows=[]
def score(g,m): return g+m
rows.append(("2025 GAAP before interest", 94.7+21.3, 115.9))
rows.append(("2025 GAAP after interest", 94.7+21.3-10.9, 105.0))
rows.append(("2025 cash after interest", 94.7+22.2, 116.9))
rows.append(("2025 cash before interest (24% tax addback)", 94.7+22.2+10.9*0.76, 125.2))
rows.append(("2025 fully charged (lower bound)", 94.7+30.5-141.8, -16.5))
rows.append(("Q2-26 reported growth GAAP", 126.3+34.1, 160.5))
rows.append(("Q2-26 organic before interest", 3+34.1, 37.1))
rows.append(("Q2-26 organic after interest", 3+34.1-15.5, 21.6))
rows.append(("Q2-26 organic bef int+reorg", 3+34.1+7.2, 44.3))
ok=True; det=[]
for nm,mine,pap in rows:
    det.append(f"{nm}: {mine:.1f} vs {pap}")
    if abs(mine-pap)>0.25: ok=False; det[-1]+=" <-- MISMATCH"
rec("Bending Spoons score arithmetic (Table 3)", "PASS" if ok else "FAIL", "; ".join(det))

# ------------------------------------------------------------------
# 7. Lemma 3(d)/Rule-of-1000 illustration (main p.17)
# X=1,k=0,m0=0.6,G=0.2 => R_inf=.8; Lambda(Rbar=10) from (10)
# ------------------------------------------------------------------
a=0.3; X=1; k=0; Rinf=0.8
Ca = C(a)
# (10): Lambda(Rbar) = [ (1/(X-k)) * ((Rbar-Rinf)/C_alpha) ]^(1-alpha)
# NOTE: first run divided by C_a OUTSIDE the power -> wrong; corrected.
Lam = ((10.0-Rinf)/((X-k)*Ca))**(1-a)
# claimed: Lambda ~ 8.71; at threshold Delta* = (Rbar-Rinf)/((1-a)(X-k))
Dstar=(10-0.8)/((1-a)*1)
sig = a*(10-0.8)/(1-a)
m = 0.6 - 0*(0.2+Dstar) - sig
rec("Rule-of-1000 illustration (main p.17)", "PASS" if abs(Lam-8.71)<0.05 else "FAIL",
    f"Lambda={Lam:.2f} (paper 8.71); Delta*={Dstar*100:.0f}pts (paper ~1314); "
    f"spend={sig*100:.0f}% (paper ~394%); margin={m*100:.0f}% (paper ~ -334%)")

# ------------------------------------------------------------------
# 8. Execution-path arithmetic (main 7.3): 6.3%/yr embed rate; b_bar=0.67
# ------------------------------------------------------------------
# central: capacity 10%/yr of program, pemb=.70, freeze ~10% => 6.3%/yr
rate = 0.10*0.70*(1-0.10)
E36 = min(1.0, rate*10)      # 10 waves by 2036 (2026..2036, Temb=1.25, Tpar=1)
realized = 0.67*E36
rec("Central execution: embed ~61% and realize ~41% by 2036", "PASS" if
    (abs(rate-0.063)<1e-6 and abs(E36-0.63)<0.03 and abs(realized-0.422)<0.02) else "FAIL",
    f"embed rate {rate:.3f}/yr, E(2036)={E36:.2f} (paper ~61%), realized={realized:.2f} (paper ~41%)")

# ------------------------------------------------------------------
# 9. Accountability-floor example (main 7.2): 0.30% direct + 0.075% design
# ------------------------------------------------------------------
direct = 0.30; design = 0.075
tot = direct + design
rec("Accountability floor example 0.37-0.38%", "PASS" if abs(tot-0.375)<0.006 else "FAIL",
    f"0.30 direct + 0.075 design = {tot:.3f}% (paper: 0.37-0.38%)")

# ------------------------------------------------------------------
# 10. Lemma S2(a) pass-through: gamma=1-f-u/p, dgamma/du = -(1-eps_p)/p  [HAND]
# ------------------------------------------------------------------
import sympy as sp
u,p,f,eps = sp.symbols("u p f eps", positive=True)
gam = 1 - f - u/p
# eps_p = dln p / dln u => dp/du = eps*p/u
dgdu = sp.diff(gam,u) + sp.diff(gam,p)*eps*p/u
simplified = sp.simplify(dgdu + (1-eps)/p)
rec("Lemma S2(a) dgamma/du = -(1-eps_p)/p under eps_p = dlnp/dlnu", "PASS" if simplified==0 else "FAIL",
    f"sympy residual: {simplified}")

print("\n==== SUMMARY ====")
for lab,st,det in results:
    print(f"{st:5s} {lab}")
n_pass = sum(1 for _,s,_ in results if s=="PASS")
print(f"{n_pass}/{len(results)} checks pass")