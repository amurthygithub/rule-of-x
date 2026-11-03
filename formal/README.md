# Machine-checked static core of "The Rule of 40 as a Price Line"

This directory contains a Lean 4 / Mathlib formalization of the static results of the model
section: Assumptions ass:market, ass:growth, ass:costs, ass:capital, Definition def:frontier, the
constants of eq:constants, Lemmas prop:frontier, prop:score, prop:saturation, prop:envelope,
Proposition prop:budget (discrete time fully; continuous time under a stated extra hypothesis),
Corollaries cor:transient, cor:capital and the exact parts of cor:priorities.

Every theorem is proved without `sorry`, `admit` or new axioms; `RuleOfX/Axioms.lean` prints the
axioms of every main theorem (`propext`, `Classical.choice`, `Quot.sound` only).

## Build

* Toolchain: Lean 4.35.0 (`lean-toolchain`), Mathlib tag `v4.35.0` (`lakefile.toml`).
* Mathlib is built from source (there is no olean cache for this toolchain on the build machine).
* Commands, with the Lean toolchain on the `PATH`:

  ```
  cd formal
  lake build            # builds Mathlib dependencies, then the library RuleOfX
  ```

  `lake build` compiles the import closure of `RuleOfX/Imports.lean` and
  `RuleOfX/BudgetCont.lean`; on the 2-core, 7 GB machine used here, the Mathlib closure of
  `RuleOfX/Imports.lean` (2327 modules) took about 36 minutes to compile, and the additional
  measure-theory closure needed by `RuleOfX/BudgetCont.lean` (about 480 more modules) about 10
  minutes. The `RuleOfX` files
  themselves compile in a few seconds each.
* `RuleOfX/Axioms.lean` runs `#print axioms` on every main theorem; the output appears in the
  build log (`lake build` prints it as `info` messages).

## Files

| File | Content |
|---|---|
| `RuleOfX/Defs.lean` | Constants of eq:constants, growth technology eq:growth, feasible set, dominance, frontier, score (def:frontier), `m*`, closed forms `Δ*`, `σ*`, `g*`, `Π`, `R_∞`, `R*_X` as a function of all parameters; elementary identities. |
| `RuleOfX/Frontier.lean` | Lemma prop:frontier (a)–(d). |
| `RuleOfX/Score.lean` | Lemma prop:score (a)–(e). |
| `RuleOfX/Saturation.lean` | Lemma prop:saturation (a)–(d); the `C¹` lemma for `y ↦ (y₊)^{1/(1-α)}`. |
| `RuleOfX/Envelope.lean` | Lemma prop:envelope. |
| `RuleOfX/Capital.lean` | Corollary cor:capital; Corollary cor:priorities (i), (ii), (iii), (v). |
| `RuleOfX/Budget.lean` | Proposition prop:budget (b), (c) in discrete time; Corollary cor:transient (a). |
| `RuleOfX/BudgetCont.lean` | Proposition prop:budget (a), (c) in continuous time and Corollary cor:transient (b), under the extra hypothesis described below. |
| `RuleOfX/Axioms.lean` | `#print axioms` for all main theorems. |

## Conventions

* `α ∈ (0,1)` is the spend elasticity, `β = 1/α`, `κ = ℓ^{-β}`, `C_α = (1-α)α^{α/(1-α)}`
  (`RuleOfX.β`, `RuleOfX.κ`, `RuleOfX.Cα`). Real powers are Mathlib's `Real.rpow` (`x ^ y`);
  every base that occurs in a statement is nonnegative on the stated domain.
* `ℓ = λ h(s) > 0` is a parameter of the frontier and score results (the paper says "fix `s`").
  `λ` is a reserved word in Lean, so demand pull is `lam`; `h(s) = 1 - s/s̄` is `hdr sbar s`.
