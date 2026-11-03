"""Extract a JSON payload returned by the browser tool (saved tool-result file) into a clean JSON file.
A payload keyed by CIK (companyfacts) loses the registrants excluded in code/exclusions.py.
Usage: python3 extract_browser_payload.py <tool_result_file> <PREFIX> <out_json>"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exclusions import is_excluded  # noqa: E402  registrants excluded at the author's request
src, prefix, out = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(src))
t = d[0]['text']
t = t.split('\n\n(captured at origin')[0]
s = json.loads(t)             # the returned JS string
assert s.startswith(prefix + ':'), s[:50]
payload = json.loads(s[len(prefix) + 1:])
if isinstance(payload, dict):
    payload = {k: v for k, v in payload.items() if not is_excluded(k)}
json.dump(payload, open(out, 'w'))
print('ok', type(payload).__name__, len(payload))
