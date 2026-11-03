# Referee report 2 (financial statement measurement and valuation)

Paper: "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation" (sole author; arXiv q-fin.GN), version paper1_v1.

Materials used: `paper1/paper1.tex` and `sections/*.tex` (the text as compiled into `paper1_v1.pdf`), `paper1/macros.tex`, `sections/tables/*.tex`, `data/panel_v2_all.csv`, `data/panel.csv`, `data/panel_broad.csv`, `data/companyfacts_extract.json`, `code/build_panel_v2.py`, `paper_stats.py`, `estimate_revised.py`, `estimate_frontier.py`, `estimate_organic.py`, `decompose_gap.py`, `calibrate_horizons.py`, `paper1_macros.py`, `notes/*.json`, `notes/case_bending_spoons_f1_extract.md`, `data/raw/damodaran_2026/wacc.xls`.

Replication steps taken: rebuilt the core and broad samples from `panel_v2_all.csv` with the filters of `build_panel_v2.py`; recomputed every descriptive table and most text statistics independently; re-ran `calibrate_horizons.py` in a scratch copy of the package (it overwrites `sections/tables/tab_calib.tex` and `notes/calibration_results.json`, so it was not run in place); both outputs were byte-identical to the distributed files. New referee analyses (blocks F1, F2, F5, F6 and F10 below) are in `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/referee2_checks.py`, a session scratch file that reads the package and writes nothing to it; each finding states its sample and estimator so that it can be re-run from the package alone. Bootstrap intervals in F2 use 400 firm-cluster draws and will vary slightly by seed. No paper or code file was edited.

---

## 1. Summary

The paper models a software firm that buys growth with expensed spend at diminishing returns, derives a concave growth-margin frontier and reads the Rule of 40 and Rule of X as price lines; separates an investor's screening weight on growth (a duration) from a firm's decision weight (the marginal value of revenue); restates the Rule of X as economic profit plus growth at the net weight X - k; and bounds the cash-basis score under full automation, at full cost and at an attainable pace. Empirically it builds an "as first reported" XBRL panel of 293 SIC 7372 firms (1,929 firm-years, 2010 to 2025) and reports two estimands: observed scores (E1) and an organic frontier (E2) that removes acquired growth by pro forma adjustment or exclusion. Headline results: the 95th percentile of the score fell 12 to 15 points from 2016-19 to 2023-25; the upper-decile slope of margin on growth is about -0.6 (GAAP) and -0.4 (cash) on E2; S&M spending implies a decision weight of 7 to 13; the cash-basis tail is 11 points lower for capital-intensive firms; and a mature asset-light firm exceeds a cash Rule of 100 only if its market grows faster than about 42% a year at a 20% compute share. A new section treats acquired growth, with score bounds, an annuity middle case and a Bending Spoons case.

The arithmetic is unusually well controlled: of 80 checked items (several hundred individual values), 73 match the code and my recomputations, 6 match with a labeling or sample caveat and 1 does not reproduce. The theory's closed forms that I checked are correct. My concerns are about identification and measurement, not arithmetic: the "7 to 13" decision weight is not identified by the ratio the paper uses; the capital-intensity result is driven by capitalized software, not by the physical capital the model describes; the cash-basis score is levered and after actual taxes in a window with large interest-rate and tax-law changes; the calibration infers demand pull at X = 1 while arguing that firms act on X of 7 to 13; and the panel back-fills pre-listing years asymmetrically across periods.

## 2. Recommendation

**Major revision.** The data construction and the code are careful and transparent, and the theory is a useful organizing device. Four findings below (F1 to F4) affect headline claims in the abstract and introduction and must be resolved before the empirical and calibration conclusions can be relied on. None requires new data beyond XBRL elements already available from the same `companyfacts` source.

Severity count: 4 major, 4 moderate, 6 minor.

---

## 3. Findings

### F1 (Major). The decision weight of "7 to 13" is not identified by the spend ratio; the paper's own first-order condition, estimated in levels, gives about 1 to 2

**Location.** Abstract; Introduction (second finding); Section `sec:empirics`, subsection "What the data do and do not say about the growth technology"; Proposition `prop:dynamic`, "Implication"; Table `tab:estimands`, rows "Spend-to-excess-growth ratio" and "Implied weight on growth"; Discussion "Two weights on growth"; Conclusion.

**Issue.** The inversion X - k = (median of sigma/Delta)/alpha requires Delta = g - G with G the firm's zero-spend growth (equation `eq:sigstar`). The code measures excess growth from the cross-sectional median growth of the year (`estimate_revised.py` section 7; `estimate_organic.py` spend frame), which is 13 to 19% by period. In the model every firm with X > k spends, so median growth equals G plus the median firm's Delta; measuring Delta from the median understates it and overstates the ratio. More fundamentally, the first-order condition is linear: sigma_i = alpha(X - k)(g_i - G). A level regression of the S&M share on growth with year effects identifies alpha(X - k) as the slope without knowing G; the median ratio is instead identified by the level of S&M at median growth.

