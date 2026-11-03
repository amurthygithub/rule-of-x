# Paper 1: response to the round-2 reviews

Prepared by the editor-author agent on 2 November 2026 for the third version of *The Rule of 40 as a Price Line*. The snapshot reviewed was frozen on 29 October at 18:42 (UTC-7); the plan is notes/reviews/paper1_v2/revision_plan_r2.md and the findings are in issue_log_r2.md and the eight r2_*.md reports.

**Status of this document.** It records the final placement pass of 2 November. The coding agent's recomputations (plan items B1-B13, C1-C3, the CLAIMS part of A2) and the SEC data (D1-D3) are in, and every number in the paper comes from the generated macros. The paper carries one red \todo marker, in Appendix A, until the author's own review is complete; her reviewers' findings (independent LLM reviews run outside this workflow) will be logged here as AU-* items. No reviewer's number was copied into the paper; where a reviewer's figure appears in a note below, it is the coder's recomputation. Author decision 7 (2 November, about 12:35 UTC-8: maintenance-netted S&M central for the levers too) is applied, and the text fixes of the final audit (notes/reviews/paper1_v3/final_audit.md) are logged below as FA-* rows; the coder's items (m6, m13, m15), the engine item (m11) and the author's item (m18) are now Fixed. At the author's instruction of 14:50 one registrant, not named, was removed from all data, code and replication files (notes/r2_exclusion.md); no figure in Paper 1 changed. Build of 2 November, after the audit fixes and the exclusion: main paper 82 pages, supplement 57, no undefined references, overfull boxes or oversized floats; CLAIMS pass in strict mode; verify_theory 191/191.

**Statuses.** Fixed: addressed in full in the text. Partly: addressed in part; the note says what remains and why. Declined: deliberately not done, with the reason. Waiting: the change belongs to a code or engine file, or to the author's own decision, that this pass did not change.

**Locations.** M = main paper, S = Supplementary Appendix; the numbers are those of the third version. The main paper's former Appendix A (full-cost floors, the accountability floor in numbers, owned compute) is Supplement Section S8 (Lemma S4, Remarks S9 to S11, Tables S13 and S14), and the protocol is Appendix A (decisions: Table 8). Supplement tables were renumbered when two new tables entered Sections S1 and S2: S1 notation, S2 pass-through readings (new), S3 iso-score values (new), S4 robustness, S5 frontier grid, S6 E1-E2 contrasts, S7 yearly statistics, S8 cash-score bridge, S9 parameter sources (formerly S7), S10 anchor firm-years, S11 agents, S12 errors, S13 break-evens of the control designs (new), S14 full-cost floors (formerly S11). New supplement subsections: S2.8 (compute share, path and pass-through), S2.9 (execution yield, ownership and the change from the first version), S2.10 (scores in filings) and S4.1 (interest paid and events after the second-quarter report). The glossary is Section S9.

## Counts by status

| Report | Findings | Fixed | Partly | Declined | Waiting on code or data | Open |
|---|---:|---:|---:|---:|---:|---:|
| X2: Executives panel | 25 | 12 | 12 | 1 | 0 | 0 |
| F2: Finance and accounting referee | 14 | 9 | 5 | 0 | 0 | 0 |
| RR: Risk, audit and regulatory panel | 23 | 18 | 5 | 0 | 0 | 0 |
| IO2: IO and AI economics referee | 21 | 19 | 1 | 0 | 1 | 0 |
| TH2: Theory referee | 18 | 17 | 1 | 0 | 0 | 0 |
| IM2: Investment management panel | 13 | 11 | 2 | 0 | 0 | 0 |
| E2: Econometrics referee | 14 | 14 | 0 | 0 | 0 | 0 |
| IB2: Investors and bankers panel | 25 | 18 | 6 | 1 | 0 | 0 |
| FA: Final audit of the third version | 24 | 23 | 1 | 0 | 0 | 0 |
| **All eight reports and the final audit** | **177** | **141** | **33** | **2** | **1** | **0** |

Plan items (A1-F5, grouped as in the plan): Fixed 39, Partly 7.

## Plan items

| Item | Status | Note |
|---|---|---|
| A1 | Fixed |  |
| A2 | Fixed | CLAIMS 60/60 (coder); text by procedure. |
| A3 | Fixed |  |
| A4 | Fixed | Bin range, quantile shifts and cohort counts placed. |
| A5 | Fixed | Recovery with and without acquisition years. |
| A6 | Fixed |  |
| A7 | Fixed | Table 7 regenerated; withdrawn macros removed from the text. |
| A8 | Fixed |  |
| A9 | Fixed |  |
| A10 | Fixed |  |
| A11 | Fixed |  |
| A12 | Fixed |  |
| B1 | Fixed | Rate on all savings; Table S2 next to Lemma S2. |
| B2 | Fixed |  |
| B3 | Fixed | Drivers in Section S2.8. |
| B4 | Fixed |  |
| B5 | Fixed |  |
| B6 | Fixed |  |
| B7 | Fixed |  |
| B8 | Fixed | In text (k < 0 and a typical firm), not as Table 4 rows. |
| B9 | Partly | Owner-led execution row not built; the sponsor-latency variant has no effect while change capacity binds (§7.3). |
| B10 | Fixed | §8.1 and Section S2.2. |
| B11 | Fixed | Table S3 (supplement, page limit) with the intro sentence. |
| B12 | Fixed |  |
| B13 | Fixed |  |
| C1 | Fixed |  |
| C2 | Fixed | Table S13 in Section S8. |
| C3 | Fixed |  |
| C4 | Fixed |  |
| C5 | Partly | Later editions out pending source reading. |
| C6 | Fixed | $204,672 line inside the design. |
| D1 | Fixed |  |
| D2 | Fixed |  |
| D3 | Fixed | Summary in §6, dated events in Section S4.1. |
| D4 | Partly | Elect-out bar stated qualitatively. |
| D5 | Fixed |  |
| E1 | Fixed |  |
| E2 | Fixed |  |
| E3 | Partly | Decision 7: §7.5, Table 7, summary box, intro and conclusion state the ranking on the netted basis with both bounds (G&A cut ahead of the growth engine at 5 of 6 positions; growth engine ahead only in the growth corner; engineering above both in the companion paper). Cost of revenue not ranked in P1. |
| E4 | Fixed |  |
| E5 | Fixed |  |
| F1 | Partly | Tools and roles stated; nothing claimed about transcript retention beyond the package. |
| F2 | Partly | Author's review described as she stated it; one todo until it is complete. |
| F3 | Fixed |  |
| F4 | Fixed | Text confirmed by the author. |
| F5 | Partly | Register alpha class: coder. |

