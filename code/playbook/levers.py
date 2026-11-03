"""Position-level lever map (part2/theory_playbook.tex, Proposition prop:playbook-rank; Paper 1 Section
sec:levers-position). Every formula is the engine's (autofrontier.formulas); this module only evaluates them at an
archetype's Part I state and an owner's growth weight.

Lever values are first-order changes in the maximal Rule-of-X score R*_X at the owner's optimum (Proposition
prop:envelope, Corollary cor:priorities), for a common normalization: the same proportional improvement x in each
line (x = PROP, 10 percent). The exact values re-optimize spend and are computed with F.R_star.
"""
from __future__ import annotations

import math

PROP = 0.10      # normalization: 10% of a line automated, or a 10% gain in demand pull
D_G = 0.01       # retention lever: one point of zero-spend growth


def _F():
    from autofrontier import formulas as F
    return F


def regime_weights(st: dict, p) -> dict:
    """Growth weight X_o of each owner (Proposition prop:reg-weight; prop:acq-pc(d)), from engine formulas and the
    engine's regime presets. The marginal dollar of revenue earns m_hat = m0 - k G_i, the margin a permanent dollar
    earns without growth spend (Proposition prop:dynamic(a)); the engine's regimes.growth_weight uses the firm's current
    cash margin instead (engine spec, item W1). Rates are continuous, as in the engine. The revealed weight X_hat is read
    as the public owner's net weight (the panel is public filers); the other owners' weights do not depend on it except
    through the going-concern weight X_gc that removes the public earnings pressure.

    XBOUNDS (P2 theory pass v2, D-1): X_hat - k = r_sigma/alpha is an implication of the spend-ratio calibration, not an
    estimate of the owner's weight; rankings through (X_o - k)/(X_hat - k) do not depend on its level, comparisons of
    X_hat with weights computed from rates (sponsor, permanent acquirer, venture investor) do."""
    F = _F()
    rg, fin = p.regime, p.finance
    k, G, ell, a = st["k"], st["G_i"], st["ell"], st["alpha"]
    m_hat = st["m0"] - k * G
    out = {"m_hat": m_hat}
    X_hat = st["X_hat"]
    out["revealed"] = X_hat
    v0_pub = F.gordon_v0(st["m0"], G, k, ell, rg.public_r, a)
    v0_fam = F.gordon_v0(st["m0"], G, k, ell, rg.public_r + rg.family_r_spread, a)
    out["v0_public"], out["v0_family"] = v0_pub, v0_fam
    # public: the panel's firms are public, so the weight their spending reveals is a public owner's net weight under
    # its earnings pressure, X^my of eq. reg-Xmy (prop:reg-weight(b)); the same firm without the pressure has the
    # going-concern weight X_gc = k + (1 + w_pub)(X_hat - k)
    out["public"] = X_hat
    X_gc = k + (1 + rg.public_myopia) * (X_hat - k)
    out["going_concern_public_rate"] = X_gc
    out["hybrid"] = F.myopic_weight(X_gc, k, rg.hybrid_myopia)
    # family: no earnings pressure and a lower rate, which raises the weight (prop:reg-weight(a)); X_gc scaled by
    # v0(r_fam)/v0(r_pub) when the Gordon root exists at both rates, otherwise held at X_gc (a lower bound)
    out["private_family"] = X_gc * (v0_fam / v0_pub) if (v0_pub and v0_fam) else X_gc
    out["family_scaled"] = bool(v0_pub and v0_fam)
    # PE: hold and exit at the EBITDA rule (prop:reg-weight(c)), at entry (tau = hold). Eq. reg-Xexit holds for any
    # finite horizon, so G is not capped at r; at r = G it is its limit m_hat tau + X_T. The terminal value uses the
    # marginal EBITDA margin m_hat^E; for a permanent dollar without growth spend that is m0 (capital spending is not
    # an EBITDA item), which differs from m_hat = m0 - k G_i by the growth capital.
    def _exit(m, r, Gx, tau, X_T):
        if abs(r - Gx) < 1e-9:
            return m * tau + X_T
        return F.exit_weight(m, r, Gx, tau, X_T)
    r_pe = rg.pe_irr_target
    X_T_pe = rg.h_x * rg.pe_M_exit * st["m0"]
    out["pe"] = _exit(m_hat, r_pe, G, rg.pe_hold, X_T_pe)
    out["pe_mid_hold"] = _exit(m_hat, r_pe, G, rg.pe_hold / 2, X_T_pe)
    # VC: market rule with the engine's exit revenue multiple preset (class d)
    out["vc"] = _exit(m_hat, rg.vc_r, G, rg.vc_horizon, rg.vc_revenue_multiple)
    # permanent capital: going concern at the unlevered hurdle (prop:acq-pc(d)), defined only if the hurdle exceeds
    # the retention growth G_i; otherwise None (the going-concern value of a permanent dollar is unbounded)
    try:
        r_pc = rg.pc_irr_unlevered
    except AttributeError:
        r_pc = math.log(1.25)
    out["pc_hurdle"] = r_pc
    out["permanent_capital"] = (m_hat / (r_pc - G)) if r_pc > G else None
    out["permanent_capital_undefined"] = None if r_pc > G else "retention growth G_i at or above the unlevered hurdle"
    out["screening"] = None      # filled by the caller from Lemma lem:valuation2 if wanted
    return out


