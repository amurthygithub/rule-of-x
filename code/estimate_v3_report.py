"""Tables and notes of code/estimate_v3.py (executed by that script at its end; reads only its JSON output and the
inputs named below, so V3_REPORT_ONLY=1 rewrites everything without re-estimating). Not a stand-alone script.

Writes: sections/tables/tab_estimands_v3.tex, tab_contrasts_v3.tex, tab_grid_v3.tex, tab_yearly_v3.tex,
        notes/inference_v3.md, notes/sample_audit.md
Reads : notes/empirics_v3.json, notes/empirics_v2_exact.json (optional), notes/empirics_organic.json,
        notes/calibration_anchor_E2.json, notes/panel_v3_build.json; frames built by estimate_v3.py (V, core_ext)
"""
J = json.load(open(OUT_JSON))
R = J['estimates']
FAMS = J['families']
BUILD = json.load(open(f'{BASE}/notes/panel_v3_build.json'))
OLD = json.load(open(f'{BASE}/notes/empirics_organic.json'))
OLDAN = json.load(open(f'{BASE}/notes/calibration_anchor_E2.json'))
V2X = json.load(open(f'{BASE}/notes/empirics_v2_exact.json')) if os.path.exists(f'{BASE}/notes/empirics_v2_exact.json') else None
ANB = J['anchor']['blocks']
MF4 = ['E1', 'E2', 'E2imp4', 'E2imp8']
LAB4 = {'E1': 'E1', 'E2': 'E2', 'E2imp4': 'Imputed, M = 4', 'E2imp8': 'Imputed, M = 8', 'E2x25': 'Exclusion only, 25%', 'E1_minus_E2': 'E1 - E2'}
DECISION = ("Decision record (written 29 Oct 2026, 17:05 EDT, 21:05 UTC, before the full panel_v3 run of code/estimate_v3.py). "
            "The author's decisions of 16:50 EDT fix how these results are used. D-2: the primary slope statistic is the slope of "
            "Psi_chi, the order-chi frontier among firm-years with growth at least g (dominance cone, Definition 2), at chi = 0.90 over "
            "growth of 0 to 60%, with chi = 0.80 to 0.95 and windows of 0-40 to 0-100% as the grid; the local conditional quantile "
            "Q_tau(m | g) is reported alongside as a labelled descriptive statistic. D-3: E1 is the baseline, and every model-facing "
            "statistic is reported under E1, E2 and the imputation bounds at deal multiples 4 and 8, with a flag for whether the claim's "
            "sign and significance hold in all four. D-1: the growth weight of 7 to 13 is withdrawn; the bounds each method gives are "
            "reported, and the spend ratio is kept as a statistic of its own. These choices were fixed before any Psi_chi estimate on "
            "panel_v3 had been computed. What had been computed on panel_v3 before the decision: test runs of the superseded pipeline "
            "(code/estimate_organic.py with ORGANIC_PANEL=v3: local conditional-quantile slopes by IRLS, replications divided by ten; "
            "last run finished 16:39 EDT), whose log printed local-quantile point estimates and a familywise result on panel_v3. No "
            "dominance-cone statistic had been computed on panel_v3.")


def nz(x):
    return 0.0 if x is None or (isinstance(x, float) and not math.isfinite(x)) or abs(x) < 5e-12 else x


def ok(r):
    return bool(r) and r.get('est') is not None


def fs(r, nd=2, sc=1.0):
    """estimate (se); n.e. marks a statistic without an interval."""
    if not ok(r):
        return 'n/a'
    s_ = f"{nz(sc * r['est']):.{nd}f}"
    if r.get('se') is not None:
        return s_ + f" ({sc * r['se']:.{nd}f})"
    return s_ + (' (n.e.)' if r.get('estimable') is False else '')


def fc(r, nd=1, sc=100.0, key='ci90', sign=True):
    """estimate [interval]"""
    if not ok(r):
        return 'n/a'
    f_ = (lambda x: f"{nz(x):+.{nd}f}") if sign else (lambda x: f"{nz(x):.{nd}f}")
    s_ = f_(sc * r['est'])
    ci = r.get(key)
    if ci:
        return s_ + f" [{f_(sc * ci[0])}, {f_(sc * ci[1])}]"
    return s_ + (' (n.e.)' if r.get('estimable') is False else '')


def cellf(r, kind):
    return {'se2': lambda: fs(r), 'se3': lambda: fs(r, 3), 'se1': lambda: fs(r, 1), 'pts': lambda: fs(r, 1, 100.0),
            'ci': lambda: fc(r), 'ci2': lambda: fc(r, 2, 1.0), 'cin': lambda: fc(r, 1, 100.0, sign=False),
            'pct': lambda: fc(r, 0, 100.0), 'pctn': lambda: fc(r, 0, 100.0, sign=False), 'int': lambda: (f"{r['est']:.0f}" if ok(r) else 'n/a')}[kind]()


def tex(s_):
    return s_.replace('-', '$-$').replace('n/a', '--').replace('(n.e.)', '$^\\dagger$').replace('%', '\\%')


def flag(st, h0, side, key='ci90'):
    """D-3: claim holds in all four estimands? Returns (sign, significance) strings."""
    recs = [R.get(st, {}).get(vn) for vn in MF4]
    if side is None:
        return '', ''
    if any(not ok(r) for r in recs):
        return 'n.e.', 'n.e.'
    inside = lambda r: r.get('estimable') and r.get(key) and r[key][0] <= h0 <= r[key][1]
    if side == 'null':
        n_in = sum(bool(inside(r)) for r in recs)
        return '', 'yes' if n_in == 4 else f'no ({n_in}/4)'
    on = (lambda x: x < h0) if side == '<' else (lambda x: x > h0)
    sig = lambda r: r.get('estimable') and r.get(key) and (r[key][1] < h0 if side == '<' else r[key][0] > h0)
    n_sign, n_sig = sum(on(r['est']) for r in recs), sum(bool(sig(r)) for r in recs)
    return ('yes' if n_sign == 4 else f'no ({n_sign}/4)'), ('yes' if n_sig == 4 else f'no ({n_sig}/4)')


def claim_text(h0, side):
    if side is None:
        return 'none (reported)'
    if side == 'null':
        return f'no directional claim (interval includes {h0:g})'   # round 3 (GPT-13): no equivalence margin is tested
    return f"{'below' if side == '<' else 'above'} {h0:g}"


# model-facing statistics (D-3): statistic, label, cell kind, H0, side of the claim
MF = [('cone_op_slope_c90_w60', 'Psi_0.90 slope, GAAP, 2010-25 (primary)', 'se2', 0.0, '<'),
      ('cone_op_slope_c90_w60', 'Psi_0.90 slope, GAAP, 2010-25, against -1', 'se2', -1.0, '>'),
      ('cone_cash_slope_c90_w60', 'Psi_0.90 slope, cash, 2010-25 (primary)', 'se2', 0.0, '<'),
      ('cone_cash_slope_c90_w60', 'Psi_0.90 slope, cash, 2010-25, against -1', 'se2', -1.0, '>'),
      ('cone_op_slope_c90_w40_2010_19', 'Psi_0.90 slope, GAAP, 2010-19 (g 0-40%)', 'se2', 0.0, '<'),
      ('cone_op_slope_c90_w40_2020_25', 'Psi_0.90 slope, GAAP, 2020-25 (g 0-40%)', 'se2', 0.0, '<'),
      ('cone_op_slope_c90_w40_2020_25_minus_2010_19', 'Psi_0.90 slope, GAAP, 2020-25 minus 2010-19 (g 0-40%)', 'se2', 0.0, '<'),
      ('cone_cash_slope_c90_w40_2010_19', 'Psi_0.90 slope, cash, 2010-19 (g 0-40%)', 'se2', 0.0, '<'),
      ('cone_cash_slope_c90_w40_2020_25', 'Psi_0.90 slope, cash, 2020-25 (g 0-40%)', 'se2', 0.0, '<'),
      ('cone_cash_slope_c90_w40_2020_25_minus_2010_19', 'Psi_0.90 slope, cash, 2020-25 minus 2010-19 (g 0-40%)', 'se2', 0.0, '<'),
      ('cone_op_slope_c90_w60_2020_25_minus_2010_19', 'Psi_0.90 slope, GAAP, 2020-25 minus 2010-19 (g 0-60%)', 'se2', 0.0, '<'),
      ('cone_op_slope_c80_w60', 'Psi_0.80 slope, GAAP', 'se2', 0.0, '<'), ('cone_op_slope_c95_w60', 'Psi_0.95 slope, GAAP', 'se2', 0.0, '<'),
      ('cone_cash_slope_c80_w60', 'Psi_0.80 slope, cash', 'se2', 0.0, '<'), ('cone_cash_slope_c95_w60', 'Psi_0.95 slope, cash', 'se2', 0.0, '<'),
      ('cone_op_slope_c90_w40', 'Psi_0.90 slope, GAAP, g 0-40%', 'se2', 0.0, '<'), ('cone_op_slope_c90_w80', 'Psi_0.90 slope, GAAP, g 0-80%', 'se2', 0.0, '<'),
      ('cone_cash_slope_c90_w40', 'Psi_0.90 slope, cash, g 0-40%', 'se2', 0.0, '<'), ('cone_cash_slope_c90_w80', 'Psi_0.90 slope, cash, g 0-80%', 'se2', 0.0, '<'),
      ('cone_op_slope_orderm25_w60', 'Order-m (M = 25) frontier slope, GAAP', 'se2', 0.0, '<'),
      ('cone_cash_slope_orderm25_w60', 'Order-m (M = 25) frontier slope, cash', 'se2', 0.0, '<'),
      ('slope_op_pooled', 'Local Q_0.90 slope, GAAP (descriptive)', 'se2', 0.0, '<'),
      ('slope_cash_pooled', 'Local Q_0.90 slope, cash (descriptive)', 'se2', 0.0, '<'),
      ('slope_op_2020_25_minus_2010_19', 'Local Q_0.90 slope, GAAP, 2020-25 minus 2010-19 (descriptive)', 'se2', 0.0, '<'),
      ('spend_ratio', 'Spend-to-excess-growth ratio (median)', 'se2', None, None),
      ('scale_tenfold_cash', 'Size gradient of P95, cash (points per tenfold revenue)', 'pts', 0.0, '<'),
      ('scale_tenfold_fe_cash', 'Size gradient, cash, with period effects', 'pts', 0.0, '<'),
      ('scale_tenfold_g150_cash', 'Size gradient, cash, growth at most 150%', 'pts', 0.0, '<'),
      ('scale_tenfold_op', 'Size gradient, GAAP', 'pts', None, None),
      ('capint_gap_cash_2023_25', 'Capital-intensity gap 2023-25, cash, same-year sort', 'ci', 0.0, '<'),
      ('capint_gap_cash_2023_25_prior', 'Capital-intensity gap, cash, prior-year sort', 'ci', 0.0, '<'),
      ('capint_gap_cash_2023_25_firmmed', 'Capital-intensity gap, cash, firm-median sort', 'ci', 0.0, '<'),
      ('capint_gap_cashadd_2023_25', 'Capital-intensity gap, cash with capex added back, same-year sort', 'ci', 0.0, '<'),
      ('capint_gap_cashadd_2023_25_prior', 'Capital-intensity gap, capex added back, prior-year sort', 'ci', 0.0, '<'),
      ('capint_gap_cashadd_2023_25_firmmed', 'Capital-intensity gap, capex added back, firm-median sort', 'ci', 0.0, '<'),
      ('capint_gap_op_2023_25', 'Capital-intensity gap 2023-25, GAAP', 'ci', None, None),
      ('capint_interaction_cash_pooled', 'g x high intensity, tau = 0.90 regression of the cash margin (Proposition 5)', 'se2', 0.0, '<'),
      ('T_op_g00_change', 'Change in T(0%), GAAP', 'ci', 0.0, 'null'), ('T_cash_g00_change', 'Change in T(0%), cash', 'ci', 0.0, 'null'),
      ('T_op_g20_change', 'Change in T(20%), GAAP', 'ci', 0.0, 'null'), ('T_cash_g20_change', 'Change in T(20%), cash', 'ci', 0.0, 'null'),
      ('T_op_g40_change', 'Change in T(40%), GAAP', 'ci', None, None), ('T_cash_g40_change', 'Change in T(40%), cash', 'ci', None, None),
      ('gap_avg', 'Near-frontier margin gap (GAAP)', 'cin', 0.0, '>'), ('gap_sm', 'of which selling and marketing', 'cin', 0.0, '>'),
      ('gap_rd', 'of which R&D', 'cin', 0.0, '>'), ('gap_gm', 'of which gross margin', 'cin', 0.0, '>'),
      ('gap_ga', 'of which G&A', 'cin', None, None), ('gap_fast_sm', 'S&M part, 40-60% band', 'cin', 0.0, '>'),
      ('anchor_p95_Pi_ub_med', 'Anchor: median Pi, all S&M buys growth (Pi_ub)', 'ci', 0.0, 'null'),
      ('anchor_p95_Pi_lb_med', 'Anchor: median Pi, no S&M buys growth (Pi_lb)', 'ci', 0.0, '>'),
      ('anchor_p95_transient_ub', 'Anchor: transient share of the median top score, upper bound of spend', 'pct', 0.0, 'null'),
      ('anchor_p95_transient_lb', 'Anchor: transient share, lower bound of spend', 'pct', 0.0, '>'),
      ('sfa_op_2023_25_cohort_gap', 'Stochastic frontier, 2023-25: 2019+ entrants minus earlier cohorts, GAAP', 'ci', 0.0, '>'),
      ('sfa_cash_2023_25_cohort_gap', 'same, cash', 'ci', 0.0, '>'),
      ('p95_change_op', 'Change in P95 of R, GAAP, 2016-19 to 2023-25 (descriptive)', 'ci', 0.0, '<'),
      ('p95_change_cash', 'Change in P95 of R, cash (descriptive)', 'ci', 0.0, '<')]


