"""Numerical audits: (1) brute-force maximize R_X on grid vs closed form;
(2) worked examples quoted in text (Rule of 1000 threshold, transient bounds);
(3) envelope finite differences; (4) score-budget sharpness counterexample attempt;
(5) HJB numerical solution + verification hypothesis diagnostics."""
import numpy as np, json
from scipy.optimize import minimize_scalar, brentq
out = {}
rng = np.random.default_rng(20261103)

# (1) brute force vs closed form over random params
maxrel = 0.0
for i in range(3000):
    a = rng.uniform(0.05, 0.95); G = rng.uniform(-0.2, 0.6); m0 = rng.uniform(0.0, 0.9)
    k = rng.uniform(0.0, 2.0); X = rng.uniform(0.0, 12.0); lam = rng.uniform(0.01, 5.0)
    sbar = rng.uniform(0.05, 1.0); s = rng.uniform(1e-6, sbar*0.999)
    h = 1 - s/sbar; l = lam*h; y = X - k
    if X <= k:
        gstar, Rstar = G, m0 + y*G
    else:
        beta = 1/a; kap = l**(-beta); Ca = (1-a)*a**(a/(1-a))
        Dstar = l**(1/(1-a))*(a*y)**(a/(1-a))
        gstar = G + Dstar
        Rstar = m0 + y*G + Ca*(l*y)**(1/(1-a))
    def negR(sig):
        g = G + l*sig**a; m = m0 - sig - k*g; return -(X*g + m)
    r = minimize_scalar(negR, bounds=(0, 50), method='bounded', options={'xatol':1e-14})
    Rbf = -r.x and -r.fun
    # also grid
    sigs = np.linspace(0, 50, 200001)
    g = G + l*sigs**a; m = m0 - sigs - k*g; Rv = X*g + m
    Rgrid = Rv.max()
    rel = abs(Rgrid - Rstar)/max(1e-12, abs(Rstar))
    maxrel = max(maxrel, rel)
    if i < 3:
        out.setdefault('examples', []).append(dict(a=a,G=G,m0=m0,k=k,X=X,lam=lam,s=s,sbar=sbar,Rstar=Rstar,Rgrid=Rgrid))
out['max_rel_err_grid_vs_closed_3000draws'] = maxrel

# (2) quoted worked example: a=0.3, X=1, k=0, m0=0.6, G=0.2, Rinf=0.8, Rule of 1000 requires lam*h >= Lambda ~ 8.71; at threshold grows ~1314 pts faster, spends ~394%, margin ~ -334%
a=0.3; X=1.0; k=0.0; m0=0.6; G=0.2; Rinf=m0+(X-k)*G; Rbar=10.0
Ca=(1-a)*a**(a/(1-a))
Lam = (1/(X-k))*((Rbar-Rinf)/Ca)**(1-a)
D = (Rbar-Rinf)/((1-a)*(X-k)); sig = a*(Rbar-Rinf)/(1-a)
g = G+D; m = m0 - k*g - sig
out['rule1000'] = dict(Lambda=Lam, Delta=D, sigma=sig, g=g, m=m, R=X*g+m)
print('Rule1000: Lambda=%.4f (paper ~8.71), Delta=%.1f (paper ~1314), sigma=%.1f (paper ~394), m=%.1f (paper ~-334)'%(Lam, D*100, sig*100, m*100))

# transient bounds example: X=1,k=0,m0=0.6,G=0.2,sbar=0.5, s0=0.01: >=1000pts at most one year (bound 1.8); >=140pts at most 9 years (9.6); s0=1e-5: >=1000 at most 5 years (5.0); continuous: 0.43y at 1000, 0.30y at static optimum
def T_bound(Rbar, s0, sbar, X, k, G, Rinf):
    import math
    return math.log(sbar/s0)/math.log(1+(Rbar-Rinf)/((X-k)*(1+G)))
