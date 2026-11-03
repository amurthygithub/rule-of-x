#!/usr/bin/env python3
"""
verify_part2_ext.py

Symbolic (sympy) and numerical (numpy/scipy) checks of every closed form, threshold and
worked example in
  part2/theory_ext.tex   (Section "Constraints, Dynamics and Organization", label sec:ext)
  part2/proofs_ext.tex   (Appendix "Proofs for Section sec:ext", label app:proofs-ext)
Paper 2, "The Economics of AI Transformation" (formerly Part II of "The Efficient Frontier of Growth and Profitability").

Run:  python3 code/verify_part2_ext.py      (well under a minute)
Exit code 0 iff every check passes. Check names cite the LaTeX labels of the results.
Numbers printed with "->" are the ones quoted in theory_ext.tex; the script asserts them.

Notation (see notes/theory_ext_notes.md, Sections 2 and 4). Mapping from script names to the paper:
  xi -> xi_j (review share), ximin -> xi^min(c), alt -> vartheta (altruism, $ per own hour retained),
  success probabilities p, pi0 -> varpi_p, varpi^0_p (pi is the inference price only in the paper),
  betaU -> t/t^U - 1, spend weights x_j -> E_j, load ratio x -> varkappa, W (team) -> mathcal W,
  dual-running cost d1 n + d2 n^2 -> C^dr(n) = c^dr_1 n + c^dr_2 n^2, per-process savings s -> W_p.
  modes Z in {H, O, A, U, N} (x in the paper);  AI modes {A, U, N};  non-AI modes {H, O}
  effective unit cost  ct_Z = what*h_Z + c_ext + (1+tau_A)(c_mach + Ups*c_K) + omega/(1-tau) + C_cust
  what = w0 (1 + tau_L) - vartheta/(1 - tau),   Ups = (1 - psi tau)/(1 - tau)
  mode A: what*h_A + c_ext = c^Q_j of prop:tasks-review evaluated at the wage what (review share re-optimized),
          with h_A = xi* t^R and c_ext = e L [1 - xi*(1 + ln(1/xi*))]
  B_j = min_{non-AI} ct - min_{AI} ct    (net automation advantage per unit)
"""
import itertools
import math
import sys

import numpy as np
import sympy as sp
from scipy import integrate, optimize
from scipy.stats import norm

RNG = np.random.default_rng(20261029)
# XBOUNDS: placeholder values of the firm's decision weight on growth X. The author withdrew the 7-to-13 estimate
# (revision plan, decision D-1); the examples are evaluated at these placeholders until the replacement bounds are in.
# To swap in the final bounds, edit this tuple, rerun, and check the "% XBOUNDS" sentences of theory_ext.tex.
XBOUNDS = (2.5, 5.0, 9.0)
MAC = {}      # macros written to part2/tables/ext_macros.tex (read by theory_ext.tex)
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ::  {detail}" if detail else ""))


