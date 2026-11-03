import RuleOfX.Imports

/-!
# Definitions for the static core of the model

This file fixes the objects of Section "A Model of the Growth-Profitability Frontier":
Assumptions ass:market, ass:growth, ass:costs, ass:capital, Definition def:frontier and the
constants of eq:constants.

Conventions.
* `α` is the spend elasticity, `α ∈ (0,1)`; `β = 1/α`.
* `ℓ = λ h(s) > 0` is the effective growth opportunity; the frontier and score results are
  stated for a fixed `ℓ` (the paper says "fix `s`"), and the saturation and envelope results
  substitute `ℓ = lam * hdr sbar s`. `λ` is a reserved word in Lean, so demand pull is `lam`.
* The financing cap `σ̄ ∈ (0, ∞]` is a `WithTop ℝ`; `⊤` is `σ̄ = ∞`.
* `h(s) = 1 - s/s̄` is `hdr sbar s` (the name `h` is kept for hypotheses).
* Real powers `x ^ y` are `Real.rpow`.  All bases that occur in the statements are
  nonnegative on the stated domains.
-/

noncomputable section
open Real Set Filter Topology

set_option autoImplicit false

namespace RuleOfX

/-! ### The constants of eq:constants -/

/-- `β := 1/α`. -/
def β (α : ℝ) : ℝ := 1 / α

/-- `κ := ℓ^{-β}`. -/
def κ (α ℓ : ℝ) : ℝ := ℓ ^ (-(β α))

/-- `C_α := (1-α) α^{α/(1-α)}`. -/
def Cα (α : ℝ) : ℝ := (1 - α) * α ^ (α / (1 - α))

/-- Headroom `h(s) = 1 - s/s̄` of eq:growth. -/
def hdr (sbar s : ℝ) : ℝ := 1 - s / sbar

/-! ### Growth technology, feasible set, dominance, frontier, score (def:frontier) -/

/-- Growth technology eq:growth with `ℓ = λ h(s)`: `g = G + ℓ σ^α`. -/
def growth (G ℓ α σ : ℝ) : ℝ := G + ℓ * σ ^ α

/-- Admissible spend levels `σ ∈ [0, σ̄]`, with `σ̄ = ⊤` meaning no cap. -/
def Spend (σbar : WithTop ℝ) : Set ℝ := {σ | 0 ≤ σ ∧ (σ : WithTop ℝ) ≤ σbar}

/-- The feasible set `𝓕` of def:frontier: pairs `(g, m)` such that for some `σ ∈ [0, σ̄]`,
`g = G + ℓ σ^α` and `m ≤ m₀ - σ - k g`. -/
def Feasible (m0 G k α ℓ : ℝ) (σbar : WithTop ℝ) : Set (ℝ × ℝ) :=
  {p | ∃ σ ∈ Spend σbar, p.1 = growth G ℓ α σ ∧ p.2 ≤ m0 - σ - k * p.1}

/-- `q = (g', m')` dominates `p = (g, m)`: `g' ≥ g`, `m' ≥ m`, at least one strict. -/
def Dominates (q p : ℝ × ℝ) : Prop := p.1 ≤ q.1 ∧ p.2 ≤ q.2 ∧ (p.1 < q.1 ∨ p.2 < q.2)

/-- The efficient frontier: the undominated points of the feasible set. -/
def Frontier (m0 G k α ℓ : ℝ) (σbar : WithTop ℝ) : Set (ℝ × ℝ) :=
  {p | p ∈ Feasible m0 G k α ℓ σbar ∧ ¬ ∃ q ∈ Feasible m0 G k α ℓ σbar, Dominates q p}

/-- The Rule-of-`X` score `R_X(g, m) = X g + m`. -/
def score (X : ℝ) (p : ℝ × ℝ) : ℝ := X * p.1 + p.2

/-- `ḡ := G + ℓ σ̄^α`, with `ḡ = ⊤` when `σ̄ = ⊤`. -/
def gbar (G ℓ α : ℝ) (σbar : WithTop ℝ) : WithTop ℝ := WithTop.map (growth G ℓ α) σbar

/-- The growth interval `I := [G, ḡ] ∩ ℝ`. -/
def I (G ℓ α : ℝ) (σbar : WithTop ℝ) : Set ℝ := {g | G ≤ g ∧ (g : WithTop ℝ) ≤ gbar G ℓ α σbar}

/-- The spend that produces growth `g`: `σ(g) = κ (g - G)^β`. -/
def spendOf (G α ℓ g : ℝ) : ℝ := κ α ℓ * (g - G) ^ β α

/-- The frontier function eq:frontier: `m*(g) = m₀ - k g - κ (g - G)^β`. -/
def mstar (m0 G k α ℓ g : ℝ) : ℝ := m0 - k * g - spendOf G α ℓ g

