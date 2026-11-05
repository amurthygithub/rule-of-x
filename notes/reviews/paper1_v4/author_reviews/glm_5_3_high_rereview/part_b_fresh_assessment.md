# Part B — The revised paper assessed afresh (4 November 2026 build)
*This is the panel's independent fresh assessment of the revised version, at the standard of
the first review. Written and saved with its SHA-256 hash recorded in README.md BEFORE any
restricted material (other reviewers' folders, their response files, the joint response) was
opened. Panel: Lead + five specialist contexts (A theory/Lean, B empirics, C accounting/case,
C2 citations/legal/tax, D execution/stress/S12), same single-LLM family in one harness — not
independent human experts; the deterministic evidence (scripts, fetches, stored outputs) is
the strong kind and was re-executed wherever material.*

## B.1 Theorems, proofs, and the Lean formalization

- **Static and dynamic theory: re-verified on the new build.** `verify_theory.py` run by the
  panel: 116 checks PASS (one apparent 15p failure was a scratch working-directory artifact;
  confirmed clean from the repo root). The round-1 verdict stands: the closed forms, the
  envelope results, the budget propositions, the free-entry and control-standard results are
  correct as stated; Proposition 2's dependence on the unproved verification hypothesis (H) is
  now stated at ~16 sites including the proposition's title, with one editorial remnant
  (§3.5's parallel sentence lacks "(H)" while its §7.4 twin has it).
- **New S4 (Lean 4 formalization): genuine at source level.** 35 main theorems in
  `formal/RuleOfX/*.lean` map faithfully to the paper's Lemma 1–2, Lemma 3, Lemma 4, Prop 1 and
  the score/capital results; `Axioms.lean`/`Imports.lean` show standard Mathlib imports only —
  no `sorry`, no custom axioms, no `native_decide` in any file. The two tightenings the
  formalization forced are implemented in Lean AND reflected in the paper: σ*=0 for X ≤ k
  inside the score lemma's cap condition (Lemma 2 preamble), and a measurable moving intercept
  in Proposition 1(c). S4's text describes the formalization accurately, including the honest
  note that the induced-path construction postdates the paper's second internal audit.
  **Limitation (disclosed):** no Lean compiler in this environment — compilation was not
  verified; the audit is a source-level fidelity review by specialists who re-derived the
  mathematics in round 1.
- **Theory diff discipline:** `git diff 62e574b..eb7537b` on `sections/model.tex`,
  `sections/appendix_proofs.tex`, `part2/proofs_core.tex` shows only the documented fixes
  (U-shape sentences, (H) qualifiers, after-tax parenthetical, novelty rephrase, two
  tightenings); `proofs_core.tex` is unchanged. Nothing undocumented moved.

## B.2 Estimation, inference, and the sample

- **The re-estimated empirical core again replicates completely.** New Table 2: 164/164 cells
  reconcile with committed outputs (Ψ0.90 −0.20 GAAP / −0.17 cash; P95 fall −11.9 / −12.6;
  anchor 14 firm-years of 7 firms; Romano–Wolf p 0.075 with its MC standard error now
  disclosed; 1,732 firm-years / 284 firms; all acquisition-flag and growth-count cells).
  The **full 999-replication bootstrap pipeline was rerun by the panel on this commit**
  (Part C): regenerated tables, anchors, and `paper_stats.json` byte-identical; frontier
  slopes at machine epsilon (6.7e-16); the only deviations anywhere are SFA maximum-likelihood
  fields (≤8.3e-5; 1,818 of ~6,500 fields, all `sfa_detail`) and a cosmetic `/meta/workers`
  field — the same optimizer-path noise as round 1, now with a printed reproducibility caveat
  (row M18).
- **R2 (principal business) on the whole main sample: sound and pre-specified.** Business
  descriptions for all 293 core registrants are archived in the repo; the keyword rule's lists
  are unchanged in git between the relevant commits (pre-fixation as claimed); the panel's
  classifier rerun reproduces exactly the 8 firms / 56 firm-years removed; the reported
  Cohen's κ = 0.952 against the two blind readings reproduces (0.9525; note the panel's first
  pass used a multi-class agreement statistic — the paper's binary-verdict κ is the right
  object). The resulting sample changes (284 firms; slope −0.20/−0.17; p95 fall −12.6 cash;
  anchor 14 firm-years; 2036 score 58) are consistently propagated through abstract, summary
  box, §5, §7 and the supplement.
- **New S11 (specification curve): a genuinely strong addition.** Table S19 reproduces
  cell-by-cell from the stored 155,328-row specification table; the pre-specification claim is
  credible (timestamped design.md of 3 Nov 14:36 UTC with corrections logged); the forward-
  pairing variant requested in round 1 (row M9) is computed under all four views and the whole
  grid (P95 falls −11.1/−11.1; slopes −0.29/−0.24; no sign changes; the E2/imputation 60%
  cells correctly marked undefined at 15/26 pairs); leave-one-firm-out is included. The curve
  honestly narrows the paper's own claims (the steepening's interval, the netted anchor) —
  no defect found.
