#!/usr/bin/env python3
"""Data audit (round 3), follow-up to test 1: capitalized software that the panel misses.

The panel's capitalized software is PaymentsForSoftware + PaymentsToDevelopSoftware from SEC companyfacts (us-gaap only),
so a filer that tags it with a company-specific element shows 0. For every panel_v3 firm-year with cap_sw = 0 and capex
reported (1,213), the cash-flow statement of the filing the panel used was read from its XBRL rendering (FilingSummary.xml
and the statement's R page) on sec.gov in the browser, 3 Nov 2026 (notes/data_audit/capsw_cashflow_rows_2026-11-03.json).
This script keeps the investing-section lines that are capitalized software outflows, reads the fiscal-year value (first
numeric column, scaled by the page's unit), and flags a possible double count when the panel's capex already came from
PaymentsToAcquireProductiveAssets (which can include software).
Output: notes/data_audit/capsw_missed.csv and a summary.
"""
import json, re
import pandas as pd

D = json.load(open('notes/data_audit/capsw_cashflow_rows_2026-11-03.json'))
P = pd.read_csv('data/panel_v3.csv')
E = json.load(open('data/companyfacts_extract.json'))
KEEP = re.compile(r'software')
CAP = re.compile(r'capitali[sz]|additions? to|development of|internal[- ]use|internally developed|purchases? of (computer )?software|software development costs$|software costs$')
DROP = re.compile(r'amortiz|impair|stock|share[- ]based|compensation|interest|contract|lease|definition|licen|intangible|property|equipment|acquisition|proceeds|sale|gain|loss|write|depreciat|deferred|distribution rights|change in|increase|decrease|accrued|payable|non-?cash|supplemental')


def scale(head):
    h = ' '.join(head).lower()
    return 1e6 if 'in millions' in h else (1e3 if 'in thousands' in h else 1.0)


def first_num(row):
    for cell in row.split(' | ')[1:]:
        c = cell.replace('$', '').replace(' ', '')
        m = re.fullmatch(r'\(?(-?[\d,]+(\.\d+)?)\)?', c)
        if m and m.group(1).replace(',', '').replace('.', '').lstrip('-').isdigit():
            v = float(m.group(1).replace(',', ''))
            return -abs(v) if c.startswith('(') or c.startswith('-') else v
    return None


rows = []
for r in P[(P.cap_sw == 0) & P.capex_ppe.notna()].itertuples():
    nd = r.accn.replace('-', '')
    rec = D.get(nd, {})
    if rec.get('error'):
        rows.append(dict(cik=r.cik, year=r.year, accn=r.accn, status='not read: ' + rec['error'])); continue
    sc = scale(rec.get('head', []))
    hits = []
    for h in rec.get('hits', []):
        lab = h.split(' | ')[0].strip().lower()
        if KEEP.search(lab) and CAP.search(lab) and not DROP.search(lab):
            v = first_num(h)
            if v is not None and v != 0:
                hits.append((lab, v * sc))
    if not hits:
        continue
    lab, v = hits[0]
    # which capex element did the panel use? (concept indices of code/fetch_companyfacts.py: 8 PP&E, 9 productive assets)
    f = E[str(r.cik)]
    acc_idx = [i for i, a in enumerate(f['acc']) if a[0] == r.accn]
    used = sorted({c for c, a, s, e, val in f['f'] if a in acc_idx and c in (8, 9, 10, 11) and abs(val - r.capex_ppe) < 1})
    rows.append(dict(cik=r.cik, year=r.year, accn=r.accn, name=r.name, label=lab, cap_sw_filing=abs(v), outflow=v < 0,
                     n_lines=len(hits), rev=r.rev, pct_rev=100 * abs(v) / r.rev, capex_elements=str(used),
                     double_count_risk=(9 in used and 8 not in used), period=r.period, R_fcf_sbc=r.R_fcf_sbc,
                     status='missed'))
M = pd.DataFrame(rows)
M.to_csv('notes/data_audit/capsw_missed.csv', index=False)
miss = M[M.status == 'missed']
print('firm-years checked', int(((P.cap_sw == 0) & P.capex_ppe.notna()).sum()), '| not read', int((M.status != 'missed').sum()),
      '| with a missed capitalized-software line', len(miss), '| firms', miss.cik.nunique())
print('share of revenue: median %.2f%%, p90 %.2f%%, max %.2f%%' % (miss.pct_rev.median(), miss.pct_rev.quantile(0.9), miss.pct_rev.max()))
print('outflow sign', miss.outflow.value_counts().to_dict(), '| possible double count (capex from ProductiveAssets):', int(miss.double_count_risk.sum()))
print(miss.groupby('period').size().to_dict())
print(miss.label.value_counts().head(15).to_string())
