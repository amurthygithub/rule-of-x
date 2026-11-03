"""Check 7: firm-cluster bootstrap SE of the envelope slope; frontier score and slope excluding SIC 7370."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/paper/notes/referee3')
from r3lib import *

df = load()
def slope(gv, mv):
    phi = order_alpha(gv, mv); ok = ~np.isnan(phi)
    return np.polyfit(GRID[ok], phi[ok], 1)[0] if ok.sum() >= 2 else np.nan
rows = []
for m in ['m_op', 'm_fcf_sbc']:
    for p in PERIODS:
        d = df[df.period == p][['cik', 'g', m, 'sic']].dropna().reset_index(drop=True)
        rng = np.random.default_rng(71); idx = cluster_index(d.cik.values)
        bs = [slope(*(lambda ii: (d.g.values[ii], d[m].values[ii]))(cluster_draw(idx, rng))) for _ in range(400)]
        x = d[d.sic != 7370]
        rows.append(dict(m=m, p=p, slope=round(slope(d.g.values, d[m].values), 3), slope_se=round(float(np.nanstd(bs)), 3),
                         slope_ci90=[round(float(v), 2) for v in np.nanquantile(bs, [.05, .95])],
                         score_ex7370=round(100 * frontier_score(x.g.values, x[m].values)[0], 1),
                         slope_ex7370=round(slope(x.g.values, x[m].values), 3), n_ex7370=len(x)))
print(pd.DataFrame(rows).to_string())
