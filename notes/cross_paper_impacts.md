# Cross-paper impact register

Every finding or change to a shared input is logged here with the papers it affects. A change counts as done only when every affected paper has been updated and regenerated. The author's instruction, 29 Oct 13:08 (UTC−7): "Please keep all papers updated."

**Papers**
- **P1:** The Rule of 40 as a Price Line. Built from sections/ and paper1/.
- **P2:** The Economics of AI Transformation. Built from part2/.
- **P3:** the autofrontier engine. Built from engine/ and code/playbook.

**Shared inputs, and who consumes them**

| Shared input | P1 | P2 | P3 (engine) |
|---|---|---|---|
| SEC panel (data/panel_v2_all.csv; panel_v3 in progress) | empirics, calibration anchor, acquired-growth flag | software rows of industry_function_shares (data agent); backtest firm-level test (206 firms); playbook archetype quantiles (2023–25, 446 firm-years) | software priors; synthetic firm |
| Execution parameters (success rate, change capacity, pace) | prop:expected; horizons | core and ext transitions; invoice example (ϖ_p); waves | defaults.yaml org.*, success logits |
| Growth weight X (decision) and screening weight | abstract and model (7–13, 2–3) | examples at X = 9; regimes' X_o; the playbook ranking (calibrated to α(X̂−k) = 3.3) and the thresholds X‡₀ and (X_o−k)/(X̂−k) | finance and growth-weight defaults |
| Rules for charging acquired growth (cash flow classification, annuity) | sec:acquired-growth | sec:acquirer (prop:acq-pc, the treadmill) | acquirer limits; growth-quality report |
| Bending Spoons facts (notes/case_bending_spoons_f1_extract.md) | sec:acquired-growth | sec:acquirer; playbook A7 | params permanent_capital |
| Compute share c_c | ceiling, 42% threshold, horizons | extension tornado, product margin crossover, playbook owned-compute rule | finance and compute defaults |
| Reliability and ICFR cost inputs (r̄, e_H, q_M, regulated multiplier, ICFR line) | prop:amin | invoice example, acct-amin, acct-itgc, playbook catch-rate gate | engine finance rules, ITGC lines |
| params.yaml and defaults.yaml | the full-cost floors in the ceiling | every example | everything |

**Round-2 parameters adopted (29 Oct, params commit; notes/params_commit_2026-10-29.md).** Every row of notes/assumptions_round2.md §0 except the growth weight X (pending bounds) is now in params.yaml, params_reliability.yaml, engine defaults and calibrate_horizons.py. Text in P1 and P2 still carries the old numbers until each section is regenerated or rewritten; the failing verify checks list where.

## Open items from the round-1 review of Paper 1

The consolidated plan is notes/reviews/paper1_v1/revision_plan.md.