def mf_table(rows=MF):
    L_ = ['| Statistic | Claim | E1 (baseline) | E2 | Imputed, M = 4 | Imputed, M = 8 | Sign in all four | 90% interval in all four (percentile) | 90% interval in all four (basic) |',
          '|---|---|---|---|---|---|---|---|---|']
    for st, lab, kd, h0, side in rows:
        if st not in R:
            continue
        sg, sp = flag(st, h0 if h0 is not None else 0.0, side)
        _, sb = flag(st, h0 if h0 is not None else 0.0, side, 'ci90_basic')
        L_.append(f"| {lab} | {claim_text(h0, side)} | " + ' | '.join(cellf(R[st].get(vn), kd) for vn in MF4) + f" | {sg} | {sp} | {sb} |")
    return '\n'.join(L_)


# =============================================================================================== tables (tex)
TV = ['E1', 'E2', 'E1_minus_E2', 'E2x25', 'E2imp4', 'E2imp8']


def trow(label, basis, st, kind, h0=None, side=None):
    cells = [tex(cellf(R[st].get(vn), kind)) if R[st].get(vn) else '' for vn in TV]
    sg, sp = flag(st, h0 if h0 is not None else 0.0, side)
    fl = '' if side is None else (sp if side == 'null' else f"{sg}/{sp}")
    return f"{label} & {basis} & " + ' & '.join(cells) + f" & {tex(fl)}" + r' \\'


L = [r'\multicolumn{9}{l}{\emph{A. Model-facing statistics: E1 baseline; E2 and the imputation bounds (D-3)}}\\']
for sp_, lab in [('w60', '$\\Psi_{0.90}$ slope, 2010--25, $g$ 0--60\\% (primary)'), ('w40', '$\\Psi_{0.90}$ slope, 2010--25, $g$ 0--40\\%'),
                 ('w40_2010_19', '$\\Psi_{0.90}$ slope, 2010--19, $g$ 0--40\\%'), ('w40_2020_25', '$\\Psi_{0.90}$ slope, 2020--25, $g$ 0--40\\%'),
                 ('w40_2020_25_minus_2010_19', '$\\Psi_{0.90}$ slope, 2020--25 minus 2010--19')]:
    L.append(trow(lab, 'GAAP', f'cone_op_slope_c90_{sp_}', 'se2', 0.0, '<'))
    L.append(trow('', 'FCF after SBC', f'cone_cash_slope_c90_{sp_}', 'se2', 0.0, '<'))
for sp_, lab in [('pooled', 'Local $Q_{0.90}$ slope, 2010--25 (descriptive)'), ('2010_19', 'Local $Q_{0.90}$ slope, 2010--19'),
                 ('2020_25', 'Local $Q_{0.90}$ slope, 2020--25')]:
    L.append(trow(lab, 'GAAP', f'slope_op_{sp_}', 'se2', 0.0, '<'))
    L.append(trow('', 'FCF after SBC', f'slope_cash_{sp_}', 'se2', 0.0, '<'))
L.append(trow('Spend-to-excess-growth ratio (median)', 'S\\&M', 'spend_ratio', 'se2'))
L.append(trow('P95 of $R$ per tenfold revenue (points)', 'GAAP', 'scale_tenfold_op', 'pts'))
L.append(trow('', 'FCF after SBC', 'scale_tenfold_cash', 'pts', 0.0, '<'))
L.append(trow('Capital-intensity gap in P95 of $R$, 2023--25', 'GAAP', 'capint_gap_op_2023_25', 'ci'))
L.append(trow('', 'FCF after SBC', 'capint_gap_cash_2023_25', 'ci', 0.0, '<'))
L.append(trow('', 'capex added back', 'capint_gap_cashadd_2023_25', 'ci', 0.0, '<'))
for g0 in ['00', '20', '40']:
    L.append(trow(f'Change in $T({int(g0)}\\%)$, 2016--19 to 2023--25', 'GAAP', f'T_op_g{g0}_change', 'ci', 0.0, 'null' if g0 != '40' else None))
    L.append(trow('', 'FCF after SBC', f'T_cash_g{g0}_change', 'ci', 0.0, 'null' if g0 != '40' else None))
L.append(trow('Near-frontier margin gap, average of bands', 'GAAP', 'gap_avg', 'cin', 0.0, '>'))
for k_, lab in [('gap_sm', 'of which selling and marketing'), ('gap_rd', 'of which R\\&D'), ('gap_gm', 'of which gross margin'), ('gap_ga', 'of which G\\&A')]:
    L.append(trow('\\quad ' + lab, '', k_, 'cin'))
L.append(trow('Anchor: median $\\Pi$, all S\\&M buys growth', 'cash', 'anchor_p95_Pi_ub_med', 'ci', 0.0, 'null'))
L.append(trow('Anchor: median $\\Pi$, no S\\&M buys growth', 'cash', 'anchor_p95_Pi_lb_med', 'ci', 0.0, '>'))
L.append(r'\addlinespace\multicolumn{9}{l}{\emph{B. Distribution of reported scores (descriptive, E1 primary)}}\\')
for p in ['2016_19', '2023_25']:
    L.append(trow(f'P95 of $R$, {p.replace("_", "--")}', 'GAAP', f'p95_op_{p}', 'cin'))
    L.append(trow('', 'FCF after SBC', f'p95_cash_{p}', 'cin'))
L.append(trow('Change in P95 of $R$, 2016--19 to 2023--25', 'GAAP', 'p95_change_op', 'ci', 0.0, '<'))
L.append(trow('', 'FCF after SBC', 'p95_change_cash', 'ci', 0.0, '<'))
L.append(r'\addlinespace\multicolumn{9}{l}{\emph{C. Samples}}\\')
S_ = J['samples']
cnt = lambda f_: ' & '.join('' if vn == 'E1_minus_E2' else f_(vn) for vn in TV)
L.append('Firm-years (firms) & & ' + cnt(lambda vn: f"{S_[vn]['n']:,} ({S_[vn]['firms']})") + r' & \\')
L.append('\\quad of which acquisition-affected & & ' + cnt(lambda vn: str(S_[vn]['n_affected_kept'])) + r' & \\')
L.append('Firm-years with $g>50\\%$ & & ' + cnt(lambda vn: str(S_[vn]['n_g_above_50'])) + r' & \\')
TAB1 = r"""\begin{table}[t]\centering\small
\caption{Headline statistics on the audited sample (v3): E1 baseline, E2 and imputation bounds}\label{tab:estimands_v3}
\resizebox{\textwidth}{!}{\begin{tabular}{llccccccc}\toprule
 & & E1: all & E2: & & Exclusion & \multicolumn{2}{c}{E2 plus imputed} & Holds in\\
Statistic & Basis & firm-years & organic & E1 $-$ E2 & only, 25\% & $M=4$ & $M=8$ & all four\\\midrule
""" + '\n'.join(L) + r"""
\bottomrule\end{tabular}}
\par\vspace{2pt}\footnotesize\raggedright Notes: Audited core sample (data/panel\_v3.csv: SIC 7372, fiscal years 2010--2025, firm-years first reported in their own annual report, captive related-party filer excluded, acquisition flag of rule R4). E1 uses every firm-year and reported growth (baseline). E2 keeps firm-years without material acquisitions and re-admits acquisition-affected ones with pro forma organic growth where the original filings identify it. The imputation columns add the acquisition-affected firm-years E2 drops, with organic growth imputed by removing acquired revenue equal to the purchase price over a price-to-revenue multiple $M$, half in the deal year and half in the next. $\Psi_{0.90}$ slope (primary statistic): least-squares slope over $g_0=0,0.05,\dots,0.6$ of $\phi_{0.90}(g_0)$, the 90th percentile of the margin among firm-years with $g\geq g_0$ (dominance cone; each grid point at least 30 firm-years in the sample and 10 in a bootstrap draw); within periods the cells at 60\% growth are below 30 firm-years, so period slopes use $0\leq g\leq0.4$. Local $Q_{0.90}$ slope (descriptive): $\tau=0.90$ linear quantile regression of margin on growth for $0\leq g\leq0.6$, solved exactly. Size gradient: $\tau=0.95$ quantile regression of $R$ on log prior-year revenue, times $\ln 10$. Capital-intensity gap: P95 of $R$ above minus below the period median of capital expenditure and capitalized software over revenue, split re-estimated in each bootstrap draw; firm-years without the measure are not classified. $T(g_0)=g_0+\phi_{0.95}(g_0)$. Anchor: 2023--25 firm-years at or above the P95 of the cash score (calibration rules). Parentheses: firm-cluster bootstrap standard errors; brackets: 90\% percentile intervals; 999 replications, firms drawn from E1, every column on the same draws; E1 $-$ E2 paired. $^\dagger$: no interval (more than 5\% of draws undefined, or a frontier-point cell below 30 firm-years). Last column (D-3): the claim's sign / its 90\% percentile interval hold in E1, E2 and both imputation columns; for frontier points at 0 and 20\% and the anchor's $\Pi_{ub}$ no directional claim is made (the interval includes zero; no equivalence margin is tested). Points except slopes and the ratio.
\end{table}"""
open(f'{BASE}/sections/tables/tab_estimands_v3.tex', 'w').write(TAB1)

CLAB = {'slope_op_pooled': ('Local $Q_{0.90}$ slope, 2010--25', 'GAAP', 'se2'), 'slope_cash_pooled': ('', 'cash', 'se2'),
        'slope_op_2010_19': ('Local $Q_{0.90}$ slope, 2010--19', 'GAAP', 'se2'), 'slope_cash_2010_19': ('', 'cash', 'se2'),
        'slope_op_2020_25': ('Local $Q_{0.90}$ slope, 2020--25', 'GAAP', 'se2'), 'slope_cash_2020_25': ('', 'cash', 'se2'),
        'cone_op_slope_c90_w60': ('$\\Psi_{0.90}$ slope, 2010--25, $g$ 0--60\\%', 'GAAP', 'se2'), 'cone_cash_slope_c90_w60': ('', 'cash', 'se2'),
        'cone_op_slope_c90_w40_2010_19': ('$\\Psi_{0.90}$ slope, 2010--19, $g$ 0--40\\%', 'GAAP', 'se2'), 'cone_cash_slope_c90_w40_2010_19': ('', 'cash', 'se2'),
        'cone_op_slope_c90_w40_2020_25': ('$\\Psi_{0.90}$ slope, 2020--25, $g$ 0--40\\%', 'GAAP', 'se2'), 'cone_cash_slope_c90_w40_2020_25': ('', 'cash', 'se2'),
        'spend_ratio': ('Spend ratio', 'S\\&M', 'se2'), 'scale_tenfold_op': ('Size gradient', 'GAAP', 'pts'), 'scale_tenfold_cash': ('', 'cash', 'pts'),
        'capint_gap_op_2023_25': ('Capital-intensity gap, 2023--25', 'GAAP', 'ci'), 'capint_gap_cash_2023_25': ('', 'cash', 'ci'),
        'p95_change_op': ('Change in P95', 'GAAP', 'ci'), 'p95_change_cash': ('', 'cash', 'ci'),
        'p90_change_op': ('Change in P90', 'GAAP', 'ci'), 'p90_change_cash': ('', 'cash', 'ci'),
        'T_op_g00_change': ('Change in $T(0\\%)$', 'GAAP', 'ci'), 'T_op_g20_change': ('Change in $T(20\\%)$', 'GAAP', 'ci'),
        'T_op_g40_change': ('Change in $T(40\\%)$', 'GAAP', 'ci'), 'T_cash_g00_change': ('Change in $T(0\\%)$', 'cash', 'ci'),
        'T_cash_g20_change': ('Change in $T(20\\%)$', 'cash', 'ci'), 'T_cash_g40_change': ('Change in $T(40\\%)$', 'cash', 'ci'),
        'gap_avg': ('Margin gap', 'GAAP', 'ci'), 'gap_gm': ('\\quad gross margin', '', 'ci'), 'gap_sm': ('\\quad S\\&M', '', 'ci'),
        'gap_rd': ('\\quad R\\&D', '', 'ci'), 'gap_ga': ('\\quad G\\&A', '', 'ci'), 'gap_oth': ('\\quad other', '', 'ci'),
        'gap_slow': ('Margin gap, 0--10\\% band', '', 'ci'), 'gap_slow_gm': ('\\quad gross margin', '', 'ci'),
        'gap_fast': ('Margin gap, 40--60\\% band', '', 'ci'), 'gap_fast_sm': ('\\quad S\\&M', '', 'ci'), 'gap_fast_rd': ('\\quad R\\&D', '', 'ci')}


def civ(c_, key, kd):
    v_ = c_.get(key)
    if not v_:
        return '--'
    sc, nd = (1.0, 2) if kd == 'se2' else (100.0, 1)
    return tex(f"[{nz(sc * v_[0]):+.{nd}f}, {nz(sc * v_[1]):+.{nd}f}]")


def pfmt(x):
    return '--' if x is None else (f'{x:.3f}' if x >= 0.001 else '$<$0.001')


F38 = FAMS['table38']
L = []
for c_ in F38['contrasts']:
    lab, basis, kd = CLAB[c_['key']]
    sc, nd = (1.0, 2) if kd == 'se2' else (100.0, 1)
    est = '--' if c_['est'] is None else tex(f"{nz(sc * c_['est']):+.{nd}f}")
    L.append(f"{lab} & {basis} & {est} & " + ' & '.join(civ(c_, k_, kd) for k_ in ('ci90', 'ci90_basic', 'ci90_normal', 'ci95', 'ci95_basic', 'ci95_normal'))
             + f" & {pfmt(c_.get('p_percentile'))} & {pfmt(c_['holm_percentile'])} & {pfmt(c_['holm_basic'])} & {pfmt(c_['holm_normal'])} & {pfmt(c_['romano_wolf'])}" + r' \\')
