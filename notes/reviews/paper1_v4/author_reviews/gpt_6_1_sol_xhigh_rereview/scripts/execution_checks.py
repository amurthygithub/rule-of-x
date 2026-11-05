"""Independent exact checks from printed assumptions, not repository reproduction.

No random seed: every calculation is deterministic or exact enumeration.
"""
from pathlib import Path
import json, math

ROOT=Path(__file__).resolve().parents[1]
out={"scope":"Printed-parameter calculations only; not a run of the repository or its stored outputs", "seed":"not applicable: exact enumeration/deterministic arithmetic"}

# Randomized Latin hypercube with n=2, d=2. Each marginal uses lower and upper
# half once. The two relative stratum permutations are equally probable.
# Indicator is 1 exactly when coordinates are in the same half.
lhs_share=[1.0,0.0]
mean=sum(lhs_share)/2
lhs_var=sum((x-mean)**2 for x in lhs_share)/2
iid_var=0.5*(1-0.5)/2
out['lhs_counterexample']={"n":2,"d":2,"event":"coordinates fall in same half of [0,1]", "share_possible_values":lhs_share,"each_value_probability":0.5,"true_share_variance":lhs_var,"iid_binomial_share_variance":iid_var,"true_se_over_iid_se":math.sqrt(lhs_var/iid_var),"implication":"The iid share standard error need not overstate randomized-LHS error; iid order-statistic/binomial laws do not automatically apply to dependent LHS outputs."}

def recurrence(rho,tpar,p,b,temb):
    cw=rho*tpar
    n_upper=math.ceil(1/(p*cw))
    u=1.0
    first99=None
    for n in range(1,10000):
        u-=p*min(cw,u)
        if 1-u>=.99:
            first99=n
            break
    return {"rho":rho,"Tpar":tpar,"p":p,"b":b,"cw":cw,
            "upper_bound_whole_program_wave":n_upper,"exact_99_percent_wave":first99,
            "upper_bound_program_time":temb+(n_upper-1)*tpar,
            "exact_99_program_time":temb+(first99-1)*tpar,
            "benefit_shortfall_bound":b*cw,
            "finite_exact_completion":"never: U>0 geometrically after capacity becomes slack"}
out['program_recurrence']={
    'central':recurrence(.10,.17,.70,.67,1.25),
    'fast':recurrence(.22,.08,.80,.85,1.0),
    'note':'Values from supplement S2.7/S2.9 and TableS11 pp38-39. Dates here are program time; calendar freeze law is deliberately not guessed.'}

p0,p1,T=1,.71,11
price_log_growth=math.log(p1/p0)/T
quantity_log_growth=.129
out['price_revenue_identity']={"identity":"S=p*Q; dlog(S)=dlog(p)+dlog(Q)","illustrative_price_ratio":p1,"years":T,"illustrative_constant_quantity_log_growth":quantity_log_growth,"constant_log_price_growth":price_log_growth,"implied_revenue_log_growth":quantity_log_growth+price_log_growth,"note":"Example of the accounting identity only. Not a correction to S12.2's actual path, whose year-by-year prices have not been provided in the PDFs."}

out['central_execution_exception']={"printed_min_payback_years":4.99,"less_than_five":4.99<5,"implication":"The condition 'central execution' alone does not imply failure of a five-year cash-payback test; main pp5/64 need central-other-input or exception qualifiers."}
out['positive_capital_counterexample']={"after_tax_intercept":.675,"capital_intensity":.5,"deductibility_psi":0,"market_growth":.7,"mature_cash_score":.675+(1-.5)*.7,"note":"Static score counterexample only: no claim that 70% mature software-market growth is empirically plausible. Shows negligible capital needs are not a mathematical necessity of score>100."}
out['negative_cash_capital_counterexample']={"after_tax_intercept":.675,"capital_intensity":-.3,"deductibility_psi":0,"market_growth":.26,"mature_cash_score":.675+(1+.3)*.26,"note":"Matches the negative cash capital extension acknowledged on main p60: sustained score>100 at growth below32.5%, so the central k=0 threshold is not a universal necessary condition."}
(ROOT/'results'/'execution_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
