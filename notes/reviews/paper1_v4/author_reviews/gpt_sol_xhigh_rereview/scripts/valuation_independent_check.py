"""Independent point-estimate and weak-denominator check; never imports author code.

This reads the filtered committed panel, not raw SEC filings. The Fieller set
is an asymptotic 90% Wald/Fieller diagnostic using firm-cluster covariance;
it is not presented as an exact finite-sample replacement for bootstrap inference.
"""
from pathlib import Path
import json, math
import numpy as np
import pandas as pd
from statistics import NormalDist

root=Path(__file__).resolve().parents[1]
src=root/'pinned_snapshot'
p=pd.read_csv(src/'data/panel_v3.csv',parse_dates=['fy_end'])
f=pd.read_csv(src/'data/v3_inputs/public_float.csv',parse_dates=['float_date'])
f=f.loc[f.public_float_usd_thousands>0]
d=p.merge(f,on='cik',how='left')
d['days']=(d.float_date-d.fy_end).dt.days
d=d.loc[d.days.between(120,260)].copy()
d['distance']=(d.days-182).abs()
d=d.sort_values('distance').drop_duplicates(['cik','fy_end']).sort_values(['cik','fy_end'])
d=d.loc[d.rev>0].copy()
d['response']=np.log(d.public_float_usd_thousands*1000/d.rev)
for col in ['g','m_op','m_fcf_sbc']:
    lo,hi=d[col].quantile([.01,.99])
    d[col+'_w']=d[col].clip(lo,hi)
z=NormalDist().inv_cdf(.95)
out=[]
stored=json.loads((src/'notes/open_questions/valuation.json').read_text())
for basis,col in [('cash','m_fcf_sbc_w'),('gaap','m_op_w')]:
    for sample,mask in [('all',pd.Series(True,index=d.index)),('2010-19',d.year<=2019),('2020-25',d.year>=2020),('top40',d.g_w+d[col]>=.4),('no_acq',~d.acq_flag_v3.fillna(False).astype(bool))]:
        q=d.loc[mask].dropna(subset=['response','g_w',col]).copy()
        years=pd.get_dummies(q.year.astype(str),drop_first=True,dtype=float)
        X=np.column_stack([np.ones(len(q)),q.g_w,q[col],years.to_numpy()])
        y=q.response.to_numpy()
        coef=np.linalg.lstsq(X,y,rcond=None)[0]
        bg,bm=coef[1:3]
        residual=y-X@coef
        groups=q.cik.to_numpy()
        unique=np.unique(groups)
        scores=np.array([(X[groups==g_]*residual[groups==g_,None]).sum(axis=0) for g_ in unique])
        bread=np.linalg.pinv(X.T@X)
        correction=len(unique)/(len(unique)-1)*(len(q)-1)/(len(q)-X.shape[1])
        cluster_cov=correction*bread@(scores.T@scores)@bread
        cov=cluster_cov[1:3,1:3]
        A=bm**2-z*z*cov[1,1]
        B=-2*bg*bm+2*z*z*cov[0,1]
        C=bg**2-z*z*cov[0,0]
        disc=B*B-4*A*C
        if disc<0:
            fieller={'shape':'all real numbers' if A<0 else 'empty','roots':None}
        else:
            roots=sorted([(-B-math.sqrt(disc))/(2*A),(-B+math.sqrt(disc))/(2*A)])
            fieller={'shape':'bounded interval between roots' if A>0 else 'two unbounded exterior intervals','roots':roots}
        s=stored[basis][sample]
        delta=max(abs(bg-s['beta_g']),abs(bm-s['beta_m']))
        assert delta<1e-10,(basis,sample,delta)
        se_delta=max(abs(math.sqrt(cov[0,0])-s['beta_g_se']),abs(math.sqrt(cov[1,1])-s['beta_m_se']))
        assert se_delta<1e-9,(basis,sample,'cluster covariance mismatch',se_delta)
        out.append({'basis':basis,'sample':sample,'n':len(q),'firms':int(q.cik.nunique()),'beta_g':float(bg),'beta_m':float(bm),
                    'max_coefficient_difference_from_committed':float(delta),'max_standard_error_difference_from_committed':float(se_delta),'fieller90_diagnostic':fieller,
                    'committed_ci':[None if not math.isfinite(v) else v for v in (s.get('weight_ci90') or [])],
                    'committed_nonpositive_or_nonfinite_share':s.get('weight_share_nonpositive')})
result={'scope':'Independent reimplementation of data matching and point regressions from committed processed data; no author program imported or executed, no raw SEC audit.',
        'inference_scope':'Fieller sets are asymptotic Wald diagnostics, using normal critical value and firm-cluster covariance. Signed ratio parameter; not a test of screening-weight model or a finite-sample coverage proof.',
        'seed':'Not applicable: deterministic calculations; no bootstrap rerun.',
        'matched':len(d),'results':out}
(root/'expert_notes/valuation_independent_check.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(result,indent=2,allow_nan=False))
