#!/usr/bin/env python3
"""Build panel v3: the v2 panel after the sample audit of 29 Oct 2026 (review panels of Paper 1 v1).

v2 files are read, never written. Every rule below is applied by code to every firm-year; the inputs that local
data cannot supply are read from data/v3_inputs/ when present, and the rule is otherwise recorded as not applied.

R1  First reported (applied to all firm-years). A firm-year is excluded when its values come from a filing whose own
    reporting period (the latest annual revenue period it reports) ends after the firm-year's fiscal year end: the
    year exists only as a comparative in a later report, so it was not first reported and, for years before a
    registrant's first annual report, it is selected on a later event (an IPO, spin-off, de-SPAC or the first XBRL
    report). Types: 'fy2010_before_first_xbrl_report' (fiscal 2010, before the registrant's first XBRL annual
    report: XBRL phase-in or pre-registration, which local data cannot tell apart), 'before_first_annual_report'
    (later pre-registration years), 'later_vintage_only' (a year whose own report carries no revenue fact, so its
    values come from a restated later report). Sensitivity kept for the estimation: the fiscal-2010 years of
    registrants that were already public were reported in real time, so the look-ahead objection does not apply to
    them; the variant k2010 adds all fiscal-2010 backfilled years back.
R2  Business classification (applied to the main sample when the business description of every registrant is in
    data/v3_inputs/business_descriptions.json; since 3 Nov 2026 it is). The principal business, read from the
    opening of Item 1 of the latest 10-K (Item 4.B of a 20-F; the AIF of a 40-F), is classified by keyword counts into
    interactive entertainment (video, mobile or online games), gambling (casino gaming equipment or systems, wagering,
    lottery, social casino), compute infrastructure (renting compute or data-centre capacity), or software; a firm is
    excluded when a non-software class has at least three keyword hits and more hits than the software class. The rule
    and its keyword lists were fixed before any description was read and are not changed. Descriptions: the 16 firms
    the review panels named (data/v3_inputs/business_descriptions_named.json, retrieved 29 Oct 2026) and every other
    core registrant (retrieved 3 Nov 2026), merged by code/audit/r2_descriptions.py. The classifier is a partial check:
    it misses game publishers and the AI-cloud provider whose openings do not use its phrases. Sensitivities: the
    classes that two independent readers gave each description (data/v3_inputs/business_class_reader_{a,b}.csv, columns
    cik, name, class, subclass, confidence, reason, quote, note) in business_class_reader_a and _b; and the classifier
    on the 16 named firms alone (business_class_named), which now coincides with the main-sample classes of those firms.
R3  Captive related-party revenue (applied). A firm-year is excluded when related-party revenue is at least 50% of
    revenue: XBRL elements RevenueFromRelatedParties or RelatedPartyTransactionRevenuesFromTransactionsWithRelatedParty
    over revenue (data/v3_inputs/related_party.json, SEC frames: non-dimensional facts, latest filed value), or the
    registrant's own filing states that substantially all revenue comes from related parties
    (data/v3_inputs/captive_verified.csv, with the quoted source).
R4  Acquisition flag v3 (applied to all firm-years). The v2 criteria, with two fixes: (a) when the prior-year-end
    goodwill instant is missing, the goodwill increase is measured from the latest goodwill instant 300 to 770 days
    before the fiscal year end; (b) a cheap-acquisition criterion: cash paid for acquisitions or the goodwill
    increase, C, is at least 10% of prior-year revenue and growth accelerates, relative to the year's median growth
    in the v2 core sample, by at least C (so the acquisition could explain the acceleration at a price of at most
    one times revenue). The flag covers the year and the following fiscal year; v2 shifted by row, so seven
    following-year flags crossed gaps in a firm's years, and v3 shifts by fiscal year. (c) A year in which acquired
    businesses contributed at least 10% of revenue since their acquisition dates is flagged as well (XBRL
    BusinessCombinationProFormaInformationRevenueOfAcquireeSinceAcquisitionDateActual, data/v3_inputs/acquiree_revenue.json).
    Coverage of (c) is thin: the element is usually tagged on a business-combination axis, and SEC frames keep only
    non-dimensional facts (63 facts for the panel's registrants).
R5  No listed equity (flagged, not excluded). Read from the sign of dei:EntityPublicFloat on the 10-K cover page by
    fiscal year (data/v3_inputs/listing_status.json: any float instant in the 366 days up to the fiscal year end;
    SEC frames, latest filed). The float is measured at the end of the second fiscal quarter, so a zero float also
    occurs in the first annual report after an IPO or spin-off; the rule separates the two. For a 10-K firm-year with a
    float fact that is not positive: (i) IPO or spin-off timing when the firm reports a positive float in one of the
    next two fiscal years; (ii) IPO timing, unresolved, when the year is the firm's first annual report and its only
    float fact (the 2025 IPOs, whose next report does not exist yet); (iii) otherwise no listed equity. A firm-year
    without a float fact takes the status no listed equity when the firm's nearest float facts on each available side
    are no listed equity (gaps in a debt-only filer's tagging), and is unknown otherwise. 20-F and 40-F annual reports
    are not tested: their cover pages report shares outstanding, not public float, so a zero there is not evidence;
    their Section 12(b) listing is on the cover page, which is not in the inputs. Status in r5_status, flag in
    no_listed_equity. Current EDGAR names cannot stand in: Informatica LLC, VMware LLC and 2U, LLC carry post-delisting
    names but their panel years are listed years. The four debt-only filers named by the finance referee stay in
    debt_only_named so the earlier with-and-without comparison is kept.
B5  Cash-score bridge (columns only). Interest paid and income taxes paid by firm-year (data/v3_inputs/cash_interest_taxes.json:
    InterestPaidNet, else InterestPaid; IncomeTaxesPaidNet, else IncomeTaxesPaid; SEC frames, latest filed value, not
    first reported). A missing element counts as zero when the firm-year reports any of the four; the columns are
    missing when it reports none.
C1  Capitalized software from the filing (data/v3_inputs/capitalized_software_filings.json, {cik: {fy_end: {value, accn,
    label}}}). The panel's cap_sw is PaymentsForSoftware + PaymentsToDevelopSoftware (build_panel_v2.py), so a filer
    that tags capitalized software with a company-specific element shows 0 and its free cash flow is overstated. Where
    the XBRL cap_sw is 0 and the file holds the outflow read from the cash-flow statement of the same filing
    (code/audit/capsw_scan_parse.py; data audit of 3 Nov 2026), cap_sw takes the filing value and every column built
    on it is recomputed as in build_panel_v2.py: m_fcf, m_fcf_sbc, m_fcf_sbc_lease (margins outside [-3, 1] missing in
    the core sample), R_fcf, R_fcf_sbc, R_fcf_sbc_lease, capex_int and capex_lease_int. cap_sw_xbrl keeps the XBRL
    value and cap_sw_source says which was used ('xbrl' or 'filing_cash_flow_statement').

Inputs : data/panel_v2_all.csv, data/panel.csv, data/companyfacts_extract.json, data/v3_inputs/* (optional)
Outputs: data/panel_v3_all.csv (all firm-years, v2 columns plus audit columns), data/panel_v3_core_full.csv (the
         1,929 v2 core firm-years with audit columns and the exclusion reason), data/panel_v3.csv (the v3 core
         analysis sample), notes/panel_v3_build.json (counts and firm lists)
"""
import json
import os
import sys
from datetime import date

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exclusions import drop_excluded, is_excluded  # noqa: E402  registrants excluded at the author's request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INP = f'{BASE}/data/v3_inputs'
D = date.fromisoformat
REV = {0, 1, 2, 3, 4}                    # revenue elements in build_panel_v2.CON
GW = 26                                   # Goodwill in build_panel_v2.CON
CHEAP_MIN, RP_MAX = 0.10, 0.50
PANEL_NAMED = {2491: 'casino gaming (IB)', 712515: 'games (IB, FR)', 718877: 'games (IB, FR)', 946581: 'games (IB, FR)',
               1315098: 'games (IB, FR)', 1823878: 'games (IB, FR)', 1769628: 'compute infrastructure (IB)',
               1510593: 'internet services (IB)', 865570: 'games (FR)', 1810806: 'game engine (FR)',
               1512673: 'payments, bitcoin revenue gross (FR)', 910638: '3D printers (FR)', 1340476: 'modular interiors (FR)',
               1607310: 'driver-assistance chips (FR)', 1910139: 'driver-assistance chips (FR)', 1788999: 'licensing and devices (FR)'}
