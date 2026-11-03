"""Check 8: within-firm FE slope of margin on growth, excluding acquisition-flagged firm-years and DXC/Aspen-type mergers."""
import numpy as np, pandas as pd, statsmodels.formula.api as smf
df = pd.read_csv('/home/claude/paper/data/panel.csv')
for m in ['m_op', 'm_fcf_sbc']:
    for lab, d in [('paper', df), ('organic', df[df.acq_flag == 0]), ('organic, |g|<=0.6', df[(df.acq_flag == 0) & (df.g.abs() <= 0.6)])]:
        d = d[['cik', 'year', 'g', m]].dropna(); d = d[d.g <= 1.5]
        fe = smf.ols(f'{m} ~ g + C(year) + C(cik)', d).fit(cov_type='cluster', cov_kwds={'groups': d['cik']})
        print(m, lab, round(fe.params['g'], 3), round(fe.bse['g'], 3), len(d))
