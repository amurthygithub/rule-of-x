import RuleOfX.Envelope

/-!
# Corollary cor:capital (Capital-for-labor substitution) and Corollary cor:priorities
# (Automation priorities), exact parts

`σ̄ = ∞`, `ℓ = λ h(s)`, `m₀ = γ - a`. "To first order" is read as a statement about the
derivative along the direction of the change (see `cor_capital`, last conjuncts).
-/

noncomputable section
open Real Set Filter Topology

set_option autoImplicit false

namespace RuleOfX

variable {m0 G k α lam sbar X s : ℝ}

theorem Rst_add_m0 (d : ℝ) :
    Rst α sbar (m0 + d) G k X lam s = Rst α sbar m0 G k X lam s + d := by
  unfold Rst; ring

theorem gstar_antitone_k (hα : 0 < α) (hα1 : α < 1) {ℓ : ℝ} (hℓ : 0 < ℓ) {k k' : ℝ}
    (hkk' : k ≤ k') : gstar G k' α ℓ X ≤ gstar G k α ℓ X := by
  unfold gstar
  have := Δplus_monotone hα hα1 hℓ (show X - k' ≤ X - k by linarith)
  linarith

theorem G_le_gstar (hα : 0 < α) {ℓ : ℝ} (hℓ : 0 < ℓ) : G ≤ gstar G k α ℓ X := by
  unfold gstar
  have := Δplus_nonneg hα hℓ (X - k)
  linarith

/-- The exact bracket eq:kl-bracket, by the mean value theorem and the monotonicity of `g*`
in `k` (equivalently, the convexity of `R*_X` in `k`). -/
theorem kl_bracket (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar)
    (hs : s < sbar) (γ a : ℝ) {da dk : ℝ} (hdk : 0 < dk) :
    da - gstar G k α (lam * hdr sbar s) X * dk ≤
      Rst α sbar (γ - (a - da)) G (k + dk) X lam s - Rst α sbar (γ - a) G k X lam s ∧
    Rst α sbar (γ - (a - da)) G (k + dk) X lam s - Rst α sbar (γ - a) G k X lam s ≤
      da - gstar G (k + dk) α (lam * hdr sbar s) X * dk := by
  have hℓ := ℓ_pos hlam hsbar hs
  have hΦ : ∀ x, HasDerivAt (fun k => Rst α sbar (γ - a) G k X lam s)
      (-(gstar G x α (lam * hdr sbar s) X)) x := fun x => hasDerivAt_Rst_k hα hα1 hlam hsbar hs
  have hcont : ContinuousOn (fun k => Rst α sbar (γ - a) G k X lam s) (Icc k (k + dk)) :=
    (continuous_iff_continuousAt.2 fun x => (hΦ x).continuousAt).continuousOn
  obtain ⟨c, hc, hceq⟩ := exists_hasDerivAt_eq_slope (fun k => Rst α sbar (γ - a) G k X lam s)
    (fun x => -(gstar G x α (lam * hdr sbar s) X)) (by linarith : k < k + dk) hcont
    (fun x _ => hΦ x)
  have hm0 : γ - (a - da) = (γ - a) + da := by ring
  rw [hm0, Rst_add_m0]
  have hslope : Rst α sbar (γ - a) G (k + dk) X lam s - Rst α sbar (γ - a) G k X lam s =
      -(gstar G c α (lam * hdr sbar s) X) * dk := by
    have h := hceq
    rw [add_sub_cancel_left] at h
    rw [h]; field_simp
  have h1 := gstar_antitone_k (G := G) (X := X) hα hα1 hℓ hc.1.le
  have h2 := gstar_antitone_k (G := G) (X := X) hα hα1 hℓ hc.2.le
  constructor
  · nlinarith [mul_le_mul_of_nonneg_right h1 hdk.le]
  · nlinarith [mul_le_mul_of_nonneg_right h2 hdk.le]

/-- **Corollary cor:capital.** "Let `σ̄ = ∞`, and suppose automation lowers `a` by `da > 0` and
raises `k` by `dk > 0`, with other parameters fixed. Then the change in the maximal score
satisfies `da - g*(k) dk ≤ ΔR*_X ≤ da - g*(k+dk) dk`. Hence the score rises if `da > g*(k) dk`
and does not rise if `da ≤ g*(k+dk) dk`. To first order, it rises if and only if `da > g* dk`."
(The first-order claim is read as: the derivative of `t ↦ R*_X(a - t da, k + t dk)` at `t = 0`
equals `da - g*(k) dk`, which is positive iff `da > g*(k) dk`.) -/
theorem cor_capital (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar)
    (hs : s < sbar) (γ a : ℝ) {da dk : ℝ} (_hda : 0 < da) (hdk : 0 < dk) :
    (da - gstar G k α (lam * hdr sbar s) X * dk ≤
      Rst α sbar (γ - (a - da)) G (k + dk) X lam s - Rst α sbar (γ - a) G k X lam s ∧
    Rst α sbar (γ - (a - da)) G (k + dk) X lam s - Rst α sbar (γ - a) G k X lam s ≤
      da - gstar G (k + dk) α (lam * hdr sbar s) X * dk) ∧
    (gstar G k α (lam * hdr sbar s) X * dk < da →
      0 < Rst α sbar (γ - (a - da)) G (k + dk) X lam s - Rst α sbar (γ - a) G k X lam s) ∧
    (da ≤ gstar G (k + dk) α (lam * hdr sbar s) X * dk →
      Rst α sbar (γ - (a - da)) G (k + dk) X lam s - Rst α sbar (γ - a) G k X lam s ≤ 0) ∧
    HasDerivAt (fun t => Rst α sbar (γ - (a - t * da)) G (k + t * dk) X lam s)
      (da - gstar G k α (lam * hdr sbar s) X * dk) 0 ∧
    (0 < da - gstar G k α (lam * hdr sbar s) X * dk ↔ gstar G k α (lam * hdr sbar s) X * dk < da) := by
  have hb := kl_bracket (G := G) (k := k) (X := X) hα hα1 hlam hsbar hs γ a (da := da) hdk
  refine ⟨hb, fun h => by linarith [hb.1], fun h => by linarith [hb.2], ?_, ?_⟩
  swap
  · constructor <;> intro h <;> linarith
  have hf : (fun t => Rst α sbar (γ - (a - t * da)) G (k + t * dk) X lam s) =
      fun t => Rst α sbar (γ - a) G (k + t * dk) X lam s + t * da := by
    funext t; unfold Rst; ring
  rw [hf]
  have h1 := (hasDerivAt_Rst_k (m0 := γ - a) (G := G) (X := X) (k := k + 0 * dk)
    hα hα1 hlam hsbar hs).comp (0 : ℝ) (((hasDerivAt_id' (0 : ℝ)).mul_const dk).const_add k)
  have h2 := (hasDerivAt_id' (0 : ℝ)).mul_const da
  refine (h1.add h2).congr_deriv ?_
  simp only [zero_mul, add_zero]
  ring

/-! ### Corollary cor:priorities, exact parts -/

/-- **cor:priorities (i).** "Removing non-discretionary cost `da` raises `R*_X` by `da` and the
saturated score `R_∞` by `da`." (Exact, through `m₀ = γ - a`.) -/
theorem cor_priorities_i (γ a da : ℝ) :
    Rst α sbar (γ - (a - da)) G k X lam s = Rst α sbar (γ - a) G k X lam s + da ∧
    Rinf (γ - (a - da)) G k X = Rinf (γ - a) G k X + da := by
  constructor
  · unfold Rst; ring
  · unfold Rinf; ring

/-- `R*_X` under `λ ↦ λ c` for `c ≥ 0`: the surplus is multiplied by `c^{1/(1-α)}`. -/
theorem Rst_scale_lam (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar)
    (hs : s < sbar) {c : ℝ} (hc : 0 ≤ c) :
    Rst α sbar m0 G k X (lam * c) s - Rst α sbar m0 G k X lam s =
      surplus α (lam * hdr sbar s) (X - k) * (c ^ (1 / (1 - α)) - 1) := by
  have hℓ := ℓ_pos hlam hsbar hs
  rw [surplus_eq_Cα hα hα1 hℓ, Rst_eq, Rst_eq]
  have e : lam * c * hdr sbar s * max (X - k) 0 = c * (lam * hdr sbar s * max (X - k) 0) := by ring
  rw [e, Real.mul_rpow hc (mul_nonneg hℓ.le (le_max_right _ _))]
  ring

/-- **cor:priorities (ii), exact statements.** "Let an improvement `x` in the efficiency of
growth spend deliver the same growth for spend `σ/(1+x)`, which maps to `λ ↦ λ(1+x)^α`. It
raises `R*_X` ... exactly, by `Π[(1+x)^{α/(1-α)} - 1]`. Measured instead as a rise `x_λ` in
demand pull, the gain is ... `Π[(1+x_λ)^{1/(1-α)} - 1]` exactly. Neither raises `R_∞`, and both
vanish as `s → s̄`." (The first-order claims are the derivatives at `x = 0`: `σ*` and
`(X-k)Δ* = σ*/α`, proved for `X > k`.) -/
theorem cor_priorities_ii (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar)
    (hs : s < sbar) {x : ℝ} (hx : -1 < x) :
    Rst α sbar m0 G k X (lam * (1 + x) ^ α) s - Rst α sbar m0 G k X lam s =
      surplus α (lam * hdr sbar s) (X - k) * ((1 + x) ^ (α / (1 - α)) - 1) ∧
    Rst α sbar m0 G k X (lam * (1 + x)) s - Rst α sbar m0 G k X lam s =
      surplus α (lam * hdr sbar s) (X - k) * ((1 + x) ^ (1 / (1 - α)) - 1) ∧
    (k < X → HasDerivAt (fun x => Rst α sbar m0 G k X (lam * (1 + x) ^ α) s)
      (σplus α (lam * hdr sbar s) (X - k)) 0) ∧
    (k < X → HasDerivAt (fun x => Rst α sbar m0 G k X (lam * (1 + x)) s)
      ((X - k) * Δplus α (lam * hdr sbar s) (X - k)) 0 ∧
      (X - k) * Δplus α (lam * hdr sbar s) (X - k) = σplus α (lam * hdr sbar s) (X - k) / α) ∧
    Tendsto (fun s => Rst α sbar m0 G k X (lam * (1 + x) ^ α) s - Rst α sbar m0 G k X lam s)
      (𝓝[<] sbar) (𝓝 0) ∧
    Tendsto (fun s => Rst α sbar m0 G k X (lam * (1 + x)) s - Rst α sbar m0 G k X lam s)
      (𝓝[<] sbar) (𝓝 0) := by
  have hℓ := ℓ_pos hlam hsbar hs
  have h1x : 0 < 1 + x := by linarith
  have hA := Rst_scale_lam (m0 := m0) (G := G) (k := k) (X := X) hα hα1 hlam hsbar hs
    (Real.rpow_nonneg h1x.le α)
  rw [← Real.rpow_mul h1x.le, show α * (1 / (1 - α)) = α / (1 - α) by ring] at hA
  have hB := Rst_scale_lam (m0 := m0) (G := G) (k := k) (X := X) hα hα1 hlam hsbar hs h1x.le
  refine ⟨hA, hB, fun hX => ?_, fun hX => ⟨?_, ?_⟩, ?_, ?_⟩
  · -- derivative of the exact gain `Π[(1+x)^{α/(1-α)} - 1]` at `x = 0`
    have hy : 0 < X - k := sub_pos.2 hX
    have hev : (fun x => Rst α sbar m0 G k X (lam * (1 + x) ^ α) s) =ᶠ[𝓝 (0 : ℝ)]
        fun x => Rst α sbar m0 G k X lam s +
          surplus α (lam * hdr sbar s) (X - k) * ((1 + x) ^ (α / (1 - α)) - 1) := by
      filter_upwards [Ioi_mem_nhds (show (-1 : ℝ) < 0 by norm_num)] with x hx'
      have h := Rst_scale_lam (m0 := m0) (G := G) (k := k) (X := X) hα hα1 hlam hsbar hs
        (Real.rpow_nonneg (show (0 : ℝ) ≤ 1 + x by linarith [mem_Ioi.1 hx']) α)
      rw [← Real.rpow_mul (show (0 : ℝ) ≤ 1 + x by linarith [mem_Ioi.1 hx']),
        show α * (1 / (1 - α)) = α / (1 - α) by ring] at h
      linarith
    have hd : HasDerivAt (fun x : ℝ => (1 + x) ^ (α / (1 - α)))
        (1 * (α / (1 - α)) * (1 + 0) ^ (α / (1 - α) - 1)) 0 :=
      ((hasDerivAt_id' (0 : ℝ)).const_add 1).rpow_const (Or.inl (by norm_num))
    have hd2 := (((hd.sub_const 1).const_mul (surplus α (lam * hdr sbar s) (X - k))).const_add
      (Rst α sbar m0 G k X lam s))
    refine (hd2.congr_of_eventuallyEq hev).congr_deriv ?_
    rw [σplus_of_pos hy.le, σstar_eq hα hα1 hℓ hy, surplus_of_pos hy.le]
    simp only [add_zero, Real.one_rpow, one_mul, mul_one]
    have h1α : (1 - α) ≠ 0 := by linarith
    field_simp
  · have hy : 0 < X - k := sub_pos.2 hX
    have hev : (fun x => Rst α sbar m0 G k X (lam * (1 + x)) s) =ᶠ[𝓝 (0 : ℝ)]
        fun x => Rst α sbar m0 G k X lam s +
          surplus α (lam * hdr sbar s) (X - k) * ((1 + x) ^ (1 / (1 - α)) - 1) := by
      filter_upwards [Ioi_mem_nhds (show (-1 : ℝ) < 0 by norm_num)] with x hx'
      have h := Rst_scale_lam (m0 := m0) (G := G) (k := k) (X := X) hα hα1 hlam hsbar hs
        (show (0 : ℝ) ≤ 1 + x by linarith [mem_Ioi.1 hx'])
      linarith
    have hd : HasDerivAt (fun x : ℝ => (1 + x) ^ (1 / (1 - α)))
        (1 * (1 / (1 - α)) * (1 + 0) ^ (1 / (1 - α) - 1)) 0 :=
      ((hasDerivAt_id' (0 : ℝ)).const_add 1).rpow_const (Or.inl (by norm_num))
    have hd2 := (((hd.sub_const 1).const_mul (surplus α (lam * hdr sbar s) (X - k))).const_add
      (Rst α sbar m0 G k X lam s))
    refine (hd2.congr_of_eventuallyEq hev).congr_deriv ?_
    rw [Δplus_of_pos hy.le, surplus_of_pos hy.le]
    simp only [add_zero, Real.one_rpow, one_mul, mul_one]
    have h1α : (1 - α) ≠ 0 := by linarith
    field_simp
  · have hy : 0 < X - k := sub_pos.2 hX
    rw [Δplus_of_pos hy.le, σplus_of_pos hy.le, σstar_eq hα hα1 hℓ hy]
    field_simp
  · have h1 := (prop_saturation_b (m0 := m0) (G := G) (k := k) hα hα1
      (mul_pos hlam (Real.rpow_pos_of_pos h1x α)) hsbar X).1
    have h2 := (prop_saturation_b (m0 := m0) (G := G) (k := k) hα hα1 hlam hsbar X).1
    have := h1.sub h2
    rwa [sub_self] at this
  · have h1 := (prop_saturation_b (m0 := m0) (G := G) (k := k) hα hα1
      (mul_pos hlam h1x) hsbar X).1
    have h2 := (prop_saturation_b (m0 := m0) (G := G) (k := k) hα hα1 hlam hsbar X).1
    have := h1.sub h2
    rwa [sub_self] at this

/-- **cor:priorities (iii).** "Raising zero-spend growth `G_i` by `dG` raises `R*_X` by
`(X-k) dG`, and `R_∞` by the same amount; at a fixed weight the gain does not depend on the
firm's share or growth." (Here `G` is the zero-spend growth rate; the derivative `X - k` is the
same at every share `s`, `s'`.) -/
theorem cor_priorities_iii :
    HasDerivAt (fun G => Rst α sbar m0 G k X lam s) (X - k) G ∧
    HasDerivAt (fun G => Rinf m0 G k X) (X - k) G ∧
    ∀ s' : ℝ, deriv (fun G => Rst α sbar m0 G k X lam s) G =
      deriv (fun G => Rst α sbar m0 G k X lam s') G := by
  refine ⟨hasDerivAt_Rst_G, ?_, fun s' => ?_⟩
  · unfold Rinf
    exact (((hasDerivAt_id' G).const_mul (X - k)).const_add m0).congr_deriv (by ring)
  · rw [hasDerivAt_Rst_G.deriv, hasDerivAt_Rst_G.deriv]

/-- **cor:priorities (v).** "Automation that adds capital `dk` while removing cost `da` raises
`R*_X` if and only if `da > g* dk` (cor:capital); since `g* ≥ G`, the hurdle is lowest for the
slowest growers." (First order: sign of the derivative in `cor_capital`; `g* ≥ G`; the hurdle
`g* dk` is nondecreasing in `g*`.) -/
theorem cor_priorities_v (hα : 0 < α) (hα1 : α < 1) (hlam : 0 < lam) (hsbar : 0 < sbar)
    (hs : s < sbar) (γ a : ℝ) {da dk : ℝ} (hda : 0 < da) (hdk : 0 < dk) :
    HasDerivAt (fun t => Rst α sbar (γ - (a - t * da)) G (k + t * dk) X lam s)
      (da - gstar G k α (lam * hdr sbar s) X * dk) 0 ∧
    (0 < da - gstar G k α (lam * hdr sbar s) X * dk ↔ gstar G k α (lam * hdr sbar s) X * dk < da) ∧
    G ≤ gstar G k α (lam * hdr sbar s) X ∧
    (∀ g g' : ℝ, g ≤ g' → g * dk ≤ g' * dk) := by
  have h := cor_capital (G := G) (k := k) (X := X) hα hα1 hlam hsbar hs γ a hda hdk
  exact ⟨h.2.2.2.1, h.2.2.2.2, G_le_gstar hα (ℓ_pos hlam hsbar hs),
    fun g g' hgg' => mul_le_mul_of_nonneg_right hgg' hdk.le⟩

end RuleOfX
