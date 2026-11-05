#!/usr/bin/env python3
"""Supplement Section supp:extensions: three analyses added after the third review round (author's decision, 4 Nov 2026).

They were first built for the plain-language companion page and checked there by an independent agent; this script
formats them for the paper and tests every qualitative statement the section makes (check_text_claims), stopping if a
rerun no longer supports one.

Inputs (all committed outputs; nothing here is estimated twice):
  notes/open_questions/valuation.json   code/biz_valuation.py: log(public float / revenue) on growth and margin
  notes/open_questions/paths.json       code/biz_open_questions.py: paths of a firm that does not automate (Paper 1's
                                        pass-through scenario with the firm's own automation set to zero)
  notes/mc_results_2026-11-03_1m/draws_lhs.csv.gz and mc_claims.json   the million-draw stress test (Section supp:stress)
  Paper 1's calibration, loaded unchanged in a shadow tree (code/mc_claims.py load_calibration), for the central-case sweeps
Outputs:
  paper1/ext_macros.tex                  \\Ex* macros (input from paper1/macros.tex, as stress_macros.tex is)
  sections/tables/tab_ext_valuation.tex  Table tab:ext-valuation
  sections/tables/tab_ext_nothing.tex    Table tab:ext-nothing
  sections/tables/tab_ext_payback.tex    Table tab:ext-payback
Run after code/biz_open_questions.py and code/biz_valuation.py:  python3 code/supp_extensions.py
"""
import importlib.util
import json
import math
import os
import sys
import tempfile

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MC = os.path.join(BASE, 'notes', 'mc_results_2026-11-03_1m')
V = json.load(open(os.path.join(BASE, 'notes', 'open_questions', 'valuation.json')))
P = json.load(open(os.path.join(BASE, 'notes', 'open_questions', 'paths.json')))
J = json.load(open(os.path.join(MC, 'mc_claims.json')))
M = {}
CHECKS = []


def half_up(x, nd=0):
    q = 10 ** nd
    return math.floor(x * q + 0.5) / q


def fnum(x, nd):
    s = f"{half_up(x, nd):.{nd}f}"
    return f"$-${s[1:]}" if s.startswith('-') else s


def fint(n):
    return f"{int(n):,}".replace(',', '{,}')


def put(k, v):
    assert k.startswith('Ex') and k.isalpha(), k
    assert k not in M, k
    M[k] = v


def claim(text, ok):
    CHECKS.append((text, bool(ok)))


# ------------------------------------------------------------------------------------------------ (a) valuation
SAMPLES = [('all', 'All firm-years'), ('2010-19', '2010--19'), ('2020-25', '2020--25'),
           ('no_acq', 'No acquisition-affected years'), ('top40', 'Score of 40 or more')]
BASIS = [('cash', 'Free cash flow after SBC'), ('gaap', 'GAAP operating margin')]
put('ExPanelN', fint(V['n_panel'])); put('ExMatchN', fint(V['n_matched'])); put('ExMatchFirms', str(V['firms']))
U = V['unmatched']
put('ExUnmN', fint(U['total'])); put('ExUnmNoFloat', str(U['registrant_without_float'])); put('ExUnmLate', str(U['fy2025']))
put('ExUnmOther', str(U['total'] - U['registrant_without_float'] - U['fy2025']))
put('ExMultMed', fnum(V['median_multiple'], 1))
for b, _ in BASIS:
    for s, _ in SAMPLES:
        assert V[b].get(s), (b, s)
# Interval convention (revision of 5 November 2026, outside re-review GPT F08): weight_ci90 is the 5th to 95th percentile of
# beta_g / beta_m over the bootstrap samples with beta_m > 0, and weight_share_bm_nonpositive the share of samples with
# beta_m <= 0; the table gives no upper end where that share exceeds one in twenty. A missing or non-finite end is an
# error here (it was printed as infinity before), never a table entry.
MAX_BAD = 0.05
for b, _ in BASIS:
    for s, _ in SAMPLES:
        r = V[b][s]
        if r['weight'] is None:
            assert 'weight_ci90' not in r, (b, s)
            continue
        ci, bad = r.get('weight_ci90'), r.get('weight_share_bm_nonpositive')
        if ci is None or bad is None or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in list(ci) + [bad]):
            sys.exit(f'supp_extensions: valuation interval for {b}/{s} is missing or not finite ({ci}, {bad}); rerun code/biz_valuation.py')
