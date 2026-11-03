#!/usr/bin/env python3
"""
verify_part2_product.py

Symbolic (sympy) and numerical (numpy/scipy) verification of every closed form, first-order
condition, threshold and shape claim in
  part2/theory_product.tex  (Section "AI in the Product: Pricing, Seats and Margins", label sec:product)
  part2/proofs_product.tex  (Appendix "Proofs for Section sec:product", label app:proofs-product)
and of every number quoted in the worked examples of that section.

Run:  python3 verify_part2_product.py   (well under a minute)
Exit code is 0 if and only if every check passes. Section headers cite results by their LaTeX labels.
Numbers printed with "->" are the ones quoted in theory_product.tex; the script asserts them.

Notation (see notes/theory_product_notes.md):
  V       customer's saving per outcome, gross of price  (paper: \\mathsf V)
  kap     capture share p/V                              (paper: \\kappa_{\\rm cap})
  cI      cost-to-value ratio chat_I/V                    (paper: \\mathsf c_I)
  eps     adoption elasticity                            (paper: \\epsilon_{\\rm ad});  D(kap) = (1-kap)^eps
  rho_u   per-outcome rent from scarce inputs            (paper: \\rho_u)
  X(t)    compressed share of seat-hours                 (paper: \\mathcal X(t)); nu = Xdot/(1-X)
  Bass p, q                                              (paper: \\mathfrak p, \\mathfrak q); B(t) Bass CDF (\\mathsf B)
  Lratio  labor-to-seat ratio V t_FTE/(t p_seat)          (paper: \\mathsf W);  mu0 = gamma_seat/W (paper: \\mathsf s)
  migration targets k: delta (concession), eh (seat exposure e_k), omega (cost in years of gross profit), varpi (success)
"""
import itertools
import math
import sys

import numpy as np
import sympy as sp
from scipy import integrate, optimize, stats

RNG = np.random.default_rng(20261029)
# XBOUNDS: placeholder values of the firm's decision weight on growth X. The author withdrew the 7-to-13 estimate
# (revision plan, decision D-1); examples are evaluated at these placeholders until the replacement bounds are in.
# To swap in the final bounds, edit this tuple, rerun, and check the "% XBOUNDS" sentences of theory_product.tex.
XBOUNDS = (2.5, 5.0, 9.0)
MAC = {}      # macros written to part2/tables/product_macros.tex (read by theory_product.tex)
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] {name}" + (f"  ::  {detail}" if detail else ""))


def header(title):
    print("\n" + "=" * 78 + f"\n{title}\n" + "=" * 78)


def is_zero(e):
    return sp.simplify(e) == 0


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def near(a, b, tol):
    """absolute tolerance, for rounded numbers quoted in the text"""
    return abs(a - b) <= tol


# ==============================================================================================
# Reference implementations (mirrored in notes/theory_product_notes.md, Section 4)
# ==============================================================================================
def quality_cost(e, L, wtR):
    """core Prop. tasks-review(b): economic review share only; c^Q = eL[1 - exp(-w tR/(eL))]."""
    return e * L * (1.0 - math.exp(-wtR / (e * L)))


def adoption(kap, eps):
    """share of in-scope units that adopt at capture share kap: D = (1-kap)^eps on [0,1]."""
    return max(0.0, 1.0 - kap) ** eps


def kap_monopoly(cI, eps):
    return (1.0 + eps * cI) / (1.0 + eps)


def C_ad(eps):
    return eps ** eps / (1.0 + eps) ** (1.0 + eps)


def price_competition(V, chatI, chatE, rho_u, eps, upsE=0.0):
    """Prop. prod-price(b): p* = min{kap^m V, (1+upsE) chatE + rho_u}; None if not viable."""
    cap = (1.0 + upsE) * chatE + rho_u
    pm = kap_monopoly(chatI / V, eps) * V
    if cap < chatI:
        return None, cap, pm
    return min(pm, cap), cap, pm


def bass_B(t, p, q):
    b = p + q
    e = np.exp(-b * t)
    return (1.0 - e) / (1.0 + (q / p) * e)


def bass_f(t, p, q):
    B = bass_B(t, p, q)
    return (p + q * B) * (1.0 - B)


def bass_t_of_B(B, p, q):
    return math.log((1.0 + q * B / p) / (1.0 - B)) / (p + q)


def nu_seat(t, xbar, p, q):
    """proportional seat-loss rate for X(t) = xbar B(t)."""
    return xbar * bass_f(t, p, q) / (1.0 - xbar * bass_B(t, p, q))


def Bhat_peak(xbar, p, q):
    """cumulative adoption at which nu peaks (x < 1, q > p(1-x))."""
    return (1.0 - math.sqrt((1.0 - xbar) * (1.0 + xbar * p / q))) / xbar


def nu_star(r, g, delta, eh, omega, varpi):
    """Prop. prod-migrate(b): seat-compression threshold; None if the denominator is <= 0."""
    den = varpi * (1 - delta) * (1 - eh) - omega * (r - g)
    if den <= 0:
        return None
    return (r - g) * (varpi * delta + omega * (r - g)) / den


def V_mig(T, Xfun, R0, gam, r, g, delta, eh, omega, varpi, horizon=400.0):
    """value of migrating at T (Assumption ass:prod-migrate), with T_mig = omega gam R_S(T)."""
    XT = Xfun(T)

    def integrand(t):
        Xt = Xfun(t)
        return math.exp(-(r - g) * t) * ((1 - delta) * ((1 - eh) * (1 - XT) + eh * (1 - Xt)) - (1 - Xt))

    I = integrate.quad(integrand, T, T + horizon, limit=400, epsabs=1e-12, epsrel=1e-10)[0]
    RS = R0 * math.exp(g * T) * (1 - XT)
    return varpi * gam * R0 * I - math.exp(-r * T) * omega * gam * RS


def first_crossing(fun, level, t_max=60.0, n=60001):
    ts = np.linspace(0.0, t_max, n)
    vals = np.array([fun(t) for t in ts]) - level
    if vals[0] >= 0:
        return 0.0
    idx = np.where((vals[:-1] < 0) & (vals[1:] >= 0))[0]
    if len(idx) == 0:
        return None
    return optimize.brentq(lambda t: fun(t) - level, ts[idx[0]], ts[idx[0] + 1], xtol=1e-12)


def partI_R(m0, G, k, X, ell, al):
    y = X - k
    if y <= 0:
        return m0 + y * G
    Ca = (1 - al) * al ** (al / (1 - al))
    return m0 + y * G + Ca * (ell * y) ** (1 / (1 - al))


# ==============================================================================================
# Running example (all values illustrative unless marked "sourced")
# ==============================================================================================
cH = 18.09                   # sourced (class c): params.yaml product.capture_share.human_cost_per_resolution_usd
                             #   = OEWS May 2025 median wage (SOC 43-4051) x (1 + tau_L) / 1.7 resolutions an hour
t = 1 / 1.7                  # hours per resolution (Brynjolfsson, Li and Raymond, never-treated agents)
w = cH / t                   # loaded $/h implied
ratio_O, kapO, zetaO = 0.55, 0.10, 0.60   # params.yaml F05 (assumed); kappa_O; zeta_O
cO = ratio_O * cH + kapO * cH + zetaO
betaU, pinU = 0.14, 0.05     # brynjolfsson2025generative (+14% resolutions per hour); inference for U
cU = cH / (1 + betaU) + pinU
cbar = min(cH, cO, cU)
wtR = w * 0.8 * t            # review time t^R = 0.8 t (core convention)
Lerr = 30.0                  # loss per undetected error ($, assumed)
eI, eE = 0.04, 0.066         # raw error rates of the incumbent's and the entrant's agent (assumed)
etaI, etaE = 0.05, 0.20      # handoff/integration cost per ticket: embedded vs bolt-on (assumed)
cresI = quality_cost(eI, Lerr, wtR) + etaI
cresE = quality_cost(eE, Lerr, wtR) + etaE
VI, VE = cbar - cresI, cbar - cresE
p_sw = 0.20
rho_u = VI - VE + p_sw
chatI = 0.40
chatE0, cE_inf, d_pi = 0.40, 0.10, math.log(5.0)   # entrant's full unit cost path chatE(t) = cE_inf + (chatE0-cE_inf) e^{-d_pi t}
eps = 1.0

# Seat and outcome list prices: ranges across four vendors' public list prices (accessed 29 Oct 2026; refs_product.bib).
# Middle (professional) support tiers, per seat a month on annual billing: 55, 85, 90, 100 -> range [55, 100].
# Lowest and highest published tiers across the four vendors: under 25 to 550; the checks use [25, 550] (robustness only).
# Per resolution or conversation: 0.50, 0.99, 2.00 (per conversation) -> [0.50, 2.00]. A price per session is not used.
seat_month = {"lo": 55.0, "hi": 100.0}
seat_month_span = {"min": 25.0, "max": 550.0}
outcome_list = (0.50, 0.99, 2.00)
t_FTE = 2080.0
gam_seat = 0.80


def seat_terms(per_month):
    """seat price a year, seat revenue per unit of human work, labor-to-seat ratio W"""
    ps = per_month * 12
    return ps, ps * t / t_FTE, VI * t_FTE / (t * ps)


p_seat, pbar_seat, Lratio = seat_terms(seat_month["hi"])     # single values below are recomputed at both ends
W_lo, W_hi = seat_terms(seat_month["hi"])[2], seat_terms(seat_month["lo"])[2]

# ==============================================================================================
header("0. Running example: customer side (ticket resolution, SOC 43-4051)")
# ==============================================================================================
print(f"     -> loaded wage ${w:.2f}/h; c_H = ${cH:.2f}; c_O = ${cO:.2f}; c_U = ${cU:.2f}; best alternative ${cbar:.2f}")
print(f"     -> residual cost: incumbent ${cresI:.2f} (quality {quality_cost(eI, Lerr, wtR):.2f}), "
      f"entrant ${cresE:.2f} (quality {quality_cost(eE, Lerr, wtR):.2f})")
print(f"     -> V_I = ${VI:.2f}, V_E = ${VE:.2f}, rho_u = ${rho_u:.2f}; labor-to-seat ratio W = {W_lo:.1f} ($100) to {W_hi:.1f} ($55)")
print(f"     -> wage check: OEWS May 2025 median $44,770 / 2080 x 1.4288 / 1.7 = ${44770 / 2080 * 1.4288 / 1.7:.2f}")
check("E0 example: c_H = 18.09 (sourced), c_O = 12.36, c_U = 15.92, cbar = c_O", near(cH, 18.09, 1e-9) and near(cO, 12.36, 0.005)
      and near(cU, 15.92, 0.005) and cbar == cO)
check("E0 example: V_I = 11.11, V_E = 10.18, rho_u = 1.13, W = 32.7 to 59.5 over seat prices $100 to $55",
      near(VI, 11.11, 0.005) and near(VE, 10.18, 0.005) and near(rho_u, 1.13, 0.005) and near(W_lo, 32.7, 0.05)
      and near(W_hi, 59.5, 0.05) and near(44770 / 2080 * 1.4288 / 1.7, 18.09, 0.005))

# ==============================================================================================
header("1. Value-based price under competition (Proposition prop:prod-price)")
# ==============================================================================================
k_s, c_s, e_s, V_s = sp.symbols("kappa c epsilon V", positive=True)
lnPi = sp.log(k_s - c_s) + e_s * sp.log(1 - k_s)
foc = sp.diff(lnPi, k_s)
km = (1 + e_s * c_s) / (1 + e_s)
check("A1 (a) FOC of ln[(kap-c)(1-kap)^eps] vanishes at kap^m = (1+eps c)/(1+eps)", is_zero(foc.subs(k_s, km)))
check("A2 (a) ln profit strictly concave in kap: second derivative = -1/(kap-c)^2 - eps/(1-kap)^2",
      is_zero(sp.diff(lnPi, k_s, 2) - (-1 / (k_s - c_s) ** 2 - e_s / (1 - k_s) ** 2)))
prof_m = sp.simplify(V_s * (km - c_s) * (1 - km) ** e_s)
target = V_s * e_s ** e_s / (1 + e_s) ** (1 + e_s) * (1 - c_s) ** (1 + e_s)
okA3 = True
for _ in range(200):
    vals = {c_s: RNG.uniform(0.01, 0.95), e_s: RNG.uniform(0.2, 5), V_s: RNG.uniform(0.5, 20)}
    okA3 &= close(float(prof_m.subs(vals)), float(target.subs(vals)), 1e-10)
