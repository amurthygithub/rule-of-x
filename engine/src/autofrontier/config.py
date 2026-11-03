# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Parameters: defaults.yaml with provenance, values pulled from the data agent's params.yaml where a default
links to it, scenario and regime overlays, and command-line overrides. No network access."""
from __future__ import annotations

import copy
import datetime as _dt
import hashlib
import math
import os
import re
from pathlib import Path
from typing import Any

import yaml

PKG_DIR = Path(__file__).resolve().parent
DEFAULTS_PATH = PKG_DIR / "defaults.yaml"
PRIORS_DIR = PKG_DIR / "priors"
ENGINE_DIR = PKG_DIR.parent.parent          # engine/ in the repository layout
REPO_DIR = ENGINE_DIR.parent                # the paper repository


_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
_YAML_CACHE: dict = {}


def read_yaml(path: Path) -> Any:
    """Safe YAML load with the C loader when available, cached by path and modification time (params.yaml is
    large and read by several modules)."""
    path = Path(path)
    key = (str(path.resolve()), path.stat().st_mtime_ns)
    if key not in _YAML_CACHE:
        with open(path, encoding="utf-8") as fh:
            _YAML_CACHE[key] = yaml.load(fh, Loader=_LOADER) or {}
    return copy.deepcopy(_YAML_CACHE[key])


class ConfigError(ValueError):
    """A parameter file or override is invalid. The message says what to fix."""


class Section:
    """Attribute access to one section's values: p.finance.r."""

    def __init__(self, name: str, values: dict[str, Any]):
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_v", values)

    def __getattr__(self, k: str) -> Any:
        if k.startswith("__") or k in ("_v", "_name"):
            raise AttributeError(k)
        try:
            return self._v[k]
        except KeyError as e:
            raise AttributeError(f"unknown parameter {self._name}.{k}") from e

    def __setattr__(self, k: str, v: Any) -> None:
        raise AttributeError("use Params.set() so that the change is logged")

    def __getstate__(self):
        return {"_name": self._name, "_v": self._v}

    def __setstate__(self, s):
        object.__setattr__(self, "_name", s["_name"])
        object.__setattr__(self, "_v", s["_v"])

    def keys(self):
        return self._v.keys()


