# Referee Panel A (Mathematical Economics & Optimal Control) — First Report

**Paper:** "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the
Limits of AI Automation" (A. B. S. Murthy, November 2026). Main 82pp + Supplement 57pp.

**Specialist:** Referee A2 (mathematical economics and optimal control), replacing
predecessor A who ran out of context after completing most diagnostics.

**Model identity disclosure (per MANIFEST):** All agents on this panel (Lead and teammates
A–F) are separate conversation contexts of the SAME large language model (GLM glm-5.3, via
DeepSeek Harness). We are NOT independent human experts and not independent model-family
evidence. All numeric/symbolic evidence below was produced by deterministic Python scripts
(seeded, archived under `/root/tmp/ruleof40/diagnostics/A/` [predecessor, inherited] and
`/root/tmp/ruleof40/diagnostics/A2/` [this referee]) whose outputs I checked; the LLM
supplied only interpretation.

**Source discipline:** Frozen sources per `MANIFEST.md`: main
`/root/Paper Review/sources/paper1_nov_2.pdf`, supplement `/root/Paper Review/sources/supplement_nov_2.pdf`;
page-indexed text under `/root/tmp/ruleof40/extraction/`. Printed page == PDF page index for both.
QUARANTINE (`/root/tmp/ruleof40/quarantine/`) not opened. Other panelists' reports
(C_accounting.md, D_reliability_controls.md, E_prior_art.md) not read.

---

## 0. Coverage of this report

- [x] §1 Inventory of the inherited 75 PASS checks (what they establish) — read scripts+outputs.
- [x] §2 HEADLINE: v′(s) investigation — the U-shape near the cap, what claims fail.
- [x] §3 Proof audit of supp S3/S4-era propositions (Props 4–9, Lemmas S3, S4).
- [x] §4 Strengths (verified correct).
- [x] §5 Open questions for the adversarial auditor.
- [x] §6 What verify_theory.py actually checks (author evidence, labeled as such).

## 0.1 Inheritance statement

Predecessor A completed: s1_symbolic.py (42 symbolic checks, all PASS), s2_numeric_frontier.py
(16 PASS), s3_budget_dynamics.py (11 PASS), s5_hjb.py (7 of 8 PASS; 1 FAIL is the seed of §2).
s4 (empirical panel) and s6 (if any) were NOT inherited — s5_hjb.py was the predecessor's last
work unit. I re-ran every inherited script before relying on it (§1.1). All findings below
carry the manifest finding format (locator, description, classification, evidence, strongest
author defense, verdict, affected conclusions, smallest correction + acceptance test).

(Report being written incrementally — sections appended after each work unit.)
---

## 1. Inventory of inherited checks (what they establish)