| Issue | Affects | Owner | Status |
|---|---|---|---|
| IM-1: backfilled, non-first-reported firm-years (138) | P1 empirics and calibration; P2 backtest, software priors and playbook archetypes; P3 priors | sample audit (econometrician), then the data agent, backtest agent and playbook regeneration | sample audit running (panel_v3) |
| IB-5 and IM-4: misclassified firms (game publishers, casino gaming, CoreWeave), the captive Exzeo, Xunlei's missed acquisition | same as IM-1 | sample audit | running |
| IB-5: the 0.54 success rate is pilot attrition, not failed transitions | P1 pace and horizons; P2 transitions and the invoice example; P3 defaults | assumptions round 2 proposes ϖ 0.70 [0.54, 0.80] (b) | proposal in; to adopt |
| EX-4: re-ground execution pace | P1 prop:expected and horizons; P2 waves, transitions and playbook; P3 org defaults | assumptions round 2 proposes b̄ 0.67 [0.37, 0.85]; drop the disruption haircut when ϖ and b̄ come from outcome surveys (double count); T_emb 1.25 [1, 2]; κ_abs 0.10 [0.05, 0.22] re-grounded; a revealed-pace reference (FY22→FY24 median op-margin +7.5 pts, n = 149). Expected effect: embedded share 2.5/10/23% → ~7/20/41%, dip-crossing 9 → ~4 years | proposal in; to adopt |
| IB-4: operating cash flow is already after interest under US GAAP, so the WACC annuity double counts | P1 sec:acquired-growth; P2 sec:acquirer; P3 report basis | acquirer agent (done for P1 and P2, 29 Oct: before-interest cash margin, four charging conventions, return on acquisition capital, Q2 organic score 37 before interest and 22 after; notes/acquirer_fixes_v2.md) | P1, P2 done; P3 pending: report before-interest basis, convention grid, return on capital |
| IM-5, IB-1, EX-2, R1-5, R2-1, FE-1, R3-4: the 7–13 growth weight. Fable econometrics shows it is an artifact of median S&M/(g−G) (10.5 in the lowest excess-growth tercile, 1.8 in the highest); referee 3 (Opus) gets 2.5–4.5 after netting out maintenance S&M; assumptions round 2 gives 3–13 by baseline (2.9–5.2 on the CAC-ratio baseline) and verifies Bessemer 2–9× at source | P1 abstract, model and empirics; P2 every example at X = 9, regimes, and the playbook calibration α(X̂−k) = 3.3 and thresholds; P3 defaults | dedicated growth-weight analysis (to start), then the P1 editor, P2 owners, playbook and engine | open; decision needed before rewrite |
| IM-3, FE-4, R3-5: the capital-intensity gap is mostly the capex deduction (−6 [−15, +5] E1, −3 [−12, +6] E2 with capex added back) | P1 empirics; P2 playbook, if cited | P1 editor: withdraw as evidence for Prop. 5 | to apply |
| IM-2 and FE-7: yearly series; the P95 decline is compositional (2025 E1 GAAP P95 54.6, near 2016–19; within-year slope ≈ 0) | P1 abstract, empirics; P2 anything citing the decline | sample audit (reweighting), then the P1 editor | running |
| FE-2, R3-1, R3-2, R3-3: E1–E2 contrasts fail Holm (best adjusted p 0.66) and depend on the interval type; E2 is mostly an exclusion sample, and imputing the 410 dropped firm-years returns E1's slope and gradient, so the contrasts measure selection | P1 empirics, tab_estimands, abstract; P2 sec:acquirer if it cites "acquired growth flattens the slope" | P1 editor; sample audit to report basic/normal/percentile and Holm | to apply |
| FE-3, R3-6: T(40%) under E2 (30–35% NaN replicates) | P1 | P1 editor: withdraw | to apply |
| FE-5, R3-12: calibration anchor is noise-dominated (cluster-bootstrap Π_ub −1 [−16, +16]; transient share [−35%, +29%]) | P1 calibration, horizons; P2 anything that uses the anchor's Π or transient share; P3 calibration defaults | sample audit (firm-cluster bootstrap), then the P1 editor | running |
| FE-6, R3-11: the E2 switch after the robustness results and the pro forma ambiguity rule are undisclosed in the main text; E2 is nearly exclusion-only (410 of 469 dropped) | P1 empirics and protocol; P2, P3 protocol appendices | lead agent and P1 editor | open |
| R3-9: the slope uses the local conditional quantile Q_0.9(m\|g), but the frontier the theory defines (Ψ_χ, Def. 2; Prop. 7) is the dominance-cone order-α frontier, which is much flatter (E2 GAAP −0.31, cash −0.19). The earlier "flat frontier reversed" is an estimator switch, not a data finding | P1 Sections 2.3, 3.7 (ℓ calibrated to −0.4), 5.1, 5.3, App. E; P2 anything calibrated to ℓ or quoting the slope; P3 the ℓ default | sample audit to report both objects, order-m, and a τ and window grid; then the P1 editor and core theorist decide which object calibrates ℓ | open; decision needed |
| R3-7, R3-8: the E2 GAAP slope −0.59 is a solver approximation (exact −0.564); τ = 0.90 and the 0–60% window are unjustified (about −0.4 over 0–100%) | P1 macros and text; P2/P3 where ℓ is used | sample audit: exact LP solver throughout, τ and window grid | open |
| R3-10, R3-14: the size gradient lacks period effects (E1 cash −2.8, E2 −0.9 with them); period slope differences are untested (only E1 GAAP is significant); "never with a full point" fails in 2020–25 | P1 Section 5.3, 5.5, intro, abstract | sample audit, then the P1 editor | open |
| R3-13: stochastic frontier (cohort frontiers, survivorship, no inference); the result survives a common frontier (14.0 [8.9, 20.3] GAAP) | P1 Section 5.7 | sample audit, then the P1 editor | open |
| R3-15 to R3-19: within-firm timing (g_{t+1}), bootstrap B and seeds, replication order (estimate_organic.py missing), consolidated margins under E2, documentation mismatches | P1; regenerate_all.sh and REPLICATION_README for all papers | sample audit and lead agent | open |
| FT-3: rem:owncompute mixes ψ = 0 for server capital with full deduction of replacement; under ψ = 1 the thresholds are 16.5%/49.5%, not 20.1%/60.4% | P1 rem:owncompute; P2 playbook owned-compute rule (0.27–0.64 of opex per $ of capital) and regimes' owned-capacity K; P3 compute defaults | core theorist (one convention), then playbook and engine | open |
| FT-7 and R1-1: the pace numbers (23% by 2036, completion 2033) come from a fluid relaxation that prop:expected does not cover (n_cap = 0 at 0.82 processes per wave); the deterministic clock is assumed, not derived | P1 prop:expected and horizons; P2 waves and transitions; P3 pace | Part I integration theorist; with EX-4 | open |
| FT-20: possible double count of the retest at each model upgrade between C^itgc_g and c_mnt | P1 lem:fullcost, ass:layers; P2 acct-itgc lines; P3 ITGC and maintenance lines | accounting theorist and engine builder | open |
| FT-21: prop:acquired-score(d) set the base's zero-spend growth to ln NRR | P1 measurement_acquired; P2 treadmill and prop:acq-retention(b); P3 regimes.limits_check, formulas.acq_standstill | acquirer agent: G_i = ln[1 + (S_sub/S)(NRR−1) + (1−S_sub/S)γ_ns]; required acquired growth = growth + organic decay (71.7–76.0% of revenue a year for 2025; 63.7% at 3% organic) | P1, P2 done; P3 pending (engine pass) |
| FT-14, R1 novelty, FI missing literature: customer capital and market penetration (Arkolakis; Gourio–Rudanko; Drozd–Nosal; Foster–Haltiwanger–Syverson), q-theory of advertising (Vitorino; Belo et al.) | P1 literature and contributions; P2 literature where the growth technology is reused | literature agent (verify before citing) | open |
| IB-3: scores on FCF before SBC | P1 | P1 editor | open |
| IM-6: panels are single AI agents playing several roles | P1, P2 and P3 protocol appendices | lead agent | open |
| EX-1: decision rules for finance teams | P1 (short); P2 playbook; P3 lever map | playbook delivered prop:levers-position and tab:levers-position for P1; P2 theory_playbook | delivered; place in P1 (end of horizons.tex proposed) and revalidate after X and pace changes |
| EX-9: licenses cover text and code, not ideas | P1, P2, P3 license footnotes and conclusions | lead agent | open |
| Review independence: the author asked (13:08) for different models. Round-1 cross-model referees ran on Fable; round 2 and the final audit will run on models different from the drafting agents'. Each agent's model is recorded in agent_log | protocol appendices of P1, P2, P3 | lead agent | in progress |
| RA-1: the accountability floor must be a pass/fail ICFR constraint, not a cost-loss trade. Assumptions round 2: ICFR line per in-scope AI application $347k → $80k [$16k, $350k] (KPMG); regulated multiplier 1.5 [1.1, 2.0] | P1 prop:amin; P2 prop:acct-amin, prop:acct-itgc, playbook gates; P3 amin_design and ITGC lines | accounting theorist, then the P1 editor and the engine builder | open; inputs in |
| RA-2: common-mode failure. Kim et al. (ICML 2025) verified: 0.60 [0.42, 0.60] is P(same wrong answer \| both wrong) on HELM MMLU, not P(B wrong \| A wrong); any use as a conditional error rate is wrong | P1 Ass. 7; P2 ext common-mode, reliability parameters; P3 risk | core and ext owners; engine builder | verified; to apply |
| Reliability inputs: r̄_high 0.99 → 0.98 [0.975, 0.995]; e_H 0.02 kept [0.009, 0.05]; q_M 0.998 → 0.995 | P2 invoice example and playbook catch-rate gate; P3 finance rules | to adopt with the params commit | proposal in |
| RA-5: SR 26-2 / OCC 2026-13 (17 Apr 2026) supersede SR 11-7, with generative and agentic AI out of scope (fn. 3); Reg. (EU) 2026/1744 (in force 27 Jul 2026): Annex III high-risk from 2 Dec 2027, Annex I from 2 Aug 2028 | P1 discussion; P2 accounting, labor, product; P3 MODEL_RISK.md and EU flags | verified at primary sources; owners to apply | verified; to apply |
| R4-F2: compute share c_c. Proposal: 0.06 [0.01, 0.20] at 2025 prices, 0.12 [0.02, 0.30] in 2028, 0.08 [0.01, 0.25] in 2031, 0.05 [0.01, 0.20] in 2036. Central threshold 42.3% → ~32–36%, horizon-dependent (dG*/dc_c = 0.82) | P1 ceiling, 42% threshold, abstract and horizons; P2 extension tornado, product margin crossover, playbook owned-compute rule; P3 finance and compute defaults | to adopt with the params commit, then the P1 editor, P2 owners and the engine builder | proposal in |
| R4-F3: pass-through. Proposal: φ scenario {0, 0.5, 0.7} (Apple/Analysis Group ≈ 0 short run; Ganapati 0.7) | P1 ceiling and horizons; P2 competition already consistent; P3 dilution | P1 editor (with the competition notes) | proposal in |
| R4-F1 and R4 citation errors (Demirer, ICONIQ, Gundlach, Bonney, Terry, Hampole; METR uncited) | P1 literature.tex:27, horizons.tex:6 and :13; P2 literature_modern:21, theory_core:76, theory_product:162 and :177 (ICONIQ 2026 treated as realized); every paper citing the keys | literature pass v2 done: 8 entries corrected, 21 wording corrections at 16 .tex lines (old → new in notes/lit_pass_v2.md §a); editors apply. Key point: Demirer's −1.11 is a within-model cross-provider substitution elasticity, so "the compute share need not fall" is unsupported and must change with the round-2 c_c | corrections ready; to apply in P1 rewrite and P2 propagation |

