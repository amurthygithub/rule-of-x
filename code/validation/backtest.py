#!/usr/bin/env python3
"""Backtest of the Part II task-level model (unified spec Section 24.1).

Run from anywhere:   python3 -I code/validation/backtest.py        (about one minute; deterministic)

Question
  At parameters available at the end of 2021, the model of Section sec:tasks scores every activity (an O*NET
  detailed work activity, DWA, performed in an occupation) for whether automation (mode A) is feasible and
  cost-minimizing: exposure x capability feasibility x cost crossover, with the stakes-targeted review share of
  prop:tasks-review and the capability path of ass:ext-capability. Do occupations the model scores as more
  automatable show lower growth of employment, wage-bill share and mean wage between OEWS May 2021 and May 2025,
  and does the score predict beyond LLM exposure alone? Do SEC software firms whose function mix the model scores
  as more automatable show larger declines in cost shares between FY2021-22 and FY2024-25?

What "2021 parameters" means here
  - wages: OEWS May 2021 national (redistributed in the GPTs-are-GPTs repository);
  - exposure: Eloundou et al. task labels (GPT-4 beta, O*NET 27.2 tasks), occupation-specific by task ID;
  - capability: the 50% horizon path of data/tasks/params.yaml (METR TH1.1 fit, H0 = 11.98 h at 2026-02-05,
    doubling 143 days), evaluated from the end-2021 state forward over the window. At end-2021 the horizon is
    about 30 seconds, so no activity passes the capability test for A at that date (the static score is zero
    everywhere; reported). The main score is therefore the model's own forward object: the share of exposed
    activity time for which A is optimal, averaged over Dec 2021 to May 2025 along the capability and price
    paths (prop:tasks-curve(b), prop:ext-feasible). Variants use the end-of-window share, slower or fitted paths.
  - task length: the O*NET-only frequency identity (activities.hours_identity_median) in the main score, because
    the AEI task times (est_task_hours) exist only for DWAs used with Claude in 2026, which would leak outcome
    information; the AEI times are a robustness variant.
  - inference price: frontier price per human-hour from params.yaml (the model assumes a flat frontier price);
    a 10x price is a robustness variant.

Inputs (all local; see notes/backtest_notes.md for the crosswalks)
  data/raw/gpts_are_gpts/repo/data/national_May2021_dl.csv     OEWS May 2021 national (SOC 2018)
  data/raw/bls_oews_2025/oesm25nat.zip                          OEWS May 2025 national (SOC 2018)
  data/raw/gpts_are_gpts/repo/data/autoScores.csv               SOC 2010 cross-section (tot_emp, a_mean), vintage
                                                                undocumented, consistent with OEWS May 2016; used
                                                                only for the pre-period placebo and trend control
  data/raw/gpts_are_gpts/repo/data/occupations_projections_processed.csv   BLS 2020-30 projections (Sept 2021)
  data/raw/gpts_are_gpts/repo/data/full_labelset.tsv            Eloundou task labels
  data/raw/onet_31_0/job_zones.csv                              O*NET job zones
  data/tasks/{occ_activity,activities,occupations,occ_exposure,xw_task_dwa,xw_oews_onetsoc,function_occ,
              function_occ_by_industry,industry_function_shares,functions}.csv, params.yaml, _build/capability.json
  engine/src/autofrontier/defaults.yaml, engine/src/autofrontier/priors/activity_attributes.csv
  data/panel_v2_all.csv                                         SEC firm-years (SIC 7370-7374)

Outputs
  notes/backtest_results.json
  part2/tables/backtest_occ.tex, backtest_sweep.tex, backtest_decomp.tex, backtest_robust.tex, backtest_firm.tex,
  backtest_tests.tex, and backtest_macros.tex (every number quoted in part2/validation_backtest.tex, as \newcommand)

Runtime about 3.5 minutes, mostly the review-time-ratio sweep (0.01 grid over the sourced range).
"""
from __future__ import annotations

import os

# single-threaded linear algebra, so that results are bit-for-bit reproducible across runs
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import hashlib
import io
import json
import math
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
from exclusions import is_excluded  # noqa: E402  registrants excluded at the author's request
RAW = ROOT / "data" / "raw"
TASKS = ROOT / "data" / "tasks"
ENGINE = ROOT / "engine" / "src" / "autofrontier"
OUT_JSON = ROOT / "notes" / "backtest_results.json"
TAB = ROOT / "part2" / "tables"

F_OEWS21 = RAW / "gpts_are_gpts/repo/data/national_May2021_dl.csv"
F_OEWS25 = RAW / "bls_oews_2025/oesm25nat.zip"
F_OEWS16 = RAW / "gpts_are_gpts/repo/data/autoScores.csv"
F_PROJ = RAW / "gpts_are_gpts/repo/data/occupations_projections_processed.csv"
F_LABELS = RAW / "gpts_are_gpts/repo/data/full_labelset.tsv"
F_JZ = RAW / "onet_31_0/job_zones.csv"
F_PANEL = ROOT / "data" / "panel_v2_all.csv"
F_OEWS21_IND = RAW / "bls_oews_2021/oesm21in4.zip"       # OEWS May 2021 industry-specific (NAICS 2017), supplied 29 Oct
F_OEWS25_IND = RAW / "bls_oews_2025/oesm25in4.zip"       # OEWS May 2025 industry-specific (NAICS 2022)
F_SOCXW = RAW / "bls_soc/soc_2010_to_2018_crosswalk.xlsx"  # BLS SOC 2010 to 2018 crosswalk, November 2017
F_OEWS19 = RAW / "bls_oews_2019/oesm19nat.zip"           # OEWS May 2019 national (hybrid SOC 2010/2018), supplied 29 Oct
F_OEWS20 = RAW / "bls_oews_2020/oesm20nat.zip"           # OEWS May 2020 national (hybrid SOC 2010/2018), supplied 29 Oct
# The 2016 cross-section in autoScores.csv was verified against BLS's May 2016 national tables (read in a browser by
# the coordinator, 29 Oct 2026): all 737 occupations match; these sums match too. The script asserts them.
VERIFIED_2016 = {"url": "https://www.bls.gov/oes/2016/may/oes_nat.htm", "accessed": "2026-10-29",
                 "n_occupations": 737, "sum_tot_emp": 133977150, "sum_a_mean": 43494840,
                 "bls_detailed_occupations_listed": 820}
MIN_CELL_EMP = 1000      # occupation x industry cells: May 2021 employment at least this, reported in both vintages
CELL_CV_REPS = 10        # repetitions of the occupation-grouped cross-validation for cells (each fit is large)
CELL_GRID_STEP = 0.05    # review-ratio grid for the cell-level sweep
# NAICS 2017 (May 2021) to NAICS 2022 (May 2025) harmonization at four digits. Retail trade (44-45) is taken at the
# sector level, because NAICS 2022 folded nonstore retailers into the product-line retailers.
IND_REMAP = {"511100": "5131", "513100": "5131",                       # publishers (renumbered)
             "511200": "5132", "513200": "5132",                       # software publishers (renumbered)
             "515100": "51X", "515200": "51X", "519100": "51X",        # broadcasting, cable and other information
             "516100": "51X", "516200": "51X", "519200": "51X"}       # (content reallocated; combined)

SEED0 = 20211231
RHO_PRE_AUDIT = 0.8      # engine default review.rho_rev before it was linked to the audited value (assumed)
N_TESTS = 28             # size of the multiple-testing family (Table backtest-tests)
N_TESTS_PREVIOUS = 20    # the family reported before the industry, crosswalk and 2019 tests were added
N_CV_REPS = 50
K_FOLDS = 10

# Judgment-based exclusion sets for confounder checks (documented in notes/backtest_notes.md)
TECH_SOC_PREFIX = ("15-",)                       # computer and mathematical occupations
TECH_SOC_EXTRA = {"11-3021"}                     # computer and information systems managers
RATE_SENSITIVE = {"13-2072", "43-4131", "41-9021", "41-9022", "13-2023", "43-4041", "13-2041"}
COVID_GROUPS = {"35", "39", "27"}                # food preparation, personal care, arts and entertainment


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(",", "", regex=False).str.strip(), errors="coerce")


def date_to_year(s: str) -> float:
    ts = pd.Timestamp(s)
    start = pd.Timestamp(year=ts.year, month=1, day=1)
    return ts.year + (ts - start).days / 365.25


def expit(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -60, 60)))


# =============================================================================================================
# 1. Parameters
# =============================================================================================================

def load_parameters() -> dict:
    P = yaml.safe_load(open(TASKS / "params.yaml"))
    D = yaml.safe_load(open(ENGINE / "defaults.yaml"))
    cap = P["capability_path"]
    dv = lambda sec, key: D[sec][key]["value"]
    b = float(cap["logistic_slope_b"]["value"])
    chi = lambda r: 2.0 ** (math.log(r / (1 - r)) / b)
    capj = json.load(open(TASKS / "_build" / "capability.json"))
    th10 = capj["th10_point_estimates"]["2019-01-01"]
    par = {
        # capability path, params.yaml (METR TH1.1 refit and Kwa et al. 2025)
        "H0": float(cap["H0_hours_p50"]["value"]),
        "t0": date_to_year(str(cap["t0"]["value"])),
        "Td_days": float(cap["T_d_days"]["value"]),
        "Td_days_slow": float(cap["T_d_scenarios_days"]["slow"]),
        "b": b,
        "L_W": float(cap["physical_lag_years"]["value"]),
        "r_A": float(dv("capability", "r_A")),
        "r_U": float(dv("capability", "r_U")),
        "chi_A": chi(float(dv("capability", "r_A"))),
        "chi_U": 1.0,
        # METR TH1.0 fit 2019+ (ln p50 in minutes, OLS on release date): an alternative, earlier-anchored path
        "th10_ln_p50_min_2019": float(th10["ln_p50_at_2019"]),
        "th10_slope_per_day": float(th10["slope_per_day"]),
        # readiness and errors (engine defaults; core notes 4.2)
        "e0": float(dv("capability", "e0")),
        "e1": float(dv("capability", "e1")),
        "iota": 0.5,
        # review (engine defaults)
        "rho_rev": float(dv("review", "rho_rev")),
        "wage_premium": float(dv("review", "wage_premium")),
        "L_mult_regulated": float(dv("review", "L_mult_regulated")),
        "r_bar_licensed": float(dv("review", "r_bar_licensed")),
        "xi_min": {k: float(v) for k, v in P["regulatory_oversight_floor_psi_min"]["value"].items()},
        "licensed_share_threshold": float(dv("permissibility", "licensed_share_threshold")),
        "licensed_blocks_A": bool(dv("permissibility", "licensed_blocks_A")),
        # prices (params.yaml; engine defaults for the assumed pieces)
        "pi_h": float(P["ai_cost"]["inference_cost_usd_per_human_hour"]["value"]
                      ["frontier_tier (Claude Mythos 5.1 / Fable 5.1)"]),
        "delta_pi": float(P["inference_price"]["delta_pi_continuous"]["value"]),
        "floor_share": float(dv("prices", "floor_share")),
        "u_tok": float(dv("prices", "u_tok")),
        "retry_cap": float(dv("prices", "retry_cap")),
        "class_mult": {k: float(v) for k, v in dv("prices", "class_multiplier").items()},
        # augmentation and outsourcing
        "beta_U": float(P["ai_cost"]["augmentation_gain_beta_U"]["value"]),
        "exposure_ref": float(dv("augment", "exposure_ref")),
        "rho_O": float(dv("outsourcing", "rho_O_default")),
        "kappa_O": float(P["outsourcing"]["coordination_overhead_kappa_O"]["value"]),
        "zeta_O": float(P["outsourcing"]["risk_premium_zeta_O"]["value"]),
        "delta_O": float(P["outsourcing"]["vendor_price_decline_per_year"]["value"]),
        "separable_threshold": float(dv("outsourcing", "separable_threshold")),
        # loading of the OEWS hourly rate per hour worked (BLS ECEC, params.yaml)
        "tau_L_hour": float(P["payroll_loading"]["tau_L_per_hour_worked"]["value"]),
        # dates
        "t_freeze": 2022.0,                # end of 2021: the parameter freeze
        "t_may21": date_to_year("2021-05-12"),
        "t_may25": date_to_year("2025-05-12"),
        "grid_step": 1.0 / 24.0,
    }
    return par


# =============================================================================================================
# 2. Occupation data: OEWS vintages, crosswalks, controls
# =============================================================================================================

def load_oews_2021() -> pd.DataFrame:
    a = pd.read_csv(F_OEWS21, encoding="utf-8-sig", dtype=str)
    a = a[a.O_GROUP == "detailed"].copy()
    out = pd.DataFrame({"soc": a.OCC_CODE.values, "title": a.OCC_TITLE.values,
                        "emp": num(a.TOT_EMP).values, "a_mean": num(a.A_MEAN).values,
                        "h_mean": num(a.H_MEAN).values})
    return out


def load_oews_2025() -> pd.DataFrame:
    z = zipfile.ZipFile(F_OEWS25)
    name = [n for n in z.namelist() if n.endswith(".xlsx")][0]
    b = pd.read_excel(io.BytesIO(z.read(name)), dtype=str)
    b = b[b.O_GROUP == "detailed"].copy()
    return pd.DataFrame({"soc": b.OCC_CODE.values, "title": b.OCC_TITLE.values, "emp": num(b.TOT_EMP).values,
                         "a_mean": num(b.A_MEAN).values, "h_mean": num(b.H_MEAN).values})


