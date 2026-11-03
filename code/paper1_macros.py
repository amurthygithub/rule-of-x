#!/usr/bin/env python3
"""Generate the numbers quoted in Paper 1 ("The Rule of 40 as a Price Line").

Reads (never writes) the outputs of the analysis scripts:
  notes/calibration_results.json   code/calibrate_horizons.py   (ceiling, thresholds, pace, horizons, anchor)
  notes/paper_stats.json           code/paper_stats.py          (statistics quoted only in the text)
  notes/empirics_revised.json      code/estimate_revised.py     (slopes, top quantiles, spend ratio, capital split)
  notes/gap_decomposition.json     code/decompose_gap.py        (margin-gap decomposition)
  notes/empirics_organic.json      code/estimate_organic.py     (estimands E1, observed scores, and E2, organic frontier)
  data/panel.csv, data/panel_broad.csv                          (sample counts)
  notes/empirics_v3.json, notes/frontier_slope_v3.json         code/estimate_v3.py (audited sample, revision v2: every
  notes/empirics_v2_exact.json                                 number of the data, empirical and data-appendix sections)
  notes/panel_v3_build.json, data/panel_v3.csv                 code/build_panel_v3.py (sample rules R1 to R5)
  sections/tables/tab_{estimands,contrasts,grid,yearly}_v3.tex  code/estimate_v3_report.py
and writes
  paper1/tab_robust_v3.tex   the robustness table (tab:robust) from notes/empirics_v3.json
  paper1/tab_*_v3.tex        copies of the four v3 tables with the bootstrap seeds in their notes (and, for
                             tab_contrasts_v3, the labels of the three cash rows and the reference to the first version)
  paper1/macros.tex          one \\newcommand per quoted number (rounded half up as stated per macro)
  paper1/abstract_plain.txt  the abstract of sections/abstract.tex with the macros expanded, as plain text for the
                             arXiv abstract field (fails if it exceeds 1,920 characters)

Every number in the abstract, introduction, horizons section and conclusion of Paper 1 is a macro defined here,
except model inputs stated as assumptions (for example a 20% compute share) and counts of theoretical objects.
A few model examples (the duration bound of Corollary cor:transient and the free-entry score of Proposition
prop:entry) are evaluated here from their closed forms at the example inputs stated in the text.

Run from anywhere:  python3 code/paper1_macros.py
"""
import json
import math
import os
import re
import sys

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE, 'paper1')
CAL = json.load(open(os.path.join(BASE, 'notes', 'calibration_results.json')))
STATS = json.load(open(os.path.join(BASE, 'notes', 'paper_stats.json')))
EMP = json.load(open(os.path.join(BASE, 'notes', 'empirics_revised.json')))
GAP = json.load(open(os.path.join(BASE, 'notes', 'gap_decomposition.json')))
ORG = json.load(open(os.path.join(BASE, 'notes', 'empirics_organic.json')))
MAX_ABSTRACT = 1920

M = {}          # macro name -> LaTeX string
PLAIN = {}      # macro name -> plain-text string (for the arXiv abstract)


def half_up(x, nd=0):
    q = 10 ** nd
    return math.floor(x * q + 0.5) / q


def fmt(x, nd=0, pct=True):
    """x is a fraction if pct, else a plain number; returns the rounded value as text (no % sign)."""
    v = half_up(100 * x if pct else x, nd)
    s = f"{v:.{nd}f}"
    return s


def put(name, text, plain=None):
    assert re.fullmatch(r'[A-Za-z]+', name), name
    assert name not in M, f"duplicate macro {name}"
    M[name] = text
    PLAIN[name] = plain if plain is not None else text


def num(name, x, nd=0, pct=True):
    s = fmt(x, nd, pct)
    if s.startswith('-'):
        put(name, f"$-${s[1:]}", f"-{s[1:]}")
    else:
        put(name, s)


def thousands(n):
    return f"{n:,}".replace(',', '{,}'), f"{n:,}"


# ---------------------------------------------------------------------------------------------- samples
core = pd.read_csv(os.path.join(BASE, 'data', 'panel.csv'))
broad = pd.read_csv(os.path.join(BASE, 'data', 'panel_broad.csv'))
put('NFirms', str(core.cik.nunique()))
t, p = thousands(len(core)); put('NFirmYears', t, p)
put('NFirmsBroad', str(broad.cik.nunique()))
t, p = thousands(len(broad)); put('NFirmYearsBroad', t, p)

# ---------------------------------------------------------------------------------------------- empirics
sl = EMP['local']
num('SlopeOp', -sl['op']['slopes']['pooled']['b'], 2, pct=False)       # 0.46
num('SlopeCash', -sl['cash']['slopes']['pooled']['b'], 2, pct=False)   # 0.37
sr = EMP['spend_ratio']['median']
num('SpendRatio', sr, 1, pct=False)                                    # 3.3
num('WeightLo', ORG['headline']['weight_lo']['E2']['est'], 0, pct=False)   # E2: alpha(X - k) = spend ratio, alpha in [0.25, 0.45]
num('WeightHi', ORG['headline']['weight_hi']['E2']['est'], 0, pct=False)
num('TopDropOp', -EMP['top']['op']['diff_1619|q95']['diff'])           # 12 points, GAAP
num('TopDropCash', -EMP['top']['cash']['diff_1619|q95']['diff'])       # 15 points, FCF after SBC
num('ScaleSlope', -EMP['scale']['cash']['slope']['b'] * math.log(10))  # points per tenfold increase in revenue
num('CapIntGap', -EMP['capint']['cash']['2023-25']['gap'])            # 2023-25, cash basis
num('GapAvg', GAP['avg']['gap'])                                       # about 35 points
num('GapAvgOne', GAP['avg']['gap'], 1)
band40 = [b for b in GAP['bands'] if b['band'] == 4][0]                # growth 40 to 60%
num('GapFast', band40['gap'])
num('GapFastSM', band40['d_sms'])
band0 = [b for b in GAP['bands'] if b['band'] == 0][0]                 # growth below 10%
num('GapSlow', band0['gap'])
num('GapSlowGM', band0['d_gm'])
num('MedGrossMargin', CAL['pass_through']['gross_margin_median_2023_25'])   # median core firm 2023-25, audited panel
ga = STATS['ga_median_by_size']
num('GAsmall', ga['<1B']); num('GAmid', ga['1-10B']); num('GAlarge', ga['>10B'])
num('GAleanLo', STATS['ga_microsoft_oracle_range'][0], 1); num('GAleanHi', STATS['ga_microsoft_oracle_range'][1], 1)
num('PalantirGAAP', STATS['palantir_2025']['R_op'])

# ---------------------------------------------------------------------------------------------- estimands
# E1 = observed scores (all firm-years), E2 = organic frontier (pro forma adjusted where disclosed, otherwise
# acquisition-affected firm-years excluded). Model-facing statements use E2, descriptive statements E1.
H = ORG['headline']
def e(key, est='E2'):
    return H[key][est]['est']
def ci(key, est='E2'):
    return H[key][est]['ci90']
smp = ORG['samples']['E2']
t_, p_ = thousands(smp['n']); put('EtwoFirmYears', t_, p_); put('EtwoFirms', str(smp['firms']))
put('EtwoAffectedKept', str(smp['n_affected_kept'])); put('EtwoFastTwentyThree', str(smp['n_g_ge_40_2023_25']))
put('EoneFastTwentyThree', str(ORG['samples']['E1']['n_g_ge_40_2023_25']))
num('EtwoSlopeOp', -e('slope_op_pooled'), 2, pct=False); num('EtwoSlopeCash', -e('slope_cash_pooled'), 2, pct=False)
num('EtwoSlopeOpSe', H['slope_op_pooled']['E2']['se'], 2, pct=False)
num('EtwoSlopeCashSe', H['slope_cash_pooled']['E2']['se'], 2, pct=False)
num('SlopeOpDiffLo', H['slope_op_pooled']['E1_minus_E2']['ci90'][0], 2, pct=False)
num('SlopeOpDiffHi', H['slope_op_pooled']['E1_minus_E2']['ci90'][1], 2, pct=False)
num('SlopeCashDiffLo', H['slope_cash_pooled']['E1_minus_E2']['ci90'][0], 2, pct=False)
num('SlopeCashDiffHi', H['slope_cash_pooled']['E1_minus_E2']['ci90'][1], 2, pct=False)
for per, nm in [('2010_19', 'Early'), ('2020_25', 'Late')]:
    num('EoneSlopeOp' + nm, -e('slope_op_' + per, 'E1'), 2, pct=False); num('EtwoSlopeOp' + nm, -e('slope_op_' + per), 2, pct=False)
    num('EoneSlopeCash' + nm, -e('slope_cash_' + per, 'E1'), 2, pct=False); num('EtwoSlopeCash' + nm, -e('slope_cash_' + per), 2, pct=False)
num('EoneSpendRatio', e('spend_ratio', 'E1'), 1, pct=False); num('EtwoSpendRatio', e('spend_ratio'), 1, pct=False)
num('EoneWeightLo', e('weight_lo', 'E1'), 1, pct=False); num('EoneWeightHi', e('weight_hi', 'E1'), 1, pct=False)
num('EtwoWeightLoOne', e('weight_lo'), 1, pct=False); num('EtwoWeightHiOne', e('weight_hi'), 1, pct=False)
num('EoneScaleCash', -e('scale_tenfold_cash', 'E1')); num('EoneScaleCashOne', -e('scale_tenfold_cash', 'E1'), 1)
num('EoneScaleCashSe', H['scale_tenfold_cash']['E1']['se'], 1)
num('EtwoScaleCashOne', -e('scale_tenfold_cash'), 1); num('EtwoScaleCashSe', H['scale_tenfold_cash']['E2']['se'], 1)
num('EoneCapIntGap', -e('capint_gap_cash_2023_25', 'E1')); num('EtwoCapIntGap', -e('capint_gap_cash_2023_25'))
num('EtwoCapIntLo', -ci('capint_gap_cash_2023_25')[1]); num('EtwoCapIntHi', -ci('capint_gap_cash_2023_25')[0])
cg = H['capint_gap_cash_2023_25']['E2']
num('EtwoCapIntHiHalf', cg['hi']); num('EtwoCapIntLoHalf', cg['lo'])
num('EtwoCapIntOp', -e('capint_gap_op_2023_25')); num('EtwoCapIntOpLo', ci('capint_gap_op_2023_25')[0]); num('EtwoCapIntOpHi', ci('capint_gap_op_2023_25')[1])
num('EtwoScaleOpOne', e('scale_tenfold_op'), 1); num('EtwoScaleOpSe', H['scale_tenfold_op']['E2']['se'], 1)
num('ScaleDiffLo', H['scale_tenfold_cash']['E1_minus_E2']['ci90'][0], 1); num('ScaleDiffHi', H['scale_tenfold_cash']['E1_minus_E2']['ci90'][1], 1)
num('EtwoTopDropOp', -e('p95_change_op')); num('EtwoTopDropCash', -e('p95_change_cash'))
num('EtwoTfortyOp', e('T_op_g40_change')); num('EtwoTfortyCash', e('T_cash_g40_change'))
num('EtwoTfortyCashLo', ci('T_cash_g40_change')[0]); num('EtwoTfortyCashHi', ci('T_cash_g40_change')[1])
num('EtwoTfortyOpLo', ci('T_op_g40_change')[0]); num('EtwoTfortyOpHi', ci('T_op_g40_change')[1])
sp2 = H['spend_ratio']['E2']
num('EtwoSpendIqrLo', sp2['iqr'][0], 1, pct=False); num('EtwoSpendIqrHi', sp2['iqr'][1], 1, pct=False)
num('EtwoMedSM', sp2['med_sm']); num('EtwoMedExcess', sp2['med_excess'], 1)
num('EtwoGapAvgLo', ci('gap_avg')[0]); num('EtwoGapAvgHi', ci('gap_avg')[1])
num('EtwoGapSM', e('gap_sm'), 1); num('EtwoGapFastOne', e('gap_fast'), 1); num('EtwoGapFastSMOne', e('gap_fast_sm'), 1)
num('EtwoGapSlowOne', e('gap_slow'), 1); num('EtwoGapSlowGMOne', e('gap_slow_gm'), 1)
num('EtwoGapAvg', e('gap_avg')); num('EtwoGapAvgOne', e('gap_avg'), 1)
num('EtwoGapFast', e('gap_fast')); num('EtwoGapFastSM', e('gap_fast_sm'))
num('EtwoGapSlow', e('gap_slow')); num('EtwoGapSlowGM', e('gap_slow_gm'))

# ---------------------------------------------------------------------------------------------- ceiling
C = CAL['ceiling']
cases = [('Fav', 'favorable'), ('Cen', 'central'), ('Cons', 'conservative'), ('High', 'high compute')]
for tag, key in cases:
    c = C[key]
    num('Gstar' + tag, c['G100'])                      # market growth for R_max = 100, k = 0
    num('Gstar' + tag + 'One', c['G100'], 1)
    num('GstarAcc' + tag, c['G100_acc'])               # accountability costs only
    num('Margin' + tag, c['base'], 1)                  # margin term (ceiling at G = 0), one decimal
    num('Margin' + tag + 'R', c['base'])               # rounded
    num('Cfull' + tag, c['c_full'], 1)
    num('Cc' + tag, c['c_c'])
    for G, gname in [(0.05, 'Five'), (0.15, 'Fifteen'), (0.30, 'Thirty')]:
        num('Ceil' + tag + gname, c['base'] + G)       # ceiling at k = 0
    num('MarginAcc' + tag, c['base_acc'], 1)           # margin term with accountability costs only
    # Table tab:ceiling columns (G, k), psi = 0, delta_K = 0: R_max = base + (1 - k) G, one decimal
    for col, (G, kk) in zip('ABCDEF', [(0.05, 0), (0.15, 0), (0.30, 0), (0.15, 0.5), (0.05, 1.5), (0.30, 1.5)]):
        num('CeilTab' + tag + col, c['base'] + (1 - kk) * G, 1)
cc = {float(k): v for k, v in CAL['cc_sensitivity'].items()}
num('CcLo', min(cc)); num('CcHi', max(cc))
num('GstarCcLo', cc[min(cc)][0]); num('GstarCcHi', cc[max(cc)][0])
num('GstarAccCcLo', cc[min(cc)][1]); num('GstarAccCcHi', cc[max(cc)][1])
tau = {float(k): v for k, v in CAL['tau_sensitivity'].items()}
num('TauLow', 0.09); num('GstarTauLow', tau[0.09][0]); num('GstarAccTauLow', tau[0.09][1])
num('GstarTauLo', tau[0.15][0]); num('GstarTauHi', tau[0.21][0])
am = {float(k): v for k, v in CAL['amin_sensitivity'].items()}
num('GstarAminLo', am[min(am)][0]); num('GstarAminHi', am[max(am)][0])
num('AminLo', min(am), 1); num('AminHi', max(am), 1)
ce = CAL['cerr_sensitivity']
num('GstarCerrFav', ce['favorable'][1]); num('GstarCerrCons', ce['conservative'][1])
num('GstarCerrHigh', ce['high rates, unit loss'][1]); num('CerrHigh', ce['high rates, unit loss'][0], 1)
ps = CAL['psi_sensitivity']
loss = ps['ceiling_k15_G30_loss']
num('KcapLossNone', loss['none']['0.18'])
num('KcapLossDomLo', min(loss['domestic'].values())); num('KcapLossDomHi', max(loss['domestic'].values()))
num('KcapLossForLo', min(loss['foreign_15y'].values())); num('KcapLossForHi', max(loss['foreign_15y'].values()))
num('PsiAddMax', max(C[c_]['tau'] for c_ in C) * 1.5 * 0.30, 1)    # tau k G at k = 1.5, G = 0.30, largest tau
num('PsiFifteen', ps['psi']['foreign_15y'], 2, pct=False); num('PsiFive', ps['psi']['prior_5y'], 2, pct=False)
cen = C['central']
num('ReplCen', (1 - cen['tau']) * 0.25 * 0.5, 2)       # (1 - tau) delta_K k at delta_K = 0.25, k = 0.5, points
num('OwnMarkupFive', 3.3 * 0.05)                        # Remark rem:owncompute at psi = 1: s_srv L_srv G = 0.6 x 5.5 x G
num('OwnMarkupFifteen', 3.3 * 0.15)
num('OwnMarkupFiveNone', (cen['tau'] * 0.6 + 3.3 * 0.05) / (1 - cen['tau']))      # psi = 0 sensitivity
num('OwnMarkupFifteenNone', (cen['tau'] * 0.6 + 3.3 * 0.15) / (1 - cen['tau']))
for tag, key in cases:                                    # input columns of Table tab:ceiling
    c = C[key]
    num('CeilCc' + tag, c['c_c'], 2, pct=False); num('CeilF' + tag, c['f'], 3, pct=False)
    num('CeilAmin' + tag, c['a_min'], 3, pct=False); num('CeilTau' + tag, c['tau'], 2, pct=False)
    num('CeilAminPct' + tag, c['a_min'], 1 if abs(1000 * c['a_min'] - round(1000 * c['a_min'])) < 1e-9 and round(1000 * c['a_min']) % 10 else 0)
num('FeeLo', min(C[c_]['f'] for c_ in C), 0); num('FeeHi', max(C[c_]['f'] for c_ in C), 0)
AG = CAL['amin_grounding']
num('AminGaCoreFive', AG['p5_1to10bn'], 1); num('AminGaCoreTen', AG['p10_above10bn'], 1)

# Rule of 1000 (Proposition prop:saturation(d)) and the duration bound (Corollary cor:transient)
L1000 = {float(k): v for k, v in CAL['Lambda_rule1000'].items()}
num('LamThouLo', L1000[0.45], 1, pct=False); num('LamThouHi', L1000[0.25], 1, pct=False)
# Pull implied by the anchor's upper-quartile surplus: upper bound on growth spend only (revision v2). Under the lower
# bound no spend buys growth, so the surplus is not a return to spend and implies no demand pull (the reason the old
# horizon upper ends were dropped, revision plan A9); the JSON keeps both bounds for the record.
lp = CAL['lam_for_Pi']['ub']
num('LamPiLo', min(lp.values()), 2, pct=False)
num('LamPiHi', max(lp.values()), 2, pct=False)
mult = CAL['rule1000_multiple']['ub']
num('PullMultLo', min(mult.values()), 0, pct=False)
num('PullMultHi', max(mult.values()), 0, pct=False)


def transient_bound(s0, Rbar=10.0, m0=0.6, G=0.2, X=1.0, k=0.0, sbar=0.5):
    Rinf = m0 + (X - k) * G
    return math.log(sbar / s0) / math.log(1 + (Rbar - Rinf) / ((X - k) * (1 + G)))