## Items from the playbook build (29 Oct, ae6a9bd71174c8ad2)

| Item | Affects | Status |
|---|---|---|
| The revealed weight is already the public owner's net weight; applying earnings pressure again double-counted it. Fixed in the lever map and in the engine (W14) | P2 theory_playbook, theory_regimes (check X_o for the public owner); P3 | fixed in P2 playbook and P3; theory_regimes to be checked |
| The playbook is calibrated to α(X̂−k) = 3.3 and the panel archetypes (panel_v2, 2023–25) | P1 levers_by_position; P2 theory_playbook; P3 playbook outputs | regenerate after panel_v3, the growth-weight decision and the params commit |
| W5 (step-level physical/licensed overrides) and W6 (AEI augmentation share) still need data; until then ten finance steps are wrongly physical-bound and carry Tier A | P2 playbook tables; P3 | open (data agent) |
| Engine W8 (readiness threshold per process), W12 (owner capability), W9 (cycle time), cross-process dependencies | P3; P2 playbook | open |
| P2 main file needs longtable, the two playbook inputs and validation_backtest.tex | P2 assembly | open (assembly) |
| Acquirer X placeholders (`% XBOUNDS`): P1 sign statement (acquired growth raises the fully charged score iff X > k^acq; flips at 1.7–3.2× revenue) and the P2 replace example (break-even 0.67/0.34/0.19% at X = 2.5/5/9); P2 theory_playbook.tex line 102 and engine levers.py line 140 apply k^acq < X_o and must be made conditional | P1, P2, P3 | swap in final bounds in code/verify_part2_acquirer.py (XBOUNDS), rerun; check E15 if the lower bound falls outside 1.73–3.23; playbook and engine in the propagation pass | open (awaits bounds) |
| Unused macros AcqTreadLo/Hi in code/paper1_macros.py | P1 | P1 editor | open |
| Bibliography merge: refs_additions_v2.bib (89 verified entries) goes first; the 8 superseded entries are deleted from paper1/refs_paper1.bib, part2/refs_modern.bib and refs.bib; key collisions resolved per notes/lit_pass_v2.md §d (bls2026joltsnews; eu2026reg1744 = eu2026regulation; vectara2026leaderboard = vectara2026hallucination; gans2026market supersedes gans2024market; agrawal2019exploring ≠ agrawal2019artificial). Canonical bib: paper1/refs_paper1.bib for P1; refs.bib is legacy (old combined paper.tex) and is not maintained | P1, P2, P3 docs | P1 editor and P2 assembly | open |
| Parameter-source table sections/tables/tab_param_sources.tex (44 rows; needs longtable) | P1 appendix; P2 may reuse | P1 editor | ready |
| Params-commit follow-ups: (1) the engine's shock model may still double count disruption against P1 (success.a0 branch; ISSUES 9); (2) central Cournot φ_ind is still 0.8 against the new φ scenario set (ISSUES 10); (3) the ICFR target of $80k per in-scope AI application is not reached by the explicit unit costs (invoice line $267k); (4) the invoice conditional case's q_cap 0.988 now exceeds the 0.98 reliability target; (5) the high-compute case c_c 0.40 is kept but labelled infeasible (cap 0.30); (6) favorable/conservative c_c cases are the central value halved/doubled (composite rule, to state) | P1 horizons; P2 core (invoice), ext, competition, accounting; P3 | P2 theory pass (items 2–4), engine pass (1), P1 editor (5, 6) | open |
| Verify checks failing because text carries pre-commit numbers: accounting 6c, 6g, 6j; acquirer B4 (W0 156k now above C_spec 144k: claim no longer holds); regimes C5, C6, G4 (Case R IRR 15.0% → 9.1%, minimum horizon 7.0 → 9.87 years), I3 pre-existing; core 23c–e; ext B8; verify_theory 20a, 20d, 20e, 20h, 20i, 20m, 22g | P1, P2 | section owners in the P2 theory pass and the P1 rewrite | open |
| Engine after the commit: test_tier0_only_reports_wide_ranges fails (Tier-0 spread $2.27B below full-tier $2.39B: less data should widen ranges, so this is a real property question, not a snapshot); notes lock on acquirer_notes.md (check_sync --accept after review); invoice_chain.json to regenerate | P3 | engine pass | open |
| P2 main file does not exist: regenerate_all.sh stops at latex_p2 | P2 assembly | assembly | open |

