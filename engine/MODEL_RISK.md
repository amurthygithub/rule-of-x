# Model risk statement: autofrontier

Written in the style of supervisory model risk guidance (Federal Reserve SR 26-2 and OCC Bulletin 2026-13, 17 April
2026, which supersede SR 11-7 of 2011), the NIST AI Risk Management Framework 1.0 (2023: govern, map, measure, manage)
and ISO/IEC 42001:2023 (AI management systems). SR 26-2 is guidance for banking organizations, and footnote 3 of its
attachment puts generative and agentic AI models outside its scope; the engine follows its structure as a style of
documentation, not because it applies to the engine or to the AI systems the engine plans. It is the engine's own
statement; it is not an attestation by any regulator or certifier. (SR 26-2 and OCC 2026-13 were verified at
federalreserve.gov and occ.gov by the Paper 2 theory pass, notes/p2_theory_fixes_v2.md Section 9.)

**Every report is decision support, not a decision.** The engine ranks options and quantifies their uncertainty.
People decide whether, when and how to automate work, and they remain accountable for those decisions.

**Authorship and declarations.** The author directed the research and made its decisions; AI agents drafted the text, code and proofs. Funding: the author received no funding for this work. Competing interests: the author declares no competing interests.

## 1. Intended use

- **Purpose.** An AI transformation vision, a phased roadmap and a people plan for one firm, scored with Part I's
  Rule-of-X frontier: which units of work to automate, augment, outsource or eliminate, in which order, at what
  cost and risk, under the firm's ownership regime.
- **Users.** Executives, finance, transformation and people leaders, with advisers who understand the inputs.
- **Decisions supported.** Prioritization of processes, the size and order of waves, the Wave 0 measurement scope,
  the readiness investments, the product pricing migration and the people plan's hiring and redeployment.
- **Out of scope.** Individual employment decisions, legal advice (labor law and data residency rules are model
  constraints, read at their primary sources on 29 October 2026), audit opinions on internal control, investment
  advice, and any decision about a named person.

## 2. Conceptual soundness

Each formula in `src/autofrontier/formulas.py` names the label it implements (TRACEABILITY.md):

- Part I: R*_X, the Gordon root v0, the full-automation ceiling R_max with c_mnt, c_sec, c_anc, c_err and the
  accountability floor a_min (eq:gordon, prop:dynamic, cor:ceiling).
- Core (theory_core): mode costs, review with a detection rate, augmentation, outsourcing windows, readiness,
  handoffs and all-or-nothing chains, transition NPV with parallel runs and rollback, pilots, the failure taxonomy
  (hallucination, automation bias, autonomy, pipelines, tail CVaR) and the score path (prop:tasks-*).
- Extensions (theory_ext): capability feasibility, the available universe, waves, decision bandwidth, shocks,
  organization and staffing, the competition game (prop:ext-*, cor:ext-game-engine).
- Regimes (theory_regimes), product (theory_product), accounting (theory_accounting, prop:acct-*), labor
  (theory_labor, prop:labor-*), competition (theory_competition), and the acquirer section (theory_acquirer:
  the permanent-capital regime of ass:acq-pc and prop:acq-pc, and the limits to buying growth of prop:acq-limits).

Status per formula: theory (proved in the notes and cross-tested against code/verify_part2_*.py where a reference
exists), spec (specified in notes/unified_model_spec.md without a proof), provisional (an engine rule awaiting
theory), superseded (kept for comparison). TRACEABILITY.md gives the counts.

**Rates.** All discounting is continuous: annual sources are converted once at load with ln(1 + r) and every rate
parameter is tagged annual or continuous (tests/test_rates.py). finance.r is the industry cost of capital (Damodaran,
January 2026), 0.0893 for software.

**Taxes.** finance.tau = 0.21 is the U.S. marginal statutory rate (26 U.S.C. 11(b)), right for marginal decisions on
savings. Part I's ceiling uses an average effective rate (central 0.18, params.yaml part1_ceiling.tau_cash_tax_rate).
Tax deductibility of AI development follows sec. 174A (domestic, psi = 1) and sec. 174 (foreign, psi_15 = 0.532),
independent of book capitalization (prop:acct-tax).

## 3. Assumptions and their grounding

Every parameter carries a grounding class (spec 21.1): a (sourced), b (precedent), c (calibrated or derived), d
(scenario: no measurement exists), setting or policy. Class d values are never reported as points: results that
depend on them are given as P10 to P90 ranges over the Monte Carlo or as Sobol bounds, and the report's assumptions
section lists every class d parameter with its range and the outputs it affects. The firm's own values (for example
decision bandwidth, change capacity, team ratios, success history, ICFR conditions) replace the scenario ranges.

