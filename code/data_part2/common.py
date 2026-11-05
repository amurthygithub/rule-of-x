"""Shared paths and helpers for the Part II data build.

Scripts in this folder are run with `python3 -I` (isolated mode), so each script inserts this folder on sys.path
explicitly before importing this module. Raw inputs live in data/raw/<source>/ and are treated as untrusted data:
they are only parsed, never executed.
"""
import glob
import hashlib
import io
import json
import os
import re
import sys
import zipfile

import numpy as np
import pandas as pd

BASE = os.environ.get('PAPER_ROOT', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))   # repository root; PAPER_ROOT overrides
RAW = f'{BASE}/data/raw'
OUT = os.environ.get('PART2_OUT', f'{BASE}/data/tasks')     # override only for tests
NOTES = f'{BASE}/notes'
BUILD = f'{OUT}/_build'          # machine-readable build metadata (fits, coverage stats)
os.makedirs(OUT, exist_ok=True)
os.makedirs(BUILD, exist_ok=True)

GPTS = f'{RAW}/gpts_are_gpts/repo/data'
MSAI = f'{RAW}/ms_working_with_ai/repo'
METR = f'{RAW}/metr_eval_analysis/repo'
ONET_DIR = os.environ.get('PART2_ONET_DIR', f'{RAW}/onet_31_0')
OEWS_DIR = f'{RAW}/bls_oews_2025'
AEI_DIR = f'{RAW}/anthropic_aei'


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def norm(s):
    """Normalise a column header: lower case, alphanumerics only ('O*NET-SOC Code' and 'onetsoc_code' -> 'onetsoccode')."""
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def normcols(df):
    df = df.copy()
    df.columns = [norm(c) for c in df.columns]
    return df


def soc6(code):
    """O*NET-SOC 'NN-NNNN.NN' -> SOC 2018 detailed 'NN-NNNN'."""
    s = str(code).strip()
    return s[:7] if re.match(r'^\d\d-\d{4}', s) else None


def oews_onet_crosswalk(oews_codes, onet_codes):
    """Map OEWS occupation codes to O*NET-SOC codes.
    Rule 1: O*NET-SOC codes whose first 7 characters equal the OEWS code.
    Rule 2: the BLS O*NET-SOC to NEM crosswalk (bls_nem_crosswalk) for SOC 2018 codes O*NET does not use directly.
    Rule 3: for OEWS aggregate codes ending in 0 (for example 13-1020 = 13-1021 + 13-1022 + 13-1023) with no direct
            match, all O*NET-SOC codes sharing the first 6 characters.
    Returns dict oews_code -> sorted list of O*NET-SOC codes, and dict of the rule used."""
    by7, by6 = {}, {}
    for c in onet_codes:
        s7 = soc6(c)
        if s7 is None:
            continue
        by7.setdefault(s7, []).append(c)
        by6.setdefault(s7[:6], []).append(c)
    nem = bls_nem_crosswalk()
    by_nem = {}
    for c in onet_codes:
        if c in nem:
            by_nem.setdefault(nem[c], []).append(c)
    out, rule = {}, {}
    for o in oews_codes:
        if o in by7:
            out[o], rule[o] = sorted(by7[o]), 'exact'
        elif o in by_nem:
            out[o], rule[o] = sorted(by_nem[o]), 'bls_nem_crosswalk'
        elif o.endswith('0') and o[:6] in by6:
            out[o], rule[o] = sorted(by6[o[:6]]), 'aggregate'
    return out, rule


def bls_nem_crosswalk():
    """O*NET-SOC -> SOC 2018 (BLS National Employment Matrix code), from the BLS 'O*NET-SOC to NEM and OOH Coverage
    Crosswalk' (as of 9/6/2023), redistributed in the GPTs-are-GPTs repository. Rule 3 of oews_onet_crosswalk."""
    p = f'{GPTS}/nem-onet-to-soc-crosswalk.xlsx'
    if not os.path.exists(p):
        return {}
    x = pd.read_excel(p, header=4)
    return dict(zip(x['O*NET-SOC Code'].astype(str).str.strip(), x['NEM Code'].astype(str).str.strip()))


