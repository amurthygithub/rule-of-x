# Paper 1 v2: round-2 issue log
Filled in as the round-2 reports arrive. Snapshot: notes/reviews/paper1_v2/ (frozen 18:42 UTC−7). Each entry gives the source, severity, issue and planned action. Dispositions stay pending until every report is in.

## Executives panel (Sonnet; r2_panel_executives.md): 24 new findings (5 major, 15 moderate, 4 minor). Round-1 EX status matches the authors' counts (0 resolved, 8 partly, 10 not)
- X2-N1 **(major), no go/no-go rule.** "About 4 years" (M p.54) is the year annual gains pass the annual dip. Cumulative payback is about year 7 undiscounted and about year 8 at 9.34% (reviewer arithmetic, from Table 5), so a sponsor with a 3–5 year horizon would not fund the central program. Action: verify the arithmetic in code, report the crossing year and the cumulative payback year (undiscounted and discounted), and state the implication for hold periods.
- X2-N2 **(major), execution inputs described more optimistically than their sources.** varpi 0.70 is BCG's "created some value" share (win plus worry, 74%), but M p.53 calls it a "survey rate of success". The realized share b̄ 0.67 is McKinsey's figure for successful transformations only. The reviewer's like-for-like illustration gives about 32% by 2036 instead of 41%. Action: (a) relabel varpi as "share of attempts that create some value", not success; (b) state that the calibration target is the product varpi × b̄ ≈ McKinsey's unconditional realized share (0.30 × 0.67 + 0.70 × 0.37 = 0.46), so 0.47 matches it; (c) check the reviewer's 32% claim; if the model gives failed attempts zero value, the product is the right target and 41% stands. Show 0.30 × 0.67 (BCG "win" only) as the pessimistic case in the tornado.
- X2-N3 **(major), levers-by-position not actionable.** At the revealed weight the value columns only rank line sizes; the substantive result depends on the weight, which is unidentified; R&D and cost of revenue are missing; the positions are not $1–5B peers; the conclusion's stage rule conflicts with Table 7 for the stalled firm. Action: cut §7.5 to the proposition and the ratio test with one illustrative table, point to Paper 2's playbook for decisions, and remove or fix the stage rule.
- X2-N4 **(major), no executive entry point.** No summary, glossary, worked median $1–5B firm or typical-firm row; the abstract is jargon-dense. Action: add a one-page executive summary box after the abstract, using the reviewer's draft in r2_panel_executives.md (checked against the paper's macros); add a short glossary in the supplement; add a typical-firm row to Table 4; simplify the abstract's wording within its length limit.
- X2-N5 **(major), no "how not to use these numbers" box.** Board misreads remain: 66 quoted without 55; 31% without its 6% compute and k = 0 conditions; Table 6's 117 and 92; the 5% remote threshold read as a tolerance; "because fast growers became scarcer" stated causally. Action: add the box, using the reviewer's draft, and rephrase the causal sentence as compositional ("the decline reflects fewer fast growers; we do not identify why").
- X2-N8 (moderate): §8.1 re-imports the unidentified weight through a 20-point penalty example at the 3.02 ratio. Action: restate it conditionally at the X evaluation points, or drop it.
- X2-N11 (moderate): Table 4 has no deferred-revenue (k < 0) column; for annual-upfront billers the 31% threshold is about 24% (reviewer arithmetic, not recomputed). Action: compute a k < 0 row in calibrate_horizons and report it.
- X2-N13 (moderate): the accountability-floor numbers do not match the paper's own sources. Direct audit and 404 cost of 0.14% ($1.4M per $1B) is below KPMG's $2.3M average SOX program budget alone. "15 applications" becomes about 34 at the $80k reference line rather than the $205k invoice line. Action: reconcile the direct-cost line with the KPMG survey (scope and firm size), and report the application count on both the reference and the invoice line.
- X2-N14 (moderate): the 5% remote threshold is grounded on adverse 404(b) incidence, which is not the probability of an undetected misstatement. The human-only design passes at 4.98% against 5%, a knife edge. Action: call ε̄ a scenario parameter (class d) with a plausibility argument rather than a measurement; disclose the knife edge; keep 1% and 5% side by side, and show that the conclusions drawn (no all-AI single-provider design passes; at least one human layer) hold at both.
- X2-EX9: the response overstates EX-9. The title-page footnote lacks the "firms may apply the ideas" sentence, which appears only in Table 9 (p.75). Action: add the sentence to the footnote and correct the response.
- Remaining moderate and minor items: see the report. Open practitioner items EX-6 (typical-firm row, k < 0), EX-11 (seat compression) and EX-15 (competition) need a sentence or a row each.

