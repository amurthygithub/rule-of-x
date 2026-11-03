"""Build the firm-year panel for software firms (SIC 7370-7374) from SEC XBRL frames.

Inputs
  data/sic_universe.json      [[sic, cik(str, zero-padded), name, state], ...]
  data/frames_universe.json   {"Concept|Year": {cik: [val, start, end, entityName]}}  (filtered to universe)
Output
  data/panel.csv              one row per firm-year with growth, margin measures and scores
  notes/panel_build_log.txt   construction diagnostics
"""
import json
import os
import sys
from datetime import date
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exclusions import is_excluded  # noqa: E402  registrants excluded at the author's request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # repository root
uni = [r for r in json.load(open(f'{BASE}/data/sic_universe.json')) if not is_excluded(r[1])]
sic_map = {int(r[1]): int(r[0]) for r in uni}
name_map = {int(r[1]): r[2] for r in uni}
frames = json.load(open(f'{BASE}/data/frames_universe.json'))
for k, v in json.load(open(f'{BASE}/data/frames_extra.json')).items():
    if k not in frames:
        frames[k] = v

INSTANT = {'PropertyPlantAndEquipmentNet', 'Assets', 'OperatingLeaseRightOfUseAsset', 'Goodwill'}
rows = []
for key, d in frames.items():
    concept, year = key.split('|')
    for cik, v in d.items():
        if is_excluded(cik):
            continue
        val, start, end = v[0], v[1], v[2]
        rows.append((int(cik), int(year), concept, float(val), start, end))
long = pd.DataFrame(rows, columns=['cik', 'year', 'concept', 'val', 'start', 'end'])
log = []
log.append(f'raw facts: {len(long):,}; firms: {long.cik.nunique():,}')

# duration sanity for flow concepts
dur = ~long.concept.isin(INSTANT)
s = pd.to_datetime(long.loc[dur, 'start'], errors='coerce')
e = pd.to_datetime(long.loc[dur, 'end'], errors='coerce')
days = (e - s).dt.days
bad = dur.copy(); bad.loc[dur] = ~days.between(340, 392)
log.append(f'flow facts dropped for non-annual duration: {int(bad.sum()):,}')
long = long[~bad]

wide = long.pivot_table(index=['cik', 'year'], columns='concept', values='val', aggfunc='first')
ends = long[long.concept.isin(['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax',
                               'RevenueFromContractWithCustomerIncludingAssessedTax', 'SalesRevenueNet',
                               'SalesRevenueServicesNet'])]
end_map = ends.groupby(['cik', 'year'])['end'].first()
wide = wide.reset_index()

REV = ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax',
       'RevenueFromContractWithCustomerIncludingAssessedTax', 'SalesRevenueNet', 'SalesRevenueServicesNet']
for c in REV + ['OperatingIncomeLoss', 'GrossProfit', 'CostOfRevenue', 'CostOfGoodsAndServicesSold',
                'ResearchAndDevelopmentExpense', 'ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost',
                'SellingGeneralAndAdministrativeExpense', 'SellingAndMarketingExpense',
                'GeneralAndAdministrativeExpense', 'NetCashProvidedByUsedInOperatingActivities',
                'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations',
                'PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets',
                'PaymentsForSoftware', 'PaymentsToDevelopSoftware', 'ShareBasedCompensation',
                'AllocatedShareBasedCompensationExpense', 'NetIncomeLoss', 'PropertyPlantAndEquipmentNet',
                'Assets', 'DepreciationDepletionAndAmortization', 'DepreciationAndAmortization',
                'DepreciationAmortizationAndAccretionNet', 'Goodwill',
                'PaymentsToAcquireBusinessesNetOfCashAcquired', 'PaymentsToAcquireBusinessesGross']:
    if c not in wide.columns:
        wide[c] = np.nan

def first_avail(df, cols):
    out = pd.Series(np.nan, index=df.index)
    src = pd.Series('', index=df.index, dtype=object)
    for c in cols:
        m = out.isna() & df[c].notna()
        out[m] = df.loc[m, c]
        src[m] = c
    return out, src

wide['rev'], wide['rev_src'] = first_avail(wide, REV)
wide = wide.sort_values(['cik', 'year'])

# growth: prefer a revenue concept reported in both years (priority order)
prev = wide.groupby('cik').shift(1)
prev_year = wide.groupby('cik')['year'].shift(1)
g = pd.Series(np.nan, index=wide.index)
gsrc = pd.Series('', index=wide.index, dtype=object)
for c in REV:
    m = g.isna() & wide[c].notna() & prev[c].notna() & (prev[c] > 0) & (prev_year == wide['year'] - 1)
    g[m] = wide.loc[m, c] / prev.loc[m, c] - 1
    gsrc[m] = c
