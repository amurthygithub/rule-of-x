#!/usr/bin/env python3
"""
verify_part2_labor.py

Symbolic (sympy) and numerical (numpy/scipy) checks of every closed form, threshold and worked example in
  part2/theory_labor.tex   (Section "Labor Law, Talent and Jurisdiction", label sec:labor)
  part2/proofs_labor.tex   (Appendix "Proofs for Section sec:labor", label app:proofs-labor)
Paper 2, "The Economics of AI Transformation" (formerly Part II of "The Efficient Frontier of Growth and Profitability").

Run:  python3 code/verify_part2_labor.py      (a few seconds)
Exit code 0 iff every check passes. Check names cite the LaTeX labels of the results. Every number quoted in
theory_labor.tex is printed with "->" and asserted; a few extra numbers (ramp, other countries) are checked for the
engine notes.

The statutory calculators in Section L0 mirror the engine formulas listed in notes/labor_notes.md, Section 3.
They encode the rules as model constraints, verified at the primary sources logged in
notes/ref_verification_labor.md (as of 29 Oct 2026). They are not legal advice.

Script names -> paper symbols:
  Tleg -> T^leg (procedure start to earliest effective dismissal), Ttech -> T^tech (technology consultation),
  s -> T^st_c (delay of the parallel run's start), G -> t^gate = T^st + T_par, tA -> t^A (procedure start),
  tD -> t^dis (earliest effective dismissal), m -> T^ov = min{T^leg, t^gate},
  cann -> c^ann (cost flow of the announced state), Cwd -> C^wd (withdrawal cost), om -> varpi (success prob.),
  chat, chat1 -> c-hat and c-hat' (cost of a parallel-run year after / before the hold period), D0 -> T^hold,
  D -> N^dis (displaced FTE), R -> N^sv (survivors), Q -> N^q (extra quits),
  nuq, nus, nuD, nux -> nu^q, nu^s, nu^D, nu^x (quit hazards), kdoc, kret -> kappa_doc, kappa_ret,
  Gam -> Gamma (engineering FTE), h -> dot-Gamma^hire (hiring rate), ebld, emnt -> e_bld, e_mnt,
  prem -> sans-serif p (AI wage premium), wi -> sans-serif w_c (location wage index),
  a, K (lemma) -> c-bar, c^fx, sres, sbar -> omega^res, omega-bar^res (restricted input share), nuinv -> nu^inv.
The paper avoids the reserved Part I symbols (spec Section 1), so these script names differ from the paper's.
"""
import math
import sys

import numpy as np
import sympy as sp
from scipy import integrate, optimize

RNG = np.random.default_rng(20261029)
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ::  {detail}" if detail else ""))


