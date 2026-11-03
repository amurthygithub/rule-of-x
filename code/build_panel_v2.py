"""Build the firm-year panel 'as first reported' from SEC companyfacts (second version, after referee review).

For each firm and fiscal year ending on date E, every item is taken from the ORIGINAL annual filing for that year
(the earliest-filed 10-K, 10-K/A, 10-KT, 20-F or 40-F that reports an annual revenue fact ending on E). Growth is
computed within that same filing (it reports both E and the prior fiscal year), so the two years are on the same
basis even when later filings restate them (for example after a divestiture is reclassified as discontinued
operations). Revenue is the largest revenue element reported for the year in that filing, which guards against
picking a component. Instants (goodwill, PP&E) are taken at the fiscal year-end E, so acquisition flags are aligned
with the fiscal year.

Inputs : data/companyfacts_extract.json  {cik: {"acc": [[accn, filed, form], ...], "f": [[ci, acc_idx, start, end, val], ...]}}
         data/sic_universe.json
Outputs: data/panel_v2_all.csv (all firm-years), data/panel_broad.csv (SIC 7370-7374 analysis sample),
         data/panel.csv (core software sample, SIC 7372), notes/panel_build_log.txt
"""
import os
import sys
import json
from collections import defaultdict
from datetime import date
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exclusions import is_excluded  # noqa: E402  registrants excluded at the author's request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # replication-package root
CON = ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'RevenueFromContractWithCustomerIncludingAssessedTax',
       'SalesRevenueNet', 'SalesRevenueServicesNet', 'OperatingIncomeLoss', 'NetCashProvidedByUsedInOperatingActivities',
       'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations', 'PaymentsToAcquirePropertyPlantAndEquipment',
       'PaymentsToAcquireProductiveAssets', 'PaymentsForCapitalImprovements', 'PaymentsToAcquireOtherPropertyPlantAndEquipment',
       'PaymentsForSoftware', 'PaymentsToDevelopSoftware', 'RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability',
       'FinanceLeasePrincipalPayments', 'ShareBasedCompensation', 'AllocatedShareBasedCompensationExpense',
       'SellingAndMarketingExpense', 'SellingGeneralAndAdministrativeExpense', 'GeneralAndAdministrativeExpense', 'GrossProfit',
       'CostOfRevenue', 'CostOfGoodsAndServicesSold', 'DepreciationDepletionAndAmortization', 'DepreciationAndAmortization',
       'Goodwill', 'PropertyPlantAndEquipmentNet', 'PaymentsToAcquireBusinessesNetOfCashAcquired', 'PaymentsToAcquireBusinessesGross',
       'BusinessAcquisitionsProFormaRevenue', 'IncomeLossFromDiscontinuedOperationsNetOfTax',
       'IncomeLossFromDiscontinuedOperationsNetOfTaxAttributableToReportingEntity', 'NetIncomeLoss', 'ResearchAndDevelopmentExpense']
REV = set(range(5))
INSTANT = {'Goodwill', 'PropertyPlantAndEquipmentNet'}
raw = {c: b for c, b in json.load(open(f'{BASE}/data/companyfacts_extract.json')).items() if not is_excluded(c)}
uni = [r for r in json.load(open(f'{BASE}/data/sic_universe.json')) if not is_excluded(r[1])]
sic_map = {int(r[1]): int(r[0]) for r in uni}
name_map = {int(r[1]): r[2] for r in uni}
loc_map = {int(r[1]): r[3] for r in uni}
log = []

def D(s):
    return date.fromisoformat(s)