put('TransOnePct', str(math.floor(transient_bound(0.01))))         # years at 1,000 points from 1% share
put('TransSmall', str(math.floor(transient_bound(1e-5))))          # from a thousandth of a percent
G_e, r_e, k_e = 0.05, 0.10, 0.5                                     # free-entry example of Proposition prop:entry
num('EntryScore', G_e + (r_e - G_e) * k_e, 1)           # the 92.5-point rent example is withdrawn (Proposition prop:entry(d))

# ---------------------------------------------------------------------------------------------- anchor
# Central anchor (D-3): the E1 calibration rule on the audited sample (notes/calibration_anchor_v3.json via
# code/calibrate_horizons.py); intervals in the macros AncPi* of the v3 block below.
A = CAL['anchor']
assert CAL['anchor_estimand'].startswith('E1')
put('AnchorN', str(A['n'])); put('AnchorFirms', str(A['n_firms'])); put('AnchorTail', str(A['n_tail']))
put('AnchorAcqExcl', str(A['n_acq_excluded'])); put('AnchorMarginAbove', str(A['n_tail_m_above_p95']))
for nm, key in [('Mzero', 'm0_ub'), ('Dur', 'Rinf_ub'), ('Pi', 'Pi_ub'), ('MzeroLb', 'm0_lb'), ('DurLb', 'Rinf_lb'),
                ('PiLb', 'Pi_lb')]:
    q = A[key]
    num('Anchor' + nm + 'Lo', q[0]); num('Anchor' + nm + 'Med', q[1]); num('Anchor' + nm + 'Hi', q[2])
num('AnchorScoreMed', A['R'][1])
num('AnchorShift', A['shift'])
num('AnchorGapCen', cen['base'] - A['m0_ub'][1])
num('AnchorGapFav', C['favorable']['base'] - A['m0_ub'][1])
num('AnchorTaxGap', max(ps['anchor_tau_kg']), 1)                     # tau k g at the quartiles, at most (points)
num('AnchorPthree', A['p95']); num('AnchorG', A['G'], 1)
num('MedCostRevenue', 1 - CAL['pass_through']['gross_margin_median_2023_25'])   # median cost of revenue, 2023-25 (audited panel)
put('AnchorPiUbPos', str(int(round(A['share_Pi_ub_positive'] * A['n']))))   # anchor firm-years above their durable level, upper bound

# ---------------------------------------------------------------------------------------------- accountability floor
# Illustrative example of Proposition prop:amin (Remark rem:amin-values; checked by code/verify_theory.py 25d, 25f, 27c).
# Round 2 (C1-C3; RR-N1, RR-N3 to N7, F2-2, F2-3, X2-N13, X2-N14): the remote threshold is a class d scenario parameter
# with no central value, so every output is given at 1% and at 5% a year; the cross-type term p^cc and the human miss
# rate on AI-missed items (automation bias) enter with break-evens; the direct audit and SOX cost is re-grounded on the
# KPMG 2025 SOX survey by revenue size.
def amin_P(nh, na, ph=0.05, pch=0.002, pa=0.02, pca=0.005, pcc=0.0, phm=None):
    """Probability that a material misstatement passes one opportunity (Proposition prop:amin(a)). phm: the human
    layers' miss rate on items the AI layers missed (automation bias), replacing ph when both types are present."""
    if not (nh or na):
        return 1.0
    P = 1.0
    if nh:
        p_h = phm if (na and phm is not None) else ph
        P *= pch + (1 - pch) * p_h ** nh
    if na:
        P *= pca + (1 - pca) * pa ** na
    return pcc + (1 - pcc) * P


# ITGC and revalidation line of the AI layers (follow-up 2 Nov, plan C6): the sourced line of one in-scope AI application,
# c_line below ($204,672: access, change, the upgrade retest, operations and interfaces), replaces the earlier $350,000; the
# two described the same object (the line already contains the revalidation at each model upgrade)
ITGC_LINE_DESIGN = (2000.0 * (3 + 12) + 2500.0 * 24 + 24e3 / 1.22 + 55e3 + 10000.0 * 4)
ITGC_OLD_DESIGN = 3.5e5


def amin_cost(nh, na, ch=5e5, ca=5e4, itgc=ITGC_LINE_DESIGN):
    return (itgc if na else 0.0) + nh * ch + na * ca


def amin_best(pibar, N=24, pca=0.005, kind='any', nmax=7, pcc=0.0, phm=None):
    """Cheapest admissible design at threshold pibar (Proposition prop:amin(b),(c)): admissible iff the probability of
    at least one material misstatement in the year, 1 - (1 - P)^N, is at most pibar. Returns (cost, nh, na) or None."""
    best = None
    for nh in range(nmax):
        for na in range(nmax):
            if not (nh or na) or (kind == 'human' and na) or (kind == 'ai' and nh):
                continue
            if 1 - (1 - amin_P(nh, na, pca=pca, pcc=pcc, phm=phm)) ** N <= pibar and (best is None or amin_cost(nh, na) < best[0]):
                best = (amin_cost(nh, na), nh, na)
    return best


REV = 1e9
N_OPP = 24
EPS = {'One': 0.01, 'Five': 0.05}                      # remote threshold: scenario values (class d), no central value
Pbar = lambda e, N=N_OPP: 1 - (1 - e) ** (1 / N)       # per-opportunity ceiling
pyear = lambda d, N=N_OPP, pca=0.005, pcc=0.0, phm=None: 1 - (1 - amin_P(d[1], d[2], pca=pca, pcc=pcc, phm=phm)) ** N
B_ = {t: amin_best(e) for t, e in EPS.items()}
assert B_['Five'][1:] == (1, 1) and B_['One'][1:] == (1, 2)          # Remark rem:amin-values: 1 human over 1 / 2 AI layers
assert all(amin_best(e, kind='ai') is None for e in EPS.values())       # no all-AI design passes in the example
best_h = amin_best(EPS['Five'], kind='human')                          # all-human designs pass only at 5% (three layers)
assert amin_best(EPS['One'], kind='human') is None and best_h[1] == 3
alt_N, alt_c = amin_best(EPS['Five'], N=48), amin_best(EPS['Five'], pca=0.01)
assert alt_N[1:] == (1, 2) and alt_c[1:] == (1, 1)
alt1_N, alt1_c = amin_best(EPS['One'], N=48), amin_best(EPS['One'], pca=0.01)
assert alt1_N[1:] == (2, 1) and alt1_c[1:] == (2, 1)
best_alt = max(alt1_N[0], alt1_c[0])
b_cen, b_sens = B_['Five'], B_['One']                                  # names kept for the v2 macros below
# direct costs at $1 billion of revenue. v2: audit fees at the S&P 500 ratio ($343 per $1 million of revenue, Ideagen
# Audit Analytics, FY2022) plus the SEC's 2009 median Section 404 cost ($1.04 million). Round 2 (C3, lead-agent rulings of
# 2 Nov): SOX program budget of the KPMG 2025 SOX survey by revenue size (FY2024: under $5 billion $1.5 million, $5-25
# billion $2.7 million, over $25 billion $4.7 million, average $2.3 million; "including both internal and external
# resources", i.e. co-source providers, not the auditor's fee); archived copy, web.archive.org 18 Mar 2026, p. 12, values
# read from a text extraction, chart layout and labels verified by the lead agent (columns large, mid, small). Audit fee:
# central the FY2022 average of accelerated filers, $1,492,375 (Ideagen Audit Analytics, Audit Fee Trends 2003-2022, July
# 2023, p. 14, read in the PDF by the lead agent); low bound the S&P 500 ratio, $343 per $1 million of revenue; high case
# the large-accelerated-filer average, $5,327,646.
AUDIT_FEE_LO = 343.0 * 1000
AUDIT_FEE = 1492375.0
AUDIT_FEE_HI = 5327646.0
KPMG_SIZE = {'Small': 1.5e6, 'Mid': 2.7e6, 'Avg': 2.3e6}
direct_old = (AUDIT_FEE_LO + 1.04e6) / REV
direct = (AUDIT_FEE + KPMG_SIZE['Small']) / REV                       # a $1 billion firm is in KPMG's under-$5bn class
direct_lo = (AUDIT_FEE_LO + KPMG_SIZE['Small']) / REV
direct_hi = (AUDIT_FEE_HI + KPMG_SIZE['Small']) / REV
ITGC_UNITS = dict(c_acc=2000.0, c_chg=2500.0, C_val=24e3, c_ifc=10000.0)
c_line = (ITGC_UNITS['c_acc'] * (3 + 12) + ITGC_UNITS['c_chg'] * 24 + ITGC_UNITS['C_val'] / 1.22 + 55e3
          + ITGC_UNITS['c_ifc'] * 4)
c_ref = 80e3                                                          # params.yaml icfr_line_per_in_scope_ai_application_usd
c_fb = 161e3                                                          # close fallback (companion paper)
apps = lambda fl, line: 1 + math.ceil((0.005 - fl) / (line / REV)) if fl < 0.005 else 0
floor_ = {t: direct + B_[t][0] / REV for t in EPS}
floor_old = direct_old + amin_cost(1, 1, itgc=ITGC_OLD_DESIGN) / REV          # v2: S&P 500 fee, SEC 404 median, $350k ITGC
floor_lo = {t: direct_lo + B_[t][0] / REV for t in EPS}
floor_hi = {t: direct_hi + B_[t][0] / REV for t in EPS}
put('AminEpsCen', fmt(EPS['Five'], 0)); put('AminEpsSens', fmt(EPS['One'], 0))
num('AminHuman', best_h[0] / REV, 2); num('AminBest', b_cen[0] / REV, 3); num('AminBestOne', b_sens[0] / REV, 3)
num('AminAlt', best_alt / REV, 2); num('AminDirect', direct, 2); num('AminDirectOld', direct_old, 2)
num('AminDirectLo', direct_lo, 2); num('AminDirectHi', direct_hi, 2)
for t in EPS:
    num('AminFloorLo' + ('' if t == 'Five' else t), floor_lo[t], 2); num('AminFloorHi' + ('' if t == 'Five' else t), floor_hi[t], 2)
    put('ItgcAppsLo' + ('' if t == 'Five' else t), str(apps(floor_lo[t], c_line)))
    put('ItgcAppsRefLo' + ('' if t == 'Five' else t), str(apps(floor_lo[t], c_ref)))
num('AuditFeeAccel', AUDIT_FEE / 1e6, 2, pct=False); num('AuditFeeLarge', AUDIT_FEE_HI / 1e6, 2, pct=False)
num('AuditFeeSp', AUDIT_FEE_LO / 1e6, 2, pct=False)
put('ItgcDesignOld', '350{,}000', '350,000')
num('AminCenCostOld', amin_cost(1, 1, itgc=ITGC_OLD_DESIGN) / 1e6, 2, pct=False)
num('AminSensCostOld', amin_cost(1, 2, itgc=ITGC_OLD_DESIGN) / 1e6, 2, pct=False)
num('GstarAminFloor', 1 - (1 - C['central']['tau']) * (1 - C['central']['c_c'] - C['central']['f'] - floor_['Five']
                                                        - C['central']['c_full']), 1)   # G* if a_min were the bottom-up floor
num('AminCenCost', b_cen[0] / 1e6, 2, pct=False); num('AminCenProb', pyear(b_cen), 1)
num('AminSensCost', b_sens[0] / 1e6, 2, pct=False); num('AminSensProb', pyear(b_sens), 1)
num('AminHumanCost', best_h[0] / 1e6, 2, pct=False); num('AminHumanProb', pyear(best_h), 2)
num('AminAltNCost', alt_N[0] / 1e6, 2, pct=False); num('AminAltCProb', pyear(alt_c, pca=0.01), 1)
num('AminAltOneCost', best_alt / 1e6, 2, pct=False)
num('AminAiLim', 1 - (1 - 0.005) ** 24, 1); num('AminHumLim', 1 - (1 - 0.002) ** 24, 1)
put('ItgcRetest', f"{int(ITGC_UNITS['C_val']):,}".replace(',', '{,}'), f"{int(ITGC_UNITS['C_val']):,}")
num('ItgcLine', c_line / REV, 3); num('ItgcLineFb', (c_line + c_fb) / REV, 2); num('ItgcLineRef', c_ref / REV, 3)
num('AminFloor', floor_['Five'], 2); num('AminFloorOne', floor_['One'], 2); num('AminFloorOld', floor_old, 2)
put('ItgcApps', str(apps(floor_['Five'], c_line))); put('ItgcAppsOne', str(apps(floor_['One'], c_line)))
put('ItgcAppsRef', str(apps(floor_['Five'], c_ref))); put('ItgcAppsRefOne', str(apps(floor_['One'], c_ref)))
put('ItgcAppsFb', str(1 + math.ceil((0.005 - floor_['Five'] - c_fb / REV) / ((c_line + c_fb) / REV))))
put('ItgcAppsOld', str(apps(floor_old, c_line)))
for nm_, v_ in KPMG_SIZE.items():
    num('KpmgSox' + nm_, v_ / 1e6, 1, pct=False)
    num('AminDirect' + nm_, (AUDIT_FEE + v_) / REV, 2)                   # with the accelerated-filer fee (central)
    num('AminFloor' + nm_, (AUDIT_FEE + v_) / REV + b_cen[0] / REV, 2)
    put('ItgcApps' + nm_, str(apps((AUDIT_FEE + v_) / REV + b_cen[0] / REV, c_line)))
    put('ItgcAppsRef' + nm_, str(apps((AUDIT_FEE + v_) / REV + b_cen[0] / REV, c_ref)))
# C1: per-objective reading, the common-mode condition, and both thresholds side by side
N_OBJ = 10
for t, e in EPS.items():
    num('AminObj' + t, 1 - (1 - e) ** (1 / N_OBJ), 2)                  # per-objective level over 10 objectives
    num('AminPbar' + t, Pbar(e), 4, pct=False)                         # per-opportunity ceiling = the p^cm condition
    num('AminPbarPct' + t, Pbar(e), 3)
    bo = amin_best(1 - (1 - e) ** (1 / N_OBJ))
    put('AminObjDesign' + t, f"{bo[1]} human over {bo[2]} AI" if bo else 'none')
    num('AminObjCost' + t, bo[0] / 1e6, 2, pct=False) if bo else put('AminObjCost' + t, 'none')
put('AminObjN', str(N_OBJ))
# C2: break-evens in the cross-type common mode p^cc and in the human miss rate on AI-missed items
DESIGNS = [(1, 1), (1, 2), (2, 1), (2, 2), (3, 0)]
BE = {}
for t, e in EPS.items():
    for d_ in DESIGNS:
        P0 = amin_P(*d_)
        BE[(t, d_)] = (Pbar(e) - P0) / (1 - P0)                       # largest p^cc at which the design stays admissible
        nm_ = {(1, 1): 'OneOne', (1, 2): 'OneTwo', (2, 1): 'TwoOne', (2, 2): 'TwoTwo', (3, 0): 'ThreeZero'}[d_]
        if BE[(t, d_)] > 0:
            num(f'AminPcc{nm_}{t}', BE[(t, d_)], 4, pct=False); num(f'AminPccPct{nm_}{t}', BE[(t, d_)], 3)
        else:
            put(f'AminPcc{nm_}{t}', 'none'); put(f'AminPccPct{nm_}{t}', 'none')
    Pai = 0.005 + (1 - 0.005) * 0.02
    phm = ((Pbar(e) / Pai) - 0.002) / (1 - 0.002)
    num('AminPhm' + t, phm, 1)                                          # largest human miss rate on AI-missed items, 1 over 1
