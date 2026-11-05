**Recommendation: targeted major revision before public release; not yet ready for a specialist journal.** The repository-access objection is resolved. All four required commands now pass on the pinned unmerged code, and their regenerated text outputs match the committed files; rebuilt PDFs have identical extracted text. The review sustains three major and fourteen minor manuscript findings, chiefly overbroad necessity/rent claims, the ownership-cost source conversion, and local inference/counterfactual defects. Of 49 response/stress-test rows, 40 are resolved and 9 partly resolved; no row remains unresolved solely for lack of repository access. Reproducing a numerical output does not validate its interpretation or external calibration. The expanded computational outcomes and remaining limits are stated in Part C; the original independently frozen Part B is retained with a clearly marked evidence update.

# Re-review: The Rule of 40 as a Price Line

Revised third version supplied 4 November 2026 | Review and computational update: 4 November 2026 America/Los_Angeles (5 November UTC)

## Scope, evidence and independence

The attached main paper (87 pages) and supplement (72 pages) remain authoritative for claims. The private repository is now accessible through the personal connection. This review uses commit `eb7537bee7585f2902304f62a722edea6ced8539`, named in the re-review prompt, on branch `review-round-3`; it does not review an older default-branch build. The observed branch head `786228da26e12235a9d0c7aa53f2ef1fde3c07bf` is one commit ahead and changes only `notes/reviews/paper1_v4/rereview_prompt.md`. Its program/data contents therefore equal the pinned revision. That comparison inspected file metadata, not restricted review contents. Nothing was merged or written to GitHub.

Four AI specialists reviewed mathematical theory/formalization, empirical methods, execution/stress tests, and controls/finance units/primary sources, followed by root adjudication. They use the same inherited backend and are not independent human or cross-model referees. Runtime disclosure: Codex, GPT-6-based per session instructions; exact serving build and configured effort are not exposed. The prompt's GPT-6.2 Sol (extra-high) address is not asserted as runtime fact.

The independent PDF-based Part B was completed and frozen before code became accessible. Its SHA-256 remains `85de8d0a40cb04f00202c73bf11b5e83f9b692618bfda30d1c328e2cf3c3e327`. No other-reviewer folders, other response letters or joint response were read before or after the freeze. The subsequent source inspections and reruns are separately identified, preserving the original record rather than silently rewriting it. No attempt was made to identify the excluded registrant. Author programs ran only on an isolated working copy; an independently hashed baseline was retained.

## Part A. Response audit, updated after code access

All 43 point-by-point rows and ST-1–ST-6 are included below and in response_audit.csv. “Resolved” applies to the specific objection and evidence level in that row; it does not certify every stronger use of the result. The author's status is preserved. ST rows have no status field in the response, so they are marked “Conditional qualification supplied”.

The response warns that some numbers predate the final run. The reviewed PDFs use 1,732 / 1,330 firm-years and p_RW = .075 with three of four GAAP comparisons significant at 10%; old counts and .097 are not treated as current errors.

