"""Where does the distance to the frontier sit? A descriptive decomposition by cost line (core sample).

Within each growth band (0-10, 10-20, 20-30, 30-40, 40-60%), firm-years in the top decile of GAAP operating margin
("near the frontier") are compared with firm-years between the 40th and 60th percentiles ("typical"). Because
operating margin = gross margin - S&M - R&D - G&A - other operating items (all as shares of revenue), the margin gap
splits exactly into the gaps in each line. Firm-years must report gross profit (or cost of revenue), S&M, R&D and
G&A separately. Band results are averaged with equal weights; 90% intervals come from a firm-cluster bootstrap.
"""
import json
import os
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANDS = [(0, .1), (.1, .2), (.2, .3), (.3, .4), (.4, .6)]
LINES = ['gm', 'sms', 'rds', 'gas', 'oth']
B = 999
rng = np.random.default_rng(20261029)

d = pd.read_csv(f'{BASE}/data/panel.csv')
d['gm'] = d.gp / d.rev
d['sms'] = d.sm / d.rev
d['rds'] = d.rd / d.rev
d['gas'] = d.ga / d.rev
d['oth'] = d.gm - d.sms - d.rds - d.gas - d.m_op          # other operating items (amortization, restructuring, ...)
ok = d[['m_op', 'gm', 'sms', 'rds', 'gas']].notna().all(axis=1) & d.g.between(0, 0.6, inclusive='left')
s = d[ok].copy()
s['band'] = pd.cut(s.g, [b[0] for b in BANDS] + [BANDS[-1][1]], right=False, labels=range(len(BANDS)))


def decompose(x):
    rows = []
    for b, grp in x.groupby('band', observed=True):
        top = grp[grp.m_op >= grp.m_op.quantile(.9)]
        mid = grp[grp.m_op.between(grp.m_op.quantile(.4), grp.m_op.quantile(.6))]
        if len(top) < 3 or len(mid) < 3:
            continue
        r = {'band': int(b), 'n_top': len(top), 'n_mid': len(mid), 'gap': top.m_op.mean() - mid.m_op.mean()}
        r.update({f'top_{c}': top[c].mean() for c in LINES + ['m_op', 'g']})
        r.update({f'mid_{c}': mid[c].mean() for c in LINES + ['m_op', 'g']})
        r['d_gm'] = r['top_gm'] - r['mid_gm']
        for c in ['sms', 'rds', 'gas', 'oth']:
            r[f'd_{c}'] = -(r[f'top_{c}'] - r[f'mid_{c}'])   # lower cost raises margin: sign so components add to the gap
        rows.append(r)
    return pd.DataFrame(rows)


base = decompose(s)
avg = base[['gap', 'd_gm', 'd_sms', 'd_rds', 'd_gas', 'd_oth']].mean()
firms = s.cik.unique()
boot = []
for _ in range(B):
    pick = rng.choice(firms, len(firms), replace=True)
    bs = pd.concat([s[s.cik == f] for f in pick], ignore_index=True)
    r = decompose(bs)
    boot.append(r[['gap', 'd_gm', 'd_sms', 'd_rds', 'd_gas', 'd_oth']].mean())
boot = pd.DataFrame(boot)
ci = {c: [float(boot[c].quantile(.05)), float(boot[c].quantile(.95))] for c in boot}

out = dict(n=int(len(s)), n_firms=int(s.cik.nunique()), coverage=float(ok.sum() / d.g.between(0, 0.6, inclusive='left').sum()),
           bands=base.to_dict(orient='records'), avg=avg.to_dict(), ci90=ci)
json.dump(out, open(f'{BASE}/notes/gap_decomposition.json', 'w'), indent=1)

lab = ['0--10', '10--20', '20--30', '30--40', '40--60']
pp = lambda v: f"{100 * v:.1f}"
rows = []
for _, r in base.iterrows():
    rows.append(f"{lab[int(r.band)]} & {int(r.n_top)} / {int(r.n_mid)} & {pp(r.top_m_op)} & {pp(r.mid_m_op)} & {pp(r.gap)} & "
                f"{pp(r.d_gm)} & {pp(r.d_sms)} & {pp(r.d_rds)} & {pp(r.d_gas)} & {pp(r.d_oth)} \\\\")
ci_s = lambda c: f"[{pp(ci[c][0])}, {pp(ci[c][1])}]"
rows.append(r"\midrule")
rows.append(f"Average of bands & & & & {pp(avg.gap)} & {pp(avg.d_gm)} & {pp(avg.d_sms)} & {pp(avg.d_rds)} & {pp(avg.d_gas)} & {pp(avg.d_oth)} \\\\")
rows.append(f"\\quad 90\\% interval & & & & {ci_s('gap')} & {ci_s('d_gm')} & {ci_s('d_sms')} & {ci_s('d_rds')} & {ci_s('d_gas')} & {ci_s('d_oth')} \\\\")
tab = r"""\begin{table}[t]\centering\small
\caption{Where the distance to the frontier sits: operating-margin gap between firm-years near the frontier and typical firm-years at the same growth, by cost line}\label{tab:gap}
\resizebox{\textwidth}{!}{\begin{tabular}{lrrrrrrrrr}\toprule
 & & \multicolumn{3}{c}{GAAP operating margin} & \multicolumn{5}{c}{Contribution to the gap}\\\cmidrule(lr){3-5}\cmidrule(lr){6-10}
Growth band (\%) & Obs.\ (top / typical) & Top decile & Typical & Gap & Gross margin & S\&M & R\&D & G\&A & Other\\\midrule
""" + '\n'.join(rows) + r"""
\bottomrule\end{tabular}}
\par\vspace{2pt}\footnotesize\raggedright Notes: Core sample, fiscal years 2010--2025, firm-years reporting gross profit or cost of revenue, selling and marketing, research and development, and general and administrative expense separately (""" + f"{100 * out['coverage']:.0f}" + r"""\% of firm-years with growth of 0 to 60\%). Within each growth band, ``top decile'' is the top 10\% of GAAP operating margin and ``typical'' the 40th to 60th percentiles. Entries in percentage points of revenue; contributions are the gap in gross margin and the reduction in each expense share, and sum to the gap. ``Other'' collects remaining operating items such as amortization of acquired intangibles and restructuring. The 90\% interval is from a firm-cluster bootstrap. The decomposition is descriptive: it shows where margins differ, not which changes would close the gap.
\end{table}"""
open(f'{BASE}/sections/tables/tab_gap.tex', 'w').write(tab)
print(base[['band', 'n_top', 'n_mid', 'top_m_op', 'mid_m_op', 'gap', 'd_gm', 'd_sms', 'd_rds', 'd_gas', 'd_oth']].round(3).to_string())
print('avg', avg.round(3).to_dict()); print('ci', {k: [round(v[0], 3), round(v[1], 3)] for k, v in ci.items()}); print('coverage', out['coverage'], out['n'], out['n_firms'])
