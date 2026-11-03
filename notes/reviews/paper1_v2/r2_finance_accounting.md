# Round-2 referee report: finance and accounting

Paper: "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation", version 2 (paper1_v2.pdf, supplement_v2.pdf, source_v2.tar.gz, response_to_reviewers.md). Sole author Akshaya Bangalore Sreenivasa Murthy; AI research agents drafted it under her direction.

Materials read: the v2 paper and supplement; the response to reviewers; the live repository files `sections/measurement_acquired.tex`, `appendix_proofs_acquired.tex`, `data.tex`, `horizons.tex`, `model.tex`, `appendix_proofs.tex`, `discussion.tex`, `intro.tex`, `levers_by_position.tex`, `sections/tables/acquired_macros.tex`, `tab_param_sources.tex`, `paper1/macros.tex`, `code/paper1_macros.py`, `code/calibrate_horizons.py`, `code/estimate_v3.py`, `notes/case_bending_spoons_f1_extract.md`, `notes/acquirer_fixes_v2.md`, `notes/panel_v3_build.json`, `notes/calibration_anchor_v3.json`, `data/panel_v3.csv`; the round-1 reports `referee2_finance_accounting.md`, `fable_referee_finance.md` and the accounting and filing items of `panel_risk_audit_regulatory.md` and `panel_investors_bankers.md`. Primary sources read on the web (page reads only): the Audit Analytics Seventeen-Year Review post and Eighteen-Year Review PDF; IRS Notice 2026-11; 17 CFR 229.308 and 26 CFR 1.168(k)-2 (LII); PCAOB AS 2201; Bending Spoons' Q2 2026 Form 6-K exhibits 99.1 and 99.2, the 424B4 summary (first 124,000 characters, the fetch window), the EDGAR full-text search index, and the SEC XBRL companyconcept API for Palantir. No round-2 report (`r2_*`) was read; no repository file was edited. Scratch computations are in `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_fin/check_bridge.py` (recomputes Table S6 from `data/panel_v3.csv`).

---

## 1. Summary and recommendation

The measurement problems that drove the round-1 finance and accounting verdict are largely fixed. The cash-basis score is now stated as after interest paid and cash taxes (ASC 230-10-45-17(c), (d)), with a bridge that adds them back and shows the top-tail decline unchanged (−11.0 against −11.4 points on the same firm-years; I reproduce every cell of Table S6 from `panel_v3.csv`). The Bending Spoons annuity no longer charges financing twice: every row of Table 3 is labeled before or after interest, the charges are set against a cash margin before interest, a user-cost variant and time-weighted capital are added, and the 2025 "charged as capital" range of 87 to 114 reproduces to 0.1 point from the extract. The company is no longer said to report a Rule-of-40 score; its organic growth is described as its own unaudited, estimate-based measure outside the non-GAAP section (I confirm all of this in the 6-K); the material-weakness sentence is quoted verbatim from the prospectus. The accountability floor is a pass/fail constraint with the AS 2201 A7 and Item 308(a)(3) wording correct at source; the 4.6%, 5.8% and 4.8% adverse-attestation rates are exactly what Audit Analytics published. The §168(k) statements (100% allowance for property acquired after 19 January 2025 under §70301 of P.L. 119-21; election out under §168(k)(7); ADS property excluded by 26 CFR 1.168(k)-2(b)(2)(ii)) match Notice 2026-11 and the regulation, and the owned-compute thresholds (16.5%/49.5% at ψ = 1; 33%/74% at ψ = 0) recompute. The captive registrant is excluded (rule R3) and debt-only filers are flagged and dropped in a sensitivity (rule R5, 26 firm-years of 7 firms, matching the build record). The 7-to-13 weight is withdrawn and the capital-intensity gap is reported as an accounting effect.

