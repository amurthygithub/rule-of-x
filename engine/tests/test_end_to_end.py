# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""End-to-end tests (spec 19.1): golden snapshots of the synthetic, small and PE-owned firms; determinism with a
fixed seed; a Tier-0-only run that reports wide ranges; the full synthetic run under two minutes with the report's
required sections; and the size generator from 100 to 100,000 employees.

Golden snapshots live in tests/golden/. When a change to the numbers is intended, run
    python tools/accept_golden.py
and record the reason in CHANGELOG.md."""
import json
import re
import time

import pandas as pd
import pytest

from autofrontier import REQUIRED_NOTICE, ingest, impute, pipeline, synthetic
from autofrontier.qa import GOLDEN_FIRMS, compare, golden_path, snapshot
from autofrontier.report import DECISION_SUPPORT

pytestmark = pytest.mark.slow


@pytest.mark.parametrize("name", list(GOLDEN_FIRMS))
def test_golden_snapshot(golden_run, name):
    res, _ = golden_run(name)
    path = golden_path(name)
    assert path.is_file(), f"no golden snapshot for {name}: run python tools/accept_golden.py"
    old = json.loads(path.read_text(encoding="utf-8"))
    diffs = compare(snapshot(res), old)
    assert not diffs, f"{name} differs from its golden snapshot (if intended, run tools/accept_golden.py): " + "; ".join(diffs[:10])


def test_deterministic_with_fixed_seed(golden_run):
    a, _ = golden_run("small")
    b, _ = golden_run("small", again=True)
    assert compare(snapshot(a), snapshot(b), rel=0.0) == []
    assert a["version"]["seed"] == b["version"]["seed"]
    assert a["version"]["hashes"] == b["version"]["hashes"]


def test_tier0_only_reports_wide_ranges(golden_run, firms_dir):
    """A Tier-0-only run says its ranges are wide, and the part of the spread that data can remove (imputation draws
    with parameters held at their defaults) is wider than the full-tier run's, in dollars and per dollar of plan value.

    The total P10-P90 spread is not compared (rewritten 29 Oct 2026, CHANGELOG.md, engine pass): it adds parameter and
    outcome risk that more firm data does not remove, it scales with the plan's value, which differs between the two
    runs, and at the golden sample sizes (five parameter draws) its ordering changes with the seed."""
    from autofrontier import config, economics as E, optimize as O, plans, priors, regimes, risk
    t0, out = golden_run("tier0")
    assert t0["inputs"]["tier_reached"] == 0
    md = (out / "report.md").read_text(encoding="utf-8")
    assert "only Tier 0 inputs" in md and "Ranges are wide" in md
    js = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert js["data_quality"]["label"] == "wide"
    p = config.load_params()
    pri = priors.load_priors(config.find_data_dir())
    widths, rel = {}, {}
    for nm in ("synthetic", "tier0"):
        ing = ingest.ingest_folder(firms_dir / nm, pri)
        firm = impute.build_firm(ing, pri, p)
        econ = E.build_econ(firm, p)
        reg = regimes.make_regime("public", p, firm)
        prog = O.make_program(plans.PlanBuilder(econ).build(), econ, reg, p)
        sol = O.solve(prog, method="heuristic")
        mc = risk.run_monte_carlo(firm, ing, pri, p, sol, prog, econ, reg, seed=1, n_imp=16, n_out=20, param_uncertainty=False)
        widths[nm] = mc["imputation_value"]["P90"] - mc["imputation_value"]["P10"]
        rel[nm] = widths[nm] / max(abs(float(sol.value)), 1e-9)
    assert widths["tier0"] > widths["synthetic"]
    assert rel["tier0"] > rel["synthetic"]


@pytest.fixture(scope="module")
def full_run(firms_dir, tmp_path_factory):
    out = tmp_path_factory.mktemp("full")
    t0 = time.time()
    res = pipeline.run(firms_dir / "synthetic", out)
    return res, out, time.time() - t0


def test_full_synthetic_run_under_two_minutes(full_run):
    res, out, secs = full_run
    assert secs < 120, f"full synthetic run took {secs:.0f} s"
    assert res["gsa"] is not None and res["gsa"]["sobol"] is not None


def test_report_contract(full_run, params):
    res, out, _ = full_run
    md = (out / "report.md").read_text(encoding="utf-8")
    for i, title in enumerate(["Executive summary", "Vision", "Product strategy", "Roadmap", "People", "Risk",
                               "AI failure modes and controls", "Ownership-regime view", "Security and compliance",
                               "Sensitivity", "Breakpoints", "Confidence and data gaps", "Assumptions",
                               "Data sources and attributions"], 1):
        assert re.search(rf"^## {i}\. {re.escape(title)}", md, re.M), f"missing section {i}. {title}"
    assert DECISION_SUPPORT in md and REQUIRED_NOTICE in md
    assert "—" not in md and "–" not in md, "the report must not use em or en dashes"
    assert "O*NET 31.0" in md and "CC BY 4.0" in md
    assert "Wave 0" in md
    d = pd.read_csv(out / "class_d_parameters.csv")
    keys = set(params.scenario_parameters(("d",)))
    assert keys <= set(d.key), f"class d parameters missing from the assumptions: {sorted(keys - set(d.key))[:5]}"
    assert {"range", "affects"} <= set(d.columns) and d.range.notna().all()
    js = json.loads((out / "report.json").read_text(encoding="utf-8"))
    assert js["notice"] == REQUIRED_NOTICE and js["decision_support"] == DECISION_SUPPORT
    assert js["version"]["seed"] is not None and js["version"]["hashes"]
    rec = js["recommendations"]
    assert rec and "wave 0" in rec[0]["title"].lower()


def test_no_metr_run_level_data_in_outputs(full_run):
    """METR's run-level data has no license: outputs carry only fitted parameters with a citation."""
    res, out, _ = full_run
    for f in out.rglob("*"):
        if f.is_file() and f.suffix in (".csv", ".json", ".md"):
            text = f.read_text(encoding="utf-8", errors="ignore")
            assert "n_runs" not in text and "run_id" not in text, f"{f.name} looks like run-level METR data"