class Params:
    """Engine parameters. p.finance.r is a value; p.meta('finance.r') its provenance (source, range, status)."""

    def __init__(self, tree: dict[str, dict[str, dict[str, Any]]]):
        self._tree = tree
        self._sections = {s: Section(s, {k: leaf.get("value") for k, leaf in d.items()}) for s, d in tree.items()}
        self.overrides: list[dict[str, Any]] = []
        self.params_log: list[dict[str, Any]] = []

    def __getattr__(self, s: str) -> Section:
        if s.startswith("_"):
            raise AttributeError(s)
        try:
            return self._sections[s]
        except KeyError as e:
            raise AttributeError(f"unknown parameter section {s}") from e

    def get(self, dotted: str) -> Any:
        s, k = dotted.split(".", 1)
        if s not in self._sections or k not in self._sections[s]._v:
            raise ConfigError(f"unknown parameter '{dotted}'. Run `autofrontier params` to list valid keys.")
        return self._sections[s]._v[k]

    def has(self, dotted: str) -> bool:
        s, _, k = dotted.partition(".")
        return s in self._sections and k in self._sections[s]._v

    def meta(self, dotted: str) -> dict[str, Any]:
        s, k = dotted.split(".", 1)
        return self._tree[s][k]

    def keys(self) -> list[str]:
        return [f"{s}.{k}" for s, d in self._tree.items() for k in d]

    def set(self, dotted: str, value: Any, origin: str = "override") -> None:
        """Change a parameter and log the change (scenario, regime or user override)."""
        if not self.has(dotted):
            raise ConfigError(f"unknown parameter '{dotted}'. Run `autofrontier params` to list valid keys.")
        s, k = dotted.split(".", 1)
        old = self._sections[s]._v[k]
        self._sections[s]._v[k] = value
        self.overrides.append({"key": dotted, "old": old, "new": value, "origin": origin})

    def set_range(self, dotted: str, rng, origin: str = "override", value_basis: str | None = None) -> None:
        """Change a parameter's range (firm-specific priors such as the industry k), logged like set()."""
        s, k = dotted.split(".", 1)
        old = self._tree[s][k].get("range")
        self._tree[s][k]["range"] = [float(rng[0]), float(rng[1])]
        if value_basis:
            self._tree[s][k]["basis"] = value_basis
            self._tree[s][k]["assumed"] = False
        self.overrides.append({"key": dotted + " (range)", "old": old, "new": list(rng), "origin": origin})

    def last_origin(self, dotted: str) -> str | None:
        """Origin of the most recent change to a parameter (None if it was never changed)."""
        for o in reversed(self.overrides):
            if o["key"] == dotted:
                return str(o["origin"])
        return None

    def copy(self) -> "Params":
        new = Params(copy.deepcopy(self._tree))
        for s, sec in self._sections.items():
            new._sections[s] = Section(s, copy.deepcopy(sec._v))
        new.overrides = list(self.overrides)
        new.params_log = list(self.params_log)
        return new

    def range(self, dotted: str):
        return self.meta(dotted).get("range")

    def table(self) -> list[dict[str, Any]]:
        """One row per parameter for the report's assumptions section and TRACEABILITY.md."""
        rows = []
        for s, d in self._tree.items():
            for k, leaf in d.items():
                rows.append({
                    "key": f"{s}.{k}", "value": self._sections[s]._v[k], "range": leaf.get("range"),
                    "status": "assumed" if leaf.get("assumed") else "sourced",
                    "grounding": grounding_of(leaf),
                    "source": leaf.get("source") or leaf.get("basis") or "",
                    "origin": leaf.get("origin", "defaults.yaml"), "flag": leaf.get("flag", ""),
                    "section": leaf.get("section", ""), "note": leaf.get("note", ""), "limit": bool(leaf.get("limit")),
                })
        return rows


    def grounding(self, dotted: str) -> str:
        return grounding_of(self.meta(dotted))

    def scenario_parameters(self, classes=("d",)) -> list[str]:
        """Numeric scalar parameters of the given grounding classes that carry a usable [low, high] range: the
        dimensions over which class-d dependent outputs must be reported (spec 21.1, 24.2)."""
        out = []
        for key in self.keys():
            leaf = self.meta(key)
            if grounding_of(leaf) not in classes:
                continue
            v, rng = self.get(key), leaf.get("range")
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                continue
            if not (isinstance(rng, (list, tuple)) and len(rng) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in rng)):
                continue
            if rng[1] - rng[0] <= 1e-12 * max(1.0, abs(rng[1])):
                continue
            out.append(key)
        return out


def grounding_of(leaf: dict) -> str:
    """Grounding class of a parameter (spec 21.1): a, b, c, d, or setting/policy; linked leaves inherit the class
    of their params.yaml block; a sourced leaf without a class counts as a, an assumed one as d."""
    g = leaf.get("grounding")
    if g:
        return str(g)
    return "d" if leaf.get("assumed") else "a"


# -------------------------------------------------------------------------------------------------
# params.yaml linkage
# -------------------------------------------------------------------------------------------------
def _date_to_year(v: Any) -> float:
    if isinstance(v, (int, float)):
        return float(v)
    d = v if isinstance(v, (_dt.date, _dt.datetime)) else _dt.date.fromisoformat(str(v)[:10])
    start = _dt.date(d.year, 1, 1)
    return round(d.year + (d - start).days / 365.25, 4)


def _gwa_class_map(v: dict) -> dict:
    out = {}
    for k, val in (v or {}).items():
        m = re.search(r"(4\.A\.\d(?:\.[a-z])?)", str(k))
        if m:
            out[m.group(1)] = 1.0 if val is None else float(val)
    return out


