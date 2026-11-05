# Referee Report — "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation"

**Author:** Akshaya Bangalore Sreenivasa Murthy (independent researcher), November 2026.
**Documents reviewed:** main paper, 82 pp. (`paper1_nov_2.pdf`) + Supplementary Appendix, 57 pp.
(`supplement_nov2.pdf`), plus the public replication repository `github.com/amurthygithub/rule-of-x`.
**Review executed:** 2–3 November 2026, by an AI referee panel (six roles A–F + Lead) under a
documented adversarial protocol; this report is the panel's consolidated deliverable.

---

## 0. Review provenance, capabilities, and blinding

**Who reviewed this.** The review was performed by LLM agents, not human experts. The panel
consisted of a Lead and six specialist roles: A (mathematical economics and optimal control),
B (econometrics, frontier estimation, empirical IO), C (corporate finance, accounting, taxes and
acquisition measurement), D (reliability engineering, stochastic execution, financial-reporting
controls), E (prior art, citation verification, parameter-source transport), and F (adversarial
auditor of the first reports). The harness platform reported the agents' model identity
inconsistently across the session (teammates were labeled `glm-5.3` at spawn and
`qwen/qwen3.8-27b` in a later listing; the Lead was labeled `deepseek-v4-pro:0813` then
`qwen/qwen3.8-27b`); the operative facts are that (i) all panel members ran inside the same
harness on the same infrastructure, (ii) the specialist roles were isolated conversation contexts
that did not see one another's reports before their first reports were preserved, and (iii) several
members are instances of the same model. **This panel is not a set of independent human experts and
not independent model-family evidence; its unanimous positive verdicts are weaker evidence than
human replication would be.** The paper's own Appendix A discloses exactly the analogous caveat
about its own AI research agents (main p. 82), which we assess as accurate and candid.

**Capabilities actually used.** Full-document reading of both PDFs (page-indexed extraction,
cross-checked against rendered page images where notation mattered); code execution (Python 3.12.3;
numpy 2.5.2, scipy 1.18.1, sympy 1.14.0, pandas 3.0.3, statsmodels 0.15.0); symbolic mathematics
(sympy, 50-digit spot checks); independent numerical optimization and simulation; web access to
primary sources (SEC EDGAR filings fetched in full, NBER/arXiv/NIST/OMB/Crossref, practitioner
pages, standards bodies); and independent agent delegation with isolated first reports.

**Blinding and exposure.** A first-pass blinding protocol was enforced: the repository's prior
referee/critique materials (134 files under `notes/reviews/`, `notes/referee*_report.md`,
author audit logs, response-to-reviewer drafts, and the author's own reference-verification notes)
were **quarantined outside the working repo tree before any panel member began**, and no panel
member opened them; no web search for critiques of the paper was performed. The blinding was
nevertheless **partial, and this report must not be represented as fully blinded**, for three
disclosed reasons: (1) the paper's own Appendix A describes the existence, models, dates and
dispositions of its prior internal AI-referee rounds (v1, v2, v3), including which findings were
withdrawn — unavoidable exposure; (2) the panel learned the *existence* of the quarantined
materials and their file names during inventory; (3) the panel's first reports were preserved
before this report compared or consolidated them, but the Lead's argument reconstruction (which
preceded reading any specialist report) was written knowing which claims the paper itself says
were contested in its internal rounds. No quarantined content was read at any point.

**What was NOT done.** No human expert reviewed anything. The session transcripts of the paper's
own AI agents were not part of the replication package and were not examined (the repo states
this); the quarantined prior critiques remain unread; the full text of a small number of cited
sources was inaccessible and is flagged as such in §8.

---

## 1. Evidence boundary (inventory)

