# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Input validation and the command line (spec 19.1): actionable messages that say what to fix, and clear exit
codes (0 success, 2 usage or parameter error, 3 input error, 4 runtime error, 5 refused output path)."""
import shutil

import pandas as pd
import pytest

from autofrontier import REQUIRED_NOTICE, __version__, cli, config, ingest, priors as PR
from autofrontier.ingest import InputError


@pytest.fixture(scope="module")
def pri():
    return PR.load_priors(config.find_data_dir())


def _tier0(folder, **upd):
    fin = pd.read_csv(folder / "tier0_financials.csv", dtype=str)
    for k, v in upd.items():
        fin.loc[fin.iloc[:, 0] == k, fin.columns[1]] = str(v)
    fin.to_csv(folder / "tier0_financials.csv", index=False)


def test_missing_folder_and_tier0(tmp_path, pri):
    with pytest.raises(InputError, match="autofrontier init"):
        ingest.ingest_folder(tmp_path / "nope", pri)
    (tmp_path / "empty").mkdir()
    with pytest.raises(InputError, match="tier0_financials.csv"):
        ingest.ingest_folder(tmp_path / "empty", pri)


def test_malformed_tier0_names_the_field(tmp_path, firms_dir, pri):
    f = tmp_path / "bad"
    shutil.copytree(firms_dir / "small", f)
    _tier0(f, revenue=-5)
    with pytest.raises(InputError) as e:
        ingest.ingest_folder(f, pri)
    assert "revenue" in str(e.value) and "Required fields" in str(e.value)


def test_revenue_in_thousands_detected(tmp_path, firms_dir, pri):
    f = tmp_path / "thousands"
    shutil.copytree(firms_dir / "small", f)
    fin = pd.read_csv(f / "tier0_financials.csv")
    rev = float(fin.loc[fin.iloc[:, 0] == "revenue"].iloc[0, 1])
    _tier0(f, revenue=rev / 1000.0)
    with pytest.raises(InputError, match="thousands"):
        ingest.ingest_folder(f, pri)


def test_cli_version_prints_notice(capsys):
    assert cli.main(["--version"]) == cli.EXIT_OK
    out = capsys.readouterr().out
    assert __version__ in out and REQUIRED_NOTICE in out


def test_cli_exit_codes(tmp_path, firms_dir, capsys):
    assert cli.main([]) == cli.EXIT_USAGE
    assert cli.main(["run"]) == cli.EXIT_USAGE                                   # missing arguments
    assert cli.main(["run", str(tmp_path / "missing"), "--out", str(tmp_path / "o")]) == cli.EXIT_USAGE
    (tmp_path / "empty").mkdir()
    assert cli.main(["run", str(tmp_path / "empty"), "--out", str(tmp_path / "o2"), "--quiet"]) == cli.EXIT_INPUT
    err = capsys.readouterr().err
    assert "tier0_financials" in err
    assert cli.main(["run", str(firms_dir / "small"), "--out", str(tmp_path / "o3"), "--set", "no.such=1", "--quiet"]) == cli.EXIT_USAGE
    assert "unknown parameter" in capsys.readouterr().err
    assert cli.main(["run", str(firms_dir / "small"), "--out", str(tmp_path / "o4"), "--scenario", "no_such", "--quiet"]) == cli.EXIT_USAGE
    assert cli.main(["run", str(firms_dir / "small"), "--out", str(firms_dir / "small" / "x"), "--quiet"]) == cli.EXIT_PATH


def test_cli_init_writes_templates(tmp_path):
    assert cli.main(["init", str(tmp_path / "tpl")]) == cli.EXIT_OK
    files = {p.name for p in (tmp_path / "tpl").iterdir()}
    assert "README.md" in files and any(n.startswith("tier0_financials") for n in files)
    assert any(n.startswith("tier3_org") for n in files) and any(n.startswith("tier3_jurisdictions") for n in files)
    org = next(p for p in (tmp_path / "tpl").iterdir() if p.name.startswith("tier3_org") and p.suffix == ".csv")
    text = org.read_text()
    for k in ("decisions_per_year", "change_capacity_fte", "affected_fte_per_change_manager", "benefit_realization_past"):
        assert k in text                        # templates ask for the firm's class d organizational values


def test_cli_lists(capsys):
    assert cli.main(["scenarios"]) == cli.EXIT_OK
    assert "central" in capsys.readouterr().out
    assert cli.main(["params", "--grounding", "d"]) == cli.EXIT_OK
    assert "org.e_PO" in capsys.readouterr().out
