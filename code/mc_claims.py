#!/usr/bin/env python3
"""Joint-parameter stress test of the headline claims of Paper 1 ("The Rule of 40 as a Price Line").

The paper varies its calibrated parameters one at a time (Table tab:tornado, TORNADO_ITEMS in
code/calibrate_horizons.py, and named bounds). This script varies them jointly over the ranges the paper itself states
and asks, for each headline claim, whether it holds at every point of the parameter box and, where it does not, where
it fails. It is not a forecast: most parameters are scenario values (class d) with ranges but no measured distribution.
The primary result is distribution-free: holds everywhere (yes/no) and the minimum and maximum of the tested quantity
over the box. Shares of draws are secondary and always labelled "uniform over the stated ranges (an assumption, not a
measured distribution)".

Usage
  python3 code/mc_claims.py                        # full run: 10,000 LHS draws, corners, searches, Sobol -> notes/mc/
  python3 code/mc_claims.py --n 500 --sobol-n 128 --out /tmp/mc_test     # quick test
  python3 code/mc_claims.py --print-dims           # the dimension table (markdown) and exit
  python3 code/mc_claims.py --verify-only          # reproduction checks only
  python3 code/mc_claims.py --seed 20261104 --out notes/mc_seed2 --compare-to notes/mc      # a second seed, recorded
                                                   # against the first run (block seed_comparison of its JSON and report)
An interrupted run resumes from <out>/ckpt/<configuration hash>/ when the same command is run again; --fresh discards it.
Each run writes <out>/mc_claims.json, <out>/mc_claims_report.md and <out>/draws_lhs.csv (selected outputs per
Latin-hypercube draw, read by code/mc_report_tex.py). The seed is recorded in the JSON (meta.args.seed, design.seed).

Sampling laws (round 3, 3 Nov 2026): uniform over each stated range, except compute per dollar of labor replaced at 2025
prices (kappa_2025, path mode), which spans 0.02 (the cost per completed task of agent runs) to 1 (the value test), a
factor of 50, and is drawn log-uniform: value = lo (hi/lo)^u, central 0.10 (the NaN coordinate). Every design works in
unit coordinates (LHS, corners, vertex search, Sobol, failure scans) and maps them through dim_value; dim_unit inverts it.
Sobol indices carry 95% confidence intervals: SALib analyze (num_resamples 200, conf_level 0.95; S1_conf and ST_conf are
the half-widths of its normal bootstrap interval, S1_ci and ST_ci the intervals) for the factors when SALib is used, and
a nonparametric bootstrap of the N base rows (200 resamples, 2.5th and 97.5th percentiles) for the groups and for the
numpy backend.

Nothing in the repository is written except under --out. code/calibrate_horizons.py is executed unchanged into a
namespace whose output paths point at a scratch copy of the tree (<out>/_shadow); its JSON is compared byte for byte
with notes/calibration_results.json, and the model below (a line-by-line mirror of the functions the claims use) is
checked against the executed functions and against the committed JSON and macros before any sampling.
Runs on Python 3.10-3.13 with numpy, scipy (optional, Sobol sequence), pandas and PyYAML (both only for the calibration
load in the main process); SALib is used for the factor-level Sobol indices when it is installed.
"""
import os

# One BLAS/OpenMP thread per process, set before numpy is imported here and in every spawned worker (which re-imports
# this module), so that N workers do not oversubscribe N cores. The model does no linear algebra.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"

import argparse  # noqa: E402
import ast  # noqa: E402
import contextlib  # noqa: E402
import filecmp  # noqa: E402
import gc  # noqa: E402
import hashlib  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import multiprocessing as mp  # noqa: E402
import platform  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402

try:
    import resource  # noqa: E402  (POSIX only; memory reporting)
except ImportError:                                   # pragma: no cover
    resource = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = "1.1"                                     # 1.1 (3 Nov 2026): kappa_2025 0.02-1 log-uniform; Sobol CIs; seed comparison; draws_lhs.csv
STRATA = ("net", "ub", "lb")
STRATUM_LABEL = {"net": "netted (central): S&M above the maintenance base buys growth",
                 "ub": "all S&M buys growth (bound)", "lb": "no S&M buys growth (bound)"}
HZ = ("2028", "2031", "2036")
YEARS = (2028, 2031, 2036)
H0 = 2025
N_PROC = 48
S_REF = 1e9
TOL = 1e-12
UNIFORM_LABEL = "uniform over the stated ranges (an assumption, not a measured distribution)"


def law_label(dims):
    """Label of the secondary shares: uniform over the stated ranges, naming any dimension drawn log-uniform."""
    lg = [d["name"] for d in dims if d.get("law") == "loguniform"]
    if not lg:
        return UNIFORM_LABEL
    return "uniform over the stated ranges, log-uniform for %s (an assumption, not a measured distribution)" % ", ".join(lg)
SHADOW_INPUTS = ("notes/calibration_anchor_v3.json", "notes/empirics_v3.json", "notes/bootstrap_draws_v3.npz",
                 "notes/frontier_slope_v3.json", "data/panel_v3.csv", "data/v3_inputs/interest_income_deferred.json")
CALIB = "code/calibrate_horizons.py"
PARAMS = "data/tasks/params.yaml"


# ======================================================================================================================
# Model: mirror of the functions of code/calibrate_horizons.py that the claims use. Operation order is kept so that the
# central point reproduces the committed numbers exactly; verify_mirror() checks every function against the executed
# originals (all cases, all tornado items, all payback cases) before sampling.
# ======================================================================================================================
def fullcost_v(v, c_c):
    """fullcost(case, h) with the factor values v and compute share c_c."""
    risk = v["s0"] / v["L0"] * (1 + v["L0"] + math.log(v["Me"]))
    pqc = v["phi_pqc"] * v["s0"] / v["sec_it"]
    aic = (v["aic_fixed"] + v["aic_pp"] * 48 * (30e3 + 10e3 / 1.22)) / S_REF
    c_sec = risk + pqc + aic
    c_mnt = (v["delta_M"] + v["kappa_rv"] / v["T_up"]) * v["B"]
    Emin = 1 + (1 - v["Zcap"] ** (1 - v["p_tail"])) / (v["p_tail"] - 1)
    c_err_e = v["A_auto"] * v["u_rev"] * v["ell_e"]
    c_err_m = v["A_auto"] * v["mu_m"] * (1 - v["d_m"]) * v["ell_m"] * Emin
    c_err_cm = v["nu_cm"] / 365 * v["A_auto"] * (1 + v["XY"])
    c_err = c_err_e + c_err_m + c_err_cm
    c_anc = v["s_fin"] * c_c + v["anc_fixed"] / S_REF
    c_full = c_mnt + c_sec + c_err + c_anc
    base = (1 - v["tau"]) * (1 - c_c - v["f"] - v["a_min"] - c_full)
    base_acc = (1 - v["tau"]) * (1 - c_c - v["f"] - v["a_min"])
    return dict(c_c=c_c, f=v["f"], a_min=v["a_min"], tau=v["tau"], risk=risk, pqc=pqc, aic=aic, c_sec=c_sec,
                c_mnt=c_mnt, c_err=c_err, c_err_e=c_err_e, c_err_m=c_err_m, c_err_cm=c_err_cm, c_anc=c_anc,
                c_full=c_full, base=base, base_acc=base_acc, G100=1 - base, G100_acc=1 - base_acc)


def pt_margin_v(c, phi, m0A):
    """pt_margin(c, phi, m0A) (scope 'all', rate phi): after-tax margin term at pass-through rate phi."""
    tau, f = c["tau"], c["f"]
    K = 1 - f - c["base"] / (1 - tau)
    C0 = 1 - f - m0A / (1 - tau)
    S = C0 - K
    p1 = 1 - phi * S
    return (1 - tau) * (1 - f - K / p1)


def rates_v(p, kap=None):
    kap = p["kap"] if kap is None else kap
    rho_chg = p["kappa_abs"]
    rho_dec = kap * p["Phi"] / (N_PROC * p["e"] * p["Tpar"])
    rho_sec = p["sec"] / N_PROC
    rho = min(rho_chg, rho_dec, rho_sec)
    nuD = p["nuL"] * (1 - p["kkeep"]) + p["nuV"]
    slow = 1 + p["nuR"] * p["Tfrz"]
    surv = math.exp(-nuD * slow * p["Temb"])
    q = p["varpi"] * (surv if p.get("haircut", False) else 1.0)
    return dict(rho=rho, q=q, clock=slow, attempt_rate=rho / slow,
                binding=["change", "decision", "security"][int(np.argmin([rho_chg, rho_dec, rho_sec]))])


def pace_v(p, dM):
    out = rates_v(p)
    for h in YEARS:
        tR = (h - H0) / out["clock"]
        n = 0 if tR < p["Temb"] else math.floor((tR - p["Temb"]) / p["Tpar"] + 1e-12) + 1
        raw = out["q"] * out["rho"] * p["Tpar"] * n
        done = raw >= 1
        out[h] = dict(n=n, s=p["bbar"] * min(1.0, raw), running=not done,
                      dip=0.0 if done else out["attempt_rate"] * p["Tpb"] * dM[h])
    step = out["q"] * out["rho"] * p["Tpar"]
    n_full = math.ceil(1 / step - 1e-9)
    out["complete_year"] = H0 + out["clock"] * (p["Temb"] + (n_full - 1) * p["Tpar"])
    n_cross = math.floor(out["attempt_rate"] * p["Tpb"] / (p["bbar"] * step)) + 1
    out["cross_years"] = out["clock"] * (p["Temb"] + (n_cross - 1) * p["Tpar"]) if n_cross < n_full else None
    return out


def pi_scaled_v(Pi0, mu, alpha, k):
    return Pi0 * mu ** (1 / (1 - alpha)) * (1 - k) ** (1 / (1 - alpha))


def central_path_v(m0A, Pi25, ceil_h, pace_p, phi, k_pre, psi, G, mu, alpha, tau_anchor):
    """central_path(...) with explicit inputs: ceil_h = {h: fullcost dict} of the target case, G and mu by horizon."""
    tgt = {h: pt_margin_v(ceil_h[h], phi, m0A) for h in HZ}
    P = pace_v(pace_p, {int(h): tgt[h] - m0A for h in HZ})
    k = (1 - psi * tau_anchor) * k_pre
    res = {"m0A": m0A, "Pi25": Pi25, "k": k, "pace": P}
    for h in HZ:
        yi = int(h)
        c = ceil_h[h]
        G_, mu_ = G[h], mu[h]
        s_ = P[yi]["s"]
        if phi:
            C0 = 1 - c["f"] - m0A / (1 - c["tau"])
            Sh = C0 - (1 - c["f"] - c["base"] / (1 - c["tau"]))
            m0 = (1 - c["tau"]) * (1 - c["f"] - (C0 - s_ * Sh) / (1 - phi * s_ * Sh))
        else:
            m0 = m0A + s_ * (tgt[h] - m0A)
        Rinf = m0 + (1 - k) * G_
        Pi = pi_scaled_v(Pi25, mu_, alpha, k)
        res[h] = dict(s=s_, target=tgt[h], m0=m0, G=G_, mu=mu_, Rinf=Rinf, Pi=Pi, R=Rinf + Pi, dip=P[yi]["dip"],
                      R_net=Rinf + Pi - P[yi]["dip"], running=P[yi]["running"])
    return res


_PB_GRID = {}


def _pb_grid(dt, T):
    key = (dt, T)
    if key not in _PB_GRID:
        t = np.arange(0, T, dt)
        _PB_GRID[key] = (t, H0 + t)
    return _PB_GRID[key]


def payback_v(m0A, targets, pace_p, r, dt=1 / 365, T=200.0):
    """payback(path, pace_p, r): flow crossing, cumulative payback (undiscounted and discounted), PV ratio, holds."""
    dM = {int(h): targets[h] - m0A for h in HZ}
    yrs = sorted(dM)
    rr = rates_v(pace_p)
    step = rr["q"] * rr["rho"] * pace_p["Tpar"]
    t, tH = _pb_grid(dt, T)
    tR = t / rr["clock"]
    n = np.where(tR < pace_p["Temb"], 0, np.floor((tR - pace_p["Temb"]) / pace_p["Tpar"] + 1e-12) + 1)
    raw = step * n
    dm = np.interp(tH, yrs, [dM[y] for y in yrs])
    gain = pace_p["bbar"] * np.minimum(1.0, raw) * dm
    dip = np.where(raw < 1.0, rr["attempt_rate"] * pace_p["Tpb"] * dm, 0.0)
    net = gain - dip
    disc = (1 + r) ** (-t)
    cu, cd = np.cumsum(net) * dt, np.cumsum(net * disc) * dt

    def first(m):
        return float(t[np.argmax(m)]) if m.any() else None
    neg = cu < 0
    pb_u = first((cu >= 0) & (np.cumsum(neg) > 0))
    pb_d = first((cd >= 0) & (np.cumsum(cd < 0) > 0))
    pv_gain, pv_dip = float(np.sum(gain * disc) * dt), float(np.sum(dip * disc) * dt)
    return dict(cross_flow=first((gain >= dip) & (raw < 1.0) & (raw > 0)), payback_undiscounted=pb_u,
                payback_discounted=pb_d, npv_points_years=pv_gain - pv_dip, pv_gain=pv_gain, pv_dip=pv_dip,
                ratio=pv_gain / pv_dip, complete_years=float(t[np.argmax(raw >= 1.0)]) if (raw >= 1.0).any() else None,
                hold={yr: dict(cum=float(cu[int(round(yr / dt)) - 1]), cum_disc=float(cd[int(round(yr / dt)) - 1]))
                      for yr in (3, 4, 5, 7, 10)})


def pull_multiple_v(a, P_q3):
    """rule1000_multiple['ub'][a]: demand pull a Rule of 1000 needs relative to the upper-quartile anchor surplus."""
    C = (1 - a) * a ** (a / (1 - a))
    return ((10 - (0.5 + 0.2)) / C) ** (1 - a) / (P_q3 / C) ** (1 - a)


def cc_path_v(h, sL, k25, D, kf, om, floor_share):
    """cc_path(h) of the explicit compute-share path with drivers given."""
    if h == "prices2025":
        return sL * k25
    k_fixed = max(k25 / D ** (int(h) - 2025), floor_share * k25)
    return sL * (om * kf + (1 - om) * k_fixed)


# ---- levers (code/playbook/run_archetypes.py paper1_positions and ranking_by_basis)
def growth_spend_v(sm, basis, bM):
    if basis == "net":
        return max(sm - bM, 0.0)
    if basis == "ub":
        return sm
    return 0.0


def levers_v(positions, bM, phi, alpha, basis):
    """Counts of Table tab:levers-position and of the companion paper's four-lever ranking at the revealed weight."""
    n_ge = n_eng_above = n_eng_first = 0
    ratios = []
    for p in positions:
        sig = growth_spend_v(p["sm"], basis, bM)
        n_ge += sig > p["ga"]                                   # lead = growth engine iff sigma > a_GA
        n_eng_above += p["rd"] > max(sig, p["ga"])              # engineering above both (Paper 1 text)
        f_fee = 1.0 - p["C0"] - p["m0_engine"]
        m0_b = p["m0_engine"] + (sig - p["sigma_engine"])
        keep = 1.0 - phi * max(1.0 - f_fee - m0_b, 0.0)
        vals = {"growth engine": 0.1 * sig, "overhead (G&A)": 0.1 * p["ga"], "engineering (R&D)": 0.1 * p["rd"],
                "cost of revenue": 0.1 * keep * p["c_h"]}
        rk = sorted(vals, key=lambda kk: -vals[kk])
        n_eng_first += rk[0] == "engineering (R&D)"
        if sig > 0:
            ratios.append((p["ga"] / sig) ** (1 - alpha))
    return dict(n_ge_first=float(n_ge), n_eng_above=float(n_eng_above), n_eng_first=float(n_eng_first),
                ratio_min=min(ratios) if ratios else float("nan"), ratio_max=max(ratios) if ratios else float("nan"))


# ---- accountability floor (code/paper1_macros.py, Proposition prop:amin example)
def amin_P_v(nh, na, A, pcc=0.0, phm=None, pca=None):
    pca = A["pca"] if pca is None else pca
    if not (nh or na):
        return 1.0
    P = 1.0
    if nh:
        p_h = phm if (na and phm is not None) else A["ph"]
        P *= A["pch"] + (1 - A["pch"]) * p_h ** nh
    if na:
        P *= pca + (1 - pca) * A["pa"] ** na
    return pcc + (1 - pcc) * P


def amin_cost_v(nh, na, A):
    return (A["itgc"] if na else 0.0) + nh * A["ch"] + na * A["ca"]


def amin_best_v(pibar, A, N=None, pca=None, kind="any", nmax=7, pcc=0.0, phm=None):
    N = A["N"] if N is None else N
    best = None
    for nh in range(nmax):
        for na in range(nmax):
            if not (nh or na) or (kind == "human" and na) or (kind == "ai" and nh):
                continue
            if 1 - (1 - amin_P_v(nh, na, A, pcc=pcc, phm=phm, pca=pca)) ** N <= pibar and \
                    (best is None or amin_cost_v(nh, na, A) < best[0]):
                best = (amin_cost_v(nh, na, A), nh, na)
    return best


# ======================================================================================================================
# Calibration load (main process only): execute code/calibrate_horizons.py unchanged into a shadow tree
# ======================================================================================================================
def _build_shadow(shadow):
    if os.path.isdir(shadow):
        shutil.rmtree(shadow)
    for d in ("code", "notes", os.path.join("data", "v3_inputs"), os.path.join("sections", "tables")):
        os.makedirs(os.path.join(shadow, d), exist_ok=True)
    for rel in SHADOW_INPUTS:                          # inputs: read-only symlinks (copies where symlinks fail)
        src, dst = os.path.join(REPO, rel), os.path.join(shadow, rel)
        try:
            os.symlink(src, dst)
        except (OSError, NotImplementedError, AttributeError):
            shutil.copy2(src, dst)
    shutil.copy2(os.path.join(REPO, "sections", "appendix_proofs.tex"),   # the script rewrites it: a real copy
                 os.path.join(shadow, "sections", "appendix_proofs.tex"))


def load_calibration(shadow):
    _build_shadow(shadow)
    path = os.path.join(REPO, CALIB)
    src = open(path).read()
    g = {"__name__": "calibrate_horizons_mc", "__file__": os.path.join(shadow, "code", "calibrate_horizons.py")}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src, path, "exec"), g)
    assert os.path.realpath(g["BASE"]) == os.path.realpath(shadow), "calibration outputs not redirected to the shadow"
    same = {}
    for rel in ("notes/calibration_results.json", "sections/tables/tab_calib.tex", "sections/tables/tab_tornado.tex"):
        same[rel] = filecmp.cmp(os.path.join(REPO, rel), os.path.join(shadow, rel), shallow=False)
    g["_mc_byte_identical"] = same
    g["_mc_json_diff"] = _json_numeric_diff(os.path.join(REPO, "notes", "calibration_results.json"),
                                            os.path.join(shadow, "notes", "calibration_results.json"))
    return g


def _json_numeric_diff(pa, pb):
    """Largest relative difference between the numeric leaves of two JSON files and the paths that differ (library
    versions can change the last digit of some floats, e.g. np.polyfit in the ell_psi block)."""
    A, B = json.load(open(pa)), json.load(open(pb))
    diffs = []

    def walk(a, b, path):
        if isinstance(a, dict) and isinstance(b, dict):
            for k_ in set(a) | set(b):
                if k_ not in a or k_ not in b:
                    diffs.append((path + "/" + str(k_), float("inf")))
                else:
                    walk(a[k_], b[k_], path + "/" + str(k_))
        elif isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                diffs.append((path, float("inf")))
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, path + "[%d]" % i)
        elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
            if a != b and not (a != a and b != b):                      # NaN leaves are equal here
                rel = abs(a - b) / max(abs(a), abs(b), 1e-300) if math.isfinite(a) and math.isfinite(b) else float("inf")
                diffs.append((path, rel))
        elif a != b:
            diffs.append((path, float("inf")))
    walk(A, B, "")
    blocks = sorted(set(p_.split("/")[1] for p_, _ in diffs if p_.count("/") >= 1))
    return dict(n_leaves_differ=len(diffs), max_rel_diff=max((d_ for _, d_ in diffs), default=0.0), blocks=blocks,
                first=[p_ for p_, _ in diffs[:5]])


def _ast_constants(path, names):
    """Values of simple module-level assignments and function defaults in a script, without executing it."""
    tree = ast.parse(open(path).read())
    out = {}
    safe = {"__builtins__": {}}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            nm = node.targets[0].id
            if nm in names:
                out[nm] = eval(compile(ast.Expression(node.value), path, "eval"), safe, dict(out))
        elif isinstance(node, ast.FunctionDef) and node.name in names:
            a = node.args
            dflt = a.defaults
            keys = [x.arg for x in a.args][-len(dflt):] if dflt else []
            out[node.name] = {kk: eval(compile(ast.Expression(vv), path, "eval"), safe, dict(out)) for kk, vv in zip(keys, dflt)}
    return out


def lever_positions():
    import importlib.util
    spec = importlib.util.spec_from_file_location("mc_archetypes", os.path.join(REPO, "code", "playbook", "archetypes.py"))
    AR = importlib.util.module_from_spec(spec)
    sys.modules["mc_archetypes"] = AR                   # dataclasses look the module up while the class is built
    spec.loader.exec_module(AR)
    archs, _ = AR.build_archetypes()
    R = json.load(open(os.path.join(REPO, "notes", "playbook_results.json")))
    pos = []
    for a in archs:
        if a.code == "A7":
            continue
        cfg = R["configs"][a.code + "_low"]
        st, pt, p1 = cfg["state"], cfg["pass_through"], cfg["part1"]
        for k_, v_ in (("sm", a.sm), ("a_GA", a.ga), ("rd", a.rd)):
            assert abs(st[k_] - v_) < 1e-9, ("archetype recomputed from data/panel_v3.csv differs from playbook_results", a.code, k_)
        pos.append(dict(code=a.code, name=a.name, sm=float(a.sm), ga=float(a.ga), rd=float(a.rd), c_h=float(st["c_h"]),
                        m0_engine=float(p1["m0"]), sigma_engine=float(st["sigma"]), C0=float(pt["C0"]),
                        phi_engine=float(pt["phi"])))
    return pos, float(AR.MAINT_BASE), R["ranking_by_basis"]


