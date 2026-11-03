"""function_occ.csv and industry_function_shares.csv (contract Section 12).

function_occ.csv
  Membership (which SOC occupations staff which function) and the allocation share alloc(f, soc) of an occupation's
  employment that sits in function f are CONSTRUCTED assumptions (table FUNC_SOC below). Within a function, the prior
  headcount weight is weight(f, soc) = emp(soc) * alloc(f, soc) / sum over the function, where emp is OEWS national
  cross-industry employment (vintage in occupations.csv). If the OEWS industry file is present,
  function_occ_by_industry.csv repeats the calculation with each 4-digit NAICS industry's employment, which is the
  prior the engine should use once it knows the firm's industry.

industry_function_shares.csv
  Cost-bucket shares of revenue (cogs = 1 - gross profit / revenue, rnd, sm, ga) are SOURCED from the SEC XBRL panel
  data/panel_v2_all.csv (as-first-reported 10-K values; see code/build_panel_v2.py), for SIC 7370-7374, fiscal years
  2023-2025, by revenue size band: firm means over the window, then the cross-firm mean and sd. The split of each
  bucket across functions (WITHIN) is ASSUMED, with a range; share_of_revenue = bucket share x within-bucket split.
"""
import sys
sys.path.insert(0, '/home/claude/paper/code/data_part2')
import numpy as np
import pandas as pd
from common import BASE, OUT, write_csv, save_meta, oews_industry, num, load_meta, read_sec_panel

occ = pd.read_csv(f'{OUT}/occupations.csv', dtype={'soc': str}).set_index('soc')

FUNC_SOC = {
    'F01': {'11-1011': 1, '11-1021': .5, '43-6011': 1, '13-1111': .2},
    'F02': {'15-1252': .8, '15-1253': .9, '15-1254': .6, '15-1255': .6, '15-1221': 1, '15-2051': .5, '11-3021': .4,
            '11-9041': 1, '13-1082': .3, '27-1021': 1, '27-3042': 1, '17-2061': 1, '17-2072': 1, '17-2071': .7,
            '17-2141': .6, '17-2112': .3, '17-3023': .5, '15-1211': .3, '15-1299': .5, '15-1243': .5},
    'F03': {'11-2021': 1, '11-2011': 1, '13-1161': 1, '27-1024': .5, '27-3031': .4, '27-3043': .3, '15-1254': .4,
            '15-1255': .4, '15-2051': .25},
    'F04': {'11-2022': 1, '41-3091': .8, '41-4011': 1, '41-4012': 1, '41-9031': 1, '41-1012': 1, '41-9041': 1,
            '43-4151': .5, '41-2031': 1},
    'F05': {'43-4051': .9, '15-1232': .45, '43-2011': 1, '43-4171': .5, '43-1011': .2},
    'F06': {'13-1199': .2, '41-3091': .2, '43-4051': .1, '15-1232': .1, '13-1151': .2},
    'F07': {'15-1211': .3, '15-1299': .2, '13-1151': .2, '13-1082': .3, '13-1111': .3},
    'F08': {'11-1021': .5, '43-9061': .3, '43-5071': .3, '13-1031': 1, '43-9041': 1, '43-9021': .5, '43-4151': .5,
            '43-1011': .4, '41-2011': 1, '43-5032': 1, '13-1199': .3},
    'F09': {'11-3051': 1, '11-3071': 1, '13-1081': 1, '51-1011': 1, '51-2090': 1, '51-9061': 1, '53-7062': 1,
            '53-7065': 1, '53-3032': 1, '43-5071': .7, '17-2112': .7, '17-2141': .4, '17-3023': .5, '51-4041': 1,
            '53-7051': 1, '49-9041': 1, '43-5061': 1},
    'F10': {'11-3061': 1, '13-1020': 1, '43-3061': 1},
    'F11': {'11-3031': 1, '13-2011': .85, '13-2051': 1, '13-2031': 1, '43-3031': 1, '43-3021': 1, '43-3051': 1,
            '13-2082': 1, '43-3011': 1, '13-2041': 1, '43-9061': .3, '43-9021': .5, '43-1011': .2, '13-2099': 1,
            '15-2031': .3},
    'F12': {'11-3121': 1, '11-3111': 1, '11-3131': 1, '13-1071': 1, '13-1141': 1, '13-1151': .6, '43-4161': 1,
            '43-9061': .1, '43-1011': .1},
    'F13': {'23-1011': 1, '23-2011': 1, '43-6012': 1, '23-2099': 1},
    'F14': {'13-1041': 1, '13-2011': .15, '13-2061': 1, '15-1212': .4, '13-2054': 1},
    'F15': {'11-3021': .6, '15-1211': .4, '15-1212': .6, '15-1231': .5, '15-1232': .45, '15-1241': .5, '15-1244': .5,
            '15-1242': .5, '15-1299': .3, '15-1252': .1, '15-1243': .5},
    'F16': {'15-1231': .5, '15-1241': .5, '15-1244': .5, '15-1242': .5, '15-1252': .1},
    'F17': {'11-3013': 1, '37-2011': 1, '49-9071': 1, '33-9032': 1, '43-4171': .5, '37-1011': 1},
    'F18': {'13-1111': .5, '13-1082': .4, '15-2051': .25, '15-2031': .7, '13-1199': .5, '11-9199': 1},
    'F19': {'27-3031': .6, '11-2032': 1, '11-2033': 1, '13-1131': 1, '27-3043': .2},
}

# allocation shares of a SOC across functions must not exceed 1
tot_alloc = {}
for f, m in FUNC_SOC.items():
    for s, a in m.items():
        tot_alloc[s] = tot_alloc.get(s, 0) + a