* The financing cap `σ̄ ∈ (0, ∞]` is a `WithTop ℝ`, with `⊤` for `σ̄ = ∞`, and the hypothesis
  `0 < σbar`. The spend set is `Spend σbar = {σ | 0 ≤ σ ∧ ↑σ ≤ σbar}`, `ḡ = gbar G ℓ α σbar`
  (`⊤` when `σ̄ = ⊤`) and `I = {g | G ≤ g ∧ ↑g ≤ ḡ}` (so `I = [G, ∞)` when `σ̄ = ⊤`, `I_top`, and
  `I = [G, G + ℓ σ̄^α]` otherwise, `I_coe`). No separate capped/uncapped theorems were needed.
* `y = X - k`; `Δstar α ℓ y`, `σstar α ℓ y` are eq:Dstar, eq:sigstar; `Δplus`, `σplus` are the
  same with `y` replaced by `y₊ = max y 0` (the convention the paper states after prop:score);
  `gstar G k α ℓ X = G + Δplus α ℓ (X-k)` is `g*(X)`; `surplus α ℓ y = (1-α) y Δplus α ℓ y` is the
  growth surplus `Π` (`Π` is reserved in Lean).
* `Rinf m0 G k X = m₀ + (X-k)G` is `R_∞`; `Rst α sbar m0 G k X lam s`
  `= m₀ + (X-k)G + C_α(λ h(s) (X-k)₊)^{1/(1-α)}` is `R*_X` as a function of all parameters with
  `σ̄ = ∞`; `Rst_isGreatest` shows it is the maximal score. `RstP α sbar` is the same function on
  the tuple `(m₀, G, k, X, λ, s)`, used for joint differentiability.
* `IsMax`/`IsUniqueMax m0 G k α ℓ σbar X p`: `p` is a (the unique) maximizer of `R_X` on the
  feasible set.

## Results

Status: **proved** = proved as stated in the paper; **proved (change)** = proved with a change
described in the last column.

