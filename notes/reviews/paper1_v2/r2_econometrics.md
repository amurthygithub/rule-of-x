# Referee report, round 2: econometrics

**Paper.** "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation", version 2 (`paper1_v2.pdf`, `supplement_v2.pdf`, `source_v2.tar.gz`, `response_to_reviewers.md`, all in `notes/reviews/paper1_v2/`). Sole author Akshaya Bangalore Sreenivasa Murthy; drafted by AI research agents under her direction.

**Scope.** The empirical parts: Sections 4 and 5, Section 5.8 and the anchor of Section 7.3, Tables 2 and 5, Tables S2 to S6, Appendix B.4 (choices made after results were seen), Supplement S6 and S7; the code `build_panel_v3.py`, `estimate_v3.py`, `estimate_v3_report.py`, `paper1_macros.py`; the outputs `empirics_v3.json`, `frontier_slope_v3.json`, `calibration_anchor_v3.json`, `inference_v3.md`, `sample_audit.md`, `claim_checks.txt`.

**Referee's checks.** All checks ran on copies in `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_econ/` (the repository copied to `repo/`, scripts in `checks/`, bootstrap draws in `checks/draws/`). No repository file was edited, and no script was run into a live path. The round-1 reports I was asked to read are `referee3_econometrics.md`, `fable_referee_econometrics.md` and `panel_investment_management.md`; I did not read the other round-2 reports.

---

## 1. Summary and recommendation

The revision does what the round-1 econometric reports asked, and it does it in a way that can be checked. The sample is rebuilt under five stated rules (R1, R3 and R4 applied in full; R2 and R5 partial and labeled as such). The model-facing object is now the theory's own dominance-cone frontier Psi_chi (D-2), the local conditional quantile is demoted to a descriptive statistic, and every quantile regression is solved as an exact linear program. The bootstrap is seeded by block, uses 999 replications throughout, re-estimates splits inside draws, counts undefined draws, and reports percentile, basic, normal and bias-corrected intervals with two-sided p-values of each type. Familywise error is controlled with Holm and a Romano-Wolf step-down in two stated families. The growth weight of 7 to 13 is withdrawn (D-1), E1 is the baseline and model-facing claims are confronted with E2 and two imputation bounds (D-3), and the claims that did not survive (the E1-E2 differences, the organic T(40%), the capital-intensity "finding", the "disappearing" size gradient, "never with a full point", the transient share of the anchor) are withdrawn in the text, not merely qualified.

Everything I recomputed reproduces. From the shipped panel and the shipped code I reproduce all 5,821 point estimates of `empirics_v3.json` to machine precision, and, re-running the seeded firm-cluster bootstrap for the blocks that matter for the text (cone, top, T, gap, anchor, reweight, bridge, spend, slopes, regimes, joint, capint, scale, yearly), every standard error, interval of every type, p-value, bias and undefined-draw share. The Holm-adjusted p-values reproduce from the unadjusted ones and the Romano-Wolf p-values from the re-run joint draws. Every number quoted in Sections 4, 5 and 7.3 that I traced is the macro value of the corresponding JSON entry, and the `CLAIMS` block of `paper1_macros.py` (51 qualitative statements, all passing) is a genuine safeguard. The response document's statements about the econometric findings are accurate; where it says "partly" or "not done", the paper agrees.

What remains is a set of consistency and disclosure problems, none of which changes a number but several of which change how a stated claim should read. The paper sets itself two disciplines, D-3 (a model-facing claim stands only if sign and 90% interval hold in all four views) and the familywise correction, and in three places the headline text does not follow them: the GAAP steepening (interval includes zero under E2), the "no detectable change in the best margins at a given growth rate" (T(0) after SBC excludes zero under E1 and in one bound), and the P95 decline's "survives at a familywise level of 10%" (not under the basic p-value, and the cash-basis decline survives under none). The bootstrap evaluates Psi_chi with a grid-cell minimum of 10 firm-years inside draws against 30 in the sample, so E2's primary slope has 13 to 17% of draws that the sample rule would call undefined; the numbers barely move, but the disclosure should say so and the D-3 flag for that cell should reflect it. The anchor conclusion carried into the abstract is outside both familywise families. Two disclosures in the protocol appendix are incomplete, and one round-1 item (R3-18) is still open.

