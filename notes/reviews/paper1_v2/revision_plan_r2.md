# Paper 1 v2: round-2 revision plan
Written 2 Nov 2026, 10:12 UTC−8, by the lead agent once all eight round-2 reports were in. Source: issue_log_r2.md (finding IDs below point to it). The snapshot under review is notes/reviews/paper1_v2/ (frozen 29 Oct, 18:42 UTC−7).

## Verdicts
| Report | Model | Verdict | Heaviest items |
|---|---|---|---|
| Theory | Fable | Minor | Abstract kG double count; free-entry overclaim; Cor. 4(c) proof |
| Econometrics | Fable | Minor, no numbers change | "No detectable change" fails D-3; inference sentences overstate Holm |
| Finance and accounting | Fable | Minor | Interest income left in the cash score; SOX direct cost too low; 5% threshold class |
| IO and AI economics | Fable | Minor (3 majors) | Pass-through implemented as a rate, not an elasticity; Demirer misused; compute-range factor 0.5 undocumented |
| Executives | Sonnet | 5 majors | No go/no-go (payback); varpi described as success; no executive entry point or misuse box |
| Risk, audit, regulatory | Sonnet | Minor to moderate (2 highs) | p^cc knife edge; authorship sentence; RA-3 filings paragraph |
| Investment management | Sonnet | Major revision of the empirical sections | T(20%) contradicts "no detectable change"; unstable decomposition; anchor intercept interval |
| Investors and bankers | Sonnet | 7 highs | No score-to-multiple bridge; weight leftovers; abstract basis; Bending Spoons stale |

Across models: the three Fable referees see a minor revision; the four Sonnet panels ask for more. The disagreement is about the empirical headline and the practitioner layer, not about the theory or the code. Every reported number reproduced (econometrics referee: 5,821 estimates and 1,862 bootstrap summaries; IO referee: all headline numbers from calibrate_horizons.py; theory referee: verify_theory 189/189).

## Author decisions needed
1. **Authorship wording** (RR-N2). Proposed text: "The author posed the research questions, made the decisions listed in Appendix B, and reviewed the manuscript; AI research agents drafted the text, code and proofs under her direction."
2. **Competing interests** (RR-N15, IB2-other; also RA-6 in round 1). The author decided on 29 Oct not to include a statement. Options: keep none, or add a minimal generic one.
3. **SEC data retrieval** (F2-1, IM2-N8, IB2-N6, F2-other). Through the author's built-in browser, as on 29 Oct:
   - XBRL frames for interest income;
   - contract liabilities and deferred revenue;
   - Bending Spoons 6-Ks through 29 Oct and the F-1 cash flow statement (interest paid).
4. **Central basis for the S&M bound** (IM2-N7). Report all three; choose the central basis.
   - The 2036 score is 66.2 if all S&M buys growth, 59.5 maintenance-netted and 55.7 with no S&M.
   - The lead agent recommends maintenance-netted as central, because it uses the paper's own maintenance evidence.

## A. Claims to withdraw or correct (text; editor)
- **A1. "No detectable change in the best margins at a given growth rate."**
  - Delete it in 5.10(v), the introduction and the conclusion.
  - Replace it with the facts by growth band and basis:
    - T(0) after SBC is −3.3 [−6.4, −0.2] in E1 and excludes zero in 2 of 4 views;
    - T(20%) GAAP is −10.2, excluding zero under the basic, normal and BC intervals but not the percentile interval.
  - Revisit the §7.4 inference that the supply of growth opportunities binds.
  - Sources: E2-1, IM2-N1.
- **A2. Inference sentences.**
  - The GAAP P95 decline has a Holm p range of 0.054–0.208, so it does not survive at 10% under every interval type.
  - The cash decline fails Holm at 10% (0.15–0.34) and Romano–Wolf.
  - Make the abstract asymmetric.
  - Flag the two tests against a slope of −1 and the two tautological margin-gap tests.
  - The CLAIMS check must cover all four interval types.
  - Sources: E2-2, IM2-N5/N4.
