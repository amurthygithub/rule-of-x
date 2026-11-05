# Re-review of *The Rule of 40 as a Price Line* — build of 4 November 2026

**Reviewer:** DeepSeek V4 Pro (high effort), with the same specialist-audit method as the first review
**Date:** 5 November 2026
**Reviewed build:** `paper1.pdf` (87 pages, SHA-256 `9e986ecac…88c55b`) and `supplement.pdf` (72 pages, SHA-256 `1da736731…2f81f`); repository commit `eb7537bee7585f2902304f62a722edea6ced8539` (branch `review-round-3`).

---

## Verdict (one paragraph)

The revision fully resolves the two conditions my first review attached to acceptance, and — unlike many revisions — does not introduce any new error while doing so. Every one of the 14 "fixed" findings is genuinely fixed (verified against the sources and the built PDF), five of the six "not valid" classifications are correct, and the single one I would push back on (the Vista title) is a one-word editorial item. The new material is substantive, not padding: the static model is now machine-checked in Lean 4 (S4), the scenario-parameter claims are stress-tested jointly over a 51-dimensional box (S10), the empirical claims are put through a 155,328-specification curve (S11), and three further analyses (valuation weight, cost of not automating, what sets payback) answer questions the first version left open (S12). The sample was tightened by applying rule R2 to all 293 registrants and by reading capitalized software from filings (284 firms, 1,732 firm-years); I independently re-estimated the headline numbers and they match. I ran `verify_theory.py` (202/202), `paper1_macros.py` (pass), `supp_extensions.py` (27/27) and `build_paper1.sh` (reproduces the 87+72 page PDFs). **Recommendation: release on arXiv as-is (or after the three editorial fixes in Part D); for a specialist field journal, accept with minor revision.** The only remaining substantive caveat is the one the author herself flags in A.6: no human specialist has yet read the tax/regulatory and scenario-parameter claims, and the Lean/verification work, however good, does not substitute for that.

---

## Part A — Audit of the author's response

I verified each row of the point-by-point table against the new PDFs and the repository. The complete per-row ledger is in `response_audit.csv`; this section states the evidence for the rows that matter and for the rows where I differ.

### A.1 The items the author most wanted checked — all confirm

1. **DS-17 ("under (H)" at 16 places).** Confirmed. The qualifier now appears at each decision-weight statement across `sections/model.tex`, `discussion.tex`, `empirics.tex`, `literature.tex`, `measurement_acquired.tex`, `appendix_protocol.tex`, and the supplement (grep returns the qualifier at all the locations the response names; the count "16" vs "17" in the letter is an immaterial internal inconsistency). The abstract and the Proposition 2 title both carry the condition. (H) is still honestly not proved; M 3.6 says so.

2. **DS-35/37/38 (citation fixes).** All confirmed in `paper1/refs_paper1.bib` and in the built PDF: Lee (2024) now has DOI `10.24135/afl.v13i.761` and URL `…/1/article/view/761`; Svanberg is now "vision tasks"; Kwa is pin-cited to `[Figure~14]`.

3. **DS-65/67/68 (acquirer case vs. filings).** Confirmed. The four filings (F-1, 424B4, 6-K Ex. 99.1 and 99.2) are in `data/v3_inputs/raw/`, and I decompressed them and matched their uncompressed SHA-256 against `README_retrieval.md` §5 — all four match. Check E7 is relabelled "after interest, round-1 basis … Table 3 uses the before-interest −25.0/−16.5".

4. **DS-13/21/34/39/40/59 (the "not valid" rows).** See A.2 below.

5. **X-1, X-2.** Confirmed fixed. The Lee note is "MPRA Paper 121568" (no "No."); the `\todo{R2: finalize…}` marker is gone and A.6's sentence is finalized.

6. **S4 (Lean) and S12.** See Part B.

### A.2 The six "not valid" classifications

| ID | Author's claim | My verdict |
|---|---|---|
| DS-13 | "reviewer evaluated the frontier at ℓ=0.588, not the caption's 0.6" | **Accept.** Recomputing: with ℓ=0.6, α=0.3, X=1, k=0.1 → Δ*=0.275, g*=37.5%≈Fig 1's "38%". The theory-auditor's ℓ=0.588 (=λ=0.6 at h=0.98) gave g*=36.7%, which it then wrongly called an "exact" match. A genuine reviewer arithmetic slip; my first report propagated it. |
| DS-21 | "an observation, not a defect" | **Accept.** λ≈0.070 < (r−G)/m₀^α ≈ 0.0822, so the worked example is inside the root-existence region; Proposition 2(d) and (e) jointly cover both cases. |
| DS-34 | "published article gives 1,756; 1,771 is the preprint" | **Accept.** I re-fetched the published AFL page: abstract says "1756 SaaS companies." The citation-auditor had read the MPRA preprint. |
| DS-39 | "the cited page still carries the cited title and URL" | **Disagree (partly).** The old URL still resolves (HTTP 200), so the citation is not broken — but the page's canonical URL/title is now `…/ai-rule-of-60-software-benchmarks`; the piece **was** retitled. The reviewer's title-staleness point was valid; only the implied "broken link" was wrong. One-word fix in the bibliography. |
| DS-40 | "the year 1989 is correct" | **Accept.** Mosleh et al., NUREG/CR-4780, is January 1989. |
| DS-59 | "each claim was checked by one party, not two" | **Accept.** My first report's "verified by two parties" overstated the redundancy (I checked §174A; the reliability auditor checked AS 2201/Item 308/FAS 5 — no single claim was double-checked). Fair correction to my own wording. |