def build_snapshot(g):
    """Plain-data snapshot of everything the model needs (passed once to each worker's initializer)."""
    FC = {k: [float(x) for x in v] for k, v in g["FC"].items() if k != "c_c"}
    an = g["anchor"]
    Z = g["_Z"]
    st = [str(x) for x in Z["anchor__statistics"]]
    assert str(Z["anchor__variants"][0]) == "E1"
    Ast = Z["anchor"][:, 0, :]
    draws = g["_draws"]
    boot = {b: np.array([d[b] for d in draws]) for b in STRATA}
    boot["base"] = np.array([d["base"] for d in draws])
    boot["G"] = np.array([d["G"] for d in draws])
    boot["Pi_ub"] = Ast[:, st.index("anchor_p95_Pi_ub_med")].astype(float)
    assert np.max(np.abs(boot["ub"] - Ast[:, st.index("anchor_p95_m0_ub_med")])) < 1e-12
    assert np.max(np.abs(boot["net"] - Ast[:, st.index("anchor_p95_m0_net_med")])) < 1e-9
    assert np.max(np.abs(boot["base"] - Ast[:, st.index("anchor_p95_maint_base")])) < 1e-9
    pi_ci = g["ANCHOR_BOOT"]["E1"]["Pi_ub_med"]["ci90"]
    assert abs(np.quantile(boot["Pi_ub"], 0.05) - pi_ci[0]) < 1e-9 and abs(np.quantile(boot["Pi_ub"], 0.95) - pi_ci[1]) < 1e-9
    positions, bM_ar, rbb = lever_positions()
    assert abs(bM_ar - g["MAINT_BASE"]) < 1e-15
    A = _ast_constants(os.path.join(REPO, "code", "paper1_macros.py"),
                       {"AUDIT_FEE_LO", "AUDIT_FEE", "AUDIT_FEE_HI", "KPMG_SIZE", "REV", "N_OPP", "EPS",
                        "ITGC_LINE_DESIGN", "amin_P", "amin_cost"})
    amin = dict(ph=A["amin_P"]["ph"], pch=A["amin_P"]["pch"], pa=A["amin_P"]["pa"], pca=A["amin_P"]["pca"],
                ch=A["amin_cost"]["ch"], ca=A["amin_cost"]["ca"], itgc=float(A["ITGC_LINE_DESIGN"]), REV=float(A["REV"]),
                N=int(A["N_OPP"]), fee=float(A["AUDIT_FEE"]), fee_lo=float(A["AUDIT_FEE_LO"]), fee_hi=float(A["AUDIT_FEE_HI"]),
                kpmg_small=float(A["KPMG_SIZE"]["Small"]), eps=dict(A["EPS"]))
    tf = [r for r in g["_av"]["E1"]["firm_years"]]
    snap = dict(
        FC=FC, CC={h: [float(v[0]), [float(v[1][0]), float(v[1][1])], v[2]] for h, v in g["CC"].items()},
        CC_PATH=dict(g["CC_PATH"]), CC_VALUE_TEST_CAP=float(g["CC_VALUE_TEST_CAP"]),
        KAPPA_2025=[float(g["KAPPA_LO"]), float(g["KAPPA_HI"])],      # round 3: the kappa bounds of the text (CcLo/CcHi)
        PACE={k: dict(v) for k, v in g["PACE"].items()}, PHI=[float(x) for x in g["PHI"]],
        HZ_mu={h: [float(x) for x in g["HZ"][h]["mu"]] for h in HZ}, G_BAND=[float(x) for x in g["G_BAND"]],
        G25=float(g["G25"]), ALPHA_C=float(g["ALPHA_C"]), ALPHAS=[float(x) for x in g["ALPHAS"]], TAU=float(g["TAU"]),
        MAINT_BASE=float(g["MAINT_BASE"]), R_WACC=float(g["R_WACC"]), PSI={k: float(v) for k, v in g["PSI"].items()},
        anchor={b: [float(x) for x in an["m0_" + b]] for b in STRATA}, Pi_ub=[float(x) for x in an["Pi_ub"]],
        boot={k: [float(x) for x in v] for k, v in boot.items()},
        firm_years=[dict(m=float(r["m_fcf_sbc"]), sig=float(r["sig_ub"]), kg=float(r["kg"])) for r in tf],
        positions=positions, ranking_by_basis={k: v for k, v in rbb.items() if k != "positions"}, amin=amin,
        tornado={h: [dict(key=r["key"], low=float(r["low"]), high=float(r["high"])) for r in g["TORNADO"][h]["rows"]]
                 for h in g["TORNADO"]},
        tornado_ref={h: float(g["TORNADO"][h]["reference"]) for h in g["TORNADO"]},
        G_fav=float(g["CEIL"]["favorable"]["G100"]),
    )
    return snap


# ======================================================================================================================
# Parameter box
# ======================================================================================================================
_SRC_CACHE = {}


def src_line(rel, pattern, nth=1):
    """'file:line' of the nth line of a repository file matching a regex (sources in the dimension table)."""
    key = (rel, pattern, nth)
    if key not in _SRC_CACHE:
        n_, hit = 0, None
        try:
            for i, line in enumerate(open(os.path.join(REPO, rel)), 1):
                if re.search(pattern, line):
                    n_ += 1
                    if n_ == nth:
                        hit = i
                        break
        except OSError:
            pass
        _SRC_CACHE[key] = f"{rel}:{hit}" if hit else rel
    return _SRC_CACHE[key]


FC_DIMS = [   # key, label, class, group
    ("f", "Payment fees f", "d", "fees"),
    ("tau", "Cash tax rate tau", "b", "tax"),
    ("a_min", "Accountability floor a_min (band)", "b", "accountability"),
    ("L0", "Control effectiveness L_sec", "d", "security"),
    ("Me", "Exposure multiplier at full automation", "d", "security"),
    ("sec_it", "Security share of IT spend", "a", "security"),
    ("phi_pqc", "Post-quantum migration (share of IT spend a year)", "d", "security"),
    ("aic_fixed", "AI compliance fixed cost ($ a year)", "d", "security"),
    ("aic_pp", "AI compliance per-process factor", "d", "security"),
    ("delta_M", "Upkeep rate of builds delta_M", "b", "maintenance"),
    ("kappa_rv", "Revalidation cost per build", "d", "maintenance"),
    ("T_up", "Model-upgrade interval T_up (years)", "c", "maintenance"),
    ("B", "Build stock per revenue", "d", "maintenance"),
    ("u_rev", "Error rate with no review", "d", "ai_failure"),   # round 3 (GPT-21): a sum of rates per sentence and per output
    ("ell_e", "Loss per undetected error", "d", "ai_failure"),
    ("mu_m", "Consequential misbehavior per task", "d", "ai_failure"),
    ("d_m", "Monitor recall", "a", "ai_failure"),
    ("p_tail", "Pareto tail index of misbehavior losses", "b", "ai_failure"),
    ("nu_cm", "Provider incidents a year (day-equivalents)", "b", "ai_failure"),
    ("s_fin", "Management of AI spend (share of c_c)", "d", "ancillary"),
    ("anc_fixed", "Incident-response and legal fixed cost ($ a year)", "d", "ancillary"),
]
PACE_DIMS = [  # key, label, class, params.yaml pattern (None: code only)
    ("kappa_abs", "Change capacity (share of the program a year)", "b", r"affected_fte_share_per_year:"),
    ("varpi", "Share of attempts that create value varpi", "b", r"transformation_attempt_creates_value_varpi:"),
    ("bbar", "Share of targeted value realized bbar", "a", r"transformation_value_realized_share_b_bar:"),
    ("nuR", "Reorganization hazard nu_R", "b", r"reorganization_hazard_h_R:"),
    ("Tfrz", "Reorganization freeze T_frz (years)", "b", r"reorg_freeze_T_freeze_years:"),
    ("Tpar", "Wave length / parallel run T_par (years)", "b", r"ai_agent_shadow_mode:"),
    ("Temb", "Embedding time T_emb (years)", "b", r"embedding_time_T_emb_years:"),
    ("Tpb", "Transition cost in years of savings T_pb", "d", r"embedding_time_T_emb_years:"),
    ("Phi", "Concurrent initiatives Phi", "d", r"concurrent_major_initiatives_capacity_Phi:"),
    ("e", "Decision units per initiative e", "d", r"decision_units_per_initiative_launch_and_gate:"),
    ("sec", "Security reviews a year (reviewer-quarters x 4 x 2)", "d", r"security_review_bandwidth_Phi_sec_reviews_per_reviewer_quarter:"),
]
GROUP_ORDER = ["fees", "tax", "accountability", "security", "maintenance", "ai_failure", "ancillary", "compute",
               "execution", "market_growth", "pass_through", "capital", "surplus", "discount", "anchor", "maint_base"]
FULLCOST_TARGET = ["fees", "tax", "accountability", "security", "maintenance", "ai_failure", "ancillary", "compute"]
VARIANTS = {   # named conditions of a claim, held at their central values in the conditional variant
    "full": dict(label="full box", fixed=[]),
    "A": dict(label="stated conditions: fixed prices (phi = 0), k = 0", fixed=["pass_through", "capital"]),
    "B": dict(label="stated conditions: central execution, fixed prices, k = 0",
              fixed=["execution", "pass_through", "capital"]),
    "C": dict(label="stated conditions: compute share 6% at 2025 prices, fixed prices, k = 0", fixed=[]),
}


def build_dims(snap, opts):
    """The parameter box: every dimension with its low, central and high value, sampling law, class and source.
    law 'uniform': value = lo + u (hi - lo). law 'loguniform': value = lo (hi/lo)^u (kappa_2025, which spans a factor
    of 50). law 'boot:<series>': u maps to the bootstrap quantile at level 0.05 + 0.9 u (the paper's 90% interval; the
    central value is the point estimate). 'iqr:<stratum>' (option --anchor-range iqr): uniform between the firm-year
    quartiles."""
    FC, PACE = snap["FC"], snap["PACE"]
    D = []

    def add(**kw):
        kw.setdefault("law", "uniform")
        kw.setdefault("note", "")
        D.append(kw)
    for key, lab, cls, grp in FC_DIMS:
        fav, cen, con = FC[key]
        lo, hi = min(fav, con), max(fav, con)
        note = "favorable end " + ("low" if fav < con else "high")
        src = src_line(CALIB, r"'%s'\s*:\s*\(" % re.escape(key)) + " (FC; Appendix Table tab:fullcost)"
        if key == "a_min":
            lo, hi = 0.005, 0.046
            note = "band of the text (Sec. 7.2) and params.yaml; the favorable case uses 0.015"
            src = src_line(CALIB, r"band_used=\(0\.005") + "; " + src_line(PARAMS, r"a_min_accountability_floor:") + \
                "; macros AminLo/AminHi"
        if key == "tau":
            src += "; " + src_line(PARAMS, r"tau_cash_tax_rate:")
        if key == "f":
            src += "; " + src_line(PARAMS, r"f_payment_fees:")
        add(name=key, label=lab, group=grp, cls=cls, lo=lo, central=cen, hi=hi, src=src, note=note)
    cp = snap["CC_PATH"]
    if opts["cc_mode"] == "path":
        add(name="s_L", label="Labor cost automated, share of revenue s_L (also the error base W_A)", group="compute",
            cls="c", lo=0.50, central=cp["s_L"], hi=0.65, src=src_line(CALIB, r"with s_L 0\.60") + "; " + src_line(PARAMS, r"s_L_range:"),
            note="A_auto = s_L (code comment: same base as the compute share)")
        # round 3 (3 Nov 2026): from the cost per completed task of agent runs (0.02) to the value test (1), the bounds of
        # the text's range of c_c = s_L x kappa (macros KappaLo, CcLo, CcHi); log-uniform, central 0.10. Was 0.01-0.35, uniform
        k_lo, k_hi = snap["KAPPA_2025"]
        add(name="kappa_2025", label="Compute per $ of labor replaced at 2025 prices", group="compute", cls="b",
            lo=k_lo, central=cp["kappa_2025"], hi=k_hi, law="loguniform",
            src=src_line(CALIB, r"^KAPPA_LO = ") + "-" + src_line(CALIB, r"^KAPPA_HI = ") + "; " + src_line(PARAMS, r"kappa_2025_range:"),
            note="per completed task to the value test (c_c = s_L x kappa); log-uniform, central 0.10")
        add(name="D", label="Fall of the fixed-performance price, x a year", group="compute", cls="a", lo=3.0,
            central=cp["D"], hi=10.0, src=src_line(CALIB, r"D = 5 \[3, 10\]") + "; " + src_line(PARAMS, r"D_range:"))
        add(name="kappa_front", label="Compute per $ of labor at the frontier", group="compute", cls="d", lo=0.10,
            central=cp["kappa_front"], hi=0.50, src=src_line(CALIB, r"kappa_front 0\.33") + "; " + src_line(PARAMS, r"kappa_front_range:"))
        for h, (lo, hi) in (("2028", (0.3, 0.9)), ("2031", (0.2, 0.7)), ("2036", (0.1, 0.5))):
            add(name="omega_" + h, label="Share of automated labor in frontier tasks, " + h, group="compute", cls="d",
                lo=lo, central=cp["omega"][h], hi=hi, src=src_line(PARAMS, r"omega_range:") + " (" + h + ")")
    else:
        add(name="s_L", label="Labor cost automated, share of revenue s_L (error base W_A only)", group="compute",
            cls="c", lo=0.50, central=cp["s_L"], hi=0.65, src=src_line(PARAMS, r"s_L_range:"))
        c_lo, c_hi = snap["CC"]["prices2025"][1]          # round 3: the text's range (CcLo/CcHi), from the calibration
        add(name="cc_2025", label="Compute share at 2025 prices (credible range of the text)", group="compute",
            cls="b", lo=c_lo, central=snap["CC"]["prices2025"][0], hi=c_hi,
            src="macros CcLo/CcHi; " + src_line(CALIB, r"^CC = \{"), note="s_L x kappa: per completed task to the value test")
        for h in HZ:
            c0, (lo, hi), _ = snap["CC"][h]
            add(name="cc_" + h, label="Compute share " + h, group="compute", cls="d", lo=lo, central=c0, hi=hi,
                src=src_line(CALIB, r"^CC = \{") + "; " + src_line(PARAMS, r"'%s':" % h))
    pc, pf, ps = PACE["central"], PACE["fast"], PACE["slow"]
    for key, lab, cls, pat in PACE_DIMS:
        lo, hi = min(pf[key], ps[key]), max(pf[key], ps[key])
        note = "fast end " + ("low" if pf[key] < ps[key] else "high")
        if key == "varpi" and opts.get("bcg_win"):
            lo = 0.30
            note += "; extended to 0.30 (--bcg-win: BCG win zone, tornado row)"
        src = src_line(CALIB, r"^PACE = \{") + " (slow/fast span)"
        if pat:
            src += "; " + src_line(PARAMS, pat)
        add(name=key, label=lab, group="execution", cls=cls, lo=lo, central=pc[key], hi=hi, src=src, note=note)
    gb = snap["G_BAND"]
    add(name="G", label="Market growth G", group="market_growth", cls="c", lo=gb[0], central=snap["G25"], hi=gb[1],
        src=src_line(CALIB, r"^G_BAND = ") + "; macros GBandLo/GBandHi, CenG", note="central = anchor median growth")
    add(name="phi", label="Pass-through rate phi", group="pass_through", cls="b", lo=0.0, central=0.0,
        hi=max(snap["PHI"]), src=src_line(CALIB, r"^PHI = ") + "; " + src_line(CALIB, r"\('pass_through', 'Pass-through"))
    add(name="k_pre", label="Capital per dollar of new revenue k", group="capital", cls="d", lo=0.0, central=0.0, hi=0.5,
        src=src_line(CALIB, r"\('capital', 'Capital"))
    add(name="psi", label="Tax deductibility of capital psi", group="capital", cls="a", lo=0.0, central=0.0, hi=1.0,
        src=src_line(CALIB, r"^PSI = ") + " (Remark taxes)", note="enters only with k > 0")
    add(name="alpha", label="Spend elasticity alpha", group="surplus", cls="d", lo=snap["ALPHAS"][0],
        central=snap["ALPHA_C"], hi=snap["ALPHAS"][1], src=src_line(CALIB, r"^ALPHAS = ") + "; " + src_line(CALIB, r"^ALPHA_C = ")
        + "; " + src_line(PARAMS, r"alpha_spend_elasticity:"), note="enters only through a positive surplus (ub stratum)")
    for h in HZ:
        lo, hi = snap["HZ_mu"][h]
        add(name="mu_" + h, label="Demand pull relative to 2025, " + h, group="surplus", cls="d", lo=lo,
            central=(lo + hi) / 2, hi=hi, src=src_line(CALIB, r"^HZ = \{") + " (" + h + "); central = midpoint (CEN)",
            note="enters only through a positive surplus (ub stratum)")
    a, b = snap["boot"]["Pi_ub"], snap["Pi_ub"]
    pi = np.array(a)
    if opts["anchor_range"] == "iqr":
        add(name="Pi_ub", label="Median anchor surplus, all S&M buys growth", group="surplus", cls="c", lo=b[0],
            central=b[1], hi=b[2], law="iqr:Pi_ub", src=src_line(CALIB, r"^Pi_ub = "), note="ub stratum only; floored at 0")
    else:
        add(name="Pi_ub", label="Median anchor surplus, all S&M buys growth", group="surplus", cls="c",
            lo=float(np.quantile(pi, 0.05)), central=b[1], hi=float(np.quantile(pi, 0.95)), law="boot:Pi_ub",
            src="notes/calibration_anchor_v3.json bootstrap E1 Pi_ub_med; macros AncPiUbEoneLo/Hi",
            note="ub stratum only; floored at 0 as in central_path; drawn independently of the intercept (conservative)")
    add(name="r", label="Discount rate (payback, NPV)", group="discount", cls="b", lo=0.07, central=snap["R_WACC"],
        hi=0.1066, src=src_line(CALIB, r"^R_WACC = ") + "; " + src_line(PARAMS, r"r_own_wacc:"))
    if opts["anchor_range"] == "iqr":
        add(name="m0A", label="Anchor intercept (median firm-year), stratum-specific", group="anchor", cls="c",
            lo={s: snap["anchor"][s][0] for s in STRATA}, central={s: snap["anchor"][s][1] for s in STRATA},
            hi={s: snap["anchor"][s][2] for s in STRATA}, law="iqr:m0A", src=src_line(CALIB, r"\('anchor_quartile'"),
            note="--anchor-range iqr: firm-year quartiles (tornado row)")
    else:
        bt = {s: np.array(snap["boot"][s]) for s in STRATA}
        add(name="m0A", label="Anchor intercept (median firm-year), stratum-specific", group="anchor", cls="c",
            lo={s: float(np.quantile(bt[s], 0.05)) for s in STRATA}, central={s: snap["anchor"][s][1] for s in STRATA},
            hi={s: float(np.quantile(bt[s], 0.95)) for s in STRATA}, law="boot:m0A",
            src=src_line(CALIB, r"^_Z = np\.load") + " (999 firm-cluster draws); macros AnchorMzeroNetCiLo/Hi",
            note="bootstrap law within its 90% interval; central = point estimate")
    bb = np.array(snap["boot"]["base"])
    add(name="b_M", label="Maintenance base of S&M b_M", group="maint_base", cls="c", lo=float(np.quantile(bb, 0.05)),
        central=snap["MAINT_BASE"], hi=float(np.quantile(bb, 0.95)), law="boot:base",
        src=src_line(CALIB, r"_b5\['maint_base'\]") + " (bootstrap of the anchor block)",
        note="enters the lever counts only (the netted intercept already carries its own b_M)")
    for i, d_ in enumerate(D):
        d_["idx"] = i
    return D


# ======================================================================================================================
# Worker state and evaluation
# ======================================================================================================================
_M = {}


def init_worker(snap, opts):
    """Pool initializer: builds the model constants once per worker (the calibration snapshot is loaded once)."""
    global _M
    _M = build_model(snap, opts)


def build_model(snap, opts):
    D = build_dims(snap, opts)
    M = dict(snap=snap, opts=opts, dims=D, k=len(D), idx={d["name"]: d["idx"] for d in D})
    M["fc_central"] = {k: v[1] for k, v in snap["FC"].items()}
    M["fc_keys"] = [k for k, _, _, _ in FC_DIMS]
    M["pace_central"] = dict(snap["PACE"]["central"])
    M["pace_keys"] = [k for k, _, _, _ in PACE_DIMS]
    M["cc_central"] = {h: snap["CC"][h][0] for h in snap["CC"]}
    cp = snap["CC_PATH"]
    M["cc_drv_central"] = {h: cc_path_v(h, cp["s_L"], cp["kappa_2025"], cp["D"], cp["kappa_front"],
                                        cp["omega"].get(h, 0.0), cp["floor_share"]) for h in ("prices2025",) + HZ}
    M["grid"] = np.linspace(0.0, 1.0, 999)
    M["boot_sorted"] = {k: np.sort(np.array(v)) for k, v in snap["boot"].items()}
    M["boot_raw"] = {k: np.array(v) for k, v in snap["boot"].items()}
    M["groups"] = {}
    for d in D:
        M["groups"].setdefault(d["group"], []).append(d["idx"])
    M["groups"]["fullcost_target"] = sorted(i for g_ in FULLCOST_TARGET for i in M["groups"].get(g_, []))
    return M


def dim_value(d, u, stratum=None):
    """Physical value of dimension d at unit coordinate u (NaN = the central value / point estimate)."""
    law = d["law"]
    if law == "uniform":
        if u != u:
            return d["central"]
        return d["lo"] if u == 0.0 else (d["hi"] if u == 1.0 else d["lo"] + u * (d["hi"] - d["lo"]))
    if law == "loguniform":                            # lo (hi/lo)^u; the ends exactly, the central value at NaN
        if u != u:
            return d["central"]
        return d["lo"] if u == 0.0 else (d["hi"] if u == 1.0 else d["lo"] * (d["hi"] / d["lo"]) ** u)
    if law.startswith("boot:"):
        ser = law[5:]
        if ser == "m0A":
            if u != u:
                return d["central"][stratum]
            arr = _M["boot_sorted"][stratum]
        else:
            if u != u:
                return d["central"]
            arr = _M["boot_sorted"][ser]
        p = 0.05 + 0.9 * u
        return float(np.interp(p * (len(arr) - 1), np.arange(len(arr)), arr))
    if law.startswith("iqr:"):
        if d["name"] == "m0A":
            lo, cen, hi = d["lo"][stratum], d["central"][stratum], d["hi"][stratum]
        else:
            lo, cen, hi = d["lo"], d["central"], d["hi"]
        if u != u:
            return cen
        return lo if u == 0.0 else (hi if u == 1.0 else lo + u * (hi - lo))
    raise ValueError(law)


def dim_unit(d, x):
    """Unit coordinate of the physical value x of a uniform or log-uniform dimension (the inverse of dim_value)."""
    if d["law"] == "uniform":
        return (x - d["lo"]) / (d["hi"] - d["lo"])
    if d["law"] == "loguniform":
        return math.log(x / d["lo"]) / math.log(d["hi"] / d["lo"])
    raise ValueError("dim_unit: no inverse for law %s" % d["law"])


