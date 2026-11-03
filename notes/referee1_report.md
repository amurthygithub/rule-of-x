# Referee 1 report: economic theory

**Version reviewed:** the LaTeX sources as of 23:28. Sections 5 and 6 and Table 10 were revised after `paper.pdf` was built at 22:20; page numbers refer to that PDF.

## Summary
Growth above market growth is bought with spend, g = G + λσ^α h(s). This gives a concave frontier between growth and FCF margin, with Rule-of-X lines as its supporting lines and R* = m0 + (X−k)G + Π. Extensions cover saturation, a score budget, capital envelope results, a duration foundation for X, a selection account of the cross-section and a free-entry limit. Upper-tail statistics for 579 SEC filers anchor ceilings for 2028–2036.

## Recommendation: major revision
I re-derived Propositions 1–8, Lemmas 1–3 and Corollaries 1–3, and checked the closed forms numerically on 3,000 random draws: the largest relative error is 4×10⁻¹⁵ (scripts in `notes/referee1/`). The algebra is correct. The problems are internal consistency after the revision, the concept behind the Rule-of-X weight, and the calibration anchor.

## Major issues

**1. ERROR: the front matter contradicts the revised Sections 5–6.**
- *Still in the abstract, §1 and §8:* a flat frontier; scores of 85–130 that "fall steeply" with size; a cash score "halved" by capital intensity; α estimated at 0.2–0.45; 121–220 in 2028; "40 to 60 times" the typical demand pull.
- *Revised Sections 5–6:*
  - The edge score is dropped; it moves 36–75 points with the minimum cell size.
  - The upper-decile slope is −0.25 (GAAP) and −0.16 (cash).
  - The scale effect is "modest", and the capital penalty is 14 points.
  - α is not identified.
  - Table 10 gives 49–164 for 2028; a Rule of 1000 needs 7–13 times the best firm's pull.
- *Also out of date:* the "Calibration of α" paragraph in §3.1, the opening of §3.7, §7.5, and "it is flat" in §8.
- *Fix:* rewrite these passages and recompile.

**2. The Rule-of-X weight uses the wrong margin of substitution (§3.6, Lemmas 2–3, §5, §7.1).**
- *The problem.* Lemma 2 prices a *permanent T-year* change in growth, but the frontier choice is made each period at the current share.
- *What the model implies.* With V = M·w(s), the Hamilton–Jacobi–Bellman equation r·w/s = max_σ{m0 − σ − kg + G·w/s + w′(s)Δ} shows that the firm maximizes R_X with X = w′(s): the marginal q of revenue, close to EV/S at small share (Hayashi 1982).
- *Size of the gap.* In the paper's own example (r = 0.10, g = m = 0.25, T = 10, with terminal value), the weights are 1.8 (permanent) and 13.1 (one-period).
- *The data agree.* Revised §5 reports σ/Δ ≈ 2.5, so α(X−k) ≈ 2.5, and α ≤ 0.45 then gives X ≈ 5.6–10.
- **ERROR:** calling this "consistent with weights of two to three" requires α ≈ 0.8–1.25.
- *Fix:* derive the dynamic first-order condition, separate the firm's weight (marginal q) from investors' screening weight, and derive or drop "two to three".

**3. The calibration anchor contradicts the paper's data (Table 10, §6.2).**
- **(a) ERROR: the intercept is infeasible.** m0 = 28 is φ₀.₉₅(0), a quantile across firms. Since m ≤ m0, a firm-year with m > 28 is infeasible at that intercept. In 2023–25, 18 of the 42 firm-years at or above the 95th-percentile score have FCF-after-SBC margins above 28 (among them VeriSign, Gen Digital, AppLovin and Palantir). This holds whatever α and σ are.
- **(b) The durable–transient split is not identified, and the data lean against it.** Inverting those firm-years one by one, with σ = S&M share (an upper bound) and k = capex intensity, gives a median m0 of about 49, R∞ of about 58 and Π of about 3. Even with σ = 0, 26% of them have (1−k)(g−G) below the low-end Π of 9. Scaling Π by μ^{1/(1−α)}, up to 3.5 times, is what yields the 2028 upper end of 164.
- **(c) The tail is not a clean measure.** If firms act on X ≈ 6–10 (Issue 2), they overspend relative to the R_1 optimum, and R_1 − R∞ = Δ(1 − k − α(X−k)) < 0.
- **(d) The paths are assumed.** The (m0, G, μ) paths do not come from the model's dynamics, and at g* = 209% the gap between continuous and period growth rates is first order.
- *Fix:* invert the model firm by firm, or use simulated method of moments on (g, m, S&M); run the model's dynamics forward from 2025 shares; state the units of growth; and round.

