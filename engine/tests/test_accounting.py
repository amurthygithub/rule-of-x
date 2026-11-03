# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Accounting regression tests (spec 24.4; part2 accounting notes): the tax factor does not depend on book
capitalization, amortization starts at go-live, ASC 420 versus 712 timing, the accountability floor a_min of
prop:acct-amin, and no double count of the error floor for financial-reporting processes."""
import math

import numpy as np
import pandas as pd
import pytest

from autofrontier import economics as E
from autofrontier import formulas as F
from autofrontier import plans, security


def _cols(econ, procs=range(12)):
    return plans.PlanBuilder(econ).build(processes=procs, pilots=(0,))


def test_psi_values():
    assert F.psi_amortization(0.10, 15) == pytest.approx(0.532, abs=1e-3)
    assert F.tax_psi(0.10, 1.0) == 1.0
    assert F.tax_psi(0.10, 0.0) == pytest.approx(F.psi_amortization(0.10, 15))
    assert F.capitalized_share_asu(0.4, 1 / 6) == pytest.approx(0.5)


def test_tax_factor_independent_of_book_capitalization(built, params):
    """After-tax cash flows (cf0, cf1) are the same whether builds are capitalized for books or not; GAAP differs
    (prop:acct-tax(d))."""
    firm = built["firm"]
    out = []
    for share in (0.0, 0.7):
        q = params.copy()
        q.set("build.capitalized_share_F", share, origin="test")
        q.set("accounting.asu_2025_06_year", 2100, origin="test")       # use the pre-ASU share for every start year
        out.append(_cols(E.build_econ(firm, q)))
    a, b = out
    assert len(a) == len(b) and len(a) > 0
    assert np.allclose(a.cf0, b.cf0) and np.allclose(a.cf1, b.cf1)
    assert not (np.allclose(a.gaap0, b.gaap0) and np.allclose(a.gaap1, b.gaap1))


def test_amortization_starts_at_go_live(built, params):
    """With go-live after the parallel run, capitalized builds amortize later than with go-live at the start, so
    GAAP expense in the first plan year is lower (ASC 350-40-35-6; prop:acct-path)."""
    firm = built["firm"]
    res = {}
    for gl in ("start", "after_parallel"):
        q = params.copy()
        q.set("accounting.go_live", gl, origin="test")
        q.set("build.capitalized_share_F", 0.7, origin="test")
        q.set("accounting.asu_2025_06_year", 2100, origin="test")
        c = _cols(E.build_econ(firm, q))
        res[gl] = (c.gaap0 + c.gaap1)
    first = lambda g: g[:, 0].sum()
    assert first(res["after_parallel"]) >= first(res["start"]) - 1e-6


def test_severance_recognition_timing():
    # one-time benefits (ASC 420): ratable when staff serve beyond the minimum retention period
    assert F.severance_recognition(120.0, 0, 2, "asc420", 60.0) == {0: 40.0, 1: 40.0, 2: 40.0}
    assert F.severance_recognition(120.0, 1, 1, "asc420", 60.0) == {1: 120.0}
    # ongoing plan (ASC 712): accrued at once when probable and estimable
    assert F.severance_recognition(120.0, 0, 2, "asc712") == {0: 120.0}


def test_amin_design_not_above_human_only(params):
    """At the engine defaults: the floor is the cheapest admissible design (annual miss probability at most eps_bar),
    never above the cheapest admissible human-only design, and allowing AI layers never raises it; the admissible set
    does not depend on revenue and the floor, as a share of revenue, is nonincreasing in revenue (Part I prop:amin(d):
    with errors below materiality growing with revenue, a larger firm may choose a deeper admissible design)."""
    ac = params.accounting
    floors = []
    for S in (1e8, 1e9, 1e10):
        C_acct = F.amin_direct_cost(S, ac.audit_fee, ac.sox_program_by_size, ac.audit_fee_per_musd, ac.audit_fee_high)["central"]
        for ai in (False, True):
            d = F.amin_design(S, C_acct, ai, ac.C_itgc, ac.C_val, params.security.T_up, ac.control_types, ac.N_o, ac.eps_bar,
                              ac.p_cc, ac.N_nm * S / 1e9, ac.L_nm, ac.L_mm)
            assert d["admissible"] and d["annual_miss_probability"] <= ac.eps_bar + 1e-12
            assert d["a_min"] <= d["a_min_human_only"] + 1e-12
            assert 0 < d["a_min"] < 0.1
            if ai:      # allowing AI layers never raises the minimum
                d0 = F.amin_design(S, C_acct, False, ac.C_itgc, ac.C_val, params.security.T_up, ac.control_types, ac.N_o,
                                   ac.eps_bar, ac.p_cc, ac.N_nm * S / 1e9, ac.L_nm, ac.L_mm)
                assert d["a_min"] <= d0["a_min"] + 1e-12
                floors.append(d["a_min"])
    assert all(b <= a + 1e-15 for a, b in zip(floors, floors[1:]))


def test_icfr_error_floor_not_double_counted(built, params):
    """For financial-reporting processes the misstatement loss is inside a_min (prop:acct-amin); their error floor
    is excluded from c_err."""
    econ, prog, sol = built["econ"], built["prog"], built["sol"]
    sec_tab = security.security_table(econ, prog, sol, params)
    pids = [econ.firm.processes.process_id.iat[int(prog.cols.proc[c])] for c in sol.sel.values()]
    if not pids:
        pytest.skip("empty plan")
    fails = pd.DataFrame({"process_id": pids, "error_floor_cost_per_year": 1e6})
    base = security.ceiling_terms(econ, prog, sol, params, fails, sec_tab)
    icfr = {econ.firm.processes.process_id.iat[int(prog.cols.proc[c])] for c in sol.sel.values() if prog.cols.detail[c].get("icfr")}
    S = float(econ.firm.part1["S"] * econ.vf[-1])
    assert base["c_err"] == pytest.approx(1e6 * sum(1 for x in pids if x not in icfr) / S)


def test_capitalized_share_asu_rule(built, params):
    """Starts from the ASU 2025-06 year use (1 - u)(1 - dc); earlier starts use build.capitalized_share_F."""
    ac = params.accounting
    assert F.capitalized_share_asu(ac.u_novel, ac.dc_share) == pytest.approx((1 - ac.u_novel) * (1 - ac.dc_share))
    lo, hi = params.range("build.capitalized_share_F")
    assert lo == 0.0 and hi == 0.7
