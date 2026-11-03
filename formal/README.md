# Machine-checked static core of "The Rule of 40 as a Price Line"

This directory contains a Lean 4 / Mathlib formalization of the static results of the model
section: Assumptions ass:market, ass:growth, ass:costs, ass:capital, Definition def:frontier, the
constants of eq:constants, Lemmas prop:frontier, prop:score, prop:saturation, prop:envelope,
Proposition prop:budget (discrete and continuous time, the latter with the paper's induced
share path constructed and verified), Corollaries cor:transient, cor:capital and the exact parts
of cor:priorities.

Every theorem is proved without `sorry`, `admit` or new axioms; `RuleOfX/Axioms.lean` prints the
axioms of every main theorem (`propext`, `Classical.choice`, `Quot.sound` only). A second,
non-default library `RuleOfXChecks` (directory `Checks/`) instantiates the main theorems at
concrete parameter values, which documents that their hypotheses are satisfiable; these
instances were written by the independent audit of the formalization.

## Build

* Toolchain: Lean 4.35.0 (`lean-toolchain`), Mathlib tag `v4.35.0` (`lakefile.toml`).
* Mathlib is built from source (there is no olean cache for this toolchain on the build machine).
* Commands, with the Lean toolchain on the `PATH`:

  ```
  cd formal
  lake build                 # builds Mathlib dependencies, then the library RuleOfX
  lake build RuleOfXChecks   # the audit's instances (not a default target)
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
| `RuleOfX/BudgetCont.lean` | Proposition prop:budget (a), (c) in continuous time and Corollary cor:transient (b) (both claims): general versions with the share path as a hypothesis, the construction of the paper's induced share path (`induced`, `induced_isPath`), and the corollaries with the induced path (see "Continuous time" below). |
| `RuleOfX/Axioms.lean` | `#print axioms` for all main theorems. |
| `Checks/RuleOfXChecks/Static.lean` | Instances of every static theorem at paper-like values (`α = 0.3`, `ℓ = 0.6`, `G = 0.10`, `k = 0.10`, `m₀ = 0.45`, `X = 1, 2`, `s̄ = 0.5`, `λ = 1.2`, `s = 0.1`), with uncapped, finite and exactly binding caps, negative `k`, and the discrete budget on a one-period path. |
| `Checks/RuleOfXChecks/Logistic.lean`, `Budget.lean` | The continuous budget on constant unit spend with the explicit logistic path, and with the induced path. |
| `Checks/RuleOfXChecks/Step.lean` | The continuous budget on a spend path with a jump (`σ = 0` then `1`), with the explicit induced path (shown not differentiable at the jump) and with `induced`. |
| `Checks/RuleOfXChecks/Optimum.lean` | A positive-horizon instance of the static-optimum bound `cor_transient_b_optimum`, with the share path built from Mathlib's one-dimensional inverse function theorem. |

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
* Hypotheses that a theorem does not use are kept in its statement to match the paper's
  standing assumptions, but named with a leading underscore (`_hα`, `_hk`, …). In particular
  `k ≥ 0` (ass:capital) is used only where the frontier is characterized as the set of
  undominated points (`m*` strictly decreasing): prop:frontier (a), (c) and prop:score (a);
  prop:frontier (d) and every other result hold for every real `k`, including the
  identification of `Rst` with the maximal score (`Rst_isGreatest`), which is stated as a
  conjunct of every theorem about `Rst` (prop:saturation (a)–(d), prop:envelope, cor:capital,
  cor:priorities (i), (ii), (iii), (v)).

## Results

Status: **proved** = proved as stated in the paper; **proved (change)** = proved with a change
described in the last column.