| Item | Details |
|---|---|
| Main paper | `paper1_nov_2.pdf`, 82 PDF pages = printed pages 1–82 (verified offset zero). PDF metadata: pdfTeX-1.40.25, created 2026-11-03 01:48 CET, title matches the stated manuscript ("The Rule of 40 as a Price Line…"). sha256 `bd87f45f…c6f9cf` (matches the transmitting message). ~56,600 words. |
| Supplement | `supplement_nov2.pdf`, 57 PDF pages = printed pages 1–57. "Supplementary Appendix to …", same author, Nov 2026. sha256 `acf9d62b…de02c2` (matches). ~46,700 words. Sections S1–S9. |
| Filename note | The transmitted request called the manuscript "Limits of AI Automation.pdf"; the actual supplied file is `paper1_nov_2.pdf` with the title above — confirmed identical to the described paper. |
| Repository | Clone of `github.com/amurthygithub/rule-of-x` @ `62e574b` (2026-11-02 19:55 PST): LaTeX sources, replication code (`code/`, `engine/` package with tests), data (`data/panel_v3*.csv`, task/process tables, `v3_inputs` including raw Bending Spoons 6-K JSON), figures, notes. |
| Version drift (important) | The supplied PDFs are **newer than every PDF committed in the repo** (hash mismatch vs `paper1/paper1.pdf`, and vs the v1/v2/v3 PDFs preserved in the repo's reviews folders, which were quarantined unread). The committed `.tex` also lags the supplied PDFs in at least one visible way (the supplied footnote says "Data and code are available from the author", while the committed `.tex` embeds the repository URL). The supplied PDFs were therefore treated as the sole ground truth; repo `.tex` was used only as a reading aid, and every such use is flagged in the specialist reports. Consequence: the repo as committed **cannot rebuild the supplied PDFs exactly**; a final-source commit is required for release (see §10). |
| Quarantine | 134 files of prior critique/response material moved to `/root/tmp/ruleof40/quarantine/` before panel start; unread. Preserved for the record. |
| Data/code present vs cited | The paper's prose claims replication availability; the repo contains executable panel data, estimation code, verification scripts and outputs — these were actually executed (see §7). Raw SEC XBRL fetches are not archived in the repo (fetch lists and a browser-payload extractor are), so the *panel build* from EDGAR was not re-executed from source; everything downstream of the committed panel was. |

**Pagination convention.** Throughout this report, locators cite section/equation plus printed
page (= PDF page index for both documents), e.g. "main §3.6, p. 21".

---

## 2. The paper's argument, reconstructed (strongest accurate version)

This section states the thesis in its strongest defensible form, separating claim types. The
consolidation below was written by the Lead from the sources alone, before reading any specialist
report, and is preserved at `first_reports/lead_argument_reconstruction.md`.

**Thesis.** The Rule of 40 (revenue growth + profit margin ≥ 40) and its growth-weighted variants
(the "Rule of X") are *price lines* — iso-score lines — not frontiers. The attainable set of
(growth, FCF-margin) pairs is a concave frontier generated by spending on growth under
diminishing returns in remaining market headroom; the maximal score is a tangency, with a closed
form (Lemma 2): the margin intercept, plus market growth net of the capital it requires, plus a
transient growth surplus. Five limit mechanisms bound the score: saturation (the surplus vanishes
as share approaches its cap), the **score budget** (every point of score above the saturated level
is paid out of a finite budget of log share headroom, Proposition 1), competition (free entry
passes automation's savings to customers except rents on non-replicable inputs, capped by the
full-cost ceiling, Proposition 4), the **full-cost floor** (compute, fees, cash taxes, an
accountability floor from internal-control-as-pass-fail under common-mode failure, Proposition 5,
and the recurring costs of maintaining/securing/supervising AI), and **execution** (failed
transitions, limited change capacity and disruption slow the approach like a pace cut without
lowering the level, Propositions 6–7).

**Claim types, separated.**
- *Accounting identities:* the four margin bases (GAAP operating; adjusted; FCF; FCF-after-SBC);
  growth/margin pairing; eq. (2) FCF identity; Remark 3's economic-profit/ROIC restatement;
  Proposition 8's acquired-growth decomposition R^A_X = R^org_X + (X−k_acq)g^acq; the margin-gap
  decomposition into expense lines.
- *Assumptions (disclosed):* Assumptions 1–4 (isoelastic growth technology with headroom;
  non-depreciating capital K = kS), 5 (heterogeneous firms), 6 (Cournot free entry, entry only at
  date 0, homogeneous product), 7 (layered financial controls with beta-factor common cause),
  8 (additive process increments, waves, program clock); the scenario parameter ranges (α∈[0.25,
  0.45]; compute share 1–60%; taxes 15–21%; accountability band 0.5–4.6%; execution parameters).
- *Proved propositions (statics and dynamics):* Lemmas 1–5, S1–S3; Propositions 1, 3–9, S1–S3;
  Corollaries 1–4. All audited by referee A (§4).
- *Conditional on an unproved hypothesis:* Proposition 2(b)–(d) — a value-maximizing firm
  maximizes a Rule-of-X score at every date with weight equal to the marginal value of revenue
  (marginal q of revenue) — holds under verification hypothesis (H), which the paper **explicitly
  states it has not proved** (main p. 21: "We have not proved (H)"), supplying instead numerical
  dynamic-programming evidence at the worked-example parameters. Every downstream sentence of the
  form "a value-maximizing firm acts on weight v′(s)" is conditional on (H) — the paper says this.
- *Numerical illustrations:* Table S3 (equal score ≠ equal value: 5.2×–12.1× revenue multiples on
  the same Rule-of-40 line); the Rule-of-1000 example (Λ ≈ 8.71 demand pull, 1314-point excess
  growth, 394% spend, −334% margin); Corollary 1's example budgets.
- *Calibration/scenarios:* the full-automation ceiling (Table 4), the central path to 2036
  (Table 5), the tornado sensitivities (Table 6), the lever positions (Table 7). Every number is
  conditional on disclosed scenario values, labeled as such in the text and Table S11's
  assumptions register with grounding classes.
- *Descriptive empirics:* score distributions and pass rates by basis; the p95 decline
  (−11.9 GAAP / −12.7 cash points, 2016–19 → 2023–25); the Ψ₀.₉₀ slopes (−0.22/−0.16); the spend
  ratio (3.0–3.5) and its instability as an identifier (α(X−k) ∈ [0.05, 10.1] across methods);
  scale gradient (weak); capital-intensity gap (accounting effect); near-frontier margin gap
  (34.5 points, 29.4 of 41.3 from S&M among 40–60% growers); entrant shortfall.
- *Causal/structural claims:* none asserted; the paper repeatedly concedes non-identification
  (of the weight firms act on, of the technology's curvature, of why the top fell) — and its
  empirical claims are consistently stated within those concessions (verified by B).
- *Practical recommendations:* score on annual FCF-after-SBC with basis stated; charge acquired
  growth at k_acq (annuity or user cost, not double-charging financing); supplement with economic
  profit as headcount falls; treat accountability as a design constraint, not a headcount.

**Claim-dependency (headline → supports).** The 32.5% market-growth threshold ← Corollary 4 (29)
← Remark 2 (tax) + Definition 3 floors (Lemma S4, Table S16) + Proposition 5 + scenario inputs
(fragile link: the compute share, admitted "dominant uncertainty"). The 2036 score 59 [54, 62] ←
Table 5 ← the 13-firm-year anchor inversion + Proposition 7(e)'s upper bound + the full-cost
target path (fragile links: S&M attribution — bounded 55–65; execution parameters). The p95
decline ← E1 + firm-cluster bootstrap + a familywise correction whose family the paper discloses
was fixed after the first version's results were known. "Extreme scores are transient" ←
Proposition 1 (needs zero-spend growth ≥ market growth, one market) with disclosed escape hatches
(retention lags: Remark S1(b); acquisitions buy fresh budgets: Proposition 8(e)). The
"no-all-AI-design-passes" example ← Proposition 5's beta-factor algebra + a scenario π̄ + the
example numbers (fragile link: the beta-factor form itself — see §5, finding D2).

**The few claims whose failure would materially change the contribution:** (i) hypothesis (H)
(the decision-weight reading — the paper's flagship conceptual result — is conditional on it);
(ii) Proposition 1 + Corollary 1 (transience); (iii) Proposition 5's algebra (the accountability
floor as a control standard); (iv) the ceiling arithmetic (Corollary 4, Table 4); (v) the
empirical descriptive claims (p95 decline, slope far from −1); (vi) the Bending Spoons case
arithmetic. All six were independently verified (§4, §7).

---

## 3. What the panel verified as correct (strengths)

The panel's independent checks — not the author's verification code — established the following.
Scripts and raw outputs are archived under `diagnostics/` and listed in §9.

1. **The static theory is correct as stated.** Referee A (76 inherited checks: 42 symbolic, 16
   numeric, 11 dynamic, 7 HJB; environment sympy 1.14.0 at 50-digit precision, numpy/scipy
   grids) rederived: the frontier (4) and its concavity/trichotomy at α = 1/2 (including the
   Lemma S1(c) non-convexity example: corner local max ≈ 0.486, interior local max ≈ 0.595 at
   g ≈ 0.739 — reproduced exactly); the tangency closed forms (5)–(7) against brute-force
   optimization over 400 random draws including corner (X ≤ k) and binding-cap cases; the
   duality X(g) = −m*(g)′; Lemma 3's saturation derivative dR*/ds = −(X−k)Δ*/(s̄−s) and the
   Λ-threshold; all five envelope derivatives of Lemma 4 plus convexity in k and the
   cross-partial; the budget bounds of Proposition 1 on 300 random spend paths (max ratio 0.68 of
   the bound) and the sharpness of Proposition S2 (constant-Δ policies approach ratio 1.000);
   the myopic-path decay (log-slope −3.66 ≤ −1/α); Lemma 5's duration algebra including the
   Var_w(t) identity and the Gordon limit; Proposition 4's Cournot/free-entry algebra end-to-end;
   Proposition 9's switch weights. The Lead's own independent 15-check script reproduces the
   frontier identity on 20,000 draws, the closed-form maximum vs scipy on 5,000 draws, and the
   paper's worked numbers (Corollary 1's budgets 1.8/9.6/5.0 and 0.43/0.30 years; the Rule-of-1000
   illustration Λ = 8.71, 1314/394/−334; Lemma 5's example; Table S3's multiples 12.1/11.7/8.3/5.2).
   Two of the Lead's checks initially "failed" and were traced to errors in the Lead's own scripts
   — recorded here because the protocol requires it; the paper's numbers were right in both cases.
2. **The complete supplementary proofs hold.** A read every proof in S3/S4/S8 (Props 4–9,
   Lemmas S3/S4, Props S1–S3, Prop 5, Props 6–7 including the random-freezes part (f) whose exact
   survival formula and conservativeness inequality were re-derived, and whose finite-date
   counterexample the paper itself exhibits — verified). No proof in the audited range was found
   to need a hypothesis its statement omits (each potentially missing hypothesis — N_F ≥ 2,
   Z√(B/F̂) ≥ 1, "changes only m0 and G", N ≥ n_cap·n(t_R), no-interaction in Prop 8(b) — is
   in fact stated). One minor exception: an after-tax parenthetical applying Proposition 4(d)
   (see §5, finding M3).
3. **The Proposition 2 evidence is honest and numerically solid.** The paper proves what it can
   (homogeneity, bounds, small-share limit, no-root case), states (H) as an unproved verification
   hypothesis, and gives DP evidence. A independently solved the singular ODE by backward shooting
   from the terminal point and matched the author's upwind-DP solution to 3 decimals everywhere,
   including v₀ = 10 at λ ≈ 0.0698 and the six smaller roots of (19) across discount rates
   (14.57/10.00/5.82/3.74/2.09/1.35 vs printed 14.6/10.0/5.8/3.7/2.1/1.35). The HJB identity
   residual along the independent solution is 2×10⁻¹⁶.
4. **The empirical pipeline replicates end-to-end** (see §7): every one of the 164 cells of Table
   2, every §5 text statistic, Table 5's anchor panel and Table 7's lever cells reconcile with the
   committed outputs at printed precision; the author's code regenerates its committed outputs in
   a fresh environment (full 999-replication bootstrap included: byte-identical tables and anchors,
   machine-epsilon differences on frontier slopes, ≤2×10⁻³ differences only on SFA MLE interval
   endpoints); and an *independent* reimplementation from the panel CSV reproduces every headline
   statistic to ≤5×10⁻⁴, with a reduced 199-draw bootstrap confirming the interval rules.
5. **The case-study arithmetic is exact and faithful to filings.** Referee C recomputed, from the
   primary filings fetched in full (Bending Spoons F-1 2026-06-08, 424(b)(4) 2026-07-01, Q2-2026
   6-K exhibits 2026-08-13, notes 6-K 2026-10-28; Palantir 8-K exhibits 2026-08-03 and 2026-02-02;
   CoreWeave 10-K XBRL): every headline number the abstract advertises — 115.9 / 105.0 / 87–114
   (2025 GAAP and charged-as-capital), 160 / 22–44 (Q2 2026), Palantir's 155 (which is *Palantir's
   own reported metric*, verified — the paper's "reported" is faithful), 140, 88, CoreWeave 167/14
   — plus all rows of Table 3, the double-charge quantification (1−τ)c_fin = 8.3/10.9, the k_acq
   multiples (1.73/2.30/3.23), and the §4.6/Table S10 panel statistics. The financing
   double-count diagnosis (OCF is after interest under ASC 230; charging a debt-inclusive WACC
   against it double-counts by exactly (1−τ)c_fin) is correct and the paper's fix is the standard
   unlevered treatment.
6. **The stochastic-execution calibration is arithmetically exact.** D reproduced every §7.3
   number (41%/61% by 2036; 6.3%/17.2% per year; dips 3.6–4.2; crossing 4.0; payback 7.5/8.5;
   cumulative −8.8/−8.6 at 3/5 years; NPV 98% of a year's revenue; PV ratio 3.9; fast case
   30/73/85%, completion 2032, payback 4.7/5.0; ownership variants 28%/36%) in an independent
   Monte-Carlo implementation, confirmed the Prop 7(e) upper bound is attained through 2036,
   confirmed the disruption double-count is avoided (and quantified what it would have cost:
   41%→29%), and verified the model's primitives against the author's committed parameter file.
7. **The control-standard claims are faithful to primary texts, and no regulatory threshold is
   invented.** D verified against current authoritative text (Reg S-K Item 308(a)(3), Rule
   13a-15(f), SEC Releases 33-8238 and 34-55929, PCAOB AS 2201 including A7, .65 and B28–B31):
   the pass-fail reading, the "reasonable possibility" language, the fact that AS 2201 .65 says
   the evaluation "can be made without quantifying the probability of occurrence" (the paper's
   "the standard sets no number for 'remote'" is correct — indeed understated), the benchmarking
   conditions for automated controls, and the material-weakness standard. The π̄ = 5%/1% values
   are labeled scenario values at every use; the paper states "our operationalization of the
   standard, not an accepted audit method."
8. **Citation transport is unusually clean.** E verified 36 ledger entries against primary
   sources: Feld's origin story (verbatim), Bessemer's Rule-of-X weights (private ~2×, public
   ~2–3×, the 2–9× historical range, both R² values — exact to the digit), Bain's 16%-of-86,
   Vista's "emerging aspiration" (the source's own phrase), Lipman's Rule of 30, Palantir's 155
   with the company's own definition, NIST IR 8547's 2030/2035 dates, OMB's $7.1B "rough order of
   magnitude", Cottier's 9–900×/yr and 2.4×/yr, Gundlach's 5–10×/yr and 3–18×/yr, Demirer's −1.1
   (with the substitution-vs-aggregate caveat faithfully carried), the adoption/productivity
   numbers (1–5% of hours; 3.7→5.4%; 18%/32%/57%; 13%; null effects; 12.2%/25.1%; +19% developer
   time), and ~25 Crossref bibliographic records — all matching. Table S11's transport
   self-documentation (grounding classes, "what the source measures" columns, refusals to
   over-read) is exemplary.
