# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Cross-implementation tests (spec 19.1): the engine's formulas against the theory's reference implementations in
code/verify_part2_{core,ext,product,regimes,accounting,competition,labor}.py, imported by path (functions only), on
random inputs."""
import math

import numpy as np
import pytest

from autofrontier import config
from autofrontier import formulas as F
from conftest import load_reference

N = 200


@pytest.fixture(scope="module")
def core():
    return load_reference("verify_part2_core")


@pytest.fixture(scope="module")
def ext():
    return load_reference("verify_part2_ext")


@pytest.fixture(scope="module")
def prod():
    return load_reference("verify_part2_product")


@pytest.fixture(scope="module")
def regs():
    return load_reference("verify_part2_regimes")


@pytest.fixture(scope="module")
def acct():
    return load_reference("verify_part2_accounting")


@pytest.fixture(scope="module")
def comp():
    return load_reference("verify_part2_competition")


def test_core_review_and_quality_cost(core, rng):
    for _ in range(N):
        e, L, wtR = rng.uniform(0.005, 0.4), rng.uniform(1, 200), rng.uniform(0.1, 20)
        d, epsbar, ximin = rng.uniform(0.3, 1.0), rng.uniform(0.001, 0.2), rng.uniform(0, 0.3)
        xi_r, cq_r, eps_r = core["review"](e, L, wtR, epsbar, ximin, d)
        xi = float(F.review_share(e, L, wtR, 1 - epsbar, ximin, d))
        assert xi == pytest.approx(xi_r, abs=1e-12)
        assert float(F.quality_cost(xi, e, L, wtR, d)) == pytest.approx(cq_r, rel=1e-10)
        assert float(F.residual_error(e, xi, d)) == pytest.approx(eps_r, rel=1e-10, abs=1e-14)


def test_core_crossover_and_normal_loss(core, rng):
    for _ in range(N):
        c0A, nA = rng.uniform(0, 5), rng.uniform(1, 10)
        alts = [(rng.uniform(5, 20), rng.uniform(0, 0.5)) for _ in range(3)]
        eng = min(float(F.crossover_price(c0x, c0A, nx, nA)) for c0x, nx in alts)
        assert eng == pytest.approx(core["crossover_price"](c0A, nA, alts))
        u = rng.uniform(-3, 3)
        assert float(F.std_normal_loss(u)) == pytest.approx(core["std_normal_loss"](u), rel=1e-10)


def test_core_partI_and_gordon(core, rng):
    for _ in range(50):
        m0, G, k, X, ell, al = rng.uniform(0.05, 0.4), rng.uniform(0.0, 0.08), rng.uniform(0, 0.3), rng.uniform(1, 12), \
            rng.uniform(0.02, 0.2), rng.uniform(0.2, 0.45)
        assert float(F.R_star(m0, G, ell, X, k, al)) == pytest.approx(core["partI"](m0, G, k, X, ell, al)[2], rel=1e-10)
        r = G + rng.uniform(0.05, 0.15)
        v = F.gordon_v0(m0, G, k, ell, r, al)
        if v is not None:
            assert v == pytest.approx(core["gordon_root"](r, G, k, m0, ell, al), rel=1e-6)


def test_core_transition_npv(core, rng):
    for _ in range(100):
        P = dict(F=rng.uniform(0.1, 3), I=rng.uniform(0, 2), CJ=rng.uniform(0, 0.5), Cpar=rng.uniform(0, 2), pis=rng.uniform(0.2, 1),
                 bbar=rng.uniform(0.5, 1), W=rng.uniform(0.2, 3), Cstr=rng.uniform(0, 2), Lroll=rng.uniform(0, 3),
                 Tdet=rng.uniform(0.05, 1), Th=rng.uniform(2, 12), r=rng.uniform(0.02, 0.2))
        Tpar = rng.uniform(0.02, 1.0)
        ref = core["transition_npv"](P, Tpar)
        eng = F.transition_npv(P["F"], P["I"], P["CJ"], P["Cpar"], Tpar, P["pis"], P["bbar"], P["W"], P["Cstr"], P["Lroll"],
                               P["Tdet"], P["Th"], P["r"])
        assert eng == pytest.approx(ref, rel=1e-6, abs=1e-9)


def test_core_pilot_and_risk(core, rng):
    for _ in range(N):
        om, Ys, Yf, Fp, d = rng.uniform(0, 1), rng.uniform(0.1, 5), -rng.uniform(0.1, 5), rng.uniform(0, 0.5), rng.uniform(0.8, 1)
        assert F.pilot_value(om, Ys, Yf, Fp, d) == pytest.approx(core["pilot_value"](om, Ys, Yf, Fp, d))
        Ci, Cs = rng.uniform(1e3, 1e6), rng.uniform(1e3, 1e5)
        ref_cost, ref_spend = core["risk_cost"](Ci, Cs)
        assert float(F.risk_cost(Ci, Cs)) == pytest.approx(ref_cost, rel=1e-10)
        assert float(F.security_spend(Ci, Cs)) == pytest.approx(ref_spend, rel=1e-10, abs=1e-9)


def test_core_failure_modes(core, rng):
    for _ in range(N):
        eo, eh, do_, dh = rng.uniform(0.01, 0.2), rng.uniform(0, 0.1), rng.uniform(0.6, 1), rng.uniform(0.2, 0.8)
        xi, L, wtR = rng.uniform(0.01, 1), rng.uniform(5, 100), rng.uniform(0.2, 5)
        assert float(F.quality_cost_tax(xi, eo, eh, do_, dh, L, wtR)) == pytest.approx(core["quality_cost_tax"](xi, eo, eh, do_, dh, L, wtR), rel=1e-10)
        e, eps_d = rng.uniform(0.005, 0.05), rng.uniform(0.1, 2)
        K, dd = F.caught_errors(xi, e, eps_d, dbar=0.5, e0=1.0)
        Kr, dr = core["caught"](xi, e, eps_d, dbar=0.5, p0=1.0)
        assert float(K) == pytest.approx(Kr, rel=1e-10)
        kap, pp = rng.uniform(1.5, 100), rng.uniform(0.5, 3)
        assert float(F.emin_pareto(kap, pp)) == pytest.approx(core["Emin_pareto"](kap, pp), rel=1e-10)


def test_ext_crf_shapley_waves(ext, rng):
    for _ in range(N):
        r, T = rng.uniform(0.001, 0.3), rng.uniform(1, 10)
        assert float(F.capital_recovery_factor(r, T)) == pytest.approx(ext["crf"](r, T), rel=1e-12)
    w = rng.uniform(-1, 1, 4)
    f = lambda S: float(sum(w[i] for i in S) + 0.5 * (0 in S and 1 in S))
    sh_e = F.shapley_values(f, 4)
    sh_r = ext["shapley"](f, 4)
    assert np.allclose(sh_e, sh_r)
    if "wave_cost" in ext:
        for _ in range(50):
            sizes = list(rng.integers(1, 8, 3))
            s, Tp, d1, d2, Ow = rng.uniform(0.5, 2), rng.uniform(0.2, 1), rng.uniform(0, 0.5), rng.uniform(0.05, 0.5), rng.uniform(0, 1)
            assert F.program_cost(sizes, s, Tp, d1, d2, Ow) == pytest.approx(ext["wave_cost"](sizes, s, Tp, d1, d2, Ow), rel=1e-10)


def test_ext_shock_value(ext, rng):
    if "Vshock" not in ext:
        pytest.skip("Vshock not in the reference")
    for _ in range(50):
        nu = rng.uniform(0, 0.5)
        ref = ext["Vshock"](nu)
        eng = F.shock_value(10.0, 4.0, 0.10, nu, 0.5, 3.0, 0.0)
        assert eng == pytest.approx(ref, rel=1e-8)


def test_product_reference(prod, rng):
    for _ in range(N):
        cI, eps = rng.uniform(0, 0.9), rng.uniform(0.3, 3)
        assert float(F.kappa_monopoly(cI, eps)) == pytest.approx(prod["kap_monopoly"](cI, eps))
        assert float(F.C_ad(eps)) == pytest.approx(prod["C_ad"](eps))
        kap = rng.uniform(0, 1)
        assert float(F.adoption_share(kap, eps)) == pytest.approx(prod["adoption"](kap, eps))
        V, chI, chE, rho = rng.uniform(5, 20), rng.uniform(0.1, 2), rng.uniform(0.1, 2), rng.uniform(0, 3)
        ups = rng.uniform(0, 1)
        p_ref, cap_ref, pm_ref = prod["price_competition"](V, chI, chE, rho, eps, ups)
        cp = F.competitive_price(V, chI, chE, rho, eps, ups)
        assert cp["cap"] == pytest.approx(cap_ref)
        if p_ref is not None and cp["viable"]:
            assert cp["p"] == pytest.approx(p_ref)
        t, p, q = rng.uniform(0, 30), rng.uniform(0.01, 0.1), rng.uniform(0.2, 0.9)
        assert float(F.bass_B(t, p, q)) == pytest.approx(float(prod["bass_B"](t, p, q)))
        assert float(F.bass_f(t, p, q)) == pytest.approx(float(prod["bass_f"](t, p, q)))
        xb = rng.uniform(0.1, 0.8)
        assert float(F.nu_seat(t, xb, p, q)) == pytest.approx(float(prod["nu_seat"](t, xb, p, q)))
        if q > p * (1 - xb):
            th, _ = F.nu_peak(xb, p, q)
            Bh = prod["Bhat_peak"](xb, p, q)
            assert float(F.bass_B(th, p, q)) == pytest.approx(Bh, rel=1e-8)
        r, g = rng.uniform(0.05, 0.2), rng.uniform(0, 0.04)
        dl, eh, om, vp = rng.uniform(0, 0.3), rng.uniform(0, 0.6), rng.uniform(0.1, 1), rng.uniform(0.5, 0.95)
        ref = prod["nu_star"](r, g, dl, eh, om, vp)
        eng = F.migration_threshold(r, g, dl, eh, om, vp)
        assert (ref is None and eng is None) or eng == pytest.approx(ref)


def test_product_migration_value(prod, rng):
    for _ in range(10):
        xb, p, q = rng.uniform(0.1, 0.6), 0.027, 0.419
        X = lambda t, xb=xb: xb * F.bass_B(np.maximum(np.asarray(t, float), 0.0), p, q)
        Xs = lambda t, xb=xb: xb * float(F.bass_B(t, p, q))
        T, R0, gam, r, g = rng.uniform(0, 5), 400.0, 0.8, 0.10, 0.04
        dl, eh, om, vp = 0.08, rng.uniform(0, 0.5), 0.25, 0.8
        ref = prod["V_mig"](T, Xs, R0, gam, r, g, dl, eh, om, vp)
        eng = F.migration_value(T, X, R0, gam, r, g, dl, eh, om, vp, horizon=400.0, n=40001)
        assert eng == pytest.approx(ref, rel=2e-3, abs=0.05)


def test_regimes_reference(regs, rng):
    for _ in range(N):
        r, t, T, Mt, Ts = rng.uniform(0.05, 0.35), rng.uniform(0, 5), rng.uniform(3, 8), rng.uniform(0, 20), rng.uniform(0, 1.5)
        assert F.K_x(r, t, T, Mt, Ts) == pytest.approx(regs["K_x"](r, t, T, Mt, Ts))
        assert F.K_gc(r, t) == pytest.approx(regs["K_gc"](r, t))
        M, TT = rng.uniform(0.3, 5), rng.uniform(1, 10)
        assert F.waterfall_lp(M, TT, 0.08, 0.2) == pytest.approx(regs["waterfall_lp"](M, TT, 0.08, 0.2))
    if "zeta_pe" in regs:
        for _ in range(50):
            r, T, M, dK, hx = rng.uniform(0.1, 0.3), rng.uniform(3, 8), rng.uniform(8, 16), rng.uniform(0.1, 0.4), rng.uniform(0, 1)
            assert F.zeta_pe(r, T, M, dK, hx) == pytest.approx(regs["zeta_pe"](r, T, M, dK, hx))


def test_accounting_reference(acct, rng):
    for _ in range(N):
        T, r = int(rng.integers(2, 40)), rng.uniform(0.005, 0.3)
        assert F.psi_amortization(r, T) == pytest.approx(acct["psi_closed"](T, r), rel=1e-12)
        H, pdef, pmw, Tdc, Trem, Top = rng.uniform(0, 2), rng.uniform(0.05, 0.6), rng.uniform(0.05, 0.6), rng.uniform(0.05, 0.5), \
            rng.uniform(0, 0.3), rng.uniform(0, 0.5)
        assert F.mw_probability(H, pdef, pmw, Trem, Top, Tdc) == pytest.approx(acct["Pmw"](H, pdef, pmw, Tdc, Trem, Top))


def test_accounting_amin_probability(acct, rng):
    """prop:acct-amin(a)-(c) against verify_part2_accounting.py Section 5: the design's miss probability with a shared
    cause p0, the admissibility test and the minimal admissible depth of one type."""
    n_checked = 0
    for _ in range(80):
        types = {"a": {"p": rng.uniform(0.01, 0.3), "p_cm": rng.uniform(0, 0.02), "c": rng.uniform(1.0, 5.0)},
                 "b": {"p": rng.uniform(0.01, 0.3), "p_cm": rng.uniform(0, 0.02), "c": rng.uniform(1.0, 5.0)}}
        p0, eps, N = float(rng.uniform(0, 0.002)), float(rng.choice([0.01, 0.05, 0.1])), int(rng.integers(4, 40))
        d = F.amin_design(1e9, 0.0, True, 0.0, 0.0, 1.0, types, N, eps, p_cc=p0, n_max=4)
        for k in ("a", "b"):
            assert d["min_depth"][k] == acct["n_min_type"](p0, types[k]["p_cm"], types[k]["p"], eps, N)
        if not d["admissible"]:
            continue
        n_checked += 1
        ns = d["design"]
        P_ref = acct["P_design"]([(types[k]["p_cm"], types[k]["p"], ns[k]) for k in ("a", "b")], p0)
        assert d["misstatement_probability"] == pytest.approx(P_ref, rel=1e-10)
        assert acct["admissible"](P_ref, eps, N) and d["P_bar"] == pytest.approx(acct["Pbar"](eps, N))
    assert n_checked > 20


def test_competition_reference(comp, rng):
    for _ in range(N):
        n = int(rng.integers(2, 10))
        mg, d, Y = rng.uniform(0.1, 0.4), rng.uniform(0.01, 0.1), rng.uniform(1e6, 1e8)
        B = mg / Y
        E1, E0 = comp["lin_cournot"](n, mg, d, B)
        for k in range(n):
            assert F.cournot_earnings(mg, d, Y, n, k, True) == pytest.approx(E1(k), rel=1e-10)
            assert F.cournot_earnings(mg, d, Y, n, k, False) == pytest.approx(E0(k), rel=1e-10)


# ---------------- labor law, talent and jurisdiction (theory_labor) ----------------
@pytest.fixture(scope="module")
def lab():
    return load_reference("verify_part2_labor")


def test_labor_statutory_calculators(lab, rng):
    """Every statutory calculator of tab:labor-rules against the verify script's L0 calculators."""
    for _ in range(N):
        emp, site, n = float(rng.integers(20, 6000)), float(rng.integers(10, 3000)), float(rng.integers(0, 800))
        years, age = float(rng.uniform(0, 30)), float(rng.integers(18, 66))
        assert F.warn_federal(emp, site, n) == lab["warn_federal"](emp, site, n)
        assert F.warn_federal(emp, site, n, True) == lab["warn_federal"](emp, site, n, True)
        assert F.warn_ca(site, n) == lab["warn_ca"](site, n)
        assert F.warn_ny(emp, site, n) == lab["warn_ny"](emp, site, n)
        assert F.warn_nj(emp, n, years, 60) == lab["warn_nj"](emp, n, years, 60)
        assert F.eu_collective(site, n, n) == lab["eu_collective"](site, n, n)
        assert F.eu_collective(site, n, n, "90day") == lab["eu_collective"](site, n, n, "90day")
        assert F.de_anzeige(site, n) == lab["de_anzeige"](site, n)
        assert F.de_sozialplan_enforceable(site, n) == lab["de_sozialplan_enforceable"](site, n)
        assert F.de_notice_months(years) == pytest.approx(lab["de_notice_months"](years))
        assert F.de_1a_months(years) == pytest.approx(lab["de_1a_months"](years))
        assert F.fr_pse_required(emp, n) == lab["fr_pse_required"](emp, n)
        assert F.fr_cse_months(n) == lab["fr_cse_months"](n)
        assert F.fr_notice_months(years) == lab["fr_notice_months"](years)
        assert F.fr_indemnity_months(years) == pytest.approx(lab["fr_indemnity_months"](years))
        assert F.uk_collective(n) == lab["uk_collective"](n)
        assert F.uk_srp_weeks(age, years) == pytest.approx(lab["uk_srp_weeks"](age, years))
        assert F.in_retrenchment(years) == pytest.approx(lab["in_retrenchment"](years))


