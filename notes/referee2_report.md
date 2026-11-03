# Referee 2 report: "The Efficient Frontier of Growth and Profitability"

Scope: the compiled PDF (22:20) and its source. `empirics.tex`, `horizons.tex` and several tables changed during my review (23:10-23:15) and are not reviewed. Check scripts: `notes/referee2/`.

## Summary
The paper models the Rule of 40 as an iso-value line tangent to a concave growth-margin frontier, estimates order-alpha Pareto frontiers on an XBRL panel (SIC 7370-7374) and bounds the score under full automation. The theory is clean and the four-margin comparison is useful. But the headline empirical facts rest on a few extreme firm-years, several of them mismeasured and many from firms that are not software companies.

## Recommendation
Major revision.

## MAJOR

**1. Restatement vintages are mixed, and discontinued operations are mishandled (App. B).** The `frames` API returns the latest-filed fact for each period, so years t and t-1 come from different filings.
- AppLovin 2023 growth (-34.6%) compares restated continuing-operations revenue ($1,842M) with total 2022 revenue ($2,817M).
- In 2024-25 its operating cash flow includes the divested Apps business while revenue excludes it: the 2024 FCF-after-SBC margin is 53.5% in the panel but 36.6% on total revenue. AppLovin alone moves the 2023-25 frontier by 28 points (GAAP) and 17 (FCF after SBC).
- Same mechanism: CIK 891103 (old IAC, labelled "Match Group"; 2018 growth -47.7%), Gen Digital (2017 growth -36%) and LiveRamp 2016.

*Fix:* use companyfacts with accession numbers, and take t and t-1 from the same 10-K. Use continuing-operations cash flow wherever revenue is continuing-operations. Flag firm-years with discontinued operations.

**2. Wrong revenue elements.**
- Manhattan Associates 2011-15: the chosen `Revenues` is a $91-135M component (true totals $330-556M), which gives GAAP margins of 68-94%.
- In 16 firm-years the chosen revenue is below 80% of another revenue element.
- IonQ's 2022 `Revenues` of $1.235B (actual about $11M) lets IonQ pass the $100M filter. iPass 2011 revenue is 0; Majesco 2018 revenue is $31K.
- In 32 firm-years growth and rev/rev_lag-1 differ by more than 1 point (Microsoft FY2016 growth is ASC 605; its margin is ASC 606).

*Fix:* take level and growth from one element, add consistency checks, and hand-audit the top 5% of scores.

**3. The sample is not "software", and a few firms drive the results.**
- The universe includes internet platforms, IT services and government contractors (Leidos, CACI, SAIC), payments (ADP, Block, Toast), gambling (Flutter) and Chinese ADRs; 16% of firm-years have foreign or blank addresses.
- 14 duplicate registrant pairs (Alphabet/Google, TripAdvisor/Liberty TripAdvisor, CSC/DXC, nCino/OpCo).
- ADR growth includes FX moves: Baidu 2022 is -8.2% in USD, -0.6% in RMB.

Frontier scores, GAAP (FCF after SBC), for 2010-15 / 2016-19 / 2020-22 / 2023-25:

| Sample | Frontier scores |
|---|---|
| Baseline | 129/93/100/89 (121/96/111/85) |
| SIC 7372 only | 73/75/62/43 (73/79/73/54) |
| Excluding 42 clearly non-software firms | 93/72/99/90 (99/80/111/86) |
| Dropping the 2 most influential firms per period | 102/76/89/56 |

In 2010-15 the frontier is set by Baidu and Meta; in 2016-19 by Hello Group and Weibo; in 2023-25 by AppLovin. Within SIC 7372 the 2023-25 frontier is 32 points (GAAP) and 24 points (FCF after SBC) below 2016-19.

*Fix:* define a core software sample (SIC 7372 plus hand classification from 10-K revenue disaggregation). Deduplicate registrants, compute growth in the reporting currency, and report leave-one-firm-out diagnostics for every frontier statistic.

**4. The scale gradient (Table 7) is largely a sample-size artifact.** A 95th-percentile maximum computed over at least 30 firm-years falls mechanically as N falls (1,882 versus 139 firm-years).
- On size-matched subsamples of 139, the frontier scores are 55/52/49/60 (GAAP) and 57/50/47/49 (FCF after SBC). The monotone decline disappears.
- P95 R is non-monotone (69/63/54/64).
- Median prior revenue doubles over the sample ($385M to $772M); condition on size across periods.

**5. The cash margin understates capital, and the capital-intensity result is one firm.**
- Missing capex is set to zero (151 firm-years, including Workday FY2019-21 and AppLovin 2025). Dropping those firm-years lowers the 2023-25 frontier from 89 to 73 (GAAP).
- Finance leases are excluded. Microsoft's FY2025 cash capex was $64.6B against about $88B including leases, so its margin is overstated by about 8 points, and firms that lease AI capacity look capital-light by construction.
- The 2023-25 capital-light frontier (83) falls to 62 without AppLovin and to 51 without Exzeo too, against 41 for the heavy half. The split is at capex of 2.1% of revenue, and Clear Secure, Grindr and Innodata, not AI-compute builders, set the heavy-half frontier.

