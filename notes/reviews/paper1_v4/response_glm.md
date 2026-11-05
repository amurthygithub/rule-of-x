# Response to your review of *The Rule of 40 as a Price Line* (third version)

**To:** GLM 5.3 (high effort)
**From:** Akshaya Bangalore Sreenivasa Murthy (author), with the lead agent of the research session
**Date:** 4 November 2026
**Your review:** of the build of 2 November 2026 (main paper 82 pages, SHA-256 bd87f45f…; supplement 57 pages, acf9d62b…) and the repository at commit 62e574b
**Your verdict:** Major revision, "with acceptance expected once the four must-fix items and the Phase-2 one-liners are executed": five majors (F1 to F4 must-fix, F5 should-fix) and eighteen minors; "No theorem is false; no number in any table is wrong".

Thank you for the review. Your review was the one that re-ran the full pipeline, including the 999-replication bootstrap, and its confirmations of the static theory, the Proposition 2 numerics and all 164 cells of Table 2 stand. We verified each of your 46 findings.

All four must-fix items and the should-fix item are fixed:

- **F1:** Six sentences now describe the worked decision weight as U-shaped.
- **F2:** The availability sentences of Section 6 are corrected to what the acquirer's filings disclose, and Table 3's annual organic rows are filled.
- **F3:** Nei, Ruus and Indov (2026) is cited, and "only" is dropped.
- **F4:** The leftover marker in A.6 is gone.
- **F5:** M 5.1 now states the consequence of the post hoc family, with 18-test Holm values.

Three items were declined:

- **GLM-M17:** The author decided to keep the unsalted digest, and the paper states that the excluded registrant can be identified from it.
- **GLM-11:** The stock-constrained fast case was not computed. The stress test varies change capacity over its range, and the new S12.3 adds a related result: change capacity drops out of the payback while the program runs.
- **GLM-16:** No AI-auditing citation was added, because no specific antecedent was proposed.

Three items were only partly met (GLM-M16, GLM-10, GLM-18), and two we classify as not valid (GLM-M14, GLM-22). Each is explained in the table.

**How we handled it.** Each finding was verified in the research session against the paper's sources, the code (re-run on clean exports of the commit you read), the stored outputs and primary sources. We classified each as valid, partly valid, not valid (a reviewer error) or already handled. The author then adopted every fix the verification supported (2 November, 23:23, and 3 November; Table 8). Our evidence for each finding, including the scripts we ran, is in `notes/reviews/paper1_v3/author_reviews/glm_5_3_high/` (`issue_log.md` and `verification_claude/`). The joint response to all four outside reviews is `notes/reviews/paper1_v3/response_to_outside_reviews.md`. This letter is self-contained, but it uses that file's dispositions.

**Your findings, by status:** 30 fixed, 3 partly, 3 declined, 2 not valid, 8 already handled (46 rows). *Fixed* means changed as the issue log proposes, in the paper, the code, the data or the repository; *Partly* means part of the proposal was applied, and the row says what was not and why; *Declined* means deliberately not applied, with the reason; *Not valid* means we think the finding is mistaken, so nothing changed; *Already handled* means the paper already did what was asked, or the item was a confirmation.

## What we would most like you to check

1. F1 to F5 against the rows below
2. GLM-M9: the forward-pairing variant now computed in S11
3. GLM-M11: the compute-share floor, now in revenue units (item 2 below), which you flagged
4. The declined and partly met items: whether our reasons hold
5. A rerun of your full bootstrap replication on the current commit: R2 now applies to the main sample, and capitalized software was corrected, so several values moved (A.4 item 7 lists them)
6. S12, new

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

The finding column is the short form of your finding from the issue log; the full text, our evidence and the proposed fix are in the issue log. Locations: M = main paper, S = Supplementary Appendix, A = the main paper's Appendix A, all in the current numbering (key at the end). Numbers quoted in a row are those of the revision at the time; where a later rerun moved one, the paper is authoritative.

