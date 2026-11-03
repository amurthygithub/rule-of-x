import RuleOfX.Saturation
import Mathlib.MeasureTheory.Integral.IntervalIntegral.FundThmCalculus
import Mathlib.MeasureTheory.Integral.IntervalIntegral.Basic
import Mathlib.MeasureTheory.Function.SpecialFunctions.Basic
import Mathlib.MeasureTheory.Integral.Bochner.Basic

/-!
# Proposition prop:budget (a), (c) in continuous time, and Corollary cor:transient (b)

Continuous time on `[0, T]`, `T ≥ 0`. The spend path `σ` is measurable and nonnegative with
`∫_0^T σ^α < ∞` (`IntervalIntegrable`); margins `m` are measurable with
`m(t) ≤ m₀(t) - σ(t) - k g(t)`; growth is `g(t) = G + λ h(s(t)) σ(t)^α` (eq:growth).

**Deviation from the paper (reported in the README).** The paper takes "the induced share
path from `s(0) = s₀`", i.e. the solution of `ṡ = s λ h(s) σ^α`, which is absolutely continuous
and satisfies the equation almost everywhere. Here the share path `s` is a hypothesis: any
function that is differentiable at every `t ∈ [0, T]` with `ṡ(t) = s(t) λ h(s(t)) σ(t)^α`
(Assumption ass:market, `g = G + ṡ/s`, combined with eq:growth) and that stays in `(0, s̄)`
(Assumption ass:market). The existence and uniqueness of the logistic solution, and the
almost-everywhere version of the argument, are not formalized. When `σ` is continuous the
induced path satisfies these hypotheses.
-/

noncomputable section
open Real Set Filter Topology MeasureTheory intervalIntegral

set_option autoImplicit false

namespace RuleOfX

variable {m0 G k α lam sbar X T : ℝ}

/-- Excess growth along a path: `Δ(t) = λ h(s(t)) σ(t)^α`. -/
def Δpath (α lam sbar : ℝ) (σ s : ℝ → ℝ) (t : ℝ) : ℝ := lam * hdr sbar (s t) * σ t ^ α

/-- Score along a path: `R_X(t) = X g(t) + m(t)` with `g(t) = G + Δ(t)`. -/
def Rpath (G α lam sbar X : ℝ) (σ s m : ℝ → ℝ) (t : ℝ) : ℝ :=
  X * (G + Δpath α lam sbar σ s t) + m t