| ID | Author status | Verdict | Evidence | Locator |
|---|---|---|---|---|
| GPT-M1 | Fixed | partly resolved | The exact cone mapping and all eight pinned-data multiplier/steepest-slope pairs now independently reproduce to 1e-10. Remaining F06 concerns cap, support, k=0 and excess-growth qualifications, not a failed numerical calculation. | M p 24; S p 7 S2.3; code/calibrate_horizons.py:1137; results/theory_pinned_source_checks.json |
| GPT-M2 | Fixed | resolved | The manuscript now distinguishes a tax-PV-equivalent margin from period cash and supplies the steady-growth deduction reading. Independent shield calculations agree with the rounded examples. This resolves the labeling/interpretation objection, not every implementation question. | M pp 28–29 Remark 2; M p 60 Table 4 note/capital bullet; S p 20 tax proof; results/theory_independent_checks.json |
| GPT-M3 | Fixed | resolved | Instantaneous acquired run-rate growth and annual simple growth now have separate definitions. The annual current-revenue identity includes 1+g_t and defines the relevant annual-revenue multiple; independent algebra confirms it. | M p 51 Definition 5; S p 27 S5 proof; results/theory_independent_checks.json |
| GPT-M4 | Fixed | resolved | Economic interpretation is repaired, including exit value. The author verifier passes 202/202 and checks the 173% later value and 7.4% break-even exit calculation; calibration and path reruns agree with committed tables. | M pp 5,64,70; code/verify_theory.py:3239; results/computational/verify_theory/stdout.txt |
| GPT-M5 | Fixed | partly resolved | BCG/WEF/error-rate source descriptions and scenario labels are materially repaired and the joint envelope is disclosed. The survey-to-process transport remains an assumed calibration, not validated estimation; the all-attempt cost approximation and LHS precision claims need F14/F05. | M pp 59,62–64; S pp 9–10 S2.8–S2.9,38–44 Table S11,57–60 S9–S10 |
| GPT-M6 | Partly | partly resolved | The 999-replication empirical program now runs successfully: all 65 bootstrap arrays are exactly equal and the estimates/families match. Broad deletion code is implemented; full specification-grid execution is not claimed. Publish distinct-firm tail counts (F10); access/Lean objections are superseded by Part C. | M pp 40–49; S S7/S11; code/spec_curve.py:790; results/computational/reproduced_output_comparison.json |
| GPT-1 | Fixed | resolved | S3 includes the omitted linear forcing contribution and resonant logarithmic case. The free homogeneous coefficient remains, so the local limit alone does not select a global HJB solution. | S p 16 S3 HJB as an ODE; expert theory derivation summarized in Part B |
| GPT-2 | Fixed | resolved | The example now says the decision weight reaches a minimum near 80% of the cap and then rises toward the never-spend multiple; it no longer asserts global monotonic decline. The plotted numerical path was not rerun. | M pp 21,23 §§3.5–3.6; S p 6 S2.2 |
| GPT-3 | Already handled | resolved | Accept the already-handled response: the directional gain is explicitly first order and the finite-change bracket is stated separately. Do not sustain an objection that omits the printed qualifier. | M p 20 Corollary 2 and Corollary 3 lead-in; S p 15 associated proofs |
| GPT-4 | Fixed | partly resolved | Main prose now correctly labels upper-bound crossing and gives a 99% comparison. S10/Table S18 still call a finite crossing an expected completion year, although the exact divisible recurrence has an infinite geometric tail (F12). | M p 63; S pp 24,59–60; results/execution_checks.json |
| GPT-5 | Fixed | resolved | The share-headroom budget is a bound on excess above R_infinity. The Rule-of-1000 claim is now restricted to market growth software markets have sustained, rather than arbitrary G. F02 is a separate residual necessity overclaim. | M pp 18–19 Proposition 1, pp 5,61 §7.2; S p 29 S6 |
| GPT-6 | Fixed | resolved | The objective set must include combinations that could jointly constitute a material weakness; a narrower set yields a necessary-only condition. This matches the combined-deficiency qualification in AS 2201. Numeric probability thresholds remain scenarios. | M p 31 Proposition 5(b); PCAOB AS 2201 .62–.65 and .A7 |
| GPT-7 | Already handled | resolved | Accept already handled. The constraint is per objective, and the example explicitly translates a firm-wide 5% across ten independent objectives into about 0.51% each. This does not claim independence is universally appropriate. | S p 55 Remark S10; M p 31 Proposition 5; results/controls_cost_units.json |
| GPT-8 | Fixed | resolved | Independent opportunity draws are explicit, and S2.6 now contrasts a persistent common-mode state. Own calculations reproduce approximately 0.519% versus 11.352%, so the conditional sensitivity is repaired. | M p 30 Assumption 7; S p 8 S2.6; results/controls_cost_units.json |
| GPT-9 | Fixed | resolved | The PDFs distinguish 58 durable from about 53 net. Calibration/do-nothing paths rerun and match committed results; the abstract/main text gate passes. Exact-current-output verification now supplements the PDF repair. | M pp 1–2,5,63–64,74; results/computational/calibrate_horizons; results/computational/s12_reestimation_comparison.json |
| GPT-10 | Fixed | resolved | The current text separates Wood (1975) from the 2025 retrospective and attributes the opportunity-frontier/value tangency appropriately. The source subreview checked the publisher text; the root repeat fetch hit an inaccessible redirect, recorded as an access limit. | M p 8 §2.1 and bibliography; Wood (2025) publisher record https://academic.oup.com/cje/article/49/5/1073/8315769 |
| GPT-11 | Fixed | resolved | No unresolved todo R2 marker is present in the attached current PDF text. R2 and the subsequent sample changes are actually described. This is a current-build check, not a source diff of the uninspected historical archive. | M pp 38–39 §4.2 and pp 83–87 Appendix A; full-PDF text search |
| GPT-12 | Fixed | resolved | Current accounting reconciles: 1732−457+57−2=1330; unaffected 1273; the 400 omissions sum 203+162+26+9. The letter expressly allows counts from earlier reruns to differ. | M p 40 §4.5; results/empirical_arithmetic.json |
| GPT-13 | Fixed | partly resolved | Table 2 now correctly denies an equivalence test. But the cash-nonsteepening claim still counts an interval not below zero as support for no steepening in S19, with corresponding main prose (F11). | M p 43 Table 2 note, p 46 §5.3; S pp 62–63 Table S19/discussion |
| GPT-14 | Fixed | resolved | Current p_RW = .075 and MCSE ≈ .008 are disclosed; own arithmetic gives .00833. Full 999-resample estimates/families now reproduce, with all 65 stored arrays exact. The old .097 criticism is not a current-result finding. | M p 44; S p 31; results/computational/reproduced_output_comparison.json; results/empirical_arithmetic.json |
| GPT-15 | Fixed | resolved | The inferential target now expressly conditions on realized macroeconomic history and explains that firms, not years, are resampled. | S p 31 S7 Inference |
| GPT-16 | Fixed (3 Nov) | partly resolved | All-firm deletion code genuinely recomputes consequential statistics across four views. Our E1 g >= .60 counts show 41 GAAP / 42 cash firms, reassuring rather than a demonstrated few-cluster failure. Distinct-firm E2/cone support still should be published; F10 is a reporting request. | M pp 41,49; S p 63; code/spec_curve.py:790; results/empirical_code_checks.json |
| GPT-17 | Fixed | resolved | The paper adds SBC and a panel-basis cash score. Selected SEC inputs independently reproduce 112.6356, rounding to 112.6. This does not certify every annuity/user-cost acquisition adjustment. | M pp 54–56 §6/Table 3; SEC final prospectus F35/F59; results/controls_cost_units.json |
| GPT-18 | Fixed | resolved | The company's own organic measure is expressly distinguished from Definition 5; the text does not claim the unavailable pre-deal recognized-revenue split is observed. | M pp 54–55 §6; SEC prospectus organic-growth definition, footnote 30 |
| GPT-19 | Fixed | resolved | BCG's woe category now correctly means limited value; assigning zero realized value is explicitly the scenario construction. The primary source supports that distinction. | S p 9 S2.9; BCG (2020) Flipping the Odds, Exhibit 1 text |
| GPT-20 | Fixed | resolved | WEF's expectations through 2030 are now used as a loose analogy for change capacity, rather than measured annual process/work change. That fixes characterization; the transport remains a scenario assumption. | M p 62 §7.3 Pace/Capacity; S pp 38–39 Table S11; WEF (2025) Skills Outlook |
| GPT-21 | Fixed | resolved | The error-rate construction is explicitly class d and identifies different denominators and source types. This resolves the mischaracterization as a measured common-denominator rate; it does not validate an enterprise error probability. | S p 42 Table S11 and p 57 Table S17; S pp 9–10 S2.8–S2.9 |
| GPT-22 | Fixed | partly resolved | The successful-run qualification and labor-dollar versus revenue-unit correction are right: 2% × 60% = 1.2%. But the failed-attempt-inclusive doubling needs an assumed or measured failure cost (F14). S10 also expressly uses a broader 1.0–65% driver-implied range; the letter's one-range shorthand is not literal. | M p 59 §7.2; S p 9 S2.8, pp 39–40 Table S11, p 58 S10; METR Figure 14 |
| GPT-23 | Already handled | resolved | Accept already handled: the cross-survey population/outcome combination is labeled analogical and alternative readings are printed. Disclosure does not make the joined parameters an identified process-level distribution. | S pp 9–10 S2.9; M pp 62–64 |
| GPT-24 | Fixed | resolved | Sampling-only and joint scenario-law bands are distinguished. The stored million-draw input is verified and the supplement rebuild passes, but a fresh million-draw/search/Sobol run is not claimed. LHS precision justification remains separate F05. | M pp 2,5,7,64; S S10; code/mc_report_tex.py:220; results/computational/supp_extensions_complete |
| GPT-25 | Already handled | resolved | Accept already handled. The paper explicitly distinguishes agreement conditional on both models being wrong from the unmeasured conditional probability of the second being wrong given the first. | S p 8 S2.6 and p 54 Remark S9 |
| GPT-26 | Fixed | resolved | Wave lengths and cw=rho*Tpar are supplied. The calibration rerun reproduces committed JSON and tables byte for byte; 87 stress mirror/calibration checks pass. Exact path cash-flow implementation is now inspected and executed, resolving the previous access-based remainder. | S S2.7/Table S11; code/calibrate_horizons.py; results/computational/calibrate_horizons; results/computational/mc_verify_only |
| GPT-27 | Fixed | resolved | The main text now says the local quantile is steeper 'here', describing the observed comparison instead of a general guaranteed ordering. | M p 46 §5.3 |
| GPT-28 | Fixed | resolved | Remark 2 adds the 174A(c) election over at least 60 months. The statutory text supports the limited point that optional amortization can give a deduction-PV factor below one. | M p 29 Remark 2; 26 U.S.C. 174A(c)(1); source audit |
| GPT-29 | Already handled | resolved | Accept already handled. Attestation prevalence is explicitly not escape probability, and the discussion acknowledges that assumed human common-mode risk could be too high rather than deducing the remote threshold from prevalence. | S p 55 Remark S10 The threshold |
| GPT-30 | Already handled | resolved | Accept already handled. The paper fixes a realized benefit share per process and explicitly explains that fresh independent benefit draws with free outcome-based reversion could raise the attainable limit. It does not silently assume the latter. | M pp 33,35–36 Definition 4/Proposition 7 discussion; S p 24 proof |
| GPT-31 | Already handled | resolved | Current SIC/latest descriptions, latest-filed screens/bridge values and consolidated margins with organic growth are disclosed. These remain scope limitations rather than repaired identification, but the response does not conceal them. | M pp 37–41 §§4.1–4.6; S p 31 S7 Known limitations |
| GPT-32 | Already handled | resolved | Accept already handled. Proposition 2 is explicitly conditional on (H); the written proof does not claim an existence/regularity theorem establishing (H). | M p 22 Proposition 2; S p 16 verification/HJB discussion |
| GPT-33 | Already handled | resolved | Accept already handled. The netted/all/none selling-spend bases and reversal of the G&A/growth-engine ranking are printed and the comparison is not represented as a universal ranking of all levers. | M pp 68–69 Table 7/§7.5 and p 7 caution 6; S p 60 ST6 |
| GPT-34 | Partly | resolved | The personal connection supplies the pinned unmerged code/data. All four required commands pass; generated macros/tables/check records match, and rebuilt PDF text equals the attachments. The 999-resample run and pinned Lean main/check targets also execute. Full raw/stress/specification regeneration remains a disclosed scope limit, not an access failure. | results/computational/branch_comparison.json; snapshot_integrity.json; per-command run.json; pdf_comparison.json |
| GPT-35 | Already handled | resolved | Direct proof review and independent arithmetic support the static confirmations. Pinned Lean source types match the stated restricted scope; main and check-target results are recorded in Part C. This does not establish dynamic (H) existence or empirical calibration validity. | M §§3.1–3.6; S3–S4; expert_notes/theory_code_addendum.md; results/computational/lean_axioms.json |
| GPT-36 | Not valid | resolved | Accept the author's rejection of a claimed independence error in the current paper: reporting 450 generated pairs is not asserting 450 independent transcripts, and no independent-binomial precision is derived from that count. The full prior finding was not independently reconstructed; primary clinical full text could not be fetched, limiting historical adjudication. | S p 42 Table S11; primary clinical indexed design/abstract; source-access limits |
| GPT-37 | Not valid | resolved | Accept the narrow rounding response: arithmetic on rounded headline inputs cannot overturn a stored net result. The current PDFs consistently print 58 durable / about 53 net. The old build and its historical exact calculation were not independently reconstructed; no historical rerun is claimed. | M pp 63–64 Table 5/§7.3; S p 59 Table S18 central 57.8; Part C limitations |
| ST-1 | Conditional qualification supplied | partly resolved | The abstract and cautions condition 32.5% on central costs, compute 6% and k=0; the ranges are visible. The p61/p73 conclusion still presents negligible capital/near-complete automation as necessities, contrary to the model's scope and negative-capital exception (F02). | M pp 1–2,5,7,60–61,73; S pp 58–59 ST1; results/execution_checks.json |
| ST-2 | Conditional qualification supplied | resolved | The 54–62 band is labeled anchor/sampling-only and the joint 40.7–66.7 output band is given with assumed input laws. It is not claimed here as an empirical forecast interval; simulation precision is a separate F05 issue. | M pp 1–2,5,7,64,74; S pp 58–60 ST2/Figure S1 |
| ST-3 | Conditional qualification supplied | partly resolved | The reported central-execution minimum 4.99 years is a counterexample to the remaining unqualified five-year-failure sentences in pp5/64. P 74 correctly states exceptions. Use central inputs rather than central execution alone (F13). | M pp 5,64,74; S p 59 ST3/Table S18 |
| ST-4 | Conditional qualification supplied | resolved | The revised text acknowledges a few marginally positive points under central execution and distinguishes them from the full-box outcomes. This repairs wording, while the numerical extrema themselves are not reproduced. | M pp 2,5,64; S pp 59–60 ST4 |
| ST-5 | Conditional qualification supplied | resolved | The 41% figure is attached to central execution and the 4.9–85.0% range is supplied. It is not treated as a universal realized share across execution designs. | M pp 5,63–64,74; S p 60 ST5 |
| ST-6 | Conditional qualification supplied | resolved | The one-of-six growth-engine win count is tied to central maintenance and its 0–1 sensitivity range is printed; the all/none spend bases are separately reported. | M pp 2–3,68–69,74; S p 60 ST6 |

