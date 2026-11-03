"""Mistral F-6 check: does any simple admissible spend policy beat the no-spend value v/s = m0/(r-G) = 5.83?
If one does, the no-spend solution cannot be optimal, so a solver that converges to it is wrong for this problem.
Worked example of Section S2.2: r=0.10, G=0.04, k=0, alpha=0.3, m0=0.35, sbar=0.5, lambda set so v0=10.
Dynamics: ds/dt = s*D, D = lam*(1-s/sbar)*sig^alpha; flow per unit of initial market = s*(m0 - sig), discounted at r-G."""
import numpy as np
a, G, k, m0, r, sbar = 0.3, 0.04, 0.0, 0.35, 0.10, 0.5
Ca = (1 - a) * a ** (a / (1 - a))
lam = (((r - G) * 10.0 - (m0 - k * G)) / Ca) ** (1 - a) / (10.0 - k)
def payoff(s0, sig, s_stop, T=400.0, dt=0.002):
    s, t, V = s0, 0.0, 0.0
    while t < T:
        sg = sig if s < s_stop else 0.0
        D = lam * (1 - s / sbar) * sg ** a
        V += np.exp(-(r - G) * t) * s * (m0 - sg) * dt
        s += s * D * dt; t += dt
    V += np.exp(-(r - G) * t) * s * m0 / (r - G)       # tail: no spend after T
    return V
print('lambda', round(lam, 5), '| no-spend v/s', round(m0 / (r - G), 4))
for s0 in (0.01, 0.1):
    best = max(((payoff(s0, sg, st) / s0, sg, st) for sg in (0.05, 0.1, 0.2, 0.3) for st in (0.2, 0.3, 0.4)), key=lambda x: x[0])
    print(f's0={s0}: best simple policy v/s = {best[0]:.3f} (spend {best[1]} of revenue until share {best[2]})')
