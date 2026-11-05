"""Continuous-time budget counterexample hunt: Prop budget(a) claims
 int_0^T (R_X - Rinf)^+ dt <= y ln(s(T)/s0) for ANY feasible path with g >= G, m <= m0 - sig - k g.
Since R - Rinf = y*Delta - sig + (m - (m0 - sig - k g))... precisely R = Xg + m, Rinf = m0 + y G.
R - Rinf = X(G+D) + m - m0 - yG = y D + (m - m0 + ... ) wait: XG +XD + m - m0 - yG = kG + XD + m - m0 (since X = y+k, XG - yG = kG).
With m <= m0 - sig - k(G+D): R - Rinf <= kG + XD - sig - kG - kD = yD - sig <= yD.
And int D dt = ln(s(T)/s0) - 0 (since ds/s = (g-G)dt = D dt). So bound holds. Sharp as sig->0. Confirmed analytically.
Test numerically on random feasible paths."""
import numpy as np
rng = np.random.default_rng(42)
worst = -np.inf
for trial in range(2000):
    y = rng.uniform(0.1, 5); G = rng.uniform(0.0, 0.4); k = rng.uniform(0, 1)
    X = y + k; m0 = rng.uniform(0.2, 0.9); sbar = rng.uniform(0.3, 1.0)
    s0 = rng.uniform(1e-4, sbar*0.5)
    T = rng.uniform(0.5, 8)
    N = 20000; ts = np.linspace(0, T, N)
    sig = rng.uniform(0, 3, N)  # arbitrary measurable spend path
    lam = rng.uniform(0.05, 3); a = rng.uniform(0.2, 0.8)
    # share path: ds/dt = s * lam*(1-s/sbar)*sig^a
    D = np.zeros(N); s = np.zeros(N); s[0] = s0
    for i in range(N-1):
        d = lam*(1-s[i]/sbar)*sig[i]**a
        s[i+1] = s[i] + s[i]*d*(ts[i+1]-ts[i])
        D[i] = d
    s[-1] = s[-2] + s[-2]*(lam*(1-s[-2]/sbar)*sig[-1]**a)*(ts[-1]-ts[-2])
    D[-1] = lam*(1-s[-2]/sbar)*sig[-1]**a
    if s.max() > sbar:  # cap
        pass
    m = m0 - sig - k*(G + D)  # frontier margin (max allowed)
    R = X*(G+D) + m
    Rinf = m0 + y*G
    lhs = np.trapezoid(np.maximum(R - Rinf, 0), ts)
    rhs = y*np.log(min(s[-1], sbar)/s0)
    if rhs > 0:
        worst = max(worst, lhs - rhs)
print('max (lhs - rhs) over 2000 random feasible paths:', worst, '(must be <= ~0 up to discretization)')
