#!/usr/bin/env python3
"""
Referee A - dynamics: Proposition 1 (score budget), Corollary 1 (transience),
Proposition S1 (myopic path), Proposition S2 (sharpness), Remark S1(b) (Gi != G),
and the worked numerical examples in main Sec. 3.4.

Model under Assumptions 1-4: sdot/s = lambda h(s) sigma^alpha, h = 1 - s/sbar,
g = G + sdot/s, m <= m0 - sigma - k g, R = X g + m.
"""
import numpy as np
from scipy.integrate import solve_ivp
import math, sys, platform, datetime

rng = np.random.default_rng(20261104)
print("session:", datetime.datetime.now().isoformat())
print("python", platform.python_version(), "numpy", np.__version__, "scipy", __import__('scipy').__version__)

results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + ("  " + str(detail) if detail else ""))

# ---------------- Prop 1(a): continuous-time budget ----------------------------------
bad = 0; worst = 0.0
for trial in range(300):
    alpha = rng.uniform(0.2, 0.5)
    G = rng.uniform(0, 0.3); k = rng.uniform(0, 0.5)
    X = k + rng.uniform(0.05, 2.0)     # X > k
    lam = rng.uniform(0.1, 1.5); sbar = rng.uniform(0.2, 1.0)
    m0v = rng.uniform(0.1, 0.8)
    s0 = sbar*rng.uniform(0.001, 0.2)
    y = X - k; Rinf = m0v + y*G
    T = rng.uniform(1, 25)
    # random piecewise-constant spend path
    nsw = rng.integers(1, 8)
    switches = np.sort(rng.uniform(0, T, nsw))
    levels = rng.uniform(0, 2.5, nsw+1)
    def sig_of_t(t):
        return levels[np.searchsorted(switches, t, side='right')]
    def rhs(t, s):
        sg = sig_of_t(t)
        return lam*(1-s/sbar)*sg**alpha * s
    sol = solve_ivp(rhs, [0, T], [s0], rtol=1e-10, atol=1e-12, dense_output=True,
                    max_step=(T/500))
    ts = sol.t; ss = sol.y[0]
    # margins: use frontier margins m = m0 - sigma - k g (the most favorable)
    Delta = lam*(1-ss/sbar)*np.array([sig_of_t(t) for t in ts])**alpha
    gs = G + Delta
    ms = m0v - np.array([sig_of_t(t) for t in ts]) - k*gs
    Rx = X*gs + ms
    integ = np.trapezoid(np.maximum(Rx - Rinf, 0), ts)
    bound1 = y*math.log(ss[-1]/s0)
    bound2 = y*math.log(sbar/s0)
    if integ > bound1 + 1e-6*max(1,abs(bound1)) or bound1 > bound2 + 1e-12:
        bad += 1
    worst = max(worst, integ/max(bound1,1e-12))
check("P1a  integral (R-Rinf)^+ dt <= (X-k) ln(s(T)/s0) < (X-k) ln(sbar/s0) (300 random spend paths)",
      bad==0, f"max ratio integral/bound = {worst:.4f}")

# ---------------- Prop 1(b): discrete-time budget -------------------------------------
bad = 0
for trial in range(400):
    alpha = rng.uniform(0.2, 0.5)
    G = rng.uniform(0, 0.3); k = rng.uniform(0, 0.5)
    X = k + rng.uniform(0.05, 2.0)
    lam = rng.uniform(0.1, 1.5); sbar = rng.uniform(0.2, 1.0)
    m0v = rng.uniform(0.1, 0.8); s0 = sbar*rng.uniform(0.001, 0.2)
    y = X-k; Rinf = m0v + y*G
    T = int(rng.integers(1, 40))
    s = s0; logsum = 0.0
    for t in range(T):
        sg = rng.uniform(0, 2.0)
        gt = G + lam*(1-s/sbar)*sg**alpha     # period-rate share growth (approx. compounding)
        st1 = s*(1+gt)/(1+G)
        st1 = min(st1, sbar)
        mt = m0v - rng.uniform(0, 0.3) - k*gt  # margins even more favorable than feasible
        Rxt = X*gt + mt
        logsum += math.log1p(max(Rxt - Rinf, 0)/(y*(1+G)))
        s = st1
    if logsum > math.log(sbar/s0) + 1e-9:
        bad += 1
