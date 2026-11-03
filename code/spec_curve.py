#!/usr/bin/env python3
"""Specification curve (multiverse) of the empirical headline claims of Paper 1, with two reviewer variants.

Pre-specification: notes/spec_curve/design.md (written 2026-11-03 14:36 UTC, before any estimate of this analysis).
Method: Simonsohn, Simmons and Nelson (2020, Nature Human Behaviour); Steegen et al. (2016). The paper moves its analysis
choices one at a time (Table tab:robust, Table tab:grid_v3, the four views); this script moves them together over the
options the paper uses, reports or names as defensible, and reports for each headline claim the share of specifications
in which it holds, the median and range of its quantity and the choice that moves it most. It varies analysis choices on
fixed data and tests no causal reading.

Reuse, not re-implementation. The script executes code/estimate_v3.py up to its point-estimate section (which executes
code/estimate_organic.py up to its END OF FRAME CONSTRUCTION marker), so the frames, `variant`, `arrays`, `Sub`,
`cone_mat`, `wslope`, `q`, `spend_ratio` and `anchor_vec` are the paper's own. Two short pieces are repeated from
estimate_v3.py on the full core (core_ext) instead of the primary core, so that the sample rules can be crossed with every
treatment of acquired growth: the imputed organic growth (estimate_v3.py, the lines that build E2imp4/E2imp8) and the
bridge margins (the B5 loop). Both are checked row by row against the paper's frames. Before any result is used, the
specifications that coincide with the 22 published variants must reproduce notes/empirics_v3.json to 1e-12 for every
statistic it stores, and the printed macros of paper1/macros.tex after rounding; the script stops otherwise.

Grid (design.md, sections 2-3). Sample: treatment of acquired growth (15 levels) x R1 (2) x R2 (3) x R5 (2) x debt-only
filers (2) x growth bound (2) = 720 samples. Claim-specific: C1/C2 P95 change: quantile (0.95, 0.90) x late period
(2023-25, 2023-24, 2025) [x cash measure (3) for C2]; C3/C4 Psi slope: estimator (Psi_0.80-0.95, order-m) x window
(0-60, 0-40%) [x cash measure]; C5/C6 steepening: estimator x window x period split [x cash measure]; C7 spend ratio
(secondary: benchmark growth); C8 anchor surplus: cut-off (0.95, 0.90, 0.925, 0.975) x tail rule (observed samples).

Variants. Forward pairing (reviewer GLM-M9): F1 R_t = g_{t+1} + m_t indexed by the margin year t (model timing), F1'
the same pairs indexed by t+1, F2 R_t = g_t + m_{t+1} (literal wording of the request); baseline and four views for all,
and the full C1-C6 grid for F1 (reported separately). Leave one firm out (reviewer GPT-16): each firm dropped in turn
under E1, E2 and the imputation bounds.

Bootstrap (secondary): firm-cluster, B = 199 (SC_B), firms drawn from the 292 firms of E1, the same draws for every
specification, seed 20261030 + crc32('spec_curve') mod 1e6; on the 22 published samples plus a seeded random sample of
the others, sized so that the bootstrap stays within SC_BUDGET_MIN minutes (default 15) on SC_JOBS workers (default 2),
at least 48 samples.

Inputs : data/panel_v3*.csv and the other inputs of code/estimate_v3.py (through its own code); notes/empirics_v3.json
         (reproduction target); paper1/macros.tex (printed values, read only)
Outputs: notes/spec_curve/results.json, notes/spec_curve/specs.csv.gz (every specification of the main grid),
         notes/spec_curve/specs_forward.csv.gz (the F1 grid), notes/spec_curve/run_log.txt (this run's log),
         paper1/spec_macros.tex (\\Sc... macros), sections/tables/tab_spec_curve.tex, figures/fig_spec_curve.pdf
Run    : python3 code/spec_curve.py      (about 15 minutes on 2 shared cores, nearly all of it the bootstrap; SC_B=0 skips
         the bootstrap, SC_JOBS sets the worker processes, SC_BUDGET_MIN the bootstrap budget; SC_FROM_CACHE=1 rewrites
         the outputs from the results of the last full run, kept outside the repository at SC_CACHE, default
         <system temp folder>/spec_curve_cache.pkl)
Deterministic: every random draw comes from a generator seeded by the rule above; the subset of bootstrapped samples is
drawn from its own seeded generator (crc32('spec_curve_subset')). Only the subset's size K depends on the machine (the
timing rule of design.md, section 5); SC_BOOT_K=169 fixes it at the value of the reported run, so that
    SC_BOOT_K=169 python3 code/spec_curve.py
reproduces every reported number.
"""
import gzip
import io
import json
import math
import os
import re
import subprocess
import sys
import time
import zlib
from collections import OrderedDict
from datetime import datetime, timezone
from multiprocessing import get_context

import numpy as np
import pandas as pd

T_START = time.time()
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTD = os.path.join(BASE, 'notes', 'spec_curve')
os.makedirs(OUTD, exist_ok=True)
B_BOOT = int(os.environ.get('SC_B', '199'))
NJOBS = max(1, int(os.environ.get('SC_JOBS', '2')))
BUDGET_MIN = float(os.environ.get('SC_BUDGET_MIN', '15'))
K_MIN = 48
LOGF = open(os.path.join(OUTD, 'run_log.txt'), 'a' if os.environ.get('SC_FROM_CACHE') == '1' else 'w')


def log(*a):
    s = f'[{time.time() - T_START:7.1f}s] ' + ' '.join(str(x) for x in a)
    print(s, flush=True)
    LOGF.write(s + '\n')
    LOGF.flush()


# =============================================================================================== 1. the paper's code
os.environ['V3_PANEL'] = 'v3'
os.environ.pop('V3_REPORT_ONLY', None)
_SRC = os.path.join(BASE, 'code', 'estimate_v3.py')
_src = open(_SRC).read()
_cut = _src.index('\nif not REPORT_ONLY:\n')                       # section 4 (point estimates) and later are not run
EV = {'__file__': _SRC, '__name__': 'estimate_v3_frames'}
exec(compile(_src[:_cut], _SRC, 'exec'), EV)
V, core, core_ext, P, variant = EV['V'], EV['core'], EV['core_ext'], EV['P'], EV['variant']
arrays, Sub, cone_mat, wslope, q, med = EV['arrays'], EV['Sub'], EV['cone_mat'], EV['wslope'], EV['q'], EV['med']
spend_ratio, anchor_vec, ANCH_STATS = EV['spend_ratio'], EV['anchor_vec'], EV['ANCH_STATS']
STAT_RATE, MIN_CELL, NU, U, TAUS, GRIDF = EV['STAT_RATE'], EV['MIN_CELL'], EV['NU'], EV['U'], EV['TAUS'], EV['GRIDF']
seed_for, PERIODS = EV['seed_for'], EV['PERIODS']
fin = np.isfinite
assert TAUS == [0.80, 0.85, 0.90, 0.95] and MIN_CELL == 30 and NU == 292
log('executed code/estimate_v3.py up to its point-estimate section;', len(V), 'paper frames')

J3 = json.load(open(os.path.join(BASE, 'notes', 'empirics_v3.json')))
E3 = J3['estimates']
MACRO_TEX = open(os.path.join(BASE, 'paper1', 'macros.tex')).read()
PRINTED = dict(re.findall(r'\\newcommand\{\\([A-Za-z]+)\}\{([^\n]*)\}\s*$', MACRO_TEX, flags=re.M))

# =============================================================================================== 2. the full core
# core_ext is the core before the primary-sample filter (estimate_organic.py); the paper builds its sensitivity samples
# from it. The two pieces below repeat estimate_v3.py on core_ext (instead of core) and are checked against the paper.
cex = core_ext.merge(P[['cik', 'year', 'fy_end', 'price', 'prev_price']], on=['cik', 'year', 'fy_end'], how='left',
                     validate='one_to_one')
_fl, _now, _prev = cex.flag25.astype(bool), cex.now25.astype(bool), cex.prevnow25.astype(bool)
for M_ in (4, 8):                                                   # estimate_v3.py, imputation bounds, on core_ext
    _acq = (np.where(_now, 0.5 * cex.price / M_ / cex.rev_lag, 0.0) + np.where(_prev, 0.5 * cex.prev_price / M_ / cex.rev_lag, 0.0))
    cex[f'g_imp{M_}'] = np.where(_fl, np.where(cex.gorg25.notna(), cex.gorg25, cex.g - _acq), cex.g)
# estimate_v3.py, B5 bridge margins (row-level; the scores are formed after the variant sets its growth)
cex['m_cash_pre'] = cex.m_fcf_sbc + (cex.interest_paid + cex.income_taxes_paid) / cex.rev
cex['m_cash_bi'] = cex.m_fcf_sbc + cex.interest_paid * (1 - STAT_RATE(cex.fy_end)) / cex.rev
cex['m_cash_bs'] = cex.m_fcf_sbc.where(cex.m_cash_pre.notna())
assert isinstance(cex.size_bin.dtype, pd.CategoricalDtype)

PRIM = (cex.v3_exclude.fillna('') == '').values
K2010 = (cex.backfill_type == 'fy2010_before_first_xbrl_report').values
R2_CLS = cex.business_class_named.fillna('').isin(['interactive_entertainment', 'gambling', 'compute_infrastructure']).values
R2_ALL = (cex.panel_named.fillna('') != '').values
R5_FLAG = cex.no_listed_equity.astype(object).eq(True).values
DEBT = cex.debt_only_named.astype(bool).values
UNVER = cex.unver.astype(bool).values
BRIDGE_M = ['m_cash_pre', 'm_cash_bi', 'm_cash_bs']

# =============================================================================================== 3. the grid
ACQ = OrderedDict()                                                 # level -> (family, flag, reading, M)
ACQ['obs'] = ('observed', None, None, None)
for t_ in ('25', '10', '50'):
    for rd in ('rule', 'add', 'max'):
        ACQ[f'pf{t_}_{rd}'] = ('pro forma', t_, rd, None)
for t_ in ('25', '10', '50'):
    ACQ[f'ex{t_}'] = ('exclusion', t_, None, None)
for M_ in ('4', '8'):
    ACQ[f'imp{M_}'] = ('imputed', '25', None, M_)
SDIMS = OrderedDict(acq=list(ACQ), r1=['no', 'yes'], r2=['none', 'cls', 'all'], r5=['keep', 'drop'], debt=['keep', 'drop'],
                    trim=['g<5', 'g<=1.5'])
SAMPLES = [dict(zip(SDIMS, v)) for v in __import__('itertools').product(*SDIMS.values())]
for i, s in enumerate(SAMPLES):
    s['sid'] = i
assert len(SAMPLES) == 720
BASE_SAMPLE = dict(acq='obs', r1='no', r2='none', r5='keep', debt='keep', trim='g<5')


def acq_args(level):
    fam, t_, rd, M_ = ACQ[level]
    if fam == 'observed':
        return np.ones(len(cex), bool), None, '25'
    if fam == 'pro forma':
        col = {'rule': 'gorg', 'add': 'gadd', 'max': 'gmax'}[rd] + t_
        return ~UNVER & cex[col].notna().values, col, t_
    if fam == 'exclusion':
        return ~UNVER & ~cex['flag' + t_].astype(bool).values, None, t_
    return ~UNVER, f'g_imp{M_}', '25'


def build(s):
    """The sample frame of sample dict s (rows of the full core through the paper's `variant`)."""
    rows = PRIM | (K2010 if s['r1'] == 'yes' else False)
    if s['r2'] == 'cls':
        rows = rows & ~R2_CLS
    elif s['r2'] == 'all':
        rows = rows & ~R2_ALL
    if s['r5'] == 'drop':
        rows = rows & ~R5_FLAG
    if s['debt'] == 'drop':
        rows = rows & ~DEBT
    am, gcol, tflag = acq_args(s['acq'])
    v = variant(rows & am, gcol, tflag, frame=cex)
    for m_, R_ in [('m_cash_pre', 'R_cash_pre'), ('m_cash_bi', 'R_cash_bi'), ('m_cash_bs', 'R_cash_bs')]:
        v[R_] = v.g + v[m_]
    if s['trim'] == 'g<=1.5':
        v = v[v.g <= 1.5].reset_index(drop=True)
    return v


