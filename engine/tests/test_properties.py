# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Property tests (spec 19.1): comparative statics the theory proves, checked on the engine's formulas and on the
synthetic firm."""
import itertools
import math

import numpy as np
import pytest

from autofrontier import economics as E
from autofrontier import formulas as F
from autofrontier import optimize as O
from autofrontier import plans, regimes


def _a_share(econ, y=2):
    ct = econ.ct[:, -1, y, :]
    x = econ.firm.units.base_cost.values
    return float(np.sum(x * (np.argmin(ct, 1) == F.A)) / x.sum())


def test_cheaper_inference_raises_automation_share(built, params):
    firm = built["firm"]
    q = params.copy()
    q.set("prices.pi_h0", params.prices.pi_h0 * 10, origin="test")
    hi = _a_share(E.build_econ(firm, q, horizon=4))
    lo = _a_share(E.build_econ(firm, params, horizon=4))
    assert lo >= hi


def test_all_or_nothing_under_strong_complementarity():
    """A chain whose steps lose money one by one but gain together (strong handoff premia and released overhead):
    the best set is all steps (prop:tasks-aon)."""
    J = 5
    u = np.full(J, -1.0)
    edges = [(i, i + 1) for i in range(J - 1)]
    best, best_v = None, -np.inf
    for m in itertools.product([0, 1], repeat=J):
        Z = np.array(m, bool)
        ne = len(edges)
        v = F.process_value(Z, u, edges, eMM=np.full(ne, 3.0), eAM=np.full(ne, 4.0), eMA=np.full(ne, 4.0), eAA=np.zeros(ne),
                            qM=np.full(J, 0.99), qA=np.full(J, 0.99), vL=0.0, Xi=5.0, crit=np.ones(J, bool))
        if v > best_v:
            best, best_v = Z, v
    assert best.all() or not best.any()
    assert best.all()


def test_long_parallel_run_delays_adoption():
    W, Cpar, b, Fv = 1.0, 0.5, 1.0, 1.0
    short = F.score_path_flows(W, Cpar, 0.2, b, Fv, 0.0, 0.0, 0.0, 0.0, 4.0, 10.0, 3, "cash")
    long_ = F.score_path_flows(W, Cpar, 1.5, b, Fv, 0.0, 0.0, 0.0, 0.0, 4.0, 10.0, 3, "cash")
    assert np.cumsum(long_)[1] < np.cumsum(short)[1]


def test_long_parallel_run_delays_adoption_program(built, params):
    econ = built["econ"]
    q = params.copy()
    q.set("transition.policy", "fixed", origin="test")
    q.set("transition.T_par_default", 0.1, origin="test")
    q.set("transition.T_par_min", 0.04, origin="test")
    e1 = E.build_econ(econ.firm, q)
    c1 = plans.PlanBuilder(e1).build(processes=range(20), pilots=(0,))
    q2 = q.copy()
    q2.set("transition.T_par_default", 1.5, origin="test")
    q2.set("transition.T_par_min", 1.5, origin="test")
    q2.set("transition.T_par_min_regulated", 1.5, origin="test")
    e2 = E.build_econ(econ.firm, q2)
    c2 = plans.PlanBuilder(e2).build(processes=range(20), pilots=(0,))
    # same process, start and readiness: realized savings in the first two years are lower with the long run
    k1 = {(int(c1.proc[i]), int(c1.level[i]), int(c1.start[i]), str(c1.variant[i])): i for i in range(len(c1))}
    worse = 0
    total = 0
    for j in range(len(c2)):
        key = (int(c2.proc[j]), int(c2.level[j]), int(c2.start[j]), str(c2.variant[j]))
        if key in k1 and int(c2.start[j]) == 0:
            total += 1
            worse += c2.sav_cash[j][:2].sum() <= c1.sav_cash[k1[key]][:2].sum() + 1e-6
    assert total > 0 and worse == total


def test_concurrency_beyond_bandwidth_lowers_value():
    x = np.linspace(0.2, 1.5, 50)
    Q = F.Q_bandwidth(x, 1.0, 0.2, 0.5)
    assert np.all(np.diff(Q) <= 1e-12)


def test_concurrency_program_value_falls_with_less_bandwidth(built, params):
    econ, cols, reg = built["econ"], built["cols"], built["regime"]
    prog = O.make_program(cols, econ, reg, params)
    q = params.copy()
    q.set("decisions.Phi_base", params.decisions.Phi_base * 0.25, origin="test")
    firm = econ.firm
    org = dict(firm.org)
    firm.org.pop("decisions_per_year", None)
    try:
        prog_a = O.make_program(cols, econ, reg, params)
        prog_b = O.make_program(cols, econ, reg, q)
        va = O.solve(prog_a, method="heuristic", fixed_point=1).value
        vb = O.solve(prog_b, method="heuristic", fixed_point=1).value
    finally:
        firm.org.clear()
        firm.org.update(org)
    assert vb <= va + 1e-6 * abs(va)


def test_shorter_hold_speeds_cost_outs(built, params):
    econ, cols, firm = built["econ"], built["cols"], built["firm"]
    def mean_start(hold):
        q = params.copy()
        q.set("regime.pe_hold", hold, origin="test")
        r = regimes.make_regime("pe", q, firm)
        pg = O.make_program(cols, econ, r, q)
        so = O.solve(pg, method="heuristic", fixed_point=1)
        st = [cols.start[c] for c in so.sel.values()]
        return float(np.mean(st)) if st else 0.0
    assert mean_start(3.0) <= mean_start(7.0) + 1e-9


def test_tighter_covenant_needs_more_waves():
    D = lambda n: 2.0 * n
    w_loose = F.fastest_ramp(D, 0.5, 10.0, 30)
    w_tight = F.fastest_ramp(D, 0.5, 4.0, 30)
    assert len(w_tight) >= len(w_loose)
    assert F.ramp_linear(4.0, 0.5, 2.0, 30) >= F.ramp_linear(10.0, 0.5, 2.0, 30)


def test_seat_exposure_raises_revenue_at_risk():
    a = F.revenue_at_risk(400e6, 1.0, 0.2)
    b = F.revenue_at_risk(400e6, 1.0, 0.5)
    assert b > a
    p, q = 0.027, 0.419
    assert float(F.nu_seat(3.0, 0.5, p, q)) > float(F.nu_seat(3.0, 0.2, p, q))


def test_higher_exposure_raises_incident_cost():
    o1 = F.exposure_score(0.3, 0.5, 0.2, 0.1)
    o2 = F.exposure_score(0.9, 0.5, 0.2, 0.1)
    assert o2 > o1
    assert float(F.incident_cost(o2, 0.05, 1e-7, 1e5, 1e6)) > float(F.incident_cost(o1, 0.05, 1e-7, 1e5, 1e6))


def test_maintenance_shifts_toward_buy():
    lo = F.build_or_buy(500e3, 4, 0.10, 50e3, 1.22, 0.0, 1.0, 0.25, 550e3, 50e3, 1e6, 150e3, 50e3, 2e5)
    hi = F.build_or_buy(500e3, 4, 0.40, 50e3, 1.22, 0.0, 1.0, 0.25, 550e3, 50e3, 1e6, 150e3, 50e3, 2e5)
    assert hi["v_BB"] > lo["v_BB"]


# ---------------- Section 23 ----------------
def test_higher_autonomy_raises_tail_loss():
    m2 = F.misbehavior_rate(1e-3, 0.5, 2.0, 0.5, 0.2, 1.0, 0.5)
    m3 = F.misbehavior_rate(1e-3, 1.0, 2.0, 0.5, 0.2, 1.0, 0.5)
    v = 1e5
    t2 = float(F.cvar_compound_pareto(m2 * v * 0.3, 1.5, 1e4, 0.95, 2e5))
    t3 = float(F.cvar_compound_pareto(m3 * v * 0.3, 1.5, 1e4, 0.95, 2e5))
    assert m3 > m2 and t3 >= t2
    assert float(F.misbehavior_cost(m3, 0.3, 1e4, 2e5, 1.5)) > float(F.misbehavior_cost(m2, 0.3, 1e4, 2e5, 1.5))


def test_automation_bias_extra_review_less_effective():
    eps_d = 0.5
    K_peak, _ = F.caught_errors(math.exp(-eps_d), 0.02, eps_d, dbar=0.5, e0=1.0)
    K_more, _ = F.caught_errors(0.95, 0.02, eps_d, dbar=0.5, e0=1.0)
    assert float(K_more) < float(K_peak)


def test_pipeline_reliability_falls_with_length():
    rel = [F.pipeline_reliability([0.02] * J) for J in range(1, 12)]
    assert all(b < a for a, b in zip(rel, rel[1:]))
    assert float(F.cascade_loss(0.02, 10, 1.0)) > float(F.cascade_loss(0.02, 5, 1.0))


def test_provider_concentration_widens_loss_distribution():
    loss = np.full(10, 1.0)
    one = F.common_mode_loss_variance(2.0, loss, np.zeros(10, int))
    two = F.common_mode_loss_variance(2.0, loss, np.arange(10) % 2)
    assert one > two


def test_detection_below_threshold_not_automatable(built, params):
    econ = built["econ"]
    rel = econ.info["reliability"]
    if rel is None:
        pytest.skip("failure taxonomy off")
    # where the review floor makes A infeasible, A is not technically feasible
    bad = ~rel["review_feasible"] & econ.info["capA"]
    assert not np.any(econ.tech[:, :, :, F.A][bad])


def test_class_d_parameters_have_ranges(params):
    keys = params.scenario_parameters(("d",))
    assert len(keys) > 100
    for k in keys:
        lo, hi = params.range(k)
        assert lo < hi
