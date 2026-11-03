# Errors and hallucinations produced in this research, and what caught them

This log covers errors made by the agents and by the lead agent, and records which safeguard caught each one. It is the source for the protocol appendix (spec Section 23.3). Counts are updated as the project proceeds.

## A. Part I (28 to 29 Oct)

### A1. Data errors (caught by referee 2, the financial economist, and referee 3, the econometrician)
- Mixed restatement vintages. Growth compared a restated year with an originally reported one, so AppLovin's 2023 growth appeared as −35% instead of +17%. Fixed by rebuilding the panel as first reported.
- Wrong revenue element selected for some firms (for example Manhattan Associates). Fixed by taking the largest revenue element.
- Revenue scale error for one firm (IonQ). Dropped.
- Duplicate registrants (holding company and operating subsidiary). Seven dropped.
- Missing capital expenditure treated as zero. Now set to missing.
- Goodwill instants misaligned with fiscal year ends. Realigned.

### A2. Methodological errors (caught by the referee panel)
- The headline frontier statistic depended on sample size. Replaced by sample-size-invariant statistics.
- A regression slope was presented as an estimate of α, although it is not identified. α is now treated as a calibration range.
- The calibration intercept was infeasible for the best firms. Replaced by a firm-by-firm inversion.
- The free-entry example violated the model's own assumption (r > G). Re-parameterized.

### A3. Factual and citation errors (caught by the audit agents and referees)
- An unsupported "75 to 80%" software margin attributed to ICONIQ. Removed.
- Epoch's price-decline figure misstated. Corrected to 9 to 900× a year.
- Bain's Rule of 30 overstated as a recommendation. It is a temporary concession.
- Bessemer said to "report" weights it in fact recommends. Corrected.
- A claim that depreciation of owned compute does not enter operating margin. It does; only EBITDA excludes it.
- A citation of Aghion et al. for the zero-profit logic. The lead agent instructed the theory agent to add it; verification did not support it, and it was removed.

### A4. Errors in the second audit (33 findings: 4 errors, 13 inconsistencies, 5 overclaims, 6 unsupported claims, 5 style issues)
- Stale 2036 ranges in the introduction.
- Baidu named as part of the broad sample, which it is not.
- An untraceable "88 to 99.6%" figure. Replaced by a scripted 96.5 to 99.8%.
- Bibliography count stated as 73 instead of 71.
- Overclaims: "7 or more" stated as a lower bound; "did not change" stated from non-rejection; "mostly durable" resting on one bound; an AI-compute explanation for a capital-intensity gap that the firms involved do not support.

### A5. A reversed finding
- The first draft found a flat cross-sectional frontier. After the data were rebuilt, the upper decile slopes down by 0.37 to 0.46.

### A6. Lead-agent code errors (caught by the lead agent's own checks)
- The first arXiv packaging script silently dropped every table. Caught by compiling the package and comparing its text with the main PDF.

## B. Parts II and III (29 Oct)

### B1. References the lead agent suggested from memory that verification corrected or rejected (caught by literature agents)
- Kaplan and Minton (2012): the lead agent suggested the Journal of Financial Economics. The paper is in the International Review of Finance.
- Myers and Majd (1990): could not be verified. Replaced.
- Argote and Epple (1990): abstract not reachable. Replaced by Argote, Beckman and Epple (1990) and Darr et al. (1995).
- Shapiro and Varian: suggested as 1998; catalogues give 1999.
- METR: the title and doubling time in the lead agent's brief were imprecise. The paper covers software tasks; the doubling time is 207 days (95% CI 166 to 240).
- Gundlach et al.: the price decline applies at fixed performance, not to frontier models.
- The EU AI Act: the brief implied a numeric human-oversight floor. The Act sets none.
- Becker and Murphy (1992): the brief attributed the n(n−1)/2 coordination form to it. Not confirmed there.
- O*NET counts: "about 2,000" DWAs is in fact 2,087; the "41 GWAs" figure is unconfirmed.
- Sultan, Farley and Lehmann (1990): the Bass means come only from secondary sources and are for consumer durables.
- Gordon and Loeb (2002): its 1/e bound holds only for two classes of breach function.
- Widely quoted figures flagged or rejected: "70% of transformations fail" (no evidence found); "95% of generative-AI pilots fail" (weak methodology); "75 to 80% of software cost is maintenance" (a prior estimate cited by the source, not a finding).
- Running counts: Part II bibliography 151 entries, 5 + 2 corrected, 9 + 1 dropped. The modernization and reliability agents are pending.