/-- **Proposition prop:budget (c), continuous time** (and (a) with a constant intercept).
"(Moving intercept.) If the margin intercept moves over time, `m₀(t)`, then (a) holds with
`R_∞(t) = m₀(t) + (X-k)G` in place of `R_∞`":
`∫_0^T (R_X(t) - R_∞(t))⁺ dt ≤ (X-k) ln(s(T)/s₀) < (X-k) ln(s̄/s₀)`. -/
theorem prop_budget_c_continuous (_hα : 0 < α) (hlam : 0 < lam) (hsbar : 0 < sbar) (hXk : k < X)
    (hT : 0 ≤ T) (σ m s m0 : ℝ → ℝ) (hσm : Measurable σ) (hσ0 : ∀ t, 0 ≤ σ t)
    (hσint : IntervalIntegrable (fun t => σ t ^ α) volume 0 T)
    (hmm : Measurable m) (hm0m : Measurable m0)
    (hs : ∀ t ∈ Icc 0 T, HasDerivAt s (s t * Δpath α lam sbar σ s t) t)
    (hsrange : ∀ t ∈ Icc 0 T, 0 < s t ∧ s t < sbar)
    (hm : ∀ t, m t ≤ m0 t - σ t - k * (G + Δpath α lam sbar σ s t)) :
    ∫ t in (0 : ℝ)..T, max (Rpath G α lam sbar X σ s m t - (m0 t + (X - k) * G)) 0 ≤
      (X - k) * Real.log (s T / s 0) ∧
    (X - k) * Real.log (s T / s 0) < (X - k) * Real.log (sbar / s 0) := by
  have hy : 0 < X - k := sub_pos.2 hXk
  have hs0 := hsrange 0 ⟨le_rfl, hT⟩
  have hsT := hsrange T ⟨hT, le_rfl⟩
  have hscont : ContinuousOn s (Icc 0 T) := fun t ht =>
    (hs t ht).continuousAt.continuousWithinAt
  -- `Δ` is interval integrable: `σ^α` is, and `λ h(s(t))` is continuous
  have hΔint : IntervalIntegrable (Δpath α lam sbar σ s) volume 0 T := by
    have h1 : ContinuousOn (fun t => lam * hdr sbar (s t)) (uIcc 0 T) := by
      rw [uIcc_of_le hT]
      exact continuousOn_const.mul (hdr_continuous.comp_continuousOn hscont)
    exact hσint.continuousOn_mul h1
  -- fundamental theorem of calculus: `∫ Δ = ln s(T) - ln s(0)`
  have hlog : ∀ t ∈ uIcc 0 T, HasDerivAt (fun t => Real.log (s t)) (Δpath α lam sbar σ s t) t := by
    intro t ht
    rw [uIcc_of_le hT] at ht
    have hst := (hsrange t ht).1.ne'
    have := (hs t ht).log hst
    refine this.congr_deriv ?_
    field_simp
  have hFTC := integral_eq_sub_of_hasDerivAt hlog hΔint
  -- pointwise: `(R - R_∞)⁺ ≤ (X-k) Δ`
  have hΔ0 : ∀ t ∈ Icc 0 T, 0 ≤ Δpath α lam sbar σ s t := fun t ht =>
    mul_nonneg (mul_nonneg hlam.le (hdr_pos hsbar (hsrange t ht).2).le)
      (Real.rpow_nonneg (hσ0 t) _)
  have hpt : ∀ t ∈ Icc 0 T, max (Rpath G α lam sbar X σ s m t - (m0 t + (X - k) * G)) 0 ≤
      (X - k) * Δpath α lam sbar σ s t := by
    intro t ht
    apply max_le
    · unfold Rpath
      have := hm t
      have := hσ0 t
      nlinarith
    · exact mul_nonneg hy.le (hΔ0 t ht)
  -- integrability of `(R - R_∞)⁺`
  have hmax_int : IntervalIntegrable
      (fun t => max (Rpath G α lam sbar X σ s m t - (m0 t + (X - k) * G)) 0) volume 0 T := by
    refine IntervalIntegrable.mono_fun' (hΔint.const_mul (X - k)) ?_ ?_
    · rw [uIoc_of_le hT]
      have hsm : AEStronglyMeasurable s (volume.restrict (Ioc 0 T)) :=
        (hscont.mono Ioc_subset_Icc_self).aestronglyMeasurable measurableSet_Ioc
      have hΔm : AEStronglyMeasurable (Δpath α lam sbar σ s) (volume.restrict (Ioc 0 T)) := by
        unfold Δpath
        exact ((hdr_continuous.comp_aestronglyMeasurable hsm).const_mul lam).mul
          ((hσm.pow_const α).aestronglyMeasurable)
      have hRm : AEStronglyMeasurable
          (fun t => Rpath G α lam sbar X σ s m t - (m0 t + (X - k) * G))
          (volume.restrict (Ioc 0 T)) := by
        unfold Rpath
        exact ((hΔm.const_add G).const_mul X |>.add hmm.aestronglyMeasurable).sub
          (hm0m.aestronglyMeasurable.add_const _)
      exact (continuous_id.max continuous_const).comp_aestronglyMeasurable hRm
    · rw [uIoc_of_le hT]
      refine ae_restrict_of_forall_mem measurableSet_Ioc fun t ht => ?_
      have ht' : t ∈ Icc 0 T := Ioc_subset_Icc_self ht
      show ‖max (Rpath G α lam sbar X σ s m t - (m0 t + (X - k) * G)) 0‖ ≤ (X - k) * Δpath α lam sbar σ s t
      rw [Real.norm_of_nonneg (le_max_right _ _)]
      exact hpt t ht'
  constructor
  · calc ∫ t in (0 : ℝ)..T, max (Rpath G α lam sbar X σ s m t - (m0 t + (X - k) * G)) 0
        ≤ ∫ t in (0 : ℝ)..T, (X - k) * Δpath α lam sbar σ s t :=
          integral_mono_on hT hmax_int (hΔint.const_mul (X - k)) hpt
      _ = (X - k) * ∫ t in (0 : ℝ)..T, Δpath α lam sbar σ s t := integral_const_mul _ _
      _ = (X - k) * Real.log (s T / s 0) := by
          rw [hFTC, Real.log_div hsT.1.ne' hs0.1.ne']
  · apply mul_lt_mul_of_pos_left _ hy
    apply Real.log_lt_log (div_pos hsT.1 hs0.1)
    exact div_lt_div_of_pos_right hsT.2 hs0.1

