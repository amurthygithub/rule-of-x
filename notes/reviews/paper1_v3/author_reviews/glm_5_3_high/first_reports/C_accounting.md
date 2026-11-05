# Referee C — Corporate finance, accounting, taxes and acquisition measurement
## First-pass audit report: "The Rule of 40 as a Price Line" (Murthy, Nov 2026)

### (0) Coverage and model-identity disclosure

**Model identity disclosure (required).** All agents on this panel (Lead and referees A–F) are separate
conversation contexts of the SAME large language model (GLM glm-5.3, via DeepSeek Harness). We are not
independent human experts and not independent model-family evidence. This report is one context's audit
and carries no independent-model evidentiary weight.

**Scope actually audited (read fully, from the supplied PDFs and page-indexed extractions).** Main §1
"How not to use these numbers" (printed p.6), §3.1 (FCF margin, pairing convention, printed pp.11–12),
§3.11 (economic profit and ROIC, printed pp.34–35), §4.1–4.6 (printed pp.36–39), §5.6 (printed p.45),
§6 in full including Table 3 (printed pp.48–54), §7.1–7.2 incl. Table 4 (printed pp.53–58), §8.1–8.3
(printed pp.65–67), §9 (printed p.69); supplement S1 (Remark S1(a)–(d), Lemma S1), S2.8, S4 (proofs for
§6), S4.1, S6 (data construction, element list, Table S10), S8 as it enters §7.2's arithmetic, plus the
supplement's protocol/limitations sections as they bear on the case. Working notes and inputs consulted as
evidence: `repo/notes/accounting_notes.md`, `acquirer_notes.md`, `acquirer_fixes_v2.md`,
`case_bending_spoons_f1_extract.md`, and `repo/data/v3_inputs/` (bending_spoons_6k_2026-11-02.json [raw/],
bending_spoons_cash_interest.json, cash_interest_taxes.json, interest_income_deferred.json,
related_party.json, business_descriptions_named.json, acquiree_revenue.json, README_retrieval.md). I also
ran the author's `code/verify_part2_acquirer.py` (82/82 checks pass) and recomputed the case numbers
independently in `/root/tmp/ruleof40/diagnostics/accounting/recompute_bs.py`. Quarantine respected: nothing
under `/root/tmp/ruleof40/quarantine/` was opened, listed or grepped; no web search for critiques of the
paper. One tool limitation: this model cannot read images, so page-image rendering (manifest suggestion)
was unavailable; I compensated with `pdftotext -layout`/`-raw` on the specific pages and by re-deriving
every consequential number arithmetically rather than trusting extracted glyphs.

**Filings checked on the open web (SEC EDGAR; public access, no login; fetched 2026-11-03 with a declared
user agent; SEC blocks the default fetch tool — a declared-UA curl was used).**

| Filing | Form, date | URL / accession | Access level |
|---|---|---|---|
| Bending Spoons S.p.A. registration statement | F-1, filed 2026-06-08 | sec.gov/Archives/edgar/data/2004711/000110465926071170/tm2613674-7_f1.htm (0001104659-26-071170) | public, full document fetched |
| Bending Spoons final prospectus | 424(b)(4), filed 2026-07-01 | sec.gov/Archives/edgar/data/2004711/000110465926079884/tm2613674-14_424b4.htm (0001104659-26-079884) | public, full document fetched |
| Bending Spoons Q2 2026 results + interim statements | 6-K, filed 2026-08-13, Ex. 99.1 and 99.2 | sec.gov/Archives/edgar/data/2004711/000200471126000011/ (0002004711-26-000011) | public, both exhibits fetched in full |
| Bending Spoons notes pricing | 6-K, filed 2026-10-28, Ex. 99.1 | sec.gov/Archives/edgar/data/2004711/000200471126000021/ (0002004711-26-000021) | public, fetched in full |
| Bending Spoons filing list (form types/dates; F-1/A of 2026-06-22 noted) | EDGAR company browse, CIK 0002004711 | — | public |
| Palantir Q2 2026 press release | Ex. 99.1 to 8-K, filed 2026-08-03 | sec.gov/Archives/edgar/data/1321655/000132165526000039/a2026q2ex991pressrelease.htm (0001321655-26-000039) | public, fetched in full |
| Palantir Q4/FY2025 press release | Ex. 99.1 to 8-K, filed 2026-02-02 | sec.gov/Archives/edgar/data/1321655/000132165526000004/ (0001321655-26-000004) | public, fetched in full |
| CoreWeave FY2025 facts | 10-K via data.sec.gov XBRL companyconcept API, CIK 0001769628 | data.sec.gov/api/xbrl/companyconcept/... | public |

Form types confirm the paper's description: Bending Spoons is a foreign private issuer (F-1 → 424B4 →
6-Ks), fiscal year ends December 31, listed Nasdaq July 2026; 6-Ks through 29 October 2026 as the paper says.

---

### (1) Case calculations: a precise reproduction ledger

All recomputations mine, from the filing figures, in `/root/tmp/ruleof40/diagnostics/accounting/`
(`recompute_bs.py` and session logs). "Paper" column is main §6/Table 3 (printed pp.50–54) and the abstract.

**Bending Spoons, FY2024/FY2025 (from F-1/424B4 audited statements; every figure I checked is identical in
both documents, as the paper claims).**

