# Changelog

## S&M basis: maintenance-netted is central (author decision 7, 2 Nov 2026; notes/r2_propagation.md)

Source: coordinator message of 2 Nov 2026 (about 12:35 UTC-8): maintenance-netted is central everywhere, matching
Paper 1's 2036 path; all S&M and no S&M are bounds.

- **Calibration.** New finance.sm_basis (setting, "netted"; "all" and "none" are the bounds) and
  finance.spend_ratio_netted 0.9875 [0.6705, 1.1403] (c; Paper 1 empirics_v3 spend_maint_ratio E1, macro AlphaNet
  0.99). finance.sm_maint_base now carries Paper 1's full-precision value 0.25056806 (was rounded to 0.2506).
  finance.spend_ratio (3.3) is the all-S&M bound. New formulas.growth_spend_split (sigma = max(S&M - b_M, 0) plus the
  R&D expansion share; maintenance S&M min(S&M, b_M) is a cost line). impute.part1_baseline and levers.state use it:
  maintenance S&M moves into a (and a_gaap), so m0 is net of it; with no growth spend, ell = 0, Delta = 0 and G_i = g.
  formulas.gordon_v0 returns the margin-only Gordon value and x_dagger_0 / x_dagger_exact / x_dagger_demand_pull return
  infinity when ell = 0; levers.identified_rhs guards sigma = 0.
- **Frontier shift.** pipeline.frontier_shift splits S&M savings into the growth part and the maintenance part
  (new output delta_a_SM_maint, counted in delta_a and passed through at the industry rate like overhead); the
  report's frontier line names it.
- **Lever map and report.** levers.sm_basis_bounds gains "central"; the report's position line states the basis and
  the maintenance S&M, and the growth-spend paragraph says netted is central with the ranking on both bounds.
- **Synthetic firm** (examples/synthetic_run/report regenerated, full settings): growth spend 38.4% -> 13.3% of revenue
  (S&M 30.4% less the base 25.1%, plus the R&D expansion share 8.0%); X_hat 18.9 -> 6.9; ell 0.093 -> 0.128; m0
  0.487 -> 0.236; C0 0.49 -> 0.74, so the pass-through elasticity is 0.24 -> 0.37 and the margin keep factor of a
  replicated cut 0.76 -> 0.63; other operating cost saving -5.29% -> -8.71% of revenue (maintenance S&M -3.42%);
  X_dagger_0 against overhead 12.36 -> 9.16; sponsor, VC and permanent-capital weights 5.71 / 7.68 / 3.49 -> 2.64 /
  3.61 / 1.45. Plan values, scenario values, Monte Carlo quantiles, regime program values and FTE are unchanged (they do
  not use the Part I state), so the golden snapshots are unchanged.
- **Docs.** README (lever map) and MODEL_RISK (Section 3, growth spend basis; Section 4, limitation) state the basis
  and the bounds. finance.alpha carries a note on Paper 1's reclassification to class d (notes/assumptions_register.md,
  2 Nov 2026); the grounding stays c pending the engine owner's decision (drawing it would reshuffle every later Monte
  Carlo draw); NOTES_LOCK accepted with tools/check_sync.py --accept for the register change.
- TRACEABILITY.md regenerated; data/examples/invoice_chain.json regenerated (it records the sha256 of defaults.yaml and
  params.yaml; its macros are unchanged). 191 of 191 tests pass.

## Paper 1 round 2 carried into the engine (2 Nov 2026; notes/r2_propagation.md)

Source: notes/r2_code_changes.md (including the follow-up of 2 Nov) and the author decisions and lead-agent rulings in
notes/reviews/paper1_v2/revision_plan_r2.md.

- **Pass-through (B1).** competition.phi_ind is now read as a RATE on the unit-cost saving, applied in the score to every
  unit-cost saving the rivals make (cost of revenue, compute and overhead; Part I prop:entry(d)), with the margin at the
  post-cut price. New formulas.passthrough_terms (C0 = 1 - f - m0, total rate 1 - (1 - phi_ind rep)(1 - phi_extra),
  elasticity phi C0, margin keep factors) and formulas.margin_after_passthrough (exact, m0' = 1 - f - (C0 - S)/(1 - phi S));
  economics info pass_through. pipeline.frontier_shift uses the exact mapping for R* after the plan and the elasticity
  in part1_delta_R, which now passes overhead through as well (signature: phi_e in place of phi). The lever map
  (formulas.lever_values, levers.lever_map, levers.x_levels) values a replicated cost-of-revenue cut at
  x (1 - phi C0) c_h instead of x dur c_h (prop:levers-position(a), (d)); the exclusion rule and
  cost_of_revenue_vs_overhead use 1 - phi C0. dur = 1 - phi (1 - HHI) stays the DOLLAR share and still values plans
  (plans.py, unchanged numerically); regimes.stakeholder_values gives customers the rate phi on cost-of-revenue savings
  instead of 1 - dur. Report, scenario descriptions and defaults text updated. Synthetic firm (quick run): rate 0.50,
  C0 0.49, elasticity 0.24, margin keep 0.76 (the dollar share is 0.625).
- **Accountability floor (C1-C3, C6).** accounting.eps_bar: no central value; every floor is reported at 1% and 5%
  (security.accountability_floor by_eps_bar), and the key only selects the single-number ceiling's design (grounding
  stays "policy", so it is not drawn in the Monte Carlo). New formulas.amin_breakevens: every design is reported with its
  break-evens in the cross-type common mode p_cc and in the human miss rate on AI-missed items (Paper 1: 0.00084 and
  8.4% for one human over one AI layer at 5%). Direct cost C_acct = KPMG 2025 SOX program budget of the firm's revenue
  class (accounting.sox_program_by_size: under $5bn $1.5M, $5-25bn $2.7M, above $4.7M) plus the accelerated-filer
  average audit fee (accounting.audit_fee $1,492,375; high case audit_fee_high $5,327,646); the S&P 500 ratio
  (audit_fee_per_musd) is the low bound; accounting.sox404_median (SEC 2009, $1.04M) removed. formulas.amin_direct_cost.
  At $1bn: 0.30% of revenue (low 0.18%, high 0.68%), as Paper 1. accounting.C_itgc $50,000 -> $185,000 [16k, 330k], so the
  design's AI-layer line C_itgc + C_val/T_up is $204,672, Paper 1's ITGC_LINE_DESIGN and Paper 2's acctAminLine
  (was $69,672). Example designs at $1bn: one human over one AI layer $754,672 (5%), one over two $804,672 (1%).
