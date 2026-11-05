import RuleOfX.Defs

/-!
# Proposition prop:budget (Score budget), discrete time, and Corollary cor:transient (a)

Discrete time: `g_t`, `m_t` are period rates, `G > -1`, `s_{t+1} = s_t (1 + g_t)/(1 + G)`,
`g_t ≥ G`, `m_t ≤ m₀(t) - k g_t`, `s_t ≤ s̄`, and `R_{X,t} = X g_t + m_t`.  Part (c) (moving
intercept `m₀(t)`) is proved first; part (b) is the special case of a constant intercept.
Neither the growth technology eq:growth nor optimal behaviour is used, as the paper says.
-/

noncomputable section
open Real Set Filter Topology Finset

set_option autoImplicit false

namespace RuleOfX

/-- Positivity of the share path. -/
theorem share_pos {G : ℝ} (hG : -1 < G) {s g : ℕ → ℝ} (hs0 : 0 < s 0)
    (hrec : ∀ t, s (t + 1) = s t * (1 + g t) / (1 + G)) (hg : ∀ t, G ≤ g t) (t : ℕ) :
    0 < s t := by
  induction t with
  | zero => exact hs0
  | succ n ih =>
    rw [hrec n]
    have h1 : 0 < 1 + g n := by linarith [hg n]
    have h2 : 0 < 1 + G := by linarith
    positivity

/-- One period of the budget: the log of the score excess term is at most `ln(s_{t+1}/s_t)`. -/
theorem budget_step {m0t G k X gt mt st st1 : ℝ} (hG : -1 < G) (hXk : k < X) (hst : 0 < st)
    (hrec : st1 = st * (1 + gt) / (1 + G)) (hg : G ≤ gt) (hm : mt ≤ m0t - k * gt) :
    Real.log (1 + max (X * gt + mt - (m0t + (X - k) * G)) 0 / ((X - k) * (1 + G))) ≤
      Real.log (st1 / st) := by
  have hy : 0 < X - k := sub_pos.2 hXk
  have h1G : 0 < 1 + G := by linarith
  have hden : 0 < (X - k) * (1 + G) := mul_pos hy h1G
  -- `(R - R_∞)⁺ ≤ (X-k)(g - G)`
  have hex : max (X * gt + mt - (m0t + (X - k) * G)) 0 ≤ (X - k) * (gt - G) := by
    apply max_le
    · nlinarith
    · exact mul_nonneg hy.le (sub_nonneg.2 hg)
  have hratio : st1 / st = (1 + gt) / (1 + G) := by
    rw [hrec]; field_simp
  rw [hratio]
  apply Real.log_le_log
  · have : 0 ≤ max (X * gt + mt - (m0t + (X - k) * G)) 0 / ((X - k) * (1 + G)) :=
      div_nonneg (le_max_right _ _) hden.le
    linarith
  · have e : (1 + gt) / (1 + G) = 1 + (gt - G) / (1 + G) := by field_simp; ring
    rw [e]
    have : max (X * gt + mt - (m0t + (X - k) * G)) 0 / ((X - k) * (1 + G)) ≤ (gt - G) / (1 + G) := by
      rw [div_le_div_iff₀ hden h1G]
      nlinarith [mul_le_mul_of_nonneg_right hex h1G.le]
    linarith

/-- **Proposition prop:budget (c), discrete case.** "(Moving intercept.) If the margin intercept
moves over time, `m₀(t)`, then (b) holds with `R_∞(t) = m₀(t) + (X-k)G` in place of `R_∞`":
`∑_{t<T} ln(1 + (R_{X,t} - R_∞(t))⁺/[(X-k)(1+G)]) ≤ ln(s_T/s₀) ≤ ln(s̄/s₀)`. -/
theorem prop_budget_c_discrete {G k X sbar : ℝ} (hG : -1 < G) (hXk : k < X)
    (s g m m0 : ℕ → ℝ) (hs0 : 0 < s 0)
    (hrec : ∀ t, s (t + 1) = s t * (1 + g t) / (1 + G)) (hg : ∀ t, G ≤ g t)
    (hm : ∀ t, m t ≤ m0 t - k * g t) (hcap : ∀ t, s t ≤ sbar) (T : ℕ) :
    ∑ t ∈ range T, Real.log (1 + max (X * g t + m t - (m0 t + (X - k) * G)) 0 /
        ((X - k) * (1 + G))) ≤ Real.log (s T / s 0) ∧
    Real.log (s T / s 0) ≤ Real.log (sbar / s 0) := by
  have hpos := share_pos hG hs0 hrec hg
  constructor
  · calc ∑ t ∈ range T, Real.log (1 + max (X * g t + m t - (m0 t + (X - k) * G)) 0 /
            ((X - k) * (1 + G)))
        ≤ ∑ t ∈ range T, Real.log (s (t + 1) / s t) := by
          apply Finset.sum_le_sum
          intro t _
          exact budget_step hG hXk (hpos t) (hrec t) (hg t) (hm t)
      _ = ∑ t ∈ range T, (Real.log (s (t + 1)) - Real.log (s t)) := by
          apply Finset.sum_congr rfl
          intro t _
          rw [Real.log_div (hpos (t + 1)).ne' (hpos t).ne']
      _ = Real.log (s T) - Real.log (s 0) := Finset.sum_range_sub (fun t => Real.log (s t)) T
      _ = Real.log (s T / s 0) := by rw [Real.log_div (hpos T).ne' (hpos 0).ne']
  · rw [Real.log_div (hpos T).ne' (hpos 0).ne',
      Real.log_div (lt_of_lt_of_le (hpos 0) (hcap 0)).ne' (hpos 0).ne']
    have := Real.log_le_log (hpos T) (hcap T)
    linarith

