"""Archetypes of the playbook (part2/theory_playbook.tex, Definition def:playbook-archetypes).

Positions come from the SEC core panel (SIC 7372) of Paper 1, fiscal years 2023-25: since 29 Oct 2026 the audited v3
core sample data/panel_v3.csv (notes/sample_audit.md Section 3), the sample Paper 1 now uses, with acquisition-affected
firm-years flagged by acq_flag_v3 (rule R4) in place of acq_flag. The v2 rebuild from data/panel_v2_all.csv (checked
against data/panel.csv) is kept as load_core_panel_v2 for the old-to-new comparison in engine/CHANGELOG.md.

Rules (stated once, applied to every archetype; nothing is tuned per archetype):
  * Quantile cut points are computed on the population: every 2023-25 core firm-year with a free-cash-flow margin
    after SBC (estimand E1, Paper 1 Section sec:data-estimands).
  * Members of each cell are the non-acquisition firm-years (acq_flag_v3 == 0; the cell definition of estimand E2),
    because the playbook is model-facing; Paper 1's descriptive baseline (D-3) is E1.
  * The near-frontier elite is Paper 1's calibration anchor: firm-years at or above the 95th percentile of the
    cash-basis score among all 2023-25 core firm-years, excluding acquisition-affected ones (code/calibrate_horizons.py).
  * Cells are disjoint: the elite takes precedence.
  * Positions and cost lines are cell medians.

Part I state of each archetype (sections/model.tex), with the conventions of Paper 1:
  sigma  = growth spend. Central basis since the author's decision of 2 Nov 2026 (Paper 1 round 2, decisions 4 and 7):
           maintenance-netted, sigma = max(S&M share - b_M, 0), with b_M Paper 1's maintenance base (median lagged S&M
           share of firm-years growing at or below market, E1; notes/empirics_v3.json spend_maint_base, 25.1%); the
           maintenance share min(S&M, b_M) is a non-discretionary cost line. Bounds: all S&M (the convention before
           2 Nov) and no S&M (sigma = 0);
  k      = capital intensity: capex and capitalized software over revenue, divided by growth (anchor convention
           k = kg/g for g > 0, k = 0 otherwise);
  alpha (X_hat - k) = r_sigma, Paper 1's median ratio of growth spend to excess growth on the same basis (netted:
           spend_maint_ratio, 0.94 since 3 Nov 2026; all S&M: SPEND_RATIO 3.3; class c; Section sec:empirics), common to all firms as in
           Assumption ass:hetero (one weight X across firms);
  Delta  = sigma / r_sigma (Proposition prop:score(b): sigma* = alpha (X - k) Delta*), firm-specific zero-spend
           growth G_i = g - Delta (Remark rem:assumptions(b)), opportunity ell = Delta / sigma^alpha (eq. growth);
  m0     = m + sigma + k g (eq. fcf, pre-tax).
Under this calibration the engine's sigma* at (ell, X_hat) equals the observed S&M share: the firm is at its own
tangency (checked in code/verify_part2_playbook.py).
"""
from __future__ import annotations

import json
import math
import os
import sys
from dataclasses import dataclass, asdict, field

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "code"))
from exclusions import is_excluded  # noqa: E402  registrants excluded at the author's request
SPEND_RATIO = 3.3          # Paper 1, Section sec:empirics: median prior-year S&M share / excess growth (class c): all-S&M bound
PERIOD = "2023-25"
# Maintenance-netted basis, central (author decision of 2 Nov 2026): Paper 1's maintenance base and netted spend ratio
_E3 = json.load(open(os.path.join(ROOT, "notes", "empirics_v3.json")))["estimates"]
MAINT_BASE = float(_E3["spend_maint_base"]["E1"]["est"])            # Paper 1 macro MaintBase (25.7 since the re-estimation of 3 Nov 2026)
SPEND_RATIO_NET = float(_E3["spend_maint_ratio"]["E1"]["est"])      # median (S&M - b_M)/(g - G), E1; Paper 1 macro AlphaNet (0.94 since 3 Nov 2026)
BASIS = "netted"
BASES = ("netted", "all", "none")