- **varpi label (B9).** success.a0 and c0 text: varpi 0.70 is the share of attempts that create some value, not a success
  rate; the target is the per-attempt yield 0.70 x 0.67 = 0.47. Report label of a wave's mean varpi relabelled.
- **S&M basis (decision 4).** New finance.sm_maint_base 0.2506 [0.2326, 0.2757] (c; Paper 1 MaintBase); the lever map
  reports sm_basis_bounds (all S&M, maintenance-netted, no S&M) and the report states that its calibration on all S&M is
  an upper bound. The calibration itself is unchanged (it is Paper 1's convention in sec:levers-position); see
  notes/r2_propagation.md item 6 for the re-check of the playbook ranking.
- Golden snapshots unchanged (they pin plan values, Monte Carlo quantiles, score paths, FTE and regime values, none of
  which these changes touch). New test test_formulas::test_amin_direct_cost_and_breakevens_follow_paper1;
  test_accounting builds C_acct with amin_direct_cost. TRACEABILITY.md regenerated. 191 of 191 tests pass.
- Authorship and declarations added to README.md and MODEL_RISK.md.

## Follow-up decisions on the engine pass (29 Oct 2026, coordinator)

- **Success calibration to Paper 1's varpi (was ISSUES open 9).** The adopted round-2 rule (assumptions round 2
  Section 1.1, last paragraph) calibrates the reference process to a production probability of about 0.50 only if
  success.b_bar carries the whole realization haircut; with b_bar = 0.67, McKinsey's realized share for successful
  transformations, 0.50 x 0.67 = 0.34 misses the rule's own target of 0.46. The reference five-step process now
  succeeds with probability varpi = 0.70 [0.54, 0.80] (Paper 1's value, params.yaml
  project_outcomes.transformation_attempt_creates_value_varpi: BCG 2020; S&P Global 0.54; BCG six factors 0.80), so the
  per-attempt expected realization is 0.70 x 0.67 = 0.47 [0.20, 0.68], Paper 1's product. The previous process factor
  (c0 = 1.2, expit(c0 - 0.4 - 0.4 ln 2) = 0.63) capped the reference below 0.70, so both intercepts move: the
  reference's failure hazard is split equally between the process factor and the five activity factors (each
  sqrt(0.70) = 0.837; the split is not measured), giving success.c0 1.2 [0, 2] -> 2.31 [1.11, 3.11] (d, same offsets) and
  success.a0 1.87 [1, 3] -> 2.12 [1.19, 3.51] (b), whose range maps the reference to 0.54 and 0.80 with c0 at its
  default. The mapping is recorded in both parameters' basis text.
- **eps_bar grounding (was ISSUES open 11).** Central 5 percent kept, 1 percent a stricter sensitivity, side by side.
  Note added, citing only figures read at the source: Audit Analytics, SOX 404 Disclosures: A Seventeen-Year Review
  (2 Nov 2021): 4.6 percent of SOX 404(b) auditor attestations adverse for fiscal 2020; An Eighteen-Year Review (July
  2022, the latest edition readable at the source): 5.8 percent for fiscal 2021 and 4.8 percent for fiscal 2019. A later
  edition (Ideagen, 2026) is behind a download form and was not read. Most audited filers, with mostly human-run
  controls, obtain effective opinions, so a threshold at which the reference human-only design fails (1 percent in the
  examples) is inconsistent with the evidence.
- **Paper 2's copy of C_val (was part of ISSUES open 10).** code/verify_part2_accounting.py UNIT C_val $100k -> $24k;
  checks 6c1, 6c and 6g now state that the engine's units equal the KPMG-unit lines; the EXA LEGACY keys (C_itgc,
  C_val, T_up) and best_g are removed (test_cross_impl no longer reads them; the separate LEGACY dict, the fallback when
  invoice_chain.json is missing, stays). The script passes 47 of 47 and rewrote part2/tables/accounting_macros.tex:
  \acctItgcInvEng $267,000 -> $205,000, \acctItgcRefEng $137,000 -> $75,000, \acctItgcAppEng $150,000 -> $88,000,
  \acctItgcValEng $100,000 -> $24,000, \acctItgcNPVEng $0.52M -> $0.40M, \acctItgcTests 42 -> 10. The sentence of
  theory_accounting.tex that reads "The engine's illustrative \acctItgcValEng{} a retest, the effort of about
  \acctItgcTests{} such tests, gives \acctItgcInvEng" is now a tautology and is for the Paper 2 owner to drop.
  code/paper1_macros.py was left to the Paper 1 editor, who has since set its C_val to $24,000
  (test_regression.py::test_paper1_itgc_units_follow_engine passes).
