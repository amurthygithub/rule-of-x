#!/usr/bin/env python3
"""Paper 1 on the audited sample (panel v3): exact estimators and a seeded firm-cluster bootstrap.

Decisions this script is built to (author, 29 Oct 2026; recorded at the top of notes/inference_v3.md):
  D-1  The growth weight of 7 to 13 is withdrawn. The spend ratio is kept as a statistic of its own; the bounds that
       each method gives are reported: (a) the median of S&M share / (g - G) by tercile of excess growth and with
       excess-growth floors; (b) net of the S&M share of firm-years growing at or below the median; (c) the levels
       first-order-condition regressions of S&M share on growth (referee 2); (d) constant G of 5, 8 and 12%.
  D-2  The primary slope statistic is the slope of Psi_chi, the order-chi frontier among firm-years with growth at least
       g (dominance cone, Definition 2): phi_chi(g0) = chi-quantile of the margin among firm-years with g >= g0,
       computed exactly on the grid g0 = 0, 0.05, ..., and summarized by its least-squares slope over the grid points of
       a growth window (central: chi = 0.90, window 0 to 60%; grid chi = 0.80 to 0.95, windows 0-40 to 0-100%). A grid
       point is defined when at least 30 firm-years have g >= g0; a window slope is defined when all its grid points are.
       The local conditional quantile Q_tau(m | g) (linear quantile regression on 0 <= g <= 0.6) is reported alongside
       as a descriptive statistic.
  D-3  Every model-facing statistic is reported under E1 (the baseline), E2 and the two imputation bounds (deal
       multiples 4 and 8), with a flag for whether the claim's sign and significance hold in all four.

Samples. Frames of code/estimate_organic.py, executed up to its END OF FRAME CONSTRUCTION marker (ORGANIC_PANEL=v3, or
v2 for the like-for-like comparison). Added here:
  E2imp4, E2imp8  E2 plus the acquisition-affected firm-years E2 drops, with organic growth imputed by removing acquired
                  revenue equal to the purchase price over a price-to-revenue multiple M, half in the deal year and half
                  in the following year; the price is cash paid for acquisitions, or the increase in goodwill over 0.75
                  where no payment is reported (referee 3, c7_impute.py).
  E2testrule      E2 under the first test run's rule (additive pro forma formula on every firm-year with disclosures,
                  no ambiguity rule; protocol record in notes/estimand_notes.md). Point estimates only.
  E1r2named, E2r2named  without the review panels' named firms that the R2 classifier classes non-software (the
                  classifier run on the 16 named firms only). Since R2 applies to the main sample (3 Nov 2026) these
                  firms are already excluded, so the two variants equal E1 and E2; kept for continuity.
  E1r2both, E2r2both, E1r2either, E2r2either  R2 sensitivity from two independent readings of the business
                  descriptions (build_panel_v3.py, business_class_reader_a and _b): the main sample without the firms
                  that both readers (or either reader) class as not software (point estimates).
  E1nolist, E2nolist  without the firm-years rule R5 flags as no listed equity (sensitivity, point estimates).
Cash-score bridge (B5, v3 only): the cash score before interest paid and cash taxes, R_cash_pre = g + (FCF - SBC +
interest paid + income taxes paid) / revenue, and before interest only, R_cash_bi = g + (FCF - SBC + interest paid x
(1 - t)) / revenue with t the US federal statutory rate (35% for fiscal years ending before 2018, 21% from 2018);
elements from SEC frames (latest filed, not first reported); block 'bridge'.

Estimation. Quantile regressions are solved exactly as linear programs (HiGHS, dual formulation; coefficients are the
multipliers of the equality constraints), checked at the point estimates against the primal LP and statsmodels IRLS and
for uniqueness. Bootstrap: B = 999 firm-cluster replications for every interval. Firms are drawn from the E1 sample;
each estimand is evaluated on its own rows of the drawn firms, so marginal intervals and paired differences come from the
same draws. Each block of statistics has its own generator, seeded from the block name (seeds in the JSON), so a result
does not depend on the order of computation or on the number of worker processes. The capital-intensity split is
re-estimated inside each draw; firm-years with missing capital intensity are not classified (v1 coded them as low).
Undefined draws are counted; a statistic with more than 5% undefined draws, or a frontier-point cell T(g0) with fewer than
30 firm-years, gets no interval ('not estimable'). Intervals: percentile, basic and normal at 90% and 95%, bias-corrected
percentile at 90%; two-sided bootstrap p-values of each type. Multiplicity: Holm step-down (primary) and Romano-Wolf
studentized step-down on a joint draw (check), across the paired E1 - E2 contrasts of Table tab:estimands_v3 and across
two families of 14 headline contrasts.

Inputs : as code/estimate_organic.py; notes/panel_v3_build.json, notes/empirics_organic.json (published v2 values),
         notes/calibration_anchor_E2.json, notes/empirics_v2_exact.json (v2 run of this script)
Outputs: V3_PANEL=v2  notes/empirics_v2_exact.json
         V3_PANEL=v3  notes/empirics_v3.json, notes/bootstrap_draws_v3.npz, notes/calibration_anchor_v3.json (same format
                      as notes/calibration_anchor_E2.json), notes/frontier_slope_v3.json (Psi_chi slopes: the frontier
                      input for the calibration), sections/tables/tab_estimands_v3.tex, tab_contrasts_v3.tex,
                      tab_grid_v3.tex, tab_yearly_v3.tex, notes/inference_v3.md, notes/sample_audit.md
Run    : V3_PANEL=v2 python3 code/estimate_v3.py && python3 code/estimate_v3.py   (v2 first; V3_FAST=1: 60 replications;
         V3_JOBS: worker processes, default 2; V3_REPORT_ONLY=1: rewrite tables and notes from the JSON)
"""
import json
import math
import os
import sys
import time
import zlib
import warnings
from multiprocessing import get_context

import numpy as np
import pandas as pd
from scipy import optimize, stats as sst
from scipy.optimize import linprog
import statsmodels.formula.api as smf

warnings.filterwarnings('ignore')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL = os.environ.get('V3_PANEL', 'v3')
assert PANEL in ('v2', 'v3')
FAST = os.environ.get('V3_FAST') == '1'
REPORT_ONLY = os.environ.get('V3_REPORT_ONLY') == '1'
NJOBS = max(1, int(os.environ.get('V3_JOBS', '2')))
B = int(os.environ.get('V3_B', 60 if FAST else 999))           # V3_B: replication override for smoke tests only
SEED0 = 20261030
NAN_MAX = 0.05
MIN_CELL = 30
TAU_CAL = 0.18
ALPHA = (0.25, 0.45)
PERIODS = ['2010-15', '2016-19', '2020-22', '2023-25']
PK = [p.replace('-', '_') for p in PERIODS]
BASES = {'op': ('m_op', 'R_op', 'GAAP'), 'cash': ('m_fcf_sbc', 'R_cash', 'FCF after SBC')}
SIZE_BINS = [100e6, 500e6, 2e9, 10e9, 1e13]
SIZE_KEYS = ['0_1to0_5B', '0_5to2B', '2to10B', 'over10B']
GAP_KEYS = ['gap_avg', 'gap_gm', 'gap_sm', 'gap_rd', 'gap_ga', 'gap_oth', 'gap_slow', 'gap_slow_gm', 'gap_fast', 'gap_fast_sm', 'gap_fast_rd']
LN10 = math.log(10)
T0 = time.time()
fin = np.isfinite
OUT_JSON = f'{BASE}/notes/empirics_v3.json' if PANEL == 'v3' else f'{BASE}/notes/empirics_v2_exact.json'


def log(*a):
    print(f'[{time.time() - T0:6.0f}s]', *a, flush=True)


def seed_for(name):
    return SEED0 + zlib.crc32(name.encode()) % 1_000_000


# =============================================================================================== 1. frames
os.environ['ORGANIC_PANEL'] = PANEL
SRC = f'{BASE}/code/estimate_organic.py'
_src = open(SRC).read()
_G = {'__file__': SRC, '__name__': 'organic_frames'}
exec(compile(_src[:_src.index('# ==== END OF FRAME CONSTRUCTION')], SRC, 'exec'), _G)
V, core, P, variant, VLAB = _G['V'], _G['core'], _G['P'], _G['variant'], dict(_G['VLAB'])
core_ext = _G['core_ext']

P['price'] = P.acq_pay.where(P.acq_pay.notna() & (P.acq_pay > 0), P.gw_jump.clip(lower=0) / 0.75).fillna(0.0)
P['prev_price'] = P.groupby('cik').price.shift(1).where(P.consec, 0.0).fillna(0.0)
P['g_test'] = (1 + P.g) * (1 + P.pi25) / (1 + P.piprev25 + P.rho25) - 1
cx = core.merge(P[['cik', 'year', 'fy_end', 'price', 'prev_price', 'g_test']], on=['cik', 'year', 'fy_end'], how='left', validate='one_to_one')
_fl, _now, _prev = cx.flag25.astype(bool), cx.now25.astype(bool), cx.prevnow25.astype(bool)
IMPUTE = {}
for M in (4, 8):
    acq = (np.where(_now, 0.5 * cx.price / M / cx.rev_lag, 0.0) + np.where(_prev, 0.5 * cx.prev_price / M / cx.rev_lag, 0.0))
    cx[f'g_imp{M}'] = np.where(_fl, np.where(cx.gorg25.notna(), cx.gorg25, cx.g - acq), cx.g)
    V[f'E2imp{M}'] = variant(~cx.unver, f'g_imp{M}', frame=cx)
    re_ = (_fl & cx.gorg25.isna() & ~cx.unver).values
    IMPUTE[M] = dict(n_readmitted=int(re_.sum()), n_readmitted_without_price=int((re_ & (acq == 0)).sum()),
                     median_imputed_acquired_growth=float(np.median(acq[re_])),
                     n_dropped_by_bounds=int((re_ & ~cx[f'g_imp{M}'].between(-0.9, 5, inclusive='neither').values).sum()),
                     n=int(len(V[f'E2imp{M}'])))
V['E2testrule'] = variant(~cx.unver & cx.g_test.notna(), 'g_test', frame=cx)
V['E1all'] = V['E1']                                               # anchor of E1 with every firm-year in the tail (D-3)
if PANEL == 'v3':                                                   # sensitivities from the SEC inputs of 29 Oct 2026
    _ce = core_ext
    _prim = _ce.v3_exclude.fillna('') == ''
    _ns = _ce.business_class_named.fillna('').isin(['interactive_entertainment', 'gambling', 'compute_infrastructure'])
    _nl = _ce.no_listed_equity.astype(object).eq(True)
    V['E1r2named'] = variant(_prim & ~_ns, frame=_ce)
    V['E2r2named'] = variant(_prim & ~_ns & ~_ce.unver & _ce.gorg25.notna(), 'gorg25', frame=_ce)
    V['E1nolist'] = variant(_prim & ~_nl, frame=_ce)
    V['E2nolist'] = variant(_prim & ~_nl & ~_ce.unver & _ce.gorg25.notna(), 'gorg25', frame=_ce)
    if 'business_class_reader_b' in _ce.columns and _ce.business_class_reader_b.fillna('').ne('').all():
        _ra = _ce.business_class_reader_a.fillna('software') != 'software'
        _rb = _ce.business_class_reader_b.fillna('software') != 'software'
        for _k, _m in [('both', _ra & _rb), ('either', _ra | _rb)]:
            V[f'E1r2{_k}'] = variant(_prim & ~_m, frame=_ce)
            V[f'E2r2{_k}'] = variant(_prim & ~_m & ~_ce.unver & _ce.gorg25.notna(), 'gorg25', frame=_ce)
            VLAB.update({f'E1r2{_k}': f'E1 without the firms {_k} of two independent readers class as not software (R2 sensitivity)',
                         f'E2r2{_k}': f'E2 without the firms {_k} of two independent readers class as not software (R2 sensitivity)'})
    VLAB.update(E1r2named='E1 without the named firms the R2 classifier classes non-software (equals E1 since R2 applies to the main sample)',
                E2r2named='E2 without the named firms the R2 classifier classes non-software (equals E2 since R2 applies to the main sample)',
                E1nolist='E1 without the firm-years rule R5 flags as no listed equity',
                E2nolist='E2 without the firm-years rule R5 flags as no listed equity')
