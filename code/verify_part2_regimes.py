#!/usr/bin/env python3
"""
verify_part2_regimes.py

Symbolic (sympy) and numerical (numpy/scipy) checks of every closed form, threshold and worked example in
  part2/theory_regimes.tex   (Section "Ownership, Returns and the Pace of Transformation", label sec:regimes)
  part2/proofs_regimes.tex   (Appendix "Proofs for Section sec:regimes", label app:proofs-regimes)
Paper 2, "The Economics of AI Transformation" (formerly Part II of "The Efficient Frontier of Growth and Profitability").

Run:  python3 code/verify_part2_regimes.py      (well under a minute)
Exit code 0 iff every check passes. Check names cite the LaTeX labels of the results.
Numbers printed with "->" are the ones quoted in theory_regimes.tex; the script asserts them.

Notation (see notes/theory_regimes_notes.md):
  regime o in {pub, fam, pe, vc};  r_o rate; T_o horizon; M_exit exit multiple of EBITDA; h_x share of seasoned
  run-rate capitalized; T_sea seasoning; frakA market margin multiple (Part I Lemma valuation2); frak w myopia
  weight; frak g guided slack; lev covenant; frak B budget; Dhat, shat effective dual-running cost and savings;
  frak K capitalization of a run-rate dollar; frak p control premium; frak L leverage term; frak D valuation wedge.
  Core symbols: varpi (success probability), bbar (realized share), xi (review share), pi (inference price).
"""
import itertools
import math
import sys

import numpy as np
import sympy as sp
from scipy import integrate, optimize

RNG = np.random.default_rng(20261029)
# XBOUNDS: placeholder values of an owner's decision weight on growth X. The author withdrew the 7-to-13 estimate
# (revision plan, decision D-1); the level-dependent examples are evaluated at these placeholders until the
# replacement bounds are in. Edit the tuple, rerun, and check the "% XBOUNDS" sentences of theory_regimes.tex.
XBOUNDS = (2.5, 5.0, 9.0)
MACR = {}     # macros written to part2/tables/regimes_macros.tex (read by theory_regimes.tex)
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ::  {detail}" if detail else ""))


