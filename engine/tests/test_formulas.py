# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Unit tests per formula, with limiting cases (spec 19.1)."""
import math

import numpy as np
import pytest

from autofrontier import formulas as F


# ---------------- Part I ----------------
def test_R_star_limits():
    assert F.R_star(0.2, 0.1, 0.1, 1.0, 1.0, 0.3) == pytest.approx(0.2)          # X = k: only m0
    assert F.R_star(0.2, 0.1, 0.0, 3.0, 0.0, 0.3) == pytest.approx(0.2 + 0.3)    # no opportunity: m0 + X G


def test_gordon_v0_no_root_when_r_le_G():
    assert F.gordon_v0(0.2, 0.1, 0.0, 0.1, 0.05, 0.3) is None
    v = F.gordon_v0(0.2, 0.03, 0.0, 0.05, 0.10, 0.3)
    assert v is not None and v > 0


def test_R_max_and_threshold_consistent():
    G = F.ceiling_growth_threshold(0.21, 0.2, 0.025, 0.03)
    assert F.R_max(0.21, 0.2, 0.025, 0.03, 1.0, 0.0, G) == pytest.approx(1.0)


# ---------------- review, detection rate, failure taxonomy ----------------
def test_review_share_detection_reduces_to_core_at_d1():
    e, L, wtR = 0.072, 60.0, 4.32
    assert F.review_share(e, L, wtR, 0.95, 0.0, 1.0) == pytest.approx(F.review_share(e, L, wtR, 0.95, 0.0))
    xi1 = F.review_share(e, L, wtR, 0.95, 0.0, 1.0)
    xi8 = F.review_share(e, L, wtR, 0.95, 0.0, 0.8)
    assert xi8 >= xi1                                          # weaker detection needs more review for the target


def test_quality_cost_limits():
    assert F.quality_cost(0.0, 0.1, 10.0, 1.0) == pytest.approx(1.0)              # no review: e L
    assert F.quality_cost(1.0, 0.1, 10.0, 1.0, d=1.0) == pytest.approx(1.0)       # full review, perfect detection: w tR
    assert F.quality_cost(1.0, 0.1, 10.0, 1.0, d=0.5) == pytest.approx(1.0 + 0.5)


def test_modern_map_running_example():
    """Exception handling at readiness 0.9 (notes/modern_theory_map.md change 1): e = 0.072, epsbar = 0.05, L = $60,
    w tR = $4.32; infeasible below d = 0.31."""
    e, eps_bar = 0.072, 0.05
    assert F.detection_threshold(e, 1 - eps_bar) == pytest.approx(1 - eps_bar / e)
    assert F.detection_threshold(e, 1 - eps_bar) == pytest.approx(0.3056, abs=1e-3)


def test_halluc_taxonomy_floor_example():
    """theory_core prop:tasks-halluc example: 5% ordinary errors caught at 0.95 and 2% hallucinations at 0.5 leave a
    review-proof 1.25%, above a 1% tolerance; grounding to d_h = 0.9 brings it to 0.45%."""
    _, ok, und = F.review_share_tax(0.05, 0.02, 0.95, 0.5, 10.0, 1.0, 0.99, 0.0)
    assert not bool(ok)
    _, ok2, _ = F.review_share_tax(0.05, 0.02, 0.95, 0.9, 10.0, 1.0, 0.99, 0.0)
    assert bool(ok2)
    ebar, etil = F.catchable_rate(0.05, 0.02, 0.95, 0.5)
    assert ebar - etil == pytest.approx(0.0125)


def test_bias_peak_and_irony():
    xs = np.linspace(0.01, 0.999, 3000)
    K, _ = F.caught_errors(xs, 0.02, 0.5, dbar=0.5, e0=1.0)
    assert xs[int(np.argmax(K))] == pytest.approx(math.exp(-0.5), abs=3e-3)
    assert bool(F.irony_flag(0.762, 0.5)) and not bool(F.irony_flag(0.5, 0.5))


def test_emin_pareto_and_cvar():
    assert float(F.emin_pareto(np.inf, 2.0)) == pytest.approx(2.0)
    assert float(F.emin_pareto(10.0, 1.0)) == pytest.approx(1 + math.log(10))
    assert float(F.event_cvar(5000, 1.5, 0.99)) == pytest.approx(323.2e3, rel=1e-3)
    assert float(F.event_cvar(5000, 1.5, 0.99, 50e3)) == pytest.approx(50e3)