def growth_spend(sm: float, basis: str = BASIS) -> tuple[float, float]:
    """(sigma, maintenance S&M) on a basis: netted max(S&M - b_M, 0) and min(S&M, b_M); all S&M and 0; none 0 and S&M."""
    sm = float(sm)
    if basis == "netted":
        return max(sm - MAINT_BASE, 0.0), min(sm, MAINT_BASE)
    if basis == "all":
        return sm, 0.0
    if basis == "none":
        return 0.0, sm
    raise ValueError(f"unknown S&M basis {basis}")


def spend_ratio(basis: str = BASIS) -> float:
    return SPEND_RATIO_NET if basis == "netted" else SPEND_RATIO

# Archetype codes, names and cell rules, in the order of the playbook table.
ARCHETYPES = [
    ("A1", "Growth corner", "high growth, low margin: g at or above the 75th percentile, m below the 25th"),
    ("A2", "Balanced upper quartile", "score between the 75th and 95th percentiles, g and m both at or above the median"),
    ("A3", "Mature cash generator", "g below the median, m at or above the 75th percentile"),
    ("A4", "Sub-40 grower", "g between the median and the 75th percentile, m below the median"),
    ("A5", "Stalled", "g and m both below the median"),
    ("A6", "Near-frontier elite", "score at or above the 95th percentile (Paper 1's calibration anchor)"),
    ("A7", "Acquisition-driven compounder", "a serial acquirer: Bending Spoons, reported against organic growth"),
]


PANEL_SOURCE = "data/panel_v3.csv (audited v3 core sample; acquisition flag acq_flag_v3)"


def load_core_panel() -> pd.DataFrame:
    """The audited v3 core sample of Paper 1 (data/panel_v3.csv: the v2 core rules, SIC 7372, fiscal 2010-25, prior
    revenue >= $100M, growth in (-0.9, 5), margins outside [-3, 1] missing, less the firm-years the sample audit
    excludes). acq_flag is replaced by acq_flag_v3 (rule R4), so every cell rule below reads the audited flag."""
    core = pd.read_csv(os.path.join(ROOT, "data", "panel_v3.csv"))
    assert (core.sic == 7372).all() and core.year.between(2010, 2025).all(), "panel_v3.csv is not the core sample"
    for mm in ["m_op", "m_adj", "m_fcf", "m_fcf_sbc", "m_fcf_sbc_lease"]:
        bad = (core[mm] < -3) | (core[mm] > 1)
        assert not bad.any(), f"{mm} outside [-3, 1] in panel_v3.csv"
    core = core.copy()
    core["acq_flag_v2"] = core["acq_flag"]
    core["acq_flag"] = core["acq_flag_v3"].astype(int)
    return core


def load_core_panel_v2() -> pd.DataFrame:
    """The v2 core sample (before the sample audit), rebuilt from panel_v2_all.csv with the rules of
    code/build_panel_v2.py and checked against data/panel.csv; kept for the old-to-new comparison only."""
    a = pd.read_csv(os.path.join(ROOT, "data", "panel_v2_all.csv"))
    a = a[~a.cik.map(is_excluded)]                 # registrants excluded at the author's request (code/exclusions.py)
    x = a[a.year.between(2010, 2025) & a.g.notna() & (a.rev_lag >= 100e6) & (a.g > -0.9) & (a.g < 5)].copy()
    for mm in ["m_op", "m_adj", "m_fcf", "m_fcf_sbc", "m_fcf_sbc_lease"]:
        x.loc[(x[mm] < -3) | (x[mm] > 1), mm] = np.nan
        x["R_" + mm[2:]] = x.g + x[mm]
    x = x[x.m_op.notna() | x.m_fcf.notna()]
    core = x[x.sic == 7372].copy()
    ref = pd.read_csv(os.path.join(ROOT, "data", "panel.csv"))
    assert len(core) == len(ref) and set(core.accn) == set(ref.accn), "core panel does not match data/panel.csv"
    return core