## panel_v3 results (sample audit, completed 15:42; notes/sample_audit.md, notes/inference_v3.md, notes/empirics_v3.json)

| Result | Affects | Status |
|---|---|---|
| Ψ_0.90 slope (primary, D-2), 2010–25, 0–60%: E1 GAAP −0.22 (0.11), cash −0.16 (0.10); E2 −0.29 / −0.22; imputed −0.39 / −0.36 (M = 4). 0–40% window: E1 −0.31 / −0.27. Local quantile (descriptive): E1 −0.41 / −0.35, E2 −0.61 / −0.43. ℓ input: notes/frontier_slope_v3.json | P1 model sec:model-industry (FRONTIER-SLOPE placeholder), empirics, horizons calibration of ℓ, abstract; P2 and P3 wherever ℓ or the slope is used | to apply after the P1 theory agent fixes the ℓ mapping |
| Growth-weight bounds (D-1), as α(X−k), E1 / E2: by excess-growth tercile 10.1 / 3.0 / 1.5 (E1); floors of 10 and 20 points 1.9 and 1.3; net of the S&M share of below-median growers 0.99 / 1.14; levels regressions 0.05 to 0.43; G fixed at 5/8/12% 2.1/2.4/2.7. With α ∈ [0.25, 0.45] these span X − k from below 1 to about 12. The spend ratio itself (3.0–3.5) is robust and stays the playbook's calibration input. Evaluation points for examples stay X ∈ {2.5, 5, 9} (Bessemer screening range; the CAC-baseline and netted estimates; the middle tercile), and each paper says where a conclusion flips below 2.5, since the levels methods imply lower values | P1 abstract, intro, model, empirics; P2 all XBOUNDS spots; P3 defaults | XBOUNDS placeholders being set by both theory agents and the acquirer agent |
| D-3 robustness: holds under E1, E2 and both imputation bounds: Ψ GAAP slope negative and above −1; 0–40% slopes; margin gap and its S&M and R&D parts; anchor Π_lb > 0; entrant gap (+13.8 [8.8, 19.4] GAAP); P95 decline. Fails somewhere: cash Ψ interval (E1 includes zero), size gradient (0 of 4), capital-intensity gap with capex added back or by firm median (0 of 4), the Prop. 5 interaction (0 of 4), cash steepening (wrong sign in 3 of 4) | P1 empirics and abstract; P2 anything citing these | P1 editor |
| Familywise: of 38 E1−E2 contrasts none survives at 5%; of the 14 headline positions restated under D-2/D-3, Ψ slopes above −1, the margin gap and the S&M part of the 40–60% gap survive Holm and Romano–Wolf under every interval type; the GAAP Ψ steepening in 2020–25 (−0.38 [−0.60, −0.16]) survives under normal and basic p-values only; the P95 changes come in at 10% | P1 empirics | P1 editor |
| Composition: the E1 cash P95 decline of −12.8 splits into −16.8 composition and +4.0 within-cell; 2025 E1 GAAP P95 is 51.4 with a within-year slope of +0.11 | P1 abstract, empirics | P1 editor |
| Anchor v3 (notes/calibration_anchor_v3.json): E2 19 firm-years from 10 firms, Π_ub median −7.0 [−17.0, +15.4], Π_lb +18.5 [+6.8, +26.0], transient share −14% to 37%; E1 calibration rule 13 firm-years (7 firms), Π_ub −1.3; imputed −0.5 / −0.7. Calibration central = E1 calibration rule (D-3 baseline), with E1-all-tail, E2 and both imputations as sensitivity rows; only Π_lb > 0 is a conclusion | P1 horizons and calibrate_horizons.py (points at the v2 E2 file); P2 and P3 calibration defaults | switch calibrate_horizons.py inputs after the ℓ mapping is fixed |
| T(40%) not estimable in any estimand (E2 cell has 9 firm-years) | P1 | withdraw |
| Capital-intensity gap: capex added back −4.6 / −0.2 (E1 / E2), firm-median −4.5 / −2.8, neither significant | P1 | report as accounting effect |
| SEC data still needed: R2 (misclassified firms, 15 named), R3 XBRL part (related-party revenue), R5 (4 debt-only filers), R4(c) (acquiree revenue element), and InterestPaid / IncomeTaxesPaid for a pre-interest, pre-tax cash score (R2-3). The container cannot reach sec.gov; the subagent's browser request was refused | P1 sensitivities and B5 score bridge | retrieved 16:06–16:15 through the author's browser (data/v3_inputs/README_retrieval.md); sample audit integrating and rerunning v3 |
| Replication: estimate_organic.py's old anchor-key check fixed; run order V3_PANEL=v2 then default (about 24 and 54 minutes); add estimate_v3.py to regenerate_all.sh | all papers' build | lead agent / build script |