# fallback: chosen revenue in both years
m = g.isna() & wide['rev'].notna() & prev['rev'].notna() & (prev['rev'] > 0) & (prev_year == wide['year'] - 1)
g[m] = wide.loc[m, 'rev'] / prev.loc[m, 'rev'] - 1
gsrc[m] = 'fallback'
wide['g'] = g
wide['g_src'] = gsrc
# override with filing-consistent growth (same filing reports both years), when available
import os
if os.path.exists(f'{BASE}/data/growth_filing.csv'):
    gf = pd.read_csv(f'{BASE}/data/growth_filing.csv')
    gmap = {(int(c), e): v for c, e, v in zip(gf.cik, gf.fy_end, gf.g_filing)}
    fy_end_col = [end_map.get((c, y), '') for c, y in zip(wide.cik, wide.year)]
    g_fil = pd.Series([gmap.get((int(c), e), np.nan) for c, e in zip(wide.cik, fy_end_col)], index=wide.index)
    wide['g_frames'] = wide['g']
    has = g_fil.notna() & wide['g'].notna()
    big = has & ((g_fil - wide['g']).abs() > 0.05)
    log.append(f"filing-consistent growth available for {int(has.sum()):,} of {int(wide['g'].notna().sum()):,} growth obs; "
               f"differs from frames growth by >5pp in {int(big.sum()):,}")
    wide.loc[has, 'g'] = g_fil[has]
    wide.loc[has, 'g_src'] = 'filing'
wide['rev_lag'] = np.where(prev_year == wide['year'] - 1, prev['rev'], np.nan)
log.append(f"growth obs: {wide.g.notna().sum():,}; fallback share: {(gsrc=='fallback').mean():.3f}")

rev = wide['rev']
wide['op_inc'] = wide['OperatingIncomeLoss']
wide['ocf'], _ = first_avail(wide, ['NetCashProvidedByUsedInOperatingActivities',
                                    'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations'])
wide['capex_ppe'], wide['capex_src'] = first_avail(wide, ['PaymentsToAcquirePropertyPlantAndEquipment',
                                                         'PaymentsToAcquireProductiveAssets'])
wide['capex_missing'] = wide['capex_ppe'].isna()
wide['capex_ppe'] = wide['capex_ppe'].fillna(0.0)
wide['cap_sw'] = wide['PaymentsForSoftware'].fillna(0.0) + wide['PaymentsToDevelopSoftware'].fillna(0.0)
wide['sbc'], wide['sbc_src'] = first_avail(wide, ['ShareBasedCompensation', 'AllocatedShareBasedCompensationExpense'])
gp, _ = first_avail(wide, ['GrossProfit'])
cor, _ = first_avail(wide, ['CostOfRevenue', 'CostOfGoodsAndServicesSold'])
wide['gross_profit'] = gp.fillna(rev - cor)
rnd, _ = first_avail(wide, ['ResearchAndDevelopmentExpense', 'ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost'])
wide['rnd'] = rnd
wide['sm'] = wide['SellingAndMarketingExpense']
wide['ga'] = wide['GeneralAndAdministrativeExpense']
wide['sga'] = wide['SellingGeneralAndAdministrativeExpense']
da, _ = first_avail(wide, ['DepreciationDepletionAndAmortization', 'DepreciationAndAmortization',
                           'DepreciationAmortizationAndAccretionNet'])
wide['da'] = da
wide['ppe'] = wide['PropertyPlantAndEquipmentNet']
wide['assets'] = wide['Assets']
wide['net_inc'] = wide['NetIncomeLoss']
# acquisitions: cash paid for businesses, or a goodwill jump, relative to prior-year revenue
acq, _ = first_avail(wide, ['PaymentsToAcquireBusinessesNetOfCashAcquired', 'PaymentsToAcquireBusinessesGross'])
wide['acq_pay'] = acq
gw_prev = wide.groupby('cik')['Goodwill'].shift(1).where(prev_year == wide['year'] - 1)
wide['gw_jump'] = wide['Goodwill'] - gw_prev
rl = pd.Series(wide['rev_lag'], index=wide.index)
wide['acq_flag'] = ((wide['acq_pay'].fillna(0) >= 0.25 * rl) | (wide['gw_jump'].fillna(0) >= 0.25 * rl)).astype(int)
wide['sm_lag_share'] = (wide.groupby('cik')['SellingAndMarketingExpense'].shift(1) /
                        wide.groupby('cik')['rev'].shift(1)).where(prev_year == wide['year'] - 1)