@dataclass
class Archetype:
    code: str
    name: str
    rule: str
    n: int = 0
    n_firms: int = 0
    g: float = float("nan")              # cell medians
    m: float = float("nan")              # FCF margin after SBC
    R: float = float("nan")
    m_op: float = float("nan")
    sm: float = float("nan")             # shares of revenue
    ga: float = float("nan")
    rd: float = float("nan")
    gm: float = float("nan")
    capint: float = float("nan")
    revenue: float = float("nan")
    q_g: float = float("nan")            # population quantile rank of the cell's median g, m and R
    q_m: float = float("nan")
    q_R: float = float("nan")
    band_gap: dict = field(default_factory=dict)   # line gaps to the top decile of its growth band (Paper 1 tab:gap)
    source: str = "panel"
    extra: dict = field(default_factory=dict)

    def state(self, alpha: float, ratio: float | None = None, basis: str = BASIS) -> dict:
        """Part I state (module docstring) on an S&M basis (central: netted). Returns sigma, a_GA, a_SM (maintenance
        S&M, a cost line), rd, gamma, k, Delta, G_i, ell, X_hat, m0. With no growth spend on the basis (sigma = 0) the
        firm has no demand pull to calibrate: Delta = 0, G_i = g and ell = 0, and the growth-engine levers are zero;
        X_hat = k + r_sigma/alpha still holds under the common-weight assumption (ass:playbook-calib)."""
        sigma, a_sm = growth_spend(self.sm, basis)
        ratio = spend_ratio(basis) if ratio is None else ratio
        k = float(self.capint / self.g) if self.g > 0 else 0.0
        Delta = sigma / ratio if sigma > 0 else 0.0
        G_i = float(self.g) - Delta
        ell = Delta / sigma ** alpha if sigma > 0 else 0.0
        X_hat = k + ratio / alpha
        m0 = float(self.m) + sigma + k * float(self.g)
        return {"sigma": sigma, "a_GA": float(self.ga), "a_SM": a_sm, "rd": float(self.rd), "gamma": float(self.gm), "k": k,
                "Delta": Delta, "G_i": G_i, "ell": ell, "X_hat": X_hat, "m0": m0, "g": float(self.g), "m": float(self.m),
                "alpha": alpha, "ratio": ratio, "sm": float(self.sm), "basis": basis, "maint_base": MAINT_BASE}


def sm_basis_check(archs, alpha: float) -> dict:
    """Paper 1 round 2, author decision 4: the central basis of growth spend is maintenance-netted, sigma = max(S&M share
    - b_M, 0), with b_M Paper 1's maintenance base (the median lagged S&M share of firm-years growing at or below market,
    E1; notes/empirics_v3.json spend_maint_base, Paper 1 macro MaintBase) and the netted spend ratio (spend_maint_ratio,
    0.99) in place of the all-S&M one; all S&M and no S&M are bounds. Since the author's decision of 2 Nov 2026 (decision 7)
    the playbook and Paper 1's Table tab:levers-position calibrate on the netted basis. This block gives, on each basis,
    whether the growth engine is ahead of general and administrative cost at the weight the position's own spending
    reveals. At that weight the ratio test of prop:playbook-rank(b) is
    (a_GA/sigma)^(1-alpha) < 1, i.e. sigma > a_GA, whatever the spend ratio (which sets only the level of X_hat). Under the
    netted basis the maintenance share of S&M, min(S&M, b_M), is a cost line like overhead: automating a share x of all
    S&M is then worth x sigma (growth part, first order) plus x min(S&M, b_M) (cost part), i.e. x S&M at the revealed
    weight, as on the all-S&M basis."""
    b_M, r_net = MAINT_BASE, SPEND_RATIO_NET
    r_all_v3 = float(_E3["spend_ratio"]["E1"]["est"])
    rows = {}
    for a in archs:
        if a.code == "A7":
            continue
        sm, ga = float(a.sm), float(a.ga)
        out = {"sm": sm, "ga": ga}
        for basis, sig in ((bs, growth_spend(sm, bs)[0]) for bs in ("all", "netted", "none")):
            ratio = (ga / sig) ** (1 - alpha) if sig > 0 else float("inf")
            out[basis] = {"sigma": sig, "ratio": ratio, "growth_engine_ahead_of_ga": bool(sig > ga)}
        out["maintenance_sm"] = min(sm, b_M)
        out["sm_automation_ahead_of_ga"] = bool(sm > ga)
        rows[a.code] = out
    count = lambda basis: sum(r[basis]["growth_engine_ahead_of_ga"] for r in rows.values())
    return {"b_M": b_M, "spend_ratio_netted": r_net, "spend_ratio_all_E1_v3": r_all_v3, "alpha": alpha,
            "spend_ratio_all_bound": SPEND_RATIO, "central_basis": BASIS, "positions": rows,
            "n_ahead": {b: count(b) for b in ("all", "netted", "none")},
            "n_sm_automation_ahead": sum(r["sm_automation_ahead_of_ga"] for r in rows.values()), "n": len(rows),
            "rule": "growth engine ahead of G&A at the revealed weight iff sigma > a_GA (prop:playbook-rank(b) at X_o = X_hat)"}


