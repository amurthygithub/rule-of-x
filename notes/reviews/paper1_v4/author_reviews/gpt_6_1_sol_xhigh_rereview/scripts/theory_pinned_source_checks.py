"""Read-only targeted reconstruction from the pinned snapshot, after Part B freeze."""
from pathlib import Path
import csv, json, math, re, hashlib
import numpy as np

root=Path(__file__).resolve().parents[1]
repo=root/'pinned_snapshot'
panel=list(csv.DictReader((repo/'data/panel_v3.csv').open()))
slopes=json.loads((repo/'notes/frontier_slope_v3.json').read_text())['central']
cal=json.loads((repo/'notes/calibration_results.json').read_text())['r3']['ell_psi_cone']
grid=np.arange(13)/20
rows=[]
for basis,col in [('op','m_op'),('cash','m_fcf_sbc')]:
    growth=np.array([float(p['g']) for p in panel if p['g'] not in ('','nan') and p[col] not in ('','nan')])
    b=abs(slopes[basis]['E1']['est'])
    for alpha in [.25,.30,.35,.45]:
        beta=1/alpha
        # Quantile is calculated on transformed margins, not by applying the
        # nonlinear margin function to an interpolated empirical growth quantile.
        values=np.array([np.quantile(-growth[growth>=t]**beta,.9) for t in grid])
        S=-float(np.sum((grid-grid.mean())*(values-values.mean()))/np.sum((grid-grid.mean())**2))
        A=b/S
        steep=beta*A*.6**(beta-1)
        old=cal['by_basis'][basis]['by_alpha'][f'{alpha:.2f}']
        assert math.isclose(steep,old['steepest'],abs_tol=1e-10)
        assert math.isclose(steep/b,old['multiplier'],abs_tol=1e-10)
        rows.append({'basis':basis,'alpha':alpha,'observed_cone_slope':-b,'multiplier':steep/b,'steepest_at_window_end':steep,
                     'growth_values_used':len(growth),'values_above_window':int((growth>.6).sum()),'max_growth':float(growth.max()),
                     'implied_frontier_slope_at_max_growth':beta*A*growth.max()**(beta-1)})

def remove_comments(s):
    out=[];i=0;depth=0
    while i<len(s):
        if s[i:i+2]=='/-':depth+=1;i+=2
        elif depth and s[i:i+2]=='-/':depth-=1;i+=2
        elif depth:i+=1
        elif s[i:i+2]=='--':
            j=s.find('\n',i);i=len(s) if j<0 else j
        else:out.append(s[i]);i+=1
    assert depth==0
    return ''.join(out)
formal=repo/'formal'
files=list(formal.rglob('*.lean'))
clean='\n'.join(remove_comments(p.read_text()) for p in files)
source_scan={'source_files':len(files),'main_axiom_prints':len(re.findall(r'^#print axioms ',(formal/'RuleOfX/Axioms.lean').read_text(),re.M)),
             'new_axiom_declarations':re.findall(r'^\s*(?:axiom|constant|opaque)\s+\S+',clean,re.M),
             'placeholder_tokens':re.findall(r'\b(?:sorry|admit|sorryAx)\b',clean),
             'scope':'Static text scan; not a Lean kernel or elaboration check.'}
result={'commit':'eb7537bee7585f2902304f62a722edea6ced8539','seed':None,'method':'Deterministic cone reconstruction and source scan',
        'input_hashes':{str(p.relative_to(repo)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [repo/'data/panel_v3.csv',repo/'notes/frontier_slope_v3.json',repo/'notes/calibration_results.json']},
        'cone_reconstruction':rows,'formal_source_scan':source_scan}
(root/'results/theory_pinned_source_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
