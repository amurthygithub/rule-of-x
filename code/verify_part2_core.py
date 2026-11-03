#!/usr/bin/env python3
"""
verify_part2_core.py

Symbolic (sympy) and numerical (numpy/scipy) verification of every closed form, first-order
condition, threshold and shape claim in
  part2/theory_core.tex  (Section "What to Automate: A Task-Level Model", label sec:tasks)
  part2/proofs_core.tex  (Appendix "Proofs for Section sec:tasks", label app:proofs-tasks)
and of every number quoted in the worked examples of that section.

Run:  python3 verify_part2_core.py   (well under a minute)
Exit code is 0 if and only if every check passes. Section headers cite results by their LaTeX labels.

Sections 1 to 22 check every result on random draws and on a stylized test chain (Section 10; its parameters are test
fixtures, not the paper's example). Section 23 reads the paper's running example from data/examples/invoice_chain.yaml
(resolved with the engine's parameter loader through code/examples/invoice_chain.py), recomputes it with this script's
own implementation and checks data/examples/invoice_chain.json, part2/tables/invoice_macros.tex and the text's claims.

Notation follows part2/theory_core.tex (see notes/theory_core_notes.md):
  unit cost of mode x for activity j:  c_j(x; pi) = c0_j(x) + pi * n_j(x)
  automation:  c_j(A) = pi n_j + cQ_j + F_j/(v_j T_A) (+ capital charge (r + delta_K) K_j(A))
  quality cost (review + undetected loss), detection rate d:  K(xi) = w tR xi + e L [1 - d xi (1 + ln(1/xi))]
  optimal review fraction:  xi* = max{ exp(-w tR/(d e L)), (1 - epsbar/e)/d, ximin }, attainable iff d >= 1 - epsbar/e
  process value of automating set Z:  W_p(Z) = C_p(empty) - C_p(Z)
"""
import itertools
import re
import math
import sys

import numpy as np
import sympy as sp
from scipy import integrate, optimize, stats

RNG = np.random.default_rng(20261029)
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


# ==============================================================================================
# Reference implementations (these mirror the formulas listed for the engine in the notes)
# ==============================================================================================
def quality_cost(xi, e, L, wtR, d=1.0):
    """K(xi): review cost plus expected undetected loss when the top-xi share by stakes is reviewed and review
    detects an error with probability d."""
    if xi <= 0:
        return e * L
    return wtR * xi + e * L * (1.0 - d * xi * (1.0 + math.log(1.0 / xi)))


def review(e, L, wtR, epsbar=1.0, ximin=0.0, d=1.0):
    """Optimal review fraction, quality cost, undetected error rate (Prop prop:tasks-review), detection rate d.
    If the reliability target is infeasible (d < 1 - epsbar/e), returns xi = 1 and flags infeasibility via eps > epsbar."""
    xiE = math.exp(-wtR / (d * e * L)) if e > 0 else 0.0
    xiR = (1.0 - epsbar / e) / d if e > 0 else -np.inf
    xi = min(1.0, max(xiE, xiR, ximin))
    return xi, quality_cost(xi, e, L, wtR, d), e * (1.0 - d * xi)


def crossover_price(c0A, nA, alts):
    """pi* = min over alternatives x of (c0(x) - c0(A)) / (nA - n(x)); alts = [(c0x, nx), ...]."""
    return min((c0x - c0A) / (nA - nx) for (c0x, nx) in alts)


def best_mode(costs):
    """costs: dict mode -> cost; ties broken toward the most inference-intensive (A > U > others)."""
    order = {"A": 3, "U": 2, "O": 1, "H": 0, "N": 0}
    m = min(costs.values())
    cands = [x for x, c in costs.items() if c <= m + 1e-12]
    return max(cands, key=lambda x: order[x])


def std_normal_loss(u):
    """sfL(u) = n(u) - u (1 - N(u)), the unit normal loss function."""
    return stats.norm.pdf(u) - u * stats.norm.sf(u)


# Part I closed forms (sections/model.tex, eq:Rstar, eq:Dstar, eq:sigstar)
def partI(m0, G, k, X, ell, al):
    y = X - k
    if y <= 0:
        return 0.0, 0.0, m0 + y * G
    D = ell ** (1 / (1 - al)) * (al * y) ** (al / (1 - al))
    sig = (al * ell * y) ** (1 / (1 - al))
    R = m0 + y * G + (1 - al) * y * D
    return D, sig, R


def gordon_root(r, G, k, m0, lam, al):
    """Smallest positive root v0 of (r-G) v0 = m0 - k G + C_alpha [lam (v0-k)_+]^(1/(1-alpha)) (eq:gordon)."""
    Ca = (1 - al) * al ** (al / (1 - al))
    f = lambda v: (r - G) * v - (m0 - k * G) - Ca * (lam * max(v - k, 0.0)) ** (1 / (1 - al))
    grid = np.linspace(1e-9, 200, 200001)
    vals = np.array([f(x) for x in grid[::100]])
    idx = np.where(np.sign(vals[:-1]) != np.sign(vals[1:]))[0]
    a, b = grid[::100][idx[0]], grid[::100][idx[0] + 1]
    return optimize.brentq(f, a, b, xtol=1e-14)


# ==============================================================================================
header("1. Mode choice and the cost frontier (Proposition prop:tasks-modes)")
# ==============================================================================================
pi_s, n_s, nU_s, c0A_s, c0x_s, nx_s = sp.symbols("pi n n_U c0A c0x n_x", positive=True)
cross = (c0x_s - c0A_s) / (n_s - nx_s)
check("1a  pairwise crossover: c0A + pi n = c0x + pi n_x  at  pi = (c0x - c0A)/(n - n_x)",
      is_zero((c0A_s + cross * n_s) - (c0x_s + cross * nx_s)))

bad_conc = bad_mono = bad_over = bad_cross = bad_vol = 0
for _ in range(400):
    cH = RNG.uniform(1, 10)
    c0 = {"H": cH, "O": RNG.uniform(0.3, 1.2) * cH, "N": RNG.uniform(0.5, 3) * cH,
          "U": RNG.uniform(0.4, 0.95) * cH, "A": RNG.uniform(0.05, 0.9) * cH}
    nU = RNG.uniform(0.01, 0.5)
    nA = nU + RNG.uniform(0.05, 2.0)
    nn = {"H": 0.0, "O": 0.0, "N": 0.0, "U": nU, "A": nA}
    grid = np.linspace(0, 20, 801)
    front = np.array([min(c0[x] + p * nn[x] for x in c0) for p in grid])
    # concave (second differences <= 0) and nondecreasing
    if np.any(np.diff(front, 2) > 1e-9) or np.any(np.diff(front) < -1e-12):
        bad_conc += 1
    # monotone mode path: inference intensity of optimal mode nonincreasing in pi
    inten = [nn[best_mode({x: c0[x] + p * nn[x] for x in c0})] for p in grid]
    if np.any(np.diff(inten) > 1e-12):
        bad_mono += 1
    # crossover price characterizes A-optimality
    ps = crossover_price(c0["A"], nA, [(c0[x], nn[x]) for x in c0 if x != "A"])
    for p in grid[::40]:
        Aopt = c0["A"] + p * nA <= min(c0[x] + p * nn[x] for x in c0 if x != "A") + 1e-12
        if Aopt != (p <= ps + 1e-12):
            bad_cross += 1
    # overstatement of the automation value when measured against c_H lies in [0, c_H - c_bar]
    p = RNG.uniform(0, 5)
    cbar = min(c0[x] + p * nn[x] for x in c0 if x != "A")
    cAp = c0["A"] + p * nA
    over = max(cH - cAp, 0) - max(cbar - cAp, 0)
    if not (-1e-12 <= over <= cH - cbar + 1e-12):
        bad_over += 1
    # volume threshold: split c0A into variable part and F/(v T); A optimal iff v >= v*
    F, T, v = RNG.uniform(1e3, 1e6), RNG.uniform(1, 5), RNG.uniform(1e2, 1e6)
    cvar = c0["A"] + p * nA  # variable unit cost (excl. fixed)
    if cbar > cvar:
        vstar = F / (T * (cbar - cvar))
        if (cvar + F / (v * T) <= cbar) != (v >= vstar):
            bad_vol += 1
check("1b  (a) cost frontier min_x c_j(x;pi) is concave and nondecreasing in pi (400 draws)", bad_conc == 0,
      f"violations={bad_conc}")
check("1c  (b) inference intensity of the optimal mode is nonincreasing in pi: H/O/N -> U -> A (400 draws)",
      bad_mono == 0, f"violations={bad_mono}")
check("1d  (c) overstatement (c_H - c_A)^+ - (c_bar - c_A)^+ lies in [0, c_H - c_bar] (400 draws)", bad_over == 0)
check("1e  (d) A optimal iff pi <= pi* = min_x (c0(x) - c0(A))/(n - n(x)) (400 x 21 points)", bad_cross == 0,
      f"violations={bad_cross}")
check("1f  (e) A optimal iff v >= v* = F/(T_A (c_bar - c_var)) (400 draws)", bad_vol == 0)

# ==============================================================================================
header("2. The automation curve (Proposition prop:tasks-curve)")
# ==============================================================================================
bad_step = bad_shift = bad_delay = bad_conv = bad_env = 0
for _ in range(100):
    J = 30
    cH = RNG.uniform(1, 10, J)
    E = RNG.uniform(1e4, 1e6, J)
    cU0, nU = RNG.uniform(0.5, 0.95, J) * cH, RNG.uniform(0.0, 0.2, J)
    c0A, nA = RNG.uniform(0.05, 0.8, J) * cH, nU + RNG.uniform(0.1, 2, J)
    cO = np.where(RNG.uniform(size=J) < 0.5, RNG.uniform(0.3, 1.1, J) * cH, np.inf)
    v = E / cH
    grid = np.linspace(0.0, 15.0, 301)

    def shareA(useO):
        out = []
        for p in grid:
            alt = np.minimum(np.minimum(cH, cU0 + p * nU), cO if useO else np.inf)
            out.append(np.sum(E * (c0A + p * nA <= alt)) / E.sum())
        return np.array(out)

    SO, SN = shareA(True), shareA(False)
    if np.any(np.diff(SO) > 1e-12) or np.any(np.diff(SN) > 1e-12):
        bad_step += 1
    if np.any(SO > SN + 1e-12):
        bad_shift += 1
    # crossover with O = min(crossover without O, (cO - c0A)/nA); date delay ln(pi*N/pi*O)/delta
    psN = np.array([crossover_price(c0A[j], nA[j], [(cH[j], 0), (cU0[j], nU[j])]) for j in range(J)])
    psO = np.minimum(psN, (cO - c0A) / nA)
    dpi = math.log(3.0)
    for j in range(J):
        if psO[j] > 0 and psN[j] > 0 and psN[j] < 50:
            tN, tO = math.log(50 / psN[j]) / dpi, math.log(50 / psO[j]) / dpi
            if not close(tO - tN, math.log(psN[j] / psO[j]) / dpi, 1e-9):
                bad_delay += 1
    # savings W(pi) = sum v (c_pre - c*(pi)) is convex, and -W'(pi) = inference demand
    cpre = np.minimum(cH, cO)
    def Wsav(p):
        cstar = np.minimum.reduce([cH, cO, cU0 + p * nU, c0A + p * nA])
        return np.sum(v * (cpre - cstar))
    Ws = np.array([Wsav(p) for p in grid])
    if np.any(np.diff(Ws, 2) < -1e-6 * max(1, Ws.max())) or np.any(np.diff(Ws) > 1e-9):
        bad_conv += 1
    for p in RNG.uniform(0.1, 14, 10):
        costs = np.vstack([cH, cO, cU0 + p * nU, c0A + p * nA])
        intens = np.vstack([0 * cH, 0 * cH, nU, nA])
        idx = np.argmin(costs, axis=0)
        demand = np.sum(v * intens[idx, np.arange(J)])
        h = 1e-6
        fd = -(Wsav(p + h) - Wsav(p - h)) / (2 * h)
        if abs(fd - demand) > 1e-4 * max(1, demand):
            bad_env += 1  # (kinks have measure zero; random p avoids them a.s.)
check("2a  (a) S_A(pi) is a nonincreasing step function of pi (100 firms x 30 activities)", bad_step == 0)
check("2b  (b) the outsourcing option lowers S_A pointwise", bad_shift == 0)
check("2c  (b) crossover date delayed by ln(pi*(no O)/pi*(O))/delta_pi", bad_delay == 0)
check("2d  (c) total savings W(pi) convex and nonincreasing in pi", bad_conv == 0)
check("2e  (c) Shephard: -dW/dpi = inference demand sum_j v_j n_j(x_j*) (1000 random prices)", bad_env == 0,
      f"violations={bad_env}")

# ==============================================================================================
header("3. Vendor AI adoption and the in-house automation window (Proposition prop:tasks-window)")
# ==============================================================================================
def D_gap(p, cVH, cV0, ups, kO_cH_zO, c0A, n):
    cO = (1 + ups) * min(cVH, p * n + cV0) + kO_cH_zO
    return cO - (p * n + c0A)

bad_peak = bad_int = bad_ends = bad_mb = bad_aiexec = 0
for _ in range(500):
    n = RNG.uniform(0.05, 1)
    cVH = RNG.uniform(0.5, 2)
    cV0 = RNG.uniform(0.02, 0.5) * cVH
    ups = RNG.uniform(0, 0.5)
    extra = RNG.uniform(0, 1)
    c0A = RNG.uniform(0.1, 2.5)
    piV = (cVH - cV0) / n
    grid = np.linspace(0, 3 * piV, 3001)
    D = np.array([D_gap(p, cVH, cV0, ups, extra, c0A, n) for p in grid])
    iV = np.argmin(abs(grid - piV))
    if np.any(np.diff(D[:iV]) < -1e-12) or np.any(np.diff(D[iV + 1:]) > 1e-12):
        bad_peak += 1
    pos = D >= -1e-12
    if pos.any():
        idx = np.where(pos)[0]
        if not np.all(pos[idx[0]:idx[-1] + 1]):
            bad_int += 1
    D0 = (1 + ups) * cV0 + extra - c0A
    Dv = D_gap(piV, cVH, cV0, ups, extra, c0A, n)
    if Dv >= 0:
        piplus = ((1 + ups) * cVH + extra - c0A) / n
        piminus = 0.0 if D0 >= 0 else (-D0 / (ups * n) if ups > 0 else piV)
        if not (abs(D_gap(piplus, cVH, cV0, ups, extra, c0A, n)) < 1e-9 and piplus >= piV - 1e-12):
            bad_ends += 1
        if D0 < 0 and ups > 0 and abs(D_gap(piminus, cVH, cV0, ups, extra, c0A, n)) > 1e-9:
            bad_ends += 1
    elif pos.any():
        bad_ends += 1  # window must be empty when D(piV) < 0
    # make-or-buy volume threshold
    cQ, F, T = RNG.uniform(0, 0.5), RNG.uniform(1e4, 1e6), 3.0
    brk = (1 + ups) * cV0 + extra - cQ
    for v in RNG.uniform(1e3, 1e6, 5):
        D0v = (1 + ups) * cV0 + extra - (cQ + F / (v * T))
        if brk > 0:
            if (D0v >= 0) != (v >= F / (T * brk)):
                bad_mb += 1
        elif D0v >= 0:
            bad_mb += 1
    # AI-executed share is monotone: for H, O and A only, AI executes if A optimal or (O optimal and pi < piV)
    cH = RNG.uniform(1, 5) * (cVH + extra)
    ai = []
    for p in grid[::-1]:  # falling prices
        cO = (1 + ups) * min(cVH, p * n + cV0) + extra
        cA = p * n + c0A
        m = min(cH, cO, cA)
        x = "A" if cA <= m + 1e-12 else ("O" if cO <= m + 1e-12 else "H")
        ai.append(x == "A" or (x == "O" and p < piV))
    ai = np.array(ai)
    if np.any(ai[:-1] & ~ai[1:]):
        bad_aiexec += 1
check("3a  (a) D_j(pi) = c_O - c_A nondecreasing on [0, piV] and decreasing beyond (500 draws)", bad_peak == 0)
check("3b  (a) {pi : A beats O} is an interval (possibly empty)", bad_int == 0)
check("3c  (a)-(b) window nonempty iff D(piV) >= 0; endpoints pi+ and pi- = -D(0)/(ups n) solve D = 0", bad_ends == 0,
      f"violations={bad_ends}")
check("3d  (c) long-run in-house automation iff v >= v_MB = F/(T_A[(1+ups)cV0 + kO cH + zO - cQ])", bad_mb == 0)
check("3e  (e) AI-executed status (in-house A or AI-enabled vendor) never reverts as pi falls", bad_aiexec == 0)

# ==============================================================================================
header("4. Optimal review (Proposition prop:tasks-review)")
# ==============================================================================================
xi_s, e_s, L_s, wtR_s = sp.symbols("xi e L wtR", positive=True)
Kxi = wtR_s * xi_s + e_s * L_s * (1 - xi_s * (1 + sp.log(1 / xi_s)))
check("4a  K'(xi) = w tR - e L ln(1/xi)", is_zero(sp.diff(Kxi, xi_s) - (wtR_s - e_s * L_s * sp.log(1 / xi_s))))
check("4b  K''(xi) = e L / xi > 0", is_zero(sp.diff(Kxi, xi_s, 2) - e_s * L_s / xi_s))
xiE = sp.exp(-wtR_s / (e_s * L_s))
check("4c  K'(xi^E) = 0 at xi^E = exp(-w tR/(e L))", is_zero(sp.diff(Kxi, xi_s).subs(xi_s, xiE)))
check("4d  K(xi^E) = e L (1 - xi^E)", is_zero(sp.simplify(Kxi.subs(xi_s, xiE) - e_s * L_s * (1 - xiE))))
# K(xi) as E[review cost + loss] for threshold policy: z ~ Exp(1), review z >= ln(1/xi)
zz = sp.symbols("z", positive=True)
a_ = sp.log(1 / xi_s)
loss_int = sp.integrate(zz * sp.exp(-zz), (zz, 0, a_))
check("4e  E[z 1{z < ln(1/xi)}] = 1 - xi(1 + ln(1/xi)) for z ~ Exp(1)",
      is_zero(sp.simplify(loss_int - (1 - xi_s * (1 + sp.log(1 / xi_s))))))
# threshold policy beats random/other selection rules with the same review fraction (Monte Carlo)
z = RNG.exponential(1.0, 400000)
err = RNG.uniform(size=z.size) < 0.2
bad_sel = 0
for xi in [0.1, 0.3, 0.6]:
    thr = np.quantile(z, 1 - xi)
    lt = np.mean(z * err * (z < thr))
    rnd = RNG.uniform(size=z.size) < xi
    lr = np.mean(z * err * (~rnd))
    mid = (z > np.quantile(z, 0.2)) & (z <= np.quantile(z, 0.2 + xi))
    lm = np.mean(z * err * (~mid))
    if not (lt < lr and lt < lm):
        bad_sel += 1
    if abs(lt - 0.2 * (1 - xi * (1 + math.log(1 / xi)))) > 5e-3:
        bad_sel += 1
check("4f  top-stakes review minimizes undetected loss for a given review share; MC matches closed form", bad_sel == 0)
bad_opt = bad_cs = bad_lim = bad_smin = bad_env = bad_mono_c = bad_eps = 0
for _ in range(500):
    e, L, wtR = RNG.uniform(0.005, 0.6), RNG.uniform(1, 200), RNG.uniform(0.1, 10)
    epsb, ximin = RNG.uniform(0.001, 0.1), RNG.choice([0.0, RNG.uniform(0, 0.3)])
    xi, cQ, eps = review(e, L, wtR, epsb, ximin)
    lo = max(1 - epsb / e, ximin, 1e-12)
    res = optimize.minimize_scalar(lambda x: quality_cost(x, e, L, wtR), bounds=(lo, 1.0), method="bounded",
                                   options={"xatol": 1e-12})
    if quality_cost(xi, e, L, wtR) > res.fun + 1e-7 * max(1, res.fun):
        bad_opt += 1
    if eps > epsb + 1e-12 or xi < ximin - 1e-12:
        bad_opt += 1
    # comparative statics: xi* nondecreasing in e, L, qbar (i.e. decreasing in epsbar), ximin; nonincreasing in wtR
    f = lambda **kw: review(**{**dict(e=e, L=L, wtR=wtR, epsbar=epsb, ximin=ximin), **kw})[0]
    if not (f(e=e * 1.1) >= xi - 1e-12 and f(L=L * 1.1) >= xi - 1e-12 and f(epsbar=epsb * 0.9) >= xi - 1e-12
            and f(ximin=ximin + 0.05) >= xi - 1e-12 and f(wtR=wtR * 1.1) <= xi + 1e-12):
        bad_cs += 1
    # quality cost strictly increasing in e; undetected error rate nondecreasing in e
    c2 = review(e * 1.05, L, wtR, epsb, ximin)
    if not c2[1] > cQ:
        bad_mono_c += 1
    if c2[2] < eps - 1e-12:
        bad_eps += 1
    # smooth minimum when only the economic term binds
    xi0, cQ0, _ = review(e, L, wtR, 1.0, 0.0)
    if not (cQ0 <= min(e * L, wtR) + 1e-12 and close(cQ0, e * L * (1 - math.exp(-wtR / (e * L))))):
        bad_smin += 1
    # envelope: dcQ/de = L [1 - xi(1 + ln 1/xi)] when the economic term binds (interior)
    h = 1e-7 * e
    fd = (review(e + h, L, wtR, 1.0, 0.0)[1] - review(e - h, L, wtR, 1.0, 0.0)[1]) / (2 * h)
    an = L * (1 - xi0 * (1 + math.log(1 / xi0)))
    if abs(fd - an) > 1e-5 * max(1, an):
        bad_env += 1
    # limit e -> 0: xi* -> ximin and cQ -> ximin wtR
    xs, cs, _ = review(1e-10, L, wtR, epsb, ximin)
    if not (abs(xs - ximin) < 1e-9 and abs(cs - ximin * wtR) < 1e-4 * max(1, wtR)):
        bad_lim += 1