def header(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol * (1 + abs(b))


def zero(e):
    return sp.simplify(e) == 0


def rnd(x, d):
    return round(x + 0.0, d)


# ==============================================================================================
# Presets (data/tasks/params.yaml, block ownership_regimes; illustrative where marked)
# ==============================================================================================
# Annual presets (params.yaml) and their continuously compounded equivalents r = ln(1 + r_annual), used in every
# example (the model discounts continuously, as Part I does).
R_W_ANN, R_FAM_ANN, R_PE_ANN, R_VC_ANN, RDEBT_ANN = 0.0934, 0.0834, 0.22, 0.31, 0.08
R_W = math.log(1 + R_W_ANN)       # public WACC, software (Damodaran, data of 5 Jan 2026; practitioner data set)
R_FAM = math.log(1 + R_FAM_ANN)   # family: WACC - 1 pt annual (assumed)
R_PE = math.log(1 + R_PE_ANN)     # PE average target gross IRR (Gompers, Kaplan and Mukharlyamov 2016; survey)
R_VC = math.log(1 + R_VC_ANN)     # VC average required IRR (Gompers, Gornall, Kaplan and Strebulaev 2020; survey)
T_HOLD = 6.0      # median buyout hold (sourced)
T_VC = 7.0        # VC horizon (assumed)
M_EXIT = 14.0     # software EV/EBITDA (practitioner; flagged)
LEV0 = 5.2        # buyout entry debt/EBITDA (sourced)
LEVBAR = 7.0      # covenant (assumed)
MYO_PUB = 0.30  # myopia weight (assumed)
MYO_DC = 0.15   # dual class (assumed)
B_FAM = 0.10      # family employment preference, share of loaded wage (assumed)
R_PREF, CARRY, FEE = 0.08, 0.20, 0.02  # preferred return (secondary), carry, fee (sourced)
PREMIUM_REQ = 0.30  # control premium (sourced range 15-50%, central assumed)
LAT = dict(pub=1.0, fam=0.7, pe=0.5)  # decision-latency multipliers (assumed)


def crf(r, T):
    return r / (1 - math.exp(-r * T)) if r > 0 else 1.0 / T


def annuity(r, T):
    return (1 - math.exp(-r * T)) / r if r > 0 else T


# ---------------- capitalization of a run-rate dollar (Prop reg-value (b)) ----------------
def K_gc(r, t, life=math.inf):
    """going concern: PV at 0 of 1 a year from t to t+life (permanent if life = inf)"""
    if life == math.inf:
        return math.exp(-r * t) / r
    return (math.exp(-r * t) - math.exp(-r * (t + life))) / r


def K_x(r, t, T, Mt, Tsea=0.0):
    """exit rule: interim flow from t to T plus Mt at T if seasoned (t + Tsea <= T)"""
    interim = max(math.exp(-r * t) - math.exp(-r * T), 0.0) / r
    return interim + (math.exp(-r * T) * Mt if t + Tsea <= T else 0.0)


def frakA(r, g, T, Ginf, theta):
    """Part I Lemma valuation2: dV/dm divided by S_0 = A_T(eta) + theta eta^T Gamma"""
    eta = (1 + g) / (1 + r)
    return sum(eta ** t for t in range(1, T + 1)) + theta * eta ** T * (1 + Ginf) / (r - Ginf)


# ---------------- core transition NPV (theory_core eq:tasks-npv), regime-evaluated ----------------
# Case R: the regime examples' own transition (illustrative; NOT the core's invoice chain, which is read from
# data/examples/invoice_chain.json in section H when that file exists). Inputs in dollars:
#   legacy cost C0 = 1,000k/yr, in-house labour-equivalent spend E_p = 1,200k/yr, full-realization saving W = 400k/yr
#   for T_h = 10 years; F = 1,000k, I = 0, C^J = 50k; parallel run T_par = 0.17 yr (params: ai_agent_shadow_mode,
#   grounding b) with omega_par = 0.8 and nu_rec = 0.1 (params, grounding d), so C^par = 920k/yr; C^str = 150k,
#   C^wo = 50k, L_roll = 500k, varpi = 0.8, T_det = 0.25 yr (assumed); bbar = 0.67, the engine's success.b_bar since the
#   params commit of 29 Oct 2026 (McKinsey 2021; 0.85 before); T_A = 4 (params, grounding b).
C0_R, EP_R = 1000e3, 1200e3
TP = dict(W=400e3, F=1000e3, I=0.0, CJ=50e3, Cpar=0.8 * C0_R + 0.1 * EP_R, Cstr=150e3, Cwo=50e3,
          pis=0.80, bbar=0.67, Tdet=0.25, Lroll=500e3)
TPAR_STAR = 0.17     # parallel run of Case R (params preset), not an optimized length
TA_R, TH_R = 4.0, 10.0


def core_npv(P, r, Th, Tpar):
    A = annuity(r, Tpar)
    rampPV = integrate.quad(lambda tt: math.exp(-r * tt) * (tt / Tpar), 0, Tpar)[0]
    tail = (math.exp(-r * Tpar) - math.exp(-r * Th)) / r if math.isfinite(Th) else math.exp(-r * Tpar) / r
    pu = math.exp(-Tpar / P["Tdet"])
    om = P["pis"]
    return (-(P["F"] + P["I"] + P["CJ"]) - P["Cpar"] * A + om * P["bbar"] * P["W"] * (rampPV + tail)
            - math.exp(-r * Tpar) * ((om + (1 - om) * pu) * P["Cstr"] + (1 - om) * pu * P["Lroll"]))


def regime_value(P, r, T, Th, Tpar, TV_per_run=0.0, dK=0.0):
    """V_o = NPV(r, min(Th, T)) + e^{-rT} varpi bbar * TV_per_run * W^E ; W^E = W + dK I"""
    WE = P["W"] + dK * P["I"]
    return core_npv(P, r, min(Th, T), Tpar) + math.exp(-r * T) * P["pis"] * P["bbar"] * TV_per_run * WE


def branch_value(P, r, T, Th, Tpar, Mt, dK=0.0, n=4000):
    """direct evaluation over the outcome tree (success / detected failure / undetected failure)"""
    WE = P["W"] + dK * P["I"]
    pu = math.exp(-Tpar / P["Tdet"])
    om = P["pis"]
    H = min(Th, T)
    base = -(P["F"] + P["I"] + P["CJ"]) - P["Cpar"] * annuity(r, Tpar)
    sav = integrate.quad(lambda t: math.exp(-r * t) * (min(t / Tpar, 1.0)), 0, H, points=[Tpar], limit=200)[0]
    succ = base + P["bbar"] * P["W"] * sav - math.exp(-r * Tpar) * P["Cstr"] + math.exp(-r * T) * P["bbar"] * Mt * WE
    fail_det = base
    fail_und = base - math.exp(-r * Tpar) * (P["Cstr"] + P["Lroll"])
    return om * succ + (1 - om) * ((1 - pu) * fail_det + pu * fail_und)


# ==============================================================================================
header("A. Regime value of a transition (Proposition prop:reg-value)")
# ==============================================================================================
# A1 symbolic: exit-rule capitalization and its patience ratio
r_, t_, T_, M_ = sp.symbols("r t T M", positive=True)
Kx = (sp.exp(-r_ * t_) - sp.exp(-r_ * T_)) / r_ + sp.exp(-r_ * T_) * M_
c_ = sp.exp(-r_ * T_) * (1 - r_ * M_)
check("A1 prop:reg-value(b): frak K^x(t) = [e^{-rt} - c]/r with c = e^{-rT}(1 - r M~) (symbolic)",
      zero(Kx - (sp.exp(-r_ * t_) - c_) / r_))
ratio_minus = sp.simplify((sp.exp(-r_ * t_) - c_) / (1 - c_) - sp.exp(-r_ * t_))
check("A2 prop:reg-value(b): K^x(t)/K^x(0) - e^{-rt} = -c(1 - e^{-rt})/(1 - c) (symbolic), so positive iff r M~ > 1",
      zero(ratio_minus + c_ * (1 - sp.exp(-r_ * t_)) / (1 - c_)))
ok = True
for _ in range(2000):
    r, T, Mt = RNG.uniform(0.02, 0.4), RNG.uniform(1, 10), RNG.uniform(0.5, 25)
    t = RNG.uniform(0.01, T)
    lhs = K_x(r, t, T, Mt) / K_x(r, 0, T, Mt) > math.exp(-r * t)
    ok &= (lhs == (r * Mt > 1)) or abs(r * Mt - 1) < 1e-6
check("A3 prop:reg-value(b): exit owner more patient than a going concern at the same rate iff M~ > 1/r (2,000 draws)", ok)

# A4 regime value (a) = core NPV at (r_o, min(T_h,T_o)) + e^{-rT} varpi bbar h_x M W^E: closed form vs outcome tree
ok = True
for Th in [5.0, 10.0]:
    for (r, T, Mt) in [(R_W, math.inf, 0.0), (R_PE, 6.0, 14.0), (R_PE, 4.0, 10.0), (R_FAM, 30.0, 0.0)]:
        Tterm = T if math.isfinite(T) else 1e9
        cf = regime_value(TP, r, Tterm, Th, TPAR_STAR, TV_per_run=Mt if math.isfinite(T) else 0.0)
        bt = branch_value(TP, r, Tterm, Th, TPAR_STAR, Mt if math.isfinite(T) else 0.0)
        ok &= abs(cf - bt) < 1e-6 * (1 + abs(bt))
check("A4 prop:reg-value(a): regime value = core NPV at (r_o, T_h ^ T_o) + e^{-r_o T_o} varpi bbar h_x M_exit W^E "
      "(outcome tree, 8 cases)", ok)
ok = True
for _ in range(100):
    Pr = dict(W=RNG.uniform(1e5, 1e6), F=RNG.uniform(1e5, 2e6), I=RNG.uniform(0, 5e5), CJ=RNG.uniform(0, 1e5),
              Cpar=RNG.uniform(1e5, 1e6), Cstr=RNG.uniform(0, 3e5), Cwo=0.0, pis=RNG.uniform(0.3, 0.95),
              bbar=RNG.uniform(0.5, 1), Tdet=RNG.uniform(0.1, 0.5), Lroll=RNG.uniform(0, 2e6))
    r, T, Th, Tp, Mt = RNG.uniform(0.05, 0.3), RNG.uniform(3, 8), RNG.uniform(3, 15), RNG.uniform(0.1, 1), RNG.uniform(5, 18)
    cf = regime_value(Pr, r, T, Th, Tp, TV_per_run=Mt)
    bt = branch_value(Pr, r, T, Th, Tp, Mt)
    ok &= abs(cf - bt) < 1e-6 * (1 + abs(bt))
check("A4b prop:reg-value(a): closed form equals the outcome tree on 100 random transitions", ok)

# A5 ranking flip of mutually exclusive designs: r e^{r t_q} [V_l - V_q] strictly decreasing when C_l >= C_q, t_l > t_q
ok = True
for _ in range(2000):
    Cq, Cl = RNG.uniform(0.5, 3), 0.0
    Cl = Cq + RNG.uniform(0, 5)
    tq = RNG.uniform(0, 2)
    tl = tq + RNG.uniform(0.1, 5)
    Wq, Wl = RNG.uniform(0.2, 2), RNG.uniform(0.2, 4)
    rs = np.linspace(0.01, 0.6, 200)
    f = [r * math.exp(r * tq) * ((-Cl + Wl * K_gc(r, tl)) - (-Cq + Wq * K_gc(r, tq))) for r in rs]
    ok &= bool(np.all(np.diff(f) < 0))
check("A5 prop:reg-value(c): r e^{r t_q}(V_l - V_q) strictly decreasing in r (single crossing; 2,000 draws)", ok)

# archetypes (illustrative, $ millions): quick cost-out Q, big-push platform P, capital-heavy compute K
ARCH = dict(Q=dict(C=2.0, W=1.0, WE=1.0, t=0.5, disp=1.2),
            P=dict(C=6.0, W=2.0, WE=2.0, t=4.0, disp=2.4),
            K=dict(C=4.0, W=0.3, WE=1.3, t=0.5, disp=0.0))
FA_VC = frakA(0.10, 0.25, 10, 0.03, 0.5)


def arch_values(a):
    pub = -a["C"] + a["W"] * K_gc(R_W, a["t"])
    fam = -a["C"] + (a["W"] - B_FAM * a["disp"]) * K_gc(R_FAM, a["t"])
    pe = (-a["C"] + a["W"] * (math.exp(-R_PE * a["t"]) - math.exp(-R_PE * T_HOLD)) / R_PE
          + math.exp(-R_PE * T_HOLD) * M_EXIT * a["WE"])
    vc = -a["C"] + a["W"] * K_x(R_VC, a["t"], T_VC, FA_VC)
    return dict(pub=pub, fam=fam, pe=pe, vc=vc)


VALS = {k: arch_values(a) for k, a in ARCH.items()}
for k, a in ARCH.items():
    VALS[k]["pe5"] = (-a["C"] + a["W"] * (math.exp(-R_PE * a["t"]) - math.exp(-R_PE * T_HOLD)) / R_PE
                      + math.exp(-R_PE * T_HOLD) * 0.5 * M_EXIT * a["WE"])
print("  -> PE with h_x = 0.5: " + ", ".join(f"{k} {VALS[k]['pe5']:.2f}" for k in ARCH))
check("A6b tab:reg-rank: with h_x = 0.5 the sponsor's values are Q 3.15, P -0.26, K -0.33 (the K flip needs h_x near 1)",
      abs(VALS["Q"]["pe5"] - 3.15) < 0.005 and abs(VALS["P"]["pe5"] + 0.26) < 0.005 and abs(VALS["K"]["pe5"] + 0.33) < 0.005)
for k in ARCH:
    print(f"  -> archetype {k}: " + ", ".join(f"{o} {VALS[k][o]:.2f}" for o in ["pub", "fam", "pe", "vc"]))
print(f"  -> market margin multiple frakA (Part I discussion parameters) = {FA_VC:.1f}")
expect = dict(Q=dict(pub=8.71, fam=8.55, pe=5.27, vc=7.93), P=dict(pub=9.67, fam=9.95, pe=3.98, vc=9.90),
              K=dict(pub=-0.79, fam=-0.40, pe=2.43, vc=-1.02))
check("A6 tab:reg-rank: archetype values as printed (Q, P, K under public, family, PE, VC)",
      all(abs(VALS[k][o] - expect[k][o]) < 0.005 for k in expect for o in expect[k]) and abs(FA_VC - 48.0) < 0.05)
rank = {o: sorted(ARCH, key=lambda k: -VALS[k][o]) for o in ["pub", "fam", "pe", "vc"]}
check("A7 tab:reg-rank: public, family and VC rank P > Q > K; PE ranks Q > P > K, with K positive only under PE",
      rank["pub"] == ["P", "Q", "K"] and rank["fam"] == ["P", "Q", "K"] and rank["vc"] == ["P", "Q", "K"]
      and rank["pe"] == ["Q", "P", "K"] and VALS["K"]["pe"] > 0 > max(VALS["K"]["pub"], VALS["K"]["fam"], VALS["K"]["vc"]),
      str(rank))
fam30 = {k: -a["C"] + (a["W"] - B_FAM * a["disp"]) * (math.exp(-R_FAM * a["t"]) - math.exp(-R_FAM * 30.0)) / R_FAM
         for k, a in ARCH.items()}
print(f"  -> family with the 30-year preset and no terminal value: Q {fam30['Q']:.2f}, P {fam30['P']:.2f}")
check("A7b tab:reg-rank note: with a 30-year family horizon Q = 7.56, P = 7.96, ranking kept",
      abs(fam30["Q"] - 7.56) < 0.005 and abs(fam30["P"] - 7.96) < 0.005 and fam30["P"] > fam30["Q"] > fam30["K"])
rdag = optimize.brentq(lambda r: (-ARCH["P"]["C"] + ARCH["P"]["W"] * K_gc(r, 4.0))
                       - (-ARCH["Q"]["C"] + ARCH["Q"]["W"] * K_gc(r, 0.5)), 0.01, 0.5)
print(f"  -> going-concern switch rate between P and Q: r_dagger = {rdag:.4f}")
check("A8 prop:reg-value(c) example: r_dagger = 9.9%, about one point above the continuous WACC of 8.93%",
      abs(rdag - 0.0988) < 0.0005 and abs(R_W - 0.0893) < 0.00005)


# A9 PE capital hurdle zeta^pe
def zeta_pe(r, T, M, dK, hx=1.0):
    A = annuity(r, T)
    return (1 + dK * A) / (A + math.exp(-r * T) * hx * M)


ok = True
for _ in range(3000):
    r, T, M, dK, hx = RNG.uniform(0.05, 0.4), RNG.uniform(1, 8), RNG.uniform(4, 20), RNG.uniform(0.05, 0.5), RNG.uniform(0, 1)
    dc, DK = RNG.uniform(0.01, 2), RNG.uniform(0.1, 5)
    val = -DK + (dc - dK * DK) * annuity(r, T) + math.exp(-r * T) * hx * M * dc
    ok &= (val > 0) == (dc / DK > zeta_pe(r, T, M, dK, hx)) or abs(dc / DK - zeta_pe(r, T, M, dK, hx)) < 1e-9
check("A9 prop:reg-value(d): PE adopts a capital-for-labor switch iff Dc/DK > zeta^pe (3,000 draws)", ok)
zp = zeta_pe(R_PE, T_HOLD, M_EXIT, 1 / 3)
v_inv, dc_e, DK_e = 120000, 0.60, 1.50
pe_sw = v_inv * (-DK_e + (dc_e - DK_e / 3) * annuity(R_PE, T_HOLD) + math.exp(-R_PE * T_HOLD) * M_EXIT * dc_e)
pub_sw = v_inv * (dc_e - (R_W + 1 / 3) * DK_e) / R_W
print(f"  -> zeta^pe = {zp:.3f} per dollar of capital vs value hurdle r_w + delta_K = {R_W + 1/3:.3f}; "
      f"owned-capacity switch: PE {pe_sw:,.0f}, public {pub_sw:,.0f}")
zp5 = zeta_pe(R_PE, T_HOLD, M_EXIT, 1 / 3, 0.5)
print(f"  -> zeta^pe at h_x = 0.5: {zp5:.3f}")
pe_sw5 = v_inv * (-DK_e + (dc_e - DK_e / 3) * annuity(R_PE, T_HOLD) + math.exp(-R_PE * T_HOLD) * 0.5 * M_EXIT * dc_e)
print(f"  -> owned-capacity switch at h_x = 0.5: PE {pe_sw5:,.0f}")
check("A10b prop:reg-value(d): at h_x = 0.5, zeta^pe = 0.385, below both 0.423 and the example's 0.40, so the switch "
      "still pays the sponsor ($15k)", abs(zp5 - 0.385) < 0.001 and zp5 < 0.40 < R_W + 1 / 3 and abs(pe_sw5 - 14.9e3) < 0.5e3,
      f"{pe_sw5:,.0f}")
check("A10 prop:reg-value(d) example: zeta^pe = 0.28 < 0.42; an owned-capacity switch with ratio 0.40 is worth "
      "+$168k to PE and -$46k at WACC (illustrative case, 120,000 units)", abs(zp - 0.280) < 0.001 and abs(pe_sw - 167.7e3) < 0.5e3 and abs(pub_sw + 45.6e3) < 0.5e3)

# A11 myopia penalty on the core transition (planned GAAP path, revenue $100M, T_par = 0.5, b = 1)
gaap_y1 = -(TP["CJ"] + TP["Cpar"] * TPAR_STAR - TP["W"] * TPAR_STAR / 2 + TP["Cstr"] + TP["Cwo"]
            - TP["W"] * (1 - TPAR_STAR) + TP["F"] / TA_R)       # Prop tasks-scorepath(c), GAAP, b = 1
pen = MYO_PUB * math.exp(-R_W) * max(-gaap_y1, 0)
print(f"  -> Case R GAAP year-1 change {gaap_y1:,.0f}; myopia penalty at frak w = 0.3: {pen:,.0f}")
check("A11 def:reg-value example: Case R's year-1 GAAP dip of $290k costs a public owner $80k at frak w = 0.3",
      abs(gaap_y1 + 290.4e3) < 1 and abs(pen - 79.68e3) < 50)

# ==============================================================================================
header("B. The regime's growth weight and Part I (Proposition prop:reg-weight)")
# ==============================================================================================
ALPHA = 0.3
CA = (1 - ALPHA) * ALPHA ** (ALPHA / (1 - ALPHA))
G_, M0, K0 = 0.03, 0.35, 0.0


def v0_of(r, lam, m0=M0, G=G_, k=K0, alpha=ALPHA):
    Ca = (1 - alpha) * alpha ** (alpha / (1 - alpha))
    F = lambda v: (r - G) * v - (m0 - k * G) - Ca * (lam * max(v - k, 0)) ** (1 / (1 - alpha))
    grid = np.linspace(1e-6, 400, 40001)
    Fv = np.array([F(x) for x in grid])
    idx = np.where(np.diff(np.sign(Fv)) != 0)[0]
    if len(idx) == 0:
        return None
    return optimize.brentq(F, grid[idx[0]], grid[idx[0] + 1])


LAM = optimize.brentq(lambda L: (v0_of(R_W, L) or 1e3) - 8.0, 0.04, 0.0699)
X_PUB = v0_of(R_W, LAM)
X_FAM = v0_of(R_FAM, LAM)
print(f"  -> example firm: m0 = 0.35, G = 0.03, k = 0, alpha = 0.3, lambda = {LAM:.4f}: v0 = {X_PUB:.2f} at WACC, "
      f"{X_FAM:.2f} at the family rate")
check("B1 prop:reg-weight(a) example: lambda = 0.0535 gives v0 = 8 at the WACC (8.93%) and 10.8 at the family rate (8.01%)",
      abs(LAM - 0.0535) < 0.00005 and abs(X_FAM - 10.79) < 0.01 and abs(R_FAM - 0.0801) < 0.00005)
ok = True
for _ in range(300):
    m0, G, lam = RNG.uniform(0.2, 0.5), RNG.uniform(0.0, 0.05), RNG.uniform(0.02, 0.06)
    r1 = RNG.uniform(G + 0.05, G + 0.15)
    r2 = r1 + RNG.uniform(0.002, 0.03)
    a, b = v0_of(r1, lam, m0, G), v0_of(r2, lam, m0, G)
    if a is None or b is None:
        continue
    ok &= b < a
check("B2 prop:reg-weight(a): the small-share weight v0(r) is strictly decreasing in r (300 draws)", ok)
LAM_P1 = optimize.brentq(lambda L: (v0_of(0.10, L, m0=0.35, G=0.04) or 1e3) - 10.0, 0.05, 0.0699)
v_a = v0_of(R_W, LAM_P1, m0=0.35, G=0.04)
r_lim = optimize.brentq(lambda r: 1.0 if v0_of(r, LAM_P1, m0=0.35, G=0.04) is None else -1.0, R_W, 0.10, xtol=1e-6)
print(f"  -> Part I worked example (lambda = {LAM_P1:.4f}): v0 = 10 at r = 0.10, "
      f"{'no root' if v_a is None else f'{v_a:.2f}'} at the continuous WACC {R_W:.4f}; roots exist only for r > {r_lim:.4f}")
check("B2b notes item 12: with Part I's worked-example firm, eq:gordon has no root at the continuous WACC (8.93%); "
      "the small-share weight is unbounded below r of about 9.1%", abs(LAM_P1 - 0.0698) < 0.0001 and v_a is None
      and 0.0893 < r_lim < 0.0935, f"r_lim = {r_lim:.4f}")


def frontier(X, ell, m0=M0, G=G_, k=K0, alpha=ALPHA):
    y = max(X - k, 0)
    D = ell ** (1 / (1 - alpha)) * (alpha * y) ** (alpha / (1 - alpha))
    sig = alpha * y * D
    return dict(D=D, sig=sig, g=G + D, m=m0 - k * (G + D) - sig, R=m0 + y * G + (1 - alpha) * y * D,
                Pi=(1 - alpha) * y * D)


# B3 myopia: symbolic reformulation and numerical argmax
th_, X_, k_, m0_, sg_, g_ = sp.symbols("w_my X k m0 sigma g", real=True)
lhs = (m0_ - sg_ - k_ * g_) + X_ * g_ + th_ * (m0_ - sg_)
rhs = (1 + th_) * (m0_ - sg_ + (X_ - k_) / (1 + th_) * g_) - k_ * g_ + k_ * g_
check("B3 prop:reg-weight(b): m + Xg + frak w m_op = (1+frak w)[m0 - sigma + (X-k)/(1+frak w) g] (symbolic)",
      zero(sp.expand(lhs - rhs)))
ok = True
for _ in range(300):
    X, k, th, ell = RNG.uniform(1, 15), RNG.uniform(0, 0.5), RNG.uniform(0, 1), RNG.uniform(0.03, 0.5)
    if X <= k:
        continue
    obj = lambda s: -((M0 - s - k * (G_ + ell * s ** ALPHA)) + X * (G_ + ell * s ** ALPHA) + th * (M0 - s))
    sopt = optimize.minimize_scalar(obj, bounds=(0, 5), method="bounded", options=dict(xatol=1e-12)).x
    Xmy = k + (X - k) / (1 + th)
    pred = frontier(Xmy, ell, k=k)["sig"]
    ok &= abs(sopt - pred) < 1e-5 * (1 + pred)
check("B4 prop:reg-weight(b): the myopic optimum equals the Rule-of-X^my optimum, X^my = k + (X-k)/(1+frak w) "
      "(300 draws)", ok)
ok = True
for _ in range(300):
    X, th, ell = RNG.uniform(1, 15), RNG.uniform(0.01, 1.5), RNG.uniform(0.03, 0.5)
    f0, f1 = frontier(X, ell), frontier(X / (1 + th), ell)
    true_at_my = (M0 - f1["sig"]) + X * f1["g"]
    loss = f0["R"] - true_at_my
    rho = (1 + th) ** (-ALPHA / (1 - ALPHA))
    pred = f0["Pi"] * (1 - (rho - ALPHA * rho ** (1 / ALPHA)) / (1 - ALPHA))
    ok &= abs(loss - pred) < 1e-10 and abs(f1["D"] / f0["D"] - rho) < 1e-10 \
        and abs(f1["sig"] / f0["sig"] - (1 + th) ** (-1 / (1 - ALPHA))) < 1e-10
check("B5 prop:reg-weight(b): Delta* and sigma* fall by (1+frak w)^(-alpha/(1-alpha)) and ^(-1/(1-alpha)); "
      "loss Pi[1 - (rho - alpha rho^(1/alpha))/(1-alpha)] (300 draws)", ok)

# B6 hold-and-exit weight X^x(tau)
tau_, rr_, G2_, mh_, XT_ = sp.symbols("tau r G mhat X_T", positive=True)
u_ = sp.symbols("u", positive=True)
Xdirect = sp.integrate(sp.exp(-(rr_ - G2_) * u_) * mh_, (u_, 0, tau_)) + sp.exp(-(rr_ - G2_) * tau_) * XT_
wgt = sp.exp(-(rr_ - G2_) * tau_)
Xform = (1 - wgt) * mh_ / (rr_ - G2_) + wgt * XT_
okB6 = True
for _ in range(50):
    sub = {tau_: RNG.uniform(0.1, 10), rr_: RNG.uniform(0.06, 0.4), G2_: RNG.uniform(0, 0.05), mh_: RNG.uniform(0.05, 0.5),
           XT_: RNG.uniform(0.5, 10)}
    okB6 &= abs(float(Xdirect.subs(sub)) - float(Xform.subs(sub))) < 1e-10
check("B6 prop:reg-weight(c): value of a permanent marginal revenue dollar = (1-w)X^G + w X_T, w = e^{-(r-G)tau} "
      "(sympy integral, 50 evaluations)", okB6 and zero(sp.diff(Xform, tau_) - (mh_ - (rr_ - G2_) * Xform)))
MH, MHE = 0.25, 0.25


def X_exit(r, tau, XT, mh=MH, gm=G_):
    w = math.exp(-(r - gm) * tau)
    return (1 - w) * mh / (r - gm) + w * XT


XPE6, XPE3, XPE0 = (X_exit(R_PE, t, M_EXIT * MHE) for t in (6, 3, 0))
X_MY = K0 + (X_PUB - K0) / (1 + MYO_PUB)
print(f"  -> X^PE at 6, 3, 0 years to exit: {XPE6:.2f}, {XPE3:.2f}, {XPE0:.2f}; public X = {X_PUB:.2f}, "
      f"myopic public {X_MY:.2f}, family {X_FAM:.2f}")
check("B7 prop:reg-weight(c) example: X^PE = 2.21, 2.70, 3.50 at 6, 3, 0 years to exit; myopic public 6.15",
      abs(XPE6 - 2.21) < 0.005 and abs(XPE3 - 2.70) < 0.005 and abs(XPE0 - 3.50) < 1e-9 and abs(X_MY - 6.154) < 0.001)
FR = {o: frontier(X, LAM) for o, X in [("fam", X_FAM), ("pub", X_PUB), ("my", X_MY), ("pe", XPE3)]}
for o in FR:
    print(f"  -> frontier point {o}: g = {FR[o]['g']:.4f}, sigma = {FR[o]['sig']:.4f}, m = {FR[o]['m']:.4f}, "
          f"R* = {FR[o]['R']:.4f}")
check("B8 prop:reg-weight(d) example: growth 5.5, 5.2, 5.0, 4.4% and margins 26.8, 29.7, 31.3, 33.9% "
      "(family, public, myopic public, PE)",
      [rnd(100 * FR[o]["g"], 1) for o in ["fam", "pub", "my", "pe"]] == [5.5, 5.2, 5.0, 4.4]
      and [rnd(100 * FR[o]["m"], 1) for o in ["fam", "pub", "my", "pe"]] == [26.8, 29.7, 31.3, 33.9])
ok = all(FR[a]["g"] > FR[b]["g"] and FR[a]["m"] < FR[b]["m"] for a, b in [("fam", "pub"), ("pub", "my"), ("my", "pe")])
check("B9 prop:reg-weight(d): frontier points ordered by weight (faster growth, lower margin)", ok)
DS, DA = 0.20, 0.01
KS = (1 - DS) ** (-ALPHA / (1 - ALPHA)) - 1
XDAG = K0 + (DA / (CA * KS)) ** (1 - ALPHA) / LAM
gain = lambda X: frontier(X, LAM)["Pi"] * KS
print(f"  -> growth-engine vs one-point cost-out switch weight X_dagger = {XDAG:.2f}; gains at X = 8: "
      f"{100*gain(X_PUB):.2f} points, at X^PE: {100*gain(XPE3):.2f}")
check("B10 prop:reg-weight(e): growth engine (20% saving) beats a 1-point cost-out iff X > X_dagger = 6.85: public "
      "(8) above, pressured public (6.15) and sponsor below", abs(XDAG - 6.85) < 0.005 and abs(gain(XDAG) - DA) < 1e-12
      and gain(X_PUB) > DA > gain(X_MY) > gain(XPE3) and abs(100 * gain(X_PUB) - 1.25) < 0.005
      and abs(100 * gain(X_MY) - 0.86) < 0.005 and abs(100 * gain(XPE3) - 0.26) < 0.005,
      f"{100*gain(X_PUB):.3f}, {100*gain(X_MY):.3f}, {100*gain(XPE3):.3f}")
ok = True
for _ in range(500):
    X1, X2 = RNG.uniform(0.1, 20, 2)
    ok &= (gain(X1) > gain(X2)) == (X1 > X2)
check("B11 prop:reg-weight(e): the growth-engine gain is strictly increasing in X (500 draws)", ok)
# B12 XBOUNDS: the ranking of prop:reg-weight(e) at placeholder owner weights, at the example's demand pull. The
# going-concern weight of (a) is a model output (8 here); for this firm it is at least m0/(r_w - G) at any demand pull.
V0_MIN = M0 / (R_W - G_)
XB_R = {X_: dict(my=K0 + (X_ - K0) / (1 + MYO_PUB), g=gain(X_), g_my=gain(K0 + (X_ - K0) / (1 + MYO_PUB))) for X_ in XBOUNDS}
band_hi = K0 + (XDAG - K0) * (1 + MYO_PUB)
for X_, v in XB_R.items():
    rho_x = ((XPE3 - K0) / (X_ - K0)) ** (ALPHA / (1 - ALPHA))
    v["loss_pe"] = frontier(X_, LAM)["Pi"] * (1 - (rho_x - ALPHA * rho_x ** (1 / ALPHA)) / (1 - ALPHA))
print("  -> XBOUNDS ranking at lambda = %.4f (X_dagger %.2f): " % (LAM, XDAG) + "; ".join(
      f"X = {X_:g}: growth gain {100*v['g']:.2f} pts (pressured, X^my = {v['my']:.2f}: {100*v['g_my']:.2f}), "
      f"loss if the sponsor's 2.70 replaces it {100*v['loss_pe']:.2f}" for X_, v in XB_R.items())
      + f"; pressure reverses the public ranking for X in ({XDAG:.2f}, {band_hi:.2f}); min going-concern weight {V0_MIN:.2f}")
check("B12 XBOUNDS (2.5, 5, 9) at the example's demand pull: the overhead cut ranks first at 2.5 and 5 for every owner, "
      "and the growth engine at 9 for the public owner and, since 9/1.3 = 6.92 > 6.85, for the pressured one too; "
      "earnings pressure reverses the public ranking only for X in (6.85, 8.91); the sponsor's weight (2.21 to 3.50) "
      "is below the public owner's at 5 and 9 and, from three years before exit, above it at 2.5; the going-concern "
      "weight of this firm is at least m0/(r_w - G) = 5.90 at any demand pull",
      XBOUNDS == (2.5, 5.0, 9.0) and XB_R[2.5]["g"] < DA and XB_R[5.0]["g"] < DA and XB_R[9.0]["g"] > DA
      and XB_R[9.0]["g_my"] > DA and abs(XB_R[9.0]["my"] - 6.923) < 0.001 and abs(band_hi - 8.907) < 0.001
      and XPE0 < 5.0 and XPE3 > 2.5 and XPE6 < 2.5 and abs(V0_MIN - 5.90) < 0.005
      and abs(100 * XB_R[9.0]["loss_pe"] - 3.30) < 0.005 and abs(100 * XB_R[5.0]["loss_pe"] - 0.51) < 0.005
      and 100 * XB_R[2.5]["loss_pe"] < 0.01)
_tags = ("One", "Two", "Three")
for t_, X_ in zip(_tags, XBOUNDS):
    MACR[f"regXb{t_}"] = f"{X_:g}"
    MACR[f"regXbGain{t_}"] = f"{100 * XB_R[X_]['g']:.2f}"
    MACR[f"regXbGainMy{t_}"] = f"{100 * XB_R[X_]['g_my']:.2f}"
    MACR[f"regXbMy{t_}"] = f"{XB_R[X_]['my']:.2f}"
    MACR[f"regXbLossPE{t_}"] = f"{100 * XB_R[X_]['loss_pe']:.2f}"
MACR.update(regXbBandLo=f"{XDAG:.2f}", regXbBandHi=f"{band_hi:.2f}", regVzeroMin=f"{V0_MIN:.1f}")
print(f"  -> myopia loss in the true criterion at X = 8, frak w = 0.3: "
      f"{100*(FR['pub']['R'] - ((M0 - FR['my']['sig']) + X_PUB * FR['my']['g'])):.2f} points of R")

# ==============================================================================================
header("C. Pace (Proposition prop:reg-speed)")
# ==============================================================================================
ok = True
for _ in range(1000):
    r1, T = RNG.uniform(0.01, 0.5), RNG.uniform(0.5, 10)
    r2 = r1 + RNG.uniform(0.001, 0.2)
    ok &= crf(r2, T) > crf(r1, T)
check("C1 prop:reg-speed(a): the capital recovery factor a(r,T) is strictly increasing in r (1,000 draws)", ok)
a_sl, a_w, a_pe = 1 / TA_R, crf(R_W, TA_R), crf(R_PE, TA_R)
print(f"  -> with K(A) = 0 the volume threshold scales with a(r, T_A): T_A = 4 gives +{100*(a_w/a_sl-1):.1f}% at WACC "
      f"and +{100*(a_pe/a_sl-1):.1f}% at 22% over straight-line amortization")
check("C2 prop:reg-speed(a) example: with T_A = 4, v* is 18.9% higher at the WACC and 45.0% higher at the 22% hurdle "
      "than with straight-line amortization", abs(100 * (a_w / a_sl - 1) - 18.9) < 0.05 and abs(100 * (a_pe / a_sl - 1) - 45.0) < 0.05)
ok = True
for _ in range(500):
    n = RNG.integers(3, 12)
    ts = np.sort(RNG.uniform(0, 10, n))
    ks = RNG.integers(1, n)
    cf = np.concatenate([-RNG.uniform(0, 3, ks), RNG.uniform(0, 3, n - ks)])
    tstar = ts[ks - 1]
    rs = np.linspace(0.0, 1.0, 300)
    f = [np.sum(cf * np.exp(-r * (ts - tstar))) for r in rs]
    ok &= bool(np.all(np.diff(f) < 1e-15))
check("C3 prop:reg-speed(a): with one sign change at t*, e^{r t*} NPV(r) is decreasing in r (unique IRR; 500 draws)", ok)
check("C4 prop:reg-speed(a): Case R has one sign change (C^par >= varpi bbar W)",
      TP["Cpar"] >= TP["pis"] * TP["bbar"] * TP["W"])
irr10 = optimize.brentq(lambda r: core_npv(TP, r, TH_R, TPAR_STAR), 1e-4, 2.0)
irrinf = optimize.brentq(lambda r: core_npv(TP, r, math.inf, TPAR_STAR), 1e-3, 2.0)
npv_w10, npv_pe10 = core_npv(TP, R_W, TH_R, TPAR_STAR), core_npv(TP, R_PE, TH_R, TPAR_STAR)
print(f"  -> Case R (10-year life): IRR {irr10:.4f} (permanent: {irrinf:.4f}); NPV {npv_w10:,.0f} "
      f"at WACC, {npv_pe10:,.0f} at 22%")
check("C5 prop:reg-speed(a) example: Case R IRR 9.1% continuous (9.5% annual), barely above the continuous WACC of "
      "8.93%; NPV +$12k at the WACC, -$471k at the hurdle; IRR 15.3% with a permanent saving",
      abs(irr10 - 0.0912) < 0.0005 and abs(math.exp(irr10) - 1 - 0.0955) < 0.0005 and abs(npv_w10 - 11.5e3) < 0.5e3
      and abs(npv_pe10 + 470.9e3) < 0.5e3 and irr10 > R_W and abs(irrinf - 0.1528) < 0.0005)


def Thstar(r):
    f = lambda T: core_npv(TP, r, T, TPAR_STAR)
    if f(1e4) <= 0:
        return math.inf
    return optimize.brentq(f, TPAR_STAR + 1e-6, 1e4)


ths = [Thstar(r) for r in np.linspace(0.02, 0.25, 24)]
check("C6 prop:reg-speed(a): minimum horizon T_h*(r) nondecreasing in r (infinite above the permanent IRR); "
      "9.9 years at WACC, just inside the 10-year life", all(b >= a - 1e-9 for a, b in zip(ths, ths[1:])) and ths[-1] == math.inf
      and abs(Thstar(R_W) - 9.87) < 0.01 and Thstar(R_W) < TH_R,
      f"T_h* at WACC {Thstar(R_W):.2f} yr")
print(f"  -> minimum horizon at WACC {Thstar(R_W):.2f} years, at 22% never")
# ext timing closed form (d)(i): T* = ln[(r + delta_F) F0/S]/delta_F nondecreasing in r
ok = all(math.log((r2 + 0.3) * 20 / 4) >= math.log((r1 + 0.3) * 20 / 4)
         for r1, r2 in zip(np.linspace(0.05, 0.3, 20), np.linspace(0.06, 0.31, 20)))
Tst = {r: max(0, math.log((r + 0.3) * 20 / 4) / 0.3) for r in (0.10, R_PE)}
print(f"  -> ext timing example adoption date: {Tst[0.10]:.2f} yr at 10%, {Tst[R_PE]:.2f} yr at 22%")
check("C7 prop:reg-speed(a): adoption date of Prop ext-timing(d)(i) rises with r: 2.31 yr at 10%, 3.05 yr at the hurdle",
      ok and abs(Tst[0.10] - 2.31) < 0.005 and abs(Tst[R_PE] - 3.05) < 0.005)
# C8 bang-bang start date
s0_, C_, W_, tr_, rr2 = sp.symbols("t0 C W t_run r", positive=True)
Vt = -C_ * sp.exp(-rr2 * s0_) + W_ * (sp.exp(-rr2 * (s0_ + tr_)) - sp.exp(-rr2 * T_)) / rr2 + sp.exp(-rr2 * T_) * M_ * W_
check("C8 prop:reg-speed(b): dV/dt0 = e^{-r t0}[rC - W e^{-r t_run}] (symbolic), so the start is bang-bang",
      zero(sp.diff(Vt, s0_) - sp.exp(-rr2 * s0_) * (rr2 * C_ - W_ * sp.exp(-rr2 * tr_))))


def val_start(a, t0, T=T_HOLD, Tsea=1.0, r=R_PE, M=M_EXIT, hx=1.0):
    trun = t0 + a["t"]
    tv = math.exp(-r * T) * hx * M * a["WE"] if trun + Tsea <= T + 1e-12 else 0.0
    return -a["C"] * math.exp(-r * t0) + a["W"] * max(math.exp(-r * trun) - math.exp(-r * T), 0) / r + tv


ok = True
for _ in range(500):
    a = dict(C=RNG.uniform(0.5, 6), W=RNG.uniform(0.2, 3), t=RNG.uniform(0, 3))
    a["WE"] = a["W"] * RNG.uniform(1, 2)
    T, Tsea, r = RNG.uniform(4, 8), RNG.uniform(0, 1.5), RNG.uniform(0.1, 0.35)
    last = T - a["t"] - Tsea
    if last <= 0:
        continue
    grid = np.linspace(0, last, 401)
    vals = [val_start(a, t0, T, Tsea, r) for t0 in grid]
    best = grid[int(np.argmax(vals))]
    yld = a["W"] * math.exp(-r * a["t"]) / a["C"]
    ok &= (best == 0.0) if yld > r else (abs(best - last) < 1e-12)
check("C9 prop:reg-speed(b): optimal start is 0 if W e^{-r t_run}/C >= r_o, else the latest admissible date "
      "(500 draws)", ok)
yq = ARCH["Q"]["W"] * math.exp(-R_PE * 0.5) / ARCH["Q"]["C"]
yp = ARCH["P"]["W"] * math.exp(-R_PE * 4.0) / ARCH["P"]["C"]
vP0, vP1 = val_start(ARCH["P"], 0.0), val_start(ARCH["P"], 1.0)
vQ0h, vP0h = val_start(ARCH["Q"], 0.0, hx=0.0), val_start(ARCH["P"], 0.0, hx=0.0)
print(f"  -> cash yields: Q {yq:.3f}, P {yp:.3f}; P started at 0: {vP0:.2f}, at 1: {vP1:.2f}; "
      f"with h_x = 0: Q {vQ0h:.2f}, P {vP0h:.2f}")
check("C10 prop:reg-speed(b) example: Q (yield 0.45) starts now; P (yield 0.15 < 0.199) waits a year (3.98 -> 4.24); "
      "with h_x = 0, Q +1.03 and P -4.51",
      abs(yq - 0.453) < 0.001 and abs(yp - 0.150) < 0.001 and abs(vP0 - 3.98) < 0.005 and abs(vP1 - 4.24) < 0.005
      and abs(vQ0h - 1.03) < 0.005 and abs(vP0h + 4.51) < 0.005 and yp < R_PE < yq)
# payback cap with h_x = 0
ok = True
for _ in range(2000):
    C, W, r, tau, trun = RNG.uniform(0.5, 6), RNG.uniform(0.2, 3), RNG.uniform(0.01, 0.4), RNG.uniform(1, 8), RNG.uniform(0, 1)
    v = -C + W * max(math.exp(-r * trun) - math.exp(-r * tau), 0) / r
    if v >= 0:
        ok &= C / W <= tau - trun + 1e-12
check("C11 prop:reg-speed(b): with h_x = 0 a fundable transition has simple payback C/W <= tau - t_run (2,000 draws)", ok)


def khat(c):
    return 1 + c / 2 - math.sqrt(c + c * c / 4)


kh = {o: khat(0.125 * LAT[o]) for o in LAT}
cs = np.linspace(0.001, 3, 500)
check("C12 prop:reg-speed(c): load breakpoint 1 + c/2 - sqrt(c + c^2/4) strictly decreasing in c = r_d l0 lat_o; "
      "0.70, 0.74, 0.78 at lat 1, 0.7, 0.5",
      bool(np.all(np.diff([khat(c) for c in cs]) < 0)) and [rnd(kh[o], 2) for o in ["pub", "fam", "pe"]] == [0.70, 0.74, 0.78])

# waves (ext example): 12 processes, s = 1, T_par = 0.5, d1 = 0.2, d2 = 0.25, O_w = 0.5 ($M)
S_W, TPW, D1, D2, OW, NW = 1.0, 0.5, 0.2, 0.25, 0.5, 12
Dq = lambda n: D1 * n + D2 * n * n


def prog_cost(plan, s=S_W, Tp=TPW, D=Dq, Ow=OW):
    return sum(Tp * (s * (k + 1) * n + D(n)) + Ow for k, n in enumerate(plan))


def compositions(N, maxw):
    for w in range(1, min(N, maxw) + 1):
        for c in itertools.combinations(range(1, N), w - 1):
            yield [b - a for a, b in zip((0,) + c, c + (N,))]


ALLPLANS = list(compositions(NW, NW))
unc = min(ALLPLANS, key=prog_cost)
dl2 = min((p for p in ALLPLANS if len(p) <= 2), key=prog_cost)
dl1 = [NW]
print(f"  -> unconstrained {unc} cost {prog_cost(unc):.2f}; deadline 2 waves {dl2} {prog_cost(dl2):.2f}; "
      f"1 wave {prog_cost(dl1):.2f}")
check("C13 prop:reg-speed(c) example: unconstrained 6,4,2 (19.70); with 1.5 years left and T_sea = 1 one wave "
      "(25.70, +6.00)", unc == [6, 4, 2] and abs(prog_cost(unc) - 19.7) < 1e-9 and abs(prog_cost(dl1) - 25.7) < 1e-9
      and math.floor((1.5 - 1.0) / TPW) == 1)

# ==============================================================================================
header("D. Dip budget and constrained waves (Proposition prop:reg-dip)")
# ==============================================================================================
ok = True
for _ in range(3000):
    EB0, lev0 = RNG.uniform(10, 200), RNG.uniform(2, 6)
    lev = lev0 + RNG.uniform(0.1, 3)
    dND, dEB = RNG.uniform(-50, 100), RNG.uniform(-0.9, 0.5) * EB0
    lhs = (lev0 * EB0 + dND) <= lev * (EB0 + dEB)
    rhs = dND + lev * (-dEB) <= (lev - lev0) * EB0
    ok &= lhs == rhs
check("D1 prop:reg-dip(a): ND/EB <= lev  <=>  dND + lev(-dEB) <= (lev - lev0) EB0 when EB > 0 (3,000 draws)", ok)


def dips(plan, Dh, sh):
    out, Nc = [], 0
    for n in plan:
        out.append(Dh(n) - sh * Nc)
        Nc += n
    return out


def feasible(plan, Dh, sh, B):
    return max(dips(plan, Dh, sh)) <= B + 1e-9


def fastest_ramp(Dh, sh, B, N, integer=True, maxw=60):
    Nc, plan = 0, []
    while Nc < N - 1e-12 and len(plan) < maxw:
        budget = B + sh * Nc
        if budget <= 0:
            return None
        cap = optimize.brentq(lambda n: Dh(n) - budget, 0, 1e6)
        if integer:
            cap = math.floor(cap + 1e-9)
        if cap <= 0:
            return None
        n = min(cap, N - Nc)
        plan.append(n)
        Nc += n
    return plan


# D2 fastest ramp dominates every feasible plan (random small instances, all compositions)
ok = True
for _ in range(150):
    N = int(RNG.integers(4, 11))
    d1, d2, s = RNG.uniform(0.05, 1.0), RNG.uniform(0, 0.5), RNG.uniform(0.2, 2)
    c1, w = RNG.uniform(0, 1), RNG.uniform(1, 7)
    Dh = (lambda n, d1=d1, d2=d2, c1=c1, w=w: c1 * n + w * (d1 * n + d2 * n * n))
    sh = w * s - c1 * RNG.uniform(0, 1)
    B = RNG.uniform(1, 30)
    g = fastest_ramp(Dh, sh, B, N)
    if g is None:
        continue
    Ng = np.cumsum(g)
    for p in compositions(N, N):
        if feasible(p, Dh, sh, B):
            Np = np.cumsum(p)
            L = max(len(p), len(g))
            Np = np.pad(Np, (0, L - len(Np)), constant_values=N)
            Ngp = np.pad(Ng, (0, L - len(Ng)), constant_values=N)
            ok &= bool(np.all(Np <= Ngp + 1e-9)) and len(p) >= len(g)
check("D2 prop:reg-dip(b)(i): every feasible plan has N_k <= N^g_k and at least k-hat waves (150 instances, "
      "all compositions)", ok)
# D3 linear: closed form and optimality of the fastest ramp
k__, B_, sh_, dh_ = sp.symbols("k B s d", positive=True)
Nk = (B_ / sh_) * ((1 + sh_ / dh_) ** k__ - 1)
check("D3 prop:reg-dip(b)(ii): N_k = (B/s)[(1+s/d)^k - 1] solves N_k = N_{k-1} + (B + s N_{k-1})/d, N_0 = 0 (symbolic)",
      zero(Nk.subs(k__, 0)) and zero(sp.simplify(Nk - (Nk.subs(k__, k__ - 1) + (B_ + sh_ * Nk.subs(k__, k__ - 1)) / dh_))))
ok = True
for _ in range(150):
    N = int(RNG.integers(4, 12))
    d1, s, Ow = RNG.uniform(0.2, 2), RNG.uniform(0.2, 2), RNG.uniform(0, 1)
    B = RNG.uniform(0.5, 8)
    Dl = lambda n, d1=d1: d1 * n
    g = fastest_ramp(Dl, s, B, N)
    feas = [p for p in compositions(N, N) if feasible(p, Dl, s, B)]
    if g is None or not feas:
        continue
    best = min(prog_cost(p, s=s, D=Dl, Ow=Ow) for p in feas)
    ok &= abs(prog_cost(g, s=s, D=Dl, Ow=Ow) - best) < 1e-9
check("D4 prop:reg-dip(b)(ii): with linear dual running the fastest feasible ramp minimizes program cost "
      "(150 instances)", ok)
lin = fastest_ramp(lambda n: 1.0 * n, 1.0, 5.0, 40)
khat_lin = math.ceil(math.log(1 + 40 / 5) / math.log(2))
print(f"  -> linear example (d = s = 1, budget 5, N = 40): waves {lin}, k-hat {khat_lin}")
check("D5 prop:reg-dip(b)(ii) example: waves double, 5, 10, 20, 5; k-hat = 4", lin == [5, 10, 20, 5] and khat_lin == 4)
# D6 public budget example: guided slack 1 point of $500M revenue
S_REV = 500.0
B_PUB = 0.01 * S_REV
feasB = [p for p in ALLPLANS if feasible(p, Dq, S_W, B_PUB)]
optB = min(feasB, key=prog_cost)
pathB = [-x / S_REV * 100 for x in dips(optB, Dq, S_W)]
pathU = [-x / S_REV * 100 for x in dips(unc, Dq, S_W)]
print(f"  -> guided slack 1 point: optimum {optB}, cost {prog_cost(optB):.2f} (+{prog_cost(optB)-prog_cost(unc):.2f}); "
      f"margin path {np.round(pathB, 2)} vs {np.round(pathU, 2)}; fastest ramp {fastest_ramp(Dq, S_W, B_PUB, NW)}")
check("D6 prop:reg-dip example: budget plan 4,5,3 costs 20.45 (+0.75); waves move the margin -0.96, -0.65, +1.23 "
      "points against -2.04, +0.24, +1.72",
      optB == [4, 5, 3] and abs(prog_cost(optB) - 20.45) < 1e-9 and [rnd(x, 2) for x in pathB] == [-0.96, -0.65, 1.23]
      and [rnd(x, 2) for x in pathU] == [-2.04, 0.24, 1.72] and fastest_ramp(Dq, S_W, B_PUB, NW) == [4, 5, 3])
# unconstrained plan: dip D(n_k) - s N_{k-1} decreasing in k, so the budget binds first in wave 1
check("D7 prop:reg-dip(b)(iii): along the unconstrained plan the dip falls wave by wave (binds first in wave 1)",
      all(a > b for a, b in zip(dips(unc, Dq, S_W), dips(unc, Dq, S_W)[1:])))


# D8 exact penalty: continuous relaxation, 3 waves, KKT multipliers
def solve_hard(nw, B, Dh=Dq, dDh=lambda n: D1 + 2 * D2 * n, sh=S_W, N=NW, Tp=TPW, s=S_W):
    obj = lambda n: sum(Tp * (s * (k + 1) * n[k] + Dq(n[k])) for k in range(nw))
    cons = [dict(type="eq", fun=lambda n: np.sum(n) - N)]
    for k in range(nw):
        cons.append(dict(type="ineq", fun=lambda n, k=k: B - (Dh(n[k]) - sh * np.sum(n[:k]))))
    res = optimize.minimize(obj, np.full(nw, N / nw), constraints=cons, bounds=[(0, N)] * nw, method="SLSQP",
                            options=dict(ftol=1e-14, maxiter=500))
    n = res.x
    g = np.array([Dh(n[k]) - sh * np.sum(n[:k]) - B for k in range(nw)])
    act = [k for k in range(nw) if abs(g[k]) < 1e-7]
    # stationarity: Tp(s k + D'(n_j)) + mu_j D'(n_j) - s sum_{k>j} mu_k = lambda
    A = np.zeros((nw, 1 + len(act)))
    b = np.zeros(nw)
    for j in range(nw):
        A[j, 0] = -1.0
        for i, k in enumerate(act):
            if k == j:
                A[j, 1 + i] += dDh(n[j])
            if k > j:
                A[j, 1 + i] -= sh
        b[j] = -Tp * (s * (j + 1) + (D1 + 2 * D2 * n[j]))
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    mu = np.zeros(nw)
    for i, k in enumerate(act):
        mu[k] = sol[1 + i]
    return n, mu, obj(n), np.linalg.norm(A @ sol - b)


def solve_pen(nw, B, wmy, N=NW, Tp=TPW, s=S_W, x0=None):
    def obj(n):
        base = sum(Tp * (s * (k + 1) * n[k] + Dq(n[k])) for k in range(nw))
        pen = sum(max(Dq(n[k]) - s * np.sum(n[:k]) - B, 0.0) for k in range(nw))
        return base + wmy * Tp * pen
    best = None
    for x in ([np.full(nw, N / nw)] + ([x0] if x0 is not None else [])):
        res = optimize.minimize(obj, x, constraints=[dict(type="eq", fun=lambda n: np.sum(n) - N)],
                                bounds=[(0, N)] * nw, method="SLSQP", options=dict(ftol=1e-14, maxiter=1000))
        if best is None or res.fun < best.fun:
            best = res
    return best.x


nH, muH, cH, resid = solve_hard(3, B_PUB)
myo_star = max(muH) / TPW
print(f"  -> continuous relaxation, 3 waves: n = {np.round(nH, 3)}, multipliers {np.round(muH, 4)}, "
      f"exact-penalty threshold frak w* = {myo_star:.3f}")
check("D8 prop:reg-dip(c): KKT multipliers nonnegative and stationarity holds at the hard-budget optimum",
      np.all(muH >= -1e-8) and resid < 1e-6)
nP_hi = solve_pen(3, B_PUB, myo_star * 1.05, x0=nH)
nP_lo = solve_pen(3, B_PUB, myo_star * 0.80, x0=nH)
dip_lo = max(Dq(nP_lo[k]) - S_W * np.sum(nP_lo[:k]) for k in range(3))
check("D9 prop:reg-dip(c): penalized optimum equals the hard-budget optimum above frak w* and overshoots the "
      "guided slack below it", np.allclose(nP_hi, nH, atol=1e-3) and dip_lo > B_PUB + 1e-3,
      f"frak w* = {myo_star:.3f}; overshoot dip {dip_lo:.3f} > {B_PUB}")
check("D9b prop:reg-dip(c) example: the exact-penalty threshold is frak w* = 0.64 (continuous relaxation)",
      abs(myo_star - 0.638) < 0.002, f"{myo_star:.4f}")
# D10 integer plans by frak w
plans_by_myo = {}
for th in [0.0, 0.15, 0.30, 0.60]:
    pen = lambda p, th=th: prog_cost(p) + th * TPW * sum(max(x - B_PUB, 0) for x in dips(p, Dq, S_W))
    plans_by_myo[th] = min(ALLPLANS, key=pen)
print("  -> integer plans by frak w: " + "; ".join(f"{th}: {p} (cost {prog_cost(p):.2f}, first dip "
                                                    f"{-dips(p, Dq, S_W)[0]/S_REV*100:.2f} pts)"
                                                    for th, p in plans_by_myo.items()))
check("D10 prop:reg-dip(c), prop:reg-hybrid(a) example: frak w 0 and 0.15 keep 6,4,2; 0.30 gives 5,4,3; "
      "0.60 gives the budget plan 4,5,3",
      plans_by_myo[0.0] == [6, 4, 2] and plans_by_myo[0.15] == [6, 4, 2] and plans_by_myo[0.30] == [5, 4, 3]
      and plans_by_myo[0.60] == [4, 5, 3])
def int_plan(th):
    return min(ALLPLANS, key=lambda p: prog_cost(p) + th * TPW * sum(max(x - B_PUB, 0) for x in dips(p, Dq, S_W)))


lo_, hi_ = 0.3, 0.6
for _ in range(60):
    mid = (lo_ + hi_) / 2
    lo_, hi_ = (lo_, mid) if int_plan(mid) == [4, 5, 3] else (mid, hi_)
print(f"  -> integer plans reach the budget plan 4,5,3 from frak w = {hi_:.3f}")
check("D10b prop:reg-dip(c) example: in integers the budget plan is chosen from frak w = 0.44",
      abs(hi_ - 0.444) < 0.001, f"{hi_:.4f}")
# D11 revealed preference: market value and dip nonincreasing in frak w (random instances, integer plans)
ok = True
for _ in range(200):
    N = int(RNG.integers(4, 11))
    d1, d2, s, Ow, B = RNG.uniform(0.05, 1), RNG.uniform(0.01, 0.5), RNG.uniform(0.2, 2), RNG.uniform(0, 1), RNG.uniform(0, 5)
    D = lambda n, d1=d1, d2=d2: d1 * n + d2 * n * n
    plans = list(compositions(N, N))
    prev_cost, prev_pen = -1e18, 1e18
    for th in np.linspace(0, 5, 26):
        f = lambda p: prog_cost(p, s=s, D=D, Ow=Ow) + th * sum(max(x - B, 0) for x in dips(p, D, s))
        p = min(plans, key=f)
        cst, pn = prog_cost(p, s=s, D=D, Ow=Ow), sum(max(x - B, 0) for x in dips(p, D, s))
        ok &= cst >= prev_cost - 1e-9 and pn <= prev_pen + 1e-9
        prev_cost, prev_pen = cst, pn
check("D11 prop:reg-dip(c): program cost nondecreasing and excess dip nonincreasing in frak w (200 instances)", ok)
# D12 PE covenant example
EB0, LEV0_T, LEVBAR_T, T1, WCOV = 100.0, 6.1, 6.5, 2.5, 1.0
B_COV = (LEVBAR_T - LEV0_T) * EB0
Dh_pe = lambda n: T1 * n + LEVBAR_T * WCOV * Dq(n)
sh_pe = LEVBAR_T * WCOV * S_W - T1
feasPE = [p for p in ALLPLANS if feasible(p, Dh_pe, sh_pe, B_COV)]
optPE = min(feasPE, key=prog_cost)
rampPE = fastest_ramp(Dh_pe, sh_pe, B_COV, NW)
print(f"  -> covenant: headroom {B_COV:.0f}; Dhat = {T1:.1f} n + 6.5 D(n), shat = {sh_pe:.1f}; optimum {optPE} "
      f"(cost {prog_cost(optPE):.2f}); fastest ramp {rampPE}; headroom used {np.round(dips(optPE, Dh_pe, sh_pe), 1)}")
check("D12 prop:reg-dip example: headroom $40M; covenant plan 3,4,5 (cost 21.95, +2.25), the fastest ramp",
      abs(B_COV - 40) < 1e-9 and optPE == [3, 4, 5] and rampPE == [3, 4, 5] and abs(prog_cost(optPE) - 21.95) < 1e-9)
check("D13 prop:reg-dip(a) example: a dollar of EBITDA dip uses 6.5 dollars of headroom, a capitalized dollar one",
      abs(Dh_pe(1) - Dh_pe(0) - (T1 + LEVBAR_T * Dq(1))) < 1e-12)
# D14 exact covenant with interim cash flows (tested at the end of each wave) for the 3,4,5 plan
ND, Nc, worst = 0.0, 0, -1e9
for n in optPE:
    ND += T1 * n
    flow = S_W * Nc - Dq(n)
    ND -= flow * TPW
    worst = max(worst, ND + LEVBAR_T * WCOV * (-flow))
    Nc += n
feasEx = []
for p_ in ALLPLANS:
    ND_, Nc_, w_ = 0.0, 0, -1e9
    for n_ in p_:
        ND_ += T1 * n_
        fl_ = S_W * Nc_ - Dq(n_)
        ND_ -= fl_ * TPW
        w_ = max(w_, ND_ + LEVBAR_T * WCOV * (-fl_))
        Nc_ += n_
    if w_ <= B_COV + 1e-9:
        feasEx.append(p_)
optEx = min(feasEx, key=prog_cost)
print(f"  -> exact covenant use with interim cash, end of each wave: max {worst:.2f} of {B_COV:.0f}; exact-test optimum {optEx}")
check("D14 prop:reg-dip(b) approximation: with interim cash flows the 3,4,5 plan stays within the covenant "
      "(peak use $34.1M of $40M) and remains optimal under the exact test", worst <= B_COV and abs(worst - 34.1) < 0.05
      and optEx == [3, 4, 5])
# D15 PE squeeze: two waves before the deadline
N2 = sum(rampPE[:2])
miss = NW - N2
lost_tv = miss * M_EXIT * S_W
def two_wave(x):
    n1 = optimize.brentq(lambda n: Dh_pe(n) - (B_COV + x), 0, 1e4)
    n2 = optimize.brentq(lambda n: Dh_pe(n) - (B_COV + x + sh_pe * n1), 0, 1e4)
    return n1 + n2 - NW
cure = optimize.brentq(two_wave, 0, 500)
print(f"  -> squeeze: 2 waves migrate {N2}, {miss} miss the exit (run-rate value at exit ${lost_tv:.0f}M); "
      f"equity cure needed for 12 in two waves: ${cure:.1f}M")
check("D15 prop:reg-dip(d) example: two waves migrate 7; 5 processes ($70M of exit value) miss; a $10M cure gives 4,5,3",
      N2 == 7 and miss == 5 and abs(lost_tv - 70) < 1e-9 and fastest_ramp(Dh_pe, sh_pe, B_COV + 10, NW) == [4, 5, 3])
print(f"  -> continuous cure for completion in two waves: {cure:.2f}")
icure = min(max(Dh_pe(n1) - B_COV, Dh_pe(NW - n1) - sh_pe * n1 - B_COV) for n1 in range(1, NW))
print(f"  -> integer cure for 12 processes in two waves: ${icure:.1f}M")
check("D16 prop:reg-dip(d): completion in two waves needs a cure of $30.6M (continuous) or $41.3M (integer waves 6, 6)",
      abs(cure - 30.61) < 0.01 and abs(icure - 41.3) < 0.01, f"{cure:.2f}, {icure:.2f}")

# ==============================================================================================
header("E. Metrics (Lemma lem:reg-waterfall, Proposition prop:reg-metrics)")
# ==============================================================================================


def waterfall_lp(Mg, T, h=R_PREF, cy=CARRY):
    pref = (1 + h) ** T
    if Mg <= pref:
        return Mg
    if Mg <= 1 + (pref - 1) / (1 - cy):
        return pref
    return 1 + (1 - cy) * (Mg - 1)


def waterfall_steps(Mg, T, h=R_PREF, cy=CARRY):
    """sequential distribution: capital, preferred return, 100% catch-up, then split"""
    lp, gp, rem = 0.0, 0.0, Mg
    x = min(rem, 1.0); lp += x; rem -= x
    x = min(rem, (1 + h) ** T - 1); lp += x; rem -= x
    need = cy / (1 - cy) * (lp - 1)        # GP catch-up target: cy of total profit
    x = min(rem, max(need - gp, 0)); gp += x; rem -= x
    lp += (1 - cy) * rem; gp += cy * rem
    return lp


ok = all(abs(waterfall_lp(M, T) - waterfall_steps(M, T)) < 1e-12
         for M, T in zip(RNG.uniform(0.3, 5, 3000), RNG.uniform(1, 10, 3000)))
check("E1 lem:reg-waterfall: closed-form LP multiple equals the sequential waterfall (3,000 draws)", ok)
ok = all(waterfall_lp(M + 1e-6, 5) >= waterfall_lp(M, 5) for M in np.linspace(0.5, 4, 2000))
check("E2 lem:reg-waterfall: LP multiple nondecreasing in the gross multiple (flat in the catch-up zone)", ok)

# LBO example (Props reg-metrics and reg-lbo)
G_LBO, CF, TAX, CTX = 0.05, 0.55, 0.21, 0.02
RDEBT = math.log(1 + RDEBT_ANN)   # 8% annual debt rate (assumed) -> 7.70% continuous
WE_P, C_P = 30.0, 40.0


def dEB(t, Tr):
    return WE_P * math.exp(G_LBO * t) * min(t / Tr, 1.0)


def dCF(t, Tr):
    return (1 - TAX) * (dEB(t, Tr) - (C_P / Tr if t < Tr else 0.0))


def Vprog(Tr, r=R_W):
    if not math.isfinite(Tr):
        return 0.0
    a = integrate.quad(lambda t: math.exp(-r * t) * dCF(t, Tr), 0, Tr)[0]
    return a + (1 - TAX) * WE_P * math.exp((G_LBO - r) * Tr) / (r - G_LBO)


V_SQ = CF * EB0 / (R_W - G_LBO)


def sponsor(P0, prem, rpe, Tr=2.0, M=M_EXIT, fair=False, rd=RDEBT, T=T_HOLD, lev0=LEV0, pbL=0.0, hx=1.0):
    """EV_T = M [EB^sq_T + h_x dEB_T]: the buyer capitalizes the share h_x of the program's seasoned run-rate"""
    ND0 = lev0 * EB0
    EBT = EB0 * math.exp(G_LBO * T) + hx * (dEB(T, Tr) if math.isfinite(Tr) else 0.0)
    FCF = lambda t: CF * EB0 * math.exp(G_LBO * t) + (dCF(t, Tr) if math.isfinite(Tr) else 0.0)
    pts = [Tr] if math.isfinite(Tr) and Tr < T else None
    FV = integrate.quad(lambda t: math.exp(rd * (T - t)) * FCF(t), 0, T, points=pts)[0]
    if fair:   # value at T of the remaining flows under the buyer's plan, at the common rate rw
        EV_T = (CF * EB0 * math.exp(G_LBO * T) + ((1 - TAX) * WE_P * math.exp(G_LBO * T) if math.isfinite(Tr) else 0)) \
            / (R_W - G_LBO)
    else:
        EV_T = M * EBT
    NDT = ND0 * math.exp(rd * T) - FV
    EqT = EV_T - NDT - pbL
    Eq0 = (1 + prem + CTX) * P0 - ND0
    return dict(npv=math.exp(-rpe * T) * EqT - Eq0, moic=EqT / Eq0, Eq0=Eq0, EqT=EqT, EBT=EBT, FV=FV, ND0=ND0,
                EV_T=EV_T, NDT=NDT)


# E3 sponsor identity: NPV = V^sp - (1 + p) P0 - C_tx + frak L - risk
ok = True
for _ in range(200):
    P0, prem, rpe, rd = RNG.uniform(800, 2000), RNG.uniform(0, 0.6), RNG.uniform(0.08, 0.3), RNG.uniform(0.03, 0.12)
    lev0, pbL = RNG.uniform(2, 7), RNG.uniform(0, 100)
    s = sponsor(P0, prem, rpe, rd=rd, lev0=lev0, pbL=pbL)
    Vsp = math.exp(-rpe * T_HOLD) * (s["EV_T"] + s["FV"])
    fL = s["ND0"] * (1 - math.exp(-(rpe - rd) * T_HOLD))
    ident = Vsp - (1 + prem) * P0 - CTX * P0 + fL - math.exp(-rpe * T_HOLD) * pbL
    ok &= abs(s["npv"] - ident) < 1e-8 * (1 + abs(ident))
check("E3 prop:reg-lbo(a): sponsor NPV = V^sp - (1+p)P0 - C_tx + ND0[1 - e^{-(r_pe - r_debt)T}] - e^{-r_pe T} p_b L_b "
      "(200 draws)", ok)
# metrics example: a buyout entered and exited at the same multiple, 14x (no multiple expansion), h_x in {1, 0.5}
P0M = M_EXIT * EB0          # enterprise value at entry, no premium (entry multiple = exit multiple)
MET = {}
for hx in (1.0, 0.5):
    a_ = sponsor(P0M, 0.0, R_PE, hx=hx)
    b_ = sponsor(P0M, 0.0, R_PE, Tr=math.inf, hx=hx)
    lpa, lpb = waterfall_lp(a_["moic"], T_HOLD) / (1 + FEE * T_HOLD), waterfall_lp(b_["moic"], T_HOLD) / (1 + FEE * T_HOLD)
    MET[hx] = dict(m=a_["moic"], i=a_["moic"] ** (1 / T_HOLD) - 1, m0=b_["moic"], i0=b_["moic"] ** (1 / T_HOLD) - 1,
                   lp=lpa, li=lpa ** (1 / T_HOLD) - 1, lp0=lpb, li0=lpb ** (1 / T_HOLD) - 1, Eq0=a_["Eq0"],
                   dEB=a_["EBT"] - b_["EBT"])
    print(f"  -> buyout at 14x in and out, h_x = {hx}: entry equity {a_['Eq0']:.0f}; gross MOIC {MET[hx]['m']:.3f} "
          f"(IRR {MET[hx]['i']:.4f}) vs {MET[hx]['m0']:.3f} ({MET[hx]['i0']:.4f}) without the program; LP net "
          f"{MET[hx]['lp']:.3f} ({MET[hx]['li']:.4f}) vs {MET[hx]['lp0']:.3f} ({MET[hx]['li0']:.4f})")
m1, m5 = MET[1.0], MET[0.5]
check("E4 prop:reg-metrics(a) example (14x in and out): h_x = 1 gross MOIC 2.47 (IRR 16.2%) vs 1.71 (9.3%), LP 1.94 "
      "(11.7%) vs 1.42 (6.0%); h_x = 0.5 gross 2.16 (13.7%), LP 1.72 (9.4%)",
      abs(m1["m"] - 2.467) < 0.001 and abs(m1["i"] - 0.1624) < 0.0005 and abs(m1["m0"] - 1.705) < 0.001
      and abs(m1["i0"] - 0.0930) < 0.0005 and abs(m1["lp"] - 1.941) < 0.001 and abs(m1["li"] - 0.1168) < 0.0005
      and abs(m1["lp0"] - 1.417) < 0.001 and abs(m1["li0"] - 0.0598) < 0.0005
      and abs(m5["m"] - 2.155) < 0.001 and abs(m5["i"] - 0.1365) < 0.0005 and abs(m5["lp"] - 1.718) < 0.001
      and abs(m5["li"] - 0.0944) < 0.0005)
amp = M_EXIT * 0.01 * EB0 / m1["Eq0"]
upl1, upl5 = m1["m"] - m1["m0"], m5["m"] - m5["m0"]
cash_part = upl1 - M_EXIT * m1["dEB"] / m1["Eq0"]
print(f"  -> MOIC per 1% of entry EBITDA at exit {amp:.4f}; uplift {upl1:.3f} (h_x = 1) and {upl5:.3f} (h_x = 0.5); "
      f"cash part {cash_part:.3f}; exit part scales with h_x M_exit")
check("E5 prop:reg-metrics(a): each 1% of entry EBITDA capitalized at exit adds 0.01 M_exit EB0/Eq0 = 0.0154 of MOIC; "
      "the uplift is affine in h_x M_exit (0.76 at h_x = 1, 0.45 at 0.5)",
      abs(amp - 0.01542) < 0.00005 and abs(upl1 - 0.762) < 0.001 and abs(upl5 - 0.450) < 0.001
      and abs((upl1 - cash_part) / 1.0 - (upl5 - cash_part) / 0.5) < 1e-9)
# E6 public EPS path for the unconstrained and budget plans (annual, flows only), N_sh = 100M, tau = 0.21
def annual_oi(plan, Tp=TPW, s=S_W, years=3):
    """GAAP operating-income change by fiscal year from wave flows (one-time charges excluded)"""
    segs, t0, Nc = [], 0.0, 0
    for n in plan:
        segs.append((t0, t0 + Tp, s * Nc - Dq(n)))
        t0 += Tp
        Nc += n
    out = []
    for y in range(years):
        lo, hi = y, y + 1
        v = sum(f * max(0, min(b, hi) - max(a, lo)) for a, b, f in segs)
        v += s * Nc * max(0, hi - max(t0, lo))
        out.append(v)
    return out


eps_u = [(1 - TAX) * x / 100 for x in annual_oi(unc)]
eps_b = [(1 - TAX) * x / 100 for x in annual_oi(optB)]
print(f"  -> EPS change ($/share, 100M shares): unconstrained {np.round(eps_u, 3)}, budget plan {np.round(eps_b, 3)}")
check("E6 prop:reg-metrics(b) example: EPS -$0.036, +$0.081, +$0.095 (6,4,2) vs -$0.032, +$0.072, +$0.095 (4,5,3)",
      [rnd(x, 3) for x in eps_u] == [-0.036, 0.081, 0.095] and [rnd(x, 3) for x in eps_b] == [-0.032, 0.072, 0.095])
# E7 Delta R*_o first order vs exact for regime weights
ok = True
for X in [X_PUB, X_FAM, X_MY, XPE3]:
    da, dk, dsig, dG = 0.005, 0.01, 0.05, 0.002
    lam1 = LAM * (1 - dsig) ** (-ALPHA)
    base = frontier(X, LAM)
    def Rst(m0, k, lam, G):
        y = X - k
        return m0 + y * G + CA * (lam * y) ** (1 / (1 - ALPHA))
    eps = 1e-6
    exact = (Rst(M0 + eps * da, K0 + eps * dk, LAM * (1 - eps * dsig) ** (-ALPHA), G_ + eps * dG) - Rst(M0, K0, LAM, G_)) / eps
    fo = da - base["g"] * dk + base["sig"] * dsig + (X - K0) * dG
    ok &= abs(exact - fo) < 1e-4
check("E7 prop:reg-metrics(c): first-order Delta R*_o = da - g*(X_o) dk + sigma*(X_o) delta_sigma + (X_o - k) dG_i "
      "at each regime weight", ok)

# ==============================================================================================
header("F. Change of ownership (Proposition prop:reg-lbo)")
# ==============================================================================================
dVA, dVB = Vprog(2.0) - Vprog(5.0), Vprog(2.0)
print(f"  -> program value at WACC: {Vprog(2.0):.1f} (PE pace, 2 years), {Vprog(5.0):.1f} (public pace, 5 years); "
      f"execution gain {dVA:.1f} (slower) or {dVB:.1f} (blocked)")
ok = True
for case, Vpub in [("A", Vprog(5.0)), ("B", 0.0)]:
    P0 = V_SQ + Vpub
    pm = optimize.brentq(lambda p: sponsor(P0, p, R_W, fair=True, rd=R_W)["npv"], -0.99, 5)
    ok &= abs(pm * P0 - ((Vprog(2.0) - Vpub) - CTX * P0)) < 1e-6 * P0
check("F1 prop:reg-lbo(b): frictionless benchmark p_max P0 = Delta V^exec - C_tx (both cases)", ok)
ok = True
for _ in range(100):
    rr = RNG.uniform(0.07, 0.12)
    P0 = V_SQ * RNG.uniform(0.8, 1.2)
    # frictionless with arbitrary common rate: build directly
    def npv_common(prem, rr=rr, P0=P0):
        s = sponsor(P0, prem, rr, fair=False, rd=rr, M=0.0)
        # fair exit at the common rate rr for the PE plan's remaining flows
        EV_T = (CF * EB0 * math.exp(G_LBO * T_HOLD) + (1 - TAX) * WE_P * math.exp(G_LBO * T_HOLD)) / (rr - G_LBO)
        return math.exp(-rr * T_HOLD) * (s["EqT"] + EV_T) - s["Eq0"]
    pm = optimize.brentq(npv_common, -5, 5)
    Vsq_r = CF * EB0 / (rr - G_LBO)
    ok &= abs(pm * P0 - (Vsq_r + Vprog(2.0, rr) - P0 - CTX * P0)) < 1e-6 * P0
check("F2 prop:reg-lbo(b): with r_pe = r_debt = r and a fair exit, p_max P0 = value of the firm under the PE plan "
      "at r - P0 - C_tx (100 draws)", ok)
P0B = V_SQ + 0.0         # case B: the public owner would not execute the program (blocked by the dip budget)
P0A = V_SQ + Vprog(5.0)
pA = optimize.brentq(lambda p: sponsor(P0A, p, R_W, fair=True, rd=R_W)["npv"], -0.99, 5)
pB = optimize.brentq(lambda p: sponsor(P0B, p, R_W, fair=True, rd=R_W)["npv"], -0.99, 5)
M_ENT = (1 + PREMIUM_REQ) * P0B / EB0     # baseline: the sponsor exits at the multiple it paid
pB22 = optimize.brentq(lambda p: sponsor(P0B, p, R_PE, M=M_ENT)["npv"], -0.99, 5)
rbe = optimize.brentq(lambda r: sponsor(P0B, PREMIUM_REQ, r, M=M_ENT)["npv"], -0.5, 1.0)
pB22h = optimize.brentq(lambda p: sponsor(P0B, p, R_PE, M=M_ENT, hx=0.5)["npv"], -0.99, 5)
rbeh = optimize.brentq(lambda r: sponsor(P0B, PREMIUM_REQ, r, M=M_ENT, hx=0.5)["npv"], -0.5, 1.0)
sBB = sponsor(P0B, PREMIUM_REQ, R_PE, M=M_ENT)
print(f"  -> exit at the multiple paid ({M_ENT:.2f}x): p_max {pB22:.4f} (h_x = 1), {pB22h:.4f} (h_x = 0.5); "
      f"break-even hurdle {rbe:.4f}, {rbeh:.4f}")
fL = sBB["ND0"] * (1 - math.exp(-(R_PE - RDEBT) * T_HOLD))
Vsp = math.exp(-R_PE * T_HOLD) * (sBB["EV_T"] + sBB["FV"])
wedge = Vsp - (V_SQ + Vprog(2.0))
print(f"  -> frictionless p_max: {pA:.4f} (slower public pace), {pB:.4f} (blocked); at the sponsor's terms "
      f"(22%, exit at the multiple paid, 8% debt) p_max = {pB22:.3f}; break-even hurdle {rbe:.4f}; leverage term {fL:.1f}; valuation wedge "
      f"{wedge:.1f}")
check("F3 prop:reg-lbo example: frictionless p_max -0.5% (public merely slower) and 37% (blocked) vs 30% required",
      abs(pA + 0.0049) < 0.0005 and abs(pB - 0.374) < 0.001)
print(f"  -> break-even hurdles, annual: {math.exp(rbe) - 1:.4f} (h_x = 1), {math.exp(rbeh) - 1:.4f} (h_x = 0.5), "
      f"against the 22% target ({R_PE:.4f} continuous)")
check("F4 prop:reg-lbo example (exit at the 18.2x paid, 19.9% continuous hurdle, 7.7% debt): p_max = -0.4% (h_x = 1) and "
      "-8.3% (0.5); break-even hurdle 13.5% and 11.3% continuous (14.4% and 11.9% annual); frak L = 270, frak D = -798",
      abs(M_ENT - 18.20) < 0.005 and abs(pB22 + 0.0036) < 0.0005 and abs(pB22h + 0.0834) < 0.0005
      and abs(rbe - 0.1346) < 0.0005 and abs(rbeh - 0.1125) < 0.0005 and abs(math.exp(rbe) - 1 - 0.144) < 0.0005
      and abs(math.exp(rbeh) - 1 - 0.119) < 0.0005 and abs(fL - 269.7) < 0.1 and abs(wedge + 797.9) < 0.1,
      f"{pB22:.4f}, {rbe:.4f}, {fL:.2f}, {wedge:.1f}")
ok = abs(pB22 * P0B - (dVB + wedge + fL - CTX * P0B)) < 1e-6 * P0B
check("F5 prop:reg-lbo(c): decomposition p_max P0 = Delta V^exec + frak D + frak L - C_tx - risk (example)", ok)
# F6 revealed preference: value of the public plan nonincreasing in frak w (random linear objectives)
ok = True
for _ in range(300):
    n = 30
    npv_, P_ = RNG.normal(0, 1, n), RNG.uniform(0, 2, n)
    prevV, prevP = 1e18, 1e18
    for th in np.linspace(0, 5, 51):
        i = int(np.argmax(npv_ - th * P_))
        ok &= npv_[i] <= prevV + 1e-12 and P_[i] <= prevP + 1e-12
        prevV, prevP = npv_[i], P_[i]
check("F6 prop:reg-lbo(c): the market value and the penalty of the chosen plan are nonincreasing in frak w "
      "(300 random plan sets)", ok)
# F7 growth-weight loss of the ownership change, capitalized
rho_pe = ((XPE3 - K0) / (X_PUB - K0)) ** (ALPHA / (1 - ALPHA))
loss_pe = FR["pub"]["Pi"] * (1 - (rho_pe - ALPHA * rho_pe ** (1 / ALPHA)) / (1 - ALPHA))
print(f"  -> growth-weight loss if the PE weight X = {XPE3:.2f} replaces X = 8: {100*loss_pe:.2f} points of R a year")
check("F7 prop:reg-lbo(c): growth-weight loss = Pi[1 - (rho - alpha rho^(1/alpha))/(1-alpha)], "
      "rho = ((X^pe-k)/(X-k))^(alpha/(1-alpha)); example 2.4 points",
      abs(FR["pub"]["R"] - ((M0 - FR["pe"]["sig"]) + X_PUB * FR["pe"]["g"]) - loss_pe) < 1e-12 and abs(100 * loss_pe - 2.41) < 0.005,
      f"{100*loss_pe:.3f}")

# ==============================================================================================
header("G. Hybrids (Proposition prop:reg-hybrid)")
# ==============================================================================================
X_DC = K0 + (X_PUB - K0) / (1 + MYO_DC)
check("G1 prop:reg-hybrid(a): dual-class weight X^my(0.15) = 6.96 lies between 6.15 and 8",
      X_MY < X_DC < X_PUB and abs(X_DC - 6.957) < 0.001)
# G2 PIPE relaxes cash/covenant budgets, not the GAAP budget
pipe_pub = min((p for p in ALLPLANS if feasible(p, Dq, S_W, B_PUB)), key=prog_cost)
pipe_pe = fastest_ramp(Dh_pe, sh_pe, B_COV + 10.0, NW)
check("G2 prop:reg-hybrid(b)(i): $10M of new equity leaves the GAAP-budget plan at 4,5,3 and moves the covenant "
      "plan from 3,4,5 to 4,5,3", pipe_pub == [4, 5, 3] and pipe_pe == [4, 5, 3]
      and min((p for p in ALLPLANS if feasible(p, Dh_pe, sh_pe, B_COV + 10)), key=prog_cost) == [4, 5, 3])
# G3 weighted objective: argmax of omega R_X1 + (1-omega) R_X2 is the Rule-of-(omega X1 + (1-omega) X2) optimum
ok = True
for _ in range(300):
    X1, X2, om, ell = RNG.uniform(1, 12), RNG.uniform(1, 12), RNG.uniform(0, 1), RNG.uniform(0.03, 0.4)
    obj = lambda s: -(om * (X1 * ell * s ** ALPHA - s) + (1 - om) * (X2 * ell * s ** ALPHA - s))
    sopt = optimize.minimize_scalar(obj, bounds=(0, 5), method="bounded", options=dict(xatol=1e-12)).x
    ok &= abs(sopt - frontier(om * X1 + (1 - om) * X2, ell)["sig"]) < 1e-5 * (1 + sopt)
check("G3 prop:reg-hybrid(b)(ii): a weighted objective acts on the weighted growth weight (300 draws)", ok)
# G4 carve-out: shared separation cost and TSA overlap credit
CSEP = 600e3
CPAR_SH = 0.8 * C0_R                      # the duplication premium both routes bear during the TSA overlap
base10 = core_npv(TP, R_W, TH_R, TPAR_STAR)
carve = base10 + CSEP + CPAR_SH * annuity(R_W, TPAR_STAR)
ThS0 = Thstar(R_W)
ThS1 = optimize.brentq(lambda T: core_npv(TP, R_W, T, TPAR_STAR) + CSEP + CPAR_SH * annuity(R_W, TPAR_STAR),
                       TPAR_STAR + 1e-6, 100)
print(f"  -> carve-out (Case R at WACC): NPV {base10:,.0f} -> {carve:,.0f}; minimum horizon {ThS0:.2f} -> {ThS1:.2f} years")
check("G4 prop:reg-hybrid(c) example: a shared $600k rebuild and $800k-a-year TSA overlap add $735k to Case R and cut "
      "its minimum horizon from 9.9 to 3.7 years", abs(carve - base10 - 735e3) < 1e3 and abs(ThS0 - 9.87) < 0.01
      and abs(ThS1 - 3.67) < 0.01,
      f"{carve:,.0f}, {ThS0:.3f}, {ThS1:.3f}")
# G5 market rule: dV/dg / dV/dm = X^scr and dV/dm = S0 frakA (Part I Lemma valuation2), symbolic for T = 4
mm, gg, rr3, th3, mbar, Ginf = sp.symbols("m g r theta mbar Ginf", positive=True)
Tn = 4
eta = (1 + gg) / (1 + rr3)
Gam = (1 + Ginf) / (rr3 - Ginf)
V = mm * sum(eta ** t for t in range(1, Tn + 1)) + (th3 * mm + (1 - th3) * mbar) * eta ** Tn * Gam
dVdm = sp.diff(V, mm)
Xscr = (mm * sum(t * eta ** t for t in range(1, Tn + 1)) + (th3 * mm + (1 - th3) * mbar) * Tn * eta ** Tn * Gam) / \
    ((1 + gg) * (sum(eta ** t for t in range(1, Tn + 1)) + th3 * eta ** Tn * Gam))
check("G5 prop:reg-hybrid(d), prop:reg-value(a): dV/dm = S0[A_T + theta eta^T Gamma] and dV/dg = X^scr dV/dm "
      "(symbolic, T = 4)", zero(dVdm - (sum(eta ** t for t in range(1, Tn + 1)) + th3 * eta ** Tn * Gam))
      and zero(sp.simplify(sp.diff(V, gg) - Xscr * dVdm)))
XVC = X_exit(R_VC, T_VC, 8.0, mh=0.15, gm=0.25)
print(f"  -> VC weight with 7 years to exit, revenue multiple 8 at exit, marginal margin 0.15 growing 25%: {XVC:.2f}")
check("G6 prop:reg-hybrid(d) example: X^vc(7) = 7.93 at the 27.0% continuous VC rate", abs(XVC - 7.93) < 0.005
      and abs(R_VC - 0.2700) < 0.00005)

# ==============================================================================================
header("H. The core's invoice chain under each regime (reads data/examples/invoice_chain.json)")
# ==============================================================================================
import json
import os
SKIPPED = []
JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "examples", "invoice_chain.json")


