# Referee report: econometrics (independent cross-model review)

Paper: "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation" (paper1_v1).
Scope: Sections 4, 5 and 7.3 (anchor), Table 2 (estimands), Tables 3 to 8, 14, 15, Appendix D and E.2; code in `code/estimate_revised.py`, `estimate_organic.py`, `estimate_frontier.py`, `paper_stats.py`, `build_panel_v2.py`; outputs in `notes/empirics_revised.json`, `empirics_organic.json`, `estimand_notes.md`, `calibration_anchor_E2.json`. No other review file was read.

All checks below were run on the paper's own frames. The E1 and E2 frames were rebuilt by executing the data-construction part of `estimate_organic.py` (everything before `def clean`) without the bootstrap; point estimates reproduce the paper's to four decimals. Check scripts: `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/chk1.py` to `chk9.py`.

## Summary

The data construction (as-first-reported XBRL panel, growth within filing, inactive registrants retained) is careful, and the switch from an edge statistic to upper quantiles, fixed-threshold frontier points and an upper-quantile slope was the right response to the earlier referee round. The descriptive core holds up: the 95th percentile of the score fell by 12 to 15 points between 2016-19 and 2023-25 and the fall survives leaving out any single year or firm; the upper-tail slope is significantly negative and well above minus one under every interval type, quantile and window I tried; a reweighting of 2023-25 to the 2016-19 growth mix (which the paper does not do) confirms that the decline is compositional. Every standard error and interval quoted in the text matches the code output.

The inferential layer built on top of this is weaker than the text claims. Five findings are major. (1) The implied weight on growth of 7 to 13, which appears in the abstract, is an artifact of taking the median of S&M share over excess growth: the ratio is 10 in the lowest tercile of excess growth and 1.5 in the highest, the S&M share barely rises with excess growth (median-regression slope 0.2 to 0.5, intercept 35 points), and the implied weight falls monotonically to 2 to 4 as the denominator is bounded away from zero. (2) The paired E1 minus E2 contrasts the paper reads as significant ("significantly flatter", "reflects acquired growth rather than saturation") rest on 90% percentile intervals that barely exclude zero; basic and normal intervals include zero, 5 of 32 contrasts exclude zero against 3.2 expected under the global null, none survives a Holm correction, and the cash-basis "steepening" that E2 supposedly removes has p = 0.48 in E1 itself. (3) The E2 interval for the change in T(40%), reported as +24 [+3, +38], silently discards 30 to 35% of bootstrap replicates (fewer than ten fast growers in the resample) and the "rise" is a sample-size artifact (n = 12 against 18, same top firms). (4) The capital-intensity gap is mostly the deduction itself: adding capital spending back to the cash score leaves a gap of -6 [-15, +5] (E1) and -3 [-12, +6] (E2); sorting on a firm's median or lagged intensity leaves nothing significant. (5) The calibration anchor (20 firm-years, 12 firms, 14 firm-years from 6 firms) carries no sampling uncertainty; a firm-cluster bootstrap gives a median upper-bound surplus of -1 with a 90% interval of -16 to +16, so the E1-to-E2 "change in conclusion" (7 to -1) is noise. A sixth finding concerns transparency: the switch of the primary sample to E2 after the robustness results were known is disclosed only in Appendix E.2, the pro forma ambiguity rule added after a test run is not disclosed, and E2 is in substance the exclusion-only robustness sample (410 of 469 affected firm-years dropped, 59 adjusted), which the label "organic frontier" obscures.

## Recommendation

Major revision. The descriptive findings (i), (v) and (vi) of Section 5.10 stand. Findings (ii), (iii) and (iv) and the E1-versus-E2 narrative need to be re-estimated or rewritten as stated below, the T(40%) intervals on E2 withdrawn, and the anchor given firm-level uncertainty. None of this requires new data.

## Findings

### 1. The implied weight on growth (7 to 13) is a construction artifact [Major]

Location: Section 5.4; Table 2 rows "Spend-to-excess-growth ratio" and "Implied weight on growth"; abstract ("growth spending implies a weight on growth of 7 to 13"); Section 5.10 (ii); Section 8.1.

