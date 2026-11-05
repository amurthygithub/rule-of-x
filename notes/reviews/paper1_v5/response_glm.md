# Response to your re-review of *The Rule of 40 as a Price Line* (build of 4 November 2026)

**To:** GLM 5.3 (high effort)
**From:** Akshaya Bangalore Sreenivasa Murthy (author), with the lead agent of the research session
**Date:** 5 November 2026
**Your re-review:** of the build of 4 November 2026 (main paper 87 pages, SHA-256 9e986eca…; supplement 72 pages, 1da73673…) and the repository at commit eb7537b
**Your verdict:** release as an arXiv working paper after three minor fixes (NB1 to NB3) and an editorial sweep (NB4 to NB10), with one residual (NB11); all round-1 majors and minors resolved or defensibly declined.

Thank you for the re-review, for the four concessions in Part A, and for the correction of our round-1 record on M12, which was right.

**How we handled it.** An agent on `claude-fable-5-1` verified each of your fourteen items against the paper, the code, the stored stress-test outputs, a full rerun of `code/verify_theory.py` and primary sources, and classified each as valid, partly valid, not valid or already handled. The author adopted every fix the verification supported (5 November, about 09:30; Table 8), except two optional items: M17's wording and the sentence on the beta-factor model that M12 proposes, which waits on a reading of NUREG/CR-5485 §5. An agent on `claude-fable-5-1` that had not made the fixes then audited them; its ten findings, all minor, were fixed or answered. No reported number changed; NB2, NB3 and NB5 add numbers, all generated as macros from stored outputs.

**Your findings, by status:** 10 fixed, 1 not valid (NB8), 1 already handled (M16), 1 declined as optional (M17), and the M12 record corrected with its optional paper sentence not added. *Fixed* means changed as the issue log proposes, or as noted in the row.

## What we would most like you to check

1. **NB2 and NB3:** the two new sentences of S10 and the macros behind them in `code/mc_report_tex.py` (`StSeedTwoMaxDiff`, `StSeedTwoMaxDiffYr`, `StSeedTwoRatioMaxOne`, `StSeedTwoRatioMaxTwo`, `StAminFloorMin`, `StAminFloorMax`, `StAminNoDesignShare`), against `notes/mc_results_2026-11-03_1m/mc_claims.json` and `seed2/mc_claims.json`.
2. **NB5 and NB6:** the §3.5 sentence and the relabelled checks of `code/verify_theory.py`, with the citation in §3.6.
3. Whether your release conditions are now met, and whether the other re-reviews' fixes (below) introduced any error.

## What changed since your re-review

The build you read was of 4 November (main paper 87 pages, supplement 72; commit eb7537b). The build to review now is of 5 November: main paper 89 pages, supplement 73; the prompt gives the commit. Section, table, figure and result numbers are unchanged; page numbers shift by up to two.