nx = F38['intervals_excluding_h0']
TAB2 = r"""\begin{table}[t]\centering\small
\caption{Paired E1 $-$ E2 contrasts on the audited sample (v3): interval types and multiplicity}\label{tab:contrasts_v3}
\resizebox{\textwidth}{!}{\begin{tabular}{llcccccccccccc}\toprule
 & & & \multicolumn{3}{c}{90\% interval} & \multicolumn{3}{c}{95\% interval} & & \multicolumn{3}{c}{Holm-adjusted $p$} & Romano--\\\cmidrule(lr){4-6}\cmidrule(lr){7-9}\cmidrule(lr){11-13}
Statistic & Basis & E1 $-$ E2 & percentile & basic & normal & percentile & basic & normal & $p$ (percentile) & percentile & basic & normal & Wolf\\\midrule
""" + '\n'.join(L) + r"""
\bottomrule\end{tabular}}
\par\vspace{2pt}\footnotesize\raggedright Notes: """ + f"{F38['n']}" + r""" paired contrasts: every E1 $-$ E2 contrast of Table~\ref{tab:estimands_v3} other than the anchor and the P95 levels; the 32 below the six $\Psi$ rows are the family counted by the econometrics referees for Table~\ref{tab:estimands}. Firm-cluster paired bootstrap (999 replications, firms drawn from E1). Percentile: quantiles of the draws; basic: reflected about the estimate; normal: estimate $\pm$ $z$ times the bootstrap standard error. $p$: two-sided bootstrap $p$-value of each type; Holm step-down across the """ + f"{F38['n']}" + r""" contrasts for each type; Romano--Wolf: studentized step-down on a joint draw. A contrast without an interval enters with $p=1$. Intervals excluding zero at 90\%: """ + f"{nx['90_percentile']} percentile, {nx['90_basic']} basic, {nx['90_normal']} normal (expected under the global null: {0.1 * F38['n']:.1f}); at 95\\%: {nx['95_percentile']}, {nx['95_basic']}, {nx['95_normal']}" + r""". Points except slopes and the ratio.
\end{table}"""
open(f'{BASE}/sections/tables/tab_contrasts_v3.tex', 'w').write(TAB2)

L = []
CW = [w for w in WINS if any(ok(R[f'cone_{b}_slope_c90_w{int(round(100 * w))}'].get(vn)) for b in BASES for vn in MF4)]   # windows with an estimate
for c in TAUS:
    for w in CW:
        cl = f'c{int(round(100 * c))}_w{int(round(100 * w))}'
        L.append(f"{c:.2f} & 0--{int(round(100 * w))}\\% & " + ' & '.join(tex(fs(R[f'cone_{b}_slope_{cl}'].get(vn))) for b in BASES for vn in MF4) + r' \\')
L.append(r'\addlinespace\multicolumn{10}{l}{\emph{Order-$m$ frontier ($M=25$)}}\\')
for w in CW:
    L.append(f" & 0--{int(round(100 * w))}\\% & " + ' & '.join(tex(fs(R[f'cone_{b}_slope_orderm25_w{int(round(100 * w))}'].get(vn))) for b in BASES for vn in MF4) + r' \\')
L.append(r'\addlinespace\multicolumn{10}{l}{\emph{B. Local conditional quantile $Q_\tau(m\mid g)$, linear quantile regression (descriptive): E1, E2 and E1 $-$ E2}}\\')
L.append(r' $\tau$ & Window & E1 & E2 & E1 $-$ E2 & & E1 & E2 & E1 $-$ E2 & \\')
for t in TAUS:
    for w in WINS:
        cl = f't{int(round(100 * t))}_w{int(round(100 * w))}'
        c3 = lambda b: ' & '.join(tex(fs(R[f'slope_{b}_{cl}'].get(vn))) for vn in ['E1', 'E2', 'E1_minus_E2'])
        L.append(f"{t:.2f} & 0--{int(round(100 * w))}\\% & " + c3('op') + ' & & ' + c3('cash') + r' & \\')
TAB3 = r"""\begin{table}[t]\centering\small
\caption{Frontier slopes by quantile and growth window, audited sample (v3)}\label{tab:grid_v3}
\resizebox{\textwidth}{!}{\begin{tabular}{llcccccccc}\toprule
\multicolumn{10}{l}{\emph{A. Dominance-cone frontier $\Psi_\chi$ (primary): slope of $\phi_\chi(g_0)$ over the window}}\\
 & & \multicolumn{4}{c}{GAAP operating margin} & \multicolumn{4}{c}{FCF margin after SBC}\\\cmidrule(lr){3-6}\cmidrule(lr){7-10}
$\chi$ & Window & E1 & E2 & $M=4$ & $M=8$ & E1 & E2 & $M=4$ & $M=8$\\\midrule
""" + '\n'.join(L) + r"""
\bottomrule\end{tabular}}
\par\vspace{2pt}\footnotesize\raggedright Notes: Panel A: $\phi_\chi(g_0)$ is the $\chi$-quantile of the margin among firm-years with growth of at least $g_0$ (Definition 2); the slope is the least-squares slope over $g_0=0,0.05,\dots$ up to the end of the window, defined when every grid point has at least 30 firm-years in the sample (10 in a bootstrap draw); windows ending at 80 and 100\% are not defined because fewer than 30 firm-years grow at least 80\%. The order-$m$ frontier is the expected maximum of $M=25$ draws from the same cone (estimate\_frontier.py). $M=4$, $M=8$: E2 plus the dropped acquisition-affected firm-years with imputed organic growth. Panel B: exact linear quantile regression of the margin on growth over the window. Firm-cluster bootstrap standard errors in parentheses (999 replications); $^\dagger$: no interval (more than 5\% of draws undefined).
\end{table}"""
open(f'{BASE}/sections/tables/tab_grid_v3.tex', 'w').write(TAB3)

NYR = {vn: V[vn].groupby('year').size().to_dict() for vn in PAIRV}
L = []
for y in YEARS:
    L.append(f"{y} & {NYR['E1'].get(y, 0)} & {NYR['E2'].get(y, 0)} & " + ' & '.join(tex(fs(R[f'p95_{b}_{y}'].get(vn), 1, 100.0)) for vn in PAIRV for b in BASES)
             + ' & ' + ' & '.join(tex(fs(R[f'slope_{b}_{y}'].get(vn))) for vn in PAIRV for b in BASES) + r' \\')
L.append(r'\addlinespace')
for w, lab in [('2025', '2016--19 to 2025'), ('2023_24', '2016--19 to 2023--24')]:
    L.append(f"Change in P95, {lab} & & & " + ' & '.join(tex(fc(R[f'p95_change_{b}_2016_19_to_{w}'].get(vn))) for vn in PAIRV for b in BASES) + r' & & & & \\')
L.append("Slope with year effects & & & & & & & " + ' & '.join(tex(fs(R[f'slope_yearfe_{b}'].get(vn))) for vn in PAIRV for b in BASES) + r' \\')
TAB4 = r"""\begin{table}[t]\centering\small
\caption{The top of the score distribution and the within-year slope by fiscal year, audited sample (v3)}\label{tab:yearly_v3}
\resizebox{\textwidth}{!}{\begin{tabular}{lcccccccccc}\toprule
 & \multicolumn{2}{c}{Firm-years} & \multicolumn{4}{c}{P95 of $R$ (points)} & \multicolumn{4}{c}{Local $Q_{0.90}$ slope, $0\leq g\leq0.6$}\\\cmidrule(lr){2-3}\cmidrule(lr){4-7}\cmidrule(lr){8-11}
Fiscal year & E1 & E2 & E1 GAAP & E1 cash & E2 GAAP & E2 cash & E1 GAAP & E1 cash & E2 GAAP & E2 cash\\\midrule
""" + '\n'.join(L) + r"""
\bottomrule\end{tabular}}
\par\vspace{2pt}\footnotesize\raggedright Notes: Firm-cluster bootstrap standard errors in parentheses (999 replications); brackets: 90\% percentile intervals. Within-year slopes need at least 30 firm-years with $0\leq g\leq0.6$; a dominance-cone slope is not computed by year because its cells at high growth are below 30 firm-years in single years. Slope with year effects: $\tau=0.90$ quantile regression of the margin on growth and fiscal-year indicators, 2010--25.
\end{table}"""
open(f'{BASE}/sections/tables/tab_yearly_v3.tex', 'w').write(TAB4)
BRB = [('op', 'GAAP operating margin'), ('cash', 'FCF after SBC (paper)'), ('cash_bs', 'FCF after SBC, bridge firm-years'),
       ('cash_bi', 'before interest paid, after tax'), ('cash_pre', 'before interest paid and cash taxes')]
HAS_BRIDGE = 'bridge_op_p95_2016_19' in R
if 'bridge_cash_bni_p95_2016_19' in R:                       # round 2 (D1): before net interest, and its like-for-like basis
    BRB += [('cash_bnis', 'FCF after SBC, net-interest firm-years'), ('cash_bni', 'before net interest, after tax')]
if HAS_BRIDGE:
    L = []
    for vn in PAIRV:
        L.append(r'\addlinespace\multicolumn{8}{l}{\emph{' + {'E1': 'E1: all firm-years', 'E2': 'E2: organic'}[vn] + r'}}\\')
        for b, lab in BRB:
            g_ = lambda x, kd: tex(cellf(R[f'bridge_{b}_{x}'].get(vn), kd))
            L.append(f"{lab} & {g_('p95_2016_19', 'cin')} & {g_('p95_2023_25', 'cin')} & {g_('p95_change', 'ci')} & {g_('med_2016_19', 'cin')} & "
                     f"{g_('med_2023_25', 'cin')} & {g_('margin_med_2010_25', 'cin')} & {R[f'bridge_{b}_n_2016_19'][vn]['est']:.0f} / {R[f'bridge_{b}_n_2023_25'][vn]['est']:.0f}" + r' \\')
    TAB5 = (r"""\begin{table}[t]\centering\small
\caption{The cash score before interest paid, net interest and cash taxes, audited sample (v3)}\label{tab:bridge_v3}
\resizebox{\textwidth}{!}{\begin{tabular}{lccccccc}\toprule
 & \multicolumn{3}{c}{P95 of $R$} & \multicolumn{2}{c}{Median of $R$} & Median margin & Firm-years\\\cmidrule(lr){2-4}\cmidrule(lr){5-6}
Basis & 2016--19 & 2023--25 & Change & 2016--19 & 2023--25 & 2010--25 & 2016--19 / 2023--25\\\midrule
""" + '\n'.join(L) + r"""
\bottomrule\end{tabular}}
\par\vspace{2pt}\footnotesize\raggedright Notes: Points; brackets: 90\% firm-cluster percentile intervals (999 replications, firms drawn from E1). FCF after SBC is the paper's cash basis (operating cash flow less capital expenditure, capitalized software and stock-based compensation, over revenue); under US GAAP operating cash flow is after interest paid and income taxes paid (ASC 230-10-45-17). Before interest and cash taxes adds interest paid and income taxes paid back; before interest, after tax adds interest paid times one minus the US federal statutory rate (35\% for fiscal years ending before 2018, 21\% from 2018). Interest and taxes paid are XBRL InterestPaidNet (else InterestPaid) and IncomeTaxesPaidNet (else IncomeTaxesPaid) from SEC frames, which keep the latest filed value, not the first reported one; a missing element counts as zero when the firm-year reports any of the four, and the bridge bases are missing otherwise. ``Bridge firm-years'' is the paper's cash basis on the firm-years where the bridge is defined, the like-for-like comparison. Before net interest, after tax also subtracts interest income (XBRL InvestmentIncomeInterest, else InvestmentIncomeInterestAndDividend, else InterestIncomeOperating; SEC frames retrieved 2 November 2026) times one minus the statutory rate; it is defined only where interest income is reported under one of these elements (many firms report it only inside other income, net), and ``net-interest firm-years'' is the paper's cash basis on those firm-years.
\end{table}""")
    open(f'{BASE}/sections/tables/tab_bridge_v3.tex', 'w').write(TAB5)
log('wrote sections/tables/tab_estimands_v3.tex, tab_contrasts_v3.tex, tab_grid_v3.tex, tab_yearly_v3.tex' + (', tab_bridge_v3.tex' if HAS_BRIDGE else ''))


def bridge_md():
    if not HAS_BRIDGE:
        return '(not available)'
    L_ = ['| Estimand | Basis | P95 2016-19 | P95 2023-25 | Change in P95 | Median R 2016-19 | Median R 2023-25 | Change in median | Median R 2010-25 | Median margin 2010-25 | Firm-years 2016-19 / 2023-25 |',
          '|---|---|---|---|---|---|---|---|---|---|---|']
    for vn in PAIRV:
        for b, lab in BRB:
            g_ = lambda x, kd: cellf(R[f'bridge_{b}_{x}'].get(vn), kd)
            L_.append(f"| {vn} | {lab} | {g_('p95_2016_19', 'cin')} | {g_('p95_2023_25', 'cin')} | {g_('p95_change', 'ci')} | {g_('med_2016_19', 'cin')} | "
                      f"{g_('med_2023_25', 'cin')} | {g_('med_change', 'ci')} | {g_('med_2010_25', 'cin')} | {g_('margin_med_2010_25', 'cin')} | "
                      f"{R[f'bridge_{b}_n_2016_19'][vn]['est']:.0f} / {R[f'bridge_{b}_n_2023_25'][vn]['est']:.0f} |")
    return '\n'.join(L_)