def fill_wages(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["wage_imputed"] = d.a_mean.isna() & d.h_mean.notna()
    d["a_mean"] = d.a_mean.fillna(d.h_mean * 2080.0)      # hourly-only occupations (actors, dancers, ...)
    d["h_mean"] = d.h_mean.fillna(d.a_mean / 2080.0)      # annual-only occupations (teachers, ...)
    return d


def load_oews_2016() -> pd.DataFrame:
    """OEWS May 2016 national estimates for 737 SOC 2010 occupations, as carried in autoScores.csv (the file repeats
    one cross-section under a 2011-2019 year index; the 2016 rows are used). Verified: see VERIFIED_2016."""
    s = pd.read_csv(F_OEWS16)
    g = s.groupby("simpleOcc")[["tot_emp", "a_mean"]].nunique()
    assert (g.max() == 1).all(), "autoScores no longer repeats one cross-section"
    s = s[s.year == 2016][["simpleOcc", "tot_emp", "a_mean"]]
    assert len(s) == VERIFIED_2016["n_occupations"]
    assert int(round(s.tot_emp.sum())) == VERIFIED_2016["sum_tot_emp"]
    assert int(round(s.a_mean.sum())) == VERIFIED_2016["sum_a_mean"]
    return s.rename(columns={"simpleOcc": "soc", "tot_emp": "emp16", "a_mean": "a_mean16"})


def load_oews_hybrid(zp: Path) -> pd.DataFrame:
    """OEWS May 2019 or May 2020 national file (hybrid SOC structure): detailed rows with employment and mean wage."""
    z = zipfile.ZipFile(zp)
    name = [n for n in z.namelist() if n.endswith(".xlsx")][0]
    d = pd.read_excel(io.BytesIO(z.read(name)), dtype=str)
    d.columns = [c.upper() for c in d.columns]
    d = d[d.O_GROUP == "detailed"]
    out = pd.DataFrame({"soc": d.OCC_CODE.values, "title": d.OCC_TITLE.values, "emp": num(d.TOT_EMP).values,
                        "a_mean": num(d.A_MEAN).values, "h_mean": num(d.H_MEAN).values})
    return fill_wages(out)


def load_soc_crosswalk() -> pd.DataFrame:
    """BLS SOC 2010 to SOC 2018 crosswalk (November 2017), sheet "Sorted by 2010". Untrusted file: read as data."""
    x = pd.read_excel(F_SOCXW, sheet_name="Sorted by 2010", header=None, dtype=str)
    hdr = int(np.flatnonzero(x.iloc[:, 0].astype(str).str.strip().values == "2010 SOC Code")[0])
    x = x.iloc[hdr + 1:, :4].copy()
    x.columns = ["c10", "t10", "c18", "t18"]
    x = x.dropna(subset=["c10", "c18"])
    for c in ["c10", "c18"]:
        x[c] = x[c].astype(str).str.strip()
    assert (x.c10.str.fullmatch(r"\d\d-\d{4}") & x.c18.str.fullmatch(r"\d\d-\d{4}")).all()
    return x.reset_index(drop=True)


def pre_period_crosswalk(o16: pd.DataFrame, o21: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """2016 values in SOC 2018 terms through the official crosswalk. Nodes are SOC 2010 codes, SOC 2018 codes and
    OEWS May 2021 codes (a SOC 2018 code absent from OEWS maps to the unique OEWS aggregate sharing its first six
    characters, e.g. 13-1021 to 13-1020). Each connected component is one comparable unit. A May 2021 occupation is
    'exact' if its component has every SOC 2010 member in the 2016 file, every SOC 2018 member in OEWS 2021, and no
    other May 2021 occupation; 'allocated' if complete but shared with other May 2021 occupations (each member then
    carries the component's change, which equals allocating 2016 employment by 2021 shares); else 'incomplete'."""
    x = load_soc_crosswalk()
    oews21 = set(o21.soc)
    pref: dict = {}
    for c in sorted(oews21 - set(x.c18)):
        pref.setdefault(c[:6], []).append(c)

    def map18(c):
        if c in oews21:
            return c
        cand = pref.get(c[:6], [])
        return cand[0] if len(cand) == 1 else None

    x["o21"] = x.c18.map(map18)
    parent: dict = {}

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    for r in x.itertuples():
        union(("10", r.c10), ("18", r.c18))
        if isinstance(r.o21, str):
            union(("18", r.c18), ("21", r.o21))
    comps: dict = {}
    for node in sorted(parent):
        comps.setdefault(find(node), []).append(node)
    e16 = o16.set_index("soc")
    e21 = o21.set_index("soc")
    rows = []
    for key in sorted(comps):
        nodes = comps[key]
        c10 = [n[1] for n in nodes if n[0] == "10"]
        c18 = [n[1] for n in nodes if n[0] == "18"]
        c21 = [n[1] for n in nodes if n[0] == "21"]
        if not c21:
            continue
        ok16 = all(c in e16.index for c in c10) and all(np.isfinite(e16.emp16.get(c, np.nan)) for c in c10)
        ok18 = all(map18(c) is not None for c in c18) and all(c in e21.index for c in c21)
        E16 = float(sum(e16.emp16[c] for c in c10 if c in e16.index))
        W16 = float(sum(e16.emp16[c] * e16.a_mean16[c] for c in c10 if c in e16.index))
        okw16 = all(np.isfinite(e16.a_mean16.get(c, np.nan)) for c in c10)
        E21 = float(sum(e21.emp[c] for c in c21 if c in e21.index))
        W21 = float(sum(e21.emp[c] * e21.a_mean[c] for c in c21 if c in e21.index))
        kind = ("exact" if len(c21) == 1 else "allocated") if (ok16 and ok18) else "incomplete"
        for c in c21:
            rows.append({"soc": c, "xw_kind": kind, "xw_n10": len(c10), "xw_n21": len(c21), "xw_E16": E16,
                         "xw_E21": E21, "xw_w16": W16 / E16 if (E16 > 0 and okw16) else np.nan,
                         "xw_w21": W21 / E21 if E21 > 0 else np.nan, "xw_members21": "|".join(c21)})
    out = pd.DataFrame(rows).drop_duplicates("soc").set_index("soc")
    info = {"crosswalk_rows": int(len(x)), "soc2010_codes": int(x.c10.nunique()), "soc2018_codes": int(x.c18.nunique()),
            "oews_aggregates_used": {k: v for k, v in pref.items()},
            "soc2018_not_in_oews": sorted(set(x.c18[x.o21.isna()])),
            "soc2010_not_in_2016_file": int(len(set(x.c10) - set(o16.soc))),
            "components_with_2021_codes": int(out.xw_members21.nunique())}
    return out, info


def load_oews_cells(zp: Path, year: int) -> pd.DataFrame:
    """Occupation x harmonized-industry cells from the OEWS national industry files: four-digit NAICS outside retail,
    the retail sector (44-45) from the sector file, and the remapped information industries (IND_REMAP). Each NAICS
    has one ownership row in these files (checked). Combined industries sum employment; wages are employment-weighted
    over the rows that report them."""
    z = zipfile.ZipFile(zp)

    def rd(stem):
        name = [n for n in z.namelist() if n.endswith(f"/{stem}_M{year}_dl.xlsx")][0]
        d = pd.read_excel(io.BytesIO(z.read(name)), dtype=str)
        assert d.groupby("NAICS").OWN_CODE.nunique().max() == 1, f"{stem} {year}: several ownership rows"
        return d[["NAICS", "NAICS_TITLE", "OCC_CODE", "O_GROUP", "TOT_EMP", "A_MEAN", "H_MEAN"]]

    d4, sec = rd("nat4d"), rd("natsector")
    d = pd.concat([d4[~d4.NAICS.str[:2].isin(["44", "45"])], sec[sec.NAICS == "44-45"]], ignore_index=True)
    d = d[d.O_GROUP == "detailed"].copy()
    d["ind"] = d.NAICS.map(lambda c: IND_REMAP.get(c, c))
    d["emp"] = num(d.TOT_EMP)
    am, hm = num(d.A_MEAN), num(d.H_MEAN)
    d["am"] = am.fillna(hm * 2080.0)
    d["hm"] = hm.fillna(am / 2080.0)
    d = d[d.emp > 0]
    d["emp_w"] = np.where(d.am.notna(), d.emp, 0.0)
    d["wb"] = (d.emp * d.am).fillna(0.0)
    d["hb"] = (d.emp * d.hm).fillna(0.0)
    g = d.groupby(["ind", "OCC_CODE"], sort=True).agg(emp=("emp", "sum"), emp_w=("emp_w", "sum"), wb=("wb", "sum"),
                                                      hb=("hb", "sum"), n_naics=("NAICS", "nunique"))
    g["a_mean"] = np.where(g.emp_w > 0, g.wb / g.emp_w.where(g.emp_w > 0), np.nan)
    g["h_mean"] = np.where(g.emp_w > 0, g.hb / g.emp_w.where(g.emp_w > 0), np.nan)
    titles = d.groupby("ind").NAICS_TITLE.first()
    g = g.reset_index().rename(columns={"OCC_CODE": "soc"})
    g["ind_title"] = g.ind.map(titles)
    return g[["ind", "ind_title", "soc", "emp", "a_mean", "h_mean", "n_naics"]]


def job_zones() -> pd.Series:
    jz = pd.read_csv(F_JZ)
    xw = pd.read_csv(TASKS / "xw_oews_onetsoc.csv")
    m = xw.merge(jz, left_on="onet_soc", right_on="onetsoc_code", how="left")
    return m.groupby("soc").job_zone.mean()


def bls_projections(titles: pd.Series) -> pd.Series:
    p = pd.read_csv(F_PROJ)
    key = p.occupation.astype(str).str.lower().str.strip()
    p = p.assign(key=key).drop_duplicates("key")
    mp = dict(zip(p.key, pd.to_numeric(p.pct_emp_change_2020_2030, errors="coerce")))
    return titles.astype(str).str.lower().str.strip().map(mp)


# =============================================================================================================
# 3. Activity rows: (occupation, DWA) with the model's attributes
# =============================================================================================================

def activity_rows(par: dict) -> pd.DataFrame:
    oa = pd.read_csv(TASKS / "occ_activity.csv")
    act = pd.read_csv(TASKS / "activities.csv")
    attr = pd.read_csv(ENGINE / "priors" / "activity_attributes.csv").set_index("gwa_id")
    # occupation-specific exposure of a DWA: mean Eloundou beta over the occupation's tasks linked to the DWA
    lab = pd.read_csv(F_LABELS, sep="\t")
    lab = lab.rename(columns={"Task ID": "task_id"})[["task_id", "beta", "human_labels"]]
    lab["beta_h"] = lab.human_labels.map({"E0": 0.0, "E1": 1.0, "E2": 0.5})
    lab["task_id"] = lab.task_id.astype(int)
    xw = pd.read_csv(TASKS / "xw_task_dwa.csv")[["soc", "task_id", "dwa_id"]]
    xw = xw.merge(lab[["task_id", "beta", "beta_h"]], on="task_id", how="left")
    beta_od = xw.groupby(["soc", "dwa_id"])[["beta", "beta_h"]].mean().rename(
        columns={"beta": "beta_od", "beta_h": "beta_h_od"})
    r = oa.merge(act[["dwa_id", "gwa_id", "exposure_llm", "exposure_llm_human", "physical", "hours_identity_median",
                      "est_task_hours", "regulated_class", "licensed_time_share"]], on="dwa_id", how="left")
    r = r.merge(beta_od, left_on=["soc", "dwa_id"], right_index=True, how="left")
    r["beta"] = r.beta_od.fillna(r.exposure_llm)
    r["beta_h"] = r.beta_h_od.fillna(r.exposure_llm_human)
    r["beta_occ_specific"] = r.beta_od.notna()
    r = r[r.beta.notna() & r.hours_identity_median.notna()].copy()
    r["s"] = r.time_share / r.groupby("soc").time_share.transform("sum")
    ga = r.gwa_id.map(lambda g: g if g in attr.index else None)
    r["qbar"] = ga.map(attr.r_bar).fillna(0.95).astype(float)
    r["Lm"] = ga.map(attr.L_mult).fillna(2.0).astype(float)
    r["sep"] = ga.map(attr.separable).fillna(0.5).astype(float) >= par["separable_threshold"]
    reg = r.regulated_class.fillna("none").astype(str)
    lic = (reg == "licensed") | (r.licensed_time_share.fillna(0) >= par["licensed_share_threshold"])
    r["qbar"] = np.where(lic, np.maximum(r.qbar, par["r_bar_licensed"]), r.qbar)
    r["Lm"] = np.where(reg != "none", np.maximum(r.Lm, par["L_mult_regulated"]), r.Lm)
    r["ximin"] = np.where(reg == "high_risk_eu", par["xi_min"]["high_risk_eu"],
                          np.where(lic, par["xi_min"]["licensed"], par["xi_min"]["none"]))
    r["permA"] = ~(lic & par["licensed_blocks_A"])
    cm = par["class_mult"]
    keys = sorted(cm, key=len, reverse=True)
    r["cm"] = r.gwa_id.map(lambda g: next((cm[k] for k in keys if str(g).startswith(k)), 1.0)).astype(float)
    r["phys"] = r.physical.fillna(0).astype(float) >= 0.5
    return r.reset_index(drop=True)


# =============================================================================================================
# 4. The model at 2021 parameters
# =============================================================================================================

def horizon(t, sc):
    """50% horizon in hours on the scenario's path."""
    return sc["H0"] * np.power(2.0, (t - sc["t0"]) / sc["Td"])


def model_scores(r: pd.DataFrame, wage_h: pd.Series, par: dict, sc: dict) -> tuple[pd.DataFrame, dict]:
    """Per (occupation, DWA) row and date on the grid: is mode A optimal? Unit costs are per unit of in-house cost
    w t (so the review and error terms are wage-free; the wage enters through inference cost / wage), following
    eq. tasks-cost, prop:tasks-review (stakes-targeted review share) and ass:ext-capability (capability test with
    the 80% horizon, logistic error, physical lag). Fixed build costs are omitted at national scale."""
    grid = np.arange(par["t_freeze"], par["t_may25"] + 1e-9, par["grid_step"])
    if sc.get("grid") == "static":
        grid = np.array([par["t_freeze"]])
    t = grid[None, :]
    d = (r[sc.get("hours_col", "hours_identity_median")].values * 1.0)[:, None]
    beta = r.beta.values if sc.get("beta_col", "beta") == "beta" else r[sc["beta_col"]].values
    phys = r.phys.values[:, None]
    w = (r.soc.map(wage_h).values * (1.0 + par["tau_L_hour"]))[:, None]
    H = horizon(t, sc)
    Hp = horizon(t - par["L_W"], sc)
    Heff = np.where(phys, Hp, H)
    dA = d * par["chi_A"]
    capA = Heff >= dA
    TF = sc["t0"] + sc["Td"] * np.log2(dA / sc["H0"]) + par["L_W"] * phys      # capability date of A
    ecap = expit(par["b"] * np.log2(d / Heff))
    iota = sc.get("iota", par["iota"])
    e_ctx = par["e1"] + (par["e0"] - par["e1"]) * (1.0 - iota)
    e = 1.0 - (1.0 - e_ctx) * (1.0 - ecap)
    rho_rev = sc.get("rho_rev", par["rho_rev"])
    wtR = rho_rev * par["wage_premium"]
    qbar = r.qbar.values[:, None]
    Lm = r.Lm.values[:, None]
    ximin = r.ximin.values[:, None]
    xiE = np.exp(-wtR / (e * Lm))
    xiR = 1.0 - (1.0 - qbar) / e
    xi = np.clip(np.maximum(np.maximum(xiE, xiR), ximin), 0.0, 1.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        term = np.where(xi > 0, xi * (1.0 + np.log(1.0 / np.maximum(xi, 1e-300))), 0.0)
    cQ = wtR * xi + e * Lm * (1.0 - term)
    pmult = sc.get("price_mult", 1.0)
    pi_h = par["pi_h"] * pmult
    cm = r.cm.values[:, None]
    piA = np.maximum(pi_h * np.exp(-par["delta_pi"] * np.maximum(t - TF, 0.0)), par["floor_share"] * pi_h) * cm
    retry = 1.0 / (1.0 - np.minimum(ecap, par["retry_cap"]))
    cA = piA * retry / w + cQ
    relA = e * (1.0 - xi) <= (1.0 - qbar) + 1e-12
    capU = (~phys) & (beta[:, None] > 0.05) & (H >= d * par["chi_U"])
    betaU = par["beta_U"] * beta[:, None] / par["exposure_ref"]
    piU = np.maximum(pi_h * np.exp(-par["delta_pi"] * np.maximum(t - par["t_freeze"], 0.0)),
                     par["floor_share"] * pi_h) * cm * par["u_tok"]
    cU = 1.0 / (1.0 + betaU) + piU / w
    sep = r.sep.values[:, None] & (not sc.get("no_outsourcing", False))
    cO = np.where(sep, par["rho_O"] * (1.0 - par["delta_O"]) ** (t - par["t_freeze"]) + par["kappa_O"] + par["zeta_O"],
                  np.inf)
    altA = np.minimum(np.minimum(1.0, cO), np.where(capU, cU, np.inf))
    permA = r.permA.values[:, None]
    Aopt = capA & permA & relA & (cA <= altA)
    Uopt = capU & ~Aopt & (cU <= np.minimum(1.0, cO))
    save = np.where(Aopt, 1.0 - xi * rho_rev, 0.0) + np.where(Uopt, 1.0 - 1.0 / (1.0 + betaU), 0.0)
    rows = pd.DataFrame({
        "soc": r.soc.values, "dwa_id": r.dwa_id.values, "s": r.s.values, "beta": beta,
        "A_avg": Aopt.mean(1), "A_end": Aopt[:, -1], "A_start": Aopt[:, 0],
        "AU_avg": (Aopt | Uopt).mean(1), "save_avg": save.mean(1),
        "F_avg": (capA & permA).mean(1),
        "NP": ((~phys[:, 0]) & permA[:, 0]).astype(float),
        "first_A": np.where(Aopt.any(1), grid[np.argmax(Aopt, axis=1)], np.nan),
    })
    sw = rows.s * rows.beta
    agg = pd.DataFrame({
        "E": (sw).groupby(rows.soc).sum(),
        "M": (sw * rows.A_avg).groupby(rows.soc).sum(),
        "M_end": (sw * rows.A_end).groupby(rows.soc).sum(),
        "M_static": (sw * rows.A_start).groupby(rows.soc).sum(),
        "M_AU": (sw * rows.AU_avg).groupby(rows.soc).sum(),
        "M_save": (sw * rows.save_avg).groupby(rows.soc).sum(),
        "M_feas": (sw * rows.F_avg).groupby(rows.soc).sum(),
        "E_np": (sw * rows.NP).groupby(rows.soc).sum(),
    })
    info = {
        "H_end2021_hours": float(horizon(np.array([par["t_freeze"]]), sc)[0]),
        "H_may2025_hours": float(horizon(np.array([par["t_may25"]]), sc)[0]),
        "grid_points": int(len(grid)),
        "share_rows_capA_end2021": float(np.average(capA[:, 0], weights=r.s.values)),
        "share_rows_Aopt_end2021": float(np.average(Aopt[:, 0], weights=r.s.values)),
        "share_rows_capA_may2025": float(np.average(capA[:, -1], weights=r.s.values)),
        "share_rows_Aopt_may2025": float(np.average(Aopt[:, -1], weights=r.s.values)),
        "share_rows_Uopt_may2025": float(np.average(Uopt[:, -1], weights=r.s.values)),
        "share_capA_may2025_but_not_Aopt": float(np.average((capA[:, -1] & ~Aopt[:, -1]), weights=r.s.values)),
    }
    # where A is capability-feasible and permitted in May 2025: review share and the winning mode, weighted by
    # exposed time (s x beta)
    fe = capA[:, -1] & permA[:, -1]
    wts = (r.s.values * beta)[fe]
    if wts.sum() > 0:
        wO = (~Aopt[:, -1] & ~Uopt[:, -1] & (cO[:, -1] < 1.0))[fe]
        info["may2025_feasible_permitted"] = {
            "exposed_time_share_of_all_exposed": float(wts.sum() / (r.s.values * beta).sum()),
            "mean_review_share": float(np.average(xi[fe, -1], weights=wts)),
            "share_A": float(np.average(Aopt[fe, -1], weights=wts)),
            "share_U": float(np.average(Uopt[fe, -1], weights=wts)),
            "share_O": float(np.average(wO, weights=wts)),
            "share_U_if_beta_ge_05": float(np.average(Uopt[fe, -1][beta[fe] >= 0.5], weights=wts[beta[fe] >= 0.5])),
            "share_U_if_beta_lt_05": float(np.average(Uopt[fe, -1][beta[fe] < 0.5], weights=wts[beta[fe] < 0.5])),
        }
    return agg, info


def model_thresholds(r: pd.DataFrame, par: dict, sc: dict) -> dict:
    """The decision of model_scores written as a wage threshold. For each (activity row, date), automation is optimal
    if and only if base is true and the loaded wage is at least W: every other term of the unit costs is a share of
    w t, so the wage enters only through inference cost / w. Used to score occupation x industry cells at their own
    May 2021 wages; checked against model_scores at national wages."""
    grid = np.arange(par["t_freeze"], par["t_may25"] + 1e-9, par["grid_step"])
    t = grid[None, :]
    d = (r[sc.get("hours_col", "hours_identity_median")].values * 1.0)[:, None]
    beta = r.beta.values
    phys = r.phys.values[:, None]
    H = horizon(t, sc)
    Heff = np.where(phys, horizon(t - par["L_W"], sc), H)
    dA = d * par["chi_A"]
    capA = Heff >= dA
    TF = sc["t0"] + sc["Td"] * np.log2(dA / sc["H0"]) + par["L_W"] * phys
    ecap = expit(par["b"] * np.log2(d / Heff))
    iota = sc.get("iota", par["iota"])
    e = 1.0 - (1.0 - (par["e1"] + (par["e0"] - par["e1"]) * (1.0 - iota))) * (1.0 - ecap)
    wtR = sc.get("rho_rev", par["rho_rev"]) * par["wage_premium"]
    qbar, Lm, ximin = r.qbar.values[:, None], r.Lm.values[:, None], r.ximin.values[:, None]
    xi = np.clip(np.maximum(np.maximum(np.exp(-wtR / (e * Lm)), 1.0 - (1.0 - qbar) / e), ximin), 0.0, 1.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        term = np.where(xi > 0, xi * (1.0 + np.log(1.0 / np.maximum(xi, 1e-300))), 0.0)
    cQ = wtR * xi + e * Lm * (1.0 - term)
    pi_h = par["pi_h"] * sc.get("price_mult", 1.0)
    cm = r.cm.values[:, None]
    piA = np.maximum(pi_h * np.exp(-par["delta_pi"] * np.maximum(t - TF, 0.0)), par["floor_share"] * pi_h) * cm
    num_ = piA / (1.0 - np.minimum(ecap, par["retry_cap"]))              # inference $ per human-hour, with retries
    relA = e * (1.0 - xi) <= (1.0 - qbar) + 1e-12
    capU = (~phys) & (beta[:, None] > 0.05) & (H >= d * par["chi_U"])
    betaU = par["beta_U"] * beta[:, None] / par["exposure_ref"]
    piU = np.maximum(pi_h * np.exp(-par["delta_pi"] * np.maximum(t - par["t_freeze"], 0.0)),
                     par["floor_share"] * pi_h) * cm * par["u_tok"]
    sep = r.sep.values[:, None] & (not sc.get("no_outsourcing", False))
    cO = par["rho_O"] * (1.0 - par["delta_O"]) ** (t - par["t_freeze"]) + par["kappa_O"] + par["zeta_O"]
    with np.errstate(divide="ignore", invalid="ignore"):
        thrH = np.where(cQ < 1.0, num_ / (1.0 - cQ), np.inf)
        thrO = np.where(sep, np.where(cQ < cO, num_ / (cO - cQ), np.inf), 0.0)
        k = 1.0 / (1.0 + betaU) - cQ
        nU = num_ - piU
        thrU = np.where(capU, np.where(nU > 0, np.where(k > 0, nU / k, np.inf), np.where(k >= 0, 0.0, np.inf)), 0.0)
    base = capA & r.permA.values[:, None] & relA
    return {"base": base, "W": np.maximum(np.maximum(thrH, thrO), thrU), "grid": grid,
            "n_upper_bound_cases": int((capU & base & (nU <= 0) & (k < 0)).sum())}


def cell_scores(r: pd.DataFrame, thr: dict, socs: np.ndarray, wages_h: np.ndarray, tau: float) -> np.ndarray:
    """Model automatable share for each cell (occupation soc, hourly wage), exposure-weighted over the occupation's
    activities and averaged over the window, as in model_scores."""
    sw = (r.s * r.beta).values
    rows_by_soc = r.groupby("soc").indices
    out = np.full(len(socs), np.nan)
    cells_by_soc = pd.Series(np.arange(len(socs))).groupby(np.asarray(socs)).indices
    for soc in sorted(cells_by_soc):
        ri = rows_by_soc.get(soc)
        if ri is None:
            continue
        ci = cells_by_soc[soc]
        w = np.asarray(wages_h, float)[ci] * (1.0 + tau)
        A = thr["base"][ri][None, :, :] & (w[:, None, None] >= thr["W"][ri][None, :, :])
        out[ci] = (A.mean(2) * sw[ri][None, :]).sum(1)
    return out


def scenario(par: dict, name: str) -> dict:
    base = {"H0": par["H0"], "t0": par["t0"], "Td": par["Td_days"] / 365.25}
    if name == "td207":
        base["Td"] = par["Td_days_slow"] / 365.25
    if name == "th10":
        # ln p50 (minutes) = a + slope * days since 2019-01-01
        base = {"H0": math.exp(par["th10_ln_p50_min_2019"]) / 60.0, "t0": 2019.0,
                "Td": math.log(2.0) / par["th10_slope_per_day"] / 365.25}
    if name == "aei_hours":
        base["hours_col"] = "est_task_hours"
    if name == "price10":
        base["price_mult"] = 10.0
    if name == "no_outsourcing":
        base["no_outsourcing"] = True
    if name == "iota02":
        base["iota"] = 0.2
    if name == "iota08":
        base["iota"] = 0.8
    if name == "human_beta":
        base["beta_col"] = "beta_h"
    if name == "static":
        base["grid"] = "static"
    if name.startswith("rho") and name[3:].isdigit():
        base["rho_rev"] = {"rho037": 0.37, "rho08": 0.8, "rho119": 1.19}[name]
    return base


# =============================================================================================================
# 5. Regressions
# =============================================================================================================

def zs(x: pd.Series) -> pd.Series:
    return (x - x.mean()) / x.std(ddof=0)


def _as_list(v) -> list:
    return [] if v is None else ([v] if isinstance(v, str) else list(v))


def design(d: pd.DataFrame, xs: list, controls: list, fe):
    X = d[xs + controls].astype(float).copy()
    for c in xs:
        X[c] = zs(X[c])
    for f in _as_list(fe):
        X = pd.concat([X, pd.get_dummies(d[f].astype(str), prefix="fe_" + f, drop_first=True, dtype=float)], axis=1)
    X = sm.add_constant(X, has_constant="add")
    return X


def _sort_cols(df: pd.DataFrame) -> list:
    cols = [c for c in ["soc", "ind"] if c in df.columns]
    return cols or [df.columns[0]]


def ols(df: pd.DataFrame, y: str, xs: list, controls: list, fe="major", weight: str | None = None,
        cluster=None) -> dict:
    """OLS (WLS with `weight`); fe: one or several fixed-effect columns; cluster: one column (one-way) or two
    columns (two-way, Cameron-Gelbach-Miller as implemented in statsmodels); HC1 otherwise."""
    need = [y] + xs + controls + ([weight] if weight else []) + _as_list(fe) + _as_list(cluster)
    d = df.dropna(subset=need).sort_values(_sort_cols(df), kind="mergesort").copy()
    X = design(d, xs, controls, fe)
    Y = d[y].astype(float)
    if weight:
        mod = sm.WLS(Y, X, weights=d[weight].astype(float))
    else:
        mod = sm.OLS(Y, X)
    cl = _as_list(cluster)
    if len(cl) == 1:
        fit = mod.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d[cl[0]])[0]})
    elif len(cl) == 2:
        g = np.column_stack([pd.factorize(d[cl[0]])[0], pd.factorize(d[cl[1]])[0]])
        fit = mod.fit(cov_type="cluster", cov_kwds={"groups": g})
    else:
        fit = mod.fit(cov_type="HC1")
    out = {"n": int(len(d)), "r2": float(fit.rsquared), "coef": {}, "y_mean": float(Y.mean()), "y_sd": float(Y.std())}
    for c in xs:
        out["coef"][c] = {"b": float(fit.params[c]), "se": float(fit.bse[c]), "t": float(fit.tvalues[c]),
                          "p": float(fit.pvalues[c]), "sd_x": float(d[c].std(ddof=0)),
                          "b_per_unit": float(fit.params[c] / d[c].std(ddof=0))}
    return out


def cv_r2_grouped(df: pd.DataFrame, y: str, sets: dict, controls: list, fe, group: str, reps: int) -> dict:
    """Repeated K-fold out-of-sample R^2 with folds formed by `group` (all cells of an occupation in one fold)."""
    allx = sorted({c for v in sets.values() for c in v})
    d = df.dropna(subset=[y] + allx + controls + _as_list(fe) + [group]).sort_values(
        _sort_cols(df), kind="mergesort").reset_index(drop=True)
    Y = d[y].values.astype(float)
    mats = {k: design(d, v, controls, fe).values for k, v in sets.items()}
    gid = pd.factorize(d[group])[0]
    G = int(gid.max()) + 1
    res = {k: [] for k in sets}
    for rep in range(reps):
        rng = np.random.default_rng(SEED0 + rep)
        folds = (rng.permutation(G) % K_FOLDS)[gid]
        for k, X in mats.items():
            sse = 0.0
            for f in range(K_FOLDS):
                tr, te = folds != f, folds == f
                beta, *_ = np.linalg.lstsq(X[tr], Y[tr], rcond=None)
                sse += float(((Y[te] - X[te] @ beta) ** 2).sum())
            res[k].append(1.0 - sse / float(((Y - Y.mean()) ** 2).sum()))
    out = {k: {"mean": float(np.mean(v)), "sd": float(np.std(v))} for k, v in res.items()}
    out["reps_detail"] = {k: list(map(float, v)) for k, v in res.items()}
    out.update({"n": int(len(d)), "groups": G, "reps": reps, "folds": K_FOLDS, "sets": sets})
    return out


def cv_r2(df: pd.DataFrame, y: str, sets: dict, controls: list, fe: str = "major") -> dict:
    """Repeated K-fold out-of-sample R^2 for nested regressor sets on a common sample (deterministic seeds)."""
    allx = sorted({c for v in sets.values() for c in v})
    d = df.dropna(subset=[y] + allx + controls + [fe]).sort_values("soc").reset_index(drop=True)
    Y = d[y].values.astype(float)
    mats = {k: design(d, v, controls, fe).values for k, v in sets.items()}
    n = len(d)
    res = {k: [] for k in sets}
    for rep in range(N_CV_REPS):
        rng = np.random.default_rng(SEED0 + rep)
        folds = rng.permutation(n) % K_FOLDS
        for k, X in mats.items():
            sse = 0.0
            for f in range(K_FOLDS):
                tr, te = folds != f, folds == f
                beta, *_ = np.linalg.lstsq(X[tr], Y[tr], rcond=None)
                sse += float(((Y[te] - X[te] @ beta) ** 2).sum())
            res[k].append(1.0 - sse / float(((Y - Y.mean()) ** 2).sum()))
    out = {k: {"mean": float(np.mean(v)), "sd": float(np.std(v))} for k, v in res.items()}
    out.update({k + "_reps": list(map(float, v)) for k, v in res.items()})
    if "exposure" in res and "both" in res:
        out["share_reps_both_beats_exposure"] = float(np.mean(np.array(res["both"]) > np.array(res["exposure"])))
    if "exposure" in res and "model" in res:
        out["share_reps_model_beats_exposure"] = float(np.mean(np.array(res["model"]) > np.array(res["exposure"])))
    out["n"] = int(n)
    out["reps"] = N_CV_REPS
    out["folds"] = K_FOLDS
    out["sets"] = {k: v for k, v in sets.items()}
    return out


def ols_within(df: pd.DataFrame, y: str, xs: list, controls: list, fe2: list, cluster=None, weight=None,
               tol: float = 1e-11, maxit: int = 5000) -> dict:
    """OLS with two sets of fixed effects absorbed by alternating (weighted) demeaning, then OLS on the demeaned
    data without a constant (Frisch-Waugh-Lovell). Scores in xs are standardized before demeaning, so coefficients
    are per 1 sd of the score across cells. Fixed effects nested within the clusters are not counted in the
    small-sample correction, as is standard."""
    need = [y] + xs + controls + list(fe2) + _as_list(cluster) + ([weight] if weight else [])
    d = df.dropna(subset=need).sort_values(_sort_cols(df), kind="mergesort").copy()
    Z = d[[y] + xs + controls].astype(float).copy()
    sds = {c: float(Z[c].std(ddof=0)) for c in xs}
    for c in xs:
        Z[c] = zs(Z[c])
    w = d[weight].values.astype(float) if weight else np.ones(len(d))
    gs = [pd.factorize(d[f])[0] for f in fe2]
    A = Z.values.copy()
    it = 0
    for it in range(maxit):
        prev = A.copy()
        for g in gs:
            sums = np.zeros((int(g.max()) + 1, A.shape[1]))
            np.add.at(sums, g, A * w[:, None])
            A = A - (sums / np.bincount(g, weights=w)[:, None])[g]
        if np.max(np.abs(A - prev)) < tol:
            break
    X = pd.DataFrame(A[:, 1:], columns=xs + controls, index=d.index)
    Y = pd.Series(A[:, 0], index=d.index)
    mod = sm.WLS(Y, X, weights=w) if weight else sm.OLS(Y, X)
    cl = _as_list(cluster)
    if len(cl) == 2:
        fit = mod.fit(cov_type="cluster", cov_kwds={"groups": np.column_stack([pd.factorize(d[c])[0] for c in cl])})
    elif len(cl) == 1:
        fit = mod.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d[cl[0]])[0]})
    else:
        fit = mod.fit(cov_type="HC1")
    out = {"n": int(len(d)), "r2_within": float(fit.rsquared), "iterations": int(it + 1), "coef": {}}
    for c in xs:
        out["coef"][c] = {"b": float(fit.params[c]), "se": float(fit.bse[c]), "t": float(fit.tvalues[c]),
                          "p": float(fit.pvalues[c]), "sd_x": sds[c], "b_per_unit": float(fit.params[c] / sds[c])}
    return out


