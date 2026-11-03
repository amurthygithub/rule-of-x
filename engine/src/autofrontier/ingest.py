# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Read a folder of CSV/XLSX input files, validate them, report the tier each piece reaches, and map
cost centers and GL accounts to the function taxonomy, job titles to SOC codes, and vendors to
categories. Every mapping carries a confidence score and is written to mapping_review.csv, which the
user can correct and feed back as mappings.csv."""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pydantic import ValidationError

from . import schema
from .priors import Priors, norm_soc


class InputError(ValueError):
    """A required input is missing or invalid, so the engine cannot run. The message says how to fix it."""

STOP = {"of", "and", "the", "a", "an", "for", "to", "in", "all", "other", "except", "i", "ii", "iii", "iv", "sr", "jr",
        "senior", "junior", "lead", "principal", "staff", "associate", "assistant", "head", "chief", "&", "-", "/"}
LEVEL_PATTERNS = [
    (r"\b(chief|cxo|ceo|cfo|cto|coo|cio|cmo|cro|chro|president|evp|svp|vp|vice president|head of)\b", "executive"),
    (r"\b(director)\b", "director"),
    (r"\b(manager|mgr|supervisor|team lead|lead)\b", "manager"),
    (r"\b(principal|staff|senior|sr\.?|iii|expert)\b", "senior"),
    (r"\b(junior|jr\.?|associate|entry|intern|trainee|apprentice|i)\b", "junior"),
]


def _norm_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [re.sub(r"[^a-z0-9]+", "_", str(c).strip().lower()).strip("_") for c in df.columns]
    return df.dropna(how="all")


def _read_any(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in (".xlsx", ".xlsm", ".xls"):
        xl = pd.ExcelFile(path, engine="openpyxl")
        sheet = "data" if "data" in xl.sheet_names else xl.sheet_names[0]
        return _norm_cols(xl.parse(sheet, dtype=object))
    return _norm_cols(pd.read_csv(path, dtype=object, encoding_errors="replace"))


def _issue(issues: list, severity: str, code: str, file: str, message: str, fix: str = "", fallback: str = "",
           row: int | None = None, column: str | None = None) -> None:
    """Record a validation issue. Messages name files, rows and columns, never the values themselves."""
    issues.append({"severity": severity, "code": code, "file": file, "row": row, "column": column,
                   "message": message, "fix": fix, "fallback": fallback})


def find_input_files(folder: Path) -> dict[str, Path]:
    """Locate each template's file by name prefix (CSV or XLSX); CSV wins if both exist."""
    found: dict[str, Path] = {}
    files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in (".csv", ".xlsx", ".xlsm"))
    for name in schema.TEMPLATES:
        cands = [p for p in files if p.stem.lower() == name or p.stem.lower().startswith(name + "_")
                 or p.stem.lower().startswith(name + "-")]
        if name == "mappings":
            cands = [p for p in files if p.stem.lower() in ("mappings", "mapping_review", "mappings_corrected")]
        if cands:
            cands.sort(key=lambda p: (p.suffix.lower() != ".csv", len(p.name)))
            found[name] = cands[0]
    return found


def _keyvalue(df: pd.DataFrame) -> dict[str, Any]:
    if {"field", "value"} <= set(df.columns):
        kv = {str(r.field).strip(): r.value for r in df.itertuples() if pd.notna(r.value) and str(r.value).strip() != ""}
    else:  # a one-row table is accepted too
        kv = {c: df.iloc[0][c] for c in df.columns if pd.notna(df.iloc[0][c])} if len(df) else {}
    out = {}
    for k, v in kv.items():
        try:
            out[k] = float(str(v).replace(",", "")) if re.fullmatch(r"-?[\d,]*\.?\d+(e-?\d+)?", str(v).strip(), re.I) else v
        except ValueError:
            out[k] = v
    return out


def _validate_rows(df: pd.DataFrame, model, errors: list, name: str) -> pd.DataFrame:
    """Validate each row against the template's model. Invalid rows are left out and reported with their row
    number (as in a spreadsheet, header = row 1), the column and what is expected."""
    rows, keep = [], []
    for i, rec in enumerate(df.to_dict("records")):
        rec = {k: (None if (v is None or (isinstance(v, float) and np.isnan(v)) or str(v).strip() == "") else v)
               for k, v in rec.items()}
        for k, v in list(rec.items()):
            if isinstance(v, str) and re.fullmatch(r"-?[\d,]+(\.\d+)?", v.strip()) and k not in ("cost_center", "gl_account", "role_id", "soc", "naics", "sic", "step"):
                rec[k] = float(v.replace(",", ""))
        try:
            m = model(**{k: v for k, v in rec.items() if k in model.model_fields})
            rows.append(m.model_dump())
            keep.append(i)
        except ValidationError as e:
            for x in e.errors():
                col = ".".join(map(str, x["loc"])) or None
                _issue(errors, "error", "invalid_value", name, f"row {i + 2}: column '{col}': {x['msg']}",
                       fix=f"correct column '{col}' in row {i + 2} (see README_{name}.md for the expected type and range)",
                       fallback="the row is left out", row=i + 2, column=col)
    out = pd.DataFrame(rows)
    if len(out):
        dup = out.duplicated(keep="first")
        if dup.any():
            _issue(errors, "warning", "duplicate_rows", name, f"{int(dup.sum())} rows are exact duplicates of earlier rows",
                   fix="remove the duplicate rows, or make them distinct if they are separate items",
                   fallback="exact duplicates are dropped so that nothing is counted twice")
            out = out[~dup].reset_index(drop=True)
    return out