| Claim | Paper | My recomputation | Verdict |
|---|---|---|---|
| Revenue 2023/24/25 ($k) | 387,067 / 671,053 / 1,306,404 | same (424B4 income statement) | reproduced |
| Growth g 2024 / 2025 | 73.4% / 94.7% | 73.35% / 94.68% (66.64% cont.) | reproduced |
| GAAP operating margin 2024 / 2025 | 19.0% / 21.3% | 127,352/671,053 = 18.98% / 277,851/1,306,404 = 21.27% | reproduced |
| GAAP score, before interest, 2024 / 2025 | 92.3 / 115.9 | 92.35 / 115.95 | reproduced |
| GAAP score after interest, 2024 / 2025 | 87.5 / 105.0 | 92.35−4.86 = 87.49; 115.95−10.92 = 105.03 | reproduced |
| Cash score after interest paid (g+OCF/S), 2024 / 2025 | 103.9 / 116.9 | 204,895→30.53% → 103.90; 290,600→22.24% → 116.92 | reproduced |
| Cash score before interest (interest expense add-back net of tax 24%), 2024 / 2025 | 107.6 / 125.2 | 107.59 / 125.22 | reproduced |
| Company-adjusted margin score 2025 | 141.6 | 613,247/1,306,404 = 46.94% (filing: "47%") + 94.68 = 141.62 | reproduced |
| Fully charged (before interest, τ=24%), 2024 / 2025 | −25.0 / −16.5 (lower bound) | 107.59−132.57 = −24.98; 125.22−141.75 = −16.53 | reproduced |
| Net investing outflow / revenue 2024 / 2025 | 132.6% / 141.8% | 132.57% / 141.75% | reproduced |
| Charged as capital, 2025, all conventions (2 charges × 2 timings × NRR 91–95% × τ∈{0,24%} × H2-2025 dated 1 Oct–24 Nov) | "between 87 and 114" | 87.2 to 114.0 (min: user cost, year-end, NRR 91%, τ24; max: level annuity, time-weighted, NRR 95%, τ0, Vimeo-close timing) | reproduced |
| Table 3 sub-ranges at τ=24%: annuity YE / annuity TW / user cost YE / user cost TW | 92.7–101.1 / 104.4–111.3 / 87.2–95.2 / 100.9–108.0 | 92.7–101.1 / 104.4–111.3 / 87.2–95.2 / 100.9–108.0 | reproduced exactly |
| Same charges against OCF after interest (the double-charge illustration) | 79 to 103 | 78.9 to 103.0 | reproduced |
| Double charge = (1−τ)c_fin | 8.3 (τ24) / 10.9 (τ0) points | 8.30 / 10.92 | reproduced |
| Interest-paid variant of the 2025 charged scores (S4.1) | 86.6 to 113.1 | 86.6 to 113.2 (interest paid 130,881; 424B4 F-34/35) | reproduced |
| Charged at the 9.625% coupon | 86.0 to 112.8 | 86.0–112.8 **but on the interest-paid basis** (see finding F3); on the interest-expense basis I get 86.7–113.7 | reproduced numerically; basis switch unstated |
| Return on acquisition capital, 2025 | "22% to 28%", "14% to 22% after economic depreciation"; Table 3: 22.3–25.8% / 13.6–19.8% | With the author's script convention (denominator = time-weighted **decayed** capital): 22.3–28.0% / 13.6–21.9% ✓. With the natural reading (undecayed time-weighted outlays): 21.4–25.9% / 13.6–21.9% | partially reproduced (see F4) |
| Sensitivity of user-cost score to r ("decayed capital to revenue") | 1.2 to 2.1 points | year-end decayed capital/revenue 2.06–2.14; time-weighted ≈ 1.14–1.35 | reproduced (rounding at the low end) |
| Amortization & impairment of acquired intangibles 2024 / 2025 | 12.8% / 11.5% | 85,947→12.81%; 150,532→11.52% (424B4 non-GAAP table) | reproduced |
| Transaction expense 2024 / 2025 | 4.8% / 6.5% | 31,952→4.76%; 85,466→6.54% | reproduced |
| Reorganization expense 2024 / 2025 / Q1-26 / Q2-26 | 7.7% / 6.0% / 12.6% / 7.2% | 51,792→7.72%; 78,607→6.02%; 75,759→12.60%; 50,799→7.21% | reproduced |
| Interest paid 2023/24/25, Q1-26 (S4.1: 4.3/2.9/10.0/14.8% of revenue) | as stated | 16,581; 19,168; 130,881; 89,037 → 4.28/2.86/10.02/14.81% (424B4 F-34/35, F-6/7) | reproduced |
| Interest paid / interest expense H1-25, H1-26 | 90%, 80% | 49,737/55,049 = 90.4%; 161,153/202,154 = 79.7% (6-K Ex. 99.2) | reproduced |
| Run-rate interest after new debt | 20.3%; 27.9% if new term loans carry the coupon | (2×202,154 + 1,250×9.625% + 500×8.625%×1.10)/4×704,155 = 20.32%; +2,234×9.625% → 27.95% | reproduced |
| Acquisition-flag arithmetic (§6 end) | outflows 2.3×/2.8× prior-year revenue; escapes flag only if <11%/9% paid for acquisitions; Q1-26 capital deployed 1.5× 2025 revenue; pro forma +100% | 2.298/2.760; 10.9%/9.1%; $2.01B/$1,306.4M = 1.54; 2,608,496/1,306,404−1 = 99.7% | reproduced |
| k_acq of the three pro forma deals | 1.7–3.2× annual revenue | Eventbrite 505/291.8 = 1.73; AOL 1,454/633.4 = 2.30; Vimeo 1,359/(376.883×365/327) = 3.23 (424B4 pro forma components) | reproduced |
| Full charge per point of acquired growth / spread charge per point | 0.7–2.2 / 0.19–0.59 | k_acq−1 = 0.73–2.23; CRF×k_acq = 0.19–0.47; (r+d)k_acq = 0.24–0.59 | reproduced |
| Material weaknesses quote; no §404 assessment; Q1-2026 cash flows restated | as stated | quote verbatim in F-1 and 424B4 (summary risk factor); "neither we nor an independent registered public accounting firm have performed an evaluation"; "restated the Condensed consolidated statement of cash flows for the three months ended March 31, 2026 to correct a misclassification error" | reproduced |
| The 6-K exhibits through 29 Oct 2026 (S4.1): notes $1.25B at 9.625% + €500M at 8.625% due 2032 at par, upsized from ~$1.5B, issued by two subsidiaries, company does not issue or guarantee, proceeds to fund future acquisitions; Berkshire $330M at $33.00 | as stated | verified verbatim from the 28 Oct 2026 6-K Ex. 99.1 and the filing list (6-Ks on 28 Jul, 4 Aug, 13 Aug, 4 Sep, 10 Sep, 2 Oct, 14 Oct, 26 Oct, 27 Oct, 28 Oct, 29 Oct) | reproduced |