out['transient'] = dict(
    T1000_s001=T_bound(10.0, 0.01, 0.5, 1,0,0.2,0.8),
    T140_s001=T_bound(1.4, 0.01, 0.5, 1,0,0.2,0.8),
    T1000_s1em5=T_bound(10.0, 1e-5, 0.5, 1,0,0.2,0.8),
    T1000_cont=(1-0)*np.log(0.5/0.01)/(10.0-0.8),
    T1000_cont_static=(1-0.3)*np.log(0.5/0.01)/(10.0-0.8))
print('transient:', {k2: round(v,3) for k2,v in out['transient'].items()})

# (3) envelope finite differences
a=0.3; X=5.0; k=0.2; G=0.1; m0=0.5; lam=1.5; sbar=0.8; s=0.2
h=1-s/sbar; l=lam*h; y=X-k; beta=1/a; kap=l**(-beta); Ca=(1-a)*a**(a/(1-a))
Dstar=l**(1/(1-a))*(a*y)**(a/(1-a)); gstar=G+Dstar
Rstar=m0+y*G+Ca*(l*y)**(1/(1-a))
def Rf(m0=m0,G=G,k=k,X=X,lam=lam,s=s):
    hh=1-s/sbar; ll=lam*hh; yy=X-k
    if X<=k: return m0+yy*G
    return m0+yy*G+(1-a)*(a** (a/(1-a)))*0 + (1-a)*yy*(ll**(1/(1-a))*(a*yy)**(a/(1-a)))
eps=1e-6
fd = dict(dX=(Rf(X=X+eps)-Rf(X=X-eps))/(2*eps), dk=(Rf(k=k+eps)-Rf(k=k-eps))/(2*eps),
          dm0=(Rf(m0=m0+eps)-Rf(m0=m0-eps))/(2*eps), dG=(Rf(G=G+eps)-Rf(G=G-eps))/(2*eps),
          dlam=(Rf(lam=lam+eps)-Rf(lam=lam-eps))/(2*eps))
out['envelope_fd'] = dict(fd=fd, theory=dict(dX=gstar, dk=-gstar, dm0=1, dG=y, dlam=y*Dstar/lam))
print('envelope fd:', {k2: round(v,6) for k2,v in fd.items()}, 'theory:', {k2: round(v,6) for k2,v in out['envelope_fd']['theory'].items()})

# (4) score budget sharpness: is int (R-Rinf)^+ dt <= y ln(sT/s0) tight? Try adversarial path: spend tiny epsilon each period -> R-Rinf ~ y*l*sig^a - sig; optimize per-period ratio (y l sig^a - sig)/(l sig^a) = y - sig^{1-a}/l -> as sig->0 ratio -> y. So bound approached by slow spending. Verify numerically.
sig_grid = np.logspace(-12, 0, 500)
a=0.3; l=1.0; y=1.0
ratio = (y*l*sig_grid**a - sig_grid)/(l*sig_grid**a)
out['budget_sharp'] = dict(max_ratio=float(ratio.max()), at_sig=float(sig_grid[ratio.argmax()]), y=y)
print('budget sharpness max ratio (should ->1 as sig->0):', out['budget_sharp'])

