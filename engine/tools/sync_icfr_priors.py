# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Regenerate the engine's fallback ICFR scope priors from the data contract (spec 24.4).

The data contract (data/tasks/processes.csv icfr_* columns and process_activities.csv icfr_* and typical_systems
columns, built by code/data_part2/07_processes.py) is the single source. The engine ships a snapshot in
src/autofrontier/priors/icfr_scope.csv and icfr_steps.csv, used only when the data files lack the columns;
tests/test_icfr_contract.py fails when the snapshot and the data disagree.

Run from engine/:   python tools/sync_icfr_priors.py"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ENGINE = Path(__file__).resolve().parents[1]
DATA = ENGINE.parent / "data" / "tasks"
PRI = ENGINE / "src" / "autofrontier" / "priors"
SCOPE_COLS = ["process_id", "process_name", "icfr_scope", "icfr_basis"]
STEP_COLS = ["process_id", "step", "dwa_id", "step_name", "icfr_step", "icfr_condition", "icfr_channel", "icfr_basis",
             "icfr_source", "typical_systems", "financial_system_written"]


def snapshot() -> tuple[pd.DataFrame, pd.DataFrame]:
    pr = pd.read_csv(DATA / "processes.csv", dtype=str)
    pa = pd.read_csv(DATA / "process_activities.csv", dtype=str)
    if "icfr_scope" not in pr.columns or "icfr_step" not in pa.columns:
        raise SystemExit("the data contract has no ICFR columns yet; nothing to sync")
    sc = pr[[c for c in SCOPE_COLS if c in pr.columns]].copy()
    st = pa[[c for c in STEP_COLS if c in pa.columns]].copy()
    for c in STEP_COLS:
        if c not in st.columns:
            st[c] = ""
    return sc, st[STEP_COLS]


def main():
    sc, st = snapshot()
    sc.to_csv(PRI / "icfr_scope.csv", index=False)
    st.to_csv(PRI / "icfr_steps.csv", index=False)
    print(f"wrote {PRI / 'icfr_scope.csv'} ({len(sc)} processes) and {PRI / 'icfr_steps.csv'} ({len(st)} steps)")


if __name__ == "__main__":
    sys.exit(main())