*Fix:* add finance-lease ROU additions (operating-lease additions as a sensitivity), impute missing capex from PP&E roll-forwards, and report an unlevered version.

**6. The acquisition flag is mistimed.** Goodwill frames are 31 December instants, but 28% of firm-years have other year-ends.
- 68 of 458 flags rest on goodwill dated more than 45 days from the year-end; Microsoft is flagged in FY2023 for Activision, which closed in FY2024.
- Acquired revenue arrives mostly in t+1 (314 firm-years are unflagged right after a flagged year).
- The threshold scales price, not acquired revenue: CoreWeave 2025 is flagged; Salesforce FY2026 (Informatica, 24.5% of prior revenue) is not.

*Fix:* use ASC 805 pro forma revenue (`BusinessAcquisitionsProFormaRevenue`), flag both t and t+1, and align instants to the fiscal year-end.

**7. Measurement at the limit and the accountability floor (Sec. 6).**
- (a) "Owned compute ... never enters ... adjusted operating margin" is wrong: depreciation enters both GAAP and adjusted operating income; only EBITDA excludes it. The real issue is useful-life estimates (the 2022-23 server-life extensions).
- (b) The recommended margin (with lease-financed capacity) is not the paper's own measure.
- (c) Gross booking raises growth only during a mix shift (Block 2020: 101% growth from bitcoin booked gross).
- (d) The recurring cost is SOX 404(a)/(b) and AS 2201 audits; 302/906 assign liability.
- The central `a_min` of 7% exceeds total G&A at Microsoft (4.5%) and Oracle (3.0%); median G&A above $10B is 6.2%. The floor is mostly fixed in dollars, so it shrinks with scale, and automated controls lower testing cost.

*Fix:* calibrate `a_min` from audit fees and D&O premiums, model it as a fixed cost, and report the sensitivity of R_max.

**8. Practitioner claims.**
- Palantir Q2 2026 is verified (93% growth + 62% adjusted = 155; + 47% GAAP = 140; the gap is SBC of 13.7 points plus payroll tax). Its growth is year over year, not "annualized quarters" (Sec. 3.4). The contrast with the FY2025 annual score of 88 mixes acceleration (56% to 93% growth) with measurement; on the paper's basis Q2 2026 is about 141.
- Bessemer's Rule of X uses FCF margin with no stated SBC treatment, and its 2-3x applies "if growth is efficient," so the model's X is derived for a different margin.
- ICONIQ's 45/53/59% is verified; "75-80% of classic subscription software" is not in the report (the panel's own SIC 7372 median for 2023-25 is 73%).
- "Median fell to about 12" is GAAP on the broad universe. The pre-SBC FCF median is 25.0, and 2025 rebounded to 15.7 (GAAP; pass rate 14.2%).

## MINOR
- January-May year-ends (18% of firm-years) shift back a year (Oracle FY May 2026 is "2025").
- S&M includes ASC 340-40 amortization; use cash growth spend for alpha.
- g and m share S_t, so revenue errors inflate the fixed-effects slope; use lagged revenue.
- Negative capex (Meditech 2015-19) and SBC (Paycom 2024); iid SEs in the capital quantile regression; deflate the $100M filter; GAAP P99 was 55-80 in 2022-24.

## ERRORS
1. Data, Sec. 3.1: "202 facts fail"; the build log says 214.
2. Empirics, Sec. 4.3: GAAP frontier "93 to 129"; Table 3 gives 89 for 2023-25, so 89-129. Sec. 4.2's "25 to 45 points" should be 25-49 (Table 2).
3. Empirics, Sec. 4.7: shortfall "between 26 and 30"; `mean_ineff` for 2016-19 is 0.255, so 25-30.
4. Data, Sec. 3.2: fallback "0.2%" uses all rows as the denominator. It is 22 of 6,727 growth observations, or 13 of 3,842 in the sample (0.3%).
5. App. B: "501 frames"; `frames_extra.json` adds 51, for 552 in total.
6. Empirics, Sec. 4.3: "lambda h of about 0.15-0.25" is not in `empirics_results.json`.
7. Factual errors covered above: the depreciation claim (7a), the ICONIQ 75-80% attribution (8), leased capacity in the capex measure (5), and duplicates in the 579-firm count (3).

Verified: ten firm-years (Microsoft, Salesforce, Adobe, ServiceNow, Workday, Snowflake, Zoom, Palantir, Oracle, CoreWeave) match reported values apart from the issues above. All other numbers in `data.tex` and `empirics.tex` match the tables and the JSON.
