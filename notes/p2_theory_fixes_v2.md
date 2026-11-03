# Paper 2 theory fixes, v2 (29 October 2026)

P2 theory agent. Scope: Paper 1 round-1 review items that fall on Part II (RA-1, RA-2, RA-5, FI-5, D-1, FT-20, flags 4 and 6), alignment with today's params commit, and the coordinator's note on the growth weight. Files edited: `part2/` (theory, proofs, bibs, generated macro tables), `code/examples/invoice_chain.py`, `data/examples/invoice_chain.yaml` (version string only) and its JSON, `code/verify_part2_*.py`, `code/playbook/levers.py` and `run_archetypes.py` (comments and table-note text only; no regeneration). Nothing in `sections/`, `paper1/`, `engine/`, the params YAML, the estimation code or the panel was changed.

## 0. Verify scripts (all rerun after the last edit)

| script | before this pass | now |
|---|---|---|
| verify_part2_accounting.py | 6c, 6g, 6j failing | 47/47 |
| verify_part2_acquirer.py | B4 failing | 80/80 |
| verify_part2_competition.py | 43/43 | 44/44 (F5 added) |
| verify_part2_core.py | 23c to 23e failing | 158/158 (23s2 added) |
| verify_part2_ext.py | B8 failing | 143/143 (J7, M1 added) |
| verify_part2_labor.py | 43/43 | 43/43 |
| verify_part2_playbook.py | 36/36 | 36/36 |
| verify_part2_product.py | (not recorded) | 94/94 (M1 added; D6, G5 rewritten) |
| verify_part2_regimes.py | C5, C6, G4, I3 failing | 85/85 (B12, M1 added) |

No check was loosened to fit the text. Checks whose content changed were rewritten because the result they test changed (RA-1, conditional case, B4) and say so in their names.

Engine tests (`engine/tests`, run read-only, not edited): 182 passed, 3 failed before the fix below; after it, `test_cross_impl.py` passes (20/20). Remaining failures are not from P2 theory files: `test_change_control::test_notes_unchanged_since_engine_update` (notes/acquirer_notes.md changed at 14:32 by the acquirer agent; engine owner must run `tools/check_sync.py --accept`) and `test_end_to_end::test_tier0_only_reports_wide_ranges` (an engine Monte Carlo width comparison; it reads no P2 file). `test_cross_impl::test_accounting_itgc_lines_and_timeliness` failed with a KeyError because it reads the old cost-plus-loss example from verify_part2_accounting.py; the script now exports clearly labelled LEGACY keys (`EXA["C_itgc"]`, `C_val`, `T_up`) and `best_g` that no check or text uses, so the engine's current `amin_design` can still be cross-checked until the engine pass replaces it (engine change E2).

## 1. RA-1: the accountability floor as a pass/fail ICFR constraint

Verified at primary sources (29 Oct 2026): AS 2201 at https://pcaobus.org/oversight/standards/auditing-standards/details/AS2201 (.02, .03, .62 to .64, A3, A7 and its note that "reasonable possibility" means reasonably possible or probable as in FAS 5); Regulation S-K Item 308(a)(3) at https://www.law.cornell.edu/cfr/text/17/229.308 (management may not conclude ICFR is effective if there are one or more material weaknesses); FAS 5 para. 3 at https://storage.fasb.org/aop_fas5.pdf ("remote": the chance is slight; PDF text partly garbled, the definitions legible).

