# Playbook engine spec: the lever map and the executable playbook (Papers 2 and 3)

Owner: synthesis theorist (AI) for the lead author. Reader: the engine builder. Status: draft 2, 29 Oct 2026 12:50
(draft 1 12:20); the field list of Section 4 is final, Sections 2 and 3 are final except where marked OPEN. Draft 2
adds W14 (public weight), the corrected W5 list from the reference runs, the engine-tier discrepancy (W10), the
merge of the engine's playbook rows (Section 6) and corrected test values (Section 7).
Theory: `part2/theory_playbook.tex` (sec:playbook) and `part2/proofs_playbook.tex`; Paper 1 summary
`sections/levers_by_position.tex` (sec:levers-position). Spec sections 28 and 29 of `notes/unified_model_spec.md`.
Runner: `code/playbook/run_archetypes.py` (with `archetypes.py`, `levers.py`, `steps.py` in the same folder), written
against the engine's public API; it does not edit `engine/`.

Every formula below names its paper label. Every number the engine writes for these outputs must come from these
formulas; no typed values. Units: shares of revenue unless stated, rates continuous, money in the firm's currency.

## 1. What the engine already provides (checked 29 Oct, 12:15)

- `api.run`, `api.playbook`, `api.write_playbook`, `api.synthetic_firm`, `api.REGIMES` (with `permanent_capital`).
- Per step and per DWA activity (`roadmap.playbook`): modes now, in plan and at target readiness; binding constraint;
  preconditions; gates; wave, depends_on, moves_with; roles, FTE, jurisdiction leads; KPIs; ICFR status, channel and
  condition; ITGC and interface lines; fallback; evidence keys with class; AEI automation share; O*NET task count;
  tier; thresholds with distances.
- Part I objects in `formulas.py` (R_star, delta_star, sigma_star, gordon_v0, part1_delta_R, lambda_after_savings),
  the regime weights (myopic_weight, exit_weight, pc_growth_weight, hybrid_weight), game_shares (durable share),
  zeta_pe, R_max, entry_limit_score.

Not yet: the lever map (Section 2), the items of Section 3, and the archetype dataset (the runner writes it).

## 2. The lever map (new output `result["lever_map"]`, report section "Levers by position and setup")

### 2.1 Inputs: the state vector (all from data the engine already ingests)

Position (Tier 0, `part1_baseline`):
| symbol | field | source |
|---|---|---|
| g, m | revenue_growth; m_cash | tier0 |
| sigma | sm / revenue (growth spend; see 2.2 on expansion R&D) | tier0 |
| a_GA, a_RD | ga / revenue; (1 - rd_expansion_share) rnd / revenue, reported separately (W3) | tier0 |
| gamma, c_h, c_c | 1 - cogs/revenue; labor and compute shares of cost of revenue | tier0 + priors |
| k | capital_intensity_k (input), else capex/(g S) when g > 0 (Paper 1 anchor convention), else the industry k | tier0 |
| G_i | market_growth (input), else the calibration of 2.2 | tier0 |
| ell, X_hat | 2.2 | derived |
| s, h(s) | not identified separately from lambda; thresholds are stated relative to today's headroom (2.4) | - |
| X^scr | Lemma lem:valuation2 at the firm's (g, m, r) with the regime presets T = 10, theta = 1/2 (as `_frakA`) | derived |

Setup (Tier 3 and the regime):
| dimension | engine object | gate or weight it feeds |
|---|---|---|
| ownership regime | `regimes.make_regime`, `growth_weight` | X_o (prop:reg-weight, prop:acq-pc(d)); dip budget (prop:reg-dip); hold deadline (prop:reg-speed(b)); capital hurdle zeta_pe (prop:reg-value(d)) |
| scale and volume | units.v, revenue | v*_j (prop:tasks-modes(e)), v^MB (prop:tasks-window(c)), v^BB (prop:tasks-buildbuy(a)) |
| data readiness | iota0 by function (tier3_systems) | iota_j floor (prop:tasks-review(d)), iota*_p (prop:tasks-readiness(b), W8), big push (prop:tasks-readiness(d)) |
| regulated share | icfr_status, regulated_class, eu_market | ITGC lines (prop:acct-itgc), cutover (prop:acct-cutover), NPV^ICFR (cor:acct-npv), xi_min (cor:ext-floor) |
| labor jurisdiction | tier3_jurisdictions, `statutory_terms` | T^leg (prop:labor-lead), pace (cor:labor-pace) |
| change capacity, bandwidth, leadership | org inputs, K_chg, Phi, nu_D | pace (prop:attainable(c), prop:ext-bandwidth(b)), tenure breakpoint r_D T_emb = 1 (prop:ext-shocks(b)) |
| product model | tier3_products (seat or usage) | nu vs nu*_k (prop:prod-migrate(b)); tariff pass-through (prop:prod-aggregate(c)) |
| market structure | market_hhi, industry_pass_through | dur = 1 - phibar^ind (1 - HHI) (cor:ext-game-engine(a)); entry (prop:ext-should(b)-(d)) |
| owner capability | OPEN (W12): u_F, N_pl, rebuild flag, varpi^o, T_h^o, N^core | prop:acq-owner, prop:acq-replace |

