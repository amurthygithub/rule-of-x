# Round 3 code, data and generated-output changes (coding agent, 2-3 Nov 2026)

Scope: the code side of the round-3 plan approved by the author at 23:23 on 2 Nov 2026 (outside reviews of v3:
`notes/reviews/paper1_v3/author_reviews/{deepseek_v4_pro_high,gpt_6_1_sol_xhigh,glm_5_3_high}/issue_log.md`). The macro
names and values for the editor are in `notes/r3_macro_contract.md`. Nothing was committed; prose files were not edited.

## Changed printed numbers (old -> new)

| Macro | Old | New | Item |
|---|---|---|---|
| `\CcLo` | 1 | 2 | GLM-M11 / GPT-22: low credible compute share per completed process (1% successful-run cost at a 50% success rate) |
| `\GstarCcLo` | 28 | 29 | same (29.2%) |
| `\GstarAccCcLo` | 23 | 24 | same, accountability-only threshold |

No other existing macro changed value. Macros removed: the six unused v2 gap macros `\GapAvg`, `\GapAvgOne`, `\GapFast`,
`\GapFastSM`, `\GapSlow`, `\GapSlowGM` (GLM-M2; no .tex file used them). Every other change adds macros or relabels.
Flagged, not changed (GPT-4): under the exact recurrence the fast case's NPV and PV ratio would print 213 and 7.0 instead of
212 and 6.9; the central numbers are unchanged at their printed rounding.

## Code

- `code/calibrate_horizons.py` — new block `out['r3']` after `out['r2']` (new keys only; verified that every pre-existing
  value of `notes/calibration_results.json` and every table the script writes are byte-identical to the committed ones
  before the GPT-21 row text below):
  - `ell_psi_cone` (GPT-M1): the frontier-slope multiplier through the E1 growth values of each basis, in closed form
    (cone slope at ell = 1, cells g >= g0 as in `estimate_v3.py` cone_mat). `ell_psi` is kept unchanged.
  - `psi_period_cash` (GPT-M2): psi_15 evaluated at g and the period-cash loss at k = 1.5, G = 30%.
  - `exit_value` (GPT-M4): value at year 5 of the later flows and the break-even sale recovery, from the stored payback.
  - `payback_to_completion` (GLM-M5): `payback()` with T = the date the capped bound reaches the program.
  - `exact_recurrence` (GPT-4): the divisible program's exact expected recurrence U_w = U_{w-1} - q min(c, U_{w-1}),
    99% dates, payback, NPV and PV ratio with attempts continuing on the residual; asserts that the bound's dates are
    pace()'s and that the central realized shares through 2036 are the bound's.
  - `vprime_shape` (GLM-F1 / GPT-2): the worked example's v'(s) profile on the N = 4000 upwind sweep (a copy of
    `verify_theory.solve_hjb`), v' from the HJB optimality condition.
  - `compute_credible` (GLM-M11): CC_LO_SUCCESSFUL_RUNS 0.01, METR_SUCCESS_RATE 0.50, low bound 0.02, high 0.60, thresholds.
  - `pace_params` (GPT-26): the execution cases' inputs.
  - Table tab:fullcost row "Error rate with no review" (written into `sections/appendix_proofs.tex` between the markers):
    class "(a, b) omission and hallucination rates of retrieval-grounded work" -> "(d) scenario value: an omission rate per
    source sentence plus a hallucination rate per output sentence (favorable) or per summary or answer (central,
    conservative), which have different denominators, ..." (GPT-21). Value unchanged. Comment at FC['u_rev'] updated.