DEBT_NAMED = {1337272: 'SunGard', 1556148: 'Infor, Inc.', 1517393: 'Epicor Software Corp', 1501919: 'SSI Investments II Ltd'}

raw = {c: b for c, b in json.load(open(f'{BASE}/data/companyfacts_extract.json')).items() if not is_excluded(c)}
P = drop_excluded(pd.read_csv(f'{BASE}/data/panel_v2_all.csv')).sort_values(['cik', 'fy_end'], kind='stable').reset_index(drop=True)
core = drop_excluded(pd.read_csv(f'{BASE}/data/panel.csv')).reset_index(drop=True)

# ------------------------------------------------------------------------------------------- C1 capitalized software
_csw_path = f'{INP}/capitalized_software_filings.json'
csw = json.load(open(_csw_path)) if os.path.exists(_csw_path) else {}      # {cik: {fy_end: {value, accn, label}}}
N_CSW = sum(len(v) for v in csw.values())


def capsw_fix(df, trim):
    """C1: the filing's capitalized-software outflow where the XBRL elements give 0, and the columns built on it."""
    rec_ = [csw.get(str(c), {}).get(e) for c, e in zip(df.cik, df.fy_end)]
    hit = pd.Series([r_ is not None for r_ in rec_], index=df.index) & (df.cap_sw == 0)
    assert all(r_['accn'] == a_ for r_, a_, h_ in zip(rec_, df.accn, hit) if h_), 'filing value read from another filing'
    df['cap_sw_xbrl'] = df.cap_sw
    df['cap_sw_source'] = np.where(hit, 'filing_cash_flow_statement', 'xbrl')
    df.loc[hit, 'cap_sw'] = [float(r_['value']) for r_, h_ in zip(rec_, hit) if h_]
    fcf = df.ocf - df.capex_ppe - df.cap_sw                  # as build_panel_v2.py (NaN when capex is not reported)
    new = dict(m_fcf=fcf / df.rev, m_fcf_sbc=(fcf - df.sbc) / df.rev, m_fcf_sbc_lease=(fcf - df.sbc - df.lease_rou) / df.rev,
               capex_int=(df.capex_ppe + df.cap_sw) / df.rev, capex_lease_int=(df.capex_ppe + df.cap_sw + df.lease_rou) / df.rev)
    for c_, v_ in new.items():
        if trim and c_.startswith('m_'):
            v_ = v_.where((v_ >= -3) & (v_ <= 1))               # analysis bounds of build_panel_v2.py
        df.loc[hit, c_] = v_[hit]
    for mm in ('m_fcf', 'm_fcf_sbc', 'm_fcf_sbc_lease'):
        df.loc[hit, 'R_' + mm[2:]] = (df.g + df[mm])[hit]
    if trim:                                                  # build_panel_v2.py keeps a core row with m_op or m_fcf
        assert (df.m_op.notna() | df.m_fcf.notna())[hit].all()
    return hit


