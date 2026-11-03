# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Safe output (spec 19.2 item 9). Every file the engine writes goes through OutputDir, which
  - resolves each path inside the chosen output folder and refuses absolute paths, '..' and symlinks that
    lead outside it;
  - neutralizes spreadsheet formula injection: a text cell that starts with =, +, -, @, tab or carriage
    return gets a leading apostrophe in CSV and XLSX outputs, unless the whole cell is a plain number;
  - never logs input values (only file names and counts)."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_FORMULA_START = ("=", "+", "-", "@", "\t", "\r")
_NUMBER = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")


class UnsafePathError(ValueError):
    """An output path would leave the output folder."""


def neutralize_cell(v: Any) -> Any:
    """Prefix an apostrophe to text that a spreadsheet would read as a formula."""
    if isinstance(v, str) and v.startswith(_FORMULA_START) and not _NUMBER.match(v.strip()):
        return "'" + v
    return v


def neutralize_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [neutralize_cell(str(c)) for c in out.columns]
    for c in out.columns:
        if out[c].dtype == object or pd.api.types.is_string_dtype(out[c]):
            out[c] = out[c].map(neutralize_cell)
    return out


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.ndarray):
        return [_json_default(x) if isinstance(x, (np.generic, np.ndarray)) else x for x in o.tolist()]
    if isinstance(o, (set, tuple)):
        return list(o)
    if isinstance(o, Path):
        return str(o)
    if isinstance(o, pd.Timestamp):
        return o.isoformat()
    return str(o)


def clean_json(o: Any) -> Any:
    """Replace NaN and inf by None, recursively, so the JSON is strict (no NaN tokens)."""
    if isinstance(o, pd.DataFrame):
        return clean_json(o.to_dict(orient="records"))
    if isinstance(o, pd.Series):
        return clean_json(o.to_dict())
    if isinstance(o, dict):
        return {str(k): clean_json(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean_json(v) for v in o]
    if isinstance(o, np.ndarray):
        return clean_json(o.tolist())
    if isinstance(o, (float, np.floating)):
        return None if not math.isfinite(float(o)) else float(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


class OutputDir:
    """The only way the engine writes files."""

    def __init__(self, root: str | Path, create: bool = True):
        root = Path(root).expanduser()
        if create:
            root.mkdir(parents=True, exist_ok=True)
        if not root.is_dir():
            raise UnsafePathError(f"output folder {root} is not a directory")
        self.root = root.resolve()
        self.written: list[str] = []

    def path(self, rel: str | Path) -> Path:
        rel = Path(rel)
        if rel.is_absolute() or any(part == ".." for part in rel.parts):
            raise UnsafePathError(f"refusing to write {rel}: outputs must stay inside {self.root}")
        target = (self.root / rel).resolve()
        if target != self.root and self.root not in target.parents:
            raise UnsafePathError(f"refusing to write {rel}: it resolves outside {self.root}")
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def _record(self, p: Path):
        self.written.append(str(p.relative_to(self.root)))

    def write_text(self, rel: str | Path, text: str) -> Path:
        p = self.path(rel)
        p.write_text(text, encoding="utf-8")
        self._record(p)
        return p

    def write_json(self, rel: str | Path, obj: Any) -> Path:
        return self.write_text(rel, json.dumps(clean_json(obj), indent=1, default=_json_default, allow_nan=False))

    def write_csv(self, rel: str | Path, df: pd.DataFrame) -> Path:
        p = self.path(rel)
        neutralize_frame(df).to_csv(p, index=False)
        self._record(p)
        return p

    def write_xlsx(self, rel: str | Path, sheets: dict[str, pd.DataFrame]) -> Path:
        p = self.path(rel)
        with pd.ExcelWriter(p, engine="openpyxl") as xw:
            for name, df in sheets.items():
                neutralize_frame(df).to_excel(xw, sheet_name=str(name)[:31], index=False)
        self._record(p)
        return p