def assemble(u):
    M = _M
    D, ix = M["dims"], M["idx"]

    def val(nm, s=None):
        return dim_value(D[ix[nm]], u[ix[nm]], s)
    v = dict(M["fc_central"])
    for k_ in M["fc_keys"]:
        v[k_] = val(k_)
    sL = val("s_L")
    v["A_auto"] = sL
    cc = {}
    if M["opts"]["cc_mode"] == "path":
        cp = M["snap"]["CC_PATH"]
        k25, Dd, kf = val("kappa_2025"), val("D"), val("kappa_front")
        for h in ("prices2025",) + HZ:
            om = val("omega_" + h) if h != "prices2025" else 0.0
            x = cc_path_v(h, sL, k25, Dd, kf, om, cp["floor_share"])
            cc[h] = M["cc_central"][h] * (x / M["cc_drv_central"][h])   # path drivers rescaled to the rounded centrals
    else:
        cc["prices2025"] = val("cc_2025")
        for h in HZ:
            cc[h] = val("cc_" + h)
    pace = dict(M["pace_central"])
    for k_ in M["pace_keys"]:
        pace[k_] = val(k_)
    G = val("G")
    P = dict(v=v, cc=cc, pace=pace, phi=val("phi"), k_pre=val("k_pre"), psi=val("psi"), alpha=val("alpha"),
             G={h: G for h in HZ}, mu={h: val("mu_" + h) for h in HZ}, r=val("r"), Pi_ub=val("Pi_ub"), bM=val("b_M"),
             m0A={s: val("m0A", s) for s in STRATA})
    return P


PARTS_ALL = frozenset(["gstar", "path", "pathA", "pathB", "pt0", "pb", "pbA", "pbB", "lev", "boot"])


def _nn(x):
    return float("nan") if x is None else float(x)


def _pb_record(pb, prefix, out, dM_min):
    out[prefix + "dM_min"] = dM_min                  # domain of the payback claims: the target lies above the anchor
    cross = _nn(pb["cross_flow"])
    pb_u = float("inf") if pb["payback_undiscounted"] is None else pb["payback_undiscounted"]
    pb_d = float("inf") if pb["payback_discounted"] is None else pb["payback_discounted"]
    comp = _nn(pb["complete_years"])
    cross_eff = cross if cross == cross else comp
    h = pb["hold"]
    out[prefix + "cross"] = cross
    out[prefix + "pb_u"] = pb_u
    out[prefix + "pb_d"] = pb_d
    out[prefix + "ratio"] = pb["ratio"]
    out[prefix + "npv"] = pb["npv_points_years"]
    out[prefix + "cum3"], out[prefix + "cum5"] = h[3]["cum"], h[5]["cum"]
    out[prefix + "cumd3"], out[prefix + "cumd5"] = h[3]["cum_disc"], h[5]["cum_disc"]
    out[prefix + "hold_max"] = max(h[3]["cum"], h[5]["cum"], h[3]["cum_disc"], h[5]["cum_disc"])
    out[prefix + "gap"] = pb_u - cross_eff if cross_eff == cross_eff else float("nan")
    out[prefix + "complete"] = comp


def _path_record(cp, prefix, out):
    for h in HZ:
        out[prefix + "R_" + h] = cp[h]["R"]
    out[prefix + "R_pathmax"] = max(cp[h]["R"] for h in HZ)
    out[prefix + "rise_min"] = min(cp["2031"]["R"] - cp["2028"]["R"], cp["2036"]["R"] - cp["2031"]["R"])
    out[prefix + "gap_2036"] = cp["2036"]["target"] - cp["2036"]["m0"]
    out[prefix + "completed_2036"] = cp["2036"]["target"] + (1 - cp["k"]) * cp["2036"]["G"]


def evaluate(u, parts=PARTS_ALL, strata=STRATA, rep=-1):
    """All claim quantities at the unit point u (NaN entries = central). Keys: '<stratum>.<quantity>' and
    stratum-free quantities. 'A.' = fixed prices and k = 0; 'B.' = central execution, fixed prices, k = 0."""
    M = _M
    P = assemble(u)
    v, cc = P["v"], P["cc"]
    tau_a = M["snap"]["TAU"]
    ceil = {h: fullcost_v(v, cc[h]) for h in ("prices2025",) + HZ}
    ceil_h = {h: ceil[h] for h in HZ}
    out = {}
    if "gstar" in parts:
        out["Gstar_2025"] = ceil["prices2025"]["G100"]
        out["Gstar_2025_cc6"] = fullcost_v(v, M["cc_central"]["prices2025"])["G100"]
        for h in HZ:
            out["Gstar_" + h] = ceil[h]["G100"]
        out["Gstar_hmin"] = min(ceil[h]["G100"] for h in HZ)
        out["c_c_2025"], out["c_c_2036"] = cc["prices2025"], cc["2036"]
        out["pull_multiple"] = pull_multiple_v(P["alpha"], M["snap"]["Pi_ub"][2])
    pace_p, pace_c = P["pace"], M["pace_central"]
    path_parts = parts & {"path", "pathA", "pathB", "pt0", "pb", "pbA", "pbB", "boot"}
    if path_parts:
        P0 = pace_v(pace_p, {y: 0.0 for y in YEARS})
        out["s_2036"] = P0[2036]["s"]
        out["s_2028"], out["s_2031"] = P0[2028]["s"], P0[2031]["s"]
        out["E_2036"] = P0[2036]["s"] / pace_p["bbar"]
        out["complete_year"] = P0["complete_year"]
        out["binding_change"] = float(P0["binding"] == "change")
    for s in strata:
        m0A = P["m0A"][s]
        Pi25 = max(P["Pi_ub"], 0.0) if s == "ub" else 0.0
        pre = s + "."
        if "gstar" in parts:
            gp = [1 - pt_margin_v(ceil[h], P["phi"], m0A) for h in ("prices2025",) + HZ]
            g0 = [1 - pt_margin_v(ceil[h], 0.0, m0A) for h in ("prices2025",) + HZ]
            out[pre + "Gstar_2025_phi"] = gp[0]
            out[pre + "pt_raise_min"] = min(a_ - b_ for a_, b_ in zip(gp, g0))
        cp = cpA = None
        if parts & {"path", "pt0", "pb"}:
            cp = central_path_v(m0A, Pi25, ceil_h, pace_p, P["phi"], P["k_pre"], P["psi"], P["G"], P["mu"], P["alpha"], tau_a)
            _path_record(cp, pre, out)
            for h in HZ:
                out[pre + "m0_" + h] = cp[h]["m0"]
                out[pre + "target_" + h] = cp[h]["target"]
                out[pre + "dip_" + h] = cp[h]["dip"] if cp[h]["running"] else 0.0
        if "pt0" in parts:
            cp0 = central_path_v(m0A, Pi25, ceil_h, pace_p, 0.0, P["k_pre"], P["psi"], P["G"], P["mu"], P["alpha"], tau_a)
            out[pre + "pt_lower_min"] = min(cp0[h]["R"] - cp[h]["R"] for h in HZ)
        if parts & {"pathA", "pbA", "pbB"}:
            cpA = central_path_v(m0A, Pi25, ceil_h, pace_p, 0.0, 0.0, 0.0, P["G"], P["mu"], P["alpha"], tau_a)
            _path_record(cpA, pre + "A.", out)
        if "pathB" in parts:
            cpB = central_path_v(m0A, Pi25, ceil_h, pace_c, 0.0, 0.0, 0.0, P["G"], P["mu"], P["alpha"], tau_a)
            _path_record(cpB, pre + "B.", out)
        if "pb" in parts:
            _pb_record(payback_v(m0A, {h: cp[h]["target"] for h in HZ}, pace_p, P["r"]), pre + "pb.", out,
                       min(cp[h]["target"] - m0A for h in HZ))
        if parts & {"pbA", "pbB"}:
            dmA = min(cpA[h]["target"] - m0A for h in HZ)
        if "pbA" in parts:
            _pb_record(payback_v(m0A, {h: cpA[h]["target"] for h in HZ}, pace_p, P["r"]), pre + "A.pb.", out, dmA)
        if "pbB" in parts:
            _pb_record(payback_v(m0A, {h: cpA[h]["target"] for h in HZ}, pace_c, P["r"]), pre + "B.pb.", out, dmA)
        if "boot" in parts and rep >= 0:
            m0r = M["boot_raw"][s][rep]
            cpr = central_path_v(m0r, Pi25, ceil_h, pace_p, P["phi"], P["k_pre"], P["psi"], P["G"], P["mu"], P["alpha"], tau_a)
            for h in HZ:
                out[pre + "boot.R_" + h] = cpr[h]["R"]
        if "lev" in parts:
            lv = levers_v(M["snap"]["positions"], P["bM"], P["phi"], P["alpha"], s)
            for k_, v_ in lv.items():
                out["lev." + pre + k_] = v_
    if ("path" in parts or "pathA" in parts) and len(strata) == 3:
        for pre in ("", "A."):
            ks = [s + "." + pre + "R_" + h for s in STRATA for h in HZ]
            if all(k_ in out for k_ in ks):
                out[pre + "basis_order"] = min(min(out["net." + pre + "R_" + h] - out["lb." + pre + "R_" + h],
                                                   out["ub." + pre + "R_" + h] - out["net." + pre + "R_" + h]) for h in HZ)
    return out


def eval_sobol(u):
    r = evaluate(u, parts=frozenset(["gstar", "path"]), strata=("net",))
    return [r["net.R_2028"], r["net.R_2031"], r["net.R_2036"], r["Gstar_2025"]]


SOBOL_OUTPUTS = ["net.R_2028", "net.R_2031", "net.R_2036", "Gstar_2025"]


# ---- pool tasks (top-level functions: spawn-safe)
def _own_maxrss_mb():
    """Peak resident memory of this process in MB: VmHWM of /proc/self/status on Linux (ru_maxrss would include the
    parent's pages copied at the fork that precedes exec in the spawn start method), else ru_maxrss."""
    try:
        with open("/proc/self/status") as fh:
            for line in fh:
                if line.startswith("VmHWM:"):
                    return float(line.split()[1]) / 1024.0
    except OSError:
        pass
    if resource is None:
        return float("nan")
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024.0 * 1024.0 if sys.platform == "darwin" else 1024.0)


def task_draws(args):
    i0, U, reps = args
    recs = [evaluate(U[i], rep=int(reps[i])) for i in range(U.shape[0])]
    keys = sorted(recs[0])
    return i0, {k_: np.array([r_.get(k_, np.nan) for r_ in recs], dtype=float) for k_ in keys}, _own_maxrss_mb()


def task_sobol(args):
    tag, i0, U = args
    return tag, i0, np.array([eval_sobol(U[i]) for i in range(U.shape[0])], dtype=float), _own_maxrss_mb()


def task_search(args):
    sid, key, sign, free, starts, budget, seed, parts, strata, domain = args
    f = _Objective(key, sign, frozenset(parts), tuple(strata), domain)
    x, fx, n, oat = vertex_search(f, _M["k"], free, starts, np.random.default_rng(seed), budget)
    return sid, dict(u=[None if v_ != v_ else float(v_) for v_ in x], f=float(fx), n=n,
                     value=float(sign * fx) if math.isfinite(fx) else None, oat=oat, maxrss_mb=_own_maxrss_mb())


def task_scan(args):
    sid, key, j, ref, grid, parts, strata, domain = args
    out = []
    for gv in grid:
        y = np.array(ref, dtype=float)
        y[j] = gv
        r = evaluate(y, parts=frozenset(parts), strata=tuple(strata))
        out.append([float(r[key]), float(r[domain]) if domain else 1.0])
    return sid, out


def task_eval_points(args):
    sid, pts, parts, strata = args
    return sid, [evaluate(np.array(p, dtype=float), parts=frozenset(parts), strata=tuple(strata)) for p in pts]


class _Objective(object):
    """sign x quantity at u; +inf outside the claim's domain or where the quantity is undefined."""
    def __init__(self, key, sign, parts, strata, domain=None):
        self.key, self.sign, self.parts, self.strata, self.domain = key, sign, parts, strata, domain

    def __call__(self, u):
        r = evaluate(u, parts=self.parts, strata=self.strata)
        if self.domain and not r[self.domain] > 0:
            return float("inf")
        val = r[self.key]
        return self.sign * val if val == val else float("inf")


def vertex_search(f, k, free, starts, rng, budget):
    """Minimize f over the box: one-at-a-time ends at the centre give each free dimension's direction; start from the
    resulting vertex and from the given points, flip single coordinates while that improves f (greedy vertex
    search), then try interior values (central, 1/4, 1/2, 3/4) per coordinate and repeat the flips once."""
    n = [0]

    def F(x):
        n[0] += 1
        return f(x)
    centre = np.full(k, np.nan)
    f_c = F(centre)
    oat = {}
    v = centre.copy()
    for j in free:
        a = centre.copy()
        a[j] = 0.0
        b = centre.copy()
        b[j] = 1.0
        fa, fb = F(a), F(b)
        oat[int(j)] = (fa, fb)
        v[j] = 0.0 if fa <= fb else 1.0
    cands = [(F(v), v)] + [(F(np.array(s_, dtype=float)), np.array(s_, dtype=float)) for s_ in starts]
    cands.append((f_c, centre))
    fx, x = min(cands, key=lambda t: t[0])
    x = x.copy()

    def flips(x, fx):
        improved = True
        while improved and n[0] < budget:
            improved = False
            for j in rng.permutation(free):
                cur = x[j]
                for val in ((1.0 - cur,) if cur in (0.0, 1.0) else (0.0, 1.0)):
                    y = x.copy()
                    y[j] = val
                    fy = F(y)
                    if fy < fx - 1e-15:
                        x, fx, improved = y, fy, True
                        break
                if n[0] >= budget:
                    break
        return x, fx
    x, fx = flips(x, fx)
    for j in rng.permutation(free):
        if n[0] >= budget:
            break
        for val in (np.nan, 0.25, 0.5, 0.75):
            y = x.copy()
            y[j] = val
            fy = F(y)
            if fy < fx - 1e-15:
                x, fx = y, fy
    x, fx = flips(x, fx)
    oat_eff = {str(j): (None if not (math.isfinite(a) and math.isfinite(b)) else float(b - a)) for j, (a, b) in oat.items()}
    return x, fx, n[0], oat_eff


# ======================================================================================================================
# Claims: every headline claim of the abstract, introduction, Sections 7 and 8, the conclusion and the summary box that
# depends on calibrated parameters, with the exact test the text makes
# ======================================================================================================================
def _claims(snap):
    gb_hi = snap["G_BAND"][1]
    C = []

    def claim(cid, title, quote, where, tests):
        C.append(dict(id=cid, title=title, quote=quote, where=where, tests=tests))

    def T(tid, key, op, thr, text, variant="full", strata=None, kind="margin", domain=None, note=""):
        if domain is None and ".pb." in key:
            domain = key.rsplit(".pb.", 1)[0] + ".pb.dM_min"
        return dict(tid=tid, key=key, op=op, thr=thr, text=text, variant=variant, strata=strata, kind=kind,
                    domain=domain, note=note)
    claim("C1", "A cash-basis Rule of 100 needs market growth above about G*",
          "complete automation keeps a mature asset-light firm's cash score below 100 unless its market grows faster "
          "than 32.5% a year, with compute at 6% of revenue; that bound is 72 to 97 points for market growth of 5 to 30%",
          "abstract; Sec. 1; Sec. 7.2 'Three conclusions'; summary item 5; conclusion",
          [T("C1.cond", "Gstar_2025_cc6", ">", 0.30, "G* > 30% (ceiling below 100 for market growth up to 30%)", variant="C",
             note="the paper itself gives 22% for its favorable case (compute 3%), so this test is expected to fail there"),
           T("C1.full", "Gstar_2025", ">", 0.30, "G* > 30% with the compute share on its range"),
           T("C1.fav", "Gstar_2025", ">=", snap["G_fav"], "G* at least the favorable case's %.1f%%, the lowest threshold the paper "
             "states at 2025 prices" % (100 * snap["G_fav"])),
           T("C1.iqr", "Gstar_2025", ">", gb_hi, "G* above the upper quartile of 2023-25 growth (%.1f%%)" % (100 * gb_hi))])
    claim("C2", "Thresholds along the compute-share path stay above 30%",
          "Along a scenario path of the compute share it is 38, 34 and 32% in 2028, 2031 and 2036 (37.6, 34.2, 31.7), "
          "against 32.5% at 2025 prices",
          "Sec. 1; Sec. 7.2 'By horizon and with pass-through'",
          [T("C2.full", "Gstar_hmin", ">", 0.30, "min over 2028, 2031, 2036 of G* > 30%")])
    claim("C3", "Pass-through raises every threshold",
          "pass-through raises every threshold (36.2% at phi = 0.5, 38.3% at 0.7, against 32.5%)",
          "abstract; Sec. 7.2; conclusion",
          [T("C3.full", "{s}.pt_raise_min", ">=", 0.0, "G*(phi) - G*(0) >= 0 at 2025 prices and every horizon",
             strata=STRATA)])
    claim("P1", "No Rule of 100 on the central path",
          "No single input in the table lifts the 2036 central score to 100; the path is 46, 50 and 59 in 2028, 2031, 2036",
          "Sec. 7.3 'Sensitivity'; Sec. 1; conclusion",
          [T("P1.full", "{s}.R_pathmax", "<", 1.0, "max(R_2028, R_2031, R_2036) < 100", strata=STRATA),
           T("P1.A", "{s}.A.R_pathmax", "<", 1.0, "max over horizons < 100", variant="A", strata=STRATA)])
    claim("P2", "A completed program brings the durable score only to the target plus market growth",
          "Even a completed program would bring the durable score only to the target plus market growth, about 68 plus "
          "12.7 points in 2036", "Sec. 7.3 'Central path'",
          [T("P2a.full", "{s}.gap_2036", ">=", 0.0, "m0(2036) <= target m0F(2036)", strata=STRATA),
           T("P2b.full", "{s}.completed_2036", "<", 1.0, "target + (1-k)G in 2036 < 100", strata=STRATA),
           T("P2b.A", "{s}.A.completed_2036", "<", 1.0, "target + G in 2036 < 100", variant="A", strata=STRATA)])
    claim("P3", "The central firm has realized less than half of its program by 2036",
          "the central firm has realized less than half of its program by 2036 (41% realized, 61% embedded)",
          "Sec. 7.3 'Central path'; abstract; summary item 6",
          [T("P3.full", "s_2036", "<", 0.5, "realized share bbar E(2036) < 0.5",
             note="depends on the execution dimensions only; under central execution (the claim's condition) it is fixed at 0.41")])
    claim("P3b", "The program is still running in 2036",
          "Over the life of the program, which completes in 2042 ... while it is transforming the dip is 3.6 to 4.2 points",
          "Sec. 7.3 'Pace'",
          [T("P3b.full", "complete_year", ">", 2036.0, "expected completion date after 2036",
             note="depends on the execution dimensions only; under central execution it is fixed at 2042")])
    claim("P4", "The central path rises from 2028 to 2036",
          "as the intercept rises from 31 to 33, 38 and 46 points (score 46, 50, 59)", "Sec. 7.3 'Central path'",
          [T("P4.full", "{s}.rise_min", ">=", 0.0, "R_2028 <= R_2031 <= R_2036", strata=STRATA,
             note="omega and mu are drawn independently by horizon, so the box contains compute paths whose frontier share "
                  "rises over time (the paper's path falls: 0.6, 0.4, 0.25); such paths can lower the target between horizons"),
           T("P4.A", "{s}.A.rise_min", ">=", 0.0, "R_2028 <= R_2031 <= R_2036", variant="A", strata=STRATA)])
    claim("P5", "Pass-through lowers the path",
          "With pass-through of phi = 0.5 the central path is 45, 48 and 55 ... pass-through lowers only the target",
          "Sec. 7.3 'Central path'",
          [T("P5.full", "{s}.pt_lower_min", ">=", 0.0, "R_h(phi = 0) - R_h(phi) >= 0 at every horizon", strata=STRATA)])
    claim("P6", "Ordering across the S&M bases",
          "scores 59 [54, 62] (55 to 65 as none or all selling spend buys growth)", "abstract; Sec. 1; conclusion",
          [T("P6.full", "basis_order", ">=", 0.0, "R(no S&M) <= R(netted) <= R(all S&M) at every horizon"),
           T("P6.A", "A.basis_order", ">=", 0.0, "same, fixed prices and k = 0", variant="A")])
    claim("B1", "The flow crossing comes before payback",
          "Annual gains first exceed the costs of transitions in flight after about 4.0 years ... That flow crossing is "
          "not payback: the cumulative gains repay the cumulative dip only after 7.5 years", "Sec. 7.3 'Pace'; summary item 6",
          [T("B1.full", "{s}.pb.gap", ">", 0.0, "payback - flow crossing > 0", strata=STRATA),
           T("B1.B", "{s}.B.pb.gap", ">", 0.0, "payback - flow crossing > 0", variant="B", strata=STRATA)])
    claim("B2", "The program does not repay its transition costs within five years",
          "the program repays those costs only after 7.5 years (8.5 discounted) ... an owner with a horizon of five years "
          "or less would not fund the whole program under central execution", "Sec. 1; Sec. 7.3; Sec. 8.2; conclusion",
          [T("B2.full", "{s}.pb.pb_u", ">", 5.0, "undiscounted payback > 5 years", strata=STRATA),
           T("B2.A", "{s}.A.pb.pb_u", ">", 5.0, "undiscounted payback > 5 years", variant="A", strata=STRATA),
           T("B2.B", "{s}.B.pb.pb_u", ">", 5.0, "undiscounted payback > 5 years", variant="B", strata=STRATA)])
    claim("B3", "Cumulative effect negative at three and at five years",
          "at three and at five years its cumulative effect is still negative (-8.8 and -8.6 points of revenue times "
          "years; -7.8 discounted)", "Sec. 1; Sec. 7.3 'Pace'; summary item 6",
          [T("B3.full", "{s}.pb.hold_max", "<", 0.0, "max(cum3, cum5, NPV3, NPV5) < 0", strata=STRATA),
           T("B3.B", "{s}.B.pb.hold_max", "<", 0.0, "max(cum3, cum5, NPV3, NPV5) < 0", variant="B", strata=STRATA)])
    claim("B4", "Over its life the program is worth more than its transition costs",
          "gains are worth 3.9 times the dip in present value and the net present value is 98% of a year's revenue",
          "Sec. 7.3 'Pace'",
          [T("B4.full", "{s}.pb.ratio", ">", 1.0, "PV(gains) / PV(dip) > 1", strata=STRATA),
           T("B4.B", "{s}.B.pb.ratio", ">", 1.0, "PV(gains) / PV(dip) > 1", variant="B", strata=STRATA)])
    claim("R1", "A Rule of 1000 is not a steady state",
          "A Rule of 1000 is not a steady state: it requires 9 to 20 times the demand pull of today's best public "
          "software firms", "Sec. 1; Sec. 7.2 'Three conclusions'",
          [T("R1.full", "pull_multiple", ">", 1.0, "required demand pull / today's best > 1",
             note="varies with alpha only (the upper-quartile surplus is held at its point estimate, as in the code), so "
                  "the box range equals the paper's 9-20")])
    claim("L1", "The growth engine outranks the G&A cut at 1 of 6 positions on the netted basis",
          "cutting general and administrative cost outranks automating the growth engine at 5 of 6 positions; if all "
          "S&M buys growth the growth engine leads at 6 of 6, if none does at 0",
          "Sec. 7.4 (Table tab:levers-position, levers_position_macros.tex); Sec. 1; summary item 7; conclusion",
          [T("L1.full", "lev.{s}.n_ge_first", "==", {"net": 1.0, "ub": 6.0, "lb": 0.0},
             "count of positions with sigma > a_GA equals the stated count", strata=STRATA, kind="count",
             note="b_M is an estimate with a firm-cluster bootstrap (class c), not a scenario value: its draws follow the "
                  "bootstrap distribution, so the share of draws here is a bootstrap probability within the 90% interval, "
                  "not a uniform-law share")])
    claim("L2", "Engineering ranks above both levers at all six positions",
          "the companion paper, which also values research and development as a cost line, ranks engineering above both "
          "at all 6 positions on the central basis", "Sec. 7.4; summary item 7; conclusion",
          [T("L2.full", "lev.{s}.n_eng_above", "==", {"net": 6.0}, "count of positions with R&D > max(sigma, a_GA) = 6",
             strata=("net",), kind="count")])
    claim("L3", "Engineering is the first of the four levers at all six positions (companion-paper ranking)",
          "engineering first at 6 of 6 positions (ranking_by_basis: growth engine, G&A, R&D, cost of revenue at the "
          "revealed weight; cost of revenue at the drawn pass-through)", "notes/playbook_results.json ranking_by_basis",
          [T("L3.full", "lev.{s}.n_eng_first", "==", {"net": 6.0}, "count of positions where R&D ranks first = 6",
             strata=("net",), kind="count")])
    return C


