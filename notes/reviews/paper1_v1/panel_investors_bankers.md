# Practitioner panel: investors and bankers on Paper 1 (v1)

Paper: "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation" (October 2026 draft, `paper1_v1.pdf` / `paper1_v1.txt`).
Panel convened 29 October 2026. Seven roles, each played with its own incentives: long-only growth PM, short-seller, sell-side software analyst, PE operating partner, growth-stage VC, leveraged-finance/credit analyst, M&A banker (software take-privates).
Materials: the paper; `notes/case_bending_spoons_f1_extract.md`; `notes/assumptions_register.md`; `data/tasks/params.yaml`. Read-only. The panel also ran read-only computations on `data/panel.csv` (the core sample) and on the F-1 extract; those are labeled "panel computation" below and are not in the paper.
Standard: every external claim below was checked against a public source during this session (Section A). Secondary sources are flagged as such.

---

## Verdict

**As theory, worth publishing. As a practitioner tool, not yet usable; and four of its headline numbers are likely to be misquoted.**

What the panel would use: the price-line reading of the Rule of X (Proposition 2, Remark 6); the split between durable and transient score (Proposition 3, Proposition 4, Corollary 1); the organic-versus-acquired estimands (Section 4.4); the net weight X − k^acq (Proposition 14); and the cost-line decomposition of the distance to the frontier (Table 8).

What stops it changing how anyone screens, values or underwrites:

1. **No bridge from score to price.** Nothing maps a score to EV/revenue or EV/FCF, so no one can act on it.
2. **The two weights are drawn too sharply.** Bessemer's own regression put the implied growth weight between 2 and 9. In the paper's own Proposition 6 example, the decision weight falls to about 2 at a buyout hurdle rate.
3. **Scores are not reported on the basis practitioners quote.** On FCF before SBC, the median score did not fall between 2016–19 and 2023–25.
4. **The serial-acquirer illustration mixes conventions.**
   - Operating cash flow under US GAAP is already after interest, but the paper then also charges WACC.
   - Capex is treated as a material contaminant, but it is negligible.
   - It uses a level annuity on year-end capital.
   - Depending on these choices, the 2025 charged score runs from about 78 to 109, not 84.4 to 92.8.

Highest misuse risk:
- the decision weight of "7 to 13" (cover for cash burn);
- the "fully charged −24.8" (a short-report headline);
- the "ceiling below 100" (read as a cap on valuation);
- "only 9.4% pass" (a basis artifact).

---

## A. Verification log (claims tested against public evidence)

