#!/usr/bin/env python3
"""Data audit (round 3, test 1): compare panel_v3 values with the face financial statements of the filing the panel used.

Inputs : notes/data_audit/sample.csv (seeded stratified sample, notes/data_audit/sample_design.json);
         notes/data_audit/filing_statements_raw.json (statement tables read from each filing on sec.gov in the browser,
         3 November 2026; table rows as text, cells joined by ' | ').
Output : notes/data_audit/compare.csv, printed summary. A value matches when a number in the statement row of that
         line item equals the panel value (in dollars) to within 0.5 of the statement's last printed digit at scale 1,
         1e3 or 1e6; the column of the match is recorded (0 = first numeric column).
Run    : python3 code/audit/data_audit_compare.py
"""
import json, re, sys
import pandas as pd

S = pd.read_csv('notes/data_audit/sample.csv')
R = json.load(open('notes/data_audit/filing_statements_raw.json'))
ITEMS = {  # panel column: (statement, row-label regex, sign convention of the panel)
    'rev': ('is', r'^(total )?(net )?(revenues?|net sales|sales|total revenues?)( ,? ?net)?( \(note \d+\))?\b(?!.*(cost|deferred))', 1),
    'op_inc': ('is', r'(income|loss|profit)( \(loss\))?( \(income\))? from operations|operating (income|loss|profit)( \(loss\))?|^(loss|income) from operations', 1),
    'sm': ('is', r'^(sales and marketing|selling and marketing|marketing and sales|selling(,)? general|sales, marketing)', 1),
    'ocf': ('cf', r'net cash (provided by|used in|from|\(used in\)|generated)( \(used in\))?( \(used for\))?( operating activities| by operating activities| operating)', 1),
    'capex_ppe': ('cf', r'(purchases?|acquisitions?|additions?|investment) (of|to|in) (property|premises|fixed assets|equipment|plant)|capital expenditures|purchase of property', -1),
    'sbc': ('cf', r'(stock|share|equity)[- ]based compensation|stock compensation|share[- ]based payment', 1),
}
NUM = re.compile(r'\(?-?\$?\s?\d[\d,]*(\.\d+)?\)?')


def nums(row):
    """Numeric cells of a statement row as (value, decimals printed)."""
    out = []
    for cell in row.split(' | ')[1:]:
        c = cell.replace('$', '').replace(' ', '').replace('—', '').replace('–', '')
        m = re.fullmatch(r'\(?(-?\d[\d,]*(\.(\d+))?)\)?', c)
        if m:
            v = float(m.group(1).replace(',', ''))
            out.append((-v if c.startswith('(') or c.startswith('-') else v, len(m.group(3) or '')))
    return out


def header_years(t):
    """Years of the column headers: the first row with at least two 4-digit years (19xx/20xx)."""
    for row in t['rows'][:8]:
        ys = re.findall(r'\b(19\d\d|20\d\d)\b', row)
        if len(ys) >= 2:
            return [int(y) for y in ys]
    return None


def rows_of(rec, kind):
    for p in rec.get('parts', []):
        for t in p.get(kind, []):
            yield t
rows = []
for s in S.itertuples():
    rec = R[s.accn]
    for col, (kind, rx, sgn) in ITEMS.items():
        pv = getattr(s, col)
        res = dict(accn=s.accn, cik=s.cik, year=s.year, fy_end=s.fy_end, form=s.form, stratum=s.stratum, item=col, panel=pv,
                   found=None, col=None, scale=None, label=None, col_year=None, header_years=None, status=None)
        if pd.isna(pv):
            res['status'] = 'panel NaN'; rows.append(res); continue
        best = None
        for ti, t in enumerate(rows_of(rec, kind)):
            for row in t['rows']:
                label = row.split(' | ')[0].lower().strip()
                if not re.search(rx, label):
                    continue
                vals = nums(row)
                for j, (v, dec) in enumerate(vals):
                    for sc in (1, 1e3, 1e6):
                        tol = 0.5 * 10 ** (-dec) * sc + 1e-6
                        if abs(abs(v * sc) - abs(pv)) <= tol:
                            ys = header_years(t)
                            yr = ys[j] if ys and len(ys) == len(vals) else None
                            key = (ti, j)
                            if best is None or key < best[0]:
                                best = (key, v, sc, label, yr, ys)
        if 'xbrl_instance' in rec and best is None:
            res['status'] = 'see XBRL instance'
        if best:
            fy = int(str(s.fy_end)[:4])
            yr = best[4]
            st = ('match, fiscal-year column' if yr == fy else ('match, OTHER YEAR column' if yr is not None else
                  ('match, first column' if best[0][1] == 0 else 'match, column year not determined')))
            res.update(found=best[1], col=best[0][1], scale=best[2], label=best[3][:60], col_year=yr,
                       header_years=str(best[5]), status=st)
        elif res['status'] is None:
            res['status'] = 'no match'
        rows.append(res)
