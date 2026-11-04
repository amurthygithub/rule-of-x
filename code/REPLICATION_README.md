# Replication package

Paper: *The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation*, by Akshaya Bangalore Sreenivasa Murthy.

This package regenerates every table and figure in the paper from SEC XBRL data. Paper 1's own scripts read nothing but the SEC extract and the other files shipped in `data/`; the third-party datasets used by Paper 2 and the engine are not redistributed and are fetched by `code/fetch_raw_data.py` (section Running).

## Contents

| Path | What it is |
|---|---|
| `code/retrieval_browser.js` | The browser script that retrieved the data on 28 and 29 October 2026 (data.sec.gov companyfacts API). |
| `code/fetch_companyfacts.py` | An equivalent Python retrieval script. |
| `code/build_panel_v2.py` | Builds the firm-year panel with every item as first reported. |
| `code/estimate_frontier.py` | Produces the descriptive table and the within-firm results. |
| `code/estimate_revised.py` | Produces the frontier statistics, robustness checks and empirical figures. |
| `code/decompose_gap.py` | The first version's (v2) decomposition of the gap to the frontier by cost line, kept as the v2 reproduction reference of `estimate_organic.py`; the paper's decomposition is the v3 one of `estimate_v3.py`. |
| `code/estimate_organic.py` | The two estimands, observed scores (E1) and the organic frontier (E2): Table `tab:estimands`, `notes/empirics_organic.json`, `notes/estimand_notes.md` and the calibration anchor inputs `notes/calibration_anchor_E2.json`, which `calibrate_horizons.py` reads. |
| `code/calibrate_horizons.py` | Runs the firm-by-firm inversion and the horizon calibration. |
| `code/paper_stats.py` | Computes the statistics quoted only in the text (on the audited sample, `data/panel_v3.csv`). |
| `code/mc_claims.py`, `code/mc_report_tex.py` | The joint-parameter stress test of the headline claims (Latin-hypercube draws, box corners and a vertex search over every stated range; Sobol indices), and the script that turns its stored output (`notes/mc_results_2026-11-03/`) into Table `tab:stress`, `paper1/stress_macros.tex` and `figures/fig_stress.pdf`. |
| `data/v3_inputs/raw/bending_spoons_*.htm.gz`, `bsp_ex99-*.htm.gz`, `data/v3_inputs/bending_spoons_annual_2024_2025.json` | The case study's filings as downloaded from sec.gov (gzip'd HTML; SHA-256 of the documents in `data/v3_inputs/README_retrieval.md` section 5) and the figures read from them with page references; `code/verify_part2_acquirer.py` checks each figure against the decompressed document. |
| `code/verify_theory.py` | Runs the symbolic and numerical checks of every closed form in the model. |
| `code/frontier_figures.py` | Draws the theory figures. |
| `code/exclusions.py`, `code/purge_excluded.py` | The registrants excluded at the author's request, identified by the SHA-256 digest of the CIK, and the script that removes them from the data files and checks that none is left. The fetch and panel scripts skip them. |
| `data/companyfacts_ciks.txt` | The 661 registrants retrieved and kept (662 were retrieved; one was removed at the author's request). |
| `data/sic_universe.json` | The EDGAR registrants with SIC codes 7370 to 7374, given as [sic, cik, name, state]. |
| `data/companyfacts_extract.json` | The retrieved facts: 240,318 facts for 35 US-GAAP elements. |
| `data/panel_v2_all.csv`, `data/panel_broad.csv`, `data/panel.csv` | All firm-years, the broad sample (SIC 7370 to 7374) and the core sample (SIC 7372). |
| `code/build_panel_v3.py` | The audited sample (panel v3): sample rules R1 to R5 of `notes/sample_audit.md` applied to the v2 panel, and capitalized software read from the cash-flow statement where the XBRL elements give 0 (C1). |
| `code/estimate_v3.py`, `code/estimate_v3_report.py` | Estimates on the audited sample with exact quantile regression and a seeded firm-cluster bootstrap (999 replications); the report module writes the v3 tables and notes and is run by `estimate_v3.py`. |
| `data/panel_v3_all.csv`, `data/panel_v3_core_full.csv`, `data/panel_v3.csv` | The v2 panel with the audit columns, the v2 core sample with the reason for each exclusion, and the v3 core sample. The acquisition flag of rule R4 is the column `acq_flag_v3`; `acq_flag` is the v2 flag, kept for the audit, and the estimation code replaces it by `acq_flag_v3` when it reads the panel (a reuse that takes `acq_flag` gets 15 anchor firm-years instead of 14). `cap_sw_source` says whether capitalized software is the XBRL value or the filing's (`cap_sw_xbrl` keeps the XBRL value). |
| `data/v3_inputs/` | Inputs of the sample rules and the cash-score bridge from SEC data retrieved on 29 October 2026 (provenance and transfer hashes in `data/v3_inputs/README_retrieval.md`): `related_party.json` (R3), `acquiree_revenue.json` (R4c), `listing_status.json` (R5), `cash_interest_taxes.json` (bridge), `business_descriptions.json` (R2: the business descriptions of all core registrants, merged by `code/audit/r2_descriptions.py` from `business_descriptions_named.json`, the 16 named firms retrieved on 29 October, and `raw/business_descriptions_raw_2026-11-03.json`, the others retrieved on 3 November), `business_class_reader_a.csv` and `business_class_reader_b.csv` (R2 sensitivity: two independent readings of the descriptions), `capitalized_software_filings.json` (C1, from the cash-flow statements read on 3 November; `code/audit/capsw_scan_parse.py`), `captive_verified.csv` (R3, filing text), and the originals in `raw/`. The XBRL inputs come from SEC frames, which keep the latest filed value. |
| `code/regenerate_all.sh` | Every stage of the three papers in dependency order (`--list`, `--from`, `--to`, `--keep-going`, `--skip-raw`); the header lists what each stage reads. |
| `code/fetch_raw_data.py`, `data/raw/` | The third-party data of Paper 2 and the engine (not redistributed): the script fetches each source from its official address and verifies every file against `data/raw/CHECKSUMS.sha256`; `--check` verifies offline. Sources and terms: `data/raw/README.md`. |
| `code/audit/`, `notes/data_audit/` | The data audit of 3 November 2026: a seeded sample of 40 firm-years compared with the face statements of the filings (`data_audit_compare.py`), the scan of the cash-flow statements for capitalized software (`capsw_scan_parse.py`) and the merge of the R2 descriptions (`r2_descriptions.py`). |

## Running

Requirements: Python 3.11 or later with the packages pinned in `requirements.txt` (`python3 -m pip install -r requirements.txt`). For byte-identical figures use `requirements-lock.txt`, the exact versions of every package in the clean Python 3.13.18 environment that produced the committed outputs; other versions of indirect dependencies (fonttools, pillow) can shift figure layout by a fraction of a point.

The whole build runs in dependency order with `code/regenerate_all.sh` (stages: `bash code/regenerate_all.sh --list`; logs in `build_logs/`). Three of its stages read third-party files in `data/raw/`, which the repository does not redistribute: `params` (`code/data_part2/08_params.py`, METR's run data), `backtest` (`code/validation/backtest.py`, GPTs-are-GPTs, the BLS OEWS and SOC files and O*NET job zones) and `playbook` (`code/playbook/run_archetypes.py`, O*NET task statements). Before its first stage, the script checks that the folders the selected stages read are present and match `data/raw/CHECKSUMS.sha256`, and stops naming `code/fetch_raw_data.py` if they are not. On a fresh clone, either fetch them first or skip those stages:

```
python3 code/fetch_raw_data.py            # fetch and verify the third-party data (data/raw/README.md; some hosts need a browser)
bash code/regenerate_all.sh               # every stage
bash code/regenerate_all.sh --skip-raw    # every stage but params, backtest and playbook, whose committed outputs are kept
```

Paper 1's own stages (`panel`, `empirics`, `empirics_v3`, `calibrate`, `stress_report`, `paper1_macros`, `verify_theory`, `latex_p1`) read nothing in `data/raw/`. Besides the SEC extract and `data/v3_inputs/` they read shipped files written by other stages: `data/tasks/params.yaml` (calibration and macros; stage `params`), the lever table of Section `sec:levers-position` (`sections/tables/levers_position_macros.tex`, `tab_levers_position.tex`, `notes/playbook_results.json`; stage `playbook`), `sections/tables/acquired_macros.tex` (`code/verify_part2_acquirer.py`), the stored stress test and `paper1/spec_macros.tex` (`code/spec_curve.py`, run separately). By hand, from the repository root, in the pipeline's order:

```
python3 code/build_panel_v2.py        # data/panel*.csv, notes/panel_build_log.txt
python3 code/build_panel_v3.py        # data/panel_v3*.csv, notes/panel_v3_build.json (audited sample)
python3 code/estimate_frontier.py     # tab_desc.tex, fig_scores_time.pdf, notes/empirics_results.json
python3 code/estimate_revised.py      # remaining empirical tables and figures, notes/empirics_revised.json (several minutes: firm-cluster bootstrap)
python3 code/decompose_gap.py         # sections/tables/tab_gap.tex, notes/gap_decomposition.json
python3 code/paper_stats.py           # notes/paper_stats.json (audited sample)
python3 code/estimate_organic.py      # tab_estimands.tex, notes/empirics_organic.json, notes/estimand_notes.md, notes/calibration_anchor_E2.json (about 30 minutes)
V3_PANEL=v2 python3 code/estimate_v3.py   # notes/empirics_v2_exact.json: the v3 estimators on the v2 sample (about 15 minutes on two cores)
python3 code/estimate_v3.py           # notes/empirics_v3.json, notes/calibration_anchor_v3.json, notes/frontier_slope_v3.json, notes/bootstrap_draws_v3.npz,
                                      # tab_estimands_v3, tab_contrasts_v3, tab_grid_v3, tab_yearly_v3, tab_bridge_v3, notes/inference_v3.md, notes/sample_audit.md (about 35 minutes)
python3 code/calibrate_horizons.py    # sections/tables/tab_calib.tex, notes/calibration_results.json (reads notes/calibration_anchor_v3.json)
python3 code/mc_report_tex.py         # sections/tables/tab_stress.tex, paper1/stress_macros.tex, figures/fig_stress.pdf (from the stored stress test)
python3 code/playbook/run_archetypes.py   # the lever table of Section sec:levers-position (needs data/raw/onet_31_0; or keep the committed outputs)
python3 code/verify_part2_acquirer.py # sections/tables/acquired_macros.tex (the acquired-growth figures)
python3 code/paper1_macros.py         # paper1/macros.tex; stops if any sentence of the text is no longer supported (CLAIMS)
python3 code/verify_theory.py > notes/verify_theory_output.txt   # after paper1_macros.py: its [text] checks read paper1/macros.tex
bash code/build_paper1.sh             # paper1/paper1.pdf and paper1/supplement.pdf
```

`V3_REPORT_ONLY=1 python3 code/estimate_v3.py` rewrites the v3 tables and notes from `notes/empirics_v3.json` without re-estimating. `code/audit/r2_descriptions.py` (which merged `data/v3_inputs/business_descriptions.json` from the retrieved descriptions) and `code/frontier_figures.py` (the theory figures `figures/fig_frontier_tangency.pdf` and `figures/fig_saturation.pdf`) are not pipeline stages; their outputs are shipped.

The stress test itself (`code/mc_claims.py`) is not part of the regeneration (`code/regenerate_all.sh` formats its committed
output in stage `stress_report`). To reproduce it, run from the repository root

```
python3 code/mc_claims.py --n 10000 --workers 4 --out notes/mc
```

which writes `mc_claims.json`, `mc_claims_report.md` and `draws_lhs.csv` to `notes/mc/` (about 75 seconds on
four cores; seeds 20261102 for the draws and 20261103 for the corners by default, `--seed` to change them). The results that stage
`stress_report` formats are in `notes/mc_results_2026-11-03_1m/`: a million draws per seed (seed 20261102, and the second seed 20261104 in `seed2/`), run on the author's computer on 3 Nov 2026 with the commands of `notes/mc_claims_method.md` section 8a (the per-draw file is gzipped, `draws_lhs.csv.gz`; `run_stress.sh` and `logs/` record how the run was made). `notes/mc_results_2026-11-03/` holds the 10,000-draw run of the same box, from the command above (`--out` aside), after the compute-share fix of 3 Nov 2026. `notes/mc_results_2026-11-02/` holds the earlier run, which predates the
fix (its `draws_lhs.csv` and `amin_points.csv` were taken from its checkpoint for the dashboard). `MC_DIR=notes/mc python3 code/mc_report_tex.py` formats
a new run. A second seed, recorded against the first:
`python3 code/mc_claims.py --n 10000 --seed 20261104 --workers 4 --out notes/mc/seed2 --compare-to notes/mc`;
`mc_report_tex.py` then also writes the `\StSeedTwo*` macros (`MC_SEED2_DIR` overrides `<MC_DIR>/seed2`).
The method is in `notes/mc_claims_method.md`.

The business dashboard "Rule of 40 and AI: business guide" (a Claude dashboard; 3 Nov 2026) reads only committed outputs: `python3 code/biz_dashboard_data.py` writes its data files to `notes/mc_results_2026-11-03_1m/dashboard/` from the million-draw run, `notes/playbook_results.json` and the paper's macros (every number quoted in its text is a row of `facts.csv`, with its macro and section), and `python3 code/biz_dashboard_page.py` builds `index.html` there from `index.src.html`, stopping if a number in the text has no row in `facts.csv`. It runs no model.

`calibrate_horizons.py` runs after `estimate_v3.py`, whose anchor (`notes/calibration_anchor_v3.json`) it reads; `estimate_v3.py` runs after `build_panel_v3.py` and `estimate_organic.py` (it reads `notes/empirics_organic.json`), and its v2 run comes first, because the v3 notes compare against it. On a first run from an empty `notes/` folder, `estimate_organic.py` skips its regression check against `notes/calibration_results.json` or `notes/empirics_v2_exact.json` (neither exists yet) and says so in the anchor file; running it again after `calibrate_horizons.py` performs the check (`code/regenerate_all.sh` does this in stage `calibrate`). `paper1_macros.py` runs after `run_archetypes.py`, `mc_report_tex.py` and `verify_part2_acquirer.py`, whose outputs it reads; `mc_report_tex.py` and `verify_part2_acquirer.py` also read `paper1/macros.tex` of the previous run (an assertion on the compute-share range, and the expansion of the sentences they check), so after a change that moves those numbers rerun them, and then `paper1_macros.py`, once more (`code/regenerate_all.sh` does this automatically).

Run the scripts in this order: `estimate_revised.py` overwrites two figures and one table that `estimate_frontier.py` also writes, and `estimate_frontier.py` writes four further tables (`tab_frontier`, `tab_qreg`, `tab_envelope`, `tab_organic`) from an earlier draft that the paper no longer uses. Bootstrap seeds are fixed, so the numbers match the paper exactly when run on the distributed extract.

To retrieve the SEC data again, run `python3 code/fetch_companyfacts.py "Your Name your.email@example.com"`. The SEC requires a User-Agent with contact details. Registrants excluded in `code/exclusions.py` are skipped. Facts filed after 29 October 2026 will make a new extract differ slightly from the distributed one.

## Machine-checked proofs of the static model (`formal/`)

`formal/` is a Lean 4 project that formalizes the statements of Sections 3.1 to 3.5 of Paper 1 (the static model) and checks their proofs (Supplement Section `supp:formal`; `formal/README.md` maps every part of every statement to its Lean theorems and states each difference of form). It is not a stage of `code/regenerate_all.sh`, because it needs the Lean toolchain rather than Python.

```bash
# Lean 4.35.0 (https://github.com/leanprover/lean4/releases/tag/v4.35.0, or elan with formal/lean-toolchain) on PATH
cd formal
lake build                 # Mathlib v4.35.0 and the library RuleOfX; prints the axioms of every main theorem
lake build RuleOfXChecks   # the audit's instances: the theorems at the paper's illustrative values and for a spend path with a jump
```

Without a Mathlib cache (`lake exe cache get`), Mathlib is compiled from source: about 2,800 modules, about 50 minutes on 2 cores. Every theorem printed by `formal/RuleOfX/Axioms.lean` must depend only on `propext`, `Classical.choice` and `Quot.sound`; `paper1_macros.py` counts them for the Supplement (`\FormalNThm`).

## License

Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. The code in this package is licensed under the PolyForm Noncommercial License 1.0.0 (LICENSE.md) or, at your option, the PolyForm Internal Use License 1.0.0 (LICENSE-INTERNAL-USE.md), which lets a company run and modify it for its own internal business operations but not distribute it or offer it as a service. The author's own data compilations and documentation are licensed under CC BY-NC-ND 4.0. Any other commercial use requires the author's prior written permission. Third-party data keep their own terms, listed below and in NOTICE.md.

## Data source and terms

The data are public filings retrieved from the U.S. Securities and Exchange Commission's EDGAR XBRL application programming interface.

## Checks of the numerical HJB solution

`code/verify_theory.py` solves the HJB of Proposition 2 by an upwind backward sweep (checks 15g to 15p). Check 15q is
independent of that solver: an admissible constant-spend policy (5% of revenue until the share reaches 40% of the market)
is simulated directly, and its discounted payoff is a lower bound on the value; it exceeds the no-spend value, and the
sweep's value lies above it. A solver that returns the no-spend value for the worked example is therefore wrong for this
problem (see `notes/reviews/paper1_v3/author_reviews/mistral_large_4_high/issue_log.md`, F-6).