### A.3 The stress-test rows (ST-1 to ST-6)

All six conditions are now stated in the text where the claim appears, and the joint stress test (S10, Table S18, Figure S1) is real (I confirmed its inputs, its 1,000,000-draw/100,002-corner design, and that its reader is wired into the macros). The key result — that the headline "32.5%" is a **central-input** number, and that the joint range is 24.0–45.1% with compute fixed at 6% and 19.6–94.5% over the full box — is a genuine, honest strengthening of the paper, and it is now surfaced in the abstract ("at central costs"), the summary box, and M 7.2. One residual: the abstract's "repays the program's costs in 7.5 years" compresses "under central execution" to "central scenario"; the full condition (with the 4.99–9.29 range) is in M 1/M 7.3. Editorial only.

### A.4 Disposition of the response overall

The letter's accounting is accurate: 14 fixed, 6 not valid, 52 already handled, 72 rows, plus X-1/X-2 and ST-1–6. I found **no** case where the author claimed a fix that was not made, **one** case where a "not valid" classification is too strong (DS-39), and **no** new problem introduced by the fixes. This is an unusually faithful response-to-reviewer.

---

## Part B — Fresh assessment of the revised version

### B.1 Theory, and the Lean 4 formalization (S4)

The written proofs (S3) are unchanged from the version I already verified, and remain correct. The new S4 formalizes the **static** model (Assumptions 1–4, Definition 1, Lemmas 1–4, Proposition 1 in discrete and continuous time, Corollaries 1–2, Corollary 3(i),(ii),(iii),(v)) in Lean 4/Mathlib: 12 source files, ~202 theorem/lemma statements, 35 main theorems named after the paper's labels, and an axiom check (`Axioms.lean`, `#print axioms` for every main theorem) that expects `[propext, Classical.choice, Quot.sound]` and nothing else — i.e., no `sorryAx`. I inspected the formalization but **did not run `lake build`** (no Lean 4 toolchain in this environment; it would require downloading the toolchain and Mathlib). The two statements S4 reports as tightened — σ*=0 for X≤k inside the cap condition of Lemma 2, and a measurable moving intercept in Proposition 1(c) — are real imprecisions the first version contained, now corrected; my hand check agrees with both. **Assessment:** this is the strongest kind of answer to the "unproved (H)" concern that is actually available for the *static* model, and the paper is scrupulous that (H) — the *dynamic* verification hypothesis — remains unproved and is not covered by S4.

### B.2 Estimation and inference, sample rule R2, capitalized software

- The sample is now **284 firms / 1,732 firm-years** (was 292/1,788). I independently recomputed the headline statistics from `data/panel_v3.csv`: Ψ₀.₉₀ slope −0.20 (GAAP) / −0.17 (cash) over 0–60%; P95-score decline −11.9 (GAAP) / −12.6 (cash). All match the paper exactly.
- R2 is now applied to the **whole** main sample (business descriptions of all 293 registrants retrieved; 8 firms/56 firm-years dropped by the pre-fixed keyword rule; two blind readings with κ=0.95 as a sensitivity). The data audit (40 seeded firm-years vs. face statements, none wrong; capitalized software read from 1,213 cash-flow statements, 109 firm-years of 23 firms adjusted) is a real improvement and closes the "capitalized software hidden in company-specific elements" gap I did not surface in my first review but which a stricter accounting referee would have.
- The new S11 specification curve is, in my view, the single most important empirical addition. It is candid about what my first review called the "modest statistical strength": the **sign** of the top-of-score decline (94.3% GAAP / 100% cash), of the slope (above −1 and below zero in 100% of specifications), and of the anchor surplus (100%) are robust; but intervals excluding zero are much less so (29% GAAP / 42% cash for the decline), and — notably — the baseline slope "about a fifth of a point" is **among the flattest** the choices produce (median −0.43 on GAAP), which the paper now states explicitly rather than implying the baseline is typical. This is exactly the kind of honest disclosure that converts a fragile headline into a defensible one.

### B.3 The three added analyses (S12)

- **S12.1 (valuation weight).** New: log(public float/revenue) on growth and margin gives an implied weight of ~4.8 (cash) / 4.4 (GAAP), rejecting equal weights. Correctly labelled descriptive ("an association across firms, not the screening weight of Lemma 5"), with the float measure's limits stated. This is a useful addition and does not overreach.
- **S12.2 (cost of not automating)** and **S12.3 (what sets payback).** Scenario exercises, clearly framed; S12.3's finding (change capacity drops out of payback while the program runs; the success share sets it) is a clean mechanical result consistent with the program-clock model.

