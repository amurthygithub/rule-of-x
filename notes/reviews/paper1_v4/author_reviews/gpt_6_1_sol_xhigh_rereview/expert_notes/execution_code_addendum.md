# Execution/stress code inspection addendum

Pinned source inspected: commit `eb7537bee7585f2902304f62a722edea6ced8539`, copied under `pinned_snapshot/`. The baseline was not modified. No `notes/reviews/` material or restricted other-review responses were read. This addendum follows the independent PDF assessment and adds code anchors; it does not claim a million-draw run or full author-pipeline reproduction.

## Findings updated by source inspection

1. **S12.2 price/revenue identity is confirmed by code.** `code/biz_open_questions.py:51–61` computes the rival-dependent price, then sets `G = rivals[h]['G']` and `R = m0 + G`. The automating comparison at lines68–78 likewise uses the original growth term with a changed output price. The generated table note in `code/supp_extensions.py:178` says both volume and growth are held as in the paper path. There is no price-growth adjustment or compensating quantity path in these formulas. The necessary repair remains: specify a constant-revenue-growth margin counterfactual with quantity adjustment, or retain quantity paths and compute revenue growth from `S=pQ`. The gap ranking may remain because a common growth correction can cancel. The new section's score levels need reconciliation.

2. **The LHS confidence objection is confirmed by the actual design and formatter.** `code/mc_claims.py:1396–1400` generates randomized LHS by independently permuting strata and adding uniform jitter for every coordinate. This is not a collection of iid vector draws. `code/mc_report_tex.py:220–225` nonetheless computes `sqrt(p(1-p)/N)` and claims this overstates LHS error. Lines226–236 use ranks `Nq ± 1.96 sqrt(Nq(1-q))` for the percentile confidence bands. Those iid-normal/binomial rank approximations do not acquire distribution-free95% coverage merely because the draws are LHS. The exact two-point counterexample in our `scripts/execution_checks.py` applies directly to the design class in this code.

3. **Sobol estimates use an appropriate common point-estimation structure, but their stated confidence coverage also deserves approximation language.** `code/mc_claims.py:1415–1427` uses a scrambled Sobol sequence when SciPy is available, with pseudo-random fallback. Lines1850–1862 split the base into A/B matrices and replace factors/groups; `sobol_indices` at1543–1557 computes Saltelli first-order and Jansen total-order estimates. Its bootstrap resamples base rows as though those rows form ordinary exchangeable empirical draws. Lines1891–1919 give200 bootstrap resamples, and SALib is used for factor estimates if installed. This is routine approximate sensitivity-analysis machinery, but resampling rows of one randomized QMC design is not a proof of95% randomization coverage. Recommend repeated independent scrambles/design replications if precise numerical CIs are meant as guaranteed accuracy. This extension does not negate the central point estimates or prove they change materially.

4. **Completion-label repair is incomplete in source as well as PDF.** `code/mc_claims.py:145–159` sets the embedded share to `min(1, q*rho*Tpar*n)` and calculates `complete_year` when that upper bound reaches1. `code/calibrate_horizons.py:321–341` implements the same formula; comments at332–335 still call it the date the program is embedded in expectation. `code/mc_report_tex.py:80` (the P3b row in ROWS; nearby lines78–81) labels it “expected completion year”. The exact geometric-tail recurrence is a different object. Relabel the variable's interpretation, table row and S10 prose, or consistently report a chosen completion tolerance. No need to change the central pre-completion payback numbers solely to repair this name.

5. **S12.3's reported cancellation is genuine in this implementation's maintained setup.** `code/mc_claims.py:201–228` uses a daily time grid over200years, a piecewise linearly interpolated target gain, benefits proportional to realized attempted mass, and in-flight costs proportional to attempt rate; cash payback is the first nonnegative cumulative sum after it has been negative. `code/supp_extensions.py:184–222` forms the6×6 median matrix, rank correlations and textual gates from four CSV columns. Lines224–248 execute the unchanged calibration in a shadow tree and sweep18 capacity values, holding the remaining central inputs fixed, to check exactly constant payback to1e-9years. The structure supports cancellation before the program-completion cap binds. It does not justify a general claim for fixed startup costs, heterogeneous process sequencing or endogenous capacity costs; the paper's current “in the model” framing is the appropriate scope.