rows = []
n_fallback_items = 0
for cik_s, blob in raw.items():
    cik = int(cik_s)
    acc = blob['acc']
    filed = {i: a[1] for i, a in enumerate(acc)}
    # index facts: by (concept, end) -> list of (filed, acc_idx, start, val)
    flows = defaultdict(list)
    inst = defaultdict(list)
    for ci, ai, start, end, val in blob['f']:
        c = CON[ci]
        if val is None:
            continue
        if c in INSTANT:
            inst[(c, end)].append((filed[ai], ai, val))
        else:
            if not start:
                continue
            days = (D(end) - D(start)).days
            if 340 <= days <= 392:
                flows[(c, end)].append((filed[ai], ai, val))
    # fiscal year ends from annual revenue facts
    ends = sorted({e for (c, e) in flows if CON.index(c) in REV})
    for E in ends:
        rev_facts = [(f, a, v) for ci in REV for (f, a, v) in flows.get((CON[ci], E), [])]
        if not rev_facts:
            continue
        a0 = min(rev_facts)[1]                      # original filing: earliest filed
        f0 = filed[a0]
        rev = max(v for (f, a, v) in rev_facts if a == a0)
        # prior fiscal year in the same filing
        prevE = [e for (c, e) in flows if CON.index(c) in REV and 345 <= (D(E) - D(e)).days <= 385
                 and any(a == a0 for (_, a, _) in flows[(c, e)])]
        rev_prev = None
        if prevE:
            Ep = max(prevE)
            vals = [v for ci in REV for (f, a, v) in flows.get((CON[ci], Ep), []) if a == a0]
            rev_prev = max(vals) if vals else None
        rec = dict(cik=cik, fy_end=E, accn=acc[a0][0], filed=f0, form=acc[a0][2], rev=rev, rev_prev=rev_prev)

        def get(c, end=E, instant=False):
            global n_fallback_items
            pool = (inst if instant else flows).get((c, end), [])
            same = [v for (f, a, v) in pool if a == a0]
            if same:
                return same[0], 0
            if pool:
                return min(pool)[2], 1          # earliest other filing
            return None, 0

        fb = 0
        fb_items = []
        for c in CON[5:]:
            v, flag = get(c, instant=(c in INSTANT))
            rec[c] = v
            fb += flag
            if flag:
                fb_items.append(c)
        rec['fb_items'] = ';'.join(fb_items)
        if prevE:
            rec['Goodwill_prev'] = get('Goodwill', end=max(prevE), instant=True)[0]
            for c in ['SellingAndMarketingExpense']:
                rec[c + '_prev'] = get(c, end=max(prevE))[0]
        rec['n_fallback'] = fb
        rows.append(rec)

p = pd.DataFrame(rows)
log.append(f'firms: {p.cik.nunique():,}; firm-years (any fiscal year): {len(p):,}')
p['fy_end_d'] = pd.to_datetime(p.fy_end)
p['year'] = np.where(p.fy_end_d.dt.month >= 6, p.fy_end_d.dt.year, p.fy_end_d.dt.year - 1)   # Compustat convention
p = p.sort_values(['cik', 'fy_end_d']).drop_duplicates(['cik', 'year'], keep='last')

def first(df, cols):
    out = pd.Series(np.nan, index=df.index)
    for c in cols:
        if c in df:
            out = out.fillna(df[c])
    return out

p['g'] = p.rev / p.rev_prev - 1
p['op_inc'] = p['OperatingIncomeLoss']
p['ocf'] = first(p, ['NetCashProvidedByUsedInOperatingActivitiesContinuingOperations', 'NetCashProvidedByUsedInOperatingActivities'])
p['capex_ppe'] = first(p, ['PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets',
                           'PaymentsForCapitalImprovements', 'PaymentsToAcquireOtherPropertyPlantAndEquipment'])
p['capex_missing'] = p.capex_ppe.isna()
p['cap_sw'] = p['PaymentsForSoftware'].fillna(0) + p['PaymentsToDevelopSoftware'].fillna(0)
p['lease_rou'] = p['RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability'].fillna(0)
p['sbc'] = first(p, ['ShareBasedCompensation', 'AllocatedShareBasedCompensationExpense'])
p['sm'] = p['SellingAndMarketingExpense']
fbi = p['fb_items'].fillna('')
def from_original(cols):
    # item taken from the original filing: the element actually used was reported there (NaN if the item is missing)
    used = pd.Series(None, index=p.index, dtype=object)
    for c in cols:
        used = used.where(used.notna() | p[c].isna(), c)
    return pd.Series([np.nan if u is None or pd.isna(u) else float(u not in s.split(';')) for u, s in zip(used, fbi)], index=p.index)