**Bending Spoons, Q2 2026 (from 6-K Ex. 99.1/99.2 of 13 Aug 2026, unaudited).**

| Claim | Paper | My recomputation | Verdict |
|---|---|---|---|
| Revenue growth 704,155/311,100 | 126% (Table 3: 126.3%) | 126.34% | reproduced |
| Organic revenue growth, company measure | 3% | "Organic revenue growth was 3% in Q2 2026" (Ex. 99.1, unaudited operating results; definition in footnote 4 matches the paper's description verbatim; not among the non-GAAP measures; not reconciled; no Rule-of-40 score anywhere in the exhibit) | reproduced |
| GAAP operating margin | 34% (Table 3: 34.1%) | 240,251/704,155 = 34.12% | reproduced |
| Score on reported growth | about 160 (Table 3: 160.5) | 160.46 | reproduced |
| Organic score (3+34) | about 37 (37.1) | 37.12 | reproduced |
| Interest 15.5% of revenue; organic after interest about 22 | 15.5%; 21.6 | 108,970/704,155 = 15.48%; 37.12−15.48 = 21.64 | reproduced |
| Reorganization 7.2%; organic +reorg about 44 before interest, 29 after | 44.3 / 28.9 | 50,799→7.21%; 44.33 / 28.85 | reproduced |
| Score on reported growth after interest | about 145 | 144.98 | reproduced |
| Q1 2026 rows of Table 3 (g 132.2, margin 20.0, interest 15.5, cash 144.8, before interest 156.6, fully charged −117.5, adjusted 183.4) | as stated | all reproduce (601,321/258,946−1 = 132.25%; 120,171/601,321 = 19.98%; 75,654→12.58%; +11.80% = 24.38%; 132.25+24.38−274.06 = −117.4; 308,011→51.16%) | reproduced |

**Palantir (abstract/intro/§8.3).**

| Claim | Paper | Source check | Verdict |
|---|---|---|---|
| "Palantir reported a score of 155 for the second quarter of 2026 on its adjusted margin" | 155 | Q2 2026 press release (Ex. 99.1 to 8-K filed 3 Aug 2026): "Rule of 40 score of 155%", defined as "the sum of our revenue growth rate year-over-year and our adjusted operating margin"; revenue grew 93% to $1,935.5M; adjusted income from operations $1.194B = 62%; GAAP income from operations $912.0M = 47%. 93+62 = 155. **Palantir itself reports the score**, so the intro's "reported" is faithful, and item 8 of "How not to use" ("scores for named companies are our computations... not the companies' measures") does not apply to this number. | reproduced; description faithful |
| §8.3: 140 on GAAP operating margin of 47% | 140 | 93+47 = 140 ✓ | reproduced |
| §8.3: adjusted margin excludes SBC "and the related employer payroll taxes" | as stated | press release: adjusted income from operations "excludes stock-based compensation and related employer payroll taxes" | reproduced |
| §8.3: "Its annual GAAP score for fiscal 2025 was 88" | 88 | FY2025 (Q4 press release, 8-K of 2 Feb 2026): revenue $4,475.4M, +56% Y/Y; GAAP income from operations $1,414.0M = 32%. 56+32 = 88 ✓ ("comparison also reflects an acceleration of growth": 56%→93%) | reproduced |

**CoreWeave (§4.6/§5.6 illustration).**

| Claim | Paper | Source check (10-K FY2025 via XBRL companyconcept) | Verdict |
|---|---|---|---|
| Grew 168% in fiscal 2025 at GAAP operating margin about zero, GAAP score 167 | 167 | revenue $5,131M vs $1,915M (2024): +167.9%; operating income −$46M → −0.9%; score 167.0 | reproduced |
| FCF margin after SBC −154%, cash score 14 | 14 | (OCF 3,058 − capex 10,309 − SBC 630)/5,131 = −153.6%; 167.9−153.6 = 14.3 | reproduced |

**Panel statistics (§4.6, Table S10 bridge) recomputed from `repo/data/panel_v3_all.csv`
(core = `in_core_v2` & no `v3_exclude`): 1,788 firm-years / 292 firms ✓; shares clearing 40: GAAP 14.3%,
after-SBC 15.9%, adjusted 26.6%, FCF-before-SBC 30.5% ✓; 2023–25 medians 12.0/15.3/26.4/29.2 and
shares 9.7/9.2/24.8/29.0 ✓; median SBC 12.3% of revenue ✓; period counts 465/418/458/447 ✓. Table S10
bridge: p95 56.0→44.6 (−11.4) on bridge firm-years; before interest and cash taxes 60.8→49.8 (−11.0) ✓;
"interest alone" (interest paid × (1−statutory rate), 35% pre-2018) moves p95 by +0.6 (2016–19) and +0.1
(2023–25) ✓. All exactly as stated.**

**Deferred revenue / negative capital intensity ('How not to use' item 2; §7.2; Remark S1(c)).**
Median ratio of the change in deferred revenue (or contract-liability) to the change in revenue among
growing firm-years of 2023–25, from `interest_income_deferred.json` matched to the panel (±10 days):
**0.274 (sum of the two elements) to 0.276 (max)**, n=355 firm-years → the paper's 0.27 reproduces. Central
threshold at k=−0.27: 32.5/1.27 = 25.6 → "26%" ✓; at k=−0.3: 25.0% ✓. The flow-to-stock interpretation is
sound: net investment = (k_fix−ρ)·gS with ρ = ΔDR/ΔRev, so k = −ρ for an asset-light firm.

**Not reproduced / reproducible only under the author's convention (details in findings F3–F4):**
(i) the text's "22% to 28%" return on acquisition capital reproduces only when the denominator is the
time-weighted *decayed* (written-down) capital, which the phrase "capital deployed" does not say;
(ii) the coupon-variant range 86.0–112.8 is on the interest-*paid* basis while the paragraph's anchor
(87–114) is on the interest-expense basis.

---

### (2) Verified-correct items (rederived or source-verified)

1. **Remark 3 identities (§3.11), all rederived:** e := m + k(g−r) gives eS = m_op·S − r·K and
   ROIC = m_op/k, exact under Assumption 4 and eq. (2) (m = m_op − kg). RX = (X−k)g + e + rk =
   k[ROIC + (X/k − 1)g] ✓. With k=0, e=m ✓. R1 = (1−k)g + e + rk ✓ — the cash Rule of 40 weights growth at
   1−k in (g,e) coordinates, penalizes growth for k>1, ignores it at k=1, and ∂R1/∂k = r−g at fixed (g,e) ✓.
   The worked example (k=1.5, g=15%, r=10%: 7.5 points below asset-light; −0.5 per extra point of growth) ✓.
   The economic-margin frontier e*(g) = m0 − rk − κ(g−G)^β is correct (the +kg from k(g−r) cancels the −kg
   inside m*(g)); slope zero at G, concave, decreasing beyond; ROIC frontier [m0 − κ(g−G)^β]/k ✓. Valuation
   identities V/S = m/(r−g) = k + e/(r−g), V/(kS) = 1 + (ROIC−r)/(r−g), iso-value lines through (r,0), and
   "yield + growth = r" ✓. Remark 3 is correctly presented as an identity/restatement, not a new result.
2. **Remark 4 / Proposition 8 charging constructions.** Both spreads are PV-preserving: the level annuity
   CRF(r,T)∫₀ᵀe^{−rt}dt = 1 and the user cost ∫₀^∞(r+d)e^{−(r+d)t}dt = 1 — each outlay's charges have
   present value equal to the outlay, so the transformation preserves valuation while changing period
   margins (both sides of the task's distinction established). The ordering fully-charged ≤ annuity ≤
   uncharged holds under the stated condition (annuity on in-life outlays below the current outlay), which
   holds by a wide margin in the case years (141.8-point outlay vs 13.8–38.0-point annuity). The
   double-charge diagnosis is exactly right: under US GAAP interest paid is an operating outflow, so OCF is
   an after-interest margin; setting a cost-of-capital charge that includes the cost of debt against it
   charges the debt-financed share twice, by exactly (1−τ)c_fin = 8.3/10.9 points — verified numerically.
   The paper's fix (m^cf = OCF + (1−τ)·interest, over revenue, charged at the WACC) is the standard
   unlevered-FCF-at-WACC treatment — no double count. Definition 5's rate identities (continuous and simple)
   are algebraically correct.
3. **k_acq construction.** k_acq is a price per dollar of annual run-rate acquired revenue (not a PV of
   the acquired stream), consistently paired with the run-rate growth concept g_acq of Definition 5; the
   three pro forma multiples (1.73/2.30/3.23) recompute from the 424B4. The full charge per point (k_acq−1
   = 0.73–2.23 at X=1) and the spread charge per point (0.19–0.59) are right, and the conclusion that "the
   charging convention, not the data, decides the sign in the year of purchase" is verified, as is the
   sign-flip at X = k_acq. The supplement correctly warns that Airtable/Miro EVs are against ARR, not GAAP
   revenue, and are not comparable one-for-one.
4. **§7.2 tax path and Table 4 arithmetic, fully rederived.** After-tax margin = (1−τ)(1−cc−f−amin−cfull):
   central 0.82×0.823 = 67.5; favorable 77.7; conservative 50.5; high-compute 38.7 ✓. Threshold
   G* = τ + (1−τ)(cc+f+amin+cfull) = 18.0+4.9+2.1+2.5+5.1 = 32.6≈32.5; 22.3/49.5/61.3 ✓. "Accountability
   costs alone" bases 79.5/72.6/63.5/44.7 → thresholds 21/27/36/55 ✓. Compute-bound sensitivity 28→78%
   (23→72% without the full-cost floors; the 78% upper end pairs cc=60% with the high-compute cfull=7.2) ✓.
   ψ (PV of deductions per dollar of capital) = 1 for domestic R&E under §174A and bonus-eligible property;
   ψ₁₅ = 0.53 for foreign; the τkG add-back (≤9.5 points) and the δ_K·k replacement deduction (12.5 at ψ=0,
   10.25 central at ψ=1) ✓. The cash-tax-rate treatment is disclosed as a scenario (15–21% federal-only,
   state excluded, GAO effective rates 9–16% given a sensitivity); NOLs are not modeled (an unstated
   steady-state assumption — see open questions, not a defect at this scope).
5. **§8.3's four measurement mechanisms are accounting-correct.** Capitalized compute enters operating
   income only through depreciation, never EBITDA, fully in FCF ✓; lengthening server lives raises operating
   margins without changing cash flow ✓; the permanent GAAP-over-cash premium of a growing capitalization
   program is real (amortization_t = (kg/T)Σ_{j≤T}S_{t−j} < kgS_t = capex whenever revenue grows, growing in
   the gap) — I rederived this; gross-vs-net recognition raises reported revenue and reported growth while
   the gross-recorded mix rises ✓; run-rate/annualized revenue runs ahead of annual revenue in a spurt ✓.
   The recommendation to state the basis with every score, and to deduct finance-lease additions where
   lease-financed capacity is material, is sound under US GAAP (finance-lease principal sits in financing
   activities; operating-lease payments are already inside OCF — and S6 discloses that operating-lease
   capacity is otherwise not counted as capital).
6. **The reliability paragraph is accurate**: the material-weakness sentence is verbatim from the F-1 and
   424B4; no SOX 404 assessment exists yet ("neither we nor an independent registered public accounting firm
   have performed an evaluation"); the Q1 2026 cash-flow statement was restated (misclassification error);
   quarterly reports are unaudited; the pro forma statements are unaudited and illustrative; the Q2 exhibit
   mentions no Rule-of-40 score and presents organic growth outside the non-GAAP section, unreconciled.
7. **The company's organic-growth definition is described faithfully** (footnote 4 of Ex. 99.1, verbatim),
   including the difference from Definition 5 (acquired businesses' growth over their own estimated
   pre-deal revenue counts as organic on the company's measure).
8. **SBC treatment across bases is economically consistent** (m_adj adds SBC to operating income to mimic
   company measures; m_fcf−sbc deducts it as the economic cost; §4.6's bridge quantifies the difference),
   and the interest treatment of each of the four §4.3 bases is stated correctly with ASC cites
   (230-10-45-17(c),(d)); the frames-vintage caveat (interest/taxes paid are latest-filed, not
   first-reported) is disclosed in both main and supplement.

---

### (3) Candidate findings

**F1. The paper understates what the filings disclose about the case: annual organic growth, the
subscription share, SBC, and the annual investing split are all in the F-1/424B4 it says it read.**
1. **Locators.** Main §6, printed p.53 (= PDF p.53), last two paragraphs: "the company reports organic
   growth for one quarter; a split of 2024 and 2025 growth and spend by business is not in the filings we
   read" and "its organic growth is measured only by the company, for one quarter"; main §6, printed p.52,
   "the subscription share of revenue is not in our extract"; printed p.51, "its stock-based compensation
   is not in our extract"; printed p.51, "In the first halves of 2025 and 2026, the periods for which the
   filings split them, acquisitions were 99.9% and 99.8% of the net investing outflow"; Table 3
   (printed p.54): organic-growth row "–" for 2024 and 2025.
2. **Description.** The paper states that the company's organic growth is available only for one quarter
   (Q2 2026), that the subscription share of revenue, SBC, and the annual composition of the investing
   outflow are unavailable in the filings it read, and correspondingly leaves the annual organic rows of
   Table 3 empty.
3. **Classification.** Demonstrated error (factual claim about the primary sources), with an
   evidence-transport root cause: the case rests on the author's extract, and fields outside the extract
   were declared unavailable without re-reading the full primary documents.
4. **Evidence (all from the F-1 filed 8 June 2026, the document the extract says was read in full at
   ~1.32M characters, and the 424B4 of 1 July 2026; identical in both):**
   - MD&A: "Organic revenue growth was **7% in 2024**" and "Organic revenue growth was **13% in 2025**"
     (F-1 MD&A, "Results of operations"; footnote defines the measure identically to the Q2 6-K footnote,
     with the same worked example). Q1 2026 organic is *not* disclosed; Q2 2026 is from the 6-K.
   - "Subscriptions accounted for **95% of our revenue in 2023, 92% in 2024, and 93% in 2025**"
     (Revenue sources section; Q1 2026: 84% subscriptions, 12% advertising).
   - Audited annual cash-flow statements (424B4 F-34/35; F-1 identical) report **Equity compensation
     expense of $14,900 (2023), $25,855 (2024), $55,523 (2025)** thousand — SBC for 2025 is 4.25% of
     revenue.
   - The same audited statements split the annual investing outflow: **Acquisitions of businesses net of
     cash $170,586 (2023) / $726,574 (2024) / $1,851,307 (2025); purchase of intangible assets $958 /
     $162,476 / $67; purchase of PP&E $4,044 / $604 / $501**. In 2024, acquisitions of businesses were
     81.7% of the net outflow, not 99.9%; the H1-2025/2026 shares the paper quotes are correct for those
     halves (verified: 575,228/575,563 = 99.9%; 2,286,259/2,290,228 = 99.8%).
   Consequences the paper could have computed: 2025 organic score = 13 + 21.3 = **34.3** before interest
   (23.4 after; 40.3 / 29.4 with the reorganization add-back); 2024 organic = 26.0 / 21.1 (33.7 / 28.8).
   The panel-basis (after-SBC) 2025 cash score = 116.9 − 4.25 = **112.7** after interest paid (121.0 before
   interest). Excluding the 2024 intangible purchase from acquisition capital would raise the 2025 charged
   scores by ≈1.3–1.8 points (CRF × 162,476/1,306,404) — or by nothing, if that purchase was itself an
   asset acquisition of a business (the F-1 says the 2024 Mosaic deal "was an asset deal"); the direction
   is not determinable from the statements.
5. **Strongest author defense.** The hedged phrase "not in the filings we read" is literally accurate for
   the extract; the company's organic measure is unaudited, estimated and company-defined, which the paper
   already stresses; the by-business split of growth and spend genuinely is not disclosed; charging the
   whole net outflow is consistent with the fully-charged score being a lower bound; and the annual
   organic scores (21–40 across treatments) fall inside the paper's own 22–44 bracket, so no conclusion
   reverses — indeed the disclosed annual figures *strengthen* the paper's argument that the 115.9 rests
   on uncharged acquired growth.
6. **Verdict.** Narrowed but stands as an error: the specific sentences "the company reports organic growth
   for one quarter" and "its organic growth is measured only by the company, for one quarter" are false
   about the primary sources the paper itself cites and claims to have checked ("every F-1 figure we use is
   unchanged in the final prospectus"). The "not in our extract" sentences are literally true but, under
   this review's rule that a field absent from the extract must be checked in the underlying filing before
   being declared unavailable, they understate the record.
7. **Affected conclusions and magnitude.** No empirical or theoretical conclusion reverses. Table 3 is
   incomplete (organic rows for 2024/2025 fillable; an after-SBC cash row computable); the "22 to 44"
   abstract framing gains annual support; the §6 statement that the bounds are as wide as −16.5 to 125.2
   "because the filings split neither growth nor spend by business" overstates the data limitation.
   Practical magnitude: moderate for the case section's completeness, nil for the paper's theorems.
8. **Smallest correction and acceptance test.** Add one sentence: "The company's MD&A also reports its
   organic revenue growth for 2024 (7%) and 2025 (13%) on the same definition, and subscriptions were
   92–95% of revenue; Table 3's organic rows use them (2024: 26.0; 2025: 34.3 before interest)"; add the
   SBC row (4.3% of 2025 revenue) and a panel-basis cash score; cite the annual investing split.
   Acceptance test: every "not in the filings/extract" sentence in §6 survives a full-text search of the
   F-1 and 424B4; Table 3's organic rows are non-empty for 2024 and 2025.

**F2. The empirical implementation uses the contemporaneous growth–margin pairing that the paper's own
model flags as inconsistent when capital expenditure leads revenue; no forward-pairing robustness is
reported.**
1. **Locator.** Main §3.1, printed p.11 ("Reported scores pair growth over the past year, g_t, with FCF_t,
   which is the contemporaneous convention; for firms whose capital expenditure leads revenue, g_{t+1} +
   m_t is the pairing consistent with (2)"); §4.3, printed p.37 ("The Rule-of-40 score is R = g + m under
   each definition", with g_it = S_it/S_i,t−1 − 1); supp Lemma S1 (printed p.2); Table S4's 22 variants
   (supp, printed p.30ff) contain no forward-pairing variant.
2. **Description.** The panel pairs same-year growth with same-year FCF margin throughout, including for
   the model-facing cash-basis results (§5.6 capital intensity, the 95th-percentile declines, the
   calibration anchor), while the model's eq. (2) holds exactly only with capital installed one period
   ahead and forward growth.
3. **Classification.** Ambiguity/missing robustness (the convention is disclosed in §3.1 but never
   connected to the empirical implementation).
4. **Evidence.** Lemma S1(b): with contemporaneous capital, m = m_op − kg/(1+g), so the two conventions
   differ by kg²/(1+g). For the median firm (k≈0.11, g≈15%) this is 0.2 points — negligible. For
   capital-intensive outliers it is enormous: CoreWeave (k = capex/S = 10,309/5,131 = 2.01, g = 1.68)
   gives kg²/(1+g) ≈ 2.1, i.e. 210 points, so its quoted cash score of 14 is convention-dependent to a
   degree the text does not remind the reader of at the point of use (§4.6/§5.6). The §5.6 conclusion
   ("the cash-basis gap is an accounting effect") is itself the same-direction point, which mitigates.
5. **Strongest author defense.** E1 is by construction the *reported* score, and reported scores are the
   stated object; Lemma S1 shows the non-convex region is a sliver just above market growth for asset-light
   firms, which dominate the frontier estimates; every model-facing claim is repeated on the GAAP basis
   (where the issue is depreciation timing, not capex timing) and survives; the anchor firms are
   asset-light (typical firm k = 0.11).
6. **Verdict.** Survives as a disclosed modeling choice, narrowed: a single sentence in §4.3 stating that
   the panel follows the reported-score convention and a forward-pairing column for the cash-basis headline
   statistics would close it.
7. **Affected conclusions.** None of the stated claims flips under the alternative pairing at plausible
   parameters (the difference is second-order for k<0.3); the CoreWeave illustration's exact number is
   convention-bound but its qualitative point is not.
8. **Smallest correction / acceptance test.** Add the convention statement plus a Table S4 variant with
   g_{t+1} + m_t for the cash basis; acceptance: the §5 headline signs (slope sign, top-decline sign) are
   unchanged in that variant.

**F3. Two basis-labeling slips in the charging-as-capital paragraph.**
1. **Locators.** Main §6, printed p.52: "Charged at the 9.625% coupon of the company's dollar notes
   instead of the sector cost of capital, the 2025 charged scores are 86.0 to 112.8"; main §6, printed p.50:
   "Interest on debt raised to pay for acquisitions (Bending Spoons S.p.A., **2026b**), 15.5% of revenue".
2. **Description.** (a) The 86.0–112.8 range is computed on the interest-**paid** add-back basis (the
   author's `verify_part2_acquirer.py` applies `grid_scores(R_DEBT_NOTES)` to the paid basis; my
   recomputation confirms: paid basis at r=ln(1.09625)=9.19% gives 86.0–112.8, expense basis gives
   86.7–113.7), while the surrounding charged-score discussion ("between 87 and 114") is on the
   interest-expense basis; the switch is not stated. The rate conversion itself is correct (the script
   uses ln(1.09625), consistent with its ln(1.0934) treatment of the WACC). (b) The Q2-2026 interest figure
   (15.5% of Q2 revenue) comes from the 6-K (2026c), not the final prospectus (2026b) — although the Q1
   rate happens to be identical (93,184/601,321 = 15.50%) and is in the prospectus.
3. **Classification.** Minor presentation issue (basis labeling; citation slip).
4. **Evidence.** As above; magnitudes ≤1.0 point on a sensitivity variant.
5. **Strongest author defense.** The two bases are both reported elsewhere in the same section with their
   ranges (86.6–113.1 paid vs 87.2–114.0 expense), and the coupon variant is directional ("lowers every
   charged score"), which is true on either basis.
6. **Verdict.** Survives; correction warranted for a paper whose own item 9 is "quote every score with its
   margin basis".
7. **Affected conclusions.** None; magnitude ≤1 point.
8. **Smallest correction / acceptance test.** "…charged at the notes' coupon, on the interest-paid basis,
   the 2025 charged scores are 86.0 to 112.8 (86.7 to 113.7 on interest expense)"; re-cite the 15.5%
   to the 6-K. Test: the basis named in each charged-score sentence matches the one used by the script.

**F4. The "return on acquisition capital" wording does not disclose its denominator convention.**
1. **Locator.** Main §6, printed p.52: "Operating cash flow before interest was 22% to 28% of the
   time-weighted capital deployed in acquisitions since 2023 … and 14% to 22% after economic depreciation
   at d"; Table 3 (printed p.54): "Return on acquisition capital before / after depreciation 22.3%–25.8%
   / 13.6%–19.8%".
2. **Description.** The denominator is the time-weighted average of the **decayed** (written-down)
   acquisition-capital stock (script: `ret = m_unlev·REV/avg_d`; `avg_d` decays at d), not the undecayed
   time-weighted outlays; "before depreciation" refers to the numerator only.
3. **Classification.** Ambiguity/notation.
4. **Evidence.** Under the script's convention the ranges reproduce (22.3–28.0% across τ∈{0,24%};
   13.6–21.9% after decay). Under the natural reading (undecayed time-weighted outlays: 1.67–1.86×
   revenue) the gross range is 21.4–25.9% — the text's upper end "28%" is not reachable. The qualitative
   claim — the return exceeds the 8.93% cost of capital in every cell — holds under **both** conventions
   (min 21.4% and 13.6% respectively).
5. **Strongest author defense.** Using the written-down capital at risk is a defensible ROIC convention;
   the stated biases (pre-2023 businesses' cash flow counted without their price; expensed deal costs left
   in the flow) are disclosed in the same paragraph, and the direction of each is stated.
6. **Verdict.** Narrowed (wording only).
7. **Affected conclusions.** None; the "cleaner statistic" point stands.
8. **Smallest correction / acceptance test.** "…of the time-weighted **written-down** acquisition capital";
   test: the recomputed range from the stated formula matches the text.

**F5. 'How not to use' item 8 states the fully-charged lower bound unconditionally; Remark 4's inequality
is conditional.**
1. **Locator.** Main §1, printed p.6, item 8 ("scores with acquisitions charged in full are lower bounds");
   Remark 4 / eq. (31), printed p.50 ("the first inequality holds whenever the annuity on outlays still
   within their life is below the current outlay").
2. **Description.** (31)'s ordering fully-charged ≤ annuity-charged requires C_t^acq ≥ CRF·Σ(in-life
   outlays). In a quiet year after an acquisition-heavy year (C_t = 0) the "charged in full" score equals
   the uncharged score and sits *above* the properly annuity-charged score, so it is not then a lower
   bound on the sensibly charged score.
3. **Classification.** Minor presentation issue (an over-broad summary of the paper's own conditional
   result).
4. **Evidence.** Algebra of (31) and the S4 proof (verified); in Table 3's years the condition holds by a
   wide margin (outlay 141.8 points vs annuity 13.8–38.0), so the Table 3 use is correct.
5. **Strongest author defense.** The item addresses serial acquirers in their outlay phase, where outlays
   grow quickly and the condition holds; the precise condition is stated one page later in Remark 4.
6. **Verdict.** Narrowed.
7. **Affected conclusions.** None (direction: item 8 slightly overstates the scope of a correct result).
8. **Smallest correction / acceptance test.** "…are lower bounds in any year whose outlay is at least the
   annuity on outlays still within their life (as in a serial acquirer's outlay phase)"; test: restate
   item 8 as the conditional.

**F6. The supplement's XBRL element list omits the operating-income element (and the PP&E instant), while
§4.3's headline margin is defined only in words.**
1. **Locator.** Supp §S6, printed p.28, "Elements." bullet list (checked with both `-layout` and `-raw`
   extraction); main §4.3, printed p.37 ("GAAP operating margin, m_op: operating income"); supp p.27
   ("for 35 US-GAAP elements").
2. **Description.** The list names the revenue, OCF, capex/software/lease, SBC, S&M/G&A/R&D/gross-profit,
   acquisition, goodwill, pro-forma and discontinued-operations elements but not the element behind
   operating income (the build code uses `OperatingIncomeLoss`; `build_panel_v2.py` line 131), nor the
   PP&E instant used for the capital-intensity split, though the text claims 35 elements and says instants
   of "goodwill, property and equipment" are taken.
3. **Classification.** Minor presentation issue.
4. **Evidence.** Element list as extracted; repo code as cited. A reader cannot tell which tag supplies the
   paper's GAAP margin — the one definitional input the whole GAAP analysis rests on.
5. **Strongest author defense.** The code and the replication package disclose it; operating income has an
   unambiguous standard tag.
6. **Verdict.** Survives as a documentation gap only.
7. **Affected conclusions.** None (I verified the panel's `R_op` reproduces the §4.6 statistics exactly,
   so the construction is as intended).
8. **Smallest correction / acceptance test.** Add "Operating income: OperatingIncomeLoss" and the PP&E
   instant element to the S6 list; test: the element list, counted, matches "35".

---

### (4) Strengths

- **The flagship case survives a full independent recomputation.** Every headline number the abstract
  advertises — 115.9, 105.0, 87–114, 160, 22–44 — and every row of Table 3 reproduces exactly from the
  underlying filings, most to the decimal. I could not break any of them with the filings in hand.
- **The financing double-count fix is exactly right and exactly quantified.** The paper's insight that
  OCF is an after-interest margin under ASC 230, that a WACC-including-debt charge against it double
  charges by (1−τ)c_fin, and its before-interest reconstruction, are all correct and reproduce to 0.1
  points. The charged-score family (annuity vs user cost, year-end vs time-weighted) is internally
  consistent, PV-preserving, and correctly ordered, with the conditionality of each inequality proved in S4.
- **Unusual honesty about reliability.** The paper volunteers the material weaknesses, the restatement, the
  unaudited quarterly data, the company-defined unreconciled organic measure, and the "we use the figures
  as filed" stance — all verified accurate against the filings.
- **The basis-bridge empirics (§4.6, Table S10) reproduce exactly** from the replication panel (1,788
  firm-years, all shares and medians, the −11.4→−11.0 bridge, the ≤0.6-point interest-alone effect), and
  the deferred-revenue threshold input (median 0.27, threshold 26%) reproduces from the retrieved frames.
- **Named-company claims are faithful**: Palantir's 155 is the company's own reported metric with the
  company's own definition, verified at the primary source, as are the 140 and 88 variants; CoreWeave's
  167/14 reproduce from its 10-K XBRL facts.
- **The measurement-basis discipline the paper preaches (item 9), it largely practices**: Table 3 labels
  every score before/after interest; the growth measure (reported vs company-organic) is labeled; the
  abstract's claims are all basis-labeled and survive the labeling audit (findings F3/F4 are the residue).
- The author's verification script (82 checks) passes, is single-sourced from the extract, and its numbers
  tie to the paper — a replication practice worth commending.

### (5) Open questions for the adversarial auditor

1. If the annual organic figures of F1 are adopted (7% for 2024, 13% for 2025), should the abstract's
   "22 to 44" be restated on annual data (2025: 23.4–40.3 across the same interest/reorganization
   treatments), or kept as the Q2 illustration with the annual figures added to Table 3 only?
2. Is the 2024 intangible-asset purchase of $162.5M an asset acquisition of a business (in which case
   charging it as acquisition capital is right, and the paper's whole-outlay charge is correct) or a
   non-acquisition IP purchase (in which case the 2025 charged scores are understated by ~1.3–1.8 points)?
   The filings I read do not resolve this; the F-1's business-combination note (not fully extracted) might.
3. §7.2's ceiling applies a cash tax rate to the full-cost margin with no NOL or jurisdiction layering, and
   §3.11's economic-profit identities are pre-tax while §7.2's are after-tax; the paper never states how
   the two tax treatments reconcile if Remark 3's screen is applied to the same firm. Scenario-disclosed,
   but a reconciliation sentence would help.
4. Does the 60%-of-revenue labor share replaced by compute in §7.2 include stock-based compensation? If
   it excludes SBC, the ceiling is not directly comparable to the after-SBC cash scores it is set against
   (median SBC is 12.3% of revenue in the 2023–25 sample); S2.8's evidence does not settle it.
5. The frames-based interest/tax and deferred-revenue inputs keep the latest-filed value, not the
   first-reported one (disclosed for interest/taxes; the same caveat applies to the 0.27 deferred-revenue
   median but is not stated there). How sensitive is the 0.27/26% pair to the vintage?
6. For future filings: if the FASB's cash-flow classification alternative for interest paid (allowing
   financing classification) is adopted by software issuers, the paper's OCF-is-after-interest premise
   (correct for every filing studied here, verified for Bending Spoons) would need an issuer-by-issuer
   check. No action needed for this version.
7. The excluded registrant (removed from the repo at the author's request, hash-dropped in
   `code/exclusions.py`): the panel statistics I recomputed (1,788/292) already reflect the exclusion; the
   Lead may want confirmation that no named-company case or headline number depends on it (the paper says
   none does; I could not falsify that, but also could not independently verify it since the identity is
   hashed).

---

*Report ends. Diagnostics: scripts, filing texts and recomputation outputs are in
`/root/tmp/ruleof40/diagnostics/accounting/` (recompute_bs.py, bs_f1.txt, bs_424b4.txt, bs_q2_ex991.txt,
bs_q2_ex992.txt, pltr_q2_pr.txt, pltr_q4_pr.txt, and the panel recomputation logs).*