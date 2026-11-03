import json, pandas as pd, numpy as np
pd.set_option('display.width',250)
exec(open('/home/claude/paper/notes/referee2/check_frontier.py').read().split("P=['2010-15'")[0])
df=pd.read_csv('/home/claude/paper/data/panel.csv')
u=json.load(open('/home/claude/paper/data/sic_universe.json')); st={int(r[1]):r[3] for r in u}
df['state']=df.cik.map(st).fillna('')
US=set('AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR'.split())|{''}
df['us']=df.state.isin(US)
print('explicit non-US address share:',round(1-df.us.mean(),3), df[~df.us].state.value_counts().head(8).to_dict())
P=['2010-15','2016-19','2020-22','2023-25']
for lab,sub in [('US/unknown address',df[df.us])]:
    print(lab,len(sub),[f'{100*fs(sub[sub.period==p],m)[0]:.0f}' for m in ['m_op','m_fcf_sbc'] for p in P])
# hand list of clearly non-software businesses among large names
pat=('Alphabet|GOOGLE INC|Meta Platforms|Baidu|Snap Inc|PINTEREST|TWITTER|Match Group|TripAdvisor|WEIBO|JOYY|Autohome|Bilibili|Hello Group|Yalla|Sohu|SINA|Nebius|YANDEX|'
     'Flutter|Light & Wonder|BALLY|DraftKings|'
     'AUTOMATIC DATA|PAYCHEX|Block, Inc|Toast|FISERV|FIDELITY NATIONAL INFO|GLOBAL PAYMENTS|BROADRIDGE|WEX|EURONET|'
     'COGNIZANT|DXC|COMPUTER SCIENCES|EPAM|Kyndryl|Leidos|CACI|Science Applications|PARSONS|UNISYS|Perspecta|CSRA|MANTECH|Booz|GENPACT|CONDUENT|'
     'People Inc|IAC|Sabre|Liberty TripAdvisor|Exzeo')
df['nonsw']=df.name.str.contains(pat,case=False,regex=True)
print('hand-flagged internet/IT-services/payments/gaming firm-years:',df.nonsw.sum(),'share',round(df.nonsw.mean(),3),'firms',df[df.nonsw].cik.nunique())
sub=df[~df.nonsw]
print('excluding hand-flagged:',len(sub),[f'{100*fs(sub[sub.period==p],m)[0]:.0f}' for m in ['m_op','m_fcf_sbc'] for p in P])
print(df[df.name.str.contains('Exzeo')][['name','sic','year','rev','rev_lag','g','m_op','m_fcf_sbc','state']].to_string())
# gross margin of SIC 7372 2023-25
s=df[(df.sic==7372)&(df.period=='2023-25')]
print('SIC7372 2023-25 median GAAP gross margin',round(s.gm.median(),3),'IQR',s.gm.quantile([.25,.75]).round(3).tolist())
# SBC/revenue at the top
df['sbc_r']=df.sbc/df.rev; df['R']=df.g+df.m_op
print('median SBC/rev, R_op>=60:',round(df[df.R>=.6].sbc_r.median(),3),' all:',round(df.sbc_r.median(),3))
# applovin capex flag
print(df[df.name.str.contains('AppLovin')][['year','capex_ppe','capex_missing','cap_sw']].to_string())
# capital split membership 2023-25
d=df[df.period=='2023-25'].copy(); d['hi']=d.capex_int>d.capex_int.median()
for h in [False,True]:
    x=d[d.hi==h]; s,gs=fs(x,'m_fcf_sbc'); print('hi' if h else 'lo', round(100*s), gs, x[x.g>=gs].nlargest(3,'m_fcf_sbc')[['name','year','g','m_fcf_sbc','capex_int']].to_dict('records'))
# scale: frontier restricted to common growth support g<=0.30
GR=GRID
bins=[100e6,500e6,2e9,10e9,1e13]; df['sb']=pd.cut(df.rev_lag,bins,right=False)
for m in ['m_op','m_fcf_sbc']:
    out=[]
    for b,dd in df.groupby('sb',observed=True):
        f=oa(dd.dropna(subset=['g',m]).g.values, dd.dropna(subset=['g',m])[m].values)
        v=GR+f; ok=GR<=0.30
        out.append((round(100*np.nanmax(v[ok])), round(100*GR[~np.isnan(f)].max())))
    print(m,'frontier score restricted to g<=30% (score, support):',out)