p['orig_op'] = from_original(['OperatingIncomeLoss'])
p['orig_ocf'] = from_original(['NetCashProvidedByUsedInOperatingActivitiesContinuingOperations', 'NetCashProvidedByUsedInOperatingActivities'])
p['orig_capex'] = from_original(['PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets',
                                 'PaymentsForCapitalImprovements', 'PaymentsToAcquireOtherPropertyPlantAndEquipment'])
p['orig_sbc'] = from_original(['ShareBasedCompensation', 'AllocatedShareBasedCompensationExpense'])
p['ga'] = p['GeneralAndAdministrativeExpense']
p['rd'] = p['ResearchAndDevelopmentExpense']
p['gp'] = p['GrossProfit'].fillna(p.rev - first(p, ['CostOfRevenue', 'CostOfGoodsAndServicesSold']))
p['disc_flag'] = ((p['IncomeLossFromDiscontinuedOperationsNetOfTax'].fillna(0).abs() > 0) |
                  (p['IncomeLossFromDiscontinuedOperationsNetOfTaxAttributableToReportingEntity'].fillna(0).abs() > 0)).astype(int)
p['acq_pay'] = first(p, ['PaymentsToAcquireBusinessesNetOfCashAcquired', 'PaymentsToAcquireBusinessesGross'])
p['gw_jump'] = p['Goodwill'] - p['Goodwill_prev']
p['proforma_gap'] = p['BusinessAcquisitionsProFormaRevenue'] - p['rev']
rl = p['rev_prev']
acq_now = ((p.acq_pay.fillna(0) >= 0.25 * rl) | (p.gw_jump.fillna(0) >= 0.25 * rl) | (p.proforma_gap.fillna(0) >= 0.10 * p.rev))
p['acq_now'] = acq_now.astype(int)
p['acq_flag'] = (acq_now | acq_now.groupby(p.cik).shift(1).fillna(False).astype(bool)).astype(int)    # flag t and t+1
p['sm_lag_share'] = p['SellingAndMarketingExpense_prev'] / p['rev_prev']
p['rev_lag'] = p['rev_prev']

# margins
p['m_op'] = p.op_inc / p.rev
p['m_adj'] = (p.op_inc + p.sbc) / p.rev
p['fcf'] = p.ocf - p.capex_ppe - p.cap_sw                  # NaN when capex is not reported
p['m_fcf'] = p.fcf / p.rev
p['m_fcf_sbc'] = (p.fcf - p.sbc) / p.rev
p['m_fcf_sbc_lease'] = (p.fcf - p.sbc - p.lease_rou) / p.rev
p['capex_int'] = (p.capex_ppe + p.cap_sw) / p.rev
p['capex_lease_int'] = (p.capex_ppe + p.cap_sw + p.lease_rou) / p.rev

# revenue spikes (scale errors): revenue more than 10x both neighbours
prv = p.groupby('cik').rev.shift(1); nxt = p.groupby('cik').rev.shift(-1)
spike = (p.rev > 10 * prv) & (p.rev > 10 * nxt)
log.append(f'revenue spikes dropped: {int(spike.sum())}')
p = p[~spike]

# duplicate registrants: two CIKs reporting the same revenue in the same fiscal year at least three times
key = p[['cik', 'year', 'rev']].dropna()
key = key[key.rev > 5e7]
key['rk'] = (key.rev / 1e5).round().astype(int)
pairs = key.merge(key, on=['year', 'rk'])
pairs = pairs[pairs.cik_x < pairs.cik_y].groupby(['cik_x', 'cik_y']).size()
dups = pairs[pairs >= 2].reset_index()          # identical revenue (to $0.1M) in two or more fiscal years
nobs = p.groupby('cik').size()
drop = set()
for _, r in dups.iterrows():
    drop.add(r.cik_y if nobs.get(r.cik_x, 0) >= nobs.get(r.cik_y, 0) else r.cik_x)
