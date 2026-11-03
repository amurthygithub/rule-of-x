# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Regression tests for reported defects and recent wiring: regulated status decoupled from the reliability target,
the industry priors beyond software (spec 24.10), and the labor-law wiring (theory_labor)."""
import math

import numpy as np
import pandas as pd
import pytest

from autofrontier import config, economics as E, impute, industry, ingest, plans, priors as PR


@pytest.fixture(scope="module")
def pri():
    return PR.load_priors(config.find_data_dir())


def _firm(folder, pri, p):
    ing = ingest.ingest_folder(folder, pri)
    return ing, impute.build_firm(ing, pri, p)


# ---------------- regulated status (coordinator bug report, 29 Oct) ----------------
def test_target_change_never_changes_regulated_status(firms_dir, pri, params, built):
    """Lowering the reliability target (r_bar_high 0.99 -> 0.988, as in the invoice example's illustration) changes
    neither the regulated status of any unit or process nor the regulated build multiplier."""
    q = params.copy()
    q.set("review.r_bar_high", 0.988, origin="test")
    q.set("review.r_bar_licensed", 0.985, origin="test")
    _, f2 = _firm(firms_dir / "synthetic", pri, q)
    f1 = built["firm"]
    assert (f1.units.r_bar.values != f2.units.r_bar.values).any()          # the target did change
    assert np.array_equal(f1.units.regulated.values, f2.units.regulated.values)
    assert np.array_equal(f1.processes.regulated.values, f2.processes.regulated.values)
    e1, e2 = built["econ"], E.build_econ(f2, q)
    assert np.array_equal(E.unit_regulated(f1.units), E.unit_regulated(f2.units))
    a1, a2 = e1.F_build[..., E.A], e2.F_build[..., E.A]
    ok = np.isfinite(a1) & np.isfinite(a2)
    assert np.allclose(a1[ok], a2[ok], rtol=1e-12)


def test_regulated_from_class_icfr_high_risk_licensed(built):
    """Regulated status comes from the regulated class (licensed, high-risk), ICFR scope or a firm input."""
    U = built["firm"].units
    reg = U.regulated.values.astype(bool)
    assert (reg == (U.regulated_basis.astype(str).values != "")).all()
    assert reg[(U.regulated_class.values != "none")].all()
    P = built["firm"].processes
    assert P.loc[P.process_name.str.lower().str.contains("procure to pay|payroll|record to report"), "regulated"].eq(1).all()
    # Lead to close is in scope only through its order-booking step (CRM-to-billing integration, channel c)
    p08 = U[(U.process_id == "P08") & (U.icfr_step == 1)]
    assert set(p08.step.astype(int)) <= {6} and (p08.icfr_channel.str.contains("integration")).all()


def test_regulated_multiplier_in_sobol_set():
    from autofrontier.scenarios import SOBOL_ALWAYS
    assert "build.regulated_mult" in SOBOL_ALWAYS


def test_round2_parameters_follow_params_files(params):
    """Params commit of 29 Oct 2026: the compute-share path and the pass-through scenario set equal data/tasks/params.yaml,
    and the linked round-2 values arrive with their classes (notes/params_commit_2026-10-29.md)."""
    raw = config.read_yaml(config.REPO_DIR / "data" / "tasks" / "params.yaml")
    cc = raw["part1_ceiling"]["c_c_compute_share"]
    want = {"2025": cc["value"], **{h: v["value"] for h, v in cc["by_horizon"].items()}}
    assert {k: float(v) for k, v in params.finance.c_c_full_automation.items()} == pytest.approx(want)
    assert list(params.competition.phi_ind_scenarios) == raw["pass_through"]["industry_pass_through_scenarios"]["value"]
    for key, val, rng, cls in [("success.b_bar", 0.67, [0.37, 0.85], "a"), ("constraints.kappa_abs", 0.10, [0.05, 0.22], "b"),
                               ("review.r_bar_high", 0.98, [0.975, 0.995], "b"), ("review.q_M", 0.995, [0.99, 0.998], "b"),
                               ("augment.e_H", 0.02, [0.009, 0.05], "b"), ("build.regulated_mult", 1.5, [1.1, 2.0], "b")]:
        assert params.get(key) == pytest.approx(val) and params.range(key) == pytest.approx(rng) and params.grounding(key) == cls, key
    from autofrontier.scenarios import scenario_set
    names = {k for k in scenario_set(params, type("F", (), {"base_year": 2026, "fin": {}})()) if k.startswith("pass_through_")}
    assert names == {"pass_through_0", "pass_through_50", "pass_through_70"}
    # Paper 1's own copies (its replication package does not ship data/tasks): code/calibrate_horizons.py and
    # code/paper1_macros.py carry the same values
    from conftest import load_reference
    cal = load_reference("calibrate_horizons")
    assert cal["CC"]["prices2025"][0] == pytest.approx(cc["value"]) and list(cal["CC"]["prices2025"][1]) == pytest.approx(cc["range"])
    for h, v in cc["by_horizon"].items():
        assert cal["CC"][h][0] == pytest.approx(v["value"]) and list(cal["CC"][h][1]) == pytest.approx(v["range"]), h
    po, ch = raw["project_outcomes"], raw["change_capacity"]
    for k, blk, lo_case, hi_case in [("varpi", po["transformation_attempt_creates_value_varpi"], "slow", "fast"),
                                     ("bbar", po["transformation_value_realized_share_b_bar"], "slow", "fast"),
                                     ("kappa_abs", ch["affected_fte_share_per_year"], "slow", "fast"),
                                     ("Temb", ch["embedding_time_T_emb_years"], "fast", "slow")]:
        assert cal["PACE"]["central"][k] == pytest.approx(blk["value"]), k
        assert cal["PACE"][lo_case][k] == pytest.approx(blk["range"][0]) and cal["PACE"][hi_case][k] == pytest.approx(blk["range"][1]), k
    assert not any(p_.get("haircut") for p_ in cal["PACE"].values())
    assert list(cal["PHI"]) == raw["pass_through"]["industry_pass_through_scenarios"]["value"]
    assert cal["HHI"] == pytest.approx(params.competition.hhi)


def test_paper1_itgc_units_follow_engine(params):
    """Paper 1's copy of the ITGC unit costs (code/paper1_macros.py ITGC_UNITS, the \\ItgcLine and \\ItgcApps macros) equals
    the engine defaults. Engine change E3 (29 Oct 2026) set accounting.C_val to the KPMG control-test effort of $24,000
    (Paper 2's value); Paper 1's copy follows when its owner updates paper1_macros.py."""
    from conftest import load_reference
    mac = load_reference("paper1_macros")
    assert mac["ITGC_UNITS"] == {"c_acc": params.accounting.itgc_c_acc, "c_chg": params.accounting.itgc_c_chg,
                                 "C_val": params.accounting.C_val, "c_ifc": params.accounting.itgc_c_ifc}


# ---------------- industry priors (spec 24.10) ----------------
def test_industry_match_and_k(pri):
    sw = industry.industry_prior(pri, "513210")
    assert sw["group"] == "Software (System & Application)" and sw["k"] == pytest.approx(0.574, abs=1e-3)
    assert sw["k_variant"] in ("unadj", "unadjusted")
    hosp = industry.industry_prior(pri, "622110")
    assert hosp["weak_prior"] and any("weak prior" in f for f in hosp["flags"])
    gen = industry.industry_prior(pri, "999999")
    assert gen["group"] == industry.GENERIC_GROUP
    k, rng, src = industry.k_default(sw, config.load_params())
    assert rng == (0.22, 2.03) and "industry k" in src


def test_pooled_software_row_not_used_for_professional_services(pri):
    """A law firm (NAICS 541110) must not get the pooled 51/54 software prior."""
    law = impute._industry_shares(pri, "541110", 5e8)
    soft = impute._industry_shares(pri, "513210", 5e8)
    assert "51/54" not in law.attrs["source"] and "software" not in law.attrs["source"].lower()
    assert law.attrs["prior_basis"] != "sec_panel" and soft.attrs["prior_basis"] == "sec_panel"


def test_industry_rate_applied_unless_overridden(pri):
    p = config.load_params()
    ind = industry.industry_prior(pri, "622110")
    keys = industry.apply_rates(p, ind)
    assert "finance.r" in keys and p.finance.r == pytest.approx(math.log1p(ind["cost_of_capital"]))
    lo, hi = p.range("finance.r")
    assert lo < p.finance.r < hi
    q = config.load_params()
    q.set("finance.r", 0.05, origin="command line")
    assert "finance.r" not in industry.apply_rates(q, ind) and q.finance.r == 0.05
    s = config.load_params()
    assert industry.apply_rates(s, industry.industry_prior(pri, "513210")) == []      # software: the default group


# ---------------- labor wiring (theory_labor) ----------------
def test_labor_site_table_and_severance(built):
    f = built["firm"]
    sites = f.jurisdictions
    assert {"T_leg", "floor_months", "severance_months", "residency_status", "unverified"} <= set(sites.columns)
    assert (sites.severance_months >= sites.floor_months - 1e-12).all()
    assert (sites.severance_months >= sites.plan_months - 1e-12).all()
    assert f.org["jurisdiction"]["rules_as_of"] == "2026-10-29"


def test_residency_cap_and_mechanism(firms_dir, pri, params):
    """EU personal data with a U.S.-only vendor and no mechanism caps readiness; a DPF-certified vendor lifts the
    cap for sites without a firm-declared residency rule."""
    ing, f = _firm(firms_dir / "synthetic", pri, params)
    e = E.build_econ(f, params)
    om = e.info["omega_res"]
    if not (om > 0).any():
        pytest.skip("synthetic firm has no restricted personal data")
    ing.org = ing.org.model_copy(update={"vendor_regions": "US; EU"})
    f2 = impute.build_firm(ing, pri, params)
    e2 = E.build_econ(f2, params)
    assert e2.info["omega_res"].sum() < om.sum()
    assert (e2.iota_u >= e.iota_u - 1e-12).all()


def test_legal_hold_extends_parallel_run(built, params):
    """A legal lead longer than the parallel run extends T_par to the earliest dismissal date (prop:labor-lead(e))."""
    econ = built["econ"]
    pb = plans.PlanBuilder(econ)
    fv = {"share": np.array([1.0]), "T_leg": np.array([0.8]), "T_tech": np.array([0.0]), "cont0": np.array([True])}
    T = econ.T
    Tp, Cp, Tst, tau = pb._legal_timing(fv, np.full(T, 0.2), np.full(T, 1e5), np.full(T, 0.8), 0.85, np.full(T, 1e6),
                                        np.full(T, 2e5), np.full(T, 5e5), np.full(T, 4e5), np.full(T, 1e4), np.ones(T, bool), True)
    assert (Tp >= 0.8 - 1e-9).all()
    assert (Cp < 1e5).all()                       # the run before the hold ends costs c-hat' only
    Tp0, Cp0, _, _ = pb._legal_timing({**fv, "T_leg": np.array([0.0])}, np.full(T, 0.2), np.full(T, 1e5), np.full(T, 0.8), 0.85,
                                      np.full(T, 1e6), np.full(T, 2e5), np.full(T, 5e5), np.full(T, 4e5), np.full(T, 1e4),
                                      np.ones(T, bool), True)
    assert np.allclose(Tp0, 0.2) and np.allclose(Cp0, 1e5)


def test_survivor_wave_charge_in_program(built):
    prog = built["prog"]
    assert prog.info["O_s"] > 0 and prog.O_w > 0


def test_ai_engineer_premium_grounded(params):
    assert params.build.ai_engineer_premium == pytest.approx(1 + params.talent.premium)
    assert params.grounding("build.ai_engineer_premium") == "a"


# ---------------- ICFR scope: process- and step-level (coordinator decision, 29 Oct) ----------------
def test_icfr_scope_recruiting_out_p2p_in(built):
    """Recruiting, sourcing and selection steps of Hire to retire are outside ICFR; compensation and termination
    changes are inside; every Procure-to-pay step (PO approval, matching, payment, payables) is ICFR and regulated."""
    U = built["firm"].units
    p05 = U[U.process_id == "P05"]
    recruit = p05[p05.step.isin([1, 2, 3, 4])]
    assert len(recruit) and (recruit.icfr_step == 0).all()
    assert not recruit.regulated_basis.astype(str).str.contains(r"(?:^|;)icfr(?:;|$)").any()
    # where recruiting is regulated at all, it is through the EU AI Act high-risk class, not ICFR
    assert set(recruit.loc[recruit.regulated == 1, "regulated_basis"].astype(str)) <= {"regulated_class:high_risk_eu"}
    comp = p05[p05.step.isin([6, 8])]
    assert len(comp) and (comp.icfr_step == 1).all() and (comp.regulated == 1).all()
    p2p = U[U.process_id == "P02"]
    assert len(p2p) and (p2p.icfr_step == 1).all() and (p2p.regulated == 1).all()
    P = built["firm"].processes.set_index("process_id")
    assert P.loc["P02", "icfr_scope"] == "full" and P.loc["P05", "icfr_scope"] == "partial"
    for pid in ("P12", "P18", "P22", "P23"):
        if pid in P.index:
            assert P.loc[pid, "icfr_scope"] == "none" and not (U[U.process_id == pid].icfr_step == 1).any()


def test_quote_to_contract_negotiate_terms_out_of_scope(built):
    """Spec 26: the Quote-to-contract "negotiate terms" step stays outside ICFR scope; contract approval and the
    review of non-standard terms that affect revenue recognition stay in."""
    S = built["firm"].priors.icfr_steps if hasattr(built["firm"], "priors") else None
    if S is None:
        from autofrontier import config, priors as PR
        S = PR.load_priors(config.find_data_dir()).icfr_steps
    q = S[S.process_id == "P09"].set_index("step_name")
    assert not bool(q.loc["Negotiate terms", "icfr_step"])
    assert bool(q.loc["Approve and sign", "icfr_step"]) and bool(q.loc["Review terms for compliance", "icfr_step"])
    neg_step = int(q.loc["Negotiate terms", "step"])
    U = built["firm"].units
    u = U[(U.process_id == "P09") & (U.step == neg_step)]
    assert (u.icfr_step == 0).all()


def test_icfr_inventory_steps_need_inventory(firms_dir, pri, params):
    """Inventory, costing and cut-off steps of P20 and P21 count only where the firm holds inventory: out when the
    firm says it holds none, in when it reports inventory, "assumed in scope" when no input says either way."""
    ing = ingest.ingest_folder(firms_dir / "synthetic", pri)
    f0 = impute.build_firm(ing, pri, params)                       # the synthetic firm says holds_inventory = 0
    u0 = f0.units[f0.units.process_id.isin(["P20", "P21"])]
    if not len(u0):
        pytest.skip("P20 and P21 not built for the synthetic firm")
    assert (u0.icfr_step == 0).all() and (u0[u0.icfr_status != "out"].icfr_status == "out (firm input)").all()
    ing.org = ing.org.model_copy(update={"holds_inventory": None})
    f1 = impute.build_firm(ing, pri, params)
    u1 = f1.units[f1.units.process_id == "P20"]
    assert (u1.loc[u1.step == 2, "icfr_status"] == "assumed in scope").all() and (u1.loc[u1.step == 2, "icfr_step"] == 1).all()
    ing.financials = ing.financials.model_copy(update={"inventory": 5e6})
    f2 = impute.build_firm(ing, pri, params)
    u2 = f2.units[f2.units.process_id == "P20"]
    assert (u2.loc[u2.step == 2, "icfr_status"] == "in scope").all()


def test_icfr_firm_override_wins(firms_dir, pri, params):
    ing = ingest.ingest_folder(firms_dir / "synthetic", pri)
    vols = ing.volumes.copy()
    vols["icfr_scope"] = np.where(vols.process_id == "P07", "full", None)
    ing.volumes = vols
    f = impute.build_firm(ing, pri, params)
    P = f.processes.set_index("process_id")
    if "P07" in P.index and "P07" in set(vols.process_id):
        assert P.loc["P07", "icfr_scope"] == "full" and (f.units[f.units.process_id == "P07"].icfr_step == 1).all()


def test_survivor_cost_nonzero_uses_inhouse_base(built, params):
    """With a share-dependent survivor quit rate, C^surv is positive and equals the formula on the one survivor base
    (in-house FTE on the changed steps less the displaced; outsourced work excluded)."""
    from autofrontier import formulas as F
    q = params.copy()
    q.set("labor.survivor_quits_per_share", 0.05, origin="test")
    econ = E.build_econ(built["firm"], q)
    pb = plans.PlanBuilder(econ)
    checked = 0
    for pidx in range(len(built["firm"].processes)):
        lvl = econ.L - 1
        md = np.asarray(pb.modes(pidx, "full")[0][:, lvl, -1])
        pi = pb._pinfo[pidx]
        t = pb.terms(pidx, lvl, md)
        if t is None or not (t["fte_removed"] > 0).any():
            continue
        ch = md != pi["bm"]
        inh = pi["bm"] == E.H
        y = int(np.argmax(t["fte_removed"] > 0))
        _, N_sv, x = F.survivor_base(float((pi["fte"] * (ch & inh)).sum() * econ.vf[y]), float(t["fte_removed"][y]))
        exp = float(F.survivor_cost(N_sv, float(np.mean(pi["w"])) * q.labor.hours_per_fte, q.labor.nu_q,
                                    0.05 * x / q.labor.T_s, q.labor.T_s, q.labor.c_rep, 0.0))
        assert exp > 0 and float(t["C_attr"][y]) == pytest.approx(exp, rel=1e-9)
        checked += 1
        if checked >= 3:
            break
    assert checked > 0



# ---------------- ICFR channels and consequences (coordinator, 29 Oct) ----------------
def test_refund_step_in_scope_via_billing(firms_dir, pri, params, built):
    """Ticket to resolution: the step that issues refunds or credits writes billing (channel b), so it is in scope;
    a firm that says its support team issues none takes it out; without an input it is assumed in scope."""
    U = built["firm"].units
    ref = U[(U.process_id == "P07") & (U.icfr_step == 1)]
    assert len(ref) and ref.icfr_channel.str.contains("system").all()
    assert ref.financial_system_written.str.contains("billing").all() and (ref.icfr_status == "in scope").all()
    ing = ingest.ingest_folder(firms_dir / "synthetic", pri)
    ing.org = ing.org.model_copy(update={"issues_refunds_credits": 0})
    f = impute.build_firm(ing, pri, params)
    assert not (f.units[f.units.process_id == "P07"].icfr_step == 1).any()
    ing.org = ing.org.model_copy(update={"issues_refunds_credits": None})
    f = impute.build_firm(ing, pri, params)
    assert (f.units[(f.units.process_id == "P07") & (f.units.icfr_step == 1)].icfr_status == "assumed in scope").all()


def test_recruiting_not_regulated_for_us_only_firm(firms_dir, pri, params):
    """EU AI Act high-risk status needs an EU nexus (Art. 2): a U.S.-only firm's recruiting steps are not regulated."""
    ing = ingest.ingest_folder(firms_dir / "synthetic", pri)
    ing.jurisdictions = None
    ros = ing.roster.copy()
    ros["location"] = "Austin, TX"
    ing.roster = ros
    ing.org = ing.org.model_copy(update={"eu_market": 0})
    f = impute.build_firm(ing, pri, params)
    rec = f.units[(f.units.process_id == "P05") & f.units.step.isin([2, 3, 4])]
    assert len(rec) and (rec.regulated == 0).all() and (rec.regulated_class != "high_risk_eu").all()
    ing.org = ing.org.model_copy(update={"eu_market": 1})
    f2 = impute.build_firm(ing, pri, params)
    rec2 = f2.units[(f2.units.process_id == "P05") & f2.units.step.isin([2])]
    assert (rec2.regulated == 1).all()


def test_agent_on_gl_carries_itgc_costs(built, params):
    """An agent that performs an in-scope step (posting to the GL, subledgers or billing) is an in-scope application:
    its column carries the ITGC line of eq:acct-itgc (access, change, the ICFR retest at each forced model upgrade,
    operations and its interfaces to in-scope systems), the setup cost and the timeliness cost C^tml; an agent on
    out-of-scope steps carries none."""
    from autofrontier import formulas as F
    econ = built["econ"]
    pb = plans.PlanBuilder(econ)
    ac, sec, rl = params.accounting, params.security, params.reliability
    nu_out = rl.downtime_hours / 24.0 / ac.D_bar
    tml = F.timeliness_cost(ac.n_cl, nu_out, ac.T_cw, ac.D_bar, ac.T_sl, ac.c_del, ac.L_late, ac.C_fb, ac.c_fb, ac.t_sw)["C_tml"]
    inside = outside = 0
    for pidx in range(len(econ.firm.processes)):
        for lvl in range(econ.L):
            md = np.asarray(pb.modes(pidx, "full")[0][:, lvl, -1])
            t = pb.terms(pidx, lvl, md)
            if t is None or not (md == E.A).any():
                continue
            if t["icfr_units_automated"] > 0:
                inside += 1
                base = (ac.itgc_c_acc * (ac.itgc_n_id + ac.itgc_perm_per_step * t["icfr_units_automated"]) + ac.itgc_c_chg * ac.itgc_n_chg
                        + ac.C_val / sec.T_up + ac.itgc_c_ops)
                extra = t["itgc_annual"] - base
                assert extra >= -1e-6 and extra / ac.itgc_c_ifc == pytest.approx(round(extra / ac.itgc_c_ifc))
                assert t["itgc_setup"] == ac.itgc_setup and t["tml"] == pytest.approx(tml)
                assert np.allclose(t["fallback_annual"], tml)
            else:
                outside += 1
                assert t["itgc_annual"] == 0 and t["itgc_setup"] == 0 and t["tml"] == 0
        if inside >= 3 and outside >= 3:
            break
    assert inside > 0 and outside > 0


def test_icfr_snapshot_matches_data_contract():
    """The engine's fallback snapshot (priors/icfr_*.csv) equals the data contract; regenerate it with
    tools/sync_icfr_priors.py when the data changes."""
    import importlib.util
    from pathlib import Path
    tool = Path(__file__).resolve().parents[1] / "tools" / "sync_icfr_priors.py"
    spec = importlib.util.spec_from_file_location("sync_icfr_priors", tool)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        sc, st = mod.snapshot()
    except SystemExit:
        pytest.skip("data contract has no ICFR columns")
    pri_dir = Path(__file__).resolve().parents[1] / "src" / "autofrontier" / "priors"
    sc0 = pd.read_csv(pri_dir / "icfr_scope.csv", dtype=str).fillna("")
    st0 = pd.read_csv(pri_dir / "icfr_steps.csv", dtype=str).fillna("")
    pd.testing.assert_frame_equal(sc.fillna("").reset_index(drop=True), sc0.reset_index(drop=True), check_dtype=False)
    pd.testing.assert_frame_equal(st.fillna("").reset_index(drop=True), st0.reset_index(drop=True), check_dtype=False)


def test_regulated_class_ties_go_to_the_stricter_class():
    """A tie between a unit's activity classes goes to the most demanding class: licensed, then EU AI Act high-risk
    (with an EU nexus), then ICFR, then other regulated classes, then none."""
    m = impute.modal_regulated_class
    assert m(["icfr", "none"]) == "icfr" and m(["none", "icfr", "icfr", "none"]) == "icfr"
    assert m(["none", "none", "icfr"]) == "none"                       # a majority still wins
    assert m(["high_risk_eu", "licensed"]) == "licensed"
    assert m(["high_risk_eu", "icfr"]) == "high_risk_eu"
    assert m(["high_risk_eu", "icfr"], eu_nexus=False) == "icfr"
    assert m(["high_risk_eu", "none"], eu_nexus=False) == "none"
    assert m(["other_regulated", "none"]) == "other_regulated" and m([]) == "none"