check("P1b  discrete: sum log(1+(R-Rinf)^+/(y(1+G))) <= ln(sbar/s0) (400 random paths)",
      bad==0)

# ---------------- Corollary 1 example numbers (main p.17-18) ------------------------
X, k, m0v, G0, sbar = 1.0, 0.0, 0.6, 0.2, 0.5
Rinf = m0v + (X-k)*G0
y = X-k
# N(1000) bound from s0=0.01
def Tbar(Rbar, s0):
    return math.log(sbar/s0)/math.log(1 + (Rbar-Rinf)/(y*(1+G0)))
check("C1a  example: bound on years at score>=1000 from s0=1% is 1.8 (-> at most 1 year)",
      abs(Tbar(10.0, 0.01) - 1.81) < 0.01, f"{Tbar(10.0,0.01):.3f}")
check("C1a  example: bound on years at score>=140 from s0=1% is 9.6 (-> at most 9)",
      abs(Tbar(1.4, 0.01) - 9.65) < 0.01, f"{Tbar(1.4,0.01):.3f}")
check("C1a  example: bound on years at score>=1000 from s0=1e-5 is 5.0 (-> at most 5)",
      abs(Tbar(10.0, 1e-5) - 5.01) < 0.01, f"{Tbar(10.0,1e-5):.3f}")
# continuous-time bound: (X-k) ln(sbar/s0)/(Rbar-Rinf)
check("C1b  example: continuous time at >=1000 from s0=1%: at most 0.43 years; 0.30 at static optimum",
      abs(y*math.log(sbar/0.01)/(10-Rinf) - 0.4252) < 0.005
      and abs(0.7*y*math.log(sbar/0.01)/(10-Rinf) - 0.2977) < 0.005)

# ---------------- how long can an extreme score actually last? (compare bound vs achievable)
# myopic policy: sigma(t) = sigma*(ell(s), X); R* (s(t)) - Rinf <= bound (S1)
alpha, X, k, m0v, G0, lam, sbar = 0.3, 1.0, 0.0, 0.6, 0.2, 1.2, 0.5
Rinf = m0v + G0
def Dstar(ell): return ell**(1/(1-alpha))*(alpha*(X-k))**(alpha/(1-alpha))
def sigstar(ell): return (alpha*ell*(X-k))**(1/(1-alpha))
s0 = 0.01
def rhs(t, s):
    ell = lam*(1-s/sbar)
    return s*ell*(sigstar(ell)/s and 1)*0 + s*Dstar(ell)*0 + s* (sigstar(ell)**alpha * lam*(1-s/sbar))
sol = solve_ivp(rhs, [0, 60], [s0], rtol=1e-11, atol=1e-13, dense_output=True)
ts = np.linspace(0, 60, 6001)
ss = sol.sol(ts)[0]
Rs = Rinf + (1-alpha)*(X-k)*Dstar(lam*(1-ss/sbar))
# bound (S1)
Dstar0 = Dstar(lam)
q = 1/(1-alpha)
boundS1 = (1-alpha)*alpha**(alpha/(1-alpha))*(lam*(X-k))**q * \
          ((1-s0/sbar)**(-alpha/(1-alpha)) + (alpha/(1-alpha))*Dstar0*(s0/sbar)*ts)**(-1/alpha) \
          if False else (1-alpha)*alpha**(alpha/(1-alpha))*(lam*(X-k))**q * \
          (( (1-s0/sbar)**(-alpha/(1-alpha)) ) + (alpha/(1-alpha))*Dstar0*(s0/sbar)*ts)**(-alpha and 1)
