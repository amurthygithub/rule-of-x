#!/usr/bin/env python3
"""
verify_part2_competition.py

Symbolic (sympy) and numerical (numpy/scipy) checks of every closed form, threshold, equilibrium claim
and worked example in
  part2/theory_competition.tex   (subsection "Strategic adoption among incumbents", label sec:ext-game)
  part2/proofs_competition.tex   (proofs, label app:proofs-game)
Paper 2, "The Economics of AI Transformation" (formerly Part II of "The Efficient Frontier of Growth and Profitability").

Run:  python3 code/verify_part2_competition.py      (about ten seconds)
Exit code 0 iff every check passes. Check names cite the LaTeX labels of the results.
Numbers printed with "->" are the ones quoted in theory_competition.tex; the script asserts them, and
check T1 confirms that each quoted string appears in the tex file.

Notation (see notes/competition_notes.md):
  n      -> n_c (number of incumbents), H = 1/n_c (Herfindahl index of symmetric firms)
  E1(k), E0(k) -> E_a(k): flow earnings of an adopter / non-adopter when k rivals have adopted (times e^{Gt})
  Epriv(k) = E1(k) - E0(k);  Eeq = E1(n-1) - E0(0)
  phi_ind, phi_own -> bar varphi^ind, bar varphi^own (level pass-through of a common / unilateral saving)
  phi    -> varphi (elasticity pass-through of Lemma prices),  eps -> epsilon (price elasticity of demand)
  w      -> varpi (probability that the automation works for the industry)
  To(E)  -> T^circ(E), the single-firm adoption date of eq:ext-game-To
  VL, VF, VJ -> V^L, V^F, V^J (leader, follower and joint-adoption values, present values at date 0)
"""
import math
import re
import sys
from pathlib import Path

import numpy as np
import sympy as sp
from scipy import integrate, optimize

RNG = np.random.default_rng(20261029)
RESULTS = []
ROOT = Path(__file__).resolve().parent.parent
QUOTED = []          # strings that must appear in theory_competition.tex


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ::  {detail}" if detail else ""))


