"""Calibrate the maximal Rule-of-40 score by horizon (fourth revision: full cost, capacity, risk and transition dips).

Model: R* = R_inf + Pi with R_inf = m0 + (1-k) G (durable part) and Pi the transient growth surplus, X = 1,
free-cash-flow-after-SBC basis (Proposition score, Remark taxes). A firm still transforming at the horizon scores
lower by the in-flight dip d (Propositions tasks-scorepath and ext-waves(f)), which is reported separately.

Anchor (revision v2 of Paper 1, decision D-3: the E1 calibration rule is central, read from
notes/calibration_anchor_v3.json, the audited sample of code/estimate_v3.py; the all-tail E1, the organic E2 and the two
imputation bounds are sensitivity rows; set P1_V3_DIR to read a pinned snapshot of the v3 outputs). The data identify neither alpha nor lambda*h (Section 5), and a single
cross-firm intercept is infeasible for firms whose margins exceed it. We therefore invert the model firm by firm for the
top tail of 2023-25: firm-years at or above the 95th percentile of the cash-basis score, excluding acquisition-affected
firm-years (purchased growth is not the growth the model describes). On the after-tax cash basis, m = m0 - (1-tau) sigma
- k g (Remark taxes with psi = 0: growth spend is deductible, growth capital is not), so m0 = m + (1-tau) sigma + k g.
Growth spend sigma is bounded: the selling-and-marketing share is an upper bound (all S&M buys growth) and zero a lower
bound (none does). A firm-year that does not report S&M is treated as having none. Then R_inf = m0 + (1-k) G and
Pi = R - R_inf.

Horizons (new in this revision). The margin intercept is no longer a scenario range. It moves from the anchor toward the
full-cost margin term of Corollary ceiling (Table tab:ceiling, Appendix tab:fullcost) at the pace that the attainable and
expected frontiers allow (Propositions attainable and expected):
  m0(h) = m0_A + s(h) [m0_F - m0_A],
  s(h)  = bbar * min{1, q rho T_par n(t_R)},  t_R = (h - 2025)/(1 + nu_R T_frz),
  n(t)  = floor((t - T_emb)/T_par) + 1 for t >= T_emb (waves embedded by t),
  q     = varpi (params commit of 29 Oct 2026: varpi and bbar come from outcome surveys, which already include
          disruptions, so the haircut exp(-nu_D T_emb), nu_D = nu_L (1 - kappa_keep) + nu_V, is not applied; nu_D is
          kept for the shock-timing results),
  rho   = min{change capacity, decision capacity, security-review capacity}, as shares of the program a year.
The full-cost margin term m0_F is horizon-specific (compute share c_c by horizon, CC below), and pass-through phi is a
scenario dimension (PHI below; phi = 0 is the fixed-prices case of Table tab:calib).
The high end of each range pairs the anchor's upper quartile with the favorable full-cost term and the fast pace; the
low end pairs the lower quartile with the central full-cost term and the central pace (an exceptional firm executes at
least as well as a typical one). The dip of a firm still transforming at h is d = a_r T_pb [m0_F - m0_A], with attempt
rate a_r = rho/(1 + nu_R T_frz) and one-time plus parallel-run costs of T_pb years of the savings attempted, as long as
the program has not been completed (expected embedded share below one).
  Pi scales the 2025 interquartile range by mu^(1/(1-alpha)) (demand pull relative to 2025) and by (1-k)^(1/(1-alpha)).
The lower-bound case shifts every m0 down by the anchor's median difference between the two bounds and scales the
lower-bound Pi, as in the third revision. Regime variants: a public firm that holds to a guided dip (Proposition
reg-dip), and a sponsor's faster decisions where decision bandwidth binds (Proposition reg-speed(c)).
The third-revision ranges (fixed m0 scenarios 40-62, 45-65, 50-69) are recomputed and stored under 'previous' so the
memo can report old and new numbers side by side.

Tax deductions for capital (Remark taxes; Part II Proposition acct-tax). The table keeps psi = 0 (capital not
deductible), which suits working capital and is a lower bound. Under current U.S. law domestic research and experimental
expenditure, including software development, is deducted when incurred (26 U.S.C. 174A, tax years beginning after
31 Dec 2024) and equipment acquired after 19 Jan 2025 takes the 100% allowance (IRS Notice 2026-11), so psi = 1; foreign
research is amortized over 15 years from the midpoint (26 U.S.C. 174), psi_15 = 0.532 at r = 0.10; the 2022-2024
five-year regime had psi_5 = 0.796. Block 'psi_sensitivity' reports the anchor intercepts, the k = 0.5 column and the
capital term of the ceiling under each.
"""
import json
import math
import os
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # replication-package root
V3DIR = os.environ.get('P1_V3_DIR')                  # pinned snapshot of the v3 outputs (see code/paper1_macros.py)


def v3path(kind, name):
    return os.path.join(V3DIR, name) if V3DIR else os.path.join(BASE, kind, name)


TAU = 0.18                                          # central cash tax rate, Table ceiling


def psi_T(T, r=0.10):
    """PV per dollar of deductions taken ratably over T years from the midpoint of the first year (Prop. acct-tax(a))."""
    return (1 + (1 + r) ** (-T)) / (2 * T) + (1 - (1 + r) ** (-(T - 1))) / (r * T)


PSI = {'none': 0.0, 'foreign_15y': psi_T(15), 'prior_5y': psi_T(5), 'domestic': 1.0}
ALPHAS = [0.25, 0.45]
H0 = 2025                                           # end of the anchor period; the program starts after it

# ----------------------------------------------------------------------------------------------
# Full-cost margin terms (Corollary ceiling, Definition fullcost). The inputs duplicate those of
# code/verify_theory.py section 20, which checks that this script's JSON reproduces them.
# ----------------------------------------------------------------------------------------------
S_REF = 1e9                                         # reference revenue for fixed and per-process costs, $
WAGE_GOV = 88400 * (1 + 0.4287)                     # compliance officer (SOC 13-1041) mean wage, OEWS May 2025, loaded (ECEC)

# ----------------------------------------------------------------------------------------------
# Compute share at full automation, by horizon (params commit of 29 Oct 2026; notes/assumptions_round2.md Section 2).
# The same values are in data/tasks/params.yaml part1_ceiling.c_c_compute_share (engine tests/test_regression.py checks
# that they agree). c_c(H) = s_L x kappa(H): s_L the labor cost the ceiling automates (share of revenue), kappa the
# compute cost per dollar of labor replaced (retries, verification, orchestration; human review is priced in a_min and
# the full-cost floors). Explicit path:
#   kappa(H) = omega_H kappa_front + (1 - omega_H) kappa_fixed(H),  kappa_fixed(H) = max(kappa_2025 / D^(H - 2025),
#              floor_share kappa_2025),
# with s_L 0.60 [0.50, 0.65] (c), kappa_2025 0.10 [0.01, 0.35] (b: METR run costs, Stevens 2026, AI-native products),
# D = 5 [3, 10] a year (a: Gundlach et al. 2026), kappa_front 0.33 [0.10, 0.50] (d, capped by the value test kappa < 1),
# omega_H the share of automated labor cost in tasks reached within two years of H (d), floor_share 0.005 (d).
# Values (value, credible bounds, class): sources read 29 Oct 2026.
# ----------------------------------------------------------------------------------------------
CC_PATH = dict(s_L=0.60, kappa_2025=0.10, D=5.0, floor_share=0.005, kappa_front=0.33,
               omega={'2028': 0.6, '2031': 0.4, '2036': 0.25})


def cc_path(h):
    """c_c of the explicit path for horizon h ('2028', '2031', '2036'), or at 2025 prices for h = 'prices2025'."""
    c = CC_PATH
    if h == 'prices2025':
        return c['s_L'] * c['kappa_2025']
    om = c['omega'][h]
    k_fixed = max(c['kappa_2025'] / c['D'] ** (int(h) - H0_PRICES), c['floor_share'] * c['kappa_2025'])
    return c['s_L'] * (om * c['kappa_front'] + (1 - om) * k_fixed)


H0_PRICES = 2025
CC = {'prices2025': (0.06, (0.01, 0.20), 'b'),       # 2025 prices, no price path (b-anchored); the static ceiling
      '2028': (0.12, (0.02, 0.30), 'd'), '2031': (0.08, (0.01, 0.25), 'd'), '2036': (0.05, (0.01, 0.20), 'd')}
assert all(abs(cc_path(h) - v[0]) < 0.005 for h, v in CC.items()), 'compute-share path and CC centrals disagree'
# Cases. c_c is a class d composite at every horizon (and b-anchored only at 2025 prices), so by the rule below the
# favorable and conservative cases take the central value halved and doubled; the credible bounds above are the
# scenario bounds of the sensitivity (cc_sensitivity). The 0.40 high-compute case of earlier drafts exceeds the
# value-test cap s_L x 0.5 = 0.30, so it is kept only for comparison and labelled infeasible at full automation.
CC_CASES = {h: (v[0] / 2, v[0], 2 * v[0]) for h, v in CC.items()}
CC_HIGH = 0.40
# Value test (round 2, B2 / IO2-3): a task is automated only while its compute costs less than the labor it replaces,
# kappa < 1, so c_c <= s_L. Earlier drafts capped c_c at s_L x 0.5, a factor the assumptions memo attributed to
# "1 - review share"; the full-automation ceiling has no human review (Lemma fullcost(c)) and no source documents the
# half, so the stated test is used. The old cap 0.30 is kept as a reference point (CC_OLD_CAP) in cc_sensitivity.
CC_VALUE_TEST_FACTOR = 1.0
CC_VALUE_TEST_CAP = CC_PATH['s_L'] * CC_VALUE_TEST_FACTOR
CC_OLD_CAP = CC_PATH['s_L'] * 0.5

FC = {  # favorable, central, conservative; c_c by horizon is in CC_CASES; the high-compute case uses central values
    # Rules (Appendix Table tab:fullcost): factors with a sourced or precedent range (classes a to c in
    # notes/assumptions_register.md) take its low end, central value and high end; scenario (class d) composites take a
    # central value from the stated structure, halved and doubled.
    'c_c': CC_CASES['prices2025'], 'f': (0.02, 0.025, 0.03), 'tau': (0.15, 0.18, 0.21),
    'a_min': (0.015, 0.03, 0.046),                  # register band [0.005, 0.046] (b); the third revision used 6%
    # c_sec: risk cost of Proposition tasks-security(b) scaled from today's spend, plus PQC and AI compliance
    's0': (0.0069, 0.0069, 0.0069),                 # security spend, share of revenue (IANS 2025; a, flagged)
    'L0': (4.0, 2.0, 1.0),                          # ln(C_inc/C_s): controls remove 98, 86, 63% of expected loss (d)
    'Me': (1.0, 2.0, 3.0),                          # exposure multiplier at full automation (params autonomy multipliers, d)
    # security share of IT spend, IANS 2025 benchmark (published 5 Aug 2025, page read 2 Nov 2026): 10.9% in 2025 (central;
    # was 0.099, a value the cited source does not contain, IO2-N19), 11.9% in 2024 (favorable), 8.6% in 2020 (conservative)
    'sec_it': (0.119, 0.109, 0.086),
    'phi_pqc': (0.0075, 0.015, 0.03),               # PQC migration a year, share of IT spend (d)
    'aic_fixed': (12e3 + 10e3 + 2.5e3 + (5e3 + 13e3) / 3 + 0.10 * WAGE_GOV,
                  30e3 + 35e3 + 6e3 + (13.5e3 + 30e3) / 3 + 0.25 * WAGE_GOV,
                  150e3 + 60e3 + 9e3 + (20e3 + 50e3) / 3 + 1.00 * WAGE_GOV),   # SOC 2, ISO 42001, NIST AI RMF ($/yr)
    'aic_pp': (0.5, 1.0, 2.0),                      # factor on 48 processes x ($30k red team + $10k PIA / T_up) (d)
    # c_mnt: (delta_M + kappa_reval / T_up) x build stock per revenue
    'delta_M': (0.10, 0.17, 0.40),                  # register: 0.17 [0.10, 0.40] (b)
    'kappa_rv': (0.05, 0.10, 0.20),                 # d
    'T_up': (1.75, 1.22, 0.99),                     # c: median GA model life from 2025; 0.99 = shortest observed
    'B': (0.012, 0.024, 0.048),                     # 48 processes x $0.5M (b) at $1B revenue (d)
    # c_err = errors and hallucination + misbehavior (Proposition tasks-cerr) + common-mode (Proposition ext-commonmode(a));
    # rates from data/tasks/params_reliability.yaml (a, b), loss severities and exposure scenario (d); the no-review rate
    # u_rev below adds rates with different denominators, so as used it is a scenario value, class d (round 3, GPT-21)
    # in-house cost of the automated work, share of revenue (round 2, B4 / IO2-6): the same base as the compute share,
    # s_L = 0.60 of revenue in automated labor (CC_PATH); earlier drafts charged errors on 0.30 with no stated reason
    'A_auto': (0.60, 0.60, 0.60),
    # no review at full automation (Lemma fullcost(c), FI-5): the measured catch rates are those of human reviewers, so
    # the ceiling uses the no-review rate e_o + e_h; AI review would lower it at most to chi(e_o + e_h), with its
    # compute in c_c. Omission 0.0345 in every case; hallucination 0.015 (favorable) and 0.05 (central, conservative:
    # worse rates fail the scope test of Lemma fullcost(c))
    'u_rev': (0.0345 + 0.015, 0.0345 + 0.05, 0.0345 + 0.05),
    'ell_e': (0.25, 0.5, 1.0),                      # loss per undetected error, multiple of the unit's in-house cost (d)
    'mu_m': (0.0005, 0.001, 0.002),                 # consequential misbehavior per task (d; file range 5e-5 to 1e-2)
    'd_m': (0.95, 0.60, 0.42),                      # monitor recall (a)
    'ell_m': (10.0, 10.0, 10.0),                    # loss scale per event, multiple of the unit's in-house cost (d)
    'p_tail': (2.3, 1.5, 1.15), 'Zcap': (100.0, 100.0, 100.0),   # Pareto tail index (b); least-privilege cap (d)
    'nu_cm': (0.5, 2.0, 6.0),                       # provider day-equivalent incidents a year (b)
    'XY': (1.0, 1.0, 1.0),                          # exposure X = A_auto, X/(2 Y_f) = 1, single provider H = 1 (d)
    # c_anc: management of AI spend (FinOps, which for API spend also covers vendor management) and fixed costs
    's_fin': (0.015, 0.03, 0.06),                   # d
    'anc_fixed': (62.5e3, 125e3, 250e3),            # incident-response retainer and legal review of 5 AI vendors (d)
}


def fullcost(case, h='prices2025'):
    """Full-cost floors and the ceiling's margin term for a case at horizon h (compute share CC_CASES[h])."""
    i = {'favorable': 0, 'central': 1, 'conservative': 2, 'high compute': 1}[case]
    v = {k: val[i] for k, val in FC.items()}
    v['c_c'] = CC_CASES[h][i]
    if case == 'high compute':
        v['c_c'] = CC_HIGH
    risk = v['s0'] / v['L0'] * (1 + v['L0'] + math.log(v['Me']))
    pqc = v['phi_pqc'] * v['s0'] / v['sec_it']
    aic = (v['aic_fixed'] + v['aic_pp'] * 48 * (30e3 + 10e3 / 1.22)) / S_REF
    c_sec = risk + pqc + aic
    c_mnt = (v['delta_M'] + v['kappa_rv'] / v['T_up']) * v['B']
    Emin = 1 + (1 - v['Zcap'] ** (1 - v['p_tail'])) / (v['p_tail'] - 1)
    c_err_e = v['A_auto'] * v['u_rev'] * v['ell_e']
    c_err_m = v['A_auto'] * v['mu_m'] * (1 - v['d_m']) * v['ell_m'] * Emin
    c_err_cm = v['nu_cm'] / 365 * v['A_auto'] * (1 + v['XY'])
    c_err = c_err_e + c_err_m + c_err_cm
    c_anc = v['s_fin'] * v['c_c'] + v['anc_fixed'] / S_REF
    c_full = c_mnt + c_sec + c_err + c_anc
    base = (1 - v['tau']) * (1 - v['c_c'] - v['f'] - v['a_min'] - c_full)
    base_acc = (1 - v['tau']) * (1 - v['c_c'] - v['f'] - v['a_min'])
    out = dict(c_c=v['c_c'], f=v['f'], a_min=v['a_min'], tau=v['tau'], risk=risk, pqc=pqc, aic=aic, c_sec=c_sec,
               c_mnt=c_mnt, c_err=c_err, c_err_e=c_err_e, c_err_m=c_err_m, c_err_cm=c_err_cm, c_anc=c_anc,
               c_full=c_full, base=base, base_acc=base_acc, G100=1 - base, G100_acc=1 - base_acc, horizon=h)
    if case == 'high compute':
        out.update(feasible_at_full_automation=CC_HIGH <= CC_VALUE_TEST_CAP, value_test_cap=CC_VALUE_TEST_CAP)
    return out