## Finance and accounting referee (Fable; r2_finance_accounting.md): minor revision. Round 1: 24 findings tracked, 14 resolved, 8 partly, 2 not done. New: 14 findings (0 major, 3 moderate, 11 minor). Numbers checked: 41 (36 matched, 3 partly, 2 not)
**Verified correct at the source:**
- Cash-score basis (ASC 230-10-45-17(c),(d)); the Table S6 bridge reproduces cell for cell.
- Bending Spoons: no double charge; Q2 2026 figures match the 6-K exhibits; the material-weakness sentence is verbatim.
- AS 2201 A7 and .03; Item 308(a)(3),(b).
- Audit Analytics rates of 4.6%, 5.8% and 4.8%.
- §168(k) as amended by P.L. 119-21 §70301, the (k)(7) election out, the ADS exclusion and Notice 2026-11.
- Owned-compute thresholds 16.5/49.5 and 33/74.
- R3 and R5.

**Findings:**
- F2-1 (moderate), interest income. The "before interest" bridge removes interest paid only; interest income stays in operating cash flow. Interest income is material for the debt-free, cash-rich firms in the 2023–25 top tail and the anchor (Palantir 2025 InvestmentIncomeInterest $229.2M, 5.1% of revenue; 6.9% in 2024).
  - Action: retrieve the interest-income elements (InvestmentIncomeInterest and related) and add a "before net interest" row.
  - Relabel the existing row "before interest paid".
  - Restate the anchor net of after-tax interest income, or report its sensitivity.
  - Retrieving the elements needs an SEC frames pull through the author's browser.
- F2-2 (moderate), direct audit and SOX cost of 0.14% at $1B. It has no Table S7 row and is below the KPMG 2025 survey ($2.3M average; $1.5–2.7M by size). Size-matched, the floor is 0.34–0.56%, not 0.23%, and the 0.5% band end is reached at 1 to 9 applications, not 15. Same issue as X2-N13.
  - Action: re-ground the direct-cost line on KPMG by size, add the Table S7 row, and recompute the floor and the application counts.
- F2-3 (moderate), the 5% threshold. It is presented as class b, but the inference runs through illustrative parameters: the human design passes at 4.98% against 5%. "No all-AI design on one provider passes" holds only if the AI common-mode rate is at least 1 − 0.95^(1/24) = 0.0021 per opportunity. It holds at 0.005 and fails at 0.002. Same issue as X2-N14.
  - Action: reclassify ε̄ as class d, state the common-mode condition, and report both thresholds.
- F2-4 (minor), the X = 2.5/5/9 placeholders in §6. These are leftover XBOUNDS macros with no motivation. Action: replace them with the sign-flip statement at X = k_acq between 1.7 and 3.2.
- F2-5 (minor), Bending Spoons basis labels.
  - Intro and §8.3 chain GAAP 115.9 → 105.0 → "87 to 114 charged" as if on one basis.
  - The cash rows are before SBC (3.3% in H1 2026), while the panel is after SBC.
  - "The convention decides the sign" needs "in the year of purchase".
  - Action: relabel, add an SBC note, and qualify the sentence.
- F2-other (minor):
  - Interest paid for 2023–25 is in the F-1 ("Interests paid") and should replace interest expense. This needs the browser, because WebFetch cannot read past about 124k characters.
  - §8.5: "attest to that assessment" against AS 2201.03, and 18 U.S.C. §1350 is missing.
  - WACC 9.34% is a sector average, below the firm's 9.625% notes and its 25% hurdle. State this.
  - CAMT is cited as a 15% floor, but it applies only above $1B AFSI.
  - The T(0) text says "all firm-years", while the code uses g ≥ 0.
  - §7.2 conflates electing out of §168(k) (bars about 20%/54%) with ψ = 0 (33%/74%).

