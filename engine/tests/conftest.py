# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Shared fixtures: parameters, synthetic firms (generated into a temporary folder), quick pipeline runs, a socket
guard, and a loader for the theory's reference implementations in code/verify_part2_*.py (imported by path,
functions only: the scripts run their checks at module level, so only imports, constant assignments and function
definitions are executed)."""
from __future__ import annotations

import ast
import socket
import sys
from pathlib import Path

import numpy as np
import pytest

sys.dont_write_bytecode = True          # the engine writes only to its output folder; tests write only to tmp_path
ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
sys.path.insert(0, str(ENGINE / "src"))

from autofrontier import config  # noqa: E402

_SAFE_CALLS = {"dict", "float", "int", "math.log", "math.exp", "math.sqrt", "np.random.default_rng", "np.array", "range", "list",
               "tuple"}


def _call_name(node) -> str:
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        parts = []
        while isinstance(f, ast.Attribute):
            parts.append(f.attr)
            f = f.value
        if isinstance(f, ast.Name):
            parts.append(f.id)
        return ".".join(reversed(parts))
    return ""


def load_reference(name: str) -> dict:
    """Functions of code/<name>.py without running its checks."""
    path = REPO / "code" / f"{name}.py"
    if not path.is_file():
        pytest.skip(f"reference script {path} not found")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    ns: dict = {"__name__": f"ref_{name}", "__file__": str(path)}
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            try:
                exec(compile(ast.Module([node], []), str(path), "exec"), ns)
            except ImportError:
                pass
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            try:
                exec(compile(ast.Module([node], []), str(path), "exec"), ns)
            except Exception:
                pass
        elif isinstance(node, ast.Assign):
            calls = [n for n in ast.walk(node.value) if isinstance(n, ast.Call)]
            if all(_call_name(c) in _SAFE_CALLS for c in calls):
                try:
                    exec(compile(ast.Module([node], []), str(path), "exec"), ns)
                except Exception:
                    pass
    # second pass: functions whose defaults needed later constants
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name not in ns:
            try:
                exec(compile(ast.Module([node], []), str(path), "exec"), ns)
            except Exception:
                pass
    return ns


@pytest.fixture(scope="session")
def params():
    return config.load_params()


@pytest.fixture(scope="session")
def rng():
    return np.random.default_rng(12345)


@pytest.fixture(scope="session")
def firms_dir(tmp_path_factory):
    from autofrontier import synthetic
    from autofrontier.qa import GOLDEN_FIRMS
    root = tmp_path_factory.mktemp("firms")
    for name, kw in GOLDEN_FIRMS.items():
        synthetic.generate(root / name, **kw)
    synthetic.generate(root / "tier0", employees=3200, seed=0, tiers=(0,), products=False)
    return root


@pytest.fixture(scope="session")
def built(firms_dir, params):
    """The synthetic firm built from its inputs, its economics and a solved public program."""
    from autofrontier import economics as E, impute, ingest, optimize as O, plans, priors, regimes
    pri = priors.load_priors(config.find_data_dir())
    ing = ingest.ingest_folder(firms_dir / "synthetic", pri)
    firm = impute.build_firm(ing, pri, params)
    econ = E.build_econ(firm, params)
    cols = plans.PlanBuilder(econ).build()
    reg = regimes.make_regime("public", params, firm)
    prog = O.make_program(cols, econ, reg, params)
    sol = O.solve(prog, method="heuristic")
    return {"priors": pri, "ingest": ing, "firm": firm, "econ": econ, "cols": cols, "regime": reg, "prog": prog, "sol": sol}


_RUNS: dict = {}


def quick_run(folder, out, n_imp: int = 6, n_out: int = 60, **kw):
    """A quick pipeline run (fewer scenarios and draws, no global sensitivity), cached per arguments."""
    from autofrontier import pipeline
    key = (str(folder), str(out), n_imp, n_out, tuple(sorted((k, str(v)) for k, v in kw.items())))
    if key not in _RUNS:
        _RUNS[key] = pipeline.run(folder, out, quick=True, n_imp=n_imp, n_out=n_out, **kw)
    return _RUNS[key]


@pytest.fixture()
def no_network(monkeypatch):
    """Any attempt to open a network connection fails the test."""
    def guard(*a, **k):
        raise AssertionError("network access attempted")
    monkeypatch.setattr(socket.socket, "connect", guard)
    monkeypatch.setattr(socket.socket, "connect_ex", guard)
    monkeypatch.setattr(socket, "create_connection", guard)
    monkeypatch.setattr(socket, "getaddrinfo", guard)
    yield


class NoNetwork:
    """Context manager: any attempt to open a network connection raises (used around whole engine runs)."""

    def __enter__(self):
        def guard(*a, **k):
            raise AssertionError("network access attempted")
        self._saved = (socket.socket.connect, socket.socket.connect_ex, socket.create_connection, socket.getaddrinfo)
        socket.socket.connect = guard
        socket.socket.connect_ex = guard
        socket.create_connection = guard
        socket.getaddrinfo = guard
        return self

    def __exit__(self, *exc):
        socket.socket.connect, socket.socket.connect_ex, socket.create_connection, socket.getaddrinfo = self._saved
        return False


@pytest.fixture(scope="session")
def golden_run(firms_dir, tmp_path_factory):
    """get(name) -> (result, output folder): a run of a golden firm with the golden settings, written to a fresh
    temporary output folder with network access blocked; cached for the session."""
    from autofrontier import pipeline
    from autofrontier.qa import GOLDEN_RUN
    cache: dict = {}

    def get(name: str, again: bool = False):
        key = (name, again)
        if key not in cache:
            out = tmp_path_factory.mktemp(f"out_{name}{'_again' if again else ''}")
            with NoNetwork():
                res = pipeline.run(firms_dir / name, out, **GOLDEN_RUN)
            cache[key] = (res, out)
        return cache[key]
    return get