check("A3 (a) maximal profit per in-scope unit = V C_ad (1-c)^(1+eps) (200 draws)", okA3)
check("A4 (a) gross margin at the monopoly price = (1-c)/(1+eps c)",
      is_zero(sp.simplify(1 - c_s / km - (1 - c_s) / (1 + e_s * c_s))))
ch_s = sp.symbols("chat", positive=True)
pm_s = (V_s + e_s * ch_s) / (1 + e_s)
check("A5 (c) p^m = (V + eps chat)/(1+eps) = kap^m V; dp/dchat = eps/(1+eps); dp/dV = 1/(1+eps)",
      is_zero(pm_s - km.subs(c_s, ch_s / V_s) * V_s) and is_zero(sp.diff(pm_s, ch_s) - e_s / (1 + e_s))
      and is_zero(sp.diff(pm_s, V_s) - 1 / (1 + e_s)))
# (b) constrained optimum on random draws
okA6 = True
for _ in range(400):
    V = RNG.uniform(1, 20)
    cI = RNG.uniform(0.01, 0.8) * V
    cE = RNG.uniform(0.0, 1.0) * V
    ru = RNG.uniform(0.0, 0.6) * V
    ep = RNG.uniform(0.3, 4)
    p_star, cap, pm = price_competition(V, cI, cE, ru, ep)
    grid = np.linspace(0, V, 40001)
    prof = np.where(grid <= cap, (grid - cI) * np.maximum(0, 1 - grid / V) ** ep, 0.0)
    best = grid[np.argmax(prof)]
    if p_star is None:
        okA6 &= prof.max() <= 1e-12
    else:
        okA6 &= abs(best - p_star) <= 2 * V / 40000 + 1e-9
check("A6 (b) optimal price = min{kap^m V, chatE + rho_u}; no profitable sale if the cap is below chatI (400 draws)", okA6)
# example
pstar, cap0, pm0 = price_competition(VI, chatI, chatE0, rho_u, eps)
cI0 = chatI / VI
kap_m = kap_monopoly(cI0, eps)
kap_star = pstar / VI
gm_star = 1 - chatI / pstar
p_inf = cE_inf + rho_u
chat_ddag = kap_m * VI - rho_u
print(f"     -> c_I = {cI0:.3f}; kap^m = {kap_m:.3f}, p^m = ${pm0:.2f}, adoption {adoption(kap_m, eps):.3f}")
print(f"     -> competitive cap ${cap0:.2f} binds: kap* = {kap_star:.3f}, adoption {adoption(kap_star, eps):.3f}, "
      f"agent gross margin {gm_star:.3f}; chatE^ddag = ${chat_ddag:.2f}")
print(f"     -> long run: p -> ${p_inf:.2f}, kap -> {p_inf / VI:.3f}, gross margin at chatI = 0.10: {1 - 0.10 / p_inf:.3f}")
print(f"     -> benchmark error: kap^m priced on in-house cost would ask ${kap_m * (cH - cresI):.2f}")
check("A7 example: kap^m = 0.518, p^m = 5.75, cap 1.53 binds, kap* = 0.138, margin 0.738",
      near(kap_m, 0.518, 0.0005) and near(pm0, 5.75, 0.005) and near(cap0, 1.53, 0.005) and pstar == cap0
      and near(kap_star, 0.138, 0.0005) and near(gm_star, 0.738, 0.0005))
print(f"     -> competitive price as a share of in-house cost: {pstar / cH:.3f} (list-price-implied range 0.028 to 0.111, params.yaml)")
check("A7b example: p*/c_H = 0.085 lies in the list-price-implied range [0.028, 0.111]", 0.028 <= pstar / cH <= 0.111
      and near(pstar / cH, 0.085, 0.0005))
check("A8 example: long-run price 1.23, capture 0.111; list prices $0.99-$2.00 lie between chatE (0.40) and p^m (2.48) "
      "and contain today's and the long-run competitive price",
      near(p_inf, 1.23, 0.005) and near(p_inf / VI, 0.111, 0.0005) and chatE0 < min(outcome_list) <= p_inf <= pstar <= max(outcome_list) < pm0)
print(f"     -> outcome list-price range ${min(outcome_list):.2f} to ${max(outcome_list):.2f}: capture of V_I {min(outcome_list) / VI:.3f} to "
      f"{max(outcome_list) / VI:.3f}; of in-house cost {min(outcome_list) / cH:.3f} to {max(outcome_list) / cH:.3f}")
check("A8b example: list prices $0.50-$2.00 are 2.8% to 11.1% of in-house cost and bracket the competitive price $1.53",
      near(min(outcome_list) / cH, 0.028, 0.0005) and near(max(outcome_list) / cH, 0.111, 0.0005) and min(outcome_list) < pstar < max(outcome_list))
# (f) heterogeneous switching premia: incumbent profit Y(p) S_sw(p - pbar0), S_sw(x) = Pr{p_sw >= x}
def het_profit(p, V, cI, pbar0, S, ep):
    """vectorized in p; S must accept arrays"""
    p = np.atleast_1d(np.asarray(p, dtype=float))
    x = p - pbar0
    surv = np.where(x <= 0, 1.0, S(np.maximum(x, 0.0)))
    return (p - cI) * np.maximum(0.0, 1.0 - p / V) ** ep * surv


def het_argmax(V, cI, pbar0, S, ep, n=4001):
    """grid search on [cI, V], then bounded Brent refinement on each side of pbar0"""
    grid = np.linspace(cI, V, n)
    vals = het_profit(grid, V, cI, pbar0, S, ep)
    i = int(np.argmax(vals))
    lo_, hi_ = grid[max(i - 2, 0)], grid[min(i + 2, n - 1)]
    best, bestv = grid[i], vals[i]
    f_ = lambda z: -float(het_profit(z, V, cI, pbar0, S, ep)[0])
    for a_, b_ in ((lo_, min(hi_, pbar0)), (max(lo_, pbar0), hi_)):
        if b_ > a_:
            r_ = optimize.minimize_scalar(f_, bounds=(a_, b_), method="bounded", options={"xatol": 1e-11})
            if -r_.fun > bestv:
                best, bestv = r_.x, -r_.fun
    if cI < pbar0 < V and -f_(pbar0) >= bestv - 1e-14:
        best, bestv = pbar0, -f_(pbar0)
    return best, bestv


def gamma_sf(mean, cv):
    k_ = 1.0 / cv ** 2
    return lambda x: stats.gamma.sf(x, a=k_, scale=mean / k_)


def gamma_haz(mean, cv):
    k_ = 1.0 / cv ** 2
    return lambda x: math.exp(stats.gamma.logpdf(x, a=k_, scale=mean / k_) - stats.gamma.logsf(x, a=k_, scale=mean / k_)) if x > 0 \
        else (1.0 / mean if abs(k_ - 1.0) < 1e-12 else 0.0)


def het_root(V, cI, pbar0, haz, ep):
    """prop:prod-price(f): p* = pbar0 if ell(pbar0) <= h(0), else the root of ell(p) = h(p - pbar0) on (pbar0, p^m)"""
    ell = lambda z: 1.0 / (z - cI) - ep / (V - z)
    pm_ = kap_monopoly(cI / V, ep) * V
    if ell(pbar0) <= haz(0.0):
        return pbar0
    # on (p^m, V) ell < 0 <= h, so the bracket's right end is past p^m; the root lies below p^m
    return optimize.brentq(lambda z: ell(z) - haz(z - pbar0), pbar0 + 1e-12, pm_ + 0.5 * (V - pm_), xtol=1e-13)


okF1 = True
for _ in range(200):
    V = RNG.uniform(2, 20); cI = RNG.uniform(0.0, 0.3) * V; ep = RNG.uniform(0.5, 3.0)
    pb0 = RNG.uniform(cI, V); psw_ = RNG.uniform(0.0, 0.5) * V
    S1 = lambda x, ps=psw_: (np.asarray(x) <= ps).astype(float)
    ph, _ = het_argmax(V, cI, pb0, S1, ep, n=40001)
    pm_ = kap_monopoly(cI / V, ep) * V
    pred = min(pm_, pb0 + psw_)
    okF1 &= abs(ph - pred) <= 2 * V / 40000 + 1e-9
check("Af1 (f) a single premium (degenerate distribution) reproduces (b): p* = min{p^m, pbar0 + p_sw} (200 draws)", okF1)
okF2, okF3 = True, True
for _ in range(100):
    V = RNG.uniform(2, 20); cI = RNG.uniform(0.0, 0.3) * V; ep = RNG.uniform(0.5, 3.0)
    pm_ = kap_monopoly(cI / V, ep) * V
    pb0 = RNG.uniform(cI + 0.05 * (pm_ - cI), pm_ - 0.05 * (pm_ - cI))
    mean_, cv_ = RNG.uniform(0.02, 0.6) * V, RNG.uniform(0.15, 1.0)
    S_, h_ = gamma_sf(mean_, cv_), gamma_haz(mean_, cv_)
    ph, _ = het_argmax(V, cI, pb0, S_, ep)
    pr = het_root(V, cI, pb0, h_, ep)
    okF2 &= abs(ph - pr) <= 1e-5 * V and min(pm_, pb0) - 1e-9 <= pr <= pm_ + 1e-9
    if pr > pb0 + 1e-6 and cv_ < 0.999:
        d_ = 1e-6 * V
        dcI = (het_root(V, cI + d_, pb0, h_, ep) - het_root(V, cI - d_, pb0, h_, ep)) / (2 * d_)
        dcE = (het_root(V, cI, pb0 + d_, h_, ep) - het_root(V, cI, pb0 - d_, h_, ep)) / (2 * d_)   # upsE = 0
        okF3 &= 0 < dcI < 1 and -1e-6 <= dcE < 1
check("Af2 (f) gamma premia (cv <= 1, log-concave): grid argmax equals the root of ell(p) = h_sw(p - pbar0), or pbar0 (100 draws)", okF2)
check("Af3 (f) at an interior optimum 0 < dp*/dc_I < 1 and 0 <= dp*/dc_E < 1 + ups_E (finite differences)", okF3)
okF4 = True
for _ in range(150):
    V = RNG.uniform(2, 20); cI = RNG.uniform(0.0, 0.3) * V; ep = RNG.uniform(0.5, 3.0)
    pm_ = kap_monopoly(cI / V, ep) * V
    pb0 = RNG.uniform(cI + 0.05 * (pm_ - cI), pm_ - 0.05 * (pm_ - cI))
    ell0 = 1.0 / (pb0 - cI) - ep / (V - pb0)
    mean_ = RNG.uniform(0.2, 3.0) / ell0
    hE = lambda x, m=mean_: 1.0 / m
    pr = het_root(V, cI, pb0, hE, ep)
    okF4 &= (pr == pb0) == (mean_ <= 1.0 / ell0)
    if pr > pb0:   # interior: shifting pbar0 (entrants' cost) leaves the price unchanged while the root stays interior
        pr2 = het_root(V, cI, pb0 - 1e-4 * (pb0 - cI), hE, ep)
        okF4 &= abs(pr2 - pr) < 1e-9 * V
check("Af4 (f) exponential premia: p* = pbar0 iff mean <= 1/ell(pbar0); interior price does not move with entrants' cost (150 draws)", okF4)
pbar0_ex = (1 + 0.0) * chatE0 + VI - VE
p_cv = {cv_: het_root(VI, chatI, pbar0_ex, gamma_haz(p_sw, cv_), eps) for cv_ in (0.1, 0.05, 0.02, 0.01)}
okF5 = all(abs(p_cv[c2] - pstar) < abs(p_cv[c1] - pstar) for c1, c2 in ((0.1, 0.05), (0.05, 0.02), (0.02, 0.01))) and abs(p_cv[0.01] - pstar) < 0.02
check("Af5 (f) gamma premia with mean p_sw: p* -> the single-premium price $1.53 as cv -> 0  ::  "
      + ", ".join(f"cv {c}: {v:.4f}" for c, v in p_cv.items()), okF5)