- **Capitalized-software correction: complete trail.** 1,213 firm-years scanned, 121
  candidates, 109 kept (23 firms; median 1.6%, max 9.2% of revenue), all recorded in
  `notes/data_audit/` with the panel's verification of the panel-side flag (109 rows).
  40 seeded firm-years were checked against face statements by the author; the panel did not
  re-read the filings (recorded as not-checked).

## B.3 The joint-parameter stress test (S10) and its transcription

- **Design:** 1,000,000 Latin-hypercube draws per seed (two seeds) over a 51-dimension box of
  the stated ranges, 100,002 corners, a vertex search, Sobol indices on 65,536 base samples.
  Run on the author's machine; the panel audited the stored JSONs (both seeds), ran
  `mc_claims.py --verify-only` (87/87), and re-derived the load-bearing numbers from stored
  draws (ST-1's 19.6–94.5% vertex bounds; ST-6's 57.6% share of draws, 57.4% by panel recompute,
  within convention noise; ST-5's threshold "about 13%" = 12.3% by recompute, covered by
  "about").
- **Transcription discipline:** all six conditioned claims (ST-1..ST-6) are now stated with
  their conditions at every appearance (abstract, summary box, M 1, M 7.2/7.3/7.5, M 9) —
  verified appearance-by-appearance by two specialists independently.
- **One minor defect found (new):** S10's seed-stability sentence ("no lowest or highest value
  across the six headline statistics moves by more than 0.02 point") is contradicted by the
  author's own stored `seed_comparison` on its natural reading (PV-ratio max 79.44 → 74.42, a
  5.03 move; flow-crossing minimum 0.64 → 0.60). The *verdicts* are stable across seeds
  (69/69), which is what matters; the sentence overstates. **Minor; one-line reword**
  (e.g., "no verdict changes across seeds").