def header(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def zero(e):
    return sp.simplify(e) == 0


YEAR = 365.0
MONTH = 1.0 / 12.0
WEEK_PER_MONTH = 52.0 / 12.0

# ==============================================================================================
header("L0. Statutory calculators (tab:labor-rules; engine formulas, notes Section 3)")
# ==============================================================================================


def warn_federal(employer_ft, site_active_ft, losses_30d, plant_closing=False):
    """29 U.S.C. 2101-2102, 20 CFR 639.3: employer of 100+ (excl. part-time); plant closing: 50+ at a single site
    in 30 days; mass layoff: 50+ and 33% of active employees, or 500+. Returns (triggered, notice_days)."""
    if employer_ft < 100:
        return False, 0
    if plant_closing:
        trig = losses_30d >= 50
    else:
        trig = losses_30d >= 500 or (losses_30d >= 50 and losses_30d >= 0.33 * site_active_ft)
    return trig, (60 if trig else 0)


def warn_ca(establishment_12m, layoffs_30d):
    """Cal. Lab. Code 1400.5, 1401: covered establishment 75+ in the preceding 12 months; mass layoff 50+ in 30
    days (no percentage test); 60 days' notice."""
    trig = establishment_12m >= 75 and layoffs_30d >= 50
    return trig, (60 if trig else 0)


def warn_ny(employer_ft_ny, site_ft, layoffs):
    """NY DOL fact sheet P483: employers of 50+ full-time employees in NY; mass layoff 25+ if 33% of the site,
    or 250+; 90 days' notice."""
    if employer_ft_ny < 50:
        return False, 0
    trig = layoffs >= 250 or (layoffs >= 25 and layoffs >= 0.33 * site_ft)
    return trig, (90 if trig else 0)


def warn_nj(employer, terminated, years, notice_days):
    """NJ DOL form NJES-997 (2/26): employers of 100+; 50+ terminated at or reporting to an NJ establishment;
    mandatory severance of one week per full year, plus four weeks if notice is under 90 days.
    Returns (triggered, severance_weeks)."""
    trig = employer >= 100 and terminated >= 50
    if not trig:
        return False, 0
    return True, math.floor(years) + (4 if notice_days < 90 else 0)


def eu_collective(size, d30, d90, option="30day"):
    """Directive 98/59/EC Art. 1(1)(a): (i) over 30 days, >=10 (21-99), >=10% (100-299), >=30 (>=300);
    (ii) over 90 days, >=20 whatever the size. Member States choose the option."""
    if option == "90day":
        return d90 >= 20
    if 20 < size < 100:
        return d30 >= 10
    if 100 <= size < 300:
        return d30 >= 0.10 * size
    if size >= 300:
        return d30 >= 30
    return False


def de_anzeige(size, d30):
    """KSchG 17(1): >20 and <60: more than 5; 60 to 499: 10% or more than 25; >=500: at least 30 (30 days)."""
    if 20 < size < 60:
        return d30 > 5
    if 60 <= size < 500:
        return d30 >= 0.10 * size or d30 > 25
    if size >= 500:
        return d30 >= 30
    return False


def de_sozialplan_enforceable(size, d):
    """BetrVG 112a(1): <60: 20% and at least 6; 60-249: 20% or at least 37; 250-499: 15% or at least 60;
    >=500: 10% and at least 60."""
    if size < 60:
        return d >= 0.20 * size and d >= 6
    if size < 250:
        return d >= 0.20 * size or d >= 37
    if size < 500:
        return d >= 0.15 * size or d >= 60
    return d >= 0.10 * size and d >= 60


def de_notice_months(years):
    """BGB 622(2): employer notice by tenure: 2y 1, 5y 2, 8y 3, 10y 4, 12y 5, 15y 6, 20y 7 months (to month end);
    below 2 years the basic four weeks of 622(1) (about 0.92 months)."""
    for t, m in [(20, 7), (15, 6), (12, 5), (10, 4), (8, 3), (5, 2), (2, 1)]:
        if years >= t:
            return float(m)
    return 4.0 / WEEK_PER_MONTH


def de_1a_months(years):
    """KSchG 1a(2): 0.5 monthly earnings per year of employment (if the employer offers it in the notice)."""
    return 0.5 * years


def fr_pse_required(firm_size, d30):
    """Code du travail L1233-61: firms of 50+, 10+ dismissals within 30 days."""
    return firm_size >= 50 and d30 >= 10


def fr_cse_months(d):
    """L1233-30: CSE opinion within 2 months (<100), 3 months (100-249), 4 months (>=250) from the first meeting."""
    return 2.0 if d < 100 else (3.0 if d < 250 else 4.0)


def fr_admin_days(agreement):
    """L1233-57-4: validation of an agreement within 15 days; homologation of a unilateral document in 21 days."""
    return 15 if agreement else 21


def fr_notice_months(years):
    """L1234-1: 6 months to 2 years: one month; 2 years or more: two months (shorter tenures: law or agreement)."""
    return 2.0 if years >= 2 else (1.0 if years >= 0.5 else 0.0)


def fr_indemnity_months(years):
    """R1234-2: 1/4 month per year up to ten years, 1/3 month per year beyond ten."""
    return 0.25 * min(years, 10) + max(years - 10, 0) / 3.0


def uk_collective(d90_one_establishment):
    """TULRCA 188(1): 20 or more at one establishment within 90 days; 188(1A): 45 days (100+), else 30 days."""
    if d90_one_establishment < 20:
        return False, 0
    return True, (45 if d90_one_establishment >= 100 else 30)


def uk_srp_weeks(age, years):
    """ERA 1996 s.162: counting back from the relevant date, 1.5 weeks for each year aged 41+, 1 week aged 22-40,
    0.5 week otherwise; at most 20 years."""
    w = 0.0
    for k in range(min(int(years), 20)):
        a = age - 1 - k          # age during the k-th year counted back
        w += 1.5 if a >= 41 else (1.0 if a >= 22 else 0.5)
    return w


UK_WEEK_CAP_2026 = 751.0        # GBP, from 6 April 2026 (Employment Rights (Increase of Limits) Order 2026)
UK_PROTECTIVE_MAX_DAYS = 180    # TULRCA 189(4) as amended by ERA 2025 s.30(2), from 6 April 2026


def in_retrenchment(years, chapter_x=False):
    """IR Code 2020 s.70 (in force 21 Nov 2025): one month's notice or pay; compensation 15 days' average pay per
    completed year (a part year over six months counted as a year, ID Act convention, flagged); s.83: re-skilling
    fund contribution of 15 days' wages. Chapter X (s.77: factories, mines, plantations of 300+) requires prior
    permission; its notice length is not verified here. Returns months of pay (notice, compensation, fund),
    with 15 days = 0.5 month."""
    full = math.floor(years) + (1 if years - math.floor(years) > 0.5 else 0)
    return 1.0, 0.5 * full, 0.5


ok = True
ok &= warn_federal(5000, 1000, 400)[0] and not warn_federal(5000, 1500, 400)[0] and warn_federal(5000, 3000, 500)[0]
ok &= not warn_federal(90, 100, 60)[0] and warn_federal(150, 100, 50, plant_closing=True) == (True, 60)
ok &= warn_ca(80, 50) == (True, 60) and not warn_ca(74, 60)[0]
ok &= warn_ny(60, 100, 33) == (True, 90) and not warn_ny(60, 100, 30)[0] and warn_ny(60, 2000, 250)[0]
ok &= warn_nj(150, 60, 5.7, 60) == (True, 9) and warn_nj(150, 60, 5.7, 90) == (True, 5)
check("L0a WARN federal (100 employer; 50 plant closing; 50 and 33% or 500 mass layoff; 60 days), Cal-WARN "
      "(75; 50 in 30 days; 60 days), NY (50; 25 and 33% or 250; 90 days), NJ (100; 50; 1 week a year + 4)", ok)
ok = eu_collective(80, 10, 0) and not eu_collective(80, 9, 0) and eu_collective(200, 20, 0) \
    and not eu_collective(200, 19, 0) and eu_collective(1000, 30, 0) and eu_collective(10, 0, 20, "90day")
ok &= de_anzeige(50, 6) and not de_anzeige(50, 5) and de_anzeige(400, 26) and de_anzeige(200, 20) \
    and not de_anzeige(200, 19) and de_anzeige(800, 30) and not de_anzeige(800, 29)
ok &= de_sozialplan_enforceable(1000, 100) and not de_sozialplan_enforceable(1000, 99) \
    and de_sozialplan_enforceable(200, 37) and not de_sozialplan_enforceable(50, 5)
check("L0b Directive 98/59/EC Art. 1(1)(a) thresholds; KSchG 17(1) notification thresholds; BetrVG 112a(1) "
      "enforceable social plan thresholds", ok)
ok = [de_notice_months(y) for y in (1, 2, 5, 8, 10, 12, 15, 20, 30)] == [4.0 / WEEK_PER_MONTH, 1, 2, 3, 4, 5, 6, 7, 7]
ok &= de_1a_months(5) == 2.5 and fr_indemnity_months(5) == 1.25 and abs(fr_indemnity_months(12) - (2.5 + 2 / 3)) < 1e-12
ok &= fr_cse_months(99) == 2 and fr_cse_months(100) == 3 and fr_cse_months(250) == 4
ok &= fr_notice_months(5) == 2 and fr_notice_months(1) == 1 and fr_pse_required(50, 10) and not fr_pse_required(49, 50)
check("L0c BGB 622(2) notice ladder (1-7 months); KSchG 1a 0.5 month a year; R1234-2 (1/4 to 10 years, 1/3 beyond); "
      "L1233-30 CSE periods 2/3/4 months; L1234-1 notice; L1233-61 PSE trigger", ok)
srp_45_10 = uk_srp_weeks(45, 10)
srp_30_5 = uk_srp_weeks(30, 5)
ok = srp_45_10 == 12.0 and srp_30_5 == 5.0 and uk_srp_weeks(61, 30) == 30.0 and uk_srp_weeks(60, 30) == 29.5 and uk_collective(150) == (True, 45) \
    and uk_collective(20) == (True, 30) and not uk_collective(19)[0]
check("L0d TULRCA 188 (20 at one establishment in 90 days; 30 or 45 days); ERA s.162 ladder with the 20-year cap "
      "(age 45, 10 years -> 12 weeks: 4 years aged 41+ at 1.5 and 6 at 1; age 61, 30 years -> 20 years at 1.5 = 30 weeks; age 60 -> 29.5)", ok,
      f"age 45/10y {srp_45_10}, age 30/5y {srp_30_5}")
n_, c_, f_ = in_retrenchment(5.0)
n2, c2, f2 = in_retrenchment(5.6)
check("L0e IR Code 2020 s.70/s.83: at 5 years, 1 month notice + 2.5 months compensation + 0.5 month re-skilling fund "
      "(5.6 years -> 3.0 months)", (n_, c_, f_) == (1.0, 2.5, 0.5) and c2 == 3.0)
# statutory floors per displaced FTE at 5 years of tenure (months of pay), the row 'cash floor' of tab:labor-rules
floors = {"US-federal": 0.0, "NJ": warn_nj(150, 60, 5, 90)[1] / WEEK_PER_MONTH, "UK": uk_srp_weeks(35, 5) / WEEK_PER_MONTH,
          "DE (1a)": de_1a_months(5), "FR": fr_indemnity_months(5), "IN": sum(in_retrenchment(5.0)[1:])}
print("     -> statutory cash floors at 5 years (months of pay): "
      + ", ".join(f"{k} {v:.2f}" for k, v in floors.items()))
check("L0f statutory floors at 5 years' tenure: NJ 1.15, UK 1.15 (below the weekly cap), DE 2.5 (if 1a used), "
      "FR 1.25, IN 3.0 (compensation plus fund), US federal 0 months",
      abs(floors["NJ"] - 1.154) < 1e-3 and abs(floors["UK"] - 1.154) < 1e-3 and floors["DE (1a)"] == 2.5
      and floors["FR"] == 1.25 and floors["IN"] == 3.0)

# legal leads (years) used in the examples; DE consultation and technology periods are scenario values (class d)
Tleg = {"US": 60 / YEAR, "NY/NJ": 90 / YEAR, "UK": 45 / YEAR, "IN": MONTH,
        "DE": 3 * MONTH + max(1.0, de_notice_months(5)) * MONTH,
        "FR": fr_cse_months(150) * MONTH + fr_admin_days(False) / YEAR + fr_notice_months(5) * MONTH}
Ttech = {"US": 0.0, "NY/NJ": 0.0, "UK": 0.0, "IN": 0.0, "DE": 3 * MONTH, "FR": 2 * MONTH}
print("     -> legal leads T^leg (years): " + ", ".join(f"{k} {v:.3f}" for k, v in Tleg.items()))
check("L0g example leads: US 60 days = 0.164 yr; NY/NJ 0.247; UK 45 days = 0.123; IN 0.083; DE 3 months of "
      "consultation + max(1-month Sperrfrist, 2-month notice) = 0.417; FR 3 months CSE + 21 days + 2 months = 0.474",
      abs(Tleg["US"] - 0.1644) < 1e-4 and abs(Tleg["NY/NJ"] - 0.2466) < 1e-4 and abs(Tleg["UK"] - 0.1233) < 1e-4
      and abs(Tleg["DE"] - 0.41667) < 1e-4 and abs(Tleg["FR"] - 0.47420) < 1e-4)

# ==============================================================================================
header("L1. Proposition prop:labor-lead (lead times, wave timing, streams, windows, announcement, free run)")
# ==============================================================================================
Tpar = 0.5
# (a) cutover dates with the procedure started at the decision date (early) or at the gate (late); s = Ttech
early = {k: max(Ttech[k] + Tpar, Tleg[k]) for k in Tleg}
late = {k: Ttech[k] + Tpar + Tleg[k] for k in Tleg}
print("     -> cutover, procedure started at the decision date: " + ", ".join(f"{k} {v:.3f}" for k, v in early.items()))
print("     -> cutover, procedure started at the gate:          " + ", ".join(f"{k} {v:.3f}" for k, v in late.items()))
ok = all(abs(early[k] - v) < 5e-4 for k, v in {"US": 0.5, "UK": 0.5, "IN": 0.5, "DE": 0.75, "FR": 0.6667}.items())
ok &= all(abs(late[k] - v) < 5e-4 for k, v in {"US": 0.6644, "UK": 0.6233, "IN": 0.5833, "DE": 1.1667, "FR": 1.1409}.items())
# delay formula: t^D - T_par = max{s, T^leg - T_par} when started at 0
ok &= all(abs((early[k] - Tpar) - max(Ttech[k], Tleg[k] - Tpar)) < 1e-12 for k in Tleg)
check("L1a (a) with T_par = 0.5: early start -> cutover 0.5 (US, UK, IN), 0.67 (FR), 0.75 (DE); start at the gate -> "
      "0.66, 0.62, 0.58, 1.14, 1.17; delay = max{s, T^leg - T_par}", ok)
# (b) streams: optimal partition into groups that are intervals in the order of t^D (brute force over partitions)


def partitions(seq):
    if not seq:
        yield []
        return
    first, rest = seq[0], seq[1:]
    for p in partitions(rest):
        yield [[first]] + p
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]