# predecessor/successor registrants overlapping in a single year (verified by name): drop the predecessor's overlap year
SUCC = [(1288776, 1652044), (1316360, 1598014), (1355754, 1841804)]   # Google/Alphabet, IHS/IHS Markit, Instructure
yr_succ = {(pred, y) for pred, succ in SUCC for y in p.loc[p.cik == succ, 'year']}
over = p.apply(lambda r: (r.cik, r.year) in yr_succ, axis=1)
log.append(f'duplicate registrant pairs: {len(dups)}; registrants dropped: {len(drop)}; predecessor overlap years dropped: {int(over.sum())}')
p = p[~p.cik.isin(drop) & ~over]

p['sic'] = p.cik.map(sic_map)
p['name'] = p.cik.map(name_map)
p['loc'] = p.cik.map(loc_map)
p['period'] = pd.cut(p.year, [2009, 2015, 2019, 2022, 2025], labels=['2010-15', '2016-19', '2020-22', '2023-25'])
for mm in ['m_op', 'm_adj', 'm_fcf', 'm_fcf_sbc', 'm_fcf_sbc_lease']:
    p['R_' + mm[2:]] = p.g + p[mm]
keep = ['cik', 'name', 'sic', 'loc', 'year', 'period', 'fy_end', 'accn', 'form', 'rev', 'rev_lag', 'g', 'op_inc', 'ocf',
        'capex_ppe', 'capex_missing', 'cap_sw', 'lease_rou', 'sbc', 'sm', 'ga', 'gp', 'rd', 'orig_op', 'orig_ocf', 'orig_capex', 'orig_sbc', 'sm_lag_share', 'acq_pay', 'gw_jump', 'proforma_gap',
        'acq_now', 'acq_flag', 'disc_flag', 'n_fallback', 'm_op', 'm_adj', 'm_fcf', 'm_fcf_sbc', 'm_fcf_sbc_lease', 'capex_int',
        'capex_lease_int', 'R_op', 'R_adj', 'R_fcf', 'R_fcf_sbc', 'R_fcf_sbc_lease']
p[keep].to_csv(f'{BASE}/data/panel_v2_all.csv', index=False)

a = p[p.year.between(2010, 2025) & p.g.notna() & (p.rev_lag >= 100e6) & (p.g > -0.9) & (p.g < 5)].copy()
for mm in ['m_op', 'm_adj', 'm_fcf', 'm_fcf_sbc', 'm_fcf_sbc_lease']:
    a.loc[(a[mm] < -3) | (a[mm] > 1), mm] = np.nan
    a['R_' + mm[2:]] = a.g + a[mm]
a = a[a.m_op.notna() | a.m_fcf.notna()]
broad = a[a.sic.between(7370, 7374)]
core = a[a.sic == 7372]
broad[keep].to_csv(f'{BASE}/data/panel_broad.csv', index=False)
core[keep].to_csv(f'{BASE}/data/panel.csv', index=False)
for nm, x in [('broad (SIC 7370-7374)', broad), ('core (SIC 7372)', core)]:
    log.append(f'{nm}: {len(x):,} firm-years, {x.cik.nunique():,} firms; by period: ' +
               ', '.join(f'{k} {v}' for k, v in x.groupby("period", observed=True).size().items()))
    log.append(f'  capex missing {x.capex_missing.mean():.3f}; sbc missing {x.sbc.isna().mean():.3f}; acquisition-flagged {x.acq_flag.mean():.3f}; '
               f'discontinued ops {x.disc_flag.mean():.3f}; items from a later filing {(x.n_fallback > 0).mean():.3f}; '
               f'S&M available {x.sm_lag_share.notna().mean():.3f}; finance-lease ROU reported {(x.lease_rou > 0).mean():.3f}')
open(f'{BASE}/notes/panel_build_log.txt', 'w').write('\n'.join(log) + '\n')
print('\n'.join(log))