## P1 after phase A (editor, about 16:30)

| Item | Owner | Status |
|---|---|---|
| Rerun of v3 with the new SEC inputs is overwriting live outputs; paper1_macros.py refuses inputs with fewer than 999 replications and was run on the 16:17 snapshot; rerun `python3 code/paper1_macros.py` (no option) after the rerun; the CLAIMS block will stop on any qualitative claim that changes | editor after rerun | open |
| Abstract, intro, horizons, discussion and conclusion still carry v2/E2 numbers and the withdrawn 7–13 | editor phase B | open |
| acquired_macros.tex shows a 24%/37% flag and a 10–26 P95 fall, but data.tex now has 26%/42% and 8–13: rerun verify_part2_acquirer.py (it also writes part2/, so wait for the P2 theory agent) | lead, after the P2 theory agent | open |
| verify_theory 160/168 (20a, d, e, h, i, l, m, 22g: calibration_results.json predates the params commit) | phase B (recalibrate) | open |
| Proposition/lemma references: switch every "Proposition~\ref" to \autoref (the theory agent renames environments) | editor phase B | open |
| Method citations Holm (1979), Romano and Wolf (2005), DiNardo, Fortin and Lemieux (1996), Jondrow et al. (1982): verified by the lead agent in paper1/refs_methods_v2.bib | editor merge | ready |
| Length 111 pages (target about 75): supplementary appendix for the parameter-source table, v3 robustness tables and the detailed protocol tables; keep a concise protocol appendix in the paper | editor phase B | open |

## P2 after the theory pass (about 16:50; notes/p2_theory_fixes_v2.md)

| Item | Affects | Status |
|---|---|---|
| RA-1 pass/fail floor (def:acct-admissible), ICFR lines reconciled (upgrade retest at KPMG effort, $24k; invoice line $205k, reference application $88k), invoice cap at min(r̄_high, q*), common mode with ITGC, φ_ind central 0.5, ψ = 1 for domestic servers, failing checks fixed, XBOUNDS placeholders, RA-5 dates, literature corrections | P2 | done |
| Sign or rank changes: invoice capture-and-matching pair now pays at readiness 0.9 (+$6.6k, fragile: −$1.5k with the cap at q*); accounting floor design depends on ε̄ (all-AI never admissible); regimes example: overhead first at X = 2.5 and 5; product: dilution plan fails below X − k = 3; playbook: Vimeo's price fails at X_o = 2.5 and AOL's below 2.3 | P2 text; P1 only where it cites these | recorded |
| Engine changes E1–E9: shock double count (ISSUES 9); amin_design to the constrained minimum; C_val $100k → $24k; φ_ind central 0.5; psi_equipment wording (40% is the §168(k)(10) transitional election, not the election-out case); X-level-dependent outputs (levers.py line 140, X_default [5, 13]); MODEL_RISK.md (SR 11-7 → SR 26-2) and EU dates in impute.py; c_err at the review that remains; playbook outputs to regenerate after the φ change | P3 | open (engine pass) |
| Engine tests failing outside P2: test_change_control (acquirer_notes.md changed at 14:32), test_end_to_end tier0 Monte Carlo | P3 | open (engine pass) |
| Root refs.bib ICONIQ entry replaced with the corrected v2 entry by the lead agent (backup in scratchpad) | P2 | done |
| P2 length 240 pages in the test assembly | P2 assembly | open (later) |
| Unverified: §168(k) statute text (Notice 2026-11 and LII sub-sections verified); EU Art. 113 operative text (dates from recitals); APQC primary values (via vendor blog) | P2 | listed |