def part_cost(groups, tD, W, Ow):
    c = 0.0
    for g in groups:
        T = max(tD[i] for i in g)
        c += sum(W[i] * (T - tD[i]) for i in g)
    return c + (len(groups) - 1) * Ow


bad = 0
for _ in range(400):
    n = int(RNG.integers(2, 6))
    tD = RNG.uniform(0.3, 1.5, n)
    W = RNG.uniform(0.1, 3, n)
    Ow = RNG.uniform(0, 1)
    best = min(partitions(list(range(n))), key=lambda g: part_cost(g, tD, W, Ow))
    bestc = part_cost(best, tD, W, Ow)
    order = list(np.argsort(tD))
    # best among interval partitions in t^D order
    best_int = math.inf
    for mask in range(2 ** (n - 1)):
        groups, cur = [], [order[0]]
        for k in range(1, n):
            if mask >> (k - 1) & 1:
                groups.append(cur)
                cur = [order[k]]
            else:
                cur.append(order[k])
        groups.append(cur)
        best_int = min(best_int, part_cost(groups, tD, W, Ow))
    if best_int > bestc + 1e-9:
        bad += 1
    # two-stream rule: splitting the fastest i jurisdictions pays iff sum_{l<=i} W(l)(tmax - t(i)) > O_w
    srt = sorted(range(n), key=lambda i: tD[i])
    for i in range(1, n):
        fast = srt[:i]
        gain = sum(W[l] * (tD[srt[-1]] - tD[srt[i - 1]]) for l in fast)
        split_cost = part_cost([fast, srt[i:]], tD, W, Ow)
        sync_cost = part_cost([srt], tD, W, Ow)
        if (split_cost < sync_cost - 1e-12) != (gain > Ow + 1e-12) and abs(gain - Ow) > 1e-9:
            bad += 1
check("L1b (b) an optimal grouping of jurisdictions into cutover streams consists of intervals in the order of t^D; "
      "splitting off the fastest group pays iff its forgone savings exceed O_w (400 random waves, all partitions)",
      bad == 0)
ex_tD = {"US": early["US"], "FR": early["FR"], "DE": early["DE"]}
ex_W = {"US": 3.0, "FR": 1.0, "DE": 1.0}
sync_wait = {k: ex_W[k] * (ex_tD["DE"] - ex_tD[k]) for k in ex_tD}
print(f"     -> synchronized cutover at {ex_tD['DE']:.2f}: US waits {ex_tD['DE'] - ex_tD['US']:.2f} yr at $3M "
      f"(${sync_wait['US']:.2f}M), FR {ex_tD['DE'] - ex_tD['FR']:.3f} yr (${sync_wait['FR']:.3f}M)")
check("L1c (b) example: US $3M, FR $1M, DE $1M a year; the U.S. part waits 0.25 years ($0.75M) for Germany, more "
      "than an overhead of $0.5M, so it should cut over in its own stream",
      abs(sync_wait["US"] - 0.75) < 1e-9 and abs(sync_wait["FR"] - 0.0833) < 1e-3 and sync_wait["US"] > 0.5)


# (c) window bound
def min_span(D, Nthr, Twin):
    """smallest span of D dismissal dates with at most Nthr - 1 in any window of length Twin (greedy)."""
    k = math.ceil(D / (Nthr - 1)) - 1
    return k * Twin


