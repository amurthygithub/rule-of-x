# Pressure-test panel: investment management and asset owners

**Paper:** Paper 1 v1, "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation" (`notes/reviews/paper1_v1/paper1_v1.pdf`, `.txt`)
**Date:** 29 October 2026
**Panel roles:** quantitative equity researcher (QR); stewardship and engagement lead (SE); CIO of a pension or endowment allocating to PE and growth equity (CIO); fundamental risk manager (RM); technology-sector strategist (TS)
**Materials used:** the paper; `data/panel.csv` (core sample), `data/panel_v2_all.csv`, `code/estimate_organic.py`, `code/estimate_revised.py`, `notes/empirics_organic.json`, `notes/calibration_anchor_E2.json`, `notes/assumptions_register.md`; public sources listed at the end. Nothing in the paper, code or data was edited.

**Independence caveat (for Appendix E.3).** One AI agent played all five roles, on the same model family as the agents that wrote the paper. The roles were run one after another with shared test results, so they are not independent reviewers. Appendix E.7 already warns that agreement among same-model agents is weak evidence. Treat this as a structured self-critique that a human panel should confirm. Every numerical claim below comes from a script that was run (Appendix A of this note) or from a source that was opened.

---

## 0. Verdict

**Useful, but not yet safe to hand to practitioners in its present form.** The theory gives investors three things they can use: (i) the split between the screening weight and the decision weight (Lemma 1 and Proposition 6); (ii) the rule for charging acquired growth (Proposition 14 and Remark 3); (iii) the measurement checklist in Section 8.3. One descriptive fact survives every test we ran: the 95th percentile of the score fell between 2016-19 and 2023-25. Four of the claims the abstract leads with are weaker than stated:

1. **Backfill.** About 100 pre-IPO comparative years are backfilled into the "as first reported" panel, and they sit almost entirely in the earlier periods. They account for about 3 of the 15 points in the cash-basis decline.
2. **Capital intensity.** Finding (iv) is mostly the accounting identity that the cash score deducts capital spending. On the organic frontier it does not survive sorting on the prior year's capital intensity.
3. **The weight on growth of 7 to 13.** This figure is a lagged sales-efficiency ratio divided by an unidentified alpha. It moves against valuation multiples: lowest in 2021, highest in 2023-25.
4. **The horizon ranges and the execution pace.** These rest on an anchor of 20 firm-years from 12 firms, which includes a captive related-party revenue firm and an unflagged acquirer. Their execution parameters are mostly class-d scenario values.

The E1-versus-E2 contrasts behind three "changed conclusions" (Appendix E.2) do not survive a familywise correction, or a bootstrap interval of a different type.

| Role | Usefulness for practice | Main methodological concern | Recommendation |
|---|---|---|---|
| QR | Medium: Lemma 1 and Proposition 13 suggest factor variants; E2 changes who is in the top bucket | Backfill; non-stationary slope; multiple testing; no return or holdout evidence | Major revision of Section 5 inference; add holdout and screen tests |
| SE | High: metric spec, pay design, AI-programme questions | Engagement-grade numbers must be robust: only the P95 decline is | Add a "how to use" box; cite 12 points, not 15 |
| CIO | Medium-high: acquired-growth charging, execution as the driver of pace | Anchor and execution parameters too thin to underwrite with; sample excludes growth-equity targets | Restate the pace as illustrative; state the coverage limits |
| RM | Medium: Section 8.3 red flags, Proposition 10 common-mode risk | Parameter risk (compute share), tail sample, regime shift, flag false negatives | Report parameter-uncertainty bands and annual series |
| TS | Medium: "neither 100 nor 1000" framing, free-entry result | Pooled 2023-25 hides a 2025 rebound; public-only sample misses AI-native firms; compute share treated as exogenous | Annual series; co-headline the high-compute case |

---

## 1. Tests the panel ran

Each test ran on the shipped data. Code is in Appendix A. "E2 proxy" is the exclusion-only organic sample (`acq_flag == 0` and no unverified hypergrowth), which reproduces the paper's E2 anchor closely (P95 cut-off 0.4366 against 0.4361; median growth 11.9% against 12.0%).

