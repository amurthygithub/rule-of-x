# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""The playbook and the lever map (spec 28 and 29; notes/playbook_engine_spec.md): decisions per activity unit,
execution per process step, through the public API (autofrontier.api), with the test values of spec Section 7."""
import math
import shutil

import numpy as np
import pandas as pd
import pytest

from autofrontier import api, config, formulas as F, impute, ingest, priors as PR

ACT_FIELDS = ["unit_key", "kind", "function_id", "process_id", "step", "step_name", "dwa_id", "dwa_title", "gwa_id", "critical_path",
              "volume_per_year", "hours_per_unit", "fte_in_house", "mode_activity_now", "mode_activity_target", "mode_step_now",
              "mode_step_target", "mode_plan_best", "first_year_A_at_target", "binding_now", "binding_target", "binding_now_detail",
              "icfr_status", "icfr_channel", "icfr_condition", "regulated_class", "program_constraint", "pre_readiness_floor",
              "pre_readiness_now", "pre_readiness_target", "pre_review_share_target", "pre_eval_set", "pre_itgc_lines", "typical_systems",
              "gate_min_detection", "gate_detection_now", "gate_max_residual_error", "residual_error_A_target", "gate_min_volume",
              "pilot_band_low", "pilot_band_high", "gate_threshold", "wave", "wave_start_year", "depends_on", "moves_with_steps",
              "integration_first", "role_process_owner", "role_occupations", "role_ai_engineer_months", "role_control_owner",
              "role_reviewer_fte_target", "fte_effect_target", "labor_lead_days", "kpi_unit_cost_now", "kpi_residual_error",
              "kpi_review_share", "kpi_cycle_time", "ctl_icfr", "ctl_itgc_line_usd", "ctl_interface_line", "fallback",
              "ev_exposure_llm", "ev_aei_usage_share", "ev_aei_automation_pct", "ev_aei_augmentation_pct", "ev_task_hours",
              "ev_physical_share", "ev_licensed_share", "ev_metr_feasibility_date", "ev_capability_margin_log", "ev_detection_src",
              "ev_target_src", "ev_build_src", "ev_review_time_src", "ev_onet_task_links", "ev_task_ids", "ev_task_examples",
              "tier_now", "tier_target", "tier_target_reason", "mode_swap_params_now", "switch_conditions"]
BINDINGS = {"permissibility", "feasibility: physical", "feasibility: capability horizon", "readiness", "reliability: detection",
            "reliability: residual or appetite", "volume threshold", "cost", "none"}


# ---------------- spec Section 7 test values (no run needed) ----------------
def test_spec7_values():
    for g, sig, k in ((0.25, 0.43, 0.0), (0.05, 0.2, 0.5), (0.6, 0.55, 1.2)):
        c = F.playbook_calibration(g, sig, k, 0.3, 3.3)
        assert abs(float(F.sigma_star(c["ell"], c["X_hat"] - k, 0.3)) - sig) < 1e-12                 # lem:playbook-calib(a)
        assert float(F.delta_star(c["ell"], c["X_hat"] - k, 0.3)) == pytest.approx(c["Delta"], rel=1e-12)
    x0 = F.x_dagger_0(0.0, 0.05, 0.3, 0.0535)
    assert abs(F.x_dagger_exact(0.0, 0.0535, 0.3, 1e-4, 1e-4 * 0.05) / x0 - 1) < 1e-3                  # the d_sigma -> 0 limit
    assert F.x_dagger_exact(0.0, 0.0535, 0.3, 0.2, 0.01) == pytest.approx(6.85, abs=0.005)            # theory_regimes example
    assert 2 / (3 + 1) == pytest.approx(0.5) and 2 / (1 / 0.25 + 1) == pytest.approx(0.40)             # Cournot 2/(n+1) at HHI 0.25
    lv = F.lever_values(0.35, 0.03, 0.0535, 9.0, 0.0, 0.3, 0.1, 0.05, 0.02, 0.1, 0.4, 0.6, 0.09, 0.25)
    assert lv["retention_point"] == pytest.approx(0.09) and lv["ai_product_breakeven"] == pytest.approx(9.0)
    assert 9 * 0.01 - 0.03 == pytest.approx(0.06) and 2.5 * 0.01 - 0.03 == pytest.approx(-0.005)      # cor:prod-dilution example
    xs = [F.exit_weight(0.25, math.log(1.22), 0.03, t, 14 * 0.25) for t in (6, 3, 0)]               # regimes B7
    assert [round(v, 2) for v in xs] == [2.21, 2.70, 3.50] and round(F.myopic_weight(8, 0, 0.3), 2) == 6.15
    for g, d, h in ((0.5, 0.0, 0.05), (0.1, 0.0, 0.01), (0.5, 0.25, 0.075), (0.1, 0.25, 0.035)):          # cor:capital
        assert (g + d) * 0.10 == pytest.approx(h)


# ---------------- one run ----------------
@pytest.fixture(scope="module")
def book(golden_run):
    res, out = golden_run("synthetic")
    return res, out, api.playbook(res)


@pytest.mark.slow
def test_every_field_and_file(book):
    res, out, bk = book
    ac, st = bk["activities"], bk["steps"]
    assert len(ac) == len(res["firm_obj"].units)
    assert set(ACT_FIELDS) <= set(ac.columns), sorted(set(ACT_FIELDS) - set(ac.columns))
    assert set(ac.binding_now) <= BINDINGS and set(ac.binding_target) <= BINDINGS
    assert set(ac.tier_target) <= {"A", "B", "C"} and set(st.tier_target) <= {"A", "B", "C"}
    for f in ("playbook_steps.csv", "playbook_activities.csv", "playbook_data_dictionary.csv"):
        assert (out / f).is_file()
    dic = bk["dictionary"]
    assert set(ac.columns) - {"regime", "mode_now", "mode_plan", "in_plan", "fte_after", "saving_per_year", "kpi_unit_cost_plan",
                              "interface_lines_process", "interface_line_per_year_process", "ev_exposure_llm_class", "ev_aei_class",
                              "ev_task_hours_class", "ev_capability_class", "ev_volume_src", "robustness_share_positive",
                              "tier_now_reason", "binding_target_detail", "role_occupations_source", "preconditions", "gates",
                              "threshold_cost_gap_share", "distance_capability_years", "distance_readiness", "distance_reliability",
                              "distance_detection", "distance_volume", "process_name", "iota0"} <= set(dic.field)
    assert "CC BY 4.0" in dic.attribution.iat[0]
    md = (out / "report.md").read_text(encoding="utf-8")
    assert "### Playbook by process step" in md and "### Levers by position and setup" in md
    assert "O*NET" in md.splitlines()[-1] or "O*NET" in md[-800:]


@pytest.mark.slow
def test_task_statements_attached(book):
    _, _, bk = book
    ac = bk["activities"]
    if res_has_tasks(ac):
        dwa = ac[ac.ev_onet_task_links.fillna(0) > 0]
        assert len(dwa) and (dwa.ev_task_examples.str.len() > 0).all() and (dwa.ev_task_ids.str.len() > 0).all()


def res_has_tasks(ac):
    return ac.ev_task_ids.notna().any()


@pytest.mark.slow
def test_steps_aggregate_activities(book):
    _, _, bk = book
    ac, st = bk["activities"], bk["steps"]
    assert st.fte_in_house.sum() == pytest.approx(ac.fte_in_house.sum())
    assert st.fte_after.sum() == pytest.approx(ac.fte_after.sum())
    assert st.activity_units.sum() == len(ac)


@pytest.mark.slow
def test_tier_rule_and_consistency(book, params):
    res, _, bk = book
    ac = bk["activities"]
    tc = params.playbook.tier_c_prob
    rob = ac.robustness_share_positive
    assert (ac.loc[rob.notna() & (rob < tc), "tier_target"] == "C").all()          # Monte Carlo part of def:playbook-tier
    a = ac[ac.tier_target == "A"]
    assert a.binding_target.isin(["permissibility", "feasibility: physical", "feasibility: capability horizon"]).all()
    c = ac[ac.tier_target == "C"]
    assert (c.tier_target_reason.str.contains("flips with") | c.tier_target_reason.str.contains("Monte Carlo")).all()
    auto = ac[ac.mode_plan == "A"]
    assert len(auto) and auto.in_plan.all()
    off = ac[~ac.in_plan]
    assert (off.mode_plan == off.mode_now).all() and off.wave.isna().all()
    assert set(ac[ac.in_plan].process_id) == set(res["plan"].process_id)
    icfr_auto = auto[auto.icfr_status.isin(["in scope", "assumed in scope"])]
    assert (icfr_auto.fallback != "none needed").all() and icfr_auto.gates.str.contains("quarter-end close").all()
    assert ac.kpi_cycle_time.str.contains("Wave 0|Tier 4").all()
    assert bk["summary"]["flip_keys_tested"] > 0


@pytest.mark.slow
def test_lever_map(book):
    res, _, _ = book
    lm = api.lever_map(res)
    assert set(lm["regimes"]) == set(res["regimes"])
    st = lm["state"]
    if "observed spend optimal" in st["source"]:
        assert abs(lm["check_calibration"]) < 1e-9
    for nm, o in lm["regimes"].items():
        if not o.get("applicable"):
            continue
        th = o["thresholds"]["overhead"]
        assert th["distance_X_dagger_0"] == pytest.approx(o["X_o"] - th["X_dagger_0"])
        grow_first = (o["X_o"] - st["k"]) / (st["X_hat"] - st["k"]) > (st["a_GA"] / st["sigma"]) ** (1 - st["alpha"])
        if grow_first:
            assert o["X_o"] > th["X_dagger_0"] - 1e-9 or "observed spend optimal" not in st["source"]
    assert lm["binding_setup"]["capacity"] is not None


@pytest.mark.slow
def test_api_writes_the_playbook(book, tmp_path):
    res, _, bk = book
    paths = api.write_playbook(res, tmp_path / "pb")
    assert len(paths) >= 3 and pd.read_csv(paths[0]).shape[0] == len(bk["steps"])
    assert api.version()["notice"] and "permanent_capital" in api.REGIMES
    assert "cross_process_dependencies" in bk["not_computed"]


# ---------------- firm inputs: task list and policy ----------------
def test_firm_tasks_override_the_step(firms_dir, tmp_path, params):
    pri = PR.load_priors(config.find_data_dir())
    f = tmp_path / "tasks"
    shutil.copytree(firms_dir / "small", f)
    pa = pri.process_activities
    row = pa[pa.process_id == "P02"].iloc[0]
    dwa = row.dwa_id
    pd.DataFrame([{"firm_task": "Our own matching task", "process_id": "P02", "step": row.step, "dwa_id": dwa, "hours": 0.5},
                  {"firm_task": "zzqx unmappable words qqzz", "process_id": "P02", "step": row.step, "dwa_id": "", "hours": 0.1}]
                 ).to_csv(f / "tier3_tasks.csv", index=False)
    pd.DataFrame([{"field": "residual_error_tolerance", "value": 0.01}]).to_csv(f / "tier3_policy.csv", index=False)
    ing = ingest.ingest_folder(f, pri)
    assert ing.firm_tasks is not None and ing.policy.residual_error_tolerance == 0.01
    firm = impute.build_firm(ing, pri, params)
    tm = firm.task_map
    assert (tm.method == "given").sum() == 1 and tm.method.str.startswith("unmapped").sum() == 1
    U = firm.units
    u = U[(U.process_id == "P02") & (U.step == row.step)]
    assert len(u) and set(u.activity_id) == {dwa} and (u.tier4 == 1).all()


# ---------------- synthesis theorist W14 to W16 ----------------
def test_exit_weight_limit_and_pc_weight_domain():
    tau, m, XT = 5.0, 0.3, 4.0
    assert F.exit_weight(m, 0.1, 0.1, tau, XT) == pytest.approx(m * tau + XT)
    assert F.exit_weight(m, 0.1, 0.1 - 1e-6, tau, XT) == pytest.approx(m * tau + XT, rel=1e-5)     # continuous at r = G
    assert F.pc_growth_weight(0.3, 0.2231, 0.329) is None                                           # G_i >= i_U: undefined


def test_net_multiple_flag_sets_the_public_weight(params):
    from types import SimpleNamespace
    from autofrontier import regimes
    pt = {"m0": 0.3, "G": 0.2, "k": 0.5, "ell": 0.05, "alpha": 0.3, "X": 11.1, "m_cash": -0.1, "m_op": 0.0, "S": 1e9}
    for flag, expect in ((1, 11.1), (0, None)):
        firm = SimpleNamespace(part1=pt, fin={"ev_revenue_multiple": 11.1, "multiple_is_net_of_pressure": flag, "da": 0.0})
        reg = regimes.make_regime("public", params, SimpleNamespace(regime={}, fin={}, part1={"g": 0.3, "G": 0.2}))
        X = regimes.growth_weight(firm, reg, params)["X_o"]
        if expect is not None:
            assert X == pytest.approx(expect)
        else:
            assert X < 11.1


@pytest.mark.slow
def test_ranking_uses_the_four_proportional_levers(book):
    res, _, _ = book
    for o in api.lever_map(res)["regimes"].values():
        if o.get("applicable"):
            assert {k for k, _ in o["ranking"]} == {"growth_automation", "overhead", "engineering", "cost_of_revenue_replicable"}
            assert "retention_point" in o["reported_separately"]