**Limits that have no value.** A class d limit parameter whose params.yaml value is null (net debt per dollar of
revenue, deals a year, the size elasticity of hurdle headroom, series-review and foreign-investment review, consumer
law) takes its neutral value, so the limit is off, until a scenario or an override sets it. It has no sensitivity
range: the domain over which the reference script checks a result is never used as one.

**Permanent capital.** The hurdles, IRR window, debt policy and covenant are one owner's disclosed policy (Bending
Spoons, Form F-1, June 2026; cost of new debt from its 6-K of 28 October 2026). They describe that owner, not a
benchmark for others; the PE regime keeps the regimes section's 8 percent debt preset.

**Regulated status.** A unit is regulated if its activities' regulated class is not none (licensed sign-off, EU AI
Act high-risk with an EU nexus, other regulated classes), if it is in ICFR scope, or if the firm says so; the
reliability target plays no part. A unit's class is the most frequent class among its activities, and a tie goes to
the most demanding class: licensed sign-off, then EU AI Act high-risk (with an EU nexus), then ICFR, then any other
regulated class, then none. The rule is deterministic and never picks the weaker class.

**Accountability floor.** A control design over financial reporting is admissible only if no in-scope control
objective is left with a reasonable possibility of a material misstatement that is not prevented or detected on a
timely basis (AS 2201.A7, Regulation S-K Item 308(a)(3)); the engine reads "reasonable possibility" as an annual
probability above a remote threshold that no standard sets. The threshold is a scenario value with no central value:
every floor is reported at 1 percent and at 5 percent a year, and accounting.eps_bar only selects the one the
single-number ceiling uses. The floor is the cheapest admissible design; the consequence of a material misstatement is
reported, never traded against cost. The cheapest design is conditional on the papers' illustrative layer parameters,
so each design is reported with its break-evens in the cross-type common mode and in the human miss rate on
AI-missed items (automation bias); the firm's control-testing evidence and its auditor decide. The direct cost common
to every design is the KPMG 2025 SOX program budget of the firm's revenue class plus the accelerated-filer average
audit fee (Audit Analytics), with the S&P 500 fee ratio as the low bound.

