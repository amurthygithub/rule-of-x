# Executive pressure-test panel: Paper 1, v1

**Paper:** "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation", v1, October 2026 (`notes/reviews/paper1_v1/paper1_v1.pdf`, `.txt`).
**Grounding files read:** `notes/assumptions_register.md`, `notes/assumptions_memo.md`, `data/tasks/params.yaml`, `data/tasks/params_reliability.yaml`.
**Panel date:** 29 October 2026. No paper or code file was edited.

**Method.** Eight roles, each argued from its own incentives and experience. Every factual pushback was checked before it was asserted: against a public source (web, accessed 29 October 2026; links in each table and in Appendix B), or against the paper's own core panel (`data/panel.csv`, SIC 7372, observed scores E1 unless stated). Panel computations are quick replications with the filters given in Appendix A. They are not the paper's estimates, and the author should recompute them with the replication scripts before using them.

**Verdict labels used in the evidence tables.**
- *Confirmed*: the source says what the paper says, and it fits the use.
- *Confirmed, caveat*: the source is right, but the paper's use needs a qualifier.
- *Contested*: the evidence points another way, or the grounding measures a different thing.
- *Not grounded*: a scenario value with no precedent, presented in a way that a reader could take as evidence.

---

## 0. The panel's verdict

The paper is the most careful treatment of the Rule of 40 any of us has read. Three of its ideas would change how we run a $1-5B public software company:
1. Report the score on one stated basis, with a bridge from the number we publish.
2. Charge acquired growth with what it cost.
3. Treat the capacity to absorb change, not the technology, as the binding constraint on AI-driven margin.

It also gives a board a defensible upper bound for management's AI margin claims (Table 10).

It is not yet usable for planning, for five reasons:
- It gives no decision rules in the units a finance team budgets in.
- Its most quotable number, a decision weight on growth of 7 to 13, depends on an attribution choice. Our replication moves it to 2 to 6 when that choice changes.
- Its horizon ranges (for example, 40 to 156 in 2028) are too wide to plan on.
- Its central execution case is roughly ten times slower than what the median public software firm achieved in 2022-24 without AI.
- Its licence bars the use by for-profit firms that its own conclusion recommends.

We would not circulate it to a board as written. With the ten changes in Section 4, Sections 4.5, 6, 7.2 and 8 would become board-usable, and the rest would survive a CFO's red pen.

| Role | Usefulness today | After the top 10 changes | What the role would actually use |
|---|---|---|---|
| CEO / COO | Medium | High | Table 10 as a cap on AI promises; Corollary 3 stage priorities; the score bridge |
| CFO | Medium | High | Section 6 acquisition charging; Corollary 2 and Remark 11 hurdles; the SBC basis |
| CHRO | Low | Medium | Proposition 11(c) speed limit as a planning constraint |
| CIO / CISO | Medium | High | Proposition 10 diversity rule; ITGC per AI application; revalidation cost |
| Chief product officer | Low | Medium | Corollary 3(ii); gross profit per compute dollar (Section 8.4) |
| Head of transformation | Medium | High | Propositions 11(d) and 12(c): sequence by scarcest capacity, manage the embedding probability |
| Audit committee chair | Medium | High | Proposition 10; the bridge; Table 10 as a plausibility check |
| General counsel | Low (licence blocks use) | Medium | Nothing until the licence and disclosure items are fixed |

## 1. What the panel found credible

- **The data.** It uses XBRL facts as first reported, keeps inactive registrants (so it does not condition on survival), reports four margin bases, and separates the two estimands. The AppLovin restatement example (Section 4.1) is what an audit committee wants to see.
- **The measurement message.** Basis choices move scores by more than operations do (Sections 4.5 and 8.3). CoreWeave scores 167 on GAAP and 14 on cash after SBC.
- **Acquired growth.** The acquired-growth algebra and the Remark 3 bounds (Section 6) hold. The net weight X - k_acq is the cleanest idea in the paper for an M&A committee.
- **The hurdles.** The capital-for-labor hurdle, with depreciation (Corollary 2, Remark 4(c)), and the own-versus-rent compute test (Remark 11) are usable as stated.
- **Control design.** Proposition 10(a): stacking layers on one model provider addresses independent failures. Only diversity addresses common-mode failures. This is correct, and boards need to hear it.
- **Candor.** Scenario values are flagged, the paper reports results that reversed earlier drafts, and Appendix E discloses the AI collaboration in full.

---

## 2. Role reviews

### 2.1 CEO / COO of a $1-5B public SaaS company

**1. What I would actually do differently**
- **Change how the score is reported to me and my board.** For my peer group the basis decides whether we are a "Rule-of-40 company". Among core-sample firm-years of 2023-25 with $1-5B of prior-year revenue (111 firm-years, 42 firms), 52% clear 40 on free cash flow before SBC and 10% after SBC. The medians are 40 and 23 (panel computation, Appendix A). I would require the bridge every quarter.
- **Rank AI initiatives by stage (Corollary 3).** While we are gaining share, productivity of selling and retention come before G&A automation. A 10% gain in growth per dollar of selling is worth 2.2 to 4 times a 10% cut in an equally large cost line (Corollary 3(ii)).
- **Use Table 10 to cap expectations.** For a mature firm in a market growing about 15%, the central full-automation ceiling is 73 points on cash after SBC. The best organic firms' durable scores today are 47 to 63 (Table 11 anchor). The prize is tens of points over a decade, not "Rule of 100 by 2028". I would use this against internal and banker narratives.
- **What I would not do.** I would not change growth spending on the strength of "a weight of 7 to 13", and I would not put the horizon ranges in any plan.

**2. What I would not believe, and the checks**