def _find(d, names):
    """depth-first search for the first key in names (the single source's schema is owned by the core theorist)"""
    if isinstance(d, dict):
        for n in names:
            if n in d and isinstance(d[n], (int, float)):
                return float(d[n])
        for v in d.values():
            x = _find(v, names)
            if x is not None:
                return x
    return None


KEYS = dict(W=["W", "W_cash", "saving_W"], F=["F", "F_build", "build_F"], I=["I", "capex_I"], CJ=["C_J", "CJ"],
            Cpar=["C_par", "Cpar"], Cstr=["C_str", "Cstr"], Cwo=["C_wo", "Cwo"], pis=["varpi_p", "varpi", "pis"],
            bbar=["bbar_p", "bbar", "b_bar"], Tdet=["T_det", "Tdet"], Lroll=["L_roll", "Lroll"],
            Tpar=["T_par", "Tpar", "T_par_star"], Th=["T_h", "Th"])
if not os.path.exists(JSON_PATH):
    SKIPPED.append("H1")
    print("[SKIP] H1 data/examples/invoice_chain.json not found: the core's invoice chain is not evaluated by regime "
          "(dependency on the core theorist's single source; no number in theory_regimes.tex uses it)")
else:
    with open(JSON_PATH) as fh:
        IC = json.load(fh)
    tj = IC.get("transition", {})
    MAPJ = dict(W="W", F="F", I="I", CJ="C_J", Cpar="C_par", Cstr="C_str", Cwo="C_wo", pis="varpi_p", bbar="bbar_p",
                Tdet="T_det", Lroll="L_roll")
    missing = [v for v in list(MAPJ.values()) + ["T_par", "T_h", "r"] if tj.get(v) is None]
    if missing:
        SKIPPED.append("H1")
        print(f"[SKIP] H1 invoice_chain.json transition block lacks {missing}; regime evaluation not run")
    else:
        Pj = {k: float(tj[v]) for k, v in MAPJ.items()}
        Tpj, Thj, rj = float(tj["T_par"]), float(tj["T_h"]), float(tj["r"])
        npv_core_json = tj.get("results", {}).get("NPV")
        mine = core_npv(Pj, rj, Thj, Tpj)
        print(f"  .. single source (version {IC.get('meta', {}).get('version')}): W = {Pj['W']:,.0f}, F = {Pj['F']:,.0f}, "
              f"T_h = {Thj:g}; core NPV {npv_core_json:,.0f}, this script {mine:,.0f} at r = {rj}")
        check("H0 single source: eq:tasks-npv as implemented here reproduces the core's NPV of the invoice chain",
              npv_core_json is not None and abs(mine - npv_core_json) < 1e-6 * (1 + abs(npv_core_json)))
        okH, vals_reg = True, {}
        for name, (r, T, Mt) in dict(pub=(R_W, 1e9, 0.0), fam=(R_FAM, 1e9, 0.0), pe1=(R_PE, T_HOLD, M_EXIT),
                                     pe5=(R_PE, T_HOLD, 0.5 * M_EXIT), vc=(R_VC, T_VC, FA_VC)).items():
            v1 = regime_value(Pj, r, T, Thj, Tpj, TV_per_run=Mt)
            v2 = branch_value(Pj, r, T, Thj, Tpj, Mt)
            okH &= abs(v1 - v2) < 1e-6 * (1 + abs(v2))
            vals_reg[name] = v1
        print("  .. invoice chain by regime: " + ", ".join(f"{k} {v:,.0f}" for k, v in vals_reg.items()))
        check("H1 prop:reg-value(a) on the core's invoice chain (single source): closed form = outcome tree, and with a "
              "negative run-rate saving (W < 0) no regime values it above zero",
              okH and (Pj["W"] >= 0 or max(vals_reg.values()) < 0))