# the published variants inside the grid (Table tab:robust without the superseded first-test-run rule)
PUB = {'E1': {}, 'E2': dict(acq='pf25_rule'), 'E2pf10': dict(acq='pf10_rule'), 'E2pf50': dict(acq='pf50_rule'),
       'E2x10': dict(acq='ex10'), 'E2x25': dict(acq='ex25'), 'E2x50': dict(acq='ex50'), 'E2add': dict(acq='pf25_add'),
       'E2max': dict(acq='pf25_max'), 'E2imp4': dict(acq='imp4'), 'E2imp8': dict(acq='imp8'),
       'E1k2010': dict(r1='yes'), 'E2k2010': dict(acq='pf25_rule', r1='yes'), 'E1clean': dict(r2='all'),
       'E2clean': dict(acq='pf25_rule', r2='all'), 'E1r2named': dict(r2='cls'), 'E2r2named': dict(acq='pf25_rule', r2='cls'),
       'E1nolist': dict(r5='drop'), 'E2nolist': dict(acq='pf25_rule', r5='drop'), 'E1nodebt': dict(debt='drop'),
       'E2nodebt': dict(acq='pf25_rule', debt='drop')}


def sid_of(**kw):
    d = dict(BASE_SAMPLE, **kw)
    return next(s['sid'] for s in SAMPLES if all(s[k] == d[k] for k in SDIMS))


PUB_SID = {vn: sid_of(**kw) for vn, kw in PUB.items()}
FOUR = ['E1', 'E2', 'E2imp4', 'E2imp8']

# ---- statistics of one sample (point estimate: mn = 30, the sample rule; bootstrap draw: mn = 10, the draw rule)
MEAS = OrderedDict(op=('m_op', 'R_op'), cash=('m_fcf_sbc', 'R_cash'), cash_pre=('m_cash_pre', 'R_cash_pre'),
                   cash_bi=('m_cash_bi', 'R_cash_bi'))
QS = OrderedDict(p95=0.95, p90=0.90)
LATES = ['2023_25', '2023_24', '2025']
EST = ['c90', 'c80', 'c85', 'c95', 'om25']
EST_ROW = dict(c80=0, c85=1, c90=2, c95=3, om25=4)                # rows of cone_mat: TAUS, then the order-m frontier
WIN = OrderedDict(w60=0.6, w40=0.4)
SPLITS = ['A', 'B']                                                 # A: 2010-19 vs 2020-25; B: 2010-15 vs 2018-25
CUTS = [0.95, 0.90, 0.925, 0.975]
BENCH = OrderedDict(median=None, G05=0.05, G08=0.08, G12=0.12)
IX_LB, IX_NET, IX_UB = (ANCH_STATS.index(k) for k in ('Pi_lb_med', 'Pi_net_med', 'Pi_ub_med'))


class Override:
    """A view of a Sub with some columns replaced (used to pass a constant benchmark growth to the paper's spend_ratio)."""

    def __init__(self, z, **kw):
        self.z, self.kw = z, kw

    def __getitem__(self, k):
        return self.kw[k] if k in self.kw else self.z[k]

    def __len__(self):
        return len(self.z)


def stats(z, mn, observed, parts=('P95', 'PSI', 'DIFF', 'SPEND', 'ANC')):
    out = OrderedDict()
    g, per, yr = z['g'], z['per'], z['year']
    if 'P95' in parts:
        early = per == 1
        late = {'2023_25': per == 3, '2023_24': (yr == 2023) | (yr == 2024), '2025': yr == 2025}
        for ms, (_, Rc) in MEAS.items():
            y = z[Rc]
            for qn, qq in QS.items():
                a = q(y[early], qq)
                for ln in LATES:
                    out[('P95', ms, qn, ln)] = q(y[late[ln]], qq) - a
    if 'PSI' in parts or 'DIFF' in parts:
        spl = {'A': (np.isin(per, [0, 1]), np.isin(per, [2, 3])), 'B': ((yr >= 2010) & (yr <= 2015), (yr >= 2018) & (yr <= 2025))}
        for ms, (mc, _) in MEAS.items():
            y = z[mc]
            k = fin(g) & fin(y)
            if 'PSI' in parts:
                R, cnt = cone_mat(g[k], y[k], min_n=mn)
                for e in EST:
                    for wn, w in WIN.items():
                        out[('PSI', ms, e, wn)] = wslope(R[EST_ROW[e]], w)
                out[('PHI60', ms)] = R[2, 12]                       # phi_0.90 at 60% growth (GPT-16)
                out[('CELL60', ms)] = float(cnt[12])
            if 'DIFF' in parts:
                for sn in SPLITS:
                    ea, la = spl[sn]
                    Re = cone_mat(g[k & ea], y[k & ea], min_n=mn)[0]
                    Rl = cone_mat(g[k & la], y[k & la], min_n=mn)[0]
                    for e in EST:
                        for wn, w in WIN.items():
                            out[('DIFF', ms, e, wn, sn)] = wslope(Rl[EST_ROW[e]], w) - wslope(Re[EST_ROW[e]], w)
    if 'SPEND' in parts:
        for bn, c in BENCH.items():
            out[('SPEND', bn)] = spend_ratio(z if c is None else Override(z, G_t=np.full(len(z), c)))
    if 'ANC' in parts:
        for cut in CUTS:
            for tail in (('drop', 'keep') if observed else ('keep',)):
                v = anchor_vec(z, cut, tail == 'drop')
                out[('ANC', 'lb', cut, tail)] = v[IX_LB]
                out[('ANC', 'net', cut, tail)] = v[IX_NET]
                out[('ANC', 'ub', cut, tail)] = v[IX_UB]
    return out


def is_obs(s):
    return ACQ[s['acq']][0] == 'observed'


# =============================================================================================== 4. reproduction check
def reproduction_check():
    nchk, worst, fails = 0, 0.0, []

    def chk(label, mine, ref, tol=1e-12):
        nonlocal nchk, worst
        nchk += 1
        if ref is None:
            ok = not fin(mine)
        else:
            d = abs(mine - ref)
            worst = max(worst, d if fin(d) else np.inf)
            ok = fin(mine) and d <= tol
        if not ok:
            fails.append((label, mine, ref))

    for vn, sid in PUB_SID.items():
        s = SAMPLES[sid]
        df = build(s)
        ref = V[vn]
        key = lambda d: sorted(zip(d.cik, d.year, d.fy_end))
        assert key(df) == key(ref), f'{vn}: sample rows differ from the paper frame'
        mg = df.merge(ref, on=['cik', 'year', 'fy_end'], suffixes=('', '_p'))
        for c in ['g', 'm_op', 'm_fcf_sbc', 'R_op', 'R_cash', 'G_t', 'sm_lag_share', 'acq_flag'] + \
                 (['m_cash_pre', 'm_cash_bi', 'R_cash_pre', 'R_cash_bi'] if 'm_cash_pre' in ref.columns else []):
            a, b = mg[c].to_numpy(float), mg[c + '_p'].to_numpy(float)
            assert np.array_equal(np.isnan(a), np.isnan(b)) and np.allclose(a[~np.isnan(a)], b[~np.isnan(b)], rtol=0, atol=1e-15), (vn, c)
        z = Sub(arrays(df))
        st = stats(z, MIN_CELL, is_obs(s))
        ev = lambda name: E3[name][vn]['est'] if vn in E3.get(name, {}) else 'absent'
        for b, ms in (('op', 'op'), ('cash', 'cash')):
            for qn in ('p95', 'p90'):
                r = ev(f'{qn}_change_{b}')
                if r != 'absent':
                    chk(f'{vn} {qn}_change_{b}', st[('P95', ms, qn, '2023_25')], r)
            for ln, nm in (('2025', '2025'), ('2023_24', '2023_24')):
                r = ev(f'p95_change_{b}_2016_19_to_{nm}')
                if r != 'absent':
                    chk(f'{vn} p95 to {nm} {b}', st[('P95', ms, 'p95', ln)], r)
            for e in EST:
                for wn in WIN:
                    nm = f'cone_{b}_slope_{"orderm25" if e == "om25" else e}_{wn}'
                    r = ev(nm)
                    if r != 'absent':
                        chk(f'{vn} {nm}', st[('PSI', ms, e, wn)], r)
            for wn in WIN:
                for sn, nm in (('A', '2020_25_minus_2010_19'), ('B', '2018_25_minus_2010_15')):
                    r = ev(f'cone_{b}_slope_c90_{wn}_{nm}')
                    if r != 'absent':
                        chk(f'{vn} cone {b} c90 {wn} {nm}', st[('DIFF', ms, 'c90', wn, sn)], r)
            r = ev(f'cone_{b}_phi90_g60')
            if r != 'absent':
                chk(f'{vn} phi90 g60 {b}', st[('PHI60', ms)], r)
            r = ev(f'cone_{b}_cell60')
            if r != 'absent':
                chk(f'{vn} cell60 {b}', st[('CELL60', ms)], r)
        for ms in ('cash_pre', 'cash_bi'):
            r = ev(f'bridge_{ms}_p95_change')
            if r != 'absent':
                chk(f'{vn} bridge {ms}', st[('P95', ms, 'p95', '2023_25')], r)
        for bn, nm in (('median', 'spend_ratio'), ('G05', 'spend_G05_ratio'), ('G08', 'spend_G08_ratio'), ('G12', 'spend_G12_ratio')):
            r = ev(nm)
            if r != 'absent':
                chk(f'{vn} {nm}', st[('SPEND', bn)], r)
        tail = 'drop' if vn == 'E1' else 'keep'
        for cut, cn in ((0.95, 'p95'), (0.975, 'p975')):
            for basis, nm in (('lb', 'Pi_lb_med'), ('net', 'Pi_net_med'), ('ub', 'Pi_ub_med')):
                r = ev(f'anchor_{cn}_{nm}')
                if r != 'absent':
                    chk(f'{vn} anchor {cn} {nm}', st[('ANC', basis, cut, tail)], r)
        CS = J3['anchor']['cutoff_sensitivity']
        for cut in CUTS:
            for tl, key_vn in ((tail, vn), ('keep', 'E1all')):
                if key_vn == 'E1all' and vn != 'E1':
                    continue
                k_ = f'{key_vn}|{cut}'
                if k_ in CS:
                    chk(f'{k_} Pi_lb', st[('ANC', 'lb', cut, tl)], CS[k_]['Pi_lb'][1], 1e-12)
                    chk(f'{k_} Pi_ub', st[('ANC', 'ub', cut, tl)], CS[k_]['Pi_ub'][1], 1e-12)
        if vn == 'E1':                                              # the paper's leave-one-firm range of the anchor
            A = z.A
            LO = J3['anchor']['leave_one_firm_out_median_Pi_ub']['E1']
            nm2fi = {nm: int(df.loc[df.name == nm, 'cik'].map(EV['UIX']).iloc[0]) for nm in LO}
            for nm, ref_v in LO.items():
                zz = Sub(A, np.nonzero(A['fi'] != nm2fi[nm])[0])
                chk(f'E1 anchor LOFO {nm}', anchor_vec(zz, 0.95, True)[IX_UB], ref_v)
    # printed macros (rounded as code/paper1_macros.py rounds them)
    M = {}
    for vn, tag in (('E1', 'Eone'), ('E2', 'Etwo'), ('E2imp4', 'ImpFour'), ('E2imp8', 'ImpEight')):
        s = SAMPLES[PUB_SID[vn]]
        st = stats(Sub(arrays(build(s))), MIN_CELL, is_obs(s))
        M[f'TopFallOp{tag}'] = fmt_num(-st[('P95', 'op', 'p95', '2023_25')], 1, 100)
        M[f'TopFallCash{tag}'] = fmt_num(-st[('P95', 'cash', 'p95', '2023_25')], 1, 100)
        M[f'PsiOp{tag}'] = fmt_num(st[('PSI', 'op', 'c90', 'w60')], 2, 1)
        M[f'PsiCash{tag}'] = fmt_num(st[('PSI', 'cash', 'c90', 'w60')], 2, 1)
        M[f'PsiDiffOp{tag}'] = fmt_num(st[('DIFF', 'op', 'c90', 'w40', 'A')], 2, 1)
        M[f'PsiDiffCash{tag}'] = fmt_num(st[('DIFF', 'cash', 'c90', 'w40', 'A')], 2, 1)
        M[f'Spend{tag}'] = fmt_num(st[('SPEND', 'median')], 2, 1)
        tl = 'drop' if vn == 'E1' else 'keep'
        M[f'AncPiLb{tag}'] = fmt_sgn(st[('ANC', 'lb', 0.95, tl)], 1, 100)
        M[f'AncPiNet{tag}'] = fmt_sgn(st[('ANC', 'net', 0.95, tl)], 1, 100)
        M[f'AncPiUb{tag}'] = fmt_sgn(st[('ANC', 'ub', 0.95, tl)], 1, 100)
        if vn == 'E1':                                              # levels behind the changes, and the period slopes
            z1 = Sub(arrays(build(s)))
            for b, tg in (('op', 'Op'), ('cash', 'Cash')):
                y = z1[MEAS[b][1]]
                M[f'TopEarly{tg}'] = fmt_num(q(y[z1['per'] == 1], .95), 1, 100)
                M[f'TopLate{tg}'] = fmt_num(q(y[z1['per'] == 3], .95), 1, 100)
                M[f'PsiEarly{tg}'] = fmt_num(wslope_period(z1, b, 0), 2, 1)
                M[f'PsiLate{tg}'] = fmt_num(wslope_period(z1, b, 1), 2, 1)
    nmac, mac_fail = 0, []
    for k, v in M.items():
        nmac += 1
        if PRINTED.get(k) != v:
            mac_fail.append((k, v, PRINTED.get(k)))
    return dict(n_json_checks=nchk, max_abs_diff=worst, json_failures=[list(map(str, f)) for f in fails],
                n_macro_checks=nmac, macro_failures=mac_fail, macros_checked=sorted(M))