Predecessor A archived 4 scripts + outputs under `/root/tmp/ruleof40/diagnostics/A/`.
Totals: 42 (s1) + 16 (s2) + 11 (s3) + 8 (s5) = **77 checks, 76 PASS, 1 FAIL**
(the brief's "75 PASS" is a slight undercount; the precise figures are these).
Environment: python 3.12.3, numpy 2.5.2, scipy 1.18.1, sympy 1.14.0.

**s1_symbolic.py (42 PASS)** — closed-form identities rederived symbolically/numerically:
Lemma 1(a,c) σ↔Δ conversions and m*′(g); Lemma 2(b,c,e) eqs (5)–(7), tangency m*′(G+Δ*) = −X,
growth surplus Π = C_α(ℓy)^{1/(1−α)}; Lemma 3(a,d) dR*/ds and the Λ-threshold; Lemma 4 all
envelope derivatives (dR*/dX = g*, dR*/dk = −g*, dR*/dλ, dR*/dG = X−k, convexity in k, cross-partial);
Lemma 5(a,b,d,e) duration algebra and screening weight (20); Remark 2 taxed identities and
ψ_T schedule; Remark 3(b); Prop 4(a,c) Cournot algebra; Lemma S4(b) c* closed form; Prop S3(iv)
curvature; Remark S1(a).

**s2_numeric_frontier.py (16 PASS)** — frontier shape: decreasing & concave for k ≥ 0 across
α×k×G grid; non-convexity for k < 0 with interior peak (Remark S1(c) example: corner local max
S ≈ 0.486, interior local max S ≈ 0.595 at g ≈ 0.739, reproduced exactly); α-regime split of
m*″(G+) (finite/zero/−∞ at α = 1/2, <1/2, >1/2); brute-grid vs closed-form R* over 400 draws
incl. corners and caps; hypograph convexity; Rule-of-1000 example numbers.

**s3_budget_dynamics.py (11 PASS)** — Prop 1 integral and discrete budget bounds on 300/400
random spend paths; Corollary 1 example year-counts (1.8→1, 9.6→9, 5.0→5) and continuous-time
0.43/0.30 years; Prop S1 myopic-path decay (log-slope −3.662 ≤ −1/α); Prop S2 sharpness
(ratio→1 as Δ→0: 0.924, 0.995, 1.000, 1.000); Remark S1(b) budget under G_i < G; Corollary 2
bracket da − g*(k+dk)dk ≤ ΔR* ≤ da − g*(k)dk.

**s5_hjb.py (7 of 8 PASS)** — the Prop 2 / §S2.2 worked example solved independently by
backward shooting of the singular ODE from s = s̄: λ ≈ 0.0698 gives v0 = 10 (and 0.0808 gives 15);
static optimum g0 = 7.57%, σ0 = 10.71%, m0∘ = 24.29%, Gordon check exact; smaller roots of (19)
14.57/10.00/5.82/3.74/2.09/1.35 at r = 9.34/10/12/15/22/31% (all match printed 14.6/10.0/5.8/3.7/2.1/1.35);
HJB identity residual 2e-16; bounds (m0−kG)s/(r−G) ≤ v ≤ v0·s; u(s→0) → 9.9997 ≈ v0;
claimed weights/multiples reproduce: v′ = 9.08/7.25/5.39 vs printed 9.1/7.2/5.4; v/s = 9.41/8.10/6.47
vs printed 9.4/8.1/6.5.
**The one FAIL:** "v′(s) ≤ v(s)/s on the interior, and v′ falling with s". Investigated in §2.

---

## 2. HEADLINE INVESTIGATION: the v′(s) profile — the inherited FAIL, resolved

**Setup.** Prop 2 (main §3.6, printed p.20–21 = PDF pp.20–21) makes no claim about the shape of
v′. All shape claims are prose, in five places:
- **supp §S2.2, printed p.6 (lines 44–48)**: "With the share cap s̄ = 0.5 and v0 = 10, a numerical
  solution of (17) gives a growth weight v′(s) of 9.1, 7.2 and 5.4 at 1%, 10% and 50% of the cap,
  against revenue multiples v(s)/s of 9.4, 8.1 and 6.5. In this example the firm's own weight is
  close to, and below, its revenue multiple, **and it falls with share**."
- **main §3.6, printed p.21 (worked example paragraph, lines 42–45)**: "acts on a growth weight of
  9.1, 7.2 and 5.4 at 1%, 10% and 50% of its share cap, close to and below its revenue multiple,
  **and falling with share**; a multiple of 15 gives correspondingly higher weights. **In the
  example the weight lies below the revenue multiple at every share**, so the firm's own weight
  exceeds the screening weights of 2 to 3 when its revenue multiple is well above three".
- **main §3.5, printed p.20 (intuition after Corollary 3)**: "If the firm acts on its own decision
  weight X dyn(s) = v′(s) of Proposition 2, **which falls with share in the worked example there**,
  then the gains in (ii) and (iii), both proportional to X − k, are larger for a firm at small
  share".
- **main §7.4, printed p.63**: "For a firm **that acts on a decision weight that falls with share
  (Proposition 2, under its hypothesis (H))**, Corollary 3 orders the levers it controls by
  stage…". (Note: this attributes to Prop 2 a monotonicity claim Prop 2 does not state.)
- **main §1, printed p.3 (intro)**: "For a firm whose decision weight falls with share, fast
  growth gains most from automating the growth engine and retention and maturity from automating
  overhead." (Conditional phrasing.)

### 2.1 What is actually true (my evidence)

**(a) Analytic terminal behavior (derivation, A2).** Let ū := (m₀−kG)/(r−G) and suppose ū > k
(so the firm spends at every share; the paper itself notes at main p.21 that ū ≤ k gives the linear
solution v̂(s) = ūs and no spend). Where spend is positive, (17) is equivalent (supp printed p.16)
to the singular ODE v′(s) = Φ(v(s)/s, s) with Φ(u,s) = k + [((r−G)u − (m₀−kG))/C_α]^{1−α}/ℓ(s).
Seeking u = v/s = ū + a·t^q near t := s̄−s → 0, q = 1/(1−α): the LHS s·u′ = −s̄a q t^{q−1} → 0
(q > 1), while Φ − u → [k + ((r−G)a/C_α)^{1−α}(s̄/λ)] − ū; consistency forces the bracket to zero,
i.e.
  **a = C_α·[(λ/s̄)(ū−k)]^q/(r−G)  and  v′(s̄⁻) = ū = (m₀−kG)/(r−G).**
(The coefficient a is exactly the one the predecessor's s5_hjb.py used — it was right.) Moreover
v′(s) − ū = a·t^q − s̄a q·t^{q−1} ~ −s̄a q·t^{q−1} < 0, so **v′ approaches ū from BELOW,
strictly increasing**, with slope dv′/ds = s̄a q(q−1)t^{q−2} → +∞. Since v′(s) = v(s)/s + s·u′(s)
and u is decreasing (verified below), v′ < v(s)/s on the interior with equality only in the limits
s→0 (both → v₀) and s→s̄ (both → ū). Also (19) gives (r−G)(v₀−ū) = C_α(λ(v₀−k))^{1/(1−α)} > 0
whenever λ > 0, so **v₀ > ū always**. Consequence: for EVERY parameter draw with λ > 0 and
ū > k, v′ starts at v₀ > ū, falls, and must rise again on a terminal interval into ū from below;
min v′ < ū < v₀. **The U-shape is a structural property of the model, not an artifact of the
worked example.** ("v′ falls with share" is false for every admissible interior parameterization;
in the never-spend case ū ≤ k it is false too, being constant.)

**(b) Numerical confirmation, method 1 (inherited shooting, refined).** A2/s1_vprime_profile.py
re-solves the ODE by backward shooting (predecessor's method, shot started at t₀ = 10⁻⁶s̄ to keep
v′ = Φ noise-clean; shot matches v₀ = 10 at s→0 within 3×10⁻⁴). Worked example profile
(r=.10, G=.04, k=0, α=.3, m₀=.35, λ≈.0698, s̄=.5; v/s in parentheses):
1%: v′=9.08 (9.41); 5%: 7.95 (8.62); 10%: 7.25 (8.10); 25%: 6.18 (7.22); 50%: 5.39 (6.47);
60%: 5.23; 70%: 5.12; 75%: 5.09; **80%: 5.084 (minimum, ≈ 5.99)**; 85%: 5.10; 90%: 5.14;
95%: 5.25; 98%: 5.40; 99%: 5.50; 99.5%: 5.57; 99.9%: 5.70 → 5.833 = ū at the cap.
So: **v′ falls on (0, ≈0.80·s̄), rises on (≈0.80·s̄, s̄), and returns to v′(s̄⁻) = ū = 5.833**
— the predecessor's dying conjecture was correct. v′ exceeds its printed 50%-of-cap value (5.39)
again for s ≳ 97.5% of the cap. v′(s) ≤ v(s)/s everywhere on the interior (max gap = −0.035, i.e.
strictly below, with the gap → 0⁻ at both ends). Terminal asymptotics verified: v′−ū ~ −s̄a q t^{q−1}
and u−ū ~ a t^q hold to <10% relative error at t = 10⁻⁴s̄.

**(c) Numerical confirmation, method 2 (the author's own code).** I copied `solve_hjb` verbatim
from repo `code/verify_theory.py` (upwind DP, N=4000) and evaluated v′ = Φ(u,s) on its output
(A2/s2_author_grid.py). Identical profile: v′ = 9.07/7.23/5.39/5.09/5.08/5.10/5.14/5.25/5.40/
5.50/5.57/5.70/5.78 at 1/10/50/75/80/85/90/95/98/99/99.5/99.9/99.99% of the cap; min ≈ 5.084 at
≈80% of cap; v′(s̄⁻) → ū = 5.8333; v′ < v/s everywhere (max gap −0.035 over s ∈ (10⁻⁴, 0.98)s̄).
Two fully independent discretizations agree to 3 decimals. **The author's own numerical solution,
which supp §S2.2 cites, contains the U-turn — it was not looked at near the cap.**

### 2.2 The three printed numbers are right; the shape sentences are wrong where they generalize

The sampled values 9.1, 7.2, 5.4 (weights) and 9.4, 8.1, 6.5 (multiples) all reproduce (inherited
s5 PASS; both methods here). The errors are in the two generalizing clauses:

- **"falls with share"** — false globally: v′ rises on (≈0.80 s̄, s̄) back to ū. True only on the
  sampled range (1%–50%) and up to ≈80% of the cap.
- **"the weight lies below the revenue multiple at every share" (main §3.6, p.21)** — TRUE (verified
  on fine grids, both methods, strict on the open interval, equality approached only in the s→0
  and s→s̄ limits). This claim survives.
- The §3.5/§7.4 premise "v′ falls with share" is false as stated; the near-saturation weight is
  ū−k ≈ 5.83, not the minimum 5.08.

### 2.3 Finding, in the manifest format

1. **Locator:** supp §S2.2, printed p.6 (= PDF p.6), lines 44–48; main §3.6, printed p.21
   (= PDF p.21), lines 42–45; main §3.5 intuition, printed p.20 (= PDF p.20), lines 7–9;
   main §7.4, printed p.63 (= PDF p.63), lines 18–19; main §1, printed p.3 (= PDF p.3), lines 28–29.
2. **Claim:** the firm's decision weight v′(s) "falls with share" in the worked example (and, in
   §7.4, as a general property attributed to Prop 2 under (H)).
3. **Classification: demonstrated error** (prose characterization of the worked example's solution;
   no formal proposition is false — Prop 2 asserts no monotonicity; supp §S3's proof of Prop 2
   (printed pp. 15–16) and its "HJB as ODE" discussion assert nothing about v′'s shape).
4. **Evidence:** §2.1(a) analytic: for every draw with λ > 0 and ū > k, v′(s̄⁻) = ū, approached
   from below, strictly increasing on a terminal interval, with v′(s̄⁻) − ū ~ −s̄a q t^{q−1};
   v₀ > ū by (19). §2.1(b,c) numerical, two independent discretizations (min v′ = 5.084 at 80% of
   cap in the worked example; return to 5.833 = ū at the cap). Predecessor's s5 FAIL check
   reproduced and explained (its grid ran to 98% of the cap and caught the rising tail).
5. **Strongest author defense:** (i) All three *printed* numbers are correct, and they lie on the
   falling branch; "falls with share" could be read as describing the sampled range 1%–50%, the
   only range the example numbers cover. (ii) The economic conclusion the paper draws from the
   falling weight — gains proportional to X−k "larger for a firm at small share" (§3.5, p.20) —
   remains true in the weak sense: v′(s) < v₀ for every interior share (since v′ < v/s ≤ v₀), so
   both retention gains (X−k)dG and growth-engine gains are still maximized at small share.
   (iii) The §7.4 stage narrative does not depend solely on v′: the growth-engine lever's gain
   vanishes at saturation through h(s) → 0 (Cor 3(ii), Prop 9(c)) regardless of v′, which the
   paper itself proves. (iv) The claim appears only in prose; the formal apparatus (Prop 2,
   Cor 3, Prop 9) is untouched.
6. **Verdict: the error is demonstrated; the affected conclusions are narrowed, not overturned.**
   - "falls with share": **withdrawn/narrowed** to "falls with share up to roughly 80% of the cap
     in the worked example, then rises back to (m₀−kG)/(r−G) at the cap; the rise is generic."
   - "below the revenue multiple at every share" (main §3.6): **survives** (verified).
   - §3.5 intuition "gains in (ii) and (iii) larger at small share": **survives in the weak sense**
     (max at s→0), but the stated *reason* is false — the retention gain (X−k)dG is U-shaped and
     never vanishes: it dips from ≈9.1·dG to ≈5.08·dG at 80% of cap and rises back to ≈5.83·dG at
     saturation, i.e. near saturation the firm's own retention gain is ~64% of its small-share
     level. "Falling" is the wrong mental model for ranking retention vs overhead across stages;
     the correct statement is "retention gains do not vanish at saturation; they stay within a
     factor ≈1.8 of their small-share level."
   - §7.4 stage narrative: **narrowed.** Growth-engine lever: survives via the h(s) channel
     (σ*(s) strictly decreasing — verified numerically; gain xσ*(s) → 0 as s → s̄). Overhead and
     accountability floor: unaffected (fixed weight, no share dependence). But retention is
     misclassified as an early-stage lever: under the firm's own weight it is an *every-stage*
     lever (gain (v′(s)−k)dG ∈ [5.08, 10]·dG in the example), so near saturation the set of
     dominant levers is {overhead, accountability floor, **retention**}, not {overhead, floor}.
     The paper's own Cor 3(iii) already concedes the retention gain "does not depend on the firm's
     share" at a fixed weight, so the correction is to §7.4's sentence, not to any theorem.
   - Prop 9 (§7.5): unaffected — all its statements are at a fixed weight X; the ratio test needs
     no weight estimate, as the paper says (p.63).
   - Screening-weight comparison ("weight exceeds the screening weights of 2 to 3 when its
     revenue multiple does"): survives a fortiori (v′ ≥ min over share ≈ 5.08 > 3 in the example).
7. **Affected conclusions and magnitude:** modest. The false clause supports one intuition
   paragraph (§3.5), one premise sentence (§7.4) and one characterization of the worked example
   (§3.6, supp §S2.2). Quantitatively, in the worked example the weight's error against the truth
   is bounded by |v′(s) − min v′| ≤ 0.76 (5.83 vs 5.08) near the cap — a 15% misstatement of the
   retention-lever gain at near-saturation shares — and 0 at the sampled shares. No table, figure,
   calibration or theorem depends on v′ monotonicity (I checked the §7.3 central path uses fixed
   weights X ∈ {2.5, 5, 9}; §7.5/Prop 9 uses fixed X and the ratio test).
8. **Smallest correction:** in supp §S2.2 and main §3.6, replace "and it falls with share" with
   "it falls with share up to about 80% of the cap and then rises back to (m₀−kG)/(r−G), the
   never-spend multiple, at the cap"; in main §3.5/§7.4, replace "which falls with share in the
   worked example there" with "which is largest at small share" (true, since v′ < v/s ≤ v₀), and
   in §7.4 add retention to the near-saturation lever set or note the U-shape. **Decisive
   acceptance test:** add to verify_theory.py (whose grid already reaches the cap) the checks
   (i) v′(0.95 s̄) > v′(0.5 s̄) and v′(0.99 s̄) → (m₀−kG)/(r−G) within 1%, (ii) v′(s) ≤ v(s)/s on
   the whole grid, (iii) argmin v′ lies in the interior with min v′ < (m₀−kG)/(r−G). The revised
   claim passes iff all three hold; the current "falls with share" wording fails (i).

### 2.4 Genericity sweep

The analytic argument in §2.1(a) already establishes genericity: the terminal condition forces
v′(s̄⁻) = ū approached from below with v′ strictly increasing on a terminal interval whenever
ū > k, and v₀ > ū whenever λ > 0, so no admissible draw can have globally falling v′.

Numerical confirmation (A2/s3_fast_sweep.py, 12 draws, lighter tolerances: rtol 1e-9, shot from
t₀ = 10⁻⁵s̄, integrate to 10⁻⁵s̄; near-cap points with t < 10⁻⁴s̄ are noise-contaminated at this
tolerance because v′ = Φ(u,s) amplifies solver error by ∂Φ/∂u → ∞ as t → 0 — noted, and the
high-accuracy run in progress supersedes them). In **every** draw: min v′ < ū < v₀, and v′ at 99%
of the cap exceeds the minimum (the rise toward ū is already visible):

| draw | v₀ | ū | min v′ | at % cap | v′(99% cap) |
|---|---|---|---|---|---|
| worked example | 10.0 | 5.833 | 5.084 | 80.0 | 5.50 |
| v0=15 calibration | 15.0 | 5.833 | ≈4.6* | ~80* | 5.43 |
| v0=6 | 6.0 | 5.833 | 5.295 | ~80* | 5.80 |
| r=22% (v0≈2.1) | 2.1 | 1.944 | 1.767 | ~80* | 1.92 |
| α=0.25 | 10.0 | 5.833 | 4.978 | 83.6 | 5.34 |
| α=0.45 | 10.0 | 5.833 | ≈5.2* | ~80* | 5.77 |
| α=0.7 | 10.0 | 5.833 | (shot inaccurate at light tol) | — | 5.77 |
| k=0.05 | 10.0 | 5.800 | 5.055 | 80.0 | 5.47 |
| m0=0.25 | 10.0 | 4.167 | 3.541 | 79.7 | 3.88 |
| G=0.08 fast market | 10.0 | 5.000 | ≈2.8* | ~80* | 4.68 |
| s̄=0.25 tight cap | 10.0 | 5.833 | 5.084 | 80.0 | 5.50 |
| r=9.34% (v0≈14.6) | 14.6 | 6.554 | 5.591 | 79.7 | 6.11 |

(*) entries affected by near-cap noise at light tolerance; the *qualitative* pattern (dip below ū
around 79–84% of the cap, rise toward ū thereafter) is unambiguous in all draws. The argmin
location is remarkably stable across draws (79–84% of the cap in the clean ones). The s̄ = 0.25
draw is numerically identical to the worked example — a useful incidental check of scale
invariance in s̄ (the model only sees s/s̄).

The high-accuracy sweep (A2/s1_vprime_profile.py, rtol 1e-11, 13 shots, checks B1–B4: min v′ < ū
in every draw, rising terminal tail in every draw, v′ ≤ v/s in every draw, shot matches v₀) was
still running at report time on a loaded machine; its output will be archived next to this report
as s1_output.txt and supersedes the table's starred entries wherever they differ. The analytic
result does not depend on it.

---

## 3. Proof audit of the supplementary proofs (S3, printed pp. 10–25; S4, p. 26; S8, p. 49)

I read the complete proofs of every item listed in my brief and re-derived the key algebra;
symbolic/numeric cross-references are to the inherited checks (§1) and my own derivations.

**Lemma S1, Lemma 1, Lemma 2, Remarks S2–S4 (supp pp. 10–12):** verified correct. The Lemma S1(c)
non-convexity example (S(G) ≈ 0.486 corner local max; interior local max S ≈ 0.595 at g ≈ 0.739)
reproduces exactly (s2). The α-regime trichotomy of m*″(G+) (β > 2 / = 2 / < 2) is correct
(s2: −2κ at α = 1/2; 0 at α = 0.3; → −∞ at α = 0.7). Lemma 2(b) tangency, (5)–(7), FOC/SOC and
the y ≤ 0 corner case all check (s1 L2b, L2c; s2 brute-grid match over 400 draws incl. corners).

**Lemma 3 and Lemma 3(d) threshold (supp pp. 12–13):** verified; dR*/ds = −(X−k)⁺Δ*/(s̄−s) (s1 L3a),
Λ threshold and the Δ*, σ* identities at threshold (s1 L3d).

**Prop S1 (myopic path), Prop 1 (budget), Prop S2 (sharpness), Corollaries 1–2 (supp pp. 13–14):**
verified; the logistic transform and the "only place (1) is used" remark are correct; the discrete
budget (12) and its ln(1+·) accounting check; s3 reproduces all example numbers (1.81→1, 9.65→9,
5.01→5 years; 0.43/0.30 continuous) and the sharpness ratios → 1.

**Lemma 4 (envelope, supp p. 14):** all five derivatives, convexity in k and λ, and the
cross-partial verified symbolically (s1). One subtlety I checked: differentiability of y⁺^{1/(1−α)}
at y = 0 holds because 1/(1−α) > 1 ✓ (the proof says exactly this).

**Corollary 3 (supp p. 14–15):** (i)–(v) verified. (ii)'s exact forms Π[(1+x)^{α/(1−α)}−1] (spend
efficiency) and Π[(1+x_λ)^{1/(1−α)}−1] (demand pull) and the 1/α unit conversion all check against
Lemma 2(e) and (6). (iii) reduces to Remark S1(b) ✓. (iv) uses Lemma S2(a) and Prop 4(b) ✓.

**Proposition 2 (supp pp. 15–16):** the proof is sound and honest about its own limits. (a)
homogeneity and bounds ✓ (s5 reproduced both bounds). (b) the verification argument (supersolution
inequality (S3) + attainment under (H)) is standard and correctly executed. (c) the Rule-of-X
reading ✓ (s5 HJB identity residual 2e-16). (d) the root analysis: H(0) < 0 requires k ≥ 0 (noted
in Remark S1(c), which handles k < 0 separately); simple-root ⟹ g◦ < r ✓; v0 = m◦/(r−g◦) ✓ (s5
Gordon check); upper bound v ≤ v0 s via the supersolution v0 s ✓; lower bound via constant policy
and monotone convergence ✓; marginal-q limit v̂′ → v0 ✓ (s5: u(s→0) = 9.9997). (e) no-root case ✓.
The "HJB as ODE" discussion (p. 16) is correct — I independently verified both singular-point
analyses: at s = 0, ∂Φ/∂u = (r−G)/∆◦ > 1 (I recomputed: 1.680 for the worked example), so
u − v0 ∝ s^{(r−G)/∆◦−1} is a one-parameter family and the small-share limit alone does not pin
the solution down; at s = s̄ my §2.1(a) analysis confirms the paper's statement that a proof of (H)
"would have to select the solution through the terminal singular point" — and characterizes what
any such solution must look like near s̄ (v′ ↑ ū from below). The paper's candor here ("we have not
done this") is appropriate. **No missing hypothesis found in Prop 2 itself.** All corollaries of
the shape of v′ are confined to prose (§2 above).

**Lemma 5 (supp p. 16):** (a)–(e) verified symbolically (s1 L5a,b,d,e). The exponential-family
identity dD/d ln η = Var_w(t) checks. (c)'s monotonicity-in-θ derivative: I re-derived the sign —
correct, including the m = m̄ boundary case.

**Proposition 3, Prop S3(iv)–(v) (supp pp. 17–18):** verified. The envelope argument (iii), the
slope min{ξ, 0} of Ψ on the chosen segment, the observational-equivalence construction (inverting
(5) to build a firm with elasticity α′ that chooses the same point — I checked the construction:
ℓ′(∆) = ∆^{1−α}(α′y′)^{−α} indeed gives σ* = α′y′∆ ≤ y′(g_hi−G)), and the (S2) covariance
decomposition all check. s1 PS3iv verified the curvature identity m*″(gc) = −(1−α)y/(αΔ*).

**Proposition 4 (supp pp. 18–19; statement main pp. 25–26):** verified in full. (a) The
own-vs-rent equivalence via integration by parts requires monotone output paths — stated and
satisfied by the equilibrium (output grows at G) ✓. The simultaneous-entry free-entry convention
(n* = largest n with π_n ≥ F, i.e., n* = ⌊N_F⌋−1) is the standard integer-entry logic and matches
the Mankiw–Whinston citation; the statement carries "Assume N_F ≥ 2" so n* ≥ 1 ✓. The Lerner bound
0 < L_{n*} < (A−ĉ)/[ĉ(N_F−1)] ✓ (I checked A + n*ĉ > ĉ⌊N_F⌋). (b) limits as F → 0 ✓. (c) scarce
input: w_n = A−ĉ−BZ(n+1)/n > 0 for every n ≥ 1 under Z < (A−ĉ)/(2B) ✓ (n/(n+1) ≥ 1/2); P = A−BZ
independent of n ✓; net per-firm profit BZ²/n²·e^{Gt} ✓ (s1 P4c); n* = ⌊Z√(B/F̂)⌋ with the stated
"Assume Z√(B/F̂) ≥ 1" ✓; input owner's margins and the ρ → 1−ĉ/(A−BZ) limit ✓. (d) the hypothesis
"u/P ≥ cc+f+a_min+c_full at the limit price" IS stated in the proposition (main p.26), and the
algebra XG + (r−G)(k+k_a) + ρ ≤ 1−cc−f−a_min−c_full + XG − G(k+k_a) = pre-tax Rmax with capital
k+k_a checks exactly. The intuition-page numbers (ka = 0.10/0.05 = 2 giving (r−G)ka = 10 points)
check.

**Lemma S2, Remark 1, Remark S7, Remark 2, Corollary 4 (supp pp. 19–20):** verified. Remark 2's
tax substitution (m̃0 = (1−τ)m0 − (1−ψ)τδ_K k, k̃ = (1−ψτ)k, λ̃ = (1−τ)^{−α}λ) is exact (s1 R2
checks; ψ_T schedule reproduces: 0.796, 0.532). Corollary 4(a) R∞ ≤ Rmax iff C′ ≥ cc+f+a_min+c_full
✓; (c) the X-improving-at-saturation equivalence and the program-max argument ✓.

**Proposition 5 (supp pp. 20–21; statement main pp. 29–30):** verified. (a) the beta-factor
formula Po(D) = p^cc + (1−p^cc)∏_j[p^cm_j^{n_oj} + (1−p^cm_j)p_j^{n_oj}] and its monotonicities ✓
(strict decrease in depth per used type; ≥ common-mode bound). (b) admissibility iff Po(D) ≤ P̄o
with P̄o = 1−(1−π̄)^{1/No} ✓ (algebra checked); the "no design using only types in J is
admissible while the common-mode bound is at or above P̄o" implication is proved strictly ✓.
(c) the constrained-minimum floor (28): existence via finiteness of cheap admissible designs ✓;
"inadmissible designs are excluded whatever their cost" is the definition, not a trade-off ✓.
(d) Scale: the admissible set is S-free ✓; the minimized floor is nonincreasing in S ✓; the limit
is ∑_o ω_o L_onm·[p^cc(θ̄) + (1−p^cc(θ̄))∏_{j∈J} p^cm_j(θ̄)] with θ̄ = max Θ ✓ — I checked both
halves: the lower bound (every admissible D has Po(D) ≥ bracket(θ̄), using unused types contribute
factor 1 and p_j ≤ 1) and the upper bound (raise θ to θ̄, add layers of every type in J — neither
step raises any Po(D) by (a) — then F_D/S → 0 and Po(D) → bracket + ε) ✓. The statement's
"min_θ" over the bracket is exactly the bracket at θ̄ since both probabilities are nonincreasing
in θ ✓.

**Lemma S4 (supp p. 21 proof; statement supp p. 49, §S8):** verified. (a) maintenance flow
r/(e^{rT}−1) ✓. (b) security: c* = c_eff ln(c^inc/c_eff), C(c*) = c_eff[1+ln(c^inc/c_eff)],
c* ≤ c^inc/e via ln x ≤ x/e, and the (c0/Lsec)(1+Lsec+ln ξ^exp) form ✓ (s1 LS4b). (c) the
review-proof error rate ū = ε^o[χ+(1−χ)(1−d^o)^{n_r}] + ε^h[χ+(1−χ)(1−d^h)^{n_r}], its limit
χ(ε^o+ε^h), and the depth-existence iff χ(ε^o+ε^h) < ε̄ ✓; the "whatever units are reviewed" lower
bound (unreviewed units are worse) ✓. (d) E min{Y, Ȳ} for Pareto tails, all three regimes ✓ (I
re-derived the integral). (e) common-mode provider events: the ν^cm thinning (outages + unstopped
regressions), the containment cost T_con[x + x²/(2Y_fb)], the H_cm = ∑w²_m single-provider worst
case via ∑w² ≤ (∑w)² ✓.

**Proposition 6 (supp pp. 21–22; statement main pp. 32–33):** verified. Wave counting n(t) =
⌊(t−T_emb)/T_par⌋+1 for t ≥ T_emb ✓ used consistently. (a) monotonicity via set inclusion ✓
(the finiteness argument making sup a max is stated). (b) n̄ definition and A_t = A_∞ from
t ≥ T_emb + (n̄−1)T_par ✓ (n̄ well-defined since Z_n contains every subset iff P ∈ Z_n ✓). (c)
speed limit: summing wave constraints gives ∑_p c^p_i ≤ n(t)Γ_i ✓; identical-uses n_cap = min⌊Γ_i/c_i⌋ ✓;
the date bound T_emb + (⌈N/n_cap⌉−1)T_par ≥ max_i N c_i T_par/Γ_i ✓ (uses T_emb ≥ T_par and
n_cap ≤ Γ_i/c_i — both available). (d) knapsack bound: the hypothesis "each δϑ_p changes only m0
and G" is stated ✓; the indicator vector of Z ∈ Z_n(t) is feasible for the LP defining V_i(n(t)Γ_i)
by (c) ✓; LP value concave, piecewise linear, nondecreasing in the RHS ✓; the greedy
exchange argument for the decreasing ΔR^p/c^p_i order ✓.

**Proposition 7 (supp pp. 22–24; statement main pp. 33–34):** verified. The three observations
(revert anytime; the uniform-clock transformation; primitive independent shares) are each sound;
I checked (ii) in detail: with freezes of T_frz calendar per reorganization arriving at rate ν_R
in program time, program time u ↔ calendar u + T_frz N^R(u), so disruption exposure per program
time is ν_D(1+ν_R T_frz) and a flight survives with exp{−ν_D(1+ν_R T_frz)T_emb} ✓; the calendar-rate
conversion ν^cal = ν_R/(1+ν_R T_frz) in Definition 4(b) matches ✓. (a) upper bound via raising
shares to one inside B ✓. (b) all five comparative statics via explicit couplings (coin-flip
thinning for ϖ; superposed Poisson for ν_D; freeze transformation) — standard and correctly
executed. (c) E|Z^e_t| ≤ p_emb n_cap n(t_R) with equality construction when N ≥ n_cap n(t_R) ✓ (I
checked the wave-filling arithmetic); the score bound with E∑b^p ≤ b̄ p_emb n_cap n(t_R) using
independence of first-embedding timing and b^p ✓, and the "reverting and re-migrating cannot
raise the share" point ✓. (d) retry plan: geometric number of attempts, a.s. embedding, bounded
convergence ✓; the final convergence R̄_X(t) → R^att_X(∞) as capacities grow ✓ (I checked the
coupling: superposing rate-ν_D on the extra calendar flight reproduces the longer-flight model).
(e) fluid limit (i)–(iii) ✓ (the available-mass recursions check; the ν_D = 0 case's shortfall
bound < c_w ✓). **(f) Random freezes:** the exact survival probability
exp{−ν_D T_emb − ν_R T_emb(1−e^{−ν_D T_frz})} is correct for the stated model — it is
E[e^{−ν_D(T_emb + T_frz N)}] with N ~ Poisson(ν_R T_emb) — and the claimed inequality "at least
the uniform-clock value" follows from 1−e^{−x} ≤ x ✓. The counterexample showing the uniform-clock
bounds can fail at finite dates (T_emb = T_par = 1, ϖ = 1, ν_D = 0, ν_R = 0.5, T_frz = 2, t = 1.5:
uniform clock gives t_R = 0.75 < T_emb hence bound 0, while with probability e^{−0.5} ≈ 0.61 no
freeze occurs and the program embeds by calendar time 1) ✓ verified. This is a well-constructed
result: the assumption (uniform clock) is shown conservative, not just convenient.

**Lemma S3 (supp p. 24):** verified — concavity of E m*(g; ϑ_t) as an average of concave
extended-valued functions, the affine case, and the flexibility bound Xg + m_tE(g) ≤ E R*_X(ϑ_t)
✓. This is the "value of flexibility" result (the expected frontier exceeds the frontier at the
expectation), correctly proved.

**Proposition 8 (supp p. 26; statement main pp. 48–49):** verified. (a) the decomposition and the
ln-identity ✓. (b) separation under the stated hypothesis ("acquisitions leave the growth
technology of the businesses already owned unchanged" — stated) ✓; bang-bang in g_acq ✓.
(c) financing ✓. (d) NRR: a = (S_sub/S)(NRR−1) + (1−S_sub/S)γ_ns, G_i = ln(1+a), the [ln NRR, 0]
bracket ✓. (e) fresh budgets: per-business bound (X−k)[ln(s̄_b/s_b) + (G−G_i,b)T] — I verified the
bracket is automatically nonnegative (it equals ∫(g−G_i)dt ≥ 0 since g ≥ G_i pointwise), so "each
acquisition adds a nonnegative term" holds under X ≥ k ✓; the same-market caveat is stated ✓.
(f) treadmill: g_acq = g + d^org, score falls by k_acq per unit of decay ✓.

**Proposition 9 (supp p. 25; statement main p. 64):** verified. The first-order lever algebra
(xσ*, xσ*/α, xa, x(1−ε_p)c_h), the switch weights X0‡ = k + a^{1−α}/(αℓ) and k + (αa)^{1−α}/(αℓ)
✓ (I re-derived both iff-conditions), the ratio form (X−k)/(X̂−k) > (a/σ̂)^{1−α} ✓, (c) the
h(s)^{1/(1−α)} headroom factor and the (a/σ*)^{1−α} crossover ✓, (e) the exact (X−k)ΔG − D ✓,
(f) the screening-weight comparison ✓.

**Remark S11 (supp p. 25):** verified, including both threshold formulas and their numeric values
(0.165/0.495 at ψ=1; 0.333/0.735 at ψ=0, τ=0.18).

### 3.1 Findings from the proof audit (other than §2)

**Finding A2-2 (minor, missing hypothesis).** **Locator:** main §7.2, printed p.58 (≈ PDF p.58),
parenthetical: "(This applies Proposition 4(d) after tax: with profits and rents taxed at τ and
growth capital deducted at ψ, its bound is the after-tax Rmax of Corollary 4 with capital k + ka.)"
**Description:** the after-tax version of the Prop 4(d) ceiling is asserted to be Corollary 4's
Rmax evaluated at capital k + ka (a single ψ for both). **Classification:** missing hypothesis /
minor presentation issue. **Evidence:** under Assumption 6 (main p.25) customer-acquisition spend
is *expensed when incurred*, so its after-tax deduction is immediate (effective shield 1, i.e.,
its flow cost enters at (1−τ)), whereas plugging ka into Cor 4's Rmax charges it at (1−ψτ). My
re-derivation: the input owner's after-tax limit score is bounded by
XG + (1−τ)(1−cc−f−a_min−c_full) − (1−ψτ)kG − (1−τ)k_a G = "Rmax with capital k+k_a" + k_a G τ(1−ψ),
which EXCEEDS the claimed bound whenever k_a > 0 and ψ < 1. Magnitude: in the p.26 illustration
(k_a = 0.10/0.05 = 2, G = 0.05, τ = 0.18, ψ = 0.532) the slack is 0.84 points of score; in the
§7.2 application as stated (k = 0.5, no customer capital, k_a = 0) it is exactly zero, and the
quoted "central margin term plus 2.5 to 3 points" checks out (G(1−(1−ψτ)k)·100 = 2.66–2.74).
**Strongest author defense:** in the numerical use k_a = 0, so the parenthetical is exact there;
and one may read "growth capital deducted at ψ" as applying to k only. **Verdict: survives as
applied; the general parenthetical needs a one-line qualification** (customer capital expensed
under Assumption 6 earns a full deduction, so charge k_a at ψ = 1 — the ceiling is then slightly
higher, by k_a G τ(1−ψ), which weakens, not strengthens, the "100 out of reach" claim by <1 point).
**Smallest correction:** add "with k_a expensed (full deduction), the bound is Rmax with k at ψ and
k_a at ψ = 1" or restrict the parenthetical to k_a = 0. **Acceptance test:** recompute the §7.2
ceiling with k_a = 2: the corrected ceiling exceeds the stated one by 0.84 points; both remain
far below 100, so no conclusion changes.

No other proof in the audited range needs a hypothesis its statement omits. In particular I
checked: Prop 4(b) "N_F ≥ 2" ✓ stated; Prop 4(c) "Z√(B/F̂) ≥ 1" ✓ stated; Prop 4(d) "u/P ≥ floors"
✓ stated; Prop 6(d) "changes only m0 and G" ✓ stated; Prop 7(c) equality condition "N ≥ n_cap n(t_R)"
✓ stated; Prop 8(b) no-interaction hypothesis ✓ stated; Cor 3 fixed-weight caveat ✓ stated ("with
the weight X held fixed").

---

## 4. Strengths (independently verified correct)

1. **The static theory (Lemmas 1–4, Props 1, 3, 9, Cor 1–3)** is verified in full — 75+ independent
   symbolic/numeric checks (s1–s3), including frontier concavity, the (5)–(7) closed forms, all
   envelope derivatives, the budget arithmetic and its sharpness, and the non-convexity example.
2. **The worked example §S2.2 reproduces to the last printed digit** (λ = 0.0698/0.0808; static
   optima; the six smaller roots of (19) across r; the three weight/multiple pairs), and the HJB
   identity holds to machine precision along my independent solution (residual 2×10⁻¹⁶).
3. **Prop 2's verification-argument structure is sound and honestly labeled**: the paper proves
   what it can (homogeneity, bounds, small-share limit, no-root case), states (H) as an unproved
   hypothesis, says so twice (main p.21, supp p.16), and supplies numerical evidence for (H) at
   the worked-example parameters. My s5/A2 work independently confirms (H)'s numerical solution
   from both ends: the backward shot from the terminal singular point matches v0 at s→0 to 3×10⁻⁴,
   and the author's DP grid and my shooting agree everywhere to 3 decimals.
4. **The two-ends singular-point analysis in supp p.16 is correct** (I re-derived both: the s→0
   exponent (r−G)/∆◦−1 with ∂Φ/∂u = (r−G)/∆◦ = 1.68 in the example, and — my addition — the
   s→s̄ balance that pins the expansion coefficient a = C_α[(λ/s̄)(ū−k)]^q/(r−G) and forces
   v′(s̄⁻) = ū).
5. **The competition results (Prop 4, Cor 4)** are correct with all hypotheses on display; the
   scarce-input and full-cost-bound chains check line by line, and the after-tax extension
   (Remark 2) is an exact substitution.
6. **The program-clock results (Props 6–7, Lemma S3)** are a clean, self-consistent block: the
   wave-counting, knapsack bound and its concavity, all five coupling arguments, the fluid limit,
   and the random-freezes result — whose exact survival formula and conservativeness inequality I
   verified, including the instructive counterexample where the uniform-clock bound fails at
   finite dates.
7. **The reliability block (Prop 5, Lemma S4)** is mathematically sound (beta-factor common-cause
   model, admissibility algebra, the scale limit's two-sided argument, Pareto-tail expectations,
   provider-event thinning) — this referee checked the mathematics, not the auditing-standard
   interpretation (panel members C/D own that).
8. **verify_theory.py is genuine and strong author evidence** (§6): 26 sections, ~150+ checks,
   symbolic (sympy, 50-digit spot checks) plus numeric, that rederive essentially every closed
   form in the paper. Every check I cross-examined (15a–15m, 3j–3m) does what it claims.

---

## 5. Open questions for the adversarial auditor

1. **(H) remains unproved** — the paper says so. My terminal-singularity analysis (§2.1(a)) shows
   what any proof must deliver: existence of a bounded C¹ solution on (0, s̄) passing through
   (s̄, ū s̄) with the a-coefficient expansion, matching v0 at the other end. The two numerical
   methods agree, but the paper's conditional phrasing ("Every statement … conditional on (H)")
   is load-bearing and the auditor should not let prose forget it (§7.4's "under its hypothesis (H)"
   is correct; check every other v′-dependent sentence for the same qualifier).
2. **v′(s) < v(s)/s is verified, not proved.** The "below the revenue multiple at every share"
   claim (main p.21) is true in every draw I computed (equivalently: the revenue multiple v(s)/s
   is strictly decreasing), but neither I nor the paper has a proof. If it is provable (e.g., via
   a comparison argument on the ODE), the paper should say "verified numerically" or prove it;
   as written it is an example-level claim, which is how it is labeled ("In the example…").
3. **Does anything else in the paper quietly use monotonicity of v′?** I traced §3.5 intuition,
   §3.6, §7.4, §7.5, §8.1 and the intro; §7.5/Prop 9 are fixed-weight and clean. The auditor
   should double-check the companion paper's "playbook by position" (not in evidence here) does
   not inherit the "falls with share" premise.
4. **Where exactly does the retention lever rank near saturation?** With the U-shaped weight,
   near-saturation retention gains are (ū−k)dG ≈ 5.83·dG vs overhead cuts xa: the §7.4 stage
   sentence's ranking is parameter-dependent there. The paper concedes "which comes first at a
   given position also depends on the weight the owner acts on" — the auditor may ask for the
   U-shape to be reflected in Table 7's discussion.
5. **The ψ-vs-expensed customer capital point (Finding A2-2)** deserves a one-line fix; the
   auditor should confirm no table uses k_a > 0 with the common-ψ Rmax.
6. **Model identity reminder:** all panel members are contexts of the same LLM (glm-5.3); my
   numeric evidence is deterministic and archived, but the panel's "independent" judgments are
   not model-family-independent evidence.

---

## 6. What code/verify_theory.py actually checks (AUTHOR EVIDENCE — not my verification)

Scope: repo `code/verify_theory.py` (3082 lines, 26 headed sections). I read the structure and
section 15 in full; I did not re-run the whole file (the Lead's repo clone is available; the
author's printed numbers that I re-derived independently all reproduce, s1–s5 + A2).

What it checks (by section): 1–4 frontier, timing, score, saturation/myopic; 5 budget, sharpness,
transience; 6 envelope + capital-for-labor; 7 valuation lemmas; 8 free entry; 9–10 price channels,
AI shifts; 11 taxes + ceiling; 12 figure parameters; 13 heterogeneous firms; 14 pass-through;
**15 dynamic optimality (Prop 2)**; 16 screening weight; 17 assumptions; 18 automation priorities;
19 industry; 20 full-cost ceiling; 21 attainable frontier; 22 expected frontier; 23 economic
profit; 24 ownership; 25 tax/accountability; 26 Lemma S4/Prop 5 (full-cost + accountability);
28 "revision v2 theory fixes".

Section 15 (the Prop 2 evidence, checks 15a–15m): 15a–15d symbolic HJB reduction, Gordon identity,
root derivative; 15e 500-draw root sweep (g◦ < r, Gordon, simplicity); 15f the worked-example
calibration (λ, g0, σ0, m0∘ for v0 = 10 and 15); 15g–15m the numerical solution by upwind DP on a
4000-point grid that REACHES the cap: 15g the three sampled weights/multiples, 15h grid convergence,
15i bounds, 15j small-share limits, 15k the HJB identity on s ∈ (10⁻⁵, 0.45) — i.e. only BELOW 90%
of the cap — 15l closed-loop payoff match from s0 = 0.005 and 0.05, 15m the constant-policy lower
bound.

**What it does NOT check (and how this relates to §2):** (i) no check of v′ monotonicity or of
"falls with share"; (ii) no check of v′(s) ≤ v(s)/s beyond the three sampled shares — and the HJB
identity itself is verified only up to 0.45 (= 90% of the cap), leaving the U-turn region
(80–100% of the cap) outside every shape check; (iii) no check near the cap at all beyond the
terminal bound 15i. The author's grid contains the U-shape (I ran the author's own `solve_hjb`:
min v′ = 5.084 at 80% of cap, rising to 5.78 at 99.99%, §2.1(c)) — the claims about the profile
simply were never tested against it. This is consistent with the error's character: correct
sampled numbers, untested generalization. Label: author evidence; my independent verifications
are in §1–§2 and /root/tmp/ruleof40/diagnostics/A2/.

*End of report (A2, mathematical economics and optimal control).*