def test_optimal_autonomy_example():
    """prop:tasks-autonomy example (invoice approval): approval optimal at $0.57."""
    wt = 45.0 * 0.05
    hum = np.array([np.inf, 0.6 * wt, 0.2 * wt, 0.10])
    Em = float(F.emin_pareto(10.0, 1.5))
    cm = np.array([0.0, 0.0, 1e-4 * 0.1 * 5000 * Em, 2e-4 * 0.7 * 5000 * Em])
    lvl, best = F.optimal_autonomy(hum + cm, np.array([False, True, True, True]))
    assert int(lvl) == 2 and float(best) == pytest.approx(0.568, abs=1e-3)


def test_pipeline_formulas():
    assert int(F.max_pipeline_length(0.01, 0.95)) == 5
    assert int(F.max_pipeline_length(0.01, 0.95, k=5)) == 1
    assert float(F.max_pipeline_length(0.01, 0.95, 1, J_s=3, d_c=0.5)) > 5
    eps, J, Lc = 0.01, 10, 2.0
    assert float(F.cascade_loss(eps, J, Lc)) == pytest.approx(Lc * eps * J * (J + 1) / 2, rel=0.05)
    assert F.pipeline_reliability([0.01] * 5) == pytest.approx(0.99 ** 5)


# ---------------- capability ----------------
def test_chi_forms():
    assert float(F.chi_reliability(0.8, 1.161)) == pytest.approx(5.0, abs=0.05)
    assert float(F.chi_reliability(0.8, 1.161, "constant_hazard")) == pytest.approx(1 / math.log2(1 / 0.8))
    assert float(F.chi_reliability(0.5, 1.161, "constant_hazard")) == pytest.approx(1.0)


def test_plateau_makes_late_feasibility_never():
    tf = F.feasibility_date(2027.0, 2026.1, 0.5671, np.array([1.0, 10.0]), 0.0, np.zeros(2), plateau_year=2028.0)
    assert np.isfinite(tf[0]) and np.isinf(tf[1])


def test_physical_horizon_starts_lagged():
    h_soft = F.capability_horizon(2026.1 - 5.0, 12.0, 2026.1, 0.5671)
    h_phys = F.capability_horizon_physical(2026.1, 12.0, 2026.1, 0.5671, 5.0, 1.667)
    assert float(h_phys) == pytest.approx(float(h_soft))


def test_integration_cost_convex():
    a = float(F.integration_cost(0.4, 0.9, 4, 60e3))
    assert a == pytest.approx(60e3 * 4 * (0.9 / 0.1 - 0.4 / 0.6))
    assert float(F.integration_cost(0.4, 0.9, 4, 60e3, kappa=1.5)) > a


# ---------------- transition, success, pilot ----------------
def test_transition_npv_limits():
    # certain success, no parallel run and an infinite horizon: -F + W/r
    v = F.transition_npv(F=1.0, I=0.0, C_J=0.0, C_par=0.0, T_par=1e-9, varpi=1.0, bbar=1.0, W=1.0, C_str=0.0, L_roll=0.0,
                         T_det=0.25, T_h=math.inf, r=0.1)
    assert v == pytest.approx(-1.0 + 1.0 / 0.1, rel=1e-6)
    # a longer parallel run lowers the value when failure risk is nil
    v1 = F.transition_npv(1.0, 0.0, 0.0, 0.5, 0.1, 1.0, 1.0, 1.0, 0.0, 0.0, 0.25, 10.0, 0.1)
    v2 = F.transition_npv(1.0, 0.0, 0.0, 0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 0.0, 0.25, 10.0, 0.1)
    assert v2 < v1


def test_optimal_parallel_run_zero_when_success_certain():
    assert F.optimal_parallel_run(1.0, 1.0, 0.85, 1.0, 2.0, 2.0, 0.25) == pytest.approx(0.0)
    assert F.optimal_parallel_run(0.1, 0.5, 0.85, 1.0, 5.0, 5.0, 0.25) > 0


def test_payback_formula():
    assert F.payback_years(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0) == pytest.approx(1.0)


def test_pilot_value_reference_identity():
    assert F.pilot_value(0.5, 2.0, -1.0, 0.1, 1.0) == pytest.approx(1.0 - 0.1 - 0.5)


def test_std_normal_loss_limits():
    assert float(F.std_normal_loss(0.0)) == pytest.approx(1 / math.sqrt(2 * math.pi))
    assert float(F.std_normal_loss(8.0)) < 1e-12


# ---------------- Section 18 ----------------
def test_risk_cost_security_spend():
    assert float(F.risk_cost(5.0, 10.0)) == pytest.approx(5.0)                   # below C_s: no spending
    assert float(F.security_spend(5.0, 10.0)) == pytest.approx(0.0)
    assert float(F.risk_cost(100.0, 10.0)) == pytest.approx(10 * (1 + math.log(10)))


