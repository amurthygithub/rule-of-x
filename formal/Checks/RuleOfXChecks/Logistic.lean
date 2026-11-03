import RuleOfX

/-!
# A concrete logistic share path

`Fl v = 0.5 / (1 + 49 e^{-1.2 v})` is the share path induced by constant unit spend with
`λ = 1.2`, `s̄ = 0.5`, `s₀ = 0.01` (so `s̄/s₀ - 1 = 49`). Its derivative is bounded by 30 on
`[0, ∞)`, which makes it Lipschitz, hence absolutely continuous, there. (Audit instances.)
-/

noncomputable section
open Real Set Filter Topology MeasureTheory RuleOfX
open scoped NNReal

namespace RuleOfXChecks

def Dn (v : ℝ) : ℝ := 1 + 49 * Real.exp (-(1.2 * v))
def Fl (v : ℝ) : ℝ := 0.5 / Dn v
def Fl' (v : ℝ) : ℝ :=
  (0 * Dn v - 0.5 * (49 * (Real.exp (-(1.2 * v)) * (-(1.2 * 1))))) / Dn v ^ 2

theorem Dn_pos (v : ℝ) : 0 < Dn v := by
  unfold Dn; have := Real.exp_pos (-(1.2 * v)); linarith

theorem Fl_hasDerivAt (v : ℝ) : HasDerivAt Fl (Fl' v) v := by
  have he : HasDerivAt (fun t : ℝ => Real.exp (-(1.2 * t)))
      (Real.exp (-(1.2 * v)) * (-(1.2 * 1))) v :=
    (((hasDerivAt_id v).const_mul 1.2).neg).exp
  have hd : HasDerivAt Dn (49 * (Real.exp (-(1.2 * v)) * (-(1.2 * 1)))) v :=
    (he.const_mul 49).const_add 1
  exact (hasDerivAt_const v (0.5 : ℝ)).div hd (Dn_pos v).ne'

theorem Fl'_bound {v : ℝ} (hv : 0 ≤ v) : ‖Fl' v‖₊ ≤ (30 : ℝ≥0) := by
  rw [← NNReal.coe_le_coe, coe_nnnorm, Real.norm_eq_abs]
  have he : Real.exp (-(1.2 * v)) ≤ 1 := Real.exp_le_one_iff.2 (by linarith)
  have he0 := Real.exp_pos (-(1.2 * v))
  have hD : 1 ≤ Dn v := by unfold Dn; linarith
  have hval : Fl' v = 29.4 * Real.exp (-(1.2 * v)) / Dn v ^ 2 := by unfold Fl'; ring
  rw [hval, abs_of_nonneg (by positivity)]
  rw [div_le_iff₀ (by positivity)]
  push_cast
  nlinarith

theorem Fl_lipschitz : LipschitzOnWith 30 Fl (Ici 0) :=
  (convex_Ici (0:ℝ)).lipschitzOnWith_of_nnnorm_hasDerivWithin_le
    (fun v _ => (Fl_hasDerivAt v).hasDerivWithinAt) (fun _ hv => Fl'_bound hv)

theorem Fl_range (v : ℝ) : 0 < Fl v ∧ Fl v < 0.5 := by
  unfold Fl
  have hp := Dn_pos v
  have he := Real.exp_pos (-(1.2 * v))
  refine ⟨div_pos (by norm_num) hp, ?_⟩
  rw [div_lt_iff₀ hp]; unfold Dn; nlinarith

theorem Fl_cont : Continuous Fl := by
  unfold Fl Dn
  exact continuous_const.div (by fun_prop) (fun t => (Dn_pos t).ne')

theorem clamp_lipschitz : LipschitzWith 1 (fun t : ℝ => max (t - 1) 0) := by
  refine LipschitzWith.of_dist_le_mul fun x y => ?_
  rw [Real.dist_eq, Real.dist_eq, NNReal.coe_one, one_mul]
  calc |max (x - 1) 0 - max (y - 1) 0| ≤ |(x - 1) - (y - 1)| := abs_max_sub_max_le_abs _ _ _
    _ = |x - y| := by ring_nf

end RuleOfXChecks
