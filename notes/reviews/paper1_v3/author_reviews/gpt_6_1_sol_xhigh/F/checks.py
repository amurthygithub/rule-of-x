"""F's independent deterministic adversarial checks; no author/other-agent code imports."""
import hashlib
import json
import math
import platform
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def ols_slope(x, y):
    xb, yb = sum(x) / len(x), sum(y) / len(y)
    return sum((a-xb)*(b-yb) for a, b in zip(x, y)) / sum((a-xb)**2 for a in x)


def half_year_factor(rate, years):
    return (1 + (1+rate)**(-years))/(2*years) + sum((1+rate)**(-a) for a in range(1, years))/years


alpha, beta, ell, W, p, chi = .3, 1/.3, .721826999314566, .6, 14.833990914027952, .9
grid = [j*.05 for j in range(13)]
q = [W*(1-chi+chi*(g/W)**p)**(1/p) for g in grid]
m = [.8-(a/ell)**beta for a in q]
cone_slope = ols_slope(grid, m)
true_max_weight = beta*W**(beta-1)/ell**beta
multiplier = (beta+1)*(beta+2)/6
foc_max_error = 0.
for j in range(1, 101):
    g = W*j/100
    spend = (g/ell)**beta
    weight = beta*g**(beta-1)/ell**beta
    foc_max_error = max(foc_max_error, abs(alpha*weight*ell*spend**(alpha-1)-1))

tax = []
for growth in [.05, .10, .15, .30]:
    actual = half_year_factor(growth, 15)
    pv = half_year_factor(.1, 15)
    # Positive means paper's PV-equivalent cash score exceeds actual-vintage score.
    difference = .18*1.5*growth*(pv-actual)
    tax.append(dict(growth=growth, actual_cash_factor=actual, pv_factor=pv,
                    paper_minus_actual_score_points=100*difference))

annual = dict(prior_revenue=100, continuing_revenue=100, acquired_recognized_revenue=100,
              current_revenue=200, cash_price=300, price_per_recognized_revenue=3,
              actual_cash_charge=1.5, simple_component=1, log_component=math.log(2),
              mistaken_simple_product=3, mistaken_log_product=3*math.log(2),
              corrected_simple_charge=3/(1+1))

owner = dict(discount_rate=.1, exit_year=5, first_benefit_year=6,
             current_outlay=1, permanent_annual_benefit=.2)
owner['cash_pv_through_exit'] = -1
owner['exit_value'] = (.2/.1)*math.exp(-.1*(6-5))
owner['total_npv'] = -1+math.exp(-.1*5)*owner['exit_value']
owner['full_horizon_npv'] = -1+(.2/.1)*math.exp(-.1*6)
owner['terminal_value_fraction_break_even'] = 1/(math.exp(-.1*5)*owner['exit_value'])

cm, miss, N, n = .005, .02, 24, 3
temporal = dict(per_challenge_common_mode=cm, independent_miss=miss, challenges=N,
                ai_layers=n, iid_annual_floor=1-(1-cm)**N,
                persistent_annual_risk=cm+(1-cm)*(1-(1-miss**n)**N),
                three_ai_layers_plus_itgc_cost=3*50000+204672,
                outside_assumption_7=True)

# For 0<p<1 and constant capacity, after the last capacity-filled wave,
# U_{w+1}=(1-p)U_w>0. This finite calculation illustrates, not proves, the induction.
U, embedding_probability, capacity = 1., .8, .055
remaining = []
for wave in range(1, 41):
    U -= embedding_probability*min(capacity, U)
    remaining.append(dict(wave=wave, unembedded_mass=U))

# Independent local-ODE calculation at alpha=.5, k=G=0:
# rho*v-b = .25*(lambda*v)^2, hence .01*v^2-.1*v+.1=0.
v0 = (.1-math.sqrt(.1**2-4*.01*.1))/(2*.01)
delta0 = .2*(.5*.2*v0)
exponent = .1/delta0-1
local_ode = dict(alpha=.5, lambda_value=.2, rho=.1, m0=.1, k=0,
                 physical_share_cap=.5, v0=v0, delta0=delta0,
                 homogeneous_exponent=exponent,
                 forcing_coefficient_in_z=v0,
                 particular_linear_coefficient_in_z=v0/(1-exponent),
                 physical_s_coefficient=2*v0/(1-exponent),
                 interpretation='A supplementary universal asymptotic needs the forced term; no refutation of Proposition 2 limits.')

results = dict(
    provenance=dict(python=sys.version, platform=platform.platform(),
                    method='Independent standard-library deterministic arithmetic; no simulation or author code; no HJB re-solve.'),
    M1=dict(cone_projection_slope=cone_slope, max_support_weight=true_max_weight,
            paper_approx_multiplier=multiplier, inferred_max_weight=abs(cone_slope)*multiplier,
            physical_share=.25, physical_share_cap=.5, lambda_value=2*ell,
            max_spend=(W/ell)**beta, minimum_margin=.8-(W/ell)**beta,
            maximum_interior_foc_error=foc_max_error,
            scope='Heterogeneous-weight common-frontier narrative, outside formal common-X Assumption 5.'),
    M2=dict(schedule='Half-year 15-year deductions, fully mature balanced-growth vintage history; forward investment/revenue=kg.', cases=tax),
    M3=annual, M4=owner, D3=dict(two_objective_union=1-.96**2, two_submaterial_joint=.2**2),
    D4=temporal, D2=dict(capacity=capacity, probability=embedding_probability,
                       records=remaining, exact_finite_completion=False),
    A1=local_ode,
    G1000=dict(G=9.5, m0=.5, k=0, X=1, physical_cap=.5, initial_share=.1,
               spend=0, permanent_score=9.5+.5,
               scope='Extreme permitted static parameter example; not an economically relevant headline refutation.'),
)
assert abs(cone_slope+.22) < 1e-12
assert abs(true_max_weight-3) < 1e-12
assert abs(annual['corrected_simple_charge']-annual['actual_cash_charge']) < 1e-12
assert abs(owner['total_npv']-owner['full_horizon_npv']) < 1e-12
assert temporal['persistent_annual_risk'] < .01
assert all(x['unembedded_mass'] > 0 for x in remaining)
assert exponent > 1
(OUT/'results.json').write_text(json.dumps(results, indent=2)+'\n')
print(json.dumps({k:v for k,v in results.items() if k != 'D2'}, indent=2))
print('All deterministic assertions passed. D2 trajectory retained in results.json.')
