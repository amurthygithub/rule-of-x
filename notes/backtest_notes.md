# Backtest of the Part II model (spec Section 24.1): method, crosswalks and limits

Empirical-validation agent, 29 Oct 2026 (revised the same day after the coordinator's four follow-ups).

**Script and outputs.**
- Script: `code/validation/backtest.py`. Run `python3 -I code/validation/backtest.py`; it takes about 5 minutes, most of it the two review-ratio sweeps (occupations, then cells). It is single-threaded and seeded, so repeated runs give byte-identical outputs (checked).
- `notes/backtest_results.json`: every estimate, sample sizes, the sweep path, the multiple-testing family, the text macros, input sha256 hashes and the parameter values used.
- Seven tables in `part2/tables/`: `backtest_{occ,sweep,decomp,robust,cells,firm,tests}.tex`, all with `[tbp]` placement.
- `part2/tables/backtest_macros.tex`: every number quoted in the text, as `\newcommand` macros named `\bt...` (letters only).
- The text, `part2/validation_backtest.tex` (`\subsection`, `\label{sec:backtest}`). It `\input`s the macro file once, at its top, and the six tables, by paths relative to the paper root.
- The script reads only local files and writes nothing else.

**Important for the lead author.**
1. **Live parameters.** The script reads `data/tasks/params.yaml` and `engine/src/autofrontier/defaults.yaml` live. A rerun after either file changes regenerates every table and every number in the text.
2. **Prose to check on a rerun.** A few qualitative words in the prose are not generated and should be checked: "predicts and adds to exposure" in a paragraph title, "opposite sign" for the wage placebo, "below the controls alone" for the 0.8 case, and "probably because" for the firm exposure mix. Sentences whose truth depends on signs or significance are generated as macros: the firm sign sentence, the list of surviving tests, the placebo sentence and the sweep monotonicity clause.
3. **What remains typed.** The only digits left in the text are dates, column labels, the 5% test level and the name "50% horizon".
4. **The result is conditional on the review-time ratio** (`review.rho_rev`). It is reported as a sweep over its sourced range (Section 5b).
5. **Placement.** With seven floats and about four pages of text, the tables may drift into the following section. If they do, consider `\FloatBarrier` (package `placeins`) after `\input{part2/validation_backtest.tex}`.

## 0. Order of events (disclosure; times are file modification times, PDT, 29 Oct 2026)

1. **08:51 to 08:52.** The assumptions auditor finished `notes/assumptions_memo.md` and `notes/assumptions_register.md`. `08_params.py` rebuilt `data/tasks/params.yaml` (modified 08:52:18) with the new block `ai_cost.review_time_ratio_rho_rev` = 0.575 [0.37, 1.19]. Its sources are post-editing studies: Plitt and Masselot (2010); the review in Ahsan et al. (2021); Becker et al. (2025) for the upper end. The register (row 5) recommends that the engine's assumed `review.rho_rev` move from 0.8 to 0.575. Neither audit file mentions the backtest.
2. **After 08:52, before about 09:00.** The backtest's first run read the rebuilt `params.yaml`, but the engine defaults were not yet linked to the new block. It therefore used `rho_rev` = 0.8 and the old `e0`/`e1` of 0.20/0.01. Evidence: re-running today's code at 0.8 and 0.20/0.01 reproduces the first-run coefficient (-0.0131, SE 0.0104) only with the audited inference price of $1.27, not with the pre-audit $1.805. Result: the main score was null.
3. **About 09:00.** The engine defaults were linked to the audited values (`defaults.yaml` modified at 09:00:46): `rho_rev` 0.575, `e0`/`e1` 0.25/0.033. The next backtest run read them; the main score became significant. The change was detected because estimates differed between runs, and traced through the input hashes and parameter values in the JSON.
4. **After that.** The 0.8 case was kept as a reported variant. At the coordinator's request, the result is now reported as a sweep over the whole sourced range, with this order disclosed in the text. The coordinator records the episode in `notes/research_errors_log.md` (B1c).

The audit's value existed before any backtest estimate, so the change could not have been made in response to the backtest. At current values of the other parameters, the 0.8 case gives -0.009 (SE 0.010). With the old error rates it gave -0.013 (0.010). Both are null.

## 1. What is tested

1. **Occupation level, national, May 2021 to May 2025.** The model's automatable share at 2021 parameters is the main score. Exposure alone is the benchmark. The outcomes are the changes in log employment, log wage-bill share and log mean wage.
2. **Occupation by industry.** May 2021 against May 2025 cells (four-digit NAICS), with industry fixed effects and with occupation and industry fixed effects (Section 5e).
3. **Firm level, SEC software firms (SIC 7370-7374).** The firm's function-mix automatability is regressed on the change in cost-bucket shares of revenue, FY2021-22 to FY2024-25.

## 2. The score (what "2021 parameters" means)

An activity is (OEWS occupation o, O*NET 31.0 DWA j) with time share s_oj from `occ_activity.csv` (IM x F x RT weights). There are 17,444 rows and 783 occupations.

**Exposure.** beta_oj is the mean Eloundou et al. GPT-4 beta (E1 = 1, E2 = 0.5) over the occupation's own tasks linked to the DWA, joined by Task ID through `xw_task_dwa.csv`. This is occupation-specific for 99.4% of time; elsewhere the DWA mean `activities.exposure_llm` is used. The labels date from 2023 and rate O*NET 27.2 tasks. The benchmark is E_o = sum_j s_oj beta_oj, whose correlation with the published occupation-level beta is 0.99.

**Capability** (ass:ext-capability, prop:ext-feasible).
- H(t) = H0 2^((t - t0)/T_d), with H0 = 11.98 h at t0 = 2026-02-05 and T_d = 143 days (params.yaml `capability_path`).
- Mode A is feasible if H(t) >= d_j chi(0.8), with chi(0.8) = 2^(logit(0.8)/b) = 5.0 and b = 0.597.
- Physical DWAs (`activities.physical`) face H(t - L_W), with L_W = 5 years.
- The raw error is e = 1 - (1 - e_ctx)(1 - e_cap). Here e_cap = expit(b log2(d/H)) and e_ctx = e1 + (e0 - e1)(1 - iota) at readiness iota = 0.5. Readiness is not observed at the occupation level, so iota = 0.2 and 0.8 are run as variants.
- H(end-2021) = 0.0085 h (31 s), so **no DWA is feasible at end-2021 and the static score is identically zero** (JSON `scores.scenario_info.static`).
- The main score therefore uses the model's forward object. It averages over a half-monthly grid from 2022.0 to May 2025, along the capability and price paths. H(May 2025) = 3.25 h on this path; our refit of METR's runs gives about 2 h for the spring 2025 frontier, so the path runs ahead of the realized frontier at the end of the window.

**Task length.** d_j = `activities.hours_identity_median`: time share x 1,877 h / expected annual frequency, from O*NET ratings only. The AEI `est_task_hours` are not used in the main score. They exist only for DWAs used with Claude in 2026, and are about ten times longer than the identity, so mixing the two would make AI-used DWAs look harder. The AEI version is a variant.

**Unit costs, per unit of in-house cost w t** (ass:tasks-modes, prop:tasks-review, prop:tasks-augment).
- Automation (A): c_A/(w t) = pi(t) cm_j retry / w + c_Q. The quality cost is c_Q = w_R t_R xi + e L [1 - xi(1 + ln(1/xi))]. The review share is xi* = clip(max(exp(-w_R t_R/(e L)), 1 - (1 - qbar)/e, xi_min)), with:
  - review hours t_R = rho_rev t, with rho_rev = 0.575 (engine `review.rho_rev`, now linked to params.yaml);
  - reviewer wage premium 1.2;
  - L = L_mult x w t;
  - qbar and L_mult by GWA from `engine/src/autofrontier/priors/activity_attributes.csv`; licensed DWAs have qbar >= 0.999 and L_mult >= 10, and high-risk EU DWAs have L_mult >= 10;
  - xi_min: none 0, high-risk EU 0.25, licensed 0.30 (params.yaml).
- Licensed DWAs (`regulated_class` licensed or `licensed_time_share` >= 0.5) cannot be automated, but can be augmented. This follows the engine's `licensed_blocks_A`.
- A must also meet the residual-error requirement e(1 - xi) <= 1 - qbar.
- Inference: pi(t) is the frontier price per human-hour (params.yaml `ai_cost.inference_cost_usd_per_human_hour`, frontier tier; $1.27 at the time of the final run). It is flat until first feasibility and then falls at delta_pi = 2.303 a year, with a floor of 0.5%. The activity-class multipliers cm_j come from the engine defaults. retry = 1/(1 - min(e_cap, 0.8)).
- Augmentation (U): c_U = 1/(1 + beta_U) + pi_U/w. Here beta_U = 0.25 x beta_oj / 0.5, the engine's rule that the gain scales with exposure (assumed). pi_U = 0.25 pi, falling from 2022. U is feasible if non-physical, beta > 0.05 and H(t) >= d (the 50% horizon).
- Outsourcing (O), for separable GWAs (separable >= 0.5): c_O = 0.75 (0.95)^(t - 2022) + 0.10 + 0.03 (engine default vendor price ratio, coordination and risk shares).
- In-house (H): c_H = 1.
- A is optimal at t if it is feasible, permitted, meets the reliability requirement, and costs no more than min(c_H, c_O, c_U).
- Build costs F_A/(v T_A) and capital charges are omitted. At national scale volume is very large, which is a choice to note.
- Wages: OEWS May 2021 H_MEAN x (1 + 0.4287); A_MEAN/2080 where only an annual wage is published. Prices are 2026 list prices and are not deflated to 2021, because no deflator is local.

**Scores per occupation** (all sum_j s_oj beta_oj x indicator, averaged over the window).

| score | indicator |
|---|---|
| E | none (exposure) |
| E_np | non-physical and permitted for A |
| M_feas | capability-feasible for A (includes the physical lag and licensing) |
| M_AU | A or U optimal |
| **M (main)** | **A optimal** |
| M_save | hours saved (A: 1 - xi rho_rev; U: beta_U/(1 + beta_U)) |
| M_end | A optimal in May 2025 only |

The variants recompute M (and M_feas where it changes) under:
- T_d = 207 days;
- the METR TH1.0 2019+ fitted trend (H0 = exp(-3.712)/60 h at 2019.0, doubling 201 days);
- AEI task hours;
- inference price x10;
- no outsourcing option;
- iota = 0.2 or 0.8;
- rho_rev = 0.37, 0.8 or 1.19;
- human-rated exposure labels.

## 3. Crosswalks

- **OEWS May 2021 to May 2025.** Both vintages use SOC 2018. All 830 detailed codes in May 2025 appear in May 2021 with identical titles (checked programmatically). 11-1031 Legislators is in 2021 only and is dropped. No other crosswalk is needed. Five occupations per year have only an hourly wage (A_MEAN filled as H_MEAN x 2080).
- **OEWS to O*NET.** `xw_oews_onetsoc.csv` and `occ_activity.csv` (data agent). 47 residual codes (1.3% of employment) have no O*NET tasks, which leaves 782 occupations with all controls (98.5% of May 2021 employment).
- **May 2016 cross-section.**
  - Source: `gpts_are_gpts/repo/data/autoScores.csv`, columns `tot_emp` and `a_mean`. The file repeats one cross-section under a 2011-2019 year index (checked); the 2016 rows are used.
  - **Vintage verified.** The coordinator read BLS's May 2016 national tables (https://www.bls.gov/oes/2016/may/oes_nat.htm, 820 detailed occupations) in a browser on 29 Oct 2026. All 737 occupations match.
  - Checksums: sum of tot_emp 133,977,150 and sum of a_mean 43,494,840 in both. The script asserts these values (`VERIFIED_2016`).
  - Earlier versions of these notes recalled spot values; that caveat is withdrawn.
- **SOC 2010 to SOC 2018: the official BLS crosswalk** (`data/raw/bls_soc/soc_2010_to_2018_crosswalk.xlsx`, November 2017, sheet "Sorted by 2010"; 900 rows, 840 SOC 2010 and 867 SOC 2018 codes; read with `python3 -I`).
  - Nodes are SOC 2010 codes, SOC 2018 codes and OEWS May 2021 codes.
  - A SOC 2018 code absent from OEWS 2021 maps to the unique OEWS aggregate sharing its first six characters. There are 12 such aggregates: 13-1020, 13-2020, 21-1018, 25-2052, 25-9045, 29-2010, 31-1120, 39-7010, 47-4090, 51-2028, 51-2090 and 53-1047. Military 55- codes and 45-3031 are outside OEWS.
  - Each connected component is one comparable unit.
  - An occupation is **exact** when its component has all SOC 2010 members in the 2016 file, all SOC 2018 members in OEWS 2021, and no other 2021 occupation. **Allocated** means complete but shared; each member then carries the component change, which equals allocating 2016 employment by 2021 shares. **Incomplete** means members are missing; 103 SOC 2010 codes are not in the 2016 file.
  - Recovery:

| rule | occupations | share of May 2021 employment |
|---|---|---|
| exact (main) | 691 | 89.5% |
| exact + allocated | 748 | 95.1% |
| earlier identity rule | 639 | 77.7% |

  - Where the exact and identity rules overlap, the changes are identical (correlation 1.00).
  - The largest allocated component holds the computer occupations (12 occupations, including software developers).
- **May 2019 and May 2020 (hybrid SOC)** (`data/raw/bls_oews_2019/oesm19nat.zip`, `data/raw/bls_oews_2020/oesm20nat.zip`).
  - Each file has 789 detailed codes: 758 shared with SOC 2018 and OEWS 2021, 29 hybrid aggregates (for example 15-1256 = software developers + QA testers), one SOC 2010 code (19-3031) and Legislators.
  - Codes shared with SOC 2018 carry SOC 2018 definitions, so 2019-21 and 2019-20 changes are taken code by code: 758 occupations, 94.4% of employment.
  - 2016-19 uses the exact crosswalk components whose code is published in 2019: 691 occupations.
  - Occupations inside hybrid aggregates are dropped, because BLS's hybrid membership table is not local.
- **Occupation x industry (NAICS 2017 to 2022)** (`data/raw/bls_oews_2021/oesm21in4.zip`, `data/raw/bls_oews_2025/oesm25in4.zip`; nat4d and natsector sheets; one ownership row per NAICS in each file, checked).
  - Common four-digit codes are kept; 11 differ only in title wording (for example "Stores" to "Retailers").
  - 5111 to 5131 and 5112 to 5132, both renumbered.
  - 5151, 5152 and 5191 are combined with 5161, 5162 and 5192, because NAICS 2022 reallocated streaming and internet publishing.
  - Retail trade 44-45 is taken from the sector file, because NAICS 2022 folded nonstore retailers into the product-line retailers.
  - Result: 225 harmonized industries in both years.
  - Cells: detailed occupations in the occupation sample with at least 1,000 jobs in May 2021 and an estimate in May 2025, which gives 9,556 cells (76 cells missing in 2025 are dropped). The cells cover 755 occupations and 221 industries, 93% of May 2021 employment.
  - Combined industries sum employment; wages are employment-weighted.
- **BLS Employment Projections 2020-30** (released 2021; `occupations_projections_processed.csv`): exact lower-case title match to 2021 OEWS titles, 757 of 830 matched.
- **O*NET job zones:** mean over the O*NET-SOC codes of each OEWS code.
- **Firms.**
  - Function to occupation weights come from `function_occ_by_industry.csv`: SIC 7372 to NAICS 5132, 7371 and 7373 to 5415, 7374 to 5182. SIC 7370 uses the national `function_occ.csv`.
  - Function scores are wage-bill weighted (May 2021 mean wages).
  - Bucket scores use the within-bucket function splits of `industry_function_shares.csv`. These are assumed, and identical across SIC codes (checked), so the pooled row is used.
  - Bucket mapping follows `functions.csv` cost_bucket: COGS = revenue - gross profit; S&M; G&A; R&D = F02.

## 4. Estimation

**Occupation level.**
- OLS across 782 occupations, with 22 SOC major-group fixed effects and controls for physical task share, log 2021 mean wage and job zone. HC1 standard errors; clustered by SOC minor group as a robustness row.
- Scores are standardized within each regression sample, so coefficients are per 1 sd. The JSON also gives per-unit coefficients.
- Employment-weighted (May 2021) versions are reported.
- Out-of-sample R^2: 10-fold cross-validation, 50 repetitions with fixed seeds, on a common sample. The share of repetitions in which a set beats exposure is reported.

**Placebos and controls.**
- Placebos: the same scores and controls regressed on:
  - the 2016-21 change (exact crosswalk; variants with split codes and with the superseded identity rule);
  - the 2016-19 change, before COVID (exact crosswalk and hybrid 2019 codes);
  - log mean wage over the same windows.
- Trend controls: the occupation's own 2016-21, 2019-21 and 2016-19 changes, and the 2019-20 COVID shock.
- Expectations control: BLS 2020-30 projected growth.

**Occupation x industry cells.**
- Regressions:
  - Delta log employment on exposure, the cell model share, or the capability-feasible share, with industry and SOC major-group fixed effects. Controls: physical share, job zone and log cell wage.
  - The cell model share with occupation and industry fixed effects (absorbed exactly by alternating demeaning; checked against explicit dummies to 1e-6) plus the log cell wage.
- Standard errors are clustered two-way by occupation and industry (statsmodels).
- The cell model share uses the cell's May 2021 wage in the cost crossover. This is implemented as an exact wage-threshold form of the model, checked to reproduce the national scores to 0.
- Diagnostics: no industry effects; occupations weighted equally (1 / cells per occupation).
- Out-of-sample R^2: 10-fold, folds by occupation, 10 repetitions.
- Review-ratio sweep on a 0.05 grid plus the table points.

**Confounder exclusions** (judgment-based, defined in the script).
- Computer occupations: SOC 15 and 11-3021.
- Credit and real-estate occupations: 13-2023, 13-2041, 13-2072, 41-9021, 41-9022, 43-4041, 43-4131 (six are in the sample).
- COVID-rebound groups: SOC 27, 35 and 39.

**Firm level.**
- Sample: SIC 7370-7374 in `data/panel_v2_all.csv`, revenue >= $10M in the pre window, and all four cost lines in [0, 2] of revenue in both windows. 206 firms in the main window, 161 in the placebo.
- Windows: mean of FY2021-22 against mean of FY2024-25; placebo FY2016-17 against FY2019-20, which does not overlap the main window.
- Outcomes: changes in percentage points of revenue, winsorized at 2.5/97.5.
- Regressor: the cost-weighted mean of the bucket scores, standardized.
- Controls: log revenue growth, log pre-window revenue, pre-window total cost share, that bucket's own pre-window share, and SIC fixed effects. HC1 standard errors.
- Variants in the JSON: excluding acquirers (`acq_flag` in either window) and unwinsorized.

## 5. Results (final run; see the JSON for everything)

Occupation level, change in log employment, per 1 sd, HC1 SE:

| score | alone | with exposure (score; exposure) | out-of-sample R^2 | placebo 2016-21 (crosswalk) |
|---|---|---|---|---|
| exposure E | -0.052 (0.017) | | 0.160 | -0.039 (0.024) |
| E_np | -0.058 (0.015) | -0.048 (0.019); -0.014 (0.022) | 0.166 | -0.027 (0.019) |
| M_feas | -0.047 (0.012) | -0.041 (0.016); -0.012 (0.022) | 0.169 | -0.020 (0.017) |
| M_AU | -0.052 (0.014) | -0.051 (0.021); -0.001 (0.025) | 0.168 | -0.022 (0.018) |
| **M (main)** | **-0.046 (0.012)** | **-0.039 (0.015); -0.015 (0.021)** | **0.168** | **-0.016 (0.016)** |
| M, rho_rev = 0.8 | -0.009 (0.010) | -0.003 (0.010); -0.051 (0.016) | 0.148 | -0.004 (0.014) |

- The controls alone give an out-of-sample R^2 of 0.150.
- Wage-bill share: E -0.064 (0.018), M -0.045 (0.013); they tie out of sample (0.164).
- Mean wage: E -0.012 (0.007), M 0.001 (0.004); with both, M 0.013 (0.005). The wage placebo for M has the opposite sign.
- Employment-weighted: E -0.034 (0.016), M -0.023 (0.010); with both, neither is significant.
- Capability timing: holding E_np fixed, feas_frac = M_feas/E_np gives -0.044 (0.018), with a 2016-21 placebo of -0.001 (0.023).
- Mode split where A is feasible and permitted in May 2025 (exposed-time weights):
  - at rho_rev 0.575: A 99%, mean review share 0.74;
  - at 0.8: A 37%, U 50%, O 13%;
  - at 1.19: A 3%.
- The automate-or-augment share at rho_rev 0.8 still predicts: -0.048 (0.013).

**Firms.** All model-mix coefficients are positive (the wrong sign) and none is significant: total costs 2.2 pp per sd (2.0), with a placebo of 2.0 (2.3). The exposure mix gives 4.1 (1.5) for total costs. The mix score has an sd of 0.004 around a mean of 0.061. Mean changes: total -12.5 pp, S&M -5.3, G&A -2.5, COGS -2.3, R&D -2.2.

## 5b. Sweep over the review-time ratio (coordinator follow-up 1)

**Method.** The main specification (Table 1, panel A) is re-estimated at every value on a 0.01 grid over the sourced range [0.37, 1.19], plus the 9 evenly spaced points shown in Table `tab:backtest-sweep` and the pre-audit 0.8. At each point the script records:
- the model share alone, and the model share with exposure;
- out-of-sample R^2 for exposure, the model, and both, on the same folds and seeds;
- the share of the 50 repetitions in which the model beats exposure;
- the share of feasible, permitted exposed time on which automation is cheapest in May 2025.

Thresholds interpolate linearly between grid points. The JSON key is `occ.rho_sweep`.

**Results (final run).**
- Up to a ratio of about 0.57, automation is cheapest on all feasible exposed time, and the model share equals the capability-feasible score: -0.047 (0.012); with exposure, -0.041 (0.016).
- With exposure in the regression, the model share loses 5% significance at a ratio of **0.63**.
- It stops beating exposure out of sample at **0.66** (with exposure in the regression, at 0.69).
- Alone, it loses 5% significance at **0.71**.
- Automation is cheapest on less than half of the feasible time above 0.75.
- At 1.19 the model share gives +0.007 (0.011).
- The path is monotone: once lost, significance does not return.

The model beats exposure only in the lowest 35% of the sourced range. The sourced 0.575 lies inside that part; the pre-audit 0.8 lies outside it.

## 5c. Multiple testing (coordinator follow-ups)

**Family.** The family now has 28 tests: the 20 headline tests, 4 cell tests, the 2016-19 placebos (exposure, model share) and the model share with the 2019-21 and 2016-19 trend controls. The 2016-21 placebos now use the official crosswalk. Bonferroni at 5% two-sided needs |t| >= 3.12; for 20 tests it was 3.02. Holm's procedure gives the same set (checked in the script).

**Survivors (9):**
- the model share, log employment (t = 3.8);
- non-physical, permissible exposure;
- the capability-feasible share;
- the automate-or-augment share;
- the model share with the 2016-21, 2019-21 and 2016-19 trend controls;
- exposure, log wage-bill share;
- the model share, log wage-bill share.

**Headline change.** Exposure alone (t = 3.12) no longer survives at 28 tests. It survived at 20. No other original test changes status.

**Still not surviving:**
- the model share with exposure in the regression (t = 2.5), so "adds to exposure" rests on out-of-sample fit;
- all cell tests;
- all firm tests;
- all placebos. The 2016-19 model-share placebo has t = 2.2, which is significant at the 5% level before correction.

## 5d. Conclusions the evidence supports (revised after the new tests)

**Consistent with the evidence, with two qualifications.** The feasibility filters (activity type, i.e. non-physical work; licensing; the capability horizon) predict occupation-level employment change from 2021 to 2025 better than exposure alone, out of sample, and the capability-feasible score survives the correction. The qualifications:
1. The same scores already predicted slower growth from 2016 to 2019, before COVID and LLMs. Model share -0.025 (0.011); capability-feasible -0.027 (0.011). Per year this is 58% of the post-2021 slope. Controlling for that trend leaves -0.050 (0.011).
2. In occupation x industry cells, the advantage over exposure depends on weighting.

**Not validated:**
- the cost-crossover step: inert at the sourced ratio, harmful above about 0.66, and untestable within occupations;
- the automate-versus-augment choice;
- firm-level predictions.

This revises the conclusion previously recorded in `notes/integration_todo.md`: the pre-COVID placebo was not available then.

## 5e. Occupation x industry cells (coordinator follow-up, files supplied 29 Oct)

Coefficients per 1 sd, two-way clustered standard errors, 9,556 cells.

**With industry and major-group effects:**
- exposure -0.056 (0.022);
- model share -0.031 (0.014);
- capability-feasible share -0.034 (0.014);
- exposure and model share together: model -0.007 (0.016), exposure -0.051 (0.027).

**Out of sample** (folds by occupation, unweighted): exposure 0.126, model 0.123, capability-feasible 0.124, controls alone 0.123. Exposure is best here.

**Weighting, not industry effects, explains the difference from the national result.** The 50 most widespread occupations hold 43% of cells, and office and administrative support (SOC 43) alone holds 16%.
- Occupations weighted equally, with industry effects: model -0.045 (0.023), exposure -0.017 (0.037).
- Unweighted, without industry effects: model -0.018 (0.017) with exposure in the regression.

**Wage-driven cost crossover within occupations.**
- The within-occupation sd of the cell score is 0.0004, which is 0.01% of its variance.
- Coefficient per within-sd: +0.0062 (0.0044), the wrong sign. Employment-weighted: +0.0116 (0.0044). With inference x10: +0.0066 (0.0078).
- Significant at only 1 of 22 estimable grid points (positive sign).
- The test is uninformative.

**Cell sweep.** The model share alone loses 5% significance at a review ratio of 0.61. With exposure in the regression it is not significant at any ratio.

## 5f. Pre-COVID placebo and 2019 controls (coordinator follow-up, files supplied 29 Oct)

| test | coefficient (s.e.) |
|---|---|
| placebo 2016-19: exposure | -0.022 (0.020) |
| placebo 2016-19: model share | -0.025 (0.011) |
| placebo 2016-19: capability-feasible | -0.027 (0.011) |
| placebo 2016-21 (crosswalk): exposure | -0.039 (0.024) |
| placebo 2016-21 (crosswalk): model share | -0.016 (0.016) |
| placebo 2016-21 with split codes: model share | -0.008 (0.015) |
| placebo 2016-21, identity rule: model share | -0.014 (0.017) |

**Trend controls:**
- the 2019-21 trend moves the model share from -0.056 to -0.055;
- the 2019-20 COVID shock gives -0.056;
- the 2016-19 trend moves it from -0.057 to -0.050.

## 6. Limits

1. **Predictive, not causal.** The window contains the post-2021 COVID rebound, the 2022-23 tech layoffs and the rate cycle. Each is correlated with exposure. Fixed effects, exclusions and trend controls reduce but cannot remove this.
2. **Look-ahead in the inputs.** The capability path was fitted on runs through 2026, and T_d = 143 days is a 2024-onward estimate. The exposure labels were made with GPT-4 in 2023. O*NET 31.0 time shares, the Tomlinson et al. (2025) physical flags and the May 2025 staffing used for the firm-level function weights are all recent. Task length is O*NET-only, which avoids the AEI leakage.
3. **Specification search.**
   - About twenty specifications were run.
   - The decomposition columns E_np and rho_rev = 0.8, and the layer-by-layer arrangement, were added after the first estimates. The first estimates were made at rho_rev = 0.8, before the parameter files changed.
   - The main score's coefficient alone (t = 3.8) survives a Bonferroni correction for the 20-test family; with exposure in the regression (t = 2.5) it does not (Section 5c).
   - The variants that differ from the baseline are all reported.
4. **Calibration dependence.** The cost layer is nearly inert at the sourced review ratio, and it removes the signal at 0.8 or above. The exposure-scaled augmentation gain (`augment.exposure_ref`, assumed) drives the high-exposure activities into augmentation when review is costly. The backtest therefore does not validate the engine's automate-versus-augment choice.
5. **Measurement.** OEWS counts jobs, not hours, so the hours outcome in spec 24.1 is not testable. OEWS estimates are three-year rolling samples with sampling error. May 2021 employment was still COVID-affected. (The 2016 vintage is now verified; see Section 3.)
6. **Scope.** The backtest implements the paper's core model: theory_core unit costs, crossover and review share, plus the capability assumption of theory_ext. It does not implement every engine extension in `defaults.yaml`, such as domain-specific horizons, the computer-use multiplier, the slow-doubling physical mode, the augmentation quality terms or the failure taxonomy. It is a test of the paper's model with the engine's parameter values, not a test of the engine code.
7. **Firm level.** The score varies only through four cost buckets and the SIC code, and within-bucket splits are assumed. With 206 firms the test has little power, and it is dominated by the 2022-24 efficiency drive, which the model cannot separate from AI adoption.
8. **Occupation by industry.** Run (Section 5e). Results depend on weighting; the wage-driven cost term has almost no within-occupation variation.