# simpler direct bound: h(t)^(-alpha/(1-alpha)) >= h0^(-alpha/(1-alpha)) + (alpha/(1-alpha)) D*0 s0/sbar t
h0 = 1 - s0/sbar
hnum = h0**(-alpha/(1-alpha)) + (alpha/(1-alpha))*Dstar0*(s0/sbar)*ts
bound = (1-alpha)*alpha**(alpha/(1-alpha))*(lam*(X-k))**q * hnum**(-alpha/1 if False else -1/alpha)
ok = np.all((Rs - Rinf) <= bound + 1e-9)
check("PS1  myopic path: R*(s(t)) - Rinf <= bound (S1) along the ODE (t up to 60)", ok)
# decay rate vs t^{-1/alpha}
tail = (ts > 20)
sl_excess = Rs[tail] - Rinf
tt = ts[tail]
ref = sl_excess[0]*(tt[0]/tt)**(1/alpha*1.0)
# check the excess decays at least as fast as t^{-1/alpha}: compare log slopes
fit = np.polyfit(np.log(tt), np.log(sl_excess), 1)
check("PS1  myopic excess decays at least as fast as t^{-1/alpha} (log-slope <= -1/alpha)",
      fit[0] <= -1/alpha + 1e-3, f"slope={fit[0]:.3f} vs {-1/alpha:.3f}")

# ---------------- Prop S2: sharpness (slow constant-Delta policies) ------------------
alpha, X, k, m0v, G0, lam, sbar = 0.3, 1.0, 0.0, 0.6, 0.2, 1.2, 0.5
y = X-k; Rinf = m0v+y*G0
s0 = 0.01
ratios = []
for Delt in [0.3, 0.1, 0.03, 0.01, 0.003]:
    s1 = 0.9*sbar
    # policy: hold excess growth at Delta until s reaches s1
    def rhs(t, s):
        hnow = 1-s/sbar
        sg = (Delt/(lam*hnow))**(1/alpha)
        return s*Delt
    T1 = math.log(s1/s0)/Delt
    sol = solve_ivp(rhs, [0, T1], [s0], rtol=1e-10, dense_output=True)
    # excess score: y*Delta - sigma(t); sigma = (Delta/(lam h))^(1/alpha)
    def excess(t):
        s = sol.sol(t)[0]; hnow = 1-s/sbar
        return y*Delt - (Delt/(lam*hnow))**(1/alpha)
    integ = solve_ivp(lambda t, z: excess(t), [0, T1], [0.0], rtol=1e-9).y[0][-1]
    ratios.append(integ/(y*math.log(s1/s0)))
check("PS2  sharpness: constant-Delta policies approach the budget (ratio -> 1 as Delta -> 0)",
      ratios[-1] > 0.9 and all(np.diff(ratios) > 0), f"ratios={['%.3f'%r for r in ratios]}")

