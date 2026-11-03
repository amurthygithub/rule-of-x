import numpy as np
from scipy.optimize import minimize_scalar
def Dstar(l, y, a): return l**(1/(1-a)) * (a*y)**(a/(1-a))
def Rstar(m0, G, l, a, k=0.0, X=1.0):
    y = X-k
    if y <= 0: return m0 + y*G, G
    D = Dstar(l, y, a); return m0 + y*G + (1-a)*y*D, G + D
print("== 1b. recheck closed form with adaptive bound")
rng = np.random.default_rng(0); bad = 0; worst = 0
for _ in range(3000):
    a = rng.uniform(0.1, 0.9); l = rng.uniform(0.05, 3); m0 = rng.uniform(0, .8)
    G = rng.uniform(-.1, .4); k = rng.uniform(0, 2); X = rng.uniform(0, 4); y = X-k
    ss = (a*l*max(y,1e-9))**(1/(1-a)); ub = max(10*ss, 1.0)
    f = lambda s: -(X*(G + l*s**a) + m0 - s - k*(G + l*s**a))
    res = minimize_scalar(f, bounds=(0, ub), method='bounded', options={'xatol': 1e-14})
    num = max(-res.fun, -f(0.0)); cf = Rstar(m0, G, l, a, k, X)[0]
    e = abs(num-cf)/max(1, abs(cf)); worst = max(worst, e); bad += e > 1e-6
print("violations:", bad, "worst rel err:", worst)

print("\n== 2b. Table calib sensitivity to alpha (exceptional, k=0); and typical-pull firm's sigma*")
rows = {'2025': (0.28, 0.10, 1.0, 0.28, 0.10, 1.5), '2028': (0.30, 0.10, 1.5, 0.40, 0.20, 2.5),
        '2031': (0.40, 0.08, 1.0, 0.55, 0.20, 2.0), '2036': (0.45, 0.05, 0.5, 0.64, 0.30, 1.5)}
for a in (0.20, 0.25, 0.30, 0.43):
    s = []
    for h, (m0l, Gl, ll, m0h, Gh, lh) in rows.items():
        s.append(f"{h}: {100*Rstar(m0l,Gl,ll,a)[0]:.0f}-{100*Rstar(m0h,Gh,lh,a)[0]:.0f}")
    print(f"  alpha={a}: " + "; ".join(s))
for a in (0.20, 0.25, 0.43):
    D = Dstar(0.25, 1, a); print(f"  typical lam_h=.25, alpha={a}: Delta*={D:.3f}, sigma*={a*D:.3f} (vs S&M ~0.35); "
                                 f"growth at sigma=.35: {0.25*0.35**a:.3f}; score gain from cutting to sigma*: "
                                 f"{100*((a and (1-a)*D) - (0.25*0.35**a - 0.35)):.1f} pts")
print("  implied alpha*X from sigma/Delta = 0.35/0.15:", 0.35/0.15, "-> X at alpha=.25:", 0.35/0.15/0.25)

print("\n== 3b. 2025 calibration: transient vs durable split")
for lh in (1.0, 1.5):
    R, g = Rstar(0.28, 0.10, lh, 0.25); print(f"  calib lam_h={lh}: R_inf=0.38, surplus={R-0.38:.2f}, chosen (g,m)=({g:.2f},{0.28-0.25*(g-0.1):.2f})")
print("  empirical frontier point 2023-25 FCF-SBC: (g,m)=(0.40,0.45) [Table envelope]")