- **A3. Slopes.**
  - Report the break (−0.22 before 2020, −0.60 after) instead of the pooled slope in the abstract.
  - "The GAAP slope steepened" holds in 3 of 4 views; say so.
  - Sources: E2-4, IM2-N4.
- **A4. Composition.**
  - Present the decomposition as not robust to binning: composition ranges from −3 to −18 across specifications.
  - Drop "because fast growers became scarcer".
  - Add the full-distribution shift (P10 −19.9, P50 −6.9, P95 −11.9) and the IPO-cohort count (83 → 18 first-year firm-years) as competing readings.
  - Sources: IM2-N2, X2-N5.
- **A5. 2025 recovery.** It holds in E1 only; excluding acquisition years it is 2.8 points, not 9.3. Sources: IM2-N3.
- **A6. Screening advice.** Remove "use the Rule of 40 to screen firms", or state that the paper does not test it. Sources: IM2-screen.
- **A7. Leftovers of the withdrawn weight.**
  - Fix these four places:
    - §8.1's "20 points below" (the net spend ratio of 0.99 implies about 0);
    - Table 7's X̂−k = 11 proxy;
    - the conclusion's "accept a lower Rule-of-40 score";
    - the worked example's "5 to 15".
  - Replace the X = 2.5/5/9 placeholders in §6 with the sign-flip statement at X = k_acq (between 1.7 and 3.2).
  - Sources: IB2-N3/N4, X2-N8, IM2-N9, E2-minor, F2-4.
- **A8. Theory wording.**
  - TH2-1: the abstract intercept ("the margin intercept, plus …").
  - TH2-4:
    - "Under free entry, the limit is set by what stays scarce" becomes: scarcity decides who captures the savings;
    - "near-complete automation" is softened to match Cor. 4(a).
  - TH2-2: the Cor. 4(c) condition δm0 − Gδk + (X−k)δG ≥ 0.
  - TH2-3: ν_D = 0 in the pace formula, and remove the companion-paper residue.
  - TH2-5:
    - state the two HJB consequences of (H);
    - add the after-tax extension of Prop 4(d).
  - TH2-minor list.
  - The free-entry sentence gets the homogeneous-product qualifier (IO2-other).
- **A9. Demirer et al.** Remove the pass-through claim (§7.2, Table S7). Sources: IO2-2.
- **A10. Authorship sentence.** Use the author's approved wording (decision 1). Sources: RR-N2.
- **A11. Owner-type sentence.** Fix or remove "a sponsor's faster decisions change nothing", and point to Paper 2 for owner analysis. Sources: IB2-N7.
- **A12. Title-page footnote.** Add "firms may apply the ideas" and correct the response's EX-9 entry. Sources: X2-EX9.

## B. Recomputations (code: calibrate_horizons.py, paper1_macros.py; lead agent writes, editor places)
- **B1. Pass-through.**
  - Re-derive from Lemma S2 as an elasticity, including the effect of the price cut on the revenue denominator.
  - Define and cite the retention rule.
  - Treat all savings consistently (Prop 4(d)).
  - Recompute G* with pass-through. The reviewer expects about 32%.
  - Fix the introduction's "36% if half pass through" and the abstract.
  - Sources: IO2-1.
- **B2. Compute-share range.** Justify CC_VALUE_TEST_CAP = s_L × 0.5 and reconcile it with the no-review ceiling, or use the stated value test (range 27–77%). Recompute the abstract range and the 40% high-compute case. Sources: IO2-3.
- **B3. Compute path.**
  - State κ_front and ω_H as class-d drivers.
  - Say that the 31% headline is at 2025 prices and is not a date on the path.
  - Remove "no measured analog".
  - Sources: IO2-4.
- **B4. Text–code consistency.**
  - Error-loss labor share: 30% vs 60%.
  - Transition cost: "two years" vs 1.25 in code. Decide from the source, then recompute the dip and the crossing.
  - The basis of the fast-execution dip.
  - The "highest measured error rates" case must use AI catch rates.
  - Sources: IO2-5.
