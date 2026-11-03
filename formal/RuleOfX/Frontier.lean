import RuleOfX.Defs

/-!
# Lemma prop:frontier (Efficient frontier)

Hypotheses throughout: `0 < α < 1`, `0 < ℓ`, `0 ≤ k`, and `0 < σ̄` (so `σ̄ ∈ (0, ∞]`).
-/

noncomputable section
open Real Set Filter Topology

set_option autoImplicit false

namespace RuleOfX

variable {m0 G k α ℓ : ℝ} {σbar : WithTop ℝ}

/-! ### Part (a): the feasible set is the hypograph of `m*` over `I` -/

/-- The feasible set is `{(g, m) : g ∈ I, m ≤ m*(g)}`. -/
theorem feasible_iff (hα : 0 < α) (hℓ : 0 < ℓ) (hσbar : 0 < σbar) (p : ℝ × ℝ) :
    p ∈ Feasible m0 G k α ℓ σbar ↔ p.1 ∈ I G ℓ α σbar ∧ p.2 ≤ mstar m0 G k α ℓ p.1 := by
  constructor
  · rintro ⟨σ, hσ, hp1, hp2⟩
    have hI : p.1 ∈ I G ℓ α σbar := (mem_I_iff hα hℓ hσbar p.1).2 ⟨σ, hσ, hp1.symm⟩
    have hs : spendOf G α ℓ p.1 = σ := by rw [hp1]; exact spendOf_growth hα hℓ hσ.1
    refine ⟨hI, ?_⟩
    unfold mstar; rw [hs]; linarith
  · rintro ⟨hI, hle⟩
    obtain ⟨σ, hσ, hg⟩ := (mem_I_iff hα hℓ hσbar p.1).1 hI
    have hs : spendOf G α ℓ p.1 = σ := by rw [← hg]; exact spendOf_growth hα hℓ hσ.1
    refine ⟨σ, hσ, hg.symm, ?_⟩
    unfold mstar at hle; rw [hs] at hle; linarith

theorem feasible_eq (hα : 0 < α) (hℓ : 0 < ℓ) (hσbar : 0 < σbar) :
    Feasible m0 G k α ℓ σbar = {p | p.1 ∈ I G ℓ α σbar ∧ p.2 ≤ mstar m0 G k α ℓ p.1} :=
  Set.ext (feasible_iff hα hℓ hσbar)

/-- `m*` is strictly decreasing on `[G, ∞)` (hence on `I`). -/
theorem mstar_strictAntiOn (hα : 0 < α) (hℓ : 0 < ℓ) (hk : 0 ≤ k) :
    StrictAntiOn (mstar m0 G k α ℓ) (Ici G) := by
  intro x hx y hy hxy
  have h1 := spendOf_strictMonoOn (G := G) hα hℓ hx hy hxy
  have h2 := mul_le_mul_of_nonneg_left hxy.le hk
  unfold mstar
  linarith

theorem mstar_antitoneOn (hα : 0 < α) (hℓ : 0 < ℓ) (hk : 0 ≤ k) :
    AntitoneOn (mstar m0 G k α ℓ) (Ici G) :=
  (mstar_strictAntiOn hα hℓ hk).antitoneOn

/-- `m*` is strictly concave on `[G, ∞)`: fact (F1) of the proofs, through
`strictConvexOn_rpow`. -/
theorem mstar_strictConcaveOn (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) :
    StrictConcaveOn ℝ (Ici G) (mstar m0 G k α ℓ) := by
  have hconv := strictConvexOn_rpow (one_lt_β hα hα1)
  refine ⟨convex_Ici G, ?_⟩
  intro x hx y hy hxy a b ha hb hab
  have hx' : x - G ∈ Ici (0 : ℝ) := mem_Ici.2 (sub_nonneg.2 hx)
  have hy' : y - G ∈ Ici (0 : ℝ) := mem_Ici.2 (sub_nonneg.2 hy)
  have hne : x - G ≠ y - G := fun h => hxy (by linarith)
  have key := hconv.2 hx' hy' hne ha hb hab
  simp only [smul_eq_mul] at key ⊢
  have hκ := κ_pos (α := α) hℓ
  have e : a * x + b * y - G = a * (x - G) + b * (y - G) := by linear_combination G * hab
  have key2 : κ α ℓ * (a * x + b * y - G) ^ β α <
      a * (κ α ℓ * (x - G) ^ β α) + b * (κ α ℓ * (y - G) ^ β α) := by
    rw [e]
    have := mul_lt_mul_of_pos_left key hκ
    linarith
  obtain rfl : b = 1 - a := by linarith
  simp only [mstar, spendOf]
  nlinarith [key2]