**Evidence** (same 615 firm-years as the paper's ratio of 3.31; `referee2_checks.py`, block F1):

| Estimator | alpha(X - k) | Implied X - k, alpha = 0.45 to 0.25 |
|---|---|---|
| Paper: median of S&M share / (g - median g) | 3.31 | 7.4 to 13.2 |
| Same ratio, baseline G = 5% | 2.26 | 5.0 to 9.0 |
| Same ratio, baseline G = 0 | 1.85 | 4.1 to 7.4 |
| OLS of S&M share on g, year effects, above-median growers | 0.34 (SE 0.10) | 0.8 to 1.4 |
| Median regression, same sample | 0.45 (intercept 0.28) | 1.0 to 1.8 |
| OLS, year effects, all organic firm-years (n = 1,310) | 0.41 (0.06) | 0.9 to 1.6 |
| Firm and year effects, all organic | 0.15 (0.05) | 0.3 to 0.6 |

The median-regression intercept of 0.28 implies a zero-spend growth rate of about -63%, so proportionality between spend and excess growth is rejected: most S&M at median growth is not marginal growth spend. Three further points. (i) Under Remark `rem:taxes` the pre-tax spend satisfies sigma = alpha(X - k)Delta/(1 - tau), so the after-tax decision weight that is comparable with valuation multiples is (1 - tau) times the paper's figure: about 5.9 to 10.7 at tau = 0.18. (ii) The text says log-log slopes are "below one, such as those we obtain"; `notes/empirics_results.json` (`alpha_est`) gives 0.39 (0.14) pooled but 1.09 (0.35) with firm effects, so the within-firm estimate is not below one. (iii) Under ASC 340-40 the S&M line contains amortized commissions, which lag cash commissions in growing firms; the paper notes this but not its sign for the ratio (downward).

**Required change.** Remove "7 to 13" as a finding from the abstract and introduction, or re-derive it: report alpha(X - k) from level regressions (pooled, year effects, firm effects) alongside the ratio; report the ratio under explicit zero-spend baselines (zero, an industry growth proxy, ln NRR where disclosed); state the after-tax conversion; benchmark against the EV/revenue multiples of the same firm-years; and reconcile with F4, where the anchor firms behave as if X were 2 to 5. If the paper keeps a range, it should be stated as conditional on the maintained assumption that all S&M at median growth is growth spend.

### F2 (Major). The capital-intensity gap is driven by capitalized software, not by physical capital; the "capital channel" pattern does not appear in either component

**Location.** Introduction (fourth finding); Section `sec:empirics`, "Capital intensity"; Summary (iv); Section `sec:horizons`, "Levers" (lever 3 evidence); Conclusion ("the cash-basis penalty on capital intensity survives"); Table `tab:estimands`, capital-intensity rows.

**Issue.** The sort variable is capital expenditure plus capitalized software over revenue (`capex_int`). Capitalized development cost is development spending whose classification is a GAAP policy choice (ASC 350-40 for internal-use software, ASC 985-20 for software to be sold); in the model it is expansion R&D (part of sigma) or maintenance (part of a), not the capital k "installed before the revenue it serves" (Assumption `ass:capital`). The paper reads "a cash gap without a GAAP gap" as the capital channel's signature and concedes it is "partly mechanical".

**Evidence** (P95 of R, above minus below the 2023-25 median of the sort variable; 90% firm-cluster bootstrap, 400 draws; E2x25 is the exclusion-only organic sample, which differs from E2 only by its 59 pro forma-adjusted firm-years):

| Sort variable | E1 cash | E1 GAAP | E2x25 cash | E2x25 GAAP |
|---|---|---|---|---|
| capex + capitalized software (paper) | -14.9 [-21.0, -5.1] | -1.9 | -10.9 [-18.8, -3.0] | -1.2 |
| PP&E capex only | +1.8 [-7.4, +11.4] | +2.5 | +4.3 [-3.0, +15.5] | +3.6 |
| capitalizers vs non-capitalizers of software | -13.4 [-24.2, -3.7] | -12.5 | -10.0 [-20.7, -1.8] | -10.2 |
| paper's sort, sorting variable added back to the cash score | -6.1 | | -2.6 | |

Physical capital, the model's k (owned compute), shows no gap on either basis. The software contrast shows a gap on both bases. On E2x25, adding back the sorting variable removes three quarters of the cash gap, so the organic result is almost entirely mechanical.

**Required change.** Report the PP&E and capitalized-software components separately; sort on lagged PP&E intensity or on the PP&E stock over revenue rather than on a flow deducted from the outcome; treat capitalized software as R&D in the gap decomposition and when comparing GAAP margins across firms; and withdraw the "survives" claim and the lever-3 evidence unless a PP&E-based test supports them.

### F3 (Major). The cash-basis score is levered and after actual cash taxes, in a window with large interest-rate and tax-law changes; the model and the ceiling are unlevered and taxed at tau

**Location.** Section `sec:data`, definition 4 (FCF after SBC); Section `sec:empirics` (cash-basis decline of 15 points, Table `tab:top`); Section `sec:horizons-ranges` (anchor intercepts and the comparison with Table `tab:ceiling`); Proposition `prop:acquired-score`(c) ("margins exclude interest").

**Issue.** Operating cash flow under US GAAP includes interest received and interest paid (ASC 230-10-45-16(b), 45-17(d)) and actual cash taxes. Three effects move within the comparison windows: (a) interest income on cash and securities: three-month Treasury yields averaged about 1.3% over 2016-19 and about 4.7% over 2023-25, so a firm holding cash equal to one year's revenue gained roughly 3 to 4 points of cash margin between the windows from interest alone, which biases the measured cash-basis decline toward zero and inflates the 2023-25 anchor intercepts of cash-rich firms; (b) section 174 capitalization (tax years beginning after 31 December 2021) raised cash taxes of profitable U.S. filers in fiscal 2022 to 2024 (for R&D at 20% of revenue, the first-year disallowance alone is about 18% of revenue of deductions, roughly 3.8 points of revenue at 21%), and section 174A with its transition election for unamortized 2022-24 amounts lowers fiscal 2025 cash taxes; 9 of the 20 E2 anchor firm-years are fiscal 2025; (c) ASU 2016-09 moved excess tax benefits of share-based payment from financing to operating cash flow from 2017, so OCF of profitable, SBC-heavy filers is not comparable between 2010-16 and later years. In addition, the anchor computes m0 = m + (1 - tau)sigma + kg with the observed FCF margin m after actual taxes, which are close to zero for several anchor firms with loss carryforwards, but compares m0 with a ceiling taxed at tau = 0.18; for a zero-tax firm the comparable after-tax intercept is lower by tau(m + kg), about 4 points at the anchor median m of 22.8.

**Evidence.** The panel contains no interest or tax-paid elements (`build_panel_v2.py` retrieves 35 elements, none of them `InterestPaidNet`, `InvestmentIncomeInterest` or `IncomeTaxesPaidNet`), so the paper cannot currently size these effects. The text is silent on all three.

**Required change.** Retrieve `InterestPaidNet`, `InvestmentIncomeInterest` (and variants), `IncomeTaxesPaidNet` and, for pre-2017 years, `ExcessTaxBenefitFromShareBasedCompensationFinancingActivities`. Report (i) an unlevered cash margin that adds back after-tax net interest, and (ii) a constant-tax cash margin that replaces actual cash taxes with tau times the pre-tax operating cash margin; repeat Table `tab:top`, the E2 decline and the anchor on both. Report cash taxes paid by period and flag U.S. cash taxpayers in fiscal 2022 to 2025.

### F4 (Major). The calibration infers demand pull and surpluses at X = 1 while the paper argues that firms act on X of 7 to 13; the two are inconsistent, and the lower-bound horizon case has no structural interpretation

**Location.** Section `sec:horizons-ranges` (Anchor, Ranges) and Table `tab:calib`; "Rule of 1000" paragraph of Section `sec:horizons-ceiling`; Introduction paragraph "Combining model and estimates"; Discussion "Two weights on growth"; abstract (horizon claims).

**Issue and evidence.**
(a) Under the paper's decision weight, R1 - R_inf = Delta(1 - k - alpha(X - k)), negative for every optimizing firm when alpha X >= 1.75 (Discussion, first paragraph). Among the 18 anchor firm-years growing faster than G, the median spend ratio sigma_ub/(g - G) is 1.0 (1.2 excluding the firm-year without S&M; `notes/calibration_anchor_E2.json`): for example Palantir 2025, 0.53; Clear Secure 2023, 0.25; Duolingo 2024, 0.42; Global-E 2025, 1.25; monday.com 2023, 2.1. That is alpha X near 1, X of about 2 to 5 for alpha of 0.45 to 0.25, not 7 to 13. The paper should say which weight it believes the anchor firms act on.
(b) For a given observed surplus Pi = R1 - R_inf, the pull consistent with optimization at weight X solves Pi = (lambda h)^(1/(1-alpha)) f(X) with f(X) = (alpha X)^(alpha/(1-alpha))(1 - alpha X), which is maximized at X = 1. The X = 1 inversion therefore gives the minimum lambda h, and "a Rule of 1000 needs roughly 7 to 21 times the demand pull of the best public software firms" is an upper bound.
(c) The horizon R* values are maximal Rule-of-40 scores. A firm acting on its decision weight would not choose them; the abstract and introduction present them as what "exceptional asset-light firms would reach".
(d) The lower-bound case sets sigma = 0 in m0 yet scales Pi by mu^(1/(1-alpha)), a relation that holds only at an interior optimum with positive spend. The 156-point upper end of the combined 2028 range comes from this case (`calibration_results.json`, `lower_bound`, 2028: 40 to 156).
(e) Exzeo Group 2025 does not report S&M, which the anchor sets to zero in the "upper bound" (sigma_ub = 0), so its upper-bound surplus of 49 points is not an upper bound; it is the largest surplus quoted ("Palantir and Exzeo ... 24 to 49 points"). Exzeo's revenue appears to come largely from its parent's insurance subsidiaries; the related-party share should be verified from its filings, since a transfer-priced margin is not a market margin.

**Required change.** State that R* is the Rule-of-40 maximum, not the value-maximizing choice, and report alongside it the Rule-of-40 score a firm acting on X^dyn would choose under the same lambda h, R_inf + Delta*(X)(1 - k - alpha(X - k)); label the Rule-of-1000 multiple an upper bound; drop the lower-bound horizon scaling or derive it from an explicit alternative measure of growth spend (for example, R&D share); replace a missing S&M share with SG&A or exclude the firm-year from the upper-bound case.

### F5 (Moderate). "As first reported" back-fills pre-listing years for firms that later list, asymmetrically across periods (look-ahead selection)

**Location.** Section `sec:data`, Sample ("the sample does not condition on survival"); Appendix `app:data`, "As-first-reported construction"; Section `sec:empirics`, decline of the top tail and the fall in fast growers; Introduction (fifth finding).

**Issue.** The original filing is the earliest-filed annual report containing the year. For a firm that lists later, its first 10-K contains pre-listing comparative years, which enter the panel only because the firm later listed. This is the back-fill bias documented for Compustat by Banz and Breen (1986, Journal of Finance 41(4)). The 2023-25 window cannot yet be back-filled by firms that will list in 2026-27, so the bias is asymmetric and works toward finding a decline. Separately, 51% of fiscal 2010 firm-years come from a later 10-K because of the XBRL phase-in for non-large-accelerated filers, so those years are not "as first reported".

**Evidence** (firm-years whose original filing was filed more than 400 days after fiscal year-end; `referee2_checks.py`, block F5). Share by period: 9.9%, 8.7%, 7.7% and 2.2%. Five of the 23 top-5% cash scores of 2016-19 are back-filled pre-IPO years (ZoomInfo 2019, Datadog 2018, CrowdStrike 2018, Nutanix 2016, MuleSoft 2016). Excluding back-filled firm-years, the change in P95 is -11.5 points on the GAAP basis (paper -11.7) and -12.0 on the cash basis (paper -15.2). Of the firm-years growing at least 40%, 16 of 80 (2016-19) and 11 of 98 (2020-22) are back-filled, against 1 of 18 in 2023-25. A balanced panel of the 88 firms present in both windows still shows P95 falling from 56.2 to 45.1 (GAAP) and 60.1 to 43.4 (cash), so the decline itself survives.

**Required change.** Flag firm-years whose original filing is not that year's own annual report; report the main statistics without them and on the balanced panel; qualify "does not condition on survival" (true for exits, not for entries); and note the XBRL phase-in for 2010.

### F6 (Moderate). The annuity "middle case" is a timing allocation, not an intermediate measure of value; its sign result is an artifact of a single-year snapshot

**Location.** Remark `rem:acquired-bounds` and equation `eq:acquired-bounds`; Section `sec:acquired-growth`, "Worked numbers"; Table `tab:acquired-score`; Introduction and Discussion "Measurement at the limit".

**Issue and evidence.**
(a) By construction CRF(r, T) times the integral of e^(-rt) over [0, T] equals 1 (Appendix `app:proofs-acquired`), so the annuity and the full charge have the same present value. In the year of purchase the annuity charges only CRF times k_acq per point of acquired growth (0.19 to 0.47, as the paper reports) against the full one-time growth credit; the remaining charges fall on later years' scores, which receive no growth credit. The undiscounted lifetime annuity is 1.55 to 2.11 times k_acq. "The charging convention, not the data, decides the sign" is therefore true only of a single year; in value, and summed over the life of the purchase, the sign is set by k_acq against X under both conventions, as Proposition `prop:acquired-score`(a) states.
(b) Proposition `prop:general`(b) shows that when capital is charged as a carrying cost (economic profit), growth must be weighted at the net weight X - k. The annuity score charges a carrying cost but keeps the gross weight X = 1, so it is not a value-consistent middle case under the paper's own generalization.
(c) A level annuity over the mean life is not the charge matched to revenue that decays at rate delta = -ln NRR; the matched charge is (r + delta) on the undepreciated balance. On the extract's figures it gives 77.5 to 86.2 for 2025 (paper 84.4 to 92.8) and 75.3 to 81.9 for 2024 (paper 80.9 to 86.8).
(d) The ordering "fully charged <= annuity" holds only when outlays grow fast (the Remark states the condition); for a steady acquisition programme, CRF times T exceeds 1 and the annuity score is the lower of the two. The case text calls the full charge "a lower bound, not an estimate" without the condition.
(e) The Introduction and Discussion present 84.4 to 92.8 as following from the 115.9 GAAP score ("115.9, 105.0 after interest and 84.4 to 92.8 when ... charged as an annuity"), but the annuity and full charge are computed from the operating-cash-flow score of 116.9. Whether that score is already after interest depends on the basis of preparation: interest paid is operating under US GAAP and an accounting choice under IAS 7.33. The extract does not say which framework Bending Spoons uses; the paper's conditional ("If operating cash flow is stated after interest paid ...") should be resolved from the F-1.

**Required change.** Present the annuity as an allocation with the same present value as the full charge; state that the sign of acquired growth's value effect is set by k_acq versus X; add the matched declining-balance variant or justify the level annuity; condition the "lower bound" language; relabel the Introduction and Discussion sequence by basis (GAAP, cash); and state the framework and the classification of interest paid.

### F7 (Moderate). SIC 7372 is not the Rule-of-40 population; the broad sample is not a software superset

**Location.** Section `sec:data`, Sample ("prepackaged software (SIC 7372), the industry to which the Rule of 40 is usually applied"); Appendix `app:data`, Known limitations.

**Evidence** (`data/sic_universe.json`). The core excludes Workday (SIC 7374), Zscaler (7371), Zoom Communications (7370) and Wix (7370); Palo Alto Networks and Fortinet are absent from the 7370-7374 universe altogether because their EDGAR SIC lies outside it. The core includes CoreWeave (AI computing capacity; 2025 GAAP score 167), Exzeo Group, GCL Global Holdings and Xunlei. The broad sample adds internet platforms (Meta, Alphabet, AppLovin), payroll processing (ADP) and IT services, so it is not a software robustness check but a different industry mix.

**Required change.** Define a software sample from business descriptions or a practitioner constituent list (for example, historical constituents of a cloud-software index), include software firms with hardware SIC codes, report the headline statistics on it, and flag non-software firms in the core.

### F8 (Moderate). E2 is mostly an exclusion sample; E1 - E2 differences mix sample composition with growth adjustment; the flag has avoidable gaps

**Location.** Section `sec:data-estimands`; Table `tab:estimands`; Section `sec:empirics` ("Acquired growth flattens the GAAP slope"; size gradient "disappears"); the acquisition-flag paragraph of Section `sec:acquired-growth`.

**Evidence.** Only 59 of 469 acquisition-affected firm-years (12.6%) receive a pro forma adjustment; 410 are excluded (`empirics_organic.json`, `coverage`). E2 removes 21.7%, 21.0%, 29.6% and 12.7% of firm-years by period, so its composition changes across the windows being compared. The exclusion-only sample gives a GAAP slope of -0.56 against -0.59 for E2 and -0.46 for E1: most of the E1 - E2 difference comes from dropping firm-years, not from correcting their growth. The flag threshold is a price (25% of prior revenue), so at software prices of 5 to 10 times revenue it removes deals adding only 2.5 to 5% of growth, while cheap revenue purchases without pro forma disclosure, and asset acquisitions with no goodwill, pass. Two coding gaps: the cash criterion fails when a filer tags `PaymentsToAcquireBusinessesNetOfCashAcquired` with a negative sign (22 core firm-years; none large in the core, but Aspen Technology fiscal 2022 shows -$5.57 billion in the broad sample); and the following-year flag uses a row shift, so it fails when the acquisition year is missing from the panel. Aspen Technology fiscal 2023, with 116% growth after its 2022 combination, is unflagged and is the top cash score of the broad sample in 2023-25 (136).

**Required change.** Use the absolute value of acquisition payments; add payments for intangible assets as an asset-acquisition criterion; flag the following year by fiscal-year adjacency, not row order; report a fixed-sample comparison (same firm-years, reported versus organic growth) to separate the growth correction from composition; replace causal wording ("acquired growth flattens") with sample wording; and say "halves and loses significance" rather than "disappears" for the size gradient (E2 -2.7, SE 3.4).

### F9 (Minor). Accounting-standard breaks inside the "as first reported" windows

**Location.** Section `sec:data`; Appendix `app:data`, Known limitations.

**Issue.** (a) ASC 606, effective for public entities for annual periods beginning after 15 December 2017, was mostly adopted by the modified retrospective method, so the adoption-year filing reports the current year under ASC 606 and the prior year under ASC 605; growth in fiscal 2018 for calendar filers mixes standards inside the 2016-19 base window. (b) ASC 340-40 capitalization of commissions, adopted with ASC 606, lowered reported S&M expense from adoption, which raises GAAP margins after 2017 and affects the S&M proxy of F1. (c) Before ASU 2021-08 (effective for public entities in fiscal years beginning after 15 December 2022), acquired contract liabilities were written down to fair value, so post-acquisition revenue, and pro forma revenue, were understated for pre-2023 deals.

**Required change.** Flag ASC 606 adoption years and show the decline and slopes without them; note the direction of each break.

### F10 (Minor). The upper end of the accountability-floor band does not reproduce; direct audit cost is mis-scaled to the reference firm

**Location.** Section `sec:horizons-ceiling`, "Accountability floor"; Discussion "The accountability floor"; `calibrate_horizons.py` (`a_min` hard-coded at 0.046).

**Evidence.** The text sets the upper end (4.6%) at "the fifth-percentile general and administrative share of firms with $1 to 10 billion of revenue in our panel". On the current panel, 2023-25, the fifth percentile is 5.92% by current revenue (n = 142) and 4.74% by prior-year revenue (n = 123); no script computes 4.6%. The central 3% reproduces approximately (tenth percentile above $10 billion: 2.79%, n = 21). The bottom-up floor applies the S&P 500 audit fee per $1 million of revenue ($343) to a $1 billion firm, but audit fees per dollar of revenue fall steeply with size, so the direct cost at $1 billion is understated; this contradicts the paper's own statement that these costs are fixed in dollars.

**Required change.** Compute the band in code from the panel; use size-matched audit-fee data for Remark `rem:amin-values`; the effect on the central threshold is small (40 to 44% over the band), so this is a grounding fix.

### F11 (Minor). Tax-rate range and after-tax weights

**Location.** Section `sec:horizons-ceiling`, "Taxes, fees and compute"; Remark `rem:taxes`.

**Issue.** The 15% corporate alternative minimum tax applies only to corporations with average adjusted financial statement income above $1 billion (26 U.S.C. 59(k)), so it is not a floor for the $1 billion reference firm. The 21% upper end excludes state taxes; a combined rate of about 25% is the natural upper end for a fully taxed U.S. firm and raises the central threshold to 47.2% (versus 42.3%). Fees of 2 to 3% "of card processing" do not fit invoiced enterprise revenue (near zero) or app-store revenue (15 to 30%; Duolingo is in the anchor). See also F1(i) on after-tax decision weights.

**Required change.** Restate the tax range as statutory federal plus state, with lower effective rates as sensitivity; ground fees by revenue channel.

### F12 (Minor). Accounting statements in the acquired-growth section

**Location.** Remark `rem:acquired-bounds`; Proposition `prop:acquired-score`(d) and its proof; Definition `def:acquired-growth`; Introduction.

**Issues.** (a) "On the GAAP basis it touches the score only through the amortization of acquired finite-lived intangibles": acquisition-related costs are expensed (ASC 805-10-25-23; 6.5% of Bending Spoons' 2025 revenue, reported in the same section), liability-classified contingent consideration is remeasured through earnings (ASC 805-30-35-1), goodwill impairment is charged (ASC 350-20), and before ASU 2021-08 the deferred-revenue write-down lowered acquired revenue. (b) Part (d) equates ln NRR with zero-spend growth, but NRR is achieved with retention and expansion spend, so ln NRR is at most an upper bound on zero-spend growth of the base. (c) The treadmill applies to the subscription share only, (S_sub/S)(NRR - 1); the Introduction's "standing still requires acquiring revenue at that rate" should carry that factor, which matters after AOL (advertising) and Eventbrite (transaction fees). (d) "Shrinks by 5.1 to 9.4% a year" are continuously compounded rates; the annual shrinkage at NRR of 91 to 95% is 5 to 9%. (e) g_acq is defined annually as partial-year acquired revenue over prior revenue, while k_acq is a price per dollar of run-rate revenue, so C_acq = k_acq g_acq fails in the year of a mid-year close; the text acknowledges the timing but the definition should use run-rate revenue.

**Required change.** Correct (a); qualify (b) and (c); relabel (d); align (e).

### F13 (Minor). Score-definition details that bear on interpretation

**Location.** Section `sec:data` (definitions); Section `sec:empirics` (GAAP versus cash slopes); Appendix `app:data`; anchor construction.

**Issues.** (a) The cash-minus-GAAP margin rises with growth across firms (pooled slope 0.083, SE 0.04; median regression 0.12), consistent with deferred revenue financing growth (negative k, Remark `rem:assumptions`(c)); this is part of why the cash-basis slope is flatter than the GAAP slope and should be discussed. (b) Element precedence: 5 core firm-years combine `PaymentsToAcquireProductiveAssets` with a software element (possible double count) and 25 report only software elements and so receive a missing FCF. (c) The anchor's kg uses total capital expenditure, including maintenance, which the model places in a. (d) Taking the largest revenue element can select a gross-of-tax figure (`...IncludingAssessedTax`) in some years and not others.

**Required change.** Discuss (a); document (b) to (d) or adjust.

### F14 (Minor). Text-code inconsistencies and editorial points

1. T(0) is described as "the 95th-percentile GAAP margin among all firm-years"; the code uses firm-years with g >= 0 (`estimate_revised.py`, threshold block).
2. "Slopes below one, such as those we obtain": within-firm 1.09 (see F1).
3. The note to Table `tab:estimands` says the spend ratio of Section `sec:empirics` is the 25% column (3.31; IQR 1.88 to 7.40), but the text uses the E2 values (3.26; IQR 1.88 to 7.26). Both round to 3.3; the note should match the text.
4. "Only 18 firm-years grew at least 40% in 2023-25, against 57 to 98 ... and 132 ... against 175 to 255" uses the GAAP-margin subsample; the full sample has 100 and 258 in 2020-22. State the sample.
5. "Embeds about 23% of its automation program by 2036" is benefit-weighted (b-bar = 0.85; 27% of processes are embedded), while "3.0% of itself a year" is not; use one basis.
6. "The score falls toward market growth plus the return on capital": the term is (r - G)k, a growth-adjusted return.
7. The proof of Corollary `cor:ceiling` cites "a_min = 0.06 ... the earlier form of the corollary", a value no longer used.
8. The Reproducibility paragraph of Appendix `app:data` omits `estimate_organic.py`, `paper1_macros.py` and `verify_part2_acquirer.py`, which generate E2, the macros and the acquired-growth figures.
9. Macro naming: `\acqCrfLo` is 14.6% and `\acqCrfHi` 10.8%, so the text reads "a CRF of 14.6 to 10.8%".

---

## 4. Numbers checked

"Code" means the distributed JSON or table output; "recomputed" means my own computation from the panel or the extract. Values in percentage points unless stated. Match: Yes (agrees at the precision printed), Partial (number agrees but its label or sample in the text does not), No.

| # | Item (location) | Text | Code / recomputed | Match |
|---|---|---|---|---|
| 1 | Core sample (sec:data) | 1,929 fy, 293 firms | 1,929, 293 (rebuilt from panel_v2_all.csv) | Yes |
| 2 | Broad sample | 3,626, 541 | 3,626, 541 | Yes |
| 3 | Firm-years by period | 517 / 458 / 496 / 458 | same | Yes |
| 4 | Items from original filing | 96.5 to 99.8% | 96.47 to 99.84% | Yes |
| 5 | Pass rates GAAP / FCF-SBC / adj / FCF | 14.8 / 16.9 / 26.7 / 30.9 | same | Yes |
| 6 | U.S.-address share | 88% | 88.4% | Yes |
| 7 | Acquisition flag coverage | 24%; 37% of g > 50% | 24.3%; 36.5% | Yes |
| 8 | Discontinued ops; capex missing | 6%; 2.2% | 6.0%; 2.18% | Yes |
| 9 | AppLovin restated vs original; growth | -35%; +17% | -34.6%; +16.5% | Yes |
| 10 | CoreWeave 2025 | 168%, ~0, 167; -154%, 14 | 167.9%, -0.9%, 167.0; -153.6%, 14.3 | Yes |
| 11 | Table tab:desc (40 cells) | e.g. median R 23.6 to 11.9; pass 18.6 to 9.9 | recomputed, all identical | Yes |
| 12 | Median g 2020-22 to 2023-25; median m | 20.6 to 12.9; -6.5 to -1.6 | same (GAAP subsample) | Yes |
| 13 | P95 GAAP 2016-19, 2023-25; change | 56, 44; -12 [-21, -7] | 55.9, 44.1; -11.74 [-20.7, -7.0] | Yes |
| 14 | P95 cash change; P90 changes | -15; -8, -10 | -15.17; -7.77, -9.77 | Yes |
| 15 | Leave-one-firm-out ranges | -11 to -12; -13 to -16 | -11.1 to -12.4; -12.7 to -16.1 | Yes |
| 16 | E2 P95 change | -12, -12 | -11.64, -12.43 | Yes |
| 17 | T(0) change | +2 [-4, +5]; -3 [-5, +1] | +2.46 [-3.5, +4.9]; -2.89 [-5.4, +0.7] | Yes |
| 18 | T(20%), T(40%) changes | -9 to +13 | -8.9 to +12.7 | Yes |
| 19 | E2 T(40%) | +23 [-9, +40]; +24 [+3, +38] | +23.4 [-9.3, +39.6]; +24.2 [+3.1, +38.3] | Yes |
| 20 | Fast-grower counts | 18 vs 57 to 98; 132 vs 175 to 255 | same in GAAP subsample (full: 100, 258) | Partial |
| 21 | Upper-decile GAAP margin by band | 29 / 27 / 19 / 17 / 13 / 12 | 29.3 / 26.9 / 18.7 / 17.4 / 13.3 / 12.3 | Yes |
| 22 | E1 slopes | -0.46 (0.14); -0.37 (0.11) | -0.459 (0.137); -0.366 (0.112) | Yes |
| 23 | E2 slopes | -0.59 (0.16); -0.43 (0.11) | -0.585 (0.158); -0.432 (0.115) | Yes |
| 24 | E1 - E2 paired intervals | 0.02 to 0.33; -0.01 to 0.22 | 0.022 to 0.325; -0.010 to 0.222 | Yes |
| 25 | Sub-period slopes E1 / E2 | -0.31/-0.77, -0.45/-0.79; cash -0.25/-0.40, -0.48/-0.43 | -0.313/-0.767, -0.453/-0.787; -0.253/-0.400, -0.475/-0.425 | Yes |
| 26 | One observation per firm-period | -0.60, -0.43 | -0.602, -0.431 | Yes |
| 27 | Fixed effects; pooled | +0.08 (0.07), -0.02 (0.04); -0.21, -0.24 | +0.080 (0.069), -0.019 (0.041); -0.209, -0.235 | Yes |
| 28 | E2 spend ratio, IQR, medians | 3.3 (1.9 to 7.3); 41; 11.5 | 3.26 (1.88 to 7.26); 41.4; 11.49 | Yes |
| 29 | Implied weights E2; E1 | 7.2 to 13.0; 6.5 to 11.6 | 7.24 to 13.04; 6.47 to 11.65 | Yes |
| 30 | Log-log slopes "below one" | below one | pooled 0.39 (0.14); firm FE 1.09 (0.35) | Partial |
| 31 | Scale: P95 cash by size class | 64 / 56 / 54 / 48 | 63.7 / 55.9 / 54.2 / 47.7 | Yes |
| 32 | Scale slopes | -2.5 (1.2); 5.7 (2.8) per tenfold; GAAP +0.7 (1.3) | same | Yes |
| 33 | E2 scale; difference | -2.7 (3.4); +3.4 (2.6); [-8.1, -0.4] | -2.71 (3.43); +3.43 (2.62); [-8.08, -0.39] | Yes |
| 34 | Capital-intensity gap E1 | 38 vs 53, -15 [-22, -3]; GAAP -2 [-10, +3] | 37.6 vs 52.5, -14.9 [-22.3, -3.4]; -2.1 [-9.6, +3.4] | Yes |
| 35 | Capital-intensity gap E2 | -11 (37 vs 48) [-20, -3]; GAAP -1 [-8, +5] | -10.6 (37.5 vs 48.1) [-19.6, -3.1]; -1.3 [-8.2, +5.0] | Yes |
| 36 | Start of capital-intensive half | 2% | 2.07% | Yes |
| 37 | Stochastic-frontier shortfalls; entrants | 18/25/32/29, 14/20/27/24; 31/28 vs 22/15 | 18.4/25.5/32.2/28.8, 14.1/20.4/26.9/24.1; 30.9/28.0 vs 21.5/14.7 | Yes |
| 38 | Gap decomposition E1 | 34.6 [28.9, 37.9]; S&M 16.0; R&D 7.6; GM 5.5; G&A 5.1 | recomputed point estimates identical | Yes |
| 39 | Gap by band | 14.9 of 37.3, S&M 4.8; 28.2 of 39.5, R&D 13.2; coverage 76% | same; 76.3% | Yes |
| 40 | Gap decomposition E2 | 32.7 [27.0, 35.7]; S&M 15.7; 16.5 of 38.6; 27.7 of 37.1 | 32.69 [27.0, 35.7]; 15.74; 16.45 of 38.56; 27.71 of 37.12 | Yes |
| 41 | Robustness ranges | P95 fall 10 to 26; slopes -0.24 to -0.60 | -9.9 to -26.3; -0.243 to -0.602 | Yes |
| 42 | Edge-statistic sensitivity | falls 26 to 50 | 26 to 50 | Yes |
| 43 | Palantir 2025 | 56%, 32%, 88; 3rd; 2nd above $1 bn | 56.2%, 31.6%, 87.8; 3; 2 | Yes |
| 44 | Median gross margin; cost of revenue | 74; 26 | 73.95; 26.05 | Yes |
| 45 | G&A medians by size; MSFT/ORCL | 20 / 12 / 7; 2.4 to 3.6 | 19.8 / 12.2 / 7.3; 2.40 to 3.57 | Yes |
| 46 | a_min upper end = p5 G&A, $1 to 10 bn | 4.6% | 5.92% (current revenue), 4.74% (prior revenue); hard-coded 0.046 | No |
| 47 | a_min central = p10 G&A above $10 bn | 3% | 2.79% (2023-25), 2.90% (all years) | Yes |
| 48 | Ceiling margin terms | 67.9 / 57.7 / 44.6 / 40.8 | 67.94 / 57.74 / 44.59 / 40.847 | Yes |
| 49 | G* thresholds | 32.1 / 42.3 / 55.4 / 59.2 | 32.06 / 42.26 / 55.41 / 59.15 | Yes |
| 50 | Table tab:ceiling (24 cells) | e.g. 62.7, 72.7, 87.7, 65.2, 55.2, 42.7 | base + (1 - k)G by hand, identical | Yes |
| 51 | Full-cost floors | 1.6 / 4.1 / 11.0 / 4.7 | 1.57 / 4.09 / 10.95 / 4.69 | Yes |
| 52 | Accountability-only bases; thresholds | 69.3 / 61.1 / 53.2 / 44.7; 31 / 39 / 47 / 55 | 69.27 / 61.09 / 53.246 / 44.69; 30.7 / 38.9 / 46.75 / 55.3 | Yes |
| 53 | Threshold sensitivities | c_c 26 to 72 (23 to 68); tau 40 to 44, 36 (32); a_min 40 to 44; c_err 41 / 44 / 48 at 7.8 | 26.2 to 71.8 (23.3 to 67.6); 40.2 to 44.4, 35.9 (32.2); 40.2 to 43.6; 41.4 / 44.3 / 47.6 at 7.77 | Yes |
| 54 | Capital sensitivities | 45; 36 to 38; 40 to 41; 9.5; 10.25 | 45.0; 35.6 to 38.3; 40.0 to 41.4; 9.45; 10.25 | Yes |
| 55 | psi_15; psi_5 | 0.53; 0.80 | 0.5324; 0.7961 | Yes |
| 56 | Rule of 1000: Lambda; lambda h; multiple | 6.8 to 9.3; 0.45 to 0.98; 7 to 21 | 6.78 to 9.35; 0.446 to 0.980; 6.92 to 20.94 | Yes |
| 57 | Transience bounds; Rule-of-1000 example | 1.8, 9.6, 5.0; 8.71, 1,314, 394%, -334% | 1.81, 9.65, 5.01; 8.711, 1,314, 394.3%, -334.3% | Yes |
| 58 | Free entry | 7.5; 92.5 | 7.5; 92.5 | Yes |
| 59 | E2 anchor (N, P95, G, quartiles, shares) | 20, 44, 12.0, 7; m0 43 (36 to 52); R_inf 55 (47 to 63); Pi -1 (-17 to 16); 45%; lb 25 / 36 / 20 (12 to 28); 51; -2 to 39% | 20, 43.6, 12.02, 7; 43.3 (35.8 to 52.3); 55.0 (46.8 to 63.5); -0.8 (-17.4 to 16.1); 45%; 24.7 / 35.9 / 19.6 (12.1 to 27.6); 50.5; -1.6 to 38.8% | Yes |
| 60 | E1 anchor; entrants | 15; 7; 25; 54; 12 to 45%; 53%; 5 entrants, 4 negative | 15; 6.7; 24.5; 54.1; 12.4 to 45.3%; 53%; 5, 4 | Yes |
| 61 | Firm cases | Clear Secure <= 4; Palantir/Exzeo 24 to 49; monday.com > 21, 64 to 65 | 4.0; 24.2 to 48.9; 21.7 / 24.8, 63.7 to 65.1 | Yes |
| 62 | Anchor vs full-cost terms | 14; 25 | 14.4; 24.6 | Yes |
| 63 | Pace (central / fast) | p_emb 0.34 / 0.74; 3.0 / 14.5%; nu_D 0.23 / 0.07; freeze 10 / 2%; 2.5 / 10 / 23; 30 / 73 / 100; 2033; dip 3.9 / 3.0; 9 years | 0.340 / 0.744; 3.05 / 14.53%; 0.232 / 0.0725; 10.3 / 2.3%; 2.46 / 9.82 / 23.08; 29.8 / 72.6 / 100; 2032.8; 3.93 / 3.05; 9.05 | Yes |
| 64 | Horizon ranges (all UB, LB, combined, k = 0.5, deducted) | e.g. 46 to 134, 40 to 156, 41 to 83, 42 to 91 | calibrate_horizons.py rerun: tab_calib.tex and calibration_results.json byte-identical | Yes |
| 65 | Ownership variants | 25%; 8%; 2 vs 5 points; 16%; < 1% | 25.4%; 8.0%; 1.75 vs 5.05; 15.9%; 0.68% | Yes |
| 66 | Bending Spoons ratios (Table tab:acquired-score, 27 cells) | e.g. g 73.4 / 94.7 / 132.2; m_op 19.0 / 21.3 / 20.0 | recomputed from the extract, identical | Yes |
| 67 | Bending Spoons scores | 92.3 / 115.9 / 152.2; 87.5 / 105.0 / 136.7; 103.9 / 116.9 / 144.8; 118.0 / 141.6 / 183.4; -28.7 / -24.8 / -129.3 | identical | Yes |
| 68 | Annuity; CRF; life; r | 80.9 to 86.8, 84.4 to 92.8; 14.6 to 10.8%; 10.6 to 19.5; 8.93% (9.34%) | identical; r verified in wacc.xls (Software, System and Application, 9.344%) | Yes |
| 69 | Deal prices; points per point of growth | 1.7 to 3.2x; 0.7 to 2.2; 0.19 to 0.47 | 1.73 / 2.30 / 3.23x; 0.73 to 2.23; 0.187 to 0.471 | Yes |
| 70 | Flag arithmetic | 17; 2.3 / 2.8x; 11% / 9%; 1.5x; 100% | 16.7; 2.30 / 2.76x; 10.9% / 9.1%; 1.54x; 99.7% | Yes |
| 71 | Q2 2026 scores | 160 / 37 / 123 | 160 / 37 / 123 | Yes |
| 72 | Treadmill (Introduction) | "shrinks by 5.1 to 9.4% a year" | ln NRR: -5.13 to -9.43%; annual shrink 5 to 9% | Partial |
| 73 | Introduction / Discussion sequence | 115.9 GAAP, then 84.4 to 92.8 annuity | annuity computed from OCF score 116.9 | Partial |
| 74 | Valuation worked example | 5.8x; lambda 0.070: 7.6 / 10.7 / 24.3; lambda 0.081: 9.2 / 23.6 / 11.4 | 5.83x; 0.0698: 7.58 / 10.75 / 24.25; 0.0808: 9.24 / 23.58 / 11.42 | Yes |
| 75 | Screening-weight examples | D 10.25 (T = 15), 6.5 (T = 10); 1.8 / 2.8; 5.4 / 6.2 | 10.25, 6.53; 1.78 / 2.79; 5.42 / 6.20 | Yes |
| 76 | Common-frontier example (sec:model-industry) | l 0.86 / 1.14; steepest slope 0.9 to 1.6 | 0.857 / 1.140; 0.889 to 1.600 | Yes |
| 77 | Proposition prop:general example | 7.5 points; -0.5 per point | 7.5; -0.5 | Yes |
| 78 | Discussion figures | 23 points below; a quarter >= 17 below | 23.0; Pi_ub first quartile -17.4 | Yes |
| 79 | T(0) definition | "among all firm-years" | code: firm-years with g >= 0 | Partial |
| 80 | Note to tab:estimands | spend ratio = 25% column | text uses E2 (3.26), not 25% column (3.31) | Partial |

Tally: 80 items checked; 73 match, 6 partial (items 20, 30, 72, 73, 79, 80), 1 does not reproduce (item 46).

---

## 5. What I found correct

- **Panel construction reproduces.** The core and broad samples, period counts and all cells of Tables `tab:desc`, `tab:top`, `tab:threshold`, `tab:local`, `tab:scale` and `tab:gap` (point estimates) reproduce from `panel_v2_all.csv`. The as-first-reported logic in `build_panel_v2.py` (original filing; growth within the same filing; Compustat fiscal-year convention; duplicate and predecessor handling) is implemented as described, and the AppLovin example is correct.
- **E1 and E2 numbers.** Every E1 and E2 figure quoted in the text matches `empirics_organic.json`, including the paired intervals. The pro forma organic-growth formula (1 + g_t)(1 + pi_t)/(1 + pi_{t-1} + rho_t) - 1 correctly implements a constant-perimeter comparison under ASC 805-10-50-2(h), and the ambiguity rule for cumulative comparative presentation is a sensible safeguard.
- **The decline in the top tail is robust where I tested it.** It survives a balanced panel of the 88 firms present in both windows (GAAP 56.2 to 45.1; cash 60.1 to 43.4) and the exclusion of back-filled firm-years (F5), although the cash-basis magnitude falls to about 12 points.
- **Theory.** I verified the frontier, tangency and surplus closed forms in the examples; the economic-profit identity R_X = (X - k)g + e + rk and its value corollaries (Proposition `prop:general`); the score-budget and transience bounds; psi_T; the free-entry limit; and the screening-weight Lemma `lem:valuation2` examples. The separation of screening and decision weights is clear and, in my view, the paper's most useful contribution.
- **Calibration code.** `calibrate_horizons.py` reproduces `tab_calib.tex` and `calibration_results.json` exactly; the ceiling arithmetic, the compute-share, tax, failure-cost, accountability and capital sensitivities, the pace and dip computations and the ownership variants all match the text. The section states its outputs conditionally and labels scenario values throughout, which meets the standard asked for.
- **Tax law as stated is current.** Section 174A expensing of domestic research and experimental expenditure for tax years beginning after 2024, 15-year amortization of foreign research under section 174, the 100% allowance for property acquired after 19 January 2025 and the psi values (0.53, 0.80) are correctly stated and computed.
- **Bending Spoons figures.** All growth rates, margins, ratios and scores in Table `tab:acquired-score` and the text reproduce from the extract; the cost of capital (9.34%, 8.93% continuously compounded) is verified in the Damodaran file; the deal multiples, flag arithmetic and Q2 2026 scores are correct. Proposition `prop:acquired-score`(a), the net weight X - k_acq, is the right organizing result, and its contrast with the uncharged score is the section's strongest point.
- **Transparency.** The decision to report two estimands, the edge-statistic disclosure (Table `tab:edge`) and the appendix protocol are exemplary.
