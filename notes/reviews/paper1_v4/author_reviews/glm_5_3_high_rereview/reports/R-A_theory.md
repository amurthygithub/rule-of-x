# Re-review report — Theory (referee A, mathematical economics & optimal control)

**Round:** 2 (re-review of the 4 Nov build: main 87pp + supp 72pp; repo_v4 @ eb7537b, branch
review-round-3). Ground-truth sources per `/root/tmp/rereview/MANIFEST.md` (read in full first).

**Model-identity disclosure (required):** I am a separate conversation context of the same LLM
family as the Lead and the other panel members ("GLM 5.3 (high effort)" is how the author
addressed this panel; platform labels have been unstable). We are NOT independent human experts
and not independent model-family evidence. All numeric/symbolic evidence below is produced by
deterministic, seeded Python scripts archived under `/root/tmp/rereview/diag/rereview-theory/`,
whose outputs I checked; the LLM supplied only interpretation. No Lean compiler and no LaTeX are
available in this environment — Lean and .tex items are source-level audits only (recorded as
such where relevant).

## Round-1 inheritance

My round-1 report (math-frontier / specialist A2) established: the decision weight v′(s) in the
Prop 2 worked example is U-shaped (min ≈ 5.08 at ~80% of the cap, rising back to
ū = (m₀−kG)/(r−G) = 5.833 at the cap) — a structural property, not an example artifact; the
"falls with share" claims were false while the sampled numbers 9.1/7.2/5.4 and "below the
revenue multiple at every share" were correct; plus a minor after-tax Prop 4(d) parenthetical
gap (customer capital expensed ⇒ charge k_a at full deduction, not (1−ψτ)). Round-1 scripts:
`/root/outputs/rule-of-40-review/diagnostics/A2/` (copies archived by the author under
`notes/reviews/paper1_v3/author_reviews/glm_5_3_high/`).

## Coverage skeleton

- [x] 1. ROW GLM-F1: the v′-shape fix (six sentences; new checks 15l–15p; acceptance-test dispute).
- [x] 2. ROWS GLM-M3 (after-tax Prop 4(d) wording), GLM-M15 (novelty rephrase), GLM-1
      ("below the multiple" qualifier), GLM-7 (after-tax reconciliation after Remark 5).
- [x] 3. PART B: (a) supp S4 Lean formalization fidelity audit (source-level only); (b) the 16
      "(H)" qualifiers; (c) git diff of theory tex 62e574b..eb7537b; (d) new abstract/summary
      box conditions; (e) ST-1 threshold audit (S10, Table S18, stored mc outputs).
- [x] 4. Findings register with severities; limitations (no Lean, no LaTeX).
- [x] 5. Summary message to Lead.

(Appended incrementally after every work unit.)

---

## 1. ROW GLM-F1 — the v′-shape fix (author: "Valid → Fixed"; six sentences; checks 15l–15p)

**Author's claim:** six sentences corrected (supp S2.2; main 3.5, 3.6, 7.4, 1, 9); new macros
\Vp*; verify_theory checks 15l–15p added; "the reviewer's acceptance tests were not used,
because they fail on the correct solution."

### 1.1 The six sentences, verified in the new PDFs

I found every v′-shape sentence in the 4 Nov build (grep for "falls with share", "U-shaped",
"rises back/toward", "highest at small share" over `/root/tmp/rereview/extraction/`) and read
each in context. All six corrections are present and match the true profile:

1. **supp §S2.2, printed p.6:** "the firm's own weight, v′(s) under (H), is close to, and below,
   its revenue multiple; it falls with share to a minimum of about 5.1 near 80% of the cap and
   then rises toward the never-spend multiple (m₀−kG)/(r−G) ≈ 5.8." ✓
2. **main §3.5 (intuition after Cor 3), printed p.21:** "which in the worked example there falls
   from 9.1 at 1% of the cap to about 5.1 near 80% and stays below its small-share values up to
   saturation, then the gains in (ii) and (iii)… are larger for a firm at small share, although
   near saturation the retention gain of (iii) is still about 56% of its small-share value." ✓
   (both clauses true — see 1.3 for the 56% nuance)
