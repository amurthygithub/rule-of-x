import RuleOfX.Frontier

/-!
# Lemma prop:score (Maximal Rule-of-X score)

`y = X - k` throughout. The closed forms eq:Dstar, eq:sigstar, eq:Rstar are `Δstar`, `σstar`
and the value `m₀ + y G + (1-α) y Δ* = m₀ + y G + C_α (ℓ y)^{1/(1-α)}`.
-/

noncomputable section
open Real Set Filter Topology

set_option autoImplicit false

namespace RuleOfX

variable {m0 G k α ℓ y : ℝ} {σbar : WithTop ℝ}

/-! ### Maximizers -/

/-- `p` maximizes `R_X` on the feasible set. -/
def IsMax (m0 G k α ℓ : ℝ) (σbar : WithTop ℝ) (X : ℝ) (p : ℝ × ℝ) : Prop :=
  p ∈ Feasible m0 G k α ℓ σbar ∧ ∀ q ∈ Feasible m0 G k α ℓ σbar, score X q ≤ score X p

/-- `p` is the unique maximizer of `R_X` on the feasible set. -/
def IsUniqueMax (m0 G k α ℓ : ℝ) (σbar : WithTop ℝ) (X : ℝ) (p : ℝ × ℝ) : Prop :=
  p ∈ Feasible m0 G k α ℓ σbar ∧ ∀ q ∈ Feasible m0 G k α ℓ σbar, q ≠ p → score X q < score X p

theorem IsUniqueMax.isMax {X : ℝ} {p : ℝ × ℝ} (h : IsUniqueMax m0 G k α ℓ σbar X p) :
    IsMax m0 G k α ℓ σbar X p := by
  refine ⟨h.1, fun q hq => ?_⟩
  by_cases hqp : q = p
  · rw [hqp]
  · exact (h.2 q hq hqp).le

