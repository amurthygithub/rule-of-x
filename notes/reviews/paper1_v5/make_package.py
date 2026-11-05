#!/usr/bin/env python3
"""One package per outside reviewer for the second re-review, from the committed state of the repository (5 Nov 2026).

Writes dist/rereview2/:
  rereview2_<key>.zip    paper1.pdf, supplement.pdf, RESPONSE.md (that reviewer's response only), PROMPT.md (filled),
                         MANIFEST.txt (commit, SHA-256 of every file)
  repository.zip         git archive of the same commit (shared by all four; also branches main and review-round-3)
Stops if the working tree has uncommitted changes to tracked files, if the PDF snapshots differ from the built PDFs,
or if an excluded registrant would be shipped.
Run from the repository root:  python3 notes/reviews/paper1_v5/make_package.py
"""
import hashlib
import os
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OUT = os.path.join(ROOT, 'dist', 'rereview2')
# key: (model as addressed, folder of the first review in paper1_v3, folder of the re-review in paper1_v4)
REV = {'deepseek': ('DeepSeek V4 Pro (high effort)', 'deepseek_v4_pro_high', 'deepseek_v4_pro_high_rereview'),
       'gpt': ('GPT-6.1 Sol (extra-high effort)', 'gpt_6_1_sol_xhigh', 'gpt_6_1_sol_xhigh_rereview'),
       'glm': ('GLM 5.3 (high effort)', 'glm_5_3_high', 'glm_5_3_high_rereview'),
       'mistral': ('Mistral Large 4 (high effort)', 'mistral_large_4_high', 'mistral_large_4_high_rereview')}


def sh(*a):
    return subprocess.run(a, cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


dirty = sh('git', 'status', '--porcelain', '--untracked-files=no')
if dirty:
    sys.exit('commit first; tracked files differ from HEAD:\n' + dirty)
commit = sh('git', 'rev-parse', 'HEAD')
subprocess.run([sys.executable, os.path.join(ROOT, 'code', 'purge_excluded.py'), '--check'], cwd=ROOT, check=True)
for key, (_, f1, f2) in REV.items():
    for d in (os.path.join(ROOT, 'notes', 'reviews', 'paper1_v3', 'author_reviews', f1),
              os.path.join(ROOT, 'notes', 'reviews', 'paper1_v4', 'author_reviews', f2)):
        assert os.path.isdir(d), f'missing review folder {d}'
    assert os.path.exists(os.path.join(ROOT, 'notes', 'reviews', 'paper1_v4', f'response_{key}.md'))
os.makedirs(OUT, exist_ok=True)
repo = os.path.join(OUT, 'repository.zip')
sh('git', 'archive', '--format=zip', f'--prefix=rule-of-x-{commit[:7]}/', '-o', repo, commit)
pdf = {n: os.path.join(HERE, f) for n, f in (('paper1.pdf', 'paper1_v5.pdf'), ('supplement.pdf', 'supplement_v5.pdf'))}
assert sha(pdf['paper1.pdf']) == sha(os.path.join(ROOT, 'paper1', 'paper1.pdf')), 'snapshot differs from paper1/paper1.pdf'
assert sha(pdf['supplement.pdf']) == sha(os.path.join(ROOT, 'paper1', 'supplement.pdf')), 'snapshot differs from paper1/supplement.pdf'
prompt = open(os.path.join(HERE, 'rereview2_prompt.md'), encoding='utf-8').read()
for key, (model, f1, f2) in REV.items():
    filled = (prompt.replace('{MODEL}', model).replace('{KEY}', key).replace('{FOLDER1}', f1).replace('{FOLDER2}', f2)
              .replace('{COMMIT}', commit))
    assert '{' not in filled.replace('{,}', ''), 'unfilled placeholder'
    members = {'paper1.pdf': open(pdf['paper1.pdf'], 'rb').read(), 'supplement.pdf': open(pdf['supplement.pdf'], 'rb').read(),
               'RESPONSE.md': open(os.path.join(HERE, f'response_{key}.md'), 'rb').read(), 'PROMPT.md': filled.encode()}
    man = [f'Second re-review package for {model}',
           f'Repository commit: {commit} (branches main and review-round-3, github.com/amurthygithub/rule-of-x)',
           f'repository.zip (shared, separate file): SHA-256 {sha(repo)}', '']
    man += [f'{n}: SHA-256 {hashlib.sha256(b).hexdigest()}, {len(b):,} bytes' for n, b in members.items()]
    members['MANIFEST.txt'] = ('\n'.join(man) + '\n').encode()
    z = os.path.join(OUT, f'rereview2_{key}.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as fh:
        for n, b in members.items():
            fh.writestr(f'rereview2_{key}/{n}', b)
    print(f'wrote {os.path.relpath(z, ROOT)} ({os.path.getsize(z) / 1e6:.1f} MB)')
print(f'wrote {os.path.relpath(repo, ROOT)} ({os.path.getsize(repo) / 1e6:.1f} MB) at commit {commit}')
