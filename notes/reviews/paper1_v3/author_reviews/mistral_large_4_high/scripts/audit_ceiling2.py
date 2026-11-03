import re, json
mac = open('/root/Paper Review/work/repo/rule-of-x/paper1/macros.tex').read()
def val(name):
    m = re.search(r'\\newcommand\\{%s}{([^}]*)}' % re.escape(name), mac)
    return m.group(1) if m else None
cases = {
 'Favorable': dict(cc=float(val('CeilCcFav')), f=float(val('CeilFFav')), amin=float(val('CeilAminFav')), tau=float(val('CeilTauFav')), cfull=float(val('CfullFav'))/100, margin=float(val('MarginFav')), gstar=float(val('GstarFavOne'))),
 'Central': dict(cc=float(val('CeilCcCen')), f=float(val('CeilFCen')), amin=float(val('CeilAminCen')), tau=float(val('CeilTauCen')), cfull=float(val('CfullCen'))/100, margin=float(val('MarginCen')), gstar=float(val('GstarCenOne'))),
 'Conservative': dict(cc=float(val('CeilCcCons')), f=float(val('CeilFCons')), amin=float(val('CeilAminCons')), tau=float(val('CeilTauCons')), cfull=float(val('CfullCons'))/100, margin=float(val('MarginCons')), gstar=float(val('GstarConsOne'))),
 'High compute': dict(cc=float(val('CeilCcHigh')), f=float(val('CeilFHigh')), amin=float(val('CeilAminHigh')), tau=float(val('CeilTauHigh')), cfull=float(val('CfullHigh'))/100, margin=float(val('MarginHighR')), gstar=float(val('GstarHighOne'))),
}
out={}
for name,c in cases.items():
    base = (1-c['tau'])*(1-c['cc']-c['f']-c['amin']-c['cfull'])
    gstar = c['tau'] + (1-c['tau'])*(c['cc']+c['f']+c['amin']+c['cfull'])
    out[name] = dict(base_computed=round(base*100,2), margin_paper=c['margin'],
                     gstar_computed=round(gstar*100,2), gstar_paper=c['gstar'],
                     Rmax_G005=round((base+0.05)*100,1), Rmax_G015=round((base+0.15)*100,1), Rmax_G030=round((base+0.30)*100,1))
print(json.dumps(out, indent=1))
# paper table values for comparison
for t in ['CeilTabFavA','CeilTabFavB','CeilTabFavC','CeilTabCenA','CeilTabCenB','CeilTabCenC','CeilTabConsA','CeilTabConsB','CeilTabConsC','CeilTabHighA','CeilTabHighB','CeilTabHighC','CeilFavFive','CeilFavFifteen','CeilFavThirty','CeilCenFive','CeilCenFifteen','CeilCenThirty','CeilConsFive','CeilConsFifteen','CeilConsThirty','GstarFavOne','GstarConsOne','GstarHighOne']:
    print(t, '=', val(t))