def x_dagger0(a_line: float, ell: float, k: float, alpha: float) -> float:
    """First-order switch weight X^ddagger_0 = k + a^(1-alpha)/(alpha ell): at X above it, automating a proportion x of
    the growth activities raises R*_X more than automating the same proportion of a line of size a (Proposition
    prop:playbook-rank(b); the small-saving limit of eq. reg-Xdag)."""
    if ell <= 0:          # no growth spend on the S&M basis: no demand pull, the growth engine never outranks a line
        return math.inf
    return k + a_line ** (1 - alpha) / (alpha * ell)


def x_dagger_exact(da: float, d_sigma: float, ell: float, k: float, alpha: float) -> float:
    """Exact switch weight of Proposition prop:reg-weight(e), eq. reg-Xdag."""
    C = (1 - alpha) * alpha ** (alpha / (1 - alpha))
    return k + (1 / ell) * (da / (C * ((1 - d_sigma) ** (-alpha / (1 - alpha)) - 1))) ** (1 - alpha)


def lever_values(st: dict, X: float, c_h: float, keep: float, delta_K: float, r_o: float) -> dict:
    """Lever values at the owner's optimum with weight X (Proposition prop:playbook-rank(a)); points of revenue (x100
    for score points). Uses F.sigma_star, F.delta_star, F.R_star and F.lambda_after_savings."""
    F = _F()
    k, ell, a, G = st["k"], st["ell"], st["alpha"], st["G_i"]
    y = max(X - k, 0.0)
    sig = float(F.sigma_star(ell, y, a))
    Dst = float(F.delta_star(ell, y, a))
    R0 = float(F.R_star(st["m0"], G, ell, X, k, a))
    ell_cost = float(F.lambda_after_savings(ell, PROP, a))
    out = {
        "X": X, "X_minus_k": y, "sigma_star": sig, "Delta_star": Dst, "g_star": G + Dst, "R_star": R0,
        # growth engine: automate PROP of the growth activities (prop:tasks-aggregate(b)); first order sigma* x
        "ge_cost_first": PROP * sig,
        "ge_cost_exact": float(F.R_star(st["m0"], G, ell_cost, X, k, a)) - R0,
        # growth engine: PROP gain in demand pull (cor:priorities(ii)); first order x sigma*/alpha
        "ge_pull_first": PROP * sig / a if a > 0 else float("nan"),
        "ge_pull_exact": float(F.R_star(st["m0"], G, ell * (1 + PROP), X, k, a)) - R0,
        # overhead and engineering: PROP of the line (cor:priorities(i)); linear, survives saturation
        "oh": PROP * st["a_GA"],
        # maintenance S&M (netted basis, decision 7): a cost line like overhead, reported beside the ranking, not in it
        "sm_maint": PROP * float(st.get("a_SM", 0.0)),
        "eng": PROP * st["rd"],
        # cost of revenue: PROP of human service cost, of which the margin keeps 1 - phi C0 when every rival replicates
        # the cut (Part I round 2, B1: phi the industry pass-through rate, margins at the post-cut price; Part I
        # prop:levers-position(a), (d)). The durable share dur = 1 - phi (1 - HHI) of cor:ext-game-engine(a) is the share
        # of the dollar saving with the volume gain; it does not enter the score. keep comes from the engine
        # (economics info pass_through.keep_replicable), so the engine's lever map and this table agree.
        "cor": PROP * keep * c_h,
        "cor_given_prices": PROP * c_h,
        # retention: one point of zero-spend growth (cor:priorities(iii)); linear
        "ret_point": (X - k) * D_G,          # exact for any X (R* is linear in G_i); negative if X < k
        # AI product: largest margin dilution per point of retention that still pays (cor:prod-dilution(i))
        "dilution_breakeven": X - k,
        "interior": X > k,                   # X <= k: no growth spend at the optimum (sigma* = 0)
        # capital for labor: opex saved per dollar of capital must exceed g* + delta_K (score) and r + delta_K (value).
        # Tax convention (P2 theory pass v2, prop:playbook-rank(f)): these hurdles hold after tax as stated when server
        # capital is fully expensed, psi = 1, which is current U.S. law for domestic servers acquired after 19 Jan 2025
        # (IRC sec. 168(k) as amended by P.L. 119-21 sec. 70301; IRS Notice 2026-11) unless the firm elects out
        # (sec. 168(k)(7)). For servers used predominantly outside the United States (ADS, sec. 168(g)(1)(A); no bonus)
        # or after an election out, multiply both by Upsilon = (1 - psi tau)/(1 - tau) (prop:acct-tax). Not applied here.
        "cap_hurdle_score": G + Dst + delta_K, "cap_hurdle_value": r_o + delta_K,
        # acquisition: acquired revenue raises the charged score iff its price per dollar is below X (prop:acquired-score(a)).
        # XBOUNDS: the sign of this test depends on the level of X, which Part I does not identify (D-1); report it at
        # X in {2.5, 5, 9} as well as at the owner's weight, and do not read X_hat = r_sigma/alpha as an estimate.
        "acq_max_price_score": X, "acq_max_price_r40": 1.0,
    }
    # switch thresholds (prop:playbook-rank(b), (c)) against overhead (G&A)
    if ell > 0:
        out["X_dagger0_oh"] = x_dagger0(st["a_GA"], ell, k, a)
        out["X_dagger_oh"] = x_dagger_exact(PROP * st["a_GA"], PROP, ell, k, a)
        out["X_dagger0_eng"] = x_dagger0(st["rd"], ell, k, a)
        out["X_dagger0_pull_oh"] = k + (a * st["a_GA"]) ** (1 - a) / (a * ell)
    else:
        out["X_dagger0_oh"] = out["X_dagger_oh"] = out["X_dagger0_eng"] = out["X_dagger0_pull_oh"] = float("inf")
    # headroom at which overhead overtakes the growth engine, relative to today's (prop:playbook-rank(c))
    out["headroom_switch"] = (st["a_GA"] / sig) ** (1 - a) if sig > 0 else float("inf")
    # ranking among the proportional levers (cost-automation normalization)
    vals = {"growth engine": out["ge_cost_first"], "overhead (G&A)": out["oh"], "engineering (R&D)": out["eng"],
            "cost of revenue": out["cor"]}
    out["ranking"] = sorted(vals, key=lambda kk: -vals[kk])
    out["ranking_values"] = vals
    return out