**Growth spend basis.** Only selling and marketing above a maintenance level buys growth (finance.sm_basis =
netted, the central basis of Paper 1 since 2 November 2026, author decision 7). Growth spend is the S&M share less
finance.sm_maint_base (25.1 percent of revenue: the median S&M share, in the previous year, of firm-years growing at
or below the year's median; class c, Paper 1 empirics), and zero below it; the rest of S&M is a cost line like
overhead, and the spend ratio is finance.spend_ratio_netted (0.99). All S&M as growth spend (finance.spend_ratio,
3.3) and none of it are bounds: the report and the lever map state the ranking on each. The lead lever depends on the
basis. At the six panel positions of Part II, cutting G&A comes before automating the growth engine at five on the
netted basis and at none on the all-S&M bound, and automating the growth engine leads only where S&M is well above
the maintenance level (the growth corner).

**Disruption and realization.** The realized share (McKinsey) and the success logit (production rates) come from
outcome surveys that already include leadership and strategy changes, so the base case does not also cancel work in
flight on leadership or vision shocks (shocks.disruption_haircut, scenario disruption_shocks). Reorganization freezes
delay work in the plan and in the Monte Carlo.

**Growth weight.** The data do not identify a firm's decision weight on growth (Paper 1, decision D-1). Owner weights
come from the regime presets (the Gordon root at the owner's rate, exit and permanent-capital weights) or a firm input;
recommendations that depend on the level of the weight are reported at X = 2.5, 5 and 9 or the firm's range, with sign
flips flagged. finance.X_default (5) is an evaluation point, used only when the Gordon equation has no root.

**Playbook confidence tiers (def:playbook-tier).** A: the step's recommendation is bound by a feasibility filter
the backtest supports (capability horizon, physical work, permissibility). B: it rests on the cost crossover or a
reliability gate with sourced inputs, which the backtest does not validate. C: the decision to automate, or to use
AI at all, changes when one class d input moves to an end of its range with the others at their defaults, or the
process's value is positive in fewer than playbook.tier_c_prob = 0.8 of the Monte Carlo draws. Gates use the
firm's acceptance values (tier3_policy) where given and say so.

## 4. Limitations

- **Capability.** The horizon path rests on METR's fitted 50 percent horizons for software tasks (Kwa et al. 2025);
  transfer to other domains, computer-use tasks (40 to 100 times shorter) and physical work is uncertain and is
  carried as scenarios (plateau, constant hazard, slow physical doubling).
- **Reliability.** Detection rates, hallucination and misbehavior rates come from the literature summarized in
  params_reliability.yaml; consequential misbehavior rates, autonomy multipliers and control effects are scenario
  only.
- **Industry priors.** Damodaran's ratios aggregate listed U.S. firms; private firms and public employers differ,
  and five large employment groups are flagged as weak priors. Outside software the labor share per function is
  the software prior, so people costs are flagged low confidence.
- **Occupations and tasks.** O*NET task content is U.S.-based; outside the U.S. the dispersion is widened, but the
  mix is not re-estimated.
- **Labor law and residency.** Rules not confirmed at a primary source are listed as unverified in every report
  that uses them. Rules move (UK thresholds, the DPF appeal, Indian notifications, EU AI Act dates). Under the AI
  Act as amended by Regulation (EU) 2026/1744 (in force 27 July 2026), high-risk obligations apply from 2 December
  2027 for the Annex III areas and from 2 August 2028 for systems under Annex I (dates from recitals 40 and 46; the
  operative amendment of Article 113 was not read). A unit in an Annex III area counts as high risk only when the
  firm has an EU nexus and the plan's horizon runs past the applicable date (regulation.eu_ai_act_annex_iii_from);
  the engine models no Annex I system.
- **ICFR scope.** Scope by process, step, system, integration and policy is a precedent-based prior (class b); the
  firm's own scoping and its auditor decide.
- **Growth spend.** How much S&M buys growth is not observed. The netted basis is central, all S&M and none of it are
  bounds, and the growth-engine ranking moves between them (Section 3); maintenance R&D is all R&D, an upper bound on
  the engineering lever.
- **Optimization.** The program is solved by a heuristic with multi-start polishing; it is not guaranteed optimal.
  Minimax regret across scenarios is reported for robustness.

## 5. Validation record

- Unit and limiting-case tests of formulas; cross-implementation tests against the theory's reference scripts
  (code/verify_part2_{core,ext,product,regimes,accounting,competition,labor}.py, imported by path).
- Property tests of the comparative statics the theory proves (for example: higher autonomy raises tail loss,
  automation bias makes extra review less effective, pipeline reliability falls with length, provider concentration
  widens the loss distribution, a tighter covenant needs more waves).
- Paper sync: the running example (data/examples/invoice_chain.yaml and .json) is reproduced by the engine's
  formulas, and its inputs resolve to the engine's defaults (tests/test_paper_examples.py).
- Regression tests for reported defects (QA/ISSUES.md), golden snapshots of three firms, determinism with a fixed
  seed, a Tier-0-only run that reports wide ranges, and privacy guards.
- Backtest of the activity model: notes/backtest_notes.md (outside the engine).

## 6. Monitoring

Each report records the engine version, the seed and the sha256 of the notes, defaults.yaml and the data files it
used. Re-run when the inputs change by a tier, when a named scenario's trigger occurs (a capability plateau, an
AI-native entrant, a strict regulation, an energy shock), when the data contract changes, or quarterly during a
program. Compare realized savings, success rates and parallel-run lengths with the plan; past outcomes enter the
next run as the firm's own success history.

## 7. Change control

- The notes the engine implements are hashed in src/autofrontier/NOTES_LOCK.json; tests/test_change_control.py fails
  when they change without an engine update (tools/check_sync.py --accept after the re-check).
- Golden snapshots change only through tools/accept_golden.py, with a CHANGELOG.md entry.
- TRACEABILITY.md is regenerated from the code and checked by tests.
- Findings go to QA/ISSUES.md with the side (engine, example, data or notes) that was wrong.

## 8. Human decision rights

People decide: the scope of automation, the plan and its waves, the reliability targets and risk appetite (policy
parameters), redundancies and their timing, the pricing of products, and every exception. The engine never makes
employment decisions about individuals and never acts on systems. A required manual fallback is kept for in-scope
financial-reporting steps that agents perform.

## 9. Privacy and security of the engine

Runs are local, with no network calls and no telemetry (tests block sockets during a run). Files are written only
inside the chosen output folder (path traversal refused); spreadsheet formula injection is neutralized; the run log
holds no input values.