# ==============================================================================================
header("I. Permanent-capital row of tab:reg-presets and the myopia symbol")
# ==============================================================================================
import re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
HUR_U_ANN, HUR_L_ANN, LTV_PC, COV_PC, T_REP_PC = 0.25, 0.65, 0.85, 4.0, 5   # F-1 policy (via theory_acquirer.tex)
NOTES_USD_C, NOTES_EUR_C = 0.09625, 0.08625   # 6-K of 28 Oct 2026, senior secured notes (USD 1.25bn, EUR 500m)


def _pct(x, nd=1):
    return f"{100 * x:.{nd}f}"


with open(os.path.join(ROOT, "part2", "theory_regimes.tex")) as fh:
    TEX_REG = fh.read()
row = next((ln for ln in TEX_REG.splitlines() if ln.startswith("Permanent capital, serial acquirer")), "")
row = row if "\\input{part2/tables/acquirer_macros.tex}" in TEX_REG else ""   # macros must be loaded before the table
need = [f"=25\\%$ ({_pct(math.log(1 + HUR_U_ANN))}\\%)", f"=65\\%$ ({_pct(math.log(1 + HUR_L_ANN))}\\%)",
        "=85\\%$", "4.0\\,\\mathrm{EB}_t", "T^{\\rm IRR}=5", "\\ln(1+\\acqNotesUsdC)=\\acqRdebt", "\\citep{bendingspoons2026sixk}", "r_{\\rm tv}=r_w",
        "\\ref{prop:acq-pc}", "\\infty"]