### Broader response claims

| Claim | Independent assessment |
|---|---|
| Mathematical repairs and (H) | Written proof review supports the repairs; M1's eight numerical pairs now reproduce to 1e-10. Dynamic existence/regularity is still assumed and disclosed. Static formal scope is assessed separately from dynamic existence. |
| R2 applied to the whole main sample | Code does apply the keyword rule to all covered descriptions. That partial rule does not establish that all 284 retained registrants principally sell software; F17 remains. |
| Bootstrap, deletion and specification sensitivity | The actual source implements firm-cluster resampling and all-firm deletion. Published counts reconcile. Full-bootstrap and specification-grid execution scopes are distinguished in Part C; source inspection alone is not called a rerun. |
| Joint stress test rerun | The stored million-draw inputs are now accessible and feed a successful S12 rebuild; the stress mirror check runs here. Fresh million-draw/corner/Sobol/search execution is not claimed. F05 concerns precision justification, not a demonstrated change in the central scenario band. |
| S12 added and audited | Valuation and do-nothing analyses are rerun here, and the supplement generator passes. The valuation NaN/censoring chain and price-growth omission are confirmed by actual code; a passing gate does not resolve them. |
| Fresh-clone build matches | Our pinned file bytes were independently checked against Git blob IDs. Source PDFs equal the supplied attachments. The four required commands pass and the rebuilt PDF text matches. This is our evidence, separate from the author's earlier reproduction claim. |
| Lean: 35 theorems / standard axioms | Source correspondence and build results are reported separately in the addendum and Part C. No author/reviewer assertion substitutes for those checks. |
| Capitalized-software and filing audit | Committed audit inputs/results are accessible and the empirical program uses them. We do not claim a fresh re-extraction of every SEC filing or a complete independent audit of all 234 compared values. |
| Legal/tax/citation repairs | Targeted primary-source checks support the repaired characterizations and qualifications, subject to access limits below. This is not an exhaustive bibliography audit. |
| Abstract preserves every condition | It retains many key conditions, but F01/F15/F17 remain. The conclusion's necessity claims and ownership conversion require substantive revision. |
| Rejected GPT-36/GPT-37 | Accept the narrow current-text and rounding responses. Reporting 450 generated pairs does not itself assert 450 independent transcripts; rounded inputs cannot refute an exact net score. Old-build historical provenance remains distinct from this current-build reproduction. |


**Preserved independent assessment.** The following Part B is the exact text frozen before repository access. Its statements about unavailable code describe that stage of the review and are superseded by the post-access addendum and current Part C. Its hash has not changed.

## Part B. Fresh assessment of the revised version

### Overall assessment and evidentiary boundary

This is a materially improved paper. Its static power-technology framework is coherent; several earlier objections have been repaired rather than merely answered in a letter. The population cone identity is corrected, the HJB expansion includes the forcing term, acquisition growth has separate instantaneous and annual units, and tax present value is distinguished from period cash. The empirical text is much more candid about non-identification, sample selection, common macroeconomic history, specification sensitivity and thin tails. The central path is expressly a scenario, and the paper distinguishes durable scores, transition costs, cash payback and investment value.

The remaining concerns are concentrated in translating conditional results into headline conclusions, one source-to-parameter conversion, and parts of the new analyses. I find three major interpretation/calibration issues and fourteen minor issues. Major means material to a prominent conclusion or decision-relevant numerical comparison; it does not mean the core static theorem is false. Two major findings concern summaries that are stronger than the paper's own equations. Some specialist subreviews regarded these as wording issues; I assign major priority because the abstract, executive summary and conclusion repeat them as economic implications.

The supplied PDFs are the authority for manuscript claims. No repository checkout, stored numerical outputs, formalization or old review archive was obtained. Accordingly, the 35 Lean theorem claims, empirical multipliers, million-draw stress test, specification curve, regressions and macro gates remain author-reported computational results. Independent calculations below establish particular identities, counterexamples and source reconciliations; they do not certify those pipelines. No restricted reviewer folders, other response letters or joint response were read before this assessment or its hash was saved.

### Theorems, proofs and the Lean formalization

Direct derivation supports the decreasing concave frontier, the interior tangency condition, the capital-for-labor finite-change bracket and the decomposition into a saturated term and transient growth surplus, within the stated power model. In 1,000 seeded numerical evaluations, the static first-order, tangency and decomposition identities agreed to a maximum relative discrepancy of approximately 5.13e-15. This is a useful implementation-independent arithmetic check, not proof by simulation.

For a continuous distribution of chosen growth on a strictly decreasing common frontier, the corrected identity is

\[
\Psi_\chi(t)=m^*\{F^{-1}[1-\chi+\chi F(t)]\}.
\]

Its chain rule contains the density ratio printed in S2.3, supplement p7. Dense sampling does not remove that factor. The identity is repaired; the E1-data multiplier 2.1–4.0 cannot be independently reproduced without the data and exact estimator. F06 below concerns the interpretation of that multiplier, rather than the identity itself.

The HJB expansion in S3 p16 has the corrected linear forcing term, with the appropriate logarithmic resonance case. It preserves the free homogeneous coefficient. Proposition 2 is now explicitly a verification result under (H); the paper does not establish existence and regularity of a solution satisfying (H). I do not renew that disclosed limitation as a supposedly missing unconditional proof. The verification argument is coherent on its stated assumptions, but the dynamic result is outside the reported Lean scope.

