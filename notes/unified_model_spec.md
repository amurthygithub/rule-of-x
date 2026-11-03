# Unified model spec, v1 (lead author, 29 Oct 2026)

This is the shared brief for Part II (theory of what to automate) and Part III (engine). Everyone builds against this notation. Theorists may refine definitions, but any change must be reported back with the reason, so the engine and the paper stay consistent.

## 0. Purpose and the author's 12 questions

The author wants a model that takes a firm's financial and organizational data and returns three things: an automation and AI transformation vision, a roadmap, and the people needed to execute a durable transformation. Part II must answer these questions:

1. How granular can the spend breakdown get, and what is automating worth, based at least in part on spend?
2. How do we standardize units of work and standard enterprise functions, to decide what is worth automating?
3. How does the curve change when outsourcing an activity costs less per unit than AI?
4. What is full integration and automation worth, compared with manual, low-cost work?
5. What do competition, AI-native startups, AGI and fusion energy do to the curve? What *should* be automated, as opposed to what *could* be?
6. How sensitive is the "available to automate" universe to taxes, regulation, morality, religious belief and altruism?
7. What do the speed of LLM capability growth, world models, organizational context engines and databases do to that universe?
8. What happens to collaborative work as the solo "10x" individual contributor develops?
9. Where are the breakpoints in the scaling model?
10. Which specific jobs are worth automating with AI, which outsourcing, and which leaving alone?
11. How integrated must an organization's data be before AI automation delivers its full results?
12. Can all of this be one mathematical model that an AI system runs on organizational data to produce the strategy?

## 1. Link to Part I

Part I's firm-level objects carry over unchanged:
- R_X = Xg + m, with m = m0 − σ − kg.
- m0 = γ − a, where γ is gross margin and a is non-discretionary operating cost.
- Growth technology g = G + λ σ^α h(s).
- R*_X = m0 + (X − k)G + Π. The firm's own weight is X = v'(s), the marginal q of revenue (Prop dynamic).
- Envelope results (Prop envelope, eq dRdzeta) and Cor priorities.
- Cor ceiling: R_max = (1−τ)(1 − c_c − f − a_min) + (1−k)G.
- Prop entry: under free entry the score tends to XG + (r−G)k + ρ.
- Lemma prices: pass-through φ.

**Reserved symbols** (do not reuse with another meaning): α, β = 1/α, τ (profit tax), m, m0, γ, a, a_min, σ, k, g, G, λ, h, s, s̄, X, Δ, Π, R∞, ρ (rent), r (cost of capital), φ (pass-through), c_c, c_h, f, ψ (tax deductibility of growth capital), D, θ (margin persistence in Lemma valuation), μ (pull multiplier in the calibration), ℓ.

Part II works *below* these objects. Every activity-level decision must aggregate into changes in (γ, a, σ-productivity λ, k, c_c, a_min, G_i, φ), so that a strategy can be scored by Part I's R*_X and firm value.

## 2. Units of work: the standard taxonomy (Q2)

Four levels:
- **Function** F. A standard enterprise function list of about 15 to 20 functions, cross-industry. Examples: product and engineering; customer support; customer success; professional services; sales; marketing; finance and accounting; HR; legal and compliance; IT; procurement; facilities; operations and fulfilment; risk, audit and governance; executive. Map it to the APQC Process Classification Framework where possible.
- **Occupation** o. SOC 2018 / O*NET-SOC codes. Wages come from BLS OES.
- **Activity** j. The O*NET Detailed Work Activity (DWA, about 2,000). It rolls up to Intermediate (IWA) and Generalized (GWA, 41) work activities. Each occupation has task statements linked to DWAs, with importance and frequency ratings, which give an activity's time share within the occupation.
- **Process** p. An ordered chain or DAG of activities that delivers a business output: order-to-cash, procure-to-pay, record-to-report, hire-to-retire, ticket-to-resolution, lead-to-close, idea-to-release, and so on. It has an output unit (an invoice, a ticket, a release) and an annual volume.

**The standard unit of work** is an activity-hour of a given DWA in a given occupation. Its cost is the loaded wage. Output units per process translate activity-hours into units per invoice, per ticket, and so on.

## 3. Activity economics and modes (Q1, Q3, Q4, Q10)

Each activity j has:
- annual volume v_j (units)
- in-house human time per unit t_j (hours)
- loaded wage w_j (gross wage times 1 + τ_L, where τ_L covers payroll tax and benefits)
- required reliability r̄_j
- loss per undetected error L_j
- difficulty or task length d_j, measured in human hours to complete one instance

There are five modes μ ∈ {H, O, A, U, N}, with unit costs:
- **H (in-house):** c_H = w t.
- **O (outsource):**
  - c_O = p_O + κ_O w t + ζ_O.
  - p_O is the vendor price. It reflects vendor wage arbitrage and the vendor's own AI adoption, so p_O falls over time.
  - κ_O is the management and coordination share: transaction cost, Williamson asset specificity.
  - ζ_O is the risk and quality premium (IP, data protection, rework).
  - Feasible only if the activity is separable, meaning low asset specificity, and permissible.
- **A (automate with AI):**
  - c_A = π n + ψ_A(ι, r̄) w t + ε_A(ι) L + F_A/(v T_A).
  - π n is the inference price per unit of work: price per token times tokens, or price per agent-step times steps.
  - ψ_A is the human review fraction. It falls with data readiness ι and rises with required reliability and regulation (a mandatory oversight floor ψ_min).
  - ε_A is the residual error rate.
  - F_A is the build and integration fixed cost, amortized over T_A years.
  - Feasible only if capability covers the task (Section 6) and data readiness ι_j ≥ ι*_j.
- **U (augment):** c_U = w t/(1+β_U) + π n_U. Here β_U is the productivity gain; it is available at lower capability than A.
- **N (eliminate):** the activity is dropped because the process is redesigned. The cost is zero, but there may be a value loss.

**Handoffs:**
- Activities in a process are linked by edges (j, j′).
- A handoff cost η(μ_j, μ_j′, ι) per unit applies when the modes differ or the work crosses an organizational boundary. η(A, A, ι→1) → 0.
- The cost of a process with mode vector μ is:
  - C_p(μ) = Σ_j v_j c_{μ_j, j} + Σ_{(j,j′)} v η(·) + latency value + O-ring error term.
- Process success probability is Π_j r_j (Kremer 1993).

**Core questions for the theorists:**
- (a) The cost frontier of a single activity across modes. When c_O < c_A, the value of automation is c_min(H,O) − c_A, not c_H − c_A.
  - The automation curve, meaning the share of spend automated as AI cost falls, shifts right by the outsourcing option.
  - Outsourced activities have their own decline path, because vendors adopt AI, so the incumbent's decision is about timing.
- (b) Process complementarity. Show when the optimal mode vector is all-or-nothing on a process (supermodularity from handoffs), and derive the value of full integration versus a manual, low-cost chain (Q4).
- (c) The value of granularity (Q1):
  - The firm observes spend at tier T (Section 9).
  - Estimated automation value has prior uncertainty from imputing finer levels.
  - Derive the value of information from moving down a tier, as an expected gain from better mode assignment.
  - Show where coarse data suffices: when imputed activities are far from the cost crossovers.

## 4. Data readiness and integration (Q11)

- ι_j ∈ [0,1] is the share of activity j's inputs that are machine-accessible: digitized, permissioned, joinable and of known quality. Process readiness is ι_p; with a weakest-link structure, ι_p = min over the critical path, or the product.
- Integration investment I(ι) is convex.
- Readiness affects A in two ways:
  - feasibility: ι_j ≥ ι*_j;
  - cost: ψ_A(ι) and ε_A(ι) fall with ι.
- **Required result:** a threshold readiness ι* at which full automation of a process becomes optimal. Below it, only augmentation pays.
- Also characterize the "J-curve": integration costs come first and benefits later (Brynjolfsson, Rock, Syverson).
- The engine needs an operational readiness index built from observable proxies:
  - share of processes with system-of-record coverage;
  - API availability;
  - master-data quality;
  - identity resolution;
  - number of systems per process;
  - share of unstructured inputs.

## 5. Permissibility and the "available to automate" universe (Q6)

