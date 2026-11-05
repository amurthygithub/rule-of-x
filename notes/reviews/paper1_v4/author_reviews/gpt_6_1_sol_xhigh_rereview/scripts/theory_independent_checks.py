"""Independent arithmetic and counterexamples, not a rerun of author code."""
import json
import math
import random
from pathlib import Path

SEED = 20261104
rng = random.Random(SEED)
out = {"seed": SEED, "scope": "Independent closed-form checks; author repository and Lean not executed."}
errors=[]
for _ in range(1000):
    alpha=rng.uniform(.05,.95);ell=rng.uniform(.01,2);k=rng.uniform(0,2);X=k+rng.uniform(.01,10)
    G=rng.uniform(0,.4);m0=rng.uniform(-1,1)
    spend=(alpha*ell*(X-k))**(1/(1-alpha));excess=ell*spend**alpha
    slope=-k-(1/alpha)*ell**(-1/alpha)*excess**(1/alpha-1)
    score=X*(G+excess)+m0-spend-k*(G+excess)
    expected=m0+(X-k)*G+(1-alpha)*(X-k)*excess
    errors.append(max(abs(slope+X)/(1+X),abs(score-expected)/(1+abs(expected))))
out['static_1000_draw_max_relative_error']=max(errors)
assert max(errors)<1e-10

alpha=.3;beta=1/alpha;chi=.9;g=.3;A=.7;m0=.6
q=lambda z:1-chi+chi*z
cone=lambda z:m0-A*q(z)**beta
eps=1e-6
fd=(cone(g+eps)-cone(g-eps))/(2*eps)
derivative=-A*beta*q(g)**(beta-1)*chi
out['uniform_growth_cone']={'growth':g,'quantile_growth':q(g),'finite_difference':fd,'chain_rule':derivative}
assert math.isclose(fd,derivative,rel_tol=1e-8)

# Under the allowed finite cap a high weight selects the endpoint.
cap=1.0;ell=1.0;high_weight=10.0
uncapped_spend=(alpha*ell*high_weight)**(1/(1-alpha))
out['common_frontier_capped_weight_counterexample']={
    'alpha':alpha,'ell':ell,'spend_cap':cap,'X':high_weight,
    'uncapped_spend':uncapped_spend,'chosen_growth':ell*cap**alpha,
    'frontier_steepest_slope_magnitude':beta,'X_exceeds_frontier_slope':high_weight>beta}
assert uncapped_spend>cap and high_weight>beta

G=.10;r=.15;ku=1.;ac=0.
limits=[]
for u in [.85,.35]:
    full_cost=u+r*(ku+ac)
    limits.append({'u':u,'full_cost':full_cost,'competitive_score':G+(r-G)*(ku+ac)/full_cost})
out['free_entry_without_scarce_input']=limits
assert limits[1]['competitive_score']>limits[0]['competitive_score']

out['general_concave_growth_counterexample']={
    'phi':'sigma','ell':1,'X':2,'k':0,'G':0,'m0':0,
    'unbounded_score':'sigma','scores_at_spend_1_10_100':[1,10,100]}

Sprev=100.;Scn=120.;Sac=50.;St=Scn+Sac;kacq=3.;growth=St/Sprev-1;acq_growth=Sac/Sprev
out['annual_acquisition_identity']={'growth':growth,'acquired_growth':acq_growth,'cash_over_current_revenue':kacq*Sac/St,'corrected_identity':kacq*acq_growth/(1+growth)}
assert math.isclose(kacq*Sac/St,kacq*acq_growth/(1+growth))

def psi(T,rate):
    return (1+(1+rate)**(-T))/(2*T)+(1-(1+rate)**(-(T-1)))/(rate*T)
out['tax_shields']={'psi_5_at_discount_10pct':psi(5,.1),'psi_15_at_discount_10pct':psi(15,.1),'psi_15_at_growth_30pct':psi(15,.3)}
pc=.005;p=.02;nlayer=3;N=24
independent=1-(1-(pc+(1-pc)*p**nlayer))**N
persistent=pc+(1-pc)*(1-(1-p**nlayer)**N)
out['temporal_common_mode_sensitivity']={'independent_annual_escape':independent,'period_persistent_annual_escape':persistent}
target=Path(__file__).resolve().parents[1]/'results/theory_independent_checks.json'
target.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