/-- **Proposition prop:budget (a).** "(Continuous time.) Take any measurable spend path
`σ : [0,T] → [0, σ̄]` with `∫_0^T σ^α dt < ∞`, any measurable margins
`m(t) ≤ m₀ - σ(t) - k g(t)`, and the induced share path from `s(0) = s₀`. Then
`∫_0^T (R_X(t) - R_∞)⁺ dt ≤ (X-k) ln(s(T)/s₀) < (X-k) ln(s̄/s₀)`."
(See the file docstring for how the share path enters; the cap `σ ≤ σ̄` is not needed.) -/
theorem prop_budget_a (hα : 0 < α) (hlam : 0 < lam) (hsbar : 0 < sbar) (hXk : k < X)
    (hT : 0 ≤ T) (σ m s : ℝ → ℝ) (hσm : Measurable σ) (hσ0 : ∀ t, 0 ≤ σ t)
    (hσint : IntervalIntegrable (fun t => σ t ^ α) volume 0 T) (hmm : Measurable m)
    (hs : ∀ t ∈ Icc 0 T, HasDerivAt s (s t * Δpath α lam sbar σ s t) t)
    (hsrange : ∀ t ∈ Icc 0 T, 0 < s t ∧ s t < sbar)
    (hm : ∀ t, m t ≤ m0 - σ t - k * (G + Δpath α lam sbar σ s t)) :
    ∫ t in (0 : ℝ)..T, max (Rpath G α lam sbar X σ s m t - Rinf m0 G k X) 0 ≤
      (X - k) * Real.log (s T / s 0) ∧
    (X - k) * Real.log (s T / s 0) < (X - k) * Real.log (sbar / s 0) :=
  prop_budget_c_continuous hα hlam hsbar hXk hT σ m s (fun _ => m0) hσm hσ0 hσint hmm
    measurable_const hs hsrange hm