S4 pp26–27 appropriately limits formalization to static Sections 3.1–3.5, excluding Corollary 3(iv) and numerical examples. It distinguishes kernel checking from correspondence between the Lean statements and the paper, explains Caratheodory paths when spend jumps, and describes the audit history. Those are strengths. Without `formal/`, its toolchain and a build, this review cannot verify theorem statements, absence of `sorry` or extra axioms, imports, instances or semantic correspondence. An independent build and statement-by-statement mapping are still needed; arithmetic scripts cannot substitute for them.

### Estimation, inference, sample rules and S11

The revised E2 accounting reconciles: 1,732−457+57−2=1,330, with 1,273 unaffected firm-years and 400 affected years omitted. The paper discloses that adjusted growth is paired with consolidated margins and that the views are related sensitivities, not independent replications. Its cluster bootstrap is explicitly conditional on realized years and common shocks. The current Romano–Wolf p-value .075 has a binomial-style Monte Carlo standard error about .00833 at 999 draws. The old .097 boundary criticism must not be repeated as if it were the current result. This arithmetic does not verify the adjustment implementation.

R2 has now been applied across all 293 descriptions using the stated keyword rule. Application to the entire universe is different from complete substantive classification: the manuscript admits that many registrants both independent readers regard as nonsoftware remain in the baseline. S11 properly exposes how much choices change magnitudes: the headline decline is among the largest and the baseline slope among the flattest in its contemplated choices. Forward pairing and all-firm deletion checks are substantial improvements. Specification shares are not probabilities over a scientifically privileged choice distribution; unadjusted interval shares do not replace familywise error control. The manuscript generally says this. F08–F11 and F17 identify specific residual issues; none establishes that every empirical result is wrong.

The data describe chosen points across firms. They do not identify an individual production frontier, its decision weight, the causal effect of AI, or an empirically measured minimum enterprise cost. A specialist journal could assess this as a theoretical synthesis with descriptive evidence and conditional scenarios; stronger claims to identified economic limits would need additional identification, rather than additional scenario draws alone.

### Joint stress test and the three S12 additions

S10 is a serious improvement in sensitivity disclosure. It says that finite search is not proof and that uniform/log-uniform laws are assumptions. The joint score band 40.7–66.7 is a distribution of model outputs under those laws, not a 90% empirical confidence interval for what firms will achieve. The anchor-only interval 54–62 is now labeled separately. The numerical extrema and Sobol indices cannot be reproduced here. F05 concerns the stated Monte Carlo confidence justification, not a demonstrated change in those substantive scenario results.

S12.1 is an exploratory descriptive regression in public float/revenue observed after the accounting year. It is not an enterprise-value estimate, a return test, or a structural estimate of Lemma 5's within-firm screening weight. The paper discloses insider ownership, debt/cash, persistence and omitted characteristics. A coefficient ratio near 4.8 can be reported as a conditional association. Comparing its interval with a theoretical screening range does not validate or reject that theoretical weight without a mapping between the two estimands. F08 asks for a defensible ratio-confidence procedure; further controls and an alternative value measure would matter if this becomes a central empirical contribution.

S12.2 usefully distinguishes the gains from automating from a rival-driven deterioration in prices. Its reported score levels need the price–quantity–revenue reconciliation in F04. The automating/non-automating gap may survive because a common growth correction can cancel. No numeric replacement for the actual Table S21 is invented here.

S12.3's payback cancellation is plausible within its homogeneous proportional-cost program: while the program is running, changing capacity scales gains and in-flight costs together. Completion before payback breaks that cancellation, as the supplement acknowledges. Fixed setup costs, heterogeneous processes, changing bottlenecks, nonlinear capacity costs or different revenue paths would also break it. Thus this is a conditional mechanism, not evidence that execution capacity generally does not affect a real enterprise's funding or payback. Its sweeps and rank correlations remain unverified without code.

### New and remaining findings

#### F01 — Major: free-entry prose confuses disappearing rents with an unchanged accounting score

**Locator:** Main p1, final abstract sentence; p2 item8; p27 Proposition 4 intuition; p74 conclusion. Compare Proposition 4(b), p26, and Corollary 3(iv), p21.

**Evidence:** In the competitive limit without a scarce input, the paper itself gives `R = XG + (r−G)(ku+ac)/[u+r(ku+ac)]`. With X=1, G=.10, r=.15, ku=1 and ac=0, lowering u from .85 to .35 raises the score from .15 to .20 although the limiting Lerner rent is zero. All these values meet the stated assumptions. Normal return per dollar of revenue changes when the competitive price changes. Thus the repeated claim that automation raises the score only for firms with an uncopyable input is too strong. The abstract also omits the homogeneous-product and vanishing-replication-cost conditions.

**Fix:** State that competition removes economic rents under that specified market structure; distinguish the normal-return component of the score. For example: “With a homogeneous product and vanishing replication costs, competition removes operating rents. Persistent rents require a scarce input, while the cash score can still reflect normal returns on capital.” The theorem need not be replaced; the interpretation needs correction. Own counterexample: `results/theory_independent_checks.json`.

#### F02 — Major: the conclusion presents a conditional cost threshold as necessary automation and capital conditions

**Locator:** Main p61, “Three conclusions”; p73, conclusion. Compare Corollary 4(a),(c), p32, and the negative-capital exception, p60.

**Evidence:** The statement that sustained scores above 100 require near-complete automation and negligible capital needs does not follow from a cost-share formula. Corollary 4(c) explicitly allows a partial program to do better if some processes are not improving. The paper's own negative cash-capital case gives a direct contradiction to a universal 32.5% requirement: the central after-tax intercept .675, k=−.3 and G=.26 give .675+1.3×.26=1.013. Positive capital is not mathematically impossible either; larger G can offset its charge. This does not imply that such high market growth is empirically typical.

**Fix:** Keep 32.5% conditional on the chosen costs and k=0; state that positive capital raises and negative cash capital lowers the threshold. Describe near-complete automation as the scenario's assumed route to its costs, rather than a technology or staffing necessity established by the model. Own checks: `results/execution_checks.json`.

#### F03 — Major: the cited ownership calibration mixes annualized capital recovery with replacement cash

**Locator:** Supplement p56, Remark S11; main p60, capital bullet. Primary source: Epoch AI, Michael and Cottier, Data/Analysis and annual/upfront cost tables [EPOCH].

**Evidence:** The equation `kc = s_srv L_srv TCO` needs `s_srv TCO` to be replacement cash. Epoch's server share is a WACC-based annualized capital charge, not cash depreciation. Its tables give server stock 21,188, annualized server charge 5,021 and annual total 8,514, in USD millions. The stock/TCO ratio is 2.489, whereas .60×5.5=3.3. Other annualized assets also sit in the remaining cost share. Consequently the cited source does not establish the displayed ownership markup hurdles. Merely substituting 2.489 into the existing comparison would not reconcile all its components.

**Fix:** Rebuild from installed asset stocks, cash operations, replacement schedules and rental prices; derive cash-score and economic-value comparisons separately. Conditional algebra under a correctly defined replacement-share parameter can remain. Recompute all affected examples and gates. Own unit reconciliation: `results/controls_cost_units.json`.

#### F04 — Minor: S12.2 fixes both volume and revenue growth while prices change

**Locator:** Supplement p66, S12.2 first paragraph and Table S21 notes.

**Evidence:** Revenue is price times quantity, so `dlog S = dlog p + dlog Q`. A falling price path cannot leave both quantity and revenue-growth paths unchanged. The table appears to adjust margin while holding the score's growth term fixed. This can be a useful constant-growth margin comparison, but it is not the full price effect on a firm with the stated unchanged volume path. Common growth corrections may cancel in the two-firm gap, so this finding does not by itself overturn its ranking.

**Fix:** Specify which path is fixed. Either label a constant-revenue-growth counterfactual and its implied volume adjustment, or recompute growth and score levels from the actual price/quantity paths. Report whether levels and gaps change. The saved illustration of a 29% price fall is an accounting example, not a reconstruction of their unobserved yearly path.

#### F05 — Minor: the LHS precision guarantees use independence arguments without justification

**Locator:** Supplement p58, S10 “Monte Carlo precision”.