PCC_GRID = [0.0, 0.0001, 0.0002, 0.0005, 0.0008, 0.001, 0.0015, 0.002, 0.0025]
PHM_GRID = [0.05, 0.10, 0.20, 0.50]
dname = lambda b: 'none admissible' if b is None else f"{b[1]}H + {b[2]}AI, \\${b[0] / 1e6:.2f}m ({100 * b[0] / REV:.3f}\\%)"
_pr = [f"{x:g} & " + ' & '.join(dname(amin_best(EPS[t], pcc=x)) for t in ('One', 'Five')) + r' \\' for x in PCC_GRID]
_hr = [f"{x:g} & " + ' & '.join(dname(amin_best(EPS[t], phm=x)) for t in ('One', 'Five')) + r' \\' for x in PHM_GRID]
tabp = r"""\begin{table}[t]\centering\small
\caption{Cheapest admissible control design in the example of Remark~\ref{rem:amin-values}, by remote threshold, as the cross-type common mode $p^{\rm cc}$ and the human miss rate on AI-missed items vary}\label{tab:amin-pcc}
\begin{tabular}{@{}lll@{}}\toprule
 & $\bar\pi=1\%$ a year & $\bar\pi=5\%$ a year\\\midrule
\multicolumn{3}{@{}l}{\emph{Cross-type common mode $p^{\rm cc}$ per opportunity (human miss rate 0.05)}}\\
""" + '\n'.join(_pr) + r"""
\addlinespace\multicolumn{3}{@{}l}{\emph{Human miss rate on items the AI layers missed ($p^{\rm cc}=0$)}}\\
""" + '\n'.join(_hr) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: """ + f"{N_OPP}" + r""" opportunities a year at \$1 billion of revenue; human layer: miss rate 0.05, common mode 0.002, \$500{,}000; AI layer: miss rate 0.02, common mode 0.005, \$50{,}000, plus the ITGC and revalidation line of one in-scope AI application, \$""" + f"{ITGC_LINE_DESIGN:,.0f}".replace(",", "{,}") + r""", for any design with AI layers; designs of up to six layers of each type. H: human layers; AI: AI layers; cost in millions of dollars and as a share of revenue. A design is admissible if the probability of at least one undetected material misstatement in the year is at most $\bar\pi$. The threshold is a scenario value; the table conditions on it and on the illustrative layer parameters, and it is not a control-design recommendation.
\end{table}"""
open(os.path.join(BASE, 'sections', 'tables', 'tab_amin_pcc.tex'), 'w').write(tabp)
AMIN_R2 = dict(Pbar={t: Pbar(e) for t, e in EPS.items()}, breakeven_pcc={f'{t}|{d_}': v for (t, d_), v in BE.items()},
               cheapest_by_pcc={t: {x: amin_best(EPS[t], pcc=x) for x in PCC_GRID} for t in EPS},
               cheapest_by_phm={t: {x: amin_best(EPS[t], phm=x) for x in PHM_GRID} for t in EPS},
               floor=floor_, floor_old=floor_old, floor_lo=floor_lo, floor_hi=floor_hi, direct=direct, direct_old=direct_old,
               direct_lo=direct_lo, direct_hi=direct_hi, itgc_design=ITGC_LINE_DESIGN,
               apps={'invoice_line': {t: apps(floor_[t], c_line) for t in EPS}, 'reference_line': {t: apps(floor_[t], c_ref) for t in EPS}})
json.dump({k: {str(kk): vv for kk, vv in v.items()} if isinstance(v, dict) else v for k, v in AMIN_R2.items()},
          open(os.path.join(BASE, 'notes', 'amin_r2.json'), 'w'), indent=1, default=str)
PIBAR, PIBAR_SENS = EPS['Five'], EPS['One']

# ---------------------------------------------------------------------------------------------- pace
P = CAL['pace']
for tag, key in [('Cen', 'central'), ('Fast', 'fast')]:
    pc = P[key]; prm = pc['params']
    num('PaceCap' + tag, prm['kappa_abs'])
    num('PaceSucc' + tag, prm['varpi'], 2, pct=False)
    num('PaceDisr' + tag, pc['nuD'], 2, pct=False)
    num('PaceEmb' + tag, prm['Temb'], 0 if float(prm['Temb']).is_integer() else 2, pct=False)   # 1.25 since 29 Oct
    num('PaceReal' + tag, prm['bbar'])
    num('PaceFrz' + tag, (pc['clock'] - 1) / pc['clock'])
    num('PaceQ' + tag, pc['q'], 2, pct=False)
    num('PaceRate' + tag, pc['eff_rate'], 1)              # q rho / clock: attempts that succeed, share of the program a year
    if 'eff_rate_realized' in pc:                          # written by calibrate_horizons.py since the params commit
        num('PaceRateReal' + tag, pc['eff_rate_realized'], 1)  # bbar q rho / clock: realized value, share of the program a year
    if tag == 'Cen':
        num('PaceDip' + tag, pc['2028']['dip'], 1)
    for y, yn in [('2028', 'Eight'), ('2031', 'One'), ('2036', 'Six')]:
        num('Pace' + tag + yn, pc[y]['s'], 1 if pc[y]['s'] < 0.05 else 0)
put('PaceNproc', str(P['central']['params']['n_proc']))
put('PaceFastDone', str(math.floor(P['fast']['complete_year'] + 0.5)))
assert P['central']['cross_years'] is not None
put('PaceCrossCen', str(math.floor(P['central']['cross_years'] + 0.5)))
slow = CAL['variants']['slow_public']
num('PaceCapSlow', slow['rho_chg'])
V = CAL['variants']
num('VarDipOneShare', V['public_guided_dip_1pt']['2036']['s'])
num('VarDipTwoShare', V['public_guided_dip_2pt']['2036']['s'])
num('VarDipOneInit', V['public_guided_dip_1pt']['a0_share'])
assert CAL['variants_basis'].startswith('central path')
num('VarDipOneMzero', V['public_guided_dip_1pt']['m0']['2036'] - A['m0_net'][1])
num('VarCenMzero', V['central_fluid']['m0']['2036'] - A['m0_net'][1])
num('VarSlowShare', V['slow_public']['2036']['s'], 1)     # the horizons text quotes this share (no longer 'under 1%')

# ---------------------------------------------------------------------------------------------- round 2 (29 Oct 2026)
# compute share and thresholds by horizon (fixed prices), the pass-through scenarios, the revealed-pace reference
# notes/calibration_results.json is regenerated at the freeze (notes/params_commit_2026-10-29.md); until then the live
# file predates the params commit and the round-2 macros, which no section uses yet, are skipped with a warning.
ROUND2 = 'ceiling_by_horizon' in CAL
if not ROUND2:
    print('NOTE: notes/calibration_results.json predates the params commit; round-2 macros skipped', file=sys.stderr)
if ROUND2:
    CH = CAL['ceiling_by_horizon']
    YN_LONG = [('2028', 'TwentyEight'), ('2031', 'ThirtyOne'), ('2036', 'ThirtySix')]   # 'One' already means one decimal here
    for y, yn in YN_LONG:
        for tag, key in [('Fav', 'favorable'), ('Cen', 'central'), ('Cons', 'conservative')]:
            num('Cc' + tag + yn, CH[y][key]['c_c'])
            num('Gstar' + tag + yn, CH[y][key]['G100']); num('Gstar' + tag + yn + 'One', CH[y][key]['G100'], 1)
            num('GstarAcc' + tag + yn, CH[y][key]['G100_acc'])
            num('Margin' + tag + yn, CH[y][key]['base'], 1)
    num('CcValueTestCap', CAL['compute_share']['high_compute_case']['value_test_cap'])
    PT = CAL['pass_through']
    for phi, ptag in [('0.5', 'PhiHalf'), ('0.7', 'PhiSeven')]:
        pt = PT[phi]
        num('Dur' + ptag, pt['dur'], 2, pct=False)
        num('Gstar' + ptag, pt['ceiling']['central']['G100']); num('Gstar' + ptag + 'One', pt['ceiling']['central']['G100'], 1)
        for y, yn in YN_LONG:
            num('Gstar' + ptag + yn, pt['ceiling_by_horizon'][y]['central']['G100'])
            ub, lb = pt['upper_bound'][y]['0.0']['R'], pt['lower_bound'][y]['0.0']['R']
            num('Hz' + ptag + yn + 'Lo', min(ub[0], lb[0])); num('Hz' + ptag + yn + 'Hi', max(ub[1], lb[1]))
    num('PassHHI', PT['hhi'], 2, pct=False)
    RV = CAL['revealed_pace']
    num('RevealedOpMed', RV['gaap_op_margin']['median'] / 100, 1); num('RevealedOpLo', RV['gaap_op_margin']['p25'] / 100, 1)
    num('RevealedOpHi', RV['gaap_op_margin']['p75'] / 100, 1); num('RevealedFcfMed', RV['fcf_sbc_margin']['median'] / 100, 1)
    put('RevealedN', str(RV['gaap_op_margin']['n']))
    for tag, key in [('Cen', 'central'), ('Fast', 'fast')]:
        pp = CAL['pace_previous'][key]
        for y, yn in [('2028', 'Eight'), ('2031', 'One'), ('2036', 'Six')]:
            num('PacePrev' + tag + yn, pp[y]['s'], 1)
    put('PacePrevCrossCen', str(math.floor(CAL['pace_previous']['central']['cross_years'] + 0.5)))

# ---------------------------------------------------------------------------------------------- horizons
YN = [('2028', 'Eight'), ('2031', 'One'), ('2036', 'Six')]
for y, yn in YN:
    ub = CAL['upper_bound'][y]; lb = CAL['lower_bound'][y]
    for b, tag in [(ub, 'Ub'), (lb, 'Lb')]:
        num(tag + yn + 'Lo', b['0.0']['R'][0]); num(tag + yn + 'Hi', b['0.0']['R'][1])
        num(tag + 'Dur' + yn + 'Lo', b['0.0']['Rinf'][0]); num(tag + 'Dur' + yn + 'Hi', b['0.0']['Rinf'][1])
    num('Hz' + yn + 'Lo', min(ub['0.0']['R'][0], lb['0.0']['R'][0]))
    num('Hz' + yn + 'Hi', max(ub['0.0']['R'][1], lb['0.0']['R'][1]))
    num('HzDur' + yn + 'Lo', min(ub['0.0']['Rinf'][0], lb['0.0']['Rinf'][0]))
    num('HzDur' + yn + 'Hi', max(ub['0.0']['Rinf'][1], lb['0.0']['Rinf'][1]))
    num('Kh' + yn + 'Lo', ub['0.5']['R'][0]); num('Kh' + yn + 'Hi', ub['0.5']['R'][1])
    kd = ps['k05_upper_bound']['domestic'][y]
    num('Kd' + yn + 'Lo', kd[0]); num('Kd' + yn + 'Hi', kd[1])

# ---------------------------------------------------------------------------------------------- central path (v2)
# Central path and tornado of code/calibrate_horizons.py (revision plan A9, D5): Table tab:calib and Table tab:tornado.
CPA = CAL['central_path']
for y, yn in YN:
    # round 2 (decision 4): CenR* is the maintenance-netted central basis; CenRUb* and CenRLb* are the two bounds
    u, l_, n_ = CPA['path']['ub'][y], CPA['path']['lb'][y], CPA['path']['net'][y]
    assert CPA['central_basis'] == 'net'
    num('CenShare' + yn, n_['s']); num('CenTarget' + yn, n_['target']); num('CenMzero' + yn, n_['m0']); num('CenR' + yn, n_['R'])
    num('CenMzeroUb' + yn, u['m0']); num('CenRUb' + yn, u['R'])
    num('CenMzeroLb' + yn, l_['m0']); num('CenRLb' + yn, l_['R']); num('CenDip' + yn, n_['dip'], 1)
    num('CenDipUb' + yn, u['dip'], 1)
    num('CenEmb' + yn, n_['s'] / CAL['pace']['central']['params']['bbar'])      # embedded share = realized / bbar
    num('CenRise' + yn, n_['m0'] - CPA['path']['net']['m0A'])                    # intercept gain since the anchor
    for phi, ptag in [('0.5', 'PhiHalf'), ('0.7', 'PhiSeven')]:
        num('CenR' + ptag + yn, CPA['pass_through'][phi]['net'][y]['R'])
    AIv = CAL['r2']['anchor_interval']                                          # B5: anchor-sampling intervals, 90%
    for b, bt in [('net', ''), ('ub', 'Ub'), ('lb', 'Lb')]:
        lo_, hi_ = AIv[b]['path'][y]['ci90_joint']
        num(f'CenR{bt}{yn}Lo', lo_); num(f'CenR{bt}{yn}Hi', hi_)
    # editor's naming (round 2): \CenR<yr> = maintenance-netted (central); \CenR<yr>AllSM and \CenR<yr>NoSM = the bounds
    for b, sfx in [('ub', 'AllSM'), ('lb', 'NoSM')]:
        pb_ = CPA['path'][b][y]
        num(f'CenR{yn}{sfx}', pb_['R']); num(f'CenMzero{yn}{sfx}', pb_['m0'])
        lo_, hi_ = AIv[b]['path'][y]['ci90_joint']
        num(f'CenR{yn}{sfx}Lo', lo_); num(f'CenR{yn}{sfx}Hi', hi_)
        for phi, ptag in [('0.5', 'PhiHalf'), ('0.7', 'PhiSeven')]:
            num(f'CenR{ptag}{yn}{sfx}', CPA['pass_through'][phi][b][y]['R'])
    lo_, hi_ = AIv['ub']['path'][y]['ci90_intercept_only']
    num(f'CenRUb{yn}IntLo', lo_); num(f'CenRUb{yn}IntHi', hi_)
    PF = CAL['pace']['fast']
    num('FastShare' + yn, PF[y]['s']); num('FastEmb' + yn, min(1.0, PF[y]['s'] / PF['params']['bbar']))
num('CenAlpha', CPA['alpha'], 2, pct=False)
num('CenG', CAL['anchor']['G'], 1)
TOR = CAL['tornado']
for y, yn in [('2036', 'Six'), ('2028', 'Eight')]:
    T = TOR[y]
    num('TornRef' + yn, T['reference'])
    for r in T['rows']:
        key = ''.join(w.capitalize() for w in r['key'].split('_'))
        num('Torn' + key + yn + 'Lo', r['low']); num('Torn' + key + yn + 'Hi', r['high'])
        num('Torn' + key + yn + 'Swing', r['high'] - r['low'])
    _order = [r['key'] for r in T['rows']]
    put('TornFirst' + yn, {'G': 'market growth', 'pace': 'execution', 'surplus': 'the transient surplus', 'bcg_win': 'the execution yield',
                           'attribution': 'how much selling spend buys growth', 'anchor_quartile': "the anchor's intercept",
                           'target': 'the full-cost target', 'capital': 'capital intensity',
                           'pass_through': 'pass-through', 'dip': 'the dip', 'anchor_sample': 'the anchor sample'}[_order[0]])
EL = CAL['ell_psi']
_st = [EL[r][a_]['steepest'] for r in ('E1_cash_w60', 'E1_op_w60') for a_ in ('0.25', '0.45')]
num('PsiSteepLo', min(_st), 2, pct=False); num('PsiSteepHi', max(_st), 2, pct=False)
_el = [EL[r][a_]['ell'] for r in ('E1_cash_w60', 'E1_op_w60') for a_ in ('0.25', '0.45')]
num('PsiEllLo', min(_el), 2, pct=False); num('PsiEllHi', max(_el), 2, pct=False)

# ---------------------------------------------------------------------------------------------- round 2 (2 Nov 2026)
# notes/calibration_results.json block 'r2' (code/calibrate_horizons.py); items B1-B12 of revision_plan_r2.md
R2 = CAL['r2']


def sgn(name, x, nd=1, pct=True):
    """signed number with an explicit plus sign (for intervals and changes); redefined identically in the v3 block"""
    s_ = fmt(x, nd, pct)
    if s_.startswith('-'):
        put(name, f"$-${s_[1:]}", f"-{s_[1:]}")
    elif float(s_) == 0:
        put(name, s_)
    else:
        put(name, f"$+${s_}", f"+{s_}")


YN3 = [('2028', 'Eight'), ('2031', 'One'), ('2036', 'Six')]
# anchor on the three bases (B6) and its sampling interval (B5)
for b, bt in [('net', 'Net'), ('ub', ''), ('lb', 'Lb')]:
    iv = R2['anchor_interval'][b]['m0A']['ci90']
    num(f'AnchorMzero{bt}CiLo', iv[0], 1); num(f'AnchorMzero{bt}CiHi', iv[1], 1)
    num(f'AnchorMzero{bt}MedOne', A['m0_' + b][1], 1)
for i_, q_ in enumerate(('Lo', 'Med', 'Hi')):
    num('AnchorMzeroNet' + q_, A['m0_net'][i_]); num('AnchorPiNet' + q_, A['Pi_net'][i_])
num('AnchorShiftNet', A['shift_net']); num('MaintBase', CAL['central_path']['maint_base'], 1)
put('AnchorSmAboveBase', str(A['n_sm_above_base']))
num('AnchorGapCenNet', cen['base'] - A['m0_net'][1])
num('AnchorGOneLo', R2['anchor_interval']['G']['ci90'][0], 1); num('AnchorGOneHi', R2['anchor_interval']['G']['ci90'][1], 1)
put('AnchorBootB', str(R2['anchor_interval']['B']))
# B1 pass-through
PTR = R2['pass_through']
for phi, ptag in [('0.5', 'Half'), ('0.7', 'Seven')]:
    v_ = PTR['by_phi'][phi]
    num('PtGstarOld' + ptag, v_['v2_code_variable_old_revenue'], 1)
    num('PtGstarRef' + ptag, v_['referee_rate_phi_1mH_variable'], 1)
    num('PtGstarVar' + ptag, v_['rate_phi_variable'], 1)
    num('PtGstarRefAll' + ptag, v_['referee_rate_phi_1mH_all_ub'], 1)
    num('PtGstarUb' + ptag, v_['rate_phi_all_ub'], 1)
    num('PtGstarLb' + ptag, v_['rate_phi_all_lb'], 1)
    num('PtPriceCut' + ptag, v_['price_cut_central'])
    num('PtElas' + ptag, v_['elasticity_first_order_central'], 2, pct=False)
num('PtCzero', 1 - C['central']['f'] - PTR['C0_m0A'] / (1 - C['central']['tau']))
# final audit M3: whose saving sets the price cut (the anchor's own) and the typical $1-5bn firm's alternative
UC = PTR['unit_costs']
num('PtCzeroOne', UC['C0_anchor'], 1); num('PtKfull', UC['K_full'], 1); num('PtSaving', UC['S_anchor'], 1)
num('PtCzeroTyp', UC['C0_typical']); num('PtSavingTyp', UC['S_typical'], 1)
for phi, ptag in [('0.5', 'Half'), ('0.7', 'Seven')]:
    num('PtGstarTyp' + ptag, PTR['typical'][phi]['G'], 1); num('PtPriceCutTyp' + ptag, PTR['typical'][phi]['price_cut'])
    num('PtGstarTypGap' + ptag, PTR['typical'][phi]['G'] - PTR['by_phi'][phi]['rate_phi_all_net_CENTRAL'], 1)
# B2 compute range under the stated value test
CR = R2['compute_range']
num('CcOldCap', CR['old_cap']); num('GstarCcOldCap', CR['G_old_cap'])
put('CcHighFeasible', 'feasible' if CR['high_feasible'] else 'infeasible')
# B3 compute-path drivers (class d) and the year the path reaches the 2025-price share
CPd = R2['compute_path']
num('CcKappaFront', CPd['kappa_front'], 2, pct=False)
for y, yn in [('2028', 'TwentyEight'), ('2031', 'ThirtyOne'), ('2036', 'ThirtySix')]:
    num('CcOmega' + yn, CPd['omega'][y])
num('CcKappaFixedTwentyEight', CPd['kappa_fixed_2028'], 2)
put('CcYearSix', str(int(math.floor(CPd['year_cc_reaches_2025_value'] + 0.5))))
num('CcYearSixOne', CPd['year_cc_reaches_2025_value'], 1, pct=False)
for k_, nm_ in [('omega_0.3', 'OmegaLo'), ('omega_0.9', 'OmegaHi'), ('kappa_front_0.1', 'KfLo'), ('kappa_front_0.5', 'KfHi')]:
    num('Cc' + nm_ + 'TwentyEight', CPd['sens_2028'][k_]['cc']); num('Gstar' + nm_ + 'TwentyEight', CPd['sens_2028'][k_]['G'])
# B4 error base, transition cost, dips
num('ErrBase', C['central']['c_err_e'] / ((0.0345 + 0.05) * 0.5))                       # W_A (= s_L)
num('CerrHighAi', ce['high rates, unit loss, AI review bound'][0], 1); num('GstarCerrHighAi', ce['high rates, unit loss, AI review bound'][1])
num('CerrHighOld', ce['high rates, unit loss, human catch rates (v2, superseded)'][0], 1)
DP = R2['dip']
num('PaceTpb', DP['Tpb'], 2, pct=False)
num('PaceCrossCenOne', DP['cross_years'], 1, pct=False)
for y, yn in YN3:
    num('DipTpbTwo' + yn, DP['Tpb2'][y], 1)
num('CrossTpbTwo', DP['Tpb2_cross_years'], 1, pct=False)
num('PaceDipFast', DP['fast_central_basis']['2028'], 1); num('PaceDipFastUb', DP['fast_ub_median_central_target']['2028'], 1)
num('PaceDipFastOld', DP['fast_old_range_basis']['2028'], 1)
# B7 payback, NPV, hold periods, decomposition
PB = R2['payback']
for pc, tg in [('central', 'Cen'), ('fast', 'Fast'), ('slow', 'Slow')]:
    v_ = PB[pc]
    num('PayCross' + tg, v_['cross_flow'], 1, pct=False)
    (num('PayBack' + tg, v_['payback_undiscounted'], 1, pct=False) if v_['payback_undiscounted'] is not None
     else put('PayBack' + tg, 'never'))
    (num('PayBackDisc' + tg, v_['payback_discounted'], 1, pct=False) if v_['payback_discounted'] is not None
     else put('PayBackDisc' + tg, 'never'))
    num('PayNpv' + tg, v_['npv_points_years'])                         # NPV, percent of one year's revenue
    num('PayRatio' + tg, v_['ratio'], 1, pct=False)
    num('PayHoldFive' + tg, v_['hold']['5']['cum'], 1); num('PayHoldFiveDisc' + tg, v_['hold']['5']['cum_disc'], 1)
    num('PayHoldThree' + tg, v_['hold']['3']['cum'], 1)
put('PayDoneCen', str(int(math.floor(2025 + PB['central']['complete_years'] + 0.5))))
num('PayRatioCenTen', PB['central_r10']['ratio'], 1, pct=False)
GD = R2['gstar_decomposition']
for k_, nm_ in [('tax', 'Tax'), ('compute', 'Compute'), ('fees', 'Fees'), ('accountability', 'Acc'), ('full_cost', 'Full')]:
    num('Gdec' + nm_, GD[k_], 1)
for k_, nm_ in [('c_mnt', 'Mnt'), ('c_sec', 'Sec'), ('c_err', 'Err'), ('c_anc', 'Anc')]:
    num('Gdec' + nm_, GD['full_cost_parts'][k_], 2)                     # final audit m15: two decimals, so the parts visibly sum
num('GdecFullTwo', GD['full_cost'], 2)
# B8 deferred revenue and a typical $1-5 billion firm
KR = R2['k_rows']['-0.30']['G_star']
num('GstarKdefCen', KR['central']); num('GstarKdefFav', KR['favorable']); num('GstarKdefCons', KR['conservative'])
TY = R2['typical_1to5bn']
put('TypN', str(TY['n'])); put('TypFirms', str(TY['firms']))
for k_, nm_ in [('g', 'G'), ('m_fcf_sbc', 'Margin'), ('R_fcf_sbc', 'Score'), ('R_op', 'ScoreOp'), ('sms', 'Sm'), ('gas', 'Ga'),
                ('rds', 'Rd'), ('gms', 'Gm'), ('sbcs', 'Sbc'), ('m0_net', 'MzeroNet'), ('m0_ub', 'MzeroUb'), ('m0_lb', 'MzeroLb')]:
    num('Typ' + nm_, TY[k_], 1)
num('TypK', TY['k'], 2, pct=False); num('TypGstarK', TY['G_star_at_own_k'])
num('TypGapNet', TY['gap_to_central_margin_term']['net']); num('TypDurNet', TY['durable_at_own_growth']['net'])
# B9 pace bridge
BR = R2['pace_bridge']
num('BridgeOld', BR['s2036_old'], 1); num('BridgeNew', BR['s2036_new'], 1)
sh = BR['shapley']
sgn('BridgeSucc', sh['success (varpi, disruption haircut)']); sgn('BridgeBbar', sh['realized share bbar'])
sgn('BridgeTemb', sh['embedding time T_emb (= T_pb)'])
sgn('BridgeVarpi', BR['shapley4']['varpi']); sgn('BridgeHaircut', BR['shapley4']['haircut removed'])
num('BridgeQOld', BR['old']['q'], 2, pct=False)
num('YieldModel', BR['yield_model'], 2, pct=False); num('YieldExec', BR['yield_exec_like_for_like'], 2, pct=False)
num('YieldMck', BR['yield_mckinsey_unconditional'], 2, pct=False)
num('ShareExec', BR['s2036_at_exec_yield'], 1); num('ShareMck', BR['s2036_at_mck_yield'], 1)
num('ShareBcgWin', BR['s2036_bcg_win'], 1); num('ScoreBcgWin', BR['R2036_bcg_win'])
# B10 decision weight by discount rate; B11 iso-score values
for r_, nm_ in [('0.0934', 'Wacc'), ('0.1000', 'Ten'), ('0.1200', 'Twelve'), ('0.1500', 'Fifteen'), ('0.2200', 'TwentyTwo'),
                ('0.3100', 'ThirtyOne')]:
    num('Weight' + nm_, R2['decision_weight']['by_r'][r_], 1 if R2['decision_weight']['by_r'][r_] >= 2 else 2, pct=False)
for p_ in R2['iso_score']['points']:
    nm_ = {0.30: 'Thirty', 0.20: 'Twenty', 0.10: 'Ten', 0.0: 'Zero'}[round(p_['g'], 2)]
    num('Iso' + nm_, p_['multiple'], 1, pct=False)
# D1/D2 (IM2-N8, F2-1): interest income and deferred revenue in the cash-GAAP wedge (calibrate_horizons.py r2.wedge)
WG = R2['wedge']
for per, pn in [('2016-19', 'Early'), ('2023-25', 'Late')]:
    T_ = WG['top_tail'][per]
    num('Wedge' + pn, T_['wedge'], 1); num('WedgeDdr' + pn, T_['ddr'], 1); num('WedgeOnDdr' + pn, T_['wedge_on_ddr'], 1)
    sgn('WedgeLessDdr' + pn, T_['wedge_less_ddr']); num('WedgeIi' + pn, T_['ii'], 1)
    put('WedgeN' + pn, str(T_['n'])); put('WedgeNDdr' + pn, str(T_['n_ddr'])); put('WedgeNIi' + pn, str(T_['n_ddr_ii']))
    num('WedgeAll' + pn, T_['all_firms']['wedge'], 1)
WA_ = WG['anchor']
num('WedgeAnchor', WA_['wedge'], 1); num('WedgeAnchorDdr', WA_['ddr'], 1); sgn('WedgeAnchorLessDdr', WA_['wedge_less_ddr'])
put('WedgeAnchorNDdr', str(WA_['n_ddr'])); put('WedgeAnchorNIi', str(R2['anchor_interest']['n_with_ii']))
num('WedgeAnchorIi', R2['anchor_interest']['ii_median'], 1)
num('AnchorIiMzeroSame', R2['anchor_interest']['m0_net_same_firm_years']); num('AnchorIiMzero', R2['anchor_interest']['m0_net_less_ii'])
cv = WG['coverage']
for k_, nm_ in [('firm_years', 'All'), ('ii', 'Ii'), ('ii_primary', 'IiPrimary'), ('ddr', 'Ddr'), ('both_differ', 'BothDiffer'),
                ('both_equal', 'BothEqual')]:
    put('SecCov' + nm_, *thousands(cv[k_]))
num('KdefMed', WG['k_def']['median'], 2, pct=False); num('KdefLo', WG['k_def']['p25'], 2, pct=False)
num('KdefHi', WG['k_def']['p75'], 2, pct=False); put('KdefN', str(WG['k_def']['n']))
num('GstarKdefMedCen', WG['G_star_at_kdef']['central'])
num('GBandLo', CAL['central_path']['G_band'][0], 1); num('GBandHi', CAL['central_path']['G_band'][1], 1)
for y, yn in [('2036', 'Six'), ('2028', 'Eight')]:
    gob = CAL['tornado'][y]['G_old_band']
    num('TornGOld' + yn + 'Lo', gob['low']); num('TornGOld' + yn + 'Hi', gob['high'])

# ---------------------------------------------------------------------------------------------- acquired growth
# The treadmill of Proposition prop:acquired-score(f): the existing subscription base shrinks at -G_i = -ln NRR a year.
# Read from sections/tables/acquired_macros.tex (generated by code/verify_part2_acquirer.py from the F-1 extract).
acq_path = os.path.join(BASE, 'sections', 'tables', 'acquired_macros.tex')
if os.path.exists(acq_path):
    acq = dict(re.findall(r'\\providecommand\{\\(acq[A-Za-z]+)\}\{(.*)\}', open(acq_path).read()))
    gi = []
    for key in ['acqGiTwentyFour', 'acqGiTwentyFive']:
        v = acq[key].replace('\\ensuremath{-}', '-').replace('\\%', '')
        gi.append(-float(v))
    put('AcqTreadLo', f"{min(gi):.1f}"); put('AcqTreadHi', f"{max(gi):.1f}")

# ============================================================================================== v3: audited sample
# Revision v2 of Paper 1 (author decisions D-1 to D-3, 29 Oct 2026, 13:53 UTC-7). Every number in sections/data.tex,
# sections/empirics.tex and sections/appendix_data.tex comes from this block. Inputs: code/estimate_v3.py
# (notes/empirics_v3.json, notes/frontier_slope_v3.json), code/build_panel_v3.py (notes/panel_v3_build.json,
# data/panel_v3.csv) and, for the protocol record of the post-test-run rules, notes/empirics_v2_exact.json.
# Units in empirics_v3.json: fractions (0.01 = one point) except slopes, ratios and regression coefficients.
# P1_V3_DIR pins a snapshot of these outputs (one folder holding empirics_v3.json, panel_v3_build.json,
# empirics_v2_exact.json, frontier_slope_v3.json, panel_v3.csv and tab_*_v3.tex), for use while estimate_v3.py is
# being rerun; by default the live files of the repository are read.
V3DIR = os.environ.get('P1_V3_DIR')


def v3path(kind, name):
    return os.path.join(V3DIR, name) if V3DIR else os.path.join(BASE, kind, name)


V3 = json.load(open(v3path('notes', 'empirics_v3.json')))
V3E = V3['estimates']
V3B = json.load(open(v3path('notes', 'panel_v3_build.json')))
V2X = json.load(open(v3path('notes', 'empirics_v2_exact.json')))
FS3 = json.load(open(v3path('notes', 'frontier_slope_v3.json')))
num('PsiSlopeOp', abs(FS3['central']['op']['E1']['est']), 2, pct=False)      # D-2: |Psi_0.90 slope|, E1, g 0-60%
num('PsiSlopeCash', abs(FS3['central']['cash']['E1']['est']), 2, pct=False)
assert V3['meta']['panel'] == 'v3' and not V3['meta']['fast_mode'] and V3['meta']['replications'] >= 999
FOUR = [('E1', 'Eone'), ('E2', 'Etwo'), ('E2imp4', 'ImpFour'), ('E2imp8', 'ImpEight')]
WORD = {0: 'none', 1: 'one', 2: 'two', 3: 'three', 4: 'all four'}


def vrec(stat, e='E1'):
    r = V3E[stat][e]
    assert r.get('est') is not None, (stat, e)
    return r


def vest(stat, e='E1'):
    return vrec(stat, e)['est']


def vci(stat, e='E1'):
    r = vrec(stat, e)
    assert r.get('estimable', True) and r.get('ci90'), (stat, e)
    return r['ci90']


def sgn(name, x, nd=1, pct=True):
    """signed number with an explicit plus sign (for intervals and changes)"""
    s = fmt(x, nd, pct)
    if s.startswith('-'):
        put(name, f"$-${s[1:]}", f"-{s[1:]}")
    elif float(s) == 0:
        put(name, s)
    else:
        put(name, f"$+${s}", f"+{s}")


def ival(prefix, stat, e='E1', nd=1, pct=True):
    lo, hi = vci(stat, e)
    sgn(prefix + 'Lo', lo, nd, pct); sgn(prefix + 'Hi', hi, nd, pct)


def est_se(name, stat, e='E1', nd=2, pct=False, signed=False):
    r = vrec(stat, e)
    (sgn if signed else num)(name, r['est'], nd, pct)
    num(name + 'Se', r['se'], nd, pct)


def count_four(stat, test):
    """number of the four model-facing views (E1, E2, both imputation bounds) whose 90% percentile interval passes"""
    return sum(bool(test(vci(stat, e))) for e, _ in FOUR)


# ---- samples and sample rules (build_panel_v3.py)
S3 = V3['samples']
for e, tag in [('E1', 'Eone'), ('E2', 'Etwo'), ('E2x25', 'Excl'), ('E2imp4', 'Imp')]:
    t_, p_ = thousands(S3[e]['n']); put('VN' + tag, t_, p_); put('VFirms' + tag, str(S3[e]['firms']))
for per, nm in [('2010-15', 'TenFifteen'), ('2016-19', 'SixteenNineteen'), ('2020-22', 'TwentyTwentyTwo'),
                ('2023-25', 'TwentyThreeTwentyFive')]:
    put('VNPer' + nm, str(S3['E1']['by_period'][per]))
    put('VFastPer' + nm, str(S3['E1']['n_g_ge_40'][per.replace('-', '_').replace('_15', '_15')]
                             if per.replace('-', '_') in S3['E1']['n_g_ge_40'] else
                             S3['E1']['n_g_ge_40'][per[:4] + '_' + per[5:]]))
t_, p_ = thousands(V3B['core_v2']); put('VNvTwo', t_, p_); put('VFirmsvTwo', str(V3B['firms_v2']))
assert V3B['core_v3'] == S3['E1']['n'] and V3B['firms_v3'] == S3['E1']['firms']
R1 = V3B['R1']
put('VRone', str(R1['n'])); put('VRoneTen', str(R1['by_type']['fy2010_before_first_xbrl_report']))
put('VRoneIpo', str(R1['by_type']['before_first_annual_report'])); put('VRoneLate', str(R1['by_type']['later_vintage_only']))
num('VRoneGrowth', R1['median_growth_backfilled'], 1); num('VRoneGrowthOther', R1['median_growth_other'], 1)
put('VRthree', str(V3B['excluded']['R3_captive_related_party']))
put('VRfourOld', str(V3B['R4']['v2_flagged'])); put('VRfourNew', str(V3B['R4']['v3_flagged']))
num('VCheapShare', V3B['rules']['cheap_acquisition_min_share']); num('VCaptiveShare', V3B['rules']['related_party_max_share'])
put('VRtwoFirms', str(len(V3B['panel_named']['firms']))); put('VRtwoN', str(V3B['panel_named']['firm_years_in_v3']))
put('VRfiveFirms', str(len(V3B['R5']['debt_only_named']))); put('VRfiveN', str(V3B['R5']['firm_years_v3']))
# Rules after the rerun with the SEC inputs retrieved on 29 October (R3 and R4(c) applied, R5 a flag, R2 on named firms)
_x3 = V3B['R3']['xbrl']
put('VRthreeXbrlN', str(_x3['core_v3_firm_years_with_fact'])); put('VRthreeXbrlHit', str(_x3['n_at_or_above_50pct']))
num('VRthreeMax', _x3['max_share'], 1)
_a4 = V3B['R4']['acquiree_revenue']
put('VRfourCN', str(len(_a4['core_v3_at_or_above_10pct']))); put('VRfourCNew', str(len(_a4['new_flags_core_v2'])))
_nl = V3B['R5']['no_listed_equity_v3']
put('VRfiveFlagN', str(V3B['R5']['firm_years_no_listed_equity_v3'])); put('VRfiveFlagFirms', str(len(_nl)))
assert sum(len(v) for v in _nl.values()) == V3B['R5']['firm_years_no_listed_equity_v3']
_r2 = V3B['R2_named']
put('VRtwoClassFirms', str(len(_r2['non_software']))); put('VRtwoClassN', str(_r2['firm_years_v3_non_software']))
RT = V3['routes']
put('VAffected', str(RT['n_flagged'])); put('VAffAcqYear', str(RT['n_acq_year'])); put('VAffFollow', str(RT['n_following_only']))
put('VAffKept', str(RT['n_kept_pro_forma'])); put('VAffDropped', str(RT['n_dropped'])); num('VAffDroppedShare', RT['share_dropped'], 1)
put('VUnaffected', thousands(RT['n_unaffected_kept'])[0], thousands(RT['n_unaffected_kept'])[1])
put('VUnverified', str(RT['n_unverified']))
_rs = RT['reasons']
put('VDropNoPf', str(_rs['acquisition year: no current-year pro forma revenue in the original filing']))
put('VDropFollow', str(_rs["following year: no valid pro forma revenue in the acquisition year's original filing"]))
put('VDropAmbig', str(_rs['carry-over and current-year comparative both disclosed; readings differ by more than one point']))
put('VDropOther', str(RT['n_dropped'] - sum(_rs[k] for k in _rs if k.startswith(('acquisition year: no current', 'following year', 'carry-over')))))
num('VImpFourAcq', V3['imputation']['4']['median_imputed_acquired_growth'], 1)
num('VImpEightAcq', V3['imputation']['8']['median_imputed_acquired_growth'], 1)
put('VImpReadmit', str(V3['imputation']['4']['n_readmitted'])); put('VImpNoPrice', str(V3['imputation']['4']['n_readmitted_without_price']))

# ---- descriptive statistics of the v3 sample (definitions as in code/paper_stats.py)
c3 = pd.read_csv(v3path('data', 'panel_v3.csv'))
assert len(c3) == S3['E1']['n']
for m_, tag in [('op', 'Op'), ('fcf_sbc', 'Cash'), ('adj', 'Adj'), ('fcf', 'Fcf')]:
    num('VPass' + tag, (c3[f'R_{m_}'] >= 0.4).sum() / c3[f'R_{m_}'].notna().sum(), 1)
num('VUsShare', c3['loc'].fillna('').str.fullmatch(r'[A-Z]{2}').mean())
num('VAcqShare', c3.acq_flag_v3.mean()); num('VAcqShareFast', c3.loc[c3.g > 0.5, 'acq_flag_v3'].mean())
num('VDiscShare', c3.disc_flag.mean()); num('VCapexMissing', c3.capex_missing.mean(), 1)
assert int(c3.acq_flag_v3.sum()) == RT['n_flagged']
cw3 = c3[c3.name.str.contains('CoreWeave', na=False) & (c3.year == 2025)].iloc[0]
num('VCwGrowth', cw3.g); num('VCwOp', cw3.R_op); num('VCwFcfMargin', cw3.m_fcf_sbc); num('VCwCash', cw3.R_fcf_sbc)
for per, nm in [('2010-15', 'Early'), ('2023-25', 'Late')]:
    x = c3[c3.period == per]
    for m_, tag in [('op', 'Op'), ('fcf_sbc', 'Cash')]:
        num(f'VMed{tag}{nm}', x[f'R_{m_}'].median(), 1)
        num(f'VPass{tag}{nm}', (x[f'R_{m_}'] >= 0.4).sum() / x[f'R_{m_}'].notna().sum(), 1)
x = c3[c3.period == '2023-25']                                            # the bridge between bases, 2023-25
for m_, tag in [('op', 'Op'), ('adj', 'Adj'), ('fcf', 'Fcf'), ('fcf_sbc', 'Cash')]:
    num('VBridgeMed' + tag, x[f'R_{m_}'].median(), 1)
    num('VBridgePass' + tag, (x[f'R_{m_}'] >= 0.4).sum() / x[f'R_{m_}'].notna().sum(), 1)
num('VBridgeSbc', (x.sbc / x.rev).median(), 1)
_orig = [c3[f'orig_{c}'].mean() for c in ('op', 'ocf', 'capex', 'sbc')]    # share taken from the original filing
num('VOrigLo', min(_orig), 1); num('VOrigHi', max(_orig), 1)
num('VSmShare', c3.sm.notna().mean())                                  # selling and marketing reported separately
num('AppRestated', -STATS['applovin']['restated_vs_original']); num('AppGrowth', STATS['applovin']['g2023_as_first_reported'])

# ---- bootstrap design
put('BootB', str(V3['meta']['replications'])); put('BootFirms', str(V3['meta']['firms_in_bootstrap_universe']))
put('BootSeedZero', str(V3['meta']['seed0'])); num('BootNanMax', V3['meta']['nan_max'])
put('BootMinCell', str(V3['meta']['min_cell']))
assert V3['meta']['seed_rule'] == 'SEED0 + crc32(block name) mod 1e6'
put('BootSeeds', ', '.join(f"{k} {v}" for k, v in V3['meta']['seeds'].items()))
assert sum(V3['meta']['errors_in_draws'].values()) == 0

# ---- primary slope: Psi_0.90 over growth of 0 to 60% (D-2), all four views (D-3)
for b, B_ in [('op', 'Op'), ('cash', 'Cash')]:
    st = f'cone_{b}_slope_c90_w60'
    assert abs(FS3['central'][b]['E1']['est'] - vest(st)) < 1e-12
    for e, tag in FOUR:
        est_se(f'Psi{B_}{tag}', st, e)
    ival(f'Psi{B_}Eone', st, 'E1', 2, False)
    put(f'Psi{B_}CountNeg', WORD[count_four(st, lambda c: c[1] < 0)])
    put(f'Psi{B_}SignNeg', WORD[sum(vest(st, e) < 0 for e, _ in FOUR)])
    put(f'Psi{B_}CountAbove', WORD[count_four(st, lambda c: c[0] > -1)])
    grid_e1 = [vest(f'cone_{b}_slope_c{c}_w{w}') for c in (80, 85, 90, 95) for w in (40, 60)]
    grid_all = [vest(f'cone_{b}_slope_c{c}_w{w}', e) for c in (80, 85, 90, 95) for w in (40, 60) for e, _ in FOUR]
    num(f'PsiGrid{B_}Lo', min(grid_e1), 2, False); num(f'PsiGrid{B_}Hi', max(grid_e1), 2, False)
    num(f'PsiGridAll{B_}Lo', min(grid_all), 2, False); num(f'PsiGridAll{B_}Hi', max(grid_all), 2, False)
    est_se(f'OrderM{B_}', f'cone_{b}_slope_orderm25_w60')
    est_se(f'PsiForty{B_}', f'cone_{b}_slope_c90_w40')
    # the local conditional quantile (descriptive), tau = 0.90, growth 0 to 60%
    for e, tag in FOUR:
        est_se(f'Loc{B_}{tag}', f'slope_{b}_pooled', e)
    # periods (window 0 to 40%: the 60% cells fall below the minimum within periods)
    est_se(f'PsiEarly{B_}', f'cone_{b}_slope_c90_w40_2010_19')
    est_se(f'PsiLate{B_}', f'cone_{b}_slope_c90_w40_2020_25')
    for e, tag in FOUR:
        est_se(f'PsiDiff{B_}{tag}', f'cone_{b}_slope_c90_w40_2020_25_minus_2010_19', e)
    ival(f'PsiDiff{B_}Eone', f'cone_{b}_slope_c90_w40_2020_25_minus_2010_19', 'E1', 2, False)
    put(f'PsiDiff{B_}SignNeg', WORD[sum(vest(f'cone_{b}_slope_c90_w40_2020_25_minus_2010_19', e) < 0 for e, _ in FOUR)])
    put(f'PsiDiff{B_}CountNeg', WORD[count_four(f'cone_{b}_slope_c90_w40_2020_25_minus_2010_19', lambda c: c[1] < 0)])
    est_se(f'LocDiff{B_}', f'slope_{b}_2020_25_minus_2010_19')
ival('PsiDiffOpEtwo', 'cone_op_slope_c90_w40_2020_25_minus_2010_19', 'E2', 2, False)
put('PsiCellsSixtyEone', str(V3['cone_cells']['E1']['op']['0.60'])); put('PsiCellsEightyEone', str(V3['cone_cells']['E1']['op']['0.80']))

# ---- familywise results
FB = {c['key']: c for c in V3['families']['headline14B']['contrasts']}
ADJ = ('holm_normal', 'holm_percentile', 'holm_basic')


def holm_range(prefix, key, nd=2):
    vals = [FB[key][t] for t in ADJ]
    num(prefix + 'Lo', min(vals), nd, False); num(prefix + 'Hi', max(vals), nd, False)
    num(prefix + 'RW', FB[key]['romano_wolf'], nd, False)


holm_range('HolmPsiOpZero', 'psi_op_E1_vs_0'); holm_range('HolmPsiCashZero', 'psi_cash_E1_vs_0')
holm_range('HolmPsiDiff', 'psi_op_E1_2020_25_minus_2010_19', 3)
holm_range('HolmTop', 'p95chg_op_E1', 3); holm_range('HolmCap', 'capint_cash_E1', 3)
holm_range('HolmSize', 'size_cash_E1')
put('FamBN', str(V3['families']['headline14B']['n']))
SB5 = V3['families']['headline14B']['survivors_5pct']
SB10 = V3['families']['headline14B']['survivors_10pct']
put('HolmDiffFive', WORD[sum('psi_op_E1_2020_25_minus_2010_19' in SB5[t] for t in SB5)])
F38 = V3['families']['table38']
put('ContrN', str(F38['n'])); put('ContrNEst', str(F38['n_estimable']))
ex = F38['intervals_excluding_h0']
put('ContrExclPct', str(ex['90_percentile'])); put('ContrExclBasic', str(ex['90_basic'])); put('ContrExclNormal', str(ex['90_normal']))
num('ContrExpected', 0.10 * F38['n_estimable'], 1, False)
# B13 (E2-3): the E2 primary slope with the sample's 30-firm-year rule applied inside draws (defined draws only); the
# cone block now records the 60% cell size of every draw (cone_<basis>_cell60)
import numpy as _np13
_Z13 = _np13.load(v3path('notes', 'bootstrap_draws_v3.npz'), allow_pickle=True)
_st13, _va13 = [str(x) for x in _Z13['cone__statistics']], [str(x) for x in _Z13['cone__variants']]
for b, B_ in [('op', 'Op'), ('cash', 'Cash')]:
    _d = _Z13['cone'][:, _va13.index('E2'), _st13.index(f'cone_{b}_slope_c90_w60')]
    _n = _Z13['cone'][:, _va13.index('E2'), _st13.index(f'cone_{b}_cell60')]
    _ok = _np13.isfinite(_d) & (_n >= 30)
    num(f'DefDraw{B_}Share', float((_n < 30).mean()), 1)
    sgn(f'DefDraw{B_}Lo', float(_np13.quantile(_d[_ok], .05)), 3, False); sgn(f'DefDraw{B_}Hi', float(_np13.quantile(_d[_ok], .95)), 3, False)
    put(f'DefDraw{B_}Cell', str(int(vest(f'cone_{b}_cell60', 'E2'))))
# D1: the cash score before net interest (bridge rows cash_bni and its like-for-like basis cash_bnis)
for k_, nm_ in [('bnis', 'Bnis'), ('bni', 'Bni')]:
    sgn(f'BridgeChange{nm_}', vest(f'bridge_cash_{k_}_p95_change')); ival(f'BridgeChange{nm_}', f'bridge_cash_{k_}_p95_change')
    num(f'BridgeLate{nm_}', vest(f'bridge_cash_{k_}_p95_2023_25'), 1)
put('BridgeNBni', str(int(vest('bridge_cash_bni_n_2016_19')) + int(vest('bridge_cash_bni_n_2023_25'))))            # B13: 10% of the 36 estimable contrasts (was 38)
num('ContrSpendHolm', [c for c in F38['contrasts'] if c['key'] == 'spend_ratio'][0]['holm_percentile'], 3, False)

# ---- growth technology: the bounds on alpha (X - k) that each method gives (D-1)
for e, tag in FOUR:
    est_se('Spend' + tag, 'spend_ratio', e)
num('SpendLo', min(vest('spend_ratio', e) for e, _ in FOUR), 1, False)
num('SpendHi', max(vest('spend_ratio', e) for e, _ in FOUR), 1, False)
num('SpendQlo', vest('spend_q25'), 1, False); num('SpendQhi', vest('spend_q75'), 1, False)
num('SpendPenaltyTen', 0.10 * (vest('spend_ratio') - 1), 0, pct=True)   # Discussion: score shortfall at 10 points of excess growth
num('AnchorPiLoAbs', -CAL['anchor']['Pi_ub'][0])                           # lower-quartile upper-bound surplus, sign dropped
put('SpendN', str(int(vest('spend_n')))); num('SpendSM', vest('spend_med_sm')); num('SpendExcess', vest('spend_med_excess'), 1)
METHODS = dict(AlphaTercLow='spend_terc1_ratio', AlphaTercMid='spend_terc2_ratio', AlphaTercHigh='spend_terc3_ratio',
               AlphaFloorTen='spend_floor10_ratio', AlphaFloorTwenty='spend_floor20_ratio', AlphaNet='spend_maint_ratio',
               AlphaOlsAbove='foc_ols_ye_above', AlphaMedAbove='foc_medreg_above_slope', AlphaOlsAll='foc_ols_ye_all',
               AlphaFeAll='foc_fe_all', AlphaMedExcess='foc_medreg_excess_slope',
               AlphaGFive='spend_G05_ratio', AlphaGEight='spend_G08_ratio', AlphaGTwelve='spend_G12_ratio')
for nm, st in METHODS.items():
    num(nm, vest(st), 2 if vest(st) < 1 else 1, False)
num('AlphaNetEtwo', vest('spend_maint_ratio', 'E2'), 2, False)
_lev = [vest(METHODS[k]) for k in ('AlphaOlsAbove', 'AlphaMedAbove', 'AlphaOlsAll', 'AlphaFeAll', 'AlphaMedExcess')]
num('AlphaLevelLo', min(_lev), 2, False); num('AlphaLevelHi', max(_lev), 2, False)
_all = [vest(st) for st in METHODS.values()] + [vest('spend_ratio')]
num('AlphaAllLo', min(_all), 2, False); num('AlphaAllHi', max(_all), 1, False)
num('XkLo', min(_all) / 0.45, 1, False); num('XkHi', max(_all) / 0.25, 0, False)   # alpha in [0.25, 0.45]

# ---- scale
for e, tag in FOUR:
    est_se('ScaleCash' + tag, 'scale_tenfold_cash', e, 1, True, signed=True)
    est_se('ScaleCashFe' + tag, 'scale_tenfold_fe_cash', e, 1, True, signed=True)
est_se('ScaleOpEone', 'scale_tenfold_op', 'E1', 1, True, signed=True)
put('ScaleCount', WORD[count_four('scale_tenfold_cash', lambda c: c[1] < 0)])
put('ScaleFeCount', WORD[count_four('scale_tenfold_fe_cash', lambda c: c[1] < 0)])
for cls, nm in [('0_1to0_5B', 'A'), ('0_5to2B', 'B'), ('2to10B', 'C'), ('over10B', 'D')]:
    num('ScaleClass' + nm, vest(f'scale_p95_cash_{cls}'), 1)

# ---- capital intensity (an accounting effect)
for st, nm in [('capint_gap_cash_2023_25', 'CapCash'), ('capint_gap_cash_2023_25_prior', 'CapPrior'),
               ('capint_gap_cash_2023_25_firmmed', 'CapFirmMed'), ('capint_gap_cashadd_2023_25', 'CapAdd'),
               ('capint_gap_op_2023_25', 'CapOp'), ('capint_gap_cash_2016_19', 'CapCashEarly'),
               ('capint_gap_cashadd_2016_19', 'CapAddEarly')]:
    sgn(nm + 'Eone', vest(st)); ival(nm + 'Eone', st)
    sgn(nm + 'Etwo', vest(st, 'E2'))
num('CapHiHalf', vest('capint_hi_cash_2023_25')); num('CapLoHalf', vest('capint_lo_cash_2023_25'))
put('CapCashCount', WORD[count_four('capint_gap_cash_2023_25', lambda c: c[1] < 0)])
put('CapAddCount', WORD[count_four('capint_gap_cashadd_2023_25', lambda c: c[1] < 0)])
put('CapFirmMedCount', WORD[count_four('capint_gap_cash_2023_25_firmmed', lambda c: c[1] < 0)])
est_se('CapInter', 'capint_interaction_cash_pooled', 'E1', 2, False, signed=True)
put('CapInterSign', WORD[sum(vest('capint_interaction_cash_pooled', e) < 0 for e, _ in FOUR)])

# ---- the top of the distribution and its composition
for b, B_ in [('op', 'Op'), ('cash', 'Cash')]:
    num(f'TopEarly{B_}', vest(f'p95_{b}_2016_19'), 1); num(f'TopLate{B_}', vest(f'p95_{b}_2023_25'), 1)
    for e, tag in FOUR:
        num(f'TopFall{B_}{tag}', -vest(f'p95_change_{b}', e), 1)
    lo, hi = vci(f'p95_change_{b}')
    num(f'TopFall{B_}EoneLo', -hi, 1); num(f'TopFall{B_}EoneHi', -lo, 1)
    sgn(f'TopTwentyFive{B_}', vest(f'p95_change_{b}_2016_19_to_2025')); ival(f'TopTwentyFive{B_}', f'p95_change_{b}_2016_19_to_2025')
    sgn(f'TopTwentyFour{B_}', vest(f'p95_change_{b}_2016_19_to_2023_24')); ival(f'TopTwentyFour{B_}', f'p95_change_{b}_2016_19_to_2023_24')
    for part in ('within_A', 'composition_A', 'composition_B', 'within_B', 'within_size'):
        nm = ''.join(w.capitalize() for w in part.split('_'))
        sgn(f'Rw{B_}{nm}', vest(f'rw_{b}_{part}')); ival(f'Rw{B_}{nm}', f'rw_{b}_{part}')
num('TopYearMinOp', vest('p95_op_2024'), 1); num('TopYearLastOp', vest('p95_op_2025'), 1)
_vars = [k for k in V3E['p95_change_op'] if k not in ('E1_minus_E2', 'E1all')]
_falls = [-vest(f'p95_change_{b}', v_) for b in ('op', 'cash') for v_ in _vars]
num('TopFallAllLo', min(_falls)); num('TopFallAllHi', max(_falls))
put('TopCount', WORD[count_four('p95_change_op', lambda c: c[1] < 0)])
put('TopCountCash', WORD[count_four('p95_change_cash', lambda c: c[1] < 0)])
est_se('SlopeYearFeOp', 'slope_yearfe_op')
TC = V3['T_cells']
put('TwentyCellEarly', str(TC['E1']['T_op_g20_change'][0])); put('TwentyCellLate', str(TC['E1']['T_op_g20_change'][1]))
put('FortyCellEarly', str(TC['E1']['T_op_g40_change'][0])); put('FortyCellLate', str(TC['E1']['T_op_g40_change'][1]))
put('FortyCellLateEtwo', str(TC['E2']['T_op_g40_change'][1]))
num('FortyNanEone', V3E['T_op_g40_change']['E1']['nan_share'], 1); num('FortyNanEtwo', V3E['T_op_g40_change']['E2']['nan_share'])
num('FortyNanImpFour', V3E['T_op_g40_change']['E2imp4']['nan_share'])
for st, nm in [('T_op_g00_change', 'TzeroOp'), ('T_op_g20_change', 'TtwentyOp'), ('T_cash_g00_change', 'TzeroCash'),
               ('T_cash_g20_change', 'TtwentyCash')]:
    sgn(nm, vest(st)); ival(nm, st)

# ---- round 2, A4 (IM2-N2) and A5 (IM2-N3): robustness of the composition decomposition to binning, the shift of every
# quantile, first-year firm-years, and the 2025 recovery without acquisition-affected firm-years (point estimates on the
# E1 frame, data/panel_v3.csv; estimators as in estimate_v3.py f_reweight, type-7 quantiles)
import numpy as _np


def _wq7(x, w, p):
    k = w > 0
    x, w = x[k], w[k]
    o = _np.argsort(x, kind='stable')
    x, w = x[o], w[o]
    c = (_np.cumsum(w) - w) / (w.sum() - w[-1])
    return float(_np.interp(p, c, x))


def _decomp(y_col, nb):
    a_, c_ = c3[(c3.period == '2016-19') & c3[y_col].notna()], c3[(c3.period == '2023-25') & c3[y_col].notna()]
    ga, gc, ya, yc = a_.g.values, c_.g.values, a_[y_col].values, c_[y_col].values
    e = _np.unique(_np.quantile(_np.r_[ga, gc], _np.linspace(0, 1, nb + 1)))
    e[0], e[-1] = e[0] - 1, e[-1] + 1
    n_ = len(e) - 1
    bins = lambda x: _np.clip(_np.searchsorted(e, x, 'left') - 1, 0, n_ - 1)
    ba, bc = bins(ga), bins(gc)
    fa, fc = _np.bincount(ba, minlength=n_) / len(ba), _np.bincount(bc, minlength=n_) / len(bc)
    w_ = lambda f1, f2, bb: _np.where(f2[bb] > 0, f1[bb] / _np.where(f2[bb] > 0, f2[bb], 1), 0.0)
    oa, oc = _wq7(ya, _np.ones(len(ya)), .95), _wq7(yc, _np.ones(len(yc)), .95)
    cfc, cfa = _wq7(yc, w_(fa, fc, bc), .95), _wq7(ya, w_(fc, fa, ba), .95)
    return dict(comp_A=oc - cfc, within_A=cfc - oa, comp_B=cfa - oa, within_B=oc - cfa)


for col, B_ in [('R_op', 'Op'), ('R_fcf_sbc', 'Cash')]:
    dd = [_decomp(col, nb) for nb in range(4, 41)]
    comp = [x[k] for x in dd for k in ('comp_A', 'comp_B')]
    within = [x[k] for x in dd for k in ('within_A', 'within_B')]
    sgn(f'BinComp{B_}Lo', min(comp)); sgn(f'BinComp{B_}Hi', max(comp))
    sgn(f'BinWithin{B_}Lo', min(within)); sgn(f'BinWithin{B_}Hi', max(within))
for col, B_ in [('R_op', 'Op'), ('R_fcf_sbc', 'Cash'), ('R_fcf', 'Fcf')]:
    a_, c_ = c3.loc[c3.period == '2016-19', col].dropna(), c3.loc[c3.period == '2023-25', col].dropna()
    for qq, qn in [(.10, 'Ten'), (.25, 'TwentyFive'), (.50, 'Fifty'), (.75, 'SeventyFive'), (.90, 'Ninety'), (.95, 'NinetyFive')]:
        sgn(f'QShift{B_}{qn}', float(c_.quantile(qq) - a_.quantile(qq)))
_first = c3.groupby('cik').year.transform('min') == c3.year
for per, nm in [('2016-19', 'SixteenNineteen'), ('2020-22', 'TwentyTwentyTwo'), ('2023-25', 'TwentyThreeTwentyFive')]:
    put('FirstYear' + nm, str(int((_first & (c3.period == per)).sum())))
_p95y = lambda yr, x: float(x.loc[(x.year == yr), 'R_op'].dropna().quantile(.95))
_rec_all = _p95y(2025, c3) - _p95y(2024, c3)
_nx = c3[c3.acq_flag_v3 == 0]
_rec_nx = _p95y(2025, _nx) - _p95y(2024, _nx)
assert abs(_p95y(2025, c3) - vest('p95_op_2025')) < 1e-9 and abs(_p95y(2024, c3) - vest('p95_op_2024')) < 1e-9
sgn('RecoveryYoyEone', _rec_all); sgn('RecoveryYoyNoAcq', _rec_nx)                 # 2025 against 2024
_p95s = lambda yrs, x: float(x.loc[x.year.isin(yrs), 'R_op'].dropna().quantile(.95))
_r_all = _p95s([2025], c3) - _p95s([2023, 2024], c3)                                   # 2025 against 2023-24 pooled
assert abs(_r_all - (vest('p95_change_op_2016_19_to_2025') - vest('p95_change_op_2016_19_to_2023_24'))) < 1e-9
sgn('RecoveryEone', _r_all); sgn('RecoveryNoAcq', _p95s([2025], _nx) - _p95s([2023, 2024], _nx))
num('TopYearMinOpNoAcq', _p95y(2024, _nx), 1); num('TopYearLastOpNoAcq', _p95y(2025, _nx), 1)

# ---- the distance to the frontier: stochastic frontier and gap decomposition
for st, nm in [('sfa_op_2016_19_mean_shortfall', 'SfaEarly'), ('sfa_op_2023_25_mean_shortfall', 'SfaLate')]:
    num(nm, vest(st), 1)
for st, nm in [('sfa_op_2023_25_cohort_gap', 'SfaCohortOp'), ('sfa_cash_2023_25_cohort_gap', 'SfaCohortCash'),
               ('sfa_op_balanced_change', 'SfaBalanced'), ('sfa_op_entrants_minus_balanced_2023_25', 'SfaEntrants')]:
    sgn(nm, vest(st)); ival(nm, st)
put('SfaCohortCount', WORD[count_four('sfa_op_2023_25_cohort_gap', lambda c: c[0] > 0)])
SV = V3['sfa_detail']['E1|survivorship']
put('SfaPreFirms', str(SV['pre2019_firms_in_2016_19'])); put('SfaStill', str(SV['still_in_2023_25']))
num('SfaSurvMargin', SV['op_2016_19_median_margin_survivors'], 1); num('SfaLeaveMargin', SV['op_2016_19_median_margin_leavers'], 1)
for st, nm in [('gap_avg', 'GapV'), ('gap_sm', 'GapVSM'), ('gap_rd', 'GapVRD'), ('gap_gm', 'GapVGM'), ('gap_ga', 'GapVGA'),
               ('gap_slow', 'GapVSlow'), ('gap_slow_gm', 'GapVSlowGM'), ('gap_fast', 'GapVFast'),
               ('gap_fast_sm', 'GapVFastSM'), ('gap_fast_rd', 'GapVFastRD')]:
    num(nm, vest(st), 1); ival(nm, st)
num('GapVEtwo', vest('gap_avg', 'E2'), 1)
put('GapGMCount', WORD[count_four('gap_gm', lambda c: c[0] > 0)])

# ---- within-firm slopes with the model's timing
W3 = V3['within']
for key, nm in [('E1|op', 'Op'), ('E1|cash', 'Cash')]:
    for spec, sn in [('contemporaneous', 'Now'), ('lead_reported', 'Lead')]:
        sgn(f'Wf{nm}{sn}', W3[key][spec]['b'], 2, False); num(f'Wf{nm}{sn}Se', W3[key][spec]['se'], 2, False)
for key, nm in [('E2|op', 'Op'), ('E2|cash', 'Cash')]:
    sgn(f'WfEtwo{nm}Lead', W3[key]['lead_same_estimand']['b'], 2, False)
    num(f'WfEtwo{nm}LeadSe', W3[key]['lead_same_estimand']['se'], 2, False)

# ---- calibration anchor (v3): intervals; only Pi_lb > 0 is a conclusion
for e, tag in FOUR:
    put('AncN' + tag, str(int(vest('anchor_p95_n', e)))); put('AncFirms' + tag, str(int(vest('anchor_p95_firms', e))))
    sgn('AncPiUb' + tag, vest('anchor_p95_Pi_ub_med', e)); ival('AncPiUb' + tag, 'anchor_p95_Pi_ub_med', e)
    sgn('AncPiLb' + tag, vest('anchor_p95_Pi_lb_med', e)); ival('AncPiLb' + tag, 'anchor_p95_Pi_lb_med', e)
    sgn('AncPiNet' + tag, vest('anchor_p95_Pi_net_med', e)); ival('AncPiNet' + tag, 'anchor_p95_Pi_net_med', e)   # FA-m13: netted (central)
    sgn('AncTrUb' + tag, vest('anchor_p95_transient_ub', e), 0); sgn('AncTrLb' + tag, vest('anchor_p95_transient_lb', e), 0)
ival('AncTrUbEone', 'anchor_p95_transient_ub', 'E1', 0); ival('AncTrLbEone', 'anchor_p95_transient_lb', 'E1', 0)
_tr = [vest(f'anchor_p95_transient_{s}', e) for s in ('ub', 'lb') for e, _ in FOUR]
sgn('AncTrAllLo', min(_tr), 0); sgn('AncTrAllHi', max(_tr), 0)
LO = V3['anchor']['leave_one_firm_out_median_Pi_ub']['E1']
sgn('AncLooLo', min(LO.values())); sgn('AncLooHi', max(LO.values()))

# ---- the E2 construction before the two post-test-run rules (protocol record)
for st, nm in [('slope_op_pooled', 'LocOp'), ('slope_cash_pooled', 'LocCash'), ('cone_op_slope_c90_w60', 'PsiOp'),
               ('cone_cash_slope_c90_w60', 'PsiCash')]:
    num(f'Test{nm}', vest(st, 'E2testrule'), 3, False); num(f'TestRef{nm}', vest(st, 'E2'), 3, False)
    num(f'TestvTwo{nm}', V2X['estimates'][st]['E2testrule']['est'], 3, False)
    num(f'TestvTwoRef{nm}', V2X['estimates'][st]['E2']['est'], 3, False)

# ---- what was known when the primary sample was switched (29 Oct, 11:19; notes/estimand_notes.md section 1, v2 sample)
OE = ORG['estimates']
for st, nm, nd, pct in [('slope_op_pooled', 'SlopeOp', 2, False), ('slope_cash_pooled', 'SlopeCash', 2, False),
                        ('p95_change_op', 'TopOp', 1, True), ('p95_change_cash', 'TopCash', 1, True)]:
    num('Known' + nm + 'Excl', OE[st]['E2x25']['est'], nd, pct); num('Known' + nm + 'Eone', OE[st]['E1']['est'], nd, pct)

# ---- qualitative statements of sections/data.tex, empirics.tex, appendix_data.tex and appendix_protocol.tex (CLAIMS)
# Each entry is (sentence it supports, test on the estimates). A refreshed run of estimate_v3.py or build_panel_v3.py that
# no longer supports a sentence stops this script and names the sentence, so the text is revised before it is rebuilt.
# Set P1_CLAIMS_WARN_ONLY=1 to print the failures without stopping (for builds of other papers in the meantime).
put('AncPiLbCount', WORD[count_four('anchor_p95_Pi_lb_med', lambda c: c[0] > 0)])
put('AncPiNetCount', WORD[count_four('anchor_p95_Pi_net_med', lambda c: c[0] > 0)])
put('AncPiUbCount', WORD[count_four('anchor_p95_Pi_ub_med', lambda c: c[0] < 0 < c[1])])
_cb = V3B['cash_score_basis']
# B5 bridge (notes/empirics_v3.json, bridge_* keys; Table tab:bridge_v3): the cash score before interest paid and cash
# taxes (pre) and before interest only (bi), against the paper's cash score on the same firm-years (bs). Interest and taxes
# come from SEC frames (latest filed, not first reported).
BRIDGE_DONE = 'bridge_cash_pre_p95_change' in V3E
assert BRIDGE_DONE, 'notes/empirics_v3.json has no bridge_* keys'
_bl = {per: vest(f'bridge_cash_pre_p95_{per}') - vest(f'bridge_cash_bs_p95_{per}') for per in ('2016_19', '2023_25')}
num('BridgeLiftLo', min(_bl.values()), 1); num('BridgeLiftHi', max(_bl.values()), 1)
_bi = {per: abs(vest(f'bridge_cash_bi_p95_{per}') - vest(f'bridge_cash_bs_p95_{per}')) for per in ('2016_19', '2023_25')}
num('BridgeIntMax', max(_bi.values()), 1)
for k_, nm_ in [('bs', 'Bs'), ('pre', 'Pre'), ('bi', 'Bi')]:
    sgn(f'BridgeChange{nm_}', vest(f'bridge_cash_{k_}_p95_change')); ival(f'BridgeChange{nm_}', f'bridge_cash_{k_}_p95_change')
num('BridgePreMedLate', vest('bridge_cash_pre_med_2023_25'), 1); num('BridgeBsMedLate', vest('bridge_cash_bs_med_2023_25'), 1)
put('BridgeN', str(int(vest('bridge_cash_bs_n_2016_19')) + int(vest('bridge_cash_bs_n_2023_25'))))
_cov = re.match(r'(\d+) of (\d+)', _cb['coverage_core'])
put('BridgeCov', *thousands(int(_cov.group(1)))); put('BridgeCovOf', thousands(int(_cov.group(2)))[0], thousands(int(_cov.group(2)))[1])
_R = V3B['rules']
FB10 = V3['families']['headline14B']['survivors_10pct']
# B13: the anchor's conclusion (Pi_lb median > 0, E1) added to family B; raw bootstrap p-values from
# notes/calibration_anchor_v3.json, Holm over the 15 tests by interval type
_ab = json.load(open(v3path('notes', 'calibration_anchor_v3.json')))['bootstrap']['E1']['Pi_lb_med']


def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for r, i in enumerate(o):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        adj[i] = run
    return adj


HOLM_ANCHOR = {}
for t in ('normal', 'percentile', 'basic'):
    ps = [c['p_' + t] for c in V3['families']['headline14B']['contrasts'] if c.get('p_' + t) is not None] + [_ab['p_' + t]]
    HOLM_ANCHOR['holm_' + t] = holm(ps)[-1]
    num('HolmAnchor' + t.capitalize(), HOLM_ANCHOR['holm_' + t], 3, False)
    ps15 = [(c['p_' + t] if c.get('p_' + t) is not None else 1.0) for c in V3['families']['headline14B']['contrasts']] + [_ab['p_' + t]]
    num('HolmAnchorFifteen' + t.capitalize(), holm(ps15)[-1], 3, False)     # counting the non-estimable test (p = 1)
put('FamBNPlus', str(V3['families']['headline14B']['n_estimable'] + 1))
# B13: within-firm lead regressions in all four views (bounds), and the expected count of false exclusions
for key, nm in [('E2imp4|op', 'ImpFourOp'), ('E2imp4|cash', 'ImpFourCash'), ('E2imp8|op', 'ImpEightOp'), ('E2imp8|cash', 'ImpEightCash'),
                ('E2|op', 'EtwoOp'), ('E2|cash', 'EtwoCash')]:
    sgn(f'Wf{nm}LeadRep', W3[key]['lead_reported']['b'], 2, False); num(f'Wf{nm}LeadRepSe', W3[key]['lead_reported']['se'], 2, False)
    if nm.startswith('Imp'):
        sgn(f'Wf{nm}LeadSame', W3[key]['lead_same_estimand']['b'], 2, False)


TYPES4 = ('ci90', 'ci90_basic', 'ci90_normal', 'ci90_bc')         # percentile, basic, normal, bias-corrected (A2)


def types_pass(stat, test, e='E1'):
    """number of the four 90% interval types of one view that pass a test (A2: claims cover every interval type)"""
    r = vrec(stat, e)
    return sum(bool(test(r[t])) for t in TYPES4 if r.get(t))


def in_all(sets, key):
    return all(key in v for v in sets.values())


def in_none(sets, key):
    return not any(key in v for v in sets.values())


CLAIMS = [
    # data.tex, sample rules and the bridge (status of notes/panel_v3_build.json as estimated)
    ('data, appendix and discussion: R2 is a sensitivity on the named firms only, not applied to the main sample',
     _R['R2'].startswith('main sample: not applied') and 'named firms' in _R['R2']),
    ('data: the R2 classifier classes exactly Activision, Bally, EA and PLAYSTUDIOS non-software and misses THQ, Take-Two, '
     'Roblox, CoreWeave and Unity', sorted(V3B['R2_named']['non_software']) == sorted(['Activision Blizzard, Inc.',
     'BALLY TECHNOLOGIES, INC.', 'ELECTRONIC ARTS INC.', 'PLAYSTUDIOS, Inc.'])
     and all(V3B['R2_named']['classes'][f] == 'software' for f in ('THQ INC', 'TAKE TWO INTERACTIVE SOFTWARE INC',
                                                                  'Roblox Corp', 'CoreWeave, Inc.', 'Unity Software Inc.'))),
    ('data and discussion: R5 is a flag and sensitivity, not an exclusion; foreign filers not tested',
     _R['R5'].startswith('applied (flag and sensitivity') and 'foreign_not_tested' in V3B['R5']['status_counts_v3']),
    ('data: the R5 flag names Meditech, SunGard, Infor and Epicor among its firms',
     all(f in V3B['R5']['no_listed_equity_v3'] for f in ('Medical Information Technology, Inc.', 'SunGard', 'Infor, Inc.',
                                                         'Epicor Software Corp'))),
    ('data: R3 applied with XBRL and filing text; no XBRL firm-year reaches the threshold; the largest share is SINA 2015',
     _R['R3'].startswith('applied (XBRL') and V3B['R3']['xbrl']['n_at_or_above_50pct'] == 0
     and V3B['R3']['xbrl']['top'][0].startswith('SINA CORP 2015')),
    ('data: R4 applied with criteria a, b and c; (c) adds no core flag', _R['R4'] == 'applied (criteria a, b and c)'
     and V3B['R4']['acquiree_revenue']['new_flags_core_v2'] == []),
    ('data: R3 excludes one firm-year (Exzeo 2025)', V3B['R3']['firm_years'] == ['Exzeo Group, Inc. 2025']),
    ('data: adding back interest and cash taxes lifts P95 by roughly 5 points in both periods and leaves the decline in place '
     '(change within one point of the like-for-like change, interval below zero)',
     all(3 <= 100 * v <= 7 for v in _bl.values()) and abs(vest('bridge_cash_pre_p95_change') - vest('bridge_cash_bs_p95_change')) < 0.01
     and types_pass('bridge_cash_pre_p95_change', lambda c: c[1] < 0) == 4),
    ('data: interest alone moves P95 by less than one point', max(_bi.values()) < 0.01),
    ('data: CoreWeave 2025 GAAP operating margin of about zero', abs(cw3.m_op) < 0.01),
    ('empirics: period slopes on the 0-60% window are not defined under E2 (cells too thin)',
     V3E['cone_op_slope_c90_w60_2020_25_minus_2010_19']['E2'].get('est') is None),
    ('empirics: the P95 and capital-intensity headline statistics do not survive Holm at 5%',
     in_none(SB5, 'p95chg_op_E1') and in_none(SB5, 'capint_cash_E1')),
    # empirics.tex
    ('empirics: the P95 decline holds in every variant', min(_falls) > 0),
    ('empirics (A2): the GAAP P95 decline survives Holm at 10% under the normal and percentile intervals and Romano-Wolf '
     'but not the basic interval (Holm p 0.054 to 0.208), and at 5% under none',
     all(FB['p95chg_op_E1'][t] < 0.10 for t in ('holm_normal', 'holm_percentile', 'romano_wolf'))
     and FB['p95chg_op_E1']['holm_basic'] > 0.10 and in_none(SB5, 'p95chg_op_E1')),
    ('empirics (editor text): the GAAP decline is "significant at 10% after familywise correction under most procedures": '
     'three of the four (Holm normal, Holm percentile, Romano-Wolf; not Holm basic), and its 90% interval excludes zero under '
     'all four interval types', sum(FB['p95chg_op_E1'][t] < 0.10 for t in ('holm_normal', 'holm_percentile', 'holm_basic',
                                                                         'romano_wolf')) == 3
     and types_pass('p95_change_op', lambda c: c[1] < 0) == 4),
    ('empirics (editor text): the cash decline is "not significant" after familywise correction: Holm (normal, percentile, '
     'basic) and Romano-Wolf all above 10%, although each of its four 90% intervals excludes zero before correction',
     all(FB['p95chg_cash_E1'][t] > 0.10 for t in ('holm_normal', 'holm_percentile', 'holm_basic', 'romano_wolf'))
     and types_pass('p95_change_cash', lambda c: c[1] < 0) == 4),
    ('empirics (A2): the cash P95 decline fails Holm at 10% under every interval type and Romano-Wolf',
     all(FB['p95chg_cash_E1'][t] > 0.10 for t in ('holm_normal', 'holm_percentile', 'holm_basic', 'romano_wolf'))),
    ('empirics: the P95 low year is 2024 and it recovered in 2025; the 2016-19 to 2025 interval includes zero',
     vest('p95_op_2024') == min(vest(f'p95_op_{y}') for y in range(2016, 2026)) and vest('p95_op_2025') > vest('p95_op_2024')
     and types_pass('p95_change_op_2016_19_to_2025', lambda c: c[0] < 0 < c[1]) == 4),
    ('empirics (A4): composition (B) excludes zero under three of the four interval types (not the basic) on both bases; '
     'within-bin (B) includes zero under all four; the size mix leaves the decline under all four',
     all(types_pass(f'rw_{b}_composition_B', lambda c: c[1] < 0) == 3 and vci(f'rw_{b}_composition_B', 'E1') is not None
         and vrec(f'rw_{b}_composition_B')['ci90_basic'][1] > 0
         and types_pass(f'rw_{b}_within_B', lambda c: c[0] < 0 < c[1]) == 4
         and types_pass(f'rw_{b}_within_size', lambda c: c[1] < 0) == 4 for b in ('op', 'cash'))),
    ('empirics (A1): T(0) GAAP includes zero under all four interval types; T(20%) GAAP excludes zero under the basic, '
     'normal and BC intervals but not the percentile interval',
     types_pass('T_op_g00_change', lambda c: c[0] < 0 < c[1]) == 4
     and types_pass('T_op_g20_change', lambda c: c[1] < 0) == 3 and vci('T_op_g20_change')[0] < 0 < vci('T_op_g20_change')[1]),
    ('empirics (A1): T(0) after SBC excludes zero under E1 with the percentile and basic intervals (not normal or BC) and in '
     'two of the four views (percentile)',
     types_pass('T_cash_g00_change', lambda c: c[1] < 0) == 2 and vci('T_cash_g00_change')[1] < 0
     and vrec('T_cash_g00_change')['ci90_basic'][1] < 0 and count_four('T_cash_g00_change', lambda c: c[1] < 0) == 2),
    ('empirics: T(40%) has no interval under E1 and no estimate under E2',
     not V3E['T_op_g40_change']['E1']['estimable'] and V3E['T_op_g40_change']['E2'].get('est') is None),
    ('empirics [FLAG: test against a slope of -1, not of a zero null]: Psi slope above -1 in all four views, both bases, '
     'and survives Holm at 5%',
     all(count_four(f'cone_{b}_slope_c90_w60', lambda c: c[0] > -1) == 4 for b in ('op', 'cash'))
     and in_all(SB5, 'psi_op_E1_vs_m1') and in_all(SB5, 'psi_cash_E1_vs_m1')),
    ('empirics: Psi slope negative does not survive Holm at 5% or 10%',
     all(in_none(S, k) for S in (SB5, FB10) for k in ('psi_op_E1_vs_0', 'psi_cash_E1_vs_0'))),
    ('empirics: grid slopes all negative', max(grid_all) < 0),
    ('empirics: the local quantile is steeper than Psi in every view',
     all(vest(f'slope_{b}_pooled', e) < vest(f'cone_{b}_slope_c90_w60', e) for b in ('op', 'cash') for e, _ in FOUR)),
    ('empirics (A3): GAAP steepening survives Holm at 10% under every procedure; its E1 interval excludes zero under all '
     'four types; it holds in three of four views (E2 includes zero)',
     in_all(FB10, 'psi_op_E1_2020_25_minus_2010_19')
     and types_pass('cone_op_slope_c90_w40_2020_25_minus_2010_19', lambda c: c[1] < 0) == 4
     and vci('cone_op_slope_c90_w40_2020_25_minus_2010_19', 'E2')[1] > 0
     and all(vci('cone_op_slope_c90_w40_2020_25_minus_2010_19', e)[1] < 0 for e in ('E1', 'E2imp4', 'E2imp8'))),
    ('empirics: no cash steepening (E1 interval includes zero under the percentile, normal and BC intervals, not the basic; '
     'positive in the other three views)',
     types_pass('cone_cash_slope_c90_w40_2020_25_minus_2010_19', lambda c: c[0] < 0 < c[1]) == 3
     and vrec('cone_cash_slope_c90_w40_2020_25_minus_2010_19')['ci90_basic'][1] < 0
     and all(vest('cone_cash_slope_c90_w40_2020_25_minus_2010_19', e) > 0 for e in ('E2', 'E2imp4', 'E2imp8'))),
    ('empirics: the spend ratio is within 3.0 to 3.5 in the four views',
     3.0 <= half_up(min(vest('spend_ratio', e) for e, _ in FOUR), 1) and half_up(max(vest('spend_ratio', e) for e, _ in FOUR), 1) <= 3.5),
    ('empirics: the size gradient interval includes zero in every view, with and without period effects',
     all(count_four(st, lambda c: c[0] < 0 < c[1]) == 4 for st in ('scale_tenfold_cash', 'scale_tenfold_fe_cash'))),
    ('empirics: the capital-intensity gap vanishes with capex added back and with the firm-median sort',
     count_four('capint_gap_cashadd_2023_25', lambda c: c[0] < 0 < c[1]) == 4
     and count_four('capint_gap_cash_2023_25_firmmed', lambda c: c[0] < 0 < c[1]) == 4
     and vci('capint_gap_op_2023_25')[0] < 0 < vci('capint_gap_op_2023_25')[1]),
    ('empirics: the growth-by-intensity interaction is negative in fewer than all four views',
     sum(vest('capint_interaction_cash_pooled', e) < 0 for e, _ in FOUR) < 4),
    ('empirics: balanced-panel SFA change includes zero under all four interval types',
     types_pass('sfa_op_balanced_change', lambda c: c[0] < 0 < c[1]) == 4),
    ('empirics: gross-margin part of the gap includes zero in every view under the percentile interval only; under E1 the '
     'basic, normal and BC intervals exclude zero',
     count_four('gap_gm', lambda c: c[0] < 0 < c[1]) == 4 and types_pass('gap_gm', lambda c: c[0] > 0) == 3),
    ('empirics [FLAG: tautological margin-gap tests; the top decile minus the middle is positive by construction]: the '
     'average gap and the fast-band S&M part survive Holm at 5%', in_all(SB5, 'gap_E1') and in_all(SB5, 'gap_fast_sm_E1')),
    ('empirics: anchor Pi_lb above zero and Pi_ub including zero in all four views, and under all four interval types in E1',
     count_four('anchor_p95_Pi_lb_med', lambda c: c[0] > 0) == 4 and count_four('anchor_p95_Pi_ub_med', lambda c: c[0] < 0 < c[1]) == 4
     and types_pass('anchor_p95_Pi_lb_med', lambda c: c[0] > 0) == 4
     and types_pass('anchor_p95_Pi_ub_med', lambda c: c[0] < 0 < c[1]) == 4),
    ('empirics (B13): the anchor test added to family B keeps Holm p below 10% under every type, below 5% only under '
     'normal and basic', all(HOLM_ANCHOR[t] < 0.10 for t in HOLM_ANCHOR) and HOLM_ANCHOR['holm_percentile'] > 0.05
     and HOLM_ANCHOR['holm_normal'] < 0.05 and HOLM_ANCHOR['holm_basic'] < 0.05),
    ('empirics: no E1-E2 contrast survives Holm at 5%; at 10% only the spend ratio, percentile only',
     all(not F38['survivors_5pct'][t] for t in F38['survivors_5pct'])
     and F38['survivors_10pct']['holm_percentile'] == ['spend_ratio']
     and not any(F38['survivors_10pct'][t] for t in ('holm_normal', 'holm_basic', 'romano_wolf'))),
]
# horizons.tex and levers_by_position.tex: qualitative statements about the calibration (notes/calibration_results.json)
# and the generated lever table (sections/tables/levers_position_macros.tex, code/playbook/run_archetypes.py)
# WITHDRAWN UNDER D-1; DO NOT QUOTE: \lpXhat, \lpXdagMin, \lpXdagMax and \lpScreenBelowAll (written by
# code/playbook/run_archetypes.py into levers_position_macros.tex) are computed at the revealed weight X-hat = k + spend
# ratio / alpha, which decision D-1 withdrew; they stay defined so that old text compiles, and the editor removes their uses.
_lp = {}
_lpf = os.path.join(BASE, 'sections', 'tables', 'levers_position_macros.tex')
if os.path.exists(_lpf):
    _lp = dict(re.findall(r'\\newcommand\{\\(lp[A-Za-z]+)\}\{([^}]*)\}', open(_lpf).read()))
# decision 7: recompute the growth-engine-versus-G&A counts from the playbook's cell medians on each S&M basis
sys.path.insert(0, os.path.join(BASE, 'code', 'playbook'))
import archetypes as _ARC
_pos = [a for a in _ARC.build_archetypes(_ARC.load_core_panel())[0] if a.code != 'A7']
_bM = vest('spend_maint_base')
assert abs(_bM - _ARC.MAINT_BASE) < 1e-12
_sig_b = {'netted': lambda a: max(a.sm - _bM, 0.0), 'all': lambda a: a.sm, 'none': lambda a: 0.0}
LV_REC = {b: sum(f(a) > a.ga for a in _pos) for b, f in _sig_b.items()}
LV_REC.update(n=len(_pos), net_list=[a.name for a in _pos if _sig_b['netted'](a) > a.ga])
_RB = json.load(open(os.path.join(BASE, 'notes', 'playbook_results.json'))).get('ranking_by_basis', {})
# text check: no sentence of the levers section may say that the growth engine leads (outranks, comes first) at every position
_lt = re.sub(r'(?<!\\)%.*', '', open(os.path.join(BASE, 'sections', 'levers_by_position.tex')).read())
_every = re.compile(r'every position|each position|all six positions|all (the )?positions|at every|lpGEFirstAll\b|lpNGEFirstAllSM')
_lead = re.compile(r'outrank|ranks? .*above|leads?|comes? first|ranks? first|ahead of')
_neg = re.compile(r'\bnot\b|\bonly\b|\bnone\b|lpNGEFirstNet|all selling and marketing|all S\\&M|upper bound|bound')
LV_TEXT_BAD = [x.strip()[:160] for x in re.split(r'(?<=[.;])\s+', _lt)
               if re.search(r'growth[- ]engine', x) and _every.search(x) and _lead.search(x) and not _neg.search(x)]
for x in LV_TEXT_BAD:
    print(f"levers text claims a lead at every position: {x}", file=sys.stderr)
_T36 = CAL['tornado']['2036']
_CP = CAL['central_path']['path']
CLAIMS += [
    ('anchor (empirics): netted median surplus above zero in all four views, E1 lower end near zero (under 1 point)',
     count_four('anchor_p95_Pi_net_med', lambda c: c[0] > 0) == 4 and 0 < vrec('anchor_p95_Pi_net_med', 'E1')['ci90'][0] < 0.01),
    ('horizons: the 2028 compute share is above the 2025-prices value and the 2031 and 2036 values (rises, then falls)',
     CAL['compute_share']['values']['2028']['value'] > max(CAL['compute_share']['values'][h]['value'] for h in ('2031', '2036'))
     and CAL['compute_share']['values']['2028']['value'] > C['central']['c_c']),
    ('horizons: pass-through raises every central threshold (2025 prices and each horizon)',
     all(CAL['pass_through'][f]['ceiling']['central']['G100'] > CAL['pass_through']['0.0']['ceiling']['central']['G100']
         for f in ('0.5', '0.7'))
     and all(CAL['pass_through'][f]['ceiling_by_horizon'][h]['central']['G100']
             > CAL['pass_through']['0.0']['ceiling_by_horizon'][h]['central']['G100'] for f in ('0.5', '0.7') for h in ('2028', '2031', '2036'))),
    ('horizons: the upper-bound median anchor intercept is below the central and favorable full-cost margin terms',
     A['m0_ub'][1] < cen['base'] and A['m0_ub'][1] < C['favorable']['base']),
    ('horizons: change capacity binds under central and fast execution',
     CAL['pace']['central']['binding'] == 'change' and CAL['pace']['fast']['binding'] == 'change'),
    ('horizons: the greedy plan fills every wave under central execution through 2036 (upper bound attained)',
     (lambda P_: P_['rho'] * P_['params']['Tpar'] * (1 + P_['params']['varpi'] * (P_['2036']['n'] - 1)) <= 1)(CAL['pace']['central'])),
    ('horizons: central execution realizes less than half of the program by 2036', CAL['pace']['central']['2036']['s'] < 0.5),
    ('horizons: the median anchor firm-year has no upper-bound surplus to scale (Pi_ub median <= 0)', A['Pi_ub'][1] <= 0),
    ('horizons: the central path is below 100 at every horizon on all three bases, and the upper end of its anchor-sampling '
     'interval too', all(_CP[b][h]['R'] < 1.0 and CAL['r2']['anchor_interval'][b]['path'][h]['ci90_joint'][1] < 1.0
                         for b in ('net', 'ub', 'lb') for h in ('2028', '2031', '2036'))),
    ('horizons (decision 4): the netted central path lies between the two bounds at every horizon',
     all(_CP['lb'][h]['R'] <= _CP['net'][h]['R'] <= _CP['ub'][h]['R'] for h in ('2028', '2031', '2036'))),
    ('horizons (B7): cumulative payback comes after the flow crossing, and the discounted payback after the undiscounted',
     CAL['r2']['payback']['central']['cross_flow'] < CAL['r2']['payback']['central']['payback_undiscounted']
     < CAL['r2']['payback']['central']['payback_discounted']),
    ('horizons (B7): under central execution the cumulative cash effect is negative at a five-year hold',
     CAL['r2']['payback']['central']['hold']['5']['cum'] < 0),
    ('horizons: no single tornado input lifts the 2036 central score to 100', max(r['high'] for r in _T36['rows']) < 1.0),
    ('horizons: a guided dip slows the program (realized share below the central one by 2036)',
     V['public_guided_dip_1pt']['2036']['s'] < CAL['pace']['central']['2036']['s']
     and V['public_guided_dip_2pt']['2036']['s'] < CAL['pace']['central']['2036']['s']),
    ('abstract and intro: the Psi slope is about a fifth of a point (absolute value 0.15 to 0.25 on both bases, E1)',
     all(0.15 <= abs(FS3['central'][b]['E1']['est']) <= 0.25 for b in ('op', 'cash'))),
    ('abstract: the GAAP P95 fall is the smaller of the two bases (written "by GAAP to cash points")',
     -vest('p95_change_op', 'E1') <= -vest('p95_change_cash', 'E1')),
    ('discussion: the E1 spend ratio exceeds one and the lower-quartile anchor surplus (upper bound) is negative',
     vest('spend_ratio') > 1 and CAL['anchor']['Pi_ub'][0] < 0),
    ('accountability floor (C1): the bottom-up floors at 1% and 5% differ by less than 0.01% of revenue',
     abs(floor_['Five'] - floor_['One']) < 1e-4),
    ('accountability floor (C1): in the example, no single-provider all-AI design passes at either threshold because the '
     'AI common mode 0.005 exceeds the per-opportunity ceiling', all(0.005 >= Pbar(e) for e in EPS.values())),
    ('accountability floor (C2): one human over one AI layer stops being admissible at 5% once p^cc exceeds about 0.0008',
     0.0008 <= BE[('Five', (1, 1))] < 0.0009),
    ('accountability floor: all-human designs fail at the stricter threshold but pass at the central one (text: 1% "does so here")',
     amin_best(PIBAR_SENS, kind='human') is None and amin_best(PIBAR, kind='human') is not None),
    # author decision 7 (2 Nov, ~12:35): maintenance-netted S&M is central for the levers too. The counts are recomputed
    # here from the playbook's cell medians (code/playbook/archetypes.py, data/panel_v3.csv) on each basis: at the weight
    # a position's own spending reveals, the growth engine leads the G&A cut iff its growth spend exceeds its G&A share
    ('levers (decision 7): the growth engine leads the G&A cut at the netted count recomputed from the cell medians '
     '(lpNGEFirstNet), at all positions on all S&M and at none on no S&M; the G&A cut leads at the rest (lpNGACutFirstNet)',
     _lp.get('lpNGEFirstNet') == str(LV_REC['netted']) and _lp.get('lpNGEFirstAllSM') == str(LV_REC['all'])
     and _lp.get('lpNGEFirstNoSM') == str(LV_REC['none']) and LV_REC['all'] == LV_REC['n'] and LV_REC['none'] == 0
     and _lp.get('lpNGACutFirstNet') == str(LV_REC['n'] - LV_REC['netted'])
     and _lp.get('lpGEFirstNetList') == (', '.join(LV_REC['net_list']) or 'none') and _lp.get('lpGEFirstAll') == 'no'
     and _lp.get('lpNPositions') == str(LV_REC['n'])),
    ('levers (decision 7): the spend ratio of the table is the netted one (lpRatio = AlphaNet), the all-S&M ratio a bound',
     _lp.get('lpRatio') == fmt(vest('spend_maint_ratio'), 2, pct=False) and _lp.get('lpBasis') == 'maintenance-netted'),
    ('levers (decision 7): engineering ranks first of the four levers at every position on the netted basis, and the '
     'counts of notes/playbook_results.json agree with the recomputed growth-engine counts on all three bases',
     _RB.get('n_eng_first_netted') == LV_REC['n'] and all(_RB.get(f'n_ge_ahead_of_ga_{b}') == LV_REC[b] for b in ('netted', 'all', 'none'))),
    ('levers text (decision 7): sections/levers_by_position.tex does not claim that the growth engine leads at every position',
     not LV_TEXT_BAD),
    ('levers: at the proxy calibration every switch weight exceeds screening weights of 2 to 3 (lpScreenBelowAll)',
     _lp.get('lpScreenBelowAll') == 'yes'),
]
_failed = [c for c, ok in CLAIMS if not ok]
os.makedirs(OUT_DIR, exist_ok=True)
FLAGS = ['psi_op_E1_vs_m1', 'psi_cash_E1_vs_m1', 'gap_E1', 'gap_fast_sm_E1']
open(os.path.join(OUT_DIR, 'claim_checks.txt'), 'w').write(
    ''.join(f"{'ok  ' if ok else 'FAIL'} {c}\n" for c, ok in CLAIMS)
    + '\n# Interval claims are checked under the percentile, basic, normal and BC 90% intervals (TYPES4); Holm under the\n'
    + '# normal, percentile and basic p-values and Romano-Wolf (the outputs carry no BC p-value).\n'
    + '# FLAGGED family-B tests (A2): ' + '; '.join(f"{k} ({'slope against -1' if 'm1' in k else 'tautological margin gap'})"
                                                  for k in FLAGS) + '\n'
    + f"# Family B with the anchor test (13 estimable tests + the anchor; the referee counted 15), Holm p of the anchor: " + ', '.join(f"{k} {v:.3f}" for k, v in HOLM_ANCHOR.items()) + '\n')
if _failed:
    for c in _failed:
        print(f"CLAIM CHECK FAILED: {c}", file=sys.stderr)
    if os.environ.get('P1_CLAIMS_WARN_ONLY') != '1':
        sys.exit(f"{len(_failed)} qualitative statements are no longer supported (paper1/claim_checks.txt)")

# ---- generated tables for Paper 1
# (1) the robustness table (tab:robust): every sample variant of estimate_v3.py, point estimates
ROWS = [('E1', r'E1: all firm-years (baseline)'),
        ('E1k2010', r'E1 plus fiscal-2010 years first reported in a later filing (R1 sensitivity)'),
        ('E1clean', r'E1 without all 16 firms the panels named as possibly not software'),
        ('E1r2named', r'E1 without the named firms the R2 classifier classes non-software'),
        ('E1nolist', r'E1 without the firm-years R5 flags as having no listed equity'),
        ('E1nodebt', r'E1 without the four debt-only filers a referee named'),
        ('E2', r'E2: organic growth, pro forma where disclosed (25\% flag)'),
        ('E2pf10', r'E2 with the flag at 10\%'), ('E2pf50', r'E2 with the flag at 50\%'),
        ('E2x10', r'Acquisition-affected years excluded, 10\% flag'), ('E2x25', r'Acquisition-affected years excluded, 25\% flag'),
        ('E2x50', r'Acquisition-affected years excluded, 50\% flag'),
        ('E2add', r'E2, ambiguous pro forma cases read additively'), ('E2max', r'E2, ambiguous pro forma cases read cumulatively'),
        ('E2testrule', r"E2 under the first test run's rule"),
        ('E2k2010', r'E2 plus fiscal-2010 years first reported in a later filing'),
        ('E2clean', r'E2 without all 16 named firms'), ('E2r2named', r'E2 without the named firms R2 classes non-software'),
        ('E2nolist', r'E2 without the firm-years R5 flags'), ('E2nodebt', r'E2 without the four named debt-only filers'),
        ('E2imp4', r'E2 plus the dropped years, organic growth imputed at $M=4$'),
        ('E2imp8', r'E2 plus the dropped years, organic growth imputed at $M=8$')]
COLS = [('cone_op_slope_c90_w60', 2, False), ('cone_cash_slope_c90_w60', 2, False), ('slope_op_pooled', 2, False),
        ('slope_cash_pooled', 2, False), ('p95_change_op', 1, True), ('p95_change_cash', 1, True), ('spend_ratio', 2, False),
        ('gap_avg', 1, True)]


for b, B_ in [('op', 'Op'), ('cash', 'Cash')]:
    _pv = [vest(f'cone_{b}_slope_c90_w60', v_) for v_, _ in ROWS]
    num(f'PsiVar{B_}Lo', min(_pv), 2, False); num(f'PsiVar{B_}Hi', max(_pv), 2, False)
    _lv = [vest(f'slope_{b}_pooled', v_) for v_, _ in ROWS]
    num(f'LocVar{B_}Lo', min(_lv), 2, False); num(f'LocVar{B_}Hi', max(_lv), 2, False)
put('NVariants', str(len(ROWS)))


def cell(x, nd, pct):
    s = fmt(x, nd, pct)
    return f"$-${s[1:]}" if s.startswith('-') else s


tl = [r'\begin{table}[t]\centering\footnotesize\setlength{\tabcolsep}{3pt}',     # final audit m6: no \resizebox
      r'\caption{Sensitivity of the headline statistics to the sample rules and the construction of E2, audited sample (v3)}\label{tab:robust}',
      r'\begin{tabular}{@{}>{\raggedright\arraybackslash}p{5.4cm}rcccccccc@{}}\toprule',
      r' & & \multicolumn{2}{c}{$\Psi_{0.90}$ slope} & \multicolumn{2}{c}{Local $Q_{0.90}$ slope} & \multicolumn{2}{c}{Change in P95 of $R$} & Spend & Margin\\'
      r'\cmidrule(lr){3-4}\cmidrule(lr){5-6}\cmidrule(lr){7-8}',
      r'Sample & Firm-years & GAAP & cash & GAAP & cash & GAAP & cash & ratio & gap\\\midrule']
for v_, lab in ROWS:
    tl.append(f"{lab} & {thousands(S3[v_]['n'])[0]} & " + ' & '.join(cell(vest(st, v_), nd, pct) for st, nd, pct in COLS) + r' \\')
tl += [r'\bottomrule\end{tabular}',
       r'\par\vspace{2pt}\footnotesize\raggedright Notes: Point estimates from \texttt{code/estimate\_v3.py}; definitions as in '
       r'Table~\ref{tab:estimands_v3}, which gives firm-cluster bootstrap intervals for the E1, E2, exclusion-only (25\%) and '
       r'imputed rows. Change in P95: 2016--19 to 2023--25, points. Spend ratio: median selling-and-marketing share over growth '
       r'in excess of the year median, firm-years growing faster than the median. Margin gap: GAAP operating margin of the top '
       r'decile minus the 40th--60th percentiles within growth bands, average of bands, points. Sensitivity rows add back or '
       r'remove firm-years by the rule named; R2 and R5 cannot be applied from the local data, so the firms the review panels '
       r'named enter only these rows.',
       r'\end{table}']
open(os.path.join(OUT_DIR, 'tab_robust_v3.tex'), 'w').write('\n'.join(tl) + '\n')

# (2) the tables of estimate_v3_report.py, with the bootstrap seeds in their notes and two fixes for this paper
SEEDS = (f"Bootstrap: {V3['meta']['replications']} firm-cluster replications; one generator per block of statistics, "
         f"seeded with {V3['meta']['seed0']} plus the CRC-32 checksum of the block name modulo $10^6$ ("
         + ', '.join(f"{k} {v}" for k, v in V3['meta']['seeds'].items()) + ').')
SEEDREF = (f"Bootstrap: {V3['meta']['replications']} firm-cluster replications; seeds by block in the notes to "
           r"Table~\ref{tab:estimands_v3}.")


def table_copy(name, fixes, seeds):
    src = open(v3path(os.path.join('sections', 'tables'), name)).read()
    for old, new in fixes:
        assert src.count(old) == 1, (name, old)
        src = src.replace(old, new)
    assert src.rstrip().endswith(r'\end{table}'), name
    src = src.rstrip()[:-len(r'\end{table}')].rstrip() + ' ' + seeds + '\n' + r'\end{table}' + '\n'
    open(os.path.join(OUT_DIR, name), 'w').write(src)


table_copy('tab_estimands_v3.tex', [], SEEDS)
# final audit m6 and m13: the main-text Table 2 keeps E1, E2, both imputation bounds and the D-3 column at \footnotesize
# without \resizebox; the E1 - E2 and exclusion-only columns move to a supplement table appended to the file of Table S6
# (paper1/tab_contrasts_v3.tex, after its table). The netted (central) anchor-surplus row is added under the two bounds.
_src = open(os.path.join(OUT_DIR, 'tab_estimands_v3.tex')).read()
_lines = _src.split('\n')
_i0 = next(i for i, l in enumerate(_lines) if l.startswith('\\multicolumn{9}{l}{\\emph{A.'))
_i1 = next(i for i, l in enumerate(_lines) if l.startswith('\\bottomrule'))
_body = _lines[_i0:_i1]
_notes = '\n'.join(_lines[_i1 + 1:]).replace('\\end{table}', '').strip()
assert _notes.startswith('\\par\\vspace{2pt}\\footnotesize\\raggedright Notes:')


def _cells(l):
    t = l.rstrip()
    assert t.endswith('\\\\'), l
    return [c.strip() for c in re.split(r'(?<!\\)&', t[:-2])]


def _netted_row():
    """median netted surplus with 90% percentile intervals in the four views and the D-3 column (sign / interval)"""
    def cellv(e):
        r = vrec('anchor_p95_Pi_net_med', e)
        f1 = lambda x: (f"$-${abs(half_up(100 * x, 1)):.1f}" if half_up(100 * x, 1) < 0 else f"+{half_up(100 * x, 1):.1f}")
        return f"{f1(r['est'])} [{f1(r['ci90'][0])}, {f1(r['ci90'][1])}]"
    sign_n = sum(vest('anchor_p95_Pi_net_med', e) > 0 for e, _ in FOUR)
    int_n = count_four('anchor_p95_Pi_net_med', lambda c: c[0] > 0)
    d3 = ('yes' if sign_n == 4 else f'no ({sign_n}/4)') + '/' + ('yes' if int_n == 4 else f'no ({int_n}/4)')
    return ['Anchor: median $\\Pi$, maintenance-netted (central)', 'cash', cellv('E1'), cellv('E2'), cellv('E2imp4'),
            cellv('E2imp8'), d3]


_main, _more = [], []
for l in _body:
    if '\\multicolumn{9}' in l and ' & ' not in l:
        _main.append(l.replace('\\multicolumn{9}', '\\multicolumn{7}')); _more.append(l.replace('\\multicolumn{9}', '\\multicolumn{4}'))
        continue
    c = _cells(l)
    assert len(c) == 9, l
    cm = [x.replace('FCF after SBC', 'cash') for x in c[:2]] + c[2:]        # basis abbreviated (defined in the notes)
    _main.append(' & '.join(cm[:4] + cm[6:9]) + ' \\\\')
    _more.append(' & '.join(c[:2] + c[4:6]) + ' \\\\')
    if c[0].startswith('Anchor: median $\\Pi$, no S\\&M buys growth'):
        _main.append(' & '.join(_netted_row()) + ' \\\\')
_C = r'>{\centering\arraybackslash}p{1.9cm}'
_kB = next(i for i, l in enumerate(_main) if l.startswith('Anchor: median'))   # part 2 starts at the anchor rows
_main.insert(_kB, '\\multicolumn{7}{l}{\\emph{A. Model-facing statistics (continued)}}\\\\')
_HEAD = (r"""\begin{tabular}{@{}>{\raggedright\arraybackslash}p{3.9cm}l""" + _C * 4 + r"""c@{}}\toprule
 & & E1: all & E2: & \multicolumn{2}{c}{E2 plus imputed} & Holds in\\\cmidrule(lr){5-6}
