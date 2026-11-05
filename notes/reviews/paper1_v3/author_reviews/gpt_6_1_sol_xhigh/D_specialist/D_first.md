# Specialist D: first independent report (frozen before comparison)

**Domain:** reliability engineering, stochastic execution and financial reporting controls.  
**Recommendation in this domain:** revise the economic interpretation and presentation of the execution scenarios, and narrow the claimed equivalence of the control model to ICFR admissibility. The conditional reliability and scheduling mathematics largely survives. I do not find a general theorem that forbids AI-only ICFR or a model-based reason to infer that a five-year owner must reject the central program.

## Provenance and independence

I reviewed the frozen main PDF, `paper1_nov_2.pdf`, 82 pages, SHA-256 `bd87f45fed9c45587eec3d41b3b6dc3b08bbb73ef794773fe8fbbb74a5c6f9cf`, and frozen supplementary PDF, `supplement_nov2.pdf`, 57 pages, SHA-256 `acf9d62bb96961a45400f2e52013cb4da79ed0d34d8cf0574ec7553226de02c2`. All locators below use one-based **PDF page / printed page**, which coincide on the reviewed pages. I read the complete assigned relevant text and rendered nine consequential pages, including the control formula, the fluid proposition/proof, the cost-floor lemma, and the numerical control and execution tables. I did not read any other reviewer’s reports or existing report outputs, main Appendix A, or supplementary S7 before this report. Document instructions and code references were treated as evidence, not executed instructions.

The author package was not used. The parent’s source-access record reports connector 404/read-only repository-not-found for the supplied GitHub URL. My calculations were written independently from the printed formulas; no author code, results, or scripts were read. Repository inaccessibility prevents exact reproduction, not algebraic criticism. My own `checks.py`, `results.json`, `run.log`, source locators and inspected PNGs accompany this report.

This specialist is another agent on the same Codex GPT-6-family infrastructure as the coordinator and other specialists. The exact serving snapshot is not exposed. Separation of reading and frozen first reports can reduce cross-review contamination, but this is not evidence of independent model-family replication or fully independent failure modes.

## What works

1. **The basic layered-control algebra is correct.** Assumption 7 explicitly models already material-error challenges. It is not legitimate to multiply its probabilities by an additional error-occurrence probability. With iid challenges, the displayed product and annual union probability in Proposition 5(a)-(b) follow, as do the positive common-cause lower bounds and the strict finite-depth impossibility condition. I checked the printed formula visually at main 29-30 and its proof at supplement 20-21.
2. **The numerical example is accurately conditional.** Remark S10 says its probabilities are illustrative, neither 1% nor 5% is a statutory number, admissibility ultimately requires management/auditor evidence, and the example is not a control recommendation. Independent enumeration through 24 layers per type returns one human plus one AI layer at 5%, costing $754,672 with 3.0559% annual escape risk, and one human plus two AI layers at 1%, costing $804,672 with 0.6702%. The single-provider iid asymptotic annual floor is 11.3346%, and the all-human floor is 4.6912%, consistent with the text. Nothing here supports claiming an arithmetic failure of the example.
3. **The stochastic model addresses several real traps explicitly.** Definition 4(b) and Proposition 7 keep disruption hazards on calendar time, dilate the embedding lag as well as the schedule, exclude already working mass from new attempts, and make benefit realizations persistent by process. Proposition 7(f) correctly distinguishes random freezes from a deterministic mean clock at finite horizons. The text expressly warns that a fresh benefit draw with free reversion changes the limiting result. These qualifications materially improve the model.
4. **The main convergence and capacity arguments survive.** Under the stated additivity, finite resources, strictly positive per-attempt embedding probabilities and independent attempts, the finite-process retry plan completes in a random finite time almost surely. That is compatible with a positive noncompletion probability at every specified finite date. The subset/packing arguments behind Proposition 6 and the count upper bound of Proposition 7(c) are sound in the stated setting. The fractional-knapsack upper bound need not make the whole attainable frontier concave, and the paper correctly says so.
5. **The auxiliary loss-floor formulas are coherent as conditional models.** The exponential security-loss minimization, capped-Pareto expectation and the concentration term in Lemma S4 are correctly derived under their assumptions. Table S16 prominently classifies loss severities, exposure and several build/implementation inputs as scenarios. The paper does not improperly apply the measured human review catch rates to the no-human operational review case.

