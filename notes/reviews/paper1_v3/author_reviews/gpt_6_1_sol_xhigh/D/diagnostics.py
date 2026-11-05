"""Independent diagnostics. Run from this directory; no author code or panel is used."""
from pathlib import Path
import json, math, sys, platform, importlib.metadata
import numpy as np
import scipy
from scipy.optimize import minimize_scalar
import sympy as sp
OUT=Path(__file__).resolve().parent
results={"seed":20261102,"type":"independent deterministic derivation, optimization, exact recurrence and Monte Carlo; no author code"}
# Enumerate the exact illustrative control-cost problem (at most six layers of each type).
def design(nh,na,pcc=0,ph=.05):
 h=1 if nh==0 else .002+.998*ph**nh
 a=1 if na==0 else .005+.995*.02**na
 p=pcc+(1-pcc)*h*a
 annual=-math.expm1(24*math.log1p(-p)) if p<1 else 1.
 cost=nh*500000+na*50000+(204672 if na else 0)
 return {'human':nh,'AI':na,'cost_usd':cost,'per_opportunity':p,'annual':annual}
rows=[]
for threshold in [.01,.05]:
 for pcc in [0,.0001,.0002,.0005,.0008,.001,.0015,.002,.0025]:
  feasible=[design(h,a,pcc) for h in range(7) for a in range(7) if h+a and design(h,a,pcc)['annual']<=threshold]
  rows.append({'threshold':threshold,'pcc':pcc,'best':min(feasible,key=lambda x:x['cost_usd']) if feasible else None})
results['control_designs']=rows
results['all_AI_annual_lower_bound']=-math.expm1(24*math.log1p(-.005))
# Security objective independently optimized over a broad log grid; units normalized to revenue.
sec=[]
for initial,L,exposure in [(0.0069,4,1),(.0069,2,2),(.0069,1,3)]:
 eff=initial/L; inc=eff*math.exp(L)*exposure
 opt=minimize_scalar(lambda x:x+inc*math.exp(-x/eff),bounds=(0,max(1.,10*inc)),method='bounded',options={'xatol':1e-13})
 exact=eff*(1+L+math.log(exposure))
 sec.append({'L':L,'exposure':exposure,'analytic':exact,'numerical':float(opt.fun),'abs_residual':abs(exact-opt.fun)})
results['security']=sec
x,c,I=sp.symbols('x c I',positive=True)
results['symbolic_security_first_order_residual']=str(sp.simplify(sp.diff(x+I*sp.exp(-x/c),x).subs(x,c*sp.log(I/c))))
y,p=sp.symbols('y p',positive=True); cap=sp.symbols('cap',positive=True)
results['symbolic_pareto_integral']=str(sp.integrate(y**(-p),(y,1,cap))+1)
# Exact fluid recurrence under Prop7(e)(iii). For 0<p<1 and 0<cw<1,
# once U<cw, U_next=(1-p)U>0; exact completion never occurs at finite w.
def fluid(prob,cw,n):
 u=1.; out=[]
 for w in range(1,n+1):
  attempt=min(cw,u);u-=prob*attempt
  out.append({'wave':w,'embedded':1-u,'unembedded':u,'linear_cap':min(1.,prob*cw*w)})
 return out
results['fluid_illustrations']={}
for label,prob,cw in [('central_quarterly_illustration',.7,.025),('fast_quarterly_illustration',.8,.055)]:
 seq=fluid(prob,cw,200)
 results['fluid_illustrations'][label]={'parameters':{'success':prob,'cw':cw,'Tpar':.25,'warning':'Tpar is illustrative; not verified author input. Not a reproduction of dated path.'},'selected':[seq[i-1] for i in [20,24,35,57,60]],'first_99_percent_wave':next(q['wave'] for q in seq if q['embedded']>=.99),'first_99_9_percent_wave':next(q['wave'] for q in seq if q['embedded']>=.999),'largest_bound_shortfall':max(q['linear_cap']-q['embedded'] for q in seq)}
# Random-freeze survival: expectation over Poisson freezes, not the deterministic clock.
rng=np.random.default_rng(20261102); draws=200000
nuD=.23;nuR=.4;freeze=.5;lag=1.25
counts=rng.poisson(nuR*lag,size=draws)
vals=np.exp(-nuD*(lag+freeze*counts)); exact=math.exp(-nuD*lag-nuR*lag*(1-math.exp(-nuD*freeze)))
results['random_freeze_survival']={'draws':draws,'nuD':nuD,'nuR':nuR,'freeze':freeze,'lag':lag,'analytic':exact,'simulation_mean':float(vals.mean()),'MC_SE':float(vals.std(ddof=1)/math.sqrt(draws)),'uniform_clock':math.exp(-nuD*(1+nuR*freeze)*lag)}
# Lower-bound transport diagnostic: input and output sentence rates need conversion first.
results['Asgari_denominator_diagnostic']={'hallucination_output_rate':191/12999,'omission_input_rate':1712/49590,'noncomparable_sum':191/12999+1712/49590,'event_count_per_output_sentence':(191+1712)/12999,'warning':'Event intensity only; not a probability of an erroneous output, not a task cost rate. Source has multiple configurations.'}
# Table4 central structural arithmetic using printed rounded cost components.
base=(1-.18)*(1-.06-.025-.030-.0623)
results['central_ceiling_from_printed_costs']={'margin_base':base,'market_growth_for_score_1':1-base,'score_at_G_15pct_k_0':base+.15,'warning':'Rounded input arithmetic; no raw calibration replication'}
results['environment']={'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__,'sympy':sp.__version__,'algorithm_notes':'bounded scalar optimization xatol=1e-13; exact deterministic control enumeration depths0..6; Monte Carlo seed20261102; no fit to manuscript data'}
(OUT/'results.json').write_text(json.dumps(results,indent=2))
(OUT/'execution_log.txt').write_text('Completed diagnostics.py\n'+json.dumps(results['environment'],indent=2)+'\nChecks: 18 threshold/pcc combinations; 3 security optimizations; symbolic derivative and integral; 2 200-wave recurrences; 200000 Poisson draws.\n')
print(json.dumps({k:results[k] for k in ['all_AI_annual_lower_bound','security','random_freeze_survival','central_ceiling_from_printed_costs','Asgari_denominator_diagnostic']},indent=2))