C = pd.DataFrame(rows)
C.to_csv('notes/data_audit/compare.csv', index=False)
print(C.status.value_counts().to_string())
print(C[~C.status.isin(['match, fiscal-year column', 'match, first column'])][['accn', 'year', 'fy_end', 'form', 'item', 'panel', 'status', 'found', 'col', 'header_years', 'label']].to_string())

# ---- Manual resolution of the items the label patterns did not match (each read in the statement rows printed by
# this script's companion inspection, 3 Nov 2026); status 'match' means the panel value is the filing's number.
MANUAL = {
    ('0001193125-15-121530', 'ocf'): ('match', 'continuing-operations line "Net cash (used in) provided by operating activities from continuing operations" (13,344); the panel uses continuing operations where reported'),
    ('0001628280-17-001754', 'ocf'): ('match', '"Net cash (used in) provided by operating activities" 23,131 (label pattern miss)'),
    ('0001564590-18-005797', 'ocf'): ('match', '"Net cash and cash equivalents used in operating activities" (5,937) (label pattern miss)'),
    ('0001418100-21-000095', 'rev'): ('match', 'unlabeled total row under REVENUE: 2,973 (in millions)'),
    ('0000876167-25-000010', 'ocf'): ('match', '"Net cash flows from operating activities" 211,494 (label pattern miss)'),
    ('0001410578-23-000797', 'op_inc'): ('match', 'face income statement "Operating (loss)/income ... 10,065" (the tables first found were the VIE condensed schedule)'),
    ('0001410578-23-000797', 'ocf'): ('match', 'face cash-flow statement "Net cash (used in)/generated from operating activities ... 51,109"'),
    ('0000950170-24-029241', 'capex_ppe'): ('definition', 'panel 4,703 is the XBRL fact PaymentsToAcquirePropertyPlantAndEquipment (gross) of this filing; the face statement shows purchases net of sale proceeds, (1,843); 0.28% of revenue'),
    ('0000860731-19-000009', 'sm'): ('match (missing in filing)', 'the statement reports only selling, general and administrative expenses; no separate S&M line'),
    ('0001418100-21-000095', 'sm'): ('match (missing in filing)', 'the statement reports only selling, general and administrative; no separate S&M line'),
    ('0000950170-24-023077', 'capex_ppe'): ('missing in panel', 'the statement reports "Purchases of equipment" (2,254); no us-gaap capex element in companyfacts; the firm-year is excluded from the cash basis (capex_missing)'),
}
XBRL_INSTANCE = {'0001104659-14-026957': 'the 40-F carries no financial-statement exhibit; all six values equal the facts of the XBRL instance filed with it (dsgx-20140131.xml)'}
C['resolved'] = C.status
C['evidence'] = ''
for i, r in C.iterrows():
    k = (r.accn, r['item'])
    if k in MANUAL:
        C.at[i, 'resolved'], C.at[i, 'evidence'] = MANUAL[k]
    elif r.status == 'see XBRL instance':
        C.at[i, 'resolved'], C.at[i, 'evidence'] = 'match (XBRL instance)', XBRL_INSTANCE[r.accn]
    elif r.status.startswith('match'):
        C.at[i, 'resolved'] = 'match'
C.to_csv('notes/data_audit/compare.csv', index=False)
print('\nresolved:\n' + C.resolved.value_counts().to_string())
# capitalized software (enters free cash flow), read from the same cash-flow tables
CAPSW = [  # (accn, statement value in the filing's units x scale, panel cap_sw, status)
    ('0001514416-20-000027', 3544e3, 'match'), ('0001560327-21-000043', 6130e3, 'match'), ('0001558370-21-001638', 13255e3, 'match'),
    ('0001834494-23-000026', 8228e3, 'match'), ('0000950170-24-029241', 16561e3, 'missed'), ('0001640147-25-000052', 29433e3, 'match'),
    ('0001628280-26-011055', 65663e3, 'match'), ('0001564590-17-005637', 584e3, 'match'), ('0001178913-18-001044', 27936e3, 'match'),
    ('0001535527-20-000006', 7289e3, 'match'), ('0001178913-23-000966', 2998e3, 'match'), ('0001640147-23-000030', 24012e3, 'match'),
    ('0001562088-25-000042', 9024e3, 'missed (line combined with purchases of intangible assets)')]
K = pd.DataFrame(CAPSW, columns=['accn', 'filing_value', 'status']).merge(S[['accn', 'cik', 'year', 'stratum', 'rev']], on='accn')
K = K.merge(pd.read_csv('data/panel_v3.csv')[['cik', 'year', 'cap_sw']], on=['cik', 'year'])
K['miss_pct_rev'] = ((K.filing_value - K.cap_sw) / K.rev * 100).round(2)
assert ((K.status == 'match') == (abs(K.filing_value - K.cap_sw) < 1)).all()
K.to_csv('notes/data_audit/capitalized_software.csv', index=False)
print('\ncapitalized software:\n' + K[['accn', 'year', 'stratum', 'filing_value', 'cap_sw', 'status', 'miss_pct_rev']].to_string())