check("4g  (a) xi* = max{xi^E, xi^R, ximin} minimizes K on the feasible set (500 draws)", bad_opt == 0,
      f"violations={bad_opt}")
check("4h  (c) xi* nondecreasing in e, L, qbar, ximin; nonincreasing in w tR", bad_cs == 0, f"violations={bad_cs}")
check("4i  (c) quality cost strictly increasing in e; undetected rate e(1-xi*) nondecreasing in e",
      bad_mono_c == 0 and bad_eps == 0, f"{bad_mono_c},{bad_eps}")
check("4j  (b) unconstrained cQ = eL(1 - exp(-w tR/(eL))) <= min(eL, w tR)", bad_smin == 0)
check("4k  (c) envelope dcQ/de = L[1 - xi*(1 + ln(1/xi*))] (economic term binding)", bad_env == 0)
check("4l  (d) as e -> 0: xi* -> ximin and cQ -> ximin w tR", bad_lim == 0)
# xi^E vanishes faster than any power of e
check("4m  (d) exp(-c/e)/e^k -> 0 as e -> 0 for every k", is_zero(sp.limit(sp.exp(-1 / e_s) / e_s**7, e_s, 0)))
# --- detection rate d^R (modern map, ranked change 1) ---------------------------------------------
d_s = sp.symbols("d", positive=True)
Kd = wtR_s * xi_s + e_s * L_s * (1 - d_s * xi_s * (1 + sp.log(1 / xi_s)))
xiEd = sp.exp(-wtR_s / (d_s * e_s * L_s))
check("4n  (a) with detection d: K'(xi) = w tR - d e L ln(1/xi), K'' = d e L/xi > 0, zero at exp(-w tR/(d e L)), "
      "K(xi^E) = e L (1 - d xi^E)",
      is_zero(sp.diff(Kd, xi_s) - (wtR_s - d_s * e_s * L_s * sp.log(1 / xi_s)))
      and is_zero(sp.diff(Kd, xi_s, 2) - d_s * e_s * L_s / xi_s) and is_zero(sp.diff(Kd, xi_s).subs(xi_s, xiEd))
      and is_zero(sp.simplify(Kd.subs(xi_s, xiEd) - e_s * L_s * (1 - d_s * xiEd))))
bad_dmc = 0
for dd in [0.455, 0.65, 0.9]:
    for xi in [0.2, 0.5, 0.8]:
        thr = np.quantile(z, 1 - xi)
        rev_ = z >= thr
        det_ = RNG.uniform(size=z.size) < dd
        miss = err & ~(rev_ & det_)
        if abs(np.mean(z * miss) - 0.2 * (1 - dd * xi * (1 + math.log(1 / xi)))) > 5e-3:
            bad_dmc += 1
        if abs(np.mean(miss) - 0.2 * (1 - dd * xi)) > 3e-3:
            bad_dmc += 1
check("4o  (a) top-stakes review with detection d: undetected loss e L[1 - d xi(1+ln 1/xi)], undetected rate e(1 - d xi) (MC)",
      bad_dmc == 0, f"violations={bad_dmc}")
bad_dopt = bad_dfeas = bad_dcs = bad_deps = bad_db = 0
n_infeas = 0
for _ in range(600):
    e, L, wtR = RNG.uniform(0.005, 0.6), RNG.uniform(1, 200), RNG.uniform(0.1, 10)
    epsb, ximin = RNG.uniform(0.001, 0.1), RNG.choice([0.0, RNG.uniform(0, 0.3)])
    dd = RNG.uniform(0.2, 1.0)
    feasible = dd >= 1 - epsb / e
    grid_x = np.linspace(0, 1, 2001)
    any_ok = np.any(e * (1 - dd * grid_x) <= epsb + 1e-12)
    if feasible != any_ok:
        bad_dfeas += 1
    if not feasible:
        n_infeas += 1
        continue
    xi, cQ, eps = review(e, L, wtR, epsb, ximin, d=dd)
    lo = max((1 - epsb / e) / dd, ximin, 1e-12)
    res = optimize.minimize_scalar(lambda x: quality_cost(x, e, L, wtR, dd), bounds=(lo, 1.0), method="bounded",
                                   options={"xatol": 1e-12})
    if quality_cost(xi, e, L, wtR, dd) > res.fun + 1e-7 * max(1, res.fun) or eps > epsb + 1e-12:
        bad_dopt += 1
    # quality cost nonincreasing in d; economic share rises with d; reliability share falls with d
    d2 = min(1.0, dd * 1.05)
    if review(e, L, wtR, epsb, ximin, d=d2)[1] > cQ + 1e-9:
        bad_dcs += 1
    if not (math.exp(-wtR / (d2 * e * L)) >= math.exp(-wtR / (dd * e * L))
            and (e <= epsb or (1 - epsb / e) / d2 <= (1 - epsb / e) / dd + 1e-15)):
        bad_dcs += 1
    # undetected rate nondecreasing in e (where still feasible)
    e2 = e * 1.03
    if dd >= 1 - epsb / e2 and review(e2, L, wtR, epsb, ximin, d=dd)[2] < eps - 1e-12:
        bad_deps += 1
    # (b) economic-only: cQ = eL(1 - d xi^E) < min(eL, w tR + eL(1-d))
    xi0, cQ0, _ = review(e, L, wtR, 1.0, 0.0, d=dd)
    if not (close(cQ0, e * L * (1 - dd * math.exp(-wtR / (dd * e * L)))) and cQ0 < min(e * L, wtR + e * L * (1 - dd)) + 1e-12):
        bad_db += 1
check("4p  (d) detection threshold: the reliability target is attainable at some review share iff d >= 1 - epsbar/e "
      f"(600 draws, {n_infeas} infeasible)", bad_dfeas == 0 and n_infeas > 50, f"violations={bad_dfeas}")
check("4q  (a) with detection d, xi* = max{exp(-w tR/(d e L)), (1 - epsbar/e)/d, ximin} minimizes K on the feasible set",
      bad_dopt == 0, f"violations={bad_dopt}")
check("4r  (c) quality cost nonincreasing in d; economic share rises and reliability share falls with d; undetected rate "
      "nondecreasing in e", bad_dcs == 0 and bad_deps == 0, f"{bad_dcs},{bad_deps}")
check("4s  (b) economic term only: cQ = e L[1 - d exp(-w tR/(d e L))] < min{e L, w tR + e L(1 - d)}", bad_db == 0)
# example threshold: exceptions (e0=.45, e1=.03, qbar=.95) with d = 0.8 needs e <= 0.25, iota >= 0.476

# ==============================================================================================
header("5. Augment or automate: the activity readiness threshold (Proposition prop:tasks-augment)")
# ==============================================================================================
bad_thr = bad_xiAU = bad_dom = 0
n_dom = 0
for _ in range(300):
    e0, e1 = RNG.uniform(0.1, 0.6), RNG.uniform(0.001, 0.05)
    L, wt = RNG.uniform(5, 100), RNG.uniform(1, 10)
    wtR, wtU = RNG.uniform(0.3, 0.9) * wt, RNG.uniform(0.5, 0.95) * wt
    epsb = RNG.uniform(0.005, 0.05)
    piN, piNU, fix = RNG.uniform(0, 0.5) * wt, RNG.uniform(0, 0.1) * wt, RNG.uniform(0, 0.3) * wt
    iolow = RNG.uniform(0, 0.5)
    eU = RNG.uniform(-0.02, 0.05)
    cU = wtU + piNU + eU * L
    cA = lambda io: piN + review(e1 + (e0 - e1) * (1 - io), L, wtR, epsb)[1] + fix
    grid = np.linspace(0, 1, 1001)
    modes = ["A" if (io >= iolow and cA(io) <= cU) else "U" for io in grid]
    # single switch from U to A
    switches = sum(1 for a, b in zip(modes[:-1], modes[1:]) if a != b)
    if switches > 1 or (switches == 1 and modes[0] == "A"):
        bad_thr += 1
    # necessary condition: A beats U only if xi* < xi^AU = (wtU + piNU - piN - fix)/wtR
    for io in grid[::100]:
        e = e1 + (e0 - e1) * (1 - io)
        xi = review(e, L, wtR, epsb)[0]
        if cA(io) <= cU and not xi * wtR <= cU - piN - fix + 1e-12:
            bad_xiAU += 1
    # (d) decision tasks: with tR = tU, A (optimal review, detection d) beats U whenever
    #     (eU - e(1-d)) L >= pi(n - nU) + F/(vT) and the target is attainable
    dd = RNG.uniform(0.4, 1.0)
    for io in grid[::50]:
        e = e1 + (e0 - e1) * (1 - io)
        if dd < 1 - epsb / e:
            continue
        cU_same = wtR + piNU + eU * L
        cA_d = piN + review(e, L, wtR, epsb, 0.0, d=dd)[1] + fix
        if (eU - e * (1 - dd)) * L >= piN - piNU + fix:
            n_dom += 1
            if cA_d > cU_same + 1e-9:
                bad_dom += 1
check("5a  (b) optimal mode switches once, from U to A, at iota* = max(iota_min, iota^c) (300 draws)", bad_thr == 0)
check("5b  (c) A beats U only if xi* w tR <= w tU + eU L + pi(nU - n) - F/(vT)", bad_xiAU == 0)
check(f"5c  (d) decision tasks: with tR = tU, (eU - e(1-d))L >= pi(n-nU) + F/(vT) implies c(A) <= c(U) ({n_dom} cases)",
      bad_dom == 0 and n_dom > 20, f"violations={bad_dom}")

# ==============================================================================================
header("6. Process complementarity (Proposition prop:tasks-complement)")
# ==============================================================================================
def make_process(J, edges, rng, ratio_side=None, homog_ratio=None, Xi=None, crit=None):
    P = dict(J=J, edges=edges)
    P["u"] = rng.uniform(-3, 3, J)  # unit savings v_j (c_M - c_A)
    P["eMM"] = rng.uniform(0, 1, len(edges))
    P["eAM"] = P["eMM"] + rng.uniform(-0.2, 1, len(edges))
    P["eMA"] = P["eMM"] + rng.uniform(-0.2, 1, len(edges))
    # integration premium eta^x = eAM + eMA - eAA - eMM >= 0
    P["eAA"] = np.maximum(0, P["eAM"] + P["eMA"] - P["eMM"] - rng.uniform(0, 1.5, len(edges)))
    P["eAA"] = np.minimum(P["eAA"], P["eAM"] + P["eMA"] - P["eMM"])
    P["qM"] = rng.uniform(0.9, 0.999, J)
    if homog_ratio is not None:
        P["qA"] = P["qM"] * homog_ratio
    elif ratio_side == "up":
        P["qA"] = np.minimum(1.0, P["qM"] * rng.uniform(1, 1.1, J))
    else:
        P["qA"] = P["qM"] * rng.uniform(0.9, 1.0, J)
    P["vL"] = rng.uniform(0, 5)
    P["Xi"] = rng.uniform(0, 3) if Xi is None else Xi
    P["crit"] = set(range(J)) if crit is None else crit
    return P


def Wp(P, Z):
    Z = set(Z)
    val = sum(P["u"][j] for j in Z)
    for k, (i, j) in enumerate(P["edges"]):
        yi, yj = i in Z, j in Z
        eta = P["eAA"][k] if (yi and yj) else (P["eAM"][k] if yi else (P["eMA"][k] if yj else P["eMM"][k]))
        val += P["eMM"][k] - eta
    Q = np.prod([P["qA"][j] if j in Z else P["qM"][j] for j in range(P["J"])])
    val += P["vL"] * (Q - np.prod(P["qM"]))
    val += P["Xi"] * (1.0 if P["crit"] <= Z else 0.0) - P["Xi"] * (1.0 if P["crit"] <= set() else 0.0)
    return val


def subsets(J):
    for r in range(J + 1):
        for Z in itertools.combinations(range(J), r):
            yield frozenset(Z)


def chain_edges(J):
    return [(i, i + 1) for i in range(J - 1)]


bad_sm = bad_dec = 0
for trial in range(120):
    J = int(RNG.integers(2, 6))
    allpairs = [(i, j) for i in range(J) for j in range(i + 1, J)]
    edges = chain_edges(J) + [e for e in allpairs if e[1] > e[0] + 1 and RNG.uniform() < 0.3]
    P = make_process(J, edges, RNG, ratio_side="up" if trial % 2 else "down",
                     crit=set(RNG.choice(J, size=int(RNG.integers(1, J + 1)), replace=False).tolist()))
    S = list(subsets(J))
    vals = {Z: Wp(P, Z) for Z in S}
    for A in S:
        for B in S:
            if vals[A | B] + vals[A & B] < vals[A] + vals[B] - 1e-9:
                bad_sm += 1
    # decomposition of the handoff part: W_eta(Z) = sum_{j in Z} W_eta({j}) + sum_{e in Z} eta^x
    P0 = dict(P); P0["u"] = np.zeros(J); P0["vL"] = 0.0; P0["Xi"] = 0.0
    for Z in S:
        lhs = Wp(P0, Z)
        rhs = sum(Wp(P0, frozenset([j])) for j in Z) + sum(
            P["eAM"][k] + P["eMA"][k] - P["eAA"][k] - P["eMM"][k] for k, (i, j) in enumerate(edges) if i in Z and j in Z)
        if abs(lhs - rhs) > 1e-9:
            bad_dec += 1
check("6a  (a) W_p supermodular under eta^x >= 0, same-direction reliability changes, overhead Xi_p (120 processes)",
      bad_sm == 0, f"violations={bad_sm}")
check("6b  (b) handoff decomposition W(Z) = sum_j W({j}) + sum_{e in Z} v_e eta^x_e", bad_dec == 0)
# Topkis: as pi falls, the largest optimal automated set expands
bad_top = 0
for trial in range(80):
    J = int(RNG.integers(2, 6))
    P = make_process(J, chain_edges(J), RNG, ratio_side="up")
    base_u = RNG.uniform(-4, 1, J)
    nint = RNG.uniform(0.1, 1, J)
    prev = None
    for p in np.linspace(5, 0, 26):
        P["u"] = base_u + (5 - p) * nint  # unit savings rise as pi falls
        vals = {Z: Wp(P, Z) for Z in subsets(J)}
        m = max(vals.values())
        largest = frozenset().union(*[Z for Z, val in vals.items() if val >= m - 1e-9])
        if prev is not None and not prev <= largest:
            bad_top += 1
        prev = largest
check("6c  (c) Topkis: largest optimal automated set is nested and expands as pi falls (80 processes x 26 prices)",
      bad_top == 0)

# ==============================================================================================
header("7. All-or-nothing (Proposition prop:tasks-aon)")
# ==============================================================================================
def h_const(J, edges, wts):
    tot = sum(wts)
    best = np.inf
    for r in range(1, J):
        for Z in itertools.combinations(range(J), r):
            Zs = set(Z)
            inside = sum(w for (i, j), w in zip(edges, wts) if i in Zs and j in Zs)
            D = (r / J) * tot - inside
            best = min(best, D * J / (r * (J - r)))
    return best


c = 1.3
ok_h = True
for J in range(2, 9):
    hc = h_const(J, chain_edges(J), [c] * (J - 1))
    star = [(0, i) for i in range(1, J)]
    hs = h_const(J, star, [c] * (J - 1))
    ok_h &= close(hc, c / (J - 1), 1e-12) and close(hs, c / (J - 1), 1e-12)
    if J >= 3:
        cyc = chain_edges(J) + [(J - 1, 0)]
        hy = h_const(J, cyc, [c] * J)
        target = 4 * c / J if J % 2 == 0 else 4 * c * J / (J**2 - 1)
        ok_h &= close(hy, target, 1e-12)
    comp = [(i, j) for i in range(J) for j in range(i + 1, J)]
    ok_h &= close(h_const(J, comp, [c] * len(comp)), c * J / 2, 1e-12)
# random trees
for _ in range(40):
    J = int(RNG.integers(3, 9))
    tree = [(int(RNG.integers(0, i)), i) for i in range(1, J)]
    ok_h &= close(h_const(J, tree, [c] * (J - 1)), c / (J - 1), 1e-12)
check("7a  (b) h_p = c/(J-1) for chains, stars and 40 random trees; 4c/J (cycle, J even), 4cJ/(J^2-1) (odd); cJ/2 (complete)",
      ok_h)

bad_aon = 0
count = 0
for trial in range(300):
    J = int(RNG.integers(2, 7))
    kind = trial % 3
    if kind == 0:
        edges = chain_edges(J)
    elif kind == 1:
        edges = [(int(RNG.integers(0, i)), i) for i in range(1, J)]
    else:
        edges = [(i, j) for i in range(J) for j in range(i + 1, J) if RNG.uniform() < 0.6] or chain_edges(J)
        # keep connected by adding a chain
        edges = sorted(set(edges) | set(chain_edges(J)))
    P = make_process(J, edges, RNG, homog_ratio=RNG.uniform(0.95, 1.04), Xi=RNG.uniform(0, 2))
    P["qA"] = np.minimum(P["qA"], 1.0)
    ratio = P["qA"] / P["qM"]
    P["qA"] = P["qM"] * ratio.min()  # enforce a common ratio
    wx = [P["eAM"][k] + P["eMA"][k] - P["eAA"][k] - P["eMM"][k] for k in range(len(edges))]
    hp = h_const(J, edges, wx)
    bound = hp + P["Xi"] / max(J - 1, 1)
    if bound < 0:  # dense sub-cluster: the sufficient condition cannot hold, so the draw is outside the claim
        continue
    # choose stand-alone values with dispersion <= h_p + Xi/(J-1)
    singles_target = RNG.uniform(-2, 2) + RNG.uniform(0, 1, J) * bound
    # set u so that W({j}) = singles_target[j]
    P["u"] = np.zeros(J)
    base = np.array([Wp(P, frozenset([j])) for j in range(J)])
    P["u"] = singles_target - base
    vals = {Z: Wp(P, Z) for Z in subsets(J)}
    WJ = vals[frozenset(range(J))]
    for Z, val in vals.items():
        if val > (len(Z) / J) * WJ + 1e-9:
            bad_aon += 1
    count += 1
check(f"7b  (a) under dispersion <= h_p + Xi/(J-1): W(Z) <= (|Z|/J) W(J) for every Z ({count} processes: chains, trees, dense)",
      bad_aon == 0 and count > 200, f"violations={bad_aon}")
# sharpness for chains
ok_sharp = True
for J in range(2, 10):
    for Dl in [c / (J - 1) * 1.01, c / (J - 1) * 2, 3 * c]:
        wh = (Dl - (J - 1) * c) / J
        wl = wh - Dl
        w = np.array([wh] * (J - 1) + [wl])
        def Wchain(Z):
            return sum(w[j] for j in Z) + sum(c for (i, j) in chain_edges(J) if i in Z and j in Z)
        Z = frozenset(range(J - 1))
        ok_sharp &= abs(Wchain(frozenset(range(J)))) < 1e-9 and Wchain(Z) > 1e-12
        ok_sharp &= close(Wchain(Z), ((J - 1) * Dl - c) / J, 1e-9)
    # at the bound the construction gives W(Z) = 0 exactly
    Dl = c / (J - 1)
    wh = (Dl - (J - 1) * c) / J
    w = np.array([wh] * (J - 1) + [wh - Dl])
    ok_sharp &= abs(sum(w[:J - 1]) + (J - 2) * c) < 1e-9
check("7c  (c) sharpness: chain with dispersion > c/(J-1) and W(J) = 0 has W(J minus last) = ((J-1)D - c)/J > 0",
      ok_sharp)

# ==============================================================================================
header("8. Value of full integration and the O-ring (Proposition prop:tasks-integration, Lemma lem:tasks-oring)")
# ==============================================================================================
bad_int = bad_weier = 0
for trial in range(200):
    J = int(RNG.integers(2, 7))
    P = make_process(J, chain_edges(J), RNG, ratio_side="up" if trial % 2 else "down", Xi=RNG.uniform(0, 3))
    full = frozenset(range(J))
    WJ = Wp(P, full)
    comp = (np.sum(P["u"]) + np.sum(P["eMM"] - P["eAA"]) + P["vL"] * (np.prod(P["qA"]) - np.prod(P["qM"]))
            + P["Xi"])
    if abs(WJ - comp) > 1e-9:
        bad_int += 1
    prem = WJ - sum(Wp(P, frozenset([j])) for j in range(J))
    ex = np.sum(P["eAM"] + P["eMA"] - P["eAA"] - P["eMM"])
    rho = P["qA"] / P["qM"]
    oring = P["vL"] * np.prod(P["qM"]) * (np.prod(rho) - 1 - np.sum(rho - 1))
    if abs(prem - (ex + oring + (P["Xi"] if J >= 2 else 0))) > 1e-9 or oring < -1e-12:
        bad_int += 1
    x = RNG.uniform(0, 1, J) * (1 if trial % 2 else -1)
    if np.prod(1 + x) < 1 + np.sum(x) - 1e-12:
        bad_weier += 1
check("8a  (a) W(J) = unit + coordination + reliability + overhead dividends (200 chains)", bad_int == 0)
check("8b  (b) W(J) - sum_j W({j}) = sum_e v_e eta^x_e + O-ring interaction (>= 0) + Xi_p", bad_int == 0)
check("8c  Weierstrass: prod(1+x_j) >= 1 + sum x_j for same-sign x_j in [-1, inf)", bad_weier == 0)
qb = sp.symbols("qbar", positive=True)
ok_or = True
for Jn in [2, 5, 10, 50]:
    for qv in [0.9, 0.95, 0.99, 0.999]:
        tol = 1 - qv ** (1 / Jn)
        ok_or &= (1 - qv) / Jn <= tol + 1e-15 and tol <= -math.log(qv) / Jn + 1e-15
        ok_or &= close((1 - tol) ** Jn, qv, 1e-12)
