import json, pandas as pd, numpy as np
fx=json.load(open('/home/claude/paper/data/frames_extra.json'))
df=pd.read_csv('/home/claude/paper/data/panel.csv')
ends=[]
for _,r in df.iterrows():
    v=fx.get(f'Goodwill|{r.year}',{}).get(str(r.cik))
    ends.append(v[2] if v else None)
df['gw_end']=pd.to_datetime(pd.Series(ends),errors='coerce')
df['fye']=pd.to_datetime(df.fy_end,errors='coerce')
df['gap']=(df.gw_end-df.fye).dt.days.abs()
h=df[df.gw_end.notna()]
print('firm-years with goodwill instant:',len(h))
print('share with |gw date - FYE|>45 days:', (h.gap>45).mean().round(3), ' count', (h.gap>45).sum())
print('non-Dec FYE share of sample:', (df.fye.dt.month!=12).mean().round(3))
print('acq_flag=1 rows where gw date misaligned >45d:', ((df.acq_flag==1)&(df.gap>45)).sum(), 'of', df.acq_flag.sum())
# acq flag from payment only vs goodwill only
pay=(df.acq_pay.fillna(0)>=.25*df.rev_lag); gw=(df.gw_jump.fillna(0)>=.25*df.rev_lag)
print('flag via payment only',(pay&~gw).sum(),'goodwill only',(gw&~pay).sum(),'both',(pay&gw).sum())
print('acq_pay missing share',df.acq_pay.isna().mean().round(3),'gw_jump missing share',df.gw_jump.isna().mean().round(3),'both missing',(df.acq_pay.isna()&df.gw_jump.isna()).mean().round(3))
# flag in t-1 but not t (partial-year consolidation effect)
df=df.sort_values(['cik','year']); df['flag_lag']=df.groupby('cik').acq_flag.shift(1)
print('firm-years unflagged but flagged in t-1:',((df.acq_flag==0)&(df.flag_lag==1)).sum())
# G&A share for large firms
df['ga_share']=df.ga/df.rev
big=df[df.rev_lag>=10e9]
print('G&A/revenue, prior rev>=$10B: median',big.ga_share.median().round(3),'p10',big.ga_share.quantile(.1).round(3),'min',big.ga_share.min().round(3))
print(big.groupby('name').ga_share.median().sort_values().head(12).round(3))
mid=df[(df.rev_lag>=1e9)]
print('G&A/rev prior>=1B: p5',mid.ga_share.quantile(.05).round(3),'median',mid.ga_share.median().round(3))