def test_labor_example_leads():
    """Example leads for 150 dismissals at 5 years of tenure (labor notes 3.1, verify L0g)."""
    de = F.statutory_terms("DE", site_headcount=1000, employer_headcount=1000, n_dis=150, tenure=5, works_council=True)
    fr = F.statutory_terms("FR", site_headcount=1000, employer_headcount=1000, n_dis=150, tenure=5)
    uk = F.statutory_terms("UK", site_headcount=1000, employer_headcount=1000, n_dis=150, tenure=5, age=35)
    us = F.statutory_terms("US", site_headcount=300, employer_headcount=1000, n_dis=150, tenure=5)
    ny = F.statutory_terms("US", "NY", site_headcount=300, employer_headcount=1000, n_dis=150, tenure=5)
    ind = F.statutory_terms("IN", site_headcount=300, employer_headcount=1000, n_dis=150, tenure=5)
    assert de["T_leg"] == pytest.approx(0.41667, abs=1e-4) and fr["T_leg"] == pytest.approx(0.47420, abs=1e-4)
    assert uk["T_leg"] == pytest.approx(0.1233, abs=1e-4) and us["T_leg"] == pytest.approx(0.1644, abs=1e-4)
    assert ny["T_leg"] == pytest.approx(0.2466, abs=1e-4) and ind["T_leg"] == pytest.approx(1 / 12)
    # floors at 5 years: UK 1.15, DE 2.5, FR 1.25, IN 3.0 (compensation plus fund), US 0
    assert uk["floor_months"] == pytest.approx(1.154, abs=1e-3) and de["floor_months"] == 2.5
    assert fr["floor_months"] == 1.25 and ind["floor_months"] == 3.0 and us["floor_months"] == 0.0