check("8d  (a) per-step tolerance 1 - qbar^(1/J) in [(1-qbar)/J, -ln(qbar)/J]", ok_or)
tol10 = 1 - 0.99 ** 0.1
check("8e  example: a 10-step chain at 99% needs per-step error below 0.1005%", abs(tol10 - 0.001005) < 1e-6,
      f"{tol10:.6f}")
bad_pos = 0
for _ in range(300):
    eps1 = RNG.uniform(1e-4, 0.05); growth = RNG.uniform(0, 0.3); qb_ = RNG.uniform(0.8, 0.999)
    eps_k = lambda k: min(0.999, eps1 * (1 + growth) ** (k - 1))  # nondecreasing in position
    Jpos = 0
    while sum(-math.log(1 - eps_k(k)) for k in range(1, Jpos + 2)) <= -math.log(qb_):
        Jpos += 1
    Jcom = math.floor(math.log(qb_) / math.log(1 - eps1))
    meets = lambda J_: np.prod([1 - eps_k(k) for k in range(1, J_ + 1)]) >= qb_
    if Jpos > Jcom or not meets(Jpos) or meets(Jpos + 1):
        bad_pos += 1
check("8g  (a) step-specific errors: target met iff sum -ln(1 - eps_k) <= -ln qbar; with eps_k nondecreasing in position "
      "the common-eps_1 length bound is an overstatement (300 draws)", bad_pos == 0)
q1, q2, q3 = sp.symbols("q1 q2 q3", positive=True)
Qs = q1 * q2 * q3
check("8f  (b) dQ/dq_j = Q/q_j and d2Q/dq_i dq_j = Q/(q_i q_j) > 0",
      is_zero(sp.diff(Qs, q1) - Qs / q1) and is_zero(sp.diff(Qs, q1, q2) - Qs / (q1 * q2)))

# ==============================================================================================
header("9. Straight-through rate (Lemma lem:tasks-stp)")
# ==============================================================================================
xis = np.array([0.1, 0.25, 0.05, 0.4])
a = np.log(1 / xis)
N = 400000
zi = RNG.exponential(1, (N, 4))
stp_ind = np.mean(np.all(zi < a, axis=1))
zc = RNG.exponential(1, N)
stp_com = np.mean(np.all(zc[:, None] < a, axis=1))
# positively dependent: Gaussian copula with correlation 0.6 mapped to Exp(1)
Cm = 0.6 * np.ones((4, 4)) + 0.4 * np.eye(4)
g = RNG.multivariate_normal(np.zeros(4), Cm, N)
ze = -np.log(stats.norm.sf(g))
stp_pos = np.mean(np.all(ze < a, axis=1))
prod, mn = np.prod(1 - xis), np.min(1 - xis)
check("9a  independent stakes: STP = prod(1 - xi_j)", abs(stp_ind - prod) < 3e-3, f"{stp_ind:.4f} vs {prod:.4f}")
check("9b  common stakes: STP = min(1 - xi_j)", abs(stp_com - mn) < 3e-3, f"{stp_com:.4f} vs {mn:.4f}")
check("9c  positively associated stakes: prod <= STP <= min", prod - 3e-3 <= stp_pos <= mn + 3e-3,
      f"{prod:.4f} <= {stp_pos:.4f} <= {mn:.4f}")

# ==============================================================================================
header("10. Stylized test chain (formula checks; the paper's example is Section 23)")
# ==============================================================================================
EX = dict(w=45.0, t=np.array([0.05, 0.08, 0.12, 0.05]), v=120000.0,
          Ofeas=np.array([1, 1, 0, 0], bool), pO_share=0.45, kO=0.10, zO=0.30, tU_share=0.75, piNU=0.05,
          piN=np.array([0.10, 0.15, 0.50, 0.10]), tR_share=0.8,
          e0=np.array([0.15, 0.20, 0.45, 0.10]), e1=np.array([0.005, 0.01, 0.03, 0.005]),
          L=np.array([15., 40., 60., 80.]), qbar=np.array([0.98, 0.98, 0.95, 0.99]),
          FA=np.array([120e3, 120e3, 200e3, 80e3]), TA=3.0,
          etaMM=0.40, etaAM=0.70, etaAA0=0.50, Lp=20.0, qM=0.998, Xi=120e3,
          det=np.array([1.0, 1.0, 0.8, 1.0]))
X_ = EX
cH_ex = X_["w"] * X_["t"]
cO_ex = (X_["pO_share"] + X_["kO"]) * cH_ex + X_["zO"]
cU_ex = X_["tU_share"] * cH_ex + X_["piNU"]
cM_ex = np.where(X_["Ofeas"], np.minimum(cO_ex, cU_ex), cU_ex)
cM_ex = np.minimum(cM_ex, cH_ex)


def ex_acts(iota, pi_scale=1.0, Kcharge=0.0):
    out = []
    for j in range(4):
        e = X_["e1"][j] + (X_["e0"][j] - X_["e1"][j]) * (1 - iota)
        xi, cQ, eps = review(e, X_["L"][j], X_["w"] * X_["tR_share"] * X_["t"][j], 1 - X_["qbar"][j], d=X_["det"][j])
        cA = pi_scale * X_["piN"][j] + cQ + X_["FA"][j] / (X_["v"] * X_["TA"]) + Kcharge
        out.append(dict(e=e, xi=xi, cQ=cQ, eps=eps, cA=cA))
    return out


def ex_feasible(iota, j):
    """Automation of step j can meet its reliability target at some review share (Prop review(d))."""
    e = X_["e1"][j] + (X_["e0"][j] - X_["e1"][j]) * (1 - iota)
    return X_["det"][j] >= 1 - (1 - X_["qbar"][j]) / e - 1e-12


def ex_W(Z, iota, pi_scale=1.0, require_feasible=False):
    a_ = ex_acts(iota, pi_scale)
    v = X_["v"]
    if require_feasible and not all(ex_feasible(iota, j) for j in Z):
        return -np.inf
    val = sum(v * (cM_ex[j] - a_[j]["cA"]) for j in Z)
    etaAA = X_["etaAA0"] * (1 - iota)
    for (i, j) in chain_edges(4):
        yi, yj = i in Z, j in Z
        eta = etaAA if (yi and yj) else (X_["etaAM"] if (yi or yj) else X_["etaMM"])
        val += v * (X_["etaMM"] - eta)
    Q0 = X_["qM"] ** 4
    Q = np.prod([(1 - a_[j]["eps"]) if j in Z else X_["qM"] for j in range(4)])
    val += v * X_["Lp"] * (Q - Q0)
    if len(set(Z)) == 4:
        val += X_["Xi"]
    return val


full4 = frozenset(range(4))
EH = X_["v"] * cH_ex.sum()
EM = X_["v"] * cM_ex.sum() + 3 * X_["v"] * X_["etaMM"]
print(f"     c_H = {np.round(cH_ex, 3)}, c_O = {np.round(cO_ex, 3)}, c_U = {np.round(cU_ex, 3)}, c_M = {np.round(cM_ex, 3)}")
print(f"     in-house labor-equivalent spend E = {EH:,.0f}; low-cost manual chain cost incl. handoffs = {EM:,.0f}")
istar = optimize.brentq(lambda i: ex_W(full4, i), 0.5, 1.0, xtol=1e-12)
a04, a09 = ex_acts(0.4), ex_acts(0.9)
print(f"     iota=0.4: e={[round(x['e'],3) for x in a04]}, xi={[round(x['xi'],3) for x in a04]}, cA={[round(x['cA'],2) for x in a04]}")
print(f"     iota=0.9: e={[round(x['e'],3) for x in a09]}, xi={[round(x['xi'],3) for x in a09]}, cA={[round(x['cA'],2) for x in a09]}")
W04, W09 = ex_W(full4, 0.4), ex_W(full4, 0.9)
print(f"     W(full) at 0.4 = {W04:,.0f}, at 0.9 = {W09:,.0f}; iota*_p = {istar:.4f}")
iota_feas3 = 1 - ((1 - X_["qbar"][2]) / (1 - X_["det"][2]) - X_["e1"][2]) / (X_["e0"][2] - X_["e1"][2])
singles09 = [ex_W(frozenset([j]), 0.9) for j in range(4)]
print(f"     stand-alone values at 0.9: {[round(s_) for s_ in singles09]}")
# all proper subsets have negative value on a neighborhood of the threshold (percolation / all-or-nothing)
ok_aon_ex = True
for io in np.linspace(istar - 0.1, 0.853, 31):
    vals = {Z: ex_W(Z, io, require_feasible=True) for Z in subsets(4)}
    best = max(vals, key=vals.get)
    if io > istar + 1e-6:
        ok_aon_ex &= best == full4
    elif io < istar - 1e-6:
        ok_aon_ex &= vals[best] <= 1e-6
    ok_aon_ex &= all(val < 0 for Z, val in vals.items() if 0 < len(Z) < 4)
first_pos = min(io for io in np.linspace(0.5, 1.0, 5001)
                if any(ex_W(Z, io) > 0 for Z in subsets(4) if 0 < len(Z) < 4))
best_above = all(max(subsets(4), key=lambda Z: ex_W(Z, io, require_feasible=True)) == full4
                 for io in np.linspace(istar + 1e-4, 1.0, 60))
print(f"     first proper subset with positive value at iota = {first_pos:.4f}")
# readiness monotonicity and big push
Wg = np.array([ex_W(full4, io) for io in np.linspace(0, 1, 201)])
check("10f (a) W_p(J; iota) strictly increasing in iota (stylized test chain)", np.all(np.diff(Wg) > 0))
# integration decomposition at 0.9
a_ = a09
unit = X_["v"] * np.sum(cM_ex - np.array([x["cA"] for x in a_]))
coord = 3 * X_["v"] * (X_["etaMM"] - X_["etaAA0"] * 0.1)
rel = X_["v"] * X_["Lp"] * (np.prod([1 - x["eps"] for x in a_]) - X_["qM"] ** 4)
print(f"     dividends at 0.9: unit {unit:,.0f}, coordination {coord:,.0f}, reliability {rel:,.0f}, overhead {X_['Xi']:,.0f}")
Q09 = np.prod([1 - x["eps"] for x in a_])
print(f"     process reliability at 0.9: automated {Q09:.4f} vs manual {X_['qM']**4:.4f}; "
      f"residual step errors {[round(x['eps'], 4) for x in a_]}")
# exceptions step activity threshold vs augmentation
c3U = cU_ex[2]
ist3 = optimize.brentq(lambda i: ex_acts(i)[2]["cA"] - c3U, 0.5, 1.0)
print(f"     exceptions step: c_U = {c3U:.3f}, c_A(0.9) = {a09[2]['cA']:.3f}, iota*_3 = {ist3:.4f}")
# detection-rate sweep for exceptions at 0.9 (modern map, ranked change 1)
def exc_cost(dd, iota=0.9):
    e = X_["e1"][2] + (X_["e0"][2] - X_["e1"][2]) * (1 - iota)
    xi, cQ, eps = review(e, X_["L"][2], X_["w"] * X_["tR_share"] * X_["t"][2], 1 - X_["qbar"][2], d=dd)
    return X_["piN"][2] + cQ + X_["FA"][2] / (X_["v"] * X_["TA"]), eps
e09 = X_["e1"][2] + (X_["e0"][2] - X_["e1"][2]) * 0.1
dmin = 1 - (1 - X_["qbar"][2]) / e09
sweep = {dd: exc_cost(dd)[0] for dd in [1.0, 0.9, 0.8, 0.455]}
print(f"     exceptions at 0.9 by detection rate: {dict((k, round(v_, 3)) for k, v_ in sweep.items())}; infeasible below d = {dmin:.4f}")

# ==============================================================================================
header("11. Readiness threshold, weakest link, big push (Proposition prop:tasks-readiness)")
# ==============================================================================================
# (c) marginal value of readiness highest at the least-ready step when q(iota) is increasing and concave
bad_wl = 0
for _ in range(200):
    J = int(RNG.integers(2, 6))
    io = np.sort(RNG.uniform(0, 1, J))
    q = lambda x: 1 - 0.3 * (1 - x) ** 2 - 0.01
    qp = lambda x: 0.6 * (1 - x)
    Q = np.prod([q(x) for x in io])
    mv = [Q * qp(x) / q(x) for x in io]
    if np.argmax(mv) != 0:
        bad_wl += 1
check("11a (c) marginal value of readiness dQ/d iota_j = Q q'(iota_j)/q(iota_j) is largest at the least-ready step",
      bad_wl == 0)
# (d) big push: with W(iota) <= 0 below iota* and I increasing, optimal iota is iota0 or >= iota*
bad_bp = 0
for _ in range(200):
    ist = RNG.uniform(0.3, 0.9)
    slope, curv = RNG.uniform(0.5, 3), RNG.uniform(0.1, 5)
    io0 = RNG.uniform(0, ist)
    Wfun = lambda x: np.maximum(0, slope * (x - ist) + (x > ist) * 0.0) * (x >= ist)
    Ifun = lambda x: curv * (x - io0) ** 2
    grid = np.linspace(io0, 1, 2001)
    obj = Wfun(grid) / 0.1 - Ifun(grid)
    best = grid[np.argmax(obj)]
    if io0 + 1e-9 < best < ist - 1e-9:
        bad_bp += 1
check("11b (d) big push: optimal readiness is iota0 or at least iota*_p (200 draws)", bad_bp == 0)

# ==============================================================================================
header("12. Capital per unit of work (Proposition prop:tasks-capital)")
# ==============================================================================================
r_s, g_s, dK_s, dc_s, DK_s, v0_s, t_s = sp.symbols("r g delta_K Dc DK v0 t", positive=True)
npv_exp = sp.integrate(sp.exp(-r_s * t_s) * (dc_s * v0_s * sp.exp(g_s * t_s)
                                              - DK_s * (g_s + dK_s) * v0_s * sp.exp(g_s * t_s)),
                       (t_s, 0, sp.oo), conds="none") - DK_s * v0_s
npv_exp = sp.simplify(npv_exp.subs(r_s, g_s + sp.Symbol("d", positive=True)))
target = v0_s * (dc_s - (sp.Symbol("d", positive=True) + g_s + dK_s) * DK_s) / sp.Symbol("d", positive=True)
check("12a (a) exponential volume, r = g + d: NPV = v0 [Dc - (r + delta_K) DK]/(r - g)", is_zero(npv_exp - target))
bad_path = 0
for _ in range(100):
    r, dK = RNG.uniform(0.05, 0.15), RNG.uniform(0.05, 0.5)
    dc, DK = RNG.uniform(0.1, 2), RNG.uniform(0.1, 3)
    v0, vmax, gg = RNG.uniform(1, 5), RNG.uniform(6, 20), RNG.uniform(0.05, 0.6)
    vt = lambda tt: vmax / (1 + (vmax / v0 - 1) * math.exp(-gg * tt))  # logistic, nondecreasing
    vdot = lambda tt: gg * vt(tt) * (1 - vt(tt) / vmax)
    flow = lambda tt: math.exp(-r * tt) * (dc * vt(tt) - DK * (vdot(tt) + dK * vt(tt)))
    npv = integrate.quad(flow, 0, 400, limit=400)[0] - DK * v0
    pv = integrate.quad(lambda tt: math.exp(-r * tt) * vt(tt), 0, 400, limit=400)[0]
    if abs(npv - (dc - (r + dK) * DK) * pv) > 1e-6 * max(1, abs(npv)):
        bad_path += 1
check("12b (a) any nondecreasing volume path: NPV = [Dc - (r + delta_K) DK] * PV_r(v) (100 logistic paths)",
      bad_path == 0)
# ranking regions
bad_rank = 0
for _ in range(2000):
    r, g, dK = RNG.uniform(0.04, 0.15), RNG.uniform(0, 0.6), RNG.uniform(0.05, 0.5)
    DK = RNG.uniform(0.1, 3)
    dc = RNG.uniform(0, 2)
    val, cash, gaap = dc - (r + dK) * DK, dc - (g + dK) * DK, dc - dK * DK
    if g < r and val > 0 and not cash > 0:
        bad_rank += 1
    if g > r and cash > 0 and not val > 0:
        bad_rank += 1
    if cash > 0 and not gaap > 0:
        bad_rank += 1
    # equal economic cost: cash prefers the capital-heavy mode iff g < r
    K1, K2 = RNG.uniform(0, 1), RNG.uniform(1, 3)
    c1 = RNG.uniform(1, 3); c2 = c1 - (r + dK) * (K2 - K1)
    cash_diff = (c2 + (g + dK) * K2) - (c1 + (g + dK) * K1)
    if (cash_diff < 0) != (g < r):
        bad_rank += 1
check("12c (c) ranking: g<r => value-creating switches raise the cash score; g>r => cash-raising switches create value; "
      "cash => GAAP; equal economic cost => cash prefers capital-heavy iff g<r", bad_rank == 0)
# example: Dc = 0.60, DK = 1.50, delta = 1/3, r = 0.10, g = 0.05
dc, DK, dK, r, g = 0.60, 1.50, 1 / 3, 0.10, 0.05
exv, exc, exg = dc - (r + dK) * DK, dc - (g + dK) * DK, dc - dK * DK
print(f"     capital example per unit: value {exv:+.4f}, cash {exc:+.4f}, GAAP {exg:+.4f}")

# ==============================================================================================
header("13. Transition value (Proposition prop:tasks-transition)")
# ==============================================================================================
def ramp_lin(u):
    return u


def transition_npv(P, Tpar, ramp=ramp_lin):
    r, Th = P["r"], P["Th"]
    A = (1 - math.exp(-r * Tpar)) / r if r > 0 else Tpar
    rampPV = integrate.quad(lambda tt: math.exp(-r * tt) * ramp(tt / Tpar), 0, Tpar)[0] if Tpar > 0 else 0.0
    tailPV = (math.exp(-r * Tpar) - math.exp(-r * Th)) / r if r > 0 else Th - Tpar
    pu = math.exp(-Tpar / P["Tdet"]) if Tpar > 0 else 1.0
    om = P["pis"]
    return (-(P["F"] + P["I"] + P["CJ"]) - P["Cpar"] * A + om * P["bbar"] * P["W"] * (rampPV + tailPV)
            - math.exp(-r * Tpar) * ((om + (1 - om) * pu) * P["Cstr"] + (1 - om) * pu * P["Lroll"]))


def simulate_npv(P, Tpar, nsim=200000, rng=RNG):
    r, Th = P["r"], P["Th"]
    succ = rng.uniform(size=nsim) < P["pis"]
    b = np.where(succ, rng.beta(P["bbar"] * 8, (1 - P["bbar"]) * 8, nsim), 0.0)
    det_time = rng.exponential(P["Tdet"], nsim)
    detected = (~succ) & (det_time < Tpar)
    A = (1 - math.exp(-r * Tpar)) / r
    rampPV = integrate.quad(lambda tt: math.exp(-r * tt) * (tt / Tpar), 0, Tpar)[0]
    tailPV = (math.exp(-r * Tpar) - math.exp(-r * Th)) / r
    npv = -(P["F"] + P["I"] + P["CJ"]) - P["Cpar"] * A + b * P["W"] * (rampPV + tailPV)
    npv -= np.where(detected, 0.0, math.exp(-r * Tpar) * P["Cstr"])
    npv -= np.where((~succ) & (~detected), math.exp(-r * Tpar) * P["Lroll"], 0.0)
    return npv.mean(), npv


# example parameters: the invoice chain at iota = 0.9 (W excludes the amortized build, counted in F)
Wcash = W09 + np.sum(X_["FA"]) / X_["TA"]
C0 = EM
# Transition inputs of the stylized test chain (formula checks of Section 13 only). The paper's running example is
# read from data/examples/invoice_chain.yaml in Section 23.
f_int = lambda io: io / (1 - io)
I_int = 60e3 * 4 * (f_int(0.9) - f_int(0.4))
TP = dict(r=0.10, Th=4.0, W=Wcash, F=np.sum(X_["FA"]) + I_int, I=0.0, CJ=60e3,
          Cpar=0.25 * C0 + 0.05 * EH + 50e3, Cstr=0.5 * 0.25 * X_["v"] * X_["tU_share"] * (cH_ex[2] + cH_ex[3]) + 100e3,
          Cwo=150e3, pis=0.75, bbar=0.85, Tdet=0.25, Lroll=2.0e6)
print(f"     transition example: W = {TP['W']:,.0f}/yr, F = {TP['F']:,.0f}, C_par = {TP['Cpar']:,.0f}/yr, "
      f"C_str = {TP['Cstr']:,.0f}")
mc_mean, _ = simulate_npv(TP, 0.5)
cf = transition_npv(TP, 0.5)
check("13a (a) risk-adjusted NPV closed form matches Monte Carlo of the outcome tree (200k draws)",
      abs(mc_mean - cf) < 0.01 * abs(cf) + 5e3, f"closed {cf:,.0f}, MC {mc_mean:,.0f}")
# (b) undiscounted breakpoint and minimum horizon
TP0 = dict(TP, r=0.0)
lhs = TP["pis"] * TP["bbar"] * TP["W"] * (TP["Th"] - 0.5 * 0.5)
pu = math.exp(-0.5 / TP["Tdet"])
rhs = TP["F"] + TP["I"] + TP["CJ"] + TP["Cpar"] * 0.5 + (TP["pis"] + (1 - TP["pis"]) * pu) * TP["Cstr"] \
    + (1 - TP["pis"]) * pu * TP["Lroll"]
check("13b (b) undiscounted NPV = varpi_p bbar W [T_h - (1 - rhobar) T_par] - [F + I + C^J + C^par T_par + ...]",
      abs(transition_npv(TP0, 0.5) - (lhs - rhs)) < 1e-3 * abs(lhs - rhs) + 1)
Thmin = 0.5 * 0.5 + rhs / (TP["pis"] * TP["bbar"] * TP["W"])
check("13c (b) minimum horizon T_h* = (1 - rhobar) T_par + [costs]/(varpi_p bbar W) makes undiscounted NPV zero",
      abs(transition_npv(dict(TP0, Th=Thmin), 0.5)) < 1e-2)
