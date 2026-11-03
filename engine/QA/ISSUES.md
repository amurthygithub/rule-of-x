# QA findings

Each finding names the side that was wrong (engine, example, data, notes) and what fixed it. Open items are at the
end.

## Fixed (29 Oct 2026)

1. **Regulated status tied to the reliability target (engine).** A step counted as regulated only if its target was
   at least 99 percent, so lowering the target to 98.8 percent removed the 1.5x build multiplier. Regulated status
   is now an explicit attribute from the regulated class, EU AI Act high-risk status (with an EU nexus), licensed
   sign-off, ICFR scope or a firm input. Regression test: tests/test_regression.py::test_target_change_never_changes_regulated_status.
   build.regulated_mult is always in the Sobol set.
2. **Function-level ICFR scope (engine).** accounting.icfr_functions over-included HR recruiting and missed
   Procure to pay. Replaced by process, step, system, integration and policy scope from the data contract
   (spec 25), with conditions decided by firm inputs and "assumed in scope" otherwise.
3. **Hard-coded wages from the May 2024 OEWS vintage (engine).** economics.role_rates and impute fallbacks used
   $133,080 (15-1252) and similar. All role wages now resolve from data/tasks/occupations.csv (OEWS May 2025) with the
   vintage recorded; tests/test_wages.py fails on any wage constant that differs.
4. **AI engineer premium (engine).** 1.3 (class d) replaced by 1 + talent.premium = 1.11 (class a, Alekseeva et al.
   2021).
5. **Survivor cost (example and engine).** The example used the placeholder C_attr; the engine used process FTE
   including outsourced work. Both now use F.survivor_base (in-house FTE on changed steps less the displaced) and
   F.survivor_cost; the announcement part is the per-wave charge O_s.
6. **Capital intensity k (engine).** The 0.02 default was far below Part I's concept; now the industry's invested
   capital per dollar of revenue on the unadjusted basis (0.574 for software; range 0.22 to 2.03).
7. **Pooled software prior (engine).** The SEC "51/54" row gave law, accounting and consulting firms a software
   prior; it now serves software codes only.
8. **Discount rate by industry (engine).** finance.r was the software WACC for every firm; it is now the industry
   cost of capital (continuous), unless the user sets it.
