import json, pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_rows',200)
f=json.load(open('/home/claude/paper/data/frames_universe.json'))
REV=['Revenues','RevenueFromContractWithCustomerExcludingAssessedTax','RevenueFromContractWithCustomerIncludingAssessedTax','SalesRevenueNet','SalesRevenueServicesNet']
df=pd.read_csv('/home/claude/paper/data/panel.csv')
alt=[]
for i,r in df.iterrows():
    vals={c:f.get(f'{c}|{r.year}',{}).get(str(r.cik)) for c in REV}
    vals={c:v[0] for c,v in vals.items() if v}
    mx=max(vals.values()) if vals else np.nan
    alt.append(mx)
df['rev_max']=alt
df['ratio']=df.rev/df.rev_max
b=df[df.ratio<0.8]
print('firm-years where chosen revenue < 80% of largest alternative revenue element:',len(b))
print(b[['name','year','rev_src','rev','rev_max','m_op','m_fcf_sbc','g']].to_string())
hi=df[df.m_op>0.55][['name','year','rev','rev_src','op_inc','m_op','g']]
print('\nGAAP op margin > 55%:',len(hi)); print(hi.to_string())
print('\nneg capex/sbc/capsw rows'); print(df[(df.capex_ppe<0)|(df.sbc<0)|(df.cap_sw<0)][['name','year','capex_ppe','sbc','cap_sw']].to_string())
