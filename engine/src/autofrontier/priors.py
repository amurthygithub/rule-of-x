# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Priors: the data agent's files in data/tasks/ (spec Section 12) when present, otherwise the
built-in fallback tables in autofrontier/priors/ (all marked assumed). Each table records where it
came from, so the report can trace every prior."""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from .config import PRIORS_DIR

BUILTIN = "built-in fallback (assumed)"


def norm_soc(x) -> str | None:
    """Normalize SOC codes: '151252', '15-1252', '15-1252.00' -> '15-1252'."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    s = str(x).strip()
    m = re.match(r"^(\d{2})-?(\d{4})", s)
    return f"{m.group(1)}-{m.group(2)}" if m else None


def _read_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=True)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def _num(df: pd.DataFrame, cols, default=np.nan):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _pick(df: pd.DataFrame, *names):
    for n in names:
        if n in df.columns:
            return n
    return None


def soc_family(soc: str) -> str:
    """Fallback activity-profile family for an SOC code without one (used only when the data agent's
    occ_activity.csv is missing for that occupation)."""
    if not soc:
        return "analyst"
    major, minor = soc[:2], soc[3:5]
    if soc == "11-1011":
        return "executive"
    if major == "11":
        return "manager"
    if major == "15":
        return "software" if soc.startswith("15-125") else ("analyst" if soc.startswith("15-2") else "it_ops")
    if major == "13":
        return "accounting" if soc.startswith("13-20") else ("hr" if soc.startswith("13-107") else "analyst")
    if major == "23":
        return "legal"
    if major == "27":
        return "design"
    if major == "41":
        return "sales"
    if major == "43":
        return "support_agent" if soc.startswith("43-4051") else "clerical"
    if major == "33":
        return "security_guard"
    if major in {"35", "37", "47", "49", "51", "53"}:
        return "facilities_phys"
    return "analyst"


def _exposure_from_occupations(occ_exposure_path, occ_activity_path, activity_ids, interim: bool):
    """Activity-level LLM exposure when only occupation-level measures exist: the employment- and
    time-share-weighted mean of occupations' Eloundou et al. GPT-4 beta (spec Section 12 exposure_llm)."""
    ex = _read_csv(occ_exposure_path)
    ex["soc"] = ex["soc"].map(norm_soc)
    bcol = _pick(ex, "eloundou_gpt4_beta", "eloundou_human_beta", "exposure")
    ex = _num(ex, [bcol, "employment"])
    if occ_activity_path is None:
        return pd.Series(np.nan, index=activity_ids.index)
    oa = _read_csv(occ_activity_path)
    if "dwa_id" not in oa.columns or interim:
        oa["dwa_id"] = oa.get("iwa_id", oa.get("dwa_id"))
    oa["soc"] = oa["soc"].map(norm_soc)
    oa = _num(oa, ["time_share"])
    m = oa.merge(ex[["soc", bcol, "employment"]], on="soc", how="inner").dropna(subset=[bcol])
    m["w"] = m["time_share"] * m["employment"].fillna(1.0)
    agg = m.groupby("dwa_id").apply(lambda g: float(np.average(g[bcol], weights=g["w"])) if g["w"].sum() > 0 else np.nan,
                                    include_groups=False)
    return activity_ids.map(agg)


