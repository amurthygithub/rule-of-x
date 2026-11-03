# Auditor's Report — Bending Spoons S.p.A. Case (Section 6, Table 3, Supplement S4)

**Auditor role:** corporate-finance / accounting / acquisition-measurement referee
**Date:** 2026-11-03
**Scope:** Independent audit of the paper's Bending Spoons case study, reproducing Table 3 and the charged-as-capital scores, verifying the accounting claims, the acquisition-flag logic, Proposition 8, and the "fully charged = lower bound" claim.

**Blind-pass compliance:** I did not read anything under `notes/reviews/`. All figures below come from the paper, `notes/case_bending_spoons_f1_extract.md`, `notes/acquirer_notes.md`, `data/v3_inputs/bending_spoons_cash_interest.json`, `data/v3_inputs/raw/bending_spoons_6k_2026-11-02.json`, and `code/verify_part2_acquirer.py`.

---

## 1. Headline conclusion

**No arithmetic error, sign error, or double-count was found in the paper.** Every Table 3 figure I checked reproduces exactly from the repo's extracted data. The accounting claims (ASC 230 / ASC 350 / ASC 805) are correctly stated. Proposition 8's "net weight X − k_acq" is algebraically exact. The "fully charged is a lower bound" claim is correct given the Vimeo timing mismatch. The verification script `verify_part2_acquirer.py` runs clean (82/82 checks pass) and its generated macro file `sections/tables/acquired_macros.tex` matches Table 3 digit-for-digit.

I found **one internal documentation inconsistency** (not a paper error) and **one disclosed measurement choice** worth flagging, both described in §7.

---

## 2. Reproduced Table 3 numbers

Underlying thousands (from the F-1 extract markdown, unchanged in the 424B4):

| | 2023 | 2024 | 2025 | Q1 2025 | Q1 2026 |
|---|---|---|---|---|---|
| Revenue | 387,067 | 671,053 | 1,306,404 | 258,946 | 601,321 |
| Operating income | 84,267 | 127,352 | 277,851 | (4,615) | 120,171 |
| Interest expense | 17,173 | 32,605 | 142,601 | 19,316 | 93,184 |
| OCF | 59,154 | 204,895 | 290,600 | 21,350 | 75,654 |
| Investing CF | (170,294) | (889,654) | (1,851,874) | (485,746) | (1,647,942) |

### Growth, margins, interest (all reproduce ✓)

| Item | Paper | My recomputation |
|---|---|---|
| Revenue 2024 / 2025 | $671.1m / $1,306.4m | 671,053 / 1,306,404 ✓ |
| Growth g 2024 | 73.4% | 671,053/387,067 − 1 = 73.37% ✓ |
| Growth g 2025 | 94.7% | 1,306,404/671,053 − 1 = 94.68% ✓ (66.62% c.c., paper says 66.6% ✓) |
| GAAP op. margin 2024 / 2025 | 19.0% / 21.3% | 127,352/671,053 = 18.98% ; 277,851/1,306,404 = 21.27% ✓ |
| Interest c_fin 2024 / 2025 | 4.9% / 10.9% | 32,605/671,053 = 4.86% ; 142,601/1,306,404 = 10.92% ✓ |

### Score computations (all reproduce ✓)

| Score | Paper | Recomputation |
|---|---|---|
| g + m_op 2024 / 2025 | 92.3 / 115.9 | 73.37+18.98 = 92.35 ; 94.68+21.27 = 115.95 ✓ |
| g + m_op − c_fin 2024 / 2025 | 87.5 / 105.0 | 73.37+14.12 = 87.49 ; 94.68+10.35 = 105.03 ✓ |
| g + OCF/S 2024 / 2025 (after interest) | 103.9 / 116.9 | 73.37+30.53 = 103.90 ; 94.68+22.24 = 116.92 ✓ |
| g + m^cf 2024 / 2025 (before interest, τ=24%) | 107.6 / 125.2 | 73.37+34.22 = 107.59 ; 94.68+30.54 = 125.22 ✓ |

where m^cf = OCF/S + (1−τ)·interest/S at τ = 24% (Italy IRES): 2024 = 30.53% + 0.76×4.86% = **34.22%**; 2025 = 22.24% + 0.76×10.92% = **30.54%**. Table 3's "Cash margin before interest m^cf" = 34.2% / 30.5% ✓.

**Q1 2026 column** also reproduces: growth 132.2% (601,321/258,946 − 1 = 132.22%); op margin 20.0% (120,171/601,321 = 19.98%); interest 15.5% (93,184/601,321 = 15.50%); OCF margin 12.6% (75,654/601,321 = 12.58%); m^cf 24.4% (12.58% + 0.76×15.50% = 24.36%); outflow/revenue 274.1% (1,647,942/601,321 = 274.05%); fully charged −117.5 (132.22 + 24.36 − 274.05 = −117.5). ✓