9. **ICFR keyword "close" (engine).** Matched "Lead to close"; replaced by the data contract's scope.
10. **Section pickling (engine).** config.Section recursed in __getattr__ when unpickled; fixed.
11. **Vendor names (engine).** Spec 26: one vendor is not named anywhere; price examples use four vendors only
    (Freshworks, Intercom, Salesforce, HubSpot; Freshworks's only usage price is per session and is not used).
    Seat and outcome defaults and the public source text were changed; tests/test_disclosure.py.

12. **Hash-seed dependence (engine).** A unit's regulated class was the most frequent class among its activities,
    with ties broken in set order, so the plan value of the small firm differed by about 1 percent between processes.
    Ties now go to the most demanding class (licensed, EU AI Act high-risk with a nexus, ICFR, other, none;
    MODEL_RISK.md Section 3); tests/test_end_to_end.py::test_golden_independent_of_hash_seed and
    tests/test_regression.py::test_regulated_class_ties_go_to_the_stricter_class.
13. **ITGC lines in the ceiling (engine).** a_min_used = a_min_fixed - (human-only minus best design) cancelled the
    plan's per-application ITGC lines; they are now added on top (prop:acct-itgc(b)).

14. **Tier 4 time studies did not reach the units (engine).** The time study set the step's hours and a tier4 flag
    in the process library, but the flag never reached the activity units, so measured steps kept the prior's
    Dirichlet dispersion in the Monte Carlo. The flag (and any measured cycle time) now reaches the units; the
    synthetic and PE goldens' value quantiles changed accordingly (CHANGELOG).
15. **Sponsor and permanent-owner growth weights used the cash margin (engine; synthesis theorist W1).** exit_weight
    and pc_growth_weight took m_cash, which nets today's growth spend; they now take m0 - k G (prop:dynamic(a)),
    and the m_cash versions are reported next to them.

## Fixed (29 Oct 2026, engine pass after the Paper 1 and Paper 2 revisions)

16. **Disruption counted twice (engine; was open item 9).** The base case no longer applies the leadership and vision
    shocks on top of the survey-based realized share and success logit: shocks.disruption_haircut is off
    (plans.py flow survival, risk.py disruption draws), as Paper 1 drops exp(-nu_D T_emb) from q. nu_D still prices the
    timing of disruptions (prop:ext-shocks) and the named scenario disruption_shocks turns the haircut on. Recalibrating
    a0 instead (round 2 Section 1.1, second branch) was rejected: with survival 0.75 at nu_D 0.23 and a 1.25-year flight,
    a product of 0.46 would need a production probability of 0.92 against the 0.48 to 0.54 the logit is calibrated to.
17. **Monte Carlo never drew the regime shocks (engine).** risk.run_monte_carlo switched shocks off on the copy of the
    parameters used to re-price the columns (so that they are not applied twice) and then passed that copy to
    outcome_draws, so the explicit draws (disruptions, reorganization freezes) never ran. The draws now read the run's
    own shock settings; reorganization freezes, which Paper 1 keeps as its clock, are now in the Monte Carlo.
18. **Central industry pass-through (engine; was open item 10).** competition.phi_ind is 0.5 (class b, range 0 to 0.7)
    when the firm gives none, Paper 2's calibration; the derived homogeneous-Cournot value (0.8 at HHI 0.25) is
    reported as a benchmark (econ.info game.cournot and the should-versus-could paragraph). Durable share at the default
    HHI: 0.625, was 0.40.
19. **ICFR retest per forced upgrade (engine; was open item 11).** accounting.C_val $100,000 -> $24,000 (10 controls x 16
    hours x $150, KPMG test effort; class b), FT-20 resolved by definition (regression suite in the run costs, change
    ticket in itgc_c_chg, control re-testing in C_val). The accounting example's invoice application line is $204,672
    and the refund agent's $74,672; a reference application at the engine's default counts $87,672, within 10 percent of
    the KPMG-anchored $80,000. The invoice line stays above the target because of its 24 changes and 4 interfaces.
20. **Accountability floor as a cost-plus-loss minimum (engine; RA-1).** formulas.amin_design minimized cost plus
    N_mm L_mm P. It is now the constrained minimum of prop:acct-amin and Part I prop:amin: a design is admissible only
    if no in-scope objective has more than an eps_bar chance a year of an undetected material misstatement, and a_min is
    the cheapest admissible design (inf if none); the consequence of a material misstatement is reported as the
    residual expected consequence, never traded against cost; errors below materiality enter as N_nm L_nm P. Default
    layer types are the papers' example (one human over one AI layer at 5 percent, one over two at 1 percent).
21. **c_err at human catch rates under full automation (engine; FI-5).** The ceiling now reports c_err at the review
    that remains (no review, the ceiling's convention; one AI layer on another provider as a sensitivity, with the
    unmeasured joint-error probability as a class d value) and the expected common-mode cost, with nu_cm = nu_out +
    (1 - q_chg) nu_reg (prop:tasks-cerr(c), ass:ext-commonmode; Part I lem:fullcost(c), (e)).
22. **Withdrawn growth weight in a default (engine; D-1).** finance.X_default 8 [5, 13] cited the withdrawn 7 to 13; it
    is now the middle evaluation point 5 [2.5, 9] (setting, not an estimate), used only when the Gordon equation has no
    root and no multiple is given. X-dependent recommendations (top lever, growth engine against overhead, the
    acquisition price rule in full, annuity and user-cost form, AI product dilution, the feature portfolio) are reported
    at finance.X_eval_points (2.5, 5, 9) or the firm's range, with sign flips flagged (lever_map x_levels).
23. **Organic growth set to ln NRR (engine; F21).** regimes.limits_check used ln NRR for every firm; it now takes the
    company's reported organic growth (ln(1 + x), labelled company-defined) or G_i = ln[1 + s(NRR - 1) + (1 - s)
    gamma_ns], reports both cases, and works in continuously compounded rates; acq_standstill reports growth plus organic
    decay. The growth-quality block gives the before-interest cash basis, the charging-convention grid and the return on
    acquisition capital (IB-4).
24. **EU AI Act dates (engine; RA-5).** Annex III high-risk status now also needs a plan that runs past 2 December 2027
    (Regulation (EU) 2026/1744); the dates are reported. MODEL_RISK.md cites SR 26-2 and OCC 2026-13 in place of SR 11-7.
25. **Server tax deductibility wording and the foreign-server case (engine; FT-3).** finance.psi_equipment's note said
    the 40 percent applied when the firm elects out; it is the 168(k)(10) transitional election, and electing out gives
    no bonus. Firm inputs bonus_election and foreign_server_share give psi from MACRS and ADS schedules; owned compute
    capital now carries the servers' psi (it carried the development psi), and the capital hurdles rise by Upsilon_K
    when psi < 1.