- **Golden snapshots re-accepted** after this diff, all from the success recalibration (higher success probabilities
  raise every plan's risk-adjusted value; a0 and c0 are drawn over their new ranges):
  synthetic: plan value $1,762.9M -> $1,995.1M; 24 -> 22 items (added P12 and the F02 residual stream 11; dropped the
  F02 and F03 outsourced streams and the F07 residual stream 8 and F12 residual stream 2); P10/P50/P90
  $764M/$1,739M/$2,356M -> $710M/$951M/$2,395M; final cash Rule of 40 43.4 -> 44.1; FTE after 2,399 -> 2,392; regime values public $1,995.1M,
  family $2,654.1M, pe $621.4M, vc $1,011.4M, hybrid $1,997.9M, permanent capital $382.2M. The lower P50 is a
  sampling effect of the golden settings, which draw parameters five times: in three of the five draws a drawn class b
  or d parameter makes 9 to 12 of the 22 plan columns infeasible (worth zero in that draw, as before this change; with
  the previous calibration and its own random sequence one draw of five did so), and the point draw's P50 is $2,471M.
  small: plan value $89.1M -> $105.6M, same 11 items; P10/P50/P90 $0.0M/$4.1M/$140.9M -> -$0.1M/$26.9M/$121.3M; final
  cash Rule of 40 20.1 -> 21.3.
  pe: plan value $112.8M -> $157.4M; 8 -> 9 items (F02 residual stream 6 added); P10/P50/P90 -$13.1M/-$4.1M/$5.8M ->
  -$25.0M/-$2.6M/$12.6M; final cash Rule of 40 39.9 -> 41.1; FTE after 1,617 -> 1,595.
- **examples/synthetic_run/report regenerated** (full settings): planning-case plan value $1,813.5M -> $2,087.4M; P10/P50/P90
  $116M/$1,138M/$2,221M -> $235M/$1,340M/$2,205M; probability of loss 0.025 -> 0.010; final cash Rule of 40 P50 0.232 ->
  0.242; 24 items either way (F04 residual 11, F12 residual 2 and F13 residual 1 in; F02 residual 11, F07 residuals 8
  and 9 out); Wave 0 covers 18 processes for $1.3M (was 20 for $1.4M); junior production work halves in 3 functions
  (was 2); regime values public $2,087.4M, family $2,654.1M, pe $621.4M, vc $1,011.4M, hybrid $1,997.9M, permanent
  capital $382.2M. Lever rankings, X-level choices, durable share 0.625, a_min (three human layers, 0.03) and
  R_max 0.761 are unchanged.
- **Paper 2's invoice example.** data/examples/invoice_chain.yaml sources success.a0 and success.c0 from the engine
  defaults, so test_paper_examples::test_inputs_resolve_to_engine_defaults fails until code/examples/invoice_chain.py
  regenerates data/examples/invoice_chain.json (and part2/tables/invoice_macros.tex); its varpi_p rises with the new
  calibration. Not regenerated here (Paper 2's files).

## Engine pass after the Paper 1 and Paper 2 revisions (29 Oct 2026)

Brings the engine in line with notes/p2_theory_fixes_v2.md Section 11 (engine changes E1 to E9), notes/theory_fixes_v2.md
Section 10 (Paper 1), notes/acquirer_fixes_v2.md Section 5, today's params commit follow-ups (QA/ISSUES.md items 9 to
12) and the P3 rows of notes/cross_paper_impacts.md. Engine version unchanged (0.2.0). No params YAML, .tex or
estimation file was edited.

- **E1, disruption counted twice (ISSUES fixed 16, was open 9).** New setting shocks.disruption_haircut, off: the base case no longer
  cancels work in flight on leadership changes and vision overhauls (plans.py flow survival; risk.py disruption
  draws), because success.b_bar (McKinsey 2021) and the success logit (Gartner and S&P Global production rates) come
  from outcome surveys that already include them; Paper 1 drops exp(-nu_D T_emb) from q for the same reason. nu_D still
  prices the timing of disruptions (prop:ext-shocks); the new named scenario disruption_shocks turns the haircut on.
  Recalibrating a0 instead (round 2 Section 1.1, second branch) would need a production probability of 0.92 to reach
  the product 0.46 under a survival of 0.75, against the 0.48 to 0.54 the logit is calibrated to. Open for the author
  (ISSUES open 9, new text): the engine's expected realization at the reference process is 0.50 x 0.67 = 0.34 against
  Paper 1's 0.47.
- **Monte Carlo shock draws never ran (bug, ISSUES fixed 17).** run_monte_carlo switched shocks off on the parameter copy used
  to re-price the columns and passed that copy to outcome_draws, so the explicit draws (disruptions, reorganization
  freezes) were skipped. outcome_draws now takes the run's own shock section; reorganization freezes, which Paper 1
  keeps as its clock (1 + nu_R T_frz), now enter the Monte Carlo; disruptions do only under disruption_shocks.
- **E2, accountability floor as an ICFR constraint (RA-1).** formulas.amin_design is the constrained minimum of
  prop:acct-amin and def:acct-admissible (Part I prop:amin(b), (c)): a design is admissible iff 1 - (1 - P)^{N_o} <=
  eps_bar with P = p_cc + (1 - p_cc) prod_x [p_cm,x + (1 - p_cm,x) p_x^{n_x}]; a_min is the cheapest admissible design
  (inf if none) plus the plan's ITGC lines and C^tml and the expected cost of errors below materiality N_nm L_nm P; the
  consequence of a material misstatement, N_o L_mm P, is reported as the residual expected consequence and never
  traded against cost; also reported: each type's minimal admissible depth and common-mode floor, the cheapest
  admissible human-only design and the cost-plus-consequence optimum with its admissibility (prop:acct-amin(f)). New
  helpers amin_admissible and amin_min_depth. Parameters: accounting.N_o 24 [12, 48] (d), eps_bar 0.05 [0.01, 0.05]
  (policy; the report shows 5 and 1 percent; Paper 1 takes 1 percent as central, see ISSUES open 11), p_cc 0 [0, 0.002] (d),
  L_mm $10M (d, reported only); N_mm and L_mm became N_nm and L_nm (errors below materiality, same values);
  control_types are now the papers' example (human 0.05 / 0.002 / $500,000, AI 0.02 / 0.005 / $50,000; the engine's
  unsourced three-type set is gone), which give one human over one AI layer at 5 percent and one over two at 1 percent.
  security.accountability_floor reports both thresholds; the ceiling credits a design gain only when both the best and
  the human-only designs are admissible.
- **E3, C_val $100,000 -> $24,000 (class d -> b).** 10 controls x 16 hours (KPMG 2025, class b) x $150 (class d), range
  $12,000 to $48,000; FT-20 resolved by definition (regression suite in the run costs, change ticket in itgc_c_chg,
  control re-testing in C_val). Accounting example lines: invoice application $204,672 (was $266,967), refund agent
  $74,672 (was $136,967), a reference application at the engine's default counts $87,672, within 10 percent of the
  KPMG-anchored $80,000 (ISSUES fixed 19, was open 11). Paper 1's and Paper 2's copies still carry $100,000 (ISSUES open 10).
- **E4, central industry pass-through 0.5 (ISSUES fixed 18, was open 10).** competition.phi_ind 0.5 [0, 0.7] (b) when the firm gives
  none; the derived homogeneous-Cournot value (0.8 at HHI 0.25) is reported as a benchmark (econ info game.cournot,
  should-versus-could paragraph). Durable share at the default HHI 0.625, was 0.40. phi_ind is now drawn in the Monte
  Carlo over its range; pass_through_50 equals the central case unless the firm gives a value.