**Q2 2026 column**: growth 126.3% (704,155/311,100 − 1); GAAP margin 34.1% (240,251/704,155); score 160.5 ✓; interest 15.5% (108,970/704,155); organic score 37.1 (=3+34.1), after interest 21.6, before reorg 44.3. ✓ (All match the extract's Q2 tables and the code's A12/A14.)

### Non-GAAP / add-back shares (all reproduce ✓)

| Item | Paper | Recomputation |
|---|---|---|
| Amort. & impairment of acquired intangibles 2024 / 2025 | 12.8% / 11.5% | 85,947/671,053 = 12.81% ; 150,532/1,306,404 = 11.52% ✓ |
| Transaction expense 2024 / 2025 | 4.8% / 6.5% | 31,952/671,053 = 4.76% ; 85,466/1,306,404 = 6.54% ✓ |
| Reorganization expense 2024 / 2025 | 7.7% / 6.0% | 51,792/671,053 = 7.72% ; 78,607/1,306,404 = 6.02% ✓ |
| Adjusted margin score 2025 | 141.6 | 94.68 + 613,247/1,306,404 (=46.94%) = 141.62 ✓ |
| Net investing outflow / revenue 2024 / 2025 | 132.6% / 141.8% | 889,654/671,053 = 132.58% ; 1,851,874/1,306,404 = 141.75% ✓ |

---

## 3. Charged-as-capital scores (Table 3 rows for 2025; §E of the script)

I ran `python3 code/verify_part2_acquirer.py` (exit 0, 82/82 checks pass) and independently re-derived the numbers. Key facts:

- **r = 8.93%** continuous (= ln 1.0934, the 9.34% Damodaran software WACC preset); **d = −ln NRR**; **T_life = 1/d**. NRR range 91%–95% → T_life 10.6–19.5 years, CRF 14.59%–10.83% (code E8 output). ✓
- Outlays charged since 2023 (net investing outflow by year, negative CFI): 2023 = 170,294k, 2024 = 889,654k, 2025 = 1,851,874k.
- Timing: 2023/2024 at mid-year; 2025 by quarter/half-year (Q1 2025 = 485,746k, H1 2025 = 575,563k), second-half 2025 outlays placed between mid-H2 (t=0.75) and Vimeo's close (t = 327/365 = 0.8959).

**Fully charged lower bound (before interest, τ = 24%) — REPRODUCED ✓:**

- 2024: g + m^cf − outflow/S = 73.37 + 34.22 − 132.58 = **−25.0**
- 2025: 94.68 + 30.54 − 141.75 = **−16.5**

These match Table 3's "Fully charged, before interest (lower bound): −25.0 / −16.5" exactly (macro `acqRAllInvUTwentyFour/Five` = −25.0 / −16.5).