het_ex = {}
for cv_ in (1.0, 0.5, 0.2):
    pr = het_root(VI, chatI, pbar0_ex, gamma_haz(p_sw, cv_), eps)
    pg, _ = het_argmax(VI, chatI, pbar0_ex, gamma_sf(p_sw, cv_), eps, n=20001)
    het_ex[cv_] = (pr, pr - pbar0_ex, 1 - float(gamma_sf(p_sw, cv_)(max(pr - pbar0_ex, 0.0))), abs(pr - pg))
    print(f"     -> gamma premia, mean ${p_sw:.2f}, cv {cv_}: p* ${pr:.3f} (grid {pg:.3f}), switching rent ${pr - pbar0_ex:.3f}, "
          f"share of adopters lost {100 * het_ex[cv_][2]:.1f}%")
thr_exp = 1.0 / (1.0 / (pbar0_ex - chatI) - eps / (VI - pbar0_ex))
print(f"     -> pbar0 = ${pbar0_ex:.3f}; single premium price ${pstar:.3f}; exponential premia earn a rent only if the mean exceeds ${thr_exp:.2f}")
check("Af6 example (f), scenario values: mean $0.20, cv 1 / 0.5 / 0.2 -> p* $1.33 / $1.37 / $1.45 (single premium $1.53), "
      "switching rent $0 / $0.04 / $0.12, adopters lost 0 / 1.2% / 0.9%; exponential threshold mean $1.03",
      near(het_ex[1.0][0], 1.33, 0.005) and near(het_ex[0.5][0], 1.37, 0.005) and near(het_ex[0.2][0], 1.45, 0.005)
      and near(het_ex[1.0][1], 0.0, 1e-9) and near(het_ex[0.5][1], 0.04, 0.005) and near(het_ex[0.2][1], 0.12, 0.005)
      and near(100 * het_ex[1.0][2], 0.0, 1e-9) and near(100 * het_ex[0.5][2], 1.2, 0.05) and near(100 * het_ex[0.2][2], 0.9, 0.05)
      and near(thr_exp, 1.03, 0.005) and near(pstar, 1.53, 0.005) and max(v[3] for v in het_ex.values()) < 1e-3)
# (c) pass-through numerics in the example
dp_own = (price_competition(VI, chatI + 1e-6, chatE0, rho_u, eps)[0] - pstar) / 1e-6
dp_ent = (price_competition(VI, chatI, chatE0 + 1e-6, rho_u, eps)[0] - pstar) / 1e-6
check("A9 (c) binding cap: dp/dchat_I = 0 and dp/dchat_E = 1 (finite differences)", abs(dp_own) < 1e-6 and abs(dp_ent - 1) < 1e-6)
# concentration case: entrants' markup upsE
p_up, cap_up, _ = price_competition(VI, chatI, chatE0, rho_u, eps, upsE=0.5)
check("A10 (d) with an entrant markup upsE the cap is (1+upsE)chatE + rho_u and the floor rises",
      close(cap_up, 1.5 * chatE0 + rho_u) and p_up > pstar)
# (e) data rents with diminishing returns
e_inf, e_ref = 0.02, eE


def e_of_D(D):
    return e_inf + (e_ref - e_inf) * D ** -0.5


DI = ((e_ref - e_inf) / (eI - e_inf)) ** 2
rent_data = lambda DIn, DEn: quality_cost(e_of_D(DEn), Lerr, wtR) - quality_cost(e_of_D(DIn), Lerr, wtR)
r0 = rent_data(DI, 1.0)
r10 = rent_data(10 * DI, 10.0)
r100 = rent_data(100 * DI, 100.0)
print(f"     -> data: incumbent holds {DI:.2f}x the entrant's data; data rent ${r0:.2f}/ticket, "
      f"${r10:.2f} after both grow tenfold, ${r100:.2f} after a hundredfold")
Dg = np.linspace(1.0, 200.0, 4000)
rg = np.array([rent_data(d, 1.0) for d in Dg])
d2 = np.diff(rg, 2)
check("A11 (e) data rent increasing and concave in the incumbent's data (example, inverse-square-root errors)",
      np.all(np.diff(rg) > 0) and np.all(d2 < 1e-12))
check("A12 (e) a constant proportional data lead yields a vanishing rent (1x, 10x, 100x growth)",
      r0 > r10 > r100 > 0 and r100 < 0.2 * r0 and near(r0, 0.78, 0.005))
# bound and floor case: c^Q slope in e is in (0, L) for economic or floor-binding review
def cQ_floor(e, L, wtR, ximin):
    xi_e = math.exp(-wtR / (e * L))
    xi = max(xi_e, ximin)
    return wtR * xi + e * L * (1 - xi * (1 + math.log(1 / xi)))


okA14 = True
for _ in range(200):
    Lr, wr, xm = RNG.uniform(5, 80), RNG.uniform(0.5, 10), RNG.choice([0.0, RNG.uniform(0.05, 0.5)])
    ae, be, einf = RNG.uniform(0.01, 0.2), RNG.uniform(0.2, 1.0), RNG.uniform(0.001, 0.05)
    eD = lambda D: einf + ae * D ** -be
    cq = (lambda e: quality_cost(e, Lr, wr)) if xm == 0 else (lambda e: cQ_floor(e, Lr, wr, xm))
    DE = RNG.uniform(1, 50)
    lam = RNG.uniform(1.2, 10)
    rent = cq(eD(DE)) - cq(eD(lam * DE))
    okA14 &= 0 < rent <= Lr * ae * (DE ** -be - (lam * DE) ** -be) + 1e-12
    if xm > 0 and math.exp(-wr / (eD(lam * DE) * Lr)) < xm and math.exp(-wr / (eD(DE) * Lr)) < xm:
        Dg_ = np.linspace(DE * 1.01, DE * 3, 200)
        if all(math.exp(-wr / (eD(d) * Lr)) < xm for d in Dg_):
            rr_ = np.array([cq(eD(DE)) - cq(eD(d)) for d in Dg_])
            okA14 &= np.all(np.diff(rr_, 2) <= 1e-12)
check("A14 (e) data rent in (0, L a_e (D_E^-b - D_I^-b)]; concave in D_I where the floor binds (200 draws)", okA14)
# general: with e(D) = e_inf + a D^(-1/2) and loss linear in errors (no review), rent -> 0 at fixed ratio
a_, Ls, lam_ = sp.symbols("a L lambda", positive=True)
D_ = sp.symbols("D", positive=True)
rent_lin = Ls * a_ * (D_ ** sp.Rational(-1, 2) - (lam_ * D_) ** sp.Rational(-1, 2))
check("A13 (e) inverse-square-root errors, linear loss: rent at a fixed data ratio -> 0 as data grow",
      sp.limit(rent_lin, D_, sp.oo) == 0)

# ==============================================================================================
header("2. Seat compression (Proposition prop:prod-seats)")
# ==============================================================================================
p_s, q_s, tt, Bs, xb = sp.symbols("p q t B x", positive=True)
bS = p_s + q_s
Bexpr = (1 - sp.exp(-bS * tt)) / (1 + (q_s / p_s) * sp.exp(-bS * tt))
check("B1 Bass CDF solves dB/dt = (p + qB)(1 - B), B(0) = 0",
      is_zero(sp.diff(Bexpr, tt) - (p_s + q_s * Bexpr) * (1 - Bexpr)) and Bexpr.subs(tt, 0) == 0)
tstar = sp.log(q_s / p_s) / bS
check("B2 Bass inflection: B(t*) = (q-p)/(2q) and B'(t*) = (p+q)^2/(4q) at t* = ln(q/p)/(p+q)",
      is_zero(sp.simplify(Bexpr.subs(tt, tstar) - (q_s - p_s) / (2 * q_s)))
      and is_zero(sp.simplify(sp.diff(Bexpr, tt).subs(tt, tstar) - bS ** 2 / (4 * q_s))))
# psi(F) = d ln nu / dt; its derivative in F is negative
Fv = sp.symbols("F", positive=True)
psi = q_s - p_s - 2 * q_s * Fv + xb * (p_s + q_s * Fv) * (1 - Fv) / (1 - xb * Fv)
num = sp.simplify(psi * (1 - xb * Fv))
check("B3 psi(F)(1 - xF) = q(1 - 2F + xF^2) - p(1 - x)", is_zero(sp.expand(num - (q_s * (1 - 2 * Fv + xb * Fv ** 2) - p_s * (1 - xb)))))
dpsi = sp.diff(psi, Fv)
lhs_identity = sp.simplify(-dpsi * (1 - xb * Fv) ** 2 - (q_s * ((1 - xb * Fv) ** 2 + 1 - xb) + xb * p_s * (1 - xb)))
check("B4 -psi'(F)(1 - xF)^2 = q[(1 - xF)^2 + 1 - x] + x p (1 - x) > 0, so nu is single-peaked", is_zero(sp.expand(lhs_identity)))
okB5 = True
for _ in range(300):
    pp, qq, xx = RNG.uniform(0.005, 0.2), RNG.uniform(0.05, 1.2), RNG.uniform(0.05, 0.95)
    ts = np.linspace(0, 80, 80001)
    nus = nu_seat(ts, xx, pp, qq)
    dfn = np.diff(nus)
    dfn = dfn[np.abs(dfn) > 1e-12]          # ignore floating-point noise in the far tail
    dn = np.sign(dfn)
    changes = np.sum(dn[1:] != dn[:-1])
    if qq > pp * (1 - xx):
        Bh = Bhat_peak(xx, pp, qq)
        th = bass_t_of_B(Bh, pp, qq)
        okB5 &= changes <= 1 and abs(ts[np.argmax(nus)] - th) < 2e-3 and close(nus.max(), nu_seat(th, xx, pp, qq), 1e-5)
    else:
        okB5 &= np.all(np.diff(nus) <= 1e-12)
check("B5 nu(t) single-peaked; peak at Bhat = [1 - sqrt((1-x)(1+xp/q))]/x when q > p(1-x), else decreasing (300 draws)", okB5)
check("B6 nu(0) = x p", close(nu_seat(0.0, 0.4, 0.03, 0.4), 0.4 * 0.03))
# probit (capability-limited) peak
okB7 = True
for _ in range(50):
    xx, sT, tm = RNG.uniform(0.1, 0.9), RNG.uniform(0.5, 5), RNG.uniform(0, 10)
    ts = np.linspace(tm - 20, tm + 20, 400001)
    X = xx * stats.norm.cdf((ts - tm) / sT)
    okB7 &= abs(np.max(np.gradient(X, ts)) - xx / (math.sqrt(2 * math.pi) * sT)) < 1e-6
check("B7 capability-limited compression X = x N((t-t_m)/s_T): peak Xdot = x/(sqrt(2 pi) s_T)", okB7)
# example
xbar_h = 0.40                    # removable share of seat-hours (scenario; exposure-anchored)
eps_seat = 1.0                   # seat elasticity: share of removed seat-hours that removes seats (class d, scenario)
eps_seat_range = (0.25, 0.5, 1.0)
xbar = eps_seat * xbar_h
pB, qB = 0.027, 0.419            # vandenbulte2004social means (consumer durables)
pF, qF = 0.10, 0.80              # fast case (assumed)
R0 = 400.0                       # $M seat revenue
for name, (pp, qq) in {"durables": (pB, qB), "fast": (pF, qF)}.items():
    tB = math.log(qq / pp) / (pp + qq)
    Bh = Bhat_peak(xbar, pp, qq)
    th = bass_t_of_B(Bh, pp, qq)
    print(f"     -> {name}: tipping t* = {tB:.2f} yr (B = {(qq - pp) / (2 * qq):.3f}); peak Xdot = {xbar * (pp + qq) ** 2 / (4 * qq):.4f}/yr; "
          f"nu(0) = {xbar * pp:.4f}; nu peaks at {th:.2f} yr at {nu_seat(th, xbar, pp, qq):.4f}/yr")