bad = 0
for _ in range(300):
    Nthr = int(RNG.integers(2, 40))
    D = int(RNG.integers(1, 400))
    Tw = float(RNG.uniform(10, 120))
    # greedy placement in blocks attains the bound and satisfies the window constraint
    dates = np.array([(i // (Nthr - 1)) * Tw for i in range(D)])
    for i in range(D - Nthr + 1):
        if dates[i + Nthr - 1] - dates[i] < Tw * (1 - 1e-9):
            bad += 1
            break
    if abs((dates[-1] - dates[0]) - min_span(D, Nthr, Tw)) > 1e-9:
        bad += 1
    # any feasible sorted placement has span >= bound: random feasible placements
    gaps = RNG.uniform(0, 2 * Tw, D)
    t = np.cumsum(gaps)
    # repair to feasibility: enforce t[i+N-1] - t[i] >= Tw
    for i in range(Nthr - 1, D):
        t[i] = max(t[i], t[i - Nthr + 1] + Tw)
        if i + 1 < D:
            t[i + 1:] = np.maximum(t[i + 1:], t[i])
    if t[-1] - t[0] < min_span(D, Nthr, Tw) - 1e-9:
        bad += 1
uk_span = min_span(200, 20, 90)
de_span = min_span(300, 30, 30)
print(f"     -> sub-threshold pacing: UK 200 dismissals -> {uk_span:.0f} days ({uk_span / YEAR:.2f} yr); "
      f"DE (500+ establishment) 300 -> {de_span:.0f} days")
check("L1d (c) at most N^thr - 1 dismissals in every window of length T^win requires a span of at least "
      "(ceil(D/(N^thr-1)) - 1) T^win, and block placement attains it; UK 200 -> 900 days (2.46 yr), DE 300 -> 300 days",
      bad == 0 and uk_span == 900 and abs(uk_span / YEAR - 2.466) < 1e-3 and de_span == 300)


# (d) announcement timing
def ann_cost(tA, G, Tl, om, W, cann, Cwd):
    if tA >= G:
        return om * (cann + W) * Tl
    tD = max(G, tA + Tl)
    return om * (cann * (tD - tA) + W * (tD - G)) + (1 - om) * (cann * (G - tA) + Cwd)


def ann_rule(G, Tl, om, W, cann, Cwd):
    m = min(Tl, G)
    late = om * W * m < (1 - om) * (cann * m + Cwd)
    return G if late else max(0.0, G - Tl)


bad = 0
for _ in range(2000):
    G, Tl = RNG.uniform(0.05, 1.5), RNG.uniform(0.02, 1.2)
    om, W, cann, Cwd = RNG.uniform(0.05, 0.99), RNG.uniform(0, 5), RNG.uniform(0, 2), RNG.uniform(0, 2)
    grid = np.concatenate([np.linspace(0, G, 2001)[:-1], [G]])
    vals = np.array([ann_cost(x, G, Tl, om, W, cann, Cwd) for x in grid])
    tA = ann_rule(G, Tl, om, W, cann, Cwd)
    if ann_cost(tA, G, Tl, om, W, cann, Cwd) > vals.min() + 1e-9:
        bad += 1
check("L1e (d) the optimal procedure start is (G - T^leg)_+ or the gate G; start at the gate iff "
      "varpi W m < (1 - varpi)(c^ann m + C^wd), m = min{T^leg, G} (2,000 draws against a grid)", bad == 0)
Gfr = Ttech["FR"] + Tpar
m_fr = min(Tleg["FR"], Gfr)
om_cut = (0.3 * m_fr + 0.2) / (1.0 * m_fr + 0.3 * m_fr + 0.2)
lhs, rhs = 0.75 * 1.0 * m_fr, 0.25 * (0.3 * m_fr + 0.2)
print(f"     -> France: m = {m_fr:.3f}; varpi W m = {lhs:.3f} vs (1-varpi)(c m + C) = {rhs:.3f}; cutoff varpi^A = {om_cut:.3f}")
check("L1f (d) example (France, W = $1M, c^ann = $0.3M, C^wd = $0.2M, varpi = 0.75): start early; the cutoff "
      "success probability is 0.42", lhs > rhs and abs(om_cut - 0.419) < 1e-3)
# legal cap t^A <= t^cont: with the cap the constrained optimum is min(rule, t_cont) when the cost is piecewise linear
bad = 0
for _ in range(500):
    G, Tl = RNG.uniform(0.1, 1.5), RNG.uniform(0.02, 1.2)
    om, W, cann, Cwd = RNG.uniform(0.05, 0.99), RNG.uniform(0, 5), RNG.uniform(0, 2), RNG.uniform(0, 2)
    tcont = RNG.uniform(0, G)
    grid = np.linspace(0, tcont, 1001)
    vals = [ann_cost(x, G, Tl, om, W, cann, Cwd) for x in grid]
    cand = [min(max(0.0, G - Tl), tcont), 0.0, tcont]
    if min(ann_cost(c, G, Tl, om, W, cann, Cwd) for c in cand) > min(vals) + 1e-9:
        bad += 1
check("L1g (d) with a legal bound t^A <= t^cont the optimum is one of min{(G - T^leg)_+, t^cont}, 0 or t^cont "
      "(piecewise-linear cost; 500 draws)", bad == 0)


# (e) free parallel run
def Jrun(T, D0, chat, chat1, R, Tdet):
    return -chat1 * min(T, D0) - chat * max(T - D0, 0.0) - R * math.exp(-T / Tdet)


def Tstar(chat, R, Tdet):
    return Tdet * math.log(R / (Tdet * chat)) if R > Tdet * chat else 0.0


bad = 0
for _ in range(1000):
    chat = RNG.uniform(0.1, 2)
    chat1 = RNG.uniform(0, chat)
    R = RNG.uniform(0.01, 5)
    Tdet = RNG.uniform(0.05, 1)
    D0 = RNG.uniform(0, 2)
    Ts, Tss = Tstar(chat, R, Tdet), Tstar(chat1, R, Tdet) if chat1 > 0 else math.inf
    Topt = min(Tss, max(D0, Ts))
    res = optimize.minimize_scalar(lambda T: -Jrun(T, D0, chat, chat1, R, Tdet), bounds=(0, 20), method="bounded",
                                   options={"xatol": 1e-10})
    grid = np.linspace(0, 6, 6001)
    gbest = max(Jrun(x, D0, chat, chat1, R, Tdet) for x in grid)
    if Jrun(Topt, D0, chat, chat1, R, Tdet) < max(gbest, -res.fun) - 1e-7:
        bad += 1
check("L1h (e) with dismissals barred before D0, the optimal parallel run is min{T**, max{D0, T*}} "
      "(T** uses c-hat' = nu_rec E_p + C^dup; 1,000 draws)", bad == 0)
# concavity of J (piecewise linear concave cost with chat1 <= chat, plus concave -R e^{-T/Tdet})
Ts_, D0_, c_, c1_, R_, Td_ = sp.symbols("T D0 c c1 R T_d", positive=True)
J2 = sp.diff(-R_ * sp.exp(-Ts_ / Td_), Ts_, 2)
check("L1i (e) J is concave: the detection term has second derivative -R e^{-T/T_det}/T_det^2 < 0 and the cost "
      "slope rises from c-hat' to c-hat at D0", zero(J2 + R_ * sp.exp(-Ts_ / Td_) / Td_ ** 2))
chat_e, chat1_e, R_e, Td_e = 0.600, 0.130, 0.25 * 2.2, 0.25
Ts_e, Tss_e = Tstar(chat_e, R_e, Td_e), Tstar(chat1_e, R_e, Td_e)
To_fr = min(Tss_e, max(Tleg["FR"], Ts_e))
To_us = min(Tss_e, max(Tleg["US"], Ts_e))
res_star, res_fr = 0.25 * math.exp(-Ts_e / Td_e), 0.25 * math.exp(-To_fr / Td_e)
print(f"     -> T* = {Ts_e:.3f}, T** = {Tss_e:.3f}; France (D0 = {Tleg['FR']:.3f}) T_opt = {To_fr:.3f}; "
      f"US T_opt = {To_us:.3f}; undetected-failure risk {res_star:.4f} -> {res_fr:.4f}")
check("L1j (e) example (c-hat $600k, c-hat' $130k, (1-varpi)(C^str+L_roll) = $550k, T_det 0.25): T* = 0.32, "
      "T** = 0.71; with France's lead the run extends to 0.47 years and the undetected-failure risk falls from "
      "6.8% to 3.8%; the U.S. lead (0.16) leaves T* unchanged",
      abs(Ts_e - 0.3248) < 1e-3 and abs(Tss_e - 0.7072) < 1e-3 and abs(To_fr - 0.4742) < 1e-3
      and abs(To_us - Ts_e) < 1e-12 and abs(res_star - 0.0682) < 1e-3 and abs(res_fr - 0.0375) < 1e-3)

# ==============================================================================================
header("L2. Proposition prop:labor-survivor (backfill, one cut, success, retention, redeployment)")
# ==============================================================================================
# (a) extra quits: R e^{-nuq Ts}(1 - e^{-nus Ts}) <= R nus Ts
bad = 0
for _ in range(500):
    R, nq, ns, Tsv = RNG.uniform(10, 5000), RNG.uniform(0, 0.5), RNG.uniform(0, 1), RNG.uniform(0.1, 3)
    Q = R * math.exp(-nq * Tsv) * (1 - math.exp(-ns * Tsv))
    Qdiff = R * ((1 - math.exp(-(nq + ns) * Tsv)) - (1 - math.exp(-nq * Tsv)))
    if not (abs(Q - Qdiff) < 1e-9 * R and Q <= R * ns * Tsv + 1e-12):
        bad += 1
# Monte Carlo of the excess quits
R0, nq0, ns0, T0 = 1000, 0.13, 0.3, 1.0
sim_base = (RNG.exponential(1 / nq0, (400, R0)) < T0).sum(1).mean()
sim_ann = (RNG.exponential(1 / (nq0 + ns0), (400, R0)) < T0).sum(1).mean()
Qcf = R0 * math.exp(-nq0 * T0) * (1 - math.exp(-ns0 * T0))
check("L2a (a) extra quits Q = R e^{-nu^q T_s}[1 - e^{-nu^s T_s}] <= R nu^s T_s (500 draws; Monte Carlo)",
      bad == 0 and abs((sim_ann - sim_base) - Qcf) < 0.03 * Qcf, f"MC {sim_ann - sim_base:.1f} vs {Qcf:.1f}")
q_store = 2.2 / 93.6
crep = 13.5 / 52 + 0.15 * 2
Q_ex = 400 * q_store
C_ex = Q_ex * crep * 0.100
print(f"     -> excess quits per announcement {q_store:.4f} of survivors; 400 survivors -> {Q_ex:.2f} quits; "
      f"c^rep = {crep:.3f} years of wages; cost ${C_ex:.3f}M at $100k")
check("L2b (a) example: 2.2 induced quits per 93.6-worker store = 2.35% of survivors; 400 survivors -> 9.4 quits; "
      "c^rep = 13.5 weeks of hiring cost + 15% shortfall for two years = 0.56 years of wages; $0.53M",
      abs(q_store - 0.0235) < 1e-4 and abs(Q_ex - 9.40) < 0.01 and abs(crep - 0.5596) < 1e-3 and abs(C_ex - 0.526) < 1e-3)


# (b) subadditivity of star-shaped functions and the square-root rule with O_s
def star_fns():
    a, b, c = RNG.uniform(0, 0.2), RNG.uniform(0, 1), RNG.uniform(0.2, 1)
    return [lambda x: (a if x > 0 else 0.0) + b * x,
            lambda x: b * (1 - math.exp(-x / c)),
            lambda x: b * x ** c,
            lambda x: b * math.log1p(x / c)]


bad = 0
for _ in range(300):
    for f in star_fns():
        d = RNG.uniform(0.01, 1)
        parts = RNG.dirichlet(np.ones(int(RNG.integers(2, 6)))) * d
        if sum(f(p) for p in parts) < f(d) - 1e-12:
            bad += 1
        seq = [n * f(d / n) for n in range(1, 8)]
        if any(seq[i + 1] < seq[i] - 1e-12 for i in range(len(seq) - 1)):
            bad += 1
check("L2c (b) nu^s(x)/x nonincreasing implies subadditivity: tranches never lower total excess quits, and n equal "
      "tranches give n nu^s(d/n), nondecreasing in n (jump-plus-linear, exponential, power, log forms)", bad == 0)
# square-root rule with an extra per-wave charge O_s: continuous minimizer of C(n_w) with equal waves
WN, Tp, c2, Ow, Os = 12.0, 0.5, 0.25, 0.5, C_ex


def prog_cost_equal(nw, Wp=1.0, N=12, c1=0.2, c2=0.25, Tp=0.5, Ow=0.5):
    n = N / nw
    return Tp * (Wp * N * (nw + 1) / 2 + c1 * N + c2 * N ** 2 / nw) + nw * Ow


nstar0 = math.sqrt((WN / 2 + Ow / Tp) / c2)
nstar1 = math.sqrt((WN / 2 + (Ow + Os) / Tp) / c2)
res0 = optimize.minimize_scalar(lambda nw: prog_cost_equal(nw), bounds=(0.5, 12), method="bounded")
res1 = optimize.minimize_scalar(lambda nw: prog_cost_equal(nw, Ow=Ow + Os), bounds=(0.5, 12), method="bounded")
print(f"     -> wave size n* = {nstar0:.2f} without and {nstar1:.2f} with O_s = {Os:.3f}; "
      f"minimizers N/n_w: {12 / res0.x:.2f}, {12 / res1.x:.2f}")
check("L2d (b) the survivor charge enters prop:ext-waves(c) like overhead: n* = sqrt((WN/2 + (O_w+O_s)/T_par)/c^dr_2); "
      "example 5.29 -> 5.67 processes per wave",
      abs(12 / res0.x - nstar0) < 1e-3 and abs(12 / res1.x - nstar1) < 1e-3 and abs(nstar0 - 5.292) < 1e-3
      and abs(nstar1 - 5.674) < 2e-3)


# (c) success: exact factor [kdoc + (1-kdoc) e^{-(1-kret) nux tau}]^{nK} >= exponential lower bound
def succ_exact(nK, kdoc, kret, nux, tau):
    return (kdoc + (1 - kdoc) * math.exp(-(1 - kret) * nux * tau)) ** nK


def succ_lb(nK, kdoc, kret, nux, tau):
    return math.exp(-nK * (1 - kdoc) * (1 - kret) * nux * tau)


bad = 0
for _ in range(500):
    nK, kd, kr, nx, ta = int(RNG.integers(1, 8)), RNG.uniform(0, 1), RNG.uniform(0, 1), RNG.uniform(0, 3), RNG.uniform(0, 2)
    if succ_exact(nK, kd, kr, nx, ta) < succ_lb(nK, kd, kr, nx, ta) - 1e-12:
        bad += 1
# Monte Carlo of the exact factor
nK, kd, kr, nx, ta = 3, 0.2, 0.0, 0.5, Tleg["FR"]
dep = RNG.exponential(1 / ((1 - kr) * nx), (200000, nK)) < ta
fail_given = RNG.uniform(size=(200000, nK)) < (1 - kd)
mc = 1 - (dep & fail_given).any(1).mean()
s0 = succ_exact(3, 0.2, 0.0, 0.5, Tleg["FR"])
s1 = succ_exact(3, 0.2, 0.8, 0.5, Tleg["FR"])
print(f"     -> success factor without retention {s0:.4f} (lower bound {succ_lb(3, 0.2, 0.0, 0.5, Tleg['FR']):.4f}); "
      f"with kappa_ret = 0.8 {s1:.4f}; Monte Carlo {mc:.4f}")
check("L2e (c) the knowledge-holder factor [kappa_doc + (1-kappa_doc) e^{-(1-kappa_ret) nu^x tau}]^{n_K} is at least "
      "exp(-n_K(1-kappa_doc)(1-kappa_ret) nu^x tau) (Jensen; 500 draws) and matches Monte Carlo",
      bad == 0 and abs(mc - s0) < 0.004)
check("L2f (c) example: three holders among the displaced, nu^x = 0.5, kappa_doc = 0.2, announced for 0.474 years: "
      "factor 0.57; a retention award removing 80% of the excess hazard restores 0.89",
      abs(s0 - 0.5743) < 1e-3 and abs(s1 - 0.8930) < 1e-3)
# (d) retention rule
om0, stake, Cret, nq_h = 0.75, 1.9, 0.060, 0.132
gain = om0 * (s1 - s0) * stake
qstay = math.exp(-(nq_h + (1 - 0.8) * 0.5) * Tleg["FR"])
pay = 3 * Cret * qstay
fo_bound = om0 * (1 - 0.2) * 0.8 * 0.5 * Tleg["FR"] * stake
print(f"     -> retention gain ${gain:.3f}M vs expected payments ${pay:.3f}M (q_stay {qstay:.3f}); "
      f"first-order cap per holder ${fo_bound:.3f}M")
check("L2g (d) example: raising success from 0.43 to 0.67 on a $1.9M stake is worth $0.45M against $0.16M of "
      "expected awards ($60k each, paid to the 90% who stay)",
      abs(om0 * s0 - 0.4307) < 1e-3 and abs(om0 * s1 - 0.6698) < 1e-3 and abs(gain - 0.454) < 2e-3
      and abs(pay - 0.161) < 1e-3 and abs(qstay - 0.896) < 1e-3 and gain > pay)
# first-order: dvarpi/dkret at kret=0 equals varpi0 nK (1-kdoc) nux tau e^{...}/(...)
k_s = sp.symbols("k", nonnegative=True)
nK_s, kd_s, nx_s, ta_s = sp.symbols("n_K kappa_d nu tau", positive=True)
f_s = (kd_s + (1 - kd_s) * sp.exp(-(1 - k_s) * nx_s * ta_s)) ** nK_s
d0 = sp.diff(f_s, k_s).subs(k_s, 0)
lim = sp.limit(d0 / (nx_s * ta_s), nx_s, 0)
check("L2h (d) to first order in nu^x tau, d varpi/d kappa_ret = varpi^0 n_K (1-kappa_doc) nu^x tau, which gives "
      "the per-holder cap C^ret < varpi^0 (1-kappa_doc) kappa_ret nu^x tau (Y_s - Y_f)",
      zero(lim - nK_s * (1 - kd_s)))
# (e) redeployment bound and attrition time
bad = 0
for _ in range(300):
    nq, Noth, T, D, prd = RNG.uniform(0.02, 0.4), int(RNG.integers(50, 5000)), RNG.uniform(0.05, 2), int(RNG.integers(1, 500)), RNG.uniform(0.05, 1)
    V = RNG.poisson(nq * Noth * T, 4000)
    placed = np.minimum(D, RNG.binomial(V, prd))
    if placed.mean() / D > min(1.0, prd * nq * Noth * T / D) + 0.01:
        bad += 1
ud_ex = min(1.0, 0.3 * 0.132 * 2000 * Tleg["FR"] / 100)
Tatt = math.log(1 / 0.9) / 0.132
print(f"     -> redeployment bound u_d <= {ud_ex:.3f}; attrition-only time to shed 10%: {Tatt:.3f} years")
check("L2i (e) u_d <= min{1, varpi^rd nu^q N^oth T^w / D} (Poisson vacancies, binomial placement; 300 draws); "
      "example 0.375; shedding 10% by attrition at nu^q = 0.132 takes 0.80 years",
      bad == 0 and abs(ud_ex - 0.3755) < 1e-3 and abs(Tatt - 0.798) < 1e-3)
check("L2j JOLTS quits rates, Aug 2026 (monthly): information 1.1%, finance 1.0%, professional and business services "
      "2.1%; annual hazards 0.132, 0.120, 0.252", abs(12 * 0.011 - 0.132) < 1e-12 and abs(12 * 0.021 - 0.252) < 1e-12)

# ==============================================================================================
header("L3. Proposition prop:labor-talent (premium, maintenance ceiling, hiring path, hire or contract)")
# ==============================================================================================
# (a) premium: F(p) = F0 (1 + l p); T_h* rises by l p F0/(varpi b W) only where W > 0.
# The example reads the running invoice example (data/examples/invoice_chain.json, macros in
# part2/tables/invoice_macros.tex): its F_build is engineering time priced at w^AI = premium x wage x (1 + tau_L).
import json
import os
_IC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "examples", "invoice_chain.json")
with open(_IC) as _fh:
    IC = json.load(_fh)
ic_t, ic_in, ic_mac = IC["transition"], IC["inputs"], IC["macros"]
prem = ic_in["ai_engineer_premium"]["value"] - 1.0
F_ic, Fb_ic, Fint_ic, W_ic = ic_t["F"], ic_t["F_build"], ic_t["F_int"], ic_t["W"]
prem_part = Fb_ic * prem / (1 + prem)            # premium inside the build
F0_ic = F_ic - prem_part                          # investment at the developer wage
l_AI = (Fb_ic / (1 + prem)) / F0_ic               # engineering share of F0
print(f"     -> invoice example (version {IC['meta']['version']}): F = ${F_ic:,.0f} ({ic_mac['icF']}), "
      f"F_build = ${Fb_ic:,.0f} ({ic_mac['icFbuild']}), F_int = ${Fint_ic:,.0f}, W = ${W_ic:,.0f} ({ic_mac['icW']})")
print(f"     -> premium inside the build ${prem_part:,.0f} = {prem_part / F_ic:.2%} of F; l_AI = {l_AI:.3f}; "
      f"l_AI p = {l_AI * prem:.4f}")
# The example's invoice-derived numbers enter theory_labor.tex only through part2/tables/labor_macros.tex, written by
# code/make_labor_macros.py. Here they are recomputed from the JSON independently and compared with the macro file,
# so a change to the invoice example fails L3a, L3b or L3f until the generator is rerun.
import re as _re
_LM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "part2", "tables", "labor_macros.tex")
with open(_LM) as _fh:
    LAB = dict(_re.findall(r"\\newcommand\{\\(lab[A-Za-z]+)\}\{(.*)\}", _fh.read()))


def _num(tex):
    """numeric value of a macro string such as '\\$61{,}600', '2.2\\%' or '0.20'."""
    return float(tex.replace("\\$", "").replace("{,}", "").replace("\\%", ""))


print("     -> labor_macros.tex: " + ", ".join(f"{k} = {v}" for k, v in LAB.items()))
_tex_uses = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "part2", "theory_labor.tex")).read()
check("L3a (a) invoice example: the macros for the premium inside the build, its share of F, l_AI and l_AI p match the "
      "JSON (to $100, 0.1 point, 0.01, 0.1 point); F = F0 (1 + l_AI p) reconstructs F; W < 0, so no finite minimum "
      "horizon exists and the horizon statement of part (a) does not apply; the tex uses the macros",
      _num(LAB["labPremAmt"]) == round(prem_part, -2) and _num(LAB["labPremShareF"]) == round(100 * prem_part / F_ic, 1)
      and _num(LAB["labLAI"]) == round(l_AI, 2) and _num(LAB["labLAIp"]) == round(100 * l_AI * prem, 1)
      and _num(LAB["labPremRate"]) == round(100 * prem) and abs(F0_ic * (1 + l_AI * prem) - F_ic) < 1e-6 * F_ic
      and W_ic < 0 and all(f"\\{k}" in _tex_uses for k in ("labPremAmt", "labPremShareF", "labLAI", "labLAIp")))
