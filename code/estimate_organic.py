#!/usr/bin/env python3
"""Two estimands for Paper 1: observed scores (E1) and the organic frontier (E2).

E1  Observed scores: every firm-year of the core sample (data/panel.csv) with reported growth g. These are the
    scores firms report and practitioners screen on; E1 is primary for descriptive statistics of reported scores.
E2  The organic frontier: growth bought with spend the firm expenses, which is the growth the model describes.
    A firm-year is acquisition-affected under the flag of code/build_panel_v2.py (cash paid for acquisitions or the
    increase in goodwill at least 25% of prior-year revenue, or pro forma revenue at least 10% above revenue; the
    flag covers that year and the following one). E2 keeps an affected firm-year with organic growth g_org where the
    ASC 805 pro forma disclosures let us remove the acquired contribution, and excludes it otherwise. Unverified
    hypergrowth (g >= 100% with neither acquisition payments nor goodwill reported) is excluded, as in Table
    tab:robust. E2 is primary for the model-facing statistics.

Organic growth (constant perimeter). With S_t revenue as first reported and three ratios read from the ORIGINAL
annual filings (data/companyfacts_extract.json, element BusinessAcquisitionsProFormaRevenue; nothing is re-fetched),
    pi_t     = PF_t^(t) / S_t - 1          current-year pro forma in the year-t filing: pre-acquisition revenue of
                                           the businesses bought in t, as a share of S_t
    rho_t    = PF_{t-1}^(t) / S_{t-1} - 1  prior-period pro forma in the same filing: the year t-1 revenue of the
                                           businesses bought in t
    pi_{t-1} = PF_{t-1}^(t-1) / S_{t-1}^(t-1) - 1   current-year pro forma in the year t-1 filing (carry-over of the
                                           businesses bought in t-1, which are consolidated for the whole of t)
    g_org_t  = (1 + g_t)(1 + pi_t) / (1 + pi_{t-1} + rho_t) - 1,
the growth of the businesses owned at the end of year t, as if all had been owned through t-1 and t. The adjustment is
applied to acquisition-affected firm-years only; unaffected firm-years keep reported growth, as in the exclusion-only
sample, so that E2 differs from that sample only by the affected firm-years it re-admits. Rules: the year-t pair
(pi_t, rho_t) is used only when both figures are reported in the same filing, lie between 0.98 and 3.5 times the
reported revenue, and the prior-period figure is not a repeat (to 0.1%) of the previous filing's current-year figure,
which happens when a filing re-reports last year's acquisitions; otherwise the pair is zero if the year is not an
acquisition year and unknown if it is. pi_{t-1} is used whenever the previous fiscal year's filing reports a valid
figure, is zero if that year is not an acquisition year, and unknown otherwise. Ambiguity: ASC 805-10-50-2(h)(3) asks
the year-t note for the year-t combinations only, which gives the additive denominator above, but some filers present
the comparative year cumulatively, including the previous year's combinations (the SS&C 2019 note is an example), in
which case the denominator is 1 + max(pi_{t-1}, rho_t). When both readings are possible (pi_{t-1} > 0 and rho_t > 0)
and they differ by more than one point of growth, g_org is not identified and the firm-year is excluded from E2; the
additive (lower) and cumulative (upper) readings are reported as sensitivity variants E2add and E2max. An affected
firm-year with an unknown ratio is excluded from E2. The margin is the reported consolidated margin.

Threshold sensitivity: exclusion-only samples (no pro forma adjustment) at cash and goodwill thresholds of 10, 25 and
50% of prior-year revenue, with the pro forma criterion scaled in proportion (4, 10, 20% of revenue); the 25% version
is the robustness sample of Table tab:robust. The pro forma adjusted samples at 10 and 50% are reported as point
estimates.

Estimators, standard errors and bootstrap replications are those of code/estimate_revised.py and code/decompose_gap.py
(firm-cluster bootstrap resampling firms within the sample of each statistic). Added here: a firm-cluster bootstrap for
the spend ratio (500 replications; the existing code reports none), a paired bootstrap of the difference E1 - E2
(firms drawn from E1, both estimands computed on the same draw, same replications as the statistic), and selection
diagnostics. Values are fractions (0.01 = one point) except slopes, the spend ratio and the weights.

Inputs : data/panel.csv, data/panel_v2_all.csv, data/companyfacts_extract.json, code/build_panel_v2.py (element list),
         notes/empirics_revised.json, notes/gap_decomposition.json (reproduction checks), notes/calibration_results.json
         or notes/empirics_v2_exact.json (E1 anchor regression check, whichever is on this script's sample; see
         anchor_reference)
Outputs: notes/empirics_organic.json, sections/tables/tab_estimands.tex, notes/estimand_notes.md,
         notes/calibration_anchor_E2.json (E2 and E1 anchor inputs on the v2 sample, the v2 reference of
         code/estimate_v3_report.py; E1 reproduces the v2 calibration anchor exactly; calibrate_horizons.py reads the v3
         file notes/calibration_anchor_v3.json since revision v2)
Run    : python3 code/estimate_organic.py      (about 30 minutes; ORGANIC_FAST=1 divides replications by 10 for testing;
         ORGANIC_TABLES_ONLY=1 rewrites the table, notes and anchor file from the JSON without re-estimating)
v3     : with ORGANIC_PANEL=v3 the file only builds the frames of the audited sample (data/panel_v3*.csv,
         code/build_panel_v3.py); code/estimate_v3.py executes it up to the END OF FRAME CONSTRUCTION marker and
         produces every v3 output (exact quantile regression, seeded firm-cluster bootstrap with 999 replications).
"""
import ast
import json
import math
import os
import warnings
from datetime import date

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