Issue: The statistic is the median over firm-years with g > G_t of sm_lag_share / (g - G_t). The denominator is a noisy, selected quantity bounded away from zero only by the selection itself, so the ratio is dominated by firm-years with excess growth near zero. The model's first-order condition sigma = alpha (X - k) Delta implies proportionality; the data reject it, because S&M is mostly a level that does not vary with excess growth. Reading the level ratio as alpha (X - k) therefore attributes the maintenance component of S&M (the paper itself names this bias, Section 5.4) to growth purchase, and the paper's "uncertain net sign" understates a bias of a factor of two to five.

Evidence (chk6.py, E2 sample, n = 636):
- Median ratio by tercile of excess growth: lowest tercile (median excess 3.3 points) 10.5; middle (11.5 points) 3.5; highest (27.8 points) 1.8. Median S&M share in the three terciles: 34%, 41%, 52%.
- Median ratio when excess growth is required to exceed 0, 5, 10, 15, 20, 30 points: 3.26, 2.53, 2.17, 1.84, 1.63, 1.08; implied weight at alpha = 0.45: 7.2, 5.6, 4.8, 4.1, 3.6, 2.4; at alpha = 0.25: 13.0, 10.1, 8.7, 7.4, 6.5, 4.3.
- Median regression of S&M share on excess growth: intercept 0.354, slope 0.44 (E1: 0.361, 0.18). Least squares through the origin: 1.36 (E1: 1.01). On the marginal reading alpha (X - k) is 0.2 to 1.4, so X - k is 0.5 to 5.8, which spans the screening weights of two to three the paper says firms "act well above".
- Benchmark sensitivity: G = 0 gives 1.84; G = 5% gives 2.23; G = year P25 gives 2.24; G = year P75 gives 4.31.
- The same pattern holds in E1 and in the exclusion-only sample.

Required change: Drop the level-ratio estimate of alpha (X - k) or report it only as an upper bound that assumes every dollar of S&M buys growth. Estimate the marginal spend per point of excess growth (median or quantile regression of S&M share on excess growth, with and without firm effects) and report the implied weight from the slope, with its range; report the tercile table. Revise the abstract, Section 5.10 (ii) and Section 8.1 accordingly: the data do not show that firms act on a weight "well above" screening weights. The calibration's use of the S&M share as an upper bound on sigma (Section 7.3) is consistent with this reading and does not need to change.

### 2. The E1 minus E2 contrasts are not significant under alternative interval types or any familywise correction, and one contrast was never a finding [Major]

Location: Introduction ("in observed scores the GAAP slope is significantly flatter"); Section 5.3 ("Acquired growth flattens the GAAP slope: the paired 90% interval ... 0.02 to 0.33, excludes zero"; "the steepening of the cash-basis slope in observed scores reflects acquired growth"); Section 5.5 ("the paired 90% interval ... -8.1 to -0.4 points, excludes zero, so the cash-basis gradient in observed scores reflects acquired growth rather than saturation"); Section 5.10 (iii); Appendix E.2 ("Three conclusions of the earlier draft changed").

Issue: (a) All intervals in the paper are Efron percentile intervals of a firm-cluster bootstrap; the paper does not say so. For the two headline contrasts the percentile interval excludes zero by 0.02 and 0.4 points while the basic (Hall) and normal intervals include zero. (b) Table 2 reports 26 paired contrasts (32 including sub-rows) with no multiplicity adjustment; the number excluding zero at 90% is what the global null predicts. (c) The cash-basis steepening from -0.25 to -0.40 in E1, which the paper says E2 "removes", is itself not distinguishable from zero. (d) The GAAP E1 minus E2 slope difference is specific to tau = 0.90.

