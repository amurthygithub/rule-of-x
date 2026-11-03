import RuleOfX.Saturation
import Mathlib.MeasureTheory.Integral.IntervalIntegral.FundThmCalculus
import Mathlib.MeasureTheory.Integral.IntervalIntegral.Basic
import Mathlib.MeasureTheory.Integral.IntervalIntegral.AbsolutelyContinuousFun
import Mathlib.MeasureTheory.Function.AbsolutelyContinuous
import Mathlib.MeasureTheory.Function.SpecialFunctions.Basic
import Mathlib.MeasureTheory.Integral.Bochner.Basic
import Mathlib.Analysis.Calculus.MeanValue

/-!
# Proposition prop:budget (a), (c) in continuous time, and Corollary cor:transient (b)

Continuous time on `[0, T]`, `T ≥ 0`. The spend path `σ` is measurable and nonnegative with
`∫_0^T σ^α < ∞` (`IntervalIntegrable`); margins `m` are measurable with
`m(t) ≤ m₀(t) - σ(t) - k g(t)`; growth is `g(t) = G + λ h(s(t)) σ(t)^α` (eq:growth).

**The share path.** The paper takes "the induced share path from `s(0) = s₀`", i.e. the
(Carathéodory) solution of `ṡ = s λ h(s) σ^α`: an absolutely continuous function that satisfies
the equation almost everywhere. Here the share path is a hypothesis with exactly those
properties: `s` is absolutely continuous on `[0,T]` (`AbsolutelyContinuousOnInterval s 0 T`),
satisfies `ṡ(t) = s(t) λ h(s(t)) σ(t)^α` for almost every `t ∈ [0,T]`, and stays in `(0, s̄)` on
`[0,T]` (Assumption ass:market). The existence (and uniqueness) of this solution, which the
paper's proof obtains from the explicit logistic formula, is not formalized; the paper also
derives `s < s̄` from that formula, whereas here it is assumed. Every measurable spend path for
which the induced share path exists is covered.
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

/-- Convenience: a share path that satisfies the share equation at every `t ∈ [0,T]` satisfies it
almost everywhere. -/
theorem hode_of_forall {σ s : ℝ → ℝ}
    (hs : ∀ t ∈ Icc 0 T, HasDerivAt s (s t * Δpath α lam sbar σ s t) t) :
    ∀ᵐ t, t ∈ Icc 0 T → HasDerivAt s (s t * Δpath α lam sbar σ s t) t :=
  Filter.Eventually.of_forall hs

/-- Convenience: a `C¹` share path is absolutely continuous (Mathlib's
`ContDiffOn.absolutelyContinuousOnInterval`). -/
theorem ac_of_contDiffOn {s : ℝ → ℝ} (hs : ContDiffOn ℝ 1 s (uIcc 0 T)) :
    AbsolutelyContinuousOnInterval s 0 T :=
  hs.absolutelyContinuousOnInterval

