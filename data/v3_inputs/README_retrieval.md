# SEC inputs for the v3 sample rules and the cash-score bridge (retrieved 29 Oct 2026)

These files were retrieved on 29 Oct 2026, between about 16:06 and 16:15 UTC−7, after the author approved the download at 16:05. The author's computer ran the retrieval in the built-in browser of the Claude desktop app, because the compute environment cannot reach sec.gov. The lead agent wrote the browser code and ran it with the author's approval. Nothing was entered on any site, and no account was used.

## 1. XBRL frames (data.sec.gov)

**Endpoint and calls.** `https://data.sec.gov/api/xbrl/frames/{taxonomy}/{tag}/USD/{period}.json`: 209 calls with 3 parallel workers and a 200 ms pause between calls. About 42 MB of JSON was received (uncompressed size; the bytes actually sent were smaller, because SEC compresses responses).

**Concepts and periods.**
- US-GAAP, periods CY2008–CY2026:
  - InterestPaid
  - InterestPaidNet
  - IncomeTaxesPaid
  - IncomeTaxesPaidNet
  - RevenueFromRelatedParties
  - RelatedPartyTransactionRevenuesFromTransactionsWithRelatedParty
  - BusinessCombinationProFormaInformationRevenueOfAcquireeSinceAcquisitionDateActual
- dei: EntityPublicFloat, instants CY2008Q1I–CY2026Q4I.

