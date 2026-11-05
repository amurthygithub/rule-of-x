# Re-review report — R-B (empirics/econometrics/frontier estimation)

Paper: "The Rule of 40 as a Price Line..." (A. B. S. Murthy), 4 Nov build (87 pp main +
72 pp supp), repo_v4 @ eb7537b (branch review-round-3).

**Model-identity disclosure:** I am a separate conversation context of the same LLM
family as the Lead and all other panel members (the author addressed this panel as
"GLM 5.3 (high effort)"). We are not independent human experts and not independent
model-family evidence.

**Round-1 baseline:** I was referee B2 in round 1
(`/root/outputs/rule-of-40-review/` archive + the author's copy in
`repo_v4/notes/reviews/paper1_v3/author_reviews/glm_5_3_high/`). Round-1 conclusion: all
headline statistics replicated three ways (text↔outputs, outputs↔rerun, my own code from
the raw panel); findings were F1 stale `paper_stats.py` (v2 panel), F2 stale
`gap_decomposition.json`, F3 post-hoc 14-statistic familywise family (survivors fragile),
F4 excluded-registrant purge verifiability, F5 §5.8 counterfactual p drift, F6 SFA
reproducibility, plus estimand observations (firm-year pooling; capital-timing convention).

**Status: WORK IN PROGRESS — appended per work unit.**

## Plan (per assignment)

- C1 (STARTED FIRST, background): copy code/data/notes to scratch, rerun
  `code/estimate_v3.py` (author explicitly requests it: sample changed — R2 now removes
  8 firms/56 firm-years → 284 firms; capitalized software corrected; several headline
  values moved). Diff regenerated outputs vs committed when done.
- C2: run and time verify_theory.py, paper1_macros.py, supp_extensions.py,
  verify_part2_acquirer.py. No LaTeX in environment — record limitation; do
  text↔macros↔outputs reconciliation instead.
- C3 rows: GLM-F5, GLM-M1, GLM-M2, GLM-M9, GLM-M10, GLM-M18, GLM-2, GLM-3, GLM-4, GLM-20,
  GLM-23, ST-6 (verdict vocabulary: resolved / partly resolved / not resolved / disagree
  with the classification / new problem introduced).
- C4 Part B: (a) re-estimated headline numbers vs committed outputs; (b) new S11 spec
  curve audit; (c) R2 whole-sample application audit (kappa 0.95); (d) capitalized-software
  correction trail; (e) abstract consistency with new numbers.

