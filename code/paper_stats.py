"""Statistics quoted in the text that no table reports (Sections 4, 5, 6 and 7). Writes notes/paper_stats.json."""
import json
import os
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
core = pd.read_csv(f'{BASE}/data/panel.csv')
broad = pd.read_csv(f'{BASE}/data/panel_broad.csv')
S = {}

# Section 4: data construction
S['orig_filing_share_among_reporting'] = {c: float(core[f'orig_{c}'].mean()) for c in ['op', 'ocf', 'capex', 'sbc']}
S['us_address_share'] = float(core['loc'].fillna('').str.fullmatch(r'[A-Z]{2}').mean())
S['acq_flag_share'] = float(core.acq_flag.mean())
S['acq_flag_share_g_above_50'] = float(core.loc[core.g > 0.5, 'acq_flag'].mean())
S['disc_flag_share'] = float(core.disc_flag.mean())
S['capex_missing_share'] = float(core.capex_missing.mean())
S['pass40'] = {m: float((core[f'R_{m}'] >= 0.4).sum() / core[f'R_{m}'].notna().sum()) for m in ['op', 'fcf_sbc', 'adj', 'fcf']}
cw = core[core.name.str.contains('CoreWeave', na=False) & (core.year == 2025)].iloc[0]
S['coreweave_2025'] = dict(g=float(cw.g), m_op=float(cw.m_op), R_op=float(cw.R_op), m_fcf_sbc=float(cw.m_fcf_sbc), R_fcf_sbc=float(cw.R_fcf_sbc))

# AppLovin: restated 2023 revenue (latest annual filing) against the originally reported 2022 total
raw = json.load(open(f'{BASE}/data/companyfacts_extract.json'))
app = broad[broad.name.str.contains('AppLovin', na=False)]
if len(app):
    blob = raw[str(int(app.cik.iloc[0]))]
    filed = {i: a[1] for i, a in enumerate(blob['acc'])}
    rev = [f for f in blob['f'] if f[0] < 5 and f[2]]
    def annual(end, pick):
        cand = [(filed[f[1]], f[4]) for f in rev if f[3] == end and 340 <= (pd.Timestamp(f[3]) - pd.Timestamp(f[2])).days <= 392]
        by_filing = {}
        for fd, v in cand:
            by_filing[fd] = max(v, by_filing.get(fd, -np.inf))
        return by_filing[pick(by_filing)]
    r23_restated = annual('2023-12-31', max)
    r22_original = annual('2022-12-31', min)
    g23 = float(app.loc[app.year == 2023, 'g'].iloc[0])
    S['applovin'] = dict(rev2023_restated=r23_restated, rev2022_original=r22_original,
                         restated_vs_original=r23_restated / r22_original - 1, g2023_as_first_reported=g23)

# Section 5: Palantir and the top of 2023-25
late = core[core.year >= 2023].sort_values('R_op', ascending=False)
pl = core[core.name.str.contains('Palantir', na=False) & (core.year == 2025)].iloc[0]
S['palantir_2025'] = dict(g=float(pl.g), m_op=float(pl.m_op), R_op=float(pl.R_op),
                          rank_2023_25=int((late.R_op > pl.R_op).sum() + 1),
                          rank_above_1B=int((late[late.rev > 1e9].R_op > pl.R_op).sum() + 1))
S['top_R_op_2023_25'] = late[['name', 'year', 'R_op']].head(5).values.tolist()

# Section 6: median gross margin, 2023-25
x = core[core.year >= 2023]
S['median_gross_margin_2023_25'] = float((x.gp / x.rev).median())

# Section 7: general and administrative expense by size, 2023-25
x = x.assign(gas=x.ga / x.rev)
S['ga_median_by_size'] = {lab: float(x.loc[(x.rev >= lo) & (x.rev < hi), 'gas'].median())
                          for lab, lo, hi in [('<1B', 0, 1e9), ('1-10B', 1e9, 1e10), ('>10B', 1e10, np.inf)]}
lean = x[x.name.str.contains('MICROSOFT|ORACLE', na=False)]
S['ga_microsoft_oracle_range'] = [float(lean.gas.min()), float(lean.gas.max())]

# Section 6: firm-level growth surplus in the calibration anchor (both bounds; see calibrate_horizons.py)
d = core[core.period == '2023-25'].copy()
d['R'] = d.g + d.m_fcf_sbc
G25 = d.g.median()
top = d[(d.R >= d.R.quantile(.95)) & (d.acq_flag == 0)].copy()
sig = (top.sm / top.rev).fillna(0.0)
kg = top.capex_int.fillna(0.0)
k = np.where(top.g > 0, kg / top.g, 0.0)
top['m0_ub'] = top.m_fcf_sbc + 0.82 * sig + kg
top['Pi_ub'] = top.R - (top.m0_ub + (1 - k) * G25)
top['Pi_lb'] = top.R - (top.m_fcf_sbc + kg + (1 - k) * G25)
top['Rinf_ub'] = top.m0_ub + (1 - k) * G25
S['anchor_firms'] = top[['name', 'year', 'R', 'm0_ub', 'Rinf_ub', 'Pi_ub', 'Pi_lb']].round(4).values.tolist()

# Section 5: capital-intensity split, 2023-25
x = core[core.period == '2023-25']
med = x.capex_int.median()
hi = x[x.capex_int > med].dropna(subset=['R_fcf_sbc'])
S['capint_median_2023_25'] = float(med)
S['capint_hi_top_by_cash_score'] = hi.sort_values('R_fcf_sbc', ascending=False)[['name', 'year', 'capex_int', 'R_fcf_sbc']].head(8).round(4).values.tolist()

json.dump(S, open(f'{BASE}/notes/paper_stats.json', 'w'), indent=1)
print(json.dumps(S, indent=1))
