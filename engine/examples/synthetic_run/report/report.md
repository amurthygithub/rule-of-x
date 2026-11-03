# AI transformation plan: Synthetic Software Co (fictional)

Engine autofrontier 0.2.0. Ownership regime: public. Scenario: central. Seed 20261029. Input tier reached: 4.

> This report is decision support, not a decision. It is produced by a model whose limits, validation record and the decisions it leaves to people are described in MODEL_RISK.md of the engine.

How to read the numbers. Results that depend on scenario parameters (grounding class d: no measurement exists) are given as ranges: P10 to P90 over the Monte Carlo, which draws the firm's uncertain data and every class b and d parameter over its range, or the low and high ends of the parameter. Tables of individual processes show the planning case, in which those parameters sit at their central scenario values. The assumptions section lists every class d parameter.

Data quality: inputs reached Tier 4. The P10 to P90 range of plan value is 1.5 times its median; the remaining spread comes mainly from class d scenario parameters, which more firm data cannot remove.

## 1. Executive summary

- **Value of the plan**: $235.0M to $2.2B (P10 to P90; median $1.3B). The expected value in the worst 5 percent of outcomes is $19.3M. Chance of a loss: 1%. Chance of reaching 80% of the planning-case value: 33%.
- **Scope**: 24 processes and workstreams change mode over 6 waves after Wave 0, affecting about 1,649 FTE and removing about 1,212 FTE of work by the final year (planning case, at today's volumes the residual organization has 2,389 FTE of 3,222).
- **Rule of 40 (cash)**: today 17.5%; in the final plan year 18.7% to 28.5% (P10 to P90). The transition dip in the planning case is -16.0 points on a cash basis and -15.8 points on a GAAP basis, lasting 1 and 1 years.
- **Robustness**: across 17 scenarios the recommended plan's largest regret is $214.0M; the minimax-regret plan is the capability slow plan.

Top recommendations:

1. **Start with Wave 0: measure before you automate.** Inventory and classify the data of every system, and run process mining and time studies on 18 processes where better data is worth more than it costs. Wave 0 costs about $1.3M and takes about 3 months. (Source: core prop:tasks-granularity; spec 24.9.)
2. **Automate the highest-value processes first, integrating their data before automating.** The five largest are Sales: other work, stream 10 ($347.8M), Product and engineering: other work, stream 12 ($216.3M), Executive and strategy: other work, stream 2 ($197.2M), Product and engineering: other work, stream 5 ($196.5M), Product and engineering: other work, stream 9 ($158.1M), planning case values. 5 of them raise data readiness first. Robustness: positive in 83% of draws. (Source: core prop:tasks-transition, prop:tasks-readiness; ext prop:ext-waves.)
3. **Move Service desk toward a two-part tariff as seats compress.** Migration value -$483.2M to $2.5B across the scenario values of the concession, cost, success and seat elasticity; it pays in 67% of those scenarios. Robustness: positive in 67% of draws. (Source: prop:prod-migrate; prop:prod-seats.)
4. **Protect the path from junior to senior work.** Junior production work falls by more than half in 3 functions while review and sign-off stay senior. Keep junior roles in review rotations and training. (Source: notes/modern_theory_map.md change 6.)

## 2. Vision: target operating model and frontier shift

Share of spend that is technically feasible, permissible, preferred and economical to move to AI modes: today 86%, 86%, 80%, 76%; in plan year 3 at the best readiness 95%, 95%, 86%, 84%. The economical universe is worth $306.2M a year in plan year 3 (ext prop:ext-universe; planning case).

Part I frontier shift at the end of the plan (planning case, first order, core prop:tasks-aggregate): change in cost-of-revenue labor -0.60% of revenue, compute 0.00%, other operating cost -8.81% (G&A -3.61%, maintenance R&D -1.68%, maintenance S&M -3.51%), capital intensity 0.00%, growth-spend saving 18.3% (worth 1.72 points of score at the firm's weight, exact, against 2.31% of revenue in cash); industry pass-through rate 50% on every unit-cost saving the rivals make, margins at the post-cut price (Part I round 2: elasticity 0.37 at today's unit cost of 75% of price; the firm's dollar share of a replicated saving, 62%, cor:ext-game-engine(a), values the plan in dollars and does not enter the score). Change in the Rule-of-40 score R*: 7.4 points; at the firm's own growth weight: 7.4 points. R* moves from 27.9% to 34.1%.

Full-automation ceiling with run costs (spec 22): maintenance 0.02%, security 0.01%, ancillary 0.03% and the error floor 0.64% of revenue; accountability floor a_min 3.00% (prop:acct-amin for financial-reporting processes). Ceiling R_max 76.7% without and 76.1% with these terms, at the firm's current compute share. At Part I's compute share at full automation for 2036 (5.0% of revenue, a scenario path) the ceiling is 77.6% without and 77.1% with these terms.
Without people the error floor is evaluated at the review that remains (prop:tasks-cerr(c); Part I lem:fullcost(c)): 0.64% of revenue with no review, the ceiling's convention because the measured catch rates are human reviewers', and 0.43% with one AI review layer on another provider that shares the producing model's errors with probability 0.30 (a scenario value: P(the second model also errs) is not measured; only the agreement given a joint error, 0.60, is). The expected common-mode cost of provider events adds 0.12% (2.00 events a year after change controls; ext notes 4.8). With both, the ceiling without people is 76.0% at the current compute share and 77.0% at Part I's.
Accountability floor as an ICFR constraint (prop:acct-amin, def:acct-admissible; Part I prop:amin): a control design is admissible only if no in-scope objective is left with more than a remote chance a year of a material misstatement that is not prevented or detected (24 opportunities a year). No standard sets the remote threshold, and it has no central value here: the floor is shown at 1% and at 5% a year. At 1% no design with the available layer types is admissible: each type's common-mode floor alone exceeds the threshold, so only another layer type or better ITGCs would help (with the illustrative layer parameters; the firm's own control-testing evidence replaces them). At 5% the cheapest admissible design is 3 human layers (5.0% a year) (it stays admissible up to a cross-type common mode p_cc of 0.00001 per opportunity); human layers alone: 3 human; residual expected consequence $510k a year. The designs are conditional on the illustrative layer parameters. The direct cost common to every design is $3.0M a year (0.08% of revenue: the KPMG 2025 SOX program budget of the firm's revenue class, $1.5M, plus the accelerated-filer average audit fee, $1.5M); 0.08% with the S&P 500 fee ratio and 0.19% with the large-accelerated-filer fee. The single-number ceiling below uses the 5% design (a setting, not a central value). The residual expected consequence of a material misstatement is reported, not traded against cost; a cheaper inadmissible design is a material weakness, not an option.

### Levers by position and setup

Position (lem:playbook-calib, market growth (input); observed spend optimal): growth 17.0%, growth spend 12.6% (netted S&M basis; maintenance S&M 25.7%), G&A 20.5%, maintenance R&D 8.0%, cost-of-revenue labor 15.8%; calibrated weight X_hat 6.6, zero-spend growth G_i 10.0%, demand pull ell 0.130. Each lever is valued at a common 10% change in its line (prop:playbook-rank(a)), in points of the owner's score:

| regime | X_o | growth engine | demand pull | G&A | maintenance R&D | cost of revenue | 1 point of retention (other scale) | X_dagger_0 vs G&A (distance) | levers excluded |
|---|---|---|---|---|---|---|---|---|---|
| public | 3.98 | 0.60 | 1.91 | 2.05 | 0.80 | 0.99 | 3.40 | 9.02 (-5.04) | 4 |
| private family | 5.00 | 0.88 | 2.77 | 2.05 | 0.80 | 0.99 | 4.43 | 9.02 (-4.02) | 4 |
| pe | 2.55 | 0.28 | 0.88 | 2.05 | 0.80 | 0.99 | 1.98 | 9.02 (-6.47) | 4 |
| vc | 3.49 | 0.48 | 1.53 | 2.05 | 0.80 | 0.99 | 2.92 | 9.02 (-5.53) | 4 |
| hybrid | 4.42 | 0.72 | 2.27 | 2.05 | 0.80 | 0.99 | 3.85 | 9.02 (-4.60) | 4 |
| permanent capital | 1.40 | 0.08 | 0.25 | 2.05 | 0.80 | 0.99 | 0.82 | 9.02 (-7.63) | 4 |

Growth-spend basis (Paper 1, author decisions 4 and 7): netted is central. On the maintenance-netted basis only S&M above a maintenance base of 25.7% buys growth: growth spend is 12.6% of revenue and the maintenance share of S&M, 25.7%, is a cost line like overhead. At the weight the firm's own spending reveals the growth engine is not ahead of G&A on that basis; on the bounds it is ahead of G&A if all S&M buys growth (38.4%) and not ahead of it if none does.

Binding constraint. Position: S&M, the line with the largest gap to the top decile of operating margin among firms growing 10% to 20% (Paper 1 Table tab:gap). Setup: decision bandwidth is the scarcest capacity in the first plan year (118% used), and reliability: detection is the gate that binds automation across the most in-house hours.

The ranking compares only the four levers valued at the same proportion (growth engine, G&A, maintenance R&D, cost of revenue; prop:playbook-rank(b)); demand pull values the growth engine another way, and a point of retention is on another scale. Durability: G&A, maintenance R&D, retention and cost of revenue at given demand raise the long-run score; both growth-engine values vanish as the firm's share approaches its ceiling. The excluded levers and their rules are in report.json (lever_map).

Owning compute rather than renting it (Part I rem:owncompute) raises the cash ceiling only if the vendor's markup exceeds 30.0% at market growth 10.0% (capital 3.0 per dollar a year of compute, servers' tax deductibility psi 1.00); at psi = 0 the bar would be 48.6%.

The weight on growth is not identified by the data (Paper 1 decision D-1), so recommendations that depend on its level are shown at X = 2.5, 5.0, 9.0 (finance.X_eval_points (Papers 1 and 2 evaluation points; not estimates)):

| X | top lever | growth engine above G&A | largest price per $ of acquired revenue (full charge / annuity / user cost) |
|---|---|---|---|
| 2.5 | overhead | no | 2.50 / n/a / n/a |
| 5.0 | overhead | no | 5.00 / n/a / n/a |
| 9.0 | overhead | no | 9.00 / n/a / n/a |

No recommendation in this table changes sign between the points. Outside the points: growth engine above overhead (X^ddagger_0) flips at X = 9.02, above the highest point; AI product dilution pays (break-even weight) flips at X = 0.57, below the lowest point. Ratio tests against the revealed spend weight ((X_o - k)/(X_hat - k)) do not depend on the level.

## 3. Product strategy

**Service desk** ($475.2M, seat pricing). Seat revenue at risk when customers automate the seat holders' work: $32.1M to $276.1M at full adoption over seat elasticity 0.25 to 1.00 and exposure 27% to 58% (customer occupations (occ_exposure.csv: Eloundou beta, Tomlinson applicability)). Seat losses peak about 7.7 years out with consumer-durables diffusion and 3.6 years with fast diffusion (prop:prod-seats).
An agent that does the work prices at $1.66 per outcome, 17% of the customer's net saving and 8.2% of in-house cost, capped by AI-native entrants (prop:prod-price). Rent per outcome $1.26: data $0.87, workflow $0.17, switching $0.22. Agent gross margin 76%. Under concentrated model supply the price is $2.06.
Vendor list prices per outcome range from $0.50 to $2.00 (params.yaml, list prices).
Cannibalization: the seat margin per unit of work is $0.24; launching now pays against an entry hazard; replacement cost 5.0% of the launch gain (prop:prod-cannibal).
Model sourcing at 511.9M outcomes a year: own; the own-model test passes in the long run (prop:prod-model).
Pricing migration (prop:prod-migrate; conditional on scenario costs): usage: threshold seat-loss rate 0.98%, migrate now, value -$149.3M to $2.4B (pays in 67% of scenarios); two-part: threshold seat-loss rate 0.52%, migrate now, value -$483.2M to $2.5B (pays in 67% of scenarios); hybrid: threshold seat-loss rate 0.51%, migrate now, value -$650.7M to $1.3B (pays in 62% of scenarios).

**IT asset management** ($233.3M, seat pricing). Seat revenue at risk when customers automate the seat holders' work: $12.3M to $153.6M at full adoption over seat elasticity 0.25 to 1.00 and exposure 21% to 66% (customer occupations (occ_exposure.csv: Eloundou beta, Tomlinson applicability)). Seat losses peak about 7.6 years out with consumer-durables diffusion and 3.5 years with fast diffusion (prop:prod-seats).
Pricing migration (prop:prod-migrate; conditional on scenario costs): usage: threshold seat-loss rate 0.98%, migrate in 0.5 years, value -$225.3M to $1.3B (pays in 67% of scenarios); two-part: threshold seat-loss rate 0.52%, migrate now, value -$237.7M to $1.4B (pays in 67% of scenarios); hybrid: threshold seat-loss rate 0.51%, migrate now, value -$85.5M to $726.3M (pays in 67% of scenarios).

**Analytics add-on** ($155.5M, usage pricing). Seat revenue at risk when customers automate the seat holders' work: $0.00 to $0.00 at full adoption over seat elasticity 0.25 to 1.00 and exposure 25% to 55% (customer occupations (occ_exposure.csv: Eloundou beta, Tomlinson applicability)). Seat losses peak about 7.7 years out with consumer-durables diffusion and 3.6 years with fast diffusion (prop:prod-seats).

Feature portfolio within 55 engineer-years (prop:prod-portfolio): Resolution agent ($429.1M at the firm's weight, $408.8M at the screening weight), Agent copilot ($105.5M at the firm's weight, $63.3M at the screening weight), Asset discovery agent ($72.1M at the firm's weight, $67.7M at the screening weight), Natural-language analytics ($57.6M at the firm's weight, $51.3M at the screening weight).
At the growth-weight evaluation points (finance.X_eval_points (Papers 1 and 2 evaluation points; not estimates)): X = 2.5: Agent copilot, Asset discovery agent, Natural-language analytics, Resolution agent; X = 5.0: Agent copilot, Asset discovery agent, Natural-language analytics, Resolution agent; X = 9.0: Agent copilot, Asset discovery agent, Natural-language analytics, Resolution agent. The chosen set is the same at every point. The ranking of features changes between points.
AI product gross margins cross the subscription margin of 73% around 2030 (fit without a cost floor) or 2033 (fit with a floor); the data do not identify the pass-through (prop:prod-margin).

## 4. Roadmap and score path

**Wave 0: measurement** (2027): cost $1.3M, 3 months. systems and data inventory (firm (38 systems)); data classification (public, internal, confidential, restricted) (firm (38 systems)); process mining or event logs and time study (P08); process mining or event logs and time study (F02::residual3); process mining or event logs and time study (F02::residual5); process mining or event logs and time study (F02::residual6) and more.
**Wave 1** (2027): 3 processes (0 integrate data first, 0 pilot first), one-time cost $5.0M, dual running $0.00 a year while it lasts, NPV $121.1M, cash payback 2.0 years from the wave's start, mean probability that an attempt creates some value 84%. Depends on: Wave 0.
**Wave 2** (2028): 5 processes (5 integrate data first, 0 pilot first), one-time cost $12.9M, dual running $7.1M a year while it lasts, NPV $755.8M, cash payback 2.0 years from the wave's start, mean probability that an attempt creates some value 92%. Depends on: Wave 0, data integration of F04::residual10, data integration of F01::residual2, data integration of P08 and more.
**Wave 3** (2029): 4 processes (4 integrate data first, 0 pilot first), one-time cost $10.6M, dual running $6.5M a year while it lasts, NPV $612.0M, cash payback 2.0 years from the wave's start, mean probability that an attempt creates some value 96%. Depends on: Wave 0, data integration of F02::residual12, data integration of F02::residual5, data integration of F02::residual10 and more.
**Wave 4** (2030): 4 processes (4 integrate data first, 0 pilot first), one-time cost $9.8M, dual running $7.3M a year while it lasts, NPV $449.1M, cash payback 2.0 years from the wave's start, mean probability that an attempt creates some value 97%. Depends on: Wave 0, data integration of F02::residual9, data integration of F11::residual4, data integration of F07::residual10 and more.
**Wave 5** (2031): 4 processes (4 integrate data first, 0 pilot first), one-time cost $10.9M, dual running $7.8M a year while it lasts, NPV $402.0M, cash payback 2.0 years from the wave's start, mean probability that an attempt creates some value 97%. Depends on: Wave 0, data integration of F03::residual4, data integration of F03::residual3, data integration of F15::residual1 and more.
**Wave 6** (2032): 4 processes (4 integrate data first, 0 pilot first), one-time cost $11.2M, dual running $9.0M a year while it lasts, NPV $341.2M, cash payback 2.0 years from the wave's start, mean probability that an attempt creates some value 96%. Depends on: Wave 0, data integration of F01::residual1, data integration of F03::residual5, data integration of F04::residual5 and more.

Processes in the plan (planning case):

| start | process | modes | data first | FTE removed | one-time cost | saving a year | parallel run (yr) | success | value |
|---|---|---|---|---|---|---|---|---|---|
| 2027 | Product and engineering: other work, stream 3 | augmented 1 | no | 20 | $1.9M | $3.6M | 0.25 | 86% | $48.6M |
| 2027 | Sales: other work, stream 11 | augmented 1 | no | 15 | $1.8M | $3.1M | 0.25 | 79% | $38.0M |
| 2027 | Product and engineering: other work, stream 7 | augmented 1 | no | 14 | $1.2M | $2.5M | 0.25 | 88% | $34.6M |
| 2028 | Sales: other work, stream 10 | automated 1 | yes | 31 | $3.8M | $25.4M | 0.05 | 90% | $347.8M |
| 2028 | Executive and strategy: other work, stream 2 | automated 6, augmented 6 | yes | 21 | $3.2M | $14.6M | 0.05 | 89% | $197.2M |
| 2028 | Lead to close | augmented 4, eliminated 2 | yes | 73 | $3.3M | $9.5M | 0.05 | 91% | $125.3M |
| 2028 | Sales: other work, stream 9 | automated 1, outsourced 1 | yes | 10 | $1.1M | $3.0M | 0.05 | 91% | $43.0M |
| 2028 | Product and engineering: other work, stream 6 | automated 2, augmented 2, outsourced 2 | yes | 12 | $1.4M | $2.9M | 0.05 | 96% | $42.5M |
| 2029 | Product and engineering: other work, stream 12 | automated 1 | yes | 95 | $2.9M | $18.2M | 0.05 | 96% | $216.3M |
| 2029 | Product and engineering: other work, stream 5 | automated 1 | yes | 83 | $2.8M | $16.4M | 0.05 | 97% | $196.5M |
| 2029 | Product and engineering: other work, stream 10 | automated 1, augmented 1, outsourced 1 | yes | 51 | $1.8M | $9.3M | 0.05 | 97% | $111.4M |
| 2029 | Legal: other work, stream 1 | automated 8, augmented 5, outsourced 14, eliminated 2 | yes | 45 | $3.1M | $6.8M | 0.17 | 94% | $87.8M |
| 2030 | Product and engineering: other work, stream 9 | automated 1 | yes | 91 | $2.6M | $16.0M | 0.05 | 97% | $158.1M |
| 2030 | Finance and accounting: other work, stream 4 | automated 3, augmented 1, outsourced 1, eliminated 1 | yes | 50 | $2.8M | $13.4M | 0.17 | 96% | $131.8M |
| 2030 | Professional services: other work, stream 10 | automated 1 | yes | 76 | $2.4M | $8.8M | 0.05 | 97% | $85.3M |
| 2030 | Finance and accounting: other work, stream 3 | automated 3, augmented 2, outsourced 7, eliminated 2 | yes | 45 | $2.0M | $7.4M | 0.17 | 97% | $73.8M |
| 2031 | Marketing: other work, stream 4 | automated 1, augmented 2, outsourced 3, eliminated 1 | yes | 63 | $2.6M | $14.8M | 0.05 | 96% | $118.7M |
| 2031 | Marketing: other work, stream 3 | automated 4, augmented 1, outsourced 2, eliminated 1 | yes | 65 | $2.7M | $14.3M | 0.05 | 96% | $115.0M |
| 2031 | Information technology and security: other work, stream 1 | automated 7, augmented 4, outsourced 11, eliminated 1 | yes | 58 | $2.9M | $11.5M | 0.17 | 97% | $94.7M |
| 2031 | Finance and accounting: other work, stream 2 | automated 2, augmented 1, outsourced 1 | yes | 53 | $2.7M | $8.3M | 0.05 | 98% | $73.5M |
| 2032 | Executive and strategy: other work, stream 1 | automated 3, augmented 10, outsourced 3, eliminated 2 | yes | 59 | $4.0M | $15.3M | 0.05 | 96% | $102.1M |
| 2032 | Marketing: other work, stream 5 | automated 3, augmented 1, outsourced 2 | yes | 63 | $2.9M | $15.8M | 0.17 | 96% | $102.5M |
| 2032 | Sales: other work, stream 5 | automated 4, augmented 1, outsourced 5, eliminated 1 | yes | 73 | $2.4M | $12.1M | 0.05 | 96% | $79.9M |
| 2032 | Human resources: other work, stream 2 | automated 1, augmented 1, outsourced 2 | yes | 45 | $1.9M | $8.6M | 0.17 | 96% | $56.6M |


Rule-of-40 path (percent of revenue). Cash and GAAP, planning case, and the P10 to P90 band on a cash basis:

| year | baseline | plan, cash | plan, GAAP | cash P10 to P90 |
|---|---|---|---|---|
| 2027 | 17.5% | 1.6% | 8.0% | 15.4% to 17.3% |
| 2028 | 17.5% | 22.5% | 28.7% | 11.9% to 17.7% |
| 2029 | 17.5% | 36.9% | 42.5% | 15.9% to 20.7% |
| 2030 | 17.5% | 44.1% | 49.2% | 16.8% to 23.4% |
| 2031 | 17.5% | 48.3% | 53.2% | 18.1% to 24.8% |
| 2032 | 17.5% | 50.1% | 54.8% | 18.5% to 25.8% |
| 2033 | 17.5% | 50.6% | 55.3% | 18.7% to 28.2% |
| 2034 | 17.5% | 48.7% | 53.4% | 18.7% to 28.4% |
| 2035 | 17.5% | 46.6% | 51.4% | 18.7% to 28.5% |
| 2036 | 17.5% | 44.6% | 49.5% | 18.7% to 28.5% |

Constraints: change capacity is used up to 100% in its peak year; the decision load reaches 0.85 of bandwidth (breakpoint 0.72); security reviews peak at 6.8 against capacity 156 a year.

### Playbook by process step

Decisions are made per activity unit (an O*NET detailed work activity in a process step) and executed per process step: 667 activity units in 667 steps, 3,665 FTE now and 2,490 after the plan. Each row carries the mode now, in the plan and at target readiness, the binding constraint, preconditions, go/no-go gates with their source, wave and dependencies, roles and FTE, KPIs, controls (ICFR channel and condition, ITGC and interface lines, fallback), evidence keys with their grounding class, O*NET task statements, a confidence tier and the firm's distance to each switch threshold (playbook_activities.csv, playbook_steps.csv; playbook_data_dictionary.csv defines every field).

Activity units by mode in the plan: in-house 436, outsourced 119, automated 54, augmented 45, eliminated 13. What binds automation at target readiness: reliability: detection 452, feasibility: physical 125, feasibility: capability horizon 55, none 15, permissibility 14, volume threshold 5, cost 1. Confidence at target: tier A 111, tier B 132, tier C 424 (def:playbook-tier. A: bound by capability, physical work or permissibility, filters the backtest supports. B: rests on the cost crossover or a reliability gate with sourced inputs, not validated by the backtest. C: the decision to automate, or to use AI at all, changes when one of 149 class d inputs moves to an end of its range, or the process's value is positive in fewer than 80% of the Monte Carlo draws).

| process | step | step name | now | plan | wave | binds today at target readiness | FTE now | FTE after | saving a year | tier |
|---|---|---|---|---|---|---|---|---|---|---|
| Product and engineering: other work, stream 12 |  | residual work | H | A | 3 | reliability: detection | 70.1 | 0.5 | $15.3M | C |
| Sales: other work, stream 10 |  | residual work | H | A | 2 | reliability: detection | 63.5 | 37.0 | $14.5M | C |
| Product and engineering: other work, stream 9 |  | residual work | H | A | 4 | reliability: detection | 57.6 | 0.5 | $13.6M | C |
| Product and engineering: other work, stream 5 |  | residual work | H | A | 3 | reliability: detection | 64.7 | 3.8 | $12.9M | C |
| Professional services: other work, stream 10 |  | residual work | H | A | 4 | reliability: detection | 47.6 | 0.1 | $12.0M | C |
| Marketing: other work, stream 4 |  | residual work | H | A | 5 | reliability: detection | 25.0 | 0.1 | $11.0M | C |
| Marketing: other work, stream 5 |  | residual work | H | A | 6 | reliability: detection | 22.1 | 0.0 | $10.4M | C |
| Finance and accounting: other work, stream 4 |  | residual work | H | A | 4 | feasibility: capability horizon | 17.8 | 0.1 | $8.5M | C |
| Product and engineering: other work, stream 10 |  | residual work | H | A | 3 | reliability: detection | 35.1 | 0.0 | $7.7M | C |
| Marketing: other work, stream 3 |  | residual work | H | A | 5 | reliability: detection | 19.2 | 0.0 | $7.4M | C |
| Human resources: other work, stream 2 |  | residual work | H | A | 6 | reliability: detection | 14.2 | 0.1 | $6.4M | C |
| Executive and strategy: other work, stream 2 |  | residual work | H | A | 2 | reliability: detection | 19.2 | 11.1 | $5.6M | C |
| Sales: other work, stream 5 |  | residual work | H | A | 6 | reliability: detection | 8.4 | 0.0 | $4.9M | C |
| Executive and strategy: other work, stream 1 |  | residual work | H | A | 6 | reliability: detection | 6.4 | 0.0 | $4.3M | C |
| Lead to close | 7 | Record in CRM | H | N | 2 | reliability: detection | 37.7 | 0.0 | $3.9M | C |

(167 more rows in the CSV)


Modes: H in-house, O outsourced, U augmented, A automated, N eliminated. The binding column is the first gate that fails today at the highest readiness; a step the plan automates in a later wave waits for that gate to clear (first_year_A_at_target). Cycle time is not modeled; each step's KPI says to measure it in Wave 0 (event logs or process mining, or a time study) unless a Tier 4 study gives it.

## 5. People

Residual organization at today's volumes (planning case): 2,389 FTE of 3,222. Spans widen with automation (Garicano); manager counts are shown at the central AI span uplift of 0.50 (range 0.0 to 1.0).

| function | FTE today | FTE after | junior | senior | review and sign-off | managers today | managers after | apprenticeship gap |
|---|---|---|---|---|---|---|---|---|
| Product and engineering | 552 | 278 | 0 | 234 | 1 | 152 | 80 |  |
| Sales | 570 | 386 | 0 | 65 | 1 | 103 | 59 | yes |
| Marketing | 177 | 80 | 0 | 11 | 0 | 23 | 5 |  |
| Finance and accounting | 192 | 104 | 0 | 13 | 0 | 37 | 11 | yes |
| Executive and strategy | 81 | 23 | 0 | 0 | 0 | 8 | 0 |  |
| Professional services | 398 | 350 | 0 | 0 | 0 | 76 | 65 |  |
| Legal | 61 | 28 | 0 | 0 | 0 | 15 | 8 |  |
| Information technology and security | 47 | 16 | 0 | 0 | 0 | 11 | 5 |  |
| Human resources | 75 | 55 | 0 | 0 | 0 | 16 | 11 | yes |
| Service delivery and operations | 16 | 16 | 2 | 0 | 0 | 0 | 0 |  |
| Customer support | 568 | 568 | 191 | 0 | 0 | 167 | 167 |  |
| Customer success and account management | 186 | 186 | 0 | 21 | 0 | 51 | 51 |  |
| Supply chain, manufacturing and logistics | 17 | 17 | 5 | 0 | 0 | 4 | 4 |  |
| Procurement | 15 | 15 | 0 | 0 | 0 | 4 | 4 |  |
| Technical operations and hosting | 232 | 232 | 0 | 37 | 0 | 64 | 64 |  |
| Facilities and real estate | 35 | 35 | 0 | 0 | 0 | 7 | 7 |  |


Transformation team by year (lem:ext-staffing), peak 26 FTE in 2032. The sizing ratios are scenario values unless the firm gave its own (e_PO 0.25 to 1.00, e_SME 0.10 to 0.50, l_DI 0.40 to 0.80, l_AI 0.40 to 0.80, N_CM 50.00 to 200.00, e_RG 0.25 to 1.00); a firm's own ratios in tier3_org replace them.

| year | AI engineers | data engineers | process owners | change managers | domain experts | risk and audit | security | total |
|---|---|---|---|---|---|---|---|---|
| 2027 | 0.8 | 0.0 | 1.5 | 2.2 | 0.8 | 0.0 | 0.2 | 6.5 |
| 2028 | 7.4 | 9.4 | 2.5 | 2.9 | 1.2 | 0.0 | 0.6 | 25.0 |
| 2029 | 8.3 | 8.7 | 2.0 | 2.9 | 1.0 | 0.5 | 0.5 | 24.8 |
| 2030 | 8.6 | 6.8 | 2.0 | 2.8 | 1.0 | 1.0 | 0.5 | 23.8 |
| 2031 | 10.2 | 6.9 | 2.0 | 2.8 | 1.0 | 0.5 | 0.5 | 25.0 |
| 2032 | 11.1 | 6.9 | 2.0 | 2.9 | 1.0 | 1.0 | 0.5 | 26.3 |
| 2033 | 9.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 9.6 |
| 2034 | 9.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 9.6 |
| 2035 | 9.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 9.6 |
| 2036 | 9.6 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 9.6 |


### Labor law, survivors and talent (theory_labor)

Separations net of redeployment total 867 over the plan, with severance of $28.5M at 2.7 months of pay per displaced employee on average: at each site the larger of the statutory floor (tab:labor-rules, at the site's tenure and age) and the negotiated plan. Legal leads (procedure start to the earliest effective dismissal) average 0.2 months and reach 1.0 at the slowest site; the engine starts the procedure at the decision where the law requires it (EU and UK) or where the success probability clears the cutoff of prop:labor-lead(d), and extends the parallel run to the earliest dismissal date when that is cheaper than idling (prop:labor-lead(e)). Rules as of 2026-10-29; source of site data: tier3_jurisdictions. These are model constraints, not legal advice.

EU AI Act: high-risk obligations apply from 2027-12-02 for the Annex III areas and from 2028-08-02 for systems under Annex I (Regulation (EU) 2026/1744 (recitals 40 and 46)). The firm has an EU nexus and the plan runs past the Annex III date, so staffing and other Annex III activities on personal data are treated as high risk (oversight floor and regulated build effort).

| site | country | headcount | rule | lead (months) | technology consultation (months) | statutory floor (months) | severance used (months) | personal data for AI |
|---|---|---|---|---|---|---|---|---|
| Austin, TX | US | 938 | WARN Act (federal) | 0.0 | 0.0 | 0.00 | 3.00 | in_region |
| Bangalore, India | IN | 175 | Industrial Relations Code 2020 s.70, s.83 | 1.0 | 0.0 | 2.50 | 2.50 | free |
| Dublin, Ireland | IE | 358 | Directive 98/59/EC minimum (national law sets more) | 1.0 | 0.0 | 0.00 | 1.50 | restricted |
| Krakow, Poland | PL | 87 | Directive 98/59/EC minimum (national law sets more) | 1.0 | 0.0 | 0.00 | 1.50 | restricted |
| Manila, Philippines | PH | 52 | none modeled | 0.0 | 0.0 | 0.00 | 1.00 | free |
| Remote US | US | 786 | WARN Act (federal) | 0.0 | 0.0 | 0.00 | 3.00 | in_region |
| San Francisco, CA | US | 826 | WARN Act (federal) | 0.0 | 0.0 | 0.00 | 3.00 | in_region |


With the planned separations, a collective procedure is triggered at 0 site-years (all program dismissals at a site in a window counted together; sub-threshold pacing is off). At 14 site-years the trigger test differs from the prior test used while the plan was built; the leads there are approximate.

Rules used here that could not be confirmed at a primary source (flagged as unverified): IE: only the EU minimum is modeled; national rules not read; India 15/26 convention for monthly-rated pay; PH: no statutory rule modeled; notice and severance from the plan only; PL: only the EU minimum is modeled; national rules not read; s.79 notice length and state Shops and Establishments Acts.

Survivors (prop:labor-survivor): each announced wave adds about 2.35% quits among the remaining staff of the functions it touches (Sajjadiani et al. 2023, class b), 86.4 extra quits over the plan, each costing 0.56 years of wages; they are backfilled in the hiring plan, and the per-wave charge O_s = $382k enters the wave optimizer. The redeployment share 25% exceeds the vacancy bound of prop:labor-survivor(e) (22%), so fewer people can be redeployed than assumed.

Engineering talent (prop:labor-talent): loaded AI engineer cost $195k a year (OEWS median for software developers with the 11% AI premium of Alekseeva et al. 2021 and payroll loading). With 57 engineers today and 6.3 hires a year after a 3-month lead, the firm can sustain at most 246 automated processes in run mode at 0.48 engineers each (assumptions register row 14, class b); bringing the plan's 20 automated processes into run mode takes 0.3 years. Hiring keeps pace with the team plan.

Pace (cor:labor-pace): the program cannot finish faster than change capacity 5.7 years, decision bandwidth 0.4 years, engineering talent 0.3 years; the binding constraint is change capacity.

Cutover streams (prop:labor-lead(b)): wave 2: (Austin, TX, Manila, Philippines, Remote US, San Francisco, CA) at 0.6 months then (Dublin, Ireland, Krakow, Poland, Bangalore, India) at 1.0 months. Faster jurisdictions cut over in their own stream when their forgone savings exceed the wave overhead.

Location (lem:labor-location): at a site with wage index w, automation pays at least ln(1/w)/delta_pi years later than in the U.S.: Bangalore, India 1.4 years (w 0.04, OECD average wage), Dublin, Ireland 0.0 years (w 0.95, engine location prior), Krakow, Poland 0.5 years (w 0.33, OECD average wage), Manila, Philippines 0.6 years (w 0.25, engine location prior).

Data residency (prop:labor-residency): 14% of staff sit where personal data cannot be sent to the AI vendor's regions (US) without a mechanism; readiness for personal-data activities there is capped at (1 - omega^res) iota. An in-region deployment, the EU-U.S. Data Privacy Framework or standard contractual clauses (tier3_org vendor_regions, vendor_dpf_certified; tier3_jurisdictions transfer_mechanism) remove the cap.

Hiring for AI and data roles starts 3 months ahead (vacancy duration plus candidate notice, class b, 1 to 6 months).

## 6. Risk and outcome distribution

Monte Carlo: 30 draws of the firm's data and of 403 class b and d parameters, each with 200 outcome draws (success or partial realization, correlated platform failure, heavy-tailed overruns with tail index 2.3, leadership, vision and reorganization shocks, misbehavior and provider events). Value P10 $235.0M, P50 $1.3B, P90 $2.2B; CVaR at 95 percent $19.3M. Misbehavior losses over the plan $169k to $6.6M; provider (common-mode) losses $1.0M to $12.9M. Convergence: the mean moved 7.9% between half and full sample.

Stage gates (core prop:tasks-pilot): a revealing pilot pays for 0 of 24 processes.
Parameters most associated with the plan's value across draws (rank correlation): capability.e1 (-0.59), capability.r_U (-0.55), product.mig_omega_range (-0.53), decisions.Phi_base (-0.51), accounting.T_rem (-0.50), outsourcing.separable_threshold (-0.48).

## 7. AI failure modes and controls

By process, planning case (core prop:tasks-halluc, prop:tasks-bias, prop:tasks-autonomy, prop:tasks-pipeline). Hallucination, catch rates and misbehavior rates come from data/tasks/params_reliability.yaml; scenario-only reliability parameters are drawn over their ranges in the risk section.

| process | autonomy | review share | undetected errors | expected misbehavior loss a year | tail loss per event (CVaR) | required controls |
|---|---|---|---|---|---|---|
| Lead to close | draft | n/a | n/a | n/a | n/a | human review of every output (augmentation) |
| Executive and strategy: other work, stream 1 | act autonomously | 0% | 7.85% | $46k | $134k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback |
| Executive and strategy: other work, stream 2 | act autonomously | 2% | 9.17% | $48k | $32k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback |
| Product and engineering: other work, stream 3 | draft | n/a | n/a | n/a | n/a | human review of every output (augmentation) |
| Product and engineering: other work, stream 5 | act autonomously | 0% | 8.68% | $63k | $25k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback |
| Product and engineering: other work, stream 6 | act autonomously | 0% | 8.94% | $6k | $15k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback |
| Product and engineering: other work, stream 7 | draft | n/a | n/a | n/a | n/a | human review of every output (augmentation) |
| Product and engineering: other work, stream 9 | act autonomously | 0% | 7.47% | $54k | $13k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback |
| Product and engineering: other work, stream 10 | act autonomously | 0% | 7.57% | $20k | $7k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback |
| Product and engineering: other work, stream 12 | act autonomously | 0% | 7.90% | $60k | $14k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback |
| Marketing: other work, stream 3 | act autonomously | 0% | 7.91% | $99k | $71k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback; prompt-injection defenses on external inputs |
| Marketing: other work, stream 4 | act autonomously | 0% | 7.29% | $48k | $15k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback; prompt-injection defenses on external inputs |
| Marketing: other work, stream 5 | act autonomously | 0% | 7.26% | $77k | $24k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback; prompt-injection defenses on external inputs |
| Sales: other work, stream 5 | act autonomously | 0% | 7.79% | $70k | $59k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback; prompt-injection defenses on external inputs |
| Sales: other work, stream 9 | act autonomously | 0% | 8.74% | $12k | $14k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback; prompt-injection defenses on external inputs |
| Sales: other work, stream 10 | act autonomously | 0% | 9.55% | $132k | $30k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback; prompt-injection defenses on external inputs |
| Sales: other work, stream 11 | draft | n/a | n/a | n/a | n/a | human review of every output (augmentation) |
| Professional services: other work, stream 10 | act autonomously | 0% | 7.53% | $75k | $23k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback; prompt-injection defenses on external inputs |
| Finance and accounting: other work, stream 2 | act autonomously | 0% | 7.87% | $9k | $28k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback |
| Finance and accounting: other work, stream 3 | act autonomously | 0% | 9.10% | $41k | $101k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback |
| Finance and accounting: other work, stream 4 | act autonomously | 0% | 7.55% | $50k | $44k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback |
| Human resources: other work, stream 2 | act autonomously | 0% | 9.78% | $25k | $17k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback |
| Legal: other work, stream 1 | act autonomously | 0% | 8.42% | $17k | $74k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback |
| Information technology and security: other work, stream 1 | act autonomously | 0% | 7.51% | $31k | $176k | least privilege on write and transaction rights; monitoring with detection lag; kill switch and rollback |


Provider concentration: 1 model provider(s), HHI 1.00. A provider event (about 2.0 a year) degrades about 16% of requests for about 14 days in every process on that provider at once; a second provider costs about $20k a process a year and narrows the loss distribution.

Sources: Hallucination rates: Vectara (2026), Hallucination Leaderboard; Tamber et al. (2025), EMNLP Industry Track; Magesh et al. (2025), Journal of Empirical Legal Studies 22(2); Dahl et al. (2024), Journal of Legal Analysis 16(1). Reviewer catch rates and automation bias: Agarwal et al. (2023), NBER w31422; Panko (1999), JMIS 16(2); Goddard, Roudsari and Wyatt (2012), JAMIA 19(1); Parasuraman and Manzey (2010), Human Factors 52(3); Si et al. (2024), NAACL. Agentic misbehavior: Lynch et al. (2025), arXiv:2510.05179; Meinke et al. (2024), arXiv:2412.04984; Von Arx, Chan and Barnes (2025), METR; Baker et al. (2025), arXiv:2503.11926; Ruan et al. (2024), ICLR. Prompt injection: Zhan et al. (2024), Findings of ACL; Debenedetti et al. (2024), NeurIPS Datasets and Benchmarks; Zou et al. (2025), NeurIPS. Agent pipelines: Yao et al. (2025), tau-bench; Cemri et al. (2025), multi-agent failure taxonomy; Kwa et al. (2025). Common-mode failure: Chen, Zaharia and Zou (2024), Harvard Data Science Review 6(2); OpenAI (2025), Expanding on what we missed with sycophancy; Anthropic (2026), An update on recent Claude Code quality reports. Loss severity: de Fontnouvelle, Rosengren and Jordan (2007), in The Risks of Financial Institutions; IBM and Ponemon (2026), Cost of a Data Breach.

## 8. Ownership-regime view

Each regime values the same candidate plans with its own rate (continuous), horizon, terminal rule and constraints (theory_regimes.tex). Side by side:

| regime | rate (annual) | horizon | plan value | processes | first-year launches | GAAP dip (points) | growth weight X |
|---|---|---|---|---|---|---|---|
| public | 9.3% | going concern | $2.1B | 24 | 3 | -1.1 | 4.0 |
| private family | 8.3% | going concern | $2.7B | 24 | 3 | -1.0 | 5.0 |
| pe | 22.0% | 6 years | $621.4M | 19 | 2 | -1.3 | 2.6 |
| vc | 31.0% | 7 years | $1.0B | 22 | 2 | -1.2 | 3.5 |
| hybrid | 9.3% | going concern | $2.0B | 22 | 2 | -1.3 | 4.4 |
| permanent capital | 25.0% | going concern | $382.2M | 24 | 2 | -1.0 | 1.4 |

PE at h_x = 0.5 (share of seasoned run-rate the buyer capitalizes): MOIC 2.54 without the plan and 4.32 with it; gross IRR 16.8% and 27.6%; net IRR to LPs 12.2% and 21.8%.
PE at h_x = 1 (share of seasoned run-rate the buyer capitalizes): MOIC 2.54 without the plan and 5.56 with it; gross IRR 16.8% and 33.1%; net IRR to LPs 12.2% and 26.8%.
Entry at 14.0 times EBITDA (equal to the exit multiple unless the firm gave both). Peak leverage with the plan 5.5 times against a covenant of 7.0. With h_x = 0.5 the PE plan is worth $366.9M (19 processes).
Public: operating income turns accretive in 2029; the largest GAAP dip is -1.1 points; Rule of 40 below guidance in 2027, 2028, 2029, 2030 (GAAP).
Take-private (prop:reg-lbo): the largest premium a sponsor could pay is 45% at h_x = 1 and 20% at h_x = 0.5, against a required control premium of 30%.

### Permanent capital

A permanent-capital owner never sells and holds internal decisions to its unlevered hurdle as a going concern (prop:acq-pc(d)); it buys only if the method IRR (five years of free cash flow, then a terminal value at 9.3%) clears 25% unlevered and 65% levered (annual; presets from the case firm's F-1, class a). At a price of $1.6B (market price times one plus the control premium and transaction costs), the unlevered method IRR is -31.6% without the plan and 27.0% with it; levered under the debt policy, -32.3% and 28.3%.
The most it can pay at the unlevered hurdle (P^max, eq:acq-pmaxbound) is $1.8B with the plan, 20.0 times EBITDA and 52% of the value at the terminal rate (bound 51%); without the plan $93.6M. Debt at entry is the lower of 85% of the price and the debt five years of free cash flow repay at 9.6% ($170.4M, repayment binds; 1.9 times EBITDA against a covenant of 4.0). The hurdle holds if the program raises value at the terminal rate by at least 154% and only if by at least 30% (the control premium); this plan raises it by 1899%.

Limits to buying growth (prop:acq-limits), in continuously compounded rates. Holding growth of 15.7% (17.0% a year) needs acquired growth of 5.7% a year, growth less organic growth 10.0%; standing still needs 0.0%. Organic growth 10.0% is taken from Part I's zero-spend growth G, since no NRR or reported organic growth was supplied; g^max needs the price paid per dollar of acquired revenue (tier3_regime acquisition_price_to_revenue). Deal-size, series-review, foreign-investment and consumer-law limits are off: their class d parameters have no value, so each takes its neutral value until a scenario or --set gives one (the verified domain of the reference script is not used as a range).

Value by stakeholder (PV over the plan): owners $2.1B, customers $27.0M, government $488.3M, displaced employees -$50.4M, vendors $0.00.

## 9. Security and compliance

Firm-level compliance once AI is deployed: $75k in the first year and $303k a year after (SOC 2, ISO/IEC 42001, NIST AI RMF alignment, incident response, the AI share of cyber insurance; certifications already held are not counted). Security-review queue at its peak: 6.8 reviews a year against capacity 156, latency 2 days (prop:tasks-secreview).
Post-quantum cryptography: migration of about $4.3M by 2035 (NIST IR 8547: quantum-vulnerable algorithms deprecated after 2030 and disallowed after 2035); the cost is a scenario range scaled by IT spend, and it uses the same budget as the AI program.

| process | data class | exposure | incident loss a year | security spend | maintenance | build or buy |
|---|---|---|---|---|---|---|
| Lead to close | internal | 0.00 | $0.00 | $0.00 | $0.00 | nan |
| Executive and strategy: other work, stream 1 | internal | 0.43 | $14k | $0.00 | $13k | buy |
| Executive and strategy: other work, stream 2 | internal | 0.43 | $29k | $7k | $86k | buy |
| Product and engineering: other work, stream 3 | internal | 0.00 | $0.00 | $0.00 | $0.00 | nan |
| Product and engineering: other work, stream 5 | internal | 0.43 | $5k | $0.00 | $38k | buy |
| Product and engineering: other work, stream 6 | internal | 0.43 | $10k | $0.00 | $32k | buy |
| Product and engineering: other work, stream 7 | internal | 0.00 | $0.00 | $0.00 | $0.00 | nan |
| Product and engineering: other work, stream 9 | internal | 0.43 | $5k | $0.00 | $20k | buy |
| Product and engineering: other work, stream 10 | internal | 0.43 | $5k | $0.00 | $19k | buy |
| Product and engineering: other work, stream 12 | internal | 0.43 | $5k | $0.00 | $30k | buy |
| Marketing: other work, stream 3 | internal | 0.49 | $22k | $2k | $29k | buy |
| Marketing: other work, stream 4 | internal | 0.49 | $6k | $0.00 | $10k | buy |
| Marketing: other work, stream 5 | internal | 0.49 | $17k | $0.00 | $15k | buy |
| Sales: other work, stream 5 | internal | 0.49 | $23k | $2k | $15k | buy |
| Sales: other work, stream 9 | internal | 0.49 | $6k | $0.00 | $18k | buy |
| Sales: other work, stream 10 | internal | 0.49 | $6k | $0.00 | $44k | buy |
| Sales: other work, stream 11 | internal | 0.00 | $0.00 | $0.00 | $0.00 | nan |
| Professional services: other work, stream 10 | internal | 0.49 | $6k | $0.00 | $23k | buy |
| Finance and accounting: other work, stream 2 | internal | 0.43 | $10k | $0.00 | $13k | buy |
| Finance and accounting: other work, stream 3 | internal | 0.43 | $15k | $0.00 | $26k | buy |

(4 more rows in the CSV)


### Financial reporting (ICFR) scope and controls

A step is in scope for internal control over financial reporting if it initiates, authorizes, records, processes or reports a transaction or estimate that reaches the financial statements (a), reads or writes an in-scope system (b), creates or changes an integration feeding one (c), or executes an ICFR-relevant policy (d); scope and channels come from the data contract (class b: PCAOB AS 2201, common SOX scoping). 51 steps are in scope, 3 are assumed in scope because no input says whether their condition holds, and 5 are out because the firm's inputs say the condition does not hold. Answering the conditions in tier3_org (refunds issued, CRM-to-billing integration, inventory held and so on) replaces the assumptions.

In-scope steps that the plan automates, and steps assumed in scope:

| process | step | activity | channel | condition | status | automated |
|---|---|---|---|---|---|---|
| Incident to resolution | 4 | Resolve computer network problems. | b: in-scope system | when the fix changes data or configuration in an in-scope system | assumed in scope |  |
| Implementation project | 3 | Configure computer networks. | b: in-scope system; c: integration feeding an in-scope system | when time or progress entries feed percent-complete revenue or billing | assumed in scope |  |
| Contract review and legal advice | 5 | Negotiate contracts with clients or service providers. | d: ICFR-relevant policy | when a settlement or claim feeds a loss-contingency accrual or disclosure (ASC 450) | assumed in scope |  |


## 10. Sensitivity

Scenarios (plan value of each scenario's own plan and of the recommended plan):

| scenario | what changes | own plan | recommended plan | regret of recommended |
|---|---|---|---|---|
| central | defaults and the firm's inputs | $2.1B | $2.1B | $0.00 |
| capability slow | task horizons double every 240 days | $2.0B | $1.8B | $214.0M |
| capability fast | task horizons double every 143 days | $2.1B | $2.1B | $0.00 |
| capability plateau | task horizons stop growing after 2028 | $1.0B | $908.5M | $121.7M |
| agi 2030 | cognitive tasks of any length become feasible in 2030 | $2.1B | $2.1B | $0.00 |
| constant hazard | agent reliability follows a constant hazard (chi(0.8) = 3.1) instead of METR's logistic | $2.1B | $2.1B | $0.00 |
| ai native entrant | AI-native entrants force a further 58% of unit-cost savings to customers | $2.1B | $2.0B | $24.4M |
| concentrated supply | concentrated model supply: inference prices fall 5 times a year, not 10, and entrants keep a markup | $2.0B | $2.1B | $0.00 |
| energy fusion | energy price falls to a tenth (fusion) | $2.0B | $2.1B | $0.00 |
| energy shock | energy price triples | $2.0B | $2.1B | $0.00 |
| regulation strict | human review of 30 percent of AI output everywhere, full review in high-risk uses, approval of irreversible actions | $1.6B | $1.7B | $0.00 |
| regulation light | no oversight floor outside licensed work | $2.0B | $2.1B | $0.00 |
| quantum | early quantum risk: post-quantum migration by 2030 at higher cost (changes only that cost) | $2.0B | $2.1B | $0.00 |
| disruption shocks | leadership changes and vision overhauls cancel work in flight on top of the survey-based realized share (counts disruption twice unless the firm's realized share excludes it) | $1.5B | $1.6B | $0.00 |
| pass through 0 | fixed prices: no cost-of-revenue saving is passed to customers | $2.2B | $2.1B | $22.2M |
| pass through 50 | industry pass-through rate 0.5 on unit-cost savings the rivals make (margins at the post-cut price); the firm keeps 62% of the dollar value of a replicated cost-of-revenue saving | $2.0B | $2.1B | $0.00 |
| pass through 70 | industry pass-through rate 0.7 on unit-cost savings the rivals make (margins at the post-cut price); the firm keeps 48% of the dollar value of a replicated cost-of-revenue saving | $2.1B | $2.1B | $127k |

Spec 5 tornado: share of spend economical to move to AI modes at the low and high end of each tax, regulation and preference parameter: customer preference for human service 85% to 75%; customer pull lost to automation 84% to 75%; owner's value of a retained job 84% to 90%; ethics penalty per automated unit 84% to 83%; licensing threshold 84% to 84%; data-protection cap on readiness 84% to 84%.

Global sensitivity (spec 24.2), Morris screening over 179 class b and d parameters in 14 groups; top groups: group capability (14) (1.00), group reliability (41) (0.30), group build (15) (0.28), group review (11) (0.20).
Sobol indices (first order and total) for the annual saving of the recommended plan and for its five-year net value after one-time build and integration costs: capability.e1 0.57 and 0.88 (net value 0.57 and 0.87); capability.e0 0.15 and 0.25 (net value 0.15 and 0.25); capability.transfer 0.00 and 0.00 (net value 0.00 and 0.00); reliability.d_e 0.45 and 0.24 (net value 0.43 and 0.23); reliability.acc0 0.04 and 0.00 (net value 0.04 and 0.00); reliability.rho_appr -0.03 and 0.01 (net value -0.03 and 0.01); build.int_cost_per_system 0.00 and 0.00 (net value 0.01 and 0.00); build.int_convexity 0.00 and 0.00 (net value 0.01 and 0.00); build.regulated_mult 0.00 and 0.00 (net value 0.00 and 0.00).
Sobol bounds over the sample (P10 to P90): annual saving $45.0M to $244.5M; five-year net value $147.8M to $951.7M. The integration cost per system and the convexity of the integration cost in readiness are always in this set, because they decide the sign of the paper's core transition example.

## 11. Breakpoints

Distance to the breakpoints of each automated process (core prop:tasks-breakpoints): how far the inference price could rise (as a share), how far volume could fall, the slack in reviewer detection rate before the reliability target fails, the readiness slack and the years of capability slack.

| process | price headroom | volume headroom | detection slack | readiness slack | capability slack (yr) | value z-score |
|---|---|---|---|---|---|---|
| Lead to close | n/a | n/a | n/a | n/a | n/a | 1.3 |
| Executive and strategy: other work, stream 1 | 2273507% | 6488% | 0.52 | 0.33 | 4.9 | 2.7 |
| Executive and strategy: other work, stream 2 | 123314% | 329% | 0.28 | 0.22 | 1.2 | 3.3 |
| Product and engineering: other work, stream 3 | n/a | n/a | n/a | n/a | n/a | 1.6 |
| Product and engineering: other work, stream 5 | 613071% | 5038% | 0.49 | 0.43 | 2.1 | 1.1 |
| Product and engineering: other work, stream 6 | 175149% | 531% | 0.39 | 0.33 | 1.5 | 0.6 |
| Product and engineering: other work, stream 7 | n/a | n/a | n/a | n/a | n/a | 1.3 |
| Product and engineering: other work, stream 9 | 219972% | 3280% | 0.52 | 0.33 | 3.3 | 1.6 |
| Product and engineering: other work, stream 10 | 769484% | 6445% | 0.52 | 0.33 | 2.5 | 0.9 |
| Product and engineering: other work, stream 12 | 782298% | 8610% | 0.53 | 0.33 | 2.4 | 1.6 |
| Marketing: other work, stream 3 | 1497326% | 4590% | 0.51 | 0.33 | 4.0 | 2.1 |
| Marketing: other work, stream 4 | 357269% | 5505% | 0.51 | 0.33 | 4.5 | 3.4 |
| Marketing: other work, stream 5 | 1082314% | 9615% | 0.51 | 0.33 | 5.1 | 1.6 |
| Sales: other work, stream 5 | 1312901% | 6431% | 0.51 | 0.22 | 5.3 | 0.6 |
| Sales: other work, stream 9 | 174143% | 1843% | 0.39 | 0.33 | 1.5 | 0.4 |
| Sales: other work, stream 10 | 62417% | 4814% | 0.27 | 0.33 | 1.2 | 1.8 |
| Sales: other work, stream 11 | n/a | n/a | n/a | n/a | n/a | 1.4 |
| Professional services: other work, stream 10 | 739064% | 8068% | 0.52 | 0.33 | 3.1 | 1.3 |
| Finance and accounting: other work, stream 2 | 1502002% | 3965% | 0.52 | 0.43 | 3.9 | 2.6 |
| Finance and accounting: other work, stream 3 | 1496797% | 1340% | 0.52 | 0.22 | 3.0 | 1.7 |
| Finance and accounting: other work, stream 4 | 1384540% | 2850% | 0.52 | 0.33 | 2.9 | 1.9 |
| Human resources: other work, stream 2 | 1034016% | 15893% | 0.53 | 0.22 | 5.4 | 1.9 |
| Legal: other work, stream 1 | 583751% | 359% | 0.42 | 0.22 | 1.9 | 2.7 |
| Information technology and security: other work, stream 1 | 1401350% | 1734% | 0.51 | 0.33 | 3.6 | 5.9 |


Should versus could (cor:ext-game-engine): with market concentration HHI 0.25 and industry pass-through 0.50 (competition.phi_ind), the firm keeps 62% of the dollar value of a replicable cost-of-revenue saving, its volume gain counted (the margin share is lower than the price cut alone implies and does not depend on HHI; the homogeneous-Cournot benchmark, pass-through 0.80, would leave 40%; scenarios pass_through_0, _50 and _70 span the anchors). Labels: value-creating 106, not feasible 3. Adoption is a dominant strategy for 35 processes, falls in the automation dilemma window for 3, and is defensive against AI-native entry for 17.

## 12. Confidence and data gaps

Input tier reached: 4. Files used: tier0_financials, tier1_opex, tier2_roster, tier3_vendors, tier3_systems, tier3_volumes, tier3_org, tier3_jurisdictions, tier3_sponsors, tier4_time_study, tier3_products, tier3_product_occupations, tier3_ai_features, tier3_security, tier3_regime.
Gaps filled from priors (28): tier0.capital_intensity_k; tier3 systems: data classification missing for some functions (defaults: confidential with personal data, else internal); tier3 org: sponsor_tenure_years from prior; tier3 org: key_persons from prior; tier3 org: documentation_coverage from prior; tier3 org: change_capacity_fte not given; class d scenario range used; tier3 org: ai_engineers_per_process not given; class d scenario range used; tier3 org: process_owners_per_process not given; class d scenario range used; tier3 org: sme_fte_per_process not given; class d scenario range used; tier3 org: affected_fte_per_change_manager not given; class d scenario range used; tier3 org: pilots_to_production_past not given; class d scenario range used; tier3 org: redeployment_share not given; class d scenario range used; and more (see report.json).
Value of better data (core prop:tasks-granularity): measurement pays for 18 of 24 processes in the plan.
The width of the value range (P90 minus P10: $2.0B) reflects data gaps and scenario parameters together.
Industry prior (spec 24.10): Software (System & Application) (Damodaran, January 2026; crosswalk confidence high (engine mapping of software codes)); Part I's k 0.574 (industry k (Software (System & Application), unadj basis, Damodaran January 2026)); discount rate 8.93% continuous.

## 13. Assumptions

405 parameters are class d (free scenario parameters: no measurement exists). Every result that depends on them is reported over their range. The full list, with sources, ranges and grounding classes of all parameters, is in assumptions.csv and report.json. Class d parameters with numeric ranges:

| parameter | central | range | outputs affected |
|---|---|---|---|
| finance.fees_f | 0.0250 | 0.0200 to 0.0300 | valuation and the Part I mapping |
| finance.market_growth_G | 0.1000 | 0.0500 to 0.1500 | valuation and the Part I mapping |
| finance.revenue_growth_g | 0.1200 | 0.0000 to 0.3000 | valuation and the Part I mapping |
| finance.rd_expansion_share | 0.5000 | 0.3000 to 0.7000 | valuation and the Part I mapping |
| finance.terminal_multiple_cap | 20.0000 | 12.0000 to 30.0000 | valuation and the Part I mapping |
| finance.pass_through_phi | 0.0000 | 0.0000 to 1.0000 | valuation and the Part I mapping |
| finance.c_c_full_automation | {'2025': 0.06, '2028': 0.12, '2031': 0.08, '2036': 0.05} | 0.0100 to 0.3000 | valuation and the Part I mapping |
| labor.tau_L_contractor | 0.1000 | 0.0000 to 0.2500 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.training_hours_per_fte | 20.0000 | 8.0000 to 60.0000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.change_mgmt_cost_per_fte | 2,000.0000 | 500.0000 to 8,000.0000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.survivor_quits_per_share | 0.0000 | 0.0000 to 0.1000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.delta_eff | 0.0000 | 0.0000 to 0.1000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.nu_x | 0.5000 | 0.0000 to 1.0000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.kappa_doc | 0.2000 | 0.0000 to 0.5000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.kappa_ret | 0.8000 | 0.5000 to 0.9000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.C_ret | 60,000.0000 | 30,000.0000 to 120,000.0000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.knowledge_holders_per_process | 0.0000 | 0.0000 to 5.0000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.varpi_rd | 0.3000 | 0.1000 to 0.5000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.c_ann_share | 0.3000 | 0.0000 to 0.6000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.C_wd_share | 0.2000 | 0.0000 to 0.5000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.dismissal_share_prior | 0.1500 | 0.0500 to 0.4000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.age_default | 40.0000 | 30.0000 to 50.0000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.T_proc_DE | 0.2500 | 0.0833 to 0.5000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.T_tech_DE | 0.2500 | 0.0000 to 0.5000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| labor.T_bld_default | 0.2500 | 0.1000 to 0.5000 | legal leads, severance floors, survivor quits, redeployment, training and change costs |
| capability.r_U | 0.5000 | 0.5000 to 0.8000 | feasibility dates, automation share, plan value |
| capability.xi_exposure | 1.0000 | 0.5000 to 2.0000 | feasibility dates, automation share, plan value |
| capability.exposure_floor | 0.0500 | 0.0200 to 0.1000 | feasibility dates, automation share, plan value |
| capability.xi_context | 0.5000 | 0.3000 to 0.8000 | feasibility dates, automation share, plan value |
| capability.context_coverage | 0.0000 | 0.0000 to 0.9000 | feasibility dates, automation share, plan value |
| capability.L_W | 5.0000 | 2.0000 to 10.0000 | feasibility dates, automation share, plan value |
| capability.physical_threshold | 0.5000 | 0.3000 to 0.7000 | feasibility dates, automation share, plan value |
| capability.api_readiness | 0.6000 | 0.4000 to 0.8000 | feasibility dates, automation share, plan value |
| prices.frontier_factor | 1.0000 | 1.0000 to 18.0000 | inference spend, automation share, plan value |
| prices.floor_share | 0.0050 | 0.0010 to 0.0200 | inference spend, automation share, plan value |
| prices.energy_index | 1.0000 | 0.1000 to 3.0000 | inference spend, automation share, plan value |
| prices.u_tok | 0.2500 | 0.1000 to 0.5000 | inference spend, automation share, plan value |
| prices.tau_A | 0.0000 | 0.0000 to 0.3000 | inference spend, automation share, plan value |
| prices.class_multiplier | {'4.A.1': 0.5, '4.A.2': 1.0, '4.A.3.b': 1.0, '4.A.4': 1.5, '4.A.3.a': 1.0} | 0.3000 to 3.0000 | inference spend, automation share, plan value |
| build.em_base | 3.0000 | 1.0000 to 8.0000 | build and integration costs, payback, plan value |
| build.xi_d | 0.5000 | 0.2500 to 1.0000 | build and integration costs, payback, plan value |
| build.physical_mult | 5.0000 | 2.0000 to 10.0000 | build and integration costs, payback, plan value |
| build.vendor_share | 0.3000 | 0.0000 to 0.6000 | build and integration costs, payback, plan value |
| build.scope_elasticity | 0.3000 | 0.0000 to 0.6000 | build and integration costs, payback, plan value |
| build.U_share | 0.1500 | 0.0500 to 0.3000 | build and integration costs, payback, plan value |
| build.delta_F | 0.3000 | 0.0000 to 0.5000 | build and integration costs, payback, plan value |
| build.int_convexity | 1.0000 | 0.5000 to 1.5000 | build and integration costs, payback, plan value |
| build.int_cost_per_system | 60,000.0000 | 20,000.0000 to 200,000.0000 | build and integration costs, payback, plan value |
| build.T_int | 0.5000 | 0.2500 to 1.0000 | build and integration costs, payback, plan value |
| build.redesign_months | 3.0000 | 1.0000 to 6.0000 | build and integration costs, payback, plan value |
| build.capitalized_share_F | 0.5000 | 0.0000 to 0.7000 | build and integration costs, payback, plan value |
| build.capitalized_share_I | 0.5000 | 0.2000 to 0.7000 | build and integration costs, payback, plan value |
| readiness.iota_min_regulated_add | 0.1000 | 0.0000 to 0.2000 | readiness levels and integration costs |
| readiness.iota_N | 0.8000 | 0.6000 to 0.9000 | readiness levels and integration costs |
| readiness.n_systems_ref | 3.0000 | 2.0000 to 6.0000 | readiness levels and integration costs |
| readiness.default_n_systems | 4.0000 | 2.0000 to 8.0000 | readiness levels and integration costs |
| readiness.personal_data_cap | 1.0000 | 0.7000 to 1.0000 | readiness levels and integration costs |
| outsourcing.rho_O_default | 0.7500 | 0.5000 to 1.0000 | outsourced-mode costs |
| outsourcing.kappa_O | 0.1000 | 0.0500 to 0.1500 | outsourced-mode costs |
| outsourcing.zeta_O | 0.0300 | 0.0000 to 0.1000 | outsourced-mode costs |
| outsourcing.delta_O | 0.0500 | 0.0000 to 0.1500 | outsourced-mode costs |
| outsourcing.separable_threshold | 0.5000 | 0.3000 to 0.7000 | outsourced-mode costs |
| outsourcing.ups_O | 0.1500 | 0.0500 to 0.3000 | outsourced-mode costs |
| augment.exposure_ref | 0.5000 | 0.3000 to 0.7000 | augmentation savings and quality |
| augment.u_decision | 0.2500 | 0.0000 to 0.6000 | augmentation savings and quality |
| augment.u_creation | 0.1500 | 0.0000 to 0.4000 | augmentation savings and quality |
| review.wage_premium | 1.2000 | 1.0000 to 1.6000 | review costs, error rates |
| review.L_mult | 2.0000 | 0.5000 to 5.0000 | review costs, error rates |
| review.L_mult_regulated | 10.0000 | 5.0000 to 30.0000 | review costs, error rates |
| review.lambda_out | 1.0000 | 0.0000 to 3.0000 | review costs, error rates |
| review.r_bar_licensed | 0.9990 | 0.9900 to 0.9999 | review costs, error rates |
| review.xi_min_none | 0.0000 | 0.0000 to 0.0500 | review costs, error rates |
| review.xi_min_high_risk | 0.2500 | 0.1000 to 1.0000 | review costs, error rates |
| review.xi_min_licensed | 0.3000 | 0.1500 to 0.6000 | review costs, error rates |
| handoff.h_MM | 0.0089 | 0.0000 to 0.0300 | process value through handoffs |
| handoff.h_AM | 0.0156 | 0.0050 to 0.0500 | process value through handoffs |
| handoff.h_AA0 | 0.0111 | 0.0000 to 0.0300 | process value through handoffs |
| handoff.h_O | 0.0200 | 0.0050 to 0.0600 | process value through handoffs |
| handoff.Xi_share | 0.0740 | 0.0000 to 0.1500 | process value through handoffs |
| eliminate.delta_N | 0.3000 | 0.1000 to 0.6000 | eliminated work |
| permissibility.licensed_share_threshold | 0.5000 | 0.3000 to 0.7000 | available universe |
| permissibility.delta_G | 0.0000 | -0.0020 to 0.0050 | available universe |
| permissibility.delta_lambda | 0.0000 | 0.0000 to 0.0500 | available universe |
| org.span_ai_uplift | 0.5000 | 0.0000 to 1.0000 | people plan: team sizes, spans, managers |
| org.chi_h | 0.0300 | 0.0100 to 0.0600 | people plan: team sizes, spans, managers |
| org.team_scope_fte | 6.0000 | 2.0000 to 12.0000 | people plan: team sizes, spans, managers |
| org.l_DI | 0.6000 | 0.4000 to 0.8000 | people plan: team sizes, spans, managers |
| org.l_AI | 0.6000 | 0.4000 to 0.8000 | people plan: team sizes, spans, managers |
| org.e_bld | 1.5000 | 0.7500 to 3.0000 | people plan: team sizes, spans, managers |
| org.e_PO | 0.5000 | 0.2500 to 1.0000 | people plan: team sizes, spans, managers |
| org.e_RG | 0.5000 | 0.2500 to 1.0000 | people plan: team sizes, spans, managers |
| org.e_SME | 0.2500 | 0.1000 to 0.5000 | people plan: team sizes, spans, managers |
| org.N_CM | 100.0000 | 50.0000 to 200.0000 | people plan: team sizes, spans, managers |
| competition.hhi | 0.2500 | 0.1000 to 0.5000 | durable share of cost-of-revenue savings, should-versus-could |
| competition.curvature_e | 0.0000 | 0.0000 to 1.5000 | durable share of cost-of-revenue savings, should-versus-could |
| competition.rep | 1.0000 | 0.0000 to 1.0000 | durable share of cost-of-revenue savings, should-versus-could |
| competition.n_rivals | 8.0000 | 3.0000 to 20.0000 | durable share of cost-of-revenue savings, should-versus-could |
| competition.replication_share | 0.6000 | 0.0000 to 1.0000 | durable share of cost-of-revenue savings, should-versus-could |
| competition.p_sw | 0.0500 | 0.0000 to 0.1500 | durable share of cost-of-revenue savings, should-versus-could |
| competition.entrant_markup | 0.1500 | 0.0500 to 0.3000 | durable share of cost-of-revenue savings, should-versus-could |
| competition.entrant_iota | 1.0000 | 0.9000 to 1.0000 | durable share of cost-of-revenue savings, should-versus-could |
| transition.T_par_min | 0.0400 | 0.0000 to 0.1000 | parallel runs, stranded costs, payback, score-path dip |
| transition.T_par_max | 0.5000 | 0.2500 to 1.0000 | parallel runs, stranded costs, payback, score-path dip |
| transition.T_learn_U | 0.2500 | 0.1000 to 0.5000 | parallel runs, stranded costs, payback, score-path dip |
| transition.omega_par | 0.8000 | 0.5000 to 1.0000 | parallel runs, stranded costs, payback, score-path dip |
| transition.nu_rec | 0.1000 | 0.0500 to 0.2500 | parallel runs, stranded costs, payback, score-path dip |
| transition.dup_license_months | 3.0000 | 0.0000 to 12.0000 | parallel runs, stranded costs, payback, score-path dip |
| transition.license_cost_per_system | 60,000.0000 | 20,000.0000 to 200,000.0000 | parallel runs, stranded costs, payback, score-path dip |
| transition.severance_months_other | 1.0000 | 0.5000 to 3.0000 | parallel runs, stranded costs, payback, score-path dip |
| transition.u_d | 0.2500 | 0.1000 to 0.5000 | parallel runs, stranded costs, payback, score-path dip |
| transition.redeploy_months | 2.0000 | 1.0000 to 4.0000 | parallel runs, stranded costs, payback, score-path dip |
| transition.break_months_O | 4.0000 | 2.0000 to 9.0000 | parallel runs, stranded costs, payback, score-path dip |
| transition.break_months_license | 6.0000 | 0.0000 to 24.0000 | parallel runs, stranded costs, payback, score-path dip |
| transition.retire_fraction | 0.5000 | 0.2000 to 1.0000 | parallel runs, stranded costs, payback, score-path dip |
| transition.legacy_book_value_per_system | 150,000.0000 | 0.0000 to 500,000.0000 | parallel runs, stranded costs, payback, score-path dip |
| transition.dip_share | 0.1000 | 0.0100 to 0.3000 | parallel runs, stranded costs, payback, score-path dip |
| transition.dip_years | 1.0000 | 0.2500 to 3.0000 | parallel runs, stranded costs, payback, score-path dip |
| transition.T_det | 0.2500 | 0.1000 to 0.5000 | parallel runs, stranded costs, payback, score-path dip |
| transition.L_roll_mult | 1.0000 | 0.3000 to 3.0000 | parallel runs, stranded costs, payback, score-path dip |
| program.O_w_share | 0.0100 | 0.0000 to 0.0300 | wave overheads and congestion |
| program.d2_share | 0.2500 | 0.0000 to 0.5000 | wave overheads and congestion |
| program.O_re_share | 0.5000 | 0.0000 to 1.0000 | wave overheads and congestion |
| success.a_iota | 2.0000 | 1.0000 to 3.0000 | success probabilities and risk-adjusted value |
| success.a_H | 0.5000 | 0.2000 to 1.0000 | success probabilities and risk-adjusted value |
| success.a_R | 0.5000 | 0.0000 to 1.0000 | success probabilities and risk-adjusted value |
| success.c0 | 2.3100 | 1.1100 to 3.1100 | success probabilities and risk-adjusted value |
| success.c_exc | 1.0000 | 0.0000 to 2.0000 | success probabilities and risk-adjusted value |
| success.c_fte | 0.4000 | 0.0000 to 0.8000 | success probabilities and risk-adjusted value |
| success.c_team | 1.0000 | 0.3000 to 2.0000 | success probabilities and risk-adjusted value |
| success.c_sponsor | 0.8000 | 0.2000 to 1.5000 | success probabilities and risk-adjusted value |
| success.c_past | 1.0000 | 0.3000 to 1.5000 | success probabilities and risk-adjusted value |
| success.U_bonus | 1.0000 | 0.3000 to 2.0000 | success probabilities and risk-adjusted value |
| success.b_conc | 8.0000 | 4.0000 to 20.0000 | success probabilities and risk-adjusted value |
| success.upsilon_L | 1.0000 | 0.5000 to 1.5000 | success probabilities and risk-adjusted value |
| success.delta_E | 0.3000 | 0.1000 to 0.5000 | success probabilities and risk-adjusted value |
| success.eta_tr | 0.5000 | 0.2000 to 1.0000 | success probabilities and risk-adjusted value |
| success.p_P | 0.9000 | 0.7000 to 0.9700 | success probabilities and risk-adjusted value |
| success.past_prior_a | 2.0000 | 1.0000 to 5.0000 | success probabilities and risk-adjusted value |
| success.past_prior_b | 2.0000 | 1.0000 to 5.0000 | success probabilities and risk-adjusted value |
| success.team_prior | 0.5000 | 0.2500 to 0.7500 | success probabilities and risk-adjusted value |
| success.sponsor_prior | 0.5000 | 0.2000 to 0.9000 | success probabilities and risk-adjusted value |
| success.progress_ratio | 0.8500 | 0.7000 to 1.0000 | success probabilities and risk-adjusted value |
| success.target_share | 0.8000 | 0.5000 to 1.0000 | success probabilities and risk-adjusted value |
| success.b_bar_U | 0.6000 | 0.3000 to 0.8500 | success probabilities and risk-adjusted value |
| success.a_J | 0.3000 | 0.0000 to 1.0000 | success probabilities and risk-adjusted value |
| pilot.T_pil | 0.2500 | 0.1000 to 0.5000 | pilot decisions |
| pilot.cost_share | 0.1500 | 0.0500 to 0.3000 | pilot decisions |
| pilot.fixed_cost | 50,000.0000 | 10,000.0000 to 200,000.0000 | pilot decisions |
| pilot.overrun_cap | 3.0000 | 2.0000 to 5.0000 | pilot decisions |
| decisions.Phi_base | 5.0000 | 3.0000 to 10.0000 | decision bandwidth and pace |
| decisions.e_launch | 1.0000 | 0.5000 to 2.0000 | decision bandwidth and pace |
| decisions.e_gate | 0.5000 | 0.2500 to 1.0000 | decision bandwidth and pace |
| decisions.e_regulated | 0.5000 | 0.0000 to 1.0000 | decision bandwidth and pace |
| decisions.e_appr_share | 0.3000 | 0.2000 to 0.5000 | decision bandwidth and pace |
| decisions.A_Phi | 0.2500 | 0.0000 to 1.0000 | decision bandwidth and pace |
| decisions.phi_per_TO_fte | 0.5000 | 0.2000 to 1.0000 | decision bandwidth and pace |
| decisions.phi_per_sponsor | 0.5000 | 0.2000 to 1.0000 | decision bandwidth and pace |
| decisions.delegation_uplift | 0.5000 | 0.2000 to 1.0000 | decision bandwidth and pace |
| decisions.delegation_risk | 0.5000 | 0.0000 to 1.0000 | decision bandwidth and pace |
| decisions.delta_V | 0.4000 | 0.1000 to 1.0000 | decision bandwidth and pace |
| decisions.eta_q | 1.0000 | 0.5000 to 2.0000 | decision bandwidth and pace |
| decisions.x_cap | 0.9500 | 0.8000 to 0.9900 | decision bandwidth and pace |
| decisions.governance_layers | 3.0000 | 2.0000 to 5.0000 | decision bandwidth and pace |
| decisions.concurrent_initiatives | 4.0000 | 1.0000 to 10.0000 | decision bandwidth and pace |
| decisions.transformation_office_fte | 2.0000 | 0.0000 to 10.0000 | decision bandwidth and pace |
| decisions.sponsors | 3.0000 | 1.0000 to 8.0000 | decision bandwidth and pace |
| decisions.delegation | 0.0000 | 0.0000 to 1.0000 | decision bandwidth and pace |
| decisions.existing_load_years | 1.0000 | 0.5000 to 2.0000 | decision bandwidth and pace |
| overrun.body_sigma | 0.2500 | 0.1000 to 0.4000 | cost overruns in the outcome distribution |
| shocks.kappa_keep | 0.6000 | 0.3000 to 0.8500 | leadership, vision and reorganization shocks |
| shocks.nu_V | 0.1500 | 0.0500 to 0.3000 | leadership, vision and reorganization shocks |
| shocks.vision_jump | 3.0000 | 1.5000 to 6.0000 | leadership, vision and reorganization shocks |
| shocks.owner_turnover | 0.3000 | 0.1000 to 0.6000 | leadership, vision and reorganization shocks |
| shocks.nu_K | 0.1500 | 0.0800 to 0.3000 | leadership, vision and reorganization shocks |
| shocks.eta_K | 1.0000 | 0.5000 to 2.0000 | leadership, vision and reorganization shocks |
| shocks.kappa_doc | 0.5000 | 0.2000 to 0.8000 | leadership, vision and reorganization shocks |
| shocks.key_persons_per_function | 2.0000 | 1.0000 to 6.0000 | leadership, vision and reorganization shocks |
| shocks.ctx_iota_loss | 1.0000 | 0.5000 to 2.0000 | leadership, vision and reorganization shocks |
| shocks.s_reuse_platform | 0.8000 | 0.6000 to 0.9500 | leadership, vision and reorganization shocks |
| shocks.s_reuse_on_platform | 0.5000 | 0.3000 to 0.7000 | leadership, vision and reorganization shocks |
| shocks.s_reuse_specific | 0.2000 | 0.0000 to 0.4000 | leadership, vision and reorganization shocks |
| shocks.C_rep_share | 0.1000 | 0.0500 to 0.2500 | leadership, vision and reorganization shocks |
| security.reval_share | 0.1000 | 0.0300 to 0.3000 | run, security and compliance costs, ceiling terms |
| security.c_int | 3,000.0000 | 1,000.0000 to 10,000.0000 | run, security and compliance costs, ceiling terms |
| security.c_cpl | 2,000.0000 | 0.0000 to 5,000.0000 | run, security and compliance costs, ceiling terms |
| security.autonomy_A | 1.0000 | 0.7000 to 1.0000 | run, security and compliance costs, ceiling terms |
| security.autonomy_U | 0.3000 | 0.1000 to 0.5000 | run, security and compliance costs, ceiling terms |
| security.h_f | 0.0500 | 0.0100 to 0.2000 | run, security and compliance costs, ceiling terms |
| security.h_u | 0.0000 | 0.0000 to 0.0000 | run, security and compliance costs, ceiling terms |
| security.L_inc_scale | 1.0000 | 0.3000 to 3.0000 | run, security and compliance costs, ceiling terms |
| security.C_s | 20,000.0000 | 5,000.0000 to 60,000.0000 | run, security and compliance costs, ceiling terms |
| security.L_max | 50,000,000.0000 | 5,000,000.0000 to 200,000,000.0000 | run, security and compliance costs, ceiling terms |
| security.tail_multiple | 10.0000 | 5.0000 to 30.0000 | run, security and compliance costs, ceiling terms |
| security.reviews_per_fte | 12.0000 | 6.0000 to 24.0000 | run, security and compliance costs, ceiling terms |
| security.reviewer_share | 0.0040 | 0.0010 to 0.0100 | run, security and compliance costs, ceiling terms |
| security.p_sec | 60,000.0000 | 30,000.0000 to 120,000.0000 | run, security and compliance costs, ceiling terms |
| security.buy_markup | 0.2500 | 0.1000 to 0.5000 | run, security and compliance costs, ceiling terms |
| security.buy_pooled_share | 0.1000 | 0.0200 to 0.3000 | run, security and compliance costs, ceiling terms |
| security.buy_integration_share | 0.3000 | 0.1000 to 0.6000 | run, security and compliance costs, ceiling terms |
| security.switching_cost_share | 0.6000 | 0.2000 to 1.5000 | run, security and compliance costs, ceiling terms |
| security.contract_years | 3.0000 | 1.0000 to 5.0000 | run, security and compliance costs, ceiling terms |
| security.pia_cost | 10,000.0000 | 3,000.0000 to 40,000.0000 | run, security and compliance costs, ceiling terms |
| security.redteam_cost | 30,000.0000 | 10,000.0000 to 150,000.0000 | run, security and compliance costs, ceiling terms |
| security.legal_review_cost | 15,000.0000 | 5,000.0000 to 50,000.0000 | run, security and compliance costs, ceiling terms |
| security.eval_data_cost | 20,000.0000 | 5,000.0000 to 100,000.0000 | run, security and compliance costs, ceiling terms |
| security.finops_share | 0.0300 | 0.0100 to 0.0800 | run, security and compliance costs, ceiling terms |
| security.vendor_mgmt_fte_per_vendor | 0.1000 | 0.0500 to 0.3000 | run, security and compliance costs, ceiling terms |
| security.incident_response_fte_per_10 | 0.5000 | 0.2000 to 1.0000 | run, security and compliance costs, ceiling terms |
| security.per_process_share | 0.3000 | 0.0500 to 1.0000 | run, security and compliance costs, ceiling terms |
| security.nist_rmf_initial_fte_months | 3.0000 | 1.0000 to 12.0000 | run, security and compliance costs, ceiling terms |
| security.nist_rmf_ongoing_fte | 0.2500 | 0.1000 to 1.0000 | run, security and compliance costs, ceiling terms |
| security.cyber_insurance_share | 0.0010 | 0.0003 to 0.0030 | run, security and compliance costs, ceiling terms |
| security.ir_retainer | 50,000.0000 | 20,000.0000 to 200,000.0000 | run, security and compliance costs, ceiling terms |
| security.vendor_mgmt_share | 0.0300 | 0.0100 to 0.0600 | run, security and compliance costs, ceiling terms |
| product.fast_frak_p | 0.1000 | 0.0300 to 0.1500 | product strategy: seat revenue at risk, migration, pricing |
| product.fast_frak_q | 0.8000 | 0.4000 to 0.9000 | product strategy: seat revenue at risk, migration, pricing |
| product.feature_frak_p | 0.0500 | 0.0100 to 0.1500 | product strategy: seat revenue at risk, migration, pricing |
| product.feature_frak_q | 0.5000 | 0.2500 to 0.9000 | product strategy: seat revenue at risk, migration, pricing |
| product.eps_seat | 1.0000 | 0.2500 to 1.0000 | product strategy: seat revenue at risk, migration, pricing |
| product.seat_lag_years | 1.0000 | 0.5000 to 2.0000 | product strategy: seat revenue at risk, migration, pricing |
| product.xbar_low_mult | 0.7000 | 0.5000 to 0.9000 | product strategy: seat revenue at risk, migration, pricing |
| product.xbar_default | 0.4000 | 0.2800 to 0.5700 | product strategy: seat revenue at risk, migration, pricing |
| product.eps_ad | 1.0000 | 0.5000 to 3.0000 | product strategy: seat revenue at risk, migration, pricing |
| product.outsource_ratio | 0.5500 | 0.4000 to 0.8000 | product strategy: seat revenue at risk, migration, pricing |
| product.e_I | 0.0400 | 0.0200 to 0.0800 | product strategy: seat revenue at risk, migration, pricing |
| product.e_E | 0.0660 | 0.0300 to 0.1200 | product strategy: seat revenue at risk, migration, pricing |
| product.L_outcome_mult | 1.6600 | 0.5000 to 5.0000 | product strategy: seat revenue at risk, migration, pricing |
| product.tR_ratio | 0.8000 | 0.3000 to 1.2000 | product strategy: seat revenue at risk, migration, pricing |
| product.eta_I_share | 0.0028 | 0.0000 to 0.0200 | product strategy: seat revenue at risk, migration, pricing |
| product.eta_E_share | 0.0110 | 0.0000 to 0.0500 | product strategy: seat revenue at risk, migration, pricing |
| product.p_sw_share | 0.0110 | 0.0000 to 0.0300 | product strategy: seat revenue at risk, migration, pricing |
| product.ups_E | 0.0000 | 0.0000 to 1.0000 | product strategy: seat revenue at risk, migration, pricing |
| product.chat_share | 0.0220 | 0.0080 to 0.0550 | product strategy: seat revenue at risk, migration, pricing |
| product.c_E_inf_share | 0.0055 | 0.0028 to 0.0166 | product strategy: seat revenue at risk, migration, pricing |
| product.delta_u | 0.3000 | 0.0000 to 1.6090 | product strategy: seat revenue at risk, migration, pricing |
| product.u_h_share | 0.2300 | 0.0000 to 0.4000 | product strategy: seat revenue at risk, migration, pricing |
| product.phi_margin | 0.5100 | 0.0000 to 0.9100 | product strategy: seat revenue at risk, migration, pricing |
| product.gamma_seat | 0.8000 | 0.7000 to 0.8500 | product strategy: seat revenue at risk, migration, pricing |
| product.entry_hazard | 0.2500 | 0.0500 to 1.0000 | product strategy: seat revenue at risk, migration, pricing |
| product.g_v | 0.0400 | 0.0000 to 0.1000 | product strategy: seat revenue at risk, migration, pricing |
| product.k_def | 0.2500 | 0.0000 to 0.5000 | product strategy: seat revenue at risk, migration, pricing |
| product.migration_years | 1.5000 | 1.0000 to 3.0000 | product strategy: seat revenue at risk, migration, pricing |
| product.mig_delta_range | 0.0800 | 0.0000 to 0.3000 | product strategy: seat revenue at risk, migration, pricing |
| product.mig_omega_range | 0.2500 | 0.1000 to 1.0000 | product strategy: seat revenue at risk, migration, pricing |
| product.mig_varpi_range | 0.8000 | 0.5000 to 0.9500 | product strategy: seat revenue at risk, migration, pricing |
| product.feature_dev_share | 0.0200 | 0.0050 to 0.0500 | product strategy: seat revenue at risk, migration, pricing |
| product.uplift_share | 0.0500 | 0.0000 to 0.1500 | product strategy: seat revenue at risk, migration, pricing |
| product.feature_cost_share | 0.0150 | 0.0020 to 0.0200 | product strategy: seat revenue at risk, migration, pricing |
| product.retention_dG | 0.0010 | 0.0000 to 0.0030 | product strategy: seat revenue at risk, migration, pricing |
| product.engineer_years_per_musd | 2.5000 | 1.0000 to 5.0000 | product strategy: seat revenue at risk, migration, pricing |
| product.platform_cost_share | 0.0300 | 0.0100 to 0.0500 | product strategy: seat revenue at risk, migration, pricing |
| capital.delta_K_compute | 0.2500 | 0.2000 to 0.3300 | capital charges |
| capital.owned_compute_share | 0.0000 | 0.0000 to 1.0000 | capital charges |
| capital.compute_capital_per_annual_dollar | 3.0000 | 2.0000 to 4.0000 | capital charges |
| capital.owned_opex_share | 0.3000 | 0.2000 to 0.5000 | capital charges |
| capital.robot_capital_per_fte | 250,000.0000 | 100,000.0000 to 600,000.0000 | capital charges |
| regime.public_myopia | 0.3000 | 0.0000 to 0.6000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.public_myopia_years | 2.0000 | 1.0000 to 3.0000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.public_latency_mult | 1.0000 | 1.0000 to 1.5000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.pe_latency_mult | 0.5000 | 0.3000 to 0.8000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.vc_horizon | 7.0000 | 5.0000 to 10.0000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.vc_revenue_multiple | 8.0000 | 4.0000 to 15.0000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.family_r_spread | -0.0100 | -0.0300 to 0.0200 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.family_horizon | 30.0000 | 10.0000 to 100.0000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.family_employment_pref | 0.1000 | 0.0000 to 0.3000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.family_latency_mult | 0.7000 | 0.4000 to 1.0000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.hybrid_myopia | 0.1500 | 0.0000 to 0.3000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.debt_rate | 0.0770 | 0.0583 to 0.1044 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.public_payout | 0.3000 | 0.0000 to 0.6000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.c_tx | 0.0200 | 0.0100 to 0.0400 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.w_cov | 1.0000 | 0.5000 to 1.0000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.Y_m | 2.0000 | 1.0000 to 3.0000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.vc_theta | 1.0000 | 0.5000 to 1.0000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.h_x | 1.0000 | 0.0000 to 1.0000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.T_sea | 1.0000 | 0.0000 to 2.0000 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| regime.pc_myopia | 0.0000 | 0.0000 to 0.1500 | regime values, IRR, MOIC, dip budgets, permanent-capital hurdle and debt |
| reliability.grounding | 0.5000 | 0.2000 to 0.9000 | failure modes, autonomy, tail losses |
| reliability.h_floor_share | 0.1000 | 0.0500 to 0.3000 | failure modes, autonomy, tail losses |
| reliability.d_m_review | 0.3000 | 0.1000 to 0.5000 | failure modes, autonomy, tail losses |
| reliability.d_m_approval | 0.8500 | 0.6000 to 0.9500 | failure modes, autonomy, tail losses |
| reliability.approval_thoroughness | 0.6000 | 0.4000 to 0.9000 | failure modes, autonomy, tail losses |
| reliability.rho_appr | 0.2500 | 0.1000 to 0.5000 | failure modes, autonomy, tail losses |
| reliability.b_ab | 0.3000 | 0.0000 to 0.6000 | failure modes, autonomy, tail losses |
| reliability.phi_v | 0.3000 | 0.0000 to 0.6000 | failure modes, autonomy, tail losses |
| reliability.m0 | 0.0010 | 0.0001 to 0.0100 | failure modes, autonomy, tail losses |
| reliability.kappa_h | 0.5000 | 0.2000 to 1.0000 | failure modes, autonomy, tail losses |
| reliability.injection_mult | 1.0000 | 0.0000 to 3.0000 | failure modes, autonomy, tail losses |
| reliability.sev_mult | 5.0000 | 1.0000 to 20.0000 | failure modes, autonomy, tail losses |
| reliability.lp_cut | 0.5000 | 0.2000 to 0.8000 | failure modes, autonomy, tail losses |
| reliability.lp_cost | 15,000.0000 | 5,000.0000 to 50,000.0000 | failure modes, autonomy, tail losses |
| reliability.mon_cut | 0.3000 | 0.1000 to 0.6000 | failure modes, autonomy, tail losses |
| reliability.mon_lag_days | 1.0000 | 0.1000 to 7.0000 | failure modes, autonomy, tail losses |
| reliability.mon_cost | 20,000.0000 | 5,000.0000 to 60,000.0000 | failure modes, autonomy, tail losses |
| reliability.kill_cap_mult | 20.0000 | 5.0000 to 100.0000 | failure modes, autonomy, tail losses |
| reliability.kill_cost | 10,000.0000 | 2,000.0000 to 40,000.0000 | failure modes, autonomy, tail losses |
| reliability.high_stakes_mult | 5.0000 | 2.0000 to 20.0000 | failure modes, autonomy, tail losses |
| reliability.cvar_q | 0.9500 | 0.9000 to 0.9900 | failure modes, autonomy, tail losses |
| reliability.kappa_cvar | 0.1000 | 0.0000 to 0.5000 | failure modes, autonomy, tail losses |
| reliability.cascade | 0.5000 | 0.0000 to 1.0000 | failure modes, autonomy, tail losses |
| reliability.provider_correlation | 1.0000 | 0.3000 to 1.0000 | failure modes, autonomy, tail losses |
| reliability.q_chg | 0.0000 | 0.0000 to 0.9000 | failure modes, autonomy, tail losses |
| reliability.ai_review_joint_error | 0.5000 | 0.1000 to 1.0000 | failure modes, autonomy, tail losses |
| reliability.diversity_cost | 20,000.0000 | 5,000.0000 to 80,000.0000 | failure modes, autonomy, tail losses |
| reliability.a_fm | 0.5000 | 0.0000 to 1.0000 | failure modes, autonomy, tail losses |
| reliability.churn_per_failure | 0.5000 | 0.0000 to 2.0000 | failure modes, autonomy, tail losses |
| reliability.bias_prevalence_ratio | 1.0000 | 0.5000 to 2.0000 | failure modes, autonomy, tail losses |
| reliability.eps_d | 0.5000 | 0.1000 to 1.0000 | failure modes, autonomy, tail losses |
| reliability.d_h_open_mult | 0.7500 | 0.5000 to 1.0000 | failure modes, autonomy, tail losses |
| reliability.L_max_event | 5,000,000.0000 | 1,000,000.0000 to 50,000,000.0000 | failure modes, autonomy, tail losses |
| reliability.J_s | 3.0000 | 2.0000 to 6.0000 | failure modes, autonomy, tail losses |
| reliability.d_c | 0.5000 | 0.2000 to 0.9000 | failure modes, autonomy, tail losses |
| reliability.L_c_share | 0.2000 | 0.0500 to 0.5000 | failure modes, autonomy, tail losses |
| measurement.inventory_cost_per_system | 5,000.0000 | 2,000.0000 to 15,000.0000 | Wave 0 scope and cost |
| measurement.classification_cost_per_system | 3,000.0000 | 1,000.0000 to 10,000.0000 | Wave 0 scope and cost |
| measurement.inventory_years | 0.2500 | 0.1500 to 0.5000 | Wave 0 scope and cost |
| measurement.process_mining_cost | 40,000.0000 | 15,000.0000 to 120,000.0000 | Wave 0 scope and cost |
| measurement.time_study_cost | 15,000.0000 | 5,000.0000 to 40,000.0000 | Wave 0 scope and cost |
| measurement.process_years | 0.2500 | 0.1000 to 0.5000 | Wave 0 scope and cost |
| measurement.sd_after_measurement | 0.3000 | 0.1500 to 0.5000 | Wave 0 scope and cost |
| accounting.icfr_redesign_cost | 50,000.0000 | 20,000.0000 to 150,000.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.T_B | None | 3.0000 to 5.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.u_novel | 0.4000 | 0.0000 to 0.8000 | GAAP path, ICFR timing, accountability floor |
| accounting.dc_share | 0.1670 | 0.0000 to 0.4000 | GAAP path, ICFR timing, accountability floor |
| accounting.T_cl | 0.1670 | 0.0800 to 0.2500 | GAAP path, ICFR timing, accountability floor |
| accounting.T_op | 0.2500 | 0.1000 to 0.5000 | GAAP path, ICFR timing, accountability floor |
| accounting.T_rem | 0.1000 | 0.0000 to 0.2500 | GAAP path, ICFR timing, accountability floor |
| accounting.T_dc | 0.2500 | 0.1000 to 0.5000 | GAAP path, ICFR timing, accountability floor |
| accounting.p_def | 0.2000 | 0.0500 to 0.4000 | GAAP path, ICFR timing, accountability floor |
| accounting.p_mw | 0.2000 | 0.0500 to 0.5000 | GAAP path, ICFR timing, accountability floor |
| accounting.L_mw | 5,000,000.0000 | 1,000,000.0000 to 20,000,000.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.C_itgc | 185,000.0000 | 16,000.0000 to 330,000.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.itgc_setup | 25,000.0000 | 10,000.0000 to 75,000.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.itgc_c_acc | 2,000.0000 | 1,000.0000 to 5,000.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.itgc_n_id | 2.0000 | 1.0000 to 5.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.itgc_perm_per_step | 2.0000 | 1.0000 to 4.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.itgc_n_chg | 12.0000 | 6.0000 to 24.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.interface_control_setup | 15,000.0000 | 5,000.0000 to 50,000.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.T_cw | 0.0192 | 0.0137 to 0.0384 | GAAP path, ICFR timing, accountability floor |
| accounting.D_bar | 0.1250 | 0.0200 to 1.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.T_sl | 2.0000 | 0.5000 to 5.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.c_del | 50,000.0000 | 10,000.0000 to 200,000.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.L_late | 2,000,000.0000 | 500,000.0000 to 10,000,000.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.C_fb | 100,000.0000 | 25,000.0000 to 200,000.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.c_fb | 30,000.0000 | 10,000.0000 to 100,000.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.t_sw | 0.1000 | 0.0000 to 0.5000 | GAAP path, ICFR timing, accountability floor |
| accounting.N_o | 24.0000 | 12.0000 to 48.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.p_cc | 0.0000 | 0.0000 to 0.0020 | GAAP path, ICFR timing, accountability floor |
| accounting.N_nm | 2,000.0000 | 200.0000 to 20,000.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.L_nm | 20,000.0000 | 5,000.0000 to 100,000.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.L_mm | 10,000,000.0000 | 2,000,000.0000 to 50,000,000.0000 | GAAP path, ICFR timing, accountability floor |
| accounting.restructuring_charge_share | 1.0000 | 0.5000 to 1.0000 | GAAP path, ICFR timing, accountability floor |
| jurisdiction.works_council_months | 4.0000 | 2.0000 to 9.0000 | works-council and union priors, effects bargaining |
| jurisdiction.union_months | 3.0000 | 1.0000 to 6.0000 | works-council and union priors, effects bargaining |
| jurisdiction.survivor_attrition | 0.0500 | 0.0100 to 0.1000 | works-council and union priors, effects bargaining |
| jurisdiction.replacement_cost_months | 6.0000 | 3.0000 to 12.0000 | works-council and union priors, effects bargaining |
| jurisdiction.eu_works_council_prior | 0.5000 | 0.0000 to 1.0000 | works-council and union priors, effects bargaining |
| talent.premium_agent | 0.1100 | 0.0500 to 0.4000 | AI engineer wage, hiring lead and ramp, hire or contract |
| talent.T_cn_months | 1.0000 | 0.5000 to 3.0000 | AI engineer wage, hiring lead and ramp, hire or contract |
| talent.delta_rp | 0.1500 | 0.0500 to 0.3000 | AI engineer wage, hiring lead and ramp, hire or contract |
| talent.u_ct | 0.5000 | 0.3000 to 1.0000 | AI engineer wage, hiring lead and ramp, hire or contract |
| talent.T_ct_months | 1.0000 | 0.0000 to 2.0000 | AI engineer wage, hiring lead and ramp, hire or contract |
| talent.hires_per_1000 | 2.0000 | 0.5000 to 5.0000 | AI engineer wage, hiring lead and ramp, hire or contract |
| talent.ai_share_of_developers | 0.1000 | 0.0200 to 0.3000 | AI engineer wage, hiring lead and ramp, hire or contract |
| location.onet_widening | 1.5000 | 1.0000 to 2.0000 | site wage index, O*NET transfer |
| residency.nu_inv_SCC | 0.0000 | 0.0000 to 0.0500 | data-residency mechanisms, in-region premium |
| residency.C_sw | 500,000.0000 | 100,000.0000 to 2,000,000.0000 | data-residency mechanisms, in-region premium |
| residency.F_tr | 50,000.0000 | 10,000.0000 to 200,000.0000 | data-residency mechanisms, in-region premium |
| residency.p_reg | 0.0000 | 0.0000 to 0.3000 | data-residency mechanisms, in-region premium |
| residency.T_lag | 0.0000 | 0.0000 to 1.0000 | data-residency mechanisms, in-region premium |
| pqc.cost_share_it | 0.1000 | 0.0300 to 0.3000 | post-quantum migration cost |
| pqc.it_share_revenue | 0.0500 | 0.0300 to 0.1000 | post-quantum migration cost |
| pqc.quantum_cost_mult | 2.0000 | 1.5000 to 3.0000 | post-quantum migration cost |
| pqc.quantum_deadline | 2,030.0000 | 2,029.0000 to 2,032.0000 | post-quantum migration cost |


Parameters linked to data/tasks/params.yaml: 159. Command-line or scenario overrides: 0.

## 14. Data sources and attributions

- This report uses information from the O*NET 31.0 Database by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA), used under the CC BY 4.0 license. The engine modified it: occupations and activities were converted, aggregated to standard units of work and linked to other sources. USDOL/ETA has not approved, endorsed or tested these modifications. O*NET is a trademark of USDOL/ETA.
- BLS Occupational Employment and Wage Statistics, May 2025 (U.S. Bureau of Labor Statistics; public domain): wages and staffing.
- SEC EDGAR XBRL filings (public): the Part I panel behind the accountability floor and margins.
- Anthropic Economic Index (Anthropic; data under CC BY): automation and augmentation patterns of activities.
- Eloundou, Manning, Mishkin and Rock, GPTs are GPTs (MIT License, copyright 2024 OpenAI): LLM exposure of occupations.
- Tomlinson, Jaffe, Wang, Counts and Suri, Working with AI (CC BY 4.0): AI applicability of occupations.
- Kwa et al. (2025), Measuring AI Ability to Complete Long Tasks, METR, arXiv:2503.14499: only fitted parameters (the 50 percent horizon, its doubling time and the logistic slope) are used, with citation. METR's run-level data has no license and is not bundled or redistributed.
- APQC Process Classification Framework: process category names only, with attribution to APQC (PCF is a trademark of APQC).
- Bending Spoons S.p.A., Form F-1 (SEC, 8 June 2026) and Form 6-K (28 October 2026), public filings: the permanent-capital presets (IRR hurdles and window, debt policy, covenant, cost of new debt). Used as one owner's disclosed policy, not as a benchmark for other owners.

---

This report is decision support, not a decision. It is produced by a model whose limits, validation record and the decisions it leaves to people are described in MODEL_RISK.md of the engine.

Required Notice: Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. All rights reserved, except as granted in LICENSE.md (PolyForm Noncommercial License 1.0.0). Commercial use requires prior written permission from the copyright holder (bs.akshay@gmail.com).

O*NET task statements in the playbook: This dataset includes information from the O*NET 31.0 Database by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). Used under the CC BY 4.0 license. O*NET® is a trademark of USDOL/ETA. The authors of this project have modified all or some of this information. USDOL/ETA has not approved, endorsed, or tested these modifications.
