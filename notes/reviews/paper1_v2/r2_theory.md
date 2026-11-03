# Round-2 referee report (economic theory): "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation", version 2

Scope: the model (main paper Section 3 and Appendix A; Supplementary Appendix S1 to S5, including every proof in S3 and S4), the use of the theory in Sections 6 to 9, the match between the abstract, introduction and conclusion and what is proved, the positioning in Section 2, and `code/verify_theory.py`. Pages are those of the v2 build (M = main paper, S = supplement). I read the two round-1 theory reports (`referee1_theory.md`, `fable_referee_theory.md`) and the authors' response; no other round-2 report. Every status below was checked in the paper or the code, not in the response. The verification script was run on a copy in my scratch directory (`/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_theory/`), and my own checks are in `r2_checks.py` there.

## 1. Summary and recommendation

The revision does what the round-1 theory reports asked, with two exceptions the authors declare (existence of the HJB solution, a few citations and renames) and a handful of small slips it introduces. Of the 51 round-1 theory findings (26 from Referee 1, 25 from the cross-model referee), I count 46 resolved, 5 partly resolved, none unresolved. The four statements that were false in v1 are now true as stated: the program clock is an assumption with disruptions in calendar time and a corrected embedding probability, plus a random-freeze version (Prop. 7(f)) that proves the round-1 counterexample; partial realization is a property of the process, so the convergence-level claim follows (Prop. 7(d)); the ceiling is a bound at its cost structure with an explicit scope statement (Cor. 4(a)); and the timing lemma gives the right conditions (Lemma S1(d)). The decision-weight result is now a verification theorem under a named hypothesis (H), and every downstream statement I could find is conditioned on it. The free-entry result has customer capital, a date-0 entry assumption, an ownership/rental equivalence stated for monotone output, and a new full-cost bound on the rent (Prop. 4(d)). The accountability floor is a pass/fail constrained minimum with a cross-type common cause (Prop. 5), and its worked numbers reproduce. The ψ convention is unified and Remark 7's thresholds at ψ = 1 (16.5% and 49.5%) are right.

I re-derived every proposition, lemma, corollary and remark that is new or changed (Props. 1(c), 2(b) to (e), 4(a) to (d), 5(a) to (d), 7(a) to (f), 9; Cors. 1(b), 3(ii) to (iii), 4(a) to (c); Lemmas 2(b), 5(e), 6(e), S1(d), S3; Remarks 2, 3, 7, S1(b), S4, S6) and found them correct, with one exception in a proof (Finding 2 below) and one in the abstract's wording (Finding 1). `verify_theory.py` passes 189 of 189 checks in 5 min 53 s on my copy; the new section-28 checks are substantive (Monte Carlo of the exact claims, including the round-1 counterexample, selective reversion with fixed and redrawn shares, the T_emb and share-dominance couplings, random freezes, and the scope of the ceiling), and the stale checks and draft residue are gone.

What remains is small: an abstract sentence that double-counts the capital charge, a proof step in Cor. 4(c) that asserts an implication which fails for processes that change λ or k, a calibration sentence that cites Prop. 7(e)(iii) outside the case in which it is proved, a slogan in the abstract and conclusion ("not by what is automated") that the paper's own Prop. 4(c) to (d) contradicts for input owners, and several notation and wording slips. None needs a new result.

**Recommendation: minor revision.** Counts of new findings: error 2, gap 1, overclaim 3, unclear 4, minor 8 (18 in all).

## 2. Status of the round-1 theory findings

Status: resolved / partly / not resolved. "Evidence" is what I checked in the paper, supplement or code.

### Referee 1 (theory), Findings 1 to 26