- **B5. Anchor interval.** Carry the intercept's firm-cluster interval (median 42.0, [34.1, 52.4]) through the central path. The reviewer's reconstruction gives 2036 ≈ 62–72 and 2028 ≈ 49–66. Report the intervals in the abstract and the table. Sources: IM2-N6.
- **B6. S&M bound.** Report all three bases, with the central basis per decision 4. Sources: IM2-N7.
- **B7. Payback and value.**
  - Report the crossing year next to the cumulative payback year, both undiscounted and at 9.34%; the reviewer has about 7 and 8.
  - Add the G* decomposition: taxes are 18.0 of the 31.0 points.
  - Add the program NPV.
  - State what follows for 3–5 year holds.
  - Sources: X2-N1, IO2-other.
- **B8. Rows to add.** A k < 0 row for annual-upfront billers (the reviewer has about 24%), and a typical $1–5B firm row in Table 4. Sources: X2-N11, X2-N4.
- **B9. Pace bridge.**
  - Decompose the move from 23% to 41% into three parts: success rate, realized share and T_emb.
  - Relabel varpi as "share of attempts that create some value".
  - State that the target is the product varpi × b̄ ≈ McKinsey's unconditional realized share.
  - Test the reviewer's 32%.
  - Add BCG win-only (0.30 × 0.67) as the pessimistic tornado case.
  - Add an owner-led execution row.
  - Sources: X2-N2, IB2-N8.
- **B10. Decision weight by discount rate.** Show it at r = 9.34, 10, 12, 15, 22 and 31%. Sources: IB2-N3.
- **B11. Score to multiple.**
  - Add an analytical table of iso-score points at different values from Lemma 5, in code.
  - State in the main text that no mapping is estimated.
  - Define "price line" at first use.
  - Sources: IB2-N1/N2.
- **B12. Tornado.** Motivate the 5–30% G band or narrow it. Sources: IO2-other.
- **B13. Econometric disclosures.**
  - The E2 grid-cell minimum inside draws (10 vs 30 in the sample) and the defined-draw interval [−0.505, −0.080].
  - The anchor added to family B (Holm p: normal 0.006, percentile 0.096, basic 0.030).
  - Bounds on the lead regressions.
  - An accurate description of Romano–Wolf (max-t with fixed scaling).
  - "3.8 expected" becomes 3.6.
  - The DFL quantile definition.
  - "The 2016–19 gap behaves the same way" is softened.
  - R3-18.
  - Sources: E2-3, E2-5, E2-minor.

## C. Accountability floor (code: the ICFR block of calibrate_horizons.py and paper1_macros.py; editor for the text)
- **C1. Threshold ε̄.**
  - Make it a class-d scenario parameter with no central value, and report 1% and 5% side by side.
  - Add the per-objective reading: 5% at firm level is about 0.5% per objective across about 10 objectives.
  - Define the event behind π against AS 2201.
  - State the common-mode condition: no single-provider all-AI design passes only if p^cm ≥ 0.0021.
  - Disclose the 1% → 5% switch in B.4 (research_errors_log B1o).
  - Sources: X2-N14, F2-3, RR-N3–N7.
- **C2. Break-evens.**
  - Add break-evens in p^cc (one-over-one fails above about 0.0008 at 5%) and in the human miss rate (fails at 10%).
  - State automation bias as excluded, or add a parameter for it.
  - Present the cheapest design as conditional, not as a finding.
  - Sources: RR-N1.
- **C3. Direct audit and SOX cost.**
  - Re-ground on KPMG by firm size; add a Table S7 row.
  - Recompute the floor (the reviewer has 0.34–0.56%) and the application counts on both the $80k reference line and the $205k invoice line.
  - Sources: X2-N13, F2-2, RR-N11.
- **C4. Labels and limits.**
  - Label 10 controls and $150/h as assumptions; only the 16 h per control is KPMG.
  - Add the external audit effort for AI-performed controls, and the policy and third-party channels, as stated limitations.
  - Sources: RR-N8–N10.
