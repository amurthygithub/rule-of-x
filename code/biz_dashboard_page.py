#!/usr/bin/env python3
"""Build the page of the business dashboard from its template (3 November 2026).

  notes/mc_results_2026-11-03_1m/dashboard/index.src.html  ->  .../dashboard/index.html

In the template every number of the text is written {{key}}, a key of facts.csv (code/biz_dashboard_data.py). Each
becomes an element the page fills from that file, so no number is typed into the page:
  <b>{{key}}</b>  ->  <b data-draw="f" data-source="facts" data-field="display" data-where="key=key">—</b>
  {{key}}         ->  the same as a <span> (years and references are never bold)
The script stops if a key is missing from facts.csv, and lists any digit left in the page's visible text outside the
names it allows (Rule of 40, 100 and 1000; Paper 1).  Run from anywhere:  python3 code/biz_dashboard_page.py
"""
import csv
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(BASE, 'notes', 'mc_results_2026-11-03_1m', 'dashboard')
src = open(os.path.join(DIR, 'index.src.html'), encoding='utf-8').read()
facts = {r['key']: r for r in csv.DictReader(open(os.path.join(DIR, 'facts.csv'), encoding='utf-8'))}
used = set(re.findall(r'\{\{([a-z0-9_]+)\}\}', src))
missing = sorted(used - facts.keys())
if missing:
    sys.exit('keys missing from facts.csv: ' + ', '.join(missing))


def mark(tag, key, cls=''):
    c = f' class="{cls}"' if cls else ''
    return f'<{tag}{c} data-draw="f" data-source="facts" data-field="display" data-where="key={key}">—</{tag}>'


plain = lambda k: k.startswith(('y', 'ref_'))
out = re.sub(r'<b>\{\{([a-z0-9_]+)\}\}</b>', lambda m: mark('span' if plain(m.group(1)) else 'b', m.group(1)), src)
out = re.sub(r'<span>\{\{(ref_[a-z0-9_]+)\}\}</span>', lambda m: mark('span', m.group(1), 'st-ref'), out)
out = re.sub(r'\{\{([a-z0-9_]+)\}\}', lambda m: mark('span', m.group(1)), out)
assert '{{' not in out
open(os.path.join(DIR, 'index.html'), 'w', encoding='utf-8').write(out)

# digits left in visible text (outside style, script, tags and the filled elements)
vis = re.sub(r'<style>.*?</style>|<script>.*?</script>', ' ', out, flags=re.S)
vis = re.sub(r'<(b|span)[^>]*data-draw="f"[^>]*>—</\1>', ' ', vis)
vis = re.sub(r'<[^>]+>', ' ', vis)
vis = re.sub(r'Rule(?: |-)of(?: |-)(?:1000|100|40)|Paper 1|notes/mc_results_2026-11-03_1m/', ' ', vis)
left = sorted(set(re.findall(r'[^\s]*\d[^\s]*', vis)))
print(f'index.html: {len(out):,} bytes, {len(used)} fact keys, {out.count("data-draw=\"f\"")} filled elements')
print('digits left in text:', left if left else 'none')
