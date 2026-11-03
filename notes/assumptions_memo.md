# Assumptions memo for the lead author

Assumptions auditor, 29 Oct 2026. Full register: `notes/assumptions_register.md`. Sources: `notes/data_sources_part2.md` Section 7f. Changes were made only in `code/data_part2/08_params.py` (rebuilt `data/tasks/params.yaml`; `10_validate.py` passes). The paper and the engine were read, not edited.

## 1. What changed

- Every params.yaml block now carries a spec 21.1 class (`grounding`). Before: a 72, b 15, c 12, d 109 (216 blocks). After: a 72, b 36, c 15, d 100, ref 13 (236 blocks, 20 new).
- Re-grounded with stated precedent (d to b): domain transfer, review fraction (full-review cells), F_A, T_A, outsourcing level, parallel-run lengths, U.S. severance, decision latency, reorganization freeze, change capacity, PE covenant, maintenance share, capture share.
- Inference cost per human-hour is now calibrated from METR's recorded generation costs (d to c). The frontier-tier value fell from $1.805/h to $1.27/h.
- New blocks:
  - `ai_cost.review_time_ratio_rho_rev` and `ai_cost.raw_error_rate_e` (e0, e1);
  - `organization` (span of control from OEWS; run-mode AI engineers);
  - `part1_ceiling`, which records tau, a_min, c_c, f and the calibration scenarios with their classes and threshold sensitivities;
  - reference blocks for SOX 404 costs, audit fees, the Treasury floor and Eisenhardt's latency ratio.
- No engine sensitivity results exist: QA, examples and tests are empty, and the package does not import, because `synthetic.py` imports a missing `config.load_defaults`. The influence ranking is therefore reasoned from the formulas (register Section 2).

## 2. Headline claims that rest on a class d parameter, and must be stated conditionally

**Part I**