Evidence:
- Re-run paired bootstrap (chk3.py, B = 200 for slopes and scale, 400 for the capital split, 500 for P95): slope_op_pooled E1 - E2 = +0.126, se 0.080; percentile [+0.021, +0.291], basic [-0.039, +0.231], normal [-0.006, +0.258]; two-sided percentile p = 0.06, normal p = 0.12. scale_tenfold_cash E1 - E2 = -0.030, se 0.024; percentile [-0.080, -0.003], basic [-0.057, +0.020], normal [-0.069, +0.009]; p = 0.09 / 0.20. The paper's own draws (`empirics_organic.json`, headline block) give se 0.089 and 0.024 for these two contrasts, i.e. z = 1.4 and 1.3.
- Multiplicity (from the paper's JSON, 32 contrasts, normal p from est/se): 5 exclude zero at the 90% percentile level against 3.2 expected; smallest p is 0.020 (spend ratio, a contrast that is mechanical because acquired growth enlarges the denominator), then 0.067, 0.071, 0.155 (slope_op_pooled), 0.176, 0.187, 0.196, 0.208 (scale_cash). Holm at a familywise 10% level rejects none.
- Steepening test (chk4.py): slope(2020-25) minus slope(2010-19), firm-cluster bootstrap. E1 GAAP -0.45, se 0.16, p = 0.03; E1 cash -0.15, se 0.15, p = 0.48; E2 GAAP -0.33, se 0.19, p = 0.11; E2 cash +0.05, p = 0.87. The sentence "After SBC the observed slope steepened ... but the organic slope did not, so the steepening ... reflects acquired growth" attributes a non-result.
- tau sensitivity (chk1.py, window [0, 0.6]): E1 minus E2 GAAP slope difference is 0.02 at tau = 0.75, 0.01 at 0.80, 0.10 at 0.85, 0.13 at 0.90, 0.18 at 0.95.
- Leave-one-year-out (chk2.py): the pooled GAAP difference ranges 0.08 to 0.20 across dropped years; not driven by one year.

Required change: State the interval type; report basic or BCa intervals alongside percentile ones for the contrasts, or report bootstrap p-values. Treat the E1 minus E2 contrasts as a family and say so; with a Holm or Romano-Wolf correction none is significant, so the text must downgrade "significantly flatter" and "reflects acquired growth rather than saturation" to "the point estimates move in the direction acquired growth would produce; the differences are within sampling error". Delete the cash-basis steepening sentence or report its test. Rewrite Appendix E.2's "three conclusions changed": one point estimate moved (GAAP slope -0.46 to -0.59) and two non-significant patterns became other non-significant patterns.

### 3. The E2 change in T(40%) rests on an invalid bootstrap and a sample-size artifact [Major]

Location: Table 2 rows "Change in T(40%)"; Section 5.2 ("On the organic frontier (E2) the 40% point rose, by 23 points ... and 24 after SBC (+3 to +38)"); Section 5.10 (v) and abstract ("except at the thinly populated 40% threshold of the organic frontier"); Section 5.1 claim that the four statistics' "meaning does not depend on sample size".

Issue: `T` returns NaN when fewer than ten resampled firm-years grow at least 40% (estimate_revised.py line 126; estimate_organic.py line 404) and `np.nanquantile` then drops those replicates. For E2 in 2023-25 (12 fast growers) this discards about a third of the replicates, and the survivors are the resamples with unusually many fast growers. Separately, with 12 observations the "95th percentile" lies between the two largest margins, so T(40%) in E2 exceeds T(40%) in E1 (79 against 74) with the identical top firms (Exzeo, Palantir); the "+24" is the difference between a near-maximum of 12 observations and a 95th percentile of 55.

Evidence (chk8.py, 500 replicates): E2 GAAP 150 NaN replicates, E2 cash 174; E1 15 and 17. Share of replicates with fewer than 15 fast growers in 2023-25: 0.77 (E2), 0.23 (E1). Top four margins among g >= 0.4 in 2023-25 are identical in E1 and E2 (GAAP 3.3, 8.4, 31.6, 48.8; cash 21.8, 26.4, 31.7, 43.7); E2's P95 is 39.4 (GAAP) against E1's 34.2 only because n is 12 rather than 18. E2's 2016-19 base is lower (56.0 against 61.5) because the exclusion removes 24 of 80 fast growers.

Required change: Remove the T(40%) intervals for E2 (and flag E1's) or replace them with a statistic that is valid at this cell size: a fixed-m order-m frontier (Cazals, Florens and Simar) with m well below the cell size, or subsampling. Report the minimum cell size at which the bootstrap is used and never drop replicates silently (return the statistic as missing for the whole cell instead). Delete "except at the thinly populated 40% threshold of the organic frontier" from the abstract and Section 5.10; nothing happened at that threshold. Qualify the "meaning does not depend on sample size" sentence: the estimands are N-invariant, the near-maximum estimates are not.

### 4. The capital-intensity gap is largely mechanical and is presented as a finding [Major]

Location: Section 5.6; Table 2 rows "Capital-intensity gap"; abstract and Introduction ("since 2023 the upper tail of the cash-basis score has been 11 points lower for capital-intensive firms ... with no comparable gap on the GAAP basis"); Section 5.10 (iv).

Issue: The sorting variable (capex plus capitalized software over revenue) is subtracted from the outcome (free cash flow after SBC over revenue). A gap on the cash basis and none on the GAAP basis is then an accounting identity, not a test of Proposition 5, whose content is that the cash score falls in proportion to growth (k g). The paper says "partly mechanical" and then lists the gap as the fourth of six findings.

Evidence (chk5.py, 2023-25, 90% firm-cluster intervals):
- Contemporaneous sort, cash score: E1 -14.9 [-21.3, -3.5], E2 -10.6 [-17.5, -2.6] (reproduces the paper).
- Same sort, cash score with capital spending added back (g + OCF/revenue - SBC/revenue): E1 -6.1 [-14.6, +4.5], E2 -2.9 [-12.1, +5.7]. Operating-cash-flow score (no capex, no SBC deducted): -1.5 and -2.4, both inside wide intervals.
- Sort on the firm's median intensity over all its years: cash E1 -5.9 [-15.5, +2.2], E2 -4.7 [-13.8, +3.5]; GAAP +2.3 and +3.6.
- Sort on lagged intensity: cash E1 -8.5 [-16.1, -0.3], E2 -5.9 [-15.9, -0.6]; GAAP -0.6 and +2.4.
- Median intensity of the high half is 3.7%, 90th percentile 9.4%; that alone accounts for 4 to 9 points of a P95 gap.
- Minor code point: `hi_k` is built as `(x > x.median())`, so firm-years with missing capital intensity (12 in 2023-25) fall in the low-intensity group for the GAAP basis; immaterial here (-1.9 against -2.1) but wrong.

Required change: Either present the split as an accounting fact and remove it from the list of findings, or test Proposition 5 as stated: regress the upper quantile of the cash score on g, capital intensity and their interaction (or compare the gap across growth bands), and sort on predetermined intensity. Fix `hi_k` to exclude missing intensity. Rewrite abstract, Introduction and Section 5.10 (iv).

### 5. The calibration anchor has no sampling uncertainty, is concentrated in six firms, and its E1-to-E2 "change" is noise [Major]

Location: Section 7.3 "Anchor"; Table 11 row "2025 (anchor)"; Introduction ("the median top score of 2023-25 was at its durable level if all selling and marketing expense buys growth, and ... up to 39% of it was a transient growth surplus if none does"); Appendix E.2 last sentence.

Issue: The anchor is the 20 firm-years at or above the P95 of the 2023-25 E2 cash score. They belong to 12 firms; Clear Secure and Duolingo contribute three firm-years each, Palantir, monday.com, Global-E and Cellebrite two each (14 of 20 from six firms). The firm-year with the largest score (Exzeo 2025, R = 106) reports no selling and marketing expense and is treated as having none, so it has the largest upper-bound intercept (45) and surplus (49). No interval is reported for any anchor quartile, yet the text draws a sign conclusion from a median of -0.8 points and Appendix E.2 records a conclusion that "changed" when the median moved from +7 (E1) to -1 (E2).

Evidence (chk7.py, firm-cluster bootstrap over the 2023-25 E2 sample, 1000 replicates, cut-off and G recomputed in each draw): median Pi_ub -0.7, se 10.0, 90% [-15.6, +16.3]; transient share at the upper bound -1% [-35%, +29%]; share of anchor firm-years with Pi_ub > 0: 45% [21%, 75%]; median m0_ub 43 [34, 52]; median Pi_lb 20 [11, 27]. Leave-one-firm-out moves the median Pi_ub between -7.3 (dropping Duolingo or Clear Secure) and +3.0. Cut-off sensitivity: at P97.5 (10 firm-years) median Pi_ub is +17 (28% transient); at P92.5 it is -9; at P90 it is -10.

Required change: Report firm-cluster intervals for the anchor quartiles and for the transient shares in Table 11 and in the text; state the number of distinct firms; treat Exzeo's missing S&M as missing (drop or impute) rather than zero; remove the sign claims ("was at its durable level", "only 45% ... scored above it") or state them with the interval; rewrite the Appendix E.2 sentence to say the two anchors are statistically indistinguishable. Since the horizon ranges of Table 11 inherit the anchor's quartiles, say that their lower and upper ends carry at least +/- 9 points of sampling error from the anchor alone.

### 6. The post hoc choice of E2 and the construction of the pro forma rule are not disclosed where the reader meets them, and "organic frontier" overstates what E2 is [Major, transparency]

Location: Section 4.4; Table 2; Appendix E.2 "Choice of estimand"; `notes/estimand_notes.md` Section 1.

Issue: (a) The notes record, and Appendix E.2 states, that the primary sample for the model-facing results was changed to E2 after the exclusion-only robustness row (-0.56 / -0.43 slopes; -11.4 / -12.4 P95 changes) was known. Section 4.4 presents the two estimands as designed, with no cross-reference. (b) The notes also record that the pro forma ambiguity rule (exclude 26 firm-years whose additive and cumulative readings differ by more than one point) was added after a first test run whose E2 point estimates had been seen. The paper does not mention this. (c) E2 drops 410 of the 469 acquisition-affected firm-years and adjusts 59 (5 of the 46 flagged fast growers); its headline statistics differ from the exclusion-only 25% column by at most 0.03 in the slopes and by at most one point elsewhere. E2 is therefore a renamed robustness sample, not a frontier net of acquired growth. (d) The dropped firm-years are selected on the outcome: flagged firm-years have reported growth 10 points higher and scores 9 to 10 points higher than unflagged ones; acquirers' unflagged years have GAAP margins 11.5 points higher and growth 4.5 points lower than never-acquirers (`estimand_notes.md` Section 5). None of this is in the paper, and the effect on period comparisons is non-trivial: E2 retains 78% of 2010-15 and 79% of 2016-19 firm-years but 87% of 2023-25, and 34 of 57 (2010-15) and 56 of 80 (2016-19) fast growers against 12 of 18 in 2023-25.

Evidence: `estimand_notes.md` lines 8 to 39; Table 2 columns "E2" against "25%"; `empirics_organic.json` samples block; chk2.py yearly counts.

Required change: In Section 4.4 say in one sentence that E2 was adopted after the exclusion-only robustness results were known and point to Appendix E.2; disclose the test run and the rule added after it; call E2 what it is ("firm-years not affected by material acquisitions, with 59 firm-years adjusted by pro forma disclosure"); add a short selection paragraph with the diagnostics above and their implication (E2 is not the counterfactual organic behavior of acquirers; the slope on E2 is steeper partly because acquirers' high-margin, low-growth years stay in while their high-growth years leave).

### 7. Time variation: show the yearly series; 2025 does not fit the "since 2023" narrative [Moderate]

Location: Section 5.2 and Table 4 (period aggregates); Section 5.3 (period slopes); Figure 3 (shows yearly medians, P90 and P99 but not the P95 the text uses, and no slopes).

Evidence (chk2.py):
- Yearly P95 of the GAAP score, E1: 2016-19 62.8, 51.1, 55.6, 54.0; 2020-22 59.2, 56.2, 50.4; 2023 42.8; 2024 41.5; 2025 54.6. Cash basis 2025: 50.5. On E2 2025 is 46.6 (GAAP) and 44.1 (cash). The 2023-25 average of 44 is a 2023-24 phenomenon; the latest year is back near the 2016-19 level on E1 GAAP.
- Yearly tau = 0.90 slopes (E1 GAAP): 2010-16 between +0.19 and -0.55; 2017-24 between -0.56 and -1.07; 2025 +0.11 (E2: +0.08). The "steeper after 2020" period slope pools 2020 (-1.07), 2023 (-0.83) and 2024 (-1.03) with a 2025 cross-section that shows no trade-off at all.
- Leave-one-year-out change in P95 (2016-19 to 2023-25): E1 GAAP between -10.5 and -14.0, cash -13.1 to -17.8; E2 GAAP -7.4 (dropping 2018) to -12.9. Alternative windows (2017-19, 2016-18, 2024-25, 2023-24) give -10.8 to -17.8. The decline is robust.
- A quantile regression with year effects gives slopes of -0.54 (E1 GAAP), -0.35 (E1 cash), -0.66 (E2 GAAP), -0.41 (E2 cash): the pooled slope is not an artifact of between-year shifts.
- Reweighting (chk9.py): holding the 2016-19 growth-bin distribution fixed, the 2023-25 P95 would be 61 (E1 GAAP) and 63 (E1 cash) against observed 56 and 60 in 2016-19; reweighting 2016-19 to the 2023-25 mix gives 48 and 49 against observed 44 and 45. The decline is entirely compositional, which is the paper's claim; this is a cleaner demonstration than the T(g0) argument and should be reported.

Required change: Add a panel or table with the yearly P95 (both bases, E1 and E2) and the yearly slopes; mention 2025 explicitly and either explain it (a fiscal-2025 effect of AI demand, or noise with n = 145) or soften "since 2023". Report the reweighting decomposition. Keep the period contrasts.

### 8. Inference details not stated: interval type, replication counts, non-convergence [Minor]

Location: Table 2 notes, Section 5.1, Tables 4 to 8.

Evidence: Percentile intervals throughout; replications are 500 (period changes), 300 (levels), 200 (slopes, scale), 400 (capital split), 999 (gap decomposition), stated only for Table 4. Bootstrap quantile-regression fits are capped at 2,000 iterations and the cap is hit in some replicates (IterationLimitWarning), which adds noise to the slope standard errors.

Required change: State "percentile intervals" and the replication count for each statistic; raise the iteration cap or record the share of non-converged replicates.

### 9. The linear upper-decile slope averages a kinked frontier; state the window and quantile dependence [Minor]

Location: Section 5.3, Table 6, abstract ("about half a point").

Evidence: Band values in Table 6 fall from 27 to 19 between the 10-20 and 20-30 bands (about -0.8 per point of growth) and from 17 to 13 between 30-40 and 40-60 (about -0.27), then flatten. chk1.py: E2 GAAP slope by window at tau = 0.90 is -0.77 ([0, 0.4]), -0.59 ([0, 0.6]), -0.53 ([0, 0.8]), -0.38 ([0, 1.0]); by tau in [0, 0.6]: -0.55 (0.75), -0.55 (0.80), -0.63 (0.85), -0.59 (0.90), -0.63 (0.95). E2 cash: -0.26 to -0.55. The qualitative claim ("well under a point") holds everywhere; the specific -0.59 does not.

Required change: Report the slope for two or three windows and quantiles in Table 14, and say that the trade-off is concentrated between 10% and 30% growth.

### 10. The growth-spend elasticity regression is alluded to but not reported, and its within-firm estimate supports the paper's reading [Minor]

Location: Section 5.4 ("Slopes below one, such as those we obtain ..."); `empirics_results.json` alpha_est.

Evidence: log excess growth on log lagged S&M share, firm-years with g > G_t, unflagged: pooled with year effects 0.39 (se 0.14); with firm and year effects 1.09 (se 0.35), n = 617. The within-firm slope is one, which under the paper's own argument says variation is in opportunity, not in the weight; the pooled slope below one is the cross-firm mix. Reporting both would strengthen the identification discussion rather than weaken it.

Required change: Report both estimates with the sentence.

### 11. Smaller code and presentation points [Minor]

- `tab_robust.tex` "one observation per firm and period" averages all firm-years (including negative growth) before restricting to [0, 0.6]; the `firm_means` entry in `empirics_revised.json` averages non-negative-growth years only and gives -0.63 / -0.35 instead of -0.60 / -0.43. The text cites the table, so there is no error, but the cash slope's sensitivity to this choice is worth a word.
- The following-year acquisition flag uses `groupby(cik).shift(1)` without checking that the previous row is the previous fiscal year (build_panel_v2.py line 159); a gap year propagates the flag to a non-adjacent year. Probably rare; check.
- `proforma_gap` comes from a later filing for 64 core firm-years and is the sole basis for 16 acquisition-year flags (`estimand_notes.md` Section 3.7), a small departure from the as-first-reported principle that should be footnoted.
- The stochastic-frontier shortfalls (Section 5.7) carry no standard errors; the cohort comparison is descriptive and should be labeled so.
- Section 5.1 cites Aragon et al. for the conditional quantile frontier; the object used (quantile of m among firm-years with g >= g0) is the output-oriented order-alpha frontier in the two-output, no-input case, which is fine, but the sentence "the firm-cluster bootstrap is also not valid for such an extreme statistic" applies with equal force to T(40%) at n = 12 to 18 (Finding 3).

## Checks run

1. Rebuilt E1, E2 and the 25% exclusion-only frames from `estimate_organic.py` (no bootstrap) and reproduced the four pooled slopes to four decimals (-0.4592, -0.3662, -0.5851, -0.4316).
2. Slope sensitivity: tau in {0.75, 0.80, 0.85, 0.90, 0.95} by window in {[0, 0.4], [0, 0.6], [0, 0.8], [0, 1.0], [-0.1, 0.6], [0.05, 0.6]}, E1 and E2, both bases (chk1.py).
3. Yearly P95, P90, median growth, fast-grower counts and yearly tau = 0.90 slopes, 2010-2025, E1 and E2; leave-one-year-out and alternative period windows for the P95 change; leave-one-year-out for the pooled slopes and the E1 minus E2 difference (chk2.py).
4. Paired firm-cluster bootstrap for slope (pooled and 2010-19), scale gradient, capital split and P95 change contrasts, with percentile, basic and normal 90% intervals, skewness and two-sided p-values (chk3.py).
5. Quantile regression with year effects; bootstrap test of the 2010-19 to 2020-25 slope change (chk4.py).
6. Capital-intensity gap under contemporaneous, lagged, lead and firm-median sorts, for GAAP, cash after SBC, cash before SBC and operating-cash-flow scores, and for the cash score with capital spending added back (chk5.py).
7. Spend ratio by tercile of excess growth, by minimum excess growth, by benchmark G, ratio of medians, median regression and least squares through the origin (chk6.py).
8. Anchor: firm-cluster bootstrap of cut-off, G and all quartiles (1000 draws), leave-one-firm-out, Exzeo excluded, cut-off at P90 to P97.5 (chk7.py).
9. T(40%) bootstrap: count of NaN replicates and of replicates with fewer than 15 fast growers; order statistics behind the P95 (chk8.py).
10. Reweighting of the 2023-25 growth-bin distribution to 2016-19 and the reverse, for the P95 of both scores (chk9.py).
11. Multiplicity: tabulated all 32 paired contrasts from `empirics_organic.json`, normal p-values and a Holm correction at familywise 10%.
12. Read-through of `estimate_revised.py`, `estimate_organic.py` (sections 1 to 9), `estimate_frontier.py` (within-firm and elasticity blocks), `paper_stats.py`, flag lines of `build_panel_v2.py`; compared every standard error, interval and count quoted in Sections 4, 5 and 7.3 and Tables 2 to 8 with the JSON outputs.

## What I found correct

- Every standard error, interval, count and point estimate quoted in the text and in Tables 2 to 8 and 14 matches the code output (E1 slopes 0.137 / 0.112; E2 0.158 / 0.115; scale -2.5 (1.2), 5.7 (2.8), +0.7 (1.3), E2 -2.7 (3.4), +3.4 (2.6); capital split 38 vs 53 [-22, -3], E2 37 vs 48 [-20, -3]; P95 changes -12 [-21, -7], -15 [-27, -5]; leave-one-firm-out ranges; fixed-effects +0.08 (0.07), -0.02 (0.04), pooled -0.21, -0.24; anchor n = 20, cut-off 44, G 12.0, 7 above the P95 margin, quartiles 36-52, 47-63, -17 to 16, 12 to 28, transient -2% to 39%; sample counts 1,929 / 293, 1,516 / 283, 59 adjusted, 24% flagged, 37% of fast growers flagged). The paper's E1 - E2 standard errors are the paired draws, as stated.
- The paired bootstrap is correctly paired (firms drawn from E1, both estimands evaluated on the same firms' rows; `boot_pair`), and the period-change bootstraps resample firms across both periods, preserving within-firm dependence.
- The pro forma organic-growth formula is correct under the additive (ASC 805) reading, the carry-over treatment in the following year is consistent with flagging t + 1, and the validity, repeat and ambiguity rules are sensible given what companyfacts exposes.
- The headline descriptive results are robust: the P95 decline survives every leave-one-year-out and alternative window; the upper-tail slope is negative under every tau, window and interval type; the year-effects slope confirms it is a within-year cross-sectional pattern; the reweighting confirms the compositional reading.
- The use of upper quantiles and fixed-threshold frontier points instead of the edge maximum, the disclosure of the edge statistic's cell-size dependence (Table 15), the explicit statement that the cross-section does not identify any firm's trade-off (Proposition 7), and the rejection of the log-log spend regression as an estimator of alpha are all sound.
- The as-first-reported panel construction, the retention of inactive registrants, and the pro forma adjustment applied only to flagged firm-years (so that unaffected growth never changes; asserted in code) are well designed.
- Appendix E.2 does disclose the post hoc choice of E2 and the conclusions that moved; the issue in Finding 6 is placement, completeness and labeling, not concealment.
