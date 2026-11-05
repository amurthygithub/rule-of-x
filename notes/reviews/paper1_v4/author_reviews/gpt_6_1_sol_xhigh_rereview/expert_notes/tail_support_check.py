"""Counts committed filtered E1 support without executing an author program."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

root=Path(__file__).resolve().parents[1]
p=pd.read_csv(root/'pinned_snapshot/data/panel_v3.csv')
out=[]
for label,sel,threshold in [('pooled',p.g>=.6,.6),('early2010_19',(p.g>=.4)&(p.year<=2019),.4),('late2020_25',(p.g>=.4)&(p.year>=2020),.4),('recent2023_25',(p.g>=.4)&(p.year>=2023),.4)]:
    for basis in ['m_op','m_fcf_sbc']:
        d=p.loc[sel&p[basis].notna()]
        by=d.groupby('cik').size()
        out.append({'sample':'E1','period':label,'growth_threshold':threshold,'basis':basis,'firm_years':len(d),
                    'distinct_firms':len(by),'largest_firm_year_count':int(by.max()),'largest_firm_share':float(by.max()/len(d))})
# Standalone numerical diagnostic, not a rerun of a paper bootstrap.
a=np.r_[np.arange(939,dtype=float),np.full(60,np.inf)]
with np.errstate(invalid='ignore'):
    q=np.quantile(a,[.05,.95]).tolist()
result={'scope':'Independent counts from committed filtered panel; no raw-data audit or author program run.',
        'seed':'Not applicable: deterministic calculations.', 'numpy_version':np.__version__,
        'tail_support':out,'infinity_quantile_demonstration':{'array_size':999,'positive_infinity_count':60,
            'quantile_05_95':[v if np.isfinite(v) else 'NaN' if np.isnan(v) else 'Infinity' for v in q]}}
(root/'expert_notes/empirical_code_checks.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(result,indent=2,allow_nan=False))
