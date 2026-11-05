# Playbook notes: derivations, cell-to-label map, grounding, open items

Owner: synthesis theorist (AI). Files: `part2/theory_playbook.tex` (sec:playbook), `part2/proofs_playbook.tex`
(app:proofs-playbook, app:playbook-tables), `sections/levers_by_position.tex` (Paper 1, sec:levers-position),
`code/playbook/{archetypes,levers,steps,run_archetypes}.py`, `code/verify_part2_playbook.py`,
`notes/playbook_engine_spec.md` (engine spec), outputs listed in Section 7. Every number in the three .tex files is a
macro written by `run_archetypes.py` (`part2/tables/playbook_macros.tex`, `sections/tables/levers_position_macros.tex`)
or a value checked by `verify_part2_playbook.py`; numbers quoted below are from the run of 29 Oct 2026 and are for
orientation only (the generated files are authoritative).

## 1. Derivations

### 1.1 Calibration of a position (ass:playbook-calib, lem:playbook-calib)
- sigma = S&M / revenue (Paper 1's growth spend, sections/data.tex); k = (capex + capitalized software)/revenue / g for
  g > 0, else 0 (Paper 1 anchor convention). For small g this k is large (A5: g = 2.1%, k = 1.15); it is the
  convention's arithmetic, kept because Paper 1 uses it, and it moves X_dagger_0 one for one (A5's 8.9).
- One net weight for all firms (Paper 1 ass:hetero): alpha (X_hat - k) = r_sigma = 3.3, Paper 1's median ratio of
  prior-year S&M share to excess growth (sections/empirics.tex, organic above-median growers; class c).
- Delta = sigma / r_sigma, G_i = g - Delta, ell = Delta / sigma^alpha. Then sigma*(ell, X_hat) = (alpha ell (X_hat-k))^(1/(1-alpha))
  = (ell r_sigma)^(1/(1-alpha)) = (sigma^(1-alpha))^(1/(1-alpha)) = sigma. For another weight X_o, sigma* scales with
  ((X_o - k)/(X_hat - k))^(1/(1-alpha)).
- alpha = 0.3 in the engine runs (engine default finance.alpha) and in Paper 1's table.

### 1.2 Lever values (prop:playbook-rank(a)); proofs in app:proofs-playbook
- Closed forms: sigma* = (alpha ell y)^e, Delta* = ell^e (alpha y)^(alpha e), Pi = C_alpha (ell y)^e, y = X - k, e = 1/(1-alpha).
- Growth automation (share x of growth-activity cost): lambda -> lambda (1-x)^(-alpha) (prop:tasks-aggregate(a));
  dR = x sigma* to first order, Pi[(1-x)^(-alpha e) - 1] exactly (>= first order by convexity).
- Demand pull +x: x sigma*/alpha (cor:priorities(ii)); exact Pi[(1+x)^e - 1].
- Overhead, engineering: x a, exact (R* affine in m0). Engineering uses all R&D (runner override
  finance.rd_expansion_share = 0), an upper bound on maintenance R&D.
- Cost of revenue: x (1 - phi) c_h at given demand; x dur c_h when rivals replicate (cor:ext-game-engine(a)); engine
  default HHI 0.25 gives dur = 2H/(1+H) = 0.40.
- Retention: (X - k) dG exactly, for any X (R* linear in G_i; negative if X < k).
- Capital: dR*/dk = -(g* + delta_K) with replacement (Remark rem:assumptions(c)); delta_K = 0.25 (engine
  capital.delta_K_compute, Paper 1 cor:capital intuition).
- Product: (X - k) dG - D_m exactly (cor:prod-dilution(i)).
- Acquisition: R^A = R^org + (X - k^acq) g^acq (prop:acquired-score(a)).

### 1.3 Switch thresholds (prop:playbook-rank(b)-(d))
- X_dagger_0 = k + a^(1-alpha)/(alpha ell): x sigma* > x a iff alpha ell y > a^(1-alpha). Under the calibration
  alpha ell = sigma^(1-alpha)/(X_hat - k), so the condition is (X_o - k)/(X_hat - k) > (a/sigma)^(1-alpha): data
  identify it without lambda or h separately.
- Demand-pull version: k + (alpha a)^(1-alpha)/(alpha ell).
- X_dagger_0 is the delta_sigma -> 0 limit of the exact X_dagger of eq:reg-Xdag with da = delta_sigma a
  (phi(d)/d -> alpha e and C_alpha alpha e = alpha^e).