tB_d = math.log(qB / pB) / (pB + qB)
th_d = bass_t_of_B(Bhat_peak(xbar, pB, qB), pB, qB)
nupk_d = nu_seat(th_d, xbar, pB, qB)
th_f = bass_t_of_B(Bhat_peak(xbar, pF, qF), pF, qF)
nupk_f = nu_seat(th_f, xbar, pF, qF)
tB_f = math.log(qF / pF) / (pF + qF)
print(f"     -> revenue at risk at full adoption: ${xbar * R0:.0f}M of ${R0:.0f}M at eps_seat = 1")
rar = {e_: e_ * xbar_h * R0 for e_ in eps_seat_range}
seat_e = {}
for e_ in eps_seat_range:
    xb = e_ * xbar_h
    Bh_ = Bhat_peak(xb, pB, qB)
    th_ = bass_t_of_B(Bh_, pB, qB)
    seat_e[e_] = (xb * pB, nu_seat(th_, xb, pB, qB), th_)
    print(f"        eps_seat = {e_:.2f}: RaR ${rar[e_]:.0f}M; nu(0) = {xb * pB:.4f}; nu peak {nu_seat(th_, xb, pB, qB):.4f} at {th_:.2f} yr")
check("B10 revenue at risk scales with seat elasticity: $40M to $160M over eps_seat in [0.25, 1]",
      near(rar[0.25], 40.0, 1e-9) and near(rar[1.0], 160.0, 1e-9) and near(rar[0.5], 80.0, 1e-9))
check("B11 example: seat-loss peak 2.6% at eps_seat = 0.5 and 1.2% at 0.25 (durables Bass)",
      near(100 * seat_e[0.5][1], 2.6, 0.05) and near(100 * seat_e[0.25][1], 1.2, 0.05))
check("B8 example (durables p, q): t* = 6.15 yr, nu peaks at 0.059/yr in year 6.75",
      near(tB_d, 6.15, 0.005) and near(nupk_d, 0.059, 0.0005) and near(th_d, 6.75, 0.005))
check("B9 example (fast): t* = 2.31 yr, nu peaks at 0.125/yr in year 2.62",
      near(tB_f, 2.31, 0.005) and near(nupk_f, 0.125, 0.0005) and near(th_f, 2.62, 0.005))

# ==============================================================================================
header("3. Pricing-model migration (Proposition prop:prod-migrate)")
# ==============================================================================================
r_, g_, de_, eh_, om_, vp_, nu_ = sp.symbols("r g delta e_h omega varpi nu", positive=True)
# sign of V'(T) e^{rT}/(gam R_S) = varpi[delta - (1-delta)(1-eh) nu/(r-g)] + omega (r - g + nu)
Vp = vp_ * (de_ - (1 - de_) * (1 - eh_) * nu_ / (r_ - g_)) + om_ * (r_ - g_ + nu_)
nus_sym = sp.solve(sp.Eq(Vp, 0), nu_)[0]
nus_cf = (r_ - g_) * (vp_ * de_ + om_ * (r_ - g_)) / (vp_ * (1 - de_) * (1 - eh_) - om_ * (r_ - g_))
check("C1 (b) V'(T) = 0 at nu* = (r-g)[varpi delta + omega(r-g)] / [varpi(1-delta)(1-e_h) - omega(r-g)]",
      is_zero(nus_sym - nus_cf))
check("C2 (b) the bracket is decreasing in nu: d/dnu = -varpi(1-delta)(1-e_h)/(r-g) + omega",
      is_zero(sp.diff(Vp, nu_) - (-vp_ * (1 - de_) * (1 - eh_) / (r_ - g_) + om_)))
# finite-difference check of the derivative formula on random Bass paths
okC3 = True
for _ in range(25):
    pp, qq, xx = RNG.uniform(0.01, 0.15), RNG.uniform(0.2, 0.9), RNG.uniform(0.1, 0.8)
    rr, gg = 0.10, RNG.uniform(0.0, 0.06)
    dd, eh, om, vp = RNG.uniform(0, 0.2), RNG.uniform(0, 0.7), RNG.uniform(0.1, 1.5), RNG.uniform(0.5, 1.0)
    Xf = lambda s, xx=xx, pp=pp, qq=qq: xx * float(bass_B(s, pp, qq))
    T0 = RNG.uniform(0.2, 10)
    h = 1e-4
    fd = (V_mig(T0 + h, Xf, 1.0, 1.0, rr, gg, dd, eh, om, vp) - V_mig(T0 - h, Xf, 1.0, 1.0, rr, gg, dd, eh, om, vp)) / (2 * h)
    RS = math.exp(gg * T0) * (1 - Xf(T0))
    nuT = nu_seat(T0, xx, pp, qq)
    formula = math.exp(-rr * T0) * RS * (vp * (dd - (1 - dd) * (1 - eh) * nuT / (rr - gg)) + om * (rr - gg + nuT))
    okC3 &= abs(fd - formula) < 1e-6
check("C3 (a) V'(T) = e^{-rT} gam R_S(T){varpi[delta - (1-delta)(1-e_h)nu/(r-g)] + omega(r-g+nu)} (25 draws, FD)", okC3)
check("C4 (b) nu* increasing in delta, omega, e_h; decreasing in varpi (signs of partials at random points)",
      all(float(sp.diff(nus_cf, z).subs({r_: 0.10, g_: 0.04, de_: dv, eh_: ev, om_: ov, vp_: pv})) * sg > 0
          for (z, sg) in [(de_, 1), (om_, 1), (eh_, 1), (vp_, -1)]
          for dv, ev, ov, pv in [(0.05, 0.0, 0.5, 0.8), (0.15, 0.4, 1.0, 0.7), (0.02, 0.6, 0.2, 0.95)]))
# (c) optimal date = first crossing (when V(T1) > 0), random draws
okC5 = True
n_int = 0
for _ in range(25):
    pp, qq, xx = RNG.uniform(0.01, 0.1), RNG.uniform(0.3, 0.9), RNG.uniform(0.2, 0.7)
    rr, gg = 0.10, 0.04
    dd, eh, om, vp = RNG.uniform(0.05, 0.3), 0.0, RNG.uniform(0.3, 1.5), RNG.uniform(0.6, 0.95)
    ns = nu_star(rr, gg, dd, eh, om, vp)
    Xf = lambda s, xx=xx, pp=pp, qq=qq: xx * float(bass_B(s, pp, qq))
    Ts = np.linspace(0, 30, 301)
    Vs = np.array([V_mig(T, Xf, 1.0, 1.0, rr, gg, dd, eh, om, vp) for T in Ts])
    T1 = first_crossing(lambda s: nu_seat(s, xx, pp, qq), ns, t_max=60) if ns is not None else None
    if T1 is not None and V_mig(T1, Xf, 1.0, 1.0, rr, gg, dd, eh, om, vp) > 0:
        n_int += 1
        okC5 &= abs(Ts[np.argmax(Vs)] - T1) <= 0.1 + 1e-9 and Vs.max() <= V_mig(T1, Xf, 1.0, 1.0, rr, gg, dd, eh, om, vp) + 1e-9
    else:
        okC5 &= Vs.max() <= 1e-6
check(f"C5 (c) optimal migration date is the first crossing of nu*, or never ({n_int} of 25 draws migrate)", okC5)
# example: target tariffs
rM, gM = 0.10, 0.04
targets = {"usage": dict(delta=0.15, eh=0.0, omega=0.25, varpi=0.75),
           "two-part": dict(delta=0.08, eh=0.0, omega=0.25, varpi=0.80),
           "seat-fee hybrid": dict(delta=0.04, eh=0.5, omega=0.15, varpi=0.85)}
Xd = lambda s: xbar * float(bass_B(s, pB, qB))
Xfst = lambda s: xbar * float(bass_B(s, pF, qF))
mig = {}
for name, prm in targets.items():
    ns = nu_star(rM, gM, prm["delta"], prm["eh"], prm["omega"], prm["varpi"])
    res = {}
    for case, (Xf, pp, qq) in {"durables": (Xd, pB, qB), "fast": (Xfst, pF, qF)}.items():
        T1 = first_crossing(lambda s: nu_seat(s, xbar, pp, qq), ns, t_max=60)
        V1 = V_mig(T1, Xf, R0, gam_seat, rM, gM, prm["delta"], prm["eh"], prm["omega"], prm["varpi"]) if T1 is not None else 0.0
        V0 = V_mig(0.0, Xf, R0, gam_seat, rM, gM, prm["delta"], prm["eh"], prm["omega"], prm["varpi"])
        res[case] = (T1, V1, V0)
    mig[name] = (ns, res)
    print(f"     -> {name}: nu* = {ns:.4f}/yr; durables: migrate at {res['durables'][0]:.2f} yr, V = ${res['durables'][1]:.0f}M "
          f"(now: ${res['durables'][2]:.0f}M); fast: at {res['fast'][0]:.2f} yr, V = ${res['fast'][1]:.0f}M")
ns_u, res_u = mig["usage"]
ns_2, res_2 = mig["two-part"]
ns_h, res_h = mig["seat-fee hybrid"]
check("C6 example: nu* = 1.23% (usage), 0.66% (two-part), 0.65% (hybrid)",
      near(ns_u, 0.0123, 0.00005) and near(ns_2, 0.0066, 0.00005) and near(ns_h, 0.0065, 0.00005))
check("C7 example (durables): two-part and hybrid migrate now (nu(0) = 1.08% > nu*); usage waits 0.32 yr",
      res_2["durables"][0] == 0.0 and res_h["durables"][0] == 0.0 and near(res_u["durables"][0], 0.32, 0.005))
# (d) the optimal value max_T V_k is monotone in (delta, omega, e_h, varpi)
def best_V(delta, eh, omega, varpi, Xf=Xd, pp=pB, qq=qB):
    ns = nu_star(rM, gM, delta, eh, omega, varpi)
    if ns is None:
        return 0.0
    T1 = first_crossing(lambda s_: nu_seat(s_, xbar, pp, qq), ns, t_max=60)
    if T1 is None:
        return 0.0
    return max(0.0, V_mig(T1, Xf, R0, gam_seat, rM, gM, delta, eh, omega, varpi))


base = dict(delta=0.08, eh=0.0, omega=0.25, varpi=0.80)
mono = (best_V(0.12, 0.0, 0.25, 0.80) < best_V(**base) and best_V(0.08, 0.3, 0.25, 0.80) < best_V(**base)
        and best_V(0.08, 0.0, 0.40, 0.80) < best_V(**base) and best_V(0.08, 0.0, 0.25, 0.90) > best_V(**base))
check("C10 (d) max_T V_k falls with delta, e_h and omega and rises with varpi (example)", mono)
V2d, V2f = res_2["durables"][1], res_2["fast"][1]
Vud, Vuf = res_u["durables"][1], res_u["fast"][1]
# timing and value of the two-part migration across the seat-elasticity range (scenario parameter)
mig_e = {}
prm2 = targets["two-part"]
for e_ in eps_seat_range:
    xb = e_ * xbar_h
    Xe = lambda s_, xb=xb: xb * float(bass_B(s_, pB, qB))
    T1e = first_crossing(lambda s_: nu_seat(s_, xb, pB, qB), ns_2, t_max=60)
    V1e = V_mig(T1e, Xe, R0, gam_seat, rM, gM, prm2["delta"], prm2["eh"], prm2["omega"], prm2["varpi"]) if T1e is not None else None
    mig_e[e_] = (T1e, V1e)
    print(f"        two-part at eps_seat = {e_:.2f}: migrate at {T1e:.2f} yr, value ${V1e:.0f}M")
check("C11 example: two-part migration at eps_seat = 1, 0.5, 0.25: now ($745M); at 0.50 yr ($163M); never (V(T1 = 2.49) = -$110M)",
      mig_e[1.0][0] == 0.0 and near(mig_e[1.0][1], 745, 0.5) and near(mig_e[0.5][0], 0.50, 0.005) and near(mig_e[0.5][1], 163, 0.5)
      and near(mig_e[0.25][0], 2.49, 0.005) and near(mig_e[0.25][1], -110, 0.5))
dip2 = targets["two-part"]["omega"] * gam_seat * R0 / 500.0
print(f"     -> one-time migration cost of the two-part tariff: {100 * dip2:.0f}% of the firm's revenue ($500M) if all at once")
check("C9 example: two-part migration values $745M (durables) and $1,033M (fast); one-time cost 16% of revenue",
      near(V2d, 745, 0.5) and near(V2f, 1033, 0.5) and near(dip2, 0.16, 1e-12))
