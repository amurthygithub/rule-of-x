#!/usr/bin/env python3
"""
verify_part2_playbook.py

Symbolic (sympy) and numerical checks of every closed form, threshold and generated number in
  part2/theory_playbook.tex      (Section "The Playbook: Levers by Position and Setup", label sec:playbook)
  part2/proofs_playbook.tex      (Appendix app:proofs-playbook)
  sections/levers_by_position.tex (Paper 1, Section sec:levers-position)
and of the archetype runner's outputs (code/playbook/run_archetypes.py: notes/playbook_results.json,
data/playbook/*.csv, part2/tables/playbook_macros.tex, sections/tables/levers_position_macros.tex).

Run:  python3 code/verify_part2_playbook.py        (under a minute; needs the runner's outputs)
Exit code 0 iff every check passes. Check names cite the LaTeX labels of the results.

Cross-checks against other verification scripts use their inputs, restated here, and the values those scripts assert:
  verify_part2_regimes.py B7, B10 (X^PE 2.21/2.70/3.50, X^my 6.15, X_dagger 6.85),
  verify_part2_core.py 18g (20% growth-activity saving: 2.1 points first order, 2.5 exact, Part I's worked example),
  verify_part2_competition.py F1 (dur = 2H/(1+H) under linear demand), Paper 1 cor:capital intuition (5 and 1 points,
  7.5 and 3.5 with depreciation 0.25).
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code" / "playbook"))
sys.path.insert(1, str(ROOT / "engine" / "src"))

import archetypes as AR  # noqa: E402
import levers as LV      # noqa: E402
from autofrontier import formulas as F  # noqa: E402

RNG = np.random.default_rng(20261029)
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ::  {detail}" if detail else ""))


def header(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def zero(e):
    return sp.simplify(e) == 0


def same(v1, v2) -> bool:
    if v1 is None or v2 is None:
        return v1 is None and v2 is None
    f1, f2 = float(v1), float(v2)
    if math.isnan(f1) or math.isnan(f2):
        return math.isnan(f1) and math.isnan(f2)
    return abs(f1 - f2) < 1e-12


def C_alpha(a):
    return (1 - a) * a ** (a / (1 - a))


def sig_star(ell, y, a):
    return (a * ell * y) ** (1 / (1 - a))


def R_star(m0, G, ell, X, k, a):
    y = X - k
    return m0 + y * G + C_alpha(a) * (ell * y) ** (1 / (1 - a))


# ==============================================================================================
header("1. Lemma lem:playbook-calib: a calibrated firm is at its own tangency")
# ==============================================================================================
s_, r_, a_, k_, X_, Xo_ = sp.symbols("sigma r alpha k X X_o", positive=True)
Delta_ = s_ / r_
ell_ = Delta_ / s_ ** a_
Xhat_ = k_ + r_ / a_
sig_hat = (a_ * ell_ * (Xhat_ - k_)) ** (1 / (1 - a_))
D_hat = ell_ ** (1 / (1 - a_)) * (a_ * (Xhat_ - k_)) ** (a_ / (1 - a_))
ok = True
for _ in range(200):
    sub = {s_: RNG.uniform(0.05, 0.6), r_: RNG.uniform(1.5, 8), a_: RNG.uniform(0.2, 0.5), k_: RNG.uniform(0, 1.5)}
    ok &= abs(float(sig_hat.subs(sub)) - sub[s_]) < 1e-10 and abs(float(D_hat.subs(sub)) - sub[s_] / sub[r_]) < 1e-10
check("C1 lem:playbook-calib(a): sigma*(ell, X_hat) = sigma and Delta*(ell, X_hat) = Delta (200 draws, sympy forms)", ok)
ok = True
for _ in range(200):
    s, r, a, k = RNG.uniform(0.05, 0.6), RNG.uniform(1.5, 8), RNG.uniform(0.2, 0.5), RNG.uniform(0, 1.5)
    ell = (s / r) / s ** a
    Xh = k + r / a
    Xo = k + RNG.uniform(0.2, 3.0) * (Xh - k)
    ratio = (Xo - k) / (Xh - k)
    ok &= abs(float(F.sigma_star(ell, Xo - k, a)) - s * ratio ** (1 / (1 - a))) < 1e-10
    ok &= abs(float(F.delta_star(ell, Xo - k, a)) - (s / r) * ratio ** (a / (1 - a))) < 1e-10
check("C2 lem:playbook-calib(b): sigma*(ell, X_o) = sigma ((X_o-k)/(X_hat-k))^(1/(1-alpha)), Delta* likewise with "
      "alpha/(1-alpha) (engine formulas F.sigma_star, F.delta_star; 200 draws)", ok)
# central basis since the author's decision of 2 Nov 2026 (decision 7): maintenance-netted, r = 0.99 (Paper 1's
# spend_maint_ratio); before it, all S&M with r = 3.3, now the upper bound ([7.3, 13.2])
r_c = AR.spend_ratio()
lo, hi = r_c / 0.45, r_c / 0.25
lo_a, hi_a = AR.SPEND_RATIO / 0.45, AR.SPEND_RATIO / 0.25
check("C3 lem:playbook-calib(c): X_hat - k in [r/0.45, r/0.25] = [2.2, 4.0] for the netted r = 0.99 (central), and "
      "[7.3, 13.2] for the all-S&M r = 3.3 (bound); an implication of the calibration, not an estimate of the weight",
      AR.BASIS == "netted" and abs(r_c - 0.98754) < 1e-4 and round(lo, 1) == 2.2 and round(hi, 1) == 4.0
      and abs(AR.SPEND_RATIO - 3.3) < 1e-12 and round(lo_a, 1) == 7.3 and round(hi_a, 1) == 13.2,
      f"netted {lo:.2f}, {hi:.2f}; all S&M {lo_a:.2f}, {hi_a:.2f}")

# ==============================================================================================
header("2. Proposition prop:playbook-rank (and Paper 1 prop:levers-position)")
# ==============================================================================================
m0_, G_, l_, x_, aL_ = sp.symbols("m0 G ell x a_line", positive=True)
y_ = sp.symbols("y", positive=True)
Rs = m0_ + y_ * G_ + C_alpha(a_) * (l_ * y_) ** (1 / (1 - a_))
sigs = (a_ * l_ * y_) ** (1 / (1 - a_))
# (a) growth-engine automation: ell -> ell (1-x)^(-alpha)
R_cost = Rs.subs(l_, l_ * (1 - x_) ** (-a_))
d_cost = sp.diff(R_cost, x_).subs(x_, 0)
R_pull = Rs.subs(l_, l_ * (1 + x_))
d_pull = sp.diff(R_pull, x_).subs(x_, 0)
ok = True
for _ in range(200):
    sub = {m0_: RNG.uniform(0.1, 0.5), G_: RNG.uniform(-0.1, 0.3), l_: RNG.uniform(0.02, 0.3), y_: RNG.uniform(1, 15),
           a_: RNG.uniform(0.2, 0.5)}
    sv = float(sigs.subs(sub))
    ok &= abs(float(d_cost.subs(sub)) - sv) < 1e-9 * (1 + sv) and abs(float(d_pull.subs(sub)) - sv / sub[a_]) < 1e-9 * (1 + sv)
    xx = RNG.uniform(0.01, 0.5)
    exact = float((R_cost - Rs).subs(sub).subs(x_, xx))
    Pi_v = float((C_alpha(a_) * (l_ * y_) ** (1 / (1 - a_))).subs(sub))
    ok &= abs(exact - Pi_v * ((1 - xx) ** (-sub[a_] / (1 - sub[a_])) - 1)) < 1e-10 and exact >= xx * sv - 1e-12
check("R1 prop:playbook-rank(a), prop:levers-position(a): dR/dx|0 = sigma* (automation of growth activities) and "
      "sigma*/alpha (demand pull); exact gain Pi[(1-x)^(-alpha/(1-alpha)) - 1] >= x sigma* (200 draws)", ok)
check("R2 prop:playbook-rank(a), (e): R* is linear in m0 (slope 1) and in G_i (slope X - k), so overhead, engineering, "
      "retention and the product plan (X-k)dG - D are exact",
      zero(sp.diff(Rs, m0_) - 1) and zero(sp.diff(Rs, G_) - y_) and zero(sp.diff(Rs, G_, 2)) and zero(sp.diff(Rs, m0_, 2)))
# (f) capital with depreciation: R* = m0 - delta k + (X-k)G + C(ell(X-k))^(1/(1-a))
dl_, kk_ = sp.symbols("delta k", positive=True)
Rk = m0_ - dl_ * kk_ + (X_ - kk_) * G_ + C_alpha(a_) * (l_ * (X_ - kk_)) ** (1 / (1 - a_))
Dst = l_ ** (1 / (1 - a_)) * (a_ * (X_ - kk_)) ** (a_ / (1 - a_))
ok = True
for _ in range(100):
    sub = {m0_: 0.3, G_: RNG.uniform(0, 0.3), l_: RNG.uniform(0.02, 0.3), X_: RNG.uniform(3, 15), kk_: RNG.uniform(0, 1),
           a_: RNG.uniform(0.2, 0.5), dl_: RNG.uniform(0.1, 0.4)}
    ok &= abs(float(sp.diff(Rk, kk_).subs(sub)) + float((G_ + Dst + dl_).subs(sub))) < 1e-9
check("R3 prop:playbook-rank(f), prop:levers-position(a): dR*/dk = -(g* + delta_K) with depreciation (Remark "
      "rem:assumptions(c)), so owned compute raises the score iff da/dk > g* + delta_K (100 draws)", ok)
pts = [(g + d) * 0.10 * 100 for g in (0.5, 0.1) for d in (0.0, 0.25)]
check("R4 Paper 1 cor:capital intuition: dk = 0.10 needs 5 and 1 points of opex at g = 50% and 10%, 7.5 and 3.5 at "
      "delta = 0.25 (the hurdle used for Table tab:levers-position)", [round(p, 2) for p in pts] == [5.0, 7.5, 1.0, 3.5])
# (b) switch weight
ok = True
for _ in range(500):
    a = RNG.uniform(0.2, 0.5)
    ell = RNG.uniform(0.02, 0.3)
    k = RNG.uniform(0, 1.5)
    aline = RNG.uniform(0.02, 0.4)
    xd = LV.x_dagger0(aline, ell, k, a)
    for X in (xd * 0.97, xd * 1.03):
        if X <= k:
            continue
        ge = 0.1 * sig_star(ell, X - k, a)
        ok &= (ge > 0.1 * aline) == (X > xd)
    xdp = k + (a * aline) ** (1 - a) / (a * ell)
    for X in (xdp * 0.97, xdp * 1.03):
        if X <= k:
            continue
        ok &= (0.1 * sig_star(ell, X - k, a) / a > 0.1 * aline) == (X > xdp)
    # identified form under the calibration
    s = RNG.uniform(0.05, 0.6)
    r = RNG.uniform(1.5, 8)
    ellc = (s / r) / s ** a
    Xh = k + r / a
    ok &= abs(LV.x_dagger0(aline, ellc, k, a) - (k + (Xh - k) * (aline / s) ** (1 - a))) < 1e-9
check("R5 prop:playbook-rank(b), prop:levers-position(b): growth engine beats a line of size a iff X > X_dagger_0 = "
      "k + a^(1-alpha)/(alpha ell); productivity iff X > k + (alpha a)^(1-alpha)/(alpha ell); identified form "
      "(X-k)/(X_hat-k) > (a/sigma)^(1-alpha) (500 draws)", ok)
ok = True
for _ in range(200):
    a, ell, k, aline = RNG.uniform(0.2, 0.5), RNG.uniform(0.02, 0.3), RNG.uniform(0, 1.5), RNG.uniform(0.02, 0.4)
    xd0 = LV.x_dagger0(aline, ell, k, a)
    xs = [LV.x_dagger_exact(ds * aline, ds, ell, k, a) for ds in (1e-3, 1e-5)]
    ok &= abs(xs[1] - xd0) < 1e-3 * xd0 and abs(xs[1] - xd0) < abs(xs[0] - xd0) + 1e-12
check("R6 prop:playbook-rank(b): X_dagger_0 is the limit of the exact X_dagger of eq:reg-Xdag as delta_sigma -> 0 with "
      "da = delta_sigma a (200 draws)", ok)
ok = True
for _ in range(200):
    a, lam, k = RNG.uniform(0.2, 0.5), RNG.uniform(0.02, 0.3), RNG.uniform(0, 1)
    X = k + RNG.uniform(2, 12)
    h1, h2 = RNG.uniform(0.2, 1), RNG.uniform(0.2, 1)
    s1, s2 = sig_star(lam * h1, X - k, a), sig_star(lam * h2, X - k, a)
    ok &= abs(s2 / s1 - (h2 / h1) ** (1 / (1 - a))) < 1e-9
    aline = RNG.uniform(0.2, 1.5) * s1
    hdag = h1 * (aline / s1) ** (1 - a)
    ok &= abs(sig_star(lam * hdag, X - k, a) - aline) < 1e-9
check("R7 prop:playbook-rank(c), prop:levers-position(c): sigma* proportional to h^(1/(1-alpha)); at h_dagger = "
      "h (a/sigma*)^(1-alpha) the growth engine equals the line (200 draws)", ok)
Hs, Es = sp.symbols("H E", positive=True)
dur_lin = 1 - (1 / (1 + Hs)) * (1 - Hs)
dur_E = (2 - Es) / (1 / Hs + 1 - Es)
check("R8 cor:ext-game-engine(a) (dollar share, not the score): dur = 2H/(1+H) under linear demand, -> 0 as H -> 0, "
      "negative for curvature E > 2 at H < 1 (verify_part2_competition F1); dur = 0.40 at H = 0.25, the engine's default",
      zero(dur_lin - 2 * Hs / (1 + Hs)) and sp.limit(dur_lin, Hs, 0) == 0
      and float(dur_E.subs({Hs: 0.5, Es: 2.5})) < 0 and abs(float(dur_lin.subs(Hs, 0.25)) - 0.40) < 1e-12)
# Part I round 2 (B1): the score uses the pass-through RATE phi on the unit-cost saving with the margin at the post-cut
# price, m(S) = 1 - f - (C0 - S)/(1 - phi S); dm/dS at S = 0 is 1 - phi C0 (the elasticity phi C0 of Part I lem:prices), so
# prop:playbook-rank(a) and (d) use 1 - phi C0, which does not depend on H; the engine's keep factor is that value
Ss, Cs, ps, fs = sp.symbols("S C0 phi f", positive=True)
m_post = 1 - fs - (Cs - Ss) / (1 - ps * Ss)
ok8 = zero(sp.diff(m_post, Ss).subs(Ss, 0) - (1 - ps * Cs))
check("R8b prop:playbook-rank(a), (d) after Part I round 2: a replicated cost-of-revenue cut keeps 1 - phi C0 of its margin "
      "gain to first order (symbolic derivative of the post-cut margin), independent of HHI (the archetypes' keep factors "
      "are checked in L3)", ok8)
check("R9 prop:playbook-rank(e), cor:playbook-nopay(vi); verify_part2_product G5: the product plan pays iff "
      "D_m/dG < X_o - k; D_m = 0.03, dG = 0.01, k = 0 gives +6.0 points at X = 9 and -0.5 at a screening weight of 2.5",
      abs(100 * (9 * 0.01 - 0.03) - 6.0) < 1e-9 and abs(100 * (2.5 * 0.01 - 0.03) + 0.5) < 1e-9
      and (0.03 / 0.01 < 9) and not (0.03 / 0.01 < 2.5))

# ==============================================================================================
header("3. Cross-checks with other verification scripts")
# ==============================================================================================
ALPHA, G0, M0, K0 = 0.3, 0.03, 0.35, 0.0
R_W = math.log(1.0934)
from scipy import optimize  # noqa: E402
lam8 = optimize.brentq(lambda L: (F.gordon_v0(M0, G0, K0, L, R_W, ALPHA) or 1e3) - 8.0, 0.04, 0.0699)
XDAG = LV.x_dagger_exact(0.01, 0.20, lam8, K0, ALPHA)
check("X1 verify_part2_regimes B10: exact switch weight for a 20% growth-activity saving against a 1-point cost-out is "
      "6.85 (levers.x_dagger_exact, engine F.gordon_v0)", abs(XDAG - 6.85) < 0.005, f"{XDAG:.4f}")
R_PE = math.log(1.22)
xpe = [F.exit_weight(0.25, R_PE, G0, t, 14.0 * 0.25) for t in (6, 3, 0)]
xmy = F.myopic_weight(8.0, 0.0, 0.30)
check("X2 verify_part2_regimes B7: X^PE = 2.21, 2.70, 3.50 at 6, 3, 0 years to exit; X^my = 6.15 (engine formulas used "
      "by levers.regime_weights)", [round(v, 2) for v in xpe] == [2.21, 2.70, 3.50] and abs(xmy - 6.154) < 0.001)
lam10 = optimize.brentq(lambda L: (F.gordon_v0(0.35, 0.04, 0.0, L, 0.10, ALPHA) or 1e3) - 10.0, 0.05, 0.0699)
s10 = sig_star(lam10, 10.0, ALPHA)
first, exact = 0.2 * s10, C_alpha(ALPHA) * (lam10 * 10.0) ** (1 / (1 - ALPHA)) * (0.8 ** (-ALPHA / (1 - ALPHA)) - 1)
first_lv = LV.lever_values({"k": 0.0, "ell": lam10, "alpha": ALPHA, "G_i": 0.04, "m0": 0.35, "a_GA": 0.1, "rd": 0.1},
                           10.0, 0.1, 0.4, 0.25, 0.1)["ge_cost_first"] * 2.0
check("X3 verify_part2_core 18g: a 20% cut in growth-activity cost adds 2.1 points first order and 2.5 exactly at Part "
      "I's worked example (and levers.lever_values gives the same first-order value per 10%)",
      abs(first - 0.0214) < 5e-4 and abs(exact - 0.0251) < 5e-4 and abs(first_lv - first) < 1e-12, f"{first:.4f}, {exact:.4f}")

# ==============================================================================================
header("4. Archetypes and calibrated states (Definition def:playbook-archetypes, Table tab:playbook-archetypes)")
# ==============================================================================================
RES = ROOT / "notes" / "playbook_results.json"
if not RES.exists():
    check("D0 runner outputs exist (run code/playbook/run_archetypes.py first)", False)
    sys.exit(1)
R = json.load(open(RES))
core = AR.load_core_panel()
archs, cuts = AR.build_archetypes(core)
ok = all(abs(cuts[k] - R["cuts"][k]) < 1e-12 for k in ("g25", "g50", "g75", "m25", "m50", "m75", "R75", "R95")) and \
    all(cuts[k] == R["cuts"][k] for k in ("n_population", "n_E2", "n_pass40_non_elite_balanced"))
check("D1 cut points and counts reproduce from data/panel_v2_all.csv", ok,
      f"n = {cuts['n_population']}, E2 = {cuts['n_E2']}, pass-40 balanced = {cuts['n_pass40_non_elite_balanced']}")
JA = {a["code"]: a for a in R["archetypes"]}
ok = True
for a in archs:
    j = JA[a.code]
    for f in ("g", "m", "sm", "ga", "rd", "gm", "n"):
        v1, v2 = getattr(a, f), j[f]
        ok &= same(v1, v2)
check("D2 archetype cell medians in notes/playbook_results.json reproduce from the panel", ok)
# cells are disjoint and the elite takes precedence
c = core[core.period == AR.PERIOD].copy()
c["R"] = c.g + c.m_fcf_sbc
pop = c.dropna(subset=["m_fcf_sbc"])
d = pop[pop.acq_flag == 0]
el = d.R >= cuts["R95"]
rules = [(d.g >= cuts["g75"]) & (d.m_fcf_sbc < cuts["m25"]) & ~el,
         (d.R >= cuts["R75"]) & (d.R < cuts["R95"]) & (d.g >= cuts["g50"]) & (d.m_fcf_sbc >= cuts["m50"]) & ~el,
         (d.g < cuts["g50"]) & (d.m_fcf_sbc >= cuts["m75"]) & ~el,
         (d.g >= cuts["g50"]) & (d.g < cuts["g75"]) & (d.m_fcf_sbc < cuts["m50"]) & ~el,
         (d.g < cuts["g50"]) & (d.m_fcf_sbc < cuts["m50"]) & ~el, el]
cnt = sum(r.astype(int) for r in rules)
check("D3 the six panel cells are disjoint (each firm-year in at most one cell)", int(cnt.max()) <= 1,
      f"{int((cnt == 1).sum())} of {len(d)} E2 firm-years classified")
ok = True
n_zero = 0
for key, s in R["configs"].items():
    st = s["state"]
    if st["sigma"] <= 0:          # no S&M above the maintenance base: no growth spend, no demand pull (sigma* = 0)
        n_zero += 1
        ok &= st["ell"] == 0 and float(F.sigma_star(st["ell"], st["X_hat"] - st["k"], st["alpha"])) == 0
        ok &= abs(st["sigma_star_engine"]) < 1e-3      # the engine's own state keeps ell at its floor of 1e-4
        continue
    ok &= abs(F.sigma_star(st["ell"], st["X_hat"] - st["k"], st["alpha"]) / st["sigma"] - 1) < 1e-8
    ok &= abs(st["sigma_star_engine"] / st["sigma"] - 1) < 1e-8
    ok &= abs(st["sigma"] - max(st["sm"] - AR.MAINT_BASE, 0.0)) < 1e-9      # netted basis (decision 7)
check("D4 lem:playbook-calib(a) in the engine runs: the engine's own sigma* at (ell, X_hat) equals the growth spend on "
      "the maintenance-netted basis, S&M less the 25.1% base, for every archetype and readiness case (relative 1e-8); "
      "where S&M is at or below the base the growth spend and sigma* are zero", ok, f"{n_zero} configurations without growth spend")
ok = True
for a in archs:
    if a.code == "A7":
        continue
    s = R["configs"][f"{a.code}_low"]["state"]
    st = a.state(alpha=s["alpha"])
    ok &= all(abs(st[k] - s[k]) < 1e-6 for k in ("k", "G_i", "ell", "X_hat", "sigma", "a_SM"))
check("D5 engine part1 state equals the calibration of Assumption ass:playbook-calib at the engine's alpha", ok)

# ==============================================================================================
header("5. Lever map at the archetypes (Table tab:playbook, tab:playbook-grid; Paper 1 Table tab:levers-position)")
# ==============================================================================================
ok, det = True, []
for key, s in R["configs"].items():
    st = s["state"]
    for nm, L in s["levers"].items():
        X = L["X"]
        ok &= abs(L["ge_cost_first"] - 0.1 * F.sigma_star(st["ell"], X - st["k"], st["alpha"])) < 1e-12
        ok &= abs(L["oh"] - 0.1 * st["a_GA"]) < 1e-12 and abs(L["eng"] - 0.1 * st["rd"]) < 1e-12
        ok &= abs(L["cor"] - 0.1 * s["keep"] * st["c_h"]) < 1e-12
        ok &= abs(s["keep"] - (1 - s["pass_through"]["phi"] * s["pass_through"]["C0"])) < 1e-12   # 1 - phi C0 (R8b)
        ok &= abs(L["ret_point"] - 0.01 * (X - st["k"])) < 1e-12 and abs(L["dilution_breakeven"] - (X - st["k"])) < 1e-12
        ok &= abs(L["cap_hurdle_score"] - (st["G_i"] + L["Delta_star"] + 0.25)) < 1e-12
        vals = L["ranking_values"]
        ok &= L["ranking"] == sorted(vals, key=lambda kk: -vals[kk])
        # switch consistency: growth engine above overhead iff X > X_dagger_0
        ok &= (L["ge_cost_first"] > L["oh"]) == (X > L["X_dagger0_oh"])
        ok &= (L["ge_cost_first"] > L["eng"]) == (X > L["X_dagger0_eng"])
check("L1 every lever value in the runner's lever map equals Proposition prop:playbook-rank(a) at the owner's weight, "
      "and every ranking switch is a crossing of X_dagger_0 (part (b)), for all owners and archetypes", ok)
ok = True
for key, s in R["configs"].items():
    if not key.endswith("_low"):
        continue
    W, st = s["weights"], s["state"]
    ok &= abs(W["public"] - st["X_hat"]) < 1e-12
    Xgc = st["k"] + 1.3 * (st["X_hat"] - st["k"])
    ok &= abs(W["hybrid"] - F.myopic_weight(Xgc, st["k"], 0.15)) < 1e-9
    if W.get("permanent_capital") is not None:
        ok &= abs(W["permanent_capital"] - W["m_hat"] / (W["pc_hurdle"] - st["G_i"])) < 1e-9 and W["pc_hurdle"] > st["G_i"]
    else:
        ok &= W["pc_hurdle"] <= st["G_i"]
check("L2 owner weights: public = revealed X_hat (eq:reg-Xmy read backwards), dual class X^my(0.15) of the going-concern "
      "weight k + 1.3(X_hat - k), permanent acquirer X^G = m_hat/(i_U - G_i) where defined (prop:acq-pc(d))", ok)
ok, det = True, []
for key, s in R["configs"].items():
    em = s.get("engine_lever_map") or {}
    st = s["state"]
    for nm, er in (em.get("regimes") or {}).items():
        if not er.get("applicable"):
            continue
        L = LV.lever_values(st, float(er["X_o"]), st["c_h"], s["keep"], 0.25, 0.1)
        ev = er["levers"]
        pairs = [("ge_cost_first", "growth_automation"), ("ge_cost_exact", "growth_automation_exact"),
                 ("ge_pull_first", "demand_pull"), ("oh", "overhead"), ("eng", "engineering"),
                 ("cor", "cost_of_revenue_replicable"), ("ret_point", "retention_point"),
                 ("cap_hurdle_score", "capital_hurdle_score"), ("dilution_breakeven", "ai_product_breakeven")]
        for mine, theirs in pairs:
            if theirs in ev and abs(L[mine] - ev[theirs]) > 1e-5 * (1 + abs(ev[theirs])):
                ok = False
                det.append(f"{key} {nm} {mine} {L[mine]:.5f} vs {ev[theirs]:.5f}")
        x0 = er.get("X_dagger_0_overhead")
        if x0 is not None and abs(L["X_dagger0_oh"] - x0) > 1e-5 * (1 + x0):
            ok = False
            det.append(f"{key} {nm} X_dagger_0 {L['X_dagger0_oh']:.4f} vs {x0:.4f}")
n_eng = sum(len((s.get("engine_lever_map") or {}).get("regimes") or {}) for s in R["configs"].values())
check("L4 the engine's own lever map (api.lever_map, item W13) gives the runner's lever values and switch weights at "
      "the engine's regime weights (growth automation first order and exact, demand pull, overhead, engineering, cost "
      "of revenue, retention, capital hurdle, product break-even, X_dagger_0)", ok and n_eng > 0,
      f"{n_eng} engine regime maps; " + "; ".join(det[:4]))
# S&M basis re-check (Paper 1 round 2, author decision 4: maintenance-netted central, all S&M and no S&M bounds), recomputed
# here from the cell medians and notes/empirics_v3.json, independently of code/playbook/archetypes.sm_basis_check
_E3 = json.load(open(ROOT / "notes" / "empirics_v3.json"))["estimates"]
_bM = float(_E3["spend_maint_base"]["E1"]["est"])
_arch = {a["code"]: a for a in R["archetypes"] if a["code"] != "A7"}
_mine = {"all": sum(a["sm"] > a["ga"] for a in _arch.values()),
         "netted": sum(max(a["sm"] - _bM, 0.0) > a["ga"] for a in _arch.values()), "none": 0}
SB = R.get("sm_basis_check") or {}
check("L5 S&M basis (Paper 1 decisions 4 and 7): at the weight each position's spending reveals the growth engine outranks "
      "G&A iff sigma > a_GA; on the central maintenance-netted basis (sigma = max(S&M - b_M, 0), b_M = Paper 1's "
      "MaintBase) only where S&M exceeds b_M + a_GA, on the all-S&M bound at every position, and nowhere with no S&M; the "
      "runner's block agrees",
      bool(SB) and SB.get("n_ahead") == _mine and abs(SB["b_M"] - _bM) < 1e-12 and _mine["all"] == len(_arch),
      f"b_M {_bM:.4f}; ahead of G&A: all {_mine['all']}, netted {_mine['netted']}, none {_mine['none']} of {len(_arch)}")
P1 = R.get("paper1_positions") or []
ok = len(P1) == 6
for p in P1:
    sig = max(p["sm"] - _bM, 0.0)
    ok &= abs(p["sigma"] - sig) < 1e-12 and abs(p["ge"] - 0.1 * sig) < 1e-12 and abs(p["oh"] - 0.1 * p["ga"]) < 1e-12
    ok &= (p["lead"] == "growth engine") == (sig > p["ga"]) and (p["lead_all_sm"] == "growth engine") == (p["sm"] > p["ga"])
    ok &= p["lead_no_sm"] == "G&A cut" and abs(p["cap_hurdle"] - (p["g"] + 0.25)) < 1e-12
    if sig > 0:
        ok &= abs(p["X_dagger0"] - (p["k"] + (p["X_hat"] - p["k"]) * p["ratio"])) < 1e-9 and abs(p["X_hat"] - p["k"] - AR.spend_ratio() / 0.3) < 1e-9
    else:
        ok &= math.isinf(p["X_dagger0"]) and math.isinf(p["ratio"])
LPM = dict(re.findall(r"\\newcommand\{\\(lp[A-Za-z]+)\}\{([^}]*)\}", open(ROOT / "sections" / "tables" / "levers_position_macros.tex").read()))
ok &= (LPM.get("lpNGEFirstNet"), LPM.get("lpNGEFirstAllSM"), LPM.get("lpNGEFirstNoSM")) == (str(_mine["netted"]), str(_mine["all"]), "0")
check("L3 Paper 1 Table tab:levers-position (decision 7): on the central maintenance-netted basis the growth-engine lever "
      "is 10% of the S&M above the base and leads the G&A cut at the position's own weight iff that exceeds G&A; the "
      "table's all-S&M and no-S&M columns and the macros lpNGEFirstNet/AllSM/NoSM agree with the cell medians", ok,
      "; ".join(f"{p['code']} {p['lead']} (all S&M: {p['lead_all_sm']})" for p in P1))

# decision 7: four-lever ranking at the revealed weight by basis, recomputed from the cell medians (first order: at the
# revealed weight the owner's spend is the firm's, so the growth engine is worth x*sigma, overhead x*a_GA, engineering
# x*a_RD); the cost-of-revenue value is the runner's (keep factor by basis), checked only not to change the leader
RB = R.get("ranking_by_basis") or {}
ok, det = bool(RB), []
cnt = {b: {"ge": 0, "eng": 0, "ga": 0, "ahead": 0} for b in ("netted", "all", "none")}
for c, a in _arch.items():
    for b in ("netted", "all", "none"):
        sig = {"netted": max(a["sm"] - _bM, 0.0), "all": a["sm"], "none": 0.0}[b]
        v = {"growth engine": 0.1 * sig, "overhead (G&A)": 0.1 * a["ga"], "engineering (R&D)": 0.1 * a["rd"]}
        rv = RB["positions"][c][b]["values"]
        ok &= all(abs(rv[k] - v[k]) < 1e-12 for k in v)
        v["cost of revenue"] = rv["cost of revenue"]
        top = max(v, key=v.get)
        ok &= RB["positions"][c][b]["ranking"][0] == top
        cnt[b]["ge"] += top == "growth engine"
        cnt[b]["eng"] += top == "engineering (R&D)"
        cnt[b]["ga"] += top == "overhead (G&A)"
        cnt[b]["ahead"] += v["growth engine"] > v["overhead (G&A)"]
        if b == "netted":
            det.append(f"{c} {top}")
for b in ("netted", "all", "none"):
    ok &= (RB.get(f"n_ge_first_{b}"), RB.get(f"n_eng_first_{b}"), RB.get(f"n_ga_first_{b}"), RB.get(f"n_ge_ahead_of_ga_{b}")) == \
          (cnt[b]["ge"], cnt[b]["eng"], cnt[b]["ga"], cnt[b]["ahead"])
ok &= RB.get("n_sm_maint_above_ga") == sum(min(a["sm"], _bM) > a["ga"] for a in _arch.values())
check("L6 four-lever ranking at the revealed weight by basis (decision 7) recomputed from the cell medians: growth engine "
      "first on netted / all S&M / none at %d / %d / %d positions, engineering at %d / %d / %d" %
      (cnt["netted"]["ge"], cnt["all"]["ge"], cnt["none"]["ge"], cnt["netted"]["eng"], cnt["all"]["eng"], cnt["none"]["eng"]),
      ok, "; ".join(det))

# ==============================================================================================
header("6. Playbook records (data/playbook) and the confidence tier (Definition def:playbook-tier)")
# ==============================================================================================
S = pd.read_csv(ROOT / "data" / "playbook" / "playbook_steps.csv", low_memory=False)
U = pd.read_csv(ROOT / "data" / "playbook" / "playbook_activities.csv", low_memory=False)
A = pd.read_csv(ROOT / "data" / "playbook" / "playbook_dwa.csv", low_memory=False)
DD = pd.read_csv(ROOT / "data" / "playbook" / "data_dictionary.csv")
cols = set(S.columns) | set(U.columns) | set(A.columns)
check("P1 the data dictionary has one row per column of the three playbook files", set(DD.column) - {"(all)"} == cols,
      f"{len(cols)} columns")
undocumented = [c for c in DD[DD.description.isna() | (DD.description.astype(str).str.strip().isin(["", "engine:"]))].column]
check("P2 every dictionary row has a description", not undocumented, ", ".join(undocumented[:8]))
pa = pd.read_csv(ROOT / "data" / "tasks" / "process_activities.csv")
ncfg = S.groupby(["archetype", "readiness_case"]).ngroups
check("P3 coverage: every step of the 136-step process map appears once per configuration",
      len(S) == len(pa) * ncfg and S.groupby(["archetype", "readiness_case", "process_id", "step"]).size().max() == 1,
      f"{len(pa)} steps x {ncfg} configurations")
ok_cat = S[S.tier_now.isin(["A", "B", "C"])]
feas = ok_cat.binding_now.str.startswith(("feasibility", "permissibility"))
reason_flip = ok_cat.tier_now_reason.astype(str).str.contains("flips|Monte Carlo")
check("P4 tier rule: Tier A only where a backtest-supported feasibility filter binds (capability, physical, "
      "permissibility); every Tier C names a class-d flip or the Monte Carlo share; Tier B otherwise",
      bool(feas[ok_cat.tier_now == "A"].all()) and bool(reason_flip[ok_cat.tier_now == "C"].all())
      and bool((~feas[ok_cat.tier_now == "B"]).all()),
      ", ".join(f"{t} {int((ok_cat.tier_now == t).sum())}" for t in "ABC"))
mc = pd.to_numeric(ok_cat.get("eng_robustness_share_positive"), errors="coerce")
check("P5 Definition def:playbook-tier, Monte Carlo clause: no Tier A or B step has an engine robustness share below 0.8",
      bool(((mc < 0.8) & ok_cat.tier_now.isin(["A", "B"])).sum() == 0))
agr = [s.get("agreement_with_engine") or {} for s in R["configs"].values()]
ok = bool(agr) and all(a.get("mode_activity_now") == 1.0 and a.get("mode_activity_target") == 1.0
                       and (a.get("binding_now_category") or 0) >= 0.99 for a in agr)
check("P5b runner and engine (api.playbook, version 1.0) agree on every activity decision now and at target, and on "
      "at least 99% of binding categories (the runner names the build-or-buy volume gate where the engine says cost), "
      "in every configuration; tiers differ where the two test different class-d key sets", ok,
      "binding " + ", ".join(f"{a.get('binding_now_category', float('nan')):.3f}" for a in agr)
      + "; tier " + ", ".join(f"{a.get('tier_now_after_mc', float('nan')):.2f}" for a in agr))
inv = S[(S.process_id == "P02") & (S.step == 5)]
ok = len(inv) == ncfg and bool(inv.dwa_id.eq("4.A.2.a.2.d.1").all() if "4.A.2.a.2.d.1" in set(inv.dwa_id) else True)
check("P6 the invoice chain's matching step (P02 step 5) has a record in every configuration", ok)
hi = S[(S.readiness_case == "high") & (S.process_id == "P02") & (S.step == 5)]
lo = S[(S.readiness_case == "low") & (S.process_id == "P02") & (S.step == 5)]
phys_hi = hi.binding_now.str.startswith("feasibility: physical")
check("P7 the matching step: at readiness 0.4 bound by readiness, at 0.9 by the catch-rate gate as in Section sec:tasks "
      "(prop:tasks-review(d)), wherever the DWA-level physical flag (item W5) does not bind first",
      bool(lo[~lo.binding_now.str.startswith("feasibility: physical")].binding_now.eq("readiness").all())
      and bool(hi[~phys_hi].binding_now.str.startswith("reliability").all()) and bool((hi[~phys_hi].gate_min_detection > hi[~phys_hi].gate_detection_now).all()),
      "; ".join(f"{r.archetype} {'physical' if r.binding_now.startswith('feasibility: physical') else f'd* {r.gate_min_detection:.2f} vs {r.gate_detection_now:.2f}'}" for r in hi.itertuples()))

# ==============================================================================================
header("7. Generated macros match the results and every macro the text uses is defined")
# ==============================================================================================


def read_macros(p: Path) -> dict:
    out = {}
    for line in p.read_text().splitlines():
        m = re.match(r"\\newcommand\{\\([A-Za-z]+)\}\{(.*)\}$", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


M2 = read_macros(ROOT / "part2" / "tables" / "playbook_macros.tex")
M1 = read_macros(ROOT / "sections" / "tables" / "levers_position_macros.tex")
used2 = set(re.findall(r"\\((?:pb|SpendRatio)[A-Za-z]*)", (ROOT / "part2" / "theory_playbook.tex").read_text()
                       + (ROOT / "part2" / "proofs_playbook.tex").read_text()))
used1 = set(re.findall(r"\\(lp[A-Za-z]*)", (ROOT / "sections" / "levers_by_position.tex").read_text()))
check("M1 every macro used in part2/theory_playbook.tex and proofs is generated", used2 <= set(M2), ", ".join(sorted(used2 - set(M2))))
check("M2 every macro used in sections/levers_by_position.tex is generated", used1 <= set(M1), ", ".join(sorted(used1 - set(M1))))
ok = M2.get("SpendRatioPB") == "0.99" and M2.get("SpendRatioPBAll") == "3.3" and M2.get("pbCutNpop") == str(cuts["n_population"]) and M2.get("pbCutNEtwo") == str(cuts["n_E2"])
ok &= M2.get("pbCutGmed") == f"{100 * cuts['g50']:.1f}" and M2.get("pbCutRninetyfive") == f"{100 * cuts['R95']:.1f}"
cfgA5 = R["configs"]["A5_low"]
ok &= M2.get("pbAFivePubCaph") == f"{cfgA5['levers']['public']['cap_hurdle_score']:.2f}"
_fin = [p for p in P1 if math.isfinite(p["X_dagger0"])]      # decision 7: positions with growth spend above the base
ok &= M1.get("lpXdagMin") == f"{min(p['X_dagger0'] for p in _fin):.1f}" and M1.get("lpXdagMax") == f"{max(p['X_dagger0'] for p in _fin):.1f}"
ok &= M1.get("lpRatio") == "0.99" and M1.get("lpXhat") == "3"
ok &= M1.get("lpRatioMin") == f"{min(p['ratio'] for p in _fin):.2f}" and M1.get("lpRatioMax") == f"{max(p['ratio'] for p in _fin):.2f}"
ok &= M1.get("lpRatioAllSMMin") == f"{min(p['ratio_all_sm'] for p in P1):.2f}" and M1.get("lpMaintBase") == f"{100 * _bM:.1f}"
check("M3 spot checks: macros equal the values recomputed from the panel and the results file", ok)
n_ge = sum(R["configs"][f"{c}_low"]["levers"]["public"]["ranking"][0] == "growth engine" for c in ("A1", "A2", "A3", "A4", "A5", "A6"))
words = {0: "none", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
check("M4 the count of panel archetypes whose first lever is the growth engine at the public weight matches the text "
      "macro", M2.get("pbNGEFirstPub") == words[n_ge], f"{n_ge}")

W = words
ok = all(M2.get(f"pbNGEFirstRev{nm}") == W[cnt[b]["ge"]] and M2.get(f"pbNEngFirstRev{nm}") == W[cnt[b]["eng"]]
         and M2.get(f"pbNGAFirstRev{nm}") == W[cnt[b]["ga"]] for b, nm in (("netted", "Net"), ("all", "All"), ("none", "None")))
ok &= M2.get("pbNGAAheadGENet") == W[len(_arch) - cnt["netted"]["ahead"]] and M2.get("pbNGEAheadGANet") == W[cnt["netted"]["ahead"]]
ok &= M2.get("pbGEAheadNetList") == ", ".join(c for c, a in _arch.items() if max(a["sm"] - _bM, 0) > a["ga"])
ok &= M2.get("pbSMNetZeroList") == ", ".join(c for c, a in _arch.items() if a["sm"] <= _bM)
for c, nm in (("A1", "One"), ("A4", "Four")):
    ok &= M2.get(f"pbA{nm}Sigma") == f"{100 * max(_arch[c]['sm'] - _bM, 0):.0f}" and M2.get(f"pbA{nm}GA") == f"{100 * _arch[c]['ga']:.0f}"
# the text's reading: growth spend above the base exceeds overhead at A1 and falls short at A4; A3 and A5 have their
# largest gap in R&D and engineering as their first lever (they 'point to the same line')
ok &= _arch["A1"]["sm"] - _bM > _arch["A1"]["ga"] and 0 < _arch["A4"]["sm"] - _bM < _arch["A4"]["ga"]
ok &= all(R["configs"][f"{c}_low"]["levers"]["public"]["ranking"][0] == "engineering (R&D)"
          and M2.get(f"pbA{nm}Gap") == "research and development" for c, nm in (("A3", "Three"), ("A5", "Five")))
fam = [c for c in _arch if R["configs"][f"{c}_low"]["levers"]["private_family"]["ranking"][0] == "growth engine"]
ok &= M2.get("pbGEFirstFamList") == (", ".join(fam) or "none") and M2.get("pbNGEFirstFam") == W[len(fam)]
check("M5 decision-7 text macros (basis counts, lists, A1/A4 growth spend against overhead, the gap reading, the "
      "family owner's switch) match the cell medians and the results file", ok,
      f"family GE first: {fam}; A1 {100 * (_arch['A1']['sm'] - _bM):.1f} vs {100 * _arch['A1']['ga']:.1f}; "
      f"A4 {100 * (_arch['A4']['sm'] - _bM):.1f} vs {100 * _arch['A4']['ga']:.1f}")

# ==============================================================================================
n_fail = sum(1 for _, ok in RESULTS if not ok)
print(f"\n{len(RESULTS) - n_fail} of {len(RESULTS)} checks passed")
sys.exit(1 if n_fail else 0)