def to_continuous(r_annual: Any) -> float:
    """Continuous rate of an annual source rate, ln(1 + r) (theory convention: continuous compounding). Every annual
    rate in params.yaml enters the engine through this helper (transform: to_continuous)."""
    return math.log1p(float(r_annual))


TRANSFORMS = {
    None: lambda v: v,
    "to_continuous": to_continuous,
    "days_to_years": lambda v: float(v) / 365.0,
    "months_to_years": lambda v: float(v) / 12.0,
    "date_to_year": _date_to_year,
    "ln": lambda v: math.log(float(v)),
    "gwa_class_map": _gwa_class_map,
}


def _lookup(tree: dict, path: str) -> Any:
    x: Any = tree
    for part in path.split("."):
        if not isinstance(x, dict) or part not in x:
            return None
        x = x[part]
    return x


def _pick(value: Any, key: str | None) -> Any:
    if key is None or not isinstance(value, dict):
        return value
    if key in value:
        return value[key]
    for k, v in value.items():
        if str(k).lower().startswith(key.lower()):
            return v
    return None


def apply_params_yaml(tree: dict, params_path: Path, link_key: str = "params") -> list[dict[str, Any]]:
    """Replace linked defaults with params.yaml values (spec Section 12: params.yaml values are the defaults
    where they exist). Returns a log of every linked key: applied, missing, or kept by rule."""
    raw = read_yaml(params_path)
    log = []
    for s, d in tree.items():
        for k, leaf in d.items():
            path = leaf.get(link_key)
            if not path:
                continue
            node = _lookup(raw, path)
            if node is None:
                log.append({"key": f"{s}.{k}", "params": path, "status": "missing in params.yaml; defaults.yaml value kept"})
                continue
            is_leaf = isinstance(node, dict) and "value" in node
            val = node["value"] if is_leaf else node
            val = _pick(val, leaf.get("pick"))
            if val is None and is_leaf and "neutral_value" in node:
                # a class d limit with no value (acquirer.limits): its neutral value, so the limit is off unless a
                # scenario or an override sets it; verified_domain is never used as a range
                neutral = node["neutral_value"]
                leaf.update(value=neutral, neutral_value=neutral, range=None, assumed=True, limit=True,
                            grounding=str(node.get("grounding") or "d"))
                src = node.get("source")
                leaf["source"] = (f"{src} " if src else "") + f"(data/tasks/{params_path.name}: {path}; null, so the neutral value {neutral!r}: limit off)"
                leaf["origin"] = f"{params_path.name}:{path} (neutral)"
                log.append({"key": f"{s}.{k}", "params": path, "status": "null in params.yaml: neutral value (limit off)", "value": neutral})
                continue
            if val is None:
                log.append({"key": f"{s}.{k}", "params": path, "status": "no value for pick; defaults.yaml value kept"})
                continue
            try:
                val = TRANSFORMS[leaf.get("transform")](val)
            except (ValueError, TypeError) as e:
                raise ConfigError(f"params.yaml entry {path} cannot be read for {s}.{k}: {e}") from e
            leaf["value"] = val
            if is_leaf:
                rng = _pick(node.get("range"), leaf.get("pick"))
                if leaf.get("range_from") == "range_multiplier" and isinstance(node.get("range_multiplier"), (list, tuple)) \
                        and isinstance(val, (int, float)):
                    rng = [float(val) * float(m) for m in node["range_multiplier"]]
                numeric = isinstance(val, (int, float)) and not isinstance(val, bool)
                if numeric and isinstance(rng, (list, tuple)) and len(rng) == 2 and not leaf.get("range_override"):
                    try:
                        leaf["range"] = [TRANSFORMS[leaf.get("transform")](x) if x is not None else None for x in rng]
                    except (ValueError, TypeError, AttributeError):
                        pass
                src = leaf.get("source_public") or node.get("source")      # source_public: text for outputs (spec 26)
                leaf["source"] = f"{src} (data/tasks/{params_path.name}: {path})" if src else f"data/tasks/{params_path.name}: {path}"
                leaf["assumed"] = bool(node.get("assumed", False))
                if node.get("grounding"):
                    leaf["grounding"] = str(node.get("grounding"))
                if node.get("quality"):
                    leaf.setdefault("flag", node.get("quality"))
            else:
                leaf["source"] = f"data/tasks/{params_path.name}: {path}"
            leaf["origin"] = f"{params_path.name}:{path}" + (f"[{leaf['pick']}]" if leaf.get("pick") else "")
            log.append({"key": f"{s}.{k}", "params": path, "status": "applied", "value": val})
    return log


