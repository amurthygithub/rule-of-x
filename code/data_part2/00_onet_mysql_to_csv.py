"""Convert the O*NET 31.0 MySQL distribution (db_31_0_mysql.zip) into the per-table CSV files the build expects.

The SQL dumps contain CREATE TABLE and single-row INSERT statements in standard SQL ('' escapes quotes). They are
loaded into an in-memory SQLite database after dropping MySQL conditional comments, then written out with the
SQL column names (common.normcols maps both naming styles to the same keys).
"""
import csv
import os
import re
import sqlite3
import sys
import zipfile

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'raw', 'onet_31_0')
TABLES = ['task_statements', 'task_ratings', 'task_categories', 'tasks_to_dwas', 'gwas_to_iwas_to_dwas', 'gwas_to_iwas',
          'occupation_data', 'content_model_reference', 'work_context', 'work_context_categories', 'job_zones',
          'scales_reference', 'work_activities', 'job_titles']
zpath = os.path.join(RAW, 'db_31_0_mysql.zip')
z = zipfile.ZipFile(zpath)
names = {re.sub(r'^\d+_', '', os.path.basename(n))[:-4]: n for n in z.namelist() if n.endswith('.sql')}
for t in TABLES:
    if t not in names:
        print('missing in archive:', t); continue
    sql = z.read(names[t]).decode('utf-8')
    sql = re.sub(r'/\*!.*?\*/;?', '', sql)                    # MySQL conditional comments
    sql = re.sub(r',\s*FOREIGN KEY \([^)]*\) REFERENCES [^)]*\)', '', sql)
    # the dump is untrusted input: refuse statements that could touch files or load code inside SQLite
    if re.search(r'^\s*(ATTACH|DETACH|VACUUM|PRAGMA)\b|load_extension\s*\(', sql, re.I | re.M):
        sys.exit(f'refusing {names[t]}: unexpected statement type in SQL dump')
    con = sqlite3.connect(':memory:')
    con.executescript(sql)
    cur = con.execute(f'SELECT * FROM {t}')
    cols = [c[0] for c in cur.description]
    out = os.path.join(RAW, f'{t}.csv')
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(cols)
        n = 0
        for row in cur:
            w.writerow(row); n += 1
    print(f'{t}: {n} rows -> {out}')
