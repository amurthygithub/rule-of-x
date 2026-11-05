"""Mistral F-4: data/panel_v3.csv carries the v2 flag (acq_flag) and the v3 flag (acq_flag_v3); the estimation code
replaces the first by the second when it loads the panel (code/estimate_organic.py, lines 130 and 195). Counts the rows
where they differ and the calibration anchor's firm-years under each flag (2023-25, cash score at or above its 95th
percentile, acquisition-flagged firm-years dropped), against notes/calibration_anchor_v3.json."""
import json, pandas as pd
P = pd.read_csv('data/panel_v3.csv')
print('firm-years', len(P), '| rows where acq_flag != acq_flag_v3:', int((P.acq_flag != P.acq_flag_v3).sum()))
src = open('code/estimate_organic.py').read().splitlines()
print('estimate_organic.py line 130:', src[129].strip()); print('estimate_organic.py line 195:', src[194].strip())
L = P[P.year.between(2023, 2025)]
cut = L.R_fcf_sbc.quantile(0.95)
for f in ('acq_flag', 'acq_flag_v3'):
    a = L[(L.R_fcf_sbc >= cut) & (L[f] == 0)]
    print(f'{f:12s}: cut {100 * cut:.2f}, anchor firm-years {len(a)}, firms {a.cik.nunique()}')
A = json.load(open('notes/calibration_anchor_v3.json'))
print('notes/calibration_anchor_v3.json keys:', sorted(A)[:12])
