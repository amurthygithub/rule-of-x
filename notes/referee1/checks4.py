"""Revised calibration (Table 10): decomposition of the upper tail into R_inf and growth surplus, alpha-free.
At X=1, observed Pi_obs = R - R_inf = (1-k)(g-G) - sigma, using S&M share as sigma and capex intensity as k."""
import json, pandas as pd, numpy as np
d = pd.read_csv('/home/claude/paper/data/panel.csv'); x = d[d.period == '2023-25'].copy()
x['R'] = x.g + x.m_fcf_sbc; x = x.dropna(subset=['R'])
G = 0.098; q95 = x.R.quantile(.95); top = x[x.R >= q95].copy()
top['sig'] = top.sm_share.fillna(np.nan); top['k'] = top.capex_int.clip(lower=0).fillna(0)
top['m0_impl'] = top.m_fcf_sbc + top.sig + top.k*top.g
top['Rinf_impl'] = top.m0_impl + (1-top.k)*G
top['Pi_obs'] = top.R - top.Rinf_impl
print(top[['name','g','m_fcf_sbc','sig','k','m0_impl','Rinf_impl','Pi_obs','R']].round(3).head(45).to_string())
t = top.dropna(subset=['sig'])
print(f"\nTop-5% firm-years with S&M: n={len(t)} of {len(top)}; median m0_impl={t.m0_impl.median():.3f}; "
      f"median R_inf_impl={t.Rinf_impl.median():.3f}; median Pi_obs={t.Pi_obs.median():.3f}; share Pi_obs<0: {(t.Pi_obs<0).mean():.2f}; "
      f"share g<0.20: {(top.g<0.2).mean():.2f}; share m0_impl>1: {(t.m0_impl>1).mean():.2f}")
cal = json.load(open('/home/claude/paper/notes/calibration_results.json'))
C = lambda a: (1-a)*a**(a/(1-a))
print("\nlam_anchor:", cal['lam_anchor']); print("Lambda_rule1000:", cal['Lambda_rule1000'])
for a in (0.25, 0.45):
    print(f"  alpha={a}: ratio Lambda/lam_anchor = {cal['Lambda_rule1000'][str(a)]/cal['lam_anchor'][str(a)]:.1f}")

print("\n== Revised anchor: robust bounds on growth surplus Pi (X=1): Pi_obs = R - R_inf <= (1-k)(g-G) since sigma>=0")
top['Pi_ub'] = (1-top.k)*(top.g - G)
print(f"  top-5% firm-years: median g-G = {(top.g-G).median():.3f}; share with Pi_ub < Pi_lo(0.085): {(top.Pi_ub<0.085).mean():.2f}; "
      f"share with m > m0_anchor(0.283): {(top.m_fcf_sbc>0.2834).mean():.2f}")
print("  median observed S&M/(g - median g) among top 5% with S&M and g>G:",
      round(float((t.sig/(t.g-G))[t.g>G].median()),2))
print("\n== Revealed X from sigma/Delta = alpha (X-k) = 2.5 (revised Section 5)")
for a in (0.25, 0.45): print(f"  alpha={a}: X-k = {2.5/a:.1f}")
print("  X in [2,3] requires alpha in", [round(2.5/3,2), round(2.5/2,2)])
print("  at that spend, R_1 - R_inf = Delta (1 - alpha (X-k)) = -1.5 Delta < 0")
print("\n== Regression slope of log Delta on log sigma: variation in ell -> 1, variation in y -> alpha")