def drop_reps(d: dict) -> dict:
    return {k: v for k, v in d.items() if not k.endswith("_reps")}


# =============================================================================================================
# 6. Firm level
# =============================================================================================================

SIC_NAICS = {7372: "5132", 7371: "5415", 7373: "5415", 7374: "5182"}
BUCKETS = ["cogs", "sm", "ga", "rd"]
BUCKET_NAME = {"cogs": "cogs", "sm": "sm", "ga": "ga", "rd": "rnd"}


def function_scores(occ: pd.DataFrame, col: str) -> dict:
    """Score of each function: wage-bill-weighted mean of occupation scores (national and by NAICS)."""
    fo = pd.read_csv(TASKS / "function_occ.csv")
    fi = pd.read_csv(TASKS / "function_occ_by_industry.csv", dtype={"naics": str})
    sc = occ.set_index("soc")[col]
    wg = occ.set_index("soc")["a_mean21"]
    out = {}

    def agg(t):
        t = t.assign(x=t.soc.map(sc), w=t.soc.map(wg)).dropna(subset=["x", "w"])
        ww = t.weight * t.w
        return float((ww * t.x).sum() / ww.sum()) if ww.sum() > 0 else np.nan

    out["national"] = {f: agg(g) for f, g in fo.groupby("function_id")}
    for n in sorted(set(SIC_NAICS.values())):
        out[n] = {f: agg(g) for f, g in fi[fi.naics == n].groupby("function_id")}
    return out


def bucket_scores(fs: dict) -> dict:
    """Bucket score = within-bucket-split-weighted mean of function scores. The splits in
    industry_function_shares.csv are assumed and identical across SIC 7370-7374 (checked), so the pooled row is used."""
    ifs = pd.read_csv(TASKS / "industry_function_shares.csv", dtype={"sic": str})
    s = ifs[(ifs.sic == "7370-7374") & (ifs.size_band == "all")]
    out = {}
    for key, fmap in fs.items():
        o = {}
        for b in ["cogs", "sm", "ga", "rnd"]:
            t = s[s.cost_bucket == b].copy()
            t["x"] = t.function_id.map(fmap)
            t = t.dropna(subset=["x"])
            o[b] = float((t.within_bucket_split * t.x).sum() / t.within_bucket_split.sum())
        out[key] = o
    return out


def firm_window(p: pd.DataFrame, years: list) -> pd.DataFrame:
    x = p[p.year.isin(years) & (p.rev > 0)].copy()
    x["cogs"] = x.rev - x.gp
    for b in BUCKETS:
        x["s_" + b] = x[b] / x.rev
        x.loc[(x["s_" + b] < 0) | (x["s_" + b] > 2), "s_" + b] = np.nan
    g = x.groupby("cik").agg(rev=("rev", "mean"), sic=("sic", "first"), acq=("acq_flag", "max"),
                             **{"s_" + b: ("s_" + b, "mean") for b in BUCKETS})
    return g


def firm_level(occ: pd.DataFrame) -> dict:
    p = pd.read_csv(F_PANEL)
    p = p[p.sic.between(7370, 7374) & ~p.cik.map(is_excluded)]     # registrants excluded at the author's request
    res = {"buckets": {}, "regressions": {}, "placebo": {}, "notes": []}
    bs = {}
    for col in ["M", "E"]:
        fs = function_scores(occ, col)
        bs[col] = bucket_scores(fs)
        res["buckets"][col] = {"functions_national": fs["national"], "buckets": bs[col]}

    def A_of(sic, col, b):
        key = SIC_NAICS.get(int(sic), "national")
        return bs[col].get(key, bs[col]["national"])[BUCKET_NAME[b]]

    def build(pre_years, post_years):
        pre, post = firm_window(p, pre_years), firm_window(p, post_years)
        f = pre.join(post, lsuffix="_pre", rsuffix="_post", how="inner")
        f = f.dropna(subset=[f"s_{b}_{w}" for b in BUCKETS for w in ("pre", "post")])
        f = f[f.rev_pre >= 10e6].copy()
        f["sic"] = f.sic_pre.astype(int)
        f["total_pre"] = sum(f[f"s_{b}_pre"] for b in BUCKETS)
        f["total_post"] = sum(f[f"s_{b}_post"] for b in BUCKETS)
        for b in BUCKETS + ["total"]:
            dlt = 100.0 * (f[f"{b}_post" if b == "total" else f"s_{b}_post"] - f[f"{b}_pre" if b == "total" else f"s_{b}_pre"])
            lo, hi = np.nanpercentile(dlt, [2.5, 97.5])
            f["d_" + b] = dlt.clip(lo, hi)
            f["d_" + b + "_raw"] = dlt
        f["growth"] = np.log(f.rev_post / f.rev_pre)
        f["size"] = np.log(f.rev_pre)
        for col in ["M", "E"]:
            num_ = sum(f[f"s_{b}_pre"] * f.sic.map(lambda s, b=b: A_of(s, col, b)) for b in BUCKETS)
            f["mix_" + col] = num_ / f.total_pre
        f["soc"] = f.index.astype(str)  # sort key for ols()
        f["acq_any"] = (f.acq_pre.fillna(0) + f.acq_post.fillna(0)) > 0
        return f.reset_index()

    main = build([2021, 2022], [2024, 2025])
    plac = build([2016, 2017], [2019, 2020])
    res["sample"] = {"main_n": int(len(main)), "placebo_n": int(len(plac)),
                     "main_windows": "FY2021-22 mean to FY2024-25 mean", "placebo_windows": "FY2016-17 mean to FY2019-20 mean",
                     "filters": "SIC 7370-7374; revenue >= $10M in the pre window; COGS (revenue - gross profit), S&M, "
                                "G&A and R&D each reported and between 0 and 2 of revenue in both windows; changes in "
                                "percentage points of revenue winsorized at 2.5/97.5 percentiles",
                     "mix_M_mean": float(main.mix_M.mean()), "mix_M_sd": float(main.mix_M.std()),
                     "mix_E_mean": float(main.mix_E.mean()), "mix_E_sd": float(main.mix_E.std()),
                     "corr_mix_M_E": float(main[["mix_M", "mix_E"]].corr().iloc[0, 1]),
                     "mean_change_pp": {b: float(main["d_" + b].mean()) for b in BUCKETS + ["total"]},
                     "median_change_pp": {b: float(main["d_" + b + "_raw"].median()) for b in BUCKETS + ["total"]},
                     "mean_pre_share": {b: float(main[f"s_{b}_pre"].mean()) for b in BUCKETS}}
    ctrl = ["growth", "size"]
    for b in BUCKETS + ["total"]:
        cb = ctrl + (["total_pre"] if b == "total" else [f"s_{b}_pre", "total_pre"])
        res["regressions"][b] = {
            "model": ols(main, "d_" + b, ["mix_M"], cb, fe="sic"),
            "exposure": ols(main, "d_" + b, ["mix_E"], cb, fe="sic"),
            "both": ols(main, "d_" + b, ["mix_M", "mix_E"], cb, fe="sic"),
        }
        res["placebo"][b] = {"model": ols(plac, "d_" + b, ["mix_M"], cb, fe="sic")}
    res["regressions"]["total_no_acquirers"] = {
        "model": ols(main[~main.acq_any], "d_total", ["mix_M"], ctrl + ["total_pre"], fe="sic")}
    res["regressions"]["total_raw_unwinsorized"] = {
        "model": ols(main.assign(d_total=main.d_total_raw), "d_total", ["mix_M"], ctrl + ["total_pre"], fe="sic")}
    res["notes"].append("mix_M is the cost-weighted mean over the firm's four cost buckets of the model's bucket "
                        "automatable share; bucket shares are wage-bill-weighted function scores, with function to "
                        "occupation weights from function_occ_by_industry.csv for SIC 7371-7374 and function_occ.csv "
                        "for SIC 7370, and the within-bucket function splits of industry_function_shares.csv (assumed).")
    return res


# =============================================================================================================
# 7. LaTeX tables
# =============================================================================================================