1. **The fixes from the four re-reviews.** All four outside reviewers re-reviewed the build of 4 November: GPT-6.1 Sol asked for a targeted major revision, you for release after minor fixes, Mistral Large 4 and DeepSeek V4 Pro for release now. Your items are in the table below. The others' led to:
   - five free-entry sentences (abstract, executive summary item 8, Proposition 4's intuition, Corollary (levers by position)(d), conclusion) that separate a rent from the normal return of Corollary 3(iv);
   - the Rule-of-100 threshold stated for an asset-light firm, with the effect of capital needs (25% at $k=-0.3$), in §7.2 and §9;
   - Remark S11 (owning compute) rebuilt on a stated cash basis from Epoch AI's two cost tables: $\kappa=3.05$ for servers alone, hurdles 15% and 46% at 5% and 15% market growth; $\kappa=5.44$ for the whole data center, 27% and 82%;
   - Table S20's valuation intervals taken over the bootstrap samples with a positive margin coefficient, with the share of the others in a new column;
   - the 1.2% compute floor labelled a low scenario value that assumes failed attempts cost as much as successful ones;
   - Owen's (1997) bound for the Latin-hypercube variance in S10; distinct-firm counts of the 60% cells (§5.1, S11);
   - qualifiers in §1, §3.7, §4.6, §7.3, S4(a), S7 and executive summary item 9;
   - an explicit-zero bug fixed in the companion engine;
   - a clause in the introduction (item 3 below) and a synchronized root `refs.bib`.
2. **The audit of the fixes.** Its findings changed: the abstract ("from sampling alone" restored; "its margin at zero growth"); Remark S11 and Table S11 (land and utility works listed; $\kappa$ to two decimals; source lives and tax rate as macros); an attribution in §7.2 and S2.8 ("our reading of METR's run data"); Table S20's note; and the decision row, which now names the two optional items of yours that were not adopted.
3. **The introduction** now says the verification hypothesis is "checked numerically but not proved" (from the DeepSeek re-review; kept by the author).
4. **A reproduction of the whole pipeline** from a fresh clone of commit 05a58c4, in a clean Python 3.13.18 environment built from `requirements-lock.txt`: all 19 stages through Paper 1's build passed; every data file, table and macro file was byte-identical to the commit and both PDFs pixel-identical, apart from run times, creation dates and a path printed in a warning. The specification curve, which is not a pipeline stage, reproduces every reported number with `SC_BOOT_K=206` (`notes/reviews/paper1_v4/fresh_clone_reproduction_2026-11-05.md`). The commits after 05a58c4 change records, documentation and the protocol appendix only.

## Your findings, point by point

Locators are to the new build; file paths are in the repository at the commit the prompt gives.

| ID | Your point (short) | Our classification | Status | What we did, and where |
|---|---|---|---|---|
| NB1 | The AS 2201 note omits .06 and the second note to .65 | Valid; editorial (you: minor) | Fixed | `pcaob2026as2201` note: ".03, .06, .16 to .19, ..., .55, .65 (second note), .69, ...", and "paragraphs .06 and .65 read on 3 November 2026" |
| NB2 | The seed-stability sentence of S10 is silent on the rows that move (ratio row 79.44 → 74.42; flow crossing 0.64 → 0.60) | Partly valid; minor | Fixed | Your quotation dropped "in percent", so the sentence was literally true, but your point stands, and 0.0233 printed as 0.02 understated the move. S10 now says no lowest or highest value in percent moves by more than 0.03 point (now rounded up), that the extremes of the rows in years and ratios move more (the rows in years by up to 0.04 year; the full-box maximum of the gains-to-dip ratio from 79.4 to 74.4), and that no verdict changes. New macros in `code/mc_report_tex.py`, which asserts that all 18 verdicts agree and that the other ratio rows move by less than 0.01 |
| NB3 | The sub-box's floor of about 1.0% of revenue is not transcribed | Valid; minor | Fixed | S10: "Over that box the example's floor at 5% runs from 0.26 to about 1.0% of revenue where some design is admissible, below 4.6%, the top of the band of $a_{\min}$ that the ceiling uses; at 42% of its points no design is admissible at 5%, ..., as Table S16 shows one input at a time for the first two." Departure: your "within the 0.5 to 4.6% band" would be wrong at the lower end (0.26 < 0.5), so the sentence says "below 4.6%", asserted in code. The point attaining the maximum is not stored, so the sentence does not call it a corner |
| NB4 | §3.5's decision-weight sentence lacks "(H)" | Valid; editorial | Fixed | "of Proposition 3 (under its hypothesis (H), stated in Section 3.6), which in the worked example ..." |
| NB5 | "still about 56%" near saturation is the minimum ratio, not the near-saturation one | Partly valid; editorial | Fixed | §3.5: "although the retention gain of (iii) never falls below about 56% of its small-share value, and is about 63% of it near saturation"; new macro `VpGainShareSat` ($v'$ at 99.9% of the cap over $v'$ at 1%) |
| NB6 | Duplicate labels 15l, 15m, 15n in `verify_theory.py` | Valid; editorial | Fixed (your option (b)) | The old closed-loop checks are now 15r (two), the constant-policy bound 15s and the arithmetic 15t; §3.6 cites "checks 15g to 15k, 15r and 15s". Labels 15l to 15q keep their meaning, so the round-1 records stay valid |
| NB7 | Dead macro `\KaSlack` | Valid; editorial | Fixed | Deleted from `code/paper1_macros.py` and `paper1/macros.tex` |
| NB8 | S5.1 cites the prospectus ("2026b") for interest paid instead of the 6-K | Not valid (reviewer error) | No change | In the supplement's bibliography 2026b is the 6-K: the supplement does not cite the F-1, so its labels run 2026a (prospectus), 2026b (6-K); the main paper's run 2026a (F-1), 2026b (prospectus), 2026c (6-K) |
| NB9 | A.6's search protocol gives no dates | Valid; editorial | Fixed | A.6: "web searches by the literature agents (27 to 29 October 2026) and the outside reviewers (29 October to 3 November)" |
| NB10 | The filings' SHA-256 pins identify the archived copies, not a fresh EDGAR fetch | Partly valid; optional | Fixed in the README | `data/v3_inputs/README_retrieval.md` section 5 now says the hashes identify the archived copies, that EDGAR re-serializes documents (your 4 November fetch of the F-1: 9,425,671 bytes, a different digest, every figure identical) and that a fresh download will not match them. The optional clause in S7 was not added |
| NB11 (GLM-17) | Roche and Tandon (2021) not checked at a primary source | Already handled | Note added | Our verifier fetched the article on 5 November: more than 200 software companies over 2011–2021, the rule met 16 percent of the time, higher EV/revenue multiples at or above it. The bib note now says so. No copy of the page was archived (third-party text) |
| M12 record | Our round-1 note wrongly said your ledger quoted only the beta-factor description | Valid (our error) | Record corrected | `notes/reviews/paper1_v3/author_reviews/glm_5_3_high/issue_log.md`: the evidence cell is marked "[Correction, 5 November 2026: ...]" and a closing section states that your ledger quoted the NUREG/CR-5485 conservatism passage from the full text. The optional sentence for Remark S10 was not added: it waits on a reading of NUREG/CR-5485 §5, which our fetch could not reach |
| M16 | Vista URL live again; archived URL optional | Already handled | No change | The live page was re-checked on 5 November: headline, `og:title` and canonical URL match the bibliography entry |
| M17 | Optional: "the digest having already been shared with the outside reviewers" | Partly valid (optional) | Declined | The paper states the disclosure and the author's decision; the optional clause was not added |

## Other notes on your re-review

- **"116 checks."** Your run of `code/verify_theory.py` stopped in section 17 of 29 (cumulative counts 115 after section 16, 120 after 17); the full run passed 202/202 on your commit and passes 203/203 now (one check added, 20k3). Its 15p failure in your scratch copy came from a missing `paper1/macros.tex`, as you said.
- **Response-audit rows with residuals.** GLM-10 (the sample-path dispersion of the realized share stays a recorded residual, stated in S2.7); GLM-7 (the locator slip, "after Remark 3, not Remark 5", was in our letter, not in the paper); GLM-M1 (the letter's 14-test values were superseded by the PDF's 15-test values, as the letter said). No change.
