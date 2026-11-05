"""Recompute the full-automation ceiling table (eq Rmax, psi=0, delta=0) from macro values
and check G* threshold formula G* = tau + (1-tau)(c_c+f+a_min+c_full) for k=0."""
import json
# central case macros
tau=0.18; cc=0.06; f=None; amin=0.030; cfull=6.23/100
# need Fee central: grep macros
import re
mac = open('/root/Paper Review/work/repo/rule-of-x/paper1/macros.tex').read()
def val(name, default=None):
    m = re.search(r'\\newcommand\\{%s}{([^}]*)}' % re.escape(name), mac)
    return m.group(1) if m else default
print('FeeCen', val('CeilFCen'), 'FeeLo', val('FeeLo'), 'FeeHi', val('FeeHi'))
print('CeilTauCen', val('CeilTauCen'), 'CeilAminCen', val('CeilAminCen'), 'CeilCcCen', val('CeilCcCen'), 'CfullCen', val('CfullCen'))
print('MarginCen', val('MarginCen'), 'GstarCenOne', val('GstarCenOne'))
fee = float(val('CeilFCen'))/100
tau = float(val('CeilTauCen'))/100 if float(val('CeilTauCen'))<1 else float(val('CeilTauCen'))/100
cc = float(val('CeilCcCen'))  # 0.06
amin_c = float(val('CeilAminCen'))  # 0.030
cfull_c = float(val('CfullCen'))/100  # 6.23 -> 0.0623
base = (1-tau)*(1-cc-fee-amin_c-cfull_c)
print('computed base (central, k=0,G=0):', round(base*100,2), 'paper MarginCen:', val('MarginCen'))
Gstar = tau + (1-tau)*(cc+fee+amin_c+cfull_c)
print('computed G* (central):', round(Gstar*100,2), 'paper GstarCenOne:', val('GstarCenOne'))
for G in [0.05,0.15,0.30]:
    print(f'  Rmax(G={G},k=0) = {round((base+(1-0)*G)*100,2)}  paper: CeilCenFive={val("CeilCenFive")} CeilCenFifteen={val("CeilCenFifteen")} CeilCenThirty={val("CeilCenThirty")}')
# pass-through phi: price falls by phi * unit-cost saving; check claim G* rises to GstarPhiHalfOne=36.2 at phi=0.5
# saving = top-tail anchor firm's own from unit cost PtCzero of price. Pass-through: p' = p - phi*(saving)*p? Check formula: price cut PtPriceCutHalf; threshold = tau+(1-tau)(cc+f+amin+cfull)/ (1 - phi*share?) ... just check internal consistency: G*_phi = tau + (1-tau)*(cost shares at lower price). Cost shares scale by p_old/p_new = 1/(1-phi*s) where s = saving share of price.
PtCzero = float(val('PtCzero'))/100
phi=0.5
cut = phi*PtCzero
Gstar_phi = tau + (1-tau)*(cc+fee+amin_c+cfull_c)/(1-cut)
print('phi=0.5: price cut', round(cut*100,2), '% paper PtPriceCutHalf:', val('PtPriceCutHalf'), '; G* computed', round(Gstar_phi*100,2), 'paper GstarPhiHalfOne:', val('GstarPhiHalfOne'))