print(f"  -> pc row: unlevered {_pct(math.log(1 + HUR_U_ANN), 2)}%, levered {_pct(math.log(1 + HUR_L_ANN), 2)}% continuous; "
      f"missing strings: {[s for s in need if s not in row]}")
check("I1 tab:reg-presets pc row: infinite horizon, hurdles 25% and 65% annual shown as ln(1+r) = 22.3% and 50.1%, "
      "LTV 85%, 5-year repayment, covenant 4.0, r_tv = r_w, debt rate ln(1.09625) via acqRdebt cited to the 6-K, "
      "cross-reference to prop:acq-pc",
      bool(row) and all(s in row for s in need))

MAC_PATH = os.path.join(ROOT, "part2", "tables", "acquirer_macros.tex")
if os.path.exists(MAC_PATH):
    with open(MAC_PATH) as fh:
        MAC = dict(re.findall(r"\\providecommand\{\\(acq\w+)\}\{([^}]*)\}", fh.read()))
    want = dict(acqHurU="25\\%", acqHurL="65\\%", acqIrrU=f"{_pct(math.log(1 + HUR_U_ANN))}\\%",
                acqIrrL=f"{_pct(math.log(1 + HUR_L_ANN))}\\%", acqLtv="85\\%", acqTirr=str(T_REP_PC),
                acqRtv=f"{_pct(R_W, 2)}\\%", acqRdebt=f"{_pct(math.log(1 + NOTES_USD_C), 2)}\\%",
                acqNotesUsdC="9.625\\%", acqNotesEurC="8.625\\%")
    if "acqRdebtReg" in MAC:   # the acquirer's copy of the regimes debt preset (its pc debt rate is its own)
        want["acqRdebtReg"] = f"{_pct(RDEBT)}\\%"
    got = {k: MAC.get(k) for k in want}
    cov_ok = MAC.get("acqCov") is not None and abs(float(MAC["acqCov"]) - COV_PC) < 1e-9
    print(f"  -> acquirer macros: {got}, acqCov {MAC.get('acqCov')}")
    check("I2 the pc row agrees with the acquirer section's generated macros (hurdles, conversions, LTV, repayment "
          "years, covenant, r_tv = r_w, pc debt rate ln(1 + 9.625%) = 9.19% and coupons, regimes debt preset copy)", all(got[k] == v for k, v in want.items()) and cov_ok,
          str({k: (got[k], v) for k, v in want.items() if got[k] != v}))
