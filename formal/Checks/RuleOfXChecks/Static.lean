import RuleOfX

/-!
# Instances of the static main theorems at paper-like parameter values

`α = 0.3`, `ℓ = 0.6`, `G = 0.10`, `k = 0.10`, `m₀ = 0.45`, `X = 1` or `2`, `s̄ = 0.5`,
`λ = 1.2`, `s = 0.1`. Each `example` instantiates a main theorem, so every hypothesis is
discharged by a proof; this documents that the hypotheses are satisfiable (the theorems are not
vacuous). These instances were written by the independent audit of the formalization and
adapted to the final statements.
-/

noncomputable section
open Real Set Filter Topology RuleOfX

namespace RuleOfXChecks

theorem hα : (0:ℝ) < 0.3 := by norm_num
theorem hα1 : (0.3:ℝ) < 1 := by norm_num
theorem hℓ : (0:ℝ) < 0.6 := by norm_num
theorem hk : (0:ℝ) ≤ 0.1 := by norm_num
theorem hlam : (0:ℝ) < 1.2 := by norm_num
theorem hsbar : (0:ℝ) < 0.5 := by norm_num
theorem hs : (0.1:ℝ) < 0.5 := by norm_num

/-- the uncapped case -/
example := prop_frontier_a (m0 := 0.45) (G := 0.1) hα hα1 hℓ hk (σbar := ⊤) zero_lt_top
/-- a finite cap σ̄ = 1 -/
example := prop_frontier_a (m0 := 0.45) (G := 0.1) hα hα1 hℓ hk (σbar := ((1:ℝ) : WithTop ℝ))
  (by exact_mod_cast (show (0:ℝ) < 1 by norm_num))
example := prop_frontier_b (m0 := 0.45) (G := 0.1) (k := 0.1) (ℓ := 0.6) hα hα1
example := prop_frontier_c (m0 := 0.45) (G := 0.1) hα hα1 hℓ hk ⊤
example := prop_frontier_d (m0 := 0.45) (G := 0.1) (k := 0.1) hα hα1 hℓ
/-- negative capital intensity in (d) -/
example := prop_frontier_d (m0 := 0.45) (G := 0.1) (k := -0.3) hα hα1 hℓ

/-- The frontier is a genuinely nonempty set derived from dominance: the corner is on it,
a point strictly below the corner is not. -/
example : ((0.1:ℝ), (0.45:ℝ) - 0.1 * 0.1) ∈ Frontier 0.45 0.1 0.1 0.3 0.6 ⊤ ∧
    ((0.1:ℝ), (0.0:ℝ)) ∉ Frontier 0.45 0.1 0.1 0.3 0.6 ⊤ := by
  rw [frontier_eq hα hℓ hk zero_lt_top]
  refine ⟨⟨by rw [I_top]; exact (le_refl (0.1:ℝ)), ?_⟩, ?_⟩
  · simp only; rw [mstar_G hα]
  · rintro ⟨_, h⟩
    simp only at h
    rw [mstar_G hα] at h
    norm_num at h

example := prop_score_a (m0 := 0.45) (G := 0.1) hα hα1 hℓ hk (σbar := ⊤) zero_lt_top 1

/-- prop_score_b at X = 1, uncapped, and with a finite cap σ̄ = 1 (σ* ≈ 0.074 ≤ 1). -/
example := prop_score_b (m0 := 0.45) (G := 0.1) hα hα1 hℓ hk (σbar := ⊤) zero_lt_top
  (X := 1) (by norm_num) le_top

theorem σstar_le_one : σstar 0.3 0.6 ((1:ℝ) - 0.1) ≤ 1 := by
  unfold σstar
  exact Real.rpow_le_one (by norm_num) (by norm_num) (by norm_num)

example := prop_score_b (m0 := 0.45) (G := 0.1) hα hα1 hℓ hk
  (σbar := ((1:ℝ) : WithTop ℝ)) (by exact_mod_cast (show (0:ℝ) < 1 by norm_num))
  (X := 1) (by norm_num) (by exact_mod_cast σstar_le_one)

