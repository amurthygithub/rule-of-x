"""Independent exact-population diagnostics; never reads author panel/code."""
from pathlib import Path
import json, platform, sys, hashlib
import numpy as np
import scipy
from scipy.optimize import minimize_scalar

HERE=Path(__file__).resolve().parent
inputs=json.loads((HERE/'inputs.json').read_text())
a=inputs['alpha']; beta=1/a; W=inputs['support_max_growth']; chi=inputs['chi']
ell=inputs['ell']; m0=inputs['m0']; cap=inputs['spend_cap']; p=inputs['growth_cdf_power']
grid=np.arange(0,W+1e-12,inputs['author_grid_step'])
def F(g): return (np.asarray(g)/W)**p
def density(g): return p/W*(np.asarray(g)/W)**(p-1)
def margin(g): return m0-(np.asarray(g)/ell)**beta
def derivative(g): return -beta*np.asarray(g)**(beta-1)/ell**beta
def qmap(g): return W*((1-chi)+chi*F(g))**(1/p)
def slope(x,y): return float(np.dot(x-x.mean(),y-y.mean())/np.dot(x-x.mean(),x-x.mean()))
q=qmap(grid); cone=margin(q); cone_slope=slope(grid,cone)
naive_factor=(beta+1)*(beta+2)/6
analytic=[]
for g in [0.1,0.3,0.5,0.59]:
 qg=float(qmap(g)); qp=chi*float(density(g))/float(density(qg)); exact=float(derivative(qg)*qp)
 h=1e-6; fd=float((margin(qmap(g+h))-margin(qmap(g-h)))/(2*h))
 analytic.append({'g':g,'conditional_growth_quantile':qg,'qprime':qp,'exact_cone_derivative':exact,'finite_difference':fd,'abs_error':abs(fd-exact)})
# Dense, uniformly located growth support points, with masses from exact population CDF.
# This is deterministic quadrature, NOT a random empirical panel.
mesh=[]
for n in [1001,10001,100001]:
 edges=np.linspace(0,W,n+1); points=(edges[1:]+edges[:-1])/2; masses=np.diff(F(edges)); quantiles=[]
 for threshold in grid:
  use=points>=threshold
  if not np.any(use): quantiles.append(W); continue
  pts=points[use]; weights=masses[use]; cum=np.cumsum(weights); target=(1-chi)*cum[-1]
  quantiles.append(float(pts[min(np.searchsorted(cum,target),len(pts)-1)]))
 ys=margin(np.array(quantiles))
 mesh.append({'support_points':n,'max_gap':W/n,'cone_slope':slope(grid,ys),'max_quantile_error':float(np.max(np.abs(np.array(quantiles)-q)))})
# Verify common-frontier optimizing choices on the spending domain [0,cap].
checks=[]
for growth in np.linspace(.001,W,101):
 X=float(-derivative(growth)); spend=float((growth/ell)**beta)
 def obj(sigma): return -(X*ell*sigma**a+m0-sigma)
 opt=minimize_scalar(obj,bounds=(0,cap),method='bounded',options={'xatol':1e-13,'maxiter':1000})
 checks.append({'growth':float(growth),'X':X,'spend':spend,'optimizer_spend':float(opt.x),'objective_error':float(abs(obj(spend)-opt.fun)),'success':bool(opt.success)})
res={
 'kind':'exact population plus deterministic numerical diagnostics; no author-data re-estimation',
 'input_sha256':hashlib.sha256((HERE/'inputs.json').read_bytes()).hexdigest(),
 'parameters':inputs,
 'beta':beta,
 'cone_slope_on_author_grid':cone_slope,
 'frontier_slope_on_author_grid':slope(grid,margin(grid)),
 'actual_frontier_steepest_slope_magnitude':float(-derivative(W)),
 'naive_factor':naive_factor,
 'naive_inferred_steepest_slope_magnitude':-cone_slope*naive_factor,
 'max_spend':float((W/ell)**beta),
 'min_margin':float(margin(W)),
 'max_X':float(-derivative(W)),
 'derivative_checks':analytic,
 'dense_weighted_support_mesh':mesh,
 'optimizer_count':len(checks),
 'optimizer_all_success':all(x['success'] for x in checks),
 'max_optimization_objective_error':max(x['objective_error'] for x in checks),
 'sample_flow':{'E1':1788,'flagged':466,'retained_flagged':58,'implied_E2':1788-466+58,'reported_E2':1378,'implied_exclusion_only':1788-466,'reported_exclusion_only':1320,'imputed_total':1786,'unreconciled_E2_difference':2},
 'MC_standard_error_example':{'B':999,'reported_p':.097,'binomial_approximation':float(np.sqrt(.097*(1-.097)/999))},
 'environment':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform()},
 'no_randomness':True,
}
(HERE/'results.json').write_text(json.dumps(res,indent=2))
np.savetxt(HERE/'population_grid.csv',np.column_stack([grid,q,cone,margin(grid)]),delimiter=',',header='growth_threshold,conditional_growth_quantile,cone_margin_quantile,true_frontier_margin',comments='')
(HERE/'optimization_checks.json').write_text(json.dumps(checks,indent=2))
(HERE/'execution_log.txt').write_text('Executed: python3 outputs/review_bundle/B/diagnostics.py\nNo raw paper data or author scripts used.\n'+json.dumps(res,indent=2)+'\n')
print(json.dumps({k:res[k] for k in ['cone_slope_on_author_grid','actual_frontier_steepest_slope_magnitude','naive_inferred_steepest_slope_magnitude','max_spend','optimizer_all_success','max_optimization_objective_error','dense_weighted_support_mesh']},indent=2))