theorem mstar_def (m0 G k α ℓ g : ℝ) :
    mstar m0 G k α ℓ g = m0 - k * g - κ α ℓ * (g - G) ^ β α := rfl

/-! ### Optimum (closed forms of prop:score) -/

/-- Excess growth at the optimum, eq:Dstar, with `y = X - k`:
`Δ* = ℓ^{1/(1-α)} (α y)^{α/(1-α)}`. -/
def Δstar (α ℓ y : ℝ) : ℝ := ℓ ^ (1 / (1 - α)) * (α * y) ^ (α / (1 - α))

/-- Spend at the optimum, eq:sigstar: `σ* = (α ℓ y)^{1/(1-α)}`. -/
def σstar (α ℓ y : ℝ) : ℝ := (α * ℓ * y) ^ (1 / (1 - α))

/-- `Δ*(ℓ, X)` with `(X-k)` replaced by `(X-k)_+` (the convention stated after prop:score). -/
def Δplus (α ℓ y : ℝ) : ℝ := Δstar α ℓ (max y 0)

/-- `σ*(ℓ, X)` with `(X-k)` replaced by `(X-k)_+`. -/
def σplus (α ℓ y : ℝ) : ℝ := σstar α ℓ (max y 0)

/-- The optimal growth rate `g*(X) = G + Δ*` (equal to `G` when `X ≤ k`). -/
def gstar (G k α ℓ X : ℝ) : ℝ := G + Δplus α ℓ (X - k)

/-- Growth surplus `Π = (1-α)(X-k)Δ*`, zero if `X ≤ k`. -/
def Π (α ℓ y : ℝ) : ℝ := (1 - α) * y * Δplus α ℓ y

/-- Score along the frontier as a function of excess growth: `𝓢(Δ) = y Δ - κ Δ^β`. -/
def S (α ℓ y Δ : ℝ) : ℝ := y * Δ - κ α ℓ * Δ ^ β α

/-- Saturated score eq:Rinf: `R_∞ = m₀ + (X - k) G`. -/
def Rinf (m0 G k X : ℝ) : ℝ := m0 + (X - k) * G

/-- The maximal score with `σ̄ = ∞` as a function of all parameters, with `ℓ = λ h(s)` and
`(X-k)_+`: `R*_X = m₀ + (X-k) G + C_α [λ h(s) (X-k)_+]^{1/(1-α)}`. -/
def Rst (α sbar m0 G k X lam s : ℝ) : ℝ :=
  m0 + (X - k) * G + Cα α * (lam * hdr sbar s * max (X - k) 0) ^ (1 / (1 - α))

/-- The demand-pull threshold eq:Lambda. -/
def Λ (α m0 G k X Rbar : ℝ) : ℝ :=
  (1 / (X - k)) * ((Rbar - Rinf m0 G k X) / Cα α) ^ (1 - α)

/-! ### Elementary facts about the constants -/

section constants
variable {α ℓ : ℝ}

theorem β_pos (hα : 0 < α) : 0 < β α := by
  unfold β; positivity

theorem one_lt_β (hα : 0 < α) (hα1 : α < 1) : 1 < β α := by
  unfold β
  rw [lt_div_iff₀ hα, one_mul]
  exact hα1