| # | Claim tested (paper location) | Result | Bearing on the claim |
|---|---|---|---|
| T1 | "SEC filings as first reported" (Abstract; Section 4.1; Appendix D) | 141 core firm-years (7.3%) come from a filing later than the year's normal 10-K. 138 of them are the registrant's first panel year: 40 of the 76 fiscal-2010 firm-years (XBRL phase-in) and about 100 pre-IPO comparative years from a first 10-K (for example Datadog FY2018, ZoomInfo FY2019, Roblox FY2020, Marqeta FY2020). These backfilled years grew at a median 33.7% against 16.4% in 2016-19. They are 9% of the 2016-19 GAAP top 5% and 0% of the 2023-25 top 5%. | The label is not accurate for these years, and the bias is **asymmetric** across the two periods being compared |
| T2 | P95 fell 12 to 15 points, 2016-19 to 2023-25 (Section 5.2, Table 4) | Without late-source years: GAAP -11.5 [-20.6, -5.3]; cash -12.0 [-20.3, -2.9] (baseline -15.2). The fall holds among the 88 stayers (GAAP -11.1 [-21.1, -5.1]; cash -16.7 [-29.5, -8.9]) and with a constant-real $100M threshold (-11.4 and -13.7) | **Survives**; the cash headline should be about 12 |
| T3 | Stability of the decline and of the slope (Sections 5.2, 5.3) | Annual GAAP P95: 2016-22 range 50 to 63; 2023: 42.8; 2024: 41.5; **2025: 54.6**. 2016-19 to fiscal 2025 alone: GAAP -1.3 [-16.2, +10.9]. Upper-decile GAAP slope in rolling three-year windows: about -0.25 through 2016, then -0.74 to -0.83 from 2018 | The decline is a 2023-24 trough, partly reversed in 2025. The slope has two regimes, so "about half a point" is their average, not a stable parameter |
| T4 | Capital-intensity gap, finding (iv) (Section 5.6) | E2 proxy, 2023-25: same-year sort -10.9 [-19.2, -2.6]; capital spending added back -2.6 [-14.3, +7.6]; **prior-year sort -2.9 [-13.1, +0.8]** | Mostly mechanical. Not robust on the estimand the paper calls primary |
| T5 | Calibration anchor (Section 7.3, Table 11, 2025 row) | 20 firm-years from **12 firms**; 6 firms supply 14. Firm-cluster bootstrap: median intercept 44.6 [34.1, 52.3]; **upper-quartile intercept 52.4 [42.0, 63.7]**; median surplus -0.9 [-15.7, +16.5]. The top anchor, Exzeo 2025 (score 106, no S&M line), gets "substantially all" of its revenue from affiliates of its controlling stockholder. Xunlei 2025 (+42.5%) acquired Hupu that year but is not flagged | The upper ends of every horizon range carry about ±10 points of sampling error that is not reported, plus two contaminated observations |
| T6 | Weight on growth of 7 to 13 (Abstract; Section 5.4; Section 8.1) | Median ratio by period: 3.11, 2.84, 2.98, **4.21** (2023-25); by year, **2.28 in 2021** and 5.11 in 2023. Median cloud software EV/NTM revenue was 19.8x in February 2021 and 6.1x at the end of 2024. Fixing G at 8% to 15% gives a ratio of 2.50 to 3.23 | The ratio moves **against** the marginal value of revenue; it behaves like a sticky-spend sales-efficiency ratio |
| T7 | Out-of-sample content of the durable and transient split (Sections 3.4, 7.3) | Next-year change in the cash score, trained on 2011-18 and tested on 2019-24: out-of-sample R^2 is 0.153 on the score, 0.180 adding the surplus, **0.182 on growth and margin separately**, and 0.177 adding the surplus to that | The split predicts reversion, but adds nothing beyond "growth reverts faster than margin" |
| T8 | Inference on E1-minus-E2 contrasts (Sections 5.3, 5.5; Table 2) | GAAP slope difference 0.13 (SE 0.09): percentile interval [0.02, 0.33]; basic interval [-0.07, 0.23]. Cash size-gradient difference -3.0 (SE 2.4): percentile [-8.1, -0.4]; basic [-5.6, +2.1] | "Excludes zero" depends on the interval type; with t = 1.4 and 1.3 these are not established |
| T9 | Multiple testing across the six findings (Section 5.10) | 14 claimed contrasts, Holm-adjusted. Survivors: cash slope against -1 (t = 4.9), the S&M component of the fast-band gap (t = 5.4), and the E1 capital-intensity gap (t = 2.9, Holm p = 0.04). All four P95-change tests have Holm p of 0.12 to 0.21 (BH 0.03 to 0.05). Only the two t > 4.9 results clear the t > 3 hurdle of Harvey, Liu and Zhu (2016) | The headline decline is credible as one pre-specified test, not as one of a family |
| T10 | Does E1 versus E2 matter for screens? (Section 4.4) | Share of the E1 top 5% by cash score that is acquisition-affected: 46%, 30%, 46%, 35% by period; top quintile 21% to 43%. E2 assigns an organic growth rate to only 59 of 469 affected firm-years (12.6%) | Large effect on **membership**, small effect on aggregate statistics. As defined, E2 cannot be implemented in a screen |

---

## 2. Role reports

### 2.1 Quantitative equity researcher (factor and screening design)

**1. Usefulness**

- **Is "Rule of X as a price line" actionable?** Partly, and indirectly. The price-line reading (Proposition 2(d): choosing X is choosing a frontier point) is a statement about **operating choices**, not about returns. Two derived results are usable in factor design:
  - Lemma 1 makes the screening weight a duration-scaled margin, so the weight on growth should fall when discount rates rise or growth persistence falls. A rate-conditional X is a testable factor variant that no practitioner screen uses today.
  - Proposition 13(b) and (d) give an economic-margin score, `e + (X - k) g`, for capital-heavy names such as CoreWeave, where the cash Rule of 40 is uninformative (cash score 14 against a GAAP score of 167; Section 4.5).

  The paper contains no return test. The only return evidence is Lee (2024): the Rule of 40 "adds value and delivers a moderately high Sharpe ratio" on 1,756 SaaS firms, 2003-22. Section 8 should say plainly that nothing in this paper bears on expected returns.
- **Would E1/E2 change factor construction?** Yes for membership, no for aggregates (T10). Between a fifth and a half of the top bucket of an observed-score screen is acquisition-affected, so a screen built on reported growth is substantially a roll-up screen. But E2 *excludes* most affected firm-years rather than measuring them, and a factor cannot drop a quarter of its universe. The implementable version is Remark 3: charge acquisition outlays as an annuity, with the fully charged score as a bound. The paper should present Remark 3 as the screening estimand and E2 as the research estimand.
- **Signal persistence and turnover.** Mean year-to-year rank autocorrelation is 0.67 for the cash score, 0.65 at X = 3 and 0.83 for margin alone. Annual turnover of the top quintile is 45% for the cash score, 53% at X = 3 and 28% for margin. Higher X means more turnover, consistent with T7: growth is the transient part. The paper's split amounts, in factor terms, to the Chan, Karceski and Lakonishok (2003) result that growth rates have little persistence.

**2. Methodological challenges**

- **Look-ahead and first-reported data.** See T1. The construction in Appendix D, "the earliest-filed annual report containing an annual revenue fact", is correct for registrants already filing, but it *backfills*:
  - the pre-IPO year that a first 10-K reports as a comparative;
  - fiscal 2010 for registrants not yet filing XBRL.

  These years could not have been screened in real time. They are selected on a later event (the IPO), and IPO firms' operating performance peaks around the listing (Jain and Kini, 1994; Pastor, Taylor and Veronesi, 2009). This is the backfill bias known from Compustat (Banz and Breen, 1986; Kothari, Shanken and Sloan, 1995). It matters here because the comparison window is asymmetric: firms that will list in 2027 cannot yet contribute 2025 comparatives.

  Two smaller issues: the panel has no filing-date column, so no point-in-time backtest can be built from it; and SIC codes are current, not historical (Section 8.6), which is a look-ahead in classification.