**Hard rules honored:** excluded registrant NOT to be recovered or named (author's rule
this round — supersedes my round-1 F4 verification; I will not use round-1 knowledge of
its identity in this report); restricted reading (other reviewers' folders, response files)
sealed until Part B saved+hashed; work on copies only.

---

## C1 — Full pipeline rerun (launched first)

- Scratch copy of repo_v4 code/data/notes (+ sections/, paper1/ needed by the report stage)
  at `diag/rereview-empirics/scratch/`. `data/panel_v3.csv` sha256
  03b698206b9182a33e8866451fb723447f03f26ac0545475e6e661531aa74924 (round-1 panel was
  c44416b1… — the sample has changed, as the author says).
- New panel: **1,732 firm-years / 284 firms** (was 1,788/292; −56 firm-years / −8 firms ✓
  the R2 whole-sample change). By period 444/405/446/437 (was 465/418/458/447).
- `V3_JOBS=4 nohup python3 code/estimate_v3.py` launched 03:45:33 CET; point estimates
  done at **16 s** (round 1: 38 s — faster machine/code); 999-rep bootstrap in progress.
  (A first launch with the env var mistyped as argv and a second concurrent launch were
  killed within 30 s — no output files had been written yet; a single clean run then
  started. Recorded for transparency.)
- Diff vs committed outputs: PENDING (appended below when the run completes).

## C3 — Row verdicts

### GLM-F5 (post hoc family; consequence now stated) — **resolved**

- Locator: M 5.1, printed p. 43 (= PDF p. 43).
- The new sentence: "The survival statements depend on the family: adding the
  frontier-point changes T (20%) on both bases and T (0) after SBC, and the anchor test of
  Section 5.8, gives an 18-test family in which the Holm-adjusted p-value of the 2020–25
  steepening is 0.037, 0.132 and 0.036 (normal, percentile, basic), that of the GAAP
  decline 0.061, 0.104 and 0.270, and that of the anchor 0.004, 0.120 and 0.036."
- My recomputation from the stored (re-estimated) p-values
  (`scripts_holm_f5_m1.py` → `holm_f5_m1.txt`): steepening **0.037/0.132/0.036**, GAAP
  p95 decline **0.061/0.104/0.270**, anchor **0.004/0.120/0.036** — **exact match** on all
  nine values. The 18-test family is exactly the one my round-1 counterfactual proposed
  (T(20%) both bases + T(0%) cash + anchor).
- Two corrections to my round-1 report that the author's issue log made and I accept:
  (i) my "loses 5% survival under all types" was wrong for the 18-test family under the
  normal type (0.048 < 0.05 on the old sample); the correct statement is
  family-composition- and type-dependent, which the new sentence now states per type.
  (ii) my round-1 "0.008–0.371" anchor values in the 20-test scenario were misindexed
  (position 14 held T(20%) GAAP, not the anchor; the anchor's true 20-test values were
  0.008/0.144/0.040). The author's issue log caught both; being right matters more than
  defending my first review.
- Note: the printed 18-test values are those of the NEW sample (they differ from the
  issue log's old-sample values 0.048/0.084/0.052, as the response's caveat "numbers
  quoted in the rows below that predate this re-estimation can therefore differ" warns).

### GLM-M1 (anchor Holm count) — **resolved**

- Locator: M 5.8, printed p. 48.
- The new text goes further than the response letter described: instead of "over 14
  tests (the family's estimable members and the anchor)", the printed text uses **"over
  15 tests (the family, with its non-estimable member at p = 1 as in the 18-test family
  above, and the anchor)"** — i.e. the stricter count that treats the family exactly as
  its own correction does — and prints 0.003 (normal), 0.090 (percentile), 0.030 (basic).
- My recomputation from stored p-values: 15-test anchor Holm = **0.003/0.090/0.030**
  (exact match); the 14-test (13 estimable + anchor) alternative would give
  0.003/0.080/0.028. The printed conclusion "survives at 10% under every type and at 5%
  under two" holds for the printed 15-test values (0.090 < 0.10; 0.003 and 0.030 < 0.05).
- The response letter's "14 tests / 0.006, 0.096, 0.030" reflects the pre-re-estimation
  vintage; the PDF is internally consistent with the new stored p-values. No defect.
- Note: the response letter and the PDF describe the count differently (14 vs 15); the
  PDF text is the authoritative and self-consistent one. Not a finding — the response
  says explicitly that the paper is authoritative where the rerun moved numbers.

### GLM-2 (firm-year pooling clause) — **resolved**

- Locator: M 5.1, printed p. 41: "…the χ-quantile of the margin among firm-years that
  grew at least g0 (computed over firm-years, so each firm contributes one chosen point a
  year)". Exactly the clause my round-1 observation (a) proposed. Verified present.

### Round-1 E2 thinness numbers (context, not a row): the new §5.1 prints 14.6%/12.1%
(was 16.8%/13.0%) and conditional E2 intervals −0.486 to −0.069 / −0.407 to −0.028;
these moved with the re-estimated sample and will be checked against the rerun output
below.

## C4(a) — Re-estimated headline numbers vs committed outputs — **ALL VERIFIED**

New Table 2 (printed pp. 42–43) reconciled cell-by-cell against the committed
`notes/empirics_v3.json` (`scripts_reconcile_t2_v4.py`): **164/164 cells match** (point
estimates, SEs, 90% percentile intervals, all four views), as do all sample counts
(1,732/284; 1,330/270; 1,730/283 ×2; 457/57 acquisition-affected; 105/62/88/91 with
g>50%). The response's moved values all verify:
- **Ψ0.90 slope −0.20 (0.11; 90% CI −0.42 to −0.03) GAAP / −0.17 (0.09; −0.29 to +0.01)
  cash** — stored: −0.2001 (se 0.1133, CI [−0.4168, −0.0276]) / −0.1695 (0.0944,
  [−0.2910, +0.0116]) ✓; χ×window ranges −0.45…−0.19 GAAP, −0.31…−0.09 cash ✓;
  order-m −0.188/−0.147 → "−0.19 and −0.15" ✓.
- **P95 fall −11.9 (GAAP) / −12.6 (cash)** ✓ (Table 2 B-panel and §5.2; intervals
  [−20.2,−6.6] / [−20.7,−4.1] match stored CIs).
- **Anchor 14 firm-years** (of 7 firms) under E1, 19 of 10 under E2 ✓
  (`calibration_anchor_v3.json`: n=14, n_firms=7).
- **2036 central score 58 [54, 62], 53 after the in-flight dip** ✓
  (`calibration_results.json` central_path: R∞=0.5777→58, dip=0.0443→4.4,
  R_net=0.5334→53; Table 6 row "A firm still transforming (in-flight dip) 53 58 4";
  Table 5 dip column 3.8/4.1/4.4 matches stored 0.0377/0.0415/0.0443).
- **Romano–Wolf p of the GAAP decline 0.075** ✓ (headline14B p95chg_op: RW=0.075; the
  paper now also discloses the Monte Carlo SE ≈0.008 — a GPT-14 suggestion, good).
- **284 firms** ✓ (panel: 1,732 firm-years / 284 firms; §4.2 "1,732 firm-years for 284
  firms (1,929 and 293 before the rules)" matches `panel_v3_build.json` counts).
- Also verified in passing: §5.2's Holm claims (GAAP decline Holm 0.045/0.072/0.210 →
  "0.045 to 0.210", survives 5% only under normal ✓; cash decline none ✓); §5.1's updated
  E2-thinning numbers (14.6%/12.1%; conditional intervals −0.486/−0.069, −0.407/−0.028 —
  to be re-confirmed from my rerun); §4.5's E2 arithmetic (457 affected = 270+187; 57
  kept; 400 dropped; 2 unverifiable ≥100%-growth years; E2 1,330/270; bounds 1,730);
  §4.1/4.4 stats vs regenerated `paper_stats.json` (26%/41% flag shares; 96.3–99.8%
  original-filing; 89% US address; 6% discontinued; 2.2% capex-missing).

### GLM-M2 (stale paper_stats.py) — **resolved**

- `code/paper_stats.py:13` now reads `data/panel_v3.csv` with `acq_flag_v3`, and its
  docstring records the round-3 fix; meta records panel/n/firms/acq_flag source.
- Regenerated in scratch (11 s): **41/41 fields byte-identical to the committed
  `notes/paper_stats.json`** (0 value diffs). The text-facing fields now match the v3
  macros.
- The companion stale artifact (`decompose_gap.py`) was retired rather than regenerated:
  it is now labeled in code and in its own output meta as "v2 reproduction reference"
  (`status='v2 reproduction reference for code/estimate_organic.py'`), which addresses
  the confusion risk my round-1 F2 flagged. Verified in `code/decompose_gap.py:9,67`.

## C1/C2 status (Lead-covered, recorded)

The Lead completed my C1 rerun diff (byte-identical tables/anchors/paper_stats;
frontier slopes at machine epsilon; only SFA fields differ ≤8.3e-5, plus cosmetic
/meta/workers) and my C2 script runs (verify_theory 116 PASS; paper1_macros PASS with
macros byte-identical and abstract 1916/1920 chars; supp_extensions 27/27;
verify_part2_acquirer 90/90). Archived at `diag/rereview-empirics/lead_full_bootstrap_diff.txt`.
My own earlier partial runs agree: paper_stats.py regenerated 41/41 fields identical;
my first verify_theory run hit my own 900 s timeout mid-run (machine contention with the
4-worker bootstrap) — superseded by the Lead's clean run. NOT run by anyone: LaTeX builds
(no TeX in this environment) — recorded limitation; text↔macros↔outputs reconciliation
done instead (Table 2: 164/164 cells; §5.2/5.3 values; Table 5 path vs
`calibration_results.json`).

## C3 remaining rows

### ST-6 (growth-engine lever count) — **resolved**

- Locator: M 7.5 printed p. 68; supp S10 printed p. 60; Table S18 row "Growth engine ahead
  of the G&A cut at one of six positions (count)".
- Stored outputs: `notes/mc_results_2026-11-03_1m/mc_claims_report.md` L1.full.net row:
  count range 0.00–1.00, share at stated count **0.576** ✓ (dims table: maintenance base
  bootstrap 5–95% = 0.2368/0.2574/0.2791 ✓ = `anchor_p95_maint_base` E1 est/ci90).
- My independent recomputation from the stored anchor-block bootstrap draws
  (`bootstrap_draws_v3.npz`, 999 draws of the maintenance base) + Table 7 cell medians
  (`playbook_results.json`): count at the central base = **1** ✓; restricted to the 90%
  interval of the maintenance base (as the S10 sentence discloses: "whose maintenance base
  follows its bootstrap distribution within that interval"), count range **0–1** ✓ and share
  with count 1 = **57.4%** vs the printed/stored 57.6% (difference ≤0.2pp, interval-edge
  convention). Note: unrestricted over all draws the count reaches 2 (Sub-40 grower's
  σ̂ overtakes its G&A when the base falls below 23.5%), but the paper's claim is
  explicitly the interval-restricted one, correctly worded. M 7.5's sentence "at 5 of the
  6 positions … at the central maintenance level; over the 90% bootstrap interval of that
  level the growth engine leads at 0 to 1 positions" ✓ consistent with new Table 7
  (growth corner ratio 0.99 → growth engine; maintenance base now 25.7%).

### GLM-M9 (pairing convention + S11 forward variant) — **resolved**

- M 4.3 sentence present: "pairing growth over the past year with the same year's margin,
  the contemporaneous convention of reported scores (Section 3)" ✓.
- S11 forward-pairing: every quoted number reproduces from
  `notes/spec_curve/specs_forward.csv.gz` (point estimates, my own reads): E1 declines
  **−11.1/−11.1** (vs −11.9/−12.6 reported) ✓; slopes **−0.29/−0.24** (vs −0.20/−0.17) ✓;
  period differences **−0.30/−0.08** ✓; E2 declines **−8.8/−9.6** (pf25_rule rows) ✓;
  pair counts: **1,441 of 1,732** firm-years (my panel count: 1,441 ✓) and **270** pairs
  with a 2023/2024 margin (my count: 270 ✓); E2 60%-cell **15 pairs** and imputation-M4
  **26 pairs** (both recomputed from the author's frames + my pairing logic) → 0–60%
  slope undefined there ✓; grid-wide: decline holds in 100% of 3,840 GAAP / 98.7% of
  11,520 cash defined specs ✓, slope above −1 and below zero in every defined spec ✓,
  above −0.5 in 26.7% GAAP ✓, GAAP difference negative in 92.6% ✓. No sign change under
  E1 ✓ (all declines negative; steepening −0.30 GAAP still negative).
- Response's S11 wording ("no pairing changes the sign of the decline, the slope or the
  GAAP steepening under E1") is accurate.

### GLM-M10 (S7 element list) — **resolved**

- S7 Elements (supp printed p. 30) now names OperatingIncomeLoss ("Operating income, the
  numerator of the GAAP margin: OperatingIncomeLoss") and, under "Retrieved but not used
  in any reported statistic", the six: NetIncomeLoss; PropertyPlantAndEquipmentNet (an
  instant); DepreciationDepletionAndAmortization and DepreciationAndAmortization;
  FinanceLeasePrincipalPayments; SellingGeneralAndAdministrativeExpense.
- Count check vs `code/fetch_companyfacts.py` CON list (35 elements): I matched all 35
  named tags against S7's bullets — **35/35 now nameable by tag** (was 27/35). ✓

### GLM-M18 (SFA reproducibility footnote) — **resolved**

- S7 Reproducibility (supp printed p. 45 area): "…exactly when run on the distributed
  extract, apart from the stochastic-frontier maximum-likelihood estimates, whose
  optimizer can end at slightly different points across environments." ✓ exactly the
  proposed fix; consistent with the Lead's rerun diff (SFA-only deviations).

### GLM-3 (lagged S&M provenance) — **resolved**

- M 5.4: "the median ratio of the previous year's selling-and-marketing share, taken like
  growth from the same filing" ✓ (sentence present; matches the build convention my
  round-1 Q4 identified).

### GLM-4 (build-after-purge) — **already handled, confirmed**

- S7 states the build scripts drop the excluded registrant (verified present in the
  data-construction section; consistent with `code/exclusions.py` mechanism). ✓

### GLM-20 (search protocol) — **resolved**

- A.6 now has the sentence describing how the negative-existence statements were
  searched (web searches by the literature agents and outside reviewers; candidates
  checked at Crossref/RePEc/publisher; **no query log kept**) ✓. The no-log disclosure is
  honest; the protocol is minimal but stated, as proposed.

### GLM-23 (confirmations) — **confirmed, no change needed**

- My round-1 confirmations (164/164 Table 2 cells; full-bootstrap rerun; independent
  reimplementation ≤5e-4; Prop 2 numerics) remain valid for the old build; the author's
  issue log accepted them; nothing further required.

## C4 remaining Part B items

### (b) S11 specification-curve audit — **verified; pre-specification credible**

- **Table S19: every cell reproduces** from `notes/spec_curve/specs.csv.gz`
  (155,328 rows; my `scripts_spec_curve_check.py` → `spec_curve_check.txt`): C1 5,760
  defined, 94.3% point/29.0% interval, baseline −11.9, median −4.9, −14.4 to +2.6 ✓;
  C2 17,280, 100/42.2, −12.6, −7.2, −13.6 to −1.0 ✓; C3 8,360 defined (of 9,600),
  100/100, below zero 100/96.1, above −0.5 65.5% ✓; C4 23,520, 100/100, 100/99.2,
  87.9% ✓; C5 6,080, 91.9/18.4, −0.41, median −0.24, −0.49 to +0.20 ✓; C6 17,800,
  74.4/99.0 ✓; C7 960, 32.5%, baseline 3.07, median 3.65, 3.05–3.80 ✓; C7s 3,840, 31.0%,
  median 2.93, 2.05–3.80 ✓; C8a 4,096, 100/99.2, +19.2, median +16.4, +6.3 to +28.1 ✓;
  C8b 99.7/38.4, +12.3, +9.8, −0.2 to +27.1 ✓; C8c 22.3% above zero, −1.6, −10.1, −17.8
  to +18.3 ✓. §5.8's quotes (99.7%/38.4%/99.2%) ✓; §5.2's quotes (6.3–12.9 GAAP, 6.8–12.7
  cash; 62.6%/56.3% interval shares — from the S11 text) and §5.3's are consistent with
  the stored design.
- **Choices varied** (design.md §2): 15 treatments of acquired growth (observed, pro
  forma at 3 flags × 3 readings, exclusion at 3 flags, imputation M=4/8), R1/R2/R5/
  debt-only sensitivities, two growth bounds, per-claim options (quantile, period split,
  estimator Ψ0.80/0.85/0.90/0.95/order-m, window, benchmark, anchor cut-off, S&M basis)
  — 960 samples × claim-specific options; each specification counted once; intervals on
  206 bootstrapped samples × 199 reps. Coherent and matches the CSV columns.
- **"Written down before any estimate"**: `notes/spec_curve/design.md` is timestamped
  2026-11-03 14:36 UTC and states nothing below was changed after the first run, with
  later corrections recorded in `log.md` with times (I verified both files exist; the
  design quotes the pre-re-estimation text, consistent with its date). The claim is
  credible and checkable via git history; the design doc also operationalises C3c ("well
  under a point" as > −0.5) with the honest label "Operationalised here, not by the paper".
- **Leave-one-firm-out**: present as part of the sample options (design §2/§5; the S11
  text and §5.9 reference it; the LOFO machinery for the anchor is in
  `calibration_anchor_v3.json` leave_one_firm_out). Verified as an option in the stored
  spec columns.
- **E2/imputation 60%-cell statement**: verified true (15/26 pairs; see GLM-M9 row).
- **Assessment**: this is a genuinely strong addition — a Simonsohn-style multiverse over
  the paper's own defensible choices, pre-specified, with all 155,328 specs stored. It
  materially narrows several claims (steepening interval 18.4%; netted anchor 38.4%) and
  the paper says so in §5.2/§5.8. No defect found.

### (c) R2 whole-sample application — **verified, adequately described**

- All 293 pre-rule core registrants' descriptions retrieved and archived:
  `data/v3_inputs/business_descriptions.json` (n=293, covers every core v3 firm ✓);
  provenance in `README_retrieval.md` + `code/audit/r2_descriptions.py` (named-firm text
  of 29 Oct + 3 Nov retrieval for the rest, same extraction rule, asserts full coverage).
- Pre-fixed keyword rule: `code/build_panel_v3.py:242-260` (KW lists; a non-software class
  with ≥3 hits and more hits than software ⇒ excluded); **git diff 62e574b→eb7537b shows
  the KW lists unchanged** — only the application scope moved from named-firms-only to
  the whole sample. Rerunning `classify()` on the descriptions I reproduce exactly the 8
  firms the paper names (Bally, Inspired; Activision, Changyou, EA, GCL, PLAYSTUDIOS,
  Snail) ✓; `panel_v3_build.json`: excluded R2_not_software = 56 firm-years ✓
  (1,929 − 140 − 56 − 1 = 1,732 ✓).
- Two blind readers: `business_class_reader_{a,b}.csv` (293 each, with class/subclass/
  confidence/reason/quote). My recomputation: **binary software/not-software agreement
  289/293** ✓; **Cohen's κ = 0.9525 → 0.95** ✓ (my first pass used multi-class agreement
  and got 286/0.917 — my error, corrected; the paper's is the binary verdict, which is
  the R2-relevant one); both readers class 49 not software, at least one 53 ✓; the
  sensitivity firm-year counts 223/237 ✓ (`R2_readers.v3_firm_years_dropped`).
- Adequacy: §4.2 and §5.9 describe the partial nature of the classifier (it misses THQ,
  Take-Two, Roblox, Unity, CoreWeave) and report the reader-based sensitivities
  (P95 fall 8.8/9.1, slope −0.37/−0.29 without both-readers' firms) — the strongest R2
  reading moves the slope to −0.37, which the paper states plainly. Good disclosure.

### (d) Capitalized-software correction trail — **verified, complete**

- `notes/data_audit/` contains the full trail: `sample_design.json` (40 seeded firm-years,
  seed 20261103, 16 from the top decile of the cash score, frame = panel_v3 pre-R2
  1,788), `compare.csv`, `capsw_summary.json`, `capsw_missed.csv`,
  `capsw_cashflow_rows_2026-11-03.json`, and `code/audit/capsw_scan_parse.py`.
- S7's numbers all reproduce from `capsw_summary.json`: **1,213 scanned** ✓ (frame =
  3 Nov pre-R2 core), 1 not read, **121 candidates** ✓, dropped 3 not-outflow + 9
  combined-capex lines ✓, **109 kept firm-years of 23 firms** ✓, median 1.58% → "1.6%" ✓,
  max 9.21% → "9.2%" ✓. The panel carries `cap_sw_source` with exactly **109** rows
  'filing_cash_flow_statement' ✓. The 40-firm-year face-statement check (234 values, 230
  equal, none wrong) is in `sample.csv`/`compare.csv`; I did not re-read the sec.gov
  filings myself (recorded as not re-checked; the artifacts are internally consistent and
  the seeded design is recorded).

## Coverage summary

- **Verified by me**: new Table 2 (164/164 cells) and §5.2–5.3/5.8 text numbers vs
  committed outputs; Table 5/6 path + in-flight dip vs calibration_results; headline moves
  (−0.20/−0.17; −11.9/−12.6; anchor 14; 58/53; RW 0.075; 284 firms); GLM-F5/M1 Holm
  recomputations (18-test and 15-test, exact); GLM-2/M10/M18/M3/M4/M20 sentences present;
  GLM-M9 + S11 forward pairing (all quoted numbers incl. 1,441/270/15/26 pairs, E2
  declines); Table S19 (all cells from specs.csv.gz); S11 design/pre-specification; R2
  (descriptions, classifier rerun, 8 firms/56 firm-years, κ=0.95, 49/53, 223/237);
  capitalized-software trail (1,213/121/109/1.6%/9.2%); ST-6 (0–1, 57.4% vs 57.6%);
  paper_stats regeneration (41/41).
- **Covered by the Lead** (not redone): full 999-rep bootstrap rerun diff (byte-identical
  except SFA ≤8.3e-5); verify_theory 116 PASS; paper1_macros PASS (macros byte-identical,
  abstract 1916/1920); supp_extensions 27/27; verify_part2_acquirer 90/90.
- **Not checked**: Lean formalization (S4; no Lean here — R-A's remit); LaTeX build of the
  PDFs (no TeX in this environment — text↔macros used instead); sec.gov face-statement
  re-reading for the 40-firm-year audit; the stress test's own Monte Carlo (1m draws —
  stored outputs audited, not re-run); S12's three analyses in depth (R-A/R-C per the
  Lead's split); restricted reading sealed until Part B hash (not opened).

**Bottom line for my remit**: the re-estimated empirical core again replicates
completely (text ↔ committed outputs ↔ my independent recomputation), every round-1
finding in my assignment was addressed (F5 and M1 beyond what the response letter
described), and the two new analyses that touch my remit (S11 specification curve, R2
whole-sample) are sound, pre-specified where claimed, and honestly described — including
where they weaken the paper's own claims (steepening interval 18.4%; netted anchor 38.4%).
No new problem introduced by the fixes surfaced in my checks.

### (e) Abstract consistency — **verified**

New abstract (printed p. 1) quotes the new numbers everywhere and keeps the conditions:
"284 software companies" ✓; "fell … by 11.9 points on GAAP … (6.3 to 12.9 across samples;
significant at 10% under three of four corrections for multiple tests)" ✓ (Holm normal
0.0455 + percentile 0.072 + RW 0.075 of four; basic 0.210 fails); "by 12.6 on free cash
flow after stock-based pay (not significant)" ✓; "about a fifth of a point less margin" ✓
(−0.20); "at central costs and fixed prices … over 32.5% a year, with AI compute at 6% of
revenue (28 to 78% across compute costs…)" ✓ (ST-1 condition stated); "realizes 41% of its
program's benefits by 2036 and reaches a lasting score of 58 (53 while still paying for
changes under way; 54 to 62 from sampling alone)" ✓ (58/53/41%/[54,62] all verified vs
stored outputs; "from sampling alone" = ST-2's anchor-only-interval disclosure ✓);
"repays … in 7.5 years" ✓; "Under a verification hypothesis" ✓ (the (H) qualifier kept).
No stale number found in the abstract.