**Evidence:** The text calls iid share standard errors conservative for a Latin hypercube and labels order-statistic percentile intervals distribution-free 95% intervals. Randomized LHS points are dependent. An exact counterexample uses two points in two dimensions and the event that their coordinates occupy the same half of the unit square: the estimated share is 0 or 1, equally likely, with variance .25; two iid points give variance .125. Thus iid conservativeness is not general. The iid binomial/order-statistic coverage argument also cannot simply be transferred. This does not demonstrate inaccurate million-draw output bands.

**Fix:** Use independently randomized LHS replications or a design-valid variance/quantile procedure, or label the iid calculations as approximations. Two similar seeds are not a coverage proof. Counterexample: `results/execution_checks.json`.

#### F06 — Minor: the common-frontier interpretation still needs cap and support qualifications

**Locator:** Main p24, §3.7; supplement p7, S2.3; p33, Table S5 note.

**Evidence:** A firm's weight equals a frontier tangent only at an interior optimum. With a binding cap it can exceed the endpoint slope. For alpha=.3, ell=1, cap spend=1 and X=10, the capped optimum has growth1, although the steepest common-frontier slope magnitude is only 3.333. A lower-weight firm can choose an interior point on the same frontier. Also a cone threshold window ending at 60% includes observations above 60%; a bound on the frontier inside that window is not a bound on every included firm's weight. S2.3 additionally sets k=0 and reads the window as excess growth.

**Fix:** Restrict the weight claim to slack-cap firms choosing within the specified support, and carry the capital and growth-origin assumptions into the main numerical interpretation. Preserve the repaired cone identity and the broader non-identification result. Exact E1 multipliers still require reproduction.

#### F07 — Minor: the generalized concave-technology remark omits finite-optimum conditions

**Locator:** Supplement p3, Remark S4(a).

**Evidence:** For the stated general increasing concave growth function, an unbounded financing problem need not have a finite maximum. Take phi(spend)=spend, ell=1, X=2 and k=G=m0=0: the score equals spend and is unbounded. Even strict concavity is insufficient without a tail restriction: spend+log(1+spend) has the same problem. Envelope derivatives of a finite optimized value are then unavailable. The sublinear power model is unaffected.

**Fix:** Require a finite attained optimum and suitable differentiation conditions; use a finite cap or an appropriate sublinear tail condition, with the constrained envelope when caps bind.

#### F08 — Minor: valuation ratio intervals combine two procedures without defining their coverage

**Locator:** Supplement p65, S12.1, Table S20 note; p66 reading.

**Evidence:** The note calls the interval the 5th–95th bootstrap percentiles, then replaces its upper endpoint with infinity if more than 5% of bootstrap margin coefficients are nonpositive. That additional convention is not an ordinary percentile interval, nor is a Fieller/test-inversion confidence set specified. A sign-changing denominator can produce unbounded or disconnected ratio sets. This does not establish that the finite all-year interval 3.1–15.8 is wrong; its draws are unavailable.

**Fix:** Report denominator uncertainty and sign shares; distinguish finite-ratio percentiles from a weak-denominator warning, or implement and document a suitable ratio-confidence set. Keep the public-float association distinct from a structural screening weight.

#### F09 — Minor: the interest-income robustness interval contradicts its verbal interpretation

**Locator:** Supplement p31, S7 final paragraph; main p41, §4.6.

**Evidence:** The supplement prints a −14.2-point change with interval [−35.9,−2.3], then says both intervals on this subsample include zero. The displayed interval excludes zero. The main text repeats the statement. This was checked on the rendered PDF, not inferred from a missing sign in extraction.

**Fix:** Regenerate the bridge, reconcile the interval and prose, and print both paired-sample intervals. Retain the thin-sample warning. The contradiction alone does not determine which element is stale.

#### F10 — Minor: distinct-firm support for consequential cone cells remains missing

**Locator:** Main p41, §5.1; supplement p63, S11 “Leave one firm out”; compare the improved anchor disclosure, main p49.

**Evidence:** The E2 60% cell has 37 firm-years and its deletion minimum is 34. The relevant passages do not state the number of distinct firms. All-firm deletion robustness is useful, but does not supply the number of independent tail clusters or establish cluster-bootstrap adequacy. The anchor now does report 14 firm-years/7 firms and concentration, which should be credited.

**Fix:** Give firm-years, distinct firms, largest-firm share and undefined-draw frequency for consequential endpoint and period cells. Decide on additional cluster sensitivity after seeing those counts; do not automatically declare an interval invalid merely because it uses 37 firm-years.

#### F11 — Minor: “did not steepen” still treats lack of detection as a directional result

**Locator:** Main p46, §5.3; supplement p62, Table S19 cash-steepening row; p63 discussion.

**Evidence:** Table 2's no-equivalence note is repaired. But S19 counts an interval not wholly below zero as support for “cash frontier did not steepen”, and p46 makes a corresponding conclusion. Nonnegative point estimates in particular adjusted views are descriptive facts; failure to detect a negative change is not a test of equivalence or non-steepening.

**Fix:** Say no common statistically detected steepening is established across the adjusted views. Label the interval criterion as lack of detected steepening under that test, and keep point-estimate ordering separate.

#### F12 — Minor: stress-test completion labels retain the exact-recurrence problem

**Locator:** Supplement p59, Table S18 “expected completion year”; p60, “Other failures”. Compare main p63 and supplement p24.

**Evidence:** The exact divisible recurrence leaves positive remaining mass at every finite wave once it enters its geometric tail. The finite date being tabulated is an upper-bound crossing. Main prose correctly says this, but S18 still calls it expected completion and p60 says the program completes. Own printed-parameter checks recover the upper-bound/99% wave distinction; exact calendar dates were not reconstructed.

**Fix:** Use “upper-bound crossing date” throughout, or tabulate a specified completion fraction such as 99% consistently. Do not conflate the divisible fluid recurrence with almost-sure completion in the separate finite-process model.

#### F13 — Minor: central execution alone does not imply failure of five-year payback

**Locator:** Main pp5 and 64; compare supplement p59, ST-3/Table S18, and main p74.

**Evidence:** The sensitivity range at central execution is 4.99–9.29 years. Thus the unqualified p5/p64 inference that the program fails a five-year test “under central execution” has exceptions within its own reported range. The p74 conclusion and the central-scenario abstract are better qualified.

**Fix:** Use “at the central inputs” for 7.5 years and failure of five-year payback; retain the range and exceptions when other inputs vary. This is a condition repair, not evidence that the 7.5-year computation is wrong.

#### F14 — Minor: failed-attempt-inclusive compute cost needs a further cost assumption

**Locator:** Main p59; supplement p9, S2.8; Table S11, pp39–40.

**Evidence:** Multiplying compute per labor dollar by the labor share correctly gives revenue units. But a 1% successful-run cost at 50% success becomes 2% per completion only if failed attempts have the same average cost as successful attempts. In general total cost per completion is `c_success + [(1−p)/p] c_failure`. The benchmark's success-conditioned costs do not determine the missing failure-cost term or the success rate of an enterprise task mix [METR].

**Fix:** State that approximation or compute all-attempt spending per accepted task from run data. Keep 1.2% as a conditional low scenario, with review/integration costs separately covered, rather than an observed enterprise minimum.

#### F15 — Minor: the abstract's plain-language decomposition can charge capital twice

**Locator:** Main p1; compare Assumption 3 p14 and Lemma 2, pp16–17.

**Evidence:** “Margin it earns growing with its market” ordinarily means m0−kG. Adding market growth “net of the capital growth needs” would then subtract kG again. The correct decomposition is m0+(1−k)G+surplus, equivalently the cash margin at market growth plus G plus surplus.

**Fix:** Say “margin before growth investment” in the first term, or add unnetted market growth to the actual cash margin at market growth. This is summary ambiguity, not a failure of the displayed theorem.

#### F16 — Minor: the summary drops the one-objective scope of the accountability example

**Locator:** Main p2, item9; supplement pp54–55, Remark S10; main p30.

