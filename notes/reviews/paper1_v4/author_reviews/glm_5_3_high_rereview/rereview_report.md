# Re-review report — "The Rule of 40 as a Price Line" (revised third version, 4 November 2026)

**Reviewer:** the same panel that produced the first review of 2–3 November 2026 (Lead +
five specialist contexts; see disclosure below). **Reviewed build:** main 87 pp.
(SHA-256 9e986eca…c55b) + supplement 72 pp. (1da73673…2b81), repo `rule-of-x` @ `eb7537b`
(branch `review-round-3`). **Inputs:** PROMPT.md, RESPONSE.md, the repo, and our own
first-round archive (in the repo under `notes/reviews/paper1_v3/author_reviews/glm_5_3_high/`).

## Verdict (one paragraph)

The revision clears our bar. All four must-fix and the one should-fix item of our first review
are verified fixed — several better than promised — and the author was right where we were
wrong on four round-1 items (the Lee sample count, the version-drift direction, the truncated
PV ratio, and the U-shape acceptance tests), all of which we concede on the record. The three
declined items are defensible on their stated grounds; of the two findings the author
classified "not valid," we accept both after independent re-verification; of the three
"partly," one is adequately covered (GLM-16), one is acceptable as far as it goes (GLM-10),
and one retains a small residual (GLM-17, the Roche–Tandon sentence, still the only §2.2
practitioner fact we could not check at a primary source in two rounds). The new material is
sound and reproducible where we could reach it: a source-level-faithful Lean 4 formalization
with standard axioms only; a specification curve that honestly narrows the paper's own claims;
a million-draw joint stress test whose six conditional results are transcribed with their
conditions at every appearance; and three post-round analyses whose tables we reproduced
cell-by-cell from committed outputs. The fresh pass found **three minor and eight editorial
new items, none affecting any result** (§B.9). We recommend release as an arXiv working paper
after the three minor fixes and the editorial sweep, and we would now also support submission
to a specialist journal (see Part D for the ranked conditions).

---

## Disclosure

- **Panel and model identity.** This re-review was produced by an AI referee panel: a Lead
  and five resumed specialist contexts from the first review (theory/Lean; empirics;
  accounting/case; citations/legal/tax; execution/stress), each a separate conversation
  context of the same single LLM family in one harness (platform model labels were unstable
  across the session; the author addressed this panel as "GLM 5.3 (high effort)"). We are not
  independent human experts and not independent model-family evidence; the strongest evidence
  in this report is the deterministic kind — scripts, reruns, fetched primary sources, stored
  outputs — which was re-executed by the panel wherever material, and which any reader with
  the repo can reproduce.
- **Date.** 4–5 November 2026.
- **Environment and tools.** Python 3.12.3; numpy 2.5.2, scipy 1.18.1, sympy 1.14.0, pandas
  3.0.3, statsmodels 0.15.0; git; pdftotext/pdftoppm; direct fetches of primary sources
  (SEC EDGAR with declared user agent, Crossref, LII/irs.gov/GAO, publisher pages where
  reachable). **Not available in this environment:** Lean 4 (S4 audited at source level only;
  no compilation claimed), LaTeX (`build_paper1.sh` not runnable; the text↔macro↔output
  reconciliation was done instead — the committed PDFs' numbers were checked against the
  committed tex/macros/outputs), pandoc.
- **Independence rule compliance.** Part B was written and saved with SHA-256
  `a6c16bf0f187ae88f18ba6ad7d5ef5a5cd963106305ec03223ecf964c05ee510` (recorded in README.md)
  BEFORE any restricted material was opened. After that: the Lead read the header and counts
  sections of the joint response (`response_to_outside_reviews.md`, ~60 lines, including a
  sample of DS rows) as a consistency check; it matches RESPONSE.md's dispositions and counts
  and changed no verdict. No other reviewer's folder or response file was read, and nothing
  restricted was used in any verdict.
- **The excluded registrant** was not recovered or named anywhere in this round's
  deliverables, per the prompt's rule.
- **Copyright.** No third-party full texts are reproduced; quotations are short with locators.