def header(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def close(a, b, tol=1e-9, rel=True):
    return abs(a - b) <= tol * (1 + (abs(b) if rel else 0))


def zero(e):
    return sp.simplify(e) == 0


# ==============================================================================================
# Activity model used throughout Section 5 of the spec (ext.1)
# ==============================================================================================
def crf(r, T):
    """capital recovery factor a(r,T) = r / (1 - e^{-rT});  -> 1/T as r -> 0"""
    return r / (1 - math.exp(-r * T)) if r > 0 else 1.0 / T


BASE = dict(tau_L=0.43, tau=0.21, psi=1.0, tau_A=0.0,
            ximin={0: 0.0, 1: 0.0, 2: 0.10}, alt=0.0, delta_mult=1.0, pi_mult=1.0,
            F_mult=1.0, iota_mult=1.0, omega_scale=0.0, r=0.10, Xw=9.0, kfirm=0.0,
            exclude_sensitive=False, disp_tax=0.0)
# Current law (coordinator decision, 29 Oct: rebase): BASE psi = 1, domestic software development deducted when paid or
# incurred (26 U.S.C. 174A, taxable years beginning after 31 Dec 2024). Foreign research is amortized over 15 years from
# the midpoint of the taxable year (26 U.S.C. 174(a)), psi_15 = 0.532 at r = 0.10 (midpoint convention,
# verify_part2_accounting.py check 3b); the tornado's psi row spans the foreign share from 1 to 0 (psi_15 to 1).
# PSI_OLD = 0.787 (five-year straight-line, the 2022-2024 rule) is kept only to report the earlier results.
PSI_OLD = (1 - math.exp(-0.5)) / 0.5


def psi_mid(T, r):
    """PV per dollar of deductions ratably over T years from the midpoint of tax year 1 (statutory convention)."""
    return (1 + (1 + r) ** -T) / (2 * T) + (1 - (1 + r) ** -(T - 1)) / (r * T)


PSI15 = psi_mid(15, 0.10)
P_SUP = dict(BASE); P_SUP["psi"] = 1.0       # support example: domestic development, deducted when incurred


def Xhat(P):
    return (P["Xw"] - (1 - P["psi"] * P["tau"]) * P["kfirm"]) / (1 - P["tau"])


def loss_frac(xi):
    """share of the unreviewed expected loss e L that remains when the highest-stakes share xi is reviewed
    (stakes z ~ Exp(1)):  1 - xi (1 + ln(1/xi));  equals 1 at xi = 0 and 0 at xi = 1"""
    return 1.0 if xi <= 0 else 1.0 - xi * (1.0 + math.log(1.0 / xi))


def quality_cost(xi, wh, tR, e, L):
    """core prop:tasks-review(a): c^Q(xi) = w t^R xi + e L [1 - xi(1 + ln(1/xi))], here at the wage wh"""
    return wh * tR * xi + e * L * loss_frac(xi)


def review(wh, tR, e, L, epsbar, ximin):
    """core eq:tasks-xi: xi* = max{exp(-w t^R/(e L)), 1 - epsbar/e, xi_min} (capped at 1), and c^Q(xi*)"""
    eL = e * L
    xiE = math.exp(-wh * tR / eL) if eL > 0 and wh > 0 else (1.0 if eL > 0 else 0.0)
    xiR = max(0.0, 1.0 - epsbar / e) if e > 0 else 0.0
    xi = min(1.0, max(xiE, xiR, ximin))
    return xi, quality_cost(xi, wh, tR, e, L)


def mode_costs(a, P, machine_free=False):
    """Effective unit costs ct_Z (pre-tax-equivalent dollars per unit) for the permitted, feasible modes.
    Returns dict Z -> (cost, own_hours, payroll_base, c_mach, c_K)."""
    tau, tauL, tauA = P["tau"], P["tau_L"], P["tau_A"]
    ups = (1 - P["psi"] * tau) / (1 - tau)
    wh = a["w0"] * (1 + tauL) - P["alt"] / (1 - tau)          # effective own-labour cost per hour
    whL = a["wL0"] * (1 + tauL) - P["alt"] / (1 - tau)
    t = a["t"]
    out = {}
    disp = P["disp_tax"]

    def add(Z, lab_hours_w, lab_hours_L, ext, mach, K, omega, cust):
        h = lab_hours_w + lab_hours_L
        pay = a["w0"] * lab_hours_w + a["wL0"] * lab_hours_L
        if machine_free:
            mach, K = 0.0, 0.0
        c = (wh * lab_hours_w + whL * lab_hours_L + ext + (1 + tauA) * (mach + ups * K)
             + omega / (1 - tau) + cust + disp * (t - h))
        out[Z] = (c, h, pay, mach, K)

    add("H", t, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    if a["O"]:
        add("O", a["kO"] * t, 0.0, a["pO"] + a["zO"], 0.0, 0.0, 0.0, 0.0)
    cls = a["cls"]
    sens = a["sensitive"]
    excl = P["exclude_sensitive"] and sens
    cust_A = Xhat(P) * a["cust"] * P["delta_mult"]
    omA = P["omega_scale"] * a["cH0"] if sens else 0.0
    if a["Afeas"] and cls != 3 and not excl:
        # quality cost of prop:tasks-review at the effective wage; a displacement tax lowers the effective cost
        # of a retained review hour by disp, so the share is chosen at wh - disp (exact equivalence, A11)
        e_now = min(1.0, a["e"] * P["iota_mult"])
        xi, _ = review(wh - disp, a["tR"], e_now, a["L"], a["epsbar"], P["ximin"].get(cls, 0.0))
        K = a["FA"] * P["F_mult"] * crf(P["r"], a["TA"]) / a["v"]
        add("A", xi * a["tR"], a["lic"] * a["tL"], e_now * a["L"] * loss_frac(xi), a["pin"] * P["pi_mult"], K,
            omA, cust_A)
    if a["Ufeas"] and cls != 3 and not excl:
        add("U", t / (1 + a["betaU"]), 0.0, 0.0, a["pinU"] * P["pi_mult"], 0.0, 0.3 * omA, 0.2 * cust_A)
    if a["N"] and not a["lic"] and not excl:
        K = a["FN"] * P["F_mult"] * crf(P["r"], a["TA"]) / a["v"]
        add("N", 0.0, 0.0, a["lossN"], 0.0, K, omA, cust_A)
    return out


AI = ("A", "U", "N")
NONAI = ("H", "O")


def advantage(a, P, machine_free=False):
    mc = mode_costs(a, P, machine_free)
    c0 = min(mc[Z][0] for Z in NONAI if Z in mc)
    ai = [mc[Z][0] for Z in AI if Z in mc]
    if not ai:
        return -math.inf, mc
    return c0 - min(ai), mc


def layers(a, P):
    """membership of the four nested sets for activity a"""
    tech = a["Afeas"] or a["Ufeas"] or a["N"]
    perm = (a["Afeas"] or a["Ufeas"]) and a["cls"] != 3 or (a["N"] and not a["lic"])
    if P["exclude_sensitive"] and a["sensitive"]:
        perm = False
    perm = perm and tech
    Bpre, _ = advantage(a, P, machine_free=True)
    Beco, _ = advantage(a, P)
    pre = perm and Bpre > 0
    eco = perm and Beco > 0
    return tech, perm, pre, eco


def gen_population(n, rng):
    acts = []
    for _ in range(n):
        w0 = rng.uniform(25, 85)
        t = float(np.clip(math.exp(rng.normal(math.log(0.4), 0.8)), 0.02, 8))
        v = math.exp(rng.normal(math.log(30000), 1.2))
        cH0 = w0 * 1.43 * t
        a = dict(w0=w0, t=t, v=v, cH0=cH0, wL0=1.6 * w0)
        a["O"] = rng.random() < 0.55
        a["pO"] = rng.uniform(0.35, 0.95) * cH0
        a["kO"] = rng.uniform(0.05, 0.20)
        a["zO"] = rng.uniform(0, 0.08) * cH0
        a["Afeas"] = rng.random() < 0.65
        a["pin"] = rng.uniform(0.005, 0.12) * cH0
        # review and errors (prop:tasks-review): review hours, raw error rate, loss per error, reliability target
        a["tR"] = rng.uniform(0.3, 1.0) * t
        a["e"] = rng.uniform(0.01, 0.40)
        a["L"] = math.exp(rng.uniform(math.log(0.3), math.log(15.0))) * cH0
        a["epsbar"] = rng.uniform(0.005, 0.06)
        a["FA"] = math.exp(rng.uniform(math.log(5e4), math.log(3e6)))
        a["TA"] = 3.0
        a["Ufeas"] = rng.random() < 0.80
        a["betaU"] = rng.uniform(0.1, 0.8)
        a["pinU"] = rng.uniform(0.002, 0.04) * cH0
        a["N"] = rng.random() < 0.08
        a["lossN"] = rng.uniform(0.2, 1.0) * cH0
        a["FN"] = rng.uniform(2e4, 5e5)
        u = rng.random()
        a["cls"] = 0 if u < 0.60 else (1 if u < 0.80 else (2 if u < 0.95 else 3))
        a["lic"] = rng.random() < 0.08
        a["tL"] = rng.uniform(0.05, 0.25) * t
        a["cf"] = rng.random() < 0.30
        a["cust"] = (rng.uniform(0, 0.4) * cH0 / (9.0 / 0.79)) if a["cf"] else 0.0
        a["sensitive"] = rng.random() < 0.05
        acts.append(a)
    return acts


def shares(acts, P):
    x = np.array([a["v"] * a["cH0"] for a in acts])
    flags = np.array([layers(a, P) for a in acts])
    S = [float(x[flags[:, i]].sum() / x.sum()) for i in range(4)]
    B = np.array([advantage(a, P)[0] for a in acts])
    V = float(sum(a["v"] * max(b, 0.0) for a, b in zip(acts, B)) / x.sum())
    return S, V


# ==============================================================================================
header("A. Permissibility and the available universe (sec:ext-universe)")
# ==============================================================================================
tau, psi, tauA, tauL, w0, vth, h, cext, cmach, cK, om, Cc = sp.symbols(
    "tau psi tau_A tau_L w_0 vartheta h c_ext c_mach c_K omega C_c", positive=True)
J_after = ((1 - tau) * (w0 * (1 + tauL) * h + cext + (1 + tauA) * cmach) + (1 - psi * tau) * (1 + tauA) * cK
           + om - vth * h + (1 - tau) * Cc)
Ups = (1 - psi * tau) / (1 - tau)
ct = (w0 * (1 + tauL) - vth / (1 - tau)) * h + cext + (1 + tauA) * (cmach + Ups * cK) + om / (1 - tau) + Cc
check("A1 def:ext-effcost  after-tax objective / (1 - tau) equals the effective unit cost ct_Z", zero(J_after / (1 - tau) - ct))
check("A2 Ups = (1-psi tau)/(1-tau) >= 1 with equality iff psi = 1 or tau = 0;  dUps/dtau = (1-psi)/(1-tau)^2",
      zero(sp.diff(Ups, tau) - (1 - psi) / (1 - tau) ** 2) and zero((Ups - 1) - tau * (1 - psi) / (1 - tau)))
rr, TR, tt = sp.symbols("r T_R t", positive=True)
psi_SL = sp.integrate(sp.exp(-rr * tt) / TR, (tt, 0, TR))
check("A3 straight-line deductions over T_R years: psi = (1 - e^{-r T_R})/(r T_R)",
      zero(psi_SL - (1 - sp.exp(-rr * TR)) / (rr * TR)))
psi5 = (1 - math.exp(-0.5)) / 0.5
ups5 = (1 - psi5 * 0.21) / 0.79
ups15 = (1 - PSI15 * 0.21) / 0.79
sfor = 0.3
psi_mix = (1 - sfor) + sfor * PSI15
print(f"     -> current law: domestic psi = 1, Ups = 1; foreign psi_15 = {PSI15:.3f}, Ups = {ups15:.4f} (penalty "
      f"{100 * (ups15 - 1):.1f}%); 2022-2024 five-year rule psi = {psi5:.3f}, Ups = {ups5:.4f} ({100 * (ups5 - 1):.1f}%); "
      f"30% foreign: psi = {psi_mix:.3f}")
check("A3b current law: domestic psi = 1 gives Ups = 1; foreign psi_15 = 0.532 (midpoint convention) gives Ups = 1.124 "
      "(12.4% penalty at tau = 0.21); the 2022-2024 five-year rule gave psi = 0.787 and 5.7%; "
      "psi = (1 - s_for) + s_for psi_15 is linear in the foreign share",
      abs((1 - 1.0 * 0.21) / 0.79 - 1) < 1e-15 and abs(PSI15 - 0.532) < 5e-4 and abs(ups15 - 1.1243) < 5e-4
      and abs(psi5 - 0.787) < 5e-4 and abs(ups5 - 1.0566) < 5e-4 and abs(psi_mix - (0.7 + 0.3 * PSI15)) < 1e-15)
aT = sp.symbols("a_T", positive=True)
crf_s = rr / (1 - sp.exp(-rr * TR))
check("A4 capital recovery factor: PV of a(r,T) over T is 1, and a -> 1/T as r -> 0",
      zero(crf_s * (1 - sp.exp(-rr * TR)) / rr - 1) and zero(sp.limit(crf_s, rr, 0) - 1 / TR))

# derivatives of B = ct_{Z0} - ct_{Z1} with fixed minimizers (prop:ext-statics, table)
h0, h1, k0, k1, m1, om1, om0, Cc1, Cc0, e0, e1, psimin, tA_ = sp.symbols(
    "h0 h1 k0 k1 m1 om1 om0 Cc1 Cc0 e0 e1 psimin t_A", positive=True)


def ctZ(hh, ee, mm, kk, oo, cc):
    return (w0 * (1 + tauL) - vth / (1 - tau)) * hh + ee + (1 + tauA) * (mm + Ups * kk) + oo / (1 - tau) + cc


B = ctZ(h0, e0, 0, k0, om0, Cc0) - ctZ(h1, e1, m1, k1, om1, Cc1)
ok = zero(sp.diff(B, tauL) - w0 * (h0 - h1))
ok &= zero(sp.diff(B, vth) + (h0 - h1) / (1 - tau))
ok &= zero(sp.diff(B, tauA) + (m1 + Ups * k1) - Ups * k0)
ok &= zero(sp.diff(B, psi) - (1 + tauA) * tau * (k1 - k0) / (1 - tau))
ok &= zero(sp.diff(B, tau) + ((1 + tauA) * (1 - psi) * (k1 - k0) + (om1 - om0) + vth * (h0 - h1)) / (1 - tau) ** 2)
ok &= zero(sp.diff(B, om1) + 1 / (1 - tau))
check("A5 prop:ext-statics derivative formulas for tau_L, vartheta, tau_A, psi, tau, omega (symbolic)", ok)
# mode A uses the core's quality cost: by the envelope theorem its wage derivative is the review hours xi* t^R,
# so the derivative formulas above apply with h_A = xi* t^R although the share is re-optimized (prop:ext-statics(b))
okenv = True
for _ in range(400):
    whv, tRv, ev, Lv, ebv = RNG.uniform(10, 120), RNG.uniform(0.02, 1.0), RNG.uniform(0.01, 0.6), \
        RNG.uniform(1, 400), RNG.uniform(0.005, 0.2)
    xmv = RNG.choice([0.0, RNG.uniform(0, 0.8)])
    xi0, cq0 = review(whv, tRv, ev, Lv, ebv, xmv)
    hstep = 1e-6 * whv
    dnum = (review(whv + hstep, tRv, ev, Lv, ebv, xmv)[1] - review(whv - hstep, tRv, ev, Lv, ebv, xmv)[1]) / (2 * hstep)
    okenv &= abs(dnum - xi0 * tRv) < 1e-6 * (1 + tRv)
    # c^Q at the optimum never exceeds reviewing nothing (e L) or everything (w t^R) unless a constraint forces it
    if xi0 == math.exp(-whv * tRv / (ev * Lv)):
        okenv &= cq0 <= min(ev * Lv, whv * tRv) + 1e-12
check("A5b prop:ext-statics(b): with mode A at the core's quality cost, d c^Q/d what = xi* t^R (envelope; 400 draws "
      "across the economic, reliability and floor regimes)", okenv)
# oversight floor (prop:ext-statics(a), prop:ext-breaks(d)): where the floor binds, d c^Q/d xi_min = w t^R - e L ln(1/xi_min),
# which lies in [0, w t^R]: positive because the floor is above the economic share, below w t^R because review catches errors
xs_, wts, eLs = sp.symbols("xi w_tR e_L", positive=True)
cQs = wts * xs_ + eLs * (1 - xs_ * (1 + sp.log(1 / xs_)))
okf = zero(sp.diff(cQs, xs_) - (wts - eLs * sp.log(1 / xs_))) and zero(sp.diff(cQs, xs_, 2) - eLs / xs_)
for _ in range(300):
    whv, tRv, ev, Lv = RNG.uniform(10, 120), RNG.uniform(0.02, 1.0), RNG.uniform(0.01, 0.6), RNG.uniform(1, 400)
    xiE = math.exp(-whv * tRv / (ev * Lv))
    xm = RNG.uniform(xiE + 1e-4, 1.0 - 1e-4)
    slope = (review(whv, tRv, ev, Lv, 1.0, xm + 1e-7)[1] - review(whv, tRv, ev, Lv, 1.0, xm - 1e-7)[1]) / 2e-7
    okf &= abs(slope - (whv * tRv - ev * Lv * math.log(1 / xm))) < 1e-5 * whv * tRv and -1e-9 <= slope <= whv * tRv + 1e-9
check("A6 oversight floor: d c^Q/d xi_min = w t^R - e L ln(1/xi_min) in [0, w t^R] where the floor binds; c^Q convex", okf)

# monotone comparative statics on random populations
pop = gen_population(500, RNG)


def S_eco(P):
    return shares(pop, P)[0][3]


def scan(key, vals, setter=None):
    out = []
    for vv in vals:
        P = dict(BASE)
        P["ximin"] = dict(BASE["ximin"])
        if setter:
            setter(P, vv)
        else:
            P[key] = vv
        out.append(S_eco(P))
    return out


mono = {}
mono["tau_A (down)"] = scan("tau_A", [0, 0.1, 0.3, 0.6, 1.0])
mono["pi (down)"] = scan("pi_mult", [0.1, 0.5, 1, 2, 4])
mono["F_A (down)"] = scan("F_mult", [0.3, 1, 2, 5])
mono["xi_min (down)"] = scan(None, [0.0, 0.1, 0.3, 0.6, 1.0], lambda P, v: P["ximin"].__setitem__(2, v))
mono["omega (down)"] = scan("omega_scale", [0, 0.2, 0.5, 1.0])
mono["delta_H (down)"] = scan("delta_mult", [0, 1, 2, 4])
mono["iota: worse readiness (down)"] = scan("iota_mult", [0.5, 0.8, 1.0, 1.3, 1.6])
mono["psi deductibility (up)"] = scan("psi", [0.0, 0.4, 0.787, 1.0])
okm = True
for k_, vals in mono.items():
    seq = np.array(vals)
    if "(up)" in k_:
        okm &= bool(np.all(np.diff(seq) >= -1e-12))
    else:
        okm &= bool(np.all(np.diff(seq) <= 1e-12))
check("A7 prop:ext-statics(a): Sigma_eco monotone in tau_A, pi, F_A, xi_min, omega, delta^G, readiness, psi "
      "(500 synthetic activities)", okm, "; ".join(f"{k_}: {vals[0]:.3f}->{vals[-1]:.3f}" for k_, vals in mono.items()))
# exclusions: set inclusion
Pex = dict(BASE); Pex["exclude_sensitive"] = True
fl0 = [layers(a, BASE)[3] for a in pop]
fl1 = [layers(a, Pex)[3] for a in pop]
check("A8 prop:ext-statics(a): adding hard exclusions shrinks the available universe (set inclusion)",
      all((not f1) or f0 for f0, f1 in zip(fl0, fl1)) and sum(fl1) <= sum(fl0))
# profit tax: monotone when omega >= 0, vartheta = 0 and k_nonAI = 0
mono_tau = []
for tv in [0.0, 0.1, 0.21, 0.3, 0.45]:
    Pq = dict(BASE); Pq["ximin"] = dict(BASE["ximin"]); Pq["psi"] = PSI15; Pq["tau"] = tv
    mono_tau.append(S_eco(Pq))
check("A9 prop:ext-statics(b): Sigma_eco nonincreasing in tau when psi < 1 (foreign build, psi_15; no non-pecuniary "
      "terms)",
      bool(np.all(np.diff(mono_tau) <= 1e-12)), f"{mono_tau}")
Pfull = dict(BASE); Pfull["psi"] = 1.0
vals_tau_full = []
for tv in [0.0, 0.1, 0.21, 0.3]:
    Pq = dict(Pfull); Pq["tau"] = tv; Pq["delta_mult"] = 0.0
    vals_tau_full.append(S_eco(Pq))
check("A9b with full expensing (psi = 1) and no customer penalty, tau is neutral",
      max(vals_tau_full) - min(vals_tau_full) < 1e-12, f"{vals_tau_full}")
# payroll tax: local sign = sign(h_{Z0} - h_{Z1}); counterexample with outsourcing comparator
ex = dict(w0=40.0, t=0.25, v=1e6, cH0=40 * 1.43 * 0.25, wL0=64.0, O=True, pO=7.0, kO=0.10, zO=0.60,
          Afeas=True, pin=0.40, tR=0.25, e=0.10, L=17.69, epsbar=0.085, FA=1.5e6, TA=3.0, Ufeas=True, betaU=0.15, pinU=0.10,
          N=False, lossN=0, FN=0, cls=0, lic=False, tL=0, cf=False, cust=0.0, sensitive=False)
Bex, mcex = advantage(ex, P_SUP)
e = 1e-6
Pp = dict(P_SUP); Pp["tau_L"] += e
dB = (advantage(ex, Pp)[0] - Bex) / e
print(f"     support example: costs " + ", ".join(f"{Z}={mcex[Z][0]:.2f}" for Z in mcex) + f"; B = {Bex:.2f}")
check("A10 prop:ext-statics(b): with outsourcing as the comparator, dB/dtau_L = w0 (h_O - h_A) < 0 "
      "(payroll tax shrinks the AI advantage)", abs(dB - 40 * (0.025 - 0.0375)) < 1e-5 and dB < 0, f"dB/dtau_L={dB:.4f}")
exH = dict(ex); exH["O"] = False
BexH = advantage(exH, P_SUP)[0]
dBH = (advantage(exH, Pp)[0] - BexH) / e
check("A10b with in-house as the comparator, dB/dtau_L = w0 (t - h_A) = 8.5 > 0", abs(dBH - 40 * (0.25 - 0.0375)) < 1e-5)

# equivalence: payroll tax, altruism and a per-hour displacement tax act through what (prop:ext-statics(c))
okq = True
for a in pop[:200]:
    for TD in [3.0, 11.0]:
        P1 = dict(BASE); P1["disp_tax"] = TD
        P2 = dict(BASE); P2["alt"] = TD * (1 - BASE["tau"])
        b1, b2 = advantage(a, P1)[0], advantage(a, P2)[0]
        if math.isfinite(b1) or math.isfinite(b2):
            okq &= abs(b1 - b2) < 1e-9 * (1 + abs(b1))
    # altruism vartheta equivalent to payroll-tax cut d tau_L = vartheta/((1-tau) w0) when wL0 = w0 (single wage)
check("A11 prop:ext-statics(c): a deductible displacement tax T_D per displaced hour and altruism "
      "vartheta = (1 - tau) T_D give identical advantages B_j (200 activities)", okq)
aa = dict(ex); aa["wL0"] = aa["w0"]
P1 = dict(BASE); P1["alt"] = 5.0
P2 = dict(BASE); P2["tau_L"] = BASE["tau_L"] - 5.0 / ((1 - BASE["tau"]) * aa["w0"])
check("A11b altruism vartheta equals a payroll-tax cut of vartheta/((1-tau) w0) (single-wage activity)",
      abs(advantage(aa, P1)[0] - advantage(aa, P2)[0]) < 1e-9)

# nesting and the machine-free (preferred) layer
okn, oknm = True, True
for a in pop:
    tech, perm, pre, eco = layers(a, BASE)
    okn &= (not eco or pre) and (not pre or perm) and (not perm or tech)
for mult in [0.0, 0.01, 0.5, 1, 5]:
    Pm = dict(BASE); Pm["pi_mult"] = mult; Pm["F_mult"] = mult if mult > 0 else 0.0
    for a in pop:
        oknm &= layers(a, Pm)[2] == layers(a, BASE)[2]
Sb, Vb = shares(pop, BASE)
P0m = dict(BASE); P0m["pi_mult"] = 0.0; P0m["F_mult"] = 0.0
S0m, _ = shares(pop, P0m)
check("A12 lem:ext-nested: J_eco subset J_pre subset J_per subset J_fea for every activity", okn)
check("A13 lem:ext-nested(b): the preferred layer does not depend on inference or build prices; at zero machine "
      "cost Sigma_eco = Sigma_pre", oknm and abs(S0m[3] - S0m[2]) < 1e-12 and abs(S0m[2] - Sb[2]) < 1e-12)
print(f"     -> baseline waterfall (synthetic): fea {Sb[0]:.3f}, per {Sb[1]:.3f}, pre {Sb[2]:.3f}, eco {Sb[3]:.3f}; "
      f"value {100 * Vb:.1f}% of spend")

# density formula (prop:ext-margin(a)): S(theta) = sum_b P(b) Phi((m + c b + theta b)/s)
bvals = np.array([-1.0, 0.5, 2.0]); pb = np.array([0.2, 0.5, 0.3]); m_, c_, s_ = -0.3, 0.4, 1.1
Sfun = lambda th: float(np.sum(pb * norm.cdf((m_ + c_ * bvals + th * bvals) / s_)))
fd = (Sfun(1e-6) - Sfun(-1e-6)) / 2e-6
f0 = float(np.sum(pb * norm.pdf((m_ + c_ * bvals) / s_) / s_))
Eb = float(np.sum(pb * bvals * norm.pdf((m_ + c_ * bvals) / s_) / s_)) / f0
check("A14 prop:ext-margin(a): dSigma/dtheta = f_B(0) E[b | B = 0] (mixture of normals, exact)", abs(fd - f0 * Eb) < 1e-8,
      f"fd={fd:.6f}, formula={f0 * Eb:.6f}")
# large-population version: kernel estimate of the density formula versus a finite difference
Np = 400000
bb = RNG.choice(bvals, size=Np, p=pb)
B0 = m_ + c_ * bb + s_ * RNG.standard_normal(Np)
hh = 0.02
fdp = (np.mean(B0 + hh * bb > 0) - np.mean(B0 - hh * bb > 0)) / (2 * hh)
kern = np.mean(bb * norm.pdf(B0 / 0.02) / 0.02)
check("A14b same identity on a simulated population of 400,000 activities (Monte Carlo, 3% tolerance)",
      abs(fdp - f0 * Eb) < 0.03 * abs(f0 * Eb) and abs(kern - f0 * Eb) < 0.03 * abs(f0 * Eb),
      f"fd={fdp:.4f}, kernel={kern:.4f}, exact={f0 * Eb:.4f}")


# envelope and convexity of the universe value (prop:ext-margin(b),(c))
def Vval(P):
    return sum(a["v"] * max(advantage(a, P)[0], 0.0) for a in pop)


okv, okc = True, True
for key, base_v, dv in [("tau_A", 0.13, 1e-5), ("pi_mult", 1.3, 1e-5), ("F_mult", 1.1, 1e-5)]:
    P0 = dict(BASE); P0[key] = base_v
    Pp_ = dict(P0); Pp_[key] = base_v + dv
    Pm_ = dict(P0); Pm_[key] = base_v - dv
    fdv = (Vval(Pp_) - Vval(Pm_)) / (2 * dv)
    env = 0.0
    for a in pop:
        b0 = advantage(a, P0)[0]
        if b0 > 0:
            env += a["v"] * (advantage(a, Pp_)[0] - advantage(a, Pm_)[0]) / (2 * dv)
    okv &= abs(fdv - env) < 1e-6 * (1 + abs(env))
    grid = [base_v * x for x in (0.5, 0.75, 1.0, 1.25, 1.5)]
    vv = [Vval(dict(P0, **{key: g})) for g in grid]
    okc &= all(vv[i - 1] + vv[i + 1] - 2 * vv[i] >= -1e-6 * abs(vv[i]) for i in range(1, 4))
check("A15 prop:ext-margin(b): dV/dtheta = sum over inframarginal activities only (no boundary term)", okv)
check("A16 prop:ext-margin(c): V is convex in parameters that raise only AI-mode costs (tau_A, pi, F_A)", okc)

# customer preference and the marginal q (prop:ext-customer)
r_, G_, k_, al_ = 0.10, 0.04, 0.0, 0.30
Ca = (1 - al_) * al_ ** (al_ / (1 - al_))


def v0_root(m0, Gi, lam):
    """smallest positive root of eq:gordon (Part I) with G replaced by G_i"""
    f = lambda v: (r_ - Gi) * v - (m0 - k_ * Gi + Ca * (lam * max(v - k_, 0)) ** (1 / (1 - al_)))
    grid_v = np.linspace(1e-6, 100, 20001)
    fv = np.array([f(x) for x in grid_v])
    idx = np.where(np.sign(fv[:-1]) != np.sign(fv[1:]))[0]
    if len(idx) == 0:
        return math.inf
    i0 = idx[0]
    return optimize.brentq(f, grid_v[i0], grid_v[i0 + 1], xtol=1e-14)


lam_ = optimize.brentq(lambda L: v0_root(0.35, G_, L) - 10.0, 0.065, 0.075, xtol=1e-14)
v0b = v0_root(0.35, G_, lam_)
D0 = lam_ ** (1 / (1 - al_)) * (al_ * (v0b - k_)) ** (al_ / (1 - al_))
g0 = G_ + D0
eps = 1e-6
dv_m = (v0_root(0.35 + eps, G_, lam_) - v0b) / eps
dv_G = (v0_root(0.35, G_ - eps, lam_) - v0b) / eps
dv_l = (v0_root(0.35, G_, lam_ * (1 - eps)) - v0b) / eps
check("A17 prop:ext-customer(b): small-share limit dv0 = [dm0 - (v0-k)(dG + Delta dlam/lam)]/(r - g)",
      abs(dv_m - 1 / (r_ - g0)) < 1e-4 * dv_m and abs(-dv_G - (v0b - k_) / (r_ - g0)) < 1e-4 * abs(dv_G)
      and abs(-dv_l - (v0b - k_) * D0 / (r_ - g0)) < 1e-3 * abs(dv_l),
      f"lambda={lam_:.4f}, v0={v0b:.3f}, g={g0:.4f}; loss ratio retention/margin {-dv_G / dv_m:.4f} vs v0-k={v0b - k_:.4f}")
S_rev, vol = 500e6, 1e6
Xh_of = lambda X: (X - (1 - P_SUP["psi"] * 0.21) * 0.0) / 0.79   # X_hat with k = 0 (psi does not enter)
dstar_x = {X: Bex / (Xh_of(X) * S_rev / vol) for X in XBOUNDS}
print(f"     -> support: B = {Bex:.2f}/ticket; breakeven retention loss at the XBOUNDS placeholders: "
      + ", ".join(f"X = {X:g}: {1e4 * d:.2f} bp" for X, d in dstar_x.items()))
check("A18 example (domestic build, psi = 1; XBOUNDS placeholders 2.5, 5, 9): breakeven retention loss 31, 15.5 and 8.6 "
      "basis points, inversely proportional to X; positive at every weight, so the sign of the decision does not flip",
      XBOUNDS == (2.5, 5.0, 9.0) and abs(1e4 * dstar_x[2.5] - 31.0) < 0.05 and abs(1e4 * dstar_x[5.0] - 15.5) < 0.05
      and abs(1e4 * dstar_x[9.0] - 8.61) < 0.01 and all(d > 0 for d in dstar_x.values())
      and abs(dstar_x[2.5] * 2.5 - dstar_x[9.0] * 9.0) < 1e-12, f"{[round(1e4 * d, 2) for d in dstar_x.values()]}")
_bp = lambda d: f"{1e4 * d:.1f}".rstrip("0").rstrip(".")
MAC.update(extXbOne=f"{XBOUNDS[0]:g}", extXbTwo=f"{XBOUNDS[1]:g}", extXbThree=f"{XBOUNDS[2]:g}",
           extXbRetOne=_bp(dstar_x[XBOUNDS[0]]), extXbRetTwo=_bp(dstar_x[XBOUNDS[1]]), extXbRetThree=_bp(dstar_x[XBOUNDS[2]]))

# support example numbers (Section ext.1 example)
cH, cO, cA, cU = (mcex[Z][0] for Z in ("H", "O", "A", "U"))
print(f"     -> c_H={cH:.2f}, c_O={cO:.2f}, c_A={cA:.2f}, c_U={cU:.2f}, B={Bex:.2f}")
xi_ex, cQ_ex = review(57.2, 0.25, 0.10, 17.69, 0.085, 0.0)   # epsbar = 0.085: q-bar = 0.915
print(f"     -> support review: xi* = {xi_ex:.3f} (reliability binds; economic share "
      f"{math.exp(-57.2 * 0.25 / (0.10 * 17.69)):.4f}), error cost {0.10 * 17.69 * loss_frac(xi_ex):.3f}, c^Q = {cQ_ex:.3f}")
check("A19 support example (domestic build, psi = 1): c_H = 14.30, c_O = 9.03, c_A = 4.12, c_U = 12.53 "
      "(t^U = t/1.15), B = 4.91; review share 0.15 set by the reliability target, error cost 1.00, c^Q = 3.15",
      abs(cH - 14.30) < 0.005 and abs(cO - 9.03) < 0.005 and abs(cA - 4.12) < 0.005 and abs(cU - 12.53) < 0.006
      and abs(Bex - 4.91) < 0.005 and abs(xi_ex - 0.15) < 1e-12 and abs(0.10 * 17.69 * loss_frac(xi_ex) - 1.00) < 0.005
      and abs(cQ_ex - 3.15) < 0.005)
# floor breakpoint (prop:ext-breaks(d)): the bound xi* + B/(what t^R) and the exact root, at which c^Q rises by B
xmin_bound = xi_ex + Bex / cH
xmin_exact = optimize.brentq(lambda x: quality_cost(x, 57.2, 0.25, 0.10, 17.69) - cQ_ex - Bex, xi_ex, 1.0, xtol=1e-12)
Pf = dict(P_SUP); Pf["ximin"] = {0: 0.5, 1: 0.0, 2: 0.10}
Pf2 = dict(P_SUP); Pf2["ximin"] = {0: 0.56, 1: 0.0, 2: 0.10}
print(f"     -> oversight-floor breakpoint: exact xi_min* = {xmin_exact:.3f} >= bound {xmin_bound:.3f}; "
      f"B at a floor of 0.5: {advantage(ex, Pf)[0]:.2f}; at 0.56: {advantage(ex, Pf2)[0]:.2f}")
check("A20 oversight-floor breakpoint: exact xi_min* = 0.55 exceeds the bound xi* + B/(what t^R) = 0.49, because "
      "forced review also catches errors; a floor of 0.5 keeps the activity automated, 0.56 sends it to the vendor",
      abs(xmin_bound - 0.493) < 5e-4 and abs(xmin_exact - 0.548) < 0.0005 and xmin_exact > xmin_bound
      and advantage(ex, Pf)[0] > 0 and advantage(ex, Pf2)[0] < 0)
Palt = dict(P_SUP); Palt["alt"] = 10.0
Balt = advantage(ex, Palt)[0]
BaltH = advantage(exH, Palt)[0]
print(f"     -> altruism vartheta=$10/h: B (vs outsourcing) {Bex:.2f} -> {Balt:.2f}; B (vs in-house) {BexH:.2f} -> {BaltH:.2f}")
check("A21 altruism example: $10 an hour raises B against outsourcing (4.91 -> 5.06) and lowers it against in-house "
      "work (10.18 -> 7.49)", Balt > Bex and BaltH < BexH and round(Balt, 2) == 5.06 and round(BexH, 2) == 10.18
      and round(BaltH, 2) == 7.49, f"{Bex:.4f}, {Balt:.4f}, {BexH:.4f}, {BaltH:.4f}")

# activity-level accountability floor and R_max (cor:ext-floor)
tau_c, cc_, f_, amin0 = 0.18, 0.06, 0.025, 0.03      # c_c: Part I central at 2025 prices since the params commit of 29 Oct 2026
Rmax = lambda amin, chmin: (1 - tau_c) * (1 - chmin - cc_ - f_ - amin) + 0.15
wt_share = 0.08    # sum over high-risk G&A activities of v w t / S
dR = (Rmax(amin0 + wt_share * 0.1, 0) - Rmax(amin0, 0)) / 0.1
check("A22 cor:ext-floor: dR_max/dxi_min(c) = -(1 - tau) * sum_{j in class c} v_j w_j t^R_j / S",
      abs(dR + (1 - tau_c) * wt_share) < 1e-12)


# Shapley decomposition (prop:ext-shapley)
def shapley(f, K):
    phis = []
    for k in range(K):
        tot = 0.0
        others = [i for i in range(K) if i != k]
        for rsz in range(K):
            for T in itertools.combinations(others, rsz):
                wgt = math.factorial(len(T)) * math.factorial(K - len(T) - 1) / math.factorial(K)
                tot += wgt * (f(set(T) | {k}) - f(set(T)))
        phis.append(tot)
    return phis


groups = [("taxes", dict(tau_L=0.25, tau=0.30, psi=1.0)), ("regulation", dict(ximin={0: 0, 1: 0.05, 2: 0.6})),
          ("ethics", dict(omega_scale=0.5, exclude_sensitive=True)), ("altruism", dict(alt=10.0)),
          ("customers", dict(delta_mult=2.0)), ("AI prices", dict(pi_mult=0.3, F_mult=0.5))]
cache = {}


def f_scen(T):
    key = tuple(sorted(T))
    if key not in cache:
        P = dict(BASE); P["ximin"] = dict(BASE["ximin"])
        for i in T:
            P.update(groups[i][1])
        cache[key] = S_eco(P)
    return cache[key]


phis = shapley(f_scen, len(groups))
total = f_scen(set(range(len(groups)))) - f_scen(set())
check("A23 prop:ext-shapley(a): Shapley attributions sum exactly to the scenario change (6 groups)",
      abs(sum(phis) - total) < 1e-12, "; ".join(f"{g[0]} {p:+.4f}" for g, p in zip(groups, phis)) + f"; total {total:+.4f}")
addf = lambda T: sum([0.1, -0.2, 0.05, 0.3][i] for i in T)
check("A24 prop:ext-shapley(b): for an additively separable function Shapley = one-at-a-time changes",
      all(abs(p - q) < 1e-12 for p, q in zip(shapley(addf, 4), [0.1, -0.2, 0.05, 0.3])))
oat = [f_scen({k}) - f_scen(set()) for k in range(len(groups))]
check("A25 prop:ext-shapley(c): one-at-a-time changes do not add up when constraints interact (synthetic)",
      abs(sum(oat) - total) > 1e-4, f"sum OAT {sum(oat):+.4f} vs total {total:+.4f}")

# Tornado (def:ext-tornado, tab:ext-tornado)
torn = [("Payroll loading $\\tau_L$", "tau_L", 0.25, 0.55), ("Profit tax $\\tau$", "tau", 0.15, 0.30),
        ("Deductibility $\\psi$", "psi", PSI15, 1.00), ("Automation tax $\\tau_A$", "tau_A", 0.0, 0.5),
        ("Oversight floor, high risk", "ximin2", 0.05, 0.60), ("Altruism $\\vartheta$ (\\$/h)", "alt", 0.0, 15.0),
        ("Ethics penalty (scale)", "omega_scale", 0.0, 0.5), ("Customer penalty (multiple)", "delta_mult", 0.0, 3.0),
        ("Inference price (multiple)", "pi_mult", 0.1, 3.0), ("Build cost (multiple)", "F_mult", 0.5, 2.0),
        ("Readiness: raw error rate (multiple)", "iota_mult", 0.6, 1.4)]
rows = []
for lab, key, lo, hi in torn:
    out = []
    for vv in (lo, hi):
        P = dict(BASE); P["ximin"] = dict(BASE["ximin"])
        if key == "ximin2":
            P["ximin"][2] = vv
        else:
            P[key] = vv
        S_, V_ = shares(pop, P)
        out.append((S_[3], V_))
    rows.append((lab, lo, hi, out[0][0], out[1][0], out[0][1], out[1][1]))
rows.sort(key=lambda z: -abs(z[6] - z[5]))
print("     -> tornado (synthetic population, 500 activities): baseline Sigma_eco = %.3f, value = %.1f%% of spend"
      % (Sb[3], 100 * Vb))
for z in rows:
    print(f"        {z[0]:<40s} [{z[1]:.2f}, {z[2]:.2f}]  Sigma {z[3]:.3f} / {z[4]:.3f}   V {100 * z[5]:.1f} / {100 * z[6]:.1f}")
TORNADO = rows
check("A26 tornado: ranking by value differs from ranking by spend share for at least one pair (share fragile, "
      "value robust)", [z[0] for z in sorted(rows, key=lambda z: -abs(z[4] - z[3]))] != [z[0] for z in rows])

# ==============================================================================================
header("B. Capability and cost dynamics (sec:ext-dynamics)")
# ==============================================================================================
d_, H_, eta, rb = sp.symbols("d H eta rbar", positive=True)
p_succ = 1 / (1 + (d_ / H_) ** (1 / eta))
chi = (rb / (1 - rb)) ** eta
odds = sp.symbols("o", positive=True)          # o = r/(1-r)
p_at = 1 / (1 + sp.powdenest((H_ * odds ** (-eta) / H_) ** (1 / eta), force=True))
check("B1 ass:ext-capability: p(H/chi(r), H) = r with chi(r) = (r/(1-r))^eta (logistic in log length)",
      zero(sp.simplify(p_at - odds / (1 + odds))) and
      all(abs(1 / (1 + ((1 / (rv / (1 - rv)) ** 1.3)) ** (1 / 1.3)) - rv) < 1e-12 for rv in (0.6, 0.8, 0.95, 0.99)))
check("B1b p(H, H) = 1/2, and p -> 1 as H -> infinity for fixed d", zero(p_succ.subs(d_, H_) - sp.Rational(1, 2))
      and sp.limit(1 / (1 + (2 / H_) ** (1 / sp.Rational(7, 6))), H_, sp.oo) == 1)
eta_r = math.log(5) / math.log(4)
Td = 207 / 365.25            # kwa2025measuring v4: 207 days (95% CI 166-240), 2019-2025
Td24 = 143 / 365.25          # models since 2024: 143 days
lag = lambda r1, r2: eta_r * math.log2((r2 / (1 - r2)) / (r1 / (1 - r1)))
L80, L95, L99 = lag(0.5, 0.8), lag(0.5, 0.95), lag(0.5, 0.99)
print(f"     -> eta_r = {eta_r:.3f}; doublings 50->80: {L80:.2f}, ->95: {L95:.2f}, ->99: {L99:.2f}; "
      f"years at T_d=207d: {L80 * Td:.2f}, {L95 * Td:.2f}, {L99 * Td:.2f}; at 143d: {L99 * Td24:.2f}")
check("B2 prop:ext-feasible(b): eta_r = ln5/ln4 = 1.161; reliability lags 2.32, 4.93, 7.70 doublings = 1.32, 2.79, "
      "4.36 years (T_d = 207 days; 99%: 3.01 years at 143 days)", abs(eta_r - 1.161) < 5e-4 and abs(L80 - 2.32) < 0.005
      and abs(L95 - 4.93) < 0.006 and abs(L99 - 7.70) < 0.006 and abs(L80 * Td - 1.32) < 0.006
      and abs(L95 * Td - 2.79) < 0.006 and abs(L99 * Td - 4.36) < 0.006 and abs(L99 * Td24 - 3.01) < 0.006)
eta_lo, eta_hi = math.log(4) / math.log(4), math.log(6) / math.log(4)
check("B2b 80% horizons 4 to 6 times shorter give eta_r in [1.00, 1.29]", abs(eta_lo - 1) < 1e-12 and abs(eta_hi - 1.292) < 5e-4)
H0, t0, Tds, kap, tt_ = sp.symbols("H_0 t_0 T_d kappa t", positive=True)
TF = t0 + Tds * sp.log(d_ * chi / (H0 * kap), 2)
check("B3 prop:ext-feasible(a): H(T_F) kappa_ctx = d chi(r) at T_F = t0 + T_d log2(d chi/(H0 kappa))",
      zero(sp.simplify(H0 * 2 ** ((TF - t0) / Tds) * kap - d_ * chi)))
xi_, iota_, Cv = sp.symbols("xi iota C", positive=True)
check("B4 ass:ext-capability(iii): d/(d^g + (1 - iota C) d^c) = 1/(1 - xi iota C) with xi = d^c/d",
      zero(d_ / (d_ * (1 - xi_) + (1 - iota_ * Cv) * xi_ * d_) - 1 / (1 - xi_ * iota_ * Cv)))
K1 = (1 / (1 - 0.5 * 0.9)) / (1 / (1 - 0.5 * 0.2))
print(f"     -> context engine xi=0.5, iota*C 0.2->0.9: factor {K1:.3f}, {math.log2(K1):.2f} doublings, "
      f"{Td * math.log2(K1):.2f} years")
check("B4b example: factor 1.636 = 0.71 doublings = 0.40 years", abs(K1 - 1.636) < 5e-4 and abs(math.log2(K1) - 0.71) < 0.005
      and abs(Td * math.log2(K1) - 0.40) < 0.005)
# feasible share S-curve
muH, sdH = 4.0, 3.0
draws = muH + sdH * RNG.standard_normal(400000)
SF = lambda t, T: float(norm.cdf(((t - 2025.2) / T - muH) / sdH))
mc_ok = all(abs(np.mean(draws <= (t - 2025.2) / Td) - SF(t, Td)) < 3e-3 for t in [2025.5, 2027, 2028, 2030])
width = 2 * norm.ppf(0.9) * sdH * Td
check("B5 prop:ext-feasible(d): normal log-horizon requirements give a probit S-curve (Monte Carlo)", mc_ok)
check("B5b 10-90 width = 2 z_0.9 sd T_d = 4.36 years for sd = 3 doublings (3.01 at 143-day doubling)",
      abs(width - 4.36) < 0.005 and abs(2 * norm.ppf(0.9) * sdH * Td24 - 3.01) < 0.005, f"{width:.3f}")
check("B5c time scaling: Sigma(t; T_d') = Sigma(t0 + (T_d/T_d')(t - t0); T_d)",
      all(abs(SF(t, Td24) - SF(2025.2 + (Td / Td24) * (t - 2025.2), Td)) < 1e-12 for t in [2026, 2027.5, 2030]))
# energy share
sE0, dE, dX, tt2 = sp.symbols("s_E0 delta_E delta_hw t", positive=True)
sE = sE0 * sp.exp(-dE * tt2) / (sE0 * sp.exp(-dE * tt2) + (1 - sE0) * sp.exp(-dX * tt2))
check("B6 prop:ext-energy(b): ds_E/dt = s_E (1 - s_E)(delta_hw - delta_E)",
      zero(sp.diff(sE, tt2) - sE * (1 - sE) * (dX - dE)))
sEv = 0.07
days = lambda ef, dpi: -math.log(1 - sEv * ef) / dpi * 365.25
print(f"     -> fusion: free energy = {days(1, math.log(5)):.1f} days of the trend at 5x/yr, {days(1, math.log(10)):.1f} at 10x/yr;"
      f" 90% cut: {days(0.9, math.log(5)):.1f} days at 5x/yr")
# c_c: Part I's compute share at full automation (params commit of 29 Oct 2026): 0.06 at 2025 prices; by horizon
# 0.12 (2028), 0.08 (2031), 0.05 (2036) (code/calibrate_horizons.py CC; params.yaml part1_ceiling.c_c_compute_share)
CC_P1 = {'2025 prices': 0.06, '2028': 0.12, '2031': 0.08, '2036': 0.05}
dRm = 0.82 * sEv * 0.9 * CC_P1['2025 prices']
print("     -> energy cut by horizon (points of R_max, 90% cut): "
      + ", ".join(f"{h} {100 * 0.82 * sEv * 0.9 * c:.2f}" for h, c in CC_P1.items()))
check("B7 prop:ext-energy(a): with s_E = 0.07 free energy equals 16.5 days of a 5x/yr price trend (11.5 at 10x/yr)",
      abs(days(1, math.log(5)) - 16.5) < 0.05 and abs(days(1, math.log(10)) - 11.5) < 0.05)
dRm_h = {h: 100 * 0.82 * sEv * 0.9 * c for h, c in CC_P1.items()}
check("B8 prop:ext-energy(d): R_max rises by (1 - tau) s_E e_f c_c: 0.31 points at Part I's central c_c at 2025 prices "
      "(0.06), and 0.62, 0.41 and 0.26 points at its 2028, 2031 and 2036 central shares (tau 0.18, 90% cut)",
      abs(100 * dRm - 0.31) < 0.005 and abs(dRm_h["2028"] - 0.62) < 0.005 and abs(dRm_h["2031"] - 0.41) < 0.005
      and abs(dRm_h["2036"] - 0.26) < 0.005, f"{100 * dRm:.3f} points; {dRm_h}")
# AGI limit: the capability condition becomes slack; error rate 1 - p -> 0
pH = lambda d, H: 1 / (1 + (d / H) ** (1 / eta_r))
check("B9 prop:ext-agi(a): as H -> infinity, every cognitive activity passes the capability test and 1 - p -> 0",
      pH(500.0, 1e8) > 0.999 and pH(500.0, 1e12) > pH(500.0, 1e8) and 1 - pH(500.0, 1e15) < 1e-9)
okagi = True
for a in pop[:200]:
    P_agi = dict(BASE); P_agi["iota_mult"] = 1e-9
    m_agi = mode_costs(dict(a, Afeas=True), P_agi)
    if "A" in m_agi:
        xm_ = BASE["ximin"].get(a["cls"], 0)
        floor = (a["w0"] * 1.43) * xm_ * a["tR"] + a["lic"] * a["wL0"] * 1.43 * a["tL"]
        c_, h_, _, mach_, K_ = m_agi["A"]
        ups_ = (1 - BASE["psi"] * BASE["tau"]) / (1 - BASE["tau"])
        nonlab = (1 + BASE["tau_A"]) * (mach_ + ups_ * K_) + (0.0) + Xhat(BASE) * a["cust"]
        okagi &= c_ >= floor - 1e-9 and abs((c_ - nonlab) - floor) < 1e-6 * (1 + floor)
        okagi &= abs(h_ - (xm_ * a["tR"] + a["lic"] * a["tL"])) < 1e-9
check("B9b prop:ext-agi(b): as the raw error rate vanishes, the review share of mode A tends to the floor and its "
      "human cost to what xi_min t^R + lic what^L t^L (200 activities)", okagi)

# adoption timing (prop:ext-timing)
T, r, dF, F0, Sb_, v_, gv = sp.symbols("T r delta_F F_0 Sbar v g_v", positive=True)
tau_s = sp.symbols("s", positive=True)
cN, lA, p0, dpi = sp.symbols("c_N ell_A pi_0 delta_pi", positive=True)
s_of = cN - lA - p0 * sp.exp(-dpi * tau_s)
Wint = sp.integrate(sp.exp(-r * tau_s) * v_ * s_of, (tau_s, T, sp.oo), conds="none")
W = Wint - sp.exp(-r * T) * F0 * sp.exp(-dF * T)
dW = sp.diff(W, T)
claim = sp.exp(-r * T) * ((r + dF) * F0 * sp.exp(-dF * T) - v_ * s_of.subs(tau_s, T))
check("B10 prop:ext-timing(a): O'(T) = e^{-rT}[(r + delta_F) F(T) - v s(T)] (pay-as-you-go AI cost)",
      zero(sp.simplify(dW - claim)))
# closed form (i)
Tstar_i = sp.log((r + dF) * F0 / Sb_) / dF
check("B11 prop:ext-timing(d)(i): constant savings flow: T* = ln[(r + delta_F) F0 / Sbar]/delta_F solves the FOC",
      zero(Sb_ - (r + dF) * F0 * sp.exp(-dF * Tstar_i)))
Tst = math.log(0.4 * 20 / 4) / 0.3
O_ = lambda T_: math.exp(-0.1 * T_) * (4 / 0.1 - 20 * math.exp(-0.3 * T_))
res = optimize.minimize_scalar(lambda T_: -O_(T_), bounds=(0, 20), method="bounded", options={"xatol": 1e-10})
print(f"     -> timing example: T* = {Tst:.3f} yr, O(0) = {O_(0):.2f}, O(T*) = {O_(Tst):.2f} ($M)")
check("B12 example: T* = 2.31 years; NPV now 20.0 > 0 yet waiting adds 3.8 ($M)",
      abs(Tst - 2.31) < 0.005 and abs(res.x - Tst) < 1e-6 and abs(O_(0) - 20) < 1e-9 and abs(O_(Tst) - 23.81) < 0.005)
# closed form (ii)
Tstar_ii = sp.log(p0 / (cN - lA - r * F0 / v_)) / dpi
foc_ii = (r * F0 - v_ * s_of.subs(tau_s, T)).subs(T, Tstar_ii)
check("B13 prop:ext-timing(d)(ii): falling inference price, constant F: T* = ln[pi0/(c_0 - c^Q - r F0/v)]/delta_pi",
      zero(sp.simplify(foc_ii)))
# vintage lock-in (e)
Wlock = sp.integrate(sp.exp(-r * tau_s) * v_ * sp.exp(gv * tau_s), (tau_s, T, sp.oo), conds="none")
cAv = lA + p0 * sp.exp(-dpi * T)
Wl = Wlock * (cN - cAv) - sp.exp(-r * T) * F0 * sp.exp(-dF * T)
Wl = Wl.subs(gv, sp.Rational(1, 50)).subs(r, sp.Rational(1, 10))
dWl = sp.diff(Wl, T)
vT = v_ * sp.exp(T / 50)
claim_l = sp.exp(-T / 10) * ((sp.Rational(1, 10) + dF) * F0 * sp.exp(-dF * T) + vT * dpi * p0 * sp.exp(-dpi * T)
                              / (sp.Rational(1, 10) - sp.Rational(1, 50)) - vT * (cN - cAv))
check("B14 prop:ext-timing(e): vintage lock-in adds v |c_A'| / (r - g_v) to the hurdle (the spec's cost-decline term)",
      zero(sp.simplify(dWl - claim_l)))
# parallel-run generalization (a'): numerical derivative of the value with a ramp and a transition-cost path
Tpar, rr_ = 0.5, 0.10
ramp_bar = (1 - math.exp(-rr_ * Tpar)) / (rr_ * Tpar)


def O_par(Ta, Sflow=4.0, F0_=20.0, dF_=0.3, Cdup=1.07, Sstr=2.0, brk=3.0, Tc=3.0):
    sav = integrate.quad(lambda t_: math.exp(-rr_ * t_) * Sflow * min(max((t_ - Ta) / Tpar, 0), 1), Ta, Ta + 60,
                         limit=400)[0] + math.exp(-rr_ * (Ta + 60)) * Sflow / rr_
    Tcost = F0_ * math.exp(-dF_ * Ta) + Cdup + Sstr + brk * max(1 - Ta / Tc, 0)
    return sav - math.exp(-rr_ * Ta) * Tcost


hurdle = lambda Ta, brk=3.0, Tc=3.0: (rr_ * (20 * math.exp(-0.3 * Ta) + 1.07 + 2.0 + brk * max(1 - Ta / Tc, 0))
                                       + 0.3 * 20 * math.exp(-0.3 * Ta) + (brk / Tc if Ta < Tc else 0.0))
okp = True
for Ta in [0.7, 1.6, 2.4]:
    num = (O_par(Ta + 1e-5) - O_par(Ta - 1e-5)) / 2e-5
    okp &= abs(num - math.exp(-rr_ * Ta) * (hurdle(Ta) - ramp_bar * 4.0)) < 1e-5
check("B15 prop:ext-timing(f): with a ramp and transition-cost path, O'(T) = e^{-rT}[r T(T) - T'(T) - rampbar S]",
      okp, f"discounted ramp factor (linear, 6 months) = {ramp_bar:.4f}")
Tnofee = math.log(20 * 0.4 / (ramp_bar * 4.0 - 0.1 * 3.07)) / 0.3
grid = np.linspace(0, 6, 60001)
Tbest = grid[np.argmax([O_par(x) for x in grid[::100]]) * 100]
Tbest = optimize.minimize_scalar(lambda x: -O_par(x), bounds=(max(Tbest - 0.05, 0), Tbest + 0.05), method="bounded").x
print(f"     -> with parallel run and stranded costs: T* (no break fee) = {Tnofee:.3f}; "
      f"with a break fee expiring at 3.0: T* = {Tbest:.3f}")
check("B16 example: parallel-run and stranded costs delay T* from 2.31 to 2.67 years; a break fee that expires at "
      "T_c = 3 moves adoption to the expiry date", abs(Tnofee - 2.67) < 0.005 and abs(Tbest - 3.0) < 2e-3
      and hurdle(2.999) > ramp_bar * 4 > hurdle(3.0))

# ==============================================================================================
header("C. Competition: should versus could (sec:ext-competition)")
# ==============================================================================================
Asym, Bsym = sp.symbols("A B", positive=True)
cs = sp.symbols("c1:5", positive=True)
xs = sp.symbols("x1:5", positive=True)
Ntot = 4
Pexpr = Asym - Bsym * sum(xs)
focs = [sp.diff((Pexpr - cs[i]) * xs[i], xs[i]) for i in range(Ntot)]
sol = sp.solve(focs, xs, dict=True)[0]
Psol = sp.simplify(Pexpr.subs(sol))
check("C1 lem:ext-retained: asymmetric Cournot price P = (A + sum c_i)/(N + 1) (N = 4, symbolic)",
      zero(Psol - (Asym + sum(cs)) / (Ntot + 1)) and all(zero(sol[xs[i]] - (Psol - cs[i]) / Bsym) for i in range(Ntot)))
dd = sp.symbols("d", positive=True)
okc = True
for M in range(0, Ntot):
    sub = {cs[0]: cs[0] - dd}
    for j in range(1, M + 1):
        sub[cs[j]] = cs[j] - dd
    Pn = Psol.subs(sub)
    okc &= zero((Pn - (cs[0] - dd)) - (Psol - cs[0]) - (Ntot - M) * dd / (Ntot + 1))
    if M + 1 < Ntot:
        okc &= zero((Pn - cs[Ntot - 1]) - (Psol - cs[Ntot - 1]) + (M + 1) * dd / (Ntot + 1))
check("C2 lem:ext-retained(a): adopter's margin rises by (N-M)d/(N+1); non-adopter's falls by (M+1)d/(N+1)", okc)
Ng = 50
check("C3 lem:ext-retained(b): retained share (N-M)/(N+1) -> 1 - rep as N grows with M = rep (N-1)",
      abs((Ng - 0.6 * (Ng - 1)) / (Ng + 1) - 0.4) < 0.02 and abs((2000 - 0.6 * 1999) / 2001 - 0.4) < 1e-3)


def Epriv(m, d, N, M):
    return ((m + (N - M) * d / (N + 1)) ** 2 - max(m - M * d / (N + 1), 0) ** 2)


def Eeq(m, d, N):
    return (m + d / (N + 1)) ** 2 - m ** 2


oks = True
for _ in range(500):
    m, d, N = RNG.uniform(0.05, 1), RNG.uniform(0.01, 0.8), int(RNG.integers(2, 12))
    vals = [Epriv(m, d, N, M) for M in range(N)]
    oks &= all(vals[i] >= vals[i + 1] - 1e-12 for i in range(N - 1)) and vals[N - 1] >= Eeq(m, d, N) - 1e-12
check("C4 prop:ext-should(a): private gains are decreasing in the number of adopting rivals (strategic substitutes) "
      "and exceed the equilibrium gain (500 draws)", oks)
m, d, N, Bq = 0.20, 0.10, 4, 1.0
g_eq, g_priv_all, g_priv_none = Eeq(m, d, N) / Bq, Epriv(m, d, N, N - 1) / Bq, Epriv(m, d, N, 0) / Bq
print(f"     -> Cournot example m=0.20, d=0.10, N=4: E_eq={g_eq:.4f}, E_priv(N-1)={g_priv_all:.4f}, E_priv(0)={g_priv_none:.4f}")
check("C5 example: defensive window E_eq = 0.0084 <= K < 0.0288 = E_priv(N-1); E_priv(0) = 0.0384",
      abs(g_eq - 0.0084) < 5e-5 and abs(g_priv_all - 0.0288) < 5e-5 and abs(g_priv_none - 0.0384) < 5e-5)
# AI-native entrant: flip date, long-run viability
cE = lambda t_: 0.45 + 0.75 * math.exp(-0.4 * t_)
TM = optimize.brentq(lambda t_: cE(t_) + 0.05 - 1.00, 0, 20)
print(f"     -> AI-native entry: flip date T_M = {TM:.3f} yr; long-run price {0.45 + 0.05:.2f}")
check("C6 prop:ext-should(c): flip date T_M = ln 1.5/0.4 = 1.01 years; the incumbent with c_I* = 0.55 is not viable",
      abs(TM - math.log(1.5) / 0.4) < 1e-9 and abs(TM - 1.01) < 0.005 and 0.55 > 0.45 + 0.05)
# covering problem: greedy ratio rule solves the LP relaxation
okg = True
for _ in range(200):
    n_ = int(RNG.integers(3, 12))
    cost = RNG.uniform(0.1, 3, n_)
    cover = RNG.uniform(0.05, 1, n_)
    D = RNG.uniform(0.1, 0.9) * cover.sum()
    lp = optimize.linprog(cost, A_ub=-cover[None, :], b_ub=[-D], bounds=[(0, 1)] * n_, method="highs")
    order = np.argsort(cost / cover)
    rem, val = D, 0.0
    for i in order:
        take = min(1.0, rem / cover[i])
        val += take * cost[i]
        rem -= take * cover[i]
        if rem <= 1e-15:
            break
    okg &= abs(val - lp.fun) < 1e-8 * (1 + lp.fun)
check("C7 prop:ext-should(d): the greedy ratio rule solves the LP relaxation of the covering problem (200 instances)", okg)

# ==============================================================================================
header("D. Organization (sec:ext-org)")
# ==============================================================================================
n_, Wv, ch = sp.symbols("n W chi_h", positive=True)
nroot = ((1 + ch / 2) - sp.sqrt((1 + ch / 2) ** 2 - 2 * ch * Wv)) / ch
check("D1 prop:ext-team(b): n*(W) solves n - chi n(n-1)/2 = W", zero(sp.expand(nroot - ch * nroot * (nroot - 1) / 2 - Wv)))
check("D1b n*(1) = 1 and W_max = (1 + chi/2)^2/(2 chi)",
      zero(sp.simplify(nroot.subs(Wv, 1) - 1).subs(ch, sp.Rational(3, 100))) and
      zero(sp.simplify(((1 + ch / 2) ** 2 - 2 * ch * Wv).subs(Wv, (1 + ch / 2) ** 2 / (2 * ch)))))
dn = sp.diff(nroot, Wv)
d2n = sp.diff(nroot, Wv, 2)
okn2 = all(float(dn.subs({ch: c, Wv: w})) >= 1 and float(d2n.subs({ch: c, Wv: w})) > 0
           for c in [0.01, 0.03, 0.1] for w in [1.0, 3.0, 8.0] if w < (1 + c / 2) ** 2 / (2 * c))
check("D2 prop:ext-team(e): dn*/dW = 1/(1 - chi(n - 1/2)) >= 1 and n* is convex in W", okn2 and
      zero(sp.simplify(dn - 1 / (1 - ch * (nroot - sp.Rational(1, 2))))))
nnum = lambda W, c: ((1 + c / 2) - math.sqrt((1 + c / 2) ** 2 - 2 * c * W)) / c if W > 1 else W
Wlev = lambda Ag, nu, psA: 1 / ((1 - nu) / Ag + nu * psA)
n_pre = nnum(8.0, 0.03)
W1 = 8.0 / Wlev(1.5, 0.6, 0.15)
n1 = nnum(W1, 0.03)
L2 = Wlev(2.0, 0.9, 0.05)
print(f"     -> team: pre-AI n* = {n_pre:.2f}; with A_g=1.5, nu=0.6, xi^t=0.15: W = {W1:.3f}, n* = {n1:.2f}; "
      f"leverage at (2, 0.9, 0.05) = {L2:.2f}")
check("D3 example: 8 person-years of work needs 9.11 people (chi = 0.03); with AI W = 2.85 and n* = 2.94; "
      "leverage 10.5 makes the scope solo", abs(n_pre - 9.11) < 0.005 and abs(W1 - 2.853) < 5e-4 and abs(n1 - 2.94) < 0.005
      and abs(L2 - 10.53) < 0.005 and 8.0 / L2 < 1)
okA = True
for _ in range(2000):
    Ag, nu, psA = RNG.uniform(1, 3), RNG.uniform(0, 1), RNG.uniform(0.01, 1)
    Lv = Wlev(Ag, nu, psA)
    okA &= Lv <= Ag / (1 - nu) + 1e-12 if nu < 1 else True
    okA &= Lv <= 1 / (nu * psA) + 1e-12 if nu > 0 else True
check("D4 prop:ext-team(d): Amdahl bounds Lambda <= A_g/(1 - nu) and Lambda <= 1/(nu xi^t) (2000 draws); "
      "Lambda -> 1/xi^t as nu -> 1", okA and abs(Wlev(2.0, 1 - 1e-12, 0.1) - 10) < 1e-8)


# agent share: bang-bang when the activity-level test holds; interior otherwise (prop:ext-team(a))
def team_cost(nu, W0, Ag, psA, c, w, pa, Ya):
    W = W0 * ((1 - nu) / Ag + nu * psA)
    Wmax = (1 + c / 2) ** 2 / (2 * c)
    if W > Wmax:
        return math.inf
    return w * nnum(W, c) + pa * nu * W0 / Ya


okb = True
W0e, Age, psAe, ce, we, Yae = 20.0, 1.3, 0.2, 0.03, 1.0, 1.0
thr = we * (1 / Age - psAe) * Yae          # agents win at the activity level iff pa < thr
for pa in [0.3, 0.5, thr * 0.99]:
    res = optimize.minimize_scalar(lambda q: team_cost(q, W0e, Age, psAe, ce, we, pa, Yae), bounds=(0, 0.8),
                                   method="bounded", options={"xatol": 1e-10})
    okb &= res.x > 0.8 - 1e-4
res_int = optimize.minimize_scalar(lambda q: team_cost(q, W0e, Age, psAe, ce, we, thr * 1.25, Yae), bounds=(0, 0.8),
                                   method="bounded", options={"xatol": 1e-10})
Wi = W0e * ((1 - res_int.x) / Age + res_int.x * psAe)
ni = nnum(Wi, ce)
foc_int = we * (1 / Age - psAe) / (1 - ce * (ni - 0.5)) - thr * 1.25 / Yae
okb &= 0 < res_int.x < 0.8 and abs(foc_int) < 1e-5
check("D5 prop:ext-team(a): agents take all feasible work when p_a/Y_a < w(1/A_g - xi^t); otherwise interior share "
      "where the coordination-adjusted wage w/(1 - chi(n - 1/2)) equals the agent cost", okb,
      f"interior share {res_int.x:.3f}, n={ni:.2f}")
# profit-maximizing team size rises with A_g (remark)
npi = lambda Ag, wP, c: 0.5 + (Ag - wP) / c
check("D6 prop:ext-team(f): with unlimited scope, n^pi = 1/2 + (A_g - w/P)/chi rises with A_g",
      npi(2.0, 0.6, 0.03) > npi(1.5, 0.6, 0.03) and zero(sp.diff(sp.Symbol('P') * (n_ * sp.Symbol('A_g') - ch * n_ * (n_ - 1) / 2)
                                                                - sp.Symbol('w') * n_, n_).subs(n_, sp.Rational(1, 2) + (sp.Symbol('A_g') - sp.Symbol('w') / sp.Symbol('P')) / ch)))
# Garicano hierarchy (prop:ext-hierarchy)
zw, cK, kc, wm, zm, ww = sp.symbols("z_w c_K kappa_c w_m z_m w_w", positive=True)
Cw = ww + cK * zw + kc * sp.exp(-zw) * (wm + cK * zm)
zstar = sp.log(kc * (wm + cK * zm) / cK)
check("D7 prop:ext-hierarchy(a): z_w* = ln[kappa_c (w_m + c_K z_m)/c_K] and span = (w_m + c_K z_m)/c_K",
      zero(sp.diff(Cw, zw).subs(zw, zstar)) and zero(sp.simplify(1 / (kc * sp.exp(-zstar)) - (wm + cK * zm) / cK)))
check("D7b comparative statics: span falls in c_K, does not depend on kappa_c; z_w* rises one-for-one with ln kappa_c",
      zero(sp.diff((wm + cK * zm) / cK, cK) + wm / cK ** 2) and zero(sp.diff(zstar, kc) * kc - 1))


# general distribution: d ln span / d ln kappa = -1 + lambda/( lambda - lambda'/lambda )
def span_general(kap, f, Sbar, kshape, c=1.0, K=5.0):
    """FOC kap K f(z) = c on the decreasing branch of the density (second-order condition f' < 0)"""
    zlo = ((kshape - 1) / kshape) ** (1 / kshape) + 1e-9 if kshape > 1 else 1e-12
    z = optimize.brentq(lambda z: kap * K * f(z) - c, zlo, 50)
    return 1 / (kap * Sbar(z)), z


okg2 = True
for kshape, kap0 in [(0.6, 0.5), (1.0, 0.5), (1.8, 1.0)]:    # Weibull: decreasing, constant, increasing hazard
    f = lambda z, k=kshape: k * z ** (k - 1) * math.exp(-z ** k)
    Sbar = lambda z, k=kshape: math.exp(-z ** k)
    s0, z0 = span_general(kap0, f, Sbar, kshape)
    s1, _ = span_general(kap0 * (1 + 1e-6), f, Sbar, kshape)
    el = (math.log(s1) - math.log(s0)) / math.log(1 + 1e-6)
    lam = kshape * z0 ** (kshape - 1)
    lamp = kshape * (kshape - 1) * z0 ** (kshape - 2)
    pred = -1 + lam / (lam - lamp / lam)
    okg2 &= abs(el - pred) < 1e-4 and (np.sign(el) == np.sign(kshape - 1) if kshape != 1 else abs(el) < 1e-5)
check("D8 prop:ext-hierarchy(b): d ln span/d ln kappa_c = -1 + lam/(lam - lam'/lam); negative under decreasing "
      "hazard (cheaper communication widens spans), zero for the exponential, positive under increasing hazard", okg2)
# AI bottom layer and memorylessness (c)
zA = 1.2
wwv, wmv, cKv, kcv, zmv = 1.0, 1.6, 0.08, 0.15, 6.0
Cfull = lambda zr: wwv + cKv * zr + kcv * math.exp(-zr) * (wmv + cKv * (zmv - zA))   # humans above AI layer
res_h = optimize.minimize_scalar(Cfull, bounds=(0, zmv - zA), method="bounded", options={"xatol": 1e-12})
zr_pred = math.log(kcv * (wmv + cKv * (zmv - zA)) / cKv)
sp_pre, sp_ai = (wmv + cKv * zmv) / cKv, (wmv + cKv * (zmv - zA)) / cKv
# simulate: problems escalated by an AI layer at zA have residual difficulty Exp(1)
zs = RNG.exponential(1.0, 1000000)
esc = zs[zs > zA] - zA
check("D9 prop:ext-hierarchy(c): above an AI layer the human hierarchy is the original one with z_m -> z_m - z_A; "
      "human headcount per problem falls by e^{-z_A}", abs(res_h.x - zr_pred) < 1e-6 and abs(np.mean(zs > zA) - math.exp(-zA)) < 2e-3
      and abs(esc.mean() - 1) < 5e-3 and sp_ai < sp_pre, f"spans {sp_pre:.1f} -> {sp_ai:.1f}; e^-zA = {math.exp(-zA):.3f}")
zetaP = 0.5
rate = zetaP * math.log(2) / Td
print(f"     -> Pareto task lengths, tail 0.5: human exception load falls at {rate:.3f}/yr (halves every {math.log(2) / rate:.2f} yr)")
check("D10 prop:ext-hierarchy(d): with Pareto task lengths the exception share (H/d_min)^(-zeta) falls at zeta ln2/T_d "
      "= 0.612/yr, halving every 1.13 years", abs(rate - 0.612) < 5e-4 and abs(math.log(2) / rate - 1.13) < 0.005)
# staffing identities (lem:ext-staffing)
hours = {"H": 0.25, "O": 0.025, "A": 0.0375 + 0.0, "U": 0.25 / 1.15, "N": 0.0}
vol = 1e6
base_fte = vol * 0.25 / 2080
res_fte = vol * hours["A"] / 2080
check("D11 lem:ext-staffing(a): baseline FTE = residual FTE + displaced FTE (support example: 120.2 -> 18.0)",
      abs(base_fte - (res_fte + vol * (0.25 - hours["A"]) / 2080)) < 1e-9 and abs(base_fte - 120.19) < 0.01
      and abs(res_fte - 18.03) < 0.01)

# ==============================================================================================
header("E. Program sequencing, parallel running and change capacity (sec:ext-program)")
# ==============================================================================================


def wave_cost(sizes, s, Tpar, d1, d2, Ow):
    return sum(Tpar * (s * (k + 1) * n + d1 * n + d2 * n * n) + Ow for k, n in enumerate(sizes) if n > 0)


Nn, s_w, Tp, d1, d2, Ow = 12, 1.0, 0.5, 0.2, 0.25, 0.5
best = None
for comp_mask in range(2 ** (Nn - 1)):
    cuts = [i + 1 for i in range(Nn - 1) if comp_mask >> i & 1]
    sizes = [b - a for a, b in zip([0] + cuts, cuts + [Nn])]
    c = wave_cost(sizes, s_w, Tp, d1, d2, Ow)
    if best is None or c < best[0] - 1e-12:
        best = (c, sizes)
nstar_eq = math.sqrt((s_w * Nn / 2 + Ow / Tp) / d2)
print(f"     -> program N=12, s=1, T_par=0.5, d1=0.2, d2=0.25, O_w=0.5: best waves {best[1]}, cost {best[0]:.3f}; "
      f"square-root rule n* = {nstar_eq:.2f}, K* = {Nn / nstar_eq:.2f}")
check("D/E1 prop:ext-waves(b): the optimal integer wave plan is front-loaded with decrement about s/(2 d2) = 2",
      best[1] == sorted(best[1], reverse=True) and all(abs((best[1][i] - best[1][i + 1]) - 2) <= 1 for i in range(len(best[1]) - 1)),
      f"{best[1]}")
# continuous KKT sizes for given K and C(K) closed form
okw = True
for K in [2, 3, 4]:
    c_ = s_w / (2 * d2)
    sizes = [Nn / K + c_ * ((K + 1) / 2 - k) for k in range(1, K + 1)]
    if min(sizes) <= 1e-9:
        continue
    cons = {"type": "eq", "fun": lambda x: np.sum(x) - Nn}
    resq = optimize.minimize(lambda x: wave_cost(list(x), s_w, Tp, d1, d2, Ow), x0=np.full(K, Nn / K),
                             constraints=[cons], bounds=[(0, None)] * K, method="SLSQP", options={"ftol": 1e-14})
    okw &= np.allclose(resq.x, sizes, atol=1e-5)
    CK = Tp * (s_w * Nn * (K + 1) / 2 + d1 * Nn + d2 * Nn ** 2 / K - s_w ** 2 * K * (K ** 2 - 1) / (48 * d2)) + K * Ow
    okw &= abs(CK - wave_cost(sizes, s_w, Tp, d1, d2, Ow)) < 1e-9
check("E2 prop:ext-waves(b): for given K the cost-minimizing sizes are n_k = N/K + (s/2d2)((K+1)/2 - k), and "
      "C(K) = T_par[sN(K+1)/2 + d1 N + d2 N^2/K - s^2 K(K^2-1)/(48 d2)] + K O_w", okw)
# equal-size square-root rule
nn = sp.symbols("n", positive=True)
Ceq = s_w * Tp * Nn ** 2 / (2 * nn) + Nn * Ow / nn + Nn * Tp * d2 * nn
nst = sp.solve(sp.diff(Ceq, nn), nn)
check("E3 prop:ext-waves(c): equal-size approximation gives n* = sqrt[(sN/2 + O_w/T_par)/d2]",
      any(abs(float(x) - nstar_eq) < 1e-9 for x in nst))
# ordering by savings (exchange argument)
oko = True
for _ in range(100):
    svals = RNG.uniform(0.2, 3, 6)
    sizes = [3, 2, 1]
    def cost_assign(order):
        tot, idx = 0.0, 0
        for k, n in enumerate(sizes):
            for _ in range(n):
                tot += Tp * (k + 1) * svals[order[idx]]
                idx += 1
        return tot
    best_o = min(itertools.permutations(range(6)), key=cost_assign)
    oko &= abs(cost_assign(best_o) - cost_assign(list(np.argsort(-svals)))) < 1e-12
check("E4 prop:ext-waves(a): processes enter waves in decreasing order of savings (brute force, 100 instances)", oko)
# capacity binding
a_fte, Kchg = 40.0, 320.0
ncap = Kchg * Tp / a_fte
best_cap = None
for comp_mask in range(2 ** (Nn - 1)):
    cuts = [i + 1 for i in range(Nn - 1) if comp_mask >> i & 1]
    sizes = [b - a for a, b in zip([0] + cuts, cuts + [Nn])]
    if max(sizes) > ncap:
        continue
    c = wave_cost(sizes, s_w, Tp, d1, d2, Ow)
    if best_cap is None or c < best_cap[0] - 1e-12:
        best_cap = (c, sizes)
dur = len(best_cap[1]) * Tp
print(f"     -> capacity 320 FTE/yr, 40 FTE per process: n_cap = {ncap:.0f}; best plan {best_cap[1]}, cost {best_cap[0]:.3f} "
      f"(unconstrained {best[0]:.3f}); duration {dur:.1f} yr >= N a/K_chg = {Nn * a_fte / Kchg:.1f}")
check("E5 prop:ext-waves(d): binding change capacity caps wave size at K_chg T_par / a and the duration at >= N a/K_chg",
      max(best_cap[1]) <= ncap and dur >= Nn * a_fte / Kchg - 1e-12 and best_cap[0] > best[0])
# shadow value of capacity: finite difference on the integer program
def best_plan(cap):
    bb_ = None
    for comp_mask in range(2 ** (Nn - 1)):
        cuts = [i + 1 for i in range(Nn - 1) if comp_mask >> i & 1]
        sizes = [b - a for a, b in zip([0] + cuts, cuts + [Nn])]
        if max(sizes) > cap:
            continue
        c = wave_cost(sizes, s_w, Tp, d1, d2, Ow)
        if bb_ is None or c < bb_[0]:
            bb_ = (c, sizes)
    return bb_


gain = best_plan(5)[0]
print(f"     -> raising capacity from 4 to 5 processes per wave saves {best_cap[0] - gain:.3f} ($M)")
check("E6 prop:ext-waves(d): change capacity has positive shadow value when it binds", best_cap[0] - gain > 0)
# linear dual-running cost: big bang
check("E7 prop:ext-waves(e): with d2 = 0 a single wave is optimal when capacity allows",
      min(range(1, Nn + 1), key=lambda K: wave_cost([Nn / K] * K, s_w, Tp, d1, 0.0, Ow)) == 1)
# score path dip (prop:ext-waves(f))
Srev = 500.0
sizes = best[1]
dips = []
for k, n in enumerate(sizes):
    done = sum(sizes[:k])
    dips.append((done * s_w - (d1 * n + d2 * n * n)) / Srev)
depth = -min(dips)
below = sum(1 for x in dips if x < 0)
print(f"     -> score path by wave (points of revenue): {[round(100 * x, 2) for x in dips]}; depth {100 * depth:.2f} points, "
      f"{below} wave(s) below baseline; final +{100 * Nn * s_w / Srev:.1f} points")
qd = (d1 * sizes[0] + d2 * sizes[0] ** 2) / (sizes[0] * s_w)
check("E8 prop:ext-waves(f): dip depth (D(n1))/S in wave 1; waves below baseline while (k-1) n s < D(n)",
      abs(depth - (d1 * sizes[0] + d2 * sizes[0] ** 2) / Srev) < 1e-12 and below >= 1)

# ==============================================================================================
header("F. Risky portfolios, learning and decision bandwidth (sec:ext-bandwidth)")
# ==============================================================================================
# two-process ordering with learning
V1, V2, p1, p2, dl1, dl2, dd_ = sp.symbols("V1 V2 pi1 pi2 Dpi1 Dpi2 delta_d", positive=True)
EV12 = p1 * V1 + dd_ * V2 * (p2 + p1 * dl2)
EV21 = p2 * V2 + dd_ * V1 * (p1 + p2 * dl1)
check("F1 prop:ext-portfolio(a): EV(1->2) - EV(2->1) = (1-delta)(varpi1 V1 - varpi2 V2) + delta(varpi1 Dvarpi2 V2 - varpi2 Dvarpi1 V1)",
      zero(EV12 - EV21 - ((1 - dd_) * (p1 * V1 - p2 * V2) + dd_ * (p1 * dl2 * V2 - p2 * dl1 * V1))))
logit = lambda p: math.log(p / (1 - p))
expit = lambda x: 1 / (1 + math.exp(-x))
pA, pB, VA, VB, dlt, upsL = 0.80, 0.45, 1.0, 1.0, 0.95, 1.0
dA = expit(logit(pA) + upsL * math.log(2)) - pA
dB_ = expit(logit(pB) + upsL * math.log(2)) - pB
diffAB = (1 - dlt) * (pA * VA - pB * VB) + dlt * (pA * dB_ * VB - pB * dA * VA)
print(f"     -> learning: logit shift upsilon ln2; Dpi = {dA:.3f} (likely win), {dB_:.3f} (hard); EV(win first) - EV(hard first) = {diffAB:.4f}")
check("F2 example: start with the likely win (varpi = 0.80) before the hard process (0.45): advantage 0.109 per unit "
      "value (activity and congestion factors equal to one, so varpi = varpi^c)", abs(diffAB - 0.109) < 5e-4 and diffAB > 0)
# learning acts on the process factor varpi^c of eq:tasks-success: varpi = R varpi^c with R = q prod varpi_pj
okl = True
for _ in range(400):
    Rf, pc, u_ = RNG.uniform(0.3, 1.0), RNG.uniform(0.05, 0.95), RNG.uniform(1e-7, 1e-6)
    dnum = (Rf * expit(logit(pc) + u_) - Rf * pc) / u_
    okl &= abs(dnum - Rf * pc * (1 - pc)) < 1e-5            # d varpi / d logit(varpi^c) = varpi (1 - varpi^c)
    # exact sign: with a common R and a common logit shift, varpi1 Dvarpi2 - varpi2 Dvarpi1 has the sign of varpi1 - varpi2
    pc1, pc2, sh = RNG.uniform(0.02, 0.98), RNG.uniform(0.02, 0.98), RNG.uniform(0.01, 3.0)
    d1_ = Rf * (expit(logit(pc1) + sh) - pc1)
    d2_ = Rf * (expit(logit(pc2) + sh) - pc2)
    term = Rf * pc1 * d2_ - Rf * pc2 * d1_
    okl &= (np.sign(term) == np.sign(pc1 - pc2)) or abs(pc1 - pc2) < 1e-12
check("F2b prop:ext-portfolio(a): with learning on the process factor varpi^c, d varpi/d logit varpi^c = varpi(1 - varpi^c); "
      "with common activity and congestion factors the learning term has the sign of varpi_1 - varpi_2 exactly (400 draws)", okl)
# the wave payoffs V_k (success) and C_k (failure) reproduce the core's risk-adjusted NPV eq:tasks-npv
Fs, Is, CJs, Cps, Ars, bWS, Cstr, Lroll, pu, rT, vp = sp.symbols("F I C_J C_par A_r bWS_r C_str L_roll p_u e_rT varpi")
V_succ = -(Fs + Is + CJs) - Cps * Ars + bWS - rT * Cstr
C_fail = (Fs + Is + CJs) + Cps * Ars + rT * pu * (Cstr + Lroll)
npv_core = -(Fs + Is + CJs) - Cps * Ars + vp * bWS - rT * ((vp + (1 - vp) * pu) * Cstr + (1 - vp) * pu * Lroll)
check("F2c ass:ext-portfolio: V_k on success and C_k on failure (up-front costs, parallel premium and, if undetected with "
      "probability e^{-T_par/T_det}, stranded and rollback costs) give varpi V - (1-varpi) C = eq:tasks-npv",
      zero(sp.expand(vp * V_succ - (1 - vp) * C_fail - npv_core)))
# common platform shock: sequential vs simultaneous
pP, pi_, Vv, Cf, dlt2 = 0.7, 0.9, 1.0, 0.6, 0.95
EV1 = pP * pi_ * Vv - (1 - pP * pi_) * Cf
pPost = pP * (1 - pi_) / (1 - pP * pi_)
EV2post = pPost * pi_ * Vv - (1 - pPost * pi_) * Cf
seq = EV1 + dlt2 * (EV1 + (1 - pP * pi_) * max(0, -EV2post))
sim = 2 * EV1
# brute-force enumeration
seq_bf = 0.0
for good in (1, 0):
    pg = pP if good else 1 - pP
    for s1 in (1, 0):
        p1_ = (pi_ if good else 0) if s1 else (1 - (pi_ if good else 0))
        v1 = Vv if s1 else -Cf
        cont_val = (pi_ * Vv - (1 - pi_) * Cf) if s1 else EV2post
        v2 = 0.0
        if cont_val > 0:
            v2 = (pi_ * Vv - (1 - pi_) * Cf) if good else -Cf
        seq_bf += pg * p1_ * (v1 + dlt2 * v2)
print(f"     -> platform shock p_P=0.7, pi=0.9: EV simultaneous {sim:.4f}, sequential {seq:.4f}; posterior after failure {pPost:.3f}")
check("F3 prop:ext-portfolio(b): sequencing value = delta (1 - p_P pi)(-EV_2(p'))_+ - (1 - delta) EV_1, enumeration agrees",
      abs(seq - seq_bf) < 1e-12 and abs((seq - sim) - (dlt2 * (1 - pP * pi_) * max(0, -EV2post) - (1 - dlt2) * EV1)) < 1e-12
      and seq > sim)
Kw = 5
varS = pP * Kw * pi_ * (1 - pi_) + Kw ** 2 * pi_ ** 2 * pP * (1 - pP)
sims = []
for _ in range(200000):
    g = RNG.random() < pP
    sims.append((RNG.random(Kw) < pi_).sum() if g else 0)
check("F4 prop:ext-portfolio(c): Var(successes) = p_P K pi(1-pi) + K^2 pi^2 p_P(1-p_P) (Monte Carlo)",
      abs(np.var(sims) - varS) < 0.02 * varS and abs(np.mean(sims) - Kw * pP * pi_) < 0.01)
# load breakpoint with M/M/1 latency
c_ = 0.5 * 0.25
xhat = 1 + c_ / 2 - math.sqrt(c_ + c_ ** 2 / 4)
Q = lambda x: math.exp(-c_ / (1 - x))
resx = optimize.minimize_scalar(lambda x: -x * Q(x), bounds=(0, 0.999), method="bounded", options={"xatol": 1e-12})
print(f"     -> load breakpoint with M/M/1 latency (r_d l_0 = 0.125): x_hat = {xhat:.4f}")
check("F5 prop:ext-bandwidth(a): x Q(x) peaks where the elasticity of Q equals one; M/M/1: x_hat = 1 + c/2 - sqrt(c + c^2/4)",
      abs(resx.x - xhat) < 1e-6 and abs(xhat - 0.703) < 5e-4)
# with quality congestion q(x) = exp(-eta (x-1)_+) and no latency: x_hat = 1/eta if eta < 1 else 1
etq = 0.6
resq2 = optimize.minimize_scalar(lambda x: -x * math.exp(-etq * max(x - 1, 0)), bounds=(0, 5), method="bounded",
                                 options={"xatol": 1e-12})
check("F5b quality congestion q = exp(-eta (x-1)_+): breakpoint x_hat = 1/eta for eta < 1", abs(resq2.x - 1 / etq) < 1e-6)
# value of bandwidth: envelope dEV*/dPhi = (n pi0 V Q / Phi) * eps_Q
pi0, Vb_, e_i, Phi0, D2 = 0.7, 3.0, 1.0, 10.0, 0.02


def EV_n(n, Phi):
    x = n * e_i / Phi
    if x >= 1:
        return -math.inf
    return n * pi0 * Vb_ * Q(x) - D2 * n * n


def opt_n(Phi):
    r_ = optimize.minimize_scalar(lambda n: -EV_n(n, Phi), bounds=(0, Phi * 0.999), method="bounded",
                                  options={"xatol": 1e-12})
    return r_.x, -r_.fun


ns, EVs = opt_n(Phi0)
dEV = (opt_n(Phi0 * (1 + 1e-5))[1] - opt_n(Phi0 * (1 - 1e-5))[1]) / (2e-5 * Phi0)
xs_ = ns * e_i / Phi0
epsQ = c_ * xs_ / (1 - xs_) ** 2
pred = ns * pi0 * Vb_ * Q(xs_) * epsQ / Phi0
print(f"     -> bandwidth example: n* = {ns:.2f} concurrent initiatives (load {xs_:.3f}), value of one more decision unit "
      f"{dEV:.4f}")
check("F6 prop:ext-bandwidth(c): marginal value of bandwidth = (expected portfolio value / Phi) x elasticity of Q",
      abs(dEV - pred) < 1e-4 * (1 + abs(pred)) and xs_ < xhat)
# AI-assisted bandwidth: Amdahl cap from accountable approval
eap, epr = 0.3, 0.7
gain = lambda A: (eap + epr) / (eap + epr / (1 + A))
check("F7 prop:ext-bandwidth(d): AI preparation support raises bandwidth by at most (e_appr + e_prep)/e_appr = 3.33",
      gain(1e9) < 1 / 0.3 and abs(gain(1e12) - 1 / 0.3) < 1e-9 and gain(1.0) > 1)
# delegation rule: delegate iff (pi_top - pi_del) V < lambda_Phi e
okd = True
lamPhi = dEV
for _ in range(500):
    Vi, ei, dp = RNG.uniform(0.1, 5), RNG.uniform(0.2, 2), RNG.uniform(0, 0.3)
    delegate = dp * Vi < lamPhi * ei
    okd &= delegate == (Vi * (pi0 - dp) + lamPhi * ei > Vi * pi0)
check("F8 prop:ext-bandwidth(e): delegate an initiative iff the expected loss from delegated quality is below the "
      "shadow price of top bandwidth times its load", okd)
# pace bound
Ttot = max(12 * 40 / 320, 12 * 1.0 * 0.5 / (xhat * 10))
check("F9 prop:ext-bandwidth(b): program duration >= max(N a/K_chg, N e T_par/(x_hat Phi))",
      abs(Ttot - max(1.5, 12 * 0.5 / (0.703 * 10))) < 1e-3)

# ----------------------------------------------------------------------------------------------
# rem:ext-seccap: decision bandwidth Phi, security-review capacity Phi_sec (core prop:tasks-secreview) and change capacity.
# n concurrent initiatives, each active T_par, deploy at nu = n/T_par a year; by prop:tasks-secreview(d) a deployment keeps
# Q_sec = (Phi_sec - nu)/(Phi_sec - nu + r_d) of its value, independently of the decision gate.
# ----------------------------------------------------------------------------------------------
def Qsec(n, Phis, Tpar_, rd):
    nu = n / Tpar_
    return (Phis - nu) / (Phis - nu + rd) if nu < Phis else 0.0


def eps_sec(n, Phis, Tpar_, rd):
    nu = n / Tpar_
    return nu * rd / ((Phis - nu) * (Phis - nu + rd))


def nu_hat_sec(Phis, rd):
    """security-only breakpoint: eps_sec = 1  <=>  nu = Phi_sec + r_d - sqrt(r_d^2 + r_d Phi_sec)"""
    return Phis + rd - math.sqrt(rd * rd + rd * Phis)


ok_a = True
for _ in range(300):
    rd, Phis, Tp_, cdec, ee, Phid = (RNG.uniform(0.1, 1.0), RNG.uniform(2, 40), RNG.uniform(0.25, 1.5),
                                    RNG.uniform(0.02, 0.5), RNG.uniform(0.3, 2.0), RNG.uniform(3, 30))
    # elasticity of Q_sec by finite difference
    n0 = 0.4 * Tp_ * Phis
    fd = -(math.log(Qsec(n0 * (1 + 1e-6), Phis, Tp_, rd)) - math.log(Qsec(n0 * (1 - 1e-6), Phis, Tp_, rd))) / 2e-6
    ok_a &= abs(fd - eps_sec(n0, Phis, Tp_, rd)) < 1e-5 * (1 + fd)
    # closed-form security-only breakpoint maximizes n Q_sec(n)
    nh = nu_hat_sec(Phis, rd)
    rs = optimize.minimize_scalar(lambda nu: -nu * (Phis - nu) / (Phis - nu + rd), bounds=(0, Phis * (1 - 1e-12)),
                                  method="bounded", options={"xatol": 1e-12})
    ok_a &= abs(rs.x - nh) < 1e-6 * (1 + nh) and nh < Phis and abs(eps_sec(nh * Tp_, Phis, Tp_, rd) - 1) < 1e-9
    # combined breakpoint: gross value n Q_dec(n e/Phi) Q_sec(n) peaks where the elasticities sum to one, below both
    xh = 1 + cdec / 2 - math.sqrt(cdec + cdec ** 2 / 4)
    ncap_dec, ncap_sec = xh * Phid / ee, Tp_ * nh
    nmax = min(Phid / ee, Tp_ * Phis) * (1 - 1e-9)
    g2 = lambda n: -(n * math.exp(-cdec / (1 - n * ee / Phid)) * Qsec(n, Phis, Tp_, rd))
    r2 = optimize.minimize_scalar(g2, bounds=(1e-9, nmax), method="bounded", options={"xatol": 1e-12})
    n2 = r2.x
    xd = n2 * ee / Phid
    tot_el = cdec * xd / (1 - xd) ** 2 + eps_sec(n2, Phis, Tp_, rd)
    ok_a &= n2 <= min(ncap_dec, ncap_sec) + 1e-6 and abs(tot_el - 1) < 1e-4
ok_a &= nu_hat_sec(20.0, 0.5) < 20.0
check("F10 rem:ext-seccap(a): eps_sec = nu r_d/[(Phi_sec - nu)(Phi_sec - nu + r_d)]; the security-only breakpoint "
      "nu_hat = Phi_sec + r_d - sqrt(r_d^2 + r_d Phi_sec) < Phi_sec; the combined peak, where eps_Q + eps_sec = 1, lies below "
      "both single-capacity breakpoints (300 draws)", ok_a)

# example and shadow values (rem:ext-seccap(b)), with the bandwidth example of prop:ext-bandwidth
TpS, rdS, PhisS = 0.5, 0.5, 20.0
c_dec = 0.5 * 0.25                           # r_d l_0 as in F5
Qd = lambda x: math.exp(-c_dec / (1 - x)) if x < 1 else 0.0


def EV2(n, Phi, Phis, ncap=math.inf):
    if n > ncap or n * e_i / Phi >= 1 or n / TpS >= Phis:
        return -math.inf
    return n * pi0 * Vb_ * Qd(n * e_i / Phi) * Qsec(n, Phis, TpS, rdS) - D2 * n * n


def opt2(Phi, Phis, ncap=math.inf):
    hi = min(Phi / e_i, TpS * Phis, ncap) * (1 - 1e-12)
    rr2 = optimize.minimize_scalar(lambda n: -EV2(n, Phi, Phis, ncap), bounds=(0, hi), method="bounded",
                                   options={"xatol": 1e-13})
    cand = [(rr2.x, -rr2.fun)]
    if ncap < math.inf:
        cand.append((ncap, EV2(ncap, Phi, Phis, ncap)))
    return max(cand, key=lambda z: z[1])


n2s, EV2s = opt2(Phi0, PhisS)
x2 = n2s * e_i / Phi0
nu2 = n2s / TpS
Vdep = pi0 * Vb_ * Qd(x2)                    # value per deployment net of decision congestion
hP = 1e-5
dPhi = (opt2(Phi0 * (1 + hP), PhisS)[1] - opt2(Phi0 * (1 - hP), PhisS)[1]) / (2 * hP * Phi0)
dPhis = (opt2(Phi0, PhisS * (1 + hP))[1] - opt2(Phi0, PhisS * (1 - hP))[1]) / (2 * hP * PhisS)
pred_Phi = n2s * pi0 * Vb_ * Qd(x2) * Qsec(n2s, PhisS, TpS, rdS) / Phi0 * (c_dec * x2 / (1 - x2) ** 2)
secvalue = nu2 * Vdep * rdS / (PhisS - nu2 + rdS) ** 2     # core eq:tasks-secvalue at nu = n*/T_par, V_dep
nh2 = optimize.minimize_scalar(lambda n: -n * Qd(n * e_i / Phi0) * Qsec(n, PhisS, TpS, rdS),
                               bounds=(1e-9, min(Phi0 / e_i, TpS * PhisS) * (1 - 1e-12)), method="bounded",
                               options={"xatol": 1e-12}).x
print(f"     -> two review capacities (Phi = 10, Phi_sec = 20 reviews a year, T_par = 0.5, r_d = 0.5): breakpoints "
      f"decision-only {xhat * Phi0 / e_i:.2f}, security-only {TpS * nu_hat_sec(PhisS, rdS):.2f}, combined {nh2:.2f}; "
      f"n* = {n2s:.2f} (vs {ns:.2f} without security review); shadow values: decision unit {dPhi:.3f}, "
      f"review a year {dPhis / TpS:.4f} per year (eq:tasks-secvalue {secvalue:.4f})")
# square-root rule of prop:tasks-secreview(c), given n*: at Phi*_sec the per-year shadow value equals p_sec
p_sec = 0.05
Phis_star = nu2 - rdS + math.sqrt(nu2 * Vdep * rdS / p_sec)
dEV_at_star = n2s * pi0 * Vb_ * Qd(x2) * rdS / (Phis_star - nu2 + rdS) ** 2 / TpS
check("F11 rem:ext-seccap(b): envelope shadow values: dEV*/dPhi = [n* varpi0 V Q Q_sec/Phi] eps_Q, and per year "
      "(1/T_par) dEV*/dPhi_sec = eq:tasks-secvalue with nu = n*/T_par and V_dep = varpi0 V Q; given n*, the square-root "
      "rule of prop:tasks-secreview(c) equates it to p_sec",
      abs(dPhi - pred_Phi) < 1e-4 * (1 + pred_Phi) and abs(dPhis / TpS - secvalue) < 1e-4 * (1 + secvalue)
      and abs(dEV_at_star - p_sec) < 1e-12 and n2s < ns and nh2 < min(xhat * Phi0 / e_i, TpS * nu_hat_sec(PhisS, rdS)),
      f"n*={n2s:.3f}, dEV/dPhi={dPhi:.4f} vs {pred_Phi:.4f}; per-year dEV/dPhi_sec={dPhis / TpS:.4f} vs {secvalue:.4f}")
REM_SEC = dict(n_dec=xhat * Phi0 / e_i, n_sec=TpS * nu_hat_sec(PhisS, rdS), n_comb=nh2, n_star=n2s, n_star0=ns,
               dPhi=dPhi, dPhis=dPhis / TpS)
check("F11b example quoted after rem:ext-seccap: breakpoints 7.0 (decision only), 8.6 (security only), 6.8 (both); "
      "optimum 6.8 -> 6.5; decision unit 0.78 -> 0.61; review capacity 0.17 a year",
      round(REM_SEC["n_dec"], 1) == 7.0 and round(REM_SEC["n_sec"], 1) == 8.6 and round(nh2, 1) == 6.8
      and round(ns, 1) == 6.8 and round(n2s, 1) == 6.5 and round(dEV, 2) == 0.78 and round(dPhi, 2) == 0.61
      and round(dPhis / TpS, 2) == 0.17)
# change capacity: hard cap n <= n_cap with multiplier zeta = varpi0 V Q Q_sec (1 - eps) - C'(n_cap) when it binds
okcc = True
for ncap_ in (4.0, 6.0, 9.0):
    nn_, vv_ = opt2(Phi0, PhisS, ncap_)
    binds = abs(nn_ - ncap_) < 1e-6
    hh_ = 1e-5
    dcap = (opt2(Phi0, PhisS, ncap_ + hh_)[1] - opt2(Phi0, PhisS, ncap_ - hh_)[1]) / (2 * hh_)
    if binds:
        xx = ncap_ * e_i / Phi0
        zeta = (pi0 * Vb_ * Qd(xx) * Qsec(ncap_, PhisS, TpS, rdS) * (1 - c_dec * xx / (1 - xx) ** 2
                                                                     - eps_sec(ncap_, PhisS, TpS, rdS)) - 2 * D2 * ncap_)
        okcc &= zeta > 0 and abs(dcap - zeta) < 1e-4 * (1 + zeta)
    else:
        okcc &= abs(dcap) < 1e-6
check("F12 rem:ext-seccap(b): change capacity, a hard cap, has shadow value zeta T_par/a with zeta = varpi0 V Q Q_sec "
      "(1 - eps_Q - eps_sec) - C^dr'(n_cap) when it binds and none when it is slack; review capacities keep positive "
      "shadow values either way", okcc and dPhi > 0 and dPhis > 0)


# hard caps (rem:ext-seccap(c)): relaxed wave problem with n_k <= nbar = min(K_chg T_par/a, Phi/e, T_par Phi_sec)
def Cstar(nbar, Nw=4, Ntot=12.0, Wp=1.0, Tp_=0.5, c1=0.2, c2=0.25):
    """relaxed program cost with n_w = Nw waves: min sum_k T_par (W k n_k + c1 n_k + c2 n_k^2), sum n_k = N,
    0 <= n_k <= nbar; solved exactly by bisection on the multiplier of sum n_k = N"""
    def sizes(lam):
        return [min(nbar, max(0.0, (lam / Tp_ - Wp * k - c1) / (2 * c2))) for k in range(1, Nw + 1)]
    lo, hi = 0.0, 1e4
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if sum(sizes(mid)) < Ntot else (lo, mid)
    lam = 0.5 * (lo + hi)
    nk = sizes(lam)
    cost = sum(Tp_ * (Wp * k * n + c1 * n + c2 * n * n) for k, n in zip(range(1, Nw + 1), nk))
    zetas = [max(0.0, lam - Tp_ * (Wp * k + c1 + 2 * c2 * nbar)) if abs(n - nbar) < 1e-9 else 0.0
             for k, n in zip(range(1, Nw + 1), nk)]
    return cost, nk, sum(zetas)


def C_caps(Kc, Phi_, Phis_, a_=40.0, e_=1.0, Tp_=0.5):
    return Cstar(min(Kc * Tp_ / a_, Phi_ / e_, Tp_ * Phis_))[0]


okh = True
grid_nb = np.linspace(3.2, 6.0, 15)
vals_nb = [Cstar(x)[0] for x in grid_nb]
okh &= all(vals_nb[i] >= vals_nb[i + 1] - 1e-12 for i in range(len(vals_nb) - 1))           # nonincreasing
okh &= all(vals_nb[i - 1] + vals_nb[i + 1] - 2 * vals_nb[i] >= -1e-9 for i in range(1, len(vals_nb) - 1))   # convex
c4, nk4, z4 = Cstar(4.0)
okh &= np.allclose(nk4, [4.0, 4.0, 3.0, 1.0]) and abs(z4 - 1.0) < 1e-9
dnb = (Cstar(4.0 + 1e-6)[0] - Cstar(4.0 - 1e-6)[0]) / 2e-6
okh &= abs(-dnb - z4) < 1e-5
# change capacity binds alone: K_chg = 320 -> 4; Phi/e = 5; T_par Phi_sec = 6
h_ = 1e-4
sK = -(C_caps(320 + h_, 5.0, 12.0) - C_caps(320 - h_, 5.0, 12.0)) / (2 * h_)
sP = -(C_caps(320, 5.0 + h_, 12.0) - C_caps(320, 5.0 - h_, 12.0)) / (2 * h_)
sS = -(C_caps(320, 5.0, 12.0 + h_) - C_caps(320, 5.0, 12.0 - h_)) / (2 * h_)
okh &= abs(sK - z4 * 0.5 / 40.0) < 1e-6 and abs(sP) < 1e-9 and abs(sS) < 1e-9
# security review binds alone: T_par Phi_sec = 4 < Phi/e = 5 < K_chg T_par/a = 6
sK2 = -(C_caps(480 + h_, 5.0, 8.0) - C_caps(480 - h_, 5.0, 8.0)) / (2 * h_)
sS2 = -(C_caps(480, 5.0, 8.0 + h_) - C_caps(480, 5.0, 8.0 - h_)) / (2 * h_)
okh &= abs(sK2) < 1e-9 and abs(sS2 - z4 * 0.5) < 1e-6
# tie: K_chg T_par/a = Phi/e = 4; raising either alone is worth nothing, raising both is worth z4 per unit of n-bar
up_one = C_caps(320 + 1e-3, 4.0, 12.0) - C_caps(320, 4.0, 12.0)
up_both = (C_caps(320 + 80 * 1e-3, 4.0 + 1e-3, 12.0) - C_caps(320, 4.0, 12.0)) / 1e-3
okh &= abs(up_one) < 1e-12 and abs(up_both + z4) < 1e-3
print(f"     -> hard caps: n-bar = 4 gives sizes {nk4} and -dC*/dn-bar = {z4:.2f}; shadow value per affected FTE a year "
      f"{sK:.4f}, per decision unit {sP:.4f}, per review a year {sS:.4f} (change capacity binding); "
      f"per review a year {sS2:.4f} when security review binds")
check("F13 rem:ext-seccap(c): with hard caps the relaxed program cost C*(n-bar) is convex and nonincreasing, "
      "-C*' = sum zeta_k, and only the capacity that attains min(K_chg T_par/a, Phi/e, T_par Phi_sec) has value "
      "(sum zeta_k times T_par/a, 1/e or T_par); at a tie raising one capacity alone is worth nothing", okh)

# ==============================================================================================
header("G. Breakpoints in this section (prop:ext-breaks)")
# ==============================================================================================
# regulatory class boundary with an assistive exemption: A -> U switch
exr = dict(ex); exr["O"] = False
Pr = dict(BASE); Pr["ximin"] = {0: 0.9, 1: 0, 2: 0.1}
mc0 = mode_costs(exr, BASE)
mc1 = mode_costs(exr, Pr)
best0 = min(("A", "U"), key=lambda Z: mc0[Z][0])
best1 = min(("A", "U"), key=lambda Z: mc1[Z][0])
jump = mc1["A"][0] - mc0["A"][0]
loss = min(mc1["A"][0], mc1["U"][0]) - mc0["A"][0]
J_exact = quality_cost(0.9, 57.2, 0.25, 0.10, 17.69) - quality_cost(0.15, 57.2, 0.25, 0.10, 17.69)
check("G1 prop:ext-breaks(c): a class boundary raises c_A by J = c^Q(xi_min') - c^Q(xi*) <= what t^R (xi_min' - xi*)_+; "
      "where the assistive mode is exempt, the optimal mode switches A -> U and the value loss is min(J, c_U - c_A)",
      abs(jump - J_exact) < 1e-9 and jump <= 57.2 * 0.25 * (0.9 - 0.15) and best0 == "A" and best1 == "U"
      and abs(loss - min(jump, mc0["U"][0] - mc0["A"][0])) < 1e-9, f"J={jump:.2f} (bound {57.2 * 0.25 * 0.75:.2f}), "
                                                                    f"loss={loss:.2f}")
Tsolo = optimize.brentq(lambda t_: 8.0 * ((1 - min(0.95, 0.5 + 0.12 * t_)) / (1.3 + 0.2 * t_) + min(0.95, 0.5 + 0.12 * t_)
                                         * 0.2 * math.exp(-0.35 * t_)) - 1.0, 0, 30)
print(f"     -> solo date for an 8 person-year scope (illustrative paths): {Tsolo:.2f} years")
check("G2 prop:ext-breaks(a): the solo date solves W(t) = 1 and is unique when W is decreasing",
      Tsolo > 0 and all(8.0 * ((1 - min(0.95, 0.5 + 0.12 * t_)) / (1.3 + 0.2 * t_) + min(0.95, 0.5 + 0.12 * t_) * 0.2
                                * math.exp(-0.35 * t_)) > 1 for t_ in np.linspace(0, Tsolo - 1e-6, 50)))

# ==============================================================================================
header("H. Consistency of numbers quoted in theory_ext.tex, and further claims")
# ==============================================================================================
# tab:ext-tornado is read from theory_ext.tex itself, so the check compares the printed table with the script
import os
import re
TEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "part2", "theory_ext.tex")
TEX = open(TEX_PATH, encoding="utf-8").read()
ex_strings = [f"costs \\${cA:.2f} at $\\tau=0.21$ and $\\psi=1$", f"$\\mathcal B=\\${Bex:.2f}$ a ticket",
              f"\\${Bex:.2f} million a year", f"to \\${Balt:.2f}", f"from \\${BexH:.2f} to \\${BaltH:.2f}",
              f"$\\xi^{{\\min*}}={xmin_exact:.2f}$", f"={xmin_bound:.2f}$", "inversely proportional to the growth weight: \\extXbRetOne, \\extXbRetTwo{} and \\extXbRetThree{} basis points",
              "% XBOUNDS: placeholder weights (macros extXb*", "$\\psi_{15}=0.532$", "12.4\\%"]
check("H0 support example and tax statements as printed in theory_ext.tex match the script (psi = 1 domestic)",
      all(x in TEX for x in ex_strings), [x for x in ex_strings if x not in TEX])
tab = TEX.split("\\label{tab:ext-tornado}")[1].split("\\bottomrule")[0].split("\\midrule")[1]
tex_rows = []
for line in tab.strip().split("\\\\"):
    cells = [c.strip() for c in line.split("&")]
    if len(cells) == 6:
        tex_rows.append((cells[0], float(cells[2]), float(cells[3]), float(cells[4]), float(cells[5])))
TORNADO_KEYS = ["Inference", "Altruism", "Payroll", "Readiness", "Customer", "Build", "Automation tax", "Ethics",
                "Oversight", "Profit tax", "Deductibility"]
oktt = len(tex_rows) == len(TORNADO) == len(TORNADO_KEYS)
for z, tr in zip(TORNADO, tex_rows):
    key = [k_ for k_ in TORNADO_KEYS if z[0].startswith(k_)]
    oktt &= len(key) == 1 and tr[0].startswith(key[0])
    oktt &= (abs(round(z[3], 3) - tr[1]) < 1e-9 and abs(round(z[4], 3) - tr[2]) < 1e-9
             and abs(round(100 * z[5], 1) - tr[3]) < 1e-9 and abs(round(100 * z[6], 1) - tr[4]) < 1e-9)
check("H1 tab:ext-tornado as printed in theory_ext.tex matches the script (values and order)", oktt,
      f"{len(tex_rows)} rows parsed")
wf_txt = (f"$\\Sigma^{{\\rm fea}}={Sb[0]:.3f}$, $\\Sigma^{{\\rm per}}={Sb[1]:.3f}$, $\\Sigma^{{\\rm pre}}={Sb[2]:.3f}$ and "
          f"$\\Sigma^{{\\rm eco}}={Sb[3]:.3f}$")
check("H2 waterfall quoted in the text (current law, psi = 1): 0.862, 0.824, 0.776, 0.742 and value 25.0% "
      "(string found in theory_ext.tex)",
      [round(x, 3) for x in Sb] == [0.862, 0.824, 0.776, 0.742] and round(100 * Vb, 1) == 25.0 and wf_txt in TEX
      and f"baseline {Sb[3]:.3f} and {100 * Vb:.1f}\\%" in TEX)
check("H3 Shapley example quoted in the text (current law): total and one-at-a-time sum as printed",
      f"rises by {100 * total:.1f} points" in TEX and f"sum to {100 * sum(oat):.1f} points" in TEX,
      f"total {100 * total:.4f}, OAT {100 * sum(oat):.4f}; " + "; ".join(f"{g[0]} {100 * p_:+.3f}"
                                                                         for g, p_ in zip(groups, phis)))
# learning with decay: E after one success k waves earlier
dE_, etr = 0.3, 0.6
E = 0.0
hist = []
for k_ in range(1, 7):
    succ = 1 if k_ == 1 else 0
    hist.append(E)
    E = (1 - dE_) * E + etr * succ
check("H4 prop:ext-portfolio(a): with E_{k+1} = (1-delta_E)E_k + eta_tr*successes, a success k waves earlier leaves "
      "E = eta_tr (1-delta_E)^(k-1)", all(abs(hist[k_] - etr * (1 - dE_) ** (k_ - 1)) < 1e-12 for k_ in range(1, 6)))
# capacity-weighted ordering: fractional relaxation fills earlier waves by s/a
okr = True
for _ in range(60):
    P_, K_ = 6, 3
    sv, av = RNG.uniform(0.2, 3, P_), RNG.uniform(0.5, 2, P_)
    cap = av.sum() / K_ * 1.05
    cvec = np.array([Tp * (k + 1) * sv[p_] for p_ in range(P_) for k in range(K_)])
    Aeq = np.zeros((P_, P_ * K_)); Aub = np.zeros((K_, P_ * K_))
    for p_ in range(P_):
        for k in range(K_):
            Aeq[p_, p_ * K_ + k] = 1; Aub[k, p_ * K_ + k] = av[p_]
    lp = optimize.linprog(cvec, A_ub=Aub, b_ub=np.full(K_, cap), A_eq=Aeq, b_eq=np.ones(P_), bounds=[(0, 1)] * (P_ * K_),
                          method="highs")
    order = np.argsort(-sv / av)
    rem = [cap] * K_
    val = 0.0
    k = 0
    for p_ in order:
        need = av[p_]
        while need > 1e-12:
            take = min(need, rem[k])
            val += Tp * (k + 1) * sv[p_] * take / av[p_]
            need -= take; rem[k] -= take
            if rem[k] <= 1e-12:
                k += 1
    okr &= abs(val - lp.fun) < 1e-7 * (1 + lp.fun)
check("H5 prop:ext-waves(a): with capacity weights, filling earlier waves in decreasing s_p/a_p solves the fractional "
      "relaxation (60 linear programs)", okr)
# contested region: an equilibrium with partial adoption exists
okc2 = True
for _ in range(300):
    n_c = int(RNG.integers(2, 9)); dd_ = RNG.uniform(0.01, 0.3)
    m_ = RNG.uniform((n_c - 1) * dd_ / (n_c + 1), 1.0)
    lo, hi = Epriv(m_, dd_, n_c, n_c - 1), Epriv(m_, dd_, n_c, 0)
    Kf = RNG.uniform(lo, hi)
    found = False
    for Mhat in range(1, n_c):
        if Epriv(m_, dd_, n_c, Mhat - 1) > Kf >= Epriv(m_, dd_, n_c, Mhat):
            found = True
    okc2 &= found
check("H6 prop:ext-should(a): in the contested region an equilibrium with M-hat adopters exists (300 draws)", okc2)
# capacity with front-loading: earliest waves at the cap, later waves keep the decrement
s9, d29, N9, K9, cap9 = 1.0, 0.25, 12, 4, 4.5
cons = [{"type": "eq", "fun": lambda x: np.sum(x) - N9}]
resc = optimize.minimize(lambda x: wave_cost(list(x), s9, Tp, d1, d29, 0.0), x0=np.full(K9, N9 / K9), constraints=cons,
                         bounds=[(0, cap9)] * K9, method="SLSQP", options={"ftol": 1e-14})
xc = resc.x
free = [i for i in range(K9) if xc[i] < cap9 - 1e-6]
okcap = all(xc[i] >= cap9 - 1e-6 for i in range(K9) if i < free[0]) and all(
    abs((xc[free[i]] - xc[free[i + 1]]) - s9 / (2 * d29)) < 1e-4 for i in range(len(free) - 1))
check("H7 prop:ext-waves(d): with a binding cap the earliest waves sit at the cap and later waves keep the decrement",
      okcap, f"sizes {np.round(xc, 3)}")
# agent pod cap
Ya_, cha = 3.0, 0.2
mm = optimize.minimize_scalar(lambda n: -(n * Ya_ - cha * n * (n - 1) / 2), bounds=(0, 100), method="bounded")
check("H8 prop:ext-team(g): agents' joint output is at most (Y_a + chi_a/2)^2/(2 chi_a)",
      abs(-mm.fun - (Ya_ + cha / 2) ** 2 / (2 * cha)) < 1e-6)
# heavy tails: P(X1+X2 > x)/P(X > x) -> 2 for a Lomax tail of index 2.3
zt, lam_l = 2.3, 1.0
sf = lambda x: (1 + x / lam_l) ** (-zt)
pdf = lambda x: zt / lam_l * (1 + x / lam_l) ** (-zt - 1)


def sum_sf(x):
    """P(X1 + X2 > x) = S(x/2)^2 + 2 int_0^{x/2} f(y) S(x - y) dy (symmetric split, smooth integrand)"""
    pts = [p_ for p_ in (1.0, 10.0, 100.0, 1000.0) if p_ < x / 2]
    return sf(x / 2) ** 2 + 2 * integrate.quad(lambda y: pdf(y) * sf(x - y), 0, x / 2, limit=1000, points=pts or None)[0]


ratios = [sum_sf(x) / sf(x) for x in (1e1, 1e2, 1e3, 1e4)]
check("H9 prop:ext-portfolio(d): P(X1 + X2 > x)/P(X > x) decreases to 2 for a power-law tail of index 2.3",
      all(ratios[i] > ratios[i + 1] for i in range(3)) and abs(ratios[-1] - 2) < 0.02 and ratios[-1] >= 2,
      f"ratios {[round(r_, 4) for r_ in ratios]}")
# tenfold condition
ok10 = True
for _ in range(5000):
    Ag, nu, psA = RNG.uniform(1, 2), RNG.uniform(0, 1), RNG.uniform(0, 0.5)
    if Wlev(Ag, nu, psA) >= 10:
        ok10 &= nu >= 0.8 - 1e-12 and psA <= 0.125 + 1e-12
check("H10 prop:ext-team(d): with A_g <= 2 a tenfold contributor requires nu_a >= 0.8 and xi^t <= 0.125", ok10)
# score dips rise with k when sizes are nonincreasing
okdip = True
for _ in range(200):
    sizes_ = sorted(RNG.integers(1, 8, size=4), reverse=True)
    dips_ = [(sum(sizes_[:k]) * 1.0 - (d1 * n + d2 * n * n)) for k, n in enumerate(sizes_)]
    okdip &= all(dips_[i] <= dips_[i + 1] + 1e-12 for i in range(3))
check("H11 prop:ext-waves(f): with nonincreasing wave sizes the margin change rises from wave to wave", okdip)


# after-tax envelope used in prop:ext-customer(a)
def Rstar_after(m0, Gi, lam, X, k, tau, psi, al=0.3, h=0.7):
    f = lambda sg: -(X * (Gi + lam * h * sg ** al) + (1 - tau) * (m0 - sg) - (1 - psi * tau) * k * (Gi + lam * h * sg ** al))
    r_ = optimize.minimize_scalar(f, bounds=(0, 50), method="bounded", options={"xatol": 1e-13})
    return -r_.fun


args = (0.40, 0.08, 0.6, 3.0, 0.3, 0.21, 0.6)
R0 = Rstar_after(*args)
eh = 1e-6
dRm = (Rstar_after(args[0] + eh, *args[1:]) - R0) / eh
dRG = (Rstar_after(args[0], args[1] + eh, *args[2:]) - R0) / eh
check("H12 prop:ext-customer(a): after-tax dR*/dm0 = 1 - tau and dR*/dG_i = X - (1 - psi tau) k",
      abs(dRm - 0.79) < 1e-4 and abs(dRG - (3.0 - (1 - 0.6 * 0.21) * 0.3)) < 1e-4, f"{dRm:.5f}, {dRG:.5f}")
# D-tilde convex where xQ is concave (M/M/1 latency), prop:ext-bandwidth(f)
xs_grid = np.linspace(0.01, xhat, 400)
xQ = xs_grid * np.exp(-c_ / (1 - xs_grid))
conc = np.all(np.diff(xQ, 2) <= 1e-12)
Dt = xs_grid - xQ
check("H13 prop:ext-bandwidth(f): with queueing latency x Q(x) is concave below x_hat, so x - xQ(x) is convex there",
      bool(conc) and bool(np.all(np.diff(Dt, 2) >= -1e-12)))

# ==============================================================================================
header("I. Regime shocks: leadership, vision, reorganization, context (sec:ext-shocks)")
# ==============================================================================================
def Vshock(nu, F=10.0, S=4.0, r=0.10, Tpar=0.5, Temb=3.0, R=0.0):
    rD = r + nu
    sav = S * ((math.exp(-rD * Tpar) - math.exp(-rD * Temb)) / rD + math.exp(-rD * Temb) / r)
    rec = R * nu * (1 - math.exp(-rD * Temb)) / rD if nu > 0 else 0.0
    return -F + sav + rec


def Phi_pay(tau, S=4.0, r=0.10, Tpar=0.5, Temb=3.0, R=0.0):
    if tau >= Temb:
        return S * math.exp(-r * Tpar) / r
    sv = S * (math.exp(-r * Tpar) - math.exp(-r * tau)) / r if tau > Tpar else 0.0
    return sv + math.exp(-r * tau) * R


okv1 = True
for nu_ in (0.05, 0.3, 0.8):
    for R_ in (0.0, -1.0, 2.0):
        exact = -10 + Phi_pay(1e9, R=R_) * math.exp(-nu_ * 3.0) + integrate.quad(
            lambda t_: nu_ * math.exp(-nu_ * t_) * Phi_pay(t_, R=R_), 0, 3.0, points=[0.5], limit=200)[0]
        okv1 &= abs(exact - Vshock(nu_, R=R_)) < 1e-8
dr = RNG.exponential(1 / 0.3, 400000)
mc = -10 + np.mean(np.where(dr >= 3.0, Phi_pay(1e9), np.where(dr > 0.5, 4 * (math.exp(-0.05) - np.exp(-0.1 * dr)) / 0.1, 0.0)))
check("I1 prop:ext-shocks(a): closed form (eq:ext-Vshock) equals E[Phi(tau_D)] by quadrature; Monte Carlo within 0.1",
      okv1 and abs(mc - Vshock(0.3)) < 0.1, f"V(0)={Vshock(0):.2f}, V(0.3)={Vshock(0.3):.2f}, MC={mc:.2f}")
check("I2 example: $10m process saving $4m a year, T_par 0.5, T_emb 3: value 28.0 without shocks, 7.2 at nu_D = 0.3",
      abs(Vshock(0) - 28.05) < 0.01 and abs(Vshock(0.3) - 7.22) < 0.01)
okm2 = True
for _ in range(300):
    S_, r_s, Tp_, Te_ = RNG.uniform(1, 5), RNG.uniform(0.05, 0.15), RNG.uniform(0, 1), RNG.uniform(1, 5)
    R_ = RNG.uniform(-3, 0) if RNG.random() < 0.7 else 0.0
    vals = [Vshock(n_, S=S_, r=r_s, Tpar=Tp_, Temb=Tp_ + Te_, R=R_) for n_ in np.linspace(0, 2, 30)]
    okm2 &= all(vals[i] > vals[i + 1] for i in range(29))
check("I3 prop:ext-shocks(a): V strictly decreasing in nu_D when V_rec <= 0 (300 random processes)", okm2)
fdv = (Vshock(1e-7) - Vshock(0)) / 1e-7
expo = integrate.quad(lambda t_: Phi_pay(1e9) - Phi_pay(t_), 0, 3.0, points=[0.5])[0]
check("I4 prop:ext-shocks(a): dV/dnu_D at 0 equals minus the area of value at risk", abs(fdv + expo) < 1e-4 * expo,
      f"{fdv:.3f} vs {-expo:.3f}")
Tt, rDs, vb = sp.symbols("T r_D vbar", positive=True)
check("I5 prop:ext-shocks(b): vbar T e^{-r_D T} peaks at T = 1/r_D",
      zero(sp.diff(vb * Tt * sp.exp(-rDs * Tt), Tt).subs(Tt, 1 / rDs)) and
      sp.diff(vb * Tt * sp.exp(-rDs * Tt), Tt, 2).subs(Tt, 1 / rDs).subs({vb: 1, rDs: 0.3}) < 0)
ten_bp = 1 / ((1 / 3 - 0.10 - 0.05) / 0.5)
check("I6 example: with kappa_keep 0.5, nu_V 0.05, r 0.10, a 3-year window passes the breakpoint below 2.7 years of tenure",
      abs(ten_bp - 2.727) < 1e-3)


def seq_value(order, Vs, taus, rD):
    t_, tot = 0.0, 0.0
    for i in order:
        t_ += taus[i]
        tot += Vs[i] * math.exp(-rD * t_)
    return tot


oks2 = True
for _ in range(200):
    nj = 5
    Vs, taus, rD = RNG.uniform(0.5, 10, nj), RNG.uniform(0.2, 4, nj), RNG.uniform(0.02, 1.0)
    best_v = max(seq_value(o, Vs, taus, rD) for o in itertools.permutations(range(nj)))
    idx_order = sorted(range(nj), key=lambda i: -Vs[i] / (math.exp(rD * taus[i]) - 1))
    oks2 &= abs(seq_value(idx_order, Vs, taus, rD) - best_v) < 1e-9 * best_v
check("I7 prop:ext-shocks(c): ordering by V/(e^{r_D tau} - 1) is optimal (brute force, 200 instances of 5 processes)", oks2)
ix = lambda V_, t_, rD: V_ / (math.exp(rD * t_) - 1)
rsw = optimize.brentq(lambda rD: ix(2, 0.75, rD) - ix(10, 3, rD), 0.01, 2)
grid_r = np.linspace(0.01, 2, 400)
diffs = [ix(2, 0.75, g_) - ix(10, 3, g_) for g_ in grid_r]
check("I8 prop:ext-shocks(c): unique switch r_D* = 0.19 for a $2m, 9-month quick win against a $10m, 3-year process",
      abs(rsw - 0.187) < 1e-3 and sum(1 for i in range(399) if np.sign(diffs[i]) != np.sign(diffs[i + 1])) == 1)
dVs = (Vshock(0.3, R=0.787 * 10 + 1e-6 * 10 - 1) - Vshock(0.3, R=0.787 * 10 - 1)) / 1e-6
pred = 10 * (0.3 / 0.4) * (1 - math.exp(-0.4 * 3))
incr = all((n2 / (0.1 + n2)) * (1 - math.exp(-(0.1 + n2) * 3)) > (n1 / (0.1 + n1)) * (1 - math.exp(-(0.1 + n1) * 3))
           for n1, n2 in zip(np.linspace(0.01, 1, 50)[:-1], np.linspace(0.01, 1, 50)[1:]))
check("I9 prop:ext-shocks(d): dV/ds_reuse = (F+I)(nu/r_D)(1 - e^{-r_D T_emb}), increasing in nu_D",
      abs(dVs - pred) < 1e-5 * pred and incr)
# context stock: shot noise moments
nuK, etaK = 0.15, 1.0


def sim_m(kdoc, nK, reps=60000):
    lam_ = nuK * nK
    j_ = (1 - kdoc) / nK
    horizon = 25.0 / etaK
    counts = RNG.poisson(lam_ * horizon, reps)
    out = np.empty(reps)
    for i_ in range(reps):
        ages = RNG.uniform(0, horizon, counts[i_])
        out[i_] = 1 - j_ * np.exp(-etaK * ages).sum()
    return out


okm3 = True
for kd, nK in [(0.2, 3), (0.7, 3), (0.2, 30)]:
    sm = sim_m(kd, nK)
    m_pred = 1 - nuK * (1 - kd) / etaK
    v_pred = nuK * (1 - kd) ** 2 / (2 * etaK * nK)
    okm3 &= abs(sm.mean() - m_pred) < 4 * sm.std() / math.sqrt(len(sm)) + 1e-4 and abs(sm.var() - v_pred) < 0.05 * v_pred
check("I10 prop:ext-continuity(a): E[m] = 1 - nu_K(1-k_doc)/eta_K and Var = nu_K(1-k_doc)^2/(2 eta_K n_K) (simulation)", okm3)
check("I11 example: k_doc 0.2 -> 0.7 lifts E[m] from 0.88 to 0.955 (sd 0.13 -> 0.05 with 3 holders) and is worth $3.75m",
      abs(1 - nuK * 0.8 - 0.88) < 1e-12 and abs(1 - nuK * 0.3 - 0.955) < 1e-12
      and abs(math.sqrt(nuK * 0.64 / 6) - 0.126) < 5e-4 and abs(math.sqrt(nuK * 0.09 / 6) - 0.047) < 5e-4
      and abs(5 * nuK * 0.5 / (etaK * 0.10) - 3.75) < 1e-12)
# commitment devices
PVv = 1 - math.exp(-0.25 * 2)
Vp, Vm, Vr, pinf = 10.0, 4.0, 1.0, 0.3
no_dev = (1 - PVv) * Vp + PVv * (pinf * Vr + (1 - pinf) * Vr)          # continuation values: informative case continuation is -Vm
no_dev = (1 - PVv) * ((1 - pinf) * Vp + pinf * (-Vm)) + PVv * Vr
binding = (1 - pinf) * Vp + pinf * (-Vm)
gated = (1 - PVv) * ((1 - pinf) * Vp + pinf * (-Vm)) + PVv * ((1 - pinf) * Vp + pinf * Vr)
val_b = binding - no_dev
val_g = gated - no_dev
check("I12 prop:ext-continuity(b): binding device = P_V[(1-p)(V+ - Vrec) - p(V- + Vrec)] = 1.89; gated = P_V(1-p)(V+ - Vrec) = 2.48",
      abs(val_b - PVv * ((1 - pinf) * (Vp - Vr) - pinf * (Vm + Vr))) < 1e-12 and abs(val_g - PVv * (1 - pinf) * (Vp - Vr)) < 1e-12
      and abs(val_b - 1.889) < 1e-3 and abs(val_g - 2.479) < 1e-3)
# availability under freezes (alternating renewal)
nuR, Tfrz = 0.3, 0.25
tt_, up = 0.0, 0.0
while tt_ < 2e5:
    u_ = RNG.exponential(1 / nuR)
    up += u_
    tt_ += u_ + Tfrz
check("I13 prop:ext-continuity(c): share of time available = 1/(1 + nu_R T_frz) (renewal simulation)",
      abs(up / tt_ - 1 / (1 + nuR * Tfrz)) < 3e-3, f"{up / tt_:.4f} vs {1 / (1 + nuR * Tfrz):.4f}")
# freeze cost: exact first-order accounting on the wave plan
sizes_f = [6, 4, 2]
Ore = 0.8


def cost_with_freeze(sizes, k_hit):
    """program cost when one freeze of length T_frz hits wave k_hit (0-based)"""
    base = wave_cost(sizes, s_w, Tp, d1, d2, Ow)
    extra = Tfrz * (d1 * sizes[k_hit] + d2 * sizes[k_hit] ** 2) + Tfrz * s_w * sum(sizes[k_hit:]) + Ore
    return base + extra


first_order = sum(Tp * (cost_with_freeze(sizes_f, k) - wave_cost(sizes_f, s_w, Tp, d1, d2, Ow)) for k in range(3))
formula = Tfrz * (wave_cost(sizes_f, s_w, Tp, d1, d2, Ow) - 3 * Ow) + Tp * 3 * Ore
check("I14 prop:ext-continuity(d): expected freeze cost per unit hazard = T_frz (C_prog - K O_w) + T_par K O_re",
      abs(first_order - formula) < 1e-12)
okn3 = True
for _ in range(300):
    s_, N_, Tp2, d2_, Ow_, Ore_, Tf_, nu_ = (RNG.uniform(0.5, 2), 12, RNG.uniform(0.25, 1), RNG.uniform(0.05, 0.5),
                                             RNG.uniform(0.1, 2), RNG.uniform(0.1, 3), RNG.uniform(0.1, 1), RNG.uniform(0.05, 0.5))
    def cfr(n, nu_=nu_):
        return (1 + nu_ * Tf_) * Tp2 * (s_ * N_ ** 2 / (2 * n) + s_ * N_ / 2 + d1 * N_ + d2_ * N_ * n) + (N_ / n) * (Ow_ + nu_ * Tp2 * Ore_)
    n0 = optimize.minimize_scalar(lambda n: cfr(n, 0.0), bounds=(0.1, 200), method="bounded").x
    n1_ = optimize.minimize_scalar(lambda n: cfr(n), bounds=(0.1, 200), method="bounded").x
    pred_n = math.sqrt((s_ * N_ / 2 + (Ow_ + nu_ * Tp2 * Ore_) / ((1 + nu_ * Tf_) * Tp2)) / d2_)
    okn3 &= abs(n1_ - pred_n) < 1e-3 * pred_n and ((n1_ > n0) == (Tp2 * Ore_ > Tf_ * Ow_))
check("I15 prop:ext-continuity(d): freeze-adjusted square-root rule; freezes favor fewer waves iff T_par O_re > T_frz O_w "
      "(300 draws)", okn3)
ns_ = 4
coupled = nuR * Tfrz * 10.0
decoupled = sum((nuR / ns_) * Tfrz * (10.0 / ns_ * ns_) / ns_ for _ in range(ns_))
check("I16 prop:ext-continuity(d): unit-specific freezes over n_s decoupled streams cost 1/n_s of program-wide freezes",
      abs(decoupled - coupled / ns_) < 1e-12)

# ----------------------------------------------------------------------------------------------
# ==============================================================================================
header("J. Common-mode failure, model diversity and governance (prop:ext-portfolio(e), prop:ext-commonmode)")
# ==============================================================================================
# prop:ext-portfolio(e): waves on M providers, each sound w.p. p_P independently; n_m waves on provider m
okj1 = True
for alloc in ([5], [3, 2], [2, 2, 1], [1, 1, 1, 1, 1]):
    nw_, M_ = sum(alloc), len(alloc)
    Hn = sum((n_ / nw_) ** 2 for n_ in alloc)
    var_pred = pP * nw_ * pi_ * (1 - pi_) + nw_ ** 2 * pi_ ** 2 * pP * (1 - pP) * Hn
    sims_ = np.zeros(200000)
    for n_ in alloc:
        good = RNG.random(200000) < pP
        sims_ += np.where(good, RNG.binomial(n_, pi_, 200000), 0)
    pz = np.mean(sims_ == 0)
    okj1 &= abs(np.var(sims_) - var_pred) < 0.02 * var_pred and pz >= (1 - pP) ** M_ - 3e-3
check("J1 prop:ext-portfolio(e): with M providers, Var(successes) = p_P n_w varpi(1-varpi) + n_w^2 varpi^2 p_P(1-p_P) H_n "
      "and Pr(no success) >= (1-p_P)^M (Monte Carlo, four allocations)", okj1)


def cm_mean(Xs, nu, Tc, Yf, kfo=1.0):
    return nu * Tc * sum(kfo * x + (kfo * x) ** 2 / (2 * Yf) for x in Xs)


def cm_var(Xs, nu, Tc, Yf):
    return nu * Tc ** 2 * sum((x + x * x / (2 * Yf)) ** 2 for x in Xs)


# (a) compound Poisson mean and variance by simulation; Schur-convexity (more unequal shares cost more)
Xs_a, nu_a, Tc_a, Yf_a = [12.0, 6.0, 2.0], 2.0, 0.01, 10.0
draws_ = sum(RNG.poisson(nu_a, 400000) * Tc_a * (x + x * x / (2 * Yf_a)) for x in Xs_a)
Htot = sum((x / sum(Xs_a)) ** 2 for x in Xs_a)
okj2 = abs(draws_.mean() - cm_mean(Xs_a, nu_a, Tc_a, Yf_a)) < 0.01 * cm_mean(Xs_a, nu_a, Tc_a, Yf_a)
okj2 &= abs(draws_.var() - cm_var(Xs_a, nu_a, Tc_a, Yf_a)) < 0.02 * cm_var(Xs_a, nu_a, Tc_a, Yf_a)
okj2 &= abs(cm_mean(Xs_a, nu_a, Tc_a, Yf_a) - nu_a * Tc_a * (20 + Htot * 400 / (2 * Yf_a))) < 1e-12
for _ in range(300):        # a Robin Hood transfer (less unequal) lowers mean and variance
    k_ = int(RNG.integers(2, 6))
    xs0 = sorted(RNG.uniform(0.5, 10, k_), reverse=True)
    tr = RNG.uniform(0, (xs0[0] - xs0[-1]) / 2)
    xs1 = list(xs0); xs1[0] -= tr; xs1[-1] += tr
    okj2 &= cm_mean(xs1, 1, 1, 5) <= cm_mean(xs0, 1, 1, 5) + 1e-12 and cm_var(xs1, 1, 1, 5) <= cm_var(xs0, 1, 1, 5) + 1e-12
check("J2 prop:ext-commonmode(a): annual common-mode cost has mean nu T_con [X + H X^2/(2Y_f)] and variance "
      "nu T_con^2 sum (X_m + X_m^2/(2Y_f))^2 (simulation); both fall under transfers that equalize shares", okj2)
# (b) diversity, variance ratio and redundancy
okj3 = True
for _ in range(300):
    X_, nu_, Tc_, Yf_, M_ = RNG.uniform(1, 50), RNG.uniform(0.2, 5), RNG.uniform(0.002, 0.05), RNG.uniform(1, 40), \
        int(RNG.integers(2, 8))
    save = cm_mean([X_], nu_, Tc_, Yf_) - cm_mean([X_ / M_] * M_, nu_, Tc_, Yf_)
    okj3 &= abs(save - nu_ * Tc_ * X_ ** 2 * (1 - 1 / M_) / (2 * Yf_)) < 1e-9 * (1 + save)
    okj3 &= cm_var([X_ / M_] * M_, nu_, Tc_, Yf_) <= cm_var([X_], nu_, Tc_, Yf_) / M_ + 1e-12
    kf = RNG.uniform(0, 1)
    Xs_r = list(RNG.uniform(0.5, 10, 3))
    H_r = sum((x / sum(Xs_r)) ** 2 for x in Xs_r)
    red = cm_mean(Xs_r, nu_, Tc_, Yf_) - cm_mean(Xs_r, nu_, Tc_, Yf_, kfo=kf)
    pred_r = nu_ * Tc_ * ((1 - kf) * sum(Xs_r) + (1 - kf ** 2) * H_r * sum(Xs_r) ** 2 / (2 * Yf_))
    okj3 &= abs(red - pred_r) < 1e-9 * (1 + red)
check("J3 prop:ext-commonmode(b): equal split over M providers saves nu T_con X^2 (1 - 1/M)/(2 Y_f) and divides the "
      "variance by at least M; failover with residual share kappa_fo is worth nu T_con[(1-k)X + (1-k^2) H X^2/(2Y_f)]", okj3)


# (c) scale against diversification: brute force over M
def J_cost(M_, Cinf, bv, FM, K_, Xlin):
    return Cinf * M_ ** bv + M_ * FM + Xlin + K_ / M_            # K_ = nu T_con X^2/(2 Y_f), Xlin = nu T_con X


def M_rule(Cinf, bv, FM, K_):
    M_ = 1
    while K_ > M_ * (M_ + 1) * (FM + Cinf * ((M_ + 1) ** bv - M_ ** bv)):
        M_ += 1
    return M_


okj4 = True
for _ in range(500):
    Cinf, bv, FM, K_ = RNG.uniform(0, 20), RNG.choice([0.0, RNG.uniform(0, 0.6)]), RNG.uniform(0.01, 2), \
        math.exp(RNG.uniform(math.log(0.01), math.log(200)))
    Mb = min(range(1, 400), key=lambda m: J_cost(m, Cinf, bv, FM, K_, 0.0))
    okj4 &= M_rule(Cinf, bv, FM, K_) == Mb
    okj4 &= (Mb == 1) == (K_ / 2 <= FM + Cinf * (2 ** bv - 1))
    if bv == 0.0:
        Md = math.sqrt(K_ / FM)
        okj4 &= Mb in (max(1, math.floor(Md)), max(1, math.ceil(Md)))
    # single crossing: M(M+1)[(M+1)^b - M^b] is increasing
    hh_ = [m * (m + 1) * ((m + 1) ** bv - m ** bv) for m in range(1, 60)]
    okj4 &= all(hh_[i + 1] >= hh_[i] - 1e-12 for i in range(len(hh_) - 1))
# example quoted in the text: X = 20, nu = 2, T_con = 0.01, Y_f = 10, F_M = 0.15; volume discounts b_v = 0.1 on C_inf = 3
X_e, nu_e, Tc_e, Yf_e, FM_e, Ci_e, bv_e = 20.0, 2.0, 0.01, 10.0, 0.15, 3.0, 0.1
K_e = nu_e * Tc_e * X_e ** 2 / (2 * Yf_e)
cm1, cm2 = cm_mean([X_e], nu_e, Tc_e, Yf_e), cm_mean([X_e / 2] * 2, nu_e, Tc_e, Yf_e)
Mnod, Mdisc = M_rule(0.0, 0.0, FM_e, K_e), M_rule(Ci_e, bv_e, FM_e, K_e)
print(f"     -> common mode: expected cost one provider {cm1:.2f}, two {cm2:.2f} ($M/yr); M* without discounts {Mnod} "
      f"(M-dagger {math.sqrt(K_e / FM_e):.2f}); with volume discounts b_v = 0.1 on $3M: {Mdisc}; "
      f"threshold F_M + C(2^b - 1) = {FM_e + Ci_e * (2 ** bv_e - 1):.3f} vs K/2 = {K_e / 2:.2f}")
check("J4 prop:ext-commonmode(c): the optimal number of providers is the smallest M with nu T X^2/(2Y_f) <= "
      "M(M+1)[F_M + C_inf((M+1)^b - M^b)] (brute force, 500 draws); one provider iff nu T X^2/(4Y_f) <= F_M + C_inf(2^b - 1); "
      "without discounts the optimum is next to sqrt(nu T X^2/(2 Y_f F_M)); example: 0.80 -> 0.60, M* = 2, one provider "
      "with volume discounts", okj4 and abs(cm1 - 0.80) < 1e-9 and abs(cm2 - 0.60) < 1e-9 and Mnod == 2 and Mdisc == 1)


# (d) staged release of a model update
def ev_stage(eta, pg, Bup, dc, Tc, X, Yf):
    return pg * Bup * (1 - (1 - eta) * dc) - (1 - pg) * Tc * (eta * X + (eta * X) ** 2 / (2 * Yf))


def eta_star(pg, Bup, dc, Tc, X, Yf, emin):
    return min(1.0, max(emin, (Yf / X) * (pg * Bup * dc / ((1 - pg) * Tc * X) - 1)))


okj5 = True
for _ in range(400):
    pg, Bup, dc, Tc, X_, Yf_, emin = (RNG.uniform(0.5, 0.99), RNG.uniform(0.05, 5), RNG.uniform(0.01, 0.5),
                                      RNG.uniform(0.002, 0.1), RNG.uniform(1, 40), RNG.uniform(1, 40), 0.02)
    grid_e = np.linspace(emin, 1, 20001)
    vals_e = ev_stage(grid_e, pg, Bup, dc, Tc, X_, Yf_)
    es = eta_star(pg, Bup, dc, Tc, X_, Yf_, emin)
    okj5 &= ev_stage(es, pg, Bup, dc, Tc, X_, Yf_) >= vals_e.max() - 1e-9
    okj5 &= (es == 1.0) == (pg * Bup * dc >= (1 - pg) * Tc * X_ * (1 + X_ / Yf_))
pg_e, Bup_e, dc_e = 0.9, 0.5, 0.1
es_e = eta_star(pg_e, Bup_e, dc_e, Tc_e, X_e, Yf_e, 0.02)
gain_e = ev_stage(es_e, pg_e, Bup_e, dc_e, Tc_e, X_e, Yf_e) - ev_stage(1.0, pg_e, Bup_e, dc_e, Tc_e, X_e, Yf_e)
Treb = 0.05
roll_e = (1 - pg_e) * (Treb - Tc_e) * (es_e * X_e + (es_e * X_e) ** 2 / (2 * Yf_e))
print(f"     -> staged update (B_up 0.5, p_g 0.9, delay cost 10%): eta* = {es_e:.3f}, gain over a full release "
      f"{1000 * gain_e:.1f} $k; rollback path worth {1000 * roll_e:.1f} $k per update (rebuild 0.05 yr)")
check("J5 prop:ext-commonmode(d): the staged-release value is concave and maximized at the truncated closed form; "
      "a full release is optimal iff p_g B_up delta_c >= (1-p_g) T_con X (1 + X/Y_f) (400 draws); example eta* = 0.625, "
      "rollback path worth $81k per update",
      okj5 and abs(es_e - 0.625) < 1e-12 and round(1000 * roll_e) == 81)
# (e) kill switch, substitutes, and the decision-rights wedge
Tresp, Tks = 0.008, 0.001
ks1 = nu_e * (Tresp - Tks) * (X_e + 1.0 * X_e ** 2 / (2 * Yf_e))
ks2 = nu_e * (Tresp - Tks) * (X_e + 0.5 * X_e ** 2 / (2 * Yf_e))
Hs, Ts = sp.symbols("H T_con", positive=True)
mean_s = sp.Symbol("nu") * Ts * (sp.Symbol("X") + Hs * sp.Symbol("X") ** 2 / (2 * sp.Symbol("Y_f")))
cross = sp.diff(mean_s, Hs, Ts)
okj6 = zero(cross - sp.Symbol("nu") * sp.Symbol("X") ** 2 / (2 * sp.Symbol("Y_f"))) and ks1 > ks2
# wedge: unit bears T x_u (1 + X_m/(2Y_f)) per event; firm bears T (X_m + X_m^2/(2Y_f))
for _ in range(300):
    xs_u = RNG.uniform(0.1, 5, int(RNG.integers(2, 8)))
    nu_, Tc_, Yf_ = RNG.uniform(0.5, 4), RNG.uniform(0.002, 0.05), RNG.uniform(1, 30)
    Xm = xs_u.sum()
    h_ = 1e-6
    unit_c = lambda x0: nu_ * Tc_ * x0 * (1 + (Xm - xs_u[0] + x0) / (2 * Yf_))
    firm_c = lambda x0: nu_ * Tc_ * ((Xm - xs_u[0] + x0) + (Xm - xs_u[0] + x0) ** 2 / (2 * Yf_))
    du = (unit_c(xs_u[0] + h_) - unit_c(xs_u[0] - h_)) / (2 * h_)
    df = (firm_c(xs_u[0] + h_) - firm_c(xs_u[0] - h_)) / (2 * h_)
    okj6 &= abs((df - du) - nu_ * Tc_ * (Xm - xs_u[0]) / (2 * Yf_)) < 1e-6
# symmetric units with benefit a_b x - x^2/(2 g_b): Nash exposure exceeds the firm optimum; the charge restores it
nU, ab, gb = 5, 0.2, 2.0
nuT = nu_e * Tc_e
x_opt = optimize.brentq(lambda x: (ab - x / gb) - nuT * (1 + nU * x / Yf_e), 0, ab * gb)
x_nash = optimize.brentq(lambda x: (ab - x / gb) - nuT * (1 + (nU + 1) * x / (2 * Yf_e)), 0, ab * gb)
charge = nuT * (nU - 1) * x_opt / (2 * Yf_e)
x_br = optimize.brentq(lambda x: (ab - x / gb) - nuT * (1 + ((nU - 1) * x_opt + x) / (2 * Yf_e) + x / (2 * Yf_e)) - charge,
                       0, ab * gb)
okj6 &= x_nash > x_opt and abs(x_br - x_opt) < 1e-10
print(f"     -> kill switch (response 0.008 -> 0.001 yr): worth {ks1:.3f} $M/yr on one provider, {ks2:.3f} on two; "
      f"charge with many small units {nuT * X_e / (2 * Yf_e):.3f} per $ of exposure; Nash {x_nash:.3f} vs optimum {x_opt:.3f}")
check("J6 prop:ext-commonmode(e): kill switch worth nu (T_resp - T_ks)[X + H X^2/(2Y_f)], more under concentration "
      "(positive cross-partial in H and T_con); a unit's marginal cost falls short of the firm's by nu T_con (X_m - x_u)/(2Y_f); "
      "Nash exposure is too high and the internal charge restores the optimum; example 0.56 and 0.42 $M a year, "
      "wedge 0.02 against a firm marginal cost of 0.06, M-dagger 1.63",
      okj6 and abs(ks1 - 0.56) < 1e-9 and abs(ks2 - 0.42) < 1e-9 and abs(nuT * X_e / (2 * Yf_e) - 0.02) < 1e-12
      and abs(nuT * (1 + X_e / Yf_e) - 0.06) < 1e-12 and round(math.sqrt(K_e / FM_e), 2) == 1.63)
# J7 change management: nu^cm = nu^out + nu^chg(kappa); the mean of (a) is linear in nu^cm, so d mean/d kappa =
# nu^chg'(kappa) T_con [X + H X^2/(2 Y_f)], larger with H and T_con
okj7 = True
for _ in range(300):
    nuo, nc0, slope = RNG.uniform(0.1, 3), RNG.uniform(0.1, 3), RNG.uniform(0.1, 2)
    Tc_, X_, Yf_, H_ = RNG.uniform(0.002, 0.05), RNG.uniform(1, 50), RNG.uniform(1, 30), RNG.uniform(0.2, 1)
    nuchg = lambda kq: nc0 * math.exp(-slope * kq)
    mean_k = lambda kq: (nuo + nuchg(kq)) * Tc_ * (X_ + H_ * X_ ** 2 / (2 * Yf_))
    kq, hq = RNG.uniform(0, 2), 1e-6
    num_d = (mean_k(kq + hq) - mean_k(kq - hq)) / (2 * hq)
    pred = -nc0 * slope * math.exp(-slope * kq) * Tc_ * (X_ + H_ * X_ ** 2 / (2 * Yf_))
    okj7 &= abs(num_d - pred) < 1e-5 * max(1, abs(pred)) and num_d < 0
    okj7 &= (-pred) < (nc0 * slope * math.exp(-slope * kq) * Tc_ * (X_ + min(1, H_ + 0.1) * X_ ** 2 / (2 * Yf_))) + 1e-12
check("J7 prop:ext-commonmode(f): with nu^cm = nu^out + nu^chg(kappa_itgc), the mean cost falls by -nu^chg' T_con "
      "[X + H X^2/(2Y_f)] per unit of control quality, more under higher concentration (300 draws)", okj7)

# ==============================================================================================
header("K. Capability plateau (prop:ext-feasible(f), prop:ext-timing(g), prop:ext-should(f))")
# ==============================================================================================
# feasibility: H stops growing at t_p; activity j is ever feasible iff n_dbl_j <= (t_p - t0)/T_d
t0p, tp_ = 2025.2, 2027.0
draws_p = muH + sdH * RNG.standard_normal(400000)                 # required doublings, as in B5
SFp = lambda t: float(np.mean(draws_p <= (min(t, tp_) - t0p) / Td))
lim_p = float(norm.cdf(((tp_ - t0p) / Td - muH) / sdH))
okk1 = abs(SFp(2040.0) - lim_p) < 3e-3 and abs(SFp(2026.0) - float(np.mean(draws_p <= (2026.0 - t0p) / Td))) < 1e-12
okk1 &= SFp(2030.0) == SFp(2060.0)
# context engines are the only lever after the plateau: crossing requires kappa' >= kappa dbar/H_p
dbar_, Hp_, kap_ = 40.0, 16.0, 1.25
need = kap_ * dbar_ / Hp_
okk1 &= abs(dbar_ * kap_ / need - Hp_) < 1e-12 and need > kap_
print(f"     -> plateau at {tp_}: capability-feasible share stops at {lim_p:.3f} (vs 1 in the limit without a plateau)")
check("K1 prop:ext-feasible(f): with a plateau at t_p the feasible share is frozen at F((t_p - t0)/T_d) < 1 (0.39 for a "
      "plateau in 2027, median 4 doublings, sd 3); an activity above the plateau crosses only if context raises kappa_ctx "
      "by dbar_j/H_p", okk1 and round(lim_p, 2) == 0.39)


# adoption timing with a plateau: W(t) = v[c0 - c_Q(t) - pi(t) n], c_Q falls with capability until t_p
def W_path(t, tp=None, v=1.0, c0=3.0, cq0=2.0, dq=0.5, p0=1.0, dpi=0.6, dpi_p=None):
    tq = t if tp is None else min(t, tp)
    if tp is None or t <= tp or dpi_p is None:
        pr = p0 * math.exp(-dpi * t)
    else:
        pr = p0 * math.exp(-dpi * tp - dpi_p * (t - tp))
    return v * (c0 - cq0 * math.exp(-dq * tq) - pr)


def O_payg(T, tp=None, F0=6.0, dF=0.2, r=0.10, **kw):
    pts = [T] + ([tp] if tp is not None and tp > T else []) + [T + 60.0]
    val = sum(integrate.quad(lambda t: math.exp(-r * t) * W_path(t, tp, **kw), a_, b_, limit=400, epsabs=1e-12,
                             epsrel=1e-12)[0] for a_, b_ in zip(pts[:-1], pts[1:]))
    val += integrate.quad(lambda t: math.exp(-r * t) * W_path(t, tp, **kw), T + 60.0, np.inf, limit=400)[0]
    return val - math.exp(-r * T) * F0 * math.exp(-dF * T)


def Tstar_payg(tp=None, F0=6.0, dF=0.2, r=0.10, **kw):
    N = lambda T: W_path(T, tp, **kw) - (r + dF) * F0 * math.exp(-dF * T)
    if N(0) >= 0:
        return 0.0
    if N(200) < 0:
        return math.inf
    return optimize.brentq(N, 0, 200)


okk2 = True
Ts0, Tsp = Tstar_payg(), Tstar_payg(tp=1.0)
okk2 &= Tsp >= Ts0
for tp in (0.5, 1.0, 2.0):
    d0 = O_payg(0.0) - O_payg(0.0, tp)
    okk2 &= all(abs((O_payg(T) - O_payg(T, tp)) - d0) < 1e-6 for T in (0.0, 0.25, tp * 0.9))   # equal loss up to t_p
    okk2 &= all(O_payg(T) - O_payg(T, tp) <= d0 + 1e-9 for T in (tp + 0.5, tp + 2.0))         # smaller loss later
# option value of waiting (max_T O - O(0)) rises weakly under pay-as-you-go
grid_T = np.linspace(0, 12, 241)
ov0 = max(O_payg(T) for T in grid_T) - O_payg(0.0)
ovp = max(O_payg(T, 1.0) for T in grid_T) - O_payg(0.0, 1.0)
okk2 &= ovp >= ov0 - 1e-9
# never crosses: plateau leaves W below the user cost forever (prices stop falling too, F does not fall)
okk2 &= Tstar_payg(tp=0.5, dF=0.0, F0=6.0, dpi_p=0.0, c0=2.4) == math.inf and Tstar_payg(dF=0.0, F0=6.0, c0=2.4) < math.inf
print(f"     -> plateau, pay-as-you-go: T* {Ts0:.2f} -> {Tsp:.2f} (t_p = 1); option value of waiting {ov0:.3f} -> {ovp:.3f}")


# lock-in: c_var fixed at adoption; O_L(T) = int_T e^{-rt} v (c0 - cvar(T)) dt - e^{-rT} F(T)
def cvar(T, tp=None, cq0=2.0, dq=0.5, p0=1.0, dpi=0.6):
    tq = T if tp is None else min(T, tp)
    tpr = T if tp is None else min(T, tp)
    return cq0 * math.exp(-dq * tq) + p0 * math.exp(-dpi * tpr)


def O_lock(T, tp=None, F0=6.0, dF=0.2, r=0.10, gv=0.0, c0=3.0):
    return (c0 - cvar(T, tp)) * math.exp(-r * T) / (r - gv) - math.exp(-r * T) * F0 * math.exp(-dF * T)


okk3 = True
for tp in (0.5, 1.0, 3.0):
    okk3 &= all(abs(O_lock(T) - O_lock(T, tp)) < 1e-12 for T in np.linspace(0, tp, 7))
    okk3 &= all(O_lock(T, tp) <= O_lock(T) + 1e-12 for T in np.linspace(tp, tp + 10, 21))
    m0 = max(O_lock(T) for T in grid_T) - O_lock(0.0)
    mp = max(O_lock(T, tp) for T in grid_T) - O_lock(0.0, tp)
    okk3 &= mp <= m0 + 1e-12
TL0 = grid_T[int(np.argmax([O_lock(T) for T in grid_T]))]
TLp = grid_T[int(np.argmax([O_lock(T, 1.0) for T in grid_T]))]
print(f"     -> plateau, lock-in: best date {TL0:.2f} -> {TLp:.2f} (t_p = 1)")
check("K2 prop:ext-timing(g): pay-as-you-go: the plateau lowers the value of every adoption date up to t_p by the same "
      "amount and later dates by less, delays T* (and can prevent adoption), and weakly raises max_T O - O(0)", okk2)
check("K3 prop:ext-timing(g): lock-in: values up to t_p are unchanged and later ones fall, so the option value of "
      "waiting max_T O - O(0) weakly falls", okk3)
# should versus could under a plateau of the entrant's cost path c_E(t) = 0.45 + 0.75 e^{-0.4 t}
cE = lambda t, tp=None: 0.45 + 0.75 * math.exp(-0.4 * (t if tp is None else min(t, tp)))
PI_, psw = 1.00, 0.05
flip = lambda tp=None: next((t for t in np.linspace(0, 50, 50001) if PI_ > cE(t, tp) + psw), math.inf)
okk4 = abs(flip() - math.log(1.5) / 0.4) < 2e-3 and flip(0.5) == math.inf and abs(flip(2.0) - flip()) < 2e-3
lr_price = cE(1e9, 2.0) + psw
gap = 0.10                                  # incumbent's readiness and legacy gap over the entrant (prop:ext-should(c))
viable = lambda tp=None: cE(1e9, tp) + gap <= cE(1e9, tp) + psw      # survival test at the long-run entrant cost
okk4 &= (viable() == viable(2.0) == False) and abs(cE(0.5, 0.5) - 1.064) < 5e-4
print(f"     -> plateau and entry: flip date {flip():.2f} without a plateau; never with t_p = 0.5 (entrant cost stays at "
      f"{cE(0.5, 0.5):.3f}); with t_p = 2 the flip is unchanged and the long-run price is {lr_price:.3f} instead of "
      f"{cE(1e9) + psw:.2f}; with a constant gap of 0.10 the incumbent is not viable either way")
check("K4 prop:ext-should(f): a plateau raises the entrant's cost path, so the flip comes later or never: with t_p = 0.5 "
      "entry never binds and no automation is defensive; with t_p = 2 the flip date is unchanged and the long-run price "
      "is 0.837; viability depends on the incumbent's gap, not on the plateau", okk4 and abs(lr_price - 0.837) < 5e-4)

_mac_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "part2", "tables", "ext_macros.tex")
with open(_mac_path, "w", encoding="utf-8") as _fh:
    _fh.write("% Generated by code/verify_part2_ext.py; do not edit. XBOUNDS placeholders: " + ", ".join(f"{x:g}" for x in XBOUNDS) + ".\n")
    for _k, _v in MAC.items():
        _fh.write(f"\\providecommand{{\\{_k}}}{{{_v}}}\n")
_used = set(re.findall(r"\\(ext[A-Z][A-Za-z]*)", open(os.path.join(os.path.dirname(_mac_path), "..", "theory_ext.tex")).read()))
check("M1 every \\ext... macro used in theory_ext.tex is generated by this script, and the section inputs the file",
      _used <= set(MAC) and "part2/tables/ext_macros.tex" in open(os.path.join(os.path.dirname(_mac_path), "..", "theory_ext.tex")).read(),
      f"undefined: {sorted(_used - set(MAC))}")
n_fail = sum(1 for _, ok in RESULTS if not ok)
print("\n" + "=" * 78)
print(f"SUMMARY: {len(RESULTS) - n_fail}/{len(RESULTS)} checks passed" + ("" if n_fail == 0 else f"; {n_fail} FAILED"))
print("=" * 78)
sys.exit(0 if n_fail == 0 else 1)