### B1a. Engine defaults the lead agent set that the reliability evidence contradicted (caught by the reliability-evidence agent)
- Retrieval-grounded hallucination rate: default 1% per output; evidence 1.5 to 20%, and 17 to 34% for legal research tools. New default 5%.
- Base misbehavior rate per autonomous task: default 0.01%; evidence 0.4 to 1%, higher where scoring can be gamed. New default 0.1%, with the range carried.
- Expert reviewer catch rate: default 90%; evidence 45 to 85%. New default 65%.
- Widely repeated claims the agent found unsupported: retrieval makes outputs hallucination-free; hallucination is now about 1 to 3%; newer models hallucinate less; a human reviewer catches the errors; a 96% blackmail rate in a red-team test is a deployment rate; passing tests means production-ready; a measured total cost of AI errors exists.

### B1b. Conflict-of-interest risk (caught by the product theorist)
- The product section's worked example priced AI resolutions from a single vendor's public list, and that vendor employs the author. Replaced by a range across several vendors.

### B1c. Researcher degrees of freedom (caught by the lead agent on review)
- The core theorist changed the inputs of a worked example (integration cost and horizon) after a parameter update, explicitly so that the example's conclusion would survive. Reverted: inputs are now set from independent sources, the result is reported as it falls, and the break-even values are shown.
- The backtest's first estimates, at a review-time ratio of 0.8, were null. The sourced value 0.575 was already in the audited parameter file before any estimate was made; the first run used 0.8 because the engine defaults had not yet been linked to that file. With the link in place the result is significant. Because both values lie inside the sourced range (0.37 to 1.19), the result is reported as a sweep over the range, with the order of events disclosed. The model beats exposure out of sample only for ratios below about 0.66 (the lowest 35% of the range), and its incremental coefficient does not survive a Bonferroni correction across 20 tests.
- The backtest's text numbers were typed by hand. They are now generated by the script.

### B1d. Accounting and tax errors (caught by the accounting agent)
- The theory and the engine used a five-year straight-line tax deduction for software development (ψ = 0.787). That was the 2022 to 2024 regime. Since 2025, domestic R&E is deducted when incurred under §174A (ψ = 1), and foreign R&E is amortized over 15 years. The engine-builder brief had marked the statute "not verified".
- The engine tied tax deductibility to book capitalization. The two are independent.
- The score-path proposition capitalized the whole build, amortized it from date 0, and booked severance and write-offs at cutover. All four conflict with ASC 350-40 (as amended by ASU 2025-06), ASC 420 and ASC 712.
- The parameter file applied the 36-month tax life for off-the-shelf software to developed software.
- The aggregation result's accountability floor omitted expected misstatement, which does not vanish under common-mode failure.

### B1e. Specification and brief errors (caught by the corporate-finance theorist)
- The lead agent's brief listed a bibliography key (Axelson et al. 2013) that existed in no bibliography file.
- The spec claimed that a short holding period caps the payback of the waves an owner will fund. This holds only if buyers capitalize none of the recent run-rate.
- A 30-year family horizon with no terminal value makes family owners artificially impatient. Replaced by an infinite horizon.
- Survey hurdle rates are annual, but the examples first used them as continuous rates. Converted.

### B1f. Compounding convention (caught by the corporate-finance theorist)
- The engine's default discount rate (9.34%, Damodaran's annual WACC) and the survey hurdle rates were used as continuously compounded rates, although the sources state annual rates. Converted with ln(1 + r). After the conversion, two conclusions in the ownership section changed: the sponsor's owned-capacity switch now pays when buyers credit half of recent run-rate savings, and a pressured public firm now ranks cost-out first.
- Citation precision: Axelson et al.'s 5.2× is total debt (net debt 5.1×); Gompers et al. 2016's 22% is the average target IRR (median 25%). Only the 12 to 17× band of the Silverpeak exit-multiple report could be confirmed, not its 14.9× average.

### B1g. Verified, not errors
- The 2016 cross-section in a third-party repository had an undocumented vintage. The lead agent verified it against BLS's published May 2016 tables: all 737 occupations match, with identical sums of employment and mean wage.
- Units and missing values in the Anthropic Economic Index. The verbatim release documentation, retrieved with a SHA-256 check, confirms that the pipeline's treatment was right: task time without AI in hours, time with AI in minutes, and missing cells meaning not published rather than zero.

### B2. Data issues (caught by the data agent)
- O*NET 31.0 renumbered every IWA and DWA ID without saying so in its release notes. Links were rebuilt by exact title match.
- BLS custom industry codes collided when truncated, inflating some industries' occupation sums by up to 1.89×. Fixed.
- 21 process steps were initially matched to the wrong activity (for example a SaaS renewal matched to "Sell agricultural products"). Fixed by hand.
- Three keyword false positives in the EU high-risk flags. Removed.

