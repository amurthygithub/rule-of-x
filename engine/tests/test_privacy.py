# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Privacy guards (spec 19.1): no network access during a run, writes only inside the chosen output folder, path
traversal refused, spreadsheet formula injection neutralized, and no input data in the run log."""
import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from autofrontier import cli
from autofrontier.safeio import OutputDir, UnsafePathError, neutralize_cell, neutralize_frame


def _tree(folder: Path) -> dict:
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.rglob("*")) if p.is_file()}


def test_run_without_network_writes_only_to_output(golden_run, firms_dir):
    before = _tree(firms_dir / "synthetic")
    res, out = golden_run("synthetic")              # runs inside NoNetwork: any socket use raises
    assert _tree(firms_dir / "synthetic") == before, "the run changed the input folder"
    files = [p for p in out.rglob("*") if p.is_file()]
    assert files and all(out in p.parents for p in files)
    written = json.loads((out / "manifest.json").read_text())["files"] if (out / "manifest.json").exists() else None
    if written is not None:
        assert set(written) <= {str(p.relative_to(out)) for p in files}
    for name in ("report.md", "report.json", "run_log.txt"):
        assert (out / name).is_file()


def test_run_log_has_no_input_data(golden_run, firms_dir):
    res, out = golden_run("synthetic")
    log = (out / "run_log.txt").read_text(encoding="utf-8")
    folder = firms_dir / "synthetic"
    secrets = set()
    roster = pd.read_csv(folder / "tier2_roster.csv")
    secrets |= {str(t) for t in roster.title.dropna().unique() if len(str(t)) > 4}
    if (folder / "tier3_vendors.csv").exists():
        secrets |= {str(v) for v in pd.read_csv(folder / "tier3_vendors.csv").vendor.dropna().unique() if len(str(v)) > 3}
    if (folder / "tier3_jurisdictions.csv").exists():
        secrets |= {str(v) for v in pd.read_csv(folder / "tier3_jurisdictions.csv").site.dropna().unique() if len(str(v)) > 3}
    fin = pd.read_csv(folder / "tier0_financials.csv")
    name_row = fin[fin.iloc[:, 0].astype(str) == "company_name"]
    if len(name_row):
        secrets.add(str(name_row.iloc[0, 1]))
    leaked = sorted(s for s in secrets if s in log)
    assert not leaked, f"input values in run_log.txt: {leaked[:5]}"


def test_output_dir_refuses_path_traversal(tmp_path):
    od = OutputDir(tmp_path / "out")
    for bad in ("../escape.txt", "a/../../escape.txt", str(tmp_path / "elsewhere.txt"), "/etc/passwd"):
        with pytest.raises(UnsafePathError):
            od.path(bad)
    outside = tmp_path / "outside"
    outside.mkdir()
    (tmp_path / "out" / "link").symlink_to(outside, target_is_directory=True)
    with pytest.raises(UnsafePathError):
        od.write_text("link/x.txt", "no")
    assert not (outside / "x.txt").exists()


def test_formula_injection_neutralized(tmp_path):
    for v in ("=HYPERLINK(\"http://x\")", "+1+1", "-2+3", "@SUM(A1)", "\t=1", "\r=1"):
        assert str(neutralize_cell(v)).startswith("'")
    assert neutralize_cell("plain") == "plain" and neutralize_cell(3.5) == 3.5
    df = pd.DataFrame({"title": ["=cmd|' /C calc'!A0", "Analyst"], "n": [1, 2]})
    assert neutralize_frame(df).title.iloc[0].startswith("'")
    od = OutputDir(tmp_path / "out")
    od.write_csv("t.csv", df)
    text = (tmp_path / "out" / "t.csv").read_text()
    assert "'=cmd" in text and "\n=cmd" not in text


def test_cli_refuses_output_inside_input(firms_dir, capsys):
    code = cli.main(["run", str(firms_dir / "small"), "--out", str(firms_dir / "small" / "out"), "--quick", "--quiet"])
    assert code == cli.EXIT_PATH
    assert not (firms_dir / "small" / "out").exists()


def test_no_telemetry_or_network_libraries_imported():
    """The engine's modules import no network client libraries."""
    import ast
    src = Path(__file__).resolve().parents[1] / "src" / "autofrontier"
    banned = {"requests", "urllib3", "httpx", "aiohttp", "http.client", "urllib.request", "socket", "smtplib", "ftplib"}
    found = []
    for f in src.glob("*.py"):
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                ([node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
            found += [f"{f.name}: {n}" for n in names if n in banned or n.split(".")[0] in {"requests", "httpx", "aiohttp"}]
    assert not found, found