- **Survivorship.** The design passes. The universe includes inactive registrants: 41.7% of 2016-19 firms are last seen by 2022, including 9 of the 26 top-decile cash-score firms. The decline also holds among the 88 stayers (T2). The material selection problem is backfill, not survivorship.
- **Sample size of the tails.** Each period's top 5% has 23 to 26 firm-years from 15 to 17 firms. The anchor has 20 firm-years from 12 firms (T5), and leaving one firm out moves the median upper-bound surplus between -7.4 and +2.8 points. T(40%) rests on 18 firm-years (E1) and 12 (E2), as Section 5.2 says. The firm-level IQRs in Table 11 are quoted as if they were 20 independent draws; their own sampling error is not reported.
- **Stability over time.** See T3. Two consequences follow:
  - "A point of growth has come with about half a point less margin" pools a -0.25 regime (to 2016) with a -0.8 regime (from 2018). That is a structural break, not a parameter.
  - The 2023-25 trough is two years deep. Fiscal 2025's GAAP P95 of 54.6 is back inside the 2016-19 range on E1, though only to 47 on the E2 proxy.
- **Multiple-testing burden.** See T9. Beyond the six findings there are two bases, two estimands, three flag thresholds, four periods and three sub-samples (Table 2 alone has over 30 contrasts). The primary estimand was switched after the robustness results were seen (Appendix E.2; disclosed, which is to the paper's credit). The capital-intensity finding was reported for the one period of four in which it is significant ("since 2023"). Under Holm across the 14 claimed contrasts, the P95 decline is not significant (adjusted p 0.12 to 0.21), although it is the one pre-specified question the paper started with. Pre-registering it as the single confirmatory test would let it stand at t = 2.1 to 2.5. The difference between a significant E1 estimate and a non-significant E2 estimate is not itself evidence (Gelman and Stern, 2006). Sections 5.5 and 5.10 lean on exactly that comparison ("the gradient disappears").
- **Out-of-sample relevance.** The paper reports no holdout. T7 provides one. The surplus Π predicts next-year reversion out of sample (R^2 rises from 0.153 to 0.180), but splitting the score into growth and margin does as well (0.182). The model-specific decomposition earns its place as interpretation, not as a signal.

**3. Grounding.** Three assumptions are loose:
- **Alpha.** The register classifies α ∈ [0.25, 0.45] as class c, "calibrated from our own data (S&M ratio 3.3)". The ratio identifies α(X - k), not α (Section 5.4 says so), and the same 3.3 is then divided by α to get X = 7 to 13. This is circular. The register should mark α as class d. The only external order of magnitude is the advertising-elasticity literature: a mean short-run elasticity of 0.12 (Sethuraman, Tellis and Briesch, 2011), a different object but at or below the paper's lower bound.
- **Market growth.** G is set to the cross-sectional median firm growth rate, with no precedent. A fixed G of 8% to 15% moves the ratio to 2.50 to 3.23.
- **The anchor.** Treating realised margins of firms selected on the outcome as their intercepts is a winner's-curse construction. Firms in the top 5% fall from a median score of 72 to 54 the next year and 38 the year after.

**4. Misuse.** "Half a point" will be quoted as a structural trade-off in factor tilts and in "efficient growth" scoring models. The surplus will be marketed as a model-derived "transience" signal when it is, to first order, excess growth (T7).

### 2.2 Stewardship and engagement lead

**1. Usefulness**

- **Metric specification for engagement letters.** Section 8.3 and the conclusion give a defensible standard: annual FCF after SBC and after capital spending including capitalised software; organic growth on a constant perimeter; acquired growth charged at its price; gross profit per dollar of compute; economic profit for capital-heavy builds (Proposition 13). This is the most directly usable output for stewardship teams.
- **Pay design.** The Rule of 40 is already in pay plans. LiveRamp's CEO PSUs weight it at 70%, with relative TSR at 30% (DEFA14A, 2024). The paper implies three things for such plans. First, a fixed threshold rewards under-investment when the decision weight exceeds one (Section 8.1). Second, an adjusted-margin definition credits SBC. Third, reported growth credits acquisitions at weight one whatever their price (Proposition 14(a)). Stewards can ask plans to use the cash-after-SBC basis and organic growth, charge acquisitions, and measure over several years so that a transient surplus is not paid out.
- **Engagement on AI strategy.** Section 3.10 and Section 7.4 turn "what is your AI strategy?" into answerable questions:
  - how many employees' work changes each year;
  - what share of pilots reach production, and how long embedding takes;
  - how sponsorship survives a leadership change;
  - how many AI applications are in ICFR scope, and whether control layers share one model (Proposition 10's common-mode floor).

  The finding that **pace, not technology, separates central from fast execution** (Section 8.2) points engagement at governance and change capacity. A board-level issue that stewards can actually influence.
- **E1/E2 in engagement.** Bending Spoons (Section 6) is the case to cite: a reported score of about 160 against about 37 on the company's own organic measure. Ask every serial acquirer to disclose organic growth on a stated definition each period.

**2. Methodological challenges (what is safe to cite).**
- **Safe to cite:** the P95 decline of about 12 points (T2), and the measurement distortions in Section 8.3, which are accounting, not estimation.
- **Not safe to cite:**
  - the capital-intensity penalty (T4);
  - "growth is worth 7 to 13 times margin" (T6);
  - "acquired growth flattens the trade-off" (T8);
  - any horizon range, because Table 11 rests on 12 firms (T5).

  Engagement letters that quote these will be rebutted by any company IR team with a quant.
- **Look-ahead and survivorship** do not change the safe-to-cite list except to lower 15 to 12.
- **Stability:** a 2025 rebound (T3) means "software scores have structurally fallen" is a weaker engagement premise than the abstract suggests.

**3. Grounding.** The execution parameters behind "23% embedded by 2036 and all of it by 2033" are a mix of classes:
- surveys of a different construct: the 0.54 is the share of AI pilots reaching production, not the probability that a process migration embeds with realised savings;
- an analogy: change capacity of 10% a year is grounded on JOLTS layoff rates, but layoffs are not a capacity to change work;
- class-d values: programme size of 48 processes, embedding times, the 0.6 keep probability ("Not found; d" in the register), and the disruption rates.

The paper says this in Section 7.3, but the abstract does not. Under the author's own rule this is the loosest block in the paper.

**4. Misuse.** Management teams will use three sentences against stewards:
1. "A fixed threshold ... marks down firms whose growth spending earns more than it costs" (Section 8.1), to deflect pressure on cash burn.
2. "A screen that reads the dip as weakness penalizes firms that are executing" (Section 8.2), to excuse underperformance as "transitions in flight".
3. The decision weight of 7 to 13, to justify S&M intensity.

Each needs a guardrail sentence (Section 4 below).

### 2.3 CIO, pension or endowment (PE and growth-equity allocation)

**1. Usefulness**

- **Underwriting AI value creation in a hold period.** The execution result is the most decision-relevant output for a PE allocator. Read through Table 11:
  - Central execution embeds 2.5% of the programme by 2028 and 10% by 2031.
  - The intercept therefore moves about 2 points over a typical 2026-31 hold (10% of the 22-point gap between the lower anchor quartile and the central full-cost term).
  - Fast execution embeds 30% and 73%, worth about 5 and 12 points at the upper end.

  The entire spread is execution, not technology. The decisive sentence is buried in Section 7.3: "Under central execution, embedded gains first exceed that dip after about 9 years." Under central execution, then, a four-to-six-year hold exits before the programme pays back on the cash score. The exit buyer must capitalise the in-flight programme, a parameter (h_x) that the register says has no precedent. GPs who underwrite AI margin expansion are implicitly assuming fast execution. LPs should ask for evidence of the fast-case inputs: pilot-to-production rates, change capacity, sponsor continuity.
- **Ownership.** Remark 2 and Section 7.3 ("Ownership") imply private ownership mainly speeds the pace. A public firm held to a guided dip of one point embeds 8% by 2036 against 23%. This supports the take-private-for-transformation thesis. The paper also says a sponsor's faster decisions "change nothing" when change capacity binds. That undercuts a common GP claim that faster governance accelerates AI value creation. Both statements rest on scenario values.
- **Buy-and-build.** Proposition 14 and Remark 3 are directly usable in LP reporting:
  - At X = 1, any purchase above 1x revenue lowers the properly charged Rule of 40.
  - A base with NRR below 100% must keep buying to stand still (Proposition 14(f)).

  Ask GPs to report organic and charged scores for platform companies, with the annuity life stated.
- **Coverage.** The analysis sample needs prior-year revenue of at least $100M and SEC registration (Sections 4.1 and 8.6). Most growth-equity targets are below that, and the fastest AI-native firms are private. **The frontier in Section 5 is not a benchmark for growth-equity targets**, and the paper should say so in one sentence in Section 8.6.

**2. Methodological challenges (allocator angle)**
- **Backfill** (T1) matters most to this reader. The backfilled pre-IPO years are VC- and PE-owned years selected on a successful exit, so the "frontier" in 2016-22 partly reflects the private-to-public pipeline. Benchmarking a private portfolio company against it double-counts exit selection.
- **Durable against transient** is exactly the exit-underwriting question: will the buyer pay for the score you are selling? T7 says the split predicts reversion but no better than growth and margin separately. The practical rule "pay for margin, haircut growth" is as good.
- **Anchor sampling error** (T5) is about ±10 points on the upper-quartile intercept. That is the size of a typical value-creation plan's margin bridge.
- **Stability:** the post-2022 trough coincides with the rate shock. Table 4 shows P95 unchanged from 2016-19 to 2020-22 and then a fall of 12. A cyclical reading is as consistent with the data as the structural reading in Section 7.4.

**3. Grounding.** Loose for this use:
- the execution block (see 2.2);
- the annuity life T_life = -1/ln NRR for the Bending Spoons case (a scenario, as Section 6 says);
- h_x (no precedent);
- the demand-pull multiplier µ of 1 to 2 for 2028 (class d), which alone raises the 2028 transient part from about 16 to 57 points, so the 134-point upper end would be about 93 at µ = 1.

**4. Misuse.** GP pitch decks are the highest-risk channel:
- "Rule of 156 attainable by 2028" from Table 11 or the abstract, without the durable part (27 to 98) or the "not forecasts" caveat;
- "our portfolio sits on the efficient frontier", whereas Proposition 7(iv) says the cross-section identifies no firm's frontier;
- "fast execution" as a base case;
- roll-up sponsors choosing the annuity convention with a long life. The paper itself shows the annuity can *raise* the score of an acquirer paying 1.7 to 3.2 times revenue (Section 6, "the charging convention, not the data, decides the sign").

### 2.4 Fundamental risk manager

**1. Usefulness**
- Section 8.3's four distortions (SBC add-backs, capitalised compute, gross revenue, run-rate revenue) and the acquired-growth charge form a ready-made red-flag list for credit and equity underwriting.
- Proposition 10's common-mode term is a clean statement of model-provider concentration risk in controls. Operational risk teams can use it as stated: depth of controls addresses independent failures; only diversity of types addresses common-mode ones.
- The ceiling results (Table 10) are useful as **sanity bounds** on management targets, provided the compute share is treated as the dominant unknown, as the paper says.

**2. Methodological challenges**
- **Parameter risk.** The full-automation threshold ranges from 26% to 72% over the credible compute share (Section 7.2), against 32% to 59% across all other cases combined. The central compute share of 20% is below the only measured analog: cost of revenue of AI products, 41% to 55% implied by ICONIQ's 45% to 59% gross margins. The high-compute case (40%, threshold 59%) is the observed-analog case, and it should share the headline.
- **Tail and data quality.** Two contaminated anchor firm-years (T5). Exzeo's revenue is captive: its 10-K says it "did not generate meaningful revenue from Non-HCI affiliated customers in fiscal year 2025". Xunlei acquired Hupu in 2025 without triggering the flag, which shows the flag has **false negatives**: acquisitions paid in stock, or below the cash, goodwill and pro forma thresholds, pass as organic. In the core sample, US-GAAP foreign private issuers' dollar growth includes FX (Section 4.1).
- **Regime risk.** The slope break around 2017-18 and the 2023-24 trough (T3) mean any risk model calibrated on the pooled 2010-25 parameters is mis-specified for at least one regime.
- **Inference.** Percentile intervals on medians and quantile-regression slopes are biased when the bootstrap distribution is skewed (T8). BCa or basic intervals should be reported for every contrast that the text calls significant.

**3. Grounding.** The ceiling holds output prices fixed while compute costs fall (Corollary 4; Section 7.2 says the thresholds rise if costs are passed through). For a risk manager this is the wrong default: Lemma 3 and Proposition 8 say pass-through is the competitive outcome. The pass-through case should get a row in Table 10.

**4. Misuse.** "Durable score" will migrate into credit memos as if it were a measured quantity. It is the residual of an inversion that swings by 19 points depending on whether S&M buys growth (Section 7.3).

### 2.5 Technology-sector strategist

**1. Usefulness**
- The answer "neither 100 nor 1000 as a steady state" (Section 9) is well framed and well defended. The free-entry result (Proposition 8: under free replication the limit is set by what stays scarce) is the right strategic message for AI-era software. So are the stage-ordering of levers (Corollary 3: growth engine and retention for fast growers, overhead for mature firms).
- Section 5.8's decomposition is a useful map of where the best fast growers win: S&M efficiency, 28 of 40 points in the 40% to 60% band. The paper correctly calls it descriptive.

**2. Methodological challenges**
- **The 2023-25 pool hides the AI cycle.** Fiscal 2025 shows a GAAP P95 of 54.6 (T3), led by Exzeo, Palantir (GAAP score 88) and several acquisition-affected names (CoreWeave, Gen Digital, Clearwater). A strategist wants the annual series, and fiscal 2025 shown separately, before accepting "fast growers became scarcer" as a durable state.
- **Public-only sample.** The firms that define the AI frontier in 2025-26 are private (Section 8.6). The paper's frontier is a frontier of public incumbents in a transition.
- **Endogenous compute share.** The compute share depends on pricing model: usage-based pricing passes compute through, seat pricing absorbs it, and outcome pricing shares it. Treating cc as an exogenous scenario value misses the strategic choice that sets it. Section 7.4 lever 4 gestures at this.
- **A hypothesis for the slope break, to test.** The GAAP slope steepened after 2017 more than the cash slope did. That is consistent with upfront billing (deferred revenue) flattering the cash margins of fast growers in the 2019-21 IPO cohort. Checking it is a one-regression addition (control for the change in deferred revenue).

**3. Grounding.**
- The G paths (5% to 30% by 2036) and the 42% market-growth threshold need a precedent for how long software categories sustain such growth. The paper's own sample has only 18 firm-years growing at least 40% in 2023-25.
- Free entry only at date 0 (Assumption 6) is a strong simplification for software, where entry is continuous. The paper flags it.

**4. Misuse.** "Rule of 1000" and "Rule of 60" headlines will be lifted into AI-thematic marketing. The paper's own sentence, "a Rule of 1000 can be sustained only briefly", should not be paraphrased as "a Rule of 1000 is attainable".

---

## 3. Assumptions the panel considers loose against the "solid precedent" rule

| Assumption | Where used | Register class | Problem | Fix |
|---|---|---|---|---|
| α ∈ [0.25, 0.45] | Section 3.1, 5.4, 7; weights 7-13; Rule-of-1000 pull; Table 11 Π scaling | c ("S&M ratio 3.3") | Circular: the ratio identifies α(X - k), not α. No external precedent cited | Reclassify as d; cite the advertising-elasticity literature as the only order-of-magnitude anchor; report results at α = 0.15 |
| G = year median of firm growth | Spend ratio; anchor G = 12.0% | not listed | No precedent for median firm growth as market growth; ratio 2.50-3.64 across reasonable choices | Use an external software-spending growth series as the main case; median as robustness |
| S&M share as upper bound on growth spend | Spend ratio; anchor σ_ub | implicit | 19-point swing in intercepts; part of S&M serves the existing base | Use disclosed new-versus-existing splits where firms report them, or survey splits, as a precedent |
| Anchor = realised margins of the top 5% | Section 7.3, Table 11 | c | Winner's curse: the top 5% fall from 72 to 54 the next year; 12 firms; two contaminated observations | Two-year averages; firm-cluster bootstrap; drop captive and unflagged-acquirer firm-years |
| Success probability 0.54 (central), 0.80 (fast) | Section 7.3, execution | a (survey) | Construct mismatch: pilot-to-production rate, and a survey of transformations "meeting six conditions" (survivor-selected) | Map explicitly to the model object; widen the range; tornado |
| Change capacity 10% of employees a year | Section 7.3 | b (JOLTS layoffs) | Layoffs are not a capacity to change work | Keep as d with the JOLTS figure as an upper reference |
| Programme size, embedding times, keep probability, disruption rates | Section 7.3, abstract pace | d | Abstract quotes "23% by 2036, all by 2033" without class-d labelling | Remove from the abstract or give the full range including slow execution (<1%) |
| Compute share 20% central | Table 10, abstract threshold of 42% | d | Below the only measured analog (AI-product cost of revenue 41-55%) | Co-headline the 40% case (threshold 59%) |
| Prices fixed in the ceiling | Corollary 4; Table 10 | modelling choice | Competitive pass-through is the paper's own long-run case | Add a pass-through row |
| µ demand-pull multiplier 1-2 (2028) | Table 11 | d | Raises the 2028 transient part from about 16 to 57 points; the 134-point upper end is about 93 at µ = 1 | Show Table 11 with µ = 1 as the main case |
| T_life = -1/ln NRR | Section 6, Table 9 | d | Long life makes the annuity favourable to acquirers | Report at 5 and 10 years alongside |

Well grounded, and the panel has no objection: the tax law (ψ, Remark 1), NIST post-quantum dates, SOX 404 and PCAOB AS 2201 requirements, the Damodaran cost of capital, the XBRL extraction and duplicate handling, and the accountability-floor arithmetic of Remark 10.

---

## 4. Misuse risk: marketing materials and manager pitches

| Quotable line (location) | Likely misuse | Guardrail text to add |
|---|---|---|
| "growth spending implies a weight on growth of 7 to 13" (Abstract; Section 5.4) | Justify cash burn or S&M intensity: "academic research shows growth is worth 7 to 13 times margin" | "This ratio describes what firms spend, not what is value-maximising. It depends on an unidentified elasticity, and it rose when valuation multiples fell." |
| "maximal scores of roughly 40 to 156 in 2028" (Abstract; Section 7.3) | "Rule of 150 by 2028" in AI-themed fund decks | "Scenario bounds, not forecasts; the durable part is 27 to 98; the upper end needs a doubling of demand pull and growth above 100%." Never quote upper ends alone |
| "embeds ... all of it by 2033 under fast execution" (Abstract) | GP value-creation plans assume fast execution | "Under central execution, embedded gains first exceed the cost of transitions in flight after about nine years." |
| "A fixed threshold ... marks down firms whose growth spending earns more than it costs" (Section 8.1) | Management deflects investor pressure | "...provided the firm can show that its growth spending earns more than it costs; the score cannot show this." |
| "a screen that reads the dip as weakness penalizes firms that are executing" (Section 8.2) | "We are in the dip" as an excuse | "A dip is evidence of execution only with disclosed programme milestones; in our scenarios it is 3 to 4 points." |
| "efficient frontier" (title and throughout) | "Our portfolio companies sit on the efficient frontier" | Repeat Proposition 7(iv) in Section 9: "No firm's position relative to its own frontier can be read from the cross-section." |
| Annuity-charged acquirer score (Section 6) | Roll-up sponsors report the annuity score with a long life | "Report fully charged, annuity at stated lives, and uncharged scores together." |
| Bending Spoons -24.8 (Section 6) | Short-seller headline | "A lower bound that sets a full year's outlay against part of the growth it bought; not an estimate." |
| Organic frontier (E2) | Companies define "organic" favourably | "Organic growth here is constant-perimeter growth from ASC 805 pro forma disclosures; company-defined organic growth is not comparable." |

Licence note: CC BY-NC-ND 4.0 and PolyForm Noncommercial reduce misuse through derivative charts. They also prevent legitimate commercial uptake, such as index providers or manager research using the code, without written permission. The author should decide whether that is intended and say so in the README.

---

## 5. Consolidated top 10 changes

**1. Remove backfill from "as first reported" and restate the decline (Sections 4.1 and 5.2; Abstract; Table 14).**
- *Analysis:* add `filed` (filing date) and `backfill` (fiscal year sourced from a later filing) columns to the panel. Add a Table 14 row, "Excluding fiscal years not first reported (138 firm-years)": GAAP 56 to 44, change -11.5; cash 57 to 45, change -12.0.
- *Section 4.1, add:* "Fiscal years that precede a registrant's first XBRL annual report are not first reported: fiscal 2010 for registrants not yet filing XBRL (40 firm-years) and pre-IPO years reported as comparatives in a first Form 10-K (about 100). They are selected on a later listing, so we flag them and exclude them from statements about change over time."
- *Abstract:* "...the top of the distribution of reported scores fell by about 12 points between 2016-19 and 2023-25 on both bases, concentrated in 2023 and 2024, as fast growers became scarcer."

**2. Report the annual series and the slope break (Sections 5.2, 5.3, 5.10; new figure).**
- *Analysis:* annual P95 with firm-cluster intervals, and rolling three-year upper-decile slopes for E1 and E2.
- *Section 5.2, add:* "The decline is concentrated in fiscal 2023 and 2024 (GAAP 95th percentiles of 43 and 42). In fiscal 2025 the GAAP percentile returned to 55, within the 2016-19 range (change -1 point, 90% interval -16 to +11), largely through acquisition-affected firm-years; on the organic frontier it reached 47."
- *Section 5.3, replace* "On the organic frontier, then, a point of growth has come with about half a point less margin" *with:* "The upper-tail slope is not stable: about -0.25 in three-year windows to 2016 and -0.75 to -0.83 from 2018. The pooled value, about half a point, averages two regimes."

**3. Adopt a confirmatory family and fix the interval type (Sections 5.1, 5.3, 5.5, 5.10; Table 2).**
- *Analysis:* designate the P95 change (GAAP, E1) as the single pre-specified confirmatory test. Report Holm-adjusted p-values for the other contrasts, and BCa or basic bootstrap intervals for every contrast called significant.
- *Section 5.3, replace* "Acquired growth flattens the GAAP slope: the paired 90% interval ... excludes zero" *with:* "Acquired growth may flatten the GAAP slope: the difference is 0.13 (standard error 0.09); a percentile interval excludes zero but a basic bootstrap interval (-0.07 to 0.23) does not, so we do not treat it as established."
- *Section 5.5, replace* "so the cash-basis gradient in observed scores reflects acquired growth rather than saturation" *with:* "the difference between the estimands, -3.0 points (standard error 2.4), is not significant, so the data do not say whether acquired growth or saturation produces the observed gradient."
- *Appendix E.2:* restate the three "changed conclusions" accordingly.

**4. Demote finding (iv) to an identity (Section 5.6; Section 5.10; Abstract; Section 7.4 lever 3).**
- *Analysis:* add the prior-year sort and the add-back.
- *Text:* "Sorting on the previous year's capital intensity, which the current cash margin does not contain, the organic-frontier gap is -3 points (90% interval -13 to +1), and adding capital spending back removes the gap under either sort. The cash-basis gap restates that the cash score deducts capital spending, the k g term of equation (2); it does not test the model."
- Remove it from the abstract and the list of six findings.

**5. Repair and bound the anchor (Section 7.3; Table 11).**
- *Analysis:*
  - list the 20 firm-years (12 firms);
  - drop Exzeo 2025 (captive related-party revenue) and Xunlei 2025 (acquired Hupu, unflagged);
  - use two-year average margins;
  - report firm-cluster bootstrap intervals for the anchor quartiles and carry them into Table 11.
- *Text:* "The anchor rests on 20 firm-years from 12 firms. Its upper-quartile intercept of 52 points has a firm-cluster bootstrap 90% interval of 42 to 64, and every upper end of Table 11 inherits that uncertainty."

**6. Reinterpret the spend ratio and bound the weight without α (Abstract; Sections 3.6 Implication, 5.4, 8.1).**
- *Analysis:* the ratio by period and year, set against public software multiples; sensitivity to G.
- *Section 5.4, add:* "The ratio is the reciprocal of a sales-efficiency measure on excess growth. It was lowest in 2021 (2.3), when the median cloud software multiple was near 20 times forward revenue, and highest in 2023-25 (4.2), when it was near 6. A weight equal to the marginal value of revenue would have moved the other way, so we read the ratio as revealed spend intensity."
- *Abstract, replace* "growth spending implies a weight on growth of 7 to 13" *with:* "the growth spending of organic growers exceeds 3 points of revenue per point of excess growth, which, for any spend elasticity below one, implies a weight on growth above the screening weights of two to three."
- Reclassify α as class d in the register.

**7. Add a holdout and a screen test, and say what the paper does not show about returns (new Section 5.11; Section 8).**
- *Analysis:* T7 (out-of-sample R^2 0.153 / 0.180 / 0.182 / 0.177); turnover and rank persistence; T10 (acquisition-affected share of the top bucket); a screen on the charged score of Remark 3 as the implementable organic estimand.
- *Text:* "The durable and transient split predicts next-year reversion out of sample, but no better than growth and margin entered separately. This paper contains no test of returns; Lee (2024) is the only evidence that the Rule of 40 predicts them."

**8. Discipline the scenario headlines (Abstract; Sections 1, 7.2, 7.3, 9).**
- Quote every horizon range with its durable part, and never quote an upper end alone.
- Co-headline the high-compute threshold: "about 42% a year if compute absorbs 20% of revenue, and 59% if it stays near the cost of revenue of AI products today".
- Replace the execution-pace sentence in the abstract with: "under illustrative execution assumptions, the share of an automation programme embedded by 2036 ranges from under 1% to all of it, and the difference lies in success rates and sponsorship, not technology".
- Add a tornado of the expected share embedded by 2036 over the class-d parameters.
- Add a price pass-through row to Table 10.

**9. Bring the assumptions register into line with the author's rule (assumptions register; Section 7 opening; Appendix E.4).**
- Add a column "precedent measures the model's object: yes / partial / no".
- Reclassify α (c to d) and change capacity (b to d, with JOLTS as a reference).
- Mark the success probabilities as "partial" (pilot-to-production is not process embedding).
- List G-as-median-growth and S&M-as-growth-spend as assumptions.
- State in Section 7: "The headline thresholds and horizon ranges rest on the following class-d values: ..."

**10. Add a practitioner box and coverage limits (new box in Section 8; Section 8.6).**
- *Box title:* "Using these results in practice". Content:
  1. compute the cash Rule of 40 after SBC and capital spending including capitalised software;
  2. report organic growth on a stated definition, and charge acquired growth with fully charged, annuity and uncharged scores shown together;
  3. use the Rule of 40 to screen firms, not to set pay or spending thresholds; if used in pay, use multi-year organic cash scores;
  4. do not read a firm's position relative to its own frontier from the cross-section;
  5. the weight-on-growth figures describe spending, not value;
  6. horizon ranges are scenario bounds, not forecasts.
- *Section 8.6, add:* "The analysis sample requires $100 million of prior-year revenue and SEC registration, so it excludes most growth-equity targets and the private AI-native firms that set the frontier at high growth. It should not be used to benchmark them."

**For Appendix E.3 (to complete the placeholder):** "Practitioner panel, investment management and asset owners: five roles played in sequence by one AI agent on the same model family as the authoring agents, with access to the data and code; not independent. Findings: T1-T10 of `notes/reviews/paper1_v1/panel_investment_management.md`. Changes made: [author to record]. Declined: [author to record, with reasons]."

---

## Appendix A. Reproduction code

Run with `python3 -I panel_checks.py` from any directory (reads only `data/panel.csv`). Outputs match Section 1 (bootstrap draws: 300 to 1,000; seeds fixed).

```python
import json, numpy as np, pandas as pd, statsmodels.formula.api as smf
BASE = '/home/claude/paper'
c = pd.read_csv(f'{BASE}/data/panel.csv').sort_values(['cik', 'year'])
c['R_cash'] = c.g + c.m_fcf_sbc
fye = pd.to_datetime(c.fy_end)
acc_yy = c.accn.str.split('-').str[1].astype(int) + 2000
c['late'] = acc_yy > np.where(fye.dt.month <= 9, fye.dt.year, fye.dt.year + 1)   # source filing later than the normal 10-K
c['unver'] = (c.g >= 1.0) & c.acq_pay.isna() & c.gw_jump.isna()
e2 = (c.acq_flag == 0) & ~c.unver                                                 # exclusion-only proxy for E2

def boot(d, fn, B=300, seed=1):
    d = d.reset_index(drop=True); rng = np.random.default_rng(seed)
    f, inv = np.unique(d.cik.values, return_inverse=True); idx = [np.where(inv == j)[0] for j in range(len(f))]
    return np.array([fn(d.iloc[np.concatenate([idx[j] for j in rng.integers(0, len(f), len(f))])]) for _ in range(B)])
def q(x, p=.95): return float(np.quantile(x.dropna(), p))
def chg(d, R, a='2016-19', b='2023-25'): return q(d.loc[d.period == b, R]) - q(d.loc[d.period == a, R])
def show(lab, d, fn):
    bs = boot(d, fn); print(f'{lab}: {fn(d)*100:+.1f} 90% [{np.quantile(bs,.05)*100:+.1f}, {np.quantile(bs,.95)*100:+.1f}]')

# T1/T2 backfill and the P95 change
print('late-source firm-years:', int(c.late.sum()), 'of which first panel year:', int((c.late & (c.year == c.groupby('cik').year.transform('min'))).sum()))
P = c[c.period.isin(['2016-19', '2023-25'])]
for R in ['R_op', 'R_cash']:
    show(f'P95 change {R} baseline', P[['cik', 'period', R]].dropna(), lambda z: chg(z, R))
    show(f'P95 change {R} no late-source', P[~P.late][['cik', 'period', R]].dropna(), lambda z: chg(z, R))

# T4 capital-intensity gap 2023-25, E2 proxy: same-year vs prior-year sort, and capex added back
c['k_lag'] = c.groupby('cik').capex_int.shift(1).where(c.groupby('cik').year.shift(1) == c.year - 1)
c['R_addback'] = c.R_cash + c.capex_int
D = c[e2 & (c.period == '2023-25')]
for s in ['capex_int', 'k_lag']:
    x = D.dropna(subset=[s]).copy(); x['hi'] = x[s] > x[s].median()
    for R in ['R_cash', 'R_addback']:
        show(f'gap sort={s} {R}', x[['cik', 'hi', R]].dropna(), lambda z: q(z[z.hi][R]) - q(z[~z.hi][R]))

# T5 anchor: firm-cluster bootstrap of the 2023-25 top-tail inversion (tau = 0.18)
S = c[e2 & (c.period == '2023-25')].dropna(subset=['R_cash'])
def anchor(z):
    t = z[z.R_cash >= q(z.R_cash)]; G = z.g.median(); sig = (t.sm / t.rev).fillna(0); kg = t.capex_int.fillna(0)
    k = np.where(t.g > 0, kg / t.g, 0); m0 = t.m_fcf_sbc + .82 * sig + kg
    return np.array([m0.median(), m0.quantile(.75), (t.R_cash - m0 - (1 - k) * G).median()])
bs = boot(S, anchor, B=1000, seed=7)
print('anchor median m0, Q3 m0, median Pi (ub):', anchor(S).round(3), '90%:', np.quantile(bs, [.05, .95], axis=0).round(3).tolist())

# T6 spend ratio by period (E2 proxy)
c['G_t'] = c.groupby('year').g.transform('median')
x = c[e2 & (c.g > c.G_t) & c.sm_lag_share.between(.01, 1.5)].copy(); x['ratio'] = x.sm_lag_share / (x.g - x.G_t)
print('spend ratio by period:', x.groupby('period').ratio.median().round(2).to_dict(), 'year 2021:', round(x[x.year == 2021].ratio.median(), 2))

# T7 out-of-sample: next-year change in the cash score
c['k2'] = np.where(c.g > .05, c.capex_int.fillna(0) / c.g, 0)
c['Pi_lb'] = c.R_cash - (c.m_fcf_sbc + c.capex_int.fillna(0) + (1 - c.k2) * c.G_t)
g = c.groupby('cik'); c['R_f1'] = g.R_cash.shift(-1).where(g.year.shift(-1) == c.year + 1)
d = c[(c.year <= 2024) & (c.g > .05)][['cik', 'year', 'R_cash', 'R_f1', 'Pi_lb', 'g', 'm_fcf_sbc']].dropna()
for v in ['R_cash', 'R_f1', 'Pi_lb', 'g', 'm_fcf_sbc']:
    d[v] = d[v].clip(*d[v].quantile([.01, .99]))
d['dR'] = d.R_f1 - d.R_cash; tr, te = d[d.year <= 2018], d[d.year >= 2019]
for f in ['dR ~ R_cash', 'dR ~ R_cash + Pi_lb', 'dR ~ g + m_fcf_sbc', 'dR ~ g + m_fcf_sbc + Pi_lb']:
    p = smf.ols(f, tr).fit().predict(te)
    print(f'OOS 2019-24 R2 {f}: {1 - np.mean((te.dR - p)**2) / np.mean((te.dR - tr.dR.mean())**2):.3f}')
```

Additional checks run but not reproduced above:
- the real-threshold and stayer versions of T2 (CPI-U annual averages; 88 firms present in both periods);
- annual P95 and rolling quantile-regression slopes (T3);
- 2016-19 against fiscal 2025 alone;
- the T9 Holm and BH adjustments, computed from the SEs in `notes/empirics_organic.json` (`headline` block);
- turnover and rank autocorrelation;
- the T10 acquisition-affected shares;
- the G sensitivity of the spend ratio.

## Appendix B. Sources opened for this review

- Exzeo Group, Inc., Form 10-K for fiscal 2025, risk factors on customer concentration: https://www.sec.gov/Archives/edgar/data/1873951/000119312526076686/xzo-20251231.htm
- Xunlei fourth-quarter 2025 results call summary (revenue +42.5%; Hupu acquired in 2025): https://finance.yahoo.com/news/xunlei-q4-earnings-call-highlights-154702786.html
- LiveRamp DEFA14A (2024): CEO PSUs weighted 70% on the Rule of 40 and 30% on relative TSR: https://capedge.com/filing/733269/0001104659-24-078324/RAMP-DEFA14A
- Clouded Judgement, 5 February 2021 (median EV/NTM revenue 19.8x): https://cloudedjudgement.substack.com/p/clouded-judgement-2521
- Clouded Judgement, 27 December 2024 (median 6.1x at year end): https://cloudedjudgement.substack.com/p/clouded-judgement-122724-2024-year
- Lee (2024), Applied Finance Letters 13, abstract: https://ojs.aut.ac.nz/applied-finance-letters/article/view/761
- Sethuraman, Tellis and Briesch, advertising-elasticity meta-analysis (mean short-run elasticity 0.12): https://papers.ssrn.com/ab_id=1866002 (published in Journal of Marketing Research, 2011)
- Standard references cited from the literature, not re-opened:
  - Harvey, Liu and Zhu (2016), Review of Financial Studies 29(1);
  - Chan, Karceski and Lakonishok (2003), Journal of Finance 58(2);
  - Gelman and Stern (2006), The American Statistician 60(4);
  - Banz and Breen (1986), Journal of Finance 41(4);
  - Kothari, Shanken and Sloan (1995), Journal of Finance 50(1);
  - Jain and Kini (1994), Journal of Finance 49(5);
  - Pastor, Taylor and Veronesi (2009), Review of Financial Studies 22(8).
