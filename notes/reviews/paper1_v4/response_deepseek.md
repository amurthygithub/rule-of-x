# Response to your review of *The Rule of 40 as a Price Line* (third version)

**To:** DeepSeek V4 Pro (high effort)
**From:** Akshaya Bangalore Sreenivasa Murthy (author), with the lead agent of the research session
**Date:** 4 November 2026
**Your review:** of the build of 2 November 2026 (main paper 82 pages, SHA-256 bd87f45f…; supplement 57 pages, acf9d62b…) and the repository at commit 62e574b
**Your verdict:** "No demonstrated error was found"; accept for release as a working paper with minor corrections, and minor revision at a specialist field journal contingent on (a) proving or re-scoping hypothesis (H) and (b) human specialist sign-off on the tax, regulatory and scenario-parameter claims.

Thank you for the review. Your review reproduced every headline number you re-derived, confirmed the theory you checked and found no error in the theorems, the estimates, the case study or the regulatory claims. We verified each of your 70 findings, plus two defects (X-1, X-2) found during that verification that no review had raised. Your two conditions are where the paper moved most:

- **(H):** We took your option (ii). "Under (H)" now appears at each of the 16 decision-weight statements (DS-17). (H) is still not proved, and the paper says so in M 3.6.
- **Specialist sign-off:** No human specialist has read the paper. In its place, every legal and tax citation was checked at its primary source (item 9 below), the scenario parameters were stress-tested jointly (S10), and the static theory was machine-checked in Lean 4 (S4). A human specialist's reading before journal submission is still advisable, and A.6 says what the protocol does not establish.

Six of your findings we classify as not valid; each is explained in the table. Please contest any of them you think we have wrong.

**How we handled it.** Each finding was verified in the research session against the paper's sources, the code (re-run on clean exports of the commit you read), the stored outputs and primary sources. We classified each as valid, partly valid, not valid (a reviewer error) or already handled. The author then adopted every fix the verification supported (2 November, 23:23, and 3 November; Table 8). Our evidence for each finding, including the scripts we ran, is in `notes/reviews/paper1_v3/author_reviews/deepseek_v4_pro_high/` (`issue_log.md` and `verification_claude/`). The joint response to all four outside reviews is `notes/reviews/paper1_v3/response_to_outside_reviews.md`. This letter is self-contained, but it uses that file's dispositions.

**Your findings, by status:** 14 fixed, 6 not valid, 52 already handled (72 rows). *Fixed* means changed as the issue log proposes, in the paper, the code, the data or the repository; *Partly* means part of the proposal was applied, and the row says what was not and why; *Declined* means deliberately not applied, with the reason; *Not valid* means we think the finding is mistaken, so nothing changed; *Already handled* means the paper already did what was asked, or the item was a confirmation.

## What we would most like you to check

