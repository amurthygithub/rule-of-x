"""sha256 of every raw input file (excluding .git internals) -> data/raw/CHECKSUMS.sha256, plus git commit of each clone."""
import sys
sys.path.insert(0, '/home/claude/paper/code/data_part2')
import os
import subprocess
from common import RAW, sha256, save_meta

lines, commits = [], {}
for root, dirs, files in os.walk(RAW):
    dirs[:] = sorted(d for d in dirs if d != '.git')
    for f in sorted(files):
        p = os.path.join(root, f)
        if f == 'CHECKSUMS.sha256':
            continue
        lines.append(f'{sha256(p)}  {os.path.relpath(p, RAW)}  {os.path.getsize(p)}')
for d in sorted(os.listdir(RAW)):
    repo = os.path.join(RAW, d, 'repo')
    if os.path.isdir(os.path.join(repo, '.git')):
        out = subprocess.run(['git', '-C', repo, 'log', '-1', '--format=%H %ci'], capture_output=True, text=True).stdout.strip()
        url = subprocess.run(['git', '-C', repo, 'remote', 'get-url', 'origin'], capture_output=True, text=True).stdout.strip()
        commits[d] = f'{url} {out}'
with open(os.path.join(RAW, 'CHECKSUMS.sha256'), 'w') as fh:
    fh.write('# sha256  path-relative-to-data/raw  bytes\n')
    fh.write('\n'.join(lines) + '\n')
save_meta('raw_inputs', dict(n_files=len(lines), commits=commits))
print(len(lines), 'files hashed'); print(commits)