csw_hit_all, csw_hit_core = capsw_fix(P, trim=False), capsw_fix(core, trim=True)
assert int(csw_hit_core.sum()) == int(csw_hit_all.sum()) == N_CSW, 'a filing value matched no firm-year with cap_sw = 0'

# ------------------------------------------------------------------------------------------- R1 first reported
own, filed, gw = {}, {}, {}
for cik, b in raw.items():
    mx, g = {}, {}
    for ci, ai, s, e, v in b['f']:
        if ci in REV and s and 340 <= (D(e) - D(s)).days <= 392:
            mx[ai] = max(mx.get(ai, ''), e)
        if ci == GW:
            f = b['acc'][ai][1]
            if e not in g or f < g[e][0]:
                g[e] = (f, v)
    for i, a in enumerate(b['acc']):
        own[a[0]] = mx.get(i)
        filed[a[0]] = a[1]
    gw[int(cik)] = {e: v for e, (f, v) in g.items()}
P['filed'] = P.accn.map(filed)
P['src_period_end'] = P.accn.map(own)
P['backfill'] = P.src_period_end > P.fy_end
first_own = P[P.src_period_end == P.fy_end].groupby('cik').fy_end.min()
P['first_own_fy_end'] = P.cik.map(first_own)
before = P.backfill & (P.first_own_fy_end.isna() | (P.fy_end < P.first_own_fy_end))
P['backfill_type'] = np.select([before & (P.year == 2010), before, P.backfill],
                               ['fy2010_before_first_xbrl_report', 'before_first_annual_report', 'later_vintage_only'], '')

# ------------------------------------------------------------------------------------------- R4 acquisition flag
def gw_prior(cik, E):
    best = None
    for e, v in gw.get(cik, {}).items():
        if 300 <= (D(E) - D(e)).days <= 770 and (best is None or e > best[0]):
            best = (e, v)
    return best


cur, pri = [], []
for r in P.itertuples():
    cur.append(gw.get(r.cik, {}).get(r.fy_end, np.nan))
    b = gw_prior(r.cik, r.fy_end)
    pri.append(b[1] if b else np.nan)
P['gw_cur'], P['gw_prior_fallback'] = cur, pri
P['gw_jump_v3'] = P.gw_jump.where(P.gw_jump.notna(), P.gw_cur - P.gw_prior_fallback)
rl = P.rev_lag
P['acq_spend_share'] = np.fmax(P.acq_pay.fillna(0), P.gw_jump_v3.fillna(0)) / rl
grp = P.groupby('cik')
consec = grp.year.shift(1) == P.year - 1
P['g_prev'] = grp.g.shift(1).where(consec)
Gc = core.groupby('year').g.median()                     # benchmark of estimate_revised.py (v2 core sample)
P['accel_rel'] = (P.g - P.year.map(Gc)) - (P.g_prev - (P.year - 1).map(Gc))
v2_now = P.acq_now == 1
gw_fix = (P.gw_jump_v3.fillna(0) >= 0.25 * rl) & ~v2_now
cheap = (P.acq_spend_share >= CHEAP_MIN) & (P.accel_rel >= P.acq_spend_share) & P.g_prev.notna() & ~v2_now & ~gw_fix
P['acq_now_v3'] = (v2_now | gw_fix | cheap).astype(int)
prev_now = (P.acq_now_v3.astype(float).groupby(P.cik).shift(1).fillna(0) > 0) & consec     # by fiscal year, not by row
acq_rev = os.path.exists(f'{INP}/acquiree_revenue.json')
P['acquiree_rev_share'] = np.nan
if acq_rev:                                                # R4(c): revenue of acquirees since the acquisition date
    ar = json.load(open(f'{INP}/acquiree_revenue.json'))   # {cik: {fy_end: value}}
    P['acquiree_rev_share'] = [ar.get(str(c), {}).get(e, np.nan) / s_ if s_ else np.nan for c, e, s_ in zip(P.cik, P.fy_end, P.rev)]
    extra = (P.acquiree_rev_share >= 0.10) & (P.acq_now_v3 == 0)
    P.loc[extra, 'acq_now_v3'] = 1
else:
    extra = pd.Series(False, index=P.index)
prev_now = (P.acq_now_v3.astype(float).groupby(P.cik).shift(1).fillna(0) > 0) & consec
v2_row_shift_gap = (P.acq_now.astype(float).groupby(P.cik).shift(1).fillna(0) > 0) & ~consec & (P.acq_now == 0)
P['v2_flag_across_gap'] = v2_row_shift_gap & (P.acq_flag == 1)
P['acq_flag_v3'] = ((P.acq_now_v3 == 1) | prev_now).astype(int)
P['acq_reason_v3'] = np.select([v2_now, gw_fix, cheap, extra, prev_now],
                               ['v2_criteria', 'goodwill_fallback', 'cheap_acquisition', 'acquiree_revenue', 'following_year'], '')