theorem mstar_concaveOn (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) :
    ConcaveOn ℝ (Ici G) (mstar m0 G k α ℓ) :=
  (mstar_strictConcaveOn hα hα1 hℓ).concaveOn

theorem mstar_strictConcaveOn_I (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (σbar : WithTop ℝ) :
    StrictConcaveOn ℝ (I G ℓ α σbar) (mstar m0 G k α ℓ) :=
  (mstar_strictConcaveOn hα hα1 hℓ).subset (I_subset_Ici σbar) (convex_I σbar)

theorem mstar_strictAntiOn_I (hα : 0 < α) (hℓ : 0 < ℓ) (hk : 0 ≤ k) (σbar : WithTop ℝ) :
    StrictAntiOn (mstar m0 G k α ℓ) (I G ℓ α σbar) :=
  (mstar_strictAntiOn hα hℓ hk).mono (I_subset_Ici σbar)

/-- The feasible set is convex. -/
theorem feasible_convex (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hσbar : 0 < σbar) :
    Convex ℝ (Feasible m0 G k α ℓ σbar) := by
  rw [feasible_eq hα hℓ hσbar]
  exact ((mstar_concaveOn hα hα1 hℓ).subset (I_subset_Ici σbar) (convex_I σbar)).convex_hypograph

/-- A feasible point is dominated iff it lies strictly below the frontier. -/
theorem dominated_iff (hα : 0 < α) (hℓ : 0 < ℓ) (hk : 0 ≤ k) (hσbar : 0 < σbar)
    {p : ℝ × ℝ} (hp : p ∈ Feasible m0 G k α ℓ σbar) :
    (∃ q ∈ Feasible m0 G k α ℓ σbar, Dominates q p) ↔ p.2 < mstar m0 G k α ℓ p.1 := by
  rw [feasible_iff hα hℓ hσbar] at hp
  constructor
  · rintro ⟨q, hq, hq1, hq2, hstrict⟩
    rw [feasible_iff hα hℓ hσbar] at hq
    by_contra hnot
    push_neg at hnot
    have hmono := mstar_antitoneOn (m0 := m0) hα hℓ hk hp.1.1 hq.1.1 hq1
    have h2 : q.2 = p.2 := le_antisymm (by linarith) hq2
    rcases hstrict with h | h
    · have := mstar_strictAntiOn (m0 := m0) hα hℓ hk hp.1.1 hq.1.1 h
      linarith
    · linarith
  · intro hlt
    refine ⟨(p.1, mstar m0 G k α ℓ p.1), ?_, le_rfl, hlt.le, Or.inr hlt⟩
    rw [feasible_iff hα hℓ hσbar]
    exact ⟨hp.1, le_rfl⟩

/-- The efficient frontier is the graph of `m*` over `I`. -/
theorem frontier_eq (hα : 0 < α) (hℓ : 0 < ℓ) (hk : 0 ≤ k) (hσbar : 0 < σbar) :
    Frontier m0 G k α ℓ σbar = {p | p.1 ∈ I G ℓ α σbar ∧ p.2 = mstar m0 G k α ℓ p.1} := by
  ext p
  simp only [Frontier, Set.mem_ofPred_eq]
  constructor
  · rintro ⟨hp, hnd⟩
    have hp' := (feasible_iff hα hℓ hσbar p).1 hp
    refine ⟨hp'.1, le_antisymm hp'.2 ?_⟩
    by_contra hlt
    push_neg at hlt
    exact hnd ((dominated_iff hα hℓ hk hσbar hp).2 hlt)
  · rintro ⟨hI, heq⟩
    have hp : p ∈ Feasible m0 G k α ℓ σbar := (feasible_iff hα hℓ hσbar p).2 ⟨hI, heq.le⟩
    refine ⟨hp, ?_⟩
    rw [dominated_iff hα hℓ hk hσbar hp, heq]
    exact lt_irrefl _

/-- Each `g ∈ I` is produced by exactly one admissible spend level, namely `κ (g - G)^β`. -/
theorem unique_spend (hα : 0 < α) (hℓ : 0 < ℓ) (hσbar : 0 < σbar) {g : ℝ}
    (hg : g ∈ I G ℓ α σbar) :
    (∃! σ, σ ∈ Spend σbar ∧ growth G ℓ α σ = g) ∧
      ∀ σ ∈ Spend σbar, growth G ℓ α σ = g → σ = κ α ℓ * (g - G) ^ β α := by
  have huniq : ∀ σ ∈ Spend σbar, growth G ℓ α σ = g → σ = κ α ℓ * (g - G) ^ β α := by
    intro σ hσ hgσ
    have := spendOf_growth (G := G) hα hℓ hσ.1
    rw [hgσ] at this
    exact this.symm
  refine ⟨?_, huniq⟩
  obtain ⟨σ, hσ, hgσ⟩ := (mem_I_iff hα hℓ hσbar g).1 hg
  refine ⟨σ, ⟨hσ, hgσ⟩, ?_⟩
  rintro σ' ⟨hσ', hgσ'⟩
  rw [huniq σ' hσ' hgσ', huniq σ hσ hgσ]

/-- **Lemma prop:frontier (a).** "The efficient frontier is the graph of
`m*(g) = m₀ - k g - κ (g - G)^β`, `g ∈ I`. The feasible set `𝓕 = {(g,m) : g ∈ I, m ≤ m*(g)}`
is convex. A feasible point is dominated if and only if `m < m*(g)`. Each frontier point is
produced by the unique spend level `σ = κ (g - G)^β`." -/
theorem prop_frontier_a (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hk : 0 ≤ k)
    (hσbar : 0 < σbar) :
    Frontier m0 G k α ℓ σbar = {p | p.1 ∈ I G ℓ α σbar ∧ p.2 = m0 - k * p.1 - κ α ℓ * (p.1 - G) ^ β α} ∧
    Feasible m0 G k α ℓ σbar = {p | p.1 ∈ I G ℓ α σbar ∧ p.2 ≤ mstar m0 G k α ℓ p.1} ∧
    Convex ℝ (Feasible m0 G k α ℓ σbar) ∧
    (∀ p ∈ Feasible m0 G k α ℓ σbar,
      (∃ q ∈ Feasible m0 G k α ℓ σbar, Dominates q p) ↔ p.2 < mstar m0 G k α ℓ p.1) ∧
    (∀ p ∈ Frontier m0 G k α ℓ σbar,
      (∃! σ, σ ∈ Spend σbar ∧ growth G ℓ α σ = p.1 ∧ p.2 = m0 - σ - k * p.1) ∧
      ∀ σ ∈ Spend σbar, growth G ℓ α σ = p.1 → σ = κ α ℓ * (p.1 - G) ^ β α) := by
  refine ⟨frontier_eq hα hℓ hk hσbar, feasible_eq hα hℓ hσbar,
    feasible_convex hα hα1 hℓ hσbar, fun p hp => dominated_iff hα hℓ hk hσbar hp, ?_⟩
  intro p hp
  rw [frontier_eq hα hℓ hk hσbar] at hp
  obtain ⟨hI, heq⟩ := hp
  obtain ⟨⟨σ, ⟨hσ, hgσ⟩, huniq⟩, hform⟩ := unique_spend hα hℓ hσbar hI
  refine ⟨⟨σ, ⟨hσ, hgσ, ?_⟩, ?_⟩, hform⟩
  · rw [heq, mstar_def, hform σ hσ hgσ]; ring
  · rintro σ' ⟨hσ', hgσ', _⟩
    exact huniq σ' ⟨hσ', hgσ'⟩

/-! ### Derivatives of `m*` -/

/-- `m*` is differentiable everywhere with `m*'(g) = -k - β κ (g - G)^{β-1}` (Mathlib's
`rpow` makes this true at `g = G` as well, where the value is `-k`). -/
theorem mstar_hasDerivAt (hα : 0 < α) (hα1 : α < 1) (g : ℝ) :
    HasDerivAt (mstar m0 G k α ℓ) (-k - β α * κ α ℓ * (g - G) ^ (β α - 1)) g := by
  have h1 : HasDerivAt (fun x : ℝ => (x - G) ^ β α) (1 * β α * (g - G) ^ (β α - 1)) g :=
    ((hasDerivAt_id' g).sub_const G).rpow_const (Or.inr (one_lt_β hα hα1).le)
  have h2 := ((hasDerivAt_const g m0).sub ((hasDerivAt_id' g).const_mul k)).sub
    (h1.const_mul (κ α ℓ))
  have hf : mstar m0 G k α ℓ = fun x => m0 - k * x - κ α ℓ * (x - G) ^ β α := rfl
  rw [hf]
  exact h2.congr_deriv (by ring)

theorem mstar_continuous (hα : 0 < α) (hα1 : α < 1) : Continuous (mstar m0 G k α ℓ) :=
  continuous_iff_continuousAt.2 fun g => (mstar_hasDerivAt hα hα1 g).continuousAt

theorem deriv_mstar (hα : 0 < α) (hα1 : α < 1) :
    deriv (mstar m0 G k α ℓ) = fun g => -k - β α * κ α ℓ * (g - G) ^ (β α - 1) :=
  funext fun g => (mstar_hasDerivAt hα hα1 g).deriv

/-- **Lemma prop:frontier (b).** "At `g = G` the frontier takes the value `m*(G) = m₀ - kG`,
and its right derivative there is `-k`." -/
theorem prop_frontier_b (hα : 0 < α) (hα1 : α < 1) :
    mstar m0 G k α ℓ G = m0 - k * G ∧
    HasDerivWithinAt (mstar m0 G k α ℓ) (-k) (Ici G) G := by
  refine ⟨mstar_G hα m0 G k ℓ, ?_⟩
  have := (mstar_hasDerivAt (m0 := m0) (G := G) (k := k) (ℓ := ℓ) hα hα1 G).hasDerivWithinAt
    (s := Ici G)
  have hz : (G - G) ^ (β α - 1) = 0 := by
    rw [sub_self]; exact Real.zero_rpow (sub_pos.2 (one_lt_β hα hα1)).ne'
  rwa [hz, mul_zero, sub_zero] at this

/-- The second derivative of `m*` for `g > G`. -/
theorem mstar_hasDerivAt_deriv (hα : 0 < α) (hα1 : α < 1) {g : ℝ} (hg : G < g) :
    HasDerivAt (deriv (mstar m0 G k α ℓ))
      (-(β α * (β α - 1) * κ α ℓ * (g - G) ^ (β α - 2))) g := by
  rw [deriv_mstar hα hα1]
  have h1 : HasDerivAt (fun x : ℝ => (x - G) ^ (β α - 1))
      (1 * (β α - 1) * (g - G) ^ (β α - 1 - 1)) g :=
    ((hasDerivAt_id' g).sub_const G).rpow_const (Or.inl (sub_ne_zero.2 hg.ne'))
  have h2 := (hasDerivAt_const g (-k)).sub (h1.const_mul (β α * κ α ℓ))
  refine h2.congr_deriv ?_
  rw [show β α - 1 - 1 = β α - 2 by ring]
  ring

theorem mstar_deriv2_neg (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) {g : ℝ} (hg : G < g) :
    -(β α * (β α - 1) * κ α ℓ * (g - G) ^ (β α - 2)) < 0 := by
  have h1 := β_pos hα
  have h2 := sub_pos.2 (one_lt_β hα hα1)
  have h3 := κ_pos (α := α) hℓ
  have h4 := Real.rpow_pos_of_pos (sub_pos.2 hg) (β α - 2)
  have := mul_pos (mul_pos (mul_pos h1 h2) h3) h4
  linarith

/-- The three limits of `m*''(g)` as `g ↓ G`, stated for the closed form. -/
theorem deriv2_limit_lt (hα : 0 < α) (hα12 : α < 1 / 2) :
    Tendsto (fun g => -(β α * (β α - 1) * κ α ℓ * (g - G) ^ (β α - 2))) (𝓝[>] G) (𝓝 0) := by
  have hβ : 0 ≤ β α - 2 := (sub_nonneg.2 (two_lt_β hα hα12).le)
  have h1 : Tendsto (fun g : ℝ => g - G) (𝓝[>] G) (𝓝 (G - G)) :=
    ((continuous_sub_right G).tendsto G).mono_left nhdsWithin_le_nhds
  have h2 : Tendsto (fun g : ℝ => (g - G) ^ (β α - 2)) (𝓝[>] G) (𝓝 ((G - G) ^ (β α - 2))) :=
    ((Real.continuousAt_rpow_const (G - G) (β α - 2) (Or.inr hβ)).tendsto).comp h1
  rw [sub_self, Real.zero_rpow] at h2
  · have h3 := (tendsto_const_nhds : Tendsto (fun _ : ℝ => β α * (β α - 1) * κ α ℓ)
      (𝓝[>] G) (𝓝 (β α * (β α - 1) * κ α ℓ))).mul h2
    rw [mul_zero] at h3
    have h4 := h3.neg
    rw [neg_zero] at h4
    exact h4
  · exact (sub_pos.2 (two_lt_β hα hα12)).ne'

theorem deriv2_eq_half (hα : α = 1 / 2) {g : ℝ} (hg : G < g) :
    -(β α * (β α - 1) * κ α ℓ * (g - G) ^ (β α - 2)) = -2 * κ α ℓ := by
  rw [β_eq_two hα, sub_self, Real.rpow_zero]; ring

theorem deriv2_limit_gt (hα : 1 / 2 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) :
    Tendsto (fun g => -(β α * (β α - 1) * κ α ℓ * (g - G) ^ (β α - 2))) (𝓝[>] G) atBot := by
  have hα0 : 0 < α := by linarith
  have hβ2 : 0 < 2 - β α := sub_pos.2 (β_lt_two hα hα1)
  have hc : 0 < β α * (β α - 1) * κ α ℓ :=
    mul_pos (mul_pos (β_pos hα0) (sub_pos.2 (one_lt_β hα0 hα1))) (κ_pos hℓ)
  -- `g - G → 0⁺`
  have h1 : Tendsto (fun g : ℝ => g - G) (𝓝[>] G) (𝓝[>] 0) := by
    apply tendsto_nhdsWithin_of_tendsto_nhds_of_eventually_within
    · have := ((continuous_sub_right G).tendsto G).mono_left
        (nhdsWithin_le_nhds (s := Ioi G))
      rw [sub_self] at this
      exact this
    · exact eventually_nhdsWithin_of_forall fun g hg => mem_Ioi.2 (sub_pos.2 hg)
  -- `(g - G)⁻¹ → +∞`, then `((g - G)⁻¹)^{2-β} → +∞`
  have h2 : Tendsto (fun g : ℝ => ((g - G)⁻¹) ^ (2 - β α)) (𝓝[>] G) atTop :=
    (tendsto_rpow_atTop hβ2).comp (tendsto_inv_nhdsGT_zero.comp h1)
  have h3 : Tendsto (fun g : ℝ => β α * (β α - 1) * κ α ℓ * (g - G) ^ (β α - 2)) (𝓝[>] G)
      atTop := by
    refine (h2.const_mul_atTop hc).congr' ?_
    refine eventually_nhdsWithin_of_forall fun g hg => ?_
    have hpos : (0 : ℝ) ≤ g - G := (sub_pos.2 hg).le
    dsimp only
    rw [Real.inv_rpow hpos, ← Real.rpow_neg hpos, neg_sub]
  exact tendsto_neg_atTop_atBot.comp h3

/-- **Lemma prop:frontier (c).** "`m*` is strictly decreasing and strictly concave on `I`.
For `g > G`, `m*'(g) = -k - βκ(g-G)^{β-1}` and `m*''(g) = -β(β-1)κ(g-G)^{β-2} < 0`.
As `g ↓ G`, `m*''(g)` tends to `0` if `α < 1/2`, equals `-2κ` if `α = 1/2`, and tends to
`-∞` if `α > 1/2`." -/
theorem prop_frontier_c (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hk : 0 ≤ k)
    (σbar : WithTop ℝ) :
    StrictAntiOn (mstar m0 G k α ℓ) (I G ℓ α σbar) ∧
    StrictConcaveOn ℝ (I G ℓ α σbar) (mstar m0 G k α ℓ) ∧
    (∀ g, G < g → HasDerivAt (mstar m0 G k α ℓ) (-k - β α * κ α ℓ * (g - G) ^ (β α - 1)) g) ∧
    (∀ g, G < g → HasDerivAt (deriv (mstar m0 G k α ℓ))
        (-(β α * (β α - 1) * κ α ℓ * (g - G) ^ (β α - 2))) g ∧
      -(β α * (β α - 1) * κ α ℓ * (g - G) ^ (β α - 2)) < 0) ∧
    (α < 1 / 2 → Tendsto (fun g => deriv (deriv (mstar m0 G k α ℓ)) g) (𝓝[>] G) (𝓝 0)) ∧
    (α = 1 / 2 → ∀ g, G < g → deriv (deriv (mstar m0 G k α ℓ)) g = -2 * κ α ℓ) ∧
    (1 / 2 < α → Tendsto (fun g => deriv (deriv (mstar m0 G k α ℓ)) g) (𝓝[>] G) atBot) := by
  have hd2 : ∀ g, G < g → deriv (deriv (mstar m0 G k α ℓ)) g =
      -(β α * (β α - 1) * κ α ℓ * (g - G) ^ (β α - 2)) :=
    fun g hg => (mstar_hasDerivAt_deriv hα hα1 hg).deriv
  have hev : (fun g => deriv (deriv (mstar m0 G k α ℓ)) g) =ᶠ[𝓝[>] G]
      fun g => -(β α * (β α - 1) * κ α ℓ * (g - G) ^ (β α - 2)) :=
    eventually_nhdsWithin_of_forall fun g hg => hd2 g hg
  refine ⟨mstar_strictAntiOn_I hα hℓ hk σbar, mstar_strictConcaveOn_I hα hα1 hℓ σbar,
    fun g _ => mstar_hasDerivAt hα hα1 g,
    fun g hg => ⟨mstar_hasDerivAt_deriv hα hα1 hg, mstar_deriv2_neg hα hα1 hℓ hg⟩,
    fun h => (deriv2_limit_lt hα h).congr' hev.symm,
    fun h g hg => by rw [hd2 g hg, deriv2_eq_half h hg],
    fun h => (deriv2_limit_gt h hα1 hℓ).congr' hev.symm⟩

/-! ### Part (d): the uncapped frontier at large growth -/

theorem tendsto_sub_const_atTop (c : ℝ) : Tendsto (fun x : ℝ => x - c) atTop atTop :=
  tendsto_atTop_atTop.2 fun b => ⟨b + c, fun a ha => by linarith⟩

theorem tendsto_rpow_sub_atTop {p : ℝ} (hp : 0 < p) (c : ℝ) :
    Tendsto (fun x : ℝ => (x - c) ^ p) atTop atTop :=
  (tendsto_rpow_atTop hp).comp (tendsto_sub_const_atTop c)

/-- **Lemma prop:frontier (d).** "If `σ̄ = ∞`, then as `g → ∞`, `m*(g) → -∞`,
`m*'(g) → -∞` and `m*(g)/g → -∞`." (`I = [G, ∞)` when `σ̄ = ⊤`, see `I_top`.) -/
theorem prop_frontier_d (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hk : 0 ≤ k) :
    Tendsto (mstar m0 G k α ℓ) atTop atBot ∧
    Tendsto (deriv (mstar m0 G k α ℓ)) atTop atBot ∧
    Tendsto (fun g => mstar m0 G k α ℓ g / g) atTop atBot := by
  have hβ := β_pos hα
  have hβ1 := sub_pos.2 (one_lt_β hα hα1)
  have hκ := κ_pos (α := α) hℓ
  refine ⟨?_, ?_, ?_⟩
  · -- `m*(g) ≤ (m₀ - kG) - κ (g-G)^β` for `g ≥ G`, and the right side tends to `-∞`.
    have h1 : Tendsto (fun g : ℝ => κ α ℓ * (g - G) ^ β α) atTop atTop :=
      (tendsto_rpow_sub_atTop hβ G).const_mul_atTop hκ
    have h2 : Tendsto (fun g : ℝ => (m0 - k * G) + -(κ α ℓ * (g - G) ^ β α)) atTop atBot :=
      tendsto_const_nhds.add_atBot (tendsto_neg_atTop_atBot.comp h1)
    refine tendsto_atBot_mono' atTop ((eventually_ge_atTop G).mono fun g hg => ?_) h2
    rw [mstar_def]
    have := mul_le_mul_of_nonneg_left hg hk
    linarith
  · rw [deriv_mstar hα hα1]
    have h1 : Tendsto (fun g : ℝ => β α * κ α ℓ * (g - G) ^ (β α - 1)) atTop atTop :=
      (tendsto_rpow_sub_atTop hβ1 G).const_mul_atTop (mul_pos hβ hκ)
    have h2 : Tendsto (fun g : ℝ => -k + -(β α * κ α ℓ * (g - G) ^ (β α - 1))) atTop atBot :=
      tendsto_const_nhds.add_atBot (tendsto_neg_atTop_atBot.comp h1)
    refine h2.congr' (Eventually.of_forall fun g => ?_)
    ring
  · -- `m*(g)/g = m₀/g - k - κ (g-G)^{β-1} · ((g-G)/g)`, and `(g-G)/g → 1`.
    have hA : Tendsto (fun g : ℝ => m0 / g) atTop (𝓝 0) :=
      tendsto_const_nhds.div_atTop tendsto_id
    have hB : Tendsto (fun g : ℝ => (g - G) / g) atTop (𝓝 1) := by
      have : Tendsto (fun g : ℝ => 1 - G / g) atTop (𝓝 (1 - 0)) :=
        tendsto_const_nhds.sub (tendsto_const_nhds.div_atTop tendsto_id)
      rw [sub_zero] at this
      refine this.congr' ?_
      filter_upwards [eventually_gt_atTop 0] with g hg
      rw [sub_div, div_self hg.ne']
    have hC : Tendsto (fun g : ℝ => κ α ℓ * ((g - G) ^ (β α - 1) * ((g - G) / g))) atTop atTop :=
      ((tendsto_rpow_sub_atTop hβ1 G).atTop_mul_pos one_pos hB).const_mul_atTop hκ
    have hD : Tendsto (fun g : ℝ => (m0 / g - k) +
        -(κ α ℓ * ((g - G) ^ (β α - 1) * ((g - G) / g)))) atTop atBot :=
      (hA.sub tendsto_const_nhds).add_atBot (tendsto_neg_atTop_atBot.comp hC)
    refine hD.congr' ?_
    filter_upwards [eventually_gt_atTop (max 0 G)] with g hg
    have hg0 : 0 < g := lt_of_le_of_lt (le_max_left 0 G) hg
    have hgG : 0 < g - G := sub_pos.2 (lt_of_le_of_lt (le_max_right 0 G) hg)
    have hg0' := hg0.ne'
    have hgG' := hgG.ne'
    rw [mstar_def, Real.rpow_sub_one hgG']
    field_simp
    ring

end RuleOfX
