# Independent empirical and inferential re-review

Prepared 4 November 2026 (client date). This note uses the supplied revised PDFs and the permitted RESPONSE.md. It has not read any other reviewers' folders, joint response, or restricted responses. At this stage repository/data access has not been supplied to this reviewer. Accordingly no empirical table, raw-data extraction, valuation regression, specification curve, or bootstrap has been independently reproduced. PDF page numbers below are both physical and printed numbers.

## Independent assessment (Part B contribution)

The revision substantially improves the distinction between descriptive evidence and identification. The four estimands, conditional macroeconomic inferential target, multiplicity dependence, specification sensitivity, forward pairing, and leave-one-firm-out analysis are explained rather than hidden. S11 expressly says specification shares are not probabilities and its intervals do not replace familywise corrections. It also discloses that the headline decline is among the largest, and its headline slope among the flattest, in the contemplated choices. These are meaningful repairs. They do not identify a firm's feasible frontier, decision weight, causal effect of automation, or a stable market valuation weight.

### E-1. Contradictory inferential statement in the interest-income bridge (minor; confirmed)

- Locator: supplement p31, S7, final paragraph “Additional tables”; main p41, §4.6.
- Evidence: S7 gives the change in the net-of-after-tax-interest-income 95th percentile as −14.2 with a displayed 90% interval [−35.9, −2.3], then says both intervals on the thin subsample include zero. The displayed interval excludes zero. Main §4.6 repeats that both intervals include zero. Original PDF page31 was rendered and visually checked: minus 2.3 is printed, not an extraction artifact.
- Significance: readers cannot know whether the stored interval or the verbal qualification is stale. This affects a robustness argument, not the main P95 finding.
- Fix: regenerate the bridge and macros; reconcile the two statements and report both paired-sample intervals. If the displayed interval is right, retain the thin-sample warning but remove the assertion that both intervals include zero.

### E-2. Valuation ratio “90% interval” is not the procedure its note says it is (minor method issue; code-dependent extent)

- Locator: supplement p65, S12.1 and Table S20 note; p66 reading.
- Evidence: the note defines the interval as the 5th–95th percentile of 999 bootstrap ratios, but replaces the upper endpoint with infinity when more than one in twenty bootstrap denominator coefficients are nonpositive. A percentile of finite ratios does not acquire an infinite endpoint solely because the denominator changes sign. The note therefore describes an ordinary percentile interval plus an additional weak-denominator diagnostic/rule, rather than one ordinary percentile interval. It does not describe a Fieller confidence-set inversion or another interval construction that justifies the resulting set.
- Scope: this establishes an incomplete/inconsistent method description. It does not establish that the finite all-year interval [3.1,15.8] is numerically wrong, since the draws and code are unavailable. The 2010–19 cash row and score≥40 GAAP row are explicitly affected by the infinity convention. Do not invent the underlying sign shares.
- Fix: publish denominator sign shares and its confidence interval; report the finite-ratio percentiles separately from the weak-denominator diagnostic, or use and document a confidence set for the ratio obtained by inversion (potentially unbounded/disconnected). Avoid describing the ad hoc infinity convention as a standard percentile interval.

### E-3. Headline sample description overstates the principal-software screen (minor scope/abstract wording)

- Locator: main p1 abstract; p38 §4.2 R2; p43 Table2 notes; supplement pp31–32 S7/TableS4.
- Evidence: the abstract calls the observations those of “284 software companies.” The paper's R2 paragraph says the fixed keyword classifier excludes 8 registrants, but both blind readers classify 49 registrants as not software; removing these beyond the keyword exclusions removes another 223 baseline firm-years (TableS4: 1,732→1,509). The authors acknowledge missed games/cloud and other business types. This is a screen applied to all descriptions, not successful exclusion of every principal-nonsoftware business.
- Significance: the analysis remains a legitimate SIC7372-based sample with transparent sensitivity analyses. It is not demonstrated to be a clean software-company population. R2 sensitivities change GAAP slope −0.20→−0.37 and P95 fall 11.9→8.8; S11 gives a median slope −0.51 with either-reader exclusions, so the scope matters for magnitudes.
- Fix: in abstract and Table2 notes say “284 SEC registrants classified in SIC7372, after the stated screens,” or “software-classified registrants”; keep the blinded-reader restriction as a prominently reported sensitivity. If the intended population is principal-software businesses, adjudicate the discrepant classifications by an outcome-blind substantive rule and rerun. Do not silently replace a prespecified screen after seeing results.

### E-4. Unique-firm support remains incomplete for consequential cone cells (minor; partly outstanding GPT-16)

- Locator: main p41 §5.1; supplement p63 S11 “Leave one firm out”; main p49 §5.8 and supplement TableS12.
- Evidence: the E2 60% growth cell contains 37 firm-years; its LOFO minimum is 34, while E1's is 60. Neither passage gives distinct firms in each consequential cone cell. The anchor now gives 14 firm-years/7 firms (and E2 19/10), concentration, and all-firm deletion ranges. LOFO robustness shows no single firm reverses the relevant signs. It does not itself establish enough independent tail clusters for the cluster bootstrap, nor replaces the requested distinct-firm counts.
- Fix: add firm-years, distinct firms, largest firm share and undefined-draw percentage for endpoint/period cells and tail/anchor cells. Judge whether joint deletion or a small-cluster sensitivity is warranted after seeing those counts. Do not infer an invalid interval solely from 37 firm-years.