theorem α_mul_β (hα : 0 < α) : α * β α = 1 := by
  unfold β; rw [mul_one_div, div_self hα.ne']

theorem κ_pos (hℓ : 0 < ℓ) : 0 < κ α ℓ := Real.rpow_pos_of_pos hℓ _

theorem κ_mul_rpow_β (hℓ : 0 < ℓ) : κ α ℓ * ℓ ^ β α = 1 := by
  unfold κ
  rw [Real.rpow_neg hℓ.le]
  exact inv_mul_cancel₀ (Real.rpow_pos_of_pos hℓ _).ne'

theorem κ_rpow_α (hα : 0 < α) (hℓ : 0 < ℓ) : κ α ℓ ^ α = ℓ⁻¹ := by
  unfold κ
  rw [← Real.rpow_mul hℓ.le, neg_mul, mul_comm (β α) α, α_mul_β hα, Real.rpow_neg_one]

theorem Cα_pos (hα : 0 < α) (hα1 : α < 1) : 0 < Cα α := by
  unfold Cα
  exact mul_pos (by linarith) (Real.rpow_pos_of_pos hα _)

theorem Cα_lt_one (hα : 0 < α) (hα1 : α < 1) : Cα α < 1 := by
  unfold Cα
  have h1 : α ^ (α / (1 - α)) < 1 :=
    Real.rpow_lt_one hα.le hα1 (div_pos hα (by linarith))
  have h2 : 0 < α ^ (α / (1 - α)) := Real.rpow_pos_of_pos hα _
  nlinarith

/-- `1/(1-α) - 1 = α/(1-α)`. -/
theorem q_sub_one (hα1 : α < 1) : 1 / (1 - α) - 1 = α / (1 - α) := by
  have : (1 - α) ≠ 0 := by linarith
  rw [div_sub_one this]; congr 1; ring

theorem q_pos (hα1 : α < 1) : 0 < 1 / (1 - α) := by
  have : 0 < 1 - α := by linarith
  positivity

theorem one_lt_q (hα : 0 < α) (hα1 : α < 1) : 1 < 1 / (1 - α) := by
  have : 0 < 1 - α := by linarith
  rw [lt_div_iff₀ this, one_mul]; linarith

/-- `C_α · (1/(1-α)) = α^{α/(1-α)}`. -/
theorem Cα_mul_q (hα1 : α < 1) : Cα α * (1 / (1 - α)) = α ^ (α / (1 - α)) := by
  unfold Cα
  have : (1 - α) ≠ 0 := by linarith
  rw [mul_comm, ← mul_assoc, one_div, inv_mul_cancel₀ this, one_mul]

/-- The constant `β = 1/α` is `2` exactly when `α = 1/2`. -/
theorem β_eq_two (hα : α = 1 / 2) : β α = 2 := by
  subst hα; unfold β; norm_num

theorem two_lt_β (hα : 0 < α) (hα12 : α < 1 / 2) : 2 < β α := by
  unfold β
  rw [lt_div_iff₀ hα]; linarith

theorem β_lt_two (hα : 1 / 2 < α) (hα1 : α < 1) : β α < 2 := by
  unfold β
  have : 0 < α := by linarith
  rw [div_lt_iff₀ this]; linarith

end constants

/-! ### The growth map and its inverse -/

section growth
variable {G α ℓ : ℝ}

theorem growth_nonneg_sub (hℓ : 0 < ℓ) {σ : ℝ} (hσ : 0 ≤ σ) : G ≤ growth G ℓ α σ := by
  unfold growth
  have : 0 ≤ ℓ * σ ^ α := mul_nonneg hℓ.le (Real.rpow_nonneg hσ _)
  linarith

theorem growth_strictMonoOn (hα : 0 < α) (hℓ : 0 < ℓ) :
    StrictMonoOn (growth G ℓ α) (Ici 0) := by
  intro x hx y _ hxy
  unfold growth
  have := Real.rpow_lt_rpow hx hxy hα
  have := mul_lt_mul_of_pos_left this hℓ
  linarith

theorem growth_monotoneOn (hα : 0 < α) (hℓ : 0 < ℓ) :
    MonotoneOn (growth G ℓ α) (Ici 0) :=
  (growth_strictMonoOn hα hℓ).monotoneOn

/-- `σ(G + ℓ σ^α) = σ` for `σ ≥ 0`. -/
theorem spendOf_growth (hα : 0 < α) (hℓ : 0 < ℓ) {σ : ℝ} (hσ : 0 ≤ σ) :
    spendOf G α ℓ (growth G ℓ α σ) = σ := by
  unfold spendOf growth
  have h1 : G + ℓ * σ ^ α - G = ℓ * σ ^ α := by ring
  rw [h1, Real.mul_rpow hℓ.le (Real.rpow_nonneg hσ _), ← Real.rpow_mul hσ, α_mul_β hα,
    Real.rpow_one, ← mul_assoc, κ_mul_rpow_β hℓ, one_mul]

/-- `G + ℓ (κ Δ^β)^α = G + Δ` for `Δ ≥ 0`. -/
theorem growth_κ_rpow (hα : 0 < α) (hℓ : 0 < ℓ) {Δ : ℝ} (hΔ : 0 ≤ Δ) :
    growth G ℓ α (κ α ℓ * Δ ^ β α) = G + Δ := by
  unfold growth
  have hκ : 0 ≤ κ α ℓ := (κ_pos hℓ).le
  rw [Real.mul_rpow hκ (Real.rpow_nonneg hΔ _), ← Real.rpow_mul hΔ, mul_comm (β α) α,
    α_mul_β hα, Real.rpow_one, κ_rpow_α hα hℓ, ← mul_assoc, mul_inv_cancel₀ hℓ.ne', one_mul]

/-- `G + ℓ σ(g)^α = g` for `g ≥ G`. -/
theorem growth_spendOf (hα : 0 < α) (hℓ : 0 < ℓ) {g : ℝ} (hg : G ≤ g) :
    growth G ℓ α (spendOf G α ℓ g) = g := by
  unfold spendOf
  rw [growth_κ_rpow hα hℓ (sub_nonneg.2 hg)]; ring

theorem spendOf_nonneg (hℓ : 0 < ℓ) {g : ℝ} (hg : G ≤ g) : 0 ≤ spendOf G α ℓ g :=
  mul_nonneg (κ_pos hℓ).le (Real.rpow_nonneg (sub_nonneg.2 hg) _)

theorem spendOf_self (hα : 0 < α) : spendOf G α ℓ G = 0 := by
  unfold spendOf
  rw [sub_self, Real.zero_rpow (β_pos hα).ne', mul_zero]

theorem spendOf_strictMonoOn (hα : 0 < α) (hℓ : 0 < ℓ) :
    StrictMonoOn (spendOf G α ℓ) (Ici G) := by
  intro x hx y _ hxy
  unfold spendOf
  have hx' : (0 : ℝ) ≤ x - G := sub_nonneg.2 hx
  have := Real.rpow_lt_rpow hx' (by linarith : x - G < y - G) (β_pos hα)
  exact mul_lt_mul_of_pos_left this (κ_pos hℓ)

theorem spendOf_monotoneOn (hα : 0 < α) (hℓ : 0 < ℓ) :
    MonotoneOn (spendOf G α ℓ) (Ici G) :=
  (spendOf_strictMonoOn hα hℓ).monotoneOn

theorem mstar_G (hα : 0 < α) (m0 G k ℓ : ℝ) : mstar m0 G k α ℓ G = m0 - k * G := by
  unfold mstar; rw [spendOf_self hα, sub_zero]

end growth

/-! ### The interval `I` and the spend set -/

section interval
variable {G α ℓ : ℝ}

theorem zero_lt_top : (0 : WithTop ℝ) < ⊤ := WithTop.coe_lt_top 0

theorem I_top : I G ℓ α ⊤ = Ici G := by
  ext g; simp [I, gbar]

theorem I_coe (b : ℝ) : I G ℓ α (b : WithTop ℝ) = Icc G (growth G ℓ α b) := by
  ext g; simp [I, gbar, WithTop.map_coe]

theorem Spend_top : Spend ⊤ = Ici 0 := by
  ext σ; simp [Spend]

theorem Spend_coe (b : ℝ) : Spend (b : WithTop ℝ) = Icc 0 b := by
  ext σ; simp [Spend]

theorem convex_I (σbar : WithTop ℝ) : Convex ℝ (I G ℓ α σbar) := by
  induction σbar using WithTop.recTopCoe with
  | top => rw [I_top]; exact convex_Ici G
  | coe b => rw [I_coe]; exact convex_Icc _ _

theorem I_subset_Ici (σbar : WithTop ℝ) : I G ℓ α σbar ⊆ Ici G := fun _ hg => hg.1

theorem G_mem_I (hα : 0 < α) (hℓ : 0 < ℓ) {σbar : WithTop ℝ} (hσbar : 0 < σbar) :
    G ∈ I G ℓ α σbar := by
  induction σbar using WithTop.recTopCoe with
  | top => rw [I_top]; exact left_mem_Ici
  | coe b =>
    rw [I_coe]
    have hb : (0 : ℝ) < b := by exact_mod_cast hσbar
    exact ⟨le_rfl, growth_nonneg_sub hℓ hb.le⟩

/-- `g ∈ I` iff some admissible spend produces it. -/
theorem mem_I_iff (hα : 0 < α) (hℓ : 0 < ℓ) {σbar : WithTop ℝ} (hσbar : 0 < σbar) (g : ℝ) :
    g ∈ I G ℓ α σbar ↔ ∃ σ ∈ Spend σbar, growth G ℓ α σ = g := by
  induction σbar using WithTop.recTopCoe with
  | top =>
    rw [I_top, Spend_top]
    constructor
    · intro hg
      exact ⟨spendOf G α ℓ g, spendOf_nonneg hℓ hg, growth_spendOf hα hℓ hg⟩
    · rintro ⟨σ, hσ, rfl⟩
      exact growth_nonneg_sub hℓ hσ
  | coe b =>
    have hb : (0 : ℝ) < b := by exact_mod_cast hσbar
    rw [I_coe, Spend_coe]
    constructor
    · rintro ⟨hg, hgb⟩
      refine ⟨spendOf G α ℓ g, ⟨spendOf_nonneg hℓ hg, ?_⟩, growth_spendOf hα hℓ hg⟩
      have := spendOf_monotoneOn hα hℓ hg (growth_nonneg_sub hℓ hb.le) hgb
      rwa [spendOf_growth hα hℓ hb.le] at this
    · rintro ⟨σ, ⟨hσ0, hσb⟩, rfl⟩
      exact ⟨growth_nonneg_sub hℓ hσ0, growth_monotoneOn hα hℓ hσ0 hb.le hσb⟩

end interval

end RuleOfX
