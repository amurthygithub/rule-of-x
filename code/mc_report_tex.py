#!/usr/bin/env python3
"""Supplement table, macros and figure of the joint-parameter stress test (round 3, decision 7 of the outside-review plan).

Reads the committed outputs of code/mc_claims.py (it does not re-run the Monte Carlo):
  notes/mc_results_2026-11-02/mc_claims.json   claim tests, quantities over the box, levels, Sobol indices, accountability sub-box
  notes/mc_results_2026-11-02/draws_lhs.csv    the 10,000 Latin-hypercube draws (selected outputs per draw)
and writes
  sections/tables/tab_stress.tex   Table tab:stress: the headline claim tests, whether each holds at every evaluated point of
                                   the box of the paper's stated ranges, the central value and the lowest-highest over the box
  paper1/stress_macros.tex         \\St* macros quoted in the text (input from paper1/macros.tex)
  figures/fig_stress.pdf           two panels: the 2036 central score (netted) over the draws with the paper's 90% anchor
                                   interval, and the 100-point growth threshold G* over the draws with the 30% line
The Monte Carlo itself is reproduced by  python3 code/mc_claims.py --n 10000 --workers 4 --out notes/mc  (see
code/REPLICATION_README.md); this script only formats its stored results. MC_DIR overrides the input folder.

Framing (as in the stress-test report): not a forecast. 'Holds everywhere' is distribution-free: no evaluated point (every
draw, the box corners and a vertex search for each tested quantity) violates the test, which is a search, not a proof.
Shares of draws assume uniform laws over the stated ranges, an assumption, and are not shown in the table.

Run from anywhere:  python3 code/mc_report_tex.py
"""
import json, re
import math
import os

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MC = os.environ.get('MC_DIR', os.path.join(BASE, 'notes', 'mc_results_2026-11-02'))
J = json.load(open(os.path.join(MC, 'mc_claims.json')))
D = pd.read_csv(os.path.join(MC, 'draws_lhs.csv'))
TESTS = {t['tid']: t for c in J['claims'] for t in c['tests']}
AMIN = {a['tid']: a for a in J['amin']['tests']}
QUANT = {q['key']: q for q in J['quantities']}
assert J['meta']['args']['n'] == len(D) == J['design']['n_lhs'] and not J['meta']['small_n_warning']
assert J['reproduction']['all_passed'], 'the stress test did not reproduce the paper at the centre of the box'


def half_up(x, nd=0):
    q = 10 ** nd
    return math.floor(x * q + 0.5) / q


def fnum(x, nd):
    s = f"{half_up(x, nd):.{nd}f}"
    return f"$-${s[1:]}" if s.startswith('-') else s


# ---------------------------------------------------------------------------------------------- (a) Table tab:stress
# (test id, claim as the paper states it, conditions held, value printed, format). Formats: pct = 100 x with one decimal
# (points or percent), pctsign = the same with a percent sign, yr1 = a year to one decimal, x2 = two decimals, int = integer
ROWS = [
    ('C1.full', r'Cash ceiling below 100 up to 30\% market growth: threshold $G^*$ above 30\%', 'full box', 'pctsign'),
    ('C1.cond', r'The same', r'compute 6\% of revenue, fixed prices, $k=0$', 'pctsign'),
    ('C2.full', r'Threshold above 30\% in 2028, 2031 and 2036 (lowest of the three)', 'full box', 'pctsign'),
    ('C3.full.net', r'Pass-through raises every threshold (smallest rise, points)', 'full box', 'pct'),
    ('P1.full.net', r'No Rule of 100 on the central path (highest score, 2028--36)', 'full box', 'pct'),
    ('P2b.full.net', r'A completed program: 2036 target plus market growth below 100', 'full box', 'pct'),
    ('P3.full', r'Less than half of the program realized by 2036 (realized share)', 'full box', 'pctsign'),
    ('P3b.full', r'Program still running in 2036 (expected completion year)', 'full box', 'yr1'),
    ('P4.full.net', r'The central path rises from 2028 to 2036 (smallest step, points)', 'full box', 'pct'),
    ('P6.full', r'Netted path between the no-S\&M and all-S\&M bounds (smallest gap, points)', 'full box', 'pct'),
    ('B1.full.net', r'Flow crossing before payback (years between them)', 'full box', 'x2'),
    ('B2.full.net', r'No payback within five years (payback, years)', 'full box', 'x2'),
    ('B2.B.net', r'The same', r'central execution, fixed prices, $k=0$', 'x2'),
    ('B4.full.net', r'Gains worth more than the dip in present value (ratio)', 'full box', 'x2'),
    ('B4.B.net', r'The same', r'central execution, fixed prices, $k=0$', 'x2'),
    ('R1.full', r"Rule of 1000 not a steady state (pull needed over today's best)", 'full box', 'x2'),
    ('L1.full.net', r'Growth engine ahead of the G\&A cut at one of six positions (count)', r'full box, maintenance base drawn', 'int'),
    ('A1.Five', r'No all-AI design on one provider admissible (lowest annual miss probability)',
     r'accountability sub-box, $\bar\pi=5\%$', 'pctsign'),
]


