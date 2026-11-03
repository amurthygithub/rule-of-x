import re, json
mac = open('/root/Paper Review/work/repo/rule-of-x/paper1/macros.tex').read()
def val(name):
    m = re.search(r'\\newcommand\\{%s}{([^}]*)}' % re.escape(name), mac)
    return m.group(1) if m else None
cases = {
 'Favorable': dict(cc=0.03, f=0.020, amin=0.015, tau=0.15, cfull=float(val('CfullFav'))/100, margin=float(val('MarginFav')), gstar=float(val('GstarFavOne')), a=val('CeilFavFive'), b=val('CeilFavFifteen'), c=val('CeilFavThirty')),
 'Central': dict(cc=0.06, f=0.025, amin=0.030, tau=0.18, cfull=float(val('CfullCen'))/100, margin=float(val('MarginCen')), gstar=float(val('GstarCenOne')), a=val('CeilCenFive'), b=val('CeilCenFifteen'), c=val('CeilCenThirty')),
 'Conservative': dict(cc=0.12, f=0.030, amin=0.046, tau=0.21, cfull=float(val('CfullCons'))/100, margin=float(val('MarginCons')), gstar=float(val('GstarConsOne')), a=val('CeilConsFive'), b=val('CeilConsFifteen'), c=val('CeilConsThirty')),
 'HighCompute': dict(cc=0.40, f=0.025, amin=0.030, tau=0.18, cfull=float(val('CfullHigh'))/100, margin=float(val('MarginHighR')), gstar=float(val('GstarHighOne')), a=None,b=None,c=None),
}
out={}
for name,c in cases.items():
    base=(1-c['tau'])*(1-c['cc']-c['f']-c['amin']-c['cfull'])
    gstar=c['tau']+(1-c['tau'])*(c['cc']+c['f']+c['amin']+c['cfull'])
    out[name]=dict(base_calc=round(base*100,1), margin_paper=c['margin'], gstar_calc=round(gstar*100,1), gstar_paper=c['gstar'],
                   RmaxG005=round((base+0.05)*100,1), paper_a=c['a'], RmaxG015=round((base+0.15)*100,1), paper_b=c['b'], RmaxG030=round((base+0.30)*100,1), paper_c=c['c'])
print(json.dumps(out, indent=1))
# pass-through check: phi=0.5, saving share PtCzero of price
pt = float(val('PtCzero'))
cc,f,amin,tau,cfull = 0.06,0.025,0.030,0.18,float(val('CfullCen'))/100
cut = 0.5*pt/100
Gstar_phi = tau + (1-tau)*(cc+f+amin+cfull)/(1-cut)
print('phi=0.5 cut=%.2f%% paper PtPriceCutHalf=%s Gstar calc=%.1f paper=%s' % (cut*100, val('PtPriceCutHalf'), Gstar_phi*100, val('GstarPhiHalfOne')))
