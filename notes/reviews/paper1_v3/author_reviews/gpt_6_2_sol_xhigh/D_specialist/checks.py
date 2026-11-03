"""Independent review calculations, written from manuscript formulas; no author code used."""
import json, math
from pathlib import Path


def miss(nh,na,pcc=0):
    h=.002+(1-.002)*.05**nh if nh else 1
    a=.005+(1-.005)*.02**na if na else 1
    return pcc+(1-pcc)*h*a

control={}
for threshold in [.05,.01]:
    choices=[]
    for nh in range(0,25):
        for na in range(0,25):
            p=miss(nh,na)
            period=-math.expm1(24*math.log1p(-p)) if p<1 else 1
            cost=500000*nh+50000*na+(204672 if na else 0)
            if period<=threshold: choices.append((cost,nh,na,p,period))
    best=min(choices)
    control[str(threshold)]={'per_challenge_threshold':-math.expm1(math.log1p(-threshold)/24),'cheapest':{'cost':best[0],'human':best[1],'AI':best[2],'p_challenge':best[3],'p_period':best[4]}}
control['single_AI_infinite_depth_period_floor']=-math.expm1(24*math.log1p(-.005))
control['single_human_infinite_depth_period_floor']=-math.expm1(24*math.log1p(-.002))
# Same marginal common-mode probability per material challenge, but one persistent provider state per year.
control['persistent_AI_common_state']={str(n):.005+.995*(-math.expm1(24*math.log1p(-.02**n))) for n in [1,2,3,4]}
control['persistent_AI_three_layers_cost']=204672+3*50000
# Annual aggregation illustration; each challenge is already a material-error challenge.
control['two_objectives_each_4pct_period_union']=1-(1-.04)**2
control['ten_objective_equal_allocation_5pct_firm']=1-(1-.05)**.1


def fluid(p,cw,n):
    u=1
    rows=[]
    for w in range(1,n+1):
        attempted=min(cw,u)
        u-=p*attempted
        rows.append({'wave':w,'E':1-u,'unembedded':u,'upper':min(1,p*cw*w),'attempted':attempted})
    return rows
# A quarterly wave is an admissible illustration, not an author-code reproduction. It recovers the central rounded shares, but not every fast-case share; the printed text does not specify Tpar.
execution={}
for label,p,rho,unfrozen,emb,b in [('central',.7,.1,.9,1.25,.67),('fast',.8,.22,.98,1,.85)]:
    rows=fluid(p,rho*.25,80)
    horizons={}
    for t in [3,6,7,11,17]:
        n=max(0,math.floor((t*unfrozen-emb)/.25+1e-12)+1)
        row=rows[n-1] if n else {'E':0,'unembedded':1,'upper':0}
        horizons[str(2025+t)]={'n':n,**row,'realized':b*row['E'],'upper_realized':b*row['upper']}
    execution[label]={'assumed_Tpar':.25,'horizons':horizons,'strict_finite_completion':False,'recurrence':'U_w=U_(w-1)-p*min(cw,U_(w-1))'}
# Finite 48-process benchmark: even with unlimited concurrent retries, there is positive noncompletion probability.
execution['finite_48_all_complete_after_10_rounds_p80']=(1-.2**10)**48
execution['finite_48_all_complete_after_5_rounds_p80']=(1-.2**5)**48
# Simple ownership counterexample: cost 14 today, annual benefit 2 for 20 years, sold after 5 at PV of remaining benefits.
r=.1
ann=lambda n:(1-(1+r)**(-n))/r
ownership={'cost':14,'annual_benefit':2,'life_years':20,'holding_years':5,'discount':r,'undiscounted_5yr_net_cash':-14+5*2,'undiscounted_payback':7,'exit_value_5':2*ann(15),'PV_5yr_cash':2*ann(5),'PV_exit':2*ann(15)/(1+r)**5,'NPV_5yr_including_exit':-14+2*ann(5)+2*ann(15)/(1+r)**5,'NPV_full_life':-14+2*ann(20)}
# Random freeze formula and finite horizon counterexample in the manuscript, independently checked.
nuD,nuR,Temb,Tfrz=.23,.5,1.25,2
freeze={'random_survival':math.exp(-nuD*Temb-nuR*Temb*(1-math.exp(-nuD*Tfrz))),'uniform_survival':math.exp(-nuD*(1+nuR*Tfrz)*Temb),'no_freeze_first_unit':math.exp(-.5)}
# Selection effect only matters if the fluid part retains heterogeneous, observed persistent benefits and arbitrary reversion.
selection={'mean_b':.5,'one_wave_embeds_all_then_revert_b0':{'retained_embedded_mass':.5,'actual_realized_benefit':.5,'bbar_times_retained_mass':.25}}
results={'controls':control,'execution':execution,'ownership':ownership,'random_freeze':freeze,'fluid_selection_conditional_counterexample':selection}
Path('work/D_independent/results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