Statistic & Basis & firm-years & organic & $M=4$ & $M=8$ & all four\\\midrule
""")
# two floats, both numbered Table 2 (the second decrements the counter), each within one page at \footnotesize
_tab2 = (r"""\begin{table}[p]\centering\footnotesize\setlength{\tabcolsep}{1.5pt}\renewcommand{\arraystretch}{0.92}
\caption{Headline statistics on the audited sample (v3): E1 baseline, E2 and imputation bounds}\label{tab:estimands_v3}
""" + _HEAD + '\n'.join(_main[:_kB]) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: Panels B and C and the notes follow on the next page. Cash: free cash flow after SBC.
\end{table}
\begin{table}[p]\centering\footnotesize\setlength{\tabcolsep}{1.5pt}\renewcommand{\arraystretch}{0.92}\addtocounter{table}{-1}
\caption{Headline statistics on the audited sample (v3), continued}
""" + _HEAD + '\n'.join(_main[_kB:]) + r"""
\bottomrule\end{tabular}
""" + _notes.replace('Notes:', r'Notes: Cash: free cash flow after SBC. The E1 $-$ E2 contrasts and the exclusion-only sample are in Table~\ref{tab:estimands_v3_more}; the maintenance-netted row nets the maintenance level of selling and marketing out of growth spend in each view and each draw (Section~\ref{sec:horizons-ranges}).', 1) + '\n\\end{table}\n')
if os.environ.get('P1_TABLE2_COMPACT') == '1':     # one float, the seven main columns scaled to the text width (page budget)
    _tab2 = (r"""\begin{table}[t]\centering\small
\caption{Headline statistics on the audited sample (v3): E1 baseline, E2 and imputation bounds}\label{tab:estimands_v3}
\resizebox{\textwidth}{!}{\begin{tabular}{llccccc}\toprule
 & & E1: all & E2: & \multicolumn{2}{c}{E2 plus imputed} & Holds in\\\cmidrule(lr){5-6}
Statistic & Basis & firm-years & organic & $M=4$ & $M=8$ & all four\\\midrule
""" + '\n'.join(_main) + r"""
\bottomrule\end{tabular}}
""" + _notes.replace('Notes:', r'Notes: Cash: free cash flow after SBC. The E1 $-$ E2 contrasts and the exclusion-only sample are in Table~\ref{tab:estimands_v3_more}.', 1) + '\n\\end{table}\n')
open(os.path.join(OUT_DIR, 'tab_estimands_v3.tex'), 'w').write(_tab2)
TAB2_MORE = (r"""\begin{table}[t]\centering\footnotesize
\caption{Headline statistics on the audited sample (v3), continued: E1 $-$ E2 and the exclusion-only sample}\label{tab:estimands_v3_more}
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{7.2cm}lcc@{}}\toprule
Statistic & Basis & E1 $-$ E2 & Exclusion only, 25\%\\\midrule
""" + '\n'.join(_more) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: The columns of Table~\ref{tab:estimands_v3} that the main text does not show, same statistics, definitions and bootstrap. E1 $-$ E2: paired firm-cluster bootstrap of the difference (its interval types and multiplicity adjustments are in Table~\ref{tab:contrasts_v3}). Exclusion only: E2's construction with every acquisition-affected firm-year at the 25\% flag excluded instead of re-admitted pro forma.
\end{table}
""")
_c = open(v3path(os.path.join('sections', 'tables'), 'tab_contrasts_v3.tex')).read().split('\n')
_i = [j for j, l in enumerate(_c) if l.startswith(r'$\Psi_{0.90}$ slope, 2020--25')][0]
_labels = [_c[j].split(' & ')[0] for j in (_i - 2, _i - 1, _i)]
assert all(_c[_i + 1 + j].startswith(' & cash & ') for j in range(3))
_fix = [(_c[_i + 1 + j], _labels[j] + _c[_i + 1 + j]) for j in range(3)]
table_copy('tab_contrasts_v3.tex', _fix + [
    (r'the family counted by the econometrics referees for Table~\ref{tab:estimands}.',
     r'the family the econometrics referees counted in the estimands table of the first version.')], SEEDREF)
_cs = open(os.path.join(OUT_DIR, 'tab_contrasts_v3.tex')).read().split('\n')
_j0 = next(i for i, l in enumerate(_cs) if l.startswith('Statistic & Basis & E1 $-$ E2'))
_j1 = next(i for i, l in enumerate(_cs) if l.startswith('\\bottomrule'))
_cnotes = '\n'.join(_cs[_j1 + 1:]).replace('\\end{table}', '').strip()
_rowsA, _rowsB = [], []
for l in _cs[_j0 + 1:_j1]:
    if not l.strip():
        continue
    if l.startswith('\\multicolumn') or l.startswith('\\addlinespace'):
        _rowsA.append(l.replace('\\multicolumn{14}', '\\multicolumn{7}')); _rowsB.append(l.replace('\\multicolumn{14}', '\\multicolumn{8}'))
        continue
    c = _cells(l)
    assert len(c) == 14, l
    _rowsA.append(' & '.join(c[:6] + [c[9]]) + ' \\\\')
    _rowsB.append(' & '.join(c[:2] + c[6:9] + c[10:14]) + ' \\\\')
_IV = r'>{\centering\arraybackslash}p{1.85cm}'
_S6a = (r"""\begin{table}[t]\centering\footnotesize\setlength{\tabcolsep}{2.5pt}\renewcommand{\arraystretch}{0.88}
\caption{Paired E1 $-$ E2 contrasts on the audited sample (v3): estimates, 90\% intervals and unadjusted $p$}\label{tab:contrasts_v3}
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{5.6cm}lc""" + _IV * 3 + r"""c@{}}\toprule
 & & & \multicolumn{3}{c}{90\% interval} & \\\cmidrule(lr){4-6}
