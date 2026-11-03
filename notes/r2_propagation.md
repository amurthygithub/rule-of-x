# Paper 1 round 2 carried into Paper 2 and the engine (2 Nov 2026)
Written 2 Nov 2026 by the propagation agent. Sources: notes/r2_code_changes.md (with "Follow-up 2 Nov"), the author
decisions and lead-agent rulings in notes/reviews/paper1_v2/revision_plan_r2.md, and the checklist "Round-2 review of P1
v2 ... items to propagate" in notes/cross_paper_impacts.md. Paper 1 files (sections/*.tex, paper1/*,
code/calibrate_horizons.py, code/paper1_macros.py, code/estimate_v3*.py) were not edited. Every number below comes from
code run on 2 Nov 2026 or from the Paper 1 code and sources named.

## Checks (final)
| Check | Before | After |
|---|---|---|
| verify_part2_accounting | 47/47 | **48/48** (new 5k, break-evens; 6g and 6j updated, below) |
| verify_part2_acquirer | 82/82 | **82/82** (B6 updated, below) |
| verify_part2_core | 156/158 (23a, 23y: invoice JSON stale) | **158/158** |
| verify_part2_regimes, ext, labor, product, competition | 85, 143, 43, 94, 44 | unchanged, all pass |
| verify_part2_playbook | 36/36 | **40/40** (new R8b, L5; L1 and L4 now use the margin keep factor; decision 7: new L6, M5; C3, D4, D5, L3, M3 updated) |
| engine pytest (full, incl. slow) | 189/190 (test_inputs_resolve_to_engine_defaults) | **191/191** (one new test) |
| params.yaml rule | | calibrate_horizons.py + paper1_macros.py in two scratch copies differing only in params.yaml: paper1/macros.tex and notes/calibration_results.json byte-identical; the scratch run also reproduces the live paper1/macros.tex |
| P1-facing playbook outputs | | sections/tables/levers_position_macros.tex and tab_levers_position.tex byte-identical after the regeneration |

