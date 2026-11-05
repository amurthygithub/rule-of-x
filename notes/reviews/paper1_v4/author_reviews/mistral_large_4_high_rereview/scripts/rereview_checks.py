"""Rearview verification scripts (re-review of v4 build, commit eb7537b).
Runs against /root/tmp/rereview/repo-v4 (worktree of eb7537b) and the shipped panel.
All seeds recorded. Outputs appended to ../results/*.json."""
import pandas as pd, numpy as np, json, re, os
REPO = '/root/tmp/rereview/repo-v4'
OUT = '/root/outputs/rereview-mistral-large-4/results'
os.makedirs(OUT, exist_ok=True)
res = {}

# 1. Headline re-estimation on the v4 panel (R2 applied to all 293 core registrants)
df = pd.read_csv(f'{REPO}/data/panel_v3.csv')
res['panel_v4'] = dict(rows=len(df), firms=int(df.cik.nunique()),
                       periods={k: int(v) for k, v in df.period.value_counts().items()})
def psi90(sub, mcol):
    pts = []
    for g0 in np.arange(0, 0.60+1e-9, 0.05):
        x = sub[sub.g >= g0][mcol].dropna()
        if len(x) >= 30: pts.append((g0, np.quantile(x, 0.90)))
    pts = np.array(pts); A = np.vstack([pts[:,0], np.ones(len(pts))]).T
    c, *_ = np.linalg.lstsq(A, pts[:,1], rcond=None); return float(c[0])
res['psi90_v4'] = dict(gaap=psi90(df, 'm_op'), cash=psi90(df, 'm_fcf_sbc'))
e = df[df.period == '2016-19']; l = df[df.period == '2023-25']
res['p95_fall_v4'] = dict(
    gaap_pts=float(np.nanpercentile(e.R_op, 95) - np.nanpercentile(l.R_op, 95)) * 100,
    cash_pts=float(np.nanpercentile(e.R_fcf_sbc, 95) - np.nanpercentile(l.R_fcf_sbc, 95)) * 100)
# anchor under both flag columns
p = l; R = (p.g + p.m_fcf_sbc).values; fin = np.isfinite(R); cut = np.quantile(R[fin], 0.95)
for flag in ['acq_flag_v3', 'acq_flag']:
    t = fin & (R >= cut) & (p[flag].values == 0)
    res.setdefault('anchor_v4', {})[flag] = dict(n=int(t.sum()), firms=int(len(np.unique(p.cik.values[t]))), cut=float(cut))

# 2. Within-firm slopes with the paper's stated g<=150% trim
import statsmodels.api as sm
def fe_slope(mcol, lead=False):
    sub = df.dropna(subset=[mcol, 'g']).copy()
    sub = sub[sub.g <= 1.5]
    if lead: sub['x'] = sub.groupby('cik')['g'].shift(-1)
    else: sub['x'] = sub.g
    sub = sub.dropna(subset=['x'])
    fe = pd.get_dummies(sub.cik.astype('category'), prefix='f', drop_first=True).astype(float)
    yr = pd.get_dummies(sub.year.astype('category'), prefix='y', drop_first=True).astype(float)
    X = pd.concat([fe, yr], axis=1); X['x'] = sub.x.values; X = sm.add_constant(X)
    m = sm.OLS(sub[mcol].values, X.values).fit(cov_type='cluster', cov_kwds={'groups': sub.cik.values})
    return float(m.params[-1]), float(m.bse[-1])
res['fe_v4'] = dict(op_now=fe_slope('m_op'), op_lead=fe_slope('m_op', True), cash_now=fe_slope('m_fcf_sbc'))

# 3. Compute-share floor units and G* range
tau, f, amin, cfull = 0.18, 0.025, 0.030, 0.06225897153079383
res['gstar_range'] = dict(cc_lo=1.2, gstar_at_lo=float((tau + (1-tau)*(0.012+f+amin+cfull))*100),
                          gstar_at_hi=float((tau + (1-tau)*(0.60+f+amin+cfull))*100))
# kappa check: runs cost 0.4-1.1% of human at $143.61/h; at 50% success, cost per completed task ~ 2x -> 0.8-2.2%; x labor share 60% -> 0.5-1.3%; paper uses KappaLo=2% -> 1.2%
res['cc_floor_check'] = dict(kappa_lo_pct=2.0, labor_share_pct=60, cc_lo_pct=1.2, note='cost/completed task = run cost / success rate; 1%/0.5 = 2%; x0.6 = 1.2% of revenue')

# 4. F-6 policy bound (solver-independent), worked example params
from scipy.integrate import solve_ivp
r, G, k, a, m0, sbar = 0.10, 0.04, 0.0, 0.3, 0.35, 0.5
Ca = (1-a)*a**(a/(1-a)); lam = (((r-G)*10.0 - m0)/Ca)**(1-a)/10.0
def value(s0, sig_fn, T=300):
    def rhs(t, z):
        s = z[0]; sig = sig_fn(s)
        D = lam*(1-s/sbar)*sig**a; m = m0 - sig - k*(G+D)
        return [s*D, np.exp(-(r-G)*t)*s*m]
    return solve_ivp(rhs, (0, T), [s0, 0.0], rtol=1e-11, atol=1e-13, max_step=0.25).y[1, -1]
res['f6_policy_bound'] = {str(s0): dict(no_spend=round(value(s0, lambda s: 0.0)/s0, 3),
                                        policy=round(value(s0, lambda s: 0.05 if s < 0.4 else 0.0)/s0, 3))
                          for s0 in [0.01, 0.1]}

# 5. Stress-test spot check: G* over the box corners for a few dims (tau, cc, f, amin, cfull)
import itertools
lo = dict(tau=0.15, cc=0.012, f=0.020, amin=0.015, cfull=0.0214)
hi = dict(tau=0.21, cc=0.60, f=0.030, amin=0.046, cfull=0.1647)
gs = [t + (1-t)*(c+f+am+cf) for t, c, f, am, cf in itertools.product(
    [lo['tau'], hi['tau']], [lo['cc'], hi['cc']], [lo['f'], hi['f']], [lo['amin'], hi['amin']], [lo['cfull'], hi['cfull']])]
res['gstar_corner_range_5dims'] = dict(lo=round(min(gs)*100, 1), hi=round(max(gs)*100, 1),
                                       note='paper full-box 51-dim range 19.6-94.5%; this 5-dim corner subset gives the span of the five main cost dims only')

# 6. Lean: no sorry/admit; theorem count
lean = ''
import glob
for f in glob.glob(f'{REPO}/formal/RuleOfX/*.lean') + glob.glob(f'{REPO}/formal/Checks/**/*.lean', recursive=True):
    lean += open(f).read()
res['lean'] = dict(theorems_lemmas=len(re.findall(r'^(?:theorem|lemma)\s', lean, re.M)),
                   sorry=len(re.findall(r'\bsorry\b', lean)), admit=len(re.findall(r'\badmit\b', lean)),
                   sorryAx_mentions=lean.count('sorryAx'))
json.dump(res, open(f'{OUT}/rereview_checks.json', 'w'), indent=1, default=float)
print(json.dumps(res, indent=1, default=float))