/-- **Proposition prop:budget (b).** "(Discrete time.) Suppose instead that growth and margins
are period rates, with `G > -1`: `s_{t+1} = s_t(1+g_t)/(1+G)`, `g_t ≥ G`, `m_t ≤ m₀ - k g_t`,
and `s_t ≤ s̄` for all `t`. Then
`∑_{t=0}^{T-1} ln(1 + (R_{X,t} - R_∞)⁺/[(X-k)(1+G)]) ≤ ln(s_T/s₀) ≤ ln(s̄/s₀)`."
(Hypotheses `X > k` and `s₀ > 0` as in the proposition's setting.) -/
theorem prop_budget_b {m0 G k X sbar : ℝ} (hG : -1 < G) (hXk : k < X)
    (s g m : ℕ → ℝ) (hs0 : 0 < s 0)
    (hrec : ∀ t, s (t + 1) = s t * (1 + g t) / (1 + G)) (hg : ∀ t, G ≤ g t)
    (hm : ∀ t, m t ≤ m0 - k * g t) (hcap : ∀ t, s t ≤ sbar) (T : ℕ) :
    ∑ t ∈ range T, Real.log (1 + max (X * g t + m t - Rinf m0 G k X) 0 /
        ((X - k) * (1 + G))) ≤ Real.log (s T / s 0) ∧
    Real.log (s T / s 0) ≤ Real.log (sbar / s 0) :=
  prop_budget_c_discrete hG hXk s g m (fun _ => m0) hs0 hrec hg hm hcap T

/-- **Corollary cor:transient (a).** "(Period rates.) In the setting of prop:budget (b), the
number `𝒯(R̄)` of periods in which a firm starting at share `s₀` scores at least `R̄` satisfies
`𝒯(R̄) ≤ ln(s̄/s₀) / ln(1 + (R̄ - R_∞)/[(X-k)(1+G)])`." (Stated for the periods `t < T`, for
every horizon `T`; the bound does not depend on `T`.) -/
theorem cor_transient_a {m0 G k X sbar Rbar : ℝ} (hG : -1 < G) (hXk : k < X)
    (hR : Rinf m0 G k X < Rbar) (s g m : ℕ → ℝ) (hs0 : 0 < s 0)
    (hrec : ∀ t, s (t + 1) = s t * (1 + g t) / (1 + G)) (hg : ∀ t, G ≤ g t)
    (hm : ∀ t, m t ≤ m0 - k * g t) (hcap : ∀ t, s t ≤ sbar) (T : ℕ) :
    (((range T).filter fun t => Rbar ≤ X * g t + m t).card : ℝ) ≤
      Real.log (sbar / s 0) / Real.log (1 + (Rbar - Rinf m0 G k X) / ((X - k) * (1 + G))) := by
  have hy : 0 < X - k := sub_pos.2 hXk
  have h1G : 0 < 1 + G := by linarith
  have hden : 0 < (X - k) * (1 + G) := mul_pos hy h1G
  set c := Real.log (1 + (Rbar - Rinf m0 G k X) / ((X - k) * (1 + G))) with hc
  have hc0 : 0 < c := by
    rw [hc]
    apply Real.log_pos
    have : 0 < (Rbar - Rinf m0 G k X) / ((X - k) * (1 + G)) := div_pos (sub_pos.2 hR) hden
    linarith
  set f : ℕ → ℝ := fun t => Real.log (1 + max (X * g t + m t - Rinf m0 G k X) 0 /
    ((X - k) * (1 + G))) with hf
  have hfnonneg : ∀ t, 0 ≤ f t := by
    intro t
    apply Real.log_nonneg
    have : 0 ≤ max (X * g t + m t - Rinf m0 G k X) 0 / ((X - k) * (1 + G)) :=
      div_nonneg (le_max_right _ _) hden.le
    linarith
  have hfc : ∀ t ∈ (range T).filter (fun t => Rbar ≤ X * g t + m t), c ≤ f t := by
    intro t ht
    have ht' := (Finset.mem_filter.1 ht).2
    apply Real.log_le_log
    · have : 0 < (Rbar - Rinf m0 G k X) / ((X - k) * (1 + G)) := div_pos (sub_pos.2 hR) hden
      linarith
    · have : Rbar - Rinf m0 G k X ≤ max (X * g t + m t - Rinf m0 G k X) 0 :=
        le_max_of_le_left (by linarith)
      have := div_le_div_of_nonneg_right this hden.le
      linarith
  have hsum := (prop_budget_b hG hXk s g m hs0 hrec hg hm hcap T)
  have hsum' : ∑ t ∈ range T, f t ≤ Real.log (sbar / s 0) := hsum.1.trans hsum.2
  have hsub : ∑ t ∈ (range T).filter (fun t => Rbar ≤ X * g t + m t), f t ≤ ∑ t ∈ range T, f t :=
    Finset.sum_le_sum_of_subset_of_nonneg (Finset.filter_subset _ _) (fun t _ _ => hfnonneg t)
  have hcard : ((range T).filter (fun t => Rbar ≤ X * g t + m t)).card • c ≤
      ∑ t ∈ (range T).filter (fun t => Rbar ≤ X * g t + m t), f t :=
    Finset.card_nsmul_le_sum _ _ _ hfc
  rw [nsmul_eq_mul] at hcard
  rw [le_div_iff₀ hc0]
  linarith

end RuleOfX