def fmt_val(x, kind):
    if kind == 'pct':
        return fnum(100 * x, 1)
    if kind == 'pctsign':
        return fnum(100 * x, 1) + r'\%'
    if kind == 'yr1':
        return fnum(x, 1)
    if kind == 'x2':
        return fnum(x, 2)
    if kind == 'int':
        return fnum(x, 0)
    raise ValueError(kind)


def row_values(tid):
    if tid in AMIN:
        a = AMIN[tid]
        thr = float(a['threshold'].rstrip('%')) / 100
        return a['holds_everywhere'], thr + a['margin_central'], a['quantity']['min'], a['quantity']['max']
    t = TESTS[tid]
    q = t['quantity']
    return t['holds_everywhere'], q['central'], q['min'], q['max']


# round 3 audit (F1): the box moves the compute share through the drivers of its path (compute per dollar of labor
# replaced at 2025 prices, kappa_2025, and the labor share automated, s_L), not over the 2-60% scenario range of
# Section 7.2; the note, S9 and the figure say so, with the range this gives
_DIM = {d_['name']: d_ for d_ in J['dims']}
_CC = QUANT['c_c_2025']
assert abs(_CC['min'] - _DIM['kappa_2025']['lo'] * _DIM['s_L']['lo']) < 1e-9
assert abs(_CC['max'] - _DIM['kappa_2025']['hi'] * _DIM['s_L']['hi']) < 1e-9
CC_BOX_LO, CC_BOX_HI = fnum(100 * _CC['min'], 1), fnum(100 * _CC['max'], 0)
_PM = dict(re.findall(r'\\newcommand\{\\(\w+)\}\{([^}]*)\}', open(os.path.join(BASE, 'paper1', 'macros.tex')).read()))
CC_SCEN_LO, CC_SCEN_HI = _PM['CcLo'], _PM['CcHi']     # the scenario range of Section 7.2, as the paper prints it
lines = []
for tid, claim, cond, kind in ROWS:
    ok, cen, lo, hi = row_values(tid)
    lines.append(f"{claim} & {cond} & {'yes' if ok else 'no'} & {fmt_val(cen, kind)} & {fmt_val(lo, kind)} to {fmt_val(hi, kind)} \\\\")