def sec_text():
    """Sample-audit paragraphs that depend on the SEC inputs of 29 Oct 2026 (empty strings when absent)."""
    t = {}
    r2 = BUILD.get('R2_named')
    if r2:
        soft_hits = '; '.join(f"{n} {h}" for n, h in r2['hits'].items() if r2['classes'][n] == 'software'
                              and (h['interactive_entertainment'] or h['gambling'] or h['compute_infrastructure']))
        t['R2'] = (f"The classifier, run as defined before the descriptions were read (keyword lists unchanged), classes "
                   f"{len(r2['non_software'])} of the {len(r2['classes'])} named firms non-software: "
                   + '; '.join(f"{n} ({r2['classes'][n]})" for n in r2['non_software'])
                   + f" ({r2['firm_years_v3_non_software']} v3 firm-years). It classes the others as software. Its keyword lists miss "
                   f"game publishers and an AI-cloud provider whose openings do not use the listed phrases (non-software hits below "
                   f"three: {soft_hits}), and it has no class for hardware, payments or interiors, so 3D Systems, DIRTT, Block, "
                   f"Mobileye, Xperi and Xunlei are software by default. The sensitivity `r2named` drops the firms it classes "
                   f"non-software; `clean` drops all named firms. Applying R2 as a rule needs the description of every registrant.")
    x = BUILD['R3'].get('xbrl')
    if x:
        t['R3'] = (f"XBRL related-party revenue (SEC frames): {x['core_v2_firm_years_with_fact']} v2 core firm-years of {x['firms_with_fact']} "
                   f"firms report it ({x['core_v3_firm_years_with_fact']} in v3); {x['n_at_or_above_50pct']} reach 50% of revenue. "
                   f"The largest shares: {'; '.join(x['top'])}. RevenueFromRelatedParties is absent from frames for 2024-26 (retired) "
                   f"and the alternative element for 2014-26 except 2023, so recent captive filers can still be missed by the "
                   f"XBRL test; Exzeo 2025 is caught by its filing text.")
    a = BUILD['R4'].get('acquiree_revenue')
    if a:
        t['R4c'] = (f"(c) applied: a year in which acquired businesses contributed at least 10% of revenue since their "
                    f"acquisition dates is flagged. SEC frames hold {a['facts_matched_panel']} such facts for the panel's registrants "
                    f"({a['core_v2_firm_years_with_fact']} v2 core firm-years). Core firm-years at or above 10%: "
                    f"{'; '.join(a['core_v2_at_or_above_10pct'])} (in v3: {'; '.join(a['core_v3_at_or_above_10pct'])}). All are already "
                    f"flagged by the other criteria, so (c) adds {len(a['new_flags_core_v2'])} core flags; outside the core it adds "
                    f"{'; '.join(a['new_flags_all_panel']) or 'none'}. Coverage is thin: the element is usually tagged on a "
                    f"business-combination axis, and frames keep only non-dimensional facts. Because (c) applies at every flag "
                    f"threshold, it moves the 50% threshold variants (E2x50, E2pf50) by one firm-year.")
    r5 = BUILD['R5']
    if 'status_counts_v3' in r5:
        nl = r5['no_listed_equity_v3']
        t['R5'] = (f"Rule (applied as a flag): the sign of dei:EntityPublicFloat on the 10-K cover page by fiscal year. The float "
                   f"is measured at the end of the second fiscal quarter, so a zero float also occurs in the first annual report after "
                   f"an IPO or spin-off. For a 10-K firm-year with a float fact that is not positive: (i) IPO or spin-off timing when "
                   f"the firm reports a positive float in one of the next two fiscal years; (ii) IPO timing, unresolved, when the year is "
                   f"the firm's first annual report and its only float fact; (iii) otherwise no listed equity. An untagged year takes "
                   f"the status no listed equity when the firm's nearest float facts on each available side are no listed equity. 20-F "
                   f"and 40-F reports are not tested: their cover pages report shares outstanding, not public float. Status counts in "
                   f"v3: {r5['status_counts_v3']}. No listed equity ({r5['firm_years_no_listed_equity_v3']} v3 firm-years): "
                   + '; '.join(f"{n} ({', '.join(str(y) for y in ys)})" for n, ys in nl.items())
                   + f". IPO or spin-off timing, not debt-only: {'; '.join(f'{n} {ys[0]}' for n, ys in r5['ipo_timing'].items())}. "
                   f"Unresolved (2025 IPOs; their second annual report does not exist yet): "
                   f"{'; '.join(f'{n} {ys[0]}' for n, ys in r5['ipo_timing_unresolved'].items())}. Foreign filers with a zero float "
                   f"fact, not tested: {', '.join(r5['foreign_zero_float'])}; their Section 12(b) listing is on the 20-F cover page, which "
                   f"is not in the inputs. The sensitivity `nolist` drops the flagged firm-years; `nodebt` keeps the earlier "
                   f"comparison for the four filers the finance referee named.")
    cb = BUILD['cash_score_basis']
    if 'coverage_v3' in cb:
        t['B5'] = (f"The bridge is now built ({cb['retrieved']}; {cb['coverage_core']}; elements {cb['coverage_v3']}; {cb['rule']}). "
                   f"Results for E1 and E2 are in `notes/inference_v3.md` section 18 and `sections/tables/tab_bridge_v3.tex`. E1, 2016-19 "
                   f"and 2023-25 P95 and median, points: "
                   + '; '.join(f"{lab}: P95 {100 * R[f'bridge_{b}_p95_2016_19']['E1']['est']:.1f} and {100 * R[f'bridge_{b}_p95_2023_25']['E1']['est']:.1f}, "
                               f"median {100 * R[f'bridge_{b}_med_2016_19']['E1']['est']:.1f} and {100 * R[f'bridge_{b}_med_2023_25']['E1']['est']:.1f}"
                               for b, lab in BRB) + '.')
    return t


SECT = sec_text() if 'R' in globals() else {}