STAT_RATE = lambda fy_end: np.where(pd.to_datetime(fy_end) < pd.Timestamp('2018-01-01'), 0.35, 0.21)
# Round 2 (D1, F2-1): interest income from SEC frames (data/v3_inputs/interest_income_deferred.json, retrieved 2 Nov 2026),
# matched to the panel fiscal-year ends. InvestmentIncomeInterest first; documented fallbacks, in order, the elements closest
# to interest earned: InvestmentIncomeInterestAndDividend, InterestIncomeOperating. InvestmentIncomeNonoperating and
# InterestAndOtherIncome (which may include gains or other income) and InterestIncomeExpenseNonoperatingNet (net of interest
# expense) are not used. A firm-year without one of the three elements is missing, not zero.
II_ORDER = ['InvestmentIncomeInterest', 'InvestmentIncomeInterestAndDividend', 'InterestIncomeOperating']
_iip = os.path.join(BASE, 'data', 'v3_inputs', 'interest_income_deferred.json')
II = json.load(open(_iip)) if os.path.exists(_iip) else {}


def _ii(cik, fy_end):
    e = II.get(str(int(cik)), {}).get(str(fy_end)[:10], {})
    for el in II_ORDER:
        if e.get(el) is not None:
            return float(e[el]), el
    return np.nan, ''


for _vn, _df in V.items():                                          # B5 bridge bases (missing on v2 frames)
    if 'interest_paid' in _df.columns and 'm_cash_pre' not in _df.columns and II:
        _x = [_ii(c_, f_) for c_, f_ in zip(_df.cik, _df.fy_end)]
        _df['interest_income'] = [v_ for v_, _ in _x]
        _df['interest_income_element'] = [e_ for _, e_ in _x]
        _t = 1 - STAT_RATE(_df.fy_end)
        _df['m_cash_bni'] = _df.m_fcf_sbc + (_df.interest_paid - _df.interest_income) * _t / _df.rev
        _df['m_cash_bnis'] = _df.m_fcf_sbc.where(_df.m_cash_bni.notna())
        for _m, _R in [('m_cash_bni', 'R_cash_bni'), ('m_cash_bnis', 'R_cash_bnis')]:
            _df[_R] = _df.g + _df[_m]
for _vn, _df in V.items():                                          # B5 bridge bases (missing on v2 frames)
    if 'interest_paid' in _df.columns and 'm_cash_pre' not in _df.columns:
        _df['m_cash_pre'] = _df.m_fcf_sbc + (_df.interest_paid + _df.income_taxes_paid) / _df.rev
        _df['m_cash_bi'] = _df.m_fcf_sbc + _df.interest_paid * (1 - STAT_RATE(_df.fy_end)) / _df.rev
        _df['m_cash_bs'] = _df.m_fcf_sbc.where(_df.m_cash_pre.notna())
        for _m, _R in [('m_cash_pre', 'R_cash_pre'), ('m_cash_bi', 'R_cash_bi'), ('m_cash_bs', 'R_cash_bs')]:
            _df[_R] = _df.g + _df[_m]
VLAB.update(E2imp4='E2 plus the dropped acquisition-affected firm-years, organic growth imputed at a price-to-revenue multiple of 4',
            E2imp8='E2 plus the dropped acquisition-affected firm-years, organic growth imputed at a price-to-revenue multiple of 8',
            E2testrule="E2 under the first test run's rule (additive formula on every firm-year with disclosures, no ambiguity rule)",
            E1all='E1 (same frame); used for the anchor with acquisition-affected firm-years kept in the tail, against the calibration rule that drops them')
BOOTV = ['E1', 'E2', 'E2x25', 'E2imp4', 'E2imp8']                 # bootstrapped variants of the headline blocks
MFV = ['E1', 'E2', 'E2imp4', 'E2imp8']                            # D-3: the four estimands of every model-facing claim
PAIRV = ['E1', 'E2']
POINTV = [vn for vn in V if vn not in BOOTV]

E1f = V['E1']
U = np.unique(E1f.cik.values)
UIX = {c: i for i, c in enumerate(U)}
NU = len(U)
FIRST_YEAR = E1f.groupby('cik').year.min()
G_P25, G_P75 = E1f.groupby('year').g.quantile(.25), E1f.groupby('year').g.quantile(.75)
FCOLS = ['g', 'g_rep', 'm_op', 'm_fcf_sbc', 'R_op', 'R_cash', 'lsize', 'capex_int', 'k_lag', 'k_firmmed', 'sm_lag_share',
         'G_t', 'G_p25', 'G_p75', 'gm', 'sms', 'rds', 'gas', 'oth', 'sm', 'rev', 'rev_lag',
         'm_cash_pre', 'm_cash_bi', 'm_cash_bs', 'R_cash_pre', 'R_cash_bi', 'R_cash_bs',
         'm_cash_bni', 'm_cash_bnis', 'R_cash_bni', 'R_cash_bnis']
ICOLS = ['year', 'per', 'fi', 'cik', 'aff', 'acq_flag', 'sb', 'coh19']


def arrays(df):
    d = df.copy()
    d['k_firmmed'] = d.groupby('cik').capex_int.transform('median')
    d['G_p25'], d['G_p75'] = d.year.map(G_P25), d.year.map(G_P75)
    d['per'] = d.period.map({p: i for i, p in enumerate(PERIODS)}).fillna(-1).astype(int)
    d['fi'] = d.cik.map(UIX).fillna(-1).astype(int)
    d['sb'] = d.size_bin.cat.codes.astype(int)
    fy = d.cik.map(FIRST_YEAR).fillna(d.groupby('cik').year.transform('min'))
    d['coh19'] = (fy >= 2019).astype(int)
    A = {c: (d[c].to_numpy(float) if c in d.columns else np.full(len(d), np.nan)) for c in FCOLS}
    A.update({c: d[c].astype(int).to_numpy() for c in ICOLS})
    order = np.argsort(A['fi'], kind='stable')
    fs = A['fi'][order]
    st, en = np.searchsorted(fs, np.arange(NU), 'left'), np.searchsorted(fs, np.arange(NU), 'right')
    A['_rows'] = [order[a:b] for a, b in zip(st, en)]
    return A


AR = {vn: arrays(df) for vn, df in V.items()}


class Sub:
    """Columns of a variant restricted to row positions idx (None: all rows), computed on first access."""
    __slots__ = ('A', 'idx', 'c')

    def __init__(self, A, idx=None):
        self.A, self.idx, self.c = A, idx, {}

    def __getitem__(self, k):
        v = self.c.get(k)
        if v is None:
            v = self.A[k] if self.idx is None else self.A[k][self.idx]
            self.c[k] = v
        return v

    def __len__(self):
        return len(self.A['g']) if self.idx is None else len(self.idx)


def full(vn):
    return Sub(AR[vn])


def drawn(vn, draw):
    rows = AR[vn]['_rows']
    return Sub(AR[vn], np.concatenate([rows[j] for j in draw]))


# =============================================================================================== 2. estimators
def q(x, p):
    x = x[fin(x)]
    return float(np.quantile(x, p)) if len(x) else np.nan


def med(x):
    x = x[fin(x)]
    return float(np.median(x)) if len(x) else np.nan


def qr_fit(y, X, tau):
    """Exact linear quantile regression: max y'a s.t. X'a = (1 - tau) X'1, 0 <= a <= 1; beta = constraint multipliers."""
    r = linprog(-np.asarray(y, float), A_eq=X.T, b_eq=(1 - tau) * X.sum(0), bounds=(0, 1), method='highs')
    return -r.eqlin.marginals if r.status == 0 else np.full(X.shape[1], np.nan)


def qr_primal(y, X, tau):
    n, k = X.shape
    c = np.r_[np.zeros(2 * k), tau * np.ones(n), (1 - tau) * np.ones(n)]
    r = linprog(c, A_eq=np.c_[X, -X, np.eye(n), -np.eye(n)], b_eq=y, bounds=[(0, None)] * (2 * k + 2 * n), method='highs')
    return r.x[:k] - r.x[k:2 * k], r.fun


def qr_range(y, X, tau, j=1):
    """Smallest and largest coefficient j over the set of minimizers (referee 3, c1c_nonunique.py)."""
    n, k = X.shape
    c = np.r_[np.zeros(2 * k), tau * np.ones(n), (1 - tau) * np.ones(n)]
    A, bnd = np.c_[X, -X, np.eye(n), -np.eye(n)], [(0, None)] * (2 * k + 2 * n)
    fmin = linprog(c, A_eq=A, b_eq=y, bounds=bnd, method='highs').fun
    out = []
    for s in (1, -1):
        cs = np.zeros(2 * k + 2 * n)
        cs[j], cs[k + j] = s, -s
        r = linprog(cs, A_ub=c[None, :], b_ub=[fmin * (1 + 1e-10) + 1e-12], A_eq=A, b_eq=y, bounds=bnd, method='highs')
        out.append(float(r.x[j] - r.x[k + j]))
    return out


def check_loss(y, X, b, tau):
    u = y - X @ b
    return float(np.sum(u * (tau - (u < 0))))


def qmask(z, m, lo=0.0, hi=0.6, per=None, years=None):
    g, y = z['g'], z[m]
    k = fin(g) & fin(y) & (g >= lo) & (g <= hi)
    if per is not None:
        k &= np.isin(z['per'], per)
    if years is not None:
        yr = z['year']
        k &= (yr >= years[0]) & (yr <= years[1])
    return k


def qslope(z, m, tau=0.9, lo=0.0, hi=0.6, per=None, years=None, min_n=30):
    k = qmask(z, m, lo, hi, per, years)
    n = int(k.sum())
    if n < min_n:
        return np.nan
    return float(qr_fit(z[m][k], np.c_[np.ones(n), z['g'][k]], tau)[1])


# ---- (a) local conditional quantile slopes (descriptive under D-2)
SPL = {'pooled': [0, 1, 2, 3], '2010_19': [0, 1], '2020_25': [2, 3]}
SLOPE_NAMES = [f'slope_{b}_{sp}' for b in BASES for sp in SPL] + [f'slope_{b}_2020_25_minus_2010_19' for b in BASES]


def f_slopes(z, vn):
    s = [qslope(z, BASES[b][0], per=per) for b in BASES for sp, per in SPL.items()]
    return s + [s[2] - s[1], s[5] - s[4]]


TAUS = [0.80, 0.85, 0.90, 0.95]
WINS = [0.4, 0.6, 0.8, 1.0]
GRID_NAMES = [f'slope_{b}_t{int(round(100 * t))}_w{int(round(100 * w))}' for b in BASES for t in TAUS for w in WINS]


def f_grid(z, vn):
    return [qslope(z, BASES[b][0], tau=t, hi=w) for b in BASES for t in TAUS for w in WINS]


# ---- (b) dominance-cone frontier Psi_chi (primary under D-2)
GRIDF = np.round(np.arange(0, 1.0001, 0.05), 2)
GPTS = [0.0, 0.2, 0.4, 0.6]
PERW = [0.6, 0.4]                                          # windows of the period slopes (cells at 60% growth are small within periods)
CONE_PARTS = ([f'slope_c{int(round(100 * c))}_w{int(round(100 * w))}' for c in TAUS for w in WINS]
              + [f'slope_c90_w{int(round(100 * w))}_{x}' for w in PERW for x in ('2010_19', '2020_25', '2020_25_minus_2010_19',
                                                                                 '2010_15', '2018_25', '2018_25_minus_2010_15')]
              + [f'slope_orderm25_w{int(round(100 * w))}' for w in WINS]
              + [f'{o}_g{int(round(100 * g0)):02d}' for o in ('phi90', 'phi95', 'orderm25') for g0 in GPTS]
              + ['cell60'])                                   # round 2 (B13): firm-years in the 60% cell, sample and draws