**4. Assumptions doing hidden work (Assumptions 2–5).**
- **(a) No operating leverage**, although the paper's own quantile regressions show margins rising 4–7 points per log unit of revenue. With a = a_v + F/S, R∞ rises with S, which confounds the scale test (size is not share).
- **(b) A common zero-spend G with no churn.** In SaaS, zero-spend growth is firm-specific net revenue retention, and Remark 3 shows that heterogeneous G_i break the downward slope of Φ.
- **(c) k ≥ 0 with no depreciation.** Deferred revenue makes cash capital intensity negative, adding about 9–15 points at G = 30%. GPUs depreciate at 20–33% a year, which raises Corollary 2's "1 point at 10% growth" to about 3.5.
- **(d) Decreasing h rules out the network effects** that §6.4 lists. Proposition 3 needs decreasing h; Proposition 4 does not.
- *Fix:* add a fixed cost, net deferred revenue out of k, make depreciation explicit, allow G_i to differ, and state which results survive.

**5. Overclaiming (abstract, §1, §6.3–6.4, §8).**
- **"The limit is set by what stays scarce."** This holds only under free entry; at given prices, R_max rises one-for-one with automation (Corollary 3). It is standard zero-profit logic, as in Aghion, Jones and Jones (2019). State the condition and cite them.
- **"Above about 33%".**
  - This is the favorable case with k = 0; with a compute share of 5% the threshold is about 22%.
  - Prices are held fixed while compute costs fall 5 to 50 times a year.
  - G is addressable-market growth, so comparing it with Epoch's scenarios for aggregate growth is a category error.
- **"At most about a year".** This holds only for s0 = 1%; at s0 = 10⁻⁵ the bound is 5 years. Headline the formula in Proposition 4 instead.
- **"Necessary conditions".** These are levers; only the joint condition R∞ > 1 is necessary.
- **"Limited by growth opportunity".** This is not identified (Proposition 6(iv)).

**6. Positioning and length.**
- *Antecedents.* The tangency frontier is Marris, Solow (1971) and Odagiri (1981); the growth technology is Vidale–Wolfe (1957) and Nerlove–Arrow (1962); σ* = α(X−k)Δ* is a Dorfman–Steiner (1954) condition; the duration link follows Dechow, Sloan and Soliman (2004).
- *Claims.* Replace "has no theory" with the real contributions: the Rule-of-X reading, the score budget, non-identification and the mapping of AI effects onto parameters. The "AI-growth" link is a reduced-form mapping without task structure. The Markowitz framing misleads, since the object is a transformation curve with a price line.
- *Length.* Of 46 pages, 14 are the model. Move Lemma 1(b–c), Proposition 3(e), Proposition 4(b), Lemma 2 (fold it into Lemma 3), Proposition 6(iv–v), Remarks 3–4, Lemma 4 and Proposition 8(a–b) to the appendix. Cut §2.1's empirical paragraph and §2.5 to two sentences each.

## Errors
- **E1 (§6.3, p. 27).** "G = 0.10 … cost of capital of 9%" violates r > G (Assumption 6).
- **E2 (§6.3, §1).** "A rent of 60 to 80 points" is wrong: R = G + (r−G)k + ρ = 1 requires ρ ≈ 0.90, and after tax the score is unreachable, since ρ < 1.
- **E3 (Appendix C).** "Added Proposition 5" should read Proposition 6.
- Also flagged as errors above: Issues 1, 2 and 3(a).

## Minor issues
1. Notation clashes: α, τ, m, ρ and D each carry two meanings.
2. Scores pair backward g_t with FCF_t, which is the timing of Lemma 1(b). For capex-led firms, also report g_{t+1} + m_t.
3. Proposition 7: entry occurs only at date 0, and input supply grows at exactly G, a knife-edge case. State both.
4. The revised cross-section no longer needs selection. A common frontier with α = 0.25 and ℓ = 0.85–1 has an average slope of −0.13 to −0.24 over Δ ∈ [0, 0.5]; only the within-firm sign needs Proposition 6(v).
5. §5: the log–log slope is one under variation in ℓ, but α under variation in X.
6. §5: capital leaves operating margins unaffected only at fixed σ, and σ* falls with k.
7. §6.3: "35 to 45" mixes ψ = 0 and ψ = 1; Table 3 (ψ = 0) gives 45.
8. α differs across examples: 0.30, 0.35 and 0.25–0.45.
9. The calibration ignores the tax-adjusted pull (1−τ)^{−α}λ.
10. Abstract: only the maximal iso-score line is tangent; drop the protocol sentence.