over = {s: a for s, a in tot_alloc.items() if a > 1 + 1e-9}
assert not over, over
missing = sorted({s for m in FUNC_SOC.values() for s in m if s not in occ.index})


def weights(emp):
    rows = []
    for f, m in FUNC_SOC.items():
        w = {s: emp.get(s, np.nan) * a for s, a in m.items()}
        w = {s: v for s, v in w.items() if pd.notna(v) and v > 0}
        t = sum(w.values())
        for s, v in w.items():
            rows.append((f, s, v / t, m[s]))
    return pd.DataFrame(rows, columns=['function_id', 'soc', 'weight', 'alloc_assumed'])


fo = weights(occ.employment.to_dict())
fo['title'] = fo.soc.map(occ.title)
fo['basis'] = f'membership and alloc assumed (constructed); emp = OEWS national {occ.oews_vintage.iloc[0]}'
write_csv(fo, 'function_occ.csv')

ind = oews_industry()
if ind is not None:
    st = pd.read_csv(f'{OUT}/industry_staffing.csv', dtype={'naics': str, 'soc': str})
    st = st[st.naics_level == '4-digit']
    frames = []
    for n, g in st.groupby('naics'):
        w = weights(g.set_index('soc').employment.to_dict())
        w.insert(0, 'naics', n)
        frames.append(w)
    write_csv(pd.concat(frames), 'function_occ_by_industry.csv')

# ------------------------------------------------------------------ industry function shares (software, SEC panel)
p = read_sec_panel('panel_v2_all.csv')          # without excluded registrants (code/exclusions.py)
p = p[(p.year >= 2023) & (p.year <= 2025) & (p.rev > 0)].copy()
p['cogs'] = 1 - p.gp / p.rev
p['rnd'] = p.rd / p.rev
p['sm_s'] = p.sm / p.rev
p['ga_s'] = p.ga / p.rev
p = p.dropna(subset=['cogs', 'rnd', 'sm_s', 'ga_s'])
p = p[p[['cogs', 'rnd', 'sm_s', 'ga_s']].apply(lambda c: c.between(0, 2)).all(axis=1)]
f = p.groupby('cik').agg(sic=('sic', 'first'), rev=('rev', 'mean'), cogs=('cogs', 'mean'), rnd=('rnd', 'mean'),
                         sm=('sm_s', 'mean'), ga=('ga_s', 'mean'), n_years=('year', 'nunique'))
bands = [(0, 1e8, '<100M'), (1e8, 1e9, '100M-1B'), (1e9, 1e10, '1B-10B'), (1e10, np.inf, '>10B')]
f['size_band'] = pd.cut(f.rev, [b[0] for b in bands] + [np.inf], labels=[b[2] for b in bands], right=False).astype(str)

# within-bucket function splits (ASSUMED): central value and a +/- range in share points
WITHIN = {
    'cogs': {'F16': (.45, .15), 'F05': (.25, .10), 'F07': (.25, .10), 'F06': (.05, .05)},
    'rnd': {'F02': (1.0, 0.0)},
    'sm': {'F04': (.55, .10), 'F03': (.30, .10), 'F06': (.15, .07)},
    'ga': {'F11': (.28, .08), 'F12': (.12, .05), 'F13': (.10, .05), 'F15': (.15, .07), 'F14': (.05, .03),
           'F17': (.10, .05), 'F01': (.10, .05), 'F18': (.05, .03), 'F19': (.03, .02), 'F10': (.02, .01)},
}
for b, m in WITHIN.items():
    assert abs(sum(v[0] for v in m.values()) - 1) < 1e-9, b

SIC2NAICS = {7370: '5415/5182/5132 (mixed)', 7371: '5415', 7372: '5132', 7373: '5415', 7374: '5182/5415'}
rows = []
groups = [('7370-7374', f)] + [(str(s), g) for s, g in f.groupby('sic')]
for sic, g0 in groups:
    for band, g in [('all', g0)] + list(g0.groupby('size_band')):
        if len(g) < 5:
            continue
        for b, m in WITHIN.items():
            col = {'cogs': 'cogs', 'rnd': 'rnd', 'sm': 'sm', 'ga': 'ga'}[b]
            mb, sb = g[col].mean(), g[col].std()
            for fid, (s, r) in m.items():
                ss = r / 2                                      # treat the range as +/- 2 sd
                sd = np.sqrt(sb ** 2 * s ** 2 + ss ** 2 * mb ** 2 + sb ** 2 * ss ** 2)
                rows.append(dict(sic=sic, naics=SIC2NAICS.get(int(sic), '') if sic.isdigit() else '51/54 software and IT services',
                                 size_band=band, function_id=fid, cost_bucket=b, share_of_revenue_prior=mb * s,
                                 share_of_revenue_sd=sd, bucket_share_mean=mb, bucket_share_sd=sb,
                                 bucket_share_median=g[col].median(), within_bucket_split=s, within_bucket_range=r,
                                 within_bucket_assumed=True, n_firms=len(g), years='FY2023-2025',
                                 source='SEC XBRL panel (data/panel_v2_all.csv) for bucket shares; within-bucket split assumed'))
ifs = pd.DataFrame(rows)
write_csv(ifs, 'industry_function_shares.csv')
save_meta('function_priors', dict(missing_soc_in_occupations=missing, n_firms=int(len(f)),
                                  firms_by_band=f.size_band.value_counts().to_dict(),
                                  bucket_means_all=f[['cogs', 'rnd', 'sm', 'ga']].mean().round(4).to_dict(),
                                  bucket_medians_all=f[['cogs', 'rnd', 'sm', 'ga']].median().round(4).to_dict()))
print('missing SOCs:', missing)
print(f.groupby('size_band')[['cogs', 'rnd', 'sm', 'ga']].agg(['mean', 'count']).round(3))