CONE_NAMES = [f'cone_{b}_{x}' for b in BASES for x in CONE_PARTS]
_LSW = {}
for _w in WINS:
    _x = GRIDF[GRIDF <= _w + 1e-9]
    _LSW[_w] = (len(_x), (_x - _x.mean()) / ((_x - _x.mean()) ** 2).sum())


def cone_mat(g, y, chis=TAUS, om=True, min_n=MIN_CELL):
    """phi_chi(g0) for chi in chis (rows) and the order-m (M = 25) frontier (last row) on GRIDF; NaN below min_n firm-years.
    Grid points enter a statistic when the sample cell has at least 30 firm-years (estimate_frontier.py); inside a
    bootstrap draw a grid point needs 10 (the T(g0) rule), so that a draw is undefined only when the cell nearly empties."""
    res = np.full((len(chis) + 1, len(GRIDF)), np.nan)
    o = np.argsort(-g, kind='stable')
    ys, ng = y[o], -g[o]
    cnt = np.searchsorted(ng, -GRIDF, side='right')
    for i, n in enumerate(cnt):
        if n < min_n:
            continue
        s = np.sort(ys[:n])
        res[:len(chis), i] = np.quantile(s, chis)
        if om:
            j = np.arange(1, n + 1)
            res[-1, i] = ((j / n) ** 25 - ((j - 1) / n) ** 25) @ s
    return res, cnt


def wslope(v, w):
    n, wt = _LSW[w]
    v = v[:n]
    return float(wt @ v) if np.all(fin(v)) else np.nan


def cone_min(z):
    return MIN_CELL if z.idx is None else 10


def f_cone(z, vn):
    out = []
    g, per, yr = z['g'], z['per'], z['year']
    mn = cone_min(z)
    for b in BASES:
        y = z[BASES[b][0]]
        k = fin(g) & fin(y)
        R, cnt_ = cone_mat(g[k], y[k], min_n=mn)
        out += [wslope(R[ci], w) for ci in range(len(TAUS)) for w in WINS]
        rows = [cone_mat(g[kk], y[kk], chis=[0.9], om=False, min_n=mn)[0][0] for kk in (
            k & np.isin(per, [0, 1]), k & np.isin(per, [2, 3]), k & (yr >= 2010) & (yr <= 2015), k & (yr >= 2018) & (yr <= 2025))]
        for w in PERW:
            a, c, e, f = (wslope(r_, w) for r_ in rows)
            out += [a, c, c - a, e, f, f - e]
        out += [wslope(R[-1], w) for w in WINS]
        ix = [int(round(g0 / 0.05)) for g0 in GPTS]
        out += [R[2, i] for i in ix] + [R[3, i] for i in ix] + [R[-1, i] for i in ix]
        out += [float(cnt_[int(round(0.60 / 0.05))])]
    return out


# ---- (c) spend ratio and the bounds on the growth weight (D-1)
FLOORS = [0.05, 0.10, 0.15, 0.20, 0.30]
GCONST = [0.05, 0.08, 0.12]
SPEND_NAMES = (['spend_ratio', 'spend_q25', 'spend_q75', 'spend_med_sm', 'spend_med_excess', 'spend_n']
               + [f'spend_terc{i}_{x}' for x in ('ratio', 'excess', 'sm') for i in (1, 2, 3)]
               + [f'spend_floor{int(round(100 * f)):02d}_ratio' for f in FLOORS]
               + ['spend_maint_base', 'spend_maint_ratio']
               + [f'spend_G{int(round(100 * c)):02d}_ratio' for c in GCONST] + ['spend_G00_ratio', 'spend_Gp25_ratio', 'spend_Gp75_ratio']
               + ['foc_ols_ye_above', 'foc_medreg_above_slope', 'foc_medreg_above_intercept', 'foc_medreg_above_zero_spend_growth',
                  'foc_ols_ye_all', 'foc_fe_all', 'foc_medreg_excess_slope', 'foc_ls_origin_excess']
               + ['spend_ratio_of_medians', 'spend_share_ratio_gt10'])


def spend_ratio(z):
    g, s, G = z['g'], z['sm_lag_share'], z['G_t']
    k = fin(s) & (s >= 0.01) & (s <= 1.5) & (g > G)
    return med(s[k] / (g[k] - G[k]))


def demean(v, groups):
    out = []
    for gi in groups:
        cnt = np.bincount(gi)
        out.append(cnt)
    w = v.astype(float).copy()
    for _ in range(500):
        w0 = w
        for gi, cnt in zip(groups, out):
            w = w - (np.bincount(gi, w) / cnt)[gi]
        if np.max(np.abs(w - w0)) < 1e-11:
            break
    return w


def fe_slope(y, x, groups):
    yt, xt = demean(y, groups), demean(x, groups)
    return float((xt @ yt) / (xt @ xt))


def f_spend(z, vn):
    g, s, G, yr = z['g'], z['sm_lag_share'], z['G_t'], z['year']
    sok = fin(s) & (s >= 0.01) & (s <= 1.5) & fin(g)
    k = sok & (g > G)
    ex, sk = g[k] - G[k], s[k]
    r = sk / ex
    out = [med(r), q(r, .25), q(r, .75), med(sk), med(ex), float(len(r))]
    t1, t2 = np.quantile(ex, [1 / 3, 2 / 3])
    bins = [ex <= t1, (ex > t1) & (ex <= t2), ex > t2]
    out += [med(r[b_]) for b_ in bins] + [med(ex[b_]) for b_ in bins] + [med(sk[b_]) for b_ in bins]
    out += [med(r[ex > f]) for f in FLOORS]
    base = med(s[sok & (g <= G)])
    out += [base, med((sk - base) / ex)]
    for Gb in [np.full(len(g), c) for c in GCONST] + [np.zeros(len(g)), z['G_p25'], z['G_p75']]:
        kk = sok & (g > Gb)
        out.append(med(s[kk] / (g[kk] - Gb[kk])))
    yi = np.unique(yr, return_inverse=True)[1]
    out.append(fe_slope(sk, g[k], [yi[k]]))
    bm = qr_fit(sk, np.c_[np.ones(len(sk)), g[k]], 0.5)
    out += [float(bm[1]), float(bm[0]), float(-bm[0] / bm[1]) if bm[1] != 0 else np.nan]
    fi = np.unique(z['cik'], return_inverse=True)[1]
    out += [fe_slope(s[sok], g[sok], [yi[sok]]), fe_slope(s[sok], g[sok], [fi[sok], yi[sok]])]
    be = qr_fit(sk, np.c_[np.ones(len(ex)), ex], 0.5)
    out += [float(be[1]), float((sk * ex).sum() / (ex * ex).sum())]
    out += [med(sk) / med(ex), float((r > 10).mean())]
    return out


# ---- (d) size gradient
SCALE_SPECS = [('', False, None), ('_fe', True, None), ('_g150', False, 1.5), ('_fe_g150', True, 1.5)]
SCALE_NAMES = [f'scale_tenfold{sfx}_{b}' for b in BASES for sfx, _, _ in SCALE_SPECS] + [f'scale_p95_{b}_{sk}' for b in BASES for sk in SIZE_KEYS]


def scale_one(z, R, fe=False, gmax=None):
    y, ls, g = z[R], z['lsize'], z['g']
    k = fin(y) & fin(ls) & fin(g) & (z['sb'] >= 0)
    if gmax is not None:
        k &= g <= gmax
    n = int(k.sum())
    X = np.c_[np.ones(n), ls[k]]
    if fe:
        X = np.c_[X, (z['per'][k][:, None] == np.array([1, 2, 3])[None, :]).astype(float)]
    return float(qr_fit(y[k], X, .95)[1]) * LN10


def f_scale(z, vn):
    out = [scale_one(z, BASES[b][1], fe, gm) for b in BASES for _, fe, gm in SCALE_SPECS]
    for b in BASES:
        y = z[BASES[b][1]]
        k = fin(y) & fin(z['lsize']) & (z['sb'] >= 0)
        out += [q(y[k & (z['sb'] == i)], .95) for i in range(4)]
    return out


# ---- (e) capital intensity: split re-estimated in each draw; sorts on same-year, prior-year and firm-median intensity
SORTS = {'': 'capex_int', '_prior': 'k_lag', '_firmmed': 'k_firmmed'}
CAP_BASES = ['op', 'cash', 'cashadd']
CAP_NAMES = ([f'capint_gap_{cb}_{pk}{sfx}' for pk in PK for sfx in SORTS for cb in CAP_BASES]
             + [f'capint_{lvl}_{b}_2023_25' for b in BASES for lvl in ('hi', 'lo')]
             + [f'capint_interaction_{b}_{w}' for b in BASES for w in ('pooled', '2023_25')])


def split(z, p, kcol):
    kv = z[kcol]
    ok = (z['per'] == p) & fin(kv)
    if not ok.any():
        return ok, ok
    m_ = np.median(kv[ok])
    return ok & (kv > m_), ok & (kv <= m_)


def capint_score(z, cb):
    return z['R_cash'] + z['capex_int'] if cb == 'cashadd' else z[BASES[cb][1]]


def f_capint(z, vn):
    out = []
    for p in range(4):
        for sfx, kcol in SORTS.items():
            hi, lo = split(z, p, kcol)
            for cb in CAP_BASES:
                y = capint_score(z, cb)
                out.append(q(y[hi], .95) - q(y[lo], .95))
    hi, lo = split(z, 3, 'capex_int')
    for b in BASES:
        y = z[BASES[b][1]]
        out += [q(y[hi], .95), q(y[lo], .95)]
    hia, oka = np.zeros(len(z), bool), np.zeros(len(z), bool)
    for p in range(4):
        hi, lo = split(z, p, 'capex_int')
        hia |= hi
        oka |= hi | lo
    for b in BASES:
        m = BASES[b][0]
        for pers in ([0, 1, 2, 3], [3]):
            k = oka & qmask(z, m, per=pers)
            gg, h = z['g'][k], hia[k].astype(float)
            out.append(float(qr_fit(z[m][k], np.c_[np.ones(len(gg)), gg, h, gg * h], .9)[3]))
    return out


# ---- (f) upper quantiles, frontier points, margin gap
TOP_NAMES = [f'{s}_{b}' if s.endswith('change') else f'p95_{b}_{s}' for b in BASES for s in ('2016_19', '2023_25', 'p95_change', 'p90_change')]


def f_top(z, vn):
    out = []
    for b in BASES:
        y, per = z[BASES[b][1]], z['per']
        a, c = y[per == 1], y[per == 3]
        out += [q(a, .95), q(c, .95), q(c, .95) - q(a, .95), q(c, .90) - q(a, .90)]
    return out


G0S = [0.0, 0.1, 0.2, 0.3, 0.4]
T_NAMES = [f'T_{b}_g{int(round(100 * g0)):02d}_change' for b in BASES for g0 in G0S]


def Tval(z, m, g0, p):
    g, y = z['g'], z[m]
    s = y[(z['per'] == p) & fin(g) & fin(y) & (g >= g0)]
    return g0 + float(np.quantile(s, .95)) if len(s) >= 10 else np.nan


def f_T(z, vn):
    return [Tval(z, BASES[b][0], g0, 3) - Tval(z, BASES[b][0], g0, 1) for b in BASES for g0 in G0S]


GB_EDGES = np.array([0.1, 0.2, 0.3, 0.4])


def gap_rows(z):
    g, mo = z['g'], z['m_op']
    ok = fin(mo) & fin(z['gm']) & fin(z['sms']) & fin(z['rds']) & fin(z['gas']) & (g >= 0) & (g < 0.6)
    band = np.searchsorted(GB_EDGES, g[ok], side='right')
    cols = {c: z[c][ok] for c in ('m_op', 'gm', 'sms', 'rds', 'gas', 'oth')}
    rows = {}
    for b_ in range(5):
        w = band == b_
        if not w.any():
            continue
        x = cols['m_op'][w]
        top = x >= np.quantile(x, .9)
        mid = (x >= np.quantile(x, .4)) & (x <= np.quantile(x, .6))
        if top.sum() < 3 or mid.sum() < 3:
            continue
        d = {c: np.nanmean(v[w][top]) - np.nanmean(v[w][mid]) for c, v in cols.items()}
        rows[b_] = dict(gap=d['m_op'], gm=d['gm'], sm=-d['sms'], rd=-d['rds'], ga=-d['gas'], oth=-d['oth'])
    return rows