CASES = ['favorable', 'central', 'conservative', 'high compute']
CEIL = {c: fullcost(c) for c in CASES}               # static ceiling (Table tab:ceiling) at 2025 prices
CEIL_H = {h: {c: fullcost(c, h) for c in CASES} for h in ['2028', '2031', '2036']}   # by horizon (price path)
M0_FAV = {h: CEIL_H[h]['favorable']['base'] for h in CEIL_H}   # favorable full-cost margin term, by horizon
M0_CEN = {h: CEIL_H[h]['central']['base'] for h in CEIL_H}     # central full-cost margin term, by horizon
M0_CAP_OLD = (1 - 0.15) * (1 - 0.15 - 0.02 - 0.015) # third revision: favorable accountability-only margin term

# ----------------------------------------------------------------------------------------------
# Pass-through (params commit of 29 Oct 2026; notes/assumptions_round2.md Section 4). Scenario dimension phi, the
# industry pass-through of variable-cost savings (c_h and c_c; the non-discretionary cost a is not passed through),
# entering through the competition result of the companion paper and the engine: the firm keeps
# dur = 1 - phi (1 - HHI) of a saving every rival makes (theory_competition.tex eq:ext-game-dur; engine
# formulas.game_shares). phi = 0 is the fixed-prices case, reported beside the others. Anchors (b, read 29 Oct 2026):
# 0 to 0.1 for differentiated software in the short run (Apple/Analysis Group DMA study, 2025), 0.7 for an
# industry-wide cost shock (Ganapati, Shapiro and Walker 2020), 0.5 the central medium-run case. HHI = 0.25 is the
# engine's competition.hhi (four symmetric incumbents; class d). The saving passed through is today's non-fee unit
# cost of revenue of the median core firm in 2023-25, U0 = 1 - gamma0 - f, less the compute share that replaces it.
# ----------------------------------------------------------------------------------------------
PHI = (0.0, 0.5, 0.7)
HHI = 0.25


def dur(phi, hhi=HHI):
    return 1.0 - phi * (1.0 - hhi)

# ----------------------------------------------------------------------------------------------
# Pace and risk (Assumption program, Definition attainable(b), Proposition expected(c)). Values adopted by the params
# commit of 29 Oct 2026 (notes/assumptions_round2.md Sections 1.1 to 1.6; the same values are in data/tasks/params.yaml
# project_outcomes and change_capacity); sources read 29 Oct 2026:
#   change capacity kappa_abs 0.10 [0.05, 0.22] (b: WEF Future of Jobs 2025, about 12% of workers' work changes a year;
#     one-year reductions in filings 6 to 22%, Meta 2023 the high end; JOLTS layoffs 1% a month);
#   varpi, the probability that a funded transition creates value: 0.70 [0.54, 0.80] (b: BCG 2020, 30% win + 44% worry
#     zone = 74% created value, rounded down for self-report; low end S&P Global pilot attrition 0.54, high end BCG's
#     six-factor rate 0.80);
#   bbar, the share of targeted value realized: 0.67 [0.37, 0.85] (a, flagged: McKinsey 2021, n = 1,034, successful
#     transformations 67%, all others 37%, top quartile the high end);
#   T_emb = T_pb, the payback date including the parallel run: 1.25 [1, 2] years (b: Salesforce workforce actions
#     substantially complete about 13 months after announcement; McKinsey half of value within 18 months);
#   q = varpi, without the disruption haircut exp(-nu_D T_emb): varpi and bbar come from outcome surveys, which already
#     include leadership changes and strategy shifts, so the haircut would count them twice (it took q from 0.54 to 0.34).
#     nu_D = nu_L (1 - kappa_keep) + nu_V is kept and reported for the shock-timing results (Proposition ext-shocks):
#     nu_L sponsor hazard 0.204 [0.15, 0.30] (Korn Ferry C-suite tenure; practitioner data); kappa_keep 0.60 [0.30, 0.85]
#     (d), nu_V 0.15 [0.05, 0.30] (d);
#   nu_R 0.46 [0.30, 0.60] (b, flagged), T_frz 0.25 [0.08, 1.0] (b, flagged); T_par 0.17 [0.08, 0.42] (b: AI shadow mode
#     up to about five months); concurrent initiatives Phi 5 [3, 10] and decision units e 1 [0.5, 2] (d); load
#     breakpoints 0.70 and 0.78 for latency factors 1.0 and 0.5 (Proposition reg-speed(c)); security reviews 10 [5, 20]
#     per reviewer-quarter (d), two reviewers.
# The fast case takes the favorable end of every range and the slow case the unfavorable end. The central path is
# "AI migration only": the revealed pace of cost programs (REVEALED_PACE below) is reported beside it, not added to it.
# Set 'haircut': True in a case to restore q = varpi exp(-nu_D T_emb) (for inputs that are not outcome-survey based).
# ----------------------------------------------------------------------------------------------
N_PROC = 48
PACE = {
    'fast':    dict(kappa_abs=0.22, varpi=0.80, bbar=0.85, nuL=0.15, kkeep=0.85, nuV=0.05, nuR=0.30, Tfrz=0.08,
                    Tpar=0.08, Temb=1.0, Tpb=1.0, Phi=10, e=0.5, kap=0.70, sec=20 * 4 * 2, haircut=False),
    'central': dict(kappa_abs=0.10, varpi=0.70, bbar=0.67, nuL=0.204, kkeep=0.60, nuV=0.15, nuR=0.46, Tfrz=0.25,
                    Tpar=0.17, Temb=1.25, Tpb=1.25, Phi=5, e=1.0, kap=0.70, sec=10 * 4 * 2, haircut=False),
    'slow':    dict(kappa_abs=0.05, varpi=0.54, bbar=0.37, nuL=0.30, kkeep=0.30, nuV=0.30, nuR=0.60, Tfrz=1.00,
                    Tpar=0.42, Temb=2.0, Tpb=2.0, Phi=3, e=2.0, kap=0.70, sec=5 * 4 * 2, haircut=False),
}
# Values before the params commit (third and fourth revisions), recomputed under 'pace_previous' for comparison only
PACE_PREVIOUS = {
    'fast':    dict(PACE['fast'], kappa_abs=0.20, varpi=0.80, bbar=1.00, Temb=1.0, Tpb=1.0, haircut=True),
    'central': dict(PACE['central'], kappa_abs=0.10, varpi=0.54, bbar=0.85, Temb=2.0, Tpb=2.0, haircut=True),
    'slow':    dict(PACE['slow'], kappa_abs=0.05, varpi=0.30, bbar=0.50, Temb=3.0, Tpb=3.0, haircut=True),
}
# Revealed pace of cost programs (class c reference, not a model input; assumptions round 2 Section 1.5): own calculation
# on data/panel_v2_all.csv, SIC 7372, FY2022 revenue >= $100M, change FY2022 to FY2024, percentage points. Flag: to
# recompute on panel_v3 (computed on panel_v2, which the IM-1 sample audit is rebuilding).
REVEALED_PACE = dict(
    grounding='c', flag='to recompute on panel_v3', basis='data/panel_v2_all.csv, SIC 7372, FY2022 revenue >= $100M, FY2022-FY2024',
    gaap_op_margin=dict(n=149, p10=-7.8, p25=2.1, median=7.5, p75=21.5, p90=36.0),
    fcf_sbc_margin=dict(n=145, p10=-6.3, p25=1.3, median=9.5, p75=23.5, p90=35.4),
    gm_less_ga=dict(n=129, p10=-2.8, p25=0.4, median=3.8, p75=8.0, p90=13.0),
    spend_shares_median=dict(sm=-3.7, rd=-1.2, ga=-1.5, sbc=-0.9))
YEARS = [2028, 2031, 2036]


def rates(p, kap=None):
    kap = p['kap'] if kap is None else kap
    rho_chg = p['kappa_abs']
    rho_dec = kap * p['Phi'] / (N_PROC * p['e'] * p['Tpar'])
    rho_sec = p['sec'] / N_PROC
    rho = min(rho_chg, rho_dec, rho_sec)
    binding = ['change', 'decision', 'security'][int(np.argmin([rho_chg, rho_dec, rho_sec]))]
    nuD = p['nuL'] * (1 - p['kkeep']) + p['nuV']
    slow = 1 + p['nuR'] * p['Tfrz']
    # survival of a flight that lasts (1 + nu_R T_frz) T_emb in calendar time (Definition attainable(b)); applied only
    # when 'haircut' is set (outcome-survey rates already include disruptions)
    surv = math.exp(-nuD * slow * p['Temb'])
    q = p['varpi'] * (surv if p.get('haircut', False) else 1.0)
    return dict(rho=rho, binding=binding, rho_chg=rho_chg, rho_dec=rho_dec, rho_sec=rho_sec, nuD=nuD, q=q,
                q_with_dilated_haircut=p['varpi'] * surv, disruption_haircut_applied=bool(p.get('haircut', False)),
                clock=slow, eff_rate=q * rho / slow, eff_rate_realized=p['bbar'] * q * rho / slow, attempt_rate=rho / slow)


def _dM_at(dM, h):
    """dM is one number, or a dict {horizon year: dM} (the full-cost margin term moves with the compute share)."""
    return dM[h] if isinstance(dM, dict) else dM


def pace(p, dM, kap=None):
    """Waves of Assumption program: expected embedded share s (Proposition expected(c), greedy plan) and the in-flight
    dip by horizon. Waves of length T_par in program time t_R = t/(1 + nu_R T_frz); n(t_R) waves embedded by t."""
    out = rates(p, kap)
    for h in YEARS:
        tR = (h - H0) / out['clock']
        n = 0 if tR < p['Temb'] else math.floor((tR - p['Temb']) / p['Tpar'] + 1e-12) + 1
        raw = out['q'] * out['rho'] * p['Tpar'] * n
        done = raw >= 1
        out[h] = dict(n=n, s=p['bbar'] * min(1.0, raw), running=not done,
                      dip=0.0 if done else out['attempt_rate'] * p['Tpb'] * _dM_at(dM, h))
    # Derived dates quoted in Paper 1 (read by code/paper1_macros.py). With the greedy plan each embedded wave adds
    # step = q rho T_par to the expected embedded share (before bbar). complete_year: the calendar date at which the
    # program is embedded in expectation; cross_years: years after H0 at which the embedded gain bbar E dM first
    # exceeds the in-flight dip a_r T_pb dM (None if it never does while the program runs).
    step = out['q'] * out['rho'] * p['Tpar']
    n_full = math.ceil(1 / step - 1e-9)
    out['complete_year'] = H0 + out['clock'] * (p['Temb'] + (n_full - 1) * p['Tpar'])
    n_cross = math.floor(out['attempt_rate'] * p['Tpb'] / (p['bbar'] * step)) + 1
    out['cross_years'] = (out['clock'] * (p['Temb'] + (n_cross - 1) * p['Tpar'])
                          if n_cross < n_full else None)
    out['params'] = dict(p, dM=dM, n_proc=N_PROC)
    return out


def pace_fluid(p, dM, kap=None, dip_budget=None, dt=1 / 365):
    """Fluid version in program time, optionally with a dip budget (a public firm that holds to a guided dip,
    Proposition reg-dip): the calendar flow change bbar E dM - a T_pb dM/clock may not fall below -dip_budget, so the
    attempt rate a <= clock (dip_budget + bbar E dM)/(T_pb dM), and a <= rho; E(t) = q x (share attempted by t - T_emb)."""
    out = rates(p, kap)
    rho, q, clock = out['rho'], out['q'], out['clock']
    nT = int(round(((max(YEARS) - H0) / clock) / dt)) + 2
    lag = int(round(p['Temb'] / dt))
    cum = np.zeros(nT + 1)            # cumulative share attempted
    a_hist = np.zeros(nT + 1)
    # dM by calendar date: linear between the horizons, flat before the first (the compute share moves along its path)
    dM_t = (lambda t: float(np.interp(t, YEARS, [dM[h] for h in YEARS]))) if isinstance(dM, dict) else (lambda t: dM)
    for i in range(nT):
        E = min(1.0, q * (cum[i - lag] if i >= lag else 0.0))
        dMi = dM_t(H0 + i * dt * clock)
        if q * cum[i] >= 1.0:          # enough attempts made: the program winds down
            a = 0.0
        else:
            a = rho if dip_budget is None else min(rho, clock * (dip_budget + p['bbar'] * E * dMi) / (p['Tpb'] * dMi))
        a_hist[i] = a
        cum[i + 1] = cum[i] + a * dt
    for h in YEARS:
        i = int(round(((h - H0) / clock) / dt))
        E = min(1.0, q * (cum[i - lag] if i >= lag else 0.0))
        out[h] = dict(s=p['bbar'] * E, attempt_rate=a_hist[i], dip=a_hist[i] / clock * p['Tpb'] * _dM_at(dM, h),
                      running=a_hist[i] > 0)
    out['a0_share'] = a_hist[0] / rho                  # initial attempt rate as a share of the unconstrained one
    return out


# ----------------------------------------------------------------------------------------------
# Anchor (revision v2, D-3). Central: the E1 calibration rule, the 2023-25 firm-years of the audited sample (v3) at or
# above the 95th percentile of the cash score, without acquisition-affected firm-years; notes/calibration_anchor_v3.json
# (code/estimate_v3.py) holds it with the sensitivity blocks (E1all: every firm-year in the tail; E2, the organic sample;
# E2imp4 and E2imp8, the imputation bounds) and firm-cluster bootstrap intervals. The E1 block is reproduced below from
# data/panel_v3.csv. Only the lower-bound surplus Pi_lb > 0 is a conclusion; the upper-bound surplus has an interval
# that includes zero in every view (notes/inference_v3.md section 12).
# ----------------------------------------------------------------------------------------------
_av = json.load(open(v3path('notes', 'calibration_anchor_v3.json')))
d = pd.read_csv(v3path('data', 'panel_v3.csv'))
# Revealed pace of cost programs, recomputed on the audited panel (the flag of the params commit): change in the GAAP
# operating margin and in the FCF-after-SBC margin between fiscal 2022 and 2024 of the core firms with fiscal-2022
# revenue of at least $100 million, percentage points. A reference beside the central path, not a model input.
_r22 = d[(d.year == 2022) & (d.rev >= 1e8)][['cik', 'm_op', 'm_fcf_sbc']]
_r24 = d[d.year == 2024][['cik', 'm_op', 'm_fcf_sbc']]
_rv = _r22.merge(_r24, on='cik', suffixes=('_22', '_24'))
_qs = lambda x: dict(n=int(x.notna().sum()), **{nm: float(np.floor(10 * x.quantile(qq) + 0.5) / 10)
                                               for nm, qq in [('p10', .1), ('p25', .25), ('median', .5), ('p75', .75), ('p90', .9)]})
REVEALED_PACE_V2 = REVEALED_PACE
REVEALED_PACE = dict(grounding='c', basis='data/panel_v3.csv, core firms, FY2022 revenue >= $100M, FY2022-FY2024',
                     gaap_op_margin=_qs(100 * (_rv.m_op_24 - _rv.m_op_22)),
                     fcf_sbc_margin=_qs((100 * (_rv.m_fcf_sbc_24 - _rv.m_fcf_sbc_22)).dropna()),
                     previous_v2=REVEALED_PACE_V2)
# Grounding of the a_min band in the audited core sample (revision plan D8; the band itself is the params commit's): the
# 5th-percentile G&A share of firm-years with $1-10 billion of revenue and the 10th percentile above $10 billion, 2010-25.
_ga = d[d.ga.notna() & (d.rev > 0)].assign(gas=lambda x: x.ga / x.rev)
AMIN_GROUNDING = dict(basis='data/panel_v3.csv, 2010-25, G&A / revenue',
                      p5_1to10bn=float(_ga[(_ga.rev >= 1e9) & (_ga.rev < 1e10)].gas.quantile(.05)),
                      p10_above10bn=float(_ga[_ga.rev >= 1e10].gas.quantile(.10)),
                      n_1to10bn=int(((_ga.rev >= 1e9) & (_ga.rev < 1e10)).sum()), n_above10bn=int((_ga.rev >= 1e10).sum()),
                      band_used=(0.005, 0.046), note='band set from the broader software and internet universe; not changed here')
d = d[d.period == '2023-25'].copy()
d['R'] = d.g + d.m_fcf_sbc
_p95 = float(d.R.quantile(.95))
_tail = d[d.R >= _p95]
assert abs(_p95 - _av['E1']['p95']) < 1e-12 and len(_tail) == _av['E1']['n_tail'] \
    and int((_tail.acq_flag_v3 == 0).sum()) == _av['E1']['n'] and abs(float(d.g.median()) - _av['E1']['G']) < 1e-12, \
    'E1 block of calibration_anchor_v3.json does not reproduce from data/panel_v3.csv'