def _check_columns(df: pd.DataFrame, spec, issues: list) -> bool:
    """Every required column of a table template must be present. Returns False if the file must be skipped."""
    req = [c for c, _, r in spec.columns if r]
    missing = [c for c in req if c not in df.columns]
    if missing:
        _issue(issues, "error", "missing_columns", spec.name, f"required columns missing: {', '.join(missing)}",
               fix=f"add the columns {', '.join(missing)} (templates: autofrontier init <folder>)",
               fallback="the file is ignored and the engine uses priors for this tier")
        return False
    unknown = [c for c in df.columns if c not in {c2 for c2, _, _ in spec.columns}]
    if unknown:
        _issue(issues, "info", "unknown_columns", spec.name, f"columns not used by the engine: {', '.join(unknown[:10])}",
               fallback="ignored")
    return True


# --------------------------------------------------------------------------------------------
# Mapping helpers
# --------------------------------------------------------------------------------------------

def _tokens(s: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9&+]+", str(s).lower()) if t not in STOP and len(t) > 1}


class TitleMatcher:
    """Fuzzy title matching against O*NET titles (occupation titles and alternate titles when the
    data agent supplies them), with a keyword-rule fallback."""

    def __init__(self, titles: pd.DataFrame, rules: pd.DataFrame):
        t = titles.dropna().copy()
        t["norm"] = t.title.str.lower().str.replace(r"[^a-z0-9 &+]", " ", regex=True)
        self.titles = t.reset_index(drop=True)
        self.index: dict[str, list[int]] = {}
        for i, s in enumerate(self.titles.norm):
            for tok in _tokens(s):
                self.index.setdefault(tok, []).append(i)
                # crude stemming so "developer" meets "developers"
                if tok.endswith("s"):
                    self.index.setdefault(tok[:-1], []).append(i)
        self.rules = [(re.compile(r.pattern, re.I), r.soc, float(r.confidence)) for r in rules.itertuples()]

    def candidates(self, title: str, k: int = 60) -> dict[str, float]:
        """Best fuzzy score per SOC over a shortlist of O*NET titles (rarest shared tokens first)."""
        q = str(title).lower()
        toks = _tokens(q)
        toks |= {t[:-1] for t in toks if t.endswith("s")}
        counts: dict[int, float] = {}
        for tok in toks:
            post = self.index.get(tok, [])
            if not post:
                continue
            w = 1.0 / np.log(2.0 + len(post))
            for i in post:
                counts[i] = counts.get(i, 0.0) + w
        out: dict[str, float] = {}
        for i in sorted(counts, key=counts.get, reverse=True)[:k]:
            s = self.titles.norm.iat[i]
            ratio = difflib.SequenceMatcher(None, q, s).ratio()
            st = _tokens(s) | {x[:-1] for x in _tokens(s) if x.endswith("s")}
            jac = len(toks & st) / max(len(toks | st), 1)
            sc = 0.5 * ratio + 0.5 * jac
            soc = self.titles.soc.iat[i]
            if sc > out.get(soc, 0.0):
                out[soc] = sc
        return out

    def fuzzy(self, title: str) -> tuple[str | None, float, str]:
        c = self.candidates(title)
        if not c:
            return None, 0.0, "none"
        soc = max(c, key=c.get)
        return soc, float(c[soc]), "fuzzy_onet_title"

    def keyword(self, title: str) -> tuple[str | None, float, str]:
        for rx, soc, conf in self.rules:
            if rx.search(str(title)):
                return soc, conf, "keyword_rule"
        return None, 0.0, "none"

    def match(self, title: str, context: dict[str, float] | None = None) -> tuple[str | None, float, str]:
        """Choose the SOC that maximizes fuzzy score + context bonus + keyword agreement. The context is
        the occupation mix of the row's function (from its cost center), so that an alternate title
        listed under several SOCs resolves to the one the function employs."""
        c = self.candidates(title)
        k_soc, k_sc, _ = self.keyword(title)
        ctx = context or {}
        if k_soc and k_soc not in c:
            c[k_soc] = 0.5 * k_sc
        if not c:
            return None, 0.0, "unmapped"
        best_sc = max(c.values())
        scored = {}
        for soc, sc in c.items():
            if sc < best_sc - 0.15 and soc != k_soc:
                continue
            bonus = 0.3 * min(1.0, 10.0 * ctx.get(soc, 0.0)) + (0.25 if soc == k_soc else 0.0)
            scored[soc] = sc + bonus
        soc = max(scored, key=scored.get)
        base = c[soc]
        rivals = [x for x, v in c.items() if x != soc and v >= base - 0.03]
        conf = float(min(0.98, base if not rivals else base * 0.85))
        if soc == k_soc:
            conf = max(conf, k_sc)
        method = "fuzzy_onet_title" + ("+context" if ctx.get(soc, 0) > 0 else "") + ("+keyword" if soc == k_soc else "")
        if base < 0.35 and soc != k_soc:
            return None, 0.0, "unmapped"
        return soc, conf, method


