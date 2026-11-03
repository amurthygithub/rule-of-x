import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd, lib
V = lib.V; TAU = 0.18
def anchor(df, drop_flagged):
    d = df[df.period == '2023-25'].copy(); d['R'] = d.g + d.m_fcf_sbc; d = d.dropna(subset=['R'])
    G, p95 = d.g.median(), d.R.quantile(.95)
    top = d[d.R >= p95]; top = top[top.acq_flag == 0] if drop_flagged else top
    sig = (top.sm / top.rev).fillna(0.0); kg = top.capex_int.fillna(0.0); k = np.where(top.g > 0, kg / top.g, 0.0)
    Pi_ub = top.R - (top.m_fcf_sbc + (1 - TAU) * sig + kg + (1 - k) * G); Pi_lb = top.R - (top.m_fcf_sbc + kg + (1 - k) * G)
    return np.array([len(top), Pi_ub.median(), Pi_lb.median(), Pi_ub.median() / top.R.median(), Pi_lb.median() / top.R.median()])
rng = np.random.default_rng(15)
for vn, drop in [('E2', False), ('E1', True)]:
    est = anchor(V[vn], drop)
    bs = lib.boot(V[vn][V[vn].period == '2023-25'], lambda z: anchor(z, drop), 1000, rng)
    print(vn, 'n=%d  median Pi_ub %.1f [90%% %.1f, %.1f]  median Pi_lb %.1f [%.1f, %.1f]  transient share ub %.0f%% [%.0f, %.0f]  lb %.0f%% [%.0f, %.0f]' % (
        est[0], 100*est[1], 100*np.quantile(bs[:,1],.05), 100*np.quantile(bs[:,1],.95), 100*est[2], 100*np.quantile(bs[:,2],.05), 100*np.quantile(bs[:,2],.95),
        100*est[3], 100*np.quantile(bs[:,3],.05), 100*np.quantile(bs[:,3],.95), 100*est[4], 100*np.quantile(bs[:,4],.05), 100*np.quantile(bs[:,4],.95)))