ANCHOR_CENTRAL = 'E1'
ANCHOR_SENS = ['E1all', 'E2', 'E2imp4', 'E2imp8']
ANCHORS = {nm: {k: v for k, v in _av[nm].items() if k != 'firm_years'} for nm in [ANCHOR_CENTRAL] + ANCHOR_SENS}
ANCHOR_BOOT = {nm: _av['bootstrap'][nm] for nm in [ANCHOR_CENTRAL] + ANCHOR_SENS}
anchor = ANCHORS[ANCHOR_CENTRAL]
top = pd.DataFrame(_av[ANCHOR_CENTRAL]['firm_years'])   # anchor firm-years (tax-deduction sensitivity)
q3 = lambda s: [float(s.quantile(.25)), float(s.quantile(.5)), float(s.quantile(.75))]
G25 = anchor['G']
# Round 2 (author decision 4, 2 Nov 2026; IM2-N7): the central basis nets the maintenance level of selling and marketing
# out of growth spend. sigma_net = max(S&M share - b_M, 0), with b_M the paper's own maintenance base: the median lagged
# S&M share of firm-years growing at or below the year median (notes/empirics_v3.json spend_maint_base, E1, all years;
# the statistic behind the netted spend ratio of Section 5.4). All S&M (upper bound) and no S&M (lower bound) are the
# bounds. m0_net = m + (1 - tau) sigma_net + kg; R_inf = m0 + (1 - k) G; Pi = R - R_inf, as for the bounds.
_E3 = json.load(open(v3path('notes', 'empirics_v3.json')))
MAINT_BASE = float(_E3['estimates']['spend_maint_base']['E1']['est'])
CENTRAL_BASIS = 'net'


def _net_stats(fy, G):
    t = pd.DataFrame(fy)
    m0n = t.m_fcf_sbc + (1 - TAU) * (t.sig_ub - MAINT_BASE).clip(lower=0) + t.kg
    rinf = m0n + (1 - t.k.fillna(0.0)) * G
    return dict(m0_net=q3(m0n), Rinf_net=q3(rinf), Pi_net=q3(t.R - rinf), shift_net=float(t.m0_ub.median() - m0n.median()),
                sig_net=q3((t.sig_ub - MAINT_BASE).clip(lower=0)), n_sm_above_base=int((t.sig_ub > MAINT_BASE).sum()))


for _nm in ANCHORS:
    ANCHORS[_nm].update(_net_stats(_av[_nm]['firm_years'], ANCHORS[_nm]['G']))

HZ = {
    '2028': dict(G=(0.10, 0.20), mu=(1.0, 2.0)),
    '2031': dict(G=(0.08, 0.20), mu=(0.75, 1.5)),
    '2036': dict(G=(0.05, 0.30), mu=(0.5, 1.25)),
}
HZ_OLD_M0 = {'2028': (0.40, 0.62), '2031': (0.45, 0.65), '2036': (0.50, M0_CAP_OLD)}


def Pi_scaled(Pi0, mu, alpha, k):
    return Pi0 * mu ** (1 / (1 - alpha)) * (1 - k) ** (1 / (1 - alpha))


Pi_ub = (max(anchor['Pi_ub'][0], 0.0), anchor['Pi_ub'][2])
Pi_lb = (max(anchor['Pi_lb'][0], 0.0), anchor['Pi_lb'][2])
m0A = (anchor['m0_ub'][0], anchor['m0_ub'][2])      # anchor interquartile ends, upper-bound case
# the full-cost margin terms move with the compute share, so the distance to them is horizon-specific
dM_lo = {int(h): M0_CEN[h] - m0A[0] for h in M0_CEN}
dM_hi = {int(h): M0_FAV[h] - m0A[1] for h in M0_FAV}
PL = pace(PACE['central'], dM_lo)
PH = pace(PACE['fast'], dM_hi)
PREV = {nm: pace(PACE_PREVIOUS[nm], dM_lo) for nm in PACE_PREVIOUS}     # pre-commit pace values, for comparison

# Pass-through: the saving passed to prices is the non-fee unit cost of revenue the program removes. U0 is today's
# (median core firm, 2023-25, data/panel_v3.csv: 1 - gross margin - fees); at full automation the unit cost is c_c.
GM0 = float((d.gp / d.rev).median())
U0 = 1.0 - GM0 - FC['f'][1]
PT_M0A = anchor['m0_' + CENTRAL_BASIS][1]          # pass-through baseline: the median anchor firm-year, central basis


# Pass-through, round 2 (B1 / IO2-1). phi is the industry pass-through RATE dp/du of Ganapati et al. (the share of a
# common unit-cost change that reaches the output price). Lemma lem:prices(a) holds for the elasticity d ln p/d ln u =
# phi u/p, and the margin share is computed at the post-cut price, so the revenue denominator falls with the price.
# All savings are exposed (Proposition prop:entry(d) prices the full unit cost, a_min and c_full included): the firm's
# non-fee unit cost falls from C0 = 1 - f - m0A/(1 - tau) today (the after-tax intercept m0A of the firm the ceiling or
# path describes, central basis) to K = 1 - f - base/(1 - tau) at the full-cost structure, a saving S = C0 - K per unit of
# today's price; the price falls to 1 - phi S, fees stay proportional to price and the other costs fixed per unit, so the
# after-tax margin term is (1 - tau)(1 - f - K/(1 - phi S)). The retention rule dur = 1 - phi (1 - HHI) (companion paper,
# eq:ext-game-dur) is the share of the DOLLAR saving a Cournot firm keeps once its volume gain is counted (first order:
# 1 - phi + phi/n with n = 1/HHI); the margin share does not depend on volume when costs are per unit, so HHI does not
# enter the score. scope 'variable' reproduces the v2 exposure (cost of revenue only, S = U0 - c_c) for comparison.
def pt_margin(c, phi, m0A=None, scope='all', rate=None):
    tau, f = c['tau'], c['f']
    K = 1 - f - c['base'] / (1 - tau)
    if scope == 'variable':
        S = U0 - c['c_c']
    else:
        C0 = 1 - f - (PT_M0A if m0A is None else m0A) / (1 - tau)
        S = C0 - K
    p1 = 1 - (phi if rate is None else rate) * S
    return (1 - tau) * (1 - f - K / p1)


def base_phi(c, phi, m0A=None):
    """After-tax margin term of a ceiling case c at pass-through rate phi, all savings exposed (round 2)."""
    return pt_margin(c, phi, m0A)


def horizon(h, Pi_25, m0_pair, dip_pair, shift=0.0, psi=0.0):
    p = HZ[h]
    rec = {}
    for k_pre in [0.0, 0.5]:
        k = (1 - psi * TAU) * k_pre                  # after-tax capital intensity (Remark taxes)
        m0 = (m0_pair[0] - shift, m0_pair[1] - shift)
        Rinf = (m0[0] + (1 - k) * p['G'][0], m0[1] + (1 - k) * p['G'][1])
        Pi = (min(Pi_scaled(Pi_25[0], p['mu'][0], a, k) for a in ALPHAS),
              max(Pi_scaled(Pi_25[1], p['mu'][1], a, k) for a in ALPHAS))
        R = (Rinf[0] + Pi[0], Rinf[1] + Pi[1])
        rec[str(k_pre)] = dict(m0=m0, Rinf=Rinf, Pi=Pi, R=R, dip=dip_pair,
                           R_net=(R[0] - dip_pair[0], R[1] - dip_pair[1]))
    return rec


out = dict(anchor=anchor, anchor_estimand='E1, calibration rule (D-3); sensitivity blocks in anchor_sensitivity',
           anchor_sensitivity=ANCHORS, anchor_bootstrap=ANCHOR_BOOT,
           ceiling=CEIL, ceiling_basis='2025 prices (c_c with no price path); ceiling_by_horizon follows the compute-share path',
           ceiling_by_horizon=CEIL_H,
           compute_share={'path': CC_PATH, 'values': {h: dict(value=v[0], bounds=v[1], grounding=v[2], model=cc_path(h),
                                                              cases=CC_CASES[h]) for h, v in CC.items()},
                          'high_compute_case': dict(value=CC_HIGH, feasible_at_full_automation=CC_HIGH <= CC_VALUE_TEST_CAP,
                                                    value_test_cap=CC_VALUE_TEST_CAP),
                          'case_rule': 'favorable and conservative = central halved and doubled (class d composite rule)'},
           pace={'central': PL, 'fast': PH}, pace_previous=PREV, revealed_pace=REVEALED_PACE, amin_grounding=AMIN_GROUNDING,
           upper_bound={}, lower_bound={}, previous={'upper_bound': {}, 'lower_bound': {}})


def horizon_ranges(phi=0.0):
    """Upper- and lower-bound horizon ranges at pass-through phi: the intercept moves toward the full-cost margin
    terms net of the saving passed to prices (the in-flight dip is a cost, so it is not passed through)."""
    res = {'upper_bound': {}, 'lower_bound': {}}
    for h in HZ:
        yi = int(h)
        s_pair = (PL[yi]['s'], PH[yi]['s'])
        tgt = (base_phi(CEIL_H[h]['central'], phi), base_phi(CEIL_H[h]['favorable'], phi))
        m0_pair = (m0A[0] + s_pair[0] * (tgt[0] - m0A[0]), m0A[1] + s_pair[1] * (tgt[1] - m0A[1]))
        dip_pair = (PL[yi]['dip'], PH[yi]['dip'])
        for b, Pi25, sh in [('upper_bound', Pi_ub, 0.0), ('lower_bound', Pi_lb, anchor['shift'])]:
            res[b][h] = horizon(h, Pi25, m0_pair, dip_pair, shift=sh)
            res[b][h]['s'] = s_pair
            res[b][h]['m0_target'] = tgt
    return res


_r0 = horizon_ranges(0.0)                            # fixed prices: the case reported in Table tab:calib
for b in ['upper_bound', 'lower_bound']:
    out[b] = _r0[b]
    for h in HZ:
        out['previous'][b][h] = horizon(h, Pi_ub if b == 'upper_bound' else Pi_lb, HZ_OLD_M0[h], (0.0, 0.0),
                                        shift=0.0 if b == 'upper_bound' else anchor['shift'])
# pass-through scenario dimension: ceilings (static and by horizon) and horizon ranges for each phi
out['pass_through'] = {'phi': list(PHI), 'hhi': HHI, 'U0': U0, 'gross_margin_median_2023_25': GM0,
                       'rule': 'round 2: phi is the pass-through rate of the whole unit-cost saving S = C0 - K (all savings, prop:entry(d)); '
                                   'margin share at the post-cut price 1 - phi S; dur = 1 - phi (1 - HHI) is the dollar-profit share '
                                   'with the volume response and is reported, not used', 'C0_baseline_m0A': PT_M0A}
for phi in PHI:
    rr = horizon_ranges(phi)
    out['pass_through'][f'{phi:.1f}'] = dict(
        dur=dur(phi),
        ceiling={c: dict(base=base_phi(CEIL[c], phi), G100=1 - base_phi(CEIL[c], phi)) for c in CASES},
        ceiling_by_horizon={h: {c: dict(base=base_phi(CEIL_H[h][c], phi), G100=1 - base_phi(CEIL_H[h][c], phi))
                                for c in CASES} for h in CEIL_H},
        upper_bound=rr['upper_bound'], lower_bound=rr['lower_bound'])

# Regime and pace variants, on the central path of Table tab:calib (revision v2): the median anchor firm-year's
# upper-bound intercept moving toward the central full-cost margin term at each horizon, output prices fixed
dM_c = {int(h): base_phi(CEIL_H[h]['central'], 0.0) - anchor['m0_' + CENTRAL_BASIS][1] for h in HZ}
var = {}
var['central_fluid'] = pace_fluid(PACE['central'], dM_c)
var['public_guided_dip_1pt'] = pace_fluid(PACE['central'], dM_c, dip_budget=0.01)
var['public_guided_dip_2pt'] = pace_fluid(PACE['central'], dM_c, dip_budget=0.02)
var['sponsor_latency_0.5'] = pace(PACE['central'], dM_c, kap=0.78)
var['slow_public'] = pace(PACE['slow'], dM_c, kap=0.70)
var['slow_sponsor_latency_0.5'] = pace(PACE['slow'], dM_c, kap=0.78)
for name, v in var.items():
    v['m0'] = {h: anchor['m0_' + CENTRAL_BASIS][1] + v[h]['s'] * dM_c[h] for h in YEARS}
out['variants'] = var
out['variants_basis'] = ('central path: median anchor firm-year, maintenance-netted basis (round 2, decision 4), central '
                         'full-cost target at each horizon')
# compute-share sensitivity (Corollary ceiling): central case over the scenario bounds of c_c, and tau at 9%
def G100_central(cc, tau=None):
    v = {k: val[1] for k, val in FC.items()}
    tau = v['tau'] if tau is None else tau
    c = fullcost('central')
    c_anc = v['s_fin'] * cc + v['anc_fixed'] / S_REF
    full = c['c_full'] - c['c_anc'] + c_anc
    return 1 - (1 - tau) * (1 - cc - v['f'] - v['a_min'] - full), 1 - (1 - tau) * (1 - cc - v['f'] - v['a_min'])
# grid: the credible bounds of every horizon (0.01 to the value-test cap s_L = 0.60), the centrals, the old central 0.20,
# the old cap 0.30 and the high-compute case 0.40
CC_GRID = sorted({0.01, 0.02, 0.05, 0.06, 0.08, 0.12, 0.20, 0.25, CC_OLD_CAP, CC_HIGH, CC_VALUE_TEST_CAP})
out['cc_sensitivity'] = {f'{cc:.2f}': G100_central(cc) for cc in CC_GRID}
out['cc_sensitivity_by_horizon'] = {h: {f'{cc:.2f}': G100_central(cc) for cc in sorted({v[1][0], v[0], v[1][1]})}
                                    for h, v in CC.items()}
out['tau_sensitivity'] = {f'{t:.2f}': G100_central(FC['c_c'][1], t) for t in [0.09, 0.15, 0.18, 0.21]}
out['cerr_sensitivity'] = {}
for nm, ce in [('favorable', fullcost('favorable')['c_err']), ('central', fullcost('central')['c_err']),
               ('conservative', fullcost('conservative')['c_err']),
               # round 2 (B4 / IO2-7): today's highest measured rates (omission 0.18, Magesh et al.; hallucination 0.20)
               # at unit loss on the automated-work base W_A, under the ceiling's no-review rule (e_o + e_h), and the
               # AI-review bound chi (e_o + e_h) with chi = 0.60, P(same wrong answer | both wrong) (Kim et al. 2025)
               ('high rates, unit loss', FC['A_auto'][1] * (0.18 + 0.20) * 1.0),
               ('high rates, unit loss, AI review bound', FC['A_auto'][1] * 0.60 * (0.18 + 0.20) * 1.0),
               ('high rates, unit loss, human catch rates (v2, superseded)', 0.30 * (0.18 * 0.55 + 0.20 * 0.80) * 1.0)]:
    c = fullcost('central')
    v = {k: val[1] for k, val in FC.items()}
    out['cerr_sensitivity'][nm] = (ce, 1 - (1 - v['tau']) * (1 - v['c_c'] - v['f'] - v['a_min'] - c['c_full'] + c['c_err'] - ce))
out['amin_sensitivity'] = {}
for am in [0.005, 0.03, 0.046]:
    v = {k: val[1] for k, val in FC.items()}
    c = fullcost('central')
    out['amin_sensitivity'][f'{am:.3f}'] = (1 - (1 - v['tau']) * (1 - v['c_c'] - v['f'] - am - c['c_full']),
                                            1 - (1 - v['tau']) * (1 - v['c_c'] - v['f'] - am))

# Tax deductions for capital: anchor intercepts, k = 0.5 column and the ceiling's capital term under each psi
psi_out = {'psi': PSI, 'anchor_m0_ub': {}, 'anchor_m0_lb': {}, 'k05_upper_bound': {}, 'ceiling_k15_G30_loss': {}}
for nm, ps in PSI.items():
    psi_out['anchor_m0_ub'][nm] = q3(top.m_fcf_sbc + (1 - TAU) * top.sig_ub + (1 - ps * TAU) * top.kg)
    psi_out['anchor_m0_lb'][nm] = q3(top.m_fcf_sbc + (1 - ps * TAU) * top.kg)
    psi_out['k05_upper_bound'][nm] = {}
    for h in HZ:
        yi = int(h)
        s_pair = (PL[yi]['s'], PH[yi]['s'])
        m0_pair = (m0A[0] + s_pair[0] * dM_lo[yi], m0A[1] + s_pair[1] * dM_hi[yi])
        psi_out['k05_upper_bound'][nm][h] = horizon(h, Pi_ub, m0_pair, (PL[yi]['dip'], PH[yi]['dip']), psi=ps)['0.5']['R']
    psi_out['ceiling_k15_G30_loss'][nm] = {f'{t:.2f}': (1 - ps * t) * 1.5 * 0.30 for t in FC['tau']}
