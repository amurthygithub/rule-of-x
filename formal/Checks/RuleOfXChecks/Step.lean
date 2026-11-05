import RuleOfXChecks.Logistic

/-!
# The continuous-time theorems on a spend path with a jump

`σ = 0` on `(-∞,1)`, `1` on `[1,∞)`; `T = 2`; `λ = 1.2`, `s̄ = 0.5`, `s₀ = 0.01`, `α = 0.3`;
`X = 1`, `k = 0`, `m₀ = 0.6`, `G = 0.2` (`R_∞ = 0.8`). The induced share path is constant on
`[0,1]` and logistic after: `s(t) = 0.5 / (1 + 49 e^{-1.2 max(t-1,0)})`. It is not
differentiable at `t = 1`, so an everywhere-differentiable share-path hypothesis could not be
met; the absolutely continuous / almost-everywhere hypotheses are. Two instances: with the
explicit path `sStep`, and with the paper's `induced` path (no construction). (Audit instances.)
-/

noncomputable section
open Real Set Filter Topology MeasureTheory RuleOfX
open scoped NNReal

namespace RuleOfXChecks

def σStep : ℝ → ℝ := fun t => if t < 1 then 0 else 1

/-- the induced share path, written explicitly -/
def sStep (t : ℝ) : ℝ := Fl (max (t - 1) 0)

theorem sStep_ac : AbsolutelyContinuousOnInterval sStep 0 2 :=
  Fl_lipschitz.comp_absolutelyContinuousOnInterval (g := fun t : ℝ => max (t - 1) 0)
    (fun _ _ => mem_Ici.2 (le_max_right _ _))
    (clamp_lipschitz.lipschitzOnWith.absolutelyContinuousOnInterval)

theorem sStep_cont : Continuous sStep := by
  unfold sStep
  exact Fl_cont.comp (by fun_prop)

theorem sStep_range (t : ℝ) : 0 < sStep t ∧ sStep t < 0.5 := Fl_range _