## Risk, audit and regulatory panel (Sonnet; r2_panel_risk_audit_regulatory.md): minor-to-moderate revision, no re-estimation. Round 1 (RA-1 to RA-6): 2 resolved, 3 partly, 1 not resolved (RA-3); the response's "Fixed" for RA-2 and RA-5 is downgraded to partly. New: 22 findings (2 high, 13 medium, 7 low)
Verified at primary sources: AS 2201 A7, Item 308(a)(3), SR 26-2, OCC 2026-13, Reg. (EU) 2026/1744 Recital 40 dates, Release 33-10751, C&DI, NIST IR 8547, the Bending Spoons and Palantir figures, Kim et al., KPMG.
- RR-N1 **(high)**, the cross-type common-mode term p^cc is 0 in every number, so the headline design sits on a knife edge.
  - At 5%, one human over one AI stops being admissible once p^cc exceeds about 0.0008.
  - At p^cc = 0.002 the cheapest design is two humans over one AI ($1.40M); from 0.0021 up nothing is admissible at 5%.
  - If a human misses 10% of AI-missed items, the one-over-one design fails at 5.9%.
  - The dollar floor barely moves (0.090% → 0.145%); the identity of the cheapest design does.
  - Action: add break-evens in p^cc and the human miss rate to Remark 6, add an automation-bias parameter or state it as excluded, and stop presenting a single "cheapest design" as a finding.
- RR-N2 **(high)**, authorship. The Introduction says the paper "was written by its human author", which contradicts Table S8 and B.1: AI agents wrote the text, code, proofs and protocol appendix. Action: replace with accurate wording (the author posed the questions, made the decisions in Appendix B and reviewed the manuscript; AI agents drafted text, code and proofs under her direction). Author to approve the wording.
- RR-RA3, still missing: the "Use in filings" paragraph (Reg G, Item 10(e), 2022 C&DIs, Release 33-10751, the IPO safe harbor). The panel supplies verified text. Action: add it to §8.3, verified by the editor.
- RR-N3 to N7, the 5% threshold:
  - The Audit Analytics 4.6% and 5.8% figures are two editions stale. The panel reports later editions with 6.8%, 4.7%, 6.2% and 7.6% for FY2019 to FY2022 and 3.8% for FY2025 large accelerated filers; the FY2019 figure conflicts with the 4.8% cited. Must be verified at the source before use.
  - The evidence is firm-level, but the constraint is per control objective: 5% firm-level spread over about 10 objectives is about 0.5% each.
  - The lead agent moved the central value from 1% to 5% after results were visible, and B.4 does not list this.
  - "No design on one provider passes" is an assumption of the example (p^cm 0.005 against a 0.0021 ceiling), not a finding.
  - The event behind π is undefined and misread against AS 2201.
  - Action (with F2-3 and X2-N14):
    - make ε̄ a scenario parameter (class d) with no central value chosen on results;
    - report both 1% and 5%, and the per-objective reading;
    - define the event;
    - state the p^cm condition;
    - disclose the 1%→5% switch in B.4;
    - verify the edition figures at source before citing any.
- RR-N8 to N10, ICFR practice:
  - Only the 16 hours per control in the ITGC retest is KPMG-sourced; the 10 controls and $150/h are assumptions (relabel).
  - External audit effort for AI-performed controls (AS 2201 B28–B31, AS 1105, AS 2601) is omitted, and C^acct is design-invariant by assumption.
  - The policy and third-party channels are not priced.
  - Action: label the assumptions, and add the omitted channels and audit effort as stated limitations.
