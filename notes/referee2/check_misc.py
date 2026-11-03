import json, pandas as pd, numpy as np
exec(open('/home/claude/paper/notes/referee2/check_frontier.py').read().split("P=['2010-15'")[0])
r=json.load(open('/home/claude/paper/notes/empirics_results.json'))
print('2023-25 median R on FCF (pre-SBC) basis:',round(100*r['desc']['m_fcf']['2023-25']['med_R'],1),'adjusted:',round(100*r['desc']['m_adj']['2023-25']['med_R'],1))
df=pd.read_csv('/home/claude/paper/data/panel.csv')
df['m_fcf_sbc_acq']=df.m_fcf_sbc-df.acq_pay.fillna(0).clip(lower=0)/df.rev
df.loc[(df.m_fcf_sbc_acq<-3)|(df.m_fcf_sbc_acq>1),'m_fcf_sbc_acq']=np.nan
P=['2010-15','2016-19','2020-22','2023-25']
print('frontier FCF-SBC-acq:',[round(100*fs(df[df.period==p],'m_fcf_sbc_acq')[0]) for p in P])
# AppLovin with total-company revenue for 2024 (4,709m) as denominator for cash margins
a=df.name.str.contains('AppLovin')&(df.year==2024)
x=df.loc[a].iloc[0]; print('AppLovin 2024 m_fcf_sbc panel',round(x.m_fcf_sbc,3),' on total revenue 4,709m:',round((x.fcf-x.sbc)/4.709e9,3))