3. **main §3.6 (worked example), printed p.23:** "the weight falls to about 5.1 near 80% of the
   cap and then rises toward the never-spend multiple of 5.8… In the example the weight lies
   below the revenue multiple at every share." ✓ (the second clause is the round-1 "survives"
   claim, retained correctly)
4. **main §7.4, printed p.66–67:** "a decision weight that is highest at small share
   (Proposition 2, under its hypothesis (H))… once it is near saturation, overhead and the
   accountability floor do (lever 5), **while retention still raises the durable score by X−k a
   point (Proposition 9(a))**." ✓ — "highest at small share" is true (v′ < v/s ≤ v₀ on the
   interior), and the retention clause now states the durable gain correctly (Prop 9(a) does say
   a point of G_i raises R* and R∞ by X−k).
5. **main §1, printed p.3:** "For a firm whose decision weight is highest at small share, fast
   growth gains most from automating the growth engine and retention, and maturity from
   automating overhead, while retention still adds to the durable score near saturation." ✓
6. **main §9 (Conclusion), printed p.74:** "gains from the growth engine are transient and from
   retention durable, so the growth engine matters most where a firm has share to gain and
   overhead where it has little, while retention counts at every stage (Corollary 3)." ✓

Remaining "falls with share" instances in the new PDFs are all legitimately about R* (Lemma 3,
main pp. 21, 26 — proven, and verified in round 1) or about X_scr's duration (supp p.6), not
about v′. The protocol section (supp p.50, p.53) accurately describes the round-1 finding
("described as falling to a minimum near 80% of the share cap and then rising, with retention
still adding to the durable score near saturation").

### 1.2 Numerical re-verification (my own run, new repo's solver)

`/root/tmp/rereview/diag/rereview-theory/s1_f1_shape.py` runs the NEW repo's `solve_hjb`
(N=4000, copied verbatim to scratch) and computes v′ both ways — `np.gradient` (the author's
method in 15g–15p) and the exact Φ(v/s,s) from the ODE (my round-1 method). The two agree to 3
decimals. Output (`s1_f1_output.txt`):

| s/s̄ | v′ (grad) | v′ (Φ) | v/s |
|---|---|---|---|
| 0.01 | 9.077 | 9.075 | 9.409 |
| 0.10 | 7.244 | 7.239 | 8.092 |
| 0.50 | 5.393 | 5.388 | 6.473 |
| 0.80 | **5.084 (min, at 80.1%)** | 5.084 | 5.992 |
| 0.90 | 5.142 | 5.143 | 5.893 |
| 0.95 | 5.252 | 5.253 | 5.856 |
| 0.99 | 5.496 | 5.496 | 5.836 |
| 0.999 | 5.697 | 5.697 | 5.833 |
| 0.9999 | 5.781 | 5.781 | 5.833 |

- The printed numbers are unchanged and correct: 9.1/7.2/5.4 (weights), 9.4/8.1/6.5 (multiples).
- "about 5.1 near 80% of the cap" ✓ (5.084 at 80.1%); "rises toward the never-spend multiple
  (m₀−kG)/(r−G) ≈ 5.8" ✓ (5.781 at 99.99% of cap, limit 5.8333).
- Macros `paper1/macros.tex:976–997` all check against the grid: VpMinTwo 5.08, VpMinAt 80,
  VpLimitTwo 5.83, VpSatLo 5.08, VpSatHi 5.70 (at 99.9%), VpNinetyNine 5.50, VpFourNines 5.78,
  VpGainShare 56. Also \KaSlack = 0.84 — the author adopted the exact magnitude from my round-1
  M3 finding (see §2.1 below). ✓

### 1.3 The acceptance-test dispute — the author is right; I concede

My round-1 report proposed: (i) v′(0.95·s̄) > v′(0.5·s̄); (ii) v′(0.99·s̄) within 1% of
(m₀−kG)/(r−G). **Both fail on the correct solution**: v′(0.95 s̄) = 5.252 < 5.393 = v′(0.5 s̄),
and v′(0.99 s̄) = 5.496 is 5.8% below 5.833. Worse, my own round-1 profile table contained the
contradicting data (5.25 at 95%; "exceeds its printed 50%-of-cap value again for s ≳ 97.5%") —
the acceptance test I wrote was inconsistent with my own computed table. The rise toward ū is
asymptotically slow (v′−ū ~ −C(s̄−s)^{α/(1−α)} = −C·t^{0.43}), so a passing test must go very
close to the cap. The author's replacements, check 15l (v′(0.99 s̄) > v′(0.5 s̄): 5.496 > 5.393,
PASS) and 15m (v′(0.9999 s̄) within 1% of 5.8333: 0.90%, PASS), are correctly calibrated and I
verify they pass on my own run too. 15n (interior minimum below the limit between 70% and 90% of
the cap; v′ < v/s everywhere on z ∈ (0.02, 0.9999), max gap −0.052) and 15o (retention gain
v′−k ≥ half its 1%-of-cap value from the minimum to 99.9% of cap — the minimum ratio is
5.084/9.077 = 56.0% ≥ 50%; growth spend σ* falls to 0.0006 < 0.1·σ*(1%) = 0.0092 by 95% of cap)
also pass. The code comment documents the correction explicitly ("with the acceptance tests as
the GLM issue log corrects them (0.99 and 0.9999 of the cap, not 0.95 and 0.99)"). I have no
disagreement: **the author's version of the tests is the right one, and the corrected sentences
pass it.**

Two small observations, not defects of the fix:
- **15l's margin is thin** (5.496 vs 5.393, a 2% gap; the crossover of v′(0.5 s̄) is at ≈97.5% of
  cap), so 15l is sensitive to grid refinement — but it passes at both N=4000 and in my Φ-based
  recomputation, and 15m/15n are the load-bearing checks anyway.