def wslope_period(z, b, late):
    g, y, per = z['g'], z[MEAS[b][0]], z['per']
    k = fin(g) & fin(y) & np.isin(per, [2, 3] if late else [0, 1])
    return wslope(cone_mat(g[k], y[k], chis=[0.9], om=False, min_n=MIN_CELL)[0][0], 0.4)


def half_up(x, nd=0):
    qq = 10 ** nd
    return math.floor(x * qq + 0.5) / qq


def fmt_plain(x, nd, scale=1.0):
    return f'{half_up(scale * x, nd):.{nd}f}'


def fmt_num(x, nd, scale=1.0):
    s = fmt_plain(x, nd, scale)
    return f'$-${s[1:]}' if s.startswith('-') else s


def fmt_sgn(x, nd, scale=1.0):
    s = fmt_plain(x, nd, scale)
    if s.startswith('-'):
        return f'$-${s[1:]}'
    return s if float(s) == 0 else f'$+${s}'


# =============================================================================================== 5. specifications
# claim groups: the quantity of each group and its tests (design.md, section 1). holds_a/b/c are the tests' results.
CLAIMS = OrderedDict([
    ('C1', dict(tag='TopOp', label='P95 of the GAAP score, change from 2016-19', dims=['quantile', 'late'], scale=100, nd=1,
                tests=[('a', 'change < 0', lambda v: v < 0)])),
    ('C2', dict(tag='TopCash', label='P95 of the cash score, change from 2016-19', dims=['quantile', 'late', 'measure'], scale=100, nd=1,
                tests=[('a', 'change < 0', lambda v: v < 0)])),
    ('C3', dict(tag='PsiOp', label='Psi slope, GAAP', dims=['estimator', 'window'], scale=1, nd=2,
                tests=[('a', 'slope > -1', lambda v: v > -1), ('b', 'slope < 0', lambda v: v < 0), ('c', 'slope > -0.5', lambda v: v > -0.5)])),
    ('C4', dict(tag='PsiCash', label='Psi slope, cash', dims=['estimator', 'window', 'measure'], scale=1, nd=2,
                tests=[('a', 'slope > -1', lambda v: v > -1), ('b', 'slope < 0', lambda v: v < 0), ('c', 'slope > -0.5', lambda v: v > -0.5)])),
    ('C5', dict(tag='DiffOp', label='Steepening of the GAAP frontier (late minus early slope)', dims=['estimator', 'window', 'split'], scale=1, nd=2,
                tests=[('a', 'difference < 0', lambda v: v < 0)])),
    ('C6', dict(tag='DiffCash', label='Steepening of the cash frontier (late minus early slope)', dims=['estimator', 'window', 'split', 'measure'], scale=1, nd=2,
                tests=[('a', 'difference >= 0 (no steepening in sign)', lambda v: v >= 0)])),
    ('C7', dict(tag='Spend', label='Spend ratio', dims=[], scale=1, nd=2,
                tests=[('a', '2.95 <= ratio < 3.55', lambda v: (v >= 2.95) & (v < 3.55))])),
    ('C7s', dict(tag='SpendBench', label='Spend ratio, benchmark growth varied (secondary)', dims=['benchmark'], scale=1, nd=2,
                 tests=[('a', '2.95 <= ratio < 3.55', lambda v: (v >= 2.95) & (v < 3.55))])),
    ('C8a', dict(tag='AncLb', label='Anchor surplus, no S&M buys growth (median Pi_lb)', dims=['cutoff', 'tail'], scale=100, nd=1,
                 tests=[('a', 'median > 0', lambda v: v > 0)])),
    ('C8b', dict(tag='AncNet', label='Anchor surplus, netted basis (median Pi_net)', dims=['cutoff', 'tail'], scale=100, nd=1,
                 tests=[('a', 'median > 0', lambda v: v > 0)])),
    ('C8c', dict(tag='AncUb', label='Anchor surplus, all S&M buys growth (median Pi_ub; no claim)', dims=['cutoff', 'tail'], scale=100, nd=1,
                 tests=[('a', 'median > 0 (descriptive)', lambda v: v > 0)])),
])
# bootstrap test: the 90% percentile interval lies on the claimed side
BOOT_TEST = {'C1': ('a', lambda lo, hi: hi < 0), 'C2': ('a', lambda lo, hi: hi < 0), 'C5': ('a', lambda lo, hi: hi < 0),
             'C3': ('a', lambda lo, hi: lo > -1), 'C4': ('a', lambda lo, hi: lo > -1),
             'C6': ('a', lambda lo, hi: not (hi < 0)), 'C8a': ('a', lambda lo, hi: lo > 0), 'C8b': ('a', lambda lo, hi: lo > 0)}
BOOT_TEST_B = {'C3': lambda lo, hi: hi < 0, 'C4': lambda lo, hi: hi < 0}      # C3b, C4b: interval below zero
BASE_CLAIM = dict(quantile='p95', late='2023_25', estimator='c90', benchmark='median', cutoff=0.95)
CLAIM_DIM_BASE = {'C1': dict(measure='op'), 'C2': dict(measure='cash'), 'C3': dict(measure='op', window='w60'),
                  'C4': dict(measure='cash', window='w60'), 'C5': dict(measure='op', window='w40', split='A'),
                  'C6': dict(measure='cash', window='w40', split='A')}
SPEC_COLS = ['claim', 'sid'] + list(SDIMS) + ['family', 'measure', 'quantile', 'late', 'estimator', 'window', 'split',
                                               'benchmark', 'cutoff', 'tail', 'value']


def spec_rows(s, st):
    base = [s['sid']] + [s[k] for k in SDIMS] + [ACQ[s['acq']][0]]
    out = []
    for key, val in st.items():
        k0 = key[0]
        r = dict(measure='', quantile='', late='', estimator='', window='', split='', benchmark='', cutoff='', tail='')
        if k0 == 'P95':
            claim = 'C1' if key[1] == 'op' else 'C2'
            r.update(measure=key[1], quantile=key[2], late=key[3])
        elif k0 == 'PSI':
            claim = 'C3' if key[1] == 'op' else 'C4'
            r.update(measure=key[1], estimator=key[2], window=key[3])
        elif k0 == 'DIFF':
            claim = 'C5' if key[1] == 'op' else 'C6'
            r.update(measure=key[1], estimator=key[2], window=key[3], split=key[4])
        elif k0 == 'SPEND':
            claim = 'C7' if key[1] == 'median' else 'C7s'
            r.update(benchmark=key[1])
        elif k0 == 'ANC':
            claim = {'lb': 'C8a', 'net': 'C8b', 'ub': 'C8c'}[key[1]]
            r.update(cutoff=key[2], tail=key[3])
        else:
            continue
        out.append([claim] + base + [r[c] for c in SPEC_COLS[3 + len(SDIMS):-1]] + [val])
        if k0 == 'SPEND' and key[1] == 'median':                    # ... so the median benchmark also enters C7s
            out.append(['C7s'] + base + [r[c] for c in SPEC_COLS[3 + len(SDIMS):-1]] + [val])
    return out


def is_baseline_row(df):
    """Baseline specification of each claim: the baseline sample and the paper's claim-specific choices."""
    b = np.ones(len(df), bool)
    for k, v in BASE_SAMPLE.items():
        b &= (df[k] == v).values
    out = np.zeros(len(df), bool)
    for c in CLAIMS:
        m = b & (df.claim == c).values
        d = dict(CLAIM_DIM_BASE.get(c, {}))
        if c in ('C1', 'C2'):
            d.update(quantile='p95', late='2023_25')
        if c in ('C3', 'C4', 'C5', 'C6'):
            d.update(estimator='c90')
        if c in ('C7', 'C7s'):
            d.update(benchmark='median')
        if c.startswith('C8'):
            d.update(cutoff=0.95, tail='drop')
        for k, v in d.items():
            m &= (df[k] == v).values
        out |= m
    return out


def add_tests(df):
    for c, cd in CLAIMS.items():
        m = (df.claim == c).values
        v = df.value.values[m]
        for tn, _, f in cd['tests']:
            col = f'holds_{tn}'
            if col not in df:
                df[col] = np.nan
            res = np.where(fin(v), f(np.nan_to_num(v, nan=0.0)).astype(float), np.nan)
            df.loc[m, col] = res
    return df


def influence(d, c):
    """Per choice: medians and primary-test shares by level, range of the level medians, eta squared."""
    cd = CLAIMS[c]
    dims = list(SDIMS) + cd['dims'] + ['family']
    out = OrderedDict()
    v_all = d.value.values
    for dim in dims:
        dd = d[d.family == 'observed'] if dim == 'tail' else d   # the tail rule applies to observed-growth samples only
        if dd[dim].nunique() < 2:
            continue
        vv = dd.value.values
        lv = OrderedDict()
        for lev, gq in dd.groupby(dim, sort=False):
            lv[str(lev)] = dict(n=int(len(gq)), median=float(np.median(gq.value)), share=float(gq.holds_a.mean()),
                                min=float(gq.value.min()), max=float(gq.value.max()))
        mu = vv.mean()
        ss_t = ((vv - mu) ** 2).sum()
        ss_b = sum(len(gq) * (gq.value.mean() - mu) ** 2 for _, gq in dd.groupby(dim))
        meds = [x['median'] for x in lv.values()]
        out[dim] = dict(levels=lv, range_of_medians=float(max(meds) - min(meds)), eta2=float(ss_b / ss_t) if ss_t > 0 else 0.0,
                        within='observed-growth samples' if dim == 'tail' else 'all valid specifications')
    ranked = sorted([k for k in out if k != 'family'], key=lambda k: -out[k]['range_of_medians'])
    return out, ranked


def summarize_claim(d, c, boot=None):
    cd = CLAIMS[c]
    dv = d[fin(d.value)]
    rec = OrderedDict(label=cd['label'], n_specs=int(len(d)), n_valid=int(len(dv)), n_invalid=int(len(d) - len(dv)))
    for tn, tl, _ in cd['tests']:
        rec[f'share_{tn}'] = float(dv[f'holds_{tn}'].mean())
        rec[f'test_{tn}'] = tl
    v = dv.value.values
    rec.update(median=float(np.median(v)), min=float(v.min()), max=float(v.max()), p05=float(np.quantile(v, .05)),
               p95=float(np.quantile(v, .95)), share_negative=float((v < 0).mean()))
    bl = dv[dv.baseline]
    assert len(bl) == 1, (c, len(bl))
    rec['baseline'] = float(bl.value.iloc[0])
    rec['baseline_holds_a'] = bool(bl.holds_a.iloc[0])
    infl, ranked = influence(dv, c)
    rec['influence'] = infl
    rec['ranked_choices'] = ranked
    rec['most_influential'] = ranked[0] if ranked else None
    rec['by_family'] = {k: dict(n=int(len(g_)), share=float(g_.holds_a.mean()), median=float(np.median(g_.value)))
                        for k, g_ in dv.groupby('family', sort=False)}
    rec['invalid_by_dim'] = {}
    inv = d[~fin(d.value)]
    for dim in cd['dims']:
        if len(inv):
            rec['invalid_by_dim'][dim] = {str(k): int(x) for k, x in inv[dim].value_counts().items()}
    return rec