def test_build_or_buy_volume_threshold():
    b = F.build_or_buy(500e3, 4, 0.17, 50e3, 1.22, 0.0, 1.0, 0.25, 550e3, 50e3, 1e6, 150e3, 50e3, 10.0)
    assert b["choice"] == "buy"
    b2 = F.build_or_buy(500e3, 4, 0.17, 50e3, 1.22, 0.0, 1.0, 0.25, 550e3, 50e3, 1e6, 150e3, 50e3, 1e9)
    assert b2["choice"] == "build"


def test_review_queue():
    assert math.isinf(float(F.review_latency(5.0, 5.0)))
    assert float(F.review_latency(10.0, 5.0)) == pytest.approx(0.2)
    assert F.optimal_review_capacity(4.0, 1e6, 0.5, 6e4) > 4.0


# ---------------- accounting (theory_accounting) ----------------
def test_psi_15():
    assert F.psi_amortization(0.10, 15) == pytest.approx(0.532, abs=5e-4)
    assert F.tax_psi(0.10, 1.0) == pytest.approx(1.0)
    assert F.tax_psi(0.10, 0.0) == pytest.approx(0.532, abs=5e-4)


def test_asu_capitalized_share_example():
    assert F.capitalized_share_asu(0.4, 1 / 6) == pytest.approx(0.5)


def test_mw_and_cutover():
    assert F.cutover_delay(0.25, 1 / 6) == pytest.approx((0.25 + 1 / 6) ** 2 / 2)
    assert F.mw_probability(0.0, 0.2, 0.2, 0.1, 0.25, 0.25) == pytest.approx(0.04)
    assert F.mw_probability(5.0, 0.2, 0.2, 0.1, 0.25, 0.25) < 1e-6


def test_amin_direct_cost_and_breakevens_follow_paper1(params):
    """Paper 1 round 2 (C1-C3, C6), from its own code (code/paper1_macros.py, notes/amin_r2.json): at $1 billion of revenue
    the direct cost is the KPMG under-$5bn SOX budget plus the accelerated-filer audit fee, 0.30% of revenue (low 0.18%,
    high 0.68%); with the engine's layer types and the design line C_itgc + C_val/T_up = $204,672, the cheapest designs
    are one human over one AI layer ($754,672) at 5% and one over two ($804,672) at 1%; one over one stays admissible at
    5% up to p_cc = 0.00084 and a human miss rate on AI-missed items of 8.4%, and is not admissible at 1% at any p_cc."""
    ac = params.accounting
    dc = F.amin_direct_cost(1e9, ac.audit_fee, ac.sox_program_by_size, ac.audit_fee_per_musd, ac.audit_fee_high)
    assert dc["central"] == pytest.approx(1492375.0 + 1.5e6) and dc["central_share"] == pytest.approx(0.002992375)
    assert dc["low_share"] == pytest.approx(0.001843) and dc["high_share"] == pytest.approx(0.006827646)
    assert ac.C_itgc + ac.C_val / params.security.T_up == pytest.approx(204672.131, abs=0.01)
    d = {e: F.amin_design(1e9, 0.0, True, ac.C_itgc, ac.C_val, params.security.T_up, ac.control_types, 24, e) for e in (0.05, 0.01)}
    assert d[0.05]["design"] == {"human": 1, "ai": 1} and d[0.05]["a_min"] * 1e9 == pytest.approx(754672.131, abs=0.01)
    assert d[0.01]["design"] == {"human": 1, "ai": 2} and d[0.01]["a_min"] * 1e9 == pytest.approx(804672.131, abs=0.01)
    assert d[0.05]["breakeven"]["p_cc"] == pytest.approx(0.0008437187, rel=1e-6)
    P_bar, P_ai = 1 - 0.95 ** (1 / 24), 0.005 + 0.995 * 0.02          # Paper 1 paper1_macros.py: closed form for one over one
    assert d[0.05]["breakeven"]["human_miss"] == pytest.approx((P_bar / P_ai - 0.002) / 0.998, rel=1e-9)   # 8.4%
    assert d[0.01]["breakeven"]["p_cc"] == pytest.approx(0.0001385589, rel=1e-6)
    one_one_at_1 = F.amin_breakevens(ac.control_types, {"human": 1, "ai": 1}, 0.01, 24)
    assert one_one_at_1["p_cc"] is None
    assert d[0.05]["human_only_design"] == {"human": 3, "ai": 0} and d[0.05]["human_only_breakeven"]["p_cc"] == pytest.approx(1.021e-5, rel=1e-3)