def _q_rank(series: pd.Series, value: float) -> float:
    s = series.dropna().values
    return float((s < value).mean() + 0.5 * (s == value).mean())


def band_gaps(core: pd.DataFrame, cell: pd.DataFrame) -> dict:
    """Gap of the cell's median cost lines to the top decile of GAAP operating margin in the cell's growth band,
    on the sample and bands of Paper 1's Table tab:gap (code/decompose_gap.py): positive values mean the top decile
    spends less (or earns more gross margin) by that many points of revenue."""
    gj = json.load(open(os.path.join(ROOT, "notes", "gap_decomposition.json")))
    edges = [0, 0.1, 0.2, 0.3, 0.4, 0.6]
    g = float(cell.g.median())
    b = int(np.clip(np.searchsorted(edges, g, side="right") - 1, 0, len(edges) - 2))
    band = [r for r in gj["bands"] if int(r["band"]) == b][0]
    med = {"gm": float((cell.gp / cell.rev).median()), "sms": float((cell.sm / cell.rev).median()),
           "rds": float((cell.rd / cell.rev).median()), "gas": float((cell.ga / cell.rev).median())}
    out = {"band": b, "band_label": f"{int(100 * edges[b])}-{int(100 * edges[b + 1])}", "g_clipped": g < 0 or g >= 0.6,
           "gm": band["top_gm"] - med["gm"], "sms": med["sms"] - band["top_sms"], "rds": med["rds"] - band["top_rds"],
           "gas": med["gas"] - band["top_gas"]}
    lines = {"gm": "gross margin (cost of revenue)", "sms": "selling and marketing (growth engine)",
             "rds": "research and development", "gas": "general and administrative (overhead)"}
    k = max(["gm", "sms", "rds", "gas"], key=lambda c: out[c])
    out["largest"] = k
    out["largest_label"] = lines[k]
    return out