### E-5. Residual no-change wording should describe evidence rather than non-steepening as a population conclusion (minor/editorial)

- Locator: main p46 §5.3 closing sentences; supplement p62 TableS19 cash steepening row and p63 discussion.
- Evidence: the Table2 note now correctly says no directional claim is made when the interval includes zero. TableS19 nevertheless titles its claim “Cash frontier did not steepen,” and defines interval success as an interval not lying below zero. Main p46 ends “the cash frontier did not steepen once acquired growth is removed.” The relevant point estimates are nonnegative in E2/bounds, but the multiverse also produces negative estimates and imprecise intervals. Failure of an interval to lie below zero is absence of detected steepening, not a non-steepening or equivalence test.
- Fix: “No common negative change is established across the acquisition-adjusted views”; for TableS19, “No statistically detected steepening under the stated unadjusted test.” Distinguish observed point-estimate ordering from inference about a population change.

### Interpretation and specialist-journal limits (not newly discovered numerical errors)

1. S12.1 provides a conditional association in a future public-float/revenue proxy, with year effects only. Non-affiliate float differs from total equity and enterprise value; ownership, debt/cash, size, expected persistence, and denominator sharing can affect the coefficient ratio. The paper does explicitly acknowledge most of this (pp65–66), so the regression is not a newly proved causal error. Its language “the market's valuations put” should remain tied to that descriptive ratio. Comparing its interval with the structural screening range cannot falsify or validate Lemma5 without an explicit mapping. Better sensitivity to ownership/firm characteristics and another value measure would be required if market-weight inference is a central journal contribution.
2. Empirical signs across observed chosen points do not identify a feasible frontier or a firm's own trade-off. The manuscript now says this clearly (main pp4,46), so no renewed criticism that it claims direct identification is justified.
3. Current SIC and latest business descriptions, nominal revenue threshold, XBRL source coverage, acquisition adjustment of only 57 affected years, and consolidated margins paired with organic growth remain stated limitations. Their disclosure is not their removal. The E1/E2/bounds are related views, not independent replications; the paper correctly says so.
4. Nine hundred ninety-nine bootstrap draws can be sufficient for a working-paper illustration but do not remove uncertainty at tail probability cutoffs. Current p_RW=.075 has binomial-style Monte Carlo SE approximately .0083. Its approximate ±1.96SE band is .0587–.0913, so the old p=.097 boundary claim should not be repeated as if still the current result. This arithmetic does not validate the Romano–Wolf implementation.
5. The specification curve is a very useful robustness audit, not an error-rate correction or proof the analyst-choice distribution is natural. Its design was recorded after earlier headline estimates existed; the manuscript does not claim a blind original-study preregistration and appropriately flags original family selection after results.

## Part A contribution: response audit

| ID | Author status | Verdict | Evidence and locator |
|---|---|---|---|
| GPT-M6 | Partly | partly resolved | Sample-flow accounting, no-equivalence note, Monte Carlo error, conditional bootstrap target and LOFO are now explicit (M pp40–46; S pp31,61–64). Distinct tail-cell firm counts still incomplete, and repository reproduction has not occurred in this review. |
| GPT-12 | Fixed | resolved (PDF accounting) | M p40 §4.5: 1,732−457+57−2=1,330; 457=270+187; omitted affected years400=203+162+26+9; unaffected1,273. The author's response quotes earlier counts but expressly says later rerun controls. Actual records still require code audit. |
| GPT-13 | Fixed | partly resolved | M p43 Table2 note correctly says no directional claim and no equivalence margin. However residual cash-nonsteepening wording in M p46 and S pp62–63 conflates no detected negative change with non-steepening; see E-5. |
| GPT-14 | Fixed | resolved (disclosure/arithmetic) | M p44 §5.2 reports p_RW=.075 and MCSE≈.008 at999. Author's old .097/.009 is superseded by documented sample rerun. Current three-of-four significance count is consistent with the listed procedures; the bootstrap itself is not rerun. |
| GPT-15 | Fixed | resolved | S p31 “Inference” explicitly conditions on realized macroeconomic history; resamples firms, not years. |
| GPT-16 | Fixed (3Nov) | partly resolved | S p63 supplies all-firm deletion results across four views and anchor. M p49 gives anchor unique firms/concentration. Consequential cone cells still show firm-years without distinct firms; see E-4. |
| GPT-24 | Fixed | resolved as a framing change, not an empirical validation | M p2 gives the uniform/log-uniform joint-scenario 40.7–66.7 band and labels distribution assumptions; S10 supplied values require root's stress-test review and reproduction. |
| GPT-31 | Already handled | resolved as disclosed limitation | M pp37–41 and S p31 disclose current SIC/latest descriptions, latest-filed bridge values and consolidated margins. These are residual scope restrictions, not repaired measurement identification. |
| GPT-34 | Partly | not resolved at this stage | This reviewer has received no source/data copy and has executed no committed pipeline. Need root's access/run record before final verdict. |

## Empirical release recommendation

For an arXiv working paper, the empirical portion is suitable as descriptive evidence after the internal interval contradiction and scope/method wording are repaired and the frozen replication package is actually made accessible. Publication should not describe unavailable reproduction as accomplished. For a specialist journal, major revision remains appropriate: an accessible verified pipeline and a sharply stated empirical estimand are essential; more identification or narrower theoretical-empirical claims are needed if the article wishes to estimate actual economic limits. A descriptive association paper can be judged on a narrower claim, but the specification curve cannot supply missing causal or structural identification.
