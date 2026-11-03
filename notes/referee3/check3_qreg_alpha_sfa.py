"""Check 3: quantile-regression specification; growth-spend elasticity alpha; implied lambda*h; SFA diagnostics."""
import json, sys, warnings
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats, optimize
sys.path.insert(0, '/home/claude/paper/notes/referee3')
from r3lib import *
warnings.filterwarnings('ignore')

df = load(); out = {}
df['post'] = (df.year >= 2023).astype(int); df['g2'] = df.g ** 2; df['lsize'] = np.log(df.rev_lag / 1e9)

# ---------------- (3) quantile regressions
def qr_boot(form, d, q=0.90, B=200, seed=1):
    fit = smf.quantreg(form, d).fit(q=q, max_iter=5000)
    rng = np.random.default_rng(seed); idx = cluster_index(d.cik.values); bs = []
    for _ in range(B):
        try:
            bs.append(smf.quantreg(form, d.iloc[cluster_draw(idx, rng)]).fit(q=q, max_iter=2000).params.values)
        except Exception:
            pass
    se = np.array(bs).std(axis=0)
    return {k: (round(float(b), 3), round(float(s), 3)) for k, b, s in zip(fit.params.index, fit.params.values, se)}

print('=== QR specification variants (2016-25) ===')
qv = {}
excl = df.name.str.contains('AppLovin|Palantir', case=False, na=False)
for m in ['m_op', 'm_fcf', 'm_fcf_sbc']:
    base = df[df.year >= 2016][['cik', 'name', 'g', 'g2', 'post', 'lsize', m]].dropna()
    specs = {
        'baseline (paper)': (base[base.g <= 1.5], f'{m} ~ g + g2 + post + post:g + lsize', 0.90),
        'no size control': (base[base.g <= 1.5], f'{m} ~ g + g2 + post + post:g', 0.90),
        'g in [0,1]': (base[(base.g >= 0) & (base.g <= 1.0)], f'{m} ~ g + g2 + post + post:g + lsize', 0.90),
        'linear g, g in [0,0.6]': (base[(base.g >= 0) & (base.g <= 0.6)], f'{m} ~ g + post + post:g + lsize', 0.90),
        'tau=0.95': (base[base.g <= 1.5], f'{m} ~ g + g2 + post + post:g + lsize', 0.95),
        'drop AppLovin, Palantir': (base[(base.g <= 1.5) & ~excl.loc[base.index]], f'{m} ~ g + g2 + post + post:g + lsize', 0.90),
    }
    qv[m] = {}
    for nm, (d, form, q) in specs.items():
        r = qr_boot(form, d.reset_index(drop=True), q=q, B=150)
        keep = {k: v for k, v in r.items() if k in ['g', 'g2', 'post', 'post:g', 'lsize']}
        # marginal effect of g at g=0.3 (pre-period) and joint
        me = keep['g'][0] + (2 * 0.3 * keep['g2'][0] if 'g2' in keep else 0)
        keep['dm/dg at g=0.3'] = round(me, 3); keep['n'] = len(d)
        qv[m][nm] = keep
        print(m, nm, keep)
out['qreg_variants'] = qv

