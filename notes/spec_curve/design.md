# Specification curve of the empirical headline claims: pre-specification

Written 2026-11-03 14:36 UTC, before any estimate of this analysis was computed. Nothing below was changed after the
first run of `code/spec_curve.py`; corrections found later are recorded in `notes/spec_curve/log.md` with their time,
not edited in here.

Method: specification curve / multiverse analysis (Simonsohn, Simmons and Nelson 2020, Nature Human Behaviour 4:1208-14;
Steegen, Tuerlinckx, Gelman and Vanpaemel 2016, Perspectives on Psychological Science 11:702-12). The paper already moves
many analysis choices one at a time (Table tab:robust, Table tab:grid_v3, E1/E2 and the imputation bounds, R1-R5). This
analysis moves them together, over the options the paper itself uses, reports or names as defensible, and asks of each
headline empirical claim in how many of the resulting specifications it holds. Supplement S9 does the same for the
calibrated claims only; nothing here re-tests those.

## 1. Claims, quantities and tests

Units: points (0.01 of revenue = 1 point) for score changes and the anchor; margin per unit of growth for slopes.
"Baseline" is the specification the paper prints. Every test is on the point estimate of the specification unless
stated otherwise.

| Id | Claim as the paper states it (source) | Quantity | Claim holds if |
|---|---|---|---|
| C1 | "Between 2016--19 and 2023--25 the 95th percentile of the GAAP score fell from 55.9 to 43.9, by 11.9 points" (sections/empirics.tex:20; abstract; intro "fell in every sample variant") | change in the upper quantile of R_op, late period minus 2016-19 | change < 0 |
| C2 | The same after SBC: "from 57.3 to 44.6, by 12.7 points" (empirics.tex:20) | change in the upper quantile of the cash score | change < 0 |
| C3a | Psi_0.90 GAAP slope is "far above -1, the one-for-one trade that the Rule-of-40 line describes" (empirics.tex:29) | slope of the partial frontier over growth | slope > -1 |
| C3b | "That it is negative holds in sign in all four views" (empirics.tex:29) | same | slope < 0 |
| C3c | "a point of growth has come with well under a point less margin, about a fifth of a point in the baseline" (empirics.tex:29). Operationalised here, not by the paper, as "well under a point": | same | slope > -0.5 |
| C4a-c | The same three statements on the cash basis (empirics.tex:29) | slope, FCF margin after SBC | as C3a-c |
| C5 | "The GAAP frontier steepened after 2020" (empirics.tex:31; abstract quotes -0.60 in 2020-25) | late-period slope minus early-period slope, GAAP | difference < 0 |
| C6 | "After SBC there was no steepening: the difference is -0.19 under E1 and positive in the other three views" (empirics.tex:31) | same, cash basis | see below |
| C7 | The spend ratio "is robust across the four views, at 3.0 to 3.5" (empirics.tex:36) | median S&M share (previous year) over growth in excess of the year median, firm-years above the median | 2.95 <= ratio < 3.55 (3.0 to 3.5 at one decimal) |
| C8a | Calibration anchor: "Only the statement in which no selling spend buys growth is a conclusion: if selling spend does not buy growth, the best scores of 2023--25 exceed their durable level" (empirics.tex:52) | median growth surplus Pi_lb of the anchor firm-years | median Pi_lb > 0 |
| C8b | Netted (central) basis: "above zero in all four views" (empirics.tex:52) | median Pi_net | median Pi_net > 0 |
| (C8c) | Pi_ub, all S&M buys growth: the paper makes no sign claim ("includes zero") | median Pi_ub | descriptive only |

C6 is a claim of absence. Its baseline point estimate is itself negative, so a point-estimate sign test cannot test it.
Reported: (i) the share of specifications in which the cash difference is negative in sign ("steepened in sign"; the
baseline is one of them); (ii) on the bootstrapped subset (Section 5), the claim holds if the 90% percentile interval of
the difference does not lie entirely below zero. The C6 "share holding" in the table is (ii).

Definitions are the paper's, reused from its code (code/estimate_v3.py, executed, not re-implemented): P95 via
`np.quantile` on the period's finite scores (`f_top`); Psi_chi via `cone_mat` and `wslope` (grid g0 = 0, 0.05, ...,
window end; a grid point needs 30 firm-years in the sample, 10 in a bootstrap draw); the period slopes on their own
period's firm-years (`f_cone`); spend ratio via `spend_ratio` / `f_spend`; the anchor via `anchor_vec` (2023-25, at or
above the cut-off quantile of the cash score; Pi_lb = R - (m + k_g + (1 - k) G), Pi_net nets the maintenance level of
S&M, tau = 0.18).

## 2. Analysis choices and their options

Options are only those the paper uses, reports or names as defensible. Source in brackets. First option = baseline.

### 2.1 Sample (shared by all claims): 15 x 2 x 3 x 2 x 2 x 2 = 720 samples