c, g = V['cash']['all'], V['gaap']['all']
put('ExNCash', fint(c['n'])); put('ExNGaap', fint(g['n'])); put('ExFirmsCash', str(c['firms']))
put('ExWCash', fnum(c['weight'], 1)); put('ExWCashLo', fnum(c['weight_ci90'][0], 1)); put('ExWCashHi', fnum(c['weight_ci90'][1], 1))
put('ExWGaap', fnum(g['weight'], 1)); put('ExWGaapLo', fnum(g['weight_ci90'][0], 1)); put('ExWGaapHi', fnum(g['weight_ci90'][1], 1))
put('ExBgCash', fnum(c['beta_g'], 2)); put('ExBmCash', fnum(c['beta_m'], 2))
put('ExWNoAcqCash', fnum(V['cash']['no_acq']['weight'], 1)); put('ExWNoAcqGaap', fnum(V['gaap']['no_acq']['weight'], 1))
put('ExWEarlyCash', fnum(V['cash']['2010-19']['weight'], 1)); put('ExWLateCash', fnum(V['cash']['2020-25']['weight'], 1))
put('ExRFullCash', fnum(100 * c['r2_within_full'], 0)); put('ExRScoreCash', fnum(100 * c['r2_within_score'], 0))
put('ExRFullGaap', fnum(100 * g['r2_within_full'], 0)); put('ExRScoreGaap', fnum(100 * g['r2_within_score'], 0))
t = V['cash']['top40']
put('ExTopN', fint(t['n'])); put('ExTopRScore', fnum(100 * t['r2_within_score'], 1)); put('ExTopRFull', fnum(100 * t['r2_within_full'], 1))
put('ExTopPCash', fnum(t['equal_weights_p'], 2)); put('ExTopPGaap', fnum(V['gaap']['top40']['equal_weights_p'], 2))
put('ExWCashBad', fnum(100 * c['weight_share_bm_nonpositive'], 1)); put('ExWGaapBad', fnum(100 * g['weight_share_bm_nonpositive'], 1))
claim('valuation: in both all-firm-year samples at most one bootstrap sample in twenty has beta_m <= 0, so both upper ends are given',
      c['weight_share_bm_nonpositive'] <= MAX_BAD and g['weight_share_bm_nonpositive'] <= MAX_BAD)
claim('valuation: every interval contains its point estimate',
      all(V[b][s]['weight_ci90'][0] <= V[b][s]['weight'] <= V[b][s]['weight_ci90'][1]
          for b, _ in BASIS for s, _ in SAMPLES if V[b][s]['weight'] is not None))
claim('valuation: in the score-of-40 cash subsample neither coefficient is significant at 5%',
      abs(t['beta_g'] / t['beta_g_se']) < 1.96 and abs(t['beta_m'] / t['beta_m_se']) < 1.96)
put('ExBoot', '999')
_P = pd.read_csv(os.path.join(BASE, 'data', 'panel_v3.csv'))
_F = pd.read_csv(os.path.join(BASE, 'data', 'v3_inputs', 'public_float.csv'))
_nf = _P[~_P.cik.isin(_F[_F.public_float_usd_thousands > 0].cik)]
claim('valuation: the registrants that report no float are mostly foreign private issuers (Form 20-F or 40-F firm-years over half)',
      len(_nf) == U['registrant_without_float'] and _nf.form.str.match(r'^(20-F|40-F)').mean() > 0.5)