def margin_of(op, q, thr):
    q = np.asarray(q, dtype=float)
    if op in (">", ">="):
        return q - thr
    if op in ("<", "<="):
        return thr - q
    if op == "==":
        return np.where(q == thr, 1.0, -1.0)
    raise ValueError(op)


def passes(op, m):
    m = np.asarray(m, dtype=float)
    if op in (">", "<", "=="):
        return m > 0
    return m >= -TOL


def parts_for(key):
    if key.startswith("Gstar") or ".Gstar" in key or "pt_raise" in key or key.startswith(("pull_multiple", "c_c_")):
        return ["gstar"]
    if ".B.pb." in key:
        return ["pbB"]
    if ".A.pb." in key:
        return ["pbA"]
    if ".pb." in key:
        return ["pb"]
    if ".B." in key:
        return ["pathB"]
    if ".A." in key or key.startswith("A."):
        return ["pathA"]
    if "pt_lower" in key:
        return ["path", "pt0"]
    if key.startswith("lev."):
        return ["lev"]
    return ["path"]


def strata_for(key):
    s = key.split(".")[1] if key.startswith("lev.") else key.split(".")[0]
    if s in STRATA:
        return [s]
    if "basis_order" in key:
        return list(STRATA)
    return ["net"]


# ======================================================================================================================
# Reproduction of the paper at the centre of the box
# ======================================================================================================================
def read_macros():
    M = {}
    for rel in ("paper1/macros.tex", "sections/tables/levers_position_macros.tex"):
        for line in open(os.path.join(REPO, rel)):
            m = re.match(r"\\newcommand\{\\(\w+)\}\{(.*)\}\s*$", line)
            if m:
                M[m.group(1)] = m.group(2)
    return M


def half_up(x, nd=0):
    q = 10 ** nd
    return math.floor(x * q + 0.5) / q


def _macro_check(checks, macros, name, x, pct=True):
    txt = macros[name]
    s = txt.replace("$-$", "-")
    nd = len(s.split(".")[1]) if "." in s else 0
    got = half_up(100 * x if pct else x, nd)
    ok = abs(got - float(s)) < 1e-9
    checks.append(dict(check="macro \\" + name, expected=txt, got=("%." + str(nd) + "f") % got, ok=bool(ok)))


def _eq_check(checks, name, got, want, tol=1e-12):
    ok = abs(got - want) <= tol * max(1.0, abs(want))
    checks.append(dict(check=name, expected=repr(float(want)), got=repr(float(got)), ok=bool(ok)))


def verify_mirror(g, snap, opts):
    """Mirror functions against the executed code/calibrate_horizons.py (same process, exact equality)."""
    checks = []
    init_worker(snap, opts)
    FC = g["FC"]
    for case, i in (("favorable", 0), ("central", 1), ("conservative", 2), ("high compute", 1)):
        v = {k: val[i] for k, val in FC.items()}
        for h in ("prices2025",) + HZ:
            cc = g["CC_HIGH"] if case == "high compute" else g["CC_CASES"][h][i]
            mine, orig = fullcost_v(v, cc), g["fullcost"](case, h)
            for key in ("base", "G100", "c_full", "c_err", "c_sec", "c_mnt", "c_anc", "base_acc"):
                assert mine[key] == orig[key], ("fullcost mirror", case, h, key)
    checks.append(dict(check="fullcost_v == fullcost (4 cases x 4 horizons, 8 fields, exact)", ok=True))
    for c in g["CASES"]:
        for phi in g["PHI"]:
            assert pt_margin_v(g["CEIL"][c], phi, g["PT_M0A"]) == g["base_phi"](g["CEIL"][c], phi)
    checks.append(dict(check="pt_margin_v == base_phi (all ceiling cases x phi, exact)", ok=True))
    for nm, p in list(g["PACE"].items()) + [("bcg", g["PACE_BCG_WIN"])] + [("prev_" + k, v) for k, v in g["PACE_PREVIOUS"].items()]:
        for dM in (g["dM_lo"], g["dM_hi"], g["dM_c"]):
            a, b = pace_v(p, dM), g["pace"](p, dM)
            for y in YEARS:
                assert a[y] == {k: b[y][k] for k in a[y]}, ("pace mirror", nm, y)
            assert a["complete_year"] == b["complete_year"] and a["cross_years"] == b["cross_years"]
    checks.append(dict(check="pace_v == pace (all pace cases incl. pre-commit and BCG win, 3 dM paths, exact)", ok=True))
    ceil_c = {h: g["CEIL_H"][h]["central"] for h in HZ}
    tau_a = g["TAU"]

    def cp_mirror(anc=None, bound="net", q=1, pace_case="central", target_case="central", phi=0.0, k_pre=0.0, psi=0.0,
                  G=None, mu=None, alpha=None, pi_q=None, pace_params=None, m0A=None):
        anc = g["anchor"] if anc is None else anc
        m0A_ = anc["m0_" + bound][q] if m0A is None else m0A
        Pi25 = max(anc["Pi_ub"][q if pi_q is None else pi_q], 0.0) if bound == "ub" else 0.0
        G_ = {h: g["CEN"][h]["G"] for h in HZ} if G is None else G
        mu_ = {h: g["CEN"][h]["mu"] for h in HZ} if mu is None else mu
        pp = g["PACE"][pace_case] if pace_params is None else pace_params
        return central_path_v(m0A_, Pi25, {h: g["CEIL_H"][h][target_case] for h in HZ}, pp, phi, k_pre, psi, G_, mu_,
                              g["ALPHA_C"] if alpha is None else alpha, tau_a)
    n_cp = 0
    for key, lab, klo, khi in g["TORNADO_ITEMS"]:
        for kw in (klo, khi):
            a, b = cp_mirror(**kw), g["central_path"](**kw)
            for h in HZ:
                for f_ in ("R", "m0", "target", "s", "dip", "Pi"):
                    assert a[h][f_] == b[h][f_], ("central_path mirror", key, kw, h, f_)
            n_cp += 1
    for b_ in g["BASES3"]:
        for phi in g["PHI"]:
            a, b = cp_mirror(bound=b_, phi=phi), g["central_path"](bound=b_, phi=phi)
            assert all(a[h]["R"] == b[h]["R"] for h in HZ)
            n_cp += 1
    checks.append(dict(check="central_path_v == central_path (%d cases: every tornado item, every basis x phi, exact)" % n_cp, ok=True))
    for pc in ("slow", "central", "fast"):
        a = payback_v(g["central_path"](pace_case=pc)["m0A"], {h: g["central_path"](pace_case=pc)[h]["target"] for h in HZ},
                      g["PACE"][pc], g["R_WACC"])
        b = g["R2"]["payback"][pc]
        for f_ in ("cross_flow", "payback_undiscounted", "payback_discounted", "ratio", "npv_points_years", "complete_years"):
            assert a[f_] == b[f_], ("payback mirror", pc, f_)
        assert all(a["hold"][y] == b["hold"][y] for y in a["hold"])
    a = payback_v(g["CPc"]["m0A"], {h: g["CPc"][h]["target"] for h in HZ}, g["PACE"]["central"], 0.10)
    assert a["ratio"] == g["R2"]["payback"]["central_r10"]["ratio"]
    checks.append(dict(check="payback_v == payback (slow, central, fast, central at r = 10%, exact)", ok=True))
    for h in HZ:
        assert abs(g["cc_path"](h) - _M["cc_drv_central"][h]) == 0.0
    checks.append(dict(check="cc_path_v == cc_path (2028, 2031, 2036, exact)", ok=True))
    return checks


def reproduce_paper(snap, opts, g=None):
    """Assert, at the centre of the box, the paper's central values against notes/calibration_results.json and the
    macros (before any sampling)."""
    init_worker(snap, opts)
    CAL = json.load(open(os.path.join(REPO, "notes", "calibration_results.json")))
    macros = read_macros()
    checks = []
    c = evaluate(np.full(_M["k"], np.nan))
    path = CAL["central_path"]["path"]
    _eq_check(checks, "R_2036 netted == calibration_results.json central_path.path.net.2036.R", c["net.R_2036"], path["net"]["2036"]["R"])
    _eq_check(checks, "G* (2025 prices) == calibration_results.json ceiling.central.G100", c["Gstar_2025"], CAL["ceiling"]["central"]["G100"])
    for s, tag in (("net", ""), ("ub", "AllSM"), ("lb", "NoSM")):
        for h, yn in (("2028", "Eight"), ("2031", "One"), ("2036", "Six")):
            _eq_check(checks, "R_%s %s == JSON" % (h, s), c[s + ".R_" + h], path[s][h]["R"])
            _macro_check(checks, macros, "CenR" + yn + tag, c[s + ".R_" + h])
    _macro_check(checks, macros, "CenTargetSix", c["net.target_2036"])
    _macro_check(checks, macros, "CenMzeroSix", c["net.m0_2036"])
    _macro_check(checks, macros, "CenDipEight", c["net.dip_2028"])
    _macro_check(checks, macros, "CenDipSix", c["net.dip_2036"])
    _macro_check(checks, macros, "PaceCenSix", c["s_2036"])
    _macro_check(checks, macros, "CenEmbSix", c["E_2036"])
    _macro_check(checks, macros, "GstarCenOne", c["Gstar_2025"])
    for h, yn in (("2028", "TwentyEight"), ("2031", "ThirtyOne"), ("2036", "ThirtySix")):
        _macro_check(checks, macros, "GstarCen" + yn + "One", c["Gstar_" + h])
    pb = CAL["r2"]["payback"]["central"]
    _eq_check(checks, "payback (central execution) == JSON r2.payback.central", c["net.B.pb.pb_u"], pb["payback_undiscounted"])
    for nm, key, pct in (("PayCrossCen", "net.B.pb.cross", False), ("PayBackCen", "net.B.pb.pb_u", False),
                         ("PayBackDiscCen", "net.B.pb.pb_d", False), ("PayRatioCen", "net.B.pb.ratio", False),
                         ("PayNpvCen", "net.B.pb.npv", True), ("PayHoldThreeCen", "net.B.pb.cum3", True),
                         ("PayHoldFiveCen", "net.B.pb.cum5", True), ("PayHoldFiveDiscCen", "net.B.pb.cumd5", True)):
        _macro_check(checks, macros, nm, c[key], pct=pct)
    done = str(int(math.floor(2025 + c["net.B.pb.complete"] + 0.5)))
    checks.append(dict(check="macro \\PayDoneCen", expected=macros["PayDoneCen"], got=done, ok=done == macros["PayDoneCen"]))
    assert c["net.pb.pb_u"] == c["net.B.pb.pb_u"] and c["net.R_2036"] == c["net.A.R_2036"] == c["net.B.R_2036"]
    # pass-through thresholds at the central structure (saving of the netted anchor)
    for phi, nm in ((0.5, "GstarPhiHalfOne"), (0.7, "GstarPhiSevenOne")):
        val = 1 - pt_margin_v(fullcost_v(_M["fc_central"], _M["cc_central"]["prices2025"]), phi, snap["anchor"]["net"][1])
        _eq_check(checks, "G*(phi=%.1f) == JSON pass_through" % phi, val, CAL["pass_through"]["%.1f" % phi]["ceiling"]["central"]["G100"])
        _macro_check(checks, macros, nm, val)
    for phi, tag in ((0.5, "Half"), (0.7, "Seven")):
        u = np.full(_M["k"], np.nan)
        d_ = _M["dims"][_M["idx"]["phi"]]
        u[_M["idx"]["phi"]] = dim_unit(d_, phi)
        r_ = evaluate(u, parts=frozenset(["path"]))
        for h, yn in (("2028", "Eight"), ("2031", "One"), ("2036", "Six")):
            _eq_check(checks, "R_%s phi=%.1f == JSON" % (h, phi), r_["net.R_" + h], CAL["central_path"]["pass_through"]["%.1f" % phi]["net"][h]["R"], tol=1e-12)
    for a_, nm in ((snap["ALPHAS"][0], "PullMultHi"), (snap["ALPHAS"][1], "PullMultLo")):
        _macro_check(checks, macros, nm, pull_multiple_v(a_, snap["Pi_ub"][2]), pct=False)
    # levers
    pos = snap["positions"]
    lv = {s: levers_v(pos, snap["MAINT_BASE"], 0.0, 0.3, s) for s in STRATA}
    for s, nm in (("net", "lpNGEFirstNet"), ("ub", "lpNGEFirstAllSM"), ("lb", "lpNGEFirstNoSM")):
        checks.append(dict(check="macro \\" + nm, expected=macros[nm], got=str(int(lv[s]["n_ge_first"])),
                           ok=str(int(lv[s]["n_ge_first"])) == macros[nm]))
        assert c["lev." + s + ".n_ge_first"] == lv[s]["n_ge_first"]
    checks.append(dict(check="macro \\lpNGACutFirstNet", expected=macros["lpNGACutFirstNet"],
                       got=str(int(len(pos) - lv["net"]["n_ge_first"])), ok=str(int(len(pos) - lv["net"]["n_ge_first"])) == macros["lpNGACutFirstNet"]))
    for nm, x in (("lpRatioMin", lv["net"]["ratio_min"]), ("lpRatioMax", lv["net"]["ratio_max"]),
                  ("lpRatioAllSMMin", lv["ub"]["ratio_min"]), ("lpRatioAllSMMax", lv["ub"]["ratio_max"])):
        _macro_check(checks, macros, nm, x, pct=False)
    rb = snap["ranking_by_basis"]
    phi_e = pos[0]["phi_engine"]
    for s, b_ in (("net", "netted"), ("ub", "all"), ("lb", "none")):
        lvv = levers_v(pos, snap["MAINT_BASE"], phi_e, 0.3, s)
        checks.append(dict(check="ranking_by_basis n_eng_first_%s (engine phi = %.2f)" % (b_, phi_e),
                           expected=str(rb["n_eng_first_" + b_]), got=str(int(lvv["n_eng_first"])),
                           ok=int(lvv["n_eng_first"]) == rb["n_eng_first_" + b_]))
    checks.append(dict(check="text: engineering above both levers at all 6 positions (netted)", expected="6",
                       got=str(int(lv["net"]["n_eng_above"])), ok=int(lv["net"]["n_eng_above"]) == 6))
    # accountability floor
    A = snap["amin"]
    for t, nm, design in (("Five", "AminFloor", (1, 1)), ("One", "AminFloorOne", (1, 2))):
        e = A["eps"][t]
        b_ = amin_best_v(e, A)
        fl = (A["fee"] + A["kpmg_small"]) / A["REV"] + b_[0] / A["REV"]
        _macro_check(checks, macros, nm, fl)
        checks.append(dict(check="cheapest design at %g%%" % (100 * e), expected=str(design), got=str(b_[1:]), ok=b_[1:] == design))
        lo = (A["fee_lo"] + A["kpmg_small"]) / A["REV"] + b_[0] / A["REV"]
        hi = (A["fee_hi"] + A["kpmg_small"]) / A["REV"] + b_[0] / A["REV"]
        _macro_check(checks, macros, "AminFloorLo" + ("" if t == "Five" else t), lo)
        _macro_check(checks, macros, "AminFloorHi" + ("" if t == "Five" else t), hi)
    # tornado reproduced with the box's own dimensions where a tornado row is one dimension or one case
    T36 = {r["key"]: r for r in snap["tornado"]["2036"]}
    for key, dims_set in (("G", {"G": (0.0, 1.0)}), ("pass_through", {"phi": (1.0,)})):
        vals = []
        for uu in list(dims_set.values())[0]:
            u = np.full(_M["k"], np.nan)
            u[_M["idx"][list(dims_set)[0]]] = uu
            vals.append(evaluate(u, parts=frozenset(["path"]), strata=("net",))["net.R_2036"])
        if key == "pass_through":
            vals.append(c["net.R_2036"])
        _eq_check(checks, "tornado 2036 row '%s' low/high from the box" % key, min(vals), T36[key]["low"])
        _eq_check(checks, "tornado 2036 row '%s' high from the box" % key, max(vals), T36[key]["high"])
    # round 3 (3 Nov 2026): the compute share's ends in the box are the text's range, c_c = s_L x kappa (one range for the
    # text, the calibration and the box), and the log-uniform law inverts exactly at the central kappa
    CCR = CAL["r3"]["compute_credible"]
    sL_c = snap["CC_PATH"]["s_L"]
    if "kappa_2025" in _M["idx"]:
        dk = _M["dims"][_M["idx"]["kappa_2025"]]
        k_ends = (dim_value(dk, 0.0), dim_value(dk, 1.0))
        checks.append(dict(check="kappa_2025 box ends == calibration r3.compute_credible kappa_lo, kappa_hi",
                           expected=repr((CCR["kappa_lo"], CCR["kappa_hi"])), got=repr(k_ends),
                           ok=bool(k_ends == (CCR["kappa_lo"], CCR["kappa_hi"]))))
        _macro_check(checks, macros, "KappaLo", k_ends[0])
        _macro_check(checks, macros, "CcLo", sL_c * k_ends[0])
        _macro_check(checks, macros, "CcHi", sL_c * k_ends[1])
        _eq_check(checks, "kappa_2025 law (%s): dim_value(dim_unit(central)) == central" % dk["law"],
                  dim_value(dk, dim_unit(dk, dk["central"])), dk["central"])
    else:
        dc = _M["dims"][_M["idx"]["cc_2025"]]
        checks.append(dict(check="cc_2025 box ends == calibration r3.compute_credible lo, hi", expected=repr((CCR["lo"], CCR["hi"])),
                           got=repr((dc["lo"], dc["hi"])), ok=bool((dc["lo"], dc["hi"]) == (CCR["lo"], CCR["hi"]))))
        _macro_check(checks, macros, "CcLo", dc["lo"])
        _macro_check(checks, macros, "CcHi", dc["hi"])
    ok = all(ch["ok"] for ch in checks)
    if g is not None:
        checks = verify_mirror(g, snap, opts) + checks
        init_worker(snap, opts)
    return checks, ok


# ======================================================================================================================
# Designs
# ======================================================================================================================
def lhs(n, k, rng):
    U = np.empty((n, k))
    for j in range(k):
        U[:, j] = (rng.permutation(n) + rng.random(n)) / n
    return U


def corner_design(k, n_random, rng):
    rows = [np.zeros(k), np.ones(k)]
    labels = ["all-low", "all-high"]
    if k <= 14:
        for i in range(2 ** k):
            rows.append(np.array([(i >> j) & 1 for j in range(k)], dtype=float))
            labels.append("vertex")
        return np.array(rows[2:]), labels[2:]
    R = rng.integers(0, 2, size=(n_random, k)).astype(float)
    return np.vstack([np.array(rows), R]), labels + ["random vertex"] * n_random


def qmc_base(n, d, seed):
    try:
        from scipy.stats import qmc
        try:
            eng = qmc.Sobol(d=d, scramble=True, rng=seed)
        except TypeError:
            eng = qmc.Sobol(d=d, scramble=True, seed=seed)
        m = int(round(math.log2(n)))
        if 2 ** m == n:
            return eng.random_base2(m), "scrambled Sobol sequence (scipy.stats.qmc)"
        return eng.random(n), "scrambled Sobol sequence (scipy.stats.qmc)"
    except Exception:                                  # scipy missing or too old: plain Monte Carlo
        return np.random.default_rng(seed).random((n, d)), "pseudo-random (numpy)"


def config_hash(args, dims, snap):
    """Checkpoint key: run options, the box, the calibration snapshot and the source of every function that changes
    results (so a resumed run never mixes outputs of different code or inputs)."""
    import inspect
    fns = (fullcost_v, pt_margin_v, rates_v, pace_v, pi_scaled_v, central_path_v, payback_v, pull_multiple_v, cc_path_v,
           growth_spend_v, levers_v, build_dims, dim_value, assemble, evaluate, _pb_record, _path_record, eval_sobol,
           vertex_search, lhs, corner_design, qmc_base, _claims, parts_for, strata_for)
    src = "".join(inspect.getsource(f) for f in fns)
    d = dict(v=VERSION, n=args.n, seed=args.seed, corners=args.corners, cc=args.cc_mode, bcg=args.bcg_win,
             anchor=args.anchor_range, sobol_n=args.sobol_n, amin_n=args.amin_n, budget=args.search_budget,
             dims=[(x["name"], repr(x["lo"]), repr(x["central"]), repr(x["hi"]), x["law"]) for x in dims],
             src=hashlib.sha256(src.encode()).hexdigest(),
             snap=hashlib.sha256(json.dumps(snap, sort_keys=True, default=str).encode()).hexdigest())
    return hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()[:12]


def _atomic_save_npz(path, **arrs):
    tmp = path + ".tmp.npz"
    np.savez(tmp, **arrs)
    os.replace(tmp, path)


def _atomic_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(obj, fh, indent=1, default=_json_default)
    os.replace(tmp, path)


def _json_default(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    return str(o)


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating,)):
        o = float(o)
    if isinstance(o, float):
        return None if not math.isfinite(o) else o
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