| Paper statement | Lean theorem(s) | Status | Difference from the paper's wording |
|---|---|---|---|
| prop:frontier (a): frontier is the graph of eq:frontier on `I`; `𝓕 = {g ∈ I, m ≤ m*(g)}` convex; dominated iff `m < m*(g)`; unique spend `κ(g-G)^β` | `prop_frontier_a` (`frontier_eq`, `feasible_eq`, `feasible_convex`, `dominated_iff`, `unique_spend`) | proved | none |
| prop:frontier (b): `m*(G) = m₀ - kG`, right derivative `-k` | `prop_frontier_b` | proved | right derivative stated as `HasDerivWithinAt … (Ici G) G` |
| prop:frontier (c): strictly decreasing, strictly concave on `I`; `m*'`, `m*''` for `g > G`, `m*'' < 0`; limits of `m*''` as `g ↓ G` for `α < 1/2`, `= 1/2`, `> 1/2` | `prop_frontier_c` | proved | the derivatives are `HasDerivAt` statements (`m*'` as given also holds at `g = G` with Mathlib's `rpow`); the `α = 1/2` case is `m*''(g) = -2κ` for every `g > G` |
| prop:frontier (d): `σ̄ = ∞ ⇒ m* → -∞`, `m*' → -∞`, `m*/g → -∞` | `prop_frontier_d` | proved | none (`I = [G, ∞)` by `I_top`) |
| prop:score (a): iso-score lines; a maximizer exists; every maximizer is on the frontier | `prop_score_a` (`exists_isMax`, `isMax_mem_frontier`) | proved | holds for every real `X`, not only `X ≥ 0` |
| prop:score (b): for `X > k` and `σ* ≤ σ̄`: unique interior maximizer, tangency `m*'(g*) = -X` (left derivative when `σ* = σ̄`, where `g* = ḡ`), eq:Dstar, eq:sigstar (both forms), eq:Rstar (both forms), `m*(g*) = m₀ - kg* - α(X-k)Δ*` | `prop_score_b` (`isUniqueMax_gstar`, `foc`, `σstar_eq`, `S_Δstar`, `Π_eq`) | proved | the cap condition is the hypothesis `↑(σstar α ℓ (X-k)) ≤ σbar`; tangency is `HasDerivAt` (two-sided), from which the left derivative follows; "`σ* = σ̄ ⇒ g* = ḡ`" is included |
| prop:score (c): `X ≤ k`: unique maximizer `g* = G`, `σ* = 0`, `R* = m₀ + (X-k)G` | `prop_score_c` | proved | `σ* = 0` is `σplus α ℓ (X-k) = 0` and `spendOf G α ℓ G = 0` |
| prop:score (d): each `G < g < ḡ` is the unique maximizer for exactly the weight `X(g) = -m*'(g) = k + βκ(g-G)^{β-1}`; `g = G` is a maximizer iff `X ≤ k` | `prop_score_d` (`eq_Xof_of_isMax`, `Δstar_Xof`) | proved | "for exactly one weight" is `∀ X, IsUniqueMax … ↔ X = Xof G k α ℓ g` |
| prop:score (d), `σ̄ = ∞`: `g*(X)` continuous, nondecreasing, strictly increasing on `X > k` | `prop_score_d_uncapped` | proved | `g*` is `gstar`, shown to be the unique maximizer for every `X`; continuity and monotonicity on all of `ℝ` |
| prop:score (e): `Π = max_{σ≥0}{(X-k)ℓσ^α - σ}`, `R* = m₀ + (X-k)G + Π` | `prop_score_e` | proved (change) | `max` is `IsGreatest` of the image of `[0,∞)`; the second claim is `IsGreatest (score X '' 𝓕) (m₀ + (X-k)G + Π)` under the cap condition `↑(σplus α ℓ (X-k)) ≤ σbar`, i.e. with `σ* = 0` when `X ≤ k` (the paper's eq:sigstar is not defined for `X < k`, see Findings) |
| prop:saturation (a): `R*_X(s) = R_∞ + C_α[λh(s)y₊]^{1/(1-α)}`; strictly decreasing with `dR*/ds = -(X-k)Δ*/(s̄-s)` if `X > k`; constant if `X ≤ k` | `prop_saturation_a` (`Rst_isGreatest`, `Rst_hasDerivAt`) | proved | "`R*_X(s)` is the maximal score" is the conjunct `IsGreatest (score X '' 𝓕) (Rst …)`; strict decrease on `(0, s̄)` |
| prop:saturation (b): `lim_{s→s̄} R* = R_∞`; Rule of 40 with `k = 0`; eq:rule100 | `prop_saturation_b` | proved | limit along `𝓝[<] s̄`; eq:rule100 under `c_h, c_c, f, a_min ≥ 0`, `a ≥ a_min`, `m₀ = 1 - c_h - c_c - f - a` |
| prop:saturation (c): `sup_{(0,s̄)} R* = lim_{s→0} R* = R⁰`; not attained if `X > k`; constant and attained if `X ≤ k` | `prop_saturation_c` | proved | `sup` is `IsLUB` of the image of `(0, s̄)`; the limit is along `𝓝[>] 0` |
| prop:saturation (d): threshold `Λ(R̄)`; `R*(s) ≥ R̄ ⇔ λh(s) ≥ Λ`; attainable at some share `⇔ λ > Λ`; values at the threshold | `prop_saturation_d` | proved | none |
| prop:envelope: `R*_X` continuously differentiable in `(m₀,G,k,X,λ,s)`; eq:envelope; `∂/∂γ, ∂/∂a, ∂/∂c_c`; convex in `k` and in `λ`; `∂²R*/∂k∂λ = -Δ*/[(1-α)λ] ≤ 0` | `prop_envelope` (`contDiffOn_RstP`, `hasDerivAt_Rst_*`, `Rst_convexOn_k`, `Rst_convexOn_lam`, `hasDerivAt_cross_lam`, `hasDerivAt_cross_k`) | proved | joint `C¹` is `ContDiffOn ℝ 1 (RstP α sbar) (Dom sbar)` on the open set `{λ > 0, s < s̄}` (it contains the paper's domain); the partial derivatives are one-variable `HasDerivAt` statements; convexity in `k` on `ℝ`, in `λ` on `(0,∞)`; the cross-partial is proved in both orders; `X ≥ 0` is not needed |
| cor:capital: bracket eq:kl-bracket; rises if `da > g*(k)dk`; does not rise if `da ≤ g*(k+dk)dk`; to first order rises iff `da > g* dk` | `cor_capital` (`kl_bracket`) | proved (reading) | "to first order" is read as: `t ↦ R*_X(a - t·da, k + t·dk)` has derivative `da - g*(k)dk` at `t = 0`, and this derivative is `> 0 ⇔ da > g*(k)dk`; `da > 0` is not needed for the bracket |
| cor:priorities (i) | `cor_priorities_i` | proved | exact, through `m₀ = γ - a` |
| cor:priorities (ii), exact formulas and first-order gains | `cor_priorities_ii` (`Rst_scale_lam`) | proved (reading) | exact gains `Π[(1+x)^{α/(1-α)} - 1]`, `Π[(1+x_λ)^{1/(1-α)} - 1]` for `x > -1`; "to first order" is the derivative at `x = 0`: `σ*`, resp. `(X-k)Δ* = σ*/α`, proved for `X > k`; "neither raises `R_∞`" is immediate (`Rinf` does not depend on `λ`) and is not stated; "both vanish as `s → s̄`" is a `Tendsto` along `𝓝[<] s̄` |
| cor:priorities (iii) | `cor_priorities_iii` | proved (reading) | the zero-spend growth `G_i` is the parameter `G` of eq:growth; the gain is the derivative `X - k` of `R*` and of `R_∞` in `G`; "does not depend on share or growth" is stated as equality of the derivative at any two shares |
| cor:priorities (iv) | — | not formalized | out of scope (needs lem:prices and prop:entry) |
| cor:priorities (v) | `cor_priorities_v` | proved (reading) | first-order claim as in cor:capital; `g* ≥ G`; the hurdle `g*dk` is nondecreasing in `g*` |
| prop:budget (b) (discrete time) | `prop_budget_b` | proved | hypotheses `s₀ > 0` and `X > k` (from the proposition's setting) made explicit |
| prop:budget (c), discrete case | `prop_budget_c_discrete` | proved | none |
| prop:budget (a) (continuous time) | `prop_budget_a` | proved (change) | see "Continuous time" below |
| prop:budget (c), continuous case | `prop_budget_c_continuous` | proved (change) | see "Continuous time" below |
| cor:transient (a) | `cor_transient_a` | proved | "the number of periods" is the number of `t < T` with `R_{X,t} ≥ R̄`, for every horizon `T` (the bound is uniform in `T`) |
| cor:transient (b), first claim | `cor_transient_b` | proved (change) | the time is the Lebesgue measure of `{t ∈ (0,T] : R_X(t) ≥ R̄}` for every `T`; hypotheses as in prop:budget (a) below |
| cor:transient (b), second claim (static-optimum policy) | — | not formalized | refers to prop:myopic, out of scope |

### Continuous time (prop:budget (a), (c); cor:transient (b))

The paper takes "the induced share path from `s(0) = s₀`", i.e. the solution of
`ṡ = s λ h(s) σ^α`, which for a merely measurable `σ` is absolutely continuous and satisfies the
equation almost everywhere. In `RuleOfX/BudgetCont.lean` the share path is a **hypothesis**: a
function `s` that is differentiable at every `t ∈ [0,T]` with
`ṡ(t) = s(t) · λ h(s(t)) σ(t)^α` (ass:market, `g = G + ṡ/s`, combined with eq:growth) and that
stays in `(0, s̄)` on `[0,T]` (ass:market). This is **stronger** than the paper's hypothesis
(differentiability everywhere instead of almost everywhere; the paper derives `s < s̄` from the
explicit logistic solution instead of assuming it). When `σ` is continuous the induced path
satisfies these hypotheses. The existence and uniqueness of the logistic solution, and the
almost-everywhere version of the argument, are not formalized. The cap `σ ≤ σ̄` is not needed and
not assumed; `σ` and `m` are assumed measurable, `σ ≥ 0`, and `∫_0^T σ^α < ∞` is
`IntervalIntegrable (fun t => σ t ^ α) volume 0 T`.

## Findings about the paper

None of the statements in scope was found to be false. The following points are imprecise or
need a reading:

1. **eq:sigstar for `X < k` (prop:score, preamble and part (e)).** The lemma assumes for parts (b)
   and (e) that "`σ* ≤ σ̄` with `σ*` given in eq:sigstar". For `X < k`, eq:sigstar is
   `[αλh(X-k)]^{1/(1-α)}` with a negative base, which is not a real number in general; part (e)
   is stated for all `X ≥ 0`. The convention "`(X-k)` replaced by `(X-k)_+`" is introduced only
   after the lemma. The formalization uses `σ* = 0` for `X ≤ k` (`σplus`), which is the spend of
   the corner maximizer of part (c); with that reading (e) holds for all `X`.
2. **Unused hypotheses.** "Fix `X ≥ 0`" (prop:score, prop:saturation, prop:envelope): the sign
   of `X` is never used; all results are proved for every real `X`. Likewise `k ≥ 0` is not used
   in prop:score (c), `da > 0` is not used for the bracket of cor:capital, and `α > 0` is not used
   in the continuous-time budget (only `σ ≥ 0`). Hypotheses that a theorem does not use are kept
   in its statement, to match the paper, but named with a leading underscore (`_hα`, `_hk`, …).
3. **Tangency "for the left derivative" when `σ* = σ̄` (prop:score (b)).** Since `m*` is given by
   a formula that extends beyond `ḡ`, the formalization proves the two-sided derivative
   `m*'(g*) = -X` (as a function on `ℝ`), from which the left derivative follows; the statement
   as written is correct.
4. **"The point `g = G` is a maximizer iff `X ≤ k`" (prop:score (d)).** Correct; note it is a
   statement about maximizers (not unique maximizers), and for `X ≤ k` the maximizer at `G` is
   in fact unique (part (c)).
5. **"To first order" (cor:capital, cor:priorities).** Read as statements about derivatives (see
   the table). cor:priorities (ii) says the efficiency gain "raises `R*_X` by `xσ*`, the same as
   cutting a non-discretionary cost line of size `σ*` by the proportion `x`"; the formalization
   proves the derivative at `x = 0` equals `σ*` and, separately, part (i); the comparison itself
   is arithmetic.
6. **prop:envelope, order of the cross-partial.** The proof differentiates `∂R*/∂k` in `λ`. Both
   orders give `-Δ*/[(1-α)λ]` and both are proved.
7. **prop:envelope, joint `C¹`.** The claim holds on the open parameter domain `λ > 0`, `s < s̄`
   (which contains `s ∈ (0, s̄)`); across `X = k` it relies on `y ↦ (y₊)^{1/(1-α)}` being `C¹`,
   which is proved (`contDiff_fplus`).
8. **prop:budget (b).** The statement needs `s₀ > 0` for the logarithms and `X > k` (both are in
   the proposition's preamble); it does not need the growth technology or `s₀ < s̄`.
9. **prop:budget (a), cor:transient (b).** The paper's "induced share path" and the a.e. argument
   were replaced by the explicit hypothesis described above; the inequality itself and the
   Markov-inequality step of cor:transient (b) are verified. This is a gap in the formalization,
   not a flaw found in the paper.
10. **prop:saturation (c).** "the supremum is not attained" is proved for shares in the open
    interval `(0, s̄)`; the limit `s → 0` is a limit from the right.