def build_archetypes(core: pd.DataFrame | None = None) -> tuple[list[Archetype], dict]:
    core = load_core_panel() if core is None else core
    c = core[core.period == PERIOD].copy()
    c["R"] = c.g + c.m_fcf_sbc
    pop = c.dropna(subset=["m_fcf_sbc"])
    q = lambda s, p: float(s.quantile(p))
    cuts = {"g25": q(pop.g, .25), "g50": q(pop.g, .5), "g75": q(pop.g, .75), "m25": q(pop.m_fcf_sbc, .25),
            "m50": q(pop.m_fcf_sbc, .5), "m75": q(pop.m_fcf_sbc, .75), "R75": q(pop.R, .75),
            "R95": q(c.R, .95), "n_population": int(len(pop)), "n_E2": int((pop.acq_flag == 0).sum())}
    d = pop[pop.acq_flag == 0]
    el = d.R >= cuts["R95"]
    rules = {
        "A1": (d.g >= cuts["g75"]) & (d.m_fcf_sbc < cuts["m25"]) & ~el,
        "A2": (d.R >= cuts["R75"]) & (d.R < cuts["R95"]) & (d.g >= cuts["g50"]) & (d.m_fcf_sbc >= cuts["m50"]) & ~el,
        "A3": (d.g < cuts["g50"]) & (d.m_fcf_sbc >= cuts["m75"]) & ~el,
        "A4": (d.g >= cuts["g50"]) & (d.g < cuts["g75"]) & (d.m_fcf_sbc < cuts["m50"]) & ~el,
        "A5": (d.g < cuts["g50"]) & (d.m_fcf_sbc < cuts["m50"]) & ~el,
        "A6": el,
    }
    cuts["n_pass40_non_elite_balanced"] = int(((d.R >= 0.40) & ~el & (d.g >= cuts["g50"]) & (d.m_fcf_sbc >= cuts["m50"])).sum())
    out = []
    for code, name, rule in ARCHETYPES:
        a = Archetype(code, name, rule)
        if code in rules:
            s = d[rules[code]]
            a.n, a.n_firms = int(len(s)), int(s.cik.nunique())
            a.g, a.m, a.R, a.m_op = (float(s.g.median()), float(s.m_fcf_sbc.median()), float(s.R.median()),
                                     float(s.m_op.median()))
            a.sm, a.ga = float((s.sm / s.rev).median()), float((s.ga / s.rev).median())
            a.rd, a.gm = float((s.rd / s.rev).median()), float((s.gp / s.rev).median())
            a.capint, a.revenue = float(s.capex_int.median()), float(s.rev.median())
            a.q_g, a.q_m, a.q_R = _q_rank(pop.g, a.g), _q_rank(pop.m_fcf_sbc, a.m), _q_rank(pop.R, a.R)
            a.band_gap = band_gaps(core, s)
            a.extra["sm_missing"] = int(s.sm.isna().sum())
        else:
            a = compounder(a)
        out.append(a)
    return out, cuts


def compounder(a: Archetype) -> Archetype:
    """The acquisition-driven compounder, from notes/case_bending_spoons_f1_extract.md (Form F-1 of 8 June 2026 and the
    Q2 2026 6-K). Reported growth includes acquisitions; organic growth is the company's own Q2 2026 figure (3%). The
    cost lines are fiscal 2025 shares of revenue from the F-1 income statement. Not a panel position: SIC 7370, an
    acquisition-affected firm (estimand E1 only)."""
    rev24, rev25 = 671_053.0, 1_306_404.0
    cogs25, rd25, sm25, ga25, oi25 = 449_134.0, 120_737.0, 131_728.0, 326_953.0, 277_851.0
    ocf25, cfi25, int25 = 290_600.0, -1_851_874.0, 142_601.0
    a.source = "F-1 (8 Jun 2026) and 6-K (13 Aug 2026)"
    a.n, a.n_firms = 1, 1
    a.g = rev25 / rev24 - 1
    a.m_op = oi25 / rev25
    a.m = ocf25 / rev25 + cfi25 / rev25          # fully charged cash margin (Remark rem:acquired-bounds lower bound)
    a.R = a.g + a.m
    a.sm, a.ga, a.rd, a.gm = sm25 / rev25, ga25 / rev25, rd25 / rev25, 1 - cogs25 / rev25
    a.capint, a.revenue = float("nan"), rev25
    a.extra = {"g_reported_q2_2026": 704_155.0 / 311_100.0 - 1, "g_organic_q2_2026": 0.03,
               "m_op_q2_2026": 240_251.0 / 704_155.0, "nrr_2025": 0.95, "G_i_2025": math.log(0.95),
               "R_reported_q2_2026": 704_155.0 / 311_100.0 - 1 + 240_251.0 / 704_155.0,
               "R_organic_q2_2026": 0.03 + 240_251.0 / 704_155.0,
               "R_uncharged_cash_2025": a.g + ocf25 / rev25, "R_charged_2025": a.R, "interest_share_2025": int25 / rev25,
               "hurdle_unlevered": 0.25, "hurdle_levered": 0.65, "spooners": 621, "reorg_expense_share_2025": 78_607.0 / rev25,
               "acq_price_to_revenue": {"AOL": 2.30, "Eventbrite": 1.73, "Vimeo": 3.2}}
    return a


def archetype_table_rows(archs: list[Archetype]) -> list[dict]:
    return [asdict(a) for a in archs]
