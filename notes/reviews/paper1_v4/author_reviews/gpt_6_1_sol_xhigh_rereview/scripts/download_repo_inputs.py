"""Transfer explicitly selected GitHub file URLs; never persist URL capabilities."""
from pathlib import Path
import hashlib, json, shutil, sys, termios, urllib.request
root = Path(sys.argv[1]).resolve()
if sys.stdin.isatty():
    settings = termios.tcgetattr(0)
    settings[3] &= ~(termios.ECHO | termios.ICANON)
    settings[6][termios.VMIN] = 1
    settings[6][termios.VTIME] = 0
    termios.tcsetattr(0, termios.TCSANOW, settings)
print('ready', flush=True)
for line in sys.stdin:
    try:
        q = json.loads(line)
        if q.get('op') == 'close': break
        target = (root / q['path']).resolve()
        if not target.is_relative_to(root): raise ValueError('path outside snapshot')
        target.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(q['url'], timeout=120) as response, target.open('wb') as output:
            shutil.copyfileobj(response, output)
        b = target.read_bytes()
        observed = hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        if observed != q['sha']: raise ValueError('Git SHA mismatch')
        print(json.dumps({'path':q['path'], 'bytes':len(b), 'git_blob_sha':observed, 'verified':True}), flush=True)
    except Exception as exc:
        print(json.dumps({'path':q.get('path'), 'error_type':type(exc).__name__}), flush=True)