| ID | Your finding (short) | Our assessment | Status | What changed, and where (current numbering) |
|---|---|---|---|---|
| GLM-F1 | The worked decision weight v'(s) is U-shaped, not "falling with share", so four prose sentences overgeneralize.… | Valid (the reviewer's acceptance tests… | Fixed | Six sentences corrected: S2.2; M 3.5 (intuition after Cor. 3); M 3.6 (worked example); M 7.4 ("highest at small share", and retention still raises the durable score by X - k a point near saturation, Prop. 9(a)); M 1; M 9 ("gains ... from retention are transient" -> durable). New macros \Vp* (coding agent; verify_theory checks 15l-15p). The reviewer's acceptance tests were not used, because they fail on the correct solution. |
| GLM-F2 | The filings the paper cites disclose the following, which the paper says are unavailable: annual organic growth… | Valid | Fixed | M 6: the five availability sentences are corrected (organic growth for 2024, 2025 and Q2 2026; the subscription share; equity compensation; the annual investing split; capital expenditure by year), as is the Table 3 note. Table 3's annual organic rows are filled from the coding agent's macros, with a new panel-basis cash row. The figures are read from the sec.gov filings (decision 2). |
| GLM-F3 | Lee (2024) is not the only peer-reviewed academic study of the rule: Nei, Ruus and Indov (2026) is a second | Valid | Fixed | Author decision 4: M 1 and M 2.2 cite Nei, Ruus and Indov (2026) and drop "only"; neither study estimates the frontier. The bibliography entry is taken from the Crossref record. Only the record and abstract were read, not the article, and both the text and the bibliography note say so. |
| GLM-F4 | Unresolved marker "[R2: finalize once the author's review is complete]" prints in A.6 (p. 82) | Valid | Fixed | = X-2. |
| GLM-F5 | The post hoc family is disclosed but its consequence is not. Adding headline statistics the family omits raises… | Partly valid | Fixed | Author decision 5: M 5.1 adds the family sentence, with the 18-test Holm values of the steepening, the GAAP decline and the anchor (\HolmEighteen*); M 5.8 adds that the anchor fails at 10% under the percentile type in that family. |
| GLM-M1 | §5.8 prints the anchor's Holm p as 0.084 (percentile) and 0.028 (basic); the stored p-values give 0.096 and 0.030 | Partly valid (no arithmetic error; the… | Fixed | M 5.8 states the count: "over 14 tests (the family's estimable members and the anchor)", i.e. 13 estimable tests plus the anchor. The 15-test values (0.006, 0.096, 0.030) are in this response; the conclusion is the same. |
| GLM-M2 | Two committed notes files are stale v2 artifacts that contradict printed v3 numbers. "Relatedly", the committed… | Partly valid (the stale files are… | Fixed | Coding agent: code/paper_stats.py now reads data/panel_v3.csv. No printed number depended on the stale files. |
| GLM-M3 | The after-tax Prop. 4(d) bound charges customer capital k_a at psi, but Assumption ass:entry expenses customer… | Valid (minor) | Fixed | M 7.2 parenthetical: customer acquisition is expensed and deducted in full, so the bound is R_max with capital k, less (1 - tau) k_a G; here k_a = 0. |
| GLM-M4 | "Counting the costs of accountability alone and none of the costs of running AI" still charges compute and fees… | Partly valid (wording) | Fixed | M 7.2 (four places): "with accountability costs alone" -> "without the full-cost floors"; "Counting compute, fees and the accountability floor but none of the full-cost floors". |
| GLM-M5 | (i) Payback is an expectation construction with two near-cancelling biases. (ii) "Over the life of the program ...… | Partly valid | Fixed | (ii) M 7.3: "(2.1 counting only gains until then)" (\PayRatioDoneCen). (i) The capped bound is handled under GPT-4. |
| GLM-M6 | (a) The coupon variant 86.0-112.8 is on the interest-paid basis while 87-114 is on interest expense. (b) The Q2… | Valid | Fixed | (a) M 6: the coupon variant is given on both bases (86.0 to 112.8 with interest paid; 86.7 to 113.7 with interest expense). (b) The Q2 interest share is cited to the 6-K. |
| GLM-M7 | "22% to 28% of the time-weighted capital deployed": the denominator is the time-weighted capital written down at… | Valid (wording) | Fixed | M 6 and the Table 3 note: "written down at the decay rate d". |
| GLM-M8 | "Scores with acquisitions charged in full are lower bounds" is unconditional; Remark rem:acquired-bounds is… | Valid (minor) | Fixed | M 1, misreading 8: the lower bound is stated with its condition (Remark 4). |
| GLM-M9 | The panel pairs past-year growth with the same year's margin; no forward-pairing variant exists for the Ψ/P95… | Partly valid | Fixed (3 Nov) | M 4.3 states the pairing convention. S11 (forward pairing) computes this year's margin with next year's growth (the model's timing; also indexed by the growth year) and this year's growth with next year's margin, under the four views and over the whole specification grid. Under E1 the P95 falls are 11.1 (GAAP) and 11.1 (cash) points against 11.9 and 12.6 with the reported pairing, and the Psi_0.90 slopes -0.29 and -0.24 against -0.20 and -0.17; no pairing changes the sign of the decline, the slope or the GAAP steepening under E1; the 0-60% slope is not defined under E2 and the imputation bounds (60% cell of 15 and 26 pairs). Earlier status: partly (convention stated, variant not computed). |
| GLM-M10 | The S7 element list omits OperatingIncomeLoss, the tag behind the GAAP headline margin, and the PP&E instant | Valid | Fixed | S7, Elements: OperatingIncomeLoss is added, and the six retrieved but unused elements are named. |
| GLM-M11 | The 1% credible lower bound of the compute share is a cost per successful run; per completed process it is about… | Partly valid (same as GPT-22) | Fixed | As GPT-22. The coding agent adopted the per-completed-process cost: 2% low end, 29% threshold low end. **Units corrected (3 Nov 2026):** the 2% is compute per dollar of labor (kappa); times the 60% labor share it is 1.2% of revenue, threshold low end 28% (23% accountability-only). The per-completed-process floor stands. See GPT-22 and `notes/r3_compute_fix.md`. |
| GLM-M12 | "However many layers": correct within the beta-factor form, which the CCF literature calls conservative when not… | Already handled | Already handled | Already scoped ("an assumption of the example"). No change. |
| GLM-M13 | AS 2201 ".03" states the auditor's objective; the obligation flows from Item 308(b) | Partly valid (= DS-50) | Fixed | = DS-50. |
| GLM-M14 | Lee (2024) "1,756 SaaS firms" should be 1,771 | Not valid (reviewer error; = DS-34) | Not valid | = DS-34. |
| GLM-M15 | Non-identification of firm frontiers from chosen points is listed as believed new, while §2.1 calls it an instance… | Partly valid | Fixed | M 1 (novelty list) and M 3 (opening): "a worked instance ... of the classical non-identification". |
| GLM-M16 | The Vista URL dead-ends (cite an archived snapshot); the Svanberg full text is unverifiable, so add an a_{min}… | Partly valid | Partly | Vista: the bibliography URL loads the cited article, so no change. The optional a_min sensitivity over delta_M is covered by the stress test, which varies delta_M over 0.10 to 0.40 jointly with the other inputs (S10); no separate row was added. |
| GLM-M17 | The exclusion identifies the registrant by an unsalted SHA-256 of its CIK. CIKs are short integers, so enumerating… | Valid (process) | Declined | Author decision (22:44): the digest is kept. Table 8 and S7 state that it can be inverted and that the registrant can be identified from the code. |
| GLM-M18 | SFA maximum-likelihood outputs are not bit-reproducible across environments | Valid (minor) | Fixed | S7, Reproducibility: the stochastic-frontier ML estimates may differ slightly across environments. |
| GLM-1 | "Below the revenue multiple at every share" is verified numerically, not proved | Already handled | Already handled | Already "in the example". No change. |
| GLM-2 | Definition 2 is per firm; Ψχ pools firm-years | Partly valid (optional) | Fixed | M 5.1: "(computed over firm-years, so each firm contributes one chosen point a year)". |
| GLM-3 | The lagged S&M share uses the prior year as restated in the current filing, not as first reported (124 firm-years… | Partly valid (documentation) | Fixed | M 5.4: "taken like growth from the same filing". |
| GLM-4 | The panel can be rebuilt from raw filings only after the purge | Already handled | Already handled | S7 already says so. No change. |
| GLM-5 | Restate the Q2 organic range (22 to 44) on annual data too (2025: 23.4 to 40.3)? | Partly valid (optional; follows F2) | Fixed | M 1: "(on its annual figures for 2025, about 23 to 40)". |
| GLM-6 | Is the 2024 purchase of intangible assets (162.5M) acquisition capital? | Partly valid (unresolved) | Fixed | M 6: the 2024 intangible-asset purchase ($162.5 million, an asset deal among them) is counted as acquisition capital, and the text says so. |
| GLM-7 | Remark 3's identities are pre-tax while §7.2 is after tax; no reconciliation sentence | Partly valid (optional) | Fixed | M 3.11, after Remark 5: the identities hold for the after-tax margin with k read as (1 - psi tau)k, the basis of Section 7. |
| GLM-8 | Does the 60%-of-revenue labor share replaced by compute include SBC? | Partly valid (state the basis) | Fixed | M 7.2: "labor costs of 60% of revenue, including stock-based compensation". That is the basis of s_L in the assumptions register (GAAP operating costs); the central compute share is unchanged. |
| GLM-9 | The deferred-revenue median 0.27 comes from SEC frames (latest filed), but that is not said there | Valid (minor) | Fixed | M 7.2: "(from SEC frames, which keep the latest filed value)". |
| GLM-10 | Only the mean bar b is specified, so the dispersion of the 2036 41% is unidentified; asks for a two-point or Beta… | Partly valid (optional) | Partly | The stress test varies the realized share bbar over 0.37 to 0.85 jointly with the execution inputs; the realized share by 2036 then runs from about 5 to 85% (S10, ST-5). No two-point or Beta dispersion of bbar was computed. |
| GLM-11 | Stock versus flow reading of change capacity: the fast case sits at the capacity line | Partly valid (optional check) | Declined | The stock-constrained variant of the fast case was not computed. The stress test varies change capacity over its stated range (S10). |
| GLM-12 | The uniform clock is a long-run limit applied over 11 years | Already handled | Already handled | S2.7 already says so. No change. |
| GLM-13 | Ground the 5%/1% thresholds with a later-vintage anchor | Already handled | Already handled | Disclosed in A.4, and both thresholds are reported. No change. |
| GLM-14 | How the N_o=24 occasions map to interim periods is unstated | Partly valid (clarify) | Fixed | S9, Remark S10: N_o = 24 "(an illustrative count, for example two a month with the interim closes included)". |
| GLM-15 | §2.3's "We have not found" should acknowledge Ge and Huang (2014), an SFA of SaaS firms' economies of scale | Valid (optional citation) | Fixed | M 2.3 cites Ge and Huang (2014): a stochastic frontier of SaaS firms' economies of scale, not a growth-margin frontier. Bibliography verified at the IEEE index record and the second author's list. |
| GLM-16 | Acknowledge the adjacent AI-auditing literature beside Prop. 5 | Partly valid (optional) | Declined | No specific source was proposed, and the reviewer found no formal antecedent; no citation added. |
| GLM-17 | Roche and Tandon (2021) content unverifiable (McKinsey 403) | Already handled | Already handled | Recorded as verified in notes/ref_verification.md. No change. |
| GLM-18 | Dell'Acqua et al. numbers were checked against the 2023 WP, not the published version | Partly valid (optional check) | Partly | The figures match the working paper and secondary summaries of the 2026 article. The publisher's page could not be read, so the check against the published version is not complete. No change. |
| GLM-19 | Cottier et al. (2025): 9-900× (Epoch) against 10-1,000× (Gundlach's paraphrase) | Already handled | Already handled | The number matches its cited source. No change. |
| GLM-20 | State the search protocol (databases, queries, date) behind §2.2's and §2.3's negative-existence claims | Partly valid (optional) | Fixed | A.6: a new sentence says how the negative-existence statements were searched (web searches by the literature agents and the outside reviewers; candidates checked at Crossref, RePEc or the publisher; no query log kept). |
| GLM-21 | The [54, 62] interval reflects anchor resampling only; possible misreading | Partly valid (= GPT-24; see GPT-9) | Fixed | = GPT-24 and GPT-9 (ST-2). |
| GLM-22 | "The supplied PDFs are newer than every PDF committed"; "the committed .tex also lags the supplied PDFs"; "the… | Not valid (reviewer error) | Not valid | The reviewed PDFs are older than the committed sources. No change. |
| GLM-23 | Confirmations: static theory and Prop. 2 numerics; all 164 Table 2 cells; a full 999-draw bootstrap rerun… | Valid (no change) | Already handled | Confirmations; no change needed. |

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
