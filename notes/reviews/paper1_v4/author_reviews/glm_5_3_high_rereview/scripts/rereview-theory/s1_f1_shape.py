#!/usr/bin/env python3
"""A2 round-2: verify every number in the six corrected v'-shape sentences,
against the NEW repo's solve_hjb (copied verbatim), computing v' BOTH ways:
(np.gradient as in the new verify_theory 15g-15p) and (exact Phi from the ODE).
Also adjudicate the acceptance-test dispute:
  round-1 (mine):   v'(0.95 sbar) > v'(0.5 sbar)   and  v'(0.99 sbar) within 1% of ulim
  author's (new):   v'(0.99 sbar) > v'(0.5 sbar)   and  v'(0.9999 sbar) within 1% of ulim
"""
import numpy as np
from scipy.optimize import minimize_scalar
import platform, datetime
print("session:", datetime.datetime.now().isoformat())
print("python", platform.python_version(), "numpy", np.__version__)

r_, G_, k_, a_, m0_ = 0.10, 0.04, 0.0, 0.3, 0.35
Ca = (1 - a_) * a_ ** (a_ / (1 - a_))
lam_for = lambda v0: (((r_ - G_) * v0 - (m0_ - k_ * G_)) / Ca) ** (1 - a_) / (v0 - k_)
lam10 = lam_for(10.0)
sbar_ = 0.5
ulim = (m0_ - k_ * G_) / (r_ - G_)

def solve_hjb(m0_, k_, G_, r_, lam_, a_, sbar_, N=4000, smin=1e-9):
    half = N // 2
    u = np.concatenate([np.geomspace(smin, 0.5, half, endpoint=False), 1 - np.geomspace(0.5, 1e-9, N - half)])
    s = sbar_ * u
    v = np.zeros(N); sig = np.zeros(N)
    v[-1] = s[-1] * (m0_ - k_ * G_) / (r_ - G_)
    grid = np.concatenate([[0.0], np.geomspace(1e-10, 50, 240)])
    for i in range(N - 2, -1, -1):
        ell_i = lam_ * (1 - s[i] / sbar_)
        ds = s[i + 1] - s[i]
        def val(sg):
            D_ = ell_i * sg**a_
            ai = s[i] * D_ / ds
            return (s[i] * (m0_ - sg - k_ * (G_ + D_)) + ai * v[i + 1]) / ((r_ - G_) + ai)
        vals = np.array([val(x) for x in grid])
        j = int(np.argmax(vals))
        lo, hi = grid[max(j - 1, 0)], grid[min(j + 1, len(grid) - 1)]
        res = minimize_scalar(lambda x: -val(x), bounds=(lo, hi), method="bounded", options={"xatol": 1e-13})
        if -res.fun >= vals[j]:
            v[i], sig[i] = -res.fun, res.x
        else:
            v[i], sig[i] = vals[j], grid[j]
    return s, v, sig

s_h, v_h, sig_h = solve_hjb(m0_, k_, G_, r_, lam10, a_, sbar_, N=4000)
vp_grad = np.gradient(v_h, s_h)                      # author's method
def Phi(u, s):
    w = (r_ - G_) * u - (m0_ - k_ * G_)
    if w <= 0: return k_
    return k_ + (w / Ca) ** (1 - a_) / (lam10 * (1 - s / sbar_))
vp_phi = np.array([Phi(v_h[i]/s_h[i], s_h[i]) for i in range(len(s_h))])  # my method
z = s_h / sbar_
atg = lambda zz: float(np.interp(zz, z, vp_grad))
atp = lambda zz: float(np.interp(zz, z, vp_phi))
sig_at = lambda zz: float(np.interp(zz, z, sig_h))

print(f"\nworked example: lam={lam10:.4f}, v0=10, never-spend multiple ulim={ulim:.4f}")
print(f"{'s/sbar':>8} {'v\' (grad)':>10} {'v\' (Phi)':>10} {'v/s':>7}")
for f in [0.01, 0.10, 0.50, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.98, 0.99, 0.995, 0.999, 0.9999]:
    print(f"{f:8.4f} {atg(f):10.4f} {atp(f):10.4f} {float(np.interp(f, z, v_h/s_h)):7.4f}")
msk = (z > 0.02) & (z < 0.9999)
for name, vp in [("grad", vp_grad), ("Phi", vp_phi)]:
    i_min = int(np.argmin(np.where(msk, vp, np.inf)))
    print(f"\n[{name}] min v' = {vp[i_min]:.4f} at {100*z[i_min]:.2f}% of cap; "
          f"ratio to 1% value: {vp[i_min]/at(0.01) if False else vp[i_min]/ (np.interp(0.01,z,vp)):.4f}")
