#!/usr/bin/env python3
"""Data audit (round 3), follow-up to test 1: capitalized software that the panel misses, and its correction.

The panel's capitalized software is PaymentsForSoftware + PaymentsToDevelopSoftware from SEC companyfacts (us-gaap only),
so a filer that tags it with a company-specific element shows 0. For every panel_v3 firm-year with cap_sw = 0 and capex
reported (1,213), the cash-flow statement of the filing the panel used was read from its XBRL rendering (FilingSummary.xml
and the statement's R page) on sec.gov in the browser, 3 Nov 2026 (notes/data_audit/capsw_cashflow_rows_2026-11-03.json).
This script keeps the investing-section lines that are capitalized software outflows, reads the fiscal-year value (first
numeric column, scaled by the page's unit), and flags a possible double count when the panel's capex already came from
PaymentsToAcquireProductiveAssets (which can include software).

Frame. The scan covered the v3 core sample as it stood on 3 Nov before rule R2 applied to the main sample (1,788 firm-years):
the v2 core firm-years (data/panel.csv, XBRL values) that rules R1 and R3 keep (data/panel_v3_core_full.csv). The values
are read from data/panel.csv, which build_panel_v3.py never writes, so the scan does not depend on the correction it feeds.

Correction (data/v3_inputs/capitalized_software_filings.json, read by build_panel_v3.py where the XBRL cap_sw is 0). A
candidate line is kept when
  - its value is an outflow (a negative number in the investing section; positive lines are non-cash add-backs);
  - its label is not a combined capital-expenditure line ("capital expenditures ...", "... and expenditures"), whose
    value would include the capex the panel already deducts; and
  - the panel's capex cannot contain it: the capex came from PaymentsToAcquirePropertyPlantAndEquipment, or, where it came
    from PaymentsToAcquireProductiveAssets (double_count_risk), the capex is smaller than the software line, so the two
    are separate lines of the statement (MedAssets 2010-11 and Coursera 2021-25). Set KEEP_SEPARATE_LINE = False to drop
    every double_count_risk row instead.
Outputs: notes/data_audit/capsw_missed.csv (every candidate), data/v3_inputs/capitalized_software_filings.json
         ({cik: {fy_end: {value, accn, label}}}, value in dollars), notes/data_audit/capsw_summary.json (counts) and a
         printed summary.
Run    : python3 code/audit/capsw_scan_parse.py   (from the repository root)
"""
import json, re
import pandas as pd

KEEP_SEPARATE_LINE = True
D = json.load(open('notes/data_audit/capsw_cashflow_rows_2026-11-03.json'))
_cf = pd.read_csv('data/panel_v3_core_full.csv', usecols=['cik', 'year', 'fy_end', 'v3_exclude'])
_scan = _cf[~_cf.v3_exclude.fillna('').str.startswith(('R1', 'R3'))]
P = pd.read_csv('data/panel.csv').merge(_scan[['cik', 'year', 'fy_end']], on=['cik', 'year', 'fy_end'], validate='one_to_one')
assert len(P) == 1788, len(P)
E = json.load(open('data/companyfacts_extract.json'))
KEEP = re.compile(r'software')
CAP = re.compile(r'capitali[sz]|additions? to|development of|internal[- ]use|internally developed|purchases? of (computer )?software|software development costs$|software costs$')
DROP = re.compile(r'amortiz|impair|stock|share[- ]based|compensation|interest|contract|lease|definition|licen|intangible|property|equipment|acquisition|proceeds|sale|gain|loss|write|depreciat|deferred|distribution rights|change in|increase|decrease|accrued|payable|non-?cash|supplemental')
COMBINED = re.compile(r'capital expenditures|and expenditures')


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


scanned = P[(P.cap_sw == 0) & P.capex_ppe.notna()]
assert len(scanned) == len(D) == 1213, (len(scanned), len(D))
rows = []
for r in scanned.itertuples():
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
print('firm-years checked', len(scanned), '| not read', int((M.status != 'missed').sum()),
      '| with a missed capitalized-software line', len(miss), '| firms', miss.cik.nunique())
print('share of revenue: median %.2f%%, p90 %.2f%%, max %.2f%%' % (miss.pct_rev.median(), miss.pct_rev.quantile(0.9), miss.pct_rev.max()))
print('outflow sign', miss.outflow.value_counts().to_dict(), '| possible double count (capex from ProductiveAssets):', int(miss.double_count_risk.sum()))
print(miss.groupby('period').size().to_dict())
print(miss.label.value_counts().head(15).to_string())

# ---- the correction: rows kept for data/v3_inputs/capitalized_software_filings.json
fy = P.set_index(['cik', 'year']).fy_end
capex = P.set_index(['cik', 'year']).capex_ppe
miss = miss.assign(fy_end=[fy[(c, y)] for c, y in zip(miss.cik, miss.year)],
                   capex_ppe=[capex[(c, y)] for c, y in zip(miss.cik, miss.year)])
comb = miss.label.str.contains(COMBINED)
dcr = miss.double_count_risk.astype(bool)
separate = dcr & (miss.capex_ppe < miss.cap_sw_filing)
keep = miss.outflow.astype(bool) & ~comb & (~dcr | (separate if KEEP_SEPARATE_LINE else False))
K = miss[keep]
out = {}
for r in K.sort_values(['cik', 'fy_end']).itertuples():
    v = float(r.cap_sw_filing)
    out.setdefault(str(int(r.cik)), {})[r.fy_end] = dict(value=int(v) if v.is_integer() else v, accn=r.accn, label=r.label)
json.dump(out, open('data/v3_inputs/capitalized_software_filings.json', 'w'), indent=1)
S = dict(frame='data/panel.csv rows kept by rules R1 and R3 (the v3 core sample of 3 Nov before R2: 1,788 firm-years)',
         n_frame=int(len(P)), n_scanned=int(len(scanned)), n_not_read=int((M.status != 'missed').sum()),
         n_candidates=int(len(miss)), n_candidate_firms=int(miss.cik.nunique()),
         dropped=dict(not_outflow=int((~miss.outflow.astype(bool)).sum()),
                      combined_capex_line=int((miss.outflow.astype(bool) & comb).sum()),
                      capex_may_contain_line=int((miss.outflow.astype(bool) & ~comb & dcr & ~(separate if KEEP_SEPARATE_LINE else False)).sum())),
         kept_separate_line_productive_assets=int((keep & dcr).sum()),
         n_kept=int(len(K)), n_kept_firms=int(K.cik.nunique()), kept_by_period={str(k): int(v) for k, v in K.groupby('period').size().items()},
         kept_pct_rev=dict(median=float(K.pct_rev.median()), p90=float(K.pct_rev.quantile(0.9)), max=float(K.pct_rev.max())),
         keep_separate_line=KEEP_SEPARATE_LINE)
json.dump(S, open('notes/data_audit/capsw_summary.json', 'w'), indent=1)
print(f"\nkept for data/v3_inputs/capitalized_software_filings.json: {S['n_kept']} firm-years of {S['n_kept_firms']} firms "
      f"(dropped: {S['dropped']}; kept with capex from ProductiveAssets smaller than the software line: "
      f"{S['kept_separate_line_productive_assets']}); share of revenue median {S['kept_pct_rev']['median']:.2f}%")
