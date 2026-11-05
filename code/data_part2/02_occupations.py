"""occupations.csv (contract Section 12) and occ_exposure.csv (occupation-level AI exposure and usage, extra file).

Inputs
- BLS OEWS national cross-industry estimates: May 2025 if data/raw/bls_oews_2025/ holds oesm25nat.zip (requested),
  otherwise the May 2021 national file redistributed in openai/GPTs-are-GPTs (data/national_May2021_dl.csv).
- O*NET-SOC codes per SOC: O*NET 31.0 occupation_data if downloaded, otherwise the O*NET-SOC list in the
  GPTs-are-GPTs occupation file (O*NET 27.2 era).
- physical_share: microsoft/working-with-ai v1.1 (Tomlinson et al.), soc_iwa_weights.csv and
  soc_iwa_nonphysical_weights.csv. Both weight an occupation's IWAs by O*NET 29.0 task relevance and importance;
  the second counts only tasks classified as nonphysical. physical_share = 1 - sum(nonphysical) / sum(all).
- licensed_signoff: constructed rule (see LICENSED below and notes/data_sources_part2.md).
- occ_exposure.csv: Eloundou et al. (2024) occupation scores (occ_level.csv, O*NET-SOC -> SOC by simple mean),
  Tomlinson et al. AI applicability score, and (when downloaded) Anthropic Economic Index occupation shares.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import re
import numpy as np
import pandas as pd
from common import (GPTS, MSAI, oews_national, num, read_onet, pick, soc6, write_csv, save_meta, oews_onet_crosswalk)

nat, vintage = oews_national()
occ = nat[nat.ogroup.astype(str).str.lower() == 'detailed'].copy()
occ['soc'] = occ.occcode.astype(str).str.strip()
occ['title'] = occ.occtitle.astype(str).str.strip()
occ['employment'] = occ.totemp.map(num)
occ['wage_mean'] = occ.amean.map(num)
occ['wage_median'] = occ.amedian.map(num)
occ['wage_median_topcoded'] = occ.amedian.astype(str).str.strip().eq('#').astype(int)
occ['wage_mean_topcoded'] = occ.amean.astype(str).str.strip().eq('#').astype(int)
occ['hourly_mean'] = occ.hmean.map(num)
occ['annual_only'] = occ['annual'].astype(str).str.upper().eq('TRUE').astype(int) if 'annual' in occ else 0
occ['oews_vintage'] = vintage
occ = occ[['soc', 'title', 'wage_median', 'wage_mean', 'employment', 'hourly_mean', 'wage_median_topcoded',
           'wage_mean_topcoded', 'annual_only', 'oews_vintage']].drop_duplicates('soc')

# ------------------------------------------------------------------ O*NET-SOC codes within each SOC
od = read_onet('occupation_data')
if od is not None:
    onet_codes = od[pick(od, 'onetsoccode')].astype(str).tolist()
    onet_src = 'O*NET 31.0 occupation_data'
else:
    onet_codes = pd.read_csv(f'{GPTS}/occ_level.csv')['O*NET-SOC Code'].astype(str).tolist()
    onet_src = 'GPTs-are-GPTs occ_level.csv (O*NET 27.2 codes with task data)'
xw, xw_rule = oews_onet_crosswalk(occ.soc.tolist(), onet_codes)
occ['onet_soc'] = occ.soc.map(lambda s: ';'.join(xw.get(s, [])))
occ['onet_match'] = occ.soc.map(xw_rule).fillna('none')

# ------------------------------------------------------------------ physical share (Tomlinson et al. v1.1)
w_all = pd.read_csv(f'{MSAI}/soc_iwa_weights.csv').set_index('SOC Code')
w_np = pd.read_csv(f'{MSAI}/soc_iwa_nonphysical_weights.csv').set_index('SOC Code')
assert (w_np.columns == w_all.columns).all()
tot, npw = w_all.sum(axis=1), w_np.reindex(w_all.index).sum(axis=1)
assert (npw <= tot + 1e-9).all()
phys = (1 - npw / tot).clip(0, 1)
occ['physical_share'] = occ.soc.map(phys)

# ------------------------------------------------------------------ licensed sign-off (constructed classification)
# Rule: 1 if U.S. federal or state law requires a licensed, certificated or registered individual to perform the
# occupation's core regulated act or to sign or take legal responsibility for its core work product (for example an
# audit opinion, a legal filing, a prescription, a stamped design, a flight). Entries are (code or prefix, basis).
LICENSED = [
    ('13-2011', 'CPA licence required to sign audit and attest reports'),
    ('13-2020', 'appraiser licence or certification (OEWS aggregate of 13-2022 and 13-2023)'),
    ('13-2022', 'appraiser licensing or certification (personal and business property)'),
    ('13-2023', 'state real estate appraiser licence or certification'),
    ('13-2052', 'investment adviser representative registration'),
    ('15-2011', 'qualified actuary signs statements of actuarial opinion'),
    ('17-1011', 'state architect licence; stamped drawings'),
    ('17-1012', 'state landscape architect licence'),
    ('17-1022', 'state surveyor licence; signed and sealed surveys'),
    ('17-2051', 'professional engineer licence; sealed civil designs'),
    ('19-3033', 'state psychologist licence'),
    ('19-3034', 'state psychologist licence or school certification'),
    ('21-1013', 'state marriage and family therapist licence'),
    ('21-1018', 'state counselor licence'),
    ('21-1022', 'state social work licence'),
    ('21-1023', 'state clinical social work licence'),
    ('23-1011', 'bar admission; legal advice and filings'),
    ('23-1021', 'appointed adjudicator; judgments of persons'),
    ('23-1023', 'judicial office; judgments of persons'),
    ('25-2', 'state teaching certificate or licence (minor group 25-2000, except 25-2011 preschool)'),
    ('29-1', 'state licence to diagnose or treat (minor group 29-1000, except 29-1125 and 29-1128)'),
    ('29-2061', 'state practical or vocational nurse licence'),
    ('39-4031', 'state funeral director licence'),
    ('41-3021', 'state insurance producer licence'),
    ('41-3031', 'FINRA registration for securities sales'),
    ('41-9021', 'state real estate broker licence'),
    ('41-9022', 'state real estate salesperson licence'),
    ('47-2111', 'state or local electrician licence'),
    ('47-2152', 'state or local plumber licence'),
    ('53-2011', 'FAA airline transport pilot certificate'),
    ('53-2012', 'FAA commercial pilot certificate'),
    ('53-2021', 'FAA air traffic control certificate'),
    ('53-5021', 'U.S. Coast Guard merchant mariner credential'),
]
LIC_EXCEPT = {'25-2011', '29-1125', '29-1128'}


def lic(soc):
    if soc in LIC_EXCEPT:
        return 0, ''
    for key, basis in LICENSED:
        if soc == key or (len(key) == 4 and soc.startswith(key)):
            return 1, basis
    return 0, ''


occ[['licensed_signoff', 'licensed_basis']] = occ.soc.apply(lambda s: pd.Series(lic(s)))
missing = [k for k, _ in LICENSED if len(k) == 7 and k not in set(occ.soc)]  # expected: codes OEWS reports only in aggregate

out = occ[['soc', 'onet_soc', 'title', 'wage_median', 'wage_mean', 'employment', 'physical_share', 'licensed_signoff',
           'licensed_basis', 'onet_match', 'hourly_mean', 'wage_median_topcoded', 'wage_mean_topcoded', 'annual_only', 'oews_vintage']]
out = out.sort_values('soc')
write_csv(out, 'occupations.csv')

# ------------------------------------------------------------------ occupation-level exposure and usage
el = pd.read_csv(f'{GPTS}/occ_level.csv')
exw, _ = oews_onet_crosswalk(occ.soc.tolist(), el['O*NET-SOC Code'].astype(str).tolist())
inv = {c: o for o, cs in exw.items() for c in cs}                 # O*NET-SOC -> OEWS code (simple mean within)
el['soc'] = el['O*NET-SOC Code'].map(inv)
ecols = ['dv_rating_alpha', 'dv_rating_beta', 'dv_rating_gamma', 'human_rating_alpha', 'human_rating_beta', 'human_rating_gamma']
eg = el.groupby('soc')[ecols].mean()
eg.columns = ['eloundou_gpt4_alpha', 'eloundou_gpt4_beta', 'eloundou_gpt4_gamma',
              'eloundou_human_alpha', 'eloundou_human_beta', 'eloundou_human_gamma']
eg['eloundou_n_onetsoc'] = el.groupby('soc').size()
ms = pd.read_csv(f'{MSAI}/ai_applicability_scores.csv').set_index('SOC Code')['ai_applicability_score']
msm = pd.read_csv(f'{MSAI}/soc_metrics.csv').set_index('SOC Code')
ex = occ[['soc', 'title', 'employment']].set_index('soc').join(eg, how='left')
ex['tomlinson_ai_applicability'] = ms
ex['tomlinson_coverage_user'] = msm['coverage_user']
ex['tomlinson_completion_user'] = msm['completion_user']
ex = ex.reset_index()
write_csv(ex, 'occ_exposure.csv')

meta = dict(oews_vintage=vintage, onet_soc_source=onet_src, n_occ=len(out),
            employment_total=float(out.employment.sum()),
            physical_share_coverage_emp=float(out.loc[out.physical_share.notna(), 'employment'].sum() / out.employment.sum()),
            licensed_n=int(out.licensed_signoff.sum()),
            licensed_emp_share=float(out.loc[out.licensed_signoff == 1, 'employment'].sum() / out.employment.sum()),
            licensed_codes_not_in_oews=missing,
            eloundou_coverage_emp=float(ex.loc[ex.eloundou_gpt4_beta.notna(), 'employment'].sum() / ex.employment.sum()),
            tomlinson_coverage_emp=float(ex.loc[ex.tomlinson_ai_applicability.notna(), 'employment'].sum() / ex.employment.sum()),
            wage_median_topcoded_n=int(out.wage_median_topcoded.sum()),
            onet_match_counts=out.onet_match.value_counts().to_dict(),
            onet_unmatched_emp_share=float(out.loc[out.onet_match == 'none', 'employment'].sum() / out.employment.sum()))
save_meta('occupations', meta)
print(meta)
