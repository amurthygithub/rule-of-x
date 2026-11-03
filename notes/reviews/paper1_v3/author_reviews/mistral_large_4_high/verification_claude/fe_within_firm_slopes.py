"""Mistral EMPIRICAL_ASSESSMENT item 7: its within-firm slopes (+0.083, lead -0.112, cash -0.009) differ from the
printed ones (+0.06, -0.03, -0.03). This reruns the paper's specification (code/estimate_v3.py, lines 1150-1173) on the
shipped panel: firm and year fixed effects, standard errors clustered by firm, growth at most 150% (and the lead in
(-90%, 150%]), with and without that trim."""
import warnings; warnings.filterwarnings('ignore')
import pandas as pd, statsmodels.formula.api as smf
P = pd.read_csv('data/panel_v3.csv')
Pl = P[['cik', 'year', 'g']].sort_values(['cik', 'year']).copy()
Pl['g_lead'] = Pl.groupby('cik').g.shift(-1).where(Pl.groupby('cik').year.shift(-1) == Pl.year + 1)
v = P.merge(Pl[['cik', 'year', 'g_lead']], on=['cik', 'year'])
for m, lab in [('m_op', 'GAAP operating margin'), ('m_fcf_sbc', 'cash margin after SBC')]:
    for trim in (True, False):
        d = v[['cik', 'year', 'g', m]].dropna(); d = d[d.g <= 1.5] if trim else d
        f = smf.ols(f'{m} ~ g + C(year) + C(cik)', d).fit(cov_type='cluster', cov_kwds={'groups': d.cik})
        dl = v[['cik', 'year', 'g', 'g_lead', m]].dropna().rename(columns={'g_lead': 'gl'})
        if trim: dl = dl[(dl.g <= 1.5) & (dl.gl <= 1.5) & (dl.gl > -0.9)]
        a = smf.ols(f'{m} ~ gl + C(year) + C(cik)', dl).fit(cov_type='cluster', cov_kwds={'groups': dl.cik})
        print(f'{lab:24s} {"trimmed" if trim else "untrimmed":9s} same year {f.params.g:+.3f} ({f.bse.g:.3f}) n={len(d)}; lead {a.params.gl:+.3f} ({a.bse.gl:.3f}) n={len(dl)}')