## Point-by-point

### X2. Executives panel (Sonnet; r2_panel_executives.md), findings N-1 to N-24 and the EX-9 check

| ID | Finding | Status | Note |
|---|---|---|---|
| X2-N1 | No go/no-go rule; '4 years' is a flow crossover, not payback | Fixed | §7.3 separates the flow crossing (4.0 years) from cumulative payback (7.5 years undiscounted, 8.5 at 9.34%), reports the program NPV (98% of a year's revenue, revenue held constant) and the present-value ratio of gains to dip (3.9), and states that the cumulative effect is negative at three and at five years, so an owner with a horizon of five years or less would not fund the central program. Same statement in the intro, summary box, §8.2 and conclusion. |
| X2-N2 | Execution inputs more optimistic than sources; varpi called 'success' | Fixed | varpi is now 'the share of attempts that create some value', not a success rate (§7.3, Section S2.9). The yield varpi x b-bar = 0.47 is set against the unconditional 0.46; the like-for-like reading gives 31.5% realized by 2036 (the panel's 'about 32%' reproduces); BCG win zone only gives 17.4% and a 2036 score of 50 (new Table 6 row). Shapley bridge from the first version's inputs: 21.9% to 40.7% (S2.9). |
| X2-N3 | Levers by position not actionable | Partly | §7.5 rewritten around the ratio test, and Table 7 regenerated without the withdrawn weight on the maintenance-netted basis (author decision 7): at the revealed weight, cutting G&A outranks automating the growth engine at 5 of 6 positions; the growth engine leads only in the growth corner, where S&M is 25 points above the 25.1% maintenance base; two positions have no S&M above it. On the all-S&M bound the growth engine leads at all 6, and with no S&M at none. The text says this is a ranking against the growth engine, not of every lever: the companion paper, which values R&D as a cost line, ranks engineering above both at every position. The same statement is in the summary box, intro, how-not-to-use list and conclusion. Cost of revenue is not ranked in P1, and the positions are not $1-5B peers. |
| X2-N4 | No executive entry point | Fixed | Summary box after the abstract, glossary (Section S9), shorter abstract, and a worked typical $1-5B firm (2023-25 medians: intercept 49 points below the central full-cost term on the netted basis, threshold 37% at its own k), in §7.2 and Section S6 ('A typical firm'). Given in text, not as a Table 4 row. |
| X2-N5 | No 'how not to use these numbers' box | Fixed | Ten-item list at the end of §1; causal sentence replaced (empirics, abstract, intro, conclusion). |
| X2-N6 | Empirical headlines stronger than the evidence | Fixed | 'Because fast growers became scarcer' removed; 'across firms'; familywise status in the abstract; cost-of-capital and IPO-window readings in §5.2; 'not a case for lowering the bar' in the box. |
| X2-N7 | Headline scenario numbers can be misquoted | Fixed | The 2036 path is quoted everywhere with its anchor-sampling interval and both bounds: 59 [54, 62], 65 if all and 55 if none of selling spend buys growth (abstract, box, intro, §7.3, conclusion). Table 6 keeps one surplus row, with a note that it adds a transient surplus the median firm-year does not have. |
| X2-N8 | §8.1 re-imports the unidentified weight | Fixed | §8.1 restated: sign depends on alpha(X-k); 20 points only if all S&M buys growth, about zero net of maintenance; 'marks down such firms when...'. |
| X2-N9 | Central path has no decomposition; no firm-specific G | Partly | G* decomposition in §7.2 (tax 18.0, compute 4.9, fees 2.1, accountability floor 2.5, full-cost floors 5.1 points; 32.5% in all); pace bridge in S2.9; a typical firm's threshold at its own k (37%). No worksheet for a reader's own G. |
| X2-N10 | Seat compression, AI-native entry, pricing; regime test | Partly | Table 1 rows for seat compression and AI-native entry (scenarios); §8.6 sentence. No regime test, no consumption-pricing row. |
| X2-N11 | Table 4 omits k < 0 | Fixed | §7.2 bullet 'Deferred revenue and a typical firm': at k = -0.3 the central threshold is 25% (favorable and conservative cases also given), and at the median deferred-revenue intensity of growing 2023-25 firm-years (0.27) it is 26%. In text, not as a Table 4 row. |
| X2-N12 | Compute share conflates internal and product inference | Partly | The high-compute case is now within the value test and described as a feasible, compute-heavy full-automation structure (§7.2), and Section S2.8 says that the survey's AI-product cost of revenue includes talent and hosting. Not split into internal-automation compute and product inference: the ceiling prices a firm's own automation, and product-inference margins enter through gross margin (Definition 3), which we do not tabulate by AI revenue share. |
| X2-N13 | Floor numbers vs KPMG and SOX practice | Fixed | Direct cost re-grounded (C3): KPMG's budget for firms under $5bn ($1.5m; archived PDF, values read from a text extraction, chart labels verified) plus the Audit Analytics average audit fee of accelerated filers ($1,492,375), 0.30% of revenue at $1bn (0.18% with the S&P 500 fee ratio, 0.68% with the large-accelerated fee). Floor 0.37% (0.26 to 0.76%). The floor reaches 0.5% at 8 in-scope AI applications on the $204,672 invoice line and 17 on the $80k line (§7.2, Remark S10, Table S9 rows). |
| X2-N14 | Remote threshold: wrong object, knife edge | Fixed | The threshold is a scenario value (class d) with no central value; 5% and 1% are reported side by side (§3.9, §7.2, §8.5, Remark S10, Table S9, A.4). The all-human design's 4.98% against 5% is stated as a knife edge; break-evens in p^cc and the human miss rate, the per-objective reading and the common-mode condition are in Remark S10 and Table S13. |
| X2-N15 | Program structure: identical processes, one capacity | Partly | Section S2.9 ('Program structure') states that the path is that of a program of identical processes, that a program whose savings are concentrated and that attempts the best processes first (the order of Prop 6(d)) realizes more early, so the path understates it; that the binding-capacity result follows from scenario values; and that engineering and data capacity are not modeled and would slow the path if they bind. No concentrated-benefits variant: no source gives the distribution of savings across processes. |
| X2-N16 | Operational definitions; people-side guardrails | Partly | Box item 9: full automation is an analytical bound, not a staffing plan. No definitions box. |
| X2-N17 | No acceptance rule for acquisitions | Partly | §6 now states the rule that follows from Prop 8(a): pay less per dollar of acquired revenue than the firm's own weight on growth, the marginal value of a dollar of revenue (Prop 2). No single basis is recommended for board reporting, because the right spreading depends on how fast acquired revenue decays, which differs by deal; the one-quarter caveat is not repeated at first mention. |
| X2-N18 | Statutory compliance and labor law in the cost lines | Partly | Table S14 note: AI-compliance line excludes high-risk AI Act obligations (dates cited). WARN/works-council timelines not added. |
| X2-N19 | Common-mode scope limited to model providers | Partly | Section S2.6 states that the cross-type term does not cover shared tooling (identity provider, endpoint security agent, cloud region), that the diversity rule therefore addresses the failures of models, not the availability and tooling risk beneath them, and that the full-cost floor omits the cost of keeping a second provider ready. No new term and no scaling of the ITGC line with agent identities: no source gives their size. |
| X2-N20 | Licence, competing interests, unpublished dependence | Fixed | Footnote: 'the licenses cover the text and the software, not the ideas, which firms may apply'; declarations line added and confirmed by the author. Internal use: author decision of 2 November (19:17); the software is licensed under PolyForm Noncommercial 1.0.0 or, at the user's option, PolyForm Internal Use 1.0.0, so a company may run and modify it for its own internal operations but not distribute it or offer it as a service (footnote, Table 8, LICENSE files). Companion-paper dependence: the intro states that this paper does not depend on it; the companion paper is cited as in preparation. |
| X2-N21 | Own-vs-rent rule silent on utilization | Partly | Remark S11 now says that the comparison assumes full use, that at utilization u the capital cost per unit used is 1/u times that at full use, so the markup at which owning pays rises as utilization falls, and that staff and power limits raise it further. Qualitative only: no utilization term in the formula and no §7.2 sentence (page limit). |
| X2-N22 | Deterministic controls; AS 2201 reading presented as the standard | Partly | §8.5: Proposition 5 is our operationalization, not an accepted audit method. No deterministic-control type added. |
| X2-N23 | Table labels and readability | Declined | Main-text tables are generated by the code in the paper's notation; every symbol is defined in the table notes and in the glossary (Section S9), and Table 2 stays in the main text because the headline statistics are quoted from it. No 'what to budget' line was added to the full-cost table, now Table S14 in the supplement. |
| X2-N24 | Editorial items | Partly | Duplicate sentence deleted; companion title case fixed. 'Mature asset-light firm' and Rule-of-1000 mentions kept. |
| X2-EX9 | Response overstated EX-9; footnote lacks the ideas sentence | Fixed | Sentence added to the rights footnote (p1_preamble.tex). |

### F2. Finance and accounting referee (Fable; r2_finance_accounting.md), findings 1 to 14

| ID | Finding | Status | Note |
|---|---|---|---|
| F2-1 | Interest income left in the cash score | Fixed | Table S8 adds 'before net interest, after tax' (335 E1 firm-years that tag interest income); the existing rows are relabeled 'before interest paid'. Section S6: the P95 change net of interest income is -12.9 [-36.6, +0.2] against -10.8 on the cash basis on the same firm-years, so interest income does not explain the decline; the anchor's netted intercept on the 6 firm-years that tag it falls from 26 to 22 points, and the other 7 cannot be restated; §4 points to S6. |
| F2-2 | Direct audit and SOX cost 0.14% unsourced and low | Fixed | C3: 0.30% at $1bn from KPMG's under-$5bn budget plus the accelerated-filer average audit fee, with a low and a high end; new Table S9 row (see X2-N13). |
| F2-3 | 5% threshold: class and all-AI condition | Fixed | Class d, both thresholds reported, and the condition stated: no single-provider all-AI design passes iff its common-mode probability is at least 0.0021 per occasion at 5% (0.0004 at 1%) (§7.2, Remark S10, Table S9). |
| F2-4 | X = 2.5/5/9 placeholders in §6 | Fixed | Replaced by the sign flip at X = k_acq, between the deals' prices (macros). |
| F2-5 | Bending Spoons cash rows before SBC | Partly | Labels fixed (before/after interest; cash rows before SBC) and a note in §6 that the company's cash scores are not on the panel's basis. Its SBC share is not in our F-1 extract and was not computed. |
| F2-6 | GAAP score chained into the cash charged range | Fixed | Intro, §8.3 and summary box name the cash basis of the charged range. |
| F2-7 | Interest paid for 2023-25 should replace interest expense | Partly | Interest paid from the final prospectus and the 6-Ks is reported (Section S4.1), and §6 gives the 2025 charged range with interest paid added back, 86.6 to 113.1. The headline range stays on the interest-expense basis of Table 3 (87 to 114). |
| F2-8 | 'The convention decides the sign' is a one-year statement | Fixed | 'in the year of purchase' added. |
| F2-9 | §8.5 attestation wording; §906 | Fixed | AS 2201.03 opinion wording, filer status, 18 U.S.C. 1350 (verified at LII, new reference). |
| F2-10 | Cost of capital below the firm's marginal debt cost | Partly | §6 states that 9.34% is a sector figure below the 9.625% coupon of the notes priced 28 Oct and gives the 2025 charged range at that coupon, 86.0 to 112.8. The firm's own acquisition hurdle is not cited (not re-verified at the prospectus). |
| F2-11 | Tax and fee statements | Fixed | CAMT threshold (26 U.S.C. 59(k), verified) in §7.2 and Table S9; fees labeled as card rates applied to all revenue. |
| F2-12 | Table S6 bridge conventions | Partly | The three conventions are disclosed in Section S6 (bridge now Table S8). The count of firm-years that tag both elements was not computed, and S6 says so. |
| F2-13 | §7.2 conflates the §168(k) elect-out with psi = 0 | Partly | Separated: Remark S11 says that a firm that elects out of the allowance has psi < 1 and a higher bar, and reports the bar at the lower bound psi = 0. The bar under five-year depreciation was not computed and is stated qualitatively. |
| F2-14 | T(0) definition vs code (g >= 0) | Fixed | §5.2 now says 'firm-years with nonnegative growth'. |

### RR. Risk, audit and regulatory panel (Sonnet; r2_panel_risk_audit_regulatory.md), findings N1 to N22 and RA-3

| ID | Finding | Status | Note |
|---|---|---|---|
| RR-N1 | p^cc = 0 everywhere: knife-edge cheapest design; automation bias | Fixed | Remark S10 and Table S13 give break-evens for every design: one human over one AI fails at 5% once p^cc exceeds 0.0008 per occasion or the human misses more than 8.4% of the items the AI layers missed; the cheapest design is stated as conditional on p^cc; automation bias is named as what raises the miss rate (§8.5, Remark S10, with Vaccaro et al.). |
| RR-N2 | Authorship sentence contradicts the protocol | Fixed | Author's approved wording in §1 and A.1; Table S11 consistent. |
| RR-RA3 | 'Use in filings' paragraph missing | Fixed | Summary in §8.3; the full paragraph is Section S2.10 (moved for the page limit); Reg G 100(a),(b), Item 10(e), C&DIs 100.01/102.07/102.10(a), Release 33-10751, 15 U.S.C. 77z-2(b)(2)(D) and Palantir's presentation each verified at the primary source on 2 Nov. |
| RR-N3 | Per-objective vs firm-level threshold | Fixed | Remark S10: 5% at firm level is about 0.51% per objective across 10 objectives; the per-objective designs and costs are given at 5% and 1%. |
| RR-N4 | Audit Analytics editions stale | Partly | Later editions stay out (C5): Remark S10 notes that they exist but could not be read at the source; the rates are read as an incidence of material weaknesses found, not a tolerance. |
| RR-N5 | 1%->5% switch not in B.4 | Fixed | A.4 item 8, which now adds that in the third version neither value is central. |
| RR-N6 | 'No single-provider design passes' is an assumption of the example | Fixed | §7.2 and Remark S10 conditional on the example, with the 0.0021 condition. |
| RR-N7 | Event behind pi undefined | Fixed | Assumption 7 defines the opportunities for a material misstatement in a year; the threshold applies to the probability that at least one passes every layer over the year (§3.9, §7.2, glossary). |
| RR-N8 | ITGC retest less grounded than 'KPMG' suggests | Fixed | Remark S10 and the Table S9 row label the 10 controls and $150/h as assumptions and the other items as scenario values. |
| RR-N9 | External audit effort omitted | Fixed | §8.5 limitation with AS 2201 B28-B31 (verified at pcaobus.org); note after Assumption 7. |
| RR-N10 | Four-channel scope not mapped | Fixed | Note after Assumption 7; Table S9 scope sentence ('performs or supports a control or report that is relied on'). |
| RR-N11 | 0.14% direct cost unsourced | Fixed | C3 (see X2-N13): KPMG size budget plus the Audit Analytics accelerated-filer fee, with the S&P 500 ratio as the low end; Table S9 row. |
| RR-N12 | 'No access' in B.1 | Fixed | 'Not given the others' outputs and told not to read them; one shared file system' (A.1, Table S11). |
| RR-N13 | Model IDs, tools, transcripts | Partly | Exact IDs in A.1 and Table S11; A.1 states that every agent had the same tools (files, code, web search), that roles were set by instruction, not permissions, and what the replication package contains. Nothing further is claimed about how the session transcripts are retained. |
| RR-N14 | Author checks; no human specialist | Partly | A.1 now says what is true at this pass: the author is reading the manuscript and has commissioned independent reviews by other LLMs outside this workflow, whose findings will be logged and answered here before release (final audit B1); A.6: no human lawyer, auditor or accounting specialist reviewed the statements; CLAIMS checks test text against outputs. One todo remains until her review is complete; her reviewers' findings will be logged as AU-* items. |
| RR-N15 | Competing interests next to 'Independent researcher' | Fixed | Title footnote: 'Funding: the author received no funding for this work. Competing interests: the author declares no competing interests.' Confirmed by the author on 2 Nov; Table 8 records it. |
| RR-N16 | $350k vs $204,672 ITGC figures | Fixed | The design's ITGC-and-revalidation cost is now the sourced line of one in-scope AI application, $204,672, which already contains the revalidation at each model upgrade; the cheapest design at 5% costs $0.75m (Remark S10). |
| RR-N17 | Table S7/S9 labels; AI Act scope | Fixed | C&DI and CAMT 'not read' notes removed (now read); S11 label qualified (recitals only); AI-compliance line scoped against the AI Act. |
| RR-N18 | SR 26-2 caveat only in the supplement | Fixed | Lever 5 in §7.4. |
| RR-N19 | §8.5 filer status, §906, AS 2201 reference list | Partly | Filer status and §906 fixed; the reference's paragraph list not trimmed. |
| RR-N20 | CAMT treated as a floor | Fixed | §7.2 and Table S9. |
| RR-N21 | Palantir payroll taxes; organic growth as non-GAAP | Partly | Payroll taxes in §8.3 and the filings paragraph; Barnes Group letter not added (not re-read). |
| RR-N22 | Housekeeping (browser wording, EDGAR access, availability) | Fixed | (a) S6 and A.1 both say the data were retrieved through a browser on the author's computer. (b) S6 now states the browser script's request pattern (four concurrent requests, each followed by a 150 ms pause); we make no claim about compliance with the SEC's fair-access limits. (c) Author decision of 2 November (19:17): the code and data of all three papers are in an open GitHub repository, github.com/amurthygithub/rule-of-x, private until submission; the title footnote and S6 give the URL. No DOI deposit. |

### IO2. IO and AI economics referee (Fable; r2_io_ai.md), findings N1 to N20

| ID | Finding | Status | Note |
|---|---|---|---|
| IO2-N1 | Pass-through as a rate, not an elasticity | Fixed | B1: the industry passes the share phi of every unit-cost saving to its price and the margin is taken at the lower price; the elasticity is phi u/p (0.30 at phi = 0.5; Lemma S2). Thresholds 36.2% and 38.3% (lead-agent ruling); Table S2, placed next to Lemma S2, reconciles the readings, including the referee's (33.4/33.8), cost-of-revenue savings only (33.7/34.3) and a typical $1-5bn firm's saving (37.8/41.5). §7.2 says the saving is the top-tail anchor firm's own (unit cost 60% of price). Distinct symbols: phi is the rate, epsilon_p the elasticity (Lemma S2, Prop AI(iv), Prop 9). A sentence states that the scenario applies a medium-run marginal-cost rate to every unit cost. Ganapati and Choi sentence kept. |
| IO2-N2 | Demirer et al. misused for pass-through | Fixed | Clause removed from §7.2 and the row removed from Table S9. |
| IO2-N3 | Compute-share range: undocumented factor 0.5 | Fixed | B2: the credible upper bound is the value test (compute at most the labor it replaces, 60% of revenue); range of the threshold 28 to 78%; the high-compute case lies within the value test (§7.2, Table 4). |
| IO2-N4 | Compute path driven by unstated class-d values | Fixed | B3: the two drivers (frontier price 0.33 of the labor replaced; frontier share 60, 40 and 25%) and the 2028 threshold at a frontier share of 30% or 90% are stated (Section S2.8; §7.2 points there). |
| IO2-N5 | 2025-price headline not a date on the path; 'no measured analog' | Fixed | §7.2: the compute share 'has not been measured'; the headline 6% at 2025 prices is reached on the path only in about 2034. |
| IO2-N6 | Two labor bases | Fixed | B4: errors and misbehavior are charged on the same base as compute, the 60% of revenue in automated labor; the central threshold becomes 32.5% (lead-agent ruling). |
| IO2-N7 | Highest-error case uses human catch rates | Fixed | B4: with no review the failure term is 22.8 points and the threshold 48%; with AI review at its bound, 13.7 points and 41% (§7.2). |
| IO2-N8 | Tornado 5-30% G band unmotivated | Fixed | B12: narrowed to the interquartile range of 2023-25 growth, 5.4 to 21.4% (51 to 67 in 2036); the old band on the new basis is reported (51 to 76). Execution, not market growth, is now the largest 2036 swing (summary box, intro, §7.3). |
| IO2-N9 | Capability feasibility unstated | Fixed | §7.3 states the assumption; §8.2 qualified; §8.6 limitation with METR TH1.1 (verified). |
| IO2-N10 | Dip text-code mismatch | Fixed | B4: the transition cost is the time to payback, 1.25 years (the embedding time of Table S9), not 'two years'; dip 3.6 to 4.2 points on the central basis, 5.7 to 6.8 at two years of savings (crossing 5.6 years); fast dip 6.8 in 2028. §7.3 says that no source measures transition cost in years of savings. |
| IO2-N11 | Prop 4(d) pre-tax bound with after-tax term | Fixed | After-tax reading stated in §7.2. |
| IO2-N12 | Free-entry qualifiers; Babina; Sutton | Fixed | Homogeneous-product qualifier in abstract, intro, §3.8 intuition, §7.2, conclusion, summary; Babina clause (§2); Sutton (S2.4). |
| IO2-N13 | ICONIQ sentence draws an unsupported conclusion | Fixed | Sentence ends at the scope (now Section S2.8). |
| IO2-N14 | AI map asserts channels without sign | Fixed | Table 1: scenario labels and two negative rows; §8.6 sentence. |
| IO2-N15 | Spurious precision; METR note | Fixed | Thresholds by horizon rounded to whole points (38, 34 and 32%); the 2025-price headline keeps one decimal (32.5%), as the lead agent set it. The METR note is corrected in Table S9 and the bibliography: runs.jsonl carries generation_cost, human_cost and tokens_count (checked at the source on 2 Nov; first record 16.41 against 2,099.14). |
| IO2-N16 | Change-capacity mapping one for one | Fixed | Section S2.9 states that capacity maps one for one onto the program and that this assumes the program spans all employees' work evenly, as full automation approximately does; §7.3 points there. |
| IO2-N17 | NPV not reported | Fixed | B7: §7.3 reports the NPV (98% of a year's revenue) and the present-value ratio (3.9). |
| IO2-N18 | G* decomposition | Fixed | B7: §7.2 gives the decomposition (tax 18.0, compute 4.9, fees 2.1, accountability floor 2.5, full-cost floors 5.1 points). |
| IO2-N19 | Security share of IT spend | Waiting on code or data | Code value (FC['sec_it'] in calibrate_horizons.py) not changed in this round; Table S9 states the source's values. Effect about 0.01 points on the post-quantum line. Left to the coder. |
| IO2-N20 | 'Mature firm' and 'at fixed prices' | Partly | 'At fixed prices' added to the intro and conclusion path sentences; 'mature' kept. |
| IO2-cit | Uncited: Weyl-Fabinger, Sutton, Vaccaro, AGG 2019/2024, Gans-Goldfarb, METR TH1.1 | Fixed | All cited and verified (Crossref, NBER, METR, LSE record; Vaccaro at nature.com); existing bib entries reused where present. |

### TH2. Theory referee (Fable; r2_theory.md), findings 1 to 18

| ID | Finding | Status | Note |
|---|---|---|---|
| TH2-1 | Abstract double-counts kG | Fixed | 'the margin intercept, plus ...'. |
| TH2-2 | Cor 4(c) and its proof | Fixed | Condition at saturation stated in the corollary and the proof (S3). |
| TH2-3 | §7.3 cites Prop 7(e)(iii) with nu_D > 0; companion residue | Fixed | Pace formula read with nu_D = 0; disruption-rate sentence and 'kept for the timing of shocks' removed. |
| TH2-4 | 'The limit is set by what stays scarce' | Fixed | Abstract, conclusion, summary and §3.8 intuition: scarcity decides who captures the savings. |
| TH2-5 | 'Requires near-complete automation' | Fixed | Conclusion: a cost structure at least as lean as the full-automation structure. |
| TH2-6 | §7.2 applies the pre-tax Prop 4(d) | Fixed | After-tax extension stated in §7.2. |
| TH2-7 | Content of (H) | Fixed | Two HJB consequences and the automatic feedback condition stated after Prop 2. |
| TH2-8 | nu^R program vs calendar time | Fixed | Def 4(b) states the program-time reading and the conversion. |
| TH2-9 | 'Exceeds the screening weights when its multiple does' | Fixed | 'Well above three' in abstract, intro, §3.6, §8.1. |
| TH2-10 | 'Acts like a cut in capacity' | Fixed | Intro and §8.2: approximately like a cut in pace; partial-realization condition added. |
| TH2-11 | Duplicated sentence | Fixed | Deleted. |
| TH2-12 | delta vs delta_K; F for two objects | Partly | delta_K in Prop 9 and a note on Table 7's column; Table S1 'F' note not added. |
| TH2-13 | Two values of alpha in §7 | Fixed | §7.5 says why Table 7 uses 0.3. |
| TH2-14 | Prop 7(e) fluid limit | Fixed | Stated, with check 28m. |
| TH2-15 | Fill condition uses varpi | Fixed | Covered by the nu_D = 0 reading. |
| TH2-16 | Docstring run time | Fixed | code/verify_theory.py docstring gives the measured run time: wall clock 3 min 0 s here and 5 min 53 s on a referee's copy, so three to six minutes depending on the machine (coder). |
| TH2-17 | Marschak-Andrews (1944) | Fixed | Cited in §2 (verified at Crossref and the Econometric Society). |
| TH2-18 | Belo et al. range unverifiable | Fixed | Verified: the 6-25% range is in the article's abstract (RePEc); no change. |

### IM2. Investment management panel (Sonnet; r2_panel_investment_management.md), findings N1 to N12 and the screen item

| ID | Finding | Status | Note |
|---|---|---|---|
| IM2-N1 | T(20%) contradicts 'no detectable change' | Fixed | Sentence removed everywhere; §5.2 reports T(20%) under E1 by interval type (the basic, normal and bias-corrected intervals exclude zero, the percentile interval does not); §7.4 inference rewritten. |
| IM2-N2 | Composition decomposition unstable | Fixed | Presented as not robust: over 4 to 40 growth bins the composition term runs from -16.8 to -2.0 (GAAP) and -17.3 to -6.0 (cash), and the within-cell term changes sign; quantile shifts at P10 to P95 and first-year cohort counts are reported (§5.2). |
| IM2-N3 | 2025 recovery E1-only | Fixed | §1 and §5.2: P95 of the GAAP score in 2025 against 2023-24 is +9.2 under E1 and +2.8 without acquisition-affected firm-years. |
| IM2-N4 | Abstract slope pools a break | Fixed | Abstract gives -0.60 for 2020-25 and growth up to 40%; intro and summary give the break and the 3-of-4 qualifier. |
| IM2-N5 | Multiplicity statements | Fixed | §5.1-5.2 by procedure: the GAAP decline survives 10% under three of four procedures; the cash decline fails Holm at 10% under every interval type and Romano-Wolf; slope-vs-minus-one and gap tests flagged; family chosen after v1. CLAIMS test the wording against all types (60/60). |
| IM2-N6 | Anchor intercept has no interval | Fixed | B5: firm-cluster intervals for the intercept (netted 30.6 [24.1, 34.7]; all-S&M 42.0 [34.1, 52.4]) carried through the path: 2036 59 [54, 62] (Table 5, §7.3, abstract). |
| IM2-N7 | Headline uses the all-S&M bound | Fixed | B6 (author decision 4): the maintenance-netted basis is central (maintenance level 25.1% of revenue); all-S&M (65 in 2036) and no-S&M (55) are bounds. |
| IM2-N8 | Cash intercept carries interest income and billing timing | Fixed | D1, D2 (Section S6): for the anchor, about 9 of the 13-point cash-GAAP gap is deferred revenue, and after-tax interest income is 3.9 points where reported; removing it lowers the netted intercept of those firm-years from 26 to 22 points. The before-net-interest bridge row is in Table S8. |
| IM2-N9 | Spend ratio and the §8.1 illustration | Partly | §8.1 gives the netted ratio (0.99) result; permutation benchmark not added. |
| IM2-N10 | D-3 views not independent; bounds not bounds for cheap deals | Fixed | §4.5: sensitivity set; bounds hold only for prices of M or more. |
| IM2-N11 | SIC current; $50M screen look-ahead; not shown specific to SIC 7372 | Fixed | Supplement S6 limitations. |
| IM2-N12 | Register alpha class; '5 to 15' | Partly | '5 to 15' restated (§8.1). The register class of alpha is written by calibrate_horizons.py and was not changed in this round (left to the coder). |
| IM2-screen | 'Use the Rule of 40 to screen firms' | Fixed | Conclusion and §8.1: the paper does not test it as a screen; §8.6 adds no test of multiples or returns. |

### E2. Econometrics referee (Fable; r2_econometrics.md), findings 1 to 14

| ID | Finding | Status | Note |
|---|---|---|---|
| E2-1 | 'No detectable change' fails D-3 | Fixed | Removed from §5.10(v), §1 and §9; T(0) after SBC reported as falling in two of four views. |
| E2-2 | Familywise standing of the P95 declines | Fixed | Text by procedure; abstract asymmetric (GAAP 'significant at 10% after familywise correction under most procedures', cash 'not significant'); CLAIMS test both statements over all interval types and Romano-Wolf. |
| E2-3 | In-draw grid rule (10 vs 30) | Fixed | §5.1 discloses the in-draw rule, the share of undefined E2 draws under the sample's 30-firm-year rule and the defined-draw interval (GAAP [-0.505, -0.080]). |
| E2-4 | GAAP steepening stated as fact | Fixed | 3-of-4 qualifier in §5.3, §5.10(i), intro and conclusion. |
| E2-5 | Anchor conclusion outside the families; D-2 disclosure | Fixed | §5.8 gives the anchor's Holm-adjusted p-values within family B (normal 0.006, percentile 0.084, basic 0.028); A.4 item 4 discloses the v1 Psi slopes. |
| E2-6 | CLAIMS test vs sentence procedure sets | Fixed | Coder (A2): CLAIMS test the sentence's procedure set (60/60). |
| E2-7 | '3.8 expected' should be 3.6 | Fixed | Macro ContrExpected is now 3.6 (10% of the 36 estimable contrasts). |
| E2-8 | D-2 knowledge disclosure | Fixed | A.4 item 4. |
| E2-9 | Lead regressions in two of four views | Fixed | §5.3 reports the within-firm lead regressions under E2 and both imputation bounds. |
| E2-10 | §8.1 reuses 3.02 as alpha(X-k) | Fixed | §8.1 restated. |
| E2-11 | 'The 2016-19 gap behaves the same way' | Fixed | The sentence no longer appears; §5.7 reports the gap with its intervals and robustness. |
| E2-12 | R3-18: E2 pairs organic growth with consolidated margins | Fixed | Sentence in §4.5. |
| E2-13 | Romano-Wolf description | Fixed | 'Step-down max-t with statistics scaled by their bootstrap standard errors' (§5.1). |
| E2-14 | DFL quantile definition | Fixed | The code now uses the linear (type-7) weighted quantile (coder); Section S6 ('Inference') states the definition. |

### IB2. Investors and bankers panel (Sonnet; r2_panel_investors_bankers.md), findings N1 to N25

| ID | Finding | Status | Note |
|---|---|---|---|
| IB2-N1 | 'Price line' reads as a valuation line | Fixed | Defined at first use (intro); abstract: 'of equal score, not equal value'. |
| IB2-N2 | Score-to-multiple bridge | Fixed | Analytical iso-score table (Table S3, in Section S2.2 with Lemma 5): four firms scoring 40 are worth 12.1, 11.7, 8.3 and 5.2 times revenue; the intro quotes the range and says that no mapping is estimated. |
| IB2-N3 | Decision weight at one discount rate; one-sided sentence | Fixed | Section S2.2 gives the small-share multiple of the worked example at 9.34, 10, 12, 15, 22 and 31% (14.6, 10.0, 5.8, 3.7, 2.1 and 1.35); §8.1 quotes 10.0 at 10% falling to 2.1 at 22% and 1.35 at 31%, within or below the screening range. |
| IB2-N4 | Withdrawn weight re-enters in four places | Fixed | §8.1, conclusion and '5 to 15' fixed; Table 7 regenerated without the proxy weight and on the netted basis (decision 7), and the withdrawn macros (lpXhat, lpXdagMin/Max, lpScreenBelowAll) are not quoted anywhere in the text. |
| IB2-N5 | Abstract decline: basis, familywise, recovery | Partly | Basis (GAAP; free cash flow after SBC) and familywise status in the abstract and summary box; FCF-before-SBC fall not added; the recovery is in §1 and the summary, not the abstract (character limit). |
| IB2-N6 | Bending Spoons stale | Fixed | Every fact from the 6-K texts (data/v3_inputs/raw); bib note corrected; run-rate interest 20.3% of second-quarter revenue at an annual rate (27.9% if the unpriced term loans carry the notes' coupon) in §6, with the dated events in Section S4.1; charged ranges at interest paid and at the marginal coupon in §6. |
| IB2-N7 | Owner types; sponsor sentence | Partly | Scope stated (no PE or permanent-capital analysis); §7.3 states that a variant with shorter sponsor latency has no effect while change capacity binds and that no owner-led execution case is computed, and points to the companion paper for owners' dip budgets and decision speeds. No owner-type table. |
| IB2-N8 | Success re-grounding; 23%->41% bridge | Fixed | B9: relabeled share of attempts that create value; Shapley bridge from the first version's inputs (21.9%) to 40.7% (Section S2.9). |
| IB2-N9 | Bessemer 2-9 range in the main text | Partly | §8.1 now says Bessemer offers two to three as a conservative base within a reported range of about 2 to 9 (checked at bvp.com on 2 Nov; bib note updated). Definition 1 unchanged, and Meritech's regression is not cited (not verified at the source). |
| IB2-N10 | Level anchors (SEG, Meritech); CAC proxy | Partly | The decision weight is now reported by discount rate (IB2-N3), which bounds its level. The SEG and Meritech multiples were not added because they were not verified at the source in this round, and the CAC proxy stays in Table S9 because it rests on a survey ratio and an assumed alpha. |
| IB2-N11 | 'A fifth of a point' is the flattest specification | Fixed | Abstract and intro give the 2020-25 slope. |
| IB2-N12 | 'Because' and 'no detectable change' | Fixed | Removed. |
| IB2-N13 | Basis comparability | Partly | §8.3 and the conclusion: state the basis; not comparable with quoted scores. No size split. |
| IB2-N14 | Sample framing; anchor firms | Fixed | §4.1 framing; Table S10 names the anchor firm-years; Section S6 decomposes the anchor's cash-GAAP gap (deferred revenue about 9 of 13 points). |
| IB2-N15 | 'Exceptional' and 'not a forecast' | Fixed | Text: 'top-tail firm (95th percentile)'; abstract 'not a forecast'; the caption of Table 5 now says 'a top-tail asset-light firm'. |
| IB2-N16 | Miro price; price rising with volume | Partly | Miro EV and ARR stated (Section S4.1, from the 6-K); 'its price may rise with the volume bought' after Prop 8. Not added as a fourth deal price. |
| IB2-N17 | How-not-to-use box; ceiling not a valuation cap | Fixed | Box at the end of §1, item 1. |
| IB2-N18 | No test of prices or returns | Fixed | §8.6. |
| IB2-N19 | Stewardship: competing interests, licence, AI panels | Fixed | 'AI review panels' in §4.2; ideas sentence; declarations confirmed by the author; internal use permitted for the software under PolyForm Internal Use 1.0.0 at the user's option (author decision, 2 November 19:17). |
| IB2-N20 | After-interest score measures capital structure | Fixed | Prop 8(c) is followed by the statement that a score after interest measures capital structure as well as operations and belongs beside the score before interest and a measure of interest coverage. The panel's buyout arithmetic is not reproduced in the text. |
| IB2-N21 | Charging rate below marginal coupon | Fixed | §6 gives the 2025 charged range at the notes' 9.625% coupon, 86.0 to 112.8. |
| IB2-N22 | Organic score ignores amortization | Declined | A cash organic score needs a second-quarter cash flow derived from a restated first quarter, which we did not compute; §6 lists amortization, transaction and reorganization expense as the channels by which acquisitions reach the GAAP margin and says which the adjusted margin adds back. |
| IB2-N23 | Return range: text vs table | Fixed | §6 says the text range spans tax rates of zero and the Italian rate. |
| IB2-N24 | Duplicated sentence | Fixed | Deleted. |
| IB2-N25 | References list unused material | Fixed | 6-K note lists the reports used and the text now uses them. |

### FA. Final audit of the third version (claude-fable-5-1; notes/reviews/paper1_v3/final_audit.md): blocker B1, majors M1-M4, minors m1-m19

| ID | Finding | Status | Note |
|---|---|---|---|
| FA-B1 | A.1 asserts a review that has not happened; red todo | Partly | A.1 rewritten to what is true now: the author is reading the manuscript and has commissioned independent LLM reviews, whose findings will be logged and answered here before release. The todo in A.6 stays until her review is complete. |
| FA-M1 | Decision 7 missing from the protocol appendix | Fixed | Table 8 row 'Basis of the levers (2 November, 12:35)'; A.4 item 'Basis of selling and marketing' records that both basis choices (10:15 and 12:35) were made after the results on each basis were known and that the second reversed the second version's lever finding; A.2 counts the six rows of Table 8 dated 2 November. |
| FA-M2 | Table S12 stops at the first-version review | Fixed | New group 'Review of the second version' with the errors and who caught each: IO referee (pass-through at the old revenue, the misread inference-price paper, the 0.5 factor, the 30% error base, 'two years', human catch rates in the high-error case); econometrics referee and investment management panel (Holm overstatement, 'no detectable change'); finance referee, risk panel and executives panel (unsourced 0.14%, the undisclosed threshold switch); risk panel (authorship sentence); investors and bankers panel (6-K bib note). |
| FA-M3 | Pass-through baseline and symbol | Fixed | §7.2 says the saving is the top-tail anchor firm's own (60% of price) and gives a typical firm's thresholds (37.8/41.5; Table S2 row by the coder); phi is the rate and epsilon_p the elasticity in Lemma S2, its proof, Prop AI(iv), the ceiling proof and Prop 9; a clause after Lemma S2(a) extends it to costs beyond cost of revenue. No generated table prints the symbol for the elasticity, so no table change was needed. |
| FA-M4 | 'All twelve reports recommended major revision' | Fixed | A.2 and S7.3: the eight referee reports recommended major revision; the practitioner panels asked for changes before release (S7.3 quotes the investors and bankers and the risk panels). |
| FA-m1 | Abstract slope windows | Fixed | Abstract: '-0.60 in 2020-25 at growth up to 40%'. |
| FA-m2 | Basis of the cash decline | Fixed | Abstract and summary box: 'on free cash flow after stock-based compensation'. |
| FA-m3 | 'In every sample variant' read as magnitudes | Fixed | Intro: 'fell in every sample variant, by 11.9 ... and 12.7 ... in the baseline'. |
| FA-m4 | Conclusion steepening without qualifier | Fixed | Conclusion adds 'with an interval that excludes zero in three of four views'. |
| FA-m5 | Floor 0.37% stated without the threshold | Fixed | Summary box and §7.2: 0.37 to 0.38% at the two thresholds. |
| FA-m6 | Table 2 type size | Fixed | Table 2 is two float pages at \footnotesize without \resizebox, both numbered Table 2; seven columns (Statistic, Basis, E1, E2, M = 4, M = 8, D-3), basis 'cash' defined in the notes. The E1 - E2 and exclusion-only columns are Table S8. Table S4 is unscaled and Table S6 is split into S6 and S7 (coder). A one-page version at \scriptsize did not fit (float 283 pt too tall). The main paper is 82 pages as a result. |
| FA-m7 | Two stale response entries | Fixed | IB2-N15 (now Fixed) and X2-N5 (ten items) corrected. |
| FA-m8 | Competing-interests record in S7.3 superseded | Fixed | S7.3: 'a decision she reversed on 2 November (Table 8)'. |
| FA-m9 | Decision count in A.2 | Fixed | See FA-M1. |
| FA-m10 | Usage-limit stop of the round-2 reviews | Fixed | Appendix A intro: six of the eight round-2 reviews stopped on 29 October at the account's usage limit and resumed from saved state on 2 November. |
| FA-m11 | Engine compute-share range | Fixed | engine defaults.yaml c_c_full_automation note: [0.01, 0.30] is the envelope of the scenario-path ranges used for the tornado, not Paper 1's credible range of 1-60% at 2025 prices (engine tests pass). |
| FA-m12 | Central audit fee is low-side | Fixed | §7.2 and Remark S10: the accelerated-filer fee is the low-side choice, because a public firm with $1bn of revenue is normally a large accelerated filer. |
| FA-m13 | Netted anchor surplus not in Table 2 | Fixed | Table 2 row 'Anchor: median Pi, maintenance-netted (central)' (coder; estimate_v3 statistics anchor_p95_Pi_net_*). §5.8 now reports it with macros \AncPiNet*: +12.4 [+0.3, +25.7] under E1 and +12.2 [+0.5, +24.7] under E2, above zero in all four views but with a lower end near zero under E1 and no multiplicity adjustment; the conclusion remains the statement in which no selling spend buys growth. CLAIMS entry added. |
| FA-m14 | Interest-income sentence in §4.6 unqualified | Fixed | §4.6: 'leaves a decline of similar size, although on the thin subsample that reports interest income both intervals include zero'. |
| FA-m15 | G* decomposition parts round to 5.2 | Fixed | \GdecMnt 0.50, \GdecSec 1.28, \GdecErr 3.17, \GdecAnc 0.16 print to two decimals, with \GdecFullTwo 5.11 (coder). |
| FA-m16 | Medium-run marginal-cost rate applied to all costs | Fixed | §7.2 sentence: the scenario applies that short- to medium-run rate, measured for marginal-cost shocks, to every unit cost, which Prop 4(d) supports only as a long-run argument under free entry. |
| FA-m17 | 2 Nov retrieval missing from S6 and Table S11 | Fixed | S6 gives the date and scope (144 frames, 21 6-K documents, prospectus and interim cash-flow pages; README_retrieval sections 3-4); Table S11's lead-agent row names both retrievals. |
| FA-m18 | Competing interests | Fixed | The author confirmed on 2 November (10:45) that the research is independent; the title footnote states no funding and no competing interests. At her instruction (14:50) one registrant, not named, was removed from all data, code and replication files (notes/r2_exclusion.md); it is outside the estimation sample and no reported figure changed. Section 4.1, Appendix S6 and Table 8 say so. |
| FA-m19 | METR 0.4 to 1.1% | Fixed | Section S2.8: '0.4 to 1.1% of it, rounded to 1%'. |

## Round 3: outside reviews

The three outside reviews the author commissioned on the third version (DeepSeek V4 Pro, GPT-6.2 Sol and GLM 5.3, run outside this workflow) and the joint-parameter stress test are answered in `notes/reviews/paper1_v3/response_to_outside_reviews.md`: one row per finding of the three issue logs, with its status and where and how it was handled, a counts table, and rows ST-1 to ST-6 for the six claims the stress test shows to be conditional. The red \todo marker of Appendix A that this document mentions above was removed in that round (X-2, GPT-11, GLM-F4); the AU-* items it anticipated are the DS-*, GPT-* and GLM-* rows there.