**Filters.**
- Rows were kept only for the 654 registrants in `data/panel_v3_all.csv`. (One of them was removed from the repository on 2 Nov 2026 at the author's request, `code/exclusions.py`; it had no rows in these files, raw or derived.)
- The interest, tax and float concepts were further limited to the 292 core v3 registrants.
- Public float was reduced to a sign (1 if positive, else 0).

**Not available.** 17 frames returned 404 and are absent from the files:
- RevenueFromRelatedParties for 2024–2026, after the element was retired;
- RelatedPartyTransactionRevenuesFromTransactionsWithRelatedParty for 2014–2026, except 2023;
- the acquiree-revenue element for 2008;
- the float instant CY2026Q4I.

**Coverage limits.**
- Frames contain only non-dimensional facts, and for each company and period they keep the latest filed value. They are therefore not first-reported values.
- Acquiree revenue since acquisition is usually tagged with a business-combination axis, so it is absent from frames for most filers. The frames contain 63 facts.

**Transfer and check.** The browser transferred the compact result as gzip plus base64. Its FNV-1a hash (73ee6d58) matched in the container: 6,903 rows, stored as `raw/sec_frames_2026-10-29.txt`. Each row is: concept index, CIK, end date, value. CIK, end date (days since 2000-01-01) and value are in base 36.

**Derived files.**

| File | Content | Matching rule |
|---|---|---|
| `related_party.json` | {cik: {fy_end: related-party revenue}} | Maximum of the two elements, matched to the panel fiscal-year end within ±10 days |
| `acquiree_revenue.json` | {cik: {fy_end: value}} | Same rule |
| `listing_status.json` | {cik: {fiscal year: public float positive}} | Any float instant in the 366 days up to the fiscal-year end |
| `cash_interest_taxes.json` | {cik: {fy_end: {element: value}}} | Same ±10-day rule |

`listing_status.json` is not yet a no-listed-equity flag. A zero float in a firm's first annual report after its IPO reflects timing, not debt-only status (Duolingo, Figma and others), so the R5 rule must separate the two cases.

## 2. Business descriptions (www.sec.gov)

**Firms covered.** The 16 registrants named by the review panels.

**Source document.** For each firm, the latest annual report (10-K, or 20-F for Xunlei and Mobileye B.V.) listed in `data.sec.gov/submissions/CIK##########.json`.

**Text kept.** The primary document was fetched in full, because a Range header was not honored. The first 3,500–4,000 characters of Item 1 (Business) were kept; for a 20-F, the text of Item 4.B (Business Overview). The section was located as the heading occurrence with the longest span before the next item (Item 1A or 4A, or 4.C for a 20-F). Cross-references and table-of-contents entries were excluded. The extraction is in the lead agent's browser code.

**Download size.** About 90 MB of HTML in total (uncompressed size), including a second pass after the first extraction rule failed on headings run together with the next word.

**Check.** The transfer hash (cd54dbce) matched.

**Files.**
- `raw/business_descriptions_raw_2026-10-29.json`: text with accession number, document and URL.
- `business_descriptions_named.json`: {cik: text}.

**Scope.** These descriptions cover only the named firms. On 29 Oct R2 therefore remained a sensitivity, and `business_descriptions.json`, the name `build_panel_v3.py` reads to apply R2 to the main sample, was deliberately not created. The descriptions of every other core registrant were retrieved on 3 Nov 2026 by the same rule (section 6); `business_descriptions.json` now exists, and R2 applies to the main sample by its pre-set classifier.

# Second retrieval (2 Nov 2026): interest income, deferred revenue and Bending Spoons filings

**Approval and method.** The author approved this retrieval on 2 Nov 2026 at about 10:15 UTC−8 (round-2 decision 3). It ran from about 10:17 to 10:21 UTC−8 in the built-in browser of the Claude desktop app on the author's computer, with browser code written by the lead agent. Nothing was entered on any site, and no account was used.

## 3. XBRL frames (data.sec.gov)
**Calls.** `https://data.sec.gov/api/xbrl/frames/us-gaap/{tag}/USD/CY{year}.json`, years CY2008–CY2025. That is 144 calls, with 3 parallel workers and a 200 ms pause between calls. About 13.5 MB of JSON was received (uncompressed size).

**Rows kept.** Only the 292 core v3 registrants.

**Concepts (all duration facts):**

| # | Concept |
|---|---|
| 0 | InvestmentIncomeInterest |
| 1 | InvestmentIncomeInterestAndDividend |
| 2 | InterestAndOtherIncome |
| 3 | InvestmentIncomeNonoperating |
| 4 | InterestIncomeOperating |
| 5 | InterestIncomeExpenseNonoperatingNet |
| 6 | IncreaseDecreaseInContractWithCustomerLiability |
| 7 | IncreaseDecreaseInDeferredRevenue |

**Not available.** Seven frames returned 404: IncreaseDecreaseInContractWithCustomerLiability for CY2008–CY2014, before the element was in use.

**Transfer and check.** The FNV-1a hash (75057154) matched in the container. There are 4,070 rows, stored as `raw/sec_frames_interest_deferred_2026-11-02.txt`, in the same row format as section 1.

**Derived file.** `interest_income_deferred.json`: {cik: {fy_end: {element: value}}}, matched to the panel fiscal-year end within ±10 days. The match rate:
- 1,736 of 1,788 panel firm-years matched at least one element, with no conflicting values.
- Interest income (any of elements 0–4): 843 firm-years. InvestmentIncomeInterest alone: 696.
- Deferred-revenue or contract-liability change (element 6 or 7): 1,660 firm-years.

**Check against a reviewer's figure.** Palantir 2025 InvestmentIncomeInterest is $229,181,000, matching the finance referee's $229.2M.

**Limitations:**
- Many firms report interest income only inside "interest and other income, net", or under a non-operating element not retrieved here. A missing interest-income element therefore does not mean zero interest income.
- Elements 6 and 7 can be complementary (for example Palantir reports both, one for customer deposits and one for deferred revenue) or alternative tags for the same line. They must not be summed without checking the filer's cash-flow statement.
- Frames keep the latest filed value, not the first-reported one (same as section 1).
- Contract-liability levels (balance-sheet instants) were not retrieved.

## 4. Bending Spoons S.p.A. (CIK 2004711), www.sec.gov
**Filings list.** `data.sec.gov/submissions/CIK0002004711.json` lists 6-Ks after the IPO on 28 Jul, 4 Aug, 13 Aug, 4 Sep, 10 Sep, 2 Oct, 14 Oct, 26 Oct, 27 Oct, 28 Oct and 29 Oct 2026.

**6-K text retrieved.** The cover document and Exhibit 99.1 of each 6-K were fetched in full and reduced to text (21 documents, about 257 KB of HTML). Stored in `raw/bending_spoons_6k_2026-11-02.json`, with the URL of each document. Transfer hash 9693da30 matched. Not included:
- the Q2 results exhibits of 13 Aug (99.1 and 99.2), already used in v2;
- Exhibit 99.2 of 29 Oct, a 381 KB PDF.

**Cash interest.** Read from the final prospectus (424B4, 1 Jul 2026, 9.7 MB of HTML) and from Exhibit 99.2 of the 13 Aug 6-K. Stored in `bending_spoons_cash_interest.json` (thousands of USD):

| Item | Values | Source |
|---|---|---|
| Interests paid | 16,581 (2023); 19,168 (2024); 130,881 (2025) | Prospectus, F-34 and F-35 |
| Income taxes paid | 7,732 (2023); 6,456 (2024); 14,615 (2025) | Prospectus, F-34 and F-35 |
| Interests paid | 30,166 (Q1 2025, as restated); 89,037 (Q1 2026) | Prospectus, F-6 and F-7 |
| Interests paid | 49,737 (H1 2025); 161,153 (H1 2026) | Exhibit 99.2 |
| Interest expense on debt | 202,154 (H1 2026) | Exhibit 99.2 |
| Total future principal payments at 30 Jun 2026 | 4,983,469 | Exhibit 99.2 |

## 5. Bending Spoons filings, full documents (retrieved 2 Nov 2026, about 23:25 UTC−8)

The author approved this download at 23:23 (decision 3 of the outside-review plan). The documents were fetched from www.sec.gov in the built-in browser of the Claude desktop application on the author's computer. Each document was fetched once, from the EDGAR page's own origin, and nothing was entered on any site. The SHA-256 of each document's bytes was computed in the browser, and the transferred copy was checked against it after decompression. The files are stored gzip-compressed (`gzip -9 -n`). The hashes below are of the uncompressed documents.

| File | Document | URL | Bytes | SHA-256 |
|---|---|---|---|---|
| `raw/bending_spoons_f1_2026-06-08.htm.gz` | Form F-1, filed 8 Jun 2026 | https://www.sec.gov/Archives/edgar/data/2004711/000110465926071170/tm2613674-7_f1.htm | 9,426,040 | fbe3a107690009d6a0e84ecb05b61b178e7bba7f3ef4c931080628891aaf1fad |
| `raw/bending_spoons_424b4_2026-07-01.htm.gz` | Final prospectus, Rule 424(b)(4), filed 1 Jul 2026 | https://www.sec.gov/Archives/edgar/data/2004711/000110465926079884/tm2613674-14_424b4.htm | 9,714,600 | 86d91db82f3c5b793b1106b5397471a778667a5c547896302c151793735f3240 |
| `raw/bsp_ex99-1_2026-08-13.htm.gz` | Form 6-K of 13 Aug 2026, Exhibit 99.1 | https://www.sec.gov/Archives/edgar/data/2004711/000200471126000011/bsp_ex99-1.htm | 261,276 | 69e4c0c145f8b188d2ae00d18373b36a1ce0a85da8cb9d1a7383837b16a402f0 |
| `raw/bsp_ex99-2_2026-08-13.htm.gz` | Form 6-K of 13 Aug 2026, Exhibit 99.2 | https://www.sec.gov/Archives/edgar/data/2004711/000200471126000011/bsp_ex99-2.htm | 757,525 | 04f118132aca7fa9a33202619ce7d2ca8b65b4413ba72ff2ac6a8f74e5e1a82f |

These are the primary sources for the case study in Section 6. They replace the GLM reviewers' text extractions, which were used only to cross-check. In these copies the 424B4 states:
- annual organic revenue growth of 7% (2024) and 13% (2025);
- a subscription share of 95%, 92% and 93% of revenue (2023 to 2025);
- the pro forma revenue of $2,608,496 thousand.

# Third retrieval (3 Nov 2026): business descriptions of every core registrant, and the data audit

These files were read from sec.gov on 3 Nov 2026 through the browser on the author's computer, with browser code written by the lead agent, as in sections 1 to 5.

## 6. Business descriptions of the other core registrants (www.sec.gov), rule R2

**Firms covered.** The 277 registrants of the v2 core sample (`data/panel.csv`, 293 registrants) that the review panels had not named. With the 16 named firms of section 2 they cover every core registrant.

**Source document.** As in section 2: for each firm, the latest annual report listed in `data.sec.gov/submissions/CIK##########.json` (250 Form 10-K, 26 Form 20-F, 1 Form 40-F; filed 2010 to 2026, because registrants that stopped filing keep their last report).

**Text kept.** The first 3,999 to 4,000 characters of Item 1 (Business) of a 10-K, Item 4.B (Business Overview) of a 20-F, or the business section of the Annual Information Form filed as an exhibit to a 40-F. The section was located as in section 2. Where the primary heading pattern failed, a fallback heading pattern was used; the record then carries a `rule` field (9 firms). Edge cases:
- 1845338 (monday.com, 20-F): the 20-F uses a cross-reference index, so its Item 4.B only points to pages of the annual report; the text kept is from the report's "About Us" section, which describes the business.
- 1050140 (Descartes Systems Group, 40-F): the opening of the Annual Information Form is its table of contents followed by preliminary notes (basis of presentation, forward-looking statements), so the 4,000 characters kept contain no description of the business. The classifier classes it as software by default (no non-software keyword hits); both readers class it as software.

**Files.**
- `raw/business_descriptions_raw_2026-11-03.json`: {cik: {cik, form, accn, doc, period, filed, url, text, and `rule` where a fallback was used}}; SHA-256 25985f36bef5f00adfcc24dd6be0a66a7aed6811a22f6b8d4fbc5120edfbbcd4.
- `business_descriptions.json`: {cik: text} for all 293 core registrants, written by `code/audit/r2_descriptions.py` from `business_descriptions_named.json` (the 16 named firms, text of 29 Oct) and the raw file of 3 Nov (the other 277). The script checks that the two sets are disjoint and cover the v2 core sample exactly. `build_panel_v3.py` reads it and applies R2 to the main sample with the keyword classifier fixed before any description was read; the keyword lists are unchanged.

**Independent readings (R2 sensitivity).** Two readers, LLM agents on different models, blind to all outcome data (panel values, scores, estimates), each classified all 293 descriptions as software, interactive_entertainment, gambling, compute_infrastructure or other_non_software, with a subclass, confidence, reason and supporting quote. Their files are copied unchanged as `business_class_reader_a.csv` (SHA-256 b60e2002be554d0dc621131a905eb63999b6b306fa5ced9108360349e4083c57) and `business_class_reader_b.csv` (96d1cf1337d0ea16261269a51a4d31552f9c1c47d62c2d4c5b3782159ac116de), columns cik, name, class, subclass, confidence, reason, quote, note. They enter only as sensitivities (`build_panel_v3.py` columns `business_class_reader_a` and `_b`; variants `E1r2both`, `E2r2both`, `E1r2either`, `E2r2either` of `code/estimate_v3.py`); Cohen's kappa between them (software against not) is in `notes/panel_v3_build.json`, block `R2_readers`.

## 7. Data audit: financial statements of the filings the panel used (www.sec.gov)

**Seeded sample.** 40 firm-years of the v3 core sample of 3 Nov (before R2 applied: 1,788 firm-years), drawn with seed 20261103, 16 from the top decile of the cash score in their period and 24 from the rest (`notes/data_audit/sample.csv`, `sample_design.json`). For each, the face income and cash-flow statements of the filing the panel used were read and saved as table rows (`notes/data_audit/filing_statements_raw.json`, SHA-256 bd362129d49072832470b539b698bb3dac199da899acba91c91ed1c5ea6493f6; for one 40-F without statement exhibits, the facts of its XBRL instance). `code/audit/data_audit_compare.py` compares six items per firm-year and writes `compare.csv` and `capitalized_software.csv`.

**Capitalized-software scan.** For every firm-year of that frame with no capitalized software in companyfacts (PaymentsForSoftware + PaymentsToDevelopSoftware = 0) and capital expenditure reported (1,213), the cash-flow statement of the filing the panel used was read from its XBRL rendering: `FilingSummary.xml` of the filing, then the statement's R page. The rows of the investing section whose labels mention software or capitalization were kept with the page's unit (`notes/data_audit/capsw_cashflow_rows_2026-11-03.json`, keyed by accession number without dashes; SHA-256 10fdb9224b6e14ff9ad3f9fa9d2991f47db308d1c7bb169c052e1eca98492f15). One filing could not be read (FilingSummary.xml returned 404).

**Derived file.** `code/audit/capsw_scan_parse.py` reads the fiscal-year value of each capitalized-software line (121 candidate firm-years, `notes/data_audit/capsw_missed.csv`) and keeps a line when it is an outflow, is not a combined capital-expenditure line ("capital expenditures, including capitalization of software costs", "capitalized software and expenditures") and cannot be contained in the panel's capex: the capex came from PaymentsToAcquirePropertyPlantAndEquipment or, where it came from PaymentsToAcquireProductiveAssets, it is smaller than the software line, so the two are separate lines of the statement (7 firm-years: MedAssets 2010-11, Coursera 2021-25). Kept: 109 firm-years of 23 firms, written to `capitalized_software_filings.json` ({cik: {fy_end: {value (dollars), accn, label}}}; SHA-256 2fe3b7da3671ed46f906b09a89cba1fa1170a5961064cdda78d7e344d3ae7004); dropped: 9 combined lines and 3 lines that are not outflows (non-cash add-backs). Counts in `notes/data_audit/capsw_summary.json`. `build_panel_v3.py` uses the value where the XBRL cap_sw is 0 and recomputes the free-cash-flow margins, scores and capital intensity (column `cap_sw_source`; `cap_sw_xbrl` keeps the XBRL value). Check: Box, Inc. (CIK 1372612), fiscal year ending 31 Jan 2024, "Capitalized internal-use software costs" 16,561 thousand.