psi_out['anchor_tau_kg'] = q3(TAU * top.kg)
out['psi_sensitivity'] = psi_out

C = lambda a: (1 - a) * a ** (a / (1 - a))
out['Lambda_rule1000'] = {a: ((10 - (0.5 + 0.2)) / C(a)) ** (1 - a) for a in [0.2, 0.25, 0.3, 0.45]}
out['lam_for_Pi'] = {b: {a: (P[1] / C(a)) ** (1 - a) for a in ALPHAS} for b, P in [('ub', Pi_ub), ('lb', Pi_lb)]}
out['rule1000_multiple'] = {b: {a: out['Lambda_rule1000'][a] / out['lam_for_Pi'][b][a] for a in ALPHAS} for b in ['ub', 'lb']}


# ----------------------------------------------------------------------------------------------
# Central path and tornado (revision v2; revision plan A9 and D5, panel item EX-5). The ranges above pair the extreme
# ends of every assumption, and their upper ends in 2028 and 2031 scaled the lower-bound surplus, for which the model
# gives no basis (when no spend buys growth the surplus is not a return to spend). They are kept in the JSON for the
# record only. The paper reports a central path and one-at-a-time sensitivities instead.
# Central path: the median anchor firm-year's intercept m_0A (central anchor, both bounds on growth spend) moves toward
# the central full-cost margin term at each horizon at central execution, output prices fixed, k = 0, market growth G
# held at the anchor's median growth of 2023-25 (the horizon ranges of G enter the tornado). The durable score is R_inf = m_0 + G. A transient surplus is added only under
# the upper bound on spend, where the model's scaling Pi ~ mu^(1/(1-alpha)) applies; at the median anchor firm-year it
# is zero (Pi_ub median below zero, floored), so the central maximal score equals the durable score.
# ----------------------------------------------------------------------------------------------
ALPHA_C = 0.35
CEN = {h: dict(G=G25, mu=sum(HZ[h]['mu']) / 2) for h in HZ}   # G held at the anchor's median growth (firm-level reading)


def central_path(anc=None, bound=CENTRAL_BASIS, q=1, pace_case='central', target_case='central', phi=0.0, k_pre=0.0,
                 psi=0.0, G=None, mu=None, alpha=ALPHA_C, pi_q=None, pace_params=None, m0A=None):
    """Path of the durable score (and the surplus under the upper bound) for one anchor firm-year type.
    bound: 'net' (central, maintenance-netted), 'ub' (all S&M buys growth) or 'lb' (none does). q: quartile index of the
    anchor intercept; pi_q: quartile index of the surplus (None: the same as q). A surplus is scaled only under 'ub'.
    phi > 0: the industry realizes the same share s as the firm, so the price is 1 - phi s S_h and the intercept is
    (1 - tau)[1 - f - (C0 - s S_h)/(1 - phi s S_h)] (exact; equals m0A + s (m0F - m0A) at phi = 0)."""
    anc = anchor if anc is None else anc
    m0A_ = anc['m0_' + bound][q] if m0A is None else m0A
    Pi25 = max(anc['Pi_ub'][q if pi_q is None else pi_q], 0.0) if bound == 'ub' else 0.0
    tgt = {h: base_phi(CEIL_H[h][target_case], phi, m0A_) for h in HZ}
    P = pace(PACE[pace_case] if pace_params is None else pace_params, {int(h): tgt[h] - m0A_ for h in HZ})
    k = (1 - psi * TAU) * k_pre
    res = {'m0A': m0A_, 'Pi25': Pi25, 'R25': anc['R'][1], 'bound': bound}
    for h in HZ:
        yi = int(h)
        c = CEIL_H[h][target_case]
        G_ = CEN[h]['G'] if G is None else G[h]
        mu_ = CEN[h]['mu'] if mu is None else mu[h]
        s_ = P[yi]['s']
        if phi:
            C0 = 1 - c['f'] - m0A_ / (1 - c['tau'])
            Sh = C0 - (1 - c['f'] - c['base'] / (1 - c['tau']))
            m0 = (1 - c['tau']) * (1 - c['f'] - (C0 - s_ * Sh) / (1 - phi * s_ * Sh))
        else:
            m0 = m0A_ + s_ * (tgt[h] - m0A_)
        Rinf = m0 + (1 - k) * G_
        Pi = Pi_scaled(Pi25, mu_, alpha, k)
        res[h] = dict(s=s_, target=tgt[h], m0=m0, G=G_, mu=mu_, Rinf=Rinf, Pi=Pi, R=Rinf + Pi,
                      dip=P[yi]['dip'], R_net=Rinf + Pi - P[yi]['dip'], running=P[yi]['running'])
    res['pace'] = {kk: P[kk] for kk in ('complete_year', 'cross_years', 'attempt_rate', 'q', 'rho', 'clock')}
    return res


BASES3 = ['net', 'ub', 'lb']
CP = {b: central_path(bound=b) for b in BASES3}
CP_PHI = {f'{phi:.1f}': {b: central_path(bound=b, phi=phi) for b in BASES3} for phi in PHI}
CP_ANCHOR = {nm: {b: central_path(anc=ANCHORS[nm], bound=b) for b in BASES3} for nm in ANCHORS}
lo_hi = lambda key: ({h: HZ[h][key][0] for h in HZ}, {h: HZ[h][key][1] for h in HZ})
MU_lo, MU_hi = lo_hi('mu')
# Round 2 (B12 / IO2-N8): the 5-30% band of market growth had no stated basis. The tornado now takes the interquartile
# range of revenue growth of the core firm-years of 2023-25 (class c, own data, data/panel_v3.csv), the sample whose
# median sets the central G; the old bands stay in HZ for the record of the dropped ranges.
G_BAND = (float(d.g.quantile(.25)), float(d.g.quantile(.75)))
G_lo, G_hi = ({h: G_BAND[0] for h in HZ}, {h: G_BAND[1] for h in HZ})
G_lo_old, G_hi_old = lo_hi('G')
# BCG "win" only (round 2, B9 / X2-N2): 30% of transformations met their targets (Forth et al. 2020), each realizing the
# 67% that McKinsey (2021) reports for successful transformations; failed attempts realize nothing in the model.
PACE_BCG_WIN = dict(PACE['central'], varpi=0.30)
TORNADO_ITEMS = [   # (key, label, low-case kwargs, high-case kwargs); the reference is the central path (central basis)
    ('anchor_quartile', 'Anchor intercept: lower and upper quartile', dict(q=0), dict(q=2)),
    ('surplus', 'Transient surplus of the upper-quartile firm-year (all selling and marketing buys growth), pull and '
                '$\\alpha$ at their ends', dict(bound='ub', q=1, pi_q=2, mu=MU_lo, alpha=0.25),
     dict(bound='ub', q=1, pi_q=2, mu=MU_hi, alpha=0.45)),
    ('G', 'Market growth $G$ over the interquartile range of 2023--25 growth', dict(G=G_lo), dict(G=G_hi)),
    ('pace', 'Execution: slow and fast', dict(pace_case='slow'), dict(pace_case='fast')),
    ('bcg_win', 'Execution yield: BCG win zone only ($\\varpi=0.30$, $\\bar b=0.67$)', dict(pace_params=PACE_BCG_WIN), dict()),
    ('target', 'Full-cost target: conservative and favorable case', dict(target_case='conservative'),
     dict(target_case='favorable')),
    ('pass_through', 'Pass-through $\\varphi=0.7$ of all savings (fixed prices at the central value)', dict(phi=0.7), dict()),
    ('capital', 'Capital $k=0.5$, not deductible', dict(k_pre=0.5, psi=0.0), dict()),
    ('attribution', 'Selling and marketing: none and all of it buys growth', dict(bound='lb'), dict(bound='ub')),
]
TORNADO = {}
for h in HZ:
    ref = CP[CENTRAL_BASIS][h]['R']
    rows_t = []
    for key, lab, klo, khi in TORNADO_ITEMS:
        lo_ = central_path(**klo)[h]['R']
        hi_ = central_path(**khi)[h]['R']
        rows_t.append(dict(key=key, label=lab, low=min(lo_, hi_), high=max(lo_, hi_)))
    an = [CP_ANCHOR[nm][CENTRAL_BASIS][h]['R'] for nm in ANCHOR_SENS]
    rows_t.append(dict(key='anchor_sample', label='Anchor sample: every firm-year of the tail, E2, $M=4$, $M=8$',
                       low=min(an), high=max(an)))
    rows_t.append(dict(key='dip', label='A firm still transforming (in-flight dip)', low=ref - CP[CENTRAL_BASIS][h]['dip'],
                       high=ref))
    rows_t.sort(key=lambda r: -(r['high'] - r['low']))
    TORNADO[h] = dict(reference=ref, rows=rows_t,
                      G_old_band=dict(low=central_path(G=G_lo_old)[h]['R'], high=central_path(G=G_hi_old)[h]['R'],
                                      band=HZ[h]['G']))
out['central_path'] = dict(alpha=ALPHA_C, scenario=CEN, path=CP, pass_through=CP_PHI, by_anchor=CP_ANCHOR,
                          central_basis=CENTRAL_BASIS, maint_base=MAINT_BASE, G_band=G_BAND)
out['tornado'] = TORNADO

# ----------------------------------------------------------------------------------------------
# The frontier-slope mapping of Section model-industry (D-2; notes/theory_fixes_v2.md 1.10): under a common frontier
# with k = 0, the Psi_chi slope -b on the estimator's grid g0 = 0, 0.05, ..., W implies ell = (S_beta/b)^alpha, with S_beta
# the least-squares slope of Delta^beta on that grid, and a steepest slope beta W^(beta-1) b/S_beta at the window's end.
# The calibration inverts the model firm by firm and does not use ell; the mapping is recorded for the text.
# ----------------------------------------------------------------------------------------------
FS3 = json.load(open(v3path('notes', 'frontier_slope_v3.json')))


def ell_map(b, W, a):
    be = 1 / a
    g_ = np.arange(0, W + 1e-9, 0.05)
    S_ = float(np.polyfit(g_, g_ ** be, 1)[0])
    return dict(ell=(S_ / b) ** a, steepest=be * W ** (be - 1) * b / S_)


ELL_ROWS = {'E1_cash_w60': (abs(FS3['central']['cash']['E1']['est']), 0.6),
            'E1_op_w60': (abs(FS3['central']['op']['E1']['est']), 0.6),
            'E2_cash_w60': (abs(FS3['central']['cash']['E2']['est']), 0.6),
            'E2_op_w60': (abs(FS3['central']['op']['E2']['est']), 0.6),
            'E1_cash_w40': (abs(FS3['grid']['cash']['chi90_w40']['E1']['est']), 0.4),
            'E1_op_w40': (abs(FS3['grid']['op']['chi90_w40']['E1']['est']), 0.4)}
out['ell_psi'] = {r: {f'{a:.2f}': ell_map(b, W, a) for a in (0.25, 0.30, 0.35, 0.45)} | dict(b=b, W=W)
                  for r, (b, W) in ELL_ROWS.items()}


# ==============================================================================================================
# ROUND 2 REVISION (2 Nov 2026; notes/reviews/paper1_v2/revision_plan_r2.md items B1-B12; notes/r2_code_changes.md).
# Everything below is written to out['r2'] and read by code/paper1_macros.py.
# ==============================================================================================================
R2 = {}
CEN_C = CEIL['central']
_pct = lambda x: float(np.floor(1000 * x + 0.5) / 10)

# ---- B1. Pass-through: reconciliation of the v2 implementation, the referee's reading and the round-2 mapping
def _G(base):
    return 1 - base


def _v2_base(c, phi):                                 # v2: margin share at the old revenue, dur on the variable saving
    return c['base'] - (1 - c['tau']) * (1 - dur(phi)) * (U0 - c['c_c'])


_pt = {}
for phi in (0.5, 0.7):
    rate_dur = phi * (1 - HHI)                        # the v2 code's passed share, read as a price rate (the referee's reading)
    _pt[f'{phi:.1f}'] = {
        'v2_code_variable_old_revenue': _G(_v2_base(CEN_C, phi)),
        'referee_rate_phi_1mH_variable': _G(pt_margin(CEN_C, phi, scope='variable', rate=rate_dur)),
        'rate_phi_variable': _G(pt_margin(CEN_C, phi, scope='variable')),
        'referee_rate_phi_1mH_all_ub': _G(pt_margin(CEN_C, phi, m0A=anchor['m0_ub'][1], rate=rate_dur)),
        'rate_phi_all_ub': _G(pt_margin(CEN_C, phi, m0A=anchor['m0_ub'][1])),
        'rate_phi_all_net_CENTRAL': _G(pt_margin(CEN_C, phi)),
        'rate_phi_all_lb': _G(pt_margin(CEN_C, phi, m0A=anchor['m0_lb'][1])),
        'dur_dollar_share': dur(phi), 'price_cut_central': phi * ((1 - CEN_C['f'] - PT_M0A / (1 - CEN_C['tau']))
                                                                  - (1 - CEN_C['f'] - CEN_C['base'] / (1 - CEN_C['tau']))),
        'elasticity_first_order_central': phi * (1 - CEN_C['f'] - PT_M0A / (1 - CEN_C['tau'])),
    }
# the retention rule, checked in linear Cournot with n = 1/HHI symmetric firms: dP/dc = n/(n+1) and a firm keeps
# 2/(n+1) = 1 - phi (1 - 1/n) of a common saving delta q, counting its volume gain
_n, _A, _b, _c0, _dl = 4, 10.0, 1.0, 4.0, 1e-6
_q = lambda c: (_A - c) / (_b * (_n + 1))
_pi = lambda c: _b * _q(c) ** 2
_phi_ind = _n / (_n + 1)
_ret = (_pi(_c0 - _dl) - _pi(_c0)) / (_dl * _q(_c0))
assert abs(_ret - (1 - _phi_ind * (1 - 1 / _n))) < 1e-5
R2['pass_through'] = dict(by_phi=_pt, C0_m0A=PT_M0A, U0=U0, hhi=HHI, cournot_check=dict(n=_n, phi_ind=_phi_ind, retained=_ret),
                          note='central: rate phi, all savings, net-basis anchor; others for reconciliation (same W_A = s_L)')

# ---- B2. Compute share range under the stated value test (c_c <= s_L)
R2['compute_range'] = dict(cap=CC_VALUE_TEST_CAP, old_cap=CC_OLD_CAP, G_lo=out['cc_sensitivity']['0.01'][0],
                           G_cap=G100_central(CC_VALUE_TEST_CAP)[0], G_old_cap=G100_central(CC_OLD_CAP)[0],
                           G_high=G100_central(CC_HIGH)[0], high_feasible=CC_HIGH <= CC_VALUE_TEST_CAP)

# ---- B3. Compute path drivers (class d) and the date at which the path's share reaches the 2025-price value
def cc_at(t, kap_front=None, om=None):
    c = CC_PATH
    yrs = [2028, 2031, 2036]
    oms = [c['omega'][str(y)] for y in yrs] if om is None else om
    w = float(np.interp(t, yrs, oms))
    kf = c['kappa_front'] if kap_front is None else kap_front
    k_fixed = max(c['kappa_2025'] / c['D'] ** (t - H0_PRICES), c['floor_share'] * c['kappa_2025'])
    return c['s_L'] * (w * kf + (1 - w) * k_fixed)


_ts = np.arange(2028, 2036.0001, 0.01)
_cc = np.array([cc_at(t) for t in _ts])
_t6 = float(_ts[np.argmax(_cc <= CC['prices2025'][0] + 1e-12)])
_G28 = lambda cc: G100_central(cc)[0]
R2['compute_path'] = dict(kappa_front=CC_PATH['kappa_front'], omega=CC_PATH['omega'], D=CC_PATH['D'],
                          kappa_2025=CC_PATH['kappa_2025'], s_L=CC_PATH['s_L'], grounding='d (kappa_front, omega_H)',
                          year_cc_reaches_2025_value=_t6, cc_2025_value=CC['prices2025'][0],
                          kappa_fixed_2028=max(CC_PATH['kappa_2025'] / CC_PATH['D'] ** 3, CC_PATH['floor_share'] * CC_PATH['kappa_2025']),
                          sens_2028={f'omega_{w}': dict(cc=cc_at(2028, om=[w, 0.4, 0.25]), G=_G28(cc_at(2028, om=[w, 0.4, 0.25])))
                                     for w in (0.3, 0.9)}
                          | {f'kappa_front_{k}': dict(cc=cc_at(2028, kap_front=k), G=_G28(cc_at(2028, kap_front=k)))
                             for k in (0.10, 0.50)})