print(f"     undiscounted NPV(T_par=0.5) = {lhs - rhs:,.0f}; minimum horizon T_h* = {Thmin:.3f} years; "
      f"discounted NPV = {cf:,.0f}")
# (c) payback extension
bad_pb = 0
for _ in range(200):
    W, F, I, CJ, Cs = RNG.uniform(1, 5), RNG.uniform(0, 5), RNG.uniform(0, 3), RNG.uniform(0, 1), RNG.uniform(0, 2)
    Cp, T = RNG.uniform(0, 2), RNG.uniform(0.1, 2)
    ramp_shape = RNG.choice(["lin", "sq", "sqrt"])
    rf = {"lin": lambda u: u, "sq": lambda u: u * u, "sqrt": lambda u: math.sqrt(u)}[ramp_shape]
    rbar = integrate.quad(rf, 0, 1)[0]
    cum = lambda tt: -(F + I + CJ) - Cp * min(tt, T) + W * (integrate.quad(lambda s: rf(s / T), 0, min(tt, T))[0]) \
        - (Cs if tt >= T else 0) + W * max(tt - T, 0)
    tp = (F + I + CJ + Cs) / W + T * (1 - rbar + Cp / W)
    if tp >= T:
        if abs(cum(tp)) > 1e-6 or cum(tp - 1e-3) > 0:
            bad_pb += 1
check("13d (c) payback t_pay = (F+I+C^J+C^str)/W + T_par(1 - rhobar + C^par/W) for linear, convex, concave ramps",
      bad_pb == 0)
# (d) optimal parallel-run length
bad_T = 0
for _ in range(300):
    Cp, W, om, bb = RNG.uniform(0.1, 2), RNG.uniform(1, 5), RNG.uniform(0.3, 0.98), RNG.uniform(0.5, 1)
    Td, Cs, Lr, rbar = RNG.uniform(0.05, 1), RNG.uniform(0, 2), RNG.uniform(1, 30), 0.5
    chat = Cp + om * bb * W * (1 - rbar)
    R = (1 - om) * (Cs + Lr)
    obj = lambda T: chat * T + R * math.exp(-T / Td)
    Tst = Td * math.log(R / (chat * Td)) if R > chat * Td else 0.0
    res = optimize.minimize_scalar(obj, bounds=(0, 20), method="bounded", options={"xatol": 1e-12})
    if abs(res.x - Tst) > 1e-5 and obj(Tst) > res.fun + 1e-9:
        bad_T += 1
    if Tst > 0 and abs((1 - om) * math.exp(-Tst / Td) - chat * Td / (Cs + Lr)) > 1e-9:
        bad_T += 1
check("13e (d) T_par* = T_det ln[(1-varpi_p)(C^str+L_roll)/(T_det c_hat)]^+ minimizes the undiscounted cost (300 draws)",
      bad_T == 0)
check("13f (d) at T_par* the residual undetected-failure probability equals T_det c_hat/(C^str + L_roll)", bad_T == 0)
Tsym, Td_s, ch_s, R_s = sp.symbols("T T_d chat R", positive=True)
objs = ch_s * Tsym + R_s * sp.exp(-Tsym / Td_s)
Tstar_s = Td_s * sp.log(R_s / (ch_s * Td_s))
check("13g (d) FOC: d/dT [c_hat T + R exp(-T/T_det)] = 0 at T*, second derivative > 0",
      is_zero(sp.diff(objs, Tsym).subs(Tsym, Tstar_s)) and sp.simplify(sp.diff(objs, Tsym, 2)).is_positive)
# comparative statics of T*
Tst_f = lambda Cp, W, om, Cs, Lr, Td=0.25, bb=0.85: Td * math.log((1 - om) * (Cs + Lr) / (Td * (Cp + om * bb * W * 0.5)))
base = (TP["Cpar"], TP["W"], TP["pis"], TP["Cstr"], TP["Lroll"])
Tex = Tst_f(*base)
check("13h (d) T* rises with L_roll and C^str, falls with C^par and with varpi_p (example neighborhood)",
      Tst_f(base[0], base[1], base[2], base[3], base[4] * 1.2) > Tex and Tst_f(base[0] * 1.2, *base[1:]) < Tex
      and Tst_f(base[0], base[1], base[2] + 0.05, base[3], base[4]) < Tex
      and Tst_f(base[0], base[1], base[2], base[3] * 1.2, base[4]) > Tex)
chat_ex = TP["Cpar"] + TP["pis"] * TP["bbar"] * TP["W"] * 0.5
resid = TP["Tdet"] * chat_ex / (TP["Cstr"] + TP["Lroll"])
# discounted optimum for comparison
resd = optimize.minimize_scalar(lambda T: -transition_npv(TP, T), bounds=(0.01, 3), method="bounded")
print(f"     T_par* (undiscounted) = {Tex:.4f} yr; discounted optimum = {resd.x:.4f} yr; residual risk = {resid:.4f}; "
      f"c_hat = {chat_ex:,.0f}")
npv_T = transition_npv(TP, Tex)
npv_det = transition_npv(dict(TP, pis=1.0, bbar=1.0), Tex)
rr = TP["r"]
A_T = (1 - math.exp(-rr * Tex)) / rr
ramp_T = integrate.quad(lambda tt: math.exp(-rr * tt) * tt / Tex, 0, Tex)[0]
tail_T = (math.exp(-rr * Tex) - math.exp(-rr * TP["Th"])) / rr
pu_T = math.exp(-Tex / TP["Tdet"])
base_T = -(TP["F"] + TP["I"] + TP["CJ"]) - TP["Cpar"] * A_T
Ys_ex = base_T + TP["bbar"] * TP["W"] * (ramp_T + tail_T) - math.exp(-rr * Tex) * TP["Cstr"]
Yf_ex = base_T - math.exp(-rr * Tex) * pu_T * (TP["Cstr"] + TP["Lroll"])
print(f"     at T_par*: risk-adjusted NPV {npv_T:,.0f}; deterministic NPV {npv_det:,.0f}; Y_s {Ys_ex:,.0f}; Y_f {Yf_ex:,.0f}")
pb_ex = (TP["F"] + TP["I"] + TP["CJ"] + TP["Cstr"]) / TP["W"]
ext_ex = 0.5 * (0.5 + TP["Cpar"] / TP["W"])
print(f"     payback without parallel run {pb_ex:.3f} yr; extension from a 6-month run {ext_ex:.3f} yr")
# break-even values (T_par re-optimized, discounted)
def npv_opt(P):
    res_ = optimize.minimize_scalar(lambda T: -transition_npv(P, T), bounds=(0.01, 3), method="bounded",
                                    options={"xatol": 1e-10})
    return -res_.fun
F_be = optimize.brentq(lambda F_: npv_opt(dict(TP, F=F_)), 0.0, 5e6)
npv_perp = npv_opt(dict(TP, Th=1e4))
npv_sure = npv_opt(dict(TP, pis=1.0))
PB_ = dict(TP, F=np.sum(X_["FA"]))
npv_builds = npv_opt(PB_)
Th_be_builds = optimize.brentq(lambda T: npv_opt(dict(PB_, Th=T)), 1.0, 60.0)
npv_Th = {T: npv_opt(dict(TP, Th=T)) for T in (3.0, 5.0)}
print(f"     break-evens: F* = {F_be:,.0f}; NPV with an unlimited horizon {npv_perp:,.0f}; with varpi_p = 1 {npv_sure:,.0f}; "
      f"T_h = 3, 5: {npv_Th[3.0]:,.0f}, {npv_Th[5.0]:,.0f}; without the integration NPV {npv_builds:,.0f}, "
      f"break-even T_h {Th_be_builds:.2f}")

# ==============================================================================================
header("14. Score path through a transition (Proposition prop:tasks-scorepath)")
# ==============================================================================================
def annual_dm(P, Tpar, S, basis="cash", b=1.0, years=6, TA=3.0):
    out = []
    for y in range(1, years + 1):
        lo, hi = y - 1, y
        f = lambda tt: (b * P["W"] * (tt / Tpar) - P["Cpar"]) if tt < Tpar else b * P["W"]
        val = integrate.quad(f, lo, hi, points=[Tpar] if lo < Tpar < hi else None)[0]
        if y == 1:
            val -= P["CJ"] + (P["F"] + P["I"] if basis == "cash" else 0)
        if lo <= Tpar < hi:
            val -= P["Cstr"] + (P["Cwo"] if basis == "gaap" else 0)
        if basis == "gaap":
            val -= P["F"] / TA * max(0, min(hi, TA) - lo)
        out.append(val / S)
    return np.array(out)


Sx = 100e6
cash = annual_dm(TP, 0.5, Sx, "cash")
gaap = annual_dm(TP, 0.5, Sx, "gaap")
print(f"     annual change in the Rule-of-40 score (points), revenue $100M, T_par = 0.5: cash {np.round(100*cash, 2)}, "
      f"GAAP {np.round(100*gaap, 2)}")
# formulas: year-1 cash and GAAP with T_par <= 1 and linear ramp
y1c = -(TP["F"] + TP["I"] + TP["CJ"] + TP["Cpar"] * 0.5 - TP["W"] * 0.25 + TP["Cstr"] - TP["W"] * 0.5) / Sx
y1g = -(TP["CJ"] + TP["Cpar"] * 0.5 - TP["W"] * 0.25 + TP["Cstr"] + TP["Cwo"] - TP["W"] * 0.5 + TP["F"] / 3) / Sx
check("14a (a)-(b) year-1 dip: cash -[F+I+C^J+C^str+C^par T - W T/2 - W(1-T)]/S; GAAP replaces F+I by F/T_A and adds C^wo",
      close(cash[0], y1c, 1e-9) and close(gaap[0], y1g, 1e-9))
# flow-negative duration with linear ramp: T C^par/(bW) when C^par < bW
tneg = 0.5 * TP["Cpar"] / TP["W"]
f = lambda tt: TP["W"] * tt / 0.5 - TP["Cpar"]
check("14c (a) flow below baseline exactly for t < T_par C^par/(bW) (linear ramp)",
      f(tneg - 1e-9) < 0 < f(tneg + 1e-9), f"{tneg:.3f} yr")
check("14d (c) GAAP amortization drag F/(T_A S) until T_A; new steady state at max(T_par, T_A)",
      np.all(np.diff(gaap[3:]) == 0) and gaap[3] > gaap[2])

# ==============================================================================================
header("15. Success probability (Lemma lem:tasks-success)")
# ==============================================================================================
bad_s = 0
for _ in range(300):
    J = int(RNG.integers(1, 8))
    zj = RNG.normal(1.5, 1.5, J)
    pj = 1 / (1 + np.exp(-zj))
    pp = np.prod(pj)
    if pp > pj.min() + 1e-15:
        bad_s += 1
    k = int(np.argmin(pj))
    grads = 1 - pj  # d ln varpi_p / d z_j
    if np.argmax(grads) != k:
        bad_s += 1
    h = 1e-6
    zj2 = zj.copy(); zj2[0] += h
    fd = (np.log(np.prod(1 / (1 + np.exp(-zj2)))) - np.log(pp)) / h
    if abs(fd - (1 - pj[0])) > 1e-5:
        bad_s += 1
check("15a varpi_p = prod varpi_pj <= min_j; d ln varpi_p / d z_j = 1 - varpi_pj, largest at the weakest activity",
      bad_s == 0)
zz = np.array([0.0, 30.0, 30.0, 30.0])
check("15b with logistic varpi_pj, as other margins grow, varpi_p -> varpi_pj of the weakest activity",
      abs(np.prod(1 / (1 + np.exp(-zz))) - 0.5) < 1e-9)
chi_ch = lambda q: 1 / math.log2(1 / q)
eta_r = math.log(5) / math.log(4)
chi_lg = lambda q: (q / (1 - q)) ** eta_r
lag_ch = [math.log2(chi_ch(q)) for q in (0.8, 0.95, 0.99)]
lag_lg = [math.log2(chi_lg(q)) for q in (0.8, 0.95, 0.99)]
print(f"     reliability lag (doublings above the 50% horizon) at 80/95/99%: constant hazard {np.round(lag_ch, 2)}, "
      f"logistic (eta_r = 1.16) {np.round(lag_lg, 2)}; computer-use offset log2(40..100) = {math.log2(40):.2f}..{math.log2(100):.2f}")
check("15c constant hazard: chi(q) = 1/log2(1/q) puts 80/95/99% horizons 1.64/3.76/6.11 doublings below the 50% horizon "
      "(logistic: 2.32/4.93/7.70); a 40-100x domain offset is 5.3-6.6 doublings",
      np.allclose(np.round(lag_ch, 2), [1.64, 3.76, 6.11]) and np.allclose(np.round(lag_lg, 2), [2.32, 4.93, 7.70])
      and abs(math.log2(40) - 5.32) < 0.01 and abs(math.log2(100) - 6.64) < 0.01
      and all(abs(2 ** (-1 / chi_ch(q)) - q) < 1e-12 for q in (0.8, 0.95, 0.99)))

# ==============================================================================================
header("16. The pilot as a stage gate (Proposition prop:tasks-pilot)")
# ==============================================================================================
def pilot_value(om, Ys, Yf, Fp, d=1.0):
    return d * om * Ys - Fp - max(0.0, om * Ys + (1 - om) * Yf)


bad_p = 0
for _ in range(1000):
    Ys, Yf = RNG.uniform(0.5, 5), -RNG.uniform(0.5, 5)
    Fp = RNG.uniform(0, 0.5)
    d = RNG.choice([1.0, RNG.uniform(0.9, 1.0)])
    lo = Fp / (d * Ys)
    hi = (abs(Yf) - Fp) / (abs(Yf) + (1 - d) * Ys)
    for om in np.linspace(0.001, 0.999, 60):
        vp = pilot_value(om, Ys, Yf, Fp, d)
        if (vp > 1e-12) != (lo < om < hi):
            if abs(vp) > 1e-9:
                bad_p += 1
        if d == 1.0 and abs(vp - (min(om * Ys, (1 - om) * abs(Yf)) - Fp)) > 1e-12:
            bad_p += 1
check("16a (b)-(c) pilot pays iff varpi_p in (F_pil/(dY_s), (|Y_f| - F_pil)/(|Y_f| + (1-d)Y_s)); "
      "no delay: VP = min(varpi_p Y_s, (1-varpi_p)|Y_f|) - F_pil (1000 draws)", bad_p == 0, f"violations={bad_p}")
# gate rule with imperfect binary signal
bad_g = 0
for _ in range(300):
    Ys, Yf = RNG.uniform(0.5, 5), -RNG.uniform(0.5, 5)
    om = RNG.uniform(0.05, 0.95)
    sens, spec = RNG.uniform(0.6, 0.99), RNG.uniform(0.6, 0.99)
    post_pos = om * sens / (om * sens + (1 - om) * (1 - spec))
    post_neg = om * (1 - sens) / (om * (1 - sens) + (1 - om) * spec)
    thr = -Yf / (Ys - Yf)
    for post in [post_pos, post_neg]:
        ev = post * Ys + (1 - post) * Yf
        if (ev >= 0) != (post >= thr):
            bad_g += 1
check("16b (a) gate rule: scale iff posterior success probability >= varpi^gate = |Y_f|/(Y_s + |Y_f|)", bad_g == 0)
Ys, Yf, Fp = Ys_ex, Yf_ex, 100e3
lo, hi = Fp / Ys, 1 - Fp / abs(Yf)
d = math.exp(-0.10 * 0.25)
lo_d, hi_d = Fp / (d * Ys), (abs(Yf) - Fp) / (abs(Yf) + (1 - d) * Ys)
gate = abs(Yf) / (Ys + abs(Yf))
vp0, vpd = pilot_value(TP["pis"], Ys, Yf, Fp), pilot_value(TP["pis"], Ys, Yf, Fp, d)
if Ys > 0:
    print(f"     pilot example: band ({lo:.3f}, {hi:.3f}); with 3-month delay at r = 10%: ({lo_d:.3f}, {hi_d:.3f}); "
          f"gate threshold {gate:.4f}; VP at varpi_p = 0.75: {vp0:,.0f} (no delay), {vpd:,.0f} (delay)")
else:
    print(f"     pilot example: Y_s = {Ys:,.0f} < 0, so no pilot band; a revealing pilot is worth -F_pil at every varpi_p")
# grounded example: Y_s < 0, so the transition fails even on success and no pilot has value at any varpi_p
# general revealing-pilot value d E[(E[Y | outcome])^+] - F_pil - (E Y)^+ (Prop pilot(b)); with Y_s, Y_f < 0 it is -F_pil
vp_gen = lambda om_, Ys_, Yf_, Fp_, d_=1.0: d_ * (om_ * max(Ys_, 0) + (1 - om_) * max(Yf_, 0)) - Fp_ \
    - max(0.0, om_ * Ys_ + (1 - om_) * Yf_)
vp_grid = [vp_gen(om_, Ys_ex, Yf_ex, Fp) for om_ in np.linspace(0, 1, 101)]
# conditional illustration: integration already in place (F = builds only), same T_par*, T_h = 4
rr_ = TP["r"]; Tx = Tex
A_x = (1 - math.exp(-rr_ * Tx)) / rr_
ramp_x = integrate.quad(lambda tt: math.exp(-rr_ * tt) * tt / Tx, 0, Tx)[0]
tail_x = (math.exp(-rr_ * Tx) - math.exp(-rr_ * TP["Th"])) / rr_
base_x = -(PB_["F"] + TP["I"] + TP["CJ"]) - TP["Cpar"] * A_x
Ys_b = base_x + TP["bbar"] * TP["W"] * (ramp_x + tail_x) - math.exp(-rr_ * Tx) * TP["Cstr"]
Yf_b = base_x - math.exp(-rr_ * Tx) * math.exp(-Tx / TP["Tdet"]) * (TP["Cstr"] + TP["Lroll"])
lo_b, hi_b, gate_b = Fp / Ys_b, 1 - Fp / abs(Yf_b), abs(Yf_b) / (Ys_b + abs(Yf_b))
vp_b = pilot_value(TP["pis"], Ys_b, Yf_b, Fp)
print(f"     pilot (integration in place): Y_s {Ys_b:,.0f}, Y_f {Yf_b:,.0f}; band ({lo_b:.3f}, {hi_b:.3f}); gate {gate_b:.4f}; "
      f"VP(0.75) {vp_b:,.0f}")

# ==============================================================================================
header("17. The value of granularity (Proposition prop:tasks-granularity)")
# ==============================================================================================
# (a) Jensen / Blackwell monotonicity on a simulated two-tier information structure
n = 400000
theta1 = RNG.normal(0, 1, n)
theta2 = RNG.normal(0, 1, n)
Y = 0.3 + theta1 + 0.8 * theta2 + RNG.normal(0, 0.5, n)
v0 = max(0.3, 0)
v1 = np.mean(np.maximum(0.3 + theta1, 0))
v2 = np.mean(np.maximum(0.3 + theta1 + 0.8 * theta2, 0))
vinf = np.mean(np.maximum(Y, 0))
check("17a (a) value nondecreasing in tier: V_0 <= V_1 <= V_2 <= V_inf (simulated filtration)",
      v0 <= v1 <= v2 <= vinf, f"{v0:.3f} {v1:.3f} {v2:.3f} {vinf:.3f}")
# (b) distribution-free bound
bad_b = 0
for _ in range(300):
    kind = RNG.integers(0, 3)
    m, s = RNG.normal(0, 2), RNG.uniform(0.1, 3)
    if kind == 0:
        x = RNG.normal(m, s, 200000)
    elif kind == 1:
        x = m + s * (RNG.exponential(1, 200000) - 1)
    else:
        x = m + s * RNG.choice([-1, 1], 200000)
    mm, ss = x.mean(), x.std()
    loss = np.mean(np.maximum(x, 0)) - max(mm, 0)
    bound = min(ss / 2, ss**2 / (4 * abs(mm)) if mm != 0 else np.inf)
    if loss > bound + 1e-3 * ss:
        bad_b += 1
check("17b (b) loss <= min{s/2, s^2/(4|m|)} for normal, skewed and two-point posteriors (300 draws)", bad_b == 0)
# (c) normal closed form and properties of the unit normal loss function
bad_c = 0
for _ in range(200):
    m, s = RNG.normal(0, 2), RNG.uniform(0.1, 3)
    lo_, hi_ = max(0.0, m - 14 * s), max(0.0, m + 14 * s)
    ex = (integrate.quad(lambda y: y * stats.norm.pdf(y, m, s), lo_, hi_, limit=400, epsabs=1e-13)[0] if hi_ > 0 else 0.0) \
        - max(m, 0)
    ex2 = m * stats.norm.cdf(m / s) + s * stats.norm.pdf(m / s) - max(m, 0)
    if abs(ex - s * std_normal_loss(abs(m) / s)) > 1e-7 * max(1, s) or abs(ex2 - s * std_normal_loss(abs(m) / s)) > 1e-12:
        bad_c += 1
check("17c (c) E[Y^+] - m^+ = s L(|m|/s) for Y ~ N(m, s^2)", bad_c == 0)
uu = sp.symbols("u", real=True)
Nn = (1 + sp.erf(uu / sp.sqrt(2))) / 2
nn_ = sp.exp(-uu**2 / 2) / sp.sqrt(2 * sp.pi)
Lf = nn_ - uu * (1 - Nn)
check("17d (c) L'(u) = -(1 - N(u)) < 0 and L(0) = 1/sqrt(2 pi)",
      is_zero(sp.diff(Lf, uu) + (1 - Nn)) and is_zero(Lf.subs(uu, 0) - 1 / sp.sqrt(2 * sp.pi)))
ug = np.linspace(0, 8, 801)
check("17e (c) Mills bound L(u) <= n(u)/(1 + u^2) on [0, 8]",
      np.all(std_normal_loss(ug) <= stats.norm.pdf(ug) / (1 + ug**2) + 1e-15))
