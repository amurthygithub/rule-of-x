# Non-software industry priors (spec Section 24.10): sources, method and limits

Data agent, 29 Oct 2026. Script: `code/data_part2/11_nonsoftware_priors.py` (run with `python3 -I`; it is in `build_all.sh` after `05_function_priors.py`, which rewrites `industry_function_shares.csv` with the software rows only). Build metadata, every check result and per-industry diagnostics: `data/tasks/_build/nonsoftware_priors.json`. Software sanity check: `data/tasks/_build/software_sanity_check.csv`. A rebuild from `05` through `11` reproduces all outputs byte for byte (md5 checked).

## 1. Outputs

| file | rows | content |
|---|---|---|
| `data/tasks/industry_benchmarks.csv` | 96 (94 Damodaran groups plus Total Market and Total Market without financials) | firm count, every margin and expense ratio, cost of capital and its parts, ROE, ROC, reinvestment rate, invested capital per dollar of sales (k) in three variants, derived checks, source rows |
| `data/tasks/xw_damodaran_naics.csv` | 96 | crosswalk: engine NAICS match prefixes, OEWS staffing industries, match type, confidence, notes |
| `data/tasks/industry_function_shares.csv` | 1,994 = 360 software rows (unchanged) + 1,634 new (86 groups x 19 functions) | same schema as before, plus 16 appended columns |
| `data/tasks/nonsoftware_column_grounding.csv` | 112 | every column of the three files with its grounding class (a, b, c, d) and definition; the script stops if a column has no tag |

## 2. Sources and citations

All files were downloaded by the lead author through a browser into `data/raw/damodaran_2026/` and are parsed, never executed. Each spreadsheet's cell B1 ("Date updated:") is the Excel serial 46027, which is **5 January 2026**; every data page read says "Data used is as of January 2026". sha256 (also in `data/raw/CHECKSUMS.sha256`, with roc_html.csv above): margin.xls 25b04fce9740d9a471d50e176bf55aa6b7608cd0621b00072508a20e7c35ed7a; wacc.xls d38b149c731bba6847d077ef67c9a4bfa0a54f947ba480b2f9ea89f5451d39a6; roe.xls 7da8fd4c41dd75dcc898b784f42d407e92f2b242ddda09237c99cc02a6787817; fundgrEB.xls d96d24f919d60500340b40d99cdc93dcc655be053013371a6960745589a04cb2.