# ---- B4. Dips, crossing, transition cost and the fast dip on the central path's basis
CPc = CP[CENTRAL_BASIS]
_tpb2 = central_path(pace_params=dict(PACE['central'], Tpb=2.0))
_fast = central_path(pace_case='fast')
_fast_ub = central_path(pace_case='fast', bound='ub')
R2['dip'] = dict(central={h: CPc[h]['dip'] for h in HZ}, cross_years=CPc['pace']['cross_years'],
                 Tpb=PACE['central']['Tpb'], Tpb_source='Table S7 "Embedding time" 1.25 years; params commit T_pb = T_emb',
                 Tpb2={h: _tpb2[h]['dip'] for h in HZ}, Tpb2_cross_years=_tpb2['pace']['cross_years'],
                 fast_central_basis={h: _fast[h]['dip'] for h in HZ},
                 fast_ub_median_central_target={h: _fast_ub[h]['dip'] for h in HZ}, fast_old_range_basis={h: PH[int(h)]['dip'] for h in HZ},
                 by_basis={b: {h: CP[b][h]['dip'] for h in HZ} for b in BASES3})


def _cross_fine(p_, Tpb):
    """Fluid-free check of the crossing with T_pb: first wave count at which bbar x embedded >= attempt rate x T_pb."""
    r_ = rates(p_)
    step = r_['q'] * r_['rho'] * p_['Tpar']
    n_full = math.ceil(1 / step - 1e-9)
    n_cross = math.floor(r_['attempt_rate'] * Tpb / (p_['bbar'] * step)) + 1
    return r_['clock'] * (p_['Temb'] + (n_cross - 1) * p_['Tpar']) if n_cross < n_full else None


assert abs(_cross_fine(PACE['central'], 2.0) - _tpb2['pace']['cross_years']) < 1e-12

# ---- B5. Anchor sampling interval carried through the central path (firm-cluster draws of code/estimate_v3.py)
_Z = np.load(v3path('notes', 'bootstrap_draws_v3.npz'), allow_pickle=True)
_U, _FD = _Z['firm_universe'], _Z['anchor__firm_draws']
_ST = [str(x) for x in _Z['anchor__statistics']]
_full = pd.read_csv(v3path('data', 'panel_v3.csv'))
_full['G_t'] = _full.groupby('year').g.transform('median')
_rows = {c_: np.where(_full.cik.values == c_)[0] for c_ in _U}


def _anchor_draw(x):
    s_ = x.sm_lag_share
    ok_ = s_.notna() & (s_ >= 0.01) & (s_ <= 1.5) & x.g.notna()
    base_ = float(s_[ok_ & (x.g <= x.G_t)].median())
    p_ = x[x.period == '2023-25']
    R_ = p_.g + p_.m_fcf_sbc
    G_ = float(np.median(p_.g.dropna()))
    t_ = p_[(R_ >= np.quantile(R_.dropna(), 0.95)) & (p_.acq_flag_v3 == 0)]
    sig_ = (t_.sm / t_.rev).fillna(0.0)
    kg_ = t_.capex_int.fillna(0.0)
    m_ = t_.m_fcf_sbc
    return dict(ub=float((m_ + (1 - TAU) * sig_ + kg_).median()), lb=float((m_ + kg_).median()),
                net=float((m_ + (1 - TAU) * (sig_ - base_).clip(lower=0) + kg_).median()), G=G_, base=base_)


_pt0 = _anchor_draw(_full)
assert abs(_pt0['ub'] - anchor['m0_ub'][1]) < 1e-12 and abs(_pt0['net'] - anchor['m0_net'][1]) < 1e-12 and abs(_pt0['G'] - G25) < 1e-12
_draws = [_anchor_draw(_full.iloc[np.concatenate([_rows[_U[j]] for j in _FD[b_]])]) for b_ in range(_FD.shape[0])]
_m0ub_saved = _Z['anchor'][:, 0, _ST.index('anchor_p95_m0_ub_med')]
assert max(abs(dr['ub'] - _m0ub_saved[i]) for i, dr in enumerate(_draws)) < 1e-12, 'anchor draws do not reproduce'
_pci = lambda x: [float(np.quantile(x, 0.05)), float(np.quantile(x, 0.95))]
_b5 = {'B': len(_draws), 'interval': '90% percentile, firm-cluster draws of estimate_v3.py block "anchor"'}
for b in BASES3:
    m0d = np.array([dr[b] for dr in _draws])
    Gd = np.array([dr['G'] for dr in _draws])
    _b5[b] = dict(m0A=dict(est=anchor['m0_' + b][1], ci90=_pci(m0d)), path={})
    for h in HZ:
        s_, tg = CP[b][h]['s'], CP[b][h]['target']
        _b5[b]['path'][h] = dict(R=CP[b][h]['R'], ci90_joint=_pci((1 - s_) * m0d + s_ * tg + Gd),
                                 ci90_intercept_only=_pci((1 - s_) * m0d + s_ * tg + G25))
_b5['G'] = dict(est=G25, ci90=_pci(np.array([dr['G'] for dr in _draws])))
_b5['maint_base'] = dict(est=MAINT_BASE, ci90=_pci(np.array([dr['base'] for dr in _draws])))
R2['anchor_interval'] = _b5

# ---- B7. Crossing, cumulative payback (undiscounted and at r = 9.34%), NPV and hold periods; G* decomposition
R_WACC = 0.0934


def payback(path, pace_p, r=R_WACC, dt=1 / 365, T=200.0):
    m0A_ = path['m0A']
    dM = {int(h): path[h]['target'] - m0A_ for h in HZ}
    yrs = sorted(dM)
    rr = rates(pace_p)
    step = rr['q'] * rr['rho'] * pace_p['Tpar']
    t = np.arange(0, T, dt)
    tR = t / rr['clock']
    n = np.where(tR < pace_p['Temb'], 0, np.floor((tR - pace_p['Temb']) / pace_p['Tpar'] + 1e-12) + 1)
    raw = step * n
    dm = np.interp(H0 + t, yrs, [dM[y] for y in yrs])
    gain = pace_p['bbar'] * np.minimum(1.0, raw) * dm
    dip = np.where(raw < 1.0, rr['attempt_rate'] * pace_p['Tpb'] * dm, 0.0)
    net = gain - dip
    disc = (1 + r) ** (-t)
    cu, cd = np.cumsum(net) * dt, np.cumsum(net * disc) * dt
    first = lambda m: float(t[np.argmax(m)]) if m.any() else None
    neg = cu < 0
    pb_u = first((cu >= 0) & (np.cumsum(neg) > 0))
    pb_d = first((cd >= 0) & (np.cumsum(cd < 0) > 0))
    pv_gain, pv_dip = float(np.sum(gain * disc) * dt), float(np.sum(dip * disc) * dt)
    return dict(cross_flow=first((gain >= dip) & (raw < 1.0) & (raw > 0)), payback_undiscounted=pb_u, payback_discounted=pb_d,
                npv_points_years=pv_gain - pv_dip, pv_gain=pv_gain, pv_dip=pv_dip, ratio=pv_gain / pv_dip,
                complete_years=float(t[np.argmax(raw >= 1.0)]) if (raw >= 1.0).any() else None,
                hold={yr: dict(cum=float(cu[int(round(yr / dt)) - 1]), cum_disc=float(cd[int(round(yr / dt)) - 1]))
                      for yr in (3, 4, 5, 7, 10)}, r=r, dM=dM)


R2['payback'] = {pc: payback(central_path(pace_case=pc), PACE[pc]) for pc in ('slow', 'central', 'fast')}
R2['payback']['central_r10'] = payback(CPc, PACE['central'], r=0.10)
R2['payback']['central_ub'] = payback(CP['ub'], PACE['central'])
v = {k: val[1] for k, val in FC.items()}
_dec = dict(tax=CEN_C['tau'], compute=(1 - CEN_C['tau']) * CEN_C['c_c'], fees=(1 - CEN_C['tau']) * CEN_C['f'],
            accountability=(1 - CEN_C['tau']) * CEN_C['a_min'], full_cost=(1 - CEN_C['tau']) * CEN_C['c_full'],
            full_cost_parts={k_: (1 - CEN_C['tau']) * CEN_C[k_] for k_ in ('c_mnt', 'c_sec', 'c_err', 'c_anc')})
assert abs(sum(v_ for k_, v_ in _dec.items() if k_ != 'full_cost_parts') - CEN_C['G100']) < 1e-12
R2['gstar_decomposition'] = _dec

# ---- B8. Deferred revenue (k < 0) and a typical $1-5 billion firm (central cost structure, psi = 0)
_d15 = d[(d.rev >= 1e9) & (d.rev < 5e9)].copy()
_d15['sms'], _d15['gas'], _d15['rds'], _d15['gms'] = _d15.sm / _d15.rev, _d15.ga / _d15.rev, _d15.rd / _d15.rev, _d15.gp / _d15.rev
_d15['sbcs'] = _d15.sbc / _d15.rev
_d15['kg'] = _d15.capex_int.fillna(0.0)
_d15['m0_ub'] = _d15.m_fcf_sbc + (1 - TAU) * _d15.sms.fillna(0.0) + _d15.kg
_d15['m0_net'] = _d15.m_fcf_sbc + (1 - TAU) * (_d15.sms.fillna(0.0) - MAINT_BASE).clip(lower=0) + _d15.kg
_d15['m0_lb'] = _d15.m_fcf_sbc + _d15.kg
_d15['k'] = np.where(_d15.g > 0, _d15.kg / _d15.g.where(_d15.g > 0), np.nan)
_med = lambda c_: float(_d15[c_].median())
TYP = dict(n=int(len(_d15)), firms=int(_d15.cik.nunique()), basis='data/panel_v3.csv, 2023-25 core firm-years with revenue $1-5bn',
           **{c_: _med(c_) for c_ in ('g', 'm_fcf_sbc', 'm_op', 'R_fcf_sbc', 'R_op', 'sms', 'gas', 'rds', 'gms', 'sbcs', 'kg',
                                      'm0_ub', 'm0_net', 'm0_lb', 'k')})
TYP['gap_to_central_margin_term'] = {b: CEN_C['base'] - TYP['m0_' + b] for b in BASES3}
TYP['durable_at_own_growth'] = {b: TYP['m0_' + b] + TYP['g'] for b in BASES3}
TYP['G_star_at_own_k'] = (1 - CEN_C['base']) / (1 - TYP['k'])
K_ROWS = {f'{k_:+.2f}': dict(k=k_, G_star={c: (1 - CEIL[c]['base']) / (1 - k_) for c in ('favorable', 'central', 'conservative')})
          for k_ in (-0.3, 0.0, 0.5)}
R2['k_rows'] = K_ROWS
R2['typical_1to5bn'] = TYP
# final audit M3: the same pass-through scenario when the saving is that of a typical $1-5 billion firm (netted median
# intercept), and the anchor's own implied unit cost, so that the text can say whose saving sets the price cut
_Kc = 1 - CEN_C['f'] - CEN_C['base'] / (1 - CEN_C['tau'])
_C0 = lambda m0: 1 - CEN_C['f'] - m0 / (1 - CEN_C['tau'])
R2['pass_through']['typical'] = {f'{phi:.1f}': dict(G=_G(pt_margin(CEN_C, phi, m0A=TYP['m0_net'])),
                                                    price_cut=phi * (_C0(TYP['m0_net']) - _Kc)) for phi in (0.5, 0.7)}
R2['pass_through']['unit_costs'] = dict(C0_anchor=_C0(PT_M0A), C0_typical=_C0(TYP['m0_net']), K_full=_Kc,
                                        S_anchor=_C0(PT_M0A) - _Kc, S_typical=_C0(TYP['m0_net']) - _Kc)

# ---- B9. Pace bridge from the pre-commit central case to the round-2 central case (realized share by 2036)
def s2036(p_):
    return pace(p_, dM_c)[2036]['s']


_old, _new = PACE_PREVIOUS['central'], PACE['central']
FACT = {'success (varpi, disruption haircut)': (dict(varpi=_old['varpi'], haircut=_old['haircut']), dict(varpi=_new['varpi'], haircut=_new['haircut'])),
        'realized share bbar': (dict(bbar=_old['bbar']), dict(bbar=_new['bbar'])),
        'embedding time T_emb (= T_pb)': (dict(Temb=_old['Temb'], Tpb=_old['Tpb']), dict(Temb=_new['Temb'], Tpb=_new['Tpb']))}


def _shapley(F):
    import itertools
    names = list(F)
    val = lambda S: s2036(dict(_old, **{kk: vv for nm in S for kk, vv in F[nm][1].items()}))
    sh = {nm: 0.0 for nm in names}
    perms = list(itertools.permutations(names))
    for pm in perms:
        S = []
        for nm in pm:
            sh[nm] += (val(S + [nm]) - val(S)) / len(perms)
            S.append(nm)
    return sh


_sh = _shapley(FACT)
_sh4 = _shapley({'varpi': FACT['success (varpi, disruption haircut)'][0:1] + (dict(varpi=_new['varpi']),),
                 'haircut removed': (dict(haircut=True), dict(haircut=False)),
                 'bbar': FACT['realized share bbar'], 'T_emb': FACT['embedding time T_emb (= T_pb)']})
_s_old, _s_new = s2036(_old), s2036(_new)
assert abs(_s_old + sum(_sh.values()) - _s_new) < 1e-12
_yield_model = _new['varpi'] * _new['bbar']
_yield_exec = 0.30 * 0.67 + 0.44 * 0.37                # executives panel: BCG win and worry zones, woe realizes nothing
_yield_mck = 0.30 * 0.67 + 0.70 * 0.37                 # McKinsey's "all others" (37%) for every non-successful attempt
R2['pace_bridge'] = dict(s2036_old=_s_old, s2036_new=_s_new, shapley=_sh, shapley4=_sh4,
                         old=dict(varpi=_old['varpi'], bbar=_old['bbar'], Temb=_old['Temb'], haircut=_old['haircut'],
                                  q=rates(_old)['q']),
                         new=dict(varpi=_new['varpi'], bbar=_new['bbar'], Temb=_new['Temb'], haircut=_new['haircut']),
                         yield_model=_yield_model, yield_exec_like_for_like=_yield_exec, yield_mckinsey_unconditional=_yield_mck,
                         s2036_at_exec_yield=s2036(dict(_new, varpi=_yield_exec / _new['bbar'])),
                         s2036_at_mck_yield=s2036(dict(_new, varpi=_yield_mck / _new['bbar'])),
                         s2036_bcg_win=s2036(PACE_BCG_WIN), R2036_bcg_win=central_path(pace_params=PACE_BCG_WIN)['2036']['R'],
                         failed_attempts_value='zero (s = bbar x embedded share; only embedded transitions realize value)')

# ---- B10. Decision weight v0 by discount rate (Supplement S2.2 example: m0 0.35, G 0.04, alpha 0.3, k 0; lambda set so
# that v0 = 10 at r = 10%). Small-share HJB: (r - G) v0 = m0 + ((1 - a)/a) (a lambda v0)^(1/(1 - a)).
_a, _m0e, _Ge = 0.3, 0.35, 0.04
_lam = ((10 * (0.10 - _Ge) - _m0e) * _a / (1 - _a)) ** (1 - _a) / (_a * 10)


def v0_at(r, lam=_lam):
    v_ = _m0e / (r - _Ge)
    for _ in range(100000):
        nv = (_m0e + (1 - _a) / _a * (_a * lam * v_) ** (1 / (1 - _a))) / (r - _Ge)
        if abs(nv - v_) < 1e-13:
            return nv
        v_ = nv
    return float('nan')


assert abs(v0_at(0.10) - 10) < 1e-9
R2['decision_weight'] = dict(lam=_lam, by_r={f'{r:.4f}': v0_at(r) for r in (0.0934, 0.10, 0.12, 0.15, 0.22, 0.31)},
                             example='S2.2: m0 0.35, G 0.04, alpha 0.3, k 0, lambda from v0 = 10 at r = 10%')

# ---- B11. Iso-score points and their value (Lemma lem:valuation2, persistent margin theta = 1, T = 10, G_inf = 3%)
def lemma5_value(g, m, r=R_WACC, T=10, Ginf=0.03):
    eta = (1 + g) / (1 + r)
    NT = sum(eta ** t_ for t_ in range(1, T + 1))
    return m * NT + m * eta ** T * (1 + Ginf) / (r - Ginf)


R2['iso_score'] = dict(r=R_WACC, T=10, G_inf=0.03, theta=1.0,
                       points=[dict(g=g_, m=0.40 - g_, score=0.40, multiple=lemma5_value(g_, 0.40 - g_))
                               for g_ in (0.30, 0.20, 0.10, 0.0)],
                       points_r10=[dict(g=g_, m=0.40 - g_, multiple=lemma5_value(g_, 0.40 - g_, r=0.10)) for g_ in (0.30, 0.20, 0.10, 0.0)])