- **The "56%" nuance (editorial):** the new §3.5 sentence says "near saturation the retention
  gain of (iii) is still about 56% of its small-share value." The 56% is the ratio at the
  *dip* (v′−k at its minimum 5.084 vs its 1%-of-cap value 9.077 = 56.0%); *near saturation* the
  ratio is 63.7% (5.781/9.077), or 58.3% against the small-share limit v₀ = 10. As a lower
  bound the sentence is true at every share ("still at least about 56%"), and check 15o is
  phrased exactly that way ("at least half"); but as a point statement attached to "near
  saturation" it understates by ~8 points. The author's own issue log says "about 60%".
  **Editorial severity; suggested fix: "never falls below about 56% of its small-share value"
  or "is still about 64% of its 1%-of-cap value near saturation".**
- Cosmetic: the new verify_theory.py now has duplicate check labels (two checks named "15m" and
  two named "15n" — the old 15m/15n constant-policy and spend-ratio checks were not renumbered
  after the new 15l–15p block was inserted). Harmless, but the file's check names are no longer
  unique, which weakens log greppability. Also check 15k's HJB-identity mask still stops at
  s < 0.45 (the round-1 §6 observation); the near-cap region is now covered by 15l–15n instead,
  so the gap is functionally closed.

### 1.4 VERDICT GLM-F1: **resolved**

All six sentences match the true profile (verified against the new repo's own solver, two
derivative methods, and my exact-Φ recomputation); the sampled numbers are unchanged and
correct; the macros exist and are checked (15p); the acceptance tests were correctly
recalibrated by the author after my round-1 versions failed on the correct solution (I concede
this point explicitly); the retention-durable consequence now appears at all three sites
(§3.5, §7.4, §9) with the correct Prop 9(a) citation. One editorial residue (the 56%-vs-64%
phrasing in §3.5, p.21) and two cosmetic code notes; none affects any theorem or number.

---

## 2. ROWS GLM-M3, GLM-M15, GLM-1, GLM-7

### 2.1 GLM-M3 (after-tax Prop 4(d) parenthetical) — VERDICT: **resolved**

Author's claim: main 7.2 parenthetical now reads "customer acquisition is expensed and deducted
in full, so the bound is R_max with capital k, less (1−τ)k_a G; here k_a = 0."

**Verified in the new PDF:** main §7.2, printed p.61–62: "(This applies Proposition 4(d) after
tax: with profits and rents taxed at τ, growth capital deducted at ψ and customer acquisition,
which Assumption 6 expenses when incurred, deducted in full, its bound is the after-tax Rmax of
Corollary 4 with capital k, less (1 − τ)k_a G; here k_a = 0.)"