w_se = ic_in["ai_engineer_wage"]["value"]          # engine build.ai_engineer_base_wage (OEWS May 2025 median, 135,980)
TAU_L_ANNUAL = ic_in["tau_L"]["value"]             # labor.tau_L, the loading on an annual wage (BLS ECEC, June 2026)
w_ai = w_se * (1 + prem) * (1 + TAU_L_ANNUAL)
print(f"     -> loaded AI engineer wage: ${w_se:,.0f} x {1 + prem:.2f} x {1 + TAU_L_ANNUAL:.4f} = ${w_ai:,.0f}")
check("L3b (a) w^AI = (1 + p) w^SE (1 + tau_L) from the invoice inputs matches labWAI, and labWSE and labTauL match "
      "the JSON (at the 29 Oct inputs: $135,980, the OEWS May 2025 median; 0.2896; $194,649); premium range 5% (within "
      "title) to 21% (Stephany and Teutloff)",
      _num(LAB["labWAI"]) == round(w_ai) and _num(LAB["labWSE"]) == round(w_se)
      and _num(LAB["labTauL"]) == round(TAU_L_ANNUAL, 2) and "\\labWAI" in _tex_uses)


# (b) maintenance ceiling: e dN/dt = Gamma - m N
def N_of_t(t, Gam, ebld, emnt):
    return Gam / emnt * (1 - math.exp(-emnt * t / ebld))