9. **Intellectual honesty of the disclosures.** The paper documents its own human–AI protocol
   with author decisions (Table 8), nine researcher degrees of freedom with timestamps (A.4),
   the withdrawal of first-version findings, and the fact that its familywise family was chosen
   after the first version's results were known. Its "How not to use these numbers" section
   pre-empts the most likely misreadings. The repo's QA log lists open issues a referee would
   flag. These disclosures did not prevent the panel from finding the defects in §5, but they
   materially changed their severity: nearly all findings are about sentences that generalize
   beyond what was checked, not about fabricated or irreproducible results.

*(Section 4 — the audit matrix — and Sections 5–11 follow in the consolidated report.)*
---

## 4. Claim/theorem audit matrix (deliverable B)

Legend: **✓** independently verified correct · **⚠** correct but conditional (on an unproved
hypothesis or disclosed scenario values) · **✗** found incorrect (see §5) · **~** ambiguous or
under-specified · **⊘** not tested/verifiable in this review. "A/B/C/D/E" = specialist report;
"Lead" = Lead's own checks; details in the archived reports and scripts.

| Claim (locator) | Status | Basis |
|---|---|---|
| Lemma 1 frontier (4), convexity, α-trichotomy of m*″(G+) (main §3.2, pp. 13–14) | ✓ | A: symbolic+numeric, 20k draws incl. Lead |
| Lemma S1 timing of growth capital; non-convexity example (supp §S1, pp. 2–3) | ✓ | A: example reproduced exactly (0.486/0.595 at g≈0.739) |
| Lemma 2 max score (5)–(7), tangency, duality X(g) (main §3.3, pp. 14–15) | ✓ | A: 5,000-draw brute-force match incl. corners/caps; Lead |
| Lemma 3 saturation, dR*/ds, Λ-threshold (main §3.4, pp. 16–17) | ✓ | A s1; Lead hand rederivation |
| Lemma 4 envelope derivatives, convexity in k (main §3.5, pp. 18–19) | ✓ | A: all five + cross-partial, symbolic |
| Prop 1 score budget + Cor 1 transience (main §3.4, pp. 17–18) | ✓ | A: 300 random paths; Prop S2 sharpness → 1.000; examples 1.8/9.6/5.0, 0.43/0.30 |
| Prop 2 decision weight = marginal q of revenue (main §3.6, pp. 20–21) | ⚠ | Conditional on unproved (H) — paper says so; numerical evidence verified (A: independent ODE solution matches DP to 3 decimals; HJB residual 2e−16) |
| "v′(s) falls with share" (supp §S2.2 p. 6; main §3.6 p. 21; §3.5 p. 20; §7.4 p. 63) | **✗** | A: U-shape is structural (v′(s̄)= (m₀−kG)/(r−G) approached from below; min v′=5.084 at 80% of cap in the worked example; confirmed on the author's own solver). See §5 F1 |
| "Weight below revenue multiple at every share" (main §3.6, p. 21) | ✓ | A: verified on fine grids, both methods, strict on the interior |
| Lemma 5 screening weight as duration (main §3.6, pp. 22–23; Table S3) | ✓ | A: symbolic; Lead: example numbers + Table S3 multiples |
| Prop 3 / S3 envelope, non-identification, within-firm slope (main §3.7, pp. 23–25) | ✓ | A: construction verified (observational-equivalence inversion checks) |
| Prop 4 free entry + scarce input + full-cost bound (main §3.8, pp. 25–26) | ✓ | A: algebra end-to-end; after-tax parenthetical ~ (§5 M3) |
| Prop 5 control-standard algebra + scale limit (main §3.9, pp. 29–30) | ✓ | A + D: rederived; all example numbers exact (P̄o=0.0021/0.00042; floors 0.37–0.38%) |
| β-factor "no number of AI layers passes" (Prop 5(b); §7.2 p. 56; §8.5) | ⚠ | Correct within the stated model; beta-factor all-layers-defeated form is itself the conservative idealization per the cited literature (§5 M12) |
| Remark 2 taxes, ψ_T schedules, substitutions (main §3.9, pp. 27–28) | ✓ | A: ψ5=0.796/ψ15=0.532 exact |
| Remark 3 economic-profit/ROIC identities (main §3.11, pp. 34–35) | ✓ | A, C: rederived; worked example 7.5 points/−0.5 checks |
| Cor 4 + Table 4 full-cost ceiling, 32.5% threshold (main §7.2, pp. 56–57) | ✓ arithmetic | A, D, Lead: all 32 cells + G* + decomposition reproduce; ⚠ every input a disclosed scenario; 1% compute bound is success-conditioned (§5 M11) |
| Lemma S4 floors + Table S16 (supp §S8, p. 52) | ✓ | D: row-by-row (risk cost, csec, cmnt, errors, misbehavior, common mode, canc; cfull 2.14/6.23/16.47/7.25) |
| Props 6–7 attainable/expected frontiers incl. (f) (main §3.10, pp. 31–34) | ✓ | A: proof audit + survival formula + counterexample; D: MC bound attained through 2036 |
| §7.3 execution scenario (Tables 5–6, pp. 58–62) | ✓ arithmetic | D: independent MC reproduces all numbers; author code rerun confirms; ⚠ b̄ dispersion unmodeled (open question) |
| Prop 8 + Remark 4 acquired-growth charging (main §6, pp. 48–51) | ✓ | A: proof audit incl. fresh-budget bracket; C: PV-preservation of both charges verified |
| Table 3 Bending Spoons case (main §6, pp. 54–55) | ✓ arithmetic | C: every row reproduced from primary filings |
| §6 data-availability sentences ("organic growth for one quarter", "not in our extract", H1-only investing split) (main §6, pp. 51–53) | **✗** | C: F-1/424B4 disclose annual organic growth (7%/13%), subscription shares (95/92/93%), SBC ($55.5M 2025), annual investing split (2024: 81.7% acquisitions). See §5 F2 |
| Palantir 155/140/88; CoreWeave 167/14 (main pp. 2, 45, 37) | ✓ | C, E: primary-source verified; 155 is the company's own reported metric |
| Prop 9 levers by position + Table 7 (main §7.5, pp. 64–65) | ✓ | A: algebra rederived; B: cells reconcile; ⚠ retention lever stage-classification depends on the v′ U-shape (§5 F1 narrowed impact) |
| Empirical pipeline: Table 2 (164 cells), §5 statistics, bootstrap, familywise code | ✓ | B: four-way replication (text↔outputs↔author code↔independent reimplementation); full 999-rep bootstrap rerun byte/epsilon-level (§6) |
| "GAAP p95 decline survives familywise at 10% under most procedures" (main §5.2, pp. 42–43) | ✓ as stated | B: Holm/RW implementation exact; ⚠ family chosen after v1 results known — quantified counterfactual in §5 F5 |
| Sample rules R1–R5, 292 firms / 1,788 firm-years (main §4, pp. 36–39) | ✓ | B: counts/rules verified; purged registrant identified ([excluded registrant], SIC 7374 → outside 7372 sample; claim "no figure depends on it" true for this paper) |
| Ψ₀.₉₀ orientation; non-identification discipline in §5 | ✓ | B: orientation coherent; no technology-identification claim made anywhere |
| Rule-of-1000/S5 illustration | ✓ | A, Lead: Λ≈8.71 (8.709), 1314/394/−334 |
| Practitioner-rule facts (Feld; Depeyrot-Heap; Deeter-Bondy; Vista; Lipman; Bosche) (main §2.2) | ✓ | E: primary-source verified, several verbatim |
| "Only peer-reviewed academic study of the rule is Lee (2024)" (main pp. 5, 9) | **✗** as stated | E: Nei/Ruus/Indov 2026 (Financial Markets, Institutions and Risks 10(3):130–168, pub. 26 Sep 2026) is a second journal study; the narrower "no frontier study" claim survives. See §5 F3 |
| Lee (2024) "1,756 SaaS firms" (main p. 9) | ~ | E: MPRA version says 1,771 everywhere; published AFL version inaccessible (Cloudflare). See §5 M14 |
| §2.7 novelty list (score budget; decision-vs-screening weight; non-identification; accountability floor; attainable/expected frontiers) | ✓/~ | E: score budget, Prop 2-reading, Prop 5-formalization, Props 6–7 plausibly new within bounded search; "non-identification" internally tensioned vs §2.1's Marschak-Andrews concession (§5 M15) |
| Deferred-revenue k<0 threshold ~26% at median 0.27 (main p. 58; 'How not to use' item 2) | ✓ | C: median 0.274–0.276 (n=355) from retrieved frames; 32.5/1.27 = 25.6 ≈ 26% |
| Research-protocol disclosures (App. A; supp S7) | ✓ verified where checkable | A.4 degrees of freedom verified against the repo's own logs where possible; one unresolved editorial marker remains in the text (§5 F4) |
| arXiv AI-use policy compliance claim (main §2.6, p. 11) | ✓ | E: policy text verified |
| verify_theory.py as author evidence | ✓ (cataloged) | A: 26 sections; does not test the v′ profile claims its own solution contains (relevant to F1) |


---

## 5. Major and minor findings

*(Numbered F = major; M = minor. Each entry gives locator, classification, evidence, the strongest
author defense, the adversarial disposition (referee F), affected conclusions and magnitude, and
the smallest correction with a decisive acceptance test. Root causes are deduplicated into seven
families (per the adversarial audit): (i) prose generalizing beyond what was computed (F1);
(ii) extract-relative claims of data availability (F2 + M17); (iii) version-drift and stale
artifacts (M1 + M2); (iv) post-hoc inferential choice (F5); (v) basis/convention not stated at
point of use (M3–M7, M9, M10); (vi) novelty overstatement (F3 + M15); (vii) disclosed
transport/scope conditionings (M11–M14, M16). One root cause is counted once. This section
incorporates the adversarial audit (`adversarial_audit/F_audit.md`).)*

**Major findings (each must be addressed before release; all four survived adversarial audit
with independent re-execution of the decisive evidence).**

**F1. The firm's decision weight v′(s) is U-shaped, not "falling with share" — four prose
claims about the paper's own worked example are false where they generalize.**
- *Locators (re-pinned):* supp §S2.2, p. 6 ("a numerical solution of (17) gives a growth weight
  v′(s) of 9.1, 7.2 and 5.4 at 1%, 10% and 50% of the cap … and it **falls with share**"); main
  §3.6, p. 21 ("close to and below its revenue multiple, **and falling with share**"); main §3.5,
  p. 20 ("its own decision weight X_dyn(s) = v′(s) of Proposition 2, **which falls with share in
  the worked example there**"); main §7.4, p. 63 ("For a firm **that acts on a decision weight that
  falls with share (Proposition 2, under its hypothesis (H))**"). The intro's sentence (p. 3) is
  conditional phrasing and not itself an error.
- *Classification:* demonstrated error (in prose; no formal proposition asserts monotonicity —
  Proposition 2 and its proof are silent on v′'s shape, and the paper's conditional labeling of
  (H) is consistent everywhere).
- *Evidence:* Analytically (referee A, re-derived by hand by referee F): near s = s̄ the firm never
  spends (h(s̄) = 0), so v(s) = ū·s with ū = (m₀−kG)/(r−G) locally and **v′(s̄⁻) = ū, approached
  from below** (v′−ū ~ −s̄·a·q·t^{q−1} < 0, dv′/ds → +∞), while (19) forces v₀ = v′(0⁺) > ū
  whenever λ > 0 ((r−G)(v₀−ū) = C_α(λ(v₀−k))^{1/(1−α)} = 0.250 in the example). Hence v′ falls,
  reaches an interior minimum, and rises back to ū — **for every admissible parameter draw**, not
  just the worked example. Numerically (two independent discretizations agreeing to 3 decimals,
  plus the author's own `solve_hjb`, re-run by referee F): min v′ = 5.084 at 80% of the cap,
  rising through 5.40 (98%), 5.70 (99.9%) back to 5.833 = ū. The three *printed* numbers (9.1,
  7.2, 5.4 and multiples 9.4, 8.1, 6.5) are correct and lie on the falling branch. The author's
  verification script never tests the shape claims its own solution contains (its HJB identity
  check runs only to 90% of the cap).
- *Strongest author defense:* the example's sampled range (1–50% of cap) does fall; "the weight
  lies below the revenue multiple at every share" (p. 21) is true (verified on fine grids, strict
  on the interior); the growth-engine lever still vanishes at saturation through h(s) → 0
  regardless of v′, so §7.4's stage ordering survives for that lever; and no table, calibration
  or theorem depends on v′ monotonicity (the §7.3 path uses fixed weights X ∈ {2.5, 5, 9}; Prop 9
  is fixed-weight).
- *Adversarial disposition:* SURVIVES. The defense covers §S2.2/§3.6 read as sampled-range
  descriptions but cannot cover §3.5's claim about the whole example profile or §7.4's
  attribution to Proposition 2. The retention lever is misclassified as early-stage: under the
  firm's own weight its gain (v′−k)dG never vanishes (≈5.08–10)·dG in the example, so near
  saturation the dominant set is {overhead, accountability floor, **retention**}.
- *Affected conclusions and magnitude:* modest; no numeric result changes. The wrong mental
  model misstates the near-saturation retention gain by up to ~15% (5.83 vs 5.08) and the §7.4
  stage sentence. *Smallest correction:* replace "falls with share" with "falls with share up to
  about 80% of the cap, then rises back to (m₀−kG)/(r−G), the never-spend multiple; it is largest
  at small share"; add retention to §7.4's near-saturation lever set. *Decisive acceptance test:*
  three checks on the author's own HJB grid (v′(0.95s̄) > v′(0.5s̄); v′(0.99s̄) → (m₀−kG)/(r−G)
  within 1%; interior argmin with min v′ < ū) — the current wording fails the first; the
  corrected wording passes all three (referee F re-ran the grid).

**F2. Section 6's statements about what the Bending Spoons filings disclose are false; Table 3
is incomplete accordingly.**
- *Locators:* main §6, p. 53 ("the company reports organic growth for one quarter … a split of
  2024 and 2025 growth and spend by business is not in the filings we read"; "its organic growth
  is measured only by the company, for one quarter"); p. 52 ("the subscription share of revenue
  is not in our extract"); p. 51 ("its stock-based compensation is not in our extract"); p. 51
  (H1 investing splits quoted as if annual splits were unavailable); Table 3, p. 54 (organic-growth
  rows "–" for 2024/2025).
- *Classification:* demonstrated error about the primary sources (evidence-transport root cause:
  fields absent from the author's extract were declared unavailable without re-reading the
  filings the paper itself cites as read in full).
- *Evidence (referee C, independently re-grepped by referee F in both the F-1 and the 424(b)(4)
  full texts):* the F-1/424B4 MD&A discloses "Organic revenue growth was **7% in 2024**" and
  "**13% in 2025**" on the same company definition; "Subscriptions accounted for **95% of our
  revenue in 2023, 92% in 2024, and 93% in 2025**"; audited equity compensation of **$25,855k
  (2024) and $55,523k (2025)** (4.25% of 2025 revenue); and the annual investing split
  (acquisitions $726,574k in 2024 = **81.7%** of the net outflow, intangibles $162,476k, PP&E
  $604k). The paper's H1-only shares (99.9%/99.8%) are correct *for those halves*.
- *Strongest author defense:* "not in our extract" is literally true; the company's organic
  measure is unaudited, estimated and company-defined (the paper already stresses this); the
  by-business split genuinely is not disclosed; and the annual organic scores (2025: 34.3 before
  interest; 23.4–40.3 across treatments) fall **inside** the paper's own 22–44 bracket, so no
  conclusion reverses — the disclosed figures *strengthen* the paper's argument that the 115.9
  rests on uncharged acquired growth.
- *Adversarial disposition:* SURVIVES as narrowed (the five sentences share one root cause and
  are counted once). *Affected conclusions:* none reverses; Table 3's organic rows should be
  filled (2024: 26.0/21.1; 2025: 34.3/23.4; 40.3/29.4 with the reorganization add-back; an
  after-SBC cash row is computable: 116.9 − 4.25 ≈ 112.7 after interest paid). *Smallest
  correction:* one sentence stating the MD&A's annual organic figures and the subscription and
  SBC rows, plus the Table 3 fill. *Acceptance test:* every availability sentence in §6 survives a
  full-text search of the F-1 and 424B4.

**F3. The "only peer-reviewed academic study of the rule" uniqueness claim cannot stand as
written.**
- *Locators:* main §1, p. 5; §2.2, p. 9 ("The only peer-reviewed academic study of the rule we
  are aware of / we located … is Lee (2024)").
- *Classification:* unsupported interpretation (uniqueness claim contradicted by a second
  journal study); the narrower companion sentence — "no modern peer-reviewed study of the
  growth-profitability **frontier** of software firms beyond it" — survives the panel's bounded
  search.
- *Evidence (referee E, verified by referee F against the fetched article and Crossref record):*
  Nei, Ruus & Indov (2026), "Enterprise Value Dynamics in Publicly Traded SaaS Firms: Revenue
  Growth, EBITDA Margin, and the Rule of 40 across Revenue-Defined Growth Stages," *Financial
  Markets, Institutions and Risks* 10(3):130–168, DOI 10.61093/fmir.10(3).130-168.2026, received
  29 Jun 2026, published 26 Sep 2026 — a peer-review-stamped academic study of the rule's
  valuation relevance (30 SaaS firms, 2019–2024), published a month before the paper's own
  28–29 Oct 2026 literature pass.
- *Strongest author defense:* the hedge ("we are aware of / we located"); the venue is
  low-visibility and its review rigor may reasonably be discounted — but that position must then
  be argued; and Lee 2024's own venue (Applied Finance Letters) invites the same question once
  the criterion is in play.
- *Adversarial disposition:* SURVIVES (narrowed). *Affected conclusions:* framing only.
  *Smallest correction:* cite Nei et al. and state the venue criterion, or replace the sentence
  with a search-protocol statement (databases, queries, date). *Acceptance test:* the revised
  text names the protocol and either cites or explicitly excludes Nei et al. on stated criteria.

**F4. The release text contains an unresolved editorial marker.** Main Appendix A.6, p. 82:
"[R2: finalize once the author's review is complete]" (verified verbatim). Classification:
release-readiness defect. No defense; delete before release; acceptance test: no bracketed
editorial markers anywhere in the release PDF. (Trivial, but non-negotiable for a public
document.)

**F5 (should-fix, quantified). The familywise-correction family was chosen after the first
version's results were known; the paper discloses this, but not its quantitative consequence.**
- *Locators:* main §5.1, p. 42 ("the family was chosen after the first version's results were
  known"); App. A.4 item 4, p. 80; headline survival claims at pp. 42–43 and the abstract.
- *Classification:* disclosed researcher degree of freedom; the correction's implementation is
  exactly correct (Holm and Romano–Wolf verified by referee B).
- *Evidence (referee B's counterfactuals, re-checked by F):* the 14-member family excludes the
  headline frontier-point changes T(20%) and T(0%) while including T(40%)-related members;
  adding the omitted statistics (18–20-member families) moves the 2020–25 steepening's
  Holm-adjusted p from 0.037–0.060 to **0.048–0.084** — it keeps the 10% familywise level but
  loses 5%. The p95-decline result is unaffected.
- *Strongest author defense:* the choice is disclosed with its date and reason (D-3, Table 8);
  the primary claims are worded to match ("survives … at 10% under most procedures").
- *Adversarial disposition:* SURVIVES (narrowed; one-sentence fix). *Smallest correction:* add
  the counterfactual sentence to §5.1. *Acceptance test:* the revised §5.1 states the family's
  composition dependence.

**Minor findings (grouped by root cause per the adversarial dedupe; each verified; locators
re-pinned where reporters cited section-start pages).**

*Printed-number drift (the version-drift root cause, paper-text instance):*
- **M1.** §5.8, p. 47: Holm-adjusted p-values printed as 0.084 and 0.028 for the anchor-survival
  sentence; recomputation from the committed p-values gives **0.096 and 0.030** (referee B; F
  confirms this is a genuine printed-number error, not merely a package defect). Correct the
  digits; conclusion (survives at 10% under every type) unchanged.
- **M2.** Repo hygiene (B): `notes/paper_stats.json` and `notes/gap_decomposition.json` are
  stale v2 artifacts contradicting the paper's printed v3 numbers (F re-recomputed five §4
  statistics from `panel_v3.csv` — the paper is right, the artifacts stale); regenerate or
  delete before releasing the package. Relatedly, the repo's committed sources lag the supplied
  PDFs (Lead L2): a final-source commit is required so the release is reproducible.

*Basis/convention not stated at point of use (one presentation class; each its own sentence):*
- **M3.** Main §7.2, p. 58, parenthetical: the after-tax Proposition 4(d) bound treats customer
  capital k_a at the same ψ as physical capital, but Assumption 6 (p. 25) expenses customer
  acquisition when incurred (full deduction). The corrected bound exceeds the stated one by
  k_a·G·τ(1−ψ) = 0.84 points at the p. 26 illustration; zero in the §7.2 use (k_a = 0). One-line
  qualification (A).
- **M4.** §7.2, p. 56: "Counting the costs of accountability alone" still charges compute and
  fees; the numbers are right under the intended reading (c_full removed only), but the phrase
  invites the wrong one (D; arithmetic re-derived by F).
- **M5.** §7.3, p. 61: (i) the payback arithmetic is an expectation construction with two
  near-cancelling disclosed biases (dip overstated ~8% conservatively; gains at the Prop 7(e)
  bound); (ii) "Over the life of the program … gains are worth 3.9 times the dip" includes the
  post-completion tail — truncated at 2042 the ratio is ≈2.3 (D's diagnostic). Two phrases;
  the five-year-horizon conclusion is robust (D: even the most favorable reading leaves payback
  above 7 years).
- **M6.** §6, p. 52: the coupon-variant range 86.0–112.8 is computed on the interest-paid basis
  while the surrounding discussion is on the interest-expense basis (unstated switch); and the
  Q2 15.5% interest figure is cited to the prospectus (2026b) but comes from the 6-K (2026c)
  (C).
- **M7.** §6, p. 52: "22% to 28% of the time-weighted capital deployed" — the denominator is the
  *decayed* (written-down) stock, not outlays; the qualitative claim (return > 8.93% cost of
  capital) holds under both conventions (C).
- **M8.** §1 'How not to use' item 8, p. 6: "scores with acquisitions charged in full are lower
  bounds" is unconditional while Remark 4's inequality (31) is conditional (fails in a quiet
  year after an outlay year); Table 3's years satisfy the condition (C).
- **M9.** §4.3 pairing convention: the panel pairs past-year growth with contemporaneous margin
  throughout; §5.3 (p. 44) *does* report within-firm forward-pairing regressions as a partial
  check (referee C's broader claim is narrowed accordingly — the only cross-report clash,
  resolved in B's reading), but no forward-pairing variant exists for the frontier-facing Ψ/P95
  statistics, where capital-intensive outliers are convention-sensitive (CoreWeave: ~210 points).
  One convention sentence + an optional Table S4 variant (C, B).
- **M10.** Supp §S6, p. 28: the XBRL element list omits OperatingIncomeLoss (and the PP&E
  instant) — the tag behind the paper's GAAP headline margin; count should match "35" (C).

*Transport and scope conditionings (all disclosed; small concrete fixes):*
- **M11.** §7.2, p. 56 + supp §S2.8, p. 9: the 1% credible lower bound of the compute share is a
  per-*successful*-run cost (Kwa et al.: "more than 80% of successful runs…"; Table S11's own
  note says 50% success, no review); per completed process it is ~2%, moving the threshold's low
  end from 28% to ~29% (D; F re-derived). One clause.
- **M12.** Prop 5's "however many layers" (§7.2, p. 56; Remark S10, p. 50): correct within the
  beta-factor form; the cited CCF literature itself flags the form as conservative when not all
  redundant components are defeated (NUREG/CR-5485 — fetched and verified by D). Remark S10
  already scopes the conclusion to the example; add one acknowledgment sentence and optionally a
  per-layer defeat-share q sensitivity (D, F).
- **M13.** §8.5, p. 68: AS 2201 ".03" states the auditor's objective; the opinion obligation
  flows from Item 308(b)/Reg S-X 2-02 (substance correct; citation form) (D).
- **M14.** §2.2, p. 9: Lee (2024) "1,756 SaaS firms" vs **1,771** in every occurrence of the
  MPRA version; the published AFL text was inaccessible (Cloudflare) — verify and correct to
  the cited version's number (E).
- **M15.** §2.7, p. 12 lists "non-identification of firm frontiers from chosen points" among
  results "we believe are new" while §2.1, p. 8 concedes its Marschak–Andrews parentage; rephrase
  as a new *worked instance* (E; §2.7's framing sentence partially mitigates).
- **M16.** Bib/URL hygiene: Vista (2026) URL now dead-ends (cite the archived snapshot, verified
  full text via Wayback); Svanberg et al. full text unverifiable (SSRN) — the upkeep/integration
  rows feeding δ_M are disclosed as class b/d precedents; add an a_min sensitivity over
  δ_M ∈ {0.10, 0.40} (E, D).

*Process notes (not defects of the paper's text):*
- **M17.** The purged registrant (App. A/Table 8) is identified by digest inversion as [excluded registrant],
  CIK [CIK], **SIC 7374** (F re-derived SHA-256("[CIK]") = the stored digest; live SEC API
  confirms). Since the estimation sample is SIC 7372 (p. 36), the paper's "outside the
  estimation sample, so no figure depends on it" is **true for this paper**; the caveat is that
  the purge also covers the companion paper's data, where the SIC defense may not apply — state
  this in App. S6 and archive the pre-purge panel hash.
- **M18.** SFA (stochastic-frontier) MLE outputs are not bit-reproducible across environments
  (≤2.3e-8 point differences; ≤2e-3 interval-endpoint differences — both benign optimizer-path
  effects, and the only deviations in the entire replication); add a one-line reproducibility
  footnote (B).


---

## 6. Empirical assessment: what was and was not reproduced (deliverable D)

**Reproduced (four independent routes, all executed in this review):**
1. **Text ↔ committed outputs.** All 164 cells of Table 2 (estimates, standard errors, intervals
   across the four sample views), every §5 text statistic, Table 5's anchor panel and Table 7's
   lever cells reconcile with the author's committed JSON/TeX outputs at printed precision
   (referee B; zero substantive deviations).
2. **Author's code rerun.** `estimate_v3.py` point estimates regenerate in ~38 s in a fresh
   environment; the full pipeline including the **999-replication firm-cluster bootstrap** was
   run to completion (~88 min): regenerated tables (`tab_estimands_v3.tex`, `tab_yearly_v3.tex`,
   `tab_bridge_v3.tex`) and anchors (`calibration_anchor_v3.json`, `paper_stats.json`) are
   **byte-identical**; frontier slopes differ at machine epsilon (8.3e-16); the only deviations
   anywhere are ≤2×10⁻³ on SFA MLE interval endpoints (optimizer-path noise; see M18). The
   bootstrap seed scheme (20261030 + CRC-32 of block names, as documented in Table 2's notes)
   reproduces the published draws deterministically.
3. **Independent reimplementation.** Referee B's own code (imports only numpy/pandas — verified
   by F's grep; no author code executed) recomputes every headline statistic from
   `panel_v3.csv` to ≤5×10⁻⁴: the Ψ₀.₉₀ slopes by period and window, the p95 changes −11.9/−12.7,
   T(0%)/T(20%), the spend ratio 3.024, the margin-gap decomposition (34.5 with S&M/R&D/G&A/
   gross-margin parts 16.0/7.1/5.7/5.5 and the 29.4-of-41.3 / 14.4-of-36.4 band illustrations).
   Data pairing verified row-by-row: growth is computed within the same first-reported filing as
   the margin for all 1,788 firm-years.
4. **Reduced independent bootstrap.** B's own 199-draw firm-cluster bootstrap (seed 20261103)
   reproduces the published 90% intervals within noise and verifies every interval rule
   (undefined-draw rule; the T(40%) dagger at ~5.8–6.5% undefined draws; E2's 60%-cell thinness
   15.1%/12.6% vs published 16.8%/13.0%; conditional intervals on defined draws).
5. **Case-study arithmetic** (referee C, from primary filings fetched in full; re-grepped by F):
   every Bending Spoons number in Table 3 and the abstract (115.9/105.0/87–114/160/22–44; all
   four charged-as-capital sub-ranges; the 79–103 double-charge illustration; k_acq 1.73/2.30/
   3.23), Palantir 155/140/88 (155 is the company's own reported metric), CoreWeave 167/14, and
   the §4.6/Table S10 panel statistics (1,788/292; pass rates 14.3/15.9/26.6/30.5%; the −11.4→
   −11.0 interest/tax bridge; the 0.27 deferred-revenue median → 26% threshold).
6. **Calibration code.** `calibrate_horizons.py` rerun reproduces every §7.3 number (referee D);
   `verify_part2_acquirer.py` passes 82/82 checks; `verify_theory.py` cataloged (26 sections)
   and its Prop-2 solver re-run — its solution contains the v′ U-shape (§5 F1).

**Not reproduced / not verifiable in this review (with the reason):**
- The **panel construction from SEC EDGAR** was not re-executed from source: the repo archives
  an 11 MB derived companyfacts extract (purged of the excluded registrant) and encoded fetch
  lists, but not the raw EDGAR responses; the build from EDGAR therefore rests on build logs,
  panel hashes and the paper's sample rules (which B verified as applied: counts 292/1,788,
  R1–R5 arithmetic, flag coverages 26%/42%).
- The **Lee (2024) published AFL text** (Cloudflare) and **Roche & Tandon (2021)** (McKinsey
  403, unarchived) were not verifiable; the **Svanberg et al. full text** (SSRN CAPTCHA) could
  not be checked for the upkeep/integration parameter rows.
- Table 7's g+δ column was not independently re-derived (B's stated hole).
- No claim anywhere rests on re-pulling the upstream frames; upstream-first-reported fidelity is
  supported by the build code, logs and the paper's own vintage caveats (interest/taxes are
  latest-filed by frames' design — disclosed).

**Estimand assessment (B).** The Ψχ partial-frontier orientation (χ-quantile of margin among
firm-years growing at least g₀) is coherent for two desirable outputs; the paper never claims
technology identification from it — §5's claims are consistently stated within Proposition 3's
non-identification concession (checked end-to-end). The E1/E2/imputation estimands are a
sensitivity set (shared firm-years), as the paper itself says; the familywise issue is §5 F5.

**What a full replication package needs for 100% reproduction:** the final-source commit of the
supplied PDFs' tex; regeneration or deletion of the stale v2 artifacts (M2); the raw EDGAR
responses or the pre-purge companyfacts extract hash; the AFL-version Lee citation resolution.

---

## 7. Citation / parameter-source ledger (deliverable E — summary)

The full 36-entry ledger with access levels, quoted source text, and transport judgments is in
`first_reports/E_prior_art.md`; fetched primary artifacts are archived under
`diagnostics/prior-art/`. Summary of judgments:

- **Verified exact / faithful (≈30 entries):** Feld 2015 (origin story, verbatim); Deeter & Bondy
  2024 (private ~2×, public 2–3×, 2–9× range, both R² — exact to the digit); Depeyrot & Heap 2018
  (86 firms, 16%, double EV/revenue); Bosche et al. 2022; Vista 2026 ("emerging aspiration" —
  the source's phrase; verified via archived snapshot); Lipman et al. 2026; Palantir 2026 (the
  company's own 155, definition and both margins verified at the 8-K); Bending Spoons filings
  (existence, forms, dates, material-weakness quote, unaudited organic measure); CoreWeave (10-K
  XBRL); Cottier et al. 2024 (2.4×/yr) and 2025 (9–900×/yr); Gundlach et al. 2025 (5–10×/yr;
  3–18×/yr); Demirer et al. 2025 (−1.11, substitution-vs-aggregate caveat faithfully carried);
  Moody et al. 2026 (NIST IR 8547: 2030/2035, final version); OMB 2024 ($7.1B, 2024 dollars,
  "rough order of magnitude" — both the source's words); Svanberg et al. (23% claim exact);
  Brynjolfsson et al. 2025a/b; Humlum & Vestergaard; Dell'Acqua et al. (12.2%/25.1%/−19pp vs the
  2023 WP — published-version numbers uncheckable); Becker et al. (+19%); Bick et al. (1–5%);
  Bonney et al. (3.7→5.4%; 18%/32%/57%); ~25 Crossref bibliographic records — **all matched**;
  Mosleh/Hokstad/Eckhardt/Knight-Leveson/Littlewood-Miller (fetched by D: beta-factor "most
  common form," the CCF conservatism caveat, and the multiversion-software findings support the
  attributed claims).
- **Transport problems (3):** the uniqueness claim (F3); Lee's 1,756 vs 1,771 (M14); the 1%
  success-conditioned compute bound (M11). No misattributions, nonexistent works, wrong years, or
  cross-denominator rate additions were found anywhere in the verified set.
- **Unresolved (2):** Roche & Tandon content (inaccessible); Svanberg case-study parameter rows
  (unverifiable; disclosure adequate).
- **Novelty verdicts (bounded search — do not upgrade to "verified new"):** score budget (Prop
  1) — no antecedent found stating a finite integral budget of score-above-saturation in
  exchange for log share headroom (nearest: Marris's qualitative demand ceiling); the Prop 2
  Rule-of-X reading + Lemma 5 duration screen — plausibly new, properly hedged, conditional on
  (H); non-identification — new *worked instance* of a classical problem (M15); the Prop 5
  control-design floor — plausibly new and properly scoped (adjacent AI-auditing literature
  should be acknowledged); Props 6–7 — plausibly new as a formalism (standard ingredients); the
  §2.3 estimators claim ("we have not found prior applications…") — survives the panel's bounded
  search (Ge & Huang 2014 SFA-on-SaaS should be acknowledged as adjacent); no practitioner
  source estimates a growth–margin frontier (Bessemer's regression slope is the closest object
  and is cited and correctly distinguished).

---

## 8. Independent verification: scripts, results, environment (deliverable F)

All scripts are archived under `diagnostics/` in the output folder (with raw outputs); seeds
recorded (base 20261103). Environment: Python 3.12.3; numpy 2.5.2; scipy 1.18.1; sympy 1.14.0
(50-digit spot checks); pandas 3.0.3; statsmodels 0.15.0; mpmath 1.3.0. Panel data SHA-256
hashes verified unchanged across all runs.

| Component | Contents |
|---|---|
| `diagnostics/lead/` | Lead's 15-check script + output (frontier identity on 20k draws; closed-form max vs scipy on 5k draws; Corollary 1 examples; Table 4 all cells; 32.5 decomposition; Lemma 5 example; Table S3; Rule-of-1000; execution 41%/61%; accountability example; Lemma S2(a) sympy residual = 0; Bending Spoons arithmetic). Records two initially-failed checks that were the Lead's own script errors. |
| `diagnostics/A/`, `diagnostics/A2/` | Referee A's 76 inherited checks (42 symbolic, 16 numeric, 11 dynamic, 7 HJB) + A2's U-shape investigation (analytic terminal-balance derivation; backward-shooting solution; the author's own `solve_hjb` grid re-run; genericity sweep). |
| `diagnostics/econometrics-empirics/` (incl. `b2/`) | B/B2's reconciliation tables, independent reimplementation scripts (numpy/pandas only), 199-draw bootstrap, Holm counterfactuals, sample-rule audits, panel hash records; the full-bootstrap rerun and its diff log (`execution_logs/full_bootstrap_replication.md`). |
| `diagnostics/accounting/` | C's recomputation script for the Bending Spoons/Palantir/CoreWeave cases + the full fetched filing texts (F-1, 424B4, 6-K exhibits, Palantir 8-K exhibits) used as primary evidence. |
| `diagnostics/D/` | D's independent Monte-Carlo execution model (embedded/realized shares, dips, payback, NPV, double-count variant, attainment check), Prop 5 re-derivation, Table S16 row-by-row hand checks, author-code rerun log, primary-source verification ledger (AS 2201, Reg S-K, SEC releases, NUREG, NIST, OMB). |
| `diagnostics/prior-art/` | E's fetched primary sources (Palantir and Bending Spoons filings, Nei et al. article, Vista snapshot, NIST/OMB PDFs, NBER/arXiv records, Lee MPRA text) + the 36-entry ledger. |
| `first_reports/` | The five preserved specialist first reports (A–E) + the Lead's pre-panel argument reconstruction. |
| `adversarial_audit/` | Referee F's audit: per-finding dispositions, dedupe, severity triage, circularity attacks, locator spot-checks (25+ sampled; zero misquotes; five page-citation re-pins incorporated in §5). |

Evidence-type labeling (per protocol): **symbolic verification** (sympy): the Lemma 1–5/Remark 2/
Prop 4 identities, Lemma S2(a) — A's s1 and the Lead's check 10. **Hand derivation**: A's
terminal-balance argument (independently re-derived by F), D's Prop 5 algebra, C's Remark 3/4
identities, the Lead's dR*/ds rederivation. **Numerical evidence**: all Monte Carlo, grids, and
randomized checks (labels [MC]/[NUM]; fixed seeds; tolerances recorded in the scripts).
**Simulation**: D's execution-model MC; A's path integrations. Passing many random tests does
not prove the universal claims; the U-shape finding rests on the analytic argument, with the
numerics as confirmation.

---

## 9. Revision sequence and claim-level corrections (deliverable G)

**Phase 1 — must-fix before any release (each independently re-verifiable):**
1. Delete the `[R2: …]` marker (App. A.6, p. 82).
2. Correct the four v′-shape sentences (F1) and add the three HJB-grid checks to
   `verify_theory.py` (they fail the current wording and pass the corrected one).
3. Correct §6's five availability sentences and fill Table 3's organic rows (F2); re-run the
   full-text acceptance search on the F-1/424B4.
4. Revise the "only peer-reviewed study" claim with the search protocol / Nei et al. (F3).

**Phase 2 — should-fix (text-internal; no re-analysis needed):** add the familywise
counterfactual sentence (F5); correct the §5.8 digits (M1); the basis/convention one-liners
(M3–M7, M9, M10); the transport clauses (M11–M13); the citation corrections (M14); the §2.7
rephrase (M15); the bib/URL and sensitivity additions (M16); the App. S6 exclusion note with the
pre-purge hash (M17).

**Phase 3 — package integrity for release:** final-source commit (the supplied PDFs' exact tex);
regenerate or delete the stale v2 artifacts (`paper_stats.json`, `gap_decomposition.json`;
fix `paper_stats.py` to read the v3 panel); archive raw EDGAR responses or publish the pre-purge
extract hash; resolve the Lee AFL-version number; add the SFA reproducibility footnote (M18).

**Claim-level corrections (what the revised paper may say):**
- "…the firm's own weight is largest at small share, falls with share to about 80% of the cap in
  the worked example, and rises back to the never-spend multiple (m₀−kG)/(r−G) at the cap;
  retention gains do not vanish at saturation."
- "…a sustained cash-basis Rule of 100 requires the levers jointly to push the durable score above
  100" — unchanged (verified), as are all quantitative results (the panel found no incorrect
  number in any table).
- "…the only peer-reviewed academic study of the rule meeting [stated criterion] is Lee (2024);
  Nei et al. (2026) examine the rule's valuation relevance in a low-visibility venue and do not
  estimate a frontier."
- The empirical claims need no correction; the familywise sentence gains the counterfactual.
- Everything conditional on (H) stays conditional (the labeling is already consistent).

**Evidence required to accept the revised claims:** the four Phase-1 acceptance tests (all
runnable mechanically: bracket-marker search; the three HJB-grid checks; the §6 full-text
search; the search-protocol statement), plus the Phase-2 one-liners.

---

## 10. Editorial assessment and recommendation (deliverable A)

**What the paper is.** An unusually rigorous working paper: a compact analytical core (concave
growth–margin frontier, price-line reading of the Rule of 40/X, five limit mechanisms) whose
every formula and number the panel could check was independently rederived or recomputed; an
empirical panel built from first-reported SEC XBRL with pre-registered sample rules; a
calibration labeled as scenario throughout; and a case study that survives recomputation from
the primary filings to the decimal. Its replication package is the strongest this panel has
processed: the full pipeline, including the 999-replication bootstrap, regenerates
byte-identical tables and anchors in a fresh environment, and an independent reimplementation
reproduces every headline statistic to ≤5×10⁻⁴.

**What is wrong with it.** Nothing structural. Four must-fix items — one release marker; four
sentences about the worked example's weight profile that generalize beyond what was computed
(and are false over 80–100% of the share cap, a defect the author's own solution contains but
never tested); five sentences about what the Bending Spoons filings disclose that are false
about filings the paper cites as read (the disclosed annual figures would strengthen the
paper's case); and one uniqueness claim contradicted by a second journal study. A disclosed
post-hoc inferential choice deserves one quantified sentence. The remaining ~14 items are
one-line basis/labeling/transport fixes. No theorem is false; no number in any table is wrong;
no empirical claim exceeds what the data identify (the paper's non-identification concessions
are consistent end-to-end); no citation is fabricated; no regulatory threshold is invented; and
the Bending Spoons and Palantir claims are faithful to the primary sources.

**Defensible contribution.** (i) The price-line/tangency reading of the Rule of 40/X with the
closed-form maximal score; (ii) the score budget (Proposition 1) — the paper's best claim to a
new result; (iii) the firm-vs-investor weight distinction (conditional on (H)) and the
duration-derived screening weight; (iv) non-identification as a worked instance; (v) the
accountability floor as a control-design standard under common-mode failure (properly scoped);
(vi) the attainable/expected frontier formalism; (vii) the first partial-frontier estimates on
the growth–margin plane of software firms with disciplined estimand policy; (viii) the
acquisition-charging methodology (Prop 8/Remark 4) demonstrated on a live serial acquirer.

**Recommendation.** **Major revision, with acceptance expected once the four must-fix items and
the Phase-2 one-liners are executed** — for an interdisciplinary economics/finance/technology
working-paper outlet this is close to the strongest state a referee report can find: the
analytical core replicates symbolically and numerically; the empirical core replicates
end-to-end; the case study replicates from filings; the disclosures are candid; the defects are
sentences, not results. For a journal, the publication standard shifts by contribution type:
as a *theory* paper it would need (H) proved (the paper itself says it cannot yet do this —
for a theory outlet the decision-weight result must be presented as an explicitly conjectural
reading, or the existence proof supplied); as an *empirical* paper it needs only the Phase 1–3
items plus the raw-EDGAR archival note; as a *practitioner/regulatory* piece it is already
careful (no invented thresholds; pass-fail standard quoted accurately). The panel's unanimous
positive replication verdicts are single-model evidence and should be re-run by any editor with
different tooling — every script needed is archived.

---

## 11. Uncertainty statement and coverage ledger (deliverable H)

**Not covered by this review.** (1) Any material in the quarantine (prior referee rounds and
author responses) — deliberately unread; the review is therefore blind to whether any finding
here duplicates a prior one. (2) The companion papers' content (the repo's part2/engine; only
their interfaces with this paper were examined). (3) Human-expert judgment on the auditing,
tax, and valuation-practice questions (C and D verified texts and arithmetic, not professional
practice norms). (4) The published AFL version of Lee (2024); Roche & Tandon's content; the
Svanberg full text — unverifiable (flagged, not alleged). (5) The upstream EDGAR extraction
(trusted on build logs + hashes; downstream fully replicated). (6) Whether (H) holds in
parameter regions beyond those tested — open by the paper's own statement.
(7) Single-model evidence: all panel members are contexts of the same model family in one
harness (with unstable platform model-labels, disclosed in §0); the strongest evidence here is
deterministic (scripts, hashes, fetched primary sources), which referee F re-executed wherever
material.

**Coverage ledger (pages actually read).** Lead: main pp. 1–82 in full (all 82 pages), supp
pp. 1–10 (S1–S2.6) + structural survey of the rest; referee A: main §§3–7.5, supp S1–S3, S8
proofs; referee B: main §§4–7, supp S6; referee C: main §§1, 3.1, 3.11, 4–8.3, supp S1, S2.8,
S4, S4.1, S6, S8; referee D: main §§3.9–7.4, 8.5–9, supp S2.6–S2.9, S3, S6, S8, Table S11;
referee E: main §2 + all cited sources; referee F: all five reports + targeted pages for 25+
locators. Not read by anyone: the reference-only pages of the main paper were skimmed, not
line-audited (bibliographic verification was Crossref/fetch-based); supp S5 (Rule-of-1000
details), S7 (protocol records), S9 (glossary) were covered only through their interfaces with
audited claims. Text extraction was checked against rendered page images where notation was
consequential (the Prop 5 product formula, corrected via code and re-derivation).

**Residual uncertainties passed to the editor.** (i) (H) unproved — all decision-weight
statements, including the corrected U-shape wording, remain conditional; (ii) the b_p realized-
share distribution is unspecified (only its mean), so 2036 "41%" is an expectation whose
dispersion is unidentified — a two-point sensitivity would close D's open question; (iii) the
stock-vs-flow reading of change capacity sits exactly at the capacity line in the fast-execution
case; (iv) the uniform program clock is an a.s. long-run limit applied over 11 years (the paper's
own S2.7 flags this); (v) the interim-period mapping of the 24 control occasions; (vi) whether
the 60% labor share replaced by compute in §7.2 includes SBC (if not, the ceiling is not
directly comparable to the after-SBC scores it is set against); (vii) the 2024 $162.5M
intangibles purchase's classification (asset deal vs IP purchase) shifts charged scores by
≤1.8 points either way.

**Completion check performed.** Each major objection was adversarially attacked before
inclusion (F re-derived the decisive evidence); the abstract, executive summary, §5, §7 and all
tables were reconciled against the panel's audits; no claimed execution in this report exceeds
what was performed (all scripts, logs, fetched sources and the full first reports are archived
in this package); the two failed Lead checks were traced to the Lead's own script errors and are
recorded; inaccessible evidence is listed above. This report was preserved before any comparison
with prior critiques, which remain unread.

*— End of the panel's consolidated report. Artifacts: `first_reports/` (A–E + Lead),
`adversarial_audit/F_audit.md`, `diagnostics/` (all scripts + raw outputs),
`execution_logs/full_bootstrap_replication.md`, `SOURCE_MANIFEST.md` (frozen evidence boundary,
hashes, and quarantine record).*