/-- the share ODE holds at every `t ≠ 1` -/
theorem sStep_ode {t : ℝ} (ht : t ≠ 1) :
    HasDerivAt sStep (sStep t * Δpath 0.3 1.2 0.5 σStep sStep t) t := by
  rcases lt_or_gt_of_ne ht with h | h
  · -- before the jump: σ = 0, s locally constant
    have hev : sStep =ᶠ[𝓝 t] fun _ => Fl 0 := by
      filter_upwards [Iio_mem_nhds h] with u hu
      unfold sStep; rw [max_eq_right (by linarith [mem_Iio.1 hu])]
    have hR : sStep t * Δpath 0.3 1.2 0.5 σStep sStep t = 0 := by
      unfold Δpath σStep; rw [if_pos h, Real.zero_rpow (by norm_num)]; ring
    rw [hR]
    exact (hasDerivAt_const t (Fl 0)).congr_of_eventuallyEq hev
  · -- after the jump: σ = 1, s logistic
    have hev : sStep =ᶠ[𝓝 t] (Fl ∘ fun u : ℝ => u - 1) := by
      filter_upwards [Ioi_mem_nhds h] with u hu
      show sStep u = Fl (u - 1)
      unfold sStep; rw [max_eq_left (by linarith [mem_Ioi.1 hu])]
    have hd : HasDerivAt (Fl ∘ fun u : ℝ => u - 1) (Fl' (t - 1) * 1) t :=
      (Fl_hasDerivAt (t - 1)).comp t ((hasDerivAt_id' t).sub_const 1)
    refine (hd.congr_of_eventuallyEq hev).congr_deriv ?_
    have hs : sStep t = Fl (t - 1) := by unfold sStep; rw [max_eq_left (by linarith)]
    unfold Δpath σStep hdr
    rw [if_neg (not_lt.2 h.le), Real.one_rpow, hs]
    unfold Fl Fl'
    have h0 := (Dn_pos (t - 1)).ne'
    unfold Dn at h0 ⊢
    field_simp
    ring

theorem sStep_hode :
    ∀ᵐ t, t ∈ Icc (0:ℝ) 2 → HasDerivAt sStep (sStep t * Δpath 0.3 1.2 0.5 σStep sStep t) t := by
  filter_upwards [(Set.countable_singleton (1:ℝ)).ae_notMem volume] with t ht _
  exact sStep_ode ht

/-- `sStep` is NOT differentiable at the jump. -/
example : ¬ DifferentiableAt ℝ sStep 1 := by
  intro hd
  have hL : HasDerivWithinAt sStep 0 (Iic 1) 1 := by
    refine (hasDerivWithinAt_const (1:ℝ) (Iic 1) (Fl 0)).congr (fun u hu => ?_) ?_
    · unfold sStep; rw [max_eq_right (by linarith [mem_Iic.1 hu])]
    · unfold sStep; norm_num
  have hR : HasDerivWithinAt sStep (Fl' 0) (Ici 1) 1 := by
    have hin : HasDerivAt (fun u : ℝ => u - 1) 1 1 := (hasDerivAt_id' (1:ℝ)).sub_const 1
    have hd' := HasDerivAt.comp (h := fun u : ℝ => u - 1) (h₂ := Fl) (1:ℝ) (Fl_hasDerivAt _) hin
    have h10 : (1:ℝ) - 1 = 0 := by norm_num
    rw [h10, mul_one] at hd'
    refine hd'.hasDerivWithinAt.congr (fun u hu => ?_) ?_
    · show sStep u = Fl (u - 1)
      unfold sStep; rw [max_eq_left (by linarith [mem_Ici.1 hu])]
    · show sStep 1 = Fl (1 - 1)
      unfold sStep; norm_num
  have h1 := (uniqueDiffWithinAt_Iic (1:ℝ)).eq_deriv _ hd.hasDerivAt.hasDerivWithinAt hL
  have h2 := (uniqueDiffWithinAt_Ici (1:ℝ)).eq_deriv _ hd.hasDerivAt.hasDerivWithinAt hR
  have : Fl' 0 ≠ 0 := by
    have hval : Fl' 0 = 29.4 * Real.exp (-(1.2 * 0)) / Dn 0 ^ 2 := by unfold Fl'; ring
    rw [hval]; have := Dn_pos 0; positivity
  exact this (h2.symm.trans h1)

theorem σStep_meas : Measurable σStep :=
  Measurable.ite measurableSet_Iio measurable_const measurable_const

theorem σStep_nonneg (t : ℝ) : 0 ≤ σStep t := by unfold σStep; split_ifs <;> norm_num

theorem σStep_int : IntervalIntegrable (fun t => σStep t ^ (0.3:ℝ)) volume 0 2 := by
  refine IntervalIntegrable.mono_fun' (intervalIntegrable_const (c := (1:ℝ)))
    ((σStep_meas.pow_const _).aestronglyMeasurable) (ae_of_all _ fun t => ?_)
  show ‖σStep t ^ (0.3:ℝ)‖ ≤ 1
  unfold σStep
  split_ifs
  · rw [Real.zero_rpow (by norm_num)]; simp
  · rw [Real.one_rpow]; simp

def mStep (t : ℝ) : ℝ := 0.6 - σStep t - 0 * (0.2 + Δpath 0.3 1.2 0.5 σStep sStep t)

theorem mStep_meas : Measurable mStep := by
  have hΔ : Measurable (Δpath 0.3 1.2 0.5 σStep sStep) := by
    unfold Δpath
    exact (measurable_const.mul (hdr_continuous.measurable.comp sStep_cont.measurable)).mul
      (σStep_meas.pow_const _)
  unfold mStep
  exact (measurable_const.sub σStep_meas).sub (measurable_const.mul (measurable_const.add hΔ))

/-! The continuous-time theorems apply to the step path. -/

example := prop_budget_a (m0 := 0.6) (G := 0.2) (k := 0) (X := 1) (α := 0.3) (lam := 1.2)
  (sbar := 0.5) (T := 2) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
  σStep mStep sStep σStep_meas σStep_nonneg σStep_int
  mStep_meas sStep_ac (fun t _ => sStep_range t) sStep_hode (fun t => le_refl _)

example := prop_budget_c_continuous (G := 0.2) (k := 0) (X := 1) (α := 0.3) (lam := 1.2)
  (sbar := 0.5) (T := 2) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
  σStep mStep sStep (fun _ => 0.6) σStep_meas σStep_nonneg
  σStep_int mStep_meas measurable_const sStep_ac (fun t _ => sStep_range t) sStep_hode
  (fun t => le_refl _)

example := cor_transient_b (m0 := 0.6) (G := 0.2) (k := 0) (X := 1) (α := 0.3) (lam := 1.2)
  (sbar := 0.5) (T := 2) (Rbar := 0.9) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
  (by unfold Rinf; norm_num) (by norm_num)
  σStep mStep sStep σStep_meas σStep_nonneg σStep_int
  mStep_meas sStep_ac (fun t _ => sStep_range t) sStep_hode (fun t => le_refl _)

/-- non-triviality: just after the jump the score exceeds R̄ = 0.9 > R_∞ = 0.8
(at t = 1: g = 0.2 + 1.2·(1 - 0.02) = 1.376, m = -0.4, score 0.976). -/
example : (0.9:ℝ) ≤ Rpath 0.2 0.3 1.2 0.5 1 σStep sStep mStep 1 := by
  have hs : sStep 1 = 0.5 / 50 := by unfold sStep Fl Dn; norm_num
  unfold Rpath mStep Δpath σStep hdr
  rw [if_neg (lt_irrefl _), Real.one_rpow, hs]
  norm_num

/-! The same with the paper's induced path: no share-path construction at all. -/

def mStepI (t : ℝ) : ℝ :=
  0.6 - σStep t - 0 * (0.2 + Δpath 0.3 1.2 0.5 σStep (induced 0.3 1.2 0.5 0.01 σStep) t)

theorem induced_step_cont : Continuous (induced 0.3 1.2 0.5 0.01 σStep) := by
  have hL := (logistic_lipschitz (sbar := 0.5) (s0 := 0.01) (by norm_num) (by norm_num)
    (by norm_num)).continuous
  have hS : Continuous (Spath 0.3 1.2 σStep) := by
    unfold Spath
    refine continuous_const.mul (intervalIntegral.continuous_primitive (fun a b => ?_) 0)
    refine IntervalIntegrable.mono_fun' (intervalIntegrable_const (c := (1:ℝ)))
      ((σStep_meas.pow_const _).aestronglyMeasurable) (ae_of_all _ fun t => ?_)
    show ‖σStep t ^ (0.3:ℝ)‖ ≤ 1
    unfold σStep
    split_ifs
    · rw [Real.zero_rpow (by norm_num)]; simp
    · rw [Real.one_rpow]; simp
  exact hL.comp hS

theorem mStepI_meas : Measurable mStepI := by
  have hΔ : Measurable (Δpath 0.3 1.2 0.5 σStep (induced 0.3 1.2 0.5 0.01 σStep)) := by
    unfold Δpath
    exact (measurable_const.mul (hdr_continuous.measurable.comp induced_step_cont.measurable)).mul
      (σStep_meas.pow_const _)
  unfold mStepI
  exact (measurable_const.sub σStep_meas).sub (measurable_const.mul (measurable_const.add hΔ))

example := prop_budget_a_induced (m0 := 0.6) (G := 0.2) (k := 0) (X := 1) (α := 0.3)
  (lam := 1.2) (sbar := 0.5) (T := 2) (s0 := 0.01) (by norm_num) (by norm_num) (by norm_num)
  (by norm_num) (by norm_num) (by norm_num) (by norm_num)
  σStep mStepI σStep_meas σStep_nonneg σStep_int mStepI_meas (fun t => le_refl _)

example := cor_transient_b_induced (m0 := 0.6) (G := 0.2) (k := 0) (X := 1) (α := 0.3)
  (lam := 1.2) (sbar := 0.5) (T := 2) (s0 := 0.01) (Rbar := 0.9) (by norm_num) (by norm_num)
  (by norm_num) (by norm_num) (by unfold Rinf; norm_num) (by norm_num) (by norm_num) (by norm_num)
  σStep mStepI σStep_meas σStep_nonneg σStep_int mStepI_meas (fun t => le_refl _)

end RuleOfXChecks