/-- binding cap: σ̄ = σ* exactly; the conclusion then also gives g* = ḡ. -/
example := prop_score_b (m0 := 0.45) (G := 0.1) hα hα1 hℓ hk
  (σbar := ((σstar 0.3 0.6 ((1:ℝ) - 0.1) : ℝ) : WithTop ℝ))
  (by exact_mod_cast (Real.rpow_pos_of_pos (by norm_num) _ : (0:ℝ) < σstar 0.3 0.6 ((1:ℝ) - 0.1)))
  (X := 1) (by norm_num) le_rfl

/-- X ≤ k (X = 0.05 < k = 0.1). -/
example := prop_score_c (m0 := 0.45) (G := 0.1) hα hα1 hℓ hk (σbar := ⊤) zero_lt_top
  (X := 0.05) (by norm_num)

example := prop_score_d (m0 := 0.45) (G := 0.1) hα hα1 hℓ hk (σbar := ⊤) zero_lt_top
example := prop_score_d_uncapped (m0 := 0.45) (G := 0.1) hα hα1 hℓ hk
example := prop_score_e (m0 := 0.45) (G := 0.1) hα hα1 hℓ hk 2

/-- the duality part has a hypothesis `G < g < ḡ`; instantiate it at g = 0.3, both forms -/
example := (prop_score_d (m0 := 0.45) (G := 0.1) hα hα1 hℓ hk (σbar := ⊤) zero_lt_top).1 0.3
  (by norm_num) (WithTop.coe_lt_top _)
example : ∀ X, IsMax 0.45 0.1 0.1 0.3 0.6 ⊤ X (0.3, mstar 0.45 0.1 0.1 0.3 0.6 0.3) ↔
    X = Xof 0.1 0.1 0.3 0.6 0.3 :=
  ((prop_score_d (m0 := 0.45) (G := 0.1) hα hα1 hℓ hk (σbar := ⊤) zero_lt_top).1 0.3
    (by norm_num) (WithTop.coe_lt_top _)).2.2.1

/-- Saturation with the figure's values m0 = 0.5, G = 0.2, λ = 1.2, α = 0.3, k = 0.3, s̄ = 0.5. -/
example := prop_saturation_a (m0 := 0.5) (G := 0.2) (k := 0.3) hα hα1 (by norm_num) hlam hsbar 1
example := prop_saturation_b (m0 := 0.5) (G := 0.2) (k := 0.3) hα hα1 hlam hsbar 1
example := prop_saturation_c (m0 := 0.5) (G := 0.2) (k := 0.3) hα hα1 hlam hsbar 1
/-- Rule-of-1000 example: m0 = 0.6, G = 0.2, k = 0, X = 1, R̄ = 10 (R_∞ = 0.8). -/
example := prop_saturation_d (m0 := 0.6) (G := 0.2) (k := 0) (X := 1) (Rbar := 10) hα hα1 le_rfl
  hlam hsbar (by norm_num) (by unfold Rinf; norm_num)

example := prop_envelope (m0 := 0.45) (G := 0.1) (k := 0.1) (X := 2) hα hα1 hlam hsbar hs
  0.9 0.45 0.05 0.03 0.02
/-- the point of interest is in the domain of the C¹ claim -/
example : ((0.45:ℝ), (0.1:ℝ), (0.1:ℝ), (2:ℝ), (1.2:ℝ), (0.1:ℝ)) ∈ Dom 0.5 := by
  unfold Dom; norm_num

example := cor_capital (G := 0.1) (k := 0.1) (X := 1) hα hα1 hlam hsbar hs 0.9 0.45
  (da := 0.02) (dk := 0.1) (by norm_num) (by norm_num)