assert ((P.acq_flag_v3 >= P.acq_flag) | P.v2_flag_across_gap).all()   # v3 keeps every v2 flag except row shifts across gaps

# ------------------------------------------------------------------------------------------- R2 and R3 inputs
P['panel_named'] = P.cik.map(PANEL_NAMED).fillna('')
P['debt_only_named'] = P.cik.isin(DEBT_NAMED)
P['no_listed_equity'] = np.nan                             # R5: from data/v3_inputs/listing_status.json
P['r5_status'] = 'not available'
r5_applied = os.path.exists(f'{INP}/listing_status.json')
if r5_applied:
    ls_ = {int(c): {int(y): bool(v) for y, v in d.items()} for c, d in json.load(open(f'{INP}/listing_status.json')).items()}
    foreign = P.form.str.startswith(('20-F', '40-F'))
    first_ar = P.fy_end == P.first_own_fy_end              # the firm's first annual report (rule R1's first own period)
    st = []
    for c, y, fo, fa in zip(P.cik, P.year, foreign, first_ar):
        f = ls_.get(c, {})
        if fo:
            st.append('foreign_not_tested')
        elif y not in f:
            st.append('unknown')
        elif f[y]:
            st.append('listed')
        elif f.get(y + 1) or f.get(y + 2):
            st.append('ipo_timing')
        elif fa and len(f) == 1:
            st.append('ipo_timing_unresolved')
        else:
            st.append('no_listed_equity')
    P['r5_status'] = st
    for c, g_ in P.groupby('cik'):                          # untagged years inside or next to a debt-only spell
        known = g_[g_.r5_status != 'unknown']
        for i in g_.index[g_.r5_status == 'unknown']:
            y = P.at[i, 'year']
            before, after = known[known.year < y].tail(1), known[known.year > y].head(1)
            sides = [s_.r5_status.iloc[0] for s_ in (before, after) if len(s_)]
            if sides and all(s_ == 'no_listed_equity' for s_ in sides):
                P.at[i, 'r5_status'] = 'no_listed_equity_untagged'
    P['no_listed_equity'] = np.where(P.r5_status.str.startswith('no_listed_equity'), True,
                                     np.where(P.r5_status.isin(['unknown', 'not available']), np.nan, False))
KW = {'interactive_entertainment': ['video game', 'mobile game', 'interactive entertainment', 'game developer', 'publisher of games',
                                    'franchise', 'console', 'players'],
      'gambling': ['casino', 'gaming machine', 'slot', 'wagering', 'sports betting', 'lottery', 'igaming', 'social casino'],
      'compute_infrastructure': ['gpu', 'data center capacity', 'compute capacity', 'ai infrastructure', 'high-performance compute'],
      'software': ['software', 'saas', 'cloud-based', 'platform', 'subscription', 'application']}


def classify(desc):
    cls, hits_all = {}, {}
    for c, t in desc.items():
        t = t.lower()
        hits = {k: sum(t.count(w) for w in ws) for k, ws in KW.items()}
        best = max((k for k in hits if k != 'software'), key=lambda k: hits[k])
        cls[int(c)] = best if hits[best] >= 3 and hits[best] > hits['software'] else 'software'
        hits_all[int(c)] = hits
    return cls, hits_all


NONSW = ['interactive_entertainment', 'gambling', 'compute_infrastructure']   # classes R2 excludes
P['business_class'] = ''                                   # R2, main sample: only from descriptions of every registrant
r2_applied = os.path.exists(f'{INP}/business_descriptions.json')
cls, hits_main = {}, {}
if r2_applied:
    cls, hits_main = classify(json.load(open(f'{INP}/business_descriptions.json')))      # {cik: text}
    assert set(core.cik) <= set(cls), 'R2 applied without the description of every core registrant'
    P['business_class'] = P.cik.map(cls).fillna('')
P['business_class_named'] = ''                             # R2 on the review panels' named firms only (sensitivity)
r2_named = os.path.exists(f'{INP}/business_descriptions_named.json')
cls_named, hits_named = classify(json.load(open(f'{INP}/business_descriptions_named.json'))) if r2_named else ({}, {})
P['business_class_named'] = P.cik.map(cls_named).fillna('')
assert all(cls[c_] == k_ for c_, k_ in cls_named.items()) if r2_applied else True   # same text, same class
RCLS = {'software', 'interactive_entertainment', 'gambling', 'compute_infrastructure', 'other_non_software'}
readers = {}                                               # R2 sensitivity: independent readings of the same descriptions
for rd in ('a', 'b'):
    P[f'business_class_reader_{rd}'] = ''
    f_ = f'{INP}/business_class_reader_{rd}.csv'
    if os.path.exists(f_):
        x_ = pd.read_csv(f_)
        assert x_.cik.is_unique and set(x_['class']) <= RCLS and set(core.cik) <= set(x_.cik), f_
        readers[rd] = dict(zip(x_.cik.astype(int), x_['class']))
        P[f'business_class_reader_{rd}'] = P.cik.map(readers[rd]).fillna('')