# margins
wide['m_op'] = wide['op_inc'] / rev                                  # GAAP operating margin
wide['m_adj'] = (wide['op_inc'] + wide['sbc']) / rev                 # adjusted (SBC added back)
wide['fcf'] = wide['ocf'] - wide['capex_ppe'] - wide['cap_sw']
wide['m_fcf'] = wide['fcf'] / rev                                    # FCF margin (SBC is a non-cash add-back inside OCF)
wide['m_fcf_sbc'] = (wide['fcf'] - wide['sbc']) / rev                # FCF after SBC
wide['m_ebitda'] = (wide['op_inc'] + wide['da']) / rev
wide['gm'] = wide['gross_profit'] / rev
wide['capex_int'] = (wide['capex_ppe'] + wide['cap_sw']) / rev
wide['ppe_int'] = wide['ppe'] / rev
wide['sm_share'] = wide['sm'] / rev
wide['rnd_share'] = wide['rnd'] / rev
for mm in ['m_op', 'm_adj', 'm_fcf', 'm_fcf_sbc', 'm_ebitda']:
    wide['R_' + mm[2:]] = wide['g'] + wide[mm]

wide['sic'] = wide['cik'].map(sic_map)
wide['name'] = wide['cik'].map(name_map)
wide['fy_end'] = [end_map.get((c, y), '') for c, y in zip(wide.cik, wide.year)]
wide['period'] = pd.cut(wide['year'], [2009, 2015, 2019, 2022, 2025], labels=['2010-15', '2016-19', '2020-22', '2023-25'])

keep = ['cik', 'name', 'sic', 'year', 'period', 'fy_end', 'rev', 'rev_src', 'rev_lag', 'g', 'g_src', 'g_frames',
        'op_inc', 'ocf', 'capex_ppe', 'capex_missing', 'cap_sw', 'sbc', 'sbc_src', 'gross_profit', 'rnd', 'sm',
        'ga', 'sga', 'da', 'ppe', 'assets', 'net_inc', 'fcf', 'acq_pay', 'gw_jump', 'acq_flag', 'sm_lag_share',
        'm_op', 'm_adj', 'm_fcf', 'm_fcf_sbc', 'm_ebitda', 'gm', 'capex_int', 'ppe_int', 'sm_share', 'rnd_share',
        'R_op', 'R_adj', 'R_fcf', 'R_fcf_sbc', 'R_ebitda']
panel = wide[keep].copy()
panel.to_csv(f'{BASE}/data/panel_all.csv', index=False)

# analysis sample
a = panel.copy()
n0 = len(a)
a = a[a.year.between(2010, 2025)]
a = a[a.g.notna() & a.rev_lag.notna()]
log.append(f'firm-years with growth 2010-2025: {len(a):,} ({a.cik.nunique():,} firms)')
a = a[a.rev_lag >= 100e6]
log.append(f'after prior-year revenue >= $100M: {len(a):,} ({a.cik.nunique():,} firms)')
a = a[a.m_op.notna() | a.m_fcf.notna()]
a = a[(a.g > -0.9) & (a.g < 5)]
for mm in ['m_op', 'm_adj', 'm_fcf', 'm_fcf_sbc']:
    a.loc[(a[mm] < -3) | (a[mm] > 1), mm] = np.nan
log.append(f'analysis sample: {len(a):,} firm-years, {a.cik.nunique():,} firms')
log.append('by period:\n' + a.groupby('period', observed=True).size().to_string())
log.append('by sic:\n' + a.groupby('sic').size().to_string())
log.append('rev_src counts:\n' + a.rev_src.value_counts().to_string())
log.append(f"capex missing share: {a.capex_missing.mean():.3f}; sbc missing share: {a.sbc.isna().mean():.3f}")
log.append(f"acquisition-flagged firm-years: {int(a.acq_flag.sum()):,} ({a.acq_flag.mean():.3f}); among g>=50%: {a[a.g>=.5].acq_flag.mean():.3f}")
log.append(f"S&M share (lagged) available: {a.sm_lag_share.notna().mean():.3f}")
a.to_csv(f'{BASE}/data/panel.csv', index=False)
open(f'{BASE}/notes/panel_build_log.txt', 'w').write('\n'.join(log) + '\n')
print('\n'.join(log))
