import RuleOfX.Saturation

/-!
# Lemma prop:envelope (Envelope results)

`σ̄ = ∞`, `ℓ = λ h(s)`, and `R*_X = Rst α sbar m0 G k X lam s`
`= m₀ + (X-k) G + C_α [λ h(s) (X-k)_+]^{1/(1-α)}` (the closed form of prop:score, valid for
every `X`, see `Rst_isGreatest`). `g* = gstar G k α ℓ X = G + Δ*` with `Δ* = Δplus α ℓ (X-k)`
(zero when `X ≤ k`), `σ* = σplus α ℓ (X-k)`.
-/

noncomputable section
open Real Set Filter Topology

set_option autoImplicit false

namespace RuleOfX

variable {m0 G k α lam sbar X s : ℝ}

/-! ### Monotonicity of `Δ*` in `y` -/

theorem Δplus_nonneg (hα : 0 < α) {ℓ : ℝ} (hℓ : 0 < ℓ) (y : ℝ) : 0 ≤ Δplus α ℓ y :=
  Δstar_nonneg hα hℓ (le_max_right _ _)

theorem Δplus_monotone (hα : 0 < α) (hα1 : α < 1) {ℓ : ℝ} (hℓ : 0 < ℓ) :
    Monotone (Δplus α ℓ) := by
  intro y y' hyy'
  unfold Δplus Δstar
  have hq : 0 ≤ α / (1 - α) := (div_pos hα (by linarith)).le
  have h1 : α * max y 0 ≤ α * max y' 0 :=
    mul_le_mul_of_nonneg_left (max_le_max hyy' le_rfl) hα.le
  have h2 := Real.rpow_le_rpow (mul_nonneg hα.le (le_max_right _ _)) h1 hq
  exact mul_le_mul_of_nonneg_left h2 (Real.rpow_nonneg hℓ.le _)

theorem Δplus_pos (hα : 0 < α) {ℓ y : ℝ} (hℓ : 0 < ℓ) (hy : 0 < y) : 0 < Δplus α ℓ y := by
  rw [Δplus_of_pos hy.le]; exact Δstar_pos hα hℓ hy

/-- `y Δ*(y) = ℓ^{1/(1-α)} α^{α/(1-α)} (y₊)^{1/(1-α)}` for every `y`. -/
theorem mul_Δplus (hα : 0 < α) (hα1 : α < 1) {ℓ : ℝ} (_hℓ : 0 < ℓ) (y : ℝ) :
    y * Δplus α ℓ y = ℓ ^ (1 / (1 - α)) * α ^ (α / (1 - α)) * max y 0 ^ (1 / (1 - α)) := by
  rcases le_or_gt y 0 with hy | hy
  · rw [Δplus_of_nonpos hα hα1 hy, max_eq_right hy, Real.zero_rpow (q_pos hα1).ne']; ring
  · rw [Δplus_of_pos hy.le, max_eq_left hy.le]
    unfold Δstar
    rw [Real.mul_rpow hα.le hy.le]
    have h2 : y ^ (1 / (1 - α)) = y ^ (α / (1 - α)) * y := by
      rw [show (1 : ℝ) / (1 - α) = α / (1 - α) + 1 by linarith [q_sub_one hα1],
        Real.rpow_add_one hy.ne']
    rw [h2]; ring

/-! ### Partial derivatives (eq:envelope) -/

theorem Rst_def' : Rst α sbar m0 G k X lam s =
    m0 + (X - k) * G + Cα α * (lam * hdr sbar s * max (X - k) 0) ^ (1 / (1 - α)) := rfl

/-- `∂R*/∂m₀ = 1`. -/
theorem hasDerivAt_Rst_m0 : HasDerivAt (fun m0 => Rst α sbar m0 G k X lam s) 1 m0 := by
  unfold Rst
  exact ((hasDerivAt_id' m0).add_const _).add_const _

/-- `∂R*/∂G = X - k`. -/
theorem hasDerivAt_Rst_G : HasDerivAt (fun G => Rst α sbar m0 G k X lam s) (X - k) G := by
  unfold Rst
  refine ((((hasDerivAt_id' G).const_mul (X - k)).const_add m0).add_const _).congr_deriv ?_
  ring

/-- `∂R*/∂k = -g*`. -/
theorem hasDerivAt_Rst_k (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar)
    (hs : s < sbar) :
    HasDerivAt (fun k => Rst α sbar m0 G k X lam s) (-(gstar G k α (lam * hdr sbar s) X)) k := by
  have hℓ := ℓ_pos hlam hsbar hs
  unfold Rst gstar
  have h1 : HasDerivAt (fun k => m0 + (X - k) * G) (-1 * G) k :=
    (((hasDerivAt_id' k).const_sub X).mul_const G).const_add m0
  have h2 := (hasDerivAt_surplus_y hα hα1 hℓ (X - k)).comp k ((hasDerivAt_id' k).const_sub X)
  exact (h1.add h2).congr_deriv (by ring)

/-- `∂R*/∂X = g*`. -/
theorem hasDerivAt_Rst_X (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar)
    (hs : s < sbar) :
    HasDerivAt (fun X => Rst α sbar m0 G k X lam s) (gstar G k α (lam * hdr sbar s) X) X := by
  have hℓ := ℓ_pos hlam hsbar hs
  unfold Rst gstar
  have h1 : HasDerivAt (fun X => m0 + (X - k) * G) (1 * G) X :=
    (((hasDerivAt_id' X).sub_const k).mul_const G).const_add m0
  have h2 := (hasDerivAt_surplus_y hα hα1 hℓ (X - k)).comp X ((hasDerivAt_id' X).sub_const k)
  exact (h1.add h2).congr_deriv (by ring)

/-- `∂R*/∂λ = (X-k)Δ*/λ`. -/
theorem hasDerivAt_Rst_lam (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar)
    (hs : s < sbar) :
    HasDerivAt (fun lam => Rst α sbar m0 G k X lam s)
      ((X - k) * Δplus α (lam * hdr sbar s) (X - k) / lam) lam := by
  have hh := hdr_pos hsbar hs
  rcases le_or_gt X k with hX | hX
  · have hy : X - k ≤ 0 := sub_nonpos.2 hX
    have hf : (fun lam => Rst α sbar m0 G k X lam s) = fun _ => Rinf m0 G k X := by
      funext lam; exact Rst_of_le hα1 hX s
    rw [hf, Δplus_of_nonpos hα hα1 hy, mul_zero, zero_div]
    exact hasDerivAt_const lam _
  · have hy : 0 < X - k := sub_pos.2 hX
    have hu : 0 < lam * hdr sbar s := ℓ_pos hlam hsbar hs
    have hf : (fun lam => Rst α sbar m0 G k X lam s) =
        fun lam => Rinf m0 G k X + Cα α * ((lam * hdr sbar s) * (X - k)) ^ (1 / (1 - α)) := by
      funext lam; exact Rst_of_lt hX s
    rw [hf, Δplus_of_pos hy.le]
    have hin : HasDerivAt (fun lam : ℝ => lam * hdr sbar s) (1 * hdr sbar s) lam :=
      (hasDerivAt_id' lam).mul_const _
    have hcomp := (hasDerivAt_surplus_ℓ hα hα1 hu hy).comp lam hin
    refine ((hasDerivAt_const lam (Rinf m0 G k X)).add hcomp).congr_deriv ?_
    have hh' := hh.ne'
    have hl := hlam.ne'
    field_simp
    ring

/-- `(X-k)Δ*/λ = (X-k) h (σ*)^α`, and this is `≥ 0`, with equality iff `X ≤ k`. -/
theorem Rst_lam_deriv_eq (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar)
    (hs : s < sbar) :
    (X - k) * Δplus α (lam * hdr sbar s) (X - k) / lam =
      (X - k) * hdr sbar s * σplus α (lam * hdr sbar s) (X - k) ^ α ∧
    0 ≤ (X - k) * Δplus α (lam * hdr sbar s) (X - k) / lam ∧
    (0 < (X - k) * Δplus α (lam * hdr sbar s) (X - k) / lam ↔ k < X) := by
  have hh := hdr_pos hsbar hs
  have hℓ := ℓ_pos hlam hsbar hs
  rcases le_or_gt X k with hX | hX
  · have hy : X - k ≤ 0 := sub_nonpos.2 hX
    rw [Δplus_of_nonpos hα hα1 hy, σplus_of_nonpos hα1 hy, Real.zero_rpow hα.ne']
    refine ⟨by ring, by simp, ?_⟩
    simp only [mul_zero, zero_div, lt_self_iff_false, false_iff, not_lt]
    exact hX
  · have hy : 0 < X - k := sub_pos.2 hX
    rw [Δplus_of_pos hy.le, σplus_of_pos hy.le]
    have h1 : lam * hdr sbar s * σstar α (lam * hdr sbar s) (X - k) ^ α =
        Δstar α (lam * hdr sbar s) (X - k) := by
      have := growth_σstar (G := 0) hα hα1 hℓ hy
      unfold growth at this; linarith
    have hpos : 0 < (X - k) * Δstar α (lam * hdr sbar s) (X - k) / lam :=
      div_pos (mul_pos hy (Δstar_pos hα hℓ hy)) hlam
    refine ⟨?_, hpos.le, ⟨fun _ => hX, fun _ => hpos⟩⟩
    rw [← h1]
    have hl := hlam.ne'
    field_simp

/-- Through `m₀ = γ - a` and `γ = 1 - c_h - c_c - f`: `∂R*/∂γ = 1`, `∂R*/∂a = -1`,
`∂R*/∂c_c = -1`. -/
theorem hasDerivAt_Rst_cost (γ a ch cc f : ℝ) :
    HasDerivAt (fun γ => Rst α sbar (γ - a) G k X lam s) 1 γ ∧
    HasDerivAt (fun a => Rst α sbar (γ - a) G k X lam s) (-1) a ∧
    HasDerivAt (fun cc => Rst α sbar (1 - ch - cc - f - a) G k X lam s) (-1) cc := by
  refine ⟨?_, ?_, ?_⟩
  · have := (hasDerivAt_Rst_m0 (α := α) (sbar := sbar) (G := G) (k := k) (X := X) (lam := lam)
      (s := s) (m0 := γ - a)).comp γ ((hasDerivAt_id' γ).sub_const a)
    exact this.congr_deriv (by ring)
  · have := (hasDerivAt_Rst_m0 (α := α) (sbar := sbar) (G := G) (k := k) (X := X) (lam := lam)
      (s := s) (m0 := γ - a)).comp a ((hasDerivAt_id' a).const_sub γ)
    exact this.congr_deriv (by ring)
  · have := (hasDerivAt_Rst_m0 (α := α) (sbar := sbar) (G := G) (k := k) (X := X) (lam := lam)
      (s := s) (m0 := 1 - ch - cc - f - a)).comp cc
      ((((hasDerivAt_id' cc).const_sub (1 - ch)).sub_const f).sub_const a)
    exact this.congr_deriv (by ring)

/-! ### Convexity in `k` and in `λ` -/

/-- `R*_X` is convex in `k`. -/
theorem Rst_convexOn_k (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar)
    (hs : s < sbar) : ConvexOn ℝ univ (fun k => Rst α sbar m0 G k X lam s) := by
  have hℓ := ℓ_pos hlam hsbar hs
  have hd : deriv (fun k => Rst α sbar m0 G k X lam s) =
      fun k => -(gstar G k α (lam * hdr sbar s) X) :=
    funext fun k => (hasDerivAt_Rst_k hα hα1 hlam hsbar hs).deriv
  refine Monotone.convexOn_univ_of_deriv
    (fun k => (hasDerivAt_Rst_k hα hα1 hlam hsbar hs).differentiableAt) ?_
  rw [hd]
  intro k k' hkk'
  unfold gstar
  have := Δplus_monotone hα hα1 hℓ (show X - k' ≤ X - k by linarith)
  linarith

/-- `R*_X` is convex in `λ` on `(0, ∞)` (indeed on `[0, ∞)`). -/
theorem Rst_convexOn_lam (hα : 0 < α) (hα1 : α < 1) (hsbar : 0 < sbar) (hs : s < sbar) :
    ConvexOn ℝ (Ioi 0) (fun lam => Rst α sbar m0 G k X lam s) := by
  have hh := hdr_pos hsbar hs
  have hq : 1 ≤ 1 / (1 - α) := (one_lt_q hα hα1).le
  set c := Cα α * (hdr sbar s * max (X - k) 0) ^ (1 / (1 - α)) with hc
  have hc0 : 0 ≤ c := mul_nonneg (Cα_pos hα hα1).le
    (Real.rpow_nonneg (mul_nonneg hh.le (le_max_right _ _)) _)
  have hconv : ConvexOn ℝ (Ici 0) fun lam : ℝ => Rinf m0 G k X + c * lam ^ (1 / (1 - α)) := by
    have := ((convexOn_rpow hq).smul hc0).add (convexOn_const (Rinf m0 G k X) (convex_Ici 0))
    refine this.congr fun lam _ => ?_
    simp only [Pi.add_apply, smul_eq_mul]; ring
  refine (hconv.subset Ioi_subset_Ici_self (convex_Ioi 0)).congr fun lam hlam => ?_
  rw [Rst_eq, hc]
  have hlam0 : (0 : ℝ) ≤ lam := le_of_lt hlam
  rw [show lam * hdr sbar s * max (X - k) 0 = lam * (hdr sbar s * max (X - k) 0) by ring,
    Real.mul_rpow hlam0 (mul_nonneg hh.le (le_max_right _ _))]
  ring

/-! ### The cross-partial -/

/-- `∂/∂λ (∂R*/∂k) = -Δ*/[(1-α)λ]` (with `∂R*/∂k = -g*`). -/
theorem hasDerivAt_cross_lam (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar)
    (hs : s < sbar) :
    HasDerivAt (fun lam => -(gstar G k α (lam * hdr sbar s) X))
      (-(Δplus α (lam * hdr sbar s) (X - k) / ((1 - α) * lam))) lam := by
  have hh := hdr_pos hsbar hs
  have hu := ℓ_pos hlam hsbar hs
  rcases le_or_gt X k with hX | hX
  · have hy : X - k ≤ 0 := sub_nonpos.2 hX
    have hf : (fun lam => -(gstar G k α (lam * hdr sbar s) X)) = fun _ => -G := by
      funext lam; rw [gstar_of_le hα hα1 hX]
    rw [hf, Δplus_of_nonpos hα hα1 hy, zero_div, neg_zero]
    exact hasDerivAt_const lam _
  · have hy : 0 < X - k := sub_pos.2 hX
    have hf : (fun lam => -(gstar G k α (lam * hdr sbar s) X)) =
        fun lam => -(G + Δstar α (lam * hdr sbar s) (X - k)) := by
      funext lam; rw [gstar_of_lt hX]
    rw [hf, Δplus_of_pos hy.le]
    have hin : HasDerivAt (fun lam : ℝ => lam * hdr sbar s) (1 * hdr sbar s) lam :=
      (hasDerivAt_id' lam).mul_const _
    have hcomp := (hasDerivAt_Δstar_ℓ hα hα1 hu hy).comp lam hin
    refine ((hasDerivAt_const lam G).add hcomp).neg.congr_deriv ?_
    have hh' := hh.ne'
    have hl := hlam.ne'
    have h1α : (1 - α) ≠ 0 := by linarith
    field_simp
    ring

/-- `∂/∂k (∂R*/∂λ) = -Δ*/[(1-α)λ]` (with `∂R*/∂λ = (X-k)Δ*/λ`): the mixed partial in the other
order has the same value. -/
theorem hasDerivAt_cross_k (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar)
    (hs : s < sbar) :
    HasDerivAt (fun k => (X - k) * Δplus α (lam * hdr sbar s) (X - k) / lam)
      (-(Δplus α (lam * hdr sbar s) (X - k) / ((1 - α) * lam))) k := by
  have hℓ := ℓ_pos hlam hsbar hs
  have hq := one_lt_q hα hα1
  set ℓ := lam * hdr sbar s with hℓdef
  have hf : (fun k => (X - k) * Δplus α ℓ (X - k) / lam) =
      fun k => (ℓ ^ (1 / (1 - α)) * α ^ (α / (1 - α)) / lam) * max (X - k) 0 ^ (1 / (1 - α)) := by
    funext k; rw [mul_Δplus hα hα1 hℓ]; ring
  rw [hf]
  have h1 := ((hasDerivAt_fplus hq (X - k)).comp k ((hasDerivAt_id' k).const_sub X)).const_mul
    (ℓ ^ (1 / (1 - α)) * α ^ (α / (1 - α)) / lam)
  refine h1.congr_deriv ?_
  unfold Δplus Δstar
  rw [Real.mul_rpow hα.le (le_max_right _ _), q_sub_one hα1]
  have hl := hlam.ne'
  have h1α : (1 - α) ≠ 0 := by linarith
  field_simp

theorem cross_nonpos (hα : 0 < α) (hlam : 0 < lam) (hsbar : 0 < sbar) (hs : s < sbar)
    (hα1 : α < 1) :
    -(Δplus α (lam * hdr sbar s) (X - k) / ((1 - α) * lam)) ≤ 0 := by
  have := Δplus_nonneg hα (ℓ_pos hlam hsbar hs) (X - k)
  have h1 : 0 < (1 - α) * lam := mul_pos (by linarith) hlam
  have := div_nonneg this h1.le
  linarith

/-! ### Joint continuous differentiability -/

/-- The parameter tuple `(m₀, G, k, X, λ, s)`. -/
abbrev Params := ℝ × ℝ × ℝ × ℝ × ℝ × ℝ

/-- `R*_X` as a function of the parameter tuple. -/
def RstP (α sbar : ℝ) (p : Params) : ℝ :=
  Rst α sbar p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2

/-- The parameter domain `λ > 0`, `s < s̄` (open). -/
def Dom (sbar : ℝ) : Set Params := {p | 0 < p.2.2.2.2.1 ∧ p.2.2.2.2.2 < sbar}

theorem isOpen_Dom (sbar : ℝ) : IsOpen (Dom sbar) := by
  unfold Dom
  have h1 : IsOpen {p : Params | 0 < p.2.2.2.2.1} :=
    isOpen_lt continuous_const (by fun_prop)
  have h2 : IsOpen {p : Params | p.2.2.2.2.2 < sbar} :=
    isOpen_lt (by fun_prop) continuous_const
  exact h1.inter h2

/-- `R*_X` is continuously differentiable in `(m₀, G, k, X, λ, s)` jointly, on the domain
`λ > 0`, `s < s̄` (including across `X = k`). -/
theorem contDiffOn_RstP (hα : 0 < α) (hα1 : α < 1) (hsbar : 0 < sbar) :
    ContDiffOn ℝ 1 (RstP α sbar) (Dom sbar) := by
  have hq := one_lt_q hα hα1
  have hA : ContDiff ℝ 1 (fun p : Params => p.1 + (p.2.2.2.1 - p.2.2.1) * p.2.1) := by fun_prop
  have hB0 : ContDiff ℝ 1 (fun p : Params => p.2.2.2.2.1 * hdr sbar p.2.2.2.2.2) := by
    unfold hdr; fun_prop
  have hB : ContDiffOn ℝ 1 (fun p : Params => (p.2.2.2.2.1 * hdr sbar p.2.2.2.2.2) ^ (1 / (1 - α)))
      (Dom sbar) := by
    refine ContDiffOn.rpow_const_of_ne hB0.contDiffOn ?_
    intro p hp
    exact (ℓ_pos hp.1 hsbar hp.2).ne'
  have hC : ContDiff ℝ 1 (fun p : Params => max (p.2.2.2.1 - p.2.2.1) 0 ^ (1 / (1 - α))) :=
    (contDiff_fplus hq).comp (by fun_prop : ContDiff ℝ 1 (fun p : Params => p.2.2.2.1 - p.2.2.1))
  have hF : ContDiffOn ℝ 1 (fun p : Params => p.1 + (p.2.2.2.1 - p.2.2.1) * p.2.1 +
      Cα α * (p.2.2.2.2.1 * hdr sbar p.2.2.2.2.2) ^ (1 / (1 - α)) *
        max (p.2.2.2.1 - p.2.2.1) 0 ^ (1 / (1 - α))) (Dom sbar) :=
    hA.contDiffOn.add ((contDiff_const.contDiffOn.mul hB).mul hC.contDiffOn)
  refine hF.congr fun p hp => ?_
  unfold RstP Rst
  rw [Real.mul_rpow (ℓ_pos hp.1 hsbar hp.2).le (le_max_right _ _)]
  ring

/-- **Lemma prop:envelope.** "Let `σ̄ = ∞` and `X ≥ 0`. The maximal score `R*_X` is continuously
differentiable in `(m₀, G, k, X, λ, s)`, with `∂R*/∂m₀ = 1`, `∂R*/∂G = X - k`, `∂R*/∂k = -g*`,
`∂R*/∂X = g*`, `∂R*/∂λ = (X-k)Δ*/λ = (X-k) h (σ*)^α ≥ 0`, where the last inequality is strict
iff `X > k`. Through `m₀ = γ - a` and `γ = 1 - c_h - c_c - f`, `∂R*/∂γ = 1` and
`∂R*/∂a = ∂R*/∂c_c = -1`. Moreover `R*_X` is convex in `k` and in `λ`, and
`∂²R*/∂k∂λ = -Δ*/[(1-α)λ] ≤ 0`."
(Domain: `λ > 0`, `0 < s < s̄`; `X ≥ 0` is not needed. Joint `C¹` is `ContDiffOn ℝ 1` on the open
set `Dom sbar`; the cross-partial is proved in both orders.) -/
theorem prop_envelope (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar)
    (hs : s < sbar) (γ a ch cc f : ℝ) :
    ContDiffOn ℝ 1 (RstP α sbar) (Dom sbar) ∧
    HasDerivAt (fun m0 => Rst α sbar m0 G k X lam s) 1 m0 ∧
    HasDerivAt (fun G => Rst α sbar m0 G k X lam s) (X - k) G ∧
    HasDerivAt (fun k => Rst α sbar m0 G k X lam s) (-(gstar G k α (lam * hdr sbar s) X)) k ∧
    HasDerivAt (fun X => Rst α sbar m0 G k X lam s) (gstar G k α (lam * hdr sbar s) X) X ∧
    HasDerivAt (fun lam => Rst α sbar m0 G k X lam s)
      ((X - k) * Δplus α (lam * hdr sbar s) (X - k) / lam) lam ∧
    ((X - k) * Δplus α (lam * hdr sbar s) (X - k) / lam =
      (X - k) * hdr sbar s * σplus α (lam * hdr sbar s) (X - k) ^ α ∧
      0 ≤ (X - k) * Δplus α (lam * hdr sbar s) (X - k) / lam ∧
      (0 < (X - k) * Δplus α (lam * hdr sbar s) (X - k) / lam ↔ k < X)) ∧
    (HasDerivAt (fun γ => Rst α sbar (γ - a) G k X lam s) 1 γ ∧
      HasDerivAt (fun a => Rst α sbar (γ - a) G k X lam s) (-1) a ∧
      HasDerivAt (fun cc => Rst α sbar (1 - ch - cc - f - a) G k X lam s) (-1) cc) ∧
    ConvexOn ℝ univ (fun k => Rst α sbar m0 G k X lam s) ∧
    ConvexOn ℝ (Ioi 0) (fun lam => Rst α sbar m0 G k X lam s) ∧
    HasDerivAt (fun lam => -(gstar G k α (lam * hdr sbar s) X))
      (-(Δplus α (lam * hdr sbar s) (X - k) / ((1 - α) * lam))) lam ∧
    HasDerivAt (fun k => (X - k) * Δplus α (lam * hdr sbar s) (X - k) / lam)
      (-(Δplus α (lam * hdr sbar s) (X - k) / ((1 - α) * lam))) k ∧
    -(Δplus α (lam * hdr sbar s) (X - k) / ((1 - α) * lam)) ≤ 0 :=
  ⟨contDiffOn_RstP hα hα1 hsbar, hasDerivAt_Rst_m0, hasDerivAt_Rst_G,
    hasDerivAt_Rst_k hα hα1 hlam hsbar hs, hasDerivAt_Rst_X hα hα1 hlam hsbar hs,
    hasDerivAt_Rst_lam hα hα1 hlam hsbar hs, Rst_lam_deriv_eq hα hα1 hlam hsbar hs,
    hasDerivAt_Rst_cost γ a ch cc f, Rst_convexOn_k hα hα1 hlam hsbar hs,
    Rst_convexOn_lam hα hα1 hsbar hs, hasDerivAt_cross_lam hα hα1 hlam hsbar hs,
    hasDerivAt_cross_k hα hα1 hlam hsbar hs, cross_nonpos hα hlam hsbar hs hα1⟩

end RuleOfX
