# Response to your review of *The Rule of 40 as a Price Line* (third version)

**To:** Mistral Large 4 (high effort)
**From:** Akshaya Bangalore Sreenivasa Murthy (author), with the lead agent of the research session
**Date:** 4 November 2026
**Your review:** of the build of 2 November 2026 (main paper 82 pages, SHA-256 bd87f45f…; supplement 57 pages, acf9d62b…) and the repository at commit 62e574b
**Your verdict:** Accept with minor revisions for the working-paper track: "technically sound in everything I could check"; eight findings (none an error in the paper), minor items, five editorial repairs and an eight-step revision sequence.

Thank you for the review. Your review arrived a day after the other three and set the acceptance tests that drove several of the changes:

- **Classify every registrant by its business description:** done (F-2).
- **Run a solver-independent check of the HJB profile:** done, as a lower bound (F-6, Ed-4).
- **Reproduce the whole pipeline independently:** done from a fresh clone in a fresh environment (RS-7).
- **Check the legal and tax citations at their primary sources:** done (M-8, Ed-5, RS-6).

We verified each of your findings. Two we classify as not valid, though each still led to a change:

- **F-6:** The solvers that returned the no-spend solution discount at r rather than r − G and stop after about six years of horizon. A simple admissible spend policy beats no-spend (v/s 9.02 against 5.83), and that bound is now a check in `code/verify_theory.py` (check 15q).
- **Empirical 7:** The paper's own specification reproduces the printed within-firm slopes from the shipped panel. The trim of growth at 150% that the code applies is now stated in Section 5.

**How we handled it.** Each finding was verified in the research session against the paper's sources, the code (re-run on clean exports of the commit you read), the stored outputs and primary sources. We classified each as valid, partly valid, not valid (a reviewer error) or already handled. The author then adopted every fix the verification supported (2 November, 23:23, and 3 November; Table 8). Our evidence for each finding, including the scripts we ran, is in `notes/reviews/paper1_v3/author_reviews/mistral_large_4_high/` (`issue_log.md` and `verification_claude/`). The joint response to all four outside reviews is `notes/reviews/paper1_v3/response_to_outside_reviews.md`. This letter is self-contained, but it uses that file's dispositions.

**Your findings, by status:** 6 fixed, 2 not valid, 9 already handled (17 rows). *Fixed* means changed as the issue log proposes, in the paper, the code, the data or the repository; *Partly* means part of the proposal was applied, and the row says what was not and why; *Declined* means deliberately not applied, with the reason; *Not valid* means we think the finding is mistaken, so nothing changed; *Already handled* means the paper already did what was asked, or the item was a confirmation.

## What we would most like you to check

1. F-2: R2 on the whole main sample, its two blind readings, and the re-estimated headline values (A.4 item 7)
2. F-6 and Ed-4: check 15q of `code/verify_theory.py` and whether it settles your concern
3. RS-7: a reproduction of your own on the current commit, if you can run it
4. RS-2: the caption of Table 4 and the 28 to 78% range
5. S4, S10, S11 and S12, all new since your review

## What changed in the paper since your review

These are the changes to the paper since the build you read (2 November: main paper 82 pages, supplement 57 pages, repository commit 62e574b). The paper you are asked to look at again is the build of 4 November: main paper 87 pages, supplement 72 pages; the prompt gives the commit.