- **C5. Audit Analytics later editions.** The panel's 6.8%, 4.7%, 6.2%, 7.6% and 3.8% figures stay out until the lead agent reads them at the source. Note that FY2019 conflicts with the 4.8% now cited. Sources: RR-N3.
- **C6. Low-severity items.**
  - The $350k vs $204,672 ITGC figures.
  - Table S7/S9 verification labels.
  - Scope of the AI Act line.
  - The SR 26-2 caveat into the main text.
  - Sources: RR-N16–N22.

## D. Accounting, tax and filings (editor; data by the lead agent)
- **D1. Interest income.**
  - Add a "before net interest" row, and relabel the current row "before interest paid".
  - Add a sensitivity of the anchor to after-tax interest income.
  - Needs decision 3.
  - Sources: F2-1, IM2-N8.
- **D2. Cash–GAAP gap.** Check contract liabilities and deferred revenue as drivers of the 13-point gap. Needs decision 3. Sources: IM2-N8.
- **D3. Bending Spoons.**
  - Update the case through the 29 Oct 6-Ks, each item verified at the SEC: SACE loan, term loan B add-ons, Miro, Berkshire placement, notes.
  - Add a run-rate interest note and a sensitivity at the marginal coupon.
  - Fix the basis labels and add an SBC note.
  - Qualify the convention sentence with "in the year of purchase".
  - Use F-1 interest paid for 2023–25.
  - Needs decision 3.
  - Sources: IB2-N6, F2-5, F2-other.
- **D4. §8.5 and tax wording.**
  - §8.5:
    - "attest to that assessment" against AS 2201.03;
    - add 18 U.S.C. §1350;
    - filer-status wording.
  - Tax and other wording:
    - WACC vs the firm's notes and hurdle;
    - CAMT applies above $1B AFSI;
    - T(0) text says g ≥ 0;
    - separate the §168(k) elect-out (about 20%/54%) from ψ = 0 (33%/74%).
  - Sources: F2-other, RR-N16–N22.
- **D5. "Use in filings" paragraph.** Add it to §8.3: Reg G, Item 10(e), the 2022 C&DIs, Release 33-10751, the IPO safe harbor. The editor verifies the panel's text at each source before use. Sources: RR-RA3.

## E. Executive and investor layer (editor)
- **E1. Entry points.**
  - A one-page executive summary box after the abstract, drafted from the executives panel and checked against the macros.
  - A glossary in the supplement.
  - Simpler abstract wording.
  - Sources: X2-N4.
- **E2. "How not to use these numbers" box.** It covers:
  - 66 without 55;
  - 31% without its conditions;
  - Table 6's 117 and 92;
  - ε̄ read as a tolerance;
  - causal readings.
  - Sources: X2-N5, IB2-other.
- **E3. Cut §7.5.** Keep the proposition, the ratio test and one illustrative table; point to Paper 2's playbook; fix or remove the stage rule. Sources: X2-N3.
- **E4. Sample framing; naming the anchor firms.** Sources: IB2-other.
- **E5. Missing citations.** Verify each before citing: Babina et al., Sutton, Weyl–Fabinger, Vaccaro, Agrawal–Gans–Goldfarb, Gans–Goldfarb (O-ring), METR, Marschak–Andrews (1944). Sources: IO2-other, TH2-minor.

## F. Protocol (Appendix B; editor)
- **F1. Agents and models.**
  - "No access" becomes "told not to read".
  - Give exact model IDs (claude-opus-5-5, claude-fable-5-1, claude-sonnet-5-5), tool permissions and transcript retention.
  - Sources: RR-N12–N13.
- **F2. Author checks.** State what the author personally checked, and that no human specialist reviewed the legal and accounting statements. Sources: RR-N14.
- **F3. Disclosures.**
  - E2 grid minimum.
  - The Ψ_χ slopes on the v1 sample (−0.20/−0.16) were known when D-2 was decided.
  - The ε̄ switch.
  - Sources: E2-3, E2-5, C1.
- **F4. Competing interests.** Per decision 2.
- **F5. Limitations.** Assumptions register α (class c → as used); SIC codes not point-in-time; the $50M screen on latest-filed revenue. Sources: IM2-N10/N11.

