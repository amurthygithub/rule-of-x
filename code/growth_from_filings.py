"""Filing-consistent revenue growth.

The XBRL frames interface returns, for each calendar year, the most recently filed fact. When a firm restates
prior years (for example after classifying a divested business as discontinued operations), year t and year t-1
can come from different filings on different bases, producing spurious growth. Here growth for the fiscal year
ending on date E_t is computed from a single filing that reports both E_t and the prior fiscal year: the earliest
annual filing (10-K, 10-K/A, 10-KT, 20-F, 20-F/A, 40-F) that contains both, i.e. growth as first reported on a
consistent basis.

Input : data/companyconcept_revenue.json  {"cik|concept_index": [[accn, end, val, filed, form], ...]}
Output: data/growth_filing.csv            cik, fy_end, g_filing, concept_index, accn
"""
import json
import os
import sys
from collections import defaultdict
from datetime import date
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exclusions import drop_excluded, is_excluded  # noqa: E402  registrants excluded at the author's request

BASE = '/home/claude/paper'
raw = json.load(open(f'{BASE}/data/companyconcept_revenue.json'))
raw = {k: v for k, v in raw.items() if not is_excluded(k.split('|')[0])}
by_firm = defaultdict(dict)
for key, facts in raw.items():
    cik, ci = key.split('|')
    by_firm[int(cik)][int(ci)] = facts

def d(s):
    return date.fromisoformat(s)

panel = pd.read_csv(f'{BASE}/data/panel_all.csv', usecols=['cik', 'year', 'fy_end'])
panel = drop_excluded(panel[panel.fy_end.notna() & (panel.fy_end != '')])
rows = []
for cik, g in panel.groupby('cik'):
    concepts = by_firm.get(int(cik), {})
    if not concepts:
        continue
    for _, r in g.iterrows():
        Et = d(r.fy_end)
        found = None
        for ci in sorted(concepts):
            facts = concepts[ci]
            filings = defaultdict(dict)
            filed = {}
            for accn, end, val, fdate, form in facts:
                filings[accn][d(end)] = val
                filed[accn] = fdate
            cands = []
            for accn, ends in filings.items():
                if Et not in ends:
                    continue
                prev = [e for e in ends if 345 <= (Et - e).days <= 385]
                if prev and ends[prev[0]] and ends[prev[0]] > 0:
                    cands.append((filed[accn], accn, ends[Et] / ends[prev[0]] - 1))
            if cands:
                cands.sort()
                found = (ci, cands[0][1], cands[0][2])
                break
        if found:
            rows.append((int(cik), r.fy_end, found[2], found[0], found[1]))
out = pd.DataFrame(rows, columns=['cik', 'fy_end', 'g_filing', 'concept_index', 'accn'])
out.to_csv(f'{BASE}/data/growth_filing.csv', index=False)
print(len(out), 'firm-years with filing-consistent growth')
