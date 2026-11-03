"""Contract checks for data/tasks (spec Section 12). Exits non-zero on any failure."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # this folder (python3 -I does not add it), also in a scratch copy
import pandas as pd
import yaml
from common import OUT, save_meta

REQ = {
    'functions.csv': ['function_id', 'function_name', 'description', 'apqc_category', 'cost_bucket', 'customer_facing'],
    'occupations.csv': ['soc', 'onet_soc', 'title', 'wage_median', 'wage_mean', 'employment', 'physical_share', 'licensed_signoff'],
    'activities.csv': ['dwa_id', 'dwa_title', 'iwa_id', 'gwa_id', 'gwa_title', 'physical', 'exposure_llm', 'exposure_measure',
                       'ai_usage', 'est_task_hours', 'est_task_hours_method', 'regulated_class'],
    'occ_activity.csv': ['soc', 'dwa_id', 'time_share', 'method'],
    'industry_staffing.csv': ['naics', 'soc', 'emp_share'],
    'function_occ.csv': ['function_id', 'soc', 'weight'],
    'industry_function_shares.csv': ['sic', 'naics', 'size_band', 'function_id', 'share_of_revenue_prior', 'share_of_revenue_sd'],
    'processes.csv': ['process_id', 'process_name', 'function_id', 'output_unit', 'typical_volume_per_musd_revenue', 'volume_source'],
    'process_activities.csv': ['process_id', 'step', 'dwa_id', 'critical_path'],
}
fail, info = [], {}
D = {}
for f, cols in REQ.items():
    try:
        D[f] = pd.read_csv(f'{OUT}/{f}', dtype={'soc': str, 'naics': str, 'sic': str})
    except FileNotFoundError:
        fail.append(f'{f}: missing'); continue
    miss = [c for c in cols if c not in D[f].columns]
    if miss:
        fail.append(f'{f}: missing columns {miss}')
    info[f] = len(D[f])


def check(cond, msg):
    if not cond:
        fail.append(msg)


fn, oc, ac, oa = D['functions.csv'], D['occupations.csv'], D['activities.csv'], D['occ_activity.csv']
check(fn.cost_bucket.isin(['cogs', 'rnd', 'sm', 'ga']).all(), 'functions: bad cost_bucket')
check(fn.customer_facing.isin([0, 1]).all(), 'functions: customer_facing not 0/1')
check(oc.soc.str.match(r'^\d\d-\d{4}$').all() and oc.soc.is_unique, 'occupations: soc format or duplicates')
check(oc.physical_share.dropna().between(0, 1).all(), 'occupations: physical_share outside [0,1]')
check(oc.licensed_signoff.isin([0, 1]).all(), 'occupations: licensed_signoff not 0/1')
check((oc.oews_vintage == 'May 2025').all(), 'occupations: not May 2025 vintage')
check(ac.dwa_id.is_unique, 'activities: duplicate dwa_id')
check(ac.regulated_class.isin(['none', 'high_risk_eu', 'licensed']).all(), 'activities: bad regulated_class')
check(ac.physical.dropna().isin([0, 1]).all(), 'activities: physical not 0/1')
check(ac.exposure_llm.dropna().between(0, 1).all(), 'activities: exposure outside [0,1]')
s = oa.groupby('soc').time_share.sum()
check(((s - 1).abs() < 1e-4).all(), f'occ_activity: time shares do not sum to 1 (max dev {abs(s - 1).max():.2e})')
check(oa.dwa_id.isin(ac.dwa_id).all(), 'occ_activity: dwa_id not in activities')
check(oa.soc.isin(oc.soc).all(), 'occ_activity: soc not in occupations')
info['occ_activity_soc_coverage_emp'] = float(oc.loc[oc.soc.isin(oa.soc), 'employment'].sum() / oc.employment.sum())
if 'industry_staffing.csv' in D:
    st = D['industry_staffing.csv']
    e = st.groupby('naics').emp_share.sum()
    check(((e - 1).abs() < 1e-4).all(), 'industry_staffing: shares do not sum to 1')
    check(st.naics.str.len().between(2, 6).all(), 'industry_staffing: naics length')
    check(st.soc.isin(oc.soc).mean() > 0.99, f'industry_staffing: {1 - st.soc.isin(oc.soc).mean():.3%} soc not in occupations')
fo = D['function_occ.csv']
w = fo.groupby('function_id').weight.sum()
check(((w - 1).abs() < 1e-6).all(), 'function_occ: weights do not sum to 1')
check(fo.function_id.isin(fn.function_id).all() and fo.soc.isin(oc.soc).all(), 'function_occ: unknown function or soc')
ifs = D['industry_function_shares.csv']
check(ifs.function_id.isin(fn.function_id).all(), 'industry_function_shares: unknown function')
check((ifs.share_of_revenue_prior >= 0).all() and (ifs.share_of_revenue_sd >= 0).all(), 'industry_function_shares: negative values')
# ---- non-software priors (11_nonsoftware_priors.py, spec 24.10); checked when built
import hashlib
import json
import os
ORIG_IFS = ['sic', 'naics', 'size_band', 'function_id', 'cost_bucket', 'share_of_revenue_prior', 'share_of_revenue_sd',
            'bucket_share_mean', 'bucket_share_sd', 'bucket_share_median', 'within_bucket_split', 'within_bucket_range',
            'within_bucket_assumed', 'n_firms', 'years', 'source']
if os.path.exists(f'{OUT}/industry_benchmarks.csv') and os.path.exists(f'{OUT}/xw_damodaran_naics.csv'):
    bmk = pd.read_csv(f'{OUT}/industry_benchmarks.csv')
    xw = pd.read_csv(f'{OUT}/xw_damodaran_naics.csv', dtype={'naics_match': str, 'naics_oews': str}, keep_default_na=False)
    info['industry_benchmarks.csv'], info['xw_damodaran_naics.csv'] = len(bmk), len(xw)
    for c in ['damodaran_industry', 'n_firms', 'gross_margin', 'cogs_sales', 'rnd_sales', 'sga_sales', 'cost_of_capital',
              'roe_unadj', 'roic_aftertax', 'k_ic_per_sales', 'k_flag', 'source_rows']:
        check(c in bmk.columns, f'industry_benchmarks: missing column {c}')
    check(bmk.damodaran_industry.is_unique and 'Total Market' in set(bmk.damodaran_industry), 'industry_benchmarks: names')
    check((bmk.n_firms > 0).all() and ((bmk.n_firms < 20).astype(int) == bmk.small_sample).all(), 'industry_benchmarks: firm counts or small_sample flag')
    check((bmk.sga_identity_gap.abs() < 1e-6).all() and (bmk.rnd_identity_gap.abs() < 1e-6).all(), 'industry_benchmarks: SG&A or R&D identity fails')
    check(bmk.k_ic_per_sales.dropna().gt(0).all(), 'industry_benchmarks: non-positive k')
    check(set(xw.damodaran_industry) == set(bmk.damodaran_industry), 'xw_damodaran_naics: industries differ from benchmarks')
    check(xw.confidence.isin(['high', 'medium', 'low', 'n/a']).all(), 'xw_damodaran_naics: bad confidence')
    em = xw[(xw.emit_function_shares.astype(int) == 1) & (xw.naics_match != '')]
    pre = [p_ for s_ in em.naics_match for p_ in s_.split('/')]
    check(len(pre) == len(set(pre)), 'xw_damodaran_naics: a match prefix is used by two emitted groups')
    check(not any(p_ in ('51', '54') or p_.startswith(('5132', '5415', '5182')) for p_ in pre),
          'xw_damodaran_naics: a match prefix collides with the SEC software rows')
    codes = {c_ for s_ in xw.naics_oews for c_ in s_.split('/') if c_ and c_ != 'ALL_EXCEPT_52_99'}
    if 'industry_staffing.csv' in D:
        check(codes <= set(D['industry_staffing.csv'].naics), f'xw_damodaran_naics: OEWS codes not in industry_staffing {codes - set(D["industry_staffing.csv"].naics)}')
    raw = pd.read_csv(f'{OUT}/industry_function_shares.csv', dtype=str, keep_default_na=False)
    if 'prior_basis' in raw.columns:
        meta = json.load(open(f'{OUT}/_build/nonsoftware_priors.json'))
        swr = raw[raw.prior_basis == 'sec_panel'][ORIG_IFS]
        check(hashlib.sha256(swr.to_csv(index=False).encode()).hexdigest() == meta['software_rows_sha256'],
              'industry_function_shares: software rows differ from those 11_nonsoftware_priors.py preserved')
        nn = ifs[ifs.prior_basis == 'damodaran_oews']
        check(set(nn.damodaran_industry) == set(xw[xw.emit_function_shares.astype(int) == 1].damodaran_industry),
              'industry_function_shares: emitted industries differ from the crosswalk')
        check((nn.groupby('damodaran_industry').function_id.nunique() == len(fn)).all() and
              not nn.duplicated(['damodaran_industry', 'function_id']).any(), 'industry_function_shares: not one row per function')
        ws = nn.groupby(['damodaran_industry', 'source_bucket']).within_bucket_split.sum()
        check(((ws - 1).abs() < 1e-4).all(), 'industry_function_shares: within-bucket splits do not sum to 1')
        tot = nn.groupby('damodaran_industry').share_of_revenue_prior.sum()
        expb = bmk.set_index('damodaran_industry').loc[tot.index, ['cogs_sales', 'rnd_sales', 'sga_sales']].clip(lower=0).sum(axis=1)
        check(((tot - expb).abs() < 1e-4).all(), 'industry_function_shares: function shares do not sum to Damodaran buckets')
        check(nn.share_of_revenue_prior.notna().all() and nn.share_of_revenue_sd.notna().all(), 'industry_function_shares: NaN shares')
# ---- O*NET task statements (12_task_statements.py)
if os.path.exists(f'{OUT}/task_statements.csv'):
    tsk = pd.read_csv(f'{OUT}/task_statements.csv', dtype={'soc': str, 'onet_soc': str, 'onet_version': str}, keep_default_na=False)
    xwt = pd.read_csv(f'{OUT}/xw_task_dwa.csv')
    info['task_statements.csv'] = len(tsk)
    check(tsk.task_id.is_unique, 'task_statements: duplicate task_id')
    check(set(tsk.task_id) == set(xwt.task_id), 'task_statements: task_ids differ from xw_task_dwa.csv')
    check(tsk.task.str.strip().str.len().gt(0).all(), 'task_statements: empty task text')
    check(tsk.task_type.isin(['core', 'supplemental', '']).all(), 'task_statements: bad task_type')
    check((tsk.onet_version == '31.0').all(), 'task_statements: not O*NET 31.0')
    check(tsk.onet_soc.str.match(r'^\d\d-\d{4}\.\d\d$').all(), 'task_statements: onet_soc format')
    socs = {x for v in tsk.soc for x in v.split(';') if x}
    check(socs <= set(oc.soc), f'task_statements: soc codes not in occupations {sorted(socs - set(oc.soc))[:5]}')
    ddp = f'{OUT}/data_dictionary.csv'
    check(os.path.exists(ddp), 'data_dictionary.csv missing')
    if os.path.exists(ddp):
        dd = pd.read_csv(ddp, keep_default_na=False)
        dts = dd[dd.file == 'task_statements.csv']
        check(set(dts[dts.column != '(file)'].column) == set(tsk.columns), 'data_dictionary: task_statements columns not all documented')
        check(dts[dts.column == '(file)'].attribution.str.contains('CC BY 4.0').any(), 'data_dictionary: O*NET attribution missing')
pr, pa = D['processes.csv'], D['process_activities.csv']
check(pr.function_id.isin(fn.function_id).all(), 'processes: unknown function')
check(pa.process_id.isin(pr.process_id).all(), 'process_activities: unknown process')
check(pa.dwa_id.isin(ac.dwa_id).all(), f'process_activities: {(~pa.dwa_id.isin(ac.dwa_id)).sum()} dwa_id not in activities')
check(pa.critical_path.isin([0, 1]).all(), 'process_activities: critical_path not 0/1')
# ---- ICFR scope (07_processes.py rule 6)
if 'icfr_scope' in pr.columns and 'icfr_step' in pa.columns:
    check(pr.icfr_scope.isin(['full', 'partial', 'none']).all(), 'processes: every process needs icfr_scope full, partial or none')
    check(pr.icfr_basis.fillna('').str.len().gt(0).all(), 'processes: icfr_basis missing')
    flg = pa.icfr_step.astype(str).str.lower().eq('true')
    n_flag = flg.groupby(pa.process_id).sum()
    n_step = pa.groupby('process_id').size()
    sc_ = pr.set_index('process_id').icfr_scope
    part = sc_[sc_ == 'partial'].index
    check((n_flag.reindex(part).fillna(0) >= 1).all(), f'processes: partial processes without a flagged step {[p_ for p_ in part if n_flag.get(p_, 0) < 1]}')
    full = sc_[sc_ == 'full'].index
    check((n_flag.reindex(full) == n_step.reindex(full)).all(), 'process_activities: a step of a full-scope process is not flagged')
    none_ = sc_[sc_ == 'none'].index
    check((n_flag.reindex(none_).fillna(0) == 0).all(), 'process_activities: a step of a none-scope process is flagged')
    check(pa.loc[flg, 'icfr_basis'].fillna('').str.len().gt(0).all(), 'process_activities: flagged step without icfr_basis')
    check(pa.typical_systems.fillna('').str.len().gt(0).all(), 'process_activities: typical_systems missing')
    if 'icfr_channel' in pa.columns:
        ch = pa.icfr_channel.fillna('').astype(str)
        check((ch.str.len().gt(0) == flg).all(), 'process_activities: icfr_channel must be set exactly for flagged steps')
        okc = ch[flg].str.split('; ').apply(lambda t: set(t) <= {'process', 'system', 'integration', 'policy'})
        check(okc.all(), 'process_activities: icfr_channel values outside process/system/integration/policy')
    info['icfr_steps_in_scope'] = int(flg.sum())
check((pa.groupby('process_id').step.apply(lambda x: list(x) == list(range(1, len(x) + 1)))).all(), 'process_activities: steps not 1..n')
p = yaml.safe_load(open(f'{OUT}/params.yaml'))
for k in ['payroll_loading', 'capability_path', 'inference_price', 'energy_share_s_E', 'ai_cost', 'outsourcing',
          'regulatory_oversight_floor_psi_min', 'capital_per_unit', 'depreciation', 'transition', 'project_outcomes',
          'learning', 'decision_capacity', 'leadership_and_context', 'ownership_regimes', 'product', 'security_and_maintenance',
          'acquirer']:
    check(k in p, f'params.yaml: missing {k}')
check('permanent_capital' in p.get('ownership_regimes', {}), 'params.yaml: missing ownership_regimes.permanent_capital')


def scen(d, path=''):
    # scenario blocks without a value must say how to switch the limit off and where the domain comes from
    if isinstance(d, dict) and 'quality' in d:
        if d.get('scenario') and d.get('value') is None:
            if 'neutral_value' not in d or 'verified_domain' not in d or d.get('grounding') != 'd':
                fail.append(f'params.yaml: {path} scenario without value lacks neutral_value, verified_domain or class d')
        return
    if isinstance(d, dict):
        for k, v in d.items():
            scen(v, f'{path}/{k}')


scen(p.get('acquirer', {}), 'acquirer')


def walk(d, path=''):
    if isinstance(d, dict) and 'quality' in d:
        if 'source' not in d or 'assumed' not in d:
            fail.append(f'params.yaml: {path} lacks source or assumed flag')
        return
    if isinstance(d, dict):
        for k, v in d.items():
            walk(v, f'{path}/{k}')


walk(p)
info['failures'] = fail
save_meta('validation', info)
print('\n'.join(fail) if fail else 'all contract checks passed', '\n', {k: v for k, v in info.items() if k != 'failures'})
sys.exit(1 if fail else 0)
