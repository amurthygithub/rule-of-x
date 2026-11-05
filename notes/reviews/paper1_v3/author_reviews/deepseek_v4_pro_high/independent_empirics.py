import numpy as np, pandas as pd

df = pd.read_csv('data/panel_v3.csv')
print("n firm-years:", len(df), "n firms:", df.cik.nunique())

def period(y):
    if 2010<=y<=2015: return '2010-15'
    if 2016<=y<=2019: return '2016-19'
    if 2020<=y<=2022: return '2020-22'
    return '2023-25'
df['period']=df.year.map(period)
print(df.period.value_counts().to_dict())

def frontier_slope(sub, margin_col, g0_lo=0.0, g0_hi=0.6, step=0.05):
    g0s = np.arange(g0_lo, g0_hi+1e-9, step)
    pts = []
    for g0 in g0s:
        sel = sub[sub.g >= g0]
        if len(sel) < 30:
            return None, g0
        pts.append((g0, sel[margin_col].quantile(0.90)))
    gs = np.array([p[0] for p in pts]); ms = np.array([p[1] for p in pts])
    slope = np.polyfit(gs, ms, 1)[0]
    return slope, None

def p95(sub, score_col):
    return sub[score_col].quantile(0.95)

s1,e = frontier_slope(df, 'm_op')
s2,e = frontier_slope(df, 'm_fcf_sbc')
print(f"\nPsi0.90 slope 2010-25 0-60%: GAAP={s1:.3f} cash={s2:.3f}")

s1,_ = frontier_slope(df, 'm_op', 0.0, 0.4)
s2,_ = frontier_slope(df, 'm_fcf_sbc', 0.0, 0.4)
print(f"Psi0.90 slope 2010-25 0-40%: GAAP={s1:.3f} cash={s2:.3f}")

for p in ['2010-19','2020-25']:
    sub = df[df.year.between(2010,2019)] if p=='2010-19' else df[df.year.between(2020,2025)]
    s1,_ = frontier_slope(sub, 'm_op', 0.0, 0.4)
    s2,_ = frontier_slope(sub, 'm_fcf_sbc', 0.0, 0.4)
    print(f"Psi0.90 slope {p} 0-40%: GAAP={s1:.3f} cash={s2:.3f}")

g1 = p95(df[df.year.between(2016,2019)], 'R_op'); g2 = p95(df[df.year.between(2023,2025)], 'R_op')
c1 = p95(df[df.year.between(2016,2019)], 'R_fcf_sbc'); c2 = p95(df[df.year.between(2023,2025)], 'R_fcf_sbc')
print(f"\nP95 R 2016-19: GAAP={g1:.1f} cash={c1:.1f}; 2023-25 GAAP={g2:.1f} cash={c2:.1f}")
print(f"Change in P95: GAAP={g2-g1:.1f} cash={c2-c1:.1f}")

df2 = df[df.g > df.g.median()]
spend_ratio = (df2.sm / (df2.g - df.g.median())).median()
print(f"\nSpend ratio (median S&M / excess growth): {spend_ratio:.2f}")

print("\nPer-year GAAP P95 and cash P95 of score:")
for y in range(2010, 2026):
    s = df[df.year==y]
    if len(s)>0:
        print(f"{y}: n={len(s):3d} GAAP P95={s.R_op.quantile(0.95):5.1f}  cash P95={s.R_fcf_sbc.quantile(0.95):5.1f}")

# within-firm fixed effects: margin on growth
import statsmodels.api as sm
sub = df[df.g.between(-0.9,1.5)].copy()
sub['const']=1
# firm + year FE via demeaning
for col in ['m_op','m_fcf_sbc','g']:
    pass