def f_gap(z, vn):
    rows = gap_rows(z)
    avg = {k_: np.nanmean([r[k_] for r in rows.values()]) if rows else np.nan for k_ in ('gap', 'gm', 'sm', 'rd', 'ga', 'oth')}
    b0, b4 = rows.get(0, {}), rows.get(4, {})
    return [avg['gap'], avg['gm'], avg['sm'], avg['rd'], avg['ga'], avg['oth'], b0.get('gap', np.nan), b0.get('gm', np.nan),
            b4.get('gap', np.nan), b4.get('sm', np.nan), b4.get('rd', np.nan)]


# ---- (g) composition: yearly series, regimes, reweighting
YEARS = list(range(2010, 2026))
YEARLY_NAMES = ([f'p95_{b}_{y}' for b in BASES for y in YEARS] + [f'slope_{b}_{y}' for b in BASES for y in YEARS]
                + [f'p95_change_{b}_2016_19_to_{w}' for b in BASES for w in ('2025', '2023_24')] + [f'slope_yearfe_{b}' for b in BASES])


def f_yearly(z, vn):
    yr, per = z['year'], z['per']
    p95, sl, ch, fe = [], [], [], []
    for b, (m, R, _) in BASES.items():
        y = z[R]
        p95 += [q(y[yr == t], .95) for t in YEARS]
        sl += [qslope(z, m, years=(t, t)) for t in YEARS]
        a = q(y[per == 1], .95)
        ch += [q(y[yr == 2025], .95) - a, q(y[(yr == 2023) | (yr == 2024)], .95) - a]
        k = qmask(z, m)
        D = (yr[k][:, None] == np.array(YEARS[1:])[None, :]).astype(float)
        fe.append(float(qr_fit(z[m][k], np.c_[np.ones(k.sum()), z['g'][k], D], .9)[1]))
    return p95 + sl + ch + fe


REG_NAMES = [f'slope_{b}_{r}' for b in BASES for r in ('2010_15', '2018_25', '2018_25_minus_2010_15')]


def f_regimes(z, vn):
    out = []
    for b in BASES:
        a, c = qslope(z, BASES[b][0], years=(2010, 2015)), qslope(z, BASES[b][0], years=(2018, 2025))
        out += [a, c, c - a]
    return out


def wq(x, w, p):
    k = w > 0
    x, w = x[k], w[k]
    o = np.argsort(x, kind='stable')
    x, w = x[o], w[o]
    # round 2 (E2-minor): the type-7 (linear) definition used by np.quantile everywhere else; with unit weights this is
    # np.quantile exactly (v2 used Hazen plotting positions, (cumsum - w/2)/sum)
    c = (np.cumsum(w) - w) / (w.sum() - w[-1])
    return float(np.interp(p, c, x))


RW_PARTS = ['p95_2016_19', 'p95_2023_25', 'total', 'cf_2023_25_at_2016_19_growth_mix', 'within_A', 'composition_A',
            'cf_2016_19_at_2023_25_growth_mix', 'composition_B', 'within_B', 'cf_2023_25_at_2016_19_size_mix', 'within_size']
RW_NAMES = [f'rw_{b}_{x}' for b in BASES for x in RW_PARTS]


def _bins(x, e):
    return np.clip(np.searchsorted(e, x, 'left') - 1, 0, len(e) - 2)


def _w(fa, fb, bb):
    return np.where(fb[bb] > 0, fa[bb] / np.where(fb[bb] > 0, fb[bb], 1), 0.0)


def f_reweight(z, vn):
    out = []
    g, per, rl = z['g'], z['per'], z['rev_lag']
    for b in BASES:
        y = z[BASES[b][1]]
        a, c = (per == 1) & fin(y), (per == 3) & fin(y)
        ga, gc, ya, yc = g[a], g[c], y[a], y[c]
        e = np.unique(np.quantile(np.r_[ga, gc], np.linspace(0, 1, 11)))
        e[0], e[-1] = e[0] - 1, e[-1] + 1
        nb = len(e) - 1
        ba, bc = _bins(ga, e), _bins(gc, e)
        fa, fc = np.bincount(ba, minlength=nb) / len(ba), np.bincount(bc, minlength=nb) / len(bc)
        oa, oc = wq(ya, np.ones(len(ya)), .95), wq(yc, np.ones(len(yc)), .95)
        cfc, cfa = wq(yc, _w(fa, fc, bc), .95), wq(ya, _w(fc, fa, ba), .95)
        se = np.array(SIZE_BINS, float)
        sa, sc = _bins(rl[a], se), _bins(rl[c], se)
        fsa, fsc = np.bincount(sa, minlength=4) / len(sa), np.bincount(sc, minlength=4) / len(sc)
        cfs = wq(yc, _w(fsa, fsc, sc), .95)
        out += [oa, oc, oc - oa, cfc, cfc - oa, oc - cfc, cfa, cfa - oa, oc - cfa, cfs, cfs - oa]
    return out


# ---- (h) calibration anchor
ANCH_STATS = ['n', 'firms', 'cutoff', 'G', 'R_med', 'm0_ub_q1', 'm0_ub_med', 'm0_ub_q3', 'm0_lb_med', 'Pi_ub_q1', 'Pi_ub_med',
              'Pi_ub_q3', 'Pi_lb_q1', 'Pi_lb_med', 'Pi_lb_q3', 'share_Pi_ub_pos', 'transient_ub', 'transient_lb',
              # round 2 (decision 4, final audit m13): the maintenance-netted central basis, sigma = max(S&M - b_M, 0) with
              # b_M the median lagged S&M share of firm-years growing at or below the year median, recomputed in each draw
              'maint_base', 'm0_net_med', 'Pi_net_q1', 'Pi_net_med', 'Pi_net_q3']
ANCH_CUTS = {'p95': 0.95, 'p975': 0.975}
ANCH_NAMES = [f'anchor_{c}_{s}' for c in ANCH_CUTS for s in ANCH_STATS]


def anchor_vec(z, cutq, drop_flagged):
    p = z['per'] == 3
    g, m = z['g'][p], z['m_fcf_sbc'][p]
    R = g + m
    G = med(g)
    cut = q(R, cutq)
    t = fin(R) & (R >= cut)
    if drop_flagged:
        t &= z['acq_flag'][p] == 0
    if not t.any():
        return [np.nan] * len(ANCH_STATS)
    gt, mt, Rt = g[t], m[t], R[t]
    sig = np.nan_to_num(z['sm'][p][t] / z['rev'][p][t], nan=0.0)
    kg = np.nan_to_num(z['capex_int'][p][t], nan=0.0)
    kk = np.where(gt > 0, kg / np.where(gt > 0, gt, 1), 0.0)
    m0u, m0l = mt + (1 - TAU_CAL) * sig + kg, mt + kg
    piu, pil = Rt - (m0u + (1 - kk) * G), Rt - (m0l + (1 - kk) * G)
    s_, gg, GG = z['sm_lag_share'], z['g'], z['G_t']
    bM = med(s_[fin(s_) & (s_ >= 0.01) & (s_ <= 1.5) & fin(gg) & (gg <= GG)])
    m0n = mt + (1 - TAU_CAL) * np.maximum(sig - bM, 0.0) + kg
    pin = Rt - (m0n + (1 - kk) * G)
    Rm = float(np.median(Rt))
    return [float(t.sum()), float(len(np.unique(z['cik'][p][t]))), cut, G, Rm, q(m0u, .25), med(m0u), q(m0u, .75), med(m0l),
            q(piu, .25), med(piu), q(piu, .75), q(pil, .25), med(pil), q(pil, .75), float((piu > 0).mean()), med(piu) / Rm, med(pil) / Rm,
            bM, med(m0n), q(pin, .25), med(pin), q(pin, .75)]


def f_anchor(z, vn):
    return [x for c, cq in ANCH_CUTS.items() for x in anchor_vec(z, cq, drop_flagged=(vn == 'E1'))]


# ---- (i) stochastic frontier: common frontier per period, JLMS E[u | e], cohorts, balanced panel
SFA_PARTS = [f'{pk}_{x}' for pk in ('2016_19', '2023_25') for x in ('mean_shortfall', 'jlms_2019plus', 'jlms_pre2019', 'cohort_gap')] + \
            ['balanced_jlms_2016_19', 'balanced_jlms_2023_25', 'balanced_change', 'entrants_minus_balanced_2023_25']
SFA_NAMES = [f'sfa_{b}_{x}' for b in BASES for x in SFA_PARTS]
SFA_X0 = {}


def sfa_fit(y, X, x0=None):
    k = X.shape[1]
    if x0 is None:
        x0 = np.r_[np.linalg.lstsq(X, y, rcond=None)[0], np.log(0.2), np.log(0.1)]

    def nll(th):
        b_, su, sv = th[:k], np.exp(th[k]), np.exp(th[k + 1])
        e = y - X @ b_
        s = np.sqrt(su ** 2 + sv ** 2)
        return -(np.log(2) - np.log(s) + sst.norm.logpdf(e / s) + sst.norm.logcdf(-e * (su / sv) / s)).sum()
    r = optimize.minimize(nll, x0, method='BFGS')
    b_, su, sv = r.x[:k], np.exp(r.x[k]), np.exp(r.x[k + 1])
    e = y - X @ b_
    s2 = su ** 2 + sv ** 2
    mus, ss = -e * su ** 2 / s2, su * sv / np.sqrt(s2)
    jl = mus + ss * np.exp(sst.norm.logpdf(mus / ss) - sst.norm.logcdf(mus / ss))     # E[u | e], Jondrow et al. (1982)
    return su * np.sqrt(2 / np.pi), jl, r.x


def f_sfa(z, vn):
    out = []
    for b in BASES:
        m = BASES[b][0]
        J = {}
        for p in (1, 3):
            g, y = z['g'], z[m]
            k = (z['per'] == p) & fin(g) & fin(y) & (g <= 1.5) & (y > -1.5)
            gg = g[k]
            mu, jl, xx = sfa_fit(y[k], np.c_[np.ones(len(gg)), gg, gg * gg], SFA_X0.get((vn, b, p)))
            if z.idx is None:
                SFA_X0[(vn, b, p)] = xx
            coh = z['coh19'][k]
            out += [mu, jl[coh == 1].mean(), jl[coh == 0].mean(), jl[coh == 1].mean() - jl[coh == 0].mean()]
            J[p] = (z['cik'][k], jl, coh)
        both = np.intersect1d(J[1][0], J[3][0])
        j1, j3 = J[1][1][np.isin(J[1][0], both)].mean(), J[3][1][np.isin(J[3][0], both)].mean()
        out += [j1, j3, j3 - j1, J[3][1][J[3][2] == 1].mean() - j3]
    return out


# ---- (i2) B5 bridge: cash score before interest paid and cash taxes, and before interest only
BRIDGE_BASES = {'op': ('m_op', 'R_op'), 'cash': ('m_fcf_sbc', 'R_cash'), 'cash_bs': ('m_cash_bs', 'R_cash_bs'),
                'cash_pre': ('m_cash_pre', 'R_cash_pre'), 'cash_bi': ('m_cash_bi', 'R_cash_bi')}
if II:                                                              # round 2 (D1): before net interest, and the paper's basis on its firm-years
    BRIDGE_BASES.update(cash_bni=('m_cash_bni', 'R_cash_bni'), cash_bnis=('m_cash_bnis', 'R_cash_bnis'))
BRIDGE_PARTS = ['p95_2016_19', 'p95_2023_25', 'p95_change', 'med_2016_19', 'med_2023_25', 'med_change', 'med_2010_25',
                'margin_med_2010_25', 'margin_med_2016_19', 'margin_med_2023_25', 'n_2016_19', 'n_2023_25']