## Order of work
1. Lead agent: B1–B5, B7–B12 and C1–C3 in code, with the round-2 regression check (verify_theory, claim_checks, verify_part2_accounting).
2. The SEC retrieval, if approved (D1–D3).
3. Editor (resumed): A, C4–C6, D4–D5, E and F, then B and D once the numbers are in.
4. Propagate to Paper 2 and the engine: pass-through, compute range, ε̄, direct audit cost and payback. Log each in cross_paper_impacts.md.
5. Final audit by a model that did not draft (Fable), against this plan and issue_log_r2.md.

## Author decisions (2 Nov 2026, about 10:15 UTC−8, via the question form)
1. **Authorship:** the shorter version. "The author directed the research and made its decisions; AI agents drafted the text, code and proofs (Appendix B)."
2. **Competing interests:** add a minimal statement. The lead agent drafts it and the author approves the exact text. The draft must not assert facts about the author's employment that she has not stated.
3. **SEC retrieval:** approved. Interest income and deferred revenue/contract liabilities for the 292 core firms; Bending Spoons 6-Ks through 29 Oct and the F-1 cash-flow statement. Through the built-in browser, nothing entered on any site.
4. **S&M basis:** maintenance-netted is central (59.5 for 2036 on v2 numbers). The all-S&M (66.2) and no-S&M (55.7) values are reported as bounds.
5. **Declarations confirmed (2 Nov, 10:45 UTC−8).** "Correct. This is completely independent research." The text goes in as drafted: "Funding: the author received no funding for this work. Competing interests: the author declares no competing interests."
6. **What the author checked (2 Nov, 10:45 UTC−8).** "I am reading through the paper and running through multi LLM reviews independently. I will give you the feedback from feedback agents."
   - Appendix B states that the author is reading the manuscript and commissioning independent reviews by other language models, run outside this workflow.
   - It makes no claim that she verified specific numbers, proofs or legal statements.
   - The sentence is final only once her review is complete. Her reviewers' feedback will be logged as a separate source (issue IDs AU-*) and answered in the response document.

## Lead-agent rulings on the coder's open questions (2 Nov, about 11:55 UTC−8)
Source: notes/r2_code_changes.md.

1. **Pass-through (B1): the coder's derivation is central, 36.2 / 38.3% at φ = 0.5 / 0.7.**
   - It treats φ as the industry pass-through rate on all unit-cost savings, consistent with Prop 4(d), which the referee itself asked for.
   - It agrees with Lemma S2's elasticity to first order (check 25g).
   - The referee's reading (rate φ(1−H), variable savings only; 33.7 / 34.3 at the new base) is reported in the supplement as an alternative, with the reconciliation table.
   - The final audit must re-derive this item independently.
2. **Error-loss base (B4): 60% of revenue, the same base as compute.**
   - No source was found for 30%. G* central becomes 32.5%.
3. **KPMG 2025 SOX survey by size (C3): the size labels are verified; the values are not.**
   - The PDF now returns 404 at kpmg.com (checked in the browser on 2 Nov). The lead agent opened the archived copy (web.archive.org, capture of 18 Mar 2026) and read page 12, "Average budget for SOX programs of \$2.3 M".
   - The chart "By revenue size (average budget in \$ M)" lists large (\$25B+), mid (\$5–25B) and small (under \$5B) from left to right. The values \$4.7M, \$2.7M and \$1.5M are from the text extraction; they are too small to read in the screenshot.
   - The order follows from the extraction and from the chart's title, "As revenues increased, the average SOX program budget also rose".
   - Cite the archived URL. Label the values "read from a text extraction; chart layout and labels verified".
