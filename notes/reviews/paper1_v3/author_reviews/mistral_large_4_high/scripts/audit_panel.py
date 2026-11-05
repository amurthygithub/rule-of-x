"""Independent re-computation of headline statistics directly from data/panel_v3.csv (E1/core).
Paper claims (macros): 95th pct fall 2016-19 -> 2023-25 on GAAP (R_op) and cash (R_fcf_sbc);
Psi_0.90 slope over g in [0,0.60] GAAP ~ -0.2; pass shares; spend ratio."""
import pandas as pd, numpy as np, json
df = pd.read_csv('/root/Paper Review/work/repo/rule-of-x/data/panel_v3.csv')
out = {}
out['n_rows'] = len(df); out['n_firms'] = int(df['cik'].nunique()); out['years'] = sorted(df['year'].unique().tolist())
core = df.copy()
out['period_counts'] = core['period'].value_counts().to_dict()
def p95(x): return float(np.nanpercentile(x, 95))
for col, name in [('R_op','GAAP'), ('R_fcf_sbc','cash')]:
    e = core[(core['period']=='2016-19')][col]; l = core[(core['period']=='2023-25')][col]
    out[f'top95_{name}'] = dict(early=p95(e.dropna()), late=p95(l.dropna()), fall=p95(e.dropna())-p95(l.dropna()))
# pass shares
for col, name in [('m_op','op'), ('m_adj','adj'), ('m_fcf','fcf'), ('m_fcf_sbc','cash')]:
    pass
out['pass40'] = {}
for col in ['R_op','R_adj','R_fcf','R_fcf_sbc']:
    out['pass40'][col] = float((core[col] >= 0.40).mean())
l25 = core[core['period']=='2023-25']
out['pass40_2023_25'] = {c: float((l25[c] >= 0.40).mean()) for c in ['R_op','R_adj','R_fcf','R_fcf_sbc']}
# Psi_0.90 slope: quantile of margin among firm-years with g >= g0, g0 in 0..0.60 step 0.05, LS slope
def psi90_slope(mcol):
    gs = np.arange(0, 0.60+1e-9, 0.05)
    pts = []
    for g0 in gs:
        sub = core[core['g'] >= g0]
        if len(sub) >= 30:
            pts.append((g0, float(np.nanquantile(sub[mcol], 0.90))))
    pts = np.array(pts)
    A = np.vstack([pts[:,0], np.ones(len(pts))]).T
    coef, *_ = np.linalg.lstsq(A, pts[:,1], rcond=None)
    return dict(slope=float(coef[0]), n_cells=len(pts), cells=[(float(g), float(v)) for g, v in pts])
out['psi90'] = {'GAAP': psi90_slope('m_op'), 'cash': psi90_slope('m_fcf_sbc')}
# local conditional quantile slope at 0.90 for 0<=g<=0.6 via statsmodels exact QR
try:
    import statsmodels.formula.api as smf
    sub = core[(core['g']>=0)&(core['g']<=0.6)]
    for mcol, nm in [('m_op','GAAP'), ('m_fcf_sbc','cash')]:
        m = smf.quantreg(f'{mcol} ~ g', sub).fit(q=0.90)
        out.setdefault('qr90', {})[nm] = float(m.params['g'])
except Exception as e:
    out['qr90_err'] = str(e)
# spend ratio: median over firm-years with g > year-median of sm_lag_share/(g - year-median)
core['med_g_year'] = core.groupby('year')['g'].transform('median')
fast = core[core['g'] > core['med_g_year']]
core['spend_ratio'] = np.where(core['g'] > core['med_g_year'], core['sm_lag_share']/(core['g']-core['med_g_year']), np.nan)
out['spend_ratio_median'] = float(core['spend_ratio'].median())
# within-firm FE slope margin ~ g with firm and year FE
try:
    import statsmodels.api as sm
    sub = core.dropna(subset=['m_op','g'])
    sub['cik_fe'] = sub['cik'].astype('category').cat.codes
    sub['yr_fe'] = sub['year'].astype('category').cat.codes
    X = pd.get_dummies(sub[['cik_fe','yr_fe']], drop_first=True).astype(float)
    X['g'] = sub['g'].values
    m = sm.OLS(sub['m_op'].values, X.values).fit()
    out['fe_slope_op'] = dict(coef=float(m.params[-1]), se=float(m.bse[-1]))
    X2 = X.copy(); X2['g'] = sub['g'].shift(-1).values  # lead
    sub2 = sub.copy(); sub2['g_lead'] = sub.groupby('cik')['g'].shift(-1)
    X2 = pd.get_dummies(sub2[['cik_fe','yr_fe']], drop_first=True).astype(float); X2['g_lead'] = sub2['g_lead'].values
    m2 = sm.OLS(sub2['m_op'].values, X2.values).fit(cov_type='cluster', cov_kwds={'groups': sub2['cik'].values})
    out['fe_lead_op'] = dict(coef=float(m2.params[-1]), se=float(m2.bse[-1]))
except Exception as e:
    out['fe_err'] = str(e)
# yearly 95th pct of R_op
out['yearly_top95_Rop'] = core.groupby('year')['R_op'].apply(lambda x: float(np.nanpercentile(x.dropna(),95))).to_dict()
json.dump(out, open('/root/tmp/review/out/audit_panel.json','w'), indent=1, default=float)
print(json.dumps({k:v for k,v in out.items() if k not in ('yearly_top95_Rop','psi90')}, indent=1, default=float))
print('psi90 slopes:', out['psi90']['GAAP']['slope'], out['psi90']['cash']['slope'])
print('yearly top95 R_op:', {int(k): round(v,3) for k,v in out['yearly_top95_Rop'].items()})