## v3 rerun with the SEC inputs (about 17:40)

| Item | Status |
|---|---|
| Main results identical (E1, E2, imputations, anchor, families, Ψ slopes); E2x50 and E2pf50 lose i3 Verticals 2023 (≤ 0.3 points in any reported table statistic) | done |
| R3 applied (no firm-year ≥ 50% related-party revenue; maximum SINA 2015, 26.9%); R4(c) applied (no new core flags); R5 flag and sensitivity (7 firms, 26 v3 firm-years; slope unchanged); R2 named-firm sensitivity (4 firms classed non-software; keywords miss THQ, Take-Two, Roblox, CoreWeave, Unity: report as a partial check) | done; P1 editor to report |
| B5 bridge (tab_bridge_v3.tex): adding back interest and cash taxes lifts P95 about 5 points in both periods, decline unchanged; frames values are latest-filed | done; P1 editor to fill placeholder |
| Foreign filers (AutoNavi, Changyou, Retalix) not tested for listing; full R2 needs every registrant's description | open (limitations) |

## P1 after phase B (about 18:05)

| Item | Status |
|---|---|
| Main paper 76 pages, supplementary appendix 43 pages; 1,122 macros; 49/49 machine-checked claims; abstract 1,911 characters | done |
| Headline: G* 31.0% central (was 42.3%), 36.0/32.6/30.1% at 2028/2031/2036, 36.3/38.5% with pass-through 0.5/0.7; program realized share 41% by 2036; gains exceed dip after about 4 years; maximal score on the central path 56/60/66 | done |
| verify_theory u_rev changed to no-review rates by the lead agent (one line, as tested by the editor) | done: 189/189 on the live repo (18:07) |
| Levers tables still v2 (\lpRatio 3.3): regenerate via the engine agent's E9 on panel_v3, then rerun paper1_macros.py and build_paper1.sh | waiting on engine |
| arXiv packaging: arXiv builds one PDF per submission. Lead decision: submit one combined PDF (main paper, then the supplementary appendix with S numbering, clearly marked) and keep separate PDFs for journal use | at packaging |
| Leftover XBOUNDS comment in measurement_acquired.tex (does not print) | swap in final wording at packaging |

## Engine pass results and cross-paper decisions (about 18:18)

| Item | Decision or status |
|---|---|
| Expected realization per attempt: engine 0.34 against P1 0.47 | Not an author call: notes/assumptions_round2.md §1.1 sets the product to about 0.46 unless the engine's b̄ carries the realization haircut, and it does not (0.67 is McKinsey's realized share for successful transformations). Engine to calibrate varpi 0.70 so the product is 0.47 everywhere |
| Remote threshold ε̄ for the pass/fail ICFR floor: P1 central 1%, engine 5% | Lead decision: central 5% in all three papers, 1% as the stricter sensitivity. Grounding: Audit Analytics (Seventeen-Year Review, 2 Nov 2021) reports adverse 404(b) attestations at 4.6% of all attestations for FY2020, and the Eighteen-Year Review (July 2022) 5.8% for FY2021 and 4.8% for FY2019, both verified at the source by the P1 editor. A 7.1% accelerated-filer figure, from a summarizing fetch by the lead agent, could not be found at the source and is not used. A threshold at which the reference human-only design fails (1% in the example) would contradict most filers obtaining effective opinions. Look for a newer edition |
| C_val copies: paper1_macros.py (editor) and verify_part2_accounting.py (engine agent) still at $100k | being set to $24k |
| Playbook regenerated on panel_v3: the growth engine is first for the public owner at five of six positions (A6 now R&D); durable share 0.62 (central φ_ind 0.5) | P1 levers prose: editor. P2 playbook prose: check at P2 assembly |
| Engine bug: the Monte Carlo never drew shocks (read a copy with shocks off); now fixed. Synthetic plan value $1,378M → $1,814M | done; P3 paper to report |
| Engine open items: AI reviewer catch rate, P(B wrong \| A wrong) and change-control credit are unmeasured; no Annex I system modelled | open (limitations) |

## Response document and threshold edits (about 18:40)

