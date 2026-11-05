# Empirical code addendum after the frozen fresh assessment

This addendum inspects the read-only snapshot at commit `eb7537bee7585f2902304f62a722edea6ced8539`. The independent assessment in `empirics.md` is unchanged. No restricted review folder or joint response was read. This reviewer did not run an author pipeline or mutate the snapshot. Own scripts below read committed processed inputs and outputs; raw SEC extraction and the committed bootstrap/specification grid are not independently reproduced here.

## 1. Valuation-ratio issue confirmed and localized

`code/biz_valuation.py:72–90` draws firm clusters and solves the year-effects OLS. At lines85–88 it records the signed ratio only for positive margin coefficients; every draw with a nonpositive denominator is replaced by positive infinity. Line90 then applies `np.quantile` to those values. This is a modified/censored bootstrap distribution, not the ordinary bootstrap distribution of the signed ratio. It also is not a Fieller confidence-set inversion.

The stored `notes/open_questions/valuation.json` confirms two numerical failures, at keys `cash.2010-19.weight_ci90[1]` and `gaap.top40.weight_ci90[1]`: both are **NaN**, not positive infinity. Their stored `weight_share_nonpositive` diagnostics are respectively 0.0610610611 and0.3643643644. NumPy's default interpolated quantile can yield NaN when both neighboring order statistics are infinite. `code/supp_extensions.py:123` prints any nonfinite upper endpoint as `\infty`, silently conflating this NaN with an intentionally unbounded interval. The resulting TableS20 is not a faithful presentation of a well-defined signed-ratio confidence set.

This is a confirmed code/method issue; it is narrower than a claim that the all-firm-year coefficient ratio or equal-weight test is wrong. The equal-coefficient test at `biz_valuation.py:101` does not use the ratio bootstrap. The all-year positive point ratios are reproduced below.

**Suggested fix:** define the ratio estimand and its parameter domain; publish denominator sign shares; use a documented weak-denominator confidence-set method, or label the positive-denominator censoring as a separate diagnostic instead of an ordinary ratio interval. Store nonfinite outcomes explicitly, distinguish undefined from unbounded, and make the table generator reject NaN rather than render it as infinity. Rebuild S12 table and text. A positive-parameter-domain restriction must be stated and justified, not silently imposed only within bootstrap draws.

## 2. Independent S12 point and covariance check

Own script `valuation_independent_check.py` independently:

- Reads `data/panel_v3.csv` and `data/v3_inputs/public_float.csv`.
- Matches float dates120–260 days after fiscal year end, nearest182days; obtains1,277 matches.
- Reimplements global1%/99% winsorization and all10 year-effects OLS regressions using NumPy, without importing the author's program.
- Reimplements the firm-cluster covariance sandwich with the usual finite-sample multiplier.

All10 coefficient pairs match the committed values within7.2×10⁻¹⁵ and all reported coefficient standard errors match within10⁻⁹. Thus the processed-data regressions and displayed main point estimates are independently corroborated. This check does not validate SEC source extraction, public-float coverage selection, the original bootstrap draws, or a causal/structural reading of the regression.

An asymptotic90% Wald–Fieller diagnostic, using the independently matched firm-cluster covariance and a normal critical value, gives:

| Row | Signed-ratio confidence-set diagnostic | Paper's printed interval |
|---|---|---|
| Cash, all firm-years | bounded[3.0097,13.7038] |[3.1,15.8] |
| GAAP, all firm-years | bounded[3.1293,7.6287] |[3.1,7.7] |
| Cash,2010–19 |(−∞,−118.0697] ∪[2.4992,+∞) |[2.5,+∞) |
| GAAP,score≥40 | all real numbers |[0.2,+∞) |

These diagnostics are asymptotic alternative confidence sets, not an exact finite-sample coverage claim or a numerical replacement mandated by this review. They show why the weak-denominator domain matters. Importantly, the all-year lower bounds still exceed2.8 under this independent diagnostic; therefore it would be wrong to claim the code issue overturns that particular descriptive interval comparison. That comparison still is not a structural validation of the paper's screening weight, because the empirical and theoretical estimands differ.

Reproduction files: `valuation_independent_check.py`, `valuation_independent_check.json`, `valuation_independent_check_run.txt`. No randomness was used. Initial attempts to use Statsmodels failed because it was unavailable in the default and primary runtimes; a direct NumPy implementation was used instead.

## 3. Interest-income contradiction resolved against stored outputs

`notes/empirics_v3.json` at `estimates.bridge_cash_bni_p95_change.E1` stores:

- estimate−0.1424248023;
- percentile90% interval[−0.3590228744,−0.0225171597];
- percentile95% interval[−0.3984532695,+0.0008118194].