**Recommendation: minor revision.** The empirical results can stand as reported once the text is brought into line with the paper's own rules in the places listed below. No re-estimation is needed; two numbers (the share of E2 draws below the grid rule, and the anchor conclusion's familywise standing) should be added.

**Counts.** Round 1: of the 19 findings of referee 3, 17 are resolved (four with a residual noted below), 1 partly, 1 not done; of the 11 cross-model findings, 7 resolved, 4 partly; of the 10 panel tests in my field, 7 resolved, 2 partly, 1 not done. New findings: 0 major, 5 moderate, 9 minor.

---

## 2. Round-1 status

Verdicts are mine, from the paper and the code, not from the response. "Resolved" means the finding is addressed in full and the evidence is in the paper or its outputs; "partly" names what is missing.

### Referee 3 (econometrics, `referee3_econometrics.md`)

| # | Round-1 finding | Response says | Verdict | Evidence |
|---|---|---|---|---|
| 1 | E2 is an exclusion sample; E1-E2 contrasts measure selection; add bounds or imputation | Fixed | Resolved | `estimate_v3.py` lines 115-129 build E2imp4 and E2imp8 exactly as `c7_impute.py` did (price = payments, else goodwill increase/0.75; half in the deal year, half next); 408 firm-years re-admitted, 5 without a price. Section 4.5 states the 87.6% dropped and the reasons; Section 5.9 withdraws the causal wording; Table 2 shows four views. Residual: R3-18 (below) |
| 2 | Interval type and bootstrap bias | Fixed | Resolved | `summarize()` returns percentile, basic, normal and BC intervals and p-values of each type; Table S4 reports them; bias reported in `inference_v3.md` section 4. Reproduced exactly (`c4_compare.py`) |
| 3 | Multiple comparisons | Fixed | Resolved, with a new caveat | Holm (primary) and Romano-Wolf on a joint draw in two families (38 contrasts; 14 headline). Reproduced (`c7_families.py`). See new findings 2 and 5 on how the results are stated |
| 4 | Weight of 7-13 counts maintenance S&M | Fixed | Resolved | Netted ratio 0.99 (0.14); weight withdrawn (D-1); Section 5.4 gives every method's value, 0.05 to 10.1 |
| 5 | Capital-intensity gap mechanical; interaction not tested; missing capex coded low | Fixed | Resolved | Add-back, prior-year and firm-median sorts, all periods (`inference_v3.md` section 8); interaction -0.14 (0.19), negative in 2 of 4 views; `split()` classifies only finite intensity. Section 5.6 reports it as an accounting effect. Residual: new finding 11 |
| 6 | T(40%) bootstrap invalid; draws dropped silently | Fixed | Resolved | No interval (5.8% of E1 draws, 58.9% of E2 draws undefined); cells 16 and 9; withdrawn in 5.2; NaN shares in section 7 of the notes |
| 7 | E2 GAAP slope was an IRLS approximation | Fixed | Resolved | `qr_fit` is the dual LP; `solver_check` compares dual, primal and IRLS at every point estimate and the minimizer range; the local E2 slope on v3 is -0.607 by all three |
| 8 | tau and window unjustified | Fixed | Resolved | Table S3: chi 0.80-0.95, windows 0-40 and 0-60%; wider windows undefined because 25 firm-years grow at least 80%. The local slope by growth band is in the JSON (`local_band_quantiles`) but not in the paper; acceptable |
| 9 | Estimated object differs from Psi_chi; order-m unused; "reversal" came from the estimator | Fixed | Resolved | Psi_chi primary (D-2), order-m reported (-0.22, -0.15), protocol S7.2 records that the reversal came from the estimator switch. Residual: new finding 8 on what was known when D-2 was taken |
| 10 | Size gradient without period effects; "disappears" | Fixed | Resolved | -4.1 (3.4), -1.8 with period effects; interval includes zero in every view; "weak and not robust" |
| 11 | Post hoc estimand switch disclosed incompletely | Partly | Partly | Appendix B.4 items 1 and 2 give the timing, what was known and the two post-test-run rules, and Table S2 reports E2 under the test-run rule; item reclassified as a researcher degree of freedom. The one sentence in the data section was not added. With E1 now the baseline this matters less |
| 12 | Anchor without sampling uncertainty | Fixed | Resolved | Firm-cluster intervals with cut-off and G re-estimated in every draw; only Pi_lb > 0 is stated as a conclusion; transient share "not determined". Residual: new finding 5 |
| 13 | Stochastic frontier: cohort frontiers, no inference, survivorship | Fixed | Resolved | Common frontier per period, JLMS, bootstrap intervals, balanced panel (-2.4 [-7.5, +3.5]), survivor caveat with the 72 of 129 count |
| 14 | Period slope differences untested; "never with a full point" | Fixed | Resolved, with a residual | Difference -0.38 [-0.60, -0.16], Holm 0.037-0.060, RW 0.064; phrase dropped. Residual: new finding 4 (summary states the steepening without the E2 qualifier) |
| 15 | Within-firm timing; E2 version | Fixed | Resolved, with a residual | Lead specification reported under E1 and E2. Residual: new finding 9 (imputation views computed but not reported) |
| 16 | Bootstrap design and reporting | Fixed | Resolved, with a residual | B = 999 everywhere, seeds by block in Table 2's note and S6, one source per table, splits re-estimated in draws, NaN shares reported. Residual: new finding 3 (in-draw grid rule) |
| 17 | Replication package | Fixed | Resolved | `REPLICATION_README.md` lists `estimate_organic.py`, `build_panel_v3.py`, `estimate_v3.py` in order; `regenerate_all.sh` runs them |
| 18 | E2 pairs organic growth with consolidated margins | Not done | Not done | Stated for Bending Spoons only; Section 4.5 is silent. One sentence (new finding 12) |
| 19 | Documentation mismatches | Fixed | Resolved | Tables regenerated from the JSON; S6 now describes the growth filter correctly for each regression |