- **A second minor omission (new):** the accountability sub-box's finding that the example's
  floor reaches ~1.01% of revenue at the unfavorable corner (vs the band's 0.5–4.6%) is not
  transcribed into S10's summary. One clause.

## B.4 The three post-round analyses (S12)

- **S12.1 (valuation test): sound as a disclosed descriptive association.** Public float over
  revenue regressed on growth and margin with year effects and firm clusters (data:
  `dei:EntityPublicFloat` via the SEC frames API — retrieval verified); "one point of growth
  worth about 4.8 points of margin (90% CI 3.1 to 15.8); equal weights rejected" — all Table
  S20 cells match `notes/open_questions/valuation.json`; the text carries the proxy caveats
  (float/revenue is not a market multiple; the estimate is an association) and §8.6 points to
  it as the descriptive test. Not re-estimated from the raw panel by the panel (recorded).
- **S12.2 (cost of not automating):** internally consistent (the printed 53 decomposes as
  41.7 embedded + 11.6 in-flight ≈ 53.3); the construction follows the paper's pass-through
  scenario as stated.
- **S12.3 (what sets the payback):** "change capacity drops out of the payback while the
  program runs; the share of changes that create value sets it" — verified analytically AND
  by full recomputation of Table S22 from the stored stress-test draws (every cell matches).
  This also defuses round-1's stock-vs-flow concern (row GLM-11): capacity binds the pace of
  embedding but cancels in the payback statistic.

## B.5 Scenario framing, calibration, and the compute-share units fix

- The "central scenario, not a forecast" framing is preserved at every load-bearing site,
  including the plain-language abstract; the summary box discloses the joint-draw assumption
  ("uniform over the stated ranges, log-uniform for compute per dollar of labor, an
  assumption").
- **The units fix is right and complete:** the compute-share floor was previously a cost per
  dollar of labor misread as a share of revenue; it is now 1.2% of revenue (2% per completed
  task × 60% labor share), consistent across M 7.2, S2.8 (which honestly retains the
  success-only 0.6% figure), Table S11 (per-dollar-of-labor units), the assumptions register,
  and the stress-test box (κ drawn log-uniform 0.02–1.0). No stray "1%" reading survives
  anywhere in the two PDFs. The panel re-derived 1.2%, the 28% threshold low end (28.5%
  unrounded) and the 23% accountability-only variant. The threshold's printed low end is
  unchanged (28%) because the old and new floors give 28.4% vs 28.5% — the correction changes
  the concept and the label, not the digit.

## B.6 Citations, legal and tax claims

- **Round-2 spot-checks at primary sources (9 items):** §174A R&E expensing (deduction when
  incurred; ≥60-month election; tax-years-after-2024 applicability), the §168(k) chain
  (P.L. 119-21 §70301 100% allowance; "after January 19, 2025"; (k)(7) elect-out; (g)(1)(A)
  ADS; (k)(2)(D) exclusion), 26 CFR 1.168(k)-2(b)(2)(ii)(B), IRS Notice 2026-11 (exists),
  CAMT §55(b)(2)(A) 15% + §59(k) thresholds (including the foreign-parented-group $100M
  nuance — exactly right), SOX §404(a)/(b)/(c) with the EGC carve-out, GAO-23-105384 (16% in
  2014, 9% in 2018 — verbatim), Italy IRES 24%/IRAP 3.9%. **Nothing incorrect; the items the
  author labels "imprecise, fixed" are indeed now precise.** Access-limited (flagged): the
  ASC 230-10-45-17 sub-letters (FASB paywalled; Wayback down) and the first-annual-report
  §404(a) grace sentence.
- **New citations this round:** Wood (2025) (Crossref record verified; content claim
  record-only), Hokstad & Rausand now carries a verified Springer DOI (strengthened vs
  round 1), `dei:EntityPublicFloat` (SEC frames API verified), the Bending Spoons 424B4
  accession (EDGAR-verified). **No nonexistent works or misattributions found.** Minor note:
  S10 uses Latin-hypercube and Sobol methods without methodological citations (optional).
- **One carried residual:** Roche & Tandon (2021) remains the only §2.2 practitioner fact the
  panel could not check at a primary source across two rounds (McKinsey 403 at every route;
  no archived copy shipped). The author's verification record is specific and pre-dates the
  review; the suggested fix is to put the article's own summary numbers in the bib note or
  archive the fetched page.

## B.7 The plain-language abstract

Audited number-by-number and condition-by-condition by three specialists independently:
every statistic in the abstract ties to Table 2/5, §7.2 or S5.1 at the re-estimated values;
every load-bearing condition survives — (H), central costs, fixed prices, mature/asset-light,
the compute-share range, pass-through, "a central scenario, not a forecast", the score after
in-flight costs (53), and "from sampling alone" for the [54, 62] interval. Two benign
simplifications were noted and accepted ("well above three" tightens the body's "well above
the screening weight" to a sufficient condition — true; the case-study numbers left the
abstract entirely — accurate where they live, in M 1 and §6). The abstract is 1,916 characters
against the repo gate's 1,920 limit. **Verdict: the plain-language rewrite kept the paper's
honesty.**

## B.8 Consistency of abstract, text, supplement, and code

- Text↔macros↔outputs: `paper1_macros.py` regenerates all 1,730 macros byte-identically and
  enforces the abstract length; `supp_extensions.py` passes 27/27 S12 text checks;
  `verify_part2_acquirer.py` passes 90/90 (new checks verify every case figure against both
  shipped filings with SHA-256 and page anchors); the full estimation pipeline rerun is
  byte-identical where deterministic (Part C).
- The round-1 record-keeping defects are fixed (stale artifacts regenerated or retired with
  labels; the response letter's own numbers are superseded by the PDF where the rerun moved
  them, exactly as the letter's caveat states).
- **Round-1 panel errors, corrected on the record:** the panel's re-review found the author
  right and the panel wrong on four round-1 items (the Lee sample count — accepted "not
  valid" after independently fetching the published AFL page; the version-drift direction;
  the "≈2.3" truncated PV ratio — true value 2.104; the acceptance-test thresholds for the
  U-shape, and two smaller Holm-index errors). These are recorded in the response audit.

## B.9 New findings from the fresh assessment (severity, locator, fix)

| # | Severity | Finding | Locator | Proposed fix |
|---|---|---|---|---|
| NB1 | minor | AS 2201 bib note's paragraph list (".03, .16–.19, 36, …") omits .06 and the second note to .65, which the text now cites | refs_paper1.bib `as2201` note; main 8.5 p.70; Prop 5(b) p.30 | one-line bib edit adding .06 and .65 |
| NB2 | minor | S10 seed-stability sentence ("no lowest or highest value … moves by more than 0.02 point") contradicted by the stored seed_comparison (PV-ratio 79.44→74.42); the verdicts are stable (69/69), the ranges are not | supp S10 seed-stability paragraph; notes/mc_results seed_comparison | reword to "no verdict changes across seeds; the ranges move by up to X" |
| NB3 | minor | The accountability sub-box's unfavorable-corner floor (~1.01% of revenue) is not transcribed into S10's summary | supp S10; Table S18 amin sub-box rows | one clause |
| NB4 | editorial | §3.5's decision-weight sentence lacks the "(H)" qualifier its §7.4 twin carries | main 3.5 p.21 | add "under (H)" |
| NB5 | editorial | §3.5 retention clause conflates a 56% share with the 64% ratio from the worked example | main 3.5 p.21 | correct the fraction |
| NB6 | editorial | verify_theory.py duplicate check labels (15l/m/n used twice) weaken the paper's "checks 15g to 15m" citation | code/verify_theory.py section 15 | renumber |
| NB7 | editorial | Dead macro \KaSlack defined, unused | paper1/macros.tex | remove or use |
| NB8 | editorial | S5.1's H1 interest-paid clause still cites the prospectus (2026b) instead of the 6-K | supp S5.1 | re-cite |
| NB9 | editorial | A.6's new search-protocol sentence states the method and the no-log limitation but no search date | main A.6 | add the date range |
| NB10 | editorial | S7 could note that the shipped filing copies' SHA-256 pins validate the archived HTML, not a fresh EDGAR fetch (EDGAR re-serializes) | supp S7 data section | one sentence for re-fetchers |
| NB11 | residual | Roche & Tandon content unverifiable by the panel in two rounds | main 2.2 pp.8–9 | bib note with the article's own numbers, or archive the fetched page |

**Assessment:** the revised version clears the first review's bar. Every must-fix and
should-fix item was verified as fixed (several better than promised); the declined items are
defensible on the stated grounds (with one caveat recorded on GLM-17's wording and one
factual correction to the author's verification record on M12); the new material (Lean S4,
S10, S11, S12) is sound, reproducible where the panel could reach it, and transcription-
disciplined; and the fresh pass found only three minor and eight editorial items, none of
which affects any result. The paper's replication discipline now extends end-to-end:
byte-identical regeneration of tables, anchors, macros and the case-study checks, a
machine-checked formalization of the static core, a pre-specified specification curve, and a
million-draw joint stress test whose conditions are carried into every headline sentence.