The universe has four nested layers:
- **feasible** (capability and readiness)
- **permissible**: law and regulation, professional licensing and mandatory sign-off, and ethics and religion as hard exclusions
- **preferred**: soft penalties
- **economical**: net value > 0 after the above

Parameter vector θ:
- **Taxes:**
  - τ_L, payroll taxes and benefits on labor
  - τ, profit tax, with ψ the deductibility of AI capital (expensing)
  - R&D capitalization rules
  - a hypothetical automation tax τ_A on c_A
- **Regulation:**
  - a mandatory human-oversight floor ψ_min by risk class (EU AI Act high-risk categories)
  - licensing that requires a human signatory: audit opinions, legal advice, medical decisions
  - data-protection limits on ι
- **Ethics and religion:** an exclusion set E(θ) of activities, and a penalty ω_j per automated unit, for example pastoral care, end-of-life decisions or judgments of persons.
- **Altruism:** owner utility b per human job retained, which is a wedge on the wage. Customer preference for human service enters as a demand penalty δ_H on revenue for customer-facing automation.

**Required:**
- The available universe is A(θ) = set of activities whose optimal mode is A, U or N. Its spend share is S_A(θ).
- Comparative statics of S_A in each component of θ.
- A sensitivity (tornado) layout the engine can compute.

## 6. Capability, cost and technology dynamics (Q5, Q7)

**Capability.** AI capability as a reliable task horizon, after METR, "Measuring AI ability to complete long tasks":
- H(t) = H0 · 2^{(t − t0)/T_d}, the length of task in human hours that AI completes at a given reliability.
- Activity j is feasible for A at time t if H(t) · κ_ctx(ι, context engine) ≥ d_j · χ(r̄_j). χ rises with the reliability required.
- World models extend feasibility to physical and embodied activities, with a lag. The engine should carry a physical/cognitive flag per activity.
- Organizational context engines, enterprise data platforms and long-term memory raise κ_ctx. They lower the effective difficulty of firm-specific activities.

**Price.** The inference price per unit of capability falls at rate δ_π a year (Epoch: 9 to 900× a year, depending on the threshold; Gundlach et al.: 5 to 10× a year for frontier models). Energy is a share s_E of inference cost; fusion lowers it.

**AGI** is the limit H → ∞ for cognitive work. Then the binding constraints are inference cost, accountability (a_min), physical tasks, permissibility and data readiness.

**Adoption timing.** The option to wait arises because c_A and F_A fall over time. Adopt when the savings flow exceeds (r + δ_F) F_A + the expected cost decline. Derive the optimal adoption date per process.

**Competition and AI-native entrants:**
- Entrants have no legacy labor, no stranded integration cost, ι ≈ 1 and full automation where feasible.
- Under free entry, prices converge to the entrant's unit cost (Part I, Prop entry). The incumbent then keeps only (1 − φ) of its savings, and automation becomes *defensive*: required to stay viable.
- **Should vs could:**
  - (i) value-creating: retained savings exceed cost;
  - (ii) defensive: needed to keep unit cost within the entrant's cost plus a switching-cost premium;
  - (iii) could but should not: feasible, but NPV < 0 or not permissible;
  - (iv) not feasible.

## 7. Organization: collaboration vs the solo 10x contributor (Q8)

- **Team production with coordination costs** (Becker and Murphy 1992; Brooks):
  - Output of n humans with AI leverage A_g is Y(n) = n A_g y − χ n(n−1)/2.
  - AI raises A_g and may lower χ (summaries, shared context), or raise it (review load).
  - AI agents are team members with their own coordination cost χ_a.
  - Derive the optimal human team size n*, and the breakpoint where n* = 1: the "solo 10x" individual contributor directing agents.
- **Knowledge hierarchies** (Garicano 2000): AI lowers the cost of acquiring knowledge and of communicating it. Derive the implications for spans of control and layers.
- **Output for the engine:** the residual human organization, as roles, headcount and seniority mix. Plus the transformation team, with sizes tied to the roadmap:
  - data and integration engineers ∝ integration gap;
  - AI and agent engineers ∝ automated processes;
  - process owners ∝ redesigned processes;
  - change managers ∝ affected FTE;
  - risk, governance and audit ∝ regulated activities;
  - domain SMEs.

## 8. Breakpoints (Q9)

Derive each threshold formally, and have the engine report where the firm sits relative to each:
1. cost crossover c_A = min(c_H, c_O);
2. volume threshold v* = F_A / [T_A (c_min − c_A^var)];
3. reliability threshold, with the review fraction going to 0 as ε → 0;
4. readiness threshold ι*;
5. process percolation: a whole process flips when capability crosses its hardest activity, which produces step changes in automated share;
6. organizational: n* falls to 1;
7. market: entrant cost < incumbent price − switching cost;
8. Part I thresholds: share saturation, and the ceiling growth rates of 31, 39, 48 and 55%;
9. regulatory class boundaries.

## 9. Engine: input tiers and outputs (Q1, Q12)

**Input tiers.** Each tier is optional except Tier 0.
- **Tier 0, public financials:** revenue, COGS or cost of revenue, R&D, S&M, G&A, SBC, D&A, capex, headcount and industry (NAICS/SIC). From a 10-K or XBRL.
- **Tier 1:** opex by function or cost center (GL trial balance mapped to the function taxonomy).
- **Tier 2:** headcount and compensation by role and title, mapped to SOC/O*NET-SOC, with location (wage index) and FTE/contractor status.
- **Tier 3:** vendor and outsourcing spend by category; systems inventory (applications per process, API availability); process volumes (tickets, invoices, orders).
- **Tier 4:** process event logs or time studies (optional).

**Imputation.** Missing tiers are filled with priors, and the engine carries uncertainty forward. Priors:
- function shares by industry and size (from SEC data and benchmarks);
- role mix by function and industry (BLS OES industry staffing patterns);
- activity time shares by occupation (O*NET);
- process volumes per revenue dollar (benchmarks).

**Optimization:**
- Choose μ per activity, ι investment per process and an adoption date per process, maximizing firm value. That is Part I's objective with X = marginal q, net of transformation cost and θ penalties.
- Subject to: feasibility, permissibility, a budget, and change-capacity constraints (the FTE affected per year a firm can absorb).
- Solve as a MILP, or as process-level enumeration with a greedy outer loop.

**Outputs:**
1. **Vision:** the target operating model, as the mode mix by function and the expected change in (γ, a, λ, k), giving ΔR*, Δ firm value and the new frontier position.
2. **Roadmap:** phased waves, with dependencies (data integration first), timing from the capability path, and NPV, payback and risk per wave.
3. **People:** the residual organization by role and the transformation team by phase.
4. **Sensitivity:** a θ tornado; capability-speed scenarios; competition scenarios.
5. **Confidence:** intervals on every number, from imputation uncertainty.
6. **Breakpoint report:** distance to each threshold, per process.

## 10. Deliverables by agent, and file locations

- **Theory core** (Sections 3, 4 and 8): `part2/theory_core.tex`, with proofs in `part2/proofs_core.tex`, and `code/verify_part2_core.py`.
- **Theory extensions** (Sections 5, 6 and 7): `part2/theory_ext.tex`, `part2/proofs_ext.tex`, `code/verify_part2_ext.py`.
- **Data:** `data/tasks/`, a `notes/data_sources_part2.md` log, and crosswalk tables.
- **Engine:** the `engine/` package, named `autofrontier`, with tests and an example run on the synthetic firm.
- **Literature:** `part2/literature_part2.tex`, new `refs.bib` entries in a separate file `part2/refs_part2.bib`, and `notes/ref_verification_part2.md`.

## 11. House rules

- Plain prose; no em-dashes.
- Every number must have a source or come from a script.
- Every reference must be verified, with no fabricated citations.
- Proofs must be complete, with a numerical or symbolic check in a verify script.
- Report notation changes back to the lead author.

## 12. Data contract between the data agent and the engine

The data agent writes, and the engine reads. All files go in `data/tasks/`, as UTF-8 CSV with a header row. Every file has a matching entry in `notes/data_sources_part2.md` giving source, URL, retrieval date, license and transformations.

