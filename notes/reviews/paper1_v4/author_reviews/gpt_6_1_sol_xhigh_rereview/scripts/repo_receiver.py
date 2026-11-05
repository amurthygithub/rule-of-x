"""Receive connector-fetched bytes into an isolated snapshot; verify Git blob IDs.

Input is JSON lines on stdin. No network credentials are accepted or recorded.
"""
import base64, hashlib, json, os, pathlib, sys, termios
root=pathlib.Path(sys.argv[1]).resolve();root.mkdir(parents=True,exist_ok=True)
if os.isatty(0):
    settings=termios.tcgetattr(0)
    settings[3] &= ~(termios.ECHO | termios.ICANON)
    settings[6][termios.VMIN]=1;settings[6][termios.VTIME]=0
    termios.tcsetattr(0,termios.TCSANOW,settings)
print(json.dumps({'ready':str(root)}),flush=True)
for line in sys.stdin:
    try:
        q=json.loads(line)
        if q.get('op')=='close':
            print(json.dumps({'closed':True}),flush=True);break
        p=(root/q['path']).resolve()
        if not p.is_relative_to(root):raise ValueError('path outside snapshot')
        p.parent.mkdir(parents=True,exist_ok=True)
        raw=base64.b64decode(q['data']) if q['encoding']=='base64' else q['data'].encode('utf-8')
        with p.open('wb' if q.get('first') else 'ab') as f:f.write(raw)
        result={'path':q['path'],'written':len(raw),'final':bool(q.get('final'))}
        if q.get('final'):
            content=p.read_bytes();blob=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
            if blob!=q['sha']:raise ValueError('Git blob SHA mismatch')
            os.chmod(p,0o755 if q.get('mode')=='100755' else 0o644)
            result.update(bytes=len(content),git_blob_sha=blob,verified=True)
        print(json.dumps(result),flush=True)
    except Exception as e:
        print(json.dumps({'error':str(e)}),flush=True)