- **E5, server tax deductibility.** finance.psi_equipment's note is corrected: 40 percent is the 168(k)(10)
  transitional election, electing out (168(k)(7)) gives no bonus (MACRS), and current law gives domestic servers psi = 1;
  range [0.80, 1.0]. New formulas.psi_schedule and psi_equipment (MACRS five-year GDS and ADS straight line over five
  years, 168(g)(3)(C), read at a copy of the statute) and firm inputs tier0 bonus_election and foreign_server_share.
  Owned compute capital now carries the servers' wedge Upsilon_K (it carried the development psi), and the lever map's
  capital hurdles are multiplied by Upsilon_K (= 1 under current law, so no default changes).
- **E6, the level of X (D-1).** finance.X_default 8 [5, 13] (the withdrawn 7 to 13) -> 5 [2.5, 9], a setting: the
  middle evaluation point, used only when the Gordon equation has no root and no multiple is given (no golden firm uses
  it). New finance.X_eval_points [2.5, 5, 9] and tier0 growth_weight_low/high. lever_map.x_levels reports, at each
  point, the top lever at the common proportion, whether the growth engine outranks G&A (X > X^ddagger_0), the largest
  price per dollar of acquired revenue that raises the score charged in full, as an annuity and as a user cost (new
  formulas.acquisition_price_bounds), whether the firm's own price passes, and the AI product dilution rule, with sign
  flips (formulas.sign_flips) and thresholds outside the points flagged. product.features_portfolio reports the chosen
  set and ranking at each point. The excluded-lever rule "acquisitions priced above X_o" (levers.py line 140) is now
  conditional on X_o and gives the annuity and user-cost bounds. Owner weights still come from the regime presets or a
  firm input; ratio tests against the revealed spend weight are unchanged.
- **E7, regulatory facts.** MODEL_RISK.md cites SR 26-2 and OCC Bulletin 2026-13 (17 April 2026; generative and agentic
  AI outside scope, footnote 3) in place of SR 11-7, and adds the accountability-floor, disruption and growth-weight
  conventions. impute.eu_ai_act_high_risk_applies: an Annex III unit is high risk only with an EU nexus and a plan that
  runs past 2 December 2027 (permissibility.eu_ai_act_annex_iii_from; Annex I 2 August 2028 recorded), Regulation (EU)
  2026/1744; reported in the people section.