def header(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol * (1 + abs(b))


def quote(s):
    QUOTED.append(s)
    return s


# ==============================================================================================
# Running example (illustrative values; see the text)
#   price 1.00, unit cost 0.80 (unit margin 0.20), cut delta_c = 0.10, 20 million units a firm a year (B = 0.01),
#   r = 0.10, G = 0.04, adoption cost F0 = $20 million falling 30% a year (as in prop:ext-timing's example)
# ==============================================================================================
P0, C0, MG, DC, Y0 = 1.00, 0.80, 0.20, 0.10, 20.0
BB = MG / Y0
R, GG, DF, F0 = 0.10, 0.04, 0.30, 20.0


class Timing:
    """Exponential adoption cost and growing flows: the objects of ass:ext-game."""

    def __init__(self, r=R, G=GG, dF=DF, F0_=F0):
        self.r, self.G, self.dF, self.F0 = r, G, dF, F0_

    def FA(self, t):
        return self.F0 * math.exp(-self.dF * t)

    def cost(self, t):                       # present value at date 0 of adopting at t
        return math.exp(-self.r * t) * self.FA(t)

    def I(self, a, b):                       # int_a^b e^{-(r-G)s} ds
        k = self.r - self.G
        eb = 0.0 if b == math.inf else math.exp(-k * b)
        return (math.exp(-k * a) - eb) / k

    def To(self, E):
        assert self.G + self.dF > 0, "ass:ext-game requires G > -delta_F"
        if E <= 0:
            return math.inf
        return max(0.0, math.log((self.r + self.dF) * self.F0 / E) / (self.G + self.dF))


TM = Timing()


def lin_cournot(n, mg=MG, d=DC, B=BB):
    E1 = lambda k: (mg + (n - k) * d / (n + 1)) ** 2 / B
    E0 = lambda k: (mg - k * d / (n + 1)) ** 2 / B
    return E1, E0


def cournot_solve(costs, P, dP):
    """Asymmetric Cournot equilibrium for inverse demand P(Q): solve Q P'(Q) + n P(Q) = sum c."""
    costs = np.asarray(costs, float)
    n = len(costs)
    f = lambda Q: Q * dP(Q) + n * P(Q) - costs.sum()
    lo, hi = 1e-9, 1.0
    while f(hi) > 0:
        hi *= 2
        if hi > 1e9:
            raise RuntimeError("no root")
    Q = optimize.brentq(f, lo, hi, xtol=1e-15, rtol=1e-15, maxiter=500)
    p = P(Q)
    q = (p - costs) / (-dP(Q))
    return p, q, (p - costs) * q


def bertrand_solve(costs, al, be, ga):
    """Differentiated Bertrand with q_i = al - be p_i + ga sum_{l != i} p_l."""
    c = np.asarray(costs, float)
    n = len(c)
    M = (2 * be + ga) * np.eye(n) - ga * np.ones((n, n))
    p = np.linalg.solve(M, al + be * c)
    q = al - be * p + ga * (p.sum() - p)
    return p, q, (p - c) * q


# ==============================================================================================
header("A. lem:ext-game-pass: pass-through and the adoption incentives")
# ==============================================================================================
# A1 linear Cournot closed forms against a direct equilibrium solve, and consistency with prop:ext-should(a)
ok = True
for _ in range(200):
    n = int(RNG.integers(2, 8))
    A_ = RNG.uniform(1.0, 3.0)
    B_ = RNG.uniform(0.005, 0.05)
    c = RNG.uniform(0.2, 0.6) * A_
    mg = (A_ - c) / (n + 1)
    d = RNG.uniform(0.0, 1.0) * mg * (n + 1) / (n - 1) * 0.95
    E1, E0 = lin_cournot(n, mg, d, B_)
    P = lambda Q: A_ - B_ * Q
    dP = lambda Q: -B_
    for k in range(n):
        _, _, pr = cournot_solve([c - d] * (k + 1) + [c] * (n - k - 1), P, dP)
        ok &= close(pr[0], E1(k), 1e-8)
        _, _, pr = cournot_solve([c] + [c - d] * k + [c] * (n - k - 1), P, dP)
        ok &= close(pr[0], E0(k), 1e-8)
E1, E0 = lin_cournot(4)
ok &= close(E1(3) - E0(0), 0.0084 / BB) and close(E1(3) - E0(3), 0.0288 / BB) and close(E1(0) - E0(0), 0.0384 / BB)
check("A1 lem:ext-game-pass(a): linear Cournot earnings E_1(k) = [mg + (n-k)d/(n+1)]^2/B, E_0(k) = [mg - kd/(n+1)]^2/B "
      "match a direct equilibrium solve, and reproduce prop:ext-should(a)'s 0.0084/B, 0.0288/B, 0.0384/B", ok)

# A2 differentiated Bertrand: margins are linear in cuts with coefficients a1, a2; profit = be * margin^2
ok = True
ok_cond = True
for _ in range(200):
    n = int(RNG.integers(2, 7))
    be = RNG.uniform(0.5, 2.0)
    ga = RNG.uniform(0.01, 0.99) * be / (n - 1)
    al = RNG.uniform(1.0, 3.0)
    c = RNG.uniform(0.1, 0.5)
    a2 = be * ga / ((2 * be + ga) * (2 * be - (n - 1) * ga))
    a1 = (be + ga) / (2 * be + ga) - a2
    p0, q0, pr0 = bertrand_solve([c] * n, al, be, ga)
    mg = p0[0] - c
    d = RNG.uniform(0.0, 0.9) * mg / max((n - 1) * a2, 1e-12)
    d = min(d, 0.5 * c)
    for k in range(n):
        p, q, pr = bertrand_solve([c - d] * (k + 1) + [c] * (n - k - 1), al, be, ga)
        ok &= close(pr[0], be * (mg + a1 * d - a2 * k * d) ** 2, 1e-8)
        p, q, pr = bertrand_solve([c] + [c - d] * k + [c] * (n - k - 1), al, be, ga)
        ok &= close(pr[0], be * (mg - a2 * k * d) ** 2, 1e-8)
    # pass-throughs
    phi_ind = be / (2 * be - (n - 1) * ga)
    pc, _, _ = bertrand_solve([c - 1e-6] * n, al, be, ga)
    ok &= abs((p0[0] - pc[0]) / 1e-6 - phi_ind) < 1e-6 and close(phi_ind, 1 - a1 + (n - 1) * a2, 1e-12)
    po, _, _ = bertrand_solve([c - 1e-6] + [c] * (n - 1), al, be, ga)
    ok &= abs((p0[0] - po[0]) / 1e-6 - (1 - a1)) < 1e-6 and a1 > 0 and a2 > 0
    if mg > (n - 1) * a2 * d:
        ep = [be * (mg + a1 * d - a2 * k * d) ** 2 - be * (mg - a2 * k * d) ** 2 for k in range(n)]
        e0s = [be * (mg - a2 * k * d) ** 2 for k in range(n)]
        e1s = [be * (mg + a1 * d - a2 * k * d) ** 2 for k in range(n)]
        if d > 0:
            ok_cond &= all(x > 0 for x in ep) and all(np.diff(ep) < 0) and all(np.diff(e0s) < 0) and all(np.diff(e1s) < 0)
check("A2 lem:ext-game-pass(a): differentiated Bertrand fits the linear family with a2 = be ga/[(2be+ga)(2be-(n-1)ga)], "
      "a1 = (be+ga)/(2be+ga) - a2; phi_own = 1 - a1 and phi_ind = 1 - a1 + (n-1)a2 = be/(2be-(n-1)ga)", ok)
check("A3 lem:ext-game-pass(a): in the linear family the conditions of ass:ext-game (private gain positive and "
      "decreasing, E_1 and E_0 decreasing) hold when mg > (n-1) a2 delta_c", ok_cond)
be, ga, nB = 1.0, 0.2, 4
a2B = be * ga / ((2 * be + ga) * (2 * be - (nB - 1) * ga))
a1B = (be + ga) / (2 * be + ga) - a2B
phiB_own, phiB_ind = 1 - a1B, 1 - a1B + (nB - 1) * a2B
print(f"     -> Bertrand (be = 1, ga = 0.2, four firms): phi_own = {phiB_own:.3f}, phi_ind = {phiB_ind:.3f}")
quote(f"{phiB_own:.3f}")
quote(f"{phiB_ind:.3f}")

# A4 general Cournot, first order: pass-through, common gain and private gain for several demand curves
demands = {
    "linear": (lambda Q: 2.0 - 0.01 * Q, lambda Q: -0.01, lambda Q: 0.0),
    "ces0.8": (lambda Q: Q ** (-1 / 0.8), lambda Q: -(1 / 0.8) * Q ** (-1 / 0.8 - 1),
               lambda Q: (1 / 0.8) * (1 / 0.8 + 1) * Q ** (-1 / 0.8 - 2)),
    "ces2": (lambda Q: Q ** (-0.5), lambda Q: -0.5 * Q ** (-1.5), lambda Q: 0.75 * Q ** (-2.5)),
    "exp": (lambda Q: 3.0 * math.exp(-0.02 * Q), lambda Q: -0.06 * math.exp(-0.02 * Q),
            lambda Q: 0.0012 * math.exp(-0.02 * Q)),
    "log": (lambda Q: 3.0 - 0.5 * math.log(Q), lambda Q: -0.5 / Q, lambda Q: 0.5 / Q ** 2),
}
ok = True
for nm, (P, dP, d2P) in demands.items():
    for n in (2, 3, 4, 6):
        c = 0.6 if nm != "ces2" else 0.3
        p, q, pr = cournot_solve([c] * n, P, dP)
        Q = q.sum()
        Ecurv = -Q * d2P(Q) / dP(Q)
        if n + 1 - Ecurv <= 0:
            continue
        phi_ind = n / (n + 1 - Ecurv)
        h = 1e-6
        pc, _, prc = cournot_solve([c - h] * n, P, dP)
        po, _, pro = cournot_solve([c - h] + [c] * (n - 1), P, dP)
        ok &= abs((p - pc) / h - phi_ind) < 1e-4 and abs((p - po) / h - phi_ind / n) < 1e-4
        geq = (prc[0] - pr[0]) / h / q[0]
        gpr = (pro[0] - pr[0]) / h / q[0]
        ok &= abs(geq - (1 - phi_ind * (1 - 1 / n))) < 1e-4
        ok &= abs(gpr - ((2 * n - 1) / n - (n - 1) * phi_ind / n ** 2)) < 1e-4
        # Weyl-Fabinger: dPS/dc = -Q [1 - (1 - theta) rho], theta = 1/n
        ok &= abs((pr.sum() - prc.sum()) / h - (-Q * (1 - (1 - 1 / n) * phi_ind))) < 1e-3 * (1 + Q)
check("A4 lem:ext-game-pass(b): for linear, constant-elasticity, exponential and logarithmic demand, phi_ind = "
      "n/(n+1+QP''/P'), phi_own = phi_ind/n, common gain = Y d [1 - phi_ind(1-1/n)] and private gain = "
      "Y d [(2n-1)/n - (n-1)phi_ind/n^2] to first order (finite differences); industry version is Weyl-Fabinger's "
      "dPS/dc = -Q[1 - (1-1/n) rho]", ok)

# A5 symbolic: the first-order formulas from the implicit-function derivation
n_, Ec, phi_s = sp.symbols("n E phi", positive=True)
phi_expr = n_ / (n_ + 1 - Ec)
priv_raw = -(phi_expr / n_ - 1) + phi_expr * (n_ - (n_ - 1) * Ec / n_) / n_          # from the proof
common_raw = 1 - phi_expr + phi_expr / n_
ok = sp.simplify(priv_raw - ((2 * n_ - 1) / n_ - (n_ - 1) * phi_expr / n_ ** 2)) == 0
ok &= sp.simplify(common_raw - (1 - phi_expr * (1 - 1 / n_))) == 0
ok &= sp.simplify((1 - phi_expr * (1 - 1 / n_)) - (2 - Ec) / (n_ + 1 - Ec)) == 0
# window width (private minus common) is positive
ok &= sp.simplify(((2 * n_ - 1) / n_ - (n_ - 1) * phi_s / n_ ** 2) - (1 - phi_s * (1 - 1 / n_))
                  - (n_ - 1) / n_ * (1 + phi_s * (1 - 1 / n_))) == 0
check("A5 lem:ext-game-pass(b), proof: symbolic simplification of the implicit-function derivation; common share "
      "= (2-E)/(n+1-E) with E = -QP''/P'; private minus common = (n-1)/n [1 + phi_ind(1-1/n)] > 0", ok)

# A6 constant elasticity
ok = True
eps_s, c_s, d_s = sp.symbols("epsilon c delta", positive=True)
Pces = n_ * eps_s * c_s / (n_ * eps_s - 1)
ok &= sp.simplify(sp.diff(Pces, c_s) * c_s / Pces - 1) == 0                       # phi = 1
ok &= sp.simplify((Pces - c_s) / Pces - 1 / (n_ * eps_s)) == 0                    # Lerner 1/(n eps)
ok &= sp.simplify(n_ / (n_ + 1 - (1 + 1 / eps_s)) - n_ * eps_s / (n_ * eps_s - 1)) == 0
# private gain positive to first order iff eps > (2n-1)/(2n^2-2n+1)
gpr_ces = (2 * n_ - 1) / n_ - (n_ - 1) * (n_ * eps_s / (n_ * eps_s - 1)) / n_ ** 2
num = sp.factor(sp.together(gpr_ces))
ok &= sp.simplify(sp.numer(sp.together(gpr_ces)) - (eps_s * (2 * n_ ** 2 - 2 * n_ + 1) - (2 * n_ - 1))) == 0
for n in (2, 3, 4, 6, 10):
    for eps in np.linspace(1 / n + 0.01, 3.0, 40):
        cs = 0.7
        Pf = lambda Q, e=eps: Q ** (-1 / e)
        dPf = lambda Q, e=eps: -(1 / e) * Q ** (-1 / e - 1)
        p, q, pr = cournot_solve([cs] * n, Pf, dPf)
        ok &= close(p, n * eps * cs / (n * eps - 1), 1e-7)
        p2, q2, pr2 = cournot_solve([cs - 0.07] * n, Pf, dPf)
        ok &= close(pr2[0] / pr[0], ((cs - 0.07) / cs) ** (1 - eps), 1e-7)
        ok &= close((p2 * q2[0]) / (p * q[0]), ((cs - 0.07) / cs) ** (1 - eps), 1e-7)
        ok &= (pr2[0] < pr[0]) == (eps < 1)
check("A6 lem:ext-game-pass(c): constant elasticity: P = n eps c/(n eps - 1), phi = 1, Lerner 1/(n eps), "
      "phi_ind = n eps/(n eps - 1); earnings and revenue scale with c^(1-eps), so E_eq has the sign of eps - 1; "
      "first-order private gain positive iff eps > (2n-1)/(2n^2-2n+1)", ok)
thr = {n: (2 * n - 1) / (2 * n * n - 2 * n + 1) for n in (2, 4)}
print(f"     -> private-gain thresholds: {thr[2]:.2f} (two firms), {thr[4]:.2f} (four firms)")
quote(f"{thr[2]:.1f}")
quote(f"{thr[4]:.2f}")

# A7 running examples for the lemma
phiC_own, phiC_ind = 1 / 5, 4 / 5
phiC = phiC_ind * C0 / P0
print(f"     -> Cournot, four firms: phi_own = {phiC_own:.2f}, phi_ind = {phiC_ind:.2f}, phi = {phiC:.2f}")
quote("0.64")
n, eps = 4, 0.8
c_ces = P0 * (n * eps - 1) / (n * eps)
phi_ind_ces = n * eps / (n * eps - 1)
Eeq_rel_ces = ((c_ces - DC) / c_ces) ** (1 - eps) - 1
dp_ces = DC / c_ces
print(f"     -> CES, four firms, eps = 0.8: unit cost {c_ces:.4f}, Lerner {1 / (n * eps):.4f}, phi_ind = {phi_ind_ces:.3f} "
      f"> 4/3, price falls {100 * dp_ces:.1f}%, E_eq = {100 * Eeq_rel_ces:.1f}% of earnings")
ok = close(c_ces, 0.6875) and phi_ind_ces > 4 / 3 and abs(Eeq_rel_ces + 0.0309) < 5e-4 and abs(dp_ces - 0.1455) < 5e-4
# discrete check that adoption is still privately profitable and conditions of ass:ext-game hold in the example


def ces_profit(costs, eps_):
    cs = np.asarray(costs, float)
    m = len(cs)
    Pp = eps_ * cs.sum() / (m * eps_ - 1)
    sh = eps_ * (1 - cs / Pp)
    Q = Pp ** (-eps_)
    return (Pp - cs) * sh * Q


E1c = lambda k: ces_profit([c_ces - DC] * (k + 1) + [c_ces] * (n - k - 1), eps)[0]
E0c = lambda k: ces_profit([c_ces] + [c_ces - DC] * k + [c_ces] * (n - k - 1), eps)[0]
epc = [E1c(k) - E0c(k) for k in range(n)]
ok &= all(x > 0 for x in epc) and all(np.diff(epc) < 0) and all(np.diff([E1c(k) for k in range(n)]) < 0) \
    and all(np.diff([E0c(k) for k in range(n)]) < 0) and close((E1c(n - 1) - E0c(0)) / E0c(0), Eeq_rel_ces, 1e-9)
check("A7 lem:ext-game-pass examples: Cournot phi = 0.64; CES (eps = 0.8, four firms): phi_ind = 1.455 > 4/3, price "
      "-14.5%, E_eq = -3.1% of earnings, and the discrete private gains are positive and decreasing", ok)
quote("1.455")
quote("14.5")
quote("3.1")

# ==============================================================================================
header("B. prop:ext-game-preempt: diffusion under precommitment, preemption in the duopoly")
# ==============================================================================================


def open_loop_payoff(T, others, E1, E0, tm=TM):
    """Present value of a firm adopting at T when rivals adopt at the dates in `others`."""
    pts = sorted(set([0.0, T] + [o for o in others if o < 1e6]))
    val = 0.0
    for a, b in zip(pts, pts[1:] + [math.inf]):
        mid = a + 1e-12 if b == math.inf else 0.5 * (a + b)
        k = sum(1 for o in others if o <= mid)
        val += (E1(k) if mid >= T else E0(k)) * tm.I(a, b)
    return val - tm.cost(T)


ok = True
for trial in range(40):
    n = int(RNG.integers(2, 7))
    mg = RNG.uniform(0.1, 0.3)
    d = RNG.uniform(0.2, 0.9) * mg * (n + 1) / (n - 1)
    E1, E0 = lin_cournot(n, mg, d, BB)
    tm = Timing(r=RNG.uniform(0.06, 0.15), G=RNG.uniform(-0.02, 0.05), dF=RNG.uniform(0.03, 0.4),
                F0_=RNG.uniform(5, 60))
    dates = [tm.To(E1(k) - E0(k)) for k in range(n)]
    ok &= all(dates[i] <= dates[i + 1] + 1e-12 for i in range(n - 1))
    grid = np.concatenate([np.linspace(0, max(dates) + 6, 1500), dates])
    for i in range(n):
        others = dates[:i] + dates[i + 1:]
        eq = open_loop_payoff(dates[i], others, E1, E0, tm)
        best = max(open_loop_payoff(T, others, E1, E0, tm) for T in grid)
        ok &= best <= eq + 1e-7 * (1 + abs(eq))
check("B1 prop:ext-game-preempt(a): T_k = T°(E_priv(k-1)) is nondecreasing and each firm's date is a best response to "
      "the others' (grid search over deviations, 40 random markets with n = 2..6, G of either sign)", ok)

E1, E0 = lin_cournot(4)
dates4 = [TM.To(E1(k) - E0(k)) for k in range(4)]
solo = TM.To(DC * Y0)
joint4 = TM.To(E1(3) - E0(0))
print("     -> four-firm open-loop dates " + ", ".join(f"{x:.2f}" for x in dates4)
      + f"; single-firm date {solo:.2f}; date at which the durable gain covers the user cost {joint4:.2f}")
ok = np.allclose(dates4, [2.159, 2.415, 2.695, 3.005], atol=2e-3) and abs(solo - 4.08) < 5e-3 and abs(joint4 - 6.63) < 5e-3
ok &= all(E1(k) - E0(k) > DC * Y0 for k in range(4))
check("B2 prop:ext-game-preempt(a) example: dates 2.16, 2.41, 2.69, 3.00 years, all before the single-firm date 4.08 "
      "because E_priv(k) > delta_c Y (business stealing)", ok)
for x in dates4:
    quote(f"{x:.2f}")
quote("4.08")
quote("6.63")


class Duopoly:
    def __init__(self, E1, E0, tm=TM):
        self.e0, self.eL, self.eF, self.eB = E0(0), E1(0), E0(1), E1(1)
        self.tm = tm
        self.T2 = tm.To(self.eB - self.eF)
        self.T1 = tm.To(self.eL - self.e0)
        self.TD = tm.To(self.eL - self.eF)
        self.TJ = tm.To(self.eB - self.e0)
        self.sq = self.e0 / (tm.r - tm.G)

    def VJ(self, t):
        tm = self.tm
        if t == math.inf:
            return self.sq
        return self.e0 * tm.I(0, t) + self.eB * tm.I(t, math.inf) - tm.cost(t)

    def VL(self, t):
        tm = self.tm
        if t >= self.T2:
            return self.VJ(t)
        return self.e0 * tm.I(0, t) + self.eL * tm.I(t, self.T2) + self.eB * tm.I(self.T2, math.inf) - tm.cost(t)

    def VF(self, t):
        tm = self.tm
        if t >= self.T2:
            return self.VJ(t)
        return self.e0 * tm.I(0, t) + self.eF * tm.I(t, self.T2) + self.eB * tm.I(self.T2, math.inf) - tm.cost(self.T2)

    def TP(self):
        d = lambda t: self.VL(t) - self.VF(t)
        if d(0) >= 0:
            return 0.0
        return optimize.brentq(d, 0, self.TD, xtol=1e-13)


# B3 closed forms against quadrature
D2 = Duopoly(*lin_cournot(2))


def quad_flow(segs):
    tot = 0.0
    for a, b, e in segs:
        f = lambda s: e * math.exp(-(TM.r - TM.G) * s)
        tot += integrate.quad(f, a, b, limit=200)[0] if b != math.inf else integrate.quad(f, a, np.inf)[0]
    return tot


ok = True
for t in (0.0, 0.5, 1.3, 2.9):
    vl = quad_flow([(0, t, D2.e0), (t, D2.T2, D2.eL), (D2.T2, math.inf, D2.eB)]) - TM.cost(t)
    vf = quad_flow([(0, t, D2.e0), (t, D2.T2, D2.eF), (D2.T2, math.inf, D2.eB)]) - TM.cost(D2.T2)
    vj = quad_flow([(0, t, D2.e0), (t, math.inf, D2.eB)]) - TM.cost(t)
    ok &= close(vl, D2.VL(t), 1e-8) and close(vf, D2.VF(t), 1e-8) and close(vj, D2.VJ(t), 1e-8)
ok &= close(D2.VL(D2.T2), D2.VJ(D2.T2)) and close(D2.VF(D2.T2), D2.VJ(D2.T2))
check("B3 eq:ext-game-values: closed forms of V^L, V^F, V^J agree with quadrature; V^L = V^F = V^J at T_2", ok)

# B4 shape of V^L - V^F and the ordering, on random duopolies
ok = True
cnt = 0
for _ in range(300):
    mg = RNG.uniform(0.1, 0.3)
    d = RNG.uniform(0.05, 2.9) * mg
    tm = Timing(r=RNG.uniform(0.06, 0.15), G=RNG.uniform(-0.02, 0.05), dF=RNG.uniform(0.03, 0.5), F0_=RNG.uniform(10, 80))
    D = Duopoly(*lin_cournot(2, mg, d, BB), tm=tm)
    if not (D.T2 > 0) or D.VL(0) >= D.VF(0):
        continue
    cnt += 1
    ts1 = np.linspace(0, D.TD, 200)
    ts2 = np.linspace(D.TD, D.T2, 200)
    diff1 = np.diff([D.VL(t) - D.VF(t) for t in ts1])
    diff2 = np.diff([D.VL(t) - D.VF(t) for t in ts2])
    ok &= all(diff1 > -1e-10) and all(diff2 < 1e-10) and abs(D.VL(D.T2) - D.VF(D.T2)) < 1e-9
    TP = D.TP()
    ok &= 0 < TP < D.TD < D.T1 < D.T2
    ok &= all(np.diff([D.VL(t) for t in np.linspace(0, D.T1, 200)]) > -1e-10)
    # simultaneous adoption is worse than following before T_2 (used in the FT construction)
    ok &= all(D.VF(t) > D.VJ(t) for t in np.linspace(0, D.T2 * 0.999, 50))
    # the follower's value rises with the leader's date
    ok &= all(np.diff([D.VF(t) for t in np.linspace(0, D.T2, 100)]) > 0)
check(f"B4 prop:ext-game-preempt(b): V^L - V^F rises on [0, T_D], falls on [T_D, T_2], is zero at T_2; "
      f"0 < T^P < T_D < T_1 < T_2; V^L rises on [0, T_1]; V^F > V^J before T_2; V^F rises in the leader's date "
      f"({cnt} random duopolies with V^L(0) < V^F(0))", ok and cnt > 50)

TP2 = D2.TP()
print(f"     -> duopoly: T^P = {TP2:.2f}, T_D = {D2.TD:.2f}, T_1 = {D2.T1:.2f}, T_2 = {D2.T2:.2f}; rents "
      f"{D2.VL(TP2):.1f} each against {D2.VL(D2.T1):.1f} for an unchallenged leader; status quo {D2.sq:.1f} "
      f"(earnings 4.00, 7.11, 2.78, 5.44)")
ok = abs(TP2 - 0.63) < 5e-3 and abs(D2.TD - 1.80) < 5e-3 and abs(D2.T1 - 2.78) < 5e-3 and abs(D2.T2 - 3.23) < 5e-3
ok &= abs(D2.VL(TP2) - 78.2) < 0.05 and abs(D2.VL(D2.T1) - 81.1) < 0.05 and abs(D2.sq - 66.7) < 0.05
ok &= np.allclose([D2.e0, D2.eL, D2.eF, D2.eB], [4.0, 7.111, 2.778, 5.444], atol=1e-3)
check("B5 prop:ext-game-preempt(b) example: T^P = 0.63, T_D = 1.80, T_1 = 2.78, T_2 = 3.23 years; rents 78.2 each "
      "against 81.1 at T_1; status quo 66.7", ok)
for s in ("0.63", "1.80", "2.78", "3.23", "78.2", "81.1", "66.7", "7.11", "2.78", "5.44"):
    quote(s)


# B6 discrete-time check of FT's limit: backward induction with a symmetric stage equilibrium
def discrete_first_adoption(D, dt, Tmax=12.0):
    N = int(Tmax / dt)
    ts = np.arange(N + 1) * dt
    L = np.array([D.VL(t) for t in ts])
    F = np.array([D.VF(t) for t in ts])
    M = np.array([D.VJ(t) for t in ts])
    W = M[-1]                      # beyond Tmax both adopt at once (Tmax > T_J)
    p = np.zeros(N + 1)
    val = np.zeros(N + 1)
    for i in range(N, -1, -1):
        if W >= L[i]:              # (wait, wait) is an equilibrium of the stage game; select it
            p[i], v = 0.0, W
        elif M[i] >= F[i]:         # both adopt
            p[i], v = 1.0, M[i]
        else:                      # symmetric mixed equilibrium: p M + (1-p) L = p F + (1-p) W
            p[i] = (L[i] - W) / (L[i] - W + F[i] - M[i])
            v = p[i] * F[i] + (1 - p[i]) * W
        val[i] = v
        W = v
    surv = np.cumprod(np.concatenate([[1.0], (1 - p) ** 2]))[:-1]
    prob_first = surv * (1 - (1 - p) ** 2)
    return float((prob_first * ts).sum() / prob_first.sum()), val[0]


# with the joint-waiting equilibrium selected when it exists, use a market where it does not: a large cut
Dbig = Duopoly(*lin_cournot(2, 0.2, 0.31, BB), tm=Timing(F0_=80.0))
TPbig = Dbig.TP()
exists_joint = Dbig.VJ(Dbig.TJ) >= Dbig.VL(Dbig.T1)
res = [discrete_first_adoption(Dbig, dt) for dt in (0.004, 0.001)]
ok = (not exists_joint) and TPbig > 0 and abs(res[1][0] - TPbig) < abs(res[0][0] - TPbig) and abs(res[1][0] - TPbig) < 0.06
ok &= abs(res[1][1] - Dbig.VF(TPbig)) < 0.02 * abs(Dbig.VF(TPbig))
print(f"     -> discrete-time check (cut 0.31, F0 = 80): T^P = {TPbig:.3f}; mean first adoption {res[0][0]:.3f} (dt = 0.004), "
      f"{res[1][0]:.3f} (dt = 0.001); value {res[1][1]:.2f} against V^F(T^P) = {Dbig.VF(TPbig):.2f}")
check("B6 prop:ext-game-preempt(b): in discrete time with symmetric stage equilibria, the first adoption converges to "
      "T^P and each firm's value to V^F(T^P) = V^L(T^P) as the period shrinks (Fudenberg-Tirole limit)", ok)

# ==============================================================================================
header("C. prop:ext-game-wait: late joint adoption, learning and the war of attrition")
# ==============================================================================================
# C1 joint adoption: brute-force deviation check and the integral condition
ok = True
cnt_yes = cnt_no = 0
for _ in range(300):
    mg = RNG.uniform(0.1, 0.3)
    d = RNG.uniform(0.02, 2.9) * mg
    tm = Timing(r=RNG.uniform(0.06, 0.15), G=RNG.uniform(-0.02, 0.05), dF=RNG.uniform(0.03, 0.5), F0_=RNG.uniform(10, 80))
    D = Duopoly(*lin_cournot(2, mg, d, BB), tm=tm)
    if not D.T2 > 0 or D.TJ == math.inf:
        continue
    lhs = integrate.quad(lambda t: math.exp(-tm.r * t) * ((tm.r + tm.dF) * tm.FA(t) - (D.eB - D.e0) * math.exp(tm.G * t)),
                         D.T2, D.TJ, limit=200)[0]
    rhs = integrate.quad(lambda t: math.exp(-tm.r * t) * ((D.eL - D.e0) * math.exp(tm.G * t) - (tm.r + tm.dF) * tm.FA(t)),
                         D.T1, D.T2, limit=200)[0]
    exists = D.VJ(D.TJ) >= D.VL(D.T1)
    ok &= (lhs >= rhs) == exists
    ok &= close(lhs - rhs, D.VJ(D.TJ) - D.VL(D.T1), 1e-7)
    # brute force: for T in [T_2, T_J], best deviation payoff vs V^J(T)
    for T in np.linspace(D.T2, D.TJ, 7):
        devs = [D.VL(t) for t in np.append(np.linspace(0, D.T2, 400), D.T1)] + [D.VJ(t) for t in np.linspace(D.T2, T, 50)]
        ok &= (max(devs) <= D.VJ(T) + 1e-9) == (D.VJ(T) >= D.VL(D.T1) - 1e-9)
    # joint adoption before T_2 is never an equilibrium (waiting to follow pays more)
    ok &= all(D.VF(t) > D.VJ(t) for t in np.linspace(0, 0.999 * D.T2, 20))
    cnt_yes += exists
    cnt_no += not exists
check(f"C1 prop:ext-game-wait(a): joint adoption at T in [T_2, T_J] is an equilibrium iff V^J(T) >= V^L(T_1); existence "
      f"iff eq:ext-game-joint; no joint date before T_2 ({cnt_yes} markets with, {cnt_no} without)",
      ok and cnt_yes > 10 and cnt_no > 10)

Tlo = optimize.brentq(lambda T: D2.VJ(T) - D2.VL(D2.T1), D2.T2, D2.TJ)
print(f"     -> duopoly: joint adoption is an equilibrium at any date in [{Tlo:.2f}, {D2.TJ:.2f}], worth up to "
      f"{D2.VJ(D2.TJ):.1f} each, against {D2.VL(TP2):.1f} under preemption")
ok = abs(Tlo - 3.32) < 5e-3 and abs(D2.TJ - 5.03) < 5e-3 and abs(D2.VJ(D2.TJ) - 81.8) < 0.05
gapf = lambda dd, F=F0: (lambda D: D.VJ(D.TJ) - D.VL(D.T1))(Duopoly(*lin_cournot(2, MG, dd, BB), tm=Timing(F0_=F)))
cuts_T2pos = [dd for dd in np.linspace(0.005, 0.595, 120) if Duopoly(*lin_cournot(2, MG, dd, BB)).T2 > 0]
ok &= all(gapf(dd) > 0 for dd in cuts_T2pos)
gap_big = gapf(0.31, 80.0)
ok &= gap_big < 0 and not exists_joint
print(f"     -> joint adoption equilibria exist in this market at every cut with T_2 > 0 (up to {max(cuts_T2pos):.2f}); "
      f"with a cut of 0.31 and F0 = 80 they do not (V^J(T_J) - V^L(T_1) = {gap_big:.2f}) and preemption at "
      f"{TPbig:.2f} years is the outcome")
check("C2 prop:ext-game-wait(a) example: joint-adoption dates [3.32, 5.03], worth up to 81.8 each; joint adoption "
      "equilibria exist at every cut with T_2 > 0 in this market, but not with a cut of 0.31 and F0 = 80, where "
      "preemption at 0.66 years is the outcome", ok)
quote(f"{TPbig:.2f}")
for s in ("3.32", "5.03", "81.8"):
    quote(s)

# C3 never adopting when E_eq <= 0 (constant-elasticity duopoly, eps < 1)
ok = True
for eps in (0.6, 0.7, 0.8, 0.9):
    c2 = P0 * (2 * eps - 1) / (2 * eps)
    sc = 20.0 / ces_profit([c2, c2], eps)[0]          # scale so that baseline earnings are 20 * Lerner * revenue units
    E1x = lambda k, e=eps, c=c2, s=sc: s * ces_profit([c - 0.05 * c] * (k + 1) + [c] * (1 - k), e)[0]
    E0x = lambda k, e=eps, c=c2, s=sc: s * ces_profit([c] + [c - 0.05 * c] * k + [c] * (1 - k), e)[0]
    if not (E1x(0) - E0x(0) > E1x(1) - E0x(1) > 0):
        continue
    D = Duopoly(E1x, E0x, tm=Timing(F0_=60.0))
    ok &= D.TJ == math.inf and D.eB - D.e0 < 0
    ok &= all(np.diff([D.VJ(t) for t in np.linspace(D.T2, 60, 50)]) > 0)
    never_eq = D.sq >= D.VL(D.T1)
    lhs = D.sq - D.VJ(D.T2)
    rhs = D.VL(D.T1) - D.VL(D.T2)
    ok &= (lhs >= rhs) == never_eq
check("C3 prop:ext-game-wait(a): if E_eq <= 0 (constant elasticity, eps < 1) V^J rises for ever and never adopting is "
      "an equilibrium iff E_0(0)/(r-G) >= V^L(T_1), the case T_J = infinity of eq:ext-game-joint", ok)


# C4 learning model
def VLw(D, t, w):
    tm = D.tm
    return w * D.VL(t) + (1 - w) * (D.sq - tm.cost(t))


def VFw(D, t, w):
    return w * D.VF(t) + (1 - w) * D.sq


def max_gap(D, w):
    """max over t of V^L_w - V^F_w: on t >= T_2 it is negative; on [0, T_2] the peak is at T°(w a_LF) or an end."""
    aLF = D.eL - D.eF
    cands = [0.0, D.T2]
    tpk = D.tm.To(w * aLF)
    if 0 < tpk < D.T2:
        cands.append(tpk)
    return max(VLw(D, t, w) - VFw(D, t, w) for t in cands)


ok = True
for _ in range(300):
    mg = RNG.uniform(0.1, 0.3)
    d = RNG.uniform(0.05, 2.9) * mg
    tm = Timing(r=RNG.uniform(0.06, 0.15), G=RNG.uniform(-0.02, 0.05), dF=RNG.uniform(0.03, 0.5), F0_=RNG.uniform(10, 80))
    D = Duopoly(*lin_cournot(2, mg, d, BB), tm=tm)
    wbar = (D.eB - D.eF) / (D.eL - D.eF)
    ok &= 0 < wbar < 1
    for w in RNG.uniform(0.01, wbar, 3):
        ts = np.concatenate([np.linspace(0, max(D.T2, 0.1) * 3 + 5, 400)])
        ok &= all(VFw(D, t, w) > VLw(D, t, w) for t in ts)
        ok &= max_gap(D, w) < 0
check("C4 prop:ext-game-wait(b): with varpi <= varpi_bar = E_priv(1)/[E_1(0) - E_0(1)] the follower's value exceeds the "
      "leader's at every date (300 random duopolies)", ok)

wbar2 = (D2.eB - D2.eF) / (D2.eL - D2.eF)
wstar = optimize.brentq(lambda w: max_gap(D2, w), wbar2, 0.999)
print(f"     -> duopoly: varpi_bar = {wbar2:.3f}; a preemption region reappears only above varpi = {wstar:.3f}")
ok = abs(wbar2 - 0.615) < 5e-4 and wstar > wbar2 and abs(wstar - 0.893) < 2e-3
ok &= max_gap(D2, wstar + 0.01) > 0 and max_gap(D2, wstar - 0.01) < 0
check("C5 prop:ext-game-wait(b) example: varpi_bar = 0.615 (sufficient); the exact threshold is 0.893", ok)
quote("0.615")
quote("0.893")


# C6 war of attrition: monotonicity, hazard, indifference
def hazard(D, w, t):
    tm = D.tm
    z = w * (D.eB - D.e0) * math.exp(tm.G * t) / ((tm.r + tm.dF) * tm.FA(t))
    return max(0.0, (tm.r + tm.dF) * (z - 1) / (1 - w))


ok = True
for trial in range(30):
    mg = RNG.uniform(0.1, 0.3)
    d = RNG.uniform(0.05, 2.0) * mg
    tm = Timing(r=RNG.uniform(0.06, 0.15), G=RNG.uniform(-0.01, 0.05), dF=RNG.uniform(0.05, 0.5), F0_=RNG.uniform(10, 80))
    D = Duopoly(*lin_cournot(2, mg, d, BB), tm=tm)
    wbar = (D.eB - D.eF) / (D.eL - D.eF)
    w = RNG.uniform(0.2, 0.95) * wbar
    TW = tm.To(w * (D.eB - D.e0))
    ok &= TW >= D.T2
    pre = np.linspace(0, TW, 300)
    post = np.linspace(TW, TW + 8, 300)
    ok &= all(np.diff([VLw(D, t, w) for t in pre]) > -1e-10) and all(np.diff([VLw(D, t, w) for t in post]) < 1e-10)
    # hazard equals -V^L'/(V^F - V^L) after T^W
    for t in TW + np.array([0.3, 1.0, 2.5]):
        h = 1e-6
        dVL = (VLw(D, t + h, w) - VLw(D, t - h, w)) / (2 * h)
        ok &= abs(hazard(D, w, t) - (-dVL) / (VFw(D, t, w) - VLw(D, t, w))) < 1e-4 * (1 + hazard(D, w, t))
    # indifference: expected value of planning to adopt at s >= T^W equals V^L(T^W)
    Hint = lambda s: integrate.quad(lambda u: hazard(D, w, u), TW, s, limit=200)[0]
    target = VLw(D, TW, w)
    for s in (TW + 0.5, TW + 1.5):
        dens = lambda u: hazard(D, w, u) * math.exp(-Hint(u))
        val = integrate.quad(lambda u: VFw(D, u, w) * dens(u), TW, s, limit=100)[0] + math.exp(-Hint(s)) * VLw(D, s, w)
        ok &= abs(val - target) < 1e-5 * abs(target)
    # adopting before T^W is worse; the leader's value beats the status quo
    ok &= all(VLw(D, t, w) <= target + 1e-12 for t in pre) and target > D.sq
check("C6 prop:ext-game-wait(c): V^L rises before T^W = T°(varpi E_eq) >= T_2 and falls after; the hazard "
      "eq:ext-game-hazard equals -V^L'/(V^F - V^L); a rival using it leaves a firm indifferent among all dates after "
      "T^W at V^L(T^W) > status quo (30 random duopolies)", ok)

w = 0.5
TW2 = TM.To(w * (D2.eB - D2.e0))
Hc = lambda s: (TM.r + TM.dF) / (1 - w) * ((math.exp((TM.G + TM.dF) * s) - 1) / (TM.G + TM.dF) - s)
ok = all(abs(Hc(s) - integrate.quad(lambda u: hazard(D2, w, u), TW2, TW2 + s)[0]) < 1e-8 for s in (0.5, 1.0, 2.0))
Edelay = integrate.quad(lambda s: math.exp(-2 * Hc(s)), 0, 60)[0]
med = optimize.brentq(lambda s: 2 * Hc(s) - math.log(2), 1e-9, 20)
print(f"     -> varpi = 0.5: T^W = {TW2:.2f} years; first adoption a mean {Edelay:.2f} and a median {med:.2f} years later; "
      f"value {VLw(D2, TW2, w):.1f} each against {VFw(D2, TW2, w):.1f} for the follower in the asymmetric equilibrium")
ok &= abs(TW2 - 7.07) < 5e-3 and abs(Edelay - 1.52) < 5e-3 and abs(med - 1.46) < 5e-3
ok &= abs(VLw(D2, TW2, w) - 73.4) < 0.05 and abs(VFw(D2, TW2, w) - 74.0) < 0.05
check("C7 prop:ext-game-wait(c) example: closed-form integrated hazard; T^W = 7.07, mean delay 1.52, median 1.46 "
      "years; value 73.4 each against 74.0 for an asymmetric follower", ok)
for s in ("7.07", "1.52", "1.46", "73.4", "74.0"):
    quote(s)

# ==============================================================================================
header("D. prop:ext-game-pd: the automation prisoner's dilemma")
# ==============================================================================================
ok = True
for _ in range(300):
    n = int(RNG.integers(2, 10))
    mg = RNG.uniform(0.1, 0.3)
    d = RNG.uniform(0.01, 0.99) * mg * (n + 1) / (n - 1)
    E1, E0 = lin_cournot(n, mg, d, BB)
    lo, hi = E1(n - 1) - E0(0), E1(n - 1) - E0(n - 1)
    ok &= close(hi - lo, E0(0) - E0(n - 1)) and hi > lo
    for K in np.linspace(0, 1.2 * (E1(0) - E0(0)), 25):
        dominant = all(E1(k) - K > E0(k) for k in range(n))
        no_better = E1(n - 1) - K <= E0(0)
        ok &= dominant == (K < hi) and no_better == (K >= lo)
check("D1 prop:ext-game-pd(a): adopting is strictly dominant iff K < E_priv(n-1); all no better off iff K >= E_eq; the "
      "window has width E_0(0) - E_0(n-1) > 0 (300 random markets, K on a grid)", ok)

# D2 first-order window and the durable share 1/n under linear demand
ok = True
for n in (2, 3, 4, 6, 10):
    for d in (1e-4, 1e-5):
        E1, E0 = lin_cournot(n, 0.2, d, BB)
        Yd = (0.2 / BB) * d
        ok &= abs((E1(n - 1) - E0(0)) / Yd - 2 / (n + 1)) < 1e-2 * 2 / (n + 1)
        ok &= abs((E1(n - 1) - E0(n - 1)) / Yd - 2 * n / (n + 1)) < 1e-2
        ok &= abs((E1(n - 1) - E0(0)) / (E1(n - 1) - E0(n - 1)) - 1 / n) < 1e-2 / n
E1, E0 = lin_cournot(4)
fo = (0.4 * DC * Y0, 1.6 * DC * Y0)
print(f"     -> four firms: exact window [{E1(3) - E0(0):.2f}, {E1(3) - E0(3):.2f}) $m a year; first order "
      f"[{fo[0]:.1f}, {fo[1]:.1f})")
ok &= close(E1(3) - E0(0), 0.84) and close(E1(3) - E0(3), 2.88)
check("D2 prop:ext-game-pd(a): to first order the window is [2/(n+1), 2n/(n+1)) Y delta_c under linear demand, so the "
      "durable share of the private gain is 1/n; example window [0.84, 2.88) against [0.8, 3.2) to first order", ok)
for s in ("0.84", "2.88", "0.8", "3.2"):
    quote(s)

# D3 pure dilemma equivalences
Esym = sp.symbols("E", real=True)
phi_E = n_ / (n_ + 1 - Esym)
ok = True
for nv in (2, 3, 5, 10):
    for Ev in np.linspace(-3, nv + 0.9, 60):
        pv = nv / (nv + 1 - Ev)
        ok &= (pv > nv / (nv - 1)) == (Ev > 2) and ((1 - pv * (1 - 1 / nv)) < 0) == (Ev > 2)
# constant elasticity: E = 1 + 1/eps, so E > 2 iff eps < 1; linear: E = 0
ok &= sp.simplify((1 + 1 / eps_s) - 2 - (1 - eps_s) / eps_s) == 0
check("D3 prop:ext-game-pd(b): phi_ind > n/(n-1) iff -QP''/P' > 2 (independent of n) iff the first-order common gain "
      "is negative; under constant elasticity iff eps < 1; never under linear demand", ok)


# D4 dynamic dilemma: the last adopter's exact gain relative to never adopting
def last_adopter_gain(E1, E0, n, tm):
    dates = [tm.To(E1(k) - E0(k)) for k in range(n)]
    return open_loop_payoff(dates[-1], dates[:-1], E1, E0, tm) - E0(0) / (tm.r - tm.G), dates


ok = True
for _ in range(200):
    n = int(RNG.integers(2, 12))
    mg = RNG.uniform(0.1, 0.3)
    d = RNG.uniform(0.05, 0.95) * mg * (n + 1) / (n - 1)
    tm = Timing(r=RNG.uniform(0.06, 0.15), G=RNG.uniform(-0.02, 0.05), dF=RNG.uniform(0.03, 0.5), F0_=RNG.uniform(5, 80))
    E1, E0 = lin_cournot(n, mg, d, BB)
    gain, dates = last_adopter_gain(E1, E0, n, tm)
    Tn = dates[-1]
    bound = math.exp(-(tm.r - tm.G) * Tn) * (E1(n - 1) - E0(0)) / (tm.r - tm.G) - tm.cost(Tn)
    ok &= gain <= bound + 1e-9
    cond = (E1(n - 1) - E0(0)) <= (tm.r - tm.G) * math.exp(-tm.G * Tn) * tm.FA(Tn)
    if Tn > 0:
        cond2 = (E1(n - 1) - E0(0)) <= (tm.r - tm.G) / (tm.r + tm.dF) * (E1(n - 1) - E0(n - 1))
        ok &= cond == cond2
    if cond:
        ok &= gain <= 1e-9
check("D4 prop:ext-game-pd(c): the last adopter's gain over never adopting is at most e^{-(r-G)T_n} E_eq/(r-G) - "
      "e^{-rT_n} F_A(T_n), so it is <= 0 when E_eq <= (r-G) e^{-G T_n} F_A(T_n), i.e. E_eq <= (r-G)/(r+dF) E_priv(n-1) "
      "for T_n > 0 (200 random markets)", ok)

# duopoly preemption payoff below the status quo under the same condition
ok = True
cnt = 0
for _ in range(6000):
    if cnt >= 40:
        break
    mg = RNG.uniform(0.1, 0.3)
    d = RNG.uniform(0.05, 2.9) * mg
    tm = Timing(r=RNG.uniform(0.06, 0.15), G=RNG.uniform(-0.02, 0.03), dF=RNG.uniform(0.03, 0.15), F0_=RNG.uniform(10, 300))
    D = Duopoly(*lin_cournot(2, mg, d, BB), tm=tm)
    if not D.T2 > 0 or D.VL(0) >= D.VF(0):
        continue
    if (D.eB - D.e0) <= (tm.r - tm.G) / (tm.r + tm.dF) * (D.eB - D.eF):
        cnt += 1
        ok &= D.VF(D.TP()) <= D.sq + 1e-9
check(f"D5 prop:ext-game-pd(c): in the duopoly, E_eq <= (r-G)/(r+dF) E_priv(1) leaves both firms no better off than "
      f"never adopting in the preemption equilibrium ({cnt} random duopolies satisfying the condition)", ok and cnt >= 40)

E1, E0 = lin_cournot(4)
ratio4 = (E1(3) - E0(0)) / (E1(3) - E0(3))
thr_rate = (R - GG) / (R + DF)
E1t, E0t = lin_cournot(10)
ratio10 = (E1t(9) - E0t(0)) / (E1t(9) - E0t(9))
g10, _ = last_adopter_gain(E1t, E0t, 10, TM)
tm0 = Timing(dF=0.0)
g4_0, d4_0 = last_adopter_gain(E1, E0, 4, tm0)
priv_pv = (E1(3) - E0(3)) / (R - GG)
print(f"     -> dynamic: (r-G)/(r+dF) = {thr_rate:.2f}; ratio {ratio4:.2f} with four firms (last adopter gains), "
      f"{ratio10:.3f} with ten (last adopter gains {g10:.2f}); first-order bound n >= {(R + DF) / (R - GG):.2f}; with a "
      f"constant adoption cost all four adopt at once (dates {d4_0}), each loses {-g4_0:.1f} though the private gain is "
      f"worth {priv_pv:.0f} against a cost of 20")
ok = abs(thr_rate - 0.15) < 1e-12 and abs(ratio4 - 0.29) < 5e-3 and abs(ratio10 - 0.125) < 5e-4 and g10 < 0
ok &= all(x == 0 for x in d4_0) and abs(g4_0 + 6.0) < 1e-6 and abs(priv_pv - 48) < 1e-6
check("D6 prop:ext-game-pd(c) example: threshold 0.15; four firms 0.29 (no dilemma), ten firms 0.125 (dilemma); with "
      "a constant cost all adopt at once and each loses 6.0 although the private gain is worth 48", ok)
ok_g10 = abs(g10 + 2.73) < 5e-3
check("D6b prop:ext-game-pd(c) example: with ten firms the last adopter loses 2.73", ok_g10)
for s in ("0.15", "0.29", "0.125", "6.0", "48", "6.67", "2.73"):
    quote(s)

# D7 Rule of X: exact margin identity and first-order terms
ok = True
for _ in range(200):
    n = int(RNG.integers(2, 8))
    A_ = RNG.uniform(1.2, 3.0)
    B_ = RNG.uniform(0.005, 0.05)
    c = RNG.uniform(0.3, 0.7) * A_
    d = RNG.uniform(0.0, 0.3) * (A_ - c) / (n + 1)
    K = RNG.uniform(0, 1) * ((A_ - c) / (n + 1)) ** 2 / B_
    Pf = lambda Q: A_ - B_ * Q
    p0, q0, pr0 = cournot_solve([c] * n, Pf, lambda Q: -B_)
    p1, q1, pr1 = cournot_solve([c - d] * n, Pf, lambda Q: -B_)
    S0, S1 = p0 * q0[0], p1 * q1[0]
    m0, m1 = pr0[0] / S0, (pr1[0] - K) / S1
    ok &= close(m1 - m0, (pr1[0] - pr0[0] - K - m0 * (S1 - S0)) / S1, 1e-9)
for n in (2, 4, 6):
    for nm in ("linear", "exp", "log", "ces2"):
        P, dP, d2P = demands[nm]
        c = 0.6 if nm != "ces2" else 0.3
        h = 1e-6
        p, q, pr = cournot_solve([c] * n, P, dP)
        p2, q2, pr2 = cournot_solve([c - h] * n, P, dP)
        Q = q.sum()
        eps_loc = -p / (Q * dP(Q))
        phi_loc = (p - p2) / h * c / p
        S, S2 = p * q[0], p2 * q2[0]
        ok &= abs((S2 / S - 1) / h - (-(1 - eps_loc) * phi_loc / c)) < 1e-3
        ok &= abs(((pr2[0] / S2) - (pr[0] / S)) / h - (1 - phi_loc) / p) < 1e-3
check("D7 prop:ext-game-pd(d): exact identity m_1 - m_0 = [E_eq - K - m_0 (S_1 - S_0)]/S_1; first order, revenue "
      "changes by -(1-eps) phi delta_c/c and the margin before K by (1-phi) delta_c/P", ok)

# example numbers: linear four firms and CES four firms
E1, E0 = lin_cournot(4)
P1 = P0 - 4 * DC / 5
Y1 = (MG + DC / 5) / BB
S0, S1 = P0 * Y0, P1 * Y1
m1_noK = (P1 - (C0 - DC)) / P1
m1_K = (E1(3) - 0.84) / S1
n_ces, eps_ces = 4, 0.8
lerner_ces = 1 / (n_ces * eps_ces)
g_loss = (1 - eps_ces) * 0.05
print(f"     -> Rule of X, linear four firms: revenue {100 * (S1 / S0 - 1):+.1f}%, margin before K from 20.0% to "
      f"{100 * m1_noK:.1f}%, at K = E_eq {100 * m1_K:.1f}%; CES: revenue {100 * Eeq_rel_ces:.1f}%, margin "
      f"{100 * lerner_ces:.2f}% unchanged before K; a 5% a year decline lowers nominal growth by {100 * g_loss:.0f} point")
ok = abs(S1 / S0 - 1 - 0.012) < 1e-9 and abs(m1_noK - 0.2391) < 1e-4 and abs(m1_K - 0.1976) < 1e-4
ok &= abs(g_loss - 0.01) < 1e-12 and abs(lerner_ces - 0.3125) < 1e-12
check("D8 prop:ext-game-pd(d) example: linear revenue +1.2%, margin 20.0% -> 23.9% before K and 19.8% at K = E_eq; "
      "CES revenue -3.1% with the margin of 31.25% unchanged; a 5% annual cost decline costs 1 point of growth", ok)
for s in ("1.2", "23.9", "19.8", "31.25"):
    quote(s)

# ==============================================================================================
header("E. prop:ext-game-entry: AI-native entry and defensive automation")
# ==============================================================================================
cEinf, aE, bE, psw = 0.70, 0.50, 0.40, 0.05
cE = lambda t: cEinf + aE * math.exp(-bE * t)
PE = lambda t: cE(t) + psw
PEinf = cEinf + psw
n = 4
Pk = [P0 - k * DC / (n + 1) for k in range(n + 1)]
TMk = [math.log(aE / (Pk[k] - PEinf)) / bE if Pk[k] > PEinf else math.inf for k in range(n + 1)]
ok = all(TMk[i] <= TMk[i + 1] for i in range(n))
# T_M(k) is the first date with P_E(t) < P_k
for k in range(n + 1):
    ts = np.linspace(0, 10, 100001)
    first = next(t for t in ts if PE(t) < Pk[k])
    ok &= abs(first - TMk[k]) < 2e-4
TbarM = TMk[n]
Tviab = math.log(aE / (C0 - PEinf)) / bE
Tsolo = TM.To(DC * Y0)
print("     -> entry: T_M(k) = " + ", ".join(f"{x:.2f}" for x in TMk) + f"; entry binds whatever incumbents do from "
      f"{TbarM:.2f}; non-adopters lose money from {Tviab:.2f}; post-entry single-firm date {Tsolo:.2f}")
ok &= np.allclose(TMk, [1.733, 1.941, 2.169, 2.419, 2.697], atol=1e-3) and abs(Tviab - 5.76) < 5e-3
check("E1 prop:ext-game-entry(a),(b) example: the breakpoint T_M(k) rises with the number of adopters k (1.73, 1.94, "
      "2.17, 2.42, 2.70 years); entry binds whatever incumbents do from 2.70; non-adopters lose money from 5.76", ok)
for s in ("1.73", "1.94", "2.17", "2.42", "2.70", "5.76"):
    quote(s)

# E2 after the breakpoint the gain is delta_c Y whatever the rivals do; the single-firm rule then applies
ok = True
for k in range(n):
    gain_adopt = (PEinf - (C0 - DC)) * Y0 - (PEinf - C0) * Y0
    ok &= close(gain_adopt, DC * Y0)
ok &= abs(Tsolo - 4.08) < 5e-3
# post-entry single-agent problem: value of adopting at T >= t0 is maximized at max(t0, T°)
for t0 in (2.7, 3.5, 5.0):
    f = lambda T: -(DC * Y0 * TM.I(T, math.inf) - TM.cost(T))
    grid = np.linspace(t0, t0 + 10, 4001)
    best = grid[int(np.argmin([f(T) for T in grid]))]
    ok &= abs(best - max(t0, Tsolo)) < 5e-3
check("E2 prop:ext-game-entry(a): once entry binds, an incumbent's gain from adopting is delta_c Y = 2.0 whatever its "
      "rivals do, and a firm not yet adopted at t adopts at max{t, T°(delta_c Y)} (T° = 4.08)", ok)
quote("2.0")

# E3 deterrence: entry never binds iff the j-th adoption happens by T_M(j-1) for j <= kbar
ok = True
for _ in range(300):
    cEinf_ = RNG.uniform(0.80, 0.97)
    aE_ = RNG.uniform(0.2, 0.8)
    bE_ = RNG.uniform(0.2, 0.8)
    psw_ = RNG.uniform(0.0, 0.05)
    PE_ = lambda t: cEinf_ + psw_ + aE_ * math.exp(-bE_ * t)
    PEi = cEinf_ + psw_
    if not (Pk[n] <= PEi < P0):
        continue
    kbar = min(k for k in range(n + 1) if Pk[k] <= PEi)
    TMj = [math.log(aE_ / (Pk[j] - PEi)) / bE_ if Pk[j] > PEi else math.inf for j in range(n + 1)]
    sched = np.sort(RNG.uniform(0, 6, n))
    ts = np.linspace(0, 40, 8001)
    binds = any(Pk[int((sched <= t).sum())] > PE_(t) + 1e-12 for t in ts)
    crit = all(sched[j - 1] <= TMj[j - 1] for j in range(1, kbar + 1))
    ok &= binds == (not crit)
check("E3 prop:ext-game-entry(b): entry never binds iff the j-th adoption takes place by T_M(j-1) for every j <= kbar "
      "(random entrant paths and adoption schedules)", ok)

# E4 defensive window and regimes
ok = True
low = (PEinf - P0 + DC) * Y0
high = DC * Y0
ok &= close(low, -3.0) and close(high, 2.0) and PEinf <= P0 - DC
ok &= (PEinf < C0) and (PEinf >= C0 - DC)          # needed for viability, and sufficient
for K in np.linspace(0, 2.5, 26):
    adopt_beats = (PEinf - C0 + DC) * Y0 - K > (PEinf - C0) * Y0
    better_than_before = (PEinf - C0 + DC) * Y0 - K > MG * Y0
    defensive = adopt_beats and not better_than_before
    ok &= defensive == (low <= K < high)
lr_margin = PEinf - (C0 - DC)
print(f"     -> long run: incumbent's unit margin {lr_margin:.2f} with automation (0.20 before AI, {PEinf - C0:.2f} "
      f"without); defensive window [{low:.1f}, {high:.1f})")
ok &= abs(lr_margin - 0.05) < 1e-12
check("E4 prop:ext-game-entry(c) example: P_E = 0.75 <= P_0 - delta_c = 0.90, so every adoption worth making is "
      "defensive (window [-3.0, 2.0)); long-run margin 0.05 against 0.20 before AI and -0.05 without automation", ok)
for s in ("0.75", "0.05", "-3.0"):
    quote(s)

# E5 free replication limit
ok = True
for _ in range(100):
    c0 = RNG.uniform(0.5, 0.9)
    d = RNG.uniform(0.01, 0.2)
    ps = RNG.uniform(0, 0.1)
    cEi = (c0 - d) - RNG.uniform(0, 0.1)
    ok &= (cEi + ps) - (c0 - d) <= ps + 1e-12
check("E5 prop:ext-game-entry(d): with entrants at least as efficient as the automated incumbent, the long-run margin "
      "is at most the switching premium", ok)

# ==============================================================================================
header("F. cor:ext-game-engine: durable gain, concentration and should versus could")
# ==============================================================================================
Hs = sp.symbols("H", positive=True)
ok = True
dur_lin = 1 - (1 / (1 + Hs)) * (1 - Hs)
ok &= sp.simplify(dur_lin - 2 * Hs / (1 + Hs)) == 0
dur_ces = 1 - (eps_s / (eps_s - Hs)) * (1 - Hs)
ok &= sp.simplify(dur_ces - Hs * (eps_s - 1) / (eps_s - Hs)) == 0
priv_H = 2 - Hs - Hs * (1 - Hs) * phi_s
ok &= sp.simplify(((2 * n_ - 1) / n_ - (n_ - 1) * phi_s / n_ ** 2).subs(n_, 1 / Hs) - priv_H) == 0
ok &= sp.simplify(priv_H.subs(phi_s, 1 / (1 + Hs)) - 2 / (1 + Hs)) == 0
# monotonicity in H: d dur/dH > 0 iff E < 2 (constant curvature)
dur_E = (2 - Esym) / (1 / Hs + 1 - Esym)
ok &= sp.simplify(sp.diff(dur_E, Hs) - (2 - Esym) / (Hs ** 2 * (1 / Hs + 1 - Esym) ** 2)) == 0
ok &= sp.simplify(dur_E.subs(Hs, 1) - 1) == 0
check("F1 cor:ext-game-engine(a): dur = 1 - phi_ind(1-H) = (2-E)/(1/H+1-E): 2H/(1+H) under linear demand, "
      "H(eps-1)/(eps-H) under constant elasticity; priv = 2 - H - H(1-H) phi_ind (2/(1+H) linear); dur = 1 at H = 1 "
      "and rises with concentration iff -QP''/P' < 2", ok)

# F2 partial replication: first-order linearity dur_rep = (1-rep) priv + rep dur
ok = True
for n in (3, 5, 8):
    for nr in range(n):
        dd = 1e-5
        E1, E0 = lin_cournot(n, 0.2, dd, BB)
        Yd = 0.2 / BB * dd
        rep = nr / (n - 1)
        exact = (E1(nr) - E0(0)) / Yd
        priv = 2 * n / (n + 1)
        dur = 2 / (n + 1)
        ok &= abs(exact - ((1 - rep) * priv + rep * dur)) < 1e-3
    for nm in ("exp", "log", "ces2"):
        P, dP, d2P = demands[nm]
        c = 0.6 if nm != "ces2" else 0.3
        p, q, pr = cournot_solve([c] * n, P, dP)
        Q = q.sum()
        phi_i = n / (n + 1 + Q * d2P(Q) / dP(Q))
        priv = (2 * n - 1) / n - (n - 1) * phi_i / n ** 2
        dur = 1 - phi_i * (1 - 1 / n)
        h = 1e-6
        for nr in range(n):
            _, _, pr2 = cournot_solve([c - h] * (nr + 1) + [c] * (n - nr - 1), P, dP)
            rep = nr / (n - 1)
            ok &= abs((pr2[0] - pr[0]) / h / q[0] - ((1 - rep) * priv + rep * dur)) < 1e-4
check("F2 cor:ext-game-engine(a): when the share rep of rivals can replicate the saving, the durable share is "
      "(1-rep) priv + rep dur to first order (linear, exponential, logarithmic and constant-elasticity demand)", ok)

# F3 table of durable shares
cols = [1, 2, 3, 4, 6, 10]
rows = {
    "lin_dur": [2 / (k + 1) for k in cols],
    "lin_priv": [2 * k / (k + 1) for k in cols],
    "ces2_dur": [(1 / k) * (2 - 1) / (2 - 1 / k) for k in cols],
    "ces08_dur": [((1 / k) * (0.8 - 1) / (0.8 - 1 / k)) if 0.8 * k > 1 else None for k in cols],
}
tex_rows = {}
for key, vals in rows.items():
    tex_rows[key] = " & ".join("n.a." if v is None else f"{v:.2f}".replace("-", "$-$") for v in vals)
    print(f"     -> table {key}: {tex_rows[key]}")
ok = close(rows["lin_dur"][3], 0.4) and close(rows["ces2_dur"][3], 1 / 7) and abs(rows["ces08_dur"][3] + 0.0909) < 1e-4
check("F3 tab:ext-game-dur: durable and private shares by number of firms (linear; constant elasticity 2 and 0.8)", ok)

# F4 engine classification example: four firms, linear demand, varpi = 0.6, saving 2.0 a year, transition cost 20
ok = True
wv, sav, Ttr = 0.6, DC * Y0, 20.0
npv_dur = wv * 0.4 * sav / (R - GG) - Ttr
npv_priv = wv * 1.6 * sav / (R - GG) - Ttr
npv_old = wv * (1 / 5) * sav / (R - GG) - Ttr
print(f"     -> classification: NPV_dur = {npv_dur:.1f}, NPV_priv = {npv_priv:.1f} (defensive); retained-margin rule "
      f"of def:ext-motives gives {npv_old:.1f}")
ok &= abs(npv_dur + 12.0) < 1e-9 and abs(npv_priv - 12.0) < 1e-9 and abs(npv_old + 16.0) < 1e-9
check("F4 cor:ext-game-engine(b) example: NPV_dur = -12.0 <= 0 < NPV_priv = 12.0, so the bundle is defensive; the "
      "fixed-volume retained share 1/(n+1) would give -16.0", ok)
for s in ("12.0", "16.0"):
    quote(s)

# F5 calibration of the industry pass-through (P2 theory pass v2): central 0.5, scenarios 0 and 0.7 (class b anchors:
# Choi 2025 DMA study ~0 short run; Ganapati, Shapiro and Walker 2020 ~0.7; Benedek et al. 2015 VAT 1.0 / 0.3),
# against the linear-Cournot benchmark n/(n+1) = 0.8 at four firms. dur = 1 - phi (1 - HHI) is kept.
ok = True
H4 = 0.25
cour = 4 / (4 + 1)
ok &= close(cour, 0.8) and all(n / (n + 1) >= 0.75 for n in range(3, 50))
durs = {ph: 1 - ph * (1 - H4) for ph in (0.0, 0.5, 0.7, cour)}
privs = {ph: 2 - H4 - H4 * (1 - H4) * ph for ph in (0.0, 0.5, 0.7, cour)}
ok &= close(durs[0.0], 1.0) and close(durs[0.5], 0.625) and close(durs[0.7], 0.475) and close(durs[cour], 0.4)
ok &= close(privs[cour], 1.6) and close(privs[0.0], 1.75)
npvd = {ph: wv * durs[ph] * sav / (R - GG) - Ttr for ph in durs}
npvp = {ph: wv * privs[ph] * sav / (R - GG) - Ttr for ph in privs}
ok &= abs(npvd[0.0]) < 1e-9 and abs(npvd[0.5] + 7.5) < 1e-9 and abs(npvd[0.7] + 10.5) < 1e-9
ok &= all(npvd[ph] <= 1e-9 < npvp[ph] for ph in (0.0, 0.5, 0.7, cour))      # defensive at every scenario
curv = {ph: 4 + 1 - 4 / ph for ph in (0.5, 0.7)}
ok &= close(curv[0.5], -3.0) and abs(curv[0.7] + 0.714) < 1e-3
# the general-demand formula reproduces the measured value at that curvature
ok &= all(close(4 / (4 + 1 - curv[ph]), ph) for ph in curv)
# lower pass-through raises dur at every HHI in (0, 1)
ok &= all(1 - 0.5 * (1 - h) > 1 - 0.7 * (1 - h) > 1 - (1 / h) / (1 / h + 1) * (1 - h) for h in np.linspace(0.05, 1 / 3, 19))   # three or more symmetric firms
print(f"     -> durable share at HHI 0.25: {durs[0.0]:.1f}, {durs[0.5]:.3f}, {durs[0.7]:.3f} (Cournot {durs[cour]:.2f}); "
      f"private {privs[0.0]:.2f}, {privs[0.5]:.2f}, {privs[0.7]:.2f}; NPV_dur {npvd[0.0]:.1f}, {npvd[0.5]:.1f}, "
      f"{npvd[0.7]:.1f}; NPV_priv {npvp[0.0]:.1f}, {npvp[0.5]:.1f}, {npvp[0.7]:.1f}; curvature {curv[0.5]:.0f}, {curv[0.7]:.2f}")
check("F5 calibration of phi_ind: central 0.5, scenarios 0 and 0.7 against the Cournot benchmark 0.8; dur 1.0/0.625/0.475 "
      "vs 0.40; the example bundle stays defensive at every scenario (NPV_dur 0, -7.5, -10.5; NPV_priv 15.0, 13.1, 12.4)", ok)
for s_ in ("0.625", "0.475", "1.75, 1.66 and 1.62", "$-\\$7.5$ million", "$-\\$10.5$ million", "\\$15.0, \\$13.1 and \\$12.4 million",
           "$-3$ and $-0.71$", "with central value 0.5", "0.8 for four firms"):
    quote(s_)

# ==============================================================================================
header("T. Text consistency, citations and style")
# ==============================================================================================
tex_path = ROOT / "part2" / "theory_competition.tex"
prf_path = ROOT / "part2" / "proofs_competition.tex"
if tex_path.exists() and prf_path.exists():
    tex = tex_path.read_text()
    prf = prf_path.read_text()
    missing = [s for s in QUOTED if s not in tex]
    check("T1 every number the script asserts appears in theory_competition.tex", not missing,
          "missing: " + ", ".join(missing) if missing else f"{len(QUOTED)} strings")
    # table rows
    ok = all(tex_rows[k] in tex for k in tex_rows)
    check("T2 tab:ext-game-dur rows in the tex equal the script's values", ok)
    # no em-dashes
    ok = ("\u2014" not in tex + prf) and ("---" not in tex + prf)
    check("T3 no em-dashes in theory_competition.tex or proofs_competition.tex", ok)
    # citation keys exist
    keys = set()
    for bib in ("refs.bib", "part2/refs_part2.bib", "part2/refs_modern.bib", "part2/refs_competition.bib"):
        pth = ROOT / bib
        if pth.exists():
            keys |= set(re.findall(r"@\w+\{([^,]+),", pth.read_text()))
    cited = set()
    for m in re.finditer(r"\\cite[pt]?\*?(?:\[[^\]]*\])*\{([^}]+)\}", tex + prf):
        cited |= {k.strip() for k in m.group(1).split(",")}
    check("T4 every cited key exists in refs.bib, refs_part2.bib, refs_modern.bib or refs_competition.bib",
          cited <= keys, "missing: " + ", ".join(sorted(cited - keys)) if cited - keys else f"{len(cited)} keys")
    # labels referenced in the proofs exist
    labels = set(re.findall(r"\\label\{([^}]+)\}", tex))
    refs = set(re.findall(r"\\ref\{((?:prop|lem|cor|ass|eq):ext-game[^}]*)\}", tex + prf)) | \
        set(re.findall(r"\\eqref\{(eq:ext-game[^}]*)\}", tex + prf))
    check("T5 every ext-game label referenced in the two files is defined in theory_competition.tex",
          refs <= labels, "undefined: " + ", ".join(sorted(refs - labels)) if refs - labels else f"{len(refs)} refs")
else:
    check("T0 theory_competition.tex and proofs_competition.tex exist", False)

n_fail = sum(1 for _, ok in RESULTS if not ok)
print("\n" + "=" * 78)
print(f"SUMMARY: {len(RESULTS) - n_fail}/{len(RESULTS)} checks passed" + ("" if n_fail == 0 else f"; {n_fail} FAILED"))
print("=" * 78)
sys.exit(0 if n_fail == 0 else 1)