| location | old | new |
|---|---|---|
| theory_accounting.tex intro paragraph | floor set by a cost-plus-expected-loss trade-off | the floor is a constraint: a design is admissible only if no in-scope control objective is left with a reasonable possibility of an unprevented, undetected material misstatement |
| ass:acct-layers (l. 157) | layers with miss rates and one common-mode term | objectives o with N_o opportunities, shared cause p^cm_0, per-type common mode p^cm_x(kappa_itgc) nonincreasing in ITGC quality, consequence cost L_mm (restatement, remediation, audit, cost of capital, litigation, clawback), not traded against cost |
| new paragraph after it | | independence is an assumption; automation complacency (Parasuraman and Manzey 2010) and correlated model errors (Kim et al. 2025) |
| def:acct-admissible (new, l. 163) | | Pi_o(d) = 1 - (1 - P_o(d))^{N_o} <= eps_bar, i.e. P_o <= P_bar_o = 1 - (1 - eps_bar)^{1/N_o}; eps_bar is the firm's operational reading of "remote"; no standard sets a number; illustrative 5% and 1% |
| prop:acct-amin (l. 169), renamed "The accountability floor as an ICFR constraint" | a_min = min over designs of cost + N L P | (a) a_min = min cost over admissible designs, no N L P term; (b) minimal depth n_min = ceil(ln rho / ln p); (c) common-mode floor: a type whose p^cm alone exceeds P_bar is never admissible however deep; (d) the residual expected consequence is reported, not priced into a_min; (e) ITGC quality lowers p^cm and can make a cheaper design admissible; (f) the cost-plus-consequence optimum is admissible only by coincidence |
| example after it (macros acctAmin*) | cost-loss optimum 1 human + 2 AI layers, $1.02 million | eps_bar 5%: 1 human + 1 AI, $755,000, annual miss 3.1%, residual expected consequence $310,000; eps_bar 1%: 1 + 2, $805,000, 0.7%, $67,000; all-AI on one provider never admissible (floor 11.3% a year); human-only inadmissible at 1% (4.7%); three human layers admissible at 5% (5.0%, $1.50 million); cost-plus-consequence optimum 1 + 2 at $872,000 |
| ITGC example | | weak change management (p^cm_AI 0.02): at 1% the cheapest design is 2 human + 1 AI, $1.25 million; effective ITGCs are worth $450,000 there, more than the line of $205,000 |
| prop:tasks-aggregate(a) in theory_core.tex (l. 495) | a_min mapped from the cost-loss minimum | a_min from the admissibility condition; residual consequence not in a_min |
| proofs_accounting.tex, proof of prop:acct-amin | cost-loss argument | (a) to (f) rewritten; checks 5a to 5j |

Scoping (def:acct-scope, already in place) unchanged in substance: processes, systems, integrations and policies that affect timeliness, accuracy and completeness are in scope, and an AI agent performing an in-scope step is an in-scope application with ITGCs.

## 2. ICFR cost lines (flag 4) and FT-20

