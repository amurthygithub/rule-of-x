"""Independent deterministic finance diagnostics. Run from any directory."""
import json, math, platform, sys
from pathlib import Path
import sympy as sy
here=Path(__file__).resolve().parent
inp=json.loads((here/'finance_inputs.json').read_text())
out={'method':'independent arithmetic + symbolic-engine identities; deterministic, no random draws',
'environment':{'python':sys.version,'platform':platform.platform(),'sympy':sy.__version__},'case_reconciliation':[]}
for a,b in zip(inp['annual'][:-1],inp['annual'][1:]):
 g=b['revenue']/a['revenue']-1; S=b['revenue']
 out['case_reconciliation'].append({'year':b['year'],'simple_growth':g,'log_growth':math.log1p(g),
 'gaap_score':g+b['operating_income']/S,'gaap_score_after_interest_expense':g+(b['operating_income']-b['interest_expense'])/S,
 'ocf_score_after_interest':g+b['ocf']/S,'ocf_score_with_expense_addback_tax24':g+(b['ocf']+.76*b['interest_expense'])/S,
 'ocf_score_with_cash_addback_tax24':g+(b['ocf']+.76*b['interest_paid'])/S,
 'ppe_sbc_deduction_pp':100*(b['ppe_cash']+b['sbc'])/S,
 'ppe_sbc_afterinterest_score':g+(b['ocf']-b['ppe_cash']-b['sbc'])/S,
 'ppe_sbc_beforeinterest_cashaddback_score_tax24':g+(b['ocf']-b['ppe_cash']-b['sbc']+.76*b['interest_paid'])/S,
 'intangible_cash_share':b['intangible_cash']/S})
q=inp['q2_2026'];g=q['revenue']/q['prior_revenue']-1
out['q2_2026']={'simple_growth':g,'gaap_score':g+q['operating_income']/q['revenue'],'gaap_afterinterest_score':g+(q['operating_income']-q['interest_expense'])/q['revenue'], 'organic_company_score':q['company_organic_growth']+q['operating_income']/q['revenue']}
# Acquisition finite-year normalization counterexample. All prices/revenues >0;
# constant costs can deliver any selected m in allowed domain. No claim against instantaneous algebra.
S0,Sc,Sa,C,X,m=100.,100.,100.,300.,1.,.2
S=Sc+Sa;ga=Sa/S0;gc=math.log1p(Sa/Sc);kap=C/Sa
out['acquisition_bridge']={'S_prior':S0,'S_continuing':Sc,'S_acquired_recognized':Sa,'S_current':S,'price':C,'price_per_recognized_revenue':kap,
 'true_cash_charge_current_margin':C/S,'simple_acquired_growth_prior_base':ga,'log_acquired_growth':gc,'instantaneous_like_charge_using_simple':kap*ga,'instantaneous_like_charge_using_log':kap*gc,
 'correct_simple_annual_formula':kap*ga/(1+(S/S0-1)), 'true_score':X*(S/S0-1)+m-C/S}
# PV vs actual deduction timing. Capital paid 0, fully deducted 1: equal PV, different date-0 cash.
r,tau,I=.1,.2,1.
psi=1/(1+r)
out['tax_one_vintage']={'I':I,'r':r,'tau':tau,'psi':psi,'true_t0_capital_cash':-I,'true_t1_tax_cash':tau*I,'pv_cash':-I+tau*I/(1+r),'equivalent_t0_cash':-(1-tau*psi)*I}
# Eq27 exact halfyear schedule, independent geometric sum.
def ps(T,z):return .5/T+sum((1+z)**(-a)/T for a in range(1,T))+.5*(1+z)**(-T)/T
out['tax_halfyear']=[{'T':T,'rate':r,'psi':ps(T,r)} for T in (5,15)]
# In balanced growth, vintage shield/current investment ratio discounts at growth, not WACC.
out['tax_balanced_growth']=[]
for g in (.05,.15,.30,.50):
 k=1.5;tau=.18;psi_r=ps(15,.1);ded=ps(15,g)
 out['tax_balanced_growth'].append({'simple_growth':g,'k':k,'tau':tau,'psi_wacc':psi_r,'actual_vintage_deduction_per_current_investment':ded,'model_cash_margin_overstatement_pp':100*tau*k*g*(psi_r-ded)})
# Finance identity symbolic verification.
g,m,k,r,X=sy.symbols('g m k r X'); e=m+k*(g-r);roic=(m+k*g)/k
out['symbolic_residuals']={'score_e':str(sy.simplify(X*g+m-((X-k)*g+e+r*k))),'score_roic':str(sy.simplify(X*g+m-k*(roic+(X/k-1)*g))),'value':str(sy.simplify(m/(r-g)-(k+e/(r-g))))}
# Horizon counterexample: implementation -1 at 0, permanent .2 annual benefit starts t=6;
# sale t=5 capitalizes remaining stream. PV_H cash<0, total value>0.
r=.1;H=5;benefit=.2;start=6
terminal=benefit/r*math.exp(-r*(start-H));total=-1+math.exp(-r*H)*terminal
out['horizon_counterexample']={'initial_cost':1,'benefit_flow_after_t6':benefit,'r_cont':r,'H':H,'cash_pv_through_H':-1,'terminal_at_H':terminal,'total_npv_including_sale':total,'full_horizon_npv':-1+benefit/r*math.exp(-r*start)}
# Reconstruct 2025 acquisition charge scenarios; not author-code execution.
a=inp['annual'][-1];S=a['revenue'];g=S/inp['annual'][-2]['revenue']-1
r=math.log1p(.0934);runs=[]
for nrr in (.91,.95):
 d=-math.log(nrr);T=1/d;crf=r/(1-math.exp(-r*T))
 for late in inp['2025_outlay_vintages'][-1]['time_range']:
  vs=[(v['outlay'],v.get('time',late)) for v in inp['2025_outlay_vintages']]
  end_nom=sum(c for c,t in vs);end_dec=sum(c*math.exp(-d*(2026-t)) for c,t in vs)
  avg_nom=sum(c*(1 if t<2025 else 2026-t) for c,t in vs)
  avg_dec=sum(c*math.exp(-d*max(0,2025-t))*(1-math.exp(-d*(1 if t<2025 else 2026-t)))/d for c,t in vs)
  for tax in (.24,0):
   base=g+(a['ocf']+(1-tax)*a['interest_expense'])/S
   runs.append({'NRR':nrr,'T':T,'H2_time':late,'tax_on_interest':tax,'annuity_end':base-crf*end_nom/S,'annuity_timeweighted':base-crf*avg_nom/S,'usercost_end':base-(r+d)*end_dec/S,'usercost_timeweighted':base-(r+d)*avg_dec/S})
out['acquirer_charge_scenarios']=runs
out['charge_ranges_tax24']={key:[min(z[key] for z in runs if z['tax_on_interest']==.24)*100,max(z[key] for z in runs if z['tax_on_interest']==.24)*100] for key in ('annuity_end','annuity_timeweighted','usercost_end','usercost_timeweighted')}
assert all(v=='0' for v in out['symbolic_residuals'].values())
assert abs(out['acquisition_bridge']['true_cash_charge_current_margin']-out['acquisition_bridge']['correct_simple_annual_formula'])<1e-12
assert out['horizon_counterexample']['total_npv_including_sale']>0
(here/'finance_results.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k not in ('acquirer_charge_scenarios','environment')},indent=2))
