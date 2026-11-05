"""Small independent firm-cluster bootstrap (B=200, own seed) for the two headline stats:
P95 fall of R_op and R_fcf_sbc (2016-19 -> 2023-25), and Psi_0.90 slope. Compare sign/CI with paper."""
import pandas as pd, numpy as np, json
df = pd.read_csv('/root/Paper Review/work/repo/rule-of-x/data/panel_v3.csv')
rng = np.random.default_rng(987654321)
firms = df['cik'].unique()
def psi90_slope(sub, mcol):
    gs = np.arange(0, 0.60+1e-9, 0.05); pts=[]
    for g0 in gs:
        x = sub[sub['g']>=g0][mcol].dropna()
        if len(x) >= 30: pts.append((g0, np.quantile(x, 0.90)))
    pts = np.array(pts)
    A = np.vstack([pts[:,0], np.ones(len(pts))]).T
    c,*_ = np.linalg.lstsq(A, pts[:,1], rcond=None)
    return c[0]
out = {'fall_op': [], 'fall_cash': [], 'psi_op': [], 'psi_cash': []}
B = 200
for b in range(B):
    drawn = rng.choice(firms, size=len(firms), replace=True)
    sub = df[df['cik'].isin(drawn)]
    e = sub[sub['period']=='2016-19']; l = sub[sub['period']=='2023-25']
    out['fall_op'].append(np.nanpercentile(e['R_op'],95) - np.nanpercentile(l['R_op'],95))
    out['fall_cash'].append(np.nanpercentile(e['R_fcf_sbc'],95) - np.nanpercentile(l['R_fcf_sbc'],95))
    out['psi_op'].append(psi90_slope(sub, 'm_op'))
    out['psi_cash'].append(psi90_slope(sub, 'm_fcf_sbc'))
res = {}
for k, v in out.items():
    v = np.array(v, float); v = v[~np.isnan(v)]
    res[k] = dict(n=len(v), mean=float(v.mean()), p5=float(np.percentile(v,5)), p95=float(np.percentile(v,95)))
print(json.dumps(res, indent=1))
print('paper: fall op -11.9 [-20.3,-6.4]; fall cash -12.7 [-21.6,-4.2]; psi op -0.22 [-0.42,-0.05]; psi cash -0.16 [-0.31,+0.01]')
json.dump(res, open('/root/tmp/review/out/audit_bootstrap.json','w'), indent=1)