- Headroom: sigma* is proportional to h^e, so a line a overtakes the growth engine at h_dagger = h (a/sigma*)^(1-alpha).
- Cost of revenue vs overhead: dur > a_GA / c_h (replicable), 1 - phi > a_GA / c_h (private).
- Screening reversal: if X^scr < X_dagger_0 < X_o the two weights rank differently.

### 1.4 Owner weights (runner, `levers.regime_weights`)
- Public: the revealed weight X_hat. Reason: the panel is public filers, so their spending reveals a public owner's
  net weight under the earnings pressure, X^my of eq:reg-Xmy. This replaces draft 1, which applied the pressure to
  X_hat (double counting). The engine now reads Tier 0 `multiple_is_net_of_pressure = 1` (W14) and gives the same
  public weight.
- Going concern without pressure: X_gc = k + (1 + w_pub)(X_hat - k), w_pub = 0.3 (engine preset).
- Dual class: X^my of X_gc at w = 0.15. Family: X_gc v0(r_fam)/v0(r_w) when the Gordon root exists at both rates; at
  the archetype states it does not (v0 None), so family = X_gc, a lower bound (prop:reg-weight(a)).
- Sponsor: eq:reg-Xexit at entry (tau = 6), r = pe_irr_target (continuous 19.9%), m_hat = m0 - k G_i, X_T = h_x M_exit
  m_hat^E with m_hat^E = m0 (the marginal EBITDA margin of a permanent dollar without growth spend; capital spending
  is not an EBITDA item). G is not capped at r: the formula holds for any finite horizon (limit m tau + X_T at r = G).
- VC: eq:reg-Xexit at 7 years, r = vc_r, X_T = vc_revenue_multiple (class d).
- Permanent acquirer: X^G = m_hat/(i_U - G_i), i_U = ln 1.25 (prop:acq-pc(d)); undefined if G_i >= i_U (A6).
- A6 (elite): calibrated G_i = 32.9% exceeds the sponsor's and the VC's rates, so their finite-horizon weights (17.0,
  15.7) exceed X_hat (11.0) and the growth engine stays first; this is conditional on the class-c G_i.
- m0 (and so m_hat) comes from Part I's identity m0 = m + sigma + k g at the cell's median FCF-after-SBC margin. The
  cell's median cost lines do not sum to the median margin; the runner passes `fcf_margin` (engine W17), so the
  engine's m0 equals the runner's and the line gap sits in the engine's a_other. The engine's sponsor and acquirer
  weights then equal the runner's; its VC weight uses its own exit rule and its family weight differs for A5.

### 1.5 Binding constraint (table column)
- Position: cost line with the largest gap of the cell's median to the top decile of GAAP operating margin in its
  growth band (Paper 1 tab:gap; notes/gap_decomposition.json bands). Descriptive, not a lever (sections/empirics.tex).
- Setup: the engine's most used capacity in the first plan year (`utilization`): decision bandwidth for all six
  archetypes (load 1.10 to 1.19 times the breakpoint; prop:ext-bandwidth(b)).

### 1.6 Step-level binding order (prop:playbook-gates; runner `steps.unit_decisions`)
none (A optimal), permissibility, feasibility: physical, feasibility: capability horizon, readiness, reliability:
detection, reliability: residual/appetite, volume threshold, cost. Evaluated at (level 0, 2026) for "now" and
(highest level, 2026) for "target". The engine (playbook.build, v1.0) implements the same order; the runner and the
engine agree on every activity decision and binding category (verify P5b). The engine's v0.2 rows evaluated the
binding at the plan's level and start year; superseded.

### 1.7 Confidence tier (def:playbook-tier; coordinator's rule)
- C: the automation decision (A or not) or the AI decision (U, A, N vs H, O) changes at an end of the stated range of
  some class-d key, others at defaults (one at a time; `steps.flip_params`, economics rebuilt per key, the four
  impute-level keys rebuild the firm), or the engine's Monte Carlo share of draws with positive process value is
  below 0.8 (`ROBUST_SHARE`, a setting; engine name playbook.tier_c_prob; n_imp 4 x n_out 20 draws in the runs).
- A: not C, bound by capability horizon, physical work or permissibility (backtest-supported filters).
- B: otherwise (cost crossover, reliability, readiness, volume), sourced inputs, not validated by the backtest.
- The runner's and the engine's tiers agree on 72% to 91% of units (by configuration): the two test different
  class-d key sets (the engine about 145 keys, including impute-level keys since its note-1 change; the runner the
  sections that move a mode plus four impute-level keys). The runner's tier is the one in the tables; the engine's is
  in `eng_tier_now`. Activity decisions agree on every unit; binding categories on all but P12|4.A.4.a.6.c.10 at
  readiness 0.9 in A3, A5, A6 (runner: build-or-buy volume gate; engine: cost), a definitional difference.