1. DS-17: "under (H)" at the 16 places itemised in the row (count them in the current sources)
2. DS-35, DS-37, DS-38: the bibliography and citation fixes
3. DS-65, DS-67, DS-68: the acquirer case against the filings now in `data/v3_inputs/raw/` (hashes in `README_retrieval.md`, section 5)
4. DS-13, DS-21, DS-34, DS-39, DS-40, DS-59: our reasons for classifying these as not valid
5. X-1, X-2: the two defects found during verification
6. The new S4 (machine-checked proofs) against the theorems you checked by hand, and S12

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
| DS-1 | "No demonstrated error"; "no theorem, estimate, table, or case-study number needs correction" | Partly valid | Already handled | No change to the verdict itself. The defects it missed are fixed under X-1, X-2 and DS-69. |
| DS-2 | "Every headline number I re-derived or re-ran reproduced exactly", computed "with my own script… | Partly valid | Already handled | Reviewer provenance only; the numbers are right (DS-3). No change. |
| DS-3 | Panel 1,788 / 292; period counts 465/418/458/447; Ψ0.90 slopes −0.22/−0.16 (0-60%), −0.31/−0.27 (0-40%)… | Valid | Already handled | Confirmation; no change needed. |
| DS-4 | verify_theory.py 191/191 pass | Valid | Already handled | Confirmation; no change needed. |
| DS-5 | verify_part2_acquirer.py 82/82 pass | Valid | Already handled | Confirmation; no change needed. |
| DS-6 | paper1_macros.py passes "the CLAIMS gate (every sentence of the text is supported by a pipeline output)" | Partly valid (overstated) | Already handled | Overstated claim about the CLAIMS gate; A.6 already says the checks test the text against the pipeline's outputs only. No change. |
| DS-7 | Bootstrap not re-run; seed = 20261030 + CRC-32 of the block name | Partly valid (minor misstatement) | Already handled | Reviewer's misstatement; S7 already gives the seed rule with "modulo 10^6". No change. |
| DS-8 | "five pre-registered sample rules", four estimands E1/E2/M4/M8 | Partly valid (wording) | Already handled | The paper does not say "pre-registered"; A.4 lists the choices made after results were seen. No change. |
| DS-9 | Prop 1 score budget correct and sharp; the supremum is approached, not attained (Prop S2) | Valid | Already handled | Confirmation; no change needed. |
| DS-10 | Finiteness needs zero-spend growth ≥ G; Remark S1(b) bound grows linearly in T | Already handled | Already handled | Remark S1(b) already states it. No change. |
| DS-11 | Lemma 1(a),(c) need k ≥ 0; convexity needs capacity installed ahead (Lemma S1); k < 0 caveats | Already handled | Already handled | Remark S1(c) and Lemma S1 already state it. No change. |
| DS-12 | Lemma 2 closed forms (5)-(7), tangency, duality, corner at X ≤ k | Valid | Already handled | Confirmation; no change needed. |
| DS-13 | Lemma 2 numbers at the Figure 1 parameters "match Figure 1 exactly" | Not valid (reviewer error) | Not valid | The reviewer evaluated the frontier at ell = 0.588, not the caption's 0.6; Figure 1 is correct. |
| DS-14 | Corollary 1 example: bounds 1.8, 9.6, 5.0; 0.43 and 0.30 years | Valid | Already handled | Confirmation; no change needed. |
| DS-15 | Lemmas 3-5, Cor 2-3, Prop 3 (non-identification), Remark 3, Prop 9 "OK" | Valid | Already handled | Confirmation; no change needed. |
| DS-16 | Prop 2: HJB (17), verification argument, root (19), singularity; (a),(d),(e) unconditional, (b),(c) need (H) | Valid | Already handled | Confirmation; no change needed. |
| DS-17 | MAJOR: (H) is unproved; prove it for a parameter class, or downgrade every decision-weight assertion | Partly valid | Fixed | Author decision 1 (23:23): option (ii), "under (H)" at each of the 16 places itemised in `notes/r3_text_changes.md` (17 new "(H)" strings; the independent audit of 3 Nov counted them per file: literature 3, model 5 including the title of Prop. 2, empirics 2, Section 6 1, discussion 2, S1 Remark S1(a) 1, S2.2 2, S13 glossary 1). (H) itself is not proved; the global qualifier of M 3.6 stays. |
| DS-18 | "Every 'value-maximizing firm acts on weight v′(s)' statement is flagged conditional on (H)" | Partly valid (overstated) | Fixed | Covered by DS-17. |
| DS-19 | (H) affects §8.1, "a fixed threshold marks down firms...", and the §7.5 lever ranking "at the firm's own weight" | Partly valid | Already handled | The M 7.5 ranking uses the weight a position's own spending reveals, not v'(s); the M 8.1 sentences are covered by DS-17. No further change. |
| DS-20 | Prop 2(e) proof: "uses only g(υ)<r and m(υ)>0" omits k ≥ 0 | Valid (cosmetic) | Fixed | S3, proof of Prop. 2(e): "uses only g < r, m > 0 and k >= 0". |
| DS-21 | Root of (19) exists iff λ ≤ (r−G)/(m0−kr)^α; the v0 = 10 worked example sits in a regime that is "thin when λ is… | Not valid as a defect (observation) | Not valid | An observation, not a defect: the worked example lies inside the root's existence region (threshold 0.0822 against lambda 0.070), and Prop. 2(d) and (e) cover both cases. |
| DS-22 | Prop 4 free entry correct; a special case of Mankiw-Whinston, as the paper states | Valid | Already handled | Confirmation; no change needed. |
| DS-23 | Prop 5: P_o(D) formula, admissibility equivalence, single-provider inadmissibility at any depth | Valid | Already handled | Confirmation; no change needed. |
| DS-24 | Props 6-7 (attainable and expected frontiers) correct | Valid | Already handled | Confirmation; no change needed. |
| DS-25 | Remark 2 tax treatment consistent with 26 U.S.C. §174A (Pub. L. 119-21 §70302(a)) | Valid | Already handled | Confirmation; no change needed. |
| DS-26 | Investors screen on a duration weight of 2-3 (Lemma 5) | Valid | Already handled | Confirmation; no change needed. |
| DS-27 | MAJOR: the empirics are descriptive, not structural; α(X−k) ranges 0.05-10.1 | Already handled | Already handled | The paper already states it (see the issue log for the locators). No change. |
| DS-28 | MAJOR: modest strength; Holm p 0.26-0.45 for the negative sign (GAAP); cash P95 decline survives under no… | Already handled | Already handled | The paper already states it (see the issue log for the locators). No change. |
| DS-29 | MAJOR: the 32.5% threshold is a scenario bound on an unmeasured 6% compute share; 28-78% over 1-60%; 36.2/38.3 at… | Already handled | Already handled | The paper already states it (see the issue log for the locators). No change. |
| DS-30 | State in the abstract's second sentence that 32.5% is a scenario bound conditional on 6% compute (28-78%), or… | Already handled (substance); placement… | Already handled | The abstract already states the condition on the compute share. With GPT-22 its range is now a "scenario range", and the threshold is "at central costs" (ST-1). The abstract is at its length limit, so no further placement change was made. |
| DS-31 | Ganapati et al. ϕ = 0.7 is transported from energy costs in manufacturing to an AI shock in software | Already handled | Already handled | The paper already states it (see the issue log for the locators). No change. |
| DS-32 | No human independent review; AI referees share a model family | Already handled (disclosed) | Already handled | Already disclosed. A.6 now also states what the three outside reviews did and did not establish (X-2). |
| DS-33 | Appendix A says "the eight referee reports recommended major revision" | Valid | Already handled | Confirmation; no change needed. |
| DS-34 | Lee (2024) sample: the paper's "1,756" vs the auditor's "1,771" | Not valid (auditor error; the lead… | Not valid | The published article gives 1,756 firms; 1,771 is the preprint's figure. No change. |
| DS-35 | Lee URL lacks /1/ and returns 404; DOI 10.24135/afl.v13i.761 correct | Partly valid | Fixed | Bibliography, Lee (2024): the URL now has /1/, and doi 10.24135/afl.v13i.761 is added. |
| DS-36 | Lee (2024) is the only peer-reviewed Rule-of-40 study (Crossref title search) | Valid (bounded) | Already handled | Bounded claim, now superseded by GLM-F3: a second peer-reviewed study (Nei, Ruus and Indov 2026) is cited and "only" is dropped. |
| DS-37 | Svanberg et al.: "exposed tasks" should be "vision tasks" | Valid | Fixed | M 2.4: "exposed tasks" -> "vision tasks" (Svanberg et al.). |
| DS-38 | Kwa et al. ">80% of successful runs <10% of human cost" is not in the abstract; needs a pin-cite | Partly valid | Fixed | S2.8: \citep[Figure~14]{kwa2025measuring}. The bibliography note now pins the paragraph "More use of inference compute", Appendix E.4. |
| DS-39 | The Vista (2026) title is stale; the piece was retitled to an "AI Rule of 60" slug | Not valid (reviewer error) | Not valid | The cited page still carries the cited title and URL. No change. |
| DS-40 | Mosleh et al. year "1989" could not be pinned | Not valid (the year is correct) | Not valid | The year 1989 is correct. No change. |
| DS-41 | Kim et al. (2025): "models agree 60% when both err"; the paper's caveat about what this measures is correct | Valid | Already handled | Confirmation; no change needed. |
| DS-42 | Bessemer Rule of X (~2× private, 2-3× public) and Feld (2015) attributions correct | Valid | Already handled | Confirmation; no change needed. |
| DS-43 | Brynjolfsson, Li and Raymond (2025) and Acemoglu (2025) correct; the Brynjolfsson DOI is correct and should not be… | Valid | Already handled | Confirmation; no change needed. |
| DS-44 | ICONIQ (2026): 45→53→59% AI product gross margin; 11→16→19% internal AI spend; ~300 executives | Valid | Already handled | Confirmation; no change needed. |
| DS-45 | Arkolakis (2010) and Gourio and Rudanko (2014) attributions correct | Valid | Already handled | Confirmation; no change needed. |
| DS-46 | Eight method and classic references verified bibliographically only; Dorfman-Steiner restated loosely but… | Valid (scope note) | Already handled | Confirmation; no change needed. |
| DS-47 | No direct predecessor found for the five claimed new results; non-identification rests on a known principle that… | Valid (bounded opinion) | Already handled | Confirmation; no change needed. |
| DS-48 | AS 2201 A7, Item 308(a)(3) and the FAS 5 note are quoted accurately | Valid | Already handled | Confirmation; no change needed. |
| DS-49 | 404(b) applies to accelerated and large accelerated filers, not EGCs; a newly public company's first annual report… | Valid | Already handled | Confirmation; no change needed. |
| DS-50 | §8.5 pins "AS 2201 ¶.03" for the 404(b) attestation scope; re-pin it to Item 308(b)/SOX 404(b) | Partly valid | Fixed | M 8.5: "AS 2201, paragraph .03" -> "paragraphs .03 and .06". |
| DS-51 | The paper invents no regulator-endorsed probability threshold | Valid | Already handled | Confirmation; no change needed. |
| DS-52 | Independence apart from p_cc favors diversity; shared tooling omitted; no automation-bias parameter; all disclosed | Already handled | Already handled | The paper already states it (see the issue log for the locators). No change. |
| DS-53 | A referee could ask for a parameterized automation-bias term rather than a break-even | Already handled | Already handled | The paper already states it (see the issue log for the locators). No change. |
| DS-54 | The common-mode floor follows from the beta-factor assumption; its empirical premise is unestablished | Already handled | Already handled | The paper already states it (see the issue log for the locators). No change. |
| DS-55 | Multiversion literature used correctly; beta-factor applied per control opportunity | Valid | Already handled | Confirmation; no change needed. |
| DS-56 | Remark S10 numbers reproduce (0.0021/0.0004; 11.3%; 4.7%; 3.1%, 0.75m; 1H+2AI 0.80m, 0.7%; 4.98%, 1.50m; 2H+1AI… | Valid | Already handled | Confirmation; no change needed. |
| DS-57 | Remark S10's "8.4% of the items the AI layers missed" is a miss rate apart from the human common mode; read… | Partly valid | Fixed | S9, Remark S10: the miss rate is stated apart from the human common mode of 0.002, 8.4% (8.6% including it); new macro \AminPhmTotFive. |
| DS-58 | The floor is probably understated (entity-level controls, service organizations, AS 2201 B28-B31), so the… | Already handled | Already handled | The paper already states it (see the issue log for the locators). No change. |
| DS-59 | Regulatory, accounting and tax claims "verified verbatim against primary sources by two parties" | Not valid (overstated) | Not valid | Each claim was checked by one party, not two. No change. |
| DS-60 | Table 3 reproduces (2024/2025 and Q1/Q2 2026 columns, non-GAAP shares, charged ranges, fully charged… | Valid | Already handled | Confirmation; no change needed. |
| DS-61 | r = 8.93% (ln 1.0934); T_life 10.6-19.5; CRF 14.59-10.83%; text ranges 87-114, 22-28%/14-22%, interest-paid… | Valid | Already handled | Confirmation; no change needed. |
| DS-62 | ASC 230-10-45-17(d), 350-20-35-1 and 805-10-25-23 stated correctly; the double charge is exactly (1−τ)c_fin… | Valid | Already handled | Confirmation; no change needed. |
| DS-63 | Prop 8 net weight X − k_acq; flag arithmetic (≥ 0.25/(1+g), 17 points at 50%); outflows 2.30×/2.76×… | Valid (arithmetic) | Already handled | Confirmation; no change needed. |
| DS-64 | The fully charged score is a lower bound because of the Vimeo timing (closed 24 Nov 2025; 327 days of revenue… | Valid | Already handled | Confirmation; no change needed. |
| DS-65 | E7 and notes/acquirer_notes.md still carry the fully charged −28.7/−24.8; update to −25.0/−16.5 | Partly valid | Fixed | Coding agent: check E7 relabelled (after interest, round-1 basis) and notes/acquirer_notes.md section 4 updated. The paper is unaffected. |
| DS-66 | m^cf adds back interest expense rather than interest paid; net investing outflow is a proxy (acquisitions… | Already handled | Already handled | The paper already states it (see the issue log for the locators). No change. |
| DS-67 | The raw SEC filings behind the case study are not in the repository; add them or signed checksums | Valid | Fixed | Author decision 3: the four filings (F-1, 424B4, 6-K Ex. 99.1 and 99.2) are in data/v3_inputs/raw/, with SHA-256 hashes in README_retrieval.md section 5 (retrieved 2 Nov, about 23:25). M 6 says the figures are read from the full filings; S7 describes the third retrieval; S8 Table S13 lists it. |
| DS-68 | The 6-K JSON holds only the cover page for accession 0002004711-26-000011 (Q2 2026), not Ex. 99.1 or Ex. 99.2 | Valid | Fixed | Exhibits 99.1 and 99.2 are archived in full (DS-67). |
| DS-69 | The paper discloses the pro forma caveat | Partly valid | Fixed | The pro forma figures were re-verified against the sec.gov 424B4 (coding agent, check I3; the pro forma revenue row is on 424B4 p. 143). As the log prefers, the text of M 6 is unchanged; the extract notes record the re-verification. |
| DS-70 | The working tree was a clean checkout of 586 files | Valid | Already handled | Confirmation; no change needed. |
| X-1 | The bst prints only a note's first sentence, cut at the first ". ", so four printed notes end mid-phrase: Lee… | Found in verification | Fixed | Bibliography: Lee note "MPRA Paper No. 121568" -> "MPRA Paper 121568"; deloitte2026cashflow, kpmg2025sox and brynjolfsson2025canaries: "U.S." -> "US" in the first sentence, so no printed note is cut mid-phrase. |
| X-2 | todo{R2: finalize once the author's review is complete} prints in paper1.pdf (A.6, p. 82) as "[R2: finalize once… | Found in verification | Fixed | A.6: the \todo marker is removed and the sentence finalized (author decision; see GPT-11, GLM-F4). |

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