def test_labor_lead_rules(lab, rng):
    """Procedure start (prop:labor-lead(d)), free parallel run (e), pacing span (c) and streams (b) against the
    verify script."""
    for _ in range(N):
        G, Tl = float(rng.uniform(0.05, 1.5)), float(rng.uniform(0.02, 1.2))
        om, W, cann, Cwd = float(rng.uniform(0.05, 0.99)), float(rng.uniform(0.01, 5)), float(rng.uniform(0, 2)), float(rng.uniform(0, 2))
        assert F.procedure_start(G, Tl, om, W, cann, Cwd) == pytest.approx(lab["ann_rule"](G, Tl, om, W, cann, Cwd))
        for tA in (0.0, G / 2, G):
            assert F.announcement_cost(tA, G, Tl, om, W, cann, Cwd) == pytest.approx(lab["ann_cost"](tA, G, Tl, om, W, cann, Cwd))
        chat, chat1 = float(rng.uniform(0.1, 2)), float(rng.uniform(0.01, 2))
        chat1 = min(chat1, chat)
        R, Td, D0 = float(rng.uniform(0.01, 5)), float(rng.uniform(0.05, 1)), float(rng.uniform(0, 2))
        Ts, Tss = lab["Tstar"](chat, R, Td), lab["Tstar"](chat1, R, Td)
        ref = min(Tss, max(D0, Ts))
        # engine form: c_hat = C_par + varpi b W (1 - rho), R = (1 - varpi)(C_str + L_roll); choose C_par = chat, varpi b W = 0
        mine = float(F.free_parallel_run(D0, chat, 0.0, 0.0, 0.0, R, 0.0, Td, chat1))
        assert mine == pytest.approx(ref, rel=1e-9, abs=1e-12)
    assert F.min_pacing_span(200, 20, 90) == lab["min_span"](200, 20, 90) == 900
    for _ in range(100):
        n = int(rng.integers(2, 6))
        tD, Wv, Ow = rng.uniform(0.3, 1.5, n), rng.uniform(0.1, 3, n), float(rng.uniform(0, 1))
        groups, cost = F.stream_partition(tD, Wv, Ow)
        best = min(lab["part_cost"](g, tD, Wv, Ow) for g in lab["partitions"](list(range(n))))
        assert cost == pytest.approx(best, rel=1e-9, abs=1e-12)
        assert lab["part_cost"](groups, tD, Wv, Ow) == pytest.approx(cost, rel=1e-9, abs=1e-12)


