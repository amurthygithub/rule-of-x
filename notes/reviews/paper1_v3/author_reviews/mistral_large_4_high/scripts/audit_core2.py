"""Numeric-symbolic checks with substitution to avoid sympy branch issues."""
import numpy as np, sympy as sp, json
res={}
# Use concrete-symbolic hybrid: verify identities by random numeric evaluation of both sides.
rng = np.random.default_rng(7)
def ev(expr, subs): return float(expr.subs(subs))
a_,G_,m0_,k_,X_,lam_,s_,sbar_,r_ = sp.symbols('a G m0 k X lam s sbar r', positive=True)
h = 1 - s_/sbar_; l = lam_*h; y = X_ - k_
beta = 1/a_; kap = l**(-beta); Ca = (1-a_)*a_**(a_/(1-a_))
sig_star = (a_*l*y)**(1/(1-a_)); Dstar = l*sig_star**a_
Rstar = m0_ + y*G_ + Ca*(l*y)**(1/(1-a_))
GG = sp.symbols('GG')
mstar = m0_ - k_*GG - kap*(GG-G_)**beta
checks = {
 'Rstar_eq': Rstar - (m0_ + y*G_ + (1-a_)*y*Dstar),
 'Ca_term': (1-a_)*y*Dstar - Ca*(l*y)**(1/(1-a_)),
 'sigstar': sig_star - a_*y*Dstar,
 'tangency': sp.diff(mstar, GG).subs(GG, G_+Dstar) + X_,
 'frontier_at_opt': mstar.subs(GG, G_+Dstar) - (m0_ - sig_star - k_*(G_+Dstar)),
 'env_dX': sp.diff(Rstar, X_) - (G_+Dstar),
 'env_dk': sp.diff(Rstar, k_) + (G_+Dstar),
 'env_dlam': sp.diff(Rstar, lam_) - y*Dstar/lam_,
 'env_dG': sp.diff(Rstar, G_) - y,
 'sat_dR_ds': sp.diff(m0_+y*G_+Ca*(lam_*h*y)**(1/(1-a_)), s_) + y*Dstar/(sbar_-s_),
}
worst = {k2: 0.0 for k2 in checks}
for i in range(2000):
    a = rng.uniform(0.15,0.6); X = rng.uniform(0.5, 12); k = rng.uniform(0, 2)
    if X<=k: continue
    G = rng.uniform(0.0,0.5); m0 = rng.uniform(0.2,0.9); lam = rng.uniform(0.05,4)
    sbar = rng.uniform(0.2,1.0); s = rng.uniform(1e-5, sbar*0.999); r = rng.uniform(G+0.02, 1.0)
    subs = {a_:a, G_:G, m0_:m0, k_:k, X_:X, lam_:lam, s_:s, sbar_:sbar, r_:r}
    for k2, e in checks.items():
        v = abs(ev(e, subs))
        scale = max(1.0, abs(ev(Rstar, subs)))
        worst[k2] = max(worst[k2], v/scale)
out = {k2: float(v) for k2,v in worst.items()}
print(json.dumps(out, indent=1))
json.dump(out, open('/root/tmp/review/out/audit_core2.json','w'), indent=1)
