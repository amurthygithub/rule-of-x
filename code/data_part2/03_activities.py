"""activities.csv and occ_activity.csv (contract Section 12), plus crosswalks.

FULL MODE (O*NET 31.0 files present in data/raw/onet_31_0/):
  Time shares. For each O*NET-SOC occupation and task: IM = importance (1-5), RT = relevance (% of incumbents),
  Fbar = mean frequency category (1-7) from the FT distribution. Task weight w = IM * Fbar * RT/100 (importance x
  frequency, as the spec asks, scaled by relevance so that supplemental tasks few incumbents perform get less time).
  Missing ratings are imputed with the occupation median (core tasks missing RT get 100). Each task's weight is
  split equally across the DWAs it links to; tasks with no DWA link are dropped (share reported). Shares are
  normalised within each O*NET-SOC code, then averaged with equal weights over the O*NET-SOC codes that make up
  each OEWS occupation (crosswalk rules in common.oews_onet_crosswalk), and renormalised to sum to 1 per soc.
  Alternative shares: time_share_im_f (IM x Fbar, no relevance) and time_share_equal (equal task weights).
  DWA attributes from task-level sources are averaged with weights = task time share x occupation employment:
  physical (Tomlinson et al. task classification, O*NET 29.0 Task IDs), exposure (Eloundou et al. GPT-4 beta,
  O*NET 27.2 Task IDs), AI usage (Anthropic Economic Index, if downloaded), task hours (AEI human_only_time_mean
  if downloaded, else a frequency identity marked assumed).

INTERIM MODE (no O*NET files): writes activities_iwa_interim.csv and occ_activity_iwa_interim.csv at the IWA level
  from microsoft/working-with-ai (SOC x IWA relevance-importance weights from O*NET 29.0).
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glob
import re
import numpy as np
import pandas as pd
from common import (OUT, GPTS, MSAI, AEI_DIR, read_onet, onet_available, pick, soc6, write_csv, save_meta,
                    oews_onet_crosswalk, normcols, onet_hierarchy, dwa_legacy_map, iwa_legacy_map)

occ = pd.read_csv(f'{OUT}/occupations.csv', dtype={'soc': str})
EMP = occ.set_index('soc').employment.fillna(0)
LIC = occ.set_index('soc').licensed_signoff.fillna(0)
H_WORK = 1877.0   # worked hours per FTE-year: 2,080 paid hours / (1 + paid-leave share 0.1079), ECEC June 2026 (params.yaml)
# assumed occurrences per year for O*NET frequency categories 1..7 (used only for the est_task_hours fallback)
FREQ_MID = {1: 1, 2: 4, 3: 24, 4: 130, 5: 250, 6: 750, 7: 2000}

# EU AI Act Annex III high-risk areas, matched on DWA (and IWA) titles. Constructed rule; see the source log.
ANNEX3 = [
    ('employment', r'job applicant|applicants? for (employment|positions?|jobs?)|candidates? for (employment|positions?|jobs?)|'
                   r'recruit|\bhir(e|ing)\b|job seekers|personnel (selection|actions|decisions)|staffing decisions|'
                   r'evaluat\w* (employee|personnel|staff|worker)|employee performance|selection interviews|'
                   r'performance of (staff|employees|personnel|workers|educational staff|applicants)|terminat\w* (of )?employ|'
                   r'promot\w* (of )?(employees|staff|personnel|workers)'),
    ('credit', r'credit ?worth|credit (risk|application|history|rating|score)|loan (application|applicant|request)|approve loans|lending'),
    ('insurance_life_health', r'underwrit|(life|health) insurance'),
    ('public_benefits', r'eligib\w* for (public|government|social|welfare|benefit|assistance|aid|services)|public assistance|welfare benefits'),
    ('education', r'admission|grade (student|exam|paper|test|assignment)|assess\w* (\w+ )?(student|learner)|'
                  r'evaluat\w* (student|learner)|student (performance|progress|achievement|work)|needs of students'),
    ('justice_law_enforcement', r'criminal|suspects?\b|offender|parole|probation|judicial|sentenc|court (decisions?|rulings?)|legal decisions'),
    ('migration_border', r'asylum|immigra|visa\b|border'),
    ('biometrics', r'biometric|fingerprint|facial recognition'),
    ('emergency_triage', r'emergency calls|dispatch\w* emergency|triage'),
]


def annex3(title):
    t = str(title).lower()
    for area, rx in ANNEX3:
        if re.search(rx, t):
            return area
    return ''


def wmean(v, w):
    m = v.notna() & w.notna() & (w > 0)
    return float(np.average(v[m], weights=w[m])) if m.any() else np.nan


# ------------------------------------------------------------------ task-level external sources
el = pd.read_csv(f'{GPTS}/full_labelset.tsv', sep='\t', index_col=0)
el['taskid'] = el['Task ID'].astype(int)
EMAP = {'E0': 0.0, 'E1': 1.0, 'E2': 0.5}
el_task = el.groupby('taskid').agg(gpt4_beta=('beta', 'mean'),
                                   human_beta=('human_exposure_agg', lambda s: s.map(EMAP).mean()),
                                   gpt4_automation=('automation', 'mean'))
phys_task = pd.read_csv(f'{MSAI}/physical_tasks.csv').rename(columns={'Task ID': 'taskid'})
phys_task['physical'] = phys_task.Physical.astype(str).str.lower().eq('true').astype(float)
phys_task = phys_task.set_index('taskid').physical


def load_aei(h):
    """Return (task_usage: Series taskid->share, dwa_usage: Series dwa->share, task_hours: Series taskid->hours, note)."""
    """2026-06-26 release (Claude.ai, global rows): metric 'pct' is a percent of all conversations, published only for
    cells above AEI thresholds (missing = not published, not zero); human_only_time_mean is in hours. Values are
    averaged over the monthly windows in the file (April and May 2026)."""
    note, tu, du, th = [], None, {}, None
    latest = sorted(glob.glob(f'{AEI_DIR}/**/aei_claude_ai_2026-*.csv', recursive=True))
    if latest:
        a = normcols(pd.read_csv(latest[-1], dtype=str))
        a = a[(a.categoryname == 'onet') & (a.geolevel == 'global')].copy()
        a['value'] = pd.to_numeric(a.value, errors='coerce')
        wins = sorted(a.datestart.unique())

        def metric(mid, level):
            s = a[(a.metricid == mid) & (a.hierarchylevel == level)]
            return s.groupby('nodeexternalid').value.mean()
        nodes = a[a.hierarchylevel == '1'][['nodeexternalid', 'nodename']].drop_duplicates('nodeexternalid')
        lmap = dwa_legacy_map(zip(nodes.nodeexternalid, nodes.nodename), h)      # legacy DWA id -> 31.0 DWA id
        _metric = metric

        def metric(mid, level):
            v = _metric(mid, level)
            if level == '1':
                v = v.groupby(v.index.map(lmap)).mean() if mid != 'pct' else v.groupby(v.index.map(lmap)).sum()
            return v
        note.append(f'AEI DWA nodes {len(nodes)}, mapped to 31.0 DWA ids by title: {len(lmap)}')
        du = {'ai_usage': metric('pct', '1') / 100,                                   # share of conversations
              'aei_automation_pct': metric('collaboration_bucket_automation_pct', '1'),
              'aei_human_only_hours': metric('human_only_time_mean', '1'),
              'aei_human_with_ai_minutes': metric('human_with_ai_time_mean', '1')}
        th = metric('human_only_time_mean', '0')
        th.index = th.index.astype(int)
        note.append(f'{os.path.basename(latest[-1])}: global onet rows, windows {wins}; DWA pct published for '
                    f"{du['ai_usage'].notna().sum()} DWAs, summing to {du['ai_usage'].sum():.3f} of conversations; "
                    f'task-level human_only_time_mean for {len(th)} tasks')
    v2 = glob.glob(f'{AEI_DIR}/**/release_2025_03_27/task_pct_v2.csv', recursive=True)
    ts = glob.glob(f'{AEI_DIR}/**/release_2025_03_27/onet_task_statements.csv', recursive=True)
    if v2 and ts:
        p = pd.read_csv(v2[0])
        s = pd.read_csv(ts[0])
        s['key'] = s['Task'].astype(str).str.lower().str.strip()
        tcol = [c for c in p.columns if 'task' in c.lower()][0]
        pc = [c for c in p.columns if 'pct' in c.lower()][0]
        p['key'] = p[tcol].astype(str).str.lower().str.strip()
        ids = s.groupby('key')['Task ID'].apply(list)
        rows = []
        for k, v in zip(p.key, p[pc]):
            for tid in ids.get(k, []):
                rows.append((int(tid), v / len(ids[k])))
        tu = pd.DataFrame(rows, columns=['taskid', 'pct']).groupby('taskid').pct.sum()
        matched = p.key.isin(ids.index)
        note.append(f'task_pct_v2: pct sums to {p[pc].sum():.2f}; {matched.mean():.3f} of task texts matched '
                    f'({p.loc[matched, pc].sum() / p[pc].sum():.3f} of usage)')
        tu = tu / 100
    return tu, du, th, '; '.join(note)


# ------------------------------------------------------------------ FULL MODE
def full():
    ts, tr, t2d = (read_onet(k) for k in ('task_statements', 'task_ratings', 'tasks_to_dwas'))
    h = onet_hierarchy()
    cat = read_onet('task_categories')
    cmr = read_onet('content_model_reference')
    C, T = 'onetsoccode', 'taskid'
    ts = ts.rename(columns={pick(ts, 'onetsoccode'): C, pick(ts, 'taskid'): T})
    tr = tr.rename(columns={pick(tr, 'onetsoccode'): C, pick(tr, 'taskid'): T})
    t2d = t2d.rename(columns={pick(t2d, 'onetsoccode'): C, pick(t2d, 'taskid'): T, pick(t2d, 'dwaelementid', 'dwaid'): 'dwaid'})
    ts['tasktype'] = ts[pick(ts, 'tasktype')].astype(str) if any('tasktype' in c for c in ts.columns) else 'Core'
    sc, val = pick(tr, 'scaleid'), pick(tr, 'datavalue')
    tr[val] = pd.to_numeric(tr[val], errors='coerce')
    im = tr[tr[sc] == 'IM'].groupby([C, T])[val].mean().rename('im')
    rt = tr[tr[sc] == 'RT'].groupby([C, T])[val].mean().rename('rt')
    ft = tr[tr[sc] == 'FT'].copy()
    ft['cat'] = pd.to_numeric(ft[pick(ft, 'category')], errors='coerce')
    ft['cxp'] = ft.cat * ft[val]
    ft['fmid'] = ft.cat.map(FREQ_MID) * ft[val]
    g = ft.groupby([C, T])
    fbar = (g.cxp.sum() / g[val].sum()).rename('fbar')
    fyear = (g.fmid.sum() / g[val].sum()).rename('f_per_year')
    t = ts[[C, T, 'tasktype']].drop_duplicates().set_index([C, T]).join([im, rt, fbar, fyear]).reset_index()
    t['rated'] = t[['im', 'fbar']].notna().all(axis=1).astype(int)
    for col in ['im', 'fbar', 'f_per_year']:
        t[col] = t[col].fillna(t.groupby(C)[col].transform('median')).fillna(t[col].median())
    core = t.tasktype.str.lower().str.startswith('core')
    t.loc[core & t.rt.isna(), 'rt'] = 100.0
    t['rt'] = t.rt.fillna(t.groupby(C).rt.transform('median')).fillna(t.rt.median())
    t['w'] = t.im * t.fbar * t.rt / 100
    t['w_imf'] = t.im * t.fbar
    t['w_eq'] = 1.0
    links = t2d[[C, T, 'dwaid']].drop_duplicates()
    links['ndwa'] = links.groupby([C, T]).dwaid.transform('count')
    lost = t.merge(links[[C, T]].drop_duplicates(), how='left', indicator=True)
    lost_share = float(lost.loc[lost._merge == 'left_only', 'w'].sum() / lost.w.sum())
    td = t.merge(links, on=[C, T])
    for wc in ['w', 'w_imf', 'w_eq']:
        td[wc + '_d'] = td[wc] / td.ndwa
        td[wc + '_s'] = td[wc + '_d'] / td.groupby(C)[wc + '_d'].transform('sum')   # share within O*NET-SOC
    # map O*NET-SOC -> OEWS code
    xw, rule = oews_onet_crosswalk(occ.soc.tolist(), td[C].unique().tolist())
    inv = {c: o for o, cs in xw.items() for c in cs}
    td['soc'] = td[C].map(inv)
    unmapped = sorted(set(td.loc[td.soc.isna(), C]))
    td = td[td.soc.notna()]
    n_on = td.groupby('soc')[C].nunique()
    td['emp_on'] = td.soc.map(EMP).fillna(0) / td.soc.map(n_on)
    oa = (td.groupby(['soc', 'dwaid'])[['w_s', 'w_imf_s', 'w_eq_s']].sum()
          .div(td.groupby('soc')[C].nunique(), axis=0, level='soc')).reset_index()
    for c in ['w_s', 'w_imf_s', 'w_eq_s']:
        oa[c] = oa[c] / oa.groupby('soc')[c].transform('sum')
    oa = oa.rename(columns={'w_s': 'time_share', 'w_imf_s': 'time_share_im_f', 'w_eq_s': 'time_share_equal', 'dwaid': 'dwa_id'})
    oa['method'] = 'IM x Fbar x RT/100, O*NET 31.0 task ratings, split equally over linked DWAs, equal-weight mean over O*NET-SOC codes in the OEWS code'
    write_csv(oa.sort_values(['soc', 'time_share'], ascending=[True, False]), 'occ_activity.csv')

    # ---------------- activity attributes
    td['mass'] = td.w_s * td.emp_on                     # employment x time share (task-DWA level)
    td['phys'] = td[T].astype(int).map(phys_task)
    td = td.join(el_task, on=T)
    td['lic'] = td.soc.map(LIC)
    td['hours_identity'] = (td.w / td.groupby(C).w.transform('sum')) * H_WORK / td.f_per_year
    tu, du, th, aei_note = load_aei(h)
    td['aei_hours'] = td[T].astype(int).map(th) if th is not None else np.nan
    gb = td.groupby('dwaid')
    A = pd.DataFrame({
        'emp_time_share_us': gb.mass.sum() / td.mass.sum(),
        'physical_task_share': gb.apply(lambda d: wmean(d.phys, d.mass)),
        'exposure_llm': gb.apply(lambda d: wmean(d.gpt4_beta, d.mass)),
        'exposure_llm_human': gb.apply(lambda d: wmean(d.human_beta, d.mass)),
        'automation_gpt4': gb.apply(lambda d: wmean(d.gpt4_automation, d.mass)),
        'exposure_coverage': gb.apply(lambda d: float(d.loc[d.gpt4_beta.notna(), 'mass'].sum() / d.mass.sum()) if d.mass.sum() > 0 else np.nan),
        'licensed_time_share': gb.apply(lambda d: wmean(d.lic, d.mass)),
        'n_tasks': gb[T].nunique(), 'n_occupations': gb.soc.nunique(),
        'hours_identity_median': gb.hours_identity.median(),
        'aei_hours_median': gb.aei_hours.median(),
    })
    A['physical'] = (A.physical_task_share >= 0.5).astype(int)
    A['exposure_measure'] = 'eloundou2024_gpt4_beta'
    if tu is not None:
        td['aei_share'] = td[T].astype(int).map(tu) / td.ndwa
        A['ai_usage_2025'] = td.groupby('dwaid').aei_share.sum(min_count=1)
    else:
        A['ai_usage_2025'] = np.nan
    for k, v in du.items():
        A[k] = v.reindex(A.index)
    if 'ai_usage' not in A:
        A['ai_usage'] = np.nan
    A['ai_usage_source'] = np.where(A.ai_usage.notna(), 'AEI release_2026_06_26, Claude.ai global, DWA pct / 100, mean of Apr-May 2026',
                                    'not published by AEI (below threshold); see ai_usage_2025')
    A['aei_hours_dwa'] = A.aei_human_only_hours if 'aei_human_only_hours' in A else np.nan
    A['est_task_hours'] = A.aei_hours_dwa.fillna(A.aei_hours_median).fillna(A.hours_identity_median).clip(0.05, 2000)
    A['est_task_hours_method'] = np.select(
        [A.aei_hours_dwa.notna(), A.aei_hours_median.notna()],
        ['AEI 2026-06-26 human_only_time_mean, DWA level (model estimate from conversations)',
         'AEI 2026-06-26 human_only_time_mean, median over linked tasks'],
        'assumed: time_share x 1877 h / expected annual frequency (category midpoints)')
    # hierarchy (loaded at the top of full())
    A = h.set_index('dwa_id').join(A, how='left').reset_index()
    inv_iwa = {v: k for k, v in iwa_legacy_map().items()}
    A['iwa_id_legacy'] = A.iwa_id.map(inv_iwa)
    write_csv(pd.DataFrame(sorted(inv_iwa.items()), columns=['iwa_id', 'iwa_id_legacy']).assign(
        method='exact normalised title match, O*NET 29.0 IWA list (Tomlinson et al.) vs O*NET 31.0 gwas_to_iwas'), 'xw_iwa_legacy.csv')
    A['eu_annex3_area'] = [annex3(a) or annex3(b) for a, b in zip(A.dwa_title, A.iwa_title)]
    A['regulated_class'] = np.where(A.licensed_time_share >= 0.5, 'licensed',
                                    np.where(A.eu_annex3_area != '', 'high_risk_eu', 'none'))
    cols = ['dwa_id', 'dwa_title', 'iwa_id', 'gwa_id', 'gwa_title', 'physical', 'exposure_llm', 'exposure_measure',
            'ai_usage', 'est_task_hours', 'regulated_class', 'iwa_title', 'physical_task_share', 'exposure_llm_human',
            'automation_gpt4', 'exposure_coverage', 'ai_usage_source', 'ai_usage_2025', 'aei_automation_pct',
            'aei_human_with_ai_minutes', 'est_task_hours_method', 'hours_identity_median', 'licensed_time_share',
            'eu_annex3_area', 'emp_time_share_us', 'n_tasks', 'n_occupations', 'iwa_id_legacy']
    for c in cols:
        if c not in A:
            A[c] = np.nan
    write_csv(A[cols].sort_values('dwa_id'), 'activities.csv')
    # crosswalks
    xt = td[[C, T, 'dwaid', 'soc']].drop_duplicates().rename(columns={C: 'onet_soc', T: 'task_id', 'dwaid': 'dwa_id'})
    xt['in_eloundou_27_2'] = xt.task_id.astype(int).isin(el_task.index).astype(int)
    xt['in_tomlinson_physical_29_0'] = xt.task_id.astype(int).isin(phys_task.index).astype(int)
    if tu is not None:
        xt['in_aei_task_pct_v2'] = xt.task_id.astype(int).isin(tu.index).astype(int)
    write_csv(xt, 'xw_task_dwa.csv')
    xo = pd.DataFrame([(o, c, rule[o]) for o, cs in xw.items() for c in cs], columns=['soc', 'onet_soc', 'rule'])
    write_csv(xo, 'xw_oews_onetsoc.csv')
    m = td.mass.sum()
    meta = dict(mode='full', n_dwa=int(A.dwa_id.nunique()), n_soc=int(oa.soc.nunique()),
                task_weight_without_dwa=lost_share, unmapped_onetsoc=unmapped,
                rated_task_share=float(t.rated.mean()),
                eloundou_mass_coverage=float(td.loc[td.gpt4_beta.notna(), 'mass'].sum() / m),
                physical_mass_coverage=float(td.loc[td.phys.notna(), 'mass'].sum() / m),
                aei=aei_note, regulated_counts=A.regulated_class.value_counts().to_dict(),
                freq_categories=(cat.to_dict('records') if cat is not None else None))
    save_meta('activities', meta)
    print(meta)


# ------------------------------------------------------------------ INTERIM MODE
def interim():
    w = pd.read_csv(f'{MSAI}/soc_iwa_weights.csv').set_index('SOC Code')
    wn = pd.read_csv(f'{MSAI}/soc_iwa_nonphysical_weights.csv').set_index('SOC Code').reindex(w.index)
    iw = pd.read_csv(f'{MSAI}/iwa_metrics.csv').set_index('IWA')
    long = w.stack().rename('w').reset_index().rename(columns={'SOC Code': 'soc', 'level_1': 'iwa_id'})
    long.columns = ['soc', 'iwa_id', 'w']
    long = long[long.w > 0]
    long['time_share'] = long.w / long.groupby('soc').w.transform('sum')
    long['method'] = 'interim: IWA weights from O*NET 29.0 task relevance x importance (Tomlinson et al. 2025, soc_iwa_weights.csv)'
    write_csv(long[['soc', 'iwa_id', 'time_share', 'method']], 'occ_activity_iwa_interim.csv')
    ln = wn.stack().rename('wn').reset_index()
    ln.columns = ['soc', 'iwa_id', 'wn']
    long = long.merge(ln, on=['soc', 'iwa_id'], how='left')
    long['emp'] = long.soc.map(EMP).fillna(0)
    long['mass'] = long.time_share * long.emp
    long['phys'] = 1 - long.wn / long.w
    g = long.groupby('iwa_id')
    A = pd.DataFrame({'emp_time_share_us': g.mass.sum() / long.mass.sum(),
                      'physical_task_share': g.apply(lambda d: wmean(d.phys, d.mass))})
    A = iw[['title', 'share_user', 'share_ai', 'completion_user', 'impact_scope_user']].join(A, how='left')
    A = A.reset_index().rename(columns={'IWA': 'iwa_id', 'title': 'iwa_title', 'share_user': 'copilot_share_user',
                                        'share_ai': 'copilot_share_ai'})
    A['gwa_id'] = A.iwa_id.str.replace(r'\.I\d+$', '', regex=True)
    A['physical'] = (A.physical_task_share >= 0.5).astype(int)
    A['eu_annex3_area'] = A.iwa_title.map(annex3)
    A['note'] = 'interim IWA-level file; DWA-level activities.csv is built when O*NET 31.0 is downloaded'
    write_csv(A, 'activities_iwa_interim.csv')
    save_meta('activities', dict(mode='interim', n_iwa=len(A), n_soc=int(long.soc.nunique())))


if onet_available():
    full()
else:
    print('O*NET 31.0 files not found in data/raw/onet_31_0/: building interim IWA-level files')
    interim()