# preposterior value of a finer tier
bad_pp = 0
for _ in range(50):
    m, s = RNG.normal(0, 1.5), RNG.uniform(0.5, 2)
    sp2 = RNG.uniform(0.1, 0.9) * s**2
    shat = math.sqrt(s**2 - sp2)
    mt = m + shat * stats.norm.ppf((np.arange(400000) + 0.5) / 400000)  # stratified draws of the posterior mean
    mc = np.mean(np.maximum(mt, 0)) - max(m, 0)
    if abs(mc - shat * std_normal_loss(abs(m) / shat)) > 1e-4 * max(1, shat):
        bad_pp += 1
check("17f (c) preposterior: value of a tier that cuts variance to s'^2 is shat L(|m|/shat), shat^2 = s^2 - s'^2",
      bad_pp == 0)
# (d) spend-only information has no decision value without fixed costs, option value with them
E_ = RNG.lognormal(0, 0.5, 200000)
for md in [-0.2, 0.3]:
    val_inf = np.mean(np.maximum(E_ * md, 0)) - max(E_.mean() * md, 0)
    check(f"17g (d) F = 0: observing spend has zero decision value (m_delta = {md})", abs(val_inf) < 1e-12)
md, Fc = 0.3, 0.35
Estar = Fc / md
val_inf = np.mean(np.maximum(E_ * md - Fc, 0)) - max(E_.mean() * md - Fc, 0)
alt = md * (np.mean(np.maximum(E_ - Estar, 0)) - max(E_.mean() - Estar, 0))
check("17h (d) F > 0: value of spend data = m_delta {E[(E - E*)^+] - (E[E] - E*)^+}, E* = F/(T_A m_delta) > 0",
      close(val_inf, alt, 1e-9) and val_inf > 0)
# (e) cell-level action loss
bad_e = 0
for _ in range(500):
    y = RNG.normal(0, 1, int(RNG.integers(2, 12)))
    loss = np.sum(np.maximum(y, 0)) - max(np.sum(y), 0)
    if abs(loss - min(np.sum(np.maximum(y, 0)), np.sum(np.maximum(-y, 0)))) > 1e-12:
        bad_e += 1
check("17i (e) cell-level action loss = min{sum Y^+, sum Y^-}", bad_e == 0)
# example
for (m, s) in [(200e3, 300e3), (1e6, 300e3)]:
    print(f"     granularity example m={m:,.0f}, s={s:,.0f}: normal loss {s*std_normal_loss(m/s):,.0f}; "
          f"bound {min(s/2, s*s/(4*m)):,.0f}")
check("17j example: m = $200k, s = $300k: loss $45k (bound $112.5k); m = $1M: loss $34 (bound $22.5k)",
      abs(300e3 * std_normal_loss(200 / 300) - 45.3e3) < 0.2e3 and abs(300e3 * std_normal_loss(1e6 / 300e3) - 34) < 1.0
      and abs(min(150e3, 300e3**2 / 4 / 200e3) - 112.5e3) < 1 and abs(300e3**2 / 4e6 - 22.5e3) < 1)

# ==============================================================================================
header("18. Aggregation into Part I (Proposition prop:tasks-aggregate, Corollary cor:tasks-weights)")
# ==============================================================================================
bad_lam = bad_fo = 0
for _ in range(300):
    al = RNG.uniform(0.25, 0.45)
    X, k = RNG.uniform(1, 12), RNG.uniform(0, 0.8)
    if X <= k:
        continue
    ell, m0, G = RNG.uniform(0.05, 1.2), RNG.uniform(0.1, 0.6), RNG.uniform(0, 0.3)
    dl = RNG.uniform(0, 0.5)
    D0, s0, R0 = partI(m0, G, k, X, ell, al)
    D1, s1, R1 = partI(m0, G, k, X, ell * (1 - dl) ** (-al), al)
    Pi = (1 - al) * (X - k) * D0
    if abs((R1 - R0) - Pi * ((1 - dl) ** (-al / (1 - al)) - 1)) > 1e-10:
        bad_lam += 1
    if R1 - R0 < s0 * dl - 1e-12:
        bad_fo += 1
    # first-order slope at dl = 0 equals sigma*
    h = 1e-7
    fd = (partI(m0, G, k, X, ell * (1 - h) ** (-al), al)[2] - R0) / h
    if abs(fd - s0) > 1e-5 * max(1, s0):
        bad_fo += 1
check("18a (a) growth-activity saving delta maps to lambda (1-delta)^(-alpha); exact gain Pi[(1-delta)^(-alpha/(1-alpha)) - 1]",
      bad_lam == 0)
check("18b (b) first-order gain sigma* delta, and exact gain >= sigma* delta", bad_fo == 0)
# (c) small-share multiple: r v0 = R*_{v0}; dv0 = dR*_{X}|_{X=v0} / (r - g0)
r, G, k, al, m0 = 0.10, 0.04, 0.0, 0.3, 0.35
lam10 = optimize.brentq(lambda L_: gordon_root(r, G, k, m0, L_, al) - 10.0, 0.06, 0.075)
v0 = gordon_root(r, G, k, m0, lam10, al)
D0, s0, R0 = partI(m0, G, k, v0, lam10, al)
g0 = G + D0
check("18c Part I worked example reproduced: lambda = 0.070 gives v0 = 10, g0 = 7.6%, sigma0 = 10.7%",
      abs(lam10 - 0.070) < 5e-4 and abs(g0 - 0.076) < 5e-4 and abs(s0 - 0.107) < 5e-4,
      f"lambda={lam10:.5f}, g0={g0:.4f}, sigma0={s0:.4f}")
check("18d (c) r v0 = R*_X at X = v0 (small share)", abs(r * v0 - R0) < 1e-10)
bad_dv = 0
for name, idx in [("m0", 0), ("G", 1), ("k", 2), ("lam", 3)]:
    base = [m0, G, k, lam10]
    h = 1e-6
    up = list(base); up[idx] += h
    dn = list(base); dn[idx] -= h if idx != 2 else 0.0
    vup = gordon_root(r, up[1], up[2], up[0], up[3], al)
    vdn = gordon_root(r, dn[1], dn[2], dn[0], dn[3], al)
    fd = (vup - vdn) / (h if idx == 2 else 2 * h)
    # partial of R*_X at fixed X = v0
    Rup = partI(up[0], up[1], up[2], v0, up[3], al)[2]
    Rdn = partI(dn[0], dn[1], dn[2], v0, dn[3], al)[2]
    dR = (Rup - Rdn) / (h if idx == 2 else 2 * h)
    if abs(fd - dR / (r - g0)) > 1e-4 * max(1, abs(fd)):
        bad_dv += 1
check("18e (c) dv0/dtheta = (dR*_X/dtheta at X = v0)/(r - g0) for theta in {m0, G, k, lambda}", bad_dv == 0)
v0b = gordon_root(r, G, k, m0 + 0.01, lam10, al)
print(f"     one point of G&A saved: v0 {v0:.4f} -> {v0b:.4f} (first order {0.01/(r-g0):.4f})")
check("18f example (Cor weights): one point of revenue saved in G&A raises the multiple by 0.41 to first order (0.42 exact)",
      abs(0.01 / (r - g0) - 0.412) < 0.001 and abs(v0b - v0 - 0.417) < 0.001, f"{v0b - v0:.4f}")
# growth-activity saving example
lam_b = lam10 * (1 - 0.2) ** (-al)
v0c = gordon_root(r, G, k, m0, lam_b, al)
Pi0 = (1 - al) * (v0 - k) * D0
ex_first, ex_exact = s0 * 0.2, Pi0 * ((0.8) ** (-al / (1 - al)) - 1)
print(f"     20% saving on growth activities: dR* first order {ex_first:.4f}, exact {ex_exact:.4f}; v0 {v0:.3f} -> {v0c:.3f}")
check("18g example: a 20% cut in growth-activity cost adds 2.1 points to R*_{X=v0} at first order, 2.5 exactly; "
      "multiple 10 -> 11.3", abs(ex_first - 0.0214) < 5e-4 and abs(ex_exact - 0.0251) < 5e-4 and abs(v0c - 11.28) < 0.01)
# pass-through weight for COGS
phi = 0.4
check("18h (Cor weights) COGS weight 1 - phi, G&A weight 1, growth weight 1 at first order",
      abs((1 - phi) - 0.6) < 1e-12)

# ==============================================================================================
header("19. Breakpoints (Proposition prop:tasks-breakpoints)")
# ==============================================================================================
bad_bk = 0
for _ in range(300):
    cbar = RNG.uniform(1, 5)
    n, F, T, v = RNG.uniform(0.1, 1), RNG.uniform(1e3, 1e5), 3.0, RNG.uniform(1e3, 1e5)
    L, wtR, epsb = RNG.uniform(5, 50), RNG.uniform(0.2, 2), RNG.uniform(0.01, 0.05)
    e0, e1 = RNG.uniform(0.2, 0.5), RNG.uniform(0.001, 0.01)
    io = RNG.uniform(0, 1)
    p = RNG.uniform(0, 3)
    e_of = lambda x: e1 + (e0 - e1) * (1 - x)
    cA = lambda p_=p, v_=v, e_=None: p_ * n + review(e_of(io) if e_ is None else e_, L, wtR, epsb)[1] + F / (v_ * T)
    Aopt = cA() <= cbar
    cQ = review(e_of(io), L, wtR, epsb)[1]
    pstar = (cbar - cQ - F / (v * T)) / n
    c1 = (p <= pstar) == Aopt
    cvar = p * n + cQ
    c2 = ((cbar > cvar) and (v >= F / (T * (cbar - cvar)))) == Aopt
    target_q = cbar - p * n - F / (v * T)
    fq = lambda e_: review(e_, L, wtR, epsb)[1] - target_q
    if fq(1e-9) > 0:
        c3 = not Aopt
    elif fq(1.0) <= 0:
        c3 = Aopt
    else:
        estar = optimize.brentq(fq, 1e-9, 1.0, xtol=1e-14)
        c3 = (e_of(io) <= estar + 1e-12) == Aopt
    fi = lambda x: cA(e_=e_of(x)) - cbar
    if fi(1.0) > 0:
        c4 = not Aopt
    elif fi(0.0) <= 0:
        c4 = Aopt
    else:
        ist_ = optimize.brentq(fi, 0.0, 1.0, xtol=1e-14)
        c4 = (io >= ist_ - 1e-12) == Aopt
    if not (c1 and c2 and c3 and c4):
        bad_bk += 1
check("19a (1)-(4) the four activity breakpoints (price, volume, raw error, readiness) are one inequality (300 draws)",
      bad_bk == 0, f"violations={bad_bk}")
# (5) percolation: step function in capability with one jump per process
bad_perc = 0
for _ in range(100):
    nproc = int(RNG.integers(2, 6))
    procs = []
    for _p in range(nproc):
        J = int(RNG.integers(2, 6))
        w_single = -RNG.uniform(0.1, 1)
        cc = RNG.uniform(0, 0.5)
        Xi = -(J * w_single + (J - 1) * cc) + RNG.uniform(0.1, 1)  # whole chain positive
        # ensure no proper subset positive: (J-1) w + (J-2) c <= 0
        if (J - 1) * w_single + (J - 2) * cc > 0:
            cc = -(J - 1) * w_single / max(J - 2, 1) * 0.9 if J > 2 else cc
            Xi = -(J * w_single + (J - 1) * cc) + RNG.uniform(0.1, 1)
        dbar = RNG.uniform(1, 100, J)
        spend = RNG.uniform(1, 10)
        procs.append((J, w_single, cc, Xi, dbar, spend))
    caps = np.linspace(0, 120, 241)
    share = []
    for Hc in caps:
        tot = 0
        for (J, ws, cc, Xi, dbar, spend) in procs:
            feas = [j for j in range(J) if dbar[j] <= Hc]
            best, bestZ = 0.0, frozenset()
            for r_ in range(len(feas) + 1):
                for Z in itertools.combinations(feas, r_):
                    Zs = frozenset(Z)
                    val = len(Zs) * ws + sum(cc for (i, j) in chain_edges(J) if i in Zs and j in Zs) + (Xi if len(Zs) == J else 0)
                    if val > best + 1e-12:
                        best, bestZ = val, Zs
            tot += spend * len(bestZ) / J
        share.append(tot)
    share = np.array(share)
    jumps = np.where(np.diff(share) > 1e-12)[0]
    expected = sorted(set(np.searchsorted(caps, max(pp[4])) - 1 for pp in procs))
    if np.any(np.diff(share) < -1e-12) or len(jumps) > nproc or not set(jumps) <= set(expected):
        bad_perc += 1
check("19b (5) percolation: automated share is a nondecreasing step function of capability, jumping only when "
      "capability reaches a process's hardest activity (100 economies)", bad_perc == 0)


# ==============================================================================================
header("20. Remaining example numbers quoted in Section sec:tasks")
# ==============================================================================================
# Prop modes example: invoice capture at readiness 0.4
cA_cap = a04[0]["cA"]
over_case = X_["v"] * (cH_ex[0] - cA_cap)
loss_vs_O = X_["v"] * (cA_cap - cO_ex[0])
print(f"     capture at 0.4: c_A = {cA_cap:.4f}; case vs c_H shows {over_case:,.0f}; loss vs vendor {loss_vs_O:,.0f}")
# Prop window example
cHw, cVH, ups, extra_w, c0A, cQw, n_w, cV0 = 2.25, 1.00, 0.20, 0.10 * 2.25 + 0.30, 0.90, 0.30, 1.0, 0.20
piV = (cVH - cV0) / n_w
piplus = ((1 + ups) * cVH + extra_w - c0A) / n_w
D0 = (1 + ups) * cV0 + extra_w - c0A
piminus = -D0 / (ups * n_w)
win = math.log(piplus / piminus) / math.log(5.0)
Fw = (c0A - cQw) * 120000 * 3.0
vMB = Fw / (3.0 * ((1 + ups) * cV0 + extra_w - cQw))
# brute force window on a grid
grid = np.linspace(0, 2, 200001)
inwin = np.array([D_gap(pp, cVH, cV0, ups, extra_w, c0A, n_w) >= 0 for pp in grid])
print(f"     window example: piV={piV:.3f}, pi-={piminus:.4f}, pi+={piplus:.4f}, length {win:.4f} yr at 5x/yr, "
      f"v_MB={vMB:,.0f}; today c_A={c0A + n_w:.3f} vs vendor {1.2 * cVH + extra_w:.3f}")
FA_s, TA_s, ups_s, cV0_s, kO_s, cH_s, zO_s, cAv_s = sp.symbols("F_A T_A upsilon c_V0 kappa_O c_H zeta_O c_Avar",
                                                              positive=True)
vMB_s = FA_s / (TA_s * ((1 + ups_s) * cV0_s + kO_s * cH_s + zO_s - cAv_s))
brk_pos = sp.Q.positive((1 + ups_s) * cV0_s + kO_s * cH_s + zO_s - cAv_s)
dk = sp.simplify(sp.diff(vMB_s, kO_s) + vMB_s * cH_s / ((1 + ups_s) * cV0_s + kO_s * cH_s + zO_s - cAv_s))
dF = sp.simplify(sp.diff(vMB_s, FA_s) - vMB_s / FA_s)
check("20b' (c) dv_MB/dkappa_O = -v_MB c_H/bracket < 0 (Coasean force favors the vendor) and dv_MB/dF_A = v_MB/F_A > 0 "
      "(knowledge-cost force favors in-house), symbolic", is_zero(dk) and is_zero(dF))
vMB_k = (Fw / (3.0 * ((1 + ups) * cV0 + 0.05 * 2.25 + 0.30 - cQw)))
vMB_F = 0.5 * Fw / (3.0 * ((1 + ups) * cV0 + extra_w - cQw))
print(f"     make-or-buy forces: v_MB = {vMB:,.0f}; with kappa_O halved {vMB_k:,.0f}; with F_A halved {vMB_F:,.0f}")
# piecemeal: best step-by-step choice at 0.9 and its value
pw = {Z: ex_W(Z, 0.9) for Z in subsets(4)}
piece = frozenset(j for j in range(4) if singles09[j] > 0)
print(f"     piecemeal set {sorted(piece)} worth {pw[piece]:,.0f} (sum of singles {sum(singles09[j] for j in piece):,.0f})")
# Table tab:tasks-example entries
tab_ok = np.allclose(np.round(cH_ex, 2), [2.25, 3.60, 5.40, 2.25]) and np.allclose(np.round(cM_ex, 2), [1.54, 2.28, 4.10, 1.74])
tab_ok &= np.allclose(np.round([x["e"] for x in a04], 3), [0.092, 0.124, 0.282, 0.062])
tab_ok &= np.allclose(np.round([x["e"] for x in a09], 3), [0.019, 0.029, 0.072, 0.014])
tab_ok &= np.allclose(np.round([a04[j]["cA"] for j in [0, 1, 3]], 2), [1.88, 2.97, 1.90]) and not ex_feasible(0.4, 2)
tab_ok &= np.allclose(np.round([x["cA"] for x in a09], 2), [0.73, 1.76, 4.44, 1.26])
tab_ok &= np.allclose(X_["det"], [1, 1, 0.8, 1])
# transition inputs as described in the text
# retrofit reconciliation with Part I (Prop capital intuition): dv0 incl. retrofit = (dm0 - (r+delta) dk)/(r - g0)
dm0, dk_, dlt = 0.004, 0.01, 0.25
v_new = gordon_root(r, G, dk_, m0 + dm0 - dlt * dk_, lam10, al)
lhs_r = (v_new - v0) - dk_
rhs_r = (dm0 - (r + dlt) * dk_) / (r - g0)
print(f"     retrofit reconciliation: dv0 - dk = {lhs_r:.5f}; first order (dm0 - (r+delta)dk)/(r-g0) = {rhs_r:.5f}")
check("20f Prop capital: in Part I's small-share value, steady-state change minus retrofit = (dm0 - (r+delta_K) dk)/(r - g0) "
      "to first order", abs(lhs_r - rhs_r) < 0.03 * abs(rhs_r))
# aggregation (b): with depreciation, dR*/dk = -(g* + delta_K)
bad_dep = 0
for _ in range(100):
    al_, X_w, k_ = RNG.uniform(0.25, 0.45), RNG.uniform(1, 10), RNG.uniform(0, 0.8)
    if X_w <= k_:
        continue
    ell_, m0_, G_, dl_ = RNG.uniform(0.05, 1), RNG.uniform(0.1, 0.6), RNG.uniform(0, 0.3), RNG.uniform(0.05, 0.4)
    Rk = lambda kk: partI(m0_ - dl_ * kk, G_, kk, X_w, ell_, al_)[2]
    hh = 1e-6
    fd = (Rk(k_ + hh) - Rk(k_ - hh)) / (2 * hh)
    gstar = G_ + partI(m0_ - dl_ * k_, G_, k_, X_w, ell_, al_)[0]
    if abs(fd + gstar + dl_) > 1e-6:
        bad_dep += 1
check("20g Prop aggregate (b): with m0 - delta_K k, dR*/dk = -(g* + delta_K) (100 draws)", bad_dep == 0)


# ==============================================================================================
header("21. Run costs, security and scope (Props fullcost, buildbuy, security, secreview, ancscale)")
# ==============================================================================================
# --- (a)-(b) full cost and breakpoint shifts -------------------------------------------------
bad_fc = 0
for _ in range(300):
    n_ = RNG.uniform(0.1, 1); c0A_ = RNG.uniform(0.2, 2); anc = RNG.uniform(0, 1)
    alts = [(RNG.uniform(1, 4), 0.0), (RNG.uniform(0.8, 3), RNG.uniform(0, 0.05))]
    ps0 = crossover_price(c0A_, n_, alts)
    ps1 = crossover_price(c0A_ + anc, n_, alts)
    # shift equals anc/(n - n(x*)) for the binding alternative
    xstar = min(alts, key=lambda a: (a[0] - c0A_) / (n_ - a[1]))
    xstar1 = min(alts, key=lambda a: (a[0] - c0A_ - anc) / (n_ - a[1]))
    if xstar == xstar1 and abs((ps0 - ps1) - anc / (n_ - xstar[1])) > 1e-12:
        bad_fc += 1
    # floor: automation never pays if c0A + anc >= cbar at pi = 0
    if (c0A_ + anc >= min(a[0] for a in alts)) != (ps1 <= 0):
        bad_fc += 1
check("21a (b) ancillary unit cost shifts pi* down by anc/(n - n(x*)); A never pays once c0(A) + anc >= cbar(0)",
      bad_fc == 0)
# volume threshold multiplier with maintenance and revalidation
F_, TA_, dM, Crev, Tup, cbar_, cvar_ = 300e3, 3.0, 0.15, 30e3, 1.0, 2.0, 1.5
v0_ = F_ / TA_ / (cbar_ - cvar_)
v1_ = (F_ / TA_ + dM * F_ + Crev / Tup) / (cbar_ - cvar_)
check("21b (b) v* with maintenance and revalidation = v* x (1 + delta_M T_A + C_reval T_A/(T_up F_A))",
      close(v1_ / v0_, 1 + dM * TA_ + Crev * TA_ / (Tup * F_), 1e-12))
r_s2, Tu = sp.symbols("r T_up", positive=True)
geo_ok = all(abs(sum(math.exp(-rv * tv * k) for k in range(1, 20000)) - 1 / (math.exp(rv * tv) - 1)) < 1e-10
             for rv in [0.05, 0.1, 0.2] for tv in [0.5, 1.0, 2.0])
check("21d revalidation every T_up years: annual equivalent r/(exp(r T_up) - 1) -> 1/T_up as r -> 0",
      geo_ok and is_zero(sp.limit(r_s2 / (sp.exp(r_s2 * Tu) - 1), r_s2, 0) - 1 / Tu))