---

## Part A — Audit of the response (46 rows + ST-1 to ST-6)

Full verdict table: `response_audit.csv` (columns: id, our_status, your_verdict, evidence,
locator). Panel reports with per-row evidence are in `reports/` (R-A, R-B, R-C, R-C2, R-D,
R-Lead). Summary:

**Our five majors.** F1 (U-shape): **resolved** — all six corrected sentences match the true
profile (min v′ ≈ 5.08 at ~80% of the cap, rising to the never-spend multiple 5.833; sampled
9.1/7.2/5.4 unchanged), verified on the author's own solver and our independent method, with
the new verify_theory checks passing. We also **concede the acceptance-test dispute**: the
author is right that our round-1 test thresholds fail on the correct solution; our round-1
test (i) was internally inconsistent with our own table, and the author's recalibrated tests
pass. F2 (filings disclosures): **resolved** — the five sentences are corrected, Table 3's
annual organic rows recompute exactly from the filings (26.0/34.3; 21.1/23.4; 33.7/40.3), the
new panel-basis cash row is right, and the verification script now passes 90/90 with
page-anchored checks against both shipped filings. F3 (Nei et al.): **resolved** — citation
accurate, access level disclosed, "only" dropped. F4 (marker): **resolved** — gone. F5
(familywise consequence): **resolved** — the new §5.1 sentence's nine 18-test Holm values
reproduce exactly from stored p-values; we also accept the issue log's two corrections to our
round-1 arithmetic (the "loses 5%" misstatement and misindexed 20-test anchor values).

**Our minors.** All 18 rows resolved except: M12 (declined; the scoping is adequate — with a
**record correction**: the author's verification note claims our round-1 ledger never checked
the NUREG/CR-5485 conservatism passage; it did, verbatim, and we re-verified the archived
PDF), M14 (**we accept "not valid"**: the published AFL page, fetched independently this
round, says 1,756 — our round-1 finding verified the preprint and stated the suspicion too
strongly), M16 (partly, and the declined part is reasonable), M17 (declined, defensible — the
digest is in git history from the initial commit; the paper now discloses invertibility
plainly; the SIC-class remedy was rightly dropped).