/-- `log` is Lipschitz on `[δ, ∞)` for `δ > 0`. -/
theorem log_lipschitzOnWith {δ : ℝ} (hδ : 0 < δ) :
    LipschitzOnWith ⟨δ⁻¹, (inv_pos.2 hδ).le⟩ Real.log (Ici δ) := by
  refine (convex_Ici δ).lipschitzOnWith_of_nnnorm_hasDerivWithin_le (f' := fun x => x⁻¹)
    (fun x hx => (Real.hasDerivAt_log (by linarith [mem_Ici.1 hx] : x ≠ 0)).hasDerivWithinAt)
    (fun x hx => ?_)
  have hx' : δ ≤ x := hx
  rw [Real.nnnorm_of_nonneg (inv_pos.2 (by linarith : (0 : ℝ) < x)).le]
  exact Subtype.mk_le_mk.2 (inv_anti₀ hδ hx')

/-- Share accounting along an absolutely continuous share path satisfying the share equation
almost everywhere: `∫_0^T Δ dt = ln(s(T)/s(0))`, with `Δ` interval integrable. -/
theorem integral_Δpath (_hlam : 0 < lam) (_hsbar : 0 < sbar) (hT : 0 ≤ T) (σ s : ℝ → ℝ)
    (_hσ0 : ∀ t, 0 ≤ σ t) (hσint : IntervalIntegrable (fun t => σ t ^ α) volume 0 T)
    (hac : AbsolutelyContinuousOnInterval s 0 T)
    (hsrange : ∀ t ∈ Icc 0 T, 0 < s t ∧ s t < sbar)
    (hode : ∀ᵐ t, t ∈ Icc 0 T → HasDerivAt s (s t * Δpath α lam sbar σ s t) t) :
    IntervalIntegrable (Δpath α lam sbar σ s) volume 0 T ∧
    ∫ t in (0 : ℝ)..T, Δpath α lam sbar σ s t = Real.log (s T / s 0) := by
  have hs0 := hsrange 0 ⟨le_rfl, hT⟩
  have hsT := hsrange T ⟨hT, le_rfl⟩
  have hscont : ContinuousOn s (Icc 0 T) := by
    have := hac.continuousOn; rwa [uIcc_of_le hT] at this
  -- `Δ` is interval integrable
  have hΔint : IntervalIntegrable (Δpath α lam sbar σ s) volume 0 T := by
    have h1 : ContinuousOn (fun t => lam * hdr sbar (s t)) (uIcc 0 T) := by
      rw [uIcc_of_le hT]
      exact continuousOn_const.mul (hdr_continuous.comp_continuousOn hscont)
    exact hσint.continuousOn_mul h1
  refine ⟨hΔint, ?_⟩
  -- `s` is bounded away from `0` on `[0,T]`, so `log ∘ s` is absolutely continuous
  obtain ⟨t₀, ht₀, hmin⟩ := isCompact_Icc.exists_isMinOn ⟨0, le_rfl, hT⟩ hscont
  have hδ : 0 < s t₀ := (hsrange t₀ ht₀).1
  have hmaps : MapsTo s (uIcc 0 T) (Ici (s t₀)) := by
    rw [uIcc_of_le hT]
    intro t ht
    exact (isMinOn_iff.1 hmin) t ht
  have hL : AbsolutelyContinuousOnInterval (Real.log ∘ s) 0 T :=
    (log_lipschitzOnWith hδ).comp_absolutelyContinuousOnInterval hmaps hac
  have hFTC := hL.integral_deriv_eq_sub
  -- a.e. on `[0,T]`, `(log ∘ s)' = Δ`
  have hae : ∀ᵐ t, t ∈ uIoc (0 : ℝ) T → deriv (Real.log ∘ s) t = Δpath α lam sbar σ s t := by
    filter_upwards [hode] with t ht htI
    have ht' : t ∈ Icc 0 T := by
      rw [uIoc_of_le hT] at htI; exact Ioc_subset_Icc_self htI
    have hst := (hsrange t ht').1.ne'
    have hd := (ht ht').log hst
    have : HasDerivAt (Real.log ∘ s) (Δpath α lam sbar σ s t) t := by
      refine hd.congr_deriv ?_
      field_simp
    exact this.deriv
  rw [← integral_congr_ae hae, hFTC]
  simp only [Function.comp]
  rw [Real.log_div hsT.1.ne' hs0.1.ne']

/-- Core of the score budget: if `0 ≤ f ≤ c Δ` on `[0,T]` with `f` measurable, then `f` is
integrable on `[0,T]` and `∫_0^T f ≤ c ln(s(T)/s₀) ≤ c ln(s̄/s₀)` (the last with `<` for the
logarithms). -/
theorem budget_core (hlam : 0 < lam) (hsbar : 0 < sbar) (hT : 0 ≤ T) (σ s : ℝ → ℝ)
    (hσ0 : ∀ t, 0 ≤ σ t) (hσint : IntervalIntegrable (fun t => σ t ^ α) volume 0 T)
    (hac : AbsolutelyContinuousOnInterval s 0 T)
    (hsrange : ∀ t ∈ Icc 0 T, 0 < s t ∧ s t < sbar)
    (hode : ∀ᵐ t, t ∈ Icc 0 T → HasDerivAt s (s t * Δpath α lam sbar σ s t) t)
    (f : ℝ → ℝ) (hfm : AEStronglyMeasurable f (volume.restrict (Ioc 0 T)))
    (hf0 : ∀ t, 0 ≤ f t) {c : ℝ} (_hc : 0 ≤ c)
    (hfle : ∀ t ∈ Icc 0 T, f t ≤ c * Δpath α lam sbar σ s t) :
    IntervalIntegrable f volume 0 T ∧
    ∫ t in (0 : ℝ)..T, f t ≤ c * Real.log (s T / s 0) ∧
    Real.log (s T / s 0) < Real.log (sbar / s 0) := by
  have hs0 := hsrange 0 ⟨le_rfl, hT⟩
  have hsT := hsrange T ⟨hT, le_rfl⟩
  obtain ⟨hΔint, hFTC⟩ := integral_Δpath hlam hsbar hT σ s hσ0 hσint hac hsrange hode
  have hfint : IntervalIntegrable f volume 0 T := by
    refine IntervalIntegrable.mono_fun' (hΔint.const_mul c) ?_ ?_
    · rw [uIoc_of_le hT]; exact hfm
    · rw [uIoc_of_le hT]
      refine ae_restrict_of_forall_mem measurableSet_Ioc fun t ht => ?_
      show ‖f t‖ ≤ c * Δpath α lam sbar σ s t
      rw [Real.norm_of_nonneg (hf0 t)]
      exact hfle t (Ioc_subset_Icc_self ht)
  refine ⟨hfint, ?_, ?_⟩
  · calc ∫ t in (0 : ℝ)..T, f t ≤ ∫ t in (0 : ℝ)..T, c * Δpath α lam sbar σ s t :=
          integral_mono_on hT hfint (hΔint.const_mul c) hfle
      _ = c * ∫ t in (0 : ℝ)..T, Δpath α lam sbar σ s t := integral_const_mul _ _
      _ = c * Real.log (s T / s 0) := by rw [hFTC]
  · apply Real.log_lt_log (div_pos hsT.1 hs0.1)
    exact div_lt_div_of_pos_right hsT.2 hs0.1

/-- Markov's inequality on `(0,T]`: if `f ≥ 0` is integrable with `∫_0^T f ≤ B`, the Lebesgue
measure of `{t ∈ (0,T] : f(t) ≥ ε}` is at most `B/ε`. -/
theorem time_bound (hT : 0 ≤ T) (f : ℝ → ℝ) (hfint : IntervalIntegrable f volume 0 T)
    (hf0 : ∀ t, 0 ≤ f t) {ε B : ℝ} (hε : 0 < ε) (hB : ∫ t in (0 : ℝ)..T, f t ≤ B) :
    volume.real ({t | ε ≤ f t} ∩ Ioc 0 T) ≤ B / ε := by
  have hint : Integrable f (volume.restrict (Ioc 0 T)) := by
    have := intervalIntegrable_iff.1 hfint
    rwa [uIoc_of_le hT] at this
  have hnonneg : 0 ≤ᵐ[volume.restrict (Ioc 0 T)] f := Filter.Eventually.of_forall hf0
  have hmarkov := mul_meas_ge_le_integral_of_nonneg hnonneg hint ε
  rw [measureReal_def, Measure.restrict_apply' measurableSet_Ioc, ← measureReal_def] at hmarkov
  have hB' : ∫ x, f x ∂(volume.restrict (Ioc 0 T)) ≤ B := by
    rw [← integral_of_le hT]; exact hB
  rw [le_div_iff₀ hε]
  linarith

/-- Measurability of `(R_X(t) - R_∞(t))⁺` on `(0,T]`. -/
theorem excess_aestronglyMeasurable (_hT : 0 ≤ T) (σ m s m0 : ℝ → ℝ) (hσm : Measurable σ)
    (hmm : Measurable m) (hm0m : Measurable m0) (hscont : ContinuousOn s (Icc 0 T)) :
    AEStronglyMeasurable
      (fun t => max (Rpath G α lam sbar X σ s m t - (m0 t + (X - k) * G)) 0)
      (volume.restrict (Ioc 0 T)) := by
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
    exact (((hΔm.const_add G).const_mul X).add hmm.aestronglyMeasurable).sub
      (hm0m.aestronglyMeasurable.add_const _)
  exact (continuous_id.max continuous_const).comp_aestronglyMeasurable hRm

/-- **Proposition prop:budget (c), continuous time** (and (a) with a constant intercept).
"(Moving intercept.) If the margin intercept moves over time, `m₀(t)`, then (a) holds with
`R_∞(t) = m₀(t) + (X-k)G` in place of `R_∞`": the integrand `(R_X(t) - R_∞(t))⁺` is integrable
on `[0,T]` and `∫_0^T (R_X(t) - R_∞(t))⁺ dt ≤ (X-k) ln(s(T)/s₀) < (X-k) ln(s̄/s₀)`.
(`m₀(·)` must be measurable, `hm0m`; see the file docstring for the share path.) -/
theorem prop_budget_c_continuous (_hα : 0 < α) (hlam : 0 < lam) (hsbar : 0 < sbar) (hXk : k < X)
    (hT : 0 ≤ T) (σ m s m0 : ℝ → ℝ) (hσm : Measurable σ) (hσ0 : ∀ t, 0 ≤ σ t)
    (hσint : IntervalIntegrable (fun t => σ t ^ α) volume 0 T)
    (hmm : Measurable m) (hm0m : Measurable m0)
    (hac : AbsolutelyContinuousOnInterval s 0 T)
    (hsrange : ∀ t ∈ Icc 0 T, 0 < s t ∧ s t < sbar)
    (hode : ∀ᵐ t, t ∈ Icc 0 T → HasDerivAt s (s t * Δpath α lam sbar σ s t) t)
    (hm : ∀ t, m t ≤ m0 t - σ t - k * (G + Δpath α lam sbar σ s t)) :
    IntervalIntegrable (fun t => max (Rpath G α lam sbar X σ s m t - (m0 t + (X - k) * G)) 0)
      volume 0 T ∧
    ∫ t in (0 : ℝ)..T, max (Rpath G α lam sbar X σ s m t - (m0 t + (X - k) * G)) 0 ≤
      (X - k) * Real.log (s T / s 0) ∧
    (X - k) * Real.log (s T / s 0) < (X - k) * Real.log (sbar / s 0) := by
  have hy : 0 < X - k := sub_pos.2 hXk
  have hscont : ContinuousOn s (Icc 0 T) := by
    have := hac.continuousOn; rwa [uIcc_of_le hT] at this
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
  obtain ⟨hint, hle, hlt⟩ := budget_core hlam hsbar hT σ s hσ0 hσint hac hsrange hode _
    (excess_aestronglyMeasurable hT σ m s m0 hσm hmm hm0m hscont) (fun t => le_max_right _ _)
    hy.le hpt
  exact ⟨hint, hle, mul_lt_mul_of_pos_left hlt hy⟩

/-- **Proposition prop:budget (a).** "(Continuous time.) Take any measurable spend path
`σ : [0,T] → [0, σ̄]` with `∫_0^T σ^α dt < ∞`, any measurable margins
`m(t) ≤ m₀ - σ(t) - k g(t)`, and the induced share path from `s(0) = s₀`. Then
`∫_0^T (R_X(t) - R_∞)⁺ dt ≤ (X-k) ln(s(T)/s₀) < (X-k) ln(s̄/s₀)`."
The integrand is shown to be integrable (first conjunct). See the file docstring for how the
share path enters; the cap `σ ≤ σ̄` is not needed. -/
theorem prop_budget_a (hα : 0 < α) (hlam : 0 < lam) (hsbar : 0 < sbar) (hXk : k < X)
    (hT : 0 ≤ T) (σ m s : ℝ → ℝ) (hσm : Measurable σ) (hσ0 : ∀ t, 0 ≤ σ t)
    (hσint : IntervalIntegrable (fun t => σ t ^ α) volume 0 T) (hmm : Measurable m)
    (hac : AbsolutelyContinuousOnInterval s 0 T)
    (hsrange : ∀ t ∈ Icc 0 T, 0 < s t ∧ s t < sbar)
    (hode : ∀ᵐ t, t ∈ Icc 0 T → HasDerivAt s (s t * Δpath α lam sbar σ s t) t)
    (hm : ∀ t, m t ≤ m0 - σ t - k * (G + Δpath α lam sbar σ s t)) :
    IntervalIntegrable (fun t => max (Rpath G α lam sbar X σ s m t - Rinf m0 G k X) 0)
      volume 0 T ∧
    ∫ t in (0 : ℝ)..T, max (Rpath G α lam sbar X σ s m t - Rinf m0 G k X) 0 ≤
      (X - k) * Real.log (s T / s 0) ∧
    (X - k) * Real.log (s T / s 0) < (X - k) * Real.log (sbar / s 0) :=
  prop_budget_c_continuous hα hlam hsbar hXk hT σ m s (fun _ => m0) hσm hσ0 hσint hmm
    measurable_const hac hsrange hode hm

/-- The set of dates at or above `R̄` is the set where the excess `(R_X - R_∞)⁺` is at least
`R̄ - R_∞ > 0`. -/
theorem set_ge_eq {Rbar : ℝ} (hR : Rinf m0 G k X < Rbar) (σ s m : ℝ → ℝ) :
    {t | Rbar - Rinf m0 G k X ≤ max (Rpath G α lam sbar X σ s m t - Rinf m0 G k X) 0} =
      {t | Rbar ≤ Rpath G α lam sbar X σ s m t} := by
  ext t
  simp only [Set.mem_ofPred_eq, le_max_iff]
  constructor
  · rintro (h | h)
    · linarith
    · linarith
  · intro h; left; linarith

/-- **Corollary cor:transient (b), first claim.** "(Continuous time.) In the setting of
prop:budget (a), the time a firm spends at or above `R̄` is at most
`(X-k) ln(s̄/s₀)/(R̄ - R_∞)`." The time is the Lebesgue measure of `{t ∈ (0, T] : R_X(t) ≥ R̄}`,
for every horizon `T`. -/
theorem cor_transient_b {Rbar : ℝ} (hα : 0 < α) (hlam : 0 < lam) (hsbar : 0 < sbar) (hXk : k < X)
    (hR : Rinf m0 G k X < Rbar)
    (hT : 0 ≤ T) (σ m s : ℝ → ℝ) (hσm : Measurable σ) (hσ0 : ∀ t, 0 ≤ σ t)
    (hσint : IntervalIntegrable (fun t => σ t ^ α) volume 0 T) (hmm : Measurable m)
    (hac : AbsolutelyContinuousOnInterval s 0 T)
    (hsrange : ∀ t ∈ Icc 0 T, 0 < s t ∧ s t < sbar)
    (hode : ∀ᵐ t, t ∈ Icc 0 T → HasDerivAt s (s t * Δpath α lam sbar σ s t) t)
    (hm : ∀ t, m t ≤ m0 - σ t - k * (G + Δpath α lam sbar σ s t)) :
    volume.real ({t | Rbar ≤ Rpath G α lam sbar X σ s m t} ∩ Ioc 0 T) ≤
      (X - k) * Real.log (sbar / s 0) / (Rbar - Rinf m0 G k X) := by
  have hε : 0 < Rbar - Rinf m0 G k X := sub_pos.2 hR
  obtain ⟨hint, hle, hlt⟩ := prop_budget_a hα hlam hsbar hXk hT σ m s hσm hσ0 hσint hmm hac
    hsrange hode hm
  rw [← set_ge_eq hR σ s m]
  exact time_bound hT _ hint (fun t => le_max_right _ _) hε (hle.trans hlt.le)

/-- **Corollary cor:transient (b), second claim.** "Under the growth technology eq:growth, a firm
that sets spend at the static optimum for the weight `X` at every date spends at most
`(1-α)(X-k) ln(s̄/s₀)/(R̄ - R_∞)` there." The policy is `σ(t) = σ*(λ h(s(t)), X - k)`
(eq:sigstar at the current share), hypothesis `hpol`; the other hypotheses are those of
prop:budget (a). -/
theorem cor_transient_b_optimum {Rbar : ℝ} (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam)
    (hsbar : 0 < sbar) (hXk : k < X) (hR : Rinf m0 G k X < Rbar)
    (hT : 0 ≤ T) (σ m s : ℝ → ℝ) (hσm : Measurable σ) (hσ0 : ∀ t, 0 ≤ σ t)
    (hσint : IntervalIntegrable (fun t => σ t ^ α) volume 0 T) (hmm : Measurable m)
    (hac : AbsolutelyContinuousOnInterval s 0 T)
    (hsrange : ∀ t ∈ Icc 0 T, 0 < s t ∧ s t < sbar)
    (hode : ∀ᵐ t, t ∈ Icc 0 T → HasDerivAt s (s t * Δpath α lam sbar σ s t) t)
    (hm : ∀ t, m t ≤ m0 - σ t - k * (G + Δpath α lam sbar σ s t))
    (hpol : ∀ t ∈ Icc 0 T, σ t = σstar α (lam * hdr sbar (s t)) (X - k)) :
    IntervalIntegrable (fun t => max (Rpath G α lam sbar X σ s m t - Rinf m0 G k X) 0)
      volume 0 T ∧
    ∫ t in (0 : ℝ)..T, max (Rpath G α lam sbar X σ s m t - Rinf m0 G k X) 0 ≤
      (1 - α) * (X - k) * Real.log (s T / s 0) ∧
    volume.real ({t | Rbar ≤ Rpath G α lam sbar X σ s m t} ∩ Ioc 0 T) ≤
      (1 - α) * (X - k) * Real.log (sbar / s 0) / (Rbar - Rinf m0 G k X) := by
  have hy : 0 < X - k := sub_pos.2 hXk
  have hε : 0 < Rbar - Rinf m0 G k X := sub_pos.2 hR
  have hc : 0 ≤ (1 - α) * (X - k) := mul_nonneg (by linarith) hy.le
  have hscont : ContinuousOn s (Icc 0 T) := by
    have := hac.continuousOn; rwa [uIcc_of_le hT] at this
  -- at the static optimum, `(R_X - R_∞)⁺ ≤ (1-α)(X-k)Δ`
  have hpt : ∀ t ∈ Icc 0 T, max (Rpath G α lam sbar X σ s m t - Rinf m0 G k X) 0 ≤
      (1 - α) * (X - k) * Δpath α lam sbar σ s t := by
    intro t ht
    have hℓ : 0 < lam * hdr sbar (s t) := ℓ_pos hlam hsbar (hsrange t ht).2
    -- `Δ(t) = Δ*` and `σ(t) = α (X-k) Δ*` at the current share
    have hΔ : Δpath α lam sbar σ s t = Δstar α (lam * hdr sbar (s t)) (X - k) := by
      have := growth_σstar (G := G) hα hα1 hℓ hy
      unfold growth at this
      unfold Δpath
      rw [hpol t ht]
      linarith
    have hσ : σ t = α * (X - k) * Δpath α lam sbar σ s t := by
      rw [hΔ, hpol t ht]; exact σstar_eq hα hα1 hℓ hy
    have hΔ0 : 0 ≤ Δpath α lam sbar σ s t :=
      mul_nonneg (mul_nonneg hlam.le (hdr_pos hsbar (hsrange t ht).2).le)
        (Real.rpow_nonneg (hσ0 t) _)
    apply max_le
    · unfold Rpath Rinf
      have := hm t
      rw [hσ] at this
      nlinarith
    · exact mul_nonneg hc hΔ0
  obtain ⟨hint, hle, hlt⟩ := budget_core hlam hsbar hT σ s hσ0 hσint hac hsrange hode _
    (excess_aestronglyMeasurable hT σ m s (fun _ => m0) hσm hmm measurable_const hscont)
    (fun t => le_max_right _ _) hc hpt
  refine ⟨hint, hle, ?_⟩
  rw [← set_ge_eq hR σ s m]
  refine time_bound hT _ hint (fun t => le_max_right _ _) hε (hle.trans ?_)
  exact mul_le_mul_of_nonneg_left hlt.le hc

end RuleOfX