def seniority(title: str, level: str | None = None) -> str:
    s = f"{title} {level or ''}".lower()
    for rx, lv in LEVEL_PATTERNS:
        if re.search(rx, s):
            return lv
    return "mid"


def map_function(text: str, functions: pd.DataFrame) -> tuple[str | None, float, str]:
    """Cost center (or free text) to function: keyword match on the function's keyword list, then
    fuzzy match on function names."""
    t = f" {str(text).lower()} "
    best, score = None, 0.0
    for r in functions.itertuples():
        for kw in str(r.keywords).split("|"):
            kw = kw.strip().lower()
            if kw and re.search(r"(?<![a-z])" + re.escape(kw) + r"(?![a-z])", t):
                sc = 0.6 + min(0.3, 0.03 * len(kw))
                if sc > score:
                    best, score = r.function_id, sc
    if best:
        return best, score, "keyword"
    for r in functions.itertuples():
        sc = difflib.SequenceMatcher(None, t.strip(), str(r.function_name).lower()).ratio()
        if sc > score:
            best, score = r.function_id, sc
    if best and score >= 0.5:
        return best, 0.6 * score, "fuzzy_name"
    return None, 0.0, "unmapped"


def map_regex(text: str, rules: pd.DataFrame, target_col: str, default: str) -> tuple[str, float, str]:
    for r in rules.itertuples():
        if re.search(r.pattern, str(text), re.I):
            return getattr(r, target_col), float(r.confidence), "keyword_rule"
    return default, 0.2, "default"


def wage_index(location: str | None, locations: pd.DataFrame) -> tuple[float, str]:
    if not location:
        return 1.0, "US"
    for r in locations.itertuples():
        if re.search(r.pattern, str(location), re.I):
            return float(r.wage_index), r.region
    return 1.0, "US"


# --------------------------------------------------------------------------------------------
# Result
# --------------------------------------------------------------------------------------------
@dataclass
class IngestResult:
    financials: schema.Financials
    opex: pd.DataFrame | None
    roster: pd.DataFrame | None
    vendors: pd.DataFrame | None
    systems: pd.DataFrame | None
    volumes: pd.DataFrame | None
    org: schema.OrgInputs
    sponsors: pd.DataFrame | None
    time_study: pd.DataFrame | None
    mappings: pd.DataFrame
    tiers: dict[str, Any]
    products: pd.DataFrame | None = None
    product_occupations: pd.DataFrame | None = None
    ai_features: pd.DataFrame | None = None
    security: schema.SecurityInputs = field(default_factory=schema.SecurityInputs)
    regime: schema.RegimeInputs = field(default_factory=schema.RegimeInputs)
    jurisdictions: pd.DataFrame | None = None
    integrations: pd.DataFrame | None = None
    policy: schema.PolicyInputs = field(default_factory=schema.PolicyInputs)
    firm_tasks: pd.DataFrame | None = None
    issues: list[dict] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)

    @property
    def tier_reached(self) -> int:
        return int(self.tiers.get("tier_reached", 0))

    @property
    def errors(self) -> list[dict]:
        return [i for i in self.issues if i["severity"] == "error"]

    @property
    def warnings(self) -> list[dict]:
        return [i for i in self.issues if i["severity"] == "warning"]


def _user_maps(df: pd.DataFrame | None) -> dict[tuple[str, str], str]:
    if df is None or not len(df):
        return {}
    out = {}
    for r in df.itertuples():
        conf = getattr(r, "user_confirmed", 1)
        if conf is None or (isinstance(conf, float) and np.isnan(conf)) or float(conf) >= 0.5:
            out[(str(r.source_type), str(r.source_value).strip().lower())] = str(r.target).strip()
    return out


def _check_financials(fin: schema.Financials, issues: list) -> None:
    """Unit and plausibility checks on Tier 0 that a typed schema cannot catch."""
    S = fin.revenue
    costs = fin.cogs + fin.rnd + fin.sm + fin.ga
    if fin.headcount:
        rpe = S / fin.headcount
        if rpe < 5_000:
            raise InputError(f"tier0_financials: revenue per employee is {rpe:,.0f}, which suggests revenue is in thousands "
                             "or millions while headcount is in people. Enter all amounts in currency units (for example "
                             "650000000, not 650).")
        if rpe > 50_000_000:
            _issue(issues, "warning", "unit_mismatch", "tier0_financials",
                   f"revenue per employee is {rpe:,.0f}; check that headcount is in people and revenue in currency units",
                   fix="correct headcount or revenue", fallback="values used as given")
    if costs > 3 * S:
        _issue(issues, "warning", "loss_making", "tier0_financials",
               "operating costs exceed three times revenue; check units", fallback="values used as given")
    elif costs > S:
        _issue(issues, "info", "loss_making", "tier0_financials",
               "the firm is loss-making at the operating line; the score path starts below zero margin",
               fallback="supported; no change")
    if fin.revenue_growth is not None and fin.revenue_growth < 0:
        _issue(issues, "info", "negative_growth", "tier0_financials", "revenue growth is negative", fallback="supported")
    if fin.currency.upper() != "USD":
        _issue(issues, "warning", "currency", "tier0_financials",
               f"currency is {fin.currency}; wage, price and cost priors are in USD",
               fix="convert amounts to USD, or accept that priors are not converted",
               fallback="amounts are treated as USD")