# =============================================================================================== 6. forward pairing
NEXT_COLS = ['g', 'period', 'year', 'm_op', 'm_fcf_sbc', 'm_cash_pre', 'm_cash_bi', 'm_cash_bs']


def forward_frame(df, kind):
    """F1: g_{t+1} + m_t indexed by t; F1p: the same pairs indexed by t+1; F2: g_t + m_{t+1} indexed by t."""
    assert not df.duplicated(['cik', 'year']).any()
    nx = df[['cik'] + NEXT_COLS].copy()
    nx['year'] = nx.year - 1
    nx = nx.rename(columns={c: c + '_n' for c in NEXT_COLS if c != 'year'})
    F = df.merge(nx, on=['cik', 'year'], how='inner', validate='one_to_one')
    if kind in ('F1', 'F1p'):
        F['g'] = F.g_n
        if kind == 'F1p':
            F['year'] = F.year + 1
            F['period'] = F.period_n
    elif kind == 'F2':
        for c in ('m_op', 'm_fcf_sbc', 'm_cash_pre', 'm_cash_bi', 'm_cash_bs'):
            F[c] = F[c + '_n']
    else:
        raise ValueError(kind)
    F['R_op'], F['R_cash'] = F.g + F.m_op, F.g + F.m_fcf_sbc
    for m_, R_ in [('m_cash_pre', 'R_cash_pre'), ('m_cash_bi', 'R_cash_bi'), ('m_cash_bs', 'R_cash_bs')]:
        F[R_] = F.g + F[m_]
    return F.reset_index(drop=True)


HEAD_KEYS = OrderedDict([('C1', ('P95', 'op', 'p95', '2023_25')), ('C2', ('P95', 'cash', 'p95', '2023_25')),
                         ('C3', ('PSI', 'op', 'c90', 'w60')), ('C4', ('PSI', 'cash', 'c90', 'w60')),
                         ('C5', ('DIFF', 'op', 'c90', 'w40', 'A')), ('C6', ('DIFF', 'cash', 'c90', 'w40', 'A'))])


def headline(st):
    return OrderedDict((c, st[k]) for c, k in HEAD_KEYS.items())


# =============================================================================================== 7. bootstrap worker
DRAWS = None


def boot_sample(sid):
    s = SAMPLES[sid]
    A = arrays(build(s))
    rows = A['_rows']
    keys, mat = None, []
    for b in range(DRAWS.shape[0]):
        z = Sub(A, np.concatenate([rows[j] for j in DRAWS[b]]))
        st = stats(z, 10, is_obs(s))
        if keys is None:
            keys = list(st)
        mat.append([st[k] for k in keys])
    mat = np.asarray(mat, float)
    ok = fin(mat)
    res = {}
    for j, k in enumerate(keys):
        x = mat[ok[:, j], j]
        nan_share = 1 - len(x) / len(mat)
        res[k] = (float(np.quantile(x, .05)) if len(x) else np.nan, float(np.quantile(x, .95)) if len(x) else np.nan, nan_share)
    return sid, res


def main():
    REPRO = reproduction_check()
    log('reproduction check:', REPRO['n_json_checks'], 'statistics against notes/empirics_v3.json, max |diff|',
        f"{REPRO['max_abs_diff']:.2e};", REPRO['n_macro_checks'], 'printed macros')
    if REPRO['json_failures'] or REPRO['macro_failures']:
        log('REPRODUCTION FAILED', REPRO['json_failures'][:20], REPRO['macro_failures'])
        sys.exit(1)
    log('reproduction check passed')

    # ---- main grid (point estimates) and the F1 grid
    rows, frows, NROW = [], [], {}
    for s in SAMPLES:
        df = build(s)
        NROW[s['sid']] = int(len(df))
        rows += spec_rows(s, stats(Sub(arrays(df)), MIN_CELL, is_obs(s)))
        F = forward_frame(df, 'F1')
        frows += spec_rows(s, stats(Sub(arrays(F)), MIN_CELL, is_obs(s), parts=('P95', 'PSI', 'DIFF')))
    SP = pd.DataFrame(rows, columns=SPEC_COLS)
    FP = pd.DataFrame(frows, columns=SPEC_COLS)
    for d_ in (SP, FP):
        d_['baseline'] = is_baseline_row(d_)
        add_tests(d_)
    log('grid:', len(SAMPLES), 'samples;', len(SP), 'specifications;', len(FP), 'forward-paired specifications')
    T_GRID = time.time() - T_START

    # ---- bootstrap on a subset of samples
    global DRAWS
    BOOT = {}
    K = 0
    if B_BOOT > 0:
        DRAWS = np.random.default_rng(seed_for('spec_curve')).integers(0, NU, (B_BOOT, NU))
        t0 = time.time()
        A0 = arrays(build(SAMPLES[PUB_SID['E1']]))
        for b in range(5):
            stats(Sub(A0, np.concatenate([A0['_rows'][j] for j in DRAWS[b]])), 10, True)
        t_draw = (time.time() - t0) / 5
        cost = B_BOOT * t_draw
        K = int(max(K_MIN, min(len(SAMPLES), math.floor(BUDGET_MIN * 60 * NJOBS * 0.75 / cost))))
        if os.environ.get('SC_BOOT_K'):                             # replication: the K of a previous run (the subset is seeded)
            K = int(os.environ['SC_BOOT_K'])
        must = sorted(set(PUB_SID.values()))
        rest = [s['sid'] for s in SAMPLES if s['sid'] not in must]
        pick = np.random.default_rng(seed_for('spec_curve_subset')).permutation(rest)[:max(0, K - len(must))]
        SUBSET = sorted(must + [int(x) for x in pick])
        log(f'bootstrap: {t_draw * 1000:.0f} ms per draw, {cost:.1f} s per sample; K = {len(SUBSET)} samples x B = {B_BOOT}')
        if NJOBS > 1:
            with get_context('fork').Pool(NJOBS) as pool:
                for i, (sid, res) in enumerate(pool.imap_unordered(boot_sample, SUBSET)):
                    BOOT[sid] = res
                    if (i + 1) % 25 == 0:
                        log(f'bootstrap samples {i + 1}/{len(SUBSET)}')
        else:
            for sid in SUBSET:
                BOOT[sid] = boot_sample(sid)[1]
        log('bootstrap done')
    T_BOOT = time.time() - T_START - T_GRID

    # attach intervals to the specifications of the bootstrapped samples
    for col in ('boot_lo', 'boot_hi', 'boot_nan'):
        SP[col] = np.nan
    if BOOT:
        key_of = {}
        for i, r in enumerate(SP.itertuples(index=False)):
            if r.sid not in BOOT:
                continue
            c = r.claim
            if c in ('C1', 'C2'):
                k = ('P95', r.measure, r.quantile, r.late)
            elif c in ('C3', 'C4'):
                k = ('PSI', r.measure, r.estimator, r.window)
            elif c in ('C5', 'C6'):
                k = ('DIFF', r.measure, r.estimator, r.window, r.split)
            elif c in ('C7', 'C7s'):
                k = ('SPEND', r.benchmark)
            else:
                k = ('ANC', {'C8a': 'lb', 'C8b': 'net', 'C8c': 'ub'}[c], r.cutoff, r.tail)
            key_of[i] = BOOT[r.sid][k]
        ix = np.array(list(key_of))
        vals = np.array([key_of[i] for i in ix])
        SP.loc[ix, 'boot_lo'], SP.loc[ix, 'boot_hi'], SP.loc[ix, 'boot_nan'] = vals[:, 0], vals[:, 1], vals[:, 2]
    SP['boot_ok'] = SP.boot_nan.notna() & (SP.boot_nan <= 0.05) & fin(SP.value)
    SP['boot_holds'] = np.nan
    SP['boot_holds_b'] = np.nan
    for c, (_, f) in BOOT_TEST.items():
        m = (SP.claim == c) & SP.boot_ok
        SP.loc[m, 'boot_holds'] = [float(f(lo, hi)) for lo, hi in zip(SP.loc[m, 'boot_lo'], SP.loc[m, 'boot_hi'])]
    for c, f in BOOT_TEST_B.items():
        m = (SP.claim == c) & SP.boot_ok
        SP.loc[m, 'boot_holds_b'] = [float(f(lo, hi)) for lo, hi in zip(SP.loc[m, 'boot_lo'], SP.loc[m, 'boot_hi'])]

    # ---- summaries
    SUMM = OrderedDict()
    for c in CLAIMS:
        rec = summarize_claim(SP[SP.claim == c], c)
        bs = SP[(SP.claim == c) & SP.boot_ok]
        if c in BOOT_TEST and len(bs):
            rec['boot'] = dict(n_specs=int(len(bs)), n_samples=int(bs.sid.nunique()), share_interval_on_claimed_side=float(bs.boot_holds.mean()),
                               share_point_holds_same_specs=float(bs.holds_a.mean()),
                               n_without_interval=int(((SP.claim == c) & SP.sid.isin(list(BOOT)) & fin(SP.value) & ~SP.boot_ok).sum()))
            if c in BOOT_TEST_B:
                rec['boot']['share_interval_below_zero'] = float(bs.boot_holds_b.mean())
            bl = bs[bs.baseline]
            if len(bl):
                rec['boot']['baseline_ci90'] = [float(bl.boot_lo.iloc[0]), float(bl.boot_hi.iloc[0])]
        SUMM[c] = rec
    FSUMM = OrderedDict((c, summarize_claim(FP[FP.claim == c], c)) for c in ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'])
    log('summaries done')

    # ---- forward pairing: baseline and the four views, three pairings
    FWD = OrderedDict()
    for vn in FOUR:
        s = SAMPLES[PUB_SID[vn]]
        df = build(s)
        rec = OrderedDict(contemporaneous=headline(stats(Sub(arrays(df)), MIN_CELL, True, parts=('P95', 'PSI', 'DIFF'))))
        rec['n'] = dict(contemporaneous=int(len(df)))
        for kind in ('F1', 'F1p', 'F2'):
            F = forward_frame(df, kind)
            z = Sub(arrays(F))
            st = stats(z, MIN_CELL, True, parts=('P95', 'PSI', 'DIFF'))
            rec[kind] = headline(st)
            rec['n'][kind] = int(len(F))
            rec.setdefault('n_by_period', {})[kind] = {p: int((F.period == p).sum()) for p in PERIODS}
            rec.setdefault('cell60', {})[kind] = {b: st[('CELL60', b)] for b in ('op', 'cash')}
            rec.setdefault('p95_levels', {})[kind] = {b: [q(z[MEAS[b][1]][z['per'] == 1], .95), q(z[MEAS[b][1]][z['per'] == 3], .95)] for b in ('op', 'cash')}
        rec['n_by_period']['contemporaneous'] = {p: int((df.period == p).sum()) for p in PERIODS}
        FWD[vn] = rec
    log('forward pairing done')

    # ---- leave one firm out (four views)
    LOFO = OrderedDict()
    for vn in FOUR:
        s = SAMPLES[PUB_SID[vn]]
        df = build(s)
        A = arrays(df)
        full_st = stats(Sub(A), MIN_CELL, is_obs(s), parts=('P95', 'PSI', 'DIFF', 'ANC'))
        name_of = df.groupby('cik').name.first()
        firms = sorted(df.cik.unique())
        keys = list(HEAD_KEYS.values()) + [('PHI60', 'op'), ('PHI60', 'cash'), ('CELL60', 'op'), ('CELL60', 'cash')]
        tl = 'drop' if vn == 'E1' else 'keep'
        akeys = [('ANC', 'lb', 0.95, tl), ('ANC', 'net', 0.95, tl), ('ANC', 'ub', 0.95, tl)]
        vals = {}
        for c_ in firms:
            zz = Sub(A, np.nonzero(A['fi'] != EV['UIX'][c_])[0])
            st = stats(zz, MIN_CELL, is_obs(s), parts=('P95', 'PSI', 'DIFF', 'ANC'))
            vals[c_] = [st[k] for k in keys + akeys]
        rec = OrderedDict(n_firms=len(firms))
        for j, k in enumerate(keys + akeys):
            x = np.array([vals[c_][j] for c_ in firms])
            f0 = full_st[k]
            okx = fin(x)
            i_lo, i_hi = int(np.nanargmin(x)), int(np.nanargmax(x))
            dev = np.abs(x - f0)
            i_mx = int(np.nanargmax(dev))
            nm = '|'.join(map(str, k))
            rec[nm] = dict(full=float(f0), min=float(np.nanmin(x)), max=float(np.nanmax(x)), n_undefined=int((~okx).sum()),
                           firm_at_min=str(name_of[firms[i_lo]]), firm_at_max=str(name_of[firms[i_hi]]),
                           most_influential_firm=str(name_of[firms[i_mx]]), largest_move=float(x[i_mx] - f0),
                           n_sign_reversals=int(np.sum(okx & (np.sign(x) != np.sign(f0)) & (x != 0))))
        LOFO[vn] = rec
    log('leave one firm out done')

    RUNTIME = time.time() - T_START
    return dict(REPRO=REPRO, SP=SP, FP=FP, SUMM=SUMM, FSUMM=FSUMM, FWD=FWD, LOFO=LOFO, BOOT_K=len(BOOT), NROW=NROW,
                T_GRID=T_GRID, T_BOOT=T_BOOT, RUNTIME=RUNTIME)


# =============================================================================================== 8. outputs
DIM_WORDS = dict(acq='treatment of acquired growth', r1='rule R1 (fiscal 2010)', r2='rule R2 (named firms)', r5='rule R5 (listed equity)',
                 debt='debt-only filers', trim='growth bound', quantile='upper quantile', late='end period', measure='cash measure',
                 estimator='frontier estimator', window='growth window', split='period split', benchmark='benchmark growth',
                 cutoff='anchor cut-off', tail='acquisition years in the tail', family='family of acquisition treatment')
TEX_DIM = dict(DIM_WORDS, r1='rule R1', r2='rule R2', r5='rule R5')
FIG_PATH = os.path.join(BASE, 'figures', 'fig_spec_curve.pdf')
MAC_PATH = os.path.join(BASE, 'paper1', 'spec_macros.tex')
TAB_PATH = os.path.join(BASE, 'sections', 'tables', 'tab_spec_curve.tex')


def thousands(n):
    return f'{int(n):,}'.replace(',', '{,}')


def pct_share(x):
    if x == 1:
        return '100'
    if x == 0:
        return '0'
    v = half_up(100 * x, 1)
    if v >= 100:
        return r'$>$99.9'
    if v <= 0:
        return r'$<$0.1'
    return f'{v:.1f}'


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, np.ndarray):
        return clean(o.tolist())
    if isinstance(o, (np.floating, np.integer, np.bool_)):
        o = o.item()
    if isinstance(o, float) and not math.isfinite(o):
        return None
    return o


