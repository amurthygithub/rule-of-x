import RuleOfX.Score

/-!
# Lemma prop:saturation (Saturation and the small-base bound)

`σ̄ = ∞`, `ℓ = λ h(s)` with `h(s) = 1 - s/s̄` (`hdr sbar s`), `y₊ = max (X - k) 0`,
`R_∞ = m₀ + (X-k) G` (`Rinf`), and `R*_X(s)` is `Rst α sbar m0 G k X lam s`.
-/

noncomputable section
open Real Set Filter Topology

set_option autoImplicit false

namespace RuleOfX

variable {m0 G k α lam sbar X : ℝ}

/-! ### Headroom -/

theorem hdr_pos (hsbar : 0 < sbar) {s : ℝ} (hs : s < sbar) : 0 < hdr sbar s := by
  unfold hdr; rw [sub_pos, div_lt_one hsbar]; exact hs

theorem hdr_nonneg (hsbar : 0 < sbar) {s : ℝ} (hs : s ≤ sbar) : 0 ≤ hdr sbar s := by
  unfold hdr; rw [sub_nonneg, div_le_one hsbar]; exact hs

theorem hdr_lt_one (hsbar : 0 < sbar) {s : ℝ} (hs : 0 < s) : hdr sbar s < 1 := by
  unfold hdr; have := div_pos hs hsbar; linarith

theorem hdr_strictAnti (hsbar : 0 < sbar) : StrictAnti (hdr sbar) := by
  intro a b hab
  have : 0 < (b - a) / sbar := div_pos (sub_pos.2 hab) hsbar
  rw [sub_div] at this
  unfold hdr; linarith