# technical debt on edges: reduces the integration premium by c_cpl N_i N_j / v_e (supermodularity check)
bad_td = 0
for _ in range(80):
    J = int(RNG.integers(2, 6))
    P = make_process(J, chain_edges(J), RNG, ratio_side="up")
    Nint = RNG.integers(0, 4, J)
    ccpl = RNG.uniform(0, 0.3)
    def Wtd(Z):
        return Wp(P, Z) - sum(ccpl * Nint[i] * Nint[j] for (i, j) in chain_edges(J) if i in Z and j in Z)
    net_ok = all(P["eAM"][k] + P["eMA"][k] - P["eAA"][k] - P["eMM"][k] - ccpl * Nint[i] * Nint[j] >= 0
                 for k, (i, j) in enumerate(chain_edges(J)))
    S_ = list(subsets(J)); vals = {Z: Wtd(Z) for Z in S_}
    sm = all(vals[A | B] + vals[A & B] >= vals[A] + vals[B] - 1e-9 for A in S_ for B in S_)
    if net_ok and not sm:
        bad_td += 1
check("21e (c) technical debt c_cpl N_i N_j on automated edges acts as a lower integration premium; "
      "supermodularity holds when the net premium is nonnegative (80 processes)", bad_td == 0)

# --- (c) build versus buy -----------------------------------------------------------------------
bad_bb = 0
for _ in range(500):
    FA_, FI_, a_ = RNG.uniform(1e5, 1e6), RNG.uniform(1e4, 3e5), 1 / 3
    dM_, Crev_, Ctd_, Clock_ = RNG.uniform(0, 0.3), RNG.uniform(0, 1e5), RNG.uniform(0, 1e5), RNG.uniform(0, 2e5)
    cb_, ups_B, piN_, fixV_ = RNG.uniform(0.2, 2), RNG.uniform(0, 0.5), RNG.uniform(0.1, 1), RNG.uniform(0, 0.3)
    FV_, VB_, CrevV_ = RNG.uniform(1e6, 1e7), RNG.uniform(1e7, 1e8), RNG.uniform(0, 1e6)
    v = RNG.uniform(1e3, 5e6)
    fix_build = FA_ * a_ + dM_ * FA_ + Crev_ + Ctd_
    fix_buy = FI_ * a_ + Clock_
    cv_ = (1 + ups_B) * (piN_ + (FV_ * (a_ + dM_) + CrevV_) / VB_)
    cb_tot = piN_
    build = fix_build + v * cb_tot
    buy = fix_buy + v * cv_
    if cv_ > cb_tot:
        vBB = (fix_build - fix_buy) / (cv_ - cb_tot)
        if (build <= buy) != (v >= vBB):
            bad_bb += 1
    # derivative of (build - buy) in delta_M = F_A - (1+ups_B)(v/V_B) F_V
    h_ = 1e-6
    dd = ((fix_build + h_ * FA_ + v * cb_tot) - (fix_buy + v * (1 + ups_B) * (piN_ + (FV_ * (a_ + dM_ + h_) + CrevV_) / VB_))
          - (build - buy)) / h_
    if abs(dd - (FA_ - (1 + ups_B) * (v / VB_) * FV_)) > 1e-3 * FA_:
        bad_bb += 1
check("21f (c) build iff v >= v_BB = (fixed build - fixed buy)/(c_buy - c_build); d(build - buy)/d delta_M = "
      "F_A - (1+ups_B)(v/V_B) F_V (500 draws)", bad_bb == 0)
# example: invoice chain
FA_tot = float(np.sum(X_["FA"]))
fix_build_ex = FA_tot / 3 + 0.15 * FA_tot + 30e3 + 32e3
fix_buy_ex = 150e3 / 3
piN_tot = float(np.sum(X_["piN"]))
cv_ex = 1.25 * (piN_tot + 0.12)
gap_u = cv_ex - piN_tot
vBB_ex = (fix_build_ex - fix_buy_ex) / gap_u
vBB_nomaint = (FA_tot / 3 - fix_buy_ex) / gap_u
save_buy = (fix_build_ex - fix_buy_ex) - X_["v"] * gap_u
print(f"     build/buy example: fixed build {fix_build_ex:,.0f}, fixed buy {fix_buy_ex:,.0f}, unit gap {gap_u:.4f}; "
      f"v_BB {vBB_ex:,.0f} (without run costs {vBB_nomaint:,.0f}); buying saves {save_buy:,.0f}/yr at 120k invoices")

# --- (d)-(e) security investment and scope -------------------------------------------------------
def risk_cost(Cinc, Cs):
    """min_C {C + exp(-C/Cs) Cinc}: closed form."""
    if Cinc <= Cs:
        return Cinc, 0.0
    Cstar = Cs * math.log(Cinc / Cs)
    return Cstar + Cs, Cstar


bad_sec = 0
for _ in range(500):
    Cinc, Cs = RNG.uniform(1e3, 1e6), RNG.uniform(1e3, 1e5)
    R_, Cst = risk_cost(Cinc, Cs)
    res = optimize.minimize_scalar(lambda C: C + math.exp(-C / Cs) * Cinc, bounds=(0, 20 * Cs + Cinc), method="bounded",
                                   options={"xatol": 1e-9})
    if abs(min(res.fun, Cinc) - R_) > 1e-6 * R_:
        bad_sec += 1
    if Cst > Cinc / math.e + 1e-9:
        bad_sec += 1
    if Cst > 0 and abs(math.exp(-Cst / Cs) * Cinc - Cs) > 1e-6 * Cs:
        bad_sec += 1
check("21h (d) exponential hazard: C* = C_s ln(C_inc/C_s)^+, residual loss C_s, C* <= C_inc/e (500 draws)", bad_sec == 0)
# general convex residual factor: C* nondecreasing in C_inc; risk cost concave, subadditive; R'(C_inc) = g(C*)
bad_gen = 0
for _ in range(200):
    a1, b1 = RNG.uniform(1e3, 5e4), RNG.uniform(0.5, 3)
    gfun = lambda C: (1 + C / a1) ** (-b1)  # convex decreasing, g(0) = 1
    def opt(Ci):
        rr_ = optimize.minimize_scalar(lambda C: C + gfun(C) * Ci, bounds=(0, 1e8), method="bounded",
                                       options={"xatol": 1e-6})
        return (rr_.fun, rr_.x) if rr_.fun < Ci else (Ci, 0.0)
    xs = np.sort(RNG.uniform(1e3, 1e6, 6))
    outs = [opt(x) for x in xs]
    Cs_ = [o[1] for o in outs]
    Rs_ = [o[0] for o in outs]
    if np.any(np.diff(Cs_) < -1e-3 * max(Cs_) - 1):
        bad_gen += 1
    sl = np.diff(Rs_) / np.diff(xs)
    if np.any(np.diff(sl) > 1e-6):
        bad_gen += 1
    if opt(xs[0] + xs[1])[0] > outs[0][0] + outs[1][0] + 1e-6 * outs[1][0]:
        bad_gen += 1
    h_ = 1e-3 * xs[3]
    fd = (opt(xs[3] + h_)[0] - opt(xs[3] - h_)[0]) / (2 * h_)
    if abs(fd - gfun(outs[3][1])) > 2e-3:
        bad_gen += 1
check("21i (d) convex decreasing residual factor: C* nondecreasing in exposure; risk cost concave and subadditive "
      "(pooling security is cheaper); dR/dC_inc = g(C*) (200 draws)", bad_gen == 0, f"violations={bad_gen}")
# scope: with optimal security, expected incident loss enters the scope test logarithmically
check("21j (e) risk cost = C_inc if C_inc <= C_s, else C_s[1 + ln(C_inc/C_s)]",
      all(close(risk_cost(x, 2e4)[0], (x if x <= 2e4 else 2e4 * (1 + math.log(x / 2e4))), 1e-12)
          for x in [5e3, 2e4, 1e5, 5e5, 5e6]))
# example: invoice chain ancillary costs at iota = 0.9
dM_ex, Crev_ex, Tup_ex = 0.15, 30e3, 1.0
Nint_ex = np.array([2, 2, 1, 1]); cint_ex, ccpl_ex = 3e3, 2e3
Cinc_ex = np.array([25e3, 10e3, 5e3, 60e3]); Cs_ex = 20e3


def anc_cost(Z):
    Z = set(Z)
    if not Z:
        return 0.0
    mnt = sum(dM_ex * X_["FA"][j] for j in Z)
    rev = Crev_ex / Tup_ex * len(Z) / 4
    td = cint_ex * sum(Nint_ex[j] for j in Z) + ccpl_ex * sum(Nint_ex[i] * Nint_ex[j] for (i, j) in chain_edges(4)
                                                                  if i in Z and j in Z)
    rk = risk_cost(sum(Cinc_ex[j] for j in Z), Cs_ex)[0]
    return mnt + rev + td + rk


anc_full = anc_cost(range(4))
Rk_full, Cst_full = risk_cost(Cinc_ex.sum(), Cs_ex)
W09_anc = W09 - anc_full
ist_anc = optimize.brentq(lambda i: ex_W(full4, i) - anc_full, 0.5, 1.0, xtol=1e-12)
vals_anc = {Z: ex_W(Z, ist_anc + 0.02) - anc_cost(Z) for Z in subsets(4)}
print(f"     ancillary at full automation: maintenance {dM_ex*FA_tot:,.0f}, revalidation {Crev_ex:,.0f}, technical debt "
      f"{anc_cost(range(4)) - dM_ex*FA_tot - Crev_ex - Rk_full:,.0f}, security spend {Cst_full:,.0f} + residual "
      f"{Rk_full - Cst_full:,.0f}; total {anc_full:,.0f}; W(0.9) net {W09_anc:,.0f}; iota*_p with run costs {ist_anc:.4f}")
# scope: if approval's incident cost were $500k, optimized risk cost is $84k (log), not $500k (linear)

# --- security review capacity (M/M/1) ------------------------------------------------------------
nu_s, Phi_s, rd_s, Vd_s, ps_s = sp.symbols("nu Phi r_d V p", positive=True)
mu_ = Phi_s
loss_per = Vd_s * rd_s / (Phi_s - nu_s + rd_s)
check("21m (sec. review) E[1 - exp(-r_d T)] = r_d/(Phi - nu + r_d) for T ~ Exp(Phi - nu)",
      is_zero(sp.integrate((1 - sp.exp(-rd_s * sp.Symbol("T", positive=True))) * (Phi_s - nu_s)
                           * sp.exp(-(Phi_s - nu_s) * sp.Symbol("T", positive=True)),
                           (sp.Symbol("T", positive=True), 0, sp.oo), conds="none").subs(Phi_s, nu_s + sp.Symbol("g0", positive=True))
              - (rd_s / (sp.Symbol("g0", positive=True) + rd_s))))
# simulate an M/M/1 FCFS queue: sojourn times are Exp(Phi - nu)
nu_v, Phi_v = 8.0, 10.0
nsim = 1000000
rng_q = np.random.default_rng(7)  # dedicated stream, so that checks added elsewhere do not move this simulation
arr = np.cumsum(rng_q.exponential(1 / nu_v, nsim))
svc = rng_q.exponential(1 / Phi_v, nsim)
dep = np.empty(nsim); t_free = 0.0
for i_ in range(nsim):
    start = max(arr[i_], t_free); t_free = start + svc[i_]; dep[i_] = t_free
soj = (dep - arr)[50000:]
check("21n (sec. review) simulated M/M/1 sojourn: mean 1/(Phi - nu) = 0.5 yr and E[exp(-0.25 T)] = 2/2.25",
      abs(soj.mean() - 0.5) < 0.02 and abs(np.mean(np.exp(-0.25 * soj)) - 2 / 2.25) < 0.01,
      f"mean {soj.mean():.4f}")
D_rate = nu_s * loss_per
check("21o (sec. review) marginal value of capacity -dD/dPhi = nu V r_d/(Phi - nu + r_d)^2; optimum "
      "Phi* = nu - r_d + sqrt(nu V r_d/p)",
      is_zero(-sp.diff(D_rate, Phi_s) - nu_s * Vd_s * rd_s / (Phi_s - nu_s + rd_s) ** 2)
      and is_zero((sp.diff(D_rate + ps_s * Phi_s, Phi_s)).subs(Phi_s, nu_s - rd_s + sp.sqrt(nu_s * Vd_s * rd_s / ps_s))))
nu_e, Phi_e, rd_e, Vd_e, p_e = 8.0, 10.0, 0.25, 1.5e6, 60e3
lp_e = Vd_e * rd_e / (Phi_e - nu_e + rd_e)
mv_e = nu_e * Vd_e * rd_e / (Phi_e - nu_e + rd_e) ** 2
Phis_e = nu_e - rd_e + math.sqrt(nu_e * Vd_e * rd_e / p_e)
print(f"     review example: loss per deployment {lp_e:,.0f}; per year {nu_e*lp_e:,.0f}; marginal value {mv_e:,.0f}; "
      f"Phi* = {Phis_e:.3f}; latency at Phi* {1/(Phis_e - nu_e):.3f} yr")
check("21p example: 8 deployments a year against 10 reviews: 0.5-year latency, $167k lost per deployment ($1.33M a year); "
      "a unit of capacity is worth $593k; at $60k a unit the optimum is 14.8 reviews a year (latency 0.15 years)",
      abs(lp_e - 166.7e3) < 0.1e3 and abs(nu_e * lp_e - 1.333e6) < 1e3 and abs(mv_e - 592.6e3) < 0.1e3
      and abs(Phis_e - 14.82) < 0.01 and abs(1 / (Phis_e - nu_e) - 0.147) < 0.002)

# --- (f) scaling and understatement by coarse data -----------------------------------------------
P_ = 5; phi_ = 108e3
Ns = np.array([2, 4, 6, 8, 10]); ccv = 1e3
td_true = sum(ccv * n * (n - 1) / 2 for n in Ns)
td_mean = P_ * ccv * Ns.mean() * (Ns.mean() - 1) / 2
check("21q (f) imputing the mean integration count understates convex technical debt by (c/2) P Var(N)",
      close(td_true - td_mean, ccv / 2 * P_ * Ns.var(), 1e-12) and td_true - td_mean > 0, f"{td_true - td_mean:,.0f}")
sep = P_ * risk_cost(100e3, 20e3)[0]
pool = risk_cost(5 * 100e3, 20e3)[0]
print(f"     scaling example: per-process fixed costs counted once understate by {(P_-1)*phi_:,.0f}; "
      f"technical debt gap {td_true - td_mean:,.0f}; security pooling gap {sep - pool:,.0f}")
bad_sh = 0
for _ in range(200):
    P__ = int(RNG.integers(2, 20)); spp = RNG.uniform(0, 1)
    tot = 1.0; pp_total = spp * tot; unit_total = tot - pp_total
    coarse = pp_total / P__ + unit_total
    if not close((tot - coarse) / tot, (1 - 1 / P__) * spp, 1e-12):
        bad_sh += 1
check("21s (f) pooling P equal processes understates ancillary cost by the share (1 - 1/P) s_pp", bad_sh == 0)


# ==============================================================================================
header("22. Failure modes: hallucination, automation bias, autonomy, pipelines, c_err (Section sec:tasks-failure)")
# ==============================================================================================
# (a) errors and hallucination under stakes-targeted review
def quality_cost_tax(xi, eo, eh, do_, dh, L, wtR):
    ebar, etil = eo + eh, eo * do_ + eh * dh
    g_ = 1 - xi * (1 + math.log(1 / xi)) if xi > 0 else 1.0
    return wtR * xi + etil * L * g_ + (ebar - etil) * L


bad_h = 0
zz_ = RNG.exponential(1, 400000)
for _ in range(20):
    eo, eh, do_, dh = RNG.uniform(0.01, 0.2), RNG.uniform(0.0, 0.1), RNG.uniform(0.8, 1), RNG.uniform(0.2, 0.8)
    xi = RNG.uniform(0.05, 0.9); L = 10.0; wtR = 1.0
    thr = np.quantile(zz_, 1 - xi); rev = zz_ >= thr
    o_err = RNG.uniform(size=zz_.size) < eo
    h_err = (~o_err) & (RNG.uniform(size=zz_.size) < eh / (1 - eo))
    caught = rev & ((o_err & (RNG.uniform(size=zz_.size) < do_)) | (h_err & (RNG.uniform(size=zz_.size) < dh)))
    loss_mc = L * np.mean(zz_ * (o_err | h_err) * (~caught)) + wtR * xi
    if abs(loss_mc - quality_cost_tax(xi, eo, eh, do_, dh, L, wtR)) > 0.02:
        bad_h += 1
    und_mc = np.mean((o_err | h_err) & ~caught)
    if abs(und_mc - ((eo + eh) - (eo * do_ + eh * dh) * xi)) > 3e-3:
        bad_h += 1
check("22a (a)-(b) taxonomy: cQ = w tR xi + etil L[1 - xi(1+ln 1/xi)] + (ebar - etil)L; undetected rate ebar - etil xi (MC)",
      bad_h == 0, f"violations={bad_h}")
# argmin uses etil
bad_h2 = 0
for _ in range(200):
    eo, eh, do_, dh = RNG.uniform(0.01, 0.3), RNG.uniform(0.0, 0.1), RNG.uniform(0.8, 1), RNG.uniform(0.2, 0.8)
    L, wtR = RNG.uniform(5, 100), RNG.uniform(0.2, 5)
    etil = eo * do_ + eh * dh
    res = optimize.minimize_scalar(lambda x: quality_cost_tax(x, eo, eh, do_, dh, L, wtR), bounds=(1e-12, 1), method="bounded",
                                   options={"xatol": 1e-12})
    if abs(res.x - math.exp(-wtR / (etil * L))) > 1e-5:
        bad_h2 += 1
check("22b (a) optimal economic review share exp(-w tR/(etil L)) uses the catchable rate etil", bad_h2 == 0)
# example (re-grounded on data/tasks/params_reliability.yaml): retrieval-grounded output, measured catch rates
eo_x, eh_x, do_x, dh_x, epsb_x = 0.03, 0.02, 0.65, 0.40, 0.02
floor_x = eo_x * (1 - do_x) + eh_x * (1 - dh_x)
floor_g = eo_x * (1 - do_x) + eh_x * (1 - 0.60)
floor_open = 0.05 * (1 - 0.40)
# consistency with Prop review(d): e = ebar, d = etil/ebar
ebar_x, etil_x = eo_x + eh_x, eo_x * do_x + eh_x * dh_x
bad_ht = 0
for _ in range(500):
    eo_, eh_ = RNG.uniform(0.001, 0.3), RNG.uniform(0.0, 0.2)
    do__, dh__ = RNG.uniform(0.3, 1.0), RNG.uniform(0.1, 0.9)
    eb_ = RNG.uniform(0.001, 0.2)
    ebr, etl = eo_ + eh_, eo_ * do__ + eh_ * dh__
    fl = eo_ * (1 - do__) + eh_ * (1 - dh__)
    if ((etl / ebr >= 1 - eb_ / ebr - 1e-12) != (fl <= eb_ + 1e-12)) or not close((ebr - eb_) / etl, (1 - eb_ / ebr) / (etl / ebr)):
        bad_ht += 1
check("22c (b) the hallucination feasibility test is the detection threshold of prop:tasks-review(d) with e = ebar and "
      "d = etil/ebar; the reliability share (ebar - epsbar)/etil equals (1 - epsbar/e)/d (500 draws)", bad_ht == 0)

# (b) automation bias: K(xi) = e xi (1 + ln 1/xi) d(prevalence), d = d0 (p/p0)^eps
def caught(xi, e, eps_d, dbar=0.9, p0=0.1):
    pr = e * (1 + math.log(1 / xi))
    d_ = min(1.0, dbar * (pr / p0) ** eps_d)
    return e * xi * (1 + math.log(1 / xi)) * d_, d_


bad_b = 0
for _ in range(200):
    e, eps_d = RNG.uniform(0.005, 0.05), RNG.uniform(0.1, 2)
    grid = np.linspace(0.01, 0.999, 2000)
    Ks = np.array([caught(x, e, eps_d, dbar=0.5, p0=1.0)[0] for x in grid])  # d < 1 throughout
    peak = grid[np.argmax(Ks)]
    if abs(peak - math.exp(-eps_d)) > 2e-3:
        bad_b += 1
check("22d (b) prevalence-dependent vigilance: caught errors peak at review share exp(-eps_d) (200 draws)", bad_b == 0)
# irony of automation: d(e - K)/de = 1 - (1 + eps)K/e
bad_i = 0
for _ in range(200):
    e, eps_d, xi = RNG.uniform(0.005, 0.05), RNG.uniform(0.1, 2), RNG.uniform(0.05, 0.95)
    h_ = 1e-8
    f_ = lambda ee: ee - caught(xi, ee, eps_d, dbar=0.5, p0=1.0)[0]
    fd = (f_(e + h_) - f_(e - h_)) / (2 * h_)
    K_, _ = caught(xi, e, eps_d, dbar=0.5, p0=1.0)
    if abs(fd - (1 - (1 + eps_d) * K_ / e)) > 1e-5:
        bad_i += 1
check("22e (c) d(undetected)/de = 1 - (1 + eps_d) K/e: a better model raises undetected errors when K/e > 1/(1+eps_d)",
      bad_i == 0)
xi_b, eps_b = 0.5, 0.5
share_b = xi_b * (1 + math.log(2)) * 0.85
share_c = xi_b * (1 + math.log(2)) * 0.65
print(f"     automation-bias example: peak review share {math.exp(-eps_b):.3f}; caught share at xi = 0.5: d = 0.85 {share_b:.3f}, "
      f"d = 0.65 {share_c:.3f}, vs 1/(1+eps) = {1/(1+eps_b):.3f}; detection uplift e^eps/(1+eps) = {math.exp(eps_b)/(1+eps_b):.4f}")
