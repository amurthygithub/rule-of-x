# Referee report (theory): "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation"

Independent cross-model review of paper1_v1 (PDF, sections/*.tex, appendix_proofs.tex, appendix_proofs_acquired.tex, code/verify_theory.py, code/calibrate_horizons.py, notes/calibration_results.json). No other review file was read. Labels are the LaTeX labels; PDF numbers are given once in brackets.

## 1. Summary

The paper models a firm that buys revenue growth above market growth with expensed spend at diminishing returns, g = G + λσ^α(1 − s/s̄), and pays growth capital k per dollar of new revenue. It derives (i) a concave growth–margin frontier (prop:frontier [Prop. 1]); (ii) the Rule-of-X optimum as a tangency with closed forms (prop:score [Prop. 2]); (iii) saturation, a small-base bound and a demand-pull threshold (prop:saturation [3]); (iv) a "score budget": the time integral of the score above the saturated level is at most (X − k) ln(s̄/s₀) (prop:budget [4], cor:transient [Cor. 1], prop:budget-sharp [16]); (v) envelope results and automation priorities (prop:envelope [5], cor:capital, cor:priorities); (vi) a dynamic result that a value-maximizing firm maximizes a Rule-of-X score at each date with X equal to the marginal value of a dollar of revenue, v′(s), and a separate DCF derivation of the investor's screening weight as a duration (prop:dynamic [6], lem:valuation2 [Lemma 1]); (vii) an industry envelope and a non-identification result (prop:industry [7], prop:industry-full [17]); (viii) a Cournot free-entry limit with a Ricardian rent (prop:entry [8]); (ix) a full-cost ceiling under automation with an accountability floor driven by common-mode control failure (cor:ceiling [Cor. 4], prop:amin [10], lem:fullcost [Lemma 4]); (x) an attainable frontier by date under capacity and risk (prop:attainable [11], prop:expected [12]); (xi) an economic-profit restatement (prop:general [13]); and (xii) a charged score for acquired growth (prop:acquired-score [14]).

I re-derived every proposition and proof in model.tex, appendix_proofs.tex and appendix_proofs_acquired.tex and ran code/verify_theory.py (168/168 checks pass). I found no false mathematical statement in any proposition, lemma, corollary or remark. The issues are of four kinds: (a) hidden or knife-edge assumptions that the statements do not carry (the HJB verification condition, the deterministic reorganization clock, the single exogenous market behind the budget, entry only at date 0); (b) a mismatch between the discrete capacity model of prop:expected(c) and the fluid calibration in Section sec:horizons; (c) overclaims in the abstract and introduction (the "7 to 13" weight, "penalizes capital-intensive growth whatever its return", "cannot spend the budget twice"); and (d) notation and consistency slips (an undefined symbol b in lem:prices, observed-score slopes quoted in sec:model-industry where the paper elsewhere designates the organic frontier as the model-facing estimand).

On novelty: the frontier and tangency are, as the paper says, Marris (1964), Solow (1971) and Odagiri (1981); the growth technology is Vidale–Wolfe and Nerlove–Arrow with a share cap; the closed forms are a routine power-function calculation; prop:envelope, prop:ai, prop:ai-shift, prop:general and prop:acquired-score are identities or immediate envelope statements. The results that are new in substance are the score budget (prop:budget, prop:budget-sharp, cor:transient), the two-weights distinction (prop:dynamic with lem:valuation2), the non-identification and within-firm results (prop:industry-full), the common-mode accountability floor (prop:amin), and the attainable/expected frontier (prop:attainable, prop:expected). The closest modern precedents for the growth technology, customer-capital and market-penetration models (Arkolakis 2010 JPE; Gourio and Rudanko 2014 REStud; Drozd and Nosal 2012 AER; Foster, Haltiwanger and Syverson 2016 AER), and the q-theory of advertising (Vitorino 2014 Mgmt. Sci.; Belo, Gala, Salomao and Vitorino 2022 JFE) are not cited.

## 2. Recommendation

Major revision. The theory is correct and internally consistent, and the verification script does test what the text claims. But for a top field journal the paper must (1) make the verification assumption of prop:dynamic explicit in the statement and in the abstract, or prove existence of a C¹ solution to the HJB; (2) reconcile the discrete capacity model with the fluid calibration, and state the reorganization-freeze convention as an assumption; (3) remove or condition the three overclaims listed below; (4) demote the immediate results (prop:ai, prop:ai-shift, prop:general, parts of cor:priorities, prop:saturation(b)) to remarks and cite the customer-capital precedents; (5) fix the notation and consistency slips.

## 3. Numbered findings

Severity: error, gap, overclaim, unclear, minor.

### Errors (consistency and notation; no false theorem found)

**F1. [error] lem:prices(a) and its proof use an undefined symbol b.**
Location: appendix_proofs.tex, Lemma lem:prices(a) ("with equality if and only if b = 0") and its proof ("that is, b = 0 (given r > 0)").
Issue: b is never defined in the paper. From the proof, φ = u/(u + r k_u) = 1 iff k_u = 0, so b must be k_u; the symbol is the verification script's name for k_u (checks 14b, 14c).
Required change: replace b by k_u in both places.

**F2. [error] sec:model-industry quotes the observed-score (E1) slopes as "the Section 5 estimates" while the paper's model-facing estimand is the organic frontier (E2).**
Location: model.tex, opening paragraph of sec:model-industry: "Section 5 estimates the slope of the upper decile ... at −0.46 (0.14) on the GAAP basis and −0.37 (0.11) after SBC."
Issue: these are the E1 values (\SlopeOp, \SlopeCash in paper1/macros.tex); the abstract, intro and sec:empirics headline the E2 slopes −0.59 (0.16) and −0.43 (0.11) and state that E2 "is the estimand that confronts the model." The numbers here are hard-coded, not macros, and the illustrative calibration that follows (ℓ ≈ 0.86 or 1.14 for an average slope of about −0.4) is keyed to the E1 values.
Required change: quote the E2 slopes (via macros), label E1 as the comparison, and recompute the illustrative ℓ.

**F3. [error] rem:owncompute applies ψ = 0 to server capital while deducting replacement spending in full.**
Location: appendix_proofs.tex, Remark rem:owncompute and its proof.
Issue: the remark charges the owned-server capital k_c G with ψ = 0 ("By Corollary cor:ceiling with ψ = 0") but puts the replacement spending s_srv TCO into a, which is deducted at (1 − τ). Remark rem:taxes states that equipment acquired after 19 January 2025 has ψ = 1. Under ψ = 1 the condition becomes (1 − τ)υ_c > (1 − τ)s_srv L_srv G, i.e. υ_c > 3.3 G: thresholds of 16.5% at G = 5% and 49.5% at G = 15%, not 20.1% and 60.4%. Verified by hand from the remark's own formula.
Required change: either state that ψ = 0 is a deliberate lower bound (as Table tab:ceiling's note does) and report the ψ = 1 thresholds too, or use ψ = 1 for equipment throughout the remark.

**F4. [error] Opening of sec:model says the script checks "every ... inequality claim"; three proved claims are not tested.**
Location: model.tex, first paragraph; code/verify_theory.py.
Issue: the coupling arguments of prop:expected(b) for T_emb and for first-order stochastic dominance in b_p, the free-entry count n* = ⌊Z√(B/F̂)⌋ of prop:entry(c), and the general verification inequality of prop:dynamic(b) (only one closed-loop example, 15l) are not checked. Everything else I traced is tested substantively (e.g. 3j–3l numerically optimize against the closed form; 5a–5d integrate exact share paths; 10b checks dominance point by point; 21a–21h enumerate wave packings; 22a–22e are Monte Carlo).
Required change: soften the sentence to what the script does, or add the missing checks.

### Gaps (hidden assumptions, generality)

**F5. [gap] prop:dynamic(b)–(d) assume, and do not prove, a bounded C¹ solution of the HJB.**
Location: model.tex, prop:dynamic(b) ("Let v̂ ∈ C¹((0, s̄)) be bounded and satisfy ..."), (c) ("Under the conditions of (b)"), (d) ("If a function v̂ as in (b) exists"); abstract ("the weight a value-maximizing firm puts on growth is the marginal value of revenue").
Issue: the verification theorem is correct (I checked (eq:verif), the admissibility of the feedback and the open-loop uniqueness argument). But the central claim that the firm "maximizes, at every date, the Rule-of-X score ... with weight v′(s)" holds only if such a v̂ exists; the paper's evidence is a numerical solution (checks 15g–15l). The problem is one-dimensional with monotone state and strictly concave Hamiltonian, so existence and regularity should be provable (or at least a viscosity-solution statement with a.e. differentiability of v).
Required change: either prove existence (and that v is C¹) or state the verification hypothesis in the proposition's preamble and in the abstract/intro ("under a standard verification condition"). Also state what fails if (eq:gordon) has no root: v(s)/s is then unbounded as s → 0, which is the case ruled out by the "assumed to exist" clause in (d).

**F6. [gap] def:attainable(b) replaces a Poisson freeze process by a deterministic clock; the proof of prop:expected treats this as a derived fact.**
Location: model.tex, def:attainable(b) ("Reorganizations arrive at rate ν^R and freeze the program for T_frz each, which slows its clock by the factor 1 + ν^R T_frz"); appendix_proofs.tex, proof of prop:expected, observation (ii).
Issue: with Poisson arrivals the elapsed program time by calendar t is random (and freezes can overlap); t_R = t/(1 + ν^R T_frz) is its mean to first order. Observation (ii) ("for every plan the law of ϑ_t is the law, in the model without freezes, of ϑ_{t_R}") is therefore a modeling convention, not a consequence of the arrival process as stated. Since n(t_R) is a step function, E n(t_R(ω)) ≠ n(E t_R) in general.
Required change: state in def:attainable(b) that freezes are modeled as a deterministic slowdown of the program clock (a mean-field approximation), and move observation (ii) into the definition.

**F7. [gap] prop:expected(c) is stated for integer n_cap = min_i ⌊Γ_i/c^i⌋, but the calibration's parameters give n_cap = 0.**
Location: model.tex, prop:expected(c); horizons.tex, "Pace"; code/calibrate_horizons.py (pace(): raw = q·ρ·T_par·n).
Issue: under central execution change capacity is 10% of the program a year and T_par = 0.17 years, so a wave can hold 0.82 of one process (of 48) and ⌊Γ/c⌋ = 0: under the proposition as stated nothing is ever attempted. The calibration uses a fluid relaxation (fractional processes per wave) and the greedy-plan equality, which prop:expected(c) establishes only for integer waves with N ≥ n_cap n(t_R). The quantitative pace numbers (23% by 2036, completion in 2033) are therefore not literally outputs of prop:expected(c).
Required change: either state prop:expected(c) for divisible processes (the fractional-knapsack form already used in prop:attainable(d)) or lengthen T_par in the calibration so that n_cap ≥ 1, and say which.

**F8. [gap] The score budget (prop:budget, cor:transient) rests on a single exogenous market with a fixed cap; the text generalizes beyond that.**
Location: model.tex, sec:model-limits intuition ("A firm cannot spend the budget twice"); prop:budget statement ("Hold m₀, G, k and X > k fixed").
Issue: the bound is ∫Δ dt = ln(s_T/s₀) ≤ ln(s̄/s₀). This requires that all excess growth is share growth in one market whose size M grows exogenously at G. A firm that expands its addressable market by new products (endogenous M, the usual software case) has no finite budget in this sense; the paper treats only acquisitions (prop:acquired-score(e)) and churn (rem:assumptions(b)), where the budget is explicitly not finite over time. Also, with m₀ rising over time (the whole premise of sec:horizons) the bound holds pointwise with R_∞(t), which is true but not stated.
Required change: add to prop:budget's preamble that M is exogenous and the firm operates in one market; add a remark on endogenous market creation; qualify the "cannot spend the budget twice" sentence; note the time-varying-m₀ form.

**F9. [gap] prop:entry rests on entry at date 0 only, Cournot with capital treated as rental, and a scarce input growing at exactly G.**
Location: model.tex, ass:entry, prop:entry, intuition paragraph; rem:bertrand.
Issue: the proofs are correct (I re-derived P_n, π_n, L_n, n* = ⌊N_F⌋ − 1, w_n, P = A − BZ, BZ²/n², ρ). But with G > 0 the flow profit π_n e^{Gt} grows without bound, so later entry is strictly profitable for any F; the "entry only at date 0" assumption does all the work in pinning n*. The rental/ownership equivalence holds because output is monotone, which should be said. The abstract's last sentence ("Where entry is free, the limit is set by what stays scarce") is a statement about the F → 0 limit of this one model.
Required change: state the irreversibility/monotone-output argument in ass:entry; say in the intuition that a growing market with later entry would drive L to zero faster, not slower (so the conclusion is conservative in that direction only); qualify the abstract's sentence as a free-entry benchmark.

**F10. [gap] cor:ceiling holds cost shares fixed at given prices; the intuition lists "rents on scarce inputs" as a way to exceed R_max, which contradicts R_max being an upper bound at those shares.**
Location: model.tex, cor:ceiling intuition ("Observed scores above R_max must therefore reflect one of three things: a growth surplus; rents on scarce inputs ...").
Issue: R_max = (1 − τ)(1 − c_c − f − a_min − c_full − δ_K k) + [X − (1 − ψτ)k]G already assigns all residual revenue to margin, so a rent cannot push a saturated score above it except by lowering the cost shares c_c, f (higher prices at given unit costs). The sentence should say so; otherwise the reader cannot reconcile prop:entry(c) (rent ρ) with cor:ceiling.
Required change: replace "rents on scarce inputs" with "cost shares below those assumed (for example because a rent raises price at given unit cost)".

### Overclaims

**F11. [overclaim] "Growth spending implies a weight on growth of 7 to 13" (abstract, intro, sec:empirics, Discussion).**
Location: abstract; intro paragraph 5 ("Second ..."); model.tex "Implication" after prop:dynamic; empirics.tex sec 5.4.
Issue: the inference is σ*/Δ* = α(X − k) from prop:score(b), with the observed ratio 3.3. It rests on three unidentified or proxied objects: α ∈ [0.25, 0.45] (the paper itself says the data do not identify α); all S&M being growth spend (the paper lists this bias); and Δ measured as growth in excess of the sample median, not of market growth G. The third is not listed and biases the ratio upward whenever the median firm itself has positive excess growth (with G at 5–8% instead of 12%, Δ rises and X − k falls to roughly 5–10). The direction (well above 2–3) is robust; the range "7 to 13" is a scenario, not an estimate.
Required change: in the abstract write "if all selling and marketing expense buys growth and the spend elasticity lies in [0.25, 0.45], growth spending implies ..."; add the G-proxy bias to the list in sec:empirics.

**F12. [overclaim] "the cash Rule of 40 penalizes capital-intensive growth whatever its return (Proposition prop:general)".**
Location: intro paragraph 3; prop:general(d).
Issue: prop:general(d) proves this only for k ≥ 1; for 0 < k < 1 growth still enters at the positive weight 1 − k. The intro drops the condition.
Required change: "for k ≥ 1" in the intro, or "under-weights" for k < 1.

**F13. [overclaim] "In value terms the Rule of X is a rule of economic profit" (abstract).**
Location: abstract; prop:general(b).
Issue: prop:general(b) gives R_X = e + (X − k)g + rk: economic margin plus growth at the net weight. The abstract drops the growth term; the intro states it correctly.
Required change: "a rule of economic profit plus growth at the net value of growth".

**F14. [overclaim] Contribution statement and literature relative to customer-capital models.**
Location: literature.tex "Our contribution"; sec:model-setup paragraph after ass:growth.
Issue: the growth technology (spend converts the unsaturated market at diminishing returns, roughly constant markups) is the customer-capital/market-penetration structure of Arkolakis (2010), Gourio and Rudanko (2014), Drozd and Nosal (2012) and Foster, Haltiwanger and Syverson (2016); the "marginal q of revenue" parallels the q-theory of advertising (Vitorino 2014; Belo, Gala, Salomao and Vitorino 2022). None is cited. prop:frontier, prop:score, prop:saturation, prop:envelope, prop:ai, prop:ai-shift, prop:general and prop:acquired-score are immediate given the functional form. The paper's own list of contributions should be narrowed to the budget, the two weights, non-identification/within-firm co-movement, the common-mode floor and the attainable/expected frontier.
Required change: cite and position relative to these; shorten the immediate results to remarks.

**F15. [overclaim] "A firm cannot spend the budget twice" (sec:model-limits intuition).**
Location: model.tex after prop:budget.
Issue: rem:assumptions(b) shows that with G_i < G the budget grows linearly in T, and prop:acquired-score(e) shows that each acquisition buys a new budget. The unqualified sentence in the main text contradicts both.
Required change: "within one market and at given retention, a firm cannot spend the budget twice".

### Unclear

**F16. [unclear] Two "intercepts".**
Location: ass:costs ("m₀ := γ − a is the margin intercept"); abstract and intro ("an intercept equal to the margin a firm earns when it grows with its market"); prop:frontier(b) (m*(G) = m₀ − kG).
Issue: for k > 0 the margin at market growth is m₀ − kG, not m₀. The abstract's "intercept" is the frontier's value at G; the model's "margin intercept" is the operating-margin constant. Both are used as "intercept".
Required change: call m₀ the "operating intercept" or state in the abstract "an intercept equal to the margin net of growth capital".

**F17. [unclear] prop:score(b) calls g* "interior (g* > G)" under "σ* ≤ σ̄", which admits σ* = σ̄, g* = ḡ, the right endpoint of I, where the tangency is one-sided.**
Required change: "σ* < σ̄" for the interior statement, or note the boundary case.

**F18. [unclear] The reference to prop:myopic as "if the firm spends optimally at each date" (sec:model-limits intuition).**
Issue: prop:myopic fixes X and applies the static optimum each date; the dynamically optimal policy of prop:dynamic uses X = v′(s), which falls with s. "Optimally" here means "statically optimally at a fixed weight".
Required change: say so.

**F19. [unclear] prop:amin(b) writes "An all-AI design on one provider has a_min > ..." although a_min is defined as the minimum over all designs.**
Required change: "the floor of any all-AI design on one provider exceeds ...".

**F20. [unclear] Possible double counting between C^itgc_g ("change management including a retest at each model upgrade", ass:layers) and c_mnt ("revalidation at each model upgrade", lem:fullcost(a)).**
Location: model.tex paragraph after def:fullcost ("Each cost is counted once ... the upkeep and revalidation of the builds themselves stay in c_mnt"); ass:layers.
Issue: for an in-scope application the retest of the control and the revalidation of the build at the same upgrade are the same event unless the paper delineates them (control test versus functional revalidation). The sentence asserts no double counting but does not show it; rem:amin-values prices the retest at $100,000 per upgrade inside the ITGC line while tab:fullcost prices revalidation at ϱ_rv c_bld.
Required change: one sentence delineating the two, and confirm that the $1 billion example does not count the same retest twice.

**F21. [unclear] prop:acquired-score(d) sets the zero-spend growth of "the existing base" to G_i = ln NRR after stating that the base contributes (S_sub/S)(NRR − 1) to the firm's growth.**
Issue: G_i = ln NRR is the subscription base's own growth; the firm's zero-spend growth is ln[1 + (S_sub/S)(NRR − 1)] plus the non-subscription base's drift. Section sec:acquired-growth then applies R_∞ = m₀ + (X − k) ln NRR to the firm.
Required change: state the S_sub = S approximation, or give the firm-level formula.

### Minor

**F22. [minor] Notation reuse.** y is X − k throughout the proofs but a loss rate in lem:fullcost(e) ("an event that disrupts the loss rate y"); f is fees but also the local objective in the proofs of lem:timing(c), prop:score(b) and prop:dynamic(d); p is price (lem:prices), 1/(1 − α) (proof of prop:myopic), p_j, p^cm_j, p^emb, p_Y and p_c; δ (rem:assumptions(c)) and δ_K (cor:ceiling) are both depreciation of growth capital. Rename the loss rate and the proof-local functions; unify δ and δ_K or state why they differ.

**F23. [minor] prop:attainable(d) assumes "with X ≥ k" for additivity of R*_X in (m₀, G); additivity holds for every X ≥ 0 since R*_X = m₀ + (X − k)G + Π with Π independent of (m₀, G). Drop the condition or say it is used only to sign ΔR_p.**

**F24. [minor] ass:market says growth rates are continuously compounded and then imposes G > −1, a period-rate constraint; it is needed only for prop:budget(b). Move it there.**

**F25. [minor] prop:amin(c) says the minimized floor "falls with revenue"; the proof shows "nonincreasing". Also prop:saturation(a) says "If X ≤ k, it is constant" after a sentence beginning "If X > k, this is strictly decreasing": fine, but (c) then says "supremum ... not attained" only for X > k; for X ≤ k it is attained everywhere. State it.**

## 4. What I checked and found correct

Re-derived by hand, and cross-checked against verify_theory.py where a check exists:

- prop:frontier (a)–(d): inversion σ = κ(g − G)^β, convexity of the hypograph, dominance iff m < m*(g), right derivative −k, the three curvature cases at g ↓ G, the limits as g → ∞ (checks 1a–1g).
- lem:timing (a)–(c): kg²/(1 + g) gap (0.0346 at k = 0.5, g = 0.3); convexity of m̃ near G for α < 1/2 and k > 0; the corner and interior local maxima of the example (f′(G) = 1 − 1.25/1.21 < 0; interior maximum at g ≈ 0.739) (checks 2a–2f).
- prop:score (a)–(e): existence and uniqueness, Δ* = ℓ^{1/(1−α)}(αy)^{α/(1−α)}, σ* = αyΔ* = (αℓy)^{1/(1−α)}, R* = m₀ + yG + (1 − α)yΔ* = m₀ + yG + C_α(ℓy)^{1/(1−α)}, tangency, corner for X ≤ k, duality and monotonicity of g*(X), Π as a maximum (checks 3a–3m, including numerical global maximization against the closed form).
- rem:cap, rem:r40.
- prop:saturation (a)–(d): dR*/ds = −yΔ*/(s̄ − s) (chain rule through h s̄ = s̄ − s), (eq:rule100), the small-base bound, Λ(R̄) and the Rule-of-1000 example (Λ ≈ 8.71, Δ* ≈ 13.14, σ* ≈ 3.94, m ≈ −3.34) (checks 4a–4f).
- prop:myopic: the ODE ḣ = −Δ₀*(1 − h)h^p, the comparison h^{1−p} ≥ h₀^{1−p} + (p − 1)Δ₀* ŝ₀ t, and the exponent −1/α (check 4g).
- prop:budget (a) and (b): the pointwise bound (R − R_∞)⁺ ≤ yΔ needs only m ≤ m₀ − kg; ∫Δ = ln(s_T/s₀); the discrete log inequality; prop:budget-sharp; cor:transient and its three numerical bounds (1.81, 9.65, 5.01) (checks 5a–5e).
- prop:envelope: all five first derivatives, continuous differentiability across y = 0, convexity in k and in λ, the cross-partial −Δ*/[(1 − α)λ] (checks 6a–6i); cor:capital's exact bracket (6j); cor:priorities (i)–(v), including the 1/α ratio (18a–18c); the depreciation hurdles 3.5 and 7.5 points (17d).
- prop:dynamic: homogeneity and the two value bounds; the HJB reduction (r − G)v = s max{m₀ − σ − kG + (v′ − k)ℓσ^α}; the verification inequality (eq:verif); the identity maximand = R_X − XG at X = v′(s); in (d) the root, g° < r from simplicity, v₀ = m°/(r − g°), the upper bound v(s) ≤ v₀ s via ŵ = v₀ s, the constant-policy lower bound by monotone convergence, and v′(s) → v₀; the worked example (λ ≈ 0.070 → v₀ = 10, g 7.6%, spend 10.7%, margin 24.3%) (checks 15a–15n).
- lem:valuation2 (a)–(d): ∂η/∂g = η/(1 + g), (eq:X2), D as an exponential-family mean with dD/d ln η = Var(t), the sign of d(N/D)/dθ, the Gordon limit (checks 7a–7g, 16a); the numerical examples (X = 2 at m = 0.25, D = 10, g = 0.25; D = 10.25 at T = 15 and 6.53 at T = 10; 1.8/2.8 at θ = 1/2 and 5.4/6.2 at θ = 0).
- prop:industry (i)–(v) and prop:industry-full (iv), (v): the locus (eq:locus), the quality condition, Φ = m*_ω̄, Ψ flat, the quantile argument via ω_χ(g) = H⁻¹(χ + (1 − χ)H(ω(g))), the sup identities in (iii), the two-type example ((0.21, 0.27), (0.53, 0.37), slope +0.31), the ℓ′(Δ) construction for arbitrary (α′, X′), the within-firm slope formula (eq:bW) and its example (L = 0.425, 83%) (checks 13a–13h, 19a); rem:segments.
- prop:entry (a)–(c): best responses, P_n, π_n, L_n, the ownership/rental present-value equality, k_n = k_u/P_n, m = (r − G)k_n + L_n, n* = ⌊N_F⌋ − 1 and the bound on L_{n*}, the F → 0 limit, w_n, P = A − BZ, BZ²/n², ρ = 1 − ĉ/(A − BZ) (checks 8a–8p); rem:bertrand.
- lem:prices (a), (b) (checks 9a, 9b, 14a–14c); prop:ai (10a); prop:ai-shift (a) both cases and (b) (10b, 10c).
- rem:taxes: the after-tax margin, the four substitutions, (1 − τ)κ, (eq:psiT) with ψ₅ = 0.796 and ψ₁₅ = 0.532 (11a, 11b, 25a).
- cor:ceiling and Table tab:ceiling: all rows, G* = 1 − base at k = 0, the ψ and δ_K adjustments, the central margin term 0.82 × 0.7041 = 0.5774 (11c–11h, 20a–20m); Table tab:fullcost and lem:fullcost (a)–(e) including the risk-cost identity (c₀/L)(1 + L + ln ξ), the Gordon–Loeb 1/e bound, the capped Pareto mean, and the common-mode expression (26a–26f).
- prop:amin (a)–(c) and rem:amin-values ($2.01M, $1.70M, $1.02M; 0.24% floor; 9 and 6 applications) (27a–27c, 25d, 25e).
- prop:attainable (a)–(d), including the fractional-knapsack bound and the speed limit inequality chain (21a–21h); prop:expected (a), (c), (d) and the garbling/superposition couplings in (b) (22a–22e); lem:expected-frontier (22f); rem:regimes (24a, 24b); the pace numbers q = 0.34 and 0.74, 3.0% and 14.5% a year, 23% by 2036 and completion in 2033 (22g; recomputed from calibrate_horizons.py's pace()).
- prop:general (a)–(d) and the k = 1.5 example (−7.5 points; −0.5 per point of growth) (23a–23d); rem:owncompute's algebra under its own ψ = 0 convention (20k).
- appendix_proofs_acquired.tex: prop:acquired-score (a)–(f) and the CRF inequalities of rem:acquired-bounds.
- rem:assumptions (a)–(d) and the list of which proofs use monotone h (17a–17e).
- Figures fig:frontier and fig:saturation are generated from the closed forms with the parameters stated in their captions (code/frontier_figures.py).
- The abstract's quantitative claims (42%; 26–72%; 23% by 2036; 2033) match calibrate_horizons.py and macros.tex.

Not independently verified (outside the theory remit): the empirical slopes, the anchor firm-years, and the parameter sourcing in the assumptions register.
