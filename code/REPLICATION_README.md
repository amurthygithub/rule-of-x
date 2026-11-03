# Replication package

Paper: *The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation*, by Akshaya Bangalore Sreenivasa Murthy.

This package regenerates every table and figure in the paper from SEC XBRL data.

## Contents

| Path | What it is |
|---|---|
| `code/retrieval_browser.js` | The browser script that retrieved the data on 28 and 29 October 2026 (data.sec.gov companyfacts API). |
| `code/fetch_companyfacts.py` | An equivalent Python retrieval script. |
| `code/build_panel_v2.py` | Builds the firm-year panel with every item as first reported. |
| `code/estimate_frontier.py` | Produces the descriptive table and the within-firm results. |
| `code/estimate_revised.py` | Produces the frontier statistics, robustness checks and empirical figures. |
| `code/decompose_gap.py` | Decomposes the gap to the frontier by cost line. |
| `code/estimate_organic.py` | The two estimands, observed scores (E1) and the organic frontier (E2): Table `tab:estimands`, `notes/empirics_organic.json`, `notes/estimand_notes.md` and the calibration anchor inputs `notes/calibration_anchor_E2.json`, which `calibrate_horizons.py` reads. |
| `code/calibrate_horizons.py` | Runs the firm-by-firm inversion and the horizon calibration. |
| `code/paper_stats.py` | Computes the statistics quoted only in the text. |
| `code/verify_theory.py` | Runs the symbolic and numerical checks of every closed form in the model. |
| `code/frontier_figures.py` | Draws the theory figures. |
| `code/exclusions.py`, `code/purge_excluded.py` | The registrants excluded at the author's request, identified by the SHA-256 digest of the CIK, and the script that removes them from the data files and checks that none is left. The fetch and panel scripts skip them. |
| `data/companyfacts_ciks.txt` | The 661 registrants retrieved and kept (662 were retrieved; one was removed at the author's request). |
| `data/sic_universe.json` | The EDGAR registrants with SIC codes 7370 to 7374, given as [sic, cik, name, state]. |
| `data/companyfacts_extract.json` | The retrieved facts: 240,318 facts for 35 US-GAAP elements. |
| `data/panel_v2_all.csv`, `data/panel_broad.csv`, `data/panel.csv` | All firm-years, the broad sample (SIC 7370 to 7374) and the core sample (SIC 7372). |
| `code/build_panel_v3.py` | The audited sample (panel v3): sample rules R1 to R5 of `notes/sample_audit.md` applied to the v2 panel. |
| `code/estimate_v3.py`, `code/estimate_v3_report.py` | Estimates on the audited sample with exact quantile regression and a seeded firm-cluster bootstrap (999 replications); the report module writes the v3 tables and notes and is run by `estimate_v3.py`. |
| `data/panel_v3_all.csv`, `data/panel_v3_core_full.csv`, `data/panel_v3.csv` | The v2 panel with the audit columns, the v2 core sample with the reason for each exclusion, and the v3 core sample. |
| `data/v3_inputs/` | Inputs of the sample rules and the cash-score bridge from SEC data retrieved on 29 October 2026 (provenance and transfer hashes in `data/v3_inputs/README_retrieval.md`): `related_party.json` (R3), `acquiree_revenue.json` (R4c), `listing_status.json` (R5), `cash_interest_taxes.json` (bridge), `business_descriptions_named.json` (R2 sensitivity for the 16 named firms only), `captive_verified.csv` (R3, filing text), and the originals in `raw/`. The XBRL inputs come from SEC frames, which keep the latest filed value. |

## Running

Requirements: Python 3.11 or later with numpy, pandas, scipy, statsmodels, matplotlib, sympy and mpmath.

```
cd code
python3 build_panel_v2.py        # data/panel*.csv, notes/panel_build_log.txt
python3 estimate_frontier.py     # tab_desc.tex, fig_scores_time.pdf, notes/empirics_results.json
python3 estimate_revised.py      # remaining empirical tables and figures, notes/empirics_revised.json (several minutes: firm-cluster bootstrap)
python3 decompose_gap.py         # sections/tables/tab_gap.tex, notes/gap_decomposition.json
python3 estimate_organic.py      # tab_estimands.tex, notes/empirics_organic.json, notes/estimand_notes.md, notes/calibration_anchor_E2.json (about 30 minutes)
python3 calibrate_horizons.py    # sections/tables/tab_calib.tex, notes/calibration_results.json (reads notes/calibration_anchor_E2.json)
python3 paper_stats.py           # notes/paper_stats.json
python3 verify_theory.py > ../notes/verify_theory_output.txt
python3 frontier_figures.py      # figures/fig_frontier_tangency.pdf, figures/fig_saturation.pdf
python3 build_panel_v3.py        # data/panel_v3*.csv, notes/panel_v3_build.json (audited sample)
V3_PANEL=v2 python3 estimate_v3.py   # notes/empirics_v2_exact.json: the v3 estimators on the v2 sample (about 15 minutes on two cores)
python3 estimate_v3.py           # notes/empirics_v3.json, notes/calibration_anchor_v3.json, notes/frontier_slope_v3.json, notes/bootstrap_draws_v3.npz,
                                 # tab_estimands_v3, tab_contrasts_v3, tab_grid_v3, tab_yearly_v3, tab_bridge_v3, notes/inference_v3.md, notes/sample_audit.md (about 35 minutes)
```

`estimate_organic.py` must run before `calibrate_horizons.py`, because the calibration reads its anchor file. On a first run from an empty `notes/` folder, `estimate_organic.py` skips its regression check against `notes/calibration_results.json` (which does not exist yet) and says so in the anchor file; running it again after `calibrate_horizons.py` performs the check. `estimate_v3.py` runs after `build_panel_v3.py`, and its v2 run comes first, because the v3 notes compare against it.

Run the scripts in this order: `estimate_revised.py` overwrites two figures and one table that `estimate_frontier.py` also writes, and `estimate_frontier.py` writes four further tables (`tab_frontier`, `tab_qreg`, `tab_envelope`, `tab_organic`) from an earlier draft that the paper no longer uses. Bootstrap seeds are fixed, so the numbers match the paper exactly when run on the distributed extract.

To retrieve the data again, run `python3 fetch_companyfacts.py "Your Name your.email@example.com"`. The SEC requires a User-Agent with contact details. Registrants excluded in `code/exclusions.py` are skipped. Facts filed after 29 October 2026 will make a new extract differ slightly from the distributed one.

## License

Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. The code in this package is licensed under the PolyForm Noncommercial License 1.0.0 (LICENSE.md) or, at your option, the PolyForm Internal Use License 1.0.0 (LICENSE-INTERNAL-USE.md), which lets a company run and modify it for its own internal business operations but not distribute it or offer it as a service. The author's own data compilations and documentation are licensed under CC BY-NC-ND 4.0. Any other commercial use requires the author's prior written permission. Third-party data keep their own terms, listed below and in NOTICE.md.

## Data source and terms

The data are public filings retrieved from the U.S. Securities and Exchange Commission's EDGAR XBRL application programming interface.