BRIDGE_NAMES = [f'bridge_{b}_{x}' for b in BRIDGE_BASES for x in BRIDGE_PARTS]


def f_bridge(z, vn):
    out = []
    per = z['per']
    for b, (m, R) in BRIDGE_BASES.items():
        y, mm = z[R], z[m]
        a, c = y[per == 1], y[per == 3]
        out += [q(a, .95), q(c, .95), q(c, .95) - q(a, .95), med(a), med(c), med(c) - med(a), med(y), med(mm),
                med(mm[per == 1]), med(mm[per == 3]), float(fin(a).sum()), float(fin(c).sum())]
    return out


# ---- (j) joint draw for the familywise corrections
REF32 = (['slope_op_pooled', 'slope_cash_pooled', 'slope_op_2010_19', 'slope_cash_2010_19', 'slope_op_2020_25', 'slope_cash_2020_25',
          'spend_ratio', 'scale_tenfold_op', 'scale_tenfold_cash', 'capint_gap_op_2023_25', 'capint_gap_cash_2023_25',
          'p95_change_op', 'p95_change_cash', 'p90_change_op', 'p90_change_cash']
         + [f'T_{b}_g{g0}_change' for b in BASES for g0 in ('00', '20', '40')] + GAP_KEYS)
PSI = [f'cone_{b}_slope_c90_{sp}' for b in BASES for sp in ('w60', 'w40_2010_19', 'w40_2020_25')]
FULL38 = PSI + REF32
JOINT_NAMES = FULL38 + ['slope_op_2020_25_minus_2010_19', 'cone_op_slope_c90_w40_2020_25_minus_2010_19']


def f_joint(z, vn):
    s = f_slopes(z, vn)
    psi = []
    g, per = z['g'], z['per']
    mn = cone_min(z)
    for b in BASES:
        y = z[BASES[b][0]]
        k = fin(g) & fin(y)
        for kk, w in ((k, 0.6), (k & np.isin(per, [0, 1]), 0.4), (k & np.isin(per, [2, 3]), 0.4)):
            psi.append(wslope(cone_mat(g[kk], y[kk], chis=[0.9], om=False, min_n=mn)[0][0], w))
    hi, lo = split(z, 3, 'capex_int')
    tp = f_top(z, vn)
    return (psi + [s[0], s[3], s[1], s[4], s[2], s[5]] + [spend_ratio(z), scale_one(z, 'R_op'), scale_one(z, 'R_cash')]
            + [q(z[BASES[b][1]][hi], .95) - q(z[BASES[b][1]][lo], .95) for b in BASES]
            + [tp[2], tp[6], tp[3], tp[7]]
            + [Tval(z, BASES[b][0], g0, 3) - Tval(z, BASES[b][0], g0, 1) for b in BASES for g0 in (0.0, 0.2, 0.4)]
            + f_gap(z, vn) + [s[6], psi[2] - psi[1]])


# block: (function, statistic names, bootstrapped variants, paired E1 - E2, also on the point-only variants)
BLOCKS = {
    'slopes': (f_slopes, SLOPE_NAMES, BOOTV, True, True),
    'cone': (f_cone, CONE_NAMES, BOOTV, True, True),
    'spend': (f_spend, SPEND_NAMES, BOOTV, True, True),
    'scale': (f_scale, SCALE_NAMES, BOOTV, True, True),
    'capint': (f_capint, CAP_NAMES, BOOTV, True, True),
    'top': (f_top, TOP_NAMES, BOOTV, True, True),
    'T': (f_T, T_NAMES, BOOTV, True, True),
    'gap': (f_gap, GAP_KEYS, BOOTV, True, True),
    'anchor': (f_anchor, ANCH_NAMES, BOOTV + ['E1all'], True, False),
    'sfa': (f_sfa, SFA_NAMES, MFV, True, False),
    'grid': (f_grid, GRID_NAMES, PAIRV, True, False),
    'yearly': (f_yearly, YEARLY_NAMES, PAIRV, True, False),
    'regimes': (f_regimes, REG_NAMES, PAIRV, True, False),
    'reweight': (f_reweight, RW_NAMES, PAIRV, True, False),
    'joint': (f_joint, JOINT_NAMES, PAIRV, True, False),
    'bridge': (f_bridge, BRIDGE_NAMES, PAIRV, True, False),
}
if PANEL == 'v2':                                   # the v2 run serves the old-versus-new comparison of the headlines
    BLOCKS = {k_: v_ for k_, v_ in BLOCKS.items() if k_ not in ('sfa', 'grid', 'yearly', 'regimes', 'reweight', 'bridge')}
COST = dict(yearly=10, grid=9, scale=6, slopes=5, capint=4, joint=4, sfa=5, cone=2, regimes=1, spend=2, gap=2, top=1, T=1, reweight=1, anchor=1, bridge=1)
SEEDS = {bn: seed_for(bn) for bn in BLOCKS}


# =============================================================================================== 3. summaries (functions)
def summarize(est, bs, h0=0.0, interval=True, why=None):
    bs = np.asarray(bs, float)
    nb = len(bs)
    ok = fin(bs)
    rec = dict(est=float(est), B=nb, n_nan=int((~ok).sum()), nan_share=float((~ok).mean()) if nb else None)
    if not fin(est):
        rec.update(estimable=False, note='no point estimate (cell below the minimum or empty)')
        return rec
    if nb == 0:
        return rec
    if rec['nan_share'] > NAN_MAX:
        rec.update(estimable=False, note=f'{100 * rec["nan_share"]:.0f}% of draws undefined (limit {100 * NAN_MAX:.0f}%): no interval')
        return rec
    if not interval:
        rec.update(estimable=False, note=why or 'no interval')
        return rec
    b = bs[ok]
    n = len(b)
    se = float(b.std(ddof=1))
    lo90, hi90, lo95, hi95 = np.quantile(b, [.05, .95, .025, .975])
    z0 = sst.norm.ppf(np.clip((np.sum(b < est) + 0.5 * np.sum(b == est)) / n, 1 / (n + 1), n / (n + 1)))
    bc = np.quantile(b, [sst.norm.cdf(2 * z0 - 1.6449), sst.norm.cdf(2 * z0 + 1.6449)])
    two = lambda x: float(min(1.0, 2 * min((np.sum(x <= h0) + 1) / (n + 1), (np.sum(x >= h0) + 1) / (n + 1))))
    rec.update(estimable=True, se=se, bias=float(b.mean() - est), boot_mean=float(b.mean()), h0=h0,
               ci90=[float(lo90), float(hi90)], ci95=[float(lo95), float(hi95)],
               ci90_basic=[float(2 * est - hi90), float(2 * est - lo90)], ci95_basic=[float(2 * est - hi95), float(2 * est - lo95)],
               ci90_normal=[est - 1.6449 * se, est + 1.6449 * se], ci95_normal=[est - 1.96 * se, est + 1.96 * se],
               ci90_bc=[float(bc[0]), float(bc[1])],
               p_normal=float(2 * sst.norm.sf(abs(est - h0) / se)) if se > 0 else None,
               p_percentile=two(b), p_basic=two(2 * est - b))
    return rec


def holm(p):
    p = np.asarray([1.0 if x is None or not fin(x) else x for x in p], float)
    o, adj, run = np.argsort(p, kind='stable'), np.empty(len(p)), 0.0
    for r_, i in enumerate(o):
        run = max(run, min(1.0, (len(p) - r_) * p[i]))
        adj[i] = run
    return adj


def romano_wolf(e, h0, bs):
    """Studentized step-down; contrasts without an estimate or with more than NAN_MAX undefined draws get 1."""
    col = fin(e) & (np.isfinite(bs).mean(axis=0) >= 1 - NAN_MAX)
    okr = np.isfinite(bs[:, col]).all(axis=1)
    b2 = bs[okr][:, col]
    se = b2.std(axis=0, ddof=1)
    t = np.abs((e[col] - h0[col]) / se)
    tb = np.abs((b2 - e[col]) / se)
    o, adj_c, run = np.argsort(-t, kind='stable'), np.empty(len(t)), 0.0
    for r_, i in enumerate(o):
        mx = tb[:, o[r_:]].max(axis=1)
        run = max(run, (np.sum(mx >= t[i]) + 1) / (len(mx) + 1))
        adj_c[i] = run
    adj = np.ones(len(e))
    adj[col] = adj_c
    return adj, int(okr.sum())


def work(task):
    bn, i0, i1 = task
    fn, names, vns = BLOCKS[bn][0], BLOCKS[bn][1], BLOCKS[bn][2]
    out = np.full((i1 - i0, len(vns), len(names)), np.nan)
    nerr = 0
    for r, i in enumerate(range(i0, i1)):
        for c, vn in enumerate(vns):
            try:
                out[r, c] = fn(drawn(vn, DRAW_IDX[bn][i]), vn)
            except Exception:
                nerr += 1
    return bn, i0, out, nerr


def clean(o):
    if isinstance(o, dict):
        return {str(k_): clean(v_) for k_, v_ in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v_) for v_ in o]
    if isinstance(o, np.ndarray):
        return clean(o.tolist())
    if isinstance(o, (np.floating, np.integer, np.bool_)):
        o = o.item()
    if isinstance(o, float) and not math.isfinite(o):
        return None
    return o


def anchor_block(df, drop_flagged, cutq=0.95):
    """Rules of calibrate_horizons.py and code/estimate_organic.py (anchor_block), with cut-off quantile cutq."""
    d = df[df.period == '2023-25'].copy()
    d['R'] = d.g + d.m_fcf_sbc
    G, p95, m_p95 = float(d.g.median()), float(d.R.quantile(cutq)), float(d.m_fcf_sbc.quantile(cutq))
    tail = d[d.R >= p95].copy()
    top = tail[tail.acq_flag == 0].copy() if drop_flagged else tail.copy()
    top['sig_ub'] = (top.sm / top.rev).fillna(0.0)
    top['kg'] = top.capex_int.fillna(0.0)
    top['k'] = np.where(top.g > 0, top.kg / top.g, 0.0)
    top['m0_ub'] = top.m_fcf_sbc + (1 - TAU_CAL) * top.sig_ub + top.kg
    top['m0_lb'] = top.m_fcf_sbc + top.kg
    for b_ in ['ub', 'lb']:
        top['Rinf_' + b_] = top['m0_' + b_] + (1 - top.k) * G
        top['Pi_' + b_] = top.R - top['Rinf_' + b_]
    q3 = lambda s: [float(s.quantile(.25)), float(s.quantile(.5)), float(s.quantile(.75))]
    blk = dict(cut_quantile=cutq, n_tail=int(len(tail)), n_tail_m_above_p95=int((tail.m_fcf_sbc > m_p95).sum()), m_p95_all=m_p95,
               n=int(len(top)), n_firms=int(top.cik.nunique()), n_acq_excluded=int(len(tail) - len(top)), n_sm_missing=int(top.sm.isna().sum()),
               p95=p95, G=G, tau=TAU_CAL, R=q3(top.R), m=q3(top.m_fcf_sbc), sig_ub=q3(top.sig_ub),
               **{f'{v_}_{b_}': q3(top[f'{v_}_{b_}']) for v_ in ['m0', 'Rinf', 'Pi'] for b_ in ['ub', 'lb']},
               shift=float(top.m0_ub.median() - top.m0_lb.median()), firms=sorted(top.name.unique().tolist()),
               firm_years_per_firm={k_: int(v_) for k_, v_ in top.groupby('name').size().sort_values(ascending=False).items()},
               n_sample_2023_25=int(len(d)), n_adjusted_pro_forma=int((top.aff & (top.g != top.g_rep)).sum()),
               share_Pi_ub_positive=float((top.Pi_ub > 0).mean()), share_Pi_lb_positive=float((top.Pi_lb > 0).mean()),
               transient_share_ub=float(top.Pi_ub.median() / top.R.median()), transient_share_lb=float(top.Pi_lb.median() / top.R.median()))
    cols = ['cik', 'name', 'year', 'fy_end', 'rev', 'rev_lag', 'g', 'g_rep', 'acq_flag', 'm_fcf_sbc', 'R', 'sm', 'sig_ub',
            'capex_int', 'kg', 'k', 'm0_ub', 'm0_lb', 'Rinf_ub', 'Rinf_lb', 'Pi_ub', 'Pi_lb']
    rows = top.sort_values('R', ascending=False)[cols].rename(columns={'g_rep': 'g_reported', 'g': 'g_used'})
    blk['firm_years'] = [{k_: (None if isinstance(v_, float) and not math.isfinite(v_) else v_) for k_, v_ in r.items()} for r in rows.to_dict(orient='records')]
    for r in blk['firm_years']:
        r['organic_adjusted'] = bool(r['acq_flag'] == 1)
    return blk