4. **Size-matched audit fee (C3): the Audit Analytics accelerated-filer average is now central.**
   - Source: Ideagen Audit Analytics, *Audit Fee Trends 2003–2022* (July 2023), p. 14, read by the lead agent in the PDF on 2 Nov:
     - "In FY2022, average audit fees paid by accelerated filers increased 31% from FY2021 to \$1,492,375."
     - Large accelerated filers: \$5,327,646.
   - For a \$1B-revenue firm, the accelerated-filer average is the size-matched figure. It is a lower bound if the firm is a large accelerated filer.
   - The S&P 500 fee ratio (\$343 per \$1M of revenue) becomes the low bound.
   - Central direct cost = KPMG under-\$5B SOX budget \$1.5M + \$1.49M audit fee, about 0.30% of revenue at \$1B. The finance referee's direction is confirmed; its \$1–2M fee now has a source.
5. **ITGC line (C6).** The \$350k ITGC-and-revalidation figure inside the design cost must use the sourced \$204,672 line, or document why it differs.
6. **Owner-led execution row (B9).** Not built. The sponsor-latency variant has no effect while change capacity binds; the text states this and points to Paper 2 for owner analysis (IB2-N7). Status: Partly.

## Author decision 7 (2 Nov, about 12:35 UTC−8): one S&M basis for the levers and the playbook
**What was found.** The propagation agent (notes/r2_propagation.md) re-checked the lever ranking. On the maintenance-netted basis (b_M = 25.1% of revenue), automating the growth engine beats cutting G&A at only 1 of 6 positions (the growth corner). With no S&M it leads at none; on the all-S&M basis it leads at 6 of 6. P1's levers table and the P2 playbook still used all-S&M.

**Explained to the author.** The prior assumption, that every S&M dollar buys growth, was explained to her, and she chose "netted everywhere". Accordingly:
- the levers table, the P2 playbook and the engine use the netted basis as central;
- all-S&M and no-S&M results are reported as bounds;
- the lead practitioner finding is stated as basis-dependent: cutting G&A comes first for most positions; automating the growth engine leads only where S&M well exceeds the maintenance level.

## Author instruction 8 (2 Nov, about 14:50 UTC−8): remove the employer's data
**The instruction.** Asked whether to keep "no competing interests" or add an employment line, the author replied: "I asked you to remove [employer] related data." (employer name redacted here). The lead agent's 29 Oct record ("the author's employer is not named anywhere") had kept only the name out, not the data.

**What the lead agent found** (2 Nov, by grep over the repository):
- The companion paper's price example no longer uses the employer's prices. The four products are Freshworks, Fin/Intercom, Salesforce and HubSpot, and no employer string appears in part2/ or params.yaml. The agent-log note of 29 Oct ("the author's employer is one of them") is stale.
- The employer's SEC filings remain in the broad-universe files: one SIC 7374 registrant, 10 firm-years in panel_v3_all.csv. They are also in sic_universe.json, frames_universe.json, frames_extra.json, companyfacts_ciks.txt, companyfacts_extract.json, companyconcept_revenue.json, growth_filing.csv, panel_all.csv, panel_v2_all.csv and panel_broad.csv, and in the dist/replication copies.
- The registrant is not in the 292-firm core sample (panel_v3.csv) or in the 2 Nov interest and deferred-revenue frames.

**Action.**
- Purge the registrant from every data file.
- Exclude it in the fetch and build scripts by a hashed identifier, so that a rebuild from the SEC cannot bring it back and no file names it.
- Rerun every affected stage and report every number that moves.
- The paper states only that one registrant is excluded at the author's request.
- The competing-interests line stays as the author confirmed it.

**Status (2 Nov, about 17:00 UTC−8): done.** The registrant was purged from every data file and from the replication copies, and the fetch and build scripts drop it by a one-way hash (`code/exclusions.py`, `code/purge_excluded.py`). Rebuilt panels are byte-identical to the purged ones, and a full scan of the container finds no occurrence of the name or identifier. Paper 1's reported figures are unchanged. In the companion paper the backtest placebo row moved slightly (placebo n 161 → 160; `\btFirmPlB` 2.0 → 2.1). Paper 1 states the exclusion in Section 4.1, Appendix S6 and Table 8, without naming the registrant. Details: notes/r2_exclusion.md. The declarations are unchanged (no funding, no competing interests), as the author confirmed at 10:45.
