"""Selection under E2: re-admit the excluded acquisition-affected firm-years with imputed organic growth
(acquired revenue = purchase price / price-to-revenue multiple M, half in the deal year and half in the next)."""
import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd, lib
P = lib.P.copy(); V = lib.V; core = lib.core
P['price'] = P.acq_pay.where(P.acq_pay.notna() & (P.acq_pay > 0), P.gw_jump.clip(lower=0) / 0.75)
P['price'] = P.price.fillna(0)
P['prev_price'] = P.groupby('cik').price.shift(1).where(P.consec, 0).fillna(0)
P['prev_now'] = P.groupby('cik').now25.shift(1).where(P.consec, False).fillna(False).astype(bool)
key = P.set_index(['cik', 'year'])[['price', 'prev_price', 'prev_now', 'now25']]
E1 = V['E1'].copy()
E1 = E1.join(key[['price', 'prev_price', 'prev_now']], on=['cik', 'year'])
def variant(M):
    v = E1.copy()
    acq_t = np.where(v.now25, 0.5 * v.price / M / v.rev_lag, 0.0)
    acq_c = np.where(v.prev_now, 0.5 * v.prev_price / M / v.rev_lag, 0.0)
    g_imp = v.g - acq_t - acq_c
    g_use = np.where(v.flag25, np.where(v.gorg25.notna() & v.flag25, v.gorg25, g_imp), v.g)
    v['g'] = g_use
    v = v[~v.unver & (v.g > -0.9) & (v.g < 5)].copy()
    v['R_op'] = v.g + v.m_op; v['R_cash'] = v.g + v.m_fcf_sbc
    return v
def stats_(v):
    out = {}
    for m in ['m_op', 'm_fcf_sbc']:
        d = v[['g', m]].dropna(); d = d[(d.g >= 0) & (d.g <= 0.6)]
        out['slope_' + m] = lib.qr_lp(d[m].values, d.g.values, 0.9)[1]
    for R in ['R_op', 'R_cash']:
        d = v[['lsize', R]].dropna()
        out['scale_' + R] = 100 * np.log(10) * lib.qr_lp(d[R].values, d.lsize.values, 0.95)[1]
        a = v.loc[v.period == '2023-25', R].dropna(); b = v.loc[v.period == '2016-19', R].dropna()
        out['p95chg_' + R] = 100 * (np.quantile(a, .95) - np.quantile(b, .95))
    return out
fl = E1[E1.flag25 & E1.gorg25.isna() & ~E1.unver]
print('excluded flagged firm-years:', len(fl), '; with a price measure in t or t-1:', int(((fl.now25 & (fl.price > 0)) | (fl.prev_now & (fl.prev_price > 0))).sum()))
rows = {'E1 (reported g, all)': stats_(V['E1'].assign(lsize=V['E1'].lsize)), 'E2 (paper)': stats_(V['E2']), 'E2x25 (exclusion)': stats_(V['E2x25'])}
for M in [1, 2, 4, 8]:
    v = variant(M)
    adj = (v.flag25 & v.gorg25.isna())
    rows[f'Imputed, M={M}'] = stats_(v)
    print(f'M={M}: re-admitted {int(adj.sum())} firm-years; median imputed acquired growth %.1f pts' % (100 * (E1.loc[v.index[adj], 'g'] - v.loc[adj, 'g']).median()))
df = pd.DataFrame(rows).T.round(2)
print(df.to_string())