theorem IsUniqueMax.unique {X : ℝ} {p p' : ℝ × ℝ} (h : IsUniqueMax m0 G k α ℓ σbar X p)
    (h' : IsMax m0 G k α ℓ σbar X p') : p' = p := by
  by_contra hne
  exact absurd (h'.2 p h.1) (not_le.2 (h.2 p' h'.1 hne))

theorem IsUniqueMax.isGreatest {X : ℝ} {p : ℝ × ℝ} (h : IsUniqueMax m0 G k α ℓ σbar X p) :
    IsGreatest (score X '' Feasible m0 G k α ℓ σbar) (score X p) := by
  refine ⟨⟨p, h.1, rfl⟩, ?_⟩
  rintro _ ⟨q, hq, rfl⟩
  exact h.isMax.2 q hq

/-! ### The score along the frontier -/

/-- `R_X(g, m*(g)) = m₀ + (X-k) G + 𝓢(g - G)` with `𝓢(Δ) = (X-k) Δ - κ Δ^β`. -/
theorem score_frontier (X g : ℝ) :
    score X (g, mstar m0 G k α ℓ g) = m0 + (X - k) * G + S α ℓ (X - k) (g - G) := by
  show X * g + mstar m0 G k α ℓ g = _
  rw [mstar_def]; unfold S; ring

theorem score_le_frontier (hα : 0 < α) (hℓ : 0 < ℓ) (hσbar : 0 < σbar) {X : ℝ} {q : ℝ × ℝ}
    (hq : q ∈ Feasible m0 G k α ℓ σbar) :
    score X q ≤ m0 + (X - k) * G + S α ℓ (X - k) (q.1 - G) := by
  rw [feasible_iff hα hℓ hσbar] at hq
  rw [← score_frontier]
  show X * q.1 + q.2 ≤ X * q.1 + mstar m0 G k α ℓ q.1
  linarith [hq.2]

/-! ### Facts about `𝓢` -/

theorem S_hasDerivAt (hα : 0 < α) (hα1 : α < 1) (y Δ : ℝ) :
    HasDerivAt (S α ℓ y) (y - β α * κ α ℓ * Δ ^ (β α - 1)) Δ := by
  have h1 : HasDerivAt (fun x : ℝ => x ^ β α) (β α * Δ ^ (β α - 1)) Δ :=
    Real.hasDerivAt_rpow_const (Or.inr (one_lt_β hα hα1).le)
  have h2 := ((hasDerivAt_id' Δ).const_mul y).sub (h1.const_mul (κ α ℓ))
  have hf : S α ℓ y = fun x => y * x - κ α ℓ * x ^ β α := rfl
  rw [hf]
  exact h2.congr_deriv (by ring)

theorem S_continuous (hα : 0 < α) (hα1 : α < 1) (y : ℝ) : Continuous (S α ℓ y) :=
  continuous_iff_continuousAt.2 fun Δ => (S_hasDerivAt hα hα1 y Δ).continuousAt

theorem S_zero (hα : 0 < α) (y : ℝ) : S α ℓ y 0 = 0 := by
  unfold S; rw [Real.zero_rpow (β_pos hα).ne']; ring

theorem S_nonpos (hℓ : 0 < ℓ) (hy : y ≤ 0) {Δ : ℝ} (hΔ : 0 ≤ Δ) : S α ℓ y Δ ≤ 0 := by
  unfold S
  have h1 := mul_nonneg (κ_pos (α := α) hℓ).le (Real.rpow_nonneg hΔ (β α))
  nlinarith

theorem S_neg (hα : 0 < α) (hℓ : 0 < ℓ) (hy : y ≤ 0) {Δ : ℝ} (hΔ : 0 < Δ) : S α ℓ y Δ < 0 := by
  unfold S
  have h1 := mul_pos (κ_pos (α := α) hℓ) (Real.rpow_pos_of_pos hΔ (β α))
  nlinarith

theorem Δstar_pos (hα : 0 < α) (hℓ : 0 < ℓ) (hy : 0 < y) : 0 < Δstar α ℓ y :=
  mul_pos (Real.rpow_pos_of_pos hℓ _) (Real.rpow_pos_of_pos (mul_pos hα hy) _)

theorem Δstar_nonneg (hα : 0 < α) (hℓ : 0 < ℓ) (hy : 0 ≤ y) : 0 ≤ Δstar α ℓ y :=
  mul_nonneg (Real.rpow_nonneg hℓ.le _) (Real.rpow_nonneg (mul_nonneg hα.le hy) _)

/-- `(Δ*)^{β-1} = ℓ^β α y`. -/
theorem Δstar_rpow (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hy : 0 < y) :
    Δstar α ℓ y ^ (β α - 1) = ℓ ^ β α * (α * y) := by
  unfold Δstar
  have hαy : 0 < α * y := mul_pos hα hy
  have h1 : 0 ≤ ℓ ^ (1 / (1 - α)) := Real.rpow_nonneg hℓ.le _
  have h2 : 0 ≤ (α * y) ^ (α / (1 - α)) := Real.rpow_nonneg hαy.le _
  rw [Real.mul_rpow h1 h2, ← Real.rpow_mul hℓ.le, ← Real.rpow_mul hαy.le]
  have h1α : (1 - α) ≠ 0 := by linarith
  have hα0 : α ≠ 0 := hα.ne'
  have e1 : 1 / (1 - α) * (β α - 1) = β α := by
    unfold β; field_simp; ring
  have e2 : α / (1 - α) * (β α - 1) = 1 := by
    unfold β; field_simp
  rw [e1, e2, Real.rpow_one]

/-- First-order condition: `β κ (Δ*)^{β-1} = y`. -/
theorem foc (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hy : 0 < y) :
    β α * κ α ℓ * Δstar α ℓ y ^ (β α - 1) = y := by
  rw [Δstar_rpow hα hα1 hℓ hy]
  have hA := κ_mul_rpow_β (α := α) hℓ
  have hB := α_mul_β hα
  linear_combination (y * (κ α ℓ * ℓ ^ β α)) * hB + y * hA

theorem S_strictMonoOn (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hy : 0 < y) :
    StrictMonoOn (S α ℓ y) (Icc 0 (Δstar α ℓ y)) := by
  refine strictMonoOn_of_deriv_pos (convex_Icc _ _) (S_continuous hα hα1 y).continuousOn ?_
  intro Δ hΔ
  rw [interior_Icc] at hΔ
  rw [(S_hasDerivAt hα hα1 y Δ).deriv]
  have hβκ : 0 < β α * κ α ℓ := mul_pos (β_pos hα) (κ_pos hℓ)
  have h1 := Real.rpow_lt_rpow hΔ.1.le hΔ.2 (sub_pos.2 (one_lt_β hα hα1))
  have h2 := mul_lt_mul_of_pos_left h1 hβκ
  have h3 := foc hα hα1 hℓ hy
  linarith

theorem S_strictAntiOn (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hy : 0 < y) :
    StrictAntiOn (S α ℓ y) (Ici (Δstar α ℓ y)) := by
  refine strictAntiOn_of_deriv_neg (convex_Ici _) (S_continuous hα hα1 y).continuousOn ?_
  intro Δ hΔ
  rw [interior_Ici] at hΔ
  rw [(S_hasDerivAt hα hα1 y Δ).deriv]
  have hβκ : 0 < β α * κ α ℓ := mul_pos (β_pos hα) (κ_pos hℓ)
  have h1 := Real.rpow_lt_rpow (Δstar_pos hα hℓ hy).le hΔ (sub_pos.2 (one_lt_β hα hα1))
  have h2 := mul_lt_mul_of_pos_left h1 hβκ
  have h3 := foc hα hα1 hℓ hy
  linarith

theorem S_le_S_Δstar (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hy : 0 < y) {Δ : ℝ}
    (hΔ : 0 ≤ Δ) : S α ℓ y Δ ≤ S α ℓ y (Δstar α ℓ y) := by
  rcases le_or_lt Δ (Δstar α ℓ y) with h | h
  · exact (S_strictMonoOn hα hα1 hℓ hy).monotoneOn ⟨hΔ, h⟩ ⟨(Δstar_pos hα hℓ hy).le, le_rfl⟩ h
  · exact ((S_strictAntiOn hα hα1 hℓ hy) left_mem_Ici h.le h).le

theorem S_lt_S_Δstar (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hy : 0 < y) {Δ : ℝ}
    (hΔ : 0 ≤ Δ) (hne : Δ ≠ Δstar α ℓ y) : S α ℓ y Δ < S α ℓ y (Δstar α ℓ y) := by
  rcases lt_or_gt_of_ne hne with h | h
  · exact (S_strictMonoOn hα hα1 hℓ hy) ⟨hΔ, h.le⟩ ⟨(Δstar_pos hα hℓ hy).le, le_rfl⟩ h
  · exact (S_strictAntiOn hα hα1 hℓ hy) left_mem_Ici h.le h

theorem S_le_min (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hy : 0 < y) {Δ D : ℝ}
    (hΔ : 0 ≤ Δ) (hΔD : Δ ≤ D) : S α ℓ y Δ ≤ S α ℓ y (min (Δstar α ℓ y) D) := by
  rcases le_or_lt (Δstar α ℓ y) D with h | h
  · rw [min_eq_left h]; exact S_le_S_Δstar hα hα1 hℓ hy hΔ
  · rw [min_eq_right h.le]
    exact (S_strictMonoOn hα hα1 hℓ hy).monotoneOn ⟨hΔ, hΔD.trans h.le⟩ ⟨hΔ.trans hΔD, h.le⟩ hΔD

/-! ### Closed forms -/

/-- `κ (Δ*)^β = α y Δ*`: the spend that produces `Δ*`. -/
theorem κ_Δstar_rpow (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hy : 0 < y) :
    κ α ℓ * Δstar α ℓ y ^ β α = α * y * Δstar α ℓ y := by
  have hpos := Δstar_pos hα hℓ hy
  have h1 : Δstar α ℓ y ^ β α = Δstar α ℓ y ^ (β α - 1) * Δstar α ℓ y := by
    rw [Real.rpow_sub_one hpos.ne', div_mul_cancel₀ _ hpos.ne']
  rw [h1]
  have hfoc := foc hα hα1 hℓ hy
  have hab := α_mul_β hα
  linear_combination (α * Δstar α ℓ y) * hfoc -
    (κ α ℓ * Δstar α ℓ y ^ (β α - 1) * Δstar α ℓ y) * hab

/-- eq:sigstar, second form: `σ* = α (X-k) Δ*`. -/
theorem σstar_eq (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hy : 0 < y) :
    σstar α ℓ y = α * y * Δstar α ℓ y := by
  unfold σstar Δstar
  have hαy : 0 < α * y := mul_pos hα hy
  have e : α * ℓ * y = (α * y) * ℓ := by ring
  rw [e, Real.mul_rpow hαy.le hℓ.le]
  have h2 : (α * y) ^ (1 / (1 - α)) = (α * y) ^ (α / (1 - α)) * (α * y) := by
    rw [show (1 : ℝ) / (1 - α) = α / (1 - α) + 1 by linarith [q_sub_one hα1],
      Real.rpow_add_one hαy.ne']
  rw [h2]; ring

theorem σstar_nonneg (hα : 0 < α) (hℓ : 0 < ℓ) (hy : 0 ≤ y) : 0 ≤ σstar α ℓ y :=
  Real.rpow_nonneg (mul_nonneg (mul_nonneg hα.le hℓ.le) hy) _

/-- `G + ℓ (σ*)^α = G + Δ*`. -/
theorem growth_σstar (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hy : 0 < y) :
    growth G ℓ α (σstar α ℓ y) = G + Δstar α ℓ y := by
  rw [σstar_eq hα hα1 hℓ hy, ← κ_Δstar_rpow hα hα1 hℓ hy]
  exact growth_κ_rpow hα hℓ (Δstar_pos hα hℓ hy).le

theorem spendOf_Δstar (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hy : 0 < y) :
    spendOf G α ℓ (G + Δstar α ℓ y) = σstar α ℓ y := by
  rw [← growth_σstar (G := G) hα hα1 hℓ hy]
  exact spendOf_growth hα hℓ (σstar_nonneg hα hℓ hy.le)

/-- `𝓢(Δ*) = (1-α) y Δ*`. -/
theorem S_Δstar (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hy : 0 < y) :
    S α ℓ y (Δstar α ℓ y) = (1 - α) * y * Δstar α ℓ y := by
  unfold S; rw [κ_Δstar_rpow hα hα1 hℓ hy]; ring

/-- eq:Rstar, equality of the two forms: `(1-α) y Δ* = C_α (ℓ y)^{1/(1-α)}`. -/
theorem Π_eq (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hy : 0 < y) :
    (1 - α) * y * Δstar α ℓ y = Cα α * (ℓ * y) ^ (1 / (1 - α)) := by
  unfold Δstar Cα
  rw [Real.mul_rpow hℓ.le hy.le, Real.mul_rpow hα.le hy.le]
  have h2 : y ^ (1 / (1 - α)) = y ^ (α / (1 - α)) * y := by
    rw [show (1 : ℝ) / (1 - α) = α / (1 - α) + 1 by linarith [q_sub_one hα1],
      Real.rpow_add_one hy.ne']
  rw [h2]; ring

theorem Δplus_of_pos (hy : 0 ≤ y) : Δplus α ℓ y = Δstar α ℓ y := by
  unfold Δplus; rw [max_eq_left hy]

theorem Δplus_of_nonpos (hα : 0 < α) (hα1 : α < 1) (hy : y ≤ 0) : Δplus α ℓ y = 0 := by
  unfold Δplus Δstar
  rw [max_eq_right hy, mul_zero, Real.zero_rpow, mul_zero]
  exact (div_pos hα (by linarith)).ne'

theorem σplus_of_pos (hy : 0 ≤ y) : σplus α ℓ y = σstar α ℓ y := by
  unfold σplus; rw [max_eq_left hy]

theorem σplus_of_nonpos (hα1 : α < 1) (hy : y ≤ 0) : σplus α ℓ y = 0 := by
  unfold σplus σstar
  rw [max_eq_right hy, mul_zero, Real.zero_rpow (q_pos hα1).ne']

theorem gstar_of_lt {X : ℝ} (hX : k < X) : gstar G k α ℓ X = G + Δstar α ℓ (X - k) := by
  unfold gstar; rw [Δplus_of_pos (sub_pos.2 hX).le]

theorem gstar_of_le (hα : 0 < α) (hα1 : α < 1) {X : ℝ} (hX : X ≤ k) : gstar G k α ℓ X = G := by
  unfold gstar; rw [Δplus_of_nonpos hα hα1 (sub_nonpos.2 hX), add_zero]

theorem Π_of_nonpos (hα : 0 < α) (hα1 : α < 1) (hy : y ≤ 0) : Π α ℓ y = 0 := by
  unfold Π; rw [Δplus_of_nonpos hα hα1 hy, mul_zero]

theorem Π_of_pos (hy : 0 ≤ y) : Π α ℓ y = (1 - α) * y * Δstar α ℓ y := by
  unfold Π; rw [Δplus_of_pos hy]

/-- `Π = C_α (ℓ y₊)^{1/(1-α)}` for every `y`. -/
theorem Π_eq_Cα (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (y : ℝ) :
    Π α ℓ y = Cα α * (ℓ * max y 0) ^ (1 / (1 - α)) := by
  rcases le_or_lt y 0 with hy | hy
  · rw [Π_of_nonpos hα hα1 hy, max_eq_right hy, mul_zero, Real.zero_rpow (q_pos hα1).ne',
      mul_zero]
  · rw [Π_of_pos hy.le, max_eq_left hy.le]
    exact Π_eq hα hα1 hℓ hy

/-! ### Part (a) -/

theorem isMax_mem_frontier (hα : 0 < α) (hℓ : 0 < ℓ) (hk : 0 ≤ k) (hσbar : 0 < σbar)
    {X : ℝ} {p : ℝ × ℝ} (hp : IsMax m0 G k α ℓ σbar X p) : p ∈ Frontier m0 G k α ℓ σbar := by
  rw [frontier_eq hα hℓ hk hσbar]
  have hp' := (feasible_iff hα hℓ hσbar p).1 hp.1
  refine ⟨hp'.1, le_antisymm hp'.2 ?_⟩
  have h : X * p.1 + mstar m0 G k α ℓ p.1 ≤ X * p.1 + p.2 :=
    hp.2 (p.1, mstar m0 G k α ℓ p.1) ((feasible_iff hα hℓ hσbar _).2 ⟨hp'.1, le_rfl⟩)
  linarith

/-- The frontier point with excess growth `Δ` is feasible when `Δ ∈ [0, ḡ - G]`. -/
theorem frontier_point_feasible (hα : 0 < α) (hℓ : 0 < ℓ) (hσbar : 0 < σbar) {g : ℝ}
    (hg : g ∈ I G ℓ α σbar) : (g, mstar m0 G k α ℓ g) ∈ Feasible m0 G k α ℓ σbar :=
  (feasible_iff hα hℓ hσbar _).2 ⟨hg, le_rfl⟩

theorem mem_I_top {g : ℝ} (hg : G ≤ g) : g ∈ I G ℓ α (⊤ : WithTop ℝ) := by
  rw [I_top]; exact hg

theorem mem_I_coe {b g : ℝ} (hg : G ≤ g) (hgb : g ≤ growth G ℓ α b) :
    g ∈ I G ℓ α (b : WithTop ℝ) := by
  rw [I_coe]; exact ⟨hg, hgb⟩

/-- Existence of a maximizer (with any cap). -/
theorem exists_isMax (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hk : 0 ≤ k) (hσbar : 0 < σbar)
    (X : ℝ) : ∃ p, IsMax m0 G k α ℓ σbar X p := by
  rcases le_or_lt X k with hXk | hXk
  · refine ⟨(G, mstar m0 G k α ℓ G), frontier_point_feasible hα hℓ hσbar (G_mem_I hα hℓ hσbar),
      fun q hq => ?_⟩
    have h1 := score_le_frontier (X := X) hα hℓ hσbar hq
    have hqI := ((feasible_iff hα hℓ hσbar q).1 hq).1.1
    have h2 := S_nonpos (α := α) hℓ (sub_nonpos.2 hXk) (sub_nonneg.2 hqI)
    rw [score_frontier, sub_self, S_zero hα]
    linarith
  · have hy0 : 0 < X - k := sub_pos.2 hXk
    induction σbar using WithTop.recTopCoe with
    | top =>
      refine ⟨(G + Δstar α ℓ (X - k), mstar m0 G k α ℓ (G + Δstar α ℓ (X - k))),
        frontier_point_feasible hα hℓ hσbar
          (mem_I_top (le_add_of_nonneg_right (Δstar_pos hα hℓ hy0).le)), fun q hq => ?_⟩
      have h1 := score_le_frontier (X := X) hα hℓ hσbar hq
      have hqI := ((feasible_iff hα hℓ hσbar q).1 hq).1.1
      rw [score_frontier, add_sub_cancel_left]
      exact h1.trans (add_le_add_left (S_le_S_Δstar hα hα1 hℓ hy0 (sub_nonneg.2 hqI)) _)
    | coe b =>
      have hb : (0 : ℝ) < b := by exact_mod_cast hσbar
      set D := ℓ * b ^ α with hD
      have hD0 : 0 ≤ D := mul_nonneg hℓ.le (Real.rpow_nonneg hb.le _)
      have hmin0 : 0 ≤ min (Δstar α ℓ (X - k)) D := le_min (Δstar_pos hα hℓ hy0).le hD0
      refine ⟨(G + min (Δstar α ℓ (X - k)) D,
        mstar m0 G k α ℓ (G + min (Δstar α ℓ (X - k)) D)),
        frontier_point_feasible hα hℓ hσbar (mem_I_coe (le_add_of_nonneg_right hmin0) ?_),
        fun q hq => ?_⟩
      · unfold growth; linarith [min_le_right (Δstar α ℓ (X - k)) D]
      · have h1 := score_le_frontier (X := X) hα hℓ hσbar hq
        have hqI := (feasible_iff hα hℓ hσbar q).1 hq
        rw [I_coe] at hqI
        have hqD : q.1 - G ≤ D := by
          have := hqI.1.2; unfold growth at this; linarith
        rw [score_frontier, add_sub_cancel_left]
        exact h1.trans (add_le_add_left (S_le_min hα hα1 hℓ hy0 (sub_nonneg.2 hqI.1.1) hqD) _)

/-- **Lemma prop:score (a).** "Iso-score sets `{(g,m) : Xg + m = c}` are straight lines of
slope `-X`. A maximizer of `R_X` on `𝓕` exists, and every maximizer lies on the frontier." -/
theorem prop_score_a (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hk : 0 ≤ k) (hσbar : 0 < σbar)
    (X : ℝ) :
    (∀ c : ℝ, {p : ℝ × ℝ | score X p = c} = {p | p.2 = c - X * p.1}) ∧
    (∃ p, IsMax m0 G k α ℓ σbar X p) ∧
    (∀ p, IsMax m0 G k α ℓ σbar X p → p ∈ Frontier m0 G k α ℓ σbar) := by
  refine ⟨fun c => ?_, exists_isMax hα hα1 hℓ hk hσbar X,
    fun p hp => isMax_mem_frontier hα hℓ hk hσbar hp⟩
  ext p
  simp only [score, Set.mem_setOf_eq]
  constructor <;> intro h <;> linarith

/-! ### Part (b) -/

theorem gstar_mem_I (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hσbar : 0 < σbar) {X : ℝ}
    (hX : k < X) (hcap : (σstar α ℓ (X - k) : WithTop ℝ) ≤ σbar) :
    gstar G k α ℓ X ∈ I G ℓ α σbar := by
  have hy0 : 0 < X - k := sub_pos.2 hX
  rw [gstar_of_lt hX]
  induction σbar using WithTop.recTopCoe with
  | top => exact mem_I_top (le_add_of_nonneg_right (Δstar_pos hα hℓ hy0).le)
  | coe b =>
    have hb : (0 : ℝ) < b := by exact_mod_cast hσbar
    have hσb : σstar α ℓ (X - k) ≤ b := by exact_mod_cast hcap
    refine mem_I_coe (le_add_of_nonneg_right (Δstar_pos hα hℓ hy0).le) ?_
    rw [← growth_σstar hα hα1 hℓ hy0]
    exact growth_monotoneOn hα hℓ (σstar_nonneg hα hℓ hy0.le) hb.le hσb

/-- The interior optimum is the unique maximizer. -/
theorem isUniqueMax_gstar (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hk : 0 ≤ k)
    (hσbar : 0 < σbar) {X : ℝ} (hX : k < X)
    (hcap : (σstar α ℓ (X - k) : WithTop ℝ) ≤ σbar) :
    IsUniqueMax m0 G k α ℓ σbar X (gstar G k α ℓ X, mstar m0 G k α ℓ (gstar G k α ℓ X)) := by
  have hy0 : 0 < X - k := sub_pos.2 hX
  have hgI := gstar_mem_I hα hα1 hℓ hσbar hX hcap
  refine ⟨frontier_point_feasible hα hℓ hσbar hgI, fun q hq hne => ?_⟩
  rw [gstar_of_lt hX] at hne ⊢
  have hq' := (feasible_iff hα hℓ hσbar q).1 hq
  have h1 := score_le_frontier (X := X) hα hℓ hσbar hq
  rw [score_frontier, add_sub_cancel_left]
  by_cases hg : q.1 = G + Δstar α ℓ (X - k)
  · have h2 : q.2 ≠ mstar m0 G k α ℓ q.1 := fun h => hne (Prod.ext hg (by
      show q.2 = mstar m0 G k α ℓ (G + Δstar α ℓ (X - k)); rw [h, hg]))
    have h3 : q.2 < mstar m0 G k α ℓ q.1 := lt_of_le_of_ne hq'.2 h2
    calc score X q = X * q.1 + q.2 := rfl
      _ < X * q.1 + mstar m0 G k α ℓ q.1 := by linarith
      _ = score X (q.1, mstar m0 G k α ℓ q.1) := rfl
      _ = m0 + (X - k) * G + S α ℓ (X - k) (q.1 - G) := score_frontier X q.1
      _ = m0 + (X - k) * G + S α ℓ (X - k) (Δstar α ℓ (X - k)) := by
        rw [hg, add_sub_cancel_left]
  · have h3 := S_lt_S_Δstar hα hα1 hℓ hy0 (sub_nonneg.2 hq'.1.1) (fun h => hg (by linarith))
    linarith

/-- **Lemma prop:score (b).** "If `X > k`, the maximizer is unique and interior (`g* > G`), and
there the frontier is tangent to the iso-score line: `m*'(g*) = -X` (if `σ* = σ̄`, the
maximizer is the right endpoint `ḡ` of `I` and the tangency holds for the left derivative).
In closed form, `Δ* = g* - G = (λh)^{1/(1-α)} [α(X-k)]^{α/(1-α)}`,
`σ* = [αλh(X-k)]^{1/(1-α)} = α(X-k)Δ*`,
`R*_X = m₀ + (X-k)G + (1-α)(X-k)Δ* = m₀ + (X-k)G + C_α[λh(X-k)]^{1/(1-α)}`, and the margin at
the optimum is `m*(g*) = m₀ - kg* - α(X-k)Δ*`."  (Here `ℓ = λh`; the cap condition
`σ* ≤ σ̄` is the hypothesis `hcap`.) -/
theorem prop_score_b (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hk : 0 ≤ k) (hσbar : 0 < σbar)
    {X : ℝ} (hX : k < X) (hcap : (σstar α ℓ (X - k) : WithTop ℝ) ≤ σbar) :
    IsUniqueMax m0 G k α ℓ σbar X (gstar G k α ℓ X, mstar m0 G k α ℓ (gstar G k α ℓ X)) ∧
    G < gstar G k α ℓ X ∧
    HasDerivAt (mstar m0 G k α ℓ) (-X) (gstar G k α ℓ X) ∧
    HasDerivWithinAt (mstar m0 G k α ℓ) (-X) (Iic (gstar G k α ℓ X)) (gstar G k α ℓ X) ∧
    ((σstar α ℓ (X - k) : WithTop ℝ) = σbar → (gstar G k α ℓ X : WithTop ℝ) = gbar G ℓ α σbar) ∧
    gstar G k α ℓ X - G = ℓ ^ (1 / (1 - α)) * (α * (X - k)) ^ (α / (1 - α)) ∧
    gstar G k α ℓ X - G = Δstar α ℓ (X - k) ∧
    σstar α ℓ (X - k) = (α * ℓ * (X - k)) ^ (1 / (1 - α)) ∧
    σstar α ℓ (X - k) = α * (X - k) * Δstar α ℓ (X - k) ∧
    spendOf G α ℓ (gstar G k α ℓ X) = σstar α ℓ (X - k) ∧
    score X (gstar G k α ℓ X, mstar m0 G k α ℓ (gstar G k α ℓ X)) =
      m0 + (X - k) * G + (1 - α) * (X - k) * Δstar α ℓ (X - k) ∧
    score X (gstar G k α ℓ X, mstar m0 G k α ℓ (gstar G k α ℓ X)) =
      m0 + (X - k) * G + Cα α * (ℓ * (X - k)) ^ (1 / (1 - α)) ∧
    mstar m0 G k α ℓ (gstar G k α ℓ X) =
      m0 - k * gstar G k α ℓ X - α * (X - k) * Δstar α ℓ (X - k) := by
  have hy0 : 0 < X - k := sub_pos.2 hX
  have hg := gstar_of_lt (G := G) (α := α) (ℓ := ℓ) hX
  have hΔ := Δstar_pos hα hℓ hy0
  have htan : HasDerivAt (mstar m0 G k α ℓ) (-X) (gstar G k α ℓ X) := by
    refine (mstar_hasDerivAt hα hα1 _).congr_deriv ?_
    rw [hg, add_sub_cancel_left, foc hα hα1 hℓ hy0]; ring
  refine ⟨isUniqueMax_gstar hα hα1 hℓ hk hσbar hX hcap, by rw [hg]; linarith, htan,
    htan.hasDerivWithinAt, ?_, by rw [hg]; unfold Δstar; ring, by rw [hg]; ring, rfl,
    σstar_eq hα hα1 hℓ hy0, by rw [hg]; exact spendOf_Δstar hα hα1 hℓ hy0, ?_, ?_, ?_⟩
  · intro h
    rw [← h, hg]
    simp [gbar, WithTop.map_coe, growth_σstar hα hα1 hℓ hy0]
  · rw [score_frontier, hg, add_sub_cancel_left, S_Δstar hα hα1 hℓ hy0]
  · rw [score_frontier, hg, add_sub_cancel_left, S_Δstar hα hα1 hℓ hy0, Π_eq hα hα1 hℓ hy0]
  · unfold mstar
    rw [hg, spendOf_Δstar hα hα1 hℓ hy0, σstar_eq hα hα1 hℓ hy0]

/-! ### Part (c) -/

/-- **Lemma prop:score (c).** "If `X ≤ k`, the unique maximizer is the corner `g* = G` with
`σ* = 0`, and `R*_X = m₀ + (X-k)G`. This part does not need the cap condition." -/
theorem prop_score_c (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hk : 0 ≤ k) (hσbar : 0 < σbar)
    {X : ℝ} (hX : X ≤ k) :
    IsUniqueMax m0 G k α ℓ σbar X (G, mstar m0 G k α ℓ G) ∧
    gstar G k α ℓ X = G ∧ σplus α ℓ (X - k) = 0 ∧ spendOf G α ℓ G = 0 ∧
    score X (G, mstar m0 G k α ℓ G) = m0 + (X - k) * G := by
  have hy0 : X - k ≤ 0 := sub_nonpos.2 hX
  refine ⟨⟨frontier_point_feasible hα hℓ hσbar (G_mem_I hα hℓ hσbar), fun q hq hne => ?_⟩,
    gstar_of_le hα hα1 hX, σplus_of_nonpos hα1 hy0, spendOf_self hα, ?_⟩
  · have hq' := (feasible_iff hα hℓ hσbar q).1 hq
    have h1 := score_le_frontier (X := X) hα hℓ hσbar hq
    rw [score_frontier, sub_self, S_zero hα]
    rcases lt_or_eq_of_le hq'.1.1 with hg | hg
    · have h3 := S_neg (α := α) hα hℓ hy0 (sub_pos.2 hg)
      linarith
    · have h2 : q.2 ≠ mstar m0 G k α ℓ q.1 := fun h => hne (Prod.ext hg.symm (by
        show q.2 = mstar m0 G k α ℓ G; rw [h, ← hg]))
      have h3 : q.2 < mstar m0 G k α ℓ q.1 := lt_of_le_of_ne hq'.2 h2
      calc score X q = X * q.1 + q.2 := rfl
        _ < X * q.1 + mstar m0 G k α ℓ q.1 := by linarith
        _ = score X (q.1, mstar m0 G k α ℓ q.1) := rfl
        _ = m0 + (X - k) * G + S α ℓ (X - k) (q.1 - G) := score_frontier X q.1
        _ = m0 + (X - k) * G + 0 := by rw [← hg, sub_self, S_zero hα]
  · rw [score_frontier, sub_self, S_zero hα, add_zero]

/-! ### Part (d): duality -/

/-- The weight for which the frontier point `g` is optimal: `X(g) = -m*'(g) = k + βκ(g-G)^{β-1}`. -/
def Xof (G k α ℓ g : ℝ) : ℝ := k + β α * κ α ℓ * (g - G) ^ (β α - 1)

theorem Xof_eq_neg_deriv (hα : 0 < α) (hα1 : α < 1) (g : ℝ) :
    Xof G k α ℓ g = -(deriv (mstar m0 G k α ℓ) g) := by
  rw [deriv_mstar hα hα1]; unfold Xof; ring

theorem I_mem_nhds (hσbar : 0 < σbar) {g : ℝ} (hg : G < g)
    (hlt : (g : WithTop ℝ) < gbar G ℓ α σbar) : I G ℓ α σbar ∈ 𝓝 g := by
  induction σbar using WithTop.recTopCoe with
  | top => rw [I_top]; exact Ici_mem_nhds hg
  | coe b =>
    rw [I_coe]
    have : g < growth G ℓ α b := by
      simp only [gbar, WithTop.map_coe, WithTop.coe_lt_coe] at hlt
      exact hlt
    exact Icc_mem_nhds hg this

/-- Fermat: a maximizer interior to `I` satisfies `X = X(g)`. -/
theorem eq_Xof_of_isMax (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hσbar : 0 < σbar)
    {X g : ℝ} (hg : G < g) (hlt : (g : WithTop ℝ) < gbar G ℓ α σbar)
    (hmax : IsMax m0 G k α ℓ σbar X (g, mstar m0 G k α ℓ g)) : X = Xof G k α ℓ g := by
  have hloc : IsLocalMax (fun x => X * x + mstar m0 G k α ℓ x) g := by
    refine IsMaxOn.isLocalMax (isMaxOn_iff.2 fun x hx => ?_) (I_mem_nhds hσbar hg hlt)
    exact hmax.2 (x, mstar m0 G k α ℓ x) (frontier_point_feasible hα hℓ hσbar hx)
  have hd : HasDerivAt (fun x => X * x + mstar m0 G k α ℓ x)
      (X * 1 + (-k - β α * κ α ℓ * (g - G) ^ (β α - 1))) g :=
    ((hasDerivAt_id' g).const_mul X).add (mstar_hasDerivAt hα hα1 g)
  have := hloc.hasDerivAt_eq_zero hd
  unfold Xof; linarith

theorem lt_Xof (hα : 0 < α) (hℓ : 0 < ℓ) {g : ℝ} (hg : G < g) : k < Xof G k α ℓ g := by
  unfold Xof
  have := mul_pos (mul_pos (β_pos hα) (κ_pos (α := α) hℓ))
    (Real.rpow_pos_of_pos (sub_pos.2 hg) (β α - 1))
  linarith

/-- For `X = X(g)`, `Δ*(X - k) = g - G`. -/
theorem Δstar_Xof (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) {g : ℝ} (hg : G < g) :
    Δstar α ℓ (Xof G k α ℓ g - k) = g - G := by
  have hy : 0 < Xof G k α ℓ g - k := sub_pos.2 (lt_Xof hα hℓ hg)
  have h1 := foc hα hα1 hℓ hy
  have h2 : β α * κ α ℓ * (g - G) ^ (β α - 1) = Xof G k α ℓ g - k := by unfold Xof; ring
  have hβκ : 0 < β α * κ α ℓ := mul_pos (β_pos hα) (κ_pos hℓ)
  have h3 : Δstar α ℓ (Xof G k α ℓ g - k) ^ (β α - 1) = (g - G) ^ (β α - 1) := by
    have := h1.trans h2.symm
    exact mul_left_cancel₀ hβκ.ne' this
  exact Real.rpow_left_injOn (sub_pos.2 (one_lt_β hα hα1)).ne'
    (Δstar_pos hα hℓ hy).le (sub_pos.2 hg).le h3

/-- **Lemma prop:score (d), first two claims.** "Each frontier point with `G < g < ḡ` is the
unique maximizer of `R_X` for exactly one weight, `X(g) = -m*'(g) = k + βκ(g-G)^{β-1}`. The
point `g = G` is a maximizer if and only if `X ≤ k`." -/
theorem prop_score_d (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hk : 0 ≤ k) (hσbar : 0 < σbar) :
    (∀ g, G < g → (g : WithTop ℝ) < gbar G ℓ α σbar →
      Xof G k α ℓ g = -(deriv (mstar m0 G k α ℓ) g) ∧
      Xof G k α ℓ g = k + β α * κ α ℓ * (g - G) ^ (β α - 1) ∧
      ∀ X, IsUniqueMax m0 G k α ℓ σbar X (g, mstar m0 G k α ℓ g) ↔ X = Xof G k α ℓ g) ∧
    (∀ X, IsMax m0 G k α ℓ σbar X (G, mstar m0 G k α ℓ G) ↔ X ≤ k) := by
  constructor
  · intro g hg hlt
    refine ⟨Xof_eq_neg_deriv hα hα1 g, rfl, fun X => ⟨fun h => eq_Xof_of_isMax hα hα1 hℓ hσbar
      hg hlt h.isMax, fun hX => ?_⟩⟩
    subst hX
    have hXk : k < Xof G k α ℓ g := lt_Xof hα hℓ hg
    have hgeq : gstar G k α ℓ (Xof G k α ℓ g) = g := by
      rw [gstar_of_lt hXk, Δstar_Xof hα hα1 hℓ hg]; ring
    have hcap : (σstar α ℓ (Xof G k α ℓ g - k) : WithTop ℝ) ≤ σbar := by
      have hy0 : 0 < Xof G k α ℓ g - k := sub_pos.2 hXk
      have hs : σstar α ℓ (Xof G k α ℓ g - k) = spendOf G α ℓ g := by
        rw [← spendOf_Δstar hα hα1 hℓ hy0, Δstar_Xof hα hα1 hℓ hg]; congr 1; ring
      induction σbar using WithTop.recTopCoe with
      | top => exact le_top
      | coe b =>
        have hb : (0 : ℝ) < b := by exact_mod_cast hσbar
        have hgb : g < growth G ℓ α b := by
          simp only [gbar, WithTop.map_coe, WithTop.coe_lt_coe] at hlt
          exact hlt
        rw [hs]
        have := spendOf_monotoneOn (G := G) hα hℓ hg.le (growth_nonneg_sub hℓ hb.le) hgb.le
        rw [spendOf_growth hα hℓ hb.le] at this
        exact_mod_cast this
    have := isUniqueMax_gstar (m0 := m0) hα hα1 hℓ hk hσbar hXk hcap
    rwa [hgeq] at this
  · intro X
    constructor
    · intro hmax
      by_contra hXk
      push_neg at hXk
      have hy0 : 0 < X - k := sub_pos.2 hXk
      -- a feasible point with a strictly higher score
      obtain ⟨Δ, hΔ0, hΔle, hΔI⟩ : ∃ Δ, 0 < Δ ∧ Δ ≤ Δstar α ℓ (X - k) ∧ G + Δ ∈ I G ℓ α σbar := by
        induction σbar using WithTop.recTopCoe with
        | top =>
          exact ⟨Δstar α ℓ (X - k), Δstar_pos hα hℓ hy0, le_rfl,
            mem_I_top (le_add_of_nonneg_right (Δstar_pos hα hℓ hy0).le)⟩
        | coe b =>
          have hb : (0 : ℝ) < b := by exact_mod_cast hσbar
          have hD : 0 < ℓ * b ^ α := mul_pos hℓ (Real.rpow_pos_of_pos hb _)
          refine ⟨min (Δstar α ℓ (X - k)) (ℓ * b ^ α), lt_min (Δstar_pos hα hℓ hy0) hD,
            min_le_left _ _, mem_I_coe (le_add_of_nonneg_right (lt_min (Δstar_pos hα hℓ hy0) hD).le)
              ?_⟩
          unfold growth; linarith [min_le_right (Δstar α ℓ (X - k)) (ℓ * b ^ α)]
      have h1 := hmax.2 _ (frontier_point_feasible (m0 := m0) (k := k) hα hℓ hσbar hΔI)
      rw [score_frontier, score_frontier, sub_self, S_zero hα, add_sub_cancel_left] at h1
      have h2 : S α ℓ (X - k) 0 < S α ℓ (X - k) Δ :=
        (S_strictMonoOn hα hα1 hℓ hy0) ⟨le_rfl, (Δstar_pos hα hℓ hy0).le⟩ ⟨hΔ0.le, hΔle⟩ hΔ0
      rw [S_zero hα] at h2
      linarith
    · intro hX
      exact (prop_score_c hα hα1 hℓ hk hσbar hX).1.isMax

/-- **Lemma prop:score (d), uncapped claims.** "If `σ̄ = ∞`, the optimal growth rate `g*(X)` is
continuous and nondecreasing in `X`, and strictly increasing for `X > k`." Here `g*` is
`gstar`, shown to be the unique maximizer for every `X ≥ 0` (indeed every real `X`). -/
theorem prop_score_d_uncapped (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hk : 0 ≤ k) :
    (∀ X, IsUniqueMax m0 G k α ℓ ⊤ X (gstar G k α ℓ X, mstar m0 G k α ℓ (gstar G k α ℓ X))) ∧
    Continuous (gstar G k α ℓ) ∧ Monotone (gstar G k α ℓ) ∧
    StrictMonoOn (gstar G k α ℓ) (Ioi k) := by
  have hq : 0 ≤ α / (1 - α) := (div_pos hα (by linarith)).le
  refine ⟨fun X => ?_, ?_, ?_, ?_⟩
  · rcases le_or_lt X k with hX | hX
    · rw [gstar_of_le hα hα1 hX]
      exact (prop_score_c hα hα1 hℓ hk zero_lt_top hX).1
    · exact isUniqueMax_gstar hα hα1 hℓ hk zero_lt_top hX le_top
  · unfold gstar Δplus Δstar
    refine continuous_const.add (continuous_const.mul ?_)
    refine Continuous.rpow_const ?_ fun x => Or.inr hq
    exact continuous_const.mul ((continuous_id.sub continuous_const).max continuous_const)
  · intro X X' hXX'
    unfold gstar Δplus Δstar
    have h1 : α * max (X - k) 0 ≤ α * max (X' - k) 0 :=
      mul_le_mul_of_nonneg_left (max_le_max (by linarith) le_rfl) hα.le
    have h2 := Real.rpow_le_rpow (mul_nonneg hα.le (le_max_right _ _)) h1 hq
    have h3 := mul_le_mul_of_nonneg_left h2 (Real.rpow_nonneg hℓ.le (1 / (1 - α)))
    linarith
  · intro X hX X' hX' hXX'
    rw [gstar_of_lt hX, gstar_of_lt hX']
    unfold Δstar
    have hqpos : 0 < α / (1 - α) := div_pos hα (by linarith)
    have h1 : α * (X - k) < α * (X' - k) := mul_lt_mul_of_pos_left (by linarith) hα
    have h2 := Real.rpow_lt_rpow (mul_nonneg hα.le (sub_pos.2 hX).le) h1 hqpos
    have h3 := mul_lt_mul_of_pos_left h2 (Real.rpow_pos_of_pos hℓ (1 / (1 - α)))
    linarith

/-! ### Part (e): the growth surplus -/

/-- **Lemma prop:score (e).** "The growth surplus `Π := (1-α)(X-k)Δ*` (zero if `X ≤ k`)
satisfies `Π = max_{σ ≥ 0} {(X-k) ℓ σ^α - σ}`, so that `R*_X = m₀ + (X-k)G + Π`."
The maximum is stated as `IsGreatest`; the second claim holds under the cap condition
`σ* ≤ σ̄` (with `σ* = 0` when `X ≤ k`). -/
theorem prop_score_e (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hk : 0 ≤ k) (X : ℝ) :
    IsGreatest ((fun σ => (X - k) * ℓ * σ ^ α - σ) '' Ici 0) (Π α ℓ (X - k)) ∧
    (∀ σbar : WithTop ℝ, 0 < σbar → (σplus α ℓ (X - k) : WithTop ℝ) ≤ σbar →
      IsGreatest (score X '' Feasible m0 G k α ℓ σbar) (m0 + (X - k) * G + Π α ℓ (X - k))) := by
  constructor
  · rcases le_or_lt X k with hX | hX
    · have hy0 : X - k ≤ 0 := sub_nonpos.2 hX
      rw [Π_of_nonpos hα hα1 hy0]
      refine ⟨⟨0, left_mem_Ici, ?_⟩, ?_⟩
      · show (X - k) * ℓ * (0 : ℝ) ^ α - 0 = 0
        rw [Real.zero_rpow hα.ne']; ring
      · rintro _ ⟨σ, hσ, rfl⟩
        show (X - k) * ℓ * σ ^ α - σ ≤ 0
        have hσ0 : (0 : ℝ) ≤ σ := hσ
        have h1 : 0 ≤ ℓ * σ ^ α := mul_nonneg hℓ.le (Real.rpow_nonneg hσ0 _)
        nlinarith
    · have hy0 : 0 < X - k := sub_pos.2 hX
      rw [Π_of_pos hy0.le]
      refine ⟨⟨σstar α ℓ (X - k), σstar_nonneg hα hℓ hy0.le, ?_⟩, ?_⟩
      · show (X - k) * ℓ * σstar α ℓ (X - k) ^ α - σstar α ℓ (X - k) = _
        have h1 : ℓ * σstar α ℓ (X - k) ^ α = Δstar α ℓ (X - k) := by
          have := growth_σstar (G := G) hα hα1 hℓ hy0
          unfold growth at this; linarith
        rw [mul_assoc, h1, σstar_eq hα hα1 hℓ hy0]; ring
      · rintro _ ⟨σ, hσ, rfl⟩
        show (X - k) * ℓ * σ ^ α - σ ≤ _
        have hσ0 : (0 : ℝ) ≤ σ := hσ
        have hΔ : 0 ≤ ℓ * σ ^ α := mul_nonneg hℓ.le (Real.rpow_nonneg hσ0 _)
        have h1 : κ α ℓ * (ℓ * σ ^ α) ^ β α = σ := by
          have := spendOf_growth (G := G) hα hℓ hσ0
          unfold spendOf growth at this
          rwa [add_sub_cancel_left] at this
        have h2 := S_le_S_Δstar hα hα1 hℓ hy0 hΔ
        rw [S_Δstar hα hα1 hℓ hy0] at h2
        unfold S at h2
        rw [h1] at h2
        linarith
  · intro σbar hσbar hcap
    rcases le_or_lt X k with hX | hX
    · have h := (prop_score_c (m0 := m0) hα hα1 hℓ hk hσbar hX)
      rw [Π_of_nonpos hα hα1 (sub_nonpos.2 hX), add_zero, ← h.2.2.2.2]
      exact h.1.isGreatest
    · rw [σplus_of_pos (sub_pos.2 hX).le] at hcap
      have h := prop_score_b (m0 := m0) hα hα1 hℓ hk hσbar hX hcap
      rw [Π_of_pos (sub_pos.2 hX).le, ← h.2.2.2.2.2.2.2.2.2.2.1]
      exact h.1.isGreatest

/-- The maximal score with `σ̄ = ∞`, for every `X`: `R*_X = m₀ + (X-k)G + C_α(ℓ (X-k)_+)^{1/(1-α)}`. -/
theorem Rstar_isGreatest (hα : 0 < α) (hα1 : α < 1) (hℓ : 0 < ℓ) (hk : 0 ≤ k) (X : ℝ) :
    IsGreatest (score X '' Feasible m0 G k α ℓ ⊤)
      (m0 + (X - k) * G + Cα α * (ℓ * max (X - k) 0) ^ (1 / (1 - α))) := by
  rw [← Π_eq_Cα hα hα1 hℓ]
  exact (prop_score_e hα hα1 hℓ hk X).2 ⊤ zero_lt_top le_top

end RuleOfX
