import re, json
mac = open('/root/Paper Review/work/repo/rule-of-x/paper1/macros.tex').read()
def val(name):
    m = re.search(r'\\newcommand{\\%s}{([^}]*)}' % name, mac)
    return m.group(1) if m else None
cfull = {'Central': float(val('CfullCen'))/100, 'Favorable': float(val('CfullFav'))/100, 'Conservative': float(val('CfullCons'))/100, 'HighCompute': float(val('CfullHigh'))/100}
cases = {
 'Favorable': dict(cc=0.03, f=0.020, amin=0.015, tau=0.15, margin=float(val('MarginFav')), gstar=float(val('GstarFavOne')), a=val('CeilFavFive'), b=val('CeilFavFifteen'), c=val('CeilFavThirty')),
 'Central': dict(cc=0.06, f=0.025, amin=0.030, tau=0.18, margin=float(val('MarginCen')), gstar=float(val('GstarCenOne')), a=val('CeilCenFive'), b=val('CeilCenFifteen'), c=val('CeilCenThirty')),
 'Conservative': dict(cc=0.12, f=0.030, amin=0.046, tau=0.21, margin=float(val('MarginCons')), gstar=float(val('GstarConsOne')), a=val('CeilConsFive'), b=val('CeilConsFifteen'), c=val('CeilConsThirty')),
 'HighCompute': dict(cc=0.40, f=0.025, amin=0.030, tau=0.18, margin=float(val('MarginHighR')), gstar=float(val('GstarHighOne')), a=None,b=None,c=None),
}
out={}
for name,c in cases.items():
    cf = cfull[name]
    base=(1-c['tau'])*(1-c['cc']-c['f']-c['amin']-cf)
    gstar=c['tau']+(1-c['tau'])*(c['cc']+c['f']+c['amin']+cf)
    out[name]=dict(base_calc=round(base*100,2), margin_paper=c['margin'],
                   gstar_calc=round(gstar*100,2), gstar_paper=c['gstar'],
                   Rmax_G005=round((base+0.05)*100,1), paper_a=c['a'],
                   Rmax_G015=round((base+0.15)*100,1), paper_b=c['b'],
                   Rmax_G030=round((base+0.30)*100,1), paper_c=c['c'])
print(json.dumps(out, indent=1))
pt = float(val('PtCzero'))
cc,f,amin,tau,cf = 0.06,0.025,0.030,0.18,cfull['Central']
for phi, name in [(0.5,'GstarPhiHalfOne'),(0.7,'GstarPhiSevenOne')]:
    cut = phi*pt/100
    g = tau + (1-tau)*(cc+f+amin+cf)/(1-cut)
    print('phi=%.1f cut=%.2f%% paper PtPriceCut=%s Gstar calc=%.1f paper %s=%s' % (phi, cut*100, val('PtPriceCutHalf') if phi==0.5 else val('PtPriceCutSeven'), g*100, name, val(name)))
json.dump(out, open('/root/tmp/review/out/audit_ceiling.json','w'), indent=1)