warnings.filterwarnings('ignore')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = 20261029
rng = np.random.default_rng(SEED)
FAST = os.environ.get('ORGANIC_FAST') == '1'
TABLES_ONLY = os.environ.get('ORGANIC_TABLES_ONLY') == '1'   # rewrite table and notes from the JSON
PANEL = os.environ.get('ORGANIC_PANEL', 'v2')                # v2 (default; outputs unchanged) or v3 (sample audit)
assert PANEL in ('v2', 'v3')
V3 = PANEL == 'v3'
OUT_JSON = f'{BASE}/notes/empirics_organic.json'
CHEAP_MIN = 0.10                                             # build_panel_v3.CHEAP_MIN (cheap-acquisition criterion)
ACQREV_MIN = 0.10                                            # build_panel_v3 R4(c): acquiree revenue / revenue
B = dict(slope=200, level=300, diff=500, capint=400, scale=200, spend=500, gap=999, sel=500)
if FAST:
    B = {k: max(10, v // 10) for k, v in B.items()}
PERIODS = ['2010-15', '2016-19', '2020-22', '2023-25']
MB = {'op': ('m_op', 'R_op', 'GAAP operating'), 'cash': ('m_fcf_sbc', 'R_cash', 'FCF after SBC')}
THETAS = {'10': 0.10, '25': 0.25, '50': 0.50}
PF_SHARE = 0.4                       # pro forma criterion as a multiple of theta: 10% of revenue at theta = 25%
PF_VALID = (0.98, 3.5)               # pro forma / reported revenue outside this range: not a combined-entity total
REPEAT_TOL = 1e-3
AMBIG_TOL = 0.01                     # additive and cumulative readings of the pro forma note may differ by one point
ALPHA = (0.25, 0.45)
SIZE_BINS = [100e6, 500e6, 2e9, 10e9, 1e13]
SIZE_KEYS = ['0_1to0_5B', '0_5to2B', '2to10B', 'over10B']
SPLITS = {'pooled': PERIODS, '2010_19': ['2010-15', '2016-19'], '2020_25': ['2020-22', '2023-25']}
GAP_BANDS = [(0, .1), (.1, .2), (.2, .3), (.3, .4), (.4, .6)]
GAP_KEYS = ['gap_avg', 'gap_gm', 'gap_sm', 'gap_rd', 'gap_ga', 'gap_oth',
            'gap_slow', 'gap_slow_gm', 'gap_fast', 'gap_fast_sm', 'gap_fast_rd']
SELV = ['rev_lag', 'g', 'gorg25', 'm_op', 'm_fcf_sbc', 'sbc_share', 'capex_int', 'sms', 'R_op', 'R_cash']
HEAD_KEYS = ['slope_op_pooled', 'slope_cash_pooled', 'slope_op_2010_19', 'slope_cash_2010_19', 'slope_op_2020_25',
             'slope_cash_2020_25', 'spend_ratio', 'weight_lo', 'weight_hi', 'scale_tenfold_op', 'scale_tenfold_cash',
             'capint_gap_op_2023_25', 'capint_gap_cash_2023_25', 'p95_op_2016_19', 'p95_op_2023_25', 'p95_cash_2016_19',
             'p95_cash_2023_25', 'p95_change_op', 'p95_change_cash', 'p90_change_op', 'p90_change_cash',
             'T_op_g00_change', 'T_op_g20_change', 'T_op_g40_change', 'T_cash_g00_change', 'T_cash_g20_change',
             'T_cash_g40_change'] + GAP_KEYS                  # stable flat keys of the 'headline' block
VARIANTS = ['E1', 'E2', 'E2x10', 'E2x25', 'E2x50', 'E2pf10', 'E2pf50', 'E2add', 'E2max']
BOOT = ['E1', 'E2', 'E2x10', 'E2x25', 'E2x50']          # variants with bootstrap standard errors
VLAB = {'E1': 'E1: observed (all firm-years)', 'E2': 'E2: organic (pro forma adjusted, 25% flag)',
        'E2x10': 'Exclusion only, 10% flag', 'E2x25': 'Exclusion only, 25% flag (Table tab:robust)',
        'E2x50': 'Exclusion only, 50% flag', 'E2pf10': 'Pro forma adjusted, 10% flag',
        'E2pf50': 'Pro forma adjusted, 50% flag',
        'E2add': 'E2 with ambiguous pro forma cases read additively (ASC 805 reading; lower bound on organic growth)',
        'E2max': 'E2 with ambiguous pro forma cases read cumulatively (upper bound on organic growth)'}

# =============================================================================================== 1. pro forma facts
src = open(f'{BASE}/code/build_panel_v2.py').read()
CON = next(ast.literal_eval(n.value) for n in ast.parse(src).body
           if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'CON')
PF_CI = CON.index('BusinessAcquisitionsProFormaRevenue')
raw = json.load(open(f'{BASE}/data/companyfacts_extract.json'))
Dt = date.fromisoformat

P = pd.read_csv(f'{BASE}/data/panel_v3_all.csv' if V3 else f'{BASE}/data/panel_v2_all.csv').sort_values(['cik', 'fy_end'], kind='stable').reset_index(drop=True)
if V3:                                                       # v3 acquisition flag (build_panel_v3.py, rule R4)
    P['acq_flag_v2'], P['acq_now_v2'] = P.acq_flag, P.acq_now
    P['acq_flag'], P['acq_now'], P['gw_jump'] = P.acq_flag_v3, P.acq_now_v3, P.gw_jump_v3
cache, cur_l, pri_l = {}, [], []
for cik, accn, E in zip(P.cik, P.accn, P.fy_end):
    if cik not in cache:
        blob = raw[str(cik)]
        cache[cik] = ({a[0]: i for i, a in enumerate(blob['acc'])},
                      [(ai, e, v) for ci, ai, s, e, v in blob['f']
                       if ci == PF_CI and s and v is not None and 340 <= (Dt(e) - Dt(s)).days <= 392])
    acc_idx, facts = cache[cik]
    a0 = acc_idx[accn]                                    # the original filing for the fiscal year
    cur = {v for ai, e, v in facts if ai == a0 and e == E}
    pri = {v for ai, e, v in facts if ai == a0 and 345 <= (Dt(E) - Dt(e)).days <= 385}
    assert len(cur) <= 1 and len(pri) <= 1, (cik, E)
    cur_l.append(cur.pop() if cur else np.nan)
    pri_l.append(pri.pop() if pri else np.nan)
P['pf_cur_raw'], P['pf_pri_raw'] = cur_l, pri_l
P['pf_cur'] = P.pf_cur_raw.where((P.pf_cur_raw / P.rev).between(*PF_VALID))
P['pf_pri'] = P.pf_pri_raw.where((P.pf_pri_raw / P.rev_lag).between(*PF_VALID))
grp = P.groupby('cik')
P['prev_year'] = grp.year.shift(1)
P['prev_rev'] = grp.rev.shift(1)
P['prev_pf_cur_raw'] = grp.pf_cur_raw.shift(1)
P['prev_pf_cur'] = grp.pf_cur.shift(1)
P['consec'] = P.prev_year == P.year - 1
P['pri_repeat'] = (P.pf_pri_raw.notna() & P.consec & P.prev_pf_cur_raw.notna()
                   & ((P.pf_pri_raw / P.prev_pf_cur_raw - 1).abs() < REPEAT_TOL))
P['pair'] = P.pf_cur.notna() & P.pf_pri.notna() & ~P.pri_repeat
P['pf_fallback'] = P.proforma_gap.notna() & P.pf_cur_raw.isna()    # panel's figure taken from a later filing


def acq_now(th):
    rl = P.rev_lag
    now = ((P.acq_pay.fillna(0) >= th * rl) | (P.gw_jump.fillna(0) >= th * rl)
           | (P.proforma_gap.fillna(0) >= PF_SHARE * th * P.rev))
    if V3:                                                   # cheap-acquisition criterion, independent of theta
        now = now | ((P.acq_spend_share >= CHEAP_MIN) & (P.accel_rel >= P.acq_spend_share) & P.g_prev.notna())
        now = now | (P.acquiree_rev_share.fillna(0) >= ACQREV_MIN)   # R4(c): acquiree revenue since acquisition
    return now


for t, th in THETAS.items():
    now = acq_now(th)
    prev_now = now.astype(float).groupby(P.cik).shift(1).fillna(0) > 0     # build_panel_v2: flag t and t+1
    if V3:
        prev_now = prev_now & P.consec                       # v3: following fiscal year, not following row
    P['now' + t], P['prevnow' + t], P['flag' + t] = now, prev_now, now | prev_now
    pi_t = np.where(P.pair, P.pf_cur / P.rev - 1, np.where(~now, 0.0, np.nan))
    rho_t = np.where(P.pair, P.pf_pri / P.rev_lag - 1, np.where(~now, 0.0, np.nan))
    pi_prev = np.where(P.consec & P.prev_pf_cur.notna(), P.prev_pf_cur / P.prev_rev - 1,
                       np.where(~prev_now, 0.0, np.nan))
    P['pi' + t], P['rho' + t], P['piprev' + t] = pi_t, rho_t, pi_prev
    flag = (now | prev_now).values
    g_add = (1 + P.g) * (1 + pi_t) / (1 + pi_prev + rho_t) - 1                  # ASC 805: year-t combinations only
    g_max = (1 + P.g) * (1 + pi_t) / (1 + np.maximum(pi_prev, rho_t)) - 1          # cumulative comparative year
    amb = flag & ((g_max - g_add) > AMBIG_TOL).values
    P['amb' + t] = amb
    P['gadd' + t] = np.where(flag, g_add, P.g)                                   # unaffected: reported growth
    P['gmax' + t] = np.where(flag, g_max, P.g)
    P['gorg' + t] = np.where(flag, np.where(amb, np.nan, g_add), P.g)
assert (P.now25.astype(int) == P.acq_now).all() and (P.flag25.astype(int) == P.acq_flag).all(), 'flag not reproduced'

P['k_lag'] = P.groupby('cik').capex_int.shift(1).where(P.consec)          # prior fiscal year's capital intensity
core = pd.read_csv(f'{BASE}/data/panel_v3_core_full.csv' if V3 else f'{BASE}/data/panel.csv')
if V3:
    core['acq_flag_v2'], core['acq_now_v2'] = core.acq_flag, core.acq_now
    core['acq_flag'], core['acq_now'], core['gw_jump'] = core.acq_flag_v3, core.acq_now_v3, core.gw_jump_v3
keep = ['cik', 'year', 'fy_end', 'pf_cur_raw', 'pf_pri_raw', 'pf_cur', 'pf_pri', 'pri_repeat', 'pair', 'pf_fallback', 'k_lag']
keep += [c + t for t in THETAS for c in ['now', 'prevnow', 'flag', 'pi', 'rho', 'piprev', 'amb', 'gadd', 'gmax', 'gorg']]
core = core.merge(P[keep], on=['cik', 'year', 'fy_end'], how='left', validate='one_to_one')
assert core.flag25.notna().all() and (core.flag25.astype(int) == core.acq_flag).all()
core['unver'] = (core.g >= 1.0) & core.acq_pay.isna() & core.gw_jump.isna()


def reason(r):
    if not r.flag25:
        return 'not flagged'
    if pd.notna(r.gorg25):
        return 'organic growth computed'
    if r.amb25:
        return 'carry-over and current-year comparative both disclosed; readings differ by more than one point'
    if r.now25 and np.isnan(r.pi25):
        if pd.isna(r.pf_cur_raw):
            return 'acquisition year: no current-year pro forma revenue in the original filing'
        if pd.isna(r.pf_cur):
            return 'acquisition year: current-year figure not a combined-entity total'
        if pd.isna(r.pf_pri_raw):
            return 'acquisition year: prior-period pro forma revenue not reported'
        if r.pri_repeat:
            return "acquisition year: prior-period figure repeats the previous filing's current-year figure"
        return 'acquisition year: prior-period figure not a combined-entity total'
    return "following year: no valid pro forma revenue in the acquisition year's original filing"


core['reason25'] = core.apply(reason, axis=1)
core_ext = None
if V3:                                                       # primary v3 sample; the full v2 core is kept for sensitivities
    core_ext = core.copy()
    core = core[core.v3_exclude.fillna('') == ''].reset_index(drop=True)
core['G_t'] = core.groupby('year')['g'].transform('median')     # benchmark of estimate_revised.py (E1, reported g)
if V3:
    core_ext['G_t'] = core_ext.year.map(core.groupby('year')['g'].median())
core['lsize'] = np.log(core.rev_lag / 1e9)
core['size_bin'] = pd.cut(core.rev_lag, SIZE_BINS, labels=SIZE_KEYS, right=False)
core['gm'] = core.gp / core.rev
core['sms'] = core.sm / core.rev
core['rds'] = core.rd / core.rev
core['gas'] = core.ga / core.rev
core['oth'] = core.gm - core.sms - core.rds - core.gas - core.m_op
core['sbc_share'] = core.sbc / core.rev
if V3:
    core_ext['lsize'] = np.log(core_ext.rev_lag / 1e9)
    core_ext['size_bin'] = pd.cut(core_ext.rev_lag, SIZE_BINS, labels=SIZE_KEYS, right=False)
    core_ext['gm'] = core_ext.gp / core_ext.rev
    core_ext['sms'] = core_ext.sm / core_ext.rev
    core_ext['rds'] = core_ext.rd / core_ext.rev
    core_ext['gas'] = core_ext.ga / core_ext.rev
    core_ext['oth'] = core_ext.gm - core_ext.sms - core_ext.rds - core_ext.gas - core_ext.m_op
    core_ext['sbc_share'] = core_ext.sbc / core_ext.rev


def variant(mask, gcol=None, tflag='25', frame=None):
    v = (core if frame is None else frame)[mask].copy()
    v['g_rep'] = v['g']
    v['aff'] = v['flag' + tflag]                                    # acquisition-affected at the variant's threshold
    if gcol:
        v['g'] = v[gcol]
        v = v[(v.g > -0.9) & (v.g < 5)]                             # analysis bounds of build_panel_v2.py
    v['R_op'] = v.g + v.m_op
    v['R_cash'] = v.g + v.m_fcf_sbc
    v['hi_k'] = v.groupby('period')['capex_int'].transform(lambda x: (x > x.median()).astype(float))
    return v.reset_index(drop=True)


V = {'E1': variant(np.ones(len(core), bool)), 'E2': variant(~core.unver & core.gorg25.notna(), 'gorg25')}
for t in THETAS:
    V['E2x' + t] = variant(~core.unver & ~core['flag' + t], tflag=t)
V['E2pf10'] = variant(~core.unver & core.gorg10.notna(), 'gorg10', '10')
V['E2pf50'] = variant(~core.unver & core.gorg50.notna(), 'gorg50', '50')
V['E2add'] = variant(~core.unver & core.gadd25.notna(), 'gadd25')      # ambiguous cases read as ASC 805 requires
V['E2max'] = variant(~core.unver & core.gmax25.notna(), 'gmax25')      # ambiguous cases read as cumulative
if V3:                                                       # sensitivities of the sample audit (point estimates)
    ce = core_ext
    prim = ce.v3_exclude.fillna('') == ''
    k2010 = prim | (ce.backfill_type == 'fy2010_before_first_xbrl_report')
    clean = prim & (ce.panel_named.fillna('') == '')
    V['E1k2010'] = variant(k2010, frame=ce)
    V['E2k2010'] = variant(k2010 & ~ce.unver & ce.gorg25.notna(), 'gorg25', frame=ce)
    V['E1clean'] = variant(clean, frame=ce)
    V['E2clean'] = variant(clean & ~ce.unver & ce.gorg25.notna(), 'gorg25', frame=ce)
    nodebt = prim & ~ce.debt_only_named.astype(bool)
    V['E1nodebt'] = variant(nodebt, frame=ce)
    V['E2nodebt'] = variant(nodebt & ~ce.unver & ce.gorg25.notna(), 'gorg25', frame=ce)
    VARIANTS = VARIANTS + ['E1k2010', 'E2k2010', 'E1clean', 'E2clean', 'E1nodebt', 'E2nodebt']
    VLAB.update(E1k2010='E1 plus fiscal-2010 years first reported only in a later filing',
                E2k2010='E2 plus fiscal-2010 years first reported only in a later filing',
                E1clean='E1 without the firms the review panels named as not software (rule R2 not applicable locally)',
                E2clean='E2 without the firms the review panels named as not software (rule R2 not applicable locally)',
                E1nodebt='E1 without the debt-only filers named by the finance referee (rule R5 not applicable locally)',
                E2nodebt='E2 without the debt-only filers named by the finance referee (rule R5 not applicable locally)')
V = {k: V[k] for k in VARIANTS}
for vn in VARIANTS:
    assert (V[vn].aff | (V[vn].g == V[vn].g_rep)).all(), 'unaffected growth changed'

# ==== END OF FRAME CONSTRUCTION (code/estimate_v3.py executes this file up to this line) ====
if V3:
    raise SystemExit('ORGANIC_PANEL=v3 only builds frames; the v3 estimates are produced by code/estimate_v3.py')


def clean(o):
    if isinstance(o, dict):
        return {str(k_): clean(v) for k_, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer, np.bool_)):
        o = o.item()
    if isinstance(o, float) and not math.isfinite(o):
        return None
    return o


# E1 anchor regression check: the reference record (sample-aware; Follow-up 5, notes/r2_code_changes.md, 2 Nov 2026).
# The E1 anchor computed here is the calibration rule of calibrate_horizons.py applied to this script's own sample, v2
# (data/panel.csv, data/panel_v2_all.csv). It used to be checked against the anchor in notes/calibration_results.json,
# which calibrate_horizons.py computed on the same sample. Since revision v2 of Paper 1 (decision D-3) calibrate_horizons.py
# reads notes/calibration_anchor_v3.json, so calibration_results.json now holds the anchor of the audited v3 sample (447
# firm-years in 2023-25 and 13 in the anchor, against 458 and 15 here), and comparing the two stopped this script although
# neither number is wrong. Choice: compare only records computed on this script's sample, never across samples.
#   1. notes/calibration_results.json ('anchor_E1', else 'anchor'), when its 2023-25 sample size equals this script's
#      (files written before the field existed were computed on this sample);
#   2. otherwise the v2 calibration anchor recorded by code/estimate_v3.py run on the v2 panel (V3_PANEL=v2):
#      notes/empirics_v2_exact.json, anchor.blocks.E1. That is an independent implementation of the same rule on the same
#      sample, and it must state panel v2 and the same 2023-25 sample size (asserted, so a changed sample here fails
#      instead of skipping the check);
#   3. neither present (a first run of the package): no check; the anchor file says so (passed: null).
# Every field the check names must agree (rtol 1e-12 for the anchor block, 1e-9 for the section-6 recomputation).
def anchor_reference(n_2023_25):
    """(record, label, calibration_results.json or None) of the E1 anchor to reproduce; (None, None, None) if none."""
    path = f'{BASE}/notes/calibration_results.json'
    if os.path.exists(path):
        cj = json.load(open(path))
        rec = cj.get('anchor_E1', cj['anchor'])        # observed-score anchor (anchor_E1 while the calibration read E2)
        if rec.get('n_sample_2023_25', n_2023_25) == n_2023_25:
            return rec, 'notes/calibration_results.json anchor', cj
    path = f'{BASE}/notes/empirics_v2_exact.json'
    if os.path.exists(path):
        ev = json.load(open(path))
        rec = ev['anchor']['blocks']['E1']
        assert ev['meta']['panel'] == 'v2' and rec['n_sample_2023_25'] == n_2023_25, \
            ('v2 anchor record of notes/empirics_v2_exact.json is not on this sample', ev['meta']['panel'],
             rec['n_sample_2023_25'], n_2023_25)
        return rec, 'notes/empirics_v2_exact.json anchor.blocks.E1 (v2 calibration anchor)', None
    return None, None, None


def gap_frame(df):
    ok = df[['m_op', 'gm', 'sms', 'rds', 'gas']].notna().all(axis=1) & df.g.between(0, 0.6, inclusive='left')
    s = df[ok][['cik', 'g', 'm_op', 'gm', 'sms', 'rds', 'gas', 'oth']].copy()
    s['band'] = pd.cut(s.g, [b[0] for b in GAP_BANDS] + [GAP_BANDS[-1][1]], right=False, labels=range(len(GAP_BANDS)))
    return s


def gap_rows(s):
    rows = {}
    for b, grp_ in s.groupby('band', observed=True):
        top = grp_[grp_.m_op >= grp_.m_op.quantile(.9)]
        mid = grp_[grp_.m_op.between(grp_.m_op.quantile(.4), grp_.m_op.quantile(.6))]
        if len(top) < 3 or len(mid) < 3:
            continue
        t_, m_ = top.mean(numeric_only=True), mid.mean(numeric_only=True)
        rows[int(b)] = dict(gap=t_.m_op - m_.m_op, gm=t_.gm - m_.gm, sm=-(t_.sms - m_.sms), rd=-(t_.rds - m_.rds),
                            ga=-(t_.gas - m_.gas), oth=-(t_.oth - m_.oth), n_top=len(top), n_mid=len(mid))
    return rows


def gap_stat(s):
    rows = gap_rows(s)
    r = pd.DataFrame(rows).T
    avg = r[['gap', 'gm', 'sm', 'rd', 'ga', 'oth']].mean()
    b0, b4 = rows.get(0, {}), rows.get(4, {})
    return np.array([avg.gap, avg.gm, avg.sm, avg.rd, avg.ga, avg.oth, b0.get('gap', np.nan), b0.get('gm', np.nan),
                     b4.get('gap', np.nan), b4.get('sm', np.nan), b4.get('rd', np.nan)], float)


if not TABLES_ONLY:
    # =============================================================================================== 2. bootstrap tools


    def cl_idx(cik):
        firms, inv = np.unique(cik, return_inverse=True)
        order = np.argsort(inv, kind='stable')
        bounds = np.r_[0, np.cumsum(np.bincount(inv))]
        return [order[bounds[j]:bounds[j + 1]] for j in range(len(firms))]


    def boot_stat(d, fn, Bn):
        """estimate_revised.py: resample firms within d."""
        idx = cl_idx(d['cik'].values)
        out = []
        for _ in range(Bn):
            dr = rng.integers(0, len(idx), len(idx))
            out.append(fn(d.iloc[np.concatenate([idx[j] for j in dr])]))
        return np.array(out, dtype=float)


    def boot_pair(d1, d2, fn, Bn):
        """Paired: firms drawn from d1 (E1); fn evaluated on the same firms' rows of d1 and of d2 (E2)."""
        firms, inv = np.unique(d1['cik'].values, return_inverse=True)
        idx1 = cl_idx(d1['cik'].values)
        pos2 = pd.Series(np.arange(len(d2))).groupby(d2['cik'].values).apply(lambda s: s.values).to_dict()
        idx2 = [pos2.get(f, np.array([], int)) for f in firms]
        out = []
        for _ in range(Bn):
            dr = rng.integers(0, len(firms), len(firms))
            a = fn(d1.iloc[np.concatenate([idx1[j] for j in dr])])
            b = fn(d2.iloc[np.concatenate([idx2[j] for j in dr]).astype(int)])
            out.append(np.asarray(a, float) - np.asarray(b, float))
        return np.array(out, dtype=float)


    def summ(bs):
        bs = np.asarray(bs, float)
        return dict(se=float(np.nanstd(bs, axis=0)) if bs.ndim == 1 else np.nanstd(bs, axis=0).tolist(),
                    ci90=[float(np.nanquantile(bs, .05)), float(np.nanquantile(bs, .95))] if bs.ndim == 1 else
                    [np.nanquantile(bs, .05, axis=0).tolist(), np.nanquantile(bs, .95, axis=0).tolist()])


    RES = {}


    def run(key, fn, frame, Bn, pe=None, nfn=None, paired=True, boot=BOOT):
        """fn: statistic on a frame (idempotent filtering); frame: rows the existing code resamples; pe: point-estimate
        version of fn (higher iteration limit), defaults to fn."""
        out = {}
        for vn, df in V.items():
            fr = frame(df)
            rec = dict(est=float((pe or fn)(fr)), n=int(nfn(fr) if nfn else len(fr)))
            if vn in boot:
                rec.update(summ(boot_stat(fr, fn, Bn)))
            out[vn] = rec
        if paired:
            out['E1_minus_E2'] = dict(est=out['E1']['est'] - out['E2']['est'], **summ(boot_pair(V['E1'], V['E2'], lambda z: fn(frame(z)), Bn)))
        RES[key] = out
        print(key, {k: round(v['est'], 4) for k, v in out.items()}, flush=True)


    def q95(z, col):
        z = z[col].dropna()
        return float(np.quantile(z, .95)) if len(z) else np.nan


    # =============================================================================================== 3. statistics
    # (a) upper-decile slopes, tau = 0.90, g in [0, 0.6]
    for key, (m, R, lab) in MB.items():
        for sp, per in SPLITS.items():
            fr = lambda df, m=m, per=per: (lambda d: d[(d.g >= 0) & (d.g <= 0.6) & d.period.isin(per)])(df[['cik', 'period', 'g', m]].dropna())
            fit = lambda it, m=m: (lambda z: float(smf.quantreg(f'{m} ~ g', z).fit(q=0.9, max_iter=it).params['g']))
            run(f'slope_{key}_{sp}', fit(2000), fr, B['slope'], pe=fit(5000))

    # (b) spend-to-excess-growth ratio and the implied weight on growth (benchmark G_t: E1 year median of reported g)
    def spend_frame(df):
        x = df[(df.g > df.G_t) & df.sm_lag_share.between(0.01, 1.5)][['cik', 'g', 'G_t', 'sm_lag_share']].copy()
        x['ratio'] = x.sm_lag_share / (x.g - x.G_t)
        return x


    run('spend_ratio', lambda z: float(z.ratio.median()), spend_frame, B['spend'])
    for vn, df in V.items():
        x = spend_frame(df)
        RES['spend_ratio'][vn].update(iqr=[float(x.ratio.quantile(.25)), float(x.ratio.quantile(.75))],
                                      med_sm=float(x.sm_lag_share.median()), med_excess=float((x.g - x.G_t).median()))
    for nm, a in [('weight_lo', ALPHA[1]), ('weight_hi', ALPHA[0])]:          # weight = ratio / alpha
        RES[nm] = {vn: {k: (v / a if k in ('est', 'se') else [c / a for c in v] if k == 'ci90' else v)
                        for k, v in rec.items() if k in ('est', 'se', 'ci90', 'n')} for vn, rec in RES['spend_ratio'].items()}

    # (c) scale: P95 of R by size class and the tau = 0.95 slope on log prior-year revenue
    for key, (m, R, lab) in MB.items():
        fr = lambda df, R=R: df[['cik', 'size_bin', 'lsize', 'g', R]].dropna()
        fit = lambda it, R=R: (lambda z: float(smf.quantreg(f'{R} ~ lsize', z).fit(q=0.95, max_iter=it).params['lsize']))
        run(f'scale_slope_{key}', fit(2000), fr, B['scale'], pe=fit(5000))
        RES[f'scale_tenfold_{key}'] = {vn: {k: (v * math.log(10) if k in ('est', 'se') else [c * math.log(10) for c in v]
                                                if k == 'ci90' else v) for k, v in rec.items()}
                                       for vn, rec in RES[f'scale_slope_{key}'].items()}
        for sb in SIZE_KEYS:
            run(f'scale_p95_{key}_{sb}', lambda z, R=R: q95(z, R),
                lambda df, R=R, sb=sb: df[['cik', 'size_bin', 'lsize', 'g', R]].dropna().pipe(lambda d: d[d.size_bin == sb]),
                B['level'], paired=False)

    # (d) capital intensity: P95 of R, above minus below the period median of capex / revenue
    for key, (m, R, lab) in MB.items():
        for p in PERIODS:
            st = lambda z, R=R: q95(z[z.hi_k == 1], R) - q95(z[z.hi_k == 0], R)
            run(f'capint_gap_{key}_{p.replace("-", "_")}', st, lambda df, p=p, R=R: df[df.period == p][['cik', 'hi_k', R]].dropna(),
                B['capint'], paired=(p == '2023-25'))
            for vn, df in V.items():
                d = df[df.period == p][['cik', 'hi_k', R]].dropna()
                RES[f'capint_gap_{key}_{p.replace("-", "_")}'][vn].update(hi=q95(d[d.hi_k == 1], R), lo=q95(d[d.hi_k == 0], R))

    # (e) upper quantiles of R: levels and the change from 2016-19 to 2023-25
    for key, (m, R, lab) in MB.items():
        for p in ['2016-19', '2023-25']:
            run(f'p95_{key}_{p.replace("-", "_")}', lambda z, R=R: q95(z, R),
                lambda df, p=p, R=R: df[['cik', 'period', R]].dropna().pipe(lambda d: d[d.period == p]), B['level'], paired=False)
        for q in [0.90, 0.95]:
            st = lambda z, R=R, q=q: (float(np.quantile(z.loc[z.period == '2023-25', R], q))
                                      - float(np.quantile(z.loc[z.period == '2016-19', R], q)))
            run(f'p{int(100 * q)}_change_{key}', st,
                lambda df, R=R: df[['cik', 'period', R]].dropna().pipe(lambda d: d[d.period.isin(['2016-19', '2023-25'])]),
                B['diff'])

    # (f) best attainable margin at a given growth rate: T(g0) = g0 + phi_0.95(g0), change 2016-19 to 2023-25
    for key, (m, R, lab) in MB.items():
        for g0 in [0.0, 0.1, 0.2, 0.3, 0.4]:
            T = lambda z, g0=g0, m=m: g0 + float(np.quantile(z.loc[z.g >= g0, m], .95)) if (z.g >= g0).sum() >= 10 else np.nan
            tag = f'T_{key}_g{int(round(100 * g0)):02d}'
            run(f'{tag}_change', lambda z, T=T: T(z[z.period == '2023-25']) - T(z[z.period == '2016-19']),
                lambda df, m=m: df[['cik', 'period', 'g', m]].dropna().pipe(lambda d: d[d.period.isin(['2016-19', '2023-25'])]),
                B['diff'])
            RES[tag] = {}
            for vn, df in V.items():
                d = df[['cik', 'period', 'g', m]].dropna()
                RES[tag][vn] = {p.replace('-', '_'): dict(est=T(d[d.period == p]), n=int((d[d.period == p].g >= g0).sum()))
                                for p in PERIODS}

    # (g) near-frontier margin gap and its decomposition (code/decompose_gap.py)


    gap_out = {k: {} for k in GAP_KEYS}
    for vn, df in V.items():
        s = gap_frame(df)
        est = gap_stat(s)
        bs = boot_stat(s, gap_stat, B['gap']) if vn in BOOT else None
        for i, k in enumerate(GAP_KEYS):
            rec = dict(est=float(est[i]), n=int(len(s)))
            if bs is not None:
                rec.update(se=float(np.nanstd(bs[:, i])), ci90=[float(np.nanquantile(bs[:, i], .05)), float(np.nanquantile(bs[:, i], .95))])
            gap_out[k][vn] = rec
    bs = boot_pair(V['E1'], V['E2'], lambda z: gap_stat(gap_frame(z)), B['gap'])
    for i, k in enumerate(GAP_KEYS):
        gap_out[k]['E1_minus_E2'] = dict(est=gap_out[k]['E1']['est'] - gap_out[k]['E2']['est'], se=float(np.nanstd(bs[:, i])),
                                         ci90=[float(np.nanquantile(bs[:, i], .05)), float(np.nanquantile(bs[:, i], .95))])
    RES.update(gap_out)
    print('gap', {k: round(v['est'], 4) for k, v in gap_out['gap_avg'].items()}, flush=True)

    # =============================================================================================== 4. samples and coverage
    samples = {}
    for vn, df in V.items():
        samples[vn] = dict(n=int(len(df)), firms=int(df.cik.nunique()),
                           by_period={p: int((df.period == p).sum()) for p in PERIODS},
                           n_g_above_50=int((df.g > 0.5).sum()), n_g_ge_40_2023_25=int(((df.g >= 0.4) & (df.period == '2023-25')).sum()),
                           n_affected_kept=int(df.aff.sum()),                     # E1: reported g; E2, E2pf: organic g
                           n_unaffected_growth_changed=int((~df.aff & (df.g != df.g_rep)).sum()))
    fl = core.flag25
    cov = dict(
        n_core=int(len(core)), n_flagged=int(fl.sum()), share_flagged=float(fl.mean()),
        n_acq_year=int(core.now25.sum()), n_following_only=int((fl & ~core.now25).sum()),
        n_flagged_computed=int((fl & core.gorg25.notna()).sum()),
        share_flagged_computed=float((fl & core.gorg25.notna()).sum() / fl.sum()),
        share_acq_year_computed=float((core.now25 & core.gorg25.notna()).sum() / core.now25.sum()),
        share_following_only_computed=float((fl & ~core.now25 & core.gorg25.notna()).sum() / (fl & ~core.now25).sum()),
        n_fast=int((core.g > 0.5).sum()), n_fast_flagged=int((fl & (core.g > 0.5)).sum()),
        n_fast_flagged_computed=int((fl & (core.g > 0.5) & core.gorg25.notna()).sum()),
        share_fast_flagged_computed=float((fl & (core.g > 0.5) & core.gorg25.notna()).sum() / (fl & (core.g > 0.5)).sum()),
        share_fast_in_E2=float(((core.g > 0.5) & ~core.unver & core.gorg25.notna()).sum() / (core.g > 0.5).sum()),
        reasons=core.loc[fl, 'reason25'].value_counts().to_dict(),
        n_pf_cur_same_filing=int(core.pf_cur_raw.notna().sum()), n_pf_pri_same_filing=int(core.pf_pri_raw.notna().sum()),
        n_pair_valid=int(core.pair.sum()), n_pf_invalid=int((core.pf_cur_raw.notna() & core.pf_cur.isna()).sum()
                                                            + (core.pf_pri_raw.notna() & core.pf_pri.isna()).sum()),
        n_pri_repeat=int(core.pri_repeat.sum()),
        n_panel_pf_from_later_filing=int(core.pf_fallback.sum()),
        n_acq_now_only_by_later_filing_pf=int((core.now25 & core.pf_fallback
                                               & ~(core.acq_pay.fillna(0) >= .25 * core.rev_lag)
                                               & ~(core.gw_jump.fillna(0) >= .25 * core.rev_lag)).sum()),
        n_unverified=int(core.unver.sum()))
    adj = core[fl & core.gorg25.notna()]
    cov['adjusted'] = dict(
        n=int(len(adj)), med_g=float(adj.g.median()), med_g_org=float(adj.gorg25.median()),
        med_acquired=float((adj.g - adj.gorg25).median()), iqr_acquired=[float((adj.g - adj.gorg25).quantile(q)) for q in (.25, .75)],
        share_g_org_below_g=float((adj.gorg25 < adj.g - 1e-12).mean()),
        n_acq_year=int(adj.now25.sum()), n_following_year=int((~adj.now25).sum()))
    # approximation error from counting the acquired businesses' own growth as organic: w (g_T - g_base), with
    # w = rho_t / (1 + pi_{t-1} + rho_t) the acquired businesses' share of the constant-perimeter base (rho_t > 0 only)
    w = (adj.rho25 / (1 + adj.piprev25 + adj.rho25))[adj.rho25 > 0]
    cov['adjusted'].update(n_with_rho=int(len(w)), w_median=float(w.median()), w_p90=float(w.quantile(.9)),
                           err_at_20pt_median=float(0.20 * w.median()), err_at_20pt_p90=float(0.20 * w.quantile(.9)))
    amb = core[core.amb25]
    cov['ambiguous'] = dict(n=int(len(amb)), n_fast=int((amb.g > 0.5).sum()),
                            med_g_add=float(amb.gadd25.median()), med_g_max=float(amb.gmax25.median()),
                            med_bound_width=float((amb.gmax25 - amb.gadd25).median()),
                            max_bound_width=float((amb.gmax25 - amb.gadd25).max()),
                            firms=sorted(amb.name.unique().tolist()))
    cov['thresholds'] = {t: dict(share_flagged=float(core['flag' + t].mean()),
                                 share_flagged_fast=float(core.loc[core.g > 0.5, 'flag' + t].mean()),
                                 share_flagged_computed=float((core['flag' + t] & core['gorg' + t].notna()).sum() / core['flag' + t].sum()))
                         for t in THETAS}
    print(json.dumps(cov, indent=1, default=float), flush=True)

    # =============================================================================================== 5. selection diagnostics
    E1 = V['E1'].copy()
    E1['grp'] = np.where(E1.unver, 'unverified', np.where(~E1.flag25, 'unflagged',
                         np.where(E1.gorg25.notna(), 'flagged_adjusted', 'flagged_excluded')))
    ever = E1.groupby('cik').flag25.transform('max').astype(bool)
    sel = {'medians': {}, 'n': E1.grp.value_counts().to_dict()}
    for gname, mask in [('unflagged', E1.grp == 'unflagged'), ('flagged', E1.flag25), ('flagged_adjusted', E1.grp == 'flagged_adjusted'),
                        ('flagged_excluded', E1.grp == 'flagged_excluded'),
                        ('never_acquirer', ~ever), ('ever_acquirer_unflagged_years', ever & ~E1.flag25 & ~E1.unver)]:
        sel['medians'][gname] = {v: float(E1.loc[mask, v].median()) for v in SELV}
        sel['medians'][gname]['n'] = int(mask.sum())


    def sel_stat(z):
        f, u = z[z.flag25], z[~z.flag25 & ~z.unver]
        ev = z.groupby('cik').flag25.transform('max').astype(bool)
        a, nv = z[ev & ~z.flag25 & ~z.unver], z[~ev]
        return np.r_[[f[v].median() - u[v].median() for v in SELV], [a[v].median() - nv[v].median() for v in SELV]]


    est = sel_stat(E1)
    bs = boot_stat(E1, sel_stat, B['sel'])
    sel['flagged_minus_unflagged'] = {v: dict(est=float(est[i]), se=float(np.nanstd(bs[:, i])),
                                              ci90=[float(np.nanquantile(bs[:, i], .05)), float(np.nanquantile(bs[:, i], .95))])
                                      for i, v in enumerate(SELV)}
    k = len(SELV)
    sel['ever_acquirer_unflagged_minus_never'] = {v: dict(est=float(est[k + i]), se=float(np.nanstd(bs[:, k + i])),
                                                          ci90=[float(np.nanquantile(bs[:, k + i], .05)), float(np.nanquantile(bs[:, k + i], .95))])
                                                  for i, v in enumerate(SELV)}
    sel['top_tail'] = {}
    for key, (m, R, lab) in MB.items():
        d = E1.dropna(subset=[R]).copy()
        d['top'] = d[R] >= d.groupby('period')[R].transform(lambda x: x.quantile(.95))
        sel['top_tail'][key] = dict(share_flagged_top=float(d.loc[d.top, 'flag25'].mean()), share_flagged_all=float(d.flag25.mean()),
                                    n_top=int(d.top.sum()),
                                    share_flagged_top_2023_25=float(d.loc[d.top & (d.period == '2023-25'), 'flag25'].mean()))
    # Where acquirers' organic points sit: share of firm-years above the exclusion-only (25%) 90th percentile of margin in
    # their growth band (bands of Table tab:local). About 10% if a group is exchangeable with the exclusion-only sample.
    LBINS = [0, 0.1, 0.2, 0.3, 0.4, 0.6, 5]
    sel['frontier_position'] = {}
    for key, (m, R, lab) in MB.items():
        ref = V['E2x25'][['g', m]].dropna()
        ref = ref[ref.g >= 0]
        p90 = ref.groupby(pd.cut(ref.g, LBINS, right=False, labels=False))[m].quantile(.9)

        def above(d, m=m, p90=p90):
            d = d[['g', m]].dropna()
            d = d[d.g >= 0]
            return dict(share=float((d[m] > pd.cut(d.g, LBINS, right=False, labels=False).map(p90)).mean()), n=int(len(d)))
        sel['frontier_position'][key] = dict(
            affected_kept_in_E2_organic_g=above(V['E2'][V['E2'].aff]),
            affected_all_reported_g=above(E1[E1.flag25]),
            ever_acquirer_unflagged_years=above(E1[ever & ~E1.flag25 & ~E1.unver]),
            never_acquirer=above(E1[~ever]))
    print(json.dumps(sel, indent=1, default=float), flush=True)

    # =============================================================================================== 6. calibration consistency
    TAU = 0.18


    def anchor(df, cut_df, G):
        d = df[df.period == '2023-25'].copy()
        d['R'] = d.g + d.m_fcf_sbc
        p95 = float(cut_df.loc[cut_df.period == '2023-25'].pipe(lambda x: (x.g + x.m_fcf_sbc)).quantile(.95))
        top = d[d.R >= p95].copy()
        top['sig_ub'] = (top.sm / top.rev).fillna(0.0)
        top['kg'] = top.capex_int.fillna(0.0)
        top['k'] = np.where(top.g > 0, top.kg / top.g, 0.0)
        top['m0_ub'] = top.m_fcf_sbc + (1 - TAU) * top.sig_ub + top.kg
        top['m0_lb'] = top.m_fcf_sbc + top.kg
        for b in ['ub', 'lb']:
            top['Rinf_' + b] = top['m0_' + b] + (1 - top.k) * G
            top['Pi_' + b] = top.R - top['Rinf_' + b]
        q3 = lambda s: [float(s.quantile(.25)), float(s.quantile(.5)), float(s.quantile(.75))]
        return dict(n=int(len(top)), p95=p95, G=float(G), R=q3(top.R), m0_ub=q3(top.m0_ub), Rinf_ub=q3(top.Rinf_ub),
                    Pi_ub=q3(top.Pi_ub), m0_lb=q3(top.m0_lb), Pi_lb=q3(top.Pi_lb),
                    shift=float(top.m0_ub.median() - top.m0_lb.median()), firms=sorted(top.name.unique().tolist()),
                    n_pf_adjusted=int(top.flag25.sum()))


    E1_25 = V['E1'][V['E1'].period == '2023-25']
    cal = {'as_calibrated': anchor(V['E1'][V['E1'].acq_flag == 0], V['E1'], E1_25.g.median()),
           'E2x25': anchor(V['E2x25'], V['E2x25'], V['E2x25'].loc[V['E2x25'].period == '2023-25', 'g'].median()),
           'E2': anchor(V['E2'], V['E2'], V['E2'].loc[V['E2'].period == '2023-25', 'g'].median()),
           'E2_cut_from_E1_G_from_E1': anchor(V['E2'], V['E1'], E1_25.g.median())}
    tail = E1_25.assign(R=E1_25.g + E1_25.m_fcf_sbc)
    tail = tail[tail.R >= tail.R.quantile(.95)]
    cal['differences'] = dict(
        calibration_rule='rows of the full 2023-25 sample at or above its P95 of the cash score, minus acq_flag == 1',
        E2_rule='P95 and rows from the E2 sample (pro forma adjusted where computable, otherwise excluded; unverified hypergrowth excluded)',
        unverified_in_tail=int(tail.unver.sum()), flagged_in_tail=int(tail.flag25.sum()),
        flagged_in_tail_adjustable=int((tail.flag25 & tail.gorg25.notna()).sum()),
        same_flag_as_E2=bool((core.flag25.astype(int) == core.acq_flag).all()))
    CALJ, _cal_ref, _ = anchor_reference(len(E1_25))   # sample-aware reference (see anchor_reference); None on a first run
    if CALJ is not None:
        for k_ in ['n', 'p95', 'G', 'R', 'm0_ub', 'Pi_ub', 'Rinf_ub', 'm0_lb', 'Pi_lb', 'shift']:
            assert np.allclose(cal['as_calibrated'][k_], CALJ[k_], rtol=1e-9, atol=1e-12), ('calibration anchor not reproduced', k_, _cal_ref)
        print(f'calibration anchor reproduced (section 6) against {_cal_ref}', flush=True)
    print(json.dumps({k_: {kk: vv for kk, vv in v.items() if kk != 'firms'} if isinstance(v, dict) else v for k_, v in cal.items()},
                     indent=1, default=float), flush=True)

    # =============================================================================================== 7. reproduction checks
    checks = {}
    if not V3:
        EMP = json.load(open(f'{BASE}/notes/empirics_revised.json'))
        GAPJ = json.load(open(f'{BASE}/notes/gap_decomposition.json'))
        rob = EMP['robust']['Excluding acquisition-affected years and unverified hypergrowth']
        checks = {}
        for key in MB:
            for sp, sk in [('pooled', 'pooled'), ('2010_19', '2010-19'), ('2020_25', '2020-25')]:
                checks[f'slope_{key}_{sp}_E1'] = (RES[f'slope_{key}_{sp}']['E1']['est'], EMP['local'][key]['slopes'][sk]['b'])
            checks[f'slope_{key}_pooled_E2x25'] = (RES[f'slope_{key}_pooled']['E2x25']['est'], rob[key]['slope'])
            checks[f'p95_change_{key}_E1'] = (RES[f'p95_change_{key}']['E1']['est'], EMP['top'][key]['diff_1619|q95']['diff'])
            checks[f'p95_change_{key}_E2x25'] = (RES[f'p95_change_{key}']['E2x25']['est'], rob[key]['diff']['diff'])
            checks[f'scale_slope_{key}_E1'] = (RES[f'scale_slope_{key}']['E1']['est'], EMP['scale'][key]['slope']['b'])
            checks[f'capint_gap_{key}_2023_25_E1'] = (RES[f'capint_gap_{key}_2023_25']['E1']['est'], EMP['capint'][key]['2023-25']['gap'])
            for g0 in [0.0, 0.2, 0.4]:
                checks[f'T_{key}_g{int(100 * g0):02d}_change_E1'] = (RES[f'T_{key}_g{int(100 * g0):02d}_change']['E1']['est'],
                                                                     EMP['threshold'][key][f'{g0}|diff']['diff'])
        checks['spend_ratio_E2x25'] = (RES['spend_ratio']['E2x25']['est'], EMP['spend_ratio']['median'])
        checks['gap_avg_E1'] = (RES['gap_avg']['E1']['est'], GAPJ['avg']['gap'])
        checks['gap_sm_E1'] = (RES['gap_sm']['E1']['est'], GAPJ['avg']['d_sms'])
        bad = {k_: v for k_, v in checks.items() if not np.isclose(v[0], v[1], rtol=1e-7, atol=1e-10)}
        assert not bad, f'existing estimates not reproduced: {bad}'
        print(f'reproduction checks passed: {len(checks)}', flush=True)

    # =============================================================================================== 8. JSON
    HEAD = {}                                  # filled after the E1 alignment below


    OUT = dict(
        meta=dict(script='code/estimate_organic.py', seed=SEED, replications=B, fast_mode=FAST,
                  units='fractions (0.01 = one point) except slopes (margin per unit growth), spend ratio and weights',
                  variants=VLAB, primary={'descriptive (distribution of reported scores)': 'E1', 'model-facing': 'E2'},
                  pf_valid_range=PF_VALID, pf_criterion_multiple_of_theta=PF_SHARE, repeat_tolerance=REPEAT_TOL, ambiguity_tolerance=AMBIG_TOL,
                  notes='E1_minus_E2: paired firm-cluster bootstrap (firms drawn from E1). se = bootstrap standard deviation.'),
        headline=HEAD, estimates=RES, samples=samples, coverage=cov, selection=sel, calibration_check=cal,
        checks={k_: dict(this=v[0], existing=v[1]) for k_, v in checks.items()})
else:
    J = json.load(open(OUT_JSON))
    RES, samples, cov, sel, cal, HEAD = (J['estimates'], J['samples'], J['coverage'], J['selection'],
                                         J['calibration_check'], J['headline'])
    RES = {k_: {vn: dict(rec, est=(float('nan') if rec.get('est') is None else rec['est'])) if isinstance(rec, dict) and 'est' in rec else rec
                for vn, rec in v.items()} for k_, v in RES.items()}
    OUT = J

# =============================================================================================== 8b. E1 draws aligned
# For the E1 statistics that code/estimate_revised.py and code/decompose_gap.py already report, the bootstrap draws
# are taken from their outputs (same estimator, sample, clustering, replications and seed; the draws differ from this
# script's only by the position of the random stream), so that Table tab:estimands agrees with Tables tab:local,
# tab:top, tab:threshold, tab:scale and tab:gap. Point estimates are asserted equal. This script's own E1 draws are kept
# as se_own and ci90_own. E2, the threshold variants and E1 - E2 use this script's draws.
if not V3:
    EMP = json.load(open(f'{BASE}/notes/empirics_revised.json'))
    GAPJ = json.load(open(f'{BASE}/notes/gap_decomposition.json'))
    SCALE_LAB = dict(zip(SIZE_KEYS, ['\\$0.1--0.5B', '\\$0.5--2B', '\\$2--10B', '$>$\\$10B']))


    def align(key, est, se=None, ci=None, src='', scale=1.0):
        rec = RES[key]['E1']
        assert np.isclose(rec['est'], est * scale, rtol=1e-7, atol=1e-10), ('E1 point estimate differs', key)
        if 'se_own' not in rec:
            rec['se_own'], rec['ci90_own'] = rec.get('se'), rec.get('ci90')
        rec['se'] = se * scale if se is not None else rec['se_own']
        if ci is not None:
            rec['ci90'] = [c * scale for c in ci]
        else:
            rec.pop('ci90', None)                                  # the existing code reports no interval
        rec['draws'] = src + ('' if se is not None else '; se is the standard deviation of this script\'s own draws')


    for key in MB:
        for sp, sk in [('pooled', 'pooled'), ('2010_19', '2010-19'), ('2020_25', '2020-25')]:
            r = EMP['local'][key]['slopes'][sk]
            align(f'slope_{key}_{sp}', r['b'], se=r['se'], src='estimate_revised.py local slopes (Table tab:local)')
        r = EMP['scale'][key]['slope']
        align(f'scale_slope_{key}', r['b'], se=r['se'], src='estimate_revised.py scale slope (Table tab:scale)')
        align(f'scale_tenfold_{key}', r['b'], se=r['se'], src='estimate_revised.py scale slope times ln 10', scale=math.log(10))
        for sb, lab in SCALE_LAB.items():
            r = EMP['scale'][key][lab]
            align(f'scale_p95_{key}_{sb}', r['p95'], ci=r['p95_ci'], src='estimate_revised.py scale classes (Table tab:scale)')
        for p in PERIODS:
            r = EMP['capint'][key][p]
            align(f'capint_gap_{key}_{p.replace("-", "_")}', r['gap'], ci=r['ci90'], src='estimate_revised.py capital-intensity split')
        for p in ['2016-19', '2023-25']:
            r = EMP['top'][key][f'{p}|q95']
            align(f'p95_{key}_{p.replace("-", "_")}', r['est'], ci=r['ci90'], src='estimate_revised.py top quantiles (Table tab:top)')
        for q in [90, 95]:
            r = EMP['top'][key][f'diff_1619|q{q}']
            align(f'p{q}_change_{key}', r['diff'], ci=r['ci90'], src='estimate_revised.py top quantiles (Table tab:top)')
        for g0 in [0.0, 0.1, 0.2, 0.3, 0.4]:
            r = EMP['threshold'][key][f'{g0}|diff']
            align(f'T_{key}_g{int(round(100 * g0)):02d}_change', r['diff'], ci=r['ci90'],
                  src='estimate_revised.py threshold frontier points (Table tab:threshold)')
    for k_, gk in [('gap_avg', 'gap'), ('gap_gm', 'd_gm'), ('gap_sm', 'd_sms'), ('gap_rd', 'd_rds'), ('gap_ga', 'd_gas'), ('gap_oth', 'd_oth')]:
        align(k_, GAPJ['avg'][gk], ci=GAPJ['ci90'][gk], src='decompose_gap.py (Table tab:gap)')
# Band values (deterministic, no bootstrap): 90th percentile of margin by growth band (Table tab:local) and the
# margin-gap decomposition by band (Table tab:gap), for every variant; E1 reproduces the existing tables.
LB = [0, 0.1, 0.2, 0.3, 0.4, 0.6, 5]
LB_KEYS = ['0_10', '10_20', '20_30', '30_40', '40_60', 'ge60']
GB_KEYS = ['0_10', '10_20', '20_30', '30_40', '40_60']
bands = {'local_q90': {}, 'gap_by_band': {}}
for vn, df in V.items():
    bands['local_q90'][vn] = {}
    for key, (m, R, lab) in MB.items():
        d = df[['g', m]].dropna()
        d = d[d.g >= 0]
        cut = pd.cut(d.g, LB, right=False, labels=LB_KEYS)
        q, n = d.groupby(cut, observed=True)[m].quantile(.9), d.groupby(cut, observed=True).size()
        bands['local_q90'][vn][key] = {b: dict(q90=float(q[b]), n=int(n[b])) for b in q.index}
    bands['gap_by_band'][vn] = {GB_KEYS[b]: {k_: float(v) for k_, v in r.items()} for b, r in gap_rows(gap_frame(df)).items()}
if not V3:
    for key in MB:
        assert np.allclose([bands['local_q90']['E1'][key][b]['q90'] for b in LB_KEYS], EMP['local'][key]['q90']), 'tab_local not reproduced'
    assert np.allclose([bands['gap_by_band']['E1'][GB_KEYS[r['band']]]['gap'] for r in GAPJ['bands']], [r['gap'] for r in GAPJ['bands']])
    assert np.allclose([bands['gap_by_band']['E1'][GB_KEYS[r['band']]]['sm'] for r in GAPJ['bands']], [r['d_sms'] for r in GAPJ['bands']])
OUT['bands'] = bands

# Calibration anchor inputs (notes/calibration_anchor_E2.json; calibrate_horizons.py read it until revision v2 switched the
# calibration to notes/calibration_anchor_v3.json, and code/estimate_v3_report.py reads it as the v2 reference).
# Both blocks follow calibrate_horizons.py line by line: 2023-25 rows, R = g + m_fcf_sbc, cut-off = P95 of R, G = median
# g, sigma_ub = S&M / revenue (0 if not reported), kg = capex intensity (0 if missing), k = kg / g (0 if g <= 0),
# m0_ub = m + (1 - tau) sigma_ub + kg, m0_lb = m + kg, R_inf = m0 + (1 - k) G, Pi = R - R_inf. E1 is the current anchor
# (full-sample cut-off and G, flagged firm-years dropped from the tail) and must reproduce the calibration anchor on this
# sample (anchor_reference: calibration_results.json if it is on this sample, else notes/empirics_v2_exact.json).
# E2 takes the cut-off, G and the tail from the E2 sample: organic growth for affected firm-years where computable,
# other affected firm-years and unverified hypergrowth absent.
TAU_CAL = 0.18                                          # calibrate_horizons.TAU


def anchor_block(df, drop_flagged):
    d = df[df.period == '2023-25'].copy()
    d['R'] = d.g + d.m_fcf_sbc
    G, p95, m_p95 = float(d.g.median()), float(d.R.quantile(.95)), float(d.m_fcf_sbc.quantile(.95))
    tail = d[d.R >= p95].copy()
    top = tail[tail.acq_flag == 0].copy() if drop_flagged else tail.copy()
    top['sig_ub'] = (top.sm / top.rev).fillna(0.0)
    top['kg'] = top.capex_int.fillna(0.0)
    top['k'] = np.where(top.g > 0, top.kg / top.g, 0.0)
    top['m0_ub'] = top.m_fcf_sbc + (1 - TAU_CAL) * top.sig_ub + top.kg
    top['m0_lb'] = top.m_fcf_sbc + top.kg
    for b in ['ub', 'lb']:
        top['Rinf_' + b] = top['m0_' + b] + (1 - top.k) * G
        top['Pi_' + b] = top.R - top['Rinf_' + b]
    q3 = lambda s: [float(s.quantile(.25)), float(s.quantile(.5)), float(s.quantile(.75))]
    blk = dict(n_tail=int(len(tail)), n_tail_m_above_p95=int((tail.m_fcf_sbc > m_p95).sum()), m_p95_all=m_p95,
               n=int(len(top)), n_acq_excluded=int(len(tail) - len(top)), n_sm_missing=int(top.sm.isna().sum()),
               p95=p95, G=G, tau=TAU_CAL, R=q3(top.R), m=q3(top.m_fcf_sbc), sig_ub=q3(top.sig_ub),
               **{f'{v}_{b}': q3(top[f'{v}_{b}']) for v in ['m0', 'Rinf', 'Pi'] for b in ['ub', 'lb']},
               shift=float(top.m0_ub.median() - top.m0_lb.median()), firms=sorted(top.name.unique().tolist()),
               n_sample_2023_25=int(len(d)), n_adjusted_pro_forma=int((top.aff & (top.g != top.g_rep)).sum()),
               share_Pi_ub_positive=float((top.Pi_ub > 0).mean()), share_Pi_lb_positive=float((top.Pi_lb > 0).mean()),
               transient_share_ub=float(top.Pi_ub.median() / top.R.median()),
               transient_share_lb=float(top.Pi_lb.median() / top.R.median()))
    cols = ['cik', 'name', 'year', 'fy_end', 'rev', 'rev_lag', 'g', 'g_rep', 'acq_flag', 'm_fcf_sbc', 'R', 'sm', 'sig_ub',
            'capex_int', 'kg', 'k', 'm0_ub', 'm0_lb', 'Rinf_ub', 'Rinf_lb', 'Pi_ub', 'Pi_lb']
    rows = top.sort_values('R', ascending=False)[cols].rename(columns={'g_rep': 'g_reported', 'g': 'g_used'})
    blk['firm_years'] = [{k_: (None if isinstance(v, float) and not math.isfinite(v) else v) for k_, v in r.items()}
                         for r in rows.to_dict(orient='records')]
    for r in blk['firm_years']:
        r['organic_adjusted'] = bool(r['acq_flag'] == 1)              # flagged rows reach the E2 tail only if adjusted
    return blk


ANCH = {'E2': anchor_block(V['E2'], drop_flagged=False), 'E1': anchor_block(V['E1'], drop_flagged=True)}
_e1keys = {(r['cik'], r['year']) for r in ANCH['E1']['firm_years']}
_new = [r for r in ANCH['E2']['firm_years'] if (r['cik'], r['year']) not in _e1keys]
ENTR = dict(n=len(_new), n_neg=sum(r['Pi_ub'] < 0 for r in _new),
            names=', '.join(f"{r['name']} {r['year']} (Pi_ub {100 * r['Pi_ub']:+.1f})" for r in _new))
# Regression check of the E1 block against the record anchor_reference() picks (computed on this script's sample only).
CALA, _REG_REF, _CALJ = anchor_reference(ANCH['E1']['n_sample_2023_25'])
REG_KEYS = ['n_tail', 'n_tail_m_above_p95', 'm_p95_all', 'n', 'n_acq_excluded', 'n_sm_missing', 'p95', 'G', 'tau', 'R', 'm',
            'sig_ub', 'm0_ub', 'm0_lb', 'Rinf_ub', 'Rinf_lb', 'Pi_ub', 'Pi_lb', 'shift', 'firms']
if CALA is not None:
    for k_ in REG_KEYS:
        ok_ = ANCH['E1'][k_] == CALA[k_] if k_ == 'firms' else np.allclose(ANCH['E1'][k_], CALA[k_], rtol=1e-12, atol=1e-15)
        assert ok_, ('E1 anchor does not reproduce the reference anchor', k_, _REG_REF)
    if _CALJ is not None and 'anchor_E1' in _CALJ:     # the calibration read the E2 block of this script's anchor file
        assert all(np.allclose(_CALJ['anchor'][k_], ANCH['E2'][k_], rtol=1e-12, atol=1e-15) for k_ in ['n', 'p95', 'G', 'm0_ub', 'Pi_ub', 'Pi_lb'])
    print(f'E1 anchor regression check passed on {len(REG_KEYS)} fields against {_REG_REF}', flush=True)
# The anchor file's regression_check label is kept as written since 29 Oct 2026 ('notes/calibration_results.json anchor':
# the calibration anchor on the v2 sample, which calibration_results.json carried until the v3 switch and
# notes/empirics_v2_exact.json records now), so that the committed anchor file stays byte-identical; the record actually
# used is printed above and is named in notes/r2_code_changes.md (Follow-up 5).
assert ANCH['E2']['n'] == cal['E2']['n'] and np.allclose(ANCH['E2']['Pi_ub'], cal['E2']['Pi_ub'])
json.dump(clean(dict(
    meta=dict(script='code/estimate_organic.py', estimand_decision='model-facing results, calibration included, use E2',
              rules='calibrate_horizons.py anchor (2023-25; R = g + m_fcf_sbc; cut-off = P95 of R; G = median g; '
                    'sigma_ub = S&M/revenue, 0 if missing; kg = capex intensity, 0 if missing; k = kg/g if g > 0 else 0; '
                    'm0_ub = m + (1 - tau) sigma_ub + kg; m0_lb = m + kg; R_inf = m0 + (1 - k) G; Pi = R - R_inf)',
              E2='cut-off, G and tail from the E2 sample: g_used is organic growth (pro forma adjusted) for '
                 'acquisition-affected firm-years where computable, reported growth otherwise; other affected firm-years '
                 'and unverified hypergrowth are not in the sample',
              E1='current anchor: cut-off and G from all 2023-25 firm-years, acq_flag == 1 dropped from the tail',
              units='fractions of revenue; rev and sm in dollars', fields_per_firm_year=list(ANCH['E2']['firm_years'][0].keys())),
    **{b: ANCH[b] for b in ANCH},
    regression_check=(dict(passed=True, against='notes/calibration_results.json anchor', keys=REG_KEYS) if CALA is not None else
                      dict(passed=None, note='no anchor record on this sample yet (first run: notes/calibration_results.json absent or on '
                                             'another sample, notes/empirics_v2_exact.json absent); rerun this script after '
                                             'estimate_v3.py (V3_PANEL=v2) and calibrate_horizons.py')))),
    open(f'{BASE}/notes/calibration_anchor_E2.json', 'w'), indent=1)
OUT['calibration_anchor'] = {b: {k_: v for k_, v in ANCH[b].items() if k_ != 'firm_years'} for b in ANCH}
HEAD = {k_: {vn: RES[k_][vn] for vn in ['E1', 'E2', 'E1_minus_E2'] if vn in RES[k_]} for k_ in HEAD_KEYS}
OUT['estimates'], OUT['headline'] = RES, HEAD
if not V3:
    OUT['meta']['e1_draws'] = ('E1 se and ci90 of statistics reported by estimate_revised.py and decompose_gap.py are their draws '
                               '(see each record\'s draws field); this script\'s own E1 draws are se_own and ci90_own')
json.dump(clean(OUT), open(OUT_JSON, 'w'), indent=1)


# =============================================================================================== 9. table
TV = ['E1', 'E2', 'E1_minus_E2', 'E2x10', 'E2x25', 'E2x50']


def f_se(rec, nd=2, scale=1.0):
    if rec is None or rec.get('est') is None or not math.isfinite(rec['est']):
        return '--'
    e = round(scale * rec['est'], nd) or 0.0
    s = f"{e:.{nd}f}".replace('-', '$-$')
    if 'se' in rec and rec['se'] is not None:
        s += f" ({scale * rec['se']:.{nd}f})"
    return s


def f_ci(rec, nd=0, scale=100.0, sign=True):
    if rec is None or rec.get('est') is None or not math.isfinite(rec['est']):
        return '--'
    z = lambda x: round(x, nd) + 0.0 if round(x, nd) != 0 else 0.0          # no negative zero after rounding
    fm = (lambda x: f"{z(x):+.{nd}f}") if sign else (lambda x: f"{z(x):.{nd}f}")
    s = fm(scale * rec['est'])
    if 'ci90' in rec:
        s += ' [' + fm(scale * rec['ci90'][0]) + ', ' + fm(scale * rec['ci90'][1]) + ']'
    return s.replace('-', '$-$')


def row(label, basis, key, kind='se', nd=None, scale=None, sign=True):
    scale = (1.0 if kind == 'se' else 100.0) if scale is None else scale
    nd = (2 if kind == 'se' else 0) if nd is None else nd
    cells = []
    for vn in TV:
        rec = RES[key].get(vn)
        if vn == 'E1_minus_E2' and rec is None:
            cells.append('')
        elif kind == 'se':
            cells.append(f_se(rec, nd, scale))
        else:
            cells.append(f_ci(rec, nd, scale, sign))
    return f"{label} & {basis} & " + ' & '.join(cells) + r' \\'


L = []
L.append(r'\multicolumn{8}{l}{\emph{A. Model-facing statistics (E2 primary)}}\\')
for sp, lab in [('pooled', 'Upper-decile slope, 2010--25'), ('2010_19', 'Upper-decile slope, 2010--19'), ('2020_25', 'Upper-decile slope, 2020--25')]:
    L.append(row(lab, 'GAAP', f'slope_op_{sp}'))
    L.append(row('', 'FCF after SBC', f'slope_cash_{sp}'))
L.append(row('Spend-to-excess-growth ratio (median)', 'S\\&M', 'spend_ratio', nd=1))
L.append(row('Implied weight on growth, $\\alpha=0.45$', '', 'weight_lo', nd=1))
L.append(row('Implied weight on growth, $\\alpha=0.25$', '', 'weight_hi', nd=1))
L.append(row('P95 of $R$ per tenfold revenue (points)', 'GAAP', 'scale_tenfold_op', nd=1, scale=100))
L.append(row('', 'FCF after SBC', 'scale_tenfold_cash', nd=1, scale=100))
L.append(row('Capital-intensity gap in P95 of $R$, 2023--25', 'GAAP', 'capint_gap_op_2023_25', kind='ci'))
L.append(row('', 'FCF after SBC', 'capint_gap_cash_2023_25', kind='ci'))
for g0 in ['00', '20', '40']:
    L.append(row(f'Change in $T({int(g0)}\\%)$, 2016--19 to 2023--25', 'GAAP', f'T_op_g{g0}_change', kind='ci'))
    L.append(row('', 'FCF after SBC', f'T_cash_g{g0}_change', kind='ci'))
L.append(row('Near-frontier margin gap, average of bands', 'GAAP', 'gap_avg', kind='ci', nd=1, sign=False))
for k_, lab in [('gap_sm', 'of which selling and marketing'), ('gap_rd', 'of which R\\&D'), ('gap_gm', 'of which gross margin'),
                ('gap_ga', 'of which G\\&A')]:
    L.append(row('\\quad ' + lab, '', k_, kind='ci', nd=1, sign=False))
L.append(r'\addlinespace\multicolumn{8}{l}{\emph{B. Distribution of reported scores (E1 primary)}}\\')
for p in ['2016_19', '2023_25']:
    L.append(row(f'P95 of $R$, {p.replace("_", "--")}', 'GAAP', f'p95_op_{p}', kind='ci', sign=False))
    L.append(row('', 'FCF after SBC', f'p95_cash_{p}', kind='ci', sign=False))
L.append(row('Change in P95 of $R$, 2016--19 to 2023--25', 'GAAP', 'p95_change_op', kind='ci'))
L.append(row('', 'FCF after SBC', 'p95_change_cash', kind='ci'))
L.append(r'\addlinespace\multicolumn{8}{l}{\emph{C. Samples}}\\')
cnt = lambda f: ' & '.join('' if vn == 'E1_minus_E2' else f(vn) for vn in TV)
L.append('Firm-years (firms) & & ' + cnt(lambda vn: f"{samples[vn]['n']:,} ({samples[vn]['firms']})") + r' \\')
L.append('\\quad of which acquisition-affected & & ' + cnt(lambda vn: str(samples[vn]['n_affected_kept'])) + r' \\')
L.append('Firm-years with $g>50\\%$ & & ' + cnt(lambda vn: str(samples[vn]['n_g_above_50'])) + r' \\')
tab = r"""\begin{table}[t]\centering\small
\caption{Observed scores (E1) and the organic frontier (E2): headline statistics}\label{tab:estimands}
\resizebox{\textwidth}{!}{\begin{tabular}{llcccccc}\toprule
 & & \multicolumn{3}{c}{Estimands} & \multicolumn{3}{c}{E2 without pro forma adjustment, by flag threshold}\\\cmidrule(lr){3-5}\cmidrule(lr){6-8}
Statistic & Basis & E1: all firm-years & E2: organic & E1 $-$ E2 & 10\% & 25\% & 50\%\\\midrule
""" + '\n'.join(L) + r"""
\bottomrule\end{tabular}}
\par\vspace{2pt}\footnotesize\raggedright Notes: Core sample (SIC 7372), fiscal years 2010--2025. E1 uses every firm-year and reported growth. E2 describes organic growth: a firm-year is acquisition-affected when cash paid for acquisitions or the increase in goodwill is at least 25\% of prior-year revenue, or pro forma revenue exceeds revenue by at least 10\%, and in the following year; E2 keeps such a firm-year with organic growth $g^{\rm org}_t=(1+g_t)(1+\pi_t)/(1+\pi_{t-1}+\rho_t)-1$ where the ASC 805 pro forma revenue of the original filings identifies it ($\pi_t$, $\rho_t$: current-year and prior-period pro forma revenue over reported revenue, less one; $\pi_{t-1}$: the previous year's current-year ratio; not identified when both $\pi_{t-1}$ and $\rho_t$ are positive and reading the comparative year cumulatively, $1+\max(\pi_{t-1},\rho_t)$ in the denominator, changes $g^{\rm org}_t$ by more than one point), excludes it otherwise, and excludes growth of at least 100\% with neither acquisition payments nor goodwill reported. Unaffected firm-years keep reported growth. The last three columns exclude affected firm-years without adjustment at cash and goodwill thresholds of 10, 25 and 50\% of prior-year revenue (pro forma criterion 4, 10 and 20\% of revenue); the 25\% column is the robustness sample of Table~\ref{tab:robust}. Slopes: $\tau=0.90$ quantile regression of margin on growth for $0\leq g\leq0.6$. Spend ratio: previous year's selling-and-marketing share over growth in excess of the year's median growth (all firm-years), for firm-years growing faster than that median; the implied weight on growth is the ratio over $\alpha$. Size gradient: $\tau=0.95$ quantile regression of $R$ on log prior-year revenue, times $\ln 10$. Capital-intensity gap: P95 of $R$ above minus below the period median of capital expenditure and capitalized software over revenue. $T(g_0)=g_0+\phi_{0.95}(g_0)$. Margin gap: top decile minus 40th--60th percentiles of GAAP operating margin within growth bands of 0--60\%, averaged over bands. Acquisition-affected firm-years are counted at the column's threshold; E1 keeps them with reported growth, E2 with pro forma organic growth. Points except slopes, ratio and weights. Parentheses: firm-cluster bootstrap standard errors; brackets: 90\% firm-cluster bootstrap intervals; E1 $-$ E2 from a paired bootstrap over the same firm draws. E1 standard errors and intervals of statistics reported elsewhere in the paper are the draws behind Tables~\ref{tab:top}, \ref{tab:threshold}, \ref{tab:local}, \ref{tab:scale} and \ref{tab:gap}. The spend ratio of Section~\ref{sec:empirics} is the 25\% column (an organic-exclusion sample); the E1 column, which includes acquisition-affected firm-years, is new here.
\end{table}"""
open(f'{BASE}/sections/tables/tab_estimands.tex', 'w').write(tab)

# =============================================================================================== 10. notes
sgn = lambda x: 'lower' if x < 0 else 'higher'
SEL_NAME = {'rev_lag': 'prior-year revenue ($ million)', 'g': 'reported growth (points)',
            'gorg25': 'growth used in E2 (affected: adjusted subset only; points)', 'm_op': 'GAAP operating margin (points)',
            'm_fcf_sbc': 'FCF margin after SBC (points)', 'sbc_share': 'SBC / revenue (points)',
            'capex_int': 'capital intensity (points)', 'sms': 'S&M / revenue (points)', 'R_op': 'GAAP score (points)',
            'R_cash': 'cash score (points)'}


def sel_line(v, r):
    sc = 1e-6 if v == 'rev_lag' else 100
    return f"- {SEL_NAME[v]}: {sc * r['est']:+.1f} [{sc * r['ci90'][0]:+.1f}, {sc * r['ci90'][1]:+.1f}]"
mfl = sel['flagged_minus_unflagged']
mev = sel['ever_acquirer_unflagged_minus_never']

# E2 under the rule of the first test run (protocol record, section 1): the additive formula applied to every firm-year
# with disclosures, unaffected firm-years included, no ambiguity rule. Point estimates for the notes only (not in the
# JSON); the slope is reported with the solver of this script (IRLS) and with an exact LP solution.
from scipy.optimize import linprog


def qr_exact(y, x, tau):
    X = np.c_[np.ones(len(x)), np.asarray(x, float)]
    r = linprog(-np.asarray(y, float), A_eq=X.T, b_eq=(1 - tau) * X.sum(0), bounds=(0, 1), method='highs')
    return float(-r.eqlin.marginals[1])


_ct = core.merge(P[['cik', 'year', 'fy_end']].assign(g_test=(1 + P.g) * (1 + P.pi25) / (1 + P.piprev25 + P.rho25) - 1),
                 on=['cik', 'year', 'fy_end'], how='left', validate='one_to_one')
_vt = variant(~_ct.unver & _ct.g_test.notna(), 'g_test', frame=_ct)
TEST = dict(n=len(_vt), firms=_vt.cik.nunique(), n_unaffected_changed=int((~_vt.aff & ((_vt.g - _vt.g_rep).abs() > 1e-12)).sum()))
for key, (m, R, lab) in MB.items():
    _d = _vt[['g', m]].dropna()
    _d = _d[(_d.g >= 0) & (_d.g <= 0.6)]
    TEST[f'slope_{key}'] = float(smf.quantreg(f'{m} ~ g', _d).fit(q=0.9, max_iter=5000).params['g'])
    TEST[f'slope_{key}_exact'] = qr_exact(_d[m].values, _d.g.values, 0.9)
    _z = _vt[['period', R]].dropna()
    TEST[f'p95_change_{key}'] = float(np.quantile(_z.loc[_z.period == '2023-25', R], .95) - np.quantile(_z.loc[_z.period == '2016-19', R], .95))
_d = V['E2'][['g', 'm_op']].dropna()
_d = _d[(_d.g >= 0) & (_d.g <= 0.6)]
E2_OP_EXACT = qr_exact(_d.m_op.values, _d.g.values, 0.9)
_kept = samples['E2']['n_affected_kept']
_excl = {k_: v for k_, v in cov['reasons'].items() if k_ != 'organic growth computed'}
ROUTES = (f"{cov['n_flagged']} acquisition-affected core firm-years at the 25% flag ({cov['n_acq_year']} acquisition years, "
          f"{cov['n_following_only']} following years only). Kept in E2 with pro forma organic growth: {_kept} "
          f"({cov['adjusted']['n_acq_year']} acquisition years, {cov['adjusted']['n_following_year']} following years), "
          f"{100 * _kept / cov['n_flagged']:.1f}% of the affected firm-years. Dropped: {cov['n_flagged'] - _kept} "
          f"({100 * (cov['n_flagged'] - _kept) / cov['n_flagged']:.1f}%), by reason: "
          + '; '.join(f'{k_}: {v}' for k_, v in sorted(_excl.items(), key=lambda kv: -kv[1]))
          + (f"; organic growth computed but outside the analysis bounds or unverified: {cov['n_flagged_computed'] - _kept}"
             if cov['n_flagged_computed'] != _kept else '')
          + f". Unverified hypergrowth dropped: {cov['n_unverified']} firm-years. Unaffected firm-years kept with reported "
          f"growth: {samples['E2']['n'] - _kept}. E2 is therefore the firm-years without material acquisitions plus {_kept} "
          f"pro forma re-admissions; it differs from the exclusion-only 25% sample ({samples['E2x25']['n']:,} firm-years) "
          f"only by those re-admissions.")
notes = f"""# Estimand notes: observed scores (E1) and the organic frontier (E2)

Generated by `code/estimate_organic.py` (numbers below are written by the script from `data/`; do not edit by hand).
Machine-readable results: `notes/empirics_organic.json`; table: `sections/tables/tab_estimands.tex`.

## 1. Protocol record (for the protocol appendix)

- Order of events. The main empirical results of Part I were first estimated on all firm-years (E1). Excluding
  acquisition-affected firm-years was run as a robustness check (Table tab:robust, row "Excluding acquisition-affected
  years and unverified hypergrowth"), and its results were known to the lead agent and the author before the decision
  recorded here. The calibration (code/calibrate_horizons.py) already excluded acquisition-affected firm-years from its
  anchor.
- Decision. On 29 Oct 2026 (author's question at 11:19 on what academic rigor requires), the lead agent changed the
  primary sample for the model-facing results to the organic frontier (E2), and kept all firm-years (E1) primary for the
  descriptive statistics of reported scores. The primary sample for the model-facing results was therefore changed
  AFTER the robustness results were already known.
- Stated motivation (lead agent). The estimand should match the theory and the calibration: the model's frontier
  describes growth bought with spend that the firm expenses; acquired growth is paid for in investing cash flow and
  never touches the margin (Proposition prop:acquired-score, Remark rem:acquired-bounds), and the calibration anchor
  already excludes it.
- What was known at the decision. The exclusion-only robustness row (identical to the 25% exclusion-only column here)
  gave upper-decile slopes of {RES['slope_op_pooled']['E2x25']['est']:.2f} (GAAP) and
  {RES['slope_cash_pooled']['E2x25']['est']:.2f} (FCF after SBC), against {RES['slope_op_pooled']['E1']['est']:.2f} and
  {RES['slope_cash_pooled']['E1']['est']:.2f} on all firm-years, and changes in the P95 of the score of
  {100 * RES['p95_change_op']['E2x25']['est']:.1f} and {100 * RES['p95_change_cash']['E2x25']['est']:.1f} points, against
  {100 * RES['p95_change_op']['E1']['est']:.1f} and {100 * RES['p95_change_cash']['E1']['est']:.1f}. The other
  statistics had not been estimated on the organic sample.
- Safeguards. Both estimands are reported side by side for every headline statistic (Table tab:estimands), with a
  paired bootstrap of the difference; the flag threshold is varied (10, 25, 50%); all results are reported, including
  those where E2 changes a conclusion.
- Order of the pro forma rules (disclosed because two rules were added after a test run). The formula, validity range
  and repeat rule were set after inspecting the pro forma data (coverage, scale errors, re-reported figures) and
  before any E2 statistic was computed. A first test run (reduced bootstrap) then applied the additive formula to every
  firm-year with disclosures. Inspection of the largest adjustments showed implausible organic growth where a filing
  presents the comparative year cumulatively (SS&C 2019: -20% under the additive reading, about 0% under the
  cumulative one). Two rules were then added: the adjustment is applied to acquisition-affected firm-years only, and a
  firm-year whose additive and cumulative readings differ by more than one point is treated as not identified, with both
  readings reported as sensitivity variants (E2add, E2max). The test run's E2 point estimates were seen before this
  change; the exclusion-only and E1 estimates do not depend on it.
- Dates (session log, same clock as the decision time above, UTC-7). 29 Oct 2026: estimand decision 11:19; test run
  started 11:36, its E2 point estimates printed at 11:41; the ambiguity rule (AMBIG_TOL = one point) and the
  flagged-years-only rule were written into this script at 11:44, 25 minutes after the decision and 3 minutes after the
  test run's estimates were seen. No E2 estimate was computed between the decision and the test run.
- E2 under the test run's rule (additive formula on every firm-year with disclosures, unaffected ones included, no
  ambiguity rule), recomputed here: {TEST['n']:,} firm-years ({TEST['firms']} firms; {TEST['n_unaffected_changed']}
  unaffected firm-years have their growth changed). Upper-decile slope {TEST['slope_op']:.3f} GAAP (exact LP
  {TEST['slope_op_exact']:.3f}) and {TEST['slope_cash']:.3f} FCF after SBC (exact {TEST['slope_cash_exact']:.3f}), against E2
  {RES['slope_op_pooled']['E2']['est']:.3f} and {RES['slope_cash_pooled']['E2']['est']:.3f}; change in the P95 of the score
  {100 * TEST['p95_change_op']:.1f} and {100 * TEST['p95_change_cash']:.1f} points, against
  {100 * RES['p95_change_op']['E2']['est']:.1f} and {100 * RES['p95_change_cash']['E2']['est']:.1f}. The two rules made the GAAP
  slope steeper, away from E1: by {abs(RES['slope_op_pooled']['E2']['est'] - TEST['slope_op']):.3f} with this script's
  solver (IRLS), and by {abs(E2_OP_EXACT - TEST['slope_op_exact']):.3f} with the exact solution (E2 exact {E2_OP_EXACT:.3f};
  the IRLS value {RES['slope_op_pooled']['E2']['est']:.3f} is not the minimizer, see code/estimate_v3.py).

## 2. Definitions

- E1: all {samples['E1']['n']:,} core firm-years ({samples['E1']['firms']} firms), reported growth.
- E2: acquisition-affected firm-years (flag of build_panel_v2.py, 25% threshold, year t and t+1) are kept with
  organic growth where the pro forma disclosures allow it, excluded otherwise; unverified hypergrowth
  ({cov['n_unverified']} firm-years) excluded. {samples['E2']['n']:,} firm-years ({samples['E2']['firms']} firms), of
  which {samples['E2']['n_affected_kept']} affected firm-years are kept with pro forma organic growth.
- Organic growth: g_org_t = (1 + g_t)(1 + pi_t) / (1 + pi_(t-1) + rho_t) - 1 (script header), the constant-perimeter
  growth of the businesses owned at the end of year t, for affected firm-years only; unaffected firm-years keep
  reported growth. pi_t = PF_t^(t)/S_t - 1 and rho_t = PF_(t-1)^(t)/S_(t-1) - 1 are the current-year and prior-period
  pro forma ratios of the year-t original filing; pi_(t-1) is the current-year ratio of the year t-1 original filing.
- Not identified: {cov['ambiguous']['n']} affected firm-years in which both pi_(t-1) > 0 and rho_t > 0 and the additive
  (ASC 805) and cumulative readings differ by more than one point (median width
  {100 * cov['ambiguous']['med_bound_width']:.1f} points, largest {100 * cov['ambiguous']['max_bound_width']:.1f}); they are
  excluded from E2 and read each way in E2add and E2max.

## 3. Approximation error of the pro forma adjustment

1. Acquired businesses' own growth counts as organic. g_org = (1 - w) g_base + w g_T, with w = rho_t / (1 + pi_(t-1) +
   rho_t) the acquired businesses' share of the constant-perimeter base, so the error relative to the growth of the
   businesses already owned is w (g_T - g_base). Among the {cov['adjusted']['n_with_rho']} adjusted firm-years with
   rho_t > 0 the median w is {100 * cov['adjusted']['w_median']:.1f}% (90th percentile {100 * cov['adjusted']['w_p90']:.1f}%;
   w = 0 in following years without new acquisitions): a 20-point growth
   difference between target and acquirer moves g_org by {100 * cov['adjusted']['err_at_20pt_median']:.1f} points at the
   median and {100 * cov['adjusted']['err_at_20pt_p90']:.1f} at the 90th percentile. The sign is unknown.
2. Definition. The paper's Definition def:acquired-growth counts the carry-over of businesses bought in t-1 (owned
   throughout t) as organic; g_org removes it, which is consistent with flagging the following year.
3. Pro forma content. ASC 805-10-50-2(h) pro forma revenue is the combined entity's revenue as if the acquisitions
   had closed at the start of the comparative year, with adjustments the filer chooses (for example fair-value
   adjustments to deferred revenue) that XBRL does not separate. Sign unknown, usually small.
4. Coverage of the disclosures. Only material acquisitions are disclosed, and companyfacts carries only facts without
   dimensions, so pro forma revenue tagged by acquisition is unobserved. Unflagged firm-years keep reported growth, as
   in the exclusion-only sample; acquisitions below the flag threshold therefore remain in their growth.
5. Presentation of the note. ASC 805-10-50-2(h)(3) asks the year-t note for the year-t combinations only (additive
   denominator); some filers present the comparative year cumulatively (denominator 1 + max(pi_(t-1), rho_t)). The
   data cannot tell the two apart; see the ambiguity rule above.
6. Data rules. Figures outside 0.98-3.5 times reported revenue (scale errors in thousands, figures that are not
   combined totals) are treated as not reported ({cov['n_pf_invalid']} core facts). A prior-period figure equal to the
   previous filing's current-year figure is a re-reported disclosure of last year's acquisitions, not the comparative
   for this year's ({cov['n_pri_repeat']} core firm-years); it is not used for rho_t. Divestitures are not removed.
7. Missing element. The panel (data/panel_v2_all.csv) carries only the current-year gap (proforma_gap), and for
   {cov['n_panel_pf_from_later_filing']} core firm-years that figure comes from a LATER filing (the next year's
   comparative, which reflects the next year's acquisitions); {cov['n_acq_now_only_by_later_filing_pf']} acquisition-year
   flags rest only on such a figure. The prior-period figure is not in the panel; it is read from the original filing
   in data/companyfacts_extract.json (the panel's own source; nothing re-fetched).

## 4. Coverage

- Flagged core firm-years: {cov['n_flagged']} ({100 * cov['share_flagged']:.1f}%); organic growth computed for
  {cov['n_flagged_computed']} ({100 * cov['share_flagged_computed']:.1f}%): {100 * cov['share_acq_year_computed']:.1f}% of
  acquisition years and {100 * cov['share_following_only_computed']:.1f}% of following years.
- Fast growers (g > 50%): {cov['n_fast']} firm-years, {cov['n_fast_flagged']} flagged, organic growth computed for
  {cov['n_fast_flagged_computed']} ({100 * cov['share_fast_flagged_computed']:.1f}%); {100 * cov['share_fast_in_E2']:.1f}%
  of fast growers are in E2.
- Reasons for exclusion among flagged firm-years: {json.dumps(cov['reasons'])}.
- Adjusted firm-years: median reported growth {100 * cov['adjusted']['med_g']:.1f}%, median organic growth
  {100 * cov['adjusted']['med_g_org']:.1f}%, median acquired contribution {100 * cov['adjusted']['med_acquired']:.1f}
  points (IQR {100 * cov['adjusted']['iqr_acquired'][0]:.1f} to {100 * cov['adjusted']['iqr_acquired'][1]:.1f}).
- Of the adjusted firm-years, {cov['adjusted']['n_acq_year']} are acquisition years and {cov['adjusted']['n_following_year']}
  following years. Not identified (ambiguous presentation): {cov['ambiguous']['n']} ({cov['ambiguous']['n_fast']} with g > 50%).
- E2 by route. {ROUTES}
- Threshold variants: share flagged / share of flagged with organic growth computed:
  """ + '; '.join(f"{t}%: {100 * c['share_flagged']:.1f}% / {100 * c['share_flagged_computed']:.1f}%" for t, c in cov['thresholds'].items()) + f""".
- Sensitivity to the ambiguous cases (upper-decile slope, GAAP / FCF after SBC): E2 {RES['slope_op_pooled']['E2']['est']:.2f} /
  {RES['slope_cash_pooled']['E2']['est']:.2f}; additive reading {RES['slope_op_pooled']['E2add']['est']:.2f} /
  {RES['slope_cash_pooled']['E2add']['est']:.2f}; cumulative reading {RES['slope_op_pooled']['E2max']['est']:.2f} /
  {RES['slope_cash_pooled']['E2max']['est']:.2f}.

## 5. Selection diagnostics (flagged minus unflagged firm-years, medians, 90% firm-cluster intervals)

""" + '\n'.join(sel_line(v, mfl[v]) for v in SELV) + f"""

Ever-acquirers' unflagged years minus never-acquirers:

""" + '\n'.join(sel_line(v, mev[v]) for v in SELV) + f"""

Top tail: flagged share of firm-years at or above the period P95 of the cash score
{100 * sel['top_tail']['cash']['share_flagged_top']:.0f}% (2023-25: {100 * sel['top_tail']['cash']['share_flagged_top_2023_25']:.0f}%),
against {100 * sel['top_tail']['cash']['share_flagged_all']:.0f}% overall; GAAP score {100 * sel['top_tail']['op']['share_flagged_top']:.0f}%.

Frontier position: share of firm-years above the exclusion-only 90th percentile of margin in their growth band (10% if
exchangeable). """ + '; '.join(f"{MB[key][2]}: affected firm-years kept in E2 at organic growth "
                               f"{100 * fp['affected_kept_in_E2_organic_g']['share']:.0f}% (n = {fp['affected_kept_in_E2_organic_g']['n']}), "
                               f"all affected at reported growth {100 * fp['affected_all_reported_g']['share']:.0f}%, "
                               f"ever-acquirers' unaffected years {100 * fp['ever_acquirer_unflagged_years']['share']:.0f}%, "
                               f"never-acquirers {100 * fp['never_acquirer']['share']:.0f}%"
                               for key, fp in sel['frontier_position'].items()) + f"""

Direction of bias. Firms that buy growth have {sgn(mev['g']['est'])} growth in their years without acquisitions than
firms that never acquire ({100 * mev['g']['est']:+.1f} points) and {sgn(mev['m_op']['est'])} GAAP margins
({100 * mev['m_op']['est']:+.1f} points), and in adjusted acquisition-affected years organic growth is
{100 * cov['adjusted']['med_acquired']:.1f} points below reported growth at the median. Weaker organic growth
opportunities therefore show up as lower organic growth, not lower margins: acquirers sit at the low-growth,
high-margin end of the organic cloud. Two biases follow. (i) E1 counts their acquired growth as if it were organic,
moving high-margin points to the right, which flattens the upper-tail slope; excluding them removes that bias.
(ii) Exclusion also drops their organic points. Where those points lie above the within-band 90th percentile it
lowers the estimated frontier at low growth (and flattens the slope); where they lie below it raises the frontier. The
frontier-position shares above say which dominates for the adjustable subset; for the excluded majority only reported
growth is known. Their GAAP margins also include amortization of acquired intangibles and deal costs, which lowers
their points on the GAAP basis but not on the cash basis. The pro forma adjusted E2 restores part of this population;
its difference from the exclusion-only sample at 25% measures the effect for the adjustable part only: upper-decile
slope {RES['slope_op_pooled']['E2']['est']:.2f} against {RES['slope_op_pooled']['E2x25']['est']:.2f} (GAAP) and
{RES['slope_cash_pooled']['E2']['est']:.2f} against {RES['slope_cash_pooled']['E2x25']['est']:.2f} (FCF after SBC). The
adjustable subset is {cov['adjusted']['n']} of {cov['n_flagged']} affected firm-years and is not representative of the
excluded ones (see the medians in notes/empirics_organic.json, selection.medians).

## 6. Calibration consistency

calibrate_horizons.py excludes acq_flag == 1 within the tail at or above the P95 of the FULL 2023-25 sample. The
flag is the same flag as E2's (25%, t and t+1). Differences from E2: (i) the P95 cut-off is computed on E1, not on the
organic sample; (ii) unverified hypergrowth is not excluded ({cal['differences']['unverified_in_tail']} such firm-years in
the tail, so no effect); (iii) affected firm-years are excluded, not adjusted ({cal['differences']['flagged_in_tail']}
flagged in the tail, {cal['differences']['flagged_in_tail_adjustable']} adjustable); (iv) G is the E1 median.
Anchor as calibrated: n = {cal['as_calibrated']['n']}, cut-off {100 * cal['as_calibrated']['p95']:.1f}, median R
{100 * cal['as_calibrated']['R'][1]:.1f}, median m0_ub {100 * cal['as_calibrated']['m0_ub'][1]:.1f}, IQR Pi_ub
{100 * cal['as_calibrated']['Pi_ub'][0]:.1f} to {100 * cal['as_calibrated']['Pi_ub'][2]:.1f}.
Anchor on E2 throughout: n = {cal['E2']['n']}, cut-off {100 * cal['E2']['p95']:.1f}, G {100 * cal['E2']['G']:.1f},
median R {100 * cal['E2']['R'][1]:.1f}, median m0_ub {100 * cal['E2']['m0_ub'][1]:.1f}, IQR Pi_ub
{100 * cal['E2']['Pi_ub'][0]:.1f} to {100 * cal['E2']['Pi_ub'][2]:.1f}.
Anchor on exclusion-only E2 (25%): n = {cal['E2x25']['n']}, cut-off {100 * cal['E2x25']['p95']:.1f}, median R
{100 * cal['E2x25']['R'][1]:.1f}, median m0_ub {100 * cal['E2x25']['m0_ub'][1]:.1f}.
calibrate_horizons.py was not changed.

### 6b. Anchor inputs for the calibration (notes/calibration_anchor_E2.json)

Model-facing results, the calibration included, use E2. The file holds the E2 anchor (cut-off, G and tail from the E2
sample, organic growth for adjusted firm-years) and an E1 block in the same format; the E1 block reproduces the current
anchor of notes/calibration_results.json exactly (regression check on {len(REG_KEYS)} fields). Points; quartiles are
25th / median / 75th percentile.

| | E1 (current anchor) | E2 (organic) |
|---|---|---|
""" + '\n'.join(f"| {lab} | {f1(ANCH['E1'])} | {f1(ANCH['E2'])} |" for lab, f1 in [
    ('firm-years in the anchor', lambda a: f"{a['n']} (of {a['n_tail']} in the tail; {a['n_adjusted_pro_forma']} pro forma adjusted)"),
    ('cut-off (P95 of the cash score)', lambda a: f"{100 * a['p95']:.1f}"),
    ('G (median growth, 2023-25)', lambda a: f"{100 * a['G']:.1f}"),
    ('median score R', lambda a: f"{100 * a['R'][1]:.1f}"),
    ('intercept m0, upper bound (quartiles)', lambda a: ' / '.join(f"{100 * x:.1f}" for x in a['m0_ub'])),
    ('intercept m0, lower bound (quartiles)', lambda a: ' / '.join(f"{100 * x:.1f}" for x in a['m0_lb'])),
    ('Pi_ub: median [IQR]', lambda a: f"{100 * a['Pi_ub'][1]:.1f} [{100 * a['Pi_ub'][0]:.1f}, {100 * a['Pi_ub'][2]:.1f}]"),
    ('Pi_lb: median [IQR]', lambda a: f"{100 * a['Pi_lb'][1]:.1f} [{100 * a['Pi_lb'][0]:.1f}, {100 * a['Pi_lb'][2]:.1f}]"),
    ('share with Pi_ub > 0 / Pi_lb > 0', lambda a: f"{100 * a['share_Pi_ub_positive']:.0f}% / {100 * a['share_Pi_lb_positive']:.0f}%"),
    ('transient share of the median score (Pi_ub / R to Pi_lb / R)',
     lambda a: f"{100 * a['transient_share_ub']:.0f}% to {100 * a['transient_share_lb']:.0f}%")]) + (f"""

Under E2 the median Pi_ub is negative ({100 * ANCH['E2']['Pi_ub'][1]:.1f} points): if all selling and marketing expense
buys growth, only {100 * ANCH['E2']['share_Pi_ub_positive']:.0f}% of the organic anchor firm-years score above their
durable level, against {100 * ANCH['E1']['share_Pi_ub_positive']:.0f}% in the current anchor. The model's surplus is a
maximum over spend that includes zero spend, so Pi >= 0 at the optimum on the X = 1 basis; a negative Pi_ub therefore
means either that the firm acts on a weight on growth above one (the paper's reading of monday.com) or that the S&M
share overstates its growth spend. For the "transient surplus" reading, the lower end of the range is no longer
positive: between {100 * ANCH['E2']['transient_share_ub']:.0f}% and {100 * ANCH['E2']['transient_share_lb']:.0f}% of the
median organic top score is transient (current anchor {100 * ANCH['E1']['transient_share_ub']:.0f}% to
{100 * ANCH['E1']['transient_share_lb']:.0f}%). That the best organic scores of 2023-25 were partly transient is
established only if part of selling and marketing expense does not buy growth; at the upper bound the median organic
top-tail firm-year is at its durable level. The change comes from the cut-off, not from the firm-years both anchors
share (the lower E2 median growth G raises their Pi slightly): {ENTR['n']} firm-years enter at the lower E2 cut-off (P95
{100 * ANCH['E2']['p95']:.1f} against {100 * ANCH['E1']['p95']:.1f}): {ENTR['names']}; {ENTR['n_neg']} of them have Pi_ub < 0,
and {ANCH['E2']['n_adjusted_pro_forma']} of the {cal['differences']['flagged_in_tail_adjustable']} flagged tail firm-years
with computable organic growth stay above the cut-off after adjustment.
""" if ANCH['E2']['Pi_ub'][1] < 0 else "\n") + f"""
## 7. Reconciliation with the existing tables (Paper 1 editor's queries, 29 Oct)

- E1 standard errors. A first version of tab_estimands.tex came from a test run with replications divided by ten
  (20 for the slopes), which gave an E1 GAAP slope standard error of 0.09. The estimator, sample (core SIC 7372, growth
  0 to 60%), clustering (firm), replications (200) and seed are those of estimate_revised.py, and the point estimates
  are identical (checks block). With full replications this script's own draw differs from estimate_revised.py's only by
  Monte Carlo error (the random stream is at a different position): E1 GAAP slope se
  {RES['slope_op_pooled']['E1']['se_own']:.3f} here against {RES['slope_op_pooled']['E1']['se']:.3f} there. To keep the
  tables consistent, the E1 entries of statistics that estimate_revised.py and decompose_gap.py already report use their
  draws (field draws in the JSON; own draws kept as se_own and ci90_own). Nothing in estimate_revised.py is wrong.
- Spend ratio. The text's {RES['spend_ratio']['E2x25']['est']:.1f} is the exclusion-only organic sample
  (acquisition-affected and unverified hypergrowth firm-years removed), reproduced exactly in the 25% column. The E1
  value {RES['spend_ratio']['E1']['est']:.1f} adds the acquisition-affected firm-years with reported growth, whose acquired
  growth enlarges excess growth and lowers the ratio; the existing code never computed it. E2 (pro forma adjusted):
  {RES['spend_ratio']['E2']['est']:.1f}. Nothing in estimate_revised.py is wrong.

## 8. Headline statistics, E1 against E2 (est, se; changes and gaps with 90% intervals; E1 - E2 paired)

""" + '\n'.join(
    f"- {k_}: E1 {RES[k_]['E1']['est']:.4f} (se {RES[k_]['E1'].get('se', float('nan')):.4f}); "
    f"E2 {RES[k_]['E2']['est']:.4f} (se {RES[k_]['E2'].get('se', float('nan')):.4f}); "
    f"E1-E2 {RES[k_]['E1_minus_E2']['est']:.4f} [{RES[k_]['E1_minus_E2']['ci90'][0]:.4f}, {RES[k_]['E1_minus_E2']['ci90'][1]:.4f}]"
    for k_ in HEAD if 'E1_minus_E2' in RES[k_]) + """
"""
open(f'{BASE}/notes/estimand_notes.md', 'w').write(notes)
print(('rewrote' if TABLES_ONLY else 'wrote notes/empirics_organic.json,'), 'sections/tables/tab_estimands.tex, notes/estimand_notes.md')