# ======================================================================================================================
# Analysis helpers: failure regions (shallow tree, univariate scans), Sobol estimators
# ======================================================================================================================
def tree_rules(U, fail, max_depth=2, min_leaf=None, features=None):
    """Shallow classification tree (Gini) on unit coordinates; returns the leaves with their paths."""
    n, k = U.shape
    features = list(range(k)) if features is None else list(features)
    min_leaf = max(10, int(0.02 * n)) if min_leaf is None else min_leaf
    y = fail.astype(float)

    def gini(p):
        return 2 * p * (1 - p)

    def best_split(idx):
        best = None
        ys = y[idx]
        nn = len(idx)
        if nn < 2 * min_leaf or ys.min() == ys.max():
            return None
        base = gini(ys.mean())
        for j in features:
            x = U[idx, j]
            o = np.argsort(x, kind="mergesort")
            xs, yo = x[o], ys[o]
            cum = np.cumsum(yo)
            pos = np.arange(min_leaf, nn - min_leaf + 1)
            if len(pos) == 0:
                continue
            pos = pos[xs[pos - 1] < xs[np.minimum(pos, nn - 1)]]
            if len(pos) == 0:
                continue
            nl = pos.astype(float)
            fl = cum[pos - 1]
            nr = nn - nl
            fr = cum[-1] - fl
            imp = (nl * gini(fl / nl) + nr * gini(fr / nr)) / nn
            i = int(np.argmin(imp))
            if best is None or imp[i] < best[2] - 1e-12:
                best = (j, float((xs[pos[i] - 1] + xs[pos[i]]) / 2), float(imp[i]), base)
        if best is None or best[2] >= best[3] - 1e-9:
            return None
        return best

    leaves = []

    def grow(idx, path, depth):
        sp = best_split(idx) if depth < max_depth else None
        if sp is None:
            leaves.append(dict(path=path, n=int(len(idx)), n_fail=int(y[idx].sum()), fail_share=float(y[idx].mean())))
            return
        j, t = sp[0], sp[1]
        L, R = idx[U[idx, j] <= t], idx[U[idx, j] > t]
        grow(L, path + [(j, "<=", t)], depth + 1)
        grow(R, path + [(j, ">", t)], depth + 1)
    grow(np.arange(n), [], 0)
    return leaves


def sobol_indices(fA, fB, fAB, n_boot=200, seed=0):
    """Saltelli (2010) first-order and Jansen (1999) total indices with bootstrap 95% intervals."""
    rng = np.random.default_rng(seed)
    N = len(fA)

    def est(ix):
        a, b, ab = fA[ix], fB[ix], fAB[ix]
        V = np.var(np.concatenate([a, b]))
        if V <= 0:
            return 0.0, 0.0
        return float(np.mean(b * (ab - a)) / V), float(0.5 * np.mean((a - ab) ** 2) / V)
    s1, st = est(np.arange(N))
    bs = np.array([est(rng.integers(0, N, N)) for _ in range(n_boot)])
    return dict(S1=s1, ST=st, S1_ci=[float(np.quantile(bs[:, 0], 0.025)), float(np.quantile(bs[:, 0], 0.975))],
                ST_ci=[float(np.quantile(bs[:, 1], 0.025)), float(np.quantile(bs[:, 1], 0.975))])


def physical(dims, u, stratum="net"):
    out = {}
    for d in dims:
        x = u[d["idx"]]
        x = np.nan if x is None else x
        if d["name"] == "m0A":
            out[d["name"]] = {s: dim_value(d, x, s) for s in STRATA}
        else:
            out[d["name"]] = dim_value(d, x)
    return out


def fmt_val(d, val):
    if isinstance(val, dict):
        return "/".join(fmt_val(d, val[s]) for s in STRATA)
    if d["name"] in ("aic_fixed", "anc_fixed"):
        return "%.0fk" % (val / 1e3)
    if abs(val) >= 100:
        return "%.0f" % val
    if abs(val) >= 1:
        return "%.3g" % val
    return "%.4g" % val


def describe_point(dims, u, idx_list, stratum=None):
    parts = []
    for j in idx_list:
        d = dims[j]
        x = u[j]
        x = np.nan if x is None else x
        pos = "central" if x != x else ("low end" if x == 0 else ("high end" if x == 1 else "u=%.2f" % x))
        if d["name"] == "m0A":
            val = dim_value(d, x, stratum) if stratum else {s: dim_value(d, x, s) for s in STRATA}
        else:
            val = dim_value(d, x)
        parts.append("%s = %s (%s)" % (d["name"], fmt_val(d, val), pos))
    return "; ".join(parts)


# ======================================================================================================================
# Main
# ======================================================================================================================
def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=10000, help="Latin-hypercube draws (default 10,000)")
    ap.add_argument("--seed", type=int, default=20261102, help="seed of every random design (default 20261102); a second "
                    "seed checks that the results do not depend on the draws (see --compare-to)")
    ap.add_argument("--compare-to", default=None, metavar="DIR",
                    help="output folder (or mc_claims.json) of a run with another seed: its results are compared with this "
                         "run's and the comparison is recorded in this run's JSON (seed_comparison) and report")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1, help="worker processes (default: all cores)")
    ap.add_argument("--chunk", type=int, default=200, help="draws per task and per checkpoint file (default 200)")
    ap.add_argument("--corners", type=int, default=2048, help="random vertices of the box when k > 14 (default 2048)")
    ap.add_argument("--sobol-n", type=int, default=1024, help="Saltelli base sample N, a power of two (default 1024)")
    ap.add_argument("--sobol-backend", choices=("auto", "salib", "numpy"), default="auto")
    ap.add_argument("--amin-n", type=int, default=2000, help="LHS draws of the accountability-floor sub-box")
    ap.add_argument("--search-budget", type=int, default=600, help="model evaluations per extremum search")
    ap.add_argument("--cc-mode", choices=("path", "bounds"), default="path",
                    help="compute share from its path drivers (default) or from its stated bounds by horizon")
    ap.add_argument("--anchor-range", choices=("ci90", "iqr"), default="ci90",
                    help="anchor intercept: firm-cluster bootstrap within its 90%% interval (default) or the quartiles")
    ap.add_argument("--bcg-win", action="store_true", help="extend varpi down to 0.30 (the tornado's BCG win row)")
    ap.add_argument("--out", default=os.path.join(REPO, "notes", "mc"), help="output directory (default notes/mc/)")
    ap.add_argument("--fresh", action="store_true", help="discard the checkpoint of this configuration")
    ap.add_argument("--stop-after", choices=("draws", "search", "sobol"), default=None, help="stop after a phase")
    ap.add_argument("--no-sobol", action="store_true")
    ap.add_argument("--print-dims", action="store_true", help="print the dimension table (markdown) and exit")
    ap.add_argument("--verify-only", action="store_true", help="run the reproduction checks and exit")
    return ap.parse_args(argv)


def _log(msg):
    sys.stdout.write("[mc_claims %s] %s\n" % (time.strftime("%H:%M:%S"), msg))
    sys.stdout.flush()


def dims_markdown(dims):
    lines = ["| # | Dimension | Group | Low | Central | High | Law | Class | Source | Note |", "|---|---|---|---|---|---|---|---|---|---|"]
    for d in dims:
        def f(x):
            return fmt_val(d, x)
        law = {"uniform": "uniform", "loguniform": "log-uniform"}.get(
            d["law"], d["law"].replace("boot:", "bootstrap 5-95%: ").replace("iqr:", "uniform IQR: "))
        lines.append("| %d | `%s` %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            d["idx"] + 1, d["name"], d["label"], d["group"], f(d["lo"]), f(d["central"]), f(d["hi"]), law, d["cls"],
            d["src"], d["note"]))
    return "\n".join(lines)


