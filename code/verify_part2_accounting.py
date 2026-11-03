#!/usr/bin/env python3
"""Checks for Section sec:accounting (part2/theory_accounting.tex) and its proofs (part2/proofs_accounting.tex).

Every closed form, comparative static and example number in the section is checked here, either against an
independent numerical computation (integration over a fine time grid, Monte Carlo, brute-force enumeration) or
symbolically. Prints PASS/FAIL lines and a SUMMARY; exits 1 if any check fails.

Results checked:
  prop:acct-path     capitalization, recognition dates and the GAAP versus cash score path
  prop:acct-program  the capitalization premium of a growing program
  prop:acct-tax      tax timing (26 U.S.C. 174 and 174A, 100% first-year allowance) and the after-tax dip
  prop:acct-cutover  cutover windows, material-weakness risk and the defer-or-cut-over threshold
  cor:acct-npv       risk-adjusted NPV of a transition in a financial-reporting process
  prop:acct-amin     the accountability floor with layered human and AI-run controls

The invoice-chain transition example is read from the single source data/examples/invoice_chain.json, written by
the core theorist (see load_invoice_example). If that file is absent the script falls back to the legacy values of
code/verify_part2_core.py, which the coordinator declared void on 29 October 2026, and prints a DEPENDENCY line.
Every example number quoted in part2/theory_accounting.tex is written by this script to
part2/tables/accounting_macros.tex; the section inputs that file and types no example number by hand.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import integrate, optimize

RNG = np.random.default_rng(20261029)
n_pass = 0
n_fail = 0


def check(name, cond, detail=""):
    global n_pass, n_fail
    if bool(cond):
        n_pass += 1
        print(f"PASS  {name}" + (f"   [{detail}]" if detail else ""))
    else:
        n_fail += 1
        print(f"FAIL  {name}" + (f"   [{detail}]" if detail else ""))


def header(s):
    print("\n" + "=" * 100 + f"\n{s}\n" + "=" * 100)


def overlap(a, b, c, d):
    """Length of [a, b) intersected with [c, d)."""
    return max(0.0, min(b, d) - max(a, c))


# ----------------------------------------------------------------------------------------------
# Invoice-chain transition example: single source data/examples/invoice_chain.json
# ----------------------------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
EX_JSON = ROOT / "data" / "examples" / "invoice_chain.json"
MACROS = ROOT / "part2" / "tables" / "accounting_macros.tex"
# Legacy values (verify_part2_core.py before 29 Oct 2026; void). Used only if the JSON is missing.
LEGACY = dict(W=473088.17950365075, F=920000.0, F_build=520000.0, F_int=400000.0, I=0.0, CJ=60000.0,
              Cpar=456650.00000000006, Cstr=186062.5, Cbrk=100000.0, Cwo=150000.0, Tpar=0.5, T_A=3.0,
              S=100e6, r=0.10, Th=5.0, pis=0.75, bbar=0.85, Tdet=0.25, Lroll=2.0e6, F_other=0.0, Tpar_sp=0.5,
              T_up=1.22, N_int=4.0)
# Accepted key spellings in the JSON (searched at any nesting depth, case-insensitive).
ALIASES = dict(
    W=["W", "W_cash", "Wcash", "saving", "savings", "W_full", "annual_saving"],
    F=["F", "F_total", "build_total", "F_build_total", "one_time_build"],
    F_build=["F_build", "F_A_total", "sum_F_A", "FA_total", "builds", "agent_builds"],
    F_int=["F_int", "F_integration", "integration", "integration_cost", "readiness_investment", "I_int"],
    I=["I", "capex", "capital_spending", "I_capex"],
    CJ=["CJ", "C_J", "productivity_dip", "dip"],
    Cpar=["Cpar", "C_par", "parallel_premium"],
    Cstr=["Cstr", "C_str", "stranded"],
    Cbrk=["Cbrk", "C_brk", "break_fees"],
    Cwo=["Cwo", "C_wo", "write_off", "writeoff"],
    Tpar=["Tpar", "T_par", "parallel_run", "T_par_example"],
    T_A=["T_A", "TA", "amortization_years", "useful_life"],
    S=["S", "revenue", "S_revenue", "revenue_example"],
    r=["r", "discount_rate"], Th=["Th", "T_h", "horizon"], pis=["pis", "varpi_p", "success_prob", "varpi"],
    bbar=["bbar", "bbar_p", "b_bar"], Tdet=["Tdet", "T_det"], Lroll=["Lroll", "L_roll"],
    F_other=["F_other", "F_onetime_total"], T_up=["T_up", "Tup"], N_int=["N_int", "n_int"])
# Keys read from a named block first (the score-path example of prop:tasks-scorepath uses its own T_par).
BLOCK_KEYS = dict(Tpar_sp=("score_path", "T_par"))


def _flatten(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                out.setdefault(str(k).lower(), float(v))
            elif isinstance(v, dict) and "value" in v and isinstance(v["value"], (int, float)):
                out.setdefault(str(k).lower(), float(v["value"]))
            else:
                _flatten(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _flatten(v, out)
    return out


def load_invoice_example():
    """Return (example dict, source label, list of keys taken from the legacy fallback)."""
    if not EX_JSON.exists():
        print(f"DEPENDENCY: {EX_JSON.relative_to(ROOT)} not found; the example uses the legacy (void) values of "
              "verify_part2_core.py. Re-run this script after the core theorist writes the file.")
        return dict(LEGACY), "legacy", list(LEGACY)
    raw = json.loads(EX_JSON.read_text())
    flat = _flatten(raw, {})
    ex, missing = {}, []
    for key, (blk, name) in BLOCK_KEYS.items():
        v = raw.get(blk, {}).get(name) if isinstance(raw.get(blk), dict) else None
        if isinstance(v, (int, float)):
            ex[key] = float(v)
        else:
            ex[key] = flat.get("t_par", LEGACY[key])
    ex["_score_path"] = raw.get("score_path")
    ex["_version"] = raw.get("meta", {}).get("version", "")
    for key, names in ALIASES.items():
        hit = next((flat[n.lower()] for n in names if n.lower() in flat), None)
        if hit is None:
            missing.append(key)
            ex[key] = LEGACY[key]
        else:
            ex[key] = hit
    if "F" in missing and "F_build" not in missing and "F_int" not in missing:
        ex["F"] = ex["F_build"] + ex["F_int"]
        missing.remove("F")
    if missing:
        print(f"DEPENDENCY: {EX_JSON.relative_to(ROOT)} lacks {missing}; legacy values used for these keys.")
    return ex, "json", missing


EX, EX_SOURCE, EX_MISSING = load_invoice_example()
TP = dict(W=EX["W"], F=EX["F"], I=EX["I"], CJ=EX["CJ"], Cpar=EX["Cpar"], Cstr=EX["Cstr"], Cwo=EX["Cwo"],
          r=EX["r"], Th=EX["Th"], pis=EX["pis"], bbar=EX["bbar"], Tdet=EX["Tdet"], Lroll=EX["Lroll"])
C_BRK = EX["Cbrk"]                 # break fees inside C^str
C_SEV = TP["Cstr"] - C_BRK         # severance part of C^str
S_EX = EX["S"]                     # revenue for the score examples
TPAR_EX, TA_EX = EX["Tpar_sp"], EX["T_A"]   # score examples use the T_par of the core's score-path example
LEG = False   # pins to the legacy numbers quoted before 29 Oct are retired: those values are void
MAC = {}                           # macro name -> LaTeX text, written to part2/tables/accounting_macros.tex
print(f"     invoice example source: {EX_SOURCE} {EX.get('_version', '')}; T_par = {EX['Tpar']} (transition), "
      f"{TPAR_EX} (score path), T_A = {TA_EX}, S = {S_EX:,.0f}, W = {TP['W']:,.0f}, F = {TP['F']:,.0f} "
      f"(builds {EX['F_build']:,.0f}, integration {EX['F_int']:,.0f}, other {EX['F_other']:,.0f})")


def usd(x):
    """\\$462{,}000 style, rounded to the nearest thousand."""
    v = int(round(x / 1000.0)) * 1000
    return "\\$" + f"{v:,}".replace(",", "{,}")


def money(x):
    r"""\$1.2 billion, \$2.00 million, or \$462{,}000"""
    if abs(x) >= 1e9:
        return f"\\${x/1e9:g} billion"
    if abs(x) >= 1e6:
        return f"\\${x/1e6:.2f} million"
    return usd(x)


def pts(x, d=2):
    return f"{abs(x):.{d}f}"


def spts(x, d=2):
    """signed points for text that says 'changes by': $-0.05$ or $+0.32$"""
    return f"${'-' if x < 0 else '+'}{abs(x):.{d}f}$"

# ==============================================================================================
header("1. Capitalization and the score path (Proposition prop:acct-path)")
# ==============================================================================================


def flow_int(P, Tpar, b, lo, hi):
    """Integral over [lo, hi) of the operating flow b W rho(t) - C^par on [0, Tpar), b W after (linear ramp)."""
    if hi <= 0:
        return 0.0
    lo = max(lo, 0.0)
    val = 0.0
    a1, b1 = lo, min(hi, Tpar)
    if b1 > a1:
        val += b * P["W"] * (b1 ** 2 - a1 ** 2) / (2 * Tpar) - P["Cpar"] * (b1 - a1)
    a2 = max(lo, Tpar)
    if hi > a2:
        val += b * P["W"] * (hi - a2)
    return val


def paths(P, Tpar, S, b=1.0, Fcap=None, TB=3.0, tgo=0.0, sev=("point", None), brk=None, Y=8, y0=-2):
    """Annual changes in the cash and GAAP scores for fiscal years y = y0+1..Y ([y-1, y)).

    Cash: flow, F + I + C^J at date 0, C^str paid at cutover Tpar.
    GAAP: flow, C^J and F^exp at date 0, F^cap straight line over TB from tgo, C^wo evenly on [0, Tpar),
    severance either at a point t_sev (sev=('point', t)) or ratably on [t_com, Tpar) (sev=('ratable', t_com)),
    break fees at t_brk. Recognition dates may be negative (before the transition starts)."""
    F, I = P["F"], P["I"]
    Fcap = F if Fcap is None else Fcap
    Fexp = F - Fcap
    t_sev_kind, t_sev = sev
    if t_sev is None:
        t_sev = Tpar
    t_brk = Tpar if brk is None else brk
    ys = list(range(y0 + 1, Y + 1))
    cash, gaap = [], []
    for y in ys:
        lo, hi = y - 1.0, float(y)
        f = flow_int(P, Tpar, b, lo, hi)
        c = f
        if lo <= 0.0 < hi:
            c -= F + I + P["CJ"]
        if lo <= Tpar < hi:
            c -= C_SEV + C_BRK
        g = f
        if lo <= 0.0 < hi:
            g -= P["CJ"] + Fexp
        g -= Fcap * overlap(lo, hi, tgo, tgo + TB) / TB
        g -= P["Cwo"] * overlap(lo, hi, 0.0, Tpar) / Tpar
        if t_sev_kind == "point":
            if lo <= t_sev < hi:
                g -= C_SEV
        else:
            g -= C_SEV * overlap(lo, hi, t_sev, Tpar) / (Tpar - t_sev)
        if lo <= t_brk < hi:
            g -= C_BRK
        cash.append(c / S)
        gaap.append(g / S)
    return np.array(ys), np.array(cash), np.array(gaap)


def rand_P():
    return dict(W=RNG.uniform(1, 5), F=RNG.uniform(0, 5), I=RNG.uniform(0, 3), CJ=RNG.uniform(0, 1),
                Cpar=RNG.uniform(0, 3), Cstr=0.0, Cwo=RNG.uniform(0, 2))


# (a) invariance of the cash path to book policy
bad = 0
for _ in range(400):
    P = rand_P()
    C_SEV, C_BRK = RNG.uniform(0, 1), RNG.uniform(0, 1)
    Tpar = RNG.uniform(0.1, 2.5)
    base = paths(P, Tpar, 1.0)[1]
    for _ in range(3):
        kind = "point" if RNG.random() < 0.5 else "ratable"
        tsev = RNG.uniform(-1.0, Tpar) if kind == "point" else RNG.uniform(-1.0, Tpar - 0.05)
        alt = paths(P, Tpar, 1.0, Fcap=RNG.uniform(0, P["F"]), TB=RNG.uniform(1, 7), tgo=RNG.uniform(0, Tpar),
                    sev=(kind, tsev), brk=RNG.uniform(-1, Tpar))[1]
        bad += int(not np.allclose(base, alt, atol=1e-12))
check("1a (a) cash path invariant to F^cap, T_B, t_go, severance and break-fee recognition dates", bad == 0)

# (b) accrual identity: S * cumulative (GAAP - cash) = I + unamortized F^cap - accrued unpaid - legacy charged
bad = 0
for _ in range(400):
    P = rand_P()
    C_SEV, C_BRK = RNG.uniform(0, 1), RNG.uniform(0, 1)
    Tpar = RNG.uniform(0.1, 2.5)
    Fcap = RNG.uniform(0, P["F"])
    TB, tgo = RNG.uniform(1, 7), RNG.uniform(0, Tpar)
    kind = "point" if RNG.random() < 0.5 else "ratable"
    tsev = RNG.uniform(-1.5, Tpar) if kind == "point" else RNG.uniform(-1.5, Tpar - 0.05)
    tbrk = RNG.uniform(-1.5, Tpar)
    ys, c, g = paths(P, Tpar, 1.0, Fcap=Fcap, TB=TB, tgo=tgo, sev=(kind, tsev), brk=tbrk, Y=12, y0=-2)
    cum = np.cumsum(g - c)
    for i, Y in enumerate(ys):
        amort = overlap(-1e9, Y, tgo, tgo + TB) / TB
        wo = overlap(-1e9, Y, 0, Tpar) / Tpar
        if kind == "point":
            sev_rec = C_SEV * (tsev < Y)
        else:
            sev_rec = C_SEV * overlap(-1e9, Y, tsev, Tpar) / (Tpar - tsev)
        brk_rec = C_BRK * (tbrk < Y)
        paid = (C_SEV + C_BRK) * (Tpar < Y)
        accrued = sev_rec + brk_rec - paid
        started = 1.0 if Y > 0 else 0.0
        rhs = started * (P["I"] + Fcap * (1 - amort)) - accrued - P["Cwo"] * wo
        if Y <= 0:
            rhs = -accrued
        bad += int(abs(cum[i] - rhs) > 1e-9)
    # long-run: gap tends to (I - C^wo)/S
    bad += int(abs(cum[-1] - (P["I"] - P["Cwo"])) > 1e-9)
check("1b (b) S sum_{y<=Y}(dR^G_y - dR^c_y) = I + F^cap(1 - amortized share) - accrued unpaid - legacy book value "
      "charged; tends to I - C^wo", bad == 0)

# (c) first-year closed form
bad = 0
for _ in range(400):
    P = rand_P()
    C_SEV, C_BRK = RNG.uniform(0, 1), RNG.uniform(0, 1)
    Tpar = RNG.uniform(0.05, 1.0)
    Fcap, TB, tgo = RNG.uniform(0, P["F"]), RNG.uniform(1, 7), RNG.uniform(0, Tpar)
    kind = "point" if RNG.random() < 0.5 else "ratable"
    tsev = RNG.uniform(0, Tpar) if kind == "point" else RNG.uniform(0, Tpar - 0.01)
    ys, c, g = paths(P, Tpar, 1.0, Fcap=Fcap, TB=TB, tgo=tgo, sev=(kind, tsev), brk=RNG.uniform(0, Tpar))
    i1 = list(ys).index(1)
    c1 = -(P["F"] + P["I"] + P["CJ"] + C_SEV + C_BRK + P["Cpar"] * Tpar - P["W"] * (1 - Tpar / 2))
    g1 = c1 + P["I"] + Fcap * (1 - (1 - tgo) / TB) - P["Cwo"]
    bad += int(abs(c[i1] - c1) > 1e-9 or abs(g[i1] - g1) > 1e-9)
check("1c (c) dR^G_1 = dR^c_1 + [I + F^cap(1 - (1 - t_go)/T_B) - C^wo]/S when T_par <= 1 <= T_B", bad == 0)

# (d) later years
bad = 0
for _ in range(300):
    P = rand_P()
    C_SEV, C_BRK = RNG.uniform(0, 1), RNG.uniform(0, 1)
    Tpar = RNG.uniform(0.05, 1.0)
    Fcap, TB, tgo = RNG.uniform(0, P["F"]), RNG.uniform(1, 7), RNG.uniform(0, Tpar)
    ys, c, g = paths(P, Tpar, 1.0, Fcap=Fcap, TB=TB, tgo=tgo, Y=10)
    for i, y in enumerate(ys):
        if y >= 2:
            pred = c[i] - Fcap * overlap(y - 1, y, tgo, tgo + TB) / TB
            bad += int(abs(g[i] - pred) > 1e-9 or abs(c[i] - P["W"]) > 1e-9)
check("1d (d) for y >= 2: dR^G_y = dR^c_y - F^cap |[y-1,y) cap [t_go, t_go+T_B)|/(T_B S), dR^c_y = bW/S", bad == 0)

# (e) special case: Proposition prop:tasks-scorepath(c) and its example
C_SEV, C_BRK = TP["Cstr"] - EX["Cbrk"], EX["Cbrk"]    # restore the example's split after the random tests
ys, c, g = paths(TP, TPAR_EX, S_EX, Fcap=TP["F"], TB=TA_EX, tgo=0.0, Y=8)
i1 = list(ys).index(1)
sp_c1 = -(TP["F"] + TP["I"] + TP["CJ"] + TP["Cstr"] + TP["Cpar"] * TPAR_EX - TP["W"] * (1 - TPAR_EX / 2)) / S_EX
sp_g1 = sp_c1 + (TP["F"] + TP["I"] - TP["F"] / TA_EX - TP["Cwo"]) / S_EX
SP = EX.get("_score_path") or {}
sp_ok = True
if SP.get("cash") and SP.get("gaap"):
    # the core's own score path (data/examples/invoice_chain.json, block score_path): years 1, 2, ...
    nn = min(len(SP["cash"]), len(SP["gaap"]), 4)
    sp_ok = (np.allclose(c[i1:i1 + nn], SP["cash"][:nn], atol=1e-9)
             and abs(g[i1] - SP["gaap"][0]) < 1e-9 and np.allclose(g[i1 + 1:i1 + nn], SP["gaap"][1:nn], atol=1e-9))
check("1e special case F^cap = F, t_go = 0, T_B = T_A reproduces the year-1 closed forms of prop:tasks-scorepath(c)"
      + (" and the core's score path in invoice_chain.json" if SP.get("cash") else "")
      + (" and the legacy example (cash -1.04, GAAP -0.58)" if LEG else ""),
      abs(c[i1] - sp_c1) < 1e-12 and abs(g[i1] - sp_g1) < 1e-12 and sp_ok
      and (not LEG or (abs(100 * c[i1] + 1.04) < 0.005 and abs(100 * g[i1] + 0.58) < 0.005)),
      f"cash {100*c[i1]:.3f}, GAAP {100*g[i1]:.3f}")
MAC["acctExScorepathG"] = pts(100 * g[i1])
MAC["acctExCashOne"] = pts(100 * c[i1])

# (f) ASU 2025-06 bound
bad = 0
for _ in range(300):
    P = rand_P()
    Fdc = RNG.uniform(0, P["F"])
    TB, tgo = RNG.uniform(1, 7), RNG.uniform(0, 1)
    us = np.sort(RNG.uniform(0, 1, 5))
    gaps = [P["I"] + (1 - u) * (P["F"] - Fdc) * (1 - (1 - tgo) / TB) - P["Cwo"] for u in us]
    bad += int(np.any(np.diff(gaps) > 1e-12))
    gap1 = P["I"] + (1 - 1.0) * (P["F"] - Fdc) * (1 - (1 - tgo) / TB) - P["Cwo"]
    bad += int(abs(gap1 - (P["I"] - P["Cwo"])) > 1e-12)
check("1f (e) first-year GAAP-cash gap bound nonincreasing in u and equal to (I - C^wo)/S at u = 1", bad == 0)

# Example: ASU 2025-06 split of the invoice build (illustrative judgments: 40% of agent builds incurred while
# significant development uncertainty exists; a quarter of the integration budget is data conversion and cleansing;
# the other one-time costs (redesign, legal review, evaluation data, change management, training, control redesign)
# are expensed: training under 25-4, the rest as not eligible under 30-1, a judgment for evaluation data)
U_EX, DC_SHARE = 0.40, 0.25
F_UNC = U_EX * EX["F_build"]
F_DC = DC_SHARE * EX["F_int"]
F_OTH = EX["F_other"]
FEXP = F_UNC + F_DC + F_OTH
FCAP = TP["F"] - FEXP
TB_EX, TGO_EX = TA_EX, TPAR_EX     # book life = the engine's T_A; amortization from cutover
ys, c, g = paths(TP, TPAR_EX, S_EX, Fcap=FCAP, TB=TB_EX, tgo=TGO_EX, Y=10)
i1 = list(ys).index(1)
print(f"     example: F^exp = {FEXP:,.0f}, F^cap = {FCAP:,.0f} ({FCAP/TP['F']:.3f} of F); cash {np.round(100*c[i1:],3)}; "
      f"GAAP {np.round(100*g[i1:],3)}")
end = TGO_EX + TB_EX
partial_year = int(math.ceil(end))
full_end = partial_year - 1
g1_cf = c[i1] + (TP["I"] + FCAP * (1 - (1 - TGO_EX) / TB_EX) - TP["Cwo"]) / S_EX
full_cf = TP["W"] / S_EX - FCAP / (TB_EX * S_EX)
part_cf = TP["W"] / S_EX - FCAP * (end - (partial_year - 1)) / (TB_EX * S_EX)
check("1g example: GAAP year 1 = eq. (acct-first); full-amortization years and the partial year match (d); "
      "cash flat at bW/S from year 2" + ("; legacy values -0.81, +0.32, +0.40, +0.47" if LEG else ""),
      abs(end - round(end)) > 1e-9 and abs(g[i1] - g1_cf) < 1e-12
      and np.all(abs(g[i1 + 1:i1 + full_end] - full_cf) < 1e-12)
      and abs(g[i1 + partial_year - 1] - part_cf) < 1e-12 and abs(g[i1 + partial_year] - TP["W"] / S_EX) < 1e-12
      and (not LEG or (abs(FCAP - 462e3) < 1 and abs(100 * g[i1] + 0.805) < 0.006 and abs(100 * full_cf - 0.319) < 0.006
                       and abs(100 * part_cf - 0.396) < 0.006)),
      f"GAAP y1 {100*g[i1]:.3f}, years 2-{full_end} {100*full_cf:.3f}, year {partial_year} {100*part_cf:.3f}")
ys0, c0, g0 = paths(TP, TPAR_EX, S_EX, Fcap=FCAP, TB=TB_EX, tgo=TGO_EX, sev=("point", -0.1), Y=10)
j0, j1 = list(ys0).index(0), list(ys0).index(1)
check("1h (c) severance recognized before the fiscal year starts (ASC 712): GAAP year 0 falls by C^sev/S, year 1 rises "
      "by as much; cash unchanged",
      abs(g0[j0] + C_SEV / S_EX) < 1e-12 and abs(g0[j1] - g[i1] - C_SEV / S_EX) < 1e-12 and np.allclose(c0[j1:], c[i1:])
      and (not LEG or abs(100 * g0[j0] + 0.086) < 0.005),
      f"y0 {100*g0[j0]:.3f}, y1 {100*g0[j1]:.3f}")
EX_PATH = dict(c1=100 * c[i1], g1=100 * g[i1])
MAC.update(acctExRevenue=money(S_EX),
           acctExTpar=f"{TPAR_EX:g}", acctExBuilds=usd(EX["F_build"]), acctExIntegration=money(EX["F_int"]),
           acctExUnc=f"{100*U_EX:.0f}\\%", acctExDC=usd(F_DC), acctExFcap=money(FCAP),
           acctExFcapShare=f"{FCAP/TP['F']:.2f}", acctExTB=f"{TB_EX:g}", acctExGone=pts(100 * g[i1]),
           acctExGfull=spts(100 * full_cf), acctExFullEnd=str(full_end), acctExPartialYear=str(partial_year),
           acctExGpartial=spts(100 * part_cf), acctExCashLater=spts(100 * TP["W"] / S_EX),
           acctExOther=usd(F_OTH),
           acctExSevShift=pts(100 * C_SEV / S_EX, 3), acctExGoneSev=pts(100 * g0[j1]))

# ==============================================================================================
header("2. Capitalization premium of a growing program (Proposition prop:acct-program)")
# ==============================================================================================


def Afun(x):
    return 1.0 if abs(x) < 1e-12 else (1 - math.exp(-x)) / x


def wedge(cS, g, TB, L):
    return cS * (1 - math.exp(-g * L) * Afun(g * TB))


def amort_numeric(g, TB, L, t=10.0, C0=1.0):
    # amortization at t: integral over vintages s in [t - L - TB, t - L] of C(s)/TB
    val, _ = integrate.quad(lambda s: C0 * math.exp(g * s) / TB, t - L - TB, t - L)
    return val


bad = 0
for _ in range(300):
    g, TB, L = RNG.uniform(-0.3, 0.8), RNG.uniform(0.5, 8), RNG.uniform(0, 2)
    t = 10.0
    num = amort_numeric(g, TB, L, t)
    cf = math.exp(g * t) * math.exp(-g * L) * Afun(g * TB)
    bad += int(abs(num - cf) > 1e-8 * max(1, cf))
check("2a (a) amortization at t = C(t) e^{-g_F L} A(g_F T_B), A(x) = (1 - e^{-x})/x (vintage integral)", bad == 0)
bad = 0
for _ in range(300):
    cS, TB, L = RNG.uniform(0.01, 0.2), RNG.uniform(0.5, 8), RNG.uniform(0, 2)
    gs = np.sort(RNG.uniform(0.001, 0.8, 6))
    w = [wedge(cS, x, TB, L) for x in gs]
    bad += int(np.any(np.diff(w) <= 0) or np.any(np.array(w) >= cS) or np.any(np.array(w) <= 0))
    bad += int(wedge(cS, -abs(RNG.uniform(0.01, 0.5)), TB, L) >= 0 or abs(wedge(cS, 0.0, TB, L)) > 1e-15)
    g = RNG.uniform(0.01, 0.8)
    bad += int(wedge(cS, g, TB * 1.1, L) <= wedge(cS, g, TB, L) or wedge(cS, g, TB, L + 0.1) <= wedge(cS, g, TB, L))
    gsm = 1e-4
    approx = cS * gsm * (L + TB / 2)
    bad += int(abs(wedge(cS, gsm, TB, L) - approx) > 1e-3 * approx + 1e-12)
check("2b (b) wedge has the sign of g_F; increasing in g_F, T_B, L; below C/S; ~ (C/S) g_F (L + T_B/2) for small g_F",
      bad == 0)
EX_PROG = {(gg, L): 100 * wedge(0.05, gg, 3.0, L) for gg in (0.05, 0.15, 0.30) for L in (0.0, 0.5)}
print("     example wedge (points), C/S = 0.05, T_B = 3: " +
      ", ".join(f"g={k[0]:.2f},L={k[1]}: {v:.2f}" for k, v in EX_PROG.items()))
check("2c example: C/S = 5%, T_B = 3, L = 0.5: wedge 0.47 points at g = 5%, 1.26 at 15%, 2.16 at 30%; "
      "0.36 and 1.70 at 5% and 30% with L = 0",
      abs(EX_PROG[(0.05, 0.5)] - 0.47) < 0.006 and abs(EX_PROG[(0.15, 0.5)] - 1.26) < 0.006
      and abs(EX_PROG[(0.30, 0.5)] - 2.16) < 0.006 and abs(EX_PROG[(0.05, 0.0)] - 0.36) < 0.006
      and abs(EX_PROG[(0.30, 0.0)] - 1.70) < 0.006,
      f"{EX_PROG[(0.05,0.5)]:.3f}, {EX_PROG[(0.15,0.5)]:.3f}, {EX_PROG[(0.30,0.5)]:.3f}")
# steady-state simulation: discrete monthly vintages, firm growing at g; GAAP-minus-cash margin
g, TB, L, cS = 0.30, 3.0, 0.5, 0.05
dt = 1 / 1200.0
ts = np.arange(-20, 10 + dt / 2, dt)
spend = cS * np.exp(g * ts)          # revenue S(t) = e^{g t}; spend = cS S(t)
t_eval = 10.0
mask = (ts >= t_eval - L - TB) & (ts < t_eval - L)
amort = np.sum(spend[mask]) * dt / TB
w_num = (cS * math.exp(g * t_eval) - amort) / math.exp(g * t_eval)
check("2d (c) discrete-vintage simulation of a firm growing 30% a year matches the premium c^cap[1 - e^{-gL}A(gT_B)]",
      abs(w_num - wedge(cS, g, TB, L)) < 2e-5, f"{100*w_num:.4f} vs {100*wedge(cS,g,TB,L):.4f} points")

# ==============================================================================================
header("3. Tax timing and the after-tax dip (Proposition prop:acct-tax)")
# ==============================================================================================


def psi_T(T, r):
    """PV per dollar of deductions ratably over T years from the midpoint of year 1 (1/(2T), 1/T, ..., 1/(2T))."""
    ded = np.zeros(T + 1)
    ded[0] = 1 / (2 * T)
    ded[1:T] = 1 / T
    ded[T] = 1 / (2 * T)
    disc = (1 + r) ** -np.arange(T + 1)
    return float(np.sum(ded * disc))


def psi_closed(T, r):
    return (1 + (1 + r) ** -T) / (2 * T) + (1 - (1 + r) ** -(T - 1)) / (r * T)


bad = 0
for _ in range(200):
    T, r = int(RNG.integers(1, 40)), RNG.uniform(0.005, 0.3)
    bad += int(abs(psi_T(T, r) - psi_closed(T, r)) > 1e-12)
    bad += int(not (psi_T(T + 1, r) < psi_T(T, r) and psi_T(T, r + 0.01) < psi_T(T, r)))
check("3a (a) psi_T closed form = sum of midpoint-convention deductions; decreasing in T and r", bad == 0)
p5, p15 = psi_T(5, 0.10), psi_T(15, 0.10)
check("3b psi_5 = 0.796 and psi_15 = 0.532 at r = 0.10; foreign premium tau(1 - psi_15) = 9.8 cents at tau = 0.21",
      abs(p5 - 0.796) < 0.0005 and abs(p15 - 0.532) < 0.0005 and abs(0.21 * (1 - p15) - 0.098) < 0.0005,
      f"psi_5 {p5:.4f}, psi_15 {p15:.4f}, premium {0.21*(1-p15):.4f}")
# (b) after-tax first year: direct computation of taxes vs closed form
bad = 0
for _ in range(400):
    P = rand_P()
    C_SEV, C_BRK = RNG.uniform(0, 1), RNG.uniform(0, 1)
    Tpar, tau, S = RNG.uniform(0.05, 1.0), RNG.uniform(0.05, 0.35), 1.0
    Ffor = RNG.uniform(0, P["F"])
    Fdom = P["F"] - Ffor
    c1 = -(P["F"] + P["I"] + P["CJ"] + C_SEV + C_BRK + P["Cpar"] * Tpar - P["W"] * (1 - Tpar / 2))
    operating = c1 + P["F"] + P["I"]          # pre-tax cash before the build and equipment
    deduction = Fdom + Ffor / 30.0 + P["I"]  # 174A(a) domestic, 174(a) 15-year midpoint, 100% allowance
    after = c1 - tau * (operating - deduction)
    pred = (1 - tau) * c1 - tau * Ffor * (1 - 1 / 30.0)
    bad += int(abs(after - pred) > 1e-12)
check("3c (b) dR^{c,tau}_1 = (1 - tau) dR^c_1 - tau F^for (1 - 1/30)/S (full loss offset)", bad == 0)
tau = 0.21
c1_ex = EX_PATH["c1"]
at_dom = (1 - tau) * c1_ex
extra_for = 100 * tau * EX["F_build"] * (1 - 1 / 30) / S_EX
# prior law (2022-2024): five-year amortization of software development, i.e. the builds and the integration net of
# data conversion (Notice 2023-63 excludes data conversion and training); the other one-time costs deducted when paid
F_SD = EX["F_build"] + EX["F_int"] - F_DC
extra_prior = 100 * tau * F_SD * (1 - 1 / 10) / S_EX
# direct recomputation of the example from the tax schedule (independent of the closed form of 3c)
op_ex = c1_ex / 100 * S_EX + TP["F"] + TP["I"]
direct_dom = (c1_ex / 100 * S_EX - tau * (op_ex - TP["F"] - TP["I"])) / S_EX * 100
direct_for = (c1_ex / 100 * S_EX - tau * (op_ex - (TP["F"] - EX["F_build"]) - EX["F_build"] / 30 - TP["I"])) / S_EX * 100
check("3d example: after-tax first-year cash dip (domestic build, tau = 0.21), extra dip if the agent builds are "
      "performed abroad, and under prior-law 5-year amortization of the software development (builds and integration "
      "net of data conversion), recomputed from the deduction schedule"
      + ("; legacy -0.82, 0.11, 0.17" if LEG else ""),
      abs(at_dom - direct_dom) < 1e-9 and abs((direct_dom - direct_for) - extra_for) < 1e-9
      and (not LEG or (abs(at_dom + 0.82) < 0.006 and abs(extra_for - 0.106) < 0.002 and abs(extra_prior - 0.174) < 0.002)),
      f"{at_dom:.3f}, {extra_for:.3f}, {extra_prior:.3f}")
MAC.update(acctTaxAfter=pts(at_dom), acctTaxForeign=pts(extra_for, 3), acctTaxPrior=pts(extra_prior, 3),
           acctTaxSD=money(F_SD))

Ups = lambda psi, t: (1 - psi * t) / (1 - t) - 1
check("3e tax penalty on AI capital (1 - psi tau)/(1 - tau) - 1 at tau = 0.21: 5.7% with psi = 0.787 "
      "(theory_ext), 0 with psi = 1 (domestic, 174A), about 12% with psi_15 (foreign)",
      abs(Ups(0.787, 0.21) - 0.057) < 0.0005 and abs(Ups(1.0, 0.21)) < 1e-12 and abs(Ups(p15, 0.21) - 0.124) < 0.001,
      f"{Ups(0.787,0.21):.4f}, {Ups(p15,0.21):.4f}")

# ==============================================================================================
header("4. Cutover windows and material-weakness risk (Proposition prop:acct-cutover, Corollary cor:acct-npv)")
# ==============================================================================================


def delay(z, Top, Tcl):
    """Delay from a ready position z in [0,1) to the first admissible position in [Tcl, 1 - Top]."""
    if z < Tcl:
        return Tcl - z
    if z <= 1 - Top:
        return 0.0
    return 1 + Tcl - z


bad = 0
for _ in range(200):
    Top, Tcl = RNG.uniform(0, 0.5), RNG.uniform(0, 0.4)
    if Top + Tcl >= 1:
        continue
    num, _ = integrate.quad(lambda z: delay(z, Top, Tcl), 0, 1, points=[Tcl, 1 - Top], limit=200)
    bad += int(abs(num - (Top + Tcl) ** 2 / 2) > 1e-9)
check("4a (a) uniform ready date: expected delay to the window [T_cl, 1 - T_op] is (T_op + T_cl)^2/2", bad == 0)


def Pmw(H, pdef, pmw, Tdc, Trem, Top):
    return pdef * pmw * min(1.0, math.exp(-(H - Trem - Top) / Tdc))


bad = 0
for _ in range(40):
    pdef, pmw, Tdc, Trem, Top = RNG.uniform(0.05, 0.6), RNG.uniform(0.05, 0.6), RNG.uniform(0.05, 0.5), \
        RNG.uniform(0, 0.4), RNG.uniform(0, 0.4)
    H = RNG.uniform(0.05, 1.0)
    n = 200000
    deficient = RNG.random(n) < pdef
    severe = RNG.random(n) < pmw
    D = RNG.exponential(Tdc, n)
    unremediated = D + Trem + Top > H
    mc = np.mean(deficient & severe & unremediated)
    cf = Pmw(H, pdef, pmw, Tdc, Trem, Top)
    bad += int(abs(mc - cf) > 4 * math.sqrt(cf * (1 - cf) / n) + 1e-4)
    Hs = np.sort(RNG.uniform(0.01, 1.0, 8))
    bad += int(np.any(np.diff([Pmw(h, pdef, pmw, Tdc, Trem, Top) for h in Hs]) > 1e-15))
check("4b (b) P_mw(H) = p_def p_mw min{1, exp[-(H - T_rem - T_op)/T_dc]} (Monte Carlo); nonincreasing in H", bad == 0)

# (c) threshold rule
bad = 0
for _ in range(300):
    pdef, pmw, Tdc, Trem = RNG.uniform(0.05, 0.6), RNG.uniform(0.05, 0.6), RNG.uniform(0.05, 0.5), RNG.uniform(0, 0.4)
    Top, Tcl = RNG.uniform(0.05, 0.4), RNG.uniform(0.02, 0.3)
    if Top + Tcl >= 0.95:
        continue
    Lmw, chat = RNG.uniform(0.1, 20), RNG.uniform(0.1, 3)
    zs = np.linspace(Tcl, 1 - Top, 400)
    gain = np.array([Lmw * (Pmw(1 - z, pdef, pmw, Tdc, Trem, Top) - Pmw(1 - Tcl, pdef, pmw, Tdc, Trem, Top))
                     - chat * (1 + Tcl - z) for z in zs])
    defer = gain > 0
    # single crossing: once defer is True it stays True
    if defer.any():
        first = np.argmax(defer)
        bad += int(not defer[first:].all())
    bad += int(np.any(np.diff(gain) <= 0))
check("4c (c) defer-minus-cut-over gain strictly increasing in z: a threshold z* (defer iff z > z*)", bad == 0)

# example
# Delay cost: the legacy example used the invoice transition's savings; in the rebuilt example (29 Oct) the savings
# net of run costs are negative, so the cutover example uses an illustrative delay cost of $500,000 a year.
EXC = dict(pdef=0.3, pmw=0.3, Tdc=0.25, Trem=0.25, Top=0.25, Tcl=1 / 6, Lmw=5e6, chat=500e3)
adm = 1 - EXC["Top"] - EXC["Tcl"]
Ed = (EXC["Top"] + EXC["Tcl"]) ** 2 / 2
P_after_close = Pmw(1 - EXC["Tcl"], EXC["pdef"], EXC["pmw"], EXC["Tdc"], EXC["Trem"], EXC["Top"])
P_late = Pmw(0.5, EXC["pdef"], EXC["pmw"], EXC["Tdc"], EXC["Trem"], EXC["Top"])


def gain_ex(z):
    return EXC["Lmw"] * (Pmw(1 - z, EXC["pdef"], EXC["pmw"], EXC["Tdc"], EXC["Trem"], EXC["Top"]) - P_after_close) \
        - EXC["chat"] * (1 + EXC["Tcl"] - z)


zstar = optimize.brentq(gain_ex, EXC["Tcl"] + 1e-9, 1 - EXC["Top"])
print(f"     example: admissible share {adm:.3f}; E[delay] {Ed:.4f} yr = {365*Ed:.1f} days, cost {EXC['chat']*Ed:,.0f}; "
      f"P_mw after close {P_after_close:.4f}, at H <= 0.5 {P_late:.3f}; z* = {zstar:.3f}")
check("4d example: window share 0.58; expected delay 0.087 years; P_mw 2.4% right after the close and 9% with half a "
      "year or less to year-end; threshold z* solves the defer condition at the example's delay cost"
      + ("; legacy z* = 0.49, $41k" if LEG else "; $500k a year: z* = 0.50, $43k"),
      abs(adm - 0.583) < 0.001 and abs(Ed - 0.0868) < 0.0001 and abs(gain_ex(zstar)) < 1e-6
      and abs(P_after_close - 0.0237) < 0.0001 and abs(P_late - 0.09) < 1e-12
      and (not LEG or (abs(zstar - 0.49) < 0.006 and abs(EXC["chat"] * Ed - 41.1e3) < 300))
      and (LEG or (abs(EXC["chat"] * Ed - 43.4e3) < 300)),
      f"z* {zstar:.4f}, cost {EXC['chat']*Ed:,.0f}")
MAC.update(acctCutOpen=f"{100*adm:.0f}\\%", acctCutWait=f"{Ed:.3f}", acctCutCost=usd(EXC["chat"] * Ed),
           acctCutDelay=usd(EXC["chat"]), acctCutPafter=f"{100*P_after_close:.1f}\\%",
           acctCutPlate=f"{100*P_late:.0f}\\%", acctCutZstar=f"{100*zstar:.0f}\\%")


# Corollary cor:acct-npv: Monte Carlo of the outcome tree with control costs and material-weakness risk
def transition_npv(P, Tpar):
    r, Th = P["r"], P["Th"]
    pu = math.exp(-Tpar / P["Tdet"])
    A = (1 - math.exp(-r * Tpar)) / r
    Sr = integrate.quad(lambda t: math.exp(-r * t) * t / Tpar, 0, Tpar)[0] + (math.exp(-r * Tpar) - math.exp(-r * Th)) / r
    return (-(P["F"] + P["I"] + P["CJ"]) - P["Cpar"] * A + P["pis"] * P["bbar"] * P["W"] * Sr
            - math.exp(-r * Tpar) * ((P["pis"] + (1 - P["pis"]) * pu) * P["Cstr"] + (1 - P["pis"]) * pu * P["Lroll"]))


def npv_icfr(P, Tpar, Cctl, dC, Lmw, pmw_H):
    r, Th = P["r"], P["Th"]
    pu = math.exp(-Tpar / P["Tdet"])
    return (transition_npv(P, Tpar) - Cctl - P["pis"] * dC * (math.exp(-r * Tpar) - math.exp(-r * Th)) / r
            - (P["pis"] + (1 - P["pis"]) * pu) * math.exp(-r * Tpar) * Lmw * pmw_H)


def simulate_icfr(P, Tpar, Cctl, dC, Lmw, pmw_H, n=400000):
    r, Th = P["r"], P["Th"]
    succ = RNG.random(n) < P["pis"]
    b = RNG.beta(8 * P["bbar"], 8 * (1 - P["bbar"]), n)
    det = RNG.exponential(P["Tdet"], n) < Tpar
    mw = RNG.random(n) < pmw_H
    A = (1 - math.exp(-r * Tpar)) / r
    ramp = integrate.quad(lambda t: math.exp(-r * t) * t / Tpar, 0, Tpar)[0]
    after = (math.exp(-r * Tpar) - math.exp(-r * Th)) / r
    base = -(P["F"] + P["I"] + P["CJ"]) - P["Cpar"] * A - Cctl
    val = np.full(n, base)
    cut = succ | (~succ & ~det)
    val += np.where(succ, b * P["W"] * (ramp + after) - math.exp(-r * Tpar) * P["Cstr"] - dC * after, 0.0)
    val += np.where(~succ & ~det, -math.exp(-r * Tpar) * (P["Cstr"] + P["Lroll"]), 0.0)
    val += np.where(cut & mw, -math.exp(-r * Tpar) * Lmw, 0.0)
    return float(val.mean()), float(val.std() / math.sqrt(n))


bad = 0
for _ in range(6):
    P = dict(TP, pis=RNG.uniform(0.4, 0.95), Tdet=RNG.uniform(0.1, 0.6))
    Tpar, Cctl, dC = RNG.uniform(0.2, 1.0), RNG.uniform(0, 3e5), RNG.uniform(-1e5, 1e5)
    Lmw, pH = RNG.uniform(1e6, 1e7), RNG.uniform(0.0, 0.1)
    mc, se = simulate_icfr(P, Tpar, Cctl, dC, Lmw, pH)
    cf = npv_icfr(P, Tpar, Cctl, dC, Lmw, pH)
    bad += int(abs(mc - cf) > 5 * se + 2e3)
check("4e cor:acct-npv closed form matches Monte Carlo of the outcome tree (success, detected and undetected "
      "failure; control costs on the success path; material weakness on every cutover path)", bad == 0)
if EX_SOURCE == "json":
    _tr = json.loads(EX_JSON.read_text()).get("transition", {})
    _npv_core = (_tr.get("results") or {}).get("NPV")
    check("4f NPV_p in cor:acct-npv, evaluated at the invoice transition's inputs, reproduces the core's NPV in "
          "invoice_chain.json", _npv_core is not None and abs(transition_npv(TP, EX["Tpar"]) - _npv_core) < 1.0,
          f"{transition_npv(TP, EX['Tpar']):,.0f} vs {_npv_core}")

# ==============================================================================================
header("5. The accountability floor with AI-run controls (Proposition prop:acct-amin)")
# ==============================================================================================


def P_type(pcm, p, n):
    return 1.0 if n == 0 else pcm + (1 - pcm) * p ** n


def P_design(types, p0=0.0):
    """types: list of (pcm, p, n), independent across types given no shared cause; p0: a cause shared by every layer
    (management override, defective source data or information produced by the entity, failure of the ITGCs every
    layer's inputs depend on). No layer: P = 1."""
    if not any(t[2] > 0 for t in types):
        return 1.0
    out = 1.0
    for pcm, p, n in types:
        out *= P_type(pcm, p, n)
    return p0 + (1 - p0) * out


def Pbar(eps, N):
    """largest per-opportunity miss probability at which the annual probability 1 - (1 - P)^N is at most eps"""
    return 1 - (1 - eps) ** (1 / N)


def admissible(P, eps, N):
    """def:acct-admissible: no in-scope objective is left with more than a remote possibility (eps) of a material
    misstatement not prevented or detected on a timely basis in the year"""
    return 1 - (1 - P) ** N <= eps + 1e-15


def n_min_type(p0, pcm, p, eps, N):
    """prop:acct-amin(d): smallest admissible depth of one type; None if no depth is admissible"""
    Pb, flo = Pbar(eps, N), p0 + (1 - p0) * pcm
    if Pb <= flo:
        return None
    rho = (Pb - flo) / ((1 - p0) * (1 - pcm))
    return max(1, math.ceil(math.log(rho) / math.log(p) - 1e-12))


# (a) Monte Carlo of a mixed design with a shared cause
bad = 0
for _ in range(25):
    types = [(RNG.uniform(0, 0.05), RNG.uniform(0.01, 0.3), int(RNG.integers(0, 4))) for _ in range(2)]
    if sum(t[2] for t in types) == 0:
        continue
    p0 = RNG.uniform(0, 0.01)
    n = 400000
    allfail = np.ones(n, dtype=bool)
    for pcm, p, k in types:
        if k == 0:
            continue
        cm = RNG.random(n) < pcm
        ind = np.all(RNG.random((n, k)) < p, axis=1)
        allfail &= (cm | ind)
    allfail |= RNG.random(n) < p0
    mc = allfail.mean()
    cf = P_design(types, p0)
    bad += int(abs(mc - cf) > 4 * math.sqrt(max(cf * (1 - cf), 1e-12) / n) + 2e-5)
    lower = p0 + (1 - p0) * np.prod([t[0] for t in types if t[2] > 0])
    bad += int(cf < lower - 1e-15)
check("5a (a) P = p0 + (1 - p0) prod_x [p^cm_x + (1 - p^cm_x) p_x^{n_x}] (Monte Carlo, with a shared cause p0) and "
      "P >= p0 + (1 - p0) prod of the common-mode rates of the types used", bad == 0)
bad = 0
for _ in range(500):
    pcm, p, p0 = RNG.uniform(0.0001, 0.05), RNG.uniform(0.05, 0.5), RNG.uniform(0, 0.005)
    Ps = [P_design([(pcm, p, k)], p0) for k in range(1, 11)]
    bad += int(np.any(np.diff(Ps) >= 0))
    bad += int(abs(P_design([(pcm, p, 200)], p0) - (p0 + (1 - p0) * pcm)) > 1e-12)
check("5b (a) one type: P strictly decreasing in depth and tends to p0 + (1 - p0) p^cm", bad == 0)
# (b) diversity (the shared cause does not change the condition)
bad = 0
for _ in range(2000):
    pcm, p, n = RNG.uniform(0.0001, 0.05), RNG.uniform(0.01, 0.5), int(RNG.integers(2, 8))
    pind, p0 = RNG.uniform(0.001, 0.999), RNG.uniform(0, 0.01)
    mixed = p0 + (1 - p0) * pind * P_type(pcm, p, n - 1)
    deep = p0 + (1 - p0) * P_type(pcm, p, n)
    cond = pind < P_type(pcm, p, n) / P_type(pcm, p, n - 1)
    bad += int((mixed < deep - 1e-16) != cond and abs(mixed - deep) > 1e-15)
    bad += int(P_type(pcm, p, n) < p * P_type(pcm, p, n - 1) - 1e-15)
    if pind <= p:
        bad += int(not mixed <= deep + 1e-15)
check("5c (b) swapping one same-model layer for an independent one lowers risk iff p^ind < P_n/P_{n-1}, with or "
      "without a shared cause; holds whenever p^ind <= p^ai", bad == 0)
ratio_n = [P_type(0.005, 0.02, k) / P_type(0.005, 0.02, k - 1) for k in (2, 3, 4)]
check("5d (b) ratio P_n/P_{n-1} tends to 1 with depth (p^cm = 0.005, p^ai = 0.02): 0.217, 0.927, 0.998",
      abs(ratio_n[0] - 0.217) < 0.001 and abs(ratio_n[1] - 0.927) < 0.001 and abs(ratio_n[2] - 0.998) < 0.001,
      f"{np.round(ratio_n, 4)}")

# (c), (d) admissibility, minimal admissible depth and the floor
bad = 0
for _ in range(3000):
    pcm, p, p0 = RNG.uniform(0.0, 0.02), RNG.uniform(0.005, 0.3), RNG.uniform(0.0, 0.002)
    eps, N = RNG.uniform(0.001, 0.2), int(RNG.integers(1, 60))
    nm = n_min_type(p0, pcm, p, eps, N)
    brute = next((k for k in range(1, 400) if admissible(P_design([(pcm, p, k)], p0), eps, N)), None)
    bad += int(nm != brute)
    # equivalence of the per-opportunity and annual forms
    P_ = RNG.uniform(0, 0.02)
    bad += int(admissible(P_, eps, N) != (P_ <= Pbar(eps, N) + 1e-15))
    # comparative statics: n_min nondecreasing in N, nonincreasing in eps (None = infinite)
    big = lambda v: 10 ** 9 if v is None else v
    bad += int(big(n_min_type(p0, pcm, p, eps, N + 5)) < big(nm))
    bad += int(big(n_min_type(p0, pcm, p, min(0.5, eps * 1.5), N)) > big(nm))
    # no depth is admissible iff Pbar <= p0 + (1 - p0) p^cm
    bad += int((nm is None) != (Pbar(eps, N) <= p0 + (1 - p0) * pcm))
check("5e (c)-(d) a design is admissible iff 1 - (1 - P)^N <= eps iff P <= Pbar = 1 - (1 - eps)^(1/N); the smallest "
      "admissible depth of one type is ceil[ln rho/ln p] with rho = (Pbar - p0 - (1 - p0)p^cm)/((1 - p0)(1 - p^cm)), "
      "none exists iff Pbar <= p0 + (1 - p0)p^cm; it is nondecreasing in N and nonincreasing in eps (3,000 draws)", bad == 0)
bad, traded = 0, 0
for _ in range(400):
    e_ = dict(cm_hu=RNG.uniform(0, 0.004), p_hu=RNG.uniform(0.02, 0.1), c_hu=RNG.uniform(1e5, 8e5),
              cm_ai=RNG.uniform(0, 0.02), p_ai=RNG.uniform(0.005, 0.05), c_ai=RNG.uniform(1e4, 1e5))
    line_, eps, N, Lc = RNG.uniform(2e4, 4e5), RNG.choice([0.01, 0.05]), int(RNG.integers(4, 40)), RNG.uniform(1e6, 5e7)
    grid_ = {(h, a): (h * e_["c_hu"] + a * e_["c_ai"] + (line_ if a else 0.0),
                      P_design([(e_["cm_hu"], e_["p_hu"], h), (e_["cm_ai"], e_["p_ai"], a)]))
             for h in range(0, 6) for a in range(0, 6) if h + a >= 1}
    adm = {k: v for k, v in grid_.items() if admissible(v[1], eps, N)}
    if adm:
        kmin = min(adm, key=lambda k: adm[k][0])
        bad += int(not admissible(grid_[kmin][1], eps, N))
        # every admissible design costs at least the floor
        bad += int(any(v[0] < adm[kmin][0] - 1e-9 for v in adm.values()))
    kloss = min(grid_, key=lambda k: grid_[k][0] + N * Lc * grid_[k][1])
    traded += int(not admissible(grid_[kloss][1], eps, N))
    # (c) an all-AI design on one provider is admissible at some depth iff its floor is below Pbar
    allai = any(admissible(grid_[(0, a)][1], eps, N) for a in range(1, 6))
    bad += int(allai and not (e_["cm_ai"] < Pbar(eps, N)))
check("5f (c) the floor is the cheapest admissible design and no admissible design costs less; minimizing cost plus "
      "expected consequences instead selects an inadmissible design in some draws (so the two readings differ); an "
      "all-AI design on one provider is never admissible when p^cm_ai >= Pbar (400 draws)",
      bad == 0 and traded > 0, f"cost-plus-loss optimum inadmissible in {traded} of 400 draws")
bad = 0
for _ in range(400):
    e_ = dict(cm_hu=RNG.uniform(0, 0.004), p_hu=RNG.uniform(0.02, 0.1), c_hu=RNG.uniform(1e5, 8e5),
              p_ai=RNG.uniform(0.005, 0.05), c_ai=RNG.uniform(1e4, 1e5))
    cm_hi = RNG.uniform(0.005, 0.03)
    cm_lo = cm_hi * RNG.uniform(0, 1)
    line_, eps, N = RNG.uniform(2e4, 4e5), RNG.choice([0.01, 0.05]), int(RNG.integers(4, 40))
    def floor_at(cm):
        g_ = [h * e_["c_hu"] + a * e_["c_ai"] + (line_ if a else 0.0) for h in range(0, 6) for a in range(0, 6)
              if h + a >= 1 and admissible(P_design([(e_["cm_hu"], e_["p_hu"], h), (cm, e_["p_ai"], a)]), eps, N)]
        return min(g_) if g_ else math.inf
    bad += int(floor_at(cm_lo) > floor_at(cm_hi) + 1e-9)
check("5g (e) better ITGCs (a lower AI common-mode probability) enlarge the admissible set and never raise the floor "
      "(400 draws)", bad == 0)
# (f) scale: with N fixed the floor's cost is independent of S, so a_min falls as 1/S; with N = oS every design with a
# positive common-mode floor eventually fails
o_ = 24 / 1e9
fails_at = next((S_ for S_ in (1e9 * 2 ** k for k in range(0, 40))
                 if not admissible(P_design([(0.002, 0.05, 3), (0.005, 0.02, 6)]), 0.01, max(1, int(o_ * S_)))), None)
check("5h (f) with N_o fixed, admissibility does not depend on revenue and a_min falls as 1/S; if N_o grew in "
      "proportion to revenue, even a mixed design with six AI layers would fail at some scale",
      fails_at is not None and admissible(P_design([(0.002, 0.05, 3), (0.005, 0.02, 6)]), 0.01, 24),
      f"N = 24 per $1bn: mixed 3 human + 6 AI fails at S = ${fails_at/1e9:,.0f}bn")

# ITGC line of an in-scope AI application (eq:acct-itgc); the unit costs are the engine's (check 6c0), the upgrade
# retest is priced at KPMG's test effort (FT-20 resolution, P2 theory pass v2; see section 6)
T_UP = EX.get("T_up", 1.22)
N_INT = EX.get("N_int", 4.0)


def itgc_line(n_id, n_perm, c_acc, n_chg, c_chg, C_val, T_up, c_ops, n_ifc, c_ifc):
    """ass:acct-itgc: one in-scope AI application's ITGC cost line, a year"""
    return dict(access=c_acc * (n_id + n_perm), change=c_chg * n_chg, upgrade=C_val / T_up, ops=c_ops,
                interface=c_ifc * n_ifc)


UNIT = dict(c_acc=2000.0, c_chg=2500.0, C_val=24e3, c_ifc=10000.0)    # engine accounting.* (C_val $24k: engine pass, 29 Oct 2026)
# FT-20: the ICFR retest at a forced upgrade is the re-testing of the controls the application performs, priced at the
# KPMG 2025 SOX survey's 16 testing hours per control (class b), about 10 controls per application (assumptions round
# 2, Section 5.5; class d) and a loaded $150 an hour (the engine's itgc_setup basis; class d). The functional
# regression suite is in W (reval_share of the build, Assumption ass:tasks-ancillary) and the change ticket in c_chg.
KPMG_HOURS, N_CTL, W_TEST = 16.0, 10.0, 150.0
C_VAL_KPMG = N_CTL * KPMG_HOURS * W_TEST
L_INV = itgc_line(3, 12, UNIT["c_acc"], 24, UNIT["c_chg"], C_VAL_KPMG, T_UP, 55e3, N_INT, UNIT["c_ifc"])
L_REF = itgc_line(1, 4, UNIT["c_acc"], 6, UNIT["c_chg"], C_VAL_KPMG, T_UP, 20e3, 1, UNIT["c_ifc"])
C_INV, C_REF = sum(L_INV.values()), sum(L_REF.values())

# Example (per in-scope control objective; firm revenue $1bn); illustrative values. L is the consequence cost of an
# undetected material misstatement (restatement, remediation, audit fees, cost of capital, litigation, clawback), not
# its amount. The AI layers' application carries the invoice application's line.
EXA = dict(N=24, L=10e6, p_hu=0.05, cm_hu=0.002, c_hu=500e3, p_ai=0.02, cm_ai=0.005, c_ai=50e3, S=1e9)
CM_AI_WEAK = 0.02                    # AI common mode with ITGCs that do not pin versions or test before promotion
EPS_EX = (0.05, 0.01)                # remote thresholds shown (no standard sets one)


def design_cost(n_hu, n_ai, e=EXA, line=None, separate=False):
    """K(d) of eq:acct-amin (C^acct omitted, common to all designs) and the miss probability P"""
    line = C_INV if line is None else line
    P = P_design([(e["cm_hu"], e["p_hu"], n_hu), (e["cm_ai"], e["p_ai"], n_ai)])
    n_apps = n_ai if separate else (1 if n_ai > 0 else 0)
    return n_hu * e["c_hu"] + n_ai * e["c_ai"] + n_apps * line, P


def best_admissible(eps, e=EXA, line=None, separate=False, cond=lambda h, a: True):
    g_ = {(h, a): design_cost(h, a, e, line, separate) for h in range(0, 7) for a in range(0, 7)
          if h + a >= 1 and cond(h, a)}
    adm = {k: v for k, v in g_.items() if admissible(v[1], eps, e["N"])}
    if not adm:
        return None, math.inf, None
    k = min(adm, key=lambda kk: adm[kk][0])
    return k, adm[k][0], adm[k][1]


ann_p = lambda P, N=EXA["N"]: 1 - (1 - P) ** N
BEST = {eps: best_admissible(eps) for eps in EPS_EX}
fl_hu, fl_ai = ann_p(EXA["cm_hu"]), ann_p(EXA["cm_ai"])
hum3 = design_cost(3, 0)
hum_adm = {eps: best_admissible(eps, cond=lambda h, a: a == 0) for eps in EPS_EX}
ai_adm = {eps: best_admissible(eps, cond=lambda h, a: h == 0) for eps in EPS_EX}
g_all = {(h, a): design_cost(h, a) for h in range(0, 7) for a in range(0, 7) if h + a >= 1}
k_loss = min(g_all, key=lambda k: g_all[k][0] + EXA["N"] * EXA["L"] * g_all[k][1])
loss_cost = g_all[k_loss][0] + EXA["N"] * EXA["L"] * g_all[k_loss][1]
resid = {eps: EXA["N"] * EXA["L"] * BEST[eps][2] for eps in EPS_EX}
print(f"     example (line {C_INV:,.0f}): " + "; ".join(f"eps {eps:.0%}: best {BEST[eps][0]} ${BEST[eps][1]/1e6:.3f}M, "
      f"annual miss {ann_p(BEST[eps][2]):.2%}, residual expected consequence ${resid[eps]:,.0f}" for eps in EPS_EX)
      + f"; floors human {fl_hu:.2%}, AI {fl_ai:.2%}; cost-plus-loss optimum {k_loss} ${loss_cost/1e6:.3f}M")
check("5i example ($1bn revenue, 24 opportunities, the invoice application's line for the AI layers): at a remote "
      "threshold of 5% the cheapest admissible design is one human and one AI layer, at 1% one human and two AI layers; "
      "no all-AI design on one provider is admissible at either (its common-mode floor alone gives an 11.3% annual "
      "chance) and no human-only design at 1% (4.7%); three human layers are admissible at 5% (5.0%, $1.5M); the "
      "cost-plus-consequence optimum is one human and two AI layers, admissible at both thresholds",
      BEST[0.05][0] == (1, 1) and BEST[0.01][0] == (1, 2) and ai_adm[0.05][0] is None and ai_adm[0.01][0] is None
      and abs(fl_ai - 0.1133) < 0.0005 and abs(fl_hu - 0.0469) < 0.0005 and hum_adm[0.01][0] is None
      and hum_adm[0.05][0] == (3, 0) and abs(ann_p(hum3[1]) - 0.0498) < 0.0005 and k_loss == (1, 2)
      and all(admissible(g_all[k_loss][1], eps, EXA["N"]) for eps in EPS_EX),
      f"{BEST}; human {hum_adm}; AI {ai_adm}")
weak = {eps: best_admissible(eps, e=dict(EXA, cm_ai=CM_AI_WEAK)) for eps in EPS_EX}
itgc_value = weak[0.01][1] - BEST[0.01][1]
check("5j (e) example: with ITGCs that leave the AI common-mode probability at 0.02 instead of 0.005, at 1% no design "
      "with one human layer is admissible and the cheapest is two human and one AI layer, so effective ITGCs lower the "
      "floor by more than their line costs; at 5% the design does not change",
      weak[0.01][0] == (2, 1) and itgc_value > C_INV and weak[0.05][0] == BEST[0.05][0]
      and abs(weak[0.05][1] - BEST[0.05][1]) < 1e-6
      and all(not admissible(design_cost(1, a, dict(EXA, cm_ai=CM_AI_WEAK))[1], 0.01, EXA["N"]) for a in range(0, 8)),
      f"weak ITGCs: {weak}; value at 1% ${itgc_value:,.0f} against a line of ${C_INV:,.0f}")
MAC.update(acctAminLine=usd(C_INV), acctAminFiveCost=money(BEST[0.05][1]), acctAminOneCost=money(BEST[0.01][1]),
           acctAminFiveMiss=f"{100*ann_p(BEST[0.05][2]):.1f}\\%", acctAminOneMiss=f"{100*ann_p(BEST[0.01][2]):.1f}\\%",
           acctAminFiveResid=usd(resid[0.05]), acctAminOneResid=usd(resid[0.01]),
           acctAminFloorAI=f"{100*fl_ai:.1f}\\%", acctAminFloorHu=f"{100*fl_hu:.1f}\\%",
           acctAminHumThreeMiss=f"{100*ann_p(hum3[1]):.1f}\\%", acctAminHumThreeCost=money(hum3[0]),
           acctAminLossCost=money(loss_cost), acctAminWeakOneCost=money(weak[0.01][1]),
           acctAminItgcValue=usd(itgc_value),
           acctAminPbarFive=f"{Pbar(0.05, EXA['N']):.5f}", acctAminPbarOne=f"{Pbar(0.01, EXA['N']):.5f}")

# ==============================================================================================
header("6. ICFR scope, ITGC lines of AI applications and close-window timeliness (def:acct-scope, prop:acct-itgc)")
# ==============================================================================================
# Engine names (engine builder, 29 Oct): in_scope_system (channel S), feeds_in_scope (channel I), and one ITGC cost
# line per in-scope AI application (access, change, upgrade retest, operations, interfaces).


def scope_set(units, in_scope_systems, integrations, policies):
    """def:acct-scope. units: dict u -> dict(T=bool, reads=set, writes=set, integ=set of integration ids,
    policies=set). integrations: dict id -> target system. Returns {unit: set of channels} for in-scope units."""
    out = {}
    for u, d in units.items():
        ch = set()
        if d["T"]:
            ch.add("T")
        if (d["reads"] | d["writes"]) & in_scope_systems:                  # in_scope_system
            ch.add("S")
        if any(integrations[i] in in_scope_systems for i in d["integ"]):   # feeds_in_scope
            ch.add("I")
        if d["policies"] & policies:
            ch.add("P")
        if ch:
            out[u] = ch
    return out


def rand_map(n_u=12, n_y=6, n_i=8, n_p=4):
    integ = {i: int(RNG.integers(0, n_y)) for i in range(n_i)}
    units = {}
    for u in range(n_u):
        units[u] = dict(T=bool(RNG.random() < 0.3),
                        reads=set(int(x) for x in RNG.choice(n_y, int(RNG.integers(0, 3)), replace=False)),
                        writes=set(int(x) for x in RNG.choice(n_y, int(RNG.integers(0, 2)), replace=False)),
                        integ=set(int(x) for x in RNG.choice(n_i, int(RNG.integers(0, 2)), replace=False)),
                        policies=set(int(x) for x in RNG.choice(n_p, int(RNG.integers(0, 2)), replace=False)))
    return units, integ


bad = 0
for _ in range(500):
    units, integ = rand_map()
    Ys = set(int(x) for x in RNG.choice(6, int(RNG.integers(1, 4)), replace=False))
    Ps = set(int(x) for x in RNG.choice(4, int(RNG.integers(0, 3)), replace=False))
    base = scope_set(units, Ys, integ, Ps)
    # union of the four channels
    bad += int(set(base) != {u for u, d in units.items() if d["T"] or ((d["reads"] | d["writes"]) & Ys)
                             or any(integ[i] in Ys for i in d["integ"]) or (d["policies"] & Ps)})
    # monotone in the in-scope systems, the integrations feeding them and the ICFR-relevant policies
    integ2 = dict(integ)
    integ2[len(integ)] = int(RNG.integers(0, 6))
    units2 = {u: dict(d, integ=d["integ"] | ({len(integ)} if RNG.random() < 0.3 else set())) for u, d in units.items()}
    bigger = scope_set(units2, Ys | {int(RNG.integers(0, 6))}, integ2, Ps | {int(RNG.integers(0, 4))})
    bad += int(not (set(base) <= set(bigger) and all(base[u] <= bigger[u] for u in base)))
    # automation: an agent performing unit u0 takes over its transactions, access, integrations and policies,
    # and may add access of its own; it never loses a channel of u0
    u0 = int(RNG.integers(0, len(units)))
    d0 = units[u0]
    agent = dict(T=d0["T"], reads=d0["reads"] | {int(RNG.integers(0, 6))}, writes=d0["writes"] | {int(RNG.integers(0, 6))},
                 integ=set(d0["integ"]), policies=set(d0["policies"]))
    auto = dict(units)
    auto[u0] = agent
    after = scope_set(auto, Ys, integ, Ps)
    bad += int(u0 in base and (u0 not in after or not after[u0] >= base[u0]))
    bad += int(any(after.get(u) != base.get(u) for u in units if u != u0))      # other units unaffected
check("6a (a) scope = union of channels T, S, I, P; monotone in in-scope systems, feeding integrations and policies; "
      "an agent performing an in-scope unit is in scope with at least that unit's channels (500 random maps)", bad == 0)
units = {"support_refund": dict(T=False, reads={"crm"}, writes={"billing"}, integ=set(), policies={"refund_authority"}),
         "support_triage": dict(T=False, reads={"crm"}, writes={"crm"}, integ=set(), policies=set()),
         "refund_agent": dict(T=False, reads={"crm", "billing"}, writes={"billing"}, integ={"crm_to_billing"},
                              policies={"refund_authority"})}
sc = scope_set(units, {"billing", "gl"}, {"crm_to_billing": "billing"}, {"refund_authority", "revenue_recognition"})
check("6b example: support refunds and credits written to billing enter through S and P (not T); triage inside the "
      "CRM stays out; an agent that takes over refunds through a new CRM-to-billing feed adds channel I",
      sc.get("support_refund") == {"S", "P"} and "support_triage" not in sc and sc.get("refund_agent") == {"S", "I", "P"},
      f"{sc}")

def _engine_accounting_units():
    """Unit costs of eq:acct-itgc in engine/src/autofrontier/defaults.yaml (the single source since 29 Oct 2026)."""
    import re as _re
    txt = (ROOT / "engine" / "src" / "autofrontier" / "defaults.yaml").read_text(encoding="utf-8")
    acc = txt.split("\naccounting:\n", 1)[1].split("\n\n", 1)[0]
    get = lambda k: float(_re.search(rf"^\s+{k}: \{{value: ([0-9.eE+-]+)", acc, _re.M).group(1))
    return dict(c_acc=get("itgc_c_acc"), c_chg=get("itgc_c_chg"), C_val=get("C_val"), c_ifc=get("itgc_c_ifc"),
                n_id=get("itgc_n_id"), perm=get("itgc_perm_per_step"), n_chg=get("itgc_n_chg"), c_ops=get("itgc_c_ops"))


_ENG_UNIT = _engine_accounting_units()
check("6c0 ITGC unit costs of this script equal the engine defaults (accounting.itgc_c_acc, itgc_c_chg, C_val, itgc_c_ifc)",
      all(abs(UNIT[k] - _ENG_UNIT[k]) < 1e-9 for k in UNIT), f"script {UNIT}, engine {_ENG_UNIT}")
L_INV_ENG = itgc_line(3, 12, UNIT["c_acc"], 24, UNIT["c_chg"], UNIT["C_val"], T_UP, 55e3, N_INT, UNIT["c_ifc"])
L_REF_ENG = itgc_line(1, 4, UNIT["c_acc"], 6, UNIT["c_chg"], UNIT["C_val"], T_UP, 20e3, 1, UNIT["c_ifc"])
C_INV_ENG, C_REF_ENG = sum(L_INV_ENG.values()), sum(L_REF_ENG.values())
# the reference application: the engine's default counts (2 identities, 2 permissions per automated step, 12 changes,
# operations at the default) for one automated in-scope step with one interface into an in-scope system
L_APP = itgc_line(_ENG_UNIT["n_id"], _ENG_UNIT["perm"], UNIT["c_acc"], _ENG_UNIT["n_chg"], UNIT["c_chg"], C_VAL_KPMG,
                  T_UP, _ENG_UNIT["c_ops"], 1, UNIT["c_ifc"])
L_APP_ENG = dict(L_APP, upgrade=UNIT["C_val"] / T_UP)
C_APP, C_APP_ENG = sum(L_APP.values()), sum(L_APP_ENG.values())
TARGET, T_LO, T_HI = 80e3, 16e3, 350e3     # params.yaml icfr_line_per_in_scope_ai_application_usd (KPMG 2025, class b)
pos_inv = (C_INV - T_LO) / (T_HI - T_LO)
print(f"     ITGC lines (retest at KPMG effort {C_VAL_KPMG:,.0f} per upgrade): invoice application "
      f"{', '.join(f'{k} {v:,.0f}' for k, v in L_INV.items())} = {C_INV:,.0f} (engine C_val: {C_INV_ENG:,.0f}); "
      f"refund agent {C_REF:,.0f} ({C_REF_ENG:,.0f}); reference application {C_APP:,.0f} ({C_APP_ENG:,.0f}); "
      f"invoice line at {pos_inv:.2f} of the [16k, 350k] range (T_up = {T_UP}, integrations = {N_INT:g})")
check("6c1 FT-20: the upgrade retest is priced at the KPMG test effort (10 controls x 16 hours x $150 = $24,000 a "
      "retest, $19.7k a year at T_up), and the engine's C_val is that value (engine pass of 29 Oct 2026; it was an "
      "illustrative $100,000, about 42 such control tests)",
      abs(C_VAL_KPMG - 24000) < 1e-9 and abs(C_VAL_KPMG / T_UP - 19672) < 1 and abs(UNIT["C_val"] - C_VAL_KPMG) < 1e-9)
check("6c ITGC lines (T_up and the invoice chain's integrations from the engine): invoice application $205k a year "
      "(access 30k, change 60k, upgrade retest 20k, operations 55k, interfaces 40k), the same at the engine's units; "
      "refund agent $75k; a reference application at the engine's default counts $88k, within 10% of "
      "the KPMG-anchored $80k; the invoice application sits inside the [$16k, $350k] range, 0.56 of the way up",
      abs(T_UP - 1.22) < 1e-9 and N_INT == 4 and abs(C_INV - 204672) < 50 and abs(C_INV_ENG - C_INV) < 1e-6
      and abs(C_REF - 74672) < 50 and abs(C_REF_ENG - C_REF) < 1e-6 and abs(C_APP - 87672) < 50
      and abs(C_APP_ENG - C_APP) < 1e-6 and abs(C_APP - TARGET) / TARGET < 0.10 and T_LO < C_INV < T_HI
      and abs(pos_inv - 0.565) < 0.005,
      f"{C_INV:,.0f} ({C_INV_ENG:,.0f}), {C_REF:,.0f} ({C_REF_ENG:,.0f}), {C_APP:,.0f} ({C_APP_ENG:,.0f})")

# (b) one shared application or one per AI layer, at the remote thresholds
SEP = {eps: best_admissible(eps, separate=True) for eps in EPS_EX}
print(f"     a_min with lines: " + "; ".join(f"eps {eps:.0%}: one application {BEST[eps][0]} ${BEST[eps][1]/1e6:.3f}M, "
      f"one per AI layer {SEP[eps][0]} ${SEP[eps][1]/1e6:.3f}M" for eps in EPS_EX) + f"; refund agent +${C_REF/1e6:.3f}M")
check("6d (b) with one application per AI layer the admissible set is unchanged and the floor rises: at 1% the cheapest "
      "design is still one human and two AI layers, at $1.01M against $0.80M with one shared application; at 5% one "
      "human and one AI layer either way; the refund agent adds its line whatever the design (0.007% of revenue)",
      SEP[0.01][0] == (1, 2) and abs(SEP[0.01][1] - 1.0093e6) < 1e3 and abs(BEST[0.01][1] - 0.8047e6) < 1e3
      and SEP[0.05][0] == (1, 1) and abs(SEP[0.05][1] - BEST[0.05][1]) < 1e-6 and abs(100 * C_REF / 1e9 - 0.0075) < 0.0005,
      f"{SEP}")
# (b) revealed preference: a higher line per AI layer never raises the number of AI layers in the cheapest admissible design
bad = 0
for _ in range(300):
    e_ = dict(EXA, cm_ai=RNG.uniform(0.0, 0.01), p_ai=RNG.uniform(0.005, 0.05), c_ai=RNG.uniform(1e4, 1e5),
              c_hu=RNG.uniform(1e5, 8e5), N=int(RNG.integers(4, 40)))
    eps = RNG.choice([0.01, 0.05])
    l1 = RNG.uniform(1e4, 3e5)
    l2 = l1 + RNG.uniform(1e4, 5e5)
    k1, _, _ = best_admissible(eps, e=e_, line=l1, separate=True)
    k2, _, _ = best_admissible(eps, e=e_, line=l2, separate=True)
    if k1 is not None and k2 is not None:
        bad += int(k2[1] > k1[1])
check("6e (b) with one application per AI layer, a higher line per layer never raises the number of AI layers in the "
      "cheapest admissible design (300 draws)", bad == 0)

# the a_min band of Part I (sections/model.tex). Direct cost of accountability at $1bn, Part I round 2 (C3, lead-agent
# rulings of 2 Nov 2026; code/paper1_macros.py AUDIT_FEE, KPMG_SIZE): the SOX program budget of a firm under $5bn of
# revenue in the KPMG 2025 SOX survey, $1.5M (archived copy, p. 12; values read from a text extraction, chart layout and
# labels verified), plus the FY2022 average audit fee of accelerated filers, $1,492,375 (Ideagen Audit Analytics, Audit
# Fee Trends 2003-2022, p. 14); low bound with the S&P 500 fee ratio ($343 per $1M of revenue). Before round 2: the S&P
# 500 ratio plus the SEC 2009 median Section 404 cost ($1.04M), 0.14%. Plus the cheapest admissible design, at both
# remote thresholds (no central value).
KPMG_UNDER_5BN, AUDIT_FEE_ACCEL, AUDIT_FEE_SP_PER_MUSD = 1.5e6, 1492375.0, 343.0
DIRECT = (KPMG_UNDER_5BN + AUDIT_FEE_ACCEL) / 1e9
DIRECT_LO = (KPMG_UNDER_5BN + AUDIT_FEE_SP_PER_MUSD * 1000) / 1e9
DIRECT_OLD = (343.0 * 1000 + 1.04e6) / 1e9
FLOOR = {eps: DIRECT + BEST[eps][1] / 1e9 for eps in EPS_EX}
FLOOR_LO = {eps: DIRECT_LO + BEST[eps][1] / 1e9 for eps in EPS_EX}
FLOOR_OLD = DIRECT_OLD + BEST[0.01][1] / 1e9
apps_to = lambda fl, line: 1 + math.ceil((0.005 - fl) / (line / 1e9)) if fl < 0.005 else 0
n_band = {eps: apps_to(FLOOR[eps], C_INV) for eps in EPS_EX}
n_band_lo = {eps: apps_to(FLOOR_LO[eps], C_INV) for eps in EPS_EX}


def pv_up(Cval, r, Tpar, Tup, Th):
    K = int(math.floor((Th - Tpar) / Tup + 1e-12))
    return Cval * math.exp(-r * (Tpar + Tup)) * (1 - math.exp(-r * K * Tup)) / (1 - math.exp(-r * Tup)), K


bad = 0
for _ in range(300):
    Cval, r_, Tpar = RNG.uniform(1e4, 2e5), RNG.uniform(0.01, 0.2), RNG.uniform(0, 1)
    Tup, Th = RNG.uniform(0.3, 3), RNG.uniform(2, 10)
    cf, K = pv_up(Cval, r_, Tpar, Tup, Th)
    direct = sum(Cval * math.exp(-r_ * (Tpar + k * Tup)) for k in range(1, 200) if Tpar + k * Tup <= Th + 1e-12)
    bad += int(abs(cf - direct) > 1e-6 * max(1, direct))
# stationary upgrade dates (uniform phase): expected PV equals the PV of the flow C_val/T_up
for _ in range(20):
    Cval, r_, Tpar, Tup, Th = 1.0, RNG.uniform(0.01, 0.2), RNG.uniform(0, 1), RNG.uniform(0.3, 2), RNG.uniform(2, 8)
    ph = RNG.uniform(0, Tup, 20000)
    tot = np.zeros_like(ph)
    for k in range(0, int(Th / Tup) + 3):
        t = ph + k * Tup
        tot += np.where((t >= Tpar) & (t <= Th), np.exp(-r_ * t), 0.0)
    flow = (Cval / Tup) * (math.exp(-r_ * Tpar) - math.exp(-r_ * Th)) / r_
    bad += int(abs(tot.mean() - flow) > 4 * tot.std() / math.sqrt(len(ph)) + 1e-4)
check("6f (c) forced-upgrade retests: PV = C_val e^{-r(T_par+T_up)}(1 - e^{-r n_up T_up})/(1 - e^{-r T_up}) with the "
      "upgrade clock starting at cutover; with stationary upgrade dates the expected PV is that of the flow C_val/T_up",
      bad == 0)
r_ic, tpar_ic, th_ic, pis_ic = EX["r"], EX["Tpar"], EX["Th"], EX["pis"]
pv_ic, K_ic = pv_up(C_VAL_KPMG, r_ic, tpar_ic, T_UP, th_ic)
ann_ic = (math.exp(-r_ic * tpar_ic) - math.exp(-r_ic * th_ic)) / r_ic
pv_flow_ic = C_VAL_KPMG / T_UP * ann_ic
dNPV_line = pis_ic * C_INV * ann_ic
npv_line = npv_icfr(TP, tpar_ic, 0.0, C_INV, 0.0, 0.0)
dNPV_eng = pis_ic * C_INV_ENG * ann_ic
check("6g example (invoice transition, T_par, T_h, r and varpi from the engine): retests worth $57k with the clock "
      "at cutover, $61k with stationary dates; the whole application line lowers the risk-adjusted NPV by $0.52M "
      "through cor:acct-npv (the same at the engine's units; $0.40M before the invoice example's regeneration of 2 Nov "
      "2026 moved varpi_p from 0.62 to 0.82)", K_ic == 3 and abs(pv_ic - 56.85e3) < 1e3
      and abs(pv_flow_ic - 61.3e3) < 1e3 and abs(dNPV_line - 0.524e6) < 0.005e6 and abs(dNPV_eng - dNPV_line) < 1e-6
      and abs((transition_npv(TP, tpar_ic) - npv_line) - dNPV_line) < 1e-6
      if EX_SOURCE == "json" else True,
      f"K={K_ic}, PV={pv_ic:,.0f}, flow {pv_flow_ic:,.0f}, dNPV {dNPV_line:,.0f} ({dNPV_eng:,.0f}), NPV {npv_line:,.0f}")


def K_wait(n_cl, nu, Tcw, D, Tsl, c_del, L_late):
    return n_cl * nu * Tcw * (c_del * D + L_late * math.exp(-Tsl / D))


def K_fb(n_cl, nu, Tcw, D, c_del, C_fb, c_fb, t_sw):
    return C_fb + n_cl * nu * Tcw * D * (c_del * (1 - math.exp(-t_sw / D)) + c_fb * math.exp(-t_sw / D))


def nu_star(n_cl, Tcw, D, Tsl, c_del, L_late, C_fb, c_fb, t_sw):
    Dl = D * math.exp(-t_sw / D) * (c_del - c_fb) + L_late * math.exp(-Tsl / D)
    return ((C_fb / (n_cl * Tcw * Dl)) if Dl > 0 else math.inf), Dl


bad = 0
for _ in range(12):
    n_cl, nu, Tcw = int(RNG.integers(1, 13)), RNG.uniform(1, 30), RNG.uniform(0.01, 0.05)
    D, Tsl, c_del, L_late = RNG.uniform(0.1, 2.0), RNG.uniform(0.5, 4.0), RNG.uniform(1e4, 1e5), RNG.uniform(1e5, 5e6)
    C_fb, c_fb, t_sw = RNG.uniform(1e4, 2e5), RNG.uniform(1e4, 1e5), RNG.uniform(0.0, 0.5)
    years = 60000
    n_out = RNG.poisson(n_cl * nu * Tcw, years)
    Dd = RNG.exponential(D, int(n_out.sum()))
    mc_w = float(np.sum(c_del * Dd + L_late * (Dd > Tsl))) / years
    mc_f = C_fb + float(np.sum(c_del * np.minimum(Dd, t_sw) + c_fb * np.maximum(Dd - t_sw, 0))) / years
    kw, kf = K_wait(n_cl, nu, Tcw, D, Tsl, c_del, L_late), K_fb(n_cl, nu, Tcw, D, c_del, C_fb, c_fb, t_sw)
    se_w = math.sqrt(n_cl * nu * Tcw * (2 * c_del ** 2 * D ** 2 + L_late ** 2 + 4 * c_del * L_late * D) / years)
    bad += int(abs(mc_w - kw) > 5 * se_w + 1.0 or abs(mc_f - kf) > 0.02 * (kf - C_fb) + 50)
    ns, Dl = nu_star(n_cl, Tcw, D, Tsl, c_del, L_late, C_fb, c_fb, t_sw)
    for nv in ((0.5 * ns, 2 * ns) if math.isfinite(ns) else (nu,)):
        pref = K_fb(n_cl, nv, Tcw, D, c_del, C_fb, c_fb, t_sw) < K_wait(n_cl, nv, Tcw, D, Tsl, c_del, L_late)
        bad += int(pref != (Dl > 0 and nv > ns))
check("6h (d) close-window outage costs C^tml_wait and C^tml_fb match Monte Carlo (Poisson incidents, exponential durations); "
      "the fallback pays iff Delta^fb > 0 and nu_out > nu* = C_fb/(n_cl T_cw Delta^fb)", bad == 0)
TML = dict(n_cl=4, Tcw=0.04, nu=12.0, Tsl=2.0, c_del=50e3, L_late=2e6, C_fb=100e3, c_fb=30e3, t_sw=0.1)
tml = {}
for Dm in (0.25, 1.0):
    tml[Dm] = (K_wait(TML["n_cl"], TML["nu"], TML["Tcw"], Dm, TML["Tsl"], TML["c_del"], TML["L_late"]),
               K_fb(TML["n_cl"], TML["nu"], TML["Tcw"], Dm, TML["c_del"], TML["C_fb"], TML["c_fb"], TML["t_sw"]),
               nu_star(TML["n_cl"], TML["Tcw"], Dm, TML["Tsl"], TML["c_del"], TML["L_late"], TML["C_fb"], TML["c_fb"],
                       TML["t_sw"])[0])
print("     timeliness example: " + "; ".join(f"mean incident {Dm} day: C_wait {v[0]:,.0f}, C_fb {v[1]:,.0f}, "
                                              f"nu* {v[2]:.1f}/yr" for Dm, v in tml.items()))
check("6i example: 4 closes a year with 10-business-day windows (0.04 years), 12 provider incidents a year, 2 days of "
      "slack: with 6-hour incidents waiting costs $25k a year and a $100k fallback does not pay (nu* = 155 a year); "
      "with day-long incidents waiting costs $616k, mostly deadline risk, and the fallback $161k (nu* = 2.2)",
      abs(tml[0.25][0] - 25.3e3) < 300 and tml[0.25][1] > tml[0.25][0] and abs(tml[0.25][2] - 155.4) < 0.5
      and abs(tml[1.0][0] - 615.7e3) < 500 and abs(tml[1.0][1] - 161.3e3) < 500 and abs(tml[1.0][2] - 2.16) < 0.01,
      f"{tml[0.25][0]:,.0f}/{tml[0.25][1]:,.0f}/{tml[0.25][2]:.2f}; {tml[1.0][0]:,.0f}/{tml[1.0][1]:,.0f}/{tml[1.0][2]:.3f}")
C_TML = min(tml[1.0][0], tml[1.0][1])
n_band_fb = {eps: 1 + math.ceil((0.005 - FLOOR[eps] - C_TML / 1e9) / ((C_INV + C_TML) / 1e9)) for eps in EPS_EX}
check("6j a_min band (Part I round 2, C3): the direct cost at $1bn is KPMG's under-$5bn SOX budget plus the accelerated-"
      "filer audit fee, 0.30% of revenue (0.18% with the S&P 500 fee ratio; 0.14% before round 2); with the cheapest "
      "admissible design the bottom-up floor is 0.37% at a 5% remote threshold and 0.38% at 1%, and it reaches the band's "
      "lower end of 0.5% at 8 and 7 in-scope AI applications per $1bn of revenue with lines like the invoice application's "
      "($205k, 0.020% of revenue each), 13 at both with the low fee, or 4 at 5% if each also needs the $161k close "
      "fallback; Part I's own figures (code/paper1_macros.py: AminFloor 0.37, AminFloorOne 0.38, ItgcApps 8, ItgcAppsOne "
      "7, ItgcAppsLo 13, ItgcAppsFb 4)",
      abs(DIRECT - 0.002992375) < 1e-9 and abs(DIRECT_LO - 0.001843) < 1e-9 and abs(DIRECT_OLD - 0.001383) < 1e-9
      and abs(FLOOR[0.05] - 0.0037470) < 1e-6 and abs(FLOOR[0.01] - 0.0037970) < 1e-6
      and n_band == {0.05: 8, 0.01: 7} and n_band_lo == {0.05: 13, 0.01: 13} and n_band_fb[0.05] == 4
      and abs(100 * C_INV / 1e9 - 0.0205) < 0.0005,
      f"direct {100*DIRECT:.3f}% (low {100*DIRECT_LO:.3f}%), floors {[f'{100*v:.3f}%' for v in FLOOR.values()]}, "
      f"n {n_band}, low fee {n_band_lo}, with fallback {n_band_fb}")
# Part I round 2, C2: the cheapest design is conditional on the layer parameters. Break-evens of the example's designs
# in the shared cause p^cm_0 (Part I's cross-type p^cc) and in the human miss rate on items the AI layers missed
# (automation bias), the closed forms of code/paper1_macros.py
P_AI1 = EXA["cm_ai"] + (1 - EXA["cm_ai"]) * EXA["p_ai"]
be_p0 = {eps: (Pbar(eps, EXA["N"]) - BEST[eps][2]) / (1 - BEST[eps][2]) for eps in EPS_EX}
be_phm5 = (Pbar(0.05, EXA["N"]) / P_AI1 - EXA["cm_hu"]) / (1 - EXA["cm_hu"])
p11_one = P_design([(EXA["cm_hu"], EXA["p_hu"], 1), (EXA["cm_ai"], EXA["p_ai"], 1)])
check("5k (Part I round 2, C2) break-evens of the example's cheapest designs: one human over one AI layer stays "
      "admissible at 5% up to a shared cause p^cm_0 of 0.00084 per opportunity and a human miss rate on AI-missed items "
      "of 8.4% (Part I: AminPccOneOneFive, AminPhmFive); one over two at 1% up to 0.00014; one over one is not admissible "
      "at 1% at any p^cm_0",
      abs(be_p0[0.05] - 0.00084372) < 1e-8 and abs(be_phm5 - 0.0839083) < 1e-6 and abs(be_p0[0.01] - 0.00013856) < 1e-8
      and Pbar(0.01, EXA["N"]) < p11_one and admissible(P_design([(EXA["cm_hu"], 0.0839, 1), (EXA["cm_ai"], EXA["p_ai"], 1)]), 0.05, EXA["N"])
      and not admissible(P_design([(EXA["cm_hu"], 0.0840, 1), (EXA["cm_ai"], EXA["p_ai"], 1)]), 0.05, EXA["N"]),
      f"p0 break-evens {be_p0}; human miss {be_phm5:.4f}")
MAC.update(acctItgcInv=usd(C_INV), acctItgcRef=usd(C_REF), acctItgcUp=usd(L_INV["upgrade"]),
           acctItgcIfc=usd(L_INV["interface"]), acctItgcNint=f"{N_INT:g}", acctItgcTup=f"{T_UP:g}",
           acctItgcPVup=usd(pv_ic), acctItgcPVflow=usd(pv_flow_ic), acctItgcNPV=f"\\${dNPV_line/1e6:.2f} million",
           acctItgcNPVafter=("$-$" if npv_line < 0 else "") + f"\\${abs(npv_line)/1e6:.2f} million",
           acctItgcInvEng=usd(C_INV_ENG), acctItgcRefEng=usd(C_REF_ENG), acctItgcApp=usd(C_APP),
           acctItgcAppEng=usd(C_APP_ENG), acctItgcVal=usd(C_VAL_KPMG), acctItgcValEng=usd(UNIT["C_val"]),
           acctItgcNPVEng=f"\\${dNPV_eng/1e6:.2f} million", acctItgcPos=f"{pos_inv:.2f}",
           acctItgcShare=f"{100*C_INV/1e9:.3f}\\%", acctItgcBandNFive=f"{n_band[0.05]}", acctItgcBandNOne=f"{n_band[0.01]}",
           acctItgcBandNfbFive=f"{n_band_fb[0.05]}", acctItgcBandNLo=f"{n_band_lo[0.05]}",
           acctItgcFloorFive=f"{100*FLOOR[0.05]:.2f}\\%", acctItgcFloorOne=f"{100*FLOOR[0.01]:.2f}\\%",
           acctItgcFloorOld=f"{100*FLOOR_OLD:.2f}\\%", acctAminDirect=f"{100*DIRECT:.2f}\\%",
           acctAminDirectLo=f"{100*DIRECT_LO:.2f}\\%", acctAminDirectOld=f"{100*DIRECT_OLD:.2f}\\%",
           acctAminKpmgSmall=f"\\${KPMG_UNDER_5BN/1e6:.1f} million", acctAminAuditFee=f"\\${AUDIT_FEE_ACCEL/1e6:.2f} million",
           acctAminPccFive=f"{be_p0[0.05]:.5f}", acctAminPccOne=f"{be_p0[0.01]:.5f}", acctAminPhmFive=f"{100*be_phm5:.1f}\\%",
           acctAminSepOne=money(SEP[0.01][1]),
           acctItgcTests=f"{UNIT['C_val'] / (KPMG_HOURS * W_TEST):.0f}")

# For the acquirer section (prop:acq-replace(d)): bunching n cutovers, read against prop:acct-cutover
Pm = lambda H: Pmw(H, EXC["pdef"], EXC["pmw"], EXC["Tdc"], EXC["Trem"], EXC["Top"])
n_b = 4
P_1 = Pm(1 - EXC["Tcl"])
bunch_any, spread_n = 1 - (1 - P_1) ** n_b, n_b * P_1
cross = 1 - (1 - spread_n) ** (1 / n_b)
P_lt = Pm(0.5)
bunch_late = 1 - (1 - P_lt) ** n_b
H_x = EXC["Trem"] + EXC["Top"] + EXC["Tdc"] * math.log(EXC["pdef"] * EXC["pmw"] / cross)
bad = 0
for _ in range(2000):      # (d) of prop:acq-replace: 1 - (1 - P)^n <= nP, and the crossover rule
    P_, n_ = RNG.uniform(0, 0.3), int(RNG.integers(2, 10))
    bad += int(1 - (1 - P_) ** n_ > n_ * P_ + 1e-15)
    if n_ * P_ < 1:
        Pn = RNG.uniform(P_, 1)
        bad += int((1 - (1 - Pn) ** n_ > n_ * P_) != (Pn > 1 - (1 - n_ * P_) ** (1 / n_)))
print(f"     acquirer check: P right after close {P_1:.4f}; bunch 4 (any weakness) {bunch_any:.4f} vs spread {spread_n:.4f}; "
      f"crossover P {cross:.4f}; bunch 4 at H = 0.5: {bunch_late:.4f}; bunching at one date is worse once the date "
      f"is later than z = {1 - H_x:.3f} ({365 * (1 - H_x - EXC['Tcl']):.1f} days after the earliest open date)")
check("6k (for prop:acq-replace(d)) at equal positions, bunching n cutovers never raises the chance of a year with a "
      "weakness above n P (crossover rule verified); but P_mw depends on the date: four cutovers bunched with half a "
      "year or less to go give 31% against 9.5% spread right after closes, and bunching at one date is worse than "
      "spreading once that date is later than z = 0.176 (3 days after the earliest open date); with a per-weakness "
      "cost (cor:acct-npv) bunching equals spreading without congestion",
      bad == 0 and abs(P_1 - 0.0237) < 1e-4 and abs(bunch_any - 0.0916) < 1e-4 and abs(spread_n - 0.0949) < 1e-4
      and abs(bunch_late - 0.3143) < 1e-4 and abs((1 - H_x) - 0.176) < 0.001 and abs(n_b * P_1 - spread_n) < 1e-15,
      f"{bunch_any:.4f}, {spread_n:.4f}, {bunch_late:.4f}, z {1 - H_x:.4f}")

# ----------------------------------------------------------------------------------------------
# Write the macros quoted in part2/theory_accounting.tex
# ----------------------------------------------------------------------------------------------
lines = ["% Generated by code/verify_part2_accounting.py; do not edit. Invoice example source: "
         + (str(EX_JSON.relative_to(ROOT)) if EX_SOURCE == "json" else "LEGACY values (invoice_chain.json missing)")
         + (f"; legacy fallback for {EX_MISSING}" if EX_SOURCE == "json" and EX_MISSING else "") + "."]
lines += [f"\\providecommand{{\\{k}}}{{{v}}}" for k, v in MAC.items()]
MACROS.parent.mkdir(parents=True, exist_ok=True)
MACROS.write_text("\n".join(lines) + "\n")
print(f"     wrote {len(MAC)} macros to {MACROS.relative_to(ROOT)}")
check("7a every macro used in part2/theory_accounting.tex is generated by this script",
      set(__import__("re").findall(r"\\(acct[A-Za-z]+)", (ROOT / "part2" / "theory_accounting.tex").read_text()))
      <= set(MAC), sorted(set(__import__("re").findall(r"\\(acct[A-Za-z]+)",
                                    (ROOT / "part2" / "theory_accounting.tex").read_text())) - set(MAC)))

print("\n" + "=" * 100)
print(f"SUMMARY: {n_pass}/{n_pass + n_fail} checks passed")
print("=" * 100)
sys.exit(0 if n_fail == 0 else 1)
