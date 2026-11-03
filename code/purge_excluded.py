#!/usr/bin/env python3
"""Remove the registrants excluded in code/exclusions.py from the data files on disk, and check that none is left.

Each file is edited in its own structure: CSV rows (the physical lines of the excluded registrants are dropped and every
other byte is kept), JSON object keys and list entries (the file is re-serialized with the settings that reproduce the
original bytes exactly; the script stops if no setting does), one-CIK-per-line lists, the delta-encoded base-36 CIK
lists (the list is re-encoded without the registrant; the encoding is checked to reproduce the original first), the
hexadecimal CIK list of the growth fetch, the CIK list embedded in code/retrieval_browser.js, and the data members of
dist/replication_package.zip (each member rewritten in place with its original metadata). The registrants are
identified only by digest (code/exclusions.py), so this script names none.

Usage: python3 code/purge_excluded.py [--check] [--root DIR]
  --check  change nothing; print what would be removed and exit 1 if anything would be (also checks that the digest
           set in code/retrieval_browser.js equals EXCLUDED_CIK_SHA256)
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exclusions import EXCLUDED_CIK_SHA256, is_excluded  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B36 = '0123456789abcdefghijklmnopqrstuvwxyz'


# ------------------------------------------------------------------------------------------------- encodings
def to_b36(n):
    if n < 0:
        return '-' + to_b36(-n)
    s = ''
    while True:
        n, r = divmod(n, 36)
        s = B36[r] + s
        if n == 0:
            return s


def dec_delta(s):
    out, acc = [], 0
    for x in s.split('.'):
        acc += int(x, 36)
        out.append(acc)
    return out


def enc_delta(ciks):
    return '.'.join(to_b36(c - (ciks[i - 1] if i else 0)) for i, c in enumerate(ciks))


# ------------------------------------------------------------------------------------------------- handlers: text -> (text, n removed)
def h_csv(text, col='cik'):
    lines = text.splitlines(keepends=True)
    header = next(csv.reader([lines[0]]))
    i = header.index(col)
    out, n = [lines[0]], 0
    for ln in lines[1:]:
        if not ln.strip():
            out.append(ln)
            continue
        row = next(csv.reader([ln]))
        assert len(row) == len(header), 'a CSV record spans lines; line-based removal is not safe'
        if is_excluded(row[i]):
            n += 1
            continue
        out.append(ln)
    return ''.join(out), n


JSON_SETTINGS = [{}, {'indent': 0}, {'indent': 1}, {'indent': 2}, {'separators': (',', ':')}, {'ensure_ascii': False},
                 {'indent': 0, 'ensure_ascii': False}, {'indent': 1, 'ensure_ascii': False}, {'indent': 2, 'ensure_ascii': False}]


def _json_settings(obj, text):
    for kw in JSON_SETTINGS:
        s = json.dumps(obj, **kw)
        for tail in ('', '\n'):
            if s + tail == text:
                return kw, tail
    raise SystemExit('no JSON setting reproduces the original bytes; refusing to rewrite')


def _json(edit):
    def h(text):
        obj = json.loads(text)
        kw, tail = _json_settings(obj, text)
        n = edit(obj)
        return (json.dumps(obj, **kw) + tail if n else text), n
    return h


def _drop_keys(d, key=lambda k: k):
    bad = [k for k in d if is_excluded(key(k))]
    for k in bad:
        del d[k]
    return len(bad)


h_json_top = _json(lambda o: _drop_keys(o))                                              # {cik: ...}
h_json_pipe = _json(lambda o: _drop_keys(o, lambda k: k.split('|')[0]))                  # {"cik|concept": ...}
h_json_inner = _json(lambda o: sum(_drop_keys(v) for v in o.values()))                   # {"concept|year": {cik: ...}}


def _drop_rows(lst, idx):
    bad = [r for r in lst if is_excluded(r[idx])]
    lst[:] = [r for r in lst if not is_excluded(r[idx])]
    return len(bad)


h_json_rows1 = _json(lambda o: _drop_rows(o, 1))                                         # [[sic, cik, name, state], ...]


def h_lines(text):
    lines = text.splitlines(keepends=True)
    keep = [ln for ln in lines if not (ln.strip() and is_excluded(ln.strip()))]
    return ''.join(keep), len(lines) - len(keep)


def h_delta_b36(text):
    body = text.rstrip('\n')
    tail = text[len(body):]
    ciks = dec_delta(body)
    assert enc_delta(ciks) == body, 'delta encoding does not reproduce the original'
    keep = [c for c in ciks if not is_excluded(c)]
    n = len(ciks) - len(keep)
    return (enc_delta(keep) + tail if n else text), n


def h_hex_list(text):                                     # "hexcik:codes;hexcik:codes;..."
    body = text.rstrip('\n')
    tail = text[len(body):]
    items = body.split(';')
    keep = [x for x in items if not is_excluded(int(x.split(':')[0], 16))]
    n = len(items) - len(keep)
    return (';'.join(keep) + tail if n else text), n


JS_ENC = re.compile(r"(const enc=')([^']*)(')")


def h_js(text):
    m = JS_ENC.search(text)
    assert m, 'CIK list not found in the browser script'
    new, n = h_delta_b36(m.group(2))
    return (text[:m.start(2)] + new + text[m.end(2):] if n else text), n


def js_digests(text):
    m = re.search(r'const EXCLUDED_CIK_SHA256=new Set\(\[([^\]]*)\]\)', text)
    return None if m is None else set(re.findall(r"'([0-9a-f]{64})'", m.group(1)))


# ------------------------------------------------------------------------------------------------- files
DATA = {                                      # path relative to a data root -> handler
    'sic_universe.json': h_json_rows1,
    'frames_universe.json': h_json_inner,
    'frames_extra.json': h_json_inner,
    'companyfacts_ciks.txt': h_lines,
    'companyfacts_extract.json': h_json_top,
    'companyconcept_revenue.json': h_json_pipe,
    'growth_filing.csv': h_csv,
    'panel_all.csv': h_csv,
    'panel.csv': h_csv,
    'panel_broad.csv': h_csv,
    'panel_v2_all.csv': h_csv,
    'panel_v3_all.csv': h_csv,
    'panel_v3_core_full.csv': h_csv,
    'panel_v3.csv': h_csv,
    'cik_delta_b36.txt': h_delta_b36,
    'cf_fetch_list.txt': h_delta_b36,
    'growth_fetch_list.txt': h_hex_list,
    'v3_inputs/related_party.json': h_json_top,
    'v3_inputs/acquiree_revenue.json': h_json_top,
    'v3_inputs/listing_status.json': h_json_top,
    'v3_inputs/cash_interest_taxes.json': h_json_top,
    'v3_inputs/interest_income_deferred.json': h_json_top,
    'v3_inputs/business_descriptions_named.json': h_json_top,
    'v3_inputs/raw/business_descriptions_raw_2026-10-29.json': h_json_top,
    'v3_inputs/captive_verified.csv': h_csv,
}
CODE = {'retrieval_browser.js': h_js}


def targets(root):
    for base, table in [('data', DATA), ('dist/replication/data', DATA), ('code', CODE), ('dist/replication/code', CODE)]:
        for rel, h in table.items():
            p = os.path.join(root, base, rel)
            if os.path.exists(p):
                yield os.path.join(base, rel), p, h


def handler_for_member(name):
    parts = name.split('/')
    if len(parts) >= 3 and parts[-2] in ('data', 'code'):
        return (DATA if parts[-2] == 'data' else CODE).get(parts[-1])
    return None


def purge_zip(path, check):
    with zipfile.ZipFile(path) as zf:
        members = [(zi, zf.read(zi)) for zi in zf.infolist()]
    out, total, per = [], 0, {}
    for zi, data in members:
        h = handler_for_member(zi.filename)
        if h is not None:
            new, n = h(data.decode('utf-8'))
            if n:
                per[zi.filename] = n
                total += n
                data = new.encode('utf-8')
        out.append((zi, data))
    if total and not check:
        tmp = path + '.tmp'
        with zipfile.ZipFile(tmp, 'w') as zf:
            for zi, data in out:
                zf.writestr(zi, data, compress_type=zi.compress_type)
        os.replace(tmp, path)
    return per


def purge_tree(root, check=False):
    """Remove the excluded registrants from every data file under root; returns {file: entries removed}."""
    removed = {}
    for rel, p, h in targets(root):
        text = open(p, encoding='utf-8', newline='').read()
        new, n = h(text)
        if n:
            removed[rel] = n
            if not check:
                with open(p, 'w', encoding='utf-8', newline='') as f:
                    f.write(new)
    z = os.path.join(root, 'dist', 'replication_package.zip')
    if os.path.exists(z):
        for m, n in purge_zip(z, check).items():
            removed[f'dist/replication_package.zip:{m}'] = n
    return removed


def js_mismatches(root):
    bad = []
    for rel in ('code/retrieval_browser.js', 'dist/replication/code/retrieval_browser.js'):
        p = os.path.join(root, rel)
        if os.path.exists(p) and js_digests(open(p, encoding='utf-8').read()) != set(EXCLUDED_CIK_SHA256):
            bad.append(rel)
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--root', default=ROOT)
    a = ap.parse_args()
    removed = purge_tree(a.root, a.check)
    for rel, n in removed.items():
        print(f'{rel}: {n} {"to remove" if a.check else "removed"}')
    bad_js = js_mismatches(a.root)
    for rel in bad_js:
        print(f'{rel}: digest set missing or different from code/exclusions.py')
    if not removed and not bad_js:
        print('no excluded registrant in the data files')
    if a.check and (removed or bad_js):
        sys.exit(1)


if __name__ == '__main__':
    main()