# ---------------- (4) growth-spend elasticity
print('\n=== alpha: growth-spend elasticity ===')
df['G_t'] = df.groupby('year')['g'].transform('median')
base = df[['cik', 'name', 'year', 'g', 'G_t', 'sm_lag_share', 'acq_flag', 'sm_share']].dropna(subset=['cik', 'year', 'g', 'G_t', 'sm_lag_share', 'acq_flag'])
base = base[(base.sm_lag_share > 0.01) & (base.sm_lag_share < 1.5) & (base.acq_flag == 0)].copy()
base['lx'] = np.log(base.sm_lag_share)
sel = base[base.g > base.G_t].copy(); sel['ly'] = np.log(sel.g - sel.G_t)
e_pool = smf.ols('ly ~ lx + C(year)', sel).fit(cov_type='cluster', cov_kwds={'groups': sel['cik']})
e_fe = smf.ols('ly ~ lx + C(year) + C(cik)', sel).fit(cov_type='cluster', cov_kwds={'groups': sel['cik']})
e_nofe = smf.ols('ly ~ lx', sel).fit(cov_type='cluster', cov_kwds={'groups': sel['cik']})
A = {}
A['replicate_pooled'] = (round(e_pool.params['lx'], 3), round(e_pool.bse['lx'], 3), int(e_pool.nobs))
A['replicate_fe'] = (round(e_fe.params['lx'], 3), round(e_fe.bse['lx'], 3))
A['resid_sd_pooled'] = round(float(np.std(e_pool.resid)), 3)
A['singletons_in_fe'] = int((sel.groupby('cik').size() == 1).sum())
# implied lambda*h: model log(Delta)=log(lh)+alpha*log(sigma); geometric-mean vs Duan-smeared mean, using no-year-FE fit
for a_ in [float(e_nofe.params['lx']), 0.20, 0.25, 0.43]:
    u = sel.ly - a_ * sel.lx
    lh_geo = float(np.exp(u.mean())); smear = float(np.mean(np.exp(u - u.mean())))
    A[f'lambda_h at alpha={a_:.3f}'] = dict(geometric=round(lh_geo, 3), duan_smeared_mean=round(lh_geo * smear, 3), smear_factor=round(smear, 2),
                                            growth_bought_at_sigma035_geo=round(lh_geo * 0.35 ** a_, 3))
A['nofe_alpha'] = (round(e_nofe.params['lx'], 3), round(e_nofe.bse['lx'], 3))
# alternative excess-growth baselines (less truncation): G_t = year p25 / p10
for qq in [0.25, 0.10]:
    b2 = base.copy(); b2['Gq'] = df.loc[b2.index].groupby('year')['g'].transform(lambda x: x.quantile(qq))
    b2['Gq'] = df.groupby('year')['g'].transform(lambda x: x.quantile(qq)).loc[b2.index]
    s2 = b2[b2.g > b2.Gq].copy(); s2['ly'] = np.log(s2.g - s2.Gq)
    f2 = smf.ols('ly ~ lx + C(year)', s2).fit(cov_type='cluster', cov_kwds={'groups': s2['cik']})
    A[f'pooled_alpha_baseline_p{int(qq*100)}'] = (round(f2.params['lx'], 3), round(f2.bse['lx'], 3), int(f2.nobs))
# NLS on all organic firm-years without truncation: g = G_t + lam * sigma^alpha
yrs = sorted(base.year.unique()); Y = base.g.values; S = base.sm_lag_share.values; yi = np.searchsorted(yrs, base.year.values)
def resid(th):
    lam, al = th[0], th[1]; Gy = th[2:]
    return Y - Gy[yi] - lam * S ** al
th0 = np.r_[0.3, 0.3, np.zeros(len(yrs))]
nls = optimize.least_squares(resid, th0, loss='soft_l1', f_scale=0.2)
# cluster bootstrap for NLS alpha
rng = np.random.default_rng(31); idx = cluster_index(base.cik.values); bsa = []
for _ in range(200):
    ii = cluster_draw(idx, rng); Yb, Sb, yib = Y[ii], S[ii], yi[ii]
    rr = optimize.least_squares(lambda th: Yb - th[2:][yib] - th[0] * Sb ** th[1], nls.x, loss='soft_l1', f_scale=0.2)
    bsa.append(rr.x[:2])
bsa = np.array(bsa)
A['NLS_all_organic (robust soft-L1)'] = dict(lam=round(nls.x[0], 3), alpha=round(nls.x[1], 3), alpha_ci90=[round(x, 3) for x in np.quantile(bsa[:, 1], [.05, .95])],
                                             lam_ci90=[round(x, 3) for x in np.quantile(bsa[:, 0], [.05, .95])], n=len(Y))