| Paper statement | Lean theorem(s) | Status | Difference from the paper's wording |
|---|---|---|---|
| eq:constants: `β = 1/α > 1`, `C_α ∈ (0,1)` | `one_lt_β`, `Cα_pos`, `Cα_lt_one` (also `β_pos`, `κ_pos`) | proved | none |
| prop:frontier (a): frontier is the graph of eq:frontier on `I`; `𝓕 = {g ∈ I, m ≤ m*(g)}` convex; dominated iff `m < m*(g)`; unique spend `κ(g-G)^β` | `prop_frontier_a` (`frontier_eq`, `feasible_eq`, `feasible_convex`, `dominated_iff`, `unique_spend`) | proved | none |
| prop:frontier (b): `m*(G) = m₀ - kG`, right derivative `-k` | `prop_frontier_b` | proved | right derivative stated as `HasDerivWithinAt … (Ici G) G` |
| prop:frontier (c): strictly decreasing, strictly concave on `I`; `m*'`, `m*''` for `g > G`, `m*'' < 0`; limits of `m*''` as `g ↓ G` for `α < 1/2`, `= 1/2`, `> 1/2` | `prop_frontier_c` | proved | the derivatives are `HasDerivAt` statements (`m*'` as given also holds at `g = G` with Mathlib's `rpow`); the `α = 1/2` case is `m*''(g) = -2κ` for every `g > G` |
| prop:frontier (d): `σ̄ = ∞ ⇒ m* → -∞`, `m*' → -∞`, `m*/g → -∞` | `prop_frontier_d` | proved | none (`I = [G, ∞)` by `I_top`); `k ≥ 0` not needed |
| prop:score (a): iso-score lines; a maximizer exists; every maximizer is on the frontier | `prop_score_a` (`exists_isMax`, `isMax_mem_frontier`) | proved | holds for every real `X`, not only `X ≥ 0` |
| prop:score (b): for `X > k` and `σ* ≤ σ̄`: unique interior maximizer, tangency `m*'(g*) = -X` (left derivative when `σ* = σ̄`, where `g* = ḡ`), eq:Dstar, eq:sigstar (both forms), eq:Rstar (both forms), `m*(g*) = m₀ - kg* - α(X-k)Δ*` | `prop_score_b` (`isUniqueMax_gstar`, `foc`, `σstar_eq`, `S_Δstar`, `surplus_eq`) | proved | the cap condition is the hypothesis `↑(σstar α ℓ (X-k)) ≤ σbar`; tangency is `HasDerivAt` (two-sided), from which the left derivative follows; "`σ* = σ̄ ⇒ g* = ḡ`" is included; the conjuncts `σ* = [αℓ(X-k)]^{1/(1-α)}` and `Δ* = ℓ^{1/(1-α)}[α(X-k)]^{α/(1-α)}` hold by definition (trivial) |
| prop:score (c): `X ≤ k`: unique maximizer `g* = G`, `σ* = 0`, `R* = m₀ + (X-k)G` | `prop_score_c` | proved | `σ* = 0` is `σplus α ℓ (X-k) = 0` and `spendOf G α ℓ G = 0` |
| prop:score (d): each `G < g < ḡ` is the unique maximizer for exactly the weight `X(g) = -m*'(g) = k + βκ(g-G)^{β-1}`; `g = G` is a maximizer iff `X ≤ k` | `prop_score_d` (`eq_Xof_of_isMax`, `Δstar_Xof`) | proved | "for exactly one weight" is stated in two forms: `∀ X, IsMax … ↔ X = Xof G k α ℓ g` (any maximizer, as in the paper's proof) and `∀ X, IsUniqueMax … ↔ X = Xof G k α ℓ g` |
| prop:score (d), `σ̄ = ∞`: `g*(X)` continuous, nondecreasing, strictly increasing on `X > k` | `prop_score_d_uncapped` | proved | `g*` is `gstar`, shown to be the unique maximizer for every `X`; continuity and monotonicity on all of `ℝ` |
| prop:score (e): `Π = max_{σ≥0}{(X-k)ℓσ^α - σ}`, `R* = m₀ + (X-k)G + Π` | `prop_score_e` | proved (change) | `max` is `IsGreatest` of the image of `[0,∞)`; the second claim is `IsGreatest (score X '' 𝓕) (m₀ + (X-k)G + Π)` under the cap condition `↑(σplus α ℓ (X-k)) ≤ σbar`, i.e. with `σ* = 0` when `X ≤ k` (the paper's eq:sigstar is not defined for `X < k`, see Findings) |
| prop:saturation (a): `R*_X(s) = R_∞ + C_α[λh(s)y₊]^{1/(1-α)}`; strictly decreasing with `dR*/ds = -(X-k)Δ*/(s̄-s)` if `X > k`; constant if `X ≤ k` | `prop_saturation_a` (`Rst_isGreatest`, `Rst_hasDerivAt`) | proved | "`R*_X(s)` is the maximal score" is the conjunct `IsGreatest (score X '' 𝓕) (Rst …)`; strict decrease on `(0, s̄)` |
| prop:saturation (b): `lim_{s→s̄} R* = R_∞`; Rule of 40 with `k = 0`; eq:rule100 | `prop_saturation_b` | proved | first conjunct: `Rst` is the maximal score at every `s < s̄`; limit along `𝓝[<] s̄`; the Rule-of-40 and eq:rule100 conjuncts are linear arithmetic (trivial) under `c_h, c_c, f, a_min ≥ 0`, `a ≥ a_min`, `m₀ = 1 - c_h - c_c - f - a` |
| prop:saturation (c): `sup_{(0,s̄)} R* = lim_{s→0} R* = R⁰`; not attained if `X > k`; constant and attained if `X ≤ k` | `prop_saturation_c` | proved | first conjunct: `Rst` is the maximal score at every `s < s̄`; `sup` is `IsLUB` of the image of `(0, s̄)`; the limit is along `𝓝[>] 0` |
| prop:saturation (d): threshold `Λ(R̄)`; `R*(s) ≥ R̄ ⇔ λh(s) ≥ Λ`; attainable at some share `⇔ λ > Λ`; values at the threshold | `prop_saturation_d` | proved | first conjunct: `Rst` is the maximal score at every `s ∈ (0, s̄)` |
| prop:envelope: `R*_X` continuously differentiable in `(m₀,G,k,X,λ,s)`; eq:envelope; `∂/∂γ, ∂/∂a, ∂/∂c_c`; convex in `k` and in `λ`; `∂²R*/∂k∂λ = -Δ*/[(1-α)λ] ≤ 0` | `prop_envelope` (`contDiffOn_RstP`, `hasDerivAt_Rst_*`, `Rst_convexOn_k`, `Rst_convexOn_lam`, `hasDerivAt_cross_lam`, `hasDerivAt_cross_k`) | proved | first conjunct: `Rst` is the maximal score on the feasible set (`σ̄ = ∞`) at the given parameters, for every real `X` and `k`; joint `C¹` is `ContDiffOn ℝ 1 (RstP α sbar) (Dom sbar)` on the open set `{λ > 0, s < s̄}` (it contains the paper's domain); the partial derivatives are one-variable `HasDerivAt` statements; convexity in `k` on `ℝ`, in `λ` on `(0,∞)`; the cross-partial is proved in both orders; `X ≥ 0` is not needed |
| cor:capital: bracket eq:kl-bracket; rises if `da > g*(k)dk`; does not rise if `da ≤ g*(k+dk)dk`; to first order rises iff `da > g* dk` | `cor_capital` (`kl_bracket`) | proved (reading) | first two conjuncts: the two `Rst` values are the maximal scores before and after the change; "to first order" is read as: `t ↦ R*_X(a - t·da, k + t·dk)` has derivative `da - g*(k)dk` at `t = 0`, and this derivative is `> 0 ⇔ da > g*(k)dk`; `da > 0` is not needed for the bracket |
| cor:priorities (i) | `cor_priorities_i` | proved | exact, through `m₀ = γ - a`; first two conjuncts: the `Rst` values are the maximal scores (domain `λ > 0`, `s < s̄`); the last two are identities (trivial): `Rst` and `Rinf` are affine in `m₀` with slope 1 |
| cor:priorities (ii), exact formulas and first-order gains | `cor_priorities_ii` (`Rst_scale_lam`) | proved (reading) | the map "same growth for spend `σ/(1+x)`" is the identity `growth G ℓ α ((1+x)σ) = growth G (ℓ(1+x)^α) α σ` at `ℓ = λh(s)` (first conjunct); the `Rst` values at `λ`, `λ(1+x)^α`, `λ(1+x)` are the maximal scores (next three conjuncts); exact gains `Π[(1+x)^{α/(1-α)} - 1]`, `Π[(1+x_λ)^{1/(1-α)} - 1]` for `x > -1`; "to first order" is the derivative at `x = 0`: `σ*`, resp. `(X-k)Δ* = σ*/α`, proved for `X > k`; "neither raises `R_∞`" holds by construction (`Rinf m0 G k X` has no `λ` argument) and is not stated as a theorem; "both vanish as `s → s̄`" is a `Tendsto` along `𝓝[<] s̄` |
| cor:priorities (iii) | `cor_priorities_iii` | proved (reading) | domain `λ > 0`, `s < s̄`; first conjunct: `Rst` is the maximal score; the zero-spend growth `G_i` is the parameter `G` of eq:growth; the gain is the derivative `X - k` of `R*` and of `R_∞` in `G`; "does not depend on share or growth" is stated as equality of the derivative at any two shares `s, s' < s̄` (last conjunct, trivial given the second) |
| cor:priorities (iv) | — | not formalized | out of scope (needs lem:prices and prop:entry) |
| cor:priorities (v) | `cor_priorities_v` | proved (reading) | first two conjuncts: the `Rst` values before and after the change are the maximal scores; first-order claim as in cor:capital; `g* ≥ G`; the last conjunct (the hurdle `g·dk` is nondecreasing in `g`) is trivial |
| prop:budget (b) (discrete time) | `prop_budget_b` | proved | hypotheses `s₀ > 0` and `X > k` (from the proposition's setting) made explicit |
| prop:budget (c), discrete case | `prop_budget_c_discrete` | proved | none |
| prop:budget (a) (continuous time) | `prop_budget_a_induced` (general form `prop_budget_a`; path `induced`, `induced_isPath`) | proved | as stated: any measurable `σ ≥ 0` with `∫_0^T σ^α < ∞`, measurable margins, and the induced share path `s(t) = s̄/(1 + e^{-λ∫_0^t σ^α}(s̄/s₀ - 1))` from `s₀ ∈ (0, s̄)`, shown to be absolutely continuous, in `(0, s̄)`, with `s(0) = s₀` and the share equation a.e.; the integrability of `(R_X - R_∞)⁺` on `[0,T]` is a conjunct; the general form takes any such path as a hypothesis; see "Continuous time" below |
| prop:budget (c), continuous case | `prop_budget_c_continuous_induced` (general form `prop_budget_c_continuous`) | proved (change) | as for (a); `m₀(·)` is assumed measurable (see Findings) |
| cor:transient (a) | `cor_transient_a` | proved | "the number of periods" is the number of `t < T` with `R_{X,t} ≥ R̄`, for every horizon `T` (the bound is uniform in `T`) |
| cor:transient (b), first claim | `cor_transient_b_induced` (general form `cor_transient_b`) | proved | the time is the Lebesgue measure of `{t ∈ (0,T] : R_X(t) ≥ R̄}` for every `T`; hypotheses as in prop:budget (a) |
| cor:transient (b), second claim (static-optimum policy) | `cor_transient_b_optimum_induced` (general form `cor_transient_b_optimum`) | proved (reading) | the policy is the hypothesis `σ(t) = σ*(λh(s(t)), X-k)` on `[0,T]` (eq:sigstar at the current share, a fixed-point condition between `σ` and its induced path; `Checks/RuleOfXChecks/Optimum.lean` exhibits a solution); conclusion: `∫_0^T (R_X - R_∞)⁺ ≤ (1-α)(X-k) ln(s(T)/s₀)` and the time at or above `R̄` is at most `(1-α)(X-k) ln(s̄/s₀)/(R̄ - R_∞)`; same reading of the share path as prop:budget (a). The paper's proof cites prop:myopic, but only the policy and the closed forms are needed |
| cor:transient, numerical example | — | not formalized | the numbers 1.81, 9.65, 5.01, 0.43, 0.30 are arithmetic; an independent numerical check gives 1.81, 9.65, 5.01, 0.425, 0.298 |

### Continuous time (prop:budget (a), (c); cor:transient (b))

The paper takes "the induced share path from `s(0) = s₀`", the solution of `ṡ = s λ h(s) σ^α`
for a measurable spend path `σ`, which the paper's proof writes down explicitly:
`s(t) = s̄ / (1 + e^{-Σ(t)} (s̄/s₀ - 1))` with `Σ(t) = λ ∫_0^t σ^α`. This path is constructed in
`RuleOfX/BudgetCont.lean` (`Spath`, `logistic`, `induced`) and `induced_isPath` proves, for any
`σ` with `∫_0^T σ^α < ∞` (`IntervalIntegrable (fun t => σ t ^ α) volume 0 T`) and
`0 < s₀ < s̄`, that it is absolutely continuous on `[0,T]` (`AbsolutelyContinuousOnInterval`;
`Σ` is an indefinite integral, hence absolutely continuous, and the logistic map is Lipschitz),
stays in `(0, s̄)`, starts at `s₀`, and satisfies the share equation
`ṡ(t) = s(t) λ h(s(t)) σ(t)^α` for almost every `t ∈ [0,T]` (Lebesgue differentiation,
`IntervalIntegrable.ae_hasDerivAt_integral`, composed with the smooth logistic map), i.e. it is
the Carathéodory solution. The theorems `prop_budget_a_induced`,
`prop_budget_c_continuous_induced`, `cor_transient_b_induced` and
`cor_transient_b_optimum_induced` then have no share-path hypothesis beyond "`s` is this induced
path": they cover every measurable, nonnegative spend path with `∫_0^T σ^α < ∞` and measurable
margins `m(t) ≤ m₀ - σ(t) - k g(t)` (any `T ≥ 0`), exactly as the paper states, and in
particular spend paths with jumps (`Checks/RuleOfXChecks/Step.lean`). Not formalized:
uniqueness of the solution (the paper's claim that this is *the* induced path; the general
versions below apply to any solution, so uniqueness is not needed for the bounds). The cap
`σ ≤ σ̄` is not needed and not assumed.

The general versions `prop_budget_a`, `prop_budget_c_continuous`, `cor_transient_b` and
`cor_transient_b_optimum` take any share path `s` that is absolutely continuous on `[0,T]`,
satisfies the share equation almost everywhere on `[0,T]` (`hode`) and stays in `(0, s̄)`
(ass:market) as a hypothesis. The proof uses Mathlib's fundamental theorem of calculus for
absolutely continuous functions (`AbsolutelyContinuousOnInterval.integral_deriv_eq_sub`)
applied to `log ∘ s`, which is absolutely continuous because `log` is Lipschitz on
`[min s, ∞)` and `s` is bounded away from `0` on the compact interval. Two convenience lemmas
discharge the hypotheses for a `C¹` path that satisfies the equation everywhere
(`ac_of_contDiffOn`, `hode_of_forall`).

Each continuous-time theorem states, as a conjunct, that the integrand `(R_X(t) - R_∞(t))⁺` is
interval integrable on `[0,T]`, so the integral in the bound is a genuine Lebesgue integral (in
Lean a non-integrable function integrates to `0`). cor:transient (b) states the Lebesgue measure
of `{t ∈ (0,T] : R_X(t) ≥ R̄}` (the time at or above `R̄` up to any horizon `T`); the left
endpoint `0` is a null set.

### The audit's instances (`Checks/`)

The library `RuleOfXChecks` (`lake build RuleOfXChecks`; it compiles no Mathlib module beyond
those the main library already needs) consists of `example`s that apply the main theorems to
concrete data, so that every hypothesis is discharged by a proof. They were written by the
independent audit of this formalization and adapted to the final statements. They show that the
hypotheses are satisfiable at paper-like values (including a finite cap, an exactly binding cap
`σ̄ = σ*`, `X ≤ k`, and negative `k` where allowed), that the discrete budget applies to a
one-period path with a score above `R_∞`, that the continuous budget applies to constant spend
with the logistic share path and to a spend path with a jump (whose share path is not
differentiable at the jump), and that `cor_transient_b_optimum` applies on a positive horizon
along a share path that actually follows the static-optimum policy.

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
   of `X` is never used; all results are proved for every real `X`. The standing assumption
   `k ≥ 0` (ass:capital) is needed only for the dominance results, where `m*` must be strictly
   decreasing: prop:frontier (a) and (c) (strict decrease), and prop:score (a) ("every maximizer
   lies on the frontier"); it is not used in prop:frontier (b), (d), prop:score (b)–(e), prop:saturation (a)–(d),
   prop:envelope, cor:capital, cor:priorities or the budget results, and the identification of
   the closed form with the maximal score (`Rst_isGreatest`, `Rstar_isGreatest`) holds for every
   real `k`. `da > 0` is not used for the bracket of cor:capital, and `α > 0` is not used in the
   continuous-time budget (only `σ ≥ 0`). Hypotheses that a theorem does not use are kept in its
   statement, to match the paper, but named with a leading underscore (`_hα`, `_hk`, …).
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
9. **prop:budget (a), cor:transient (b).** The paper's "induced share path" (the logistic
   formula of the proof) is constructed and verified to be an absolutely continuous solution of
   the share equation almost everywhere with values in `(0,s̄)`; with it the statements are
   proved as the paper states them. Uniqueness of the solution is not formalized; the general
   versions of the theorems apply to every such solution, so the bounds do not depend on it.
10. **prop:saturation (c).** "the supremum is not attained" is proved for shares in the open
    interval `(0, s̄)`; the limit `s → 0` is a limit from the right.
11. **prop:budget (c), continuous time: measurability of `m₀(·)`.** With a moving intercept the
    integrand `(R_X(t) - m₀(t) - (X-k)G)⁺` is measurable only if `m₀(·)` is; the paper does not
    say so (it says "measurable spend path" and "measurable margins" in (a)). The formalization
    assumes `Measurable m0` (`hm0m`). Without it the integral in eq:budget need not be defined.
12. **cor:transient (b), second claim.** The paper's proof invokes prop:myopic, but the claim
    only needs the policy `σ(t) = σ*(λh(s(t)), X-k)` and the closed forms eq:sigstar,
    eq:Dstar: along it `R_X - R_∞ ≤ (1-α)(X-k)Δ` at every date. It is formalized that way
    (`cor_transient_b_optimum`).
13. **cor:transient, numerical example.** Not formalized (arithmetic). An independent numerical
    check of the five numbers gives 1.81, 9.65, 5.01, 0.425 and 0.298, matching the paper's
    1.8, 9.6, 5.0, 0.43 and 0.30.