FAM14A = [('slope_op_E2', 'Local upper-decile slope, GAAP, E2, against -1', -1.0, 'slope_op_pooled', 'E2'),
          ('slope_cash_E2', 'Local upper-decile slope, FCF after SBC, E2, against -1', -1.0, 'slope_cash_pooled', 'E2'),
          ('weight_E2', 'Implied weight on growth at alpha = 0.45, E2, against the screening weight of 3 (withdrawn, D-1)', 3.0, 'weight_lo', 'E2'),
          ('size_cash_E2', 'Size gradient of P95, FCF after SBC, E2', 0.0, 'scale_tenfold_cash', 'E2'),
          ('capint_cash_E2', 'Capital-intensity gap, FCF after SBC, 2023-25, E2', 0.0, 'capint_gap_cash_2023_25', 'E2'),
          ('p95chg_op_E1', 'Change in P95, GAAP, E1', 0.0, 'p95_change_op', 'E1'),
          ('p95chg_cash_E1', 'Change in P95, FCF after SBC, E1', 0.0, 'p95_change_cash', 'E1'),
          ('T40_cash_E2', 'Change in T(40%), FCF after SBC, E2', 0.0, 'T_cash_g40_change', 'E2'),
          ('gap_E2', 'Near-frontier margin gap, E2', 0.0, 'gap_avg', 'E2'),
          ('gap_fast_sm_E2', 'S&M part of the gap, 40-60% band, E2', 0.0, 'gap_fast_sm', 'E2'),
          ('d_slope_op', 'E1 - E2, local GAAP slope', 0.0, 'slope_op_pooled', 'E1_minus_E2'),
          ('d_size_cash', 'E1 - E2, size gradient, FCF after SBC', 0.0, 'scale_tenfold_cash', 'E1_minus_E2'),
          ('d_T40_cash', 'E1 - E2, change in T(40%), FCF after SBC', 0.0, 'T_cash_g40_change', 'E1_minus_E2'),
          ('slope_op_E2_2020_25_minus_2010_19', 'Local GAAP slope 2020-25 minus 2010-19, E2', 0.0, 'slope_op_2020_25_minus_2010_19', 'E2')]
FAM14B = [('psi_op_E1_vs_m1', 'Psi_0.90 slope, GAAP, E1, against -1', -1.0, 'cone_op_slope_c90_w60', 'E1'),
          ('psi_cash_E1_vs_m1', 'Psi_0.90 slope, FCF after SBC, E1, against -1', -1.0, 'cone_cash_slope_c90_w60', 'E1'),
          ('psi_op_E1_vs_0', 'Psi_0.90 slope, GAAP, E1, against 0', 0.0, 'cone_op_slope_c90_w60', 'E1'),
          ('psi_cash_E1_vs_0', 'Psi_0.90 slope, FCF after SBC, E1, against 0', 0.0, 'cone_cash_slope_c90_w60', 'E1'),
          ('size_cash_E1', 'Size gradient of P95, FCF after SBC, E1', 0.0, 'scale_tenfold_cash', 'E1'),
          ('capint_cash_E1', 'Capital-intensity gap, FCF after SBC, 2023-25, E1', 0.0, 'capint_gap_cash_2023_25', 'E1'),
          ('p95chg_op_E1', 'Change in P95, GAAP, E1', 0.0, 'p95_change_op', 'E1'),
          ('p95chg_cash_E1', 'Change in P95, FCF after SBC, E1', 0.0, 'p95_change_cash', 'E1'),
          ('T40_cash_E1', 'Change in T(40%), FCF after SBC, E1', 0.0, 'T_cash_g40_change', 'E1'),
          ('gap_E1', 'Near-frontier margin gap, E1', 0.0, 'gap_avg', 'E1'),
          ('gap_fast_sm_E1', 'S&M part of the gap, 40-60% band, E1', 0.0, 'gap_fast_sm', 'E1'),
          ('d_psi_op', 'E1 - E2, Psi_0.90 slope, GAAP', 0.0, 'cone_op_slope_c90_w60', 'E1_minus_E2'),
          ('d_size_cash', 'E1 - E2, size gradient, FCF after SBC', 0.0, 'scale_tenfold_cash', 'E1_minus_E2'),
          ('psi_op_E1_2020_25_minus_2010_19', 'Psi_0.90 GAAP slope 2020-25 minus 2010-19 (g 0-40%), E1', 0.0, 'cone_op_slope_c90_w40_2020_25_minus_2010_19', 'E1')]