- `code/paper1_macros.py`:
  - compute-share range reads `r3.compute_credible` (the three changed macros above) and adds `\CcLoRuns`,
    `\GstarCcLoRuns`, `\GstarAccCcLoRuns`, `\CcSuccessRate`;
  - round-3 block (GPT-M1, M2, M4, GLM-M5, GPT-4, GPT-9, GLM-F1, GLM-M3, GPT-26), GPT-8 persistence macros (editor's
    request), DS-57 `\AminPhmTot*`, GLM-F5 counterfactual Holm families (from the stored p-values; asserts the stored
    family's Holm is reproduced), GPT-14 `\HolmTopRWSe`;
  - 11 new CLAIMS entries (listed under "New checks");
  - GLM-M2: no longer reads `notes/gap_decomposition.json`; the v2 gap macros retired;
  - `paper1/macros.tex` ends with `\IfFileExists{paper1/stress_macros.tex}{\input{...}}{}`; the stress macros are also
    loaded for the plain-text abstract.
- `code/verify_part2_acquirer.py`:
  - new section I (checks I1-I8): decompresses the sec.gov copies of the 424B4 and F-1 (and hashes the two 6-K
    exhibits), checks each SHA-256 against `data/v3_inputs/README_retrieval.md` section 5 and the figures file, splits the
    documents into printed pages, finds every figure of `data/v3_inputs/bending_spoons_annual_2024_2025.json` on its page
    in both documents (organic-growth sentences and their definition included), cross-checks the extract and the
    cash-interest file, re-verifies the pro forma (DS-69), and computes the Table 3 organic rows (GLM-F2), the panel-basis
    cash score 112.6 (GPT-17), the annual investing split (GLM-6), the annual units of the acquisition charge (GPT-M3) and
    the coupon variant on interest expense (GLM-M6);
  - the round-3 macros are always written to `sections/tables/acquired_macros.tex` (REQUIRED_P1);
  - E7 relabelled as the after-interest, round-1 basis kept as a regression check (DS-65); target unchanged.
- `code/estimate_v3_report.py` (GPT-13): "no change (includes 0)" -> "no directional claim (interval includes 0)"; the
  table note and `notes/inference_v3.md` say no directional claim is made and no equivalence margin is tested.
  Regenerated with `V3_REPORT_ONLY=1 python3 code/estimate_v3.py` (no re-estimation): only those strings changed in
  `sections/tables/tab_estimands_v3.tex` (and its copy `paper1/tab_estimands_v3.tex`) and `notes/inference_v3.md`;
  `notes/empirics_v3.json` and the other tables are byte-identical.
- `code/paper_stats.py` (GLM-M2): reads `data/panel_v3.csv` with the v3 acquisition flag; regenerated
  `notes/paper_stats.json` (the printed G&A, Microsoft/Oracle, Palantir and AppLovin macros are unchanged; the unprinted
  acquisition-flag share and pass-40 shares now match the v3 macros). `PAPER_STATS_OUT` overrides the output path.
- `code/decompose_gap.py` (GLM-M2): kept on the v2 panel as the v2 reproduction reference of `estimate_organic.py`
  (whose v2 checks read it); docstring and a `meta` block in `notes/gap_decomposition.json` say so. Rerun: the JSON is
  identical apart from `meta`; `tab_gap.tex` unchanged (not used by the paper).
- `code/verify_theory.py`:
  - checks 15l-15p (GLM-F1, on its own grid with np.gradient): v'(0.99) > v'(0.5); v'(0.9999) within 1% of 5.83;
    interior minimum at 70-90% of the cap, below its 1% value from 50% on, below v/s; retention gain near saturation;
    [text] profile macros;
  - section 29: 29a/29b (GPT-M1, brentq on ell against the closed form; [text] macros), 29c (GPT-M2 vintage schedule;
    [text]), 29d (GPT-M4 identities; [text]), 29e (GPT-4 exact recurrence: geometric tail and the 99% wave count);
  - 20h: the verify-side constant CC_BOUNDS low end 0.01 -> 0.02 to match the approved low bound (GLM-M11); the check
    now also asserts the successful-run values (`\CcLoRuns`, `\GstarCcLoRuns`, `\GstarAccCcLoRuns`). Its logic is
    unchanged: printed values against an independent recomputation at the stated bounds.
- `code/mc_claims.py` (GPT-21): class of `u_rev` "b" -> "d" (label only; the committed results are not re-run).
- `code/mc_report_tex.py` (new): Table tab:stress, `paper1/stress_macros.tex` (58 \St* macros) and
  `figures/fig_stress.pdf` from the committed stress-test outputs; asserts the draws file agrees with the JSON.
- `sections/supp_stress.tex` (at the coordinator's request, 3 Nov; the only prose file edited): "every check passed" ->
  "all \StReproChecks{} checks passed"; ST-4 "is at most marginally positive" -> "is at most \StCumMaxCen{} points of
  revenue times years" and "it can be clearly positive" -> "it reaches \StCumMax"; ST-5 "once change capacity is moderately
  above its central value of \PaceCapCen\% of the program a year" -> "once change capacity exceeds about \StCapHalf\% of
  the program a year, against its central value of \PaceCapCen\%". `code/paper1_macros.py`: the CLAIMS label that quoted
  "significant at 10% ... under most procedures" now quotes the current empirics.tex sentence, and its test adds "at 5%
  under none" (Romano-Wolf's side of 0.10 is the GPT-14 entry).
- `code/regenerate_all.sh`: new stage `stress_report` after `calibrate` (runs `mc_report_tex.py`; does not re-run the MC).
- `code/REPLICATION_README.md`: the stress test, its reproduction command (`python3 code/mc_claims.py --n 10000
  --workers 4 --out notes/mc`), `mc_report_tex.py`, the report-only rerun, the raw filings and the figures file;
  `paper_stats.py` and `decompose_gap.py` rows updated.

## Data and notes

- `data/v3_inputs/bending_spoons_annual_2024_2025.json` (new): organic growth 2024/2025, subscription shares, equity
  compensation, operating and investing cash-flow lines, interest paid, the 2025 pro forma revenue row and the three
  purchase prices, each with document, printed page(s) in the 424B4 and the F-1, section, passage and the regex the
  check uses; documents with SHA-256 of the uncompressed files. Sources: the sec.gov copies in `data/v3_inputs/raw/`
  (the GLM bundle texts, used first, are recorded as provenance only).
- `notes/case_bending_spoons_f1_extract.md`: the "not in the documents read" line now points to the figures file for
  2023-25 cash-flow lines; "Not re-verified: the pro forma statements" -> re-verified against the sec.gov 424B4
  (p. 143; F-1 p. 142; prices p. 141) (DS-69, GLM-F2).
- `notes/acquirer_notes.md` section 4 (DS-65): Table 3's before-interest values; round-1 after-interest values marked
  superseded and kept for E7. This file is under the engine's change-control lock: recorded in `engine/CHANGELOG.md`
  and re-accepted with `python3 engine/tools/check_sync.py --accept` (engine re-checked: no source or test uses these
  numbers; only that file's hash changed in `engine/src/autofrontier/NOTES_LOCK.json`).
- Regenerated outputs: `notes/calibration_results.json` (adds `r3`), `paper1/macros.tex`, `paper1/claim_checks.txt`,
  `paper1/abstract_plain.txt`, `paper1/tab_estimands_v3.tex`, `sections/tables/acquired_macros.tex`,
  `part2/tables/acquirer_macros.tex` (additions only), `sections/tables/tab_estimands_v3.tex`, `notes/inference_v3.md`,
  `notes/paper_stats.json`, `notes/gap_decomposition.json` (meta only), `notes/verify_theory_output.txt`,
  `sections/tables/tab_stress.tex`, `paper1/stress_macros.tex`, `figures/fig_stress.pdf`.

## New checks

- verify_theory.py: 15l, 15m, 15n, 15o, 15p, 29a, 29b, 29c, 29d, 29e (191 -> 201 checks).
- verify_part2_acquirer.py: I1-I8 (82 -> 90 checks).
- paper1_macros.py CLAIMS (+11): GPT-M1 steepest slope below one and below the approximation; GPT-M2 period cash above
  PV; GPT-M4 five-year owner; GLM-M5 truncated ratio above one; GPT-4 exact recurrence leaves the printed central numbers
  and dates; GPT-9 net below durable; GLM-F1 shape (two entries); GLM-F5 family dependence; GPT-14 MC error; GLM-M11.
- mc_report_tex.py: consistency of the draws file with the JSON; the stress test's own reproduction flag and all 82 of its checks; the S9 statements about ST-4 (fails narrowly under central execution, clearly over the box) and ST-5 (threshold between the central and fast change capacity).

## Not done (and why)

- GLM-M9 optional forward-pairing variant (g_{t+1} + m_t) of Table S4: author decision pending ("y (variant)"); the
  wording fix is the editor's.
- GPT-16 leave-one-firm sensitivity for the cone cells and P95 changes (optional, author decision); the anchor's
  leave-one-firm range already exists (`\AncLooLo`/`\AncLooHi`).
- GLM-10 / GLM-11 optional dispersion and stock-constrained fast-case runs; GLM-M16 optional delta_M sensitivity.
- GLM-M17 (unsalted CIK digest): options a-c await the author.
- `data/tasks/params.yaml` carries no entry for the composite no-review rate u_rev (its two components are graded as
  measurements in `params_reliability.yaml`), so there was no class to change there; `params.yaml`'s c_c range
  [0.01, 0.20] (2025 prices, successful-run basis) is unchanged because engine test_regression ties it to
  calibrate_horizons.py CC, which is unchanged; the per-completed-process low end lives in `r3.compute_credible`.
  (Superseded 3 Nov: one range, [0.012, 0.60], in CC, params.yaml and `r3.compute_credible`; see the last section.)

## Independent audit of round 3 (3 Nov): code changes

- code/mc_report_tex.py (F1): asserts that the stored 2025 compute-share range equals kappa_2025 x s_L at the box's ends;
  prints that range (0.5 to 23%) and the scenario range read from paper1/macros.tex in the Table S18 note; new macros
  \StCcBoxMin, \StCcBoxMax, \StKappaLo, \StKappaHi, \StSLLo, \StSLHi, \StGstarCcRho (Spearman of G* with the 2025 share
  over the LHS draws, 0.93) and \StOtherCcRho (largest |Spearman| of the other per-draw quantities, 0.02; asserted < 0.05);
  figure legend wording. Stored MC outputs unchanged; no rerun.
- code/paper1_macros.py (F2): \FamBNAnchor = family size + 1 (15).

## Compute-share units fix (3 Nov 2026; `notes/r3_compute_fix.md`)

The floor of the compute share at 2025 prices used kappa (compute per dollar of labor replaced, 0.02 per completed task)
as c_c itself; c_c = s_L x kappa = 0.60 x 0.02 = 0.012. One range for c_c at 2025 prices everywhere: 0.012 to the value
test, s_L = 0.60.

| Macro | Old | New |
|---|---|---|
| `\CcLo` | 2 | 1.2 (one decimal) |
| `\GstarCcLo` | 29 | 28 |
| `\GstarAccCcLo` | 24 | 23 |
| `\CcLoRuns` | 1 | 0.6 (one decimal) |
| `\KappaLo`, `\KappaLoRuns`, `\CcLaborShare` | new | 2, 1, 60 |

- `code/calibrate_horizons.py`: `KAPPA_LO_SUCCESSFUL_RUNS`, `METR_SUCCESS_RATE`, `KAPPA_LO`, `KAPPA_HI` beside `CC_PATH`;
  `CC['prices2025']` bounds (0.01, 0.20) -> s_L x [0.02, 1.0] = (0.012, 0.60); `cc_sensitivity` adds 0.006 and 0.012
  (three-decimal keys only where two would merge points); `r2.compute_range` adds `lo`, `G_lo` at the new floor;
  `r3.compute_credible` in revenue units with its kappa inputs and asserts. Tables unchanged (byte-identical).
- `code/data_part2/08_params.py` -> `data/tasks/params.yaml` (regenerated; the script reproduced the committed file byte for
  byte first): `c_c_compute_share.range` [0.012, 0.6], `path.kappa_2025_range` [0.02, 1.0], source and note text,
  `part1_ceiling.meta.one_at_a_time_threshold_range.cc` [0.2349, 0.7171].
- `code/mc_claims.py` v1.1: kappa_2025 0.02-1.0 log-uniform in path mode (from the executed calibration), `cc_2025` from
  `CC['prices2025']` in bounds mode; `dim_unit`; `law_label`; Sobol 95% intervals for factors and groups (`sobol.ci`);
  `--compare-to` (block `seed_comparison`); `draws_lhs.csv` written by the script; S2 quote from the macros;
  reproduction checks 82 -> 87.
- `code/mc_report_tex.py`: Table S18 note from the JSON (stored run: unchanged wording, scenario range now 1.2 to 60);
  `\StSobol*Lo/Hi` (6 new, from the stored run) and `\StSeedTwo*` (when `<MC_DIR>/seed2` exists); figure axes widen only
  if needed (stored figure byte-identical); `MC_ALLOW_SMALL_N` for smoke tests.
- `code/verify_theory.py` 20h: `CC_BOUNDS` (0.02, 0.60) -> s_L x kappa = (0.012, 0.60), asserts c_c = s_L x kappa
  against the calibration record (201/201 pass).
- `code/paper1_macros.py`: CLAIMS +2 (75 -> 77, all pass).
- Regenerated: `notes/calibration_results.json`, `paper1/macros.tex`, `paper1/abstract_plain.txt`,
  `paper1/claim_checks.txt`, `paper1/stress_macros.tex`, `sections/tables/tab_stress.tex`, `notes/verify_theory_output.txt`,
  `paper1/paper1.pdf`, `paper1/supplement.pdf`.
- `code/REPLICATION_README.md`, `notes/mc_claims_method.md`: the new law, intervals, seeds and CSV.