### Cross-model econometrics referee (`fable_referee_econometrics.md`)

| # | Round-1 finding | Response says | Verdict | Evidence |
|---|---|---|---|---|
| 1 | 7-13 is a construction artifact | Fixed | Resolved | Terciles 10.1 / 3.0 / 1.5, floors, levels regressions, fixed G; withdrawn |
| 2 | E1-E2 contrasts not robust; interval type; family | Fixed | Resolved | Table S4; 3 of 38 percentile intervals exclude zero (3.8 expected); none survives Holm at 5%; statements withdrawn |
| 3 | T(40%) invalid bootstrap | Fixed | Resolved | As R3-6 |
| 4 | Capital-intensity gap mechanical | Fixed | Resolved | As R3-5 |
| 5 | Anchor noise-dominated | Fixed | Resolved | Intervals; abstract and intro quote no transient share; "exceeded their durable level if little of S&M buys growth" is the only anchor conclusion |
| 6 | E2 switch and pro forma rules disclosed only in the appendix | Partly | Partly | As R3-11 |
| 7 | Yearly series; 2025 rebound; reweighting | Fixed | Resolved | Table S5; 2016-19 to 2025 -4.5 [-17.7, +8.7]; DFL decomposition both directions, both bases |
| 8 | Interval type, B, non-convergence | Fixed | Resolved | Exact LP, no iteration cap; B = 999; types stated |
| 9 | Window and quantile dependence | Partly | Partly | Grid reported; the "concentrated between 10 and 30% growth" sentence not added. Acceptable |
| 10 | Log-log elasticity regression | Partly | Partly | Levels regressions reported; log-log estimates (0.39 pooled, 1.09 within) not. Acceptable since the text no longer relies on them |
| 11 | Smaller points (row-shift flag, 64 later-filing pro forma gaps, SFA intervals) | Partly | Partly | Flag now shifted by fiscal year (`build_panel_v3.py` line 142); SFA intervals added; the later-filing source of 64 pro forma gaps still not footnoted |

### Investment-management panel, tests in my field (`panel_investment_management.md`)