# B5: interest paid and income taxes paid (cash-score bridge)
CF_ELEMS = ['InterestPaid', 'InterestPaidNet', 'IncomeTaxesPaid', 'IncomeTaxesPaidNet']
P['interest_paid'], P['income_taxes_paid'], P['interest_paid_element'], P['income_taxes_paid_element'] = np.nan, np.nan, '', ''
b5 = os.path.exists(f'{INP}/cash_interest_taxes.json')
if b5:
    cit = json.load(open(f'{INP}/cash_interest_taxes.json'))          # {cik: {fy_end: {element: value}}}
    ip_, tp_, ie_, te_ = [], [], [], []
    for c, e in zip(P.cik, P.fy_end):
        d = cit.get(str(c), {}).get(e, {})
        ie = 'InterestPaidNet' if 'InterestPaidNet' in d else ('InterestPaid' if 'InterestPaid' in d else '')
        te = 'IncomeTaxesPaidNet' if 'IncomeTaxesPaidNet' in d else ('IncomeTaxesPaid' if 'IncomeTaxesPaid' in d else '')
        ip_.append((d[ie] if ie else 0.0) if d else np.nan)
        tp_.append((d[te] if te else 0.0) if d else np.nan)
        ie_.append(ie if d else '')
        te_.append(te if d else '')
    P['interest_paid'], P['income_taxes_paid'], P['interest_paid_element'], P['income_taxes_paid_element'] = ip_, tp_, ie_, te_
P['rp_revenue_share'] = np.nan
r3_xbrl = os.path.exists(f'{INP}/related_party.json')
if r3_xbrl:
    rp = json.load(open(f'{INP}/related_party.json'))                 # {cik: {fy_end: related-party revenue}}
    P['rp_revenue_share'] = [rp.get(str(c), {}).get(e, np.nan) / s if s else np.nan for c, e, s in zip(P.cik, P.fy_end, P.rev)]
ver = pd.read_csv(f'{INP}/captive_verified.csv')
ver_keys = {(int(r.cik), int(r.year)) for r in ver.itertuples()}
P['captive_verified'] = [(c, y) in ver_keys for c, y in zip(P.cik, P.year)]
P['captive'] = (P.rp_revenue_share >= RP_MAX) | P.captive_verified

# ------------------------------------------------------------------------------------------- exclusion reason
excl_class = P.business_class.isin(NONSW)
P['v3_exclude'] = np.select([P.backfill, P.captive, excl_class],
                            ['R1_not_first_reported', 'R3_captive_related_party', 'R2_not_software'], '')
AUD = ['filed', 'src_period_end', 'backfill', 'backfill_type', 'first_own_fy_end', 'gw_cur', 'gw_prior_fallback', 'gw_jump_v3',
       'acq_spend_share', 'g_prev', 'accel_rel', 'acquiree_rev_share', 'acq_now_v3', 'acq_flag_v3', 'acq_reason_v3', 'v2_flag_across_gap',
       'panel_named', 'debt_only_named', 'no_listed_equity', 'business_class', 'rp_revenue_share', 'captive_verified', 'captive', 'v3_exclude',
       'r5_status', 'business_class_named', 'interest_paid', 'income_taxes_paid', 'interest_paid_element', 'income_taxes_paid_element',
       'business_class_reader_a', 'business_class_reader_b']
P['in_core_v2'] = P.set_index(['cik', 'year', 'fy_end']).index.isin(core.set_index(['cik', 'year', 'fy_end']).index)
P.to_csv(f'{BASE}/data/panel_v3_all.csv', index=False)
cf = core.merge(P[['cik', 'year', 'fy_end'] + AUD], on=['cik', 'year', 'fy_end'], how='left', validate='one_to_one')
assert cf.v3_exclude.notna().all() and len(cf) == len(core)
_chk = cf.merge(P[['cik', 'fy_end', 'cap_sw', 'capex_int']], on=['cik', 'fy_end'], suffixes=('', '_all'))   # C1 in both files
assert (_chk.cap_sw == _chk.cap_sw_all).all() and np.allclose(_chk.capex_int, _chk.capex_int_all, equal_nan=True)
cf.to_csv(f'{BASE}/data/panel_v3_core_full.csv', index=False)
v3 = cf[cf.v3_exclude == '']
v3.to_csv(f'{BASE}/data/panel_v3.csv', index=False)