def read_sec_panel(name='panel_v2_all.csv', **kw):
    """An SEC XBRL panel of Part I (data/<name>) without the registrants excluded in code/exclusions.py
    (registrant excluded at the author's request)."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from exclusions import drop_excluded
    return drop_excluded(pd.read_csv(f'{BASE}/data/{name}', **kw)).reset_index(drop=True)


def write_csv(df, name, float_format='%.6g'):
    path = f'{OUT}/{name}'
    df.to_csv(path, index=False, encoding='utf-8', float_format=float_format)
    print(f'wrote {path}  rows={len(df)}')
    return path


def save_meta(name, obj):
    with open(f'{BUILD}/{name}.json', 'w') as f:
        json.dump(obj, f, indent=2, default=str)


def load_meta(name):
    p = f'{BUILD}/{name}.json'
    return json.load(open(p)) if os.path.exists(p) else None


# ---------------------------------------------------------------- O*NET 31.0 loader (CSV files or the Excel zip)
ONET_FILES = {
    'task_statements': ['task_statements.csv', 'Task Statements.xlsx'],
    'task_ratings': ['task_ratings.csv', 'Task Ratings.xlsx'],
    'task_categories': ['task_categories.csv', 'Task Categories.xlsx'],
    'tasks_to_dwas': ['tasks_to_dwas.csv', 'Tasks to DWAs.xlsx'],
    'gwas_to_iwas_to_dwas': ['gwas_to_iwas_to_dwas.csv', 'GWAs to IWAs to DWAs.xlsx'],
    'gwas_to_iwas': ['gwas_to_iwas.csv', 'GWAs to IWAs.xlsx'],
    'occupation_data': ['occupation_data.csv', 'Occupation Data.xlsx'],
    'content_model_reference': ['content_model_reference.csv', 'Content Model Reference.xlsx'],
    'work_context': ['work_context.csv', 'Work Context.xlsx'],
    'job_zones': ['job_zones.csv', 'Job Zones.xlsx'],
}


def _find_any(names, roots):
    for root in roots:
        for n in names:
            hits = glob.glob(f'{root}/**/{n}', recursive=True)
            if hits:
                return sorted(hits)[0]
    return None


def onet_available(required=('task_statements', 'task_ratings', 'tasks_to_dwas', 'gwas_to_iwas_to_dwas')):
    return all(onet_path(k) for k in required)


def onet_path(key):
    roots = [ONET_DIR] if 'PART2_ONET_DIR' in os.environ else [ONET_DIR, RAW]
    p = _find_any(ONET_FILES[key], roots)
    if p:
        return p
    zips = glob.glob(f'{ONET_DIR}/*.zip')
    for z in zips:
        with zipfile.ZipFile(z) as zf:
            for member in zf.namelist():
                if os.path.basename(member) in ONET_FILES[key]:
                    return f'{z}::{member}'
    return None


def read_onet(key):
    p = onet_path(key)
    if p is None:
        return None
    if '::' in p:
        z, member = p.split('::', 1)
        with zipfile.ZipFile(z) as zf:
            data = zf.read(member)
        if member.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(data))
        else:
            df = pd.read_csv(io.BytesIO(data), sep=None, engine='python')
    elif p.endswith('.xlsx'):
        df = pd.read_excel(p)
    else:
        with open(p, 'rb') as f:
            head = f.read(4096).decode('utf-8', 'replace')
        sep = '\t' if head.count('\t') > head.count(',') else ','
        df = pd.read_csv(p, sep=sep, encoding='utf-8-sig', low_memory=False)
    return normcols(df)


def pick(df, *cands):
    """Return the first column of df whose normalised name is in cands (also accepts partial matches)."""
    cols = list(df.columns)
    for c in cands:
        if c in cols:
            return c
    for c in cands:
        for col in cols:
            if c in col:
                return col
    raise KeyError(f'none of {cands} in {cols}')


def onet_hierarchy():
    """DWA -> IWA -> GWA table with titles: dwa_id, dwa_title, iwa_id, iwa_title, gwa_id, gwa_title.
    Handles both the text-file headers (DWA ID, DWA Title, IWA ID, ...) and the 31.0 SQL headers
    (dwa_element_id, dwa_element_name, iwa_element_id, gwa_element_id), taking IWA titles from gwas_to_iwas and GWA
    titles from content_model_reference when the hierarchy file lacks them."""
    h = read_onet('gwas_to_iwas_to_dwas')
    if h is None:
        return None
    h = h.rename(columns={pick(h, 'dwaelementid', 'dwaid'): 'dwa_id', pick(h, 'dwaelementname', 'dwatitle'): 'dwa_title',
                          pick(h, 'iwaelementid', 'iwaid'): 'iwa_id'})
    gcols = [c for c in h.columns if c in ('gwaelementid', 'elementid', 'gwaid')]
    h['gwa_id'] = h[gcols[0]] if gcols else h.iwa_id.str.replace(r'\.I\d+$', '', regex=True)
    if not any(c in h.columns for c in ('iwaelementname', 'iwatitle')):
        gi = read_onet('gwas_to_iwas')
        gi = gi.rename(columns={pick(gi, 'iwaelementid', 'iwaid'): 'iwa_id', pick(gi, 'iwaelementname', 'iwatitle'): 'iwa_title'})
        h = h.merge(gi[['iwa_id', 'iwa_title']].drop_duplicates('iwa_id'), on='iwa_id', how='left')
    else:
        h = h.rename(columns={pick(h, 'iwaelementname', 'iwatitle'): 'iwa_title'})
    if not any(c in h.columns for c in ('gwaelementname', 'elementname', 'gwatitle')):
        cm = read_onet('content_model_reference')
        cm = cm.rename(columns={pick(cm, 'elementid'): 'gwa_id', pick(cm, 'elementname'): 'gwa_title'})
        h = h.merge(cm[['gwa_id', 'gwa_title']].drop_duplicates('gwa_id'), on='gwa_id', how='left')
    else:
        h = h.rename(columns={[c for c in h.columns if c in ('gwaelementname', 'elementname', 'gwatitle')][0]: 'gwa_title'})
    return h[['dwa_id', 'dwa_title', 'iwa_id', 'iwa_title', 'gwa_id', 'gwa_title']].drop_duplicates('dwa_id')


def ntitle(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def iwa_legacy_map(h=None):
    """O*NET 31.0 renumbered IWAs and DWAs (IWA '4.A.1.a.1.I01' -> '4.A.1.a.1.a'; DWA '4.A.1.a.1.I01.D01' ->
    '4.A.1.a.1.a.1'); some IWAs also moved to a different GWA. Returns {legacy IWA id: 31.0 IWA id}, by exact
    normalised-title match between the O*NET 29.0 IWA list (microsoft/working-with-ai iwa_metrics.csv) and 31.0
    gwas_to_iwas (332 of 332 match one to one)."""
    gi = read_onet('gwas_to_iwas')
    gi = gi.rename(columns={pick(gi, 'iwaelementid', 'iwaid'): 'iwa_id', pick(gi, 'iwaelementname', 'iwatitle'): 'iwa_title'})
    ms = pd.read_csv(f'{MSAI}/iwa_metrics.csv')
    m = ms.assign(k=ms.title.map(ntitle)).merge(gi.assign(k=gi.iwa_title.map(ntitle)), on='k')
    assert m.IWA.is_unique and m.iwa_id.is_unique
    return dict(zip(m.IWA, m.iwa_id))


def dwa_legacy_map(legacy, h):
    """{legacy DWA id: 31.0 DWA id} for a table of legacy (id, title) pairs, by exact normalised title; a title that
    occurs twice in 31.0 is resolved with the IWA crosswalk."""
    iw = iwa_legacy_map()
    hk = h.assign(k=h.dwa_title.map(ntitle))
    out = {}
    for lid, title in legacy:
        c = hk[hk.k == ntitle(title)]
        if len(c) > 1:
            c = c[c.iwa_id == iw.get(re.sub(r'\.D\d+$', '', lid))]
        if len(c) == 1:
            out[lid] = c.dwa_id.iloc[0]
    return out


# ---------------------------------------------------------------- OEWS loader
def oews_national():
    """Return (df, vintage). Prefers May 2025 (requested download); falls back to the May 2021 national file
    redistributed in the GPTs-are-GPTs repository."""
    cands = glob.glob(f'{OEWS_DIR}/**/national_M2025_dl.*', recursive=True)
    for z in glob.glob(f'{OEWS_DIR}/*nat*.zip') + glob.glob(f'{OEWS_DIR}/*all*.zip'):
        with zipfile.ZipFile(z) as zf:
            for m in zf.namelist():
                if re.search(r'national_M2025_dl\.(xlsx|csv)$', m) or re.search(r'all_data_M_2025\.(xlsx|csv)$', m):
                    cands.append(f'{z}::{m}')
    if cands:
        p = cands[0]
        df = _read_any(p)
        df = normcols(df)
        if 'areatype' in df.columns and 'all_data' in p:
            df = df[(df.areatype.astype(str) == '1') & (df.naics.astype(str).isin(['0', '000000']))]
        return df, 'May 2025'
    p = f'{GPTS}/national_May2021_dl.csv'
    df = pd.read_csv(p, encoding='utf-8-sig')
    return normcols(df), 'May 2021'


def oews_industry():
    """National industry-specific estimates (May 2025, file oesm25in4.zip). Returns None if not downloaded."""
    cands = glob.glob(f'{OEWS_DIR}/**/nat*d_M2025_dl.*', recursive=True)
    for z in glob.glob(f'{OEWS_DIR}/*in4*.zip'):
        with zipfile.ZipFile(z) as zf:
            for m in zf.namelist():
                if re.search(r'nat[0-9a-z]*_M2025_dl\.(xlsx|csv)$', m, re.I):
                    cands.append(f'{z}::{m}')
    if not cands:
        return None
    frames = []
    for p in sorted(set(cands)):
        d = normcols(_read_any(p))
        d['_file'] = os.path.basename(p.split('::')[-1])
        frames.append(d)
    return pd.concat(frames, ignore_index=True)


def _read_any(p):
    if '::' in p:
        z, m = p.split('::', 1)
        with zipfile.ZipFile(z) as zf:
            data = zf.read(m)
        return pd.read_excel(io.BytesIO(data)) if m.endswith('.xlsx') else pd.read_csv(io.BytesIO(data))
    return pd.read_excel(p) if p.endswith('.xlsx') else pd.read_csv(p, encoding='utf-8-sig')


def num(x):
    """Parse BLS numeric strings ('1,234', '#', '*', '**') -> float (NaN for suppressed or top-coded)."""
    if pd.isna(x):
        return np.nan
    s = str(x).replace(',', '').strip()
    try:
        return float(s)
    except ValueError:
        return np.nan