# ---- D1/D2 (IM2-N8, F2-1): interest income and the change in deferred revenue in the cash-GAAP wedge of the top tail
# and the anchor (SEC frames retrieved 2 Nov 2026, data/v3_inputs/interest_income_deferred.json; matched by fiscal-year
# end). Rules: interest income = InvestmentIncomeInterest, else InvestmentIncomeInterestAndDividend, else
# InterestIncomeOperating (as code/estimate_v3.py, D1); missing elements are missing, not zero. Deferred revenue change:
# IncreaseDecreaseInContractWithCustomerLiability (CCL) or IncreaseDecreaseInDeferredRevenue (DR); when a firm-year
# reports both and they agree within 1% they are one line under two tags (use one); when they differ they may be
# complementary lines (Palantir: customer deposits and deferred revenue) or overlapping, so the central reading takes CCL
# (the ASC 606 line) and the upper reading their sum; both are reported.
_IIJ = json.load(open(os.path.join(BASE, 'data', 'v3_inputs', 'interest_income_deferred.json')))
_II_ORDER = ['InvestmentIncomeInterest', 'InvestmentIncomeInterestAndDividend', 'InterestIncomeOperating']


def _sec(cik, fy):
    e = _IIJ.get(str(int(cik)), {}).get(str(fy)[:10], {})
    ii = next((float(e[k_]) for k_ in _II_ORDER if e.get(k_) is not None), np.nan)
    a, b = e.get('IncreaseDecreaseInContractWithCustomerLiability'), e.get('IncreaseDecreaseInDeferredRevenue')
    if a is None and b is None:
        return ii, np.nan, np.nan, ''
    if a is None or b is None:
        v_ = float(a if a is not None else b)
        return ii, v_, v_, 'one element'
    if abs(a - b) <= 0.01 * max(abs(a), abs(b), 1.0):
        return ii, float(a), float(a), 'both, equal'
    return ii, float(a), float(a) + float(b), 'both, differ'


_W = _full.copy()
_sx = [_sec(c_, f_) for c_, f_ in zip(_W.cik, _W.fy_end)]
_W['ii'], _W['ddr'], _W['ddr_hi'], _W['ddr_rule'] = zip(*_sx)
_W['t_stat'] = np.where(pd.to_datetime(_W.fy_end) < pd.Timestamp('2018-01-01'), 0.35, 0.21)
_W['wedge'] = _W.m_fcf_sbc - _W.m_op
_W['ddr_s'], _W['ddr_hi_s'] = _W.ddr / _W.rev, _W.ddr_hi / _W.rev
_W['ii_s'] = _W.ii * (1 - _W.t_stat) / _W.rev
_W['R'] = _W.g + _W.m_fcf_sbc


def _wedge_stats(x):
    v_ = x[x.ddr.notna()]
    vi = x[x.ddr.notna() & x.ii.notna()]
    md = lambda s_: float(s_.median()) if len(s_) else float('nan')
    return dict(n=int(len(x)), wedge=md(x.wedge), n_ddr=int(len(v_)), wedge_on_ddr=md(v_.wedge), ddr=md(v_.ddr_s),
                wedge_less_ddr=md(v_.wedge - v_.ddr_s), wedge_less_ddr_hi=md(v_.wedge - v_.ddr_hi_s),
                n_ddr_ii=int(len(vi)), wedge_on_both=md(vi.wedge), ii=md(vi.ii_s), wedge_less_ddr_ii=md(vi.wedge - vi.ddr_s - vi.ii_s))


_tail = {}
for per in ('2010-15', '2016-19', '2020-22', '2023-25'):
    x = _W[_W.period == per]
    _tail[per] = _wedge_stats(x[x.R >= x.R.quantile(.95)]) | dict(all_firms=_wedge_stats(x))
_anc = _W.merge(pd.DataFrame(_av['E1']['firm_years'])[['cik', 'year']], on=['cik', 'year'])
assert len(_anc) == anchor['n']
_spot = _anc[['name', 'year', 'wedge', 'ddr_s', 'ddr_hi_s', 'ddr_rule', 'ii_s']].assign(
    **{c_: lambda z, c_=c_: z[c_].astype(float) for c_ in ('wedge', 'ddr_s', 'ddr_hi_s', 'ii_s')})
# deferred-revenue intensity k_def = change in deferred revenue per dollar of new revenue (B8), 2023-25, revenue growing
_kd = _W[(_W.period == '2023-25') & (_W.rev > _W.rev_lag) & _W.ddr.notna()]
_kd = (_kd.ddr / (_kd.rev - _kd.rev_lag))
_cov = dict(firm_years=int(len(_W)), ii=int(_W.ii.notna().sum()), ii_primary=int(sum(
    _IIJ.get(str(int(c_)), {}).get(str(f_)[:10], {}).get('InvestmentIncomeInterest') is not None for c_, f_ in zip(_W.cik, _W.fy_end))),
            ddr=int(_W.ddr.notna().sum()), both_differ=int((_W.ddr_rule == 'both, differ').sum()),
            both_equal=int((_W.ddr_rule == 'both, equal').sum()))
R2['wedge'] = dict(top_tail=_tail, anchor=_wedge_stats(_anc), anchor_spot=_spot.to_dict(orient='records'), coverage=_cov,
                   k_def=dict(median=float(_kd.median()), p25=float(_kd.quantile(.25)), p75=float(_kd.quantile(.75)), n=int(len(_kd))),
                   G_star_at_kdef={c: (1 - CEIL[c]['base']) / (1 + float(_kd.median())) for c in ('favorable', 'central', 'conservative')},
                   rules='interest income: InvestmentIncomeInterest > InvestmentIncomeInterestAndDividend > InterestIncomeOperating; '
                         'deferred revenue: one element; both equal -> one; both differ -> CCL (central) or sum (upper)')
# D1: anchor sensitivity net of after-tax interest income (only firm-years reporting interest income)
_ai = _anc[_anc.ii.notna()]
_m0n_ii = (_ai.m_fcf_sbc - _ai.ii_s + (1 - TAU) * ((_ai.sm / _ai.rev).fillna(0) - MAINT_BASE).clip(lower=0)
           + _ai.capex_int.fillna(0))
_m0u_ii = _ai.m_fcf_sbc - _ai.ii_s + (1 - TAU) * (_ai.sm / _ai.rev).fillna(0) + _ai.capex_int.fillna(0)
_m0n_same = (_ai.m_fcf_sbc + (1 - TAU) * ((_ai.sm / _ai.rev).fillna(0) - MAINT_BASE).clip(lower=0) + _ai.capex_int.fillna(0))
R2['anchor_interest'] = dict(n_with_ii=int(len(_ai)), n=int(len(_anc)), ii_median=float(_ai.ii_s.median()) if len(_ai) else None,
                             m0_net_same_firm_years=float(_m0n_same.median()) if len(_ai) else None,
                             m0_net_less_ii=float(_m0n_ii.median()) if len(_ai) else None,
                             m0_ub_less_ii=float(_m0u_ii.median()) if len(_ai) else None,
                             path2036_net_less_ii=(float(_m0n_ii.median()) * (1 - CPc['2036']['s']) + CPc['2036']['s'] * CPc['2036']['target'] + G25) if len(_ai) else None,
                             firms_with_ii=sorted(_ai.name.unique().tolist()))

out['r2'] = R2

# ==============================================================================================================
# ROUND 3 REVISION (2 Nov 2026; outside reviews, notes/reviews/paper1_v3/author_reviews/*/issue_log.md; change log
# notes/r3_code_changes.md). Everything below is written to out['r3'] and read by code/paper1_macros.py. New keys only:
# no value computed above changes (checked against the committed JSON when this block was added).
# ==============================================================================================================
R3 = {}

# ---- GPT-M1. The frontier-slope mapping through the sample's growth distribution. Under a common frontier
# m* = m0 - (Delta/ell)^beta (k = 0, window read as excess growth) every firm-year sits on m*, so the cone statistic is
# Psi_chi(g0) = m*(q_chi(g0)), m* at the (1 - chi)-quantile of growth among firm-years growing at least g0. Its
# least-squares slope on the estimator's grid g0 = 0, 0.05, ..., W is -S_F / ell^beta, with S_F that slope at ell = 1
# computed on the E1 firm-years of each basis exactly as code/estimate_v3.py cone_mat does (type-7 quantiles, chi = 0.90,
# cells of at least 30 firm-years). A measured slope -b therefore implies ell^beta = S_F / b and a steepest frontier slope
# at Delta = W of beta W^(beta-1) b / S_F: the multiplier beta W^(beta-1) / S_F depends on alpha and on the growth
# distribution, not on b. It replaces, for the text, the approximation (beta+1)(beta+2)/6 of block ell_psi, which assumes
# q_chi(g0) = g0 (kept unchanged above for the record).
_GRID_CONE = np.round(np.arange(0, 0.6 + 1e-9, 0.05), 2)


def _cone_S(gv, beta, chi=0.90, W=0.6):
    gr = _GRID_CONE[_GRID_CONE <= W + 1e-9]
    o = np.sort(gv)                                     # cells: firm-years with g >= g0 (negative growth enters no cell)
    cells = [np.sort(-(o[o >= g0]) ** beta) for g0 in gr]
    assert min(len(c_) for c_ in cells) >= 30, 'a cone cell has fewer than 30 firm-years'
    c = np.array([np.quantile(c_, chi) for c_ in cells])
    return -float(np.polyfit(gr, c, 1)[0]), [int(len(c_)) for c_ in cells]


_cone = {}
for _b, _col in (('op', 'm_op'), ('cash', 'm_fcf_sbc')):
    _gv = _full.loc[_full.g.notna() & _full[_col].notna(), 'g'].to_numpy(float)
    _bb = abs(FS3['central'][_b]['E1']['est'])
    _rows_b = {}
    for _al in (0.25, 0.30, 0.35, 0.45):
        _be = 1 / _al
        _S, _cells = _cone_S(_gv, _be)
        _mult = _be * 0.6 ** (_be - 1) / _S
        _rows_b[f'{_al:.2f}'] = dict(S_F=_S, ell=(_S / _bb) ** _al, multiplier=_mult, steepest=_mult * _bb,
                                    multiplier_ls_identity=out['ell_psi'][f'E1_{_b}_w60'][f'{_al:.2f}']['steepest'] / _bb,
                                    multiplier_approx=(_be + 1) * (_be + 2) / 6)
    _cone[_b] = dict(b=_bb, n=int(len(_gv)), W=0.6, chi=0.90, cells=_cells, by_alpha=_rows_b)
_mults = [_cone[_b]['by_alpha'][_al]['multiplier'] for _b in _cone for _al in ('0.25', '0.45')]
R3['ell_psi_cone'] = dict(by_basis=_cone, multiplier_range=[min(_mults), max(_mults)],
                          note='steepest slope = multiplier x |Psi slope|; multiplier = beta W^(beta-1)/S_F at the E1 growth '
                               'values of each basis (GPT-M1)')

# ---- GPT-M2. psi substituted into the margin is a tax-PV-equivalent; on a steady growth path at g the period cash
# deduction per dollar of current investment is psi_T evaluated at g (half-year convention, the same schedule as psi_T)
R3['psi_period_cash'] = dict(
    psi15_at_g={f'{g_:.2f}': psi_T(15, r=g_) for g_ in (0.05, 0.10, 0.15, 0.30)},
    ceiling_k15_G30_loss_period_cash={f'{t:.2f}': (1 - psi_T(15, r=0.30) * t) * 1.5 * 0.30 for t in FC['tau']},
    ceiling_k15_G30_loss_pv={f'{t:.2f}': (1 - PSI['foreign_15y'] * t) * 1.5 * 0.30 for t in FC['tau']},
    note='period cash on a mature vintage history growing at G = 0.30; the PV-equivalent (psi_15 at r = 0.10) is the '
         'psi_sensitivity block')

# ---- GPT-M4. Exit value: what a five-year owner who sells recovers. PV at 0 of the net flows after year 5 is
# NPV - discounted cumulative cash at 5; capitalized at the same rate it is the value at year 5; the owner who sells
# rejects the program only if the sale recovers less than -cum_disc(5) / PV(after 5) of that value.
def _exit_value(pb):
    npv_, cd5, r_ = pb['npv_points_years'], pb['hold'][5]['cum_disc'], pb['r']
    cont = npv_ - cd5
    return dict(npv=npv_, cum_disc_5=cd5, pv0_after_5=cont, value_at_5=cont * (1 + r_) ** 5, r=r_,
                breakeven_recovery=(max(-cd5, 0.0) / cont) if cont > 0 else None)


R3['exit_value'] = {pc: _exit_value(R2['payback'][pc]) for pc in ('central', 'central_r10', 'fast', 'slow')}

# ---- GLM-M5. The PV ratio of gains to the dip counting only gains until the capped upper bound reaches the program
_Tdone = R2['payback']['central']['complete_years']
R3['payback_to_completion'] = dict(T=_Tdone, central=payback(CPc, PACE['central'], T=_Tdone))


# ---- GPT-4. The exact expected recurrence of the divisible program: wave w attempts min(c, U_{w-1}) of the unembedded
# mass U (c = rho T_par, the wave's capacity) and embeds q of it, U_w = U_{w-1} - q min(c, U_{w-1}). It equals the capped
# bound min(1, q c n) of pace() while U >= c and then approaches one geometrically, U_w = (1 - q) U_{w-1}, so the program
# is never embedded at a finite date; attempts (and the dip they cost) continue on the residual. Reported: the date of
# 99% embedded, and payback, NPV and the PV ratio with the exact recurrence (the printed values keep the bound).
def _exact_U(q_, c_, nmax):
    U = np.empty(nmax + 2)
    U[0] = 1.0
    for w_ in range(1, nmax + 2):
        U[w_] = U[w_ - 1] - q_ * min(c_, U[w_ - 1])
    return U


def exact_recurrence(path, pace_p, r=R_WACC, dt=1 / 365, T=200.0, share=0.99):
    m0A_ = path['m0A']
    dM = {int(h): path[h]['target'] - m0A_ for h in HZ}
    yrs = sorted(dM)
    rr = rates(pace_p)
    c_ = rr['rho'] * pace_p['Tpar']
    t = np.arange(0, T, dt)
    tR = t / rr['clock']
    n = np.where(tR < pace_p['Temb'], 0, np.floor((tR - pace_p['Temb']) / pace_p['Tpar'] + 1e-12) + 1).astype(int)
    U = _exact_U(rr['q'], c_, int(n.max()) + 1)
    emb = 1.0 - U[n]
    in_flight = np.minimum(c_, U[n]) / c_                              # attempts of the next wave, share of a full wave
    dm = np.interp(H0 + t, yrs, [dM[y] for y in yrs])
    gain = pace_p['bbar'] * emb * dm
    dip = rr['attempt_rate'] * pace_p['Tpb'] * dm * in_flight
    disc = (1 + r) ** (-t)
    cu, cd = np.cumsum(gain - dip) * dt, np.cumsum((gain - dip) * disc) * dt
    first = lambda m: float(t[np.argmax(m)]) if m.any() else None
    pv_gain, pv_dip = float(np.sum(gain * disc) * dt), float(np.sum(dip * disc) * dt)
    n_sh = int(np.argmax(1.0 - U >= share))
    n_full = math.ceil(1 / (rr['q'] * c_) - 1e-9)                       # waves at which the capped bound reaches one
    s_h = {h: pace_p['bbar'] * (1.0 - U[(lambda tr: 0 if tr < pace_p['Temb'] else
                                         math.floor((tr - pace_p['Temb']) / pace_p['Tpar'] + 1e-12) + 1)((int(h) - H0) / rr['clock'])])
           for h in HZ}
    return dict(payback_undiscounted=first((cu >= 0) & (np.cumsum(cu < 0) > 0)),
                payback_discounted=first((cd >= 0) & (np.cumsum(cd < 0) > 0)),
                npv_points_years=pv_gain - pv_dip, pv_gain=pv_gain, pv_dip=pv_dip, ratio=pv_gain / pv_dip,
                waves_to_share=n_sh, share=share, year_share=H0 + rr['clock'] * (pace_p['Temb'] + (n_sh - 1) * pace_p['Tpar']),
                waves_bound_full=n_full, year_bound_full=H0 + rr['clock'] * (pace_p['Temb'] + (n_full - 1) * pace_p['Tpar']),
                embedded_at_bound_full=float(1.0 - U[n_full]), realized_by_horizon=s_h,
                hold={yr: dict(cum=float(cu[int(round(yr / dt)) - 1]), cum_disc=float(cd[int(round(yr / dt)) - 1]))
                      for yr in (3, 5)}, r=r)