def test_amin_design_is_the_constrained_minimum():
    """prop:acct-amin / Part I prop:amin: a_min is the cheapest admissible design; no cheaper design that fails the
    test is chosen however cheap; a tighter threshold never lowers it; better ITGCs (lower AI common mode) never raise
    it; AI layers never raise it; the consequence of a material misstatement is not inside a_min."""
    types = {"human": {"p": 0.05, "p_cm": 0.002, "c": 5e5, "kind": "human"}, "ai": {"p": 0.02, "p_cm": 0.005, "c": 5e4, "ai": True, "kind": "ai"}}
    args = dict(S=1e9, C_acct=1.38e6, C_itgc=5e4, C_val=2.4e4, T_up=1.22, N_o=24)
    for eps in (0.05, 0.01):
        d = F.amin_design(ai=True, types=types, eps_bar=eps, L_mm=1e7, **args)
        assert d["admissible"] and d["annual_miss_probability"] <= eps + 1e-12
        assert d["a_min"] <= d["a_min_human_only"] + 1e-15
        # every cheaper design is inadmissible
        for h in range(4):
            for a in range(4):
                if h + a == 0:
                    continue
                P = (types["human"]["p_cm"] + (1 - types["human"]["p_cm"]) * 0.05 ** h if h else 1.0) * \
                    (types["ai"]["p_cm"] + (1 - types["ai"]["p_cm"]) * 0.02 ** a if a else 1.0)
                cost = args["C_acct"] + h * 5e5 + a * 5e4 + (5e4 + 2.4e4 / 1.22 if a else 0.0)
                if cost < d["a_min"] * 1e9 - 1e-6:
                    assert not F.amin_admissible(P, eps, 24)
        # the material-misstatement consequence is reported, not priced: a_min does not depend on L_mm
        d2 = F.amin_design(ai=True, types=types, eps_bar=eps, L_mm=1e9, **args)
        assert d2["a_min"] == d["a_min"] and d2["design"] == d["design"]
        d0 = F.amin_design(ai=False, types=types, eps_bar=eps, **args)
        assert d0["design"] is None or d0["design"].get("ai", 0) == 0
        assert d["a_min"] <= d0["a_min"]
    d5 = F.amin_design(ai=True, types=types, eps_bar=0.05, **args)
    d1 = F.amin_design(ai=True, types=types, eps_bar=0.01, **args)
    assert d1["a_min"] >= d5["a_min"]
    weak = dict(types, ai=dict(types["ai"], p_cm=0.02))
    assert F.amin_design(ai=True, types=weak, eps_bar=0.01, **args)["a_min"] >= d1["a_min"]
    # a type whose common-mode floor alone exceeds the threshold has no admissible depth (prop:acct-amin(c))
    assert F.amin_min_depth(0.02, 0.005, 0.05, 24) is None and F.amin_min_depth(0.05, 0.002, 0.05, 24) == 3


def test_severance_recognition():
    assert F.severance_recognition(100.0, 1, 3, "asc712") == {1: 100.0}
    r = F.severance_recognition(100.0, 1, 3, "asc420", retention_days=60)
    assert sum(r.values()) == pytest.approx(100.0) and len(r) == 3


# ---------------- PQC, labor ----------------
def test_pqc_path_sums_to_total_and_respects_deadline():
    yrs = 2026.5 + np.arange(12)
    c = F.pqc_cost_path(yrs, 1e7, 0.1, 2026, 2036, 1.0)
    assert c.sum() == pytest.approx(1e6)
    assert c[yrs > 2036].sum() == 0


def test_notice_delay():
    d = F.notice_delay_years(np.array([100.0, 10.0, 50.0]), 60, 50, 30, np.array([0, 0, 1]), 4, np.array([0, 0, 0]), 3,
                             np.array(["US", "US", "EU"]))
    assert d[0] == pytest.approx(60 / 365) and d[1] == 0 and d[2] == pytest.approx(30 / 365 + 4 / 12)


# ---------------- competition game ----------------
@pytest.mark.parametrize("n", [1, 2, 3, 4, 6, 10])
def test_durable_share_linear_cournot(n):
    g = F.game_shares(1.0 / n)
    assert g["dur"] == pytest.approx(2.0 / (n + 1))
    assert g["dur"] == pytest.approx(2 * (1 / n) / (1 + 1 / n))