| Choice | Options | Source |
|---|---|---|
| A. Treatment of acquired growth (15 levels, four families) | observed growth (E1); pro forma organic growth at the 25%, 10% and 50% flag, each with ambiguous pro forma cases excluded (the paper's rule), read additively or read cumulatively (9 levels; E2 is 25%/excluded); exclusion of acquisition-affected years at the 10%, 25% and 50% flag (3); imputation bounds at M = 4 and 8 (2) | data.tex:37-40; empirics.tex:55; Table tab:robust; code/estimate_organic.py (gadd/gmax/gorg for each flag) |
| B. Rule R1 sensitivity | fiscal-2010 years first reported only later: excluded / added back | data.tex:13; tab:robust |
| C. Rule R2 sensitivity | no firm dropped / the 4 firms the classifier classes not software / all 16 named firms | data.tex:14; tab:robust |
| D. Rule R5 sensitivity | firm-years flagged as without listed equity kept / dropped | data.tex:17; tab:robust |
| E. Debt-only filers named by a referee | kept / dropped | tab:robust |
| F. Growth upper bound | the sample bound (g < 500%) / g <= 150%, the bound the paper uses for fixed-effects regressions, the stochastic frontier and a size-gradient sensitivity | appendix_data.tex:24; estimate_v3.py SCALE_SPECS |

Crossing the pro forma reading with the 10% and 50% flags, and crossing the sample-rule sensitivities with each other and
with every acquisition treatment, combines options the paper uses separately; no new option is introduced. The
imputation bounds are defined at the 25% flag only, as in the paper.

### 2.2 Claim-specific choices

| Claims | Choice | Options | Source |
|---|---|---|---|
| C1, C2 | upper quantile | 0.95 / 0.90 | empirics.tex:20; Change in P90 row of tab:estimands_v3 and tab:contrasts_v3 |
| C1, C2 | late period | 2023-25 / 2023-24 / 2025 | empirics.tex:20 (TopTwentyFour, TopTwentyFive) |
| C2, C4, C6 | cash measure | FCF after SBC / before interest paid and cash taxes / before interest paid, after tax | data.tex:44; Table tab:bridge_v3 |
| C3-C6 | frontier estimator | Psi_0.90 / Psi_0.80 / Psi_0.85 / Psi_0.95 / order-m (m = 25) | empirics.tex:11, 27; tab:grid_v3 |
| C3, C4 | growth window | 0-60% / 0-40% | tab:grid_v3 |
| C5, C6 | growth window | 0-40% / 0-60% | empirics.tex:31; estimate_v3.py PERW |
| C5, C6 | period split | 2010-19 vs 2020-25 / 2010-15 vs 2018-25 | empirics.tex:31; notes/inference_v3.md "Slope regimes" (referee 3, finding 14) |
| C8 | cut-off quantile of the anchor | 0.95 / 0.90 / 0.925 / 0.975 | estimate_v3.py ANCH_CUT; calibration_anchor_v3.json cutoff_sensitivity |
| C8 | acquisition-affected years in the tail (observed-growth samples only) | dropped (calibration rule) / kept (E1all) | estimate_v3.py E1all |
| C7 (secondary only) | benchmark growth G | year median / 5% / 8% / 12% | empirics.tex:38 |

The spend ratio's measurement (benchmark G, terciles, floors, netting) is not a dimension of C7's primary curve: the
paper states that the ratio is robust across samples and, separately, that the product alpha(X - k) depends on how
excess growth and spend are measured (empirics.tex:38). The benchmark is reported as a secondary curve.

### 2.3 Grid sizes (before removing invalid combinations)

| Claim | Specifications |
|---|---|
| C1 | 720 x 2 x 3 = 4,320 |
| C2 | 720 x 2 x 3 x 3 = 12,960 |
| C3 | 720 x 5 x 2 = 7,200 |
| C4 | 720 x 5 x 2 x 3 = 21,600 |
| C5 | 720 x 5 x 2 x 2 = 14,400 |
| C6 | 720 x 5 x 2 x 2 x 3 = 43,200 |
| C7 | 720 (secondary: 2,880) |
| C8 | 48 observed-growth samples x 4 x 2 + 672 other samples x 4 = 3,072 |

The full grid is computed (point estimates; no sampling). Expected runtime is a few minutes.

## 3. Invalid combinations and why

- Psi slope (C3, C4) where any grid point of the window has fewer than 30 firm-years in the sample: not defined (the
  paper's rule, estimate_v3.py `cone_mat`). Counted as invalid, not as failing.
- Period slopes (C5, C6): the same rule within each period; the 0-60% window within periods is expected to be undefined
  in most samples (the paper's reason for using 0-40%).
- Anchor tail rule (C8): "drop acquisition-affected years" applies only to observed-growth samples; samples with
  organic or imputed growth keep those years (their growth is adjusted; calibration rule), and exclusion samples have
  none. Only the paper's rule is run for them.
- Pro forma reading applies only to the pro forma family; M only to the imputation family; the flag only to the pro
  forma and exclusion families.
- Bridge cash measures are missing where a firm-year reports none of the interest and tax elements (as in the paper).
- The anchor uses the paper's cash basis only (its surplus is defined on it by the calibration); no bridge measure.
- A specification whose quantity is undefined (NaN) for any other reason is counted as invalid and reported.

Considered and not included: the local conditional quantile (the paper calls it a different, descriptive object);
the adjusted and pre-SBC FCF bases (claims are stated per basis; other bases are descriptive); the first test run's
E2 rule (superseded by the ambiguity and repeat rules for a stated reason, and a near-duplicate of the additive reading);
panel-construction choices (fiscal-year convention, first-reported vintage, the $100 million threshold, the margin
bounds), for which the paper names no alternative and which would need a rebuilt panel; the minimum cell of 30 and the
grid step; tau = 0.18 in the anchor (a calibration input covered by S9); interval types (inference, not estimation).

## 4. Summary reported per claim

- specifications run (valid) and invalid;
- share of valid specifications in which the claim holds (unweighted; every valid specification counts once);
- median, minimum and maximum of the quantity, its baseline value, and the 5th and 95th percentiles;
- the most influential choice: the choice whose levels' medians of the quantity differ most (range of the per-level
  medians, in the quantity's units); also, per choice, the share holding at each level and the share of the variance of
  the quantity explained by that choice alone (eta squared);
- the share holding by acquisition family, because the unweighted share gives the pro forma family 9 of 15
  acquisition levels.

No permutation test under the null (Simonsohn et al.'s joint inference) is run: the claims are descriptive statements
about the realized sample, and the paper's own inference is the firm-cluster bootstrap.

## 5. Bootstrap on a subset (secondary)

Firm-cluster bootstrap with B = 199 replications: firms drawn with replacement from the 292 firms of E1, each
specification evaluated on its own firm-years of the drawn firms (the paper's design), the same draws for every
specification. Seed: 20261030 + crc32('spec_curve') mod 1e6 (the paper's rule). Inside a draw a grid point needs 10
firm-years (the paper's rule); a specification with more than 5% undefined draws gets no interval. Interval: 90%
percentile. Claim holds with its interval if the interval lies on the claimed side (C1, C2, C3b, C4b, C5: below zero;
C3a, C4a: above -1; C8a, C8b: above zero; C6: not entirely below zero).

Subset: the 22 samples of Table tab:robust that lie in the grid, plus a seeded uniform random sample of the other
samples, K samples in all, with K the largest number for which the measured cost keeps the bootstrap under 15 minutes
of wall time on 2 worker processes (at least 48). All claim-specific specifications of a sampled sample are
bootstrapped. Shares from the subset are estimates of the full-grid share.

## 6. Reviewer variants

- Forward pairing (reviewer GLM-M9). F1: R_t = g_{t+1} + m_t, the same firm's next consecutive fiscal year in the same
  sample (growth of the same estimand), indexed by the margin year t, the timing of the model and of the paper's lead
  regressions (empirics.tex:33). Under F1 the late period 2023-25 contains only 2023-24 margins, since fiscal 2026 growth
  does not exist. Sensitivity F1': the same pairs indexed by the growth year t+1. F2, the literal wording of the request
  ("growth of year t paired with the margin of year t+1"): R_t = g_t + m_{t+1}, indexed by t. Computed for C1-C6 on the
  baseline and the four views; F1 also over the full C1-C6 grid as a second curve, reported separately and not mixed into
  the shares of Section 4.
- Leave one firm out (reviewer GPT-16). Under E1 (and E2 and the imputation bounds), drop each firm in turn and recompute
  C1-C5 at the baseline specification, phi_0.90 at 60% growth and the 60% cell; report the range, the firm whose removal
  moves each quantity most and whether any removal reverses a sign. The anchor's existing leave-one-firm range is
  reproduced as a check, and extended to dropping every firm (not only the anchor's own).

## 7. Reproduction check (before any result is used)

The specifications that coincide with the 22 published variants (E1, E2, E2pf10/50, E2x10/25/50, E2add/max, E2imp4/8,
E1/E2 k2010, clean, r2named, nolist, nodebt) must reproduce `notes/empirics_v3.json` to 1e-12 for every statistic of
Section 1 that the JSON stores (P95 and P90 changes; Psi slopes for every chi and window and order-m; the period
differences for both splits; the spend ratio and its constant-G versions; the anchor's Pi medians, including the
cut-off sensitivity; the bridge P95 changes; the 2023-24 and 2025 P95 changes), and the printed macros of
paper1/macros.tex after rounding. The script stops if any check fails.

## 8. Outputs

`notes/spec_curve/results.json`, `notes/spec_curve/specs.csv` (every specification), `notes/spec_curve/log.md`,
`paper1/spec_macros.tex` (`\Sc...` macros), `sections/tables/tab_spec_curve.tex`, `figures/fig_spec_curve.pdf`
(two-panel specification curves for C1 and C3, the two claims the abstract states with GAAP numbers),
`sections/supp_spec_curve.tex` (draft section).

## 9. What this analysis is not

It varies analysis choices on fixed data; it says nothing about sampling or measurement error beyond the bootstrap
subset. Specifications share most of their firm-years, so they are not independent replications, and a share of
specifications is not a probability. It does not test any causal reading.