# ---------------- Remark S1(b): Gi < G grows the budget -------------------------------
bad = 0
for trial in range(200):
    alpha = rng.uniform(0.2, 0.5)
    G = rng.uniform(0.05, 0.3); Gi = G - rng.uniform(0, 0.1)   # retention lags market
    k = rng.uniform(0, 0.5); X = k + rng.uniform(0.05, 2.0)
    lam = rng.uniform(0.1, 1.5); sbar = rng.uniform(0.2, 1.0)
    m0v = rng.uniform(0.1, 0.8); s0 = sbar*rng.uniform(0.005, 0.1)
    y = X-k; Rinf_i = m0v + y*Gi
    T = rng.uniform(2, 20)
    # spend so that g = Gi + Delta with Delta constant (positive excess over own zero-spend growth)
    Delt = rng.uniform(0.01, 0.3)
    def rhs(t, s):
        sg = (Delt/(lam*(1-s/sbar)))**(1/alpha)
        return s*(Gi - G + Delt)     # sdot/s = g - G = Gi + Delta - G
    sol = solve_ivp(rhs, [0, T], [s0], rtol=1e-10, dense_output=True)
    ts = np.linspace(0, T, 2000); ss = sol.sol(ts)[0]
    if ss[-1] > sbar:  # capped
        tc = ts[ss <= sbar]; tsc = ts[:len(tc)]
        ss = ss[:len(tc)]
    else:
        tsc = ts
    sgs = np.array([(Delt/(lam*(1-v/sbar)))**(1/alpha) for v in ss])
    Rx = X*(Gi+Delt) + (m0v - sgs - k*(Gi+Delt))
    integ = np.trapezoid(np.maximum(Rx - Rinf_i, 0), tsc)
    bound = y*(math.log(min(ss[-1],sbar)/s0) + (G-Gi)*tsc[-1]) \
            if ss[-1] < sbar else y*(math.log(sbar/s0) + (G-Gi)*tsc[-1])
    # with cap at sbar the share stays; bound from Remark S1(b): y[ln(s(T)/s0) + (G-Gi)T]
    sT = min(ss[-1], sbar)
    bound_claim = y*(math.log(sT/s0) + (G-Gi)*tsc[-1])
    if integ > bound_claim + 1e-6*max(1,abs(bound_claim)):
        bad += 1
check("RS1b Gi<G: budget (X-k)[ln(s(T)/s0)+(G-Gi)T] holds (200 random paths)", bad==0)

# ---------------- Corollary 2: exact bracket ------------------------------------------
def Rstar_of_k(kk, alpha, G0, X, lam, hh, m0v):
    yv = X-kk
    if yv <= 0: return m0v + yv*G0
    return m0v + yv*G0 + (1-alpha)*yv*(lam*hh)**(1/(1-alpha))*(alpha*yv)**(alpha/(1-alpha))
bad = 0
for _ in range(300):
    alpha = rng.uniform(0.2, 0.5); G0 = rng.uniform(0, 0.3)
    X = rng.uniform(0.5, 3.0); lam = rng.uniform(0.1, 2.0); hh = rng.uniform(0.1, 1.0)
    m0v = 0.5; k0 = rng.uniform(0, min(X-0.01, 1.0))
    da = rng.uniform(0, 0.2); dk = rng.uniform(0.001, 0.3)
    dR = (Rstar_of_k(k0+dk, alpha, G0, X, lam, hh, m0v-da*0) - 0)  # placeholder
    # actual: da lowers a -> raises m0 by da; dk raises k
    R0 = Rstar_of_k(k0, alpha, G0, X, lam, hh, m0v)
    R1 = Rstar_of_k(k0+dk, alpha, G0, X, lam, hh, m0v)
    dRstar = da + (R1 - R0)
    g_lo = G0 + ( (lam*hh)**(1/(1-alpha)) * (alpha*(X-k0))**(alpha/(1-alpha)) if X>k0 else 0)
    g_hi = G0 + ( (lam*hh)**(1/(1-alpha)) * (alpha*(X-k0-dk))**(alpha/(1-alpha)) if X>k0+dk else 0)
    # paper's bracket: da - g*(k)*dk <= dR* <= da - g*(k+dk)*dk
    # (g_lo = g*(k) >= g_hi = g*(k+dk), so da - g_lo*dk <= da - g_hi*dk)
    if not (da - g_lo*dk <= dRstar + 1e-12 and dRstar <= da - g_hi*dk + 1e-12):
        bad += 1
check("C2   capital-for-labor bracket da - g*(k+dk)dk <= dR* <= da - g*(k)dk (300 draws)", bad==0)

print()
nf = sum(1 for _, ok in results if not ok)
print(f"TOTAL {len(results)} checks, {nf} failures")
sys.exit(1 if nf else 0)