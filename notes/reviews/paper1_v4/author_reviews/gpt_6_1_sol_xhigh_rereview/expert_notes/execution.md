# Independent execution, stress-test and new-business-analysis re-review

Prepared 4 November 2026 (America/Los_Angeles). Scope: main Sections 7–8 and associated abstract/summary/conclusion statements; Supplement S2.7–S2.9, S10, S12.2–S12.3; relevant response rows. This is an independent PDF-based assessment, before any restricted other-review materials. No such materials were read. No repository pipeline, Lean check or committed-output comparison is claimed here.

## Fresh assessment (Part B contribution)

The revision materially improves the distinction between an operating scenario and an empirical prediction. The central score is now given both before and after the cost of transitions; the anchor interval is clearly narrower in scope than the joint input envelope; the threshold is tied to central costs; the cash-payback criterion is distinguished from an investment-value criterion. S10 repeatedly says a numerical search is not a proof and that uniform/log-uniform input laws are assumptions rather than measured distributions. Those are real improvements. Several local statements, however, still exceed their own conditions, and the new S12.2 score path needs a revenue-accounting reconciliation.

### EX-1: Price, quantity and revenue growth are not reconciled in S12.2 (minor, substantive new analysis)

**Locator:** Supplement p66, S12.2, first paragraph and Table S21 notes; main model definition of revenue growth.

The subsection holds the firm's volume and growth as in the fixed-price path while rivals' automation lowers price. Since revenue is price times quantity, its growth obeys d log S = d log p + d log Q. A changing price path cannot coexist with both an unchanged quantity path and unchanged revenue-growth path. The displayed score levels appear to change the margin while keeping the growth component fixed. That can define a useful constant-growth margin counterfactual, but then quantity must adjust; it does not describe the entire price effect on the score of a fixed-volume-path firm.

This does **not** by itself overturn the ranking of automating versus not automating: for two firms with the same price and quantity growth, the growth correction can cancel from the gap. It does prevent interpreting the reported score levels as the stated fixed-volume path without a reconciliation. An illustrative accounting check, not a correction to their actual path, is saved in `scripts/execution_checks.py`: a price falling to 0.71 over 11 years has average log-price growth −3.11 points/year; keeping quantity log-growth 12.9% implies revenue log-growth about 9.79%, not 12.9%.

**Fix:** Explicitly choose which is fixed. Either label the table a constant-revenue-growth margin-only comparison and state the implied quantity adjustment, or retain the quantity path and recompute each year's revenue growth using the actual price path. Report whether the gap, the levels and the qualitative conclusion change. This issue is specific to the new analysis, not evidence that all fixed-price calibration results fail.

### EX-2: Monte Carlo confidence claims do not follow from randomized Latin hypercube sampling (minor)

**Locator:** Supplement p58, S10, “Monte Carlo precision”.

The paper states that an independent-draw share standard error overstates Latin-hypercube error, and calls the percentile confidence intervals obtained from order statistics “distribution-free 95%”. The classical binomial count/order-statistic coverage argument uses independent observations. LHS outputs are dependent; no design-specific theorem or randomization-valid interval is supplied.

An exact counterexample is saved in `scripts/execution_checks.py` / `results/execution_checks.json`. With two randomized-LHS points in two dimensions, let an event be that the coordinates lie in the same half of the unit interval. The estimated share is either 0 or 1 with equal probability, giving variance 0.25. Two independent samples give share variance 0.125. Thus the claimed direction of conservativeness is false in general. This counterexample does not assert that their million-point run is numerically inaccurate or that its headline scenarios change; it shows that the reported confidence justification is insufficient.

**Fix:** Use independent randomized LHS replications, a valid design-specific variance/quantile procedure, or label the iid calculations as approximations rather than guaranteed conservative/distribution-free confidence intervals. Two agreeing seeds do not establish the stated 95% coverage.

### EX-3: Finite completion is still mislabeled in the stress-test table (minor)

**Locator:** Supplement p59, Table S18, “Program still running in 2036 (expected completion year)”; p60, S10 “Other failures”; contrast main p63 and Supplement p24, proof of Proposition 7(e)(iii).

The main text now correctly labels the reported date as when an upper bound reaches the whole program and notes 99% realization in the same rounded year. But Table S18 still calls the statistic an expected completion year, and p60 says fast execution completes the program and that expected completion runs 2032–2087. In the exact divisible recurrence U_w = (1−p)U_(w−1) after remaining mass falls below wave capacity, U_w remains positive at every finite wave. The finite date is an upper-bound crossing, not exact expected completion.

The independent printed-parameter calculation reproduces upper-bound wave 85 versus exact 99%-wave 84 centrally, and waves 72 versus 71 in the fast case. Calendar dates depend on the exact freeze parameters and were not guessed or called repository reproduction. The main rounded-year precision repair is plausible; the supplement's label remains wrong.