Statistic & Basis & E1 $-$ E2 & percentile & basic & normal & $p$ (percentile)\\\midrule
""" + '\n'.join(_rowsA) + r"""
\bottomrule\end{tabular}
""" + _cnotes + ' The 95\\% intervals and the multiplicity-adjusted $p$-values are in Table~\\ref{tab:contrasts_v3b}.\n\\end{table}\n')
_S6b = (r"""\begin{table}[t]\centering\footnotesize\setlength{\tabcolsep}{2.5pt}\renewcommand{\arraystretch}{0.88}
\caption{Paired E1 $-$ E2 contrasts on the audited sample (v3), continued: 95\% intervals and multiplicity-adjusted $p$}\label{tab:contrasts_v3b}
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{4.6cm}l""" + _IV * 3 + r"""cccc@{}}\toprule
 & & \multicolumn{3}{c}{95\% interval} & \multicolumn{3}{c}{Holm-adjusted $p$} & Romano--\\\cmidrule(lr){3-5}\cmidrule(lr){6-8}
Statistic & Basis & percentile & basic & normal & percentile & basic & normal & Wolf\\\midrule
""" + '\n'.join(_rowsB) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: Same contrasts and bootstrap as Table~\ref{tab:contrasts_v3}.
\end{table}
""")
open(os.path.join(OUT_DIR, 'tab_contrasts_v3.tex'), 'w').write(_S6a + '\n' + _S6b + '\n' + TAB2_MORE)   # final audit m6
table_copy('tab_grid_v3.tex', [('(Definition 2)', r'(Definition~\ref{def:industry})')], SEEDREF)
table_copy('tab_yearly_v3.tex', [], SEEDREF)

