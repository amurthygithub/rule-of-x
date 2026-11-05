"""task_statements.csv: O*NET 31.0 task statements for the tasks the pipeline links to DWAs (playbook input).

Input: the O*NET 31.0 task_statements table (data/raw/onet_31_0/task_statements.csv, converted from the MySQL dump by
00_onet_mysql_to_csv.py; columns onetsoc_code, task_id, task, task_type, incumbents_responding, date_updated,
domain_source) and data/tasks/xw_task_dwa.csv (built by 03_activities.py). Output rows are restricted to the task_ids in
xw_task_dwa.csv; the task text is copied unchanged. soc is the OEWS occupation code that xw_task_dwa.csv assigns to the
task's O*NET-SOC code. task_type is lower-cased (core, supplemental; empty where O*NET gives none).

Also writes data/tasks/data_dictionary.csv (columns of task_statements.csv and the O*NET attribution).
License: O*NET 31.0 Database, CC BY 4.0; attribution below (wording from https://www.onetcenter.org/license_db.html,
read 29 Oct 2026; the archive's Read Me.txt states the CC BY 4.0 license).
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from common import OUT, read_onet, pick, normcols, write_csv, save_meta

ONET_VERSION = '31.0'
ATTRIBUTION = ('This dataset includes information from the O*NET 31.0 Database by the U.S. Department of Labor, Employment '
               'and Training Administration (USDOL/ETA). Used under the CC BY 4.0 license. O*NET® is a trademark of '
               'USDOL/ETA. The authors of this project have modified all or some of this information. USDOL/ETA has not '
               'approved, endorsed, or tested these modifications.')

ts = read_onet('task_statements')
if ts is None:
    print('O*NET 31.0 task_statements not found: task_statements.csv not built')
    save_meta('task_statements', dict(mode='missing'))
    sys.exit(0)
ts = normcols(ts)
c_soc, c_id, c_txt = pick(ts, 'onetsoccode', 'onetsoc'), pick(ts, 'taskid'), pick(ts, 'task')
c_typ, c_inc = pick(ts, 'tasktype'), pick(ts, 'incumbentsresponding')
c_dt, c_dom = pick(ts, 'dateupdated'), pick(ts, 'domainsource')
ts = ts.rename(columns={c_soc: 'onet_soc', c_id: 'task_id', c_txt: 'task', c_typ: 'task_type',
                        c_inc: 'incumbents_responding', c_dt: 'date_updated', c_dom: 'domain_source'})
ts['task_id'] = pd.to_numeric(ts.task_id, errors='raise').astype(int)
assert ts.task_id.is_unique, 'O*NET task_id is not unique'

xw = pd.read_csv(f'{OUT}/xw_task_dwa.csv', dtype={'soc': str, 'onet_soc': str})
keep = sorted(set(xw.task_id.astype(int)))
soc_of = xw.drop_duplicates(['task_id', 'soc']).groupby('task_id').soc.agg(lambda s: ';'.join(sorted(set(s))))
onet_of = xw.drop_duplicates(['task_id', 'onet_soc']).groupby('task_id').onet_soc.agg(lambda s: ';'.join(sorted(set(s))))
out = ts[ts.task_id.isin(keep)].copy()
missing = sorted(set(keep) - set(out.task_id))
assert not missing, f'{len(missing)} task_ids of xw_task_dwa.csv are not in O*NET 31.0 task_statements'
assert (out.set_index('task_id').onet_soc == onet_of.reindex(out.task_id).values).all(), 'O*NET-SOC differs from xw_task_dwa'
out['soc'] = out.task_id.map(soc_of)
out['task_type'] = out.task_type.fillna('').astype(str).str.strip().str.lower().replace({'n/a': ''})
assert out.task_type.isin(['core', 'supplemental', '']).all(), out.task_type.unique()
out['incumbents_responding'] = pd.to_numeric(out.incumbents_responding, errors='coerce').astype('Int64')
out['onet_version'] = ONET_VERSION
out = out[['task_id', 'onet_soc', 'soc', 'task', 'task_type', 'incumbents_responding', 'date_updated', 'domain_source',
           'onet_version']].sort_values('task_id')
write_csv(out, 'task_statements.csv')

DD = [
    ('task_statements.csv', '(file)', '', 'O*NET 31.0 task statements for the task_ids in xw_task_dwa.csv; built by '
     'code/data_part2/12_task_statements.py', 'O*NET 31.0 Database (August 2026), task_statements table', ATTRIBUTION),
    ('task_statements.csv', 'task_id', 'integer', 'O*NET task identifier (stable across releases)', 'O*NET task_statements.task_id', ''),
    ('task_statements.csv', 'onet_soc', 'string', 'O*NET-SOC code of the occupation the task belongs to', 'O*NET task_statements.onetsoc_code', ''),
    ('task_statements.csv', 'soc', 'string', 'OEWS (SOC 2018) code linked to onet_soc; several codes separated by ";"',
     'xw_task_dwa.csv (crosswalk in xw_oews_onetsoc.csv)', ''),
    ('task_statements.csv', 'task', 'string', 'task statement text, unchanged', 'O*NET task_statements.task', ''),
    ('task_statements.csv', 'task_type', 'string', 'core or supplemental (empty where O*NET gives none)', 'O*NET task_statements.task_type, lower-cased', ''),
    ('task_statements.csv', 'incumbents_responding', 'integer', 'number of incumbents responding (empty for analyst-rated or unrated tasks)',
     'O*NET task_statements.incumbents_responding', ''),
    ('task_statements.csv', 'date_updated', 'date', 'date O*NET last updated the statement', 'O*NET task_statements.date_updated', ''),
    ('task_statements.csv', 'domain_source', 'string', 'source of the rating data (for example Incumbent, Analyst)', 'O*NET task_statements.domain_source', ''),
    ('task_statements.csv', 'onet_version', 'string', 'O*NET database release', 'constant 31.0', ''),
]
dd = pd.DataFrame(DD, columns=['file', 'column', 'type', 'definition', 'source', 'attribution'])
assert set(dd[dd.column != '(file)'].column) == set(out.columns)
write_csv(dd, 'data_dictionary.csv')
save_meta('task_statements', dict(mode='full', n_rows=int(len(out)), n_onet_soc=int(out.onet_soc.nunique()),
                                  task_type_counts=out.task_type.value_counts().to_dict(),
                                  incumbents_missing=int(out.incumbents_responding.isna().sum()),
                                  onet_tasks_total=int(len(ts)), xw_task_ids=len(keep), attribution=ATTRIBUTION))
print(out.task_type.value_counts().to_dict(), 'incumbents missing', int(out.incumbents_responding.isna().sum()))