## 2. Archetypes (def:playbook-archetypes; code/playbook/archetypes.py)

Population: 2023-25 core firm-years with FCF-after-SBC margin (E1), n = 446; cells use non-acquisition firm-years (E2),
n = 377. Quantiles (population): g Q25 5.4%, median 12.9%, Q75 22.3%; m Q25 -10.7%, median 2.4%, Q75 11.5%; R Q75
27.8%, Q95 44.8%. Rules: A1 g >= Q75 and m < Q25; A2 Q75 <= R < Q95, g and m >= median; A3 g < median, m >= Q75;
A4 median <= g < Q75, m < median; A5 g and m < median; A6 R >= Q95 (precedence). Cells are disjoint (verify D3); 280
of 377 E2 firm-years fall in a cell. A7 = Bending Spoons from notes/case_bending_spoons_f1_extract.md (reported growth
Q2 2026 126%, organic 3%, NRR 0.95 so G_i = ln 0.95 = -5.1%; X^G = 1.14 at its unlevered hurdle). Only 11 non-elite
E2 firm-years pass the Rule of 40 with both components above median, hence A2's definition by score quantile.
Inputs are cell medians, not tuned (no parameter was changed after seeing a result).

## 3. Cell-to-label map (Table tab:playbook)

| column | content | labels |
|---|---|---|
| Position | cell medians, quantile ranks | def:playbook-archetypes |
| Binding constraint | largest gap line; scarcest capacity year 0 | Paper 1 tab:gap; prop:ext-bandwidth(b), prop:attainable(c) |
| First two levers | ranking of growth automation, G&A, R&D, cost of revenue at x = 0.10 and the public weight | prop:playbook-rank(a), (b) |
| Levers to avoid | owned compute below g* + delta_K (iii); CoR when dur c_h < a_GA (ii); growth engine under a sponsor when X_PE < X_dagger_0 of the first-ranked line (i); in-scope ICFR steps failing the catch-rate gate at readiness 0.9 (iv) | cor:playbook-nopay (i)-(iv); prop:playbook-rank(d), (f); prop:playbook-gates(d) |
| First wave | engine roadmap wave 1 (names, start year, NPV) | prop:ext-waves; engine plans/roadmap |
| A7 row | X^G, acquisition price test, treadmill | prop:acq-pc(d), prop:acquired-score(a), prop:acq-limits(a), prop:acq-replace |
Grid (tab:playbook-grid): X_o per owner (1.4), sigma*, lever values, X_dagger_0, first lever; engine program values
per regime (the engine's own runs; its sponsor and acquirer runs select no process for A1, A4, A5, reason not
diagnosed here). Record fields: spec Section 4.

## 4. Grounding class of every input

| input | value | class | source |
|---|---|---|---|
| cell medians g, m, S&M, G&A, R&D, GM, capex | panel | a | data/panel_v2_all.csv (SEC XBRL) |
| r_sigma | 3.3 | c | Paper 1 sections/empirics.tex |
| alpha | 0.3 | c | Paper 1 calibration range [0.25, 0.45] |
| k convention | capex/g | c | Paper 1 anchor |
| x (proportion) | 0.10 | setting | normalization |
| delta_K | 0.25 [0.20, 0.33] | d | params.yaml depreciation.accelerators_economic_delta_K |
| HHI (dur) | 0.25 [0.1, 0.5] | d | engine market.hhi |
| public w | 0.3 [0, 0.6] | b (survey) | Graham, Harvey and Rajgopal 2005 |
| dual-class w | 0.15 | d | engine preset |
| public r | ln(1.0934) | a (practitioner) | Damodaran Jan 2026 |
| family spread | -0.01 | d | engine preset |
| PE rate, hold, M_exit, h_x | 19.9% cont., 6 y, 14x, 1 | b, b, b (small sample), d | Gompers et al. 2016; Kaplan and Stromberg 2009; practitioner |
| VC rate, horizon, exit multiple | 27.0% cont., 7 y, 8x | b, d, d | Gompers et al. 2020; engine presets |
| permanent hurdle | ln 1.25 | a (company) | Bending Spoons F-1 (ass:acq-pc(ii)) |
| readiness cases | 0.4, 0.9 | d | data/examples/invoice_chain.yaml |
| step-level parameters | engine defaults | per params.yaml grounding field | tier rule uses the class-d set |
| Bending Spoons figures | F-1, 6-K | a | notes/case_bending_spoons_f1_extract.md |