**Fix:** Relabel the table quantity and p60 as the upper-bound crossing date, or use a stated 99% completion threshold consistently throughout the table and text.

### EX-4: “Central execution” alone is still an insufficient condition for failing five-year payback (minor wording with substantive logical content)

**Locator:** Main p5, introduction; p64, Section 7.3; compare Supplement p59, ST-3 and Table S18, and main p74.

The paper prints a minimum payback of 4.99 years with central execution and other inputs varied. It therefore cannot conclude without exception that the program fails the five-year test merely “under central execution”. The p5/p64 sentences still do that. The p74 conclusion now correctly says there are a few exceptions, and the abstract correctly locates 7.5 years in a central scenario.

**Fix:** Say “at the central inputs” for the 7.5-year/five-year-failure result. For the fixed-execution sensitivity, retain the 4.99–9.29 range and the exceptions. Do not describe 4.99 as no payback within five years.

### EX-5: The conclusion turns conditional thresholds into necessary technology/capital conditions (minor scope overclaim; could become major if defended as a theorem)

**Locator:** Main p61, Section 7.2 “Three conclusions”; p73, conclusion.

The conclusion says sustained scores above 100 therefore require near-complete automation and negligible capital needs. The model establishes a score formula conditional on costs and capital intensity; it does not identify which technology is necessary to attain a given cost structure. The paper's own negative cash capital extension supplies a direct counterexample to a universal32.5% growth requirement: intercept0.675, k=−0.3 and G=0.26 give a mature score0.675+1.3×0.26=1.013. Main p60 explicitly acknowledges this lower threshold. Nor is negligible positive capital a mathematical necessity: an intercept0.675 and non-deductible k=0.5 give a score1.025 at G=0.70. The latter is a static logical counterexample, not a claim that70% mature software-market growth is realistic.

**Fix:** State that the 32.5% threshold applies at the selected cost structure and k=0, that positive capital raises it and negative cash capital lowers it, and that near-complete automation is the scenario's assumed route to its costs rather than an identified necessary condition. The descriptive observation that such market growth is unusual can remain separate.

### EX-6: The abstract drops the homogeneous-product condition of the entry result (minor)

**Locator:** Main p1, final abstract sentence; contrast main pp2–3,61,74 and Proposition 4.

“With free entry” is the only industry condition retained in the abstract's final sentence, whereas the result is developed for free entry in a homogeneous product market. The abstract's plain language can keep that material condition without mathematics.

**Fix:** “With free entry into a market for the same product…” or another accurate plain-language statement of the homogeneous-product assumption.

## Relevant response audit rows (Part A contribution)

The verdicts below concern what is established from the PDFs and independent printed-assumption calculations. Repository and external-source verification remain separate evidentiary steps.