26. **test_tier0_only_reports_wide_ranges (test; was open item 12).** The total P10-P90 dollar spread of the Tier-0 and
    full-tier runs is not a property of data: it adds parameter and outcome risk that firm data does not remove, scales
    with the plan's value (which differs between the runs) and, at the golden settings (five parameter draws), orders
    the runs differently across seeds. The cause of the flip after the params commit was success.a0 (probabilities
    near one half, where outcome variance is largest); Tier-0 priors widen as they should (data-only spread $1.49bn
    against $0.85bn, 1.08 against 0.48 of plan value). The test now checks the data part in dollars and per dollar of
    plan value (CHANGELOG.md, engine pass).
27. **Expected realization of the reference process (calibration; was open item 9).** Calibrated, per the coordinator,
    to Paper 1: the reference process succeeds with varpi = 0.70 [0.54, 0.80], so production probability times
    success.b_bar is 0.47 [0.20, 0.68]. The failure hazard is split equally between the process factor and the activity
    factors (each 0.837, class d): success.c0 1.2 -> 2.31 [1.11, 3.11], success.a0 1.87 -> 2.12 [1.19, 3.51]
    (CHANGELOG.md, follow-up decisions).
28. **Remote threshold (was open item 11).** Central 5 percent, 1 percent the stricter sensitivity, both reported side by
    side; grounded on Audit Analytics' SOX 404 reviews (adverse 404(b) attestations 4.6 to 5.8 percent, FY2019 to
    FY2021) in accounting.eps_bar's note. Paper 1 is to move to 5 percent central (P1 editor).
29. **Paper 1 and Paper 2 copies of C_val (was open item 10).** verify_part2_accounting.py UNIT C_val $24,000; the EXA
    LEGACY keys and best_g removed; 47 of 47 checks pass. The Paper 1 editor set code/paper1_macros.py ITGC_UNITS C_val
    to $24,000, so test_regression.py::test_paper1_itgc_units_follow_engine passes.

## Open

1. **params.yaml text (data).** product.capture_share.theta_cap_default and the outcome price block in
   data/tasks/params.yaml name a vendor spec 26 excludes. The engine shows its own source text (source_public), but
   the data file should be edited by the data agent.
2. **Labor share per function outside software (data).** function_attributes.csv labor shares are software values;
   non-software people costs are flagged low confidence until industry-specific shares exist.
3. **ICFR conditions (author review).** The steps flagged in partial processes and their conditions await the SOX
   specialist's review (spec 25); Quote to contract "negotiate terms" stays out (spec 26).
4. **Bias threshold reference prevalence (theory).** prop:tasks-bias(d) needs the prevalence at which the catch rate
   was measured; the engine reports the flag with reliability.bias_prevalence_ratio = 1 (class d).
5. **Heuristic optimizer (engine).** Multi-start polishing improves the plan but does not prove optimality; an exact
   MILP is available for small firms only.
6. **Playbook gaps (engine).** iota*_p per process (spec W8), owner capability for permanent capital and the
   replace-or-transform test (W12), dependencies across processes, and the four impute-level keys in the
   one-at-a-time tier test are not computed yet (playbook.NOT_COMPUTED).
7. **AEI augmentation share (data, spec W6).** Not in activities.csv; ev_aei_augmentation_pct is empty.
8. **Step-level physical and licensed overrides (data, spec W5).** The engine reads physical_override and
   licensed_override from process_activities.csv; until the data agent adds them, finance steps such as P02.5 are
   bound by the DWA's physical share.
9. **Paper 2's invoice example (P2 owner).** data/examples/invoice_chain.json was built with success.a0 1.87 and c0 1.2;
    test_paper_examples::test_inputs_resolve_to_engine_defaults fails until code/examples/invoice_chain.py regenerates it
    with the recalibrated intercepts (item 27).
10. **AI reviewer catch rates (theory and data).** No source measures an AI reviewer's catch rate or P(the reviewing
    model also errs | the producing model errs); the AI-review sensitivity uses the human catch rates and a class d
    joint-error probability of 0.5. The ceiling uses no review.
11. **Change-control credit (data).** reliability.q_chg is 0 unless the firm reports its change controls; no source maps
    ITGC quality to the share of provider or prompt regressions stopped.
12. **Annex I systems (engine).** The activity library has no AI system that is a safety component of a product, so the
    2 August 2028 date is reported but not applied.