**Algebra check (my round-1 derivation, re-confirmed):** the input owner's after-tax limit score
is bounded by XG + (1−τ)(1−cc−f−a_min−c_full) − (1−ψτ)kG − (1−τ)k_a G, which is *exactly*
"[after-tax Rmax of Cor 4 with capital k] − (1−τ)k_a G" — the new sentence states my formula
correctly, with the right mechanism (Assumption 6 expensing ⇒ full deduction for customer
capital). The macro \KaSlack{0.84} is defined in `paper1/macros.tex:998` — the author also
computed the round-1 slack magnitude (0.84 points at k_a = 2, G = .05, τ = .18, ψ = .532) — but
does not use it in the text (dead macro; harmless, and the chosen "here k_a = 0" statement is
the cleaner fix). The applied numbers ("2.5 to 3 points") remain correct (G(1−(1−ψτ)k)·100 =
2.66–2.74). No residue.

### 2.2 GLM-M15 (novelty rephrase) — VERDICT: **resolved**

Author's claim: main 1 and 3 now say "a worked instance … of the classical non-identification".

**Verified:** main §1, printed p.6: "the results we believe are new are the score budget, the
firm's decision weight on growth and its relation to screening weights, **a worked instance, for
growth–margin frontiers, of the classical non-identification of technologies from chosen
points**, the accountability floor as a control standard…". Main §3, printed p.13: "…
**a worked instance of the classical non-identification of firm frontiers from chosen points,
with within-firm co-movement (Propositions 3 and S3)** …". The novelty list is now internally
consistent with §2's description of the result as classical. Resolved as claimed.

### 2.3 GLM-1 ("below the revenue multiple at every share" — verified, not proved) — VERDICT:
**agree with the author ("already handled"); no change needed**

