# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Paper sync (spec 19.1): the engine against the running example of theory_core (data/examples/invoice_chain.yaml
and .json, written by code/examples/invoice_chain.py).

1. Every input the YAML takes from the engine defaults resolves, through the engine's own loader, to the value the
   JSON records. A difference means the example is stale (regenerate it) or a default moved without the example.
2. With the example's transition terms, the engine's formulas reproduce the transition NPV, the optimal parallel run
   and the engine's policy, payback, the break-evens and the score path.
3. The engine's composition of the terms (integration cost, dual-running flow, stranded cost, rollback loss)
   reproduces the example's detail.
A disagreement is reported with the side that is wrong; tolerances are not loosened."""
import json
import math
from pathlib import Path

import pytest
import yaml
from scipy import optimize

from autofrontier import config
from autofrontier import formulas as F

EX = Path(__file__).resolve().parents[2] / "data" / "examples"
if not (EX / "invoice_chain.yaml").is_file() or not (EX / "invoice_chain.json").is_file():
    pytest.skip("data/examples/invoice_chain.* not found", allow_module_level=True)

REL = 1e-9
# Known disagreements, each with the side that is wrong (engine/QA/ISSUES.md). A known entry turns a failure into an
# expected failure with that diagnosis; a new disagreement fails.
KNOWN: dict = {}


@pytest.fixture(scope="module")
def ex():
    Y = yaml.safe_load((EX / "invoice_chain.yaml").read_text(encoding="utf-8"))
    J = json.loads((EX / "invoice_chain.json").read_text(encoding="utf-8"))
    return Y, J


def _val(x):
    return x.get("value") if isinstance(x, dict) else x


def _inputs(J):
    return {k: _val(v) for k, v in J["inputs"].items()}


def _npv(T, Tp, **kw):
    t = dict(T, **kw)
    return F.transition_npv(t["F"], t["I"], t["C_J"], t["C_par"], Tp, t["varpi_p"], t["bbar_p"], t["W"], t["C_str"], t["L_roll"],
                            t["T_det"], t["T_h"], t["r"])


def _policy(T, inp, **kw):
    t = dict(T, **kw)
    Ts = float(F.optimal_parallel_run(t["C_par"], t["varpi_p"], t["bbar_p"], t["W"], t["C_str"], t["L_roll"], t["T_det"]))
    lo = max(inp["T_par_min_regulated"], inp["icfr_min_parallel"])
    return min(max(Ts, lo), inp["T_par_max"]), Ts


def _close(a, b):
    if a is None or b is None:
        return a is None and b is None
    return math.isclose(float(a), float(b), rel_tol=REL, abs_tol=1e-6)


def test_inputs_resolve_to_engine_defaults(ex):
    """Inputs sourced default:<key> or range_low/high:<key> equal the engine's current values."""
    Y, J = ex
    p = config.load_params()
    inp = _inputs(J)
    diffs = []
    for sec in ("firm", "parameters", "capital", "parameters_extra"):
        for k, v in (Y.get(sec) or {}).items():
            src = v.get("source") if isinstance(v, dict) else None
            if not isinstance(src, str) or not src.startswith(("default:", "range_low:", "range_high:")):
                continue
            key = src.split(":", 1)[1]
            val = p.get(key) if src.startswith("default:") else p.range(key)[0 if src.startswith("range_low:") else 1]
            if v.get("pick") == "max":
                val = max(val)
            j = inp.get(k)
            same = j == val or (isinstance(j, (int, float)) and isinstance(val, (int, float)) and math.isclose(j, val, rel_tol=1e-12))
            if not same:
                diffs.append(f"{k} ({key}): example {j}, engine {val}")
    assert not diffs, "example inputs differ from engine defaults (regenerate the example or fix the default): " + "; ".join(diffs)


def test_transition_npv_and_parallel_run(ex):
    """Case (a), whose full set of terms the JSON records (case (b) records only W, F and varpi, not its legacy-cost
    terms, so it cannot be recomputed from the JSON)."""
    Y, J = ex
    inp = _inputs(J)
    T = dict(J["transition"])
    case = "transition"
    res = J[case]["results"]
    Tp, Ts = _policy(T, inp)
    assert _close(Ts, res["T_par_star"]), f"{case}: optimal parallel run engine {Ts} vs example {res['T_par_star']}"
    assert _close(Tp, res["T_par"]), f"{case}: policy T_par engine {Tp} vs example {res['T_par']}"
    assert _close(_npv(T, Tp), res["NPV"]), f"{case}: NPV engine {_npv(T, Tp)} vs example {res['NPV']}"
    assert _close(_npv(T, Tp, varpi_p=1.0, bbar_p=1.0), res["NPV_certain"])
    resid = (1 - T["varpi_p"]) * float(F.undetected_failure_prob(Tp, T["T_det"]))
    assert _close(resid, res["residual_risk"])


