"""Compare pinned outputs with reproduction; preserve NaN and array semantics."""
from pathlib import Path
import hashlib, json, math, sys
import numpy as np

root = Path(__file__).resolve().parents[1]
base, work = root/'pinned_snapshot', root/'work_pinned'
paths = sys.argv[1:] or ['notes/empirics_v3.json','notes/calibration_anchor_v3.json',
    'notes/frontier_slope_v3.json','notes/bootstrap_draws_v3.npz',
    'notes/open_questions/valuation.json','notes/open_questions/paths.json']
def walk(a,b,p,changes):
    if isinstance(a,dict) and isinstance(b,dict):
        for k in sorted(a.keys()|b.keys()):
            if k not in a or k not in b: changes.append({'path':p+'/'+k,'type':'key mismatch'})
            else:walk(a[k],b[k],p+'/'+k,changes)
    elif isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b):changes.append({'path':p,'type':'length mismatch','before':len(a),'after':len(b)})
        else:
            for i,(v,w) in enumerate(zip(a,b)):walk(v,w,p+f'/{i}',changes)
    elif isinstance(a,(int,float)) and isinstance(b,(int,float)):
        if math.isnan(a) and math.isnan(b):return
        if a!=b:changes.append({'path':p,'type':'numeric','before':a,'after':b,
                               'abs_diff':abs(a-b),'within_1e-10':math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10)})
    elif a!=b:changes.append({'path':p,'type':'value','before':a,'after':b})

results=[]
for f in paths:
    a,b=base/f,work/f
    if not (a.exists() and b.exists()):
        results.append({'path':f,'status':'missing','baseline_exists':a.exists(),'reproduced_exists':b.exists()});continue
    rec={'path':f,'bytes_identical':a.read_bytes()==b.read_bytes(),
         'baseline_sha256':hashlib.sha256(a.read_bytes()).hexdigest(),
         'reproduced_sha256':hashlib.sha256(b.read_bytes()).hexdigest()}
    if f.endswith('.json'):
        c=[];walk(json.loads(a.read_text()),json.loads(b.read_text()),'',c)
        rec.update(differences=c,difference_count=len(c),
                   outside_1e10_count=sum(x.get('type')!='numeric' or not x['within_1e-10'] for x in c))
    elif f.endswith('.npz'):
        aa,bb=np.load(a),np.load(b);rows=[]
        rec['array_keys_identical']=set(aa.files)==set(bb.files)
        for k in sorted(set(aa.files)&set(bb.files)):
            x,y=aa[k],bb[k];same=x.shape==y.shape
            row={'key':k,'shape':list(x.shape),'shape_match':same}
            if same and np.issubdtype(x.dtype,np.number):
                row.update(exact_equal_nan=bool(np.array_equal(x,y,equal_nan=True)),
                           equal_1e10_nan=bool(np.allclose(x,y,rtol=1e-10,atol=1e-10,equal_nan=True)),
                           max_abs_finite_difference=float(np.max(np.abs(x[np.isfinite(x)&np.isfinite(y)]-y[np.isfinite(x)&np.isfinite(y)]),initial=0)))
            elif same:row['exact_equal']=bool(np.array_equal(x,y))
            rows.append(row)
        rec['arrays']=rows
    results.append(rec)
target=root/'results/computational/reproduced_output_comparison.json'
target.write_text(json.dumps(results,indent=2)+'\n')
for rec in results:
    print(json.dumps({k:v for k,v in rec.items() if k not in ['differences','arrays']}))
    if rec.get('differences'):print(json.dumps(rec['differences'][:12],indent=2))