def T_of_N(N, Gam, ebld, emnt):
    Nbar = Gam / emnt
    return math.inf if N >= Nbar else ebld / emnt * math.log(Nbar / (Nbar - N))


bad = 0
for _ in range(200):
    Gam, eb, em = RNG.uniform(1, 50), RNG.uniform(0.2, 5), RNG.uniform(0.02, 1)
    sol = integrate.solve_ivp(lambda t, y: [(Gam - em * y[0]) / eb], (0, 10), [0.0], rtol=1e-10, atol=1e-12,
                              dense_output=True)
    for t in (0.5, 2.0, 7.0):
        if abs(sol.sol(t)[0] - N_of_t(t, Gam, eb, em)) > 1e-6 * (1 + Gam / em):
            bad += 1
    N = RNG.uniform(0, 0.99) * Gam / em
    if abs(N_of_t(T_of_N(N, Gam, eb, em), Gam, eb, em) - N) > 1e-8 * (1 + N) or T_of_N(N, Gam, eb, em) < eb * N / Gam - 1e-12:
        bad += 1
x = sp.symbols("x", positive=True)
stretch = -sp.log(1 - x) / x
mono = sp.simplify(sp.diff(stretch, x))
mono_ok = all(float(mono.subs(x, v)) > 0 for v in np.linspace(0.01, 0.99, 50)) and sp.limit(stretch, x, 0) == 1
check("L3c (b) N(t) = (Gamma/e_mnt)(1 - e^{-e_mnt t/e_bld}) solves the ODE (200 draws); T_Gamma(N) inverts it; the "
      "stretch factor -ln(1-x)/x rises from 1", bad == 0 and mono_ok)
ex1 = T_of_N(12, 6, 1.5, 0.48)        # engine default e_mnt = 0.48 [0.29, 1.14], class b (org.e_mnt)
ex2 = T_of_N(12, 6, 1.5, 0.25)        # sensitivity
ex3 = T_of_N(12, 12, 1.5, 0.48)
print(f"     -> 12 processes, e_bld 1.5: Gamma = 6, e_mnt = 0.48 -> {ex1:.2f} yr (3.0 without maintenance; ceiling "
      f"{6 / 0.48:.1f}); e_mnt = 0.25 -> {ex2:.2f} yr (ceiling {6 / 0.25:.0f}); Gamma = 12, e_mnt = 0.48 -> {ex3:.2f}")
check("L3d (b) example: e_bld = 1.5, e_mnt = 0.48 (engine default): 6 engineers sustain at most 12.5 processes and "
      "need 10.1 years for 12 (not 3.0); sensitivity e_mnt = 0.25: ceiling 24, 4.16 years; 12 engineers at 0.48 need 2.04",
      abs(ex1 - 10.06) < 0.01 and abs(6 / 0.48 - 12.5) < 1e-12 and abs(ex2 - 4.159) < 1e-3 and abs(ex3 - 2.044) < 1e-3)