def test_payback_and_breakevens(ex):
    Y, J = ex
    inp = _inputs(J)
    T = J["transition"]
    res = T["results"]
    Tp, _ = _policy(T, inp)
    pb0 = F.payback_years(T["F"], T["I"], T["C_J"], T["C_str"], T["W"], 0.0, T["C_par"])
    if res["payback"] is None:
        assert math.isinf(pb0) and T["W"] <= 0
    else:
        assert _close(pb0, res["payback"])
        ext = F.payback_years(T["F"], T["I"], T["C_J"], T["C_str"], T["W"], 0.5, T["C_par"]) - pb0
        assert _close(ext, res["payback_extension_6m"])
    fF = lambda x: _npv(dict(T, F=x), _policy(dict(T, F=x), inp)[0])
    be = optimize.brentq(fF, -5e7, 5e7) if fF(-5e7) * fF(5e7) < 0 else None
    assert _close(be, res["F_breakeven"]), f"F break-even engine {be} vs example {res['F_breakeven']}"
    assert _close(_npv(dict(T, T_h=1e4), Tp), res["NPV_unlimited"])
    fT = lambda th: _npv(dict(T, T_h=th), Tp)
    th_be = optimize.brentq(fT, 0.6, 1e4) if fT(0.6) < 0 < fT(1e4) else None
    assert _close(th_be, res["T_h_breakeven"])
    fp = lambda pp: _npv(dict(T, varpi_p=pp), _policy(dict(T, varpi_p=pp), inp)[0])
    assert _close(fp(0.9999), res["NPV_varpi_one"])
    vb = optimize.brentq(fp, 1e-4, 0.9999) if fp(1e-4) < 0 < fp(0.9999) else None
    assert _close(vb, res["varpi_breakeven"])


def test_score_path(ex):
    Y, J = ex
    T, sp = J["transition"], J["score_path"]
    years = int(round(T["T_h"]))
    for basis in ("cash", "gaap"):
        mine = F.score_path_flows(T["W"], T["C_par"], sp["T_par"], 1.0, T["F"], T["I"], T["C_J"], T["C_str"], T["C_wo"], T["T_A"],
                                  sp["revenue"], years, basis)
        for y, (a, b) in enumerate(zip(mine, sp[basis])):
            assert math.isclose(a, b, rel_tol=1e-7, abs_tol=1e-12), f"score path {basis} year {y + 1}: engine {a} vs example {b}"


def test_engine_composition_of_terms(ex):
    """Integration cost, dual-running flow, rollback loss, severance and the dip from the example's detail."""
    Y, J = ex
    inp = _inputs(J)
    T, d = J["transition"], J["transition"]["detail"]
    F_int = float(F.integration_cost(T["iota_from"], T["iota_to"], inp["n_systems"], d["int_cost_per_system"], inp["int_convexity"]))
    assert _close(F_int, d["F_int"])
    assert _close(float(F.parallel_cost_flow(d["C0"], d["E_p"], d["C_dup"], inp["omega_par"], inp["nu_rec"])), T["C_par"])
    assert _close(inp["L_roll_mult"] * d["C0"], T["L_roll"])
    assert _close(inp["dip_share"] * d["C0"] * inp["dip_years"], T["C_J"])
    assert _close((1 - inp["u_d"]) * inp["severance_months"] / 12.0 * d["C_disp"], d["C_sev"])
    assert _close(inp["u_d"] * inp["redeploy_months"] / 12.0 * d["C_disp"], d["C_redeploy"])


def test_engine_composition_of_stranded_cost(ex):
    """C^str = C_sev + C_brk + C_redeploy + C^surv with the engine's one survivor base (F.survivor_base: in-house FTE
    on the changed steps less the displaced) and survivor cost (prop:labor-survivor(a)); the per-wave charge O_s."""
    Y, J = ex
    p = config.load_params()
    inp = _inputs(J)
    d = J["transition"]["detail"]
    lb = p.labor
    N_hc, N_sv, x = (float(v) for v in F.survivor_base(d["N_hc"], d["fte_removed"]))
    assert _close(N_sv, d["N_sv"]) and _close(x, d["x_share"])
    C_surv = float(F.survivor_cost(N_sv, d["w_year"], lb.nu_q, lb.survivor_quits_per_share * x / lb.T_s, lb.T_s, lb.c_rep, 0.0))
    assert _close(C_surv, d["C_surv"])
    O_s = float(F.survivor_wave_charge(N_sv, d["w_year"], lb.T_s, lb.c_rep, lb.survivor_excess_quits / lb.T_s, lb.delta_eff))
    assert _close(O_s, d["O_s"])
    engine = d["C_sev"] + d["C_brk"] + d["C_redeploy"] + C_surv
    example = J["transition"]["C_str"]
    if not _close(engine, example):
        if "C_str composition" in KNOWN:
            pytest.xfail(f"C_str engine {engine:,.0f} vs example {example:,.0f}: " + KNOWN["C_str composition"])
        pytest.fail(f"C_str engine {engine} vs example {example}")
