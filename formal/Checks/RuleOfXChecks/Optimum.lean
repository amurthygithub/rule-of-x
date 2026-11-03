import RuleOfX
import Mathlib.Analysis.Calculus.InverseFunctionTheorem.Deriv
import Mathlib.Analysis.Calculus.Deriv.Inverse

/-!
# Non-vacuity of `cor_transient_b_optimum` with `T > 0`

(Audit instance.) Parameters: α = 0.5, λ = 1.2, s̄ = 0.5, X = 1, k = 0 (y = 1), G = 0.2, m₀ = 0.6, s₀ = 0.1.
Under the static-optimum policy σ(t) = σ*(λ h(s(t)), 1) = (0.6 (1 - 2 s))^2 the share ODE is
ṡ = 0.72 s (1 - 2 s)^2 =: v(s). Its time map τ(s) = (ln s - ln(1 - 2 s) + 1/(1 - 2 s))/0.72 has
τ' = 1/v, so s(t) = τ⁻¹(τ(s₀) + t). The inverse is taken from Mathlib's 1-D inverse function
theorem (an `OpenPartialHomeomorph` around s₀); `T` is chosen small enough to stay in its target
and in [0.05, 0.15]. (Mathlib's ODE existence theorems are not used, to keep the set of
compiled Mathlib modules unchanged.) -/


noncomputable section
open Real Set Filter Topology MeasureTheory Metric RuleOfX
open scoped NNReal

namespace RuleOfXChecks

def vf (x : ℝ) : ℝ := 0.72 * x * (1 - 2 * x) ^ 2

theorem hdr_half (x : ℝ) : hdr 0.5 x = 1 - 2 * x := by unfold hdr; ring
def τf (x : ℝ) : ℝ := (Real.log x - Real.log (1 - 2 * x) + (1 - 2 * x)⁻¹) / 0.72
def τf' (x : ℝ) : ℝ := (vf x)⁻¹

theorem vf_pos {x : ℝ} (h0 : 0 < x) (h1 : x < 0.5) : 0 < vf x := by
  unfold vf; have : 0 < 1 - 2 * x := by linarith
  positivity