6. **S10 makes its anchor-law and independence choices fairly explicit in code.** Lines617–626 draw the upper-bound surplus independently of the intercept (calling this conservative in a code note); lines635–645 map intercept and maintenance-base dimensions through their separate bootstrap marginal quantiles. `dim_value`, lines695–706, maps unit draws to the5th–95th percentile interval. `assemble`, lines750–756, draws market growth separately over its stated range. These are a scenario box with marginal bootstrap ingredients, not a joint empirical forecast distribution. The larger PDF interval is correctly described as a scenario-law result; do not call it an empirical joint confidence/prediction interval. Separately drawing a surplus and intercept is not guaranteed conservative for every output, so that code comment should be read as a design intention, not a proved variance ordering.

## Exact regeneration of the missing per-draw CSV

The committed first-run JSON header records these author arguments:

```
--n 1000000 --seed 20261102 --workers 11 --chunk 200
--corners 100000 --sobol-n 65536 --amin-n 100000
--search-budget 6000 --cc-mode path --anchor-range ci90
```

The second seed is20261104. `--corners100000` produces100002corner points in51dimensions because all-low and all-high are added (`mc_claims.py:1403–1412`). The first-run configuration hash in the stored header is`e291b0637f62`; a local regenerated bootstrap or changed numerical environment may change the snapshot/config hash and must be disclosed rather than silently called identical.

The unmodified author CLI writes plain `draws_lhs.csv`, not `.gz` (`mc_claims.py:2487,2491–2525`). `--stop-after draws` returns immediately after the draw/checkpoint phase, before CSV export (`main`, lines2934–2937). Thus this flag alone does **not** reconstruct the missing file consumed by `supp_extensions.py:184`.

For exact per-draw export without unnecessary searches and Sobol analyses, the helper supplied as our `scripts/export_author_mc_draws.py` uses the author's unchanged `Runner` methods: `setup`, `start_pool`, `run_draws`, `write_draws_csv`, then `stop_pool`. It sets the same design parameters, uses/resumes the author's checkpoints, and gzips the resulting CSV afterwards. All writes are directed outside the source baseline. It has not itself been run on the million-draw case merely by being included here. Suggested invocation, substituting the root's reproduction-copy path and a new output folder:

```
python3 -B scripts/export_author_mc_draws.py --repo REPRODUCTION_COPY --out NEW_MC_OUTPUT --workers 11
```

The CSV content can be compared independently of gzip metadata; the helper uses mtime 0 in gzip, which can change compressed SHA256 even when decompressed CSV bytes match. To run `supp_extensions.py` unchanged, its expected four-column input must be present at the reproduction copy's `notes/mc_results_2026-11-03_1m/draws_lhs.csv.gz`; placing regenerated inputs there must be documented as regeneration, not mistaken for an originally supplied committed binary.

Only `kappa_abs`, `varpi`, `payback_years`, `R2036_net` are needed for the S12.3 table (`supp_extensions.py:184`). A specially reduced four-column algorithm can save work, but it would be a separate reimplementation and needs its own equivalence checks. The supplied wrapper instead preserves the author computation, including all strata and checks, so is slower but easier to interpret.

## Runtime caution and non-author artifact truncation

Read-only performance diagnostic:100calls of the unchanged `payback_v` at arbitrary plausible targets took0.252seconds in this runtime, about2.52milliseconds/call. Full `evaluate` (`mc_claims.py:796–874`) calls it9times per draw (3strata×full/fixed-price/central-execution variants). One million draws therefore imply approximately6.3CPU-hours from these calls alone, about35minutes at11fully utilized cores before other costs. The measurement is in `results/payback_performance.json`; it is not a scientific reproduction or a timing guarantee. The stored header's293.6second total omits a draws timing entry and may be a resumed-phase total; do not infer that a new full million-draw evaluation must finish in five minutes.

The locally fetched `notes/mc_results_2026-11-03_1m/mc_claims.json` was exactly360000bytes and cut off mid-JSON when first inspected. This is a likely transfer/output limit, not evidence the author's committed JSON is corrupt. It was reported to root for complete retrieval. Treat access gaps separately from scientific defects.

## Status

Code inspection strengthens EX-1, EX-2 and EX-3 of the PDF review and supports the conditional mechanism in S12.3. No new author-pipeline success or output equality is claimed in this addendum; root is conducting reproduction jobs independently. No restricted material has been read.
