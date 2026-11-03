# Referee report: "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation" (paper1_v1)

Reviewer: anonymous referee, financial statement measurement and valuation. Independent cross-model review; no other review file was read. Materials: paper1_v1.pdf/.txt, sections/*.tex, paper1/macros.tex, sections/tables/*.tex, data/panel_v2_all.csv, data/panel.csv, data/companyfacts_extract.json, code/build_panel_v2.py, paper_stats.py, estimate_revised.py, estimate_organic.py, calibrate_horizons.py, notes/paper_stats.json, empirics_organic.json, empirics_revised.json, calibration_results.json, calibration_anchor_E2.json, notes/case_bending_spoons_f1_extract.md. I re-ran panel statistics from data/panel.csv, recomputed the Bending Spoons scores from the F-1 extract, and re-derived the ceiling, anchor, pace and model examples; I also read the Exzeo FY2025 10-K and the Bending Spoons F-1 on EDGAR for two facts the extract does not contain.

## Summary

The paper models the growth-margin frontier, reads the Rule of 40 and Rule of X as price lines, separates an investor's screening weight from a firm's decision weight, estimates partial-frontier statistics on an "as first reported" XBRL panel of SIC 7372 firms (2010-2025) under two estimands (observed scores E1; organic frontier E2), proposes how to score bought growth, and calibrates a full-cost ceiling and horizon ranges. The theory is carefully stated and the arithmetic of the calibration reproduces from the code. The empirical numbers quoted in the text match the code outputs almost without exception (56 of 58 checks below). The problems are in measurement: (i) the cash-flow basis used throughout is after interest paid and after cash taxes (ASC 230), which the paper never states and which breaks the Bending Spoons annuity calculation (double-counted financing) and the pre-tax/after-tax consistency of the calibration anchor; (ii) a captive, related-party registrant (Exzeo Group) sits at the top of the calibration anchor and of the 2023-25 score ranking; (iii) the "as first reported" claim fails for 7% of firm-years (half of FY2010 and 47% of each firm's first year), and the acquisition flag misses cheap acquisitions, one of which (Xunlei 2025) is in the "organic" anchor; (iv) the headline "7 to 13" weight is an inversion that is more fragile than the text conveys. None of these invalidates the framework, but the headline numbers that depend on them (Bending Spoons annuity score, anchor quartiles and horizon ranges, the Palantir ranking, the 7-13 range) need to be recomputed or requalified.

## Recommendation

Major revision. The theoretical and computational apparatus is sound and reproducible; the measurement claims need correction before the headline numbers can be trusted.

## Findings

### 1. [Major] Interest paid is in operating cash flow under US GAAP, so the annuity score for Bending Spoons double-charges financing, and the "uncharged cash" row is already after interest

Location: Section 6 (sections/measurement_acquired.tex, Remark `rem:acquired-bounds`, "Worked numbers", Table `tab:acquired-score`); abstract; introduction para. 6; Section 8.3 (discussion.tex).

Issue. The F-1 states the financial statements are "prepared in U.S. dollars in accordance with GAAP" (U.S. GAAP; sec.gov F-1, tm2613674-7_f1.htm, read 29 Oct 2026). Under ASC 230-10-45-17(d), cash paid for interest is classified in operating activities. The operating-cash-flow margin $m^{\rm cf}$ of 22.2% (2025) is therefore after interest paid (interest expense was 10.9% of revenue) and after income taxes paid. Two consequences:

(a) The table's "Uncharged, cash: $g+m^{\rm cf}$ = 116.9" is a post-interest number, while "Uncharged, GAAP = 115.9" is pre-interest and "after interest = 105.0" is the GAAP number net of interest. The three rows are not on one basis and the text's ordering ("115.9, 105.0 after interest, ... 116.9 on operating cash flow") invites the wrong reading.

(b) The annuity score charges every investing outflow at $\mathrm{CRF}(r,T)$ with $r=8.93\%$, a cost of capital for the whole capital structure (Damodaran WACC), on top of a cash margin that has already paid the interest on the term loans that financed the deals (the F-1's financing section lists TLB/TLA borrowings of roughly $2.5bn for AOL, Eventbrite and Vimeo). The debt-financed share of the outlays is charged twice. The paper concedes this conditionally ("If operating cash flow is stated after interest paid, the annuity at the cost of capital charges financing twice") but under US GAAP the condition is met, and the headline range 84.4 to 92.8 (abstract, intro, Section 8.3, Table 6) is carried forward uncorrected. The bias is of the order of after-tax interest paid, roughly 8 points of revenue in 2025 (10.9% pre-tax), so the annuity score would be in the low-to-high 90s on an unlevered basis.

Evidence. notes/case_bending_spoons_f1_extract.md: 2025 OCF 290,600; interest expense 142,601; investing outflow 1,851,874; revenue 1,306,404. Recomputed: $m^{\rm cf}=22.24\%$, annuity charge 32.5 to 24.1 points, scores 84.4 to 92.8 (matches macros). notes/acquirer_notes.md line 105 lists "interest paid classification" as "still needed".

Required change. Either (i) add back after-tax interest paid (from the F-1's supplemental cash-flow disclosure) to $m^{\rm cf}$ before applying a WACC annuity, or (ii) keep the levered cash margin and charge the annuity at the cost of equity on the equity-financed share only. Relabel the table rows by basis (pre-/post-interest, pre-/post-tax). Revise the abstract, introduction and Section 8.3 numbers accordingly, and state in Section 4.2 that the panel's cash-basis score is after interest paid and after cash taxes (see Finding 3).

### 2. [Major] A captive registrant with substantially all revenue from its controlling shareholder sits at the top of the calibration anchor and of the 2023-25 ranking

Location: Section 7.3 ("Anchor"; "Palantir and Exzeo carried the largest surpluses in 2025, 24 to 49 points"); Table `tab:calib` 2025 row and every horizon row derived from the anchor quartiles; Section 5.8 ("Palantir ... the third-highest value in 2023-25"); notes/calibration_anchor_E2.json.

Issue. Exzeo Group, Inc. (CIK 1873951; HCI Group's technology subsidiary, listed Nov 2025) is the top firm-year of both anchors (E2: $R=105.7$, cash margin 43.7%, growth 62.0%, S&M not reported and set to zero, so $\Pi_{\rm ub}=\Pi_{\rm lb}=48.9$ points). Its FY2025 10-K states: "substantially all of our revenues to date are from customers who are affiliated with our controlling stockholder, HCI" and "we did not generate meaningful revenue from Non-HCI affiliated customers in fiscal year 2025" (sec.gov, xzo-20251231.htm). Its growth and margin are intercompany transfer prices, not points on any market frontier. With $n=20$ it moves the anchor's upper quartile of $m_0$ (52 points) and of $\Pi$, which set the high ends of every horizon range in Table 7 and the text of Section 7.3; it is also the second-highest GAAP score of 2023-25 (110.8), which is why Palantir is "third-highest".

Evidence. data/panel.csv rows for Exzeo (sm NaN, acq_pay NaN, gw_jump NaN); calibration_anchor_E2.json E2 firm_years[0]; paper_stats.json top_R_op_2023_25.

Required change. Screen the panel for registrants whose revenue is substantially from related parties (XBRL `RevenueFromRelatedParties` against revenue, or a one-line disclosure check for the top tail) and exclude them from the frontier statistics and the anchor; recompute the anchor quartiles, Table 7, the "24 to 49" sentence, the Palantir rank, and the P95 statistics of 2023-25 that Exzeo enters (GAAP and cash). Report the change.

### 3. [Major] The cash-basis score is a levered, after-tax measure; the GAAP basis is unlevered and pre-tax; the model's $m$ is unlevered and pre-tax; the anchor treats observed cash margins as after-tax at $\tau=0.18$ although most anchor firms pay little cash tax

Location: Section 4.2 (definitions 3 and 4), Section 4.4, Section 5.5 (capital intensity), Section 7.3 ("On the after-tax cash basis $m=m_0-(1-\tau)\sigma-kg$"), Section 3.1 Assumption 4.

Issue. `NetCashProvidedByUsedInOperatingActivities` is after interest paid and after income taxes paid (ASC 230-10-45-17), and includes working-capital changes such as deferred-revenue inflows. So $m^{\rm fcf-sbc}$ differs from $m^{\rm op}$ by SBC, capex, accruals, working capital, cash taxes and interest paid; the paper attributes the difference to SBC and capital spending only. Three places are affected. (i) Section 4.4's basis comparison (14.8% vs 16.9% vs 26.7% vs 30.9%) mixes financing and tax with measurement. (ii) The core sample contains voluntary debt-only filers and leveraged firms (Infor, Inc.; SunGard; Epicor Software; Informatica LLC; SSI Investments II; Avaya Holdings; McAfee Corp.) whose cash-basis scores are lowered by interest paid that has nothing to do with the growth-margin trade-off; the capital-intensity gap (Section 5.5) sorts on capex and compares cash scores, so leveraged acquirers can contribute to the "gap on the cash basis without one on the GAAP basis". (iii) The anchor inverts $m_0=m+(1-\tau)\sigma+kg$ with $\tau=0.18$ on observed cash margins; Duolingo, monday.com, Global-E, CrowdStrike, Palantir (until 2025) and Clear Secure carry NOLs and large SBC deductions and paid little cash tax in these years, so their observed $m$ is close to pre-tax and the "after-tax" intercepts (median 43, upper quartile 52) are overstated relative to the after-tax ceiling terms (58, 68) they are compared with. The "14 and 25 points of room" statement understates the gap.

Required change. State the basis in Section 4.2. Add a robustness line adding back after-tax interest paid (`InterestPaidNet`, which the extract does not yet carry) and, for the anchor, either compute intercepts on a pre-tax basis and apply $(1-\tau)$ once, or use each firm's cash tax rate. Discuss deferred revenue as a reason the FCF-before-SBC pass rate (30.9%) exceeds the adjusted-GAAP pass rate (26.7%).

### 4. [Moderate] "As first reported" does not hold for 139 core firm-years (7.2%), including half of FY2010 and 47% of each firm's first sample year; early-period survivorship is understated

Location: Section 4.1 ("Every item for a fiscal year is taken as first reported ... the sample does not condition on survival"); Appendix C.

Issue. The "original filing" is the earliest annual report that contains a revenue fact for the year. For a pre-IPO year, and for FY2010 of registrants that entered XBRL in the 2011 phase-in, that filing is the following year's 10-K: 139 of 1,929 core firm-years have the original filing dated more than 400 days after the fiscal year-end (max 620 days), 39 of the 76 FY2010 firm-years, and 137 of 293 first firm-years (47%). These are comparative-year figures, which can already be restated (the AppLovin mechanism the section warns about), and they are not a random subset: median growth 24.5% vs 15.4%, P95 GAAP score 63 vs 55, P95 cash score 73 vs 57. Separately, firms delisted before filing an XBRL annual report (2010-2011) are absent, so FY2010 does condition on survival to the first XBRL filing.

Evidence. Recomputed from data/companyfacts_extract.json accession dates and data/panel.csv.

Required change. Report the count and the construction ("as first reported in an annual report on EDGAR; for x% of firm-years, the comparative column of the following year's report"), add a robustness row excluding backfilled firm-years for the P95 decline and the slope, and qualify the survivorship sentence for 2010-2011.

### 5. [Moderate] The acquisition flag misses cheap acquisitions; one such case (Xunlei 2025) is in the organic anchor; 6% of firm-years have neither tag

Location: Section 4.3; Section 6 ("The acquisition flag"); Section 7.3 anchor; Table 4 panel C.

Issue. The flag triggers on cash paid or goodwill increase at 25% of prior-year revenue, or pro forma revenue 10% above revenue. A target bought at $k^{\rm acq}\approx1$ that adds up to 25% growth is not flagged, and these are exactly the acquisitions that add most score per dollar (Proposition 14(a)). Example: Xunlei Ltd 2025 (E2 anchor, "organic" growth 42.5%): acquisition payments of $52.1m were 16% of prior revenue, and the company attributes its 2025 growth in advertising "mainly" to the acquisition of Hupu (Q4/FY2025 release). Also: 6.1% of core firm-years report neither `PaymentsToAcquireBusinesses*` nor `Goodwill`, so they cannot be flagged below the 100% "unverified hypergrowth" cut; 7 following-year flags are applied across gaps in the firm's years (row shift, not year shift). Only 59 of 469 flagged firm-years receive an organic growth; E2 is mostly an exclusion sample, which drops acquirers' organic points (the notes acknowledge this).

Required change. Add the ASC 805-10-50-2(h)(1) tag `BusinessCombinationProFormaInformationRevenueOfAcquireeSinceAcquisitionDateActual` (revenue of the acquiree included in the consolidated income statement since the acquisition date) to the extract: it gives $S^{\rm ac}_t$ directly and would both extend the organic adjustment and sharpen the flag; shift flags by fiscal year rather than row; inspect the organic top tail firm by firm (Xunlei) before using it as the anchor.

### 6. [Moderate] The "7 to 13" weight is an inversion whose value is set by the choice of $G$ and of the spend proxy; the dispersion is far wider than the quoted range

Location: Section 5.4; Section 3.6 "Implication"; abstract; Section 8.1.

Issue. $\alpha(X-k)=\sigma/\Delta$ with $\Delta=g-G_t$ and $G_t$ the annual sample median growth (12-21%). Recomputing on the panel: with $G_t$ as defined the median ratio is 3.3 (E2x25), but with $G=0$ it is 1.4 (weights 3 to 6); the interquartile range 1.9 to 7.4 maps to weights of 4 to 29. The model's $G$ is the firm's own market growth, which is not observed; the sample median is a convention. The proxy also counts retention spend as growth spend (bias up) and omits expansion R&D (bias down); Section 7.3 then calls the S&M share an "upper bound" on $\sigma$, which contradicts Section 5.4's statement that the proxy omits development work. The conclusion "well above screening weights" survives any of these choices only qualitatively.

Required change. Report the implied weight for $G\in\{0,5\%,10\%,\text{median}\}$ and for current-year vs lagged S&M (3.2 vs 3.3), state the IQR-implied range, and soften the abstract to "of the order of 5 to 15 under the stated conventions".

### 7. [Moderate] "On the GAAP basis it touches the score only through the amortization of acquired finite-lived intangibles" is incomplete

Location: Section 6, Remark `rem:acquired-bounds`.

Issue. Acquisition-related costs are expensed as incurred (ASC 805-10-25-23): 6.5% of revenue for Bending Spoons in 2025; goodwill is tested for impairment (ASC 350-20-35) and the company's own add-back line is "amortization and impairment of acquired intangibles"; reorganization costs (6.0%) are also in GAAP operating income. The GAAP score therefore already charges part of the price of buying and restructuring, which the paragraph on the adjusted margin recognizes but the Remark denies.

Required change. Rewrite the sentence: amortization and impairment of acquired intangibles, expensed transaction costs and restructuring charges enter GAAP operating income; the purchase price itself does not.

### 8. [Moderate] The anchor's growth surplus is interpreted as the $X=1$ surplus while the paper's own estimate says firms act on $X\approx7$-13

Location: Section 7.3 and Table 7 notes ("$\Pi$ scales the 2025 range, floored at zero, by $\mu^{1/(1-\alpha)}$").

Issue. $\Pi=R-R_\infty$ is observed; the horizon rows scale it as if it were $(1-\alpha)\Delta^*$ at $X=1$. If firms act on $X\gg1$ (Section 5.4), their observed point is to the right of the Rule-of-40 tangency, $\Pi_{\rm ub}<0$ is expected (it is negative for 55% of anchor firm-years), and the $X=1$ maximal surplus for the same $\lambda h$ is larger than the observed one. The transient component of Table 7 is then a lower bound on what the model allows, and the "at its durable level" reading of the median is a statement about chosen points, not about the frontier. The text treats the negative surpluses as an anomaly ("inconsistent with the model at $X=1$") rather than as the implication of its own Section 5.4.

Required change. Say so explicitly, or recover $\lambda h$ from $(\sigma,\Delta)$ under the estimated $X$ and recompute $\Pi^*$ at $X=1$.

### 9. [Minor] Grounding of $a_{\min}$ cites "our panel" but the 4.6% comes from the broad sample

Location: Section 7.2 ("the fifth-percentile general and administrative share of firms with $1 to 10 billion of revenue in our panel").

Evidence. Core sample: p5 of G&A/revenue for $1-10bn is 5.9% (2023-25) and 5.75% (all years); broad sample 2023-25: 4.57%. The p10 above $10bn is 2.8-2.9% in both (central 3% is fine).

Required change. Name the sample and period.

### 10. [Minor] Small text-output mismatches

- Section 5.3: "pooled coefficients of $-0.21$ and $-0.24$"; empirics_results.json `within.m_fcf_sbc.pooled_b` $=-0.2346$, i.e. $-0.23$.
- Appendix C: "three predecessor-successor pairs that overlap in one year"; notes/panel_build_log.txt reports 5 predecessor overlap years dropped.
- Introduction: "its existing subscription base shrinks by 5.1 to 9.4% a year" quotes $-\ln\mathrm{NRR}$ (continuous); the annual decline at NRR of 91-95% is 5 to 9%. Section 6 uses "about 5%" correctly.
- Definition 3 (acquired growth): $C^{\rm acq}=k^{\rm acq}g^{\rm acq}$ "of revenue" mixes $S_{t-1}$ (in $g^{\rm acq}$) and $S_t$ (in the score's margin); state which.

### 11. [Minor] Cash-flow element choices to disclose

- `NetCashProvidedByUsedInOperatingActivitiesContinuingOperations` is paired with total capital expenditure (continuing plus discontinued).
- `PaymentsToAcquireProductiveAssets` (used when PP&E payments are absent) can already contain software purchases; adding `PaymentsToDevelopSoftware` may double count for those filers.
- `RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability` exists only under ASC 842 (fiscal 2019 on); the lease robustness row covers no earlier year (pre-842 capital leases used other tags). Say so in Table 9's note.
- The score pairs $g_t$ with $\mathrm{FCF}_t$ (contemporaneous convention) while Lemma 2 says $g_{t+1}+m_t$ is the model-consistent pairing for capex-led firms; a one-line sensitivity for the capital-intensity gap would help.

### 12. [Minor] Sample composition under "current SIC 7372"

The core sample includes voluntary debt-only filers (Infor, Inc.; SunGard; Epicor; Informatica LLC; SSI Investments II), game publishers (Activision, EA, Take-Two, THQ, Roblox, Unity, Playstudios), Block (bitcoin revenue recorded gross), 3D Systems, DIRTT Environmental Solutions (modular interiors), Mobileye, Xperi and several PRC-based 20-F filers. The paper says SIC codes are current codes; it should also say what is in the sample and test the two central statistics excluding voluntary filers and non-software registrants.

### 13. [Minor] Scenario life and NRR in the annuity

$T^{\rm life}=-1/\ln\mathrm{NRR}$ uses a subscription-revenue retention metric while Bending Spoons' 2025-26 revenue includes substantial non-subscription revenue (AOL advertising). The paper calls the life a scenario; it should add that the metric does not cover all acquired revenue.

### 14. [Minor] Quarterly score for Q2 2026

"About 160 as reported and about 37 ... organic" adds quarterly year-on-year growth to a quarterly margin, which Section 4.4 says is not comparable with the annual measures. The caveat is present ("the company's measure for one quarter"); repeat it where the number appears in the abstract and introduction.

## Numbers checked against code outputs and data

| # | Location | Text value | Code/data value | Source | Match |
|---|---|---|---|---|---|
| 1 | Sec. 4.1 | 1,929 firm-years, 293 firms; 517/458/496/458 | 1,929; 293; 517/458/496/458 | panel.csv | Yes |
| 2 | Sec. 4.1 | 3,626 firm-years, 541 firms (broad) | 3,626; 541 | panel_broad.csv | Yes |
| 3 | Sec. 4.1 | items from original filing 96.5-99.8% | op 99.8, ocf 96.5, capex 98.4, sbc 99.2 | paper_stats.json | Yes |
| 4 | Sec. 4.1 | 88% U.S. address | 88.4% | paper_stats.json / recomputed | Yes |
| 5 | Sec. 4.1 | AppLovin restated 2023 35% below original 2022; +17% as first reported | -34.6%; +16.5% | paper_stats.json | Yes |
| 6 | Sec. 4.3 | flag covers 24%; 37% of g>50%; 6% discontinued ops | 24.3; 36.5; 6.0 | paper_stats.json / recomputed | Yes |
| 7 | Sec. 4.3 | E2: 1,516 firm-years, 283 firms, 59 kept | 1,516; 283; 59 | empirics_organic.json | Yes |
| 8 | Sec. 4.4 | pass rates 14.8 / 16.9 / 26.7 / 30.9% | 14.8 / 16.9 / 26.7 / 30.9 | recomputed | Yes |
| 9 | Sec. 4.4 | CoreWeave g 168%, GAAP score 167, cash margin -154%, cash score 14 | 167.9%, 167.0, -153.6%, 14.3 | panel.csv | Yes |
| 10 | Sec. 5.2 | median GAAP R 23.6 to 11.9; pass 18.6 to 9.9%; cash 24.0 to 15.2; 18.3 to 9.4% | same | tab_desc / recomputed | Yes |
| 11 | Sec. 5.2 | median g 20.6 to 12.9; median GAAP margin -6.5 to -1.6 | same | tab_desc | Yes |
| 12 | Sec. 5.2 | P95 GAAP 56 to 44 (-12 [-21,-7]); P90 -8; cash -15, -10 | 55.9 to 44.1; -11.7 [-20.9,-6.6]; -8; -15.2; -10 | tab_top / empirics_revised | Yes |
| 13 | Sec. 5.2 | LOO change -11 to -12 (GAAP), -13 to -16 (cash) | -11.1 to -12.4; -12.7 to -16.1 | empirics_revised loo | Yes |
| 14 | Sec. 5.2 | E2 P95 fell 12 and 12 | -11.6; -12.4 | empirics_organic | Yes |
| 15 | Sec. 5.2 | T(0) +2 [-4,+5]; cash -3 [-5,+1] | same | tab_threshold | Yes |
| 16 | Sec. 5.2 | 18 firm-years g>=40% in 2023-25 vs 57-98; 132 >=20% vs 175-255 | 18; 57/80/98; 132; 175/217/255 | recomputed | Yes |
| 17 | Sec. 5.2 | E2 T(40%) +23 [-9,+40]; +24 [+3,+38]; 12 firm-years | 23.4; 24.2; 12 | empirics_organic | Yes |
| 18 | Sec. 5.3 | upper-decile margins 29, 27, 19, 17, 13, 12 (GAAP) | 29.3, 26.9, 18.7, 17.4, 13.3, 12.3 | recomputed | Yes |
| 19 | Sec. 5.3 | slopes E2 -0.59 (0.16), -0.43 (0.11); E1 -0.46 (0.14), -0.37 (0.11) | -0.585 (0.158), -0.432 (0.115), -0.459 (0.137), -0.366 (0.112) | empirics_organic | Yes |
| 20 | Sec. 5.3 | within-firm FE +0.08 (0.07), -0.02 (0.04); pooled -0.21, -0.24 | 0.080 (0.069), -0.019 (0.041); -0.209, -0.235 | empirics_results within | -0.24 should be -0.23 |
| 21 | Sec. 5.4 | spend ratio 3.3 (IQR 1.9-7.3), S&M 41%, excess 11.5; weights 7.2-13.0; E1 2.9, 6.5-11.6 | 3.26 (1.88-7.40), 41.2, 11.4; 7.24-13.04; 2.91, 6.47-11.65 | empirics_organic / recomputed | Yes |
| 22 | Sec. 5.5 | P95 cash by size 64, 56, 54, 48; slope -2.5 (1.2), 5.7 (2.8) per tenfold; GAAP +0.7 (1.3) | 63.7, 55.9, 54.2, 47.7; -2.5; -5.72 (2.8); 0.7 | tab_scale / recomputed | Yes |
| 23 | Sec. 5.5 | E2 gradient -2.7 (3.4) cash, +3.4 (2.6) GAAP | -2.71 (3.43), 3.43 (2.62) | empirics_organic | Yes |
| 24 | Sec. 5.6 | 2023-25 cap-int gap 38 vs 53, [-22,-3]; GAAP -2 [-10,+3]; half starts at 2% | 37.6 vs 52.5; [-22.3,-3.4]; -2.1 [-9.6,+3.4]; median 2.07% | empirics_revised / recomputed | Yes |
| 25 | Sec. 5.6 | E2 gap 11 (37 vs 48) [-20,-3]; GAAP 1 [-8,+5] | -10.6; -1.3 | empirics_organic | Yes |
| 26 | Sec. 5.7 | SFA shortfall 18/25/32/29; cash 14/20/27/24; entrants 31/28 vs 22/15 | 18.4/25.5/32.2/28.8; 14.1/20.4/26.9/24.1; 30.9/28.0 vs 21.5/14.7 | empirics_revised sfa | Yes |
| 27 | Sec. 5.8 | 76% report all four lines | 76.3% | recomputed | Yes |
| 28 | Sec. 5.8 | E2 gap 32.7 [27,36]; S&M 15.7; slow 16.5 of 38.6; fast 27.7 of 37.1 | same | empirics_organic | Yes |
| 29 | Sec. 5.8 | E1 gap 34.6 [28.9,37.9]; 16.0, 7.6, 5.5, 5.1; 14.9 of 37.3; 28.2 and 13.2 of 39.5 | same | tab_gap | Yes |
| 30 | Sec. 5.8 | Palantir 2025: 56% growth, 32% margin, score 88, rank 3, rank 2 above $1bn | 56.2, 31.6, 87.8, 3, 2 | paper_stats.json | Yes |
| 31 | Sec. 5.9 | robustness: P95 fall 10 to 26; slope -0.24 to -0.60; broad -0.31 | 9.9 to 26.3; -0.24 to -0.60; -0.31 | tab_robust / empirics_revised | Yes |
| 32 | Sec. 6 | BS growth 73.4%, 94.7%, 132.2%; log 66.6% | 73.37, 94.68, 132.22; 66.6 | F-1 extract, recomputed | Yes |
| 33 | Sec. 6 | GAAP margins 19.0, 21.3, 20.0; interest 4.9, 10.9, 15.5 | 18.98, 21.27, 19.98; 4.86, 10.92, 15.50 | recomputed | Yes |
| 34 | Sec. 6 | scores GAAP 92.3, 115.9, 152.2; after interest 87.5, 105.0, 136.7 | 92.35, 115.95, 152.20; 87.49, 105.03, 136.70 | recomputed | Yes |
| 35 | Sec. 6 | OCF margins 30.5, 22.2, 12.6; cash scores 103.9, 116.9, 144.8 | 30.53, 22.24, 12.58; 103.9, 116.9, 144.8 | recomputed | Yes |
| 36 | Sec. 6 | investing outflow 132.6, 141.8, 274.1%; fully charged -28.7, -24.8, -129.3 | 132.58, 141.75, 274.05; -28.7, -24.8, -129.3 | recomputed | Yes |
| 37 | Sec. 6 | amortization 12.8, 11.5, 11.5%; adjusted margin 46.9%; score 141.6; transaction 6.5%, reorg 6.0% | 12.81, 11.52, 11.50; 46.94; 141.6; 6.54; 6.02 | recomputed | Yes |
| 38 | Sec. 6 | r 8.93%; T 10.6-19.5; CRF 14.6-10.8%; annuity 80.9-86.8 (2024), 84.4-92.8 (2025) | ln(1.0934)=0.0893; 10.60, 19.50; 0.1459, 0.1083; 80.9-86.8; 84.4-92.8 | recomputed | Yes (but see Finding 1) |
| 39 | Sec. 6 | pro forma $2,608.5m, 2.0x; k 1.7 to 3.2; full charge 0.7-2.2 pts; annuity 0.19-0.47 | 2,608,496; 1.997; 1.73, 3.23; 0.73-2.23; 0.187-0.471 | recomputed | Yes |
| 40 | Sec. 6 | Vimeo 327 days, $376.9m; outflows 2.3x, 2.8x prior revenue; 11%, 9%; Q1 2026 1.5x | 327; 376,883; 2.30, 2.76; 10.9, 9.1; 1.54 | recomputed | Yes |
| 41 | Sec. 6 | G_i -5.1%, -9.4%; flag correction 17 at 50% | ln 0.95, ln 0.91; 0.25/1.5=16.7 | recomputed | Yes |
| 42 | Sec. 6 | Q2 2026: 126% + 34% = 160; 3% + 34% = 37; gap 123 | same | extract | Yes |
| 43 | Tab. 5 | bases 67.9, 57.7, 44.6, 40.8; G* 32.1, 42.3, 55.4, 59.2; c_full 1.6, 4.1, 11.0, 4.7 | 67.94, 57.74, 44.59, 40.85; 32.06, 42.26, 55.41, 59.15; 1.57, 4.09, 10.95, 4.69 | calibration_results / recomputed | Yes |
| 44 | Tab. 5 | cells 62.7/72.7/87.7/65.2/55.2/42.7 (central) | same by formula | recomputed | Yes |
| 45 | Tab. 5 notes | psi=1 adds at most 9.5; replacement 10.25; k=1.5 loss 45; 36-38; 40-41; psi_15 0.53, psi_5 0.80 | 9.45; 10.25; 45; 35.6-38.3; 40.0-41.4; 0.532, 0.796 | recomputed | Yes |
| 46 | Sec. 7.2 | acc-only bases 69.3, 61.1, 53.2, 44.7; thresholds 31, 39, 47, 55 | 69.28, 61.09, 53.25, 44.69; 30.7, 38.9, 46.8, 55.3 | calibration_results | Yes |
| 47 | Sec. 7.2 | c_c sensitivity 26-72 (23-68 acc-only); tau 40-44, 36 at 9% (32); a_min 40-44; c_err 41, 44, 48 (7.8) | 26.2-71.8 (23.3-67.6); 40.1-44.4, 35.9 (32.2); 40.2-43.6; 41.3, 44.3, 47.6 (7.77) | calibration_results | Yes |
| 48 | Sec. 7.2 | Rule of 1000 lambda h 6.8-9.3; pull 0.45-0.98; 7-21 times; entry 7.5, rent 92.5 | 6.78-9.35; 0.446-0.980; 6.9-20.9; 7.5; 92.5 | recomputed | Yes |
| 49 | Cor. 3 | transience bounds 1.8, 9.6, 5.0 | 1.81, 9.65, 5.01 | recomputed | Yes |
| 50 | Sec. 7.3 | anchor n 20, 7 above P95 margin, P95 44, G 12.0; m0 36/43/52; durable 47/55/63; Pi -17/-1/16; lb 17/25/33, 28/36/44, 12/20/28; score 51; shift 19; -2 to 39% | same | calibration_anchor_E2.json | Yes |
| 51 | Sec. 7.3 | E1 anchor n 15, G 12.9, m0 42, Pi 7, Pi_lb 25, score 54, 12-45%, 53% | 15, 12.9, 42.0, 6.7, 24.5, 54.1, 12.4-45.3, 53.3 | calibration_anchor_E2.json | Yes |
| 52 | Sec. 7.3 | 5 entrants, 4 negative; Clear Secure <=4; Palantir/Exzeo 24-49; monday >21 below; 64-65; gaps 14 and 25; tax gap 0.3 | 5; 4; 4.0; 24.2-48.9; -21.7/-24.8; 65.1/63.7; 14.4, 24.6; 0.30 | anchor rows | Yes |
| 53 | Sec. 7.3 | pace: q 0.34/0.74; disruption 0.23/0.07; 3.0%/14.5% a year; 2.5/10/23%; 30/73/100%; 2033; dips 3.9/3.0; cross 9 yrs; freeze 10%/2% | 0.340/0.744; 0.2316/0.0725; 3.05/14.53; 2.46/9.8/23.1; 29.8/72.6/100; 2032.8; 3.93/3.05; 9.05; 10.3/2.3 | calibration_results pace | Yes |
| 54 | Tab. 7 | 2028 upper: m0 57, durable 77, Pi 57, R 134 | 56.98, 76.98, 56.8, 133.8 | upper_bound block | Yes |
| 55 | Sec. 8.1 | 23 points below no-spend score at ratio 3.3 and 10 points excess growth | 0.10 x (1 - 3.3) = -0.23 | formula | Yes |
| 56 | Sec. 3.6 | worked example v0=10: g 7.6%, spend 10.7%, margin 24.3%; v0=15: 9.2, 23.6, 11.4 | 7.59, 10.8, 24.2 at lambda 0.070; 9.3, 24.2, 10.8 at 0.081 (lambda rounded) | recomputed | Yes (rounding of lambda) |
| 57 | Sec. 3.6 | duration D=10.25 at T=15, 6.5 at T=10; X_scr 1.8/2.8 (theta=1/2), 5.4/6.2 (theta=0) | 10.25, 6.53; 1.78/2.79; 5.42/6.20 | recomputed | Yes |
| 58 | Sec. 7.2 / 8.5 | a_min 4.6% = p5 G&A $1-10bn "in our panel"; 3% = p10 above $10bn; G&A medians 20/12/7; MSFT/ORCL 2.4-3.6 | core p5 5.9 (2023-25), 5.75 (all); broad 2023-25 4.57; p10 >$10bn 2.8-2.9; 19.8/12.2/7.3; 2.40-3.57 | recomputed | 4.6 is broad, not core |

Matched: 56 of 58 (the two exceptions are a rounding slip, -0.24 vs -0.23, and the sample attribution of the 4.6% G&A percentile).

## What I found correct

- Panel construction reproduces the paper's counts exactly; growth is computed within one filing; the Compustat fiscal-year convention is implemented correctly (all 1,929 firm-years check); the duplicate-registrant and spike filters behave as described.
- Every number in the Bending Spoons table and text recomputes from the F-1 extract; the F-1 figures the extract cites were found verbatim in the final prospectus; the extract's own warnings (IPOScoop net loss, KuCoin revenue) are sound.
- Proposition 14(a)-(f) and Remark 3 are algebraically correct; the net weight $X-k^{\rm acq}$, the bang-bang result and the treadmill follow from the definitions; the inequality ordering in (12) holds under the stated condition.
- The organic-growth formula $g^{\rm org}=(1+g)(1+\pi_t)/(1+\pi_{t-1}+\rho_t)-1$ is the constant-perimeter ratio of ASC 805-10-50-2(h) pro formas with the carry-over of the prior year's acquisitions; the validity, repeat and ambiguity rules are sensible and documented, and the flag at 25% reproduces exactly in estimate_organic.py.
- The ceiling (Corollary 9, eq. 29) and its tax substitutions are right: $\psi_T$ gives 0.796 and 0.532; the §174A (domestic R&E, including software, expensed for tax years after 2024), §174 (foreign, 15 years) and §168(k) (100% allowance for property acquired after 19 Jan 2025) statements are correct; $\psi=0$ for working capital is correct.
- Proposition 13 (economic profit) is correct: $R_X=(X-k)g+e+rk$ with $e=m_{op}-rk$; the $k=1.5$, $g=15\%$, $r=10\%$ example (7.5 points, half a point per point of growth) checks. The GAAP operating margin used in the panel is pre-tax, consistent with the model's $m_{op}$; the after-tax wording in Section 8.4 should cross-reference Remark 7.
- The screening-weight lemma and its examples, the dynamic-optimality worked example, the Rule-of-1000 demand-pull requirement and the transience bounds all recompute.
- The calibration arithmetic (full-cost floors, pace, horizon ranges) is internally consistent and reproduces from calibrate_horizons.py; the paper labels scenario values as such.
- The decline in the top of the distribution is robust across the stated variants and does not depend on any single firm (leave-one-out).
- The SBC treatment (FCF after SBC deducts the expensed grant-date amount; adjusted margin adds it back) is standard and clearly defined; capitalized software is correctly deducted from FCF; capital intensity is defined consistently with it.
