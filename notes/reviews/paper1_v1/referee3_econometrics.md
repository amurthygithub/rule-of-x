# Referee report 3: econometrics

**Paper.** "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation" (Paper 1, version 1; `paper1_v1.pdf`).

**Scope.** Empirical parts only: Section 4 (`sec:data`, incl. 4.4 `sec:data-estimands`), Section 5 (`sec:empirics`), Table 2 (`tab:estimands`), Tables 3 to 8, Tables 14 and 15 (`tab:robust`, `tab:edge`), Appendix D (`app:data`), the estimand passages of Appendix E (`app:protocol`), the empirical anchor of Section 7.3 (`sec:horizons-ranges`), and the empirical inputs to Section 3.7 (`prop:industry`).

**Referee's checks.** The scripts are in `notes/reviews/paper1_v1/referee3_checks/`. They rebuild E1, E2 and the threshold variants by executing lines 1 to 232 of `code/estimate_organic.py` unchanged. I did not edit any paper or code file, and I did not rerun the full 30-minute organic script.

---

## Summary

The paper builds an as-first-reported SEC XBRL panel of 293 prepackaged-software firms (1,929 firm-years, 2010 to 2025). It reports two estimands:

- **E1**, observed scores;
- **E2**, the "organic frontier". E2 keeps acquisition-affected firm-years with pro forma organic growth where the filings allow, and excludes them otherwise.

It reports six findings:

- (i) The 0.90-quantile slope of margin on growth over 0 to 60% is about −0.5. It is steeper in E2 (−0.59 GAAP, −0.43 cash) than in E1 (−0.46, −0.37).
- (ii) S&M spending implies a weight on growth of 7 to 13.
- (iii) A cash-basis size gradient in E1 "disappears" in E2.
- (iv) Since 2023, capital-intensive firms' P95 cash score is 11 points lower in E2.
- (v) The P95 score fell by 12 to 15 points between 2016–19 and 2023–25, while frontier points at fixed growth did not change detectably, "except at the thinly populated 40% threshold of the organic frontier".
- (vi) A near-frontier margin gap of about 33 points, decomposed by cost line.

The data work is careful. Statistics built from extreme order statistics have been replaced by quantile statistics, inference uses a firm-cluster bootstrap, and the estimand switch is recorded candidly in `notes/estimand_notes.md`.

Three findings hold up: the decline in the top of the score distribution, the measurement-basis comparison and the descriptive margin-gap decomposition. The model-facing claims do not yet hold up, for five reasons:

1. E2 is in substance an exclusion sample: 59 of 469 affected firm-years are adjusted, 12.6%. The E1−E2 contrasts that the paper attributes to "acquired growth" are driven by which firm-years are dropped. When the excluded firm-years are re-admitted with imputed organic growth, the contrasts largely return to E1.
2. The "significant" E1−E2 differences rest on percentile intervals from bootstrap distributions with substantial bias. Basic and bias-corrected intervals, and the paper's own standard errors, do not exclude zero.
3. There is no correction for roughly 30 paired comparisons, nor for the period and threshold splits.
4. The weight of 7 to 13 treats all S&M as growth spend. Under the model's own logic, the S&M of firms growing at the median is maintenance. Netting it out gives weights of about 2.5 to 4.5.
5. Most of the capital-intensity gap is the accounting identity: the sorting variable is deducted from the outcome.

There are also two technical problems with the headline slope. First, the E2 GAAP slope of −0.59 is an IRLS approximation; the exact quantile-regression solution is −0.564, essentially the exclusion-only value (−0.560). Second, the slope depends on the growth window chosen.

## Recommendation

**Major revision.**

The descriptive E1 results can stand with minor changes. Before the model-facing E2 findings can be stated as in the abstract and introduction, the paper needs four things:

- a re-designed treatment of acquirers: bounds or imputation for the excluded firm-years, not exclusion alone;
- bias-robust and multiplicity-adjusted inference;
- a maintenance-adjusted spend ratio;
- a pre-capex decomposition of the capital-intensity gap.

The post hoc change of primary estimand is handled honestly in the notes and the appendix. It is not yet disclosed where readers need it, in Section 4.4. Two rules that were added after a test run are missing from the paper.

**Count of findings by severity.** 5 major, 9 moderate, 5 minor.

---

## Findings

### Major

**1. E2 is mostly an exclusion sample. E1−E2 differences measure selection, not acquired growth.**

- *Severity.* Major.
- *Location.*
  - Section 4.4 (`sec:data-estimands`);
  - Section 5.3: "Acquired growth flattens the GAAP slope";
  - Section 5.5: "the cash-basis gradient in observed scores reflects acquired growth rather than saturation";
  - Section 5.10(i) and (iii); introduction, "Third"; Table 2; Appendix E.2.