else:
    print("  [SKIP] I2: part2/tables/acquirer_macros.tex not found")
    SKIPPED.append("I2")

own = ["theory_regimes.tex", "proofs_regimes.tex"]
others = [f for f in os.listdir(os.path.join(ROOT, "part2")) if f.endswith(".tex") and f not in own
          and f not in ("theory_acquirer.tex", "proofs_acquirer.tex")]
clash_own = [f for f in own if "\\vartheta" in open(os.path.join(ROOT, "part2", f)).read()]
clash_oth = [f for f in others if re.search(r"\\mathfrak\s*\{?w\b", open(os.path.join(ROOT, "part2", f)).read())]
print(f"  -> vartheta in own files: {clash_own}; frak w elsewhere in part2: {clash_oth}")
check("I3 symbol: the myopia weight is frak w; no vartheta (theory_ext's altruism) in the regimes files, and frak w "
      "appears in no other Part II file except the acquirer section, which uses the regimes' weight",
      not clash_own and not clash_oth)

# ----------------------------------------------------------------------------------------------
with open(os.path.join(ROOT, "part2", "tables", "regimes_macros.tex"), "w", encoding="utf-8") as _fh:
    _fh.write("% Generated by code/verify_part2_regimes.py; do not edit. XBOUNDS placeholders: " + ", ".join(f"{x:g}" for x in XBOUNDS) + ".\n")
    for _k, _v in MACR.items():
        _fh.write(f"\\providecommand{{\\{_k}}}{{{_v}}}\n")
_rtex = open(os.path.join(ROOT, "part2", "theory_regimes.tex"), encoding="utf-8").read()
_rused = set(re.findall(r"\\(reg[A-Z][A-Za-z]*)", _rtex))
check("M1 every \\reg... macro used in theory_regimes.tex is generated by this script, and the section inputs the file",
      _rused <= set(MACR) and "part2/tables/regimes_macros.tex" in _rtex, f"undefined: {sorted(_rused - set(MACR))}")
n_fail = sum(1 for _, ok in RESULTS if not ok)
print("\n" + "=" * 78)
print(f"SUMMARY: {len(RESULTS) - n_fail}/{len(RESULTS)} checks passed" + ("" if n_fail == 0 else f"; {n_fail} FAILED")
      + (f"; {len(SKIPPED)} skipped (missing dependency: {', '.join(SKIPPED)})" if SKIPPED else ""))
print("=" * 78)
sys.exit(0 if n_fail == 0 else 1)