# (d) detection threshold under automation bias: min undetected = e - K(exp(-eps_d)); target feasible iff
#     d(e(1+eps_d)) >= (1 - epsbar/e) e^eps_d/(1+eps_d)
bad_bt = 0
for _ in range(300):
    e, eps_d = RNG.uniform(0.01, 0.3), RNG.uniform(0.05, 1.5)
    d0, p0 = RNG.uniform(0.2, 0.9), RNG.uniform(0.3, 3) * e
    epsb = RNG.uniform(0.1, 0.9) * e
    dfun = lambda pr: d0 * (pr / p0) ** eps_d
    grid = np.linspace(1e-4, 1, 20001)
    Ks = e * grid * (1 + np.log(1 / grid)) * d0 * ((e * (1 + np.log(1 / grid))) / p0) ** eps_d
    if np.max(Ks) > e or np.any(d0 * ((e * (1 + np.log(1 / grid))) / p0) ** eps_d > 1):
        continue  # outside the parametric assumption d < 1
    feas_grid = np.any(e - Ks <= epsb + 1e-12)
    feas_cf = dfun(e * (1 + eps_d)) >= (1 - epsb / e) * math.exp(eps_d) / (1 + eps_d) - 1e-12
    if feas_grid != feas_cf:
        bad_bt += 1
check("22s (d) under automation bias the target is attainable iff d(e(1+eps_d)) >= (1 - epsbar/e) e^eps_d/(1+eps_d); "
      "the factor e^eps/(1+eps) > 1 is 1.10 at eps_d = 0.5", bad_bt == 0 and abs(math.exp(0.5) / 1.5 - 1.0991) < 1e-4,
      f"violations={bad_bt}")

# (c) optimal autonomy with heavy tails and least privilege
def Emin_pareto(kap, pp):
    if abs(pp - 1) < 1e-12:
        return 1 + math.log(kap)
    return 1 + (1 - kap ** (1 - pp)) / (pp - 1)


bad_t = 0
for _ in range(100):
    pp, kap = RNG.uniform(0.5, 3), RNG.uniform(1.5, 1e2)
    zp = (1 - RNG.uniform(size=400000)) ** (-1 / pp)
    if abs(np.mean(np.minimum(zp, kap)) - Emin_pareto(kap, pp)) > 0.02 * Emin_pareto(kap, pp):
        bad_t += 1
    if pp > 1.1 and abs(Emin_pareto(1e300, pp) - pp / (pp - 1)) > 1e-6 * pp / (pp - 1):
        bad_t += 1
check("22g (a) E[min(Z, cap)] = 1 + (1 - cap^(1-p))/(p - 1) for Pareto(p) (MC); -> p/(p-1) if p > 1", bad_t == 0)
check("22h (a) p <= 1: E[min(Z, cap)] diverges as cap -> infinity (1 + ln cap at p = 1)",
      Emin_pareto(1e6, 1.0) > Emin_pareto(1e3, 1.0) + 6 and Emin_pareto(1e6, 0.8) > 10 * Emin_pareto(1e2, 0.8) / 3)
qv = 0.99
cvar_cf = lambda Ls, pp: Ls * pp / (pp - 1) * (1 - qv) ** (-1 / pp)
zp = (1 - RNG.uniform(size=4000000)) ** (-1 / 1.5)
var_ = np.quantile(zp, qv)
check("22i (a) CVaR_q of Pareto loss = L p (1-q)^(-1/p)/(p - 1) (MC, p = 1.5)",
      abs(zp[zp >= var_].mean() - cvar_cf(1.0, 1.5)) < 0.05 * cvar_cf(1.0, 1.5))
# monotone comparative statics of the optimal level (Topkis on a chain)
bad_m = 0
for _ in range(300):
    tlev = np.sort(RNG.uniform(0, 2, 4))[::-1]
    lhat = np.sort(RNG.uniform(0, 1, 4))
    wv = RNG.uniform(10, 100)
    prev = None
    for th in np.linspace(0, 5, 26):
        cost = wv * tlev / 50 + th * lhat
        best = max(np.where(cost <= cost.min() + 1e-12)[0])
        if prev is not None and best > prev:
            bad_m += 1
        prev = best
check("22j (c) optimal autonomy nonincreasing in a multiplier on misbehavior loss (rate, horizon, scale) (300 draws)",
      bad_m == 0)
# example: invoice approval step
wt_ap = 45.0 * 0.05
hum = {1: 0.6 * wt_ap, 2: 0.2 * wt_ap, 3: 0.10}
em = {1: 0.0, 2: 1e-4, 3: 2e-4}; dm = {1: 1.0, 2: 0.85, 3: 0.6}; Lm, pp_ex, cap_ex = 5000.0, 1.5, 50e3
Em = Emin_pareto(cap_ex / Lm, pp_ex)
cm = {a: em[a] * (1 - dm[a]) * Lm * Em for a in em}
tot = {a: hum[a] + cm[a] for a in em}
cv3 = cvar_cf(Lm, pp_ex)
print(f"     autonomy example: E[min(Z,10)] = {Em:.4f}; misbehavior cost {dict((a, round(cm[a], 4)) for a in cm)}; "
      f"total {dict((a, round(tot[a], 4)) for a in tot)}; uncapped CVaR99 at level 3 {cv3:,.0f}")
cv3_heavy = cvar_cf(Lm, 1.15)
print(f"     uncapped CVaR99 at tail index 1.15: {cv3_heavy:,.0f}")

# (d) pipelines
check("22l (a) max length for 95% at 1% per step = floor(ln .95/ln .99) = 5; pass^k with k = 5 cuts it to 1; "
      "at the measured hour-long-step reliability 0.735-0.944 no single step meets 95%, and three steps at 0.944 meet 80%",
      math.floor(math.log(0.95) / math.log(0.99)) == 5 and math.floor(math.log(0.95) / (5 * math.log(0.99))) == 1
      and 0.944 < 0.95 and math.floor(math.log(0.8) / math.log(0.944)) == 3 and 0.944 ** 3 >= 0.8 > 0.944 ** 4)
# (d) decomposition: constant hazard makes success depend on total human time; logistic with eta_r >= 1 penalizes splitting
bad_dec2 = 0
for _ in range(300):
    Dtot, Hh = RNG.uniform(0.1, 20), RNG.uniform(0.5, 20)
    parts = RNG.dirichlet(np.ones(int(RNG.integers(2, 8)))) * Dtot
    if abs(np.prod(2.0 ** (-parts / Hh)) - 2.0 ** (-Dtot / Hh)) > 1e-12:
        bad_dec2 += 1
    eta_ = RNG.uniform(1.0, 1.4)
    succ = lambda J_: (1 + (Dtot / (J_ * Hh)) ** (1 / eta_)) ** (-J_)
    if not all(succ(J_ + 1) < succ(J_) for J_ in range(1, 12)):
        bad_dec2 += 1
    # refinement: split one step of length x + y into x and y
    phi = lambda x_: math.log(1 + (x_ / Hh) ** (1 / eta_))
    x_, y_ = RNG.uniform(0.01, 10, 2)
    if not phi(x_) + phi(y_) > phi(x_ + y_):
        bad_dec2 += 1
check("22t (d) constant hazard: pipeline success 2^(-sum d_k/H) depends on total human time only; logistic with eta_r >= 1: "
      "splitting a step into two (or a task into more equal steps) lowers success (300 draws)", bad_dec2 == 0, f"violations={bad_dec2}")
bad_p2 = 0
for _ in range(200):
    eps_, dc, Js = RNG.uniform(1e-4, 0.02), RNG.uniform(0, 0.95), int(RNG.integers(1, 6))
    qb = RNG.uniform(0.8, 0.999)
    seg = (1 - (1 - eps_) ** Js) * (1 - dc)
    Jmax = Js * math.log(qb) / math.log(1 - seg)
    J0 = math.log(qb) / math.log(1 - eps_)
    if abs(Jmax * (1 - dc) / J0 - 1) > 0.05 + Js * eps_ * 2:
        bad_p2 += 1
check("22m (b) checkpoints with catch rate d_c multiply the maximum length by about 1/(1 - d_c) (small eps)", bad_p2 == 0)
bad_c = 0
for _ in range(300):
    eps_, J, Lc = RNG.uniform(1e-4, 0.3), int(RNG.integers(1, 40)), RNG.uniform(1, 10)
    direct = Lc * sum(eps_ * (1 - eps_) ** (i - 1) * (J - i + 1) for i in range(1, J + 1))
    cf = Lc * (J - (1 - eps_) * (1 - (1 - eps_) ** J) / eps_)
    if abs(direct - cf) > 1e-9 * max(1, direct):
        bad_c += 1
check("22n (c) cascading loss: L_c sum eps(1-eps)^(i-1)(J-i+1) = L_c[J - (1-eps)(1-(1-eps)^J)/eps]", bad_c == 0)
ee_s, JJ = sp.symbols("epsilon J", positive=True)
cf_s = JJ - (1 - ee_s) * (1 - (1 - ee_s) ** JJ) / ee_s
check("22o (c) small eps: expected cascading loss / L_c = eps J(J+1)/2 + O(eps^2)",
      is_zero(sp.limit(cf_s / ee_s, ee_s, 0) - JJ * (JJ + 1) / 2))

# (e) c_err floor
check("22p (a) c_err per unit >= review-proof floor (ebar - etil)L + c_m, and equals it plus etil L g(xi*)",
      all(quality_cost_tax(x, eo_x, eh_x, do_x, dh_x, 40.0, 0.0) >= (ebar_x - etil_x) * 40.0 - 1e-12
          for x in [0.1, 0.5, 0.9, 1.0]))
cerr_floor = floor_x * 40.0 + cm[2]
print(f"     c_err example (per invoice, approval step at autonomy 2): review-proof floor {floor_x*40.0:.4f} + misbehavior "
      f"{cm[2]:.4f} = {cerr_floor:.4f}; times 120k invoices = {cerr_floor*120e3:,.0f}")
# (f) success probability: pi_p = P(prod(1-eps_j) >= qbar) nonincreasing in J and rates
bad_s2 = 0
for _ in range(100):
    J = int(RNG.integers(2, 8)); qb = RNG.uniform(0.85, 0.98)
    a_, b_ = RNG.uniform(1, 3), RNG.uniform(50, 200)
    draws = RNG.beta(a_, b_, (20000, J + 1))
    p1 = np.mean(np.prod(1 - draws[:, :J], axis=1) >= qb)
    p2 = np.mean(np.prod(1 - draws, axis=1) >= qb)
    p3 = np.mean(np.prod(1 - np.minimum(1, 1.2 * draws[:, :J]), axis=1) >= qb)
    if p2 > p1 + 1e-12 or p3 > p1 + 1e-12:
        bad_s2 += 1
check("22r (f) success probability P(prod(1 - eps_j) >= qbar) falls with pipeline length and with step error rates",
      bad_s2 == 0)

# ----------------------------------------------------------------------------------------------
# ==============================================================================================
header("23. Running example: data/examples/invoice_chain.yaml (single source), its JSON and its macros")
# ==============================================================================================
# The YAML is resolved by code/examples/invoice_chain.py (engine loader for defaults). Everything below recomputes the
# example with this script's own implementation of the core formulas and checks (a) the JSON written by
# invoice_chain.py, (b) the macros file and the macros used in theory_core.tex, and (c) every qualitative claim the text
# makes about the example.
import json as _json
from pathlib import Path as _Path
_ROOT = _Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "code" / "examples"))
import invoice_chain as IC  # noqa: E402
icin = IC.load_inputs()
PI, STI = icin["P"], icin["steps"]
JS = _json.load(open(_ROOT / "data" / "examples" / "invoice_chain.json"))
check("23a the JSON was generated from the current YAML (inputs and sources agree)",
      all(_json.dumps(IC._clean(icin["log"][k]["value"])) == _json.dumps(JS["inputs"][k]["value"]) for k in icin["log"]))
expit = lambda z: 1 / (1 + math.exp(-z))
wI = PI["wage_annual"] * (1 + PI["tau_L"]) / PI["hours_per_fte"]
vI = PI["volume"]
aI = PI["r"] / (1 - math.exp(-PI["r"] * PI["T_A"]))
revfI = PI["r"] / math.expm1(PI["r"] * PI["T_up"])
i0I, i1I = PI["iota_low"], PI["iota_high"]


def ic_step(s_, qcap=None):
    """qcap: the conditional case's cap on the target (the firm accepts more residual error); the loss per error is
    unchanged. Regulated status is the process's (YAML setting); absent a setting, the engine rule target >= 0.99."""
    g_ = s_["gwa"]
    hr_ = bool(PI["high_reliability"]) and g_ in PI["high_rel_gwas"]
    q_ = max(s_["r_bar"], PI["r_bar_high"]) if hr_ else s_["r_bar"]
    if qcap is not None:
        q_ = min(q_, qcap)
    Lm_ = max(s_["L_mult"], PI["L_mult_regulated"]) if hr_ else s_["L_mult"]
    t_ = s_["t"]
    dec = any(str(g_).startswith(x) for x in PI["decision_gwas"])
    cre = any(str(g_).startswith(x) for x in PI["creation_gwas"])
    cm_ = next((PI["class_multiplier"][k] for k in sorted(PI["class_multiplier"], key=len, reverse=True) if str(g_).startswith(k)), 1.0)
    reg_ = s_["regulated_set"] if s_.get("regulated_set") is not None else (q_ >= 0.99)
    months = (PI["em_base"] * (1 + t_) ** PI["xi_d"] * (PI["regulated_mult"] if reg_ else 1.0)
              * max(vI * t_ / PI["hours_per_fte"], 0.05) ** PI["scope_elasticity"])
    FA_ = months * PI["ai_engineer_wage"] * PI["ai_engineer_premium"] * (1 + PI["tau_L"]) / 12 * (1 + PI["vendor_share"])
    return dict(id=s_["id"], t=t_, q=q_, L=Lm_ * wI * t_, wtR=PI["wage_premium"] * wI * PI["rho_rev"] * t_, cm=cm_,
                gui=any(str(g_).startswith(x) for x in PI["computer_use_gwas"]), dec=dec, cre=cre, FA=FA_,
                deff=t_ / (PI["transfer"] * max(PI["exposure"], PI["exposure_floor"]) ** PI["xi_exposure"]),
                out=s_["separable"] >= PI["separable_threshold"], elim=bool(s_["eliminable"]), imin=s_["iota_star"])


SI = [ic_step(s_) for s_ in STI]


def ic_ecap(s_, io):
    kap = 1 / (1 - min(PI["xi_context"] * io * PI["context_coverage"], 0.95))
    if s_["gui"] and io < PI["api_readiness"]:
        kap *= PI["computer_use_mult"]
    ratio = s_["deff"] / (PI["H0"] * kap)
    return expit(PI["b_logistic"] * math.log2(ratio))


def ic_e(s_, io):
    ectx = PI["e1"] + (PI["e0"] - PI["e1"]) * (1 - io)
    return 1 - (1 - ectx) * (1 - ic_ecap(s_, io))


def ic_cA(s_, io, d):
    e_ = ic_e(s_, io)
    xi_, cq_, eps_ = review(e_, s_["L"], s_["wtR"], 1 - s_["q"], PI["xi_min"], d)
    feas = (io >= s_["imin"] - 1e-12) and (d >= 1 - (1 - s_["q"]) / e_ - 1e-12)
    pin_ = PI["pi_h0"] * s_["cm"] * s_["t"] / (1 - min(ic_ecap(s_, io), PI["retry_cap"])) * (1 + PI["finops_share"])
    return dict(feas=feas, e=e_, xi=xi_, eps=eps_, pin=pin_, cA=pin_ + cq_ + s_["FA"] * aI / vI, dstar=max(1 - (1 - s_["q"]) / e_, 0))


def ic_alts(s_, io):
    wt_ = wI * s_["t"]
    c_ = {"H": wt_}
    if s_["out"]:
        c_["O"] = (PI["rho_O"] + PI["kappa_O"] + PI["zeta_O"]) * wt_
    eU_ex = PI["u_decision"] * PI["e_H"] if s_["dec"] else (-PI["u_creation"] * PI["e_H"] if s_["cre"] else 0.0)
    tU_ = s_["t"] / (1 + PI["beta_U"] * PI["exposure"] / PI["exposure_ref"])
    c_["U"] = wI * tU_ + PI["pi_h0"] * s_["cm"] * s_["t"] * PI["u_tok"] + eU_ex * s_["L"] + PI["U_share"] * s_["FA"] * aI / vI
    if s_["elim"] and io >= PI["iota_N"]:
        c_["N"] = PI["delta_N"] * wt_ + PI["redesign_months"] * PI["process_owner_wage"] * (1 + PI["tau_L"]) / 12 * aI / vI
    return c_


def ic_W(Z, io, d, S=None):
    S = SI if S is None else S
    Z = set(Z)
    if not all(ic_cA(S[j], io, d)["feas"] for j in Z):
        return -np.inf
    val = sum(vI * (min(ic_alts(S[j], io).values()) - ic_cA(S[j], io, d)["cA"]) for j in Z)
    for (i_, j_) in chain_edges(len(SI)):
        bi, bj = i_ in Z, j_ in Z
        eta_ = PI["h_AA0"] * (1 - io) if (bi and bj) else (PI["h_AM"] if (bi or bj) else PI["h_MM"])
        val += vI * wI * (PI["h_MM"] - eta_)
    Lp_ = PI["lambda_out"] * sum(wI * s_["t"] for s_ in SI)
    QZ = np.prod([1 - ic_cA(S[j], io, d)["eps"] if j in Z else PI["q_M"] for j in range(len(SI))])
    val += vI * Lp_ * (QZ - PI["q_M"] ** len(SI))
    if len(Z) == len(SI):
        val += PI["Xi_share"] * sum(vI * wI * s_["t"] for s_ in SI)
    return val


JD, JI = JS["default"], JS["illustration"]
dR0 = PI["d_R"]
ok_tab = True
for s_, rj in zip(SI, JD["activities"]):
    c0_, c1_ = ic_cA(s_, i0I, dR0), ic_cA(s_, i1I, dR0)
    al1 = ic_alts(s_, i1I)
    ok_tab &= close(rj["c_H"], wI * s_["t"]) and close(rj["c_M_high"], min(al1.values())) and close(rj["pi_n_high"], c1_["pin"])
    ok_tab &= close(rj["e_low"], c0_["e"]) and close(rj["e_high"], c1_["e"]) and close(rj["d_star_high"], c1_["dstar"])
    ok_tab &= close(rj["F_A"], s_["FA"]) and close(rj["qbar"], s_["q"]) and (rj["feasible_high"] == c1_["feas"])
d_req_I = max(ic_cA(s_, i1I, dR0)["dstar"] for s_ in SI)
# conditional case (redesigned 29 Oct 2026, P2 theory pass v2): detection at the top of the measured range; every target
# capped at min(r_bar_high, q*), where r_bar_high is the human-parity target and q* the highest level (in steps of 0.1
# percentage point) that every step above the chain's lowest target meets at readiness 0.9 at that detection rate. The
# cap never raises a target (the earlier cap at q* alone exceeded r_bar_high once r_bar_high became 0.98).
d_ill_I = icin["sensitivity"]["d_R"]["high"]
qmin_ = min(s_["q"] for s_ in SI)
qstar_I = math.floor(min(1 - ic_e(s_, i1I) * (1 - d_ill_I) for s_ in SI if s_["q"] > qmin_ + 1e-12) * 1000 + 1e-9) / 1000
qcap_I = min(PI["r_bar_high"], qstar_I)
SC = [ic_step(s_, qcap_I) for s_ in STI]
for s_, rj in zip(SC, JI["activities"]):
    c1_ = ic_cA(s_, i1I, d_ill_I)
    ok_tab &= c1_["feas"] and close(rj["c_A_high"], c1_["cA"]) and close(rj["F_A"], s_["FA"]) and close(rj["qbar"], s_["q"])
check("23b Table tab:tasks-example recomputed independently from the YAML: c_H, c_M, pi n, e(0.4), e(0.9), qbar, d*, F_A, "
      "and c_A at the conditional detection rate", ok_tab)
def ic_iota_floor(s_, d):
    """lowest readiness at which step s_ meets its target at catch rate d (bisection on this script's ic_cA); None
    if not even at full readiness"""
    if not ic_cA(s_, 1.0, d)["feas"]:
        return None
    lo_, hi_ = 0.0, 1.0
    if ic_cA(s_, 0.0, d)["feas"]:
        return 0.0
    for _ in range(60):
        mid_ = 0.5 * (lo_ + hi_)
        if ic_cA(s_, mid_, d)["feas"]:
            hi_ = mid_
        else:
            lo_ = mid_
    return hi_


SIid = {s_["id"]: s_ for s_ in SI}
JDa = {r_["id"]: r_ for r_ in JD["activities"]}
flo_ = {k_: ic_iota_floor(SIid[k_], dR0) for k_ in SIid}
MJ = JS["macros"]
check("23c default verdict: at the engine's detection rate no step can be automated at readiness 0.9 (detection thresholds "
      "above d_R); capture and matching (human-parity target r_bar_high) reach it only above the quoted readiness "
      "levels, both above 0.95; approval, whose activity prior asks for more than r_bar_high, never does (its best at "
      "full readiness is below its target); exception handling becomes feasible only just above 0.9",
      (not any(r["feasible_high"] for r in JD["activities"]))
      and all(r["d_star_high"] > dR0 for r in JD["activities"])
      and all(abs(SIid[k_]["q"] - PI["r_bar_high"]) < 1e-12 for k_ in ("capture", "match"))
      and all(flo_[k_] is not None and 0.95 < flo_[k_] < 1.0 and close(JDa[k_]["iota_feasible"], flo_[k_], 1e-6)
              for k_ in ("capture", "match"))
      and MJ["icCaptureIotaFeas"] == f"{flo_['capture']:.3f}" and MJ["icMatchIotaFeas"] == f"{flo_['match']:.3f}"
      and SIid["approval"]["q"] > PI["r_bar_high"] and flo_["approval"] is None and JDa["approval"]["iota_feasible"] is None
      and 1 - ic_e(SIid["approval"], 1.0) * (1 - dR0) < SIid["approval"]["q"]
      and JD["exceptions"]["iota_feasible"] > i1I and JD["exceptions"]["iota_feasible"] < 0.91,
      f"floors {flo_}")
