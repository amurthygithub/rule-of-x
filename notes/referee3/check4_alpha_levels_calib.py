"""Check 4: (a) levels relation between growth and lagged S&M share (binned, OLS loss NLS);
(b) model-consistency of spend levels; (c) calibration sensitivity of Table calib to alpha in [0.2, 0.45]."""
import json, sys
import numpy as np, pandas as pd
from scipy import optimize
from scipy.optimize import brentq
sys.path.insert(0, '/home/claude/paper/notes/referee3')
from r3lib import *

df = load(); out = {}
df['G_t'] = df.groupby('year')['g'].transform('median')
b = df[['cik', 'year', 'g', 'G_t', 'sm_lag_share', 'acq_flag']].dropna()
b = b[(b.sm_lag_share > 0.01) & (b.sm_lag_share < 1.5) & (b.acq_flag == 0)].copy()
b['exc'] = b.g - b.G_t
b['bin'] = pd.cut(b.sm_lag_share, [0, .1, .2, .3, .4, .5, .7, 1.5])
t = b.groupby('bin', observed=True).agg(n=('g', 'size'), mean_exc=('exc', 'mean'), med_exc=('exc', 'median'), q75_exc=('exc', lambda x: x.quantile(.75)))
print('(a) excess growth over year median by lagged S&M share (organic):'); print(t.round(3).to_string())
out['binned'] = {str(k): v for k, v in t.round(4).to_dict(orient='index').items()}
# log-log on bin medians where positive
# NLS with plain least squares on growth level, g <= 1.5
bb = b[b.g <= 1.5]
yrs = sorted(bb.year.unique()); yi = np.searchsorted(yrs, bb.year.values); Y = bb.g.values; S = bb.sm_lag_share.values
for loss in ['linear', 'soft_l1']:
    r = optimize.least_squares(lambda th: Y - th[2:][yi] - th[0] * S ** th[1], np.r_[0.3, 0.5, np.zeros(len(yrs))], loss=loss, f_scale=0.2,
                               bounds=(np.r_[0, 0.01, -np.ones(len(yrs))], np.r_[5, 5, np.ones(len(yrs))]))
    out[f'nls_{loss}'] = dict(lam=round(r.x[0], 3), alpha=round(r.x[1], 3))
    print('NLS', loss, out[f'nls_{loss}'])
# (b) model-consistency: optimal spend at the calibrated parameters vs observed spend
for a_, lh in [(0.25, 0.25), (0.25, 0.15), (0.45, 0.33), (0.20, 0.24)]:
    sig = (a_ * lh) ** (1 / (1 - a_)); D = sig / a_
    out[f'opt_spend_alpha{a_}_lh{lh}'] = dict(sigma_star=round(sig, 4), Delta_star=round(D, 3))
    print(f'alpha={a_}, lh={lh}: sigma*={sig:.4f}, Delta*={D:.3f}')
print('observed median lagged S&M share (organic, g>median):', round(float(b[b.g > b.G_t].sm_lag_share.median()), 3),
      ' all:', round(float(b.sm_lag_share.median()), 3))
out['obs_sm_median'] = float(b.sm_lag_share.median())

# (c) calibration sensitivity
def r_star(m0, G, alpha, lam_h, k=0.0, X=1.0):
    if X <= k: return m0 + (X - k) * G, G
    D = lam_h ** (1 / (1 - alpha)) * (alpha * (X - k)) ** (alpha / (1 - alpha))
    return m0 + (X - k) * G + (1 - alpha) * (X - k) * D, G + D
H = {'2025 (calibrated)': dict(m0=(0.28, 0.28), G=(0.10, 0.10), lam_exc=(1.0, 1.5)),
     '2028': dict(m0=(0.30, 0.40), G=(0.10, 0.20), lam_exc=(1.5, 2.5)),
     '2031': dict(m0=(0.40, 0.55), G=(0.08, 0.20), lam_exc=(1.0, 2.0)),
     '2036': dict(m0=(0.45, 0.64), G=(0.05, 0.30), lam_exc=(0.5, 1.5))}
rows = []
for a_ in [0.20, 0.25, 0.30, 0.35, 0.45]:
    for h, p in H.items():
        typ = [r_star(p['m0'][i], p['G'][i], a_, 0.25)[0] for i in (0, 1)]
        exc = [r_star(p['m0'][i], p['G'][i], a_, p['lam_exc'][i])[0] for i in (0, 1)]
        exc_k = [r_star(p['m0'][i], p['G'][i], a_, p['lam_exc'][i], k=0.5)[0] for i in (0, 1)]
        gx = [r_star(p['m0'][i], p['G'][i], a_, p['lam_exc'][i])[1] for i in (0, 1)]
        rows.append(dict(alpha=a_, horizon=h, typical=f'{100*typ[0]:.0f}-{100*typ[1]:.0f}', exceptional=f'{100*exc[0]:.0f}-{100*exc[1]:.0f}',
                         exc_k05=f'{100*exc_k[0]:.0f}-{100*exc_k[1]:.0f}', g_star_exc=f'{100*gx[0]:.0f}-{100*gx[1]:.0f}'))
    lam1000 = brentq(lambda lh: r_star(0.5, 0.2, a_, lh)[0] - 10.0, 0.05, 1e4)
    lam100 = brentq(lambda lh: r_star(0.28, 0.10, a_, lh)[0] - 1.0, 0.01, 1e3)
    rows.append(dict(alpha=a_, horizon='lam_h for R*=1000 (m0=.5,G=.2)', typical=f'{lam1000:.1f}', exceptional=f'lam_h for R*=100 (2025): {lam100:.2f}', exc_k05='', g_star_exc=''))
ct = pd.DataFrame(rows); print('\n(c) calibration sensitivity, lambda*h held at paper values'); print(ct.to_string())
out['calib_sens_fixed_lh'] = rows
# re-anchored: hold the 2025 exceptional range fixed in *score* (85-119), solve lambda*h at each alpha, then propagate the ratio of lam_exc to 2025 anchor
rows2 = []
for a_ in [0.20, 0.25, 0.30, 0.35, 0.45]:
    lo = brentq(lambda lh: r_star(0.28, 0.10, a_, lh)[0] - 0.852, 0.01, 100); hi = brentq(lambda lh: r_star(0.28, 0.10, a_, lh)[0] - 1.191, 0.01, 100)
    sc = (lo / 1.0 + hi / 1.5) / 2
    for h, p in H.items():
        exc = [r_star(p['m0'][i], p['G'][i], a_, p['lam_exc'][i] * sc)[0] for i in (0, 1)]
        rows2.append(dict(alpha=a_, horizon=h, lam_exc_2025=f'{lo:.2f}-{hi:.2f}', exceptional=f'{100*exc[0]:.0f}-{100*exc[1]:.0f}'))
ct2 = pd.DataFrame(rows2); print('\n(c2) re-anchored so that 2025 exceptional row still matches 85-119'); print(ct2.to_string())
out['calib_sens_reanchored'] = rows2
json.dump(out, open('/home/claude/paper/notes/referee3/check4_results.json', 'w'), indent=1, default=float)
