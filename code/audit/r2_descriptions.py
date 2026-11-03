#!/usr/bin/env python3
"""Rule R2 input: the business description of every core registrant, as data/v3_inputs/business_descriptions.json.

Sources (both retrieved from sec.gov in the built-in browser of the author's desktop application; provenance in
data/v3_inputs/README_retrieval.md, sections 2 and 6):
  data/v3_inputs/business_descriptions_named.json             the 16 firms the review panels named (29 Oct 2026)
  data/v3_inputs/raw/business_descriptions_raw_2026-11-03.json the other core registrants (3 Nov 2026), with form,
                                                               accession number, document, period, filing date, URL and,
                                                               where a fallback heading rule was used, `rule`
Both apply the same rule: the latest annual report listed in data.sec.gov submissions; the first ~4,000 characters of
Item 1 (Business) of a 10-K, Item 4.B (Business Overview) of a 20-F, or the business section of a 40-F's Annual
Information Form. The named firms keep their 29 Oct text; the 3 Nov file supplies the rest. The two sets are disjoint and
together cover every registrant of the v2 core sample (data/panel.csv), which is the frame of build_panel_v3.py.

Output: data/v3_inputs/business_descriptions.json ({cik: text}, CIKs in ascending order), which build_panel_v3.py reads to
apply R2 to the main sample. The keyword classifier and its lists are in build_panel_v3.py and are not changed here.
Run   : python3 code/audit/r2_descriptions.py
"""
import json
import os
import sys
from collections import Counter

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE, 'code'))
from exclusions import is_excluded  # noqa: E402

INP = os.path.join(BASE, 'data', 'v3_inputs')
named = json.load(open(os.path.join(INP, 'business_descriptions_named.json')))
raw = json.load(open(os.path.join(INP, 'raw', 'business_descriptions_raw_2026-11-03.json')))
core = pd.read_csv(os.path.join(BASE, 'data', 'panel.csv'))
want = {int(c) for c in core.cik if not is_excluded(c)}

assert not set(named) & set(raw), 'a named firm is also in the 3 Nov file'
assert all(str(int(k)) == k for k in list(named) + list(raw)), 'CIK keys must be decimal strings without leading zeros'
assert not any(is_excluded(k) for k in list(named) + list(raw))
have = {int(k) for k in named} | {int(k) for k in raw}
assert have == want, f'coverage: missing {sorted(want - have)}, extra {sorted(have - want)}'
assert all(str(r['cik']) == k and r['text'].strip() for k, r in raw.items())

out = {str(c): (named[str(c)] if str(c) in named else raw[str(c)]['text']) for c in sorted(have)}
json.dump(out, open(os.path.join(INP, 'business_descriptions.json'), 'w'), indent=1, ensure_ascii=False)
print(f"wrote data/v3_inputs/business_descriptions.json: {len(out)} registrants ({len(named)} from the named file of "
      f"29 Oct, {len(raw)} from the file of 3 Nov), every registrant of the v2 core sample")
print('3 Nov file, forms:', dict(Counter(r['form'] for r in raw.values())),
      '| filing years:', f"{min(r['filed'] for r in raw.values())[:4]}-{max(r['filed'] for r in raw.values())[:4]}",
      '| text length:', f"{min(len(r['text']) for r in raw.values())}-{max(len(r['text']) for r in raw.values())} characters")
print('fallback heading rules:', {k: r['rule'] for k, r in raw.items() if r.get('rule')})