def _currency_check(df: pd.DataFrame, name: str, currency: str, issues: list) -> bool:
    if "currency" in df.columns:
        cur = {str(x).strip().upper() for x in df["currency"].dropna()}
        if cur and cur != {currency.upper()}:
            _issue(issues, "error", "currency_mismatch", name,
                   f"currency column says {', '.join(sorted(cur))} but tier0_financials says {currency}",
                   fix="convert the file to the tier0 currency", fallback="the file is ignored")
            return False
    return True


def ingest_folder(folder: str | Path, priors: Priors) -> IngestResult:
    """Read and validate an input folder. Raises InputError only when Tier 0 is missing or unusable; every other
    problem becomes an issue with a documented fallback."""
    folder = Path(folder)
    if not folder.is_dir():
        raise InputError(f"input folder {folder} not found. Create one with `autofrontier init <folder>`.")
    files = find_input_files(folder)
    issues: list[dict] = []
    if "tier0_financials" not in files:
        raise InputError("tier0_financials.csv (or .xlsx) is required in the input folder. "
                         "Run `autofrontier init <folder>` for a template.")
    raw: dict[str, pd.DataFrame] = {}
    for k, p in files.items():
        try:
            raw[k] = _read_any(p)
        except Exception as e:  # malformed CSV or XLSX
            if k == "tier0_financials":
                raise InputError(f"tier0_financials could not be read ({type(e).__name__}). Save it as a UTF-8 CSV "
                                 "with columns field and value, or as the XLSX template.") from e
            _issue(issues, "error", "malformed_file", k, f"the file could not be read ({type(e).__name__})",
                   fix="save it as UTF-8 CSV or as the XLSX template", fallback="the file is ignored; priors are used")
    for k, df in list(raw.items()):
        spec = schema.TEMPLATES[k]
        if spec.kind == "table" and not _check_columns(df, spec, issues):
            raw.pop(k)

    kv = _keyvalue(raw["tier0_financials"])
    for k in ("naics", "sic"):
        if k in kv:
            kv[k] = str(kv[k]).split(".")[0]
    if "ownership_regime" in kv:
        kv["ownership_regime"] = str(kv["ownership_regime"]).strip().lower()
    unknown = [k for k in kv if k not in schema.Financials.model_fields]
    if unknown:
        _issue(issues, "info", "unknown_fields", "tier0_financials", f"fields not used: {', '.join(unknown[:10])}", fallback="ignored")
    try:
        fin = schema.Financials(**{k: v for k, v in kv.items() if k in schema.Financials.model_fields})
    except ValidationError as e:
        msgs = "; ".join(f"field '{'.'.join(map(str, x['loc']))}': {x['msg']}" for x in e.errors())
        raise InputError(f"tier0_financials is invalid: {msgs}. Required fields: revenue, cogs, rnd, sm, ga "
                         "(see README_tier0_financials.md).") from e
    _check_financials(fin, issues)
    for k in list(raw):
        if k != "tier0_financials" and not _currency_check(raw[k], k, fin.currency, issues):
            raw.pop(k)

    user = {}
    if "mappings" in raw:
        mdf = _validate_rows(raw["mappings"], schema.MappingRow, issues, "mappings")
        user = _user_maps(mdf)
    maps: list[dict] = []
    fn_ids = set(priors.functions.function_id)
    socs = set(priors.occupations.soc)

    def cc_function(cc: str, name: str | None, explicit: str | None, materiality: float) -> tuple[str | None, float, str]:
        if explicit and explicit in fn_ids:
            return (explicit, 1.0, "explicit")
        if (k := ("cost_center", str(cc).strip().lower())) in user and user[k] in fn_ids:
            return (user[k], 1.0, "user_mapping")
        if name and (k2 := ("cost_center", str(name).strip().lower())) in user and user[k2] in fn_ids:
            return (user[k2], 1.0, "user_mapping")
        return map_function(f"{name or ''} {cc}", priors.functions)

    # ---- Tier 1 opex ------------------------------------------------------------------------
    opex = None
    if "tier1_opex" in raw:
        opex = _validate_rows(raw["tier1_opex"], schema.OpexRow, issues, "tier1_opex")
        if len(opex):
            ccs = opex.groupby(["cost_center"], dropna=False).agg(
                name=("cost_center_name", "first"), fid=("function_id", "first"), amount=("amount", "sum")).reset_index()
            ccmap = {}
            for r in ccs.itertuples():
                f_, c_, m_ = cc_function(r.cost_center, r.name, r.fid, r.amount)
                ccmap[r.cost_center] = (f_, c_, m_)
                maps.append({"source_type": "cost_center", "source_value": r.cost_center, "label": r.name, "target": f_,
                             "confidence": c_, "method": m_, "materiality": r.amount})
            opex["function_id"] = opex.cost_center.map(lambda c: ccmap[c][0])
            opex["function_conf"] = opex.cost_center.map(lambda c: ccmap[c][1])
            gls = opex.groupby("gl_account", dropna=False).agg(name=("gl_name", "first"), amount=("amount", "sum")).reset_index()
            glmap = {}
            for r in gls.itertuples():
                key = ("gl_account", str(r.gl_account).strip().lower())
                if key in user:
                    t, c, m = user[key], 1.0, "user_mapping"
                else:
                    t, c, m = map_regex(f"{r.name or ''} {r.gl_account or ''}", priors.gl_rules, "cost_type", "other")
                glmap[r.gl_account] = (t, c)
                maps.append({"source_type": "gl_account", "source_value": r.gl_account, "label": r.name, "target": t,
                             "confidence": c, "method": m, "materiality": r.amount})
            opex["cost_type"] = opex.gl_account.map(lambda g: glmap.get(g, ("other", 0.2))[0])
            opex["cost_type_conf"] = opex.gl_account.map(lambda g: glmap.get(g, ("other", 0.2))[1])
            unm_cc = opex[opex.function_id.isna()]
            if len(unm_cc):
                _issue(issues, "warning", "unmapped_cost_centers", "tier1_opex",
                       f"{unm_cc.cost_center.nunique()} cost centers ({unm_cc.amount.sum() / max(opex.amount.sum(), 1):.0%} of Tier 1 spend) match no function",
                       fix="map them in mappings.csv (copy rows from mapping_review.csv)",
                       fallback="their spend is spread over functions in proportion to mapped spend")
            low_gl = opex[opex.cost_type_conf < 0.5]
            if len(low_gl):
                _issue(issues, "warning", "unmapped_gl_accounts", "tier1_opex",
                       f"{low_gl.gl_account.nunique()} GL accounts have no confident cost type",
                       fix="set their cost type in mappings.csv", fallback="treated as other (non-labor) cost")
            total0 = fin.cogs + fin.rnd + fin.sm + fin.ga
            cov = float(opex.amount.sum() / max(total0, 1e-9))
            if cov < 0.5 or cov > 1.5:
                _issue(issues, "error", "inconsistent_totals", "tier1_opex",
                       f"Tier 1 totals {cov:.0%} of the Tier 0 cost lines; the two do not describe the same firm-year",
                       fix="check the fiscal year, currency and units of tier1_opex",
                       fallback="Tier 1 is ignored and function spend comes from industry priors")
                opex = None
            elif abs(cov - 1) > 0.1:
                _issue(issues, "warning", "inconsistent_totals", "tier1_opex",
                       f"Tier 1 totals {cov:.0%} of the Tier 0 cost lines",
                       fix="add missing cost centers or check the period",
                       fallback="Tier 1 function shares are scaled to the Tier 0 cost buckets")
                opex.attrs["scale_to_tier0"] = True

    # ---- Tier 2 roster ----------------------------------------------------------------------
    roster = None
    if "tier2_roster" in raw:
        roster = _validate_rows(raw["tier2_roster"], schema.RosterRow, issues, "tier2_roster")
        if len(roster):
            cc_names = {}
            if opex is not None and len(opex):
                cc_names = opex.groupby("cost_center").cost_center_name.first().to_dict()
            known_cc = {m["source_value"]: (m["target"], m["confidence"]) for m in maps if m["source_type"] == "cost_center"}
            fids, fconf = [], []
            for r in roster.itertuples():
                if r.function_id and r.function_id in fn_ids:
                    fids.append(r.function_id); fconf.append(1.0); continue
                if r.cost_center and r.cost_center in known_cc and known_cc[r.cost_center][0]:
                    fids.append(known_cc[r.cost_center][0]); fconf.append(known_cc[r.cost_center][1]); continue
                if r.cost_center:
                    f_, c_, m_ = cc_function(r.cost_center, cc_names.get(r.cost_center), None, r.fte)
                    known_cc[r.cost_center] = (f_, c_)
                    if f_:
                        maps.append({"source_type": "cost_center", "source_value": r.cost_center, "label": cc_names.get(r.cost_center),
                                     "target": f_, "confidence": c_, "method": m_, "materiality": r.fte})
                    fids.append(f_); fconf.append(c_); continue
                fids.append(None); fconf.append(0.0)
            roster["function_id"] = fids
            roster["function_conf"] = fconf
            fo, _ = priors.function_occ_for(fin.naics)
            ctx_by_f = {f: dict(zip(g.soc, g.weight)) for f, g in fo.groupby("function_id")}
            tm = TitleMatcher(priors.onet_titles, priors.title_rules)
            tmap = {}
            for title, f_ in roster[["title", "function_id"]].drop_duplicates().itertuples(index=False):
                key = ("title", str(title).strip().lower())
                if key in user and norm_soc(user[key]) in socs:
                    tmap[(title, f_)] = (norm_soc(user[key]), 1.0, "user_mapping")
                else:
                    s_, c_, m_ = tm.match(title, ctx_by_f.get(f_))
                    tmap[(title, f_)] = (s_ if s_ in socs else None, c_ if s_ in socs else 0.0, m_ if s_ in socs else "unmapped")
            explicit = roster.soc.map(norm_soc) if "soc" in roster.columns else pd.Series([None] * len(roster))
            keys = list(zip(roster.title, roster.function_id))
            roster["soc_conf"] = [1.0 if (e and e in socs) else tmap[k][1] for e, k in zip(explicit, keys)]
            roster["soc_method"] = ["explicit" if (e and e in socs) else tmap[k][2] for e, k in zip(explicit, keys)]
            roster["soc"] = [e if (e and e in socs) else tmap[k][0] for e, k in zip(explicit, keys)]
            fte_by = roster.groupby(["title", "function_id"], dropna=False).fte.sum()
            for (t, f_), (s_, c_, m_) in tmap.items():
                maps.append({"source_type": "title", "source_value": t, "label": f_, "target": s_, "confidence": c_,
                             "method": m_, "materiality": float(fte_by.get((t, f_), 0))})
            for i in roster.index[roster.function_id.isna()]:
                cand = fo[fo.soc == roster.at[i, "soc"]]
                if len(cand):
                    roster.at[i, "function_id"] = cand.sort_values("weight").function_id.iloc[-1]
                    roster.at[i, "function_conf"] = 0.3
            wi = [wage_index(l, priors.locations) for l in roster.location]
            roster["wage_index_used"] = [r.wage_index if pd.notna(r.wage_index) else w[0] for r, w in zip(roster.itertuples(), wi)]
            roster["region"] = [w[1] for w in wi]
            roster["seniority"] = [seniority(t, l) for t, l in zip(roster.title, roster.level)]
            unm = roster[roster.soc.isna()]
            if len(unm):
                _issue(issues, "warning", "unmapped_titles", "tier2_roster",
                       f"{len(unm)} roster rows ({unm.fte.sum():.0f} FTE) have no SOC match",
                       fix="give the soc column, or correct the title mapping in mappings.csv",
                       fallback="their headcount is spread over the function's occupation prior")
            nof = roster[roster.function_id.isna()]
            if len(nof):
                _issue(issues, "warning", "unmapped_function", "tier2_roster", f"{len(nof)} roster rows have no function",
                       fix="give function_id or a mappable cost_center", fallback="assigned to the largest function")
            pay = roster.annual_base_comp
            out_hi, out_lo = int((pay > 2_000_000).sum()), int((pay < 5_000).sum())
            if out_hi or out_lo:
                _issue(issues, "warning", "outliers", "tier2_roster",
                       f"{out_hi} rows with pay above 2,000,000 and {out_lo} below 5,000 per FTE",
                       fix="check that pay is annual, per FTE and in currency units", fallback="values used as given")
            if fin.headcount:
                ratio = float(roster.fte.sum() / fin.headcount)
                if ratio < 0.8 or ratio > 1.25:
                    _issue(issues, "warning", "inconsistent_totals", "tier2_roster",
                           f"roster FTE is {ratio:.0%} of Tier 0 headcount (contractors count in the roster, not in Tier 0)",
                           fix="check for missing cost centers or a different date", fallback="the roster is used as given")

    # ---- Tier 3 vendors ---------------------------------------------------------------------
    vendors = None
    if "tier3_vendors" in raw:
        vendors = _validate_rows(raw["tier3_vendors"], schema.VendorRow, issues, "tier3_vendors")
        if len(vendors):
            cats = priors.vendor_categories.set_index("category")
            out_cat, out_conf, out_m = [], [], []
            for r in vendors.itertuples():
                key = ("vendor", str(r.vendor).strip().lower())
                if r.category and r.category in cats.index:
                    c = (r.category, 1.0, "explicit")
                elif key in user and user[key] in cats.index:
                    c = (user[key], 1.0, "user_mapping")
                else:
                    c = map_regex(f"{r.vendor} {r.description or ''}", priors.vendor_rules, "category", "other")
                out_cat.append(c[0]); out_conf.append(c[1]); out_m.append(c[2])
                maps.append({"source_type": "vendor", "source_value": r.vendor, "label": r.description, "target": c[0],
                             "confidence": c[1], "method": c[2], "materiality": r.annual_spend})
            vendors["category"] = out_cat
            vendors["category_conf"] = out_conf
            vendors["function_id"] = [f if (f and f in fn_ids) else cats.loc[c, "function_id"] for f, c in zip(vendors.function_id, out_cat)]
            vendors["labor_outsourcing"] = [int(cats.loc[c, "labor_outsourcing"]) for c in out_cat]
            vendors["family"] = [cats.loc[c, "family"] for c in out_cat]
            vendors["cost_type"] = [cats.loc[c, "cost_type"] for c in out_cat]
            tot = vendors.annual_spend.sum()
            if tot > fin.cogs + fin.rnd + fin.sm + fin.ga:
                _issue(issues, "warning", "inconsistent_totals", "tier3_vendors",
                       "vendor spend exceeds total Tier 0 costs", fix="check units", fallback="values used as given")

    systems = _validate_rows(raw["tier3_systems"], schema.SystemRow, issues, "tier3_systems") if "tier3_systems" in raw else None
    if systems is not None and len(systems):
        systems["function_id"] = [f if f in fn_ids else (map_function(f"{f or ''} {s}", priors.functions)[0])
                                  for f, s in zip(systems.function_id, systems.system)]

    volumes = None
    if "tier3_volumes" in raw:
        volumes = _validate_rows(raw["tier3_volumes"], schema.VolumeRow, issues, "tier3_volumes")
        if len(volumes):
            pids = set(priors.processes.process_id)
            names = dict(zip(priors.processes.process_name.str.lower(), priors.processes.process_id))
            res = []
            for r in volumes.itertuples():
                if r.process_id in pids:
                    res.append(r.process_id)
                    continue
                q = str(r.process_name or r.process_id or "").lower()
                m = difflib.get_close_matches(q, list(names), n=1, cutoff=0.6)
                res.append(names[m[0]] if m else None)
            volumes["process_id"] = res
            bad = volumes[volumes.process_id.isna()]
            if len(bad):
                _issue(issues, "warning", "unknown_process", "tier3_volumes", f"{len(bad)} volume rows match no library process",
                       fix="use a process_id from the engine library", fallback="those rows are ignored")
            volumes = volumes.dropna(subset=["process_id"])
            if volumes.process_id.duplicated().any():
                _issue(issues, "warning", "duplicate_rows", "tier3_volumes", "several rows give a volume for the same process",
                       fallback="volumes of the same process are added")

    def keyvalue_model(name, model):
        if name not in raw:
            return model()
        try:
            kvo = _keyvalue(raw[name])
            if "planned_reorg_years" in kvo:
                kvo["planned_reorg_years"] = str(kvo["planned_reorg_years"]).replace(".0", "")
            for k2 in ("certifications",):
                if k2 in kvo:
                    kvo[k2] = str(kvo[k2])
            return model(**{k: v for k, v in kvo.items() if k in model.model_fields})
        except ValidationError as e:
            for x in e.errors():
                col = ".".join(map(str, x["loc"]))
                _issue(issues, "error", "invalid_value", name, f"field '{col}': {x['msg']}",
                       fix=f"correct field '{col}' (see README_{name}.md)", fallback="the file is ignored; priors are used", column=col)
            return model()

    org = keyvalue_model("tier3_org", schema.OrgInputs)
    security = keyvalue_model("tier3_security", schema.SecurityInputs)
    regime = keyvalue_model("tier3_regime", schema.RegimeInputs)
    policy = keyvalue_model("tier3_policy", schema.PolicyInputs)
    firm_tasks = _validate_rows(raw["tier3_tasks"], schema.FirmTaskRow, issues, "tier3_tasks") if "tier3_tasks" in raw else None
    sponsors = _validate_rows(raw["tier3_sponsors"], schema.SponsorRow, issues, "tier3_sponsors") if "tier3_sponsors" in raw else None
    if sponsors is not None and len(sponsors):
        sponsors["function_id"] = [f if f in fn_ids else map_function(f, priors.functions)[0] for f in sponsors.function_id]
    time_study = _validate_rows(raw["tier4_time_study"], schema.TimeStudyRow, issues, "tier4_time_study") if "tier4_time_study" in raw else None

    products = _validate_rows(raw["tier3_products"], schema.ProductRow, issues, "tier3_products") if "tier3_products" in raw else None
    if products is not None and len(products):
        tot = products.revenue.sum()
        if abs(tot / fin.revenue - 1) > 0.1:
            _issue(issues, "warning", "inconsistent_totals", "tier3_products",
                   f"product-line revenue totals {tot / fin.revenue:.0%} of Tier 0 revenue",
                   fix="add missing lines or check units", fallback="each line's share of product revenue is applied to Tier 0 revenue")
        noseat = products[(products.pricing_model == "seat") & (products.seats.isna() | (products.seats <= 0))]
        if len(noseat):
            _issue(issues, "info", "no_seats", "tier3_products", f"{len(noseat)} seat-priced lines give no seat count",
                   fallback="seats are inferred from revenue and the price per seat, or seat compression is applied to revenue")
    pocc = _validate_rows(raw["tier3_product_occupations"], schema.ProductOccupationRow, issues,
                          "tier3_product_occupations") if "tier3_product_occupations" in raw else None
    if pocc is not None and len(pocc):
        pocc["soc"] = pocc.soc.map(norm_soc)
        bad = pocc[~pocc.soc.isin(socs)]
        if len(bad):
            _issue(issues, "warning", "unknown_soc", "tier3_product_occupations", f"{len(bad)} rows have unknown SOC codes",
                   fix="use 2018 SOC codes such as 43-4051", fallback="those rows are ignored")
            pocc = pocc[pocc.soc.isin(socs)]
        sums = pocc.groupby("product_line").seat_share.sum()
        if ((sums - 1).abs() > 0.05).any():
            _issue(issues, "warning", "shares_not_one", "tier3_product_occupations",
                   "seat shares do not add up to 1 for some lines", fallback="shares are rescaled to add up to 1")
            pocc["seat_share"] = pocc.seat_share / pocc.groupby("product_line").seat_share.transform("sum")
    feats = _validate_rows(raw["tier3_ai_features"], schema.AIFeatureRow, issues, "tier3_ai_features") if "tier3_ai_features" in raw else None

    jur = _validate_rows(raw["tier3_jurisdictions"], schema.JurisdictionRow, issues, "tier3_jurisdictions") \
        if "tier3_jurisdictions" in raw else None
    if jur is not None and len(jur) and fin.headcount:
        tot = float(jur.headcount.sum())
        if abs(tot / fin.headcount - 1) > 0.15:
            _issue(issues, "warning", "inconsistent_totals", "tier3_jurisdictions",
                   f"site headcount totals {tot / fin.headcount:.0%} of Tier 0 headcount",
                   fix="add missing sites or check the headcount column", fallback="site shares are applied to Tier 0 headcount")

    integ = _validate_rows(raw["tier3_integrations"], schema.IntegrationRow, issues, "tier3_integrations") \
        if "tier3_integrations" in raw else None

    mappings = pd.DataFrame(maps, columns=["source_type", "source_value", "label", "target", "confidence", "method", "materiality"])
    tiers = tier_report(fin, opex, roster, vendors, systems, volumes, org, sponsors, time_study, mappings)
    tiers["tier3"]["products"] = products is not None and len(products) > 0
    tiers["tier3"]["security"] = "tier3_security" in raw
    tiers["tier3"]["regime"] = "tier3_regime" in raw
    present = [k for k in schema.TEMPLATES if k in files]
    tiers["files_present"] = present
    return IngestResult(financials=fin, opex=opex, roster=roster, vendors=vendors, systems=systems, volumes=volumes,
                        org=org, sponsors=sponsors, time_study=time_study, mappings=mappings, tiers=tiers,
                        products=products if products is not None and len(products) else None,
                        product_occupations=pocc if pocc is not None and len(pocc) else None,
                        ai_features=feats if feats is not None and len(feats) else None,
                        security=security, regime=regime, jurisdictions=jur if jur is not None and len(jur) else None,
                        integrations=integ if integ is not None and len(integ) else None,
                        policy=policy, firm_tasks=firm_tasks if firm_tasks is not None and len(firm_tasks) else None,
                        issues=issues, files={k: str(v) for k, v in files.items()})