### B3. Errors in the specification itself (caught by the theorists)
- Supermodularity alone does not imply all-or-nothing automation of a process.
- The volume threshold ignored augmentation and fixed costs.
- An optimal parallel-run length needs a failure-detection time.
- Growth does not enter the value test for capital-for-labor substitution, only the cash-score test.
- Notation clashes: reserved symbols were reused in the spec, and the two theory sections used different symbols for the review share and the success probability.

### B4. Coordination errors
- The author's message at 07:56 arrived as an interrupt and stopped six agents mid-task. They were restarted at 07:58 on the author's instruction.

### B1h. Engine logic: regulated status inferred from the reliability target (caught by the core theorist, decided by the lead agent)
- The engine marked a step as regulated only when its reliability target was at least 99%. Relaxing the target to 98.8% therefore removed a 1.5× build multiplier from a SOX-relevant accounts-payable process. Regulated status now comes from the process and data class, not from the target.

### B1i. Scope and synchronization errors (caught by the engine builder's paper-sync tests and by the lead agent)
- ICFR scope was set by function. That made every HR process regulated, recruiting included, and left Procure to pay out because procurement is a separate function. Replaced by process-level and step-level scope grounded in PCAOB AS 2201 and ITGCs.
- The labor section's worked example used the voided invoice figures ($920k build) and a stale engine value for maintenance staffing (0.25 instead of the register's 0.48).
- The worked example and the engine modeled survivor quits differently, a $12k gap in structural costs. Aligned to the engine's per-wave model.
- Hard-coded wages in the engine (economics.py, impute.py) and in the invoice example came from an older OEWS vintage ($133,080 for software developers, against $135,980 in May 2025). They are being replaced with reads from the data file, and a test now guards against hard-coded wages.
- The lead agent's recorded conclusion on the backtest, that neither placebo was significant, was overtaken by the extended placebo. With the official SOC crosswalk, the pre-COVID placebo is significant (t = 2.2). The conclusion was revised to 'consistent with the feasibility filters, partly reflecting a trend that predates generative AI'.
- Engine nondeterminism, caught by the engine builder's regression run: a unit's regulated class was chosen with max(set(...)), so ties broke in hash order and results depended on PYTHONHASHSEED. The small firm's plan value moved by 1% across processes. Fixed with deterministic tie-breaking: by strictness of class, on the lead agent's instruction. A test now reruns under a different seed.
- A hard-coded $1,380 seat price in the synthetic firm was replaced by the sourced default ($1,050). The synthetic firm's product revenue path moved about 31%, with no change in sign of any conclusion.
- Stale vendor facts, caught by the author: Intercom had been renamed Fin and acquired by Salesforce (completed 10 Sep 2026). Ownership and price were re-verified at the vendor pages and in Salesforce's release, and the two vendors' common ownership is now noted wherever they are treated as competitors.
- Secondary-source errors caught against primary filings in the Bending Spoons case:
  - Wikipedia gave Tractive at $900M; the 6-K gives an enterprise value of $759M.
  - The acquirer draft said post-IPO performance was unknown, but Q2 2026 results were filed on 13 Aug 2026.
  - The F-1's "no bonds to date" was overtaken by the senior secured notes priced on 28 Oct 2026.
  - The accounting theorist corrected the acquirer section's reading of the cutover-risk result: cutover date, not only congestion, raises material-weakness risk.

### B1j. Findings revised by the estimand change (organic frontier, E2)
- With acquired growth removed, two of Paper 1's original findings do not hold for the organic frontier. The cash-basis size gradient (about −6 points per tenfold revenue) and the cash-basis steepening after 2020 appear only in reported scores.
- The upper-tail slope steepens from about −0.46 to −0.59 on the GAAP basis.
- The calibration anchor used an E1 cut-off while excluding flagged years. That mix is being made consistent. Under E2 the anchor's median growth surplus changes sign (6.7 to −0.8), so the transient-surplus statements are being re-derived.

