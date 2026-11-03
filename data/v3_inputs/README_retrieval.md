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

**Scope.** These descriptions cover only the named firms. R2 therefore remains a sensitivity: applying it as a rule needs descriptions for every firm. `business_descriptions.json`, the name `build_panel_v3.py` reads to apply R2 to the main sample, is deliberately not created.

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
