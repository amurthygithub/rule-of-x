"""Independent HJB via ODE shooting, worked example. Solve u=v/s ODE backward from sbar:
u' = (Phi(u,s) - u)/s, Phi = k + (((r-G)u - (m0-kG))/Ca)^(1-a) / l(s), l=lam(1-s/sbar).
Shoot from s=sbar-eps with terminal v(sbar)=(m0-kG)sbar/(r-G) => u(sbar) = (m0-kG)/(r-G).
Integrate backward to small s; check u -> v0 = 10."""
import numpy as np, json
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
a, G, k, m0, r, sbar = 0.3, 0.04, 0.0, 0.35, 0.10, 0.5
Ca=(1-a)*a**(a/(1-a))
lam = (((r-G)*10.0 - (m0-k*G))/Ca)**(1-a)/10.0
def rhs(s, u):
    u = float(np.asarray(u).ravel()[0]); s = float(s)
    l = lam*(1-s/sbar)
    inner = ((r-G)*u - (m0-k*G))/Ca
    if inner <= 0: return [0.0]
    Phi = k + inner**(1-a)/l
    return [(Phi - u)/s]





# backward integration from sbar*(1-1e-10)
s_end = sbar*(1-1e-10)
u_end = (m0-k*G)/(r-G)
sol = solve_ivp(rhs, (s_end, 1e-7), [u_end], rtol=1e-9, atol=1e-11, max_step=sbar/3000, dense_output=True)
ss = sol.t[::-1]; uu = sol.y[0][::-1]
# v' = u + s u'
vp = uu + ss*np.array([rhs(float(s),[float(u)])[0] for s,u in zip(ss,uu)])
out={}
for frac in [0.01,0.10,0.50]:
    sv=frac*sbar
    out[frac]=dict(vp=float(np.interp(sv,ss,vp)), v_over_s=float(np.interp(sv,ss,uu)))
print('lambda', round(lam,5))
print(json.dumps(out, indent=1))
print('paper 15g: vp = 9.1, 7.2, 5.4; v/s = 9.4, 8.1, 6.5')
print('u at s=1e-6:', float(np.interp(1e-6, ss, uu)))
json.dump(out, open('/root/tmp/review/out/audit_hjb3.json','w'), indent=1)