Citations (practitioner data with a stated method; quality flag `practitioner_dataset_disclosed`, the class the project already uses for Damodaran's WACC in `params.yaml`, `ownership_regimes.public.r_own_wacc`):
- Damodaran, A. (2026). Margins by Sector (US). Data as of January 2026 (spreadsheet dated 5 January 2026). NYU Stern School of Business. https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/margin.html (spreadsheet https://www.stern.nyu.edu/~adamodar/pc/datasets/margin.xls). Read 29 Oct 2026.
- Damodaran, A. (2026). Cost of Equity and Capital (US). Data as of January 2026. https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/wacc.html (wacc.xls). Read 29 Oct 2026.
- Damodaran, A. (2026). Return on Equity by Sector (US). Data as of January 2026. https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/roe.html (roe.xls). Read 29 Oct 2026.
- Damodaran, A. (2026). Fundamental Growth in EBIT by Sector (US). Data as of January 2026. https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/fundgrEB.html (fundgrEB.xls). Read 29 Oct 2026.
- Damodaran, A. (2026). Return on Capital by Sector (US). Data as of January 2026. https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/roc.html. **Source used: the page's HTML table, not roc.xls.** The coordinator extracted the full table in the author's browser on 29 Oct 2026 and saved it as `data/raw/damodaran_2026/roc_html.csv` (96 industry rows plus header; sha256 f7363946361916feb0c2876047ba8c50c1d51fd45171fac4426254d1d9c14b98, hash-verified on arrival). Columns: number of firms; pre-tax and after-tax ROIC, each unadjusted, lease adjusted, and lease and R&D adjusted; normalized 10-year ROIC. Values are percentage strings rounded to 0.01 points; financial groups are NA. **Date conflict:** the page says "Data used is as of January 2026" but its footer says "Last updated January 2025"; the firm counts equal margin.xls in every row, which is consistent with the January 2026 data. roc.xls itself was never obtained; if it arrives the script prefers it (full precision).
- Damodaran, A. (2026). Margin/ROIC by Sector (US). https://pages.stern.nyu.edu/adamodar/New_Home_Page/datafile/mgnroc.html (optional mgnroc.xls). Read 29 Oct 2026.
- Damodaran, A. (2026). Historical (Compounded Annual) Growth Rates by Sector. https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histgr.html (optional histgr.xls). Read 29 Oct 2026.
- Variable definitions: https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/variable.htm. Read 29 Oct 2026.

Verified definitions (quoted from each file's "Variables & FAQ" sheet unless stated):
- Gross Margin, COGS/Sales, R&D/Sales, SG&A/Sales, EBITDA/Sales: "Aggregated ... as a percent of aggregated revenues, across companies in the group." EBITDASG&A/Sales: "Aggregated EBITDA, with SG&A added back". So SG&A/Sales = (EBITDA+SG&A)/Sales minus EBITDA/Sales, which holds in every row to 1.1e-16; the same identity holds for R&D. Gross margin plus COGS/Sales equals 1 exactly.
- After-tax Unadjusted Operating Margin: "Aggregated as-stated operating profits, after netting effective taxes". Lease and R&D adjustments: "Operating Income + Current year's lease exp - Lease Asset Depreciation" and "Operating Income + Current year's R&D exp - Amortization of R&D asset".
- variable.htm: "ROC = EBIT (1-t) / (BV of Debt + BV of Equity-Cash)"; "After-tax Operating Margin = EBIT(1-t) / Sales". Hence k = invested capital / sales = after-tax margin / ROC when both use the same EBIT(1-t). The page does not say whether book values are lagged.
- fundgrEB.xls: "ROC: Aggregated after-tax Operating Income, across all firms in group, using trailing 12 month data/ Aggregated Invested Capital, across all firms in group, using most recent balance sheet." "Reinvestment Rate: Aggregated Reinvestment/ Aggregated after-tax Operating income, where reinvestment = Net Cap Ex (including acquisitions and R&D) + Change in non-cash Working Capital." "Fundamental Growth Rate: ROC * Reinvestment Rate". The identity holds in every row (max error 0).
- wacc.xls: inputs in the sheet are long-term Treasury rate 3.95% (row 9), equity risk premium 4.46% (row 10), global default spread 0.23% (row 11) and marginal tax rate 25% for the cost of debt (row 13). Cost of equity, after-tax cost of debt and cost of capital recompute exactly from these and the beta and weights columns. The "Tax Rate" column is not the rate used for the cost of debt; it is kept as `tax_rate_wacc_sheet`.
- The sheets say "US companies". The data service is not named on any page read ("Data Used: Multiple data services").

Redistribution. No license, terms of use or redistribution statement appears on margin.html, wacc.html, roe.html, roc.html, mgnroc.html, fundgrEB.html, histgr.html or variable.htm (all read 29 Oct 2026). A trade newsletter (BVWire, 21 Jan 2026, https://bvresources.com/articles/bvwire/damodaran-posts-his-first-data-update-for-2026) calls the data "free", which is not a license. Therefore: do not ship the raw xls files in the replication package; ship the script and these download instructions. `industry_benchmarks.csv` reproduces Damodaran's published ratios almost in full, so it should be regenerated by the script rather than shipped, unless the author obtains permission. The crosswalk and the function shares are our derived work and can ship with the citation.

Download instructions (save unchanged into `data/raw/damodaran_2026/`, which corresponds to `~/workspace/rule-of-x-paper/data_raw/damodaran_2026/` in the author's workspace): the spreadsheet links on the pages above, all of the form https://www.stern.nyu.edu/~adamodar/pc/datasets/<name>.xls for margin, wacc, roe and fundgrEB (required) and histgr and mgnroc (optional); for the return on capital, save the HTML table of roc.html as `roc_html.csv` (header row as on the page, percentage strings kept), or roc.xls if it can be downloaded. Then run `code/data_part2/build_all.sh`.

## 3. Checks on the raw data (all in `_build/nonsoftware_priors.json`, key `checks`)

- Industry names and firm counts are identical across the four files; the 94 groups sum to 5,994 firms, the Total Market count.
- Financial groups: Bank (Money Center), Banks (Regional), Brokerage & Investment Banking, Financial Svcs. (Non-bank & Insurance), the three Insurance groups, Investments & Asset Management and Reinsurance hold 1,173 firms; Total Market minus Total Market (without financials) is 1,172. These nine groups are flagged `financial_group`.
- Quirks kept as published and flagged: operating margin and EBITDA are zero for the two bank groups and Brokerage; EBITDA is below EBIT (negative implied D&A) in Insurance (Prop/Cas.), Investments & Asset Management, Precious Metals, Reinsurance and Tobacco; SG&A/Sales is negative (-0.9%) for Utility (General) and zero for Transportation (Railroads); fundgrEB reports ROC as "NA" for the two bank groups, Brokerage and Financial Svcs.
- **fundgrEB source error.** Utility (Water) and Total Market carry the same ROC to all 16 digits (0.08955910414193033). roc_html.csv shows Total Market 8.96% and Utility (Water) 7.25% lease and R&D adjusted (7.26% lease adjusted, 7.30% unadjusted, all after tax), so the Utility (Water) cell in fundgrEB is wrong. The script flags any non-total row whose ROC duplicates another row (`fundgr_suspect`) and leaves its k blank.

## 4. Invested capital per dollar of sales (Part I's k)

Part I defines k as invested capital per dollar of revenue (investment = k dS; economic margin e = m + k(g - r); sections/model.tex). k is computed as after-tax operating margin over after-tax ROC on matching adjustments.

**fundgrEB's ROC is the lease- and R&D-adjusted ROC, not the unadjusted one.** The FAQ wording does not name the adjustment. Re-checked against roc_html.csv in all 91 rows where both are published (Utility (Water) excluded): the largest absolute difference from the table's "Lease & R&D adjusted after-tax ROIC" is 4.9e-5, which is the rounding of a 0.01-point string, while the differences from the lease-adjusted and unadjusted columns reach 0.318 and 0.396. The script re-establishes this basis from the table on every run (it would switch basis only if another column matched within 1e-4).

**Default k (consistent with Part I):** `k_ic_per_sales` = after-tax unadjusted operating margin (margin.xls) / unadjusted after-tax ROIC (roc_html.csv), labelled `k_variant = unadj`, for 87 groups (all non-financial groups, Utility (Water) included, because its k no longer depends on fundgrEB); the nine financial groups are blank. The variants are kept: `k_ic_per_sales_lease` (lease-adjusted margin / lease-adjusted ROIC), `k_ic_per_sales_lease_rnd` (lease and R&D adjusted, from the table) and `k_ic_per_sales_fundgr` (lease and R&D adjusted margin / fundgrEB ROC, full precision; it agrees with the table-based variant to within 0.007).

| group | after-tax margin (unadj.) | ROIC unadj. | **k default (unadj.)** | k lease | k lease & R&D | k fundgrEB |
|---|---|---|---|---|---|---|
| Software (System & Application) | 31.17% | 54.28% | **0.574** | 0.650 | 1.113 | 1.113 |
| Software (Internet) | 3.57% | 6.10% | **0.586** | 0.741 | 1.338 | 1.337 |
| Software (Entertainment) | 32.06% | 46.86% | **0.684** | 0.744 | 1.266 | 1.267 |
| Computer Services | 6.63% | 39.28% | **0.169** | 0.193 | 0.266 | 0.266 |
| Utility (Water) | 29.94% | 7.30% | **4.102** | 4.116 | 4.119 | blank (source error) |
| Total Market (without financials) | 12.20% | 18.92% | **0.645** | 0.697 | 0.818 | 0.818 |

Across the 85 non-financial groups (totals excluded) the default k has median 0.574, p10 0.222 and p90 2.029; the highest values are real estate and utilities (Retail (REITs) 7.25, R.E.I.T. 6.59, Green & Renewable Energy 4.94, Utility (Water) 4.10). The rounding of the table moves k by at most about 0.2% relative (for ROIC near 2.5%).

Default k for the five groups with the most matched US employment (OEWS May 2025 jobs in the industries the engine matches to the group, `oews_employment_matched` in the crosswalk):

| group | matched jobs | NAICS prefixes | confidence | **k default** | k lease | k lease & R&D |
|---|---|---|---|---|---|---|
| Hospitals/Healthcare Facilities | 19.1 million | 622/623/621 | medium | **0.413** | 0.513 | 0.514 |
| Education | 13.9 million | 611 | medium | **0.445** | 0.615 | 0.730 |
| Restaurant/Dining | 12.3 million | 722 | high | **0.386** | 0.661 | 0.682 |
| Business & Consumer Services | 10.2 million | 561/812 | low | **0.309** | 0.357 | 0.392 |
| Engineering/Construction | 9.0 million | 237/2362/238/5413 | medium | **0.203** | 0.229 | 0.230 |

Caution on these five: most of their employment is in private firms or public bodies (K-12 schools are inside 611, though Damodaran's 32 education firms are private post-secondary and training providers), so a listed-firm k is a weak prior for them; restaurants show the largest lease effect (0.386 unadjusted against 0.661 lease adjusted).

Further points:
- The coordinator's first instruction (pair fundgrEB's ROC with the unadjusted margin) would have mixed bases; with the HTML table both numerator and denominator are now unadjusted.
- Financial groups: k is blank (invested capital of a bank or insurer is not operating capital).
- Book invested capital includes goodwill from acquisitions and non-cash working capital, and it is an average, not a marginal, ratio.
- If roc.xls ever arrives the script uses it instead of the HTML table (same headers, full precision); a harness that fed a synthetic roc.xls through the unmodified script confirmed that path.

Reinvestment cross-check. `reinvestment_sales` = reinvestment rate x after-tax margin on the same basis (net capex including acquisitions and R&D, plus working capital, per dollar of sales). Under stable margins the fundamental growth identity makes "reinvestment over fundamental growth" equal to k by construction, so the informative check needs realized growth. For software, with the SEC panel's realized revenue growth (FY2025 aggregate 15.1% for SIC 7372, 160 firms; FY2020-25 CAGR 14.9%, 146 firms), Damodaran's software reinvestment of 24.1% of sales (lease and R&D basis, since the reinvestment rate is relative to fundgrEB's after-tax operating income) implies marginal capital of 1.60 and 1.62 per dollar of added revenue, against the average 1.11 on the same basis (0.574 unadjusted). Damodaran's own 5-year revenue CAGR for the group (19.56% on histgr.html) would give 1.23. Marginal capital needs in software therefore look at or above the average ratio on this basis. Reinvestment rates are negative in 11 groups and above 100% in 14 (`reinvestment_flag`); in those groups average k says little about capital needs per unit of growth. With histgr.xls on disk the script computes `k_marginal_implied` = reinvestment_sales / 5-year revenue CAGR for every group.

## 5. Crosswalk from Damodaran groups to NAICS (precedent class b)

Damodaran assigns firms to his own groups and publishes no concordance to SIC or NAICS; the firm list (`indname.xls`, linked in each sheet) is not on disk. Method: each group is mapped by its name and the NAICS 2022 scope of the candidate industries to (i) engine match prefixes, chosen at the narrowest NAICS level that separates it from other groups, and (ii) OEWS May 2025 industries in `industry_staffing.csv` whose staffing splits the buckets. Rules enforced by the script and the validator: no prefix is used by two emitted groups; no prefix equals 51 or 54 or extends 5132, 5415 or 5182 (the SEC software rows); OEWS codes exist and are not nested.

Confidence: **high** if the group corresponds to one NAICS industry or a small set with essentially the same scope; **medium** if it spans several industries, if the NAICS industry contains material activity outside the group, or if staffing comes from a broader parent; **low** if the group is defined by something NAICS does not use (size, legal form, technology, conglomerate), or its composition cannot be judged without the firm list. Counts: 32 high, 42 medium, 20 low (plus 2 totals).

Not emitted to the function shares (9): the three Software groups and Computer Services (covered by the SEC rows); Heathcare Information and Technology (its firms carry software and IT codes); Bank (Money Center) (NAICS does not separate it from regional banks); Cable TV (same code as wired telecom); Retail (REITs) (same code as other REITs); Diversified (no NAICS counterpart). Total Market (without financials) is emitted with an empty `naics`, so the engine reaches it only on request.

Weak spots:
- Low confidence and emitted (14): Building Materials, Business & Consumer Services (155 firms), Chemical (Diversified), Construction Supplies, Electronics (Consumer & Office), Farming/Agriculture (OEWS does not cover farms, so staffing comes from support activities 115), Green & Renewable Energy, Healthcare Support Services, Information Services, Office Equipment & Services, Oil/Gas (Integrated), Packaging & Container, R.E.I.T. (190 firms; a tax status, not an activity), Real Estate (General/Diversified).
- Healthcare Support Services is mapped to health insurers (524114) and drug wholesalers (4242) by inference from its 12.1% gross margin, and ambulatory providers (621) are mapped to Hospitals/Healthcare Facilities. This is the most consequential judgment.
- Retail (General) reports R&D of 5.2% of sales, which is not typical of general-merchandise retailers; one very large firm with large technology spending probably dominates the aggregate (not verifiable without the firm list). Aggregates of other groups may be dominated similarly.
- 20 emitted groups use at least one NAICS code that is not listed in any OEWS file on disk, so its title is unverified (`naics_match_verified` = 0). The 30 unverified codes are 111, 112, 21222, 31211, 31212, 31213, 31214, 32221, 322291, 325413, 325414, 32616, 327213, 3273, 332431, 333132, 333242, 334413, 334510, 334511, 336992, 517112, 5231, 5239, 524113, 52413, 5311, 5312, 5313 and 541714. census.gov was not reachable from this session; please confirm against the NAICS 2022 manual.
- Several 3-digit catch-alls (Chemical (Diversified) 325, Utility (General) 221, Real Estate (General/Diversified) 531) are reached only when a firm gives a 3-digit NAICS, because every 4-digit child is assigned to another group.
- A firm-level check against `indname.xls` would upgrade the crosswalk; it is requested as optional (download requests, Section 9).

## 6. Function shares for non-software industries

Schema: identical to the software rows (`sic, naics, size_band, function_id, cost_bucket, share_of_revenue_prior, share_of_revenue_sd, bucket_share_mean, bucket_share_sd, bucket_share_median, within_bucket_split, within_bucket_range, within_bucket_assumed, n_firms, years, source`), plus appended columns (`damodaran_industry, prior_basis, source_bucket, bucket_reassigned_from, within_bucket_method, residual_share_of_function_wagebill, negative_bucket_clipped, unbucketed_cost_share, unbucketed_cost_flag, crosswalk_confidence, small_sample, financial_group, grounding_*`). The 360 software rows keep their values exactly (string-level sha256 of their original columns is asserted by the script and re-checked by the validator); they get `prior_basis = sec_panel`. One row per function per group, so the engine's per-function mean equals the value.

- **Buckets (a):** COGS/Sales, R&D/Sales and SG&A/Sales from margin.xls. Functions are pooled by their `functions.csv` cost bucket: cogs (F05, F07, F08, F09, F16), rnd (F02), and sm plus ga together for SG&A (F03, F04, F06 and F01, F10-F15, F17-F19).
- **Within-bucket split (c):** W_f = sum over SOC of OEWS May 2025 employment in the mapped industries x national annual mean wage (`occupations.csv`, median where the mean is missing) x alloc(f, soc) from `function_occ.csv` (the constructed FUNC_SOC table). Split = W_f / W_pool. `within_bucket_assumed = False` for these rows: the split is computed, not assumed; it is conditional on FUNC_SOC (constructed) and on the residual rule below. The sm/ga division of SG&A follows the same wage bill.
- **Residual rule (d):** employment no FUNC_SOC function claims (1 - sum of alloc) goes by SOC major group: 17 and 19 to F02 (engineering and science), 41 to F04 (sales), 45, 47, 49, 51 and 53 to F09 (farming, construction, repair, production, transport), everything else to F08 (service delivery). FUNC_SOC was built for software firms, so the residual is large: a median 42% of a group's wage bill (p10 21%, p90 68%; restaurants and hospitals 88%).
- **Merge rule (d):** a bucket below 0.5% of sales (negatives clipped to 0) is merged, with its amount, into SG&A if it is COGS or R&D, and into COGS if it is SG&A (90 rows; `bucket_reassigned_from`). Example: R&D-free insurers put F02 into the SG&A pool; banks (COGS 0) put the COGS functions there; railroads (SG&A 0) put the SG&A functions into COGS.
- **sd (b + d):** bucket sd = coefficient of variation of firm-mean bucket shares in the SEC software panel (FY2023-25, same filters as `05`: COGS 0.585, R&D 0.611, SG&A 0.504) x the Damodaran bucket; split sd = 25% of the split (assumed); combined as in `05`. The software panel is probably more dispersed than mature industries, so these sd are likely wide.
- **Robustness:** recomputing the splits with OEWS industry-specific mean wages instead of national ones changes the largest split in a group by a median 2.1 points (worst 9.2 points, Shoe) and the largest function share of revenue by a median 0.6 points (worst 4.6 points).
- **How the engine uses these rows:** `impute.py` rescales the prior shares within each function's own cost bucket to the firm's Tier 0 totals, so only relative weights within cogs, rnd, sm and ga matter; the merge rule and the absolute levels do not change engine results. Two caveats follow: COGS in goods, trade, insurance and energy groups is mostly purchased inputs (materials, merchandise, claims, fuel), which the split allocates in proportion to labor; and the engine's labor share per function (`priors/function_attributes.csv`) is not industry-specific, so people cost in those groups will be overstated unless the engine builder makes it so.
- **Costs outside the three buckets:** `unbucketed_opex_sales` = 1 - COGS - SG&A - R&D - operating margin - implied D&A exceeds 5% of sales in 17 emitted groups (flag `unbucketed_cost_flag`; for example hospitals 18.9%, airlines 10.6%, insurers, banks, oil and gas, power). These costs are not allocated to functions.

## 7. Grounding classes and flags

Every column is tagged in `nonsoftware_column_grounding.csv`. In summary: Damodaran values as published are **a** (practitioner data with a stated method); their use as the prior of a NAICS industry is **b** (the crosswalk is a precedent-class mapping); our arithmetic (derived ratios, k, splits, flags) is **c**; the residual rule, the merge rule, the 25% split sd and the 0.5% merge threshold are **d**; the bucket sd from the software panel is **b**. Flags: `small_sample` (fewer than 20 firms: 27 of the 86 emitted groups, among them Steel, Tobacco, Railroads with 4 firms, Rubber& Tires with 3 and Reinsurance with 1, whose ratios are that firm's), `crosswalk_confidence` (low for the 14 groups above), `financial_group`, `unbucketed_cost_flag`, `negative_bucket_clipped`, `k_flag`, `reinvestment_flag`, `fundgr_suspect`.

## 8. Coverage of US employment

Share of OEWS May 2025 employment (155.5 million jobs, the 4-digit industry partition of `industry_staffing.csv`) whose industry the engine now matches, by NAICS prefix: 76.4% to a Damodaran-based prior, 2.4% partly (a longer prefix covers part of the industry), 2.3% to the SEC software rows, 3.4% only to the pooled "51/54" software row (for example legal, accounting and consulting services, which get a software prior), and 15.5% to the engine's generic prior. Excluding government (sector 99): 81.8%, 2.6%, 2.5%, 3.6% and 9.5%. The largest industries left on the generic prior are local government (5.8 million jobs), individual and family services (3.5 million), management of companies (2.8 million), state and federal government, automotive repair, child care and the Postal Service.

## 9. Sanity check against the SEC panel (FY2025, sum over sum)

`data/panel_v2_all.csv`, fiscal year 2025, revenue-weighted aggregates over firms reporting each item (as Damodaran's are aggregates); gaps are Damodaran minus panel, in percentage points.

| metric | Damodaran Software (System & Application), 309 firms | panel SIC 7372 (n) | gap | panel SIC 7370-7374 (n) | gap | Damodaran Software (Internet), 29 firms |
|---|---|---|---|---|---|---|
| gross margin | 71.7 | 69.7 (154) | +2.0 | 65.2 (282) | +6.5 | 62.6 |
| pre-tax operating margin | 33.0 | 27.3 (166) | +5.7 | 27.0 (315) | +6.0 | 3.7 |
| operating margin before SBC | 40.8 | 35.4 (166) | +5.4 | 34.5 (304) | +6.3 | 18.6 |
| R&D / sales | 16.0 | 16.0 (152) | 0.0 | 16.9 (271) | -0.9 | 19.8 |
| SG&A / sales | 24.4 | 23.7 (147) | +0.6 | 19.9 (241) | +4.5 | 33.4 |
| SBC / sales | 7.8 | 8.1 (167) | -0.3 | 7.3 (307) | +0.5 | 14.9 |

- Against SIC 7372 the cost structure matches closely (R&D, SG&A and SBC within 0.6 points); the operating margin gap of about 5.7 points narrows to 2.8 points when the panel is restricted to US-located filers in SIC 7370 and 7372 (30.2%, 176 firms), so part of it is the panel's foreign filers (20-F and 40-F) and part is classification.
- Software (Internet) is far from every panel cut (operating margin 3.7% against 27-30%): it is a small group of low-margin firms, and the large internet platforms must sit elsewhere in Damodaran's grouping, probably in System & Application (not verifiable without the firm list).
- Aggregates are not medians: in the same panel the median operating margin of SIC 7372 is 0.3% and the median SG&A share 45.5%, against aggregates of 27.3% and 23.7%. A Damodaran ratio describes the largest firms of a group, not a typical one.
- Cost of capital: Software (System & Application) 9.34% in wacc.xls, identical to the value already in `params.yaml` (`ownership_regimes.public.r_own_wacc`), which was read from wacc.html.

## 10. Limits to carry into the paper

- **US-listed firms only, aggregated ratios.** The sheets cover "US companies" in Damodaran's sample and every ratio is aggregated across firms (sum over sum), not a median or a firm average, so large firms dominate (Section 9). No dispersion is published; the sd are borrowed from the software panel.
- **Private firms differ.** Listed firms are larger, more acquisitive (book invested capital includes goodwill) and differently financed; most employment in construction, health care, restaurants and retail is in private firms whose cost structure and capital intensity can differ from the listed aggregate.
- **Jobs, not hours.** OEWS counts jobs (a part-time job counts as one) and the split uses annual mean wages; occupations with hourly wages only have no annual wage and are dropped (at most 5.2% of a group's employment, in Entertainment). Wage bills exclude benefits; a uniform loading would not change within-bucket splits.
- **Practitioner data.** Damodaran's datasets are practitioner data with a stated method (FAQ sheets and variable.htm); the data service is not named and the accounting period is stated only in fundgrEB (trailing twelve months for operating income, most recent balance sheet for capital). Cite them as practitioner data, not as official statistics.
- **Crosswalk by name.** Damodaran's groups are his own classification; the mapping is a precedent-class judgment, 20 groups are low confidence, and 30 NAICS codes are unverified.
- **Function membership.** FUNC_SOC was built for software firms; outside software a median 42% of the wage bill is assigned by the residual rule, and `function_occ_by_industry.csv` covers only FUNC_SOC occupations, so the engine staffs F08 and F09 with the FUNC_SOC occupation mix rather than with, for example, nurses or pilots.
- **COGS is not labor.** In goods, trade, insurance and energy groups COGS is mostly purchased inputs.
- **k** is an average book ratio (equity plus debt minus cash, so it includes goodwill and working capital), from listed firms; the default (unadjusted) treats R&D as expensed, as Part I does; the ROIC inputs come from an HTML table rounded to 0.01 points whose footer date conflicts with its data date.

## 11. For the engine builder (no engine file was edited)

- `industry_function_shares.csv`: new rows are already read by `priors.py` (the `naics` column carries the match prefixes) and matched by `_industry_shares` on the longest prefix. Suggested follow-ups: (i) `synthetic.py` selects software rows with `naics_prefix.str.contains("51")`, which also matches new prefixes such as 3251, 5131, 5161 and 517; today only the size-band filter keeps them out, so select on `prior_basis == "sec_panel"`; (ii) the pooled SEC row "51/54" catches legal, accounting and consulting firms; (iii) the generic fallback could use the rows with `damodaran_industry == "Total Market (without financials)"` (empty `naics`) instead of the built-in generic rows; (iv) the SEC rows list F06 under two buckets and the engine averages rather than sums them (pre-existing).
- `defaults.yaml` `finance.capital_intensity_k` (0.02, range [0, 0.10], class d): Part I defines k as invested capital per dollar of revenue, for which the default (unadjusted) k is 0.22 to 2.03 (p10 to p90) across non-financial groups and 0.574 for Software (System & Application). Point it to `industry_benchmarks.csv: k_ic_per_sales` through `xw_damodaran_naics.csv` (use only when `k_flag` starts with "ok"; carry `k_variant`; range from the other variants), after confirming the engine's k means the same thing as Part I's.
- `finance.r` (now the software WACC for every firm): point it to `industry_benchmarks.csv: cost_of_capital` by group, with the existing `to_continuous` transform.
- Spec 24.3 objectives: `roic_minus_wacc` and `k_ic_per_sales` give the industry frontier in (growth, ROIC); `reinvestment_rate`, `reinvestment_sales` and `expected_growth_ebit` give a sustainable-growth check.
- Tier 0 defaults or plausibility flags for a firm's buckets: `cogs_sales`, `rnd_sales`, `sga_sales`, `sbc_sales`, `gross_margin`, `op_margin_pretax` by group.
- Labor share per function should become industry-specific before non-software people costs are reported (Section 6).

## 12. What remains

- roc.xls: no longer needed (the HTML table supplies the same columns); it would only add precision beyond 0.01 points.
- histgr.xls (optional): adds the 5-year revenue CAGR and the marginal capital per dollar of growth for every group.
- indname.xls (optional): firm-level check of the crosswalk.
- mgnroc.xls (optional): Sales/Invested Capital (LTM) as a direct check of k.
- Confirmation of the 30 unverified NAICS codes.
