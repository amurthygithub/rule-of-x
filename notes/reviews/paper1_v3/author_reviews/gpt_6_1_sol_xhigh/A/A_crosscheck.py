"""Post-freeze rescaling and scope check. Does not alter first-report artifacts."""
import json, pathlib, numpy as np
P=pathlib.Path(__file__).parent
r=json.loads((P/'results.json').read_text());a=np.load(P/'dynamic_solution_16000.npz')
z=a['s'];w=a['v'];sbar=.5;s=sbar*z;v=sbar*w
Dphysical=np.gradient(v,s,edge_order=2)
comparison=float(np.max(np.abs(Dphysical-a['D'])))
rho=.06;b=.35;alpha=.3;lam=r['dynamic']['parameters']['lambda_'];C=(1-alpha)*alpha**(alpha/(1-alpha))
res=rho*v-s*b-s*C*(lam*(1-s/sbar)*np.maximum(Dphysical,0))**(1/(1-alpha))
mask=(z>=.005)&(z<=.995)
record={'purpose':'Correct the literal cap in frozen A report to physical sbar=.5; original sbar=1 was normalized state domain, not a model assumption.',
 'mapping':'physical s=.5*z; physical v(s)=.5*w(z); vprime(s)=wprime(z); v(s)/s=w(z)/z',
 'sbar':sbar,'derivative_max_rescaling_difference':comparison,'physical_HJB_residual_max':float(np.max(np.abs(res[mask]))),
 'local_asymptotic_physical_parameters':dict(alpha=.5,lambda_=.2,r=.1,G=0,m0=.1,k=0,sbar=.5),
 'local_asymptotic_dimensionless_results':r['local_asymptotic'],
 'Rule1000_scope_example':{'parameters':dict(alpha=.3,lambda_=.6,G=9.5,m0=.5,k=0,sbar=.5,s0=.1,X=1),
  'zero_spend_policy':{'sigma':0,'g':9.5,'m':.5,'R1':10,'share_constant':.1},
  'static_optimal_path_saturated_limit':10,
  'limits':'Extreme growth economically outside scenarios, but not excluded by Assumptions1-4. Corollary1 requires target greater than R_infty, so is not contradicted.'}}
(P/'A_crosscheck_results.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