1. **Hypothesis (H).** Every statement that a value-maximizing firm acts on the marginal value of revenue now says "under (H)" (16 places, including the title of Proposition 2). (H) itself is still not proved; the global qualifier of M 3.6 stays.
2. **Compute share.** The floor of the compute-share range had been set in the wrong units (a cost per dollar of labor used as a share of revenue). It is now stated in revenue units: the cost per completed task times the labor share, 1.2% of revenue. One range, 1.2% to 60% at 2025 prices, is used in the text, the calibration and the stress test. The resulting range of the Rule-of-100 growth threshold is 28% to 78% (M 7.2, Table 4).
3. **Joint-parameter stress test (new S10).** 1,000,000 Latin-hypercube draws per seed over a box of 51 dimensions, 100,002 corners, a vertex search, Sobol indices on 65,536 base samples and a second seed. It was run on the author's computer. Of its 18 tests of headline statements (Table S18), 6 hold at every evaluated point. Six headline claims hold only under conditions, which the text now states wherever each claim appears (rows ST-1 to ST-6 below). Figure S1 shows the distributions.
4. **Specification curve (new S11).** Each headline empirical claim is tested over all combinations of the paper's analysis choices, written down before any estimate. Also: forward pairing of growth and margin, and leave-one-firm-out.
5. **Sample rule R2 on the whole main sample.** Business descriptions of all 293 core registrants were retrieved, and R2 was applied by the keyword rule fixed in advance: 8 firms and 56 firm-years leave the main sample. Two blind readings on other models serve as a sensitivity (Cohen's kappa 0.95). Every headline statistic was re-estimated with this sample and the corrected capitalized software (item 6); A.4 item 7 lists the values before and after. Among them: 284 firms (was 292); the slope Ψ0.90 −0.20 on GAAP and −0.17 on cash (was −0.22 and −0.16); the fall of the 95th percentile 11.9 points on GAAP (unchanged) and 12.6 on cash (was 12.7); the anchor 14 firm-years (was 13); the central 2036 score 58 (was 59), 53 after the cost of changes in flight; and the Romano-Wolf p-value of the GAAP decline 0.075 (was 0.097). Numbers quoted in the point-by-point rows below that predate this re-estimation can therefore differ from the paper by these amounts.
6. **Data audit.** 40 seeded firm-years were checked against the face statements of the filings the panel used. Capitalized software was read from the filings where company-specific XBRL elements hid it, after a scan of 1,213 firm-years (S7).
7. **Machine-checked proofs (new S4).** The static model is formalized in Lean 4 with Mathlib: 35 theorems, standard axioms only. The formalization found two statements to tighten, both now in the text: σ* = 0 for X ≤ k inside the cap condition of Lemma prop:score, and a measurable moving intercept in Proposition prop:budget (c).
8. **Reproduction from a fresh clone.** The whole pipeline was rerun from a fresh clone (commit 3998b33) in a fresh environment, with the new `code/fetch_raw_data.py` placing the third-party raw data. Data, tables, macros and the main paper matched. Two stale records and four figures whose layout depended on the Python environment were regenerated; the versions are in `requirements-lock.txt`.
9. **Legal and tax citations.** Every legal and tax citation was checked at its primary source: none was incorrect, eight were imprecise, and all eight were fixed.
10. **New S12: three further analyses added after this review round.** These were added at the author's decision on 4 November and answer questions readers asked. (a) How valuations weight growth and margin: public float over revenue on growth and margin, with year effects, firm clusters and a bootstrap of the implied weight. One point of growth is worth about 4.8 points of margin on the cash basis (90% interval 3.1 to 15.8), and equal weights are rejected. (b) The cost of not automating, in the paper's pass-through scenario. (c) What sets the payback: change capacity drops out while the program runs, and the share of changes that create value sets it. The one main-text change is the limitations sentence of M 8.6, which now points to S12.1. The public float was retrieved on 3 November with the author's approval (S7).
11. **Abstract.** Rewritten on 4 November in plain language for business readers, at the author's request. The numbers and conditions are the same: the verification hypothesis, the central costs and fixed prices, the compute share and its range, pass-through, a central scenario and not a forecast, the score after the cost of changes in flight, and the anchor-only interval. The selling-spend range of the 2036 score moved out of the abstract and stays in M 1 and M 7.3.
12. **Records.** The four outside reviews and their verification are recorded in A.2 and S8.4 (Table S14). The author's decisions are in Table 8.

## Point by point

Mistral's findings are numbered as in your report (F, M, Ed, RS); items that repeat one another are grouped in one row. Locations: M = main paper, S = Supplementary Appendix, A = the main paper's Appendix A, all in the current numbering (key at the end). Numbers quoted in a row are those of the revision at the time; where a later rerun moved one, the paper is authoritative.

| ID | Your finding (short) | Our assessment | Status | What changed, and where (current numbering) |
|---|---|---|---|---|
| F-1 | (H) is unproved and carries the "firm's own weight" claim; correctly disclosed | Valid; already handled | Already handled | "Under (H)" at the 16 decision-weight statements (round 3, DS-17); the abstract says "under a verification hypothesis". |
| F-2, Ed-3, RS-4 | R2 applied only to the 16 named firms; acceptance test: classify all registrants by business description and rerun the headline statistics | Partly valid | Fixed | Descriptions of all 293 core registrants retrieved (3 Nov; `data/v3_inputs/README_retrieval.md`, section 6); R2 applied to the main sample by the keyword rule fixed in advance (8 firms, 56 firm-years out); two blind readings on other models as a sensitivity (Cohen's kappa 0.95), rows of Table S4; every headline value re-estimated, before and after in A.4 item 7; M 4.2, S8. |
| F-3, M-1, Ed-1, RS-5 | The abstract's 2036 sentence lacks the scenario caveat | Already handled | Already handled | The abstract says "On a central scenario, not a forecast". |
| F-4, M-2, Ed-2, RS-3 | `data/panel_v3.csv` carries the v2 flag `acq_flag` and the v3 flag `acq_flag_v3`; reusing `acq_flag` gives a different anchor | Valid | Fixed | The column to use is named in S8 (Reproducibility) and `code/REPLICATION_README.md`. After the re-estimation the anchor has 15 firm-years (8 firms) with `acq_flag` and 14 (7) with `acq_flag_v3`. |
| F-5 | The accountability floor operationalizes a legal standard with a scenario probability; arithmetic exact | Valid; no change | Already handled | The paper calls the threshold a judgment and a scenario value and reports both 5% and 1%. |
| F-6 | The reviewer's solvers could not reproduce the HJB profile (v' 9.1, 7.2, 5.4) and returned the no-spend solution | Not valid (reviewer's solvers); the request for a solver-independent check is reasonable | Not valid | One solver discounts at r instead of r − G and stops after about six years; the other returns the no-spend value everywhere. A policy spending 5% of revenue until the share reaches 0.4 is worth v/s 9.02 at s0 = 0.01 and 7.33 at s0 = 0.1, against 5.83 for no spend, so no-spend is not optimal. Added: check 15q of `code/verify_theory.py` (202/202 pass) and a note in `code/REPLICATION_README.md`. |
| F-7 | Growth-rate conventions in the extreme-score passages | Valid; no change | Already handled | The conventions are labelled where it matters (S2.1). |
| F-8 | The four estimands share most firm-years; keep the "292 software firms" phrasing | Valid; already handled | Already handled | The paper calls them a sensitivity set, not four independent replications. |
| M-3 | The familywise families contain uninformative members | Already handled | Already handled | M 5.1 adds the 18-test family (GLM-F5) and says such survivals say little. |
| M-4 | Interest and taxes paid come from SEC frames (latest filed) | Already handled | Already handled | Disclosed in S8. |
| M-5, M-6, M-7 | Process candour; macros idempotent; exclusion irreversible and disclosed | Valid; no change | Already handled | None needed. |
| M-8, Ed-5, RS-6 | Citations not re-verifiable from the reviewer's environment; primary-source pass of the 2025-26 legal and tax items | Partly valid | Fixed | Primary-source pass of every legal and tax citation (`notes/legal_primary_source_pass_2026-11-03.md`): none incorrect, eight imprecise, all fixed; the IRS release number and date confirmed. A specialist's reading before journal submission is still advisable. |
| Empirical 7 | Within-firm slopes: reviewer +0.083 / lead −0.112 / cash −0.009 against printed +0.06 / −0.03 / −0.03 | Not valid (reviewer's specification) | Not valid | The paper's specification reproduces the printed values from the shipped panel (+0.059, −0.034, −0.032). The trim of growth at 150% that the code applies was not stated; it now is (Section 5). Dropping it changes little (+0.068, −0.038, −0.019). |
| Ed-4, RS-1 | The grid solution may be one of several solutions of the singular ODE; add a solver-independent check | Partly valid | Fixed | The singular point and the free constant are stated (S3, proof of Proposition 2); the policy bound of F-6 is the solver-independent check. |
| RS-2 | Compute-share caveat in the abstract and on the ceiling table; "28 to 78" | Partly valid | Fixed | The caption of Table 4 says the compute share is a scenario value that no source measures; the floor's units are corrected (1.2% of revenue, not 2%), so the threshold range is 28 to 78%. The abstract already states the condition on the compute share. |
| RS-7 | Independent full-pipeline reproduction | Valid | Fixed | Done (3 Nov) from a fresh clone of commit 3998b33 in a fresh environment, with the third-party raw data placed by the new `code/fetch_raw_data.py`; data, tables, macros and the main paper matched; two stale records and four environment-dependent figures were regenerated; `requirements-lock.txt` (`notes/reviews/paper1_v3/audit_2026-11-03_revision.md`, F1). |
| RS-8 | Keep the post hoc choices in Appendix A | Valid; no change | Already handled | A.4 lists them. |

## The joint-parameter stress test (ST-1 to ST-6)

The stress test was added in this round, partly in answer to the reviews' requests for a joint envelope of the scenario inputs. Six headline claims hold only under conditions; the text now states each condition where the claim appears. The values below are those of the million-draw run now in the paper.

| ID | Claim as the third version stated it | What the stress test found, and what the text now says |
|---|---|---|
| ST-1 | A cash score of 100 needs market growth above 32.5% a year | Holds at the central cost inputs only. With compute at 6% of revenue and the other costs moved jointly the threshold runs 24.0 to 45.1%; over the whole box, 19.6 to 94.5%. The condition is stated wherever the 32.5% appears: "at central costs" in the abstract, "at the central cost inputs" in M 1 and the summary box, "the central cost structure" in M 7.2. S10, Table S18, Figure S1. |
| ST-2 | The 2036 score: 59, interval [54, 62] | [54, 62] is the anchor-sampling interval alone. With every scenario input moved jointly, nine in ten draws lie between 40.7 and 66.7, and 29% fall inside [54, 62]. M 1, the summary box and M 9 say the interval comes "from anchor sampling alone"; the abstract, "from sampling alone". S10, Figure S1. |
| ST-3 | No payback within five years (7.5 years) | Under central execution the payback runs 4.99 to 9.29 years as the other inputs move; it is below five years only on compute paths that start high and fall steeply. Over the whole box, 3.51 to 29.07 years. The text says "under central execution", with the range (M 1, M 7.3, M 9). New in S12.3: what sets the payback. |
| ST-4 | Cumulative effect negative at three and five years | Under central execution the largest of the four effects is positive only at a few points, by at most +0.004 point-years; over the whole box by up to +11.7. M 1 and M 7.3 say "at all but a few points" and that the statement is for central execution. S10. |
| ST-5 | Less than half of the program realized by 2036 (41%) | 41% under central execution; over the stated execution ranges 4.9 to 85.0%, above half once change capacity exceeds about 13% of the program a year. M 1 and M 7.3 say "under central execution", with the range. S10. |
| ST-6 | The growth engine leads the G&A cut at 1 of 6 positions | Holds at the central maintenance base only: over its 90% bootstrap interval the growth engine leads at 0 to 1 positions, and the stated count holds in 57.6% of the draws. M 7.5 says "at the central maintenance level", with the range. S10. |

## Numbering key

| Section | In the build you read | Now |
|---|---|---|
| Further theoretical results; the model; proofs | S1, S2, S3 | S1, S2, S3 (unchanged) |
| Machine-checked proofs of the static model | (none) | S4 (new) |
| Proofs and details for Section 6 (acquired growth) | S4 | S5 |
| The Rule of 1000 | S5 | S6 |
| Data construction and inference | S6 | S7 |
| Protocol records (outside reviews: S8.4, new) | S7 | S8 |
| Full-cost floors and the accountability floor | S8 | S9 |
| Joint-parameter stress test | (none) | S10 (new) |
| Specification curve | (none) | S11 (new) |
| Further analyses added after the third review round | (none) | S12 (new) |
| Glossary | S9 | S13 |
| Supplement tables | S1 to S13 unchanged; errors S14, full-cost floors S16 | errors S15, full-cost floors S17; new S14 (outside-review counts), S18 (stress test), S19 (specification curve), S20 to S22 (S12) |
| Main paper | Sections 1 to 9, Appendix A (A.1 to A.6), Tables 1 to 8 | Same numbers; Table 8 has new rows for the decisions taken since |

Main-paper section, table, theorem, remark and equation numbers are unchanged, and so are the supplement's theorem, remark and equation numbers.
