"""Independent referee checks; no author code imported. Deterministic seed 20261102."""
import json, platform, pathlib, sys
import numpy as np
import scipy
from scipy.optimize import minimize_scalar, brentq
from scipy.integrate import solve_ivp
import sympy as sp
OUT=pathlib.Path(__file__).parent

def closed(alpha,ell,X,k,G,m0,cap=np.inf):
 y=max(X-k,0); sig=min((alpha*ell*y)**(1/(1-alpha)),cap)
 delta=ell*sig**alpha; g=G+delta
 return dict(sigma=sig,g=g,margin=m0-sig-k*g,R=m0+(X-k)*G+(X-k)*delta-sig)

rng=np.random.default_rng(20261102); err=[]
for i in range(250):
 a=rng.uniform(.1,.9); ell=rng.uniform(.05,2); X=rng.uniform(0,5); k=rng.uniform(0,1); G=rng.uniform(0,.3); m=rng.uniform(.05,.8)
 cap=rng.uniform(.01,2) if i%2 else np.inf
 c=closed(a,ell,X,k,G,m,cap)
 upper=cap if np.isfinite(cap) else max(c['sigma']*3,1)
 f=lambda sig: -(m+(X-k)*G+(X-k)*ell*sig**a-sig)
 res=minimize_scalar(f,bounds=(0,upper),method='bounded',options={'xatol':1e-12})
 numerical=max(-f(0),-f(upper),-res.fun)
 err.append(abs(c['R']-numerical))

# Symbolic verification of score-support envelope, parameterizing q=1/(1-alpha).
a,l,y=sp.symbols('a l y',positive=True)
sig=(a*l*y)**(1/(1-a)); Pi=(1-a)*a**(a/(1-a))*(l*y)**(1/(1-a))
q_sym,C_sym=sp.symbols('q C',positive=True)
Pi_sym=C_sym*l**q_sym*y**q_sym; delta_sym=q_sym*C_sym*l**q_sym*y**(q_sym-1)
symbolic={'parameterization':'q=1/(1-alpha), C=C_alpha; delta=q*C*ell^q*y^(q-1)',
 'surplus_derivative_y_minus_delta':str(sp.simplify(sp.diff(Pi_sym,y)-delta_sym)),
 'surplus_derivative_l_minus_y_delta_l':str(sp.simplify(sp.diff(Pi_sym,l)-y*delta_sym/l))}

# True finite change versus first-order hurdle (Corollary 3(v) wording).
a=.3; ell=.6; X=1.; k=.1; G=.1; m=.45; dk=.5
before=closed(a,ell,X,k,G,m); after=closed(a,ell,X,k+dk,G,m)
da=(before['R']-after['R']+before['g']*dk)/2
change=closed(a,ell,X,k+dk,G,m+da)['R']-before['R']
finite={'parameters':dict(alpha=a,ell=ell,X=X,k=k,G=G,m0=m,dk=dk,da=da),'g_before':before['g'],'g_after':after['g'],
 'actual_delta_score':change,'first_order_hurdle_gdk':before['g']*dk,'exact_break_even_saving':before['R']-after['R'],
 'interpretation':'Positive exact score gain even though da<g_before*dk. Corollary 3 introductory first-order qualification rescues (v); no theorem refutation.'}

def solve_hjb(n,a,lam,rho,b,k=0):
 s=np.linspace(0,1,n+1); ds=1/n; v=np.zeros(n+1); v[-1]=b/rho
 C=(1-a)*a**(a/(1-a)); q=1/(1-a)
 for j in range(n-1,0,-1):
  sj=s[j]; ell=lam*(1-sj); vn=v[j+1]
  fun=lambda value: rho*value-sj*b-sj*C*(ell*max((vn-value)/ds-k,0))**q
  lo=sj*b/rho; hi=b/rho
  v[j]=brentq(fun,lo,hi,xtol=1e-13,rtol=1e-13)
 D=np.gradient(v,ds,edge_order=2)
 ell=lam*(1-s); sig=(a*ell*np.maximum(D-k,0))**q
 residual=rho*v-s*b-s*C*(ell*np.maximum(D-k,0))**q
 mask=(s>=.005)&(s<=.995)
 return s,v,D,sig,float(np.max(np.abs(residual[mask])))