print(f"\nSENTENCE NUMBERS (supp S2.2 p.6; main 3.6 p.23):")
print(f"  9.1 / 7.2 / 5.4 at 1/10/50%:      grad {atg(0.01):.2f}/{atg(0.1):.2f}/{atg(0.5):.2f}  Phi {atp(0.01):.2f}/{atp(0.1):.2f}/{atp(0.5):.2f}")
print(f"  'about 5.1 near 80%':             grad {atg(0.80):.3f}  Phi {atp(0.80):.3f}")
print(f"  'rises toward 5.8 (never-spend)': ulim = {ulim:.4f}; v'(0.9999) grad {atg(0.9999):.3f} Phi {atp(0.9999):.3f}")
print(f"  macro claims (15p): min 5.08 at 80%; VpSatHi 5.70 at 99.9%; VpNinetyNine 5.50; VpFourNines 5.78")
print(f"    grad: min {np.min(np.where(msk, vp_grad, np.inf)):.4f}, at 99.9% {atg(0.999):.3f}, at 99% {atg(0.99):.3f}, at 99.99% {atg(0.9999):.3f}")
print(f"    Phi:  min {np.min(np.where(msk, vp_phi, np.inf)):.4f}, at 99.9% {atp(0.999):.3f}, at 99% {atp(0.99):.3f}, at 99.99% {atp(0.9999):.3f}")
print(f"\nRETENTION RATIO (main 3.5 p.21 'still about 56% of its small-share value'):")
i_min = int(np.argmin(np.where(msk, vp_grad, np.inf)))
print(f"  at the minimum: v'-k = {vp_grad[i_min]-k_:.3f} vs 1% value {atg(0.01)-k_:.3f} -> ratio {100*(vp_grad[i_min]-k_)/(atg(0.01)-k_):.1f}%")
print(f"  near saturation (0.9999): {atg(0.9999)-k_:.3f} -> ratio {100*(atg(0.9999)-k_)/(atg(0.01)-k_):.1f}%")
print(f"  vs small-share limit v0=10: {100*ulim/10:.1f}%")
print(f"  15o's own claim: >= half from min to 99.9%: min ratio {100*(vp_grad[i_min]-k_)/(atg(0.01)-k_):.1f}% >= 50%: "
      f"{(vp_grad[i_min]-k_) > 0.5*(atg(0.01)-k_)}; sigma(0.95)={sig_at(0.95):.4f} < 0.1*sigma(0.01)={0.1*sig_at(0.01):.4f}: {sig_at(0.95) < 0.1*sig_at(0.01)}")
print(f"\nACCEPTANCE-TEST DISPUTE:")
print(f"  MY round-1 test (i):  v'(0.95) > v'(0.5)?     grad: {atg(0.95):.4f} > {atg(0.5):.4f} -> {atg(0.95) > atg(0.5)}   "
      f"(Phi: {atp(0.95):.4f} > {atp(0.5):.4f} -> {atp(0.95) > atp(0.5)})")
print(f"  MY round-1 test (ii): v'(0.99) within 1% of ulim? grad: |{atg(0.99):.4f}-{ulim:.4f}|/{ulim:.4f} = {100*abs(atg(0.99)-ulim)/ulim:.2f}% -> {abs(atg(0.99)-ulim)/ulim < 0.01}")
print(f"  AUTHOR's 15l: v'(0.99) > v'(0.5)?    grad: {atg(0.99):.4f} > {atg(0.5):.4f} -> {atg(0.99) > atg(0.5)}   "
      f"(Phi: {atp(0.99):.4f} > {atp(0.5):.4f} -> {atp(0.99) > atp(0.5)})")
print(f"  AUTHOR's 15m: v'(0.9999) within 1% of ulim? grad: {100*abs(atg(0.9999)-ulim)/ulim:.3f}% -> {abs(atg(0.9999)-ulim)/ulim < 0.01}   "
      f"(Phi: {100*abs(atp(0.9999)-ulim)/ulim:.3f}%)")
print(f"  15n: interior min below limit, 70-90% of cap: grad min {np.min(np.where(msk, vp_grad, np.inf)):.4f} at {100*z[i_min]:.1f}% -> "
      f"{(vp_grad[i_min] < ulim) and (0.7 < z[i_min] < 0.9)}")
gap = (vp_grad - v_h/s_h)[msk]
print(f"  15n second part: v' < v/s at every share (z in 0.02-0.9999): max gap {gap.max():.4f} -> {gap.max() < 0}")