# the paper's weights, for the comparison the text makes (Section sec:discussion; Lemma lem:valuation2)
SCREEN_HI, BESSEMER = 2.8, (2.0, 9.0)
claim('valuation: equal weights rejected at 0.1% in every sample but the score-of-40 one, on both bases',
      all(V[b][s]['equal_weights_p'] < 0.001 for b, _ in BASIS for s, _ in SAMPLES if s != 'top40'))
claim('valuation: among firm-years scoring 40 or more, equal weights are rejected at 5% on the cash basis only',
      V['cash']['top40']['equal_weights_p'] < 0.05 and V['gaap']['top40']['equal_weights_p'] > 0.10)
claim('valuation: the 90% interval of the weight lies above the screening range (upper end 2.8) for the all-firm-year samples, both bases',
      c['weight_ci90'][0] > SCREEN_HI and g['weight_ci90'][0] > SCREEN_HI)
claim("valuation: both point estimates lie inside Bessemer's reported range of about 2 to 9",
      all(BESSEMER[0] <= V[b]['all']['weight'] <= BESSEMER[1] for b, _ in BASIS))
claim('valuation: the weight on the cash basis is between 3.5 and 5.5 in each period and without acquisition-affected years',
      all(3.5 <= V['cash'][s]['weight'] <= 5.5 for s in ('2010-19', '2020-25', 'no_acq')))
claim('valuation: the score alone explains about half the within-year variation that growth and margin explain (0.4 to 0.6)',
      all(0.4 <= V[b]['all']['r2_within_score'] / V[b]['all']['r2_within_full'] <= 0.6 for b, _ in BASIS))
claim('valuation: among firm-years scoring 40 or more the score explains under 1% of the within-year variation (both bases)',
      all(V[b]['top40']['r2_within_score'] < 0.01 for b, _ in BASIS))
claim('valuation: the margin coefficient is positive in every sample except the cash score-of-40 sample',
      all(V[b][s]['beta_m'] > 0 for b, _ in BASIS for s, _ in SAMPLES if (b, s) != ('cash', 'top40'))
      and V['cash']['top40']['beta_m'] <= 0)

claim('valuation: Table note: the GAAP score-of-40 interval has a lower end that prints as zero, and no bootstrap interval exists '
      'for the cash score-of-40 sample (point beta_m not positive)',
      abs(V['gaap']['top40']['weight_ci90'][0]) < 0.05 and not V['cash']['top40'].get('weight_ci90'))

rows = []
for b, bl in BASIS:
    rows.append(r'\multicolumn{10}{@{}l}{\emph{' + bl + r'}}\\')
    for s, sl in SAMPLES:
        r = V[b][s]
        w = '' if r['weight'] is None else fnum(r['weight'], 1)
        ci, bad = r.get('weight_ci90'), r.get('weight_share_bm_nonpositive')
        civ = '' if not ci else (fnum(ci[0], 1) + ' to ' + fnum(ci[1], 1) if bad <= MAX_BAD else 'from ' + fnum(ci[0], 1))
        bs = '' if bad is None else fnum(100 * bad, 1)
        p = r['equal_weights_p']
        ps = '$<$0.001' if p < 0.001 else fnum(p, 2)
        rows.append(f"\\quad {sl} & {fint(r['n'])} & {r['firms']} & {fnum(r['beta_g'], 2)} & {fnum(r['beta_m'], 2)} & {w or '--'} & "
                    f"{civ or '--'} & {bs or '--'} & {ps} & {fnum(100 * r['r2_within_full'], 1)} / {fnum(100 * r['r2_within_score'], 1)}\\\\")