# q* is the highest common target (to 0.1 pp) that every step above the chain's lowest target meets: a common target
# 0.1 pp higher fails for one of them
qstar_next_fails = min(1 - ic_e(s_, i1I) * (1 - d_ill_I) for s_ in SI if s_["q"] > qmin_ + 1e-12) < qstar_I + 0.001
relaxed_ = sorted(a_["id"] for a_, b_ in zip(SC, SI) if a_["q"] < b_["q"] - 1e-12)
check("23d conditional case: the chain's detection threshold exceeds the top of the measured range; detection is set at that "
      "top; every target is capped at min(r_bar_high, q*), q* the highest common target (to 0.1 pp) that the steps above "
      "the chain's lowest target meet there; "
      "r_bar_high binds (q* is above it), so only approval, whose prior asks for more than human parity, is relaxed; no "
      "target is raised; the residual equals the human baseline error rate; the loss per error is unchanged; the steps "
      "are regulated by a YAML setting, so their builds keep the regulated multiplier at the capped target",
      close(JD["d_required_high"], d_req_I) and d_req_I > d_ill_I and close(JI["d_R"], d_ill_I) and close(JI["q_cap"], qcap_I)
      and close(JI["q_star"], qstar_I) and qstar_I > PI["r_bar_high"] and close(qcap_I, PI["r_bar_high"])
      and relaxed_ == ["approval"] and sorted(x_["id"] for x_ in JI["relaxed_steps"]) == relaxed_
      and all(a_["q"] <= b_["q"] + 1e-12 for a_, b_ in zip(SC, SI))
      and abs((1 - qcap_I) - PI["e_H"]) < 1e-12 and close(JI["residual_accepted"], 1 - qcap_I)
      and all(ic_cA(s_, i1I, d_ill_I)["feas"] for s_ in SC) and qstar_next_fails
      and all(close(a_["L"], b_["L"]) for a_, b_ in zip(SC, SI))
      and all(close(a_["FA"], b_["FA"]) for a_, b_ in zip(SC, SI))
      and all(st_.get("regulated_set") is True for st_ in STI),
      f"q* {qstar_I}, cap {qcap_I}, relaxed {relaxed_}")
fullI = range(len(SI))
W1_I = ic_W(fullI, i1I, d_ill_I, SC)
singles_I = {SC[j]["id"]: ic_W([j], i1I, d_ill_I, SC) for j in range(len(SC))}
vals_I = {Z: ic_W(Z, i1I, d_ill_I, SC) for Z in subsets(len(SC))}
bestI = max(vals_I, key=vals_I.get)
PR = JI["process"]
pairI = frozenset(j for j in range(len(SC)) if SC[j]["id"] in ("exceptions", "approval"))
nonempty_ = {Z: v_ for Z, v_ in vals_I.items() if len(Z) > 0}
fp_ = PR["best_first_pays_iota"]
# sensitivity: approval capped at q* instead (the earlier design)
SQ = [ic_step(s_, qstar_I) for s_ in STI]
W1_Q = ic_W(fullI, i1I, d_ill_I, SQ)
pair_Q = ic_W(pairI, i1I, d_ill_I, SQ)
AQ = JI["alt_qstar"]
check("23e conditional case at readiness 0.9: W(full) negative; every step alone loses money; exception handling and "
      "approval together pay and are the best set, worth more than the sum of their stand-alone values (complements) "
      "and more than the whole chain; that pair is the first set to pay, at the quoted readiness, below the whole chain's "
      "threshold; with approval capped at q* instead, the pair loses money and W(full) is lower (sensitivity)",
      close(PR["W_full_high"], W1_I, 1e-6) and W1_I < 0 and bestI == pairI and vals_I[pairI] > 0 and PR["any_set_pays_high"]
      and sorted(PR["best_set_high"]) == ["approval", "exceptions"]
      and all(v_ < 0 for v_ in singles_I.values())
      and all(close(PR["singles_high"][k], v_, 1e-6) for k, v_ in singles_I.items())
      and close(PR["pair_exc_appr_high"], vals_I[pairI], 1e-6) and close(PR["best_value_high"], vals_I[pairI], 1e-6)
      and vals_I[pairI] > singles_I["exceptions"] + singles_I["approval"] and vals_I[pairI] > W1_I
      and sorted(PR["best_first_pays_set"]) == ["approval", "exceptions"]
      and abs(ic_W(pairI, fp_, d_ill_I, SC)) < 1.0 and ic_W(pairI, fp_ + 1e-4, d_ill_I, SC) > 0
      and all(ic_W(Z, fp_ - 1e-4, d_ill_I, SC) <= 0 for Z in subsets(len(SC)) if len(Z) > 0)
      and fp_ < PR["iota_star_above_N"]
      and pair_Q < 0 < vals_I[pairI] and W1_Q < W1_I and close(AQ["W_full_high"], W1_Q, 1e-6)
      and close(AQ["pair_exc_appr_high"], pair_Q, 1e-6) and close(AQ["q_cap"], qstar_I),
      f"W(full) {W1_I:,.0f}, pair {vals_I[pairI]:,.0f}; at q*: W(full) {W1_Q:,.0f}, pair {pair_Q:,.0f}")
dv_ = PR["dividends_high"]
check("23f integration dividends sum to W(full); unit-cost penalty negative, coordination and overhead positive, chained "
      "errors negative (Prop prop:tasks-integration(a))", close(dv_["unit"] + dv_["coord"] + dv_["rel"] + dv_["overhead"], W1_I, 1e-6)
      and dv_["unit"] < 0 < dv_["coord"] and dv_["rel"] < 0 < dv_["overhead"] and dv_["Q_A"] < dv_["Q_M"])
iN_ = PI["iota_N"]
feas_ = PR["iota_chain_feasible"]
grid_lo = [feas_ + 1e-9 + k * (iN_ - 1e-6 - feas_ - 1e-9) / 100 for k in range(101)]
grid_hi = [iN_ + 1e-9 + k * (1 - iN_ - 1e-9) / 200 for k in range(201)]
Wlo_ = [ic_W(fullI, x_, d_ill_I, SC) for x_ in grid_lo]
Whi_ = [ic_W(fullI, x_, d_ill_I, SC) for x_ in grid_hi]
Wb_, Wa_ = ic_W(fullI, iN_ - 1e-9, d_ill_I, SC), ic_W(fullI, iN_ + 1e-9, d_ill_I, SC)
check("23g conditional case: the chain is infeasible below the quoted readiness (approval's floor); below iota_N, where "
      "elimination of capture becomes feasible, W(full) rises but stays negative; at iota_N the benchmark improves and "
      "W(full) falls by the quoted amount; above iota_N it rises, is negative at 0.9 and positive at 0.95, and is zero at "
      "the quoted readiness",
      ic_W(fullI, feas_ - 1e-6, d_ill_I, SC) == -np.inf and feas_ < iN_
      and all(np.isfinite(Wlo_)) and all(b_ > a_ for a_, b_ in zip(Wlo_, Wlo_[1:])) and max(Wlo_) < 0
      and close(PR["W_below_N"], Wb_, 1e-6) and close(PR["W_above_N"], Wa_, 1e-6) and Wa_ < Wb_ < 0
      and all(np.isfinite(Whi_)) and all(b_ > a_ for a_, b_ in zip(Whi_, Whi_[1:]))
      and ic_W(fullI, 0.9, d_ill_I, SC) < 0 < ic_W(fullI, 0.95, d_ill_I, SC)
      and close(PR["W_by_iota"]["0.95"], ic_W(fullI, 0.95, d_ill_I, SC), 1e-6)
      and abs(ic_W(fullI, PR["iota_star_above_N"], d_ill_I, SC)) < 1.0,
      f"feasible from {feas_:.3f}; W just below/above iota_N {Wb_:,.0f}/{Wa_:,.0f}")
AX = JI["augment_exceptions"]
sX = SC[2]
check("23h exception handling at 0.9: automated cost by detection rate as quoted; ties augmentation at the quoted rate; "
      "infeasible below its threshold, which is above the default rate",
      close(AX["sweep"]["1.000"], ic_cA(sX, i1I, 1.0)["cA"]) and close(AX["sweep"]["0.850"], ic_cA(sX, i1I, 0.85)["cA"])
      and abs(ic_cA(sX, i1I, AX["d_tie"])["cA"] - ic_alts(sX, i1I)["U"]) < 1e-6 and AX["d_infeasible"] > dR0
      and not ic_cA(sX, i1I, dR0)["feas"])
# transition: recompute the NPV and its pieces from the JSON terms with this script's transition_npv
TJ = JS["transition"]
TPj = dict(r=TJ["r"], Th=TJ["T_h"], W=TJ["W"], F=TJ["F"], I=TJ["I"], CJ=TJ["C_J"], Cpar=TJ["C_par"], Cstr=TJ["C_str"],
           Cwo=TJ["C_wo"], pis=TJ["varpi_p"], bbar=TJ["bbar_p"], Tdet=TJ["T_det"], Lroll=TJ["L_roll"])
RJ = TJ["results"]
dt_ = TJ["detail"]
check("23i transition terms follow the engine conventions: C_par = omega C_0 + nu E_p + C_dup, C_J = dip C_0, L_roll = mult C_0, "
      "F = builds + integration + other, integration = c_sys n_sys [f(0.9) - f(0.4)], T_par = the regulated/ICFR floor",
      close(TJ["C_par"], PI["omega_par"] * dt_["C0"] + PI["nu_rec"] * dt_["E_p"] + dt_["C_dup"])
      and close(TJ["C_J"], PI["dip_share"] * dt_["C0"] * PI["dip_years"]) and close(TJ["L_roll"], PI["L_roll_mult"] * dt_["C0"])
      and close(TJ["F"], TJ["F_build"] + TJ["F_int"] + TJ["F_other"])
      and close(TJ["F_int"], PI["int_cost_per_system"] * PI["n_systems"] * (0.9 / 0.1 - 0.4 / 0.6))
      and close(TJ["F_build"], sum(s_["FA"] for s_ in SC)) and close(RJ["T_par"], max(PI["T_par_min_regulated"], PI["icfr_min_parallel"]))
      and close(TJ["W"], TJ["W_before_run"] - JS["ancillary"]["total"]))
# stranded cost and survivors (prop:labor-survivor): own implementation of N^q, C^surv and O_s
modes0_ = [min(ic_alts(s_, i0I), key=ic_alts(s_, i0I).get) for s_ in SC]
Nhc_ = sum(vI * s_["t"] / PI["hours_per_fte"] for s_, m_ in zip(SC, modes0_) if m_ in ("H", "U"))
Nsv_ = max(Nhc_ - dt_["fte_removed"], 0.0)
wy_ = wI * PI["hours_per_fte"]
nus_ = PI["survivor_quits_per_share"] * (dt_["fte_removed"] / Nhc_) / PI["T_s"]
Nq_ = Nsv_ * math.exp(-PI["nu_q"] * PI["T_s"]) * (1 - math.exp(-nus_ * PI["T_s"]))
Csurv_ = wy_ * PI["c_rep"] * Nq_
Os_ = wy_ * Nsv_ * PI["T_s"] * (PI["c_rep"] * PI["survivor_excess_quits"] / PI["T_s"] + PI["delta_eff"])
check("23z stranded cost: C_str = severance + break fees + redeployment + C^surv of prop:labor-survivor(a), zero at the "
      "engine defaults (no share-dependent quits); the announcement charge O_s of part (b) is reported separately and is not "
      "in C_str or the NPV; survivors are the in-house staff of the changed steps less the displaced",
      close(TJ["C_str"], dt_["C_sev"] + dt_["C_brk"] + dt_["C_redeploy"] + Csurv_) and Csurv_ == 0.0
      and close(TJ["C_surv"], Csurv_) and close(dt_["N_hc"], Nhc_) and close(dt_["N_sv"], Nsv_) and close(TJ["O_s"], Os_)
      and TJ["O_s"] > 0 and close(TJ["NPV_own_wave"], RJ["NPV"] - Os_) and "C_attr" not in dt_)
check("23j transition NPV, NPV if certain, Y_s and Y_f recomputed by this script's transition_npv",
      close(RJ["NPV"], transition_npv(TPj, RJ["T_par"]), 1e-9) and close(RJ["NPV_certain"], transition_npv(dict(TPj, pis=1.0, bbar=1.0), RJ["T_par"]), 1e-9))
check("23k sign claims: W < 0 after run costs, so the NPV is negative at every integration cost (low, default, high) and for "
      "a firm already integrated; no break-even in F (it would be negative), T_h (unlimited horizon negative) or varpi_p",
      TJ["W"] < 0 and TJ["W_before_run"] > 0 and all(JS["transition_cases"][c][l]["NPV"] < 0 for c in "ab" for l in ("low", "default", "high"))
      and RJ["F_breakeven"] < 0 and RJ["NPV_unlimited"] < 0 and RJ["NPV_varpi_one"] < 0 and RJ["T_h_breakeven"] is None
      and RJ["varpi_breakeven"] is None and JS["transition_cases"]["a"]["low"]["NPV"] > JS["transition_cases"]["a"]["high"]["NPV"])
check("23l even with perfect detection, full automation is positive before run costs and negative after them",
      JS["detection"]["W_at_d1"] > 0 > JS["detection"]["W_at_d1_run"])
PJ = JS["pilot"]["a"]
check("23m pilot: Y_s < 0, so a revealing pilot is worth minus its cost (the engine's share of the builds plus the fixed "
      "cost) at every success probability", PJ["Y_s"] < 0 and close(PJ["VP"], -PJ["F_pil"])
      and close(PJ["F_pil"], PI["pilot_cost_share"] * TJ["F_build"] + PI["pilot_fixed_cost"]) and JS["pilot"]["b"]["Y_s"] < 0)
SPj = JS["score_path"]
y1c_ = -(TPj["F"] + TPj["I"] + TPj["CJ"] + TPj["Cpar"] * 0.5 - TPj["W"] * 0.25 + TPj["Cstr"] - TPj["W"] * 0.5) / SPj["revenue"]
y1g_ = y1c_ + (TPj["F"] + TPj["I"] - TPj["F"] / PI["T_A"] - TPj["Cwo"]) / SPj["revenue"]
check("23n score path: first-year cash and GAAP changes match Prop scorepath(c) in the simple convention; later cash years "
      "equal W/S (negative)", close(SPj["cash"][0], y1c_, 1e-9) and close(SPj["gaap"][0], y1g_, 1e-9)
      and close(SPj["cash"][1], TPj["W"] / SPj["revenue"], 1e-9) and SPj["cash"][1] < 0)
AN = JS["ancillary"]
mt_ = PI["delta_M"] * sum(s_["FA"] for s_ in SC)
rv_ = PI["reval_share"] * sum(s_["FA"] for s_ in SC) * revfI
td_ = PI["c_int"] * 4 * len(SI) + PI["c_cpl"] * 16 * (len(SI) - 1)
check("23o run costs: maintenance, revalidation (discounted factor), technical debt (4 integrations per step, 3 coupled pairs) "
      "and risk cost as quoted; they turn the conditional case's W(full) negative at 0.9 and at every readiness",
      close(AN["maintenance"], mt_) and close(AN["revalidation"], rv_) and close(AN["tech_debt"], td_)
      and close(AN["risk"], risk_cost(AN["C_inc"], PI["C_s"])[0]) and AN["W_high_after"] < 0 and AN["iota_star_run"] is None
      and close(AN["volume_factor"], 1 + PI["delta_M"] * PI["T_A"] + PI["reval_share"] * PI["T_A"] / PI["T_up"]))
WN = JS["window"]
check("23p window (matching): review and build alone exceed the vendor's all-in price, so in-house automation never beats "
      "the vendor at any inference price", WN["c0A"] > (PI["rho_O"] + PI["kappa_O"] + PI["zeta_O"]) * wI * SI[1]["t"])
CP = JS["capital"]
check("23q capital (owned inference): value, cash and GAAP effects per invoice as quoted, all negative, and the cash penalty "
      "exceeds the value penalty because g > r", CP["value"] < 0 and CP["cash"] < CP["value"] < 0 and CP["gaap"] < 0
      and CP["g"] > CP["r"] and close(CP["value"], CP["dc"] - (CP["r"] + CP["delta_K"]) * CP["dK"]))
BB = JS["build_buy"]
check("23r build or buy: buying saves money at the example volume and the saving exceeds the lock-in cap; run costs raise "
      "the build threshold", BB["buy_saving"] > BB["lock_cap"] > 0 and BB["v_BB"] > vI > BB["v_BB_no_run"]
      and close(BB["v_BB"], (BB["C_fix_build"] - BB["C_fix_buy"]) / BB["c_v_minus_pin"]))
FH, FB, FAu, FC = JS["failure"]["hallucination"], JS["failure"]["bias"], JS["failure"]["autonomy"], JS["failure"]["cerr"]
check("23s hallucination example: the review-proof floor exceeds the tolerance, ordinary errors supply most of it, and a "
      "hallucination catch rate of 0.6 barely lowers it", FH["floor"] > FH["tolerance"] and FH["floor_ordinary"] > 0.5 * FH["floor"]
      and FH["floor_dh_06"] > FH["tolerance"] and close(FH["floor"], FH["e_o"] * (1 - FH["d_o"]) + FH["e_h"] * (1 - FH["d_h"])))
check("23t automation-bias numbers (engine eps_d): peak exp(-eps_d), irony threshold 1/(1+eps_d), caught shares at a review "
      "share of one half for the top and central catch rates on opposite sides of the threshold",
      close(FB["peak"], math.exp(-FB["eps_d"])) and FB["caught_top"] > FB["irony_threshold"] > FB["caught_central"])
check("23u autonomy example: CVaR of an event far inside the appetite at both tail indices; misbehavior costs a fraction of a "
      "cent per invoice; neither automated level can meet approval's target at the default detection rate",
      FAu["cvar_uncapped_low"] < 0.01 * FAu["L_max"] and FAu["c_m"]["3"] < 0.01 and not FAu["feasible_level3"]
      and FAu["d_star"] > dR0 and close(FC["total_unit"], FC["floor_unit"] + FC["misbehavior_unit"]))
check("23s2 prop:tasks-cerr(c): with no review the floor is (e_o + e_h) L plus misbehavior, above the floor with human "
      "review; a model reviewer that shares a share rho of the errors catches (1 - rho) d^A, between the two",
      close(FC["noreview_unit"], (FH["e_o"] + FH["e_h"]) * FC["L"] + FAu["c_m"]["3"], 1e-9)
      and FC["noreview_unit"] > FC["total_unit"] and close(FC["noreview_annual"], FC["noreview_unit"] * vI, 1e-9)
      and all(FH["e_o"] * (1 - (1 - rho_) * FH["d_o"]) * FC["L"] <= FH["e_o"] * FC["L"] + 1e-12 for rho_ in (0.0, 0.3, 0.6, 1.0)))
# macros: file = JSON copy; every \ic macro used in theory_core.tex is defined; the section inputs the file
mac_tex = open(_ROOT / "part2" / "tables" / "invoice_macros.tex").read()
mac_def = dict(re.findall(r"\\newcommand\{\\(ic[A-Za-z]+)\}\{(.*)\}\n", mac_tex))
core_tex = open(_ROOT / "part2" / "theory_core.tex").read()
used = set(re.findall(r"\\(ic[A-Z][A-Za-z]*)", core_tex))
check("23v macros: invoice_macros.tex equals the macros recorded in the JSON; every \\ic... macro used in theory_core.tex is "
      "defined; theory_core.tex inputs the macros file", mac_def == JS["macros"] and used <= set(mac_def)
      and "\\input{part2/tables/invoice_macros.tex}" in core_tex, f"undefined: {sorted(used - set(mac_def))}")
HZ = TJ["horizons"]
ThE_ = float(PI["T_h_engine"])
rb_ = [k * PI["T_A"] for k in range(1, 50) if k * PI["T_A"] < ThE_]
rbpv_ = TJ["varpi_p"] * TJ["F_build"] * sum((1 - PI["delta_F"]) ** x_ * math.exp(-TJ["r"] * x_) for x_ in rb_)
check("23x horizons: T_h is the book life of one build; over the engine's planning horizon the program redoes the builds every "
      "T_A years at the declined cost F_build (1 - delta_F)^(k T_A) on the success branch (engine plans.py), and its NPV is "
      "below the single-build NPV",
      close(TJ["T_h"], PI["T_h"]) and HZ["rebuild_years"] == rb_ and close(HZ["rebuild_pv"], rbpv_)
      and close(HZ["program"], HZ[f"{ThE_:g}"] - rbpv_) and close(HZ[f"{ThE_:g}"], transition_npv(dict(TPj, Th=ThE_), RJ["T_par"]), 1e-9)
      and HZ["program"] < RJ["NPV"] < 0)
import hashlib as _hashlib
def _sha(path_):
    return _hashlib.sha256(open(path_, "rb").read()).hexdigest()
SH = JS["source_sha256"]
check("23y the JSON records the sha256 of engine defaults.yaml (and params.yaml, params_reliability.yaml, the example YAML, "
      "the activity priors) and they match the files now: the example is current with the engine",
      SH["engine/src/autofrontier/defaults.yaml"] == _sha(_ROOT / "engine" / "src" / "autofrontier" / "defaults.yaml")
      and all(v_ == _sha(_ROOT / k_) for k_, v_ in SH.items() if v_ is not None),
      f"stale: {[k_ for k_, v_ in SH.items() if v_ is not None and v_ != _sha(_ROOT / k_)]}")
check("23w the JSON lists the transition block first (other sections' loaders search it depth first) and splits F into "
      "F_build and F_int", list(JS.keys())[0] == "transition" and all(k in JS["transition"] for k in ("F_build", "F_int", "W", "C_par", "T_par")))

n_fail = sum(1 for _, ok in RESULTS if not ok)
print("\n" + "=" * 78)
print(f"SUMMARY: {len(RESULTS) - n_fail}/{len(RESULTS)} checks passed" + ("" if n_fail == 0 else f"; {n_fail} FAILED"))
print("=" * 78)
sys.exit(0 if n_fail == 0 else 1)