alpha=.3; rho=.06; b=.35; v0=10.; C=(1-alpha)*alpha**(alpha/(1-alpha)); lam=((rho*v0-b)/C)**(1-alpha)/v0
meshes=[]; latest=None
for n in [1000,2000,4000,8000,16000]:
 s,v,D,sigma,res=solve_hjb(n,alpha,lam,rho,b)
 rec={'n':n,'continuous_HJB_residual_interior_max':res,'v_at':{},'D_at':{}}
 for x in [.01,.1,.5,.8,.9,.95,.99,.999]:
  rec['v_at'][str(x)]=float(np.interp(x,s,v));rec['D_at'][str(x)]=float(np.interp(x,s,D))
 meshes.append(rec); latest=(s,v,D,sigma)
s,v,D,sigma=latest
paths=[]
for initial in [.01,.1,.5]:
 def rhs(t,z):
  zz=float(z[0]); dd=float(np.interp(zz,s,D)); sig=(alpha*lam*(1-zz)*max(dd,0))**(1/(1-alpha))
  return [zz*lam*(1-zz)*sig**alpha]
 sol=solve_ivp(rhs,[0,100],[initial],rtol=1e-9,atol=1e-11,max_step=.05)
 paths.append({'s0':initial,'s100':float(sol.y[0,-1]),'all_values_inside_open_domain':bool(np.all(sol.y>0) and np.all(sol.y<1)),'steps':len(sol.t)})
np.savez(OUT/'dynamic_solution_16000.npz',s=s,v=v,D=D,sigma=sigma)

# Local expansion at small share, including nonautonomous forcing omitted in supplement p16.
alpha2=.5;lam2=.2;rho2=.1;b2=.1;C2=.25
root=brentq(lambda x:rho2*x-b2-C2*(lam2*x)**2,0,2)
delta2=lam2**2*root/2; exponent=rho2/delta2-1; linear=root/(1-exponent)
# ODE integrate outward from locally consistent expansion; local existence smooth away from z=0.
zs=np.geomspace(1e-7,1e-3,300)
def du(z,u):
 phi=1/(lam2*(1-z))*((rho2*u[0]-b2)/C2)**(1-alpha2)
 return [(phi-u[0])/z]
# outward integration unstable when exponent>1; integrate backward from z=1e-3, stable to zero.
sol=solve_ivp(du,[1e-3,1e-7],[root+linear*1e-3],t_eval=zs[::-1],rtol=1e-12,atol=1e-14,max_step=1e-6)
local=[]
for z,u in zip(sol.t[::-1][::60],sol.y[0,::-1][::60]):
 local.append({'z':float(z),'u_minus_root_over_z':float((u-root)/z),'u_minus_root_over_z_power_a':float((u-root)/z**exponent)})
asym={'parameters':dict(alpha=alpha2,lambda_=lam2,r=rho2,G=0,m0=b2,k=0,sbar=1),
 'smallest_simple_positive_root':root,'delta0':delta2,'a':exponent,'predicted_linear_coefficient':linear,
 'correct_linearization':'z du/dz = a(u-v0)+(v0-k)z+o(abs(u-v0)+z); general local solution C z^a+(v0-k)z/(1-a), a!=1; resonance z log z at a=1',
 'diagnostic':local,'classification':'Demonstrated local asymptotic error in supplementary discussion, not failure of Proposition 2(d) limit or conditional verification theorem.'}
result={'environment':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__,'sympy':sp.__version__},
 'static_random_check':{'draws':250,'seed':20261102,'max_score_difference':max(err),'ranges':'alpha [.1,.9],ell [.05,2],X [0,5],k [0,1],G [0,.3],m0 [.05,.8]; half capped [.01,2]','optimizer':'bounded scalar + endpoints','xatol':1e-12},
 'symbolic':symbolic,'finite_change':finite,'dynamic':{'parameters':dict(alpha=alpha,lambda_=lam,r=.1,G=.04,m0=b,k=0,v0=v0,sbar=1),'algorithm':'monotone continuous-time upwind HJB, exact closed-form control maximization, scalar brent root at each grid point from saturation downward','root_xtol':1e-13,'root_rtol':1e-13,'meshes':meshes,'feedback_paths':paths,'limitations':'Grid evidence at one worked parameterization. No proof of global C1 existence.'},'local_asymptotic':asym}
(OUT/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