| ID | Round-1 finding | Status | Evidence |
|---|---|---|---|
| R1-1 | Program clock not implied by random reorganizations; Prop. expected(a),(c) fail; hazard clock inconsistent | Resolved | M Def. 4(b) p.29: "We assume that freezes slow the program's clock uniformly"; disruptions "in calendar time, so a flight lasts (1+ν^R T_frz)T_emb in calendar time", p^emb = ϖ exp{−ν_D(1+ν^R T_frz)T_emb}. M Prop. 7(f) p.31 and its proof S p.21: t̃(t)/t → 1/(1+ν^R T_frz) a.s., R̄_X(t) ≤ E R^att_X(t̃(t)), count bound ϖe^{−ν_D T_emb} n_cap E n(t̃(t)), survival exp{−ν_D T_emb − ν^R T_emb(1−e^{−ν_D T_frz})} ≥ uniform-clock value (re-derived; 1−e^{−x} ≤ x), and the round-1 counterexample (e^{−0.5} ≈ 0.61 at t = 1.5) reproduced in the proof and in check 28o. Intuition now "approximately like a cut in the program's pace" (M p.31). The corrected p^emb is moot in the calibration, which no longer applies the hazard (M p.53-54). |
| R1-2 | "Partial realization lowers the converged level" false under free retry | Resolved | M Def. 4(b) p.29: "the share is a property of the process, so a later migration of the same process realizes the same b_p"; S2.7 p.7 gives the grounding; M p.31 intuition states it as an assumption and says what fails without it. Prop. 7(c) "also for plans that revert processes and try again" and 7(d) proofs (S p.20) use shares drawn at date 0 (observation (iii)); check 28p simulates both conventions. |
| R1-3 | Cor. ceiling bounds a firm at the full-automation cost structure only | Resolved (one proof step imprecise, Finding 2) | M Cor. 4(a) p.28: R_∞ ≤ R_max iff c′_h + c′_c + f′ + a′_op ≥ c_c + f + a_min + c_full; "a firm whose costs are leaner than that structure ... can have R_∞ > R_max". Cor. 4(c): limit max_Z R_∞(ϑ_Z). Intuition p.28 lists the fourth explanation ("a cost structure leaner than the scenario's, in particular a compute share below c_c"). M §7.2 p.49 and §8.3 p.60 repeat the scope. Re-derived (a) from Remark 2. |
| R1-4 | "α < 1/2 is exactly the range where timing matters" false | Resolved | S Lemma S1(d) p.3: α = 1/2 convex exactly on (G,(k/κ)^{1/3}−1), nonempty iff k > κ(1+G)^3; α > 1/2 convex where 2k(g−G)^{2−β}/(1+g)^3 > β(β−1)κ; asset-light sliver ends at Δ ≈ 0.021 (I reproduce 0.020 to 0.021). M §3.1 p.11-12 reworded. Check 28a reproduces the round-1 scan (convex on (0.100, 1.08), interior maximum at g ≈ 1.16). |
| R1-5 | Prop. dynamic(b) to (d) assume a bounded C^1 HJB solution | Partly (as the response says) | M Prop. 2(b) p.18 names hypothesis (H); (c) "Under (H)"; (d) last sentence conditional; new (e) for no root; p.19: "We have not proved (H)." Conditioning carried to the abstract p.1, M §1 p.2, §3.5 intuition p.17, §7.4 p.56, §8.1 p.59, §8.6 p.62. Proof S p.12-13 adds the ODE form and both singular points (I re-derived ∂Φ/∂u = (r−G)/Δ° > 1). Neither existence nor the Pontryagin restatement is supplied. |
| R1-6 | Two weights are one MRS at different persistence | Resolved | M Lemma 5(e) p.19: T = 1, θ = 0 gives X^scr = (m+m̄M_∞)/(1+g) = (V/S_0)(1+r)/(1+g)^2 (re-derived; 3.0229 in the example, check 28f). M p.19-20: "the same object ... evaluated for perturbations of different persistence"; "a weight of 2 to 3 reflects a choice of persistence, not a prediction". "Coincide approximately only when" deleted. |
| R1-7 | "7 to 13" is 3.3/α over an unsourced α range | Resolved | Withdrawn: M §3.6 p.19 ("The spend data therefore do not identify the decision weight"), §5.4 p.40 (α(X−k) from 0.05 to 10.1), abstract p.1 ("the data do not identify the weight firms act on"), §8.1 p.59. α-free bound X − k > σ*/Δ* stated (M p.19). |
| R1-8 | Iso-score, not iso-value | Resolved | M §1 p.2 "price lines, or iso-score lines"; §3.3 p.12 "its level sets are iso-score lines, not iso-value lines (Remark 3(c))"; Remark 3(c) p.32: a parallel family contains exactly one iso-value line; tangency at the small-share point (re-derived). |
| R1-9 | Economic-profit "generalization" is a change of variables (Marris) | Resolved | M §3.11 p.32-33: "an exact change of variables, so it does not widen the model's domain"; Remark 3 text: "it adds no result"; Marris (1963, 1964) and Gordon (1962) cited for (c); (d) says k > 1 / k = 1 / 0 < k < 1; (b) q_K "a label" for X ≠ X^dyn. M §1 p.2 now points to Remark S4 for what carries beyond software. |
| R1-10 | 1/α advantage is a unit artifact; stage ranking not at fixed X | Resolved | M Cor. 3(ii) p.17 gives both measures (xσ* and xσ*/α) and says the factor "reflects only the unit"; (iii): "at a fixed weight the gain does not depend on the firm's share or growth"; intuition conditions the stage ranking on X^dyn(s) falling with share. §7.4 p.56 and §9 p.63 say "For a firm whose decision weight falls with share". |
| R1-11 | General concave φ versus isoelastic | Resolved | S Remark S4 p.3-4 with proof p.9-10 (re-derived (a) to (c): slope at G is −k − 1/(ℓφ′(0+)), spend ratio (X−k)ε(σ*)); check 28c. |
| R1-12 | Budget needs zero-spend growth ≥ G | Resolved | M p.15 preamble and Prop. 1 statement ("let its growth be at least G whatever its spend"); S Remark S1(b),(d) p.1-2; abstract "within one market"; M p.16 "Within one market, and with zero-spend growth at least equal to market growth". |
| R1-13 | Hidden assumptions (no harvesting; fixed share in attainable frontier; additivity; independent disruptions) | Resolved | (a) M §3.1 p.10 ("growth cannot be traded below G for margin"); (b) M p.29 after Ass. 8 and §7.3 p.52 ("describes one firm type: the attainable frontier is taken at a fixed share"), Table 6 note p.55; check 28s computes the implied starting share; (c) Ass. 8 p.29 ("Increments are additive"); (d) S2.7 p.7 (independent across attempts; common disruption leaves (c),(e) unchanged, raises variance). |
| R1-14 | Growth-rate convention at extreme scores | Resolved | S2.1 p.5: technology holds in one convention; log-rate frontier turns convex in annual rates beyond β−1; which results use which; headroom binds at several hundred points. M §3.1 p.10 points to it; Lemma 3 example says "in continuously compounded rates" (p.14). |
| R1-15 | Taxes: replacement deducted at once; Remark owncompute at ψ = 0; δ versus δ_K | Resolved | M Remark 2 p.25: replacement "takes the same ψ: its after-tax cost is (1−ψτ)δ_K k"; m = (1−τ)(m_0−σ) − (1−ψ)τδ_K k − (1−ψτ)kg (re-derived; check 28l). Remark 7 p.72-73 at ψ = 1 with ψ = 0 as sensitivity (16.5/49.5%; 33/74%), re-derived. δ_K used in Remark S1(c) and Cor. 4; but see Finding 12 (δ reappears in Prop. 9 and Table 7). |
| R1-16 | Model section hard-codes E1 slopes | Resolved (superseded) | M §3.7 p.20 quotes Ψ_χ slopes −0.22 and −0.16 and S2.3 p.6 gives the mapping ℓ = (S_β/b)^α (re-derived S_β = 6βW^{β−1}/[(β+1)(β+2)] and the 2.3 to 5 factor). |
| R1-17 | "Embeds 23%" is the benefit-weighted share | Resolved | M abstract, §1 p.3, §7.3 p.54, Table 5 (column "Realized b̄E"), §9: "realizes about 41% ... having embedded about 61%". Arithmetic reproduced (E = 0.607, b̄E = 0.407). |
| R1-18 | verify_theory.py gaps | Resolved | Checks 28n (calendar-time disruptions under the uniform clock), 28o (Poisson freezes), 28p (selective reversion, both conventions), 28q (T_emb and FOSD couplings), 28i (verification inequality on random policies), 28f (Remarks S2, S3, D in r); "[arithmetic]" labels; 11c/11e and the "previous Table" residue gone; title updated; M §3 opening p.9 states what is checked. Run time in the docstring ("three to four minutes") is still below the 5 min 53 s I observe (trivial). |
| R1-19 | Uncited precedents; novelty overstated | Partly (as the response says) | M §2.1 p.5 (Arkolakis; Gourio-Rudanko; Drozd-Nosal; Foster et al.; Vitorino; Belo et al.; Sethi 1973, 1977; Feichtinger et al.; Dorfman-Steiner), §2.2 (Marris-Gordon valuation ratio), §2.5 p.8-9 (Mankiw-Whinston; Mosleh et al.; Hokstad-Rausand; Eckhardt-Lee; Littlewood-Miller; Knight-Leveson). Elementary results demoted to Lemmas 1 to 4 and Remarks 1, 3; contribution narrowed (M §1 p.3, §2.7 p.9, §3 opening p.9). Baumol-Panzar-Willig not cited (declined). |
| R1-20 | G_i = ln NRR inconsistent | Resolved | M Prop. 8(d) p.44: G_i = ln(1+a), a = (S_sub/S)(NRR−1) + (1−S_sub/S)γ_ns; equals ln NRR only if all revenue is subscription; proof S p.23. Caveat that retention is not literally zero-spend in S Remark S1(b). |
| R1-21 | Undefined b in Lemma prices | Resolved | S Lemma S2(a) p.5 and proof p.16: "k_u = 0". |
| R1-22 | Draft residue (0.6928 etc.; a_min = 6%) | Resolved | grep of the frozen source and script finds none; checks 11c/11e removed. |
| R1-23 | Notation clashes | Partly (as the response says) | Fixed: application index g → a, o; loss rate y → x; growth surprise ν_t → g̃_t, z_3; μ, ξ in Prop. S3(iv) → ϒ, ξ; E_t → Z^e_t; H → F_Ω; start date s → t_0; m̄_t → m^E_t; a_min wording in Prop. 5(b). Kept and listed in Table S1: θ/ϑ, process index p beside price (now capital P in Prop. 4), ξ/ξ_exp, μ. New slip: δ for δ_K in Prop. 9 and Table 7 (Finding 12); F for both the feasible set and the replication cost in Table S1. |
| R1-24 | Overstatements in attainable-frontier text | Resolved | M p.31: "the attainable score itself need not be concave, because the packing is in whole processes"; S Remark S8(iii) p.7: "weakly shrink ... weakly lower". |
| R1-25 | Budget sharp only for slow growth; continuous-time corollary | Resolved | M Cor. 1(b) p.16 with both bounds (0.43 and 0.30 years, re-derived); M p.14 "a myopic policy, not the dynamically optimal one of Proposition 2"; proof S p.11 explains the asymmetry. |
| R1-26 | Abstract wording (intercept; concavity) | Resolved as asked, but the intercept fix collides with FT-16's (Finding 1) | Abstract p.1: "concave when capacity is installed ahead of the revenue it serves"; "plus market growth net of the capital it requires". |