**The GLM-numbered items (our round-1 open questions).** Resolved or adequately handled,
except GLM-17 (Roche & Tandon: specific dated verification record exists, but the claim
remains the one §2.2 practitioner fact we could not check at a primary source across two
rounds; proposed fix: bib note with the article's own numbers or an archived copy) and
GLM-10 (partly: the stress test gives the range of the expectation, 4.9–85.0%, not sample-path
dispersion — acceptable because the 41% is explicitly an expectation).

**The two "Not valid" rows.** Both accepted with independent evidence (M14 above; GLM-22: the
supplied round-1 PDFs were built 15:48 PST on 2 Nov, before the 19:30/19:55 commits — our
"supplied newer than committed" direction was reversed; the hash-mismatch substance was real
and is now resolved by the fresh-clone reproduction).

**The stress-test rows ST-1..ST-6.** All six verified against the stored two-seed
million-draw outputs, with the conditional statements confirmed present at every appearance
(abstract, summary box, M 1, M 7.2/7.3/7.5, M 9); partial recomputations by the panel are
consistent throughout (e.g., ST-6's 57.6% share reproduces as 57.4% by our recompute;
ST-5's "about 13%" is 12.3%).

---

## Part B — The revised version assessed afresh

Full text: `part_b_fresh_assessment.md` (hash above; written before any restricted material
was opened). Headlines:

- **Theory:** re-verified (verify_theory 116 checks pass); (H) now stated at ~16 sites incl.
  Prop 2's title, one editorial remnant (§3.5); the tex diff since our reviewed commit shows
  only documented fixes. **New S4 (Lean):** 35 theorems, standard Mathlib axioms only, no
  sorry/adversarial constructs; both tightenings implemented in Lean and reflected in the
  paper; S4's text is accurate. Compilation not verified here (no Lean).
- **Empirics:** the re-estimated core replicates completely (164/164 Table 2 cells; all
  re-estimated headline values verified against committed outputs); R2's whole-sample
  application is pre-specified and reproduces exactly (8 firms / 56 firm-years; κ = 0.952
  reproduced); the capitalized-software trail is complete; **S11 is a genuinely strong
  addition** (Table S19 reproduces cell-by-cell from 155,328 stored specs; forward pairing
  computed as we asked; pre-specification credible; the curve honestly narrows the paper's
  own claims).
- **S10 stress test:** design sound; `mc_claims.py --verify-only` 87/87; all six conditional
  claims transcribed with conditions everywhere; two minor defects found (the seed-stability
  sentence is contradicted by the stored seed comparison on its natural reading; the
  accountability sub-box's unfavorable-corner floor is untranscribed).
- **S12:** valuation test sound as a disclosed descriptive association (all Table S20 cells
  match committed outputs); cost-of-not-automating internally consistent; payback-drivers
  result verified analytically and by full recomputation of Table S22 — and it defuses our
  round-1 stock-vs-flow concern.
- **Compute-share units fix:** right and complete (1.2% of revenue; consistent everywhere; no
  stray "1%" reading survives; the printed 28% low end is unchanged because the old and new
  floors give 28.4 vs 28.5%).
- **Citations/legal/tax:** nine load-bearing legal/tax items verified at primary sources —
  nothing incorrect, the "imprecise→fixed" items are now precise; new citations clean (no
  nonexistent works or misattributions); one new minor defect (the AS 2201 bib paragraph list
  is stale relative to the new .06/.65 citations).
- **Plain-language abstract:** audited by three specialists independently — every number
  ties to the body at the re-estimated values and every load-bearing condition survives
  ((H), central costs, fixed prices, scenario-not-forecast, sampling-alone interval); it is
  1,916 characters against the repo's own 1,920 gate.
- **New findings: 3 minor, 8 editorial, 1 residual** (table in part_b_fresh_assessment.md
  §B.9: NB1–NB11). None affects any result; all have one-line fixes.

---

## Part C — Reproduction (what we ran, times, differences)

All runs on scratch copies of the repo at `eb7537b`; never modified the clone. Environment as
in the disclosure. Logs in `results/` and `diag/`.

| Run | Result | Runtime |
|---|---|---|
| `python3 code/estimate_v3.py` (full pipeline incl. 999-rep bootstrap; the run RESPONSE asked for) | Point estimates 16 s; full run 5,258 s. Regenerated `tab_estimands_v3.tex`, `tab_yearly_v3.tex`, `tab_bridge_v3.tex`, `calibration_anchor_v3.json`, `paper_stats.json` **byte-identical** to committed; `frontier_slope_v3.json` at machine epsilon (6.7e-16); `bootstrap_draws_v3.npz`: 65/65 arrays present, only SFA arrays differ (max 6.8e-4); `empirics_v3.json`: only SFA fields differ (max 8.3e-5) plus cosmetic `/meta/workers` | 88 min |
| `python3 code/verify_theory.py` | 116 checks PASS, 0 genuine failures (one 15p failure was a scratch working-directory artifact; clean from repo root) | ~6 min |
| `python3 code/paper1_macros.py` (the text-support gate) | PASS; 1,730 macros regenerated **byte-identical** (`macros.tex`, `ext_macros.tex`, `stress_macros.tex`); abstract length gate 1,916/1,920 chars; the gate reads the Lean axiom file, so the scratch needs `formal/` (noted for re-runners) | 4 s |
| `python3 code/supp_extensions.py` | PASS; 64 S12 macros; **27/27 text checks pass** | 49 s |
| `python3 code/verify_part2_acquirer.py` | **90/90** (new checks verify every case figure against both shipped filings with SHA-256 and printed-page anchors) | ~1 min |
| `python3 code/paper_stats.py` (fixed in this round) | 41/41 fields **byte-identical** to committed `notes/paper_stats.json` | 11 s |
| `python3 code/mc_claims.py --verify-only` | **87/87** | ~2 min |
| `bash code/build_paper1.sh` | **NOT RUN — no LaTeX in this environment.** Substitute: text↔macro↔output reconciliation for both PDFs (all quoted numbers tied to committed macros/outputs; see Part B) | — |
| Full pipeline per `REPLICATION_README` / `regenerate_all.sh --skip-raw` | Not run as a whole (the estimation pipeline above covers its core; `fetch_raw_data.py` not needed for Paper 1's own scripts per the README). Recorded as not-run | — |

**Differences from committed outputs:** none beyond SFA MLE optimizer-path noise (≤8.3e-5 on
point statistics, ≤6.8e-4 on bootstrap arrays) and a cosmetic worker-count metadata field —
the same character as round 1, now covered by the paper's printed reproducibility caveat.

---

## Part D — Verdict and revision sequence

### For release as an arXiv working paper (q-fin.GN, cross-list econ.GN)
**Recommendation: release after the following, ranked (all small):**
1. **NB2 (minor):** reword the S10 seed-stability sentence (verdicts are seed-stable; the
   ranges are not — the stored seed comparison itself shows the gains-to-dip ratio's max
   moving 74.42→79.44, and the joint response documents the 10k→1m move).
2. **NB1 (minor):** add .06 and the second note to .65 to the AS 2201 bibliography note's
   paragraph list.
3. **NB3 (minor):** transcribe the accountability sub-box's unfavorable-corner floor
   (~1.01% of revenue) into S10's summary.
4. **Editorial sweep (NB4–NB10):** "(H)" in §3.5; the 56%-vs-64% fraction; verify_theory
   duplicate check labels; the dead \KaSlack macro; S5.1's H1 interest citation to the 6-K;
   the search-protocol date in A.6; the S7 sentence on SHA-256 pins vs EDGAR re-serialization;
   (optionally) method cites for Latin-hypercube/Sobol in S10.
5. **Optional but recommended:** the Roche–Tandon bib note (GLM-17 residual) — the article's
   own summary numbers or an archived copy; and the M12 acknowledgment sentence (the
   beta-factor form's conservatism per the cited literature — note we have re-verified the
   NUREG passage the author's log thought unchecked).

### For a specialist field journal
**Recommendation: submittable now for an empirical-finance/IO outlet, with these additional
expectations** (ranked):
1. (H) remains the central limitation — honestly disclosed and now condition-labeled
   everywhere; a journal should either accept the conditional framing (as we would) or ask
   for an existence proof for a parameter class (the paper's own S3 analysis states what any
   proof must deliver; our round-1 terminal-singularity work characterizes the required
   solution near s̄).
2. The scenario discipline (S10/S11) is now at or above the journal norm; the compute-share
   range remains the dominant disclosed uncertainty, as the paper says.
3. The one structural robustness gap this panel would still name for a journal: the anchor
   (14 firm-years of 7 firms) drives the 2036 path; the sampling interval is labeled and the
   joint range is disclosed, but a journal reviewer may ask for the anchor's own
   leave-one-firm-out path (the machinery exists — S11 does leave-one-firm-out for the
   cross-sectional claims).
4. The minor/editorial list above.

### What we could not do
Compile the Lean formalization; build the PDFs; re-pull raw SEC data (not needed — the
shipped extract plus hashes sufficed for everything we tested); verify the McKinsey page; read
the ASC sub-letters (FASB paywalled). All recorded above and in the panel reports.

**Closing note on the record.** This round the corrections ran in both directions: the author
fixed our five majors and adopted 30 of 46 findings; we found the author right on four of our
round-1 items and wrong on one verification-record claim (M12's NUREG passage). The paper's
replication discipline — byte-identical regeneration, machine-checked statics, pre-specified
spec curves, a joint stress test carried into every headline sentence, and now filings
shipped with hash pins — is, in this panel's experience across both rounds, exceptional.

*Panel reports with per-row evidence: `reports/R-A_theory.md`, `R-B_empirics.md`,
`R-C_accounting.md`, `R-C2_citations.md`, `R-D_execution.md`, `R-Lead_rows.md`. Scripts and
outputs: `scripts/` and `results/`. Verdict table: `response_audit.csv`. Hashes: README.md.*