# within-firm first-difference in levels of growth vs change in lagged S&M share
base_s = base.sort_values(['cik', 'year']).copy()
base_s['dg'] = base_s.groupby('cik').g.diff(); base_s['dlx'] = base_s.groupby('cik').lx.diff()
fd = base_s.dropna(subset=['dg', 'dlx'])
ffd = smf.ols('dg ~ dlx + C(year)', fd).fit(cov_type='cluster', cov_kwds={'groups': fd['cik']})
A['FD: d g on d log sigma_{t-1}'] = (round(ffd.params['dlx'], 3), round(ffd.bse['dlx'], 3), int(ffd.nobs))
# model FOC level implication: sigma* = alpha (X-k) Delta*  ->  alpha = sigma / ((X-k) Delta)
ratio = (sel.sm_lag_share / (sel.g - sel.G_t))
A['implied alpha from FOC, X=1,k=0: median sigma/Delta'] = round(float(ratio.median()), 2)
A['implied alpha from FOC, X=2.5: median sigma/(2.5 Delta)'] = round(float((ratio / 2.5).median()), 2)
A['share of selected obs with sigma/Delta > 1'] = round(float((ratio > 1).mean()), 2)
# simulation: model with optimizing firms + classical measurement error in sigma -> what does the paper's regression return?
rng = np.random.default_rng(41); sims = []
for true_alpha in [0.25, 0.45]:
    for me_sd in [0.0, 0.5]:
        bb = []
        for _ in range(200):
            n = 3000; ell = np.exp(rng.normal(np.log(0.3), 0.6, n))
            sig = (true_alpha * ell) ** (1 / (1 - true_alpha))          # X=1, k=0 optimum
            Dl = ell * sig ** true_alpha * np.exp(rng.normal(0, 0.5, n))  # growth noise
            sig_obs = sig * np.exp(rng.normal(0, me_sd, n))
            G = 0.0; g = G + Dl
            med = np.median(g)
            # mimic selection g > median and log Delta measured against median
            s_ = g > med
            yv = np.log(g[s_] - med); xv = np.log(sig_obs[s_])
            bb.append(np.polyfit(xv, yv, 1)[0])
        sims.append(dict(true_alpha=true_alpha, meas_err_sd=me_sd, est_mean=round(float(np.mean(bb)), 3)))
A['sim_optimizing_firms'] = sims
for k, v in A.items(): print(k, v)
out['alpha'] = A

# ---------------- (5) SFA diagnostics
print('\n=== SFA diagnostics ===')
def sfa(y, X):
    n, k = X.shape; b0 = np.linalg.lstsq(X, y, rcond=None)[0]
    def nll(th):
        b = th[:k]; su, sv = np.exp(th[k]), np.exp(th[k + 1]); e = y - X @ b; s = np.sqrt(su ** 2 + sv ** 2); lam = su / sv
        return -(np.log(2) - np.log(s) + stats.norm.logpdf(e / s) + stats.norm.logcdf(-e * lam / s)).sum()
    r = optimize.minimize(nll, np.r_[b0, np.log(0.2), np.log(0.1)], method='BFGS')
    return float(np.exp(r.x[k])), float(np.exp(r.x[k + 1]))
S = {}
stay = set(df[df.period == '2010-15'].cik) & set(df[df.period == '2023-25'].cik)
for m in ['m_op', 'm_fcf_sbc']:
    for p in PERIODS:
        d = df[df.period == p][['cik', 'g', m, 'lsize']].dropna(); d = d[(d.g <= 1.5) & (d[m] > -1.5)]
        X = np.c_[np.ones(len(d)), d.g, d.g ** 2]
        ols_res = d[m].values - X @ np.linalg.lstsq(X, d[m].values, rcond=None)[0]
        su, sv = sfa(d[m].values, X)
        Xs = np.c_[X, d.lsize]; su_s, _ = sfa(d[m].values, Xs)
        db = d[d.cik.isin(stay)]; Xb = np.c_[np.ones(len(db)), db.g, db.g ** 2]; su_b, _ = sfa(db[m].values, Xb)
        R = d.g + d[m]
        S[f'{m}_{p}'] = dict(n=len(d), sigma_u=round(su, 3), sigma_v=round(sv, 3), resid_skew=round(float(stats.skew(ols_res)), 2),
                            sigma_u_with_size=round(su_s, 3), sigma_u_stayers=round(su_b, 3), n_stayers=len(db),
                            m_p95_minus_p50=round(float(d[m].quantile(.95) - d[m].median()), 3),
                            share_m_below_minus20=round(float((d[m] < -0.2).mean()), 3))
        print(m, p, S[f'{m}_{p}'])
out['sfa'] = S
json.dump(out, open('/home/claude/paper/notes/referee3/check3_results.json', 'w'), indent=1, default=float)