| # | Claim or number tested | Source checked | Result | Used by |
|---|---|---|---|---|
| V1 | Bessemer Rule of X: growth ×2 for private, ×2–3 for public "if growth is efficient", plus FCF margin (Definition 1; Sections 2.2, 8.1) | [Bessemer, The Rule of X](https://www.bvp.com/atlas/the-rule-of-x) | **Accurate, but incomplete.** The page also says:<br>• the weight comes from "a multiple regression over the past ~5-6 years", and the implied ratio "ranged from about 2x to 9x";<br>• 2–3x is "a conservative base assumption";<br>• R² is 62% for Rule of X against 50% for Rule of 40, on FV/NTM revenue;<br>• it is "most relevant for late-stage businesses". | PM, sell-side, VC |
| V2 | Market-implied growth weight in 2026 | [Meritech Software Pulse, 31 Jul 2026](https://meritech.substack.com/p/meritech-software-pulse-31-july-2026) | • Growth is "3.8x more strongly correlated with multiple than FCF margin".<br>• Median implied ARR multiple is 4.1x.<br>• "Only 10 public software companies trade above 10x NTM revenue, and 70% trade below 5x". | PM, sell-side |
| V3 | Growth multiplier in early 2024 | [Clouded Judgement, 23 Feb 2024](https://cloudedjudgement.substack.com/p/clouded-judgement-22324-rule-of-x) | "The data today suggests that the growth multiplier is 3.0x" (the author calls this "crude"). | Sell-side |
| V4 | Bain (Depeyrot and Heap, 2018): 16% of 86 firms beat it in all of 2013–17; EV/revenue about double (Section 2.2) | [Bain, Hacking Software's Rule of 40](https://www.bain.com/insights/hacking-softwares-rule-of-40/) | **Accurate.** Bain uses **EBITDA**, and the 16% is "adjusted for M&A". Neither is mentioned in the paper. | Sell-side, M&A |
| V5 | McKinsey (Roche and Tandon, 2021): more than 200 firms, 2011–2021 | [McKinsey, SaaS and the Rule of 40](https://www.mckinsey.com/industries/technology-media-and-the-telecommunications/our-insights/saas-and-the-rule-of-40-keys-to-the-critical-value-creation-metric) | **Accurate.** "Barely one-third" achieve it, and companies exceeded it "16 percent of the time". Uses **FCF**. | Sell-side |
| V6 | Vista "Rule of 60" (Section 1) | [Vista, Jan 2026](https://www.vistaequitypartners.com/insights/rethinking-software-benchmarks-in-an-ai-driven-market/); [iCapital interview with D. Breach](https://icapital.com/insights/practice-management/the-bridge-ep-10-ai-broke-the-rule-of-40-meet-the-rule-of-70/) | **Accurate.** Vista calls it "an emerging aspiration, not a universal baseline", with the margin undefined. Breach describes 60–70 on an **EBITDA** basis and claims 15–20 points of further margin (unverified company claim). | PE |
| V7 | Bain (Lipman et al., 2026) "Rule of 30" | [Bain, Apr 2026](https://www.bain.com/insights/ai-brings-headwinds-and-tailwinds-to-the-rule-of-40/) | **Accurate.** It is a temporary concession, not a recommendation. Transformed companies saw 10–25% EBITDA increases. | PE |
| V8 | Palantir Q2 2026: 155 on adjusted margin, 140 on GAAP (Sections 1, 8.3) | [Palantir 8-K Ex. 99.1](https://www.sec.gov/Archives/edgar/data/0001321655/000132165526000039/a2026q2ex991pressrelease.htm) | **Accurate:** growth 93%, adjusted margin 62%, GAAP margin 47%. | PM |
| V9 | Damodaran software WACC 9.34% (Section 6 annuity) | [Damodaran WACC, Jan 2026](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/wacc.html); [Damodaran EV/Sales](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/psdata.html) | **Accurate.** But it rests on D/(D+E) = 5.28% and a 5.29% pre-tax cost of debt: a near-unlevered, large-cap figure. Also:<br>• Software (System & Application) aggregate EV/Sales is 11.41.<br>• Damodaran classifies **Software (Entertainment)** (77 firms) separately. | Credit, PM, sell-side |
| V10 | SaaS M&A and public multiples by score bucket | [SEG 3Q25 report](https://sandhill.com/wp-content/uploads/2025/12/SEG-Research-3Q25-SaaS-MA-and-Public-Market-Report.pdf) | **Index:** median EV/TTM revenue 5.3x (quartiles 2.8–8.4x).<br>**By "weighted Rule of 40" (1.33×growth + 0.67×EBITDA margin):** >40 → 12.7x; 30–40 → 7.9x; 20–30 → 5.2x; 10–20 → 3.4x; <10 → 1.6x.<br>**By growth:** 20–30% → 8.1x; 30%+ → 10.8x.<br>**By NRR:** 90–100% → 4.0x.<br>**M&A:** median EV/TTM revenue 4.1x. | Sell-side, M&A, PM |
| V11 | Bending Spoons Q2 2026: +126%, organic 3%, operating margin 34% (Sections 1, 6, 8.3) | [BSP 6-K Ex. 99.1, 13 Aug 2026](https://www.sec.gov/Archives/edgar/data/0002004711/000200471126000011/bsp_ex99-1.htm) | **Accurate.** Interest expense was $108.97M, **15.5% of revenue**. The 2.4x leverage ratio uses adjusted EBITDA that includes "certain expected cost savings". | Short, credit |
| V12 | BSP accounting basis and cash-flow content (Remark 3 discussion, "If operating cash flow is stated after interest paid…") | [BSP 6-K Ex. 99.2](https://www.sec.gov/Archives/edgar/data/0002004711/000200471126000011/bsp_ex99-2.htm) | • **US GAAP** (Note 1), and interest paid sits in operating cash flow: "Interests paid" was **$161.2M** in H1 2026.<br>• H1 2026 net investing outflow was $2,290.2M, of which acquisitions were **$2,286.3M** and PP&E only **$4.0M**.<br>• SBC was $43.0M (3.3% of revenue). | Credit, short, M&A |
| V13 | BSP first notes | [BSP 6-K, 28 Oct 2026](https://www.sec.gov/Archives/edgar/data/2004711/000200471126000021/bsp_ex99-1.htm); [Teleborsa on Moody's, 27 Oct 2026](https://www.teleborsa.it/DettaglioNews/219_2026-10-27_TLB/Bending-Spoons-Moodys-assegna-il-rating-Ba3-alle-nuove-obbligazioni-garantite-da-15-miliardi-di-dollari.html) | • $1.25B at 9.625% and €500M at 8.625%, issued at par, due 2032.<br>• "Bending Spoons will not issue or guarantee the notes."<br>• Moody's: Ba3 notes and Ba3 CFR, outlook stable.<br>• Moody's triggers: upgrade below 3.5x adjusted leverage; downgrade if above 4x.<br>• Moody's cites NRR of 97%, which differs from the F-1's 95% for 2025 and 94% for Q1 2026 (unverified; the period is not stated). | Credit |
| V14 | High-yield context | FRED [BB yield](https://fred.stlouisfed.org/data/BAMLH0A1HYBBEY); [B yield](https://fred.stlouisfed.org/data/BAMLH0A2HYBEY) | ICE BofA BB yield 6.67% (27 Oct 2026); B yield 7.99% (28 Oct 2026). BSP's USD secured notes priced about 160 bp over the single-B index. | Credit |
| V15 | Direct-lending norms | [KBRA DLD, 14 Oct 2026](https://www.kbra.com/analytics/products/dld/insights/monthly-insights-and-outlook-at-a-glance-october-14-2026); [KBRA DLD, 24 Sep 2026](https://www.kbra.com/analytics/products/dld/insights/software-slump-leading-new-issuance-to-three-year-low-in-private-credit); [Apollo, Apr 2026](https://www.apollo.com/content/dam/apolloaem/documents/insights/2026/reset-in-software.pdf) | • New-LBO leverage (Sep 2026): UMM/large-cap 4.6x, core MM 4.3x, lower MM 3.8x.<br>• Spreads S+510 to S+528.<br>• Software spreads "gapped to 50 bps over non-software tech".<br>• Peak growth-software buyouts: 15–20x EBITDA purchase multiples, about 6x leverage. | Credit, PE |
| V16 | Recurring-revenue (ARR) loans | [White & Case, Jul 2026](https://debtexplorer.whitecase.com/explorer/charticle/print/3703284); [AllianceBernstein, May 2025](https://www.alliancebernstein.com/us/en-us/investments/insights/investment-insights/software-recurring-revenue-lending-flexibility-and-skill-required.html) | • Peak loan-to-value 30–35%; margins 5.25–5.5%; flip to EBITDA covenants after 3–5 years.<br>• Lenders now prefer "high switching costs, strong retention and datasets competitors cannot easily replicate".<br>• AllianceBernstein example: 2.0x ARR, with the covenant flipping at year 2. | Credit |
| V17 | Serial-acquirer disclosure norm | [Constellation Software FY2025 release](https://www.csisoftware.com/constellation-software-inc-announces-results-for-the-fourth-quarter-and-year-ended-december-31-2025-and-declares-quarterly-dividend/) | • Revenue +15%, "4% organic growth, 3% after adjusting for changes in foreign exchange rates".<br>• FCFA2S of $1,683M, which the company aims to invest entirely in acquisitions that meet its hurdle rate. | M&A, short |
| V18 | US take-private volume | [White & Case](https://mergers.whitecase.com/explorer/charticle/print/3694367) | 41 US take-privates worth $242.9B in 2025, against 39 worth $104.3B in 2024. | M&A |
| V19 | 2026 software de-rating | [SaaStr, 25 Mar 2026](https://www.saastr.com/the-saas-rout-of-2026-is-even-worse-than-you-think-for-the-first-time-ever-software-now-trades-at-a-discount-to-the-sp-500) (secondary); Apollo (V15) | IGV fell about 30% from its September 2025 peak; software forward P/E was 22.7x in Jan–Mar 2026. Apollo: the index fell "as much as 35%". | PM, all |
| V20 | Private-company Rule of 40 | [Standard Metrics, Jul 2026](https://standardmetrics.io/wp-content/uploads/2026/07/Standard-Metrics-Private-Market-Report-Rule-of-40-Revisited.pdf) | • 27.9% of 1,377 private companies passed on an EBITDA basis in Q1 2026.<br>• Zone-1 medians: R40 of 227 at $1–5M ARR and 93 at $100M+.<br>• A 2x growth weight lifts the pass rate for companies with $100M+ ARR from 36% to 56%. | VC |
| V21 | ICONIQ AI gross margins of 45/53/59% (Section 7.1) | [ICONIQ State of AI 2026](https://www.iconiq.com/growth/reports/state-of-ai-2026) | **Accurate.** Consumption pricing rose from 35% to 42%, and outcome-based pricing from 18% to 23%. | VC |
| V22 | The 0.54 success probability behind central execution (Section 7.3, Pace) | [CIO Dive on S&P Global survey](https://www.ciodive.com/news/AI-project-fail-data-SPGlobal/742590/) | **Accurately transcribed, but it measures something else.** The figure is "scrapped 46% of AI proof-of-concepts before they reached production". That is attrition in a funnel of pilots, not the failure rate of committed transitions. | PE |
| V23 | Owner-led change capacity (Bending Spoons) | [PetaPixel, 23 Jan 2026](https://petapixel.com/2026/01/23/almost-all-of-vimeo-staff-laid-off-after-acquisition-by-bending-spoons/) | "A vast majority of Vimeo's staff has been let go", announced 20 Jan 2026, about eight weeks after the 24 Nov 2025 close. The scale comes from employee reports; the date was confirmed by a company spokesperson. | PE |
| V24 | Exzeo, the top organic firm-year of 2023–25 and named in Section 7.3 | [Exzeo FY2025 release](https://www.barchart.com/story/news/426150/exzeo-announces-fourth-quarter-and-full-year-2025-financial-results) | • Revenue +62% to $217.0M, driven by an "expanded scope of services".<br>• It discloses "dependence on HCI Group, Inc. for substantially all of our revenues". | Short, sell-side |
| V25 | Thoma Bravo stance on Rule of 40 weighting | [Buteau summary of Orlando Bravo interviews](https://www.antoinebuteau.com/lessons-from-orlando-bravo/) (secondary) | • Reset acquired companies to "40-60% EBITDA margins".<br>• FCF margin "should carry more weight than top-line growth". | PE |
| V26 | Airtable and Miro prices | [DualEntry](https://www.dualentry.com/blog/bending-spoons-is-buying-miro) (secondary; ARR estimates unattributed) | Airtable about 2.7x ARR; Miro about 2.3x ARR. | M&A |

Not retrieved: the S&P Global EBITDA add-back studies (the page returned no text). The panel does not rely on them.

---

## B. Panel computations (not in the paper)

**B1. Score distribution on the market-convention basis.**
- *Method:* computed from `data/panel.csv` (1,929 core firm-years); linear-interpolated quantiles, no bootstrap.
- *Check:* the method reproduces the paper's Table 4 P95 values (59.9 vs 60; 44.8 vs 45; 55.9 vs 56; 44.1 vs 44).

| Period | FCF before SBC: median | P95 | Pass rate | FCF after SBC: median | P95 | Pass rate | Median SBC/revenue |
|---|---|---|---|---|---|---|---|
| 2010–15 | 29.7 | 71.5 | 27.5% | 24.0 | 65.2 | 18.3% | 4.0% |
| 2016–19 | 30.7 | 67.4 | 32.5% | 23.7 | 59.9 | 19.4% | 6.5% |
| 2020–22 | 32.5 | 82.7 | 35.1% | 18.7 | 62.4 | 20.0% | 10.4% |
| 2023–25 | 29.1 | 57.4 | 28.7% | 15.2 | 44.8 | 9.4% | 12.1% |

Reading:
- On the basis practitioners quote (FCF before SBC: McKinsey, Bessemer, Meritech), the median did not fall from 2016–19 to 2023–25 (30.7 to 29.1).
- P95 fell 10 points, against 15 after SBC.
- Median SBC intensity nearly doubled over the same period.

**B2. Who is in SIC 7372.**
- *Game and casino firms:* the core sample includes Electronic Arts, Take-Two, Activision Blizzard, Roblox, Playstudios and Bally Technologies. Damodaran classifies the game firms separately as Software (Entertainment), V9.
- *Others:* it also includes CoreWeave and Xunlei.
- *Organic top tail of 2023–25:* it includes
  - Exzeo (related-party revenue, V24);
  - Clear Secure (FCF margin about 17 points above operating margin, from prepaid subscriptions);
  - Duolingo and Global-E;
  - Gen Digital.

**B3. Decision weight against the discount rate.**
- *Setup:* Proposition 6 worked example with the paper's parameters (m0 = 0.35, G = 0.04, α = 0.3, k = 0). λ = 0.0698 is calibrated so that v0 = 10 at r = 10%, as in the paper.

| r | 9.34% (Damodaran software WACC) | 10% | 12% | 15% | 22% (buyout target IRR, params.yaml) | 31% (VC target IRR) |
|---|---|---|---|---|---|---|
| v0 (decision weight) | 14.6 | 10.0 | 5.8 | 3.7 | 2.1 | 1.35 |

**B4. Lemma 1 range.**
- At r = 10%, g = 25%, T = 10 and m = 0.10 / 0.25, X^scr is:
  - 0.7 / 1.8 at θ = 1;
  - 1.8 / 2.8 at θ = 1/2;
  - 5.4 / 6.2 at θ = 0.
- At θ = 1/2 and m = 0.25, X^scr is 1.5 at T = 5 and 4.1 at T = 15.
- So Lemma 1 itself covers most of Bessemer's empirical 2–9; longer runways or lower θ reach the top of it.

**B5. Bending Spoons 2025 charged score under alternative conventions.**
- *Inputs:* F-1 extract and V12.
- *Rate:* r = ln(1.0934).
- *Capital:* acquisition capital is the net investing outflows of 2023–25, as in the paper.
- *Life:* decay d = −ln NRR.

| Convention | NRR 95% | NRR 91% |
|---|---|---|
| Paper: levered OCF, level CRF(r, 1/d), all outlays at full cost | 92.8 | 84.4 |
| Levered OCF, economic-depreciation charge (r + d) on year-end decayed capital | 86.2 | 77.5 |
| Unlevered (add back after-tax interest at 24%), (r + d) on year-end capital | 94.5 | 85.8 |
| Unlevered, (r + d) on **average** capital (Vimeo closed 24 Nov 2025) | 104.2 | 98.2 |
| Unlevered, level CRF on average capital | 108.8 | 103.0 |
| Cash return on average acquisition capital (unlevered OCF / capital) | 20.4% | 20.7% |
| Same, less decay d | 15.3% | 11.3% |

Reading:
- The bracket the paper reports (84.4–92.8) is one corner of a 77.5–108.8 range.
- The economically cleaner statement is the one Proposition 13 recommends: a cash return of about 11–15% on acquisition capital, after decay, against a cost of capital of 9.3% or more.
- Pre-2023 outlays are excluded, which flatters every row.

**B6. Bending Spoons Q2 2026 score after interest.**

| Score | Value |
|---|---|
| Reported | 160.5 |
| Reported, after interest | 145.0 |
| Organic (company measure) | 37.1 |
| Organic, after interest | **21.6** |

**B7. LBO after-interest arithmetic.**
- *Case:* a 10% grower with a 35% EBITDA margin, levered 7.0x at 9.5% all-in.
- *Interest:* 23.3% of revenue.
- *Score:* 45 before interest and 21.7 after.
- *At 6.0x and 9.0%:* 26.1 after interest.

**B8. Bending Spoons buyer's multiple.**
- *Inputs:* the extract's secondary IPO valuation (over $18B at the open) and Q2 net debt of $4.09B, against LTM revenue to Q2 2026 of $2,041.8M.
- *Result:* EV/LTM revenue is about 10.8x.
- *Comparison:* it bought at 1.7–3.2x revenue (F-1 pro forma) and about 2.3–2.7x ARR (V26, secondary).

---

## C. The panel, role by role

### C1. Long-only growth portfolio manager (software)

*Incentives:* a benchmark-relative, multi-year holder; wants durable compounding; is paid to hold winners through drawdowns and to avoid value traps.

**Does it change how I screen, value or underwrite?**

Somewhat, in two places.
- *Durable versus transient score (Section 7.3, Table 11):* this is the most useful idea for duration underwriting. A 2025 top-tail score that is 39% transient is a different holding from one that is durable. Clear Secure's "durable under either bound" against Palantir's 24–49-point surplus is the kind of distinction I want.
- *Organic estimand:* I already run it, but the paper makes the case for it rigorously.

What does not change my process:
- **Price lines.** My screens are already regressions of EV/NTM revenue on growth and FCF margin, which is exactly what Bessemer does (V1). The paper does not estimate that regression, so it gives me no new weight.
- **The decision weight of 7–13.** I would not act on it. It is S&M/excess growth divided by an unidentified α (Section 5.4). Even on the paper's own Proposition 6 example, it collapses from 14.6 to 5.8 when r moves from 9.34% to 12% (B3).
- **The AI ceiling (Section 7.2, Table 10)** is the ceiling of a saturated firm at fixed prices. I do not own saturated firms for their ceiling. My 2026 problem is the opposite of fixed prices: the de-rating (V19) is the market pricing Proposition 8 (replication, seat compression), not Corollary 4.

**Claims I challenge (tested):**
1. *"Screening weights of two to three" (abstract; Sections 3.6, 8.1).*
   - Bessemer's regression gave 2x–9x over five to six years, and it calls 2–3x "a conservative base assumption" (V1).
   - Meritech's July 2026 regression gives about 3.8 (V2).
   - So the market's screening weight overlapped the paper's 7–13 in 2020–21. The abstract's "not the screening weights of two to three" sets up a contrast that the practitioner sources do not support as stated.
   - Lemma 1 already spans 0.7 to 6.2 (B4). Say so.
2. *"Consistent with the marginal value of revenue" (Sections 5.4, 5.10(ii)).*
   - Under Proposition 6, X^dyn = v′(s) ≤ roughly the revenue multiple.
   - SEG's 3Q25 data put 20–30% growers at 8.1x TTM revenue and 30%+ growers at 10.8x (V10). That is consistent with 7.2 (α = 0.45), not with 13.0 (α = 0.25).
   - For the median 2026 company (70% below 5x NTM revenue, V2), spending as if a revenue dollar were worth 7+ destroys value at today's prices.
   - The claim is testable, and the paper does not test it.
3. *Discount rate.* The worked example uses r = 0.10, while the paper's own cost of capital elsewhere is 9.34% (Section 6). At 9.34%, v0 = 14.6 (B3). The headline "far above" depends on a parameter the paper does not vary.
4. *Proposition 13(b): "the Rule of X is a rule of economic profit".*
   - This is an identity: e := m + k(g − r).
   - For software, k ≈ 0 because the growth investment (S&M, R&D) is expensed in σ. So e = m, and the "economic profit" restatement adds nothing for the firms the rule is applied to.
   - I capitalize S&M and R&D for ROIC (Damodaran-style). The paper should say that, for software, the invested capital that matters is intangible and sits in σ.
5. *Checked and accurate:* Palantir 155/140 (V8). The paper is right that adjusted, quarterly scores are not comparable with annual cash scores.

**What is missing for practical use:**
- A score-to-multiple bridge, both analytical (B5 style; Change 3) and empirical (an in-sample EV/revenue regression).
- NTM rather than trailing growth.
- SBC as dilution (share-count growth) as well as expense.
- NRR and gross retention as the observable counterpart of zero-spend growth Gᵢ (Remark 4(b)), which the model has but the empirics do not use.

**Misuse risk:**
- Management teams citing "a value-maximizing firm acts on a weight of 7 to 13" (abstract, Section 8.1) in investor letters to defend sub-40 cash scores.
- PMs quoting "ceiling 63 to 88" as a cap on terminal multiples.
- Bulls quoting Corollary 1 ("1,000 for up to 5 years from 10⁻⁵ share") as feasibility.

### C2. Short-seller

*Incentives:* paid to find overstated quality; uses every adjustment that makes a reported number look worse; legal exposure if wrong about a named company.

**Does it change how I screen?**

Yes, and that is the problem. Section 6 and Section 8.3 are a ready-made short template:
- acquired growth credited at X = 1 with no price;
- interest below the line;
- adjusted margins that add back the cost of buying and restructuring businesses (Table 9: 141.6);
- an NRR below 100% read as a treadmill (Proposition 14(f)).

I would lift the fully charged −24.8 and Q1 2026's −129.3 straight into a report.

**Claims I test (and where the paper is weaker than it looks, or stronger):**
1. *Interest double count (Remark 3; Section 6, "The measure of spend cuts both ways").*
   - BSP reports under US GAAP, and interest paid ($161.2M in H1 2026) is inside operating cash flow (V12).
   - So "uncharged, cash" (116.9) is already after interest. The annuity at WACC then charges the debt-financed part of the same acquisitions again.
   - The paper hedges with "If operating cash flow is stated after interest paid…". It is, so resolve the hedge.
2. *Capex contamination is negligible.*
   - In H1 2026, net investing outflow was $2,290.2M, of which acquisitions were $2,286.3M and PP&E $4.0M (V12).
   - The paper's caveat that capital spending "makes both charged scores too low" points the reader the wrong way about the size of the bias.
3. *The bracket is one corner of the convention space.* Depending on levered versus unlevered OCF, level versus decay-consistent charges, and year-end versus average capital, the 2025 annuity score runs 77.5 to 108.8 (B5). I would quote 77.5; a long would quote 108.8. The paper should show the grid, not one bracket.
4. *Top-tail contamination (Section 7.3).*
   - Exzeo is the largest organic firm-year of 2023–25 (score 106 FCF after SBC; B2), and Section 7.3 names it among "the largest surpluses".
   - It discloses dependence on HCI Group for "substantially all" revenue, and its 2025 growth came from an "expanded scope of services" (V24).
   - That is related-party pricing, not demand pull λh. A calibration anchor that reads related-party repricing as a growth surplus is the kind of thing a short-seller finds and a referee misses.
5. *Leverage ratio.* BSP's 2.4x is on adjusted EBITDA that includes "certain expected cost savings" (V11). The paper does not use it, which is correct, but Section 6 should note that the company's own leverage metric is pro forma for savings not yet achieved.
6. *Where the paper is too harsh for my own good.* The abstract says the base "shrinks by 5.1 to 9.4% a year, so that, absent new customers, standing still requires acquiring revenue at that rate". Each part of that sentence needs a caveat:
   - These are log rates (annual 5–9%).
   - NRR covers subscription revenue only, and AOL and Eventbrite are largely not subscription.
   - The company reports +3% organic for Q2 2026, so new customers more than offset churn.
   - Moody's cites NRR of 97% (V13).
   - A target's counsel would call the sentence misleading. I would rather the paper be unimpeachable, because then I can cite it.

**What is missing:**
- A forensic checklist that maps each distortion in Section 8.3 to an XBRL test: SBC/revenue trend, capitalized software trend, deferred revenue growth versus revenue, related-party revenue, gross versus net revenue, run-rate versus GAAP revenue.
- Each test with a threshold.

**Misuse risk:** very high for −24.8 and −129.3. The paper says the fully charged score "is a lower bound, not an estimate" (Remark 3), but that caveat will not travel with the number. Remove the fully charged figures from the introduction, and keep them in Table 9 with the caveat in the row label.

### C3. Sell-side software equity analyst

*Incentives:* needs comps that clients recognize; publishes Rule of 40 charts every quarter; cannot afford basis confusion.

**Does it change my screens?** Not as written, because neither the universe nor the basis matches what I publish.

**Claims tested:**
1. *Universe (Section 4.1).*
   - SIC 7372 includes Electronic Arts, Take-Two, Activision Blizzard, Roblox, Playstudios and Bally Technologies, plus CoreWeave and Xunlei (B2).
   - Damodaran separates games into Software (Entertainment) (V9).
   - The paper calls SIC 7372 "the industry to which the Rule of 40 is usually applied". In practice the rule is applied to SaaS/cloud indices (BVP Cloud Index, Meritech, SEG SaaS Index). A SaaS-only robustness row is needed in Table 14.
2. *Basis (Tables 3–4; Section 5.2).*
   - Every practitioner source I checked uses FCF (McKinsey, Bessemer) or EBITDA (Bain 2018, SEG, Standard Metrics, Vista), before SBC (V1, V4, V5, V6, V10, V20).
   - The paper's headline decline is on SBC-burdened bases. On FCF before SBC, the median was flat (30.7 to 29.1) and P95 fell 10 points (B1), while median SBC/revenue rose from 6.5% to 12.1%.
   - The "fall in the top of the distribution" is real, but a third of it on the cash basis is the SBC trend. Table 3 should carry the FCF-before-SBC column by period.
3. *Precedent on acquired growth.* Bain's 2018 16% figure was "adjusted for M&A" (V4). The paper's E2 is a cleaner version of something practitioners already do; cite it. It strengthens Section 6 rather than weakening it.
4. *Empirical mapping exists.* SEG publishes EV/TTM revenue by weighted-Rule-of-40 bucket, with growth weighted twice margin: 12.7x / 7.9x / 5.2x / 3.4x / 1.6x (V10). The paper should place its frontier statistics against such a mapping, or estimate its own.
5. *Accurate:* the McKinsey and Bain descriptions (V4, V5); Palantir (V8); the internal arithmetic of Table 9 (recomputed: growth 94.7%, operating margin 21.3%, interest 10.9%, outflow 141.8%).

**Most actionable result for me:** Table 8. Among 40–60% growers, 28 of the 37–40-point gap to the frontier is S&M. That is the "efficient growth" Bessemer conditions its multiplier on, and I would use it in initiation reports. It needs an S&M-efficiency metric investors recognize (magic number, CAC payback) alongside it.

**Missing:**
- An NTM basis.
- A list of tickers in the core and organic samples (replication package).
- The organic top tail by name for 2023–25, so I can sanity-check the anchor.

**Misuse risk:**
- "Only 9.4% of software firms pass the Rule of 40" (Table 3, 2023–25, after SBC) will be quoted against the 28.7% on the basis everyone else uses (B1).
- The upper-decile slope of −0.43 to −0.59 will be plugged into single-company models as a growth/margin trade-off, which Proposition 7(iv) forbids.
- The paper states this in Section 5.3; it needs a boxed warning (Change 10).

### C4. PE operating partner (software buyouts)

*Incentives:* paid on MOIC/IRR over a 4–7-year hold; runs 100-day plans; cares about EBITDA, cash conversion, covenant headroom and exit multiple.

**Does it change how I underwrite?**

The structure of Section 3.10 is how good operating partners think: capacity per wave, the scarcest capacity binds (Proposition 11(c)), risk acts as a cut in capacity (Proposition 12(c)), and there is a dip budget. Corollary 3's ordering (growth engine for fast growers, overhead for mature ones) matches the playbook. But the calibration describes a public company running a cautious program, not "an exceptional firm".

**Claims tested:**
1. *Success probability 0.54 (Section 7.3, Pace; params `genai_poc_to_production_rate`).*
   - The source is "scrapped 46% of AI proof-of-concepts before they reached production" (V22).
   - PoC attrition is a deliberate screen: killing weak pilots is success, not failure.
   - Treating the funnel as the probability that a committed transition embeds understates pace. BCG's 80% with six conditions, used for fast execution, is closer to a program-level rate.
2. *Change capacity of 10% of employees a year (central).*
   - The paper's own case contradicts it. Bending Spoons let go "a vast majority" of Vimeo's staff about eight weeks after closing (V23).
   - The extract records "reorganizes at least with each acquisition" and a core team "transferred between businesses on short notice".
   - Owner-led replacement runs at a change capacity near 100% in year one. Section 7.3's ownership paragraph covers public dip budgets, but not this.
3. *Margin targets.*
   - Thoma Bravo resets acquired companies to 40–60% EBITDA margins (V25, secondary).
   - Vista's Breach claims 15–20 more points at Rule-of-70 companies (V6, company claim).
   - Bain reports 10–25% EBITDA increases (V7).
   - These are levels and paces that Table 11's central execution reaches only after decades (2.5% of the program by 2028).
4. *Weights.*
   - Orlando Bravo says FCF margin should carry more weight than growth (V25). That is X < 1, the opposite of Bessemer's 2–3.
   - The paper's Remark 2 has the right idea: owners pick different points.
   - Proposition 6 at our 22% target IRR gives a decision weight of about 2 (B3). That is the clean reconciliation, and the paper should state it.

**Missing:**
- An owner-specific calibration of X: exit EV/revenue at the hold horizon, discounted at the target IRR.
- A value-creation bridge (EBITDA growth, multiple, deleveraging) linked to the parameters (m0, λ, k).
- The replace-versus-transform choice. The companion paper has it; even one paragraph here would help.
- A dip budget tied to covenant headroom rather than "guided dip".

**Misuse risk:**
- Management teams quoting "central execution embeds 23% by 2036" (abstract, Section 8.2) to sandbag value-creation plans.
- LPs or boards quoting the 3.0–3.9-point dip to excuse a miss.
- Mixing bases: Vista's Rule of 60 is an EBITDA-basis aspiration (V6), while the paper's ceilings are after-tax FCF after SBC.

### C5. Growth-stage VC investor

*Incentives:* power-law returns; underwrites the 1-in-20 outlier; screens on ARR growth, NRR, burn multiple and gross margin; FCF is usually negative.

**Does it change how I screen?**

Marginally. Bessemer itself says the Rule of X is "most relevant for late-stage businesses" and that for negative-FCF companies burn multiple is the focus (V1).

What I would use:
- the score budget (Proposition 4, Corollary 1) as a formal statement of how long hypergrowth can last against TAM headroom;
- the compute-share sensitivity (Section 7.2), which is the live question for AI-native gross margins (ICONIQ: 45% in 2025, projected 59% in 2027; V21).

**Claims tested:**
1. *The frontier is public-only (Section 8.6).*
   - Standard Metrics' private cohort has Zone-1 median R40 of 227 at $1–5M ARR and 93 at $100M+ ARR (EBITDA basis; V20).
   - That fits the paper's small-base bound (Proposition 3(c)) and shows how far the private frontier sits from the public anchor of Table 11 (median 51).
   - The paper says only that the sample "likely understates the current frontier at high growth". It should put numbers on it.
2. *"A Rule of 1000 requires 7 to 21 times the demand pull of today's best firms" (Section 7.2).* Correct relative to public firms. But the public top tail is the wrong comparator for a VC: at $1–5M ARR, median Zone-1 companies already score above 200. The Corollary 1 example (from 10⁻⁵ share, at least 1,000 for up to 5 years) is the relevant regime for early-stage AI.
3. *Weights.* Bessemer uses about 2x for private companies (V1); Standard Metrics applies 2x (V20). Both are consistent with Lemma 1 at short persistence. The VC target IRR of 31% gives v0 = 1.35 in Proposition 6's example (B3). Investors with high hurdles act on low weights; founders with low costs of capital act on high ones. That tension is the real governance issue in growth rounds, and the paper's two-weight framework could name it.

**Missing:**
- A burn-multiple mapping. In model terms, net burn / net new ARR ≈ (σ − m0)/Δ for k ≈ 0.
- A version of the score for negative-FCF firms. Lemma 1(c) handles transitory margins; use it.
- ARR versus GAAP revenue.

**Misuse risk:**
- Founders citing the decision weight to justify burn.
- Late-stage investors citing "Rule of 1000 only briefly" to dismiss AI-native outliers, when the paper's own Corollary 1 says that brief can mean several years from a tiny base.

### C6. Leveraged-finance banker / credit analyst

*Incentives:* downside protection; paid on spread and recovery; underwrites leverage (debt/EBITDA with add-backs), coverage, FCF/debt, and LTV for ARR loans.

**Does it change how I underwrite?** No; the score is not a credit metric. Two parts are useful as a growth-quality overlay:
- Proposition 14(c): debt-financed acquisitions leave the operating score unchanged.
- The organic score after interest for serial acquirers.

**Claims tested:**
1. *Interest-adjusted score as a capital-structure measure.*
   - New-LBO leverage in September 2026 was 4.3–4.8x at spreads of S+510 to S+528 (V15). Peak software deals carried about 6x (V15).
   - At 6–7x and about 9–9.5% all-in, interest is 19–23% of revenue for a 35% EBITDA margin company, so the after-interest score of an ordinary software LBO is about 22–26 (B7).
   - Every LBO fails the Rule of 40 after interest by construction. The paper must say that the after-interest score (Definition 5) belongs beside unlevered peers only with that caveat, and that the economic-profit charge (Proposition 13) and the interest deduction must not both be applied to the same capital.
2. *Cost of capital in the annuity (Section 6, r = 8.93%).*
   - The Damodaran 9.34% is a 5%-debt, large-cap software WACC (V9).
   - BSP's marginal secured cost is 9.625% in USD (V13), priced about 160 bp over the ICE BofA single-B index (V14), with the listed parent not guaranteeing.
   - A WACC below the issuer's own secured coupon is not defensible for a firm with $4.09B of net debt at Q2 2026 and about $3.5B more raised since (TLB add-ons and notes, in the extract).
   - Show r = 11–12% as a sensitivity.
3. *Run-rate interest.*
   - Table 9 uses 2025 interest (10.9% of revenue).
   - In Q1 and Q2 2026 interest was 15.5% of revenue each quarter (Table 9; V11), before the new notes.
   - The "105.0 after interest" is therefore stale. On Q2 2026, the organic score after interest is 21.6 (B6).
4. *Adjusted leverage.* BSP's covenant ratio uses adjusted EBITDA that includes expected savings (V11). Moody's triggers are 3.5x and 4x on its adjusted basis (V13). The paper's point that reported scores credit what has not been paid for has a direct analogue in how leverage is defined; say so in one sentence.
5. *Lender practice corroborates Proposition 8.* After the 2026 sell-off, ARR lenders prefer "high switching costs, strong retention and datasets competitors cannot easily replicate" (V16). That is the scarce input ρ of Proposition 8(c), and it is practitioner evidence worth citing in Section 7.4, lever 1.

**Missing:** coverage (EBITDA/interest) and FCF/debt next to the score in Table 9, and the paper's ψ (tax deductibility) applied to interest.

**Misuse risk:**
- Credit memos citing "a durable score of 55" (Section 7.3) to justify leverage.
- Sponsors citing the decision weight to argue that cash burn is value-creating in an ARR-loan negotiation.
- Using the after-interest score as a covenant: it moves with rates, not with operations.

### C7. M&A banker (software take-privates)

*Incentives:* paid on completion; writes fairness opinions and board books; needs defensible comps and a clean organic/inorganic story.

**Does it change my work?** It gives me language for acquired growth (X − k^acq; the treadmill of Proposition 14(f)) and a principled pro forma organic method (E2, Table 2 notes, using ASC 805 pro forma). But it confuses a measurement lens with a decision rule.

**Claims tested:**
1. *"For X = 1 any purchase above one times revenue lowers the properly charged score" (Proposition 14, Intuition).*
   - True, and uninformative for value. The SaaS M&A median in 3Q25 was 4.1x TTM revenue (V10), so every normal software deal "lowers the score".
   - The decision-relevant weight is the buyer's marginal value of a revenue dollar. BSP trades around 10.8x LTM revenue on its IPO valuation (B8) and buys at 1.7–3.2x revenue, or about 2.3–2.7x ARR for Airtable and Miro (V26, secondary).
   - At that X, X − k^acq is about 8 per point of acquired growth. That is multiple arbitrage, and it creates value only if the transformation lifts acquired margins and the supply of targets ḡ^acq lasts.
   - Proposition 14(b) is exactly this bang-bang rule. The text should state it at X = X^dyn and keep X = 1 for measurement.
2. *Market practice on organic disclosure.*
   - Constellation reports total growth of 15%, with 4% organic and 3% after FX (V17).
   - BSP reports a company-defined organic measure (V11).
   - The paper's organic estimand mirrors standard disclosure for serial acquirers. A second worked case with a long disclosure history (Constellation) would make Section 6 read as measurement, not as a view on one newly listed company.
3. *Take-private context.* There were 41 US take-privates worth $242.9B in 2025 (V18). Prices are reported on EBITDA (secondary: about 18x for SaaS take-privates in 2025). The paper has no EBITDA basis at all; bankers will want one.
4. *Charging convention.* The panel's B5 grid shows that the sign and size of the charged score depend on conventions that ROIC practice already settles: unlevered, average capital, economic depreciation. Use them, and report deal-level cash ROIC against WACC.

**Missing:**
- A post-deal score bridge (standalone + synergies − financing + amortization).
- Treatment of contingent consideration and holdbacks (Constellation reports both, V17).
- A rule for organic growth when only ASC 805 pro forma totals are disclosed (the paper's formula in the Table 2 notes is good; promote it to the text).

**Misuse risk:**
- Board books citing "the Rule of 40 is a price line" to argue that a target below the line is mispriced.
- Activists citing "acquired growth enters at X − k^acq" to oppose any deal above 1x revenue.
- Fairness opinions borrowing the annuity bracket without its convention choices.

---

## D. Consolidated top 10 changes (ranked)

**1. Re-state what the screening weight is (abstract; Section 1; Definition 1; Section 3.6, Discussion after Lemma 1; Section 8.1).**
*Analysis:* V1–V3 and B4; add B3.
*Proposed text, end of the Discussion after Lemma 1:*
> "Practitioner weights are themselves estimates that move with the market. Bessemer obtains its 2 to 3 from a multiple regression of FV/NTM revenue on growth and FCF margin over about five to six years, in which the implied ratio ranged from about 2 to 9, and treats 2 to 3 as a conservative base (Deeter and Bondy, 2024); a two-factor regression in July 2026 put growth at 3.8 times FCF margin (Meritech). Lemma 1 covers most of this range: at a ten-year runway X^scr runs from 0.7 to 6.2 as margin persistence θ falls from 1 to 0, and it rises further with the runway. The decision weight is equally sensitive to the discount rate: in the worked example of Proposition 6, v0 is 14.6 at r = 9.34%, 10 at 10%, 5.8 at 12% and 2.1 at 22%, a typical buyout target return. An owner who discounts at a buyout hurdle acts on a weight inside the screening range; the gap between screening and decision weights is as much a statement about the owner's discount rate as about duration."

In the abstract, replace "not the screening weights of two to three" with:
> "which can far exceed the weights of about two to three used to screen firms."

**2. Test the 7–13 against market multiples (Sections 5.4, 5.10(ii), 8.1).**
*Proposed analysis:*
- Pull dei:EntityPublicFloat, debt and cash from the same companyfacts interface for the spend-ratio firm-years.
- Compute EV/revenue and regress it on growth and FCF margin by period. This yields the market's screening weight in-sample.
- Compare v(s)/s with α(X − k)/α by growth band.

*Interim text:*
> "For comparison, in the third quarter of 2025 SaaS firms growing 20 to 30% traded at a median 8.1 times TTM revenue and those growing faster than 30% at 10.8 (Software Equity Group); the spend-implied weight of 7.2 at α = 0.45 is consistent with these, the 13.0 at α = 0.25 is not. In July 2026, 70% of public software firms traded below five times NTM revenue (Meritech), so for the median firm a weight of 7 exceeds what the market pays for a dollar of revenue."

**3. Add a score-to-multiple bridge and a screening recipe (new box in Section 8, after 8.1).**
*(a) Analytical translation.*
- Saturated firm: EV/S = (R₁ − G)/(r − G) and EV/FCF = 1/(r − G).
- Growing firm: the Lemma 1 two-stage value, tabulated for (g, m) pairs on the R₁ = 40 line at r ∈ {9.34%, 11%, 13%}.
- Panel example at r = 9.34%, T = 10, G∞ = 3%, θ = 1: (30%, 10%) → 12.1x; (20%, 20%) → 11.7x; (10%, 30%) → 8.3x; (0%, 40%) → 5.2x.
- "The Rule of 40 line is not an iso-value line."

*(b) Empirical anchor:* the SEG weighted-score buckets (V10), cited as practitioner data.

*(c) A six-step recipe:*
1. Compute annual and NTM scores on FCF before and after SBC.
2. Replace reported growth with organic growth (company measure or ASC 805 pro forma).
3. Screen on R_X with X = 2–3.
4. Flag (i) acquisition years, (ii) related-party revenue, (iii) deferred-revenue-driven FCF, (iv) SBC/revenue above 15%.
5. For flagged high scorers, split the score into durable and transient parts (Section 7.3).
6. For levered firms, show the after-interest score only beside the unlevered score.

**4. Report the market-convention basis by period (Tables 3–4; Section 5.2; abstract).**
- Add FCF before SBC and median SBC/revenue to Table 3 (B1).

*Proposed sentence in Section 5.2:*
> "On free cash flow before SBC, the basis most practitioners quote, the median score was 31 in 2016–19 and 29 in 2023–25 and the 95th percentile fell by 10 points; the larger declines on the GAAP and after-SBC bases partly reflect a near doubling of median SBC intensity, from 6.5% to 12.1% of revenue."

In the abstract, qualify "the top of the distribution of reported scores fell by 12 to 15 points" with "after stock-based compensation".

**5. Clean the sample and the calibration anchor (Sections 4.1, 7.3; Table 14).**
- Add a Table 14 row that excludes game publishers and casino-gaming firms (EA, Take-Two, Activision, Roblox, Playstudios, Bally), CoreWeave and Xunlei. Better still, add a row restricted to a recognized SaaS index membership.
- Flag related-party revenue. Exzeo: "substantially all" revenue from HCI, with growth from expanded scope (V24).
- Re-run the 2025 anchor without related-party firm-years.
- In Section 7.3, replace "Palantir and Exzeo carried the largest surpluses in 2025" with:
  > "Palantir carried the largest surplus among firms selling to unrelated customers; Exzeo's, the largest in the sample, reflects an expanded service contract with its former parent rather than demand pull."

**6. Fix the conventions in the Bending Spoons charged scores (Section 6, Remark 3 discussion, Table 9; Sections 1 and 8.3).**
1. State that the statements are US GAAP and that operating cash flow is after interest paid ($161.2M in H1 2026). Present the annuity on an unlevered basis (add back after-tax interest), so that financing is not charged twice.
2. Replace "The net investing outflow includes capital spending … which makes both charged scores too low" with:
   > "Capital spending is negligible: in the first half of 2026 purchases of property and equipment were $4.0 million against $2,286 million for acquisitions."
3. Charge (r + d) on the time-weighted, decayed acquisition capital (economic depreciation consistent with revenue that decays at d = −ln NRR), and report the level-CRF version as a variant.
4. Add a sensitivity at r = 11–12%, noting that the issuer's secured USD notes price at 9.625%.
5. Report the grid of B5: about 78 to 109.
6. Add the measure Proposition 13 recommends: a cash return on average acquisition capital of about 20% before decay and 11–15% after, against a cost of capital of 9.3% or more.
7. In the abstract and introduction, replace "84.4 to 92.8 … with a lower bound of −24.8" with:
   > "between about 80 and 105 when its acquisitions are charged as capital, depending on the charging convention."

**7. Make the Bending Spoons illustration even-handed (abstract; Sections 1 and 6).**
1. Rewrite the NRR sentence:
   > "Its net revenue retention of 91 to 95% means that subscription revenue from existing customers declines by 5 to 9% a year before new customers; the company reports organic growth of 3% for the second quarter of 2026, so new customers more than offset it in that quarter."
2. Add "and about 22 after interest" to the Q2 2026 organic score (B6).
3. Add a second serial acquirer with a long disclosure record: Constellation Software, FY2025 revenue +15% with organic growth of 4% (V17). This shows the measurement point is general.
4. Keep the company's own capital-allocation metric beside the scores: the 25% unlevered IRR hurdle (extract).
5. Move the fully charged figures out of the abstract and introduction.

**8. Separate the measurement lens from the decision rule for acquisitions and leverage (Proposition 14 Intuition; Definition 5; Section 8.3).**
*Proposed text after Proposition 14:*
> "Part (a) at X = 1 is a statement about measurement, not about value. For the acquisition decision the relevant weight is the buyer's own marginal value of revenue, X^dyn of Proposition 6, and part (b) then says to buy whenever the price per dollar of revenue is below it. A serial acquirer that trades at about ten times revenue and buys at two to three times creates value on this test, provided the businesses it buys keep the revenue and reach the margins its plan assumes, and provided the supply of targets lasts. The charged score answers how much of a high score was bought; it does not answer whether buying it was right."

Add to Definition 5 or Section 8.3:
> "The score after interest measures capital structure as well as operations: a software buyout levered seven times EBITDA at a 9.5% coupon carries interest of about 23% of revenue, so its after-interest score sits about 23 points below an unlevered peer with identical operations. Charge either interest or a cost of capital on the same capital, not both."

**9. Recalibrate or relabel execution pace and ownership (Section 7.3, Pace and Ownership; Section 8.2; Remark 2).**
1. Relabel the 0.54 as "one minus the share of AI proofs of concept scrapped before production, a funnel statistic", and say it is a lower bound on the success of committed transitions.
2. Relabel "central execution" as a public-company case. Do not call it the pace of "an exceptional firm" (abstract, Sections 1 and 9).
3. Add an owner-led row: change capacity of 30–60% of affected employees in year one, success 0.8, embedding in one year, in line with the case firm's own practice of replacing rather than transforming (V23; extract).
4. State the buyout-weight result of B3 in Remark 2.

**10. Address the 2026 price regime and add a "how not to use" box (Sections 7.2, 7.4, 8.6; new box at the end of Section 8).**
1. Add a Table 10 variant with pass-through φ = 0.5 of cost savings and a seat-compression scenario on G.
2. Add to Section 7.2:
   > "Table 10 bounds margins at today's prices; it is neither a forecast of scores nor a cap on valuation. The de-rating of software in 2026, about 30% from the September 2025 peak, is consistent with investors weighting the replication channel of Proposition 8 over the fixed-price ceiling."
3. Cite lender practice as corroboration of lever 1 (V16).

*Box text:*
> "How not to use these results. (1) The upper-decile slopes of Section 5.3 describe chosen points across firms; they are not any firm's trade-off and should not enter a single-company model (Proposition 7(iv)). (2) The decision weight of 7 to 13 rests on an unidentified α and a discount rate; a firm that cites it to justify a low score must show that its marginal growth spend earns more than it costs, from cohort payback and retention, at a stated discount rate. (3) Fully charged scores are lower bounds, not estimates. (4) The ceilings of Table 10 hold prices fixed. (5) Whenever a score is quoted, state the margin basis (GAAP, FCF before or after SBC, adjusted), the growth measure (reported or organic) and whether interest is deducted."

---

## E. What the panel checked and found sound

- **Citations:** Palantir's 155/140 (V8); Bain 2018 and McKinsey 2021 counts (V4, V5); Bessemer's 2x / 2–3x and "if growth is efficient" (V1); Bain 2026 "Rule of 30" (V7); Vista "Rule of 60" as an aspiration (V6); ICONIQ 45/53/59% (V21); Damodaran 9.34% (V9).
- **Bending Spoons figures:** the Q2 2026 figures (V11). Every Table 9 ratio, recomputed from the extract: growth 73.4% and 94.7%; GAAP operating margin 19.0% and 21.3%; interest 4.9% and 10.9%; OCF margin 30.5% and 22.2%; outflows 132.6% and 141.8%; Q1 2026 growth 132.2%.
- **Panel replication:** the P95 values in Table 4 reproduce (B1). Lemma 1's numerical example reproduces (B4).
- **The organic estimand** matches serial-acquirer disclosure practice (V17), and Bain already adjusted for M&A in 2018 (V4). The paper is on solid ground, and should say it is extending practice, not correcting it.

## F. Limits of this panel

- **Data gaps:** the panel had no price data, so the 7–13 cross-check (Change 2) uses published practitioner multiples rather than an in-sample regression.
- **Secondary sources:**
  - IPO valuation (extract);
  - Airtable and Miro ARR (V26);
  - Thoma Bravo summary (V25);
  - SaaStr figures (V19);
  - Moody's NRR of 97% via Teleborsa (V13).
  None of the proposed changes depends on them alone.
- **B5 simplifications:** the B5 grid uses 2023–25 outlays only and a flat 24% tax rate on interest; it is a convention sensitivity, not an estimate.
- **Independence:** all seven roles were played by one agent on one model. Appendix E.7's caveat applies: agreement among these roles is weaker evidence than a human practitioner panel. The results should feed the placeholder in Appendix E.3 as such.