def test_labor_survivor_talent_location(lab, rng):
    """Survivor factor, capacity path, hiring capacity, hire or contract and the location lag (verify L2 to L4)."""
    for _ in range(N):
        nK, kd, kr, nx, ta = int(rng.integers(1, 8)), float(rng.uniform(0, 1)), float(rng.uniform(0, 1)), float(rng.uniform(0, 3)), float(rng.uniform(0, 2))
        assert float(F.knowledge_holder_factor(nK, kd, kr, nx, ta)) == pytest.approx(lab["succ_exact"](nK, kd, kr, nx, ta))
        Gam, eb, em = float(rng.uniform(1, 50)), float(rng.uniform(0.2, 5)), float(rng.uniform(0.02, 1))
        t = float(rng.uniform(0, 10))
        assert float(F.processes_in_scope(t, Gam, eb, em)) == pytest.approx(lab["N_of_t"](t, Gam, eb, em))
        Nn = float(rng.uniform(0, 1.2)) * Gam / em
        assert F.time_to_scope(Nn, Gam, eb, em) == pytest.approx(lab["T_of_N"](Nn, Gam, eb, em)) if Nn > 0 else True
        h, Tl, drp, Trp = float(rng.uniform(1, 30)), float(rng.uniform(0, 1)), float(rng.uniform(0, 0.5)), float(rng.uniform(0.1, 3))
        T = Tl + float(rng.uniform(0.1, 5))
        assert F.hiring_capacity(T, h, Tl, drp, Trp) == pytest.approx(lab["cum_capacity"](T, h, Tl, drp, Trp))
        dG, w, ch, What = float(rng.uniform(1, 20)), float(rng.uniform(0.1, 0.3)), float(rng.uniform(0.1, 0.5)), float(rng.uniform(0, 5))
        Tc, uct = float(rng.uniform(0, 0.1)), float(rng.uniform(0.1, 1.5))
        thr = F.contract_threshold(drp, Trp, ch, What, Tl, Tc, dG, w, uct)
        for Tn in (Trp + 0.01, Trp + 1, Trp + 5):
            better = lab["K_contract"](dG, w, Tn, uct, What, Tc) < lab["K_hire"](dG, w, Tn, drp, Trp, ch, What, Tl)
            if abs(Tn - thr) > 1e-9:
                assert better == (Tn < thr)
    # examples: w^AI $194,649; 12 processes with 6 engineers at e_mnt 0.25 take 4.16 years; India lag 1.97 at fivefold
    assert float(F.ai_engineer_wage(135980, 0.11, 0.2896)) == pytest.approx(194649, abs=1)
    assert F.time_to_scope(12, 6, 1.5, 0.25) == pytest.approx(4.159, abs=1e-3)
    assert F.time_to_scope(12, 6, 1.5, 0.48) == pytest.approx(10.06, abs=0.01)
    assert float(F.location_adoption_lag(1.0, 0.0, 2959 / 70627, math.log(5))) == pytest.approx(1.971, abs=1e-3)
    assert math.isinf(float(F.location_adoption_lag(1.0, 0.5, 0.4, 1.0)))
    b, bind = F.pace_bound(12, 40, 320, 1, 0.75, 1 + 0.125 / 2 - math.sqrt(0.125 + 0.125 ** 2 / 4), 10, F.time_to_scope(12, 6, 1.5, 0.25))
    assert bind == "engineering talent" and b["change capacity"] == pytest.approx(1.5) and b["decision bandwidth"] == pytest.approx(1.279, abs=2e-3)