## Findings requiring correction or explicit narrowing

### D1 — A payback beyond the holding period does not imply the owner rejects the program

**Classification:** substantive economic inference error, high confidence; consequential to the practical ownership claim.  
**Locators:** main 5, paragraph beginning “The pace”; main 61, first paragraph; main 66, §8.2; main 70, conclusion. Supporting model: supplement 10, Remark S8(ii).

The statement on main 61 that an owner holding the firm for five years or less “would therefore not fund the whole program” does not follow from a 7.5-year cumulative cash payback or negative cumulative cash at year five. Embedded benefits are expressly durable. The value of those benefits after sale can enter the sale price. The same paragraph reports a strongly positive program NPV, making omission of terminal value especially consequential. This is an error in the claimed implication, not a challenge to the reported cash-flow crossing itself.

**Independent counterexample:** pay 14 at inception for 2 per year over 20 years, discounted at 10%. Cash payback is 7 years, and cash through a five-year holding period is -4. At year five, the remaining 15 years of benefits are worth 15.2122. Five-year cash flows plus discounted exit value have NPV **+3.0271**, exactly the full-life NPV. The owner can rationally fund it despite no cash payback during ownership.

**Strongest complete-text defense:** Remark S8(ii) defines an owner who admits only transitions that pay within its own horizon; the paper may mean a hard payback covenant, a liquidity budget or an owner unable to monetize continuation value. Those are defensible restrictions, but they are not implied by a five-year holding period, and the categorical sentence currently omits them.

**Disposition after defense:** **survives, narrowed** to the unconditional ownership inference. The scenario’s payback calculation itself remains unrefuted.

**Correction / acceptance test:** replace the categorical statement with “does not repay cumulative transition cash costs within five years”; require an explicit hard payback/liquidity rule for a rejection claim. If an ownership-investment conclusion is retained, calculate five-year cash NPV plus a documented terminal value (or justify terminal value zero). Keep flow crossing, cash payback, discounted payback and investment value distinct.

### D2 — Exact completion in 2032/2042 is incompatible with the divisible retry model

**Classification:** mathematical interpretation/presentation error, high confidence; modest effect on rounded horizon scores, potentially important to completion and NPV accounting.  
**Locators:** main 5; main 60, paragraph following the embedding bullet; main 61, first paragraph (“program…completes in 2042”); main 66 §8.2; main 70. Governing model: main 34, Proposition 7(e)(iii), and supplement 23-24, proof of 7(e).

The fluid recurrence proved in the supplement is

`U_w = U_(w-1) - p min(c_w, U_(w-1))`, with `0 < p < 1`.

Once remaining mass is below one wave’s capacity, `U_w = (1-p) U_(w-1)`. It is positive at every finite wave if it was positive initially. Thus `E_w -> 1`, as the proposition correctly states, but exact full embedding is not attained at a finite date. Capping the linear upper bound `p c_w n` at one creates a finite saturation date for a bound, not an exact completion date for the greedy retry process. For a finite stochastic program, completion is almost surely finite but random, and cannot be guaranteed by the calendar year derived from an expectation or upper bound.

**Independent illustration:** an admissible quarterly-wave example with the printed fast parameters `p=.8`, `rho=.22`, unfrozen fraction `.98`, embedding lag 1 gives 99.872% embedded at elapsed year 7 (2032), rather than exactly 100%. A corresponding central illustration gives 99.4% at elapsed year 17. These are illustrations, not reproductions of the author’s undisclosed wave calibration. The analytic noncompletion result does not depend on the illustrative wave length. Even with unlimited parallel retry capacity, 48 independent processes at success probability .8 have all-complete probability `(1-.2^k)^48`, below one for every finite `k`.

**Strongest complete-text defense:** the table explicitly rounds to integer points; “all” may mean “rounds to 100%” or a practically negligible residual. Also, supplement S2.7 acknowledges that the capped bound overstates actual progress by less than a wave’s capacity.

**Disposition after defense:** **survives as a precision/correctness repair**, not as a refutation of Proposition 7 or the central 41% result. Integer rounding does not define a completion rule in the prose or specify when costs cease for the reported program NPV.