1. **The 39% threshold and its companions** (abstract; intro.tex paragraph 11; horizons.tex line 20; model.tex Cor ceiling paragraph and tab:ceiling).
   - These are the claims that the score exceeds 100 only above about 39% market growth (31, 48 and 55% in the other cases), that the ceiling is 66 to 91 points in the central case, and that it lies between 37 and 99 points (30 to 75).
   - They rest on c_c, the compute share at full automation. c_c is class d: no setting today measures it. The bounds I could justify run from 0.01 (labor replaced at METR-observed cost) to 0.55 (AI products' 2025 cost of revenue). Over those bounds, G* runs from 23% to 68%. Over the paper's own 15 to 25% bracket, it runs from 35% to 43%.
   - f (fees) is also d, because no processor price page could be read. It moves G* by only 0.8 points.
   - Suggested wording: "if compute absorbs 20% of revenue at full automation, a scenario value, ...". In the abstract: "in a central scenario". Keep the high-compute case as a scenario, not a projection.
2. **a_min.** It is now class b, with a band of [0.005, 0.046].
   - The lower end is the direct audit and SOX 404 costs.
   - The upper end is today's leanest G&A shares in our panel: p5 4.6% for software firms with $1B to 10B of revenue, and 2.9% above $10B.
   - The central 3% equals the p10 G&A share above $10B, so it assumes no G&A automation at the leanest large firms. Say so.
   - The conservative 6% lies outside the band. Capping it at 4.6% moves the conservative threshold from 47.9% to 46.8%. Over the band, the central threshold moves from 36.9% to 40.2%.
3. **tau.** It is now class b: 21% from 26 U.S.C. 11(b) and 15% from the CAMT, both read at source.
   - State that state taxes are excluded.
   - State that GAO-23-105384 finds average effective rates of 16% (2014) to 9% (2018) for profitable large corporations. At 9%, the central threshold would be 32%.
4. **Horizon ranges** (intro: roughly 50 to 160 in 2028, 45 to 125 in 2031 and 42 to 126 in 2036, with durable parts of 32 to 82, 35 to 85 and 37 to 99; tab:calib rows 2028 to 2036).
   - They rest on the m0 paths, the G paths, mu and k, all class d, and on M0_CAP, which inherits c_c.
   - The intro already says "under our scenario assumptions". The abstract and conclusion must say the same wherever they quote these ranges.
   - The 2025 anchor row is class c, and alpha is class c.
5. **"Rule of 1000 requires 7 to 19 times the demand pull"** rests on alpha (c) and the 2025 Pi (c). No change is needed.

**Part II theory** (illustrative examples: label them so, and condition them)

6. **The prop:reg-metrics example** (theory_regimes.tex): gross IRR of 11.6% with the program against 4.9% without, and LP 7.7% against 3.0%.
   - It rests on h_x = 1 (buyers capitalize all seasoned run-rate), T_sea = 1 year, an 8% debt rate and 2% transaction costs. All four are class d.
   - The program's IRR uplift scales with h_x M_exit, and M_exit is practitioner data from a small sample. Show h_x at 0.5 and 1.
7. **The PE entry multiple.** The file's historical entry EV/EBITDA (7.6x, all industries, 1980 to 2008) must not be paired with the 2025 software exit multiple (14x) in any IRR, because that builds in multiple expansion. Use entry multiple = exit multiple as the baseline. The prop:reg-metrics example already enters at a market value, so it is unaffected. Check any other regime example.
8. **Section 15 and 16 results.** Value under shocks, vision-agnostic investment (reuse fractions), context continuity, family-firm presets and myopia weights are all class d. Quantitative statements in prop:ext-shocks, prop:ext-continuity and prop:reg-speed examples are conditional.

**Part III, engine outputs for the synthetic firm** (every number must be reported over the class d ranges, as P10 to P90 or Sobol bounds per spec 24.2, never as a point)

9. **Automation share and value.** They depend on the class d parameters below, and on the domain transfer factor (b, but 4.2 horizon doublings wide).
   - the sampled-review cells of psi_A;
   - residual_after_review;
   - the activity class multipliers;
   - kappa_O and zeta_O;
   - r_A, xi_exposure, xi_context and context coverage;
   - L_mult;
   - the success-logit coefficients and b_bar;
   - p_fail.

   Feasibility dates are conditional on the transfer factor.
10. **People plan.** The transformation-team sizes depend on e_PO, e_RG, e_SME, l_DI, l_AI and N_CM, all class d. The residual organization depends on span_ai_uplift and chi_h (both d). The span itself is now class c.
11. **Roadmap pace and the score path.** These depend on decision bandwidth Phi, congestion, the shock hazards (h_V, the keep, rescope and cancel shares), omega_par, nu_rec, redeployment, break fees and the J-curve dip (all d).
12. **Regime IRRs and the side-by-side comparison.** These depend on regime.debt_rate, h_x, the latency multipliers, budget_mult and the myopia weights (all d).
13. **Product.** Revenue at risk from seat compression rests on seat elasticity (d). Every pricing-migration cost is d.

## 3. Parameters the engine builder must update

Read-only audit: these are requests. "Link" means set `params:` in defaults.yaml to the path given.

**Links to blocks added or re-grounded by this audit**

| engine key | today | change |
|---|---|---|
| review.rho_rev | 0.8 [0.3, 1.2], assumed | link `ai_cost.review_time_ratio_rho_rev`: 0.575 [0.37, 1.19], b |
| capability.e1 | 0.01 [0.005, 0.03] | link `ai_cost.raw_error_rate_e.full_readiness_e1`: 0.033 [0.01, 0.14], b. 0.01 is below every model on the Vectara leaderboard |
| capability.e0 | 0.20 [0.10, 0.45] | link `ai_cost.raw_error_rate_e.low_readiness_e0`: 0.25 [0.10, 0.45], b |
| reliability.h_retrieval | 0.01 [0.002, 0.05] | reconcile with the Vectara rates (3.3 to 13.6%) once `params_reliability.yaml` exists |
| org.span_base | 7.0 [5, 10] | link `organization.span_of_control_oews`: 4.29 for software publishers (by_industry gives 5.26, 4.42 and 7.26 for other industries), c |
| org.e_mnt | 0.25 [0.1, 0.5] | link `organization.ai_engineers_per_automated_process_run`: 0.48 [0.29, 1.14], b. Today it is below the engine's own maintenance budget |
| security.delta_M | 0.15 [0.10, 0.30] | link `security_and_maintenance.maintenance.mu_m_share_of_F_A_per_year`: 0.17 [0.10, 0.40], b |
| product.theta_cap | 0.25 [0.1, 0.5] | link `product.capture_share.theta_cap_default`: 0.10 [0.03, 0.30], b. 0.25 exceeds every list-price-implied share (0.028 to 0.111) |
| finance.a_min_fixed | 0.03 [0.015, 0.06] | link `part1_ceiling.a_min_accountability_floor`: range [0.005, 0.046] |

**Links to blocks that already existed in params.yaml**

| engine key | today | change |
|---|---|---|
| security.T_up | 1.0, basis "vendor pages not verified" | link `security_and_maintenance.model_lifecycle.T_up_years`: 1.22, c, built from verified vendor pages |
| security.reval_share | 0.06 | harmonize with `model_lifecycle.revalidation_cost_C_reval_share_of_F_A`: 0.10 (both d) |
| security.L_inc | flag "IBM not verified" | IBM 2026 is verified in `breach_cost.global_average_usd` ($4.99M); update the flag and scale |
| security.compliance_fixed | SOC 2 $150k, ISO 42001 $100k a year | link the `compliance` blocks: SOC 2 first year $80k and $35k a year after; ISO 42001 about $13.5k audit, $30k readiness and $6k a year |
| security.finops_share, pia_cost, redteam_cost, legal_review_cost, eval_data_cost; labor.training_hours_per_fte | 0.05; $15k; $25k; $20k; $30k; 24 | params.yaml has 0.03; $10k; $30k; $15k; $20k; 20. All are d: harmonize |
| finance.r | 0.10, Part I example | link `ownership_regimes.public.r_own_wacc` (9.34%, practitioner dataset) for the public default |

**Corrections that are not links**

| engine key | today | change |
|---|---|---|
| prices.pi_h0 | value now 1.27 through the link, range still [0.54, 5.42] | the range is hard-coded from the old value. Derive it from `range_multiplier` [0.3, 3.0]: [0.38, 3.81] |
| success.a0 | calibrated to about 60% success for a reference process | recalibrate to about 50%. The surveys give 48% (Gartner, Q4 2023) to 54% (S&P Global) of projects reaching production |
| decisions.ell0_base_weeks | basis "8 weeks with three layers" | per-layer latency is now 3.3 weeks (linked), so base plus three layers gives 12 weeks (Eisenhardt's fast-firm mean). Update the basis text |
| regime.debt_rate | 0.08 [0.06, 0.11] | stays d. Record the floor: 2-year Treasury 3.80% (Fed FSR, May 2026) |
| theory preset h_x | 1 | add as an engine regime parameter with range [0, 1], class d |
| all class d keys | (n/a) | run the spec 24.2 sensitivity over the class b and d ranges, and report d-dependent outputs as conditional |

**Flowing automatically through existing links** (no edit needed; check golden outputs):

| engine key | old | new |
|---|---|---|
| prices.pi_h0 | 1.805 | 1.27 |
| decisions.ell0_weeks_per_layer | 2 [1, 4] | 3.3 [1.5, 19.7] |
| shocks.T_frz range | [0.08, 0.5] | [0.08, 1.0] |
| transition.dip_years range | [0.5, 3.0] | [0.25, 3.0] |

The assumed flag turns false for capability.transfer, build.T_A, constraints.kappa_abs, the T_par keys, severance_months_US and _UK, and regime.pe_covenant.

## 4. Open questions for the theorists

- **omega_par (core theorist).** In every precedent (payroll parallel runs, clinical silent trials) the legacy process runs at full volume during the parallel run. Engine `parallel_cost_flow` adds omega_par C_0 on top of a ramp that may already count legacy work. Decide whether full parallel means omega_par = 1, or whether that is double counting. Until then omega_par stays d.
- **Domain transfer (extension theorist).** The verified precedents span 0.5 to 9.5. Feasibility and percolation results (prop:ext-feasible, prop:tasks-breakpoints 5) should be stated as functions of the transfer factor, not at 1.
- **Part I integration theorist (spec 22).** The grounded inputs for the full-cost ceiling are in `params.yaml`:
  - `part1_ceiling`;
  - the maintenance share mu_m of 0.17 of F_A a year;
  - `model_lifecycle.T_up_years` 1.22;
  - the compliance and breach blocks.

  a_min already covers SOX, audit and D&O: do not count them again in c_sec.

## 5. Not done, and why

- f, internal-use software lives, SaaS non-cancellation terms and severance in months of each firm's own pay are unverified. The processor pages and the long 10-K and proxy pages could not be fetched.
- GDPval, which would be a second precedent for domain transfer, could not be reached.
- No precedent was found, after search, for:
  - sampled-review shares;
  - redeployment rates;
  - change-manager ratios;
  - reuse fractions;
  - seat elasticity (no filing reports seats against customer headcount);
  - leveraged-loan spread levels.

  These remain class d.
