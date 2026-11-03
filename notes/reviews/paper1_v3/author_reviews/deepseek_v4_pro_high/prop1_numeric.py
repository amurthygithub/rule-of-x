"""
Independent verification of Proposition 1 (score budget), Corollary 1 example numbers,
and sharpness (Proposition S2).  Numeric via numpy/scipy.  Not the author's script.
"""
import numpy as np

# ---- Proposition 1(b) discrete bound and Corollary 1(a) example numbers ----
# X=1, k=0, m0=0.6, G=0.2  => Rinf = m0 + (X-k)G = 0.8, y = X-k = 1, sbar=0.5
X, k, m0, G = 1.0, 0.0, 0.6, 0.2
Rinf = m0 + (X-k)*G
y = X - k
sbar = 0.5
oneG = 1 + G
print("Rinf =", Rinf, " y =", y, " 1+G =", oneG)

def disc_bound(Rbar, s0):
    return np.log(sbar/s0) / np.log(1 + (Rbar - Rinf)/(y*oneG))

for Rbar, s0, name in [(10.0, 0.01, "1000pts from 1%"),
                        (1.4, 0.01, "140pts from 1%"),
                        (10.0, 1e-5, "1000pts from 1e-5")]:
    b = disc_bound(Rbar, s0)
    print(f"{name}: Rbar={Rbar}, s0={s0}, T(Rbar)<= {b:.3f}  -> floor {int(np.floor(b))}")

# ---- Continuous-time Corollary 1(b): (X-k) ln(sbar/s0)/(Rbar-Rinf) ----
s0 = 0.01
ct = y*np.log(sbar/s0)/(10.0 - Rinf)
ct_static = (1-0.3)*ct
print(f"\nContinuous time from 1% for 1000pts: {ct:.4f} yrs; static-optimum {ct_static:.4f} yrs")

# ---- Pointwise bound R_X <= Rinf + y*Delta - sigma <= Rinf + y*Delta ----
# Simulate a feasible path: choose sigma(t), compute g, m, R_X, verify integral bound.
# Use growth technology (1): g = G + lam*h(s) sigma^alpha, h = 1-s/sbar.
alpha = 0.3
lam = 1.2
sbar = 0.5
s0 = 0.01

def simulate(sigma_of_t, T, dt=1e-4):
    t = np.arange(0, T, dt)
    s = s0
    s_path = [s0]
    integ_pos = 0.0
    integ_yDelta = 0.0
    for i in range(len(t)-1):
        sig = sigma_of_t(t[i], s)
        h = 1 - s/sbar
        Delta = lam*h*sig**alpha
        g = G + Delta
        m = m0 - sig - k*g          # frontier margin (top of feasible set)
        RX = X*g + m
        excess = RX - Rinf
        integ_pos += max(excess, 0.0)*dt
        integ_yDelta += y*Delta*dt
        s = s + s*Delta*dt
        s_path.append(s)
    return np.array(s_path), integ_pos, integ_yDelta

# Case 1: static optimum spend for X=1 at every date (myopic) - should satisfy bound.
def sigma_static(t, s):
    h = 1 - s/sbar
    ell = lam*h
    return (alpha*ell*y)**(1/(1-alpha))   # sigma* = (alpha*ell*(X-k))^(1/(1-alpha))

T = 60.0
s_path, Ipos, IyD = simulate(sigma_static, T)
print(f"\nMyopic static-optimum path: integral (R_X-Rinf)^+ = {Ipos:.4f}, "
      f"integral y*Delta = {IyD:.4f}, y*ln(s(T)/s0) = {y*np.log(s_path[-1]/s0):.4f}, "
      f"y*ln(sbar/s0) = {y*np.log(sbar/s0):.4f}")
print(f"  Bound holds: {Ipos <= IyD <= y*np.log(sbar/s0)}")

# Case 2: adversarial - push spend very high briefly (fast conversion). Bound must still hold.
def sigma_fast(t, s):
    return 100.0 if t < 0.5 else 0.0
s_path2, Ipos2, IyD2 = simulate(sigma_fast, 10.0)
print(f"\nFast-spend path: integral (R_X-Rinf)^+ = {Ipos2:.4f}, y*ln(s(T)/s0) = {y*np.log(s_path2[-1]/s0):.4f}")
print(f"  Bound holds: {Ipos2 <= y*np.log(sbar/s0)} = {Ipos2 <= y*np.log(sbar/s0)}")

# ---- Sharpness: slow constant excess growth Delta -> 0, s1 -> sbar (Prop S2) ----
def slow_spend(Delta, s1, s0, sbar, lam, alpha, y):
    # hold excess growth Delta until s reaches s1; spend sigma=(Delta/(lam h(s)))^(1/alpha)
    T1 = np.log(s1/s0)/Delta
    sigma_bar1 = (Delta/(lam*(1-s1/sbar)))**(1/alpha)
    lower = y*np.log(s1/s0)*(1 - sigma_bar1/(y*Delta))
    return T1, sigma_bar1, lower

print("\nSharpness (slow Delta -> 0, s1 -> sbar):")
for Delta in [0.02, 0.005, 0.001]:
    T1, sb1, lower = slow_spend(Delta, 0.49, 0.01, 0.5, 1.2, 0.3, 1.0)
    print(f"  Delta={Delta:.3f}: T1={T1:.1f}, sigma_bar1={sb1:.4f}, "
          f"lower bound on integral = {lower:.4f} (target y ln(s1/s0)={y*np.log(0.49/0.01):.4f})")
