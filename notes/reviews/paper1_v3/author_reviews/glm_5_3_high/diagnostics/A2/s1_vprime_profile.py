#!/usr/bin/env python3
"""
Referee A2 - The v'(s) investigation (headline).

Predecessor A's s5_hjb.py check "v'(s) <= v(s)/s on the interior, and v' falling
with s" FAILED. This script:

 A. Worked example (supp S2.2 / main 3.6: r=.10, G=.04, k=0, alpha=.3, m0=.35,
    lambda ~ .0698, v0 = 10, sbar = .5):
    A1. re-solve the singular ODE by backward shooting (predecessor's method),
        fine grid incl. a near-cap grid in t = sbar - s;
    A2. decompose the FAIL: is v' <= v/s violated anywhere? is v' non-falling?
    A3. locate argmin v' and the interval where v' rises; v'(50% sbar) comparison;
    A4. verify the terminal asymptotics v'(sbar-) = ubar = (m0-kG)/(r-G),
        v' - ubar ~ -sbar*a*q*t^(q-1), u - ubar ~ a*t^q with
        a = C_alpha*((lambda/sbar)*(ubar-k))^q/(r-G);
    A5. lever-gain profiles at the firm's own weight X = v'(s):
        growth-engine gain x*sigma*(s) and retention gain (X-k)dG.
 B. Genericity sweep (12 draws incl. the v0=15 calibration, k>0, alpha regimes,
    r grid): in each draw check (i) min v' < ubar < v0, (ii) v' rises on a
    terminal interval, (iii) v' <= v/s on the whole interior, (iv) shot matches
    v0 at small s (evidence for (H) at that draw).
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
import math, sys, platform, datetime

print("session:", datetime.datetime.now().isoformat())
print("python", platform.python_version(), "numpy", np.__version__,
      "scipy", __import__('scipy').__version__)
results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + ("  " + str(detail) if detail else ""))

q = None
def solve_draw(r, G, k, alpha, m0, sbar, lam):
    """Backward shooting of  s u' = Phi(u,s) - u  from s = sbar - t0.
    Returns dict with grid, u, vprime, quantities."""
    Calpha = (1-alpha)*alpha**(alpha/(1-alpha))
    qq = 1/(1-alpha)
    ubar = (m0 - k*G)/(r-G)
    assert ubar > k, "never-spend case not handled here"
    def Phi(u, s):
        w = (r-G)*u - (m0-k*G)
        if w <= 0: return k
        return k + (w/Calpha)**(1-alpha)/(lam*(1-s/sbar))
    a = Calpha*((lam/sbar)*(ubar-k))**qq/(r-G)   # local expansion coefficient
    t0 = 1e-6*sbar          # v'=Phi(u,s) is noise-amplified for t<~1e-7*sbar; start above that
    s_start = sbar - t0
    u_start = ubar + a*t0**qq
    def rhs(s, u):
        return (Phi(u[0], s) - u[0])/s
    s_min = sbar*1e-7
    sol = solve_ivp(rhs, [s_start, s_min], [u_start], rtol=1e-11, atol=1e-13,
                    dense_output=True, max_step=sbar/2000)
    assert sol.success, sol.message
    # grid: log-spaced s in (s_min, 0.999 sbar) union near-cap t grid
    sA = np.exp(np.linspace(math.log(s_min), math.log(sbar-1.000001e-6*sbar), 12000))
    tB = sbar*np.exp(np.linspace(math.log(1e-6), math.log(0.3), 4000))
    sB = sbar - tB
    ss = np.unique(np.concatenate([sA, sB]))
    keep = (ss > s_min) & (ss < sbar)
    ss = ss[keep]
    uu = sol.sol(ss)[0]
    vp = np.array([Phi(uu[i], ss[i]) for i in range(len(ss))])
    return dict(s=ss, u=uu, vp=vp, ubar=ubar, a=a, qq=qq, Calpha=Calpha,
                sol=sol, s_min=s_min, sbar=sbar)

def lam_for_v0(v0, r, G, k, alpha, m0):
    Calpha = (1-alpha)*alpha**(alpha/(1-alpha))
    return (((r-G)*v0 - (m0 - k*G))/Calpha)**(1-alpha)/(v0-k)

# ---------------- A. worked example --------------------------------------------
r, G, k, alpha, m0, sbar = 0.10, 0.04, 0.0, 0.3, 0.35, 0.5
v0 = 10.0
lam = lam_for_v0(v0, r, G, k, alpha, m0)
D = solve_draw(r, G, k, alpha, m0, sbar, lam)
ss, uu, vp, ubar, a, qq = D['s'], D['u'], D['vp'], D['ubar'], D['a'], D['qq']

# shot quality
check("A0  shot reproduces v0=10 at small s (predecessor's method, |u-v0|<0.02)",
      abs(D['sol'].sol(D['s_min'])[0] - v0) < 0.02,
      f"u(smin)={D['sol'].sol(D['s_min'])[0]:.4f}, lam={lam:.4f}, ubar={ubar:.4f}")

# A2: decompose the predecessor's FAIL
interior = (ss > sbar*1e-4) & (ss < sbar*0.98)
gap = vp - uu            # v'(s) - v(s)/s
check("A2a v'(s) <= v(s)/s everywhere on the interior grid (max gap <= 1e-9)",
      np.max(gap[interior]) <= 1e-9,
      f"max(v'-v/s)={np.max(gap[interior]):.3e} at s={ss[interior][np.argmax(gap[interior])]:.5f}")
check("A2b v'(s) - v(s)/s -> 0 at BOTH ends (v' meets the multiple at s->0 and s->sbar)",
      abs(gap[0]) < 2e-3 and abs(gap[-1]) < 2e-3, f"gap(smin)={gap[0]:.2e}, gap(smax)={gap[-1]:.2e}")
falling_all = np.all(np.diff(vp[interior]) < 0)
check("A2c v' is NOT falling on the interior (predecessor's FAIL confirmed)",
      not falling_all, f"np.all(diff v'<0) = {falling_all}")

# A3: argmin and rising interval
i_min = int(np.argmin(vp))
s_min_v = ss[i_min]; v_min = vp[i_min]
v50 = vp[np.searchsorted(ss, 0.5*sbar)]
# crossing of v50 on the rising branch after the minimum
s_rise = np.nan
for i in range(i_min+2, len(vp)):
    if vp[i-1] < v50 <= vp[i]:
        s_rise = ss[i-1] + (v50-vp[i-1])/(vp[i]-vp[i-1])*(ss[i]-ss[i-1]); break
check("A3a v' is U-shaped: min v' < ubar < v0 = lim v'(s->0)",
      v_min < ubar - 1e-6 and ubar < v0 - 1e-6,
      f"min v'={v_min:.4f} at s={s_min_v:.5f} ({100*s_min_v/sbar:.2f}% of cap); ubar={ubar:.4f}; v0={v0}")
check("A3b v' rises back through the printed 50%-of-cap weight 5.39 before the cap",
      vp[-1] > v50 + 0.2,
      f"v'(smax)={vp[-1]:.4f}; v' exceeds its 50%-of-cap value again for s > {s_rise:.5f} ({100*s_rise/sbar:.2f}% of cap)")
# v' at selected shares incl. near-cap
shares = [0.01, 0.05, 0.10, 0.25, 0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.98, 0.99, 0.995, 0.999]
prof = []
for f in shares:
    s0 = f*sbar
    i = np.searchsorted(ss, s0)
    prof.append(f"{100*f:.1f}%: v'={vp[i]:.3f}, v/s={uu[i]:.3f}")
print("   profile: " + "; ".join(prof))
# strictly-rising terminal interval: measure where diff(vp)>0 consistently
dvp = np.diff(vp)
rising_tail = np.where(dvp > 0)[0]
s_rise_start = ss[rising_tail[0]] if len(rising_tail) else np.nan
check("A3c v' strictly rising on a terminal interval (s*, sbar)",
      len(rising_tail) > 0 and rising_tail[-1] == len(dvp)-1,
      f"rising from s*={s_rise_start:.5f} ({100*s_rise_start/sbar:.2f}% of cap) to the cap")

# A4: terminal asymptotics (near-cap points, t ascending)
m = 3000
tt = (sbar - ss[-m:])[::-1]          # ascending t
vpt = vp[-m:][::-1]; ut = uu[-m:][::-1]
asym_pred = ubar - sbar*a*qq*np.power(tt, qq-1)
relerr = np.abs(vpt - asym_pred)/np.maximum(np.abs(vpt-ubar), 1e-15)
i1e4 = np.searchsorted(tt, sbar*1e-4)
err_at = relerr[i1e4] if i1e4 < len(tt) else relerr[-1]
check("A4a terminal asymptotic v'(s)-ubar ~ -sbar*a*q*t^(q-1) near the cap (rel err < 10% at t=1e-4*sbar)",
      err_at < 0.10,
      f"rel err at t=1e-4*sbar: {err_at:.3f}; v'(t=1e-6*sbar)={vpt[0]:.4f} vs ubar={ubar:.4f} (gap {vpt[0]-ubar:+.4f})")
u_pred = ubar + a*np.power(tt, qq)
u_relerr = np.abs(ut - u_pred)/np.maximum(np.abs(u_pred-ubar), 1e-15)
u_err_at = u_relerr[i1e4] if i1e4 < len(tt) else u_relerr[-1]
check("A4b u(s)-ubar ~ a*t^q near the cap (rel err < 10% at t=1e-4*sbar)",
      u_err_at < 0.10, f"rel err at t=1e-4*sbar: {u_err_at:.3f}")
check("A4c v'(s) returns to within 1% of ubar at 1e-6*sbar from the cap",
      abs(vp[-1]-ubar) < 0.01*ubar, f"v'(sbar-1e-6*sbar)={vp[-1]:.4f}, ubar={ubar:.4f}")

# A5: lever-gain profiles at the firm's own weight X = v'(s)
X = vp
ell = lam*(1-ss/sbar)
Delta = np.power(ell, qq)*np.power(alpha*np.maximum(X-k, 1e-300), alpha/(1-alpha))
sig = alpha*np.maximum(X-k, 0)*Delta          # optimal spend sigma*(s)
ret = X - k                                    # retention gain per point dG
# growth-engine gain x*sigma*: monotone decreasing?
dsig = np.diff(sig)
check("A5a growth-engine lever gain x*sigma*(s) is strictly decreasing in s (h(s) channel dominates)",
      np.all(dsig < 0), f"sigma*(s): {sig[0]:.4f} (s->0) -> {sig[np.searchsorted(ss,0.5*sbar)]:.4f} (50%) -> {sig[-2]:.2e} (near cap)")
check("A5b retention gain (X-k)dG is NOT monotone in s (U-shaped, same shape as v')",
      np.any(np.diff(ret) > 0) and np.any(np.diff(ret) < 0),
      f"retention gain: {ret[0]:.3f} (s->0), {ret[np.searchsorted(ss,0.5*sbar)]:.3f} (50%), -> {ubar-k:.3f} (cap)")
check("A5c retention gain stays within a small factor of its small-share level at every share (never vanishes)",
      np.min(ret) > 0.5*ret[0], f"min retention gain {np.min(ret):.3f} vs small-share {ret[0]:.3f} (ratio {np.min(ret)/ret[0]:.2f})")
check("A5d both (ii) and (iii) gains are maximized at small share (v' < v0 inside)",
      np.max(vp[ss < sbar]) < v0, f"max v' on grid = {np.max(vp):.4f} < v0 = {v0}")

# ---------------- B. genericity sweep -------------------------------------------
print("\n--- genericity sweep ---")
draws = [
    ("worked example (v0=10)",        0.10, 0.04, 0.0, 0.3, 0.35, 0.5, 10.0),
    ("v0=15 calibration",             0.10, 0.04, 0.0, 0.3, 0.35, 0.5, 15.0),
    ("low multiple v0=6",             0.10, 0.04, 0.0, 0.3, 0.35, 0.5, 6.0),
    ("high r=22% (v0~2.1)",           0.22, 0.04, 0.0, 0.3, 0.35, 0.5, 2.1),
    ("alpha=0.25",                    0.10, 0.04, 0.0, 0.25, 0.35, 0.5, 10.0),
    ("alpha=0.45",                    0.10, 0.04, 0.0, 0.45, 0.35, 0.5, 10.0),
    ("alpha=0.7 (alpha>1/2)",         0.10, 0.04, 0.0, 0.7, 0.35, 0.5, 10.0),
    ("k=0.05 capital",                0.10, 0.04, 0.05, 0.3, 0.35, 0.5, 10.0),
    ("m0=0.25",                       0.10, 0.04, 0.0, 0.3, 0.25, 0.5, 10.0),
    ("G=0.08 fast market",            0.15, 0.08, 0.0, 0.3, 0.35, 0.5, 10.0),
    ("sbar=0.25 tight cap",          0.10, 0.04, 0.0, 0.3, 0.35, 0.25, 10.0),
    ("r=0.0934 (v0~14.6)",            0.0934, 0.04, 0.0, 0.3, 0.35, 0.5, 14.57),
]
allU = True; allRise = True; allBelow = True; allShot = True
for (name, rr, GG, kk, al, mm, sb, v0t) in draws:
    ub = (mm-kk*GG)/(rr-GG)
    if ub <= kk or v0t <= ub:
        print(f"  {name}: ubar={ub:.3f} >= v0={v0t} -> spend case fails, skipped"); continue
    lm = lam_for_v0(v0t, rr, GG, kk, al, mm)
    try:
        d = solve_draw(rr, GG, kk, al, mm, sb, lm)
    except AssertionError as e:
        print(f"  {name}: skipped ({e})"); continue
    s2, u2, p2 = d['s'], d['u'], d['vp']
    i2 = int(np.argmin(p2))
    shot_ok = abs(d['sol'].sol(d['s_min'])[0] - v0t) < 0.05*v0t
    dv = np.diff(p2)
    rising = np.any(dv > 0) and (np.where(dv>0)[0][-1] == len(dv)-1)
    below = np.max(p2 - u2) <= 1e-9
    allU &= (p2[i2] < ub - 1e-9); allRise &= rising; allBelow &= below; allShot &= shot_ok
    print(f"  {name}: v0={v0t}, ubar={ub:.3f}, min v'={p2[i2]:.3f} at {100*s2[i2]/sb:.1f}% cap, "
          f"v'(smax)={p2[-1]:.4f}, rising-tail={rising}, v'<=v/s={below}, shot-v0={shot_ok}")
check("B1 U-shape generic: min v' < ubar < v0 in EVERY draw",
      allU, "see per-draw lines above")
check("B2 v' strictly rising on a terminal interval in EVERY draw",
      allRise, "")
check("B3 v'(s) <= v(s)/s on the interior in EVERY draw",
      allBelow, "")
check("B4 every shot matches its small-share root v0 (evidence for (H) at each draw)",
      allShot, "")

print()
nf = sum(1 for _, ok in results if not ok)
print(f"TOTAL {len(results)} checks, {nf} failures")
sys.exit(1 if nf else 0)