| # | Claim (where) | What we checked | Verdict | Source |
|---|---|---|---|---|
| C1 | A Rule of 100 needs market growth above about 42% a year (Abstract; Section 7.2; Table 10) | The arithmetic is right. Gartner forecasts worldwide software spending growth of 12.8% in 2025 and 15.1% in 2026, against 55.8% for data center systems. The threshold is about three times the software market's growth, and plausible only in AI infrastructure or agent segments, where such growth is transient | Confirmed, caveat: the threshold should be stated against the served market, not "the market" | [Gartner, 22 Apr 2026](https://www.gartner.com/en/newsroom/press-releases/2026-04-22-gartner-forecasts-worldwide-it-spending-to-grow-13-point-5-percent-in-2026-totaling-6-point-31-trillion-dollars) |
| C2 | The top tail's durable and transient split (Section 7.3 Anchor; Table 11, 2025 row) uses one market growth of 12.0% for all 20 firm-years | Since dR∞/dG = 1 - k, about 1, a firm whose served market grows 30% gets 18 more durable points and 18 fewer transient points than the paper assigns. Palantir's and Exzeo's "24 to 49 points" of surplus is largely a statement about the 12% assumption | Contested at firm level | Paper, Proposition 5 and Table 11 notes |
| C3 | Palantir's Q2 2026 score of 155 (Section 1; Section 8.3) | 93% revenue growth plus a 62% adjusted operating margin | Confirmed | [Palantir 8-K Ex. 99.1](https://www.sec.gov/Archives/edgar/data/0001321655/000132165526000039/a2026q2ex991pressrelease.htm); [Stocktwits](https://stocktwits.com/news-articles/markets/equity/palantir-s-rule-of-40-score-hit-155-here-s-the-math-and-why-it-matters-for-software-valuations/cZo5OP3RJER) |
| C4 | Firms reinvesting in AI may have to accept a "Rule of 30" (Lipman et al., 2026) | Bain: "may force SaaS companies to accept the Rule of 30 for a while" | Confirmed | [Bain, Apr 2026](https://www.bain.com/es/insights/ai-brings-headwinds-and-tailwinds-to-the-rule-of-40/) |
| C5 | Reported-score levels (Table 3: median of 15.2 on cash after SBC in 2023-25) | Blossom Street, Q4 2024: the median score was 15 for 60 SaaS firms that listed after October 2017. That is consistent, but practitioners compute on cash before SBC, and Table 3 does not report that basis | Confirmed, caveat: add the before-SBC basis | [Blossom Street](https://blossomstreetventures.medium.com/q4-2024-rule-of-40-data-in-public-saas-d8a7d829ae16) |
| C6 | The top tail fell between 2016-19 and 2023-25 "as fast growers became scarcer", which "points to the supply of growth opportunity ... rather than willingness to trade margin for growth" (Sections 5.2 and 7.4) | The federal funds rate stood at 0.5 to 2.3% in 2016-19 and 3.7 to 5.3% in 2023-25. By Propositions 6 and 2(d) of the paper itself, a higher discount rate lowers the firm's own weight X and so its optimal growth, with no change in opportunity. The data cannot separate the two channels | Contested: the attribution is not identified | [FRED, BOGZ1FL072052006A](https://fred.stlouisfed.org/data/BOGZ1FL072052006A) |
| C7 | Central execution: an exceptional firm's margin intercept rises by about 0.6 points by 2028 and 5 points by 2036 (Section 7.3 Pace; Table 11, m0 column) | In 2022-24, without AI programs, the median core firm present in both years (142 firms) raised gross margin by 1.7 points and cut its G&A share by 1.6 and its R&D share by 1.3. Gross margin less G&A rose by a median 3.7 points (interquartile range 0.8 to 7.8) in two years | Contested: "central" is a slow case, and "fast" (about 1.6 points a year) is close to what the median firm actually did | Panel computation, Appendix A |
| C8 | Extreme scores are transient (Proposition 4; Corollary 1) | Correct for the firm. Lovable reached $100M of ARR in eight months. A transient entrant's surplus is drawn from the incumbent's share, which the paper does not discuss | Confirmed; gap noted | [tech.eu, Jul 2025](https://tech.eu/2025/07/23/lovable-becomes-fastest-software-company-ever-to-reach-100m-arr/) |

**3. What is missing for me to use it**
- **A "where am I" worksheet.** The inputs are the numbers I already have: growth, NRR, S&M share, gross margin, G&A share, SBC share and capex share. The outputs should be my durable score R∞, my surplus, my implied weight, my automation hurdle, and the share of my score that would survive saturation.
- **A go/no-go rule for a transformation program.** Under central execution, embedded gains first exceed the dip after about 9 years (Section 7.3). No board funds that. The paper should say what follows: run a narrower program, or raise the embedding probability first.
- **A planning horizon of 2027 to 2029.** 2036 is not a planning year.
- **A test for which regime applies to me.** I need observable indicators of whether I live under "prices fixed" (Corollary 4) or "free entry" (Proposition 8): gross retention, price realization, win rates against AI-native entrants.

**4. Where it could be misread or misused**
- **"Our ceiling is 88, so a plan of 55 is conservative."** Table 10 is an upper bound at full automation, not a target.
- **"The top of the distribution fell 12 to 15 points, so 40 is now top-decile and we can lower the bar."** That finding is descriptive, not normative.
- **On an earnings call: "the Rule of 40 understates us because our decision weight on growth is 10."** Investors will hear "we will burn cash".
- **"Exceptional firms could reach 156 by 2028."** This will be quoted without "scenario bound".

**5. Jargon and presentation that lose me**
- The title word "Price Line".
- The second sentence of the abstract: "price lines whose tangency with it gives the maximal score: the intercept plus market growth plus a growth surplus that vanishes as market share saturates and draws on a finite budget of share headroom".
- "Growth surplus", "share headroom budget", "estimand E1/E2", "embedding".
- The Rule of 1000. No operator runs a Rule-of-1000 company, and the section spends a page on it.

### 2.2 CFO

**1. What I would actually do differently**
- **Add an internal score on free cash flow after SBC.** It would sit next to the Street definition, not replace it. Median SBC was 14.8% of revenue for $1-5B firms in 2023-25 (panel computation); that is the gap between the two bases.
- **Adopt Section 6 for M&A reviews.** Every deal would be shown on three bases: uncharged, annuity and fully charged (Remark 3). The annuity score is the one to show the board.
- **Use Corollary 2 with depreciation (g + δ) as the hurdle for capitalized AI builds and owned compute.** Use Remark 11 for own-versus-rent: the vendor markup must exceed about 20% at 5% market growth and 60% at 15%.
- **Put current-law tax treatment into AI build cases** (Remark 1: domestic R&E expensed, ψ = 1).
- **What I would not do.** I would not adopt a decision weight of 7 to 13. The reasons follow.

**2. What I would not believe, and the checks**

| # | Claim (where) | What we checked | Verdict | Source |
|---|---|---|---|---|
| F1 | Growth spending implies a weight on growth of 7 to 13, far above screening weights (Abstract; Section 5.4; Table 2; Section 8.1) | The ratio divides the S&M share by growth *in excess of the year's median*, so it treats the median firm's growth as free. Our replication on the core panel, excluding acquisition-flagged years, gives median ratios of 3.2 with the paper's baseline (X = 7.0 to 12.7), 1.4 if zero-spend growth is zero (X = 3.1 to 5.6), and 1.0 if S&M must also replace 10% churn (X = 2.3 to 4.1). The last range overlaps Bessemer's 2 to 3. Bessemer's own regression put the implied weight at about 2x to 9x over the cycle | Contested: the headline depends on attribution | Panel computation (Appendix A); [Bessemer, Rule of X](https://bvp.com/atlas/the-rule-of-x) |
| F2 | The proxy's biases are "of uncertain net sign" (Section 5.4) | A large share of S&M maintains revenue: the median total cost of renewals was $0.13 per $1 of ARR (Pacific Crest 2015, 305 respondents). At 90% renewal that is about 12 points of revenue, roughly a third of a 40% S&M share. The zero-spend baseline (F1) and the maintenance share both push the ratio up. Only omitted expansion R&D pushes it down | Contested: the likely net sign is upward | [Gainsight summary of Pacific Crest 2015](https://www.gainsight.com/blog/8-customer-success-takeaways-from-the-2015-pacific-crest-saas-ceo-survey/) |
| F3 | X = 7 to 13 is "consistent with the marginal value of revenue" (Proposition 6) | At the optimum, the last dollar of growth spend buys 1/(X - k) dollars of annual revenue. X = 7 to 13 therefore means the marginal dollar of S&M buys 8 to 14 cents of revenue, a marginal payback on gross profit of about 9 to 17 years at a 75 to 78% gross margin. The average ratio of 3.3 implies an average payback of about 51 months. The median CAC payback reported for 2025 is 16 months (Benchmarkit and Aleph, 198 firms, mostly private) | Contested: the paper must reconcile this with paybacks in use | [ScaleXP summary of Benchmarkit/Aleph 2026](https://www.scalexp.com/?p=129928) |
| F4 | The cash tax rate runs from 15% (CAMT) to 21% (Section 7.2; Table 10) | CAMT applies only where three-year average adjusted financial statement income exceeds $1B ($800M under the simplified method). Most $1-5B revenue firms are below that, so 15% is not their floor. State taxes, excluded, push the rate the other way | Contested as grounding (the range is fine as a scenario) | [IRS, CAMT simplified method](https://irs.gov/about-irs/new-simplified-method-for-determining-status-for-corporate-alternative-minimum-tax) |
| F5 | Cost of capital of 9.34% for software firms (Section 6) | Damodaran, January 2026, Software (System & Application): 9.34% | Confirmed | [Damodaran WACC](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/wacc.html) |
| F6 | Fees of 2 to 3% of revenue "are those of card processing" (Section 7.2) | Enterprise SaaS is mostly invoiced. The register rates this class d and the lowest-influence input (a swing of 0.8 points in G*) | Confirmed, caveat: say it is a card-billing upper bound | `assumptions_register.md`, Section 3 |
| F7 | Capital intensity k is at least 0 in every calibrated case (Tables 10 and 11) | Remark 4(c) shows that deferred revenue makes the cash k negative for upfront-billed SaaS, which raises the cash score by k times g. No table shows that case | Gap: add k = -0.3 | Paper, Remark 4(c) |

**3. What is missing for me to use it**
- **A mapping from α, λ and X to my planning inputs.** I need a recipe: X ≈ (the value of a dollar of new revenue) = gross margin x (1 - cost to retain) / (r + gross churn - expansion), bounded by a terminal assumption. Then compare it with the ratio of the marginal (cohort) S&M share to new ARR. The paper's Proposition 6 is the general version; give me the operator's version.
- **Firm-level zero-spend growth from disclosed NRR.** Remark 4(b) already defines G_i = ln NRR. Use it in Section 5.4 instead of the cross-sectional median.
- **Year-by-year output in plan format (FY27 to FY29).** That means the dip, parallel-run premia and one-time costs in P&L and free-cash-flow lines, separating restructuring charges (which non-GAAP excludes) from run-rate.
- **A single-firm worksheet in the replication package.** The code licence blocks this today; see the general counsel's review.

**4. Where it could be misread or misused**
- **"Our decision weight is 10, so ignore the Rule of 40."** This is a ready-made justification for burn, and the paper gives no guardrail.
- **Applying Table 11's durable and transient split to our own firm at G = 12%.**
- **"Bending Spoons' true score is -24.8."** That is a lower bound by construction (Remark 3). Quoted alone, it misleads.
- **Treating the Table 10 ceiling as guidance.**

**5. Jargon and presentation that lose me**
- "Marginal q of revenue", "Dorfman and Steiner condition", "HJB", "y := X - k", "ψ" and "δK" in the main text.
- Table 2 has eight numeric columns; I need three.
- "First reported" is good. Keep it.

### 2.3 CHRO

**1. What I would actually do differently**
- **Treat the number of employees whose work can change each year as a hard planning constraint**, and measure it: Proposition 11(c) says no program moves faster than its scarcest capacity.
- **Protect sponsorship continuity.** A leadership change that does not keep the program is a modeled hazard, ν_L (1 - p_keep). I would put succession for program sponsors on the board's talent agenda.
- **Sequence by score gain per affected employee** (Proposition 11(d)).

**2. What I would not believe, and the checks**

| # | Claim (where) | What we checked | Verdict | Source |
|---|---|---|---|---|
| H1 | Central change capacity is 10% of employees a year, "the middle of a range of 5 to 20% that layoff rates and single restructurings bracket" (Section 7.3 Capacity; `params.yaml` change_capacity) | JOLTS, August 2026: layoffs and discharges 1.0% a month, total separations 3.2% (total nonfarm). Those are exits, concentrated in high-churn sectors, not the share of employees whose work can be redesigned. A closer precedent: WEF Future of Jobs 2025 expects 59 of every 100 workers to need training by 2030 (about 12 a year), and 19 of 100 to be reskilled and redeployed internally | Confirmed, caveat: the value is plausible, but the grounding measures a different thing | [BLS JOLTS](https://www.bls.gov/news.release/jolts.nr0.htm); [UNLEASH summary of WEF 2025](https://www.unleash.ai/artificial-intelligence/5-things-hr-needs-to-know-from-wefs-2025-future-of-jobs-report/) |
| H2 | Capacity is a fixed number per year (Assumption 8) | Gartner: employee willingness to support change fell from 74% in 2016 to 38% in 2022. Capacity falls with change load, and it can also be bought (change managers, redeployment programs). The model treats it as exogenous and constant | Contested | [Accounting Times on Gartner](https://www.accountingtimes.com.au/profession/finance-leaders-are-getting-change-management-wrong-gartner-says) |
| H3 | Transitions embed 1 to 2 years after they start (Section 7.3 Risk) | For EU entities, Directive 98/59/EC requires consultation with workers' representatives, and collective redundancies take effect no earlier than 30 days after notifying the authority (extendable to 60). Works councils add months. The range is consistent, but the paper should state the legal minimums for workforce-affecting processes | Confirmed, caveat | [EUR-Lex summary](https://eur-lex.europa.eu/EN/legal-content/summary/collective-redundancies-staff-information-and-consultation.html) |
| H4 | A disruption rate of 0.23 a year (Section 7.3 Risk) | CEO turnover (16.8%, Kaplan and Minton) is sourced. But 0.15 of the 0.23 is the strategy-change hazard, and the keep probability (0.6) is also class d ("no credible estimate found"). The dominant term is unsourced | Not grounded (the dominant term) | `params.yaml` leadership_and_context |
| H5 | HR automation's compliance cost sits in "AI compliance" at 0.1 to 0.4% of revenue (Table 13) | Under the AI Omnibus (Regulation (EU) 2026/1744, in force 27 July 2026), stand-alone high-risk systems in Annex III, which include employment uses, apply from 2 December 2027. Automating recruitment, task allocation or performance monitoring triggers those obligations; the paper does not mention it | Gap | [National Law Review](https://natlawreview.com/article/eu-digital-omnibus-ai-enters-force) |

**3. What is missing for me to use it**
- **A people-plan translation**: roles redesigned, redeployed and exited per year; reskilling hours; and the residual human organization behind the accountability floor ("whatever human review and sign-off regulation or the firm's risk appetite requires", Definition 3). Who are these people, how many, at what cost?
- **Definitions of "affected employee" and "embedded".**
- **Retention risk and retention grants during transformation.** These are SBC, so they hit the paper's own preferred margin.

**4. Where it could be misread or misused**
- **"The paper says we can change 20% of employees a year."** That will be used to justify aggressive reduction-in-force plans; 20% is the fast-execution scenario, not a norm.
- **"Full automation" read as a headcount target.**

**5. Jargon and presentation that lose me**
- "Γ_i", "c_ip", "waves", "program time t_R", "ν_D".
- The capacity argument is right but invisible: it sits in one bullet of Section 7.3.

### 2.4 CIO / CISO

**1. What I would actually do differently**
- **Design key financial controls and key processes with provider diversity** (Proposition 10(a)).
- **Budget revalidation at every model upgrade as a run cost.** T_up is about 1.2 years for models released since 2025 (Table 13). Pin versions where the platform allows.
- **Add an ITGC line to SOX scoping for each AI application that performs or supports an in-scope control** (Remark 10: about $347,000 a year at $1B of revenue).
- **Plan post-quantum migration against NIST IR 8547.**

**2. What I would not believe, and the checks**

| # | Claim (where) | What we checked | Verdict | Source |
|---|---|---|---|---|
| S1 | Security spending today is 0.69% of revenue, scaled up for full automation (Table 13) | IANS 2025 (587 CISOs): spending "held flat at 0.69%" of revenue, and 10.9% of IT spend, across all industries. For a SaaS vendor, product security, cloud security engineering and certifications (SOC 2, FedRAMP) sit partly in COGS and R&D, so the all-industry figure understates a software firm's security cost | Confirmed, caveat: right source, wrong population; use the tech-sector cut | [IANS 2025](https://www.ians.com/insights/ciso-leadership/2025-security-budget-benchmark-report) |
| S2 | Common-mode cost from 0.5, 2 or 6 day-long incidents a year at a *model provider* (Table 13; Lemma 4(e)) | The July 2024 CrowdStrike update cost Fortune 500 firms an estimated $5.4B, of which only $0.54B to $1.08B was insured. That confirms the thesis, but the largest common-mode exposures are the shared tooling stack (EDR, identity provider, cloud region), not only the model vendor | Confirmed, caveat: the scope is too narrow | [Axios on Parametrix](https://www.axios.com/2024/07/24/fortune-500-crowdstrike-outage-impact) |
| S3 | Review-proof error rates of 1.1 to 4.2% per unit (Table 13) | Measured hallucination rates depend on the judge. Gemini-2.0-Flash scored 0.7% on Vectara's original HHEM leaderboard and about 7.6% under the FaithJudge method | Confirmed, caveat: say it is an order-of-magnitude input | [Emergent Mind on Vectara](https://www.emergentmind.com/topics/vectara-s-hallucination-leaderboard); [report of the 0.7% figure](https://thedayafterai.squarespace.com/featured/gemini-20-flash-hits-07-hallucination-rate-but-trails-chatgpt-o4-mini-in-reasoning-benchmarks) |
| S4 | NIST deprecates quantum-vulnerable algorithms after 2030 and disallows them after 2035 (Section 2.4; Definition 3(ii)) | IR 8547 was published in final form on 27 October 2026. In the initial draft, deprecation after 2030 applied to 112-bit-security algorithms (such as RSA-2048) and disallowance after 2035 to all quantum-vulnerable ones; check the final text and state the distinction. The migration cost (0.75 to 3% of IT spend a year) is class d | Confirmed (dates); cost not grounded | [NIST CSRC](https://csrc.nist.gov/pubs/ir/8547/final); [Encryption Consulting](https://www.encryptionconsulting.com/nist-ir-8547-2030-2035-action-plan/) |
| S5 | Change capacity, not security review or decisions, binds (Section 7.3 Capacity; Section 8.2) | Security-review bandwidth (10 reviews per reviewer per quarter) and decision capacity (Φ = 5 concurrent initiatives) are both class d in `params.yaml`. Build and run engineering capacity (the register's 0.48 FTE per automated process in run mode, class b) and data readiness are not in the Part I resource list at all | Not grounded (conclusion rests on class d inputs) | `params.yaml` compliance, decision_capacity; `assumptions_memo.md` Section 3 |

**3. What is missing for me to use it**
- **Reference-architecture assumptions**: multi-model routing, fallback capacity (Y_fb), kill switches. The cost of keeping a second provider warm is not in c_full.
- **Agent identities.** With agents, access reviews and change management scale with agents and tool permissions, not with applications. The ITGC term should scale with agents and integrations.
- **A mapping to IT budget lines**: run versus change, opex versus capex, and which floors are mine and which are the business's.

**4. Where it could be misread or misused**
- **"Full automation" read as permission to cut IT operations and security staff.**
- **Lemma 4(b), "security ... grows only with the logarithm of exposure".** It will be quoted to argue that security budgets need not scale with AI. The result holds only under an assumed exponential hazard form.

**5. Jargon and presentation that lose me**
- "c_sec, c_err, c_anc, L_sec, ξ_exp, H_cm, Y_fb", "review-proof error rate".
- Table 13 is excellent but unreadable in two minutes: it needs a one-line "what to budget" summary per floor.

### 2.5 Chief product officer

**1. What I would actually do differently**
- **Treat growth per dollar of selling (the paper's demand pull) as the main lever while we gain share.** Track it through growth that does not need rising S&M intensity (Section 7.4, lever 2).
- **Track gross profit per dollar of compute by product line** (Section 8.4), because blended gross margin moves as AI lines grow (Definition 3).
- **Design pricing to keep part of falling inference costs** (lever 4).

**2. What I would not believe, and the checks**

| # | Claim (where) | What we checked | Verdict | Source |
|---|---|---|---|---|
| P1 | AI products' gross margins of 45% in 2025, projected 53% and 59% (Section 7.1) | ICONIQ 2026 confirms the figures. It also shows pricing shifting: consumption pricing up from 35% to 42% of models, outcome pricing from 18% to 23%, subscription at 57%. Among consumption-priced firms, 84% pass at least part of the inference bill to customers. With pass-through, the compute share is partly a pricing-design choice, not an exogenous scenario | Confirmed, caveat | [SaaStr summary of ICONIQ 2026](https://saastr.com/the-builders-economy-10-metrics-from-iconiqs-newest-2026-state-of-ai-report) |
| P2 | The price of a fixed level of benchmark performance fell 9 to 900 times a year (Sections 2.4 and 7.1) | Epoch confirms the range, with caveats: the fastest drops are recent and may not persist, and the GPQA example is about 40 times a year. The paper uses it correctly, as something competition may pass through | Confirmed | [Epoch AI](https://epoch.ai/data-insights/llm-inference-price-trends) |
| P3 | A short-run price elasticity of inference demand just above one, so spending need not fall (Section 7.1) | Demirer et al.: "preliminary short-run price elasticities just above one, suggesting limited scope for Jevons-Paradox effects". The paper's reading holds | Confirmed | [NBER w34608](https://www.nber.org/papers/w34608) |
| P4 | AI raises market growth G as labor budgets shift to software (Table 1) | Table 1 has no row for seat compression, the reverse effect for seat-priced vendors whose customers cut headcount. The register says seat elasticity is class d ("no filing reports seats against customer headcount") | Gap: the sign of dG is unknown for seat-priced firms | `assumptions_memo.md` Section 5 |

**3. What is missing for me to use it**
- **How to estimate our own demand pull from product data**: the self-serve or organic share of new ARR, sales-cycle length, win rates, NRR.
- **A mapping of AI features to λ, G and γ**, and of packaging and pricing moves to the pass-through elasticity ϕ (Lemma 3).
- **Expansion R&D.** The model counts it as growth spend, but the empirics use S&M only (Section 5.4). Product-led firms buy growth with R&D.

**4. Where it could be misread or misused**
- **Taking the 45% AI gross margin as our destiny.** It also lets a sales team argue that our 78% is untouchable.
- **"Owned compute raises margin."** Remark 11 says it does so only if the vendor's markup exceeds 20 to 60%.

**5. Jargon and presentation that lose me**
- "Demand pull λh", "pass-through elasticity ϕ", "Lemma 3".
- "Pricing power" appears as lever 4 but gets no analysis.

### 2.6 Head of transformation

**1. What I would actually do differently**
- **Apply the attainable-frontier logic.** Identify the scarcest capacity, sequence by score gain per unit of it (Proposition 11(d)), and stop launching more initiatives than it can carry.
- **Make the embedding probability the program KPI**: per wave, the share of attempts that deliver times the share that survive until savings are sustained. Each embedded process costs 1/p_emb attempts (Proposition 12(c)).
- **Report the dip of transitions in flight to the board explicitly** (Section 8.2), so that a dip from executing is not read as weakness.

**2. What I would not believe, and the checks**

| # | Claim (where) | What we checked | Verdict | Source |
|---|---|---|---|---|
| T1 | An attempt works with probability 0.54 in central execution: "the share of AI proofs of concept that reach production" (Section 7.3 Risk) | S&P Global, via CIO Dive (14 March 2025; more than 1,000 respondents): the average organization scrapped 46% of AI proofs of concept before production, and 42% of companies abandoned most AI initiatives (17% a year earlier). Reaching production is not the same as delivering durable savings, so 0.54 is an upper bound for that construct | Contested (construct mismatch) | [CIO Dive](https://www.ciodive.com/news/AI-project-fail-data-SPGlobal/742590/) |
| T2 | Fast execution succeeds with probability 0.80, "the success rate of transformations that meet six conditions" (Section 7.3 Risk) | BCG (October 2020; 825 executives plus 70 client companies): 30% of transformations met or exceeded target value with sustainable change, and 80% when six factors were present. The ratings are self-assessed on a 1 to 10 scale. The unconditional rate, 0.30, is the closer analog of the central case and is not used | Confirmed, caveat: it is a self-reported best case | [BCG press release](https://www.bcg.com/press/29october2020-companies-can-flip-the-odds-of-success-in-digital-transformations-from-30-to-80) |
| T3 | Reorganizations arrive at 0.46 a year and freeze about 10% of the time (Section 7.3) | McKinsey (2015): almost 60% of respondents had a redesign within the past two years, and fewer than 25% of redesigns succeed (sample not stated) | Confirmed, caveat (self-reported) | [McKinsey Quarterly](https://www.mckinsey.com/capabilities/people-and-organization/our-insights/getting-organizational-redesign-right) |
| T4 | Central execution embeds 2.5% of the program by 2028 and 23% by 2036; embedded gains exceed the dip after about 9 years (Section 7.3; Table 18 gives 9.1 years) | Under these rates a sponsor with a 3 to 5 year horizon would not fund the whole program. The paper does not draw that conclusion or give the embedding probability at which the program pays back | Gap: decision implication missing | Paper |
| T5 | "A program of 48 processes" covering the workforce (Section 7.3) | Class d. A real program inventory runs to hundreds of process-level items of very different sizes. The paper does not define a process in FTE or dollar terms | Not grounded | `params.yaml` |

**3. What is missing for me to use it**
- **Operational definitions.** "Attempt"; "works"; "embedded" (for example, savings sustained for four consecutive quarters at 80% of plan); "realized share b".
- **The slow case in Table 11.** It sits only in the text: "less than 1% of the program is embedded by 2036".
- **Portfolio guidance**: pilot-then-commit (Tewari is cited but not used), and the size of the J-curve dip in P&L terms.

**4. Where it could be misread or misused**
- **"The paper proves transformations take a decade."** That will be used to slow-roll.
- **"Fast execution completes by 2033."** That will be used to over-promise.
- **"Risk only delays, it does not lower the frontier"** (Proposition 12). That will be used to wave risk away. The paper itself says partial realization lowers the level, and delay lowers NPV.

**5. Jargon and presentation that lose me**
- "Waves", "T_emb", "T_par", "program time", "X-improving", "attainable versus expected frontier", "p_emb".
- The execution model is the most operator-relevant content in the paper, and it is written as Definition 4 plus Propositions 11 and 12.

### 2.7 Independent director, audit committee chair

**1. What I would actually do differently**
- **Ask management for the score bridge every quarter**: reported, then annual, then organic, then after SBC, then acquisitions charged.
- **Require control-design diversity for AI-run key controls**: at least one human layer or a second provider (Proposition 10).
- **Ask for ITGC scoping of each AI application** that performs or supports an in-scope control.
- **Use Table 10 as a plausibility check on any AI-margin narrative** in guidance.

**2. What I would not believe, and the checks**

| # | Claim (where) | What we checked | Verdict | Source |
|---|---|---|---|---|
| A1 | "Direct audit and Section 404 costs add about 0.14%" of revenue at $1B (Remark 10; Section 7.2) | Dropbox, with revenue of $2,548M in fiscal 2024, paid Ernst & Young $4.78M in audit fees (0.19% of revenue) and $6.52M in audit plus audit-related fees (0.26%), at 2.5 times the size. Audit fees rise less than proportionally with revenue, so a $1B firm's share is likely higher. The SEC's 2009 study put median 404 cost at $1.04M in 2007-08 dollars, and Protiviti (2022) found 30% of companies beyond their second year spending more than $2M | Contested: the bottom-up example understates the direct floor | [Dropbox DEF 14A, Apr 2025](https://www.sec.gov/Archives/edgar/data/1467623/000146762325000047/dbx-20250415.htm); [Dropbox FY2024 results](https://www.silicon.co.uk/press-release/dropbox-announces-fourth-quarter-and-fiscal-2024-results); [Accounting Today on Protiviti](https://accountingtoday.com/news/sox-compliance-hours-and-costs-increased) |
| A2 | Audit fees of $343 per $1M of revenue (register, lower end of the band) | Ideagen: S&P 500, fiscal 2022, average fee $10.78M. That is a large-cap ratio, not one for a $1-5B firm | Confirmed, caveat: wrong size class | [Ideagen](https://ideagen.com/thought-leadership/blog/audit-fee-trends-of-sp-500) |
| A3 | Misstatement parameters (Remark 10: 24 opportunities a year; human layers fail with probability 0.05, common mode 0.002) are "illustrative" | The three-human design implies about a 5% annual chance of an undetected material misstatement (24 x 0.0021). Adverse 404(b) opinions were 5.2% (FY2017) and 6.0% (FY2018) of auditor attestations. The orders of magnitude match | Supportive: state this as the calibration check | [Audit Analytics](https://blog.auditanalytics.com/sox-404-disclosures-a-fifteen-year-review/) |
| A4 | AI-run controls need ITGCs per application, retested at each model upgrade (Assumption 7; Remark 10) | PCAOB staff spotlight (22 July 2024) stresses "strong supervision" of GenAI; no standard yet sets AI-specific ICFR expectations. The paper's framing reads AS 2201 reasonably but is not an accepted standard | Confirmed, caveat: say it is the author's reading | [PCAOB](https://pcaobus.org/news-events/news-releases/news-release-detail/pcaob-staff-shares-observations-from-outreach-on-use-of-generative-artificial-intelligence-in-audits-and-financial-reporting) |
| A5 | Use of the score in board and investor materials (Section 8.3: "We suggest computing the score as this paper does") | SEC Release 33-10751 (2020) expects any material KPI to come with a clear definition and calculation, why it is useful, how management uses it, consistency across periods, recasting when the method changes, and disclosure controls. A cash-based Rule of 40 also uses non-GAAP inputs | Gap: give a KPI definition card | [KPMG on Release 33-10751](https://kpmg.com/us/en/frv/reference-library/2020/sec-issues-mda-guidance-kpi-metrics.html) |

**3. What is missing for me to use it**
- **A KPI definition card** that meets Release 33-10751, plus a statement of which bridge items are audited (none of the score is) and how management would control them.
- **Ownership.** Who owns the decisions behind the accountability floor, and what the board's AI-control risk appetite statement looks like.
- **A guardrail sentence on Remark 10.**

**4. Where it could be misread or misused**
- **Remark 10's numbers read as "replace control owners with AI".** An all-AI design ($1.70M) is cheaper than an all-human one ($2.01M), but it becomes the most expensive design once misstatement opportunities or the model's common-mode rate double.
- **"The accountability floor is 0.24%."** That will be used to argue the finance function can shrink to near nothing.
- **"Durable versus transient" used to excuse misses.**

**5. Jargon and presentation that lose me**
- "a_min", "P_mm", "p^cm", "C^itgc_g", "control layers of type j".
- "Accountability floor" is a good phrase. Keep it and define it in one sentence for directors.

### 2.8 General counsel

**1. What I would actually do differently**
Before anyone uses this in a board deck, sales deck or investor material, I would require four things:
- Treat any Rule-of-40 variant as a KPI, and a non-GAAP measure where it uses cash or adjusted inputs.
- Keep the paper's horizon ranges out of forward-looking statements.
- Clear every named-company comparison.
- Resolve the licence (below).

**2. What I would not believe, and the checks**

| # | Claim (where) | What we checked | Verdict | Source |
|---|---|---|---|---|
| L1 | "For practitioners the implications are concrete" (Section 9), under CC BY-NC-ND 4.0 for the paper and PolyForm Noncommercial 1.0.0 for the code (page 1 footnote) | PolyForm Noncommercial permits personal research and noncommercial organizations; internal use by a for-profit company is not a listed purpose. CC BY-NC-ND forbids sharing Adapted Material (a modified chart in a board deck is one) and limits use to purposes "not primarily intended for or directed towards commercial advantage". The paper invites a use its licence bars | Contested: a material barrier | [PolyForm NC 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/); [CC BY-NC-ND 4.0 legal code](https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.en) |
| L2 | Full-automation scenarios (Section 7) | SEC "AI-washing" actions: Delphia ($225,000) and Global Predictions ($175,000), March 2024; Presto Automation (14 January 2025), the first against a reporting company, for claiming its AI removed the need for human order-taking when most orders needed human intervention. An issuer quoting "full automation" from this paper as a plan needs substantiation | Confirmed risk | [Thomson Reuters](https://www.thomsonreuters.com/en/institute/articles/ai-washing-enforcement); [D&O Diary](https://www.dandodiary.com/2025/01/articles/artificial-intelligence/sec-files-ai-washing-enforcement-action-against-restaurant-technology-company/) |
| L3 | Legal and liability costs sit in a_min and c_sec (Definition 3) | Two dated regimes are not mentioned. The EU AI Act's Annex III high-risk obligations apply from 2 December 2027 (Regulation (EU) 2026/1744). The new Product Liability Directive (EU) 2024/2853 covers software and applies to products placed on the market after 9 December 2026 | Gap | [National Law Review](https://natlawreview.com/article/eu-digital-omnibus-ai-enters-force); [Gibson Dunn](https://www.gibsondunn.com/eu-product-liability-directive-responding-to-software-ai-and-complex-supply-chains) |
| L4 | Named-company characterizations (Section 6, Bending Spoons; Section 7.3, monday.com, Palantir, Exzeo, Clear Secure; Section 4.5, CoreWeave) | The computations come from filings, which is fine. Evaluative phrasing ("must keep buying to stand still"; "spent so heavily on selling") and a lower bound (-24.8) quoted next to a reported 115.9 invite misuse in competitive decks | Caveat: rephrase | Paper |
| L5 | Disclosure completeness | No competing-interests statement. The licence reserves commercial use to the author, so readers will ask whether the author sells related services. Appendix E.3 is a placeholder ("to be completed"). Load-bearing numbers (the dip path, the capacities, ITGC costs) come from a companion paper "in preparation" | Gap | Paper, page 1; Appendix E.3; reference list |

**3. What is missing for me to use it**
- **A "Use of this paper" statement**: not investment advice, not a forecast, and how to request commercial permission.
- **Model-based phrasing for every named company.**
- **A competing-interests statement.**

**4. Where it could be misread or misused**
- **Competitor disparagement in sales decks** using the Bending Spoons lower bound.
- **Investor letters quoting "Rule of 155 by 2028".**
- **Earnings-call claims of AI-driven margin** that echo "full automation" without substantiation.

**5. Presentation problems I would flag**
- The reference list prints a raw bibliography key: "(bendingspoons2026prospectus)".
- The companion paper's title is lower-cased ("The economics of ai transformation").
- A placeholder section in a release candidate.

---

## 3. Where the panel disagreed

- **The CFO and the CPO on the decision weight.** The CFO wants the 7 to 13 claim demoted to a sensitivity. The CPO argues that product-led firms buy growth with R&D too, which pushes the weight up. The panel's resolution: report the weight under each attribution (change 2) and stop calling the gap with screening weights a finding.
- **The CEO and the general counsel on named companies.** The CEO finds the Bending Spoons and Palantir examples the most persuasive pages in the paper. The GC wants them kept but rephrased. The resolution: keep them, and standardize the phrasing (change 9).
- **The CHRO and the head of transformation on capacity.** Both accept the speed-limit logic. The CHRO thinks 10% a year is too high under change fatigue; the head of transformation thinks it is too low for light-touch changes. The resolution: define "affected" by depth of change, and report pace at 5, 10 and 20% (change 4).
- **The CIO and the audit chair on AI controls.** The CIO reads Remark 10 as permission for a mixed human and AI design; the audit chair reads it as a warning. Both are right. The resolution: add a guardrail sentence (change 7).

---

## 4. Consolidated view: top 10 changes, ranked by importance

### 1. Add decision rules in the units a finance team budgets in, with one worked firm

*Why.* The paper's results are rules, but they are written as propositions. Executives cannot use what they cannot apply on Monday.

*Where.* A new Section 8.1, "Decision rules for operators" (renumber what follows), referenced from the abstract and the conclusion.

*Proposed text.*
> **Decision rules.** Seven rules follow from the model. Each uses numbers a finance team already has.
> **R1, growth spend.** Keep adding growth spend in a segment while the value of the revenue the last dollar buys exceeds that dollar. In practice, marginal new annual revenue per dollar of selling and marketing, times the value of a dollar of revenue (gross margin times the expected life of a dollar of revenue at the firm's retention, discounted), must exceed one. The Rule of 40 is not this test (Proposition 6).
> **R2, automation with capital.** Automate with capital (owned compute, capitalized builds) only if the operating cost it removes, as a share of revenue, exceeds (growth rate plus depreciation rate) times the capital it adds per dollar of revenue (Corollary 2, Remark 4(c)). At 15% growth and 25% depreciation, $0.10 of capital per dollar of revenue must remove 4 points of cost.
> **R3, own or rent compute.** Own compute only if the vendor's markup exceeds about 20% at 5% market growth, or 60% at 15% (Remark 11).
> **R4, stage.** While gaining share, fund the productivity of selling and retention first; near saturation, fund overhead removal (Corollary 3).
> **R5, controls.** No key financial control should rely only on layers that share one model provider. Keep at least one human layer or a second provider, and budget an IT-general-controls line for every AI application in scope (Proposition 10, Remark 10).
> **R6, acquisitions.** Score an acquisition at the weight X minus its price per dollar of revenue. On the cash Rule of 40, a purchase above one times revenue lowers the properly charged score. Judge it on the annuity basis of Remark 3, over the revenue life implied by retention.
> **R7, pace.** Before launching a program, estimate the probability that an attempt delivers and survives until its savings are sustained. Launch only the waves the scarcest capacity can carry, in order of score gain per unit of that capacity (Proposition 11(d)), and only if the program pays back within the owner's horizon at that probability.

*Analysis to add.* A one-page worked example for the median $1-5B firm-year of 2023-25 in the core panel: growth 14.1%; FCF margin 24.8% before SBC and 9.9% after; GAAP operating margin 6.8%; S&M 28.2%; G&A 12.1%; R&D 23.4%; gross margin 78.2%; SBC 14.8% (panel medians, Appendix A). Show R∞, the surplus, the implied weight under each attribution of change 2, the R2 hurdle and the Table 10 ceiling, all on one page.

### 2. Make the decision-weight result conditional on its attribution, and translate it into payback

*Why.* "7 to 13" is the paper's most quotable number and the most likely to be misused. It treats the median firm's growth as free. Our replication gives 7 to 13 with that baseline, 3 to 6 with a zero baseline, and 2 to 4 if selling must also replace churn. The last range overlaps the screening weights the paper contrasts it with.

*Where.* Abstract; Section 1 (finding two); Section 5.4; Table 2 (rows "Spend-to-excess-growth ratio" and "Implied weight"); Section 8.1 (to become 8.2); Section 9.

*Proposed text (abstract).* Replace "growth spending implies a weight on growth of 7 to 13" with:
> growth spending implies a weight on growth of 7 to 13 if growth up to the median is free, and of 2 to 6 if all growth must be bought.

*Proposed text (Section 5.4, after "roughly 7 to 13").*
> The ratio counts growth in excess of the year's median as the growth that spending buys. If growth with no selling at all is zero, the median ratio is about 1.4 and the implied weight 3 to 6; if selling must also replace about 10% of revenue lost to churn, it is about 1.0 and the weight 2 to 4. The two largest biases of the proxy, the baseline and the share of selling spent on renewals (about $0.13 per dollar of annual recurring revenue in one survey of 305 firms), both raise the ratio. In payback terms, a weight X means that the last dollar of growth spend buys 1/(X - k) dollars of annual revenue; at X = 7 to 13 and a 75% gross margin, the marginal payback on gross profit is 9 to 17 years.

*Analysis to run.*
- Recompute on E2 with three baselines: the year's median; zero; and G_i = ln(NRR) for firms that disclose NRR (Remark 4(b)). Add these as three rows to Table 2.
- Soften Section 8.1 "therefore marks down firms whose growth spending earns more than it costs" to "marks down such firms *when* their marginal returns exceed the cost; whether the typical firm's do depends on the attribution above."

### 3. Lead with a score bridge, and report the basis practitioners use

*Why.* Boards see the score on free cash flow before SBC. The paper's preferred basis turns half of the peer group from passing to failing, and Table 3 does not report the practitioners' basis.

*Where.* Section 4.5; Table 3 (add a "FCF before SBC" block); Section 8.3 (to become 8.4); a new box after the abstract.

*Proposed text (Section 4.5, new second paragraph).*
> Practitioners usually compute the score on free cash flow before SBC. For firms with $1 to 5 billion of prior-year revenue in 2023-25, the median score is 40 on that basis and 23 after deducting SBC; 52% of their firm-years clear 40 before SBC, 40% on the adjusted operating margin, 14% on the GAAP basis and 10% after SBC.

*Analysis to add.* A "score bridge" table for one firm-year and for the $1-5B median, with these rows: company-reported (quarterly, adjusted); annual on adjusted operating margin; annual on FCF before SBC; after SBC; organic (E2); acquisitions charged (annuity; Remark 3); after interest (Proposition 14(c)). Add a one-paragraph KPI definition card that meets SEC Release 33-10751: definition, calculation, why useful, consistency, recast rule.

### 4. Re-ground execution pace, and state its decision implication

*Why.* Four problems. The success probabilities measure different things. The change-capacity grounding uses exits. The central path is about ten times slower than the revealed 2022-24 pace. The paper does not say that its central case implies "do not launch the whole program".

*Where.* Section 7.3 ("Capacity", "Risk", "Embedding", "Ownership"); Table 11; Section 8.2 (to become 8.3); the abstract's execution sentence.

*Proposed text (replacing "These are survey rates: the share of AI proofs of concept that reach production, and the success rate of transformations that meet six conditions.").*
> The central value, 0.54, is one minus the 46% of AI proofs of concept that one 2025 survey found scrapped before production. It measures attrition before production, not durable savings, and so overstates a migration's success. The fast value, 0.80, is the self-reported success rate one 2020 survey found among transformations that met six conditions; the same survey's unconditional rate is 0.30, which we report as slow execution.

*Proposed text (Capacity).* Replace "that layoff rates and single restructurings bracket" with:
> ...; layoff rates (about 1% of employees a month) and single restructurings (6 to 13%) measure exits, a narrower set than employees whose work changes, and one employer survey expects 59 of every 100 workers to need training by 2030, about 12 a year.

*Analyses to run.*
- Add slow execution (success 0.30) as a row of Table 11, not only in the text.
- **Revealed-pace check.** Compare the central and fast intercept paths with 2022-24. The median core firm raised gross margin less G&A by 3.7 points in two years (IQR 0.8 to 7.8) without AI programs. Then either relabel central execution as "slow", or explain why AI process migration is slower than a cost program.
- **Payback and go/no-go.** Compute the program's payback year and NPV at r = 9.34% under each execution case, and the minimum embedding probability at which a whole-company program pays back within five years. Add the sentence: "Under central execution a sponsor with a five-year horizon would not fund the whole program; it would fund the waves with the highest score gain per affected employee."
- **Capacity sensitivity.** Report pace at 5, 10 and 20% of employees a year. Show that "change capacity binds" (Section 8.2) is conditional on the class d values of decision capacity (Φ = 5) and security-review bandwidth, and add build and run engineering capacity as a fifth resource.

### 5. Collapse the horizon ranges to a central case with a tornado; use each firm's own market growth; demote the Rule of 1000

*Why.* "40 to 156 in 2028" cannot be planned on. The lower ends sit below today's top tail, which confuses readers ("the best firms get worse?"). The 2025 anchor's durable and transient split rests on a single 12% market growth.

*Where.* Abstract; Section 1 (the paragraph starting "Combining model and estimates"); Section 7.3 "Ranges"; Table 11; Section 9; Section 7.2 "Second" (the Rule of 1000).

*Proposed text (abstract, replacing the execution and range sentences).*
> Under central assumptions, an exceptional firm captures less than a quarter of its automation program within ten years, and its margin at market growth rises by about 5 points; fast execution captures all of it by 2033 and adds about 16 points. Scores of several hundred are possible only briefly.

(Use the author's recomputed figures; ours is an editorial proposal.)

*Analyses to run.*
- **A central case per horizon**: α = 0.35, μ at the midpoint, central execution, the anchor median intercept under each S&M bound. Add a tornado over μ, α, execution, G, S&M attribution and compute share. Move the full range to a footnote.
- **Re-run the 2025 inversion with G set at each firm's served-market growth.** Use segment forecasts where available, otherwise G = 8, 12 and 20%. Report how the durable share moves; dR∞/dG = 1 - k.
- Move the Rule-of-1000 arithmetic (Proposition 3(d), Corollary 1 examples) to Appendix A, leaving one sentence in Section 7.2.

### 6. Make Table 10 usable for a typical firm, and fix the tax, fee and capital groundings

*Why.* Table 10 is the most board-useful object in the paper, but it describes only a hypothetical fully automated firm, with groundings a CFO will challenge.

*Where.* Section 7.2 ("Taxes, fees and compute"; "The ceiling"); Table 10; Section 8.4 (to become 8.5).

*Proposed text (taxes).*
> The cash tax rate of 15 to 21% runs from the 15% corporate alternative minimum tax, which applies only to corporations whose three-year average adjusted financial statement income exceeds $1 billion, to the 21% federal rate. Most firms with $1 to 5 billion of revenue fall below the minimum tax's threshold, so their cash rate is set by the statute, state taxes (excluded here) and the use of loss carryforwards and credits.

*Proposed text (fees).*
> Fees of 2 to 3% of revenue are those of card-billed revenue; invoiced enterprise revenue pays less, so this is an upper bound.

*Analyses to add.*
- **A row "Typical $1-5B firm today"** with measured cost of revenue, G&A and fee shares, and the gap to each case's ceiling.
- **A k = -0.3 column** (deferred revenue; Remark 4(c)).
- **Compute share as a decision variable.** State that each point of compute share lowers the ceiling by 1 - τ, about 0.82 points. Give the break-even compute share at which full automation leaves the cash score unchanged from today's, for the median $1-5B firm.
- **Security baseline.** Replace the all-industry 0.69% with a technology-sector figure, or bound it with disclosed peer data.

### 7. Ground the accountability floor in disclosed fees and observed control failures, and add a guardrail

*Why.* The bottom-up example understates the direct floor, and its most persuasive grounding, a match with observed adverse-opinion rates, is not used. Remark 10's numbers invite the wrong conclusion.

*Where.* Remark 10; Section 7.2 ("Accountability floor"); Section 8.5 (to become 8.6).

*Proposed text (Remark 10, replacing "Direct audit and Section 404 costs add about 0.14% at this size, for a floor of about 0.24%.").*
> Direct audit and Section 404 costs are larger than this example suggests: Dropbox, with $2.5 billion of revenue, paid its auditor $4.8 million in audit fees for 2024, 0.19% of revenue, and audit fees rise less than proportionally with revenue. We therefore treat 0.5% of revenue as the floor of a $1 billion firm before any AI-specific control cost.

*Proposed text (Remark 10, new sentence).*
> The illustrative human design implies about a 5% annual chance of an undetected material misstatement, the same order as the 5 to 6% of auditor attestations on internal control that were adverse in fiscal 2017 and 2018.

*Proposed text (Section 8.5, guardrail).*
> Remark 10 does not imply that control owners can be replaced. An all-AI design on one provider is cheaper only while misstatement opportunities and the model's common-mode failure rate are low; with twice either, it is the costliest design. And the officers who certify under Sections 302 and 906 remain people.

*Analysis to add.* Scale the ITGC term with agents and tool permissions, not only with applications, and show the floor at 10, 30 and 100 in-scope agents per $1B of revenue.

### 8. Add a "How not to use these numbers" box

*Why.* Every role named a specific misuse, and most of them would appear in a board deck within a quarter of release.

*Where.* A box at the end of Section 1, repeated as the last paragraph of Section 9.

*Proposed text.*
> **How not to use these numbers.**
> (1) The ceilings of Table 10 are upper bounds for a fully automated firm, not targets.
> (2) The horizon ranges are scenario bounds, not forecasts; a company that repeats them makes a forward-looking statement.
> (3) The weight on growth of 7 to 13 depends on how growth is attributed to spending and is not a budgeting weight; use the firm's own marginal returns (rule R1).
> (4) Cross-sectional slopes record choices; they are not any firm's own trade-off.
> (5) The fall in the top of the score distribution since 2016-19 is a description, and it coincides with a rise in the cost of capital that the model also predicts lowers growth.
> (6) Scores for named companies are the author's computations from their filings under stated assumptions, not the companies' measures; lower bounds are lower bounds.
> (7) Nothing here implies that accountable people or control owners can be removed (Proposition 10).

### 9. Fix the licence, add a competing-interests statement, and remove dependence on unpublished work

*Why.* The licence blocks the practitioner use the paper recommends. The missing disclosures will be the first question a GC or journalist asks.

*Where.* Page 1 footnote; Appendix E.3; the reference list; every "the companion paper derives" sentence that supports a number.

*Proposed text (licence).* Either:
> This paper is licensed under CC BY 4.0. The software is licensed under [Apache 2.0, or PolyForm Internal Use 1.0.0], which permits use within any organization.

or keep NC, but add:
> Use of the paper's methods and figures inside an organization, including in internal board and planning materials, is permitted with attribution; [the author grants this permission here].

*Proposed text (competing interests).*
> Competing interests: [state any employment, consulting, advisory or equity interests in software, AI-governance or compliance services; or "none"].

*Other fixes.*
- Complete or delete Appendix E.3.
- Fix "(bendingspoons2026prospectus)" and "The economics of ai transformation".
- For each number taken from the companion paper (the dip path, change capacities, ITGC costs), either include the derivation or label the number "from unpublished work; not reproduced here".

### 10. A plain-language pass and an executive summary

*Why.* A busy executive is lost by the second sentence of the abstract and by "price line" in the title. The operator-relevant content (Sections 6, 7.2, 7.3 and 8) sits behind 25 pages of propositions.

*Where.* Title (optional subtitle), abstract, a new one-page summary after the abstract, and a glossary after Table 12.

*Proposed executive summary (one page, answer-first).*
> **What this paper finds, for operators and boards.**
> 1. The Rule of 40 is a pass mark, not a frontier. Among the best software firms, a point of growth has cost about half a point of margin, not a full point.
> 2. The basis decides the answer. For $1 to 5 billion firms, half pass on free cash flow before stock compensation and one in ten after it.
> 3. Growth bought by acquisition enters the score free. Charged as an annuity, a serial acquirer's 2025 score of 116 falls to 84 to 93.
> 4. Even complete automation caps a mature asset-light firm's cash score at 63 to 88 points for market growth of 5 to 30% (central case); it passes 100 only if its market grows faster than about 42% a year, and the cap moves most with what compute costs.
> 5. Scores far above 100 can last only briefly, because they use up a limited room to gain share.
> 6. Execution, not technology, sets the pace: the capacity to change how people work, the odds that each change sticks, and sponsors who stay.
> 7. Where rivals can copy freely, the durable score is set by what stays scarce: data that renews itself, distribution, licences, trusted accountability.

*Proposed glossary (replacement terms for the main text; keep the symbols in the model sections).*

| Paper term | Plain term for executives |
|---|---|
| price line, iso-score line | trade-off line |
| efficient frontier | best attainable growth and margin combinations |
| margin intercept m0 | margin when growing with the market |
| demand pull λh | growth bought per dollar of selling |
| spend elasticity α | how fast returns to selling fall |
| growth surplus Π | temporary uplift from outgrowing the market |
| saturated score R∞ | durable score |
| score budget, share headroom | limited room to gain share |
| E1 / E2 | reported scores / organic scores |
| marginal q of revenue, X^dyn | value of an extra dollar of revenue |
| accountability floor a_min | cost of being accountable (audit, certification, insurance, required review) |
| full-cost floors c_full | cost of running AI safely |
| common-mode failure | failure shared by every control on the same model or vendor |
| embedded | savings sustained |
| attempt success ϖ, p_emb | chance a change delivers / delivers and sticks |

---

## 5. Further changes raised (not in the top 10)

- **Seat compression** (CPO): add to Table 1 a row "Customers' headcount falls, seat-priced revenue falls: G down", and state that the sign of dG is unknown for seat-priced firms.
- **Common-mode scope** (CIO/CISO): extend Lemma 4(e) beyond model providers to shared tooling (EDR, identity provider, cloud region), citing the July 2024 outage, and price a warm second provider into c_full.
- **Labor-law minimums** (CHRO): state the WARN and EU Directive 98/59/EC minimum timelines as lower bounds on embedding time for workforce-affecting processes.
- **Regulatory dates** (GC): add the EU AI Act Annex III date (2 December 2027) and the Product Liability Directive date (9 December 2026) to Definition 3(ii) and (iv).
- **Competition** (CEO): add one paragraph to Section 3.4 noting that an entrant's transient surplus is drawn from incumbents' share headroom, and what the score budget implies for an incumbent's defensive spending.
- **Leadership hazards** (head of transformation): replace the class d strategy-change hazard (0.15), which drives most of the 0.23 disruption rate, with a stated range and a sensitivity row.
- **Hallucination measurement** (CIO/CISO): note in Table 13 that measured rates vary about tenfold with the judge.
- **Expansion R&D** (CPO): report the Section 5.4 ratio with S&M plus a share of R&D as a robustness row.

---

## Appendix A. Panel computations

All computations use `data/panel.csv` (core sample, SIC 7372, fiscal years 2010-25, the paper's filters already applied) and were run from a scratch script outside the repository. They approximate the paper's statistics and are not E2 estimates.

**Peer statistics, $1-5B prior-year revenue, fiscal 2023-25** (111 firm-years, 42 firms)

| Statistic | Median | Share of firm-years with R ≥ 40 |
|---|---|---|
| Revenue growth | 14.1% | |
| R on FCF before SBC | 40.4 | 51.5% |
| R on adjusted operating margin (operating income + SBC) | 37.7 | 39.6% |
| R on GAAP operating margin | 20.3 | 14.4% |
| R on FCF after SBC | 23.1 | 9.7% |
| SBC / revenue | 14.8% | |
| S&M / revenue | 28.2% | |
| G&A / revenue (p5 5.0%, p10 7.5%) | 12.1% | |
| Gross margin | 78.2% | |

All core firm-years in 2023-25: the median R is 29.1 on FCF before SBC and 15.2 after; the share with R ≥ 40 is 28.7% and 9.4%.

**Spend ratio under alternative zero-spend baselines.** Firm-years not acquisition-flagged, growing faster than the year's median, with lagged S&M share reported; n = 652.

| Baseline for growth that needs no spending | Median ratio, lagged S&M share / (g - baseline) | Implied X at α = 0.45 to 0.25 |
|---|---|---|
| The year's median growth (as in the paper) | 3.16 | 7.0 to 12.7 |
| Zero | 1.40 | 3.1 to 5.6 |
| Minus 10% (selling replaces churn) | 1.03 | 2.3 to 4.1 |

The paper reports 3.3 on E2 with pro forma adjustment. Our 3.16 uses acquisition-flag exclusion only.

**Revealed pace, same firms in fiscal 2022 and 2024** (142 firms; the median of within-firm changes, in points of revenue)

| Line | Median change | p25 | p75 |
|---|---|---|---|
| Gross margin | +1.7 | +0.4 | +3.5 |
| G&A share | -1.6 | -4.6 | -0.1 |
| R&D share | -1.3 | -5.2 | +0.7 |
| S&M share | -3.9 | -9.1 | -1.1 |
| Gross margin less G&A (intercept proxy) | +3.7 | +0.8 | +7.8 |
| Gross margin less G&A and R&D | +6.0 | +0.8 | +12.6 |
| FCF margin after SBC | +9.7 | +1.3 | +23.5 |
| Revenue growth | -9.2 | -20.7 | -1.4 |

For comparison, the paper's intercept paths in Table 11 rise as follows:
- Central execution (low end): +0.6 points by 2028, +2.2 by 2031 and +5.1 by 2036, from 36 at the 2025 anchor.
- Fast execution (high end): +4.8 points by 2028, from 52 at the anchor.

**Payback translation.** At the optimum, σ*/Δ* = α(X - k) (the average ratio) and dσ/dΔ = X - k (the marginal ratio). Payback in years on gross profit is the ratio divided by the gross margin.

**Accountability arithmetic.**
- Dropbox fiscal 2024: audit fees of $4.78M on revenue of $2,548.2M is 0.19%; audit plus audit-related fees of $6.52M is 0.26%.
- Remark 10, three human layers: P_mm = 0.002 + 0.998 x 0.05^3 ≈ 0.00212, times 24 opportunities ≈ 0.051 a year.

## Appendix B. Sources checked (accessed 29 October 2026)

**Rule of 40 practice and markets**
- Bessemer, The Rule of X: https://bvp.com/atlas/the-rule-of-x
- Bain, AI brings headwinds and tailwinds to the Rule of 40: https://www.bain.com/es/insights/ai-brings-headwinds-and-tailwinds-to-the-rule-of-40/
- Blossom Street, Q4 2024 Rule of 40 data in public SaaS: https://blossomstreetventures.medium.com/q4-2024-rule-of-40-data-in-public-saas-d8a7d829ae16
- Palantir Q2 2026 press release: https://www.sec.gov/Archives/edgar/data/0001321655/000132165526000039/a2026q2ex991pressrelease.htm
- Stocktwits on Palantir's 155: https://stocktwits.com/news-articles/markets/equity/palantir-s-rule-of-40-score-hit-155-here-s-the-math-and-why-it-matters-for-software-valuations/cZo5OP3RJER
- Gartner IT spending forecast, 22 April 2026: https://www.gartner.com/en/newsroom/press-releases/2026-04-22-gartner-forecasts-worldwide-it-spending-to-grow-13-point-5-percent-in-2026-totaling-6-point-31-trillion-dollars
- FRED, effective federal funds rate (annual): https://fred.stlouisfed.org/data/BOGZ1FL072052006A
- tech.eu on Lovable: https://tech.eu/2025/07/23/lovable-becomes-fastest-software-company-ever-to-reach-100m-arr/

**Finance and tax**
- Damodaran, cost of capital by industry: https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/wacc.html
- IRS, CAMT simplified method: https://irs.gov/about-irs/new-simplified-method-for-determining-status-for-corporate-alternative-minimum-tax
- Gainsight on the Pacific Crest 2015 survey: https://www.gainsight.com/blog/8-customer-success-takeaways-from-the-2015-pacific-crest-saas-ceo-survey/
- ScaleXP on the Benchmarkit/Aleph 2026 CAC payback: https://www.scalexp.com/?p=129928

**Workforce and change**
- BLS JOLTS: https://www.bls.gov/news.release/jolts.nr0.htm
- UNLEASH on the WEF Future of Jobs 2025: https://www.unleash.ai/artificial-intelligence/5-things-hr-needs-to-know-from-wefs-2025-future-of-jobs-report/
- Accounting Times on Gartner change fatigue: https://www.accountingtimes.com.au/profession/finance-leaders-are-getting-change-management-wrong-gartner-says
- EUR-Lex, collective redundancies: https://eur-lex.europa.eu/EN/legal-content/summary/collective-redundancies-staff-information-and-consultation.html

**Security, reliability and AI costs**
- IANS 2025 security budget benchmark: https://www.ians.com/insights/ciso-leadership/2025-security-budget-benchmark-report
- NIST IR 8547 (final): https://csrc.nist.gov/pubs/ir/8547/final
- Encryption Consulting on IR 8547: https://www.encryptionconsulting.com/nist-ir-8547-2030-2035-action-plan/
- Axios on Parametrix and CrowdStrike: https://www.axios.com/2024/07/24/fortune-500-crowdstrike-outage-impact
- Emergent Mind on the Vectara leaderboard: https://www.emergentmind.com/topics/vectara-s-hallucination-leaderboard
- Gemini 2.0 Flash at 0.7%: https://thedayafterai.squarespace.com/featured/gemini-20-flash-hits-07-hallucination-rate-but-trails-chatgpt-o4-mini-in-reasoning-benchmarks
- SaaStr on ICONIQ 2026: https://saastr.com/the-builders-economy-10-metrics-from-iconiqs-newest-2026-state-of-ai-report
- Epoch AI on inference price trends: https://epoch.ai/data-insights/llm-inference-price-trends
- NBER w34608 (Demirer et al.): https://www.nber.org/papers/w34608

**Transformation outcomes**
- BCG, digital transformation success: https://www.bcg.com/press/29october2020-companies-can-flip-the-odds-of-success-in-digital-transformations-from-30-to-80
- CIO Dive on the S&P Global survey: https://www.ciodive.com/news/AI-project-fail-data-SPGlobal/742590/
- McKinsey, Getting organizational redesign right: https://www.mckinsey.com/capabilities/people-and-organization/our-insights/getting-organizational-redesign-right

**Audit and internal control**
- Dropbox DEF 14A (April 2025): https://www.sec.gov/Archives/edgar/data/1467623/000146762325000047/dbx-20250415.htm
- Dropbox FY2024 results: https://www.silicon.co.uk/press-release/dropbox-announces-fourth-quarter-and-fiscal-2024-results
- Ideagen, S&P 500 audit fees: https://ideagen.com/thought-leadership/blog/audit-fee-trends-of-sp-500
- Accounting Today on Protiviti's SOX survey: https://accountingtoday.com/news/sox-compliance-hours-and-costs-increased
- Audit Analytics, SOX 404 review: https://blog.auditanalytics.com/sox-404-disclosures-a-fifteen-year-review/
- PCAOB GenAI spotlight: https://pcaobus.org/news-events/news-releases/news-release-detail/pcaob-staff-shares-observations-from-outreach-on-use-of-generative-artificial-intelligence-in-audits-and-financial-reporting
- KPMG on SEC Release 33-10751: https://kpmg.com/us/en/frv/reference-library/2020/sec-issues-mda-guidance-kpi-metrics.html

**Legal and licensing**
- PolyForm Noncommercial 1.0.0: https://polyformproject.org/licenses/noncommercial/1.0.0/
- CC BY-NC-ND 4.0 legal code: https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.en
- Thomson Reuters on AI-washing enforcement: https://www.thomsonreuters.com/en/institute/articles/ai-washing-enforcement
- D&O Diary on Presto Automation: https://www.dandodiary.com/2025/01/articles/artificial-intelligence/sec-files-ai-washing-enforcement-action-against-restaurant-technology-company/
- National Law Review on the AI Omnibus: https://natlawreview.com/article/eu-digital-omnibus-ai-enters-force
- Gibson Dunn on the EU Product Liability Directive: https://www.gibsondunn.com/eu-product-liability-directive-responding-to-software-ai-and-complex-supply-chains