The paired unadjusted-cash90% interval, `bridge_cash_bnis_p95_change.E1.ci90`, is[−0.2960176888,+0.0062836436]. Therefore the PDF's displayed90% interval is supported by the stored result and excludes zero; both95% intervals include zero. The simplest repair is to specify which level the caveat concerns. Main p41 and supplement p31 currently fail to distinguish them.

The underlying variable is before **net** interest: `estimate_v3.py:182` adds interest paid minus interest income, after tax, to the cash margin. Literal wording “remove interest income” is less exact than “remove net after-tax interest.” Macro extraction at `paper1_macros.py:1089–1093` uses the correct net-interest rows. Passing a hand-written claim gate is not semantic verification of every sentence: the currently inspected claim list checks other bridge statements (`paper1_macros.py:1435–1439`) but does not catch this interval-level mismatch.

## 4. Tail support and leave-one-firm-out

`spec_curve.py:790–820` genuinely removes every firm's rows within each of the four views, and recomputes P95,cone slopes,period differences,anchor and60% cell statistics. It stores sign reversals,undefined estimates,extreme firms and deletion ranges. This confirms that the new code implements the broad deletion exercise claimed by the response. Stored `notes/spec_curve/results.json` agrees with the stated minima: the E1GAAP60% cell64firm-years,min60after a deletion; E2GAAP37,min34.

The committed `notes/empirics_v3.json.cone_cells` records counts of firm-years, not unique firms. `estimate_v3.py:362–378` likewise enforces support by firm-year counts. Own direct counts on the processed E1 panel show reassuring support rather than a demonstrated small-cluster failure:

| E1 cell | Firm-years | Distinct firms | Largest firm's firm-years |
|---|---:|---:|---:|
| g≥60%,GAAP |64|41|4|
| g≥60%,cash |65|42|4|
| g≥40%,2010–19,GAAP |111|66|5|
| g≥40%,2020–25,GAAP |102|56|4|
| g≥40%,2023–25,GAAP |15|13|2|

These counts support framing GPT-16 as **reporting completeness**, not as evidence that E1 relies on only a few clusters. Unique firm counts for E2/consequential cells should still be published. No E2 reconstruction was attempted by this reviewer.

## 5. Residual inference wording is implemented as suspected

`spec_curve.py:457–458` defines the cash-steepening point test as nonnegative difference. `spec_curve.py:470–473` defines its bootstrap “success” as `not(hi<0)`, i.e. a90% interval not entirely below zero. This intentionally measures lack of detected steepening; it is not a test of non-steepening or equivalence. The prose should use that evidence description. Hence GPT-13's Table2 repair does not fully remove the broader wording issue identified in the frozen note.

## 6. R2 is applied as a partial classifier, as the detailed text says

`build_panel_v3.py:242–255` has three possible nonsoftware keyword categories: interactive entertainment,gambling and compute infrastructure. Its default is software; there are no categories for other nonsoftware businesses such as hardware,IT services or payments. Lines264–267 assert coverage of descriptions for every core registrant and map the keyword classes; lines310–312 apply the exclusion. Thus the coverage/application repair is real. It should not be mistaken for a validated principal-software classification. The independent-reader sensitivity at lines274–282 and420–433 is separate and transparent.

## Updates to response-audit recommendations

- GPT-M6: still partly resolved overall; code access now exists and the actual estimation runs belong in root's reproduction record.
- GPT-12: source code/committed outputs are consistent with the repaired sample-flow arithmetic; no new issue identified.
- GPT-13: partly resolved, because the no-directional-claim Table2 wording is correct but non-steepening language survives with a failure-to-detect criterion.
- GPT-14/15: disclosures remain resolved; this inspection does not independently rerun their bootstrap.
- GPT-16: substantial resolution of deletion sensitivity, narrow remaining reporting request; do not characterize the demonstrated E1tail support as only a few firms.
- GPT-34: access issue now resolved for this re-review, subject to root's execution record. The initial no-access statement in the frozen note documents sequence rather than a continuing blocker.

## Dependency and record cleanup

`code/REPLICATION_README.md:40–50,59–69,93–95` documents the relevant dependency order. Full raw-data reconstruction additionally needs `data/companyfacts_extract.json`,v2inputs and the filing-derived inputs; the third-party raw-data stages may be skipped only with committed downstream products retained. The10regression check above uses processed inputs and needs only NumPy andPandas. Some description strings remain stale after the addition ofS12: `biz_valuation.py:3` and REPLICATION_README p91call these analyses “not part ofPaper1,” while the README's line22correctly identifies the newS12. This is editorial record cleanup,not a numerical result.
