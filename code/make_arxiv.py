"""Build the arXiv source package and the replication package.

arXiv source (dist/arxiv/): paper.tex, sections/*.tex (all LaTeX comments stripped), figures/*.pdf, paper.bbl
(arXiv does not run BibTeX), packed as dist/arxiv_source.tar.gz.
Replication package (dist/replication/): code, data and a README, packed as dist/replication_package.zip.
"""
import os
import re
import shutil
import tarfile
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'code'))
from purge_excluded import purge_tree  # noqa: E402  drops the registrants of code/exclusions.py
DIST = os.path.join(ROOT, 'dist')


def strip_comments(tex):
    out = []
    for line in tex.splitlines():
        # remove an unescaped % and everything after it
        m = re.search(r'(?<!\\)%', line)
        if m:
            kept = line[:m.start()]
            if kept.strip() == '':
                continue            # whole-line comment: drop the line
            line = kept.rstrip() + '%'   # keep a bare % so line-end spacing is unchanged
        out.append(line)
    text = '\n'.join(out) + '\n'
    return re.sub(r'\n{3,}', '\n\n', text)


def build_arxiv():
    d = os.path.join(DIST, 'arxiv')
    shutil.rmtree(d, ignore_errors=True)
    for sub in ['sections/tables', 'figures']:
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    main = ['paper.tex'] + [os.path.join('sections', f) for f in sorted(os.listdir(os.path.join(ROOT, 'sections'))) if f.endswith('.tex')]
    body = ''.join(strip_comments(open(os.path.join(ROOT, f)).read()) for f in main)
    inputs = set(re.findall(r'\\input\{([^}]+)\}', body))
    tables = sorted(f for f in inputs if f.startswith('sections/tables/'))
    figs = sorted(set(re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', body + ''.join(open(os.path.join(ROOT, f)).read() for f in tables))))
    for f in main + tables:
        open(os.path.join(d, f), 'w').write(strip_comments(open(os.path.join(ROOT, f)).read()))
    for f in figs:
        f = f if f.endswith('.pdf') else f + '.pdf'
        shutil.copy(os.path.join(ROOT, f), os.path.join(d, f))
    print('tables:', len(tables), 'figures:', len(figs))
    shutil.copy(os.path.join(ROOT, 'paper.bbl'), os.path.join(d, 'paper.bbl'))
    tar = os.path.join(DIST, 'arxiv_source.tar.gz')
    with tarfile.open(tar, 'w:gz') as t:
        for base, _, files in os.walk(d):
            for f in files:
                p = os.path.join(base, f)
                t.add(p, arcname=os.path.relpath(p, d))
    return d, tar


REPL_CODE = ['retrieval_browser.js', 'fetch_companyfacts.py', 'build_panel_v2.py', 'estimate_frontier.py', 'estimate_revised.py',
             'decompose_gap.py', 'calibrate_horizons.py', 'paper_stats.py', 'verify_theory.py', 'frontier_figures.py',
             'exclusions.py', 'purge_excluded.py']
REPL_DATA = ['companyfacts_ciks.txt', 'sic_universe.json', 'companyfacts_extract.json', 'panel_v2_all.csv', 'panel_broad.csv', 'panel.csv']


def build_replication(readme):
    d = os.path.join(DIST, 'replication')
    shutil.rmtree(d, ignore_errors=True)
    for sub in ['code', 'data', 'figures', 'sections/tables', 'notes']:
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    for f in REPL_CODE:
        shutil.copy(os.path.join(ROOT, 'code', f), os.path.join(d, 'code', f))
    for f in REPL_DATA:
        shutil.copy(os.path.join(ROOT, 'data', f), os.path.join(d, 'data', f))
    removed = purge_tree(d)                    # registrants excluded at the author's request (code/exclusions.py)
    if removed:
        print('excluded registrants dropped from the package copy:', removed)
    open(os.path.join(d, 'README.md'), 'w').write(readme)
    z = os.path.join(DIST, 'replication_package.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for base, _, files in os.walk(d):
            for f in files:
                p = os.path.join(base, f)
                zf.write(p, arcname=os.path.join('replication', os.path.relpath(p, d)))
        for base in ['figures', 'sections/tables', 'notes']:
            zf.writestr(f'replication/{base}/.keep', '')
    return d, z


if __name__ == '__main__':
    import sys
    os.makedirs(DIST, exist_ok=True)
    print(build_arxiv())
    if len(sys.argv) > 1:
        print(build_replication(open(sys.argv[1]).read()))