def test_core_bias_threshold_and_pipeline_decomposition(rng):
    """prop:tasks-bias(d) against a grid search of the caught-error curve, and prop:tasks-pipeline(d)
    (verify_part2_core 22s, 22t)."""
    bad = 0
    for _ in range(200):
        e, eps_d = float(rng.uniform(0.01, 0.3)), float(rng.uniform(0.05, 1.5))
        d0, p0 = float(rng.uniform(0.2, 0.9)), float(rng.uniform(0.3, 3)) * e
        epsb = float(rng.uniform(0.1, 0.9)) * e
        grid = np.linspace(1e-4, 1, 20001)
        prev = e * (1 + np.log(1 / grid))
        dd = d0 * (prev / p0) ** eps_d
        if np.any(dd > 1):
            continue
        K = e * grid * (1 + np.log(1 / grid)) * dd
        feas_grid = bool(np.any(e - K <= epsb + 1e-12))
        if feas_grid != bool(F.bias_target_attainable(d0, e, eps_d, epsb, p0)):
            bad += 1
    assert bad == 0
    assert math.exp(0.5) / 1.5 == pytest.approx(1.0991, abs=1e-4)
    for _ in range(100):
        D, H = float(rng.uniform(0.1, 20)), float(rng.uniform(0.5, 20))
        parts = rng.dirichlet(np.ones(int(rng.integers(2, 8)))) * D
        assert F.pipeline_success_decomposed(parts, H, "constant_hazard") == pytest.approx(2.0 ** (-D / H))
        eta = float(rng.uniform(1.0, 1.4))
        s = [F.pipeline_success_decomposed(np.full(J, D / J), H, "logistic", eta) for J in range(1, 10)]
        assert all(b < a for a, b in zip(s, s[1:]))