- RR-N11 (medium): the 0.14% direct audit cost is unsourced and probably low. Same as F2-2 and X2-N13.
- RR-N12 to N15, protocol accuracy:
  - B.1 says the agents had "no access" to each other's outputs, but they were only told not to read them (correct the wording).
  - Model identifiers: give exact IDs (claude-opus-5-5, claude-fable-5-1, claude-sonnet-5-5), tool permissions and transcript retention.
  - Say what the author personally checked, and that no human specialist reviewed the legal and accounting statements.
  - Competing interests declined next to an "Independent researcher" label (author's call; flagged by RA-6 in round 1 and again here).
- RR-N16 to N22 (low):
  - The $350k vs $204,672 ITGC inconsistency.
  - Table S7/S9 labels overstate verification.
  - The AI compliance line is not scoped against the AI Act.
  - The SR 26-2 caveat appears only in the supplement.
  - §8.5 filer-status wording and the section 906 citation.
  - CAMT treated as a floor.
  - Palantir and Bending Spoons precision points.
  - Round-1 housekeeping.
- Not checked at a primary source: EUR-Lex operative articles, the Bending Spoons full risk factor, the end of AS 2201, ASC 805/230, AS 1105/2601, the Barnes Group letter, and Parasuraman and Manzey (2010).

## IO and AI economics referee (Fable; r2_io_ai.md): minor revision. Round 1 (R4, FI): 9 resolved, 20 partly, 5 not resolved. New: 20 findings (3 major, 8 moderate, 9 minor). Citations checked: 31 (one mischaracterized: a new use of Demirer et al.). All headline numbers reproduce from calibrate_horizons.py.
- IO2-1 **(major), pass-through implemented wrongly.**
  - A pass-through rate (Ganapati 70%, the DMA study) is used where the paper's own Lemma S2 needs an elasticity.
  - The price cut's effect on the revenue denominator is ignored.
  - On the paper's own scenario values, the threshold with pass-through is about 32% (both φ), not 36.3%/38.5%. So the intro's "36% if half pass through" is wrong in number and description.
  - The retention rule 1 − φ(1 − H) is undefined and uncited in P1.
  - Excluding non-discretionary savings contradicts Prop 4(d).
  - Action: re-derive the pass-through mapping from Lemma S2 (elasticity, with the denominator effect), define and cite the retention rule, include all savings consistently, recompute, and fix the intro and abstract.
- IO2-2 **(major), Demirer et al. misused again.** The paper cites them for pass-through "near one between providers of the same model" (§7.2, Table S7), but the source has no pass-through analysis and documents persistent price dispersion (CV up to 1.7). Action: remove the claim.
- IO2-3 **(major), compute-share range.** The 30% upper end does not follow from the stated value test. It comes from an undocumented factor of 0.5 (CC_VALUE_TEST_CAP = s_L × 0.5). Under the stated test the range is 27–77%, not 27–51%, and the 40% high-compute case is not infeasible. Action: either justify the factor (and reconcile it with the no-review ceiling) or use the stated test. Recompute the abstract range and the high-compute case.
- IO2-4 (moderate), compute path.
  - The path (12/8/5%) is driven by two unstated class-d values (κ_front = 1/3; ω_H = 0.6/0.4/0.25).
  - The sourced price decline does not bind after 2028, and the 3–18× rise is not an input.
  - The 31% headline at 2025 prices is not a date on the path (6% is reached only around 2034).
  - "No measured analog" remains next to ICONIQ's 11%.
  - Action: state the drivers and their class, say what the 2025-price headline means, and fix the wording.
- IO2-5 (moderate), internal inconsistencies.
  - The "highest measured error rates" sensitivity still uses human catch rates (36% → about 39%).
  - Compute is charged on 60% labor but error losses on 30% (using 60% moves the threshold to 32.5%).
  - §7.3 says transitions cost "two years of savings", but the code uses 1.25. At 2 years the dip is 4–5 points and the crossing about 5.6 years.
  - The fast-execution dip of 5.1 is computed on the dropped range basis.
  - Action: make text and code agree. Decide the transition cost in years from its source, then recompute the dip and the crossing.
- IO2-other:
  - The 2036 tornado's largest swing comes from an unmotivated 5–30% G band.
  - The capability-feasibility assumption is unstated.
  - Missing: a decomposition of G* (taxes are 18.0 of the 31.0 points), and the NPV of the central program (reviewer: PV of gains ≈ 3.3 × PV of the dip; the program completes in 2042).
  - The free-entry sentence lacks the homogeneous-product qualifier.
  - Uncited: Babina et al., Sutton, Weyl–Fabinger, Vaccaro, Agrawal–Gans–Goldfarb, Gans–Goldfarb O-ring, METR TH1.1.

## Theory referee (Fable; r2_theory.md): minor revision. Round 1: 46 resolved, 5 partly (declared), 0 unresolved. New: 18 findings (2 errors, 1 gap, 3 overclaims, 4 unclear, 8 minor). verify_theory 189/189; all changed results re-derived and correct; the positioning and the narrowed contribution list are fair
- TH2-1 (error, wording): the abstract double counts kG ("intercept equal to the margin at market growth … plus market growth net of the capital it requires"). Fix to "the margin intercept, plus …".
- TH2-2 (error, low impact): the proof of Cor. 4(c) (S p.17) claims X-improving at saturation, which fails for processes that change λ or k. State the condition δm0 − Gδk + (X−k)δG ≥ 0.
- TH2-3 (unclear): §7.3 cites Prop 7(e)(iii), proved only for ν_D = 0, and quotes ν_D values from the companion paper. Fix: set ν_D = 0 in the pace formula, or extend (iii); remove the residue.
- TH2-4 (overclaim): the abstract and conclusion say "Under free entry, the limit is set by what stays scarce, not by what is automated", which contradicts Prop 4(c)-(d): scarcity decides who captures the savings, not whether they raise the score. Also, "requires near-complete automation" overstates Cor. 4(a). Fix both.
- TH2-5 (gap/unclear): hypothesis (H) is pure existence. State the two immediate HJB consequences (trivial when (m0−kG)/(r−G) ≤ k; otherwise no no-spend region and the terminal condition is forced). §7.2 applies the pre-tax Prop 4(d) with an after-tax margin term; add a one-line after-tax extension.
- TH2-minor:
  - a duplicated sentence in §3.6;
  - δ vs δ_K;
  - ν^R units differ between the model and Table S7;
  - α 0.35 (central path) vs 0.3 (Table 7);
  - "acts like a cut in capacity" wording;
  - "exceeds the screening weights when its revenue multiple does" is loose;
  - the script docstring run time;
  - cite Marschak–Andrews (1944);
  - one Belo et al. range is unverifiable.

## Investment management panel (Sonnet; r2_panel_investment_management.md): major revision of the empirical sections; not usable as a screen or factor. Round 1: 3 resolved (IM-1, IM-3, IM-6), 3 partly (IM-2, IM-4, IM-5). New: 12 findings (3 high, 6 medium, 3 low). Scripts in scratchpad/r2_im/.
- IM2-N1 **(high), T(20%) contradicts "no detectable change".** T(20%) GAAP fell 10.2 points, the same size as the P95 decline. The percentile interval [−15.1, +1.1] includes zero, but the basic [−21.5, −5.4], normal and BC intervals exclude it (basic p = 0.004). The P90 margin of firms growing 20% or more fell; that of slower firms did not. §7.4's inference that supply of growth opportunity binds rests on this. Action: report every interval type for T(20%); state that the frontier at 20% growth fell under three of four interval types; revisit the §7.4 inference and the "no detectable change" sentence.
- IM2-N2 **(high), the composition decomposition is unstable.** Across 4 to 40 bins and both directions, composition runs from −3 to −18 and the within-cell term from −8.8 to +5.9; the bootstrap cannot separate them. Every quantile fell (P10 −19.9, P50 −6.9, P95 −11.9). A cyclical or IPO-window reading is untested: first-year firm-years went from 83 in 2020–22 to 18 in 2023–25. Action: present the decomposition as not robust to binning; drop "because fast growers became scarcer" as an explanation and state the facts; add the full-distribution shift and the IPO-cohort count as competing readings.
- IM2-N6 **(high), the anchor has no interval on the intercept.** It rests on 13 firm-years from 7 firms; the intercept median is 42.0 with a 90% firm-cluster interval of [34.1, 52.4]. That maps to about 62–72 for 2036 and 49–66 for 2028 (reviewer reconstruction). Action: carry the anchor interval through calibrate_horizons and report intervals on the central path in the abstract and table.
- IM2-N7 (medium), the S&M bound. The headline uses "all S&M buys growth", yet the paper's own maintenance evidence contradicts it: below-median growers spend 25.1% of revenue on S&M. The 2036 score is 66.2 (all S&M), 59.5 (maintenance-netted) and 55.7 (no S&M). Action: report all three and choose the central value on stated grounds, not on the upper bound.
- IM2-N8 (medium): the anchor's cash margin sits 13.4 points above its GAAP margin, and the top-tail cash–GAAP gap rose from 3.7 to 13.0 points. Interest income and deferred revenue are possible drivers. Action: the same SEC pull as F2-1 (interest income, plus contract liabilities and deferred revenue).
- IM2-N5/N4 (medium), inference statements.
  - "GAAP decline survives Holm at 10% across interval types" is wrong: p runs from 0.054 to 0.208.
  - The cash decline fails Holm even at 10% (0.154–0.336).
  - Two of the five Holm survivors are tests against a slope of −1, and two are tautological margin-gap tests.
  - The abstract's pooled slope averages a documented break (−0.22 before 2020, −0.60 after), and its sign fails Holm.
  - Action: correct every inference sentence against the table, flag the tautological tests, and report the break in the abstract rather than the pooled slope.
- IM2-N3 (medium): "recovered in 2025" holds in E1 only; excluding acquisition years the recovery is 2.8 points, not 9.3. Action: qualify the statement.
- IM2-N9 (medium): the spend ratio is 2.50 under random pairing against 3.02 actual, and §8.1's "20 points below" illustration uses the gross ratio, where the net ratio of 0.99 implies about 0. Action: restate §8.1 (same as X2-N8).
- IM2-screen: the conclusion's advice to "use the Rule of 40 to screen firms" is unsupported. There are no returns, holdout or point-in-time tests; rank autocorrelation is 0.68 and top-quintile turnover 43%. Action: remove the screening advice or state that the paper does not test it.
- IM2-N10/N11 (low): the assumptions register still lists α as class c; SIC codes are current rather than point-in-time; the $50M universe screen uses latest-filed frames revenue. Action: fix the register and state the remaining items as limitations.

## Econometrics referee (Fable; r2_econometrics.md): minor revision; no numbers change.

**Reproduction.** Everything reproduces from the shipped panel and code:
- all 5,821 point estimates (to 1e-9);
- all 1,862 bootstrap summaries across 14 blocks;
- Holm and Romano–Wolf adjustments;
- every text number traced, and the 51 CLAIMS.

**Round-1 status.**
- R3: 17 resolved, 1 partly (R3-11, a data-section sentence), 1 not done (R3-18).
- FE: 7 resolved, 4 partly.
- IM tests: 7 resolved, 2 partly, 1 not done (holdout).

**New findings:** 0 major, 5 moderate, 9 minor. D-1 and D-2 are applied consistently. D-3 is applied in the tables but not in three headline sentences.

**Findings.**
- E2-1 (moderate): "No detectable change in the best margins at a given growth rate" (5.10(v), intro, conclusion) fails D-3. T(0) after SBC is −3.3 [−6.4, −0.2] under E1 and excludes zero in 2 of 4 views. Together with IM2-N1 (T(20%) GAAP), this sentence goes.
  - Action: replace it with the facts by growth band and basis.
- E2-2 (moderate): §5.2 says the GAAP P95 decline "survives at a familywise level of 10%", but its own Holm range runs to 0.208 (basic). The CLAIMS test silently excludes the basic type. The cash decline (Holm 0.15–0.34, Romano–Wolf 0.15) survives at neither level, yet the abstract and summary report 11.9 and 12.7 symmetrically. Same as IM2-N5.
  - Action: correct §5.2.
  - Report the cash decline as not surviving familywise correction.
  - Make the CLAIMS test include all interval types.
  - Make the abstract asymmetric where the evidence is.
- E2-3 (moderate): inside draws, the bootstrap uses a 10-firm-year grid-cell minimum for Ψ_χ, against 30 in the sample. For E2's primary slope, 16.8% (GAAP) and 13.0% (cash) of draws fall below the sample rule, so by the paper's own 5% rule E2 would have no interval. The numerical effect is immaterial: the defined-draw interval is [−0.505, −0.080] against the published [−0.508, −0.068].
  - Action: disclose this in §5.1 and report the defined-draw interval as a check.
- E2-4 (moderate): 5.10(i) states "The GAAP slope steepened after 2020" as a fact, but the E2 interval includes zero (−0.66 to +0.02; 3 of 4 views).
  - Action: qualify it as holding in 3 of 4 views.
- E2-5 (moderate): the abstract's anchor conclusion is outside both familywise families. Added to family B, its Holm p is 0.006 (normal), 0.096 (percentile) and 0.030 (basic).
  - Action: report these, and add it to the family. Also, the D-2 protocol entry omits that the Ψ_χ slopes on the v1 sample (−0.20/−0.16) were known from the round-1 report when the object was chosen; disclose this.
- E2-minor:
  - The within-firm lead regressions are shown in 2 of 4 views; add the bounds.
  - §8.1 reuses 3.02 as α(X−k) (same as X2-N8 and IM2-N9).
  - "The 2016–19 gap behaves the same way" overstates it.
  - R3-18 is still open.
  - Romano–Wolf is max-t with fixed scaling, so describe it accurately.
  - "3.8 expected" should be 3.6.
  - DFL uses Hazen quantiles against linear quantiles elsewhere (a 0.1-point mismatch).
  - R2, R5 and the frames inputs are presented honestly as partial.

## Investors and bankers panel (Sonnet; r2_panel_investors_bankers.md)
**Verdict.** Better and safer to quote, but still not a pricing tool. The round-1 IB status agrees with the authors' except for the IB-2 decline reason.
**Round-1 points.** 30 checked: 8 resolved, 8 partly, 14 not.
**New findings.** 25 (7 high, 13 medium, 5 low).

- **IB2-N1/N2 (high): price line and score-to-multiple bridge.**
  - "Price line" reads as a valuation line, and the iso-score ≠ iso-value caveat is buried.
  - Declining the bridge "for lack of price data" does not hold: Lemma 5 gives an analytical mapping. On the reviewer's computation, a Rule-of-40 score of 40 is worth 12.1×, 11.7×, 8.3× or 5.2× revenue at r = 9.34%, depending on the mix.
  - Action: add a short analytical table of iso-score points at different values, built from Lemma 5 in code. Say plainly in the main text that no score-to-multiple mapping is estimated. Rename or define "price line" at first use.
- **IB2-N3/N4 (high): decision weight and its leftovers.**
  - The decision weight is shown at one discount rate. On the paper's example, the weight is 14.6, 10.0, 5.8, 3.7, 2.1 and 1.35 at r = 9.34, 10, 12, 15, 22 and 31%.
  - The withdrawn weight re-enters in four places: §8.1's "20 points below"; Table 7's X̂−k = 11 proxy, which contradicts the X ∈ {2.5, 5, 9} rule; the conclusion's "accept a lower Rule-of-40 score"; and the worked example's "5 to 15".
  - Action: show the weight by discount rate, and remove or restate all four (same as X2-N8, IM2-N9, E2-minor).
- **IB2-N5 (high): abstract headline basis.**
  - "P95 fell 11.9 to 12.7" names no basis; both figures are after SBC. On FCF before SBC the fall is −8.6.
  - The abstract also omits the familywise caveat and the 2025 partial recovery.
  - Action: name the basis, add the before-SBC figure, and add the caveats (same as E2-2, IM2-N5, IM2-N3).
- **IB2-N6 (high): Bending Spoons is stale.**
  - The case stops at the 13 Aug results, yet 6-Ks through 29 Oct are listed as used.
  - Missing: the SACE term loan; the term loan B add-ons ($1.25B and €395M, with rating upgrades); Miro (about 2.3× ARR); Berkshire's $330M placement (about 4%); the $1.25B 9.625% and €500M 8.625% notes "to fund future acquisitions".
  - The 15.5% interest ratio predates all of these. The charge rate sits below the issuer's marginal coupon. The organic-score range omits amortization.
  - Action: update the case from the 6-Ks through 29 Oct, verified at the SEC; add a run-rate interest note; charge at the marginal coupon as a sensitivity.
- **IB2-N7/N8 (high): owner types and pace.**
  - P1 has no PE or permanent-capital analysis, and "a sponsor's faster decisions change nothing" is likely wrong in practice.
  - The success re-grounding mixes definitions (same as X2-N2), and the move from 23% to 41% has no bridge in the text.
  - Action: point to P2 for owner analysis and fix or remove the sponsor sentence. Add a pace bridge: the change in success rate, in the realized share, and in T_emb, each separately. Add an owner-led execution row.
- **IB2-other (medium/low):**
  - abstract slope and "fast growers scarcer" claims (same as IM2-N2, E2-4);
  - the "how not to use" box (same as X2-N5);
  - sample framing, and naming the anchor firms;
  - stewardship: competing interests, licence terms, AI panel labelling (same as RR-N12 to N15).
- **Limits:** F-1/424B4 truncation; pro forma revenue and the AOL, Eventbrite and Vimeo prices unverified.