theorem hdr_self (hsbar : 0 < sbar) : hdr sbar sbar = 0 := by
  unfold hdr; rw [div_self hsbar.ne', sub_self]

theorem hdr_zero : hdr sbar 0 = 1 := by
  unfold hdr; rw [zero_div, sub_zero]

theorem hdr_continuous : Continuous (hdr sbar) :=
  continuous_const.sub (continuous_id.div_const sbar)

theorem sbar_sub_eq (hsbar : sbar ≠ 0) (s : ℝ) : sbar - s = sbar * hdr sbar s := by
  unfold hdr
  field_simp

theorem ℓ_pos (hlam : 0 < lam) (hsbar : 0 < sbar) {s : ℝ} (hs : s < sbar) :
    0 < lam * hdr sbar s := mul_pos hlam (hdr_pos hsbar hs)

/-! ### Calculus of the growth surplus -/

/-- The derivative of `(max y 0)^q` for `q > 1`: `q (max y 0)^{q-1}`, including at `y = 0`. -/
theorem hasDerivAt_fplus {q : ℝ} (hq : 1 < q) (y : ℝ) :
    HasDerivAt (fun y : ℝ => max y 0 ^ q) (q * max y 0 ^ (q - 1)) y := by
  have hq' : q - 1 ≠ 0 := sub_ne_zero.2 hq.ne'
  rcases lt_trichotomy y 0 with hy | rfl | hy
  · have hev : (fun y : ℝ => max y 0 ^ q) =ᶠ[𝓝 y] fun _ => (0 : ℝ) ^ q := by
      filter_upwards [Iio_mem_nhds hy] with z hz
      rw [max_eq_right (le_of_lt hz)]
    rw [max_eq_right hy.le, Real.zero_rpow hq', mul_zero]
    exact (hasDerivAt_const y ((0 : ℝ) ^ q)).congr_of_eventuallyEq hev
  · rw [max_self, Real.zero_rpow hq', mul_zero]
    have hR : HasDerivWithinAt (fun y : ℝ => max y 0 ^ q) 0 (Ici 0) 0 := by
      have := (Real.hasDerivAt_rpow_const (x := (0 : ℝ)) (p := q) (Or.inr hq.le)).hasDerivWithinAt
        (s := Ici 0)
      rw [Real.zero_rpow hq', mul_zero] at this
      refine this.congr (fun z hz => ?_) ?_
      · rw [max_eq_left (show (0 : ℝ) ≤ z from hz)]
      · rw [max_self]
    have hL : HasDerivWithinAt (fun y : ℝ => max y 0 ^ q) 0 (Iic 0) 0 := by
      refine (hasDerivWithinAt_const (0 : ℝ) (Iic 0) ((0 : ℝ) ^ q)).congr (fun z hz => ?_) ?_
      · rw [max_eq_right (show z ≤ (0 : ℝ) from hz)]
      · rw [max_self]
    have := hL.union hR
    rwa [Set.Iic_union_Ici, hasDerivWithinAt_univ] at this
  · have hev : (fun y : ℝ => max y 0 ^ q) =ᶠ[𝓝 y] fun y => y ^ q := by
      filter_upwards [Ioi_mem_nhds hy] with z hz
      rw [max_eq_left (le_of_lt hz)]
    rw [max_eq_left hy.le]
    exact (Real.hasDerivAt_rpow_const (Or.inr hq.le)).congr_of_eventuallyEq hev

theorem deriv_fplus {q : ℝ} (hq : 1 < q) :
    deriv (fun y : ℝ => max y 0 ^ q) = fun y => q * max y 0 ^ (q - 1) :=
  funext fun y => (hasDerivAt_fplus hq y).deriv

theorem continuous_deriv_fplus {q : ℝ} (hq : 1 < q) :
    Continuous (fun y : ℝ => q * max y 0 ^ (q - 1)) :=
  continuous_const.mul ((continuous_id.max continuous_const).rpow_const
    fun _ => Or.inr (by linarith))

/-- `y ↦ (y₊)^q` is continuously differentiable for `q > 1`. -/
theorem contDiff_fplus {q : ℝ} (hq : 1 < q) : ContDiff ℝ 1 (fun y : ℝ => max y 0 ^ q) := by
  rw [contDiff_one_iff_deriv]
  refine ⟨fun y => (hasDerivAt_fplus hq y).differentiableAt, ?_⟩
  rw [deriv_fplus hq]
  exact continuous_deriv_fplus hq

/-- `∂Π/∂y = Δ*` (with `Δ* = 0` for `y ≤ 0`), for `Π = C_α (ℓ y₊)^{1/(1-α)}`. -/
theorem hasDerivAt_surplus_y (hα : 0 < α) (hα1 : α < 1) {ℓ : ℝ} (hℓ : 0 < ℓ) (y : ℝ) :
    HasDerivAt (fun y => Cα α * (ℓ * max y 0) ^ (1 / (1 - α))) (Δplus α ℓ y) y := by
  have hq := one_lt_q hα hα1
  have hf : (fun y => Cα α * (ℓ * max y 0) ^ (1 / (1 - α))) =
      fun y => (Cα α * ℓ ^ (1 / (1 - α))) * max y 0 ^ (1 / (1 - α)) := by
    funext y; rw [Real.mul_rpow hℓ.le (le_max_right _ _)]; ring
  rw [hf]
  refine ((hasDerivAt_fplus hq y).const_mul _).congr_deriv ?_
  unfold Δplus Δstar
  rw [Real.mul_rpow hα.le (le_max_right _ _), q_sub_one hα1]
  have hC := Cα_mul_q (α := α) hα1
  calc Cα α * ℓ ^ (1 / (1 - α)) * (1 / (1 - α) * max y 0 ^ (α / (1 - α)))
      = (Cα α * (1 / (1 - α))) * (ℓ ^ (1 / (1 - α)) * max y 0 ^ (α / (1 - α))) := by ring
    _ = _ := by rw [hC]; ring

/-- `∂Π/∂ℓ = y Δ*/ℓ` for `y > 0`, `ℓ > 0`. -/
theorem hasDerivAt_surplus_ℓ (hα : 0 < α) (hα1 : α < 1) {u y : ℝ} (hu : 0 < u) (hy : 0 < y) :
    HasDerivAt (fun u => Cα α * (u * y) ^ (1 / (1 - α))) (y * Δstar α u y / u) u := by
  have h1 : HasDerivAt (fun u : ℝ => u * y) (1 * y) u := (hasDerivAt_id' u).mul_const y
  have h2 := (h1.rpow_const (p := 1 / (1 - α)) (Or.inl (mul_pos hu hy).ne')).const_mul (Cα α)
  refine h2.congr_deriv ?_
  unfold Δstar Cα
  rw [q_sub_one hα1, Real.mul_rpow hu.le hy.le, Real.mul_rpow hα.le hy.le]
  have hu' : u ^ (1 / (1 - α)) = u ^ (α / (1 - α)) * u := by
    rw [show (1 : ℝ) / (1 - α) = α / (1 - α) + 1 by linarith [q_sub_one hα1],
      Real.rpow_add_one hu.ne']
  rw [hu']
  have h1α : (1 - α) ≠ 0 := by linarith
  have hu0 : u ≠ 0 := hu.ne'
  field_simp

/-- `Δ*` as a function of `ℓ`: `∂Δ*/∂ℓ = Δ*/((1-α) ℓ)`, for `y > 0`. -/
theorem hasDerivAt_Δstar_ℓ (hα : 0 < α) (hα1 : α < 1) {u y : ℝ} (hu : 0 < u) (hy : 0 < y) :
    HasDerivAt (fun u => Δstar α u y) (Δstar α u y / ((1 - α) * u)) u := by
  have h1 : HasDerivAt (fun u : ℝ => u ^ (1 / (1 - α))) (1 / (1 - α) * u ^ (1 / (1 - α) - 1)) u :=
    Real.hasDerivAt_rpow_const (Or.inl hu.ne')
  have h2 := h1.mul_const ((α * y) ^ (α / (1 - α)))
  unfold Δstar
  refine h2.congr_deriv ?_
  rw [Real.rpow_sub_one hu.ne']
  have h1α : (1 - α) ≠ 0 := by linarith
  have hu0 : u ≠ 0 := hu.ne'
  field_simp

/-! ### The maximal score as a function of share -/

theorem Rst_eq (s : ℝ) : Rst α sbar m0 G k X lam s =
    Rinf m0 G k X + Cα α * (lam * hdr sbar s * max (X - k) 0) ^ (1 / (1 - α)) := rfl

theorem Rst_of_le (hα1 : α < 1) (hX : X ≤ k) (s : ℝ) : Rst α sbar m0 G k X lam s = Rinf m0 G k X := by
  rw [Rst_eq, max_eq_right (sub_nonpos.2 hX), mul_zero, Real.zero_rpow (q_pos hα1).ne', mul_zero,
    add_zero]

theorem Rst_of_lt (hX : k < X) (s : ℝ) : Rst α sbar m0 G k X lam s =
    Rinf m0 G k X + Cα α * (lam * hdr sbar s * (X - k)) ^ (1 / (1 - α)) := by
  rw [Rst_eq, max_eq_left (sub_pos.2 hX).le]

theorem Rst_continuous (hα1 : α < 1) : Continuous (Rst α sbar m0 G k X lam) := by
  unfold Rst
  refine continuous_const.add (continuous_const.mul ?_)
  refine Continuous.rpow_const ?_ fun _ => Or.inr (q_pos hα1).le
  exact (continuous_const.mul hdr_continuous).mul continuous_const

/-- `R*_X(s)` is the maximal score at share `s` (prop:score with `ℓ = λ h(s)`, `σ̄ = ∞`). -/
theorem Rst_isGreatest (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar)
    {s : ℝ} (hs : s < sbar) :
    IsGreatest (score X '' Feasible m0 G k α (lam * hdr sbar s) ⊤) (Rst α sbar m0 G k X lam s) :=
  Rstar_isGreatest hα hα1 (ℓ_pos hlam hsbar hs) X

/-- Derivative of `R*_X(s)` in `s` for `X > k`: `-(X-k)Δ*/(s̄ - s)`. -/
theorem Rst_hasDerivAt (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar)
    (hX : k < X) {s : ℝ} (hs : s < sbar) :
    HasDerivAt (Rst α sbar m0 G k X lam)
      (-((X - k) * Δstar α (lam * hdr sbar s) (X - k) / (sbar - s))) s := by
  have hy : 0 < X - k := sub_pos.2 hX
  have hu : 0 < lam * hdr sbar s := ℓ_pos hlam hsbar hs
  have hf : Rst α sbar m0 G k X lam = fun s =>
      Rinf m0 G k X + Cα α * ((lam * hdr sbar s) * (X - k)) ^ (1 / (1 - α)) := by
    funext s; rw [Rst_of_lt hX]
  rw [hf]
  -- inner map `s ↦ λ h(s)` has derivative `-λ/s̄`
  have hin : HasDerivAt (fun s => lam * hdr sbar s) (lam * (0 - 1 / sbar)) s := by
    have : HasDerivAt (fun s => 1 - s / sbar) (0 - 1 / sbar) s :=
      (hasDerivAt_const s (1 : ℝ)).sub ((hasDerivAt_id' s).div_const sbar)
    exact this.const_mul lam
  have hout := hasDerivAt_surplus_ℓ hα hα1 hu hy
  have hcomp := hout.comp s hin
  refine ((hasDerivAt_const s (Rinf m0 G k X)).add hcomp).congr_deriv ?_
  rw [sbar_sub_eq hsbar.ne' s]
  have hh : hdr sbar s ≠ 0 := (hdr_pos hsbar hs).ne'
  have hsb : sbar ≠ 0 := hsbar.ne'
  have hl : lam ≠ 0 := hlam.ne'
  field_simp
  ring

/-- **Lemma prop:saturation (a).** "`R*_X(s) = R_∞ + C_α[λ h(s) y₊]^{1/(1-α)}`. If `X > k`,
this is strictly decreasing in `s`, with `dR*_X/ds = -(X-k)Δ*/(s̄ - s)`. If `X ≤ k`, it is
constant." (`R*_X(s)` is the maximal score at share `s`: first conjunct.) -/
theorem prop_saturation_a (hα : 0 < α) (hα1 : α < 1) (_hk : 0 ≤ k) (hlam : 0 < lam)
    (hsbar : 0 < sbar) (X : ℝ) :
    (∀ s, s < sbar →
      IsGreatest (score X '' Feasible m0 G k α (lam * hdr sbar s) ⊤) (Rst α sbar m0 G k X lam s)) ∧
    (∀ s, Rst α sbar m0 G k X lam s =
      Rinf m0 G k X + Cα α * (lam * hdr sbar s * max (X - k) 0) ^ (1 / (1 - α))) ∧
    (k < X → StrictAntiOn (Rst α sbar m0 G k X lam) (Ioo 0 sbar) ∧
      ∀ s, 0 < s → s < sbar → HasDerivAt (Rst α sbar m0 G k X lam)
        (-((X - k) * Δstar α (lam * hdr sbar s) (X - k) / (sbar - s))) s) ∧
    (X ≤ k → ∀ s s', Rst α sbar m0 G k X lam s = Rst α sbar m0 G k X lam s') := by
  refine ⟨fun s hs => Rst_isGreatest hα hα1 hlam hsbar hs, fun s => Rst_eq s, fun hX => ⟨?_, ?_⟩,
    fun hX s s' => by rw [Rst_of_le hα1 hX, Rst_of_le hα1 hX]⟩
  · intro s hs s' hs' hss'
    rw [Rst_of_lt hX, Rst_of_lt hX]
    have hy : 0 < X - k := sub_pos.2 hX
    have h1 : lam * hdr sbar s' * (X - k) < lam * hdr sbar s * (X - k) := by
      have := hdr_strictAnti hsbar hss'
      have := mul_lt_mul_of_pos_left this hlam
      exact mul_lt_mul_of_pos_right this hy
    have h2 := Real.rpow_lt_rpow (mul_pos (ℓ_pos hlam hsbar hs'.2) hy).le h1 (q_pos hα1)
    have h3 := mul_lt_mul_of_pos_left h2 (Cα_pos hα hα1)
    linarith
  · intro s _ hs
    exact Rst_hasDerivAt hα hα1 hlam hsbar hX hs

/-- **Lemma prop:saturation (b).** "`lim_{s→s̄} R*_X(s) = R_∞`. For the Rule of 40 with
`k = 0`, the limit is `m₀ + G`. Since `m₀ = 1 - c_h - c_c - f - a ≤ 1 - c_c - f - a_min ≤ 1`,
`R_∞ ≤ 1 - c_c - f - a_min + (X-k) G`, and for `X = 1`: `R_∞ ≤ 1 + (1-k) G`." -/
theorem prop_saturation_b (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar) (X : ℝ) :
    (∀ s, s < sbar →
      IsGreatest (score X '' Feasible m0 G k α (lam * hdr sbar s) ⊤) (Rst α sbar m0 G k X lam s)) ∧
    Tendsto (Rst α sbar m0 G k X lam) (𝓝[<] sbar) (𝓝 (Rinf m0 G k X)) ∧
    (X = 1 → k = 0 → Rinf m0 G k X = m0 + G) ∧
    (∀ ch cc f a amin : ℝ, 0 ≤ ch → 0 ≤ cc → 0 ≤ f → 0 ≤ amin → amin ≤ a →
      m0 = 1 - ch - cc - f - a →
      Rinf m0 G k X ≤ 1 - cc - f - amin + (X - k) * G ∧
      (X = 1 → Rinf m0 G k X ≤ 1 + (1 - k) * G)) := by
  refine ⟨fun s hs => Rst_isGreatest hα hα1 hlam hsbar hs, ?_,
    fun hX hk => by subst hX hk; unfold Rinf; ring, ?_⟩
  · have h := (Rst_continuous (α := α) (sbar := sbar) (m0 := m0) (G := G) (k := k) (X := X)
      (lam := lam) hα1).tendsto sbar
    have hval : Rst α sbar m0 G k X lam sbar = Rinf m0 G k X := by
      rw [Rst_eq, hdr_self hsbar, mul_zero, zero_mul, Real.zero_rpow (q_pos hα1).ne', mul_zero,
        add_zero]
    rw [hval] at h
    exact h.mono_left nhdsWithin_le_nhds
  · intro ch cc f a amin hch hcc hf hamin ha hm0
    unfold Rinf
    constructor
    · linarith
    · intro hX; subst hX; linarith

/-- **Lemma prop:saturation (c).** "`sup_{s∈(0,s̄)} R*_X(s) = lim_{s→0} R*_X(s) = R⁰ :=
`R_∞ + C_α(λ y₊)^{1/(1-α)}`. If `X > k`, the supremum is not attained; if `X ≤ k`, `R*_X` is
constant in `s` and the supremum is attained at every share." -/
theorem prop_saturation_c (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar) (X : ℝ) :
    (∀ s, s < sbar →
      IsGreatest (score X '' Feasible m0 G k α (lam * hdr sbar s) ⊤) (Rst α sbar m0 G k X lam s)) ∧
    IsLUB (Rst α sbar m0 G k X lam '' Ioo 0 sbar)
      (Rinf m0 G k X + Cα α * (lam * max (X - k) 0) ^ (1 / (1 - α))) ∧
    Tendsto (Rst α sbar m0 G k X lam) (𝓝[>] 0)
      (𝓝 (Rinf m0 G k X + Cα α * (lam * max (X - k) 0) ^ (1 / (1 - α)))) ∧
    (k < X → ∀ s ∈ Ioo 0 sbar, Rst α sbar m0 G k X lam s <
      Rinf m0 G k X + Cα α * (lam * max (X - k) 0) ^ (1 / (1 - α))) ∧
    (X ≤ k → ∀ s ∈ Ioo 0 sbar, Rst α sbar m0 G k X lam s =
      Rinf m0 G k X + Cα α * (lam * max (X - k) 0) ^ (1 / (1 - α))) := by
  set R0 := Rinf m0 G k X + Cα α * (lam * max (X - k) 0) ^ (1 / (1 - α)) with hR0
  have hval : Rst α sbar m0 G k X lam 0 = R0 := by
    rw [Rst_eq, hdr_zero, mul_one]
  have hlim : Tendsto (Rst α sbar m0 G k X lam) (𝓝[>] 0) (𝓝 R0) := by
    have h := (Rst_continuous (α := α) (sbar := sbar) (m0 := m0) (G := G) (k := k) (X := X)
      (lam := lam) hα1).tendsto 0
    rw [hval] at h
    exact h.mono_left nhdsWithin_le_nhds
  -- upper bound: `h(s) ≤ 1`
  have hub : ∀ s ∈ Ioo 0 sbar, Rst α sbar m0 G k X lam s ≤ R0 := by
    intro s hs
    rw [Rst_eq, hR0]
    have h1 : lam * hdr sbar s * max (X - k) 0 ≤ lam * max (X - k) 0 := by
      have := hdr_lt_one hsbar hs.1
      have h0 := hdr_pos hsbar hs.2
      nlinarith [le_max_right (X - k) 0, mul_nonneg hlam.le (le_max_right (X - k) 0)]
    have h2 := Real.rpow_le_rpow (mul_nonneg (ℓ_pos hlam hsbar hs.2).le (le_max_right _ _)) h1
      (q_pos hα1).le
    have h3 := mul_le_mul_of_nonneg_left h2 (Cα_pos hα hα1).le
    linarith
  refine ⟨fun s hs => Rst_isGreatest hα hα1 hlam hsbar hs, ⟨?_, ?_⟩, hlim, ?_, ?_⟩
  · rintro _ ⟨s, hs, rfl⟩
    exact hub s hs
  · intro b hb
    by_contra hlt
    push Not at hlt
    have h1 : ∀ᶠ s in 𝓝[>] (0 : ℝ), b < Rst α sbar m0 G k X lam s :=
      (tendsto_order.1 hlim).1 b hlt
    have h2 : ∀ᶠ s in 𝓝[>] (0 : ℝ), s ∈ Ioo 0 sbar :=
      Ioo_mem_nhdsGT hsbar
    obtain ⟨s, hs1, hs2⟩ := (h1.and h2).exists
    exact absurd (hb ⟨s, hs2, rfl⟩) (not_le.2 hs1)
  · intro hX s hs
    rw [Rst_of_lt hX, hR0, max_eq_left (sub_pos.2 hX).le]
    have hy : 0 < X - k := sub_pos.2 hX
    have h1 : lam * hdr sbar s * (X - k) < lam * (X - k) := by
      have := hdr_lt_one hsbar hs.1
      have h0 := mul_lt_mul_of_pos_left this hlam
      rw [mul_one] at h0
      exact mul_lt_mul_of_pos_right h0 hy
    have h2 := Real.rpow_lt_rpow (mul_pos (ℓ_pos hlam hsbar hs.2) hy).le h1 (q_pos hα1)
    have h3 := mul_lt_mul_of_pos_left h2 (Cα_pos hα hα1)
    linarith
  · intro hX s _
    rw [Rst_of_le hα1 hX, hR0, max_eq_right (sub_nonpos.2 hX), mul_zero,
      Real.zero_rpow (q_pos hα1).ne', mul_zero, add_zero]

/-- **Lemma prop:saturation (d).** "Let `X > k` and `R̄ > R_∞`, and define
`Λ(R̄) := (1/(X-k)) [(R̄ - R_∞)/C_α]^{1-α}`. Then `R*_X(s) ≥ R̄` iff `λ h(s) ≥ Λ(R̄)`, and a
score of `R̄` is attainable at some share iff `λ > Λ(R̄)`. A firm exactly at the threshold has
`Δ* = (R̄ - R_∞)/[(1-α)(X-k)]`, `σ* = α(R̄ - R_∞)/(1-α)` and `m = m₀ - k g* - σ*`." -/
theorem prop_saturation_d (hα : 0 < α) (hα1 : α < 1) (_hk : 0 ≤ k) (hlam : 0 < lam)
    (hsbar : 0 < sbar) (hX : k < X) {Rbar : ℝ} (hR : Rinf m0 G k X < Rbar) :
    (∀ s ∈ Ioo 0 sbar, Rbar ≤ Rst α sbar m0 G k X lam s ↔ Λ α m0 G k X Rbar ≤ lam * hdr sbar s) ∧
    ((∃ s ∈ Ioo 0 sbar, Rbar ≤ Rst α sbar m0 G k X lam s) ↔ Λ α m0 G k X Rbar < lam) ∧
    (∀ s ∈ Ioo 0 sbar, lam * hdr sbar s = Λ α m0 G k X Rbar →
      Δstar α (lam * hdr sbar s) (X - k) = (Rbar - Rinf m0 G k X) / ((1 - α) * (X - k)) ∧
      σstar α (lam * hdr sbar s) (X - k) = α * (Rbar - Rinf m0 G k X) / (1 - α) ∧
      mstar m0 G k α (lam * hdr sbar s) (gstar G k α (lam * hdr sbar s) X) =
        m0 - k * gstar G k α (lam * hdr sbar s) X - σstar α (lam * hdr sbar s) (X - k)) := by
  have hy : 0 < X - k := sub_pos.2 hX
  have hC := Cα_pos hα hα1
  have hq1 : 0 < 1 - α := by linarith
  have hRpos : 0 < Rbar - Rinf m0 G k X := sub_pos.2 hR
  set c := ((Rbar - Rinf m0 G k X) / Cα α) ^ (1 - α) with hc
  have hc0 : 0 ≤ c := Real.rpow_nonneg (div_pos hRpos hC).le _
  have hΛ : Λ α m0 G k X Rbar = c / (X - k) := by
    unfold Λ; rw [hc]; ring
  -- the key equivalence for `ℓ > 0`
  have key : ∀ ℓ : ℝ, 0 < ℓ →
      (Rbar ≤ Rinf m0 G k X + Cα α * (ℓ * (X - k)) ^ (1 / (1 - α)) ↔ Λ α m0 G k X Rbar ≤ ℓ) := by
    intro ℓ hℓ
    rw [hΛ, div_le_iff₀ hy]
    have hℓy : 0 ≤ ℓ * (X - k) := (mul_pos hℓ hy).le
    have e : ((ℓ * (X - k)) ^ (1 / (1 - α))) ^ (1 - α) = ℓ * (X - k) := by
      rw [← Real.rpow_mul hℓy, one_div_mul_cancel hq1.ne', Real.rpow_one]
    constructor
    · intro h
      have h1 : (Rbar - Rinf m0 G k X) / Cα α ≤ (ℓ * (X - k)) ^ (1 / (1 - α)) := by
        rw [div_le_iff₀ hC]; linarith
      have h2 := Real.rpow_le_rpow (div_pos hRpos hC).le h1 hq1.le
      rw [e] at h2
      exact h2
    · intro h
      have h1 : ((Rbar - Rinf m0 G k X) / Cα α) ^ (1 - α) ≤
          ((ℓ * (X - k)) ^ (1 / (1 - α))) ^ (1 - α) := by rw [e]; exact h
      rw [Real.rpow_le_rpow_iff (div_pos hRpos hC).le (Real.rpow_nonneg hℓy _) hq1] at h1
      rw [div_le_iff₀ hC] at h1
      linarith
  refine ⟨fun s hs => ?_, ⟨?_, ?_⟩, fun s hs hΛs => ?_⟩
  · rw [Rst_of_lt hX]
    exact key _ (ℓ_pos hlam hsbar hs.2)
  · rintro ⟨s, hs, hRs⟩
    rw [Rst_of_lt hX, key _ (ℓ_pos hlam hsbar hs.2)] at hRs
    have := hdr_lt_one hsbar hs.1
    have := mul_lt_mul_of_pos_left this hlam
    linarith
  · intro hΛlam
    have hΛ0 : 0 < Λ α m0 G k X Rbar := by
      rw [hΛ]
      exact div_pos (Real.rpow_pos_of_pos (div_pos hRpos hC) _) hy
    -- choose `s` with `λ h(s) = Λ`
    refine ⟨sbar * (1 - Λ α m0 G k X Rbar / lam), ⟨?_, ?_⟩, ?_⟩
    · have : Λ α m0 G k X Rbar / lam < 1 := by rw [div_lt_one hlam]; exact hΛlam
      exact mul_pos hsbar (by linarith)
    · have : 0 < Λ α m0 G k X Rbar / lam := div_pos hΛ0 hlam
      nlinarith
    · rw [Rst_of_lt hX, key _ (ℓ_pos hlam hsbar (by nlinarith [div_pos hΛ0 hlam]))]
      unfold hdr
      have hsb : sbar ≠ 0 := hsbar.ne'
      have hl : lam ≠ 0 := hlam.ne'
      refine le_of_eq ?_
      field_simp
      ring
  · have hℓ := ℓ_pos hlam hsbar hs.2
    -- at the threshold, `Π = R̄ - R_∞`
    have hPi : (1 - α) * (X - k) * Δstar α (lam * hdr sbar s) (X - k) = Rbar - Rinf m0 G k X := by
      rw [surplus_eq hα hα1 hℓ hy, hΛs, hΛ]
      have e : c / (X - k) * (X - k) = c := div_mul_cancel₀ c hy.ne'
      rw [e, hc, ← Real.rpow_mul (div_pos hRpos hC).le, mul_one_div_cancel hq1.ne', Real.rpow_one]
      field_simp
    have hΔ : Δstar α (lam * hdr sbar s) (X - k) = (Rbar - Rinf m0 G k X) / ((1 - α) * (X - k)) := by
      rw [eq_div_iff (mul_pos hq1 hy).ne']
      linarith [hPi]
    refine ⟨hΔ, ?_, ?_⟩
    · rw [σstar_eq hα hα1 hℓ hy, hΔ]
      field_simp
    · have h := (prop_score_b (m0 := m0) (G := G) hα hα1 hℓ _hk zero_lt_top hX le_top)
      rw [h.2.2.2.2.2.2.2.2.2.2.2.2, σstar_eq hα hα1 hℓ hy]

end RuleOfX