| Test | Round-1 finding | Verdict | Evidence |
|---|---|---|---|
| T1 | Backfilled pre-IPO and fiscal-2010 years | Resolved | Rule R1 removes 140 firm-years (98 + 40 + 2); `sample_audit.md` reconciles the panel's 141, the referee's 139 and the first-core-year 138 to R1 |
| T2 | Decline restated without backfill | Resolved | 11.9 and 12.7 points; survives every variant (7.8 to 12.8) |
| T3 | Yearly series; two slope regimes | Resolved | Table S5; regimes and rolling slopes in `inference_v3.md` section 10 |
| T4 | Capital intensity on prior-year sort | Resolved | Prior-year sort reported in the notes (-9.7 E1, -4.8 E2 on the cash basis) and the firm-median sort in the text |
| T5 | Anchor: 12 firms, Exzeo, Xunlei | Resolved | Exzeo 2025 excluded (R3); Xunlei 2025 flagged by R4(b) and excluded from the E1 anchor; intervals reported; 13 firm-years of 7 firms stated |
| T6 | Spend ratio moves against multiples | Partly | Weight withdrawn; the by-period ratio is not reported. Not needed once the weight is withdrawn |
| T7 | Holdout and returns test | Not done | Acknowledged in the response |
| T8 | Interval type on contrasts | Resolved | As FE-2 |
| T9 | Multiple testing across findings | Resolved | Family B gives the P95 decline Holm 0.054-0.208, close to the panel's 0.12-0.21 |
| T10 | E2 changes membership, not aggregates | Partly | Not discussed; E2 is now a check on E1 rather than the primary sample, which removes the practical concern |

### The author's decisions D-1 to D-3

