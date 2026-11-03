# Data download requests (Part II data agent)

These files are only available from hosts the shell cannot reach (onetcenter.org, bls.gov, huggingface.co, metr.org). Please download each through a browser and save it, unchanged and unzipped where noted, under the folder given. The build scripts in `code/data_part2/` look for exactly these paths and pick them up automatically; nothing else needs to be done after saving.

**Status (29 Oct 2026, after delivery):** received and used: O*NET 31.0 (as the MySQL archive db_31_0_mysql.zip, converted by `code/data_part2/00_onet_mysql_to_csv.py`), OEWS May 2025 (oesm25nat.zip, oesm25in4.zip), and the AEI files aei_claude_ai_2026-06-26.csv, task_pct_v2.csv and onet_task_statements.csv. Still outstanding (all OPTIONAL): the verbatim AEI release_2026_06_26/data_documentation.md (only a paraphrased summary was available), the AEI 1P API files, METR's published TH1.1 YAML files, the ECEC PDF, SEC companyfacts for non-software industries and BLS JOLTS hires rates. Rebuild with `code/data_part2/build_all.sh`.

Status key: **REQUIRED** means a contract file stays partial or missing without it; **OPTIONAL** means it adds a cross-check or a richer column.

## 1. O*NET 31.0 database (CC BY 4.0), save to `data/raw/onet_31_0/`

Source page: https://www.onetcenter.org/database.html (lists release 31.0; "Site updated October 6, 2026"). License: CC BY 4.0, credit "O*NET 31.0 Database, U.S. Department of Labor, Employment and Training Administration (USDOL/ETA)".

Individual CSV files (keep the file names as served):

| priority | file | URL | used for |
|---|---|---|---|
| REQUIRED | task_statements.csv | https://www.onetcenter.org/dl_files/database/db_31_0_csv/task_statements.csv | task IDs, task type (core/supplemental) |
| REQUIRED | task_ratings.csv | https://www.onetcenter.org/dl_files/database/db_31_0_csv/task_ratings.csv | importance (IM), relevance (RT), frequency categories (FT) for time shares |
| REQUIRED | task_categories.csv | https://www.onetcenter.org/dl_files/database/db_31_0_csv/task_categories.csv | meaning of the 7 frequency categories |
| REQUIRED | tasks_to_dwas.csv | https://www.onetcenter.org/dl_files/database/db_31_0_csv/tasks_to_dwas.csv | task to DWA links |
| REQUIRED | gwas_to_iwas_to_dwas.csv | https://www.onetcenter.org/dl_files/database/db_31_0_csv/gwas_to_iwas_to_dwas.csv | DWA titles and the DWA, IWA, GWA hierarchy |
| REQUIRED | occupation_data.csv | https://www.onetcenter.org/dl_files/database/db_31_0_csv/occupation_data.csv | O*NET-SOC titles |
| REQUIRED | content_model_reference.csv | https://www.onetcenter.org/dl_files/database/db_31_0_csv/content_model_reference.csv | GWA titles |
| OPTIONAL | gwas_to_iwas.csv | https://www.onetcenter.org/dl_files/database/db_31_0_csv/gwas_to_iwas.csv | cross-check of the hierarchy |
| OPTIONAL | work_activities.csv | https://www.onetcenter.org/dl_files/database/db_31_0_csv/work_activities.csv | GWA importance by occupation (fallback time shares) |
| OPTIONAL | work_context.csv | https://www.onetcenter.org/dl_files/database/db_31_0_csv/work_context.csv | on-site and physical context (cross-check of physical_share) |
| OPTIONAL | work_context_categories.csv | https://www.onetcenter.org/dl_files/database/db_31_0_csv/work_context_categories.csv | work context category labels |
| OPTIONAL | scales_reference.csv | https://www.onetcenter.org/dl_files/database/db_31_0_csv/scales_reference.csv | scale definitions |
| OPTIONAL | job_zones.csv | https://www.onetcenter.org/dl_files/database/db_31_0_csv/job_zones.csv | preparation level (proxy for task difficulty) |

Alternative, if the per-file links fail: the full archive https://www.onetcenter.org/dl_files/database/db_31_0_excel.zip (save as `data/raw/onet_31_0/db_31_0_excel.zip`; the scripts read .xlsx members if the CSVs are absent).

Please also save the release notes page as PDF or HTML if convenient (OPTIONAL): https://www.onetcenter.org/dictionary/31.0/nt/appendix_updates.html, to record the 31.0 release date.

## 2. BLS OEWS May 2025 (U.S. government work, public domain), save to `data/raw/bls_oews_2025/`

May 2025 is the latest OEWS reference period (the May 2025 industry and state pages were last modified 15 May 2026).

