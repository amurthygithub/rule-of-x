# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Traceability (spec 19.1): every formula names the paper label it implements, the spec section, the notes
section and its status, and engine/TRACEABILITY.md is up to date (tools/traceability.py)."""
import importlib.util
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]


def _tool(name):
    spec = importlib.util.spec_from_file_location(name, ENGINE / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_formula_is_tagged():
    rows = _tool("traceability").formula_rows()
    assert len(rows) > 200
    bad = [r["name"] for r in rows if not (r["implements"] and r["spec"] and r["notes"] and r["status"])]
    assert not bad, f"formulas without Implements/Spec/Notes/Status: {bad}"
    assert {r["status"] for r in rows} <= {"theory", "spec", "provisional", "superseded"}


def test_traceability_file_is_current():
    text = (ENGINE / "TRACEABILITY.md").read_text(encoding="utf-8")
    assert text == _tool("traceability").render(), "TRACEABILITY.md is out of date: run python tools/traceability.py"