tab = (r"""\begin{table}[!ht]\centering\footnotesize\setlength{\tabcolsep}{2.6pt}
\caption{Public float over revenue against growth and margin, with year effects: the weight the market's valuations put on growth}\label{tab:ext-valuation}
\begin{tabular}{@{}lrrrrrrrrr@{}}\toprule
Sample & Firm-years & Firms & $\beta_g$ & $\beta_m$ & Weight & 90\% interval & $\beta_m\le0$ (\%) & $p$, equal & Within $R^2$ (\%)\\\midrule
""" + '\n'.join(rows) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: OLS of $\log(\text{public float}/\text{revenue})$ on revenue growth and the margin, both as fractions and winsorized at the 1st and 99th percentiles, with fiscal-year effects; standard errors clustered by firm. Weight: $\beta_g/\beta_m$, the points of margin that one point of growth is worth in the multiple, shown where $\beta_m>0$; interval: 5th to 95th percentile of the ratio over those of the """ + M['ExBoot'] + r""" firm-cluster bootstrap samples that give $\beta_m>0$; $\beta_m\le0$: share of the bootstrap samples that do not, in which the ratio is not a weight; where that share exceeds one in twenty no upper end is given (``from'' the lower end); a lower end at zero, as in the GAAP row of firm-years scoring at least 40, comes from samples in which $\beta_g$ is negative. No bootstrap is run where the point estimate of $\beta_m$ is not positive (--). $p$, equal: test of $\beta_g=\beta_m$, the Rule of 40's equal weights. Within $R^2$: share of the variation within fiscal years explained by growth and the margin entered separately / by their sum, the score, alone. Public float is the market value of common equity held by non-affiliates at the end of the second fiscal quarter after the fiscal year (10-K cover page); the core sample of Section~\ref{sec:data}, under estimand E1. Code: \texttt{code/biz\_valuation.py}.
\end{table}
""")
open(os.path.join(BASE, 'sections', 'tables', 'tab_ext_valuation.tex'), 'w').write(tab)

# ------------------------------------------------------------------------------------------------ (b) doing nothing
H = ['2028', '2031', '2036']
dn = P['do_nothing']
put('ExNoneFixed', fnum(100 * dn['0.0|central']['2036']['R'], 1))
put('ExNoneHalfCen', fnum(100 * dn['0.5|central']['2036']['R'], 1)); put('ExNoneHalfFast', fnum(100 * dn['0.5|fast']['2036']['R'], 1))
put('ExNoneSevenFast', fnum(100 * dn['0.7|fast']['2036']['R'], 1)); put('ExNoneSevenCen', fnum(100 * dn['0.7|central']['2036']['R'], 1))
put('ExPriceSevenFast', fnum(100 * (1 - dn['0.7|fast']['2036']['price']), 0))
# revenue growth lost while the price falls (outside re-review GPT F04): d log S = d log p + d log Q; the paths, like the
# paper's pass-through path, use the market's growth at a fixed price, so both firms omit the same average term
_p36 = dn['0.7|fast']['2036']['price']
put('ExPriceFallYr', fnum(100 * (1 - _p36 ** (1 / 11)), 0))
claim('nothing: at seven tenths with fast rivals the price falls at every horizon (2028, 2031, 2036), so the omitted growth term is a loss common to both firms',
      1 > dn['0.7|fast']['2028']['price'] > dn['0.7|fast']['2031']['price'] > _p36)
ad = P['adopter']
put('ExAdoptFixed', fnum(100 * ad['0.0']['2036']['R_net'], 1)); put('ExAdoptHalf', fnum(100 * ad['0.5']['2036']['R_net'], 1))
put('ExAdoptSeven', fnum(100 * ad['0.7']['2036']['R_net'], 1))
gp = P['grids']['gap_phi_pace']
GAP = np.array(gp['gap']) * 100; NONE = np.array(gp['none']) * 100
put('ExGapFixed', fnum(GAP[0, 1], 1)); put('ExGapSevenFast', fnum(GAP[3, 2], 1)); put('ExGapHalfFast', fnum(GAP[2, 2], 1))
put('ExGapSevenSlow', fnum(GAP[3, 0], 1))
GAPD = np.array(gp['gap_dip_fixed']) * 100
put('ExGapSevenFastDipFixed', fnum(GAPD[3, 2], 1))
claim('nothing: with the in-flight dip held at its fixed-price value the gap still widens in every row and column (positive shares)',
      all(np.all(np.diff(GAPD[:, j]) > 0) for j in range(3)) and all(np.all(np.diff(GAPD[i]) > 0) for i in range(1, 4))
      and abs(GAPD[0, 1] - GAP[0, 1]) < 1e-9)
claim('nothing: at fixed prices the firm that does not automate keeps its 2025 score in every year, whatever rivals do',
      all(abs(dn[f'0.0|{p}'][h]['R'] - dn['0.0|central']['2028']['R']) < 1e-12 for p in ('central', 'fast') for h in H))
claim("nothing: at fixed prices the gap is the same at every rivals' pace", np.ptp(GAP[0]) < 1e-9)
claim("nothing: the gap rises with the share passed to price at every rivals' pace and with the rivals' pace at every positive share",
      all(np.all(np.diff(GAP[:, j]) > 0) for j in range(3)) and all(np.all(np.diff(GAP[i]) > 0) for i in range(1, 4)))
claim('nothing: the gap is positive everywhere on the grid', GAP.min() > 0)
claim('nothing: the do-nothing score falls with the share passed and with the pace of rivals',
      all(np.all(np.diff(NONE[:, j]) < 1e-12) for j in range(3)) and all(np.all(np.diff(NONE[i]) < 0) for i in range(1, 4)))
claim('nothing: the grid at pass-through 0.5 and 0.7 with rivals at the central and fast pace equals the stored paths',
      all(abs(NONE[i, j] - 100 * dn[f'{ph}|{pc}']['2036']['R']) < 1e-9
          for i, ph in ((2, '0.5'), (3, '0.7')) for j, pc in ((1, 'central'), (2, 'fast'))))
PL = ['None (prices fixed)', 'A quarter', 'Half', 'Seven tenths']
rows = [f"{PL[i]} & " + ' & '.join(f"{fnum(NONE[i, j], 1)} & {fnum(GAP[i, j], 1)}" for j in range(3)) + r'\\' for i in range(4)]
tab = (r"""\begin{table}[!ht]\centering\footnotesize\setlength{\tabcolsep}{4pt}
\caption{A top-tail firm that does not automate while its rivals do: its 2036 cash score and the gap to a firm that automates at the central pace}\label{tab:ext-nothing}
\begin{tabular}{@{}lrrrrrr@{}}\toprule
& \multicolumn{2}{c}{Rivals slow} & \multicolumn{2}{c}{Rivals central} & \multicolumn{2}{c}{Rivals fast}\\\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(l){6-7}
Share of rivals' savings passed to price & Score & Gap & Score & Gap & Score & Gap\\\midrule
""" + '\n'.join(rows) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: Paper 1's pass-through scenario (Section~\ref{sec:horizons-ceiling}): rivals realize the share of their program that the slow, central or fast pace gives by 2036 and pass the stated share of each unit-cost saving into price; the firm that does nothing has the anchor intercept and no program, so its margin falls with the price; its volume path is the paper's, and growth is the market's growth at a fixed price for both firms, as in the paper's pass-through path. Score: its durable cash score in 2036. Gap: the score of the same firm automating at the central pace, after the cost of its changes in flight (Section~\ref{sec:horizons}; valued, as in the paper, at the long-run target with the stated share passed), less the score of the firm that does nothing; the automating firm faces the same price. The quarter row is not one of the paper's cases. Code: \texttt{code/biz\_open\_questions.py}.
\end{table}
""")
open(os.path.join(BASE, 'sections', 'tables', 'tab_ext_nothing.tex'), 'w').write(tab)