**Charged-as-capital range — REPRODUCED ✓** (Table 3 shows the τ=24% cells; the paper text's "87 to 114" spans both tax rates):

| Convention (τ=24%) | 2025 |
|---|---|
| level annuity, year-end capital | 92.7 – 101.1 ✓ |
| level annuity, time-weighted capital | 104.4 – 111.3 ✓ |
| user cost (r+d), year-end capital | 87.2 – 95.2 ✓ |
| user cost (r+d), time-weighted capital | 100.9 – 108.0 ✓ |

Overall 2025 charged range across **all conventions × lives × timings × τ∈{0,24%}** = **87.2 to 114.0** → the paper's "87 to 114" ✓ (macro `acqConvLo/Hi` = 87/114). At τ=0 the add-back is gross interest, lifting the before-interest scores by τ·c_fin = 0.24×10.9 = 2.6 points, which is how the top of the range reaches 114.

**Return on acquisition capital (τ=24%, Table 3):** 22.3%–25.8% before / 13.6%–19.8% after depreciation — matches macros `acqRetTauLo/Hi` and `acqRetNetTauLo/Hi` ✓. (The paper text's "22% to 28%" and "14% to 22%" are the wider ranges spanning τ∈{0,24%}; the code's E14 confirms 22–28% / 14–22%.)

**Interest-paid sensitivity (S4.1):** "adding back interest paid instead of interest expense moves the 2025 charged scores to 86.6 to 113.1" — code F1 confirms 86.6–113.1 (interest expense 87.2–114.0) ✓. Interest paid figures (424B4 F-34/F-35 and F-6/F-7): 2023 = 16,581k (4.3%), 2024 = 19,168k (2.9%), 2025 = 130,881k (10.0%), Q1 2026 = 89,037k (14.8%) — all match `bending_spoons_cash_interest.json` and S4.1 ✓. Coupon-charged scores 86.0–112.8 (code F2) match line 2535 ✓.

---

## 4. Accounting claims — all CORRECT ✓

1. **ASC 230-10-45-17(d): interest paid is an operating cash flow.** Correct. Under U.S. GAAP cash payments to lenders/creditors for interest are operating outflows, so operating cash flow is *after* interest paid. The paper's inference that the cash score g + OCF/S is "after interest" is sound. (The 6-K Ex. 99.2 basis is "prepared in conformity with U.S. GAAP," per the extract.)
2. **ASC 350-20-35-1: goodwill is not amortized.** Correct. Goodwill is tested for impairment (at least annually), not amortized.
3. **ASC 805-10-25-23: acquisition-related costs are expensed.** Correct. They are expensed as incurred (one exception: debt/equity issuance costs).
4. **"Charge interest OR a cost of capital, not both" (Remark 4 / double-counting).** Correct, and quantitatively pinned: because OCF is after interest paid, charging a cost of capital r (which includes the cost of debt) against OCF-as-reported double-charges the debt-financed share by exactly **(1−τ)·c_fin** = 8.3 points at τ=24% and 10.9 at τ=0 (code E12, verified exactly). The fix — use the before-financing margin m^cf (add back interest net of tax) before charging r — is the standard unlevered/FCFF treatment and is applied correctly throughout Table 3.

---

## 5. Acquisition-flag logic and Proposition 8 — CORRECT ✓

**Proposition 8(a):** R^A_X = X(g_org + g_acq) + m − k_acq·g_acq = R^org_X + (X − k_acq)·g_acq. The derivative in g_acq is X − k_acq. So **acquired growth enters at net weight X − k_acq**; it raises the score iff k_acq < X (and the Rule-of-40 score iff k_acq < 1). Algebraically exact (code E1/E2 symbolic). ✓

**The flag (Section 4):** flags a firm-year when cash paid for acquisitions / goodwill increase ≥ 25% of prior-year revenue, or pro forma revenue > actual by 10%, and flags the following year. The cash threshold's relationship to (31) is arithmetic: a firm flagged on cash (≥0.25·S_{t−1}) growing at g carries a fully-charged correction ≥ 0.25/(1+g), i.e. **16.7 ≈ 17 points at g=50%** (code E9). Applied to Bending Spoons: net investing outflows were 2.30× (2024) and 2.76× (2025) prior-year revenue, so it escapes the flag only if <10.9% / 9.1% of the outflow paid for acquisitions (paper says "under 11%/9%" ✓); Q1 2026 capital deployed $2.01B = 1.54× 2025 revenue; pro forma 2025 revenue 2,608,496k = 2.00× actual (excess 99.7%, vs 10% threshold). All reproduce ✓.

**Vimeo price/revenue and the sign-flip:** AOL 1,454M/633,365k = 2.30×; Eventbrite 505M/291,843k = 1.73×; Vimeo 1,359M/(376,883k×365/327) = 3.23× ("about 3.2"). At X=1 the full charge loses k−1 = 0.73–2.23 points per point of acquired growth (paper: "0.7 to 2.2"); the annuity/user-cost spread charges only 0.19–0.59 points per point and thus *raises* the score at any weight ≥1. The sign flips at X = k_acq ∈ [1.7, 3.2]. All reproduce ✓ (code E11/E15).

---

## 6. "Fully charged score is a lower bound" and the timing mismatch — CORRECT ✓

The claim (Remark 4, last paragraph; Section 6 "Vimeo shows the timing mismatch") is sound:

- Vimeo closed **24 Nov 2025** for **$1,359M**, so the full price is charged in 2025.
- **327 days of Vimeo's 2025 revenue ($376.9M) precede the close** (1 Jan–23 Nov) and are therefore *not* in Bending Spoons' 2025 consolidated revenue. Only the ~37-day stub (24 Nov–31 Dec) enters 2025 revenue, while the acquired growth from Vimeo lands in 2026's g.
- Charging the full price against a year's revenue that contains little-to-none of the acquired business's contribution makes the fully-charged score *too low* — a **lower bound, not an estimate**. This is exactly why Section 4 also flags the following year (which the paper states). Correct.

Corroborating facts reproduced: pro forma 2025 revenue 2,608,496k = 2.0× actual; the three purchase prices 1.7–3.2× annual revenue; "at those prices k_acq > X = 1, so by part (a) each point of growth they buy lowers the fully charged Rule-of-40 score by 0.7 to 2.2 points" ✓.

---

## 7. Findings / flags

### 7.1 No arithmetic, sign, or double-count error found
All 20+ Table 3 cells, the four charged-score conventions, the fully-charged lower bounds, the return-on-capital ranges, and the interest-paid sensitivities reproduce exactly from the repo data and pass the script's 82 checks.

### 7.2 Internal inconsistency in the *verification code* (not the paper) — MINOR
Check **E7** of `verify_part2_acquirer.py` (and `notes/acquirer_notes.md` §4 "Worked numbers") still reports the fully-charged score as **−28.7 / −24.8**. That is the *pre-round-2* convention charged against **after-interest** OCF (g + (OCF+CFI)/S), which the IB-4 fix explicitly corrected away from. The paper (Table 3 and Section 6) correctly uses the **before-interest** figure **−25.0 / −16.5** (g + m^cf − outflow/S), consistent with Remark 4's definition of m^cf. The stale −28.7/−24.8 survives only in E7's hard-coded `target` and in the notes; it does **not** appear in the paper. Recommendation: update E7's target and the notes to −25.0/−16.5 to avoid future confusion.

### 7.3 Disclosed measurement choice (not an error) — NOTE
Table 3's "cash margin before interest" m^cf adds back **interest expense**, not **interest paid**, even though the margin is built on operating cash flow. The paper discloses this and the sensitivity (S4.1: using interest paid gives 86.6–113.1 instead of 87.2–114.0). Since interest paid ≈ 92% of interest expense in 2025, the expense-based add-back is slightly *larger* than the cash measure (the code itself flags "the add-back is if anything too large"). This is disclosed, defensible, and does not change any conclusion.

### 7.4 Proxy caveats already disclosed by the paper (re-verified)
- "Fully charged" uses **net investing outflow** (all of −CFI) as the acquisition charge, not "acquisitions net of cash acquired." The paper notes acquisitions were 99.9%/99.8% of the outflow in H1 2025/H1 2026 and capex is negligible (PP&E 0.05%/0.2%), and that the company's own "capital deployed in acquisitions" *exceeds* net investing outflow in 2023 and Q1 2026 — so the proxy can slightly understate the charge. Disclosed; not an error.
- Outlays before 2023 are excluded (extract doesn't report them), making every charge too small. Disclosed.

---

## 8. What I could NOT reproduce from repo data alone

The paper's financial-statement figures are **not** stored as raw SEC filings in the repo. They trace to the author's hand-extracted markdown `notes/case_bending_spoons_f1_extract.md` (plus the small `bending_spoons_cash_interest.json`). Specifically:

1. **The F-1 (8 Jun 2026) and 424B4 (1 Jul 2026) full financial statements are absent.** Only the markdown extraction exists. The revenue/operating-income/cash-flow figures are reproducible *from the extract*, but the extract's own self-consistency checks (code A1/A2: income statement adds up to ±$2k in every period; balance sheet balances) are the only in-repo defense against transcription error.
2. **The Q2 2026 results (13 Aug 2026 6-K, Ex. 99.1) and interim financial statements (Ex. 99.2) are absent in raw form.** `bending_spoons_6k_2026-11-02.json` contains the *cover pages* and Ex. 99.1 exhibits for the later Aug–Oct 6-Ks, but for accession `0002004711-26-000011` (the Q2 results) it contains only the cover page (`bsp-20260630x6k.htm`), **not** `bsp_ex99-1.htm`/`bsp_ex99-2.htm`. The Q2 revenue 704,155k and H1 cash flows come from the markdown extract and `bending_spoons_cash_interest.json` (which cites the Ex. 99.2 URL).
3. **The Article 11 pro forma (2,608,496k combined 2025 revenue) is explicitly flagged by the author as resting on a browser reading "not re-verified."**
4. Not in the extract at all (and would need EDGAR): capex by year, capitalized software, revenue by business/segment, the subscription share, and 2023–2025 acquisitions net of cash by year.

I attempted to independently fetch SEC EDGAR (`data.sec.gov` company-concepts API for CIK 2004711); it returned **HTTP 403 ("undeclared automated tool")**, so the underlying filings could not be independently retrieved in this session. **Conclusion:** every number is reproducible *from the repo's extracted data*, but the ultimate source documents (F-1/424B4 and the Q2/H1 6-K financial exhibits) are not in the repo and would require an EDGAR fetch for true independent verification. The paper itself repeatedly flags this ("the split … is not in the filings we read"; "not in our extract").

---

## 9. Bottom line

The Bending Spoons case study is arithmetically and accounting-wise sound. All Table 3 numbers reproduce; the fully-charged lower bound (−25.0 / −16.5) and the charged range (87–114) reproduce; the ASC citations are correct; Proposition 8's net-weight result is exact; and the "lower bound, not an estimate" claim correctly follows from the Vimeo timing mismatch. The only issues found are a stale −28.7/−24.8 in the verification code's E7 check/notes (the paper itself uses the correct −25.0/−16.5) and the disclosed interest-expense-vs-paid measurement choice — neither of which is an error in the paper.