def find_data_dir(explicit: str | os.PathLike | None = None) -> Path | None:
    """The data agent's folder (spec Section 12): explicit argument, then AUTOFRONTIER_DATA, then the repository
    layout engine/../data/tasks. None if none is found (the engine then uses its built-in priors)."""
    cands = []
    if explicit:
        cands.append(Path(explicit))
    if os.environ.get("AUTOFRONTIER_DATA"):
        cands.append(Path(os.environ["AUTOFRONTIER_DATA"]))
    cands.append(REPO_DIR / "data" / "tasks")
    for c in cands:
        if c.is_dir() and any(c.glob("*.csv")):
            return c
    return None


def load_params(data_dir: Path | None = None, use_params_yaml: bool = True) -> Params:
    """Defaults, with params.yaml applied when the data folder has one."""
    tree = read_yaml(DEFAULTS_PATH)
    log: list[dict[str, Any]] = []
    if use_params_yaml:
        dd = data_dir if data_dir is not None else find_data_dir()
        if dd is not None and (Path(dd) / "params.yaml").is_file():
            log = apply_params_yaml(tree, Path(dd) / "params.yaml")
        if dd is not None and (Path(dd) / "params_reliability.yaml").is_file():
            log += apply_params_yaml(tree, Path(dd) / "params_reliability.yaml", link_key="params_rel")
    for d in tree.values():                       # limits left null without params.yaml take their neutral value too
        for leaf in d.values():
            if isinstance(leaf, dict) and leaf.get("limit") and leaf.get("value") is None and "neutral_value" in leaf:
                leaf["value"] = leaf["neutral_value"]
    p = Params(tree)
    p.params_log = log
    return p


def parse_override(text: str) -> tuple[str, Any]:
    """`section.key=value` from the command line; the value is parsed as YAML (numbers, lists, true/false)."""
    if "=" not in text:
        raise ConfigError(f"override '{text}' must look like section.key=value, e.g. finance.r=0.09")
    k, v = text.split("=", 1)
    try:
        return k.strip(), yaml.safe_load(v)
    except yaml.YAMLError as e:
        raise ConfigError(f"override '{text}': value is not valid ({e})") from e


# -------------------------------------------------------------------------------------------------
# Version stamp (spec 19.1 change control)
# -------------------------------------------------------------------------------------------------
NOTES_FILES = ["notes/unified_model_spec.md", "notes/theory_core_notes.md", "notes/theory_ext_notes.md",
               "notes/theory_regimes_notes.md", "notes/theory_product_notes.md", "notes/modern_theory_map.md",
               "notes/accounting_notes.md", "notes/labor_notes.md", "notes/competition_notes.md",
               "notes/data_sources_reliability.md", "notes/data_sources_nonsoftware.md", "notes/assumptions_register.md",
               "notes/assumptions_memo.md", "notes/acquirer_notes.md",
               "notes/playbook_engine_spec.md"]


def sha256_file(path: Path) -> str | None:
    if not Path(path).is_file():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def source_hashes(data_dir: Path | None) -> dict[str, str | None]:
    """Hashes of the theory notes, the spec, defaults.yaml and params.yaml the run used."""
    out = {f: sha256_file(REPO_DIR / f) for f in NOTES_FILES}
    out["engine/defaults.yaml"] = sha256_file(DEFAULTS_PATH)
    if data_dir is not None:
        out["data/tasks/params.yaml"] = sha256_file(Path(data_dir) / "params.yaml")
        out["data/tasks/params_reliability.yaml"] = sha256_file(Path(data_dir) / "params_reliability.yaml")
    return out
