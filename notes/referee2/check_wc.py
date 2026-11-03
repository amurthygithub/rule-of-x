import pandas as pd, numpy as np, statsmodels.formula.api as smf
df=pd.read_csv('/home/claude/paper/data/panel.csv')
df['gap']=df.m_fcf_sbc-df.m_op   # cash-minus-accrual margin (both burden SBC)
d=df[['cik','year','g','gap']].dropna(); d=d[(d.g<=1.5)&(d.gap.abs()<1)]
fe=smf.ols('gap ~ g + C(year) + C(cik)',d).fit(cov_type='cluster',cov_kwds={'groups':d.cik})
po=smf.ols('gap ~ g + C(year)',d).fit(cov_type='cluster',cov_kwds={'groups':d.cik})
print('FCF-after-SBC minus GAAP margin on growth: pooled %.3f (%.3f), firm FE %.3f (%.3f), n=%d'%(po.params.g,po.bse.g,fe.params.g,fe.bse.g,len(d)))
q=smf.quantreg('gap ~ g',d).fit(q=.5); print('median reg slope %.3f (%.3f)'%(q.params.g,q.bse.g))
# share of rows where all margins missing
print('rows with no GAAP margin',df.m_op.isna().sum(),' with neither m_op nor m_fcf_sbc',(df.m_op.isna()&df.m_fcf_sbc.isna()).sum())