Decision. P2 prices the ICFR retest at a forced model upgrade at KPMG test effort: 10 controls per application (round 2, Section 5.5; class d) x 16 hours per control test (KPMG 2025 SOX Survey, n = 146, FY2024; class b) x $150 an hour (the engine's itgc_setup basis; class d) = C_val = $24,000 per upgrade, against the engine's illustrative C_val of $100,000 (about 42 control tests per upgrade, which the survey does not support). All other unit costs are the engine's (c_acc $2,000 per identity or permission, c_chg $2,500 per change, c_ifc $10,000 per interface).

| line | engine C_val ($100k) | P2 C_val ($24k) |
|---|---|---|
| invoice application (3 ids, 12 permissions, 24 changes, 4 interfaces, ops $55k, T_up 1.22) | $267,000 | $205,000 (upgrade term $82,000 -> $20,000) |
| reference application (1, 4, 6 changes, 1 interface, ops $20k) | $137,000 | $75,000 |
| reference application at the engine's default counts | $150,000 | $88,000 (within 10% of the $80,000 target) |
| PV of upgrade retests (invoice) | $237,000 | $57,000 |
| ITGC NPV / NPV after | $0.53M / -$4.44M | $0.40M / -$4.16M |

The invoice line remains above the $80,000 target [$16,000, $350,000] (KPMG 2025, assumptions_round2 Section 5.5) because it has 24 changes, 4 interfaces and the top operations cost; it sits at position 0.56 of the range, and the text says why. FT-20 is resolved by definition (ass:acct-itgc, l. 204, and the "each cost is counted once" sentence): a forced upgrade appears in three non-overlapping lines, the functional regression suite in W (reval_share of the build), the change ticket in c_chg n_chg, and the re-testing of the controls the application performs in C_val. prop:acct-itgc(b) and its proof were rewritten (revealed preference; g(n) = (n - 1)^+ C). Checks 6c0, 6c1, 6c to 6j.

## 3. Invoice example: the conditional case (flag 6)

Problem: the conditional case capped targets at q_cap 0.988, above r_bar_high 0.98, so the "cap" raised targets. Redesign (code/examples/invoice_chain.py, data version '2026-10-29c'): r_bar_high is human parity (APQC 98% error-free disbursements via Fraxion; Medius 97.5% first-time-right; class b range 97.5% to 99.5%); the cap is min(r_bar_high, q*), where q* (98.8%) is the highest common target that capture, matching and approval meet at the detection rate; a cap never raises a target, and only approval (prior 99%) is relaxed, to a residual equal to the human error rate. Inputs unchanged (no retuning). Also fixed a bug: Chain shared and mutated the step dicts across instances.

| result | old | new |
|---|---|---|
| cap | 98.8% | 98% (q* 98.8% as sensitivity) |
| integration W at readiness 0.9 | -$54,000 | -$5,500 (-$14,000 with the cap at q*) |
| best pair (capture + matching) | -$9,200 | +$6,600, the best set (-$1,500 at q*: sign is fragile) |
| best first step pays from readiness | 0.916 | 0.889 |
| iota*_N | 0.948 | 0.905 |
| chain feasible from readiness | 0.89 | 0.65 |
| W at iota_N (0.8) | | -$18,000 below, -$109,000 above, a drop of $91,000 |
| Xi range | 0.77 to 0.99 | 0.77 to 0.87 |
| NPV / W / W before run | -$3.90M / -$213,000 / $116,000 | -$3.76M / -$164,000 / $165,000 |
| capture and matching reach target at default catch | | above readiness 0.959 and 0.994 |

Part of the change in levels is today's params commit, picked up on regeneration (e.g. b_bar 0.85 -> 0.67). theory_core.tex l. 112 (default verdict and conditional case), l. 182 (process example), l. 224 (readiness), l. 442 (approval target); checks 23c, 23d, 23e, 23g rewritten, 23s2 added. Signs reported as they come: the pair now pays at 0.9, by a small margin that reverses at the q* cap.

## 4. Common mode (RA-2, FI-5)

- ass:ext-commonmode (theory_ext.tex l. 461): nu^cm = nu^out + nu^chg(kappa_itgc), with change-management ITGCs (pinned versions, testing before promotion, rollback) lowering nu^chg.
- Kim, Garg, Peng and Garg (ICML 2025; https://proceedings.mlr.press/v267/kim25e.html): 0.60 is P(same wrong answer | both wrong) on HELM (71 models, baseline 1/3), not P(B wrong | A wrong), which is not reported; text (l. 465) now says so and treats H as a lower bound on effective concentration.
- prop:ext-commonmode(f) (new): change management lowers the mean by -nu^chg'(kappa) T_con [X + H X^2/(2 Y_f)]; worth more under concentration and slow containment; the same controls lower p^cm in prop:acct-amin. Proof added to proofs_ext.tex.
- Full automation: c_err must be evaluated at the catch rate of the review that remains (AI reviewer net of shared errors, or none), prop:tasks-cerr(c) (new, theory_core.tex l. 456, proof in proofs_core.tex); invoice: no-review error cost $1.27 per invoice, $152,000 a year.
- Ext check B8 fixed: 0.31 points at 2025 prices (0.62/0.41/0.26 by horizon), not 1.0.

## 5. Pass-through: P2's central value

Decision: P2's central industry pass-through is 0.5, with scenarios 0 and 0.7 (class b anchors): Choi (Analysis Group, Apple-funded, no control group) 2025, price cuts on 9% of products after a ~10-point cost cut (pass-through near zero, short run, differentiated software); Ganapati, Shapiro and Walker (AEJ Applied 2020, verified at https://www.aeaweb.org/doi/10.1257/app.20180474): about 70% of energy-driven cost changes passed through; Benedek, de Mooij and Wingender (IMF WP 15/214): about 100% (standard rate) and 30% (reduced rate). Why: the lemma's n_c/(n_c + 1 - e) is a homogeneous-Cournot benchmark, 0.8 at four firms and at least 0.75 at three or more, above every software or industry-wide anchor, and the engine's own scenario set {0, 0.5, 0.7} does not contain it. dur = 1 - phi(1 - HHI) is kept with the measured value; within the model 0.5 and 0.7 at four firms correspond to curvature e = -3 and -0.71.

New paragraph "Calibration of the industry pass-through" in theory_competition.tex after the cor:ext-game-engine example; check F5. At HHI 0.25: dur 1.0 / 0.625 / 0.475 (phi 0 / 0.5 / 0.7) against 0.40 at Cournot; priv 1.75 / 1.66 / 1.62 against 1.60; the example bundle's NPV^dur $0 / -$7.5M / -$10.5M (Cournot -$12.0M) and NPV^priv $15.0M / $13.1M / $12.4M: it stays defensive at every scenario (boundary at phi = 0). Tables of the corollary remain the linear-demand benchmark. Playbook: prop:playbook-rank(d) adds dur = (1 + HHI)/2 at 0.5; the playbook text and table note say the engine's 0.40 is the derived Cournot value and that 0.625 at the central pass-through can only raise the cost-of-revenue lever's rank. Bib entries copied from paper1/refs_additions_v2.bib into part2/refs_competition.bib.

## 6. psi for owned compute

Convention: psi = 1 for domestic servers acquired after 19 January 2025 (100% bonus depreciation, IRC 168(k) as amended by P.L. 119-21 sec. 70301), unless the firm elects out (168(k)(7)); a transitional election to deduct 40% (60% for certain property) for property placed in service in the first taxable year ending after 19 Jan 2025 (168(k)(10)); servers used predominantly outside the United States fall under ADS (168(g)(1)(A)) and get no bonus (26 CFR 1.168(k)-2(b)(2)(ii)(B)), so psi < 1 and the capital hurdles are multiplied by Upsilon = (1 - psi tau)/(1 - tau).

Sources and what was read (29 Oct 2026):
- IRS Notice 2026-11, https://www.irs.gov/pub/irs-drop/n-26-11.pdf: Sections 2.02(1), 2.05, 3.07, 4.03 (read in full for these sections).
- 26 U.S.C. 168 at LII, https://www.law.cornell.edu/uscode/text/26/168: (e)(3)(B)(iv), (i)(2)(A) (computers are five-year property), (g)(1)(A) read; subsection (k) itself not reached.
- 26 CFR 1.168(k)-2 at LII, https://www.law.cornell.edu/cfr/text/26/1.168(k)-2: (b)(2)(ii)(B) (ADS property ineligible).
- uscode.house.gov (client error), congress.gov and govinfo (truncated), curl (proxy 403): failed; the statute's (k) text, including (k)(6) and (k)(10), is therefore taken from the Notice.

Applied: theory_accounting.tex Tax paragraph (servers sentence, cites irs2026notice202611, usc2026sec168, cfr2026sec1168k2) and prop:acct-tax(d) ("including domestic servers unless the firm elects out"); theory_ext.tex servers sentence; theory_regimes.tex (owned capacity K: all values before tax; with psi = 1 the going-concern capital tests hold after tax unchanged; Upsilon for servers abroad or after an election out; zeta^pe is before tax); theory_playbook.tex prop:playbook-rank(f) and the third reading; playbook table note; code/playbook/levers.py comment at the capital hurdles. Hurdles: with psi = 1 the after-tax hurdles equal the stated ones (savings and capital charges both scale by 1 - tau), so no hurdle value changes; for foreign servers they rise by Upsilon.

Params note (not changed): engine defaults.yaml finance.psi_equipment says "40 percent if the firm elects out"; electing out under 168(k)(7) gives no bonus (MACRS), and 40% is the 168(k)(10) transitional election. Wording fix needed (E5).

## 7. Previously failing checks

- accounting 6c, 6g, 6j: lines recomputed from the engine's units (`_engine_accounting_units`) with the P2 C_val (Section 2); 6c0 and 6c1 check the engine-unit and KPMG-unit lines separately.
- regimes C5, C6, G4: Case R restated with today's realized share b_bar_p = 0.67 (engine default; was 0.85): IRR 15.0% (16.2% annual) -> 9.1% (9.5% annual), barely above the public cost of capital 8.93%; +$388,000 -> +$12,000 at r_w; -$226,000 -> -$471,000 at the hurdle; minimum horizon 7.0 -> 9.9 years (just inside its ten-year life); a permanent saving would earn 15.3%. Carve-out: minimum horizon from 7.0 -> 2.8 became 9.9 -> 3.7 years. Signs unchanged; the margin at r_w is now thin.
- regimes I3 (pre-existing): the playbook text used \mathfrak w for the public weight's pressure, where I3 requires inverting eq:reg-Xmy at the public preset; theory_playbook.tex now says "recover the same firm's weight without the pressure by inverting eq:reg-Xmy at the public preset of Table tab:reg-presets".
- acquirer B4: the text said the integration's technical debt C_spec exceeds the gross saving; it is below it. Now: pooling alone can make the process save money, but never more than $20,900 a year and only above 11.2 sharing businesses; with a rebuild, above 2.1.

## 8. Growth weight (D-1) and the coordinator's note

Withdrawn: the 7 to 13 estimate. Evaluation points X in {2.5, 5, 9}, generated as macros by the verify scripts (tuple `XBOUNDS = (2.5, 5.0, 9.0)` in verify_part2_acquirer.py, verify_part2_ext.py, verify_part2_product.py, verify_part2_regimes.py; macro files part2/tables/{acquirer,ext,product,regimes}_macros.tex; check M1 in each confirms the macros match). The coordinator's numbers (alpha(X - k) by method from 0.05 to 10.1; X - k from below 1 to about 12 at alpha in [0.25, 0.45]) are reflected in theory_ext.tex l. 146 ("bounds by method run from below one to about twelve for X - k"). The spend ratio 3.3 stays as the playbook's calibration input; lem:playbook-calib(c) no longer calls it Part I's range, and a new paragraph says it identifies only alpha(X_hat - k) and is not an estimate of the owner's weight.

`% XBOUNDS` locations (each a LaTeX comment; text after a comment was checked not to be swallowed, see Section 10):
- theory_ext.tex l. 2 (macro input), l. 175 (support example: retention break-even 31 / 15.5 / 8.6 basis points at X = 2.5 / 5 / 9; no sign flip).
- theory_product.tex l. 2, l. 145-146 (feature portfolio: agent vs copilot rank flips at X = 7.1, so copilot-first only at 9; best set unchanged), l. 228 (dilution: D_m/Delta G = 3 pays at 5 and 9, fails at 2.5 and at every weight below 3), l. 257 (breakpoint table growth rows scale with X), l. 290 (table note).
- theory_regimes.tex l. 2, l. 135 (prop:reg-weight example: growth-engine saving worth 0.24 / 0.64 / 1.48 points against the overhead cut's 1, so overhead first at 2.5 and 5; earnings pressure reverses the public ranking only for X in (6.85, 8.91), which contains the model's 8 and none of the three points; sponsor ranks overhead first at every weight, and at 2.5 its weight is above the public owner's from three years before exit), l. 218 (LBO: loss from moving to the sponsor's weight 0.00 / 0.51 / 3.30 points; at 2.5 the sponsor's mid-hold weight 2.70 is the higher one, so a take-private would raise growth spend).
- theory_acquirer.tex l. 80 (acquirer agent's, unchanged).
- theory_playbook.tex l. 22 (calibration paragraph: which comparisons depend on the level of X_hat), l. 71 (e: dilution rule at 2.5 / 5 / 9), l. 73 (g: k^acq < X_o: Eventbrite 1.7, AOL 2.3, Vimeo 3.2 all pass at 5 and 9; at 2.5 Vimeo fails; below 2.3 AOL fails too), l. 101-103 (items vi, vii, viii to avoid), l. 124 (sponsor and permanent-acquirer switches, conditional on the level; a lower level turns more archetypes toward the growth engine), l. 125 (elite's no-switch under a sponsor rests on G_i and on the level of X_hat).
- proofs_playbook.tex appendix prose before tab:playbook-grid: public, dual-class and family rankings are level-free; sponsor, VC and permanent-acquirer rankings are conditional on X_hat - k = r_sigma/alpha.
- code/playbook/levers.py: comments at regime_weights and at acq_max_price_score.

Flips below 2.5 (stated in the text): dilution plan fails below X - k = 3; AOL's price fails below 2.3; at 2.5 the overhead cut outranks the growth engine in the reg-weight example and the sponsor's weight exceeds the public weight from three years before exit. The levels methods (alpha(X - k) of 0.05 to 0.43) would put every one of these on the "fails" side.

## 9. RA-5 regulatory facts

- SR 26-2 / OCC Bulletin 2026-13 (17 April 2026) supersede SR 11-7 (and SR 21-8; OCC 2011-12, 2021-19, 1997-24 and the MRM booklet); attachment footnote 3 puts generative and agentic AI models outside scope. Verified at https://www.federalreserve.gov/supervisionreg/srletters/sr2602.htm and https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-13.html. Added to rem:acct-evidence (theory_accounting.tex l. 114), theory_product.tex intro (l. 4), literature_modern.tex security and regulation paragraph (l. 25).
- Regulation (EU) 2026/1744 (in force 27 July 2026): Annex III high-risk obligations apply from 2 December 2027, Article 6(1)/Annex I from 2 August 2028 (recitals 40 and 46 read at https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32026R1744; the operative amendment of Article 113 not reached). Applied: theory_ext.tex Assumption (ii) (l. 22: a plan whose horizon runs past those dates should treat such use cases as class 2), theory_product.tex l. 4, theory_labor.tex (informing workers' representatives), literature_modern.tex.

## 10. Literature corrections and other fixes

- lit_pass_v2 Section (a) at part2 locations: Demirer et al. (-1.11 is a within-model elasticity across providers of identical open models) at theory_core.tex l. 76, theory_product.tex l. 160-164, literature_modern.tex; ICONIQ (2025 realized, 2026 and 2027 projected; margins on AI products sold to customers) at theory_product.tex l. 179; Hampole, Bonney (2024, 2026), Terry, Gundlach, Kwa (143-day doubling), Census BTOS wording and Allen et al. at the lit pass's P2 locations (literature_modern.tex, literature_part2.tex l. 11, theory_core.tex l. 182 and 224, theory_regimes.tex, theory_ext.tex). Corrected bib entries copied from paper1/refs_additions_v2.bib into part2/refs_modern.bib.
- Not done (outside my files): the ICONIQ entry Part II resolves is `iconiq2026state` in the root `refs.bib`, which still has the old note and the "www" URL; the lit pass's corrected entry is in paper1/refs_additions_v2.bib. Whoever owns refs.bib should replace it.
- Stale Part I reference: Part II cited Part I's Table tab:gap, which paper1/paper1.tex no longer contains; theory_playbook.tex, part2/tables/playbook_table.tex and code/playbook/run_archetypes.py now describe the bands and sample directly.
- LaTeX comment bug found while building: three `% XBOUNDS` comments inserted mid-line in theory_playbook.tex and two in theory_product.tex commented out the rest of their source lines (up to 1,650 characters each, including the second to fourth "readings" of the playbook and a paragraph of the product section). Fixed by ending the line after each comment; all part2 files were scanned for any other long text after a mid-line `%` (none).

## 11. Engine changes needed (for the engine pass; not made)

- E1 Shock model double count (ISSUES 9): unchanged by this pass; still to do.
- E2 formulas.amin_design: replace the cost-plus-consequence minimum (N_mm L_mm P term) by the constrained minimum over admissible designs (def:acct-admissible: Pi_o <= eps_bar with N_o, shared cause p^cm_0, p^cm_x(kappa_itgc)); report the residual expected consequence separately; add eps_bar as a setting (no standard; 5% and 1% illustrative). Then rewrite engine/tests/test_cross_impl.py's a_min block against verify_part2_accounting.best_admissible and delete the LEGACY keys.
- E3 accounting.C_val: $100,000 -> $24,000 (10 controls x 16 h x $150), range about [$12,000, $48,000]; basis KPMG 2025 (hours, class b), counts and rate class d; document FT-20 (regression suite in W via reval_share, change ticket in c_chg, control re-testing in C_val).
- E4 competition.phi_ind: when not measured, use 0.5 (class b, Section 5) rather than the derived n_c/(n_c + 1 - e), which lies outside the engine's own scenario set; keep the derived value as a reported benchmark. The playbook's durable share (0.40) and every cost-of-revenue lever value then change; regenerate code/playbook/run_archetypes.py outputs afterwards.
- E5 finance.psi_equipment wording (Section 6); add the foreign-server case (ADS, no bonus, Upsilon) to owned compute; confirm capital hurdles are applied before tax or with psi = 1.
- E6 XBOUNDS consumers: engine levers.py line 140 ("acquisitions priced above X_o ... lowers the charged score") and code/playbook/levers.py acq_max_price_score report a sign that depends on the level of X; report them at X in {2.5, 5, 9} too. finance.X_default 8 [5, 13] cites "roughly 7 to 13", now withdrawn; per round 2 it should widen (round 2 proposed [3, 13]; the sample audit implies X - k from below 1 to about 12).
- E7 MODEL_RISK.md line 3 cites SR 11-7, superseded by SR 26-2 / OCC 2026-13, which also excludes generative and agentic AI; impute.py eu_ai_act_nexus and any high-risk date logic should use 2 Dec 2027 (Annex III) and 2 Aug 2028 (Annex I) under Reg. (EU) 2026/1744.
- E8 Full automation c_err: evaluate at the remaining review's catch rate (AI reviewer net of shared errors, or none), prop:tasks-cerr(c); and nu^cm = nu^out + nu^chg(kappa_itgc) in the common-mode cost.
- E9 Invoice example JSON and macros are regenerated (version 2026-10-29c); engine tests test_paper_examples, test_playbook and test_accounting pass against them.

## 12. Unverified or open

- Statute text of 26 U.S.C. 168(k), including (k)(6), (k)(7) and (k)(10), not read directly (taken from IRS Notice 2026-11).
- Article 113 as amended by Reg. (EU) 2026/1744: dates taken from recitals 40 and 46 and the Parliament and Council documents.
- APQC primary values (98% error-free disbursements, 0.8% duplicate or erroneous payments) seen only through Fraxion's blog; Medius figures are vendor data without sample or method.
- P(B wrong | A wrong) for different providers: not measured by Kim et al. or any source found.
- eps_bar: no auditing or SEC standard sets a number for "remote"; 5% and 1% are illustrative.
- FAS 5 PDF partly garbled; the definitions of probable, reasonably possible and remote are legible.
- "Bounds by method from below one to about twelve" restates notes/sample_audit.md Section 4; it depends on Part I's rewrite reporting those methods.
- The 10 controls per AI application and the $150 an hour are class d.
- Engine test failures in test_change_control and test_end_to_end are not from P2 files (Section 0).

## 13. Conclusions whose sign or rank changed

- Invoice: the capture-and-matching pair now pays at readiness 0.9 (+$6,600, best set; -$1,500 if the cap is q*); integration loss shrinks from -$54,000 to -$5,500; the chain is feasible from 0.65 (was 0.89).
- Accounting: the floor design depends on eps_bar (1 + 1 at 5%, 1 + 2 at 1%), not on the consequence cost; all-AI designs on one provider are never admissible; human-only is inadmissible at 1%.
- Regimes: Case R's IRR falls from 15.0% to 9.1%, still above the public cost of capital (thin margin); the reg-weight ranking is overhead-first at X = 2.5 and 5 and growth-engine-first at 9; earnings pressure reverses the public ranking only for X in (6.85, 8.91); at X = 2.5 a take-private raises growth spend from mid-hold.
- Acquirer B4: pooling alone can now make the integration pay (above 11.2 businesses, at most $20,900 a year).
- Product: the copilot outranks the agent only above X = 7.1; the dilution plan fails at X - k = 2.5.
- Playbook: acquisition test fails for Vimeo at X_o = 2.5; the dilution test fails at 2.5; sponsor, VC and permanent-acquirer rankings are conditional on the level of X_hat.
- Pass-through: no classification changes (the example stays defensive at every scenario); durable shares rise.
- Ext: retention break-even 31 / 15.5 / 8.6 basis points at X = 2.5 / 5 / 9 (no sign flip); B8 0.31 points, not 1.0.

## 14. Build

Test assembly (all part2 sections, literature files, validation_backtest.tex, all proofs, the playbook tables including playbook_processes.tex and playbook_steps_full.tex, longtable; Part I labels imported with xr-hyper from paper1/paper1.tex): 240 pages, 0 errors, 0 undefined references or citations, no multiply defined labels or citations, no BibTeX warnings. Assembly file and steps: part2/_test_assembly_note.md.