@dataclass
class Priors:
    functions: pd.DataFrame
    occupations: pd.DataFrame
    activities: pd.DataFrame
    occ_activity: pd.DataFrame
    function_occ: pd.DataFrame
    industry_function_shares: pd.DataFrame
    industry_staffing: pd.DataFrame | None
    processes: pd.DataFrame
    process_activities: pd.DataFrame
    title_rules: pd.DataFrame
    gl_rules: pd.DataFrame
    vendor_rules: pd.DataFrame
    vendor_categories: pd.DataFrame
    locations: pd.DataFrame
    onet_titles: pd.DataFrame | None
    function_occ_by_industry: pd.DataFrame | None = None
    industry_benchmarks: pd.DataFrame | None = None
    xw_damodaran: pd.DataFrame | None = None
    icfr_scope: pd.DataFrame | None = None       # process-level ICFR scope (full, partial, none) with basis
    icfr_steps: pd.DataFrame | None = None       # steps in ICFR scope within partial processes, with basis
    task_statements: pd.DataFrame | None = None  # O*NET 31.0 task statements (data/tasks/task_statements.csv), CC BY 4.0
    xw_task_dwa: pd.DataFrame | None = None      # task_id to dwa_id links (data/tasks/xw_task_dwa.csv)
    task_attribution: str | None = None          # file-level attribution from data/tasks/data_dictionary.csv
    provenance: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    data_dir: str | None = None

    def function_occ_for(self, naics: str | None) -> tuple[pd.DataFrame, str]:
        """Function-to-occupation mix for the firm's industry (longest NAICS prefix match in
        function_occ_by_industry.csv), else the cross-industry function_occ."""
        fi = self.function_occ_by_industry
        if fi is not None and naics:
            codes = sorted(set(fi.naics.astype(str)), key=len, reverse=True)
            for c in codes:
                if str(naics).startswith(c):
                    sub = fi[fi.naics.astype(str) == c][["function_id", "soc", "weight"]].copy()
                    have = set(sub.function_id)
                    rest = self.function_occ[~self.function_occ.function_id.isin(have)]
                    sub = pd.concat([sub, rest], ignore_index=True)
                    sub["weight"] = sub.weight / sub.groupby("function_id").weight.transform("sum")
                    return sub, f"function_occ_by_industry.csv, NAICS {c}"
        return self.function_occ, "function_occ.csv (cross-industry)"

    def gwa_attributes(self) -> pd.DataFrame:
        return pd.read_csv(PRIORS_DIR / "activity_attributes.csv")


def _builtin(name: str) -> pd.DataFrame:
    return pd.read_csv(PRIORS_DIR / name)


def _reconcile_functions(data_fn: pd.DataFrame, builtin_fn: pd.DataFrame) -> dict[str, str]:
    """Map built-in function ids to the data agent's ids by id, then by name similarity."""
    mapping: dict[str, str] = {}
    ids = list(data_fn.function_id)
    names = {r.function_id: str(r.function_name).lower() for r in data_fn.itertuples()}
    for r in builtin_fn.itertuples():
        if r.function_id in ids:
            mapping[r.function_id] = r.function_id
    # One-to-one greedy assignment on name similarity (prefix of the data name before a comma
    # counts too, so "Customer success and account management" matches "Customer success").
    pairs = []
    attrs = _builtin("function_attributes.csv").set_index("function_id")
    buckets = dict(zip(data_fn.function_id, data_fn.get("cost_bucket", pd.Series([""] * len(data_fn)))))
    for r in builtin_fn.itertuples():
        if r.function_id in mapping:
            continue
        b = r.function_name.lower()
        kws = [k.strip() for k in str(attrs.loc[r.function_id, "keywords"]).split("|") if len(k.strip()) > 3] \
            if r.function_id in attrs.index else []
        for fid, nm in names.items():
            if fid in mapping.values():
                continue
            head = nm.split(",")[0].split(" and ")[0]
            s = max(difflib.SequenceMatcher(None, b, nm).ratio(), difflib.SequenceMatcher(None, b, head).ratio(),
                    difflib.SequenceMatcher(None, b.split(" and ")[0], head).ratio())
            s += 0.3 * any(re.search(r"\b" + re.escape(k) + r"\b", nm) for k in kws)
            s += 0.1 * (str(buckets.get(fid, "")).strip().lower() == r.cost_bucket)
            pairs.append((s, r.function_id, fid))
    for s, bid, fid in sorted(pairs, reverse=True):
        if s < 0.55 or bid in mapping or fid in mapping.values():
            continue
        mapping[bid] = fid
    return mapping


