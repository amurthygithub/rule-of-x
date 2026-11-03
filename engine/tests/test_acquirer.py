# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Permanent capital and the limits to buying growth (theory_acquirer.tex; notes/acquirer_notes.md Section 3).

The reference script code/verify_part2_acquirer.py writes macro files when it runs, so it is not imported; these
tests repeat its checks D0 to D4 and H1 to H5 against the engine's formulas, and test the engine rules: a class d
limit whose params.yaml value is null takes its neutral value unless a scenario sets it, verified_domain is never a
range, and annual rates enter through to_continuous()."""
import math

import numpy as np
import pytest

from autofrontier import config, formulas as F, regimes
from autofrontier.config import to_continuous

LIMIT_KEYS = ("nd", "n_dl", "eps_sz", "h_0", "a_ch", "delta_s", "L_ch", "p_fdi", "T_fdi", "h_cp", "upsilon_cp")
RNG = np.random.default_rng(20261029)


def _params_yaml():
    dd = config.find_data_dir()
    return config.read_yaml(dd / "params.yaml") if dd is not None and (dd / "params.yaml").is_file() else None


# ---------------- presets from params.yaml ----------------
def test_pc_presets_from_params_yaml(params):
    raw = _params_yaml()
    if raw is None:
        pytest.skip("no params.yaml")
    pc = raw["ownership_regimes"]["permanent_capital"]
    rg = params.regime
    assert rg.pc_irr_unlevered == pytest.approx(to_continuous(pc["hurdle_unlevered_irr_annual"]["value"]))
    assert rg.pc_irr_levered == pytest.approx(to_continuous(pc["hurdle_levered_irr_annual"]["value"]))
    assert round(rg.pc_irr_unlevered, 4) == 0.2231 and round(rg.pc_irr_levered, 4) == 0.5008       # verify D0
    assert rg.pc_window_years == pc["irr_window_years"]["value"] and rg.pc_ltv == pc["debt_ltv_cap_share_of_ev"]["value"]
    assert rg.pc_repay_years == pc["debt_repayment_years"]["value"] and rg.pc_covenant == pc["covenant_max_leverage"]["value"]
    d = pc["debt_rate_r_debt_annual"]
    assert rg.pc_debt_rate == pytest.approx(to_continuous(d["value"]))                              # annual -> ln(1 + r)
    lo, hi = params.range("regime.pc_debt_rate")
    assert lo == pytest.approx(to_continuous(d["range"][0])) and hi == pytest.approx(to_continuous(d["range"][1]))
    assert rg.pc_r_tv == pytest.approx(to_continuous(pc["terminal_value_rate_r_tv_annual"]["value"]))


def test_null_limits_take_neutral_values_and_never_verified_domain(params):
    raw = _params_yaml()
    for k in LIMIT_KEYS:
        key = f"limits.{k}"
        m = params.meta(key)
        assert "neutral_value" in m
        assert params.get(key) == m["neutral_value"], key
        assert params.range(key) is None, f"{key}: a null limit has no sensitivity range"
        v, on = regimes.limit(params, key)
        assert not on
    if raw is not None:
        node = raw["acquirer"]["limits"]["debt_and_deal_capacity"]["max_deals_per_year_n_dl"]
        dom = node.get("verified_domain")
        assert node["value"] is None and params.range("limits.n_dl") != dom
    # nothing the engine samples or screens comes from a limit
    assert not any(k.startswith("limits.") for k in params.scenario_parameters(("b", "c", "d")))


def test_scenario_turns_a_limit_on(params):
    q = params.copy()
    q.set("limits.a_ch", 2.0, origin="scenario test")
    v, on = regimes.limit(q, "limits.a_ch")
    assert v == 2.0 and on
    v, on = regimes.limit(params, "limits.a_ch")
    assert v == 0.0 and not on


def test_neutral_rule_without_params_yaml():
    p = config.load_params(use_params_yaml=False)
    for k in LIMIT_KEYS:
        assert p.get(f"limits.{k}") == p.meta(f"limits.{k}")["neutral_value"]


# ---------------- prop:acq-pc (verify D1 to D4) ----------------
def _paths(n=40):
    for _ in range(n):
        f0, f1 = RNG.uniform(0, 0.2), RNG.uniform(0.1, 0.6)
        Gx, trun = RNG.uniform(-0.15, 0.05), RNG.uniform(0, 3)
        w = RNG.uniform(0.06, 0.14)
        fcf = (lambda f0, f1, Gx, trun: (lambda t: math.exp(Gx * t) * (f0 if t < trun else f1)))(f0, f1, Gx, trun)
        pts = [trun] if 0 < trun < 5 else None
        yield fcf, w, pts, Gx


def test_method_vs_permanent_irr_and_price_bounds():
    T = 5.0
    for fcf, w, pts, Gx in _paths():
        P = RNG.uniform(0.3, 1.5) * F.pc_method_value(fcf, w, w, T, pts)
        im = F.pc_method_irr(fcf, P, w, T, pts, lo=w - 0.3)
        ip = F.pc_permanent_irr(fcf, P, pts, lo=Gx + 1e-3)
        assert (im >= ip - 1e-7) == (ip >= w - 1e-7)                                   # prop:acq-pc(a)
        rb = RNG.uniform(w, 0.6)
        b = F.pc_price_bounds(fcf, rb, w, T, pts)
        assert b["lower"] - 1e-9 <= b["P_max"] <= b["upper"] + 1e-9                    # eq:acq-pmaxbound


def test_leverage_raises_irr_iff_unlevered_above_debt_rate():
    T, rd, ltv = 5.0, math.log(1.09625), 0.85
    for fcf, w, pts, Gx in _paths(30):
        P = RNG.uniform(0.3, 1.5) * F.pc_method_value(fcf, w, w, T, pts)
        im = F.pc_method_irr(fcf, P, w, T, pts, lo=w - 0.3)
        lev = F.pc_levered_irr(fcf, P, w, T, rd, ltv, 5.0, pts)
        if lev["irr"] is None or abs(im - rd) < 1e-6:
            continue
        assert (lev["irr"] > im) == (im > rd)                                          # prop:acq-pc(c)(i)


def test_levered_irr_closed_form_when_repayment_cap_binds():
    T, rd, ltv, rtv = 5.0, math.log(1.09625), 0.85, math.log(1.0934)
    for _ in range(20):
        f1, Gx = RNG.uniform(0.1, 0.6), RNG.uniform(-0.12, 0.05)
        fcf = (lambda f1, Gx: (lambda t: f1 * math.exp(Gx * t)))(f1, Gx)
        P = 2.0 * F.pv_flow(fcf, rd, 0, T) / ltv
        lev = F.pc_levered_irr(fcf, P, rtv, T, rd, ltv, T)
        assert abs(lev["ND_0"] - lev["ND_rep"]) < 1e-9
        assert lev["irr"] == pytest.approx(F.pc_levered_irr_capped(lev["TV"], P, lev["ND_rep"], T), abs=1e-7)


def test_growth_weight_ratio():
    m, rw, rp, G = 0.3, math.log(1.0934), math.log(1.25), math.log(0.95)
    assert F.pc_growth_weight(m, rp, G) / F.pc_growth_weight(m, rw, G) == pytest.approx((rw - G) / (rp - G))
    assert F.pc_growth_weight(m, 0.01, 0.02) is None


# ---------------- prop:acq-limits (verify H1 to H5) ----------------
def test_gmax_identity_and_limits():
    for _ in range(200):
        m, k, go, nd, rd = RNG.uniform(0.05, 0.4), RNG.uniform(0.5, 3), RNG.uniform(-0.1, 0.05), RNG.uniform(0, 0.4), RNG.uniform(0.03, 0.12)
        gm = F.acq_gmax(m, k, go, nd, rd)
        assert (m + nd * gm) - (k * (gm - go) + rd * nd) == pytest.approx(0.0, abs=1e-12)   # sources = uses at g^max
        assert F.acq_gmax(m, k, go) == pytest.approx(go + m / k)
    assert F.acq_gmax(0.2, 0.3, 0.0, nd=0.3) is None
    s = F.acq_standstill(math.log(0.93), 1.2)
    assert s["acquired_growth"] == pytest.approx(0.0726, abs=1e-4) and s["cash_share_of_revenue"] == pytest.approx(1.2 * 0.0726, abs=1e-3)


def test_zero_spend_growth_and_required_acquired_growth():
    """Fable F21 in P1 prop:acquired-score(d), (f) and P2 prop:acq-limits(a) (verify E4, H6): G_i = ln[1 + s (NRR - 1) +
    (1 - s) gamma_ns], ln NRR only when all revenue is subscription; holding g needs acquired growth g + d^org."""
    for _ in range(500):
        n_, s_ = RNG.uniform(0.80, 0.999), RNG.uniform(0, 1)
        gm = RNG.uniform(n_ - 1, 0.0)
        gi = F.acq_zero_spend_growth(n_, s_, gm)
        assert math.log(n_) - 1e-12 <= gi <= 1e-12
        assert math.exp(gi) == pytest.approx(s_ * n_ + (1 - s_) * (1 + gm), rel=1e-12)
        assert F.acq_zero_spend_growth(n_, 1.0, gm) == pytest.approx(math.log(n_), rel=1e-12)
        g = RNG.uniform(0, 1)
        r = F.acq_standstill(gi, 2.0, g)
        assert r["acquired_growth"] == pytest.approx(g - gi) and r["cash_share_of_revenue"] == pytest.approx(2.0 * (g - gi))
        assert r["standstill_acquired_growth"] == pytest.approx(-gi)
    # H6: 2025 growth 94.7% simple (66.6% continuous); NRR 91% to 95%, no new customers, all on subscription: 71.7% to 76.0%;
    # at the company's reported Q2 2026 organic growth of 3%: 63.7%
    g25c = math.log(1306404 / 671053)                      # FY2025 over FY2024 revenue (F-1 extract)
    req = sorted(F.acq_standstill(F.acq_zero_spend_growth(n), None, g25c)["acquired_growth"] for n in (0.91, 0.95))
    assert round(100 * req[0], 1) == 71.7 and round(100 * req[1], 1) == 76.0
    assert round(100 * F.acq_standstill(math.log1p(0.03), None, g25c)["acquired_growth"], 1) == 63.7


def test_charging_grid_on_margins_before_interest():
    """IB-4 in P1 rem:acquired-bounds (verify E12, E13, E14): against operating cash flow after interest, a cost-of-capital
    charge charges financing twice by exactly (1 - tau) c_fin; on the margin before financing every convention lies
    between the fully charged and the uncharged score; the time average of decayed capital is exact."""
    for _ in range(200):
        S, tau = RNG.uniform(5e8, 3e9), RNG.choice([0.0, 0.24])
        ocf, ip = RNG.uniform(0.05, 0.3) * S, RNG.uniform(0.0, 0.15) * S
        flows = [(RNG.uniform(1e8, 1e9), -1.5), (RNG.uniform(1e8, 1e9), -0.5), (RNG.uniform(1e8, 2e9), RNG.uniform(0.05, 0.95))]
        nrr, r, g = RNG.uniform(0.88, 0.98), math.log(1.0934), RNG.uniform(0.0, 1.0)
        mb = F.margin_before_financing(ocf, ip, tau, S)
        assert mb["m_before_interest"] - mb["m_after_interest"] == pytest.approx((1 - tau) * ip / S) == pytest.approx(mb["double_charge"])
        gr = F.acquisition_charges(flows, S, g, mb["m_before_interest"], mb["m_after_interest"], r, nrr)
        cur = sum(c for c, t in flows if 0 < t <= 1)
        for k, v in gr["scores_before_interest"].items():
            # below the uncharged score always; above the fully charged score iff the charge is below this year's outlay
            # (E8: true in the case because the annuity on all outlays since 2023 is below the current year's outlay)
            assert v < gr["uncharged_before_interest"], k
            assert (v > gr["fully_charged_before_interest"]) == (gr["charges"][k] < cur), k
            assert v - gr["scores_after_interest_double_charged"][k] == pytest.approx(mb["double_charge"])
        d = -math.log(nrr)
        from scipy.integrate import quad
        num = sum(c * quad(lambda s_: math.exp(-d * (s_ - t)), max(t, 0.0), 1.0)[0] for c, t in flows)
        assert gr["capital"]["time_weighted_decayed"] == pytest.approx(num, rel=1e-9)
        assert gr["return_after_depreciation"] == pytest.approx(gr["return_on_acquisition_capital"] - d)


def test_acquisition_price_rule_at_evaluation_points():
    """P1 prop:acquired-score(a) at the D-1 evaluation points (verify E15): charged in full, acquired growth raises
    R^A_X iff X > k^acq: at X = 2.5 for Eventbrite (1.73) and AOL (2.30), not Vimeo (3.23); at 5 and 9 for all three.
    Spread as an annuity or a user cost the bound is X/CRF or X/(r + d), above k^acq at every point."""
    deals = {"Eventbrite": 1.73, "AOL": 2.30, "Vimeo": 3.23}
    r = math.log(1.0934)
    for X, passes in ((2.5, {"Eventbrite", "AOL"}), (5.0, set(deals)), (9.0, set(deals))):
        for nrr in (0.91, 0.95):
            b = F.acquisition_price_bounds(X, r, nrr)
            assert {nm for nm, k in deals.items() if k < b["full_charge"]} == passes
            assert all(k < b["annuity"] and k < b["user_cost"] for k in deals.values())
    flips = F.sign_flips([2.5, 5.0, 9.0], [3.23 < x for x in (2.5, 5.0, 9.0)])
    assert flips == [{"between": (2.5, 5.0), "from": False, "to": True}]


def test_limits_check_uses_organic_growth(golden_run):
    """regimes.limits_check takes organic growth from a reported value (ln(1 + x), company-defined) or from G_i, never
    ln NRR for a firm with non-subscription revenue, and reports both cases."""
    from autofrontier import regimes as R
    res, _ = golden_run("synthetic")
    firm, p = res["firm_obj"], res["params"]
    reg = R.make_regime("permanent_capital", p, firm)
    saved = dict(firm.regime)
    try:
        firm.regime.update(nrr=0.93, subscription_share=0.6, nonsub_zero_spend_growth=0.0, acquisition_price_to_revenue=2.0,
                           target_growth=0.30)
        lim = R.limits_check(firm, p, reg)
        gi = math.log(1 + 0.6 * (0.93 - 1))
        assert lim["g_org"] == pytest.approx(gi) and lim["g_org"] > math.log(0.93)
        assert lim["treadmill"]["acquired_growth"] == pytest.approx(math.log1p(0.30) - gi)
        firm.regime.update(organic_growth_reported=0.03)
        lim = R.limits_check(firm, p, reg)
        assert lim["g_org"] == pytest.approx(math.log1p(0.03)) and "company-defined" in lim["g_org_basis"]
        assert set(lim["treadmill"]["cases"]) == {"no_new_customers", "reported_organic"}
        firm.regime.update(operating_cash_flow=0.2 * firm.part1["S"], interest_paid=0.05 * firm.part1["S"], interest_tax_rate=0.24,
                           acquisition_outlays="2023:3e8; 2024:5e8; 2025:8e8@0.8")
        ag = R.limits_check(firm, p, reg)["acquired_growth"]
        assert ag["applicable"] and ag["scores"]["cash_before_interest"] - ag["scores"]["cash_after_interest"] == pytest.approx(0.76 * 0.05)
        assert ag["charging_grid"] is not None and ag["charging_grid"]["return_on_acquisition_capital"] > 0
    finally:
        firm.regime.clear()
        firm.regime.update(saved)


def test_deal_size_limit():
    for _ in range(200):
        H0, eps, S0 = RNG.uniform(1.0, 3.0), RNG.uniform(0.05, 1.5), RNG.uniform(10, 200)
        ndl, gg, go = RNG.uniform(1, 20), RNG.uniform(0.05, 1.0), RNG.uniform(-0.1, 0.05)
        zmax = S0 * H0 ** (1 / eps)
        Smax = ndl * zmax / (gg - go)
        for S in (0.5 * Smax, 2.0 * Smax):
            r = F.acq_size_limit(gg, go, S, ndl, eps, H0, S0)
            assert r["S_max"] == pytest.approx(Smax) and r["binds"] == (S > Smax)
            assert (r["g_cap"] >= gg - 1e-12) == (S <= Smax)
    off = F.acq_size_limit(0.3, 0.0, 1e9)
    assert math.isinf(off["S_max"]) and not off["binds"]


def test_series_review_and_fdi():
    for _ in range(200):
        ds, Lch, nv, a = RNG.uniform(0.01, 0.1), RNG.uniform(1, 10), RNG.uniform(0.05, 1.0), RNG.uniform(0.5, 5)
        assert F.series_review_stop(nv, ds, a, Lch, True) <= F.series_review_stop(nv, ds, a, Lch, False)
        c = [F.challenge_probability(n * ds, a) * Lch for n in range(1, 30)]
        assert all(b >= x - 1e-15 for x, b in zip(c, c[1:]))
    assert F.series_review_stop(0.1, 0.05, 0.0, 5.0) == 400                     # a = 0: no challenge risk
    assert F.fdi_multiplier(0.0, 1.0, 0.2) == 1.0 and F.fdi_multiplier(0.5, 1.0, 0.2) == pytest.approx(1 - 0.5 * (1 - math.exp(-0.2)))


def test_consumer_law_repricing():
    grid = np.linspace(0, 5, 50001)
    for _ in range(100):
        xb, h, cap = RNG.uniform(1.05, 4), RNG.uniform(0.2, 1), RNG.uniform(0, 3)
        rev = (1 + grid) * np.exp(-grid / (h * xb))
        best = grid[grid <= cap][np.argmax(rev[grid <= cap])]
        assert abs(best - F.repricing_optimum(xb, h, cap)) < 2e-4
        for u in (0.1, 0.5, 1.0):
            assert F.retained_revenue(u, xb, h) <= F.retained_revenue(u, xb, 1.0) + 1e-15
    assert F.repricing_optimum(1.6) == pytest.approx(0.6)


# ---------------- the regime and the limits check in a run ----------------
def test_permanent_capital_regime_in_run(golden_run):
    res, out = golden_run("synthetic")
    rv = res["regimes"]
    assert "permanent_capital" in rv
    pc = rv["permanent_capital"]
    assert pc["r"] == pytest.approx(res["params"].regime.pc_irr_unlevered) and pc["horizon"] is None
    rt = pc["returns"]
    assert rt["applicable"] and rt["with_plan"]["bound_share"] <= rt["with_plan"]["P_max_share_of_V_tv"] <= 1 + 1e-9
    lim = res["regimes_extra"]["limits"]
    assert lim["limits_on"] == [] and lim["deal_size"]["S_max"] == math.inf
    md = (out / "report.md").read_text(encoding="utf-8")
    assert "Permanent capital" in md and "neutral value" in md