| ID | Author status | Recommended verdict | Evidence and locator |
|---|---|---|---|
| GPT-M4 | Fixed | Resolved at interpretation level; numeric exit value unverified | Main pp5,64,70 distinguish five-year cash payback from value received in a sale; p64 gives remaining benefit value173% and break-even recovery7.4%. Approximate arithmetic is internally plausible, but exact discounted cash schedule requires code. |
| GPT-M5 | Fixed | Partly resolved | Source transport is now explicitly analogical and scenario-dependent (main pp62–64; Supplement pp9–10,38–39); joint box is supplied, but EX-2 qualifies its precision claims and the calibration is not empirically identified. |
| GPT-4 | Fixed | Partly resolved | Main p63 repaired correctly; Supplement pp59–60 still calls upper-bound crossing an expected completion date. Exact recurrence check saved. |
| GPT-5 | Fixed | Resolved for the stated score-budget issue | Main pp5,61 limits Rule-of-1000 language to market growth software markets have sustained; absolute scores are not bounded for arbitrary G. EX-5 is a related remaining necessity overclaim. |
| GPT-9 | Fixed | Resolved at printed-claim level | Abstract p1, summary p2, introduction p5, Table5 p63, Section7.3 p64 and conclusion p74 now give58 durable and53 during transitions, with separate dip. |
| GPT-19 | Fixed | Resolved as a source-characterization repair | Supplement p9 explicitly says the woe zone created limited value and that setting it to zero is the construction; no longer equates “limited” with empirically zero. Primary BCG source not separately rechecked by this subreview. |
| GPT-20 | Fixed | Resolved as a characterization repair | Main p62 pace bullet and Supplement TableS11 p38 describe cumulative expected training need to2030 as a proxy/analogy, not annual work changed. |
| GPT-21 | Fixed | Partly resolved pending quantitative sensitivity | Need the parent/source reviewer to verify reliability TableS11 details. A scenario label discloses the incompatible-denominator construction; it does not make the combined rate a measured probability. For this execution subreview no claim of source/denominator reconstruction. |
| GPT-22 | Fixed | Resolved as units/framing repair; empirical transport remains scenario | Supplement p9 and TableS11 p39 state successful-run cost, doubling at50% success, multiplying by60% labor share to1.2% revenue. Fixed-performance software tasks do not establish full-enterprise compute floors; paper now labels the range a scenario. |
| GPT-23 | Already handled | Resolved as disclosed limitation, not as identification | Supplement pp9–10 explicitly combines different survey populations and calls all readings analogies; alternative yields39.9%,31.5%,17.4% are given. |
| GPT-24 | Fixed | Partly resolved | Main pp5,7,64 and Supplement pp58–60 provide the joint scenario envelope beside the anchor-only interval. EX-2 affects the numerical-precision confidence claims; the larger scenario uncertainty is now visible. |
| GPT-26 | Fixed | Partly resolved for paper-only exact reproduction | Supplement TableS11 p39 now prints Tpar0.17/0.08/0.42 and S2.7 p9 states cw=rho*Tpar. The exact numerical cashflow integration/terminal-value rules still need repository verification; parent should update if code supplied. |
| GPT-33 | Already handled | Resolved as disclosed scope | Main pp68–69 and Table7 compare maintenance-netted/all/none attribution and state ranking is against the growth engine, not every lever. |
| GPT-37 | Not valid | Accept current arithmetic explanation, old-build adjudication not possible here | Main pp63–64 consistently says58 durable and53 net; TableS18 p59 gives unrounded57.8, so rounding the already-rounded score and dip is not a valid rebuttal. Old build/stored exact net score unavailable to this subreview. |
| ST-1 | Conditional wording supplied | Partly resolved | Abstract p1 central costs/6%; main pp5,7,59–61 state ranges and capital caveats. EX-5 remains in p61/p73 necessity wording. |
| ST-2 | Anchor-only interval relabeled | Resolved on scope; precision claim separately qualified | Abstract p1 says sampling alone; summary p2, main pp5,7,64,74 identify anchor interval; joint40.7–66.7 is clearly scenario-law-dependent on pp2,5,7 and S10. EX-2 is new. |
| ST-3 | Central execution qualifier supplied | Partly resolved | Central execution range4.99–9.29 itself supplies a counterexample; p5/p64 need explicit central-other-input or exception qualifiers (EX-4). |
| ST-4 | Exceptions supplied | Resolved at wording level | Main pp2,5,64 and Supplement pp59–60 now acknowledge a few positive points; S10 reports maximum+0.004 point-years centrally and+11.7 over full box. Code not rerun here. |
| ST-5 | Central execution qualifier/range supplied | Resolved at wording level | Main pp5,63–64,74 and Supplement p60 attach41% to central execution and give4.9–85.0% across stated execution range. |
| ST-6 | Central maintenance qualifier/range supplied | Resolved at wording level | Main pp2,3,68,74 and Supplement p60 state central-maintenance5of6 and sensitivity0–1 growth-engine wins; no universal ranking asserted. |

## S12.3 and decision implications

The cancellation of change capacity from payback while the program runs is plausible in the printed homogeneous proportional-cost model: attempted mass per unit time scales both the benefit-flow sequence and in-flight costs. S12.3 p67 acknowledges that completion before payback breaks the cancellation and reports other execution inputs as important. It is not a general proposition about enterprise funding: fixed startup costs, capacity-dependent costs, process heterogeneity, changing bottlenecks and revenues would defeat the simple cancellation. Its correct role is a conditional mechanism; the measured rank correlations over chosen scenario ranges do not establish which management intervention has the largest causal return.

The most important release sequence from this subreview is: reconcile the S12.2 revenue definition; repair the false LHS precision justification; make completion and five-year-payback language consistent in every location; and restore conditional wording in the conclusion and abstract. None of these PDF findings alone proves the central scenario arithmetic is wrong. Specialist-journal claims of numerical replication still require the pinned code/data, and the results remain a synthesis plus conditional calibration rather than identified business forecasts.

## Own checks and access disclosure (Part C contribution)

Ran `python3 scripts/execution_checks.py`; deterministic exact enumeration and arithmetic; seeds not applicable. Outputs: `results/execution_checks.json`. This demonstrates the LHS counterexample, recurrence threshold distinction, price/revenue identity, printed4.99-year exception, and static positive-capital counterexample. It is explicitly not a run of any repository script and cannot verify the million-draw results or stored outputs. Relevant PDF pages58and60 were also visually inspected after rendering. No restricted reviewers' materials were read.
