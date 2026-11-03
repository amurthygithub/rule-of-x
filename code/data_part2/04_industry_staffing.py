"""industry_staffing.csv: occupation employment shares by NAICS industry (contract Section 12).

Source: BLS OEWS May 2025 national industry-specific estimates, oesm25in4.zip (requested; see
notes/data_download_requests.md). Rows with I_GROUP in {sector, 3-digit, 4-digit} and O_GROUP = detailed are kept;
emp_share = TOT_EMP / sum of TOT_EMP over detailed occupations in the industry (ownership: private and all
ownerships as published; when an industry is published by ownership, the 'cross-ownership' row 1235 or the private
row 5 is used, in that order). Suppressed employment ('**') is dropped; the share of the industry total covered by
published detailed rows is reported as coverage.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
from common import oews_industry, num, write_csv, save_meta

d = oews_industry()
if d is None:
    print('OEWS May 2025 industry file not found (data/raw/bls_oews_2025/oesm25in4.zip): industry_staffing.csv not built')
    save_meta('industry_staffing', dict(mode='missing', needed='https://www.bls.gov/oes/special-requests/oesm25in4.zip'))
    sys.exit(0)

d['ig'] = d.igroup.astype(str).str.lower().str.strip()
d = d[d.ig.isin(['sector', '3-digit', '4-digit'])]
d['own'] = d.owncode.astype(str).str.strip() if 'owncode' in d else '1235'
d['emp'] = d.totemp.map(num)
d['naics_raw'] = d.naics.astype(str).str.strip()
ndig = d.ig.map({'sector': 2, '3-digit': 3, '4-digit': 4})
# custom BLS aggregates (e.g. 3250A1 = 3251, 3252, 3253 and 3259 only) keep their full code so they do not collide
d['naics'] = [r if ('-' in r or not r.isdigit()) else r[:n] for r, n in zip(d.naics_raw, ndig)]
# one ownership per industry: prefer 1235 (all), then 5 (private), else the largest total
tot = d[d.occcode.astype(str) == '00-0000']
pref = {'1235': 0, '5': 1}
tot = tot.assign(rank=tot.own.map(pref).fillna(9)).sort_values(['naics', 'rank', 'emp'], ascending=[True, True, False])
keep = tot.drop_duplicates('naics')[['naics', 'own', 'emp', 'naicstitle', 'ig']].rename(columns={'emp': 'ind_emp'})
det = d[d.ogroup.astype(str).str.lower() == 'detailed'].merge(keep[['naics', 'own']], on=['naics', 'own'])
det = det[det.emp.notna()]
det['emp_share'] = det.emp / det.groupby('naics').emp.transform('sum')
cov = (det.groupby('naics').emp.sum() / keep.set_index('naics').ind_emp).rename('coverage')
out = det[['naics', 'naicstitle', 'ig', 'occcode', 'emp', 'emp_share']].rename(
    columns={'naicstitle': 'naics_title', 'ig': 'naics_level', 'occcode': 'soc', 'emp': 'employment'})
out = out.merge(cov.reset_index(), on='naics', how='left')
out['oews_vintage'] = 'May 2025'
out = out[['naics', 'soc', 'emp_share', 'naics_title', 'naics_level', 'employment', 'coverage', 'oews_vintage']]
write_csv(out.sort_values(['naics', 'emp_share'], ascending=[True, False]), 'industry_staffing.csv')
assert (out.groupby('naics').soc.apply(lambda x: x.duplicated().sum()) == 0).all(), 'duplicate soc within an industry'
save_meta('industry_staffing', dict(mode='full', n_industries=int(out.naics.nunique()), coverage_median=float(cov.median()),
                                    coverage_min=float(cov.min()), coverage_max=float(cov.max()),
                                    coverage_p10=float(cov.quantile(0.1)), ownership_codes_used=keep.own.value_counts().to_dict()))