What remains is narrower than in round 1 and does not overturn a headline, but three items need work before the paper is relied on. (i) The bridge is "before interest paid", not "before interest": interest income stays in operating cash flow, and for the firms that set the 2023-25 top tail and the calibration anchor it is material (Palantir's 2025 interest income was $229.2 million, 5.1% of revenue, from its 10-K XBRL); the text's "adding back interest alone moves the 95th percentile by at most 0.6 points" is true only of interest paid, and the anchor intercepts of cash-rich firms are overstated by a few points. (ii) The direct audit and Section 404 cost of 0.14% at $1 billion has no source row in Table S7, rests on an S&P 500 fee ratio and a $1.04 million SOX cost that is below the $1.5 to $2.7 million by size in the KPMG survey the paper itself cites; the bottom-up floor (0.23%) and the "15 applications" count depend on it. (iii) The 5% "remote" threshold is described as grounded in the adverse-attestation rates, but the inference runs through the example's illustrative parameters (the three-layer all-human design passes by 0.02 points), and the headline "no all-AI design on one provider passes" holds only because the scenario AI common-mode rate (0.005) exceeds the admissibility bound (0.0021 per opportunity at N = 24); Section 7.2 states it without the condition. The rest is labeling: an unexplained X = 2.5, 5, 9 left from placeholder macros; a GAAP-to-cash sequence in the introduction and discussion that still reads as one basis; Bending Spoons' cash scores on operating cash flow before SBC while the panel's basis is after SBC; "the charging convention decides the sign" without "in the year of purchase".

**Recommendation: minor revision.** Counts: 24 round-1 finance and accounting findings tracked below, 14 resolved, 8 partly, 2 not done; 14 new findings (0 major, 3 moderate, 11 minor); 41 numbers checked, 36 matched, 3 partially matched, 2 not matched.

---

## 2. Round-1 status

Status is my verdict, not the response's. "Resolved" means the finding is addressed in the paper as the response claims; "Partly" means part of it is, with the gap stated; "Not done" means the paper is unchanged on the point.

| Round-1 ID | Finding (short) | Response says | My verdict | Evidence |
|---|---|---|---|---|
| R2-F1 / FR-6 | "7 to 13" decision weight not identified | Fixed | Resolved | §5.4 withdraws it; α(X − k) 0.05 to 10.1 across methods; abstract and §7.5 conditional on a stated proxy |
| R2-F2 | Capital-intensity gap driven by capitalized software | Fixed | Resolved | §5.6 "an accounting effect": −12.5 after SBC, −4.6 [−14.6, +6.0] with the deduction added back; "survives" claim withdrawn |
| R2-F3 / FR-3 | Cash score is levered and after actual cash taxes; anchor at τ = 0.18 | Partly | Partly | Basis stated (§4.3); Table S6 bridge reproduces (interest paid and taxes paid added back, P95 +4.8 to +5.2, decline −11.0 vs −11.4). Not done: interest income (see new finding 1); the anchor still applies τ = 0.18 to firms that pay little cash tax; the §174 episode is covered only implicitly by the before-tax row |
| R2-F4 | Pull inferred at X = 1; 156 from the lower-bound case | Fixed | Resolved | Upper ends dropped; §7.3 states that a negative upper-bound surplus means X > 1 or overstated growth spend |
| R2-F5 / FR-4 | Pre-listing years back-filled | Fixed | Resolved | Rule R1 removes 140 firm-years (98 pre-listing, 40 fiscal 2010, 2 other); decline 11.9/12.7 |
| R2-F6 / FR-1 / IB-4 / V12 | Annuity is a timing allocation; double-charged financing; level annuity not matched to decay; intro sequence mixes bases | Fixed | Partly | Remark 4 rewritten (basis, "charge interest or a cost of capital, not both", user cost (r + d), time weighting, PV identity in the appendix); Table 3 labeled by basis; 87 to 114 reproduces. Not done: "the charging convention, not the data, decides the sign" is still unqualified (new finding 8); the intro and discussion still run 115.9 → 105.0 → 87 to 114 as if on one basis (new finding 6) |
| R2-F7 / FR-12 | SIC 7372 is not the Rule-of-40 population | Partly | Partly | R2 applied to 16 named firms only, as a sensitivity; the broad sample dropped; disclosed as partial |
| R2-F8 / FR-5 | E2 mostly exclusion; flag gaps (negative payments, row shift, cheap deals) | Partly | Partly | Imputation bounds; fiscal-year adjacency; R4(b) cheap-acquisition criterion (Xunlei caught); causal wording withdrawn. Not done: absolute value of payments, intangible-asset purchases |
| R2-F9 | ASC 606 / 340-40 / ASU 2021-08 breaks | Not done | Not done | No change; minor |
| R2-F10 / FR-9 / RA-C4 | a_min 4.6% does not reproduce on the core; audit cost mis-scaled | Declined / Fixed / Partly | Partly | Source named (wider universe) and core 5.8% disclosed, which answers FR-9. Audit-cost scaling untouched and now inconsistent with the paper's own KPMG row (new finding 2) |
| R2-F11 / RA-9 / FI-16 | CAMT is not a floor for a $1bn firm; state taxes; fees are card fees | Not done | Not done | §7.2 still "runs from the 15% corporate alternative minimum tax"; Table S7 notes the §59(k) threshold "was not read"; fees unchanged (new finding 11) |
| R2-F12 / FR-7 / RA-C10 / C11 | GAAP channels of acquisitions incomplete; ln NRR; treadmill factor; log vs simple rates; C^acq timing | Fixed | Resolved | Remark 4 lists amortization and impairment, expensed transaction costs (ASC 805-10-25-23) and restructuring; Prop. 8(d) has (S_sub/S)(NRR − 1) and G_i = ln(1 + a); 5% to 9% simple where stated; Table 3 row relabeled "Amortization and impairment"; C^acq a share of current revenue (the within-year run-rate mismatch is stated, not removed) |
| R2-F13 / FR-11 | Deferred revenue; element precedence; continuing-ops OCF with total capex; lease element | Not done | Not done | Supplement S6 lists the elements but not the caveats; minor |
| R2-F14 | Text-code inconsistencies | Partly | Partly | Most moot after the rewrite; T(0) still "among all firm-years" while `Tval` uses g ≥ 0 (number 39 below) |
| FR-2 / IB-5 / V24 | Captive registrant (Exzeo) in the anchor and the 2023-25 tail | Fixed | Resolved | Rule R3 (≥ 50% related-party revenue; XBRL test, none hit, largest SINA 2015 at 26.9%; Exzeo 2025 excluded by filing text); anchor now 13 firm-years of 7 firms without it |
| FR-3 (ii) | Debt-only filers in the core | Partly | Resolved as a sensitivity | Rule R5: 26 firm-years of 7 firms (Epicor, GXS, Infor, Meditech, Serena, SSI Investments II, SunGard per `panel_v3_build.json`); kept in the main sample, dropped in Table S2; foreign filers and 19 "unknown" firm-years untested, disclosed |
| FR-8 | Anchor surplus read as the X = 1 surplus | Fixed | Resolved | §7.3 wording; surplus no longer scaled into upper ends |
| FR-10 | Small text-output mismatches | Fixed | Resolved | Rates, within-firm coefficients and C^acq fixed |
| FR-13 | NRR covers subscription revenue only | Fixed | Resolved | §6 says so twice; G_i "not identified" |
| FR-14 | Quarterly Q2 score: repeat the comparability caveat | Partly | Partly | §6 and §4.6 carry it; the introduction's "about 160" does not |
| RA-1 / C6 / plan C5 | Floor as a pass/fail ICFR constraint | Fixed | Resolved, with a condition | Prop. 5(b)-(c), Remark 6; wording of AS 2201 A7 and Item 308(a)(3) verified at source. The all-AI conclusion is parameter-driven and the threshold grounding is indirect (new finding 3) |
| RA-4 / S4 / S5 / C12 | Bending Spoons: no reported score; organic growth unaudited and estimated; material weaknesses | Fixed | Resolved | §6, §1, §8.3: "does not report a Rule-of-40 score"; organic measure described correctly (verified in 6-K Ex. 99.1 footnote 4); material-weakness sentence verbatim; no 404 assessment; Q1 2026 cash flows restated (phrase present in the F-1 and 424B4 per EDGAR full-text search) |
| RA-7 / C2 / C3 | Filer-status precision; "attest to that assessment"; 18 U.S.C. 1350; AS 2201 B28-B31 | Partly | Partly | EGC and first-report exemptions added. "Attest to that assessment" kept (statutory 404(b) wording; AS 2201.03 opines on ICFR effectiveness); §906 and audit-reliance facts not added (new finding 9) |
| RA-1.3.3 / S7 / S8 | Serial acquirer's ICFR scope lags revenue; ASC 805 pro forma supplemental and unaudited; Article 11 unaudited | Partly (in RA-4) | Partly | "Pro forma statements are unaudited and illustrative" stated; the one-year exclusion of acquired businesses from the assessment is not mentioned |
| RA-3 / plan E2 | "Use in filings" paragraph | Not done | Not done | Sources in Table S7; paragraph absent. Open item, not a correctness issue |
| IB-6 / IB-7 | Even-handed case; measurement lens vs decision rule; interest or cost of capital, not both | Partly | Partly | Organic score after interest (22) and before reorganization (44) given; conclusion carries "not both". No second acquirer; the firm's own hurdle (25% unlevered) not contrasted with the 9.34% WACC used (new finding 10) |

Tally: 24 findings; 14 resolved, 8 partly, 2 not done.

---

## 3. New findings

Severity: major (affects a headline claim), moderate (affects a reported number or a stated conclusion), minor (labeling, consistency, grounding).

### 1. (Moderate) The "before interest" bridge is before interest paid only; interest income remains in the cash margin and is material for the firms that set the top tail and the anchor

**Location.** §4.3; §4.6 ("adding back interest alone moves the 95th percentile by at most 0.6 points"); Table S6 rows "before interest, after tax" and "before interest and cash taxes"; §7.3 anchor and Table 5; `code/estimate_v3.py` block `bridge` (R_cash_bi = g + (FCF − SBC + interest paid × (1 − t))/revenue).

**Issue.** Operating cash flow includes interest received as well as interest paid (ASC 230-10-45-16(b)). The bridge adds back `InterestPaidNet` only. The firms at the 95th percentile of the 2023-25 cash score and in the calibration anchor carry no debt (interest paid is zero for Palantir, Clear Secure, Duolingo, monday.com, Global-E and Cellebrite in `panel_v3.csv`) but hold cash of the order of a year's revenue, and three-month yields averaged about 4.7% in 2023-25 against about 1.3% in 2016-19. So "before interest" overstates what the row removes, the 0.6-point statement understates the interest effect by construction, and the anchor's after-tax intercepts m_0 (median 42, upper quartile 52) include interest income that the model's margin does not.

**Evidence.** Palantir's 10-K XBRL (`InvestmentIncomeInterest`, SEC companyconcept API): $132.6 million (2023), $196.8 million (2024), $229.2 million (2025), that is 6.9% of 2024 revenue and 5.1% of 2025 revenue ($4,475 million). Palantir 2025 is the top anchor firm-year (R = 87.8, m_0 upper bound 51.8); about four points of that intercept, after tax, is interest income. The other anchor firms hold cash of $0.4 to $1.4 billion against revenue of $0.4 to $1.0 billion; their figures were not retrieved and the order of magnitude (2 to 6 points) is inferred from balances, not verified.

**Required change.** Retrieve `InvestmentIncomeInterest` (and the variants `InterestIncomeOther`, `InvestmentIncomeInterestAndDividend`, `InterestAndOtherIncome`) from the same frames; add a row "before net interest" that removes after-tax interest income as well as adding back interest paid; report the anchor intercepts net of after-tax interest income; relabel the existing rows "before interest paid" and change "adding back interest alone" to "adding back interest paid alone". The decline in the top tail will, if anything, widen on the unlevered basis, so no headline changes, but the anchor's starting intercept and Table 5's path shift down by a few points.

### 2. (Moderate) The direct audit and Section 404 cost of 0.14% at $1 billion is unsourced in Table S7 and below the paper's own KPMG figures; the bottom-up floor and the "15 applications" count depend on it

**Location.** §7.2 ("direct audit and Section 404 costs of about 0.14%"); Remark 6 (`rem:amin-values`), last sentence of its first paragraph; `code/paper1_macros.py` line `direct = (343.0 * 1000 + 1.04e6) / REV`; Table S7 (no row for this value); `notes/assumptions_round2.md` line 219.

**Issue.** The 0.14% is $343 of audit fee per $1 million of revenue (an S&P 500 average, fiscal 2022) applied to a $1 billion firm, plus a $1.04 million "median SOX cost" of unstated origin. The paper's own Table S7 row for the KPMG 2025 SOX Survey gives an average SOX budget of $2.3 million, and the round-2 register records budgets of $4.7, $2.7 and $1.5 million by size class. Audit fees per dollar of revenue rise steeply below the S&P 500. The RA panel (C4) and R2 (F10) both raised this; the response records "size-matched audit fees not added" under a declined item about the band's upper end, but the direct-cost line is a separate number that the text now uses to build the floor: 0.14% + 0.090% = 0.23%, and "the floor reaches the band's lower end at about 15 such applications".

**Evidence.** With the KPMG $1.5 to $2.7 million and an audit fee of $1 to $2 million for a $1 billion accelerated filer, direct costs are 0.25% to 0.47% of revenue, the floor 0.34% to 0.56%, and the lower end of the band is reached at 1 to 9 applications rather than 15 (ITGC line $204,672, from the macro). The 0.5% lower end of the band is itself close to being met by direct costs alone.

**Required change.** Add a Table S7 row for the direct cost with a size-matched source (Audit Analytics fee-per-revenue by filer status, or the KPMG budget by size), recompute `AminDirect`, `AminFloor`, `ItgcApps` and `ItgcAppsFb`, and say that the previous 0.14% used an S&P 500 fee ratio. Alternatively label the 0.14% "illustrative, likely understated at $1 billion" in Remark 6 and §7.2 and drop the applications count from the main text.

### 3. (Moderate) The "remote" threshold is not grounded by the adverse-attestation rates in the way the text implies, and the all-AI conclusion is stated in §7.2 without its parameter condition

**Location.** Prop. 5 intuition ("we use 5% a year, grounded in the share of adverse auditor attestations"); Remark 6; §7.2 ("No design that uses AI layers on a single provider alone passes, however many layers it stacks, because their common-mode failure is more than remote"); Table S7 row "Remote threshold" (class b); response summary item 5.

**Issue.** (a) The adverse rate is the share of filers whose controls have a material weakness; it is a population frequency, not a per-objective probability threshold, and it says nothing about where "reasonable possibility" lies. The paper's inference is: the example's three-layer all-human design has an annual miss probability of 4.98%; most filers' human-run controls are found effective; so the threshold must be at least about 5%. That uses the example's own illustrative values (p = 0.05, p_cm = 0.002, N = 24), which the Remark itself says "are not calibrated to an effective control environment". The all-human design passes the central threshold by 0.02 points (4.98% against 5%), so the threshold is in effect chosen to admit the reference design. Grounding class b ("by precedent") overstates this; it is a scenario value (class d) with a plausibility check. (b) The statement that no all-AI design on one provider is admissible holds if and only if p_cc + (1 − p_cc) p_cm^AI ≥ P̄ = 1 − 0.95^(1/24) = 0.00213 per opportunity. It holds at the scenario p_cm^AI = 0.005 (limit 11.3% a year) and fails at p_cm^AI = 0.002, the human value, at which three AI layers pass (4.7%). Remark 6 and §8.5 say "in the example"; §7.2 and the response summary present it as a result.

**Evidence.** Arithmetic from Remark 6's parameters (my recomputation agrees with every printed probability: 3.1%, 0.7%, 5.0%, 11.3%, 4.7%, 3.6%). Audit Analytics: 4.6% (fiscal 2020), 5.8% (2021), 4.8% (2019), verified at source.

**Required change.** In Prop. 5's intuition and Table S7, call the 5% a judgment consistent with (not grounded in) the attestation evidence and reclassify it as class d; state the admissibility bound P̄ explicitly and the condition p_cm^AI ≥ P̄ under which the all-AI conclusion holds; in §7.2 write "in the example of Remark 6, with an AI common-mode rate of 0.5% per opportunity, no all-AI design ... passes"; note that the all-human reference design passes the central threshold with 0.02 points to spare.

### 4. (Minor) Unexplained weights X = 2.5, 5 and 9 left from placeholder macros

**Location.** §6, paragraph "Charging acquisitions as capital": "At X = 2.5 that holds for Eventbrite (1.7) and AOL (2.3) but not for Vimeo (3.2); at X = 5 and X = 9 it holds for all three"; `sections/measurement_acquired.tex` lines 48-49 (`% XBOUNDS ... placeholders for the bounds on X`); `acquired_macros.tex` (`\acqXbOne` to `\acqXbThree`); `notes/acquirer_fixes_v2.md` §4.

**Issue.** The paper withdrew the 7-to-13 weight and says the data do not identify X. The three values are placeholders "until the bounds land" (acquirer notes) and nothing in the text motivates them; a reader will take them as estimates.

**Required change.** Replace with the statement that follows from part (a) alone: the full-charge sign flips at X = k^acq, between 1.7 and 3.2 times revenue, so a firm whose weight exceeds 3.2 gains on all three deals and one at the Rule-of-40 weight loses on all three; delete the three numbers or tie them to the §5.4 range.

### 5. (Minor) Bending Spoons' cash scores are on operating cash flow before SBC and before capital expenditure, while the panel's basis is free cash flow after SBC

**Location.** Table 3 rows "Cash, after interest paid", "Cash, before interest (uncharged)", the charged rows and their notes; §4.6 ("treat the latter as the economically relevant one").

**Issue.** The paper's cash basis deducts SBC and capital expenditure; the case uses `Net cash from operating activities` and deducts neither. Capital expenditure is immaterial (0.2% of investing outflow in H1 2026, stated), but equity compensation expense was $43.0 million in H1 2026, 3.3% of revenue (6-K Ex. 99.2, in the extract), and the F-1 cash-flow statement carries the 2023-25 figures as a non-cash add-back. The uncharged cash score of 125.2 and every charged score are therefore on a more generous basis than the 44.6-point 95th percentile they are implicitly compared with.

**Required change.** Take stock-based compensation for 2024 and 2025 from the F-1 cash-flow statement and show the cash rows after SBC, or state in the Table 3 notes that the rows are before SBC and by how much that differs from the panel's basis (about 3 points in 2026).

### 6. (Minor) The introduction and discussion still run the GAAP score into the cash-basis charged range as if on one basis

**Location.** §1 ("Its 2025 GAAP score ... is 115.9 before interest and 105.0 after; charging its acquisitions as capital, against a margin before interest ..., puts it between 87 and 114"); §8.3 ("the 2025 GAAP score of 115.9 falls to 105.0 after interest, and to between 87 and 114 when acquisitions are charged as capital against a margin before interest").

**Issue.** The 87 to 114 range is built on the cash margin before interest (uncharged 125.2), not on the GAAP margin; "falls to between 87 and 114" after "falls to 105.0" is the round-1 F6(e) sequence in new clothes, and the upper end (114) exceeds the after-interest GAAP score it follows. Table 3 is now labeled correctly; the summary sentences are not.

**Required change.** "On the cash basis, its uncharged score before interest is 125.2 and, with acquisitions charged as capital, 87 to 114."

### 7. (Minor) Interest paid for 2023-25 is in the F-1 and should replace interest expense in the add-back

**Location.** §6 "Worked numbers" ("Interest paid for 2024 and 2025 is not in the documents we read, so we add back interest expense"); Table 3 notes; `notes/acquirer_fixes_v2.md` §7.

**Issue.** The EDGAR full-text search index returns the F-1 (8 June 2026), the F-1/A and the 424B4 for the phrase "Interests paid", so the annual supplemental cash-flow disclosure exists; it lies beyond the agents' 124,000-character fetch window, not outside the documents. Interest expense includes non-cash interest ($15.8 million of $200.1 million in H1 2026), so the add-back is too large by about 10 to 20% of c_fin (1 to 2 points of 2025 revenue), as the text says in direction but not in size.

**Required change.** Read the F-1's cash-flow statement in full (it is one file; the browser session that read the pro forma statements can reach it) and use cash interest paid; keep the interest-expense proxy only if the figure cannot be reached, with the 80 to 90% ratio quantified as a correction.

### 8. (Minor) "The charging convention, not the data, decides the sign" is a single-year statement

**Location.** §6, paragraph "Charging acquisitions as capital"; Remark 4; Appendix (Supplementary) proof that CRF(r, T) ∫ e^(−rt) dt = 1 and ∫ (r + d) e^(−(r+d)t) dt = 1.

**Issue.** The appendix now proves that the annuity and the user cost repay a dollar at r, so they have the same present value as the full charge. Over the life of a deal the Rule-of-40 sign at X = 1 is therefore set by k^acq against one under every convention; only the year-of-purchase score differs. The sentence is still unqualified, and it is the one a practitioner will quote.

**Required change.** "In the year of purchase, the charging convention, not the data, decides the sign; in present value the three conventions agree, and the sign is set by k^acq against X (part (a))."

### 9. (Minor) §8.5 wording on the auditor's attestation and the missing §906 citation

**Location.** §8.5, first paragraph.

**Issue.** "The auditor of an accelerated filer must attest to that assessment in an integrated audit performed under PCAOB Auditing Standard 2201" uses the statutory wording of SOX 404(b) ("attest to, and report on, the assessment made by the management") while citing AS 2201, under which the auditor expresses an opinion on the effectiveness of ICFR (AS 2201.03, verified). "Accelerated filer" should read "accelerated or large accelerated filer that is not an emerging growth company" (Item 308(b), verified), although the next sentence supplies the EGC exemption. "Sections 302 and 906" cites 15 U.S.C. §7241 only; §906 is 18 U.S.C. §1350.

**Required change.** One sentence and one citation.

### 10. (Minor) The cost of capital used to charge the acquirer's capital is a sector average below the firm's own marginal cost of debt

**Location.** §6 ("we take r = 8.93%, the continuously compounded value of a 9.34% cost of capital for software firms"); Table 3 notes; extract (notes priced 28 October 2026 at 9.625% and 8.625%; Moody's Ba3; stated hurdles of 25% unlevered and 65% levered).

**Issue.** A WACC of 9.34% built on 5% debt weight and a 5.3% pre-tax cost of debt is below the coupon on the firm's new senior secured notes and far below the hurdle the firm says it applies. The sensitivity (1.2 to 2.1 points per point of r) is given, so the reader can adjust, but the base case should say it is a sector figure, not the firm's.

**Required change.** State that r is a sector average; add one line at the firm's marginal cost of debt (9.19% continuously compounded, which the acquirer notes already compute) or at its own unlevered hurdle.

### 11. (Minor) Tax and fee statements carried over from round 1

**Location.** §7.2 "Taxes, fees and compute"; Table S7 "Cash tax rate".

**Issue.** The range "runs from the 15% corporate alternative minimum tax" although the CAMT applies only to corporations with average adjusted financial statement income above $1 billion (26 U.S.C. §59(k)), which excludes the $1 billion-revenue reference firm; Table S7 says the threshold "was not read". Fees of 2 to 3% are card-processing fees applied to all revenue. The §168(k) remark is correct; this is the one tax statement still wrong in substance. The response lists both as not done.

**Required change.** "A scenario range of 15 to 21%; the 15% end is not the CAMT, which applies only above $1 billion of adjusted financial statement income"; ground fees by revenue channel or label them a scenario.

### 12. (Minor) Table S6 bridge conventions to disclose

**Location.** Table S6 notes; §4.6; `code/build_panel_v3.py` rule "a missing element is zero when the firm-year reports any of the four".

**Issue.** (a) Treating a missing interest-paid element as zero when only taxes paid is tagged conflates true zeros (debt-free firms) with untagged values; report how many of the 1,762 bridge firm-years tag both elements. (b) The "before interest, after tax" row applies the U.S. federal statutory rate (35%/21%) to every firm, including Israeli, Irish and Cayman filers in the top tail (monday.com, Global-E, Cellebrite). (c) `IncomeTaxesPaidNet` can be negative (a net refund; Gen Digital fiscal 2023 carries −$476 million in `panel_v3.csv`), which lowers the "before taxes" score; say that refunds are netted. (d) The text's "22% to 28%" return on acquisition capital spans τ = 0 and 24% while Table 3's "22.3 to 25.8%" is at 24% only; say so where the text quotes the wider range.

**Required change.** Four sentences in the notes.

### 13. (Minor) Owned-compute sentence in §7.2 conflates electing out with no deduction

**Location.** §7.2, "Capital" bullet: "a firm that elects out of the allowance, or whose servers are abroad, faces a higher bar, 33% and 74% if the servers cannot be deducted when bought".

**Issue.** A firm that elects out of §168(k) still depreciates under MACRS (ψ ≈ 0.8 to 0.85), which gives bars of about 20% and 54% at τ = 0.18, not 33% and 74%; the latter are the ψ = 0 lower bound, which Remark 7 labels correctly. The §7.2 sentence hedges with "if ... cannot be deducted", but the pairing with "elects out" misleads.

**Required change.** "... a higher bar: about 20% and 54% if it elects out and depreciates the servers over five years, and 33% and 74% at the lower bound ψ = 0."

### 14. (Minor) Residual text-code mismatch: T(0)

**Location.** §5.2 ("The 95th-percentile GAAP margin among all firm-years, T(0)"); `code/estimate_v3.py`, `Tval` (g ≥ g0 with g0 = 0).

**Issue.** T(0) is computed over firm-years with nonnegative growth, as in v1; the response says this item was not checked.

**Required change.** "among firm-years with nonnegative growth".

---

## 4. Numbers checked

"Matched" means the paper's figure agrees with the primary source or my recomputation at the precision printed; "Partial" means the number is right but its label, basis or source is not; "Not matched" means it does not reproduce or contradicts a source.

| # | Item (location) | Paper | Source / recomputation | Result |
|---|---|---|---|---|
| 1 | Adverse 404(b) attestations, fiscal 2020 (Remark 6, Table S7) | 4.6% | Audit Analytics, Seventeen-Year Review post, 2 Nov 2021: "4.6% of SOX 404(b) auditor attestations disclosed ineffective controls" | Matched |
| 2 | Fiscal 2021 and 2019 (Remark 6) | 5.8%; 4.8% | Eighteen-Year Review PDF: "5.8% of all auditor attestations filed for fiscal year 2021 ... an increase from the 4.8% seen in 2019" | Matched |
| 3 | §168(k): 100% allowance for property acquired after 19 Jan 2025 under §70301 of P.L. 119-21; 40% election; election out under §168(k)(7) (Remark 2) | as stated | IRS Notice 2026-11 §§2.02(1), 2.05, 3.07, 4.03 | Matched |
| 4 | ADS property excluded from the allowance (Remark 2) | 26 CFR 1.168(k)-2(b)(2)(ii) | LII: sub-paragraph (b)(2)(ii)(B), "required to be depreciated under the alternative depreciation system of section 168(g)" | Matched |
| 5 | Item 308(a)(3): management may not conclude ICFR effective with a material weakness; (b) accelerated and large accelerated filers other than EGCs; Instruction 1 transition (Prop. 5, §8.5) | as stated | LII, 17 CFR 229.308 | Matched |
| 6 | AS 2201 A7 definition and the FAS 5 note; AS 2201.03 opinion on ICFR effectiveness (Prop. 5) | as stated | pcaobus.org AS 2201 | Matched (see finding 9 for §8.5's "attest to that assessment") |
| 7 | Bending Spoons Q2 2026 revenue and growth (Table 3) | $704.2M; 126.3% | 6-K Ex. 99.1: 704,155 vs 311,100 → 126.34% | Matched |
| 8 | Q2 2026 operating margin, interest, reorganization, transaction, amortization and impairment, adjusted margin | 34.1%; 15.5%; 7.2%; 0.9%; 11.7%; 54.1% | 240,251; 108,970; 50,799; 6,553; 82,310; 381,149 over 704,155 | Matched |
| 9 | Organic growth 3%, definition, placement, reconciliation, no Rule-of-40 score (§6) | as stated | Ex. 99.1 footnote 4 verbatim ("including estimated pre-acquisition revenue, where applicable"); under operating results, not non-GAAP; not reconciled; phrase "Rule of 40" absent | Matched |
| 10 | Q2 2026 scores: reported, after interest, organic, organic after interest, organic before reorganization, both, adjusted | 160.5; 145.0; 37.1; 21.6; 44.3; 28.9; 180.5 | recomputed: 160.46; 144.98; 37.08; 21.60; 44.29; 28.81; 180.47 | Matched |
| 11 | Interest paid / interest expense, H1 2025 and H1 2026 (§6) | 90%; 80% | Ex. 99.2: 49,737/(19,316+35,733) = 90.4%; 161,153/(93,184+108,970) = 79.7%. "Interests paid" sits in the supplemental disclosure, which is consistent with operating classification under ASC 230 | Matched |
| 12 | H1 2026 acquisitions, PP&E, investing; shares (§6, Table 3 notes) | $2,286M; $4.0M; 99.8%; 0.2% | Ex. 99.2: 2,286,259; 3,969; 2,290,228 | Matched |
| 13 | Basis of preparation (Remark 4, §6) | U.S. GAAP | Ex. 99.2 Note 1 "prepared in conformity with U.S. generally accepted accounting principles"; 424B4 "in accordance with GAAP" (U.S.) | Matched |
| 14 | 2025 revenue, operating income, interest expense, OCF, investing (Table 3) | $1,306.4M; 21.3%; 10.9%; 22.2%; 141.8% | 424B4 summary: 1,306,404; 277,851; 142,601; 290,600; (1,851,874) | Matched |
| 15 | NRR 2023 to Q1 2026 (§6) | 93, 91, 95, 94% | 424B4: "93% in 2023, 91% in 2024, 95% in 2025, and 94% in Q1 2026" | Matched |
| 16 | Material-weakness sentence (§6) | verbatim | 424B4 summary risk factor, same words | Matched |
| 17 | 2025 growth, simple and continuous (§6) | 94.7%; 66.6% | 1,306,404/671,053 − 1 = 94.68%; ln = 66.6% | Matched |
| 18 | 2025 scores: GAAP before and after interest; cash after interest paid; cash before interest at τ = 24% and 0; fully charged | 115.9; 105.0; 116.9; 125.2; 127.8; −16.5 | recomputed 115.95; 105.03; 116.92; 125.22; 127.84; −16.53 | Matched |
| 19 | r, T^life, CRF (§6) | 8.93%; 10.6 to 19.5; 14.6% to 10.8% | ln 1.0934 = 0.0893; 1/0.09431, 1/0.05129; r/(1 − e^(−rT)) = 0.1459, 0.1083 | Matched |
| 20 | 2025 charged scores: level annuity year-end and time-weighted; user cost year-end and time-weighted (τ = 24%) | 92.7–101.1; 104.4–111.3; 87.2–95.2; 100.9–108.0 | recomputed from the extract with the stated timing: 92.7–101.1; 104.4–111.3; 87.2–95.1; 100.9–108.0 | Matched (±0.1) |
| 21 | Range across conventions and τ; after-interest (double-charged) range; double charge | 87–114; 79–103; 8.3 and 10.9 | 87.2–113.9; 78.9–103.0; 0.76 × 10.92 = 8.30; 10.92 | Matched |
| 22 | Return on acquisition capital, before and after depreciation (Table 3 at τ = 24%; text at τ = 0 and 24%) | 22.3–25.8% / 13.6–19.8%; 22–28% / 14–22% | time-weighted decayed capital $1,545M to $1,787M; 398,977 and 433,201 over it; minus d | Matched; the text range spans both tax rates while the table is at 24% (finding 12(d)) |
| 23 | 2024: cash before interest; annuity year-end; fully charged | 107.6; 84.5–90.5; −25.0 | 204,895 + 0.76 × 32,605 over 671,053 = 34.23%; CRF × 1,059,948 | Matched |
| 24 | Q1 2026: m^cf, cash before interest, fully charged | 24.4%; 156.6; −117.5 | 75,654 + 0.76 × 93,184 over 601,321; 132.2 + 24.4; − 274.1 | Matched |
| 25 | Deal multiples; pro forma revenue and ratio; points per point of growth | 1.7/2.3/3.2; $2,608.5M, 2.0x; −0.7 to −2.2; +0.19 to +0.59 | 505/291.8 = 1.73; 1,454/633.4 = 2.30; 1,359/(376.9 × 365/327) = 3.23; 2,608,496/1,306,404 = 1.997; 1 − k; CRF × 1.73 = 0.187, (r + d) × 3.23 = 0.593. Pro forma figures rest on the extract (beyond the fetch window) | Matched |
| 26 | Flag arithmetic (§6) | 2.3x, 2.8x; 11%, 9%; 1.5x; 100%; 17 points at 50% | 889,654/387,067; 1,851,874/671,053; 25%/2.30, 25%/2.76; 2,010/1,306; 99.7%; 25/1.5 | Matched |
| 27 | Table S6, E1 rows: P95 2016–19 and 2023–25, cash (paper), bridge firm-years, before interest after tax, before interest and taxes; changes | 57.3/44.6; 56.0/44.6; 56.6/44.7; 60.8/49.8; −11.4, −11.0 | recomputed from `panel_v3.csv` with the stated rule: 57.29/44.59; 56.04/44.59; 56.62/44.69; 60.80/49.78; −11.45, −11.02 | Matched |
| 28 | §4.6 bridge sentence: lift 4.8 to 5.2; interest alone ≤ 0.6 | as stated | 60.80 − 56.04 = 4.76; 49.78 − 44.59 = 5.19; 56.62 − 56.04 = 0.58 | Matched as "interest paid"; "interest alone" is mislabeled (finding 1) |
| 29 | Rule R5 counts (§4.2) | 26 firm-years, 7 firms | `panel_v3_build.json`: Epicor, GXS, Infor, Meditech, Serena, SSI Investments II, SunGard; 26 | Matched |
| 30 | Rule R3 (§4.2) | 74 firm-years with the element; none ≥ 50%; largest 26.9% (SINA 2015); Exzeo 2025 excluded | `macros.tex` VRthreeXbrlN 74, VRthreeMax 26.9, VRthree 1; anchor file without Exzeo | Matched |
| 31 | Ceiling bases and thresholds (Table 4) | 78.1/21.9; 69.0/31.0; 54.5/45.5; 40.3/59.7 | (1 − τ)(1 − c_c − f − a_min − c_full): 0.85 × 0.9185; 0.82 × 0.842; 0.79 × 0.69; 0.82 × 0.492 | Matched |
| 32 | a_min and τ sensitivities (§7.2) | 29–32; 28–33; 23 at 9% | 0.82 × 0.867 → 28.9; 0.82 × 0.826 → 32.3; 0.85/0.79/0.91 × 0.842 | Matched |
| 33 | Capital sensitivities (§7.2, Table 4 notes) | 45; 36–38; 40–41; 9.5; 10.25 | kG = 45; (1 − τ) × 45; (1 − 0.53τ) × 45; 0.21 × 1.5 × 0.3; 0.82 × 0.125 | Matched |
| 34 | ψ_15, ψ_5 (Remark 2) | 0.53; 0.80 | eq. (psiT) at r = 0.10: 0.5324; 0.7961 | Matched |
| 35 | Owned-compute markups (Remark 7, §7.2) | 16.5%/49.5% at ψ = 1; 33%/74% at ψ = 0 | s L G = 3.3G; [τ s + 3.3G]/(1 − τ) at τ = 0.18 | Matched |
| 36 | ICFR example probabilities and costs (Remark 6) | 1H+1AI 3.1%, $0.90M, 0.090%; 1H+2AI 0.7%, $0.95M, 0.095%; 3H 5.0%, $1.50M; all-AI limit 11.3%; all-human limit 4.7%; N = 48 → 1H+2AI; p_cm 0.01 → 3.6% | P = Π[p_cm + (1 − p_cm)p^n], π = 1 − (1 − P)^24: 3.05%, 0.67%, 4.98%, 11.33%, 4.69%, 6.0% → 1.3%, 3.65% | Matched (3H passes by 0.02 points) |
| 37 | Direct audit and 404 cost (Remark 6, §7.2) | 0.14% | macro: ($343k + $1.04M)/$1bn = 0.138%; KPMG survey in Table S7 and the register: $2.3M average, $1.5 to $2.7M by size | Not matched to the paper's own source (finding 2) |
| 38 | ITGC line, fallback, applications (Remark 6, §7.2) | 0.020%; 0.04%; 15; 8 | 2,000 × 15 + 2,500 × 24 + 24,000/1.22 + 55,000 + 10,000 × 4 = $204,672; + $161,000; 1 + ceil((0.5 − 0.228)/0.0205) = 15; 8 | Matched (conditional on finding 2) |
| 39 | T(0) definition (§5.2) | "among all firm-years" | `estimate_v3.py` `Tval`: g ≥ 0 | Not matched (finding 14) |
| 40 | Palantir 2025 interest income (new evidence for finding 1) | not in the paper | SEC companyconcept `InvestmentIncomeInterest`: $229,181k (2025), $196,792k (2024); 5.1% and 6.9% of revenue | Partial: paper's "before interest" rows omit it |
| 41 | §8.5 "auditor of an accelerated filer must attest to that assessment ... under AS 2201" | as stated | SOX 404(b) statutory wording; AS 2201.03 is an opinion on ICFR effectiveness; Item 308(b) scope | Partial (finding 9) |

Tally: 41 items; 36 matched, 3 partial (28, 40, 41), 2 not matched (37, 39).

---

## 5. What is now right

- Every Bending Spoons figure in Table 3 and §6 that I could reach at source (6-K exhibits 99.1 and 99.2 in full; the 424B4 summary) is correct, and every derived score, charge, return and multiple reproduces from the extract to the printed precision, including the new user-cost and time-weighted rows.
- The accounting statements are now accurate: ASC 230-10-45-17(c) and (d) for taxes and interest paid; ASC 805-10-25-23 for acquisition-related costs; amortization and impairment of acquired intangibles, transaction costs and restructuring as the GAAP channels; goodwill not amortized; organic growth described as the company's own unaudited, estimate-based measure outside the non-GAAP section; no Rule-of-40 score attributed to the company; material weaknesses, no 404 assessment, restated Q1 2026 cash flows and unaudited pro forma statements disclosed.
- "Charge interest or a cost of capital on the same capital, not both" is the right principle and is carried into the conclusion's practitioner list; the double charge is sized correctly at (1 − τ)c_fin.
- The statutory and regulatory citations on ICFR and depreciation hold at source: Item 308(a)(3), (b), (c) and Instruction 1; AS 2201.03 and A7 with the FAS 5 note; §168(k) as amended by P.L. 119-21 and Notice 2026-11; §168(k)(7); 26 CFR 1.168(k)-2(b)(2)(ii)(B); §174A for domestic R&E and §174 for foreign.
- The panel's basis is stated and bridged; the bridge is reproducible from the distributed panel; the sample rules R1, R3, R4 and R5 are implemented as described and their counts match the build record.
- The "7 to 13" weight, the E1–E2 attributions, the T(40%) estimate under E2 and the capital-channel reading of the cash gap are withdrawn in the text, not only in the response.