# ------------------------------------------------------------------------------------------------ (c) payback
D = pd.read_csv(os.path.join(MC, 'draws_lhs.csv.gz'), usecols=['kappa_abs', 'varpi', 'payback_years', 'R2036_net'])
dims = {d['name']: d for d in J['dims']}
bad = int((~np.isfinite(D.payback_years)).sum())
claim('payback: every draw of the stress test pays back (no infinite payback dropped from the medians)', bad == 0)
K = 6
ek = np.linspace(dims['kappa_abs']['lo'], dims['kappa_abs']['hi'], K + 1)
ew = np.linspace(dims['varpi']['lo'], dims['varpi']['hi'], K + 1)
ik = np.clip(np.searchsorted(ek, D.kappa_abs.to_numpy(), side='right') - 1, 0, K - 1)
iw = np.clip(np.searchsorted(ew, D.varpi.to_numpy(), side='right') - 1, 0, K - 1)
pbv = D.payback_years.to_numpy()
G = np.array([[np.median(pbv[(ik == a) & (iw == b)]) for b in range(K)] for a in range(K)])
NCELL = np.array([[int(((ik == a) & (iw == b)).sum()) for b in range(K)] for a in range(K)])
mx = os.path.join(MC, 'dashboard', 'matrices.csv')
if os.path.exists(mx):                                   # same grid as the companion page's heatmap
    MXD = pd.read_csv(mx)
    sub = MXD[MXD.matrix == 'payback_cap_win']
    claim('payback: the grid equals the companion page heatmap (matrices.csv)',
          all(abs(G[int(r.row), int(r.col)] - float(r.value)) < 1e-3 for r in sub.itertuples()))