### Cross-model theory referee (Fable), F1 to F25

| ID | Round-1 finding | Status | Evidence |
|---|---|---|---|
| FT-1 | Undefined b in lem:prices | Resolved | As R1-21. |
| FT-2 | E1 slopes quoted and ℓ calibrated to them | Resolved | As R1-16; S2.3 p.6 mapping. |
| FT-3 | rem:owncompute at ψ = 0 with replacement deducted in full | Resolved | As R1-15; check 20k, 20k2. |
| FT-4 | Script does not check every inequality claim | Resolved | Checks 28i (verification inequality, 40 random policies), 28q (T_emb and FOSD couplings), 8h (n* by brute force, already present); M §3 opening p.9 softened to what is done. |
| FT-5 | Bounded C^1 HJB solution assumed | Partly | As R1-5; part (e) added for the no-root case (re-derived; check 28g). |
| FT-6 | Deterministic clock replaces Poisson freezes; proof treats it as derived | Resolved | M Def. 4(b) states it as an assumption; proof observation (ii) now reads "Under the uniform clock" (S p.19); S2.7 p.7 calls it a mean-field reading with Prop. 7(f) as the long-run limit. |
| FT-7 | Calibration uses a fluid relaxation the proposition does not cover | Resolved (see Finding 3 for the ν_D = 0 caveat) | M Prop. 7(e) p.30-31 (divisible program), proof S p.20-21 (re-derived (i) to (iii)); M §7.3 p.53: "Proposition 7(e), the version for a divisible program"; check 28m confirms the calibration formula s = b̄ min{1, q ρ T_par n(t_R)} and the fill condition under central execution. |
| FT-8 | Score budget assumes one exogenous market | Resolved | M Prop. 1 p.15 preamble ("single market whose size grows exogenously at rate G, with a fixed share cap"); (c) moving intercept; intuition p.16 lists the three ways the budget is not finite; abstract "within one market". |
| FT-9 | Free entry: date-0 entry, rental capital, input growth at G | Resolved | M Ass. 6 p.22: "Entry is possible only at date 0; later entry ... is ruled out"; ownership/rental equivalence "along every nondecreasing output path"; S2.4 p.6 discusses the three assumptions and the direction of the bias. |
| FT-10 | Rents listed as a way to exceed R_max | Resolved | M Cor. 4 intuition p.28: "higher prices at given unit costs, for example from a rent on a scarce input, which lower every cost share"; Prop. 4(d) p.23 bounds the rent by the ceiling. |
| FT-11 | "7 to 13" rests on α, all S&M, median-based Δ | Resolved | M §3.6 p.19 lists all three; §5.4 p.40 reports fixed-G variants (2.1 to 2.7). |
| FT-12 | "Penalizes growth whatever its return" holds for k > 1 | Resolved | M §1 p.2 "for capital intensity above one"; Remark 3(d) p.32. |
| FT-13 | "A rule of economic profit" drops the growth term | Resolved | Abstract, M §1 p.2, §9 p.62: "economic profit plus growth at its net value". |
| FT-14 | Customer-capital, penetration and q-theory precedents uncited; immediate results as propositions | Resolved | As R1-19; M §2.1 p.5: "Our growth technology, its first-order condition for spend and the reading of the multiplier as the marginal value of a customer are therefore not new". |
| FT-15 | "Cannot spend the budget twice" | Resolved | M p.16: "Within one market, and with zero-spend growth at least equal to market growth, a firm cannot spend the budget twice." |
| FT-16 | Two "intercepts" | Resolved in §3.1 (M p.11: "the margin at market growth" for m_0 − kG), but the abstract is now internally inconsistent (Finding 1) | M p.11; abstract p.1. |
| FT-17 | Interiority at σ* = σ̄ | Resolved | M Lemma 2(b) p.12-13 parenthesis. |
| FT-18 | "Optimally at each date" for the myopic path | Resolved | M p.14 and Cor. 1(b). |
| FT-19 | a_min wording in prop:amin(b) | Resolved | M Prop. 5(b) p.26: "an all-AI design on a single provider j can be admissible only if ...". |
| FT-20 | ITGC retest versus c_mnt revalidation double count | Resolved | S2.5 p.7 delineates the two; Remark 6 p.72 prices the retest at control testing only ($24,000). |
| FT-21 | G_i = ln NRR | Resolved | As R1-20. |
| FT-22 | Notation reuse (y, f, p) | Partly (as the response says) | y and f renamed (x for the loss rate; S for the local objective in Lemma S1's proof); p kept and listed. |
| FT-23 | Needless X ≥ k in attainable(d) | Resolved | M Prop. 6(d) p.30: "for every X ≥ 0". |
| FT-24 | G > −1 belongs in budget(b) | Resolved | M Ass. 1 p.10 no longer has it; Prop. 1(b) p.15 "with G > −1". |
| FT-25 | "falls" should be "nonincreasing" | Resolved | M Prop. 5(d) p.27 "nonincreasing in S"; Lemma 3(c) p.14 states the X ≤ k case. |

## 3. New findings

Severity: error / gap / overclaim / unclear / minor.

### Finding 1 (error, wording). The abstract's closed form double-counts the capital charge on market growth

**Location.** Abstract, M p.1, sentences 2 and 3.

**Issue.** The abstract says the frontier has "an intercept equal to the margin at market growth", which Section 3.1 (p.11) defines as m_0 − kG, and then gives the maximal score as "the intercept, plus market growth net of the capital it requires, plus a growth surplus". Read with the abstract's own definition, that is (m_0 − kG) + (X − k)G + Π, which is off by kG from R*_X = m_0 + (X − k)G + Π (eq. (7)). The introduction (p.2) avoids the problem by writing "the margin intercept" (m_0) in the closed form; the abstract does not. The error comes from applying the fixes for R1-26 and FT-16 to the same sentence.

**Evidence.** With the parameters of Figure 1 (m_0 = 0.45, k = 0.10, G = 0.10, X = 1, ℓ = 0.6, α = 0.3): R* = 0.7133; the abstract's reading gives 0.7033 (`r2_checks.py`, block 3).

**Required change.** Either "the margin intercept, plus market growth net of the capital it requires, plus a growth surplus" (keeping "intercept equal to the margin at market growth" for the frontier), or "the margin at market growth, plus the weighted value of market growth, plus a growth surplus".

### Finding 2 (error, low impact). The proof of Cor. 4(c) asserts that Def. 4(c) implies "X-improving at saturation", which is false when a process changes λ or k

**Location.** M Cor. 4(c) p.28 ("this equals R_max when every process is X-improving (Definition 4(c))"); proof, S p.17 ("a process is X-improving at saturation if and only if δm_0p − Gδk_p + (X−k)δG_p ≥ 0, which Definition 4(c) implies").

**Issue.** Def. 4(c) evaluates ∇R*_X · δϑ_p = δm_0 − g*δk + (X−k)(Δ*δlnλ + δG) at the firm's current share, where Δ* > 0 and g* > G. At saturation the gradient is (1, −G, 0, X−k). A process with δlnλ > 0 and a small δm_0 < 0 satisfies Def. 4(c) at any share with headroom and lowers R_∞; a process with δk < 0 and δm_0 < 0 can satisfy Def. 4(c) and fail at saturation. The implication holds only for processes that change m_0 and G alone, which is the case the calibration uses, so the numbers are unaffected.

**Evidence.** m_0 = 0.4, k = 0, λ = 1, G = 0.1, X = 1, s/s̄ = 0.1, α = 0.3; process (δm_0, δlnλ) = (−0.01, 0.5): gradient at the current share +0.247 (R* rises from 0.860 to 1.224), gradient at saturation −0.010 (R_∞ falls from 0.500 to 0.490). `r2_checks.py`, block 1.

**Required change.** In Cor. 4(c), replace "X-improving (Definition 4(c))" by "X-improving at saturation, that is, δm_0p − Gδk_p + (X−k)δG_p ≥ 0 for every p", and in the proof replace "which Definition 4(c) implies" by "which is Definition 4(c) evaluated at s = s̄, where Δ* = 0 and g* = G; at a share with headroom the two conditions differ when a process changes λ or k".

### Finding 3 (unclear). Section 7.3 cites Prop. 7(e)(iii) for a case in which it is proved only at ν_D = 0, and the sentence on disruption rates refers to nothing in this paper

**Location.** M §7.3 p.53 ("overstates by less than one wave's capacity afterwards (Proposition 7(e)(ii)–(iii))"); p.53-54, bullets "Risk" and "Embedding" ("the disruption rates are kept for the timing of shocks").

**Issue.** Prop. 7(e)(iii) (the shortfall below min{1, ϖc_w n(t_R)} is less than c_w) is stated and proved for ν_D = 0. The calibration reads p^emb = ϖ from outcome surveys and applies no hazard, so in the proposition's terms it is the ν_D = 0 case and (iii) applies. But the text in the same paragraph quotes disruption rates of 0.23 and 0.07 a year and says they are "kept for the timing of shocks"; in Prop. 7(e) ν_D enters only through p^emb, and no result of this paper uses a timing of shocks (the phrase refers to the companion paper, per the comment in `calibrate_horizons.py`). A reader who takes ν_D = 0.07 literally will find that (iii) does not cover the fast case (where the fill condition of (ii) fails after about 2031: c_w[1+ϖ(n−1)] = 1.72 by 2036).

**Evidence.** Pace arithmetic reproduced in `r2_checks.py`, block 7 (central: n(t_R) = 9, 25, 51; E = 0.107, 0.298, 0.607; fill condition 0.11, 0.30, 0.61; fast: 0.352, 0.859, 1 with fill condition 0.36, 0.86, 1.72). A fluid simulation with disruptions (block 2) suggests the shortfall stays below c_w for ν_D > 0 as well, so a one-line extension of (iii) may be available, but it is not in the paper.

**Required change.** Say in the "Embedding" bullet that the pace formula is Prop. 7(e) with ν_D = 0 (p^emb = ϖ), delete "kept for the timing of shocks" or point it at the companion paper, and cite (iii) only under that reading; or extend (iii) to ν_D > 0.

### Finding 4 (overclaim). "The limit is set by what stays scarce, not by what is automated" contradicts Prop. 4(c) to (d) for input owners

**Location.** Abstract p.1 (last sentence); M §9 p.63 (last sentence); §3.8 intuition p.23 ("not by how much can be automated").

**Issue.** In the scarce-input case, P = A − BZ is pinned by the input's supply and the rent is ρ = 1 − ĉ/P. Automation lowers ĉ one for one, so the input owner's limit score XG + (r−G)(k+k_a) + ρ rises with every unit-cost saving, up to the full-cost ceiling of Prop. 4(d). Scarcity determines who captures the savings, not whether they lift the score. The sentence is right only for firms without a scarce input (Prop. 4(b)). Section 7.2 (p.52) already says "a durable high score requires a rent on an input rivals cannot replicate, up to that ceiling".

**Required change.** "Under free entry, automation's savings lift the score only of whoever holds an input that stays scarce, and then only up to the full-cost ceiling", or similar.

### Finding 5 (overclaim). The conclusion's "requires near-complete automation" is stronger than Cor. 4(a)

**Location.** M §9 p.62: "A sustained cash-basis score above 100 therefore requires near-complete automation, negligible capital needs and a market growing at a rate few markets sustain".

**Issue.** Cor. 4(a) says a firm with total cost share at or below that of the full-automation structure (c_c + f + a_min + c_full ≈ 15.8 points pre-tax in the central case) has R_∞ ≤ R_max; any firm whose costs are that lean, by whatever means, has the same bound. The abstract and §7.2 are careful ("complete automation ... at fixed prices"; "a firm whose costs are leaner than that structure can score more"); the conclusion drops the qualification.

**Required change.** "requires a cost structure at least as lean as the full-automation structure of Section 7.2, which for a software firm means near-complete automation, ..."

### Finding 6 (unclear). Section 7.2 applies the pre-tax bound of Prop. 4(d) to the after-tax margin term

**Location.** M §7.2 p.52: "a firm with 5% market growth and k = 0.5 scores at most the central margin term plus 2.5 to 3 points"; Prop. 4(d) p.23 and its proof S p.16 (τ = 0).

**Issue.** As stated, Prop. 4(d) gives 1 − c_c − f − a_min − c_full + XG − G(k+k_a) = 86.7 points at the central shares, not 69.0 + 2.5 to 3. The quoted numbers are those of an after-tax extension (profits and rents taxed at τ, growth capital deducted at ψ): (1−τ)(1−c_c−f−a_min−c_full) + XG − (1−ψτ)Gk = 71.5 (ψ = 0) to 72.0 (ψ = 1). The extension is immediate but not stated.

**Evidence.** `r2_checks.py`, block 4.

**Required change.** Add to Prop. 4(d) (or a footnote in §7.2) that with profits and rents taxed at τ the bound is the after-tax R_max of Cor. 4 with capital k + k_a.

### Finding 7 (gap). Hypothesis (H) is stated but its content is not delineated

**Location.** M Prop. 2(b) p.18; text after Prop. 2 p.19.

**Issue.** (H) bundles two conditions. The second, "the feedback generates a share path in (0, s̄)", is essentially automatic once the first holds: σ̂ is continuous when v̂ ∈ C^1, so Peano gives a local solution of ṡ = sℓ(s)σ̂(s)^α, which is nondecreasing and cannot cross s̄ because ℓ(s̄) = 0. The whole weight of (H) is the existence of a bounded C^1 solution of (17) on (0, s̄). Two facts that follow from the HJB and would help a reader judge (H) are not stated: (i) if (m_0 − kG)/(r−G) ≤ k the linear function v̂ = (m_0−kG)s/(r−G) solves (17), so (H) holds and the firm never spends; (ii) if (m_0 − kG)/(r−G) > k no solution can have a no-spend region (there v̂′ = (m_0−kG)/(r−G) > k, a contradiction), so under (H) the firm spends at every share, and the terminal behaviour is v̂(s)/s → v_L := (m_0−kG)/(r−G) and v̂′(s) → v_L as s → s̄ (write w := v̂/s − v_L ≥ 0; since ℓ(s) ≈ λ(s̄−s)/s̄, the ODE s w′ = k − v_L − w + ℓ(s)^{−1}[(r−G)w/C_α]^{1−α} keeps w′ bounded only if w^{1−α} is of order (s̄−s), so w → 0 at the rate (s̄−s)^{1/(1−α)} and s w′ → 0), which is the terminal condition v̂(s̄) = v_L s̄ that the numerical solution of checks 15g to 15m imposes.

**Required change.** State (i) and (ii) after Prop. 2 (both are two-line consequences of (17)), say that the feedback condition is automatic, and say that the numerical evidence for (H) is a solution through the terminal singular point with v̂(s̄) = (m_0−kG)s̄/(r−G).

### Finding 8 (unclear). The reorganization rate ν^R is a program-time rate in the model but a calendar rate in the data

**Location.** M Def. 4(b) p.29 ("ν^R is the rate of reorganizations"); Prop. 7(f) p.31 ("a Poisson process of rate ν^R in program time"); §7.3 p.54 ("reorganizations freeze the program about 10% and 2% of the time"); Table S7 (ν^R 0.46 a year, class b).

**Issue.** Under the uniform clock the frozen share of calendar time is ν^R T_frz/(1+ν^R T_frz), which is the right expression only if ν^R counts reorganizations per unit of unfrozen (program) time. If ν^R is per calendar year, the frozen share is ν^R T_frz and the clock factor 1/(1 − ν^R T_frz). At ν^R T_frz = 0.115 the two differ by 1.3% in pace; at the slow case's 0.6 they differ by 2.5 times. Prop. 7(f) is consistent with the program-time reading, Table S7's grounding with the calendar one.

**Required change.** One sentence in Def. 4(b): "ν^R is the rate of reorganizations per unit of program (unfrozen) time; a calendar rate ν^R_cal corresponds to ν^R = ν^R_cal/(1 − ν^R_cal T_frz)".

### Finding 9 (overclaim, minor). "Which exceeds the screening weights of two to three when its revenue multiple does"

**Location.** Abstract p.1; M §3.6 worked example p.19; §8.1 p.59.

**Issue.** In the paper's own example v′(s) lies below v(s)/s at every share (9.1/9.4, 7.2/8.1, 5.4/6.5), and S2.2 (p.6) says "a firm valued near three times revenue would have a decision weight near or below three". So the decision weight exceeds 2 to 3 when the multiple exceeds it by a margin, not "when" it does. No inequality v′(s) ≤ v(s)/s is proved (it would follow from concavity of v, which is not shown).

**Required change.** "which exceeds the screening weights of two to three when its revenue multiple clearly does" or "when its revenue multiple is well above three"; or prove v′ ≤ v/s under (H).

### Finding 10 (unclear). The introduction and Section 8.2 still say risk "acts like a cut in capacity"

**Location.** M §1 p.2-3 ("risk acts like a cut in capacity"); §8.2 p.60 ("act like a cut in that capacity"); contrast M p.31 ("approximately like a cut in the program's pace", for programs with many waves).

**Issue.** Round 1 established that freezes dilate time (the embedding lag included) rather than scale capacity, and the model text was corrected; the introduction and discussion were not. The introduction also states the convergence-level claim ("partial realization of benefits lowers the level to which the firm converges") without the assumption it now rests on.

**Required change.** Use "pace, approximately" in both places and add "when a process's realized share is a property of the process" to the introduction's sentence.

### Finding 11 (minor). Duplicated sentence

**Location.** M §3.6 p.19, "Implication for measurement": "The spend data therefore do not identify the decision weight. They do not identify the decision weight."

**Required change.** Delete the second sentence.

### Finding 12 (minor). δ for δ_K in Prop. 9 and Table 7; F for two objects

**Location.** M Prop. 9(a) p.57 ("da > (g* + δ)dk"); Table 7 p.58 (column "g + δ"; note "at δ = 0.25"); Table S1 p.2 (F: feasible set and replication cost).

**Issue.** The paper unified capital depreciation as δ_K (Remark S1(c), Remark 2, Cor. 4) in response to R1-15 and R1-23; Prop. 9 reintroduces δ. The feasible set and the replication cost share the letter F in the notation table (calligraphic versus italic in the text, but Table S1 does not say so).

**Required change.** δ_K in Prop. 9 and Table 7; note the calligraphic F in Table S1.

### Finding 13 (minor). Two illustrative values of α in Section 7

**Location.** M §7 p.49 ("the central path uses α = 0.35"); §7.5 p.58 and Table 7 note ("α = 0.3"); §3.1 p.12 ("use α = 0.3 in every illustrative example").

**Required change.** Say why Table 7 uses 0.3 while the path uses 0.35, or use one value.

### Finding 14 (minor). Prop. 7(e) is a deterministic fluid model stated under a stochastic definition

**Location.** M Prop. 7(e) p.30-31 ("outcomes average out over mass"; "E R*_X(ϑ_t) = ...").

**Issue.** Part (e) replaces the random outcomes of Def. 4(b) by their means ("of a mass a attempted, ϖa works and p^emb a embeds"), which is an additional modeling assumption (a law of large numbers over a continuum), not a consequence. The expectation sign is then redundant. Check 28m shows the lumpy model converges to it as N grows, which is the justification; it should be said in the statement or in S2.7.

**Required change.** Add "(a fluid limit, which the lumpy model approaches as N grows; check 28m)" to the statement or to S2.7.

### Finding 15 (minor). Prop. 7(e)(ii)'s fill condition uses ϖ while the calibration substitutes p^emb for ϖ

**Location.** M Prop. 7(e)(ii) p.31; `verify_theory.py` check 28m (fill condition evaluated with `prm['varpi']` = q = p^emb); M §7.3 p.53.

**Issue.** If the survey success rate is read as p^emb (as the "Embedding" bullet says), the underlying ϖ is p^emb/exp{−ν_D(1+ν^R T_frz)T_emb} = 0.70/0.726 ≈ 0.96 in the central case, and the fill condition c_w[1+ϖ(n−1)] is 0.84 rather than 0.61 by 2036: still below one, so the conclusion stands. Under Finding 3's reading (ν_D = 0) there is no discrepancy.

**Required change.** None beyond Finding 3; note the value of ϖ used in the fill condition.

### Finding 16 (minor). The docstring run time

**Location.** `code/verify_theory.py` line 19 ("about three to four minutes").

**Evidence.** 5 min 53 s wall clock (3 min 10 s CPU) on my copy.

### Finding 17 (minor). Positioning: one classic precedent for non-identification

**Location.** M §2.1 p.5, §2.7 p.9, §3.7 p.20-22.

**Issue.** The non-identification argument (chosen points of heterogeneous firms trace a locus of tangencies, not any firm's frontier) is the identification problem of Marschak and Andrews (1944, Econometrica) for production functions, and the selection-by-quality mechanism is the same as in heterogeneous-productivity explanations of positive growth-profit correlations. The paper's claim that the application is new is fair; the precedent for the logic should be named.

**Required change.** One sentence and a citation.

### Finding 18 (minor). A citation I could not verify

**Location.** M §3.6 p.18: "in the investment model of Belo et al. (2022), brand capital accounts for 6% to 25% of firm value, depending on the industry".

**Issue.** I could not check the range against the source offline. If the numbers are from the paper's decomposition tables, cite the table.

## 4. What I checked and found correct

Re-derived by hand (all correct unless a finding above says otherwise):

- **Frontier, score, saturation (Lemmas 1 to 3, Remarks S2, S3).** Inversion and the three curvature cases; the σ* = σ̄ endpoint statement in Lemma 2(b); duality (d); Lemma 3(a) derivative −(X−k)Δ*/(s̄−s); (c) including the X ≤ k case; the Rule-of-1000 numbers (C_0.3 = 0.418, Λ = 8.71, Δ* = 13.14, σ* = 3.94, m = −3.34) and S5's 6.8 to 9.3; Figure 1's two optima (g* = 38%, m = 34%, R = 71; g* = 48%, m = 19%, R = 114).
- **Timing (Lemma S1(a) to (d)).** The α = 1/2 interval, the α > 1/2 condition, and the asset-light sliver (κ = 1.65, Δ ≈ 0.02).
- **General technology (Remark S4).** Concavity and tangency, σ*/Δ* = (X−k)ε(σ*), slope −k − 1/(ℓφ′(0+)) at G.
- **Budget and transience (Prop. 1(a) to (c), Prop. S2, Cor. 1(a), (b), Prop. S1).** The logistic solution, the pointwise bound, the discrete inequality, the moving-intercept extension, the sharpness construction, the continuous-time bound 0.43 and the static-optimum bound 0.30 years, the exponent −1/α.
- **Comparative statics (Lemma 4, Cors. 2, 3).** All derivatives and the C^1 property at y = 0; convexity in k and λ; the cross-partial; the exact bracket (15); both measures of growth-engine productivity in Cor. 3(ii) (xσ* and xσ*/α, exact forms Π[(1+x)^{α/(1−α)} − 1] and Π[(1+x_λ)^{1/(1−α)} − 1]); (iii) to (v).
- **Dynamics (Prop. 2).** (a) the bounds; (b) the supersolution inequality (S3), transversality, and the optimality of the feedback under (H); (c) the identity maximand = R_X − XG; (d) the root, H′(v_0) = r − G − Δ° > 0, v_0 = m°/(r−g°), the supersolution v_0 s, the constant-policy lower bound by monotone convergence, and v̂′ → v_0 under (H); (e) the divergence argument; the ODE form and ∂Φ/∂u = (r−G)/Δ° at the origin; the worked example (λ ≈ 0.070 gives v_0 = 10, g° = 7.6%, σ° = 10.7%, m° = 24.3%).
- **Screening weight (Lemma 5(a) to (e)).** (20); D as an exponential-family mean; monotonicity in θ; the Gordon limit; (e) X^scr = (m+m̄M_∞)/(1+g) = (V/S_0)(1+r)/(1+g)^2 and its value 3.023 in the example; the S2.2 examples (1.8/2.8; 5.4/6.2).
- **Heterogeneous firms (Prop. 3, Prop. S3, Remark S5, S2.3).** The envelope, (22), the quality condition (0.3X per growth point), the quantile argument, (iii), the ϒ-ξ construction in S3(iv), the curvature −(1−α)y/(αΔ*), the within-firm slope (S2) and its variance shares (52%, 71%, 80%, 85%); S_β = 6βW^{β−1}/[(β+1)(β+2)] and the factor 2.3 to 5; the two-type example (+0.31).
- **Free entry (Ass. 6, Prop. 4(a) to (d), Remark S6, Lemma S2).** The stock/flow equivalence by parts on nondecreasing paths; Cournot quantities, price and profit; the Lerner index; the customer-capital accounting m_op = L + rk + (r−G)k_a and m = L + (r−G)(k+k_a); n* = ⌊N_F⌋ − 1 and the bound on L_{n*}; the F → 0 limits; the scarce-input case (w_n, P = A − BZ, BZ²/n², ρ = 1 − ĉ/(A−BZ) with A − BZ > ĉ); (d) ρ ≤ 1 − (shares) − r(k+k_a) and the match with R_max at τ = 0; the 7.5-point and 10-point examples; the pass-through elasticities (n/(n+1))u/p and u/ĉ.
- **Taxes and the ceiling (Remark 2, Cor. 4(a) to (c), Table 4, Remark 7).** The after-tax margin with the (1−ψ)τδ_K k correction; the four substitutions; ψ_5 = 0.796, ψ_15 = 0.532; the scope condition of Cor. 4(a); (b) and the ψ and δ_K adjustments; every row and threshold of Table 4 (bases 78.1, 69.0, 54.5, 40.3; G* 21.9, 31.0, 45.5, 59.7; accountability-only bases 79.5, 72.6, 63.5, 44.7); Remark 7's change in the ceiling, the ψ = 1 thresholds 16.5% and 49.5%, and the ψ = 0 thresholds 33.3% and 73.5%.
- **Full-cost floors (Lemma 6(a) to (e), Table 8).** The annual equivalents; the Gordon-Loeb-type minimization and the identity (c_0/L_sec)(1+L_sec+ln ξ_exp) with the rows 0.86, 1.27, 2.14; the review-proof error rate and its limit χ(ε^o+ε^h); the capped Pareto mean (2.8 at p = 1.5, Ȳ = 100) and the misbehavior rows 0.01, 0.34, 1.51; the common-mode cost ν_cm T_con[W_cm + H_cm W_cm²/(2Y_fb)] with the rows 0.08, 0.33, 0.99; c_mnt rows 0.15, 0.60, 2.89; c_full = 1.67, 4.30, 11.44.
- **Accountability floor (Ass. 7, Prop. 5(a) to (d), Remark 6).** P_o(D) with the cross-type term and the factor one for unused types; strict decrease in depth; the admissibility threshold P̄_o; the impossibility statement for single-type designs; the constrained minimum; the scale limit; all of Remark 6's numbers (all-AI floor 11.3%; three human layers 5.0% at $1.50m; every all-human design ≥ 4.7%; one human over one AI 3.1% at $0.90m; one over two 0.7% at $0.95m; 48 opportunities 6.0% and 1.3%; AI common mode 0.01 gives 3.6%; two human over one AI at 1%, $1.40m), and that one human over one AI is indeed the cheapest admissible design at 5%.
- **Attainable and expected frontiers (Ass. 8, Def. 4, Props. 6, 7, Lemma S3, Remark S8).** Prop. 6(a) to (d) including the fractional knapsack; Prop. 7(a) under the uniform clock with the share-raising argument; (b) all six couplings (time, capacities, success thinning, disruption superposition, freezes via the clock, embedding lag, share dominance); (c) the optional-stopping count bound and the equality for the filling plan; the share bound with shares drawn at date 0, also under reversion; (d) the retry plan, the upper bound, (1−b̄)NΔR, and the capacity limit; (e)(i) to (iii) including U_w = (1−ϖ)U_{w−1} after the first unfilled wave; (f) the SLLN clock, the pathwise bound, the conditional count bound, the Poisson survival formula and its comparison with the uniform-clock value, and the counterexample; the horizon arithmetic (6.3% and 17.2% a year; E = 11, 30, 61% and 30, 73, 85%; completion in 2032).
- **Economic profit (Remark 3(a) to (d)).** The three frontiers, the identities, V/S = k + e/(r−g), V/(kS) = (ROIC−g)/(r−g), the iso-value fan through (r, 0), the tangency at (g°, m°), and the k = 1.5 example (−7.5 points; −0.5 per point).
- **Acquired growth (Def. 5, Prop. 8(a) to (f), Remark 4).** The net weight, the bang-bang result, G_i = ln(1+a), the per-business budget, the treadmill, and the CRF and user-cost inequalities.
- **Levers by position (Prop. 9, Table 7).** All six parts; the growth-corner row (X_0‡ = 6.6 from (0.24/0.50)^{0.7} = 0.60; G_i = 14.0; values 5.0, 16.6, 2.4).
- **Discussion arithmetic (M §8.1).** R_1 − R_∞ = Δ*(1 − k − α(X−k)); −20 points at a spend ratio of 3.02 and 10 points of excess growth.

Code:
- `code/verify_theory.py` (identical to the live repository's copy, md5 compared): 189/189 pass, exit code 0, 5 min 53 s. The checks that matter for round 1 are substantive: 28n to 28q and 22a to 22e simulate the exact claims of Def. 4(b) and Prop. 7 (including the round-1 counterexample at 200,000 paths, selective reversion under both share conventions, and the two couplings that were untested), 28i tests the verification inequality on random policies, 28k the scope of Cor. 4, 28l the tax correction symbolically, 28j the customer-capital accounting symbolically, 28c three non-isoelastic technologies, 28d to 28e the new budget corollaries, 28f Lemma 5(e) against a finite-difference MRS and the two remarks that were unchecked, 28g to 28h Prop. 2(e) and the singular point, 28m the fluid program and the calibration's formula, 25d to 25e and 27a to 27d the control standard and Remark 6, 26a to 26g Lemma 6 and Table 8. Checks that verify only an example's numbers are labelled "[arithmetic]", and checks against printed numbers "[text]". The one limitation is inherent: the couplings of Prop. 7(b) and the bound of 7(a) are tested on the greedy plan and random programs, not on the supremum over plans, so they are evidence, not proof; the proofs themselves are correct.
- `notes/calibration_results.json` reproduces the pace block (q = 0.70 and 0.80, rates 6.3% and 17.2%, shares 0.072/0.199/0.407 and 0.299/0.730/0.850) from the stated parameters.