- `functions.csv`: function_id, function_name, description, apqc_category (if mapped), cost_bucket (one of cogs, rnd, sm, ga), customer_facing (0/1)
- `occupations.csv`: soc (6-digit, 2018), onet_soc (if finer), title, wage_median, wage_mean (USD per year, BLS OES national, latest year), employment, physical_share (0 to 1, the share of the occupation's activity time that is physical or on-site), licensed_signoff (0/1)
- `activities.csv`: dwa_id, dwa_title, iwa_id, gwa_id, gwa_title, physical (0/1), exposure_llm (Eloundou et al. measure, with a column naming which one), ai_usage (Anthropic Economic Index share, if mappable), est_task_hours (typical human time per instance, with a method note), regulated_class (none, high_risk_eu, licensed)
- `occ_activity.csv`: soc, dwa_id, time_share (sums to 1 per soc), with the method recorded: task importance × frequency, mapped to DWAs
- `industry_staffing.csv`: naics (2 to 4 digit), soc, emp_share (sums to 1 per naics); from BLS OES industry-specific estimates
- `function_occ.csv`: function_id, soc, weight (the share of function headcount in that occupation; a prior used when only function spend is known)
- `industry_function_shares.csv`: naics or sic, size_band, function_id, share_of_revenue_prior (mean and sd); from SEC XBRL line items plus documented benchmarks
- `processes.csv`: process_id, process_name, function_id, output_unit, typical_volume_per_musd_revenue (with source or "assumed")
- `process_activities.csv`: process_id, step, dwa_id, critical_path (0/1)
- `params.yaml`: outsourcing price ratios p_O/(w t) by function or GWA (with ranges and sources); coordination overhead κ_O; AI cost parameters (price per unit of work by activity class, review fractions, error rates); capability path (H0, t0, T_d, with source); price decline δ_π; energy share s_E; payroll loading τ_L; regulatory oversight floors.

Where a number is assumed rather than sourced, mark it `assumed: true` and give a range. The engine must work with partial data: missing files fall back to documented defaults.

## 13. Capital per unit of work, and transition costs (author request, 29 Oct 07:00)

The author asked for two additions: the capex each unit of work requires, and the cost of running parallel, duplicative systems and processes while the transformation is executed.

**13.1 Capital per unit of work.** Each mode μ for activity j can need capital per unit of annual volume, K_{μj}: computing capacity owned, devices and robotics for physical activities, integration and platform builds that are capitalized, and capitalized internal-use software.
- Upfront investment is I_{μj} = K_{μj} v_j at adoption.
- Replacement capex runs at δ_K K_{μj} v_j a year, where δ_K is the depreciation and obsolescence rate. For accelerators δ_K is high, consistent with Remark rem:assumptions(c) of Part I.
- The annualized capital charge per unit is (r + δ_K) K_{μj}.

On the cash (FCF) basis, the upfront investment hits FCF when it is made. In steady state, replacement capex lowers m. Capex tied to new volume enters Part I's k: k = capital per dollar of new revenue.
- Mode choice must use the full cost: c_{μj} plus (r + δ_K) K_{μj}.
- Required result: the substitution condition at activity level generalizes Part I's Cor substitution (da > g* dk). For efficiency automation at constant volume the condition is Δc_j > (r + δ_K) ΔK_j. For capacity that scales with growth it also includes g K. State both.
- The cash-basis Rule of 40 and the economic-value objective then rank capital-heavy automation differently. Show how.

**13.2 Transition: parallel running, duplication and stranded costs.** When activity or process p moves from mode μ0 to μ1 at date t_a, three kinds of cost arise.
- **Parallel-run period.** For T_par years the firm runs both:
  - It bears the legacy cost c_{μ0} on a share (1 − ϱ(t)) of volume and the new cost c_{μ1} on ϱ(t), where ϱ is the ramp from 0 to 1.
  - On top of that comes a duplication premium: for the whole parallel period, legacy capacity is kept at a share ω_par of full cost to allow rollback.
  - Reconciliation work costs ν_rec c_H v.
  - Duplicate system licenses and infrastructure add to the bill.
- **Stranded and one-time costs S_p:**
  - severance and redeployment (s_w months of wages per affected FTE, with redeployment share ρ_d; use another symbol if ρ clashes with Part I's rent ρ);
  - contract break fees for outsourcing vendors and legacy licenses;
  - write-off of undepreciated legacy assets (non-cash, but relevant to GAAP margins);
  - a productivity dip, the J-curve, during the ramp.
- **Rollback risk.** With probability p_fail the new mode fails, and the firm reverts and bears the parallel costs again.

**Required results:**
- the NPV of a transition including these terms;
- the payback extension caused by T_par;
- a breakpoint condition for transition (savings flow × remaining horizon > F_A + I + PV of parallel-run and stranded costs);
- how the optimal parallel-run length trades rollback risk against duplication cost;
- at program level, the dual-running cost of migrating several processes at once. This creates a sequencing constraint: dual-running budget and change capacity per period. Characterize the optimal wave structure: few large waves versus many small ones. Use a convex dual-running cost, or a fixed program overhead per wave.
- Map these to Part I: the transition depresses m (cash and GAAP) temporarily, which shows up as a Rule-of-40 dip. Quantify the dip and its duration, so the roadmap can show the score path through the transformation.

**Ownership:**
- the theory core agent covers 13.1 and the single-process parts of 13.2;
- the theory extension agent covers adoption timing with parallel runs, and the program-level sequencing and change-capacity results;
- the data agent supplies parameter ranges: parallel-run durations, duplication premia, severance norms, contract break fees and depreciation lives, sourced where possible, otherwise marked assumed;
- the engine implements everything, and the roadmap reports the score path, including the transition dip.

## 14. Probability of success, and organizational decision-making capacity (author request, 29 Oct 07:03)

**14.1 Success and failure.** Treat each transition (process p, wave w) as a risky project, not a deterministic one.
- The outcome is a benefit-realization fraction b_p ∈ [0, 1], with full success at b = 1, partial success in between, and failure (with rollback, Section 13.2) at b = 0 plus rollback costs.
- The success probability π_p depends on observable drivers:
  - data readiness ι_p;
  - process complexity (number of activities, handoffs, exceptions);
  - required reliability and regulatory class;
  - change intensity (affected FTE);
  - team capability and the share of experienced staff;
  - executive sponsorship;
  - vendor and technology maturity, linked to the capability margin H(t)·κ_ctx − d_j χ(r̄_j): the further capability exceeds the task requirement, the higher π;
  - concurrency load (14.2).
  Use a logistic or proportional-hazard form with documented assumed coefficients unless sources exist.
- Learning: π rises with the number of earlier successes in the program (an experience curve), so early waves should be chosen partly for learning value.
- Correlated failure: waves sharing a platform or data layer have correlated outcomes, with a common shock.
- Stage gates: pilot then scale. A pilot of cost F_pilot reveals information about b_p. Derive the value of the pilot as an option, the optimal gate rule, and when to skip piloting.
- The objective becomes risk-adjusted expected value, and the engine also reports outcome distributions (P10/P50/P90 of value and of the Rule-of-40 path) and the probability that the program meets its target.

**14.2 Decision-making capacity.** An organization has limited bandwidth to make and execute decisions, and it is distinct from change capacity (affected FTE per period, Section 13).
- Decision bandwidth Φ per period, in "decision units": leadership attention, governance reviews and approvals. Each initiative consumes e_i units at launch and at each gate.
- Decision latency ℓ_dec, the time from proposal to approval. It rises with governance layers and load. Delay costs value because capability, prices and competitors move (Section 6).
- Congestion: when load L exceeds bandwidth Φ, either initiatives queue (latency rises), or quality falls and success probability drops. A form like π_p = π_p^0 · q(L/Φ), with q decreasing, would do.
- AI can expand Φ by preparing analysis, drafting and monitoring, but accountable approval stays human, as with the accountability floor a_min of Part I.
- Decision rights and hierarchy (Garicano 2000): pushing decisions down raises Φ but may lower π for high-risk processes.

**Required results:**
- the optimal number of concurrent initiatives given Φ, change capacity and dual-running costs;
- the cost of decision latency;
- when to expand decision capacity (for example a transformation office, or delegated authority) and what it is worth;
- how bandwidth limits the pace of the roadmap.
This is a breakpoint too: beyond a load threshold, adding initiatives lowers expected value.

**Ownership:**
- the theory core agent covers process-level success probability, partial realization, and the pilot as an option (stage gate);
- the theory extension agent covers the program portfolio: learning, correlated failure, the decision-bandwidth constraint, congestion and latency, their interaction with change capacity and wave structure, and the value of expanding decision capacity;
- the data agent supplies parameter ranges with honest source-quality flags: IT project outcome and overrun evidence (for example Flyvbjerg and Budzier), survey-based transformation success rates (flag self-reported surveys), and generative-AI pilot-to-production rates (flag weak methodology where it applies);
- the engine implements risk-adjusted optimization, Monte Carlo outcome distributions, stage gates and the decision-bandwidth constraint, and reports P10/P50/P90 and the probability of meeting the target.

**Inputs the engine should ask for (Tier 3 organizational):**
- governance layers and approval steps per initiative size;
- the number of concurrent major initiatives today;
- the record of past transformation outcomes, if known;
- transformation office capacity;
- sponsor assignment.
Default to industry priors with wide ranges when absent.

## 15. Leadership change, context discontinuity, vision overhauls and reorganizations (author request, 29 Oct 07:42)

Transformations run for years. Over that time the people, priorities and structure that launched them change. Model these as regime shocks that arrive during the program.

**15.1 Shocks.** Four shock types arrive as (possibly correlated) Poisson processes:
- **Sponsor or leadership change** (CEO, sponsoring executive, CIO or CAIO), at hazard h_L. Expected tenure is 1/h_L, from data where available.
- **Vision overhaul**: a change in strategic objective, at hazard h_V. It is often triggered by a leadership change, so allow h_V to jump after one.
- **Reorganization**, at hazard h_R. It changes process ownership, decision rights and team boundaries.
- **Context loss**: departure of key people who hold tacit process knowledge. Model it as a hazard h_K per critical role, or as a depreciation rate of the organizational context stock.

**15.2 Effects on the program.**
- **Success.** A sponsor change resets sponsorship, a driver of ϖ_p (Section 14). The new leader keeps the program with probability κ_keep, rescopes it or cancels it.
- **Vision overhaul.** The objective is re-optimized. Assets built so far keep a fraction ϑ_reuse of their value. The fraction is high for modular data and integration platforms and low for vision-specific builds. Re-planning costs C_replan.
- **Reorganization.**
  - In-flight initiatives freeze for T_freeze, which lowers the decision bandwidth Φ (Section 14.2).
  - Handoff costs η change, and organizational boundaries move.
  - Some process owners turn over, which hits ϖ.
- **Context loss.** Losing context raises review shares and error rates and lowers readiness ι, and it slows transitions. Organizational context engines, documented processes and data platforms act as insurance: they cut the context lost per departure by a factor (1 − κ_doc). That gives a value of context continuity.

**15.3 Required results (owner: the theory extension agent):**
- Program value under shock hazards. Show that value falls with the hazards, and how much falls on payback-heavy programs.
- A breakpoint: when expected sponsor tenure is shorter than payback plus parallel-run time, sequencing should front-load quick, durable wins. Otherwise expected value falls steeply. State the condition.
- The value of robustness: when to prefer modular, vision-agnostic investments (high ϑ_reuse), such as data integration and platforms, over vision-specific ones. This links to the readiness and "big push" results of the core section.
- The value of context continuity, as an insurance value of documentation and context engines against key-person and leadership loss.
- Commitment devices that lower the effective h_V or raise κ_keep: board-level targets, a transformation charter, multi-year funding. Give their value as an option.
- How these shocks interact with decision bandwidth, change capacity and wave structure. Reorganization freezes favor fewer, decoupled waves.

**15.4 Engine.**
- Monte Carlo over shock arrivals in the outcome distributions.
- Inputs, at Tier 3 organizational:
  - sponsor and leadership tenure to date;
  - planned or likely reorganizations;
  - key-person concentration (the number of people who hold critical process knowledge);
  - documentation and context-engine coverage.
- Defaults come from data on CEO and executive turnover. Practitioner surveys on CIO/CDO tenure and reorganization frequency must be flagged as such.
- The report shows:
  - the program's sensitivity to leadership change;
  - the recommended quick-win front-loading;
  - the share of investment that is vision-agnostic.

**15.5 Data and literature.**
- **Data:** executive and CEO turnover rates and tenures, from academic sources first (for example Kaplan and Minton 2012; Jenter and Kanaan 2015), then reputable practitioner data, flagged; strategic change after succession; reorganization frequency, flagged if it comes from surveys.
- **Literature:**
  - organizational memory (Walsh and Ungson 1991);
  - knowledge depreciation and turnover (Argote, already in);
  - escalation and de-escalation of commitment (Staw);
  - abandonment options (Myers and Majd 1990);
  - CEO succession and strategic change.
  Every item must be verified.

## 16. Ownership regime: public, private, private equity and hybrid (author request, 29 Oct 07:46)

The speed and impact of a transformation, and which activities clear the bar, depend on who owns the firm and what returns its stakeholders expect.

**16.1 Regime parameters.** A regime ϱ_own ∈ {public, private (founder or family), PE-backed, VC-backed growth, hybrid} sets:
- **the discount or hurdle rate r_own**: WACC for public firms; a target IRR for PE (gross and net, with the preferred-return hurdle); higher rates for VC; possibly lower rates for family firms;
- **the horizon**: an infinite going concern, or a hold period T_hold followed by an exit;
- **the valuation rule at the horizon**: for public firms, a market multiple of revenue or FCF, with the investor screening weight of Part I's Lemma valuation; for PE, an exit multiple of EBITDA, M_exit, so each dollar of run-rate saving at exit is worth M_exit dollars; for VC, growth is valued at exit;
- **short-term pressure**: for public firms, a penalty on reported-earnings dips and missed guidance (myopia weight θ_my on near-term GAAP margin); for PE, leverage covenants that cap the transition dip (net debt/EBITDA ≤ cov);
- **financing constraints**: cash available for transformation capex and dual running, and leverage;
- **stakeholder terms**: dividend and buyback expectations, employment preferences (owner altruism, Section 5), reputational and regulatory exposure to layoffs, and the SBC and dilution tolerance of public and VC-backed firms;
- **governance and decision speed**, which feeds Section 14.2: PE and founder firms decide fast (high Φ, low latency); public firms run board and disclosure cycles.

Hybrids combine these:
- a public firm with a controlling holder or dual-class shares: long horizon with public disclosure;
- PE minority stakes, or a PIPE;
- a take-private in which the transformation runs during the hold;
- carve-outs;
- state or nonprofit ownership (optional).

**16.2 Required results** (owner: a corporate-finance theorist):
- **Regime-specific value of a transition** (Section 13 and 14 NPVs at r_own, horizon and terminal rule). Show where rankings flip.
  - PE capitalizes run-rate cost savings at M_exit, which favors fast cost-outs with payback inside T_hold.
  - Public firms with a high growth weight (Prop dynamic) favor the growth engine.
  - Family firms put more weight on employment and patience.
- **Speed:** the optimal pace (waves, front-loading) by regime. A hurdle rate above WACC raises the breakpoint thresholds of Section 8. A short hold shortens the payback each wave can have.
- **Impact metrics by regime:** ΔR* and Δ value for all regimes; IRR and MOIC for PE; the EPS and guidance path for public firms.
- **Dip budget:** the Rule-of-40 and EBITDA dip during transitions (core prop:tasks-scorepath), constrained by covenants for PE and by the myopia penalty for public firms. Derive the constrained wave structure.
- **When a change of ownership pays:** the value of taking a firm private to execute a transformation (avoiding the dip penalty and earning the exit multiple) against its costs (control premium, leverage cost and risk). State the condition.
- **Mapping to Part I:** the regime sets the effective weight X (marginal q for a value-maximizing owner; an exit-multiple weight for PE), the discount rate and the horizon. Show how R*_X and the frontier choice differ.

**16.3 Engine.**
- Add a regime input with parameter presets: r_own, T_hold, M_exit, covenants, myopia weight, dividend policy, employment preference, decision speed. Every preset carries sources or is marked assumed.
- The optimizer's objective and constraints switch by regime.
- Report regime-specific outputs:
  - IRR and MOIC (PE);
  - the EPS and Rule-of-40 path against guidance (public);
  - value per stakeholder group;
  - a side-by-side comparison of the same firm under different regimes.

**16.4 Data and literature.**
- **PE returns and hold periods:** Kaplan and Schoar 2005; Harris, Jenkinson and Kaplan 2014.
- **Buyout value creation:** Guo, Hotchkiss and Song 2011.
- **Operational engineering in PE:** for example Bernstein and Sheen 2016, on restaurants.
- **Private versus public investment:** Asker, Farre-Mensa and Ljungqvist 2015.
- **Managerial myopia:** Stein 1989; the Graham, Harvey and Rajgopal 2005 survey, flagged as a survey.
- **Family firms:** for example Villalonga and Amit 2006.
- **Covenant evidence:** for example Chava and Roberts 2008.
- **Exit multiples for software:** practitioner data, flagged.

All must be verified.

## 17. AI product strategy (author approved, 29 Oct 07:55)

Sections 3 to 16 cover how the firm runs. This section covers what the firm sells. It has to sit at the same depth and feed the same Part I parameters, so that the engine produces one plan covering both product and operations.

**17.1 Objects.**
- **Product lines** i, each with revenue S_i and a pricing model:
  - seat-based: p_seat × seats;
  - usage-based: p_u × units;
  - outcome-based: p_o × outcomes, such as resolutions, documents or transactions;
  - hybrid.
- **Customer segments**, each with seat counts tied to the customers' own occupations. Map seats to the SOC occupations whose work the product supports. Support agents for a help-desk product is one example.
- **AI features or AI-native products** f, each with:
  - development cost, which draws on the engineering activities of Sections 3 and 4;
  - a build, buy or partner choice for models: own model, API, or open weights;
  - adoption over time, using Bass diffusion with innovation and imitation coefficients;
  - a price uplift or new revenue;
  - inference COGS per unit of usage (tokens × π, Section 6), which lowers gross margin;
  - effects on retention (G_i, net revenue retention) and on demand pull λ.

**17.2 Mechanisms.**
- **Labor-substituting products and value-based pricing.** An AI agent that does a customer's work can be priced as a capture share θ_cap of the customer's labor cost saved. Competition and AI-native entrants (Section 6, Prop entry) push θ_cap toward the entrant's cost-plus floor. Rents come only from scarce inputs ρ: proprietary data, embedded workflows, distribution and trust.
- **Seat compression.** As customers automate (their own Section 3 decisions), the seats tied to exposed occupations shrink, which puts seat-based revenue at risk. Use O*NET exposure and the capability path to project seat elasticity by customer occupation.
- **Pricing-model migration.** Moving from seats to usage or outcomes protects revenue. It has migration costs and risks: customer pushback, forecastability, revenue-recognition changes, and a transition dip, as in Section 13.
- **Gross-margin dynamics.** AI products start at lower gross margins (ICONIQ 2026: 45%, rising to a projected 59%). The inference-price decline raises margins only to the extent prices are sticky (pass-through φ).
- **Interaction with operations.** The firm's own automation lowers the cost to serve. Product AI changes support volume and the services mix. TAM expands as customers' labor budgets become software budgets, which raises G.

**17.3 Required results** (owner: a product-economics theorist):
1. The optimal price and capture share for labor-substituting AI under competition.
2. Revenue at risk from seat compression, and the threshold at which migrating the pricing model pays, net of migration cost and risk.
3. The optimal AI feature portfolio and the build/buy/partner choice for models.
4. The gross-margin path, and when AI product margins converge with subscription margins.
5. The combined product and operations plan, and how the product side shifts Part I's γ, λ, G_i, G and φ, and so R*_X and the frontier.
6. Breakpoints: the seat-compression threshold, the margin crossover, the competitive price floor, and the adoption tipping point.
7. When to cannibalize your own seat revenue before an entrant does.

**17.4 Engine.**
- **Inputs (Tier 1 and 3, product):**
  - revenue by product line and pricing model;
  - seats and usage;
  - NRR and GRR;
  - the mix of customer occupations behind the seats;
  - candidate AI features, with cost estimates;
  - inference usage per customer;
  - competitor pricing, if known.
- **Outputs:**
  - a product AI roadmap;
  - a pricing-migration plan;
  - revenue at risk;
  - the gross-margin path;
  - all integrated with the operations roadmap, the people plan and the regime-specific metrics.

**17.5 Data and literature.**
- **Data:**
  - Bass diffusion parameters, from a meta-analysis such as Sultan, Farley and Lehmann 1990, verified;
  - AI product gross margins (ICONIQ, already cited);
  - public outcome-based pricing examples, such as per-resolution pricing of AI support agents, verified from vendor pages and flagged as list prices;
  - evidence on seat compression (likely thin; flag it);
  - inference usage per task (assumed).
- **Literature:**
  - information-goods pricing (Shapiro and Varian 1998; Sundararajan 2004 on nonlinear pricing);
  - Bass 1969;
  - cannibalization and product-line design (Moorthy and Png 1992, if verifiable);
  - value-based pricing;
  - recent work on pricing and competition in AI products, verified;
  - platform and data advantages.

## 18. Extraneous factors: cybersecurity, maintenance and other ancillary costs (author request, 29 Oct 07:56)

These factors change the unit cost, the speed (gating and latency) and the scope (what may be automated at all).

**18.1 Run, maintain and revalidate.** Automated and augmented modes carry ongoing costs beyond inference and review.
- **Annual maintenance:** M_A = μ_m F_A per year. This covers prompt and agent upkeep, evaluation suites, monitoring and observability, data-pipeline upkeep and drift correction.
- **Revalidation** at each model upgrade or vendor deprecation, every T_up years, at cost C_reval. Vendors' published model-deprecation cycles set T_up for API-based builds.
- **Technical debt:** maintenance rises with the number of integrations and the coupling between them (Sculley et al. 2015).
- **Build versus buy:** vendors amortize maintenance across customers, so maintenance shifts the choice toward buying (SaaS or agent platforms) and away from in-house builds. Lock-in and switching cost offset this.

**18.2 Cybersecurity and AI-specific risk.**
- **Exposure** e_j rises with:
  - the sensitivity of the data the activity touches;
  - the agent's autonomy, meaning its write and transaction rights;
  - integration breadth, the systems reachable;
  - the external input surface, which carries prompt-injection risk.
- **Expected incident loss** = h_inc(e_j, s_sec) · L_inc,j. Here h_inc is the incident hazard, and it falls with security investment s_sec.
- **Optimal security investment:** use the Gordon and Loeb (2002) logic, which gives a bound on investment as a share of expected loss. Treat it as given only after verification.
- **Fixed compliance costs:** SOC 2 and ISO/IEC 42001, the NIST AI RMF, privacy impact assessments, AI-specific red-teaming, and insurance.
- **Security and compliance review bandwidth** Φ_sec (reviews per period) gates deployments, like decision bandwidth (Section 14.2). Review latency adds delay.
- **Scope:** an activity is out of scope when its expected incident loss exceeds its savings, or when the firm's risk appetite (part of θ in Section 5) excludes the data class.

**18.3 Other ancillary costs.**
- training and change management per affected FTE;
- legal, IP and contract review;
- data labeling and evaluation datasets;
- incident response capacity;
- vendor management;
- FinOps for inference spend;
- duplicate tooling during the transition (links to Section 13).

**18.4 Required results.** Owner: the core theorist for the unit-cost, scope and breakpoint parts; coordinate with the extension theorist's bandwidth notation for the gating part.
- the full-cost unit cost of A and U including maintenance, revalidation and expected incident loss;
- how these shift the crossover and volume breakpoints;
- build versus buy with maintenance and lock-in;
- optimal security investment per process;
- scope exclusion conditions;
- deployment speed limited by security review bandwidth, and the value of adding review capacity;
- how ancillary costs scale: fixed, per process, or per unit. Coarse spend data tends to understate them; quantify by how much.

**18.5 Engine.**
- **Inputs:**
  - data classification of the systems behind each process;
  - security team capacity;
  - the current compliance certifications;
  - the vendor-versus-build preference;
  - any known incident history.
- **Default parameters** are in defaults.yaml, sourced or marked assumed.
- **Report:** a security and compliance section (exposure by process, required controls, review queue and the delay it causes), and a total-cost-of-ownership view per wave.

**18.6 Data and literature.**
- **Data:** practitioner data on breach costs (for example the IBM/Ponemon Cost of a Data Breach report, flagged); vendors' published model-deprecation policies (verified pages); compliance cost ranges (flagged or assumed); maintenance cost shares (assumed unless sourced).
- **Literature:**
  - Gordon and Loeb 2002;
  - Anderson and Moore 2006;
  - Sculley et al. 2015, hidden technical debt in ML systems;
  - Greshake et al. 2023, on indirect prompt injection;
  - the NIST AI RMF 1.0 (2023);
  - ISO/IEC 42001:2023;
  - the OWASP Top 10 for LLM applications (practitioner).

## 19. Paper–engine synchronization and the engine test program (author request, 29 Oct 08:02)

**19.1 Synchronization.** The paper and the engine must say the same thing.
- **Traceability matrix**, generated by script into `engine/TRACEABILITY.md` and an appendix table in the paper:
  - every engine formula maps to the paper result it implements, by LaTeX label, with spec section and theory-notes reference;
  - every paper result maps to its engine function, or is marked "not implemented, reason";
  - every default parameter maps to its params.yaml or defaults.yaml entry and its source.
- **Cross-implementation tests:** where a theory verify script has a reference implementation (code/verify_part2_*.py), an engine test calls both on random inputs and checks agreement to tolerance.
- **Single source of numbers:** every number Part III of the paper reports about the synthetic firm or a public firm is generated by the engine and inserted from its JSON output by script. None is typed by hand.
- **Change control:**
  - the engine records the paper version and theory-notes hashes it was built against;
  - a check fails when notes change without an engine update;
  - the CHANGELOG records formula changes.

**19.2 The test program.** It is run by independent agents, not the builder.
1. **Functional:** every module, the CLI commands, every report section and every input tier.
2. **Regression:**
   - golden outputs for the synthetic firm and two to three variant firms, with fixed seeds;
   - snapshot tests that fail on any unexplained change;
   - a documented procedure for accepting intended changes.
3. **Corner cases:**
   - empty or zero volumes; a single employee;
   - every activity infeasible; every activity feasible;
   - c_O < c_A; ι = 0 and ι = 1; capability → ∞;
   - permissibility excluding everything;
   - extreme parameters at the ends of every range;
   - negative growth; a loss-making firm;
   - regimes with infeasible covenants;
   - a product with no seats.
4. **Scenarios:** every scenario flag and regime preset, plus combinations of them.
5. **Input data quality:**
   - malformed CSV/XLSX; wrong types; missing columns; duplicate rows;
   - unmapped titles or GL accounts; inconsistent totals across tiers;
   - currency or unit mismatches; outliers; partial tiers.
   Each must produce an actionable validation message or a documented fallback, never a silent wrong answer.
6. **Error handling:**
   - solver failure falls back to the heuristic;
   - timeouts;
   - invalid configuration;
   - clear exit codes and messages.
7. **Stability:**
   - determinism under seeds;
   - numerical stability, with no NaN or inf in outputs;
   - Monte Carlo convergence diagnostics, meaning results are stable as draws increase;
   - the heuristic and the MILP agree on small cases.
8. **Performance:**
   - run time and memory on firms of 100, 2,000, 20,000 and 100,000 employees;
   - profiling of hot spots;
   - stated budgets: the synthetic mid-market firm in under two minutes; a large firm in under fifteen minutes on a laptop.
9. **Security and privacy:**
   - no network calls, tested by blocking sockets;
   - writes only inside the output folder, with path-traversal tests;
   - spreadsheet formula injection neutralized in CSV/XLSX outputs;
   - no input data in logs.
10. **Stakeholder acceptance:** persona agents run the engine on the synthetic firm and on variants, review the outputs from their seat, and file issues:
   - CFO;
   - CHRO;
   - CIO and CISO;
   - PE operating partner;
   - public-company board member or investor;
   - transformation or PMO lead;
   - head of product;
   - internal audit and risk.
   The CFO checks NPV, IRR, score paths, and GAAP against cash. The CHRO checks the people plan, the treatment of ethical parameters and change capacity. The CIO and CISO check readiness and security. The PE partner checks regime outputs and the hold-period plan. The board member checks the EPS and guidance path, and the dip. The transformation lead checks the feasibility of the waves. The head of product checks product strategy. Internal audit and risk check traceability, assumptions and the control environment around the tool.

**Issue tracking.** All findings go to `engine/QA/ISSUES.md`, with severity, steps to reproduce and status. A fix cycle follows, then a full re-run. The paper's Part III reports the test program and its results: pass counts and coverage.

## 20. Modern theoretical grounding, and quantum computing (author request, 29 Oct 08:13)

**20.1 Prefer recent theory.** The author wants the paper anchored in theory and evidence from the AI era, 2018 to 2026. Older work stays only where it is the canonical foundation and still distinctly applicable. In that case the paper says why, and pairs it with the modern treatment. Examples of pairings:
- **Boundaries of the firm:** Coase and Williamson, with AI agents lowering transaction costs (the "Coasean singularity" literature, Shahidi et al. 2025, if verified).
- **Hierarchies:** Garicano 2000, with AI in knowledge hierarchies (Ide and Talamas, if verified).
- **O-ring:** Kremer 1993, with recent work on chained AI errors and human-AI combination (for example Agarwal, Moehring, Rajpurkar and Salz on radiology).
- **Task-based automation:** Acemoglu and Restrepo 2018 to 2022, and Acemoglu 2025.
- **AGI scenarios:** Korinek and Suh 2024.
- **Data:** Jones and Tonetti 2020; Farboodi and Veldkamp.
- **Market structure of foundation models:** Korinek and Vipra.
- **Firm value and generative AI:** Eisfeldt, Schubert and Zhang.
- **Adoption:** Bick, Blandin and Deming; Humlum and Vestergaard.
- **Expertise:** Autor and Thompson.

Every item must be verified.

The theory sections then engage these results. Where a modern result changes or sharpens one of ours, the section says so, and adjusts the result if needed.

**20.2 Quantum computing**, treated factually and without hype:
- **(a) Post-quantum cryptography migration** as a known security cost inside the transformation horizon: NIST FIPS 203, 204 and 205 (August 2024), and NIST's transition guidance on deprecating quantum-vulnerable algorithms (verify NIST IR 8547 and its dates). It adds to the ancillary and security costs of Section 18, with an inventory, a migration effort and a deadline.
- **(b) Quantum computing as a capability scenario**, for optimization, simulation and cryptanalysis. Uncertainty is explicit, and any claim of practical advantage for business optimization is treated as unproven unless a verified source shows it. The engine gets a quantum scenario flag that changes only parameters with stated justification. By default it changes nothing except the PQC cost.

**20.3 Process.**
- A modernization literature agent maps each model component to modern theory and evidence, in `notes/modern_theory_map.md`.
- Its bibliography goes in `part2/refs_modern.bib`, and the lead author merges and deduplicates it later.
- It drafts `part2/literature_modern.tex`.
- After the current theorists finish, an integration theorist revises the theory sections to engage the modern results.

## 21. Pressure testing by practitioner panels, and grounding of every assumption (author request, 29 Oct 08:19)

**21.1 Assumption grounding.** "Assumed" is not an acceptable final state for a parameter that drives a result. For every parameter in params.yaml, defaults.yaml, the calibration and the numerical examples, one of these must hold:
- **(a) Sourced:** peer-reviewed, government, standards body, audited filings, or documented practitioner data with a stated method.
- **(b) Grounded by precedent:** an analogous, documented estimate from a comparable setting, with the analogy stated and the range widened to cover the uncertainty of transfer.
- **(c) Calibrated from our own data:** SEC panels, O*NET, BLS, AEI, or engine inputs supplied by the firm.
- **(d) A free scenario parameter:** reported only as a scenario dimension, never as a baseline point estimate. Any claim that depends on it must be stated conditionally.

Theory examples are labeled illustrative, and their values should still be plausible against precedent.

The assumptions register is `notes/assumptions_register.md`. For each parameter it records:
- the value or range;
- the grounding class (a to d);
- the source or precedent;
- the quality flag;
- where the parameter is used (results, engine modules);
- its sensitivity rank, from the engine tornado.

**21.2 Pressure-test panels.** These run once the paper is assembled, in addition to the academic referees (theory, financial economics, econometrics, labor and IO, operations or management science).
- **Corporate executives:** CEO or COO, CFO, CHRO, CIO and CISO, chief product officer, transformation lead, board director, general counsel or compliance.
- **Investors and capital markets:**
  - long-only public equity portfolio manager;
  - hedge fund or short-seller skeptic;
  - sell-side equity research analyst;
  - PE operating partner;
  - growth or VC investor;
  - credit analyst and leveraged-finance banker;
  - M&A and take-private investment banker;
  - asset-management stewardship and governance lead;
  - pension or endowment CIO.
- **Risk and assurance:** internal audit; a regulator's perspective.

Each panelist reviews the paper and an engine run from their seat. Their brief is to try to break the argument:
- challenge assumptions that lack precedent;
- find claims that would not survive a diligence process, an investment committee or an audit committee;
- check that the numbers reconcile with how practitioners measure (EBITDA versus FCF, GAAP versus adjusted, IRR and MOIC conventions, covenant definitions);
- flag anything a sophisticated reader would see as naive.

Findings go to `notes/pressure_test/<panel>.md`, and are consolidated into a single issues list with severity. Then:
- the lead author and theorists revise;
- a second round checks the fixes;
- the protocol appendix records the panels, the findings and the dispositions.

## 22. Applying every constraint to the Part I frontier itself (author request, 29 Oct 08:20)

Each constraint in Sections 3 to 21 must also act on Part I's frontier, ceiling and calibration, wherever it applies.

1. **Full-cost ceiling.** Extend Cor ceiling to R_max = (1−τ)(1 − c_c − f − a_min − c_mnt − c_sec − c_anc) + (1−k)G. The new terms are, as shares of revenue at full automation:
   - c_mnt: maintenance and revalidation;
   - c_sec: security operations, expected incident loss after optimal controls, post-quantum migration amortization, and AI-specific compliance beyond a_min;
   - c_anc: other ancillary costs (evaluation, FinOps, vendor management).
   Avoid double counting with a_min, which covers accountability: SOX certification and the integrated audit, D&O, legal. Recompute tab:ceiling and the growth thresholds (31, 39, 48 and 55%) using grounded values, from the assumptions register and params.yaml blocks security_and_maintenance and product. Report the new numbers.
2. **Product mix in gross margin.** γ reflects the AI product share and its margin path (Section 17).
3. **Capital per unit of work** enters k (Section 13.1).
4. **The attainable frontier over time.** Transition dips, success probability, rollback, parallel running, and change, decision and security-review capacity limit how fast a firm can move toward its frontier. Define the attainable frontier at horizon t, and the expected (risk-adjusted) frontier, and prove their properties. Leadership, vision and reorganization hazards lower expected attainment.
5. **Ownership regime** sets X, r and the horizon. Different owners choose different points on the same frontier, and pace differently (Section 16).
6. **Horizons calibration** (Part I Section 6, calibrate_horizons.py, tab_calib). Add:
   - the full-cost terms;
   - capacity-limited speed;
   - success probability and transition dips;
   - regime variants.
   State the changes in the headline ranges.
7. **Consistency.** The abstract, introduction and conclusion must use the revised numbers.

Owner: a Part I integration theorist. That theorist edits sections/model.tex, sections/appendix_proofs.tex, code/verify_theory.py, sections/horizons.tex, code/calibrate_horizons.py and sections/tables/tab_calib.tex. Part II results are cited, never re-derived.

## 23. Agentic misbehavior, errors and hallucination (author request, 29 Oct 08:26)

**23.1 In the model.** Replace the single raw error rate with a taxonomy of AI failure. For each activity:
- (i) **Ordinary errors** at rate e_j. They are detectable by review with catch rate d_e.
- (ii) **Hallucination**, meaning confident fabrication, at rate h_j. Review catches less of it (d_h < d_e), and it depends on the task type: retrieval-grounded or open-ended.
- (iii) **Agentic misbehavior**:
  - out-of-scope or unauthorized actions;
  - tool misuse;
  - specification gaming or reward hacking;
  - following injected instructions (this overlaps with Section 18);
  - deceptive or concealing behavior.
  These are rare, carry heavy-tailed losses, and rise with the agent's autonomy level a_j (read only, then draft, then act with approval, then act autonomously; write and transaction rights) and with task horizon length.
- (iv) **Common-mode and systemic failure.** When many activities rely on one model or provider, outages, regressions after model updates, and shared vulnerabilities produce correlated failures across processes.
- (v) **Cascading failure** in multi-step and multi-agent pipelines. Errors propagate and compound along the chain. This extends the O-ring lemma to agent pipelines.

**Controls:**
- review share ξ;
- the reviewer's catch rate, which falls as AI accuracy rises (automation bias, complacency): show the non-monotone effect;
- least-privilege permissions, which cut loss severity;
- guardrails and evaluations;
- monitoring with a detection lag;
- mandatory human approval for irreversible actions;
- kill switches and rollback;
- model diversity or redundancy, which cuts common-mode correlation;
- insurance and liability allocation.

**Required results:**
- the optimal autonomy level per activity, trading human cost against expected and tail loss (CVaR, or a heavy-tail expectation);
- review effectiveness under automation bias, including when more review buys less;
- the compound reliability of agent pipelines, and the maximum pipeline length for a target reliability;
- the portfolio effect of common-mode failure, and the value of model diversity;
- scope exclusion for irreversible, high-stakes actions;
- the misbehavior loss floor c_err that enters Part I's ceiling (Section 22);
- effects on success probability and on the product side (customer-facing errors cause churn, refunds and liability).

Owners:
- the core theorist, for the activity-level and pipeline results, autonomy and review;
- the extension theorist, for portfolio and common-mode effects and governance;
- the Part I integration theorist, for c_err in the ceiling;
- the engine builder, for implementation and a report section: "AI failure modes and controls".

**23.2 Evidence.** A reliability-evidence agent grounds the parameters in verified sources. Its output goes to data/tasks/params_reliability.yaml, part2/refs_reliability.bib and notes/data_sources_reliability.md. The sources must cover:
- hallucination benchmarks and domain studies (law, medicine, finance);
- agent reliability benchmarks, including pass^k reliability on repeated trials;
- multi-agent failure taxonomies;
- reward hacking and scheming evaluations from labs and independent evaluators;
- automation bias in human oversight;
- incident data.
Flag the quality of each source, and do not fabricate.

**23.3 In our own process.** The protocol appendix reports the errors and hallucinations that the research agents themselves produced and the safeguards caught. That covers:
- reference details corrected or dropped, including references the lead agent suggested from memory that verification failed;
- numerical errors found by audits;
- stale claims;
- data and element errors;
- code bugs;
- results that reversed.
Each is reported with counts and examples, as evidence of what agent-assisted research gets wrong and what catches it.

## 24. Fixes for the blind spots (author approved, 29 Oct 08:31)

**24.1 Empirical validation by backtest.** Owner: an empirical-validation agent.
- Test the activity-level model out of sample. Do occupations, and occupation × industry cells, that the model scores as automatable (exposure × cost crossover × feasibility, at 2021 parameters) show lower employment growth, wage-bill share or hours between OEWS May 2021 and May 2025?
- Firm level: in the SEC panels, did software firms' function cost shares (S&M, G&A, R&D, cost of revenue) move between FY2021–22 and FY2024–25 as the model predicts from their function mix?
- Report the effect sizes, placebo tests (pre-period trends where available) and the limits. This is evidence of predictive association, not of causal impact.

**24.2 Global sensitivity and decision robustness.** Owners: the engine builder, plus the lead author for the paper text.
- Run global sensitivity analysis (Morris screening, then Sobol indices) over the grounded ranges.
- Report recommendations by robustness: the share of the parameter space in which each recommendation holds, and minimax regret across scenarios.
- Add a capability-plateau scenario, in which the AI time horizon stops growing, alongside the faster cases. The extension theorist states its effect.

**24.3 Industry-appropriate objectives.** The Rule of 40 is a software metric.
- Generalize the objective to value-based metrics: economic profit, ROIC net of WACC, and FCF yield with growth. Specify each industry's frontier in (growth, ROIC) or (growth, economic margin). The Rule of X is the special case for asset-light subscription firms.
- Owner for the theory: the Part I integration theorist, as a short generalization result.
- Owners for priors: the data and assumption agents, for industry function shares and benchmark margins beyond software (see 24.10).
- The paper must say which conclusions are software-specific.

**24.4 Accounting treatment, and ICFR when financial processes are automated.** Owner: an accounting and controls agent.

Accounting:
- capitalization of internal-use software and AI development costs (ASC 350-40, and any 2025 FASB update; verify);
- cloud-computing implementation costs;
- restructuring and exit costs (ASC 420), severance (ASC 712, or ASC 420 for one-time benefits);
- SBC;
- the current U.S. tax treatment of R&D expenditure (Section 174 as amended; verify at a primary source).

Controls:
- redesign of internal control over financial reporting when record-to-report, procure-to-pay, order-to-cash or revenue processes are automated;
- ITGCs over AI systems: change management, access, operations, model versioning;
- how much the auditor can rely on AI-performed controls (AS 2201; any PCAOB staff publications on AI; verify);
- COSO guidance, if it exists for AI (verify);
- material-weakness risk.

Outputs:
- the GAAP score path with explicit accounting;
- control redesign as a cost and a gating constraint for financial-reporting processes;
- formulas for the engine.

**24.5 Labor law, employee response and talent supply.** Owner: a labor and jurisdiction agent.
- Collective-redundancy rules: the U.S. WARN Act, the EU Collective Redundancies Directive 98/59/EC, works councils and consultation in major jurisdictions. These set minimum timelines and costs.
- Attrition among staff who remain during restructuring, with peer-reviewed evidence.
- Feasibility of reskilling and redeployment.
- Scarcity of AI and agent-engineering talent, and the wage premium. Use peer-reviewed or government evidence first.
- Outputs: a timing constraint, transition costs, a wage premium and a hiring-lead-time constraint for the people plan.

**24.6 International scope.** Owner: the labor and jurisdiction agent.
- Location wage indices, from an OECD, ILO or national statistics source.
- Data-residency and transfer constraints on AI use: GDPR Chapter V, China's PIPL and similar laws. These limit readiness ι and permissibility.
- Jurisdiction flags in the engine schema.
- A statement of how well O*NET maps to non-U.S. workforces.

**24.7 Competitive adoption game.** Owner: an IO theorist.
- Incumbents choose adoption timing strategically: preemption, waiting games, and the prisoner's-dilemma case in which everyone automates and pass-through competes the savings away.
- Combine with Prop entry and Lemma prices.
- Derive when automating is a dominant strategy that leaves the industry no better off, and what that implies for "should versus could".

**24.8 Model risk management of the engine.** Owners: the engine builder and the lead author.
- Use Federal Reserve and OCC SR 11-7 (verify) as the governance template, together with the NIST AI RMF and ISO/IEC 42001.
- Deliver engine/MODEL_RISK.md, covering:
  - intended use and users;
  - limitations;
  - conceptual soundness, citing the paper;
  - the validation record (the QA program);
  - ongoing monitoring;
  - change control;
  - human decision rights.
- Frame the output as decision support. The paper's answer to Q12 says so.

**24.9 Wave 0, measurement.** Owner: the engine builder.
- The roadmap always begins with a measurement wave: process mining or event logs, time studies, a systems and data inventory, and data classification.
- Its scope per process comes from the value-of-granularity result (prop:tasks-granularity), with costs and durations.

**24.10 Non-software priors.** Industry function shares and margin benchmarks for non-software industries need data beyond our SEC software extract. Candidate sources:
- broader SEC XBRL frames or companyfacts by SIC, which can be retrieved through the author's browser;
- Damodaran's industry datasets (margins, SG&A and R&D shares, cost of capital), flagged as practitioner data with a stated method.
The data agent identifies the minimal retrieval and asks the lead author if a download is needed.

## 25. ICFR scope principle (author, 29 Oct 10:37)
For SOX, what matters is the processes, systems, integrations and policies that affect the timeliness, accuracy and completeness of financial reporting. A unit is in scope through any of four channels:
- process step: it initiates, authorizes, records, processes or reports transactions or estimates;
- system: it reads or writes an in-scope system;
- integration: it creates or changes an interface that feeds an in-scope system;
- policy: it executes or is governed by an ICFR-relevant policy.
An AI agent that performs an in-scope unit becomes an in-scope application, carrying ITGCs: access, change management (including retesting at each model upgrade) and operations. Each new integration feeding an in-scope system needs interface controls. Period-end outages create a timeliness risk. The EU AI Act high-risk class applies only with an EU nexus.

## 26. Publication structure (author, 29 Oct 10:50)
- **Three papers.**
  - **Paper 1:** the efficient frontier of the Rule of 40 and its limits under AI. Built from sections/*, with the Section 22 constraints, a new section on measuring acquired growth and the modern literature. It is self-contained and goes to arXiv as soon as it is ready, after the referee and practitioner panels and the final audit.
  - **Paper 2:** the economics of AI transformation. Built from part2/*: core, extensions, regimes, product, accounting, labor, competition, the acquirer case and the backtest.
  - **Paper 3:** the engine (autofrontier) as a methods and software paper, covering the data contract, validation and QA, model risk, the Claude skill, traceability and Q12.
- **Answers to the author's 12 questions:** split across Papers 2 and 3, with one table in each.
- **Disclosure:** no competing-interests statement, and the author's employer is not named anywhere. Vendor price examples use other vendors only (Freshworks, Intercom, Salesforce, HubSpot). Revisit if the papers go to a journal that requires a disclosure.
- **SOX scope:** the Quote-to-contract "negotiate terms" step stays out of scope.

## 27. Estimands for Paper 1 (lead agent, 29 Oct 11:20; author asked for the rigorous approach)
- **E1, observed scores (all firm-years).** Primary for descriptive statistics about the scores firms report.
- **E2, the organic frontier.** Acquired growth is removed with a pro forma (ASC 805) adjustment where disclosed; otherwise the firm-year is excluded, with the following year also flagged. Primary for the model-facing findings: the upper-tail slope, the growth weights, the gradients, the near-frontier gap and the calibration.
- **Abstract.** Where E1 and E2 differ materially, give both; otherwise give E2 and say "similar including acquisitions".
- **Sensitivity.** Report flag thresholds of 10%, 25% and 50%, plus selection diagnostics.
- **Disclosure.** The protocol appendix states that the primary sample for the model-facing findings was changed after the robustness results were known, to align the estimand with the theory and the calibration.

## 28. Required practical outcome (author, 29 Oct 11:40)
"How an AI transformation strategy would differ between firms at various levels of Rule of X, and what levers work or won't work at what Rule level and organization setup."
- **Paper 2:** sec:playbook. Lever rankings by firm state, switch thresholds, levers that do not pay, and an archetype playbook table generated by the engine.
- **Paper 1:** sec:levers-position. A self-contained summary of levers by position on the growth–margin plane.
- **Paper 3:** a "lever map" engine output and an archetype runner, used as validation.
- **Archetypes:** defined at quantiles of the SEC panel, crossed with ownership and readiness.

## 29. Executable playbook (author, 29 Oct 11:58)
"Break it down to the lowest process area or task, whatever is feasible. This will become an executable, evidence-based playbook."
- **Granularity:** decisions are made at the DWA activity level (2,087 activities). Execution is planned at the process-step level (136 steps across 24 processes and 19 functions). O*NET task statements (about 24k task–DWA links) are attached as descriptors and evidence. A firm's own task list overrides the defaults.
- **Fields per step:**
  - recommended mode now and at target readiness;
  - binding constraint;
  - preconditions;
  - go/no-go gates;
  - wave and dependencies (complementary sets move together);
  - roles, FTE and jurisdiction leads;
  - KPIs;
  - controls: ICFR channel and condition, ITGC and interface lines, fallback;
  - evidence keys with grounding class, Anthropic Economic Index usage and METR feasibility;
  - confidence tier:
    - A: feasibility, which the backtest supports, plus sourced costs;
    - B: cost-crossover logic, sourced but unvalidated;
    - C: sign depends on class-d inputs;
  - switch conditions, with distance to each threshold.
- **Outputs:**
  - a generic dataset (playbook_steps.csv and playbook_activities.csv, by archetype) with a data dictionary;
  - a per-firm playbook from the engine;
  - summary tables in Paper 2, with one archetype in full in an appendix;
  - the generator and per-firm output described in Paper 3;
  - delivery through the Claude skill.