- **E8, c_err at the review that remains, and common mode.** New formulas undetected_rate_remaining_review and
  cerr_remaining_review (prop:tasks-cerr(c); Part I lem:fullcost(c)) and nu_common_mode (nu_out + (1 - q_chg) nu_reg;
  ass:ext-commonmode, lem:fullcost(e)). The failure-mode table reports the error floor with no review and with one AI
  review layer on another provider (chi = reliability.ai_review_joint_error 0.5 (d, unmeasured) x ai_review_agreement
  0.60 (Kim et al. 2025, linked; P(same wrong answer | both wrong), not a conditional error rate)); the ceiling reports
  c_err without people (no review, Part I's convention), the expected common-mode cost c_cm (ext notes 4.8) and
  R_max without people. Provider events: reliability.nu_cm is split by regression_share 0.5 (b) and change controls
  q_chg 0 (d; firm input tier3_security change_controls_share); at q_chg = 0 the rate is unchanged.
- **Acquirer fixes (notes/acquirer_fixes_v2.md Section 5; IB-4, F21).** formulas.acq_zero_spend_growth (G_i =
  ln[1 + s(NRR - 1) + (1 - s) gamma_ns]); acq_standstill(g_org, k_acq, g) reports acquired growth g + d^org, its cash
  cost and the standstill case (backward compatible at g = 0); margin_before_financing, acquisition_capital,
  acquisition_charges (level annuity or user cost, year-end or time-weighted capital, the double-charged scores and the
  return on acquisition capital before and after depreciation). regimes.limits_check works in continuously compounded
  rates, takes organic growth from tier3_regime organic_growth_reported (ln(1 + x), labelled company-defined) or G_i
  (subscription_share default 1, the upper bound on decay) and reports both cases; regimes.acquired_growth_report gives
  every score labelled before or after interest, the before-interest cash basis with the double-charge warning, the
  charging grid at NRR and the return on acquisition capital (new tier3_regime inputs operating_cash_flow,
  interest_paid, interest_tax_rate, acquisition_outlays). The pc preset's r_debt already was ln 1.09625.
- **Paper 1 items (notes/theory_fixes_v2.md Section 10).** R_max takes the replacement term -(1 - psi tau) delta_K k of
  the revised cor:ceiling (delta_K = 0 keeps the Rule-of-40 form eq:Rmax, the engine's use). New
  formulas.own_compute_markup_threshold (rem:owncompute: owning pays iff the vendor markup exceeds s_srv L_srv G at
  psi = 1, 16.5 percent at G = 5 percent with Part I's 3.3; at psi < 1 the bar rises), reported in the lever map. The
  six relabelled Part I results keep their labels; formulas.py cites only prop:score among them (delta_star,
  sigma_star, R_star), whose summaries now say Lemma. The admissible a_min design (one human over one or two AI layers)
  is E2.
- **Notes lock.** notes/acquirer_notes.md changed at 14:32 (acquirer agent): items 6 (limits: holding g needs g +
  d^org, G_i formula) and 7 (m^cf before financing; user cost on decayed capital; year-end or time-weighted capital)
  and a pointer section 10. Both formula changes are implemented above; the lock is accepted
  (tools/check_sync.py --accept).
- **Tests.** test_cross_impl's a_min block is rewritten against verify_part2_accounting.best_admissible, P_design,
  admissible, Pbar and n_min_type (designs at 5 and 1 percent, one application or one per layer, all-AI and human-only
  admissibility, weak ITGCs, the cost-plus-consequence optimum, lines additive); it no longer reads the script's LEGACY
  keys or best_g, which the Paper 2 owner can now delete. The ITGC check uses the KPMG C_val and asserts it equals the
  script's C_VAL_KPMG. New: test_formulas::test_amin_design_is_the_constrained_minimum; test_accounting asserts
  admissibility and a floor nonincreasing in revenue (Part I prop:amin(d)); test_acquirer: G_i and required acquired
  growth (verify E4, H6: 71.7 to 76.0 percent, 63.7 percent), the charging grid (E12 to E14: double charge, bounds,
  exact time average), the acquisition price rule at the evaluation points (E15), limits_check with both organic
  cases and the growth-quality block. test_regression's Paper 1 ITGC copy check is split out as
  test_paper1_itgc_units_follow_engine, which fails until code/paper1_macros.py uses $24,000 (ISSUES open 10).
- **test_tier0_only_reports_wide_ranges rewritten (ISSUES fixed 26, was open 12).** The failing first assertion compared the total P10-P90
  dollar spread of the Tier-0 and full-tier runs. Cause, by one-at-a-time reverts of the round-2 changes on the
  pre-pass engine (golden settings; spreads full / Tier 0): all round-2 values $2.39bn / $2.27bn (fails); all reverted
  $1.70bn / $2.64bn; only success.a0 reverted $2.05bn / $2.26bn (passes); only success.a0 applied $2.11bn / $2.10bn
  (fails); b_bar, the reliability targets, the regulated multiplier, kappa_abs and the ITGC units change nothing
  material. The a0 recalibration (1.87 [1, 3], class b) puts success probabilities near one half, where outcome
  variance is largest, so outcome and parameter risk, which firm data cannot remove, dominate the total spread; the
  round-2 b_bar also lowered the Tier-0 plan from $1.39bn to $1.10bn, and a dollar spread scales with the plan. No
  defect in how Tier-0 priors widen: with parameters held, the imputation spread is wider at Tier 0 ($1.07bn against
  $0.98bn before this pass; $1.49bn against $0.85bn, 1.08 against 0.48 of plan value, after it). With this pass's engine
  the total dollar spread orders the two runs differently across seeds (Tier 0 wider at 2 of 4 seeds; per dollar of
  plan value at 3 of 4), because the golden settings draw parameters only five times. The property as stated is
  therefore wrong: the test now checks the data part, in dollars and per dollar of plan value, and the Tier-0 labels.
- **Golden snapshots re-accepted** (tools/accept_golden.py) after this diff. Attribution by reverting one change at a
  time with --set on the new engine: E1 accounts for nearly all of the plan-value change (plan value with the
  disruption haircut back on: synthetic $1,390.0M, small $53.3M, pe $81.5M); E4 adds $13M to the synthetic plan
  ($1,749.8M at the derived Cournot pass-through); C_val changes nothing (no golden plan deploys an in-scope AI
  application). The Monte Carlo quantiles also move because the reorganization-freeze draws now run (ISSUES fixed 17),
  phi_ind is drawn over [0, 0.7], and the new class b and d keys (accounting N_o, p_cc, N_nm, L_nm, L_mm; reliability
  regression_share, q_chg, ai_review_joint_error) change the draw sequence.
  synthetic: plan value $1,377.9M -> $1,762.9M (+28%); 23 -> 24 items (added F02 and F03 outsourced streams, F07
  residual streams 8 and 10, F12 residual stream 2; dropped P10, P12, F02 residual stream 6, F04 residual stream 4);
  P10/P50/P90 $298M/$1,448M/$2,685M -> $764M/$1,739M/$2,356M; final cash Rule of 40 41.6 -> 43.4; FTE after 2,418 ->
  2,399; regime values public $1,762.9M, family $2,391.7M (was $1,784.4M), pe $525.6M (was $402.5M), vc $916.7M,
  hybrid $1,764.9M, permanent capital $314.8M (was $246.6M).
  small: plan value $53.6M -> $89.1M; 9 -> 11 items (P12, P21 and the F08 residual stream added, P08 dropped); P10/P50/P90
  -$1.6M/$21.0M/$114.8M -> $0.0M/$4.1M/$140.9M (in two of the six imputation draws a drawn reliability parameter makes
  the plan's automated steps infeasible, so those draws are worth zero, as before this pass); final cash Rule of 40
  17.1 -> 20.1.
  pe: plan value $81.7M -> $112.8M, same 8 items; P10/P50/P90 -$21.5M/-$0.3M/$12.9M -> -$13.1M/-$4.1M/$5.8M; final cash
  Rule of 40 39.1 -> 39.9.
- **E9, playbook regenerated (code/playbook/run_archetypes.py, after the engine tests passed and the sample-audit
  rerun was final).** The archetype source switched from the v2 rebuild of data/panel_v2_all.csv to the audited v3
  core sample data/panel_v3.csv, with acquisition-affected firm-years flagged by acq_flag_v3 in place of acq_flag
  (archetypes.load_core_panel; the v2 loader is kept as load_core_panel_v2 for this comparison), so Paper 1 and Paper 2
  use one sample; cell definitions unchanged. Rewritten: data/playbook/*, part2/tables/playbook_*,
  sections/tables/levers_position_macros.tex and tab_levers_position.tex, notes/playbook_results.json; the generated
  table note now gives the durable share at the central pass-through (0.62, Cournot 0.40 as a benchmark) and names
  the v3 sample. code/verify_part2_playbook.py: 36 of 36 checks pass on the new outputs. Population (2023-25 core
  firm-years with an FCF margin) 446 -> 435, non-acquisition 377 -> 365; cut points g median 12.9 -> 12.7, g75 22.3 ->
  21.7, m25 -10.7 -> -10.3, m median 2.4 -> 2.5, m75 11.5 -> 11.7, R75 27.8 -> 27.7, R95 44.8 -> 44.6 (percent). Cell
  medians, v2 -> v3 (n (firms); g, FCF margin after SBC m, R = g + m, GAAP operating margin, S&M, G&A, R&D, gross
  margin, capex intensity, percent of revenue):

  | archetype | n (firms) | g | m | R | m_op | S&M | G&A | R&D | gross margin | capex |
  |---|---|---|---|---|---|---|---|---|---|---|
  | A1 Growth corner | 33 (23) -> 28 (23) | 30.8 -> 29.1 | -25.8 -> -23.0 | 5.6 -> 6.7 | -29.8 -> -30.2 | 50.6 -> 49.7 | 23.1 -> 23.7 | 32.0 -> 32.3 | 68.4 -> 69.6 | 2.7 -> 2.7 |
  | A2 Balanced upper quartile | 44 (30) -> 43 (30) | 21.0 -> 20.9 | 13.3 -> 13.8 | 35.8 -> 35.4 | 12.3 -> 12.4 | 25.9 -> 26.5 | 10.1 -> 10.1 | 20.0 -> 20.1 | 78.6 -> 79.1 | 2.1 -> 2.1 |
  | A3 Mature cash generator | 54 (29) -> 52 (29) | 7.7 -> 7.7 | 19.4 -> 19.7 | 26.0 -> 26.0 | 21.2 -> 21.0 | 18.9 -> 18.7 | 10.1 -> 10.0 | 14.9 -> 14.9 | 80.1 -> 80.0 | 1.6 -> 1.5 |
  | A4 Sub-40 grower | 49 (36) -> 48 (35) | 17.2 -> 17.1 | -5.2 -> -5.4 | 11.4 -> 10.8 | -10.4 -> -10.3 | 43.2 -> 43.0 | 19.4 -> 19.1 | 26.1 -> 26.1 | 74.4 -> 74.4 | 2.0 -> 2.1 |
  | A5 Stalled | 85 (51) -> 84 (49) | 2.1 -> 2.1 | -12.0 -> -12.2 | -9.6 -> -10.8 | -16.4 -> -16.5 | 32.3 -> 31.3 | 19.6 -> 19.5 | 25.1 -> 25.1 | 70.1 -> 69.6 | 2.5 -> 2.5 |
  | A6 Near-frontier elite | 15 (9) -> 13 (7) | 38.7 -> 36.3 | 22.4 -> 22.4 | 54.1 -> 54.1 | 7.4 -> 7.4 | 19.2 -> 19.8 | 14.7 -> 14.7 | 17.3 -> 21.4 | 73.0 -> 74.3 | 1.6 -> 1.6 |

  A7 (the acquisition-driven compounder) is not a panel cell and is unchanged. What moved: the elite's public-owner
  ranking flips to R&D first (2.1 points against the growth engine's 2.0; its R&D gap to the top decile 4 -> 8 points),
  so the growth engine is first at the public weight in five archetypes, not six (\pbNGEFirstPub); the durable share
  0.40 -> 0.62 (E4); sponsor and VC weights of the elite 17.0 -> 15.0 and 15.7 -> 13.5; the first waves change in every
  panel archetype (engine changes E1 and E4: for example the balanced upper quartile now starts with Lead to close,
  NPV $255M, and the mature cash generator with Quote to contract, $39M); step tiers A/B/C 49/23/28 -> 50/24/26 percent.
  The Paper 2 playbook text (part2/theory_playbook.tex) and Paper 1's sections/levers_by_position.tex read these
  macros but may describe the old ranking or durable share in prose: their owners should check them.
- **Synthetic example run regenerated** (examples/synthetic_run/report; full run, all scenarios and global
  sensitivity), against the same run on the engine of the params commit: plan value $1,378M -> $1,814M (planning
  case), P10/P50/P90 $221M/$981M/$1,909M -> $116M/$1,138M/$2,221M (reorganization freezes now drawn; phi_ind drawn),
  23 -> 24 processes (added F02 residual streams 7 and 11, F07 residual streams 8 to 10; dropped P10, P12, F04 residual
  stream 4, F13 residual stream 1); the same five largest processes lead, now $147M to $268M, and five of them (was
  four) raise data readiness first; Wave 0 covers 20 processes ($1.4M, was 17 and $1.2M); cost of revenue moves to
  second in the lever ranking of the public, family, PE, dual-class and permanent-capital owners (durable share 0.40
  -> 0.625), and the growth engine falls to last for the family and dual-class owners; the a_min design is three human
  layers (was three human and three automated under the old types; the plan puts no AI in ICFR scope); the recommended
  plan is now also the minimax-regret plan (was the pass_through_50 plan); the feature portfolio is the same at every
  growth-weight evaluation point; no X-dependent recommendation flips between 2.5 and 9 (X^ddagger_0 for G&A is
  12.4). Run time 89 s.
- **Test results.** 190 tests: 189 pass; test_paper1_itgc_units_follow_engine fails until Paper 1's copy of C_val
  follows (ISSUES open 10). test_full_synthetic_run_under_two_minutes passed (91 s; it took 125 s in an earlier run
  of this pass while the sample audit's estimate_v3.py shared the two cores, and 172 s before this pass under the same
  load); it is load-sensitive and the threshold was not changed.

## Params commit (29 Oct 2026, assumptions round 2)

All round-2 values adopted in one commit (notes/assumptions_round2.md Section 0; notes/params_commit_2026-10-29.md has
the full table with old and new values, classes, sources and the files changed). Engine version unchanged (0.2.0).

- **Defaults changed.** success.a0 3.0 [2, 4] (d) -> 1.87 [1, 3] (b): a reference five-step process reaches production
  with probability 0.50 (Gartner 48%, S&P Global 54%; 0.58 before), as Section 1.1 specifies when b_bar carries the
  realization haircut. success.b_bar 0.85 [0.5, 1] (d) -> 0.67 [0.37, 0.85] (a, survey; McKinsey 2021), linked to
  params.yaml project_outcomes. constraints.kappa_abs range [0.05, 0.20] -> [0.05, 0.22] (params change_capacity,
  re-grounded on WEF 2025). review.r_bar_high 0.99 [0.98, 0.999] (d) -> 0.98 [0.975, 0.995] (b), review.q_M 0.998
  [0.99, 0.9995] (d) -> 0.995 [0.99, 0.998] (b), augment.e_H 0.02 [0.005, 0.05] (d) -> 0.02 [0.009, 0.05] (b), all three
  linked to params_reliability.yaml human_baseline. build.regulated_mult 1.5 [1.0, 2.5] (d) -> 1.5 [1.1, 2.0] (b, KPMG
  2025 SOX survey, derived), linked; it multiplies build months only, so the ICFR lines are not counted twice.
  accounting.itgc_c_chg $5k -> $2.5k [1k, 5k], itgc_c_ops $30k -> $20k [10k, 55k], itgc_c_ifc $15k -> $10k [5k, 30k]
  (b); itgc_setup, itgc_c_acc and C_val unchanged. Notes only: review.L_mult_regulated, build.int_cost_per_system,
  success.b_bar_U, finance.pass_through_phi.
- **New.** finance.c_c_full_automation (Part I's compute share at full automation by year: 2025 prices 0.06, 2028
  0.12, 2031 0.08, 2036 0.05; d with a b anchor), reported by security.ceiling_terms as R_max at the plan's last year
  next to the firm's current compute share (report section "Part I frontier shift"). competition.phi_ind_scenarios
  [0, 0.5, 0.7] (b), linked to params.yaml pass_through: named scenarios pass_through_0 (fixed prices), pass_through_50
  and pass_through_70 set competition.phi_ind in dur = 1 - phi (1 - HHI). The central case keeps the derived Cournot
  phi_ind. tests/test_regression.py::test_round2_parameters_follow_params_files keeps the engine, params.yaml,
  code/calibrate_horizons.py and code/paper1_macros.py on the same values; test_cross_impl's ITGC line check moved to
  the new unit costs ($266,967 and $136,967, from $346,967 and $156,967) and now asserts the reference script's units
  equal the defaults.
- **Golden snapshots re-accepted** (tools/accept_golden.py) after this diff, all from the default changes above (lower
  success logit and realized share; lower review cost at the 0.98 target; cheaper ICFR lines; Monte Carlo draws over
  the new class b and d ranges, a0 now class b over [1, 3]):
  synthetic: plan value $1,394.9M -> $1,377.9M (-1.2%); plan 24 -> 23 items (P12 added; F02 outsourced and F12 residual
  stream dropped); P10/P50/P90 $643M/$1,057M/$2,339M -> $298M/$1,448M/$2,685M; final cash Rule of 40 41.7 -> 41.6.
  small: plan value $71.5M -> $53.6M (-25%); P01 dropped (10 -> 9); P10/P50/P90 $0/$6.0M/$152.4M -> -$1.6M/$21.0M/$114.8M;
  final cash Rule of 40 18.4 -> 17.1. pe: plan value $80.8M -> $81.7M (+1.1%); F13 residual stream replaced by F11
  residual stream; P50 -$5.5M -> -$0.3M.
- **Known test results after the commit.** test_tier0_only_reports_wide_ranges fails at its first assertion: with the
  golden settings (6 imputation x 60 outcome draws, parameter draws on) the full-tier P10-P90 is now $2.39bn against
  tier 0's $2.27bn ($1.70bn against $2.64bn before); the data-only spread it also tests still favors tier 0 ($1.07bn
  against $0.98bn with parameters held). test_full_synthetic_run_under_two_minutes is load-sensitive: 124 s with
  load average about 3.4 on two cores; the three pass-through scenarios add about 21% to a full run (108 s -> 131 s
  under the same load).

## 0.2.0 (29 Oct 2026)

Engine for Part III, built against notes/unified_model_spec.md Sections 0 to 29.

- **Core and extensions.** All Part I and core formulas with paper labels (formulas.py); review with a detection
  rate and the infeasibility flag; augmentation quality cost and the decision/creation flag; the failure taxonomy
  (hallucination, automation bias and its detection threshold, autonomy levels, pipelines and their decomposition,
  tail CVaR, provider concentration); constant-hazard and logistic reliability; domain and physical horizons; plateau.
- **Regimes, product, accounting, competition.** Regime NPVs with terminal values at h_x 0.5 and 1, the PE
  waterfall, EPS path, dip budgets, LBO break-even, hybrids; product pricing, Bass seats, migration with a two-part
  tariff, features, sourcing, margins; the GAAP path, ASU 2025-06, ASC 420/712, ICFR timing and a_min by design;
  durable share and the dominant-strategy and entry tests.
- **Labor, talent and jurisdiction (theory_labor).** Statutory calculators (WARN, Cal-WARN, NY, NJ, EU, DE, FR, UK,
  IN), legal leads and the free parallel run, cutover streams, severance at max(floor, plan), survivor quits and the
  per-wave charge, knowledge holders, the redeployment bound, the AI wage premium, the maintenance ceiling, hiring
  and hire-or-contract, the location lag, data residency, and the pace bound.
- **Industry priors (spec 24.10).** Damodaran groups through the NAICS crosswalk: k on the unadjusted basis, cost of
  capital as the discount rate, weak-prior and low-confidence flags.
- **ICFR scope (spec 25; sec:acct-scope).** Process, system, integration and policy channels from the data contract;
  conditions decided by firm inputs ("assumed in scope" otherwise); each in-scope AI application carries the ITGC
  line of eq:acct-itgc and the timeliness cost C^tml of prop:acct-itgc(d), in the plan and in a_min (amin_design sums
  the lines); EU AI Act high-risk status only with an EU nexus.
- **Uncertainty.** Thirteen named scenarios with minimax regret; Monte Carlo over data and class b and d parameters;
  Morris then Sobol, with int_cost_per_system, int_convexity and regulated_mult always in the Sobol set.
- **Outputs.** report.md (14 sections, plain language, every number traced, assumptions listed), report.json and
  CSV tables; Required Notice in every report and in --version; decision-support statement.
- **QA.** Traceability, cross-implementation, property, regression, paper-sync, privacy, validation, wage and
  disclosure tests; golden snapshots; notes change control; MODEL_RISK.md; QA/ISSUES.md.
- **Defaults changed in this version.** finance.capital_intensity_k 0.02 -> industry k (0.645 generic, 0.574
  software); build.ai_engineer_premium 1.3 -> 1.11; jurisdiction.hiring_lead_months 4 -> 3; role wages from OEWS May
  2025; seat price default $1,380 -> $1,050 a year (params product.seat_list_prices, class a); outcome price range
  $0.49 to $2.00 -> $0.50 to $2.00; accounting.C_val $30k -> $100k (ICFR retest per forced upgrade);
  accounting.icfr_functions removed; the synthetic firm's service-desk seat price follows the default.
- **Notes re-check (29 Oct, after spec 26 and 27).** Spec 26 now allows four vendors for price examples
  (Freshworks, Intercom, Salesforce, HubSpot): product.PRICE_VENDORS includes Freshworks, whose only usage price is
  per session and stays out of the outcome range ($0.50 to $2.00 unchanged); the seat price is the four-vendor median
  ($1,050). Quote-to-contract "negotiate terms" stays outside ICFR scope (already so in the data contract; regression
  test added). Labor notes (e_mnt 0.48 [0.29, 1.14], class b) and accounting notes (ITGC unit costs, timeliness,
  the a_min band, the acquirer replace path) match the engine; the acquirer-section text changes (4.8) and the Paper 1
  estimands (spec 27) need no engine change. Regimes notes (the permanent-capital row: debt ln(1.09625), the
  sponsor's preset kept at 8 percent) match the new regime. Spec 28 (lever map, archetype runner) is served by the
  public API; spec 29 is the playbook below. Built against spec Sections 0 to 29.
- **Permanent capital and the limits to buying growth (theory_acquirer; notes/acquirer_notes.md Section 3).** A sixth
  regime, permanent_capital: never sells, internal decisions at the unlevered hurdle ln(1.25) as a going concern
  (prop:acq-pc(d)), growth weight m_hat/(i_U - G); its returns view gives the method IRR (five years plus a terminal
  value at r_tv), the permanent IRR, the levered IRR under ND_0 = min{0.85 P, ND^rep} with a cash sweep, P^max and
  its bounds (eq:acq-pmaxbound), the program uplift the hurdle needs, and the 4.0 covenant at entry. Presets come from
  params.yaml ownership_regimes.permanent_capital (annual rates through to_continuous(); r_debt the observed 9.625%,
  range 8.625% to 9.625%). The limits check (prop:acq-limits) reports the treadmill and g^max, deal size, series and
  foreign-investment review and consumer law. Rule: a class d limit whose params.yaml value is null takes its
  neutral_value (limit off) unless a scenario or override sets it, and verified_domain is never a range. New
  tier3_regime fields: nrr, acquisition_price_to_revenue, target_growth, reference_target_revenue,
  switching_cost_ratio_mean. tests/test_acquirer.py repeats the reference checks D0 to D4 and H1 to H5 (the script
  writes macro files, so it is not imported). notes/acquirer_notes.md joins the notes lock.
- **Playbook (spec 29; notes/playbook_engine_spec.md Sections 4 and 5).** playbook.build (called as
  roadmap.playbook): playbook_activities.csv, one row per activity unit (a DWA in a process step, the decision
  level), and playbook_steps.csv, one row per process step (execution), with the spec's field names: modes now and
  at target for the activity and the step, the best column and the plan; binding_now and binding_target in the
  spec's order; preconditions; gates with their source (model, firm policy or law); wave and the steps that cut over
  together; roles (process owner, top three occupations from the roster or the prior, AI engineer months, reviewer
  FTE, legal lead); KPIs (cycle time is "measure in Wave 0" unless a Tier 4 study gives it); controls; evidence with
  grounding classes, AEI usage, METR feasibility and O*NET task statements (data/tasks/task_statements.csv, up to 12
  ids and the top two texts); tiers per def:playbook-tier (A feasibility-bound, B cost crossover or reliability
  gate, C when one class d input at a range end changes the automate or AI decision, or the process's value is
  positive in fewer than playbook.tier_c_prob = 0.8 of the Monte Carlo draws); switch conditions with distances;
  pilot bands for every process with a positive best column (W7). playbook_data_dictionary.csv carries the O*NET
  CC BY 4.0 attribution, which also closes the report.
- **Firm inputs for the playbook.** tier3_tasks (firm_task, process_id, step, dwa_id, hours, volume): tasks are
  mapped by the given DWA or by word overlap with O*NET task statements; mapped tasks replace the step's activity mix
  and hours, unmapped ones are listed in firm_tasks_mapping.csv. tier3_policy (residual_error_tolerance,
  min_pilot_success, payback_limit_years) replaces the model's gate values. tier4_time_study accepts cycle_time_days.
  process_activities.csv physical_override and licensed_override are used when present (W5).
- **Lever map (spec 28; W2, W3, W13).** levers.lever_map, result["lever_map"] and a report subsection "Levers by
  position and setup": the position calibrated so the observed spend is optimal (lem:playbook-calib,
  finance.spend_ratio 3.3, class c), per regime the lever values at levers.proportion = 0.10, the switch weights
  X^ddagger_0, exact (eq:reg-Xdag) and demand-pull, the identified form, the headroom switch, the screening flip,
  the binding constraint (position from Paper 1's gap table, snapshot in priors/frontier_gap_bands.csv by
  tools/sync_gap_bands.py; setup from first-year utilization and the playbook's gates) and the excluded levers with
  their rules. frontier_shift reports G&A and maintenance R&D separately and values growth-activity savings as score.
- **Growth weights (W1, W14, W15).** Exit and permanent-capital weights use m0 - k G, with the m_cash versions
  reported; the exit weight has no cap on G (limit m_hat tau + X_T at r = G) and its exit EBITDA per permanent dollar
  is m0; the permanent-capital weight is None when G >= i_U; a new Tier 0 flag multiple_is_net_of_pressure makes the
  input multiple the public weight and starts the other regimes from k + (1 + w)(X_in - k).
- **FCF margin (W17, optional).** A Tier 0 fcf_margin (FCF after SBC over revenue) sets m0 = fcf_margin + sigma + k g
  (Part I's identity); the difference from the line items is reported as part1.a_other inside a. Notes re-check:
  notes/playbook_engine_spec.md draft 2 (W14 to W16, the W10 resolution, Section 7 test values) matches the engine;
  the regimes B7 weights (2.21, 2.70, 3.50) and the cor:capital hurdles are tested. Its 13:35 revision (26 bytes)
  needs no engine change.
- **Lever ranking (W16).** The ranking compares growth-engine automation, G&A, maintenance R&D and cost of revenue at
  the same proportion; demand pull, retention, the product break-even and the capital hurdles are reported apart.
- **Tier test of impute-level keys (synthesis theorist note 1).** review.r_bar_high, review.L_mult_regulated,
  review.r_bar_licensed and readiness.iota_min_regulated_add are tested too: impute.retarget_units recomputes the
  units' targets, loss multiples and readiness floors before the economics is rebuilt.
- **Speed.** The playbook builds one plan year per flip (its decisions read year 0), aggregates steps with vectorized
  group sums and caches the O*NET task index; economics._gwa_match matches prefixes over unique ids. The playbook
  takes about a third of its first version's time; every result is unchanged.
- **Public API.** autofrontier.api: run, playbook, write_playbook, lever_map, synthetic_firm, version, REGIMES.
- **Golden snapshots re-accepted (29 Oct), twice.** First: the only change was the new
  regime_values.permanent_capital entry. Second: Tier 4 flags now reach the activity units (QA/ISSUES.md 14), which
  narrows the Monte Carlo spread of measured steps; only the value quantiles of the synthetic and PE firms changed
  (synthetic P10 $286M to $643M, P50 $1,030M to $1,057M, P90 $2,495M to $2,339M).
- **Fixes.** Results no longer depend on PYTHONHASHSEED (regulated-class ties were broken in set order; they now go to the most demanding class); one survivor
  base (in-house FTE on changed steps less the displaced) everywhere; plan ITGC lines no longer cancel out of the
  ceiling's a_min.