*Issue.* E2 is described as "growth net of acquired growth". In fact:

- of the 469 flagged firm-years, 59 are adjusted (12.6%), and 410 are dropped;
- only 6.4% of acquisition years are adjusted, and only 5 of the 46 flagged firm-years with g > 50%;
- E2 differs from the exclusion-only sample (25% column) by those 59 firm-years, and its statistics are nearly identical to it (Table 2).

The excluded firm-years are strongly selected. These diagnostics appear only in `estimand_notes.md` §5, not in the paper:

- flagged firm-years have median cash scores 10.1 points higher [7.2, 13.1];
- they make up 40% of firm-years at or above the period P95 of the cash score, against 24% of all firm-years;
- ever-acquirers' unflagged years have GAAP margins 11.5 points higher and growth 4.5 points lower than never-acquirers.

The E1−E2 contrast therefore combines two things: removing acquired growth from 59 points, and deleting 410 points together with their organic content. The paper attributes the whole contrast to the first.

*Evidence.* `c7_impute.py` and `c7b_impute_more.py` re-admit the 410 excluded firm-years.

- *Method.* Organic growth is imputed by removing acquired revenue equal to the purchase price over a price-to-revenue multiple M. Half is removed in the deal year and half in the next year, matching the carry-over that the paper's g_org removes. The purchase price is acquisition payments, or the goodwill increase divided by 0.75 where payments are missing.
- *Calibration.* M = 4 implies a median acquired contribution of 5.8 points. This is close to the 5.3 points measured from the pro forma subsample (`estimand_notes.md` §4).
- *Results.* Point estimates; slopes by exact LP.

| Statistic | E1 | E2 (paper) | Exclusion only, 25% | Imputed, M = 2 | M = 4 | M = 8 |
|---|---|---|---|---|---|---|
| Upper-decile slope, GAAP | −0.46 | −0.56 | −0.56 | −0.52 | −0.48 | −0.45 |
| Upper-decile slope, cash | −0.37 | −0.43 | −0.43 | −0.39 | −0.42 | −0.39 |
| Size gradient, cash (pts per tenfold) | −5.7 | −2.7 | −3.0 | −4.4 | −4.8 | −5.3 |
| Change in P95 of R, GAAP | −11.7 | −11.6 | −11.4 | −7.5 | −8.0 | −10.0 |
| Change in P95 of R, cash | −15.2 | −12.4 | −12.4 | −8.3 | −9.4 | −11.7 |
| Capital-intensity gap, cash, 2023–25 | −14.9 | −10.6 | −10.9 | −8.8 | −9.7 | −12.6 |
| Spend ratio | 2.91 | 3.26 | 3.31 | 3.29 | 3.20 | 3.09 |

At plausible software deal multiples (M = 4 to 8), keeping the acquirers' firm-years with acquired growth removed gives a GAAP slope and a cash size gradient close to E1. The steepening and the disappearing gradient come from dropping those firm-years. The imputation is crude, but it is informative about direction.

*Required change.*

- Report the coverage and the selection diagnostics in Section 4.4 or Appendix D.
- Re-label E2 as what it is: firm-years without material acquisitions, plus 59 pro forma re-admissions.
- Add a bounds or imputation analysis for the excluded firm-years. Options include multiples on a grid; the purchase-price bound with M ≥ 1; or inverse-probability weighting on observables of the probability of being adjustable.
- Restate the causal language ("acquired growth flattens", "reflects acquired growth") as statements about sample composition, unless the imputation supports them.

**2. Inference on E1−E2 differences: the conclusions depend on the interval method, because the bootstrap is biased.**

- *Severity.* Major.
- *Location.*
  - Section 5.3: "the paired 90% interval ... 0.02 to 0.33, excludes zero";
  - Section 5.5: "−8.1 to −0.4 points, excludes zero";
  - Section 5.2 and Table 2, T(20%) on the cash basis;
  - introduction: "significantly flatter"; Table 2, column E1 − E2.

*Issue.* For the paired differences on which the paper builds its conclusions, Table 2's own standard errors imply non-significance:

| Difference | Estimate (SE) | z | p (normal) |
|---|---|---|---|
| GAAP slope | 0.13 (0.09) | 1.4 | 0.16 |
| Cash size gradient | −3.0 (2.4) | 1.3 | 0.21 |
| T(20%), cash | −3.8 (4.4) | 0.9 | 0.38 |

The percentile intervals exclude zero only because the bootstrap distributions are shifted away from the estimate.

*Evidence.* `c4_paired.py` and `c6b_intervals.py`; same paired firm-cluster design as `boot_pair` in `estimate_organic.py`.