/-- **Corollary cor:transient (b), first claim.** "(Continuous time.) In the setting of
prop:budget (a), the time a firm spends at or above `R̄` is at most
`(X-k) ln(s̄/s₀)/(R̄ - R_∞)`." The time is the Lebesgue measure of `{t ∈ (0, T] : R_X(t) ≥ R̄}`,
for every horizon `T`. (The second claim, about the static optimum policy of prop:myopic, is out
of scope.) -/
theorem cor_transient_b {Rbar : ℝ} (hα : 0 < α) (hlam : 0 < lam) (hsbar : 0 < sbar) (hXk : k < X)
    (hR : Rinf m0 G k X < Rbar)
    (hT : 0 ≤ T) (σ m s : ℝ → ℝ) (hσm : Measurable σ) (hσ0 : ∀ t, 0 ≤ σ t)
    (hσint : IntervalIntegrable (fun t => σ t ^ α) volume 0 T) (hmm : Measurable m)
    (hs : ∀ t ∈ Icc 0 T, HasDerivAt s (s t * Δpath α lam sbar σ s t) t)
    (hsrange : ∀ t ∈ Icc 0 T, 0 < s t ∧ s t < sbar)
    (hm : ∀ t, m t ≤ m0 - σ t - k * (G + Δpath α lam sbar σ s t)) :
    volume.real ({t | Rbar ≤ Rpath G α lam sbar X σ s m t} ∩ Ioc 0 T) ≤
      (X - k) * Real.log (sbar / s 0) / (Rbar - Rinf m0 G k X) := by
  have hy : 0 < X - k := sub_pos.2 hXk
  have hε : 0 < Rbar - Rinf m0 G k X := sub_pos.2 hR
  obtain ⟨hint, hlt⟩ := prop_budget_a hα hlam hsbar hXk hT σ m s hσm hσ0 hσint hmm hs hsrange hm
  set f : ℝ → ℝ := fun t => max (Rpath G α lam sbar X σ s m t - Rinf m0 G k X) 0 with hf
  set μ : Measure ℝ := volume.restrict (Ioc 0 T) with hμ
  -- integrability of `f` on `(0, T]`, re-derived from the integral bound via the same lemma
  have hfint : Integrable f μ := by
    -- reuse the proof of integrability inside `prop_budget_c_continuous`
    have hs0 := hsrange 0 ⟨le_rfl, hT⟩
    have hscont : ContinuousOn s (Icc 0 T) := fun t ht =>
      (hs t ht).continuousAt.continuousWithinAt
    have hΔint : IntervalIntegrable (Δpath α lam sbar σ s) volume 0 T := by
      have h1 : ContinuousOn (fun t => lam * hdr sbar (s t)) (uIcc 0 T) := by
        rw [uIcc_of_le hT]
        exact continuousOn_const.mul (hdr_continuous.comp_continuousOn hscont)
      exact hσint.continuousOn_mul h1
    have hΔ0 : ∀ t ∈ Icc 0 T, 0 ≤ Δpath α lam sbar σ s t := fun t ht =>
      mul_nonneg (mul_nonneg hlam.le (hdr_pos hsbar (hsrange t ht).2).le)
        (Real.rpow_nonneg (hσ0 t) _)
    have hpt : ∀ t ∈ Icc 0 T, f t ≤ (X - k) * Δpath α lam sbar σ s t := by
      intro t ht
      simp only [hf]
      apply max_le
      · unfold Rpath Rinf
        have := hm t
        have := hσ0 t
        nlinarith
      · exact mul_nonneg hy.le (hΔ0 t ht)
    have hmax_int : IntervalIntegrable f volume 0 T := by
      refine IntervalIntegrable.mono_fun' (hΔint.const_mul (X - k)) ?_ ?_
      · rw [uIoc_of_le hT]
        have hsm : AEStronglyMeasurable s (volume.restrict (Ioc 0 T)) :=
          (hscont.mono Ioc_subset_Icc_self).aestronglyMeasurable measurableSet_Ioc
        have hΔm : AEStronglyMeasurable (Δpath α lam sbar σ s) (volume.restrict (Ioc 0 T)) := by
          unfold Δpath
          exact ((hdr_continuous.comp_aestronglyMeasurable hsm).const_mul lam).mul
            ((hσm.pow_const α).aestronglyMeasurable)
        have hRm : AEStronglyMeasurable
            (fun t => Rpath G α lam sbar X σ s m t - Rinf m0 G k X)
            (volume.restrict (Ioc 0 T)) := by
          unfold Rpath
          exact (((hΔm.const_add G).const_mul X).add hmm.aestronglyMeasurable).sub
            aestronglyMeasurable_const
        exact (continuous_id.max continuous_const).comp_aestronglyMeasurable hRm
      · rw [uIoc_of_le hT]
        refine ae_restrict_of_forall_mem measurableSet_Ioc fun t ht => ?_
        have ht' : t ∈ Icc 0 T := Ioc_subset_Icc_self ht
        show ‖f t‖ ≤ (X - k) * Δpath α lam sbar σ s t
        rw [Real.norm_of_nonneg (by simp only [hf]; exact le_max_right _ _)]
        exact hpt t ht'
    have := intervalIntegrable_iff.1 hmax_int
    rwa [uIoc_of_le hT] at this
  have hnonneg : 0 ≤ᵐ[μ] f := Filter.Eventually.of_forall fun t => le_max_right _ _
  have hmarkov := mul_meas_ge_le_integral_of_nonneg hnonneg hfint (Rbar - Rinf m0 G k X)
  -- the sublevel set is the set of dates with `R_X ≥ R̄`
  have hset : {x | Rbar - Rinf m0 G k X ≤ f x} = {t | Rbar ≤ Rpath G α lam sbar X σ s m t} := by
    ext t
    simp only [hf, Set.mem_ofPred_eq, le_max_iff]
    constructor
    · rintro (h | h)
      · linarith
      · linarith
    · intro h; left; linarith
  rw [hset] at hmarkov
  have hμreal : μ.real {t | Rbar ≤ Rpath G α lam sbar X σ s m t} =
      volume.real ({t | Rbar ≤ Rpath G α lam sbar X σ s m t} ∩ Ioc 0 T) := by
    rw [hμ, measureReal_def, measureReal_def, Measure.restrict_apply' measurableSet_Ioc]
  have hint' : ∫ x, f x ∂μ ≤ (X - k) * Real.log (sbar / s 0) := by
    rw [hμ, ← integral_of_le hT]
    exact hint.trans hlt.le
  rw [hμreal] at hmarkov
  rw [le_div_iff₀ hε]
  linarith

end RuleOfX
