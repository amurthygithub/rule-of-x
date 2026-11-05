"""Record inputs/environment and run only our independent scripts on a copy.

This does not execute, stand in for, or certify the author's replication suite.
"""
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import hashlib, json, os, platform, shutil, subprocess, sys, time

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
RESULTS.mkdir(exist_ok=True)
expected = {
    'paper1.pdf': '9e986ecac307d445b0f9a636788100d8fc680f3a5508b609b430ab457788c55b',
    'supplement.pdf': '1da736731466b00d583ee0055480bae7ad809c114edb25ad232a6d8078f2b81f',
    'RESPONSE.md': 'b068918d515709ea3af8d99c1428094cec6ddbd3d85f9b190d5fe888d52845f1',
    'PROMPT.md': '4fc5f4065ec94a924672d7eedaf65fa6a2dec80298bf29dfa98417e4e80415fc',
}
inputs = []
for name, wanted in expected.items():
    path = ROOT / name
    if not path.exists():
        inputs.append({'name':name, 'expected_sha256':wanted, 'status':'not bundled in deliverable; place original input here to recheck'})
        continue
    observed = hashlib.sha256(path.read_bytes()).hexdigest()
    assert observed == wanted, (name, observed)
    inputs.append({'name':name, 'bytes':path.stat().st_size, 'sha256':observed, 'manifest_match':True})
archive = ROOT.parent / 'upload' / 'rereview_gpt.zip'
manifest = ROOT / 'MANIFEST.txt'
if manifest.exists():
    inputs.append({'name':'MANIFEST.txt', 'bytes':manifest.stat().st_size, 'sha256':hashlib.sha256(manifest.read_bytes()).hexdigest()})
if archive.exists():
    inputs.append({'name':'rereview_gpt.zip', 'bytes':archive.stat().st_size, 'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()})
utc = datetime.now(timezone.utc)
env = {'recorded_utc':utc.isoformat(), 'recorded_client_time':utc.astimezone(ZoneInfo('America/Los_Angeles')).isoformat(),
       'python':sys.version, 'python_executable':sys.executable, 'platform':platform.platform(),
       'tools':{n:shutil.which(n) for n in ['git','pdftotext','pdftoppm','pdflatex','latexmk','lean','lake']},
       'model_disclosure':'Codex, GPT-6-based according to session instructions; exact serving build and configured effort level not exposed. The prompt label GPT-6.2 Sol (extra-high) is not verified runtime metadata.',
       'delegation':'Four AI subreviews: mathematical theory; empirical methods; execution and stress tests; controls, finance units and primary sources. Same inherited backend, not independent external human referees.'}
(RESULTS/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
(RESULTS/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
scripts = ['theory_independent_checks.py','execution_checks.py','check_controls_and_cost_units.py','empirical_arithmetic.py']
runs = []
for name in scripts:
    start = time.perf_counter()
    proc = subprocess.run([sys.executable,str(ROOT/'scripts'/name)],cwd=ROOT,capture_output=True,text=True)
    duration = time.perf_counter()-start
    (RESULTS/(name.removesuffix('.py')+'.stdout.txt')).write_text(proc.stdout)
    (RESULTS/(name.removesuffix('.py')+'.stderr.txt')).write_text(proc.stderr)
    runs.append({'script':'scripts/'+name,'elapsed_seconds':round(duration,6),'exit_code':proc.returncode,
                 'scope':'independent printed-formula/source-unit checks, not author-pipeline reproduction'})
    if proc.returncode:
        raise RuntimeError(f'{name} failed: {proc.stderr}')
(RESULTS/'own_run_log.json').write_text(json.dumps(runs,indent=2)+'\n')
print(json.dumps({'input_hashes_checked':sum('manifest_match' in x for x in inputs),'independent_scripts_passed':len(runs),'run_times':runs},indent=2))