spread_down = float(max(G[:, b].max() - G[:, b].min() for b in range(K)))
put('ExPbLowWin', fnum(G[2, 0], 1)); put('ExPbHighWin', fnum(G[2, K - 1], 1))
put('ExPbBoxMed', fnum(float(np.median(pbv)), 1))
put('ExKapLo', fnum(100 * ek[0], 0)); put('ExKapHi', fnum(100 * ek[-1], 0))
put('ExWinLo', fnum(100 * ew[0], 0)); put('ExWinHi', fnum(100 * ew[-1], 0))
put('ExCellMin', fint(NCELL.min()))
rk = D.rank()
put('ExRhoKap', fnum(float(np.corrcoef(rk.payback_years, rk.kappa_abs)[0, 1]), 2))
put('ExRhoWin', fnum(float(np.corrcoef(rk.payback_years, rk.varpi)[0, 1]), 2))
put('ExRhoKapScore', fnum(float(np.corrcoef(rk.R2036_net, rk.kappa_abs)[0, 1]), 2))
claim('payback: within each band of the success share, median payback moves by less than a fifth of a year across change capacity',
      spread_down < 0.2)
put('ExPbRowLab', f"{fnum(100 * ek[2], 1)}--{fnum(100 * ek[3], 1)}")
FAV = [('bbar', +1), ('varpi', +1), ('Temb', -1), ('Tpb', -1), ('Tfrz', -1)]
claim('payback: the central values of the benefit share, success share, embedding and payback times and freeze time lie toward their favorable ends',
      all(((dims[n]['central'] - dims[n]['lo']) / (dims[n]['hi'] - dims[n]['lo']) > 0.5) == (sgn > 0) for n, sgn in FAV))
claim('payback: in every row, median payback falls as the success share rises', all(np.all(np.diff(G[a]) < 0) for a in range(K)))
claim('payback: the rank correlation of payback with change capacity is below 0.05 in absolute value, with the success share below -0.25',
      abs(float(np.corrcoef(rk.payback_years, rk.kappa_abs)[0, 1])) < 0.05 and float(np.corrcoef(rk.payback_years, rk.varpi)[0, 1]) < -0.25)
claim('payback: the 2036 score rises with change capacity (rank correlation above 0.3)',
      float(np.corrcoef(rk.R2036_net, rk.kappa_abs)[0, 1]) > 0.3)