**Evidence:** The 0.37–0.38% example prices one control objective, direct audit/program costs and a particular application line. The executive sentence calls it a floor of a $1 billion firm without retaining “one control objective”. Entity/policy/provider controls are expressly unpriced elsewhere. Nearby illustrative wording helps, but does not make this a complete enterprise budget.

**Fix:** Carry the one-objective scope and low-side fee choice into the sentence, and distinguish this example from the ceiling's separate accountability band and a company's complete obligations.

#### F17 — Minor: “284 software companies” exceeds what the baseline screen establishes

**Locator:** Main p1 abstract; p38, R2; supplement pp31–32.

**Evidence:** The keyword screen excludes 8 registrants; both blind readers regard 49 as nonsoftware. The manuscript acknowledges missed games, infrastructure and other business types. The baseline is a transparent SIC7372-based screen, not a demonstrated pure principal-software population. The broader reader exclusion removes another 223 firm-years and changes magnitudes, though many signs survive.

**Fix:** Say “284 SEC registrants classified in SIC7372, after the stated screens” or “software-classified registrants”. If the intended population is narrower, adjudicate classifications by an outcome-blind substantive rule and rerun; do not silently replace the screen after seeing results.

### Citations, legal and tax checks: confirmed repairs and limits

The targeted source audit supports the combined-deficiency qualification in Proposition 5(b): AS2201 .62–.65 and .A7 require evaluation of combinations, while no fixed numeric remote threshold is prescribed [PCAOB]. The 5%/1% values remain illustrative model judgments, not legal safe harbors. The per-objective/firm-level distinction and the temporal-persistence sensitivity are now explicit. Own calculations give about 11.352% annual escape under independent opportunities versus .519% with a period-persistent AI common mode in the example.

The domestic R&E amortization election of at least 60 months under 174A(c), the qualified-property bonus-depreciation rule and the relevant elect-out/foreign-use qualifications are supported by statutory text and IRS material [174A; IRS]. The model also expressly assumes full loss offset and distinguishes purchase-date PV from period deductions. Independent shield values reproduce approximately .80, .53 and .25 in the printed cases. These are conditional financial-model calculations, not a taxpayer-specific tax opinion.

The revised banking-guidance caveat is supported by SR26-2 attachment footnote3, which excludes generative/agentic models from that guidance's scope [FED]. The EU high-risk dates in Table S17 are confirmed by the Commission's consolidated Article113 and Council adoption record: AnnexIII 2 December 2027, AnnexI 2 August 2028 [EU]. They should not be attacked on the basis of superseded dates. The compliance line nevertheless excludes those high-risk duties and remains a scoped scenario.

The BCG “woe” source describes limited value, and the revised paper now explicitly makes zero realization a scenario assignment. WEF training/skills expectations to 2030 are no longer described as measured annual process change [BCG; WEF]. The error-rate sum is expressly reclassified as a scenario built from different denominators; that is an honest repair to characterization, not validation of a measured enterprise error rate. The conditional wrong-answer agreement limitation is correctly stated. Reporting 450 generated clinical transcript-note pairs does not itself claim 450 independent transcripts; the alleged independence error should not be sustained against the current text.

The acquisition-case panel-basis cash score independently reconciles to 112.6356 from the selected SEC prospectus inputs, which rounds to 112.6 [SEC]. This does not reproduce every acquired-capital annuity or user-cost scenario. The Wood citation is now separated into 1975 and 2025 works; the source subreview verified the publisher record and tangency equation, though the root's repeat publisher fetch failed on an inaccessible redirect. Primary clinical full text and the exact EUR-Lex OJ page also had access limitations; the official EU consolidated text/adoption record was accessible. This was a targeted citation audit, not certification of every bibliography entry or legal proposition.

### Abstract consistency judgment

The rewritten abstract correctly retains (H), the descriptive empirical status, central cost/fixed-price/compute conditions, the scenario label, durable versus in-flight scores, and the sampling-only interval. Its current three-of-four GAAP significance count is consistent with the updated .075 result and need not match an older response-table count. It still needs F01, F15 and F17: qualify the entry model, distinguish rents from accounting score, avoid the capital ambiguity, and state the actual sample scope. Its 7.5 years is properly attached to a central scenario; the broader five-year wording problem is in the main text. Plain language can preserve these conditions without restoring mathematical notation to the abstract.


## Part C. Computational reproduction

| Run | Seconds | Exit | Scope |
|---|---:|---:|---|
| biz_open_questions | 9.971 | 0 | Author program, isolated pinned copy |
| biz_valuation | 9.357 | 0 | Author program, isolated pinned copy |
| build_after_regeneration | 6.275 | 0 | Author program, isolated pinned copy |
| build_paper1 | 8.360 | 0 | Author program, isolated pinned copy |
| calibrate_horizons | 8.874 | 0 | Author program, isolated pinned copy |
| estimate_v3_999 | 342.697 | 0 | Author program, isolated pinned copy |
| lean_checks | 12.519 | 0 | Pinned Lean target; see compatibility disclosure |
| lean_main | 34.963 | 0 | Pinned Lean target; see compatibility disclosure |
| mc_verify_only | 11.009 | 0 | Stress/calibration mirrors; no fresh million draws |
| paper1_macros | 1.155 | 0 | Author program, isolated pinned copy |
| paper1_macros_after_regeneration | 0.882 | 0 | Author program, isolated pinned copy |
| supp_extensions | 9.860 | 0 | Initial partial materialization; optional heatmap comparison absent; superseded by complete rerun |
| supp_extensions_after_regeneration | 12.058 | 0 | Author program, isolated pinned copy |
| supp_extensions_complete | 13.512 | 0 | Author program, isolated pinned copy |
| verify_theory | 111.211 | 0 | Author program, isolated pinned copy |

Exact commands, environments, UTC timestamps, stdout/stderr and exit codes are in results/computational/<run>/run.json and companion logs. Review programs and seeds are bundled under scripts/ and results/. Detailed comparisons, numerical tolerances and remaining limits follow in the post-access addendum; no unrun stage is inferred successful from a different stage.

### Post-access assessment: what the execution establishes

This update supersedes the frozen Part B's statements that code, multipliers, Lean and the required commands were unavailable. It preserves the original independence record. Source inspection and execution corroborate many repairs, while confirming several residual scientific issues. No restricted response or other reviewer folder was needed or read.

#### Reproduction outcomes and observed differences

| Component | Observed outcome | Boundary |
|---|---|---|
| Pinned source/data | 295 selected files match their Git blob IDs; no failed integrity check remains | A selected snapshot sufficient for these runs, not a full raw-data clone |
| Supplied versus committed PDFs | Both are byte-identical: the main and supplement hashes match the attachments | This establishes which build was reviewed |
| Theory verifier | 202/202 checks pass in 111.21 seconds | Checks conditional formulas/text gates, not every external-source conversion or prose implication |
| Main macro generator | 1, 730 macros generated; committed macros and text-check output match | Repeated after empirical/calibration regeneration and still passes |
| Supplement generator | 64 macros, three tables and 27/27 checks pass with complete inputs | Reads the actual committed million-draw CSV; does not regenerate that simulation |
| Initial supplement attempt | 26/26 checks passed while optional heatmap CSV was absent | One check record differed. After obtaining the heatmap, the complete 27-check output matches; this initial incomplete run is retained and superseded |
| PDF builds | 87 and 72 pages; extracted layout-preserving text exactly equals the supplied PDFs, including after the final rebuild | Rebuilt PDF binary hashes differ; extraction detected no text/content difference. Text equality does not itself establish pixel-level identity |
| Main empirical estimation program | 999 replications, seed0=20261030, all 16 documented block seeds, 342.70 seconds with 6 workers | Uses the pinned filing-derived panels/extract and overrides; not a fresh SEC re-extraction |
| Bootstrap NPZ | All 65 arrays, including 999-draw blocks, are exactly equal, with NaNs compared as NaNs | Compressed NPZ container bytes differ despite exact decompressed arrays |
| Empirical JSON | Published estimates, families, samples, anchor and cone outputs match | 130 scalar differences: 1 worker count (2 → 6), 100 within-regression floating-point differences and 29 solver-check diagnostics. All 100 within-regression differences are below 1e-10; the largest solver-diagnostic change is 3.777586 × 10⁻⁷. Exact LP/bootstrap outputs remain matched |
| Calibration | calibration_anchor_v3.json, frontier_slope_v3.json and calibration_results.json byte-identical; calibration/tornado and empirical TeX tables match | Empirical JSON/NPZ binary differences must not be mislabeled byte-identical |
| Stress mirrors | 87 passed, 0 failed; shadow calibration tables byte-identical | Vector/scalar/calibration agreement checks, not fresh million draws/corners/search/Sobol |
| S12.1 valuation program | All point estimates and bootstrap intervals reproduce; 13 JSON scalar differences, all below 1e-10 (maximum 2.7755575615628914 × 10⁻¹⁶) | The same NaN/censoring defect is reproduced, not repaired |
| S12.2 path program | paths.json byte-identical | The retained price-growth assumption is the subject of F04 |
| Lean main library | lake build passes in 34.96 seconds after dependency preparation | Author project compiled against pinned official Mathlib dependency cache |
| Lean concrete checks | lake build RuleOfXChecks passes in 12.52 seconds | Separate non-default target actually executed |
| Elaborated axioms | 35 main results report only propext, Classical.choice and Quot.sound | Supports restricted formal scope; does not prove dynamic (H), general growth remarks, calibrations or empirical interpretation |