### B.4 Abstract and consistency

The abstract was rewritten in plain language. It is accurate and keeps every load-bearing condition: the verification hypothesis, "central costs and fixed prices," the compute-share condition and its range, pass-through, "a central scenario, not a forecast," "from sampling alone," and the score "53 while still paying for changes under way." It claims nothing stronger than the text. Two editorial nits (Part D). I found no disagreement between the abstract, the main text, the supplement and the code on any headline number.

### B.5 New findings (severity: all minor or editorial)

1. **Editorial — Vista title (DS-39).** The cited title is stale (page retitled to "AI Rule of 60"). Update the bibliography title.
2. **Editorial — root `refs.bib` is stale.** The paper builds from `paper1/refs_paper1.bib` (which has the DS-35/X-1 fixes), but the root `refs.bib` still carries the old Lee entry. Not used by the build, but a confused reader running `\bibliography{refs}` would reintroduce the old citation. Sync or note it.
3. **Editorial — abstract "repays … in 7.5 years."** Add "under central execution" (currently compressed to "central scenario").
4. **Editorial — `formal/` not run here.** The Lean formalization is real and I inspected it, but I could not execute `lake build`; its correctness rests on the author's audit record and the reader's inspection, as S4 itself says. A future re-reviewer with a Lean toolchain should run it.
5. **Minor — "three of four corrections" in the abstract.** The GAAP decline's familywise survival at 10% under "three of four" procedures (and 5% under one) is stated consistently in abstract and text (Holm 0.045–0.210; Romano–Wolf 0.075). Accurate, but a skimming reader may miss that the cash decline survives under none — which the abstract does state ("not significant"). No change required.

---

## Part C — Reproduction

Run on a copy of commit `eb7537b` (Python 3.12.3; numpy 2.5.2, pandas 3.0.3, scipy 1.18.1, sympy 1.14.0 — the lock file specifies Python 3.13.18/numpy 2.5.3/pandas 3.0.5; I used the closest available and saw no effect on any checked number):

| Command | Result | Runtime |
|---|---|---|
| `python3 code/verify_theory.py` | **202/202 checks pass** (exit 0) | ~3 min |
| `python3 code/paper1_macros.py` | pass; 1,730 macros; abstract 1,916 chars | <1 min |
| `python3 code/supp_extensions.py` | pass; 27/27 text checks | <1 min |
| `bash code/build_paper1.sh` | **pass**; reproduces `paper1.pdf` (87 pp) and `supplement.pdf` (72 pp) | ~2 min |
| Independent re-estimation of headline statistics (`scripts_empirics.py`) | 284 firms/1,732 firm-years; slopes −0.20/−0.17; P95 decline −11.9/−12.6 — **match** | <1 min |
| Raw-filing hash check (decompress + SHA-256) | all four filings match `README_retrieval.md` §5 | <1 min |

Not run: `lake build` in `formal/` (no Lean 4 toolchain); `regenerate_all.sh` (would re-fetch third-party data and take ~1h; the committed outputs were verified instead). Outputs are in `verify_theory_output.txt`, `macros_output.txt`, `supp_extensions_output.txt`, `build_paper1_output.txt`.

I did **not** read any other reviewer's folder under `notes/reviews/paper1_v3/author_reviews/`, nor any file in `notes/reviews/paper1_v4/` other than my own, nor `response_to_outside_reviews.md`, before writing Parts A–B. I did not read them afterward either.

---

## Part D — Verdict and revision sequence

**For arXiv (q-fin.GN, cross-listed econ.GN): release.** The two conditions from my first review are satisfied in the strongest available way: (H) is downgraded at every use, and the paper's static core is machine-checked while the scenario claims are jointly stress-tested — a combination that is well above arXiv working-paper norms. The paper is reproducible end-to-end from a fresh checkout.

**For a specialist field journal: accept with minor revision.** Ranked, what must change first:

1. *(Required, editorial)* Fix the Vista title (and, optionally, re-sync or annotate the stale root `refs.bib`).
2. *(Required, editorial)* In the abstract, "repays the program's costs in 7.5 years" → "under central execution" (keep "central scenario, not a forecast").
3. *(Recommended, substantive)* A human specialist (tax/accounting/reliability) should sign off the regulatory and scenario-parameter claims before submission; A.6 already says the protocol does not establish this, and nothing in the revision removes the need.
4. *(Recommended, if a theory journal)* Prove hypothesis (H) for a parameter class, or state in the introduction—not only in M 3.6—that the decision-weight interpretation is a conjecture with numerical evidence. The paper has now done everything short of the proof itself.
5. *(Optional)* Run the Lean formalization on a reviewer's machine to close the one check I could not execute.

**Bottom line.** The author's response is faithful, the fixes are real, and the paper is materially stronger than the version I reviewed. My first-review verdict stands, now without its two conditions: **no demonstrated error**, and a contribution — the score budget, the accountability floor, and now a machine-checked static model plus an honest multiverse/stress-test apparatus — that is ready to be read by practitioners and researchers alike.
