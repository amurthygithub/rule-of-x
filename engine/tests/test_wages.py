# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Data consistency of wages: no wage constant in engine/src may differ from data/tasks/occupations.csv (OEWS,
the vintage recorded in its oews_vintage column)."""
import ast
import re
from pathlib import Path

import pandas as pd
import pytest
import yaml

from autofrontier import config, impute

SRC = Path(__file__).resolve().parents[1] / "src" / "autofrontier"
OCC = Path(__file__).resolve().parents[2] / "data" / "tasks" / "occupations.csv"


@pytest.fixture(scope="module")
def occ():
    if not OCC.is_file():
        pytest.skip("data/tasks/occupations.csv not found")
    return pd.read_csv(OCC, dtype={"soc": str}).set_index("soc")


def test_no_wage_literals_in_source(occ):
    """No numeric literal of wage size (20,000 to 500,000) on a line that mentions a wage, salary or pay, unless it
    equals an OEWS median or mean in occupations.csv (template examples)."""
    oews = set(pd.to_numeric(occ.wage_median, errors="coerce").dropna()) | set(pd.to_numeric(occ.wage_mean, errors="coerce").dropna())
    bad = []
    for f in SRC.glob("*.py"):
        text = f.read_text(encoding="utf-8")
        lines = text.splitlines()
        for node in ast.walk(ast.parse(text)):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                line = lines[node.lineno - 1].split("#", 1)[0]
                if 20_000 <= float(node.value) <= 500_000 and float(node.value) not in oews and \
                        re.search(r"wage|salary|_comp\b|annual_pay", line, re.I):
                    bad.append(f"{f.name}:{node.lineno}: {node.value}")
    assert not bad, "hard-coded wages (read occupations.csv instead): " + "; ".join(bad)


def test_wage_defaults_match_occupations(occ):
    """Every wage default in defaults.yaml equals the OEWS value it cites."""
    d = yaml.safe_load((SRC / "defaults.yaml").read_text(encoding="utf-8"))
    for sec, leaves in d.items():
        for k, leaf in (leaves or {}).items():
            if "wage" not in k or not isinstance(leaf, dict) or not isinstance(leaf.get("value"), (int, float)) \
                    or float(leaf["value"]) < 1000:          # multipliers such as review.wage_premium are not wages
                continue
            m = re.search(r"(\d{2}-\d{4})", str(leaf.get("source", "")))
            assert m, f"{sec}.{k}: a wage default must cite its SOC code"
            row = occ.loc[m.group(1)]
            assert float(leaf["value"]) == float(row.wage_median), f"{sec}.{k} {leaf['value']} vs OEWS {row.wage_median}"
            assert float(leaf["range"][1]) in (float(row.wage_median), float(row.wage_mean))


def test_role_wages_read_occupations(occ):
    p = config.load_params()
    w, src = impute.role_wages(occ, p)
    for role, soc in impute.ROLE_SOCS.items():
        assert w[role] == float(occ.loc[soc, "wage_median"])
    assert "OEWS" in src and str(occ.oews_vintage.dropna().iloc[0]) in src