R3['exact_recurrence'] = {pc: exact_recurrence(central_path(pace_case=pc), PACE[pc]) for pc in ('slow', 'central', 'fast')}
R3['exact_recurrence']['central_r10'] = exact_recurrence(CPc, PACE['central'], r=0.10)
for _pc, _P in (('central', PL), ('fast', PH)):                         # the bound's dates are the ones pace() prints
    assert abs(R3['exact_recurrence'][_pc]['year_bound_full'] - _P['complete_year']) < 1e-9
assert abs(R3['exact_recurrence']['central']['year_bound_full'] - (H0 + R2['payback']['central']['complete_years'])) < 2 / 365
assert all(abs(R3['exact_recurrence']['central']['realized_by_horizon'][h] - CPc[h]['s']) < 1e-12 for h in HZ)

# ---- GLM-F1 / GPT-2. Shape of the decision weight v'(s) in the worked example of Section S2.2 (r 0.10, G 0.04, k 0,
# alpha 0.3, m0 0.35, v0 = 10, share cap 0.5): the upwind backward sweep of code/verify_theory.py (solve_hjb, copied so
# that this generator does not run the checks), with v' read from the HJB optimality condition
# v' = k + [((r - G) v/s - (m0 - kG)) / C_alpha]^(1-alpha) / ell(s) rather than by differencing. verify_theory.py checks
# 15l-15p recompute the profile with np.gradient on its own grid and compare it with the macros.
from scipy.optimize import minimize_scalar as _minsc


def _solve_hjb(m0_, k_, G_, r_, lam_, a_, sbar_, N=4000, smin=1e-9):
    half = N // 2
    u = np.concatenate([np.geomspace(smin, 0.5, half, endpoint=False), 1 - np.geomspace(0.5, 1e-9, N - half)])
    s = sbar_ * u
    v = np.zeros(N)
    sig = np.zeros(N)
    v[-1] = s[-1] * (m0_ - k_ * G_) / (r_ - G_)
    grid = np.concatenate([[0.0], np.geomspace(1e-10, 50, 240)])
    for i in range(N - 2, -1, -1):
        ell_i = lam_ * (1 - s[i] / sbar_)
        ds = s[i + 1] - s[i]

        def val(sg):
            D_ = ell_i * sg ** a_
            ai = s[i] * D_ / ds
            return (s[i] * (m0_ - sg - k_ * (G_ + D_)) + ai * v[i + 1]) / ((r_ - G_) + ai)

        vals = np.array([val(x) for x in grid])
        j = int(np.argmax(vals))
        lo, hi = grid[max(j - 1, 0)], grid[min(j + 1, len(grid) - 1)]
        res = _minsc(lambda x: -val(x), bounds=(lo, hi), method='bounded', options={'xatol': 1e-13})
        if -res.fun >= vals[j]:
            v[i], sig[i] = -res.fun, res.x
        else:
            v[i], sig[i] = vals[j], grid[j]
    return s, v, sig


_r_e, _G_e, _k_e, _sbar_e = 0.10, _Ge, 0.0, 0.5
assert _a == 0.3 and _m0e == 0.35 and _G_e == 0.04, 'worked example inputs of block B10 were overwritten'
_Ca = (1 - _a) * _a ** (_a / (1 - _a))
_sh, _vh, _sgh = _solve_hjb(_m0e, _k_e, _G_e, _r_e, _lam, _a, _sbar_e)
_z = _sh / _sbar_e
_ell = _lam * (1 - _z)
with np.errstate(divide='ignore', invalid='ignore'):
    _vp = _k_e + np.maximum((_r_e - _G_e) * _vh / _sh - (_m0e - _k_e * _G_e), 0.0) ** (1 - _a) / _Ca ** (1 - _a) / _ell
_at = lambda arr, zz: float(np.interp(zz, _z, arr))
_FR = (0.01, 0.10, 0.25, 0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.98, 0.99, 0.999, 0.9999)
_mask = (_z > 0.02) & (_z < 0.9999)
_imin = int(np.argmin(np.where(_mask, _vp, np.inf)))
R3['vprime_shape'] = dict(
    example='S2.2: r 0.10, G 0.04, k 0, alpha 0.3, m0 0.35, v0 = 10, sbar 0.5; N = 4000 grid of verify_theory.solve_hjb',
    lam=_lam, profile={f'{zz:g}': dict(vprime=_at(_vp, zz), v_over_s=_at(_vh / _sh, zz), sigma=_at(_sgh, zz)) for zz in _FR},
    min=dict(vprime=float(_vp[_imin]), at_share_of_cap=float(_z[_imin])),
    limit_never_spend=(_m0e - _k_e * _G_e) / (_r_e - _G_e),
    near_saturation=dict(lo=float(_vp[_imin]), hi=_at(_vp, 0.999), range='minimum to 99.9% of the cap'),
    max_vprime_minus_v_over_s=float(np.max((_vp - _vh / _sh)[_mask])))

# ---- GLM-M11 / GPT-22. The compute share's low credible bound per completed process. METR's run costs (0.4 to 1.1% of
# the human cost, rounded to 1%) are for successful runs only (code/data_part2/08_params.py keeps score_binarized == 1);
# at the 50% success rate of the time-horizon definition the cost per completed task is about twice that, 2%.
CC_LO_SUCCESSFUL_RUNS = 0.01
METR_SUCCESS_RATE = 0.50
CC_CREDIBLE = dict(lo=CC_LO_SUCCESSFUL_RUNS / METR_SUCCESS_RATE, lo_successful_runs=CC_LO_SUCCESSFUL_RUNS,
                   success_rate=METR_SUCCESS_RATE, hi=CC_VALUE_TEST_CAP)
CC_CREDIBLE['G'] = {k_: G100_central(CC_CREDIBLE[k_]) for k_ in ('lo', 'lo_successful_runs', 'hi')}
assert f"{CC_CREDIBLE['lo']:.2f}" in out['cc_sensitivity'] and abs(CC_CREDIBLE['hi'] - max(CC_GRID)) < 1e-12
R3['compute_credible'] = CC_CREDIBLE

# ---- GPT-26. The execution cases' inputs as used (wave length T_par and the rest), for the parameter table
R3['pace_params'] = {pc: dict(PACE[pc]) for pc in ('slow', 'central', 'fast')}

out['r3'] = R3

def rng(t):
    a, b = int(np.floor(100 * t[0] + 0.5)), int(np.floor(100 * t[1] + 0.5))
    if a == b:
        return f"{a}"
    return f"${a}$ to {b}" if a < 0 else f"{a}--{b}"


def rng0(t):
    a, b = int(np.floor(100 * t[0] + 0.5)), int(np.floor(100 * t[1] + 0.5))
    return f"{a}" if a == b else f"{a}--{b}"


iq = lambda v: rng((v[0], v[2]))


def dipr(dp):
    lo, hi = sorted(dp)
    f1 = lambda x: f"{100 * x:.1f}".replace('.0', '') if abs(100 * x) < 1e-9 else f"{100 * x:.1f}"
    return f"{f1(lo)}" if abs(lo - hi) < 5e-4 else f"{f1(lo)}--{f1(hi)}"
A = anchor
_rr = lambda dd: f"{int(np.floor(100 * min(dd.values()) + 0.5))}--{int(np.floor(100 * max(dd.values()) + 0.5))}"
pt = lambda x: f"{int(np.floor(100 * x + 0.5))}"                 # points, rounded half up
pt1 = lambda x: f"{np.floor(1000 * x + 0.5) / 10:.1f}"
sgn = lambda x: ('$-$' + pt(x)[1:]) if pt(x).startswith('-') else pt(x)


def ci_txt(bl, key):
    lo, hi = bl[key]['ci90']
    f = lambda x: ('$-$' if x < 0 else '$+$') + f"{abs(np.floor(1000 * x + 0.5) / 10):.1f}"
    return f"[{f(lo)}, {f(hi)}]"


B0 = ANCHOR_BOOT[ANCHOR_CENTRAL]
AI_ = R2['anchor_interval']
ivt = lambda iv: f"[{pt(iv[0])}, {pt(iv[1])}]"
rows = [f"2025 (anchor) & -- & -- & {pt(A['m0_net'][1])} {ivt(AI_['net']['m0A']['ci90'])} & {pt(A['m0_net'][1] + G25)} & "
        f"{pt(A['m0_ub'][1] + G25)} & {pt(A['m0_lb'][1] + G25)} & -- \\\\"]
for h in HZ:
    n_, u, l_ = CP['net'][h], CP['ub'][h], CP['lb'][h]
    rows.append(f"{h} & {pt(n_['s'])} & {pt(n_['target'])} & {pt(n_['m0'])} & {pt(n_['R'])} {ivt(AI_['net']['path'][h]['ci90_joint'])} & "
                f"{pt(u['R'])} {ivt(AI_['ub']['path'][h]['ci90_joint'])} & {pt(l_['R'])} {ivt(AI_['lb']['path'][h]['ci90_joint'])} & "
                f"{pt1(n_['dip']) if n_['running'] else '0'} \\\\")
srow = []
lab = {'E1': 'E1, calibration rule (central)', 'E1all': 'E1, every firm-year of the tail', 'E2': 'E2, organic',
       'E2imp4': 'E2 plus imputed, $M=4$', 'E2imp8': 'E2 plus imputed, $M=8$'}
for nm in [ANCHOR_CENTRAL] + ANCHOR_SENS:
    an, bt = ANCHORS[nm], ANCHOR_BOOT[nm]
    srow.append(f"{lab[nm]} & {an['n']} ({an['n_firms']}) & {pt(an['m0_net'][1])} & {pt(an['m0_ub'][1])} & "
                f"{sgn(an['Pi_ub'][1])} {ci_txt(bt, 'Pi_ub_med')} & {pt(an['Pi_lb'][1])} {ci_txt(bt, 'Pi_lb_med')} & "
                f"{pt(CP_ANCHOR[nm]['net']['2036']['R'])} & {pt(CP_ANCHOR[nm]['ub']['2036']['R'])} / {pt(CP_ANCHOR[nm]['lb']['2036']['R'])} \\\\")
tab = r"""\begin{table}[t]\centering\small
\caption{Central path of the maximal Rule-of-40 score of a top-tail asset-light firm, at full cost and attainable pace (free-cash-flow-after-SBC basis, $X=1$, output prices fixed), with 90\% anchor-sampling intervals}\label{tab:calib}
\resizebox{\textwidth}{!}{\begin{tabular}{lrrrrrrr}\toprule
 & \multicolumn{2}{c}{Program} & \multicolumn{2}{c}{Maintenance-netted (central)} & All S\&M buys growth & None buys growth & \\\cmidrule(lr){2-3}\cmidrule(lr){4-5}
Horizon & Realized $\bar b\,\mathcal E$ & Target $m_{0F}$ & $m_0$ & $R^*=R_\infty$ & $R_\infty$ (bound) & $R_\infty$ (bound) & Dip\\\midrule
""" + '\n'.join(rows) + r"""
\addlinespace\multicolumn{8}{l}{\emph{Anchor sample: 2025 medians and the 2036 central score}}\\
 & Firm-years (firms) & $m_0$, netted & $m_0$, all & $\Pi$, all buys growth & $\Pi$, none buys growth & 2036, netted & 2036, all / none\\\midrule
""" + '\n'.join(srow) + r"""
\bottomrule\end{tabular}}
\par\vspace{2pt}\footnotesize\raggedright Notes: Percentage points, rounded half up; brackets: 90\% firm-cluster bootstrap intervals from the anchor's sampling error (""" + f"{AI_['B']}" + r""" draws of the anchor block, intercept, market growth and maintenance base redrawn together; the program and the target are held fixed). The 2025 row inverts the model for the median of the """ + f"{A['n']}" + r""" firm-years of the audited sample at or above the 95th percentile of the 2023--25 cash score, without acquisition-affected firm-years (the calibration rule; Section~\ref{sec:empirics-anchor}): on the after-tax cash basis $m_0=m+(1-\tau)\sigma+kg$ with $\tau=""" + f"{TAU:g}" + r"""$, capital treated as not deductible ($\psi=0$). Growth spend $\sigma$ is the selling-and-marketing share in excess of the maintenance level of """ + f"{pt1(MAINT_BASE)}" + r"""\% of revenue (the median share of firm-years growing at or below the year median, Section~\ref{sec:empirics}; central), the whole share (all buys growth) or zero (none does); market growth at the anchor's median growth of """ + f"{pt1(G25)}" + r"""\%. Later rows: the central path, a scenario, not a forecast. The intercept moves toward the central full-cost margin term $m_{0F}$ at each horizon's compute share, $m_0=m_{0A}+\bar b\,\mathcal E\,(m_{0F}-m_{0A})$, with $\bar b\,\mathcal E$ the share of the program's benefits realized by the horizon under central execution (the upper bound of \autoref{prop:expected}(e)); $R_\infty=m_0+(1-k)G$ (\autoref{prop:optimum}) with $k=0$ and $G$ held at the anchor's median growth. The path reports the durable score on every basis; the transient surplus enters Table~\ref{tab:tornado}. Dip: the cost of the transitions in flight for a firm still transforming, central basis. Lower panel: medians of the intercept and of the surplus $\Pi=R-R_\infty$ with 90\% firm-cluster bootstrap intervals, and the 2036 central path from each sample's median intercept.
\end{table}"""
open(f'{BASE}/sections/tables/tab_calib.tex', 'w').write(tab)

# Tornado (2036 and 2028), sorted by swing
def tornado_tex(h):
    T = TORNADO[h]
    lines = [f"{r['label']} & {pt(r['low'])} & {pt(r['high'])} & {pt(r['high'] - r['low'])} \\\\" for r in T['rows']]
    return lines, T['reference']


tl36, ref36 = tornado_tex('2036')
tl28, ref28 = tornado_tex('2028')
tabt = r"""\begin{table}[t]\centering\small
\caption{One-at-a-time sensitivity of the central maximal score (tornado), 2028 and 2036}\label{tab:tornado}
\begin{tabular}{@{}p{0.62\linewidth}rrr@{}}\toprule
Input moved to the ends of its range & Low & High & Swing\\\midrule
\multicolumn{4}{@{}l}{\emph{2036; central path """ + pt(ref36) + r"""}}\\
""" + '\n'.join(tl36) + r"""
\addlinespace\multicolumn{4}{@{}l}{\emph{2028; central path """ + pt(ref28) + r"""}}\\
""" + '\n'.join(tl28) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: Points. Each row moves one input from the central path of Table~\ref{tab:calib} (maintenance-netted basis, $k=0$, central execution, the central full-cost target, fixed prices, $\alpha=""" + f"{ALPHA_C:g}" + r"""$) to the ends of its range, holding the others at their central values; rows sorted by swing. Ranges: anchor quartiles (netted basis); market growth $G$ over the interquartile range of revenue growth of the core firm-years of 2023--25 (""" + f"{pt1(G_BAND[0])}--{pt1(G_BAND[1])}" + r"""\%, own data); for the surplus row, the upper-quartile firm-year under the upper bound on growth spend with pull $\mu$ and $\alpha$ at their ends (""" + '; '.join(f"{h}: $\\mu$ {HZ[h]['mu'][0]:g}--{HZ[h]['mu'][1]:g}" for h in HZ) + r"""); slow and fast execution of Section~\ref{sec:horizons-ranges}; the win zone of the transformation survey alone ($\varpi=0.30$) with the realized share of successful transformations; the conservative and favorable full-cost cases; pass-through at a rate $\varphi=0.7$ of all unit-cost savings, margins at the post-cut price; $k=0.5$ of capital per dollar of new revenue, not deductible ($\psi=0$), against the central $k=0$; the two bounds on growth spend; the four alternative anchor samples. One-sided rows compare one alternative with the central path. The surplus row adds the upper-quartile firm-year's transient surplus, which the median firm-year does not have, so both of its ends lie above the central path. All are scenario values.
\end{table}"""
open(f'{BASE}/sections/tables/tab_tornado.tex', 'w').write(tabt)

# Iso-score points and their value (round 2, B11 / IB2-N1): Lemma lem:valuation2 at r = 9.34%, T = 10, G_inf = 3%,
# persistent margin (theta = 1); no score-to-multiple mapping is estimated
IS = R2['iso_score']
tabi = r"""\begin{table}[t]\centering\small
\caption{Four firms on the same Rule-of-40 line are worth different revenue multiples (Lemma~\ref{lem:valuation2}, an analytical illustration)}\label{tab:isoscore}
\begin{tabular}{@{}rrrr@{}}\toprule
Growth $g$ (\%) & Margin $m$ (\%) & Rule-of-40 score & Value $V/S_0$ (times revenue)\\\midrule
""" + '\n'.join(f"{pt(p_['g'])} & {pt(p_['m'])} & {pt(p_['score'])} & {p_['multiple']:.1f}\\\\" for p_ in IS['points']) + r"""
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: $V/S_0=m\,\mathcal N_T(\eta)+m\,\eta^T\mathcal M_\infty$ with $\eta=(1+g)/(1+r)$, growth $g$ for $T=""" + f"{IS['T']}" + r"""$ years and """ + f"{pt(IS['G_inf'])}" + r"""\% thereafter, the current margin held throughout ($\theta=1$), and $r=""" + f"{100 * IS['r']:.2f}" + r"""\%$. Every row scores 40. The table is an implication of the lemma at stated inputs; the paper estimates no mapping from scores to market multiples.
\end{table}"""
open(f'{BASE}/sections/tables/tab_isoscore.tex', 'w').write(tabi)

# Pass-through reconciliation (lead-agent ruling 1, 2 Nov 2026): the central threshold under each reading of the
# pass-through scenario, at the central cost structure and 2025 prices (supplement-ready)
PTB = R2['pass_through']['by_phi']
_ptrows = [('Rate on all unit-cost savings (central): margin at the post-cut price, maintenance-netted anchor',
            'rate_phi_all_net_CENTRAL'),
           ('Same, anchor with all selling and marketing as growth spend', 'rate_phi_all_ub'),
           ('Same, anchor with no selling and marketing as growth spend', 'rate_phi_all_lb'),
           ('TYP', 'TYP'),
           ('Rate $\\varphi$ on the cost-of-revenue saving only, post-cut price', 'rate_phi_variable'),
           ("Referee's reading: rate $\\varphi(1-H)$, cost-of-revenue saving only, post-cut price", 'referee_rate_phi_1mH_variable'),
           ("Referee's reading with all savings (anchor with all selling and marketing)", 'referee_rate_phi_1mH_all_ub'),
           ('First version: share $\\varphi(1-H)$ of the cost-of-revenue saving lost at the old revenue', 'v2_code_variable_old_revenue')]
tabr = r"""\begin{table}[t]\centering\small
\caption{The 100-point growth threshold with pass-through, under each reading of the scenario (central cost structure, 2025 prices)}\label{tab:passthrough-recon}
\begin{tabular}{@{}p{0.66\linewidth}rr@{}}\toprule
Reading & $\varphi=0.5$ & $\varphi=0.7$\\\midrule
Fixed prices & \multicolumn{2}{c}{""" + f"{pt1(CEN_C['G100'])}" + r"""}\\
""" + '\n'.join((f"{lab} & {pt1(PTB['0.5'][k])} & {pt1(PTB['0.7'][k])}\\\\" if k != 'TYP' else
             "Rate on all unit-cost savings, saving of a typical \\$1--5 billion firm (its netted median intercept, "
             f"unit cost {pt(R2['pass_through']['unit_costs']['C0_typical'])}\\% of price) & "
             f"{pt1(R2['pass_through']['typical']['0.5']['G'])} & {pt1(R2['pass_through']['typical']['0.7']['G'])}\\\\")
            for lab, k in _ptrows) + r"""