def load_priors(data_dir: str | Path | None = None) -> Priors:
    prov: dict[str, str] = {}
    notes: list[str] = []
    d = Path(data_dir) if data_dir else None

    def data_file(name):
        if d is not None and (d / name).is_file():
            return d / name
        return None

    # ---- functions --------------------------------------------------------------------------
    b_fn = _builtin("functions.csv")
    fa = _builtin("function_attributes.csv")
    f = data_file("functions.csv")
    fmap = {k: k for k in b_fn.function_id}
    if f is not None:
        fn = _read_csv(f)
        need = {"function_id", "function_name", "cost_bucket"}
        if need <= set(fn.columns):
            fn["customer_facing"] = pd.to_numeric(fn.get("customer_facing", 0), errors="coerce").fillna(0).astype(int)
            fn["cost_bucket"] = fn["cost_bucket"].str.strip().str.lower()
            fmap = _reconcile_functions(fn, b_fn)
            prov["functions"] = str(f)
        else:
            notes.append(f"{f} lacks columns {need - set(fn.columns)}; using built-in functions")
            fn = b_fn.copy()
            prov["functions"] = BUILTIN
    else:
        fn = b_fn.copy()
        prov["functions"] = BUILTIN
    fa = fa.assign(function_id=fa.function_id.map(lambda x: fmap.get(x, x)))
    fn = fn.merge(fa, on="function_id", how="left")
    defaults = {"labor_share": 0.7, "iota_prior": 0.5, "rho_O": np.nan, "personal_data": 0, "high_reliability": 0,
                "compute_share_of_nonlabor": 0.0, "keywords": ""}
    for c, v in defaults.items():
        fn[c] = fn[c].fillna(v) if c in fn.columns else v
    for c in ["labor_share", "iota_prior", "rho_O", "personal_data", "high_reliability", "compute_share_of_nonlabor"]:
        fn[c] = pd.to_numeric(fn[c], errors="coerce")
    fn["keywords"] = fn["keywords"].fillna("").astype(str)
    fn["keywords"] = [k if k else str(nm).lower() for k, nm in zip(fn.keywords, fn.function_name)]

    # Function-level outsourcing price ratios from the data agent's params.yaml (keys like "F05 customer support").
    pf = data_file("params.yaml")
    if pf is not None:
        import yaml
        try:
            from .config import read_yaml
            pr_yaml = read_yaml(pf)
            ratios = ((pr_yaml.get("outsourcing") or {}).get("price_ratio_pO_over_wt") or {}).get("value") or {}
            ov = {str(k).split()[0]: float(v) for k, v in ratios.items() if v is not None}
            hit = fn.function_id.isin(list(ov))
            fn.loc[hit, "rho_O"] = fn.loc[hit, "function_id"].map(ov)
            if hit.any():
                prov["rho_O"] = f"{pf} outsourcing.price_ratio_pO_over_wt (assumed in that file)"
        except Exception as e:  # pragma: no cover - malformed file
            notes.append(f"params.yaml not read for outsourcing ratios: {e}")

    # ---- occupations -------------------------------------------------------------------------
    b_occ = _builtin("occupations.csv")
    f = data_file("occupations.csv")
    if f is not None:
        occ = _read_csv(f)
        occ["soc"] = occ[_pick(occ, "soc", "soc_code", "onet_soc")].map(norm_soc)
        occ = _num(occ, ["wage_median", "wage_mean", "employment", "physical_share", "licensed_signoff"])
        occ = occ.dropna(subset=["soc"]).drop_duplicates("soc")
        if "title" not in occ.columns:
            occ["title"] = occ["soc"]
        fam = dict(zip(b_occ.soc, b_occ.family))
        occ["family"] = [fam.get(s, soc_family(s)) for s in occ.soc]
        for c, dflt in [("physical_share", 0.0), ("licensed_signoff", 0)]:
            if c not in occ.columns:
                occ[c] = dflt
        # Fill missing wages from the built-in placeholder, flagged.
        bw = dict(zip(b_occ.soc, b_occ.wage_median))
        miss = occ.wage_median.isna() if "wage_median" in occ.columns else pd.Series(True, index=occ.index)
        if "wage_median" not in occ.columns:
            occ["wage_median"] = np.nan
        occ.loc[miss, "wage_median"] = occ.loc[miss, "soc"].map(bw)
        occ["wage_median"] = occ["wage_median"].fillna(occ["wage_median"].median())
        occ["wage_note"] = np.where(miss, "built-in placeholder (assumed)", f"data/tasks/{f.name}")
        # Keep built-in occupations the data lacks (fallback mixes may reference them).
        extra = b_occ[~b_occ.soc.isin(occ.soc)].copy()
        occ = pd.concat([occ, extra], ignore_index=True)
        prov["occupations"] = str(f)
    else:
        occ = b_occ.copy()
        prov["occupations"] = BUILTIN
    occ["physical_share"] = pd.to_numeric(occ["physical_share"], errors="coerce").fillna(0.0)
    occ["licensed_signoff"] = pd.to_numeric(occ["licensed_signoff"], errors="coerce").fillna(0).astype(int)

    # ---- activities --------------------------------------------------------------------------
    # The contract file is activities.csv at DWA level. While the data agent works at IWA level, the
    # interim files activities_iwa_interim.csv and occ_activity_iwa_interim.csv are used, with the IWA
    # as the activity unit (its id goes in the dwa_id column).
    b_act = _builtin("activities.csv")
    f = data_file("activities.csv")
    interim = False
    if f is None and data_file("activities_iwa_interim.csv") is not None:
        f = data_file("activities_iwa_interim.csv")
        interim = True
    if f is not None:
        act = _read_csv(f)
        if interim:
            act = act.rename(columns={"iwa_title": "dwa_title"})
            act["dwa_id"] = act["iwa_id"]
            if "eu_annex3_area" in act.columns:
                act["regulated_class"] = np.where(act["eu_annex3_area"].fillna("").str.strip() != "", "high_risk_eu", "none")
            notes.append("activities: interim IWA-level file used; the IWA is the activity unit until the DWA-level file lands")
        if "dwa_id" not in act.columns:
            notes.append(f"{f} lacks dwa_id; using built-in activities")
            act = b_act.copy()
            prov["activities"] = BUILTIN
        else:
            ecol = _pick(act, "exposure_llm", "exposure", "beta", "exposure_beta", "dv_rating_beta", "human_rating_beta")
            act["exposure_llm"] = pd.to_numeric(act[ecol], errors="coerce") if ecol else np.nan
            act = _num(act, ["physical", "ai_usage", "est_task_hours"])
            if act["exposure_llm"].isna().all() and data_file("occ_exposure.csv") is not None:
                act["exposure_llm"] = _exposure_from_occupations(data_file("occ_exposure.csv"),
                                                                 data_file("occ_activity.csv") or data_file("occ_activity_iwa_interim.csv"),
                                                                 act["dwa_id"], interim)
                act["exposure_measure"] = "eloundou_gpt4_beta, occupation-level, weighted by employment x time share"
                notes.append("activities: exposure derived from occupation-level Eloundou et al. GPT-4 beta (occ_exposure.csv)")
            for c, dflt in [("physical", 0), ("est_task_hours", np.nan), ("regulated_class", "none"), ("gwa_id", None),
                            ("dwa_title", None), ("gwa_title", None), ("iwa_id", None), ("ai_usage", np.nan)]:
                if c not in act.columns:
                    act[c] = dflt
            if act["gwa_id"].isna().all():
                act["gwa_id"] = act["dwa_id"].str.extract(r"^(4\.A\.\d\.[a-z]\.\d+)")[0]
            act["regulated_class"] = act["regulated_class"].fillna("none").str.strip().str.lower()
            # Fill gaps from the GWA-level fallback, flagged.
            g = b_act.set_index("gwa_id")
            nexp = act.exposure_llm.isna()
            act.loc[nexp, "exposure_llm"] = act.loc[nexp, "gwa_id"].map(g.exposure_llm)
            nh = act.est_task_hours.isna()
            act.loc[nh, "est_task_hours"] = act.loc[nh, "gwa_id"].map(g.est_task_hours)
            act["exposure_llm"] = act["exposure_llm"].fillna(0.5)
            act["est_task_hours"] = act["est_task_hours"].fillna(1.0)
            act["physical"] = act["physical"].fillna(0)
            if nexp.any() or nh.any():
                notes.append(f"activities: {int(nexp.sum())} exposure and {int(nh.sum())} task-hour values filled from the GWA fallback")
            # Keep the GWA-level rows too: residual buckets and fallback processes use them.
            act = pd.concat([act, b_act[~b_act.dwa_id.isin(act.dwa_id)]], ignore_index=True)
            prov["activities"] = str(f)
    else:
        act = b_act.copy()
        prov["activities"] = BUILTIN
    act["exposure_llm"] = pd.to_numeric(act["exposure_llm"], errors="coerce").clip(0, 1)
    act["est_task_hours"] = pd.to_numeric(act["est_task_hours"], errors="coerce").clip(lower=0.01)
    act["physical"] = pd.to_numeric(act["physical"], errors="coerce").fillna(0).clip(0, 1)
    act = act.drop_duplicates("dwa_id")

    # ---- occupation to activity time shares --------------------------------------------------
    f = data_file("occ_activity.csv")
    oa_interim = False
    if f is None and interim and data_file("occ_activity_iwa_interim.csv") is not None:
        f = data_file("occ_activity_iwa_interim.csv")
        oa_interim = True
    prof = _builtin("activity_profiles.csv")
    keymap = dict(zip(_builtin("activity_attributes.csv").key, _builtin("activity_attributes.csv").gwa_id))
    prof["dwa_id"] = prof.gwa_key.map(keymap)
    fam_rows = []
    for o in occ.itertuples():
        pp = prof[prof.family == o.family]
        fam_rows.append(pd.DataFrame({"soc": o.soc, "dwa_id": pp.dwa_id.values, "time_share": pp.share.values}))
    fam_oa = pd.concat(fam_rows, ignore_index=True)
    if f is not None:
        oa = _read_csv(f)
        if oa_interim:
            oa["dwa_id"] = oa["iwa_id"]
        oa["soc"] = oa[_pick(oa, "soc", "onet_soc", "soc_code")].map(norm_soc)
        oa = _num(oa, ["time_share"]).dropna(subset=["soc", "dwa_id", "time_share"])
        oa = oa.groupby(["soc", "dwa_id"], as_index=False).time_share.sum()
        oa["time_share"] = oa.time_share / oa.groupby("soc").time_share.transform("sum")
        missing = sorted(set(occ.soc) - set(oa.soc))
        oa = pd.concat([oa[["soc", "dwa_id", "time_share"]], fam_oa[fam_oa.soc.isin(missing)]], ignore_index=True)
        if missing:
            notes.append(f"occ_activity: {len(missing)} occupations not in the data use the built-in family profiles")
        prov["occ_activity"] = str(f)
    else:
        oa = fam_oa
        prov["occ_activity"] = BUILTIN
    known = set(act.dwa_id)
    dropped = oa[~oa.dwa_id.isin(known)]
    if len(dropped):
        notes.append(f"occ_activity: {dropped.dwa_id.nunique()} DWA ids not in activities.csv dropped")
        oa = oa[oa.dwa_id.isin(known)]
        oa["time_share"] = oa.time_share / oa.groupby("soc").time_share.transform("sum")

    # ---- function to occupation mix ----------------------------------------------------------
    b_fo = _builtin("function_occ.csv")
    f = data_file("function_occ.csv")
    if f is not None:
        fo = _read_csv(f)
        fo["soc"] = fo[_pick(fo, "soc", "onet_soc")].map(norm_soc)
        fo = _num(fo, ["weight"]).dropna(subset=["soc", "weight"])
        prov["function_occ"] = str(f)
        miss = [fid for fid in fn.function_id if fid not in set(fo.function_id)]
        if miss:
            add = b_fo.assign(function_id=b_fo.function_id.map(lambda x: fmap.get(x, x)))
            fo = pd.concat([fo, add[add.function_id.isin(miss)]], ignore_index=True)
            notes.append(f"function_occ: {len(miss)} functions use the built-in mix")
    else:
        fo = b_fo.assign(function_id=b_fo.function_id.map(lambda x: fmap.get(x, x)))
        prov["function_occ"] = BUILTIN
    fo = fo[fo.soc.isin(set(occ.soc))]
    fo["weight"] = fo.weight / fo.groupby("function_id").weight.transform("sum")
    fo_ind = None
    f = data_file("function_occ_by_industry.csv")
    if f is not None:
        fo_ind = _read_csv(f)
        fo_ind["soc"] = fo_ind["soc"].map(norm_soc)
        fo_ind = _num(fo_ind, ["weight"]).dropna(subset=["soc", "weight"])
        fo_ind = fo_ind[fo_ind.soc.isin(set(occ.soc))]
        prov["function_occ_by_industry"] = str(f)

    # ---- industry function shares --------------------------------------------------------------
    b_ifs = _builtin("industry_function_shares.csv")
    f = data_file("industry_function_shares.csv")
    if f is not None:
        ifs = _read_csv(f)
        mcol = _pick(ifs, "share_mean", "share_of_revenue_prior_mean", "share_of_revenue_prior", "mean")
        scol = _pick(ifs, "share_sd", "share_of_revenue_prior_sd", "sd")
        icol = _pick(ifs, "naics", "naics_prefix", "sic", "industry")
        if mcol and icol:
            ifs = ifs.rename(columns={mcol: "share_mean"})
            ifs["industry"] = ifs[icol].astype(str)
            ifs["naics_prefix"] = ifs[icol].map(lambda x: "/".join(re.findall(r"\d{2,6}", "" if x is None or (isinstance(x, float) and x != x) else str(x))))
            ifs["share_sd"] = pd.to_numeric(ifs[scol], errors="coerce") if scol else np.nan
            ifs["share_mean"] = pd.to_numeric(ifs["share_mean"], errors="coerce")
            ifs["share_sd"] = ifs["share_sd"].fillna(ifs["share_mean"] * 0.35)
            ifs["size_band"] = ifs["size_band"] if "size_band" in ifs.columns else "any"
            for c, dflt in (("prior_basis", "data"), ("damodaran_industry", "")):
                ifs[c] = ifs[c].fillna(dflt).astype(str) if c in ifs.columns else dflt
            ifs = pd.concat([ifs[["industry", "naics_prefix", "size_band", "function_id", "share_mean", "share_sd", "prior_basis",
                                  "damodaran_industry"]],
                             b_ifs.assign(function_id=b_ifs.function_id.map(lambda x: fmap.get(x, x)), prior_basis="builtin",
                                          damodaran_industry="")], ignore_index=True)
            prov["industry_function_shares"] = str(f) + " (built-in rows as fallback)"
        else:
            notes.append(f"{f}: columns not recognized; using built-in industry shares")
            ifs = b_ifs.copy()
            prov["industry_function_shares"] = BUILTIN
    else:
        ifs = b_ifs.assign(function_id=b_ifs.function_id.map(lambda x: fmap.get(x, x)), prior_basis="builtin", damodaran_industry="")
        prov["industry_function_shares"] = BUILTIN
    if "prior_basis" not in ifs.columns:
        ifs["prior_basis"], ifs["damodaran_industry"] = "builtin", ""

    # ---- ICFR scope (spec 24.4; class b: PCAOB AS 2201 significant accounts and relevant assertions, ITGCs and
    # common SOX process scoping). The data contract is the single source: processes.csv icfr_scope and
    # process_activities.csv icfr_step, icfr_channel, icfr_condition, typical_systems, financial_system_written
    # (code/data_part2/07_processes.py). The engine's snapshot (priors/icfr_*.csv, tools/sync_icfr_priors.py) is
    # used only when those columns are missing. -------------------------------------------------------------
    icfr_sc, icfr_st = _builtin("icfr_scope.csv"), _builtin("icfr_steps.csv")
    prov["icfr_scope"] = BUILTIN + " snapshot (priors/icfr_scope.csv, icfr_steps.csv)"
    pf, af = data_file("processes.csv"), data_file("process_activities.csv")
    if pf is not None and af is not None:
        d_pr, d_pa = _read_csv(pf), _read_csv(af)
        if "icfr_scope" in d_pr.columns and "icfr_step" in d_pa.columns:
            icfr_sc = d_pr[[c for c in ("process_id", "process_name", "icfr_scope", "icfr_basis") if c in d_pr.columns]].copy()
            keep = [c for c in ("process_id", "step", "dwa_id", "step_name", "icfr_step", "icfr_condition", "icfr_channel",
                                "icfr_basis", "icfr_source", "typical_systems", "financial_system_written") if c in d_pa.columns]
            icfr_st = d_pa[keep].copy()
            prov["icfr_scope"] = f"{pf}; {af} (data contract)"
    icfr_sc = icfr_sc.copy()
    icfr_sc["icfr_scope"] = icfr_sc.icfr_scope.fillna("none").astype(str).str.strip().str.lower()
    icfr_st = icfr_st.copy()
    for c in ("icfr_condition", "icfr_channel", "icfr_basis", "icfr_source", "typical_systems", "financial_system_written", "step_name"):
        icfr_st[c] = icfr_st[c].fillna("").astype(str) if c in icfr_st.columns else ""
    icfr_st["icfr_step"] = icfr_st.icfr_step.astype(str).str.strip().str.lower().isin(["true", "1", "yes"])

    # ---- industry benchmarks (Damodaran, January 2026) and their NAICS crosswalk (spec 24.10) ----------
    bench, xw = None, None
    f1, f2 = data_file("industry_benchmarks.csv"), data_file("xw_damodaran_naics.csv")
    if f1 is not None and f2 is not None:
        bench = _read_csv(f1)
        bench = _num(bench, ["k_ic_per_sales", "k_ic_per_sales_unadj", "k_ic_per_sales_lease", "k_ic_per_sales_lease_rnd",
                             "cost_of_capital", "n_firms", "small_sample", "financial_group", "cogs_sales", "rnd_sales",
                             "sga_sales", "gross_margin", "op_margin_pretax", "roic_minus_wacc", "reinvestment_rate"])
        xw = _read_csv(f2)
        prov["industry_benchmarks"] = f"{f1}; {f2} (Damodaran, data as of January 2026)"
    else:
        prov["industry_benchmarks"] = "not available (finance defaults apply)"

    # ---- industry staffing (optional) --------------------------------------------------------
    f = data_file("industry_staffing.csv")
    staffing = None
    if f is not None:
        staffing = _read_csv(f)
        staffing["soc"] = staffing[_pick(staffing, "soc", "onet_soc")].map(norm_soc)
        staffing = _num(staffing, ["emp_share"])
        prov["industry_staffing"] = str(f)
    else:
        prov["industry_staffing"] = "not available"

    # ---- processes -----------------------------------------------------------------------------
    b_pr = _builtin("processes.csv")
    b_pa = _builtin("process_activities.csv")
    f1, f2 = data_file("processes.csv"), data_file("process_activities.csv")
    if f1 is not None and f2 is not None:
        pr = _read_csv(f1)
        pa = _read_csv(f2)
        pr = _num(pr, ["typical_volume_per_musd_revenue", "volume_other"])
        if "volume_basis" in pr.columns:
            fixed = pr["volume_basis"].fillna("").str.contains("fixed")
            pr["fixed_volume_per_year"] = np.where(fixed, pr.get("volume_other"), np.nan)
        pa = _num(pa, ["step", "critical_path", "hours_per_unit"] + [c for c in ("physical_override", "licensed_override") if c in pa.columns])
        if "iwa_id" in pa.columns:
            empty = pa["dwa_id"].isna() | (pa["dwa_id"].astype(str).str.strip() == "")
            if interim:
                pa.loc[empty, "dwa_id"] = pa.loc[empty, "iwa_id"]
            else:
                pa = pa[~empty]
        for c, dflt in [("critical_path", 1), ("hours_per_unit", np.nan), ("regulated_class_override", np.nan)]:
            if c not in pa.columns:
                pa[c] = dflt
        if "volume_source" not in pr.columns:
            pr["volume_source"] = "data/tasks/processes.csv"
        pa = pa[pa.dwa_id.isin(set(act.dwa_id))]
        # Steps without hours: estimated task hours of the activity.
        nh = pa.hours_per_unit.isna()
        pa.loc[nh, "hours_per_unit"] = pa.loc[nh, "dwa_id"].map(act.set_index("dwa_id").est_task_hours)
        pr = pr[pr.process_id.isin(set(pa.process_id))]
        miss_fn = [fid for fid in fn.function_id if fid not in set(pr.function_id)]
        if miss_fn:
            bpr = b_pr.assign(function_id=b_pr.function_id.map(lambda x: fmap.get(x, x)))
            add = bpr[bpr.function_id.isin(miss_fn) & ~bpr.process_id.isin(pr.process_id)]
            pr = pd.concat([pr, add], ignore_index=True)
            pa = pd.concat([pa, b_pa[b_pa.process_id.isin(add.process_id)]], ignore_index=True)
            notes.append(f"processes: {len(add)} built-in processes added for functions the library does not cover")
        prov["processes"] = f"{f1}; {f2}"
    else:
        pr = b_pr.assign(function_id=b_pr.function_id.map(lambda x: fmap.get(x, x)))
        pa = b_pa.copy()
        prov["processes"] = BUILTIN
    pr["typical_volume_per_musd_revenue"] = pd.to_numeric(pr["typical_volume_per_musd_revenue"], errors="coerce")
    pa["step"] = pd.to_numeric(pa["step"], errors="coerce")
    pa["critical_path"] = pd.to_numeric(pa["critical_path"], errors="coerce").fillna(1).astype(int)
    pa["hours_per_unit"] = pd.to_numeric(pa["hours_per_unit"], errors="coerce")
    pr = pr[pr.function_id.isin(set(fn.function_id))]

    # ---- O*NET titles for fuzzy matching: O*NET 31.0 alternate titles and occupation titles ------
    onet_titles = None
    raw_onet = (d.parent / "raw" / "onet_31_0") if d is not None else None
    if raw_onet is not None and (raw_onet / "job_titles.csv").is_file():
        jt = _read_csv(raw_onet / "job_titles.csv")
        parts = [pd.DataFrame({"soc": jt["onetsoc_code"].map(norm_soc), "title": jt["job_title"].astype(str)})]
        if (raw_onet / "occupation_data.csv").is_file():
            od = _read_csv(raw_onet / "occupation_data.csv")
            parts.append(pd.DataFrame({"soc": od["onetsoc_code"].map(norm_soc), "title": od["title"].astype(str)}))
        parts.append(occ[["soc", "title"]])
        onet_titles = pd.concat(parts, ignore_index=True).dropna().drop_duplicates()
        onet_titles = onet_titles[onet_titles.soc.isin(set(occ.soc))]
        prov["onet_titles"] = f"{raw_onet / 'job_titles.csv'} and occupation_data.csv (O*NET 31.0)"
    for nm in ("onet_titles.csv", "alternate_titles.csv", "occupation_titles.csv"):
        if onet_titles is not None:
            break
        f = data_file(nm)
        if f is not None:
            t = _read_csv(f)
            scol = _pick(t, "soc", "onet_soc", "o*net-soc code", "onet_soc_code")
            tcol = _pick(t, "title", "alternate_title", "alternate title", "reported_job_title")
            if scol and tcol:
                onet_titles = pd.DataFrame({"soc": t[scol].map(norm_soc), "title": t[tcol].astype(str)}).dropna()
                prov["onet_titles"] = str(f)
                break
    if onet_titles is None:
        onet_titles = occ[["soc", "title"]].copy()
        prov["onet_titles"] = "occupation titles from " + prov["occupations"]

    # ---- O*NET task statements (playbook evidence; optional contract files) ---------------------
    tasks, xwt, t_attr = None, None, None
    ft, fx = data_file("task_statements.csv"), data_file("xw_task_dwa.csv")
    if ft is not None and fx is not None:
        tasks = _read_csv(ft)
        tasks["task_id"] = pd.to_numeric(tasks["task_id"], errors="coerce")
        tasks["incumbents_responding"] = pd.to_numeric(tasks.get("incumbents_responding"), errors="coerce")
        xwt = _read_csv(fx)[["task_id", "dwa_id", "soc"]].copy()
        xwt["task_id"] = pd.to_numeric(xwt["task_id"], errors="coerce")
        prov["task_statements"] = f"{ft}; {fx}"
        fd = data_file("data_dictionary.csv")
        if fd is not None:
            dd_ = _read_csv(fd)
            row = dd_[(dd_.get("file") == "task_statements.csv") & (dd_.get("column") == "(file)")] if "file" in dd_.columns else dd_.iloc[0:0]
            if len(row) and "attribution" in row.columns:
                t_attr = str(row.attribution.iat[0])

    return Priors(functions=fn, occupations=occ, activities=act, occ_activity=oa, function_occ=fo,
                  industry_function_shares=ifs, industry_staffing=staffing, processes=pr, process_activities=pa,
                  function_occ_by_industry=fo_ind, industry_benchmarks=bench, xw_damodaran=xw, icfr_scope=icfr_sc, icfr_steps=icfr_st,
                  title_rules=_builtin("title_rules.csv"), gl_rules=_builtin("gl_rules.csv"),
                  vendor_rules=_builtin("vendor_rules.csv"),
                  vendor_categories=_builtin("vendor_categories.csv").assign(
                      function_id=lambda x: x.function_id.map(lambda y: fmap.get(y, y))),
                  locations=_builtin("locations.csv"), onet_titles=onet_titles,
                  task_statements=tasks, xw_task_dwa=xwt, task_attribution=t_attr,
                  provenance=prov, notes=notes, data_dir=str(d) if d else None)