`results/computational/reproduced_output_comparison.json` lists all scalar and array differences, not merely a rounded summary. `minimum_suite_comparison.json` records zero modified committed files after the complete minimum suite, before optional re-estimation. `changed_files_after_empirical.json` and the final comparison record the subsequently changed JSON/NPZ files. The numeric tolerances distinguish exact equality from roundoff; the 1e-10 comparison threshold is a disclosed numerical tolerance, not an inferential confidence threshold.

The lockfile records Python 3.13.18; this reproduction uses Python 3.12.14. All 35 package versions in requirements-lock.txt match exactly, including NumPy, Pandas, SciPy, Statsmodels and SymPy. The recorded numerical re-estimation commands set BLAS/OMP threads to 1; the empirical run used 6 processes versus the committed 2. The host allows 8 CPU cores and 8 GiB RAM. Exact executable paths, commands, versions, timestamps, run times and logs are retained. Small scalar/solver differences are compatible with differing numerical execution environments; the review does not assert a proven exclusive cause for each difference.

Lean used the official 4.35.0 Linux release (commit eb6cafb7290e8bd5f2937522d8d804f58f02bafc) and Mathlib revision 56a005855ea17e0b0958f73ec801ae140b0a1679. The host exposes `/proc/self/exe` but denies the equivalent numeric own-PID path that this Lean release uses to locate itself. An openly included compatibility shim redirects only that exact own-process lookup to `/proc/self/exe`; it changes no author source, proof term, elaborator, kernel or axiom. Both targets then build. Mathlib's pinned-revision official olean cache was used; its dependencies were not rebuilt from source. The author project itself was freshly compiled. Deprecation/module-system warnings occurred; no proof error occurred. Source-level correspondence was checked independently of build success.

#### Effect on the mathematical assessment

The actual Lean types support the restricted static claims. The frontier is derived from dominance, not defined to equal the desired graph. Maximal-score linkage is included in saturation/envelope statements. Cap and interior conditions are explicit. Continuous budget statements conclude integrability and use absolutely continuous paths with an almost-everywhere ODE; the induced path is constructed and verified. Concrete examples discharge hypotheses, including cap equality, negative capital where allowed, and spend paths with jumps. No new axiom or placeholder was found in a comment-aware source scan; the successful elaborated axiom output now provides stronger evidence than that scan alone.

M1's eight multiplier/steepest-slope pairs independently match within 1e-10: GAAP multiplier 2.076–4.006 and largest-window slope 0.415–0.802; cash multiplier 2.072–3.994 and slope 0.351–0.677. F06 remains an interpretation qualifier: the calculation sets k = 0 and treats growth as excess growth, while the 0.60 threshold window does not bound all firms entering its cones. There are 64 GAAP and 65 cash observations above 0.60. A hypothetical derivative bound within that window cannot automatically bound every contributing firm's decision weight or apply at a financing cap.

The written-model issues F01/F02/F07 are outside what this restricted static Lean build settles. A formal proof of a stated conditional theorem does not add missing conditions to an abstract or conclusion. The successful kernel build therefore strengthens the static-model assessment without resolving the free-entry/accounting-score overstatement, the necessity claim or the generalized-technology finite-optimum issue.

#### Effect on empirical and S12 findings

F08 is now a confirmed implementation issue. `code/biz_valuation.py:85–90` replaces every nonpositive bootstrap margin coefficient with positive infinity rather than retaining the signed ratio. NumPy's interpolated quantile produces NaN upper endpoints for cash 2010–19 and GAAP score ≥ 40. `code/supp_extensions.py:123` renders any nonfinite upper endpoint as infinity, conflating an undefined calculation with a justified unbounded confidence set. These outcomes reproduce here. Define the ratio's domain and use a documented weak-denominator method; make table generation reject NaN and distinguish it from intentional unboundedness.

An independent NumPy implementation, without importing the author's regression program, matched all 10 coefficient pairs within 7.2 × 10⁻¹⁵ and cluster standard errors within 10⁻⁹. Its asymptotic 90% Wald–Fieller diagnostic gives cash/all [3.0097, 13.7038], GAAP/all [3.1293, 7.6287], cash 2010–19 (−∞, −118.0697] ∪ [2.4992, +∞), and all real numbers for GAAP score ≥ 40. These are alternative asymptotic diagnostics, not exact finite-sample coverage claims or mandatory replacement numbers. The main all-year lower bounds remain above 2.8. Thus F08 does not overturn the all-year descriptive association; it invalidates the blanket characterization of the censored/undefined intervals as ordinary ratio percentiles. Neither method turns an association in public float/revenue into the model's structural screening weight.

F09 is precisely an interval-level mismatch. Stored/rerun before-net-interest cash change has a 90% interval [−0.35902, −0.02252] and a 95% interval [−0.39845, +0.00081]. The former excludes zero; the latter includes it. Both 95% intervals can include zero while only one of the displayed 90% intervals does. Repair the main/supplement wording accordingly, and describe the adjustment as before net after-tax interest where appropriate.

F10 should be read narrowly. Independent E1 counts show 41 distinct firms in the 64 GAAP firm-years with g ≥ 0.60, and 42 firms in 65 cash firm-years; the largest firm contributes 4 rows. Other consequential E1 tail cells have 56–66 firms; the 2023–25 cell with g ≥ 0.40 has 13 firms in 15 rows. This is reassuring support, rather than demonstrated reliance on a few firms. The all-firm deletion code genuinely recomputes the relevant statistics. The remaining request is to publish unique-firm support for E2/consequential cells; source inspection and these E1 counts do not constitute a fresh full specification-grid bootstrap.

F11 is confirmed by `code/spec_curve.py:470–473`: “success” for cash non-steepening is an interval not wholly below zero. That is lack of detected steepening, rather than evidence of equivalence or no steepening. F04 is confirmed by `code/biz_open_questions.py:51–61, 68–78`: price changes while the score adds the original growth term; the table note also holds quantity fixed. Choose and state a coherent constant-revenue-growth margin comparison or compute revenue growth from the stated quantity and price path. A common correction may cancel in the two-firm gap, so the defect does not automatically reverse the ranking.

F05 is confirmed by `code/mc_report_tex.py:220–236`: iid share errors and iid rank formulas are applied to dependent randomized LHS points without the asserted general conservativeness/coverage proof. The exact two-point counterexample remains valid. The scrambled-QMC Sobol row bootstrap also deserves approximate-coverage language or repeated independent scrambles. These issues do not demonstrate that the stored million-draw score band or central Sobol rankings materially change.