## 5. Findings (reference runs; generated values in the macros)
- At the public (revealed) weight, the growth engine is first and engineering second for all six archetypes; it
  stays first for dual-class and family owners; under a sponsor at entry it is first only for A6; under a permanent
  acquirer for none of the five archetypes where its weight is defined.
- Switch weights X_dagger_0 against G&A: 5.8 (A2) to 9.1 (A6), all above screening weights 2-3 (Paper 1 result).
- Cost-of-revenue automation is never among the first two levers at dur = 0.40.
- Owned-compute score hurdle: 0.27 (A5) to 0.64 (A6) of opex per dollar of capital.
- Step level: at readiness 0.4 capability (about 42% of step decisions) and readiness (31%) bind most; at 0.9
  reliability (detection) binds 43% of steps and 45% of in-scope ICFR steps. Automation is the activity decision for
  15 step decisions (2%) at 0.9; augmentation for 23% at 0.4.
- Invoice chain matching step (P02.5): readiness-bound at 0.4 (0.37 vs floor 0.50), detection-bound at 0.9 (A2:
  0.61 vs 0.85; A5: 0.65 vs 0.89), outsourced in both, Tier B; physical-bound in A1 (W5).
- Ten procurement and finance steps are physical-bound in every archetype (W5 list in the spec).

## 6. Open items and change requests (not my files)
- Lead / integrator:
  1. `\input{sections/levers_by_position.tex}` at the end of `sections/horizons.tex` (after the "Levers" subsection; it is
     a \subsection) or in paper1/paper1.tex after horizons; it inputs its own macros and table. It cites
     murthy2026transformation (in paper1/refs_paper1.bib, not in refs.bib).
  2. Paper 2's main file needs `\usepackage{longtable}` (Table tab:playbook-steps), `\input{part2/theory_playbook.tex}`
     after theory_acquirer, `\input{part2/proofs_playbook.tex}` after proofs_acquirer (it also holds
     app:playbook-tables), and part2/validation_backtest.tex somewhere (sec:backtest is cited).
  3. `code/regenerate_all.sh`: run `python3 code/playbook/run_archetypes.py --jobs 3`, then
     `python3 code/verify_part2_playbook.py`, before paper1_macros.py, which reads `\lpRatio` and the lever table
     (stages `playbook` and `verify_playbook`; order corrected 3 Nov 2026).
  4. Notation table: new symbols r_sigma (\mathsf r_\sigma), X^ddagger_0, h^ddagger, Delta R_sigma, Delta R_lambda,
     Delta R_a, Delta R_h, Delta R_G, Delta R_k, x (common proportion), a_GA, a_RD; vartheta reused from Part I.
- Data agent: W5 (physical_override, licensed_override in process_activities.csv; the engine already reads them),
  W6 (aei_augmentation_pct in activities.csv).
- Engine builder: W1-W3, W5, W7, W10, W11, W13-W17 are in the engine (messages of 12:40-13:20); open: W8 (iota*_p),
  W12 (owner capability), W4 beyond frontier_shift, W9 (cycle time, author), cross-process dependencies.
- Author decisions (OPEN): reading of the revealed weight as the public net weight (1.4); cycle-time KPI (W9); whether
  to report A6's sponsor weight given G_i above the sponsor's rate.

## 7. Outputs and verification
- data/playbook/playbook_steps.csv (136 steps x 12 configurations), playbook_activities.csv (662 activity units x 12),
  playbook_dwa.csv (207 DWAs x 12), archetypes.csv, data_dictionary.csv (O*NET CC BY 4.0 attribution row).
- part2/tables/playbook_{macros,archetypes,table,grid,functions,processes,steps_full}.tex;
  sections/tables/{levers_position_macros,tab_levers_position}.tex; notes/playbook_results.json.
- `python3 code/verify_part2_playbook.py`: symbolic and numeric checks of every closed form, cross-checks with
  verify_part2_regimes (B7, B10), verify_part2_core (18g), verify_part2_competition (F1), verify_part2_product (G5),
  Paper 1 cor:capital; archetype reproduction from the panel; lever map against the engine's api.lever_map;
  runner-engine agreement; tier rule; coverage; macros.