# central case: change capacity and the success share moved one at a time in Paper 1's calibration
spec = importlib.util.spec_from_file_location('mc_claims', os.path.join(BASE, 'code', 'mc_claims.py'))
mc = importlib.util.module_from_spec(spec); spec.loader.exec_module(mc)
cal = mc.load_calibration(os.path.join(tempfile.mkdtemp(prefix='ext_shadow_'), 'tree'))
cp, payback, PACE = cal['central_path'], cal['payback'], cal['PACE']
ref = cp()
pb0 = payback(ref, PACE['central'])['payback_undiscounted']
KS = [dims['kappa_abs']['lo'], PACE['central']['kappa_abs'], dims['kappa_abs']['hi']]
sweep = []
for k in np.linspace(KS[0], KS[2], 18):
    pp = dict(PACE['central'], kappa_abs=float(k))
    path = cp(pace_params=pp)
    sweep.append((float(k), payback(path, pp)['payback_undiscounted'], path['2036']['R']))
claim('payback: at the central case, payback is the same for every change capacity in the stated range (to 1e-9 years)',
      max(abs(s[1] - pb0) for s in sweep) < 1e-9)
claim('payback: at the central case, the 2036 durable score never falls and rises overall as change capacity rises',
      all(b[2] >= a[2] - 1e-12 for a, b in zip(sweep, sweep[1:])) and sweep[-1][2] > sweep[0][2] + 0.1)
put('ExPbCen', fnum(pb0, 1))
put('ExScoreKapLo', fnum(100 * sweep[0][2], 0)); put('ExScoreKapHi', fnum(100 * sweep[-1][2], 0))
ws = []
for w in (dims['varpi']['lo'], dims['varpi']['hi']):
    pp = dict(PACE['central'], varpi=float(w))
    ws.append(payback(cp(pace_params=pp), pp)['payback_undiscounted'])
put('ExPbWinLoCen', fnum(ws[0], 1)); put('ExPbWinHiCen', fnum(ws[1], 1))
claim('payback: at the central case, payback falls from the lowest to the highest success share', ws[0] > pb0 > ws[1])

lab = lambda e, i: f"{fnum(100 * e[i], 1)}--{fnum(100 * e[i + 1], 1)}"
rows = [f"{lab(ek, a)} & " + ' & '.join(fnum(G[a, b], 1) for b in range(K)) + r'\\' for a in range(K)]
tab = (r"""\begin{table}[!ht]\centering\footnotesize\setlength{\tabcolsep}{4pt}
\caption{Median payback (years) over the stress test, by change capacity and the share of attempts that create value}\label{tab:ext-payback}
\begin{tabular}{@{}l""" + 'r' * K + r"""@{}}\toprule
& \multicolumn{""" + str(K) + r"""}{c}{Share of attempted changes that create value, $\varpi$ (\%)}\\\cmidrule(l){2-""" + str(K + 1) + r"""}
Change capacity (\% a year) & """ + ' & '.join(lab(ew, b) for b in range(K)) + r"""\\\midrule
""" + '\n'.join(rows) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: medians of the undiscounted payback over the \StDraws{} Latin-hypercube draws of Section~\ref{supp:stress}, in six equal-width bins of each input over its stated range; every other input of the box varies within each cell (at least """ + M['ExCellMin'] + r""" draws a cell). Code: \texttt{code/supp\_extensions.py}.
\end{table}
""")
open(os.path.join(BASE, 'sections', 'tables', 'tab_ext_payback.tex'), 'w').write(tab)

# ------------------------------------------------------------------------------------------------ write and check
L = ['% Generated by code/supp_extensions.py (Supplement Section supp:extensions). Do not edit by hand.']
L += [f'\\newcommand{{\\{k}}}{{{v}}}' for k, v in M.items()]
open(os.path.join(BASE, 'paper1', 'ext_macros.tex'), 'w').write('\n'.join(L) + '\n')
open(os.path.join(BASE, 'notes', 'open_questions', 'ext_claim_checks.txt'), 'w').write(
    ''.join(f"{'ok  ' if ok else 'FAIL'} {t}\n" for t, ok in CHECKS))
fail = [t for t, ok in CHECKS if not ok]
print(f'wrote paper1/ext_macros.tex ({len(M)} macros) and three tables; {len(CHECKS) - len(fail)} of {len(CHECKS)} text checks pass')
for t in fail:
    print('FAIL', t)
if fail:
    sys.exit(1)