def tier_report(fin, opex, roster, vendors, systems, volumes, org, sponsors, time_study, mappings) -> dict[str, Any]:
    """Which tier each piece of input reaches (spec Section 9), with coverage measures."""
    total_opex = fin.cogs + fin.rnd + fin.sm + fin.ga
    rep: dict[str, Any] = {"tier0": {"present": True, "fields": int(sum(v is not None for v in fin.model_dump().values()))}}
    if opex is not None and len(opex):
        mapped = opex[opex.function_conf >= 0.5].amount.sum()
        rep["tier1"] = {"present": True, "rows": len(opex), "amount": float(opex.amount.sum()),
                        "coverage_of_tier0_costs": float(opex.amount.sum() / total_opex),
                        "share_mapped_conf_ge_0_5": float(mapped / max(opex.amount.sum(), 1e-9)),
                        "labor_identified": bool((opex.cost_type == "labor").any())}
    else:
        rep["tier1"] = {"present": False}
    if roster is not None and len(roster):
        rep["tier2"] = {"present": True, "rows": len(roster), "fte": float(roster.fte.sum()),
                        "coverage_of_headcount": float(roster.fte.sum() / fin.headcount) if fin.headcount else None,
                        "share_fte_soc_conf_ge_0_5": float(roster[roster.soc_conf >= 0.5].fte.sum() / roster.fte.sum()),
                        "contractor_fte": float(roster[roster.worker_type == "contractor"].fte.sum())}
    else:
        rep["tier2"] = {"present": False}
    t3 = {"vendors": vendors is not None and len(vendors) > 0, "systems": systems is not None and len(systems) > 0,
          "volumes": volumes is not None and len(volumes) > 0,
          "org_fields": int(sum(v is not None for v in org.model_dump().values())),
          "sponsors": sponsors is not None and len(sponsors) > 0}
    t3["present"] = bool(t3["vendors"] or t3["systems"] or t3["volumes"])
    if t3["vendors"]:
        t3["vendor_spend"] = float(vendors.annual_spend.sum())
    if t3["systems"]:
        t3["systems_count"] = len(systems)
        t3["functions_with_systems"] = int(systems.function_id.nunique())
    if t3["volumes"]:
        t3["processes_with_volumes"] = int(volumes.process_id.nunique())
    rep["tier3"] = t3
    rep["tier4"] = {"present": time_study is not None and len(time_study) > 0,
                    "rows": 0 if time_study is None else len(time_study)}
    reached = 0
    for k in (1, 2, 3, 4):
        if rep[f"tier{k}"]["present"]:
            reached = k
        else:
            break
    rep["tier_reached"] = reached
    rep["tiers_present"] = [k for k in (0, 1, 2, 3, 4) if k == 0 or rep[f"tier{k}"]["present"]]
    return rep


def mapping_review(result: IngestResult, priors: Priors) -> pd.DataFrame:
    """mapping_review.csv: every mapping with its confidence; the user corrects `target`, sets
    user_confirmed to 1 and puts the file in the input folder as mappings.csv."""
    m = result.mappings.copy()
    labels = dict(zip(priors.functions.function_id, priors.functions.function_name))
    labels.update(dict(zip(priors.occupations.soc, priors.occupations.title)))
    m["target_label"] = m.target.map(labels)
    m["user_confirmed"] = ""
    m = m.sort_values(["source_type", "confidence", "materiality"], ascending=[True, True, False])
    return m[["source_type", "source_value", "label", "target", "target_label", "confidence", "method", "materiality", "user_confirmed"]]