@pytest.mark.parametrize("n", [100, 100_000])
def test_size_generator(tmp_path, n):
    from autofrontier import config, priors
    t0 = time.time()
    out = synthetic.generate(tmp_path / f"n{n}", employees=n, seed=3)
    assert abs(out["fte"] / n - 1) < 0.25 and len(out["files"]) >= 5
    pr = priors.load_priors(config.find_data_dir())
    ing = ingest.ingest_folder(tmp_path / f"n{n}", pr)
    firm = impute.build_firm(ing, pr, config.load_params())
    assert len(firm.units) > 0
    assert time.time() - t0 < 120


def test_golden_independent_of_hash_seed(tmp_path):
    """The small firm reproduces its golden snapshot in a fresh process with another PYTHONHASHSEED (no result may
    depend on set iteration order)."""
    import os
    import subprocess
    import sys
    from pathlib import Path
    src = Path(__file__).resolve().parents[1] / "src"
    code = ("import json,sys; sys.path.insert(0, %r)\n"
            "from autofrontier import pipeline, synthetic\n"
            "from autofrontier.qa import GOLDEN_FIRMS, GOLDEN_RUN, snapshot\n"
            "synthetic.generate(%r, **GOLDEN_FIRMS['small'])\n"
            "r = pipeline.run(%r, None, write=False, **GOLDEN_RUN)\n"
            "print(json.dumps(snapshot(r)))\n") % (str(src), str(tmp_path / "small"), str(tmp_path / "small"))
    env = dict(os.environ, PYTHONHASHSEED="7", PYTHONDONTWRITEBYTECODE="1")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, timeout=600, check=True)
    snap = json.loads(out.stdout.strip().splitlines()[-1])
    old = json.loads(golden_path("small").read_text(encoding="utf-8"))
    assert compare(snap, old) == []