def write_outputs(R):
    SP, FP, SUMM, FSUMM, FWD, LOFO, REPRO = R['SP'], R['FP'], R['SUMM'], R['FSUMM'], R['FWD'], R['LOFO'], R['REPRO']
    V_ = lambda c: SP[(SP.claim == c) & fin(SP.value)]
    # ---- derived summaries used by the text (computed here from the specifications)
    EXTRA = OrderedDict()
    for c in CLAIMS:
        d = V_(c)
        b = SUMM[c]['baseline']
        EXTRA[c] = dict(share_below_baseline=float((d.value < b).mean()), share_above_baseline=float((d.value > b).mean()))
    d1, d2 = V_('C1'), V_('C2')
    core1 = d1[(d1['quantile'] == 'p95') & (d1['late'] == '2023_25')]
    core2 = d2[(d2['quantile'] == 'p95') & (d2['late'] == '2023_25') & (d2['measure'] == 'cash')]
    EXTRA['decline'] = dict(
        p95_share_gaap=float(d1[d1['quantile'] == 'p95'].holds_a.mean()), p95_share_cash=float(d2[d2['quantile'] == 'p95'].holds_a.mean()),
        gaap_fail_all_p90_2025=bool(((d1.holds_a == 0) <= ((d1['quantile'] == 'p90') & (d1['late'] == '2025'))).all()),
        n_fail_gaap=int((d1.holds_a == 0).sum()),
        share_p90_2025_gaap=float(d1[(d1['quantile'] == 'p90') & (d1['late'] == '2025')].holds_a.mean()),
        core_gaap=[float(core1.value.min()), float(core1.value.max()), float(core1.value.median())],
        core_cash=[float(core2.value.min()), float(core2.value.max()), float(core2.value.median())],
        core_both_fall=[float(-max(core1.value.max(), core2.value.max())), float(-min(core1.value.min(), core2.value.min()))],
        core_share_below_baseline_gaap=float((core1.value < SUMM['C1']['baseline']).mean()),
        core_share_below_baseline_cash=float((core2.value < SUMM['C2']['baseline']).mean()))
    d3, d4 = V_('C3'), V_('C4')
    EXTRA['psi'] = dict(w60_gaap=[float(d3[d3['window'] == 'w60'].value.min()), float(d3[d3['window'] == 'w60'].value.max()), float(d3[d3['window'] == 'w60'].value.median())],
                        w60_cash=[float(d4[d4['window'] == 'w60'].value.min()), float(d4[d4['window'] == 'w60'].value.max()), float(d4[d4['window'] == 'w60'].value.median())],
                        w60c90_gaap=[float(d3[(d3['window'] == 'w60') & (d3['estimator'] == 'c90')].value.min()), float(d3[(d3['window'] == 'w60') & (d3['estimator'] == 'c90')].value.max())],
                        w60c90_cash=[float(d4[(d4['window'] == 'w60') & (d4['estimator'] == 'c90') & (d4['measure'] == 'cash')].value.min()),
                                     float(d4[(d4['window'] == 'w60') & (d4['estimator'] == 'c90') & (d4['measure'] == 'cash')].value.max())])
    d6 = V_('C6')
    EXTRA['cash_steepening'] = dict(neg_share_observed=float((d6[d6.family == 'observed'].value < 0).mean()),
                                    neg_share_organic=float((d6[d6.family.isin(['pro forma', 'exclusion'])].value < 0).mean()),
                                    neg_share_imputed=float((d6[d6.family == 'imputed'].value < 0).mean()),
                                    neg_share_split_B=float((d6[d6['split'] == 'B'].value < 0).mean()),
                                    neg_share_split_A=float((d6[d6['split'] == 'A'].value < 0).mean()))
    b6 = SP[(SP.claim == 'C6') & SP.boot_ok]
    if len(b6):
        EXTRA['cash_steepening'].update(boot_below_zero_observed=float((b6[b6.family == 'observed'].boot_hi < 0).mean()),
                                        boot_below_zero_other=float((b6[b6.family != 'observed'].boot_hi < 0).mean()),
                                        boot_below_zero_split_B=float((b6[b6['split'] == 'B'].boot_hi < 0).mean()))
    d7 = V_('C7')
    EXTRA['spend'] = dict(share_above=float((d7.value >= 3.55).mean()), share_below=float((d7.value < 2.95).mean()),
                          share_r2all=float(d7[d7.r2 == 'all'].holds_a.mean()), share_not_r2all=float(d7[d7.r2 != 'all'].holds_a.mean()))
    dF1 = FP[(FP.claim == 'C1') & fin(FP.value)]
    EXTRA['forward_fail_gaap'] = int((dF1.holds_a == 0).sum())
    bt = SP[SP.boot_ok]
    if len(bt):
        bsh = lambda m: float(bt[m].boot_holds.mean()) if m.any() else float('nan')
        cl = bt.claim
        blr = lambda c: [float(SP[SP.baseline & (SP.claim == c)].boot_lo.iloc[0]), float(SP[SP.baseline & (SP.claim == c)].boot_hi.iloc[0])]
        EXTRA['boot'] = dict(
            top_op_core=bsh((cl == 'C1') & (bt['quantile'] == 'p95') & (bt['late'] == '2023_25')),
            top_cash_core=bsh((cl == 'C2') & (bt['quantile'] == 'p95') & (bt['late'] == '2023_25') & (bt['measure'] == 'cash')),
            top_op_p90=bsh((cl == 'C1') & (bt['quantile'] == 'p90')), top_op_2025=bsh((cl == 'C1') & (bt['late'] == '2025')),
            top_cash_2025=bsh((cl == 'C2') & (bt['late'] == '2025')),
            diff_op_c90=bsh((cl == 'C5') & (bt['estimator'] == 'c90')),
            diff_op_c90_A=bsh((cl == 'C5') & (bt['estimator'] == 'c90') & (bt['split'] == 'A')),
            diff_op_c90_B=bsh((cl == 'C5') & (bt['estimator'] == 'c90') & (bt['split'] == 'B')),
            anc_net_cut95=bsh((cl == 'C8b') & (bt['cutoff'] == 0.95)),
            anc_net_obs_drop=bsh((cl == 'C8b') & (bt.family == 'observed') & (bt['tail'] == 'drop')),
            baseline_ci90=dict(C1=blr('C1'), C2=blr('C2'), C3=blr('C3'), C4=blr('C4'), C5=blr('C5'), C6=blr('C6'), C8a=blr('C8a'), C8b=blr('C8b')))

    # ---- results.json
    try:
        head = subprocess.run(['git', '-C', BASE, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    except Exception:
        head = ''
    meta = dict(script='code/spec_curve.py', design='notes/spec_curve/design.md (pre-specification, 2026-11-03 14:36 UTC)',
                run_utc=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'), git_head=head,
                runtime_seconds=R['RUNTIME'], grid_seconds=R['T_GRID'], bootstrap_seconds=R['T_BOOT'],
                n_samples=len(SAMPLES), n_specifications=int(len(SP)), n_specifications_forward=int(len(FP)),
                sample_choices={k: v for k, v in SDIMS.items()}, acquisition_levels={k: list(v) for k, v in ACQ.items()},
                claim_choices={c: CLAIMS[c]['dims'] for c in CLAIMS}, tests={c: [t[1] for t in CLAIMS[c]['tests']] for c in CLAIMS},
                bootstrap=dict(B=B_BOOT, samples=R['BOOT_K'], seed=seed_for('spec_curve'), subset_seed=seed_for('spec_curve_subset'),
                               rule='firm-cluster; firms drawn from the 292 firms of E1; same draws for every specification; grid point needs 10 '
                                    'firm-years in a draw; >5% undefined draws: no interval; 90% percentile interval',
                               budget_minutes=BUDGET_MIN, workers=NJOBS),
                units='fractions of revenue for changes and surpluses (0.01 = one point); slopes and the ratio as numbers',
                published_samples={vn: SAMPLES[sid] for vn, sid in PUB_SID.items()})
    OUT = dict(meta=meta, reproduction=REPRO, claims=SUMM, derived=EXTRA, forward=dict(grid_F1=FSUMM, views=FWD),
               leave_one_firm_out=LOFO, sample_sizes=R['NROW'])
    json.dump(clean(OUT), open(os.path.join(OUTD, 'results.json'), 'w'), indent=1)
    cols = [c for c in SP.columns]
    for d_, fn in ((SP, 'specs.csv.gz'), (FP, 'specs_forward.csv.gz')):
        buf = io.StringIO()
        d_[[c for c in cols if c in d_.columns]].to_csv(buf, index=False, float_format='%.10g')
        with gzip.GzipFile(os.path.join(OUTD, fn), 'wb', mtime=0) as fh:
            fh.write(buf.getvalue().encode())
    log('wrote notes/spec_curve/results.json, specs.csv.gz, specs_forward.csv.gz')

    # ---- macros
    MC = OrderedDict()

    def put(name, text):
        assert re.fullmatch(r'Sc[A-Za-z]+', name) and name not in MC, name
        MC[name] = text

    put('ScNSamples', str(len(SAMPLES)))
    put('ScNSpecs', thousands(len(SP)))
    put('ScNSpecsValid', thousands(int(fin(SP.value).sum())))
    put('ScNAcq', str(len(ACQ)))
    put('ScReproN', str(REPRO['n_json_checks']))
    put('ScReproMacros', str(REPRO['n_macro_checks']))
    put('ScReproVariants', str(len(PUB_SID)))
    put('ScBootB', str(B_BOOT))
    put('ScBootK', str(R['BOOT_K']))
    put('ScRuntime', str(int(round(R['RUNTIME'] / 60))))
    for c, cd in CLAIMS.items():
        T, sc, nd = cd['tag'], cd['scale'], cd['nd']
        r = SUMM[c]
        put(f'Sc{T}N', thousands(r['n_valid']))
        put(f'Sc{T}Run', thousands(r['n_specs']))
        put(f'Sc{T}Inv', thousands(r['n_invalid']))
        put(f'Sc{T}Share', pct_share(r['share_a']))
        for k_, nm in (('baseline', 'Base'), ('median', 'Med'), ('min', 'Min'), ('max', 'Max'), ('p05', 'PLo'), ('p95', 'PHi')):
            put(f'Sc{T}{nm}', fmt_sgn(r[k_], nd, sc) if sc == 100 or c in ('C5', 'C6') else fmt_num(r[k_], nd, sc))
        put(f'Sc{T}Infl', DIM_WORDS[r['most_influential']])
        put(f'Sc{T}InflRange', fmt_num(r['influence'][r['most_influential']]['range_of_medians'], nd, sc))
        put(f'Sc{T}BelowBase', pct_share(EXTRA[c]['share_below_baseline']))
        put(f'Sc{T}AboveBase', pct_share(EXTRA[c]['share_above_baseline']))
        if 'boot' in r:
            put(f'Sc{T}BootShare', pct_share(r['boot']['share_interval_on_claimed_side']))
            put(f'Sc{T}BootN', thousands(r['boot']['n_specs']))
            if 'share_interval_below_zero' in r['boot']:
                put(f'Sc{T}BootNeg', pct_share(r['boot']['share_interval_below_zero']))
    for c in ('C3', 'C4'):
        T = CLAIMS[c]['tag']
        put(f'Sc{T}ShareNeg', pct_share(SUMM[c]['share_b']))
        put(f'Sc{T}ShareHalf', pct_share(SUMM[c]['share_c']))
    put('ScDiffCashShareNeg', pct_share(SUMM['C6']['share_negative']))
    # level medians and shares quoted in the text
    LV = lambda c, dim, lev: SUMM[c]['influence'][dim]['levels'][lev]
    put('ScTopOpQNinetyFiveMed', fmt_sgn(LV('C1', 'quantile', 'p95')['median'], 1, 100))
    put('ScTopOpQNinetyMed', fmt_sgn(LV('C1', 'quantile', 'p90')['median'], 1, 100))
    put('ScTopOpLateFiveMed', fmt_sgn(LV('C1', 'late', '2025')['median'], 1, 100))
    put('ScTopOpLateMainMed', fmt_sgn(LV('C1', 'late', '2023_25')['median'], 1, 100))
    put('ScTopOpPNinetyFiveShare', pct_share(EXTRA['decline']['p95_share_gaap']))
    put('ScTopCashPNinetyFiveShare', pct_share(EXTRA['decline']['p95_share_cash']))
    put('ScTopOpFailN', str(EXTRA['decline']['n_fail_gaap']))
    put('ScTopOpPNinetyLastShare', pct_share(EXTRA['decline']['share_p90_2025_gaap']))
    put('ScTopOpCoreMin', fmt_sgn(EXTRA['decline']['core_gaap'][0], 1, 100)); put('ScTopOpCoreMax', fmt_sgn(EXTRA['decline']['core_gaap'][1], 1, 100))
    put('ScTopOpCoreMed', fmt_sgn(EXTRA['decline']['core_gaap'][2], 1, 100))
    put('ScTopCashCoreMin', fmt_sgn(EXTRA['decline']['core_cash'][0], 1, 100)); put('ScTopCashCoreMax', fmt_sgn(EXTRA['decline']['core_cash'][1], 1, 100))
    put('ScTopCashCoreMed', fmt_sgn(EXTRA['decline']['core_cash'][2], 1, 100))
    put('ScTopCoreFallLo', fmt_num(EXTRA['decline']['core_both_fall'][0], 1, 100)); put('ScTopCoreFallHi', fmt_num(EXTRA['decline']['core_both_fall'][1], 1, 100))
    put('ScTopOpCoreBelowBase', pct_share(EXTRA['decline']['core_share_below_baseline_gaap']))
    put('ScTopCashCoreBelowBase', pct_share(EXTRA['decline']['core_share_below_baseline_cash']))
    put('ScPsiOpWinSixtyMed', fmt_num(LV('C3', 'window', 'w60')['median'], 2)); put('ScPsiOpWinFortyMed', fmt_num(LV('C3', 'window', 'w40')['median'], 2))
    put('ScPsiCashWinSixtyMed', fmt_num(LV('C4', 'window', 'w60')['median'], 2)); put('ScPsiCashWinFortyMed', fmt_num(LV('C4', 'window', 'w40')['median'], 2))
    put('ScPsiOpObsMed', fmt_num(SUMM['C3']['by_family']['observed']['median'], 2)); put('ScPsiOpProMed', fmt_num(SUMM['C3']['by_family']['pro forma']['median'], 2))
    put('ScPsiOpNamedMed', fmt_num(LV('C3', 'r2', 'all')['median'], 2)); put('ScPsiOpNoNamedMed', fmt_num(LV('C3', 'r2', 'none')['median'], 2))
    for c, T in (('C3', 'PsiOp'), ('C4', 'PsiCash')):
        k_ = 'w60_gaap' if c == 'C3' else 'w60_cash'
        put(f'Sc{T}SixtyMin', fmt_num(EXTRA['psi'][k_][0], 2)); put(f'Sc{T}SixtyMax', fmt_num(EXTRA['psi'][k_][1], 2))
        k2 = 'w60c90_gaap' if c == 'C3' else 'w60c90_cash'
        put(f'Sc{T}PrimMin', fmt_num(EXTRA['psi'][k2][0], 2)); put(f'Sc{T}PrimMax', fmt_num(EXTRA['psi'][k2][1], 2))
    for e, nm in (('om25', 'OrderM'), ('c80', 'Eighty'), ('c90', 'Ninety')):
        put(f'ScDiffOp{nm}Med', fmt_sgn(LV('C5', 'estimator', e)['median'], 2, 1)); put(f'ScDiffOp{nm}Share', pct_share(LV('C5', 'estimator', e)['share']))
    put('ScDiffOpInvWindow', thousands(SUMM['C5']['invalid_by_dim']['window'].get('w60', 0)))
    CS6 = EXTRA['cash_steepening']
    put('ScDiffCashNegObs', pct_share(CS6['neg_share_observed'])); put('ScDiffCashNegOrg', pct_share(CS6['neg_share_organic']))
    put('ScDiffCashNegImp', pct_share(CS6['neg_share_imputed'])); put('ScDiffCashNegSplitB', pct_share(CS6['neg_share_split_B']))
    put('ScDiffCashNegSplitA', pct_share(CS6['neg_share_split_A']))
    if 'boot_below_zero_observed' in CS6:
        put('ScDiffCashBootNegObs', pct_share(CS6['boot_below_zero_observed'])); put('ScDiffCashBootNegOther', pct_share(CS6['boot_below_zero_other']))
        put('ScDiffCashBootNegSplitB', pct_share(CS6['boot_below_zero_split_B']))
    put('ScSpendShareAbove', pct_share(EXTRA['spend']['share_above'])); put('ScSpendShareNamed', pct_share(EXTRA['spend']['share_r2all']))
    put('ScSpendShareNotNamed', pct_share(EXTRA['spend']['share_not_r2all']))
    put('ScSpendObsMed', fmt_num(SUMM['C7']['by_family']['observed']['median'], 2)); put('ScSpendProMed', fmt_num(SUMM['C7']['by_family']['pro forma']['median'], 2))
    for cut, nm in ((0.9, 'Ninety'), (0.975, 'NinetySevenFive')):
        for c, T in (('C8a', 'AncLb'), ('C8b', 'AncNet'), ('C8c', 'AncUb')):
            put(f'Sc{T}Cut{nm}Med', fmt_sgn(LV(c, 'cutoff', str(cut))['median'], 1, 100))
    # forward pairing (four views) and its grid
    for vn, tg in (('E1', 'Eone'), ('E2', 'Etwo'), ('E2imp4', 'ImpFour'), ('E2imp8', 'ImpEight')):
        for kind, kt in (('F1', 'Fwd'), ('F1p', 'FwdNext'), ('F2', 'Lag')):
            h = FWD[vn][kind]
            for c, nm, nd, sc in (('C1', 'TopOp', 1, 100), ('C2', 'TopCash', 1, 100), ('C3', 'PsiOp', 2, 1), ('C4', 'PsiCash', 2, 1),
                                  ('C5', 'DiffOp', 2, 1), ('C6', 'DiffCash', 2, 1)):
                x = h[c]
                put(f'Sc{kt}{nm}{tg}', (fmt_sgn(x, nd, sc) if fin(x) else 'n.d.'))
            put(f'Sc{kt}N{tg}', thousands(FWD[vn]['n'][kind]))
            put(f'Sc{kt}Cell{tg}', str(int(FWD[vn]['cell60'][kind]['op'])))
        put(f'ScFwdLateN{tg}', str(FWD[vn]['n_by_period']['F1']['2023-25']))
    for c, T in (('C1', 'TopOp'), ('C2', 'TopCash'), ('C3', 'PsiOp'), ('C4', 'PsiCash'), ('C5', 'DiffOp'), ('C6', 'DiffCash')):
        r = FSUMM[c]
        sc, nd = CLAIMS[c]['scale'], CLAIMS[c]['nd']
        put(f'ScFG{T}N', thousands(r['n_valid'])); put(f'ScFG{T}Inv', thousands(r['n_invalid']))
        put(f'ScFG{T}Share', pct_share(r['share_a']))
        put(f'ScFG{T}Med', fmt_sgn(r['median'], nd, sc)); put(f'ScFG{T}Min', fmt_sgn(r['min'], nd, sc)); put(f'ScFG{T}Max', fmt_sgn(r['max'], nd, sc))
    put('ScFGPsiOpShareHalf', pct_share(FSUMM['C3']['share_c'])); put('ScFGPsiCashShareHalf', pct_share(FSUMM['C4']['share_c']))
    put('ScFGDiffCashShareNeg', pct_share(FSUMM['C6']['share_negative']))
    # leave one firm out
    LK = OrderedDict([('TopOp', ('P95|op|p95|2023_25', 1, 100)), ('TopCash', ('P95|cash|p95|2023_25', 1, 100)),
                      ('PsiOp', ('PSI|op|c90|w60', 2, 1)), ('PsiCash', ('PSI|cash|c90|w60', 2, 1)),
                      ('DiffOp', ('DIFF|op|c90|w40|A', 2, 1)), ('DiffCash', ('DIFF|cash|c90|w40|A', 2, 1)),
                      ('PhiOp', ('PHI60|op', 1, 100)), ('PhiCash', ('PHI60|cash', 1, 100))])
    for vn, tg in (('E1', 'Eone'), ('E2', 'Etwo'), ('E2imp4', 'ImpFour'), ('E2imp8', 'ImpEight')):
        L = LOFO[vn]
        for nm, (k_, nd, sc) in LK.items():
            put(f'ScLo{nm}{tg}Lo', fmt_sgn(L[k_]['min'], nd, sc) if nm.startswith(('Top', 'Diff')) else fmt_num(L[k_]['min'], nd, sc))
            put(f'ScLo{nm}{tg}Hi', fmt_sgn(L[k_]['max'], nd, sc) if nm.startswith(('Top', 'Diff')) else fmt_num(L[k_]['max'], nd, sc))
        put(f'ScLoCell{tg}Min', str(int(min(L['CELL60|op']['min'], L['CELL60|cash']['min']))))
        tl = 'drop' if vn == 'E1' else 'keep'
        for b, nm in (('lb', 'Lb'), ('net', 'Net'), ('ub', 'Ub')):
            k_ = f'ANC|{b}|0.95|{tl}'
            put(f'ScLoAnc{nm}{tg}Lo', fmt_sgn(L[k_]['min'], 1, 100)); put(f'ScLoAnc{nm}{tg}Hi', fmt_sgn(L[k_]['max'], 1, 100))
        put(f'ScLoReversals{tg}', str(sum(L[k_]['n_sign_reversals'] for k_ in ('P95|op|p95|2023_25', 'P95|cash|p95|2023_25', 'PSI|op|c90|w60',
                                                                            'PSI|cash|c90|w60', 'DIFF|op|c90|w40|A'))))
    put('ScLoDiffCashReversalsEtwo', str(LOFO['E2']['DIFF|cash|c90|w40|A']['n_sign_reversals']))
    put('ScLoDiffCashReversalsImpFour', str(LOFO['E2imp4']['DIFF|cash|c90|w40|A']['n_sign_reversals']))
    if 'boot' in EXTRA:
        EB = EXTRA['boot']
        put('ScTopOpBootCoreShare', pct_share(EB['top_op_core'])); put('ScTopCashBootCoreShare', pct_share(EB['top_cash_core']))
        put('ScTopOpBootPNinetyShare', pct_share(EB['top_op_p90'])); put('ScTopOpBootLastShare', pct_share(EB['top_op_2025']))
        put('ScTopCashBootLastShare', pct_share(EB['top_cash_2025']))
        put('ScDiffOpBootNinetyShare', pct_share(EB['diff_op_c90'])); put('ScDiffOpBootNinetySplitAShare', pct_share(EB['diff_op_c90_A']))
        put('ScDiffOpBootNinetySplitBShare', pct_share(EB['diff_op_c90_B']))
        put('ScAncNetBootCutShare', pct_share(EB['anc_net_cut95'])); put('ScAncNetBootObsDropShare', pct_share(EB['anc_net_obs_drop']))
        put('ScAncNetBootBaseLo', fmt_sgn(EB['baseline_ci90']['C8b'][0], 1, 100)); put('ScAncNetBootBaseHi', fmt_sgn(EB['baseline_ci90']['C8b'][1], 1, 100))
        put('ScPsiCashBootBaseHi', fmt_sgn(EB['baseline_ci90']['C4'][1], 2, 1))
    L = ['% Specification curve of the empirical claims (Supplement draft section supp:speccurve). Generated by code/spec_curve.py;',
         '% do not edit by hand. Pre-specification: notes/spec_curve/design.md; results: notes/spec_curve/results.json.',
         f'% Run {meta["run_utc"]}, git {head[:12]}.']
    L += [f'\\newcommand{{\\{k}}}{{{v}}}' for k, v in MC.items()]
    open(MAC_PATH, 'w').write('\n'.join(L) + '\n')
    log('wrote paper1/spec_macros.tex:', len(MC), 'macros')

    # ---- table
    def val(c, x):
        sc, nd = CLAIMS[c]['scale'], CLAIMS[c]['nd']
        return fmt_sgn(x, nd, sc) if (sc == 100 or c in ('C5', 'C6')) else fmt_num(x, nd, sc)

    def infl(c):
        r = SUMM[c]
        k_ = r['most_influential']
        return f"{TEX_DIM[k_]} ({fmt_num(r['influence'][k_]['range_of_medians'], CLAIMS[c]['nd'], CLAIMS[c]['scale'])})"

    def boot(c, key='share_interval_on_claimed_side'):
        r = SUMM[c].get('boot')
        return (pct_share(r[key]) + r'\%') if r and key in r else '--'

    TROWS = [
        ('C1', 'a', r'Top of the score fell, GAAP: change in P95 (P90) from 2016--19 below zero, points', 'share_a', None),
        ('C2', 'a', r'The same, FCF after SBC', 'share_a', None),
        ('C3', 'a', r'$\Psi$ slope, GAAP, above $-1$', 'share_a', 'share_interval_on_claimed_side'),
        ('C3', 'b', r'\quad below zero', 'share_b', 'share_interval_below_zero'),
        ('C3', 'c', r"\quad above $-0.5$ (our reading of ``well under a point'')", 'share_c', None),
        ('C4', 'a', r'$\Psi$ slope, FCF after SBC, above $-1$', 'share_a', 'share_interval_on_claimed_side'),
        ('C4', 'b', r'\quad below zero', 'share_b', 'share_interval_below_zero'),
        ('C4', 'c', r'\quad above $-0.5$', 'share_c', None),
        ('C5', 'a', r'GAAP frontier steepened: late minus early $\Psi$ slope below zero', 'share_a', None),
        ('C6', 'a', r'Cash frontier did not steepen: difference not negative (point) / interval not below zero', 'share_a', None),
        ('C7', 'a', r'Spend ratio between 3.0 and 3.5 (samples varied)', 'share_a', None),
        ('C7s', 'a', r'\quad benchmark growth also varied (secondary)', 'share_a', None),
        ('C8a', 'a', r'Anchor: median surplus $\Pi_{lb}$ above zero (no S\&M buys growth), points', 'share_a', None),
        ('C8b', 'a', r'\quad netted basis, $\Pi_{net}$, above zero', 'share_a', None),
        ('C8c', 'a', r'\quad all S\&M buys growth, $\Pi_{ub}$ (no claim; share above zero)', 'share_a', None)]
    TL = []
    for c, t, lab, sk, bk in TROWS:
        r = SUMM[c]
        first = t == 'a'
        specs = thousands(r['n_valid']) if first else ''
        base_ = val(c, r['baseline']) if first else ''
        med_ = val(c, r['median']) if first else ''
        rng_ = f"{val(c, r['min'])} to {val(c, r['max'])}" if first else ''
        inf_ = infl(c) if first else ''
        bt = boot(c, bk) if bk else (boot(c) if (first and c in BOOT_TEST) else '--')
        TL.append(f"{lab} & {specs} & {pct_share(r[sk])}\\% & {bt} & {base_} & {med_} & {rng_} & {inf_}\\\\")
    TAB = r"""\begin{table}[t]\centering\footnotesize\setlength{\tabcolsep}{3pt}
\caption{Specification curve of the empirical headline claims: in what share of the defensible analysis choices does each claim hold?}\label{tab:spec_curve}
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{4.9cm}rrrrr>{\raggedright\arraybackslash}p{2.0cm}>{\raggedright\arraybackslash}p{2.4cm}@{}}\toprule
 & & \multicolumn{2}{c}{Claim holds} & & & & \\\cmidrule(lr){3-4}
Claim (test) & Specifi\-cations & point & interval & Baseline & Median & Lowest to highest & Most influential choice (range of medians)\\\midrule
""" + '\n'.join(TL) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: """ + \
        f"{len(SAMPLES)} samples ({len(ACQ)} treatments of acquired growth, the R1, R2, R5 and debt-only sensitivities and two growth bounds, crossed), each with the claim's own options " + \
        r"""(Section~\ref{supp:speccurve}); a specification counts once. Specifications: those with a defined estimate (a frontier slope needs 30 firm-years at every grid point). Point: share in which the point estimate passes the test. Interval: share in which the 90\% firm-cluster percentile interval lies on the claimed side, on the specifications of """ + \
        f"{R['BOOT_K']} of the samples" + r""" (the """ + f"{len(PUB_SID)}" + r""" of Table~\ref{tab:robust} and a seeded random draw of the others), """ + f"{B_BOOT}" + r""" replications, firms drawn from E1. For the cash steepening the point column gives the share with a non-negative difference and the interval column the share whose interval does not lie below zero, the sense of the paper's claim. Baseline: the specification the paper prints. Most influential choice: the choice whose options' medians differ most, with that difference. Points for score changes and surpluses; slopes and the ratio as numbers. Generated by \texttt{code/spec\_curve.py}; every specification in \texttt{notes/spec\_curve/specs.csv.gz}.
\end{table}"""
    open(TAB_PATH, 'w').write(TAB + '\n')
    log('wrote sections/tables/tab_spec_curve.tex')
    make_figure(SP, SUMM)
    check_text_claims(SP, FP, SUMM, FSUMM, FWD, LOFO, EXTRA)
    return MC, EXTRA


def check_text_claims(SP, FP, SUMM, FSUMM, FWD, LOFO, EXTRA):
    """Each qualitative statement of sections/supp_spec_curve.tex, tested on this run's results. A rerun that no longer
    supports a sentence stops here and names it (set SC_CLAIMS_WARN_ONLY=1 to print the failures instead)."""
    D = EXTRA['decline']
    lofo_rev = lambda vn: sum(LOFO[vn][k]['n_sign_reversals'] for k in ('P95|op|p95|2023_25', 'P95|cash|p95|2023_25', 'PSI|op|c90|w60',
                                                                        'PSI|cash|c90|w60', 'DIFF|op|c90|w40|A'))
    fwd_e1 = [FWD['E1'][kind][c] for kind in ('F1', 'F1p', 'F2') for c in HEAD_KEYS]
    con_e1 = [FWD['E1']['contemporaneous'][c] for kind in ('F1', 'F1p', 'F2') for c in HEAD_KEYS]
    printed = lambda k: float(PRINTED[k].replace('$-$', '-').replace('$+$', ''))
    C = [
        ('decline: negative in every P95 specification on both bases', D['p95_share_gaap'] == 1 and D['p95_share_cash'] == 1),
        ('decline: every GAAP rise measures P90 to 2025 alone', D['gaap_fail_all_p90_2025'] and D['n_fail_gaap'] > 0),
        ('decline: cash negative in every specification', SUMM['C2']['share_a'] == 1),
        ('decline: the quantile moves the GAAP change most, the end period the cash change',
         SUMM['C1']['most_influential'] == 'quantile' and SUMM['C2']['most_influential'] == 'late'),
        ('decline: the baseline falls are among the largest (fewer than 15% of samples fall more)',
         D['core_share_below_baseline_gaap'] < 0.15 and D['core_share_below_baseline_cash'] < 0.15),
        ('psi: above -1 and below zero in every defined specification, both bases',
         all(SUMM[c][f'share_{t}'] == 1 for c in ('C3', 'C4') for t in ('a', 'b'))),
        ('psi: the baseline is at the flat end (fewer than 10% flatter)', EXTRA['C3']['share_above_baseline'] < 0.10 and EXTRA['C4']['share_above_baseline'] < 0.10),
        ('psi: the window moves the GAAP slope most', SUMM['C3']['most_influential'] == 'window'),
        ('psi: observed growth flatter than pro forma; dropping the 16 named firms steepens',
         SUMM['C3']['by_family']['observed']['median'] > SUMM['C3']['by_family']['pro forma']['median']
         and SUMM['C3']['influence']['r2']['levels']['all']['median'] < SUMM['C3']['influence']['r2']['levels']['none']['median']),
        ('steepening: the estimator moves the GAAP difference most; Psi_0.90 negative in every specification',
         SUMM['C5']['most_influential'] == 'estimator' and SUMM['C5']['influence']['estimator']['levels']['c90']['share'] == 1),
        ('steepening: GAAP negative in more than 95% of specifications', SUMM['C5']['share_a'] > 0.95),
        ('cash steepening: negative in most observed-growth and in a minority of organic specifications',
         EXTRA['cash_steepening']['neg_share_observed'] > 0.5 and EXTRA['cash_steepening']['neg_share_organic'] < 0.5),
        ('spend: above the range only in samples that remove acquired growth',
         bool((SP[(SP.claim == 'C7') & (SP.value >= 3.55)].family != 'observed').all()) and EXTRA['spend']['share_below'] == 0),
        ('anchor: Pi_lb and Pi_net positive in every specification; Pi_ub of either sign',
         SUMM['C8a']['share_a'] == 1 and SUMM['C8b']['share_a'] == 1 and 0 < SUMM['C8c']['share_a'] < 1),
        ('anchor: the cut-off moves each surplus most', all(SUMM[c]['most_influential'] == 'cutoff' for c in ('C8a', 'C8b', 'C8c'))),
        ('lofo: no single firm reverses a headline sign in any of the four views', all(lofo_rev(vn) == 0 for vn in FOUR)),
        ('lofo: dropping any firm leaves the E1 anchor Pi_ub within the paper\'s leave-one-firm range',
         fmt_sgn(LOFO['E1']['ANC|ub|0.95|drop']['min'], 1, 100) == PRINTED['AncLooLo'] and fmt_sgn(LOFO['E1']['ANC|ub|0.95|drop']['max'], 1, 100) == PRINTED['AncLooHi']),
        ('lofo: the cash difference under E2 changes sign when one firm is removed', LOFO['E2']['DIFF|cash|c90|w40|A']['n_sign_reversals'] > 0),
        ('forward: under E1 no pairing changes the sign of a baseline quantity', all(np.sign(a) == np.sign(b) for a, b in zip(fwd_e1, con_e1))),
        ('forward: the 0-60% slope is undefined under E2 and both imputation bounds with F1, defined under E1',
         fin(FWD['E1']['F1']['C3']) and not any(fin(FWD[vn]['F1']['C3']) for vn in ('E2', 'E2imp4', 'E2imp8'))),
        ('forward: grid slopes above -1 and below zero in every defined specification', all(FSUMM[c][f'share_{t}'] == 1 for c in ('C3', 'C4') for t in ('a', 'b'))),
        ('forward: no specification ending in 2025 is defined', bool((~fin(FP[(FP.claim.isin(['C1', 'C2'])) & (FP['late'] == '2025')].value)).all())),
        ('forward: E1 slopes steeper than contemporaneous', FWD['E1']['F1']['C3'] < FWD['E1']['contemporaneous']['C3'] and FWD['E1']['F1']['C4'] < FWD['E1']['contemporaneous']['C4']),
    ]
    boot = SUMM['C1'].get('boot')
    if boot:
        C += [('boot: every bootstrapped Psi interval lies above -1', SUMM['C3']['boot']['share_interval_on_claimed_side'] == 1
               and SUMM['C4']['boot']['share_interval_on_claimed_side'] == 1),
              ('boot: the Psi sign is not established in every specification', SUMM['C3']['boot']['share_interval_below_zero'] < 1
               or SUMM['C4']['boot']['share_interval_below_zero'] < 1),
              ('boot: Pi_lb interval above zero in every bootstrapped specification', SUMM['C8a']['boot']['share_interval_on_claimed_side'] == 1),
              ('boot: GAAP decline interval below zero in every bootstrapped sample at the paper\'s quantile and periods', EXTRA['boot']['top_op_core'] == 1),
              ('boot: decline intervals rarely below zero at P90 or to 2025 alone (under 20%)', EXTRA['boot']['top_op_p90'] < 0.2 and EXTRA['boot']['top_op_2025'] < 0.2),
              ('boot: an interval that excludes zero holds for the decline in fewer than half of the bootstrapped specifications, both bases',
               SUMM['C1']['boot']['share_interval_on_claimed_side'] < 0.5 and SUMM['C2']['boot']['share_interval_on_claimed_side'] < 0.5),
              ('boot: GAAP steepening interval below zero in fewer than half of the bootstrapped specifications', SUMM['C5']['boot']['share_interval_on_claimed_side'] < 0.5),
              ('boot: GAAP steepening with Psi_0.90: fewer than half with the paper\'s split, most with the other',
               EXTRA['boot']['diff_op_c90_A'] < 0.5 < EXTRA['boot']['diff_op_c90_B']),
              ('boot: netted anchor interval above zero in most specifications at the 95th-percentile cut-off, a minority with observed growth and the calibration rule',
               EXTRA['boot']['anc_net_cut95'] > 0.5 > EXTRA['boot']['anc_net_obs_drop']),
              ('boot: the netted baseline interval reaches zero here, within 2 points, and lies above zero in the paper',
               EXTRA['boot']['baseline_ci90']['C8b'][0] < 0 and abs(EXTRA['boot']['baseline_ci90']['C8b'][0]) < 0.02 and printed('AncPiNetEoneLo') > 0),
              ('boot: cash-steepening interval below zero in a minority of observed and almost no other specifications',
               EXTRA['cash_steepening']['boot_below_zero_observed'] < 0.5 and EXTRA['cash_steepening']['boot_below_zero_other'] < 0.02),
              ('boot: Psi intervals below zero in more than 95% of bootstrapped specifications on both bases',
               SUMM['C3']['boot']['share_interval_below_zero'] > 0.95 and SUMM['C4']['boot']['share_interval_below_zero'] > 0.95)]
    bad = [s for s, ok in C if not ok]
    for s in bad:
        log('TEXT CLAIM NOT SUPPORTED:', s)
    if bad and os.environ.get('SC_CLAIMS_WARN_ONLY') != '1':
        raise SystemExit(f'{len(bad)} statement(s) of the draft no longer supported')
    log(f'text claims: {len(C) - len(bad)}/{len(C)} supported')


def make_figure(SP, SUMM):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    from matplotlib.collections import LineCollection
    from matplotlib.gridspec import GridSpec
    available = {f.name for f in font_manager.fontManager.ttflist}
    family = next((f for f in ['Arial', 'Helvetica', 'Liberation Sans', 'Nimbus Sans', 'DejaVu Sans'] if f in available), 'sans-serif')
    plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': [family], 'font.size': 7.5, 'axes.labelsize': 7.5,
                         'xtick.labelsize': 6.5, 'ytick.labelsize': 6.5, 'legend.fontsize': 6.5, 'axes.linewidth': 0.6,
                         'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'axes.spines.top': False, 'axes.spines.right': False,
                         'pdf.fonttype': 42, 'ps.fonttype': 42, 'mathtext.fontset': 'custom', 'mathtext.rm': family,
                         'mathtext.it': f'{family}:italic', 'mathtext.bf': f'{family}:bold', 'savefig.bbox': 'tight',
                         'savefig.pad_inches': 0.03})
    BLACK, DARK, MID, LIGHT = '0.0', '0.25', '0.5', '0.85'
    # rows: every family of acquisition treatment; for every other choice only the options other than the paper's
    sample_rows = [
        ('Acquired growth', [('observed (E1)', lambda d: d.family == 'observed'), ('pro forma organic', lambda d: d.family == 'pro forma'),
                             ('acquisition years excluded', lambda d: d.family == 'exclusion'),
                             ('imputed ($M=4$ or $8$)', lambda d: d.family == 'imputed')]),
        ('Acquisition flag', [('10% of revenue', lambda d: d.acq.str.contains('10')), ('50% of revenue', lambda d: d.acq.str.contains('50'))]),
        ('Ambiguous pro forma', [('read additively', lambda d: d.acq.str.endswith('_add')), ('read cumulatively', lambda d: d.acq.str.endswith('_max'))]),
        ('Sample rules', [('fiscal-2010 years added (R1)', lambda d: d.r1 == 'yes'), ('R2 classifier firms dropped', lambda d: d.r2 == 'cls'),
                          ('all 16 named firms dropped', lambda d: d.r2 == 'all'), ('R5 firm-years dropped', lambda d: d.r5 == 'drop'),
                          ('debt-only filers dropped', lambda d: d.debt == 'drop'), ('growth at most 150%', lambda d: d.trim == 'g<=1.5')])]
    claim_rows = {
        'C1': [('Quantile', [('P90 (not P95)', lambda d: d['quantile'] == 'p90')]),
               ('End period', [('2023-24', lambda d: d['late'] == '2023_24'), ('2025', lambda d: d['late'] == '2025')])],
        'C3': [('Frontier', [(r'$\Psi_{0.80}$', lambda d: d['estimator'] == 'c80'), (r'$\Psi_{0.85}$', lambda d: d['estimator'] == 'c85'),
                             (r'$\Psi_{0.95}$', lambda d: d['estimator'] == 'c95'), ('order-$m$, $m=25$', lambda d: d['estimator'] == 'om25')]),
               ('Growth window', [('0-40% (not 0-60%)', lambda d: d['window'] == 'w40')])]}
    panels = [('C1', 'a', 100, 'Change (points)', [0.0]), ('C3', 'a', 1, r'Slope of $\Psi$', [0.0, -1.0])]
    nrow = [sum(len(g[1]) for g in sample_rows + claim_rows[c]) for c, *_ in panels]
    fig = plt.figure(figsize=(6.5, 8.3))
    gs = GridSpec(5, 1, height_ratios=[1.3, 0.128 * nrow[0], 0.5, 1.3, 0.128 * nrow[1]], hspace=0.06, figure=fig)
    for pi, (c, tcol, sc, ylab, hlines) in enumerate(panels):
        d = SP[(SP.claim == c) & fin(SP.value)].copy()
        d = d.sort_values('value', kind='stable').reset_index(drop=True)
        x = np.arange(len(d))
        y = d.value.values * sc
        holds = d[f'holds_{tcol}'].values == 1
        if c == 'C3':
            holds = d.holds_b.values == 1                           # sign test shaded; all lie above -1
        ax = fig.add_subplot(gs[3 * pi])
        bt = d.boot_ok.values
        if bt.any():
            segs = [((xi, lo * sc), (xi, hi * sc)) for xi, lo, hi in zip(x[bt], d.boot_lo.values[bt], d.boot_hi.values[bt])]
            ax.add_collection(LineCollection(segs, colors='0.88', linewidths=0.25, rasterized=True, zorder=1))
        ax.scatter(x[holds], y[holds], s=0.8, c=BLACK, linewidths=0, rasterized=True, zorder=3)
        ax.scatter(x[~holds], y[~holds], s=0.8, c=MID, linewidths=0, rasterized=True, zorder=3)
        ib = np.nonzero(d.baseline.values)[0][0]
        ax.plot([x[ib]], [y[ib]], marker='o', ms=5, mfc='white', mec=BLACK, mew=1.0, zorder=5, ls='none')
        left = ib > 0.6 * len(d)
        ax.annotate('Paper\'s baseline', xy=(x[ib], y[ib]), xytext=(x[ib] + (-0.2 if left else 0.06) * len(d), y[ib] + (0.35 if left else -0.25) * (np.nanmax(y) - np.nanmin(y))),
                    fontsize=6.5, ha='right' if left else 'left', arrowprops=dict(arrowstyle='-', lw=0.5, color=DARK, shrinkA=0, shrinkB=3))
        lo_y = min(np.nanmin(y), np.nanmin(d.boot_lo.values[bt] * sc) if bt.any() else np.inf)
        hi_y = max(np.nanmax(y), np.nanmax(d.boot_hi.values[bt] * sc) if bt.any() else -np.inf)
        pad = 0.05 * (hi_y - lo_y)
        ax.set_ylim(lo_y - pad, hi_y + pad)
        for h in hlines:
            if lo_y - pad <= h <= hi_y + pad:
                ax.axhline(h, color=MID, lw=0.6, ls=(0, (3, 2)), zorder=2)
        if c == 'C3' and lo_y - pad > -1:
            ax.text(0.01, 0.04, r'All specifications and intervals lie above $-1$ (the Rule-of-40 line)', transform=ax.transAxes, fontsize=6.3, color=DARK)
        ax.set_xlim(-0.005 * len(d), 1.005 * len(d))
        ax.set_xticks([])
        ax.set_ylabel(ylab, fontsize=6.8)
        ttl = ('A. Change in the upper quantile of the GAAP score, 2016-19 to end period: ' if c == 'C1'
               else r'B. Slope of the partial frontier $\Psi$ over growth, GAAP: ') + f'{len(d):,} specifications'
        ax.set_title(ttl, fontsize=7.5, loc='left', pad=3)
        # dashboard
        axd = fig.add_subplot(gs[3 * pi + 1])
        groups = sample_rows + claim_rows[c]
        mats, labels, gpos = [], [], []
        r0 = 0
        for gname, levs in groups:
            gpos.append((gname, r0, r0 + len(levs) - 1))
            for lab, f in levs:
                mats.append(np.asarray(f(d), bool).astype(float))
                labels.append(lab)
                r0 += 1
        Mx = np.vstack(mats)
        axd.imshow(Mx, aspect='auto', cmap='Greys', vmin=0, vmax=1.25, interpolation='nearest',
                   extent=(-0.5, len(d) - 0.5, len(labels) - 0.5, -0.5))
        axd.set_xlim(-0.005 * len(d), 1.005 * len(d))
        axd.set_yticks(range(len(labels)))
        axd.set_yticklabels(labels, fontsize=6.4)
        axd.tick_params(axis='y', length=0, pad=2)
        axd.set_xticks([])
        for sp_ in axd.spines.values():
            sp_.set_visible(False)
        for gname, a, b in gpos:
            if a > 0:
                axd.axhline(a - 0.5, color=MID, lw=0.4)
            axd.text(-0.27, (a + b) / 2, gname, transform=axd.get_yaxis_transform(), ha='right', va='center', fontsize=6.4, fontweight='bold')
        axd.set_xlabel('Specifications, sorted by the estimate; filled cells mark the options of each specification', fontsize=6.5, labelpad=2)
    fig.savefig(FIG_PATH, dpi=300, metadata={'CreationDate': None, 'ModDate': None})
    plt.close(fig)
    log('wrote figures/fig_spec_curve.pdf')


if __name__ == '__main__':
    import pickle
    import tempfile
    CACHE = os.environ.get('SC_CACHE', os.path.join(tempfile.gettempdir(), 'spec_curve_cache.pkl'))   # outside the repository
    if os.environ.get('SC_FROM_CACHE') == '1':                      # rewrite the outputs from the last run's results
        R = pickle.load(open(CACHE, 'rb'))
        log('outputs from the cached results of the last full run')
    else:
        R = main()
        pickle.dump(R, open(CACHE, 'wb'))
        log('runtime', f"{R['RUNTIME']:.0f}s")
    write_outputs(R)