| priority | file | URL | used for |
|---|---|---|---|
| REQUIRED | oesm25in4.zip | https://www.bls.gov/oes/special-requests/oesm25in4.zip | national industry-specific estimates (sector, 3-, 4-, 5/6-digit NAICS), and cross-industry rows; feeds industry_staffing.csv and occupations.csv |
| REQUIRED | oesm25nat.zip | https://www.bls.gov/oes/special-requests/oesm25nat.zip | national cross-industry estimates; feeds occupations.csv |

Note on oesm25nat.zip: the industry (oesm25in4.zip, on https://www.bls.gov/oes/2025/may/oessrci.htm) and state (oesm25st.zip, on https://www.bls.gov/oes/2025/may/oessrcst.htm) links were read from the BLS pages; the national file name follows the same BLS pattern (oesm23nat.zip, oesm24nat.zip) but I could not open the national page to confirm it. If that link fails, the national file is linked from https://www.bls.gov/oes/tables.htm ("National", "XLSX"), or use the all-data archive https://www.bls.gov/oes/special-requests/oesm25all.zip.

Until these arrive, occupations.csv is built from the May 2021 national file redistributed in the GPTs-are-GPTs repository (vintage flagged in the file).

## 3. Anthropic Economic Index (data CC BY, code MIT), save to `data/raw/anthropic_aei/` keeping the release sub-folders

Dataset: https://huggingface.co/datasets/Anthropic/EconomicIndex . Direct-download form: `https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/main/<path>`.

| priority | path inside the dataset (save under the same relative path) | direct URL | used for |
|---|---|---|---|
| REQUIRED | release_2026_06_26/data/aei_claude_ai_2026-06-26.csv (219 MB) | https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/main/release_2026_06_26/data/aei_claude_ai_2026-06-26.csv | latest usage shares at task, DWA, IWA and GWA level; human_only_time_mean (hours) per task for est_task_hours |
| REQUIRED | release_2026_06_26/data_documentation.md | https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/main/release_2026_06_26/data_documentation.md | schema and metric definitions for the above |
| REQUIRED | release_2025_03_27/task_pct_v2.csv | https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/main/release_2025_03_27/task_pct_v2.csv | task-level usage share (Claude 3.7 Sonnet era), matched to O*NET task text |
| REQUIRED | release_2025_03_27/onet_task_statements.csv | https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/main/release_2025_03_27/onet_task_statements.csv | task text to Task ID for the match above |
| OPTIONAL | release_2025_03_27/automation_vs_augmentation_by_task.csv | https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/main/release_2025_03_27/automation_vs_augmentation_by_task.csv | directive (automation) vs augmentation split per task |
| OPTIONAL | release_2026_06_26/data/aei_1p_api_2026-06-26.csv (77 MB) | https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/main/release_2026_06_26/data/aei_1p_api_2026-06-26.csv | API (enterprise) usage shares by activity |
| OPTIONAL | release_2025_09_15/data/intermediate/aei_raw_1p_api_2025-08-04_to_2025-08-11.csv | https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/main/release_2025_09_15/data/intermediate/aei_raw_1p_api_2025-08-04_to_2025-08-11.csv | onet_task::cost and token facets (relative API cost per task) for AI cost parameters |
| OPTIONAL | release_2025_09_15/data_documentation.md | https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/main/release_2025_09_15/data_documentation.md | schema for the above |

## 4. METR Time Horizon 1.1 published results (OPTIONAL cross-check), save to `data/raw/metr_th11/`

The run-level data are already cloned from GitHub (METR/eval-analysis-public), and the capability path is fitted from them by script. The published model-level estimates would let me check the refit:

- https://metr.org/assets/benchmark_results_1_1.yaml
- https://metr.org/assets/task_results_1_1.yaml
- the Time Horizon 1.1 post, saved as PDF or HTML: https://metr.org/blog/2026-1-29-time-horizon-1-1/

## 5. BLS Employer Costs for Employee Compensation, June 2026 (OPTIONAL, for checksum only), save to `data/raw/bls_ecec/`

Values were read from the archived release page; a saved copy lets the log carry a checksum.

- https://www.bls.gov/news.release/archives/ecec_09092026.pdf (if absent, save https://www.bls.gov/news.release/archives/ecec_09092026.htm as HTML)

## 6. Non-software industry cost structure (OPTIONAL, for industry_function_shares.csv beyond SIC 7370-7374)

data.sec.gov is not reachable from the shell. If the browser route used for Part I (`code/retrieval_browser.js`, `code/fetch_companyfacts.py`) can be run again, fetch companyfacts for the registrants in SIC groups the engine should cover (for example 2834 pharma, 3570-3579 computer hardware, 4813 telecom, 5961 e-commerce, 6141/6199 financial services, 6311-6411 insurance, 7389 business services, 8000-8099 health services). Save the JSON extract as `data/raw/sec_companyfacts_other/companyfacts_extract.json` in the same format as `data/companyfacts_extract.json`; `05_function_priors.py` needs a one-line path change to read it.

## 7. BLS JOLTS hires rates by industry (OPTIONAL, for the hire-to-retire volume in processes.csv)

- JOLTS landing page https://www.bls.gov/jlt/ (not opened from this session; please take the latest annual hires-rate table by industry from there). Save to `data/raw/bls_jolts/`.

## 8. Backtest of Part II (spec Section 24.1; requested by the empirical-validation agent, 29 Oct 2026)

**Status (29 Oct 2026, later the same day):** received and used:
- `oesm21in4.zip`, in `data/raw/bls_oews_2021/`;
- `soc_2010_to_2018_crosswalk.xlsx`, in `data/raw/bls_soc/`;
- `oesm19nat.zip` and `oesm20nat.zip`, in `data/raw/bls_oews_2019/` and `data/raw/bls_oews_2020/`.

`oesm16nat.zip` is no longer needed. The coordinator verified the 2016 cross-section against BLS's May 2016 national tables in a browser (https://www.bls.gov/oes/2016/may/oes_nat.htm, 29 Oct 2026; 737 of 737 occupations match; sum of employment 133,977,150 and of mean wages 43,494,840 in both).

Still open: hours by occupation (CPS or ACS), and BLS's table of members for the hybrid May 2019 and 2020 aggregates. The hybrid table would recover the occupations folded into the 29 hybrid aggregates for the 2016-19 and 2019-21 comparisons.

`code/validation/backtest.py` runs on local files only. These files would extend it; none of the URLs below was opened from the shell (bls.gov is not reachable from it). The OEWS links follow the pattern of the May 2025 files that were received (`special-requests/oesmYYnat.zip`, `oesmYYin4.zip`). U.S. government works, public domain.

| priority | file | URL | save to | what it adds |
|---|---|---|---|---|
| REQUIRED for the occupation x industry test | oesm21in4.zip (OEWS May 2021, national industry-specific: sector, 3-, 4- and 5/6-digit NAICS) | https://www.bls.gov/oes/special-requests/oesm21in4.zip | `data/raw/bls_oews_2021/` | Occupation x 4-digit NAICS cells for May 2021, to pair with `oesm25in4.zip`. Industry fixed effects absorb industry demand shocks (the software and tech-labor correction, rate-sensitive lending, the COVID rebound in leisure and hospitality), which are the main confounders of the occupation-level test; occupation fixed effects absorb occupation-wide trends; the cost-crossover term then varies within an occupation through industry wages. It also allows the firm-level function mix to be scored with 2021 rather than 2025 staffing. |
| OPTIONAL (placebo) | oesm19nat.zip and oesm20nat.zip (OEWS May 2019 and May 2020 national) | https://www.bls.gov/oes/special-requests/oesm19nat.zip ; https://www.bls.gov/oes/special-requests/oesm20nat.zip | `data/raw/bls_oews_2019/`, `data/raw/bls_oews_2020/` | A pre-period ending before COVID (2016 to 2019) and a 2019 to 2021 trend control, as the spec asks. Both vintages use the hybrid SOC 2010/2018 structure, so the crosswalk below is needed too. |
| OPTIONAL (verification) | oesm16nat.zip (OEWS May 2016 national) | https://www.bls.gov/oes/special-requests/oesm16nat.zip | `data/raw/bls_oews_2016/` | Confirms the vintage of `gpts_are_gpts/repo/data/autoScores.csv`, whose `tot_emp` and `a_mean` the backtest uses as a 2016 cross-section. The repository does not document the vintage; values are consistent with May 2016 but this is not verified against the official file. |
| OPTIONAL (crosswalk) | soc_2010_to_2018_crosswalk.xlsx (BLS SOC 2010 to SOC 2018) | https://www.bls.gov/soc/2018/soc_2010_to_2018_crosswalk.xlsx | `data/raw/bls_soc/` | Replaces the identity-on-unchanged-codes rule of the pre-period placebo (639 occupations, 78% of 2021 employment) with the official many-to-many crosswalk, recovering renumbered occupations such as software developers. |
| OPTIONAL (hours) | none in OEWS; CPS or ACS hours by occupation would be needed | (not specified) | | OEWS counts jobs, not hours; spec 24.1 mentions hours, which the backtest cannot test. |

**Status, 29 Oct 2026, 09:52:** received oesm21in4.zip, soc_2010_to_2018_crosswalk.xlsx and Damodaran fundgrEB.xls (with margin.xls, wacc.xls and roe.xls at 09:22). roc.xls is now optional, because fundgrEB.xls carries after-tax ROC. Still optional: oesm16nat.zip, which verifies the vintage of the 2016 placebo cross-section; oesm19nat.zip and oesm20nat.zip, for a pre-COVID placebo; the verbatim AEI data_documentation.md for release_2026_06_26.

**Status, 29 Oct 2026, 10:05:** received oesm19nat.zip and oesm20nat.zip. AEI release_2026_06_26/data_documentation.md was retrieved verbatim through the author's built-in browser from the Hugging Face raw URL: 7,397 bytes, SHA-256 1a01eeb7d34250b192aa9c906098bea1db971644e6bdb04497d87b7a4ed141a5, saved to data/raw/anthropic_aei/release_2026_06_26/. It confirms that human_only_time_mean is in hours and human_with_ai_time_mean in minutes, that values are rounded to two decimals, and that a missing row means the cell was not published, not that it is zero. 03_activities.py already follows all three. The author asked that future downloads use the browser where possible.

## 9. Damodaran industry datasets for non-software priors (spec Section 24.10; data agent, 29 Oct 2026)

Received and used: margin.xls, wacc.xls, roe.xls (29 Oct 2026, 09:22) and fundgrEB.xls (09:52), all dated 5 January 2026, in `data/raw/damodaran_2026/`. All items below are **OPTIONAL**: `code/data_part2/11_nonsoftware_priors.py` runs without them and picks each one up automatically from `data/raw/damodaran_2026/` (the author's `~/workspace/rule-of-x-paper/data_raw/damodaran_2026/`). Save each file unchanged under the name shown. The spreadsheet URLs are the download links on the pages named (pages read 29 Oct 2026; the files themselves were not opened from this session). No license or redistribution terms were found on any of these pages, so the raw files should not be shipped in the replication package (notes/data_sources_nonsoftware.md, Section 2).

| priority | file | URL | save to | reason |
|---|---|---|---|---|
| SUPERSEDED (29 Oct 2026, 10:09: the coordinator saved roc.html's table as `roc_html.csv`, which the script uses; roc.xls would only add precision) | roc.xls (Return on Capital by Sector, US) | https://www.stern.nyu.edu/~adamodar/pc/datasets/roc.xls (from https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/roc.html) | `~/workspace/rule-of-x-paper/data_raw/damodaran_2026/roc.xls` | fundgrEB's ROC is the lease- and R&D-adjusted ROC, so the current k includes capitalized R&D and lease debt (about twice the unadjusted k in software and retail). roc.xls adds unadjusted and lease-adjusted ROIC, so k matches Part I (R&D expensed); the script then switches the default k to the unadjusted variant and re-checks fundgrEB's basis. |
| OPTIONAL | histgr.xls (Historical Growth Rates by Sector) | https://www.stern.nyu.edu/~adamodar/pc/datasets/histgr.xls (from https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histgr.html) | `~/workspace/rule-of-x-paper/data_raw/damodaran_2026/histgr.xls` | "CAGR in Revenues- Last 5 years" turns the reinvestment cross-check into marginal capital per dollar of growth for every group (today only software, with the SEC panel's growth). |
| OPTIONAL | indname.xls (companies in each industry) | https://pages.stern.nyu.edu/~adamodar/pc/datasets/indname.xls (the link printed in every sheet's header) | `~/workspace/rule-of-x-paper/data_raw/damodaran_2026/indname.xls` | firm list per group, for a firm-level check of the name-based crosswalk (its columns are not verified; if it lists SIC codes the crosswalk can be rebuilt from firm counts). Parsing it needs a small addition to the script. |
| OPTIONAL | mgnroc.xls (Margin/ROIC by Sector, US) | https://www.stern.nyu.edu/~adamodar/pc/datasets/mgnroc.xls (from https://pages.stern.nyu.edu/adamodar/New_Home_Page/datafile/mgnroc.html) | `~/workspace/rule-of-x-paper/data_raw/damodaran_2026/mgnroc.xls` | "Sales/ Invested Capital (LTM)" is a direct check of the lease-adjusted k (on the page values it matches margin / ROIC to the displayed precision for six groups). |
**Status, 29 Oct 2026, 10:12:** oesm16nat.zip is no longer needed. In the author's built-in browser, the lead agent read BLS's May 2016 national tables (https://www.bls.gov/oes/2016/may/oes_nat.htm; 820 detailed occupations) and checked them against gpts_are_gpts autoScores.csv at year 2016. All 737 occupations match, and the sums agree exactly: tot_emp 133,977,150 and a_mean 43,494,840. The vintage is therefore May 2016.