- *GAAP slope.* Two IRLS seeds with B = 2,000 give percentile 90% intervals of [0.017, 0.294] and [0.020, 0.304], so the result is stable to Monte Carlo error. But the bootstrap mean is 0.149, against an estimate of 0.126 (IRLS) or 0.105 (exact LP). The basic interval is therefore about [−0.05, 0.23] with IRLS and [−0.10, 0.19] with exact LP (B = 600).
- *Other statistics (B = 2,000; B = 800 for the size gradient):*

| Statistic | Estimate | Bootstrap mean | Percentile | Basic | Bias-corrected |
|---|---|---|---|---|---|
| Size gradient, cash | −0.030 | −0.039 | [−0.085, −0.005] | [−0.055, +0.025] | [−0.067, +0.010] |
| T(20%) change, cash | −0.038 | −0.056 | [−0.138, −0.004] | [−0.073, +0.062] | [−0.114, +0.008] |

- *Control.* The paired difference in the P95 change shows no bias (estimate −0.027, mean −0.028). On the cash basis the pooled slope difference includes zero under every method (exact LP percentile [−0.007, +0.240]), as the paper says.

*Required change.*

- Report bias-robust intervals (BC or BCa, or a studentized bootstrap) together with the bootstrap bias.
- Make the standard errors and intervals in Table 2 agree on what is significant.
- Withdraw "significantly flatter", and "excludes zero" for the size gradient and T(20%), unless they survive.

**3. Multiple comparisons and forking paths.**

- *Severity.* Major.
- *Location.* Sections 5.2 to 5.10; Table 2; abstract; introduction ("Six findings stand out").

*Issue.* The paper reports each finding at 90% under two bases, two estimands, three thresholds and up to four periods, and builds narrative claims on single intervals. There is no designation of confirmatory statistics and no adjustment.

*Evidence.* `c6_multiple.py`.

- The headline block has 32 paired E1−E2 statistics, excluding the two weights, which are transforms of the spend ratio. Five 90% percentile intervals exclude zero. One of them, the 2010–19 GAAP slope, does so only by 0.00002. A sixth interval, T(40%) on the cash basis, ends exactly at 0.
- If the 32 tests were independent, five or more exclusions would occur with probability 0.21 under the null.
- The smallest normal p-value is 0.020 (spend ratio). Its Holm-adjusted p-value is 0.66, and its Benjamini–Hochberg q-value is 0.66.
- The capital-intensity gap is significant in one of four periods on one of two bases (finding 5).
- Period and threshold splits change signs. At the 10% flag threshold, the E2 cash slope flattens from −0.43 (2010–19) to −0.21 (2020–25), the opposite of the paper's reading (Table 2, 10% column).

*Required change.*

- Pre-designate a short list of confirmatory statistics. The natural list is: the P95 change, the pooled slopes, the spend ratio and the capital-intensity gap.
- Use 95% intervals, or adjust with Holm or a joint max-t bootstrap band.
- Label period splits, thresholds and decomposition components as exploratory.

**4. The implied weight of 7 to 13 is driven by counting maintenance S&M as growth spend, and by the choice of benchmark.**

- *Severity.* Major.
- *Location.* Section 5.4; Section 5.10(ii); Section 3.7 ("the spend-based weight of roughly 7 to 13 ... favors the second"); abstract; introduction ("Second"); Table 2.

