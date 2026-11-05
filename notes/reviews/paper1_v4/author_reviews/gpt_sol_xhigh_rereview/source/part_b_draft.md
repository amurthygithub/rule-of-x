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
