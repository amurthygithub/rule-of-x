"""Run an exact author command on an isolated checkout and preserve its evidence."""
from pathlib import Path
from datetime import datetime, timezone
import json, os, platform, subprocess, sys, time

root = Path(__file__).resolve().parents[1]
name, *command = sys.argv[1:]
out = root / 'results' / 'computational' / name
out.mkdir(parents=True, exist_ok=True)
work = (root / 'work_pinned' / os.environ.get('REVIEW_COMMAND_CWD', '')).resolve()
start = datetime.now(timezone.utc)
record = dict(name=name, command=command, cwd=str(work), start_utc=start.isoformat(),
              python_driver=sys.executable, platform=platform.platform(),
              env={k: v for k, v in os.environ.items() if k.startswith(('V3_', 'OMP_', 'OPENBLAS_', 'MKL_', 'NO_COPY', 'MPLBACKEND', 'LEAN_', 'REVIEW_COMMAND_')) or k=='LD_PRELOAD'},
              commit='eb7537bee7585f2902304f62a722edea6ced8539', status='running')
(out / 'run.json').write_text(json.dumps(record, indent=2)+'\n')
t0 = time.perf_counter()
with (out/'stdout.txt').open('w') as stdout, (out/'stderr.txt').open('w') as stderr:
    process = subprocess.run(command, cwd=work, stdout=stdout, stderr=stderr)
record.update(exit_code=process.returncode, elapsed_seconds=time.perf_counter()-t0,
              finish_utc=datetime.now(timezone.utc).isoformat(), status='completed')
(out / 'run.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps(record, indent=2))
sys.exit(process.returncode)