# (c) hiring path with lead and ramp
def cum_capacity(T, h, Tlead, drp=0.0, Trp=0.0, Gam0=0.0):
    U = max(T - Tlead, 0.0)
    ramp = drp * (min(U, Trp) ** 2 / 2 + Trp * max(U - Trp, 0.0)) if Trp > 0 else 0.0
    return Gam0 * T + h * (U ** 2 / 2) - h * ramp


bad = 0
for _ in range(200):
    h, Tl, drp, Trp, need = RNG.uniform(1, 30), RNG.uniform(0, 1), RNG.uniform(0, 0.5), RNG.uniform(0.1, 3), RNG.uniform(1, 100)
    # numeric cumulative check by integrating effective FTE of hires over time
    T = Tl + RNG.uniform(0.1, 5)
    num = integrate.quad(lambda u: h * (u - drp * min(u, Trp)), 0, T - Tl, points=[Trp] if Trp < T - Tl else None)[0]
    if abs(num - cum_capacity(T, h, Tl, drp, Trp)) > 1e-7 * (1 + num):
        bad += 1
def T_hire_maint(emnt, h=10.0, Tlead=0.25, ebld=1.5, N=12.0):
    """time to N live processes with Gamma(t) = h (t - Tlead)_+ and maintenance: e_bld dN/dt = Gamma - e_mnt N."""
    sol = integrate.solve_ivp(lambda tt, y: [(h * max(tt - Tlead, 0.0) - emnt * y[0]) / ebld], (0, 20), [0.0],
                              dense_output=True, rtol=1e-10, atol=1e-12, max_step=0.01)
    return optimize.brentq(lambda x: sol.sol(x)[0] - N, Tlead + 1e-6, 20)


T_nr = 0.25 + math.sqrt(2 * 1.5 * 12 / 10)
T_m48, T_m0 = T_hire_maint(0.48), T_hire_maint(0.0)
T_rp = optimize.brentq(lambda T: cum_capacity(T, 10, 0.25, 0.15, 2.0) - 18.0, 0.3, 10)
print(f"     -> hiring 10 a year after a 0.25-year lead: 12 processes x 1.5 person-years done at {T_nr:.3f} yr, "
      f"{T_rp:.3f} yr with a 15% two-year ramp; with maintenance at e_mnt = 0.48 (ODE) {T_m48:.3f} yr")
check("L3e (c) cumulative capacity Gamma_0 T + h[(T-T^lead)^2/2 - delta^rp(...)] (200 draws); with Gamma_0 = 0 and no "
      "ramp, T = T^lead + sqrt(2 e_bld N/h): 2.15 years; with the ramp 2.31; with maintenance at e_mnt = 0.48 "
      "(numerical ODE) 12 processes are live at 2.36 years, and the ODE with e_mnt = 0 reproduces 2.15",
      bad == 0 and abs(T_nr - 2.147) < 1e-3 and abs(T_rp - 2.308) < 1e-3 and abs(T_m48 - 2.360) < 1e-3
      and abs(T_m0 - T_nr) < 1e-4)


# (d) hire, contract or reskill
def K_hire(dG, w, Tneed, drp, Trp, ch, What, Tlead):
    return dG * w * (Tneed + drp * min(Tneed, Trp) + ch) + What * Tlead


def K_contract(dG, w, Tneed, uct, What, Tct):
    return dG * w * (1 + uct) * Tneed + What * Tct


bad = 0
for _ in range(1000):
    dG, w, drp, Trp, ch, What = RNG.uniform(1, 20), RNG.uniform(0.1, 0.3), RNG.uniform(0, 0.4), RNG.uniform(0.5, 3), RNG.uniform(0.1, 0.5), RNG.uniform(0, 5)
    Tl, Tc, uct = RNG.uniform(0.1, 0.6), RNG.uniform(0, 0.1), RNG.uniform(0.1, 1.5)
    thr = (drp * Trp + ch + What * (Tl - Tc) / (dG * w)) / uct
    for Tn in (Trp + 0.01, Trp + 1, Trp + 5):
        better_c = K_contract(dG, w, Tn, uct, What, Tc) < K_hire(dG, w, Tn, drp, Trp, ch, What, Tl)
        if better_c != (Tn < thr) and abs(Tn - thr) > 1e-9:
            bad += 1
thr_ex = (0.3 + 13.5 / 52 + 2.0 * (0.25 - 1 / 12) / (5 * w_ai / 1e6)) / 0.5
print(f"     -> contract a 5-FTE gap if it lasts under {thr_ex:.2f} years (u_ct 0.5, $2M a year gated); "
      f"labContractT = {LAB['labContractT']}")
check("L3f (d) for T^need >= T^rp contracting beats hiring iff T^need < [delta^rp T^rp + c^hire + W-hat(T^lead - "
      "T^ct)/(Delta Gamma w^AI)]/u_ct (1,000 draws); the example threshold at the JSON's w^AI matches labContractT "
      "(1.80 years at the 29 Oct inputs)",
      bad == 0 and _num(LAB["labContractT"]) == round(thr_ex, 2) and "\\labContractT" in _tex_uses)

# ==============================================================================================
header("L4. Lemma lem:labor-location (wage index and the adoption date)")
# ==============================================================================================
# OECD Pensions at a Glance 2025, Table 7.5 (gross average wage 2024, USD at market exchange rates); India and
# China from the ILO Global Wage Report 2024-25 as reproduced in the table.
AW = {"United States": 70627, "Germany": 65856, "United Kingdom": 64379, "France": 46793, "Japan": 34600,
      "Poland": 23471, "Mexico": 9657, "China": 16955, "India": 2959}
wi = {k: v / AW["United States"] for k, v in AW.items()}
lag5 = {k: math.log(1 / v) / math.log(5) for k, v in wi.items()}
lag10 = {k: math.log(1 / v) / math.log(10) for k, v in wi.items()}
print("     -> wage index (US = 1): " + ", ".join(f"{k} {v:.3f}" for k, v in wi.items()))
print("     -> minimum lag ln(1/w)/delta_pi, fivefold: " + ", ".join(f"{k} {v:.2f}" for k, v in lag5.items()))
check("L4a OECD Table 7.5 indices: Germany 0.932, UK 0.912, France 0.663, Poland 0.332, Mexico 0.137, China 0.240, "
      "India 0.042", all(abs(wi[k] - v) < 5e-4 for k, v in {"Germany": 0.932, "United Kingdom": 0.912, "France": 0.663,
                                                              "Poland": 0.332, "Mexico": 0.137, "China": 0.240,
                                                              "India": 0.0419}.items()))
check("L4b lower bound on the adoption lag at a fivefold annual price decline: Germany 0.04, France 0.26, Poland 0.69, "
      "Mexico 1.24, India 1.97 years (1.38 at tenfold)",
      abs(lag5["Germany"] - 0.044) < 1e-3 and abs(lag5["France"] - 0.255) < 1e-3 and abs(lag5["Poland"] - 0.685) < 1e-3
      and abs(lag5["Mexico"] - 1.236) < 1e-3 and abs(lag5["India"] - 1.971) < 1e-3 and abs(lag10["India"] - 1.378) < 1e-3)
# lemma: T*_c - T*_1 = ln[(a-K)/(w a - K)]/delta >= ln(1/w)/delta, equality iff K = 0; checked against the
# closed form of prop:ext-timing(d)(ii): T* = ln[pi0/(c0 - cQ - rF/v)]/delta
bad = 0
for _ in range(2000):
    a, K, w = RNG.uniform(0.5, 5), RNG.uniform(0, 2), RNG.uniform(0.02, 1)
    dl = RNG.uniform(0.5, 3)
    pi0 = 10 * a
    if w * a <= K or a <= K:
        continue
    T1 = math.log(pi0 / (a - K)) / dl
    Tc = math.log(pi0 / (w * a - K)) / dl
    if abs((Tc - T1) - math.log((a - K) / (w * a - K)) / dl) > 1e-10 or Tc - T1 < math.log(1 / w) / dl - 1e-10:
        bad += 1