- **D-1** is applied consistently: 7 to 13 appears only as a withdrawn statement (abstract, Section 1, 5.4, 8.1, B.4). Two passages re-use the spend ratio as alpha(X - k) under a stated condition (Section 8.1's 20-point illustration; the proxy calibration of Section 7.5, which is labeled "one calibration, not an estimate"). See new finding 10.
- **D-2** is applied consistently: Psi_0.90 is the primary statistic in Table 2, Sections 3.7, 5.3, 7.3 and the calibration input `frontier_slope_v3.json`; the local quantile is labeled descriptive wherever it appears. The protocol's account of what was known at the decision is incomplete (new finding 8).
- **D-3** is applied in Table 2 and Section 5.3, 5.5, 5.6, 5.8; it is not followed in three headline sentences (new findings 1 and 4) and one cell of Table 2 rests on the relaxed in-draw rule (new finding 3).

---

## 3. New findings

Severity: moderate = a stated claim should change or a result's standing is misdescribed (findings 1 to 5); minor = wording, disclosure or a number to add (findings 6 to 14).

**1. "No detectable change in the best margins at a given growth rate" fails the paper's D-3 rule for T(0) after SBC.** Moderate.
- *Location.* Section 5.10(v); Section 1 ("the best margins attainable at a given growth rate showed no detectable change"); Section 9 ("with no detectable change in the margins attainable at a given growth rate"). Section 5.2 itself is correct.
- *Issue.* The "no change" claim is a model-facing claim (Table 2 flags it as such), and D-3 requires the interval to include zero in all four views. For T(0) after SBC the change is -3.3 [-6.4, -0.2] under E1 and -3.3 [-6.4, -0.4] under M = 4; Table 2's own last column reads "no (2/4)". Section 5.2 says so ("a small fall whose interval excludes zero under E1 but not in every view"); the summary, introduction and conclusion drop the qualifier.
- *Evidence.* `c8_d3.py` applies the rule to every summary sentence: T(0) and T(20%) GAAP and T(20%) cash pass in all four views; T(0) cash passes in two.
- *Required change.* Qualify the three sentences: "no detectable change on the GAAP basis, and at 20% growth after SBC; the 95th-percentile margin among all firm-years fell by about 3 points after SBC in two of four views."

**2. The familywise standing of the P95 decline is overstated, and the cash-basis decline's standing is not reported.** Moderate.
- *Location.* Section 5.2: "the Holm-adjusted p-value of the GAAP decline is 0.054 to 0.208 across interval types (Romano-Wolf 0.097), so it survives at a familywise level of 10% but not 5%"; abstract, Section 1 (Fifth), 5.10(v), 9, which state both declines without a familywise qualifier while the slope's sign carries one.
- *Issue.* The sentence contradicts its own range: with basic p-values the adjusted value is 0.208, so the decline survives at 10% under the normal and percentile p-values and Romano-Wolf, not under the basic one. The `CLAIMS` test behind the sentence ("survives Holm at 10% (normal, percentile, Romano-Wolf), not at 5%") deliberately excludes the basic type, so the check passes while the sentence does not. The cash-basis decline (Holm 0.155, 0.154, 0.336; Romano-Wolf 0.154) survives at neither level, and this appears nowhere in the text; the abstract and summary give 11.9 and 12.7 symmetrically.
- *Evidence.* `families.headline14B` in `empirics_v3.json`; reproduced in `c7_families.py`. A single-step max-t on the same joint draw gives 0.136 for the GAAP decline.
- *Required change.* Rewrite the sentence to name the types under which it survives; add the cash result; make the `CLAIMS` test cover all three types or state the exception in the text. In the abstract, introduction and summary, treat the two declines as the paper treats the slope's sign: the declines hold in every view and every variant, and the GAAP one survives a familywise correction at 10% under three of four procedures. Alternatively, designate the GAAP P95 decline as the single pre-specified descriptive test, which the paper could defend (it was the first question asked), and say so in B.4.

**3. The bootstrap evaluates Psi_chi under a weaker grid rule than the estimator it reports, and E2's primary slope would be "not estimable" under the paper's own rule.** Moderate (disclosure; numerically immaterial).
- *Location.* Section 5.1 ("Each grid point needs at least 30 firm-years"; "A statistic with more than 5% of undefined draws gets no interval"); Table 2, notes and last column (Psi_0.90 GAAP: "yes/yes"); S6 ("Inside a draw a grid point of Psi_chi needs fewer firm-years than in the sample"); `estimate_v3.py` `cone_min()`.
- *Issue.* `cone_min` returns 30 for the sample and 10 inside a draw. For E2's 0-60% window (37 firm-years at g >= 0.6 on the GAAP basis, 38 after SBC) 16.8% (GAAP) and 13.0% (cash) of the cone-block draws have fewer than 30 firm-years in the 60% cell, so under the sample rule E2's primary slope would have more than 5% undefined draws and no interval, and the D-3 flag "interval excludes zero in all four views" for the GAAP slope would read "n.e." for E2. The relaxed in-draw rule also explains why period slopes on the 0-60% window have 99% defined draws under E2 while the sample estimate is undefined (`frontier_slope_v3.json`, `periods.op.w60_2010_19.E2`). The text of 5.1 states only the sample rule; the in-draw rule appears in a table note and in S6 without the number of draws it affects.
- *Evidence.* `c5_cells.py` (in-draw cell counts on the cone-block draw matrix); `c6_cone30.py` (same draws with the 30 rule inside draws: E2 GAAP 16.8% undefined, defined-draw 90% interval [-0.505, -0.080] against the published [-0.508, -0.068]; E2 cash 13.0%, [-0.413, -0.046] against [-0.413, -0.041]; E1 and both bounds unaffected, at most 0.4% of draws).
- *Required change.* State the in-draw rule and the affected shares in Section 5.1 or the Table 2 note ("under E2, 17% and 13% of draws evaluate the 60% cell on 20 to 29 firm-years"), and either keep the E2 interval with that disclosure or mark the E2 cell n.e. and say the interval claim holds in E1 and both bounds with E2 agreeing on the defined draws. The same disclosure applies to T(g0), where the in-draw rule is 10 against a 30-firm-year cell rule.

**4. The summary states the GAAP steepening as a fact although it fails D-3 under E2.** Moderate.
- *Location.* Section 5.10(i): "The GAAP slope steepened after 2020; the cash-basis slope did not"; Section 5.3 last sentence of the paragraph.
- *Issue.* The difference is negative in all four views but its 90% interval includes zero under E2 (-0.66 to +0.02; Table 2 "yes/no (3/4)"). Section 5.3 gives the detail and the familywise result (10% under every procedure, 5% under two); the summary, which says every fact "holds under observed scores, the organic sample and both imputation bounds unless stated otherwise", does not state otherwise.
- *Evidence.* `c8_d3.py`.
- *Required change.* "The GAAP slope steepened after 2020 in sign in every view and in three of four intervals; the cash-basis slope did not."

**5. The anchor conclusion carried into the abstract is outside both familywise families.** Moderate.
- *Location.* Abstract ("they exceeded their durable level if little of their selling and marketing expense buys growth"); Section 1; 5.8; 7.3; Table 2 anchor rows.
- *Issue.* Family B contains the slopes, size, capital intensity, the P95 changes, T(40%), the gap and two contrasts, but not the median Pi_lb, which is the one anchor statement the paper retains as a conclusion. Its unadjusted p-values are 0.0006 (normal), 0.012 (percentile) and 0.002 (basic); added to family B as a fifteenth member its Holm-adjusted values are 0.006, 0.096 and 0.030. It therefore survives at 5% under two types and at 10% under the third, which is stronger than the P95 decline but weaker than the gap results, and the reader cannot see this.
- *Evidence.* `c9_anchor_family.py`.
- *Required change.* Add the anchor Pi_lb to family B (or state in 5.8 that it is stated on its own four intervals and give the adjusted values above), and apply the same qualifier in the abstract as for the other headline results.

**6. The familywise sentence on the steepening is right; the one on the P95 decline is not, because the `CLAIMS` test and the text use different procedure sets.** Minor (covered by finding 2; recorded here as a process point).
- *Location.* `paper1_macros.py`, CLAIMS entries "the P95 decline survives Holm at 10% (normal, percentile, Romano-Wolf), not at 5%" and "GAAP steepening survives Holm at 10% under every procedure".
- *Required change.* Align the test with the sentence it guards, in both directions.

**7. Section 5.9 and Table S4: "3.8 expected by chance" assumes 38 estimable contrasts; two have no interval.** Minor.
- *Issue.* `ContrExpected = 0.10 x 38`; 36 contrasts are estimable, so 3.6. The conclusion (3 observed) is unchanged.
- *Required change.* Use `n_estimable`.

**8. Appendix B.4, item 4 (D-2): what was known when the frontier object was chosen is stated incompletely.** Minor (disclosure).
- *Location.* B.4 item 4: "The choice was made before any estimate of Psi_chi on the audited sample had been computed."
- *Issue.* True of panel v3, but the Psi_chi slopes on the first version's sample were known when D-2 was taken at 13:53: referee 3's `c16_dominance.py` (13:33) reported -0.20 (GAAP) and -0.16 (cash) under E1 and -0.31 and -0.19 under E2, and the first draft's envelope block had cash-basis order-alpha slopes of -0.06 to -0.25. Those values are within 0.02 of the v3 estimates (-0.22, -0.16). The decision was also the referee's recommendation and it weakened the paper's slope claim, so it was not self-serving, but the sentence as written suggests the chooser was blind to the object's value.
- *Required change.* Add: "The slopes of Psi_chi on the first version's sample, -0.20 and -0.16 under E1, were known from the round-1 econometrics report and the first draft; the local-quantile slopes on the audited sample had been printed by a test run."

**9. Within-firm lead regressions are reported under two views although four exist.** Minor.
- *Location.* Section 5.3, last paragraph; `empirics_v3.json` `within`.
- *Issue.* The lead coefficients are model-facing (Proposition 3(v)) and D-3 asks for four views. The JSON holds the imputation bounds: -0.07 (0.05) and -0.05 (0.05) on the GAAP basis, -0.08 (0.04) and -0.08 (0.04) after SBC. The E2 value (-0.15 (0.07), t = 2.2) is the only one that is not small, and the reader does not learn that the bounds sit between E1 and E2.
- *Required change.* Report the four views, or state that under the imputation bounds the lead coefficients are -0.05 to -0.08.

**10. Section 8.1 re-uses the spend ratio as alpha(X - k) after Section 5.4 withdrew that reading.** Minor.
- *Location.* Section 8.1: "If its spend ratio equals the median of 3.02 and it is optimal, an asset-light firm growing 10 points faster than its market scores about 20 points below ..."
- *Issue.* The 20 points follow from Delta(1 - alpha(X - k)) with alpha(X - k) = 3.02, which counts all selling and marketing as growth spend, the proxy the paper says overstates alpha(X - k) by up to a factor of 60 across methods. The sentence is conditional, but the condition is not the one that matters.
- *Required change.* "If all of its selling and marketing expense buys growth and the median ratio of 3.02 is its alpha(X - k), ... about 20 points; netting maintenance spend (ratio 0.99) the shortfall is about zero."

**11. Section 5.6: "The 2016-19 gap behaves the same way" overstates.** Minor.
- *Issue.* In 2016-19 the add-back removes a third of the gap (-15.6 to -10.8, interval [-32.4, +1.0]), against two-thirds in 2023-25 (-12.5 to -4.6); the prior-year sort gives -8.4 [-19.6, +8.7]. The conclusion (an accounting effect) still holds because no sort or basis gives an interval that excludes zero in all four views, but "the same way" is not the right description.
- *Required change.* "In 2016-19 the gap was -15.6 points and -10.8 with the deduction added back (interval -32.4 to +1.0)."

**12. R3-18 remains open: E2 pairs organic growth with consolidated margins.** Minor.
- *Location.* Section 4.5.
- *Required change.* One sentence: for the 58 adjusted firm-years the margin includes the acquired business, deal costs and, on the GAAP basis, amortization of acquired intangibles, which biases the organic GAAP margin down and the cash margin in either direction.

**13. The Romano-Wolf procedure scales every draw by the full-sample bootstrap standard error.** Minor (labeling).
- *Location.* Section 5.1 ("the studentized step-down procedure of Romano and Wolf (2005)"); `romano_wolf()` in `estimate_v3.py`.
- *Issue.* The bootstrap statistics are |b - est| / se with one se per contrast, not draw-specific standard errors, so the procedure is the max-t step-down with fixed scaling (Romano and Wolf's basic version with scaled statistics), not the studentized one. It is valid as a check and it reproduces; the label should match.
- *Required change.* Call it "the step-down max-t procedure of Romano and Wolf (2005), with statistics scaled by their bootstrap standard errors", or studentize within draws.

**14. The reweighting decomposition uses a different quantile definition from the main table.** Minor.
- *Issue.* The DFL block uses Hazen weighted quantiles (P95 56.1 and 44.1, change -12.0) while Table 2 uses the linear sample quantile (55.9, 43.9, -11.9). The parts are reported to the reader next to a total that differs by 0.1 point.
- *Required change.* State the definition in the Table S5 note or use one definition.

---

## 4. Other checks: inference, sample rules, disclosure

**Inference (task 3).** Interval types are stated (percentile in the text; the others in Table S4 and the JSON). B = 999 for every interval; the seeds and the seed rule are in Table 2's note and S6, and the seeds in the JSON match the rule (`SEED0 + crc32(name) mod 1e6`). Undefined draws are counted and reported (section 7 of `inference_v3.md`); the 5% rule is applied; T(40%) has no interval and no E2 estimate. Bootstrap standard errors in Table 2 come from the same draws as the intervals. The claims that state more than the familywise results allow are those in findings 2, 4 and 5; the slope's sign, the "far above -1" claim, the steepening in Section 5.3, the gap results and the capital-intensity gap are stated within what the results allow.

**Sample rules (task 4).** R1 is applied as defined (`build_panel_v3.py` lines 91-113: a firm-year is backfilled when its source filing's own revenue period ends after the fiscal year) and reconciled with the panel's and referee's counts. R3 is applied with the XBRL elements and the one verified filing text. R4 is applied with criteria (a) to (c), with the choice among five variants of (b) disclosed as made after the flagged lists were seen. R2 is a classifier on the 16 named firms only; the paper calls it "a partial check", names the five firms it misses, and runs both the classifier-based and the all-named sensitivities, whose extreme (E2 without the 16 named firms: Psi -0.42, P95 change -8.4) enters the reported ranges. R5 is a flag with a stated untested set (foreign filers). The frames-based inputs are described as latest-filed, not first reported, in Section 4.6, S6 and the bridge table's note, with the zero-fill rule for missing elements stated, and the bridge is presented on like-for-like firm-years. I find the presentation of R2, R5 and the frames inputs honest. Two small gaps: S6 does not say that the related-party and acquiree-revenue elements behind R3 and R4(c) are also latest-filed (the audit notes do), and R4(b)'s acceleration benchmark is the v2 core sample's yearly median rather than the v3 one (immaterial).

**Disclosure of choices made after results were seen (task 5).** Appendix B.4 lists seven items with times and what was known, reports E2 under the first test run's rule, records the test runs of the superseded pipeline before D-2, and withdraws the "three changed conclusions". It is complete and accurate except for finding 8 (the v2-sample Psi_chi values known at D-2) and one omission: the two familywise families were defined after the round-1 reports (family A for the sample audit before D-1 to D-3, family B after; `inference_v3.md` section 5), which the appendix does not say; adding the sentence would close the point. The data section states that the rules were chosen before any estimate on the resulting sample (4.2) and defers the estimand history to the appendix (R3-11, partly).

---

## 5. Checks run

All scripts are in `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_econ/checks/`; they execute the unchanged `estimate_v3.py` of the scratch copy up to its bootstrap section (`lib_v3.py`) and reuse its functions, seeds and draw matrices.

1. `lib_v3.py`: loads the frames and estimators of `estimate_v3.py` without running its bootstrap. Sample counts reproduce Table 2 panel C: E1 1,788 (292); E2 1,378 (277); exclusion-only 1,320 (274); M = 4 and M = 8 1,786 (291).
2. `c1_points.py`: every point estimate of every block and variant against `empirics_v3.json`: 5,821 of 5,821 reproduce to 1e-9, and the joint block agrees with its source blocks.
3. `c2_time.py`: per-draw timing of each block (to plan the re-runs).
4. `c3_boot.py`: re-runs the seeded firm-cluster bootstrap (same seeds, same `default_rng` draw matrix) for the blocks top, T, gap, anchor, reweight, bridge, cone, spend, regimes, slopes, joint, capint, scale and yearly, saving the draws.
5. `c4_compare.py`: every summary (se, bias, percentile/basic/normal/BC intervals at 90 and 95%, p-values, undefined shares) for every statistic, variant and paired contrast of those blocks against the JSON. Results: top, T, gap, anchor, reweight, bridge 666/666; cone 336/336; spend 228/228; regimes 18/18; slopes 48/48; capint 264/264; scale 96/96; yearly 206/206. Not re-run: sfa and grid (about 30 and 16 minutes each); their point estimates reproduce (check 2) and the SFA intervals quoted in Section 5.7 were read from the JSON only.
6. `c5_cells.py`: in-draw cell counts of the Psi_chi grid on the cone-block draws (finding 3).
7. `c6_cone30.py`: the primary slope with the 30-firm-year rule inside draws (finding 3).
8. `c7_families.py`: Holm-adjusted p-values recomputed from the unadjusted ones for all four families and three types; Romano-Wolf recomputed from the re-run joint draws for all four families; a single-step max-t for family B.
9. `c8_d3.py`: the D-3 rule applied to every statement of Section 5.10, the introduction and the conclusion (findings 1 and 4); the within-firm lead coefficients under the four views (finding 9).
10. `c9_anchor_family.py`: the anchor conclusion's Holm-adjusted p-values if added to family B (finding 5).
11. Read-through and text-to-JSON cross-check of every number in Sections 4.1 to 4.6, 5.1 to 5.10 and 7.3 (anchor), Tables 2, 5, S2 to S6, and the protocol items of B.4 (slopes, intervals, counts, Holm ranges, bridge lifts, yearly series, reweighting parts, anchor quartiles and intervals, firm counts); all match the macros and the JSON.
12. Code read-through: `estimate_v3.py` (frames, estimators, bootstrap, summaries, families, solver check, within-firm, anchor), `estimate_v3_report.py` (D-3 flags, tables), `paper1_macros.py` (v3 macros, CLAIMS, table patches), `build_panel_v3.py` (R1 to R5, bridge inputs), `estimate_organic.py` frame construction, `data/v3_inputs/README_retrieval.md`, `notes/sample_audit.md`, `notes/inference_v3.md`.

In all, 1,862 bootstrap summaries (every statistic, variant and paired contrast of the fourteen re-run blocks) reproduce the JSON to 1e-9 on every reported field, and no draw raised an error, so the seeds, the draw matrices and the estimators in the shipped code are the ones that produced the paper's tables.

## 6. What I found correct

- The point estimates, the bootstrap and the familywise results reproduce exactly from the shipped data and code; the seeds make the draws independent of the order of computation.
- The bootstrap design is right: firms are the clusters, every estimand is evaluated on its own rows of the same drawn firms, differences are paired, the capital-intensity split and the anchor cut-off are re-estimated inside draws, and undefined draws are counted rather than dropped.
- The exact LP solver removes the IRLS discrepancy of round 1; the solver check reports dual, primal and IRLS values and the minimizer range at every point estimate.
- The D-3 construction (E2 plus two imputation bounds, with sign and interval flags) is implemented as the round-1 referees proposed, and the paper's conclusions follow the flags in Sections 5.3 to 5.8.
- The withdrawn claims are withdrawn in the places where they were made (abstract, introduction, summary, protocol), not only in the robustness section.
- The sample rules are documented with the firm-years they affect, the counts reconcile across the three round-1 definitions, and the partial rules are presented as partial.
- The `CLAIMS` mechanism ties 51 qualitative sentences to the estimates and stops the build when one fails; it would catch a refreshed estimate that no longer supports a sentence. Its two gaps (findings 2 and 6) are in how two tests are written, not in the mechanism.