**Correction / acceptance test:** state a tolerance, such as 99% or 99.9% embedding, and report its date from the exact recurrence. Label deterministic bound saturation separately. Recompute cost stopping, “life of program,” benefit-to-dip ratio and the NPV if any used capped progress as exact completion. Do not claim finite exact completion for the fluid model.

### D3 — The control constraint is a stylized surrogate, not a demonstrated iff characterization of ICFR effectiveness

**Classification:** scope/identification problem in the claimed legal mapping, high confidence; the conditional mathematics survives.  
**Locators:** main 28-30, Assumption 7 and Proposition 5(b)-(c); main 3 introductory accountability claim; main 55-56; supplement 50, “The threshold” and “Direct costs”; supplementary 51 Table S15.

Item 308(a)(3) supports the paper’s pass/fail observation: a material weakness bars an effectiveness conclusion. It does not supply 1% or 5%, annual iid challenge aggregation, or a per-objective numerical safe harbor. [17 CFR 229.308(a)(2)-(3)](https://www.ecfr.gov/current/title-17/chapter-II/part-229/subpart-229.300/section-229.308).

AS 2201 requires consideration of deficiencies together, potential magnitude, interactions and timeliness; a numerical probability is unnecessary. Thus the local inequalities need an additional assertion/exposure/aggregation model before they become sufficient for the full legal conclusion. [AS 2201, .62-.67 and .A7-.A10](https://pcaobus.org/oversight/standards/auditing-standards/details/AS2201). The SEC similarly requires assessment of combinations and qualitative as well as quantitative factors. [Release 33-8810, §II.B.1, printed Federal Register p.35332](https://www.sec.gov/files/rules/interp/2007/33-8810fr.pdf).

Two particular gaps matter. First, the sum of expected losses for individually below-materiality errors in (28) cannot by itself exclude a material aggregate of errors. For example, two possible same-direction uncorrected errors of 0.6 times materiality jointly exceed materiality. If their independently surviving probabilities are .2, aggregate exposure has probability .04, although each individual error is below materiality. Those challenge populations must be included in a material aggregate objective rather than only priced as expected small losses. This example does **not** add a new occurrence factor to the manuscript’s already material challenges; it exposes a missing aggregate category.

Second, using the same annual 5% bound separately on multiple objectives does not implement a firm-wide 5% bound. Two independent objective-level material-escape probabilities of 4% produce a 7.84% probability of at least one material escape. This is not a claim that the law mandates a global 5%; it demonstrates that the scenario’s probability unit must be specified consistently. Remark S10 recognizes this distinction and computes a ten-objective allocation, which is a useful defense, but the proposition does not require aggregation-complete objectives or a firm-level allocation.

**Strongest complete-text defense:** `O` could be chosen to include all material combinations and relevant assertion risks, with a judgmental threshold for each. Main 6 says the numerical threshold is a scenario, and Remark S10 correctly reserves actual admissibility to management and audit evidence. On that construction the optimization is an illuminating reduced form.

**Disposition after defense:** **survives, narrowed** to the unconditional “if and only if / this is the standard” wording and insufficiently explicit scope. I withdraw any claim that the paper invents a statutory numerical threshold; it explicitly does not.

**Correction / acceptance test:** call the inequality a conditional numerical admissibility surrogate. State that `O` is exhaustive for material combinations, interim reporting risks, assertions and compensating controls, and explain how aggregate submaterial errors enter that set. If a firm-level probability is used, allocate it or impose a joint constraint. Retain the valid distinction between cost optimization inside admissibility and simply accepting material-error losses for money.

### D4 — The single-provider numerical impossibility depends on temporal independence as well as the common-mode probability

**Classification:** consequential sensitivity / external-validity limitation, high confidence; not an internal contradiction.  
**Locators:** main 29, Assumption 7 (“draws…independent across opportunities”); main 30 intuition; main 56; supplement 50, “Designs”; main 2 summary item 9.

The examples named for common-mode risk—persistent bad data, a regression after a model update, drift and management override—can persist across several material challenges. Assumption 7 rules that out. The annual no-AI-only result uses both the marginal per-challenge common-mode probability .005 and independent repetition over 24 challenges. Saying the provider common-mode probability is “the number to estimate” understates the role of its temporal dependence.

**Independent alternative with the same marginal per-challenge common-mode probability:** draw one persistent bad-provider state for the year with probability .005; in that state every one of the 24 already material challenges defeats every same-provider layer. Outside the state, each of `n` layers independently misses each challenge with probability .02. Then

`pi_n = .005 + .995 [1 - (1-.02^n)^24]`.

For three same-provider AI layers this is about **0.5191%**, below both scenario thresholds, at $354,672 including the illustrative ITGC line. The iid model instead makes no finite depth admissible at either threshold. The alternative uses no error-occurrence multiplier and preserves the .005 marginal common-mode chance on each challenge; it changes only temporal coupling.

**Strongest complete-text defense:** the manuscript transparently assumes independence across opportunities and calls the numerical design an illustration. Its theorem is conditional and correct; a persistent-state model is outside its theorem. Also, firms may have both persistent and fresh per-challenge common causes.

**Disposition after defense:** **survives as a required sensitivity and qualification**, not a disproof of Proposition 5. The robust claim is that redundancy cannot remove a common-mode floor; the particular annual floor, composition and cost require a temporal model.

**Correction / acceptance test:** report at least iid-per-challenge and persistent-per-period cases (or a Markov/event-time model), distinguish the probability units, and avoid provider-general inadmissibility rhetoric unless the relevant annual/period lower bound is independently supported. Add persistent versus fresh common causes to the quantities that need estimating.

### D5 — The headline 59 is a durable embedded-parameter score, not the cash score while paying the stated dip

**Classification:** presentation/estimand mismatch, medium-high confidence; no table arithmetic refuted.  
**Locators:** abstract main 1; main 2 summary item 6; main 6 item 3; main 33 paragraph after Proposition 6; main 60 Table 5 and notes; main 61 “Central path”; main 70 conclusion.

Table 5 correctly labels `R*=R_infinity`, holds the dip in a separate column, and says that it reports the durable score. The earlier model says the realized margin equals the embedded frontier margin plus in-flight net flow. Consequently, when central 2036 has a durable score about 59 and a dip 4.2, the firm’s contemporaneous cash score is about **55** while the dip is incurred. The abstract’s simpler “scores 59” and the “attainable pace” title can be read as realized all-in cash performance at that date. That reading is inconsistent with the separate dip.

**Strongest complete-text defense:** the table and surrounding text disclose the distinction, summary item 6 separately mentions transition costs, and Table 6 explicitly includes an in-flight-dip sensitivity. There is no concealed transition-cost assumption in the detailed discussion.

**Disposition after defense:** **survives as a labeling correction only**. I do not claim the author added the dip twice or that the durable score calculation is wrong.

**Correction / acceptance test:** label the abstract/summary number “durable score before transition dip,” preferably report both 59 and approximately 55 while transforming, and distinguish the uncertainty interval for the durable score from a net cash interval. State whether a given “maximal attainable” score includes the path’s in-flight costs.

### D6 — Exact horizon/payback reproduction needs additional printed execution inputs and accounting conventions

**Classification:** reproducibility limitation, high confidence; not evidence the numerical outputs are false.  
**Locators:** main 59-61, §7.3; main 32 wave definition; supplement 8 §S2.7; supplement 9 §S2.9; supplement 36-42 Table S11 and notes.

The formula for the number of embedded waves requires numerical `Tpar`. I found no numerical wave length in the inspected main text or supplement outside the excluded protocol history. “About” 10% and 2% freeze time is not the exact clock parameter. Exact dip/payback reproduction also needs the time profile of attempt charges and ramped savings, treatment of failed versus working attempts, benefit/compute-target changes between horizons, and the definition of the program endpoint. These details matter because the numerical claims are 4.0/7.5/8.5 years and 98% NPV, rather than just an order of magnitude. The source table documents many inputs admirably, but the inaccessible author package prevents resolving the remaining ones.

**Strongest complete-text defense:** the paper identifies scenario status, gives most governing quantities, documents the principal source-to-model differences and presumably contains the exact parameters and calculation in its replication package. A scenario can be informative without claiming all inputs are empirically estimated.

**Disposition after defense:** **survives as currently unverified reproducibility**, not a numerical error finding. My quarterly illustrative recurrence is deliberately not represented as an author-path replication; it matches central integer shares but not every fast-case share.

**Correction / acceptance test:** supply an accessible immutable package and a compact execution-input table with units, exact wave/clock values, horizon origin, and cash-flow rules. A clean independent implementation should reproduce central and fast embedded/realized shares, Table 5 dip, payback crossings, benefit-to-dip ratio and NPV. Program-completion tolerance must be explicit as in D2.

## Candidate objections tested and narrowed or withdrawn

- **“Add a material-error occurrence rate before annualizing.” Withdrawn.** Remark S10 explicitly says its 24 occasions are ones on which a material misstatement arises. The existing probabilities are conditional misses on already material challenges.
- **“The standard mandates a particular numeric remote probability.” Withdrawn.** The text repeatedly and correctly labels 1% and 5% scenarios. The problem is sufficiency/aggregation and the identification of the surrogate with the full standard, not failure to choose the right statutory percentage.
- **“Risks permanently lower the frontier despite retry.” Withdrawn under the assumptions.** With positive embedding probability and persistent process benefits, retries eventually reach the random persistent-benefit target. The paper correctly separates pace from a benefit shortfall.
- **“Uniform freezes are generally exact at finite dates.” Withdrawn as a criticism of the theorem.** Proposition 7(f) explicitly supplies the random-freeze qualification and counterexample. I independently checked the Laplace-transform survival expression: at `nuD=.23, nuR=.5, Temb=1.25, Tfrz=2`, random-clock survival is .595742 and uniform-clock survival .562705, in the stated direction.
- **“Fluid mean benefits hold under every adaptive reversion plan.” Narrowed to a clarification.** With heterogeneous persistent `b` learned at embedding, a plan can retain only high draws, so its retained mass need not have unconditional mean `bbar`. A continuum with half `b=0` and half `b=1`, all embedded then zero draws reverted, retains mass .5 and benefits .5, not .25. However, Proposition 7(e) expressly adds the condition that embedded mass realizes `bbar`; read literally this assumes homogeneous fluid benefit realization and excludes that example. Clarify that restriction or restrict the equality to plans without outcome-based voluntary reversion. The greedy calibration never needs to discard a nonnegative benefit, so I do not treat this as a calibration refutation.
- **“Attestation prevalence calibrates an escape-risk threshold.” Not established.** Remark S10 acknowledges these are different quantities, but its sentence using prevalence to reject a threshold that makes the illustrative human design fail also presumes that this human common-mode parameter represents effective filers. That premise is unmeasured. Remove this plausibility inference or make the extra population assumption explicit. It does not supply an additional independent estimate of the threshold.

## Coverage and limits

**Read in full for this first report:** main 1-6, 28-34, 55-62, 66 and 69-70; supplement 7-10 (including cost allocation, cross-provider dependence, program clock, yield/ownership), 20-24 (full assigned proofs), 36-42 (relevant parameter-source tables) and 49-53 (S8 and glossary opening). Supplement page 43 and the protocol histories were not read. **Visually inspected:** main 29, 30, 34, 60, 61; supplement 23, 49, 50, 52. Rendered pages use the exact frozen PDFs.

**Authority checked live:** currently effective AS 2201 (not the version effective December 15, 2026); Item 308 in the eCFR, current to October 29, 2026 as displayed; and SEC Release 33-8810 §II.B.1. The standards confirm the qualitative pass/fail premise; they do not validate the illustrative layer rates, common modes, independence, costs, or a numerical remote threshold.

**Not evaluated here:** SEC panel construction, acquisition adjustments, statistical inference, financial valuation proofs outside the ownership inference, source-level reproduction of empirical anchors, exact author-program implementation, source accuracy of every operational-cost parameter, or the quality of earlier review rounds. Shared-provider AI dependence and unpriced entity/service-organization controls are already disclosed in main 29 and supplement 8; they are limitations, not concealed omissions I rediscovered as novel flaws.

**Acceptance standard in this domain:** preserve the conditional reliability/scheduling results; repair the terminal-value inference, define completion precisely, distinguish durable and net cash scores, qualify legal equivalence and provide aggregation/temporal sensitivities, and make the execution scenario independently reproducible. These changes would substantially improve the paper without requiring abandonment of its central distinction between static full-cost potential and constrained execution pace.