Round-1 status: the sentence was already scoped "In the example" (main §3.6), and my round-1
report itself recorded that it "is an example-level claim, which is how it is labeled" (round-1
§5, open question 2). The new build keeps the scoping (main §3.6, printed p.23: "**In the
example** the weight lies below the revenue multiple at every share") **and adds numerical
codification**: verify_theory check 15n now tests max(v′ − v/s) < 0 over z ∈ (0.02, 0.9999) —
I re-ran it: max gap = −0.052 < 0, PASS. So the author's "Already handled" is accurate, and the
claim is now additionally machine-checked on the author's grid. Nothing further required.

### 2.4 GLM-7 (after-tax reconciliation after Remark 5) — VERDICT: **resolved**

Author's claim: main 3.11, after Remark 5: "the identities hold for the after-tax margin with
k read as (1−ψτ)k, the basis of Section 7."

**Verified in the new PDF:** main §3.11, printed pp.36–37: "Because (a), (b) and (d) are
identities **in m and k**, they also hold for the after-tax margin of Remark 2 with k read as
(1 − ψτ)k, the basis of Section 7."

**Algebra check:** Remark 5's parts (a), (b), (d) (printed p.36) are the identities
R_X = (X−k)g + e + rk with e = m + k(g−r); k[ROIC + (X/k − 1)g] = Xg + m with ROIC = (m+kg)/k;
and the valuation ratios V/S = k + e/(r−g), V/(kS) = (ROIC−g)/(r−g). Substituting the after-tax
FCF margin m̃ of Remark 2 and k̃ := (1−ψτ)k (Remark 2's exact effective capital coefficient,
verified in round 1): ẽ = m̃ + k̃(g−r), ROIC̃ = (m̃+k̃g)/k̃, and all three identities hold
verbatim with (m̃, k̃) — each is an identity in (m, k), so the substitution preserves it, with
the net weight correctly becoming X − k̃. I verified each by direct expansion. The sentence is
correct and the "basis of Section 7" cross-reference is accurate (§7's calibration is on the
after-tax cash basis, m = m₀ − (1−τ)σ − kg with k read as (1−ψτ)k per §7.3's anchor text).

---

## 3. PART B(b): the "(H)" qualifiers

**Author's claim:** 16 decision-weight statements now carry "under (H)", including Proposition 2's
title; the blanket sentence ("Every statement in this paper that a value-maximizing firm acts on
a weight equal to the marginal value of revenue is conditional on (H)") is retained.

**Verification.** I walked every decision-weight statement in the new main text (grep on
"marginal value of a dollar", "marginal q of revenue", "value-maximizing firm acts on", "the
firm's own weight", "decision weight", and "(H)"). The new build has 31 "(H)" occurrences;
distinct conditioned sites include: §1 intro ("Under a standard verification hypothesis
(Proposition 2)…", "the firm's own weight on growth under (H) is higher…", and the fixed
intro sentence "decision weight is highest at small share" now sits with the durable-retention
clause), §2.2 ("under its verification hypothesis (H), the marginal q of revenue of this
literature"), §2.7 roadmap ("under a stated verification hypothesis"), **Proposition 2's title —
now "Dynamic optimality: under (H), the firm's own growth weight is the marginal q of revenue"
(main §3.6, printed p.21) ✓**, the proposition statement and its closing blanket sentence
(printed p.22), the worked example (p.23 "under (H)"), the measurement implication (p.23),
§3.7 (p.24), §6 (p.47: "which for a value-maximizing firm is, under (H), the marginal value of
a dollar of revenue (Proposition 2)"), §7.3 and §7.4 ("under its hypothesis (H)", p.66),
§8.1 (twice, p.69), §8.3, and the limitations section. The count and coverage are consistent
with the "16 qualifiers" claim. Two code-facing notes: verify_theory check 15j still verifies
v′(s) → v₀ "within 0.01" at small s without conditioning — correct, since Prop 2(d)'s v(s)/s → v₀
is unconditional and only the v′ statement is (H)-conditional, and the paper's text (p.22) says
exactly that.

**Remnants found (minor, editorial):**
1. **§3.5 intuition, main printed p.21:** "If the firm acts on its own decision weight
   X dyn(s) = v′(s) of Proposition 2, which in the worked example there falls from 9.1 at 1% of
   the cap…" — no explicit "(H)", although its §7.4 parallel (p.66) reads "(Proposition 2, under
   its hypothesis (H))". The phrase "its own decision weight … of Proposition 2" presupposes the
   (H)-conditional identification. Defensible via inheritance from the now-qualified proposition
   title, but inconsistent with the §7.4 treatment. **Suggested fix: add ", under (H)," as in
   §7.4. Severity: editorial.**
2. **Remark 3(b), main printed p.36:** "When X is the firm's own weight X dyn of Proposition 2,
   qK is the marginal value of a dollar of invested capital" — same inheritance situation.
   Acceptable by reference; flag only for consistency.

**Response-documentation slip (not a paper defect):** the RESPONSE's GLM-7 row locates the new
after-tax reconciliation sentence "after Remark 5" — the main paper has no Remark 5 (its
value-based remark is **Remark 3**, printed p.36, and the reconciliation sentence follows it at
pp.36–37). The fix itself is present and correct; only the response's locator is wrong.

**Cosmetic defect introduced by the fix:** verify_theory.py now uses the labels 15l, 15m and
15n **twice each** (the new shape checks 15l–15p were inserted without renumbering the old
closed-loop "15l", constant-policy "15m" and spend-ratio "15n"). All checks still run; but the
paper's citation "checks 15g to 15m" (main §3.6, printed p.22, as evidence for (H)) no longer
identifies a unique set of checks. Suggested fix: renumber (e.g., old ones → 15r–15t) or cite by
content. Severity: editorial.

---

## 4. PART B(a): supp S4 — the Lean 4 formalization (SOURCE-LEVEL AUDIT ONLY)

**Hard limitation, recorded:** no Lean toolchain, no LaTeX in this environment. I audited the
Lean sources as text (statements, definitions, axiom discipline, docstrings) and cross-checked
them against the paper and supp S4's description. I could NOT verify that the code compiles, nor
that the `#print axioms` output is as claimed. Everything below is source-level evidence.

**Inventory** (`repo_v4/formal/RuleOfX/`, 10 files, 3065 lines): Defs, Frontier, Score,
Saturation, Envelope, Capital, Budget, BudgetCont, Imports, Axioms; plus `formal/Checks/`
(instances at paper-like values) and a README that maps every part to its Lean file.

**Axiom discipline (as documented):** `Imports.lean` is pure Mathlib (12 Mathlib imports, no
custom files). `Axioms.lean` runs `#print axioms` on **exactly 35 main theorems** — matching the
claim — with expected output "[propext, Classical.choice, Quot.sound]" and "nothing else (in
particular no sorryAx)". My source scan found **no `sorry`, no `admit`, no `axiom`, no
`native_decide`** in any of the ten files (202 theorem declarations total; the 35 main ones are
the Axioms.lean list). The README states the toolchain (Lean 4.35.0, Mathlib v4.35.0) and that
`lake build` prints the #print output. Unverifiable here, as recorded.

**Statement fidelity (spot-checked in depth):**
- The paper's **Lemma 2 cap-condition tightening is faithfully implemented**: `Score.lean`
  defines `σplus/Δplus` with `(X−k)₊` (the paper's stated convention), `gstar` uses `Δplus` so
  g* = G when X ≤ k; `prop_score_b` takes the cap as `(σstar : WithTop ℝ) ≤ σbar` (handles
  σ̄ = ∞) with `k < X`, encodes the binding-cap case (σ* = σ̄ → g* = ḡ) and the *left-derivative*
  tangency via `HasDerivWithinAt (Iic g*)`; `prop_score_c` proves the corner for X ≤ k with
  σplus = 0 and needs no cap — docstrings quote the paper text verbatim. The **paper text now
  carries the same tightening** (main §3.3, printed p.16: "assume that the financing cap does not
  bind, that is, σ* ≤ σ̄ with σ* given in (6) if X > k and **σ* = 0 if X ≤ k**", and Lemma 2(c)
  "This part does not need the cap condition"). ✓
- The **measurable-moving-intercept tightening is faithfully implemented**:
  `prop_budget_c_continuous_induced` takes `(m0 : ℝ → ℝ)` with `(hm0m : Measurable m0)`, and the
  fixed-intercept `prop_budget_a` takes `Measurable σ`, `Measurable m` — matching the paper's
  new Prop 1(a)/(c) wording ("any measurable spend path… any measurable margins…"; "(c) (Moving
  intercept.) If the margin intercept moves over time along a **measurable** path m0(t)",
  main §3.4, printed p.18). ✓
- **The induced share path** is constructed from the logistic formula (`induced`,
  `induced_isPath`) and the bounds are proved both for general Carathéodory paths (path as
  hypothesis) and for the constructed induced path. `cor_transient_b_optimum_induced`'s
  docstring honestly records the fixed-point condition between σ and its induced path as a
  hypothesis. This matches supp S4's "Readings" paragraph exactly.

**Supp S4's text vs the formalization:** accurate on every point I could check. "35 main
theorems" ✓ (counted); "none contains an unproved step… three axioms standard in Lean"
✓-as-documented; "What the check changed" states the two tightenings and they ARE in the paper ✓;
"What is not checked" (Cor 3(iv); numerical examples; everything after §3.5) is consistent with
the file inventory; "How it was produced and audited" discloses that the induced-path
construction and four comparative-statics links were added after the second audit and were not
audited a third time — an honest, disclosed limitation. The README's file table matches the
files' contents as far as I read them (Defs/Frontier/Score/BudgetCont checked in depth).

**Verdict: the formalization is real, carefully structured, and faithfully matched to the
(corrected) paper statements at source level. The two tightenings the formalization forced are
genuinely in the paper. I could not verify compilation or the kernel's axiom output — recorded
as an unchecked author claim, backed by an unusually clean source scan.**

One minor observation: supp S4 says the instances live at "α = 0.3, ℓ = 0.6, G = 0.10, k = 0.10,
m0 = 0.45, X ∈ {1, 2}, s̄ = 0.5" while the README's Checks table adds "λ = 1.2, s = 0.1" —
consistent (ℓ = λh = 1.2·0.5 = 0.6 ✓ with s = 0.1, h = 0.8? no: h(s) = 1 − 0.1/0.5 = 0.8,
λh = 0.96…; the README's ℓ = 0.6 must come from λ = 1.2, h = 0.5, i.e., s = 0.25 — a
trivial internal bookkeeping detail of the illustrative instances, not a paper claim).

---

## 5. PART B(c): theory-tex diff 62e574b..eb7537b

`git -C repo_v4 diff 62e574b..eb7537b -- sections/model.tex sections/appendix_proofs.tex
part2/proofs_core.tex`: model.tex 30 lines changed, appendix_proofs.tex 6, part2/proofs_core.tex
**unchanged**. I read every hunk. Contents:

- **model.tex (all documented fixes):** (1) §3 opening — the GLM-M15 novelty rephrase; (2) §3.1 —
  NEW sentence pointing to the Lean formalization ("machine-checked in Lean 4, except
  Corollary 3(iv) and the numerical examples"), matching supp S4; (3) Lemma 2 preamble — the cap
  condition tightening "σ* = 0 if X ≤ k"; (4) Prop 1(c) — "along a measurable path m0(t)";
  (5) §3.5 intuition — the GLM-F1 U-shape sentence (with \VpGainShare = 56); (6) §3.6 — four
  "(H)" additions (subsection opening "under (H)", Prop 2 **title**, worked example, measurement
  implication) + the worked-example U-shape sentence; (7) the two-weights paragraph — "Under (H),
  a firm that maximized a score with a weight below its decision weight…"; (8) §3.7 — the
  Ψ-multiplier rewording (\PsiMultLo–\PsiMultHi in place of (β+1)(β+2)/6), which the supp
  protocol section documents as a separate fix from another reviewer's row.
- **appendix_proofs.tex (6 lines, other reviewers' rows, documented):** accountability-floor
  example clarifications (illustrative N_o = 24; the break-even miss-rate phrasing with the
  common mode separated out) and the full-cost table's error-rate grounding note. No proof logic
  touched.
- **No undocumented theory changes.** Note for the record: the diff confirms the §3.5 sentence
  did NOT receive an "(H)" qualifier (my remnant finding, §3 above).

## 6. PART B(d): abstract and summary box keep their conditions

- Abstract (main p.1): "Under a **verification hypothesis**, a value-maximizing company weighs a
  point of growth at the value of an extra dollar of revenue…" ✓; "At **central costs and fixed
  prices**… below 100 unless its market grows over 32.5% a year, with AI compute at 6% of revenue
  (28 to 78% across compute costs; 36 or 39% if half or 70% of savings pass to customers)" ✓;
  "In a central scenario, **not a forecast**…" ✓; "the data cannot show the weight companies act
  on" ✓ (non-identification stated without a novelty claim).
- Summary box (main p.2): point 5 carries the ST-1 condition "at the central cost inputs… 28 to
  78% over the scenario range of compute cost, and 24.0 to 45.1% with compute at 6% and the other
  costs moved jointly" ✓; point 5's closing "This is a bound at that cost structure, not a
  forecast or a target" ✓. Point 6 flags the uniform-draws assumption ✓. No unconditioned theory
  claim found on either page.

## 7. PART B(e): ST-1 — the 32.5% threshold and the stress test

- **Supp §S10 text (printed p.58):** "32.5% is the threshold at the central cost inputs. With
  compute held at 6% of revenue and the other costs moved jointly, it runs from 24.0 to 45.1%,
  and it falls below 30% when the tax rate, the accountability floor and the AI-failure losses
  are all near their favorable ends; with the compute share also free over the box, up to the
  value test, it runs from 19.6 to 94.5% (one input at a time, the top of the scenario range
  takes it to 78%)." ✓ present as claimed.
- **Table S18 (printed p.59):** row "Cash ceiling below 100 up to 30% market growth: threshold
  G* above 30%" — full box: holds everywhere **no**, central 32.5%, range **19.6% to 94.5%**; row
  "The same [with] compute 6% of revenue, fixed prices, k = 0" — **no**, 32.5%, **24.0% to
  45.1%** ✓ both as claimed.
- **Against stored outputs (`repo_v4/notes/mc_results_2026-11-03/`, read not re-run):**
  `mc_claims_report.md` rows C1.cond/C1.full match Table S18 verbatim (24.0–45.1 and 19.6–94.5,
  both "NO", central 32.5%); `mc_claims.json` gives the endpoint mechanism —
  `group_swings/Gstar_2025/fullcost_target` vertex search over 28 dimensions: low **0.19637**,
  high **0.94539**, and central 0.32535; run.log records 10,000 LHS draws + 2,050 corners.
- **My independent recomputation from the stored per-draw CSV** (copied to scratch;
  `s2_st1_output.txt`): over the 10,000 LHS draws, Gstar_2025 spans 22.87–84.18% and
  Gstar_2025_cc6 spans 26.66–39.87% — inside the claimed vertex-search ranges (the extremes occur
  at box corners, which the LHS draws do not sample exactly), and the central column sits at
  32.5%. **Consistent; no discrepancy.** (I did not re-run the corner searches — recorded.)

**Verdict ST-1: resolved.** The claim is now correctly conditioned ("central cost inputs only"),
the S10 text and Table S18 agree with each other and with the archived Monte Carlo outputs, and
my partial recomputation is consistent.

---

## 8. Findings register (new items this round; severities)

| # | Severity | Locator | Finding | Proposed fix |
|---|---|---|---|---|
| N1 | editorial | main §3.5, printed p.21 | "near saturation the retention gain of (iii) is still about 56% of its small-share value": 56% is the ratio at the DIP (5.08/9.08); near saturation it is 64% (5.78/9.08), or 58% vs the small-share limit v0=10. True as a lower bound; mislabeled as the near-saturation point value. The author's own issue log says "about 60%". | "never falls below about 56% of its small-share value" or "is still about 64% of its 1%-of-cap value near saturation" |
| N2 | editorial | main §3.5, printed p.21 | The sentence "If the firm acts on its own decision weight X dyn(s) = v′(s) of Proposition 2…" lacks "(H)", unlike its §7.4 parallel. | add ", under (H)," as in §7.4 |
| N3 | editorial | code/verify_theory.py | Duplicate check labels: 15l, 15m, 15n each name two different checks after the round-3 insertion; the paper's citation "checks 15g to 15m" (main p.22) no longer identifies a unique set. | renumber old closed-loop/constant-policy/spend-ratio checks (e.g., 15r–15t) |
| N4 | note (no action) | main §3.11, printed pp.36–37 | The after-tax reconciliation sentence follows **Remark 3** (the value-based remark); the RESPONSE's locator "after Remark 5" is wrong — there is no Remark 5 in the main paper. The fix itself is correct and present. | correct the response document, not the paper |
| N5 | note (no action) | paper1/macros.tex:998 | \KaSlack{0.84} (the M3 slack magnitude) is defined but unused in the .tex. Harmless dead macro; the chosen in-text statement ("here k_a = 0") is the cleaner fix. | none |

**All five Part A rows verified; verdicts:** GLM-F1 **resolved** (with the concession on the
acceptance tests — the author's recalibration is correct); GLM-M3 **resolved**; GLM-M15
**resolved**; GLM-1 **agree with the author (already handled)** — and the author additionally
codified it as check 15n; GLM-7 **resolved** (algebra verified; response locator slip N4).

## 9. What I could not check, and why

1. **Lean compilation and kernel axiom output.** No Lean toolchain/Mathlib in this environment.
   The 35-theorem count, the axiom discipline, and the `#print axioms` claim are source-level
   findings (Axioms.lean documents them; the source scan is clean); a build machine must confirm.
2. **The corner points of the ST-1 box.** I read the stored outputs and recomputed ranges from
   the stored LHS draws only; I did not re-run the 28-dimension vertex searches (the stored
   JSON's vertex-search endpoints match the printed table exactly, which is the check that
   matters).
3. **The full verify_theory.py run** completed through section 17+ during this session with 116
   PASS and no genuine FAIL (the single 15p FAIL is my scratch-run artifact: the macro loader
   resolves `paper1/macros.tex` from the script's own root, absent in my scratch copy; I
   confirmed all ten \Vp* macros load correctly from the repo root and equal the grid values).
   The archived full log: `diag/rereview-theory/scratch/verify_full_output.txt`.
4. **LaTeX sources as build artifacts** (no LaTeX here): the .tex files were read as sources
   only; the supplied PDFs remain the ground truth per the manifest, and the one spot-check I
   made (the six v′ sentences, the macros' values) matched the PDFs exactly.

*Model-identity disclosure: this report is one context of the same LLM family as the Lead and
the other panelists; not independent human evidence. All scripts, seeds and outputs are archived
under `/root/tmp/rereview/diag/rereview-theory/`.*