F12's “expected completion” label is attached to an upper-bound capped attempt formula in `code/mc_claims.py:145–159`, rather than the exact geometric-tail divisible recurrence. S12.3's pre-completion capacity/payback cancellation is genuinely implemented under proportional benefits and transition costs and passes the supplement sweeps. Fixed setup costs, heterogeneous sequencing and endogenous capacity costs remain outside that cancellation. F13 is still a wording issue: central execution alone permits the reported 4.99-year minimum.

#### Effect on ownership, compute and accountability findings

F03 is confirmed rather than resolved by numerical agreement. `code/verify_theory.py:1763` defines capital as server annualized-cost share × life × TCO, then checks the own-minus-buy algebra conditional on that definition; `code/paper1_macros.py:211–214` hardcodes 3.3. Epoch's annualized capital recovery includes WACC, so an annualized charge A = CRF × K does not imply K = life × A unless CRF = 1/life. The source conversion must be rebuilt on consistent stock, replacement, cash and value units. Passing the verifier does not validate this calibration input.

F14 is also confirmed. `code/data_part2/08_params.py:149–161` filters successful runs for the cost observation; `code/calibrate_horizons.py:98–108` divides a successful-run cost of 1% by a fixed 0.50 success rate. That is a scenario approximation, rather than observed all-attempt cost. For independent retries, the completed-task mean is the mean successful-attempt cost plus (1 − p)/p times the mean failed-attempt cost; simple division requires an additional equality-of-cost assumption. Revenue-unit conversion, 1.2% = 2% × 60%, is correct.

Control probability/design arithmetic and the persistent-state sensitivity agree with the paper. F16 remains a scope issue: the 0.37–0.38% example covers one control objective under stated fee/risk assumptions, rather than a measured enterprise-wide floor.

A separate **minor companion-engine configuration defect**, rather than an additional demonstrated main-paper table error, is present at `engine/src/autofrontier/economics.py:306`: `owned_compute_share or default` replaces an explicit 0 with a nonzero configured default. Use an explicit `None` check. The shipped default 0 avoids a baseline effect. This is relevant when comparing rented/owned/mixed deployments. The engine's factor 3 is per reference rental-price dollar; S11's 3.3 is per at-cost TCO dollar. They must not be conflated. Conditional on engine defaults, running plus replacement at zero growth is 1 + 0.05u times the reference rental bill, while installed capital is 3u; this arithmetic is not empirical evidence that ownership saves money. Details and units are in expert_notes/controls_code_addendum.md.

Two editorial cleanups are also warranted: the `BudgetCont` module introduction predates its later induced-path construction, and some S12 program/README comments still call these analyses outside Paper 1. They are stale documentation, rather than proof or main-table failures.

#### Remaining reproduction limits

No fresh million-draw/second-seed/corner/search/Sobol experiment was executed. The actual committed million-draw CSV and summaries were recovered and verified, and the S12 statistics/gates were recomputed from them. The stress module's 87 mirror checks were executed separately. No fresh complete specification-curve grid/bootstrap, full v2 historical pipeline, raw SEC filing re-extraction or third-party benchmark acquisition was performed. The optional all-stage shell pipeline was not run. These limits remain explicit; they are not continuing repository-access failures.

The review's recommendation still rests on demonstrable mathematical, accounting, estimand and wording issues. It should no longer cite unavailable code as a reason to withhold the current build. Complete revisions should be followed by affected-stage reruns and a fresh cross-document check.

## Part D. Verdict and ranked revision sequence

### arXiv working paper

Hold this build for targeted major corrections, then release as conditional research. Repository access and the minimum computational suite are no longer release blockers. Required revisions, ranked:

1. Correct the rent-versus-accounting-score and technology-necessity claims (F01/F02), preserving homogeneous-product, cost, capital, growth and replication assumptions across abstract, executive summary and conclusion. Repair abstract capital/sample wording (F15/F17).
2. Rebuild ownership costs on consistent asset-stock, replacement-cash, running-cost and value units, or remove the unsupported numerical ownership hurdles (F03). A source-to-capital conversion is not validated by checking algebra conditional on that conversion.
3. Reconcile the S12 price–quantity–revenue counterfactual and its score levels; define valid weak-denominator ratio inference, reject NaN, and revise the LHS/QMC precision claims (F04/F08/F05). The all-year descriptive valuation association is not overturned by our diagnostic.
4. Repair interest-interval levels, non-steepening/completion/payback language and the remaining parameter/support/control/failure-cost qualifications (F06/F07/F09–F14/F16). Publish distinct-firm counts; our E1 counts do not show reliance on only a handful of clusters.
5. Rebuild and rerun the gates after these scientific changes, then compare all affected outputs. Extend the computation to the full specification/stress/raw-source pipeline if claiming independent reproduction of those stages. State each remaining scope limit accurately.

### Specialist field journal

Major revision remains; the present evidence is not submission-ready. The static conditional synthesis and descriptive growth–margin evidence may be useful, but the contribution should be positioned against prior growth–profit frontier and valuation theory. Decide whether the empirical section describes chosen operating points, tests a structural mechanism or estimates actual attainable limits. The current design principally supports the first. Specification curves and broader simulations do not identify a structural weight, a causal automation payoff or a real enterprise minimum cost.

For stronger claims, prioritize validated business-population classification; outcome-blind acquisition/capitalized-software measurement; adequate independent tail support; a well-defined valuation estimand and ratio confidence set; and representative accepted-task, failure/recovery, maintenance, oversight and utilization costs. Distinguish a conditional scenario from an estimated enterprise/economy forecast. These requirements concern stronger scientific claims, not a demand that a working paper forecast individual firms precisely.

## Primary sources and access record

The identifiers below are human-readable reference keys used in PartB; URLs are source locators, not copied article texts. Access/review date4November2026 America/Los_Angeles (some retrieval services date the same activity5NovemberUTC).

- [EPOCH] Michael and Cottier2026, “Servers account for60% of the total cost of ownership of a one-gigawatt AI data center,” Data/Analysis and tables. https://epoch.ai/data-insights/ai-datacenter-cost-breakdown
- [PCAOB] AS2201, current .62–.65 and .A7. https://pcaobus.org/oversight/standards/auditing-standards/details/AS2201
- [174A] 26USC174A(c), statutory text. https://www.law.cornell.edu/uscode/text/26/174A
- [IRS] Internal Revenue Bulletin2026-06, Notice2026-11, §3.01; qualified-property bonus depreciation and elections. https://www.irs.gov/irb/2026-06_IRB
- [FED] SR26-2 attachment, p3 footnote3. https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf
- [EU] Commission consolidated Article113(c)(i)–(ii), version27July2026, and Council final adoption29June2026. https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-113 ; https://www.consilium.europa.eu/en/press/press-releases/2026/06/29/artificial-intelligence-council-gives-final-green-light-to-simplify-and-streamline-rules/
- [METR] Kwa etal2025, Measuring AI Ability to Complete Long Software Tasks, Figure14/AppendixE. https://papers.nips.cc/paper_files/paper/2025/file/85069585133c4c168c865e65d72e9775-Paper-Conference.pdf
- [BCG] Flipping the Odds of Digital Transformation Success2020, Exhibit1 and surrounding text. https://www.bcg.com/publications/2020/increasing-odds-of-success-in-digital-transformation
- [WEF] Future of Jobs Report2025, Skills Outlook. https://www.weforum.org/publications/the-future-of-jobs-report-2025/3-skills-outlook
- [SEC] Bending Spoons final prospectus, consolidated cash flowsF35 and equity-compensation noteF59; organic-growth definition. https://www.sec.gov/Archives/edgar/data/2004711/000110465926079884/tm2613674-14_424b4.htm
- Wood2025 publisher record/source subreview, with root repeat-access failure disclosed: https://academic.oup.com/cje/article/49/5/1073/8315769

No full third-party articles or webpages are bundled. The Nature/PMC clinical full-text routes and exact EUR-Lex OJ route were inaccessible to the source subreview; indexed primary descriptions/abstract and official EU consolidation/adoption were available respectively. The root repeat Wood fetch failed on an inaccessible publisher redirect. These limits are not described as successful full-text re-audits. The legal/citation audit was targeted, not exhaustive.