## 1. Pass-through (B1)
P1: phi is the industry pass-through RATE on all unit-cost savings, margins at the post-cut price; 1 - phi(1 - H) is the
share of the dollar saving a firm keeps, not a margin share. First order, a replicated saving keeps 1 - phi C0 of its
margin gain (C0 = today's non-fee unit cost per dollar of price; P1 anchor C0 = 0.60, elasticity 0.30 at phi = 0.5).

Engine
- formulas.py: new passthrough_terms (C0 = 1 - f - m0; total rate 1 - (1 - phi_ind rep)(1 - phi_extra); elasticity
  phi C0; keep factors) and margin_after_passthrough (exact m0' = 1 - f - (C0 - S)/(1 - phi S)). part1_delta_R:
  -(1 - phi)(dc_h + dc_c) - da -> -(1 - phi_e)(dc_h + dc_c + da) (overhead now exposed; phi_e the elasticity).
  lever_values: cost_of_revenue_replicable x dur c_h -> x (1 - phi C0) c_h; given demand -> x (1 - phi_extra C0) c_h.
- economics.py: info["pass_through"] (rate, C0, elasticity, keep factors) next to the dollar share durable_share.
- pipeline.frontier_shift: m0_new = m0 - (1 - phi)(dc_h + dc_c) - da -> exact post-cut-price mapping on all unit-cost
  savings; outputs phi (rate), phi_elasticity, C0, unit_cost_saving, price_cut, durable_dollar_share.
- levers.py: lever map, x_levels, cost_of_revenue_vs_overhead and the exclusion rule use 1 - phi C0 (rule cited to
  P1 prop:levers-position(d), no longer "defensive only"); outputs margin_keep_replicable, pass_through_elasticity.
- regimes.stakeholder_values: customers' share 1 - dur (1 - phi_extra) -> the rate phi on cost-of-revenue savings.
- plans.py: unchanged numerically (dur stays the dollar share of a replicated cost-of-revenue saving); comment rewritten.
- report.py, scenarios.py, defaults.yaml (finance.pass_through_phi, competition.phi_ind, phi_ind_scenarios): wording.
- Synthetic firm (quick run): rate 0.50, C0 0.488, elasticity 0.244, margin keep 0.756, against dur 0.625 before.

Paper 2 text
- theory_core prop:tasks-aggregate (a), (b), cor:tasks-weights and the proof: added the replicated case (rate on all
  unit-cost savings, Delta a included; margin at the lower price; first order 1 - phi C0; H does not enter).
- theory_regimes prop (c): same replacement term for the replicated case.
- theory_competition cor:ext-game-engine(a): dur stated as a dollar-profit share, not a margin share; the calibration
  paragraph's "a lower pass-through raises every durable share and so weakly raises the rank of cost-of-revenue
  automation" -> the rank moves through the margin share 1 - phi u/p, not through dur.
- theory_playbook prop:playbook-rank(a): "x(1 - phi)c_h at given demand, and x dur c_h ... when every rival replicates"
  -> x(1 - phi)c_h with phi = phi_ind C0 for a replicated saving; dur values bundles in dollars only. (d): "dur >
  a_GA/c_h" (and the linear-demand dur formulas) -> (1 - phi)c_h > a_GA (P1 prop:levers-position(d)); example 0.70 at
  phi = 0.5 and C0 = 0.60. Intuition sentence, setup-table row, results paragraph ("durable share 0.62 ... can only raise
  that lever's rank" -> keep factor \pbKeepMin-\pbKeepMax = 0.62-0.73 at rate 0.50), Limits ("scenario concentration" ->
  "scenario pass-through rate"); proofs_playbook cost-of-revenue paragraph.
- Demirer et al.: P2 text never claimed pass-through near one (its two Demirer passages already describe the -1.1
  figure as cross-provider substitution); nothing to remove in P2.

Paper 2 code
- code/playbook/levers.py: cor = PROP dur c_h -> PROP keep c_h (keep from the engine's econ info, so the engine's lever
  map and the table agree; verify L4). run_archetypes.py stores keep and pass_through per configuration, writes macros
  pbKeepMin/Max (0.62/0.73), pbPtElasMin/Max (0.27/0.38), pbPtRate (0.50); "levers to avoid" text "(dur 0.62)" ->
  "(keeps 0.66 of the cut)" etc.; table notes rewritten.
- verify_part2_playbook: L1 uses keep and checks keep = 1 - phi C0; L4 passes keep; R8 relabelled as the dollar share;
  new R8b (symbolic: d/dS of the post-cut margin at 0 is 1 - phi C0).
- Effect on the playbook: cost-of-revenue lever values rise by about 0.1 point per 10% (e.g. A1 public 1.1 -> 1.2);
  no ranking changes (pbNCoRTopTwo still none; every count macro of the rankings unchanged).

params.yaml (pass_through.industry_pass_through_scenarios)
- Removed anchor identical_inference ("near 1", Demirer et al.); the note now says the -1.1 figure is cross-provider
  substitution, not pass-through.
- unit: "phi of a variable-cost saving (c_h and c_c); non-discretionary cost a is not passed through" -> a rate applied
  to every unit-cost saving with margins at the post-cut price; note: dur is the dollar share, not used in the score.

## 2. Compute-share value test (B2)
- params.yaml part1_ceiling.c_c_compute_share.high_compute_case: feasible_at_full_automation false -> true, cap 0.30 ->
  value_test_cap 0.60, note rewritten (G* 61.3%; range 28-78%; old cap gives 52.8%, all P1 macros).
- params.yaml path.sources: "kappa < 1 - review share" -> "kappa < 1, so c_c <= s_L" with the reason.
- Engine and P2: no occurrence of the 0.5 factor, the 0.30 cap, "infeasible" or 27-51% (engine
  finance.c_c_full_automation keeps its credible range [0.01, 0.30], the by-horizon scenario bounds P1 keeps).

## 3. Error-loss base and transition cost (B4)
- Checked P2 (theory_core eq:tasks-cerr, theory_ext common mode, all .tex), the engine (security.ceiling_terms c_err is
  bottom-up from the plan's automated processes; no 30% base) and params.yaml/params_reliability.yaml: no 30% error-loss
  base and no "two years" of transition cost anywhere. params.yaml change_capacity.embedding_time_T_emb_years is already
  1.25 [1, 2] (T_emb = T_pb). No change.

## 4. varpi label (B9)
- part2/theory_core.tex ass:tasks-transition(iv): "the new mode works" -> "the new mode works, that is, the attempt
  creates some value"; invoice example: added that the engine calibrates the reference process to create some value in
  70% of attempts (P1's varpi, not a success rate), with the yield varpi x b_bar = 0.47 (P1 YieldModel).
- engine defaults success.a0 and success.c0: "succeeds with probability varpi = 0.70" -> "creates some value with
  probability 0.70 ... not a success rate; target varpi x b_bar = 0.47". report.py: a wave's "mean success probability"
  -> "mean probability that an attempt creates some value".
- params.yaml project_outcomes...varpi unit: "probability that a funded transition creates value" -> "share of funded
  attempts that create some value (not a success rate)"; note adds the 0.47 target.

## 5. Accountability floor (C1-C3, C6)
Engine
- eps_bar: "Central 5 percent, 1 percent a stricter sensitivity" -> no central value; floors reported at 1% and 5%
  (by_eps_bar now in the order 1%, 5%, with break-evens and the human-only design); the key only selects the
  single-number ceiling's design (eps_bar_note). Grounding stays "policy" so the Monte Carlo does not draw a pass/fail
  threshold. MODEL_RISK.md "5 percent by default, 1 percent also shown" rewritten.
- Direct cost C_acct: S&P 500 ratio x S + SEC 2009 median $1.04M -> KPMG 2025 SOX budget by revenue class (under $5bn
  $1.5M, $5-25bn $2.7M, above $4.7M; accounting.sox_program_by_size) + accelerated-filer audit fee $1,492,375
  (accounting.audit_fee); low bound S&P 500 ratio (audit_fee_per_musd, kept as low bound), high case large-accelerated
  $5,327,646 (audit_fee_high). sox404_median removed. New formulas.amin_direct_cost. At $1bn: 0.14% -> 0.30% (low 0.18%,
  high 0.68%), equal to P1 (notes/amin_r2.json direct, direct_lo, direct_hi).
- Design ITGC line: C_itgc $50,000 [20k, 150k] -> $185,000 [16k, 330k], so C_itgc + C_val/T_up = $69,672 -> $204,672 =
  P1 ITGC_LINE_DESIGN and P2 acctAminLine. At $1bn: 1H+1AI $754,672 (5%), 1H+2AI $804,672 (1%), as P1.
- Break-evens: new formulas.amin_breakevens on every chosen and human-only design: p_cc (P1 0.00084 for 1H+1AI at 5%;
  0.00014 for 1H+2AI at 1%) and the human miss rate on AI-missed items (P1 8.4%), reproduced exactly
  (tests/test_formulas.py::test_amin_direct_cost_and_breakevens_follow_paper1).
- report.py floor paragraph rewritten (both thresholds, no central value, break-evens, direct-cost basis).
Paper 2
- verify_part2_accounting.py 6j: AUD_404 0.138% -> DIRECT 0.299% (KPMG + AA; low 0.184%); floor 0.22% (1% only) -> 0.37%
  at 5% and 0.38% at 1%; applications to the band's 0.5%: 15 -> 8 (5%) and 7 (1%), 13 with the low fee; with fallback
  9 -> 4 (5%). These equal P1's AminFloor, AminFloorOne, ItgcApps, ItgcAppsOne, ItgcAppsLo, ItgcAppsFb.
  Macros acctItgcFloorZero, acctItgcBandN, acctItgcBandNfb replaced by acctItgcFloorFive/One, acctItgcBandNFive/One/Lo,
  acctItgcBandNfbFive, acctAminDirect(Lo/Old), acctAminKpmgSmall, acctAminAuditFee.
- New check 5k and macros acctAminPccFive 0.00084, acctAminPccOne 0.00014, acctAminPhmFive 8.4%; theory_accounting.tex
  example now states the designs are conditional and gives these break-evens; "Neither threshold is a central value".
- theory_accounting.tex band sentence rewritten with the new direct cost and citations kpmg2025sox, auditanalytics2023fees.
- part2/refs_accounting.bib: kpmg2025sox replaced by P1's entry (archived URL, size values, label); auditanalytics2023fees
  added (P1's entry verbatim).
- The P2 example's design costs already used the $205k invoice line ($755k / $805k): no change.
params.yaml
- compliance.sox_program_cost_kpmg_2025_reference.by_revenue_size added (archived URL, label); new
  compliance.audit_fee_accelerated_filer_reference ($1,492,375; large accelerated $5,327,646); audit_fee_per_musd
  reference marked as the low bound; sox404 reference marked superseded; part1_ceiling.a_min_accountability_floor source
  text updated (value and band unchanged).

## 6. S&M basis (decision 4; superseded by decision 7, see the last section)
- Engine: levers.state and impute.part1_baseline count all S&M (+ theta R&D) as growth spend. Not switched: the
  playbook and P1's levers section (sections/levers_by_position.tex, "Growth spend is the selling-and-marketing share")
  use the same convention, and P1's CLAIMS check asserts lpGEFirstAll = yes. Added finance.sm_maint_base 0.2506
  [0.2326, 0.2757] (c; P1 MaintBase, notes/empirics_v3.json) and levers.sm_basis_bounds, reported in the lever map and
  the report (all S&M stated as an upper bound; ranking at the revealed weight on all three bases).
- Playbook: new archetypes.sm_basis_check, stored as playbook_results.json sm_basis_check and as P2 macros; new verify L5.
  **Re-check of "growth engine ahead of G&A at all 6 positions" (at the weight each position's spending reveals, test
  sigma > a_GA):**
  | Basis | positions where the growth engine outranks G&A |
  |---|---|
  | all S&M (tables, P1 Table tab:levers-position) | 6 of 6 (ratios 0.51-0.81), unchanged |
  | maintenance-netted, sigma = max(S&M - 25.1%, 0) (P1 central) | **1 of 6: A1 only** (ratio 0.97); A4 1.05, A5 2.23, A2 3.94; A3 and A6 have no S&M above the base |
  | no S&M | 0 of 6 |
  Automating a share of all S&M (growth part plus the maintenance share as a cost line) still outranks G&A at 6 of 6.
- P2 text: theory_playbook Limits rewritten (all S&M is an upper bound; P1's central basis nets out the 25.1% maintenance
  base; the netted re-check with macros pbNGEAheadGANet = one, pbGEAheadNetList = A1, pbSMNetZeroList = A3, A6,
  pbNSMAutoAheadGA = six); the "four readings" paragraph says it is on the all-S&M basis.
- Not resolved (decision needed): whether P1's levers section and the playbook move to the netted basis. Doing so flips
  the headline at 5 of 6 positions and would fail P1's CLAIMS check (lpGEFirstAll) and change P1's Table
  tab:levers-position, so it is P1's call.

## 7. Bending Spoons (D3)
- part2/tables/acquirer_macros.tex and sections/tables/acquired_macros.tex: regenerated by verify_part2_acquirer.py
  (script unchanged). Note: sections/tables/acquired_macros.tex had been overwritten at 11:28:58 by a run without the D3
  macros (acqChPaid*, acqRunRate*, acqIntPaidSh*, acqCouponMarg, acqNotesCoupon, acqUnpricedDebt) that the P1 text uses;
  the current script writes them back.
- theory_acquirer.tex, case table: "Margins and interest, 2025" adds interest paid ($130.9M, 10.0%) beside interest
  expense; "Debt policy" adds the 28 July SACE-guaranteed EUR 500M loan, EUR 495M term loan A and EUR 490M revolver
  increase, the 2 October term loan B add-ons, the notes as priced by two subsidiaries that the company does not issue or
  guarantee (P1 wording), their stated use, and run-rate interest $572M = 20.3% of Q2 revenue annualized (27.9% if the
  new term loans carry the notes' coupon), as P1's supplement.
- Grounding of r_debt: "the company's first senior secured notes" -> "the senior secured notes that two of its
  subsidiaries priced on 28 October 2026 ... the company does not issue or guarantee them".
- "What the case is consistent with": adds that the post-Q2 loans and notes add to the interest behind the after-interest
  scores and that the notes' stated use shows continued reliance on acquisition capital (P1 wording).

## 8. Authorship and declarations
- New part2/declarations.tex: \PtwoAuthorship and \PtwoDeclarations, verbatim, for the P2 main file's title footnote
  (P2 has no main file yet; regenerate_all.sh stage latex_p2 still stops there).
- engine/README.md: new section "Authorship and declarations"; engine/MODEL_RISK.md: same two statements after "Every
  report is decision support".

## 9. Pending P2 items
- Invoice example regenerated (code/examples/invoice_chain.py, after the last defaults.yaml edit): varpi_p 0.62 -> 0.82;
  T*_par 0.15 -> 0.00 years (the floor of 0.25 still binds); residual undetected-failure risk 14% -> 7%; NPV -$3.76M ->
  -$3.78M; with savings forever -$4.30M -> -$4.49M; program -$4.06M -> -$4.17M; break-even build -$952k -> -$970k;
  engine horizon -$3.98M -> -$4.07M; 5-year -$3.81M -> -$3.84M. Fixes core 23a/23y and the engine test
  test_inputs_resolve_to_engine_defaults.
  Downstream, legitimately moved values, checks updated (not loosened):
  - verify_part2_accounting 6g: the ITGC line lowers the invoice NPV by $0.40M -> $0.52M (= varpi_p x line x annuity);
    acctItgcNPVafter -$4.16M -> -$4.30M.
  - verify_part2_acquirer B6: at an unlimited horizon the floor is now positive at the firm's varpi (0.82 > break-even
    0.73): acqIcFloorInf -$156k -> +$141k (macro made sign-aware); acqIcFloorFour -$694k -> -$570k. The check now asserts
    the sign follows varpi against the break-even. theory_acquirer.tex example sentence rewritten accordingly (the
    success break-even is no longer a remaining condition; platform scale, reuse and horizon are).
- theory_accounting.tex: dropped "The engine's illustrative \acctItgcValEng{} a retest, ... gives \acctItgcInvEng." and
  the three parentheticals that restated the same values at "the engine's retest" (acctItgcAppEng, acctItgcNPVEng,
  acctItgcRefEng; engine C_val = KPMG value, so they were identical).
- verify_part2_accounting.py line 155: docstring made raw (r"""...""") - no SyntaxWarning in any P2 script.

## Playbook regeneration: what moved and why
Full run of code/playbook/run_archetypes.py (--jobs 4, 3 to 4 minutes) in the repository. To separate my changes from
stale outputs, the playbook was also run in a scratch copy with the engine, code/playbook and params.yaml as they were
before this pass.
- Stale before this pass (moved by the engine's success recalibration of 29 Oct, which the committed playbook results of
  29 Oct 18:05 predate): engine program values in Table tab:playbook-grid (e.g. A1 public 3,549 / 3,584 -> 4,269 / 4,310),
  first-wave processes and NPVs in Table tab:playbook, tier shares pbTierStepA 50 -> 51, pbTierUnitA 54 -> 55,
  pbTierUnitC 34 -> 33.
- From this pass: the cost-of-revenue lever values (about +0.1 point per 10%, e.g. A1 1.1 -> 1.2), the "levers to avoid"
  wording, the table notes, and the new macros (pbKeepMin/Max, pbPtElasMin/Max, pbPtRate, pbMaintBase, pbSpendRatioNet,
  pbNGEAheadGAAll/Net/None, pbGEAheadNetList, pbSMNetZeroList, pbNSMAutoAheadGA).
- Unchanged: every ranking count (pbNGEThenEng, pbNGEFirst*, pbNCoRTopTwo none, X_dagger ranges), and Paper 1's
  sections/tables/levers_position_macros.tex and tab_levers_position.tex (byte-identical; lpGEFirstAll yes, ratios
  0.51-0.81). **The ranking "growth engine ahead of G&A at all 6 positions" holds on the all-S&M basis the tables use;
  on the maintenance-netted basis it holds at 1 of 6 (item 6).**

## Engine example report (engine/examples/synthetic_run/report, full settings, seed 20261029)
Plan value, Monte Carlo quantiles, probability of loss and processes unchanged ($2,087.4M planning case; 24 items).
Part I mapping: pass-through 0.375 (old 1 - dur) -> rate 0.50 on all unit-cost savings; first-order change in the Rule
of 40 score 6.4 -> 5.2 points; R* after the plan 59.0% -> 58.0%. a_min used unchanged (0.03; the synthetic firm's plan
automates no ICFR process, so only human designs are allowed: three human layers at 5%, none at 1%).

## P2 assembly check
Fresh test assembly (the 29 Oct assembly file, live part2/ and sections/, Paper 1 labels from the build of 12:15 today):
241 pages, no LaTeX errors, no undefined references or citations.

## Regenerated outputs
data/examples/invoice_chain.json, part2/tables/{invoice,accounting,acquirer,playbook}_macros.tex,
part2/tables/playbook_{table,grid,functions,processes,steps_full,archetypes}.tex, notes/playbook_results.json,
data/playbook/*.csv, engine/TRACEABILITY.md, engine/examples/synthetic_run/report/*, sections/tables/acquired_macros.tex
(generated; see item 7).

## S&M basis (decision 7)
Author decision of 2 Nov 2026 (about 12:35 UTC-8, coordinator message): maintenance-netted is central everywhere
(levers and playbook), matching P1's 2036 path; all S&M and no S&M are bounds. Growth spend
sigma = max(S&M - b_M, 0) (+ theta R&D in the engine's Part I state), b_M = 0.25056806 (P1 MaintBase 25.1,
notes/empirics_v3.json spend_maint_base E1); maintenance S&M min(S&M, b_M) is a cost line in a; spend ratio
r_sigma = 0.98754 (spend_maint_ratio E1, P1 AlphaNet 0.99); the all-S&M ratio 3.3 is the bound.

### Code
- Engine: formulas.growth_spend_split; impute.part1_baseline and levers.state on finance.sm_basis = netted (new setting;
  "all", "none" bounds); finance.spend_ratio_netted 0.98754 [0.6705, 1.1403] (c); sm_maint_base at full precision;
  ell = 0 / Delta = 0 / G_i = g and infinite switch weights when sigma = 0; pipeline.frontier_shift splits S&M savings
  (delta_a_SM_maint); report states basis and bounds. README, MODEL_RISK (Sections 3 and 4) and CHANGELOG updated.
- Playbook (code/playbook): archetypes.state(basis="netted"), BASES, growth_spend, spend_ratio, sm_basis_check;
  levers.lever_values with a_SM; run_archetypes: netted calibration in every configuration, ranking_by_basis (four
  levers at the revealed weight on each basis), compounder netted, table notes and grid notes on the netted basis
  (rate, durable share and the basis bounds interpolated; X_dagger_0 shown as infinity where sigma = 0), P1 table with
  columns "First at own weight: central / all S&M" and a notes line for the no-S&M bound.
- verify_part2_playbook: C3 (X_hat - k in [2.2, 4.0] netted, [7.3, 13.2] all S&M), D4, D5, L3, M3 updated to the
  netted values (legitimate moves); new L6 (four-lever ranking by basis recomputed from cell medians) and M5 (the
  decision-7 text macros, the A1/A4 growth spend against overhead, the gap reading, the family switch).

### What changed in the playbook's conclusions (at the public owner's weight = the revealed weight)
| | before (all S&M) | after (netted, central) |
|---|---|---|
| First two levers | A1-A5 growth engine, R&D; A6 R&D, growth engine | A1 R&D 3.2, growth engine 2.5; A2-A6 R&D, G&A |
| Growth engine ahead of G&A | 6 of 6 | **1 of 6 (A1: sigma 24.6% vs G&A 23.7%)**; A4 17.9% vs 19.1%; A3, A6 no S&M above the base |
| Four-lever first: growth engine / engineering / G&A | 5 / 1 / 0 | **0 / 6 / 0** (bounds: all S&M 5 / 1 / 0; no S&M 0 / 6 / 0) |
| Growth engine first by owner | public 5, family 6, dual class 6, PE 1, VC 1, PC 0 of 5 | public 0, family 1 (A1), dual class 0, PE 0, VC 0, PC 0 of 5 |
| Maintenance S&M line above G&A | n.a. | 6 of 6; automating a share of all S&M still outranks G&A at 6 of 6 |
| Cost-of-revenue keep factor 1 - phi C0 | 0.62-0.73 | 0.49-0.63 (m0 is net of maintenance S&M, so C0 is larger); among first two: none (unchanged) |
| Compounder (A7) | X^G 1.14, AOL -1.16 | X^G 0.77, AOL -1.53 (its S&M is below the base) |
| First waves, binding constraints, step decisions, tiers, function and process tables | | **unchanged** (playbook_steps.csv, playbook_functions.tex, playbook_processes.tex byte-identical; the waves are the engine's plan, which does not use the Part I state) |
| Engine regime program values (grid) | | A3 VC 509.3 -> 635.5 $M (low), A4 VC 757.6 -> 667.9, A5 VC 70.8 -> 74.0; other regime values unchanged |

### P2 text (part2/theory_playbook.tex, proofs_playbook.tex)
- Definition of a position (a_SM added); Assumption ass:playbook-calib (netted sigma with b_M, a_SM, r_sigma =
  \SpendRatioPB with \SpendRatioPBAll as the all-S&M ratio, ell = 0 when sigma = 0); the restriction paragraph (the
  ratio depends on basis and method, replacing "robust across Part I's methods", which contradicted P1 Section 5.4);
  proof of lem:playbook-calib (sigma = 0 case; interval [2.2, 4.0] netted, [7.3, 13.2] all S&M).
- Section intro, first conclusion restated as basis-dependent: "cutting general and administrative cost comes first at
  five of the six panel positions, and automating the growth engine leads only where selling and marketing is well
  above that level (engineering, valued as if all R&D were maintenance, ranks above both)"; the cost-of-revenue
  conclusion now uses the keep factor (the old "in proportion to the durable share ... small in fragmented markets"
  contradicted the round-2 mapping and the third reading).
- Archetype paragraph (growth corner: S&M 50%, 25 points above the base; elite G_i = g).
- Readings: now five. (1) the lead finding by basis, with the A1/A4 numbers and the bounds; (2) the owner moves the
  ranking only where there is growth spend (family at A1; sponsor, VC, PC none); (3) the gap and the lever values
  point to the same line for A3, A5 (R&D), with the caveats; (4) owned compute and cost of revenue (unchanged);
  (5) bandwidth (unchanged).
- Limits: netted central with all-S&M and no-S&M bounds and their counts; maintenance S&M above G&A at six positions.
- Assembly: fresh test assembly with P1 labels from the 13:26 scratch build (main + supplement): 242 pages, no errors,
  no undefined references or citations.

### P1 generated files (sections/tables/, not P1 prose)
tab_levers_position.tex: columns S&M, sigma-hat (netted), G&A, k, ratio, First at own weight (central, all S&M),
g + delta; no X-hat or G_i column; "--" for no growth spend; notes give the base as P1 defines it (median S&M share, in
the previous year, of firm-years growing at or below the year's median) and the no-S&M bound. Scratch build of P1
(NO_COPY, 13:26): clean, 81 + 53 pages; the table fits the page (no overfull box; page 63).

Macros in sections/tables/levers_position_macros.tex (new or changed; for the CLAIMS check and the editor):
| macro | before | now |
|---|---|---|
| lpGEFirstAll | yes | **no** (P1's CLAIMS check in code/paper1_macros.py asserts yes: fails until the P1 coder updates it) |
| lpRatio | 3.3 | 0.99 |
| lpRatioMin / lpRatioMax | 0.51 / 0.81 | 0.97 / 3.94 (finite positions; P1 text "below one at each" is now false) |
| lpXdagMin / lpXdagMax / lpXhat (withdrawn, kept defined) | 5.7 / 9.1 / 11 | 3.3 / 13.1 / 3 |
| new: lpBasis | | maintenance-netted |
| new: lpGEFirstAllSM, lpNGEFirstAllSM | | yes, 6 |
| new: lpNGEFirstNet, lpGEFirstNetList, lpNGACutFirstNet | | 1, Growth corner, 5 |
| new: lpNGEFirstNoSM | | 0 |
| new: lpNNoGrowthSpend, lpNoGrowthSpendList | | 2, Mature cash generator, Near-frontier elite |
| new: lpRatioAllSMMin / lpRatioAllSMMax | | 0.51 / 0.81 |
| new: lpMaintBase, lpNPositions | | 25.1, 6 |
Unchanged: lpAFivecaph 0.27, lpASixcaph 0.61, lpScreenBelowAll yes.

P2 macros (part2/tables/playbook_macros.tex). Changed: SpendRatioPB 3.3 -> 0.99; pbNGEFirstPub (= pbNGEFirstRevealed)
five -> none; pbNGEThenEng five -> none; pbNGEFirstFam six -> one; pbNGEFirstHyb six -> none; pbNGEFirstPE one -> none;
pbNGEFirstVC one -> none; pbKeepMin/Max 0.62/0.73 -> 0.49/0.63; pbPtElasMin/Max 0.27/0.38 -> 0.37/0.51; pbAFiveGi -7.4
-> -4.2; pbASixGi 30.3 -> 36.3 (= g); pbASixXhat 11.0 -> 3.3; pbASixXPE 15.0 -> 11.3; pbASixXVC 13.5 -> 17.6;
pbASevenXpc 1.14 -> 0.77; pbASevenAOL -1.16 -> -1.53; pbXhatMin/Max 11.0/12.2 -> 3.3/4.5; pbXdagMin/Max 5.7/9.1 ->
3.3/13.1 (finite positions); pbXFamMin/Max 14.3/16.8 -> 4.3/22.4; pbXPEMin/Max 1.5/15.0 -> -0.1/11.3; pbXVCMin/Max
1.5/13.5 -> 0.9/17.6; pbXPCMin/Max 1.0/4.3 -> 0.1/5.4. New: SpendRatioPBAll 3.3; pbNGEFirstRev{Net,All,None}
none/five/none; pbNEngFirstRev{Net,All,None} six/one/six; pbNGAFirstRev{Net,All,None} none; pbNGAAheadGENet five;
pbNSMMaintAboveGA six; pbAOneSigma 25; pbAOneGA 24; pbAFourSigma 18; pbAFourGA 19; pbGEFirstFamList A1. Unchanged from
the decision-4 pass: pbMaintBase 25.1, pbSpendRatioNet 0.99, pbNGEAheadGA{All,Net,None} six/one/none, pbGEAheadNetList
A1, pbSMNetZeroList A3, A6, pbNSMAutoAheadGA six.

### Checks after decision 7
verify_part2: accounting 48/48, acquirer 82/82, regimes 85/85, core 158/158, ext 143/143, labor 43/43, product 94/94,
competition 44/44, playbook 40/40. Engine pytest 191/191 (golden snapshots unchanged: they pin plan, Monte Carlo,
regime program values and FTE, which do not use the Part I state). TRACEABILITY.md, data/examples/invoice_chain.json
(sha256 of defaults.yaml and params.yaml; its macros unchanged) and engine/examples/synthetic_run/report regenerated
(synthetic firm: growth spend 38.4% -> 13.3%, X_hat 18.9 -> 6.9, C0 0.49 -> 0.74, keep 0.76 -> 0.63, other opex saving
-5.29% -> -8.71% with maintenance S&M -3.42%). sections/tables/acquired_macros.tex rewritten by verify_part2_acquirer
at 13:36 and holds the D3 macros (acqRunRateShQ 20.3%, acqRunRateShQHi 27.9%, acqChPaidLo 86.6).

### Open
- P1 prose (editor): sections/levers_by_position.tex still says growth spend is the S&M share and that every position
  ranks the growth engine ahead of G&A with the ratio "below one at each"; summary box and conclusion likewise.
- P1 CLAIMS check (coder): lpGEFirstAll is now no; lpGEFirstAllSM = yes and lpNGEFirstNet = 1 carry the two bases.
- data/tasks/params.yaml was changed at 12:20 by another agent (finance alpha: grounding c -> d, quality assumed); the
  engine keeps finance.alpha at class c with a note (drawing it in the Monte Carlo would reshuffle every later draw):
  engine owner's decision.
- The Docs artifact and Word export of the playbook (cross_paper_impacts.md, decision 7) still carry the all-S&M
  playbook; they need the regenerated numbers above.