def test_accounting_itgc_lines_and_timeliness(acct, rng):
    """eq:acct-itgc, eq:acct-pvup, prop:acct-itgc(b) (a_min with per-application lines) and (d) (timeliness, nu*)
    against verify_part2_accounting.py Section 6."""
    for _ in range(N):
        args = (int(rng.integers(1, 5)), int(rng.integers(1, 15)), float(rng.uniform(1e3, 5e3)), int(rng.integers(1, 30)),
                float(rng.uniform(1e3, 1e4)), float(rng.uniform(3e4, 2e5)), float(rng.uniform(0.5, 3)), float(rng.uniform(1e4, 6e4)),
                int(rng.integers(0, 6)), float(rng.uniform(5e3, 3e4)))
        assert F.itgc_line(*args) == pytest.approx(acct["itgc_line"](*args))
        Cv, r, Tp, Tu, Th = float(rng.uniform(1e4, 2e5)), float(rng.uniform(0.01, 0.2)), float(rng.uniform(0, 1)), float(rng.uniform(0.3, 3)), float(rng.uniform(2, 10))
        a, b = F.pv_upgrade_retests(Cv, r, Tp, Tu, Th), acct["pv_up"](Cv, r, Tp, Tu, Th)
        assert a[1] == b[1] and a[0] == pytest.approx(b[0])
        t = dict(n_cl=int(rng.integers(1, 13)), nu=float(rng.uniform(1, 30)), Tcw=float(rng.uniform(0.01, 0.05)), D=float(rng.uniform(0.1, 2.0)),
                 Tsl=float(rng.uniform(0.5, 4.0)), c_del=float(rng.uniform(1e4, 1e5)), L_late=float(rng.uniform(1e5, 5e6)),
                 C_fb=float(rng.uniform(1e4, 2e5)), c_fb=float(rng.uniform(1e4, 1e5)), t_sw=float(rng.uniform(0.0, 0.5)))
        assert F.tml_wait(t["n_cl"], t["nu"], t["Tcw"], t["D"], t["Tsl"], t["c_del"], t["L_late"]) == pytest.approx(
            acct["K_wait"](t["n_cl"], t["nu"], t["Tcw"], t["D"], t["Tsl"], t["c_del"], t["L_late"]))
        assert F.tml_fallback(t["n_cl"], t["nu"], t["Tcw"], t["D"], t["c_del"], t["C_fb"], t["c_fb"], t["t_sw"]) == pytest.approx(
            acct["K_fb"](t["n_cl"], t["nu"], t["Tcw"], t["D"], t["c_del"], t["C_fb"], t["c_fb"], t["t_sw"]))
        ns, Dl = F.fallback_threshold(t["n_cl"], t["Tcw"], t["D"], t["Tsl"], t["c_del"], t["L_late"], t["C_fb"], t["c_fb"], t["t_sw"])
        ns2, Dl2 = acct["nu_star"](t["n_cl"], t["Tcw"], t["D"], t["Tsl"], t["c_del"], t["L_late"], t["C_fb"], t["c_fb"], t["t_sw"])
        assert Dl == pytest.approx(Dl2) and (ns == pytest.approx(ns2) if math.isfinite(ns2) else math.isinf(ns))
    # timeliness example (6i): 6-hour incidents $25k and nu* 155; day-long $616k, fallback $161k, nu* 2.2
    T = acct["TML"]
    for D, w, f, ns in ((0.25, 25.3e3, None, 155.4), (1.0, 615.7e3, 161.3e3, 2.16)):
        res = F.timeliness_cost(T["n_cl"], T["nu"], T["Tcw"], D, T["Tsl"], T["c_del"], T["L_late"], T["C_fb"], T["c_fb"], T["t_sw"])
        assert res["wait"] == pytest.approx(w, abs=500) and res["nu_star"] == pytest.approx(ns, abs=0.5 if ns > 10 else 0.01)
        if f is not None:
            assert res["fallback"] == pytest.approx(f, abs=500) and res["fallback_pays"] and res["C_tml"] == pytest.approx(f, abs=500)
        else:
            assert not res["fallback_pays"] and res["C_tml"] == pytest.approx(w, abs=500)
    # the ITGC line with the upgrade retest at KPMG test effort (P2 check 6c1, engine change E3): C_val = 10 controls x 16 h x $150
    pd_ = config.load_params()
    U_ = acct["UNIT"]
    assert (U_["c_acc"], U_["c_chg"], U_["c_ifc"]) == (pd_.accounting.itgc_c_acc, pd_.accounting.itgc_c_chg, pd_.accounting.itgc_c_ifc)
    assert acct["C_VAL_KPMG"] == pytest.approx(24000) and pd_.accounting.C_val == pytest.approx(acct["C_VAL_KPMG"])
    c_inv = sum(F.itgc_line(3, 12, U_["c_acc"], 24, U_["c_chg"], pd_.accounting.C_val, 1.22, 55e3, 4, U_["c_ifc"]).values())
    c_ref = sum(F.itgc_line(1, 4, U_["c_acc"], 6, U_["c_chg"], pd_.accounting.C_val, 1.22, 20e3, 1, U_["c_ifc"]).values())
    assert c_inv == pytest.approx(204672, abs=50) and c_ref == pytest.approx(74672, abs=50)        # verify 6c (KPMG units)
    # a_min as the cheapest admissible design (prop:acct-amin, 5i and 6d): the example's types, the invoice application's
    # line for the AI layers; at a remote threshold of 5% one human over one AI layer, at 1% one over two
    E_ = acct["EXA"]
    types = {"human": {"p": E_["p_hu"], "p_cm": E_["cm_hu"], "c": E_["c_hu"], "kind": "human"},
             "ai": {"p": E_["p_ai"], "p_cm": E_["cm_ai"], "c": E_["c_ai"], "ai": True, "kind": "ai"}}
    want = {(0.05, False): ((1, 1), 0.755e6), (0.01, False): ((1, 2), 0.805e6), (0.01, True): ((1, 2), 1.009e6)}
    for (eps, sep), (design, cost) in want.items():
        d = F.amin_design(E_["S"], 0.0, True, c_inv, 0.0, 1.0, types, E_["N"], eps, L_mm=E_["L"], separate=sep)
        ref = acct["best_admissible"](eps, line=c_inv, separate=sep)
        assert (d["design"]["human"], d["design"]["ai"]) == design == ref[0]
        assert d["a_min"] * E_["S"] == pytest.approx(ref[1], rel=1e-9) and d["a_min"] * E_["S"] == pytest.approx(cost, abs=0.005e6)
        assert d["misstatement_probability"] == pytest.approx(ref[2], rel=1e-12)
        assert d["residual_expected_consequence"] == pytest.approx(E_["N"] * E_["L"] * ref[2])     # reported, not in a_min
    # all-AI on one provider is never admissible (floor 11.3% a year); human-only only at 5% (three layers, $1.50M)
    for eps in (0.05, 0.01):
        d = F.amin_design(E_["S"], 0.0, True, c_inv, 0.0, 1.0, types, E_["N"], eps, L_mm=E_["L"])
        assert d["type_floors"]["ai"] == pytest.approx(0.1133, abs=5e-4) and d["min_depth"]["ai"] is None
        ref_ai = acct["best_admissible"](eps, line=c_inv, cond=lambda h, a: h == 0)
        assert ref_ai[0] is None
        ref_h = acct["best_admissible"](eps, line=c_inv, cond=lambda h, a: a == 0)
        assert (d["human_only_design"] and (d["human_only_design"]["human"], d["human_only_design"]["ai"])) == (ref_h[0] or None)
        if eps == 0.05:
            assert d["a_min_human_only"] * E_["S"] == pytest.approx(1.5e6)
        else:
            assert math.isinf(d["a_min_human_only"]) and not d["human_only_admissible"]
        # the cost-plus-consequence optimum (one human and two AI layers, $872k) is admissible only by coincidence (f)
        assert (d["cost_plus_consequence"]["design"]["human"], d["cost_plus_consequence"]["design"]["ai"]) == (1, 2)
        assert d["cost_plus_consequence"]["cost"] == pytest.approx(0.872e6, abs=0.005e6)
    # weak ITGCs (AI common mode 0.02): at 1% the cheapest admissible design is two human and one AI layer (5j)
    weak = dict(types, ai=dict(types["ai"], p_cm=0.02))
    d = F.amin_design(E_["S"], 0.0, True, c_inv, 0.0, 1.0, weak, E_["N"], 0.01)
    ref = acct["best_admissible"](0.01, e=dict(E_, cm_ai=0.02), line=c_inv)
    assert (d["design"]["human"], d["design"]["ai"]) == ref[0] == (2, 1) and d["a_min"] * E_["S"] == pytest.approx(ref[1])
    # the plan's application lines and C^tml add to a_min one for one, whatever the design
    base = F.amin_design(E_["S"], 0.0, True, c_inv, 0.0, 1.0, types, E_["N"], 0.05)
    more = F.amin_design(E_["S"], 0.0, True, c_inv, 0.0, 1.0, types, E_["N"], 0.05, itgc_lines=[c_inv, c_ref], C_tml=161.3e3)
    assert more["design"] == base["design"]
    assert (more["a_min"] - base["a_min"]) * E_["S"] == pytest.approx(c_inv + c_ref + 161.3e3)