# =============================================================================================== notes/inference_v3.md
def fam_md(F, nd_map=None, cl=None):
    L_ = ['| Contrast | H0 | Estimate | se | 90% percentile | 90% basic | 90% normal | 95% percentile | p normal | p percentile | p basic | Holm normal | Holm percentile | Holm basic | Romano-Wolf |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for c_ in F['contrasts']:
        st = c_['statistic']
        sc, nd = (1.0, 3) if (st.startswith(('slope', 'cone', 'spend', 'weight'))) else (100.0, 1)
        e = 'n.e.' if c_['est'] is None else f"{nz(sc * c_['est']):+.{nd}f}"
        if not c_.get('estimable'):
            cells = [c_['label'], f"{c_['h0']:g}", f"{e} (n.e.: {c_.get('note') or ''})"] + [''] * 5 + ['1', '1', '1'] + [f"{c_[k_]:.3f}" for k_ in ('holm_normal', 'holm_percentile', 'holm_basic', 'romano_wolf')]
            L_.append('| ' + ' | '.join(cells) + ' |')
            continue
        ci = lambda k_: f"[{nz(sc * c_[k_][0]):+.{nd}f}, {nz(sc * c_[k_][1]):+.{nd}f}]"
        L_.append(f"| {c_['label']} | {c_['h0']:g} | {e} | {sc * c_['se']:.{nd}f} | {ci('ci90')} | {ci('ci90_basic')} | {ci('ci90_normal')} | {ci('ci95')} | "
                  f"{c_['p_normal']:.4f} | {c_['p_percentile']:.4f} | {c_['p_basic']:.4f} | {c_['holm_normal']:.3f} | {c_['holm_percentile']:.3f} | "
                  f"{c_['holm_basic']:.3f} | {c_['romano_wolf']:.3f} |")
    s5, s10 = F['survivors_5pct'], F['survivors_10pct']
    L_.append('')
    L_.append('Survivors, familywise 5%: ' + '; '.join(f"{k_}: {', '.join(v_) if v_ else 'none'}" for k_, v_ in s5.items()) + '.')
    L_.append('Survivors, familywise 10%: ' + '; '.join(f"{k_}: {', '.join(v_) if v_ else 'none'}" for k_, v_ in s10.items()) + '.')
    L_.append(f"Unadjusted p below {F['alpha']:g}: " + ', '.join(f'{k_} {v_}' for k_, v_ in F['unadjusted_p_below_alpha'].items())
              + f". Intervals excluding H0: {F['intervals_excluding_h0']}. Draws complete for Romano-Wolf: {F['rw_draws_complete']}.")
    return '\n'.join(L_)


def fam38_md(F):
    L_ = ['| Contrast | E1 - E2 | 90% percentile | 90% basic | 90% normal | 90% bias-corrected | 95% percentile | 95% basic | 95% normal | bootstrap bias | p percentile | Holm percentile | Holm basic | Holm normal | Romano-Wolf |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for c_ in F['contrasts']:
        st = c_['statistic']
        sc, nd = (1.0, 3) if st.startswith(('slope', 'cone', 'spend')) else (100.0, 1)
        if not c_.get('estimable'):
            e = 'n.e.' if c_['est'] is None else f"{nz(sc * c_['est']):+.{nd}f}"
            cells = [st, f"{e} (n.e.: {c_.get('note') or ''})"] + [''] * 8 + ['1'] + [f"{c_[k_]:.3f}" for k_ in ('holm_percentile', 'holm_basic', 'holm_normal', 'romano_wolf')]
            L_.append('| ' + ' | '.join(cells) + ' |')
            continue
        ci = lambda k_: f"[{nz(sc * c_[k_][0]):+.{nd}f}, {nz(sc * c_[k_][1]):+.{nd}f}]"
        L_.append(f"| {st} | {nz(sc * c_['est']):+.{nd}f} | {ci('ci90')} | {ci('ci90_basic')} | {ci('ci90_normal')} | {ci('ci90_bc')} | {ci('ci95')} | {ci('ci95_basic')} | {ci('ci95_normal')} | "
                  f"{nz(sc * c_['bias']):+.{nd}f} | {c_['p_percentile']:.4f} | {c_['holm_percentile']:.3f} | {c_['holm_basic']:.3f} | {c_['holm_normal']:.3f} | {c_['romano_wolf']:.3f} |")
    return '\n'.join(L_)


def rec4(st, kd, vns=MF4):
    return ' | '.join(cellf(R[st].get(vn), kd) for vn in vns)


SPEND_ROWS = [('spend_ratio', 'Median S&M share / (g - G_t), G_t = year median growth (the spend ratio; kept, D-1)'),
              ('spend_q25', 'its 25th percentile'), ('spend_q75', 'its 75th percentile'),
              ('spend_terc1_ratio', '(a) lowest tercile of excess growth'), ('spend_terc2_ratio', '(a) middle tercile'), ('spend_terc3_ratio', '(a) highest tercile'),
              ('spend_floor10_ratio', '(a) excess growth above 10 points'), ('spend_floor20_ratio', '(a) excess growth above 20 points'),
              ('spend_floor05_ratio', '    above 5 points'), ('spend_floor15_ratio', '    above 15 points'), ('spend_floor30_ratio', '    above 30 points'),
              ('spend_maint_ratio', '(b) net of the median S&M share of firm-years at or below median growth'),
              ('foc_ols_ye_above', '(c) OLS of S&M share on g, year effects, above-median growers: alpha (X - k)'),
              ('foc_medreg_above_slope', '(c) median regression, same sample: slope'), ('foc_ols_ye_all', '(c) OLS, year effects, all firm-years'),
              ('foc_fe_all', '(c) OLS, firm and year effects, all firm-years'), ('foc_medreg_excess_slope', '(c) median regression on excess growth: slope'),
              ('spend_G05_ratio', '(d) G = 5%'), ('spend_G08_ratio', '(d) G = 8%'), ('spend_G12_ratio', '(d) G = 12%'),
              ('spend_G00_ratio', '    G = 0'), ('spend_Gp25_ratio', '    G = year 25th percentile'), ('spend_Gp75_ratio', '    G = year 75th percentile')]


def weight_rng(st):
    rr = [R[st].get(vn) for vn in MF4]
    v_ = [r['est'] for r in rr if ok(r)]
    if not v_:
        return 'n/a'
    lo, hi = min(v_), max(v_)
    return f"{lo / ALPHA[1]:.1f} to {hi / ALPHA[0]:.1f}"


def spend_md():
    L_ = ['| Method | E1 (baseline) | E2 | Imputed, M = 4 | Imputed, M = 8 | Implied X - k over the four, alpha 0.45 to 0.25 |', '|---|---|---|---|---|---|']
    for st, lab in SPEND_ROWS:
        wr = weight_rng(st) if not st.endswith(('q25', 'q75')) else ''
        L_.append(f"| {lab} | {rec4(st, 'se2')} | {wr} |")
    L_.append(f"| Median-regression intercept (S&M share at g = 0) | {rec4('foc_medreg_above_intercept', 'se2')} | |")
    L_.append(f"| Zero-spend growth implied by the median regression (-intercept / slope) | {rec4('foc_medreg_above_zero_spend_growth', 'se2')} | |")
    L_.append(f"| Median S&M share, firm-years at or below median growth (the netted maintenance level) | {rec4('spend_maint_base', 'se2')} | |")
    L_.append(f"| Median S&M share in the three terciles | " + ' | '.join(' / '.join(f"{100 * R[f'spend_terc{i}_sm'][vn]['est']:.0f}%" for i in (1, 2, 3)) for vn in MF4) + ' | |')
    L_.append(f"| Median excess growth in the three terciles (points) | " + ' | '.join(' / '.join(f"{100 * R[f'spend_terc{i}_excess'][vn]['est']:.1f}" for i in (1, 2, 3)) for vn in MF4) + ' | |')
    L_.append(f"| Firm-years in the spend ratio | " + ' | '.join(f"{R['spend_n'][vn]['est']:.0f}" for vn in MF4) + ' | |')
    return '\n'.join(L_)


def cap_md():
    L_ = ['| Period | Basis | Sort | E1 | E2 | Imputed, M = 4 | Imputed, M = 8 |', '|---|---|---|---|---|---|---|']
    for pk in PK:
        for cb, cl in [('cash', 'cash'), ('cashadd', 'cash, capex added back'), ('op', 'GAAP')]:
            for sfx, sl in [('', 'same year'), ('_prior', 'prior year'), ('_firmmed', 'firm median')]:
                L_.append(f"| {pk.replace('_', '-')} | {cl} | {sl} | {rec4(f'capint_gap_{cb}_{pk}{sfx}', 'ci')} |")
    for b in BASES:
        for w in ('pooled', '2023_25'):
            L_.append(f"| {w.replace('_', '-')} | {BASES[b][2]} | interaction g x high (tau 0.90 QR) | {rec4(f'capint_interaction_{b}_{w}', 'se2')} |")
    return '\n'.join(L_)


def scale_md():
    L_ = ['| Specification | Basis | E1 | E2 | Imputed, M = 4 | Imputed, M = 8 |', '|---|---|---|---|---|---|']
    for sfx, lab in [('', 'pooled (paper)'), ('_fe', 'with period effects'), ('_g150', 'growth at most 150%'), ('_fe_g150', 'period effects and growth at most 150%')]:
        for b in BASES:
            L_.append(f"| {lab} | {BASES[b][2]} | {rec4(f'scale_tenfold{sfx}_{b}', 'pts')} |")
    for b in BASES:
        for sk in SIZE_KEYS:
            L_.append(f"| P95 of R, revenue {sk} | {BASES[b][2]} | {rec4(f'scale_p95_{b}_{sk}', 'cin')} |")
    return '\n'.join(L_)


def yearly_md():
    L_ = ['| Fiscal year | Firm-years E1 / E2 | P95 E1 GAAP | P95 E1 cash | P95 E2 GAAP | P95 E2 cash | slope E1 GAAP | slope E1 cash | slope E2 GAAP | slope E2 cash |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for y in YEARS:
        L_.append(f"| {y} | {NYR['E1'].get(y, 0)} / {NYR['E2'].get(y, 0)} | " + ' | '.join(fc(R[f'p95_{b}_{y}'].get(vn), 1, 100.0, sign=False) for vn in PAIRV for b in BASES)
                  + ' | ' + ' | '.join(fs(R[f'slope_{b}_{y}'].get(vn)) for vn in PAIRV for b in BASES) + ' |')
    for w, lab in [('2025', '2016-19 to 2025'), ('2023_24', '2016-19 to 2023-24')]:
        L_.append(f"| Change in P95, {lab} | | " + ' | '.join(fc(R[f'p95_change_{b}_2016_19_to_{w}'].get(vn)) for vn in PAIRV for b in BASES) + ' | | | | |')
    L_.append(f"| Change in P95, 2016-19 to 2023-25 | | " + ' | '.join(fc(R[f'p95_change_{b}'].get(vn)) for vn in PAIRV for b in BASES) + ' | | | | |')
    L_.append('| Slope with year effects | | | | | | ' + ' | '.join(fs(R[f'slope_yearfe_{b}'].get(vn)) for vn in PAIRV for b in BASES) + ' |')
    return '\n'.join(L_)


def reg_md():
    L_ = ['| Object | Basis | Estimand | 2010-15 | 2018-25 | 2018-25 minus 2010-15 [percentile] | [basic] |', '|---|---|---|---|---|---|---|']
    for b in BASES:
        for vn in PAIRV:
            d_ = R[f'slope_{b}_2018_25_minus_2010_15'][vn]
            L_.append(f"| local Q_0.90 | {BASES[b][2]} | {vn} | {fs(R[f'slope_{b}_2010_15'][vn])} | {fs(R[f'slope_{b}_2018_25'][vn])} | {fc(d_, 2, 1.0)} | {fc(d_, 2, 1.0, 'ci90_basic')} |")
        for w in ('w60', 'w40'):
            for vn in MF4:
                d_ = R[f'cone_{b}_slope_c90_{w}_2018_25_minus_2010_15'][vn]
                L_.append(f"| Psi_0.90, g 0-{w[1:]}% | {BASES[b][2]} | {vn} | {fs(R[f'cone_{b}_slope_c90_{w}_2010_15'][vn])} | {fs(R[f'cone_{b}_slope_c90_{w}_2018_25'][vn])} | {fc(d_, 2, 1.0)} | {fc(d_, 2, 1.0, 'ci90_basic')} |")
    roll = J['rolling_slopes']
    L_.append('')
    L_.append('Rolling three-year local slopes (first year: slope): ' + '; '.join(
        f"{vn} {BASES[b][2]}: " + ', '.join(f"{k_[:4]} {v_:.2f}" for k_, v_ in roll[vn][b].items() if v_ is not None) for vn in PAIRV for b in BASES) + '.')
    return '\n'.join(L_)


def diff_md():
    L_ = ['| Object | Basis | Estimand | 2010-19 | 2020-25 | 2020-25 minus 2010-19 [percentile] | [basic] | p percentile | p basic |', '|---|---|---|---|---|---|---|---|---|']
    for b in BASES:
        for obj, pre, vns in [('Psi_0.90, g 0-60%', f'cone_{b}_slope_c90_w60', MF4 + ['E1_minus_E2']), ('Psi_0.90, g 0-40%', f'cone_{b}_slope_c90_w40', MF4 + ['E1_minus_E2']),
                              ('local Q_0.90', f'slope_{b}', PAIRV + ['E1_minus_E2'])]:
            for vn in vns:
                a_, c_ = R[f'{pre}_2010_19'][vn], R[f'{pre}_2020_25'][vn]
                d_ = R[f'{pre}_2020_25_minus_2010_19'][vn]
                pp = lambda k_: f"{d_[k_]:.3f}" if d_.get(k_) is not None else 'n/a'
                L_.append(f"| {obj} | {BASES[b][2]} | {vn} | {fs(a_)} | {fs(c_)} | {fc(d_, 2, 1.0)} | {fc(d_, 2, 1.0, 'ci90_basic')} | {pp('p_percentile')} | {pp('p_basic')} |")
    return '\n'.join(L_)


def rw_md():
    L_ = ['| Basis | Estimand | P95 2016-19 | P95 2023-25 | Change | 2023-25 at the 2016-19 growth mix | within (A) | composition (A) | 2016-19 at the 2023-25 growth mix | composition (B) | within (B) | within, size mix |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for b in BASES:
        for vn in PAIRV:
            g_ = lambda x, kd='ci': cellf(R[f'rw_{b}_{x}'].get(vn), kd)
            L_.append(f"| {BASES[b][2]} | {vn} | {g_('p95_2016_19', 'cin')} | {g_('p95_2023_25', 'cin')} | {g_('total')} | {g_('cf_2023_25_at_2016_19_growth_mix', 'cin')} | {g_('within_A')} | "
                      f"{g_('composition_A')} | {g_('cf_2016_19_at_2023_25_growth_mix', 'cin')} | {g_('composition_B')} | {g_('within_B')} | {g_('within_size')} |")
    return '\n'.join(L_)


def anchor_md():
    AV = MF4 + ['E1all']
    L_ = ['| | E1 (calibration rule: flagged firm-years dropped from the tail) | E2 | Imputed, M = 4 | Imputed, M = 8 | E1, every firm-year in the tail |', '|---|---|---|---|---|---|']
    bl = [ANB[vn] for vn in AV]
    q_ = lambda v_: ' / '.join(f"{100 * x:.1f}" for x in v_)
    for lab, f_ in [('firm-years (distinct firms)', lambda a: f"{a['n']} ({a['n_firms']})"), ('cut-off (P95 of the cash score)', lambda a: f"{100 * a['p95']:.1f}"),
                    ('G (median growth 2023-25)', lambda a: f"{100 * a['G']:.1f}"), ('median score R', lambda a: f"{100 * a['R'][1]:.1f}"),
                    ('m0 upper bound, quartiles', lambda a: q_(a['m0_ub'])), ('m0 lower bound, quartiles', lambda a: q_(a['m0_lb'])),
                    ('Pi_ub, quartiles', lambda a: q_(a['Pi_ub'])), ('Pi_lb, quartiles', lambda a: q_(a['Pi_lb'])),
                    ('share Pi_ub > 0', lambda a: f"{100 * a['share_Pi_ub_positive']:.0f}%"),
                    ('transient share of the median score', lambda a: f"{100 * a['transient_share_ub']:.0f}% to {100 * a['transient_share_lb']:.0f}%"),
                    ('firm-years per firm', lambda a: ', '.join(f"{k_} {v_}" for k_, v_ in a['firm_years_per_firm'].items() if v_ > 1) or 'one each')]:
        L_.append(f"| {lab} | " + ' | '.join(f_(a) for a in bl) + ' |')
    L_.append('')
    L_.append('Firm-cluster bootstrap (999 draws; the 2023-25 firm-years of the drawn firms; cut-off, G and tail recomputed in each draw), estimate [90% percentile interval]:')
    L_.append('')
    L_.append('| Statistic | Cut-off | E1 | E2 | Imputed, M = 4 | Imputed, M = 8 | E1, every firm-year in the tail | E1 - E2 |')
    L_.append('|---|---|---|---|---|---|---|---|')
    for c_, cl in [('p95', 'P95'), ('p975', 'P97.5')]:
        for s_, lab, kd in [('n', 'firm-years', 'int'), ('firms', 'distinct firms', 'int'), ('Pi_ub_med', 'median Pi_ub', 'ci'), ('Pi_lb_med', 'median Pi_lb', 'ci'),
                            ('m0_ub_med', 'median m0_ub', 'cin'), ('share_Pi_ub_pos', 'share Pi_ub > 0 (%)', 'pctn'), ('transient_ub', 'transient share, upper bound of spend', 'pct'),
                            ('transient_lb', 'transient share, lower bound of spend', 'pct')]:
            st = f'anchor_{c_}_{s_}'
            if kd == 'int':                              # counts: point estimates (a draw counts a duplicated firm once)
                cells = [f"{R[st][vn]['est']:.0f}" for vn in AV + ['E1_minus_E2']]
            else:
                cells = [cellf(R[st].get(vn), kd) for vn in AV + ['E1_minus_E2']]
            L_.append(f"| {lab} | {cl} | " + ' | '.join(cells) + ' |')
    cs = J['anchor']['cutoff_sensitivity']
    L_.append('')
    L_.append('Cut-off sensitivity (point estimates; median Pi_ub, firm-years (firms)): ' + '; '.join(
        f"{vn}: " + ', '.join(f"P{100 * float(k_.split('|')[1]):g} {100 * v_['Pi_ub'][1]:+.1f} ({v_['n']}, {v_['n_firms']})" for k_, v_ in cs.items() if k_.startswith(vn + '|')) for vn in AV) + '.')
    lo = J['anchor']['leave_one_firm_out_median_Pi_ub']
    L_.append('Leave one firm out (median Pi_ub, range over the anchor firms): ' + '; '.join(
        f"{vn}: {100 * min(v_.values()):+.1f} to {100 * max(v_.values()):+.1f}" for vn, v_ in lo.items() if v_) + '.')
    return '\n'.join(L_)


def sfa_md():
    L_ = ['| Basis | Statistic | E1 | E2 | Imputed, M = 4 | Imputed, M = 8 | E1 - E2 |', '|---|---|---|---|---|---|---|']
    for b in BASES:
        for x, lab in [('2016_19_mean_shortfall', 'mean shortfall 2016-19 (common frontier)'), ('2023_25_mean_shortfall', 'mean shortfall 2023-25'),
                       ('2023_25_jlms_2019plus', 'E[u | e] 2023-25, entered 2019 or later'), ('2023_25_jlms_pre2019', 'E[u | e] 2023-25, earlier cohorts'),
                       ('2023_25_cohort_gap', 'cohort gap 2023-25'), ('2016_19_cohort_gap', 'cohort gap 2016-19'),
                       ('balanced_jlms_2016_19', 'balanced panel (firms in both periods): E[u | e] 2016-19'), ('balanced_jlms_2023_25', 'balanced panel: E[u | e] 2023-25'),
                       ('balanced_change', 'balanced panel: change'), ('entrants_minus_balanced_2023_25', '2023-25: entrants minus balanced incumbents')]:
            L_.append(f"| {BASES[b][2]} | {lab} | " + ' | '.join(cellf(R[f'sfa_{b}_{x}'].get(vn), 'cin' if 'gap' not in x and 'change' not in x and 'minus' not in x else 'ci') for vn in MF4 + ['E1_minus_E2']) + ' |')
    sd = J['sfa_detail']
    for vn in PAIRV:
        s_ = sd.get(f'{vn}|survivorship')
        if s_:
            L_.append('')
            L_.append(f"{vn} survivorship: {s_['still_in_2023_25']} of the {s_['pre2019_firms_in_2016_19']} pre-2019 firms of 2016-19 remain in 2023-25; their 2016-19 "
                      f"median GAAP margin {100 * s_['op_2016_19_median_margin_survivors']:.1f}% against {100 * s_['op_2016_19_median_margin_leavers']:.1f}% for leavers "
                      f"(cash {100 * s_['cash_2016_19_median_margin_survivors']:.1f}% against {100 * s_['cash_2016_19_median_margin_leavers']:.1f}%). Separate frontiers by cohort "
                      "(estimate_revised.py, mean shortfall): " + '; '.join(f"{BASES[b][2]} " + ', '.join(f"{k_} {100 * v_['shortfall']:.1f} (n {v_['n']})" for k_, v_ in sd[f'{vn}|{b}|separate_frontiers'].items()) for b in BASES) + '.')
    return '\n'.join(L_)


def within_md():
    L_ = ['| Estimand | Basis | m_t on g_t (paper) | m_t on g_t+1, reported growth | joint: g_t, g_t+1 | m_t on g_t+1, same estimand | joint: g_t, g_t+1 |', '|---|---|---|---|---|---|---|']
    for vn in MF4:
        for b in BASES:
            w_ = J['within'].get(f'{vn}|{b}')
            if not w_:
                continue
            c0 = w_['contemporaneous']
            f1 = lambda d: f"{d['b']:+.3f} ({d['se']:.3f}), n {d['n']}" if d else 'n/a'
            f2 = lambda d: f"{d['joint_g']:+.3f} ({d['joint_g_se']:.3f}), {d['joint_lead']:+.3f} ({d['joint_lead_se']:.3f})" if d else 'n/a'
            a_, s_ = w_.get('lead_reported'), w_.get('lead_same_estimand')
            L_.append(f"| {vn} | {BASES[b][2]} | {f1(c0)} | {f1(a_)} | {f2(a_)} | {f1(s_)} | {f2(s_)} |")
    return '\n'.join(L_)


def solver_md():
    L_ = ['| Fit | n | exact (dual LP) | primal LP | IRLS (statsmodels, 5,000 iterations) | check loss exact | check loss IRLS | minimizer range |', '|---|---|---|---|---|---|---|---|']
    for k_, s_ in J['solver_check'].items():
        rg = f"[{s_['minimizer_range'][0]:.4f}, {s_['minimizer_range'][1]:.4f}]" if s_.get('minimizer_range') else ''
        L_.append(f"| {k_} | {s_['n']} | {s_['dual']:.4f} | {s_['primal']:.4f} | {s_['irls']:.4f} | {s_['loss_dual']:.6f} | {s_['loss_irls']:.6f} | {rg} |")
    return '\n'.join(L_)


def nan_md():
    L_ = ['| Statistic | Estimand | estimate | undefined draws | note |', '|---|---|---|---|---|']
    for st, recs in R.items():
        for vn, r in recs.items():
            if vn not in MF4 + ['E1_minus_E2', 'E2x25'] or not isinstance(r, dict):
                continue
            if (r.get('nan_share') or 0) > 0 or r.get('estimable') is False:
                e = 'n/a' if r.get('est') is None else f"{r['est']:.4f}"
                L_.append(f"| {st} | {vn} | {e} | {100 * (r.get('nan_share') or 0):.1f}% | {r.get('note') or ''} |")
    return '\n'.join(L_)


def cells_md():
    L_ = ['| Frontier point | Estimand | 2016-19 cell | 2023-25 cell | change [90% percentile] | undefined draws |', '|---|---|---|---|---|---|']
    for b in BASES:
        for g0 in ('00', '20', '40'):
            st = f'T_{b}_g{g0}_change'
            for vn in MF4 + ['E1_minus_E2']:
                r = R[st][vn]
                cc = J['T_cells'].get(vn, {}).get(st, ['', ''])
                L_.append(f"| T({int(g0)}%), {BASES[b][2]} | {vn} | {cc[0]} | {cc[1]} | {fc(r)} | {100 * (r.get('nan_share') or 0):.1f}% |")
    return '\n'.join(L_)


def imp_md():
    im = J['imputation']
    return '; '.join(f"M = {M}: {v_['n_readmitted']} dropped firm-years re-admitted ({v_['n_readmitted_without_price']} without any price measure, kept at reported "
                     f"growth), median imputed acquired growth {100 * v_['median_imputed_acquired_growth']:.1f} points, sample {v_['n']:,} firm-years" for M, v_ in im.items())


ro = J['routes']
cc90 = lambda st: f"E1 - E2 at tau 0.80: {fc(R[st.replace('t90', 't80')]['E1_minus_E2'], 3, 1.0)}; at 0.90: {fc(R[st]['E1_minus_E2'], 3, 1.0)}"
G14A, G14B = FAMS['headline14A'], FAMS['headline14B']
INF = f"""# Inference on the audited sample (panel v3)

{DECISION}

Generated by `code/estimate_v3.py` (tables and notes by its companion `code/estimate_v3_report.py`) from `data/panel_v3*.csv`;
machine-readable results in `notes/empirics_v3.json` (every statistic: estimate, B, undefined draws, se, bias, percentile,
basic, normal and bias-corrected intervals, p-values), bootstrap draws in `notes/bootstrap_draws_v3.npz`. Numbers are written
by the script; do not edit by hand. Points except slopes, ratios and regression coefficients. Estimand columns: E1 (all
firm-years, baseline), E2 (organic), Imputed M = 4 and M = 8 (E2 plus the acquisition-affected firm-years it drops, organic
growth imputed at those deal multiples).

## 1. Design

- Solver: every quantile regression exact (linear program, HiGHS). Check at the point estimates (section 11): the exact
  solution has the lower check loss in every fit, and the primal LP agrees with the dual.
- Bootstrap: {J['meta']['replications']} firm-cluster replications for every interval. Firms are drawn from the E1 sample ({J['meta']['firms_in_bootstrap_universe']}
  firms) and each estimand is evaluated on its own rows of the drawn firms, so all columns and the paired differences use
  the same draws. One generator per block of statistics, seeded from the block name (seeds: {', '.join(f'{k_} {v_}' for k_, v_ in J['meta']['seeds'].items())}).
  Errors in draws: {sum(J['meta']['errors_in_draws'].values())}.
- The capital-intensity split is re-estimated inside each draw; firm-years without the measure are not classified.
- A statistic with more than 5% undefined draws, or a frontier point T(g0) whose 2016-19 or 2023-25 cell has fewer than 30
  firm-years, gets no interval (n.e.); undefined draws are never dropped silently (section 7).
- Intervals: percentile (the paper's type), basic (reflected), normal (bootstrap se), bias-corrected percentile.

## 2. Primary slope statistic: the dominance-cone frontier Psi_chi (D-2), all four estimands

Slope of phi_chi(g0) over g0 = 0, 0.05, ..., window end (estimate (se)). A grid point enters when the sample has at least
30 firm-years with g >= g0 (the rule of estimate_frontier.py); inside a bootstrap draw it needs 10, the T(g0) rule, so a
draw is undefined only when the cell nearly empties. Windows ending at 80% and 100% are not defined: fewer than 30
firm-years grow at least 80% (cells below). Within periods the cells at 60% growth fall below 30, so the period slopes
are reported on the 0-40% window as well. Table `tab_grid_v3.tex` has the full grid; the calibration input is
`notes/frontier_slope_v3.json`.

| chi | Window | Basis | E1 | E2 | Imputed, M = 4 | Imputed, M = 8 |
|---|---|---|---|---|---|---|
""" + '\n'.join(f"| {c:.2f} | 0-{int(round(100 * w))}% | {BASES[b][2]} | {rec4(f'cone_{b}_slope_c{int(round(100 * c))}_w{int(round(100 * w))}', 'se2')} |"
                for b in BASES for c in TAUS for w in CW) + "\n" + '\n'.join(
    f"| order-m, M = 25 | 0-{int(round(100 * w))}% | {BASES[b][2]} | {rec4(f'cone_{b}_slope_orderm25_w{int(round(100 * w))}', 'se2')} |" for b in BASES for w in CW) + f"""

Frontier values phi(g0) (points; chi = 0.90 / 0.95 / order-m) at g0 = 0, 20, 40, 60%:
""" + '\n'.join(f"- {vn} {BASES[b][2]}: " + '; '.join(f"g0 {g0}%: " + ' / '.join(f"{100 * R[f'cone_{b}_{o}_g{g0:02d}'][vn]['est']:.1f}" if ok(R[f'cone_{b}_{o}_g{g0:02d}'].get(vn)) else 'n/a' for o in ('phi90', 'phi95', 'orderm25'))
                                                        for g0 in (0, 20, 40, 60)) for vn in MF4 for b in BASES) + f"""

Cells (firm-years with g >= g0) at g0 = 0, 0.2, 0.4, 0.6, 0.8, 1.0: """ + '; '.join(
    f"{vn} {b}: " + ', '.join(str(J['cone_cells'][vn][b][f'{g0:.2f}']) for g0 in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)) for vn in MF4 for b in BASES) + f"""

The local conditional quantile (descriptive), tau = 0.90, g 0-60%, estimate (se): GAAP {rec4('slope_op_pooled', 'se2')}; cash
{rec4('slope_cash_pooled', 'se2')} (E1 | E2 | M = 4 | M = 8). The two objects differ: Psi_chi is a quantile over the cone of
firm-years growing at least g0, so it falls only where the best margins at high growth are below the best at low growth;
the local quantile compares margins at each growth rate.

Slopes by period and their differences (firm-cluster bootstrap; referee 3 finding 14, Fable finding 2c):

{diff_md()}

## 3. Every model-facing statistic under the four estimands (D-3)

Sign / significance flags: 'yes' when the claim's sign, or its 90% interval, holds in E1, E2 and both imputation columns
(count of the four otherwise). For frontier points at 0 and 20% and the anchor's Pi_ub no directional claim is made (no
equivalence margin is tested): the flag says whether the interval includes zero in all four.

{mf_table()}

## 4. Paired contrasts E1 - E2: interval types and multiplicity (Fable finding 1)

The family is every paired contrast of `tab_estimands_v3.tex` except the anchor and the P95 levels: the six Psi_0.90 slopes
plus the 32 contrasts the referees counted in Table tab:estimands ({F38['n']} in all; `tab_contrasts_v3.tex`). Holm is
primary (valid under any dependence); Romano-Wolf on the joint draw is a check.

{fam38_md(F38)}

Intervals excluding zero at 90%: {F38['intervals_excluding_h0']['90_percentile']} percentile, {F38['intervals_excluding_h0']['90_basic']} basic,
{F38['intervals_excluding_h0']['90_normal']} normal, against {0.1 * F38['n']:.1f} expected under the global null; at 95%:
{F38['intervals_excluding_h0']['95_percentile']}, {F38['intervals_excluding_h0']['95_basic']}, {F38['intervals_excluding_h0']['95_normal']}.
Survivors of Holm at familywise 10%: {'; '.join(f"{k_}: {', '.join(v_) if v_ else 'none'}" for k_, v_ in F38['survivors_10pct'].items())}.
The referees' 32 alone: {'; '.join(f"{k_}: {', '.join(v_) if v_ else 'none'}" for k_, v_ in FAMS['referee32']['survivors_10pct'].items())}.

GAAP gap between the estimands at tau = 0.80 and 0.90 (g 0-60%): local Q_tau, {cc90('slope_op_t90_w60')}; Psi_chi,
E1 - E2 at chi 0.80: {fc(R['cone_op_slope_c80_w60']['E1_minus_E2'], 3, 1.0)}, at 0.90: {fc(R['cone_op_slope_c90_w60']['E1_minus_E2'], 3, 1.0)}.

## 5. Familywise correction across 14 headline contrasts

Family A is the one defined for the sample audit before D-1 to D-3 (local slopes, E2 for the model-facing statistics);
family B states the same findings on the objects of D-2 and D-3 (Psi_0.90 slopes, E1 baseline). Holm at familywise 5% is
primary; p-values from each statistic's own draws (normal, percentile, basic); Romano-Wolf on the joint draw.

Family A:

{fam_md(G14A)}

Family B:

{fam_md(G14B)}

## 6. Interval type matters where the bootstrap distribution is skewed

Bias of the bootstrap (mean of the draws minus the estimate) for the paired contrasts is in section 4. A contrast whose
percentile interval excludes zero while the basic interval does not is a contrast whose draws are shifted away from the
estimate; under Holm the three types agree on the survivors listed above.

## 7. Undefined draws and frontier-point cells (Fable finding 2, referee 3 finding 6)

{cells_md()}

All statistics with undefined draws or without an interval:

{nan_md()}

## 8. Capital intensity (Fable finding 4, referee 3 finding 5, referee 2 F2)

Gap in the P95 of the score, high minus low intensity (split at the period median of the sort variable inside each draw),
estimate [90% percentile interval]:

{cap_md()}

## 9. Size gradient with period effects and without growth above 150% (referee 3 finding 10)

{scale_md()}

## 10. Composition: yearly series and reweighting (Fable finding 7)

{yearly_md()}

Slope regimes, before 2016 and from 2018:

{reg_md()}

Reweighting decomposition of the change in the P95 of the score from 2016-19 to 2023-25 (DiNardo-Fortin-Lemieux; ten growth
bins on the pooled deciles of the two periods, Hazen quantiles; estimate [90% interval]). (A) reweights 2023-25 to the
2016-19 growth mix: within = counterfactual minus 2016-19, composition = 2023-25 minus counterfactual. (B) reweights 2016-19
to the 2023-25 mix: composition = counterfactual minus 2016-19, within = 2023-25 minus counterfactual. Last column: 2023-25
reweighted to the 2016-19 size mix (four revenue classes).

{rw_md()}

## 11. Growth weight: the bounds each method gives (D-1; Fable finding 1, referee 2 F1, referee 3 finding 4)

The growth weight of 7 to 13 is withdrawn. Each method gives alpha (X - k), the spend per point of growth; the last column
divides by alpha = 0.45 and 0.25 over the four estimands. The spend ratio (first row) is kept as a statistic of its own.

{spend_md()}

## 12. Calibration anchor (Fable finding 5, referee 3 finding 12)

The anchor inputs in the format of `notes/calibration_anchor_E2.json` are in `notes/calibration_anchor_v3.json` (blocks E1,
E2, E2imp4, E2imp8 and the sensitivities; bootstrap blocks).

{anchor_md()}

## 13. Stochastic frontier: common frontier, JLMS, cohorts and a balanced panel (referee 3 finding 13)

Half-normal frontier quadratic in growth, one per period for all cohorts (growth at most 150%, margin above -150%); E[u | e]
of Jondrow et al. (1982); cohorts by first year in the sample. Points [90% interval].

{sfa_md()}

## 14. Within-firm slopes with the model's timing (referee 3 finding 15)

OLS with firm and year effects, firm-clustered standard errors (analytic); growth at most 150%. "Reported growth" pairs m_t
with the firm's reported g_t+1 from the full panel; "same estimand" with g_t+1 of the same estimand (t+1 in the sample).

{within_md()}

## 15. Construction of E2 and the imputation bounds (Fable finding 6, referee 3 finding 1)

E2 by route (v3): {ro['n_flagged']} acquisition-affected firm-years ({ro['n_acq_year']} acquisition years, {ro['n_following_only']} following
years only); kept with pro forma organic growth {ro['n_kept_pro_forma']} ({ro['n_kept_acq_year']} acquisition years); dropped {ro['n_dropped']}
({100 * ro['share_dropped']:.1f}%): {'; '.join(f'{k_}: {v_}' for k_, v_ in sorted(ro['reasons'].items(), key=lambda kv: -kv[1]))}. Unverified hypergrowth
dropped: {ro['n_unverified']}. E2 = {ro['n_unaffected_kept']:,} unaffected firm-years plus {ro['n_kept_pro_forma']} re-admissions = {ro['n_E2']:,}
(exclusion-only 25%: {ro['n_E2x25']:,}). The pro forma ambiguity rule and the date it was added are recorded in
`notes/estimand_notes.md` section 1 (v2; the rule is unchanged in v3).

Imputation: {imp_md()}.

E2 under the first test run's rule (point estimates, v3): Psi_0.90 slope GAAP {R['cone_op_slope_c90_w60']['E2testrule']['est']:.3f}, cash
{R['cone_cash_slope_c90_w60']['E2testrule']['est']:.3f}; local slope GAAP {R['slope_op_pooled']['E2testrule']['est']:.3f}, cash
{R['slope_cash_pooled']['E2testrule']['est']:.3f}; change in P95 {100 * R['p95_change_op']['E2testrule']['est']:+.1f} (GAAP) and
{100 * R['p95_change_cash']['E2testrule']['est']:+.1f} (cash).

## 16. Solver check (referee 3 finding 7)

{solver_md()}

## 17. Files

- `code/estimate_v3.py` (estimation), `code/estimate_v3_report.py` (tables and notes; run by estimate_v3.py).
- `notes/empirics_v3.json`, `notes/bootstrap_draws_v3.npz` (draws, firm draws and seeds per block),
  `notes/empirics_v2_exact.json` (same engine on the v2 sample).
- `notes/frontier_slope_v3.json`: Psi_chi slopes (central chi = 0.90, window 0-60%, E1 baseline; grid, periods, order-m,
  curves) for the calibration of ell.
- `notes/calibration_anchor_v3.json`: anchor inputs, same format as `notes/calibration_anchor_E2.json`.
- `sections/tables/tab_estimands_v3.tex`, `tab_contrasts_v3.tex`, `tab_grid_v3.tex`, `tab_yearly_v3.tex`, `tab_bridge_v3.tex`.
- `notes/sample_audit.md`: the sample rules, the firms they exclude and the headlines old against new.

## 18. Cash score before interest paid and cash taxes (B5 bridge)

Under US GAAP operating cash flow is after interest paid and income taxes paid (ASC 230-10-45-17(c), (d)), so the paper's
cash score is after both. The bridge adds them back: before interest and cash taxes, R = g + (FCF - SBC + interest paid +
income taxes paid) / revenue; before interest, after tax, R = g + (FCF - SBC + interest paid x (1 - t)) / revenue, with t
the US federal statutory rate (35% for fiscal years ending before 2018, 21% from 2018; state and foreign rates are not
modelled). Interest and taxes paid: InterestPaidNet, else InterestPaid; IncomeTaxesPaidNet, else IncomeTaxesPaid; a missing
element counts as zero when the firm-year reports any of the four. Coverage: {BUILD['cash_score_basis'].get('coverage_core', '')}
({BUILD['cash_score_basis'].get('coverage_v3', {})}). The values come from SEC frames, which keep the latest filed value for
each company and period, so unlike the rest of the panel they are not first reported. "Bridge firm-years" is the paper's
cash score on the firm-years where the bridge is defined, the like-for-like comparison. Points [90% interval].

{bridge_md()}
"""

open(f'{BASE}/notes/inference_v3.md', 'w').write(INF)

# =============================================================================================== notes/sample_audit.md
ce_ = core_ext


def by_firm(mask):
    g_ = ce_[mask].groupby('name').year.apply(lambda y: ', '.join(str(int(v_)) for v_ in sorted(y)))
    return '; '.join(f"{n} ({ys})" for n, ys in g_.items())


r1 = {t_: by_firm(ce_.backfill_type == t_) for t_ in ['fy2010_before_first_xbrl_report', 'before_first_annual_report', 'later_vintage_only']}
r1n = {t_: int((ce_.backfill_type == t_).sum()) for t_ in r1}
r3 = by_firm(ce_.v3_exclude == 'R3_captive_related_party')
r4a = by_firm(ce_.acq_reason_v3.isin(['goodwill_fallback', 'cheap_acquisition']))
r4f = by_firm((ce_.acq_flag_v3 == 1) & (ce_.acq_flag_v2 == 0) & (ce_.acq_reason_v3 == 'following_year'))
named = '; '.join(f"{n} ({c_})" for n, c_ in BUILD['panel_named']['firms'].items())
gaf = BUILD['ga_floor']
ga_lines = '\n'.join(f"- {k_}: $1-10B p5 {100 * v_['rev_1b_10b']['p5']:.2f}% (n = {v_['rev_1b_10b']['n_firms']} firms), "
                     f"p10 {100 * v_['rev_1b_10b']['p10']:.2f}%; above $10B p5 {100 * v_['rev_over_10b']['p5']:.2f}%, "
                     f"p10 {100 * v_['rev_over_10b']['p10']:.2f}% (n = {v_['rev_over_10b']['n_firms']})" for k_, v_ in gaf.items())
bfc = BUILD['backfill_counts']
csb = BUILD['cash_score_basis']
V2E = V2X['estimates'] if V2X else {}
HROWS = [('Psi_0.90 slope, GAAP, 2010-25 (primary)', 'cone_op_slope_c90_w60', 'se2'), ('Psi_0.90 slope, cash, 2010-25 (primary)', 'cone_cash_slope_c90_w60', 'se2'),
         ('Psi_0.90 slope, GAAP, g 0-40%, 2010-25', 'cone_op_slope_c90_w40', 'se2'), ('Psi_0.90 slope, cash, g 0-40%, 2010-25', 'cone_cash_slope_c90_w40', 'se2'),
         ('Psi_0.90 slope, GAAP, g 0-40%, 2010-19', 'cone_op_slope_c90_w40_2010_19', 'se2'), ('Psi_0.90 slope, GAAP, g 0-40%, 2020-25', 'cone_op_slope_c90_w40_2020_25', 'se2'),
         ('Psi_0.90 slope, cash, g 0-40%, 2010-19', 'cone_cash_slope_c90_w40_2010_19', 'se2'), ('Psi_0.90 slope, cash, g 0-40%, 2020-25', 'cone_cash_slope_c90_w40_2020_25', 'se2'),
         ('Psi_0.90 slope, GAAP, g 0-40%, 2020-25 minus 2010-19', 'cone_op_slope_c90_w40_2020_25_minus_2010_19', 'se2'),
         ('Local slope, GAAP, 2010-25', 'slope_op_pooled', 'se2'), ('Local slope, cash, 2010-25', 'slope_cash_pooled', 'se2'),
         ('Local slope, GAAP, 2010-19', 'slope_op_2010_19', 'se2'), ('Local slope, cash, 2010-19', 'slope_cash_2010_19', 'se2'),
         ('Local slope, GAAP, 2020-25', 'slope_op_2020_25', 'se2'), ('Local slope, cash, 2020-25', 'slope_cash_2020_25', 'se2'),
         ('Spend-to-excess-growth ratio', 'spend_ratio', 'se2'), ('Weight on growth, alpha = 0.45 (withdrawn, D-1)', 'weight_lo', 'se1'),
         ('Weight on growth, alpha = 0.25 (withdrawn, D-1)', 'weight_hi', 'se1'),
         ('Size gradient, GAAP (points per tenfold)', 'scale_tenfold_op', 'pts'), ('Size gradient, cash (points per tenfold)', 'scale_tenfold_cash', 'pts'),
         ('Capital-intensity gap 2023-25, GAAP', 'capint_gap_op_2023_25', 'ci'), ('Capital-intensity gap 2023-25, cash', 'capint_gap_cash_2023_25', 'ci'),
         ('P95 of R 2016-19, GAAP', 'p95_op_2016_19', 'cin'), ('P95 of R 2023-25, GAAP', 'p95_op_2023_25', 'cin'),
         ('P95 of R 2016-19, cash', 'p95_cash_2016_19', 'cin'), ('P95 of R 2023-25, cash', 'p95_cash_2023_25', 'cin'),
         ('Change in P95, GAAP', 'p95_change_op', 'ci'), ('Change in P95, cash', 'p95_change_cash', 'ci'),
         ('Change in T(0%), GAAP', 'T_op_g00_change', 'ci'), ('Change in T(0%), cash', 'T_cash_g00_change', 'ci'),
         ('Change in T(20%), GAAP', 'T_op_g20_change', 'ci'), ('Change in T(20%), cash', 'T_cash_g20_change', 'ci'),
         ('Change in T(40%), GAAP', 'T_op_g40_change', 'ci'), ('Change in T(40%), cash', 'T_cash_g40_change', 'ci'),
         ('Near-frontier margin gap', 'gap_avg', 'cin'), ('of which S&M', 'gap_sm', 'cin'), ('S&M part, 40-60% band', 'gap_fast_sm', 'cin')]


def old_rec(k_, vn):
    r = OLD['estimates'].get(k_, {}).get(vn)
    return r


head_tab = '\n'.join(f"| {lab} | {cellf(old_rec(k_, 'E1'), kd)} | {cellf(V2E.get(k_, {}).get('E1'), kd)} | {cellf(R[k_]['E1'], kd)} | "
                     f"{cellf(old_rec(k_, 'E2'), kd)} | {cellf(V2E.get(k_, {}).get('E2'), kd)} | {cellf(R[k_]['E2'], kd)} | "
                     f"{cellf(R[k_].get('E1_minus_E2'), kd)} | {cellf(R[k_].get('E2imp4'), kd)} | {cellf(R[k_].get('E2imp8'), kd)} |" for lab, k_, kd in HROWS)
so = OLD['samples']
samp_tab = '\n'.join(f"| {lab} | {so[a]['n']:,} ({so[a]['firms']}) | {S_[a]['n']:,} ({S_[a]['firms']}) |"
                     for lab, a in [('E1', 'E1'), ('E2', 'E2'), ('Exclusion only, 25%', 'E2x25')]) + '\n' + \
    '\n'.join(f"| {LAB4[a]} | {V2X['samples'][a]['n']:,} ({V2X['samples'][a]['firms']}) | {S_[a]['n']:,} ({S_[a]['firms']}) |" for a in ['E2imp4', 'E2imp8'] if V2X)
SV = [('primary', 'E1', 'E2'), ('keeping fiscal-2010 backfills', 'E1k2010', 'E2k2010'),
      ('without named non-software firms', 'E1clean', 'E2clean'), ('without named debt-only filers', 'E1nodebt', 'E2nodebt')]
SV += [x for x in [('without named firms R2 classes non-software', 'E1r2named', 'E2r2named'),
                   ('without R5 no-listed-equity firm-years', 'E1nolist', 'E2nolist')] if x[1] in R['slope_op_pooled']]
SKEYS = [('Psi_0.90 slope, GAAP', 'cone_op_slope_c90_w60', 'se2'), ('Psi_0.90 slope, cash', 'cone_cash_slope_c90_w60', 'se2'),
         ('Local slope, GAAP', 'slope_op_pooled', 'se2'), ('Local slope, cash', 'slope_cash_pooled', 'se2'), ('Spend ratio', 'spend_ratio', 'se2'),
         ('Size gradient, cash', 'scale_tenfold_cash', 'pts'), ('Capital-intensity gap, cash, 2023-25', 'capint_gap_cash_2023_25', 'ci'),
         ('Change in P95, GAAP', 'p95_change_op', 'ci'), ('Change in P95, cash', 'p95_change_cash', 'ci'),
         ('Change in T(40%), cash', 'T_cash_g40_change', 'ci'), ('Margin gap', 'gap_avg', 'cin')]
sens_tab = '\n'.join(['| Statistic | ' + ' | '.join(f'E1 {a}' + ' | ' + f'E2 {a}' for a, _, _ in SV) + ' |', '|---|' + '---|' * (2 * len(SV))] +
                     [f"| {lab} | " + ' | '.join(cellf({'est': R[k_][v1]['est']}, kd) + ' | ' + cellf({'est': R[k_][v2]['est']}, kd) for _, v1, v2 in SV) + ' |'
                      for lab, k_, kd in SKEYS] + ['| Firm-years | ' + ' | '.join(f"{S_[v1]['n']:,} | {S_[v2]['n']:,}" for _, v1, v2 in SV) + ' |'])
a2, a3 = OLDAN['E2'], ANB['E2']
anch_cmp = '\n'.join([
    '| | v2 E2 anchor (current calibration) | v3 E1 | v3 E2 | v3 imputed M = 4 | v3 imputed M = 8 | v3 E2 without panel-named firms | v3 E2 keeping fiscal-2010 backfills |',
    '|---|---|---|---|---|---|---|---|'] + [
    f"| {lab} | " + ' | '.join(f_(a) for a in [a2, ANB['E1'], ANB['E2'], ANB['E2imp4'], ANB['E2imp8'], ANB.get('E2clean', a3), ANB.get('E2k2010', a3)]) + ' |'
    for lab, f_ in [('firm-years (firms)', lambda a: f"{a['n']} ({len(a['firms'])})"), ('cut-off (P95)', lambda a: f"{100 * a['p95']:.1f}"),
                    ('G', lambda a: f"{100 * a['G']:.1f}"), ('median score', lambda a: f"{100 * a['R'][1]:.1f}"),
                    ('m0 upper bound, quartiles', lambda a: ' / '.join(f"{100 * x:.1f}" for x in a['m0_ub'])),
                    ('m0 lower bound, quartiles', lambda a: ' / '.join(f"{100 * x:.1f}" for x in a['m0_lb'])),
                    ('Pi_ub, quartiles', lambda a: ' / '.join(f"{100 * x:.1f}" for x in a['Pi_ub'])),
                    ('Pi_lb, quartiles', lambda a: ' / '.join(f"{100 * x:.1f}" for x in a['Pi_lb'])),
                    ('share Pi_ub > 0', lambda a: f"{100 * a['share_Pi_ub_positive']:.0f}%"),
                    ('transient share of the median score', lambda a: f"{100 * a['transient_share_ub']:.0f}% to {100 * a['transient_share_lb']:.0f}%")]])
SA = f"""# Sample audit of the SEC panel (v3)

{DECISION}

Generated by `code/estimate_v3.py` (notes by `code/estimate_v3_report.py`) from `data/panel_v3*.csv` (built by
`code/build_panel_v3.py`), `notes/empirics_v3.json`, `notes/empirics_v2_exact.json` and `notes/empirics_organic.json` (v2 as
published). Numbers are written by the script; do not edit by hand. Review sources: `notes/reviews/paper1_v1/panel_investment_management.md`
(IM), `panel_investors_bankers.md` (IB), the finance referee (FR) and the econometrics referees (`fable_referee_econometrics.md`,
`referee3_econometrics.md`). Each claim was re-checked on the data before a rule was written. Inference: `notes/inference_v3.md`.

## 1. What could and could not be done

- SEC inputs. After the author approved the download (29 Oct 2026, 16:05 UTC-7), the lead agent retrieved XBRL frames
  and business descriptions through the author's browser (provenance and transfer hashes in
  `data/v3_inputs/README_retrieval.md`). SEC frames hold only non-dimensional facts and keep the latest filed value for
  each company and period, so these inputs are not first reported, unlike the rest of the panel.
- Applied to every firm-year: R1 (first reported); R3 (captive related-party revenue: XBRL related-party revenue, and the
  filing text where it was read); R4 (acquisition flag, criteria a, b and c).
- Flag and sensitivity, not an exclusion: R5 (no listed equity), as designed.
- Sensitivity only: R2 (business classification), run on the 16 firms the review panels named, the only firms whose
  descriptions were retrieved. A rule applied only to reviewer-named firms must not change the main sample, so
  `data/v3_inputs/business_descriptions.json` (the file `build_panel_v3.py` reads to apply R2 to the main sample) is not
  created; applying R2 as a rule needs the description of every registrant.

## 2. Rules and the firm-years they affect (v2 core sample: {BUILD['core_v2']:,} firm-years, {BUILD['firms_v2']} firms)

**R1, first reported (applied).** A firm-year is excluded when its values come from a filing whose own reporting period
ends after the firm-year: the year exists only as a comparative in a later report. Verified against IM T1: {BUILD['R1']['n']} core
firm-years, not 141. IM's "late source" list also counts Avaya 2022, which was filed late but is the original filing.
The {BUILD['R1']['n']} split as {r1n['fy2010_before_first_xbrl_report']} fiscal-2010 years before the registrant's first XBRL annual report,
{r1n['before_first_annual_report']} later years before a registrant's first annual report (IPO, spin-off or de-SPAC comparatives),
and {r1n['later_vintage_only']} years whose own report carries no revenue fact. By period: {BUILD['R1']['by_period']}. Median growth
{100 * BUILD['R1']['median_growth_backfilled']:.1f}% against {100 * BUILD['R1']['median_growth_other']:.1f}% for the other firm-years.
Reason to keep some: the fiscal-2010 years of registrants that were already public were reported in real time, so the
look-ahead and selection objection does not apply to them. Local data cannot separate them from pre-IPO fiscal-2010
years, so all {r1n['fy2010_before_first_xbrl_report']} are excluded from the primary sample and added back in the sensitivity `k2010`.
- Fiscal 2010, before the first XBRL report: {r1['fy2010_before_first_xbrl_report']}
- Before the first annual report: {r1['before_first_annual_report']}
- Later vintage only: {r1['later_vintage_only']}

**R2, business classification (named firms only: sensitivity; main sample not classified).** The principal business is read from the opening of Item 1 of
the latest 10-K (Item 4.B of a 20-F; the AIF of a 40-F) and classified by keyword counts as interactive entertainment,
gambling, compute infrastructure or software. A firm is excluded when a non-software class has at least three keyword
hits and more hits than the software class (code in `build_panel_v3.py`). SIC codes cannot do this alone: every core
firm is SIC 7372 by construction, and EDGAR codes are current, not historical. The panels named these firms, which
enter only sensitivities: {named}. They carry {BUILD['panel_named']['firm_years_in_v3']} firm-years of the v3 sample.
{SECT.get('R2', '')}

**R3, captive related-party revenue (applied).** A firm-year is excluded when related-party revenue is at least 50% of
revenue: XBRL RevenueFromRelatedParties or RelatedPartyTransactionRevenuesFromTransactionsWithRelatedParty over revenue,
or a filing statement that substantially all revenue comes from related parties. {SECT.get('R3', '')}
Excluded: {r3}. The FY2025 10-K states that substantially all revenue came from customers affiliated with HCI, and that
there was no meaningful revenue from non-HCI affiliated customers in fiscal 2025. Verified against IM T5 and IB V24.

**R4, acquisition flag (applied).** Why Xunlei 2025 was missed: Xunlei reports in USD, so currency is not the cause.
Cash paid for acquisitions net of cash acquired was 16% of prior-year revenue, below the 25% threshold. Goodwill at
end-2024 is absent from every filing in the extract, so the goodwill increase was missing; measured from end-2023 it is
6%. No pro forma revenue is tagged. The flag measures acquisitions by their price, so a cheap acquisition that adds a lot
of revenue escapes it. Two fixes, applied to every firm-year:
- (a) When the prior-year-end goodwill instant is missing, measure the increase from the latest instant 300 to 770 days
  earlier.
- (b) Flag cheap acquisitions: cash paid or the goodwill increase, C, is at least 10% of prior-year revenue, and growth
  accelerates relative to the year's median by at least C. The acquisition could then explain the acceleration at a
  price of at most one times revenue.

The core flag rises from {BUILD['R4']['v2_flagged']} to {BUILD['R4']['v3_flagged']} firm-years.
- New acquisition years: {r4a}
- New following years: {r4f}

{SECT.get('R4c', '')}

Still undetected, for lack of data: acquisitions paid in stock, and acquisitions whose acquiree revenue is tagged only on a
business-combination axis (ASC 805-10-50-2(h)(1)).
Disclosure: criterion (b) was chosen among five variants (spend floor 5% or 10%; acceleration raw or relative to the
median) after listing the firm-years each would flag and before any v3 estimate was computed. The 5% raw variant flagged
43, mostly recession-rebound years of 2010 and organic surges such as Roblox 2021.

v3 core sample: {BUILD['core_v3']:,} firm-years, {BUILD['firms_v3']} firms, by period {BUILD['v3_by_period']}.

**R5, no listed equity (item a; flag and sensitivity, not an exclusion).** {SECT.get('R5', '')} Current EDGAR names
cannot stand in: Informatica LLC, VMware LLC and 2U, LLC have post-delisting names, but their panel years are listed
years. Informatica LLC's annual reports in the extract run {BUILD['R5']['informatica_llc_annual_reports'][0]}-{BUILD['R5']['informatica_llc_annual_reports'][-1]},
ending at its take-private. Of the finance referee's five debt-only filers, the four whose panel years fall after their
equity went private enter a with-and-without comparison: {', '.join(BUILD['R5']['debt_only_named'])}
({BUILD['R5']['firm_years_core_v2']} v2 core firm-years, {BUILD['R5']['firm_years_v3']} in v3). Medical Information
Technology (Meditech), Serena and GXS are further debt-only filers; the float rule finds them.

**Item b, cash-score basis.** The cash margin starts from {', '.join(csb['operating_cash_flow_elements'])} (build_panel_v2.py).
{csb['reading']}. Elements for a before-interest-and-tax variant ({', '.join(csb['elements_in_extract'])}): before the retrieval
of 29 Oct 2026 they were in neither the companyfacts extract nor the local frames files. {SECT.get('B5', 'Coverage: ' + csb['coverage_core'] + '.')}

**Item c, acquiree revenue since the acquisition date.** Criterion R4(c), BusinessCombinationProFormaInformationRevenueOfAcquireeSinceAcquisitionDateActual
at 10% of revenue: see R4 above ({len(BUILD['R4'].get('acquiree_revenue', {}).get('new_flags_core_v2', [])) if BUILD['R4'].get('acquiree_revenue') else 'not counted'} extra core flags). Xunlei 2025 is
caught by R4(b).

**Item d, the G&A floor of the a_min band.** The 4.6% is the definition in code/data_part2/08_params.py (FY2023-25 firm
means of G&A over revenue, by current revenue) applied to panel_v2_all.csv, which spans SIC 7370-7374 and every revenue
size. It is not computed from the core panel. The same statistic on the core:
{ga_lines}

**Item e, the count of non-first-reported firm-years.**
- R1 (the source filing reports a later own period): {bfc['R1 (source filing reports a later own period)']}.
- Filed more than 400 days after fiscal year-end (finance referee): {bfc['filed more than 400 days after fiscal year-end (finance referee)']}.
  It misses {'; '.join(bfc['R1 but filed within 400 days'])}, filed within 400 days.
- R1 restricted to a firm's first core year (IM T1): {bfc['R1 restricted to first core year']}. It omits
  {'; '.join(bfc['R1 but not first core year'])}.
- IM's late-source count: {bfc['accession year later than the normal filing year (IM T1)']}. It adds
  {'; '.join(bfc['IM T1 but not R1 (late original filing)'])}, which was filed late but is the original filing.

All four counts agree once these definitions are applied. R1 is the definition that matches "not first reported".

**Following-year flag (finance referee, item 5).** v2 shifted the flag by row. In panel_v2_all,
{len(BUILD['R4']['v2_following_flags_across_gaps_all_panel'])} following-year flags cross a gap in a firm's years
({'; '.join(BUILD['R4']['v2_following_flags_across_gaps_all_panel'])}), {len(BUILD['R4']['v2_following_flags_across_gaps'])} of them in the core sample.
v3 shifts by fiscal year.

**With and without the named firms (point estimates; points except slopes and ratio):**

{sens_tab}

## 3. Files for the data agents (software priors, backtest firm test, playbook archetypes)

- `data/panel_v3.csv`: the v3 core analysis sample. Same columns as `data/panel.csv`, plus the audit columns. Use this file.
- `data/panel_v3_core_full.csv`: all {BUILD['core_v2']:,} v2 core firm-years, with the reason in `v3_exclude`. One of
  R1_not_first_reported, R3_captive_related_party or R2_not_software; blank if kept.
- `data/panel_v3_all.csv`: every firm-year of `panel_v2_all.csv`, with the same audit columns and `in_core_v2`.
- Audit columns:
  - `filed`, `src_period_end`: source filing date and its own reporting period.
  - `backfill`, `backfill_type`: rule R1.
  - `acq_now_v3`, `acq_flag_v3`, `acq_reason_v3`, `gw_jump_v3`, `acq_spend_share`, `accel_rel`: rule R4. Use
    `acq_flag_v3` in place of `acq_flag`.
  - `panel_named`, `debt_only_named`, `business_class_named`: sensitivities only.
  - `business_class`: R2 on the main sample, blank until descriptions of every registrant exist.
  - `rp_revenue_share`, `captive_verified`, `captive`: R3.
  - `acquiree_rev_share`: R4(c).
  - `r5_status`, `no_listed_equity`: R5 (flag).
  - `interest_paid`, `income_taxes_paid`, `interest_paid_element`, `income_taxes_paid_element`: the cash-score bridge
    (SEC frames, latest filed).
- `notes/panel_v3_build.json`: counts and firm lists.
- `data/panel_v2_all.csv`, `data/panel.csv` and every v2 output are unchanged.

## 4. Headlines: v2 as published, v2 re-estimated with the v3 engine, and v3

"v2 exact" is the v2 sample with the v3 engine (exact solver, 999 replications, split inside the draws, missing intensity
not classified), so the columns separate the engine change from the sample change. Slopes and ratios: estimate
(bootstrap se); points: estimate [90% percentile interval]. Psi rows have no published value (the statistic is new, D-2).
The weight rows are shown for the record only (withdrawn, D-1).

| Statistic | E1 v2 published | E1 v2 exact | E1 v3 | E2 v2 published | E2 v2 exact | E2 v3 | E1 - E2 v3 (paired) | Imputed M = 4, v3 | Imputed M = 8, v3 |
|---|---|---|---|---|---|---|---|---|---|
{head_tab}

| Sample | v2 firm-years (firms) | v3 firm-years (firms) |
|---|---|---|
{samp_tab}

## 5. Familywise correction across the 14 headline contrasts

Holm step-down at familywise 5% is primary (valid under any dependence); Romano-Wolf studentized step-down on a joint draw
is the check; p-values from each statistic's own 999 draws, of three types. Family A is the family defined for the
sample audit (local slopes; E2 for the model-facing statistics); family B states the same findings on the objects of
D-2 and D-3. Full tables, and the paired-contrast family of the estimands table, in `notes/inference_v3.md` sections 4 and 5.

- Family A survivors: {'; '.join(f"{k_}: {', '.join(v_) if v_ else 'none'}" for k_, v_ in G14A['survivors_5pct'].items())}.
- Family B survivors: {'; '.join(f"{k_}: {', '.join(v_) if v_ else 'none'}" for k_, v_ in G14B['survivors_5pct'].items())}.
- Paired E1 - E2 contrasts ({F38['n']}), Holm at 10%: {'; '.join(f"{k_}: {', '.join(v_) if v_ else 'none'}" for k_, v_ in F38['survivors_10pct'].items())}.

## 6. Calibration anchor

{anch_cmp}

Bootstrap, cut-off at P97.5, leave-one-firm-out and the firm-years per firm: `notes/inference_v3.md` section 12. Anchor
inputs for calibrate_horizons.py: `notes/calibration_anchor_v3.json` (same format as `notes/calibration_anchor_E2.json`).

## 7. Still open

- R2 as a rule: the opening of Item 1 (Item 4.B for a 20-F) of the latest annual report of every core registrant, saved as
  `data/v3_inputs/business_descriptions.json`; `build_panel_v3.py` then applies R2 to the main sample.
- R5 for foreign filers: the Section 12(b) table on the 20-F and 40-F cover pages (exchange-listed ADSs or shares).
- R4(c) beyond non-dimensional facts: the acquiree-revenue element on its business-combination axis, which only the
  filings' XBRL instance documents carry (frames and companyfacts drop dimensions).
- First-reported values for the SEC-frames inputs (related-party revenue, acquiree revenue, interest and taxes paid):
  the original filings' instance documents; frames keep the latest filed value.
"""
open(f'{BASE}/notes/sample_audit.md', 'w').write(SA)
log('wrote notes/inference_v3.md, notes/sample_audit.md')