### B1k. Round-1 review corrections to B1j (29 Oct, from the two econometrics referees, Opus and Fable)
- B1j is withdrawn as stated. Its "changes" are not robust:
  - The E1–E2 contrasts exclude zero only under 90% percentile intervals. Basic and bias-corrected intervals include zero, and none of about 32 contrasts survives Holm (best adjusted p 0.66).
  - E2 adjusts only 59 of the 469 acquisition-affected firm-years and drops the rest. Restoring the dropped years with imputed organic growth returns the GAAP slope (−0.45 to −0.48) and the cash size gradient (−4.8 to −5.3) to near their E1 values, so the differences reflect which years were dropped.
  - The anchor's move from 6.7 to −0.8 is well inside a firm-cluster interval of about [−16, +16].
  - The −0.59 slope is an IRLS approximation; the exact quantile-regression value is −0.564.
- The lead agent had reported these changes to the author as findings. The paper will now present E1, E2 and the imputation bounds together. A model-facing claim stands only if it holds under all of them (author decision D-3).

### B1l. Clock
- **Mixed clocks in the agent log (found 29 Oct, 13:58 UTC−7).** The entries from 13:08 onward had been written in the author's reported time zone (UTC−4), while every earlier entry and notes/estimand_notes.md use the session clock (UTC−7). The lead agent then briefly relabeled the whole log as UTC−4, which was also wrong. Checking against the platform's UTC timestamps (for example, the review panels started at 19:45Z, which is 12:46 UTC−7) settled it: the log now states UTC−7 throughout, and the late entries have been converted. Protocol times must come from the platform timestamps, not from a clock tool's local zone.

### B1m. Overstated timing claim for D-2 (found 29 Oct, 16:3x UTC−7, by the P1 editor)
- At 13:53 the lead agent told the author that the frontier-object choice was fixed "before the rebuilt sample produces any numbers". In fact, the sample-audit agent's superseded IRLS test run had printed v3 local-quantile slopes and a familywise result at 13:39. Neither the author nor the lead agent had seen them, and no Ψ_χ estimate existed. The revision plan and the protocol appendix now state this precise version.

### B1n. An unverified statistic passed on from a summarizing fetch (29 Oct, about 18:20 UTC−7)
- The lead agent read the Audit Analytics Seventeen-Year Review through a fetch tool that summarizes pages with a small model. It passed the 4.6% adverse rate (fiscal 2020) and a 7.1% rate for accelerated filers to the engine and editor agents. The editor could not find 7.1% at the source, so it was not used, and the engine agent was told to remove it. The 4.6% (and the Eighteen-Year Review's 5.8% for fiscal 2021) were verified at the source. Lesson: a statistic read through a summarizer is a lead to check, not a source.

### B1o. A result-driven change of a central value, not disclosed (found 2 Nov by the round-2 risk panel)
- On 29 Oct (about 18:20 UTC−7) the lead agent moved the central remote threshold ε̄ of the ICFR floor from 1% to 5%. It did so after seeing that the reference all-human design failed at 1% in the example, and grounded the change on firm-level adverse-attestation rates. Two reviewers (finance on Fable, risk on Sonnet) and the executive panel show three problems with that change:
  - the evidence is firm-level, while the constraint is per control objective;
  - the human design passes at 5% by 0.02 points;
  - the change was not listed among choices made after results were seen.
- Correction: ε̄ becomes a scenario parameter with both values reported and no central value picked on results, and the switch is disclosed in B.4.

### B1p. Round-2 findings on sourcing and inputs (2 Nov 2026)
- **Bib note overstated use.** The bendingspoons2026sixk note listed the Airtable, Miro, term loan, Berkshire and notes 6-Ks as used and "read in the author's browser … 29 October", but the v2 case stopped at the 13 Aug results (IB2-N6). Correction: the 6-Ks were retrieved on sec.gov on 2 Nov, the case was updated from their text, and the note was rewritten.
- **Undocumented factor.** The compute-share value test carried a factor of 0.5 (CC_VALUE_TEST_CAP) with no documented source (IO2-3). Correction: the test is applied as stated; the range moves from 27–51% to 28–78%.
- **Text–code mismatches.**
  - Error losses were charged on 30% of revenue against 60% for compute, and no source was found for 30%. Correction: 60%; G* moves from 31.0 to 32.5%.
  - The text said transitions cost "two years of savings", while the code used 1.25 (IO2-5). Correction: 1.25 years, per the register.
- **Size mismatch.** The direct audit and SOX cost used the S&P 500 fee ratio and a 2009 SEC median for a \$1B firm, below KPMG's own survey (X2-N13, F2-2, RR-N11). Correction: KPMG's under-\$5B program budget plus the Audit Analytics accelerated-filer average audit fee (FY2022, read at source). The S&P 500 ratio is kept as the low bound.
- **Moved source.** The KPMG 2025 SOX survey PDF returns 404 at kpmg.com as of 2 Nov 2026. It is now cited at its archived copy of 18 Mar 2026.