n_hold = sum(row_values(tid)[0] for tid, *_ in ROWS)
dsg = J['design']
tab = (r"""\begin{table}[t]\centering\footnotesize\setlength{\tabcolsep}{3pt}
\caption{Joint-parameter stress test of the headline claims: does each hold at every evaluated point of the box of stated ranges?}\label{tab:stress}
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{6.3cm}>{\raggedright\arraybackslash}p{3.3cm}ccc@{}}\toprule
Claim (quantity tested) & Conditions held & Holds everywhere & Central & Lowest to highest\\\midrule
""" + '\n'.join(lines) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: """ + (
    f"{dsg['n_lhs']:,}".replace(',', '{,}') + r" Latin-hypercube draws and " + f"{dsg['n_corners']:,}".replace(',', '{,}')
    + r" corner points of a box of " + str(len(J['dims'])) + r" dimensions, each at the ends of the range the paper states for it "
    r"(the anchor's dimensions within their 90\% firm-cluster bootstrap intervals), except the compute share, which enters "
    r"through the drivers of its path and so runs from " + CC_BOX_LO + r" to " + CC_BOX_HI + r"\% of revenue at 2025 prices, "
    r"not over the scenario range of " + CC_SCEN_LO + r" to " + CC_SCEN_HI + r"\% (Section S9); three bases for selling and marketing "
    r"(netted rows: the central, maintenance-netted basis), and a vertex search for the extremum of each tested quantity. "
    r"Holds everywhere: no evaluated point violates the claim's test; this is a search, not a proof. Central: the paper's "
    r"central case. Lowest to highest: over all evaluated points. Conditions held: the claim's own stated conditions at "
    r"their central values (full box: none). Percentages are points of revenue or percent a year. The accountability row "
    r"uses its own sub-box (" + f"{J['amin']['n_lhs']:,}".replace(',', '{,}') + r" draws and all " + str(J['amin']['n_corners'])
    + r" corners of " + str(len(J['amin']['dims'])) + r" dimensions: audit fees, the cross-type common mode, the human miss "
    r"rate on AI-missed items, the AI common mode and the number of opportunities). Most dimensions are scenario values with "
    r"stated ranges but no measured distribution, so the table reports where claims fail, not how likely they are to; it is "
    r"not a forecast. Generated by \texttt{code/mc\_report\_tex.py} from the stored output of \texttt{code/mc\_claims.py}.")
    + '\n' + r'\end{table}' + '\n')
open(os.path.join(BASE, 'sections', 'tables', 'tab_stress.tex'), 'w').write(tab)

# ---------------------------------------------------------------------------------------------- (b) macros
M = {}


def put(name, text):
    assert name.isalpha() and name.startswith('St') and name not in M, name
    M[name] = text


def num(name, x, nd=1, pct=True):
    put(name, fnum(100 * x if pct else x, nd))


put('StDraws', f"{dsg['n_lhs']:,}".replace(',', '{,}')); put('StCorners', f"{dsg['n_corners']:,}".replace(',', '{,}'))
put('StDims', str(len(J['dims']))); put('StSeed', str(dsg['seed']))
put('StAminDraws', f"{J['amin']['n_lhs']:,}".replace(',', '{,}')); put('StAminCorners', str(J['amin']['n_corners']))
put('StAminDims', str(len(J['amin']['dims'])))
put('StClaimsHold', str(n_hold)); put('StClaimsRows', str(len(ROWS)))
L36 = J['levels']['net.R_2036']
num('StNetSixPFive', L36['lhs_p05']); num('StNetSixPNinetyFive', L36['lhs_p95'])
num('StNetSixMin', L36['box_min']); num('StNetSixMax', L36['box_max']); num('StNetSixCen', L36['central'], 0)
num('StNetSixBandLo', L36['combined_band_90'][0]); num('StNetSixBandHi', L36['combined_band_90'][1])
num('StNetSixInPaper', L36['share_in_paper_interval_uniform'], 0)
G = QUANT['Gstar_2025']; G6 = QUANT['Gstar_2025_cc6']
num('StGstarMin', G['min']); num('StGstarMax', G['max']); num('StGstarPFive', G['lhs_p05']); num('StGstarPNinetyFive', G['lhs_p95'])
num('StGstarCcSixMin', G6['min']); num('StGstarCcSixMax', G6['max'])
num('StGstarHorMin', TESTS['C2.full']['quantity']['min'])
num('StGstarBelowThirty', 1 - TESTS['C1.full']['share_holds_uniform'], 0)        # share of draws with G* <= 30% (uniform)
PB, PBB = QUANT['net.pb.pb_u'], QUANT['net.B.pb.pb_u']
num('StPayCenMin', PBB['min'], 2, False); num('StPayCenMax', PBB['max'], 2, False)
num('StPayMin', PB['min'], 2, False); num('StPayMax', PB['max'], 2, False)
num('StPayCen', PB['central'], 1, False)
num('StRatioCenMin', QUANT['net.B.pb.ratio']['min'], 2, False); num('StRatioMin', QUANT['net.pb.ratio']['min'], 2, False)
num('StNpvMin', QUANT['net.pb.npv']['min'], 0); num('StNpvMax', QUANT['net.pb.npv']['max'], 0)
LV = TESTS['L1.full.net']
num('StLeverMin', LV['quantity']['min'], 0, False); num('StLeverMax', LV['quantity']['max'], 0, False)
num('StLeverOneShare', LV['share_holds_uniform'], 1)
assert abs((D.levers_growth_engine_first_count == 1).mean() - LV['share_holds_uniform']) < 1e-12
S1 = {s['id']: s for s in J['sensitivity_claims']}
num('StSobolExec', S1['S1']['sobol']['ST_execution'], 2, False)
num('StSobolG', S1['S1']['sobol']['ST_market_growth'], 2, False)
num('StSobolCc', S1['S2']['sobol']['ST_compute'], 2, False)
S36 = QUANT['s_2036']
num('StRealMin', S36['min']); num('StRealMax', S36['max'])
num('StCompleteMin', QUANT['complete_year']['min'], 0, False); num('StCompleteMax', QUANT['complete_year']['max'], 0, False)
num('StAiOnlyMin', AMIN['A1.Five']['quantity']['min'])
num('StFloorMin', AMIN['A4.Five']['quantity']['min'], 2); num('StFloorMax', AMIN['A4.Five']['quantity']['max'], 2)
num('StFloorOneMin', AMIN['A4.One']['quantity']['min'], 2); num('StFloorOneMax', AMIN['A4.One']['quantity']['max'], 2)
num('StPullMin', QUANT['pull_multiple']['min'], 1, False); num('StPullMax', QUANT['pull_multiple']['max'], 1, False)
num('StCompletedMax', TESTS['P2b.full.net']['quantity']['max'])
num('StPathMax', TESTS['P1.full.net']['quantity']['max'])
# editor's requests for Section S9 (3 Nov): the reproduction checks run before sampling; the ST-4 maxima of the cumulative
# and discounted effects at three and five years (points of revenue times years); the ST-5 change-capacity threshold
_rc = J['reproduction']['checks']
assert all(c_['ok'] for c_ in _rc) and J['reproduction']['all_passed']
put('StReproChecks', str(len(_rc)))
# round 3 audit (F1): the box's range of the 2025 compute share and of its two drivers, and how much the tested
# quantities stored per draw move with it (Spearman rank correlation over the Latin-hypercube draws)
put('StCcBoxMin', CC_BOX_LO); put('StCcBoxMax', CC_BOX_HI)
num('StKappaLo', _DIM['kappa_2025']['lo'], 0); num('StKappaHi', _DIM['kappa_2025']['hi'], 0)
num('StSLLo', _DIM['s_L']['lo'], 0); num('StSLHi', _DIM['s_L']['hi'], 0)
_rho = {c_: D[c_].corr(D.compute_share_2025, method='spearman') for c_ in
        ('Gstar_2025', 'R2028_net', 'R2031_net', 'R2036_net', 'R2036_none', 'R2036_all', 'payback_years',
         'payback_years_central_exec', 'npv_pct_revenue', 'realized_share_2036', 'levers_growth_engine_first_count',
         'completed_program_plus_G_2036')}
num('StGstarCcRho', _rho['Gstar_2025'], 2, False)
_rho_other = max(abs(v_) for k_, v_ in _rho.items() if k_ != 'Gstar_2025')
assert _rho['Gstar_2025'] > 0.9 and _rho_other < 0.05
num('StOtherCcRho', _rho_other, 2, False)


def sgn(name, x, nd=1):
    s_ = fnum(100 * x, nd)
    put(name, s_ if s_.startswith('$-$') or float(s_) == 0 else '$+$' + s_)


sgn('StCumMaxCen', TESTS['B3.B.net']['quantity']['max']); sgn('StCumMax', TESTS['B3.full.net']['quantity']['max'])
import re as _re
_scan = [u for u in TESTS['P3.full']['failure']['univariate'] if u['dim'] == 'kappa_abs' and u['reference'] == 'central'][0]
_m = _re.fullmatch(r'fails for kappa_abs in \[([\d.]+), ([\d.]+)\]', _scan['result'])
assert _m and abs(float(_m.group(2)) - max(d_['hi'] for d_ in J['dims'] if d_['name'] == 'kappa_abs')) < 1e-12
num('StCapHalf', float(_m.group(1)), 0); num('StCapHalfOne', float(_m.group(1)), 1)   # share of the program changed a year
# the qualitative statements of S9 about these numbers: ST-4 fails narrowly under central execution (largest value above
# zero but below one point of revenue times years) and clearly over the full box; ST-5's threshold lies between the
# central (0.10) and the fast (0.22) change capacity
_kc = [d_ for d_ in J['dims'] if d_['name'] == 'kappa_abs'][0]
assert 0 < TESTS['B3.B.net']['quantity']['max'] < 0.01 < TESTS['B3.full.net']['quantity']['max']
assert not TESTS['B3.B.net']['holds_everywhere'] and _kc['central'] < float(_m.group(1)) < _kc['hi']
# the draws file and the JSON must agree (same run)
assert abs(np.quantile(D.R2036_net, 0.05) / 100 - L36["lhs_p05"]) < 1e-6 and abs(np.quantile(D.R2036_net, 0.95) / 100 - L36["lhs_p95"]) < 1e-6   # the CSV is rounded
assert D.Gstar_2025.min() / 100 >= G['min'] - 1e-12 and D.Gstar_2025.max() / 100 <= G['max'] + 1e-12
assert D.realized_share_2036.min() / 100 >= S36['min'] - 1e-12 and D.realized_share_2036.max() / 100 <= S36['max'] + 1e-12
hdr = ['% Generated by code/mc_report_tex.py from notes/mc_results_2026-11-02/mc_claims.json and draws_lhs.csv',
       f"% (code/mc_claims.py v{J['meta']['version']}, config {J['meta']['config_hash']}, created {J['meta']['created']}). "
       'Do not edit by hand. Percentages without the % sign.']
open(os.path.join(BASE, 'paper1', 'stress_macros.tex'), 'w').write(
    '\n'.join(hdr + [f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in M.items()]) + '\n')

# ---------------------------------------------------------------------------------------------- (c) figure
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

available = {f.name for f in font_manager.fontManager.ttflist}
family = next((f for f in ['Arial', 'Helvetica', 'Liberation Sans', 'Nimbus Sans', 'DejaVu Sans'] if f in available), 'sans-serif')
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': [family], 'font.size': 9, 'axes.labelsize': 9,
                     'xtick.labelsize': 8, 'ytick.labelsize': 8, 'legend.fontsize': 7.5, 'axes.linewidth': 0.6,
                     'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'axes.spines.top': False,
                     'axes.spines.right': False, 'pdf.fonttype': 42, 'ps.fonttype': 42, 'mathtext.fontset': 'custom',
                     'mathtext.rm': family, 'mathtext.it': f'{family}:italic', 'mathtext.bf': f'{family}:bold', 'mathtext.cal': family,
                     'savefig.bbox': 'tight', 'savefig.pad_inches': 0.03, 'svg.hashsalt': 'fig_stress',
                     'pdf.compression': 6})
BLACK, DARK, MID, LIGHT = '0.0', '0.25', '0.5', '0.85'
fig, ax = plt.subplots(1, 2, figsize=(6.5, 2.7))
# left: the 2036 central score, netted basis, over the draws, with the paper's 90% anchor-sampling interval
r36 = D.R2036_net.to_numpy()
lo_b, hi_b = (100 * x for x in L36['paper_anchor_interval_90'])
ax[0].axvspan(lo_b, hi_b, ymax=0.7, color=LIGHT, lw=0, zorder=0, label='paper: 90% anchor interval')
ax[0].hist(r36, bins=np.arange(25, 85.1, 1.5), color=MID, edgecolor='white', lw=0.3, zorder=2, label='10,000 draws')
ax[0].axvline(100 * L36['central'], ymax=0.7, color=BLACK, lw=0.9, zorder=3, label='central path')
for i_, q_ in enumerate((L36['lhs_p05'], L36['lhs_p95'])):
    ax[0].axvline(100 * q_, ymax=0.7, color=DARK, lw=0.7, ls=(0, (3, 2)), zorder=3, label='5th and 95th percentiles' if i_ == 0 else None)
ax[0].set_xlabel('2036 central score, maintenance-netted (points)')
ax[0].set_ylabel('Draws')
ax[0].set_xlim(25, 85)
ax[0].set_ylim(0, 1.5 * np.histogram(r36, bins=np.arange(25, 85.1, 1.5))[0].max())
ax[0].legend(frameon=False, loc='upper left', ncol=2, columnspacing=1.0, handlelength=1.6)
# right: the growth threshold G* at 2025 prices over the draws (compute share over the box; and with compute at 6%)
gs, g6 = D.Gstar_2025.to_numpy(), D.Gstar_2025_cc6.to_numpy()
bins = np.arange(20, 54.1, 1.0)
ax[1].hist(gs, bins=bins, color=MID, edgecolor='white', lw=0.3, zorder=2, label='compute share over the box')
ax[1].hist(g6, bins=bins, histtype='step', color=BLACK, lw=0.8, zorder=3, label='compute at 6% of revenue')
ax[1].axvline(30, ymax=0.72, color=BLACK, lw=0.9, ls=(0, (3, 2)), zorder=4, label='30% market growth')
ax[1].set_xlabel('Growth threshold $G^*$ for a cash score of 100 (% a year)')
ax[1].set_ylabel('Draws')
ax[1].set_xlim(20, 54)
ax[1].set_ylim(0, 1.45 * np.histogram(g6, bins=bins)[0].max())
ax[1].legend(frameon=False, loc='upper left', ncol=1, handlelength=1.6)
fig.tight_layout(w_pad=1.5)
os.makedirs(os.path.join(BASE, 'figures'), exist_ok=True)
fig.savefig(os.path.join(BASE, 'figures', 'fig_stress.pdf'), metadata={'CreationDate': None, 'ModDate': None, 'Creator': None,
                                                                      'Producer': None})
print(f"wrote sections/tables/tab_stress.tex ({len(ROWS)} rows, {n_hold} hold everywhere), paper1/stress_macros.tex "
      f"({len(M)} macros) and figures/fig_stress.pdf")
