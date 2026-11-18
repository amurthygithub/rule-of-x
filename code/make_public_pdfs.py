#!/usr/bin/env python3
"""Build the copies of Part 1 that the repository hosts for readers, under the paper's title (17 Nov 2026).

The two PDFs link to each other by file name (xr-hyper). The pipeline's copies are paper1/paper1.pdf and
paper1/supplement.pdf; the hosted copies in papers/ carry the paper's title, so they are built from a scratch copy of
HEAD whose two \\externaldocument lines name the hosted files, through code/build_paper1.sh with NO_COPY=1. Nothing
else changes: the script checks that the text of each hosted copy equals the text of the pipeline's copy.

Usage: python3 code/make_public_pdfs.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = {'paper1': 'Rule-of-40-as-a-Price-Line.pdf',
         'supplement': 'Rule-of-40-as-a-Price-Line-Supplementary-Appendix.pdf'}
OTHER = {'paper1': 'supplement', 'supplement': 'paper1'}

scr = tempfile.mkdtemp(prefix='public_pdfs_')
src = os.path.join(scr, 'src')
os.makedirs(src)
subprocess.run(f'git -C "{ROOT}" archive HEAD sections paper1 figures | tar -x -C "{src}"', shell=True, check=True)
for d in NAMES:
    p = os.path.join(src, 'paper1', f'{d}.tex')
    t = open(p).read()
    old = f'\\externaldocument[][nocite]{{{OTHER[d]}}}[{OTHER[d]}.pdf]'
    assert t.count(old) == 1, f'{d}: {old} not found once'
    open(p, 'w').write(t.replace(old, f'\\externaldocument[][nocite]{{{OTHER[d]}}}[{NAMES[OTHER[d]]}]'))
build = os.path.join(scr, 'build')
r = subprocess.run(['bash', os.path.join(ROOT, 'code', 'build_paper1.sh'), build],
                   env=dict(os.environ, PAPER_ROOT=src, NO_COPY='1'), capture_output=True, text=True)
print(r.stdout.strip())
if r.returncode:
    sys.exit(r.stderr)


def text(pdf):
    return subprocess.run(['pdftotext', '-layout', pdf, '-'], capture_output=True, text=True, check=True).stdout


out = os.path.join(ROOT, 'papers')
os.makedirs(out, exist_ok=True)
for d, name in NAMES.items():
    built = os.path.join(build, f'{d}.pdf')
    assert text(built) == text(os.path.join(ROOT, 'paper1', f'{d}.pdf')), f'{d}: text differs from paper1/{d}.pdf'
    shutil.copy(built, os.path.join(out, name))
    print(f'papers/{name}: same text as paper1/{d}.pdf')
shutil.rmtree(scr)
