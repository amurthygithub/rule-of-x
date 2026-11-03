# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Snapshot Paper 1's margin-gap decomposition (Table tab:gap; notes/gap_decomposition.json, written by
code/decompose_gap.py) into src/autofrontier/priors/frontier_gap_bands.csv for the lever map's position binding
constraint (notes/playbook_engine_spec.md 2.5). Growth bands: 0-10, 10-20, 20-30, 30-40, 40-60 percent.

    python tools/sync_gap_bands.py"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ENGINE = Path(__file__).resolve().parents[1]
SRC = ENGINE.parent / "notes" / "gap_decomposition.json"
OUT = ENGINE / "src" / "autofrontier" / "priors" / "frontier_gap_bands.csv"
BANDS = [(0.0, 0.10), (0.10, 0.20), (0.20, 0.30), (0.30, 0.40), (0.40, 0.60)]


def snapshot() -> pd.DataFrame:
    d = json.loads(SRC.read_text(encoding="utf-8"))
    rows = []
    for b in d["bands"]:
        lo, hi = BANDS[int(b["band"])]
        rows.append({"band": int(b["band"]), "g_low": lo, "g_high": hi, "n_top": b["n_top"], "n_mid": b["n_mid"],
                     **{k: b[k] for k in ("top_gm", "top_sms", "top_rds", "top_gas", "top_oth", "top_m_op", "gap",
                                         "d_gm", "d_sms", "d_rds", "d_gas", "d_oth")},
                     "source": "Paper 1 Table tab:gap (notes/gap_decomposition.json; code/decompose_gap.py), core sample 2010-2025"})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    OUT.write_text(snapshot().to_csv(index=False), encoding="utf-8")
    print(f"wrote {OUT}")