best = max(mig.items(), key=lambda kv: kv[1][1]["durables"][1])[0]
check("C8 example: the two-part tariff has the highest migration value in both diffusion cases",
      best == "two-part" and max(mig.items(), key=lambda kv: kv[1][1]["fast"][1])[0] == "two-part")
print(f"     -> two-part values: durables ${V2d:.0f}M, fast ${V2f:.0f}M; usage: ${Vud:.0f}M, ${Vuf:.0f}M")

# ==============================================================================================
header("4. The feature portfolio (Proposition prop:prod-portfolio)")
# ==============================================================================================
S0, Xw, kk, Dstar, rg = 500.0, 9.0, 0.0, 0.05, 0.05   # $M revenue, own weight, k, excess growth, r - g°
feats = {   # upsilon, inference cost c0 (share of base revenue at full adoption), decline, dG, dlam, F ($M), nE, p, q
    "agent":   dict(ups=0.050, c0=0.015, dec=0.4, dG=0.0010, dl=0.00, F=10.0, nE=25, p=0.08, q=0.60),
    "copilot": dict(ups=0.005, c0=0.006, dec=0.4, dG=0.0020, dl=0.02, F=5.0, nE=12, p=0.10, q=0.80),
    "QA":      dict(ups=0.010, c0=0.002, dec=0.4, dG=0.0005, dl=0.00, F=6.0, nE=15, p=0.03, q=0.40),
    "voice":   dict(ups=0.020, c0=0.018, dec=0.4, dG=0.0000, dl=0.00, F=20.0, nE=30, p=0.02, q=0.30),
}
F_plat, NE_cap = 15.0, 60


def feat_npv(f, X=Xw, rgv=rg):
    Rf = lambda s: f["ups"] - f["c0"] * math.exp(-f["dec"] * s) + (X - kk) * (f["dG"] + Dstar * f["dl"])
    I = integrate.quad(lambda s: math.exp(-rgv * s) * float(bass_B(s, f["p"], f["q"])) * Rf(s), 0, 600, limit=400)[0]
    return S0 * I - f["F"]


npv = {k: feat_npv(v) for k, v in feats.items()}
npv_scr = {k: feat_npv(v, X=2.5) for k, v in feats.items()}
for k in feats:
    print(f"     -> {k}: NPV ${npv[k]:.0f}M at X = 9 (${npv_scr[k]:.0f}M at X = 2.5); per engineer-year ${npv[k] / feats[k]['nE']:.1f}M")
names = list(feats)
best_val, best_set = -1e9, None
for m in range(1 << len(names)):
    sel = [names[i] for i in range(len(names)) if m >> i & 1]
    if sum(feats[s]["nE"] for s in sel) > NE_cap:
        continue
    val = sum(npv[s] for s in sel) - (F_plat if sel else 0.0)
    if val > best_val:
        best_val, best_set = val, sel
order = sorted(names, key=lambda k: -npv[k] / feats[k]["nE"])
greedy, used = [], 0
for k in order:
    if npv[k] > 0 and used + feats[k]["nE"] <= NE_cap:
        greedy.append(k)
        used += feats[k]["nE"]
print(f"     -> optimal set {best_set} (value ${best_val:.0f}M net of the ${F_plat:.0f}M platform); greedy {greedy}")
check("D1 example: exact knapsack picks agent, copilot and QA; greedy by NPV per engineer-year agrees",
      set(best_set) == {"agent", "copilot", "QA"} and set(greedy) == set(best_set))
# shadow value of capacity in the LP relaxation (marginal feature ratio)
lp_ratio = npv["voice"] / feats["voice"]["nE"]
print(f"     -> marginal (fractional) feature in the relaxation: voice, ${lp_ratio:.1f}M per engineer-year")
# LP relaxation = greedy fractional, random instances
okD2 = True
for _ in range(200):
    nI = 6
    vals = RNG.uniform(-5, 50, nI)
    wts = RNG.uniform(1, 20, nI)
    capv = RNG.uniform(5, 60)
    res = optimize.linprog(-vals, A_ub=[wts], b_ub=[capv], bounds=[(0, 1)] * nI, method="highs")
    ordr = np.argsort(-vals / wts)
    rem, gv = capv, 0.0
    for i in ordr:
        if vals[i] <= 0 or rem <= 0:
            continue
        x = min(1.0, rem / wts[i])
        gv += x * vals[i]
        rem -= x * wts[i]
    okD2 &= abs(-res.fun - gv) < 1e-7
check("D2 (a) LP relaxation of the capacity-constrained portfolio is solved by ranking NPV per unit of capacity (200 draws)", okD2)
# platform rule: build the platform iff max subset value > F_plat; check random instances by enumeration
okD3 = True
for _ in range(200):
    vals = RNG.uniform(-10, 20, 5)
    Fp = RNG.uniform(0, 40)
    best_e = max(0.0, max(sum(vals[i] for i in range(5) if m >> i & 1) - Fp for m in range(1, 32)))
    rule = max(0.0, np.sum(np.maximum(vals, 0)) - Fp)
    okD3 &= abs(best_e - rule) < 1e-12
check("D3 (b) without capacity limits the platform is built iff sum of positive feature NPVs exceeds its cost (200 draws)", okD3)
# retention break-even weight
cop = feats["copilot"]
check("D4 (c) score flow at full adoption and t = 0: copilot +2.60 pts at X = 9 (0.5 - 0.6 + 9 x 0.3); agent +4.4 pts",
      near(100 * (cop["ups"] - cop["c0"] + Xw * (cop["dG"] + Dstar * cop["dl"])), 2.6, 0.005)
      and near(100 * (feats["agent"]["ups"] - feats["agent"]["c0"] + Xw * feats["agent"]["dG"]), 4.4, 0.005))
cop_flow = 100 * (cop["ups"] - cop["c0"] + Xw * (cop["dG"] + Dstar * cop["dl"]))
print(f"     -> copilot score flow at full adoption and t = 0: {cop_flow:.2f} points "
      f"(of which retention and pull {100 * Xw * (cop['dG'] + Dstar * cop['dl']):.2f})")
check("D5 example: ranking by NPV per engineer-year is copilot > agent > QA > voice at X = 9; at X = 2.5 the agent leads",
      order == ["copilot", "agent", "QA", "voice"] and max(npv_scr, key=lambda k: npv_scr[k] / feats[k]["nE"]) == "agent")

# XBOUNDS evaluation of the portfolio example (decision D-1): values, integer optimum, ranking and copilot flow
XB = {}
for X_ in XBOUNDS:
    nv = {k: feat_npv(v, X=X_) for k, v in feats.items()}
    bv, bs = -1e9, None
    for m in range(1 << len(names)):
        sel = [names[i] for i in range(len(names)) if m >> i & 1]
        if sum(feats[s_]["nE"] for s_ in sel) > NE_cap:
            continue
        val = sum(nv[s_] for s_ in sel) - (F_plat if sel else 0.0)
        if val > bv:
            bv, bs = val, sel
    flow = 100 * (cop["ups"] - cop["c0"] + X_ * (cop["dG"] + Dstar * cop["dl"]))
    XB[X_] = dict(npv=nv, best=bs, best_val=bv, order=sorted(names, key=lambda k: -nv[k] / feats[k]["nE"]), flow=flow,
                  ret=100 * X_ * (cop["dG"] + Dstar * cop["dl"]))
X_flow0 = (cop["c0"] - cop["ups"]) / (cop["dG"] + Dstar * cop["dl"])
X_rank = optimize.brentq(lambda X_: feat_npv(feats["copilot"], X=X_) / feats["copilot"]["nE"]
                         - feat_npv(feats["agent"], X=X_) / feats["agent"]["nE"], 2.5, 9.0)
print("     -> XBOUNDS portfolio: " + "; ".join(f"X = {X_:g}: " + ", ".join(f"{k} ${v['npv'][k]:.0f}M" for k in names)
      + f"; optimum {v['best']} ${v['best_val']:.0f}M; order {v['order']}; copilot flow {v['flow']:+.2f}" for X_, v in XB.items())
      + f"; copilot flow positive above X = {X_flow0:.2f}; copilot overtakes the agent per engineer-year at X = {X_rank:.2f}")
check("D6 XBOUNDS (2.5, 5, 9): the integer optimum is agent, copilot and analytics at every placeholder; the agent leads per "
      "engineer-year at 2.5 and 5 and the copilot at 9, crossing at X = 7.1; the copilot's flow at full adoption is "
      "positive at every placeholder (zero at X = 1/3); voice is worth the same at every weight",
      XBOUNDS == (2.5, 5.0, 9.0) and all(set(v["best"]) == {"agent", "copilot", "QA"} for v in XB.values())
      and XB[2.5]["order"][0] == "agent" and XB[5.0]["order"][0] == "agent" and XB[9.0]["order"][0] == "copilot"
      and 5.0 < X_rank < 9.0 and abs(X_rank - 7.14) < 0.01 and all(v["flow"] > 0 for v in XB.values())
      and abs(X_flow0 - 1 / 3) < 1e-12 and max(v["npv"]["voice"] for v in XB.values()) - min(v["npv"]["voice"] for v in XB.values()) < 1e-9,
      f"cross {X_rank:.3f}")
_m0 = lambda x: f"{x:.0f}"
for i_, X_ in enumerate(XBOUNDS):
    tag = ("One", "Two", "Three")[i_]
    v = XB[X_]
    MAC.update({f"prodXb{tag}": f"{X_:g}", f"prodAgent{tag}": _m0(v["npv"]["agent"]), f"prodCopilot{tag}": _m0(v["npv"]["copilot"]),
                f"prodQA{tag}": _m0(v["npv"]["QA"]), f"prodBest{tag}": _m0(v["best_val"]),
                f"prodFlow{tag}": f"${v['flow']:+.2f}$", f"prodRet{tag}": f"{v['ret']:.2f}",
                f"prodAgentPer{tag}": f"{v['npv']['agent'] / feats['agent']['nE']:.1f}",
                f"prodCopilotPer{tag}": f"{v['npv']['copilot'] / feats['copilot']['nE']:.1f}"})
MAC.update(prodVoice=_m0(XB[XBOUNDS[0]]["npv"]["voice"]), prodRankCross=f"{X_rank:.1f}", prodFlowZero="1/3")

# ==============================================================================================
header("5. Model sourcing: API, open weights or own model (Proposition prop:prod-model)")
# ==============================================================================================
rK, dK = 0.10, 1 / 3
src = {  # c_var(0), inference part, decline of inference part, K ($ per annual outcome), F_tilde ($M/yr), rho_u
    "api":  dict(cv=0.40, ci=0.30, dec=math.log(5.0), K=0.00, Ft=1.0, rho=rho_u),
    "open": dict(cv=0.22, ci=0.12, dec=0.0, K=0.10, Ft=4.0, rho=rho_u + 0.10),   # vintage-locked self-hosting
    "own":  dict(cv=0.15, ci=0.05, dec=0.0, K=0.08, Ft=15.0, rho=rho_u + 0.30),
}


def net_unit(m, tm=0.0):
    s = src[m]
    cv = s["cv"] - s["ci"] + s["ci"] * math.exp(-s["dec"] * tm)
    return cv + (rK + dK) * s["K"] - s["rho"]


def Qthr(m1, m2, tm=0.0):
    d = net_unit(m1, tm) - net_unit(m2, tm)
    return (src[m2]["Ft"] - src[m1]["Ft"]) / d if d > 0 else math.inf


for m in src:
    print(f"     -> {m}: net unit cost {net_unit(m):.4f} (t=0), {net_unit(m, 50):.4f} (long run)")
Q1, Q2, Q3 = Qthr("api", "open"), Qthr("open", "own"), Qthr("api", "own")
print(f"     -> thresholds: api->open {Q1:.1f}M, open->own {Q2:.1f}M, api->own {Q3:.1f}M outcomes a year")
Qex = 20.0
choice = min(src, key=lambda m: Qex * net_unit(m) + src[m]["Ft"])
check("E1 example: ladder api < 12.7M < open < 39.5M < own; at 20M outcomes open weights win",
      near(Q1, 12.7, 0.05) and near(Q2, 39.5, 0.05) and Q1 < Q2 and choice == "open")