example := cor_priorities_i (G := 0.1) (k := 0.1) (X := 1) hα hα1 hlam hsbar hs 0.9 0.45 0.02
example := cor_priorities_ii (m0 := 0.45) (G := 0.1) (k := 0.1) (X := 1) hα hα1 hlam hsbar hs
  (x := 0.1) (by norm_num)
example := cor_priorities_iii (m0 := 0.45) (G := 0.1) (k := 0.1) (X := 1) hα hα1 hlam hsbar hs
example := cor_priorities_v (G := 0.1) (k := 0.1) (X := 1) hα hα1 hlam hsbar hs 0.9 0.45
  (da := 0.02) (dk := 0.1) (by norm_num) (by norm_num)

/-- Rst really is the maximal score at the paper's point (link used by envelope/capital). -/
example := Rst_isGreatest (m0 := 0.45) (G := 0.1) (X := 2) (k := 0.1) hα hα1 hlam hsbar hs
/-- negative capital intensity, with X > k and with X ≤ k -/
example := Rst_isGreatest (m0 := 0.45) (G := 0.1) (X := 0.3) (k := -0.5) hα hα1 hlam hsbar hs
example := Rst_isGreatest (m0 := 0.45) (G := 0.1) (X := -1) (k := -0.5) hα hα1 hlam hsbar hs
/-- the IsGreatest conjuncts instantiate -/
example := (cor_capital (G := 0.1) (k := 0.1) (X := 1) hα hα1 hlam hsbar hs 0.9 0.45
  (da := 0.02) (dk := 0.1) (by norm_num) (by norm_num)).2.1
example := (prop_envelope (m0 := 0.45) (G := 0.1) (k := -0.2) (X := 2) hα hα1 hlam hsbar hs
  0.9 0.45 0.05 0.03 0.02).1
example := (prop_saturation_c (m0 := 0.5) (G := 0.2) (k := 0.3) hα hα1 hlam hsbar 1).1 0.1 hs

/-- discrete-time budget: m0 = 0.6, G = 0.2, k = 0, X = 1, s0 = 0.01, s̄ = 0.5, one period with
excess growth 1.0 (period-0 score = 2.0 > R_∞ = 0.8). -/
def gD (t : ℕ) : ℝ := if t = 0 then 1.2 else 0.2
def sD (t : ℕ) : ℝ := if t = 0 then 0.01 else 0.01 * (1 + 1.2) / (1 + 0.2)
def mD (t : ℕ) : ℝ := 0.6 - 0 * gD t

theorem sD_rec : ∀ t, sD (t + 1) = sD t * (1 + gD t) / (1 + 0.2) := by
  intro t
  rcases Nat.eq_zero_or_pos t with rfl | ht
  · simp [sD, gD]
  · have h1 : t ≠ 0 := Nat.pos_iff_ne_zero.1 ht
    simp only [sD, gD, h1, ite_false, Nat.add_one_ne_zero]; norm_num

theorem gD_ge : ∀ t, (0.2:ℝ) ≤ gD t := by
  intro t; unfold gD; split_ifs <;> norm_num

theorem sD_cap : ∀ t, sD t ≤ 0.5 := by
  intro t; unfold sD; split_ifs <;> norm_num

example := prop_budget_b (m0 := 0.6) (G := 0.2) (k := 0) (X := 1) (sbar := 0.5) (by norm_num)
  (by norm_num) sD gD mD (by unfold sD; norm_num) sD_rec gD_ge (fun t => le_refl _) sD_cap 5

example := cor_transient_a (m0 := 0.6) (G := 0.2) (k := 0) (X := 1) (sbar := 0.5) (Rbar := 1.4)
  (by norm_num) (by norm_num) (by unfold Rinf; norm_num) sD gD mD (by unfold sD; norm_num) sD_rec gD_ge
  (fun t => le_refl _) sD_cap 5

/-- the path is nontrivial: the period-0 score exceeds R_∞ -/
example : Rinf 0.6 0.2 0 1 < 1 * gD 0 + mD 0 := by
  unfold Rinf mD gD; norm_num

end RuleOfXChecks
