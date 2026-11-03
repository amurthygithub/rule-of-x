"""Fully independent HJB solver: value iteration on grid for worked example
r=0.10, G=0.04, k=0, alpha=0.3, m0=0.35, sbar=0.5, lambda chosen so v0=10."""
import numpy as np, json
from scipy.optimize import brentq
a, G, k, m0, r, sbar = 0.3, 0.04, 0.0, 0.35, 0.10, 0.5
Ca = (1-a)*a**(a/(1-a))
def lam_for(v0):
    return (((r-G)*v0 - (m0-k*G))/Ca)**(1-a)/(v0-k)
lam = lam_for(10.0)
print('lambda =', round(lam,5))
# Gordon root check
f = lambda q: (r-G)*q - (m0-k*G) - Ca*(lam*max(q-k,0))**(1/(1-a))
roots=[]
gs = np.linspace(1e-6, 60, 600000)
vals = np.array([f(q) for q in gs])
for i in range(len(gs)-1):
    if vals[i]*vals[i+1] < 0: roots.append(brentq(f, gs[i], gs[i+1]))
print('roots of gordon eq:', [round(x,4) for x in roots])
# value iteration: v(s), grid in s; flow at s: s*(m0 - sig - k(G+D)); D = lam(1-s/sbar) sig^a
# policy iteration style: discretize sig, solve linear system (I - discount*transition) v = flow
dt = 0.02
N = 4000
s = np.concatenate([np.geomspace(1e-8, sbar*0.5, N//2, endpoint=False), sbar - np.geomspace(sbar*0.5, 1e-8, N - N//2)])
sig_grid = np.concatenate([[0.0], np.geomspace(1e-8, 40, 300)])
rG = r - G
v = np.zeros(N)
for it in range(300):
    # for each state, choose sig maximizing flow*dt + exp(-r*dt) * E[v(next)]
    # next s: ds = s*D*dt approx (Euler); better: use exact flow over dt: s' = s*exp(D*dt)
    best_val = np.full(N, -1e18); best_sig = np.zeros(N)
    for sg in sig_grid:
        D = lam*(1-s/sbar)*sg**a
        m = m0 - sg - k*(G+D)
        sp = s*np.exp(D*dt)
        sp = np.minimum(sp, s[-1])
        vn = np.interp(sp, s, v)
        val = s*m*dt + np.exp(-r*dt)*vn
        upd = val > best_val
        best_val[upd] = val[upd]; best_sig[upd] = sg
    v_new = best_val
    # add terminal: at s=sbar, D->0, v = s*(m0-kG)/(r-G)
    v_new[-1] = s[-1]*(m0-k*G)/rG
    diff = np.max(np.abs(v_new - v)/np.maximum(s,1e-12))
    v = v_new
    if diff < 1e-10: break
vp = np.gradient(v, s)
out = {}
for frac in [0.01, 0.10, 0.50]:
    sv = frac*sbar
    out[frac] = dict(vp=float(np.interp(sv, s, vp)), v_over_s=float(np.interp(sv, s, v)/sv))
print('iterations:', it, 'max change:', diff)
print('v\'(s) and v/s at 1%,10%,50% of cap:', json.dumps(out, indent=1))
print('paper (verify_theory 15g): v\' = 9.1, 7.2, 5.4 ; v/s = 9.4, 8.1, 6.5')
json.dump(out, open('/root/tmp/review/out/audit_hjb_indep.json','w'), indent=1)