if not REPORT_ONLY:
    # =========================================================================================== 4. point estimates
    PE = {}
    for bn, (fn, names, vns, paired, pointv) in BLOCKS.items():
        PE[bn] = {}
        for vn in vns + (POINTV if pointv else []):
            v = np.asarray(fn(full(vn), vn), float)
            assert len(v) == len(names), (bn, len(v), len(names))
            PE[bn][vn] = v
    log('point estimates done')
    DRAW_IDX = {bn: np.random.default_rng(SEEDS[bn]).integers(0, NU, (B, NU)) for bn in BLOCKS}

    # =========================================================================================== 5. bootstrap
    DRAWS, ERRS = {}, {}
    if __name__ == '__main__':
        tasks = []
        for bn in sorted(BLOCKS, key=lambda b_: -COST[b_]):
            nch = max(1, min(B, NJOBS * 4))
            cuts = np.linspace(0, B, nch + 1).astype(int)
            tasks += [(bn, int(a), int(b_)) for a, b_ in zip(cuts[:-1], cuts[1:]) if b_ > a]
        for bn, (fn, names, vns, _, _) in BLOCKS.items():
            DRAWS[bn] = np.full((B, len(vns), len(names)), np.nan)
            ERRS[bn] = 0
        done = 0
        if NJOBS > 1:
            with get_context('fork').Pool(NJOBS) as pool:
                for bn, i0, out, nerr in pool.imap_unordered(work, tasks):
                    DRAWS[bn][i0:i0 + len(out)] = out
                    ERRS[bn] += nerr
                    done += 1
                    if done % 8 == 0 or done == len(tasks):
                        log(f'bootstrap chunks {done}/{len(tasks)}')
        else:
            for t in tasks:
                bn, i0, out, nerr = work(t)
                DRAWS[bn][i0:i0 + len(out)] = out
                ERRS[bn] += nerr
        log('bootstrap done', {k_: v for k_, v in ERRS.items() if v})

    # =========================================================================================== 6. summaries
    CELLS = {vn: {f'T_{b}_g{int(round(100 * g0)):02d}_change': [int(((full(vn)['per'] == p) & (full(vn)['g'] >= g0) & fin(full(vn)[BASES[b][0]])).sum())
                                                             for p in (1, 3)] for b in BASES for g0 in G0S} for vn in V}

    def interval_ok(stat, vns):
        if stat in CELLS['E1']:
            small = [vn for vn in vns if min(CELLS[vn][stat]) < MIN_CELL]
            if small:
                return False, 'frontier-point cell below 30 firm-years (' + ', '.join(f'{vn}: {CELLS[vn][stat][0]} in 2016-19, {CELLS[vn][stat][1]} in 2023-25' for vn in small) + ')'
        return True, None

    RES = {}
    for bn, (fn, names, vns, paired, pointv) in BLOCKS.items():
        if bn == 'joint':
            continue
        D = DRAWS[bn]
        for j, st in enumerate(names):
            rec = RES.setdefault(st, {})
            for c, vn in enumerate(vns):
                ok_, why = interval_ok(st, [vn])
                rec[vn] = summarize(PE[bn][vn][j], D[:, c, j], interval=ok_, why=why)
                rec[vn]['block'] = bn
            if paired:
                i1, i2 = vns.index('E1'), vns.index('E2')
                ok_, why = interval_ok(st, ['E1', 'E2'])
                rec['E1_minus_E2'] = summarize(PE[bn]['E1'][j] - PE[bn]['E2'][j], D[:, i1, j] - D[:, i2, j], interval=ok_, why=why)
                rec['E1_minus_E2']['block'] = bn
            if pointv:
                for vn in POINTV:
                    rec[vn] = dict(est=float(PE[bn][vn][j]))
    js = SPEND_NAMES.index('spend_ratio')
    for nm, a in [('weight_lo', ALPHA[1]), ('weight_hi', ALPHA[0])]:
        RES[nm] = {vn: dict(summarize(PE['spend'][vn][js] / a, DRAWS['spend'][:, c, js] / a), block='spend') for c, vn in enumerate(BOOTV)}
        RES[nm]['E1_minus_E2'] = dict(summarize((PE['spend']['E1'][js] - PE['spend']['E2'][js]) / a,
                                                (DRAWS['spend'][:, 0, js] - DRAWS['spend'][:, 1, js]) / a), block='spend')
        for vn in POINTV:
            RES[nm][vn] = dict(est=float(PE['spend'][vn][js] / a))
    log('summaries done')

    # =========================================================================================== 7. families
    JD, je1, je2 = DRAWS['joint'], PE['joint']['E1'], PE['joint']['E2']
    JIX = {k_: i for i, k_ in enumerate(JOINT_NAMES)}

    def own_draws(st, w):
        if st in ('weight_lo', 'weight_hi'):
            a = ALPHA[1] if st == 'weight_lo' else ALPHA[0]
            D, vns, j = DRAWS['spend'], BLOCKS['spend'][2], js
            return (D[:, vns.index('E1'), j] - D[:, vns.index('E2'), j]) / a if w == 'E1_minus_E2' else D[:, vns.index(w), j] / a
        bn = RES[st][w]['block']
        D, vns, j = DRAWS[bn], BLOCKS[bn][2], BLOCKS[bn][1].index(st)
        return D[:, vns.index('E1'), j] - D[:, vns.index('E2'), j] if w == 'E1_minus_E2' else D[:, vns.index(w), j]

    def joint_vals(st, w, e1, e2):
        if st in ('weight_lo', 'weight_hi'):
            x1, x2 = e1[..., JIX['spend_ratio']] / ALPHA[1], e2[..., JIX['spend_ratio']] / ALPHA[1]
        else:
            x1, x2 = e1[..., JIX[st]], e2[..., JIX[st]]
        return x1 if w == 'E1' else x2 if w == 'E2' else x1 - x2

    def family(spec, alpha):
        rows = []
        for key, lab, h0, st, w in spec:
            r = RES[st][w]
            if r.get('estimable'):
                rr = summarize(r['est'], own_draws(st, w), h0=h0)
            else:
                rr = dict(r)
            rows.append(dict(key=key, label=lab, h0=h0, statistic=st, estimand=w, **{k_: rr.get(k_) for k_ in (
                'est', 'se', 'bias', 'estimable', 'note', 'nan_share', 'ci90', 'ci95', 'ci90_basic', 'ci95_basic', 'ci90_normal',
                'ci95_normal', 'ci90_bc', 'p_normal', 'p_percentile', 'p_basic')}))
        for typ in ('normal', 'percentile', 'basic'):
            for c_, a_ in zip(rows, holm([c_[f'p_{typ}'] if c_.get('estimable') else 1.0 for c_ in rows])):
                c_[f'holm_{typ}'] = float(a_)
        e = np.array([joint_vals(st, w, je1, je2) for _, _, _, st, w in spec], float)
        assert np.allclose(e, [c_['est'] if c_['est'] is not None else np.nan for c_ in rows], equal_nan=True), 'joint draw differs'
        bsj = np.stack([joint_vals(st, w, JD[:, 0, :], JD[:, 1, :]) for _, _, _, st, w in spec], axis=1)
        rw, nrw = romano_wolf(e, np.array([s_[2] for s_ in spec], float), bsj)
        for c_, a_ in zip(rows, rw):
            c_['romano_wolf'] = float(a_)
        surv = lambda lv: {**{f'holm_{t_}': [c_['key'] for c_ in rows if c_[f'holm_{t_}'] < lv] for t_ in ('normal', 'percentile', 'basic')},
                           'romano_wolf': [c_['key'] for c_ in rows if c_['romano_wolf'] < lv]}
        nx = {f'{lv}_{t_}': int(sum(1 for c_ in rows if c_.get('estimable') and not (
            c_['ci' + lv + ('' if t_ == 'percentile' else '_' + t_)][0] <= c_['h0'] <= c_['ci' + lv + ('' if t_ == 'percentile' else '_' + t_)][1])))
              for lv in ('90', '95') for t_ in ('percentile', 'basic', 'normal')}
        return dict(contrasts=rows, n=len(rows), n_estimable=sum(bool(c_.get('estimable')) for c_ in rows), alpha=alpha,
                    survivors=surv(alpha), survivors_5pct=surv(0.05), survivors_10pct=surv(0.10), intervals_excluding_h0=nx,
                    rw_draws_complete=nrw, unadjusted_p_below_alpha={t_: int(sum(1 for c_ in rows if c_.get('estimable') and c_[f'p_{t_}'] is not None and c_[f'p_{t_}'] < alpha)) for t_ in ('normal', 'percentile', 'basic')})

    FAMILIES = dict(
        table38=family([(k_, k_, 0.0, k_, 'E1_minus_E2') for k_ in FULL38], 0.10),
        referee32=family([(k_, k_, 0.0, k_, 'E1_minus_E2') for k_ in REF32], 0.10),
        headline14A=family(FAM14A, 0.05), headline14B=family(FAM14B, 0.05))
    FAMILIES['method'] = ('Holm step-down (primary) on two-sided p-values from each statistic\'s own draws, three types (normal: '
                          'bootstrap standard error; percentile; basic); Romano-Wolf studentized step-down on the joint draw (block joint) '
                          'as a check. A contrast without an interval enters with p = 1.')
    log('families done', {k_: v_['survivors'] for k_, v_ in FAMILIES.items() if isinstance(v_, dict)})

    # =========================================================================================== 8. other estimates
    SOLVER = {}
    for vn in ['E1', 'E2', 'E2x25']:
        z = full(vn)
        for b in BASES:
            m, R, _ = BASES[b]
            for sp, per in SPL.items():
                k = qmask(z, m, per=per)
                SOLVER[f'{vn}|slope_{b}_{sp}'] = (z[m][k], np.c_[np.ones(k.sum()), z['g'][k]], .9)
            yk = fin(z[R]) & fin(z['lsize']) & (z['sb'] >= 0)
            SOLVER[f'{vn}|scale_{b}'] = (z[R][yk], np.c_[np.ones(yk.sum()), z['lsize'][yk]], .95)
    SOLVER_OUT = {}
    for key, (y, X, tau) in SOLVER.items():
        bd = qr_fit(y, X, tau)
        bp, fp = qr_primal(y, X, tau)
        bi = smf.quantreg('y ~ x', pd.DataFrame({'y': y, 'x': X[:, 1]})).fit(q=tau, max_iter=5000).params.values
        rg = qr_range(y, X, tau) if ('_pooled' in key or 'scale' in key) else None
        SOLVER_OUT[key] = dict(n=int(len(y)), dual=float(bd[1]), primal=float(bp[1]), irls=float(bi[1]), loss_dual=check_loss(y, X, bd, tau),
                               loss_irls=check_loss(y, X, bi, tau), minimizer_range=rg)
        assert abs(bd[1] - bp[1]) < 1e-6 or (rg and rg[0] - 1e-6 <= bd[1] <= rg[1] + 1e-6), ('dual and primal LP disagree', key)
        assert check_loss(y, X, bd, tau) <= check_loss(y, X, bi, tau) + 1e-9
    log('solver check done')

    Pl = P[['cik', 'year', 'g']].sort_values(['cik', 'year'])
    Pl['g_lead'] = Pl.groupby('cik').g.shift(-1).where(Pl.groupby('cik').year.shift(-1) == Pl.year + 1)
    WITHIN = {}
    for vn in MFV:
        v = V[vn].merge(Pl[['cik', 'year', 'g_lead']], on=['cik', 'year'], how='left')
        own = V[vn][['cik', 'year', 'g']].assign(year=lambda d: d.year - 1).rename(columns={'g': 'g_lead_own'})
        v = v.merge(own, on=['cik', 'year'], how='left')
        for b in BASES:
            m = BASES[b][0]
            out = {}
            d = v[['cik', 'year', 'g', m]].dropna()
            d = d[d.g <= 1.5]
            f = smf.ols(f'{m} ~ g + C(year) + C(cik)', d).fit(cov_type='cluster', cov_kwds={'groups': d['cik']})
            out['contemporaneous'] = dict(b=float(f.params['g']), se=float(f.bse['g']), n=int(len(d)))
            for lead, nm in [('g_lead', 'reported'), ('g_lead_own', 'same_estimand')]:
                if vn == 'E1' and nm == 'same_estimand':
                    continue
                d = v[['cik', 'year', 'g', lead, m]].dropna().rename(columns={lead: 'gl'})
                d = d[(d.g <= 1.5) & (d.gl <= 1.5) & (d.gl > -0.9)]
                a = smf.ols(f'{m} ~ gl + C(year) + C(cik)', d).fit(cov_type='cluster', cov_kwds={'groups': d['cik']})
                j = smf.ols(f'{m} ~ g + gl + C(year) + C(cik)', d).fit(cov_type='cluster', cov_kwds={'groups': d['cik']})
                out[f'lead_{nm}'] = dict(b=float(a.params['gl']), se=float(a.bse['gl']), n=int(len(d)),
                                         joint_g=float(j.params['g']), joint_g_se=float(j.bse['g']),
                                         joint_lead=float(j.params['gl']), joint_lead_se=float(j.bse['gl']))
            WITHIN[f'{vn}|{b}'] = out
    log('within-firm done')

    T_LEVELS = {vn: {f'T_{b}_g{int(round(100 * g0)):02d}': {PK[p]: dict(est=Tval(full(vn), BASES[b][0], g0, p),
                                                                         n=int(((full(vn)['per'] == p) & (full(vn)['g'] >= g0) & fin(full(vn)[BASES[b][0]])).sum()))
                                                             for p in range(4)} for b in BASES for g0 in G0S} for vn in MFV}
    CONE_CELLS = {vn: {b: dict(zip([f'{g0:.2f}' for g0 in GRIDF], cone_mat(full(vn)['g'][fin(full(vn)['g']) & fin(full(vn)[BASES[b][0]])],
                                                                         full(vn)[BASES[b][0]][fin(full(vn)['g']) & fin(full(vn)[BASES[b][0]])])[1].tolist()))
                       for b in BASES} for vn in MFV}
    CONE_CURVES = {}
    for vn in MFV:
        z = full(vn)
        for b in BASES:
            k = fin(z['g']) & fin(z[BASES[b][0]])
            R, cnt = cone_mat(z['g'][k], z[BASES[b][0]][k])
            CONE_CURVES[f'{vn}|{b}'] = dict(grid=GRIDF.tolist(), n=cnt.tolist(), **{f'phi{int(round(100 * c))}': R[i].tolist() for i, c in enumerate(TAUS)},
                                            orderm25=R[-1].tolist())
    ROLL = {vn: {b: {f'{y0}_{y0 + 2}': qslope(full(vn), BASES[b][0], years=(y0, y0 + 2)) for y0 in range(2010, 2024)} for b in BASES} for vn in PAIRV}
    LBANDS = [0, 0.1, 0.2, 0.3, 0.4, 0.6, 5]
    LOCAL = {}
    for vn in PAIRV:
        z = full(vn)
        for b in BASES:
            m = BASES[b][0]
            for tq in (.90, .95):
                LOCAL[f'{vn}|{b}|q{int(100 * tq)}'] = [dict(band=f'{LBANDS[i]:g}-{LBANDS[i + 1]:g}', n=int(((z['g'] >= LBANDS[i]) & (z['g'] < LBANDS[i + 1]) & fin(z[m])).sum()),
                                                           q=q(z[m][(z['g'] >= LBANDS[i]) & (z['g'] < LBANDS[i + 1])], tq)) for i in range(6)]

    ANCH = {'E2': anchor_block(V['E2'], False), 'E1': anchor_block(V['E1'], True), 'E1all': anchor_block(V['E1'], False)}
    for vn in [x for x in ['E2x25', 'E2imp4', 'E2imp8', 'E2clean', 'E2k2010', 'E2nodebt', 'E2testrule'] if x in V]:
        ANCH[vn] = anchor_block(V[vn], False)
    for vn in [x for x in ['E1r2both', 'E1r2either'] if x in V]:           # R2 reader sensitivities, E1 calibration rule
        ANCH[vn] = anchor_block(V[vn], True)
    assert ANCH['E2']['n'] == PE['anchor']['E2'][ANCH_NAMES.index('anchor_p95_n')]
    assert np.isclose(ANCH['E2']['Pi_ub'][1], PE['anchor']['E2'][ANCH_NAMES.index('anchor_p95_Pi_ub_med')])
    ANCH_CUT = {f'{vn}|{cq}': {k_: v_ for k_, v_ in anchor_block(V[vn], vn == 'E1', cq).items() if k_ != 'firm_years'}
                for vn in MFV + ['E1all'] for cq in (0.90, 0.925, 0.95, 0.975)}
    LOFO = {}
    for vn in MFV:
        d25 = V[vn][V[vn].period == '2023-25']
        LOFO[vn] = {}
        for nm in ANCH['E2' if vn == 'E2' else vn]['firms'] if vn in ANCH else []:
            c_ = d25.cik[d25.name == nm].iloc[0]
            LOFO[vn][nm] = anchor_block(V[vn][V[vn].cik != c_], vn == 'E1')['Pi_ub'][1]

    SFA_DETAIL = {}
    if 'sfa' in BLOCKS:
        for vn in PAIRV:
            v = V[vn]
            coh = np.where(v.cik.map(FIRST_YEAR).fillna(v.groupby('cik').year.transform('min')) >= 2019, '2019+', 'pre-2019')
            for b in BASES:
                m = BASES[b][0]
                sep = {}
                for p in ['2016-19', '2023-25']:
                    for c_ in ['pre-2019', '2019+']:
                        d = v[(v.period == p) & (coh == c_)][['g', m]].dropna()
                        d = d[(d.g <= 1.5) & (d[m] > -1.5)]
                        if len(d) >= 60:
                            sep[f'{p}|{c_}'] = dict(shortfall=float(sfa_fit(d[m].values, np.c_[np.ones(len(d)), d.g, d.g ** 2])[0]), n=int(len(d)))
                SFA_DETAIL[f'{vn}|{b}|separate_frontiers'] = sep
            x = v[coh == 'pre-2019']
            s16, s23 = set(x[x.period == '2016-19'].cik), set(x[x.period == '2023-25'].cik)
            SFA_DETAIL[f'{vn}|survivorship'] = dict(pre2019_firms_in_2016_19=len(s16), still_in_2023_25=len(s16 & s23),
                                                   **{f'{b}_2016_19_median_margin_survivors': float(x[(x.period == '2016-19') & x.cik.isin(s16 & s23)][BASES[b][0]].median()) for b in BASES},
                                                   **{f'{b}_2016_19_median_margin_leavers': float(x[(x.period == '2016-19') & ~x.cik.isin(s23)][BASES[b][0]].median()) for b in BASES})

    SAMPLES = {vn: dict(n=int(len(df)), firms=int(df.cik.nunique()), by_period={p: int((df.period == p).sum()) for p in PERIODS},
                        n_g_above_50=int((df.g > 0.5).sum()), n_affected_kept=int(df.aff.sum()),
                        n_g_ge_40={pk: int(((df.g >= 0.4) & (df.period == p)).sum()) for p, pk in zip(PERIODS, PK)}) for vn, df in V.items()}
    fl = core.flag25.astype(bool)
    kept = int(V['E2'].aff.sum())
    ROUTES = dict(n_core=int(len(core)), n_flagged=int(fl.sum()), n_acq_year=int(core.now25.astype(bool).sum()),
                  n_following_only=int((fl & ~core.now25.astype(bool)).sum()), n_kept_pro_forma=kept,
                  n_kept_acq_year=int((V['E2'].aff & V['E2'].now25.astype(bool)).sum()), n_dropped=int(fl.sum()) - kept,
                  share_dropped=float((fl.sum() - kept) / fl.sum()),
                  reasons={k_: int(v_) for k_, v_ in core.loc[fl, 'reason25'].value_counts().items() if k_ != 'organic growth computed'},
                  n_computed=int((fl & core.gorg25.notna()).sum()), n_unverified=int(core.unver.sum()), n_unaffected_kept=int(len(V['E2']) - kept),
                  n_E2=int(len(V['E2'])), n_E2x25=int(len(V['E2x25'])))

    # =========================================================================================== 9. v2 validation
    CHECKS = {}
    if PANEL == 'v2':
        OLD = json.load(open(f'{BASE}/notes/empirics_organic.json'))['estimates']
        QRS = {'slope_op_pooled', 'slope_cash_pooled', 'slope_op_2010_19', 'slope_cash_2010_19', 'slope_op_2020_25', 'slope_cash_2020_25',
               'scale_tenfold_op', 'scale_tenfold_cash'}
        vcheck = ['E1', 'E2', 'E2x10', 'E2x25', 'E2x50', 'E2pf10', 'E2pf50', 'E2add', 'E2max']
        for st in REF32 + ['p95_op_2016_19', 'p95_op_2023_25', 'p95_cash_2016_19', 'p95_cash_2023_25', 'capint_gap_cash_2010_15',
                           'capint_gap_cash_2016_19', 'capint_gap_cash_2020_22'] + [f'T_{b}_g{g}_change' for b in BASES for g in ('10', '30')]:
            for vn in vcheck:
                new, old = RES[st][vn]['est'], OLD[st][vn]['est']
                old = np.nan if old is None else old
                CHECKS[f'{st}|{vn}'] = dict(this=new, published=old, diff=new - old if fin(new) and fin(old) else None)
        irls_bad = {}
        for vn in vcheck:
            z = full(vn)
            for b in BASES:
                m, R, _ = BASES[b]
                for sp, per in SPL.items():
                    k = qmask(z, m, per=per)
                    bi = smf.quantreg('y ~ x', pd.DataFrame({'y': z[m][k], 'x': z['g'][k]})).fit(q=.9, max_iter=5000).params['x']
                    if not np.isclose(bi, OLD[f'slope_{b}_{sp}'][vn]['est'], rtol=1e-6, atol=1e-8):
                        irls_bad[f'slope_{b}_{sp}|{vn}'] = (bi, OLD[f'slope_{b}_{sp}'][vn]['est'])
                yk = fin(z[R]) & fin(z['lsize']) & (z['sb'] >= 0)
                bi = smf.quantreg('y ~ x', pd.DataFrame({'y': z[R][yk], 'x': z['lsize'][yk]})).fit(q=.95, max_iter=5000).params['x'] * LN10
                if not np.isclose(bi, OLD[f'scale_tenfold_{b}'][vn]['est'], rtol=1e-6, atol=1e-8):
                    irls_bad[f'scale_tenfold_{b}|{vn}'] = (bi, OLD[f'scale_tenfold_{b}'][vn]['est'])
        assert not irls_bad, irls_bad
        nonqr = {k_: v_ for k_, v_ in CHECKS.items() if k_.split('|')[0] not in QRS and k_.split('|')[0] != 'capint_gap_op_2023_25'}
        bad = {k_: v_ for k_, v_ in nonqr.items() if not (v_['diff'] is None and not fin(v_['this']) and not fin(v_['published']))
               and not (v_['diff'] is not None and abs(v_['diff']) < 1e-9)}
        assert not bad, f'v2 statistics not reproduced: {bad}'
        log(f'v2 validation passed: {len(nonqr)} non-QR statistics reproduced exactly; IRLS on these frames reproduces every published slope and gradient')

    OUT = dict(
        meta=dict(script='code/estimate_v3.py', panel=PANEL, replications=B, fast_mode=FAST, seeds=SEEDS, seed_rule='SEED0 + crc32(block name) mod 1e6',
                  seed0=SEED0, nan_max=NAN_MAX, min_cell=MIN_CELL, workers=NJOBS, errors_in_draws=ERRS,
                  solver='exact LP (scipy HiGHS, dual formulation)', firms_in_bootstrap_universe=NU,
                  bootstrap='firm-cluster; firms drawn from E1; each estimand on its own rows of the drawn firms; one generator per block',
                  intervals='ci90/ci95 percentile; *_basic; *_normal (bootstrap se); ci90_bc bias-corrected percentile; p-values two-sided',
                  primary_slope='Psi_chi (dominance cone), chi = 0.90, window 0-60%: statistic cone_{op,cash}_slope_c90_w60 (D-2)',
                  baseline_estimand='E1 (D-3); model-facing statistics under E1, E2, E2imp4, E2imp8',
                  variants=VLAB, bootstrapped=BOOTV, model_facing_estimands=MFV, point_only=POINTV,
                  blocks={bn: dict(variants=v_[2], statistics=v_[1]) for bn, v_ in BLOCKS.items()},
                  capint='split at the period median of the sort variable inside each draw; missing intensity not classified',
                  bridge=('B5: R_cash_pre = g + (FCF - SBC + interest paid + income taxes paid) / revenue; R_cash_bi = g + (FCF - SBC + '
                          'interest paid x (1 - t)) / revenue, t = 35% (fiscal years ending before 2018) or 21%; cash_bs = the cash '
                          'score on the firm-years where the bridge is defined; interest and taxes from SEC frames (latest filed, not '
                          'first reported); InterestPaidNet and IncomeTaxesPaidNet preferred; a missing element is zero when any is reported'),
                  sec_inputs='data/v3_inputs/ (retrieved 29 Oct 2026 with the author\'s approval; provenance in data/v3_inputs/README_retrieval.md)',
                  units='fractions (0.01 = one point) except slopes, the spend ratio, weights and regression coefficients; size gradients per tenfold revenue'),
        samples=SAMPLES, routes=ROUTES, imputation=IMPUTE, estimates=RES, families=FAMILIES, solver_check=SOLVER_OUT,
        within=WITHIN, T_levels=T_LEVELS, T_cells=CELLS, cone_cells=CONE_CELLS, cone_curves=CONE_CURVES, rolling_slopes=ROLL,
        local_band_quantiles=LOCAL,
        anchor=dict(blocks={k_: {kk: vv for kk, vv in v_.items() if kk != 'firm_years'} for k_, v_ in ANCH.items()},
                    cutoff_sensitivity=ANCH_CUT, leave_one_firm_out_median_Pi_ub=LOFO),
        sfa_detail=SFA_DETAIL, checks=CHECKS)
    json.dump(clean(OUT), open(OUT_JSON, 'w'), indent=1)
    log('wrote', OUT_JSON)
    if PANEL == 'v2':
        sys.exit(0)
    np.savez_compressed(f'{BASE}/notes/bootstrap_draws_v3.npz', **{bn: DRAWS[bn] for bn in DRAWS},
                        **{f'{bn}__variants': np.array(BLOCKS[bn][2]) for bn in DRAWS}, **{f'{bn}__statistics': np.array(BLOCKS[bn][1]) for bn in DRAWS},
                        **{f'{bn}__firm_draws': DRAW_IDX[bn].astype(np.int16) for bn in DRAWS}, firm_universe=U)
    json.dump(clean(dict(
        meta=dict(script='code/estimate_v3.py', panel='v3', rules='as notes/calibration_anchor_E2.json (calibrate_horizons.py anchor rules); '
                  'E2 is the model-facing block read by calibrate_horizons.py; E1 drops acquisition-affected firm-years from the tail as the current calibration does',
                  sample='data/panel_v3.csv', units='fractions of revenue; rev and sm in dollars', estimands=MFV),
        **{b_: ANCH[b_] for b_ in ANCH},
        bootstrap={vn: {s: RES[f'anchor_p95_{s}'][vn] for s in ANCH_STATS} for vn in BLOCKS['anchor'][2]},
        bootstrap_p975={vn: {s: RES[f'anchor_p975_{s}'][vn] for s in ANCH_STATS} for vn in BLOCKS['anchor'][2]},
        E1_minus_E2={s: RES[f'anchor_p95_{s}']['E1_minus_E2'] for s in ANCH_STATS},
        cutoff_sensitivity=ANCH_CUT, leave_one_firm_out_median_Pi_ub=LOFO)), open(f'{BASE}/notes/calibration_anchor_v3.json', 'w'), indent=1)
    FS = dict(meta=dict(script='code/estimate_v3.py', panel='v3', statistic='Psi_chi slope: least-squares slope of phi_chi(g0) on g0 over the grid '
                        'g0 = 0, 0.05, ..., window end; phi_chi(g0) = chi-quantile of the margin among firm-years with g >= g0 (dominance cone, '
                        'Definition 2); grid points need at least 30 firm-years in the sample and 10 in a bootstrap draw; '
                        'period slopes also on the 0-40% window, because within-period cells at 60% growth are below 30', central=dict(estimand='E1', chi=0.90, window=0.6),
                        decision='D-2 and D-3 (author, 29 Oct 2026)', units='margin per unit of growth (negative: trade-off)',
                        intervals='firm-cluster bootstrap, 999 replications, percentile; basic and normal in notes/empirics_v3.json'),
              central={b: {vn: RES[f'cone_{b}_slope_c90_w60'][vn] for vn in MFV} for b in BASES},
              grid={b: {f'chi{int(round(100 * c))}_w{int(round(100 * w))}': {vn: {k_: RES[f'cone_{b}_slope_c{int(round(100 * c))}_w{int(round(100 * w))}'][vn].get(k_)
                                                                               for k_ in ('est', 'se', 'ci90', 'ci95', 'estimable', 'nan_share')} for vn in MFV}
                        for c in TAUS for w in WINS} for b in BASES},
              periods={b: {f'w{int(round(100 * w))}_{sp}': {vn: RES[f'cone_{b}_slope_c90_w{int(round(100 * w))}_{sp}'][vn] for vn in MFV}
                           for w in PERW for sp in ('2010_19', '2020_25', '2020_25_minus_2010_19', '2010_15', '2018_25', '2018_25_minus_2010_15')} for b in BASES},
              order_m25={b: {f'w{int(round(100 * w))}': {vn: RES[f'cone_{b}_slope_orderm25_w{int(round(100 * w))}'][vn] for vn in MFV} for w in WINS} for b in BASES},
              local_conditional_quantile_descriptive={b: {vn: RES[f'slope_{b}_pooled'][vn] for vn in MFV} for b in BASES},
              curves=CONE_CURVES)
    json.dump(clean(FS), open(f'{BASE}/notes/frontier_slope_v3.json', 'w'), indent=1)
    log('wrote notes/bootstrap_draws_v3.npz, notes/calibration_anchor_v3.json, notes/frontier_slope_v3.json')
else:
    OUT = json.load(open(OUT_JSON))
    log('report only: read', OUT_JSON)

exec(compile(open(f'{BASE}/code/estimate_v3_report.py').read(), f'{BASE}/code/estimate_v3_report.py', 'exec'))
