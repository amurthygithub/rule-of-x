import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_rows',200)
df=pd.read_csv('/home/claude/paper/data/panel.csv')
GRID=np.round(np.arange(0,1.01,0.05),2)
def oa(gv,mv,a=.95):
    out=np.full(len(GRID),np.nan)
    for k,g0 in enumerate(GRID):
        s=mv[gv>=g0]
        if len(s)>=30: out[k]=np.quantile(s,a)
    return out
def fs(d,m):
    d=d[['g',m]].dropna(); f=oa(d.g.values,d[m].values); v=GRID+f
    if np.all(np.isnan(v)): return np.nan,np.nan
    k=int(np.nanargmax(v)); return v[k],GRID[k]
P=['2010-15','2016-19','2020-22','2023-25']
for m in ['m_op','m_fcf_sbc']:
    for p in P:
        d=df[df.period==p]
        s,gs=fs(d,m)
        sub=d[(d.g>=gs)][['name','year','g',m]].dropna().sort_values(m,ascending=False)
        print(f'\n{m} {p} score={s:.3f} g*={gs} n(g>=g*)={len(sub)}')
        print(sub.head(4).to_string())
        # leave-one-firm-out
        res=[]
        for c in d.cik.unique():
            s2,_=fs(d[d.cik!=c],m); res.append((s2-s,c))
        res.sort()
        nm=d.drop_duplicates('cik').set_index('cik').name
        print('  LOFO largest drops:',[(nm[c],round(x*100,1)) for x,c in res[:3]])