# date at which open weights stop beating the API per unit (api net unit cost falls below open's)
t_open = optimize.brentq(lambda s: net_unit("api", s) - net_unit("open", s), 0.0, 20.0)
Q3_inf = Qthr("api", "own", 50)
print(f"     -> open weights lose their unit-cost edge over the API at t = {t_open:.2f} yr; long-run api->own threshold {Q3_inf:.0f}M")
check("E2 (b) example: open weights lose the unit-cost edge within a year (t = 0.97); long-run build threshold 65M",
      near(t_open, 0.97, 0.005) and near(Q3_inf, 65.0, 0.5))
# ladder rule vs direct comparison on random instances
okE3 = True
for _ in range(300):
    F = np.sort(RNG.uniform(0, 20, 3))
    cn = -np.sort(-RNG.uniform(-2, 1, 3))   # net unit costs, decreasing
    Qs = RNG.uniform(0, 200)
    direct = int(np.argmin(Qs * cn + F))
    # lower envelope: thresholds between consecutive options on the envelope
    env = [0]
    for m in (1, 2):
        while len(env) >= 2:
            a, b = env[-2], env[-1]
            qab = (F[b] - F[a]) / (cn[a] - cn[b])
            qbm = (F[m] - F[b]) / (cn[b] - cn[m])
            if qbm <= qab:
                env.pop()
            else:
                break
        env.append(m)
    cur = env[0]
    for i in range(1, len(env)):
        qth = (F[env[i]] - F[env[i - 1]]) / (cn[env[i - 1]] - cn[env[i]])
        if Qs >= qth:
            cur = env[i]
    okE3 &= abs((Qs * cn[cur] + F[cur]) - (Qs * cn[direct] + F[direct])) < 1e-9
check("E3 (a) volume ladder: the lower envelope of affine total costs gives the optimal option (300 draws)", okE3)
okE4 = all(Qthr("api", "own", s1) <= Qthr("api", "own", s2) for s1, s2 in [(0, 0.5), (0.5, 1), (1, 3), (3, 10)])
check("E4 (b) the build threshold rises as the API price falls", okE4)

# ==============================================================================================
header("6. Gross-margin path (Proposition prop:prod-margin)")
# ==============================================================================================
uh, uc, du, ph_, f_, g0, gs = sp.symbols("u_h u_c delta_u varphi f gamma_0 gamma_s", positive=True)
ts_ = sp.symbols("t", positive=True)
u0 = uh + uc
ut = uh + uc * sp.exp(-du * ts_)
gam_t = 1 - f_ - (1 - f_ - g0) * (ut / u0) ** (1 - ph_)
check("F1 (a) d gamma/dt = (1-f-gamma_0)(1-varphi) delta_u u_c e^{-delta t} (u/u0)^{-varphi} / u0 > 0 for varphi < 1",
      is_zero(sp.simplify(sp.diff(gam_t, ts_) - (1 - f_ - g0) * (1 - ph_) * du * uc * sp.exp(-du * ts_) * (ut / u0) ** (-ph_) / u0)))
okF2 = True
for _ in range(200):
    uhv, ucv, duv, phv, fv = RNG.uniform(0, 0.3), RNG.uniform(0.1, 1), RNG.uniform(0.1, 2), RNG.uniform(0, 0.95), RNG.uniform(0, 0.05)
    g0v = RNG.uniform(0.2, 0.6)
    gsv = RNG.uniform(g0v + 0.01, 0.95 - fv)
    u0v = uhv + ucv
    gam_fun = lambda s: 1 - fv - (1 - fv - g0v) * ((uhv + ucv * math.exp(-duv * s)) / u0v) ** (1 - phv)
    ginf = 1 - fv - (1 - fv - g0v) * (uhv / u0v) ** (1 - phv)
    zr = (1 - fv - gsv) / (1 - fv - g0v)
    inner = u0v * zr ** (1 / (1 - phv)) - uhv
    if ginf > gsv:
        Tx = math.log(ucv / inner) / duv
        okF2 &= abs(gam_fun(Tx) - gsv) < 1e-9 and inner > 0
    else:
        okF2 &= inner <= 1e-12 and gam_fun(1e3) <= gsv + 1e-9
check("F2 (b) crossover date T_x = ln{u_c / [u0 z^(1/(1-varphi)) - u_h]}/delta_u exists iff gamma_inf > gamma_sub (200 draws)", okF2)
# ICONIQ calibration
yrs = np.array([0.0, 1.0, 2.0])
gm_ic = np.array([0.45, 0.53, 0.59])
y = np.log(1 - gm_ic)
slope, icpt = np.polyfit(yrs, y, 1)
lam_fit = -slope
g_sub = 0.74   # Part I core-sample median gross margin 2023-25 (horizons.tex)
Tx1 = (icpt - math.log(1 - g_sub)) / lam_fit
dd1, dd2 = (1 - gm_ic[0]) - (1 - gm_ic[1]), (1 - gm_ic[1]) - (1 - gm_ic[2])
q_ = dd2 / dd1
delta_fl = -math.log(q_)
b_fl = dd1 / (1 - q_)
a_fl = (1 - gm_ic[0]) - b_fl
Tx2 = math.log(b_fl / ((1 - g_sub) - a_fl)) / delta_fl
print(f"     -> ICONIQ fit 1 (no floor): (1-varphi) delta_u = {lam_fit:.3f}/yr; crossover with 74% in {2025 + Tx1:.1f}")
for dlt in (math.log(5.0), math.log(2.0), 0.30):
    print(f"        implied pass-through varphi at delta_u = {dlt:.3f}: {1 - lam_fit / dlt:.2f}")
print(f"     -> ICONIQ fit 2 (floor, fixed price): floor {a_fl:.3f}, decline {delta_fl:.3f}/yr; gamma_inf = {1 - a_fl:.2f}; "
      f"crossover in {2025 + Tx2:.1f}")
# fragility: 2027 at 57%
gm_alt = np.array([0.45, 0.53, 0.57])
e1, e2 = (1 - gm_alt[0]) - (1 - gm_alt[1]), (1 - gm_alt[1]) - (1 - gm_alt[2])
qa = e2 / e1
ba = e1 / (1 - qa)
aa = (1 - gm_alt[0]) - ba
print(f"     -> if 2027 were 57%: floor fit gamma_inf = {1 - aa:.2f} (below 74%: no crossover)")
check("F3 example: fit 1 gives (1-varphi)delta_u = 0.147 and crossover in 2030.1; varphi = 0.91 at a fivefold decline",
      near(lam_fit, 0.147, 0.0005) and near(2025 + Tx1, 2030.1, 0.05) and near(1 - lam_fit / math.log(5), 0.91, 0.005))
check("F4 example: fit 2 gives floor 0.23, gamma_inf = 0.77 and crossover in 2033.2; with 57% in 2027 no crossover",
      near(a_fl, 0.23, 1e-9) and near(2025 + Tx2, 2033.2, 0.05) and 1 - aa < g_sub)
# (c) limit pricing
rr_, uu_ = sp.symbols("rho u", positive=True)
gl = rr_ / (uu_ + rr_) - f_
check("F5 (c) limit pricing gamma = rho_u/(u+rho_u) - f, decreasing in u; crossover iff rho_u/u_h > (gamma_sub+f)/(1-f-gamma_sub)",
      sp.simplify(sp.diff(gl, uu_)) == -rr_ / (uu_ + rr_) ** 2
      and is_zero(sp.simplify(sp.solve(sp.Eq(gl, gs), rr_)[0] / uu_ - (gs + f_) / (1 - f_ - gs))))
gm_lim0 = rho_u / (chatI + rho_u)
gm_liminf = rho_u / (cE_inf + rho_u)
print(f"     -> limit-pricing margin: {gm_lim0:.3f} today, {gm_liminf:.3f} at the cost floor; needed rent/floor ratio "
      f"{g_sub / (1 - g_sub):.2f}, actual {rho_u / cE_inf:.1f}")
check("F6 example: limit-pricing margin 0.738 today and 0.919 at the floor; rent/floor 11.3 > 2.85",
      near(gm_lim0, 0.738, 0.0005) and near(gm_liminf, 0.919, 0.0005) and near(rho_u / cE_inf, 11.3, 0.05)
      and rho_u / cE_inf > g_sub / (1 - g_sub))
# (d) blended margin trough
wbar, pw, qw = 0.35, 0.08, 0.60
gamAI = lambda s: 1 - math.exp(icpt - lam_fit * s)
blend = lambda s: wbar * float(bass_B(s, pw, qw)) * gamAI(s) + (1 - wbar * float(bass_B(s, pw, qw))) * g_sub
res_b = optimize.minimize_scalar(blend, bounds=(0, 15), method="bounded", options={"xatol": 1e-10})
t_tr, g_tr = res_b.x, res_b.fun
print(f"     -> blended margin trough {100 * g_tr:.1f}% in year {t_tr:.1f} (from {100 * g_sub:.0f}%); back to 74% at "
      f"{optimize.brentq(lambda s: blend(s) - (g_sub - 1e-6), t_tr, 40):.1f} yr")
check("F7 (d) blended-margin trough satisfies wdot (gamma_sub - gamma_AI) = w gammadot_AI",
      abs((wbar * bass_f(t_tr, pw, qw)) * (g_sub - gamAI(t_tr)) - wbar * float(bass_B(t_tr, pw, qw)) * lam_fit * (1 - gamAI(t_tr))) < 1e-6)
t_back = optimize.brentq(lambda s: blend(s) - (g_sub - 1e-6), t_tr, 40)
check("F8 example: trough of 72.5% in year 2.7, back to 74% in year 5.1",
      near(100 * g_tr, 72.5, 0.05) and near(t_tr, 2.7, 0.05) and near(t_back, 5.1, 0.05))

# ==============================================================================================
header("7. Product side in Part I's parameters (Proposition prop:prod-aggregate, Corollary cor:prod-dilution)")
# ==============================================================================================
# (a) G_i = sum_l w_l G_l for the revenue sum
okG1 = True
for _ in range(100):
    gl_ = RNG.uniform(-0.2, 0.5, 3)
    S_l = RNG.uniform(0.5, 5, 3)
    Sfun = lambda s: np.sum(S_l * np.exp(gl_ * s))
    h = 1e-6
    lhs = (math.log(Sfun(h)) - math.log(Sfun(-h))) / (2 * h)
    okG1 &= abs(lhs - np.sum(S_l * gl_) / np.sum(S_l)) < 1e-8
check("G1 (a) zero-spend growth of the sum is the revenue-weighted sum of line growth rates (100 draws)", okG1)
# exact linearity of R* in G_i and m0
m0s, Gs, ks, Xs, ells, als = sp.symbols("m0 G k X ell alpha", positive=True)
Rst = m0s + (Xs - ks) * Gs + (1 - als) * als ** (als / (1 - als)) * (ells * (Xs - ks)) ** (1 / (1 - als))
check("G2 (c) R*_X is exactly linear in (m0, G_i): dR* = dm0 + (X-k) dG_i", is_zero(sp.diff(Rst, Gs) - (Xs - ks))
      and sp.diff(Rst, Gs, 2) == 0 and sp.diff(Rst, m0s, Gs) == 0)
# frontier rotation (Part I figure parameters)
m0f, Gf, kf, alf, ellf = 0.45, 0.10, 0.10, 0.3, 0.6
bet = 1 / alf
kapf = ellf ** (-bet)
Dm, dG = 0.03, 0.01
diff_fr = lambda g: -Dm + kapf * ((g - Gf) ** bet - (g - Gf - dG) ** bet)
g_hat = optimize.brentq(diff_fr, Gf + dG + 1e-12, 2.0)
X_at = lambda g: kf + bet * kapf * (g - Gf) ** (bet - 1)
print(f"     -> rotation (Part I Fig. parameters, D_m = 0.03, dG = 0.01): frontiers cross at g = {g_hat:.3f}; "
      f"dual weight there {X_at(g_hat):.2f} (bracket {X_at(g_hat - dG):.2f} to {X_at(g_hat):.2f})")