theorem τf_hasDerivAt {x : ℝ} (h0 : 0 < x) (h1 : x < 0.5) : HasDerivAt τf (τf' x) x := by
  have hu : 0 < 1 - 2 * x := by linarith
  have hlin : HasDerivAt (fun x : ℝ => 1 - 2 * x) (0 - 2 * 1) x :=
    (hasDerivAt_const x 1).sub ((hasDerivAt_id' x).const_mul 2)
  have h := (((Real.hasDerivAt_log h0.ne').sub (hlin.log hu.ne')).add (hlin.inv hu.ne')).div_const
    (0.72 : ℝ)
  refine h.congr_deriv ?_
  have hx : x ≠ 0 := h0.ne'
  have hu' : 1 - 2 * x ≠ 0 := hu.ne'
  unfold τf' vf
  generalize hu0 : 1 - 2 * x = u at hu' ⊢
  field_simp
  subst hu0
  ring

theorem τf'_cont {x : ℝ} (h0 : 0 < x) (h1 : x < 0.5) : ContinuousAt τf' x := by
  unfold τf'
  exact ((by unfold vf; fun_prop : Continuous vf).continuousAt).inv₀ (vf_pos h0 h1).ne'

theorem τf_strict : HasStrictDerivAt τf (τf' 0.1) 0.1 := by
  refine hasStrictDerivAt_of_hasDerivAt_of_continuousAt ?_ (τf'_cont (by norm_num) (by norm_num))
  filter_upwards [Ioo_mem_nhds (show (0:ℝ) < 0.1 by norm_num) (show (0.1:ℝ) < 0.5 by norm_num)]
    with y hy
  exact τf_hasDerivAt hy.1 hy.2

theorem τf'_ne : τf' 0.1 ≠ 0 := by
  unfold τf'; exact inv_ne_zero (vf_pos (by norm_num) (by norm_num)).ne'

/-- the local homeomorphism given by the inverse function theorem -/
def eH : OpenPartialHomeomorph ℝ ℝ :=
  (τf_strict.hasStrictFDerivAt_equiv τf'_ne).toOpenPartialHomeomorph τf

theorem eH_coe : (eH : ℝ → ℝ) = τf := rfl
theorem src : (0.1:ℝ) ∈ eH.source :=
  (τf_strict.hasStrictFDerivAt_equiv τf'_ne).mem_toOpenPartialHomeomorph_source
theorem tgt : τf 0.1 ∈ eH.target :=
  (τf_strict.hasStrictFDerivAt_equiv τf'_ne).image_mem_toOpenPartialHomeomorph_target
theorem symm_y0 : eH.symm (τf 0.1) = 0.1 := eH.left_inv src

/-- a radius around `y₀ = τ(0.1)` inside the target on which `τ⁻¹` stays in (0.05, 0.15) -/
theorem exists_eps : ∃ ε > 0, ∀ y, dist y (τf 0.1) < ε →
    y ∈ eH.target ∧ dist (eH.symm y) 0.1 < 0.05 := by
  obtain ⟨ε₁, hε₁, hball⟩ := Metric.isOpen_iff.1 eH.open_target _ tgt
  have hc := Metric.continuousAt_iff.1 (eH.continuousAt_symm tgt) 0.05 (by norm_num)
  obtain ⟨δ, hδ, hcont⟩ := hc
  refine ⟨min ε₁ δ, lt_min hε₁ hδ, fun y hy => ⟨hball (lt_of_lt_of_le hy (min_le_left _ _)), ?_⟩⟩
  have := hcont (lt_of_lt_of_le hy (min_le_right _ _))
  rwa [symm_y0] at this

def εH : ℝ := Classical.choose exists_eps
theorem εH_pos : 0 < εH := (Classical.choose_spec exists_eps).1
theorem εH_spec : ∀ y, dist y (τf 0.1) < εH → y ∈ eH.target ∧ dist (eH.symm y) 0.1 < 0.05 :=
  (Classical.choose_spec exists_eps).2

def TT : ℝ := εH / 2
theorem TT_pos : 0 < TT := by unfold TT; linarith [εH_pos]

def sO (t : ℝ) : ℝ := eH.symm (τf 0.1 + projIcc 0 TT TT_pos.le t)

theorem in_spec {t : ℝ} (ht : t ∈ Icc 0 TT) :
    τf 0.1 + t ∈ eH.target ∧ eH.symm (τf 0.1 + t) ∈ Ioo (0.05:ℝ) 0.15 := by
  have hd : dist (τf 0.1 + t) (τf 0.1) < εH := by
    rw [Real.dist_eq, add_sub_cancel_left, abs_of_nonneg ht.1]
    have := ht.2; unfold TT at this; linarith [εH_pos]
  obtain ⟨h1, h2⟩ := εH_spec _ hd
  rw [Real.dist_eq, abs_lt] at h2
  exact ⟨h1, ⟨by linarith [h2.1], by linarith [h2.2]⟩⟩

theorem sO_eq {t : ℝ} (ht : t ∈ Icc 0 TT) : sO t = eH.symm (τf 0.1 + t) := by
  unfold sO; rw [projIcc_of_mem _ ht]

theorem sO_range (t : ℝ) : sO t ∈ Ioo (0.05:ℝ) 0.15 := by
  have h := (projIcc 0 TT TT_pos.le t).2
  unfold sO; exact (in_spec h).2

theorem sO_cont : Continuous sO := by
  have : sO = eH.symm ∘ (fun t => τf 0.1 + (projIcc 0 TT TT_pos.le t : ℝ)) := rfl
  rw [this]
  exact eH.continuousOn_symm.comp_continuous
    (continuous_const.add (continuous_subtype_val.comp continuous_projIcc))
    (fun t => (in_spec (projIcc 0 TT TT_pos.le t).2).1)

/-- the inverse of the time map solves `ṡ = v(s)` -/
theorem symm_deriv {t : ℝ} (ht : t ∈ Icc 0 TT) :
    HasDerivAt (fun t => eH.symm (τf 0.1 + t)) (vf (eH.symm (τf 0.1 + t))) t := by
  obtain ⟨htg, hr⟩ := in_spec ht
  have hx0 : 0 < eH.symm (τf 0.1 + t) := by linarith [hr.1]
  have hx1 : eH.symm (τf 0.1 + t) < 0.5 := by linarith [hr.2]
  have hd : HasDerivAt eH (τf' (eH.symm (τf 0.1 + t))) (eH.symm (τf 0.1 + t)) := by
    rw [eH_coe]; exact τf_hasDerivAt hx0 hx1
  have hne : τf' (eH.symm (τf 0.1 + t)) ≠ 0 := by
    unfold τf'; exact inv_ne_zero (vf_pos hx0 hx1).ne'
  have hs := eH.hasDerivAt_symm htg hne hd
  have hc := hs.comp t ((hasDerivAt_id' t).const_add (τf 0.1))
  refine hc.congr_deriv ?_
  unfold τf'; rw [inv_inv, mul_one]

theorem sO_derivWithin : ∀ t ∈ Icc 0 TT, HasDerivWithinAt sO (vf (sO t)) (Icc 0 TT) t := by
  intro t ht
  rw [sO_eq ht]
  exact (symm_deriv ht).hasDerivWithinAt.congr (fun u hu => sO_eq hu) (sO_eq ht)

theorem vf_bound (x : ℝ) (hx : x ∈ Ioo (0.05:ℝ) 0.15) : ‖vf x‖ ≤ 1 := by
  unfold vf
  rw [Real.norm_eq_abs, abs_of_nonneg (by have := hx.1; have : 0 ≤ 1 - 2 * x := by linarith [hx.2]
                                          positivity)]
  nlinarith [hx.1, hx.2, sq_nonneg (1 - 2 * x)]

theorem sO_ac : AbsolutelyContinuousOnInterval sO 0 TT := by
  have hL : LipschitzOnWith 1 sO (Icc 0 TT) :=
    (convex_Icc (0:ℝ) TT).lipschitzOnWith_of_nnnorm_hasDerivWithin_le
      (f' := fun t => vf (sO t)) sO_derivWithin (fun t _ => by
        rw [← NNReal.coe_le_coe, coe_nnnorm, NNReal.coe_one]
        exact vf_bound _ (sO_range t))
  rw [← uIcc_of_le TT_pos.le] at hL
  exact hL.absolutelyContinuousOnInterval

/-- the static-optimum policy at the current share -/
def σO (t : ℝ) : ℝ := σstar 0.5 (1.2 * hdr 0.5 (sO t)) (1 - 0)

theorem σO_pow (t : ℝ) : σO t ^ (0.5:ℝ) = 0.6 * (1 - 2 * sO t) := by
  have hr := sO_range t
  have hb : 0 ≤ 0.5 * (1.2 * hdr 0.5 (sO t)) * (1 - 0) := by
    rw [hdr_half]; nlinarith [hr.2]
  unfold σO σstar
  rw [← Real.rpow_mul hb, show (1:ℝ) / (1 - 0.5) * 0.5 = 1 by norm_num, Real.rpow_one, hdr_half]
  ring

theorem vf_eq (t : ℝ) : vf (sO t) = sO t * Δpath 0.5 1.2 0.5 σO sO t := by
  unfold vf Δpath; rw [σO_pow, hdr_half]; ring

theorem sO_hode :
    ∀ᵐ t, t ∈ Icc (0:ℝ) TT → HasDerivAt sO (sO t * Δpath 0.5 1.2 0.5 σO sO t) t := by
  have hnull : ∀ᵐ t ∂(volume : Measure ℝ), t ∉ ({0, TT} : Set ℝ) :=
    (Set.toFinite _).countable.ae_notMem volume
  filter_upwards [hnull] with t ht hI
  simp only [mem_insert_iff, mem_singleton_iff, not_or] at ht
  have hIoo : t ∈ Ioo (0:ℝ) TT := ⟨lt_of_le_of_ne hI.1 (Ne.symm ht.1), lt_of_le_of_ne hI.2 ht.2⟩
  rw [← vf_eq]
  exact (sO_derivWithin t hI).hasDerivAt (Icc_mem_nhds hIoo.1 hIoo.2)

theorem σO_cont : Continuous σO := by
  unfold σO σstar hdr
  refine Continuous.rpow_const ?_ (fun _ => Or.inr (by norm_num))
  have := sO_cont
  fun_prop

theorem σO_nonneg (t : ℝ) : 0 ≤ σO t := by
  unfold σO σstar
  exact Real.rpow_nonneg (by rw [hdr_half]; nlinarith [(sO_range t).2]) _

def mO (t : ℝ) : ℝ := 0.6 - σO t - 0 * (0.2 + Δpath 0.5 1.2 0.5 σO sO t)

theorem mO_meas : Measurable mO := by
  have hΔ : Measurable (Δpath 0.5 1.2 0.5 σO sO) := by
    unfold Δpath
    exact (measurable_const.mul (hdr_continuous.measurable.comp sO_cont.measurable)).mul
      (σO_cont.measurable.pow_const _)
  unfold mO
  exact (measurable_const.sub σO_cont.measurable).sub (measurable_const.mul (measurable_const.add hΔ))

theorem σO_int : IntervalIntegrable (fun t => σO t ^ (0.5:ℝ)) volume 0 TT :=
  (σO_cont.rpow_const (fun _ => Or.inr (by norm_num))).intervalIntegrable _ _

/-- `cor_transient_b_optimum` applied on [0, TT], TT > 0, along the static-optimum path. -/
example := cor_transient_b_optimum (m0 := 0.6) (G := 0.2) (k := 0) (X := 1) (α := 0.5)
  (lam := 1.2) (sbar := 0.5) (T := TT) (Rbar := 0.85) (by norm_num) (by norm_num) (by norm_num)
  (by norm_num) (by norm_num) (by unfold Rinf; norm_num) TT_pos.le
  σO mO sO σO_cont.measurable σO_nonneg σO_int mO_meas sO_ac
  (fun t _ => ⟨by linarith [(sO_range t).1], by linarith [(sO_range t).2]⟩) sO_hode
  (fun t => le_refl _) (fun t _ => rfl)

/-- non-triviality: positive horizon, positive spend, positive excess growth -/
example : 0 < TT ∧ 0 < σO 0 ∧ 0 < Δpath 0.5 1.2 0.5 σO sO 0 := by
  have hr := sO_range 0
  refine ⟨TT_pos, ?_, ?_⟩
  · unfold σO σstar
    exact Real.rpow_pos_of_pos (by rw [hdr_half]; nlinarith [hr.2]) _
  · unfold Δpath; rw [σO_pow, hdr_half]
    have : 0 < 1 - 2 * sO 0 := by linarith [hr.2]
    nlinarith
end RuleOfXChecks
