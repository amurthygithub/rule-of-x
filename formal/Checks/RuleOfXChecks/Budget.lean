import RuleOfXChecks.Logistic

/-!
# Continuous-time budget on a nontrivial path: constant spend, logistic share

`σ ≡ 1`, `λ = 1.2`, `s̄ = 0.5`, `s₀ = 0.01`, `α = 0.3`, `X = 1`, `k = 0`, `m₀ = 0.6`, `G = 0.2`,
horizon `T = 1`. Two instances: (1) with the explicit logistic path `Fl` (absolutely continuous
because Lipschitz, share equation everywhere); (2) with the paper's induced path
`induced α λ s̄ s₀ σ`, which needs no construction at all. (Audit instances.)
-/

noncomputable section
open Real Set Filter Topology MeasureTheory RuleOfX
open scoped NNReal

namespace RuleOfXChecks

def σC : ℝ → ℝ := fun _ => 1

theorem Fl_ode (t : ℝ) : HasDerivAt Fl (Fl t * Δpath 0.3 1.2 0.5 σC Fl t) t := by
  refine (Fl_hasDerivAt t).congr_deriv ?_
  unfold Δpath Fl Fl' σC hdr
  rw [Real.one_rpow]
  have h0 := (Dn_pos t).ne'
  unfold Dn at h0 ⊢
  field_simp
  ring

theorem Fl_ac : AbsolutelyContinuousOnInterval Fl 0 1 :=
  (Fl_lipschitz.mono (by rw [uIcc_of_le (by norm_num : (0:ℝ) ≤ 1)]; exact Icc_subset_Ici_self))
    |>.absolutelyContinuousOnInterval

def mC (t : ℝ) : ℝ := 0.6 - σC t - 0 * (0.2 + Δpath 0.3 1.2 0.5 σC Fl t)

theorem mC_meas : Measurable mC := by
  have : Continuous mC := by
    unfold mC Δpath σC hdr
    have := Fl_cont
    fun_prop
  exact this.measurable

/-- (1) explicit path -/
example := prop_budget_a (m0 := 0.6) (G := 0.2) (k := 0) (X := 1) (α := 0.3) (lam := 1.2)
  (sbar := 0.5) (T := 1) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
  σC mC Fl measurable_const (fun _ => zero_le_one) (by simp [σC])
  mC_meas Fl_ac (fun t _ => Fl_range t) (hode_of_forall fun t _ => Fl_ode t) (fun t => le_refl _)

example := cor_transient_b (m0 := 0.6) (G := 0.2) (k := 0) (X := 1) (α := 0.3) (lam := 1.2)
  (sbar := 0.5) (T := 1) (Rbar := 0.9) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
  (by unfold Rinf; norm_num) (by norm_num)
  σC mC Fl measurable_const (fun _ => zero_le_one) (by simp [σC])
  mC_meas Fl_ac (fun t _ => Fl_range t) (hode_of_forall fun t _ => Fl_ode t) (fun t => le_refl _)

/-- non-triviality: at t = 0 the score 1·(0.2 + 1.2·0.98) + (0.6 - 1) = 1.576 exceeds
R̄ = 0.9 > R_∞ = 0.8. -/
example : (0.9:ℝ) ≤ Rpath 0.2 0.3 1.2 0.5 1 σC Fl mC 0 := by
  have hs : Fl 0 = 0.5 / 50 := by unfold Fl Dn; norm_num
  unfold Rpath mC Δpath σC hdr
  rw [Real.one_rpow, hs]
  norm_num

/-- (2) the paper's induced path, no construction needed -/
def mI (t : ℝ) : ℝ := 0.6 - σC t - 0 * (0.2 + Δpath 0.3 1.2 0.5 σC (induced 0.3 1.2 0.5 0.01 σC) t)

theorem mI_meas : Measurable mI := by
  have hs : Continuous (induced 0.3 1.2 0.5 0.01 σC) := by
    have hL := (logistic_lipschitz (sbar := 0.5) (s0 := 0.01) (by norm_num) (by norm_num)
      (by norm_num)).continuous
    have hS : Continuous (Spath 0.3 1.2 σC) := by
      unfold Spath σC
      simp only [Real.one_rpow]
      exact continuous_const.mul (intervalIntegral.continuous_primitive
        (fun a b => intervalIntegrable_const) 0)
    exact hL.comp hS
  have : Continuous mI := by
    unfold mI Δpath σC hdr
    fun_prop
  exact this.measurable

example := prop_budget_a_induced (m0 := 0.6) (G := 0.2) (k := 0) (X := 1) (α := 0.3)
  (lam := 1.2) (sbar := 0.5) (T := 1) (s0 := 0.01) (by norm_num) (by norm_num) (by norm_num)
  (by norm_num) (by norm_num) (by norm_num) (by norm_num)
  σC mI measurable_const (fun _ => zero_le_one) (by simp [σC]) mI_meas (fun t => le_refl _)

example := cor_transient_b_induced (m0 := 0.6) (G := 0.2) (k := 0) (X := 1) (α := 0.3)
  (lam := 1.2) (sbar := 0.5) (T := 1) (s0 := 0.01) (Rbar := 0.9) (by norm_num) (by norm_num)
  (by norm_num) (by norm_num) (by unfold Rinf; norm_num) (by norm_num) (by norm_num) (by norm_num)
  σC mI measurable_const (fun _ => zero_le_one) (by simp [σC]) mI_meas (fun t => le_refl _)

end RuleOfXChecks