# ------------------------------------------------------------------------------------------- build record
lst = lambda d: sorted({f'{n} {y}' for n, y in zip(d.name, d.year)})
firms = lambda d: sorted(d.name.unique().tolist())
newflag = cf[(cf.acq_flag_v3 == 1) & (cf.acq_flag == 0)]
rec = dict(
    rules=dict(R1='applied', R2=(f'applied to the main sample (keyword classifier fixed before any description was read, run on '
                                 f'the descriptions of all {len(cls)} core registrants; a partial check)') if r2_applied else ('main sample: not applied (descriptions exist only for the 16 named firms); '
                                                                'named firms: classified, sensitivity only' if r2_named else
                                                                'defined, not applied: no business descriptions available locally'),
               R3=('applied (XBRL related-party revenue, and filing text where verified)' if r3_xbrl else
                   'applied where filing text was verified (data/v3_inputs/captive_verified.csv); XBRL related-party elements not available locally'),
               R4='applied' + (' (criteria a, b and c)' if acq_rev else '; criterion (c), acquiree revenue since the acquisition date, not applied: element not in the extract'),
               R5='applied (flag and sensitivity, not an exclusion)' if r5_applied else 'defined, not applied: listing status not available locally',
               cheap_acquisition_min_share=CHEAP_MIN, related_party_max_share=RP_MAX),
    core_v2=int(len(cf)), core_v3=int(len(v3)), firms_v2=int(cf.cik.nunique()), firms_v3=int(v3.cik.nunique()),
    excluded={k: int(v) for k, v in cf.v3_exclude.value_counts().items() if k},
    R1=dict(n=int(cf.backfill.sum()), by_type={k: int(v) for k, v in cf.backfill_type.value_counts().items() if k},
            by_period={k: int(v) for k, v in cf[cf.backfill].groupby('period').size().items()},
            median_growth_backfilled=float(cf[cf.backfill].g.median()), median_growth_other=float(cf[~cf.backfill].g.median()),
            later_vintage_only=lst(cf[cf.backfill_type == 'later_vintage_only']),
            firm_years=lst(cf[cf.backfill])),
    R3=dict(firm_years=lst(cf[cf.captive]), sources=ver.to_dict(orient='records')),
    R4=dict(v2_flagged=int(cf.acq_flag.sum()), v3_flagged=int(cf.acq_flag_v3.sum()),
            new_acquisition_years={k: lst(cf[(cf.acq_reason_v3 == k)]) for k in ['goodwill_fallback', 'cheap_acquisition']},
            new_following_years=lst(newflag[newflag.acq_reason_v3 == 'following_year']),
            v2_following_flags_across_gaps=lst(cf[cf.v2_flag_across_gap]),
            v2_following_flags_across_gaps_all_panel=lst(P[P.v2_flag_across_gap]),
            removed_by_year_shift=lst(cf[(cf.acq_flag == 1) & (cf.acq_flag_v3 == 0)]),
            acquiree_revenue_extra=(int(((cf.acquiree_rev_share >= 0.10)).sum()) if acq_rev else None)),
    R5=dict(debt_only_named=sorted(DEBT_NAMED.values()), firm_years_core_v2=int(cf.debt_only_named.sum()),
            firm_years_v3=int(v3.debt_only_named.sum()),
            informatica_llc_annual_reports=sorted({a[1][:4] for a in raw['1080099']['acc']})),
    panel_named=dict(firms={n: PANEL_NAMED[c] for c, n in zip(cf.cik, cf.name) if c in PANEL_NAMED},
                     firm_years_in_v3=int(v3.panel_named.ne('').sum())),
    v3_by_period={k: int(v) for k, v in v3.groupby('period').size().items()})
if r3_xbrl:
    rpc = cf[cf.rp_revenue_share.notna()]
    rec['R3']['xbrl'] = dict(core_v2_firm_years_with_fact=int(len(rpc)), core_v3_firm_years_with_fact=int(v3.rp_revenue_share.notna().sum()),
                             firms_with_fact=int(rpc.cik.nunique()), n_at_or_above_50pct=int((rpc.rp_revenue_share >= RP_MAX).sum()),
                             max_share=float(rpc.rp_revenue_share.max()),
                             top=[f'{n} {y}: {100 * s_:.1f}%' for n, y, s_ in rpc.sort_values('rp_revenue_share', ascending=False)[['name', 'year', 'rp_revenue_share']].head(5).values])
if acq_rev:
    arc = cf[cf.acquiree_rev_share.notna()]
    rec['R4']['acquiree_revenue'] = dict(
        facts_matched_panel=int(P.acquiree_rev_share.notna().sum()), core_v2_firm_years_with_fact=int(len(arc)),
        core_v2_at_or_above_10pct=lst(arc[arc.acquiree_rev_share >= 0.10]), core_v3_at_or_above_10pct=lst(v3[v3.acquiree_rev_share >= 0.10]),
        new_flags_core_v2=lst(cf[cf.acq_reason_v3 == 'acquiree_revenue']), new_flags_all_panel=lst(P[P.acq_reason_v3 == 'acquiree_revenue']),
        note='frames keep only non-dimensional facts; the element is usually tagged on a business-combination axis, so coverage is thin')
if r5_applied:
    dl = lambda d: {n: sorted(int(y) for y in g_.year) for n, g_ in d.groupby('name')}
    rec['R5'].update(
        status_counts_core_v2={k: int(v) for k, v in cf.r5_status.value_counts().items()},
        status_counts_v3={k: int(v) for k, v in v3.r5_status.value_counts().items()},
        no_listed_equity_core_v2=dl(cf[cf.no_listed_equity == True]), no_listed_equity_v3=dl(v3[v3.no_listed_equity == True]),
        firm_years_no_listed_equity_v3=int((v3.no_listed_equity == True).sum()),
        ipo_timing=dl(cf[cf.r5_status == 'ipo_timing']), ipo_timing_unresolved=dl(cf[cf.r5_status == 'ipo_timing_unresolved']),
        foreign_zero_float=dl(cf[(cf.r5_status == 'foreign_not_tested') & cf.cik.map(lambda c: c in ls_ and not all(ls_[c].values()))]))
if r2_named:
    rec['R2_named'] = dict(classes={n: cls_named.get(int(c), '') for c, n in zip(cf.cik, cf.name) if int(c) in cls_named},
                           hits={n: hits_named[int(c)] for c, n in zip(cf.cik, cf.name) if int(c) in hits_named},
                           non_software=sorted({n for c, n in zip(cf.cik, cf.name) if cls_named.get(int(c), 'software') != 'software'}),
                           firm_years_v3_non_software=int(v3.business_class_named.isin(['interactive_entertainment', 'gambling', 'compute_infrastructure']).sum()),
                           note='rule as defined before the descriptions were read; keyword lists not changed after reading them')