\addlinespace Price cut, central reading (\% of today's price) & """ + f"{pt1(PTB['0.5']['price_cut_central'])} & {pt1(PTB['0.7']['price_cut_central'])}" + r"""\\
First-order elasticity $\varphi\,u/p$ of \autoref{lem:prices}, central reading & """ + f"{PTB['0.5']['elasticity_first_order_central']:.2f} & {PTB['0.7']['elasticity_first_order_central']:.2f}" + r"""\\
Dollar share kept with the volume response, $1-\varphi(1-H)$, $H=""" + f"{HHI:g}" + r"""$ & """ + f"{PTB['0.5']['dur_dollar_share']:.3f} & {PTB['0.7']['dur_dollar_share']:.3f}" + r"""\\
\bottomrule\end{tabular}
\par\vspace{2pt}\footnotesize\raggedright Notes: Percent a year; $G^*$ at which the ceiling reaches 100 with $k=0$. $\varphi$ is the industry pass-through rate, the share of a common unit-cost change that reaches the output price \citep{ganapati2020energy}. The central reading lets the price fall by $\varphi S$, with $S$ the firm's whole unit-cost saving from today's cost, $1-f-m_{0A}/(1-\tau)$, to the full-cost structure, and evaluates the margin share at the lower price, with fees proportional to price and the other costs fixed per unit (\autoref{lem:prices}(a): the elasticity is $\varphi u/p$, not $\varphi$). All savings are exposed because competition prices the full unit cost, the accountability floor and the costs of running AI included (\autoref{prop:entry}(d)). The share $1-\varphi(1-H)$ is the part of a common dollar saving that a Cournot firm keeps once its volume gain is counted (companion paper); with costs per unit the margin share does not depend on volume, so $H$ does not enter the score. Scenario values throughout.
\end{table}"""
open(f'{BASE}/sections/tables/tab_passthrough_recon.tex', 'w').write(tabr)

# Appendix Table tab:fullcost: every numeric cell written from FC and fullcost() (between markers in appendix_proofs.tex,
# where code/verify_theory.py check 20a reads it)
F = {c: fullcost(c) for c in CASES}
v3c = lambda key, fmt_: ' & '.join(fmt_(FC[key][i]) for i in range(3))
two = lambda x: f"{100 * x:.2f}"
g3 = lambda x: f"{x:g}"
FT = [
    r"\multicolumn{5}{@{}l}{\emph{Security, $c_{\mathrm{sec}}$}}\\",
    r"Security spending today, $c^{\rm sp}_0$ & " + v3c('s0', two) + r" & (a) survey of security officers, flagged\\",
    r"Control effectiveness $L_{\rm sec}$ & " + v3c('L0', g3) + r" & (d) controls remove " + ', '.join(f"{100 * (1 - math.exp(-x)):.0f}" for x in FC['L0']) + r"\% of loss\\",
    r"Exposure multiplier at full automation $\xi_{\rm exp}$ & " + v3c('Me', g3) + r" & (d) draft, write and transact rights\\",
    r"Risk cost $(c^{\rm sp}_0/L_{\rm sec})(1+L_{\rm sec}+\ln\xi_{\rm exp})$ & " + ' & '.join(two(F[c]['risk']) for c in CASES[:3]) + r" & Lemma~\ref{lem:fullcost}(b)\\",
    r"Post-quantum migration & " + ' & '.join(two(F[c]['pqc']) for c in CASES[:3]) + r" & (d) " + ', '.join(f"{100 * x:g}" for x in FC['phi_pqc']) + r"\% of IT spend a year; IT spend $c^{\rm sp}_0$ over the security share (a); windows in \citet{moody2026transition}; only public-sector estimates exist \citep{omb2024report}\\",
    r"AI compliance at \$1 billion of revenue & " + ' & '.join(two(F[c]['aic']) for c in CASES[:3]) + r" & vendor estimates for security attestation and ISO/IEC 42001, flagged; AI risk-framework staff, red-teaming and privacy assessments for 48 processes (d)\\",
    r"$c_{\mathrm{sec}}$ & " + ' & '.join(two(F[c]['c_sec']) for c in CASES[:3]) + r" & \\",
    r"\multicolumn{5}{@{}l}{\emph{Maintenance and revalidation, $c_{\mathrm{mnt}}$}}\\",
    r"Upkeep $\delta_M$ (share of builds a year) & " + v3c('delta_M', lambda x: f"{x:.2f}") + r" & (b) \citet{svanberg2024beyond}; software support fees\\",
    r"Revalidation cost per build $\varrho_{\rm rv}$ & " + v3c('kappa_rv', lambda x: f"{x:.2f}") + r" & (d)\\",
    r"Model-upgrade interval $T_{\mathrm{up}}$ (years) & " + v3c('T_up', lambda x: f"{x:.2f}") + r" & (c) vendor retirement dates\\",
    r"Builds $c_{\rm bld}$ & " + v3c('B', lambda x: f"{100 * x:.1f}") + r" & 48 processes at \$0.5 million (b), at \$1 billion of revenue (d)\\",
    r"$c_{\mathrm{mnt}}=(\delta_M+\varrho_{\rm rv}/T_{\mathrm{up}})c_{\rm bld}$ & " + ' & '.join(two(F[c]['c_mnt']) for c in CASES[:3]) + r" & Lemma~\ref{lem:fullcost}(a)\\",
    r"\multicolumn{5}{@{}l}{\emph{AI failure, $c_{\mathrm{err}}$}}\\",
    r"Error rate with no review $\bar u=\varepsilon^{\rm o}+\varepsilon^{\rm h}$ (per unit) & " + v3c('u_rev', lambda x: f"{x:.3f}") + r" & (d) scenario value: an omission rate per source sentence plus a hallucination rate per output sentence (favorable) or per summary or answer (central, conservative), which have different denominators, from source-grounded summarization and retrieval-based legal research; no review at full automation, Lemma~\ref{lem:fullcost}(c)\\",
    r"Loss per undetected error $L_{\rm err}$ (multiple of the unit's cost) & " + v3c('ell_e', g3) + r" & (d)\\",
    r"Errors and hallucination, $W_A\bar uL_{\rm err}$, with $W_A=" + f"{100 * FC['A_auto'][1]:g}" + r"\%$ (d) & " + ' & '.join(two(F[c]['c_err_e']) for c in CASES[:3]) + r" & Lemma~\ref{lem:fullcost}(c)\\",
    r"Misbehavior, $W_A\varepsilon^{\rm m}(1-d^{\rm m})L_{\rm mis}\mathbb E\min\{Y,\bar Y\}$ & " + ' & '.join(two(F[c]['c_err_m']) for c in CASES[:3]) + r" & $\varepsilon^{\rm m}$ " + ', '.join(f"{100 * x:g}" for x in FC['mu_m']) + r"\% per task and $L_{\rm mis}=" + f"{FC['ell_m'][1]:g}" + r"$, $\bar Y=" + f"{FC['Zcap'][1]:g}" + r"$ (d); recall $d^{\rm m}$ " + ', '.join(f"{x:g}" for x in FC['d_m']) + r" (a); tail index $p_Y$ " + ', '.join(f"{x:g}" for x in FC['p_tail']) + r" (b); Lemma~\ref{lem:fullcost}(d)\\",
    r"Common-mode failures, $\nu_{\rm cm}T_{\rm con}[W_{\rm cm}+H_{\rm cm}W_{\rm cm}^2/(2Y_{\rm fb})]$ & " + ' & '.join(two(F[c]['c_err_cm']) for c in CASES[:3]) + r" & " + ', '.join(f"{x:g}" for x in FC['nu_cm']) + r" day-long provider incidents a year (b); $W_{\rm cm}=W_A$, $W_{\rm cm}/(2Y_{\rm fb})=1$, one provider (d); Lemma~\ref{lem:fullcost}(e)\\",
    r"$c_{\mathrm{err}}$ & " + ' & '.join(two(F[c]['c_err']) for c in CASES[:3]) + r" & \\",
    r"\multicolumn{5}{@{}l}{\emph{Other, $c_{\mathrm{anc}}$}}\\",
    r"Management of AI spend (share of $c_c$) & " + v3c('s_fin', lambda x: f"{100 * x:g}") + r" & (d)\\",
    r"$c_{\mathrm{anc}}$, with fixed incident-response and legal costs & " + ' & '.join(two(F[c]['c_anc']) for c in CASES[:3]) + r" & (d); high-compute case " + two(F['high compute']['c_anc']) + r"\\",
    r"\midrule",
    r"$c_{\mathrm{full}}$ & " + ' & '.join(two(F[c]['c_full']) for c in CASES[:3]) + r" & high-compute case " + two(F['high compute']['c_full']) + r"\\",
]
_ap = f'{BASE}/sections/appendix_proofs.tex'
_src = open(_ap).read()
_B, _E = '% BEGIN ROWS GENERATED BY code/calibrate_horizons.py (tab:fullcost); do not edit by hand\n', '% END ROWS GENERATED\n'
if _B not in _src:                                   # first run: replace the hand-typed rows
    i0 = _src.index('\\multicolumn{5}{@{}l}{\\emph{Security, $c_{\\mathrm{sec}}$}}\\\\')
    i1 = _src.index('\\bottomrule', i0)
    _src = _src[:i0] + _B + _E + _src[i1:]
i0 = _src.index(_B) + len(_B)
i1 = _src.index(_E)
_src = _src[:i0] + '\n'.join(FT) + '\n' + _src[i1:]
open(_ap, 'w').write(_src)


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer, np.bool_)):
        return o.item()
    return o


json.dump(_clean(out), open(f'{BASE}/notes/calibration_results.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in anchor.items() if k != 'firms'}, indent=0))
print(anchor['firms'])
print('\n'.join(rows)); print('\n'.join(srow)); print('\n'.join(tl36))
for c, v in CEIL.items():
    print(f"ceiling {c:12s}: c_full={100 * v['c_full']:.2f} (mnt {100 * v['c_mnt']:.2f}, sec {100 * v['c_sec']:.2f}, "
          f"err {100 * v['c_err']:.2f}, anc {100 * v['c_anc']:.2f}); margin term {100 * v['base']:.2f} "
          f"(accountability only {100 * v['base_acc']:.2f}); G for 100: {100 * v['G100']:.2f}% ({100 * v['G100_acc']:.2f}%)")
for nm, P in [('central', PL), ('fast', PH)]:
    print(nm, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in P.items() if not isinstance(k, int)},
          {h: {kk: round(vv, 4) for kk, vv in P[h].items() if not isinstance(vv, bool)} for h in YEARS})
for b in ['upper_bound', 'lower_bound']:
    print(b, 'NEW', {h: (rng(v['0.0']['R']), rng(v['0.0']['Rinf']), rng(v['0.0']['Pi']), rng(v['0.5']['R']),
                         rng(v['0.0']['R_net'])) for h, v in out[b].items()})
    print(b, 'OLD', {h: (rng(v['0.0']['R']), rng(v['0.0']['Rinf']), rng(v['0.0']['Pi']), rng(v['0.5']['R']))
                     for h, v in out['previous'][b].items()})
for name, v in var.items():
    print(name, {h: (round(v[h]['s'], 4), round(100 * v['m0'][h], 2), round(100 * v[h]['dip'], 2)) for h in YEARS},
          'binding', v['binding'], 'rho', round(v['rho'], 4))
print('c_c sensitivity (G* full cost, accountability only):', {k: tuple(round(100 * x, 2) for x in v) for k, v in out['cc_sensitivity'].items()})
print('tau sensitivity:', {k: tuple(round(100 * x, 2) for x in v) for k, v in out['tau_sensitivity'].items()})
for h, cs in CEIL_H.items():
    print(f"ceiling {h}: " + "; ".join(f"{c} c_c {100 * v['c_c']:.1f}, margin term {100 * v['base']:.2f}, G* {100 * v['G100']:.2f}% "
                                       f"({100 * v['G100_acc']:.2f}%)" for c, v in cs.items()))
for phi in PHI:
    pt = out['pass_through'][f'{phi:.1f}']
    print(f"pass-through phi = {phi:g} (dur {pt['dur']:.3f}): central G* 2025 prices {100 * pt['ceiling']['central']['G100']:.2f}%, "
          + ", ".join(f"{h} {100 * pt['ceiling_by_horizon'][h]['central']['G100']:.2f}%" for h in CEIL_H)
          + "; upper bound R* " + ", ".join(f"{h} {rng(v['0.0']['R'])}" for h, v in pt['upper_bound'].items())
          + "; lower bound R* " + ", ".join(f"{h} {rng(v['0.0']['R'])}" for h, v in pt['lower_bound'].items()))
for nm, P in PREV.items():
    print('pace before the params commit', nm, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in P.items()
                                                if k in ('q', 'eff_rate', 'cross_years', 'complete_year')},
          {h: round(P[h]['s'], 4) for h in YEARS})
print('revealed pace reference (class c, panel_v3):', REVEALED_PACE['gaap_op_margin'])
print('c_err sensitivity (c_err, central G*):', {k: tuple(round(100 * x, 2) for x in v) for k, v in out['cerr_sensitivity'].items()})
print('psi:', {k: round(v, 4) for k, v in PSI.items()})
print('psi anchor m0_ub quartiles:', {k: [round(100 * x, 2) for x in v] for k, v in psi_out['anchor_m0_ub'].items()},
      'tau kg quartiles', [round(100 * x, 2) for x in psi_out['anchor_tau_kg']])
print('psi k=0.5 column (upper bound):', {k: {h: rng(r) for h, r in v.items()} for k, v in psi_out['k05_upper_bound'].items()})
print('psi ceiling loss at k=1.5, G=0.30:', {k: {t: round(100 * x, 2) for t, x in v.items()} for k, v in psi_out['ceiling_k15_G30_loss'].items()})
print('a_min sensitivity:', {k: tuple(round(100 * x, 2) for x in v) for k, v in out['amin_sensitivity'].items()})
print(out['Lambda_rule1000'], out['lam_for_Pi'], out['rule1000_multiple'])