def test_dominant_strategy_window():
    priv, eq = F.game_gains(0.2, 0.1, 20e6, 4)
    assert priv[0] > priv[-1] > 0
    assert F.dominant_strategy(0.5 * eq, priv[-1], eq)["value_creating_if_all"]
    assert F.dominant_strategy(0.5 * (eq + priv[-1]), priv[-1], eq)["dilemma"]


def test_entry_defensive():
    e = F.entry_defensive(PE_inf=0.85, P0=1.0, c0=0.8, d=0.1, Y=20e6, K=1.0e6)
    assert e["defensive"] == ((0.85 - 1.0 + 0.1) * 20e6 <= 1.0e6 < 0.1 * 20e6)


# ---------------- regimes ----------------
def test_cont_rate():
    assert F.cont_rate(0.22) == pytest.approx(0.1989, abs=1e-4)


def test_K_x_seasoning():
    assert F.K_x(0.2, 4.0, 5.0, 10.0, Tsea=1.0) > F.K_x(0.2, 4.5, 5.0, 10.0, Tsea=1.0)
    assert F.K_x(0.2, 4.5, 5.0, 10.0, Tsea=1.0) == pytest.approx((math.exp(-0.9) - math.exp(-1.0)) / 0.2)


def test_waterfall_regions():
    assert F.waterfall_lp(1.2, 5) == 1.2
    pref = 1.08 ** 5
    assert F.waterfall_lp(pref + 0.01, 5) == pytest.approx(pref)
    assert F.waterfall_lp(4.0, 5) == pytest.approx(1 + 0.8 * 3.0)


def test_fastest_ramp_grows():
    ramp = F.fastest_ramp(lambda n: 1.0 * n, 0.5, 2.0, 20)
    body = ramp[:-1]                                     # the last wave takes whatever is left
    assert ramp[0] == 2 and sum(ramp) == 20 and all(b >= a for a, b in zip(body, body[1:]))
    assert F.ramp_linear(2.0, 0.5, 1.0, 20) == len(ramp) or abs(F.ramp_linear(2.0, 0.5, 1.0, 20) - len(ramp)) <= 1


def test_myopic_weight_and_zeta():
    assert F.myopic_weight(9.0, 0.0, 0.3) == pytest.approx(9 / 1.3)
    z1, z5 = F.zeta_pe(0.2, 5, 14, 0.33, 1.0), F.zeta_pe(0.2, 5, 14, 0.33, 0.5)
    assert z5 > z1 > 0


# ---------------- product ----------------
def test_kappa_monopoly_and_price():
    assert float(F.kappa_monopoly(0.0, 1.0)) == pytest.approx(0.5)
    cp = F.competitive_price(11.11, 0.40, 0.40, 1.13, 1.0)
    assert cp["capped"] and cp["p"] == pytest.approx(1.53, abs=0.01)


def test_bass_and_seat_peak():
    p, q = 0.027, 0.419
    assert float(F.bass_B(0.0, p, q)) == pytest.approx(0.0)
    assert F.bass_tipping(p, q) == pytest.approx(math.log(q / p) / (p + q))
    th, nu = F.nu_peak(0.4, p, q)
    ts = np.linspace(0, 40, 4001)
    assert ts[int(np.argmax(F.nu_seat(ts, 0.4, p, q)))] == pytest.approx(th, abs=0.02)


def test_migration_threshold_example():
    assert F.migration_threshold(0.10, 0.04, 0.15, 0.0, 0.25, 0.75) == pytest.approx(0.0123, abs=5e-5)
    assert F.migration_threshold(0.10, 0.04, 0.08, 0.0, 0.25, 0.80) == pytest.approx(0.0066, abs=5e-5)
    assert F.migration_threshold(0.10, 0.04, 0.5, 0.9, 5.0, 0.1) is None


def test_knapsack_and_sourcing():
    chosen, val, shadow = F.knapsack([482, 272, 99, 108], [25, 12, 15, 30], 60, 15.0)
    assert set(chosen) == {0, 1, 2}
    assert F.sourcing_threshold(1.0, 0.5, 1.0, 4.0) == pytest.approx(6.0)
    assert math.isinf(F.sourcing_threshold(0.5, 1.0, 1.0, 4.0))


def test_margin_crossover_none_below_sub():
    T, g_inf = F.margin_crossover(0.45, 0.0, 0.5, 0.05, 0.3, 0.0, 0.74)
    assert T is None and g_inf < 0.74


def test_dilution():
    d = F.dilution_test(0.03, 0.01, 9.0, 0.0)
    assert d["pays"] and d["break_even_weight"] == pytest.approx(3.0)
    assert not F.dilution_test(0.03, 0.01, 2.5, 0.0)["pays"]