def f3(x, nd=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return ""
    if abs(x) < 0.5 * 10 ** (-nd):
        x = 0.0
    return f"{x:.{nd}f}".replace("-", "$-$")


def cell(reg, key, nd=3):
    c = reg["coef"].get(key)
    return (f3(c["b"], nd), f"({f3(c['se'], nd)})") if c else ("", "")


def table_occ(R: dict) -> str:
    panels = [("dlemp", "A. Change in log employment, May 2021 to May 2025"),
              ("dlwbs", "B. Change in log wage-bill share"),
              ("dlwage", "C. Change in log mean wage")]
    cols = ["exposure", "model", "both", "both_w"]
    L = [r"\begin{table}[tbp]", r"\centering",
         r"\caption{Backtest at the occupation level: OEWS May 2021 to May 2025}\label{tab:backtest-occ}",
         r"\small", r"\begin{tabular}{@{}lcccc@{}}", r"\toprule",
         r" & (1) & (2) & (3) & (4)\\",
         r" & Exposure & Model & Both & Both, weighted\\", r"\midrule"]
    for y, title in panels:
        L.append(r"\multicolumn{5}{@{}l}{\emph{" + title + r"}}\\")
        for key, lab in [("E", "Exposure (1 sd)"), ("M", "Model automatable share (1 sd)")]:
            bs, ses = zip(*[cell(R["occ"]["main"][y][c], key) for c in cols])
            L.append(lab + " & " + " & ".join(bs) + r"\\")
            L.append(" & " + " & ".join(ses) + r"\\")
        r2 = [f3(R["occ"]["main"][y][c]["r2"], 3) for c in cols]
        L.append("$R^2$ & " + " & ".join(r2) + r"\\")
        cv = R["occ"]["cv"][y]
        L.append(r"Out-of-sample $R^2$ & " + " & ".join([f3(cv["exposure"]["mean"]), f3(cv["model"]["mean"]),
                                                          f3(cv["both"]["mean"]), ""]) + r"\\")
        L.append(r"\addlinespace")
    n = R["occ"]["main"]["dlemp"]["both"]["n"]
    L += [r"\bottomrule", r"\end{tabular}", r"\smallskip",
          r"\begin{minipage}{0.97\linewidth}\footnotesize",
          (r"Notes: OLS across " + f"{n}" + r" detailed occupations (SOC 2018 codes identical in both vintages). "
           r"Exposure is the time-weighted share of an occupation's detailed work activities exposed to LLMs (GPT-4 "
           r"$\beta$ labels of \citealp{eloundou2024gpts}). The model share multiplies exposure by the indicator that "
           r"automation is feasible and cheapest, averaged over December 2021 to May 2025 along the capability and "
           r"price paths of Section~\ref{sec:ext-dynamics}, with May 2021 wages. Both are standardized. All columns "
           r"control for 22 SOC major-group effects, the physical task share, log mean wage in 2021 and the O*NET "
           r"job zone. Column (4) weights by May 2021 employment. Heteroskedasticity-robust (HC1) standard errors "
           r"in parentheses. Out-of-sample $R^2$: 10-fold cross-validation repeated 50 times on the same sample, "
           r"unweighted. Source: \texttt{code/validation/backtest.py}."),
          r"\end{minipage}", r"\end{table}"]
    return "\n".join(L) + "\n"


def table_robust(R: dict) -> str:
    rows = R["occ"]["robust_table_rows"]
    L = [r"\begin{table}[tbp]", r"\centering",
         r"\caption{Backtest robustness, confounders and placebos (change in log employment)}\label{tab:backtest-robust}",
         r"\footnotesize", r"\setlength{\tabcolsep}{4pt}", r"\begin{tabular}{@{}lccccc@{}}", r"\toprule",
         r" & Exposure & Automate & Capability- & Capability-feasible & \\",
         r" & & & feasible & with exposure & $N$\\", r"\midrule"]
    def bse(reg, key):
        if reg is None:
            return ""
        b, se = cell(reg, key)
        return f"{b} {se}"
    for row in rows:
        if row.get("header"):
            L.append(r"\multicolumn{6}{@{}l}{\emph{" + row["label"] + r"}}\\")
            continue
        L.append(row["label"] + " & " + " & ".join([bse(row["E"], row["ekey"]), bse(row["M"], row["key"]),
                                                    bse(row["F"], row["fkey"]), bse(row["FJ"], row["fkey"]),
                                                    str(row["M"]["n"])]) + r"\\")
    L += [r"\bottomrule", r"\end{tabular}", r"\smallskip",
          r"\begin{minipage}{0.97\linewidth}\footnotesize",
          (r"Notes: coefficients on standardized scores (columns 1 to 3 from separate regressions; column 4 is the "
           r"capability-feasible score in a regression that also includes exposure), with the controls of "
           r"Table~\ref{tab:backtest-occ} and HC1 standard errors in parentheses unless stated. The automation and "
           r"capability-feasible scores are columns (5) and (3) of Table~\ref{tab:backtest-decomp}. In the variant rows "
           r"a blank cell means the score is unchanged from the baseline. The 2016 rows map OEWS May 2016 (verified "
           r"against BLS's national tables) to SOC 2018 with the official BLS crosswalk, using occupations whose "
           r"crosswalk group contains no other 2021 occupation; the split-code and identity-rule rows are variants. "
           r"The 2019 and 2020 rows use the codes that the hybrid May 2019 and May 2020 files share with SOC 2018. "
           r"Computer occupations: SOC 15 and 11-3021. Credit and real-estate occupations: seven codes listed in "
           r"\texttt{notes/backtest\_notes.md}. COVID-rebound groups: SOC 27, 35 and 39."),
          r"\end{minipage}", r"\end{table}"]
    return "\n".join(L) + "\n"


def table_firm(R: dict) -> str:
    F = R["firm"]
    lab = {"cogs": "COGS", "sm": "S\\&M", "ga": "G\\&A", "rd": "R\\&D", "total": "Total"}
    L = [r"\begin{table}[tbp]", r"\centering",
         r"\caption{Backtest at the firm level: SEC software firms, FY2021--22 to FY2024--25}\label{tab:backtest-firm}",
         r"\small", r"\begin{tabular}{@{}lccccc@{}}", r"\toprule",
         r"Change in cost share of revenue (pp) & " + " & ".join(lab[b] for b in BUCKETS + ["total"]) + r"\\", r"\midrule"]
    for key, title in [("model", "Model mix (1 sd)"), ("exposure", "Exposure mix (1 sd)")]:
        k = "mix_M" if key == "model" else "mix_E"
        bs, ses = zip(*[cell(F["regressions"][b][key], k, 2) for b in BUCKETS + ["total"]])
        L.append(title + " & " + " & ".join(bs) + r"\\")
        L.append(" & " + " & ".join(ses) + r"\\")
    bs, ses = zip(*[cell(F["placebo"][b]["model"], "mix_M", 2) for b in BUCKETS + ["total"]])
    L.append(r"Placebo: model mix, FY2016--17 to 2019--20 & " + " & ".join(bs) + r"\\")
    L.append(" & " + " & ".join(ses) + r"\\")
    L.append(r"\addlinespace")
    L.append(r"Mean change (pp) & " + " & ".join(f3(F["sample"]["mean_change_pp"][b], 2) for b in BUCKETS + ["total"]) + r"\\")
    L.append(r"$N$ (main; placebo) & " + " & ".join(
        f"{F['regressions'][b]['model']['n']}; {F['placebo'][b]['model']['n']}" for b in BUCKETS + ["total"]) + r"\\")
    L += [r"\bottomrule", r"\end{tabular}", r"\smallskip",
          r"\begin{minipage}{0.97\linewidth}\footnotesize",
          (r"Notes: one regression per cell. COGS is revenue minus gross profit. The dependent variable is the change in a cost "
           r"bucket's share of revenue between the mean of fiscal years 2021 and 2022 and the mean of 2024 and 2025, in "
           r"percentage points, winsorized at 2.5 and 97.5 percent. The model mix is the cost-weighted mean of the "
           r"model's automatable share of the firm's four cost buckets; it varies across firms only through the bucket "
           r"mix and the four-digit SIC code. Controls: log revenue growth between the windows, log pre-window revenue, "
           r"the pre-window total cost share and, for bucket columns, that bucket's pre-window share; SIC fixed effects. "
           r"HC1 standard errors in parentheses. Panel: \texttt{data/panel\_v2\_all.csv}, SIC 7370 to 7374."),
          r"\end{minipage}", r"\end{table}"]
    return "\n".join(L) + "\n"


def table_decomp(R: dict) -> str:
    D = R["occ"]["decomposition"]
    keys = ["E", "E_np", "M_feas", "M_AU", "M", "M_rho08"]
    L = [r"\begin{table}[tbp]", r"\centering",
         r"\caption{Where the predictive content lies: the model score layer by layer (change in log employment)}\label{tab:backtest-decomp}",
         r"\footnotesize", r"\setlength{\tabcolsep}{4pt}", r"\begin{tabular}{@{}lcccccc@{}}", r"\toprule",
         r" & (1) & (2) & (3) & (4) & (5) & (6)\\",
         r" & Exposure & Non-physical, & Capability- & Automate & Automate & Automate,\\",
         r" & & permissible & feasible & or augment & & review 0.8\\", r"\midrule"]
    def row(label, fn, nd=3):
        bs, ses = [], []
        for k in keys:
            reg = fn(k)
            if reg is None:
                bs.append(""); ses.append(""); continue
            kk = "E" if label.startswith("Exposure in") else k
            b, se = cell(reg, kk, nd)
            bs.append(b); ses.append(se)
        L.append(label + " & " + " & ".join(bs) + r"\\")
        L.append(" & " + " & ".join(ses) + r"\\")
    row("Score alone (1 sd)", lambda k: D[k]["alone"])
    row("Score, with exposure (1 sd)", lambda k: D[k]["joint"])
    row("Exposure in that regression", lambda k: D[k]["joint"])
    row("Score alone, employment-weighted", lambda k: D[k]["weighted"])
    row("Score alone, 2016--21 trend control", lambda k: D[k]["pretrend_control"])
    row("Placebo: 2016--21 change", lambda k: D[k]["placebo_2016_21"])
    cv = D["cv"]
    L.append(r"\addlinespace")
    L.append(r"Out-of-sample $R^2$, score alone & " + " & ".join(f3(cv[k]["mean"]) for k in keys) + r"\\")
    L.append(r"Out-of-sample $R^2$, with exposure & & " + " & ".join(f3(cv["E+" + k]["mean"]) for k in keys[1:]) + r"\\")
    L.append(r"Share of repetitions improving on exposure & & " + " & ".join(
        f3(cv["share_reps_E+" + k + "_beats_E"], 2) for k in keys[1:]) + r"\\")
    L.append(r"Mean of score & " + " & ".join(f3(R["scores"]["descriptive"][k]["mean"]) for k in keys) + r"\\")
    L.append(r"Correlation with exposure & 1 & " + " & ".join(
        f3(R["scores"]["descriptive"][k]["corr_with_E"], 2) for k in keys[1:]) + r"\\")
    n = D["E"]["alone"]["n"]; npre = D["E"]["placebo_2016_21"]["n"]
    L += [r"\bottomrule", r"\end{tabular}", r"\smallskip",
          r"\begin{minipage}{0.97\linewidth}\footnotesize",
          (r"Notes: each score is the time-weighted sum over an occupation's activities of LLM exposure times an "
           r"indicator, averaged over December 2021 to May 2025: (1) none; (2) the activity is non-physical and not "
           r"reserved for a licensed signatory; (3) in addition, the 80\% horizon covers the activity's length "
           r"(Section~\ref{sec:ext-dynamics}); (4) automation or augmentation is feasible and is the cheapest mode "
           r"(augmentation needs only the 50\% horizon to cover the activity, so (4) is not nested in (3)); (5) "
           r"automation is feasible and is the cheapest mode (the main score of Table~\ref{tab:backtest-occ}); (6) as (5) "
           r"with review taking 0.8 of the doing time, the value the engine assumed before its parameters were sourced "
           r"(the current value is 0.575). Controls, fixed "
           r"effects and standard errors as in Table~\ref{tab:backtest-occ}; $N=" + f"{n}" + r"$, and $N=" + f"{npre}"
           + r"$ in the trend and placebo rows. Columns (1), (3), (4) and (5) were specified before estimation; "
           r"columns (2) and (6) and the layer-by-layer arrangement were added after the first estimates, so the "
           r"comparison across columns is exploratory."),
          r"\end{minipage}", r"\end{table}"]
    return "\n".join(L) + "\n"


def table_sweep(R: dict) -> str:
    SW = R["occ"]["rho_sweep"]
    cur, pre = round(SW["current_value"], 4), round(SW["pre_audit_value"], 4)
    pts = [q for q in SW["path"] if round(q["rho"], 4) in set(SW["table_points"]) | {pre}]
    L = [r"\begin{table}[tbp]", r"\centering",
         r"\caption{The main result across the sourced range of the review-time ratio (change in log employment)}\label{tab:backtest-sweep}",
         r"\footnotesize", r"\setlength{\tabcolsep}{4pt}", r"\begin{tabular}{@{}lccccccc@{}}", r"\toprule",
         r"Review & Automation & \multicolumn{2}{c}{Model share (1 sd)} & Exposure & \multicolumn{3}{c}{Out-of-sample $R^2$}\\",
         r"\cmidrule(lr){3-4}\cmidrule(lr){6-8}",
         r"ratio & cheapest (\%) & alone & with exposure & with model & Exposure & Model & Both\\", r"\midrule"]
    for q in pts:
        mark = "$^{a}$" if round(q["rho"], 4) == cur else ("$^{b}$" if round(q["rho"], 4) == pre else "")
        if "b_alone" not in q:
            L.append(f"{q['rho']:.3f}{mark} & {100 * q['share_A']:.0f} & \\multicolumn{{6}}{{c}}{{score has no variation}}\\\\")
            continue
        L.append(f"{q['rho']:.3f}{mark} & {100 * q['share_A']:.0f} & {f3(q['b_alone'])} ({f3(q['se_alone'])}) & "
                 f"{f3(q['b_joint'])} ({f3(q['se_joint'])}) & {f3(q['bE_joint'])} ({f3(q['seE_joint'])}) & "
                 f"{f3(q['cv_E'])} & {f3(q['cv_M'])} & {f3(q['cv_EM'])}\\\\")
    th = SW["thresholds"]
    fmt = lambda d: f"{d['rho']:.2f}" if d["rho"] is not None else d["status"]
    L += [r"\bottomrule", r"\end{tabular}", r"\smallskip",
          r"\begin{minipage}{0.97\linewidth}\footnotesize",
          (r"Notes: the specification of Table~\ref{tab:backtest-occ}, panel A, re-estimated with the review-time "
           r"ratio $t^R_j/t_j$ set to each value; the range is the sourced range in \texttt{data/\allowbreak tasks/\allowbreak params.yaml}. "
           r"$^{a}$Current sourced value. $^{b}$Value assumed by the engine before the assumptions audit. "
           r"``Automation cheapest'' is the share of exposed time, among activities where automation is capability-feasible "
           r"and permitted in May 2025, on which automation is the cheapest mode. Re-estimated on a 0.01 grid, the model "
           r"share alone stops being significant at 5\% at a ratio of " + fmt(th["alone_loses_5pct"])
           + r"; with exposure in the regression, at " + fmt(th["joint_loses_5pct"])
           + r". It stops beating exposure out of sample at " + fmt(th["alone_stops_beating_exposure_oos"])
           + r" (with exposure, at " + fmt(th["joint_stops_beating_exposure_oos"]) + r"). Thresholds interpolate "
           r"linearly between grid points; controls and standard errors as in Table~\ref{tab:backtest-occ}."),
          r"\end{minipage}", r"\end{table}"]
    return "\n".join(L) + "\n"


def table_tests(R: dict) -> str:
    MT = R["multiple_testing"]
    L = [r"\begin{table}[tbp]", r"\centering",
         r"\caption{Headline tests and a Bonferroni correction for " + str(MT["family_size"]) + r" tests}\label{tab:backtest-tests}",
         r"\footnotesize", r"\begin{tabular}{@{}lccccc@{}}", r"\toprule",
         r"Test (coefficient on the named score, 1 sd) & Estimate & (s.e.) & $|t|$ & Bonferroni $p$ & Survives\\",
         r"\midrule"]
    for f in MT["tests"]:
        nd = 2 if f["label"].startswith("Firms") else 3
        L.append(f"{f['label']} & {f3(f['b'], nd)} & ({f3(f['se'], nd)}) & {abs(f['t']):.2f} & "
                 f"{f['p_bonferroni']:.3f} & {'yes' if f['survives'] else 'no'}\\\\")
    L += [r"\bottomrule", r"\end{tabular}", r"\smallskip",
          r"\begin{minipage}{0.97\linewidth}\footnotesize",
          (r"Notes: the family is fixed in \texttt{code/\allowbreak validation/\allowbreak backtest.py}. Bonferroni "
           r"$p$ is $\min(1, " + str(MT["family_size"]) + r"p)$; a test survives if it is below 0.05, which needs "
           r"$|t|\ge" + f"{MT['critical_abs_t_normal']:.2f}" + r"$. "
           + ("Holm's step-down procedure gives the same set. " if [f["survives"] for f in MT["tests"]]
              == [f["survives_holm"] for f in MT["tests"]] else "Holm's step-down procedure differs (see the JSON). ")
           + r"For the placebo rows, surviving would count against the model. Log employment is the outcome unless "
           r"stated; firm rows are in percentage points of revenue; the within-occupation cell row is per standard "
           r"deviation of the score within occupations."),
          r"\end{minipage}", r"\end{table}"]
    return "\n".join(L) + "\n"


def table_cells(R: dict) -> str:
    C = R["cells"]
    rg, st = C["regressions"], C["stats"]

    def bs(reg, key, within=False):
        if reg is None or key not in reg["coef"]:
            return "", ""
        c = reg["coef"][key]
        b, se = (c["b_per_within_sd"], c["se_per_within_sd"]) if within else (c["b"], c["se"])
        nd = 4 if within else 3
        return f3(b, nd), f"({f3(se, nd)})"

    L = [r"\begin{table}[tbp]", r"\centering",
         r"\caption{Occupation $\times$ industry cells, May 2021 to May 2025 (change in log employment)}\label{tab:backtest-cells}",
         r"\footnotesize", r"\setlength{\tabcolsep}{5pt}", r"\begin{tabular}{@{}lcccccc@{}}", r"\toprule",
         r"\multicolumn{7}{@{}l}{\emph{A. Sourced review-time ratio}}\\",
         r" & (1) & (2) & (3) & (4) & (5) & (6)\\", r"\midrule"]
    specs = [rg["E"], rg["Mc"], rg["E_Mc"], rg["Feas"], rg["E_Feas"], rg["within"]]
    for lab, key, within in [("Exposure", "E", False), ("Model share", "Mc", False),
                             ("Capability-feasible share", "M_feas", False), ("Model share, within occupation", "Mc", True)]:
        cells_ = [bs(r_, key, within) if (within == (i == 5)) else ("", "") for i, r_ in enumerate(specs)]
        L.append(lab + " & " + " & ".join(c[0] for c in cells_) + r"\\")
        L.append(" & " + " & ".join(c[1] for c in cells_) + r"\\")
    L.append(r"Fixed effects & \multicolumn{5}{c}{industry, SOC major group} & occ., industry\\")
    cv = C["cv"]
    L.append(r"Out-of-sample $R^2$ & " + " & ".join([f3(cv["E"]["mean"]), f3(cv["Mc"]["mean"]), f3(cv["E+Mc"]["mean"]),
                                                    f3(cv["Feas"]["mean"]), "", ""]) + r"\\")
    L.append(r"\addlinespace")
    L.append(r"\multicolumn{7}{@{}l}{\emph{B. Columns (1) and (3) reweighted}} \\")
    L.append(r" & Exposure & \multicolumn{2}{c}{Exposure and model share} & & & \\")
    for lab, suf in [("No industry effects", "_noind"), ("Occupations weighted equally", "_eqw"),
                     ("Both", "_eqw_noind")]:
        e1, e2, m2 = bs(rg["E" + suf], "E"), bs(rg["E_Mc" + suf], "E"), bs(rg["E_Mc" + suf], "Mc")
        L.append(f"{lab} & {e1[0]} & {e2[0]} & {m2[0]} & & & \\\\")
        L.append(f" & {e1[1]} & {e2[1]} & {m2[1]} & & & \\\\")
    L.append(r"\addlinespace")
    L.append(r"\multicolumn{7}{@{}l}{\emph{C. Across the review-time ratio}}\\")
    L.append(r"Review ratio & \multicolumn{2}{c}{Model share} & \multicolumn{2}{c}{With exposure} & "
             r"\multicolumn{2}{c}{Within occupation}\\")
    show = set(round(x, 4) for x in R["occ"]["rho_sweep"]["table_points"]) | {round(R["occ"]["rho_sweep"]["pre_audit_value"], 4)}
    for q in C["sweep"]["path"]:
        if round(q["rho"], 4) not in show:
            continue
        if "b_alone" not in q:
            L.append(f"{q['rho']:.3f} & \\multicolumn{{6}}{{c}}{{no variation}}\\\\")
            continue
        sdw = q["sd_within"]
        if sdw > 1e-6 and "b_within" in q:
            wb, ws = f3(q["b_within"] / C["stats"]["sd_Mc"] * sdw, 4), f"({f3(q['se_within'] / C['stats']['sd_Mc'] * sdw, 4)})"
        else:
            wb, ws = "n.a.", ""
        L.append(f"{q['rho']:.3f} & {f3(q['b_alone'])} & ({f3(q['se_alone'])}) & {f3(q['b_joint'])} & "
                 f"({f3(q['se_joint'])}) & {wb} & {ws}\\\\")
    L += [r"\bottomrule", r"\end{tabular}", r"\smallskip",
          r"\begin{minipage}{0.97\linewidth}\footnotesize",
          (r"Notes: " + f"{st['n_cells']:,}" + r" occupation $\times$ industry cells (" + f"{st['n_occupations']}"
           + r" occupations, " + f"{st['n_industries']}" + r" industries) with at least " + f"{st['min_cell_emp_2021']:,}"
           + r" jobs in May 2021 and an estimate in May 2025, covering " + f"{100 * st['emp21_share_of_national']:.0f}"
           + r"\% of May 2021 employment. Industries are four-digit NAICS harmonized from NAICS 2017 to 2022, with retail "
           r"trade at the sector level. The model share uses each cell's May 2021 wage in the cost crossover. Columns "
           r"(1) to (5) control for the physical task share, the job zone and the log cell wage; column (6) for the log "
           r"cell wage, with occupation and industry effects, so its only score variation is the cell wage. The "
           r"within-occupation coefficients are per standard deviation of the score within occupations ("
           + f"{st['sd_Mc_within_occupation']:.4f}" + r", " + f"{100 * st['share_var_within']:.2f}"
           + r"\% of its variance); the others per overall standard deviation. Standard errors clustered two-way by "
           r"occupation and industry. Out-of-sample $R^2$: 10-fold cross-validation with folds by occupation, "
           + str(C["cv"]["reps"]) + r" repetitions, unweighted."),
          r"\end{minipage}", r"\end{table}"]
    return "\n".join(L) + "\n"


def mnum(x, nd=3) -> str:
    """A number for the text: an explicit minus sign that works in and out of math mode."""
    if x is None or not np.isfinite(x):
        return "n.a."
    if abs(x) < 0.5 * 10 ** (-nd):
        x = 0.0
    v = f"{abs(x):.{nd}f}"
    return r"\ensuremath{-}" + v if x < 0 else v


def pct(x, nd=0) -> str:
    return f"{100 * x:.{nd}f}\\%"


def text_macros(R: dict, INFO: dict, rr: list) -> dict:
    """Every number quoted in part2/validation_backtest.tex, as macro name -> LaTeX text."""
    M = {}

    def put(name, val):
        assert re.fullmatch(r"bt[A-Za-z]+", name), name
        assert name not in M, name
        M[name] = str(val)

    def coef(prefix, reg, key, nd=3):
        c = reg["coef"][key]
        put(prefix + "B", mnum(c["b"], nd))
        put(prefix + "Se", mnum(c["se"], nd))
        return c

    par, occ = R["parameters"], R["occ"]
    D, mn = occ["decomposition"], occ["main"]
    rb = {row["label"]: row for row in rr if not row.get("header")}
    SW = occ["rho_sweep"]
    # design and parameters
    put("btHzero", f"{par['H0']:.2f}")
    put("btTd", f"{par['Td_days']:.0f}")
    put("btHendSec", f"{INFO['main']['H_end2021_hours'] * 3600:.0f}")
    put("btRA", f"{100 * par['r_A']:.0f}\\%")
    put("btRU", f"{100 * par['r_U']:.0f}\\%")
    put("btRhoRev", f"{par['rho_rev']:g}")
    put("btRhoOld", f"{SW['pre_audit_value']:g}")
    put("btRhoLo", f"{SW['range'][0]:g}")
    put("btRhoHi", f"{SW['range'][1]:g}")
    put("btNcodes", R["crosswalk"]["oews_2021_2025"]["n_2025"])
    put("btNocc", occ["sample"]["n"])
    put("btEmpShare", f"{100 * occ['sample']['emp21_share']:.1f}\\%")
    put("btNmajor", occ["sample"]["n_major_groups"])
    put("btFolds", K_FOLDS)
    put("btReps", N_CV_REPS)
    # main result
    c = coef("btEAlone", D["E"]["alone"], "E")
    put("btEAloneLp", f"{100 * abs(c['b']):.1f}")
    c = coef("btEWbs", mn["dlwbs"]["exposure"], "E")
    put("btEWbsLp", f"{100 * abs(c['b']):.1f}")
    cM = coef("btMAlone", D["M"]["alone"], "M")
    put("btMAloneT", f"{abs(cM['t']):.1f}")
    cv = D["cv"]
    put("btCvC", f"{cv['controls']['mean']:.3f}")
    put("btCvE", f"{cv['E']['mean']:.3f}")
    put("btCvM", f"{cv['M']['mean']:.3f}")
    put("btRepsMBeatsE", f"{round(cv['share_reps_M_beats_E'] * N_CV_REPS):d}")
    cJ = coef("btMJoint", D["M"]["joint"], "M")
    put("btMJointT", f"{abs(cJ['t']):.1f}")
    coef("btEJoint", D["M"]["joint"], "E")
    put("btCvWbsE", f"{occ['cv']['dlwbs']['exposure']['mean']:.3f}")
    put("btCvWbsM", f"{occ['cv']['dlwbs']['model']['mean']:.3f}")
    coef("btMWage", mn["dlwage"]["both"], "M")
    coef("btMWagePl", occ["placebo_wage"]["pre"]["M"], "M")
    coef("btMW", D["M"]["weighted"], "M")
    coef("btMWJ", mn["dlemp"]["both_w"], "M")
    coef("btEWJ", mn["dlemp"]["both_w"], "E")
    # decomposition
    put("btCvEnp", f"{cv['E_np']['mean']:.3f}")
    put("btCvFeas", f"{cv['M_feas']['mean']:.3f}")
    coef("btTiming", D["timing"]["joint"], "feas_frac")
    coef("btTimingPl", D["timing"]["placebo_2016_21"], "feas_frac")
    fp = INFO["main"]["may2025_feasible_permitted"]
    put("btShareA", pct(fp["share_A"]))
    put("btReviewShare", pct(fp["mean_review_share"]))
    put("btCorrMFeas", f"{R['scores']['descriptive']['corr_M_Mfeas']:.2f}")
    fo = INFO["rho08"]["may2025_feasible_permitted"]
    put("btShareAOld", pct(fo["share_A"]))
    put("btShareUOld", pct(fo["share_U"]))
    put("btShareOOld", pct(fo["share_O"]))
    coef("btMOld", D["M_rho08"]["alone"], "M_rho08")
    put("btCvMOld", f"{cv['M_rho08']['mean']:.3f}")
    coef("btAU", D["M_AU"]["alone"], "M_AU")
    coef("btAUOld", D["extra"]["automate_or_augment_review_08"], "AU_rho08")
    # sweep
    th = SW["thresholds"]
    for name, key in [("btRhoStarAlone", "alone_loses_5pct"), ("btRhoStarJoint", "joint_loses_5pct"),
                      ("btRhoStarCv", "alone_stops_beating_exposure_oos"),
                      ("btRhoStarCvJoint", "joint_stops_beating_exposure_oos"),
                      ("btRhoStarHalfA", "automation_wins_under_half_of_feasible_time")]:
        put(name, f"{th[key]['rho']:.2f}" if th[key]["rho"] is not None else "n.a.")
    lo = next(q for q in SW["path"] if abs(q["rho"] - SW["range"][0]) < 1e-9)
    hi = next(q for q in SW["path"] if abs(q["rho"] - SW["range"][1]) < 1e-9)
    put("btSwLoB", mnum(lo["b_alone"])); put("btSwLoSe", mnum(lo["se_alone"]))
    put("btSwHiB", mnum(hi.get("b_alone", float("nan")))); put("btSwHiSe", mnum(hi.get("se_alone", float("nan"))))
    put("btGridStep", f"{SW['grid_step']:g}")
    sat = [q["rho"] for q in SW["path"] if q["share_A"] >= 0.995]
    put("btRhoSat", f"{max(sat):.2f}" if sat else "n.a.")
    span = SW["range"][1] - SW["range"][0]
    for name, key in [("btRangeShareCv", "alone_stops_beating_exposure_oos"), ("btRangeShareJoint", "joint_loses_5pct"),
                      ("btRangeShareAlone", "alone_loses_5pct")]:
        put(name, pct((th[key]["rho"] - SW["range"][0]) / span) if th[key]["rho"] is not None else "n.a.")
    stays = all(th[k]["stays"] for k in ["alone_loses_5pct", "joint_loses_5pct"] if th[k]["rho"] is not None)
    put("btSweepMonotone", "and it does not regain significance at higher ratios" if stays
        else "although it regains significance at some higher ratios")
    # confounders and placebos
    coef("btEExcl", rb["All three"]["E"], "E")
    coef("btMExcl", rb["All three"]["M"], "M")
    base = rb["Baseline"]
    moves = [abs(rb[k][x]["coef"][kk]["b"] - base[x]["coef"][kk]["b"])
             for k in ["Computer occupations", "Credit and real-estate occupations", "COVID-rebound groups"]
             for x, kk in [("E", "E"), ("M", "M")]]
    put("btExclMaxMove", mnum(max(moves)))
    coef("btETrendBase", rb["Trend sample, baseline controls"]["E"], "E")
    coef("btETrendCtl", rb["Trend sample, plus 2016--21 change"]["E"], "E")
    cmb = coef("btMTrendBase", rb["Trend sample, baseline controls"]["M"], "M")
    coef("btMTrendCtl", rb["Trend sample, plus 2016--21 change"]["M"], "M")
    coef("btEProj", rb["Plus BLS 2020--30 projected growth"]["E"], "E")
    coef("btMProj", rb["Plus BLS 2020--30 projected growth"]["M"], "M")
    ceb = rb["Trend sample, baseline controls"]["E"]["coef"]["E"]
    cep = coef("btEPl", D["E"]["placebo_2016_21"], "E")
    put("btEPlRatio", pct(abs(cep["b"]) / abs(ceb["b"])))
    cmp_ = coef("btMPl", D["M"]["placebo_2016_21"], "M")
    put("btMPlRatio", pct(abs(cmp_["b"]) / abs(cmb["b"])))
    # variants
    coef("btVTd", rb["Capability doubling 207 days"]["M"], "M_td207")
    coef("btVThten", rb["Capability path: METR TH1.0 trend"]["M"], "M_th10")
    coef("btVAei", rb["Task length from AEI times"]["M"], "M_aei_hours")
    coef("btVPrice", rb["Inference price $\\times 10$"]["M"], "M_price10")
    put("btVIotaLoB", mnum(rb["Data readiness 0.2"]["M"]["coef"]["M_iota02"]["b"]))
    put("btVIotaHiB", mnum(rb["Data readiness 0.8"]["M"]["coef"]["M_iota08"]["b"]))
    vk = [("Capability doubling 207 days", "M_td207"), ("Capability path: METR TH1.0 trend", "M_th10"),
          ("Task length from AEI times", "M_aei_hours"), ("Inference price $\\times 10$", "M_price10"),
          ("Data readiness 0.2", "M_iota02"), ("Data readiness 0.8", "M_iota08"), ("No outsourcing option", "M_no_outsourcing")]
    vb = [rb[l]["M"]["coef"][k]["b"] for l, k in vk]
    vt = [abs(rb[l]["M"]["coef"][k]["t"]) for l, k in vk]
    put("btVarMinB", mnum(min(vb))); put("btVarMaxB", mnum(max(vb))); put("btVarMinT", f"{min(vt):.1f}")
    put("btVarN", len(vk))
    put("btHMay", f"{INFO['main']['H_may2025_hours']:.1f}")
    pr = R["parameters"]
    put("btTdSlow", f"{pr['Td_days_slow']:.0f}")
    put("btPriceMult", f"{scenario(pr, 'price10')['price_mult']:g}")
    put("btIotaLo", f"{scenario(pr, 'iota02')['iota']:g}")
    put("btIotaHi", f"{scenario(pr, 'iota08')['iota']:g}")
    put("btIota", f"{pr['iota']:g}")
    cap = pd.read_csv(TASKS / "capability_metr_th11.csv", parse_dates=["release_date"])
    spring = cap[(cap.release_date >= "2025-03-01") & (cap.release_date <= "2025-05-31")]
    put("btHMetr", f"{spring.p50_hours.max():.1f}")
    # firms
    F = R["firm"]
    put("btNfirm", F["sample"]["main_n"])
    coef("btFirmM", F["regressions"]["total"]["model"], "mix_M", 1)
    coef("btFirmPl", F["placebo"]["total"]["model"], "mix_M", 1)
    coef("btFirmE", F["regressions"]["total"]["exposure"], "mix_E", 1)
    put("btFirmSd", f"{F['sample']['mix_M_sd']:.3f}")
    put("btFirmMean", f"{F['sample']['mix_M_mean']:.3f}")
    put("btFirmTotChg", mnum(F["sample"]["mean_change_pp"]["total"], 1))
    put("btFirmSmChg", mnum(F["sample"]["mean_change_pp"]["sm"], 1))
    cs = [F["regressions"][b]["model"]["coef"]["mix_M"] for b in BUCKETS + ["total"]]
    npos, nsig = sum(c["b"] > 0 for c in cs), sum(c["p"] < 0.05 for c in cs)
    words = {0: "none", 1: "one", 2: "two", 3: "three", 4: "four", 5: "all five"}
    if npos == 5 and nsig == 0:
        phrase = "All five coefficients are positive, the opposite of the prediction, and none is significant at 5\\%."
    else:
        phrase = (f"{words[npos].capitalize()} of the five coefficients {'is' if npos == 1 else 'are'} positive, the "
                  f"opposite of the prediction, and {words[nsig]} {'is' if nsig == 1 else 'are'} significant at 5\\%.")
    put("btFirmSignPhrase", phrase)
    # 2016 vintage verification, crosswalk recovery, 2019 and 2020 vintages
    V = R["crosswalk"]["soc2010_2018_pre_period"]["vintage_verification"]
    put("btVerUrl", r"\url{" + V["url"] + "}")
    put("btVerDate", pd.Timestamp(V["accessed"]).strftime("%-d %B %Y"))
    put("btVerN", V["n_occupations"])
    put("btVerBlsN", V["bls_detailed_occupations_listed"])
    put("btVerSumEmp", f"{V['sum_tot_emp']:,}".replace(",", "{,}"))
    put("btVerSumWage", f"{V['sum_a_mean']:,}".replace(",", "{,}"))
    X = R["crosswalk"]["soc2010_2018_pre_period"]
    put("btXwExactN", X["n_exact"]); put("btXwExactShare", pct(X["emp_share_exact"], 1))
    put("btXwAllocN", X["n_exact_or_allocated"]); put("btXwAllocShare", pct(X["emp_share_exact_or_allocated"], 1))
    put("btIdN", X["identity_rule"]["n"]); put("btIdShare", pct(X["identity_rule"]["emp_share"], 1))
    coef("btEPlSplit", rb["Log employment, split codes included"]["E"], "E")
    coef("btMPlSplit", rb["Log employment, split codes included"]["M"], "M")
    coef("btEPlId", rb["Log employment, identity rule (superseded)"]["E"], "E")
    coef("btMPlId", rb["Log employment, identity rule (superseded)"]["M"], "M")
    Hh = R["crosswalk"]["hybrid_2019_2020"]
    put("btHybN", Hh["n_detailed_2019"]); put("btHybSame", Hh["n_codes_same_as_2021"])
    put("btHybAgg", Hh["n_hybrid_aggregates"])
    put("btNOneNineTwoOne", Hh["n_2019_21"]); put("btShareOneNineTwoOne", pct(Hh["emp_share_2019_21"], 1))
    put("btNOneSixOneNine", Hh["n_2016_19_exact"]); put("btShareOneSixOneNine", pct(Hh["emp_share_2016_19"], 1))
    coef("btMNineBase", rb["2019 sample, baseline controls"]["M"], "M")
    coef("btMNineCtl", rb["2019 sample, plus 2019--21 change"]["M"], "M")
    coef("btENineBase", rb["2019 sample, baseline controls"]["E"], "E")
    coef("btENineCtl", rb["2019 sample, plus 2019--21 change"]["E"], "E")
    coef("btMCovid", rb["2019 sample, plus 2019--20 COVID shock"]["M"], "M")
    coef("btECovid", rb["2019 sample, plus 2019--20 COVID shock"]["E"], "E")
    cb16 = coef("btMSixBase", rb["2016--19 sample, baseline controls"]["M"], "M")
    coef("btMSixCtl", rb["2016--19 sample, plus 2016--19 change"]["M"], "M")
    coef("btESixCtl", rb["2016--19 sample, plus 2016--19 change"]["E"], "E")
    cpl = coef("btMPlPre", rb["Log employment, 2016--19"]["M"], "M")
    coef("btEPlPre", rb["Log employment, 2016--19"]["E"], "E")
    coef("btFPlPre", rb["Log employment, 2016--19"]["F"], "M_feas")
    put("btMPlPreT", f"{abs(cpl['t']):.1f}")
    put("btMPlPreYearRatio", pct((abs(cpl["b"]) / 3.0) / (abs(cb16["b"]) / 4.0)))
    coef("btMWagePlPre", rb["Log mean wage, 2016--19"]["M"], "M")
    # occupation x industry cells
    Ce = R["cells"]; cs_, cr_ = Ce["stats"], Ce["regressions"]
    put("btCellN", f"{cs_['n_cells']:,}".replace(",", "{,}")); put("btCellOcc", cs_["n_occupations"])
    put("btCellInd", cs_["n_industries"]); put("btCellShare", pct(cs_["emp21_share_of_national"]))
    put("btCellMin", f"{cs_['min_cell_emp_2021']:,}".replace(",", "{,}"))
    coef("btCE", cr_["E"], "E"); coef("btCM", cr_["Mc"], "Mc")
    coef("btCJM", cr_["E_Mc"], "Mc"); coef("btCJE", cr_["E_Mc"], "E")
    coef("btCF", cr_["Feas"], "M_feas"); coef("btCJFF", cr_["E_Feas"], "M_feas"); coef("btCJFE", cr_["E_Feas"], "E")
    put("btCCvE", f"{Ce['cv']['E']['mean']:.3f}"); put("btCCvM", f"{Ce['cv']['Mc']['mean']:.3f}")
    put("btCCvF", f"{Ce['cv']['Feas']['mean']:.3f}"); put("btCCvC", f"{Ce['cv']['controls']['mean']:.3f}")
    coef("btCNiJM", cr_["E_Mc_noind"], "Mc"); coef("btCNiJE", cr_["E_Mc_noind"], "E")
    coef("btCEqJM", cr_["E_Mc_eqw"], "Mc"); coef("btCEqJE", cr_["E_Mc_eqw"], "E")
    coef("btCEqJFF", cr_["E_Feas_eqw"], "M_feas"); coef("btCEqJFE", cr_["E_Feas_eqw"], "E")
    w_ = cr_["within"]["coef"]["Mc"]
    put("btCWB", mnum(w_["b_per_within_sd"], 4)); put("btCWSe", mnum(w_["se_per_within_sd"], 4))
    ww_ = cr_["within_w"]["coef"]["Mc"]
    put("btCWwB", mnum(ww_["b_per_within_sd"], 4)); put("btCWwSe", mnum(ww_["se_per_within_sd"], 4))
    wp_ = cr_["within_p10"]["coef"]["Mc_p10"]
    put("btCWpB", mnum(wp_["b_per_within_sd"], 4)); put("btCWpSe", mnum(wp_["se_per_within_sd"], 4))
    put("btCTopN", 50)
    put("btCTopShare", pct(cs_["top50_share_of_cells"])); put("btCTopGroupShare", pct(cs_["largest_major_group_share"]))
    put("btCTopGroup", cs_["largest_major_group"]); put("btCMaxCells", cs_["max_cells_per_occupation"])
    put("btCMedCells", f"{cs_['median_cells_per_occupation']:g}")
    put("btCWSign", "positive, the opposite of the prediction" if w_["b"] > 0 else "negative, as predicted")
    put("btCWsd", f"{cs_['sd_Mc_within_occupation']:.4f}"); put("btCWvar", pct(cs_["share_var_within"], 2))
    ct_ = Ce["sweep"]["thresholds"]
    put("btCRhoStarAlone", f"{ct_['alone_loses_5pct']['rho']:.2f}" if ct_["alone_loses_5pct"]["rho"] is not None
        else ct_["alone_loses_5pct"]["status"])
    put("btCJointPhrase", "it is not significant at any ratio in the range" if ct_["joint_loses_5pct"]["rho"] is None
        and "not significant" in ct_["joint_loses_5pct"]["status"] else
        f"it loses significance at {ct_['joint_loses_5pct']['rho']:.2f}" if ct_["joint_loses_5pct"]["rho"] is not None
        else "it stays significant across the range")
    put("btCWithinSig", f"{ct_['within_significant_points']} of {ct_['within_points']}")
    # multiple testing
    MT = R["multiple_testing"]
    surv = [f["label"] for f in MT["tests"] if f["survives"]]
    put("btNtests", MT["family_size"])
    put("btTcrit", f"{MT['critical_abs_t_normal']:.2f}")
    put("btNsurvive", len(surv))
    lab = lambda x: x[0].lower() + x[1:]
    put("btSurvivorsList", ("; ".join(lab(x) for x in surv[:-1]) + "; and " + lab(surv[-1])) if len(surv) > 1
        else (lab(surv[0]) if surv else "none"))
    fails = [f["label"] for f in MT["tests"] if not f["survives"] and not f["label"].startswith("Placebo")]
    put("btFailsList", ("; ".join(lab(x) for x in fails[:-1]) + "; and " + lab(fails[-1])) if len(fails) > 1
        else (lab(fails[0]) if fails else "none"))
    jt = next(f for f in MT["tests"] if f["label"] == "Model share, with exposure")
    put("btJointSurvives", "survives" if jt["survives"] else "does not survive")
    plac = [f for f in MT["tests"] if f["label"].startswith("Placebo")]
    put("btPlaceboSurvive", "No placebo survives." if not any(f["survives"] for f in plac)
        else "At least one placebo survives, which counts against the model.")
    put("btNtestsPrev", MT["previous_family_size"])
    put("btTcritPrev", f"{MT['critical_abs_t_previous']:.2f}")
    changed = [f["label"] for f in MT["tests"][:MT["previous_family_size"]] if f["survives"] != f["survives_previous_family_size"]]
    put("btSurvivalChangePhrase", "No test among the original " + str(MT["previous_family_size"]) + " changes status"
        if not changed else "The status of " + "; ".join(lab(x) for x in changed) + " changes")
    newsurv = [f["label"] for f in MT["tests"][MT["previous_family_size"]:] if f["survives"]]
    put("btNewSurvivorsList", "; ".join(lab(x) for x in newsurv) if newsurv else "none")
    emin = min(abs(f["t"]) for f in MT["tests"] if f["survives"])
    put("btMinSurvT", f"{emin:.2f}")
    tE = next(f for f in MT["tests"] if f["label"] == "Exposure, log employment")
    put("btEAloneT", f"{abs(tE['t']):.2f}")
    margin = abs(tE["t"]) - MT["critical_abs_t_normal"]
    put("btEAlonePhrase", ("Exposure alone survives narrowly" if margin < 0.25 else "Exposure alone survives")
        if tE["survives"] else "Exposure alone does not survive")
    tP = next(f for f in MT["tests"] if f["label"] == "Placebo 2016--19: model share")
    put("btPrePlaceboPhrase", "it is significant at the conventional 5\\% level" if tP["p"] < 0.05
        else "it is not significant at the conventional 5\\% level either")
    same = [f["survives"] for f in MT["tests"]] == [f["survives_holm"] for f in MT["tests"]]
    put("btHolmPhrase", "Holm's step-down procedure gives the same set." if same else
        "Holm's step-down procedure adds " + "; ".join(lab(f["label"]) for f in MT["tests"]
                                                       if f["survives_holm"] and not f["survives"]) + ".")
    return M


# =============================================================================================================
# 8. Main
# =============================================================================================================

def main():
    par = load_parameters()
    R = {"meta": {"script": "code/validation/backtest.py", "spec": "notes/unified_model_spec.md Section 24.1",
                  "deterministic": True, "seed": SEED0},
         "inputs": {}, "parameters": {}, "crosswalk": {}, "scores": {}, "occ": {}, "firm": {}}
    for f in [F_OEWS21, F_OEWS25, F_OEWS16, F_PROJ, F_LABELS, F_JZ, F_PANEL, F_OEWS21_IND, F_OEWS25_IND, F_SOCXW,
              F_OEWS19, F_OEWS20, TASKS / "capability_metr_th11.csv", TASKS / "occ_activity.csv",
              TASKS / "activities.csv", TASKS / "occupations.csv", TASKS / "occ_exposure.csv",
              TASKS / "xw_task_dwa.csv", TASKS / "xw_oews_onetsoc.csv", TASKS / "function_occ.csv",
              TASKS / "function_occ_by_industry.csv", TASKS / "industry_function_shares.csv", TASKS / "params.yaml",
              TASKS / "_build" / "capability.json", ENGINE / "defaults.yaml", ENGINE / "priors" / "activity_attributes.csv"]:
        R["inputs"][str(f.relative_to(ROOT))] = sha256(f)
    R["parameters"] = {k: v for k, v in par.items()}

    # ---- occupations: vintages and crosswalk ----------------------------------------------------------------
    o21, o25 = fill_wages(load_oews_2021()), fill_wages(load_oews_2025())
    t21, t25 = dict(zip(o21.soc, o21.title)), dict(zip(o25.soc, o25.title))
    common = sorted(set(o21.soc) & set(o25.soc))
    title_changes = [c for c in common if t21[c].strip().lower() != t25[c].strip().lower()]
    R["crosswalk"]["oews_2021_2025"] = {
        "rule": "identity on SOC 2018 detailed codes; both vintages use SOC 2018",
        "n_2021": int(len(o21)), "n_2025": int(len(o25)), "n_common": len(common),
        "only_2021": sorted(set(o21.soc) - set(o25.soc)), "only_2025": sorted(set(o25.soc) - set(o21.soc)),
        "title_changes": title_changes,
        "emp_share_2021_common": float(o21[o21.soc.isin(common)].emp.sum() / o21.emp.sum()),
        "wage_imputed_from_hourly_2021": int(o21.wage_imputed.sum()), "wage_imputed_from_hourly_2025": int(o25.wage_imputed.sum())}
    occ = o21.rename(columns={"emp": "emp21", "a_mean": "a_mean21", "h_mean": "h_mean21"}).drop(columns="wage_imputed")
    occ = occ.merge(o25[["soc", "emp", "a_mean"]].rename(columns={"emp": "emp25", "a_mean": "a_mean25"}), on="soc")
    occ["major"] = occ.soc.str[:2]
    occ["minor"] = occ.soc.str[:4]
    occ["dlemp"] = np.log(occ.emp25 / occ.emp21)
    occ["dlwage"] = np.log(occ.a_mean25 / occ.a_mean21)
    wb21, wb25 = occ.emp21 * occ.a_mean21, occ.emp25 * occ.a_mean25
    occ["wbs21"], occ["wbs25"] = wb21 / wb21.sum(), wb25 / wb25.sum()
    occ["dlwbs"] = np.log(occ.wbs25 / occ.wbs21)
    occ["dwbs_bp"] = 1e4 * (occ.wbs25 - occ.wbs21)
    occ["ln_w21"] = np.log(occ.a_mean21)
    occ["emp21_w"] = occ.emp21

    # pre-period (SOC 2010 cross-section) and controls
    o16 = load_oews_2016()
    # (a) the earlier identity rule, kept only for comparison
    idm = occ[["soc", "title", "emp21", "a_mean21"]].merge(o16, on="soc", how="left")
    resid = idm.title.str.contains("All Other", case=False, regex=False)
    idm.loc[resid, ["emp16", "a_mean16"]] = np.nan
    occ["dlemp_pre_identity"] = np.log(idm.emp21 / idm.emp16).values
    # (b) the official BLS SOC 2010 to 2018 crosswalk (main): exact components; allocated split codes as a variant
    xw, xw_info = pre_period_crosswalk(o16, o21)
    occ = occ.join(xw, on="soc")
    ok_e = (occ.xw_kind == "exact") & (occ.xw_E16 > 0)
    ok_a = occ.xw_kind.isin(["exact", "allocated"]) & (occ.xw_E16 > 0)
    occ["dlemp_pre"] = np.where(ok_e, np.log(occ.xw_E21 / occ.xw_E16.where(ok_e)), np.nan)
    occ["dlwage_pre"] = np.where(ok_e, np.log(occ.xw_w21 / occ.xw_w16.where(ok_e)), np.nan)
    occ["dlemp_pre_alloc"] = np.where(ok_a, np.log(occ.xw_E21 / occ.xw_E16.where(ok_a)), np.nan)
    tot21 = occ.emp21.sum()
    R["crosswalk"]["soc2010_2018_pre_period"] = {
        "source": str(F_OEWS16.relative_to(ROOT)),
        "crosswalk": str(F_SOCXW.relative_to(ROOT)) + " (BLS, November 2017, sheet Sorted by 2010)",
        "vintage": "undocumented in the repository; tot_emp and a_mean are constant across the file's year index; "
                   "codes are SOC 2010; spot values are consistent with OEWS May 2016 (the crosswalk does not verify it)",
        "rule": "connected components of the official crosswalk (see pre_period_crosswalk); main placebo uses exact "
                "components, the variant adds split codes, each carrying its component's change",
        "crosswalk_info": xw_info,
        "n_exact": int(occ.dlemp_pre.notna().sum()), "n_exact_or_allocated": int(occ.dlemp_pre_alloc.notna().sum()),
        "n_incomplete": int((occ.xw_kind == "incomplete").sum()),
        "emp_share_exact": float(occ.loc[occ.dlemp_pre.notna(), "emp21"].sum() / tot21),
        "emp_share_exact_or_allocated": float(occ.loc[occ.dlemp_pre_alloc.notna(), "emp21"].sum() / tot21),
        "identity_rule": {"n": int(occ.dlemp_pre_identity.notna().sum()),
                          "emp_share": float(occ.loc[occ.dlemp_pre_identity.notna(), "emp21"].sum() / tot21)},
        "agreement_with_identity_where_both": float(np.corrcoef(
            occ.dropna(subset=["dlemp_pre", "dlemp_pre_identity"]).dlemp_pre,
            occ.dropna(subset=["dlemp_pre", "dlemp_pre_identity"]).dlemp_pre_identity)[0, 1])}
    R["crosswalk"]["soc2010_2018_pre_period"]["vintage_verification"] = VERIFIED_2016
    # May 2019 and May 2020 (hybrid SOC). A code published in the hybrid files that is also a SOC 2018 code has its
    # SOC 2018 definition, so 2019 to 2021 and 2019 to 2020 changes are taken code by code. For 2016 to 2019 the
    # 2016 side uses the crosswalk's exact components. Occupations folded into one of the 29 hybrid aggregates (for
    # example software developers inside 15-1256) are left out; BLS's hybrid membership table is not local.
    o19, o20 = load_oews_hybrid(F_OEWS19), load_oews_hybrid(F_OEWS20)
    e19, e20 = o19.set_index("soc"), o20.set_index("soc")
    occ["emp19"], occ["a_mean19"] = occ.soc.map(e19.emp), occ.soc.map(e19.a_mean)
    occ["emp20"] = occ.soc.map(e20.emp)
    occ["dlemp_1921"] = np.log(occ.emp21 / occ.emp19)
    occ["dlemp_1920"] = np.log(occ.emp20 / occ.emp19)
    ok19 = ok_e & occ.emp19.notna()
    occ["dlemp_pre1619"] = np.where(ok19, np.log(occ.emp19 / occ.xw_E16.where(ok19)), np.nan)
    occ["dlwage_pre1619"] = np.where(ok19, np.log(occ.a_mean19 / occ.xw_w16.where(ok19)), np.nan)
    hyb = sorted(set(o19.soc) - set(occ.soc))
    _x = load_soc_crosswalk()
    hyb_2010 = [c for c in hyb if c in set(_x.c10) and c not in set(_x.c18)]
    hyb_2018 = [c for c in hyb if c in set(_x.c18)]
    hyb_agg = [c for c in hyb if c not in hyb_2010 and c not in hyb_2018]
    R["crosswalk"]["hybrid_2019_2020"] = {
        "files": [str(F_OEWS19.relative_to(ROOT)), str(F_OEWS20.relative_to(ROOT))],
        "n_detailed_2019": int(len(o19)), "n_detailed_2020": int(len(o20)),
        "n_codes_same_as_2021": int(occ.emp19.notna().sum()), "hybrid_or_2010_codes_2019": hyb,
        "n_hybrid_aggregates": len(hyb_agg), "soc2010_codes_2019": hyb_2010, "soc2018_codes_not_in_2021_2025": hyb_2018,
        "n_2019_21": int(occ.dlemp_1921.notna().sum()), "n_2016_19_exact": int(occ.dlemp_pre1619.notna().sum()),
        "emp_share_2019_21": float(occ.loc[occ.dlemp_1921.notna(), "emp21"].sum() / tot21),
        "emp_share_2016_19": float(occ.loc[occ.dlemp_pre1619.notna(), "emp21"].sum() / tot21),
        "rule": "2019-21 and 2019-20: identical codes (SOC 2018 definitions in the hybrid files); 2016-19: exact "
                "crosswalk components whose SOC 2018 code is published in May 2019"}
    occ["job_zone"] = occ.soc.map(job_zones())
    oc = pd.read_csv(TASKS / "occupations.csv")
    occ["phys_share"] = occ.soc.map(oc.set_index("soc").physical_share)
    ox = pd.read_csv(TASKS / "occ_exposure.csv").set_index("soc")
    occ["E_occ"] = occ.soc.map(ox.eloundou_gpt4_beta)
    occ["bls_proj"] = bls_projections(occ.title) / 100.0
    R["crosswalk"]["bls_projections_2020_30"] = {"rule": "exact lower-case title match to OEWS 2021 titles",
                                                 "n_matched": int(occ.bls_proj.notna().sum()), "n": int(len(occ))}

    # ---- the model -------------------------------------------------------------------------------------------
    rows = activity_rows(par)
    R["crosswalk"]["activities"] = {
        "rows": int(len(rows)), "socs": int(rows.soc.nunique()),
        "share_time_with_occ_specific_beta": float(np.average(rows.beta_occ_specific, weights=rows.s)),
        "note": "beta is the mean Eloundou GPT-4 beta over the occupation's own tasks linked to the DWA (task IDs, "
                "O*NET 27.2 labels joined to O*NET 31.0 task-DWA links); where the occupation has no labelled task "
                "for the DWA, the DWA-level mean in activities.csv is used"}
    wage_h = occ.set_index("soc").h_mean21
    names = ["main", "td207", "th10", "aei_hours", "price10", "no_outsourcing", "iota02", "iota08", "rho037", "rho08",
             "rho119", "human_beta", "static"]
    S, INFO = {}, {}
    for nm in names:
        agg, info = model_scores(rows, wage_h, par, scenario(par, nm))
        S[nm], INFO[nm] = agg, info
    R["scores"]["scenario_info"] = INFO
    base = S["main"]
    for c in base.columns:
        occ[c] = occ.soc.map(base[c])
    for nm in names[1:]:
        occ["M_" + nm] = occ.soc.map(S[nm]["M"])
        occ["F_" + nm] = occ.soc.map(S[nm]["M_feas"])
    occ["AU_rho08"] = occ.soc.map(S["rho08"]["M_AU"])
    occ["E_h"] = occ.soc.map(S["human_beta"]["E"])
    occ["M_human_beta"] = occ.soc.map(S["human_beta"]["M"])
    sample = occ.dropna(subset=["M", "E", "phys_share", "ln_w21", "job_zone", "dlemp"]).copy()
    R["occ"]["sample"] = {"n": int(len(sample)), "emp21_share": float(sample.emp21.sum() / occ.emp21.sum()),
                          "dropped_no_activity_data": int(occ.M.isna().sum())}
    desc = {}
    for c in ["E", "E_np", "M", "M_end", "M_static", "M_AU", "M_save", "M_feas", "E_occ"] + ["M_" + n for n in names[1:]]:
        x = sample[c]
        desc[c] = {"mean": float(x.mean()), "sd": float(x.std()), "p25": float(x.quantile(.25)),
                   "p75": float(x.quantile(.75)), "max": float(x.max()),
                   "corr_with_E": float(np.corrcoef(x, sample.E)[0, 1]) if x.std() > 0 else None,
                   "emp_weighted_mean": float(np.average(x, weights=sample.emp21))}
    desc["outcomes"] = {y: {"mean": float(sample[y].mean()), "sd": float(sample[y].std()),
                            "emp_weighted_mean": float(np.average(sample[y], weights=sample.emp21))}
                        for y in ["dlemp", "dlwage", "dlwbs", "dwbs_bp", "dlemp_pre", "dlwage_pre"]}
    top = sample.sort_values("M", ascending=False).head(15)[["soc", "title", "E", "M", "dlemp"]]
    desc["top15_by_model"] = top.round(4).to_dict(orient="records")
    gap = sample.assign(g=sample.M - sample.E * np.polyfit(sample.E, sample.M, 1)[0])
    desc["largest_model_minus_exposure_residual"] = gap.sort_values("g", ascending=False).head(10)[
        ["soc", "title", "E", "M"]].round(4).to_dict(orient="records")
    desc["smallest_model_minus_exposure_residual"] = gap.sort_values("g").head(10)[
        ["soc", "title", "E", "M"]].round(4).to_dict(orient="records")
    desc["corr_M_Mfeas"] = float(np.corrcoef(sample.M, sample.M_feas)[0, 1])
    R["scores"]["descriptive"] = desc
    R["occ"]["sample"]["n_major_groups"] = int(sample.major.nunique())

    # ---- occupation regressions ------------------------------------------------------------------------------
    C = ["phys_share", "ln_w21", "job_zone"]
    main_res = {}
    for y in ["dlemp", "dlwbs", "dlwage", "dwbs_bp"]:
        main_res[y] = {"exposure": ols(sample, y, ["E"], C), "model": ols(sample, y, ["M"], C),
                       "both": ols(sample, y, ["E", "M"], C), "both_w": ols(sample, y, ["E", "M"], C, weight="emp21_w"),
                       "exposure_w": ols(sample, y, ["E"], C, weight="emp21_w"),
                       "model_w": ols(sample, y, ["M"], C, weight="emp21_w"),
                       "both_cluster_minor": ols(sample, y, ["E", "M"], C, cluster="minor"),
                       "no_controls_exposure": ols(sample, y, ["E"], [], fe=None),
                       "no_controls_model": ols(sample, y, ["M"], [], fe=None)}
        main_res[y]["delta_r2_model_given_exposure"] = main_res[y]["both"]["r2"] - main_res[y]["exposure"]["r2"]
        main_res[y]["delta_r2_exposure_given_model"] = main_res[y]["both"]["r2"] - main_res[y]["model"]["r2"]
    R["occ"]["main"] = main_res
    R["occ"]["cv"] = {y: drop_reps(cv_r2(sample, y, {"controls": [], "exposure": ["E"], "model": ["M"], "both": ["E", "M"]}, C))
                      for y in ["dlemp", "dlwbs", "dlwage"]}

    # decomposition of the model's logic, fixed in advance as a nested sequence: exposure; exposure on non-physical,
    # permissible activities; plus the capability timing (feasible for A along the horizon path); the AI-mode share
    # (A or U optimal); the automation share (A optimal, the main score)
    s_pre = sample.dropna(subset=["dlemp_pre"])
    DEC = [("E", "Exposure"), ("E_np", "Non-physical, permissible"), ("M_feas", "Capability-feasible"),
           ("M_AU", "Automate or augment"), ("M", "Automate"), ("M_rho08", "Automate, review ratio 0.8")]
    dec = {}
    for k, lab in DEC:
        dec[k] = {"label": lab,
                  "alone": ols(sample, "dlemp", [k], C),
                  "joint": ols(sample, "dlemp", ["E", k], C) if k != "E" else None,
                  "weighted": ols(sample, "dlemp", [k], C, weight="emp21_w"),
                  "pretrend_control": ols(s_pre, "dlemp", [k], C + ["dlemp_pre"]),
                  "placebo_2016_21": ols(s_pre, "dlemp_pre", [k], C),
                  "wbs": ols(sample, "dlwbs", [k], C), "wage": ols(sample, "dlwage", [k], C)}
    sets = {"controls": []}
    for k, _ in DEC:
        sets[k] = [k]
        if k != "E":
            sets["E+" + k] = ["E", k]
    dcv = cv_r2(sample, "dlemp", sets, C)
    for k, _ in DEC:
        if k != "E":
            dcv["share_reps_" + k + "_beats_E"] = float(np.mean(np.array(dcv[k + "_reps"]) > np.array(dcv["E_reps"])))
            dcv["share_reps_E+" + k + "_beats_E"] = float(np.mean(np.array(dcv["E+" + k + "_reps"]) > np.array(dcv["E_reps"])))
    dcv = {k: v for k, v in dcv.items() if not k.endswith("_reps")}
    dec["cv"] = dcv
    sample["feas_frac"] = (sample.M_feas / sample.E_np).where(sample.E_np > 0)
    s_pre = s_pre.assign(feas_frac=(s_pre.M_feas / s_pre.E_np).where(s_pre.E_np > 0))
    dec["timing"] = {
        "note": "feas_frac = M_feas / E_np: the share of an occupation's exposed, non-physical, permissible activity "
                "time that the capability path covers, averaged over the window; tests whether capability timing "
                "adds to exposure restricted to non-physical, permissible work",
        "joint": ols(sample, "dlemp", ["E_np", "feas_frac"], C),
        "joint_weighted": ols(sample, "dlemp", ["E_np", "feas_frac"], C, weight="emp21_w"),
        "joint_trend_control": ols(s_pre, "dlemp", ["E_np", "feas_frac"], C + ["dlemp_pre"]),
        "placebo_2016_21": ols(s_pre, "dlemp_pre", ["E_np", "feas_frac"], C),
        "cv": drop_reps(cv_r2(sample.dropna(subset=["feas_frac"]), "dlemp",
                              {"E": ["E"], "E_np": ["E_np"], "E_np+feas_frac": ["E_np", "feas_frac"]}, C))}
    dec["extra"] = {"automate_or_augment_review_08": ols(sample, "dlemp", ["AU_rho08"], C),
                    "automate_or_augment_review_08_joint": ols(sample, "dlemp", ["E", "AU_rho08"], C),
                    "feasibility_and_model": ols(sample, "dlemp", ["M_feas", "M"], C),
                    "E_np_and_feasible": ols(sample, "dlemp", ["E_np", "M_feas"], C),
                    "all_three": ols(sample, "dlemp", ["E", "M_feas", "M"], C),
                    "save_share": ols(sample, "dlemp", ["M_save"], C),
                    "save_share_joint": ols(sample, "dlemp", ["E", "M_save"], C)}
    R["occ"]["decomposition"] = dec
    R["occ"]["corr_dlemp_post_pre"] = float(s_pre[["dlemp", "dlemp_pre"]].corr().iloc[0, 1])

    # robustness table rows (dependent variable: dlemp). Each row: exposure alone, the automation share alone, the
    # capability-feasible share alone, and the capability-feasible share jointly with exposure.
    def quad(df, mkey="M", fkey="M_feas", ekey="E", ctrl=C, y="dlemp", weight=None, fe="major", cluster=None,
             show_f=True, show_e=True):
        out = {"key": mkey, "fkey": fkey, "ekey": ekey,
               "M": ols(df, y, [mkey], ctrl, fe=fe, weight=weight, cluster=cluster)}
        out["E"] = ols(df, y, [ekey], ctrl, fe=fe, weight=weight, cluster=cluster) if show_e else None
        out["F"] = ols(df, y, [fkey], ctrl, fe=fe, weight=weight, cluster=cluster) if show_f else None
        out["FJ"] = ols(df, y, [ekey, fkey], ctrl, fe=fe, weight=weight, cluster=cluster) if show_f else None
        out["MJ"] = ols(df, y, [ekey, mkey], ctrl, fe=fe, weight=weight, cluster=cluster)
        return out

    tech = sample.soc.str.startswith(TECH_SOC_PREFIX) | sample.soc.isin(TECH_SOC_EXTRA)
    rate = sample.soc.isin(RATE_SENSITIVE)
    covid = sample.major.isin(COVID_GROUPS)
    rr = []
    rr.append({"header": True, "label": "Baseline and controls"})
    rr.append({"label": "Baseline", **quad(sample)})
    rr.append({"label": "Employment-weighted", **quad(sample, weight="emp21_w")})
    rr.append({"label": "Clustered by SOC minor group", **quad(sample, cluster="minor")})
    rr.append({"label": "Without controls or group effects", **quad(sample, ctrl=[], fe=None)})
    rr.append({"label": "Trend sample, baseline controls", **quad(s_pre)})
    rr.append({"label": "Trend sample, plus 2016--21 change", **quad(s_pre, ctrl=C + ["dlemp_pre"])})
    s_proj = sample.dropna(subset=["bls_proj"])
    rr.append({"label": "Plus BLS 2020--30 projected growth", **quad(s_proj, ctrl=C + ["bls_proj"])})
    s1921 = sample.dropna(subset=["dlemp_1921", "dlemp_1920"])
    rr.append({"label": "2019 sample, baseline controls", **quad(s1921)})
    rr.append({"label": "2019 sample, plus 2019--21 change", **quad(s1921, ctrl=C + ["dlemp_1921"])})
    rr.append({"label": "2019 sample, plus 2019--20 COVID shock", **quad(s1921, ctrl=C + ["dlemp_1920"])})
    s1619c = sample.dropna(subset=["dlemp_pre1619"])
    rr.append({"label": "2016--19 sample, baseline controls", **quad(s1619c)})
    rr.append({"label": "2016--19 sample, plus 2016--19 change", **quad(s1619c, ctrl=C + ["dlemp_pre1619"])})
    rr.append({"header": True, "label": "Confounders: occupations excluded"})
    rr.append({"label": "Computer occupations", **quad(sample[~tech])})
    rr.append({"label": "Credit and real-estate occupations", **quad(sample[~rate])})
    rr.append({"label": "COVID-rebound groups", **quad(sample[~covid])})
    rr.append({"label": "All three", **quad(sample[~(tech | rate | covid)])})
    rr.append({"header": True, "label": "Model variants (scores replaced)"})
    for nm, lab, fk in [("M_end", "Share in May 2025 only", None),
                        ("M_td207", "Capability doubling 207 days", "F_td207"),
                        ("M_th10", "Capability path: METR TH1.0 trend", "F_th10"),
                        ("M_aei_hours", "Task length from AEI times", "F_aei_hours"),
                        ("M_price10", "Inference price $\\times 10$", None),
                        ("M_no_outsourcing", "No outsourcing option", None),
                        ("M_iota02", "Data readiness 0.2", None), ("M_iota08", "Data readiness 0.8", None),
                        ("M_rho037", "Review time ratio 0.37", None), ("M_rho08", "Review time ratio 0.8", None),
                        ("M_rho119", "Review time ratio 1.19", None)]:
        rr.append({"label": lab, **quad(sample, mkey=nm, fkey=fk or "M_feas", show_f=fk is not None, show_e=False)})
    rr.append({"label": "Human-rated exposure labels",
               **quad(sample, mkey="M_human_beta", fkey="F_human_beta", ekey="E_h")})
    rr.append({"header": True, "label": "Placebos: change from 2016 to 2021"})
    rr.append({"label": "Log employment", **quad(s_pre, y="dlemp_pre")})
    s_pre_w = s_pre.copy()
    lo, hi = s_pre_w.dlemp_pre.quantile([0.01, 0.99])
    s_pre_w["dlemp_pre"] = s_pre_w.dlemp_pre.clip(lo, hi)
    rr.append({"label": "Log employment, winsorized 1/99", **quad(s_pre_w, y="dlemp_pre")})
    rr.append({"label": "Log employment, split codes included",
               **quad(sample.dropna(subset=["dlemp_pre_alloc"]), y="dlemp_pre_alloc")})
    rr.append({"label": "Log employment, identity rule (superseded)",
               **quad(sample.dropna(subset=["dlemp_pre_identity"]), y="dlemp_pre_identity")})
    rr.append({"label": "Log mean wage", **quad(s_pre, y="dlwage_pre")})
    rr.append({"header": True, "label": "Placebos: change from 2016 to 2019 (before COVID)"})
    s1619 = sample.dropna(subset=["dlemp_pre1619"])
    rr.append({"label": "Log employment, 2016--19", **quad(s1619, y="dlemp_pre1619")})
    rr.append({"label": "Log mean wage, 2016--19", **quad(s1619.dropna(subset=["dlwage_pre1619"]), y="dlwage_pre1619")})
    R["occ"]["robust_table_rows"] = rr
    R["occ"]["placebo_wage"] = {"post_same_sample": quad(s_pre, y="dlwage"), "pre": quad(s_pre, y="dlwage_pre")}
    R["occ"]["exclusion_sets"] = {"tech_prefix": list(TECH_SOC_PREFIX), "tech_extra": sorted(TECH_SOC_EXTRA),
                                  "rate_sensitive": sorted(RATE_SENSITIVE), "covid_groups": sorted(COVID_GROUPS),
                                  "n_tech": int(tech.sum()), "n_rate": int(rate.sum()), "n_covid": int(covid.sum())}
    # effect sizes in natural units
    b = main_res["dlemp"]["model"]["coef"]["M"]
    R["occ"]["effect_sizes"] = {
        "dlemp_model_alone_per_sd": b["b"], "sd_M": b["sd_x"],
        "dlemp_per_10pp_model_share": b["b_per_unit"] * 0.10,
        "iqr_M": float(sample.M.quantile(.75) - sample.M.quantile(.25)),
        "dlemp_p75_minus_p25": float(b["b_per_unit"] * (sample.M.quantile(.75) - sample.M.quantile(.25))),
        "dlemp_exposure_alone_per_sd": main_res["dlemp"]["exposure"]["coef"]["E"]["b"]}

    # ---- sweep over the review-time ratio rho_rev across its sourced range ------------------------------------
    # The headline flips inside the sourced range (params.yaml ai_cost.review_time_ratio_rho_rev), so the main
    # specification is re-estimated on a 0.01 grid over the range, plus the 9 evenly spaced points shown in the table.
    Pp = yaml.safe_load(open(TASKS / "params.yaml"))
    rr_lo, rr_hi = [float(x) for x in Pp["ai_cost"]["review_time_ratio_rho_rev"]["range"]]
    show = [round(float(x), 4) for x in np.linspace(rr_lo, rr_hi, 9)]
    fine = [round(float(x), 4) for x in np.arange(rr_lo, rr_hi + 1e-9, 0.01)]
    rho_grid = sorted(set(fine) | set(show) | {round(par["rho_rev"], 4), RHO_PRE_AUDIT, rr_hi})
    path = []
    for rho in rho_grid:
        agg_r, inf_r = model_scores(rows, wage_h, par, {**scenario(par, "main"), "rho_rev": rho})
        sample["M_sw"] = sample.soc.map(agg_r["M"])
        pt = {"rho": rho, "mean_M": float(sample.M_sw.mean()),
              "share_A": inf_r["may2025_feasible_permitted"]["share_A"],
              "share_U": inf_r["may2025_feasible_permitted"]["share_U"],
              "share_O": inf_r["may2025_feasible_permitted"]["share_O"]}
        if sample.M_sw.std() > 0:
            a = ols(sample, "dlemp", ["M_sw"], C)["coef"]["M_sw"]
            jr = ols(sample, "dlemp", ["E", "M_sw"], C)["coef"]
            cv = cv_r2(sample, "dlemp", {"E": ["E"], "M": ["M_sw"], "EM": ["E", "M_sw"]}, C)
            pt.update({"b_alone": a["b"], "se_alone": a["se"], "t_alone": a["t"], "p_alone": a["p"],
                       "b_joint": jr["M_sw"]["b"], "se_joint": jr["M_sw"]["se"], "t_joint": jr["M_sw"]["t"],
                       "bE_joint": jr["E"]["b"], "seE_joint": jr["E"]["se"],
                       "cv_E": cv["E"]["mean"], "cv_M": cv["M"]["mean"], "cv_EM": cv["EM"]["mean"],
                       "reps_M_beats_E": float(np.mean(np.array(cv["M_reps"]) > np.array(cv["E_reps"]))),
                       "reps_EM_beats_E": float(np.mean(np.array(cv["EM_reps"]) > np.array(cv["E_reps"])))})
        path.append(pt)
    sample = sample.drop(columns="M_sw")

    def crossing(key, level, sign=+1):
        """First rho at which key crosses `level` upward (sign=+1), by linear interpolation between grid points;
        also whether the path stays across the level afterwards."""
        pts = [q for q in path if key in q]
        xs = [q["rho"] for q in pts]
        ys = [sign * q[key] for q in pts]
        lev = sign * level
        if ys and ys[0] > lev:
            return {"rho": None, "status": "already above at the low end of the range", "stays": None}
        for i in range(1, len(ys)):
            if ys[i] > lev:
                x0, x1, y0, y1 = xs[i - 1], xs[i], ys[i - 1], ys[i]
                xr = x0 + (lev - y0) * (x1 - x0) / (y1 - y0)
                return {"rho": float(xr), "status": "crosses", "stays": bool(all(y > lev for y in ys[i:]))}
        return {"rho": None, "status": "never crosses within the range", "stays": None}

    for q in path:
        if "cv_M" in q:
            q["cv_gap_M"] = q["cv_E"] - q["cv_M"]
            q["cv_gap_EM"] = q["cv_E"] - q["cv_EM"]
    thr = {"alone_loses_5pct": crossing("t_alone", -1.96),
           "joint_loses_5pct": crossing("t_joint", -1.96),
           "alone_stops_beating_exposure_oos": crossing("cv_gap_M", 0.0),
           "joint_stops_beating_exposure_oos": crossing("cv_gap_EM", 0.0),
           "automation_wins_under_half_of_feasible_time": crossing("share_A", 0.5, sign=-1)}
    R["occ"]["rho_sweep"] = {"range": [rr_lo, rr_hi], "grid_step": 0.01, "table_points": show,
                             "pre_audit_value": RHO_PRE_AUDIT, "current_value": par["rho_rev"],
                             "path": path, "thresholds": thr,
                             "note": "main specification (Table backtest-occ, panel A) re-estimated at each rho_rev; "
                                     "thresholds interpolate linearly between grid points"}

    # ---- occupation x industry cells, May 2021 to May 2025 ----------------------------------------------------
    tau = par["tau_L_hour"]
    c21 = load_oews_cells(F_OEWS21_IND, 2021)
    c25 = load_oews_cells(F_OEWS25_IND, 2025)
    inds = sorted(set(c21.ind) & set(c25.ind))
    cells = c21[c21.ind.isin(inds)].rename(columns={"emp": "emp21", "a_mean": "a_mean21", "h_mean": "h_mean21"}).merge(
        c25[["ind", "soc", "emp", "a_mean"]].rename(columns={"emp": "emp25", "a_mean": "a_mean25"}),
        on=["ind", "soc"], how="left")
    occ_s = sample.set_index("soc")
    in_sample = cells.soc.isin(occ_s.index)
    big = in_sample & (cells.emp21 >= MIN_CELL_EMP)
    cstats = {"industries_2021": int(c21.ind.nunique()), "industries_2025": int(c25.ind.nunique()),
              "industries_common": len(inds), "only_2021": sorted(set(c21.ind) - set(c25.ind)),
              "only_2025": sorted(set(c25.ind) - set(c21.ind)),
              "cells_2021_in_occ_sample": int(in_sample.sum()), "cells_at_or_above_min": int(big.sum()),
              "cells_missing_in_2025": int((big & cells.emp25.isna()).sum()), "min_cell_emp_2021": MIN_CELL_EMP}
    cells = cells[big & cells.emp25.notna() & cells.h_mean21.notna() & cells.a_mean25.notna()].copy()
    cells["dlemp"] = np.log(cells.emp25 / cells.emp21)
    cells["dlwage"] = np.log(cells.a_mean25 / cells.a_mean21)
    cells["ln_wc"] = np.log(cells.a_mean21)
    cells["major"] = cells.soc.str[:2]
    for c in ["E", "E_np", "M_feas", "M", "phys_share", "job_zone"]:
        cells[c] = cells.soc.map(occ_s[c])
    cells["emp21_w"] = cells.emp21
    thr_main = model_thresholds(rows, par, scenario(par, "main"))
    chk = cell_scores(rows, thr_main, sample.soc.values, sample.h_mean21.values, tau)
    cstats["check_max_abs_dev_vs_model_scores"] = float(np.nanmax(np.abs(chk - sample.M.values)))
    assert cstats["check_max_abs_dev_vs_model_scores"] < 1e-9, "threshold form disagrees with model_scores"
    cstats["upper_bound_cases"] = thr_main["n_upper_bound_cases"]
    cells["Mc"] = cell_scores(rows, thr_main, cells.soc.values, cells.h_mean21.values, tau)
    cells["Mc_p10"] = cell_scores(rows, model_thresholds(rows, par, scenario(par, "price10")), cells.soc.values,
                                  cells.h_mean21.values, tau)
    dev = cells.Mc - cells.groupby("soc").Mc.transform("mean")
    cstats.update({"n_cells": int(len(cells)), "n_occupations": int(cells.soc.nunique()), "n_industries": int(cells.ind.nunique()),
                   "emp21_share_of_national": float(cells.emp21.sum() / occ.emp21.sum()),
                   "sd_Mc": float(cells.Mc.std(ddof=0)), "sd_Mc_within_occupation": float(dev.std(ddof=0)),
                   "share_var_within": float(dev.var(ddof=0) / cells.Mc.var(ddof=0)),
                   "sd_Mc_p10_within_occupation": float((cells.Mc_p10 - cells.groupby("soc").Mc_p10.transform("mean")).std(ddof=0)),
                   "share_cells_Mc_differs_from_national": float(np.mean(np.abs(cells.Mc - cells.M) > 1e-12))})
    ncell = cells.groupby("soc").size().sort_values(ascending=False, kind="mergesort")
    mg = (ncell / ncell.sum()).groupby(ncell.index.str[:2]).sum().sort_values(ascending=False, kind="mergesort")
    cstats.update({"top50_share_of_cells": float(ncell.head(50).sum() / ncell.sum()),
                   "largest_major_group": str(mg.index[0]), "largest_major_group_share": float(mg.iloc[0]),
                   "max_cells_per_occupation": int(ncell.iloc[0]), "median_cells_per_occupation": float(ncell.median())})
    CC = ["phys_share", "job_zone", "ln_wc"]
    FEc, CL = ["major", "ind"], ["soc", "ind"]
    cres = {"E": ols(cells, "dlemp", ["E"], CC, fe=FEc, cluster=CL),
            "Mc": ols(cells, "dlemp", ["Mc"], CC, fe=FEc, cluster=CL),
            "E_Mc": ols(cells, "dlemp", ["E", "Mc"], CC, fe=FEc, cluster=CL),
            "Feas": ols(cells, "dlemp", ["M_feas"], CC, fe=FEc, cluster=CL),
            "E_Feas": ols(cells, "dlemp", ["E", "M_feas"], CC, fe=FEc, cluster=CL),
            "within": ols_within(cells, "dlemp", ["Mc"], ["ln_wc"], ["soc", "ind"], cluster=CL),
            "E_Mc_w": ols(cells, "dlemp", ["E", "Mc"], CC, fe=FEc, cluster=CL, weight="emp21_w"),
            "within_w": ols_within(cells, "dlemp", ["Mc"], ["ln_wc"], ["soc", "ind"], cluster=CL, weight="emp21_w"),
            "within_p10": ols_within(cells, "dlemp", ["Mc_p10"], ["ln_wc"], ["soc", "ind"], cluster=CL),
            "wage_E_Mc": ols(cells, "dlwage", ["E", "Mc"], CC, fe=FEc, cluster=CL),
            "E_Mc_oneway_soc": ols(cells, "dlemp", ["E", "Mc"], CC, fe=FEc, cluster="soc")}
    cells["w_occ_equal"] = 1.0 / cells.groupby("soc").soc.transform("size")
    for nm, xs_ in [("E", ["E"]), ("Mc", ["Mc"]), ("E_Mc", ["E", "Mc"]), ("Feas", ["M_feas"]), ("E_Feas", ["E", "M_feas"])]:
        cres[nm + "_noind"] = ols(cells, "dlemp", xs_, CC, fe="major", cluster=CL)
        cres[nm + "_eqw"] = ols(cells, "dlemp", xs_, CC, fe=FEc, cluster=CL, weight="w_occ_equal")
        cres[nm + "_eqw_noind"] = ols(cells, "dlemp", xs_, CC, fe="major", cluster=CL, weight="w_occ_equal")
    # check the absorbed estimator against explicit dummies once
    dum = ols(cells, "dlemp", ["Mc"], ["ln_wc"], fe=["soc", "ind"], cluster=CL)
    cstats["within_check_coef_dummies_minus_absorbed"] = dum["coef"]["Mc"]["b"] - cres["within"]["coef"]["Mc"]["b"]
    assert abs(cstats["within_check_coef_dummies_minus_absorbed"]) < 1e-6
    ccv = cv_r2_grouped(cells, "dlemp", {"controls": [], "E": ["E"], "Mc": ["Mc"], "E+Mc": ["E", "Mc"],
                                         "Feas": ["M_feas"]}, CC, FEc, "soc", CELL_CV_REPS)
    reps = ccv.pop("reps_detail")
    ccv["share_reps_Mc_beats_E"] = float(np.mean(np.array(reps["Mc"]) > np.array(reps["E"])))
    ccv["share_reps_EMc_beats_E"] = float(np.mean(np.array(reps["E+Mc"]) > np.array(reps["E"])))
    ccv["share_reps_Feas_beats_E"] = float(np.mean(np.array(reps["Feas"]) > np.array(reps["E"])))
    # review-ratio sweep for the cell test
    cgrid = sorted(set(round(float(x), 4) for x in np.arange(rr_lo, rr_hi + 1e-9, CELL_GRID_STEP))
                   | set(show) | {round(par["rho_rev"], 4), RHO_PRE_AUDIT, rr_hi})
    cpath = []
    for rho in cgrid:
        thr = model_thresholds(rows, par, {**scenario(par, "main"), "rho_rev": rho})
        cells["Mc_sw"] = cell_scores(rows, thr, cells.soc.values, cells.h_mean21.values, tau)
        q = {"rho": rho, "mean_Mc": float(cells.Mc_sw.mean()),
             "sd_within": float((cells.Mc_sw - cells.groupby("soc").Mc_sw.transform("mean")).std(ddof=0))}
        if cells.Mc_sw.std() > 0:
            a1 = ols(cells, "dlemp", ["Mc_sw"], CC, fe=FEc, cluster=CL)["coef"]["Mc_sw"]
            j1 = ols(cells, "dlemp", ["E", "Mc_sw"], CC, fe=FEc, cluster=CL)["coef"]
            q.update({"b_alone": a1["b"], "se_alone": a1["se"], "t_alone": a1["t"],
                      "b_joint": j1["Mc_sw"]["b"], "se_joint": j1["Mc_sw"]["se"], "t_joint": j1["Mc_sw"]["t"],
                      "bE_joint": j1["E"]["b"], "seE_joint": j1["E"]["se"]})
            if q["sd_within"] > 1e-6:      # no within-occupation variation: the within regression is not estimable
                w1 = ols_within(cells, "dlemp", ["Mc_sw"], ["ln_wc"], ["soc", "ind"], cluster=CL)["coef"]["Mc_sw"]
                q.update({"b_within": w1["b"], "se_within": w1["se"], "t_within": w1["t"]})
        cpath.append(q)
    cells = cells.drop(columns="Mc_sw")
    cpts = [q for q in cpath if "t_alone" in q]

    def ccross(key, level=-1.96):
        xs_, ys_ = [q["rho"] for q in cpts], [q[key] for q in cpts]
        if ys_ and ys_[0] > level:
            return {"rho": None, "status": "not significant at the low end of the range"}
        for i in range(1, len(ys_)):
            if ys_[i] > level:
                x0, x1, y0, y1 = xs_[i - 1], xs_[i], ys_[i - 1], ys_[i]
                return {"rho": float(x0 + (level - y0) * (x1 - x0) / (y1 - y0)), "status": "crosses",
                        "stays": bool(all(y > level for y in ys_[i:]))}
        return {"rho": None, "status": "significant across the whole range"}

    cthr = {"alone_loses_5pct": ccross("t_alone"), "joint_loses_5pct": ccross("t_joint"),
            "within_significant_points": int(sum(abs(q["t_within"]) >= 1.96 for q in cpts if "t_within" in q)),
            "within_points": int(sum("t_within" in q for q in cpts)),
            "within_significant_signs": sorted({"positive" if q["b_within"] > 0 else "negative"
                                                for q in cpts if "t_within" in q and abs(q["t_within"]) >= 1.96})}
    for nm, key, sdw in [("within", "Mc", cstats["sd_Mc_within_occupation"]),
                         ("within_w", "Mc", cstats["sd_Mc_within_occupation"]),
                         ("within_p10", "Mc_p10", cstats["sd_Mc_p10_within_occupation"])]:
        c = cres[nm]["coef"][key]
        c["b_per_within_sd"] = c["b_per_unit"] * sdw
        c["se_per_within_sd"] = c["se"] / c["sd_x"] * sdw
    R["cells"] = {"stats": cstats, "regressions": cres, "cv": ccv,
                  "sweep": {"grid_step": CELL_GRID_STEP, "path": cpath, "thresholds": cthr},
                  "design": "Delta log employment of occupation x industry cells, May 2021 to May 2025. Industry "
                            "fixed effects (and SOC major groups) for the exposure and model scores; occupation and "
                            "industry fixed effects for the wage-driven model score, whose only within-occupation "
                            "variation is the cell's May 2021 wage in the cost crossover. Standard errors clustered "
                            "two-way by occupation and industry. Controls: physical task share, job zone and log cell "
                            "wage (the log cell wage alone within occupation).",
                  "harmonization": "NAICS 2017 to 2022 at four digits: common codes kept (renamed titles only); "
                                   "5111->5131 and 5112->5132; 5151, 5152 and 5191 combined with 5161, 5162 and 5192; "
                                   "retail trade at the sector level (44-45)."}

    # ---- firm level ------------------------------------------------------------------------------------------
    R["firm"] = firm_level(occ.dropna(subset=["M", "E"]))

    # ---- occupation x industry: not feasible -----------------------------------------------------------------
    R["occ_x_industry"] = {"feasible": True, "results": "see R['cells']",
                           "files": [str(F_OEWS21_IND.relative_to(ROOT)), str(F_OEWS25_IND.relative_to(ROOT))]}

    # ---- multiple testing: a fixed family of N_TESTS headline tests -----------------------------------------
    from scipy.stats import norm
    D = R["occ"]["decomposition"]
    rb = {row["label"]: row for row in rr if not row.get("header")}
    Fm = R["firm"]
    fam = [
        ("Exposure, log employment", D["E"]["alone"], "E"),
        ("Model share, log employment", D["M"]["alone"], "M"),
        ("Model share, with exposure", D["M"]["joint"], "M"),
        ("Exposure, with model share", D["M"]["joint"], "E"),
        ("Non-physical, permissible exposure", D["E_np"]["alone"], "E_np"),
        ("Capability-feasible share", D["M_feas"]["alone"], "M_feas"),
        ("Capability-feasible share, with exposure", D["M_feas"]["joint"], "M_feas"),
        ("Automate-or-augment share", D["M_AU"]["alone"], "M_AU"),
        ("Capability timing, given non-physical exposure", D["timing"]["joint"], "feas_frac"),
        ("Model share, employment-weighted", D["M"]["weighted"], "M"),
        ("Model share, three confounder groups excluded", rb["All three"]["M"], "M"),
        ("Model share, 2016--21 trend control", D["M"]["pretrend_control"], "M"),
        ("Model share, review ratio 0.8", D["M_rho08"]["alone"], "M_rho08"),
        ("Exposure, log wage-bill share", R["occ"]["main"]["dlwbs"]["exposure"], "E"),
        ("Model share, log wage-bill share", R["occ"]["main"]["dlwbs"]["model"], "M"),
        ("Model share with exposure, log mean wage", R["occ"]["main"]["dlwage"]["both"], "M"),
        ("Placebo 2016--21: exposure", D["E"]["placebo_2016_21"], "E"),
        ("Placebo 2016--21: model share", D["M"]["placebo_2016_21"], "M"),
        ("Firms: model mix, total cost share", Fm["regressions"]["total"]["model"], "mix_M"),
        ("Firms: exposure mix, total cost share", Fm["regressions"]["total"]["exposure"], "mix_E"),
        ("Cells: exposure, industry effects", R["cells"]["regressions"]["E"], "E"),
        ("Cells: model share, industry effects", R["cells"]["regressions"]["Mc"], "Mc"),
        ("Cells: model share with exposure, industry effects", R["cells"]["regressions"]["E_Mc"], "Mc"),
        ("Cells: model share within occupation (wage-driven)", R["cells"]["regressions"]["within"], "Mc"),
        ("Placebo 2016--19: exposure", rb["Log employment, 2016--19"]["E"], "E"),
        ("Placebo 2016--19: model share", rb["Log employment, 2016--19"]["M"], "M"),
        ("Model share, 2019--21 trend control", rb["2019 sample, plus 2019--21 change"]["M"], "M"),
        ("Model share, 2016--19 trend control", rb["2016--19 sample, plus 2016--19 change"]["M"], "M"),
    ]
    assert len(fam) == N_TESTS
    crit_t = float(norm.ppf(1 - 0.05 / (2 * N_TESTS)))
    fam_out = []
    for lab, reg, key in fam:
        c = reg["coef"][key]
        fam_out.append({"label": lab, "b": c.get("b_per_within_sd", c["b"]), "se": c.get("se_per_within_sd", c["se"]),
                        "t": c["t"], "p": c["p"],
                        "p_bonferroni": min(1.0, N_TESTS * c["p"]), "survives": N_TESTS * c["p"] < 0.05})
    order = np.argsort([f["p"] for f in fam_out])
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (N_TESTS - rank) * fam_out[i]["p"]))
        fam_out[i]["p_holm"] = running
        fam_out[i]["survives_holm"] = running < 0.05
    for f in fam_out:
        f["survives_previous_family_size"] = N_TESTS_PREVIOUS * f["p"] < 0.05
    R["multiple_testing"] = {"family_size": N_TESTS, "previous_family_size": N_TESTS_PREVIOUS,
                             "method": "Bonferroni at 5% two-sided (Holm reported too)",
                             "critical_abs_t_normal": crit_t,
                             "critical_abs_t_previous": float(norm.ppf(1 - 0.05 / (2 * N_TESTS_PREVIOUS))),
                             "tests": fam_out}

    # ---- write ----------------------------------------------------------------------------------------------
    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            return None if not np.isfinite(o) else round(float(o), 6)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.bool_,)):
            return bool(o)
        return o

    OUT_JSON.write_text(json.dumps(clean(R), indent=1))
    TAB.mkdir(parents=True, exist_ok=True)
    (TAB / "backtest_occ.tex").write_text(table_occ(R))
    (TAB / "backtest_robust.tex").write_text(table_robust(R))
    (TAB / "backtest_firm.tex").write_text(table_firm(R))
    (TAB / "backtest_decomp.tex").write_text(table_decomp(R))
    (TAB / "backtest_sweep.tex").write_text(table_sweep(R))
    (TAB / "backtest_tests.tex").write_text(table_tests(R))
    (TAB / "backtest_cells.tex").write_text(table_cells(R))
    macros = text_macros(R, INFO, rr)
    R["macros"] = macros
    OUT_JSON.write_text(json.dumps(clean(R), indent=1))
    (TAB / "backtest_macros.tex").write_text(
        "% Generated by code/validation/backtest.py; do not edit. Every number quoted in part2/validation_backtest.tex.\n"
        + "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in macros.items()))

    # ---- stdout summary --------------------------------------------------------------------------------------
    m = main_res["dlemp"]
    print("sample", R["occ"]["sample"])
    print("H end-2021 (h)", INFO["main"]["H_end2021_hours"], "H May 2025 (h)", INFO["main"]["H_may2025_hours"])
    print("static share rows A-optimal end-2021:", INFO["main"]["share_rows_Aopt_end2021"])
    for y in ["dlemp", "dlwbs", "dlwage"]:
        mm = main_res[y]
        print(y, "E alone", round(mm["exposure"]["coef"]["E"]["b"], 4), round(mm["exposure"]["coef"]["E"]["se"], 4),
              "| M alone", round(mm["model"]["coef"]["M"]["b"], 4), round(mm["model"]["coef"]["M"]["se"], 4),
              "| both E", round(mm["both"]["coef"]["E"]["b"], 4), round(mm["both"]["coef"]["E"]["se"], 4),
              "M", round(mm["both"]["coef"]["M"]["b"], 4), round(mm["both"]["coef"]["M"]["se"], 4),
              "| dR2", round(mm["delta_r2_model_given_exposure"], 4),
              "| CV", {k: round(v["mean"], 4) for k, v in R["occ"]["cv"][y].items() if isinstance(v, dict) and "mean" in v})
    def fmt(reg, key):
        if reg is None:
            return " " * 17
        c = reg["coef"][key]
        return f"{c['b']:+.4f} ({c['se']:.4f})"
    for row in rr:
        if row.get("header"):
            print("--", row["label"]); continue
        print(f"{row['label'][:40]:40s} E {fmt(row['E'], row['ekey'])} M {fmt(row['M'], row['key'])} "
              f"F {fmt(row['F'], row['fkey'])} FJ {fmt(row['FJ'], row['fkey'])} MJ {fmt(row['MJ'], row['key'])} n={row['M']['n']}")
    for k in ["E", "E_np", "M_feas", "M_AU", "M", "M_rho08"]:
        dd = R["occ"]["decomposition"][k]
        a = dd["alone"]["coef"][k]; pl = dd["placebo_2016_21"]["coef"][k]
        j = dd["joint"]["coef"] if dd["joint"] else None
        print(f"decomp {k:7s} alone {a['b']:+.4f} ({a['se']:.4f})", "" if j is None else
              f"joint {j[k]['b']:+.4f} ({j[k]['se']:.4f}) E {j['E']['b']:+.4f} ({j['E']['se']:.4f})",
              f"placebo {pl['b']:+.4f} ({pl['se']:.4f})", "cv", round(R["occ"]["decomposition"]["cv"][k]["mean"], 4))
    tj = R["occ"]["decomposition"]["timing"]
    print("timing", {k: (round(v["b"], 4), round(v["se"], 4)) for k, v in tj["joint"]["coef"].items()},
          "placebo", {k: (round(v["b"], 4), round(v["se"], 4)) for k, v in tj["placebo_2016_21"]["coef"].items()},
          "weighted", {k: (round(v["b"], 4), round(v["se"], 4)) for k, v in tj["joint_weighted"]["coef"].items()},
          "cv", {k: round(v["mean"], 4) for k, v in tj["cv"].items() if isinstance(v, dict) and "mean" in v})
    print("cv", {k: (round(v["mean"], 4) if isinstance(v, dict) else v) for k, v in R["occ"]["decomposition"]["cv"].items() if k != "sets"})
    F = R["firm"]
    print("firm sample", F["sample"]["main_n"], F["sample"]["placebo_n"])
    for bb in BUCKETS + ["total"]:
        c = F["regressions"][bb]["model"]["coef"]["mix_M"]
        cp = F["placebo"][bb]["model"]["coef"]["mix_M"]
        ce = F["regressions"][bb]["exposure"]["coef"]["mix_E"]
        print(f"firm {bb:6s} model {c['b']:+.3f} ({c['se']:.3f})  exposure {ce['b']:+.3f} ({ce['se']:.3f})  "
              f"placebo {cp['b']:+.3f} ({cp['se']:.3f})")
    print("wrote", OUT_JSON, "and tables in", TAB)


if __name__ == "__main__":
    main()