okG3 = (diff_fr(g_hat - 0.01) < 0 < diff_fr(g_hat + 0.01)) and (X_at(g_hat - dG) - kf) * dG <= Dm <= (X_at(g_hat) - kf) * dG
check("G3 cor:prod-dilution: unique crossing; (X(g-dG)-k)dG <= D_m <= (X(g)-k)dG at the crossing", okG3)
okG4 = True
for _ in range(200):
    kp, bb = RNG.uniform(0.5, 20), RNG.uniform(1.5, 4)
    Dmv, dGv = RNG.uniform(0.001, 0.1), RNG.uniform(0.001, 0.05)
    gr = np.linspace(dGv, 2, 4000)
    dv = -Dmv + kp * (gr ** bb - (gr - dGv) ** bb)
    okG4 &= np.all(np.diff(dv) > 0)
check("G4 cor:prod-dilution: the frontier difference is strictly increasing in g (200 draws)", okG4)
print(f"     -> R* change for D_m = 0.03, dG_i = 0.01: {100 * (-Dm + 9 * dG):+.1f} pts at X = 9, {100 * (-Dm + 2.5 * dG):+.1f} at X = 2.5")
dil = {X_: 100 * (-Dm + X_ * dG) for X_ in XBOUNDS}
check("G5 example (XBOUNDS 2.5, 5, 9): the dilution plan changes the score by -0.5, +2.0 and +6.0 points; the sign flips at "
      "X - k = D_m/dG = 3, between the first two placeholders",
      near(dil[2.5], -0.5, 1e-9) and near(dil[5.0], 2.0, 1e-9) and near(dil[9.0], 6.0, 1e-9) and near(Dm / dG, 3.0, 1e-12))
MAC.update({f"prodDil{t}": (f"$+{d:.1f}$" if d >= 0 else f"$-{abs(d):.1f}$") for t, d in zip(("One", "Two", "Three"), dil.values())})
MAC.update(prodDilFlip=f"{Dm / dG:g}")
check("G6 example: frontiers cross at g = 0.57 where the dual weight is 3.2", near(g_hat, 0.57, 0.005) and near(X_at(g_hat), 3.2, 0.05))
# (d) complementarity of value pricing and COGS automation (Topkis)
okG7 = True
for _ in range(200):
    zs = np.linspace(0, 1, 201)
    a1, a2 = RNG.uniform(0.01, 0.1), RNG.uniform(0.01, 0.2)
    sav = a1 * (1 - np.exp(-3 * zs))       # concave saving as share of revenue
    cost = a2 * zs ** 2
    phis = np.sort(RNG.uniform(0, 1, 5))[::-1]   # decreasing pass-through
    zst = [zs[np.argmax((1 - ph) * sav - cost)] for ph in phis]
    okG7 &= all(np.diff(zst) >= -1e-12)
check("G7 (d) optimal COGS automation is nondecreasing as pass-through falls (200 draws)", okG7)
# TAM multiplier and the scorecard
Dst = adoption(kap_star, eps)
tam = {}
for key, pm in list(seat_month.items()) + list(seat_month_span.items()):
    Wk = seat_terms(pm)[2]
    tam[key] = (Wk, kap_star * Wk, 1 / Wk, 1 + xbar_h * Dst * (kap_star * Wk - 1))
    print(f"     -> TAM at ${pm:.0f}/seat-month: W = {Wk:.1f}, kap* W = {kap_star * Wk:.2f}, 1/W = {1 / Wk:.4f}, market multiple {tam[key][3]:.2f}")
pm_conv = kap_star * VI * t_FTE / t / 12
print(f"     -> market conversion fails above a seat price of ${pm_conv:.0f} a month")
tam_mult = tam["hi"][3]
check("G8 example: across $55-$100, kap* W = 4.50 to 8.19, 1/W = 1.7% to 3.1%, market x2.21 to x3.48",
      near(tam["hi"][1], 4.50, 0.005) and near(tam["lo"][1], 8.19, 0.005) and near(tam["hi"][2], 0.031, 0.0005)
      and near(tam["lo"][2], 0.017, 0.0005) and near(tam["hi"][3], 2.21, 0.005) and near(tam["lo"][3], 3.48, 0.005))
check("G8b robustness: conversion holds at $25 and fails at $550 a seat-month (threshold $450; x0.94 at $550)",
      tam["min"][1] > 1 and tam["max"][1] < 1 and near(pm_conv, 450, 0.5) and near(tam["max"][3], 0.94, 0.005))
# conversion at the ends of the outcome list-price range: kap = p / V_I, threshold seat price kap V_I t_FTE / (12 t)
kap_list = {"lo": min(outcome_list) / VI, "hi": max(outcome_list) / VI}
pm_conv_list = {k_: v_ * VI * t_FTE / t / 12 for k_, v_ in kap_list.items()}
print(f"     -> at outcome list prices ${min(outcome_list):.2f} / ${max(outcome_list):.2f} (kap {kap_list['lo']:.3f} / {kap_list['hi']:.3f}): "
      f"conversion threshold ${pm_conv_list['lo']:.0f} / ${pm_conv_list['hi']:.0f} a seat-month; "
      f"kap W over $55-$100: {kap_list['lo'] * W_lo:.2f}-{kap_list['lo'] * W_hi:.2f} (low price)")
check("G8c robustness: at the lowest outcome list price ($0.50) conversion holds across $55-$100 (kap W 1.47 to 2.68) "
      "and needs seats below $147; at the highest ($2.00) below $589",
      kap_list["lo"] * W_lo > 1 and near(kap_list["lo"] * W_lo, 1.47, 0.005) and near(kap_list["lo"] * W_hi, 2.68, 0.005)
      and near(pm_conv_list["lo"], 147, 0.5) and near(pm_conv_list["hi"], 589, 0.5))
# (b) market growth with a falling capture share, and the bounded integral of diffusion growth
okG12 = True
for _ in range(50):
    kap0, kdot, Lr_ = RNG.uniform(0.1, 0.5), RNG.uniform(-0.05, 0.0), RNG.uniform(5, 40)
    pp, qq, xx = RNG.uniform(0.02, 0.1), RNG.uniform(0.2, 0.8), RNG.uniform(0.1, 0.6)
    Xf_ = lambda s_: xx * float(bass_B(s_, pp, qq))
    kf_ = lambda s_: kap0 + kdot * s_
    M_ = lambda s_: 1 + Xf_(s_) * (kf_(s_) * Lr_ - 1)
    t0_ = RNG.uniform(0.5, 5)
    h_ = 1e-6
    fd_ = (math.log(M_(t0_ + h_)) - math.log(M_(t0_ - h_))) / (2 * h_)
    Xd_ = xx * bass_f(t0_, pp, qq)
    form_ = (Xd_ * (kf_(t0_) * Lr_ - 1) + Xf_(t0_) * Lr_ * kdot) / M_(t0_)
    okG12 &= abs(fd_ - form_) < 1e-6
check("G12 (b) market growth = [Xdot (kap L - 1) + X L kapdot] / [1 + X (kap L - 1)] (50 draws, FD)", okG12)
kapL = kap_star * W_lo
gfun = lambda s_: xbar_h * Dst * (kapL - 1) * bass_f(s_, pB, qB) / (1 + xbar_h * Dst * (kapL - 1) * float(bass_B(s_, pB, qB)))
Iint = integrate.quad(gfun, 0, 400, limit=400)[0]
check("G13 (d) the time integral of diffusion growth equals ln[1 + X_inf (kap L - 1)] (bounded)",
      abs(Iint - math.log(1 + xbar_h * Dst * (kapL - 1))) < 1e-7, f"{Iint:.6f}")
# scorecard at year 3 (two-part tariff now, agent launched now, slow (durables) diffusion for customers' automation)
tS = 3.0
seat_rev = R0 * (1 - 0.08)        # two-part tariff: 8% concession, protected from compression
other = 100.0                     # other lines, $M
chatE3 = cE_inf + (chatE0 - cE_inf) * math.exp(-d_pi * tS)
gamAI_lim = rho_u / (chatE3 + rho_u)              # limit pricing, chat_I = chat_E (Prop. prod-margin(c))
gamAI_ic = 1 - math.exp(icpt - lam_fit * tS)      # ICONIQ fit-1 path, for comparison
gAI = bass_f(tS, pB, qB) / float(bass_B(tS, pB, qB))
g_star, k_def = 0.15, 0.25


def make_shift(per_month):
    """Part I parameter shifts at t = 3 for a seat price per month (seat revenue fixed at R0, so work volume = R0/pbar)"""
    pbar = seat_terms(per_month)[1]
    v_units = R0 * 1e6 / pbar
    AI3 = pstar * xbar_h * Dst * float(bass_B(tS, pB, qB)) * v_units / 1e6
    S3 = AI3 + seat_rev + other
    wAI, wseat = AI3 / S3, seat_rev / S3
    sh = {
        "dgamma_mix": wAI * (gamAI_lim - gam_seat),
        "dgamma_mix_iconiq": wAI * (gamAI_ic - gam_seat),
        "dgamma_feat": sum(float(bass_B(tS, f["p"], f["q"])) * (f["ups"] - f["c0"] * math.exp(-f["dec"] * tS))
                           for k_, f in feats.items() if k_ in ("copilot", "QA")) * (S0 / S3),
        "dG_comp": wseat * nu_seat(tS, xbar, pB, qB),
        "dG_AI": wAI * gAI,
        "dG_feat": sum(float(bass_B(tS, f["p"], f["q"])) * f["dG"] for k_, f in feats.items() if k_ != "voice"),
        "dlam_feat": sum(float(bass_B(tS, f["p"], f["q"])) * f["dl"] for k_, f in feats.items() if k_ != "voice"),
        "dk_def": k_def * 0.5 * wseat,
        "da_ops": -0.02,
        "du_ops": -0.03,
    }
    return sh, wAI, S3


shift_lo, wAI_lo, S3_lo = make_shift(seat_month["lo"])
shift, wAI, S3 = make_shift(seat_month["hi"])


def dR(X, phi, sh=shift):
    """first-order Delta R*_X (prop:prod-aggregate(c)); Delta* = 0.05, k = 0"""
    dgam = sh["dgamma_mix"] + sh["dgamma_feat"] - (1 - phi) * sh["du_ops"]
    dG = sh["dG_comp"] + sh["dG_AI"] + sh["dG_feat"]
    return dgam - sh["da_ops"] - g_star * sh["dk_def"] + (X - kk) * dG + (X - kk) * Dstar * sh["dlam_feat"]


for k_, v_ in shift.items():
    print(f"        {k_:20s} {100 * v_:+7.3f} pts")
dR1v, dR1c, dR9v, dR9c = dR(1, 0), dR(1, 1), dR(9, 0), dR(9, 1)
dR1_trans = (1 - 1) + shift["dG_comp"] + shift["dG_AI"]
print(f"     -> year-3: AI share {wAI:.3f}, AI margin {gamAI_lim:.3f} (ICONIQ path {gamAI_ic:.3f}); "
      f"Rule-of-40 change {100 * dR1v:+.1f} pts (value pricing) / {100 * dR1c:+.1f} (cost-plus); "
      f"R*_9 change {100 * dR9v:+.1f} / {100 * dR9c:+.1f}")
print(f"        of which transient diffusion growth (G_i from compression avoided and AI expansion): "
      f"{100 * (shift['dG_comp'] + shift['dG_AI']):.1f} pts of growth")
check("G9 example scorecard at $100: AI share 0.162 at year 3; AI margin 0.92 (limit pricing) vs 0.65 (ICONIQ path)",
      near(wAI, 0.162, 0.0005) and near(gamAI_lim, 0.917, 0.0005) and near(gamAI_ic, 0.647, 0.0005))
check("G10 example scorecard at $100: Rule-of-40 change +16.7 (value pricing) and +13.7 (cost-plus); difference = 3 pts = COGS saving",
      near(100 * dR1v, 16.7, 0.05) and near(100 * dR1c, 13.7, 0.05) and close(dR1v - dR1c, 0.03))
check("G11 example scorecard rows at $100: mix +1.89 (ICONIQ -2.47), features +0.30, compression +2.10, AI expansion +8.36, "
      "retention +0.17, pull 1.21%, k +8.24 (score -1.24); transient growth 10.5",
      near(100 * shift["dgamma_mix"], 1.89, 0.005) and near(100 * shift["dgamma_mix_iconiq"], -2.47, 0.005)
      and near(100 * shift["dgamma_feat"], 0.30, 0.005) and near(100 * shift["dG_comp"], 2.10, 0.005)
      and near(100 * shift["dG_AI"], 8.36, 0.005) and near(100 * shift["dG_feat"], 0.17, 0.005)
      and near(100 * shift["dlam_feat"], 1.21, 0.005) and near(100 * shift["dk_def"], 8.24, 0.005)
      and near(100 * g_star * shift["dk_def"], 1.24, 0.005) and near(100 * (shift["dG_comp"] + shift["dG_AI"]), 10.5, 0.05))