a_s, K_s, w_s = sp.symbols("a K w", positive=True)
gap = sp.simplify((a_s - K_s) * w_s - (w_s * a_s - K_s))
check("L4c (lemma) lag = ln[(a - K)/(w a - K)]/delta_pi >= ln(1/w)/delta_pi, because w(a - K) - (w a - K) = K(1 - w) "
      ">= 0 (2,000 draws)", bad == 0 and zero(gap - K_s * (1 - w_s)))

# ==============================================================================================
header("L5. Proposition prop:labor-residency (readiness cap, process threshold, choice of region; regional "
       "instances and mechanism hazard for the engine)")
# ==============================================================================================
iota, istar = 0.9, 0.85
sbar = 1 - istar / iota
print(f"     -> readiness 0.9, threshold 0.85: restricted share tolerated s-bar = {sbar:.4f}; 10% -> {iota * 0.9:.2f}")
check("L5a (b) with readiness 0.9 and threshold 0.85, full automation survives restrictions on up to "
      "1 - 0.85/0.9 = 5.6% of inputs; a 10% restriction caps readiness at 0.81 and flips the process",
      abs(sbar - 0.0556) < 1e-4 and abs(iota * (1 - 0.10) - 0.81) < 1e-12 and iota * 0.90 < istar)
# (b) value V(s) = [W((1-s) iota)]_+ is continuous when iota* > floor and jumps at s = 1 - floor/iota otherwise
bad = 0
for _ in range(300):
    k1, k0 = RNG.uniform(0.5, 3), RNG.uniform(0.1, 2)
    Wf = lambda i: k1 * i - k0               # increasing W in readiness
    floor = RNG.uniform(0, 0.9)
    iot = RNG.uniform(floor + 0.01, 1)
    ist = max(floor, k0 / k1)
    V = lambda s: (Wf((1 - s) * iot) if (1 - s) * iot >= floor and Wf((1 - s) * iot) >= 0 else 0.0)
    if ist < iot:
        sb = 1 - ist / iot
        left, right = V(sb - 1e-9), V(sb + 1e-9)
        jump = left - right
        expected_jump = max(Wf(floor), 0) if k0 / k1 < floor else 0.0
        if abs(jump - expected_jump) > 1e-6:
            bad += 1
check("L5b (b) the value of the process in the restricted share is continuous at s-bar when iota*_p is above the "
      "feasibility floor and drops by W_p(floor) when the floor binds (300 draws)", bad == 0)
# engine rule (notes Section 3.5): regional instances versus one global instance at the weakest readiness
bad = 0
for _ in range(500):
    R = int(RNG.integers(2, 6))
    iotas = RNG.uniform(0.3, 1, R)
    slopes, ints = RNG.uniform(0.5, 3, R), RNG.uniform(0.1, 1.5, R)
    Wc = lambda c, i: max(slopes[c] * i - ints[c], 0.0)
    Fa = RNG.uniform(0, 1)
    glob = sum(Wc(c, iotas.min()) for c in range(R))
    reg = sum(Wc(c, iotas[c]) for c in range(R)) - (R - 1) * Fa
    rule = sum(Wc(c, iotas[c]) - Wc(c, iotas.min()) for c in range(R)) > (R - 1) * Fa
    if (reg > glob) != rule:
        bad += 1
check("L5c (engine rule) regional instances beat one global instance at the weakest readiness iff the readiness gains exceed "
      "(R - 1) F a(r, T_A) (500 draws)", bad == 0)
# example: mechanism hazard precedent; (c) the region choice
sh = (2015 + (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 6) / YEAR) - (2000 + (31 + 28 + 31 + 30 + 31 + 30 + 26) / YEAR)
ps = 4.0 + 4 / YEAR
dpf = (2026 + (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 29) / YEAR) - (2023 + (31 + 28 + 31 + 30 + 31 + 30 + 10) / YEAR)
nuinv = 2 / (sh + ps + dpf)
print(f"     -> framework-years: Safe Harbour {sh:.2f}, Privacy Shield {ps:.2f}, DPF {dpf:.2f}; "
      f"nu^inv = {nuinv:.4f} a year; expected cost of reliance with C^sw = $0.5M: ${nuinv * 0.5e6:,.0f} a year")
check("L5d (example) two invalidations in 22.5 framework-years (26 Jul 2000 to 6 Oct 2015; 12 Jul 2016 to 16 Jul 2020; "
      "10 Jul 2023 to 29 Oct 2026) give nu^inv = 0.089 a year; with C^sw = $0.5M, $44k a year",
      abs(sh + ps + dpf - 22.5) < 0.05 and abs(nuinv - 0.0889) < 5e-4 and abs(nuinv * 0.5e6 - 44.4e3) < 300)
bad = 0
for _ in range(500):
    regions = int(RNG.integers(2, 5))
    pn, v = RNG.uniform(0.05, 2), RNG.uniform(100, 1e6)
    preg = RNG.uniform(0, 0.5, regions); preg[0] = 0.0
    cq = RNG.uniform(0.1, 2, regions)
    fix = RNG.uniform(0, 1e5, regions)
    cost = (1 + preg) * pn + cq + fix / v
    best = int(np.argmin(cost))
    # in-region (index 1) preferred over transfer (index 0) iff preg pn v < fix0 - fix1 + v (cq0 - cq1)
    pref1 = cost[1] < cost[0]
    if pref1 != (preg[1] * pn * v < fix[0] - fix[1] + v * (cq[0] - cq[1])):
        bad += 1
check("L5e (c) the region minimizing (1 + p^reg) pi n + c-hat^Q(iota-bar) + (F^tr + nu^inv C^sw)/v is chosen; "
      "in-region beats transfer iff p^reg pi n v < (F^tr + nu^inv C^sw) + v[c-hat^Q(abroad) - c-hat^Q(in-region)]",
      bad == 0)

# ==============================================================================================
header("L6. Corollary cor:labor-pace (combined pace bound)")
# ==============================================================================================
c_ = 0.125
xhat = 1 + c_ / 2 - math.sqrt(c_ + c_ ** 2 / 4)
Teff = early["DE"]
bounds = {"change capacity": 12 * 40 / 320, "decision bandwidth": 12 * 1 * Teff / (xhat * 10),
          "engineering (Gamma = 6)": T_of_N(12, 6, 1.5, 0.48)}
eng_025 = T_of_N(12, 6, 1.5, 0.25)
print("     -> pace bounds (years): " + ", ".join(f"{k} {v:.2f}" for k, v in bounds.items()))
check("L6a example: 12 processes of 40 affected FTE each, change capacity 320 a year (1.5 years), bandwidth 10 with "
      "the 0.70 breakpoint and German wave length 0.75 (1.28 years), 6 engineers at e_mnt = 0.48 (10.1 years, ceiling "
      "12.5): talent binds; at e_mnt = 0.25 it still binds (4.16 years)",
      abs(xhat - 0.7035) < 1e-3 and abs(bounds["change capacity"] - 1.5) < 1e-12
      and abs(bounds["decision bandwidth"] - 1.279) < 2e-3 and max(bounds, key=bounds.get) == "engineering (Gamma = 6)"
      and abs(bounds["engineering (Gamma = 6)"] - 10.06) < 0.01 and 12 < 6 / 0.48
      and eng_025 > max(bounds["change capacity"], bounds["decision bandwidth"]))
# program cost with T_par replaced by T_eff: the square-root rule uses T_eff
n_eff = math.sqrt((12 / 2 + 0.5 / Teff) / 0.25)
check("L6b with a common wave length T^eff, prop:ext-waves(c) reads n* = sqrt((WN/2 + O_w/T^eff)/c^dr_2): German "
      "waves of 0.75 years give 5.16 processes per wave (5.29 at 0.5)", abs(n_eff - 5.164) < 1e-3)

n_fail = sum(1 for _, ok in RESULTS if not ok)
print("\n" + "=" * 78)
print(f"SUMMARY: {len(RESULTS) - n_fail}/{len(RESULTS)} checks passed" + ("" if n_fail == 0 else f"; {n_fail} FAILED"))
print("=" * 78)
sys.exit(0 if n_fail == 0 else 1)