| Item | Status |
|---|---|
| notes/reviews/paper1_v1/response_to_reviewers.md: 192 findings across the 12 reports, 113 fixed, 55 partly, 2 declined, 22 not done (EX 10, R2 3, FI 3, R4 2 and others; reasons in the rows); 41 revision-plan items, 31 fixed, 8 partly, 1 declined (D8), 1 not done | done |
| P1: C_val $24k, ε̄ central 5% (cheapest design one human over one AI layer, 0.090% of revenue; 0.095% at 1%; floor about 0.23% at both), levers prose checked (growth engine ahead of G&A at all six positions; R&D-first for A6 noted as a separate lever); main paper 77 pages, supplement 44; CLAIMS 51/51 | done |
| verify_theory 27d patched by the lead agent from the editor's tested patch | done: 189/189 on the live repo (18:50) |

## Engine follow-up (about 18:55)

| Item | Status |
|---|---|
| Engine success calibration: varpi 0.70 [0.54, 0.80] so varpi × b̄ = 0.47 as in P1; the split of failure risk equally between process and activity terms (0.837 each) is an unsourced class-d assumption (success.c0 1.2 → 2.31, success.a0 1.87 → 2.12) | done; state as class d in P3 |
| ε̄ note cites only source-verified Audit Analytics figures; 7.1% removed everywhere; 2026 Ideagen edition behind a form, not read | done |
| verify_part2_accounting 47/47 with C_val $24k; accounting_macros regenerated (InvEng $205k, RefEng $75k, AppEng $88k, ValEng $24k, NPVEng $0.40M) | done |
| Synthetic run: plan value $1,813.5M → $2,087.4M, probability of loss 0.025 → 0.010; three items changed | done; P3 to report |
| P2 to-do: regenerate invoice_chain.json and invoice_macros.tex (varpi_p about 0.62 → 0.82, so the invoice example's values move and core checks that use a0/c0 move too); drop the self-referential sentence in theory_accounting.tex ("The engine's illustrative \acctItgcValEng{} a retest… gives \acctItgcInvEng"); SyntaxWarning for "\$" in verify_part2_accounting.py docstring line 155; engine test test_inputs_resolve_to_engine_defaults waits on the regeneration | open (P2 sync pass, with the P2 playbook prose check and assembly) |

## Round-2 review of P1 v2 (2 Nov 2026): items to propagate to P2 and the engine
Plan: notes/reviews/paper1_v2/revision_plan_r2.md. Author decisions taken at about 10:15 UTC−8. The P1 numbers are being recomputed by the coder (notes/r2_code_changes.md when done). Once P1 is settled, each item below must be carried into P2 and the engine.
- **Pass-through (IO2-1).** The pass-through rate is to be replaced by an elasticity from Lemma S2, including the revenue-denominator effect.
  - P2 uses φ_ind 0.5 centrally, and the engine uses φ ∈ {0, 0.5, 0.7}. Check every place either applies 1 − φ(1 − H) as a rate.
  - Remove the Demirer et al. pass-through claim wherever P2 repeats it.
- **Compute-share range (IO2-3).** If the 0.5 factor in CC_VALUE_TEST_CAP is dropped, the high-compute case changes in the engine's scenario set and in P2's compute section.
- **Transition cost and error-loss labor share (IO2-5).** Whatever P1 settles must match the engine defaults (T_emb 1.25 vs "two years"; 30% vs 60%).
- **Success label (X2-N2).** varpi 0.70 means "share of attempts that create some value", not success. Relabel it in P2 and the engine docs. The engine's class-d split (c0 2.31, a0 2.12) is unchanged unless P1's pace bridge changes the target.
- **Accountability floor (C1–C3).**
  - ε̄ becomes a class-d scenario with no central value, reported at both 1% and 5%. The engine currently defaults to 5%: expose both and stop calling one central.
  - Direct audit and SOX cost re-grounded on KPMG by firm size, which raises the floor. This affects P2's accounting chapter and verify_part2_accounting.py.
  - Add p^cc break-evens to the engine's design selection.
- **S&M basis (decision 4).** Maintenance-netted is central. Check the P2 playbook and the engine for any "all S&M buys growth" default.
- **Bending Spoons (IB2-N6).** The case must be updated through the 29 Oct 6-Ks wherever P2 uses it (acquirer chapter). Data: data/v3_inputs/bending_spoons_cash_interest.json and raw/bending_spoons_6k_2026-11-02.json.
- **Authorship and declarations.** Use the same authorship wording in P2 and P3 ("The author directed the research and made its decisions; AI agents drafted the text, code and proofs"). Add a declarations line once the author approves its text.

## Round-2 propagation to P2 and the engine (2 Nov 2026; notes/r2_propagation.md)
| Item | P2 | P3 (engine) | Status |
|---|---|---|---|
| Pass-through (B1): rate on all unit-cost savings, margin at the post-cut price; dur is the dollar share | prop:tasks-aggregate(a)(b), cor:tasks-weights and proof, regimes (c), cor:ext-game-engine(a) and calibration paragraph, prop:playbook-rank(a)(d), proof, setup table, results and Limits; playbook lever values use 1 - phi C0 (0.62-0.73 at rate 0.5); P2 text never claimed Demirer shows pass-through near one | formulas.passthrough_terms, margin_after_passthrough, part1_delta_R (overhead exposed), lever_values; frontier_shift exact mapping; lever map and exclusion rule; stakeholder split; plans.py unchanged (dollar share); report, scenarios, defaults text | done |
| params.yaml pass_through block: Demirer "near 1" anchor removed; unit and note rewritten | | | done (paper1/macros.tex unchanged, checked in scratch) |
| Compute value test (B2): cap s_L, 40% case feasible | no occurrence | no occurrence | done in params.yaml (high_compute_case, kappa cap text) |
| Error-loss base 60% and T_emb 1.25 (B4) | no 30% base or "two years" in P2 | none in the engine; params.yaml T_emb already 1.25 | checked, no change |
| varpi label (B9): share of attempts that create some value; target 0.47 | ass:tasks-transition(iv), invoice example | success.a0/c0 text, report label | done (params.yaml unit too) |
| eps_bar no central value; both 1% and 5% (C1) | already two values; "neither is central" added | eps_bar text, by_eps_bar order, eps_bar_note, MODEL_RISK, report | done |
| Direct cost KPMG + AA (C3); ITGC design line $204,672 (C6) | 6j: floor 0.37% (5%) / 0.38% (1%), apps 8 / 7 (13 low fee, 4 with fallback); text and bib (kpmg2025sox archived URL, auditanalytics2023fees) | amin_direct_cost; audit_fee, audit_fee_high, sox_program_by_size; sox404_median removed; C_itgc 50k -> 185k | done |
| p_cc and human-miss break-evens (C2) | new check 5k and text (0.00084, 8.4%, 0.00014) | amin_breakevens on every chosen and human-only design | done |
| S&M basis (decision 4) | Limits and readings paragraph: all S&M an upper bound; netted re-check reported | finance.sm_maint_base; lever map sm_basis_bounds; report | partly: calibration not switched. Re-check: growth engine ahead of G&A at the revealed weight at 6/6 positions on all S&M, **1/6 (A1) maintenance-netted**, 0/6 with no S&M. Switching would change P1 Table tab:levers-position and fail P1's CLAIMS check lpGEFirstAll: P1 decision needed |
| Bending Spoons through the 29 Oct 6-Ks (D3) | case table (interest paid; SACE, TLA, RCF, TLB add-ons; notes by subsidiaries; run-rate interest 20.3-27.9%), r_debt grounding, consistency paragraph | n/a | done |
| Authorship and declarations | part2/declarations.tex (\PtwoAuthorship, \PtwoDeclarations) for the P2 main file | README.md, MODEL_RISK.md | done; P2 main file still to be assembled |
| invoice_chain.json / invoice_macros.tex (varpi_p 0.62 -> 0.82) | regenerated; accounting 6g ($0.40M -> $0.52M) and acquirer B6 (floor at unlimited horizon now +$141k) updated with text | test_inputs_resolve_to_engine_defaults passes | done |
| Self-referential sentence in theory_accounting.tex; SyntaxWarning in verify_part2_accounting.py | dropped (with three redundant "engine's retest" parentheticals); raw docstring | | done |
| Checks | accounting 48/48, acquirer 82/82, core 158/158, regimes 85/85, ext 143/143, labor 43/43, product 94/94, competition 44/44, playbook 38/38 | pytest 191/191 | done |

### Decision 7 (2 Nov, about 12:35 UTC−8): netted S&M basis for the levers and the playbook
- The propagation agent is switching the playbook and engine; the P1 coder will update the levers CLAIMS check; the P1 editor will update §7.5, the summary box and the conclusion.
- **Downstream deliverable.** The Docs artifact "AI Transformation by Rule of X and Company Setup" (https://claude.ai/artifact/NQHXyvbuV9iBJYUxKF428U) and its Word export use the pre-revision playbook (all-S&M basis; v2 numbers). They must be updated once the playbook is regenerated.
- **Done by the propagation agent (2 Nov, about 13:40 UTC−8; notes/r2_propagation.md, section "S&M basis (decision 7)").** Engine (finance.sm_basis = netted, spend_ratio_netted 0.99, maintenance S&M a cost line; README, MODEL_RISK, CHANGELOG), playbook (run_archetypes, results, tables, macros) and P2 text (theory_playbook: assumption, conclusions, five readings, Limits; proofs_playbook) are on the netted basis with all S&M and no S&M as bounds. The S&M-basis row of the table above (decision 4, "partly") is superseded. Headline at the revealed weight: G&A cut ahead of the growth engine at 5 of 6 positions (growth engine only at A1, the growth corner); engineering first of the four levers at 6 of 6; on the all-S&M bound the growth engine is first at 5, with no S&M at none. First waves, step decisions, tiers and the function and process tables are unchanged. Checks: verify_part2 all pass (playbook 40/40), pytest 191/191.
- **P1 generated files changed** (sections/tables/tab_levers_position.tex, levers_position_macros.tex): lpGEFirstAll yes -> no (P1 CLAIMS check needs the coder's update), lpRatio 3.3 -> 0.99, lpRatioMin/Max 0.51/0.81 -> 0.97/3.94 (P1 text "below one at each" now false), new lpBasis, lpGEFirstAllSM, lpNGEFirstAllSM, lpNGEFirstNet, lpGEFirstNetList, lpNGACutFirstNet, lpNGEFirstNoSM, lpNNoGrowthSpend, lpNoGrowthSpendList, lpRatioAllSMMin/Max, lpMaintBase, lpNPositions. The table fits the page in a clean scratch build of P1.
- Still open: the P1 prose (editor), the CLAIMS check (coder), the Docs artifact and Word export above, and the engine's finance.alpha class (params.yaml now has class d; the engine keeps c with a note).
