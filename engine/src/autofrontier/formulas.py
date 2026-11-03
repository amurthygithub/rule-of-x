# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Every formula the engine uses, in one module.

Each docstring ends with a tag line that tools/traceability.py parses:

    Implements: <LaTeX labels> | Spec: <sections of notes/unified_model_spec.md> | Notes: <theory-notes section> | Status: <status>

Status is one of
  theory       the formula is as written in notes/theory_core_notes.md ("core") or notes/theory_ext_notes.md
               ("ext"), or in the tex the notes point to;
  spec         the spec states the formula and no theory note covers it yet (Sections 16 and 17);
  provisional  the spec states only a qualitative property and the engine chose a form; to be replaced
               when the theory lands.

Units: dollars per unit of work unless stated; volumes in units a year; time in years; rates a year.
Functions accept numpy arrays where that makes sense and never mutate their inputs.
"""
from __future__ import annotations

import math
from itertools import combinations
from typing import Callable, Sequence

import numpy as np
from scipy.optimize import brentq
from scipy.special import expit
from scipy.stats import norm

MODES: tuple[str, ...] = ("H", "O", "U", "A", "N")
H, O, U, A, N = range(5)
AI_MODES = (U, A, N)
NON_AI_MODES = (H, O)


def _a(x):
    return np.asarray(x, dtype=float)


# =================================================================================================
# 1. Part I objects (spec Section 1; sections/model.tex)
# =================================================================================================

def part1_constants(alpha: float) -> tuple[float, float]:
    """beta = 1/alpha and C_alpha = (1 - alpha) alpha^(alpha/(1 - alpha)).

    Implements: eq:constants | Spec: 1 | Notes: core 4.11 | Status: theory"""
    return 1.0 / alpha, (1.0 - alpha) * alpha ** (alpha / (1.0 - alpha))


def delta_star(ell, y, alpha):
    """Optimal excess growth (Part I Lemma prop:score) Delta* = ell^(1/(1-alpha)) [alpha (X - k)_+]^(alpha/(1-alpha)), y = X - k.

    Implements: eq:Dstar, prop:score | Spec: 1 | Notes: core 4.11 | Status: theory"""
    y = np.maximum(_a(y), 0.0)
    return _a(ell) ** (1.0 / (1.0 - alpha)) * (alpha * y) ** (alpha / (1.0 - alpha))


def sigma_star(ell, y, alpha):
    """Optimal growth spend (Part I Lemma prop:score) sigma* = [alpha ell (X - k)_+]^(1/(1-alpha)).

    Implements: eq:sigstar, prop:score | Spec: 1 | Notes: core 4.11 | Status: theory"""
    y = np.maximum(_a(y), 0.0)
    return (alpha * _a(ell) * y) ** (1.0 / (1.0 - alpha))


def R_star(m0, G, ell, X, k, alpha):
    """Maximal Rule-of-X score (Part I Lemma prop:score) R*_X = m0 + (X - k) G + C_alpha [ell (X - k)_+]^(1/(1-alpha)).

    Implements: eq:Rstar, prop:score | Spec: 1 | Notes: core 4.11 | Status: theory"""
    _, C = part1_constants(alpha)
    y = np.maximum(_a(X) - _a(k), 0.0)
    return _a(m0) + (_a(X) - _a(k)) * _a(G) + C * (_a(ell) * y) ** (1.0 / (1.0 - alpha))


def ell_from_growth(g, G, sigma, alpha, floor: float = 1e-4) -> float:
    """Calibrate the growth opportunity ell = lambda h by inverting g = G + ell sigma^alpha.

    Implements: eq:growth, ass:growth | Spec: 1 | Notes: core 4.11 | Status: theory"""
    sigma = max(float(sigma), 1e-9)
    return max((float(g) - float(G)) / sigma ** alpha, floor)


def growth_spend_split(sm_share, rd_share, rd_expansion_share, basis="netted", maint_base=0.2506) -> dict:
    """Growth spend sigma and the maintenance S&M cost line on an S&M basis (Paper 1 round 2, decisions 4 and 7):
    netted (central) sigma = max(sm - b_M, 0) + theta rd, maintenance min(sm, b_M); all sigma = sm + theta rd, maintenance
    0; none sigma = theta rd, maintenance sm. theta = rd_expansion_share.

    Implements: ass:playbook-calib, eq:fcf (m0 = m + sigma + k g) | Spec: 1, 2.2 | Notes: Paper 1 r2 decision 4 | Status: spec"""
    sm, rd, th = float(sm_share), float(rd_share), float(rd_expansion_share)
    if basis == "netted":
        m_M = min(sm, float(maint_base))
    elif basis == "all":
        m_M = 0.0
    elif basis == "none":
        m_M = sm
    else:
        raise ValueError(f"unknown S&M basis {basis}")
    return {"sigma": sm - m_M + th * rd, "sm_maint": m_M, "sm_growth": sm - m_M, "basis": basis}


def lambda_after_savings(ell, delta_sigma, alpha):
    """A proportional saving delta_sigma on the fixed bundle of growth activities raises the growth
    opportunity to ell (1 - delta_sigma)^(-alpha).

    Implements: prop:tasks-aggregate | Spec: 1, 9 | Notes: core 2 (growth activities), 4.11 | Status: theory"""
    return _a(ell) * (1.0 - np.clip(_a(delta_sigma), -0.95, 0.95)) ** (-alpha)


def gordon_v0(m0, G, k, ell, r, alpha) -> float | None:
    """Small-share revenue multiple v0: the smallest positive root of
    (r - G) v = m0 - k G + C_alpha [ell (v - k)_+]^(1/(1 - alpha)). None if no root exists.

    Implements: eq:gordon, prop:dynamic, cor:tasks-weights | Spec: 1 | Notes: core 4.11 | Status: theory"""
    if r <= G:
        return None
    _, C = part1_constants(alpha)
    e = 1.0 / (1.0 - alpha)

    def f(v):
        return (r - G) * v - (m0 - k * G) - C * (ell * max(v - k, 0.0)) ** e

    if f(0.0) >= 0:
        return None
    if ell <= 0:          # no demand pull: the Gordon multiple of the margin alone, (m0 - k G)/(r - G)
        return float((m0 - k * G) / (r - G))
    vmax = k + ((r - G) / (C * e * ell ** e)) ** (1.0 / (e - 1.0))   # f is concave; its maximum
    if f(vmax) < 0:
        return None
    return float(brentq(f, 0.0, vmax, xtol=1e-13))


def R_max(tau, c_c, f, a_min, X, k, G, psi=0.0, delta_K=0.0):
    """Full-automation ceiling (Part I cor:ceiling, revised: replacement capital at the same deduction rate psi)
    R_max = (1 - tau)(1 - c_c - f - a_min) - (1 - psi tau) delta_K k + [X - (1 - psi tau) k] G. The Rule-of-40 form
    eq:Rmax is X = 1, psi = 0 and delta_K = 0 (the engine's default); full expensing adds tau k G and replacement at
    delta_K subtracts (1 - psi tau) delta_K k (cor:ceiling(b)).

    Implements: cor:ceiling, eq:Rmax, cor:ext-floor | Spec: 1, 8 | Notes: ext 3.1 | Status: theory"""
    return (1.0 - tau) * (1.0 - c_c - f - a_min) - (1.0 - psi * tau) * delta_K * k + (X - (1.0 - psi * tau) * k) * G


def ceiling_growth_threshold(tau, c_c, f, a_min, X=1.0, k=0.0, psi=0.0, target=1.0) -> float:
    """Market growth G at which R_max reaches `target` (the 31 to 55 percent thresholds of spec 8.8).

    Implements: cor:ceiling | Spec: 8 | Notes: core 4.11 | Status: theory"""
    base = (1.0 - tau) * (1.0 - c_c - f - a_min)
    slope = X - (1.0 - psi * tau) * k
    return (target - base) / slope if slope > 0 else float("inf")


def entry_limit_score(X, G, r, k, rho=0.0):
    """Under free replication the score tends to X G + (r - G) k + rho.

    Implements: prop:entry, eq:Rentry | Spec: 1, 6 | Notes: ext 3.4 | Status: theory"""
    return X * G + (r - G) * k + rho


def passthrough_terms(m0, f, phi_ind, phi_extra=0.0) -> dict:
    """Pass-through of unit-cost savings, Part I round 2 (B1; code/calibrate_horizons.py pt_margin). phi is a pass-through
    RATE (the share of a common unit-cost change that reaches the price; Ganapati et al.), applied to every unit-cost
    saving the rivals make (Part I prop:entry(d)); the margin is computed at the post-cut price. Today's non-fee unit
    cost per dollar of price is C0 = 1 - f - m0 (the engine's intercept basis, taxes not separated; at least 0; above 1
    when the intercept is negative).
    The total rate combines the industry rate on replicated savings with an extra rate a scenario sets (an AI-native
    entrant): phi = 1 - (1 - phi_ind)(1 - phi_extra). To first order the margin keeps 1 - phi C0 of a replicated saving
    (phi C0 is the pass-through elasticity of Part I lem:prices at today's point) and 1 - phi_extra C0 of a saving no
    rival makes. The concentration HHI does not enter: 1 - phi_ind (1 - HHI) is the dollar-profit share
    (cor:ext-game-engine(a)), not a margin share.

    Implements: lem:prices, prop:entry(d), cor:priorities(iv) | Spec: 1, 9, 24.7 | Notes: Paper 1 r2 B1 | Status: theory"""
    C0 = max(1.0 - float(f) - float(m0), 0.0)
    phi = 1.0 - (1.0 - float(phi_ind)) * (1.0 - float(phi_extra))
    return {"C0": C0, "phi_ind": float(phi_ind), "phi_extra": float(phi_extra), "phi": phi, "elasticity": phi * C0,
            "keep_replicable": 1.0 - phi * C0, "keep_own": 1.0 - float(phi_extra) * C0}


def margin_after_passthrough(m0, f, S_saving, phi) -> dict:
    """Exact margin intercept after a unit-cost saving S (per dollar of today's price) of which the industry passes the
    rate phi to the price, Part I round 2 (B1): the price falls to 1 - phi S, fees stay proportional to price and the
    other unit costs are fixed per unit, so m0' = 1 - f - (C0 - S)/(1 - phi S) with C0 = 1 - f - m0. At phi = 0 it is
    m0 + S (fixed prices); to first order m0 + (1 - phi C0) S.

    Implements: lem:prices, prop:entry(d), cor:priorities(iv) | Spec: 1, 9 | Notes: Paper 1 r2 B1 | Status: theory"""
    C0 = 1.0 - float(f) - float(m0)
    p1 = 1.0 - float(phi) * float(S_saving)
    return {"m0_new": 1.0 - float(f) - (C0 - float(S_saving)) / p1, "price_cut": float(phi) * float(S_saving), "C0": C0}


def part1_delta_R(d_ch, d_cc, d_a, d_k, g_star, delta_K, sigma_star_, delta_sigma, X, k, dG, phi_e):
    """First-order change of R*_X: -(1 - phi_e)(dc_h + dc_c + da) - (g* + delta_K) dk + sigma* delta_sigma + (X - k) dG_i,
    with phi_e the pass-through elasticity of the unit-cost savings (passthrough_terms: rate x C0). Part I round 2 (B1)
    exposes every unit-cost saving, overhead included (prop:entry(d)), to the industry rate; at phi_e = 0 it is the
    fixed-price value.

    Implements: prop:tasks-aggregate, eq:dRdzeta, prop:entry(d) | Spec: 1, 9 | Notes: core 4.11; Paper 1 r2 B1 | Status: theory"""
    return (-(1 - phi_e) * (d_ch + d_cc + d_a) - (g_star + delta_K) * d_k + sigma_star_ * delta_sigma
            + (X - k) * dG)


# =================================================================================================
# 2. Unit costs by mode (spec 3, 5, 13.1, 18; core 4.1, 4.12; ext 3.1)
# =================================================================================================

def capital_recovery_factor(r, T):
    """a(r, T) = r / (1 - exp(-r T)), the discounted replacement for 1/T_A; tends to 1/T as r -> 0.

    Implements: ass:tasks-modes, def:ext-effcost | Spec: 3 | Notes: core 4.1, ext 3.1 | Status: theory"""
    r, T = _a(r), _a(T)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(r > 1e-12, r / (1.0 - np.exp(-r * T)), 1.0 / T)


def revalidation_factor(r, T_up):
    """Annual equivalent of a cost paid every T_up years: r / (exp(r T_up) - 1), tending to 1/T_up.

    Implements: ass:tasks-ancillary | Spec: 18.1 | Notes: core 4.12 | Status: theory"""
    r, T_up = _a(r), _a(T_up)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        return np.where(r > 1e-12, r / np.expm1(r * T_up), 1.0 / T_up)


def effective_wage(w_loaded, omega_h, tau):
    """Own-labor cost per hour net of the owner's altruism: w_hat = w0 (1 + tau_L) - omega_h / (1 - tau).
    The engine's wages are already loaded, so w_loaded = w0 (1 + tau_L).

    Implements: def:ext-effcost, eq:ext-wedges | Spec: 5 | Notes: ext 3.1 | Status: theory"""
    return _a(w_loaded) - _a(omega_h) / (1.0 - tau)


def own_compute_markup_threshold(G, psi, tau, k_c=3.3, L_srv=5.5):
    """Owning compute instead of renting it raises the cash ceiling iff the vendor markup upsilon_c exceeds
    [(1 - psi) tau s_srv + (1 - psi tau) s_srv L_srv G]/(1 - tau) (Part I rem:owncompute, after FT-3: growth and
    replacement servers take the same deduction rate psi), with k_c = s_srv L_srv the capital per dollar a year of
    compute (3.3 = 0.6 x 5.5 in Part I) and s_srv = k_c/L_srv. At psi = 1 (domestic servers under current law) the bar
    is s_srv L_srv G whatever the tax rate: 16.5 percent at G = 5 percent; at psi = 0 and tau = 0.18 it is 33 percent.

    Implements: rem:owncompute, cor:ceiling | Spec: 13.1, 24.4 | Notes: accounting 4.3 | Status: theory"""
    s_srv = float(k_c) / float(L_srv)
    return ((1.0 - psi) * tau * s_srv + (1.0 - psi * tau) * float(k_c) * float(G)) / (1.0 - tau)


def tax_wedge_capital(psi, tau):
    """Ups = (1 - psi tau)/(1 - tau), the after-tax wedge on AI capital and builds.

    Implements: eq:ext-wedges | Spec: 5 | Notes: ext 3.1 | Status: theory"""
    return (1.0 - psi * tau) / (1.0 - tau)


def X_hat(X, psi, tau, k):
    """X_hat = [X - (1 - psi tau) k]/(1 - tau), the weight of revenue effects in unit-cost dollars.

    Implements: prop:ext-customer | Spec: 5 | Notes: ext 3.1 | Status: theory"""
    return (X - (1.0 - psi * tau) * k) / (1.0 - tau)


def customer_penalty(Xh, delta_G, Delta_star, delta_lambda, S, v):
    """Per-unit customer penalty of customer-facing AI work: X_hat (delta_G + Delta* delta_lambda) S / v.

    Implements: prop:ext-customer | Spec: 5 | Notes: ext 3.1 | Status: theory"""
    return _a(Xh) * (_a(delta_G) + _a(Delta_star) * _a(delta_lambda)) * _a(S) / np.maximum(_a(v), 1e-12)


def cost_H(w, t):
    """In-house unit cost c(H) = w t.

    Implements: ass:tasks-modes, eq:tasks-cost | Spec: 3 | Notes: core 4.1 | Status: theory"""
    return _a(w) * _a(t)


def cost_O(p_O, kappa_O, w, t, zeta_O):
    """Outsourced unit cost c(O) = p_O + kappa_O w t + zeta_O.

    Implements: ass:tasks-modes, eq:tasks-cost | Spec: 3 | Notes: core 4.1 | Status: theory"""
    return _a(p_O) + _a(kappa_O) * _a(w) * _a(t) + _a(zeta_O)


def vendor_price(rho_O, w, t, delta_O, years):
    """Vendor price p_O = rho_O w t (1 - delta_O)^years: vendors adopt AI, so the price falls.

    Implements: ass:tasks-modes | Spec: 3 | Notes: core 4.5 (vendor decline path) | Status: provisional"""
    return _a(rho_O) * _a(w) * _a(t) * (1.0 - _a(delta_O)) ** _a(years)


def cost_U(w, t_U, pi_n_U):
    """Augmented unit cost c(U) = w t_U + pi n_U, with t_U = t / (1 + beta_U).

    Implements: ass:tasks-modes, prop:tasks-augment | Spec: 3 | Notes: core 4.1 | Status: theory"""
    return _a(w) * _a(t_U) + _a(pi_n_U)


def augment_hours(t, beta_U):
    """Augmented hours per unit t_U = t / (1 + beta_U).

    Implements: ass:tasks-modes | Spec: 3 | Notes: core 2 (beta_U = t/t_U - 1) | Status: theory"""
    return _a(t) / (1.0 + _a(beta_U))


def cost_N(L_N):
    """Elimination: no running cost, only the value loss L_N per unit.

    Implements: ass:tasks-modes | Spec: 3 | Notes: core 4.1 | Status: theory"""
    return _a(L_N)


def capital_charge(K, r, delta_K):
    """Annual capital charge per unit (r + delta_K) K, added to every mode's cost for mode choice.

    Implements: prop:tasks-capital | Spec: 13.1 | Notes: core 4.1, 4.8 | Status: theory"""
    return (_a(r) + _a(delta_K)) * _a(K)


def full_cost_A(pi_n, c_Q, capital, F_A, a, delta_M, C_reval, reval_factor, c_int, N_int, C_risk, v):
    """Full unit cost of automation for an activity that forms its own process:
    c(A) = pi n + c_Q + (r + delta_K) K + [F_A a + delta_M F_A + C_reval r/(e^{r T_up} - 1) + c_int N + C_risk] / v.
    With a = 1/T_A and r -> 0 this is eq:tasks-fullcost exactly. The same form gives c(U).

    Implements: prop:tasks-fullcost, eq:tasks-fullcost | Spec: 3, 18.1 | Notes: core 4.12 | Status: theory"""
    v = np.maximum(_a(v), 1e-12)
    fixed = (_a(F_A) * _a(a) + _a(delta_M) * _a(F_A) + _a(C_reval) * _a(reval_factor)
             + _a(c_int) * _a(N_int) + _a(C_risk))
    return _a(pi_n) + _a(c_Q) + _a(capital) + fixed / v


def automation_advantage(ct_nonai, ct_ai):
    """B_j = min over feasible non-AI modes of the effective cost - min over feasible AI modes; -inf when no
    AI mode is feasible. Inputs have np.inf for infeasible modes, last axis = modes.

    Implements: def:ext-effcost, eq:ext-B | Spec: 5 | Notes: ext 3.1 | Status: theory"""
    a = np.min(_a(ct_nonai), axis=-1)
    b = np.min(_a(ct_ai), axis=-1)
    with np.errstate(invalid="ignore"):
        return np.where(np.isfinite(b), a - b, -np.inf)


# =================================================================================================
# 3. Errors and review (spec 3, 4, 8.3; core 4.2)
# =================================================================================================

def raw_error_readiness(iota, e0, e1):
    """Raw AI error rate as a function of readiness, e(iota) = e1 + (e0 - e1)(1 - iota).

    Implements: prop:tasks-review, prop:tasks-readiness | Spec: 4 | Notes: core 4.2 | Status: theory"""
    return _a(e1) + (_a(e0) - _a(e1)) * (1.0 - np.clip(_a(iota), 0.0, 1.0))


def capability_error(d_eff, Hcal, b, form: str = "logistic"):
    """Error from the capability gap. Logistic in log task length (METR): e_cap = expit(b log2(d / Hcal)); constant
    hazard: e_cap = 1 - 2^(-d / Hcal). Both are 0.5 at the 50 percent horizon and 0 as capability goes to infinity.

    Implements: ass:ext-capability | Spec: 6 | Notes: ext 3.2; modern map change 4 | Status: provisional"""
    d, Hc = _a(d_eff), _a(Hcal)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(np.isinf(Hc), 0.0, d / np.maximum(Hc, 1e-300))
        if form == "constant_hazard":
            return 1.0 - np.power(2.0, -ratio)
        z = b * np.log2(np.maximum(ratio, 1e-300))
    return np.where(ratio <= 0, 0.0, expit(z))


def combine_errors(e_ctx, e_cap):
    """Raw error from missing context (readiness) and from the capability gap, 1 - (1 - e_ctx)(1 - e_cap).
    With unbounded capability it reduces to the core's e(iota).

    Implements: prop:tasks-review | Spec: 3, 4, 6 | Notes: core 4.2 composed with ext 3.2 | Status: provisional"""
    return 1.0 - (1.0 - _a(e_ctx)) * (1.0 - _a(e_cap))


def review_share(e, L, w_tR, qbar, xi_min, d=1.0):
    """Stakes-targeted review share xi* = min(1, max(xi_E, xi_R, xi_min)), with the economic term
    xi_E = exp(-w t_R / (d e L)), the reliability term xi_R = (1 - (1 - qbar)/e)/d and the regulatory floor.
    With detection rate d = 1 it is the core's formula; d < 1 is the modern map's ranked change 1.

    Implements: prop:tasks-review, eq:tasks-xi | Spec: 3, 5, 8.3, 23.1 | Notes: core 4.2; notes/modern_theory_map.md change 1 | Status: theory"""
    e = np.maximum(_a(e), 1e-12)
    L = np.maximum(_a(L), 1e-12)
    d = np.clip(_a(d), 1e-6, 1.0)
    xiE = np.exp(-_a(w_tR) / (d * e * L))
    xiR = (1.0 - (1.0 - _a(qbar)) / e) / d
    return np.clip(np.maximum(np.maximum(xiE, xiR), _a(xi_min)), 0.0, 1.0)


def quality_cost(xi, e, L, w_tR, d=1.0):
    """Review plus residual-error cost per unit, c_Q(xi) = w t_R xi + e L [1 - d xi (1 + ln(1/xi))]; c_Q(0) = e L.

    Implements: prop:tasks-review, ass:tasks-review | Spec: 3, 23.1 | Notes: core 4.2; modern map change 1 | Status: theory"""
    xi = np.clip(_a(xi), 0.0, 1.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        term = np.where(xi > 0, xi * (1.0 + np.log(1.0 / np.maximum(xi, 1e-300))), 0.0)
    return _a(w_tR) * xi + _a(e) * _a(L) * (1.0 - _a(d) * term)


def residual_error(e, xi, d=1.0):
    """Undetected error rate eps = e (1 - d xi*); the step's reliability is q(A) = 1 - eps.

    Implements: prop:tasks-review | Spec: 3, 23.1 | Notes: core 4.2; modern map change 1 | Status: theory"""
    return _a(e) * (1.0 - _a(d) * _a(xi))


def detection_threshold(e, qbar):
    """Detection rate below which no review share meets the reliability target: d* = 1 - (1 - qbar)/e. An
    activity with d < d* is not automatable.

    Implements: prop:tasks-review, prop:tasks-breakpoints | Spec: 8.3, 23.1 | Notes: modern map change 1 | Status: theory"""
    return np.maximum(1.0 - (1.0 - _a(qbar)) / np.maximum(_a(e), 1e-12), 0.0)


def augment_quality_error(e_H, task_type, u_decision, u_creation):
    """Error rate of augmented work: blended human-AI work underperforms on decision tasks where the AI is better
    and gains on creation tasks (Vaccaro et al. 2024): e_U = e_H (1 + u_decision) for decision tasks and
    e_H (1 - u_creation) for creation tasks.

    Implements: ass:tasks-modes, prop:tasks-augment | Spec: 3 | Notes: modern map change 2 | Status: provisional"""
    tt = np.asarray(task_type)
    return np.where(tt == "decision", _a(e_H) * (1 + u_decision), np.where(tt == "creation", _a(e_H) * (1 - u_creation), _a(e_H)))


# =================================================================================================
# 4. Activity breakpoints and the automation curve (spec 3, 8; core 4.3 to 4.5)
# =================================================================================================

def crossover_price(c0_alt, c0_A, n_alt, n_A):
    """Crossover inference price pi* = (c0(x) - c0(A)) / (n - n(x)) against alternative x; automate iff
    pi <= pi*. With several alternatives the engine takes the minimum. +inf if A never uses more inference
    and is cheaper; -inf if it never pays.

    Implements: prop:tasks-modes, prop:tasks-breakpoints | Spec: 8.1 | Notes: core 4.3 | Status: theory"""
    dn = _a(n_A) - _a(n_alt)
    gap = _a(c0_alt) - _a(c0_A)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(dn > 1e-15, gap / np.where(dn > 1e-15, dn, 1.0), np.where(gap >= 0, np.inf, -np.inf))


def crossover_date(pi0, pi_star, delta_pi):
    """With pi(t) = pi0 exp(-delta_pi t): t* = ln(pi0/pi*)/delta_pi; 0 if already crossed; inf if pi* <= 0.

    Implements: prop:tasks-curve | Spec: 6, 8.1 | Notes: core 4.4 | Status: theory"""
    ps = _a(pi_star)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.log(_a(pi0) / np.maximum(ps, 1e-300)) / _a(delta_pi)
    return np.where(ps <= 0, np.inf, np.maximum(t, 0.0))


def volume_threshold(F_fixed_annual, cbar, cvar):
    """v* = (annual fixed cost of automation) / (cbar - cvar); infinite when cbar <= cvar. With the
    fixed cost F_A a this is core 4.3; with run costs added it is prop:tasks-fullcost(c).

    Implements: prop:tasks-modes, prop:tasks-fullcost, prop:tasks-breakpoints | Spec: 8.2, 18 | Notes: core 4.3, 4.12 | Status: theory"""
    gap = _a(cbar) - _a(cvar)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(gap > 0, _a(F_fixed_annual) / np.where(gap > 0, gap, 1.0), np.inf)


def volume_threshold_multiplier(delta_M, T_A, C_reval, T_up, F_A):
    """Run costs multiply the volume threshold by 1 + delta_M T_A + C_reval T_A / (T_up F_A).

    Implements: prop:tasks-fullcost | Spec: 18.4 | Notes: core 4.12 | Status: theory"""
    return 1.0 + _a(delta_M) * _a(T_A) + _a(C_reval) * _a(T_A) / (_a(T_up) * np.maximum(_a(F_A), 1e-12))


def automation_curve(E, pi, pi_star):
    """Spend-weighted share automated at price pi: S_A(pi) = sum_j E_j 1{pi <= pi*_j} / sum_j E_j.

    Implements: prop:tasks-curve | Spec: 3(a) | Notes: core 4.4 | Status: theory"""
    E = _a(E)
    return float((E * (_a(pi) <= _a(pi_star))).sum() / max(E.sum(), 1e-12))


def vendor_window(c_VH, c_V0, n, ups_O, kappa_O_cH, zeta_O, c0_A, delta_pi) -> dict:
    """In-house automation window around the vendor's own AI switch: pi_V = (c_VH - c_V0)/n,
    pi+ = [(1 + ups) c_VH + kappa_O c(H) + zeta_O - c0(A)]/n, pi- from D(0), length ln(pi+/pi-)/delta_pi.

    Implements: prop:tasks-window | Spec: 3(a) | Notes: core 4.5 | Status: theory"""
    pi_V = (c_VH - c_V0) / n
    pi_p = ((1 + ups_O) * c_VH + kappa_O_cH + zeta_O - c0_A) / n
    D0 = (1 + ups_O) * c_V0 + kappa_O_cH + zeta_O - c0_A
    pi_m = 0.0 if D0 >= 0 else (-D0 / (ups_O * n) if ups_O > 0 else math.inf)
    if pi_m == 0.0 and pi_p > 0:
        length = math.inf
    elif 0 < pi_m < pi_p and math.isfinite(pi_m):
        length = math.log(pi_p / pi_m) / delta_pi
    else:
        length = 0.0
    return {"pi_V": pi_V, "pi_plus": pi_p, "pi_minus": pi_m, "window_years": length}


def bisect_root(f: Callable[[float], float], lo: float, hi: float, tol: float = 1e-7, it: int = 100):
    """Bisection used for the reliability threshold e* and the readiness thresholds iota*_j and iota*_p.
    Returns None when f has no sign change on [lo, hi].

    Implements: prop:tasks-breakpoints, prop:tasks-readiness | Spec: 8.3, 8.4 | Notes: core 4.3, 4.7 | Status: theory"""
    flo, fhi = f(lo), f(hi)
    if not (np.isfinite(flo) and np.isfinite(fhi)) or np.sign(flo) == np.sign(fhi):
        return None
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if np.sign(fm) == np.sign(flo):
            lo, flo = mid, fm
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


# =================================================================================================
# 5. Processes: handoffs, O-ring, all-or-nothing, readiness (spec 3(b), 4, 11; core 4.6, 4.7)
# =================================================================================================

def process_value(Z, u, edges, eMM, eAM, eMA, eAA, qM, qA, vL, Xi, crit, run_cost=None, c_td_edge=None,
                  risk_cost_fn=None, C_inc=None):
    """Annual value of automating the set Z of steps of a process (boolean mask over steps):
    W(Z) = sum_{j in Z} u_j + sum_e [eta(M,M) - eta(y_i, y_j)] + v_p L_p [Q(Z) - Q(empty)]
           + Xi_p [1{crit subset Z} - 1{crit empty}]
    minus the Section 18 terms: run costs of Z, technical debt c_cpl N_i N_j on automated edges and the
    process risk cost C_risk(sum_{j in Z} C_inc_j). u_j = v_j (c_M - c_A) per step.

    Implements: eq:tasks-process, ass:tasks-process, prop:tasks-complement, prop:tasks-fullcost | Spec: 3(b), 18 | Notes: core 4.6, 4.12 | Status: theory"""
    Z = np.asarray(Z, dtype=bool)
    val = float(np.sum(np.where(Z, u, 0.0)))
    for k, (i, j) in enumerate(edges):
        yi, yj = Z[i], Z[j]
        eta = eAA[k] if (yi and yj) else (eAM[k] if yi else (eMA[k] if yj else eMM[k]))
        val += eMM[k] - eta
        if c_td_edge is not None and yi and yj:
            val -= c_td_edge[k]
    Q = float(np.prod(np.where(Z, qA, qM)))
    val += vL * (Q - float(np.prod(qM)))
    crit = np.asarray(crit, dtype=bool)
    if crit.any():
        val += Xi * (1.0 if bool(np.all(Z[crit])) else 0.0)
    if run_cost is not None:
        val -= float(np.sum(np.where(Z, run_cost, 0.0)))
    if risk_cost_fn is not None and C_inc is not None:
        val -= risk_cost_fn(float(np.sum(np.where(Z, C_inc, 0.0))))
    return val


def subsets_mask(J: int) -> np.ndarray:
    """All 2^J boolean masks over J steps, as a (2^J, J) array (used for exact enumeration, J <= 15).

    Implements: prop:tasks-aon | Spec: 3(b) | Notes: core 4.6 (enumerate if J <= 15) | Status: theory"""
    idx = np.arange(2 ** J)[:, None]
    return ((idx >> np.arange(J)[None, :]) & 1).astype(bool)


def integration_dividends(u_all, coord, rel, Xi) -> dict:
    """Value of full integration split into the unit, coordination, reliability and overhead dividends.

    Implements: prop:tasks-integration, eq:tasks-premium | Spec: 3(b), Q4 | Notes: core 4.6 | Status: theory"""
    return {"unit": float(u_all), "coordination": float(coord), "reliability": float(rel), "overhead": float(Xi),
            "total": float(u_all + coord + rel + Xi)}


def oring_tolerance(qbar_p, J):
    """Per-step error tolerance 1 - qbar_p^(1/J) for a process reliability target qbar_p over J steps.

    Implements: lem:tasks-oring | Spec: 3 | Notes: core 4.6 | Status: theory"""
    return 1.0 - _a(qbar_p) ** (1.0 / _a(J))


def straight_through_bounds(xi):
    """Straight-through rate bounds: prod(1 - xi_j) <= STP <= min(1 - xi_j).

    Implements: lem:tasks-stp | Spec: 4 | Notes: core 4.7 | Status: theory"""
    x = 1.0 - _a(xi)
    return float(np.prod(x)), float(np.min(x)) if x.size else 1.0


def process_readiness(iotas, rule: str = "min") -> float:
    """Process readiness over the critical path: the weakest link (common stakes) or the product
    (independent stakes).

    Implements: lem:tasks-stp, prop:tasks-readiness | Spec: 4 | Notes: core 4.7 | Status: theory"""
    a = _a(iotas)
    if a.size == 0:
        return float("nan")
    return float(a.min() if rule == "min" else a.prod())


def readiness_index(sor, api, mdq, idr, n_systems, unstructured, weights: dict, n_ref: float = 3.0):
    """Operational readiness index from the spec's observable proxies, a weighted mean on [0, 1]; systems per
    process enter as 1 / (1 + (n - 1)/n_ref).

    Implements: - | Spec: 4 | Notes: none (the spec lists the proxies only) | Status: provisional"""
    sys_score = 1.0 / (1.0 + np.maximum(_a(n_systems) - 1.0, 0.0) / n_ref)
    parts = {"sor": _a(sor), "api": _a(api), "mdq": _a(mdq), "idr": _a(idr), "systems": sys_score,
             "unstructured": 1.0 - _a(unstructured)}
    tot = sum(weights.values())
    return np.clip(sum(weights[k] * parts[k] for k in weights) / tot, 0.0, 1.0)


def integration_cost(iota_from, iota_to, n_systems, cost_per_system, kappa=1.0):
    """Convex integration investment I(iota) = cost per system x systems x [f(iota_to) - f(iota_from)]_+ with
    f(iota) = iota/(1 - iota)^kappa (kappa = 1: the paper's iota/(1 - iota)); readiness near 1 is very costly.

    Implements: prop:tasks-readiness | Spec: 4 | Notes: core 4.7 (I_p convex); core example of Section 7 | Status: theory"""
    f = lambda x: np.clip(_a(x), 0, 0.995) / (1.0 - np.clip(_a(x), 0, 0.995)) ** kappa
    return _a(cost_per_system) * _a(n_systems) * np.maximum(f(iota_to) - f(iota_from), 0.0)


# =================================================================================================
# 6. Capital (spec 13.1; core 4.8)
# =================================================================================================

def capital_value_test(dc, dK, r, delta_K):
    """A switch adds value iff dc > (r + delta_K) dK, for any growth path.

    Implements: prop:tasks-capital | Spec: 13.1 | Notes: core 4.8 | Status: theory"""
    return _a(dc) > (_a(r) + _a(delta_K)) * _a(dK)


def cash_margin_change(v, dc, dK, g, delta_K, S):
    """Steady-state cash-margin change v [dc - (g + delta_K) dK] / S.

    Implements: prop:tasks-capital | Spec: 13.1 | Notes: core 4.8 | Status: theory"""
    return _a(v) * (_a(dc) - (_a(g) + _a(delta_K)) * _a(dK)) / _a(S)


def gaap_margin_change(v, dc, dK, delta_K, S):
    """Steady-state GAAP-margin change v [dc - delta_K dK] / S.

    Implements: prop:tasks-capital | Spec: 13.1 | Notes: core 4.8 | Status: theory"""
    return _a(v) * (_a(dc) - _a(delta_K) * _a(dK)) / _a(S)


# =================================================================================================
# 7. Transition, success, pilot (spec 13.2, 14.1; core 4.9)
# =================================================================================================

def undetected_failure_prob(T_par, T_det):
    """p_u = exp(-T_par / T_det): the chance a failure is still undetected when the parallel run ends.

    Implements: ass:tasks-transition | Spec: 13.2 | Notes: core 4.9 | Status: theory"""
    return np.exp(-_a(T_par) / np.maximum(_a(T_det), 1e-12))


def parallel_cost_flow(C_0, E_p, C_dup, omega_par, nu_rec):
    """Dual-running cost flow during the parallel run, C_par = omega_par C_0 + nu_rec E_p + C_dup.

    Implements: ass:tasks-transition | Spec: 13.2 | Notes: core 4.9 | Status: theory"""
    return _a(omega_par) * _a(C_0) + _a(nu_rec) * _a(E_p) + _a(C_dup)


def stranded_cost(C_disp, T_sev, u_d, C_brk):
    """Cash stranded cost C_str = (1 - u_d) T_sev C_disp + C_brk (severance net of redeployment, break fees).

    Implements: ass:tasks-transition | Spec: 13.2 | Notes: core 4.9 | Status: theory"""
    return (1.0 - _a(u_d)) * _a(T_sev) * _a(C_disp) + _a(C_brk)


def transition_npv(F, I, C_J, C_par, T_par, varpi, bbar, W, C_str, L_roll, T_det, T_h, r):
    """Risk-adjusted NPV of one transition with a linear ramp:
    NPV = -(F + I + C_J) - C_par A_r(T_par) + varpi bbar W S_r
          - e^{-r T_par} {[varpi + (1 - varpi) p_u] C_str + (1 - varpi) p_u L_roll},
    A_r(T) = (1 - e^{-rT})/r, S_r = int_0^T_par e^{-rt} t/T_par dt + [e^{-r T_par} - e^{-r T_h}]/r.

    Implements: prop:tasks-transition, eq:tasks-npv | Spec: 13.2, 14.1 | Notes: core 4.9 | Status: theory"""
    pu = math.exp(-T_par / T_det) if (T_det > 0 and T_par > 0) else (1.0 if T_par <= 0 else 0.0)
    if r > 0:
        Ar = (1 - math.exp(-r * T_par)) / r
        ramp_pv = (1 - math.exp(-r * T_par) * (1 + r * T_par)) / (r * r * T_par) if T_par > 0 else 0.0
        tail = (math.exp(-r * T_par) - math.exp(-r * T_h)) / r
    else:
        Ar, ramp_pv, tail = T_par, T_par / 2, T_h - T_par
    return (-(F + I + C_J) - C_par * Ar + varpi * bbar * W * (ramp_pv + tail)
            - math.exp(-r * T_par) * ((varpi + (1 - varpi) * pu) * C_str + (1 - varpi) * pu * L_roll))


def min_horizon(F, I, C_J, C_par, T_par, varpi, bbar, W, C_str, L_roll, T_det, ramp_mean=0.5):
    """Transition breakpoint: the minimum undiscounted horizon
    T_h* = (1 - rhobar) T_par + {F + I + C_J + C_par T_par + [varpi + (1 - varpi) p_u] C_str
           + (1 - varpi) p_u L_roll} / (varpi bbar W).

    Implements: prop:tasks-transition, prop:tasks-breakpoints | Spec: 13.2 | Notes: core 4.9 | Status: theory"""
    pu = float(undetected_failure_prob(T_par, T_det))
    return (1 - ramp_mean) * T_par + (F + I + C_J + C_par * T_par + (varpi + (1 - varpi) * pu) * C_str
                                      + (1 - varpi) * pu * L_roll) / max(varpi * bbar * W, 1e-12)


def payback_years(F, I, C_J, C_str, W, T_par, C_par, ramp_mean=0.5):
    """Payback under certain success, t_pay = (F + I + C_J + C_str)/W + T_par (1 - rhobar + C_par/W); the
    parallel run adds T_par (1 - rhobar + C_par/W).

    Implements: prop:tasks-transition | Spec: 13.2 | Notes: core 4.9 | Status: theory"""
    if W <= 0:
        return math.inf
    return (F + I + C_J + C_str) / W + T_par * (1 - ramp_mean + C_par / W)


def optimal_parallel_run(C_par, varpi, bbar, W, C_str, L_roll, T_det, ramp_mean=0.5):
    """Undiscounted optimal parallel run: c_hat = C_par + varpi bbar W (1 - rhobar),
    R = (1 - varpi)(C_str + L_roll); T_par* = T_det ln[R/(T_det c_hat)] if R > T_det c_hat, else 0.

    Implements: prop:tasks-transition, eq:tasks-tpar | Spec: 13.2 | Notes: core 4.9 | Status: theory"""
    chat = _a(C_par) + _a(varpi) * _a(bbar) * _a(W) * (1 - ramp_mean)
    R = (1 - _a(varpi)) * (_a(C_str) + _a(L_roll))
    Td = _a(T_det)
    with np.errstate(divide="ignore", invalid="ignore"):
        T = Td * np.log(np.maximum(R, 1e-300) / np.maximum(Td * chat, 1e-300))
    return np.where(R > Td * chat, np.maximum(T, 0.0), 0.0)


def score_path_flows(W, C_par, T_par, b, F, I, C_J, C_str, C_wo, T_A, S, years, basis="cash"):
    """Annual change of the Rule-of-40 score through one transition started at 0 (success path):
    flow(t) = b W t/T_par - C_par for t < T_par and b W after; cash subtracts F + I + C_J in year 1 and C_str in
    the year the parallel run ends; GAAP replaces F + I by the amortization F/T_A and adds the write-off C_wo.

    Implements: prop:tasks-scorepath | Spec: 13.2 | Notes: core 4.9 | Status: theory"""
    out = []
    for y in range(1, years + 1):
        lo, hi = y - 1.0, float(y)
        a, bnd = lo, min(hi, T_par)
        val = 0.0
        if T_par > 0 and bnd > a:
            val += b * W * (bnd ** 2 - a ** 2) / (2 * T_par) - C_par * (bnd - a)
        val += b * W * max(hi - max(lo, T_par), 0.0)
        if y == 1:
            val -= C_J + (F + I if basis == "cash" else 0.0)
        if lo <= T_par < hi:
            val -= C_str + (C_wo if basis == "gaap" else 0.0)
        if basis == "gaap":
            val -= F / T_A * max(0.0, min(hi, T_A) - lo)
        out.append(val / S)
    return np.array(out)


def activity_success_logit(iota, log_margin, regulated, a0, a_iota, a_H, a_R):
    """logit varpi_pj = a0 + a_iota iota_j + a_H ln(Hcal/dbar_j) - a_R 1{regulated}.

    Implements: lem:tasks-success, eq:tasks-success | Spec: 14.1 | Notes: core 4.9 | Status: theory"""
    return a0 + a_iota * _a(iota) + a_H * _a(log_margin) - a_R * _a(regulated)


def process_success_logit(exception_share, affected_fte, team, sponsor, c0, c_exc, c_fte, c_team, c_sponsor,
                          shift=0.0):
    """Logit of the process factor varpi^c_p: falls with the exception share and ln(1 + affected FTE/50),
    rises with team experience and sponsorship (both centered at 0.5); `shift` carries the past-record and
    learning terms.

    Implements: lem:tasks-success, eq:tasks-success | Spec: 14.1 | Notes: core 4.9 | Status: theory"""
    return (c0 - c_exc * _a(exception_share) - c_fte * np.log1p(np.maximum(_a(affected_fte), 0.0) / 50.0)
            + c_team * (_a(team) - 0.5) + c_sponsor * (_a(sponsor) - 0.5) + _a(shift))


def process_success(proc_logit, activity_logits) -> float:
    """varpi0_p = varpi^c_p prod_{j on the critical path} varpi_pj: success multiplies along the path, so
    complexity enters as a sum of hazards.

    Implements: lem:tasks-success | Spec: 14.1 | Notes: core 4.9 | Status: theory"""
    return float(expit(proc_logit) * np.prod(expit(_a(activity_logits))))


def pilot_value(varpi, Y_s, Y_f, F_pil, d=1.0) -> float:
    """Value of a revealing pilot: VP = d varpi Y_s - F_pil - max(0, varpi Y_s + (1 - varpi) Y_f), Y_f < 0.

    Implements: prop:tasks-pilot | Spec: 14.1 | Notes: core 4.9 | Status: theory"""
    return d * varpi * Y_s - F_pil - max(0.0, varpi * Y_s + (1 - varpi) * Y_f)


def pilot_band(Y_s, Y_f, F_pil, d=1.0) -> tuple[float, float, float]:
    """Pilot iff F_pil/(d Y_s) < varpi < (|Y_f| - F_pil)/(|Y_f| + (1 - d) Y_s); gate varpi_gate = |Y_f|/(Y_s + |Y_f|).
    Returns (low, high, gate).

    Implements: prop:tasks-pilot, eq:tasks-pilotband | Spec: 14.1 | Notes: core 4.9 | Status: theory"""
    Yf = abs(Y_f)
    lo = F_pil / max(d * Y_s, 1e-12) if Y_s > 0 else math.inf
    hi = (Yf - F_pil) / max(Yf + (1 - d) * max(Y_s, 0.0), 1e-12)
    gate = Yf / max(Y_s + Yf, 1e-12)
    return lo, hi, gate


# =================================================================================================
# 8. Granularity and the value of data (spec 3(c), Q1; core 4.10)
# =================================================================================================

def std_normal_loss(u):
    """Unit normal loss function L(u) = n(u) - u (1 - N(u)).

    Implements: prop:tasks-granularity | Spec: 3(c) | Notes: core 4.10 | Status: theory"""
    u = _a(u)
    return norm.pdf(u) - u * norm.sf(u)


def decision_loss(m, s):
    """Expected loss from deciding now on a value with posterior mean m and sd s: s L(|m|/s).

    Implements: prop:tasks-granularity | Spec: 3(c) | Notes: core 4.10 | Status: theory"""
    s = np.maximum(_a(s), 1e-12)
    return s * std_normal_loss(np.abs(_a(m)) / s)


def decision_loss_bound(m, s):
    """Distribution-free bound min(s/2, s^2/(4|m|)) on the loss from deciding now.

    Implements: prop:tasks-granularity | Spec: 3(c) | Notes: core 4.10 | Status: theory"""
    s, m = _a(s), np.abs(_a(m))
    with np.errstate(divide="ignore"):
        return np.minimum(s / 2, np.where(m > 0, s * s / (4 * m), np.inf))


def value_of_tier(m, s, s_new):
    """Value of the next data tier that cuts the variance to s_new^2: s_hat L(|m|/s_hat), s_hat^2 = s^2 - s_new^2.

    Implements: prop:tasks-granularity | Spec: 3(c) | Notes: core 4.10 | Status: theory"""
    sh = np.sqrt(np.maximum(_a(s) ** 2 - _a(s_new) ** 2, 1e-24))
    return sh * std_normal_loss(np.abs(_a(m)) / sh)


# =================================================================================================
# 9. Run costs, security and scope (spec 18; core 4.12)
# =================================================================================================

def technical_debt(N_int, Z, edges, c_int, c_cpl) -> float:
    """C_td(Z) = c_int sum_{j in Z} N_j + c_cpl sum_{automated edges (i, j)} N_i N_j.

    Implements: ass:tasks-ancillary, prop:tasks-fullcost | Spec: 18.1 | Notes: core 4.12 | Status: theory"""
    Z = np.asarray(Z, dtype=bool)
    N_int = _a(N_int)
    tot = c_int * float(N_int[Z].sum())
    for i, j in edges:
        if Z[i] and Z[j]:
            tot += c_cpl * N_int[i] * N_int[j]
    return tot


def exposure_score(data_sensitivity, autonomy, reach, external_share, weights=(0.4, 0.25, 0.2, 0.15)):
    """Exposure Omega_j(x) >= 0, nondecreasing in the four drivers of the assumption (data sensitivity, write and
    transaction rights, systems reachable, untrusted external inputs), as a weighted sum of drivers on [0, 1].

    Implements: ass:tasks-ancillary | Spec: 18.2 | Notes: core 4.12 (drivers; form left open) | Status: provisional"""
    w = weights
    return (w[0] * _a(data_sensitivity) + w[1] * _a(autonomy) + w[2] * np.clip(_a(reach), 0, 1)
            + w[3] * np.clip(_a(external_share), 0, 1))


def incident_cost(Omega, h_f, h_u, v, L_inc):
    """Expected annual incident loss without security spending: C_inc = Omega (h_f + h_u v) L_inc.

    Implements: ass:tasks-ancillary | Spec: 18.2 | Notes: core 4.12 | Status: theory"""
    return _a(Omega) * (_a(h_f) + _a(h_u) * _a(v)) * _a(L_inc)


def risk_cost(C_inc, C_s):
    """Risk cost with the exponential residual g(C) = exp(-C/C_s): C_risk = C_inc if C_inc <= C_s, else
    C_s (1 + ln(C_inc/C_s)). Concave and subadditive: pooling security on one platform is cheaper.

    Implements: prop:tasks-security | Spec: 18.2 | Notes: core 4.12 | Status: theory"""
    C_inc, C_s = _a(C_inc), np.maximum(_a(C_s), 1e-12)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(C_inc <= C_s, C_inc, C_s * (1.0 + np.log(np.maximum(C_inc, 1e-300) / C_s)))


def security_spend(C_inc, C_s):
    """Optimal security spending C_sec* = C_s ln(C_inc/C_s)^+ under the exponential residual factor. That it stays
    below C_inc/e is a property of this form (the analogue of Gordon and Loeb's bound, which holds only for two
    breach-function classes); the engine never imposes 1/e as a cap.

    Implements: prop:tasks-security | Spec: 18.2 | Notes: core 4.12 | Status: theory"""
    C_inc, C_s = _a(C_inc), np.maximum(_a(C_s), 1e-12)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(C_inc > C_s, C_s * np.log(np.maximum(C_inc, 1e-300) / C_s), 0.0)


def in_scope(savings, C_inc, C_s, data_class_allowed=True, tail_loss=0.0, L_max=math.inf):
    """Scope test: out of scope if the risk appetite excludes the data class or a single incident could exceed
    L_max; otherwise in scope iff savings exceed the risk cost C_risk(C_inc).

    Implements: prop:tasks-security | Spec: 18.2 | Notes: core 4.12 | Status: theory"""
    ok = np.asarray(data_class_allowed, dtype=bool) & (_a(tail_loss) <= L_max)
    return ok & (_a(savings) > risk_cost(C_inc, C_s))


def build_or_buy(F_A, T_A, delta_M, C_reval, T_up, C_td, pi_n, ups_B, F_V, C_reval_V, V_B, F_int, C_lock, v) -> dict:
    """Build versus buy. Build: C_fix_b = F_A/T_A + delta_M F_A + C_reval/T_up + C_td a year plus pi n a unit.
    Buy: c_v = (1 + ups_B)[pi n + (F_V (1/T_A + delta_M) + C_reval_V/T_up)/V_B] a unit plus
    C_fix_v = F_int/T_A + C_lock. Build iff v >= v_BB = (C_fix_b - C_fix_v)/(c_v - pi n); break-even lock-in
    C_lock* = C_fix_b - F_int/T_A - v (c_v - pi n).

    Implements: prop:tasks-buildbuy | Spec: 18.1 | Notes: core 4.12 | Status: theory"""
    fix_b = F_A / T_A + delta_M * F_A + C_reval / T_up + C_td
    c_v = (1 + ups_B) * (pi_n + (F_V * (1 / T_A + delta_M) + C_reval_V / T_up) / V_B)
    fix_v = F_int / T_A + C_lock
    gap = c_v - pi_n
    v_BB = (fix_b - fix_v) / gap if gap > 0 else math.inf
    build_cost = fix_b + v * pi_n
    buy_cost = fix_v + v * c_v
    return {"fixed_build": fix_b, "fixed_buy": fix_v, "unit_buy": c_v, "v_BB": v_BB,
            "build_annual": build_cost, "buy_annual": buy_cost, "choice": "build" if build_cost <= buy_cost else "buy",
            "lock_in_breakeven": fix_b - F_int / T_A - v * gap}


def review_latency(Phi_sec, nu):
    """Security-review latency of an M/M/1 queue: E[T_sec] = 1/(Phi_sec - nu); infinite when nu >= Phi_sec.

    Implements: prop:tasks-secreview | Spec: 18.2 | Notes: core 4.12 | Status: theory"""
    gap = _a(Phi_sec) - _a(nu)
    with np.errstate(divide="ignore"):
        return np.where(gap > 0, 1.0 / np.where(gap > 0, gap, 1.0), np.inf)


def review_value_lost(Phi_sec, nu, V_dep, r_d):
    """Value lost per deployment V_dep r_d/(Phi_sec - nu + r_d), per year nu V_dep r_d/(Phi_sec - nu + r_d),
    and the marginal value of capacity nu V_dep r_d/(Phi_sec - nu + r_d)^2. Returns (per deployment, per year,
    marginal).

    Implements: prop:tasks-secreview, eq:tasks-secvalue | Spec: 18.2 | Notes: core 4.12 | Status: theory"""
    den = max(Phi_sec - nu + r_d, 1e-12)
    per = V_dep * r_d / den
    return per, nu * per, nu * V_dep * r_d / den ** 2


def review_retained_share(Phi_sec, nu, r_d, ell_dec=0.0):
    """Expected share of value retained after the decision gate and security review:
    exp(-r_d ell_dec) (Phi_sec - nu)/(Phi_sec - nu + r_d); zero when the queue is unstable.

    Implements: prop:tasks-secreview | Spec: 14.2, 18.2 | Notes: core 4.12 | Status: theory"""
    gap = _a(Phi_sec) - _a(nu)
    return np.where(gap > 0, np.exp(-r_d * _a(ell_dec)) * gap / (np.maximum(gap, 0) + r_d), 0.0)


def optimal_review_capacity(nu, V_dep, r_d, p_sec):
    """Square-root staffing rule Phi* = nu - r_d + sqrt(nu V_dep r_d / p_sec) (when it exceeds nu).

    Implements: prop:tasks-secreview | Spec: 18.4 | Notes: core 4.12 | Status: theory"""
    return nu - r_d + math.sqrt(max(nu * V_dep * r_d / max(p_sec, 1e-12), 0.0))


def coarse_understatement(per_process_fixed, N_int, c_curv, C_inc_p, C_s) -> dict:
    """How much a cell that pools P processes understates ancillary costs: per-process fixed costs counted once,
    (P - 1) phi_bar; the Jensen gap of a convex technical-debt function, (c/2) P Var(N); and the security pooling
    gap sum_p C_risk(C_inc_p) - C_risk(sum_p C_inc_p).

    Implements: prop:tasks-ancscale | Spec: 18.4 | Notes: core 4.12 | Status: theory"""
    phi = _a(per_process_fixed)
    P = phi.size
    N_int = _a(N_int)
    fixed_gap = float(phi.sum() - phi.mean()) if P else 0.0
    jensen = float(c_curv / 2 * P * N_int.var()) if P else 0.0
    sec_gap = float(np.sum(risk_cost(C_inc_p, C_s)) - risk_cost(np.sum(C_inc_p), C_s)) if P else 0.0
    return {"per_process_fixed": fixed_gap, "technical_debt": jensen, "security_pooling": sec_gap,
            "total": fixed_gap + jensen + sec_gap}


# =================================================================================================
# 10. Universe, tornado, Shapley, floors (spec 5; ext 3.1)
# =================================================================================================

def waterfall(x, fea, per, pre, eco) -> dict:
    """Spend shares of the four nested layers and the waterfall of gaps (capability, rules, preferences, cost).

    Implements: def:ext-universe, lem:ext-nested, eq:ext-waterfall | Spec: 5 | Notes: ext 3.1 | Status: theory"""
    x = _a(x)
    tot = max(float(x.sum()), 1e-12)
    s = {k: float(x[np.asarray(m, bool)].sum() / tot) for k, m in (("feasible", fea), ("permissible", per),
                                                                   ("preferred", pre), ("economical", eco))}
    s["gaps"] = {"capability": 1 - s["feasible"], "rules": s["feasible"] - s["permissible"],
                 "preferences": s["permissible"] - s["preferred"], "cost": s["preferred"] - s["economical"]}
    return s


def shapley_values(f: Callable[[frozenset], float], K: int) -> np.ndarray:
    """Shapley decomposition of f(all groups moved) - f(none) across K parameter groups:
    Sh_k = sum_{T subset G minus k} |T|!(K - |T| - 1)!/K! [f(T + k) - f(T)]; the Sh_k add up exactly.

    Implements: def:ext-tornado, prop:ext-shapley, eq:ext-shapley | Spec: 5 | Notes: ext 3.1 | Status: theory"""
    cache: dict[frozenset, float] = {}

    def ff(T):
        if T not in cache:
            cache[T] = f(T)
        return cache[T]

    out = np.zeros(K)
    for k in range(K):
        others = [j for j in range(K) if j != k]
        for size in range(K):
            w = math.factorial(size) * math.factorial(K - size - 1) / math.factorial(K)
            for T in combinations(others, size):
                Ts = frozenset(T)
                out[k] += w * (ff(Ts | {k}) - ff(Ts))
    return out


def oversight_floor_breakpoint(xi_A, B, w_hat, t):
    """Oversight floor at which automation stops paying: xi_min* = xi_A + B/(w_hat t).

    Implements: prop:ext-breaks | Spec: 8.9 | Notes: ext 3.1, 3.8 | Status: theory"""
    return _a(xi_A) + _a(B) / np.maximum(_a(w_hat) * _a(t), 1e-12)


def customer_breakeven(B, v, Xh, S):
    """Customer retention loss at which a customer-facing automation stops paying: delta_G* = B v / (X_hat S).

    Implements: prop:ext-customer, prop:ext-breaks | Spec: 5 | Notes: ext 3.1 | Status: theory"""
    return _a(B) * _a(v) / max(Xh * S, 1e-12)


# =================================================================================================
# 11. Capability, prices and energy (spec 6; ext 3.2)
# =================================================================================================

def capability_horizon(t, H0, t0, Td, agi_year=None, plateau_year=None):
    """50 percent task horizon H(t) = H0 2^((t - t0)/T_d), in human hours; H = inf from agi_year; with a plateau
    (spec 24.2 scenario) the horizon stops growing at plateau_year.

    Implements: ass:ext-capability | Spec: 6, 24.2 | Notes: ext 3.2 | Status: theory"""
    t = _a(t)
    te = t if plateau_year is None else np.minimum(t, plateau_year)
    h = H0 * np.power(2.0, (te - t0) / Td)
    if agi_year is not None:
        h = np.where(t >= agi_year, np.inf, h)
    return h


def capability_horizon_physical(t, H0, t0, Td, L_W, Td_phys, plateau_year=None):
    """Physical work: the horizon starts where cognitive work stood L_W years earlier and doubles every Td_phys
    years (slower), H_phys(t) = H0 2^(-L_W/T_d) 2^((t - t0)/Td_phys), instead of a pure lag (notes/modern_theory_map.md
    change 4: self-driving improves about 0.6 doublings a year).

    Implements: ass:ext-capability(iv) | Spec: 6, 20 | Notes: ext 3.2; modern map change 4 | Status: theory"""
    t = _a(t)
    te = t if plateau_year is None else np.minimum(t, plateau_year)
    return H0 * np.power(2.0, -L_W / Td) * np.power(2.0, (te - t0) / Td_phys)


def chi_reliability(r, eta_r, form: str = "logistic"):
    """Horizon ratio between the 50 percent and the r horizons. Logistic in log length (METR's fit):
    chi(r) = (r/(1 - r))^eta_r (chi(0.8) about 5). Constant hazard per unit of human time (an agent half-life):
    chi(r) = 1/log2(1/r) (chi(0.8) = 3.1).

    Implements: ass:ext-capability | Spec: 6 | Notes: ext 3.2; modern map change 4 (constant hazard) | Status: theory"""
    r = np.clip(_a(r), 0.5, 1 - 1e-12)
    if form == "constant_hazard":
        return 1.0 / np.log2(1.0 / r)
    return (r / (1 - r)) ** eta_r


def kappa_ctx(iota, coverage, xi_context):
    """Context multiplier kappa_ctx = 1/(1 - xi iota C): the context share xi of task length is supplied by a
    context engine or documented processes with coverage C, scaled by readiness.

    Implements: ass:ext-capability | Spec: 6 | Notes: ext 3.2 | Status: theory"""
    return 1.0 / (1.0 - np.clip(_a(xi_context) * _a(iota) * _a(coverage), 0.0, 0.95))


def effective_task_length(d, exposure, transfer, xi_e=1.0, floor=0.05):
    """Task length for the capability test, d / [transfer max(exposure, floor)^xi_e]: low LLM exposure makes a
    task effectively longer for AI; `transfer` is the domain-transfer factor of params.yaml.

    Implements: ass:ext-capability | Spec: 6 | Notes: ext 3.2 (d_j); exposure link is the engine's | Status: provisional"""
    return _a(d) / (_a(transfer) * np.maximum(_a(exposure), floor) ** xi_e)


def doublings_needed(d, chi, H0, kappa):
    """calH_j = log2(d chi(rbar) / (H0 kappa_ctx)), the doublings still needed for feasibility.

    Implements: ass:ext-capability, prop:ext-feasible | Spec: 6 | Notes: ext 3.2 | Status: theory"""
    return np.log2(np.maximum(_a(d) * _a(chi), 1e-300) / (H0 * np.maximum(_a(kappa), 1e-300)))


def feasibility_date(t_now, t0, Td, calH, L_W, ph, plateau_year=None):
    """T_F_j = max(t_now, t0 + T_d calH_j + L_W ph_j): physical work waits for world models by L_W (pass ph = 0
    and a unit-specific T_d for the slow-doubling form). Under a plateau, a date after plateau_year is never.

    Implements: prop:ext-feasible | Spec: 6, 24.2 | Notes: ext 3.2 | Status: theory"""
    tf = np.maximum(t_now, t0 + _a(Td) * _a(calH) + L_W * _a(ph))
    if plateau_year is not None:
        tf = np.where(tf > max(plateau_year, t_now) + 1e-9, np.inf, tf)
    return tf


def reliability_lag(eta_r, Td, r_from, r_to):
    """Years between reaching reliability r_from and r_to: eta_r T_d log2(odds(r_to)/odds(r_from)).

    Implements: prop:ext-feasible | Spec: 6 | Notes: ext 3.2 | Status: theory"""
    odds = lambda r: r / (1 - r)
    return eta_r * Td * math.log2(odds(r_to) / odds(r_from))


def inference_price(t, T_F, price_at_feasibility, delta_pi, floor, s_E=0.0, energy_index=1.0):
    """AI spend per human-hour-equivalent at fixed difficulty: c(T_F) exp(-delta_pi (t - T_F)) after first
    feasibility, floored; energy is the share s_E of the cost and scales with the energy price index.

    Implements: prop:ext-energy, prop:tasks-curve | Spec: 6 | Notes: ext 3.2 | Status: theory"""
    t, T_F = _a(t), _a(T_F)
    tf = np.where(np.isfinite(T_F), T_F, t)
    p = _a(price_at_feasibility) * np.exp(-_a(delta_pi) * np.maximum(t - tf, 0.0))
    p = np.maximum(p, _a(floor))
    return p * ((1.0 - s_E) + s_E * _a(energy_index))


def energy_equivalent_years(s_E, eps_E, delta_pi):
    """An energy-price fall eps_E multiplies AI cost by (1 - s_E eps_E): worth -ln(1 - s_E eps_E)/delta_pi years
    of the price trend.

    Implements: prop:ext-energy | Spec: 6 | Notes: ext 3.2 | Status: theory"""
    return -math.log(1 - s_E * eps_E) / delta_pi


# =================================================================================================
# 12. Adoption timing (spec 6; ext 3.3)
# =================================================================================================

def ramp_factor_discounted(r, T_par):
    """Discounted ramp factor rho_bar = int_0^T_par e^{-r tau} d rho(tau) = (1 - e^{-r T_par})/(r T_par), linear.

    Implements: prop:ext-timing, eq:ext-Opar | Spec: 6, 13.2 | Notes: ext 3.3 | Status: theory"""
    if T_par <= 0:
        return 1.0
    return (1 - math.exp(-r * T_par)) / (r * T_par) if r > 0 else 1.0


def adoption_date(times, v_s, costs: dict, rates: dict, r, T_par) -> dict:
    """Per-process adoption date: hurdle(T) = sum_i (r + delta_i) T_i(T), net(T) = rho_bar v(T) s(T) - hurdle(T);
    T* = first T on the grid with net >= 0 (None if never); option value of waiting = int_0^T* e^{-rt}(-net) dt.

    Implements: prop:ext-timing, eq:ext-OT | Spec: 6 | Notes: ext 3.3 | Status: theory"""
    times = _a(times)
    rb = ramp_factor_discounted(r, T_par)
    hurdle = sum((r + rates.get(k, 0.0)) * _a(v) for k, v in costs.items())
    net = rb * _a(v_s) - hurdle
    idx = np.flatnonzero(net >= 0)
    if not idx.size:
        return {"T_star": None, "option_value": float("nan"), "net": net}
    Ts = float(times[idx[0]])
    m = times <= Ts
    ov = float(np.trapezoid(np.exp(-r * times[m]) * np.maximum(-net[m], 0), times[m])) if m.sum() > 1 else 0.0
    return {"T_star": Ts, "option_value": ov, "net": net}


def adoption_date_constant(r, delta_F, F0, S_flow):
    """Closed form with a constant saving flow and a build cost falling at delta_F:
    T* = max(0, ln((r + delta_F) F0 / S) / delta_F).

    Implements: prop:ext-timing | Spec: 6 | Notes: ext 3.3 | Status: theory"""
    if S_flow <= 0:
        return math.inf
    if delta_F <= 0:
        return 0.0 if S_flow >= r * F0 else math.inf
    return max(0.0, math.log((r + delta_F) * F0 / S_flow) / delta_F)


# =================================================================================================
# 13. Competition (spec 6; ext 3.4)
# =================================================================================================

def retained_share(n_c, M):
    """Share of a saving the adopter keeps when M of its n_c - 1 rivals replicate it: (n_c - M)/(n_c + 1).

    Implements: lem:ext-retained | Spec: 6 | Notes: ext 3.4 | Status: theory"""
    return (n_c - M) / (n_c + 1.0)


def competition_label(K, m, d, n_c, B) -> str:
    """Commodity automation with unit margin m, saving d, fixed cost per year K, demand slope B:
    value-creating if K < E_eq, defensive if E_eq <= K < E_priv(n_c - 1), contested if below E_priv(0),
    otherwise not worth doing.

    Implements: prop:ext-should, def:ext-motives | Spec: 6 | Notes: ext 3.4 | Status: theory"""
    a = d / (n_c + 1.0)
    E_eq = a * (2 * m + a) / B
    E_priv = lambda M: n_c * a * (2 * m + (n_c - 2 * M) * a) / B
    if K < E_eq:
        return "value-creating"
    if K < E_priv(n_c - 1):
        return "defensive"
    if K < E_priv(0):
        return "contested"
    return "not worth doing"


def flip_date(times, entrant_cost, incumbent_price, p_sw):
    """Market flip date T_M: the first t with P_I > c_E(t) + p_sw; None if never.

    Implements: prop:ext-should, prop:ext-breaks | Spec: 6, 8.7 | Notes: ext 3.4 | Status: theory"""
    ok = _a(incumbent_price) > _a(entrant_cost) + p_sw
    idx = np.flatnonzero(ok)
    return float(_a(times)[idx[0]]) if idx.size else None


def game_shares(hhi, phi_ind=None, e=0.0, rep=1.0):
    """Durable and private shares of a unit-cost cut (cor:ext-game-engine(a), lem:ext-game-pass(b)):
    phi_ind = n/(n + 1 - e) with n = 1/HHI if not supplied; dur = 1 - phi_ind (1 - HHI) (linear: 2 HHI/(1 + HHI));
    priv = 2 - HHI - HHI (1 - HHI) phi_ind (linear: 2/(1 + HHI)); dur_rep = (1 - rep) priv + rep dur. Also the pure
    dilemma flag phi_ind > n/(n - 1).

    Implements: cor:ext-game-engine(a), eq:ext-game-dur, lem:ext-game-pass(b) | Spec: 24.7 | Notes: competition 3.2 | Status: theory"""
    H = float(np.clip(hhi, 1e-6, 1.0))
    n = 1.0 / H
    if phi_ind is None:
        if n + 1 - e <= 0:
            raise ValueError("curvature e must satisfy n_c + 1 - e > 0")
        phi_ind = n / (n + 1 - e)
    dur = 1.0 - phi_ind * (1.0 - H)
    priv = 2.0 - H - H * (1.0 - H) * phi_ind
    return {"hhi": H, "n_c": n, "phi_ind": float(phi_ind), "phi_own": float(phi_ind) / n, "dur": dur, "priv": priv,
            "dur_rep": (1.0 - rep) * priv + rep * dur, "pure_dilemma": bool(n > 1 and phi_ind > n / (n - 1))}


def cournot_earnings(mg, d, Y, n_c, k, adopted: bool):
    """Exact flow earnings in linear Cournot (lem:ext-game-pass(a)): phi_own = phi_x = 1/(n_c + 1), B = mg/Y;
    E1(k) = (mg + (1 - phi_own) d - k phi_x d)^2 / B and E0(k) = (mg - k phi_x d)^2 / B (k rival adopters).

    Implements: lem:ext-game-pass(a) | Spec: 24.7 | Notes: competition 3.3 | Status: theory"""
    phi = 1.0 / (n_c + 1.0)
    B = mg / max(Y, 1e-12)
    m = mg + ((1 - phi) * d if adopted else 0.0) - k * phi * d
    return m * m / max(B, 1e-300)


def game_gains(mg, d, Y, n_c):
    """E^priv(k) = E1(k) - E0(k) for k = 0..n_c - 1 and E^eq = E1(n_c - 1) - E0(0) (linear Cournot).

    Implements: lem:ext-game-pass(a), prop:ext-game-pd | Spec: 24.7 | Notes: competition 3.3 | Status: theory"""
    n = max(int(round(n_c)), 1)
    priv = [cournot_earnings(mg, d, Y, n, k, True) - cournot_earnings(mg, d, Y, n, k, False) for k in range(n)]
    eq = cournot_earnings(mg, d, Y, n, n - 1, True) - cournot_earnings(mg, d, Y, n, 0, False)
    return priv, eq


def dominant_strategy(K, E_priv_last, E_eq):
    """Adoption is a dominant strategy iff the annualized cost K < E^priv(n_c - 1); the automation prisoner's dilemma
    window is E^eq <= K < E^priv(n_c - 1) (prop:ext-game-pd(a)).

    Implements: prop:ext-game-pd(a) | Spec: 24.7 | Notes: competition 3.5 | Status: theory"""
    return {"dominant": bool(K < E_priv_last), "dilemma": bool(E_eq <= K < E_priv_last), "value_creating_if_all": bool(K < E_eq)}


def single_firm_date(E, r, G, dF, F0):
    """T°(E) = max(0, ln((r + dF) F0 / E)/(G + dF)) for E > 0, else never (eq:ext-game-To).

    Implements: eq:ext-game-To | Spec: 24.7 | Notes: competition 3.4 | Status: theory"""
    if E <= 0:
        return math.inf
    return max(0.0, math.log((r + dF) * F0 / E) / (G + dF))


def entry_defensive(PE_inf, P0, c0, d, Y, K):
    """AI-native entry (prop:ext-game-entry(c)): adoption is defensive iff (P_E_inf - P0 + d) Y <= K < d Y; it is needed
    for viability iff P_E_inf < c0 and secures it iff P_E_inf >= c0 - d + K/Y; durable share after entry
    dur_E = (P_E_inf - P0 + d)/d.

    Implements: prop:ext-game-entry(c) | Spec: 24.7 | Notes: competition 3.6 | Status: theory"""
    return {"defensive": bool((PE_inf - P0 + d) * Y <= K < d * Y), "needed_for_viability": bool(PE_inf < c0),
            "secures_viability": bool(PE_inf >= c0 - d + K / max(Y, 1e-12)), "dur_E": (PE_inf - P0 + d) / max(d, 1e-12)}


def game_label(npv_dur, npv_priv, feasible: bool, viability: bool = False) -> str:
    """Classification of cor:ext-game-engine(b): value-creating if NPV^dur > 0; defensive-strategic if NPV^dur <= 0 <
    NPV^priv; defensive-viability if adoption is needed to stay viable against entrants; could-not-should otherwise.

    Implements: cor:ext-game-engine(b) | Spec: 24.7 | Notes: competition 3.7 | Status: theory"""
    if not feasible:
        return "not feasible"
    if npv_dur > 0:
        return "value-creating"
    if npv_priv > 0:
        return "defensive-strategic"
    if viability:
        return "defensive-viability"
    return "could-not-should"


def should_label(npv, feasible, permissible, defensive) -> str:
    """Should versus could: value-creating (NPV > 0), defensive (needed to stay within the entrant's cost plus
    the switching premium), could but should not (feasible, NPV <= 0 or impermissible), not feasible.

    Implements: def:ext-motives, prop:ext-should | Spec: 6 | Notes: ext 3.4 | Status: theory"""
    if not feasible:
        return "not feasible"
    if not permissible:
        return "could but should not (not permissible)"
    if npv > 0:
        return "value-creating"
    if defensive:
        return "defensive"
    return "could but should not (NPV <= 0)"


# =================================================================================================
# 14. Organization (spec 7; ext 3.5)
# =================================================================================================

def human_work(W0, nu_a, A_g, xi_A):
    """Person-years of human work W = W0 ((1 - nu_a)/A_g + nu_a xi_A).

    Implements: ass:ext-team, prop:ext-team | Spec: 7 | Notes: ext 3.5 | Status: theory"""
    return W0 * ((1 - nu_a) / A_g + nu_a * xi_A)


def team_size(W, chi_h):
    """n*(W) = W if W <= 1; else ((1 + chi/2) - sqrt((1 + chi/2)^2 - 2 chi W))/chi; None (split into
    sub-teams) above (1 + chi/2)^2/(2 chi).

    Implements: prop:ext-team, eq:ext-nstar | Spec: 7 | Notes: ext 3.5 | Status: theory"""
    if W <= 1:
        return float(W)
    b = 1 + chi_h / 2
    disc = b * b - 2 * chi_h * W
    if disc < 0:
        return None
    return (b - math.sqrt(disc)) / chi_h


def leverage(nu_a, A_g, xi_A):
    """Lambda = 1/((1 - nu_a)/A_g + nu_a xi_A); one person covers a scope W0 iff W0 <= Lambda (solo breakpoint).

    Implements: prop:ext-team, prop:ext-breaks | Spec: 7, 8.6 | Notes: ext 3.5 | Status: theory"""
    return 1.0 / ((1 - nu_a) / A_g + nu_a * xi_A)


def garicano_span(w_m, c_K, z_m, z_A=0.0):
    """Span of control sp* = (w_m + c_K (z_m - z_A))/c_K; an AI layer at z_A narrows the knowledge the manager
    must hold.

    Implements: prop:ext-hierarchy | Spec: 7 | Notes: ext 3.5 | Status: theory"""
    return (w_m + c_K * (z_m - z_A)) / c_K


def hierarchy_layers(n_workers, span) -> int:
    """Layers of management, about ceil(ln N_w / ln sp*).

    Implements: prop:ext-hierarchy | Spec: 7 | Notes: ext 3.5 | Status: theory"""
    n = max(float(n_workers), 1.0)
    return int(math.ceil(math.log(n) / math.log(max(float(span), 1.01)))) if n > 1 else 0


def managers_for(n_workers, span) -> float:
    """Managers for n workers at span sp, summed over layers.

    Implements: def:ext-org, lem:ext-staffing | Spec: 7 | Notes: ext 3.5 | Status: theory"""
    total, level = 0.0, float(n_workers)
    while level > 1.0:
        level /= max(float(span), 1.01)
        total += level
    return total


def change_capacity(kappa_abs, fte_base, N_CM=None, fte_CM_max=None):
    """Change capacity K_chg = min(kappa_abs FTE_base, N_CM FTE_CM_max) affected FTE a year.

    Implements: def:ext-org, lem:ext-staffing | Spec: 9, 13.2 | Notes: ext 3.5 | Status: theory"""
    cap = kappa_abs * fte_base
    if N_CM is not None and fte_CM_max is not None:
        cap = min(cap, N_CM * fte_CM_max)
    return cap


def transformation_team(I_k, F_k, D_k, n_A_before, n_redesign, A_aff, n_regulated, n_build, w_DE, w_AI,
                        h_FTE, l_DI, l_AI, e_mnt, e_PO, N_CM, e_RG, e_SME) -> dict:
    """Transformation team in wave k of duration D_k (years): data and integration engineers
    l_DI I_k/(w_DE h D_k); AI engineers l_AI F_k/(w_AI h D_k) + e_mnt N_A; process owners e_PO n_redesign;
    change managers A_aff/(D_k N_CM); risk and governance e_RG n_regulated; domain experts e_SME n_build.
    w_DE and w_AI are loaded hourly wages.

    Implements: def:ext-org, lem:ext-staffing | Spec: 7 | Notes: ext 3.5 | Status: theory"""
    D = max(D_k, 1e-9)
    return {"data_integration_engineers": l_DI * I_k / (w_DE * h_FTE * D),
            "ai_agent_engineers": l_AI * F_k / (w_AI * h_FTE * D) + e_mnt * n_A_before,
            "process_owners": e_PO * n_redesign, "change_managers": A_aff / (D * N_CM),
            "risk_governance_audit": e_RG * n_regulated, "domain_smes": e_SME * n_build}


# =================================================================================================
# 15. Program and waves (spec 13.2; ext 3.6)
# =================================================================================================

def dual_running_cost(n, d1, d2):
    """Dual-running cost flow of a wave of n processes, D(n) = d1 n + d2 n^2.

    Implements: ass:ext-program, eq:ext-progcost | Spec: 13.2 | Notes: ext 3.6 | Status: theory"""
    return d1 * _a(n) + d2 * _a(n) ** 2


def program_cost(sizes: Sequence[float], s, T_par, d1, d2, O_w) -> float:
    """First-order program cost C = sum_k [T_par k sum_{p in W_k} s_p + T_par D(n_k) + O_w] for identical
    processes with saving s.

    Implements: eq:ext-progcost | Spec: 13.2 | Notes: ext 3.6 | Status: theory"""
    return float(sum(T_par * (s * (k + 1) * n + d1 * n + d2 * n * n) + O_w for k, n in enumerate(sizes) if n > 0))


def front_loaded_sizes(N, K, s, d2) -> np.ndarray:
    """Cost-minimizing wave sizes for K waves: n_k = N/K + (s/(2 d2))((K + 1)/2 - k).

    Implements: prop:ext-waves, eq:ext-front | Spec: 13.2 | Notes: ext 3.6 | Status: theory"""
    k = np.arange(1, K + 1)
    return N / K + (s / (2 * d2)) * ((K + 1) / 2 - k)


def program_cost_K(K, N, s, T_par, d1, d2, O_w) -> float:
    """C(K) = T_par [s N (K + 1)/2 + d1 N + d2 N^2/K - s^2 K (K^2 - 1)/(48 d2)] + K O_w.

    Implements: prop:ext-waves | Spec: 13.2 | Notes: ext 3.6 | Status: theory"""
    return T_par * (s * N * (K + 1) / 2 + d1 * N + d2 * N * N / K - s * s * K * (K * K - 1) / (48 * d2)) + K * O_w


def square_root_wave_size(s, N, O_w, T_par, d2, nu_R=0.0, T_frz=0.0, O_re=0.0) -> float:
    """Square-root rule n* = sqrt([s N/2 + (O_w + nu_R T_par O_re)/((1 + nu_R T_frz) T_par)]/d2); with no
    reorganizations it is sqrt((s N/2 + O_w/T_par)/d2).

    Implements: prop:ext-waves, prop:ext-continuity | Spec: 13.2, 15.3 | Notes: ext 3.6; ext tex sec:ext-shocks | Status: theory"""
    inner = s * N / 2 + (O_w + nu_R * T_par * O_re) / ((1 + nu_R * T_frz) * max(T_par, 1e-9))
    return math.sqrt(max(inner / max(d2, 1e-12), 0.0))


def program_duration_bound(N, a, K_chg, e, T_par, x_hat, Phi) -> float:
    """Pace: T_prog >= max(N a / K_chg, N e T_par / (x_hat Phi)).

    Implements: prop:ext-bandwidth, prop:ext-waves | Spec: 14.2 | Notes: ext 3.6 | Status: theory"""
    return max(N * a / max(K_chg, 1e-12), N * e * T_par / max(x_hat * Phi, 1e-12))


# =================================================================================================
# 16. Portfolio risk and decision bandwidth (spec 14; ext 3.7)
# =================================================================================================

def learning_logit(logit0, upsilon_L, E):
    """logit varpi_k = logit varpi_k^0 + upsilon_L ln(1 + E_k).

    Implements: ass:ext-portfolio, prop:ext-portfolio | Spec: 14.1 | Notes: ext 3.7 | Status: theory"""
    return _a(logit0) + upsilon_L * np.log1p(np.maximum(_a(E), 0.0))


def experience_update(E, successes, delta_E, eta_tr=1.0):
    """E_{k+1} = (1 - delta_E) E_k + eta_tr x successes_k (decay and transfer across units below one).

    Implements: ass:ext-portfolio | Spec: 14.1 | Notes: ext 3.7 | Status: theory"""
    return (1.0 - delta_E) * _a(E) + eta_tr * _a(successes)


def platform_posterior(p_P, varpi):
    """Posterior that a platform is sound after a failure on it, p' = p_P (1 - varpi)/(1 - p_P varpi).

    Implements: prop:ext-portfolio, eq:ext-seq | Spec: 14.1 | Notes: ext 3.7 | Status: theory"""
    return p_P * (1 - varpi) / (1 - p_P * varpi)


def success_count_variance(n_w, p_P, varpi):
    """Variance of the number of successes of n_w waves on one platform (varpi is the conditional success
    probability given a sound platform): p_P n_w varpi (1 - varpi) + n_w^2 varpi^2 p_P (1 - p_P).

    Implements: prop:ext-portfolio | Spec: 14.1 | Notes: ext 3.7 | Status: theory"""
    return p_P * n_w * varpi * (1 - varpi) + n_w ** 2 * varpi ** 2 * p_P * (1 - p_P)


def sample_overrun(rng: np.random.Generator, size, tail_prob, tail_alpha, tail_xmin, body_median, body_sigma, cap=None):
    """Implementation-cost multiplier (actual / estimate): with probability tail_prob a Pareto tail of index
    tail_alpha above tail_xmin (Flyvbjerg et al. 2022: 2.3 above 2.0; one in six, Flyvbjerg and Budzier 2011),
    otherwise a lognormal body with the given median truncated below tail_xmin. A stage-gate cap truncates the
    tail.

    Implements: ass:ext-portfolio, prop:ext-portfolio | Spec: 14.1 | Notes: ext 3.7 (tail); body is the engine's | Status: provisional"""
    u = rng.random(size)
    in_tail = rng.random(size) < tail_prob
    tail = tail_xmin * (1.0 - u) ** (-1.0 / tail_alpha)
    zc = norm.cdf(math.log(tail_xmin / body_median) / body_sigma)
    body = body_median * np.exp(body_sigma * norm.ppf(np.clip(u * zc, 1e-12, 1 - 1e-12)))
    out = np.where(in_tail, tail, body)
    return np.minimum(out, cap) if cap is not None else out


def overrun_mean(tail_prob, tail_alpha, tail_xmin, body_median, body_sigma) -> float:
    """Mean of the overrun multiplier of sample_overrun (without a cap).

    Implements: ass:ext-portfolio | Spec: 14.1 | Notes: ext 3.7 | Status: provisional"""
    z = math.log(tail_xmin / body_median) / body_sigma
    body = body_median * math.exp(body_sigma ** 2 / 2) * norm.cdf(z - body_sigma) / max(norm.cdf(z), 1e-12)
    tail = tail_alpha * tail_xmin / (tail_alpha - 1.0) if tail_alpha > 1 else math.inf
    return (1.0 - tail_prob) * body + tail_prob * tail


def congestion_q(x, eta_q):
    """Quality congestion q(x) = exp(-eta_q (x - 1)_+): success falls once load exceeds bandwidth.

    Implements: ass:ext-bandwidth | Spec: 14.2 | Notes: ext 3.7 | Status: theory"""
    return np.exp(-eta_q * np.maximum(_a(x) - 1.0, 0.0))


def decision_latency(x, ell0, cap=0.95):
    """Queueing latency ell_dec(x) = ell0 / (1 - x), with the load ratio capped below one.

    Implements: ass:ext-bandwidth | Spec: 14.2 | Notes: ext 3.7 | Status: theory"""
    return _a(ell0) / (1.0 - np.minimum(_a(x), cap))


def Q_bandwidth(x, eta_q, ell0, r_d, cap=0.95):
    """Benefit factor Q(x) = q(x) exp(-r_d ell_dec(x)).

    Implements: ass:ext-bandwidth, prop:ext-bandwidth | Spec: 14.2 | Notes: ext 3.7 | Status: theory"""
    return congestion_q(x, eta_q) * np.exp(-r_d * decision_latency(x, ell0, cap))


def load_breakpoint_queue(r_d, ell0) -> float:
    """Load breakpoint with queueing latency only: x_hat = 1 + c/2 - sqrt(c + c^2/4), c = r_d ell0.

    Implements: prop:ext-bandwidth | Spec: 14.2 | Notes: ext 3.7 | Status: theory"""
    c = r_d * ell0
    return 1 + c / 2 - math.sqrt(c + c * c / 4)


def load_breakpoint(eta_q, ell0, r_d, cap=0.95) -> float:
    """Load at which x Q(x) peaks (elasticity of Q equal to one); beyond it another initiative lowers value.

    Implements: prop:ext-bandwidth, prop:ext-breaks | Spec: 14.2 | Notes: ext 3.7 | Status: theory"""
    xs = np.linspace(1e-4, cap - 1e-4, 4000)
    return float(xs[np.argmax(xs * Q_bandwidth(xs, eta_q, ell0, r_d, cap))])


def optimal_concurrency(varpi0, V, e, Phi, eta_q, ell0, r_d, d1=0.0, d2=0.0, n_max=200, cap=0.95):
    """Optimal number of concurrent initiatives max_n n varpi0 V Q(n e/Phi) - D(n).

    Implements: prop:ext-bandwidth | Spec: 14.2 | Notes: ext 3.7 | Status: theory"""
    n = np.arange(1, n_max + 1)
    x = n * e / Phi
    val = np.where(x < cap, n * varpi0 * V * Q_bandwidth(x, eta_q, ell0, r_d, cap), -np.inf) - (d1 * n + d2 * n * n)
    return int(n[np.argmax(val)]), val


def value_of_bandwidth(n_star, varpi0, V, Phi, x_star, eta_q, ell0, r_d) -> float:
    """dEV*/dPhi = [n* varpi0 V Q(x*)/Phi] x* (-Q'(x*)/Q(x*)).

    Implements: prop:ext-bandwidth | Spec: 14.2 | Notes: ext 3.7 | Status: theory"""
    h = 1e-5
    Q = float(Q_bandwidth(x_star, eta_q, ell0, r_d))
    dQ = float((Q_bandwidth(x_star + h, eta_q, ell0, r_d) - Q_bandwidth(x_star - h, eta_q, ell0, r_d)) / (2 * h))
    return n_star * varpi0 * V * Q / Phi * x_star * (-dQ / max(Q, 1e-300))


def ai_bandwidth_gain(e_appr, e_prep, A_Phi) -> float:
    """Bandwidth multiplier from AI preparation (e_appr + e_prep)/(e_appr + e_prep/(1 + A_Phi)), capped by the
    accountable-approval share at (e_appr + e_prep)/e_appr.

    Implements: prop:ext-bandwidth | Spec: 14.2 | Notes: ext 3.7 | Status: theory"""
    return (e_appr + e_prep) / (e_appr + e_prep / (1 + A_Phi))


def should_delegate(varpi_top, varpi_del, V, p_Phi, e, accountable=False) -> bool:
    """Delegate iff (varpi_top - varpi_del) V < p_Phi e, except approvals reserved to accountable officers.

    Implements: prop:ext-bandwidth | Spec: 14.2 | Notes: ext 3.7 | Status: theory"""
    return (not accountable) and (varpi_top - varpi_del) * V < p_Phi * e


# =================================================================================================
# 17. Regime shocks (spec 15; ext tex sec:ext-shocks, verify_part2_ext.py section I)
# =================================================================================================

def disruption_rate(nu_L, kappa_keep, nu_V):
    """Disruption rate of work in flight nu_D = nu_L (1 - kappa_keep) + nu_V.

    Implements: ass:ext-shocks | Spec: 15.1, 15.2 | Notes: ext tex sec:ext-shocks | Status: theory"""
    return nu_L * (1 - kappa_keep) + nu_V


def shock_value(F_I, S, r, nu_D, T_par, T_emb, V_rec=0.0):
    """Value of a process under disruption: V = -(F + I) + S [(e^{-r_D T_par} - e^{-r_D T_emb})/r_D +
    e^{-r_D T_emb}/r] + V_rec (nu_D/r_D)(1 - e^{-r_D T_emb}), r_D = r + nu_D.

    Implements: prop:ext-shocks, eq:ext-Vshock | Spec: 15.3 | Notes: ext tex sec:ext-shocks | Status: theory"""
    rD = r + nu_D
    sav = S * ((math.exp(-rD * T_par) - math.exp(-rD * T_emb)) / rD + math.exp(-rD * T_emb) / r)
    rec = V_rec * nu_D / rD * (1 - math.exp(-rD * T_emb)) if nu_D > 0 else 0.0
    return -F_I + sav + rec


def shock_survival(t_rel, nu_D, T_emb):
    """Probability a transition started at 0 is not disrupted before t: exp(-nu_D min(t, T_emb)). After
    embedding at T_emb its savings are durable.

    Implements: ass:ext-shocks, prop:ext-shocks | Spec: 15.2 | Notes: ext tex sec:ext-shocks | Status: theory"""
    return np.exp(-nu_D * np.clip(_a(t_rel), 0.0, T_emb))


def recovery_pv(V_rec, nu_D, r, T_emb, t_start=0.0):
    """PV at time 0 of the recovered value V_rec = s_reuse (F + I) - C_rep of a disruption during flight:
    V_rec (nu_D / r_D)(1 - e^{-r_D T_emb}) e^{-r t_start}.

    Implements: prop:ext-shocks, eq:ext-Vshock | Spec: 15.2 | Notes: ext tex sec:ext-shocks | Status: theory"""
    if nu_D <= 0:
        return 0.0
    rD = r + nu_D
    return V_rec * nu_D / rD * (1 - math.exp(-rD * T_emb)) * math.exp(-r * t_start)


def tenure_breakpoint(r, nu_D, T_emb) -> float:
    """Tenure breakpoint r_D T_emb = 1: positive values mean the window is too long for the hazards and the
    program should be split into wins that embed within 1/r_D. Returns r_D T_emb - 1.

    Implements: prop:ext-shocks, prop:ext-breaks | Spec: 15.3 | Notes: ext tex sec:ext-shocks | Status: theory"""
    return (r + nu_D) * T_emb - 1.0


def sequencing_index(V_emb, tau, r_D):
    """Order processes run one after another by decreasing V_emb/(e^{r_D tau} - 1): quick, durable wins first
    when hazards are high.

    Implements: prop:ext-shocks | Spec: 15.3 | Notes: ext tex sec:ext-shocks | Status: theory"""
    return _a(V_emb) / np.expm1(r_D * np.maximum(_a(tau), 1e-9))


def reuse_gain(F_I, nu_D, r, T_emb, ds_reuse=1.0):
    """Gain from a more modular (vision-agnostic) investment: ds (F + I)(nu_D/r_D)(1 - e^{-r_D T_emb}).

    Implements: prop:ext-shocks | Spec: 15.3 | Notes: ext tex sec:ext-shocks | Status: theory"""
    rD = r + nu_D
    return ds_reuse * F_I * nu_D / rD * (1 - math.exp(-rD * T_emb))


def context_stock(nu_K, kappa_doc, eta_K, n_K) -> tuple[float, float]:
    """Stationary context stock: E[m] = 1 - nu_K (1 - kappa_doc)/eta_K and Var(m) = nu_K (1 - kappa_doc)^2/(2 eta_K n_K).

    Implements: prop:ext-continuity | Spec: 15.2 | Notes: ext tex sec:ext-shocks | Status: theory"""
    mean = 1 - nu_K * (1 - kappa_doc) / eta_K
    var = nu_K * (1 - kappa_doc) ** 2 / (2 * eta_K * max(n_K, 1e-9))
    return mean, var


def documentation_value(L_ctx, nu_K, d_kappa, eta_K, r) -> float:
    """Insurance value of documentation and context engines: L_ctx nu_K d_kappa / (eta_K r).

    Implements: prop:ext-continuity | Spec: 15.3 | Notes: ext tex sec:ext-shocks | Status: theory"""
    return L_ctx * nu_K * d_kappa / (eta_K * r)


def commitment_value(nu_V, tau, p_inf, V_plus, V_minus, V_rec) -> dict:
    """Commitment devices: P_V = 1 - e^{-nu_V tau}; binding device P_V[(1 - p)(V+ - V_rec) - p(V- + V_rec)];
    gated device P_V (1 - p)(V+ - V_rec).

    Implements: prop:ext-continuity | Spec: 15.3 | Notes: ext tex sec:ext-shocks | Status: theory"""
    PV = 1 - math.exp(-nu_V * tau)
    return {"P_V": PV, "binding": PV * ((1 - p_inf) * (V_plus - V_rec) - p_inf * (V_minus + V_rec)),
            "gated": PV * (1 - p_inf) * (V_plus - V_rec)}


def freeze_availability(nu_R, T_frz) -> float:
    """Share of time decision bandwidth and change capacity are available under reorganization freezes,
    1/(1 + nu_R T_frz).

    Implements: prop:ext-continuity | Spec: 15.2 | Notes: ext tex sec:ext-shocks | Status: theory"""
    return 1.0 / (1.0 + nu_R * T_frz)


# =================================================================================================
# 18. Ownership regimes (spec 16; theory_regimes.tex; notes/theory_regimes_notes.md Section 3)
# =================================================================================================

def cont_rate(r_annual):
    """Continuous rate of an annual (survey) rate: ln(1 + r); 22 percent becomes 19.9 percent.

    Implements: ass:reg-regime (rates continuous) | Spec: 16.1 | Notes: regimes 3 | Status: theory"""
    return math.log1p(float(r_annual))


def pv(flows, times, r) -> float:
    """Present value sum_t CF_t e^{-r t} on a time grid (years).

    Implements: def:reg-value | Spec: 16.2 | Notes: regimes 3.2 | Status: theory"""
    return float(np.sum(_a(flows) * np.exp(-r * _a(times))))


def irr(cashflows, times=None) -> float:
    """Internal rate of return (annual) of flows at `times` (default 0, 1, 2, ...). NaN when undefined.

    Implements: prop:reg-metrics | Spec: 16.3 | Notes: regimes 3.6 | Status: theory"""
    cf = _a(cashflows)
    t = np.arange(len(cf), dtype=float) if times is None else _a(times)
    if not (cf < 0).any() or not (cf > 0).any():
        return float("nan")
    f = lambda rr: float(np.sum(cf * (1 + rr) ** (-t)))
    lo, hi = -0.95, 20.0
    if np.sign(f(lo)) == np.sign(f(hi)):
        return float("nan")
    return float(brentq(f, lo, hi, xtol=1e-10))


def moic(distributions, invested) -> float:
    """Multiple on invested capital, total distributions / total invested.

    Implements: prop:reg-metrics | Spec: 16.3 | Notes: regimes 3.6 | Status: theory"""
    return float(np.sum(distributions) / max(float(np.sum(invested)), 1e-12))


def K_gc(r, t, life=math.inf):
    """Capitalization of one dollar a year from t on, going concern: e^{-rt}/r (or to t + life).

    Implements: prop:reg-value(b), eq:reg-K | Spec: 16.2 | Notes: regimes 3.2 | Status: theory"""
    if life == math.inf:
        return math.exp(-r * t) / r
    return (math.exp(-r * t) - math.exp(-r * (t + life))) / r


def K_x(r, t, T, Mt, Tsea=0.0):
    """Exit rule: interim flow from t to T plus Mtilde at T if the saving is seasoned (t + T_sea <= T).

    Implements: prop:reg-value(b), eq:reg-K | Spec: 16.2 | Notes: regimes 3.2 | Status: theory"""
    interim = max(math.exp(-r * t) - math.exp(-r * T), 0.0) / r
    return interim + (math.exp(-r * T) * Mt if t + Tsea <= T else 0.0)


def zeta_pe(r, T, M_exit, delta_K, h_x=1.0):
    """PE capital hurdle: zeta_pe = [1 + delta_K A_r(T)]/[A_r(T) + e^{-rT} h_x M_exit], A_r(T) = (1 - e^{-rT})/r;
    a capital switch is worth it to the sponsor iff Dc/DK > zeta_pe (public test: Dc/DK > r_w + delta_K).

    Implements: prop:reg-value(c), eq:reg-zeta | Spec: 16.2 | Notes: regimes 3.2 | Status: theory"""
    A = (1 - math.exp(-r * T)) / r
    return (1 + delta_K * A) / (A + math.exp(-r * T) * h_x * M_exit)


def myopic_weight(X, k, theta):
    """Myopic public owner's growth weight X^my = k + (X - k)/(1 + vartheta).

    Implements: prop:reg-weight(b), eq:reg-Xmy | Spec: 16.2 | Notes: regimes 3.3 | Status: theory"""
    return k + (X - k) / (1 + theta)


def exit_weight(m_hat, r, G, tau, X_T):
    """Hold-and-exit growth weight X^x(tau) = (1 - w) mhat/(r - G) + w X_T, w = e^{-(r - G) tau}; any finite horizon,
    any G, with the limit mhat tau + X_T at r = G.

    Implements: prop:reg-weight(c), eq:reg-Xexit | Spec: 16.2 | Notes: regimes 3.3 | Status: theory"""
    if abs(r - G) < 1e-9:
        return m_hat * tau + X_T
    w = math.exp(-(r - G) * tau)
    return (1 - w) * m_hat / (r - G) + w * X_T


def myopia_penalty(gaap_dip_by_year, theta_my, years: int, r, slack=0.0) -> float:
    """P_o = vartheta sum_{y=1}^{Y_m} e^{-r y} max(0, -dOI_y - slack): penalty on reported-earnings dips beyond the
    guided slack (g_slack S).

    Implements: prop:reg-value(a) | Spec: 16.1 | Notes: regimes 3.2 | Status: theory"""
    d = _a(gaap_dip_by_year)[:years]
    t = np.arange(d.size) + 1.0
    return float(theta_my * np.sum(np.exp(-r * t) * np.maximum(-d - slack, 0.0)))


def fastest_ramp(Dhat, shat, B, N, max_waves=60):
    """Fastest wave ramp under a dip budget (prop:reg-dip): N_0 = 0, N_k = min(N, N_{k-1} + floor(Dhat^{-1}(B + shat
    N_{k-1}))), with Dhat(n) the dip of a wave of n processes (callable, increasing). Returns the wave sizes (empty if
    the first wave is infeasible).

    Implements: prop:reg-dip(a) | Spec: 16.2 | Notes: regimes 3.5 | Status: theory"""
    sizes, Nk = [], 0
    for _ in range(max_waves):
        budget = B + shat * Nk
        n = 0
        while n + 1 <= N - Nk and Dhat(n + 1) <= budget + 1e-12:
            n += 1
        if n == 0:
            break
        sizes.append(n)
        Nk += n
        if Nk >= N:
            break
    return sizes


def ramp_linear(B, shat, dhat, N):
    """Linear dip D(n) = dhat n: N_k = (B/shat)[(1 + shat/dhat)^k - 1]; waves needed k_hat = ceil(ln(1 + shat N/B) /
    ln(1 + shat/dhat)).

    Implements: prop:reg-dip(a) | Spec: 16.2 | Notes: regimes 3.5 | Status: theory"""
    if B <= 0 or dhat <= 0:
        return math.inf
    if shat <= 0:
        return math.ceil(N * dhat / B)
    return math.ceil(math.log(1 + shat * N / B) / math.log(1 + shat / dhat))


def waterfall_lp(M_gross, T, r_pref=0.08, carry=0.2):
    """LP multiple after the waterfall (lem:reg-waterfall): pref = (1 + r_pref)^T; LP = M if M <= pref; pref if
    M <= 1 + (pref - 1)/(1 - carry); else 1 + (1 - carry)(M - 1).

    Implements: lem:reg-waterfall | Spec: 16.3 | Notes: regimes 3.6 | Status: theory"""
    pref = (1 + r_pref) ** T
    if M_gross <= pref:
        return M_gross
    if M_gross <= 1 + (pref - 1) / (1 - carry):
        return pref
    return 1 + (1 - carry) * (M_gross - 1)


def pe_metrics(EB0, EB_sq_T, dEB_T, FCF, times, T, M_exit, M_entry, lev0, r_debt, h_x, premium=0.0, c_tx=0.02,
               r_pref=0.08, carry=0.2, fee=0.02) -> dict:
    """PE deal metrics (prop:reg-metrics): Eq_0 = (1 + premium + c_tx) M_entry EB0 - lev0 EB0;
    ND_T = ND_0 e^{r_debt T} - int e^{r_debt (T - t)} FCF dt; Eq_T = M_exit (EB^sq_T + h_x dEB_T) - ND_T; MOIC; gross IRR
    MOIC^{1/T} - 1; LP multiple after the waterfall, net multiple LP/(1 + fee T) and net IRR.

    Implements: prop:reg-metrics, lem:reg-waterfall | Spec: 16.3 | Notes: regimes 3.6 | Status: theory"""
    P0 = M_entry * EB0
    ND0 = lev0 * EB0
    Eq0 = (1 + premium + c_tx) * P0 - ND0
    t = _a(times)
    dt = np.diff(np.concatenate([[0.0], t + 0.5]))[: len(t)] if len(t) else np.zeros(0)
    FV = float(np.sum(np.exp(r_debt * np.maximum(T - t, 0.0)) * _a(FCF) * (t < T)))
    NDT = ND0 * math.exp(r_debt * T) - FV
    EqT = M_exit * (EB_sq_T + h_x * dEB_T) - NDT
    M = EqT / max(Eq0, 1e-9)
    lp = waterfall_lp(max(M, 0.0), T, r_pref, carry)
    net = lp / (1 + fee * T)
    return {"entry_equity": Eq0, "exit_equity": EqT, "net_debt_exit": NDT, "moic": M,
            "gross_irr": (max(M, 1e-12)) ** (1 / T) - 1 if M > 0 else -1.0, "lp_multiple": lp, "net_multiple": net,
            "net_irr": (max(net, 1e-12)) ** (1 / T) - 1 if net > 0 else -1.0, "h_x": h_x}


def lbo_breakeven(V_sp, P0, ND0, r_pe, r_debt, T, c_tx=0.02, p_b=0.0, L_b=0.0, premium_req=0.3) -> dict:
    """Take-private (prop:reg-lbo): frakL = ND_0 [1 - e^{-(r_pe - r_debt) T}]; p_max = [V_sp + frakL - c_tx P_0 -
    e^{-r_pe T} p_b L_b]/P_0 - 1; it pays iff p_max >= the required control premium.

    Implements: prop:reg-lbo, eq:reg-lbo | Spec: 16.2 | Notes: regimes 3.7 | Status: theory"""
    frakL = ND0 * (1 - math.exp(-(r_pe - r_debt) * T))
    p_max = (V_sp + frakL - c_tx * P0 - math.exp(-r_pe * T) * p_b * L_b) / max(P0, 1e-9) - 1
    return {"p_max": p_max, "pays": bool(p_max >= premium_req), "frakL": frakL, "premium_required": premium_req}


def growth_weight_loss(Pi_X, X_pe, X, k, alpha):
    """Score lost per year when the owner's weight X_pe replaces X: rho = ((X_pe - k)/(X - k))^{alpha/(1 - alpha)};
    loss = Pi(X)[1 - (rho - alpha rho^{1/alpha})/(1 - alpha)].

    Implements: prop:reg-lbo, prop:reg-weight(b) | Spec: 16.2 | Notes: regimes 3.3, 3.7 | Status: theory"""
    if X - k <= 0:
        return 0.0
    rho = (max(X_pe - k, 0.0) / (X - k)) ** (alpha / (1 - alpha))
    return Pi_X * (1 - (rho - alpha * rho ** (1 / alpha)) / (1 - alpha))


def hybrid_weight(X_inv, X_pub, omega_m):
    """Minority investor with board weight omega_m: X = omega_m X_inv + (1 - omega_m) X_pub.

    Implements: prop:reg-hybrid | Spec: 16.2 | Notes: regimes 3.8 | Status: theory"""
    return omega_m * X_inv + (1 - omega_m) * X_pub


def carve_out_npv(npv_core, C_sep, C_par_sh, r, T_par):
    """Carve-out: incremental NPV = NPV_core + C_sep + C_par_sh A_r(T_par) (separation costs avoided by transforming
    inside the carve-out).

    Implements: prop:reg-hybrid | Spec: 16.2 | Notes: regimes 3.8 | Status: theory"""
    return npv_core + C_sep + C_par_sh * (1 - math.exp(-r * T_par)) / r


def exit_value_of_savings(run_rate_saving, M_exit, h_x=1.0):
    """At a PE exit each dollar of seasoned run-rate EBITDA saving is worth h_x M_exit dollars.

    Implements: prop:reg-value | Spec: 16.1 | Notes: regimes 3.2 | Status: theory"""
    return _a(run_rate_saving) * M_exit * h_x


def covenant_headroom(net_debt, ebitda, cov):
    """Leverage covenant net debt / EBITDA <= cov: headroom cov EBITDA - net debt (negative = breach).

    Implements: prop:reg-dip | Spec: 16.1 | Notes: regimes 3.5 | Status: theory"""
    return cov * _a(ebitda) - _a(net_debt)


def take_private_gain(dV_private, dV_public, myopia_cost_avoided, control_premium, equity_value, extra_cost=0.0) -> float:
    """Frictionless benchmark of a change of ownership: (value of the sponsor's program - value of the public owner's)
    + avoided myopia cost - control premium x equity value - other costs.

    Implements: prop:reg-lbo (frictionless benchmark) | Spec: 16.2 | Notes: regimes 3.7 | Status: theory"""
    return dV_private - dV_public + myopia_cost_avoided - control_premium * equity_value - extra_cost


# =================================================================================================
# 19. Product strategy (spec 17; notes/theory_product_notes.md Section 3; theory_product.tex)
# =================================================================================================

def adoption_share(kap, eps):
    """Share of in-scope outcomes that adopt at capture share kap: D = (1 - kap)^eps on [0, 1].

    Implements: ass:prod-value, eq:prod-D | Spec: 17.1 | Notes: product 3.1 | Status: theory"""
    return np.maximum(0.0, 1.0 - _a(kap)) ** _a(eps)


def kappa_monopoly(cI, eps):
    """Monopoly capture share kappa^m = (1 + eps c_I)/(1 + eps), c_I = chat_I / V_I.

    Implements: prop:prod-price(a), eq:prod-kappa | Spec: 17.2 | Notes: product 3.1 | Status: theory"""
    return (1.0 + _a(eps) * _a(cI)) / (1.0 + _a(eps))


def C_ad(eps):
    """C_ad = eps^eps / (1 + eps)^(1 + eps); monopoly profit per outcome V_I C_ad (1 - c_I)^(1 + eps).

    Implements: prop:prod-price(a) | Spec: 17.2 | Notes: product 3.1 | Status: theory"""
    e = _a(eps)
    return e ** e / (1.0 + e) ** (1.0 + e)


def agent_rent(V_I, V_E, p_sw):
    """Rent per outcome rho_u = V_I - V_E + p_sw (data and workflow advantage plus switching premium).

    Implements: ass:prod-entry | Spec: 17.2 | Notes: product 3.1 | Status: theory"""
    return _a(V_I) - _a(V_E) + _a(p_sw)


def competitive_price(V_I, chat_I, chat_E, rho_u, eps, ups_E=0.0):
    """Price under AI-native entry: p* = min(p^m, pbar), p^m = kappa^m V_I, cap pbar = (1 + ups_E) chat_E + rho_u
    (ups_E = 0 is the free-entry limit). Viable iff pbar > chat_I. Returns dict(p, cap, p_m, kap, D, viable,
    capped, margin, profit, chat_E_ddag).

    Implements: prop:prod-price(b), eq:prod-cap | Spec: 17.2 | Notes: product 3.1 | Status: theory"""
    V_I, chat_I = float(V_I), float(chat_I)
    cap = (1.0 + ups_E) * float(chat_E) + float(rho_u)
    cI = chat_I / V_I if V_I > 0 else math.inf
    p_m = float(kappa_monopoly(cI, eps)) * V_I if cI < 1 else math.nan
    viable = bool(cap > chat_I and cI < 1)
    p = min(p_m, cap) if viable else math.nan
    kap = p / V_I if viable else math.nan
    D = float(adoption_share(kap, eps)) if viable else 0.0
    return {"p": p, "cap": cap, "p_m": p_m, "kap": kap, "kap_m": p_m / V_I if V_I > 0 else math.nan, "D": D,
            "viable": viable, "capped": bool(viable and cap < p_m), "margin": (p - chat_I) if viable else math.nan,
            "profit": (p - chat_I) * D if viable else 0.0, "chat_E_ddag": (p_m - float(rho_u)) if viable else math.nan}


def pass_through(chat_I, V_I, eps, capped: bool, source: str = "own"):
    """Pass-through of unit-cost changes: unconstrained eps chat/(V + eps chat); capped: 0 for the incumbent's own
    cost, 1 (times 1 + ups_E) for the entrants' cost.

    Implements: prop:prod-price(c) | Spec: 17.2 | Notes: product 3.1 | Status: theory"""
    if capped:
        return 0.0 if source == "own" else 1.0
    return float(eps * chat_I / (V_I + eps * chat_I))


def bass_B(t, p, q):
    """Bass cumulative adoption B(t) = (1 - exp(-(p+q)t)) / (1 + (q/p) exp(-(p+q)t)) (notes' fraktur p, q).

    Implements: prop:prod-seats | Spec: 17.1 | Notes: product 3.2 | Status: theory"""
    t = np.maximum(_a(t), 0.0)
    b = p + q
    e = np.exp(-b * t)
    return (1.0 - e) / (1.0 + (q / p) * e)


def bass_adoption(t, p, q):
    """Alias of bass_B (spec 17.1 name).

    Implements: prop:prod-seats | Spec: 17.1 | Notes: product 3.2 | Status: theory"""
    return bass_B(t, p, q)


def bass_f(t, p, q):
    """Adoption rate Bdot = (p + q B)(1 - B).

    Implements: prop:prod-seats | Spec: 17.1 | Notes: product 3.2 | Status: theory"""
    B = bass_B(t, p, q)
    return (p + q * B) * (1.0 - B)


def bass_tipping(p, q):
    """Tipping point t*_B = ln(q/p)/(p + q) if q > p (else 0), with B(t*) = (q - p)/(2q).

    Implements: prop:prod-seats, prop:prod-breaks | Spec: 17.3 | Notes: product 3.2 | Status: theory"""
    return math.log(q / p) / (p + q) if q > p else 0.0


def nu_seat(t, xbar, p, q):
    """Proportional seat-loss rate nu(t) = Xdot/(1 - X) for X(t) = xbar B(t).

    Implements: prop:prod-seats | Spec: 17.2 | Notes: product 3.2 | Status: theory"""
    return _a(xbar) * bass_f(t, p, q) / (1.0 - _a(xbar) * bass_B(t, p, q))


def nu_peak(xbar, p, q):
    """Peak of the seat-loss rate: if q > p(1 - xbar), Bhat = [1 - sqrt((1 - xbar)(1 + xbar p/q))]/xbar at
    t_hat = ln((1 + q Bhat/p)/(1 - Bhat))/(p + q); else nu falls from nu(0) = xbar p. Returns (t_hat, nu_max).

    Implements: prop:prod-seats, eq:prod-Bhat | Spec: 17.3 | Notes: product 3.2 | Status: theory"""
    if xbar <= 0:
        return 0.0, 0.0
    if q > p * (1 - xbar):
        Bh = (1.0 - math.sqrt((1.0 - xbar) * (1.0 + xbar * p / q))) / xbar
        th = math.log((1.0 + q * Bh / p) / (1.0 - Bh)) / (p + q)
        return th, float(nu_seat(th, xbar, p, q))
    return 0.0, xbar * p


def revenue_at_risk(seat_revenue, eps_seat, xbar_h, B=1.0):
    """Seat revenue at risk RaR = eps_seat xbar_h B(t) R_0 at constant volume; at full adoption eps_seat xbar_h R_0.

    Implements: prop:prod-seats | Spec: 17.2 | Notes: product 3.2 | Status: theory"""
    return _a(eps_seat) * _a(xbar_h) * _a(B) * _a(seat_revenue)


def migration_threshold(r, g_v, delta, e, omega, varpi):
    """Seat-loss rate above which migrating to a tariff pays: nu*_k = (r - g)(varpi delta + omega (r - g)) /
    (varpi (1 - delta)(1 - e) - omega (r - g)); None if the denominator is not positive (never).

    Implements: prop:prod-migrate(b), eq:prod-nustar | Spec: 17.2, 17.3 | Notes: product 3.3 | Status: theory"""
    rg = r - g_v
    den = varpi * (1 - delta) * (1 - e) - omega * rg
    if den <= 0:
        return None
    return rg * (varpi * delta + omega * rg) / den


def migration_value(T, X, R0, gamma, r, g_v, delta, e, omega, varpi, horizon=200.0, n=4001):
    """Value of migrating at T: V_k(T) = varpi gamma R0 int_T^inf e^{-(r-g)t}[(1 - delta)((1 - e)(1 - X(T)) +
    e (1 - X(t))) - (1 - X(t))] dt - e^{-rT} omega gamma R_S(T), R_S(T) = R0 e^{gT}(1 - X(T)). X is a callable.

    Implements: ass:prod-migrate, prop:prod-migrate(a) | Spec: 17.2 | Notes: product 3.3 | Status: theory"""
    ts = np.linspace(T, T + horizon, n)
    XT = float(np.asarray(X(np.array([T])), float).ravel()[0])
    Xt = np.asarray(X(ts), float)
    f = np.exp(-(r - g_v) * ts) * ((1 - delta) * ((1 - e) * (1 - XT) + e * (1 - Xt)) - (1 - Xt))
    I = float(np.trapezoid(f, ts)) if hasattr(np, "trapezoid") else float(np.trapz(f, ts))
    RS = R0 * math.exp(g_v * T) * (1 - XT)
    return varpi * gamma * R0 * I - math.exp(-r * T) * omega * gamma * RS


def first_crossing(fun, level, t_max=60.0, n=6001):
    """First t in [0, t_max] with fun(t) >= level (0 if already; None if never), by grid and bisection.

    Implements: prop:prod-migrate(c) | Spec: 17.3 | Notes: product 3.3 | Status: theory"""
    ts = np.linspace(0.0, t_max, n)
    vals = np.asarray(fun(ts), float) - level
    if vals[0] >= 0:
        return 0.0
    idx = np.flatnonzero((vals[:-1] < 0) & (vals[1:] >= 0))
    if len(idx) == 0:
        return None
    a, b = ts[idx[0]], ts[idx[0] + 1]
    for _ in range(60):
        m = 0.5 * (a + b)
        if float(fun(np.array([m]))[0]) - level >= 0:
            b = m
        else:
            a = m
    return 0.5 * (a + b)


def feature_npv(S, X, k, Dstar, r_minus_g, ups, c0, dec_u, dG, dlam, F_cost, p, q, horizon=300.0, n=6001):
    """Feature NPV at weight X: S int_0^inf e^{-(r - g)t} B_f(t)[ups - c0 e^{-dec t} + (X - k)(dG + Delta* dlam)] dt - F.
    The (X - k) term is the value of the retention point.

    Implements: prop:prod-portfolio(a), eq:prod-feature | Spec: 17.1 | Notes: product 3.4 | Status: theory"""
    ts = np.linspace(0.0, horizon, n)
    Rf = ups - c0 * np.exp(-dec_u * ts) + (X - k) * (dG + Dstar * dlam)
    f = np.exp(-r_minus_g * ts) * bass_B(ts, p, q) * Rf
    integ = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return float(S * integ(f, ts) - F_cost)


def retention_breakeven(X, k, dG, Dstar, dlam, c_f, ups):
    """Retention outweighs margin iff (X - k)(dG + Delta* dlam) > c_f - ups.

    Implements: prop:prod-portfolio(c) | Spec: 17.1 | Notes: product 3.4 | Status: theory"""
    return (X - k) * (dG + Dstar * dlam) > c_f - ups


def knapsack(values, costs, capacity, fixed=0.0):
    """Feature portfolio: max sum x_f NPV_f - F_plat 1{any} s.t. sum x_f n_f <= capacity; exact enumeration up to 20
    items, else greedy by value per unit of capacity. Returns (chosen indices, value, shadow value per unit).

    Implements: prop:prod-portfolio(b) | Spec: 17.1 | Notes: product 3.4 | Status: theory"""
    v, c = list(map(float, values)), list(map(float, costs))
    n = len(v)
    best, best_set = 0.0, []
    if n <= 20:
        for m in range(1, 1 << n):
            sel = [i for i in range(n) if m >> i & 1]
            if sum(c[i] for i in sel) > capacity + 1e-9:
                continue
            val = sum(v[i] for i in sel) - fixed
            if val > best:
                best, best_set = val, sel
    else:
        order = sorted(range(n), key=lambda i: -v[i] / max(c[i], 1e-12))
        used = 0.0
        for i in order:
            if v[i] > 0 and used + c[i] <= capacity:
                best_set.append(i)
                used += c[i]
        best = sum(v[i] for i in best_set) - (fixed if best_set else 0.0)
    order = sorted(range(n), key=lambda i: -v[i] / max(c[i], 1e-12))
    used, shadow = 0.0, 0.0
    for i in order:
        if v[i] <= 0:
            break
        if used + c[i] > capacity:
            shadow = v[i] / max(c[i], 1e-12)
            break
        used += c[i]
    return sorted(best_set), best, shadow


def sourcing_net_unit(cv, ci, dec, K, rho, r, delta_K, t=0.0):
    """Net unit cost of a model-sourcing option: c_var(t) + (r + delta_K) K - rho, with the inference part declining
    at dec (zero for vintage-locked options).

    Implements: prop:prod-model | Spec: 17.1 | Notes: product 3.5 | Status: theory"""
    return cv - ci + ci * math.exp(-dec * t) + (r + delta_K) * K - rho


def sourcing_threshold(net1, net2, Ft1, Ft2):
    """Volume above which option 2 beats option 1: (Ftilde_2 - Ftilde_1)/(net_1 - net_2) if net_1 > net_2, else inf.

    Implements: prop:prod-model | Spec: 17.1 | Notes: product 3.5 | Status: theory"""
    d = net1 - net2
    return (Ft2 - Ft1) / d if d > 0 else math.inf


def own_model_test(rho_m, rho_api, cv_m, K_m, ch_api, r, delta_K):
    """Long-run own-model test: option m beats the API at some volume only if rho_m - rho_api > c_var_m + (r + delta_K) K_m
    - c^h_api.

    Implements: prop:prod-model(c) | Spec: 17.1 | Notes: product 3.5 | Status: theory"""
    return rho_m - rho_api > cv_m + (r + delta_K) * K_m - ch_api


def gross_margin_path(t, gamma0, f, u_h, u_c, delta_u, phi):
    """AI product gross margin gamma_AI(t) = 1 - f - (1 - f - gamma0)(u(t)/u0)^(1 - phi), u(t) = u_h + u_c e^{-delta_u t}.

    Implements: prop:prod-margin, eq:prod-Tx | Spec: 17.2 | Notes: product 3.6 | Status: theory"""
    u0 = u_h + u_c
    u = u_h + u_c * np.exp(-delta_u * _a(t))
    return 1.0 - f - (1.0 - f - gamma0) * (u / u0) ** (1.0 - phi)


def margin_crossover(gamma0, f, u_h, u_c, delta_u, phi, gamma_sub):
    """Date at which the AI margin crosses the subscription margin: T_x = ln{u_c/[u0 z^(1/(1-phi)) - u_h]}/delta_u,
    z = (1 - f - gamma_sub)/(1 - f - gamma0); None if gamma_inf <= gamma_sub. Also returns gamma_inf.

    Implements: prop:prod-margin | Spec: 17.2, 17.3 | Notes: product 3.6 | Status: theory"""
    u0 = u_h + u_c
    g_inf = 1.0 - f - (1.0 - f - gamma0) * (u_h / u0) ** (1.0 - phi) if u0 > 0 else gamma0
    if g_inf <= gamma_sub or delta_u <= 0 or phi >= 1:
        return None, g_inf
    z = (1.0 - f - gamma_sub) / (1.0 - f - gamma0)
    den = u0 * z ** (1.0 / (1.0 - phi)) - u_h
    if den <= 0:
        return None, g_inf
    return max(math.log(u_c / den) / delta_u, 0.0), g_inf


def cannibalization(V_I, chat_I, eps, p_seat, t, t_FTE, gamma_seat, p_sw, nu_E, r, g_v, cap=None):
    """Replacement effect and preemption (prop:prod-cannibal): m_seat = gamma_seat p_seat t/t_FTE; without entrants
    kappa_can = (1 + eps(c_I + s))/(1 + eps), launch iff c_I + s < 1, replacement cost V C_ad[(1-c_I)^(1+eps) -
    (1-c_I-s)^(1+eps)]; with entry hazard nu_E: c_eff = chat_I + m_seat - nu_E p_sw/(r - g), launch now iff V > c_eff,
    nu_E* = (r - g)(chat_I + m_seat - V)/p_sw, launch price p_L = max(0, (V + eps c_eff)/(1 + eps)).

    Implements: prop:prod-cannibal | Spec: 17.3 item 7 | Notes: product 3.7 | Status: theory"""
    m_seat = gamma_seat * p_seat * t / t_FTE
    cI, sh = chat_I / V_I, m_seat / V_I
    kap_can = (1 + eps * (cI + sh)) / (1 + eps)
    Ca = float(C_ad(eps))
    launch_monopoly = cI + sh < 1
    gain = V_I * Ca * max(1 - cI - sh, 0.0) ** (1 + eps)
    repl = V_I * Ca * (max(1 - cI, 0.0) ** (1 + eps) - max(1 - cI - sh, 0.0) ** (1 + eps))
    rg = max(r - g_v, 1e-9)
    c_eff = chat_I + m_seat - nu_E * p_sw / rg
    nu_star = rg * (chat_I + m_seat - V_I) / p_sw if (chat_I + m_seat > V_I and p_sw > 0) else 0.0
    p_L = max(0.0, (V_I + eps * c_eff) / (1 + eps))
    if cap is not None:
        p_L = min(p_L, cap)
    val_now = (p_L - c_eff) * float(adoption_share(p_L / V_I, eps)) / (rg + nu_E) if V_I > c_eff else 0.0
    return {"m_seat": m_seat, "s": sh, "W_ratio": V_I * t_FTE / (t * p_seat), "kap_can": kap_can,
            "launch_without_entry": bool(launch_monopoly), "gain": gain, "replacement_cost": repl,
            "replacement_share": repl / max(V_I * Ca * max(1 - cI, 0.0) ** (1 + eps), 1e-12),
            "c_eff": c_eff, "launch_now": bool(V_I > c_eff), "nu_E_star": nu_star, "p_L": p_L, "value_now_vs_entry": val_now}


def product_delta_R(d_gamma, d_a, d_k, d_Gi, d_lam_rel, X, k, g_star, delta_K, Dstar):
    """First-order change in the Rule-of-X score from product strategy: Delta R* = Delta gamma - Delta a
    - (g* + delta_K) Delta k + (X - k) Delta G_i + (X - k) Delta* Delta lambda/lambda.

    Implements: prop:prod-aggregate, eq:prod-dR | Spec: 17.3 item 5 | Notes: product 3.8 | Status: theory"""
    return d_gamma - d_a - (g_star + delta_K) * d_k + (X - k) * d_Gi + (X - k) * Dstar * d_lam_rel


def dilution_test(D_m, dG, X, k):
    """Margin dilution for growth: Delta R* = -D_m + (X - k) Delta G; it pays at weight X iff X - k > D_m / Delta G.

    Implements: cor:prod-dilution | Spec: 17.3 item 5 | Notes: product 3.8 | Status: theory"""
    return {"delta_R": -D_m + (X - k) * dG, "pays": bool(-D_m + (X - k) * dG > 0),
            "break_even_weight": (D_m / dG + k) if dG > 0 else math.inf}


def complementarity_value_pricing(du_share, phi_value, phi_costplus):
    """Complementarity of value pricing and COGS automation (Topkis): the margin gain of an automation that cuts unit
    cost by du_share of price is (1 - phi) du_share, so value pricing (phi = 0 when capped) adds (phi_costplus - phi_value)
    du_share over cost-plus pricing (phi = 1).

    Implements: prop:prod-aggregate (complementarity) | Spec: 17.3 item 5 | Notes: product 3.8 | Status: theory"""
    return (phi_costplus - phi_value) * du_share


def value_based_price(labor_saved, kappa_cap, floor=0.0, moat=None):
    """Reduced form when a line gives no customer economics: price = max(floor, kappa_cap x customer labor saved).

    Implements: prop:prod-price (reduced form) | Spec: 17.2 | Notes: product 5 (capture share default) | Status: provisional"""
    return np.maximum(_a(floor), _a(kappa_cap) * _a(labor_saved))


def gross_margin(price, unit_cogs):
    """Gross margin 1 - unit cost / price.

    Implements: - | Spec: 17.2 | Notes: product 3.6 | Status: theory"""
    return 1.0 - _a(unit_cogs) / np.maximum(_a(price), 1e-12)


# =================================================================================================
# 20. AI failure modes, autonomy and controls (spec 23; core 4.13: props halluc, bias, autonomy, pipeline)
# =================================================================================================

AUTONOMY_LEVELS = ("read", "draft", "act_with_approval", "act_autonomously")


def stakes_coverage(xi):
    """Share of stakes-weighted errors that fall in the top-xi share reviewed when stakes are exponential:
    G(xi) = xi (1 + ln(1/xi)); G(0) = 0, G(1) = 1. It is the factor in the core's quality cost.

    Implements: prop:tasks-review | Spec: 3, 23.1 | Notes: core 4.2 | Status: theory"""
    xi = np.clip(_a(xi), 0.0, 1.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(xi > 0, xi * (1.0 + np.log(1.0 / np.maximum(xi, 1e-300))), 0.0)


def catchable_rate(e_o, e_h, d_o, d_h):
    """Total and catchable error rates: ebar = e_o + e_h, etil = e_o d_o + e_h d_h.

    Implements: prop:tasks-halluc | Spec: 23.1 | Notes: core 4.13 | Status: theory"""
    return _a(e_o) + _a(e_h), _a(e_o) * _a(d_o) + _a(e_h) * _a(d_h)


def quality_cost_tax(xi, e_o, e_h, d_o, d_h, L, w_tR):
    """Quality cost with ordinary errors and hallucinations: c_Q(xi) = w t_R xi + etil L [1 - xi (1 + ln(1/xi))]
    + (ebar - etil) L. The last term is the review-proof floor.

    Implements: prop:tasks-halluc(a) | Spec: 23.1 | Notes: core 4.13 | Status: theory"""
    ebar, etil = catchable_rate(e_o, e_h, d_o, d_h)
    return _a(w_tR) * _a(xi) + etil * _a(L) * (1.0 - stakes_coverage(xi)) + (ebar - etil) * _a(L)


def review_share_tax(e_o, e_h, d_o, d_h, L, w_tR, qbar, xi_min, eps_d=None):
    """Optimal review share and feasibility with hallucination: xi_E = exp(-w t_R/(etil L)), xi_R = (ebar - epsbar)/etil,
    xi* = min(1, max(xi_E, xi_R, xi_min)), epsbar = 1 - qbar. Infeasible (exclude A) if ebar - etil > epsbar.
    With a vigilance elasticity eps_d (automation bias, prop:tasks-bias(b)) review beyond exp(-eps_d) catches fewer
    errors, so the economic share is capped there and a reliability share above the cap is infeasible (unless a
    regulatory floor forces it). Returns (xi, feasible, undetected rate ebar - etil xi).

    Implements: prop:tasks-halluc(b), prop:tasks-bias(b) | Spec: 8.3, 23.1 | Notes: core 4.13 | Status: theory"""
    ebar, etil = catchable_rate(e_o, e_h, d_o, d_h)
    etil_s = np.maximum(etil, 1e-12)
    epsbar = 1.0 - _a(qbar)
    xiE = np.exp(-_a(w_tR) / (etil_s * np.maximum(_a(L), 1e-12)))
    xiR = np.where(ebar > epsbar, (ebar - epsbar) / etil_s, 0.0)
    feasible = (ebar - etil) <= epsbar + 1e-12
    if eps_d is not None and np.all(_a(eps_d) > 0):
        cap = np.exp(-_a(eps_d))
        feasible = feasible & (xiR <= cap + 1e-12)
        xiE = np.minimum(xiE, cap)
    xi = np.clip(np.maximum(np.maximum(xiE, xiR), _a(xi_min)), 0.0, 1.0)
    return xi, feasible, ebar - etil * xi


def caught_errors(xi, e, eps_d, dbar=0.9, e0=0.1):
    """Errors caught per unit under prevalence-dependent vigilance: prevalence among reviewed units
    ebar(xi) = e (1 + ln(1/xi)); catch d = min(1, dbar (ebar/e0)^eps_d); K(xi) = e xi (1 + ln(1/xi)) d. K peaks at
    xi = exp(-eps_d) when d < 1 (more review buys less beyond it).

    Implements: prop:tasks-bias(a)-(b) | Spec: 23.1 | Notes: core 4.13 | Status: theory"""
    xi = np.clip(_a(xi), 1e-12, 1.0)
    prev = _a(e) * (1.0 + np.log(1.0 / xi))
    d = np.minimum(1.0, _a(dbar) * (prev / e0) ** _a(eps_d))
    return _a(e) * stakes_coverage(xi) * d, d


def bias_target_attainable(d0, e, eps_d, eps_bar, prevalence0):
    """Detection threshold under automation bias (prop:tasks-bias(d)): with the catch rate falling with error
    prevalence, d^R(ebar) = d0 (ebar/ebar_0)^eps_d, the target eps_bar is attainable iff
    d^R(e(1+eps_d)) >= (1 - eps_bar/e) e^eps_d/(1+eps_d); the factor e^eps/(1+eps) > 1 (1.10 at eps_d = 0.5)
    tightens the unbiased threshold d >= 1 - eps_bar/e.

    Implements: prop:tasks-bias(d) | Spec: 23.1 | Notes: core 4.13 | Status: theory"""
    e, ed = _a(e), _a(eps_d)
    d_at = _a(d0) * (e * (1 + ed) / np.maximum(_a(prevalence0), 1e-12)) ** ed
    return d_at >= (1 - _a(eps_bar) / np.maximum(e, 1e-12)) * np.exp(ed) / (1 + ed) - 1e-12


def pipeline_success_decomposed(d_steps, Hcal, form="logistic", eta_r=1.161):
    """Success of an agent pipeline whose steps take d_k human hours (prop:tasks-pipeline(d)): under a constant
    hazard 2^(-sum d_k/Hcal), so only total human time matters; under the logistic form
    prod_k [1 + (d_k/Hcal)^(1/eta_r)]^(-1), which with eta_r >= 1 penalizes splitting a step.

    Implements: prop:tasks-pipeline(d) | Spec: 23.1 | Notes: core 4.13 | Status: theory"""
    d = _a(d_steps)
    if form == "constant_hazard":
        return float(2.0 ** (-np.sum(d) / float(Hcal)))
    return float(np.prod((1 + (d / float(Hcal)) ** (1.0 / float(eta_r))) ** (-1.0)))


def irony_flag(caught_share, eps_d):
    """Irony of automation: d(undetected)/de = 1 - (1 + eps_d) K/e < 0 when review catches more than 1/(1 + eps_d) of
    errors, so a more accurate model raises undetected errors.

    Implements: prop:tasks-bias(c) | Spec: 23.1 | Notes: core 4.13 | Status: theory"""
    return _a(caught_share) > 1.0 / (1.0 + _a(eps_d))


def catch_rate(d0, accuracy, b_ab, acc0, xi=0.0, phi_v=0.0):
    """Reviewer catch rate with complacency: d = d0 [1 - b_ab (acc - acc0)_+/(1 - acc0)] (1 - phi_v xi), the data
    agent's parametrization (params_reliability.yaml automation_bias). The core's form is caught_errors.

    Implements: - | Spec: 23.1 (automation bias) | Notes: params_reliability.yaml automation_bias | Status: provisional"""
    acc = _a(accuracy)
    bias = 1.0 - _a(b_ab) * np.clip((acc - acc0) / max(1.0 - acc0, 1e-9), 0.0, 1.0)
    return np.clip(_a(d0) * bias * (1.0 - _a(phi_v) * _a(xi)), 0.0, 1.0)


def hallucination_rate(h_type, iota, grounding, e_cap, r_A, floor_share=0.1):
    """Confident fabrication rate h = h_type (1 - grounding iota) max(floor, min(1, e_cap/(1 - r_A))): lower for
    retrieval-grounded tasks and with integrated data, falling as capability passes the feasibility line.

    Implements: - | Spec: 23.1(ii) | Notes: core 4.13 takes e_h as an input | Status: provisional"""
    capf = np.clip(_a(e_cap) / max(1.0 - r_A, 1e-9), floor_share, 1.0)
    return _a(h_type) * (1.0 - _a(grounding) * np.clip(_a(iota), 0, 1)) * capf


def misbehavior_rate(m0, autonomy_mult, d_eff, kappa_h, external_share, injection_mult, guard_cut=0.0):
    """Agentic misbehavior per unit of work: e_m = m0 x autonomy multiplier x (d_eff / 1 h)^kappa_h
    x (1 + injection_mult x external inputs) x (1 - guard_cut). It rises with autonomy and task horizon.

    Implements: ass:tasks-failure | Spec: 23.1(iii) | Notes: core 4.13 takes e_m(a) as an input | Status: provisional"""
    hor = np.maximum(_a(d_eff), 1e-3) ** kappa_h
    return _a(m0) * _a(autonomy_mult) * hor * (1.0 + _a(injection_mult) * np.clip(_a(external_share), 0, 1)) * (1.0 - guard_cut)


def emin_pareto(Zbar, p):
    """E min{Z, Zbar} for Z ~ Pareto(p) with scale 1: 1 + (1 - Zbar^(1-p))/(p - 1); 1 + ln Zbar at p = 1; p/(p - 1)
    uncapped (Zbar = inf) for p > 1 and infinite for p <= 1.

    Implements: prop:tasks-autonomy(a) | Spec: 23.1 | Notes: core 4.13 | Status: theory"""
    Z, p = np.maximum(_a(Zbar), 1.0), _a(p)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        capped = np.where(np.abs(p - 1) < 1e-12, 1.0 + np.log(Z), 1.0 + (1.0 - Z ** (1.0 - p)) / np.where(np.abs(p - 1) < 1e-12, 1.0, p - 1))
        unc = np.where(p > 1, p / np.maximum(p - 1, 1e-12), np.inf)
    return np.where(np.isinf(Z), unc, capped)


def pareto_mean(alpha, x_m, cap=None):
    """Mean of a Pareto(alpha, x_m) loss, truncated at `cap` (a kill switch or least-privilege limit) if given:
    x_m E min{Z, cap/x_m}.

    Implements: prop:tasks-autonomy(a) | Spec: 23.1 | Notes: core 4.13 | Status: theory"""
    xm = _a(x_m)
    Z = np.inf if cap is None else np.maximum(_a(cap), xm) / np.maximum(xm, 1e-300)
    return xm * emin_pareto(Z, alpha)


def misbehavior_cost(e_m, d_m, L_m, L_cap, p):
    """Expected misbehavior loss per unit c_m(a) = e_m(a) (1 - d_m(a)) L_m(a) E min{Z, L_cap(a)/L_m(a)}.

    Implements: prop:tasks-autonomy | Spec: 23.1 | Notes: core 4.13 | Status: theory"""
    Zb = np.inf if L_cap is None else np.maximum(_a(L_cap), _a(L_m)) / np.maximum(_a(L_m), 1e-300)
    return _a(e_m) * (1.0 - _a(d_m)) * _a(L_m) * emin_pareto(Zb, p)


def event_cvar(L_m, p, q, L_cap=None):
    """Conditional value at risk of one misbehavior event: min(L_cap, L_m p (1 - q)^(-1/p)/(p - 1)); the cap if
    p <= 1 (infinite without one).

    Implements: prop:tasks-autonomy(a) | Spec: 23.1 | Notes: core 4.13 | Status: theory"""
    Lm, p = _a(L_m), _a(p)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        unc = np.where(p > 1, Lm * p * (1.0 - q) ** (-1.0 / np.maximum(p, 1e-12)) / np.maximum(p - 1, 1e-12), np.inf)
    return unc if L_cap is None else np.minimum(unc, _a(L_cap))


def optimal_autonomy(costs, feasible, irreversible=None):
    """a* = argmin over feasible levels of c(a) = w t(a) + c_Q(a) + c_m(a) (levels 0 read, 1 draft, 2 act with
    approval, 3 act autonomously, last axis). Irreversible actions: level 3 is allowed only if it satisfies the
    risk appetite, and automation (levels 2, 3) is out of scope if level 2 does not (prop:tasks-autonomy(d)).
    Returns (level, cost); level -1 if none is feasible.

    Implements: prop:tasks-autonomy(b), (d) | Spec: 23.1 | Notes: core 4.13 | Status: theory"""
    c = np.where(_a(feasible).astype(bool), _a(costs), np.inf)
    if irreversible is not None:
        irr = np.asarray(irreversible, bool)[..., None]
        lvl = np.arange(c.shape[-1])
        no2 = ~np.asarray(feasible, bool)[..., 2:3]
        c = np.where(irr & no2 & (lvl >= 2), np.inf, c)
    a = np.argmin(c, axis=-1)
    best = np.take_along_axis(c, a[..., None], axis=-1)[..., 0]
    return np.where(np.isfinite(best), a, -1), best


def pipeline_success(eps, J, k=1):
    """Pipeline of J steps failing undetected with probability eps each: success (1 - eps)^(J k) on k tasks in a
    row (pass^k).

    Implements: prop:tasks-pipeline(a), lem:tasks-oring | Spec: 23.1(v) | Notes: core 4.13 | Status: theory"""
    return (1.0 - _a(eps)) ** (_a(J) * k)


def max_pipeline_length(eps, qbar, k=1, J_s=None, d_c=None):
    """Longest pipeline meeting the target qbar: floor(ln qbar / (k ln(1 - eps))); with a checkpoint every J_s steps
    that catches a failed segment with probability d_c: J_s ln qbar / ln(1 - [1 - (1 - eps)^J_s](1 - d_c)).

    Implements: prop:tasks-pipeline(a)-(b) | Spec: 23.1(v) | Notes: core 4.13 | Status: theory"""
    eps = np.clip(_a(eps), 1e-15, 1 - 1e-15)
    lq = np.log(np.clip(_a(qbar), 1e-300, 1.0))
    if J_s is None or d_c is None:
        return np.floor(lq / (k * np.log1p(-eps)))
    seg = (1.0 - (1.0 - eps) ** J_s) * (1.0 - _a(d_c))
    return J_s * lq / np.log1p(-np.clip(seg, 1e-15, 1 - 1e-15))


def cascade_loss(eps, J, L_c):
    """Expected loss per run when an undetected error is acted on by every later step, each adding L_c:
    L_c [J - (1 - eps)(1 - (1 - eps)^J)/eps], about L_c eps J (J + 1)/2.

    Implements: prop:tasks-pipeline(c) | Spec: 23.1(v) | Notes: core 4.13 | Status: theory"""
    eps = np.maximum(_a(eps), 1e-15)
    J = _a(J)
    return _a(L_c) * (J - (1.0 - eps) * (1.0 - (1.0 - eps) ** J) / eps)


def pipeline_reliability(eps_steps) -> float:
    """Reliability of a pipeline with step-specific undetected error rates: prod_k (1 - eps_k); the target requires
    sum_k -ln(1 - eps_k) <= -ln qbar (position-dependent errors, notes/modern_theory_map.md change 3(c)).

    Implements: lem:tasks-oring | Spec: 23.1(v) | Notes: core 4.6; modern map 3(c) | Status: theory"""
    return float(np.prod(1.0 - np.clip(_a(eps_steps), 0.0, 1.0)))


def error_floor_cost(xi, e_o, e_h, d_o, d_h, L, c_m):
    """Per-unit error cost that review cannot remove and that is not review labor or a security incident (for the
    Part I ceiling): c_err = etil L [1 - xi(1 + ln(1/xi))] + (ebar - etil) L + c_m(a*).

    Implements: prop:tasks-halluc, cor:tasks-failure | Spec: 22, 23.1 | Notes: core 4.13 | Status: theory"""
    ebar, etil = catchable_rate(e_o, e_h, d_o, d_h)
    return etil * _a(L) * (1.0 - stakes_coverage(xi)) + (ebar - etil) * _a(L) + _a(c_m)


def undetected_rate_remaining_review(e_o, e_h, d_o, d_h, chi=1.0, n_r=0):
    """Undetected error rate under the review that remains at full automation (Part I lem:fullcost(c); Paper 2
    prop:tasks-cerr(c)): n_r AI review layers whose failures are common with the reviewed model on the share chi of
    errors and otherwise catch ordinary errors and hallucinations with d_o and d_h:
    u = e_o [chi + (1 - chi)(1 - d_o)^{n_r}] + e_h [chi + (1 - chi)(1 - d_h)^{n_r}]. No review (n_r = 0) gives
    e_o + e_h; with depth u falls to chi (e_o + e_h), so an error requirement eps_bar is met at some depth iff
    chi (e_o + e_h) < eps_bar. For one reviewer (n_r = 1) the catch rate is (1 - chi) d, chi the reviewer's common-mode
    probability rho^cm (close to one on the same model).

    Implements: prop:tasks-cerr(c), lem:fullcost | Spec: 22, 23.1 | Notes: core 4.13 | Status: theory"""
    chi, n_r = float(chi), int(n_r)
    if n_r <= 0:
        return _a(e_o) + _a(e_h)
    return _a(e_o) * (chi + (1 - chi) * (1 - _a(d_o)) ** n_r) + _a(e_h) * (chi + (1 - chi) * (1 - _a(d_h)) ** n_r)


def cerr_remaining_review(e_o, e_h, L, c_m, d_o=0.0, d_h=0.0, chi=1.0, n_r=0):
    """Per-unit error and misbehavior loss floor at full automation, evaluated at the review that remains
    (prop:tasks-cerr(c)): every output is reviewed by the AI layers (their marginal cost is negligible), so
    c_err = u L + c_m with u from undetected_rate_remaining_review; with no review c_err = (e_o + e_h) L + c_m.
    Evaluating c_err at human catch rates for a firm without people understates it.

    Implements: prop:tasks-cerr(c), lem:fullcost | Spec: 22, 23.1 | Notes: core 4.13 | Status: theory"""
    return undetected_rate_remaining_review(e_o, e_h, d_o, d_h, chi, n_r) * _a(L) + _a(c_m)


def nu_common_mode(nu_out, nu_reg, q_chg=0.0):
    """Rate of common-mode events at a provider (ass:ext-commonmode; Part I lem:fullcost(e)):
    nu_cm = nu_out + (1 - q_chg) nu_reg, outages and shared vulnerabilities the firm does not control plus the
    regressions from changes to the model, prompts or tools that its change-management controls (pinned versions,
    testing before promotion, rollback) do not stop; q_chg is the share they stop (nu^chg(kappa_itgc) nonincreasing).

    Implements: ass:ext-commonmode, prop:ext-commonmode(f), lem:fullcost | Spec: 23.1(iv) | Notes: ext 4.8 | Status: theory"""
    return float(nu_out) + (1.0 - float(np.clip(q_chg, 0.0, 1.0))) * float(nu_reg)


def cvar_compound_pareto(Lambda, alpha, x_m, q=0.95, cap=None):
    """CVaR_q of the annual loss of a compound Poisson process (rate Lambda) with Pareto(alpha, x_m) severities,
    in the single-big-jump approximation: if Lambda <= 1 - q the tail is an occurrence tail, CVaR = E[S]/(1 - q);
    otherwise VaR = x_m (Lambda/(1 - q))^(1/alpha) and CVaR = VaR alpha/(alpha - 1). A cap truncates severities.
    The core gives the event CVaR (event_cvar); this annual aggregate is the engine's, for risk reporting.

    Implements: - | Spec: 23.1 (tail loss) | Notes: core 4.13 notes annual tails are not closed-form | Status: provisional"""
    Lam, al, xm = _a(Lambda), _a(alpha), _a(x_m)
    EL = Lam * pareto_mean(al, xm, cap)
    occ = EL / (1.0 - q)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        var = xm * (np.maximum(Lam, 1e-300) / (1.0 - q)) ** (1.0 / al)
        sev_tail = np.where(al > 1, var * al / np.maximum(al - 1, 1e-12), np.inf)
    if cap is not None:
        sev_tail = np.minimum(sev_tail, np.maximum(_a(cap), xm))
    return np.where(Lam <= 1.0 - q, occ, np.maximum(sev_tail, EL))


def concentration_hhi(shares) -> float:
    """Herfindahl index of provider shares (1 = one provider for everything).

    Implements: - | Spec: 23.1(iv) | Notes: none | Status: spec"""
    s = _a(shares)
    s = s / max(float(s.sum()), 1e-12)
    return float(np.sum(s * s))


def common_mode_loss_variance(nu_cm, loss_by_process, provider_of, rho=1.0) -> float:
    """Variance of the annual common-mode loss when each provider fails at rate nu_cm and a failure hits a share rho
    of the processes on it fully (rho = 1: all of them): nu_cm sum_k [rho (sum_{p on k} loss_p)^2 + (1 - rho)
    sum_{p on k} loss_p^2]. Spreading processes over providers lowers it; the mean does not change.

    Implements: - | Spec: 23.1(iv) | Notes: none | Status: spec"""
    loss = _a(loss_by_process)
    prov = np.asarray(provider_of)
    tot = 0.0
    for k in np.unique(prov):
        lk = loss[prov == k]
        tot += rho * float(lk.sum()) ** 2 + (1 - rho) * float(np.sum(lk ** 2))
    return float(nu_cm * tot)


# =================================================================================================
# 21. Dated security costs, accounting and labor law (spec 20.2, 24.4 to 24.6)
# =================================================================================================

def pqc_cost_path(years, it_spend, cost_share, start_year, deadline, inventory_years=1.0):
    """Post-quantum cryptography migration: a one-time cost C_PQC = cost_share x IT spend, spread evenly from the end
    of the inventory to the deadline (NIST IR 8547: deprecated after 2030, disallowed after 2035). Years past the
    deadline carry nothing; a deadline already passed puts the whole cost in the first year.

    Implements: modern map change 9 (ass:tasks-ancillary(v)) | Spec: 20.2 | Notes: modern_theory_map.md 12 | Status: spec"""
    yrs = _a(years)
    total = float(cost_share) * float(it_spend)
    s0 = min(float(start_year) + float(inventory_years), float(deadline) - 1.0)
    span = max(float(deadline) - s0, 1e-9)
    w = np.clip(np.minimum(yrs + 0.5, deadline) - np.maximum(yrs - 0.5, s0), 0.0, None) / span
    if w.sum() <= 1e-12:                     # deadline already passed or before the plan: pay now
        w = np.zeros(len(yrs))
        w[0] = 1.0
    return total * w


def notice_delay_years(fte_by_site, warn_days, warn_threshold, eu_days, works_council, council_months, union_share,
                       union_months, region):
    """Earliest separation after the decision, by site: U.S. sites above the WARN threshold wait warn_days; EU and
    UK sites wait the collective-redundancy notification period; a works council adds its consultation, union
    coverage its bargaining period (in proportion to coverage). Returns years, by site. Superseded in the engine
    by statutory_terms and cutover_date (theory_labor); kept for comparison.

    Implements: - | Spec: 24.5 | Notes: labor 3.1 | Status: superseded"""
    f = _a(fte_by_site)
    reg = np.asarray(region)
    us = (reg == "US") & (f >= warn_threshold)
    eu = np.isin(reg, ["EU", "UK"])
    days = np.where(us, warn_days, 0.0) + np.where(eu, eu_days, 0.0)
    months = _a(works_council) * council_months + _a(union_share) * union_months
    return days / 365.0 + months / 12.0


def severance_recognition(severance, communicate_year, separation_year, standard="asc420", retention_days=60.0):
    """GAAP timing of severance (ASC 420 and 712): an ongoing benefit plan (ASC 712) accrues the whole amount when
    the plan is approved (communication year); one-time benefits (ASC 420) are recognized at communication if staff
    leave within the minimum retention period, otherwise ratably to the separation date. Returns {year: amount}.

    Implements: - | Spec: 24.4 | Notes: notes/accounting_notes.md pending | Status: spec"""
    c, sep = int(communicate_year), int(separation_year)
    if standard == "asc712" or sep <= c or (sep - c) * 365.0 <= retention_days:
        return {c: float(severance)}
    n = sep - c + 1
    return {c + i: float(severance) / n for i in range(n)}


def psi_amortization(r, T=15):
    """Present value per dollar of a tax deduction amortized over T years from the midpoint of year 1 (26 U.S.C.
    sec. 174(a) for foreign research): psi_T = [1 + (1+r)^-T]/(2T) + [1 - (1+r)^-(T-1)]/(rT). psi_15 = 0.532 at
    r = 0.10. Domestic research is deducted when paid (sec. 174A), psi = 1.

    Implements: prop:acct-tax | Spec: 24.4 | Notes: accounting 4.3 | Status: theory"""
    r = float(r)
    if r <= 0:
        return 1.0
    return (1.0 + (1.0 + r) ** (-T)) / (2.0 * T) + (1.0 - (1.0 + r) ** (-(T - 1))) / (r * T)


# Annual depreciation rates for five-year property (computers and servers are qualified technological equipment,
# five-year property under 26 U.S.C. 168(e)(3)(B)(iv) and (i)(2)(A)): GDS 200 percent declining balance with the
# half-year convention (IRS Publication 946 Table A-1), and ADS straight line over five years with the half-year
# convention (168(g)(2) and (g)(3)(C), read at a copy of the statute on 29 Oct 2026).
MACRS_5Y_HY = (0.20, 0.32, 0.192, 0.1152, 0.1152, 0.0576)
ADS_5Y_SL_HY = (0.10, 0.20, 0.20, 0.20, 0.20, 0.10)
BONUS_ELECTIONS = {"none": 1.0, "elect_out": 0.0, "transitional_40": 0.4, "transitional_60": 0.6}


def psi_schedule(r, rates) -> float:
    """Present value per dollar of a schedule of annual tax deductions, the first year's deduction at the start (the
    convention of psi_amortization): sum_k rate_k (1 + r)^-(k - 1). r is an annual rate.

    Implements: prop:acct-tax | Spec: 24.4 | Notes: accounting 4.3 | Status: theory"""
    r = float(r)
    return float(sum(x * (1.0 + r) ** (-k) for k, x in enumerate(rates)))


def psi_equipment(r, election: str = "none", foreign_share: float = 0.0) -> dict:
    """Tax deductibility psi of owned servers (prop:acct-tax(d); theory_ext.tex Assumption (i)): domestic servers
    acquired after 19 Jan 2025 get the 100 percent first-year allowance (168(k) as amended by P.L. 119-21 sec. 70301),
    psi = 1; electing out (168(k)(7)) gives no bonus, psi = PV of MACRS five-year; the transitional election of
    168(k)(10) deducts 40 percent (60 percent for certain property) in the first year and the rest under MACRS;
    servers used predominantly outside the United States are ADS property (168(g)(1)(A)) with no bonus (26 CFR
    1.168(k)-2(b)(2)(ii)(B)), straight line over five years (168(g)(3)(C)). Mixed by the foreign share. The capital
    hurdles of cor:capital rise by Upsilon = (1 - psi tau)/(1 - tau) when psi < 1.

    Implements: prop:acct-tax(d), ass:ext-theta(i) | Spec: 24.4 | Notes: accounting 2, 4.3 | Status: theory"""
    if election not in BONUS_ELECTIONS:
        raise ValueError(f"bonus election must be one of {', '.join(BONUS_ELECTIONS)}")
    b = BONUS_ELECTIONS[election]
    macrs, ads = psi_schedule(r, MACRS_5Y_HY), psi_schedule(r, ADS_5Y_SL_HY)
    dom = b + (1.0 - b) * macrs
    fs = float(np.clip(foreign_share, 0.0, 1.0))
    return {"psi": (1.0 - fs) * dom + fs * ads, "psi_domestic": dom, "psi_foreign_ads": ads, "psi_macrs": macrs,
            "election": election, "foreign_share": fs}


def tax_psi(r, domestic_share=1.0, psi_domestic=1.0, T_foreign=15):
    """Effective deductibility of software development for tax: domestic share at psi_domestic (sec. 174A: 1) plus
    the foreign share at psi_15. Independent of book capitalization (prop:acct-tax(d)).

    Implements: prop:acct-tax(d) | Spec: 24.4 | Notes: accounting 2, 4.3 | Status: theory"""
    return domestic_share * psi_domestic + (1.0 - domestic_share) * psi_amortization(r, T_foreign)


def capitalized_share_asu(u, dc_share):
    """Capitalized share of build spending after ASU 2025-06 (ASC 350-40-25-12A): (1 - u)(F - F_dc)/F, with u the
    share incurred while significant development uncertainty exists and F_dc data conversion and training.

    Implements: prop:acct-path (ASU 2025-06 switch) | Spec: 24.4 | Notes: accounting 4.1 | Status: theory"""
    return (1.0 - u) * (1.0 - dc_share)


def program_premium(C_cap_share, g_F, L, T_B):
    """Permanent GAAP-over-cash premium of a growing capitalization program: w = (C_cap/S)[1 - e^{-g_F L} A(g_F T_B)],
    A(x) = (1 - e^{-x})/x.

    Implements: prop:acct-program, eq:acct-wedge | Spec: 24.4 | Notes: accounting 4.2 | Status: theory"""
    x = g_F * T_B
    A_ = (1.0 - math.exp(-x)) / x if abs(x) > 1e-12 else 1.0
    return C_cap_share * (1.0 - math.exp(-g_F * L) * A_)


def mw_probability(H, p_def, p_mw, T_rem, T_op, T_dc):
    """Probability of a material weakness at the assessment H years after go-live: p_def p_mw min{1, exp[-(H - T_rem
    - T_op)/T_dc]}.

    Implements: prop:acct-cutover, eq:acct-pmw | Spec: 24.4 | Notes: accounting 4.4 | Status: theory"""
    return p_def * p_mw * min(1.0, math.exp(-(H - T_rem - T_op) / T_dc))


def cutover_delay(T_op, T_cl):
    """Expected delay of an ICFR-scope cutover that must fall in the open window [T_cl, 1 - T_op] of the fiscal year,
    for a uniformly distributed ready date: (T_op + T_cl)^2 / 2.

    Implements: prop:acct-cutover | Spec: 24.4 | Notes: accounting 4.4 | Status: theory"""
    return (T_op + T_cl) ** 2 / 2.0


def amin_admissible(P, eps_bar, N_o) -> bool:
    """Admissibility of a control design for one in-scope control objective (def:acct-admissible; Part I prop:amin(b)):
    no reasonable possibility that a material misstatement is not prevented or detected on a timely basis, with a
    reasonable possibility read as an annual probability above eps_bar: 1 - (1 - P)^{N_o} <= eps_bar, equivalently
    P <= P_bar = 1 - (1 - eps_bar)^{1/N_o}. No standard sets eps_bar (AS 2201.A7 and FAS 5 define "remote" in words);
    it is the firm's operational reading.

    Implements: def:acct-admissible, prop:amin(b) | Spec: 22, 24.4 | Notes: accounting 4.5 | Status: theory"""
    return bool(1.0 - (1.0 - float(P)) ** float(N_o) <= float(eps_bar) + 1e-15)


def amin_direct_cost(S, audit_fee, sox_program_by_size, audit_fee_per_musd_low=None, audit_fee_high=None) -> dict:
    """Direct cost of accountability C^acct, common to every control design (Part I prop:amin; Part I round 2, C3 and
    the lead-agent rulings of 2 Nov 2026): the SOX program budget of the firm's revenue class in the KPMG 2025 SOX survey
    (internal and co-source resources, not the auditor's fee) plus the external audit fee. Central fee: the FY2022
    average of accelerated filers (Ideagen Audit Analytics, Audit Fee Trends 2003-2022); low bound: the S&P 500 ratio
    per $1 million of revenue; high case: the large-accelerated-filer average. sox_program_by_size is a list of
    [upper revenue bound or None, budget] in increasing order. Returns the three totals in dollars and as shares of S.

    Implements: prop:amin, prop:acct-amin (C^acct) | Spec: 24.4 | Notes: Paper 1 r2 C3 | Status: spec"""
    S = float(S)
    sox, label = None, None
    for ub, budget in sox_program_by_size:
        if ub is None or S < float(ub):
            sox, label = float(budget), ("revenue below $%.0f billion" % (float(ub) / 1e9) if ub is not None else "largest class")
            break
    if sox is None:
        sox, label = float(sox_program_by_size[-1][1]), "largest class"
    out = {"sox_program": sox, "sox_class": label, "audit_fee": float(audit_fee), "central": float(audit_fee) + sox}
    out["low"] = (float(audit_fee_per_musd_low) * S / 1e6 + sox) if audit_fee_per_musd_low is not None else out["central"]
    out["high"] = (float(audit_fee_high) + sox) if audit_fee_high is not None else out["central"]
    for k in ("central", "low", "high"):
        out[k + "_share"] = out[k] / S if S > 0 else math.inf
    return out


def amin_breakevens(types: dict, design: dict, eps_bar, N_o, p_cc=0.0) -> dict:
    """Break-evens of a chosen control design (Part I round 2, C2: the cheapest design is conditional, not a finding).
    p_cc: the largest cross-type common-mode probability per opportunity at which the design stays admissible,
    (P_bar - P_0)/(1 - P_0) with P_0 its miss probability at p_cc = 0 (negative or None: not admissible even at zero).
    human_miss: for a design with human and AI layers, the largest miss rate of the human layers on items the AI layers
    missed (automation bias, replacing the human miss rate p) at which it stays admissible at the given p_cc; None if
    the design lacks either kind, 0.0 if it fails even with perfect human review on those items.

    Implements: prop:acct-amin(a), prop:amin(a) | Spec: 24.4 | Notes: Paper 1 r2 C2 | Status: theory"""
    if not design:
        return {"p_cc": None, "human_miss": None}
    P_bar = 1.0 - (1.0 - float(eps_bar)) ** (1.0 / float(N_o))
    used = {nm: int(k) for nm, k in design.items() if int(k) > 0}
    is_ai = lambda nm: bool(types[nm].get("ai"))
    is_h = lambda nm: types[nm].get("kind", "") == "human" and not types[nm].get("ai")

    def P0(p_h=None):
        prod = 1.0
        for nm, k in used.items():
            t = types[nm]
            p = p_h if (p_h is not None and is_h(nm)) else t["p"]
            prod *= t["p_cm"] + (1 - t["p_cm"]) * p ** k
        return prod
    base = P0()
    be_cc = (P_bar - base) / (1.0 - base)
    out = {"p_cc": float(be_cc) if be_cc >= 0 else None, "P_bar": P_bar}
    if any(is_ai(n) for n in used) and any(is_h(n) for n in used):
        target = (P_bar - p_cc) / (1.0 - p_cc)
        if P0(0.0) > target:
            out["human_miss"] = 0.0
        elif P0(1.0) <= target:
            out["human_miss"] = 1.0
        else:
            lo, hi = 0.0, 1.0
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                lo, hi = (mid, hi) if P0(mid) <= target else (lo, mid)
            out["human_miss"] = lo
    else:
        out["human_miss"] = None
    return out


def amin_min_depth(p, p_cm, eps_bar, N_o, p_cc=0.0):
    """Smallest admissible depth of a design that uses one control type (prop:acct-amin(b), (c)): ceil(ln rho/ln p),
    rho = (P_bar - p_cc - (1 - p_cc) p_cm)/((1 - p_cc)(1 - p_cm)); None if no depth is admissible, i.e. if the type's
    common-mode floor p_cc + (1 - p_cc) p_cm is at or above P_bar (the common-mode floor of part (c)).

    Implements: prop:acct-amin(b), prop:acct-amin(c) | Spec: 22, 24.4 | Notes: accounting 4.5 | Status: theory"""
    Pb = 1.0 - (1.0 - float(eps_bar)) ** (1.0 / float(N_o))
    flo = p_cc + (1.0 - p_cc) * p_cm
    if Pb <= flo:
        return None
    rho = (Pb - flo) / ((1.0 - p_cc) * (1.0 - p_cm))
    return max(1, int(math.ceil(math.log(rho) / math.log(p) - 1e-12)))


def amin_design(S, C_acct, ai: bool, C_itgc, C_val, T_up, types: dict, N_o, eps_bar, p_cc=0.0, N_nm=0.0, L_nm=0.0,
                L_mm=None, n_max=6, itgc_lines=None, C_tml=0.0, separate=False) -> dict:
    """Accountability floor as an ICFR constraint (prop:acct-amin, def:acct-admissible; Part I prop:amin): the minimum
    cost over admissible designs. A design gives n_x layers of each control type x (at most 3 types); its miss
    probability per opportunity is P = p_cc + (1 - p_cc) prod_{x used} [p_cm,x + (1 - p_cm,x) p_x^{n_x}] (p_cc a cause
    shared by every layer: management override, defective shared data or IPE, failure of the ITGCs every layer relies
    on), and it is admissible iff 1 - (1 - P)^{N_o} <= eps_bar. Then
    a_min = [C_acct + sum_g C^itgc_g + C^tml + L^ai + sum_x n_x c_x + N_nm L_nm P]/S, minimized over admissible
    designs; a_min = inf if none is admissible. sum_g C^itgc_g are the ITGC lines of the plan's in-scope AI
    applications (eq:acct-itgc; they exist whatever the design) and C^tml their timeliness cost; L^ai =
    C_itgc + C_val/T_up is the line of the design's own AI layers, one if they share one application, one per layer if
    separate. N_nm L_nm P is the expected cost of errors below materiality (Part I prop:amin(c)); the consequence of a
    material misstatement is not traded against cost: N_o L_mm P is reported as the residual expected consequence,
    outside a_min (prop:acct-amin(d)). Also returned: the cheapest admissible human-only design, each type's minimal
    admissible depth and common-mode floor, and the cost-plus-consequence optimum with its admissibility
    (prop:acct-amin(f): admissible only by coincidence).

    Implements: prop:acct-amin, def:acct-admissible, eq:acct-amin, prop:acct-itgc(b), prop:amin | Spec: 22, 24.4, 25 | Notes: accounting 4.5, 4.6 | Status: theory"""
    import itertools
    names = list(types)[:3]
    if not ai:
        names = [n for n in names if not types[n].get("ai")]
    lines = float(np.sum(itgc_lines)) if itgc_lines is not None and len(np.atleast_1d(itgc_lines)) else 0.0
    layer_line = C_itgc + C_val / T_up
    P_bar = 1.0 - (1.0 - float(eps_bar)) ** (1.0 / float(N_o))
    annual = lambda P: 1.0 - (1.0 - P) ** float(N_o)

    def P_of(ns):
        if not any(ns):
            return 1.0
        prod = 1.0
        for nm, k in zip(names, ns):
            if k > 0:
                t = types[nm]
                prod *= t["p_cm"] + (1 - t["p_cm"]) * t["p"] ** k
        return p_cc + (1.0 - p_cc) * prod

    def cost_of(ns, P):
        c = 0.0
        n_ai = 0
        for nm, k in zip(names, ns):
            c += k * types[nm]["c"]
            if types[nm].get("ai"):
                n_ai += k
        own = (n_ai if separate else (1 if n_ai > 0 else 0)) * layer_line
        return C_acct + lines + C_tml + own + c + N_nm * L_nm * P

    grid = []
    for ns in itertools.product(range(n_max + 1), repeat=len(names)):
        if not any(ns):
            continue
        P = P_of(ns)
        grid.append((ns, P, cost_of(ns, P), amin_admissible(P, eps_bar, N_o)))
    adm = [g for g in grid if g[3]]
    best = min(adm, key=lambda g: (g[2], g[1])) if adm else None
    is_h = lambda ns: all(k == 0 or (types[nm].get("kind", "") == "human" and not types[nm].get("ai")) for nm, k in zip(names, ns))
    adm_h = [g for g in adm if is_h(g[0])]
    best_h = min(adm_h, key=lambda g: (g[2], g[1])) if adm_h else None
    used = [nm for nm, k in zip(names, best[0]) if k > 0] if best else []
    floor_P = p_cc + (1 - p_cc) * math.prod(types[n]["p_cm"] for n in used) if used else 1.0
    out = {"design": dict(zip(names, best[0])) if best else None, "a_min": best[2] / S if best else math.inf,
           "admissible": best is not None, "eps_bar": float(eps_bar), "N_o": float(N_o), "p_cc": float(p_cc), "P_bar": P_bar,
           "misstatement_probability": best[1] if best else None, "annual_miss_probability": annual(best[1]) if best else None,
           "a_min_human_only": best_h[2] / S if best_h else math.inf, "human_only_design": dict(zip(names, best_h[0])) if best_h else None,
           "human_only_admissible": best_h is not None,
           "common_mode_floor": annual(floor_P) if used else None,
           "type_floors": {n: annual(p_cc + (1 - p_cc) * types[n]["p_cm"]) for n in names},
           "min_depth": {n: amin_min_depth(types[n]["p"], types[n]["p_cm"], eps_bar, N_o, p_cc) for n in names},
           "itgc_lines_total": lines, "C_tml": float(C_tml), "separate_applications": bool(separate),
           "below_materiality_cost": N_nm * L_nm * best[1] if best else None}
    # the cheapest design is conditional on the layer parameters (Part I round 2, C2): break-evens in the cross-type
    # common mode p_cc and in the human miss rate on AI-missed items, for the chosen and the human-only design
    sel = {n: types[n] for n in names}
    out["breakeven"] = amin_breakevens(sel, out["design"], eps_bar, N_o, p_cc) if best else {"p_cc": None, "human_miss": None}
    out["human_only_breakeven"] = (amin_breakevens(sel, out["human_only_design"], eps_bar, N_o, p_cc) if best_h
                                   else {"p_cc": None, "human_miss": None})
    if L_mm is not None:
        out["residual_expected_consequence"] = float(N_o) * float(L_mm) * best[1] if best else None
        cpc = min(grid, key=lambda g: (g[2] + float(N_o) * float(L_mm) * g[1], g[1]))
        out["cost_plus_consequence"] = {"design": dict(zip(names, cpc[0])), "cost": cpc[2] + float(N_o) * float(L_mm) * cpc[1],
                                        "admissible": cpc[3], "annual_miss_probability": annual(cpc[1])}
    return out


def itgc_line(n_id, n_perm, c_acc, n_chg, c_chg, C_val, T_up, c_ops, n_ifc, c_ifc) -> dict:
    """ITGC cost line of one in-scope AI application, a year (ass:acct-itgc, eq:acct-itgc):
    C^itgc_g = c_acc (n_id + n_perm) + c_chg n_chg + C_val/T_up + c_ops + c_ifc n_ifc. C_val is the ICFR retest at each
    forced model upgrade, on top of the functional revalidation already in the run costs.

    Implements: ass:acct-itgc, eq:acct-itgc | Spec: 25 | Notes: accounting 4.6 | Status: theory"""
    return {"access": c_acc * (n_id + n_perm), "change": c_chg * n_chg, "upgrade": C_val / T_up, "ops": float(c_ops),
            "interface": c_ifc * n_ifc}


def pv_upgrade_retests(C_val, r, T_par, T_up, T_h):
    """Present value of the ICFR retests at forced upgrades with the clock starting at cutover (eq:acct-pvup):
    PV = C_val e^{-r(T_par + T_up)} (1 - e^{-r n_up T_up})/(1 - e^{-r T_up}), n_up = floor((T_h - T_par)/T_up).
    With stationary upgrade dates the expected PV equals that of the flow C_val/T_up. Returns (PV, n_up).

    Implements: eq:acct-pvup, prop:acct-itgc(c) | Spec: 25 | Notes: accounting 4.6 | Status: theory"""
    K = int(math.floor((T_h - T_par) / T_up + 1e-12))
    if K <= 0:
        return 0.0, 0
    return C_val * math.exp(-r * (T_par + T_up)) * (1 - math.exp(-r * K * T_up)) / (1 - math.exp(-r * T_up)), K


def tml_wait(n_cl, nu_out, T_cw, D_bar, T_sl, c_del, L_late):
    """Expected close-window outage cost when the close waits outages out (prop:acct-itgc(d)):
    nu_cw [c_del D_bar + L_late e^{-T_sl/D_bar}], nu_cw = n_cl nu_out T_cw (durations exponential, mean D_bar days).

    Implements: prop:acct-itgc(d) | Spec: 25 | Notes: accounting 4.6 | Status: theory"""
    return n_cl * nu_out * T_cw * (c_del * D_bar + L_late * math.exp(-T_sl / D_bar))


def tml_fallback(n_cl, nu_out, T_cw, D_bar, c_del, C_fb, c_fb, t_sw):
    """Expected cost with a manual fallback (prop:acct-itgc(d)): C_fb + nu_cw D_bar [c_del (1 - e^{-t_sw/D_bar}) +
    c_fb e^{-t_sw/D_bar}] (requires t_sw <= T_sl).

    Implements: prop:acct-itgc(d) | Spec: 25 | Notes: accounting 4.6 | Status: theory"""
    return C_fb + n_cl * nu_out * T_cw * D_bar * (c_del * (1 - math.exp(-t_sw / D_bar)) + c_fb * math.exp(-t_sw / D_bar))


def fallback_threshold(n_cl, T_cw, D_bar, T_sl, c_del, L_late, C_fb, c_fb, t_sw):
    """The fallback pays iff Delta_fb = D_bar e^{-t_sw/D_bar}(c_del - c_fb) + L_late e^{-T_sl/D_bar} > 0 and
    nu_out > nu* = C_fb/(n_cl T_cw Delta_fb) (prop:acct-itgc(d)). Returns (nu*, Delta_fb).

    Implements: prop:acct-itgc(d) | Spec: 25 | Notes: accounting 4.6 | Status: theory"""
    Dl = D_bar * math.exp(-t_sw / D_bar) * (c_del - c_fb) + L_late * math.exp(-T_sl / D_bar)
    return ((C_fb / (n_cl * T_cw * Dl)) if Dl > 0 else math.inf), Dl


def timeliness_cost(n_cl, nu_out, T_cw, D_bar, T_sl, c_del, L_late, C_fb, c_fb, t_sw) -> dict:
    """Timeliness cost C^tml of an in-scope AI application: the cheaper of waiting outages out and keeping a manual
    fallback, with the threshold nu* (prop:acct-itgc(d)). c_del and c_fb are increments over the ordinary outage loss
    already in the error floor's common-mode term (no double count).

    Implements: prop:acct-itgc(d) | Spec: 25 | Notes: accounting 4.6 | Status: theory"""
    w = tml_wait(n_cl, nu_out, T_cw, D_bar, T_sl, c_del, L_late)
    f = tml_fallback(n_cl, nu_out, T_cw, D_bar, c_del, C_fb, c_fb, t_sw) if t_sw <= T_sl else math.inf
    ns, Dl = fallback_threshold(n_cl, T_cw, D_bar, T_sl, c_del, L_late, C_fb, c_fb, t_sw)
    use_fb = bool(Dl > 0 and nu_out > ns and f < w)
    return {"C_tml": min(w, f), "wait": w, "fallback": f, "nu_star": ns, "fallback_pays": use_fb}


def survivor_attrition_cost(remaining_fte, wage, attrition, replacement_months):
    """Extra voluntary leavers among remaining staff after a reduction, times the cost of replacing each:
    remaining x attrition x wage x replacement_months / 12. Superseded in the engine by survivor_cost
    (prop:labor-survivor); code/examples/invoice_chain.py still calls it.

    Implements: - | Spec: 24.6 | Notes: labor 3.3 | Status: superseded"""
    return _a(remaining_fte) * _a(attrition) * _a(wage) * _a(replacement_months) / 12.0



# =================================================================================================
# 22. Labor law, talent and jurisdiction (theory_labor.tex, sec:labor; spec 24.5, 24.6)
#     Statutory calculators are model constraints as read at the primary sources on 29 Oct 2026
#     (notes/ref_verification_labor.md); they are not legal advice.
# =================================================================================================
DAYS_PER_YEAR = 365.0
WEEKS_PER_MONTH = 52.0 / 12.0


def warn_federal(employer_ft, site_active_ft, losses_30d, plant_closing=False):
    """U.S. WARN (29 U.S.C. 2101-2102; 20 C.F.R. 639.3): an employer of 100+ (excluding part-time); a plant closing
    is 50+ losses at a single site in 30 days; a mass layoff is 500+, or 50+ that are at least 33% of the site's
    active full-time employees. Returns (triggered, notice_days): 60 days when triggered.

    Implements: tab:labor-rules (US) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    if employer_ft < 100:
        return False, 0
    trig = losses_30d >= 50 if plant_closing else (losses_30d >= 500 or (losses_30d >= 50 and losses_30d >= 0.33 * site_active_ft))
    return bool(trig), (60 if trig else 0)


def warn_ca(establishment_12m, layoffs_30d):
    """Cal-WARN (Lab. Code 1400.5, 1401): an establishment of 75+ in the preceding 12 months; 50+ layoffs in 30 days
    with no percentage test; 60 days' notice. The official Cal-WARN page was not read (unverified).

    Implements: tab:labor-rules (CA) | Spec: 24.5 | Notes: labor 3.1, 7.6 | Status: theory"""
    trig = establishment_12m >= 75 and layoffs_30d >= 50
    return bool(trig), (60 if trig else 0)


def warn_ny(employer_ft_ny, site_ft, layoffs):
    """New York WARN (DOL fact sheet P483): employers of 50+ full-time in NY; a mass layoff is 25+ that are 33% of
    the site, or 250+; 90 days' notice.

    Implements: tab:labor-rules (NY) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    if employer_ft_ny < 50:
        return False, 0
    trig = layoffs >= 250 or (layoffs >= 25 and layoffs >= 0.33 * site_ft)
    return bool(trig), (90 if trig else 0)


def warn_nj(employer, terminated, years, notice_days):
    """New Jersey (NJES-997, rev. 2/26): employers of 100+ with 50+ terminated at or reporting to an NJ
    establishment; mandatory severance of 1 week per full year of service plus 4 weeks if notice is under 90 days.
    Returns (triggered, severance_weeks).

    Implements: tab:labor-rules (NJ) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    trig = employer >= 100 and terminated >= 50
    if not trig:
        return False, 0
    return True, math.floor(years) + (4 if notice_days < 90 else 0)


def eu_collective(size, d30, d90, option="30day"):
    """Directive 98/59/EC Art. 1(1)(a): over 30 days, 10+ (establishments of 21 to 99), 10%+ (100 to 299), 30+
    (300+); or the Member State option of 20+ over 90 days at any size.

    Implements: tab:labor-rules (EU) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    if option == "90day":
        return bool(d90 >= 20)
    if 20 < size < 100:
        return bool(d30 >= 10)
    if 100 <= size < 300:
        return bool(d30 >= 0.10 * size)
    if size >= 300:
        return bool(d30 >= 30)
    return False


def de_anzeige(size, d30):
    """KSchG s.17(1) notification thresholds within 30 days: more than 5 (21 to 59 employees); 10% or more than 25
    (60 to 499); 30 or more (500+).

    Implements: tab:labor-rules (DE) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    if 20 < size < 60:
        return bool(d30 > 5)
    if 60 <= size < 500:
        return bool(d30 >= 0.10 * size or d30 > 25)
    if size >= 500:
        return bool(d30 >= 30)
    return False


def de_sozialplan_enforceable(size, d):
    """BetrVG s.112a(1): a social plan for a pure staff reduction is enforceable by the conciliation board only
    above: under 60 employees 20% and at least 6; 60 to 249 20% or 37; 250 to 499 15% or 60; 500+ 10% and at least 60.

    Implements: tab:labor-rules (DE) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    if size < 60:
        return bool(d >= 0.20 * size and d >= 6)
    if size < 250:
        return bool(d >= 0.20 * size or d >= 37)
    if size < 500:
        return bool(d >= 0.15 * size or d >= 60)
    return bool(d >= 0.10 * size and d >= 60)


def de_notice_months(years):
    """BGB s.622(2) employer notice by tenure: 1 month at 2 years, 2 at 5, 3 at 8, 4 at 10, 5 at 12, 6 at 15, 7 at
    20; below 2 years the basic four weeks (about 0.92 months).

    Implements: tab:labor-rules (DE) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    for t, m in [(20, 7), (15, 6), (12, 5), (10, 4), (8, 3), (5, 2), (2, 1)]:
        if years >= t:
            return float(m)
    return 4.0 / WEEKS_PER_MONTH


def de_1a_months(years):
    """KSchG s.1a: 0.5 monthly earnings per year of employment, if the employer offers it in the notice.

    Implements: tab:labor-rules (DE) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    return 0.5 * float(years)


def fr_pse_required(firm_size, d30):
    """Code du travail L1233-61: a job-protection plan (PSE) at firms of 50+ with 10+ dismissals in 30 days.

    Implements: tab:labor-rules (FR) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    return bool(firm_size >= 50 and d30 >= 10)


def fr_cse_months(d):
    """L1233-30: CSE opinion period of 2 months (under 100 dismissals), 3 (100 to 249), 4 (250+).

    Implements: tab:labor-rules (FR) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    return 2.0 if d < 100 else (3.0 if d < 250 else 4.0)


def fr_admin_days(agreement):
    """L1233-57-4: validation of an agreement in 15 days; homologation of a unilateral document in 21 days.

    Implements: tab:labor-rules (FR) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    return 15 if agreement else 21


def fr_notice_months(years):
    """L1234-1: 1 month at 6 months to 2 years of tenure; 2 months at 2+ years.

    Implements: tab:labor-rules (FR) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    return 2.0 if years >= 2 else (1.0 if years >= 0.5 else 0.0)


def fr_indemnity_months(years):
    """R1234-2: statutory dismissal indemnity of 1/4 month a year up to 10 years and 1/3 beyond.

    Implements: tab:labor-rules (FR) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    return 0.25 * min(years, 10) + max(years - 10, 0) / 3.0


def uk_collective(d90_one_establishment):
    """TULRCA s.188: 20+ redundancies at one establishment within 90 days trigger consultation of at least 30 days
    (20 to 99) or 45 days (100+) before the first dismissal. Returns (triggered, days).

    Implements: tab:labor-rules (UK) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    if d90_one_establishment < 20:
        return False, 0
    return True, (45 if d90_one_establishment >= 100 else 30)


def uk_srp_weeks(age, years):
    """ERA 1996 s.162 statutory redundancy pay: counting back from the relevant date, 1.5 weeks for each year aged
    41+, 1 week aged 22 to 40 and 0.5 week otherwise, at most 20 years counted (the week is capped at GBP 751 from
    6 April 2026).

    Implements: tab:labor-rules (UK) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    w = 0.0
    for k in range(min(int(years), 20)):
        a = age - 1 - k
        w += 1.5 if a >= 41 else (1.0 if a >= 22 else 0.5)
    return w


def in_retrenchment(years):
    """India, Industrial Relations Code 2020 (in force 21 Nov 2025) s.70 and s.83: 1 month's notice or pay in lieu;
    compensation of 15 days' average pay per completed year (a part year over six months counts); 15 days' wages to
    the re-skilling fund. Returns (notice_months, compensation_months, fund_months) with 15 days = 0.5 month. The
    15/26 convention, the Chapter X notice length and state laws are unverified.

    Implements: tab:labor-rules (IN) | Spec: 24.5 | Notes: labor 3.1 | Status: theory"""
    full = math.floor(years) + (1 if years - math.floor(years) > 0.5 else 0)
    return 1.0, 0.5 * full, 0.5


def statutory_terms(country, subnational="", site_headcount=0.0, employer_headcount=0.0, n_dis=0.0, tenure=3.9,
                    age=40.0, works_council=False, T_proc_DE=0.25, T_tech_DE=0.25, T_tech_FR=1.0 / 6.0,
                    fr_agreement=False, eu_option="30day", india_chapter_x=False):
    """Per-site statutory terms (tab:labor-rules; labor notes 3.1): whether a collective procedure is triggered,
    the legal lead T^leg = T^proc + T^not (years from procedure start to the earliest effective dismissal), the
    technology consultation T^tech (years), the statutory cash floor and the individual notice (months of pay per
    displaced FTE), the contemplation rule (EU and UK: the procedure starts when redundancies are contemplated,
    t^cont = 0) and the rules used here that were not verified at a primary source.

    Implements: ass:labor-proc, tab:labor-rules | Spec: 24.5 | Notes: labor 3.1, 3.2 | Status: theory"""
    c = str(country or "").upper()
    sub = str(subnational or "").upper()
    out = {"triggered": False, "T_leg": 0.0, "T_tech": 0.0, "floor_months": 0.0, "notice_months": 0.0,
           "contemplation_zero": False, "rule": "", "unverified": []}
    if c == "US":
        trig, days = warn_federal(employer_headcount, site_headcount, n_dis)
        rule = "WARN Act (federal)"
        if sub == "CA":
            t2, d2 = warn_ca(site_headcount, n_dis)
            trig, days, rule = trig or t2, max(days, d2), "WARN Act and Cal-WARN"
            out["unverified"].append("Cal-WARN read at reproductions, not the official page")
        elif sub == "NY":
            t2, d2 = warn_ny(employer_headcount, site_headcount, n_dis)
            trig, days, rule = trig or t2, max(days, d2), "WARN Act and NY WARN"
        elif sub == "NJ":
            t2, wks = warn_nj(employer_headcount, n_dis, tenure, 90)
            if t2:
                trig, days, rule = True, max(days, 90), "WARN Act and NJ WARN (90 days, mandatory severance)"
                out["floor_months"] = wks / WEEKS_PER_MONTH
        out.update(triggered=bool(trig), T_leg=days / DAYS_PER_YEAR, rule=rule)
        return out
    if c == "UK" or c == "GB":
        trig, days = uk_collective(n_dis)
        out.update(triggered=trig, T_leg=days / DAYS_PER_YEAR, floor_months=uk_srp_weeks(age, tenure) / WEEKS_PER_MONTH,
                   contemplation_zero=True, rule="TULRCA s.188 consultation; ERA s.162 redundancy pay")
        out["unverified"].append("individual notice (ERA s.86) assumed to run concurrently with consultation")
        return out
    if c == "DE":
        trig = de_anzeige(site_headcount, n_dis) or eu_collective(site_headcount, n_dis, n_dis, eu_option)
        notice = de_notice_months(tenure)
        lead_proc = T_proc_DE if (trig or works_council) else 0.0
        T_leg = lead_proc + max(1.0 if trig else 0.0, notice) / 12.0
        out.update(triggered=trig, T_leg=T_leg, T_tech=T_tech_DE if works_council else 0.0,
                   floor_months=de_1a_months(tenure), notice_months=notice, contemplation_zero=True,
                   rule="KSchG s.17-18 notification and waiting period; BetrVG s.111-112 consultation; BGB s.622 notice")
        if works_council:
            out["unverified"].append("works-council consultation length (T_proc_DE, T_tech_DE) has no statutory length (scenario)")
        out["sozialplan_enforceable"] = de_sozialplan_enforceable(site_headcount, n_dis)
        return out
    if c == "FR":
        pse = fr_pse_required(employer_headcount or site_headcount, n_dis)
        notice = fr_notice_months(tenure)
        T_leg = (fr_cse_months(n_dis) / 12.0 + fr_admin_days(fr_agreement) / DAYS_PER_YEAR if pse else 0.0) + notice / 12.0
        out.update(triggered=pse, T_leg=T_leg, T_tech=T_tech_FR if (employer_headcount or site_headcount) >= 50 else 0.0,
                   floor_months=fr_indemnity_months(tenure), notice_months=notice, contemplation_zero=True,
                   rule="L1233-30 CSE opinion; L1233-57-4 administration; L1234-1 notice; R1234-2 indemnity")
        return out
    if c == "IN":
        n, comp, fund = in_retrenchment(tenure)
        out.update(triggered=bool(india_chapter_x and site_headcount >= 300), T_leg=n / 12.0, floor_months=comp + fund,
                   notice_months=n, rule="Industrial Relations Code 2020 s.70, s.83")
        out["unverified"] += ["India 15/26 convention for monthly-rated pay", "s.79 notice length and state Shops and Establishments Acts"]
        if india_chapter_x:
            out["unverified"].append("Chapter X prior-permission timing")
        return out
    if c in EU_EEA:
        trig = eu_collective(site_headcount, n_dis, n_dis, eu_option)
        out.update(triggered=trig, T_leg=(30.0 / DAYS_PER_YEAR) if trig else 0.0, contemplation_zero=True,
                   rule="Directive 98/59/EC minimum (national law sets more)")
        out["unverified"].append(f"{c}: only the EU minimum is modeled; national rules not read")
        return out
    out["unverified"].append(f"{c or 'unknown'}: no statutory rule modeled; notice and severance from the plan only")
    out["rule"] = "none modeled"
    return out


EU_EEA = {"AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT",
          "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE", "IS", "LI", "NO"}


def cutover_date(T_st, T_par, t_A, T_leg):
    """Earliest effective cutover: t^gate = T^st + T_par and t^dis = max{t^gate, t^A + T^leg}.

    Implements: prop:labor-lead(a) | Spec: 24.5 | Notes: labor 3.2 | Status: theory"""
    return np.maximum(_a(T_st) + _a(T_par), _a(t_A) + _a(T_leg))


def run_start_delay(T_tech, T_bld):
    """Delay of the parallel run's start by a technology consultation that outlasts the build: T^st = (T^tech - T^bld)_+.

    Implements: prop:labor-lead | Spec: 24.5 | Notes: labor 3.2 | Status: theory"""
    return np.maximum(_a(T_tech) - _a(T_bld), 0.0)


def announcement_cutoff(gate, T_leg, W, c_ann, C_wd):
    """Success probability above which the procedure starts early, at (t^gate - T^leg)_+:
    varpi^A = (c^ann T^ov + C^wd)/(W T^ov + c^ann T^ov + C^wd), T^ov = min{T^leg, t^gate}.

    Implements: prop:labor-lead(d), eq:labor-ann | Spec: 24.5 | Notes: labor 3.2 | Status: theory"""
    m = np.minimum(_a(T_leg), _a(gate))
    num = _a(c_ann) * m + _a(C_wd)
    return num / np.maximum(_a(W) * m + num, 1e-12)


def procedure_start(gate, T_leg, varpi, W, c_ann, C_wd, t_cont=None):
    """Optimal procedure start t^A: (t^gate - T^leg)_+ if varpi >= varpi^A, else the gate; with a legal bound
    t^A <= t^cont the start is the best of min{rule, t^cont}, 0 and t^cont (piecewise-linear cost).

    Implements: prop:labor-lead(d) | Spec: 24.5 | Notes: labor 3.2 | Status: theory"""
    G, Tl = float(gate), float(T_leg)
    early = varpi >= float(announcement_cutoff(G, Tl, W, c_ann, C_wd))
    rule = max(0.0, G - Tl) if early else G
    if t_cont is None:
        return rule
    cands = [min(rule, t_cont), 0.0, float(t_cont)]
    return min(cands, key=lambda x: announcement_cost(x, G, Tl, varpi, W, c_ann, C_wd))


def announcement_cost(t_A, gate, T_leg, varpi, W, c_ann, C_wd):
    """Expected cost of starting the procedure at t^A (verify ann_cost): announced-state cost flow, forgone savings
    after the gate on success, and the withdrawal cost on failure.

    Implements: prop:labor-lead(d) | Spec: 24.5 | Notes: labor 3.2 | Status: theory"""
    if t_A >= gate:
        return varpi * (c_ann + W) * T_leg
    tD = max(gate, t_A + T_leg)
    return varpi * (c_ann * (tD - t_A) + W * (tD - gate)) + (1 - varpi) * (c_ann * (gate - t_A) + C_wd)


def free_parallel_run(T_hold, C_par, varpi, bbar, W, C_str, L_roll, T_det, c_hat_hold, ramp_mean=0.5):
    """Optimal parallel run when dismissals are legally barred for T^hold after the run starts:
    T_opt = min{T**, max{T^hold, T*}}, with T* = T_det ln(R/(T_det c_hat)) (eq:tasks-tpar) and T** the same with
    c_hat' = nu_rec E_p + C^dup (the cost of a run year before the hold ends).

    Implements: prop:labor-lead(e), eq:labor-freerun | Spec: 24.5 | Notes: labor 3.2 | Status: theory"""
    Ts = optimal_parallel_run(C_par, varpi, bbar, W, C_str, L_roll, T_det, ramp_mean)
    R = (1 - _a(varpi)) * (_a(C_str) + _a(L_roll))
    Td = _a(T_det)
    ch1 = _a(c_hat_hold)
    with np.errstate(divide="ignore", invalid="ignore"):
        Tss = np.where(ch1 > 0, np.where(R > Td * ch1, Td * np.log(np.maximum(R, 1e-300) / np.maximum(Td * ch1, 1e-300)), 0.0), np.inf)
    return np.minimum(Tss, np.maximum(_a(T_hold), Ts))


def stream_partition(t_dis, W, O_w):
    """Cutover streams (prop:labor-lead(b)): sort jurisdictions by t^dis and choose the interval partition that
    minimizes sum_groups sum_c W_c (max_group t^dis - t^dis_c) + (#groups - 1) O_w, by dynamic programming over the
    sorted list. Returns (groups as lists of input indices, cost).

    Implements: prop:labor-lead(b) | Spec: 24.5 | Notes: labor 3.2 | Status: theory"""
    tD, Wv = _a(t_dis), _a(W)
    n = len(tD)
    if n == 0:
        return [], 0.0
    order = list(np.argsort(tD, kind="stable"))
    best = [0.0] + [math.inf] * n
    prev = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(j):
            grp = order[i:j]
            Tm = max(tD[k] for k in grp)
            c = best[i] + sum(Wv[k] * (Tm - tD[k]) for k in grp) + (O_w if i > 0 else 0.0)
            if c < best[j] - 1e-15:
                best[j], prev[j] = c, i
    groups, j = [], n
    while j > 0:
        i = prev[j]
        groups.append([int(k) for k in order[i:j]])
        j = i
    return groups[::-1], float(best[n])


def min_pacing_span(n_dis, n_thr, T_win):
    """Sub-threshold pacing: keeping at most N^thr - 1 dismissals in every window of length T^win needs a span of at
    least (ceil(N^dis/(N^thr - 1)) - 1) T^win (UK: 200 below 20 per 90 days takes 900 days).

    Implements: prop:labor-lead(c) | Spec: 24.5 | Notes: labor 3.2 | Status: theory"""
    if n_thr <= 1:
        return math.inf
    return (math.ceil(n_dis / (n_thr - 1)) - 1) * T_win


def survivor_base(fte_inhouse_changed, fte_displaced):
    """The survivor headcount of ass:labor-survivor: N^hc = the firm's own (in-house) FTE on the changed steps,
    outsourced work excluded; N^sv = max(N^hc - displaced FTE, 0); displacement share x = displaced/N^hc. The one
    definition used by plans.py, the people plan and the paper example. Returns (N_hc, N_sv, x_share).

    Implements: ass:labor-survivor | Spec: 24.6 | Notes: labor 3.3 | Status: theory"""
    N_hc = _a(fte_inhouse_changed)
    D = _a(fte_displaced)
    N_sv = np.maximum(N_hc - D, 0.0)
    x = np.where(N_hc > 0, np.minimum(D / np.maximum(N_hc, 1e-12), 1.0), 0.0)
    return N_hc, N_sv, x


def survivor_quits(N_sv, nu_q, nu_s, T_s):
    """Extra quits among survivors: N^q = N^sv e^{-nu^q T_s}(1 - e^{-nu^s T_s}) <= N^sv nu^s T_s.

    Implements: prop:labor-survivor(a), ass:labor-survivor | Spec: 24.6 | Notes: labor 3.3 | Status: theory"""
    return _a(N_sv) * np.exp(-_a(nu_q) * _a(T_s)) * (1 - np.exp(-_a(nu_s) * _a(T_s)))


def survivor_cost(N_sv, wage, nu_q, nu_s, T_s, c_rep, delta_eff):
    """Survivor cost added to C^str: C^surv = w (c^rep N^q + N^sv delta^eff T_s).

    Implements: prop:labor-survivor(a) | Spec: 24.6 | Notes: labor 3.3 | Status: theory"""
    return _a(wage) * (_a(c_rep) * survivor_quits(N_sv, nu_q, nu_s, T_s) + _a(N_sv) * _a(delta_eff) * _a(T_s))


def survivor_wave_charge(N_sv, wage, T_s, c_rep, eta0, delta0):
    """Per-wave survivor charge added to the wave overhead O_w: O_s = w N^sv T_s (c^rep eta_0 + delta_0), for
    nu^s(x) = eta_0 1{x>0} + eta_1 x and delta^eff(x) = delta_0 1{x>0} + delta_1 x.

    Implements: prop:labor-survivor(b) | Spec: 24.6 | Notes: labor 3.3 | Status: theory"""
    return _a(wage) * _a(N_sv) * _a(T_s) * (_a(c_rep) * _a(eta0) + _a(delta0))


def knowledge_holder_factor(n_K, kappa_doc, kappa_ret, nu_x, tau_ann):
    """Success factor for n_K critical knowledge holders over the announced period tau^ann:
    [kappa_doc + (1 - kappa_doc) e^{-(1 - kappa_ret) nu^x tau^ann}]^{n_K} (eq:labor-success).

    Implements: prop:labor-survivor(c), eq:labor-success | Spec: 24.6 | Notes: labor 3.3 | Status: theory"""
    return (_a(kappa_doc) + (1 - _a(kappa_doc)) * np.exp(-(1 - _a(kappa_ret)) * _a(nu_x) * _a(tau_ann))) ** _a(n_K)


def retention_award_pays(varpi0, n_K, kappa_doc, kappa_ret, nu_x, nu_q, tau_ann, Y_s, Y_f, C_ret):
    """Retention awards pay iff [varpi_p(kappa_ret) - varpi_p(0)](Y_s - Y_f) > n_K C^ret q_stay, with
    q_stay = exp(-(nu^q + (1 - kappa_ret) nu^x) tau^ann). Returns (pays, gain, expected_payments).

    Implements: prop:labor-survivor(d) | Spec: 24.6 | Notes: labor 3.3 | Status: theory"""
    gain = varpi0 * (float(knowledge_holder_factor(n_K, kappa_doc, kappa_ret, nu_x, tau_ann))
                     - float(knowledge_holder_factor(n_K, kappa_doc, 0.0, nu_x, tau_ann))) * (Y_s - Y_f)
    q_stay = math.exp(-(nu_q + (1 - kappa_ret) * nu_x) * tau_ann)
    pay = n_K * C_ret * q_stay
    return bool(gain > pay), float(gain), float(pay)


def redeployment_cap(varpi_rd, nu_q, N_oth, T_w, N_dis):
    """Bound on the redeployed share: u_d <= min{1, varpi^rd nu^q N^oth T^w / N^dis} (vacancies from quits among
    other staff during the window T^w = t^dis - t^A, each filled by a displaced worker with probability varpi^rd).

    Implements: prop:labor-survivor(e) | Spec: 24.6 | Notes: labor 3.3 | Status: theory"""
    return np.minimum(1.0, _a(varpi_rd) * _a(nu_q) * _a(N_oth) * _a(T_w) / np.maximum(_a(N_dis), 1e-12))


def ai_engineer_wage(w_SE, premium, tau_L_annual, wage_index=1.0):
    """Loaded AI engineer wage: w^AI = (1 + p) w^SE (1 + tau_L,annual) x wage_index(site); $194,649 at
    w^SE = $135,980, p = 0.11, tau_L = 0.2896.

    Implements: prop:labor-talent(a) | Spec: 24.6 | Notes: labor 3.4 | Status: theory"""
    return (1 + _a(premium)) * _a(w_SE) * (1 + _a(tau_L_annual)) * _a(wage_index)


def build_cost_premium(F0, l_AI, premium):
    """Build cost with the AI wage premium on its labor share: F = F_0 (1 + l_AI p).

    Implements: prop:labor-talent(a) | Spec: 24.6 | Notes: labor 3.4 | Status: theory"""
    return _a(F0) * (1 + _a(l_AI) * _a(premium))


def processes_in_scope(t, Gamma, e_bld, e_mnt):
    """Processes in run mode with constant engineering capacity Gamma: e_bld dN/dt = Gamma - e_mnt N, so
    N(t) = (Gamma/e_mnt)(1 - e^{-e_mnt t/e_bld}); the ceiling is Gamma/e_mnt.

    Implements: prop:labor-talent(b) | Spec: 24.6 | Notes: labor 3.4 | Status: theory"""
    return _a(Gamma) / _a(e_mnt) * (1 - np.exp(-_a(e_mnt) * _a(t) / _a(e_bld)))


def time_to_scope(N, Gamma, e_bld, e_mnt):
    """Time to bring N processes into run mode: T_Gamma(N) = (e_bld/e_mnt) ln(N-bar/(N-bar - N)), infinite when
    N >= N-bar = Gamma/e_mnt (eq:labor-TGamma).

    Implements: prop:labor-talent(b), eq:labor-TGamma | Spec: 24.6 | Notes: labor 3.4 | Status: theory"""
    Nbar = float(Gamma) / float(e_mnt) if e_mnt > 0 else math.inf
    if N <= 0:
        return 0.0
    if N >= Nbar:
        return math.inf
    return float(e_bld) / float(e_mnt) * math.log(Nbar / (Nbar - N))


def hiring_capacity(T, hire_rate, T_lead, delta_rp=0.0, T_rp=0.0, Gamma0=0.0):
    """Cumulative engineering person-years by T with hiring at rate dot-Gamma^hire after a lead T^lead and a ramp
    shortfall delta^rp over the first T^rp years: Gamma_0 T + h[U^2/2 - delta^rp(min(U, T^rp)^2/2 + T^rp (U - T^rp)_+)],
    U = (T - T^lead)_+.

    Implements: prop:labor-talent(c) (L3e) | Spec: 24.6 | Notes: labor 3.4 | Status: theory"""
    U = max(float(T) - float(T_lead), 0.0)
    ramp = delta_rp * (min(U, T_rp) ** 2 / 2 + T_rp * max(U - T_rp, 0.0)) if T_rp > 0 else 0.0
    return Gamma0 * float(T) + hire_rate * (U ** 2 / 2) - hire_rate * ramp


def contract_threshold(delta_rp, T_rp, c_hire, W_hat, T_lead, T_ct, dGamma, w_AI, u_ct):
    """Hire or contract for a gap dGamma lasting T^need >= T^rp: contract iff
    T^need < [delta^rp T^rp + c^hire + W-hat (T^lead - T^ct)/(dGamma w^AI)]/u_ct (c^hire in years of wages).

    Implements: prop:labor-talent(d) | Spec: 24.6 | Notes: labor 3.4 | Status: theory"""
    return (delta_rp * T_rp + c_hire + W_hat * (T_lead - T_ct) / max(dGamma * w_AI, 1e-12)) / max(u_ct, 1e-12)


def location_adoption_lag(cbar, c_fx, w_index, delta_pi):
    """Adoption lag of a site with wage index w relative to the U.S.: ln[(c-bar - c^fx)/(w c-bar - c^fx)]/delta_pi
    >= ln(1/w)/delta_pi; automation never pays at the site if w c-bar <= c^fx. Returns years (inf if never).

    Implements: lem:labor-location | Spec: 24.6 | Notes: labor 3.5 | Status: theory"""
    cb, cf, w = _a(cbar), _a(c_fx), _a(w_index)
    with np.errstate(divide="ignore", invalid="ignore"):
        lag = np.log((cb - cf) / (w * cb - cf)) / float(delta_pi)
    return np.where((w * cb > cf) & (cb > cf), np.maximum(lag, 0.0), np.inf)


def residency_readiness(iota, omega_res):
    """Readiness cap under data residency: iota-bar = (1 - omega^res) iota.

    Implements: prop:labor-residency(a) | Spec: 24.6 | Notes: labor 3.6 | Status: theory"""
    return (1 - np.clip(_a(omega_res), 0, 1)) * _a(iota)


def residency_threshold(iota_star, iota):
    """Largest restricted input share a process tolerates: omega-bar^res_p = 1 - iota*_p/iota_p.

    Implements: prop:labor-residency(b) | Spec: 24.6 | Notes: labor 3.6 | Status: theory"""
    return 1 - _a(iota_star) / np.maximum(_a(iota), 1e-12)


def region_cost(p_reg, pi_n, cQ, F_tr, nu_inv, C_sw, v):
    """Per-unit cost of serving an activity from region g: c_A(g) = (1 + p^reg) pi n + c-hat^Q(iota-bar(g)) +
    (F^tr + nu^inv C^sw)/v; the engine takes the minimum over regions.

    Implements: prop:labor-residency(c), eq:labor-region | Spec: 24.6 | Notes: labor 3.6 | Status: theory"""
    return (1 + _a(p_reg)) * _a(pi_n) + _a(cQ) + (_a(F_tr) + _a(nu_inv) * _a(C_sw)) / np.maximum(_a(v), 1e-12)


def regional_instances_pay(W_own, W_min, R, F_build, annuity):
    """R regional instances beat one global instance at the weakest readiness iff
    sum_c [W_c(iota_c) - W_c(iota_min)] > (R - 1) F a(r, T_A).

    Implements: engine rule (labor notes 3.6; verify L5c) | Spec: 24.6 | Notes: labor 3.6 | Status: provisional"""
    return bool(np.sum(_a(W_own) - _a(W_min)) > (R - 1) * F_build * annuity)


def pace_bound(N, a, K_chg, e, T_eff, x_hat, Phi, T_Gamma):
    """Pace bound on the program: T_prog >= max{N a/K_chg, N e T^eff/(x-hat Phi), T_Gamma(N)}. Returns the three
    bounds and the binding one.

    Implements: cor:labor-pace | Spec: 24.5, 24.6 | Notes: labor 3.7 | Status: theory"""
    b = {"change capacity": N * a / max(K_chg, 1e-12), "decision bandwidth": N * e * T_eff / max(x_hat * Phi, 1e-12),
         "engineering talent": T_Gamma}
    return b, max(b, key=b.get)


# -------------------------------------------------------------------------------------------------
# Acquirer section: permanent capital (ass:acq-pc, prop:acq-pc) and limits to buying growth (prop:acq-limits)
# -------------------------------------------------------------------------------------------------
def annual_flow(values, g_tail):
    """A cash-flow rate constant within each year y of a plan (values[y] on [y, y + 1)) that grows at g_tail after
    the plan: a callable FCF(t) with an exact pv(rho, a, b) = int_a^b e^{-rho t} FCF(t) dt, infinite when b is
    infinite and rho <= g_tail.

    Implements: eq:acq-method (annual flows) | Spec: 16.1 | Notes: acquirer 3.4 | Status: theory"""
    v = np.asarray(values, float)
    n = len(v)

    def seg(rho, lo, hi):                       # int_lo^hi e^{-rho t} dt
        if hi <= lo:
            return 0.0
        if abs(rho) < 1e-12:
            return hi - lo
        return (math.exp(-rho * lo) - (0.0 if math.isinf(hi) else math.exp(-rho * hi))) / rho

    def fcf(t):
        return float(v[int(max(t, 0.0))]) if t < n else float(v[-1]) * math.exp(g_tail * (t - n))

    def pv(rho, a, b):
        tot = 0.0
        for y in range(max(int(math.floor(a)), 0), min(n, int(math.ceil(b)) if not math.isinf(b) else n)):
            tot += v[y] * seg(rho, max(a, y), min(b, y + 1))
        if b > n:
            if math.isinf(b) and rho <= g_tail:
                return math.inf if v[-1] > 0 else (-math.inf if v[-1] < 0 else tot)
            tot += v[-1] * math.exp(-g_tail * n) * seg(rho - g_tail, max(a, n), b)
        return float(tot)
    fcf.pv = pv
    return fcf


def pv_flow(fcf, rho, a, b, pts=None):
    """Present value at time 0 of a cash-flow rate over [a, b]: int_a^b e^{-rho t} FCF(t) dt (b may be infinite);
    exact for annual_flow paths, by quadrature otherwise (an infinite b is a + 600 years, as in the reference script).

    Implements: eq:acq-method (building block) | Spec: 16.1 | Notes: acquirer 3.4 | Status: theory"""
    from scipy import integrate
    if b <= a:
        return 0.0
    if hasattr(fcf, "pv"):
        return fcf.pv(rho, a, b)
    if math.isinf(b):                              # a callable path: 600 years stand in for infinity, as in verify D
        b = a + 600.0
    return integrate.quad(lambda t: math.exp(-rho * t) * fcf(t), a, b, points=pts, limit=400)[0]


def pc_terminal_value(fcf, r_tv, T, pts=None):
    """Terminal value at T of the flows after T at the rate r_tv: TV = int_T^inf e^{-r_tv (t - T)} FCF(t) dt.

    Implements: eq:acq-method | Spec: 16.1 | Notes: acquirer 3.4 | Status: theory"""
    return math.exp(r_tv * T) * pv_flow(fcf, r_tv, T, math.inf, pts)


def pc_method_value(fcf, i, r_tv, T, pts=None):
    """Value of a business under the IRR method at the rate i: int_0^T e^{-i t} FCF dt + e^{-i T} TV, with TV at r_tv.
    At i equal to the hurdle it is P^max (prop:acq-pc(b)); at i = r_tv it is V^tv.

    Implements: eq:acq-method, prop:acq-pc(b) | Spec: 16.1 | Notes: acquirer 3.4 | Status: theory"""
    return pv_flow(fcf, i, 0.0, T, pts) + math.exp(-i * T) * pc_terminal_value(fcf, r_tv, T, pts)


def _root(fun, lo, hi):
    from scipy import optimize
    flo, fhi = fun(lo), fun(hi)
    if not (np.isfinite(flo) and np.isfinite(fhi)) or flo * fhi > 0:
        return None
    return float(optimize.brentq(fun, lo, hi, xtol=1e-12))


def pc_method_irr(fcf, P, r_tv, T, pts=None, lo=-0.5, hi=5.0):
    """Method IRR i^m: the rate at which the method value equals the price P (eq:acq-method); None if no root in
    [lo, hi].

    Implements: eq:acq-method, ass:acq-pc(ii) | Spec: 16.1 | Notes: acquirer 3.4 | Status: theory"""
    return _root(lambda x: pc_method_value(fcf, x, r_tv, T, pts) - P, lo, hi)


def pc_permanent_irr(fcf, P, pts=None, lo=-0.5, hi=5.0):
    """Permanent IRR i^inf: the rate at which int_0^inf e^{-i t} FCF dt equals P (no terminal value); None if no root
    above the flows' long-run growth.

    Implements: prop:acq-pc(a) | Spec: 16.1 | Notes: acquirer 3.4 | Status: theory"""
    def f(x):
        try:
            return pv_flow(fcf, x, 0.0, math.inf, pts) - P
        except (OverflowError, ValueError):
            return math.inf
    return _root(f, lo, hi)


def pc_price_bounds(fcf, i_bar, r_tv, T, pts=None):
    """Entry price at the hurdle and its bounds (prop:acq-pc(b), eq:acq-pmaxbound): P^max = method value at i_bar;
    for i_bar >= r_tv, e^{-(i_bar - r_tv) T} V^tv <= P^max <= V^tv, with V^tv the method value at r_tv.

    Implements: prop:acq-pc(b), eq:acq-pmaxbound | Spec: 16.1 | Notes: acquirer 3.4 | Status: theory"""
    Pm = pc_method_value(fcf, i_bar, r_tv, T, pts)
    Vtv = pc_method_value(fcf, r_tv, r_tv, T, pts)
    return {"P_max": Pm, "V_tv": Vtv, "lower": math.exp(-(i_bar - r_tv) * T) * Vtv, "upper": Vtv,
            "share_of_V_tv": Pm / Vtv if Vtv > 0 else None, "bound_share": math.exp(-(i_bar - r_tv) * T)}


def pc_hurdle_conditions(premium, i_bar, r_tv, T):
    """Program value needed over the status quo for the hurdle (prop:acq-pc(b)): with P = (1 + p) V^tv_sq, the hurdle
    holds if V^tv_prog/V^tv_sq >= (1 + p) e^{(i_bar - r_tv) T} - 1 (sufficient) and only if it is >= p (necessary).

    Implements: prop:acq-pc(b) | Spec: 16.1 | Notes: acquirer 3.4 | Status: theory"""
    return {"sufficient": (1 + premium) * math.exp((i_bar - r_tv) * T) - 1, "necessary": premium}


def pc_debt(fcf, P, ltv, r_debt, T_rep, pts=None):
    """Acquisition debt under the disclosed policy (ass:acq-pc(iii)): ND^rep = int_0^{T_rep} e^{-r_debt t} FCF dt,
    ND_0 = min{LTV P, ND^rep}.

    Implements: ass:acq-pc(iii) | Spec: 16.1 | Notes: acquirer 3.4 | Status: theory"""
    nd_rep = pv_flow(fcf, r_debt, 0.0, T_rep, pts)
    nd0 = max(min(ltv * P, nd_rep), 0.0)
    return {"ND_rep": nd_rep, "ND_0": nd0, "binding": "repayment" if nd_rep <= ltv * P else "LTV"}


def pc_levered_irr(fcf, P, r_tv, T, r_debt, ltv, T_rep, pts=None):
    """Levered method IRR under the debt policy with a cash sweep (prop:acq-pc(c)): free cash flow repays ND_0 at
    r_debt until it is repaid (date T_D); equity E_0 = P - ND_0 receives the flows after T_D and the terminal value
    less any debt left at T. Returns the IRR (None if no root), ND_0, ND^rep, T_D and E_0.

    Implements: prop:acq-pc(c) | Spec: 16.1 | Notes: acquirer 3.4 | Status: theory"""
    from scipy import optimize
    d = pc_debt(fcf, P, ltv, r_debt, T_rep, pts)
    nd0, ndrep = d["ND_0"], d["ND_rep"]
    cum = lambda t: pv_flow(fcf, r_debt, 0.0, t, pts)
    if cum(T) < nd0 - 1e-9:
        TD = None
    elif abs(nd0 - ndrep) < 1e-12 and abs(T_rep - T) < 1e-12:
        TD = T
    elif nd0 <= 0:
        TD = 0.0
    else:
        TD = float(optimize.brentq(lambda t: cum(t) - nd0, 1e-12, T))
    resid = max(math.exp(r_debt * T) * (nd0 - cum(T)), 0.0)
    E0 = P - nd0
    tv = pc_terminal_value(fcf, r_tv, T, pts)

    def eqv(rho):
        a = pv_flow(fcf, rho, TD, T, pts) if TD is not None and TD < T else 0.0
        return a + math.exp(-rho * T) * (tv - resid)
    irr = _root(lambda x: eqv(x) - E0, -0.5, 50.0) if E0 > 0 else None
    return {"irr": irr, "ND_0": nd0, "ND_rep": ndrep, "T_D": TD, "E_0": E0, "TV": tv, "debt_left_at_T": resid}


def pc_levered_irr_capped(TV, P, ND_rep, T):
    """Levered method IRR when the repayment cap binds and T_rep = T_IRR (prop:acq-pc(c)(ii)): equity receives
    nothing before T, so i^m_L = ln[TV/(P - ND^rep)]/T.

    Implements: prop:acq-pc(c) | Spec: 16.1 | Notes: acquirer 3.4 | Status: theory"""
    return math.log(TV / (P - ND_rep)) / T


def pc_growth_weight(m_hat, i_bar_U, G):
    """Growth weight of a permanent owner that holds internal decisions to the unlevered hurdle (prop:acq-pc(d)):
    X^G = m_hat/(i_bar_U - G), (r_w - G)/(i_bar_U - G) times that of a going concern at r_w; None if i_bar_U <= G.

    Implements: prop:acq-pc(d) | Spec: 16.1 | Notes: acquirer 3.4 | Status: theory"""
    return m_hat / (i_bar_U - G) if i_bar_U > G else None


def acq_gmax(m, k_acq, g_org, nd=0.0, r_debt=0.0):
    """Treadmill (prop:acq-limits(a)): with acquisitions paid from the cash margin m and net debt held at nd < k_acq
    per dollar of revenue at r_debt, growth g is financed without new equity iff g <= g^max = (m - r_debt nd + k_acq
    g_org)/(k_acq - nd); g_org + m/k_acq without debt. None if k_acq <= nd.

    Implements: prop:acq-limits(a) | Spec: 16.1 | Notes: acquirer 3.6 | Status: theory"""
    if k_acq <= nd:
        return None
    return (m - r_debt * nd + k_acq * g_org) / (k_acq - nd)


def acq_zero_spend_growth(nrr, subscription_share=1.0, nonsub_growth=0.0):
    """Continuously compounded zero-spend growth of the existing base (Part I prop:acquired-score(d) after Fable F21):
    with the subscription share s of revenue retaining at NRR and the rest changing by gamma_ns a year without spend
    (annual rates, shares at the start of the year), G_i = ln[1 + s (NRR - 1) + (1 - s) gamma_ns]. It equals ln NRR only
    if all revenue is subscription revenue (s = 1, the upper bound on decay when the rest shrinks no faster) and lies in
    [ln NRR, 0] when NRR < 1 and gamma_ns is in [NRR - 1, 0].

    Implements: prop:acquired-score(d), prop:acq-limits(a) | Spec: 16.1 | Notes: acquirer 3.6 | Status: theory"""
    s_ = float(np.clip(subscription_share, 0.0, 1.0))
    a = s_ * (float(nrr) - 1.0) + (1.0 - s_) * float(nonsub_growth)
    if a <= -1.0:
        raise ValueError("the base cannot shrink by 100 percent or more a year")
    return math.log1p(a)


def acq_standstill(g_org, k_acq=None, g=0.0):
    """Acquired growth needed to hold growth g (prop:acq-limits(a); Part I prop:acquired-score(f)), in continuously
    compounded rates: g^acq = g + d^org with organic decay d^org = -g^org, at a cash cost of k_acq (g + d^org) of revenue
    a year; standing still is g = 0. With no new customers g^org = G_i (acq_zero_spend_growth), which is ln NRR only
    when all revenue is subscription revenue; with the company's own organic growth g^org is ln(1 + reported).

    Implements: prop:acq-limits(a), prop:acquired-score(f) | Spec: 16.1 | Notes: acquirer 3.6 | Status: theory"""
    need = max(float(g) - float(g_org), 0.0)
    return {"acquired_growth": need, "target_growth": float(g), "organic_decay": -float(g_org),
            "cash_share_of_revenue": None if k_acq is None else float(k_acq) * need,
            "standstill_acquired_growth": max(-float(g_org), 0.0),
            "standstill_cash_share": None if k_acq is None else float(k_acq) * max(-float(g_org), 0.0)}


def margin_before_financing(ocf, interest_paid, tau, S):
    """Cash margin before acquisitions and before financing (Part I rem:acquired-bounds after IB-4):
    m^cf = (OCF + (1 - tau) interest paid)/S. Under U.S. GAAP interest paid is an operating cash flow (ASC 230), so a
    cost-of-capital charge against OCF as reported charges the debt-financed share twice, by exactly (1 - tau) c_fin,
    c_fin = interest paid/S: charge interest or a cost of capital on the same capital, not both.

    Implements: rem:acquired-bounds | Spec: 16.1 | Notes: acquirer 3.7 | Status: theory"""
    return {"m_before_interest": (float(ocf) + (1.0 - float(tau)) * float(interest_paid)) / float(S),
            "m_after_interest": float(ocf) / float(S), "double_charge": (1.0 - float(tau)) * float(interest_paid) / float(S)}


def acquisition_capital(flows, d):
    """Capital deployed in acquisitions, for the year [0, 1] (rem:acquired-bounds): flows are (outlay, date) with the
    date in years from the start of the year (<= 0 for earlier years). Returns the cumulative outlay, the year-end
    capital decayed at d, the time-weighted average of decayed capital over the year (exact: c e^{d t}(1 - e^{-d})/d
    for t <= 0, c (1 - e^{-d(1 - t)})/d otherwise) and the time-weighted undecayed capital (c for t <= 0, c(1 - t)).

    Implements: rem:acquired-bounds, eq:acquired-bounds | Spec: 16.1 | Notes: acquirer 3.7 | Status: theory"""
    d = float(d)
    cum = sum(c for c, _ in flows)
    end = sum(c * math.exp(-d * (1.0 - t)) for c, t in flows)
    if d > 1e-12:
        avg_d = sum(c * (math.exp(d * t) * (1 - math.exp(-d)) / d if t <= 0 else (1 - math.exp(-d * (1 - t))) / d) for c, t in flows)
    else:
        avg_d = sum(c * (1.0 if t <= 0 else 1 - t) for c, t in flows)
    avg_0 = sum(c * (1.0 if t <= 0 else 1.0 - t) for c, t in flows)
    return {"cumulative": cum, "year_end_decayed": end, "time_weighted_decayed": avg_d, "time_weighted": avg_0}


def acquisition_charges(flows, S, g, m_before, m_after, r, nrr):
    """The charging-convention grid for a score with bought growth (Part I rem:acquired-bounds after IB-4), set
    against the margin before financing: (A) level annuity CRF(r, T^life) on every outlay in the window for the full
    year, CRF = r/(1 - e^{-r T^life}), T^life = 1/d; (B) user cost (r + d) on capital decayed at d = -ln NRR at year-end
    (Hall and Jorgenson 1967); (C) the same on time-weighted decayed capital; (D) the level annuity charged from each
    outlay's date. Each charged score R = g + m^cf - charge/S lies below the uncharged g + m^cf, and above the fully
    charged g + m^cf - C_t/S when the charge is below the year's outlay C_t (true in the Paper 1 case). Also the same charges against the margin after interest (the double charge), and the return on
    acquisition capital before interest, m^cf S / K^avg, and after economic depreciation at d.

    Implements: rem:acquired-bounds, eq:acquired-bounds | Spec: 16.1 | Notes: acquirer 3.7 | Status: theory"""
    d = -math.log(float(nrr))
    if d <= 0:
        raise ValueError("the charging grid needs NRR < 1 (a positive decay rate)")
    life = 1.0 / d
    crf = float(capital_recovery_factor(r, life))
    K = acquisition_capital(flows, d)
    ch = {"annuity_full_year": crf * K["cumulative"], "user_cost_year_end": (r + d) * K["year_end_decayed"],
          "user_cost_time_weighted": (r + d) * K["time_weighted_decayed"], "annuity_from_dates": crf * K["time_weighted"]}
    cur = sum(c for c, t in flows if 0 < t <= 1)
    out = {"d": d, "life": life, "crf": crf, "capital": K, "uncharged_before_interest": g + m_before,
           "uncharged_after_interest": g + m_after, "fully_charged_before_interest": g + m_before - cur / S,
           "scores_before_interest": {k: g + m_before - v / S for k, v in ch.items()},
           "scores_after_interest_double_charged": {k: g + m_after - v / S for k, v in ch.items()}, "charges": ch}
    Kavg = K["time_weighted_decayed"]
    out["return_on_acquisition_capital"] = m_before * S / Kavg if Kavg > 0 else None
    out["return_after_depreciation"] = (m_before * S / Kavg - d) if Kavg > 0 else None
    return out


def acquisition_price_bounds(X, r=None, nrr=None):
    """Largest price per dollar of acquired revenue at which acquired growth raises the charged score R^A_X
    (prop:acquired-score(a); rem:acquired-bounds): charged in full, iff k^acq < X, so the sign flips at X = k^acq; spread
    as a level annuity, iff CRF(r, T^life) k^acq < X; as a user cost, iff (r + d) k^acq < X, d = -ln NRR. The level of
    X is not identified by the data (Paper 1 decision D-1), so the engine reports these at evaluation points.

    Implements: prop:acquired-score(a), rem:acquired-bounds | Spec: 16.1, 28 | Notes: acquirer 3.7 | Status: theory"""
    out = {"X": float(X), "full_charge": float(X), "annuity": None, "user_cost": None}
    if r is not None and nrr is not None and float(nrr) < 1:
        d = -math.log(float(nrr))
        out["annuity"] = float(X) / float(capital_recovery_factor(r, 1.0 / d))
        out["user_cost"] = float(X) / (float(r) + d)
    return out


def sign_flips(points, values) -> list:
    """Where a recommendation that depends on the level of X changes across evaluation points: the adjacent pairs of
    points (in increasing X) whose values differ (D-1: report X-dependent conclusions at the points and flag flips).

    Implements: prop:playbook-rank(b), prop:acquired-score(a), cor:prod-dilution | Spec: 28 | Notes: playbook spec 2.4 | Status: spec"""
    pv = sorted(zip(map(float, points), values), key=lambda t: t[0])
    return [{"between": (a[0], b[0]), "from": a[1], "to": b[1]} for a, b in zip(pv, pv[1:]) if a[1] != b[1]]


def acq_size_limit(g, g_org, S, n_dl=None, eps_sz=0.0, h_0=None, S_tg0=None):
    """Deal size (prop:acq-limits(b)): holding g needs a mean target revenue (g - g_org) S/n_dl; with eps_sz > 0
    targets clear the hurdle only up to S^tg_max = S^tg_0 h_0^{1/eps_sz}, so g holds only while S <= S^max =
    n_dl S^tg_max/(g - g_org), and beyond it growth is at most g_org + n_dl S^tg_max/S. A limit that is off (n_dl
    None, eps_sz 0) is infinite.

    Implements: prop:acq-limits(b), ass:acq-limits(ii) | Spec: 16.1 | Notes: acquirer 3.6 | Status: theory"""
    need = (g - g_org) * S / n_dl if (n_dl and g > g_org) else None
    S_tg_max = math.inf
    if eps_sz and eps_sz > 0 and h_0 is not None and S_tg0 is not None:
        S_tg_max = S_tg0 * h_0 ** (1.0 / eps_sz)
    if n_dl is None or math.isinf(S_tg_max) or g <= g_org:
        return {"mean_target_needed": need, "S_tg_max": S_tg_max, "S_max": math.inf, "g_cap": math.inf, "binds": False}
    S_max = n_dl * S_tg_max / (g - g_org)
    g_cap = g_org + n_dl * S_tg_max / S
    return {"mean_target_needed": need, "S_tg_max": S_tg_max, "S_max": S_max, "g_cap": g_cap, "binds": bool(S > S_max)}


def challenge_probability(s, a):
    """Probability that a deal adding to cumulative niche share s is challenged: p^ch(s) = min(1, a s^2), convex and
    nondecreasing (the form of verify H4; prop:acq-limits(c) needs only convexity and monotonicity). a = 0 is off.

    Implements: ass:acq-limits(iii) | Spec: 16.1 | Notes: acquirer 3.6 | Status: spec"""
    return min(1.0, float(a) * float(s) ** 2)


def series_review_proceeds(net_value, n, delta_s, a, L_ch, series=True):
    """Series review (prop:acq-limits(c)): the n-th deal in a niche proceeds iff V_n - P_n >= p^ch(n Delta s) L^ch
    under series review, p^ch(Delta s) L^ch if each deal is judged alone.

    Implements: prop:acq-limits(c) | Spec: 16.1 | Notes: acquirer 3.6 | Status: theory"""
    s = n * delta_s if series else delta_s
    return bool(net_value >= challenge_probability(s, a) * L_ch)


def series_review_stop(net_value, delta_s, a, L_ch, series=True, n_max=400):
    """First deal in a niche that the review test stops (prop:acq-limits(c)); n_max if none is stopped. Series
    review stops the owner no later than deal-by-deal review.

    Implements: prop:acq-limits(c) | Spec: 16.1 | Notes: acquirer 3.6 | Status: theory"""
    return next((n for n in range(1, n_max) if not series_review_proceeds(net_value, n, delta_s, a, L_ch, series)), n_max)


def fdi_multiplier(p_fdi, T_fdi, r):
    """Foreign-investment review (prop:acq-limits(c)): a delay T^fdi with probability p^fdi scales a deal's net value
    by 1 - p^fdi (1 - e^{-r T^fdi}).

    Implements: prop:acq-limits(c) | Spec: 16.1 | Notes: acquirer 3.6 | Status: theory"""
    return 1.0 - float(p_fdi) * (1.0 - math.exp(-float(r) * float(T_fdi)))


def repricing_optimum(x_bar, h_cp=1.0, upsilon_cp=None):
    """Revenue-maximizing repricing with exponential switching-cost ratios of mean x_bar (prop:acq-retention(a),
    prop:acq-limits(d)): x* = min{(h^cp x_bar - 1)^+, upsilon^cp}; h^cp = 1 and no cap give x_bar - 1.

    Implements: prop:acq-retention(a), prop:acq-limits(d) | Spec: 16.1 | Notes: acquirer 3.5, 3.6 | Status: theory"""
    x = max(h_cp * x_bar - 1.0, 0.0)
    return x if upsilon_cp is None else min(x, float(upsilon_cp))


def retained_revenue(upsilon, x_bar, h_cp=1.0):
    """Revenue retained after a repricing upsilon with exponential switching-cost ratios of mean x_bar scaled by h^cp
    (prop:acq-limits(d)): (1 + upsilon) S_sw(upsilon/h^cp) = (1 + upsilon) e^{-upsilon/(h^cp x_bar)}.

    Implements: prop:acq-retention(a), prop:acq-limits(d) | Spec: 16.1 | Notes: acquirer 3.5, 3.6 | Status: theory"""
    return (1.0 + upsilon) * math.exp(-upsilon / (h_cp * x_bar))


# -------------------------------------------------------------------------------------------------
# The lever map (part2/theory_playbook.tex sec:playbook; notes/playbook_engine_spec.md Section 2)
# -------------------------------------------------------------------------------------------------
def playbook_calibration(g, sigma, k, alpha, r_sigma, X=None, G=None) -> dict:
    """Position in which the observed growth spend is optimal (ass:playbook-calib, lem:playbook-calib): with neither
    an EV/revenue multiple X nor market growth G, X_hat = k + r_sigma/alpha, Delta = sigma/r_sigma, G_i = g - Delta,
    ell = Delta/sigma^alpha, so sigma_star(ell, X_hat - k) = sigma. A given X sets r_sigma = alpha (X - k); a given G
    sets Delta = g - G; with both, ell = (g - G)/sigma^alpha and the spend need not be optimal.

    Implements: ass:playbook-calib, lem:playbook-calib | Spec: 28 | Notes: playbook spec 2.2 | Status: theory"""
    sigma = max(float(sigma), 1e-9)
    if X is not None and G is not None:
        Delta = float(g) - float(G)
        return {"X_hat": float(X), "G_i": float(G), "Delta": Delta, "ell": max(Delta, 1e-9) / sigma ** alpha,
                "source": "EV/revenue multiple and market growth (inputs)"}
    if X is not None:
        rs = alpha * (float(X) - k)
        src, Xh = "EV/revenue multiple (input); observed spend optimal", float(X)
    elif G is not None:
        rs = sigma / max(float(g) - float(G), 1e-9)
        src, Xh = "market growth (input); observed spend optimal", k + sigma / max(float(g) - float(G), 1e-9) / alpha
    else:
        rs, src = float(r_sigma), "spend ratio r_sigma (Paper 1 median); observed spend optimal"
        Xh = k + rs / alpha
    Delta = sigma / max(rs, 1e-9)
    return {"X_hat": Xh, "G_i": float(g) - Delta, "Delta": Delta, "ell": Delta / sigma ** alpha, "source": src, "r_sigma": rs}


def x_dagger_0(k, a, alpha, ell):
    """Growth weight above which a small saving on the growth engine beats the same proportional saving on a line of
    cost share a (prop:playbook-rank(b)): X^ddagger_0 = k + a^(1-alpha)/(alpha ell).

    Implements: prop:playbook-rank(b) | Spec: 28 | Notes: playbook spec 2.4 | Status: theory"""
    if float(ell) <= 0:            # no demand pull (no growth spend on the S&M basis): the growth engine never outranks a
        return math.inf
    return k + max(float(a), 0.0) ** (1 - alpha) / (alpha * float(ell))


def x_dagger_exact(k, ell, alpha, d_sigma, da):
    """Exact switch weight for a saving d_sigma on the growth engine against da of cost (eq:reg-Xdag):
    X^ddagger = k + (1/ell) [da / (C_alpha ((1 - d_sigma)^(-alpha/(1-alpha)) - 1))]^(1 - alpha).

    Implements: eq:reg-Xdag, prop:reg-weight(e) | Spec: 28 | Notes: regimes 3.3; playbook spec 2.4 | Status: theory"""
    _, C = part1_constants(alpha)
    den = C * ((1 - d_sigma) ** (-alpha / (1 - alpha)) - 1)
    if float(ell) <= 0:
        return math.inf
    return k + (max(float(da), 0.0) / max(den, 1e-300)) ** (1 - alpha) / float(ell)


def x_dagger_demand_pull(k, a, alpha, ell):
    """Demand-pull version of the switch weight: k + (alpha a)^(1-alpha)/(alpha ell) (prop:playbook-rank(c)).

    Implements: prop:playbook-rank(c) | Spec: 28 | Notes: playbook spec 2.4 | Status: theory"""
    if float(ell) <= 0:
        return math.inf
    return k + (alpha * max(float(a), 0.0)) ** (1 - alpha) / (alpha * float(ell))


def headroom_switch(a, sigma_opt, alpha):
    """Share of today's headroom at which the growth engine and a line of cost share a rank equal
    (prop:playbook-rank(d)): h^ddagger/h = (a/sigma*)^(1-alpha).

    Implements: prop:playbook-rank(d) | Spec: 28 | Notes: playbook spec 2.4 | Status: theory"""
    return (max(float(a), 0.0) / max(float(sigma_opt), 1e-12)) ** (1 - alpha)


def lever_values(m0, G, ell, X, k, alpha, x, a_GA, a_RD, c_h, keep_rep, keep_own, r_o, delta_K) -> dict:
    """Value of each lever at the owner's weight X for the common proportion x (prop:playbook-rank(a), cor:priorities):
    growth-engine automation x sigma* (exact R_star(ell (1-x)^(-alpha)) - R_star(ell)), demand pull x sigma*/alpha
    (exact R_star(ell (1+x)) - R_star(ell)), overhead x a_GA, engineering x a_RD, cost of revenue x (1 - phi_e) c_h with
    keep_rep = 1 - phi C0 for a saving every rival replicates and keep_own for one no rival can make (passthrough_terms;
    Part I prop:levers-position(a), round 2: phi is a rate on the unit-cost saving, margins at the post-cut price; the
    dollar share dur does not enter the score), one point of retention (X - k) 0.01, the AI-product dilution break-even X - k
    (cor:prod-dilution), the capital hurdles g* + delta_K and r_o + delta_K (cor:capital), and the largest price per
    dollar of acquired revenue that raises the charged score, X (prop:acquired-score(a)).

    Implements: prop:playbook-rank(a), cor:priorities, cor:prod-dilution, cor:capital, prop:acquired-score(a) | Spec: 28 | Notes: playbook spec 2.3 | Status: theory"""
    y = max(float(X) - k, 0.0)
    s_opt = float(sigma_star(ell, y, alpha))
    g_opt = float(G) + float(delta_star(ell, y, alpha))
    R0 = float(R_star(m0, G, ell, X, k, alpha))
    return {"sigma_star": s_opt, "g_star": g_opt,
            "growth_automation": x * s_opt, "growth_automation_exact": float(R_star(m0, G, ell * (1 - x) ** (-alpha), X, k, alpha)) - R0,
            "demand_pull": x * s_opt / alpha, "demand_pull_exact": float(R_star(m0, G, ell * (1 + x), X, k, alpha)) - R0,
            "overhead": x * a_GA, "engineering": x * a_RD, "cost_of_revenue_replicable": x * keep_rep * c_h,
            "cost_of_revenue_given_demand": x * keep_own * c_h, "retention_point": y * 0.01, "ai_product_breakeven": y,
            "capital_hurdle_score": g_opt + delta_K, "capital_hurdle_value": r_o + delta_K, "acquisition_max_price": float(X)}


__all__ = [n for n in dir() if not n.startswith("_")]
