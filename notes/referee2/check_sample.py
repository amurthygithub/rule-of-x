import json, pandas as pd, numpy as np
pd.set_option('display.width',250)
exec(open('/home/claude/paper/notes/referee2/check_frontier.py').read().split("P=['2010-15'")[0])
df=pd.read_csv('/home/claude/paper/data/panel.csv')
u=json.load(open('/home/claude/paper/data/sic_universe.json')); st={int(r[1]):r[3] for r in u}
df['state']=df.cik.map(st)
US=set('AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR'.split())
df['us']=df.state.isin(US)
print('non-US business address share:', round(1-df.us.mean(),3), ' F4 (China) firm-years:', (df.state=='F4').sum())
P=['2010-15','2016-19','2020-22','2023-25']
rows=[]
for lab,sub in [('baseline',df),('SIC 7372 only',df[df.sic==7372]),('US address only',df[df.us]),('7372 & US',df[(df.sic==7372)&df.us]),('capex reported',df[~df.capex_missing])]:
    r=[lab,len(sub)]
    for m in ['m_op','m_fcf_sbc']:
        for p in P:
            s,g=fs(sub[sub.period==p],m); r.append(f'{100*s:.0f}@{100*g:.0f}' if s==s else 'na')
    rows.append(r)
print(pd.DataFrame(rows,columns=['sample','N']+[f'{m}:{p}' for m in ['op','fcfsbc'] for p in P]).to_string())
# drop top-2 firms per period (by LOFO)
for m in ['m_op','m_fcf_sbc']:
    for p in P:
        d=df[df.period==p]; base,_=fs(d,m)
        drops=sorted([(fs(d[d.cik!=c],m)[0],c) for c in d.cik.unique()])[:2]
        s2,_=fs(d[~d.cik.isin([c for _,c in drops])],m)
        print(m,p,'base',round(100*base),'drop top-2 firms ->',round(100*s2))
# p99 by year
R=df.assign(R=df.g+df.m_op,Rf=df.g+df.m_fcf_sbc).groupby('year')[['R','Rf']].quantile(.99).mul(100).round(0)
print(R.T.to_string())
print('years with GAAP p99>=95:',(R.R>=95).sum(),'of',len(R), '; FCF-SBC p99>=95:',(R.Rf>=95).sum())
# scale: subsample-size matched frontier
rng=np.random.default_rng(1)
bins=[100e6,500e6,2e9,10e9,1e13]; df['sb']=pd.cut(df.rev_lag,bins,right=False)
for m in ['m_op','m_fcf_sbc']:
    out=[]
    for b,d in df.groupby('sb',observed=True):
        vals=[]
        for _ in range(200):
            dd=d.sample(n=139,replace=False,random_state=rng.integers(1e9)) if len(d)>139 else d
            vals.append(fs(dd,m)[0])
        out.append((str(b),len(d),round(100*np.nanmedian(vals)),round(100*np.mean(np.isnan(vals)),0)))
    print(m,'size-matched (n=139) frontier score median:',out)