# ---------------------------------------------------------------------------------------------- write macros
os.makedirs(OUT_DIR, exist_ok=True)
lines = ['% Generated by code/paper1_macros.py from notes/calibration_results.json, notes/paper_stats.json,',
         '% notes/empirics_revised.json, notes/gap_decomposition.json and data/panel*.csv. Do not edit by hand.',
         '% Values are rounded half up; percentages are given without the percent sign.',
         f"% v3 outputs (notes/empirics_v3.json and companions) read from {V3DIR if V3DIR else 'the live repository'}."]
for k, v in M.items():
    lines.append(f"\\newcommand{{\\{k}}}{{{v}}}")
open(os.path.join(OUT_DIR, 'macros.tex'), 'w').write('\n'.join(lines) + '\n')

# ---------------------------------------------------------------------------------------------- plain abstract
src = open(os.path.join(BASE, 'sections', 'abstract.tex')).read()
body = src.split(r'\begin{abstract}', 1)[1].split(r'\end{abstract}', 1)[0]
body = re.sub(r'(?<!\\)%.*', '', body)                       # comments
body = body.replace(r'\noindent', '')


def expand(m):
    name = m.group(1)
    if name not in PLAIN:
        sys.exit(f"abstract uses undefined macro \\{name}")
    return PLAIN[name]


body = re.sub(r'\\(emph|textit|textbf)\{([^}]*)\}', r'\2', body)
if re.search(r'\\cite', body):
    sys.exit('the abstract must not cite')
body = re.sub(r'\\([A-Za-z]+)(\{\})?', expand, body)
body = (body.replace(r'\%', '%').replace('---', ' - ').replace('--', '-').replace('~', ' ')
        .replace(r'\$', '$').replace('$', '').replace(r'\,', ' ').replace('{,}', ','))
body = re.sub(r'\s+', ' ', body).strip()
if '\\' in body or '{' in body:
    sys.exit(f"unconverted LaTeX in abstract: {body}")
open(os.path.join(OUT_DIR, 'abstract_plain.txt'), 'w').write(body + '\n')
n = len(body)
print(f"wrote {len(M)} macros to paper1/macros.tex; abstract {n} characters (limit {MAX_ABSTRACT})")
if n > MAX_ABSTRACT:
    sys.exit(f"abstract too long: {n} > {MAX_ABSTRACT}")
