"""Independent HJB via value iteration in CONTINUOUS time (no dt): solve
(r-G) v(s) = max_sig [ s(m0 - sig - k(G+D)) + v'(s) * s * D ], D = lam(1-s/sbar) sig^a
Self-consistent: use collocation: guess v, compute v' = grad, solve nonlinear eq per node for v:
(r-G) v_i = s_i*(m0 - sig_i - k(G+D_i)) + vp_i*s_i*D_i, with vp from neighboring v.
Iterate. Boundary v(sbar) = (m0-kG) sbar/(r-G)."""
import numpy as np, json
from scipy.optimize import brentq
a, G, k, m0, r, sbar = 0.3, 0.04, 0.0, 0.35, 0.10, 0.5
Ca=(1-a)*a**(a/(1-a))
lam = (((r-G)*10.0 - (m0-k*G))/Ca)**(1-a)/10.0
def D_of(sig, s): return lam*(1-s/sbar)*sig**a
N = 1200
s = np.concatenate([np.geomspace(1e-9, sbar*0.5, N//2, endpoint=False), sbar - np.geomspace(sbar*0.5, 1e-9, N-N//2)])
v = s*(m0-k*G)/(r-G)  # initial: no-growth value
vp = np.gradient(v, s)
for it in range(400):
    vp = np.gradient(v, s)
    vnew = v.copy()
    for i in range(N-1):
        si = s[i]
        def F(sig):
            D = D_of(sig, si)
            return (r-G)*v[i] - (si*(m0 - sig - k*(G+D)) + vp[i]*si*D)
        # maximize over sig: brute grid then brent
        grid = np.concatenate([[0.0], np.geomspace(1e-9, 30, 200)])
        vals = np.array([si*(m0-sg-k*(G+D_of(sg,si))) + vp[i]*si*D_of(sg,si) for sg in grid])
        j = int(np.argmax(vals))
        lo, hi = grid[max(j-1,0)], grid[min(j+1,len(grid)-1)]
        from scipy.optimize import minimize_scalar
        res = minimize_scalar(lambda sg: -(si*(m0-sg-k*(G+D_of(sg,si))) + vp[i]*si*D_of(sg,si)), bounds=(lo,hi), method='bounded', options={'xatol':1e-14})
        sg = res.x if -res.fun >= vals[j] else grid[j]
        vnew[i] = (si*(m0-sg-k*(G+D_of(sg,si))) + vp[i]*si*D_of(sg,si))/(r-G)
    vnew[-1] = s[-1]*(m0-k*G)/(r-G)
    d = np.max(np.abs(vnew-v)/np.maximum(s,1e-12))
    v = vnew
    if d < 1e-9: break
vp = np.gradient(v, s)
out={}
for frac in [0.01,0.10,0.50]:
    sv=frac*sbar
    out[frac]=dict(vp=float(np.interp(sv,s,vp)), v_over_s=float(np.interp(sv,s,v)/sv))
print('iters', it, 'diff', d)
print(json.dumps(out, indent=1))
print('paper 15g: vp = 9.1, 7.2, 5.4; v/s = 9.4, 8.1, 6.5')
print('small-s: v/s at s=1e-6:', float(np.interp(1e-6,s,v)/1e-6), "vp:", float(np.interp(1e-6,s,vp)))
json.dump(out, open('/root/tmp/review/out/audit_hjb2.json','w'), indent=1)