*Issue.* The ratio σ/Δ (lagged S&M share over growth above the year's median) treats all S&M as growth spend. In the model, a firm growing at G spends σ = 0. Its S&M is therefore maintenance and belongs in a. The paper notes the upward bias but does not size it. The denominator is also close to zero for marginal firms: 18% of E2 ratios exceed 10. The median is therefore sensitive to the benchmark G and to the selection rule g > G.

*Evidence.* `c10_spend.py`, E2.

- Firm-years at or below the median growth have a median S&M share of 25.5%, against 41.4% above it.
- The median of (S&M share − 25.5%) / excess growth is 1.13. Divided by α ∈ [0.25, 0.45], this gives X ≈ 2.5 to 4.5, at the level of the screening weights the paper contrasts with.
- Benchmark sensitivity:

| Benchmark and selection | Median ratio | Implied weight |
|---|---|---|
| Median growth (paper) | 3.26 | 7.2–13.0 |
| Aggregate (revenue-weighted) growth | 2.86 | 6.4–11.4 |
| Median growth, selecting g > G + 5 pp | 2.53 | 5.6–10.1 |
| Median growth − 5 pp | 2.91 | 6.5–11.7 |

- E1 shows the same pattern: 2.91 unadjusted, 0.99 net of maintenance.
- The ratio is robust to how acquirers are treated: 3.1 to 3.3 under the imputations of finding 1, and 3.2 to 3.3 across thresholds.
- The standard errors of the weights in Table 2, (0.5) and (1.0), contain no uncertainty about α.

*Required change.*

- Report the maintenance-adjusted ratio and the benchmark and selection sensitivity.
- Restate the range of implied weights accordingly.
- Revisit the use of the weight in Section 3.7 (choosing between the two structures of `prop:industry`) and in Section 8.1.
- State that the standard errors are conditional on α.

**5. The capital-intensity gap is mostly mechanical, and the model's distinctive prediction is not detected.**

- *Severity.* Major.
- *Location.* Section 5.6; Section 5.10(iv); introduction ("Fourth"); Table 2; Section 7 (`horizons.tex`, levers paragraph, "lever 3").

*Issue.* The paper sorts on capex over revenue, which is subtracted from the cash margin, and calls the result "partly mechanical". It is mostly mechanical. The model's own prediction is that the cash score falls by k·g. This implies a gap that grows with g. That interaction is not tested.

*Evidence.* `c9_capint.py`, 2023–25.

| Score basis | E2 gap | E1 gap |
|---|---|---|
| Cash score as defined | −10.6 [−18.7, −3.0] | −14.9 [−22.5, −4.2] |
| Same score before deducting capex (OCF − SBC) | −2.9 [−13.2, +5.4] | −6.1 [−16.4, +3.3] |

- Firm-years in the top 5% of the high-capex half average capex of 6.8% of revenue, against 1.1% in the low half.
- In a τ = 0.90 quantile regression of the E2 cash margin on g × high-capex, the interaction is +0.05 (cluster-bootstrap SE 0.23).
- The other periods show no consistent gap:

| Estimand | 2010–15 | 2016–19 | 2020–22 |
|---|---|---|---|
| E1, cash | −6.6 | −11.5 | +2.5 |
| E2, cash | −0.6 | −9.2 | +2.1 |

- *Coding.* `hi_k` is built with `(x > x.median()).astype(float)`, so a firm-year with missing capex is coded as low capital intensity (12 firm-years in 2023–25). These firm-years enter the GAAP comparison (`estimate_revised.py` line 273; `estimate_organic.py` line 219).

*Required change.*

- Report the pre-capex gap alongside the cash gap.
- Test the growth interaction.
- Report all periods with multiplicity control.
- Code missing capex as missing.
- Drop "the pattern the capital channel predicts" as evidence, and drop the lever-3 inference in Section 7.

### Moderate

**6. T(40%): the bootstrap is invalid, draws are dropped silently, and two firm-years carry the "exception".**

- *Severity.* Moderate.
- *Location.* Section 5.2; Table 2 (rows for the change in T(40%)); Table 5 (`tab:threshold`); abstract; introduction ("except at the thinly populated 40% threshold of the organic frontier"); Section 5.10(v).

*Issue.* E2 T(40%) in 2023–25 is the 95th percentile of 12 observations. That is an interpolation between the second-largest value and the maximum, and the firm-cluster bootstrap is not valid for it. The paper's own argument against the edge statistic (Section 5.1) applies here. Bootstrap draws with fewer than 10 observations return NaN and are dropped by `nanquantile`. The interval is therefore conditional on a selected event.

*Evidence.* `c5_T40.py` and `c5b_T40_firms.py`.

- NaN shares: 27.7% (E2, GAAP) and 29.8% (E2, cash).
- Two firm-years determine the statistic. Exzeo Group 2025 has a GAAP margin of 48.8% at growth of 62%; Palantir 2025 has 31.6%. The third-highest margin in the cell is 8.4%.
- At the 10% threshold, Table 2 reports no point estimate but `empirics_organic.json` holds an interval for it.
- Small-cell bias is also material. Drawing 12 observations from the pooled 2010–22 cell at g ≥ 40% understates that cell's P95 by 5 to 7 points; drawing 80 understates it by 0.2 to 1.3 points.

*Required change.*

- Do not report bootstrap intervals for cells below about 30 observations. Use exact order-statistic intervals or an m-out-of-n bootstrap instead.
- Report NaN shares.
- Remove the "except at the 40% threshold" clause from the abstract, the introduction and Section 5.10. As the paper itself says in Section 5.2, it rests on 12 firm-years.

**7. The headline E2 GAAP slope (−0.59) is not the quantile-regression minimizer.**

- *Severity.* Moderate.
- *Location.* Introduction; Section 5.3; Section 5.10(i); Table 2; Appendix E.2 ("−0.59 against −0.46"); `estimand_notes.md`.

*Issue.* The statsmodels `QuantReg` IRLS solver reports convergence at −0.5851. The exact LP solution (HiGHS) is −0.5640, and the set of minimizers is [−0.5643, −0.5640]. The check loss is nearly flat between the two points: 42.8505978 against 42.8505973. Every other pooled and period slope matches LP to four decimals.

*Evidence.* `c1_slopes.py`, `c1b_irls.py`, `c1c_nonunique.py`. The corrected E2 slope is −0.56, identical to the exclusion-only −0.56 (−0.5604). The pro forma adjustment therefore changes nothing for this statistic, and the E1−E2 point difference becomes 0.105.

*Required change.* Estimate the quantile regressions with an exact solver (for example, the Barrodale–Roberts or interior-point methods of R `quantreg`, or an LP), in both the point estimates and the bootstrap. Check uniqueness, and regenerate every quoted value.

**8. The choice of τ = 0.90 and of the 0 to 60% window is unjustified, and the slope depends on the window.**

- *Severity.* Moderate.
- *Location.* Section 5.1; Section 5.3; Table 6 (`tab:local`); Table 2.

*Issue.* A linear fit to a concave model frontier has an average slope that depends on the window by construction. The quantile levels are also inconsistent: 0.90 for the slopes, 0.95 for φ and for the size gradient.

*Evidence.* `c1_slopes.py`, exact LP, τ ∈ {0.75, 0.80, 0.85, 0.90, 0.95}:

| Sample and basis | g ∈ [0, 0.6] | g ∈ [0, 1.0] | g ∈ [−0.1, 0.6] |
|---|---|---|---|
| E2, GAAP | −0.55 to −0.63 | −0.38 to −0.44 | −0.44 to −0.51 |
| E2, cash | −0.38 to −0.49 | −0.26 to −0.38 | — |
| E1, GAAP | −0.45 to −0.54 | −0.35 to −0.43 | — |

"About half a point" holds across τ within the chosen window. Over 0 to 100% growth it is about a third.

*Required change.*

- Add a τ × window sensitivity table.
- Justify the window: for example, data support, or the range over which Proposition 1's concavity is to be summarized.
- Consider reporting the local slope as a function of g instead of one average.
- Use one quantile level throughout, or explain the difference.

**9. The estimated object differs from the partial frontier the paper defines; order-m is cited but not used; and the "reversal" of the flat frontier comes from the change of estimator.**

- *Severity.* Moderate.
- *Location.* Section 5.1; Section 2.3; introduction ("we adapt partial-frontier estimators (Cazals et al., 2002; Aragon et al., 2005)"); Section 3.7 (`prop:industry`, Ψ_χ); Appendix E.2 ("a finding (the flat frontier reversed)").

*Issue.* Section 5.1 defines φ(g) as the quantile of margin among firm-years with growth of at least g. This is the dominance-cone version of the Aragon et al. order-α frontier and matches Ψ_χ in Definition 2. The slope finding instead uses the local conditional quantile Q_0.9(m | g). The two objects differ, and only the first is the one Proposition 7 speaks to. The order-m frontier is computed in `estimate_frontier.py` (`order_m`, M = 25) but reported nowhere.

*Evidence.* On the rebuilt panel, the dominance-cone frontier is much flatter (`c16_dominance.py`; least-squares slope over g ∈ [0, 0.6]):

| Estimand | φ_0.9, GAAP | φ_0.9, cash | φ_0.95, GAAP | φ_0.95, cash |
|---|---|---|---|---|
| E2 | −0.31 | −0.19 | −0.23 | −0.06 |
| E1 | −0.20 | −0.16 | −0.20 | −0.05 |

`notes/empirics_results.json` (`envelope`) shows cash-basis order-α slopes of −0.06 to −0.25 by period on the rebuilt data. The earlier flat frontier therefore survives the data rebuild under the original estimator. The "reversal" reflects the switch to local quantiles that the first-round referee recommended.

*Required change.*

- Report both objects and say which one maps to Ψ_χ.
- Either report order-m results or remove the claim to have adapted Cazals et al.
- Correct the protocol's account of why the finding changed.

**10. The size gradient omits period effects, and "disappears" accepts the null.**

- *Severity.* Moderate.
- *Location.* Section 5.5; Table 7 (`tab:scale`); Table 2; introduction ("Third"); Appendix D ("Quantile and fixed-effects regressions drop growth above 150%").

*Issue.* The τ = 0.95 regression of R on log revenue pools 2010–25 with no period effects. Over the same years, P95 scores fell and the median size of included firms rose, from $397 million in 2016–19 to $621 million in 2023–25, partly because the $100 million threshold is nominal. The E1 cash gradient, −5.7 (2.8), has z ≈ 2.0. The E2 gradient, −2.7 (3.4), has a 90% interval of about [−8.3, +2.9], which contains the E1 value.

*Evidence.* `c8_scale.py`, exact LP, points per tenfold increase in revenue:

| Specification | E1, cash | E2, cash | E1, GAAP |
|---|---|---|---|
| Pooled (paper) | −5.7 | −2.7 | +1.6 |
| With period dummies | −2.8 | −0.9 | +2.5 |
| Dropping growth above 150% | −5.1 | — | — |

The scale regression keeps growth above 150%, contrary to Appendix D.

*Required change.*

- Include period effects.
- Describe the gradient as weak and not robust under either estimand.
- Replace "disappears" with an equivalence statement or an interval.
- Make Appendix D match the code.

**11. The post hoc change of primary estimand is disclosed incompletely, and not where readers need it.**

- *Severity.* Moderate.
- *Location.* Section 4.4; Appendix E.2 ("Choice of estimand"); E.5 and Table 18; abstract and introduction; Section 3.7.

*Assessment.* There is much to credit:

- `estimand_notes.md` §1 records the order of events, the motivation and what was known at the decision;
- both estimands are shown side by side, with paired differences and flag thresholds;
- the switch was not self-serving: it weakened the size gradient and the transient-surplus claim, and the paper says so.

*Gaps.*

- (a) Section 4.4 presents E2 as defined in advance ("We report two explicitly defined estimands"). A reader of Sections 4 and 5 is not told that E2 became primary after the E1 results and the exclusion-only robustness row (−0.56 and −0.43; P95 changes of −11.4 and −12.4) were known.
- (b) Appendix E.2 omits what was known at the decision. It also omits that, after the E2 point estimates of a test run had been seen, two pro forma rules were added: the adjustment applies to flagged years only, and the ambiguity exclusion (`estimand_notes.md` §1, "Order of the pro forma rules").
- (c) E.5 classifies the switch as an "error ... caught by ... reversing course openly". It was a researcher degree of freedom, not an error.
- (d) Section 3.7 still quotes the E1 slopes, "−0.46 (standard error 0.14) ... −0.37 (0.11)", as "the" estimates, and calibrates ℓ to an average slope of −0.4. This is inconsistent with E2 being primary.

*Required change.*

- Add one sentence in Section 4.4 stating the timing and pointing to Appendix E.
- In Appendix E.2, list what was known at the decision and the two rules added after the test run, and report E2 without those rules (the additive formula applied to every firm-year with disclosures).
- Reclassify the item in E.5.
- Present E1 and E2 symmetrically in the abstract, or flag E2 as chosen after the fact.
- Update Section 3.7.

**12. The calibration anchor carries no sampling uncertainty, and the conclusion said to have changed is within noise.**

- *Severity.* Moderate.
- *Location.* Section 7.3 (`sec:horizons-ranges`, "Anchor"); introduction ("up to 39% ... transient"); Appendix E.2 ("fell from 7 to −1 points, so the claim ... now holds only at the lower bound").

*Evidence.* `c15_anchor.py`, firm-cluster bootstrap with the P95 cut-off and G re-estimated in every draw, B = 1,000:

| Anchor | Median Π_ub [90% interval] | Transient share, upper bound | Median Π_lb |
|---|---|---|---|
| E2 (n = 20) | −0.7 [−15.7, +16.3] | −1% [−35, +29] | 19.8 [10.8, 26.9] |
| E1 (n = 15) | +6.7 [−16.2, +16.7] | — | — |

The change from +6.7 to −0.8 that the paper treats as changing a conclusion is a fraction of that width.

*Required change.* Report intervals for the anchor statistics, and do not draw conclusions from the sign of a median of 15 to 20 firm-years.

**13. Stochastic frontier: no inference, cohort-specific frontiers, and survivorship.**

- *Severity.* Moderate.
- *Location.* Section 5.7 (title: "The distance to the frontier widened, mainly through new entrants").

*Issue.* The cohort shortfalls come from frontiers estimated separately for each cohort (`estimate_revised.py` lines 295 to 308), so they are not distances to a common frontier. No standard errors are reported. The pre-2019 cohort in 2023–25 is a set of survivors. Under the model, chosen points lie on each firm's own frontier, so the half-normal term captures heterogeneity in m0 and in choices rather than waste.

*Evidence.* `c11_sfa.py`.

- With a common frontier and Jondrow–Lovell–Materov–Schmidt E[u | ε], the 2023–25 gap between the 2019+ and pre-2019 cohorts is 14.0 [8.9, 20.3] (GAAP) and 10.9 [6.5, 15.0] (cash). The qualitative result survives.
- Of the 138 pre-2019 firms observed in 2016–19, 78 remain in 2023–25. Their 2016–19 median GAAP margin was 2.0%, against −0.2% for those that left.
- The 2023–25 GAAP mean shortfall has a 90% interval of [23.3, 32.8].

*Required change.*

- Estimate a common frontier.
- Bootstrap the shortfalls.
- Compare survivor-balanced panels, or decompose entry and exit.
- Add the interpretive caveat.

**14. Period comparisons of slopes are untested, and "never with a full point" is not supported in 2020–25.**

- *Severity.* Moderate.
- *Location.* Section 5.3 ("steeper in 2020–25 than in 2010–19 under both estimands"; "the steepening of the cash-basis slope in observed scores reflects acquired growth"; "never with a full point"); Appendix E.2.

*Evidence.* `c13_period.py`: firm-cluster bootstrap of the 2020–25 minus 2010–19 slope, B = 400.

| Estimand and basis | Difference | 90% interval | Significant at 10% |
|---|---|---|---|
| E1, GAAP | −0.45 | [−0.63, −0.10] | yes |
| E2, GAAP | −0.33 | [−0.60, +0.01] | no |
| E1, cash | −0.15 | [−0.35, +0.19] | no |

- The paper therefore explains a non-significant E1 steepening by acquired growth.
- The E2 2020–25 GAAP slope is −0.79 (0.15), with a 90% interval of [−0.98, −0.48]. A 95% normal interval includes −1.

*Required change.* Test period differences formally, and qualify "never with a full point".

### Minor

**15. The within-firm specification does not match the model's timing, and the E2 version is not reported.**

- *Location.* Section 5.3, last paragraph; Proposition 7(v).
- *Issue.* Under the model, spend at t buys growth at t+1. Section 3.1 says g_{t+1} + m_t is the consistent pairing, and the spend ratio uses lagged S&M. The fixed-effects regression nevertheless uses g_t.
- *Evidence.* `c12_within.py` and `c12b_lead.py`.
  - The E1 results reproduce: +0.080 (0.069) and −0.019 (0.041).
  - E2: +0.07 (0.10) and −0.03 (0.06).
  - Regressing m_t on g_{t+1} with firm and year fixed effects gives −0.13 (0.07) on E2 GAAP. With g_t included, the g_{t+1} coefficient is −0.17 (0.08).
  - Half the variance of growth is within firms (0.51), so measurement error and attenuation are live alternatives to "growth surprises against committed costs".
- *Required change.* Report the lead specification and E2, and soften the interpretation.

**16. Bootstrap design and reporting.**

- *Location.* Notes to Tables 2 and 4 to 8; Section 5.1.
- *Issues.*
  - Replications vary by statistic: 200 for slopes and the size gradient, 300 for levels, 400 for the capital split, 500 for changes, 999 for the gap. Only Table 4 states B. B = 200 is thin for 90% percentile endpoints.
  - The seeds (20261029 and 20261028) are not stated, and a single sequential random stream makes the draws depend on call order.
  - Table 2 mixes E1 draws from `estimate_revised.py` with paired draws from `estimate_organic.py`. Monte Carlo differences are visible: slope 2010–19 E1 SE 0.140 against 0.155 from the script's own draws; capital-gap E1 interval [−22, −3] against [−22, −5].
  - The capex median split is not re-estimated within each draw.
  - Draws returning NaN are dropped silently (finding 6).
- *Required change.* State B and the seed in each table note; use B ≥ 999 for intervals; take each table's draws from one source; re-estimate splits within draws; report NaN shares.

**17. The replication package does not regenerate the paper.**

- *Location.* Appendix D ("Reproducibility"); `code/REPLICATION_README.md`.
- *Issue.* `estimate_organic.py` is missing from both the script list and the run order, yet it writes Table 2, the E2 macros and `notes/calibration_anchor_E2.json`. `calibrate_horizons.py` now reads that file (lines 266 to 273), so the documented order cannot rebuild Section 7.
- *Required change.* Add the script to both lists and fix the order.

**18. E2 pairs organic growth with consolidated margins.**

- *Location.* Section 4.4; Table 2 notes.
- *Issue.* For adjusted firm-years, the margin includes the acquired business, deal costs and, on the GAAP basis, amortization of acquired intangibles. This is stated only in the script header.
- *Required change.* State it in the paper, and note the direction of the bias by basis.

**19. Documentation mismatches.**

- The Table 2 note says "The spend ratio of Section 5 is the 25% column". But the text's interquartile range (1.9 to 7.3), S&M share (41%) and excess growth (11.5) are E2 values. The 25% column has 7.4 and 11.4.
- Appendix D's statement about dropping growth above 150% is false for the size regression (finding 10).
- The weight standard errors are conditional on α (finding 4).

---

## Checks run

All scripts are in `notes/reviews/paper1_v1/referee3_checks/`. `lib.py` rebuilds the samples by executing the unchanged data-preparation block of `estimate_organic.py`, and reproduces Table 2, panel C exactly: E1 1,929 (293); E2 1,516 (283), of which 59 adjusted; 10% 1,118; 25% 1,457; 50% 1,664.

1. `c1_slopes.py`, `c1b_irls.py`, `c1c_nonunique.py`. IRLS against exact LP for every pooled and period slope; the set of minimizers; the τ × window grid.
2. `c4_paired.py`. Paired E1−E2 bootstrap of the pooled slopes: IRLS with two seeds at B = 2,000, and exact LP at B = 600. Reported: mean, median, percentile intervals and P(diff ≤ 0).
3. `c6_multiple.py`, `c6b_intervals.py`. A count of the paired comparisons; Holm and BH adjustment; percentile, basic and bias-corrected intervals for the size gradient, T(20%) and the P95 change.
4. `c5_T40.py`, `c5b_T40_firms.py`. NaN shares in the T(40%) bootstrap; the firm-years behind the statistic; small-cell bias of the sample P95.
5. `c7_impute.py`, `c7b_impute_more.py`. Re-admission of the excluded firm-years with imputed organic growth, M ∈ {1, 2, 4, 8}.
6. `c8_scale.py`. The size gradient with period effects and with the growth filter of Appendix D.
7. `c9_capint.py`. The pre-capex gap, the growth interaction, all periods, and the coding of missing capex.
8. `c10_spend.py`. The spend ratio under alternative benchmarks and selection rules, and net of maintenance.
9. `c11_sfa.py`. Common-frontier JLMS cohort means with bootstrap intervals; residual skewness; survivorship.
10. `c12_within.py`, `c12b_lead.py`. Within-firm slopes on E1, E2 and E2x25, and with next-year growth.
11. `c16_dominance.py`. The dominance-cone quantile frontier φ_χ(g) of Section 5.1, at χ = 0.90 and 0.95.
12. `c13_period.py`. Bootstrap tests of period differences in slopes.
13. `c14_p95.py`. The P95 change with a real-dollar threshold, and DiNardo–Fortin–Lemieux reweighting of 2023–25 to the 2016–19 distributions of growth and size.
14. `c15_anchor.py`. Bootstrap of the calibration-anchor medians.
15. JSON cross-checks against the text.
    - Table 2, all rows quoted in Sections 5.2 to 5.8.
    - Table 4 changes and the leave-one-out ranges (−11.1 to −12.4 GAAP; −12.7 to −16.1 cash).
    - Table 14 ranges (−9.9 to −26.3 points; slopes −0.24 to −0.60).
    - Table 7 slopes (0.70 (1.27); −2.49 (1.22)).
    - The SFA figures in Section 5.7.
    - The spend-ratio figures in Section 5.4, which are E2 values.
    - The counts of fast growers in Section 5.2 (18 / 57–98; 132 / 175–255).

## What I found correct

- **Point estimates reproduce.** E1 and E2 point estimates in Table 2 reproduce from the panel; every slope except the E2 pooled GAAP slope (finding 7) matches an exact solver. The fixed-effects coefficients, the counts and the leave-one-out ranges match the text.
- **The decline at the top is robust.** It holds in every Table 14 variant, in leave-one-firm-out, with a real-dollar threshold (−11.6 and −14.9) and under the imputations of finding 1 (−7.5 to −11.7). Reweighting 2023–25 to the 2016–19 growth distribution removes the E1 decline (+4.5 GAAP, +1.9 cash) and the E2 cash decline (+6.2), but leaves −5.7 for E2 GAAP. This supports "as fast growers became scarcer" for E1. The paper should report this decomposition rather than infer it from Table 5.
- **The bootstrap design is right in principle.** Resampling firms preserves serial dependence; period changes are paired within firm; the E1−E2 design draws one set of firms for both estimands. Percentile endpoints are stable across seeds at B = 2,000. The problem is bias and interval type (finding 2), not Monte Carlo noise.
- **The identification statements are sound.** The paper does not read the cross-sectional slope as any firm's trade-off (Proposition 7(iv)). It does not claim to estimate α, and correctly notes that the log-log slope is one under optimization. It abandons the edge statistic, with Table 15 showing why.
- **The pro forma formula is right.** It is the correct constant-perimeter growth. The ambiguity is bracketed: E2add and E2max give −0.585/−0.433 and −0.591/−0.442, an immaterial range. The approximation errors are documented in `estimand_notes.md` §3.
- **The spend ratio does not depend on the treatment of acquirers.** It is 3.1 to 3.3 across thresholds and imputations. The problem is the proxy (finding 4).
- **The cohort gap in the stochastic frontier survives a common frontier**, although its interpretation needs work (finding 13).
- **The estimand switch was documented in good faith.** The record in `estimand_notes.md` is candid; both estimands are always shown; and the switch did not favor the paper's priors. What is missing is placement and completeness (finding 11).
- **Data construction is sound.** The as-first-reported design, the restatement example, missing capex treated as missing in the margins, the duplicate-registrant rule and the survivorship-free universe are all appropriate and well documented.