firm_names = dict(zip(cf.cik.astype(int), cf.name))
if r2_applied:
    ex2 = cf[cf.v3_exclude == 'R2_not_software']
    ns_firms = sorted({int(c) for c in cf.cik if cls[int(c)] in NONSW})
    rec['R2'] = dict(
        n_described=len(cls), n_core_registrants=int(cf.cik.nunique()),
        class_counts_core_registrants={k: int(v) for k, v in pd.Series([cls[int(c)] for c in cf.cik.unique()]).value_counts().items()},
        non_software={firm_names[c]: cls[c] for c in ns_firms},
        hits_non_software={firm_names[c]: hits_main[c] for c in ns_firms},
        non_software_firm_years_core_v2=int(cf.business_class.isin(NONSW).sum()),
        excluded_firm_years=int(len(ex2)), excluded_firms=int(ex2.cik.nunique()),
        excluded_by_period={k: int(v) for k, v in ex2.groupby('period').size().items()},
        excluded={n: sorted(int(y) for y in g_.year) for n, g_ in ex2.groupby('name')},
        named_classes={firm_names[c]: cls[c] for c in sorted(PANEL_NAMED) if c in firm_names},
        hits_named={firm_names[c]: hits_main[c] for c in sorted(PANEL_NAMED) if c in firm_names},
        sources=dict(named='data/v3_inputs/business_descriptions_named.json (29 Oct 2026)',
                     others='data/v3_inputs/raw/business_descriptions_raw_2026-11-03.json (3 Nov 2026)',
                     merged='data/v3_inputs/business_descriptions.json (code/audit/r2_descriptions.py)'),
        note='rule and keyword lists as defined before any description was read; firm-years excluded by R1 or R3 are '
             'counted under that rule')
if len(readers) == 2:                                      # R2 sensitivity: two independent readings (software vs not)
    ids = sorted({int(c) for c in cf.cik})
    ns_r = {rd: {c for c in ids if readers[rd][c] != 'software'} for rd in readers}
    n_, agree = len(ids), sum((c in ns_r['a']) == (c in ns_r['b']) for c in ids)
    pa, pb = len(ns_r['a']) / n_, len(ns_r['b']) / n_
    po, pe = agree / n_, pa * pb + (1 - pa) * (1 - pb)
    both, either = ns_r['a'] & ns_r['b'], ns_r['a'] | ns_r['b']
    cls_ns = {c for c in ids if cls.get(c) in NONSW}
    rec['R2_readers'] = dict(
        n_firms=n_, agree=int(agree), p_observed=po, p_expected=pe, kappa=(po - pe) / (1 - pe),
        non_software=dict(a=len(ns_r['a']), b=len(ns_r['b']), both=len(both), either=len(either)),
        class_counts={rd: {k: int(v) for k, v in pd.Series([readers[rd][c] for c in ids]).value_counts().items()} for rd in readers},
        v3_firm_years_dropped=dict(both=int(v3.cik.isin(both).sum()), either=int(v3.cik.isin(either).sum())),
        v3_firms_dropped=dict(both=int(v3[v3.cik.isin(both)].cik.nunique()), either=int(v3[v3.cik.isin(either)].cik.nunique())),
        both_firms=sorted(firm_names[c] for c in both), either_only_one=sorted(firm_names[c] for c in either - both),
        classifier_non_software=dict(n=len(cls_ns), also_a=len(cls_ns & ns_r['a']), also_b=len(cls_ns & ns_r['b']),
                                     also_both=len(cls_ns & both), also_either=len(cls_ns & either),
                                     software_for_a=sorted(firm_names[c] for c in cls_ns - ns_r['a']),
                                     software_for_b=sorted(firm_names[c] for c in cls_ns - ns_r['b'])),
        files=['data/v3_inputs/business_class_reader_a.csv', 'data/v3_inputs/business_class_reader_b.csv'],
        note='kappa: Cohen, software against the four other classes, over the core registrants; the sensitivities drop, '
             'from the main sample, the firms both readers (or either reader) class as not software')
if csw:
    v3c = v3[v3.cap_sw_source == 'filing_cash_flow_statement']
    cfc = cf[cf.cap_sw_source == 'filing_cash_flow_statement']
    box = cf[(cf.cik == 1372612) & (cf.fy_end == '2024-01-31')].iloc[0]
    assert box.cap_sw == 16561000 and box.cap_sw_xbrl == 0 and box.cap_sw_source == 'filing_cash_flow_statement'
    _dm = (v3c.m_fcf_sbc - (v3c.ocf - v3c.capex_ppe - v3c.cap_sw_xbrl - v3c.sbc) / v3c.rev).dropna()
    rec['capsw'] = dict(
        source='data/v3_inputs/capitalized_software_filings.json (code/audit/capsw_scan_parse.py; cash-flow statements read 3 Nov 2026)',
        n_filing_values=N_CSW, n_firms=len(csw), panel_all=int(csw_hit_all.sum()), core_v2=int(len(cfc)),
        core_v2_firms=int(cfc.cik.nunique()), v3=int(len(v3c)), v3_firms=int(v3c.cik.nunique()),
        v3_by_period={k: int(v) for k, v in v3c.groupby('period').size().items()},
        v3_share_of_revenue=dict(median=float((v3c.cap_sw / v3c.rev).median()), max=float((v3c.cap_sw / v3c.rev).max())),
        v3_cash_margin_change=dict(median=float(_dm.median()), min=float(_dm.min())),
        box_fy2023=dict(fy_end=box.fy_end, accn=box.accn, cap_sw=float(box.cap_sw), cap_sw_xbrl=float(box.cap_sw_xbrl)))