### 2.2 Calibration of the position (Assumption ass:playbook-calib, Lemma lem:playbook-calib)

When the firm gives no EV/revenue multiple and no market growth, the engine falls back on X_default = 8 and
market_growth_G = 0.10; with g <= G it then floors ell at 1e-4, which makes sigma* about zero while the firm spends
sigma (observed 43% in the test firm). The lever map must use a state in which the observed spend is optimal:
- `spend_ratio` r_sigma: Paper 1's median S&M share over excess growth, 3.3 (class c, sections/empirics.tex), a new
  parameter `finance.spend_ratio` with range [1.9, 7.4] (Paper 1's interquartile range).
- X_hat = k + r_sigma / alpha; Delta = sigma / r_sigma; G_i = g - Delta; ell = Delta / sigma^alpha.
- Check: sigma_star(ell, X_hat - k, alpha) = sigma and delta_star = Delta (Lemma lem:playbook-calib(a)); the runner's
  verify script tests it on every archetype.
- A firm input `ev_revenue_multiple` or `market_growth` overrides the corresponding step; report which was used.
- Growth spend: Paper 1 counts S&M only (sections/data.tex). Report both the S&M-only state and the default
  rd_expansion_share state; the runner uses rd_expansion_share = 0 and reports R&D as a non-discretionary line.

### 2.3 Lever values (Proposition prop:playbook-rank(a)), for each regime o with weight X_o > k

At the owner's optimum (sigma*_o = sigma_star(ell, X_o - k, alpha), Delta*_o, g*_o = G_i + Delta*_o), for the common
proportion x = 0.10 (setting `levers.proportion`):
| lever | first order | exact | label |
|---|---|---|---|
| growth engine, automation of growth activities | x sigma*_o | R_star(ell (1-x)^(-alpha)) - R_star(ell) | prop:tasks-aggregate(b) |
| growth engine, demand pull | x sigma*_o / alpha | R_star(ell (1+x)) - R_star(ell) | cor:priorities(ii) |
| overhead (G&A) | x a_GA | same (linear) | cor:priorities(i) |
| engineering (maintenance R&D) | x a_RD | same | cor:priorities(i) |
| cost of revenue (human service) | x dur c_h (replicable); x (1 - phi) c_h at given demand | same | cor:priorities(iv), cor:ext-game-engine(a) |
| retention, one point of G_i | (X_o - k) 0.01 | same | cor:priorities(iii) |
| AI product | dilution break-even D_m/dG = X_o - k | - | cor:prod-dilution(i) |
| capital for labor (owned compute) | hurdle on opex saved per dollar of capital: g*_o + delta_K (score), r_o + delta_K (value), zeta_pe (sponsor) | - | cor:capital, rem:assumptions(c), prop:tasks-capital, prop:reg-value(d) |
| acquisition | largest price per dollar of acquired revenue that raises the charged score: X_o (Rule of 40: 1) | - | prop:acquired-score(a) |
Also report durability: which values raise R_inf (overhead, engineering, retention, cost of revenue at given demand)
and which vanish as s -> sbar (both growth-engine values).

### 2.4 Switch thresholds and the firm's distance to each (prop:playbook-rank(b)-(f))

| threshold | formula | distance reported |
|---|---|---|
| X^ddagger_0 (growth engine vs overhead; also vs engineering with a_RD) | k + a^(1-alpha) / (alpha ell) | X_o - X^ddagger_0, for every regime |
| identified form | growth first iff (X_o - k)/(X_hat - k) > (a/sigma)^(1-alpha) | the two sides |
| X^ddagger exact | eq. reg-Xdag at d_sigma = x, da = x a | X_o - X^ddagger |
| demand-pull version | k + (alpha a)^(1-alpha)/(alpha ell) | X_o minus it |
| headroom switch | h^ddagger/h = (a / sigma*_o)^(1-alpha) | 1 - h^ddagger/h (the fall in headroom that flips the ranking) |
| cost of revenue vs overhead | dur > a_GA / c_h | dur - a_GA/c_h |
| screening flip | X^scr < X^ddagger_0 < X_o | flag |
| capital | g*_o + delta_K | (needs the switch's dc/dK; per activity from econ.K, econ.cash) |

### 2.5 Binding constraint

Two parts, both reported:
1. Position: the cost line with the largest gap to the top decile of GAAP operating margin in the firm's growth band
   (Paper 1 Table tab:gap; bands 0-10, ..., 40-60%; values in notes/gap_decomposition.json `bands`): gross margin,
   S&M, R&D or G&A. The engine needs the band table as a prior file (new: `priors/frontier_gap_bands.csv`,
   generated from notes/gap_decomposition.json by the data agent).
2. Setup: the scarcest capacity in the first plan year (largest of change capacity used / capacity, decision load /
   breakpoint, reviews / capacity, budget used / budget, dual running used / budget; `roadmap.utilization`), and the
   gate that most often binds automation across in-house hours (`binding_constraint` of the playbook rows).

### 2.6 Levers excluded, with reasons (Corollary cor:playbook-nopay)

Emit one row per excluded lever with the rule that excludes it:
- growth-engine levers when X_o <= X^ddagger_0 (and the headroom flag when 1 - h^ddagger/h < 0.25 is NOT a rule;
  report the distance only; no typed cut-off);
- cost-of-revenue automation as a margin lever when dur c_h < a_GA (it stays a defensive lever: cor:ext-game-engine(b));
- owned compute when no activity's dc/dK exceeds g*_o + delta_K (score) or r_o + delta_K (value);
- automation of steps whose binding constraint is reliability (detection) or permissibility: augment or keep;
- readiness investment below iota*_p (prop:tasks-readiness(d));
- in-house builds below v^BB or v^MB (buy or outsource);
- AI products with D_m/dG > X_o - k (needs product data; otherwise report the break-even only);
- replacement when its customer cost X_o S (1 - e^(-delta^G T^cu)) exceeds the speed gain (prop:acq-replace, OPEN W12);
- acquisitions priced above X_o per dollar of revenue (prop:acquired-score(a)); the treadmill flag when G_i < 0
  (prop:acq-limits(a));
- programs whose embedding window exceeds 1/r_D (prop:ext-shocks(b)).

## 3. Changes requested (W items; priority order)

- **W1 (bug).** `regimes.growth_weight` uses the firm's current cash margin m_cash as m_hat for the exit and
  permanent-capital weights. Proposition prop:reg-weight(c) uses the margin a marginal permanent dollar earns; for a
  firm that spends on growth this is m0 - k G_i (Proposition prop:dynamic(a)), not m_cash. With m_cash < 0 (any
  growth-corner firm) the engine's sponsor weight is negative or near zero (test firm: X_exit_at_entry = 0.55).
  Use m_hat = m0 - k G (and report both).
- **W2.** The calibration of 2.2 when ev_revenue_multiple and market_growth are absent.
- **W3.** `frontier_shift` reports delta_a combined; report the G&A and maintenance-R&D parts separately (bucket ga
  vs rnd), and the growth-activity saving delta_sigma valued by the exact formula (prop:tasks-aggregate(b)).
- **W4.** Process values count savings on growth activities at their cash value. Report alongside the score value
  sigma* delta_sigma and, for demand-pull effects, x sigma*/alpha (prop:tasks-aggregate(b)); do not change the
  optimizer's objective without the author.
- **W5 (data, step level).** DWA-level attributes are applied to process steps without a step-level override, which
  misclassifies finance steps. In the reference runs (all six panel archetypes, readiness 0.4) ten procurement and
  finance steps are bound by the physical flag in every archetype: P01.4 (Collect deposits, payments or fees), P01.5,
  P03.3, P04.2 and P19.2 (Reconcile records of sales or other financial transactions, physical share 0.61), P02.6
  (Execute sales or other financial transactions), P04.4 and P19.1 (Proofread documents, records, or other files),
  P06.3 and P19.3 (Issue money, credit, or vouchers); P02.5, the invoice chain's matching step, is physical-bound in
  one archetype (A1, capability date 2026.7 after the world-model lag). Outside finance, P08.6 and P13.4 (Sell
  products or services), P10.6 (Install computer software), P11.4, P17.2 and P07.3/P11.3 (troubleshooting) are also
  physical-bound. The reconciliation DWA is performed by cashiers and retail salespersons as well as bookkeeping
  clerks (data/tasks/occ_activity.csv), which is why its physical share exceeds one half. Request to the data agent:
  add `physical_override` and `licensed_override` (0/1, blank = use the DWA) to data/tasks/process_activities.csv
  with a basis column; the engine uses the step value when present. Until W5 lands the playbook marks these rows
  Tier A for a constraint that does not apply to them (theory_playbook.tex says so).
- **W6 (data).** `aei_augmentation_pct` (collaboration_bucket_augmentation_pct) is not in activities.csv; add it
  next to aei_automation_pct (same mapping, code/data_part2/03_activities.py).
- **W7.** Pilot band (prop:tasks-pilot(c)) for every process with a positive best column, not only selected ones.
- **W8.** iota*_p per process: the smallest readiness at which full automation has positive value (bisect
  W_p(J_p; iota) between the floor and 0.98), with the big-push test (prop:tasks-readiness(d)).
- **W9.** Cycle-time KPI: not modeled; the handoff latency of ass:tasks-process is the candidate. OPEN for the author.
- **W10 (tier rule, decided by the coordinator).** Section 5. The engine's `roadmap.playbook` (version 0.2) puts
  reliability, readiness and risk-appetite bindings in Tier A; the decided rule puts them in Tier B (the backtest
  supports capability, physical work and permissibility only). Resolved in playbook.build v1.0 (engine message
  12:40), which implements def:playbook-tier as decided and the runner's binding order; remaining difference: the
  engine's flip test does not rebuild the firm for the four impute-level keys, the runner's does (about 70% tier
  agreement; both columns kept).
- **W11.** O*NET task statement text per DWA (the runner attaches up to 12 task ids and two statements from
  data/raw/onet_31_0/task_statements.csv through xw_task_dwa.csv; move this into priors).
- **W12.** Owner capability U_o (u_F, N_pl, 1^reb, varpi^o, T_h^o, N^core; ass:acq-owner) as tier3_regime inputs for
  permanent_capital, and the replace-or-transform test (prop:acq-replace(a)). Until then a permanent acquirer's run
  values the target's own transformation at the acquirer's hurdle.
- **W13.** Lever map output (Section 2) and a report section.
- **W14 (public weight).** The engine's public regime applies the earnings pressure to the input multiple
  (X^my = k + (X_in - k)/(1 + w), regimes.growth_weight). Under the playbook calibration the input multiple is the
  revealed weight X_hat, which for a public filer already is the net weight under the pressure (Proposition
  prop:reg-weight(b) read backwards), so the engine's public program is valued at X_hat/1.3 (8.6 for A1 instead of
  11.1). Request: a Tier 0 flag `multiple_is_net_of_pressure` (default false); when true, public X_o = X_in and the
  going-concern weight is k + (1 + w)(X_in - k) for the other regimes. The lever map (runner) already uses this
  reading; the engine's program values in Table tab:playbook-grid do not.
- **W15 (weights with G_i at or above the owner's rate).** `regimes.growth_weight` caps G at r - 0.01 in the exit
  and permanent-capital weights. Eq. reg-Xexit holds for any finite horizon, so the cap changes the number (A6: PE
  weight 17.0 uncapped at m0 from the FCF margin, as the runner reports); prop:acq-pc(d) is defined only for G_i below the hurdle, so return
  None there (A6) instead of m_hat/0.01.

- **W16 (lever-map ranking).** `levers.lever_map` ranks growth_automation_exact, demand_pull_exact, overhead,
  engineering, cost_of_revenue_replicable and retention_point together. A point of retention ((X - k) x 0.01) and 10%
  of a line are not commensurate, and demand pull and growth automation value the same lever two ways. Rank only
  growth_automation, overhead, engineering and cost_of_revenue_replicable at proportion x (prop:playbook-rank(b));
  report the others beside the ranking.

## 4. The playbook record (spec 29): fields

One row per (archetype or firm) x process step (`playbook_steps.csv`) and per (archetype or firm) x activity unit
(`playbook_activities.csv`; an activity unit is a DWA in a process step or in a function's residual work). Engine
field names where they exist; `pb_` fields are written by the runner from engine arrays until the engine writes them.

| # | group | field | type | definition | label |
|---|---|---|---|---|---|
| 0 | id | archetype, readiness_case, iota0, regime, unit_key, kind, function_id, process_id, step, step_name, dwa_id, dwa_title, gwa_id, critical_path, volume_per_year, hours_per_unit, fte_in_house | | identity and size | |
| 1 | mode | mode_activity_now, mode_activity_target | H/O/U/A/N | cheapest feasible mode by choice cost at (readiness level 0, 2026) and (highest level, 2026) | prop:tasks-modes, prop:tasks-augment |
| 1 | mode | mode_step_now, mode_step_target, mode_plan_best | H/O/U/A/N | mode in the process's best column at level 0 / highest level starting now / overall; baseline if no column has positive value | prop:tasks-aon, prop:tasks-transition |
| 1 | mode | first_year_A_at_target | year | first plan year in which A is cheapest at the highest level | prop:ext-feasible |
| 2 | binding | binding_now, binding_target (+ _detail) | category | first failing test in the order: permissibility (licensed, exclusion, data class, prohibited), feasibility: physical, feasibility: capability horizon, readiness, reliability: detection, reliability: residual or appetite, volume threshold, cost (which mode is cheaper); none if A is optimal | prop:tasks-breakpoints, prop:playbook-gates |
| 2 | binding | icfr_status, icfr_channel, icfr_condition, regulated_class | | scope channel (process, system, integration, policy) and condition | def:acct-scope |
| 2 | binding | program constraint | | for a positive process not in the plan: the binding program capacity (utilization) or the regime hurdle | prop:ext-waves(d), prop:reg-speed |
| 3 | preconditions | pre_readiness_floor, pre_readiness_now, pre_readiness_target, pre_review_share_target, pre_eval_set, pre_itgc_lines, typical_systems | | readiness floor and the step's systems; review share xi* at target; evaluation set if A or U; ITGC lines if in scope and A | prop:tasks-review, prop:acct-itgc |
| 4 | gates | gate_min_detection d*, gate_detection_now, gate_max_residual_error, residual_error_A_target, gate_min_volume v*, pilot_band_low/high, gate_threshold | | d* = 1 - (1 - qbar)/ebar on the catchable rate; v* = (F a + run)/(c_alt - c_A); pilot band eq. tasks-pilotband | prop:tasks-review(d), prop:tasks-halluc(b), prop:tasks-modes(e), prop:tasks-pilot(c) |
| 5 | wave | wave, wave_start_year, depends_on, moves_with_steps, integration_first | | the roadmap wave; the steps whose mode changes in the same column (complementary set) | prop:tasks-complement, prop:ext-waves |
| 6 | roles | role_process_owner, role_ai_engineer_months, role_control_owner, role_reviewer_fte_target, fte_effect_target, labor_lead_days | | build months F_A0 / ai_engineer_month; reviewer FTE xi rho_rev t v / hours; FTE effect at target; U.S. lead (or the jurisdiction file's) | prop:labor-lead |
| 7 | KPIs | kpi_unit_cost, kpi_residual_error, kpi_review_share; kpi_cycle_time (W9), kpi_nrr and kpi_seat_exposure for product steps (from product lines) | | | prop:prod-seats |
| 8 | controls | ctl_icfr, ctl_itgc_line_usd, ctl_interface_line, fallback | | eq. acct-itgc with the accounting defaults; interface line when the step writes a financial system; close fallback (prop:acct-itgc(d)) for close steps | prop:acct-itgc |
| 9 | evidence | ev_exposure_llm (eloundou2024gpts, a), ev_aei_usage_share and ev_aei_automation_pct (appel2026anthropic, a), ev_aei_augmentation_pct (W6), ev_task_hours, ev_physical_share, ev_licensed_share, ev_metr_feasibility_date, ev_capability_margin_log (kwa2025measuring refit, a), ev_detection_src, ev_target_src, ev_build_src, ev_review_time_src (each with class), ev_onet_task_links, ev_task_ids, ev_task_examples | | evidence keys with grounding class a/b/c/d | |
| 10 | tier | tier_now, tier_target (+ reasons), mode_swap_params_now | A/B/C | Section 5 | def:playbook-tier |
| 11 | switches | switch_conditions | text | each threshold with the firm's distance: catch rate d* vs now, readiness floor vs now, capability date, volume v* vs v, cost gap, first year A is cheapest, the class-d keys that flip it | prop:tasks-breakpoints |

## 5. Confidence tier (decided rule; Definition def:playbook-tier)

- **Tier C**: the recommendation changes for some value of a class-d input within its stated range, the others at
  their defaults (one-at-a-time at both range ends), or the share of Monte Carlo draws in which the process's value
  is positive is below `playbook.robust_share` = 0.8 (a setting, class "setting"). "Changes" means the automation
  decision (A or not) or the AI decision (U, A or N against H or O) changes; swaps within those classes are reported
  in `mode_swap_params_now` and do not decide the tier. Name the keys.
- **Tier A**: not C, and the recommendation is bound by a feasibility filter the backtest supports: capability
  horizon, physical work, or permissibility (licensing, exclusions; part2/validation_backtest.tex), with sourced costs.
- **Tier B**: not C, and the recommendation rests on the cost crossover (or a reliability gate) with sourced inputs;
  the cost step is not validated by the backtest.
Implementation in the runner: `steps.flip_params` (economics rebuilt per key; the impute-level keys
review.r_bar_high, review.L_mult, review.L_mult_regulated and readiness.iota_min_regulated_add rebuild the firm);
the MC part uses `mc["robustness"]` when the run has it.

## 6. Runner contract (code/playbook/run_archetypes.py)

- Reads data/panel_v2_all.csv (checked against data/panel.csv), builds the archetypes (archetypes.py), writes each
  archetype's Tier 0 and Tier 3 systems in the engine's format, runs the engine through `api.run` and reads
  `api.playbook` and `api.lever_map`, and writes data/playbook/{playbook_steps.csv (step x configuration),
  playbook_activities.csv (activity unit x configuration, the engine's file name), playbook_dwa.csv (DWA x
  configuration), archetypes.csv, data_dictionary.csv},
  notes/playbook_results.json, part2/tables/playbook_*.tex and sections/tables/{levers_position_macros.tex,
  tab_levers_position.tex}. `--tables-only` rewrites tables and macros from the saved results.
- Engine rows: every non-identity field of the engine's playbook (playbook.build v1.0) is joined to the runner's
  activity rows by unit_key and to the step rows by (process_id, step), with the prefix `eng_`; the engine's lever
  map is stored per configuration in notes/playbook_results.json (`engine_lever_map`) and checked against the
  runner's (verify L4); runner-engine agreement shares are stored as `agreement_with_engine` (verify P5b). The runner's own fields keep
  their names; where both exist (binding, tier) both are kept and the dictionary says which is which.
- Tier: the runner's `tier_now` applies Section 5, including the Monte Carlo clause through
  `eng_robustness_share_positive` (the engine computes it for processes in its plan; n_imp = 4, n_out = 20 draws).
- Override: finance.rd_expansion_share = 0 (Paper 1's sigma). Readiness cases 0.4 and 0.9 (invoice_chain.yaml).
- Archetypes A1 to A6 run through the engine; A7 (the compounder) is position-only until W12.
- Run time about 4 minutes with three workers. Regeneration order: after paper1_macros.py; then
  code/verify_part2_playbook.py.

## 7. Test values for the engine builder (from code/verify_part2_playbook.py)

- Lemma lem:playbook-calib: for every archetype, |sigma_star(ell, X_hat - k) - sigma| < 1e-12.
- X^ddagger_0 is the d_sigma -> 0 limit of eq. reg-Xdag with da = d_sigma a (relative error below 1e-3 at
  d_sigma = 1e-4).
- Theory_regimes example: X^ddagger = 6.85 at m0 = 0.35, G = 0.03, k = 0, alpha = 0.3, ell = 0.0535, d_sigma = 0.2,
  da = 0.01.
- Cor:capital: hurdles 5 and 1 points for dk = 0.10 at g = 50% and 10% (7.5 and 3.5 with delta = 0.25).
- Cor:prod-dilution example (verify_part2_product G5): +6.0 points at X = 9, -0.5 at X = 2.5 (D_m = 0.03, dG = 0.01).
- Regimes B7: X^PE = 2.21, 2.70, 3.50 at 6, 3, 0 years to exit (m_hat 0.25, G 0.03, r ln 1.22, X_T 14 x 0.25);
  X^my = 6.15 at X = 8, w = 0.3.
- Core 18g: a 20% growth-activity saving at Part I's worked example adds 2.1 points first order and 2.5 exactly.
- Durable share 2/(n+1) under linear Cournot: 0.40 at HHI = 0.25.