class Runner(object):
    def __init__(self, args):
        self.args = args
        self.opts = dict(cc_mode=args.cc_mode, anchor_range=args.anchor_range, bcg_win=bool(args.bcg_win))
        self.out = os.path.abspath(args.out)
        self.timing = {}
        self.pool = None

    # ---------------------------------------------------------------- setup
    def setup(self):
        a = self.args
        os.makedirs(self.out, exist_ok=True)
        t = time.time()
        _log("executing %s into %s (outputs redirected)" % (CALIB, os.path.join(self.out, "_shadow")))
        g = load_calibration(os.path.join(self.out, "_shadow"))
        self.byte_identical = g["_mc_byte_identical"]
        self.json_diff = g["_mc_json_diff"]
        self.snap = build_snapshot(g)
        self.timing["calibration_load_s"] = time.time() - t
        self.checks, ok = reproduce_paper(self.snap, self.opts, g)
        self.tau_coupling = self._tau_coupling()
        del g
        gc.collect()
        self.dims = _M["dims"]
        self.k = len(self.dims)
        self.law_label = law_label(self.dims)
        self.claims = _claims(self.snap)
        self.cfg = config_hash(a, self.dims, self.snap)
        self.ck = os.path.join(self.out, "ckpt", self.cfg)
        if a.fresh and os.path.isdir(self.ck):
            shutil.rmtree(self.ck)
        os.makedirs(self.ck, exist_ok=True)
        tf = os.path.join(self.ck, "timing.json")
        self.prev_timing = json.load(open(tf)) if os.path.exists(tf) else {}
        n_bad = sum(not c["ok"] for c in self.checks)
        _log("reproduction checks: %d passed, %d failed; shadow outputs byte-identical: %s%s" % (
            len(self.checks) - n_bad, n_bad, all(self.byte_identical.values()),
            "" if not self.json_diff["n_leaves_differ"] else " (JSON: %d leaves differ, max rel. %g, blocks %s)" % (
                self.json_diff["n_leaves_differ"], self.json_diff["max_rel_diff"], ",".join(self.json_diff["blocks"]))))
        if not ok:
            for c in self.checks:
                if not c["ok"]:
                    _log("FAILED: %s expected %s got %s" % (c["check"], c.get("expected"), c.get("got")))
            raise SystemExit("reproduction of the paper's central values failed; no sampling done")
        return ok

    def _tau_coupling(self):
        """Size of the coupling the code leaves out: the anchor inversion uses tau = 0.18 whatever the drawn tau."""
        fy = self.snap["firm_years"]
        bM = self.snap["MAINT_BASE"]
        med = lambda tau: float(np.median([r["m"] + (1 - tau) * max(r["sig"] - bM, 0.0) + r["kg"] for r in fy]))
        medu = lambda tau: float(np.median([r["m"] + (1 - tau) * r["sig"] + r["kg"] for r in fy]))
        return dict(net={t: med(t) - med(0.18) for t in (0.15, 0.21)}, ub={t: medu(t) - medu(0.18) for t in (0.15, 0.21)})

    def start_pool(self, workers):
        ctx = mp.get_context("spawn")
        self.pool = ctx.Pool(processes=workers, initializer=init_worker, initargs=(self.snap, self.opts))

    def stop_pool(self):
        if self.pool is not None:
            self.pool.close()
            self.pool.join()
            self.pool = None

    # ---------------------------------------------------------------- phase 2: LHS + corners
    def design(self):
        a = self.args
        p = os.path.join(self.ck, "design.npz")
        if os.path.exists(p):
            Z = np.load(p, allow_pickle=False)
            return Z["U"], Z["reps"], int(Z["n_lhs"]), [str(x) for x in Z["labels"]]
        rng = np.random.default_rng(a.seed)
        U_l = lhs(a.n, self.k, rng)
        U_c, lab_c = corner_design(self.k, a.corners, np.random.default_rng(a.seed + 1))
        U = np.vstack([U_l, U_c])
        reps = np.random.default_rng(a.seed + 2).integers(0, len(self.snap["boot"]["net"]), size=U.shape[0])
        labels = ["lhs"] * a.n + lab_c
        _atomic_save_npz(p, U=U, reps=reps, n_lhs=np.array(a.n), labels=np.array(labels))
        return U, reps, a.n, labels

    def run_draws(self):
        a = self.args
        U, reps, n_lhs, labels = self.design()
        self.U, self.reps, self.n_lhs, self.labels = U, reps, n_lhs, labels
        N = U.shape[0]
        todo = []
        for i0 in range(0, N, a.chunk):
            if not os.path.exists(os.path.join(self.ck, "draws_%07d.npz" % i0)):
                todo.append((i0, U[i0:i0 + a.chunk], reps[i0:i0 + a.chunk]))
        _log("draws: %d LHS + %d corners = %d points, %d chunks to run (%d done)" % (
            n_lhs, N - n_lhs, N, len(todo), (N + a.chunk - 1) // a.chunk - len(todo)))
        t = time.time()
        n_done = 0
        if todo:
            for i0, res, rss in self.pool.imap_unordered(task_draws, todo):
                _atomic_save_npz(os.path.join(self.ck, "draws_%07d.npz" % i0), **res)
                self.worker_rss = max(getattr(self, "worker_rss", 0.0), rss)
                n_done += 1
                if n_done % max(1, len(todo) // 20) == 0 or n_done == len(todo):
                    el = time.time() - t
                    _log("  draws chunk %d/%d (%.1f draws/s)" % (n_done, len(todo), n_done * a.chunk / max(el, 1e-9)))
        el = time.time() - t
        pts = sum(x[1].shape[0] for x in todo)
        self.timing["draws_s"] = el
        self.timing["draws_points_run"] = pts
        if pts:
            self.timing["draws_per_s"] = pts / el
            self.timing["s_per_1000_draws"] = 1000 * el / pts
            msg = "draws done: %d points in %.1f s = %.2f draws/s (%.1f s per 1,000) with %d workers" % (
                pts, el, pts / el, 1000 * el / pts, a.workers)
            if resource is not None:
                msg += "; maxrss main %.0f MB, largest worker %.0f MB" % (_own_maxrss_mb(), getattr(self, "worker_rss", 0.0))
            _log(msg)
        R = None
        for i0 in range(0, N, a.chunk):
            Z = np.load(os.path.join(self.ck, "draws_%07d.npz" % i0))
            if R is None:
                R = {k_: [] for k_ in Z.files}
            for k_ in Z.files:
                R[k_].append(Z[k_])
        self.R = {k_: np.concatenate(v_) for k_, v_ in R.items()}

    # ---------------------------------------------------------------- phase 3: extremum searches
    def search_specs(self):
        """One minimization per (quantity key, direction, free set): the extremes of every tested quantity."""
        specs = {}
        for c in self.claims:
            for t in c["tests"]:
                if t["kind"] != "margin":
                    continue
                for s in (t["strata"] or [None]):
                    key = t["key"].format(s=s) if s else t["key"]
                    fixed = VARIANTS[t["variant"]]["fixed"]
                    free = [d["idx"] for d in self.dims if d["group"] not in fixed]
                    if s and s != "ub":
                        free = [j for j in free if self.dims[j]["name"] != "Pi_ub"]
                    free = [j for j in free if not (self.dims[j]["group"] == "maint_base")]
                    dom = t["domain"].format(s=s) if (t["domain"] and s) else t["domain"]
                    for sign in (1.0, -1.0):
                        sid = "%s|%s|%s" % (key, "min" if sign > 0 else "max", t["variant"])
                        specs[sid] = dict(key=key, sign=sign, free=free, parts=parts_for(key), strata=strata_for(key),
                                          domain=dom)
        for s in STRATA:   # levels of the central path (report table)
            for h in HZ:
                key = "%s.R_%s" % (s, h)
                free = [d["idx"] for d in self.dims if d["group"] != "maint_base" and (s == "ub" or d["name"] != "Pi_ub")]
                for sign in (1.0, -1.0):
                    specs.setdefault("%s|%s|full" % (key, "min" if sign > 0 else "max"),
                                     dict(key=key, sign=sign, free=free, parts=["path"], strata=[s], domain=None))
        return specs

    def run_search(self):
        a = self.args
        specs = self.search_specs()
        p = os.path.join(self.ck, "search.json")
        done = json.load(open(p)) if os.path.exists(p) else {}
        todo = []
        for i, (sid, sp) in enumerate(sorted(specs.items())):
            if sid in done:
                continue
            q = self.R.get(sp["key"])
            starts = []
            if q is not None:
                f = sp["sign"] * q
                f = np.where(np.isfinite(f), f, np.inf)
                if sp["domain"]:
                    f = np.where(self.R[sp["domain"]] > 0, f, np.inf)
                for j in np.argsort(f)[:2]:
                    starts.append([float(x) for x in self.U[j]])
            todo.append((sid, sp["key"], sp["sign"], sp["free"], starts, a.search_budget, a.seed + 101 + i,
                         sp["parts"], sp["strata"], sp["domain"]))
        _log("searches: %d extremum searches to run (%d done)" % (len(todo), len(done)))
        t = time.time()
        n = 0
        for sid, res in self.pool.imap_unordered(task_search, todo):
            done[sid] = res
            self.worker_rss = max(getattr(self, "worker_rss", 0.0), res.get("maxrss_mb", 0.0) or 0.0)
            n += 1
            if n % 10 == 0 or n == len(todo):
                _atomic_json(p, done)
                _log("  search %d/%d" % (n, len(todo)))
        if todo:
            _atomic_json(p, done)
        self.timing["search_s"] = time.time() - t
        self.S = done
        self.specs = specs

    # ---------------------------------------------------------------- phase 4: Sobol
    def run_sobol(self):
        a = self.args
        N = a.sobol_n
        groups = [g_ for g_ in GROUP_ORDER if g_ in _M["groups"]] + ["fullcost_target"]
        use_salib = False
        if a.sobol_backend in ("auto", "salib"):
            try:
                from SALib.sample import sobol as salib_sample  # noqa: F401
                from SALib.analyze import sobol as salib_analyze  # noqa: F401
                use_salib = True
            except ImportError:
                if a.sobol_backend == "salib":
                    raise
        base, how = qmc_base(N, 2 * self.k, a.seed + 7)
        A_, B_ = base[:, :self.k], base[:, self.k:]
        blocks = [("A", A_), ("B", B_)]
        if not use_salib:
            for j in range(self.k):
                M_ = A_.copy()
                M_[:, j] = B_[:, j]
                blocks.append(("f%d" % j, M_))
        for g_ in groups:
            M_ = A_.copy()
            ix = _M["groups"][g_]
            M_[:, ix] = B_[:, ix]
            blocks.append(("g:" + g_, M_))
        X_salib = None
        if use_salib:
            from SALib.sample import sobol as salib_sample
            problem = dict(num_vars=self.k, names=[d["name"] for d in self.dims], bounds=[[0.0, 1.0]] * self.k)
            X_salib = salib_sample.sample(problem, N, calc_second_order=False, scramble=True, seed=a.seed + 9)
            blocks.append(("salib", X_salib))
        ck = os.path.join(self.ck, "sobol")
        os.makedirs(ck, exist_ok=True)
        step = 512
        todo = []
        for tag, M_ in blocks:
            for i0 in range(0, M_.shape[0], step):
                fn = os.path.join(ck, "%s_%07d.npy" % (tag.replace(":", "_"), i0))
                if not os.path.exists(fn):
                    todo.append((tag, i0, M_[i0:i0 + step]))
        _log("sobol: N = %d, %d blocks, %d evaluations to run (%s; factor indices by %s)" % (
            N, len(blocks), sum(x[2].shape[0] for x in todo), how, "SALib" if use_salib else "numpy"))
        t = time.time()
        for tag, i0, Y, rss in self.pool.imap_unordered(task_sobol, todo):
            self.worker_rss = max(getattr(self, "worker_rss", 0.0), rss)
            fn = os.path.join(ck, "%s_%07d.npy" % (tag.replace(":", "_"), i0))
            np.save(fn + ".tmp.npy", Y)
            os.replace(fn + ".tmp.npy", fn)
        self.timing["sobol_s"] = time.time() - t
        Y = {}
        for tag, M_ in blocks:
            Y[tag] = np.vstack([np.load(os.path.join(ck, "%s_%07d.npy" % (tag.replace(":", "_"), i0)))
                                for i0 in range(0, M_.shape[0], step)])
        n_boot = 200
        res = dict(N=N, base_design=how, backend_factors="SALib %s" % _salib_version() if use_salib else "numpy (Saltelli 2010 S1, Jansen 1999 ST)",
                   backend_groups="numpy (Saltelli 2010 S1, Jansen 1999 ST)", law=self.law_label + "; anchor dimensions: bootstrap law",
                   n_evaluations=int(sum(v_.shape[0] for v_ in Y.values())), outputs={},
                   ci=dict(level=0.95, n_resamples=n_boot,
                           factors=("SALib analyze, conf_level 0.95, num_resamples %d: S1_conf and ST_conf are the half-widths of "
                                    "its normal-approximation bootstrap interval; S1_ci and ST_ci = index -/+ half-width" % n_boot)
                           if use_salib else ("nonparametric bootstrap of the N base rows (%d resamples with replacement), "
                                              "2.5th and 97.5th percentiles (S1_ci, ST_ci)" % n_boot),
                           groups="nonparametric bootstrap of the N base rows (%d resamples with replacement), 2.5th and 97.5th "
                                  "percentiles (S1_ci, ST_ci)" % n_boot))
        for oi, oname in enumerate(SOBOL_OUTPUTS):
            fA, fB = Y["A"][:, oi], Y["B"][:, oi]
            o = dict(factors={}, groups={})
            if use_salib:
                from SALib.analyze import sobol as salib_analyze
                problem = dict(num_vars=self.k, names=[d["name"] for d in self.dims], bounds=[[0.0, 1.0]] * self.k)
                with contextlib.redirect_stdout(io.StringIO()):
                    Si = salib_analyze.analyze(problem, Y["salib"][:, oi], calc_second_order=False, num_resamples=n_boot,
                                               conf_level=0.95, seed=a.seed + 11, print_to_console=False)
                for j, d in enumerate(self.dims):
                    s1, st, s1c, stc = (float(Si[k_][j]) for k_ in ("S1", "ST", "S1_conf", "ST_conf"))
                    o["factors"][d["name"]] = dict(S1=s1, ST=st, S1_conf=s1c, ST_conf=stc,
                                                   S1_ci=[s1 - s1c, s1 + s1c], ST_ci=[st - stc, st + stc])
            else:
                for j, d in enumerate(self.dims):
                    o["factors"][d["name"]] = sobol_indices(fA, fB, Y["f%d" % j][:, oi], n_boot=n_boot, seed=a.seed + j)
            for g_ in groups:
                o["groups"][g_] = sobol_indices(fA, fB, Y["g:" + g_][:, oi], n_boot=n_boot, seed=a.seed + 500)
            o["var"] = float(np.var(np.concatenate([fA, fB])))
            o["mean"] = float(np.mean(np.concatenate([fA, fB])))
            res["outputs"][oname] = o
        self.sobol = res

    # ---------------------------------------------------------------- group swings (distribution-free one-group-at-a-time)
    def group_swings(self):
        out = {}
        for oname, key, strata in (("net.R_2036", "net.R_2036", ("net",)), ("Gstar_2025", "Gstar_2025", ("net",))):
            parts = frozenset(["path"]) if key.startswith("net") else frozenset(["gstar"])
            rows = {}
            for g_ in [x for x in GROUP_ORDER if x in _M["groups"]] + ["fullcost_target"]:
                ix = _M["groups"][g_]
                if g_ == "maint_base":
                    rows[g_] = dict(low=None, high=None, swing=0.0, method="no effect on this output")
                    continue
                vals = []
                if len(ix) <= 12:
                    for i in range(2 ** len(ix)):
                        u = np.full(self.k, np.nan)
                        for b, j in enumerate(ix):
                            u[j] = float((i >> b) & 1)
                        vals.append(evaluate(u, parts=parts, strata=strata)[key])
                    method = "all %d vertices of the group" % (2 ** len(ix))
                else:
                    fmin = _Objective(key, 1.0, parts, strata)
                    fmax = _Objective(key, -1.0, parts, strata)
                    rng = np.random.default_rng(self.args.seed + 3)
                    _, lo_, _, _ = vertex_search(fmin, self.k, ix, [], rng, self.args.search_budget)
                    _, hi_, _, _ = vertex_search(fmax, self.k, ix, [], rng, self.args.search_budget)
                    vals = [lo_, -hi_]
                    method = "vertex search over the group's %d dimensions" % len(ix)
                vals.append(evaluate(np.full(self.k, np.nan), parts=parts, strata=strata)[key])
                rows[g_] = dict(low=float(min(vals)), high=float(max(vals)), swing=float(max(vals) - min(vals)), method=method)
            out[oname] = rows
        return out

    # ---------------------------------------------------------------- accountability-floor sub-box
    def run_amin(self):
        a = self.args
        A = self.snap["amin"]
        dims = [dict(name="audit_fee", label="Audit fee ($)", lo=A["fee_lo"], central=A["fee"], hi=A["fee_hi"], cls="b",
                     src=src_line("code/paper1_macros.py", r"^AUDIT_FEE_LO") + "-" + src_line("code/paper1_macros.py", r"^AUDIT_FEE_HI"),
                     note="S&P 500 ratio to large-accelerated-filer average ('over the range of audit fees')"),
                dict(name="pcc", label="Cross-type common mode p_cc per opportunity", lo=0.0, central=0.0, hi=0.0025, cls="d",
                     src=src_line("code/paper1_macros.py", r"^PCC_GRID") + " (Table tab:amin-pcc)", note=""),
                dict(name="phm", label="Human miss rate on AI-missed items", lo=0.05, central=0.05, hi=0.50, cls="d",
                     src=src_line("code/paper1_macros.py", r"^PHM_GRID") + " (Table tab:amin-pcc)", note="0.05 = the human miss rate"),
                dict(name="pca", label="AI common-mode probability per opportunity", lo=A["pca"], central=A["pca"], hi=0.01,
                     cls="d", src=src_line("code/paper1_macros.py", r"^alt_N, alt_c") + " (sensitivity pca = 0.01)", note=""),
                dict(name="N_opp", label="Opportunities a year", lo=float(A["N"]), central=float(A["N"]), hi=48.0, cls="d",
                     src=src_line("code/paper1_macros.py", r"^alt_N, alt_c") + " (sensitivity N = 48)", note="")]
        k = len(dims)
        rng = np.random.default_rng(a.seed + 21)
        U = np.vstack([lhs(a.amin_n, k, rng)] + [np.array([[(i >> j) & 1 for j in range(k)] for i in range(2 ** k)], dtype=float)])
        n_lhs = a.amin_n

        def val(d, u):
            return d["central"] if u != u else d["lo"] + u * (d["hi"] - d["lo"])

        def ev(u):
            x = {d["name"]: val(d, u[i]) for i, d in enumerate(dims)}
            N = x["N_opp"]
            r = {}
            for t, e in A["eps"].items():
                ai = min(1 - (1 - amin_P_v(0, na, A, pcc=x["pcc"], pca=x["pca"])) ** N for na in range(1, 7))
                hu = min(1 - (1 - amin_P_v(nh, 0, A, pcc=x["pcc"], pca=x["pca"])) ** N for nh in range(1, 7))
                b_ = amin_best_v(e, A, N=N, pca=x["pca"], pcc=x["pcc"], phm=x["phm"])
                fl = float("inf") if b_ is None else (x["audit_fee"] + A["kpmg_small"]) / A["REV"] + b_[0] / A["REV"]
                r[t + ".ai_only_pmin"] = ai
                r[t + ".human_only_pmin"] = hu
                r[t + ".floor"] = fl
                r[t + ".design"] = -1.0 if b_ is None else 10.0 * b_[1] + b_[2]
            return r
        t0 = time.time()
        recs = [ev(U[i]) for i in range(U.shape[0])]
        centre = ev(np.full(k, np.nan))
        Ra = {k_: np.array([r_[k_] for r_ in recs]) for k_ in recs[0]}
        b5 = amin_best_v(A["eps"]["Five"], A)
        floor_lo = {t: (A["fee_lo"] + A["kpmg_small"]) / A["REV"] + amin_best_v(e, A)[0] / A["REV"] for t, e in A["eps"].items()}
        floor_hi = {t: (A["fee_hi"] + A["kpmg_small"]) / A["REV"] + amin_best_v(e, A)[0] / A["REV"] for t, e in A["eps"].items()}
        tests = []
        for t, e in A["eps"].items():
            lab = "%g%%" % (100 * e)
            design = {"Five": 11.0, "One": 12.0}[t]
            tests.append(dict(tid="A1." + t, claim="No design built only from AI layers on one provider passes",
                              text="min over all-AI designs of P(miss in year) > threshold", stratum=lab,
                              key=t + ".ai_only_pmin", m=Ra[t + ".ai_only_pmin"] - e, central=centre[t + ".ai_only_pmin"] - e))
            if t == "One":
                tests.append(dict(tid="A2.One", claim="All-human designs do not pass at 1%", text="min over all-human designs of P > 1%",
                                  stratum=lab, key=t + ".human_only_pmin", m=Ra[t + ".human_only_pmin"] - e, central=centre[t + ".human_only_pmin"] - e))
            else:
                tests.append(dict(tid="A2.Five", claim="An all-human design passes at 5% (three layers)", text="min over all-human designs of P <= 5%",
                                  stratum=lab, key=t + ".human_only_pmin", m=e - Ra[t + ".human_only_pmin"], central=e - centre[t + ".human_only_pmin"], nonstrict=True))
            tests.append(dict(tid="A3." + t, claim="Cheapest admissible design is %s" % ("1 human over 1 AI" if t == "Five" else "1 human over 2 AI"),
                              text="cheapest design equals the stated one", stratum=lab, key=t + ".design",
                              m=np.where(Ra[t + ".design"] == design, 1.0, -1.0), central=1.0 if centre[t + ".design"] == design else -1.0))
            tests.append(dict(tid="A4." + t, claim="Floor within the stated range 0.26-0.76% (audit fees)",
                              text="floor in [%.4f%%, %.4f%%]" % (100 * floor_lo[t], 100 * floor_hi[t]), stratum=lab, key=t + ".floor",
                              m=np.minimum(Ra[t + ".floor"] - floor_lo[t], floor_hi[t] - Ra[t + ".floor"]),
                              central=min(centre[t + ".floor"] - floor_lo[t], floor_hi[t] - centre[t + ".floor"]), nonstrict=True))
            tests.append(dict(tid="A5." + t, claim="Floor below the a_min band's lower end (0.5%) (informational)",
                              text="floor < 0.5%", stratum=lab, key=t + ".floor", m=0.005 - Ra[t + ".floor"],
                              central=0.005 - centre[t + ".floor"]))
        out_tests = []
        for tt in tests:
            m = np.where(np.isfinite(tt["m"]), tt["m"], -1.0)       # no admissible design: the floor claim fails
            if not math.isfinite(tt["central"]):
                tt["central"] = -1.0
            ok = (m >= -TOL) if tt.get("nonstrict") else (m > 0)
            q = Ra[tt["key"]]
            rec = dict(tid=tt["tid"], claim=tt["claim"], test=tt["text"], threshold=tt["stratum"],
                       holds_everywhere=bool(ok.all()), margin_min=float(np.min(m)), margin_central=float(tt["central"]),
                       quantity=dict(key=tt["key"], min=float(np.min(q[np.isfinite(q)])) if np.isfinite(q).any() else None,
                                     max=float(np.max(q[np.isfinite(q)])) if np.isfinite(q).any() else None,
                                     n_inf=int((~np.isfinite(q)).sum())),
                       share_holds_uniform=float(ok[:n_lhs].mean()), n_points=int(len(m)), all_corners_evaluated=True)
            if not ok.all():
                fail = ~ok[:n_lhs]
                if fail.any():
                    leaves = tree_rules(U[:n_lhs], fail, max_depth=2)
                    rec["failure_rules"] = [dict(rule=" and ".join("%s %s %s" % (dims[j]["name"], op, fmt_val(dims[j], val(dims[j], th)))
                                                                   for j, op, th in L["path"]) or "no split separates failures (whole box)",
                                                 n=L["n"], fail_share=L["fail_share"], n_fail=L["n_fail"]) for L in leaves if L["n_fail"] > 0]
                worst = int(np.argmin(m))
                rec["worst_point"] = {d["name"]: val(d, U[worst, i]) for i, d in enumerate(dims)}
            out_tests.append(rec)
        self.timing["amin_s"] = time.time() - t0
        self.amin = dict(dims=[{k_: v_ for k_, v_ in d.items()} for d in dims], n_lhs=n_lhs, n_corners=2 ** k,
                         thresholds=A["eps"], tests=out_tests, central_design_5pct=list(b5[1:]),
                         fixed=dict(ph=A["ph"], pch=A["pch"], pa=A["pa"], ch=A["ch"], ca=A["ca"], itgc=A["itgc"],
                                    kpmg_small=A["kpmg_small"]),
                         note="Separate sub-box: the accountability-floor example (Remark rem:amin-values) has its own "
                              "parameters and does not depend on any parameter of code/calibrate_horizons.py. Its ranges are "
                              "those the paper itself tabulates (audit fees; the p_cc and human-miss grids of Table "
                              "tab:amin-pcc; the N = 48 and p_ca = 0.01 sensitivities), and that table already reports the "
                              "break-evens beyond which no design is admissible, so failures driven by p_cc or the human miss "
                              "rate restate the paper's own table jointly")

    # ---------------------------------------------------------------- analysis
    def analyse(self):
        a = self.args
        R, U, n_lhs = self.R, self.U, self.n_lhs
        dims = self.dims
        claims_out = []
        scans_todo = []
        for c in self.claims:
            cout = dict(id=c["id"], title=c["title"], quote=c["quote"], where=c["where"], tests=[])
            for t in c["tests"]:
                for s in (t["strata"] or [None]):
                    key = t["key"].format(s=s) if s else t["key"]
                    thr = t["thr"][s] if isinstance(t["thr"], dict) else t["thr"]
                    q = R[key]
                    dom = (t["domain"].format(s=s) if s else t["domain"]) if t["domain"] else None
                    in_dom = (R[dom] > 0) if dom else np.ones(len(q), dtype=bool)
                    m = margin_of(t["op"], q, thr)
                    ok = passes(t["op"], m) | ~in_dom          # outside the claim's domain: not a failure
                    m_f = np.where(np.isfinite(m), m, np.where(np.isnan(m), -np.inf, m))
                    m_f = np.where(in_dom, m_f, np.inf)
                    i_min = int(np.argmin(m_f))
                    rec = dict(tid=t["tid"] + ("." + s if s else ""), test=t["text"], op=t["op"], threshold=thr,
                               variant=t["variant"], variant_label=VARIANTS[t["variant"]]["label"], stratum=s, key=key,
                               kind=t["kind"], n_points=int(len(m)), n_lhs=int(n_lhs), note=t.get("note", ""), domain=dom)
                    if dom:
                        rec["domain_text"] = "target above the anchor intercept at every horizon (the program raises the margin)"
                        rec["share_outside_domain_uniform"] = float((~in_dom[:n_lhs]).mean())
                        rec["n_outside_domain"] = int((~in_dom).sum())
                        rec["domain_min"] = float(np.min(R[dom]))
                        q = np.where(in_dom, q, np.nan)
                    qf = q[np.isfinite(q)]
                    rec["quantity"] = dict(central=None, min=float(qf.min()) if len(qf) else None,
                                           max=float(qf.max()) if len(qf) else None, n_nonfinite=int((~np.isfinite(q)).sum()),
                                           lhs_p05=float(np.quantile(q[:n_lhs][np.isfinite(q[:n_lhs])], 0.05)) if np.isfinite(q[:n_lhs]).any() else None,
                                           lhs_p95=float(np.quantile(q[:n_lhs][np.isfinite(q[:n_lhs])], 0.95)) if np.isfinite(q[:n_lhs]).any() else None)
                    rec["margin_min_sampled"] = float(m_f[i_min])
                    rec["argmin_sampled"] = dict(index=i_min, design=self.labels[i_min])
                    worst_u = [float(x) for x in U[i_min]]
                    worst_m = float(m_f[i_min])
                    found_by = "sampled (%s)" % self.labels[i_min]
                    q_min, q_max = rec["quantity"]["min"], rec["quantity"]["max"]
                    oat = None
                    for direction in ("min", "max"):
                        sid = "%s|%s|%s" % (key, direction, t["variant"])
                        if sid in self.S:
                            sr = self.S[sid]
                            val = sr["value"]
                            if val is None:
                                continue
                            if direction == "min" and (q_min is None or val < q_min):
                                q_min = val
                            if direction == "max" and (q_max is None or val > q_max):
                                q_max = val
                            mm = float(margin_of(t["op"], val, thr))
                            if mm < worst_m:
                                worst_m, worst_u, found_by = mm, sr["u"], "vertex search"
                            if (direction == "min") == (t["op"] in (">", ">=")):
                                oat = sr.get("oat")
                    rec["quantity"]["min"], rec["quantity"]["max"] = q_min, q_max
                    rec["quantity"]["central"] = float(evaluate(np.full(self.k, np.nan), parts=frozenset(parts_for(key)),
                                                                strata=tuple(strata_for(key)))[key])
                    rec["margin_min"] = worst_m
                    rec["holds_everywhere"] = bool(passes(t["op"], worst_m))
                    rec["worst_point_found_by"] = found_by
                    rec["worst_point_u"] = [None if (x is None or x != x) else x for x in worst_u]
                    rec["share_holds_uniform"] = float(ok[:n_lhs][in_dom[:n_lhs]].mean()) if in_dom[:n_lhs].any() else None
                    rec["share_label"] = self.law_label
                    rec["corners_hold"] = bool(ok[n_lhs:].all()) if len(ok) > n_lhs else None
                    if oat:
                        eff = sorted(((abs(v_), int(j)) for j, v_ in oat.items() if v_ is not None), reverse=True)
                        rec["influential_dims"] = [dims[j]["name"] for v_, j in eff[:6] if v_ > 1e-12]
                    else:
                        rec["influential_dims"] = []
                    if t["kind"] == "count":
                        rec.update(self._count_analysis(t, s, thr))
                        rec["holds_everywhere"] = rec["holds_everywhere"] and rec["count_holds_on_grid"]
                    if not rec["holds_everywhere"]:
                        fail = ~ok[:n_lhs]
                        rec["failure"] = dict(share_fail_uniform=float(fail[in_dom[:n_lhs]].mean()) if in_dom[:n_lhs].any() else 0.0)
                        if fail.any() and fail.sum() >= 5:
                            # candidate dimensions: those the tested margin depends on, by a one-at-a-time effect at the
                            # centre or a rank correlation with the margin across the LHS draws (filters chance splits)
                            mm_l = np.where(np.isfinite(m[:n_lhs]), m[:n_lhs], np.nanmin(np.where(np.isfinite(m[:n_lhs]), m[:n_lhs], np.nan)) - 1)
                            sel = in_dom[:n_lhs]
                            rk = np.argsort(np.argsort(mm_l[sel])).astype(float)
                            feats = []
                            for j in range(self.k):
                                x_ = U[:n_lhs][sel, j]
                                cc = abs(np.corrcoef(x_, rk)[0, 1]) if np.std(rk) > 0 and np.std(x_) > 0 else 0.0
                                if cc > 3.0 / math.sqrt(max(sel.sum(), 1)) or dims[j]["name"] in rec["influential_dims"]:
                                    feats.append(j)
                            leaves = tree_rules(U[:n_lhs], fail, max_depth=2, features=feats or None)
                            rules = []
                            for L in sorted(leaves, key=lambda L: -L["n_fail"]):
                                if L["n_fail"] == 0:
                                    continue
                                cond = []
                                for j, op, th in L["path"]:
                                    d = dims[j]
                                    pv = dim_value(d, th, s or "net") if d["name"] == "m0A" else dim_value(d, th)
                                    cond.append("%s %s %s" % (d["name"], op, fmt_val(d, pv)))
                                rules.append(dict(rule=" and ".join(cond) or "no split separates failures (whole box)", n=L["n"], n_fail=L["n_fail"],
                                                  fail_share_in_leaf=L["fail_share"], share_of_failures=L["n_fail"] / float(fail.sum())))
                            rec["failure"]["tree_rules"] = rules
                            split_dims = []
                            for L in leaves:
                                for j, _, _ in L["path"]:
                                    if j not in split_dims:
                                        split_dims.append(j)
                        else:
                            split_dims = []
                        cand = [j for j in split_dims if dims[j]["name"] in rec["influential_dims"]] + \
                            [self.dims_by_name(nm) for nm in rec["influential_dims"]] + split_dims
                        top = []
                        for j in cand:
                            if j not in top and self.dims[j]["group"] not in VARIANTS[t["variant"]]["fixed"]:
                                top.append(j)
                        top = top[:3]
                        rec["failure"]["scan_dims"] = [dims[j]["name"] for j in top]
                        if t["kind"] == "margin":
                            grid = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75,
                                    0.8, 0.85, 0.9, 0.95, 1.0]
                            for j in top:
                                for refname, ref in (("central", [float("nan")] * self.k), ("worst", rec["worst_point_u"])):
                                    ref_ = [float("nan") if x is None else x for x in ref]
                                    sid = "%s|%s|%d|%s" % (rec["tid"], key, j, refname)
                                    scans_todo.append((sid, key, j, ref_, grid, parts_for(key), strata_for(key), dom))
                                    rec["failure"].setdefault("_scan_ids", []).append((sid, j, refname))
                    rec["worst_point"] = describe_point(dims, rec["worst_point_u"],
                                                        [self.dims_by_name(nm) for nm in rec["influential_dims"][:5]],
                                                        stratum=s) if rec["influential_dims"] else ""
                    cout["tests"].append(rec)
            claims_out.append(cout)
        # univariate scans (in the pool)
        p = os.path.join(self.ck, "scans.json")
        done = json.load(open(p)) if os.path.exists(p) else {}
        todo = [x for x in scans_todo if x[0] not in done]
        if todo:
            _log("failure scans: %d univariate scans" % len(todo))
            for sid, vals in self.pool.imap_unordered(task_scan, todo):
                done[sid] = vals
            _atomic_json(p, done)
        grid = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
        for cout in claims_out:
            for rec in cout["tests"]:
                fl = rec.get("failure")
                if not fl or "_scan_ids" not in fl:
                    continue
                desc = []
                for sid, j, refname in fl.pop("_scan_ids"):
                    vals = done.get(sid)
                    if vals is None:
                        continue
                    d = dims[j]
                    vals = np.array(vals, dtype=float)
                    mm = margin_of(rec["op"], vals[:, 0], rec["threshold"])
                    indom = vals[:, 1] > 0
                    okk = passes(rec["op"], mm) | ~indom
                    st = rec["stratum"] or "net"
                    pv = [dim_value(d, gv, st) if d["name"] == "m0A" else dim_value(d, gv) for gv in grid]
                    if okk.all():
                        txt = "holds over the whole range"
                    elif not okk.any():
                        txt = "fails over the whole range"
                    else:
                        segs, cur = [], None
                        for gv, o_ in zip(pv, okk):
                            if not o_ and cur is None:
                                cur = [gv, gv]
                            elif not o_:
                                cur[1] = gv
                            elif cur is not None:
                                segs.append(cur)
                                cur = None
                        if cur is not None:
                            segs.append(cur)
                        txt = "fails for " + ", ".join(("%s = %s" % (d["name"], fmt_val(d, s0)) if s0 == s1 else
                                                        "%s in [%s, %s]" % (d["name"], fmt_val(d, s0), fmt_val(d, s1))) for s0, s1 in segs)
                    if not indom.all():
                        txt += " (outside the claim's domain at %d of %d grid points)" % (int((~indom).sum()), len(indom))
                    desc.append(dict(dim=d["name"], reference=refname, result=txt,
                                     margin_at_ends=[float(mm[0]), float(mm[-1])]))
                fl["univariate"] = desc
        self.claims_out = claims_out

    def dims_by_name(self, nm):
        return _M["idx"][nm]

    def _count_analysis(self, t, s, thr):
        """Lever counts depend only on b_M (and phi, alpha): exact analysis on a fine grid of the free dimensions."""
        pos = self.snap["positions"]
        d_b = self.dims[_M["idx"]["b_M"]]
        d_p = self.dims[_M["idx"]["phi"]]
        bs = [dim_value(d_b, x) for x in np.linspace(0, 1, 401)]
        ps = [dim_value(d_p, x) for x in np.linspace(0, 1, 71)]
        key = t["key"].split(".")[-1]
        counts = {}
        for b in bs:
            for ph in (ps if key == "n_eng_first" else [0.0]):
                counts[(b, ph)] = levers_v(pos, b, ph, 0.3, s)[key]
        vals = sorted(set(counts.values()))
        bad = [(b, ph) for (b, ph), v_ in counts.items() if v_ != thr]
        out = dict(count_values_on_grid=vals, count_holds_on_grid=not bad,
                   b_M_box=[d_b["lo"], d_b["hi"]], b_M_central=d_b["central"])
        if key == "n_ge_first" and s == "net":
            th = sorted(p_["sm"] - p_["ga"] for p_ in pos)
            out["switch_points_b_M"] = th
            cnt = lambda b: sum(b < x for x in th)
            iv = self._interval(th, cnt, thr)
            out["b_M_interval_with_stated_count"] = [x for x in iv]
            bb = np.array(self.snap["boot"]["base"])
            if iv and not isinstance(iv[0], list):
                out["bootstrap_share_all_draws"] = float(np.mean((bb >= iv[0]) & (bb < iv[1])))
        if key == "n_eng_above":
            th = sorted(p_["sm"] - p_["rd"] for p_ in pos)
            out["switch_points_b_M"] = th
        if bad:
            bb = sorted(set(b for b, _ in bad))
            out["b_M_fail_range_on_grid"] = [bb[0], bb[-1]]
            if key == "n_eng_first":
                pp = sorted(set(ph for _, ph in bad))
                out["phi_fail_range_on_grid"] = [pp[0], pp[-1]]
        return out

    @staticmethod
    def _interval(th, cnt, target):
        pts = [-1.0] + list(th) + [2.0]
        res = []
        for lo, hi in zip(pts[:-1], pts[1:]):
            mid = (lo + hi) / 2
            if cnt(mid) == target:
                res.append([max(lo, 0.0), hi])
        return res[0] if len(res) == 1 else res

    # ---------------------------------------------------------------- quoted quantities
    QUANTS = [("Gstar_2025", "G*, 2025 prices, fixed prices", "pct"), ("Gstar_2025_cc6", "G*, compute 6% at 2025 prices", "pct"),
              ("Gstar_2028", "G*, 2028 (compute path)", "pct"), ("Gstar_2031", "G*, 2031", "pct"), ("Gstar_2036", "G*, 2036", "pct"),
              ("net.Gstar_2025_phi", "G*, 2025 prices, drawn pass-through (netted anchor's saving)", "pct"),
              ("c_c_2025", "Compute share at 2025 prices", "pct"), ("c_c_2036", "Compute share 2036", "pct"),
              ("s_2036", "Realized share of the program by 2036", "pct"), ("E_2036", "Embedded share by 2036", "pct"),
              ("complete_year", "Expected completion year", "yr"), ("net.dip_2028", "In-flight dip 2028 (netted)", "pct"),
              ("net.dip_2036", "In-flight dip 2036 (netted)", "pct"),
              ("net.B.pb.cross", "Flow crossing, central execution (years; depends on execution only)", "yr"),
              ("net.B.pb.pb_u", "Payback, central execution (years)", "yr"),
              ("net.B.pb.pb_d", "Discounted payback, central execution (years)", "yr"),
              ("net.B.pb.ratio", "PV gains / PV dip, central execution", "x"),
              ("net.B.pb.npv", "NPV, central execution (% of a year's revenue)", "pct"),
              ("net.pb.cross", "Flow crossing, full box (years)", "yr"), ("net.pb.pb_u", "Payback, full box (years)", "yr"),
              ("net.pb.pb_d", "Discounted payback, full box (years)", "yr"), ("net.pb.ratio", "PV gains / PV dip, full box", "x"),
              ("net.pb.npv", "NPV, full box (% of a year's revenue)", "pct"),
              ("pull_multiple", "Rule of 1000: demand pull needed / today's best", "x")]

    def quantities(self):
        R, n = self.R, self.n_lhs
        c = evaluate(np.full(self.k, np.nan))
        out = []
        for key, lab, unit in self.QUANTS:
            if key not in R:
                continue
            q = np.array(R[key], dtype=float)
            if ".pb." in key:
                q = np.where(R[key.rsplit(".pb.", 1)[0] + ".pb.dM_min"] > 0, q, np.nan)
            fin = np.isfinite(q)
            lo = float(q[fin].min()) if fin.any() else None
            hi = float(q[fin].max()) if fin.any() else None
            by = "sampled"
            for sid, sr in self.S.items():
                if sid.split("|")[0] == key and sr.get("value") is not None:
                    v_ = sr["value"]
                    if sid.split("|")[1] == "min" and (lo is None or v_ < lo):
                        lo, by = v_, "sampled + search"
                    if sid.split("|")[1] == "max" and math.isfinite(v_) and (hi is None or v_ > hi):
                        hi, by = v_, "sampled + search"
            ql = q[:n][fin[:n]]
            out.append(dict(key=key, label=lab, unit=unit, central=c.get(key), min=lo, max=hi, extremes_from=by,
                            n_never=int(np.isinf(q).sum()),
                            lhs_p05=float(np.quantile(ql, 0.05)) if len(ql) else None,
                            lhs_p95=float(np.quantile(ql, 0.95)) if len(ql) else None))
        return out

    # ---------------------------------------------------------------- levels and combined band
    def levels(self):
        R, n = self.R, self.n_lhs
        CAL = json.load(open(os.path.join(REPO, "notes", "calibration_results.json")))
        ai = CAL["r2"]["anchor_interval"]
        out = {}
        for s in STRATA:
            for h in HZ:
                key = "%s.R_%s" % (s, h)
                q = R[key]
                lo, hi = float(np.min(q)), float(np.max(q))
                for direction in ("min", "max"):
                    sr = self.S.get("%s|%s|full" % (key, direction))
                    if sr:
                        if direction == "min":
                            lo = min(lo, sr["value"])
                        else:
                            hi = max(hi, sr["value"])
                bk = "%s.boot.R_%s" % (s, h)
                br = ai[s]["path"][h]["ci90_joint"]
                out[key] = dict(central=float(CAL["central_path"]["path"][s][h]["R"]), paper_anchor_interval_90=br,
                                box_min=lo, box_max=hi, lhs_p05=float(np.quantile(q[:n], 0.05)),
                                lhs_p95=float(np.quantile(q[:n], 0.95)),
                                share_in_paper_interval_uniform=float(np.mean((q[:n] >= br[0]) & (q[:n] <= br[1]))),
                                combined_band_90=[float(np.quantile(R[bk][:n], 0.05)), float(np.quantile(R[bk][:n], 0.95))] if bk in R else None)
        return out

    # ---------------------------------------------------------------- report
    def merged_timing(self):
        """Timing and worker memory of the phases actually run, merged with those of earlier (interrupted) invocations
        of the same configuration, which are kept in the checkpoint."""
        prev = dict(getattr(self, "prev_timing", {}))
        cur = dict(self.timing)
        if not cur.get("draws_points_run"):
            for k_ in ("draws_s", "draws_points_run", "draws_per_s", "s_per_1000_draws"):
                cur.pop(k_, None)
        for k_ in ("search_s", "sobol_s"):
            if cur.get(k_, 0.0) < 0.5 and k_ in prev:
                cur.pop(k_, None)
        out = dict(prev)
        out.update(cur)
        rss = [x for x in (prev.get("worker_peak_rss_mb"), getattr(self, "worker_rss", None)) if x is not None and x == x]
        if rss:
            out["worker_peak_rss_mb"] = max(rss)
        out["workers"] = self.args.workers if cur.get("draws_points_run") else prev.get("workers", self.args.workers)
        _atomic_json(os.path.join(self.ck, "timing.json"), out)
        return out

    def write_outputs(self, swings):
        a = self.args
        self.timing = self.merged_timing()
        lv = self.levels()
        sob = getattr(self, "sobol", None)
        torn = self.snap["tornado"]["2036"]
        tmap = {"pace": "execution", "surplus": "surplus", "G": "market_growth", "target": "fullcost_target",
                "bcg_win": "execution", "capital": "capital", "anchor_quartile": "anchor", "pass_through": "pass_through",
                "attribution": "(S&M stratum: not a dimension)", "dip": "(in-flight dip: a different quantity)",
                "anchor_sample": "(alternative anchor samples: not a dimension)"}
        comp = []
        for i, r in enumerate(sorted(torn, key=lambda r: -(r["high"] - r["low"]))):
            g_ = tmap.get(r["key"], "")
            row = dict(tornado_row=r["key"], tornado_rank=i + 1, tornado_swing=r["high"] - r["low"], group=g_)
            if g_ in swings["net.R_2036"]:
                row["group_swing_box"] = swings["net.R_2036"][g_]["swing"]
            if sob and g_ in sob["outputs"]["net.R_2036"]["groups"]:
                row["sobol_ST"] = sob["outputs"]["net.R_2036"]["groups"][g_]["ST"]
                row["sobol_S1"] = sob["outputs"]["net.R_2036"]["groups"][g_]["S1"]
            comp.append(row)
        sclaims = []
        sw36 = swings["net.R_2036"]
        swg = swings["Gstar_2025"]
        top_sw = max((g_ for g_ in sw36 if g_ != "fullcost_target"), key=lambda g_: sw36[g_]["swing"])
        top_swg = max((g_ for g_ in swg if g_ != "fullcost_target"), key=lambda g_: swg[g_]["swing"])
        s1 = dict(id="S1", title="Execution, not market growth, moves the 2036 score most",
                  quote="execution, not market growth, moves the 2036 score most; by 2036 the largest swing in a "
                        "one-at-a-time sensitivity comes from execution", where="summary item 6; Sec. 1; Sec. 7.3",
                  distribution_free=dict(test="group swing (all other dimensions central): execution > market growth, and "
                                              "execution the largest group", execution=sw36["execution"]["swing"],
                                         market_growth=sw36["market_growth"]["swing"], largest_group=top_sw,
                                         holds=bool(sw36["execution"]["swing"] > sw36["market_growth"]["swing"] and top_sw == "execution")))
        pm = read_macros()          # the quote as the paper now prints it (round 3: the range was 1 to 60, then 2 to 60)
        s2 = dict(id="S2", title="The compute share is the dominant uncertainty in the threshold",
                  quote="Over its scenario range of %s to %s%% of revenue, the threshold runs from %s to %s%%. This is the dominant "
                        "uncertainty." % (pm["CcLo"], pm["CcHi"], pm["GstarCcLo"], pm["GstarCcHi"]),
                  where="Sec. 7.2 'The ceiling'",
                  distribution_free=dict(test="group swing of G* (others central): compute the largest group",
                                         largest_group=top_swg, compute=swg["compute"]["swing"], holds=bool(top_swg == "compute")))
        if sob:
            gr36 = sob["outputs"]["net.R_2036"]["groups"]
            grg = sob["outputs"]["Gstar_2025"]["groups"]
            cand = [g_ for g_ in gr36 if g_ != "fullcost_target"]
            top = max(cand, key=lambda g_: gr36[g_]["ST"])
            topg = max([g_ for g_ in grg if g_ != "fullcost_target"], key=lambda g_: grg[g_]["ST"])
            ci_ = lambda gr, g_: gr[g_].get("ST_ci")
            # round 3: 95% bootstrap intervals of the group indices; 'holds_ci' asks whether the ordering survives them
            # (the leader's lower bound above every other group's upper bound)
            sep = lambda gr, g0: all(gr[g0]["ST_ci"][0] > gr[g_]["ST_ci"][1] for g_ in gr if g_ not in (g0, "fullcost_target"))
            s1["sobol"] = dict(test="group total index ST: execution > market growth, and execution the largest group",
                               ST_execution=gr36["execution"]["ST"], ST_market_growth=gr36["market_growth"]["ST"],
                               ST_execution_ci=ci_(gr36, "execution"), ST_market_growth_ci=ci_(gr36, "market_growth"),
                               largest_group=top, holds=bool(gr36["execution"]["ST"] > gr36["market_growth"]["ST"] and top == "execution"),
                               holds_ci=bool(gr36["execution"]["ST_ci"][0] > gr36["market_growth"]["ST_ci"][1] and sep(gr36, "execution")),
                               label=self.law_label, ci_method=sob["ci"]["groups"])
            s2["sobol"] = dict(test="group total index ST of G*: compute the largest group", largest_group=topg,
                               ST_compute=grg["compute"]["ST"], ST_compute_ci=ci_(grg, "compute"), holds=bool(topg == "compute"),
                               holds_ci=bool(sep(grg, "compute")), label=self.law_label, ci_method=sob["ci"]["groups"])
        sclaims = [s1, s2]
        mem = {}
        if resource is not None:
            scale = 1024.0 if sys.platform != "darwin" else 1024.0 * 1024.0
            mem = dict(main_maxrss_mb=_own_maxrss_mb(), largest_child_maxrss_mb=self.timing.get("worker_peak_rss_mb", float("nan")),
                       note="peak resident memory (VmHWM); total = main + workers x largest worker, an upper bound")
            mem["estimated_peak_total_mb"] = mem["main_maxrss_mb"] + self.timing.get("workers", a.workers) * mem["largest_child_maxrss_mb"] \
                if math.isfinite(mem["largest_child_maxrss_mb"]) else None
        res = dict(
            meta=dict(script="code/mc_claims.py", version=VERSION, config_hash=self.cfg,
                      args={k_: v_ for k_, v_ in vars(a).items()}, python=sys.version.split()[0], numpy=np.__version__,
                      platform=platform.platform(), machine=platform.machine(), cpu_count=os.cpu_count(),
                      timing=self.timing, memory=mem, created=time.strftime("%Y-%m-%d %H:%M:%S"),
                      small_n_warning=(a.n < 5000)),
            framing=("Not a forecast. Most parameters are scenario values (class d) with ranges but no measured distribution. "
                     "Primary result: does each claim hold at every point of the box of the paper's own stated ranges, and "
                     "if not, where does it fail. Shares of draws are secondary: " + self.law_label + "; the anchor "
                     "dimensions follow the firm-cluster bootstrap within its 90% interval."),
            law_label=self.law_label,
            reproduction=dict(checks=self.checks, all_passed=all(c["ok"] for c in self.checks),
                              shadow_outputs_byte_identical=self.byte_identical, shadow_json_numeric_diff=self.json_diff),
            dims=[{k_: (v_ if k_ != "law" else v_) for k_, v_ in d.items()} for d in self.dims],
            design=dict(n_lhs=self.n_lhs, n_corners=int(self.U.shape[0] - self.n_lhs), corner_rule=(
                "k = %d > 14: the all-low and all-high vertices, %d random vertices (seed %d), and for every tested "
                "quantity a directional vertex (each dimension at the end that moves the quantity the tested way at the "
                "centre) improved by greedy single-coordinate flips and an interior coordinate pass (vertex search)" % (
                    self.k, a.corners, a.seed + 1)), seed=a.seed, strata=STRATUM_LABEL, variants=VARIANTS,
                cc_mode=a.cc_mode, anchor_range=a.anchor_range, bcg_win=bool(a.bcg_win)),
            omitted_coupling=dict(tau_in_anchor=self.tau_coupling, note="the code inverts the anchor at tau = 0.18 whatever "
                                  "the target's tau; drawing tau into the anchor would move the median intercept by these amounts"),
            claims=self.claims_out, sensitivity_claims=sclaims, levels=lv, quantities=self.quantities(), group_swings=swings,
            tornado_comparison=comp, sobol=sob, amin=self.amin)
        res = _clean(res)
        if a.compare_to:                                # a second seed, recorded against the first run
            p_ = a.compare_to if a.compare_to.endswith(".json") else os.path.join(a.compare_to, "mc_claims.json")
            res["seed_comparison"] = _clean(compare_runs(res, json.load(open(p_)), other_path=p_))
            sc = res["seed_comparison"]["summary"]
            _log("seed comparison with %s (seed %s): %d of %d tests agree on holds-everywhere; largest change of a box extreme "
                 "%.2f points" % (p_, res["seed_comparison"]["other"]["seed"], sc["n_agree"], sc["n_tests"], sc["max_abs_diff_extreme_pts"]))
        _atomic_json(os.path.join(self.out, "mc_claims.json"), res)
        with open(os.path.join(self.out, "mc_claims_report.md"), "w") as fh:
            fh.write(render_report(res))
        self.write_draws_csv(os.path.join(self.out, "draws_lhs.csv"))
        _log("wrote %s, %s and draws_lhs.csv" % (os.path.join(self.out, "mc_claims.json"), os.path.join(self.out, "mc_claims_report.md")))
        return res

    # draws_lhs.csv: one row per Latin-hypercube draw (the format of notes/mc_results_2026-11-02/draws_lhs.csv, which was
    # taken from that run's checkpoint): six input dimensions at their physical values (5 decimals) and the outputs that
    # code/mc_report_tex.py reads, in percent (4 decimals) or years; a payback that never happens is written as inf
    CSV_INPUTS = ("kappa_2025", "kappa_abs", "varpi", "G", "tau", "a_min")
    CSV_OUTPUTS = (("R2028_net", "net.R_2028", 100), ("R2031_net", "net.R_2031", 100), ("R2036_net", "net.R_2036", 100),
                   ("R2036_none", "lb.R_2036", 100), ("R2036_all", "ub.R_2036", 100), ("R2036_net_combined", "net.boot.R_2036", 100),
                   ("Gstar_2025", "Gstar_2025", 100), ("Gstar_2025_cc6", "Gstar_2025_cc6", 100),
                   ("compute_share_2025", "c_c_2025", 100), ("payback_years", "net.pb.pb_u", 1),
                   ("payback_years_central_exec", "net.B.pb.pb_u", 1), ("npv_pct_revenue", "net.pb.npv", 100),
                   ("realized_share_2036", "s_2036", 100), ("levers_growth_engine_first_count", "lev.net.n_ge_first", 1),
                   ("completed_program_plus_G_2036", "net.completed_2036", 100))

    def write_draws_csv(self, path):
        n = self.n_lhs
        cols = ["draw"] + [nm for nm in self.CSV_INPUTS if nm in _M["idx"]] + [c_ for c_, _, _ in self.CSV_OUTPUTS]
        ins = {nm: [dim_value(self.dims[_M["idx"][nm]], float(self.U[i, _M["idx"][nm]])) for i in range(n)]
               for nm in self.CSV_INPUTS if nm in _M["idx"]}

        def f_(x, nd):
            x = float(x)
            if x != x:
                return ""
            if math.isinf(x):
                return "inf" if x > 0 else "-inf"
            return repr(round(x, nd))
        tmp = path + ".tmp"
        with open(tmp, "w") as fh:
            fh.write(",".join(cols) + "\n")
            for i in range(n):
                row = [str(i)] + [f_(ins[nm][i], 5) for nm in self.CSV_INPUTS if nm in ins]
                for _, key, sc in self.CSV_OUTPUTS:
                    x = self.R[key][i] if key in self.R else float("nan")
                    row.append(f_(x * sc, 4) if key != "lev.net.n_ge_first" else f_(x, 1))
                fh.write(",".join(row) + "\n")
        os.replace(tmp, path)


def _unit_of(key):
    """'yr' for years, 'x' for ratios and counts, 'pts' for shares of revenue and percent a year (shown x 100)."""
    if key.endswith(("pb_u", "pb_d", "cross", "gap", "complete")) or key == "complete_year":
        return "yr"
    if key.endswith("ratio") or key == "pull_multiple" or key.startswith("lev."):
        return "x"
    return "pts"


def compare_runs(a, b, other_path=""):
    """Compare this run (a) with a run of the same box under another seed (b): for every claim test the
    holds-everywhere verdict, the margin minimum and the extremes of the tested quantity over the box; the quoted
    quantities and the central-path levels (extremes and the 5-95% spread of the draws); the Sobol group indices of the
    two sensitivity claims with their 95% intervals. Differences are b - a, in points for shares of revenue."""
    box = lambda r: [(d["name"], repr(d["lo"]), repr(d["hi"]), d["law"]) for d in r["dims"]]
    ta = {t["tid"]: t for c in a["claims"] for t in c["tests"]}
    tb = {t["tid"]: t for c in b["claims"] for t in c["tests"]}
    sc = lambda key: 100.0 if _unit_of(key) == "pts" else 1.0
    dif = lambda x, y, s: None if (x is None or y is None) else s * (y - x)
    tests, dmax = {}, {"pts": 0.0, "yr": 0.0, "x": 0.0}
    for tid in sorted(set(ta) & set(tb)):
        x, y = ta[tid], tb[tid]
        s_, u_ = sc(x["key"]), _unit_of(x["key"])
        rec = dict(key=x["key"], unit=u_, holds_a=x["holds_everywhere"], holds_b=y["holds_everywhere"],
                   agree=bool(x["holds_everywhere"] == y["holds_everywhere"]),
                   margin_min_a=x["margin_min"], margin_min_b=y["margin_min"],
                   min_a=x["quantity"]["min"], min_b=y["quantity"]["min"], max_a=x["quantity"]["max"], max_b=y["quantity"]["max"],
                   d_min=dif(x["quantity"]["min"], y["quantity"]["min"], s_), d_max=dif(x["quantity"]["max"], y["quantity"]["max"], s_),
                   share_a=x.get("share_holds_uniform"), share_b=y.get("share_holds_uniform"))
        for d_ in (rec["d_min"], rec["d_max"]):
            if d_ is not None and math.isfinite(d_):
                dmax[u_] = max(dmax[u_], abs(d_))
        tests[tid] = rec
    qa, qb = {q["key"]: q for q in a.get("quantities", [])}, {q["key"]: q for q in b.get("quantities", [])}
    quants = {k_: {f_ + s_: q[k_].get(f_) for f_ in ("min", "max", "lhs_p05", "lhs_p95") for s_, q in (("_a", qa), ("_b", qb))}
              for k_ in sorted(set(qa) & set(qb))}
    levels = {k_: {f_ + s_: lv[k_].get(f_) for f_ in ("box_min", "box_max", "lhs_p05", "lhs_p95", "combined_band_90")
                   for s_, lv in (("_a", a["levels"]), ("_b", b["levels"]))} for k_ in sorted(set(a["levels"]) & set(b["levels"]))}
    sens = {}
    for sa in a.get("sensitivity_claims", []):
        sb = {s_["id"]: s_ for s_ in b.get("sensitivity_claims", [])}.get(sa["id"])
        if sb is None:
            continue
        rec = dict(distribution_free_a=sa["distribution_free"]["holds"], distribution_free_b=sb["distribution_free"]["holds"])
        if sa.get("sobol") and sb.get("sobol"):
            rec.update(sobol_a=sa["sobol"]["holds"], sobol_b=sb["sobol"]["holds"], largest_a=sa["sobol"]["largest_group"],
                       largest_b=sb["sobol"]["largest_group"], holds_ci_a=sa["sobol"].get("holds_ci"),
                       holds_ci_b=sb["sobol"].get("holds_ci"),
                       ST_a={k_: v_ for k_, v_ in sa["sobol"].items() if k_.startswith("ST_")},
                       ST_b={k_: v_ for k_, v_ in sb["sobol"].items() if k_.startswith("ST_")})
        rec["agree"] = bool(all(rec.get(k_ + "_a") == rec.get(k_ + "_b") for k_ in ("distribution_free", "sobol", "largest")))
        sens[sa["id"]] = rec
    n_agree = sum(t_["agree"] for t_ in tests.values())
    return dict(this=dict(seed=a["meta"]["args"]["seed"], config_hash=a["meta"]["config_hash"], n=a["design"]["n_lhs"]),
                other=dict(seed=b["meta"]["args"]["seed"], config_hash=b["meta"]["config_hash"], n=b["design"]["n_lhs"],
                           path=other_path, created=b["meta"].get("created")),
                same_box=bool(box(a) == box(b)), same_seed=bool(a["meta"]["args"]["seed"] == b["meta"]["args"]["seed"]),
                tests=tests, quantities=quants, levels=levels, sensitivity_claims=sens,
                summary=dict(n_tests=len(tests), n_agree=n_agree, disagree=[k_ for k_, t_ in tests.items() if not t_["agree"]],
                             max_abs_diff_extreme_pts=dmax["pts"], max_abs_diff_extreme_years=dmax["yr"],
                             max_abs_diff_extreme_ratio=dmax["x"], sensitivity_agree=bool(all(s_["agree"] for s_ in sens.values()))),
                note="differences are other minus this; 'pts' = points of revenue or percent a year; a verdict that differs "
                     "between seeds marks a claim decided by a few points of the box")


def _salib_version():
    try:
        from importlib.metadata import version
        return version("SALib")
    except Exception:
        try:
            import SALib
            return getattr(SALib, "__version__", "?")
        except Exception:
            return "?"


# ======================================================================================================================
# Markdown report
# ======================================================================================================================
def _f(x, nd):
    return "n/a" if x is None else ("%." + str(nd) + "f") % x


def _pct(x, nd=1):
    if x is None:
        return "n/a"
    if isinstance(x, float) and (math.isinf(x) or math.isnan(x)):
        return "never" if x > 0 else "n/a"
    return ("%." + str(nd) + "f") % (100 * x)


def _qfmt(key, x):
    if x is None:
        return "n/a (never)"
    if key.endswith(("pb_u", "pb_d", "cross", "gap", "complete", "ratio")) or key in ("complete_year", "pull_multiple") \
            or key.startswith("lev."):
        return "%.2f" % x
    return _pct(x) + ("%" if "Gstar" in key or key.startswith("s_") else "")


def render_report(r):
    L = []
    m = r["meta"]
    UL = r.get("law_label", UNIFORM_LABEL)          # the law of the main box (the accountability sub-box is uniform)
    L.append("# Joint-parameter stress test of Paper 1's headline claims")
    L.append("")
    if m["small_n_warning"]:
        L.append("> **SMALL-N TEST RUN** (n = %d LHS draws). Shares and sampled extremes are indicative only; rerun "
                 "with the default --n 10000 for the reported results." % m["args"]["n"])
        L.append("")
    L.append("Generated by `code/mc_claims.py` v%s on %s (config `%s`; Python %s, numpy %s, %s, %s cores)." % (
        m["version"], m["created"], m["config_hash"], m["python"], m["numpy"], m["machine"], m["cpu_count"]))
    L.append("")
    L.append("**Framing.** " + r["framing"])
    L.append("")
    L.append("**How to read.** *Holds everywhere* is the primary, distribution-free result: the claim's test is "
             "evaluated at every Latin-hypercube draw, at the box corners listed under Design, and at the extremum found "
             "by a vertex search for each tested quantity; 'yes' means no evaluated point violates it (a search, not a "
             "proof). *Margin min* is the smallest value of the test's margin (positive = holds). *Range* is the min and "
             "max of the tested quantity over the box. *Uniform share* is the share of LHS draws in which the claim "
             "holds: " + UL + ".")
    L.append("")
    rp = r["reproduction"]
    L.append("## Reproduction of the paper at the centre of the box")
    L.append("")
    L.append("%d checks, all passed: **%s**. Shadow run of `code/calibrate_horizons.py` byte-identical to the committed "
             "outputs: %s." % (len(rp["checks"]), "yes" if rp["all_passed"] else "NO",
                               ", ".join("%s %s" % (k_, "yes" if v_ else "NO") for k_, v_ in rp["shadow_outputs_byte_identical"].items())))
    jd = rp.get("shadow_json_numeric_diff") or {}
    if jd.get("n_leaves_differ"):
        L.append("")
        L.append("The shadow JSON differs from the committed one in %d leaves (largest relative difference %s; "
                 "blocks: %s), typically a last-digit effect of library versions; the checks above assert the claim "
                 "inputs within a relative 1e-12 and the quoted macros exactly." % (
                     jd["n_leaves_differ"], "%.1e" % jd["max_rel_diff"] if jd.get("max_rel_diff") is not None else "non-numeric",
                     ", ".join(jd["blocks"])))
    L.append("")
    L.append("<details><summary>Checks</summary>")
    L.append("")
    for c in rp["checks"]:
        L.append("- %s %s%s" % ("ok" if c["ok"] else "FAIL", c["check"],
                                (" (expected %s, got %s)" % (c.get("expected"), c.get("got"))) if "expected" in c else ""))
    L.append("")
    L.append("</details>")
    L.append("")
    d = r["design"]
    L.append("## Design")
    L.append("")
    L.append("- %d Latin-hypercube draws and %d corner points (seed %d). Corners: %s." % (d["n_lhs"], d["n_corners"], d["seed"], d["corner_rule"]))
    L.append("- Strata (not sampled): " + "; ".join("`%s` %s" % (k_, v_) for k_, v_ in d["strata"].items()) + ".")
    L.append("- Compute share mode: `%s`; anchor range: `%s`; varpi extended to the BCG win zone: %s." % (d["cc_mode"], d["anchor_range"], d["bcg_win"]))
    L.append("- Conditional variants hold a claim's own named conditions at their central values: " +
             "; ".join("`%s` %s" % (k_, v_["label"]) for k_, v_ in d["variants"].items() if k_ != "full") + ".")
    t = m["timing"]
    if t.get("s_per_1000_draws"):
        L.append("- Runtime: %.1f s per 1,000 draws (%.1f draws/s with %d workers); searches %.0f s; Sobol %.0f s." % (
            t["s_per_1000_draws"], t["draws_per_s"], t.get("workers", m["args"]["workers"]), t.get("search_s", 0), t.get("sobol_s", 0)))
    if m.get("memory"):
        mm = m["memory"]
        L.append("- Memory (peak resident, VmHWM): main process %s MB, largest worker %s MB, estimated peak total %s MB%s." % (
            _f(mm.get("main_maxrss_mb"), 0), _f(mm.get("largest_child_maxrss_mb"), 0), _f(mm.get("estimated_peak_total_mb"), 0),
            "" if mm.get("largest_child_maxrss_mb") is not None else " (no worker task ran in this invocation: resumed from the checkpoint)"))
    L.append("")
    L.append("## Parameter box (%d dimensions)" % len(r["dims"]))
    L.append("")
    L.append(dims_markdown(r["dims"]))
    L.append("")
    oc = r["omitted_coupling"]["tau_in_anchor"]
    L.append("Omitted coupling (as in the code): the anchor is inverted at tau = 0.18 whatever the drawn tau; drawing tau "
             "into the anchor would move the median netted intercept by %+.2f / %+.2f points at tau = 0.15 / 0.21 "
             "(all S&M: %+.2f / %+.2f)." % (100 * oc["net"]["0.15"], 100 * oc["net"]["0.21"], 100 * oc["ub"]["0.15"], 100 * oc["ub"]["0.21"]))
    L.append("")
    L.append("## Claims")
    L.append("")
    L.append("| Test | Variant | Stratum | Test made | Holds everywhere | Margin min | Central | Range over box | "
             "Share of draws holding (" + UL + ") |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for c in r["claims"]:
        for tt in c["tests"]:
            q = tt["quantity"]
            k_ = tt["key"]
            L.append("| %s | %s | %s | %s | **%s** | %s | %s | %s to %s | %s |" % (
                tt["tid"], tt["variant"], tt["stratum"] or "-", tt["test"] + (" (domain: %s; outside it at %.1f%% of draws)" % (
                    "target above anchor", 100 * tt["share_outside_domain_uniform"]) if tt.get("domain") else ""),
                "yes" if tt["holds_everywhere"] else "NO", _f(tt["margin_min"], 4), _qfmt(k_, q["central"]),
                _qfmt(k_, q["min"]), _qfmt(k_, q["max"]), _f(tt["share_holds_uniform"], 3)))
    L.append("")
    L.append("Variants: `full` = the whole box; `A` = fixed prices and k = 0 (the path's stated conditions); `B` = also "
             "central execution; `C` = compute share at 6% of revenue at 2025 prices. Percentages are points of revenue "
             "or percent a year; payback quantities are years.")
    L.append("")
    for c in r["claims"]:
        L.append("### %s. %s" % (c["id"], c["title"]))
        L.append("")
        L.append("*Text:* \"%s\" (%s)." % (c["quote"], c["where"]))
        L.append("")
        for tt in c["tests"]:
            line = "- **%s** (%s%s): %s. Holds everywhere: **%s**; margin min %s (%s); share of draws holding %s (%s)." % (
                tt["tid"], tt["variant_label"], (", " + STRATUM_LABEL[tt["stratum"]]) if tt["stratum"] else "", tt["test"],
                "yes" if tt["holds_everywhere"] else "NO", _f(tt["margin_min"], 4), tt["worst_point_found_by"],
                _f(tt["share_holds_uniform"], 3), UL)
            L.append(line)
            if tt.get("note"):
                L.append("  - Note: %s." % tt["note"])
            if tt.get("domain"):
                L.append("  - Domain: %s; outside it at %.1f%% of LHS draws (%d points in all; min of target minus anchor "
                         "%.4f). Points outside the domain are not counted as failures." % (
                             tt["domain_text"], 100 * tt["share_outside_domain_uniform"], tt["n_outside_domain"], tt["domain_min"]))
            if tt.get("kind") == "count":
                L.append("  - Count values over the box: %s; b_M box [%.4f, %.4f], central %.4f." % (
                    tt.get("count_values_on_grid"), tt["b_M_box"][0], tt["b_M_box"][1], tt["b_M_central"]))
                if tt.get("b_M_interval_with_stated_count") is not None:
                    L.append("  - b_M interval on which the stated count holds: %s (switch points %s)%s." % (
                        tt["b_M_interval_with_stated_count"], ", ".join("%.4f" % x for x in tt.get("switch_points_b_M", [])),
                        ("; share of all 999 bootstrap draws of b_M inside it: %.3f" % tt["bootstrap_share_all_draws"])
                        if tt.get("bootstrap_share_all_draws") is not None else ""))
                if tt.get("b_M_fail_range_on_grid"):
                    L.append("  - Fails for b_M in [%.4f, %.4f]%s." % (tuple(tt["b_M_fail_range_on_grid"]) + (
                        (" with phi in [%.2f, %.2f]" % tuple(tt["phi_fail_range_on_grid"])) if tt.get("phi_fail_range_on_grid") else "",)))
            if tt.get("worst_point"):
                L.append("  - Least favorable point (most influential dimensions): %s." % tt["worst_point"])
            fl = tt.get("failure")
            if fl:
                L.append("  - Failure region: fails in %s%% of LHS draws (%s)." % (_f(100 * fl["share_fail_uniform"], 1), UL))
                for ru in fl.get("tree_rules", [])[:3]:
                    L.append("    - tree leaf: %s: fails in %.0f%% of the leaf's draws (%d of %d; %.0f%% of all failures)." % (
                        ru["rule"], 100 * ru["fail_share_in_leaf"], ru["n_fail"], ru["n"], 100 * ru["share_of_failures"]))
                for un in fl.get("univariate", []):
                    L.append("    - %s, others %s: %s." % (un["dim"], "at central values" if un["reference"] == "central" else "at the least favorable point", un["result"]))
        L.append("")
    L.append("## Sensitivity rankings")
    L.append("")
    for sc in r["sensitivity_claims"]:
        L.append("### %s. %s" % (sc["id"], sc["title"]))
        L.append("")
        L.append("*Text:* \"%s\" (%s)." % (sc["quote"], sc["where"]))
        L.append("")
        df = sc["distribution_free"]
        L.append("- Distribution-free (%s): **%s**; largest group: `%s`." % (df["test"], "holds" if df["holds"] else "does NOT hold", df["largest_group"]))
        if sc.get("sobol"):
            so = sc["sobol"]
            L.append("- Sobol (%s; %s): **%s**; largest group: `%s`." % (so["test"], so["label"], "holds" if so["holds"] else "does NOT hold", so["largest_group"]))
            cis = [(k_[3:-3], so[k_[:-3]], so[k_]) for k_ in sorted(so) if k_.startswith("ST_") and k_.endswith("_ci") and so.get(k_)]
            if cis:
                L.append("  - 95%% intervals of ST: %s; ordering %s at the 95%% intervals (the leader's lower bound above every "
                         "other group's upper bound; %s)." % (
                             "; ".join("%s %.3f [%.3f, %.3f]" % (nm, v_, c_[0], c_[1]) for nm, v_, c_ in cis),
                             "survives" if so.get("holds_ci") else "does NOT survive", so.get("ci_method", "bootstrap")))
        L.append("")
    L.append("### Comparison with Table 6 (one-at-a-time tornado, 2036, netted central path)")
    L.append("")
    L.append("| Tornado row | Tornado rank | Tornado swing | Box group | Group swing (others central) | Sobol S1 | Sobol ST |")
    L.append("|---|---|---|---|---|---|---|")
    for row in r["tornado_comparison"]:
        L.append("| %s | %d | %.1f | %s | %s | %s | %s |" % (
            row["tornado_row"], row["tornado_rank"], 100 * row["tornado_swing"], row["group"],
            ("%.1f" % (100 * row["group_swing_box"])) if row.get("group_swing_box") is not None else "-",
            ("%.3f" % row["sobol_S1"]) if row.get("sobol_S1") is not None else "-",
            ("%.3f" % row["sobol_ST"]) if row.get("sobol_ST") is not None else "-"))
    L.append("")
    L.append("Swings in points. The tornado's anchor row uses the firm-year quartiles and its surplus row an upper-quartile "
             "firm-year under the all-S&M bound; in the box the anchor is the bootstrap of the median and the surplus enters "
             "only the all-S&M stratum, so both have little or no weight for the netted central path.")
    L.append("")
    sob = r.get("sobol")
    if sob:
        L.append("### Sobol indices (%s)" % sob["law"])
        L.append("")
        L.append("N = %d, %s; factor indices: %s; group indices: %s; %d model evaluations." % (
            sob["N"], sob["base_design"], sob["backend_factors"], sob["backend_groups"], sob["n_evaluations"]))
        if sob.get("ci"):
            L.append("")
            L.append("95%% confidence intervals: factors, %s; groups, %s." % (sob["ci"]["factors"], sob["ci"]["groups"]))
        L.append("")

        def ci_(v_, k_):
            c_ = v_.get(k_ + "_ci")
            if c_ is None and v_.get(k_ + "_conf") is not None:            # runs before round 3: SALib half-width only
                c_ = [v_[k_] - v_[k_ + "_conf"], v_[k_] + v_[k_ + "_conf"]]
            return "[%.3f, %.3f]" % tuple(c_) if c_ else "-"
        for oname in ("net.R_2036", "Gstar_2025"):
            o = sob["outputs"][oname]
            L.append("**%s** (mean %.3f, variance %.5f). Groups by total index:" % (oname, o["mean"], o["var"]))
            L.append("")
            L.append("| Group | S1 | S1 95% CI | ST | ST 95% CI |")
            L.append("|---|---|---|---|---|")
            for g_, v_ in sorted(o["groups"].items(), key=lambda kv: -kv[1]["ST"]):
                L.append("| %s | %.3f | %s | %.3f | %s |" % (g_, v_["S1"], ci_(v_, "S1"), v_["ST"], ci_(v_, "ST")))
            L.append("")
            top = sorted(o["factors"].items(), key=lambda kv: -kv[1]["ST"])[:10]
            L.append("Top factors by ST (95% CI): " + ", ".join("`%s` %.3f %s" % (k_, v_["ST"], ci_(v_, "ST")) for k_, v_ in top) + ".")
            L.append("")
    scmp = r.get("seed_comparison")
    if scmp:
        su = scmp["summary"]
        L.append("## Second seed")
        L.append("")
        L.append("This run (seed %s, config `%s`, %d draws) against `%s` (seed %s, config `%s`, %d draws, created %s); same box: "
                 "**%s**%s." % (scmp["this"]["seed"], scmp["this"]["config_hash"], scmp["this"]["n"], scmp["other"]["path"],
                                scmp["other"]["seed"], scmp["other"]["config_hash"], scmp["other"]["n"], scmp["other"]["created"],
                                "yes" if scmp["same_box"] else "NO", " (the seeds are equal)" if scmp["same_seed"] else ""))
        L.append("")
        L.append("- Holds everywhere: the two runs agree on %d of %d tests%s." % (
            su["n_agree"], su["n_tests"], (" (they differ on %s)" % ", ".join(su["disagree"])) if su["disagree"] else ""))
        L.append("- Largest change of a box extreme of a tested quantity: %.2f points of revenue or percent a year, %.2f years, "
                 "%.3f (ratios and counts)." % (su["max_abs_diff_extreme_pts"], su["max_abs_diff_extreme_years"],
                                                su["max_abs_diff_extreme_ratio"]))
        L.append("- Sensitivity rankings (S1, S2) agree: **%s**." % ("yes" if su["sensitivity_agree"] else "NO"))
        L.append("")
        L.append("| Test | Holds (this) | Holds (other) | Min (this / other) | Max (this / other) |")
        L.append("|---|---|---|---|---|")
        for tid, t_ in scmp["tests"].items():
            L.append("| %s | %s | %s | %s / %s | %s / %s |" % (
                tid, "yes" if t_["holds_a"] else "NO", "yes" if t_["holds_b"] else "NO", _qfmt(t_["key"], t_["min_a"]),
                _qfmt(t_["key"], t_["min_b"]), _qfmt(t_["key"], t_["max_a"]), _qfmt(t_["key"], t_["max_b"])))
        L.append("")
    L.append("## Quoted quantities over the box")
    L.append("")
    L.append("| Quantity | Central | Box min | Box max | 5-95% of draws (" + UL + ") | Extremes from |")
    L.append("|---|---|---|---|---|---|")

    def qf(x, unit):
        if x is None:
            return "n/a"
        if unit == "pct":
            return "%.1f" % (100 * x)
        if unit == "yr":
            return "%.1f" % x
        return "%.2f" % x
    for qq in r.get("quantities", []):
        L.append("| %s | %s | %s | %s | %s to %s | %s%s |" % (
            qq["label"], qf(qq["central"], qq["unit"]), qf(qq["min"], qq["unit"]), qf(qq["max"], qq["unit"]),
            qf(qq["lhs_p05"], qq["unit"]), qf(qq["lhs_p95"], qq["unit"]), qq["extremes_from"],
            ("; never pays back at %d points" % qq["n_never"]) if qq.get("n_never") else ""))
    L.append("")
    L.append("Percent of revenue or percent a year unless stated. Payback quantities are evaluated where the target lies "
             "above the anchor intercept (the program raises the margin). 'Sampled' extremes are the min and max over the "
             "LHS draws and corners only; 'sampled + search' adds the vertex search for the quantity.")
    L.append("")
    L.append("## Central-path levels: box range, uniform spread and combined band")
    L.append("")
    L.append("| Score | Central | Paper's 90% anchor interval | Box min | Box max | 5-95% of draws (" + UL + ") | "
             "Share of draws in the paper's interval (" + UL + ") | Combined 90% band (conditional on " + UL + ") |")
    L.append("|---|---|---|---|---|---|---|---|")
    for k_, v_ in r["levels"].items():
        cb = v_.get("combined_band_90")
        L.append("| %s | %s | [%s, %s] | %s | %s | %s to %s | %.3f | %s |" % (
            k_, _pct(v_["central"], 0), _pct(v_["paper_anchor_interval_90"][0], 0), _pct(v_["paper_anchor_interval_90"][1], 0),
            _pct(v_["box_min"], 0), _pct(v_["box_max"], 0), _pct(v_["lhs_p05"], 0), _pct(v_["lhs_p95"], 0),
            v_["share_in_paper_interval_uniform"], ("[%s, %s]" % (_pct(cb[0], 0), _pct(cb[1], 0))) if cb else "-"))
    L.append("")
    L.append("Combined band: conditional on the uniform-over-ranges assumption for every scenario dimension, with the anchor "
             "intercept drawn from all 999 firm-cluster bootstrap draws (not truncated); the paper's interval redraws only the "
             "anchor block (intercept, market growth, maintenance base) and holds the program and the target fixed.")
    L.append("")
    am = r["amin"]
    L.append("## Accountability floor (separate sub-box)")
    L.append("")
    L.append(am["note"] + ". %d LHS draws and all %d corners of its %d dimensions; thresholds 1%% and 5%% a year as strata." % (
        am["n_lhs"], am["n_corners"], len(am["dims"])))
    L.append("")
    L.append("| Dimension | Low | Central | High | Class | Source |")
    L.append("|---|---|---|---|---|---|")
    for dd in am["dims"]:
        L.append("| %s %s | %g | %g | %g | %s | %s |" % (dd["name"], dd["label"], dd["lo"], dd["central"], dd["hi"], dd["cls"], dd["src"]))
    L.append("")
    L.append("| Test | Threshold | Claim | Holds everywhere | Margin min | Range | Share of draws holding (" + UNIFORM_LABEL + ") |")
    L.append("|---|---|---|---|---|---|---|")
    for tt in am["tests"]:
        q = tt["quantity"]
        L.append("| %s | %s | %s | **%s** | %s | %s to %s%s | %.3f |" % (
            tt["tid"], tt["threshold"], tt["claim"], "yes" if tt["holds_everywhere"] else "NO", _f(tt["margin_min"], 5),
            "%.5f" % q["min"] if q["min"] is not None else "n/a", "%.5f" % q["max"] if q["max"] is not None else "n/a",
            (" (%d points with no admissible design)" % q["n_inf"]) if q.get("n_inf") else "", tt["share_holds_uniform"]))
        for ru in tt.get("failure_rules", [])[:2]:
            L.append("| | | fails where %s (%.0f%% of leaf) | | | | |" % (ru["rule"], 100 * ru["fail_share"]))
    L.append("")
    L.append("## Run")
    L.append("")
    L.append("```")
    L.append("python3 code/mc_claims.py --n %d --seed %d --workers %d --out %s%s" % (
        m["args"]["n"], m["args"]["seed"], m["args"]["workers"], m["args"]["out"],
        (" --compare-to %s" % m["args"]["compare_to"]) if m["args"].get("compare_to") else ""))
    L.append("```")
    L.append("")
    return "\n".join(L) + "\n"


def main(argv=None):
    args = parse_args(argv)
    run = Runner(args)
    if args.print_dims:
        snap_dir = os.path.join(os.path.abspath(args.out), "_shadow")
        g = load_calibration(snap_dir)
        snap = build_snapshot(g)
        init_worker(snap, run.opts)
        print(dims_markdown(_M["dims"]))
        return 0
    t_all = time.time()
    run.setup()
    if args.verify_only:
        for c in run.checks:
            print(("ok   " if c["ok"] else "FAIL ") + c["check"] + ((" (expected %s, got %s)" % (c.get("expected"), c.get("got"))) if "expected" in c else ""))
        return 0
    _log("box: %d dimensions; config %s; checkpoint %s" % (run.k, run.cfg, run.ck))
    run.start_pool(max(1, args.workers))
    try:
        run.run_draws()
        run.merged_timing()
        if args.stop_after == "draws":
            return 0
        run.run_search()
        run.merged_timing()
        if args.stop_after == "search":
            return 0
        if not args.no_sobol:
            run.run_sobol()
            run.merged_timing()
        if args.stop_after == "sobol":
            return 0
        run.run_amin()
        swings = run.group_swings()
        run.analyse()
    finally:
        run.stop_pool()
    run.timing["total_s"] = time.time() - t_all
    run.write_outputs(swings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