# (b) cash-score basis: elements available locally for a before-interest-and-tax variant
CF_ELEMS = ['InterestPaid', 'InterestPaidNet', 'IncomeTaxesPaid', 'IncomeTaxesPaidNet']
frames_concepts = set()
for f_ in ['frames_universe.json', 'frames_extra.json']:
    frames_concepts |= {k.split('|')[0] for k in json.load(open(f'{BASE}/data/{f_}'))}
src_v2 = open(f'{BASE}/code/build_panel_v2.py').read()
rec['cash_score_basis'] = dict(
    operating_cash_flow_elements=['NetCashProvidedByUsedInOperatingActivitiesContinuingOperations', 'NetCashProvidedByUsedInOperatingActivities'],
    reading='US GAAP classifies interest paid and income taxes paid as operating cash outflows (ASC 230-10-45-17(c), (d)), so '
            'operating cash flow, and the cash score built on it, is after interest paid and cash taxes',
    elements_in_extract={e: (e in src_v2) for e in CF_ELEMS}, elements_in_frames={e: (e in frames_concepts) for e in CF_ELEMS},
    coverage_core='0 firm-years: none of the four elements is in data/ (extract, frames or panels); a re-fetch is needed')
if b5:
    has = v3.interest_paid.notna()
    rec['cash_score_basis'].update(
        retrieved='data/v3_inputs/cash_interest_taxes.json (SEC frames, 29 Oct 2026; latest filed values, not first reported)',
        coverage_core=f'{int(has.sum())} of {len(v3)} v3 core firm-years report at least one of the four elements',
        coverage_v3=dict(any_element=int(has.sum()), interest_element=int((v3.interest_paid_element != '').sum()),
                         taxes_element=int((v3.income_taxes_paid_element != '').sum()),
                         both=int(((v3.interest_paid_element != '') & (v3.income_taxes_paid_element != '')).sum()),
                         interest_net_element=int((v3.interest_paid_element == 'InterestPaidNet').sum()),
                         taxes_net_element=int((v3.income_taxes_paid_element == 'IncomeTaxesPaidNet').sum())),
        rule='InterestPaidNet, else InterestPaid; IncomeTaxesPaidNet, else IncomeTaxesPaid; a missing element is zero when the firm-year reports any of the four')
# (d) G&A floor of the a_min band (code/data_part2/08_params.py definition: FY2023-25 firm means of G&A / revenue, by
#     current revenue, 0 < share < 2)
def ga_floor(df, revcol='rev'):
    d = df[(df.year >= 2023) & (df.year <= 2025) & (df.rev > 0)].assign(ga_s=lambda x: x.ga / x.rev)
    out = {}
    for lo, hi, lab in [(1e9, 1e10, 'rev_1b_10b'), (1e10, 1e15, 'rev_over_10b')]:
        f_ = d[(d[revcol] >= lo) & (d[revcol] < hi)].groupby('cik').ga_s.mean().dropna()
        f_ = f_[(f_ > 0) & (f_ < 2)]
        out[lab] = dict(n_firms=int(len(f_)), p5=float(f_.quantile(.05)), p10=float(f_.quantile(.10)), median=float(f_.median()))
    return out
rec['ga_floor'] = {'as_in_08_params (panel_v2_all, SIC 7370-7374, all revenue)': ga_floor(P),
                   'panel_v2_all, SIC 7372 only': ga_floor(P[P.sic == 7372]),
                   'core analysis sample v2 (data/panel.csv)': ga_floor(core),
                   'core analysis sample v2, by prior-year revenue': ga_floor(core, 'rev_lag'),
                   'core analysis sample v3 (data/panel_v3.csv)': ga_floor(v3)}
# (e) counts of non-first-reported firm-years under the definitions in the reviews
lagd = (pd.to_datetime(cf.filed) - pd.to_datetime(cf.fy_end)).dt.days
fye = pd.to_datetime(cf.fy_end)
late_acc = (cf.accn.str.split('-').str[1].astype(int) + 2000) > np.where(fye.dt.month <= 9, fye.dt.year, fye.dt.year + 1)
first_core = cf.year == cf.groupby('cik').year.transform('min')
rec['backfill_counts'] = {
    'R1 (source filing reports a later own period)': int(cf.backfill.sum()),
    'filed more than 400 days after fiscal year-end (finance referee)': int((lagd > 400).sum()),
    'accession year later than the normal filing year (IM T1)': int(late_acc.sum()),
    'IM T1 restricted to first core year': int((late_acc & first_core).sum()),
    'R1 restricted to first core year': int((cf.backfill & first_core).sum()),
    'R1 but filed within 400 days': lst(cf[cf.backfill & (lagd <= 400)]),
    'IM T1 but not R1 (late original filing)': lst(cf[late_acc & ~cf.backfill]),
    'R1 but not first core year': lst(cf[cf.backfill & ~first_core])}
json.dump(rec, open(f'{BASE}/notes/panel_v3_build.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in rec.items() if k not in ('R1',)}, indent=1)[:4000])
print('R1', {k: v for k, v in rec['R1'].items() if k != 'firm_years'})