# (5) HJB numeric: solve ODE for v on (0, sbar), check Xdyn=v' vs small-share v0 (Gordon root)
def solve_hjb(a=0.3, G=0.1, m0=0.5, k=0.1, lam=1.2, sbar=0.9, r=0.25):
    # HJB: (r-G) v = s max_sig {m0 - sig - kG + (v'-k) l(s) sig^a}, l=lam(1-s/sbar)
    # interior FOC: (v'-k) a l sig^(a-1) = 1 -> sig = (a l (v'-k))^{1/(1-a)} when v'>k
    # ODE: (r-G) v/s = m0 - kG + C_a (l (v'-k))^{1/(1-a)}
    # solve as boundary value: v(sbar) = (m0-kG) sbar/(r-G); and v/s -> v0 at 0 where v0 solves (r-G)v0 = m0-kG + Ca (lam (v0-k))^{1/(1-a)}
    Ca=(1-a)*a**(a/(1-a))
    def H(v0):
        return (r-G)*v0 - (m0-k*G) - Ca*(lam*max(v0-k,0))**(1/(1-a))
    # find smallest positive root
    grid = np.linspace(1e-9, 50, 200000)
    vals = np.array([H(v) for v in grid])
    roots = []
    for i in range(len(grid)-1):
        if vals[i]==0 or vals[i]*vals[i+1]<0:
            roots.append(brentq(H, grid[i], grid[i+1]))
    v0 = roots[0] if roots else None
    # integrate ODE outward from small s with v(s)=v0 s ... singular; instead integrate inward from sbar with shooting on v'(sbar-)? Use solve_bvp-like via solve_ivp on u=v/s:
    # u' = (Phi(u,s)-u)/s, Phi = k + (1/l(s)) * ( ((r-G)u - (m0-kG))/Ca )^{1-a}  when (r-G)u > m0-kG and v'>k
    from scipy.integrate import solve_ivp
    def Phi(u, s):
        l = lam*(1-s/sbar)
        inner = ((r-G)*u - (m0-k*G))/Ca
        if inner <= 0: return None
        return k + inner**(1-a)/l
    # integrate from s0 small with u(s0)=v0 + correction; singular at 0: u-v0 ~ s^{p}, p=(r-G)/Delta0 - 1
    Delta0 = lam**(1/(1-a))*(a*max(v0-k,1e-12))**(a/(1-a))
    p = (r-G)/Delta0 - 1
    s_start = 1e-6
    # try shooting: u(s0)=v0*(1 + c s0^p); integrate to sbar, match u(sbar)=(m0-kG)/(r-G)
    target = (m0-k*G)*sbar/(r-G)  # v(sbar)
    def rhs(s, u):
        ph = Phi(u[0], s)
        if ph is None: return [0.0]
        return [(ph - u[0])/s]
    def shoot(c):
        sol = solve_ivp(rhs, (s_start, sbar*(1-1e-9)), [v0*(1+c*s_start**p)], rtol=1e-10, atol=1e-12, dense_output=False, max_step=(sbar-s_start)/2000)
        return sol.y[0,-1]*sbar - target  # v(sbar*s) approx
    # bisection on c
    from scipy.optimize import brentq as bq
    try:
        c = bq(shoot, -50, 50)
        sol = solve_ivp(rhs, (s_start, sbar*(1-1e-9)), [v0*(1+c*s_start**p)], rtol=1e-9, atol=1e-11, max_step=(sbar-s_start)/4000)
        ss = sol.t; uu = sol.y[0]
        # v'(s) = u + s u'
        vp = uu + ss*np.array([rhs(s,[u])[0] for s,u in zip(ss,uu)])
        return dict(v0=v0, c=c, s=ss.tolist(), u=uu.tolist(), vp=vp.tolist(), sbar=sbar, Delta0=Delta0, p=p)
    except Exception as e:
        return dict(error=str(e), v0=v0, p=p, Delta0=Delta0)
Hb = solve_hjb()
if 'error' not in Hb:
    ss = np.array(Hb['s']); vp = np.array(Hb['vp'])
    out['hjb'] = dict(v0=Hb['v0'], p=Hb['p'], vp_at_1pct=float(np.interp(0.01, ss, vp)), vp_at_10pct=float(np.interp(0.10, ss, vp)), vp_at_50pct=float(np.interp(0.50*Hb['sbar'], ss, vp)))
    print('HJB: v0=%.4f, Xdyn at s/sbar=0.011: %.3f, 0.111: %.3f, 0.556: %.3f'%(Hb['v0'], out['hjb']['vp_at_1pct'], out['hjb']['vp_at_10pct'], out['hjb']['vp_at_50pct']))
else:
    out['hjb'] = Hb; print('HJB failed:', Hb)
json.dump(out, open('/root/tmp/review/out/audit_numeric.json','w'), indent=1, default=float)
print('saved')