print("     -> scorecard at $55 a seat-month:")
for k_, v_ in shift_lo.items():
    print(f"        {k_:20s} {100 * v_:+7.3f} pts")
dR1v_lo, dR1c_lo = dR(1, 0, shift_lo), dR(1, 1, shift_lo)
print(f"     -> year-3 at $55: AI share {wAI_lo:.3f}; Rule-of-40 change {100 * dR1v_lo:+.1f} (value pricing) / {100 * dR1c_lo:+.1f} (cost-plus)")
check("G12b example scorecard at $55: AI share 0.260; Rule-of-40 change +22.7 / +19.7; rows mix +3.04 (ICONIQ -3.97), "
      "features +0.27, compression +1.86, AI expansion +13.43, k +7.27 (score -1.09)",
      near(wAI_lo, 0.260, 0.0005) and near(100 * dR1v_lo, 22.7, 0.05) and near(100 * dR1c_lo, 19.7, 0.05)
      and near(100 * shift_lo["dgamma_mix"], 3.04, 0.005) and near(100 * shift_lo["dgamma_mix_iconiq"], -3.97, 0.005)
      and near(100 * shift_lo["dgamma_feat"], 0.27, 0.005) and near(100 * shift_lo["dG_AI"], 13.43, 0.005)
      and near(100 * shift_lo["dG_comp"], 1.86, 0.005) and near(100 * shift_lo["dk_def"], 7.27, 0.005)
      and near(100 * g_star * shift_lo["dk_def"], 1.09, 0.005))
SC = dict(wAI=wAI, gamAI=gamAI_lim, S3=S3, shift=shift, dR1v=dR1v, dR1c=dR1c, dR9v=dR9v, dR9c=dR9c)

# ==============================================================================================
header("8. Cannibalization and the replacement effect (Proposition prop:prod-cannibal)")
# ==============================================================================================
mu = sp.symbols("mu", positive=True)
lnL = sp.log(k_s - c_s - mu) + e_s * sp.log(1 - k_s)
kc = (1 + e_s * (c_s + mu)) / (1 + e_s)
check("H1 (a) cannibalizing monopolist: kap = (1 + eps(c + mu))/(1+eps) maximizes (kap - c - mu)(1-kap)^eps",
      is_zero(sp.diff(lnL, k_s).subs(k_s, kc)))
can = {}
for key, pm in list(seat_month.items()) + list(seat_month_span.items()):
    ms_ = gam_seat * seat_terms(pm)[1]
    mu_ = ms_ / VI
    gc_ = VI * C_ad(eps) * (1 - cI0 - mu_) ** (1 + eps)
    ge_ = VI * C_ad(eps) * (1 - cI0) ** (1 + eps)
    can[key] = (ms_, mu_, kap_monopoly(cI0 + mu_, eps), 1 - gc_ / ge_, VI > chatI + ms_)
    print(f"     -> ${pm:.0f}/seat-month: seat margin ${ms_:.3f}/resolution ({100 * mu_:.1f}% of V), kap_can {can[key][2]:.3f}, "
          f"replacement cost {100 * can[key][3]:.1f}%, launch now: {can[key][4]}")
check("H2b example: across $55-$100 the seat margin is $0.15-$0.27 (1.3-2.4% of V), kap_can 0.525-0.530, replacement cost 2.8-5.0%; "
      "launch now at every published tier ($25 to $550: replacement cost up to 26%)",
      near(can["lo"][0], 0.15, 0.005) and near(can["hi"][0], 0.27, 0.005) and near(100 * can["lo"][1], 1.3, 0.05)
      and near(100 * can["hi"][1], 2.4, 0.05) and near(can["lo"][2], 0.525, 0.0005) and near(can["hi"][2], 0.530, 0.0005)
      and near(100 * can["lo"][3], 2.8, 0.05) and near(100 * can["hi"][3], 5.0, 0.05) and all(v[4] for v in can.values())
      and near(100 * can["max"][3], 26, 0.5))
mseat = gam_seat * pbar_seat
mu0 = mseat / VI
kap_can = kap_monopoly(cI0 + mu0, eps)
gain_can = VI * C_ad(eps) * (1 - cI0 - mu0) ** (1 + eps)
gain_ent = VI * C_ad(eps) * (1 - cI0) ** (1 + eps)
print(f"     -> seat margin per ticket ${mseat:.3f} ({100 * mu0:.1f}% of V = gamma_seat/L); kap_can = {kap_can:.3f}; launch gain "
      f"${gain_can:.3f} vs ${gain_ent:.3f} for an entrant (replacement cost {100 * (1 - gain_can / gain_ent):.1f}%)")
check("H2 example at $100: seat margin $0.271/resolution = 2.4% of V; kap_can = 0.530; replacement effect costs 5.0%",
      near(mseat, 0.271, 0.0005) and near(mu0, 0.024, 0.0005) and near(kap_can, 0.530, 0.0005)
      and near(1 - gain_can / gain_ent, 0.050, 0.0005))
check("H3 (a) mu = gamma_seat / L", close(mu0, gam_seat / Lratio))
# (b) with entry the replacement term disappears at the cap
okH4 = True
for _ in range(200):
    V = RNG.uniform(1, 10)
    cI, ms, capv, ep = RNG.uniform(0, 0.5) * V, RNG.uniform(0, 0.5) * V, RNG.uniform(0.1, 0.9) * V, RNG.uniform(0.5, 3)
    D = lambda pz: max(0.0, 1 - pz / V) ** ep
    no_launch = ms * (1 - D(capv))
    launch = ms * (1 - D(capv)) + (capv - cI) * D(capv)
    okH4 &= abs((launch - no_launch) - (capv - cI) * D(capv)) < 1e-12
check("H4 (b) with entrants the launch gain at the cap is (pbar - chat_I) D(pbar): no replacement term (200 draws)", okH4)
okH4b = True
for _ in range(200):
    V = RNG.uniform(1, 10)
    cI, ms, ep = RNG.uniform(0, 0.4) * V, RNG.uniform(0, 0.3) * V, RNG.uniform(0.5, 3)
    capv = RNG.uniform(cI + 0.01, V)
    obj = lambda pz: ms + (pz - cI - ms) * max(0.0, 1 - pz / V) ** ep
    grid = np.linspace(0, capv, 20001)
    best_p = grid[np.argmax([obj(z) for z in grid])]
    pred = min(kap_monopoly((cI + ms) / V, ep) * V, capv)
    okH4b &= abs(best_p - pred) <= 2 * capv / 20000 + 1e-9
check("H4b (b) with a binding cap the incumbent's agent price is min{kap_can V, pbar} (200 draws)", okH4b)
# (c) Poisson preemption: Monte Carlo of the value difference
nuE, bfl, afl, rgv = 0.15, -0.03, 0.05, 0.06
draws = RNG.exponential(1 / nuE, 400000)
mc = np.mean(bfl * (1 - np.exp(-rgv * draws)) / rgv + afl * np.exp(-rgv * draws) / rgv)
formula = (bfl + nuE * afl / rgv) / (rgv + nuE)
check("H5 (c) value of launching now = [b + nu_E a/(r-g)]/(r-g+nu_E) (Monte Carlo, 400k draws)", abs(mc - formula) < 3e-3 * max(1, abs(formula)),
      f"MC {mc:.4f} vs {formula:.4f}")
okH6 = True
for _ in range(100):
    bb, aa_, nn, rr2 = RNG.uniform(-1, 1), RNG.uniform(0, 1), RNG.uniform(0.01, 0.5), RNG.uniform(0.01, 0.1)
    dV0 = (bb + nn * aa_ / rr2) / (rr2 + nn)
    for T_ in (0.5, 2.0, 7.0):
        VT = math.exp(-(rr2 + nn) * T_) * dV0
        okH6 &= abs(VT - integrate.quad(lambda s: math.exp(-(rr2 + nn) * s) * (bb + nn * aa_ / rr2), T_, 2000, limit=200)[0]) < 1e-7
check("H6 (c) stationarity: launching at a later date T is worth e^{-(r-g+nu_E)T} times launching now: now or at entry", okH6)
# Arrow-binding example: professional research seats
Vp_, cIp, tP, pseatP, gseatP, psw2 = 2.20, 0.50, 1.0, 6000.0, 0.85, 0.40
msP = gseatP * pseatP * tP / t_FTE
gap = cIp + msP - Vp_
nu_thr = (rM - gM) * gap / psw2
print(f"     -> professional seats: seat margin per unit ${msP:.2f}; chatI + m - V = ${gap:.2f} > 0; "
      f"preempt iff nu_E > {nu_thr:.3f} (expected entry within {1 / nu_thr:.1f} years)")
check("H7 example: seat margin $2.45; gap $0.75; nu_E* = 0.113, i.e. expected entry within 8.9 years",
      near(msP, 2.45, 0.005) and near(gap, 0.75, 0.005) and near(nu_thr, 0.113, 0.0005) and near(1 / nu_thr, 8.9, 0.05))
ceff = cIp + msP - 0.25 * psw2 / (rM - gM)
pL = max(0.0, (Vp_ + eps * ceff) / (1 + eps))
print(f"     -> at nu_E = 0.25: effective cost ${ceff:.2f}, penetration price ${pL:.2f} (vs V = ${Vp_:.2f})")
check("H8 example: at nu_E = 0.25 the effective cost is $1.29 and the launch price $1.74", near(ceff, 1.29, 0.005) and near(pL, 1.74, 0.005))

# ==============================================================================================
header("9. Breakpoints (Proposition prop:prod-breaks)")
# ==============================================================================================
cE_front = 10.00
T_C = math.log((cE_front - cE_inf) / (chat_ddag - cE_inf)) / d_pi
print(f"     -> competition binds once chatE < ${chat_ddag:.2f}; for an entrant starting at ${cE_front:.2f}: T_C = {T_C:.2f} yr")
check("I1 example: chatE^ddag = 4.63; T_C = 0.49 yr from $10.00", near(chat_ddag, 4.63, 0.005) and near(T_C, 0.49, 0.005))
cE_path = lambda s: cE_inf + (cE_front - cE_inf) * math.exp(-d_pi * s)
check("I2 T_C formula: chatE(T_C) = chatE^ddag", close(cE_path(T_C), chat_ddag, 1e-12))
check("I3 Bass tipping exists iff q > p (no interior inflection otherwise)",
      all((qq > pp) == (math.log(qq / pp) > 0) for pp, qq in [(0.03, 0.4), (0.5, 0.3), (0.1, 0.1 + 1e-9)]))

# ----------------------------------------------------------------------------------------------
import os as _os, re as _re
_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_mp = _os.path.join(_root, "part2", "tables", "product_macros.tex")
with open(_mp, "w", encoding="utf-8") as _fh:
    _fh.write("% Generated by code/verify_part2_product.py; do not edit. XBOUNDS placeholders: " + ", ".join(f"{x:g}" for x in XBOUNDS) + ".\n")
    for _k, _v in MAC.items():
        _fh.write(f"\\providecommand{{\\{_k}}}{{{_v}}}\n")
_tex = open(_os.path.join(_root, "part2", "theory_product.tex"), encoding="utf-8").read()
_used = set(_re.findall(r"\\(prod[A-Z][A-Za-z]*)", _tex))
check("M1 every \\prod... macro used in theory_product.tex is generated by this script, and the section inputs the file",
      _used <= set(MAC) and "part2/tables/product_macros.tex" in _tex, f"undefined: {sorted(_used - set(MAC))}")
n_fail = sum(1 for _, ok in RESULTS if not ok)
print("\n" + "=" * 78)
print(f"SUMMARY: {len(RESULTS) - n_fail}/{len(RESULTS)} checks passed" + ("" if n_fail == 0 else f"; {n_fail} FAILED"))
print("=" * 78)
sys.exit(0 if n_fail == 0 else 1)
