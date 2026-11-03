# Pressure-test panel: risk, audit and regulatory (Paper 1, v1)

Paper: "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation" (frozen snapshot `notes/reviews/paper1_v1/`, PDF and text of 29 October 2026).
Context read: `part2/theory_accounting.tex`, `notes/accounting_notes.md`, `notes/case_bending_spoons_f1_extract.md`, and, for the protocol check only, `notes/agent_log.md`, `notes/research_errors_log.md` and `code/retrieval_browser.js`.
Roles: chief audit executive (CAE); external audit engagement partner; SEC Corporation Finance reviewer; competition-authority economist; AI governance and model-risk lead.

**Disclosure for Appendix E.3.** This panel is one AI agent (Claude, model identifier claude-opus-5-5, the same model as the authoring agents) playing five roles. No human practitioner took part. Its agreement with other agents is weak evidence (Appendix E.7 says so). It verified statements against primary sources where it could reach them and labels what it could not reach.

---

## Verdict

**The citations and the numbers hold up; the framing of the accountability floor, and the absence of any securities-law, antitrust or AI-governance caveat on metrics the paper recommends, do not. Fix before release; the changes are textual, not a re-estimation.**

1. **Numbers.** Every load-bearing figure checked reproduces from the primary filing: Palantir's Q2 2026 score (93% + 62% = 155; 140 on GAAP), and every Bending Spoons figure in Table 9 (`tab:acquired-score`) and Section 6. Statute and rule citations on SOX 404, Item 308, §174A and ASC 350-40 are correct in substance.
2. **The accountability floor is stated as an expected-loss minimum, which is not how ICFR works.** Proposition 10 (`prop:amin`) and Remark 10 (`rem:amin-values`) choose the cheapest control design. ICFR is a pass-fail standard: management may not call ICFR effective if a material weakness exists (Item 308(a)(3)). In the paper's own example, the all-AI design lets through 0.12 material misstatements a year (an 11% annual chance) and the all-human design 0.05 (5%). Both fail any reasonable reading of "remote", so the comparison the paper draws between them is a comparison of two non-compliant designs.
3. **The independence assumption overstates the value of diversity.** Assumption 7 (`ass:layers`) treats human and AI failures as independent. In practice four things break that:
   - management override and bad shared source data defeat human and AI layers together;
   - a failed IT general control defeats both;
   - people who review AI output tend to accept it when it is wrong (automation bias);
   - models from different providers are often wrong on the same items: they agree on 60% of their errors on one benchmark (Kim et al., ICML 2025).
4. **Metrics without a filing caveat.** Section 8.3 and Section 9 tell practitioners how to compute a score. The paper never says that such a score, used in filings or earnings releases, would be a non-GAAP measure or a key metric, with the obligations that follow. It attributes a "reported" Rule-of-40 score of about 160 to a company that reports none.
5. **Out-of-date or wrong statements in the regulatory domains.**
   - Assumption 1 says the share cap reflects "antitrust limits". Antitrust does not cap share won organically.
   - "Model-risk validation" has had no supervisory template for generative or agentic AI since 17 April 2026, when SR 11-7 was superseded and the replacement put those models out of scope.
   - The EU AI Act's high-risk dates have moved (Regulation (EU) 2026/1744).
   - The paper treats the 15% corporate AMT as the floor of the cash tax rate. The AMT is not such a floor.
6. **Protocol appendix: unusually thorough, but not yet accurate on four points.**
   - The "referee" and "practitioner" panels are AI agents, and the appendix must say so.
   - Agents shared one file system, so "no access to the others' outputs" is not literally true.
   - The project timeline and what the author personally verified are not disclosed.
   - There is no competing-interests statement, and E.3 is still a placeholder.

---

## Primary sources checked

| Source | What was checked | Result |
|---|---|---|
| Palantir Q2 2026 press release, Ex. 99.1 to Form 8-K (3 Aug 2026), sec.gov | Score, definition, margins, labeling | 155 = 93% growth + 62% adjusted operating margin; GAAP margin 47% ($912.0M / $1,935.5M). Adjusted operating income excludes SBC **and related employer payroll taxes** ($265.2M + $17.3M). "Rule of 40" is under "Additional Definitions", not labeled non-GAAP, not reconciled as a whole; its margin input is reconciled. |
| Bending Spoons Q2 2026 results, 6-K Ex. 99.1 (13 Aug 2026), sec.gov | Growth, organic growth, margins, Rule of 40 | Revenue +126%; organic growth 3%, defined with "estimated pre-acquisition revenue"; not labeled non-GAAP or reconciled; operating margin 34%; adjusted margin 54%. **No Rule-of-40 score is reported.** |
| Bending Spoons 424B4 (1 Jul 2026), sec.gov | Basis, material weaknesses, FPI status | U.S. GAAP; foreign private issuer; summary risk factor: "We have identified material weaknesses in our internal control over financial reporting". The full risk factor was beyond the fetched text; the case extract records that no Section 404 evaluation had been performed and that the Q1 2026 cash flows were restated. |
| SEC Release 33-10751 (30 Jan 2020, effective 25 Feb 2020) | KPI guidance | A metric in MD&A should come with: a clear definition and calculation; why it is useful; how management uses it; any material estimates or assumptions. If the method changes, disclose the change and consider recasting prior periods. Disclosure controls apply to metrics. Item 10(e)(4) excludes operating and statistical measures from non-GAAP. |
| SEC non-GAAP C&DIs (last updated 13 Dec 2022), sec.gov/corpfin | 100.01, 100.04, 100.05, 100.06, 102.07, 102.10(a) to (c) | Verified. 102.10(a) treats a ratio with a non-GAAP numerator or denominator, shown without the GAAP-based ratio at equal or greater prominence, as undue prominence. 102.07: free cash flow is a liquidity measure, must not imply residual discretionary cash, and must not be shown per share. No update since 2022 found. |
| SEC staff comment letter to Barnes Group (7 Oct 2024), sec.gov CORRESP | Organic growth | "disclosure of organic sales or sales growth is a non-GAAP financial measure"; reconciliation under Item 10(e) requested. |
| 17 CFR 229.308 (LII) | Item 308(a)(3), (b), (c), Instruction 1 | Verified: material weakness bars an "effective" conclusion; attestation only for accelerated and large accelerated filers that are not EGCs; quarterly change disclosure; newly public transition. |
| PCAOB AS 2201 (pcaobus.org) | .03, .A7, .B17, .B28 to .B31, .47 | Verified. .03: the opinion is on the effectiveness of ICFR. .A7 with the ASC 450 meaning of "reasonable possibility". .B28: benchmarking rests on "entirely automated application controls" not subject to human breakdown. Amendments effective 15 Dec 2025 do not touch these paragraphs. |
| PCAOB environment (WilmerHale, 8 Apr 2026; CalCPA, 12 Aug 2026; PCAOB 2024 GenAI Spotlight) | AI guidance | No AI-specific auditing standard. The technology-assisted analysis amendments (AS 1105, AS 2301) apply to audits of fiscal years beginning on or after 15 Dec 2025. The 2026 request for comment on strategic priorities makes AI in financial reporting a central focus. |
| COSO, *Achieving Effective Internal Control Over Generative AI* (Journal of Accountancy, 26 Feb 2026) | Existence, scope | Verified. The companion paper's page-level citations were not rechecked. |
| FASB ASU 2025-06 (RSM summary) | Effective date, threshold | Issued September 2025. Effective for annual periods beginning after 15 Dec 2027, early adoption allowed. Removes project stages; capitalization waits until completion is probable and significant development uncertainty is resolved. |
| 26 U.S.C. §174A (LII) | (a), (c), (d)(3), effective date | Verified: domestic R&E is deducted when paid or incurred, with an election to amortize over at least 60 months; software development is R&E; applies to taxable years beginning after 31 Dec 2024. |
| CAMT (EY alert) | Applicability | Applies only to corporations with three-year average adjusted financial statement income (AFSI) above $1 billion. AFSI is reduced by §168 tax depreciation; no matching relief for R&E expensing was found. |
| 2023 Merger Guidelines (FTC PDF); WilmerHale, 28 Feb 2025 | Guidelines 1 and 8; status | HHI above 1,800 with a change above 100, or a share above 30% with a change above 100, is presumptively harmful. A pattern or series of acquisitions is assessed for its cumulative effect. The agencies said in February 2025 that the guidelines remain in effect; no replacement found by October 2026. |
| FTC v. Welsh Carson (USAP) consent (Duane Morris, 17 Jan 2025) | Roll-up enforcement | Roll-up of practices alleged to let prices rise to the highest rate any practice had obtained. Order requires prior approval of anesthesia deals and 30 days' notice for hospital-based practices. |
| HSR form (Katten via JD Supra, 24 Mar 2026) | Status | The new form was vacated by the Eastern District of Texas on 12 Feb 2026, and the Fifth Circuit denied a stay on 19 Mar 2026. The FTC reverted to the prior form. |
| AGCM, below-threshold mergers page | Italy call-in power | Under Art. 16(1-bis), Law 287/1990, the authority can call in a deal within six months of completion where only one turnover threshold is met or worldwide turnover exceeds €5 billion, and there are real risks to competition. Notice amended 4 Aug 2026. |
| Federal Reserve SR 26-2; OCC Bulletin 2026-13 (17 Apr 2026) | Model risk guidance | Supersede SR 11-7 and OCC 2011-12. Most relevant to banks above $30 billion of assets. OCC: generative and agentic AI models "are not within the scope of this guidance". |
| EU AI Act Digital Omnibus (Hunton, 28 Jul 2026; SecurePrivacy, 10 Jul 2026) | Dates | Regulation (EU) 2026/1744, in force 27 Jul 2026. Annex III high-risk obligations from 2 Dec 2027; Annex I from 2 Aug 2028. Not checked against EUR-Lex. |
| NIST AI RMF page | Status | AI RMF 1.0 (26 Jan 2023) "is being revised as part of the White House AI Action Plan"; Generative AI Profile AI 600-1 (26 Jul 2024). |
| Kim, Garg, Peng, Garg, "Correlated Errors in Large Language Models", ICML 2025, PMLR 267:30038–30066 | Error correlation | More than 350 LLMs; models agree on 60% of their errors on one leaderboard; larger, more accurate models have highly correlated errors even across architectures and providers. |
| 15 U.S.C. §77z-2(b)(2)(D) (LII) | Safe harbor | The PSLRA safe harbor does not apply to forward-looking statements "made in connection with an initial public offering". |
| 17 CFR 240.10D-1 (LII) | Clawback | "Financial reporting measures" include measures "derived wholly or in part" from GAAP measures, plus stock price and TSR. "Little r" restatements are triggers. |
| arXiv generative-AI policy; COPE position on authorship and AI tools | Protocol | arXiv: report significant use; AI not an author; authors fully responsible. COPE: disclose in Methods which tool was used and how. |
| SEC "Accessing EDGAR data" | Fair access | At most 10 requests a second; declare a user agent; no automated crawling outside the policy. |
| NIST IR 8547 (csrc) | Status | Final, 27 Oct 2026. The 2030 and 2035 dates were not re-read in the final text. |

---

## 1. Chief audit executive (SOX 404, ICFR)

### 1.1 Accuracy

| # | Location | Statement | Verdict | Fix |
|---|---|---|---|---|
| C1 | §8.5 | Management must assess ICFR every year | Accurate, subject to the newly-public transition, which the paper states | None |
| C2 | §8.5 | "the auditor of an accelerated filer must attest to that assessment in an integrated audit performed under PCAOB AS 2201" | Accurate in substance, imprecise on two points: the requirement covers accelerated and large accelerated filers that are not EGCs (Item 308(b)), and under AS 2201.03 the opinion is on the effectiveness of ICFR, not on management's assessment | "the auditor of an accelerated or large accelerated filer that is not an emerging growth company must express an opinion on the effectiveness of internal control over financial reporting in an integrated audit under AS 2201 (.03)" |
| C3 | §8.5 | "Sections 302 and 906 make the principal executive and financial officers personally responsible..." | Accurate; the citation is incomplete, since United States Congress (2026a) is 15 U.S.C. §7241 (§302) only | Add 18 U.S.C. §1350 (§906, criminal certification) |
| C4 | §7.2, Remark 10 (`rem:amin-values`) | "Direct audit and Section 404 costs add about 0.14% at this size" | Weakly grounded. The register builds it from the S&P 500 average audit fee ($343 per $1 million of revenue, FY2022) plus a $1.04 million median SOX cost. Fees per dollar of revenue are far higher below the S&P 500 (Audit Analytics, earlier data: accelerated filers about $479, smaller reporting companies above $5,000 per $1 million; KPMG 2025 SOX Survey: about $1.5 million of SOX program cost for companies under $5 billion of revenue). At $1 billion, 0.14% is probably low | Recalibrate with size-matched fee data, or label 0.14% "illustrative; S&P 500 fee ratio, likely understated at $1 billion" |
| C5 | Assumption 7 (`ass:layers`), Prop. 10(a) | "failures of different types are independent"; "only diversity of types addresses common-mode ones" | Correct inside the model; not a defensible description of ICFR. Cross-type common causes: management override (overrides AI configuration as easily as human review); defective source data or information produced by the entity (IPE) seen by every layer; ITGC failure (both automated controls and reviews of system reports depend on it); automation bias in human review of AI output (Parasuraman and Manzey, *Human Factors* 52(3), 2010) | State the diversity result as an upper bound; see change 2 |
| C6 | Prop. 10(b), eq. (28) (`eq:amin`) | The floor is "minimized over designs" | Correct as a cost minimum; misleading as a control standard. Per opportunity, each design lets a misstatement through with probability P_mm: (a) all-AI, three layers: 0.00501; (b) all-human, three layers: 0.00212; (c) one human over two AI: 0.00028. Times 24 opportunities, that gives 0.120 (11.4% annual chance), 0.051 (5.0%) and 0.0067 (0.7%) undetected material misstatements a year. Designs (a) and (b) fail any plausible "remote" reading of AS 2201.A7. The human common-mode term alone (24 × 0.002 = 0.048 a year) puts *every* all-human design there, which signals that N_mm and the human p^cm are miscalibrated against an effective-ICFR baseline | Impose the standard as a constraint and recalibrate; see change 1 |
| C7 | Remark 10 | "a misstatement costing L_mm = $10 million" | Unsupported framing. The cost of an undetected material misstatement is not its amount but its consequences: restatement and remediation; higher audit fees (Hogan and Wilkins, 2008: +35%, already cited in the companion paper); cost of equity; litigation and enforcement; Rule 10D-1 clawback work | Rename L_mm "consequence cost of an undetected material misstatement" and source it |
| C8 | Assumption 7, §8.5 | ITGCs per in-scope AI application: access, change management with a retest at each model upgrade, operations, interfaces | Accurate and consistent with COSO's February 2026 GenAI guidance. Gap: the model charges for ITGCs, yet they do not lower p^cm, although version pinning, testing before release and rollback exist precisely to control the model-update regression that p^cm prices | Make p^cm a decreasing function of ITGC strength, or say the floor is conservative on this point |
| C9 | Definition 3 (`def:fullcost`), §8.5 | Contents of a_min | Reasonable; omits disclosure controls and procedures (Rule 13a-15) over the KPIs and metrics an AI system may now compute (Release 33-10751), and Item 308(c) disclosure when key controls move to AI | Add both to the list |
| C10 | Remark 3 (`rem:acquired-bounds`) | "On the GAAP basis it touches the score only through the amortization of acquired finite-lived intangibles, since goodwill is not amortized" | **Inaccurate.** Acquisition-related costs are expensed (ASC 805-10-25-23). Impairments, remeasurement of contingent consideration, post-combination compensation and restructuring also reach operating income. The paper's own figures for 2025 show transaction expense of 6.5% and reorganization expense of 6.0% of revenue | See change 6 |
| C11 | Table 9 (`tab:acquired-score`) | Row "Amortization of acquired intangibles" | Label error: the 424B4 line is "Amortization and impairment of acquired intangibles" (the text says "amortization and impairment") | Relabel |
| C12 | §6 | Bending Spoons case | Omission: the filings disclose material weaknesses in ICFR and a restatement of the Q1 2026 cash flows; no Section 404 evaluation has been performed | Add a reliability caveat; see change 6 |

### 1.2 Misuse and compliance risk if a company cited the paper

- **Cutting controls on the paper's authority.** "The best design is one human layer over two AI layers" (Remark 10) could be cited to remove a human review layer or to shrink control testing. If the design does not give reasonable assurance, the result is a material weakness, an adverse 404(b) opinion and Item 308 disclosure. Officers who sign 302 certifications on the strength of a cost model, not tested controls, carry personal exposure.
- **Budgeting the floor at 0.24% of revenue.** The figure combines an illustrative design with a probably understated audit-fee ratio (C4). An audit committee using it as a benchmark for SOX and audit spend would under-fund.
- **Rule of 40 in pay plans.** A Rule-of-40 or "charged score" metric in a performance-share plan is a "financial reporting measure" under Rule 10D-1, since it is derived in part from GAAP measures. A restatement, including a "little r" one, then requires recomputing and clawing back the excess award. Scenario-dependent variants (annuity life, compute share) make the recomputation contestable.
- **Treating AI-performed controls as automated controls.** Assuming they qualify for automated-control testing (benchmarking) understates audit effort and fees; see Section 2.

### 1.3 Missing controls and caveats

1. State that Proposition 10 is a cost comparison under a compliance constraint, not a design standard; see change 1.
2. Cross-type common causes (C5) and dependence of p^cm on ITGCs (C8).
3. Serial acquirers' ICFR scope lags their revenue. SEC staff allow management to exclude an acquired business from its assessment for up to a year (staff FAQ, cited in the companion), and a newly public company's first annual report has no assessment (Item 308, Instruction 1). For a firm buying a business every quarter, a material share of revenue may never be inside a completed assessment when the score is computed. This belongs in Section 6.
4. Item 308(c): moving a key control to an AI application, or a forced model upgrade that changes a key control, can be a change that materially affects ICFR in the quarter it occurs.

### 1.4 Protocol appendix (CAE view)

Table 17 records the author's ICFR scoping principle. That is an appropriate decision for the author to own. The appendix should also say which ICFR statements a human with SOX experience reviewed line by line. The accounting agent's findings are AI findings; the appendix currently reads as though the subject-matter check were independent.

---

## 2. External audit engagement partner (PCAOB AS 2201)

### 2.1 Accuracy

| # | Location | Statement | Verdict | Fix |
|---|---|---|---|---|
| A1 | Reference "Public Company Accounting Oversight Board (2026)" | Lists paragraphs .03, .16 to .19, .36, .44 to .47, .49, .52, .53, .55, .69, .A7, .A11, .B17 to .B22, .B28 to .B31 | Paper 1's text relies on none of these except the existence of the integrated audit; the list belongs to the companion paper | Either carry the companion's Remark on reliance on AI-performed controls into Paper 1 (preferred; see change 3) or trim the list to what Paper 1 uses |
| A2 | Assumption 7, Remark 10 | AI layer cost of $50,000 a year | Probably understated for audit purposes. AS 2201.B28 to .B31 allow benchmarking only for "entirely automated application controls" with effective ITGCs and an unchanged program. A model that its vendor updates, or whose outputs vary from run to run, fails those factors (the companion's judgment, which I share). It is then tested every year by sampling or reperformance, like a manual control | State this, and fold annual testing into c_j or C^itgc_g |
| A3 | Assumption 7 | Provider assurance not discussed | Missing. AS 2201.B17 points to AS 2601 on service organizations. The assurance an auditor needs is a SOC 1 Type 2 report (controls relevant to user entities' ICFR). AI model providers' published reports are commonly SOC 2 (Trust Services Criteria), and hosting is often carved out to a subservice organization. Without a usable SOC 1, the auditor tests complementary user-entity controls and the output directly, at a cost | Add to the cost line |
| A4 | Assumption 7 | Outputs of AI layers used by human reviewers | Missing: they are information produced by the entity (AS 1105.10), whose accuracy and completeness must be tested | One sentence |
| A5 | §8.5 | No statement of the auditing-standards environment | Missing. As of October 2026: no PCAOB standard or staff guidance on AI-performed controls; 2024 GenAI Spotlight; technology-assisted analysis amendments effective for fiscal years beginning on or after 15 Dec 2025 (auditors' own tools); a 2026 request for comment on strategic priorities centred on AI in financial reporting. The ground may shift within the paper's 2028 to 2036 horizon | Add "as of October 2026" with these facts |
| A6 | §4, Appendix D | XBRL companyfacts as the data source | Accurate, but XBRL tags are not covered by the audit opinion, so tagging errors are measurement error. The paper's spot checks against named filings are the right control | Add one sentence to "Known limitations" |
| A7 | §6 | Company adjusted margin "lies further from R^A_X than the GAAP score" | Accurate, and the right audit-quality point: for a serial acquirer, transaction and reorganization costs recur | Link it to C&DI 100.01 (Section 3) |

### 2.2 Misuse and compliance risk

- **Management's assessment.** A company that cites Proposition 10 to justify its control design should expect the auditor to set the model aside. Auditors judge how severe a deficiency is by the likelihood and size of a possible misstatement (AS 2201.62 to .70) and by the evidence that the controls work, not by expected cost.
- **Auditor independence.** If the AI application that performs a control is designed or put in place by the audit firm, Rule 2-01(c)(4)(ii) of Regulation S-X (designing or implementing financial information systems) is engaged. The paper's lever 5 ("small accountability floor") invites vendor-led control automation; a short caveat avoids an independence trap.
- **Reading "the floor falls with scale" as "audit effort falls with automation".** Under A2 and A3, AI-performed controls can raise audit effort per control.

### 2.3 Missing caveats

A2 to A5 above. Also: auditors test key controls against risks and assertions, not "layers". The layer abstraction is fine for economics, but say once that it is a reduced form.

### 2.4 Protocol appendix (partner view)

E.6 says "a referee who re-derived the results independently". That referee is an AI agent, and the sentence should say so. An auditor would also ask how the 168 symbolic checks were themselves reviewed: who read `verify_theory.py`? State whether any human read it.

---

## 3. SEC Corporation Finance reviewer (non-GAAP, MD&A, metrics)

### 3.1 Accuracy

| # | Location | Statement | Verdict | Fix |
|---|---|---|---|---|
| S1 | Intro; §5.10; §8.3 | Palantir's Q2 2026 score 155 on the adjusted margin of 62%, 140 on the GAAP margin of 47% | Accurate (press release recomputed). Imprecise: "adjusted margins exclude SBC" omits that Palantir also excludes employer payroll taxes on SBC | "excludes stock-based compensation and related employer payroll taxes" |
| S2 | §4.2 | m_adj = operating income + SBC "close to the adjusted margins behind company-reported scores" | Accurate as qualified | None |
| S3 | §4.5 | Company-reported quarterly scores are not comparable with the annual measures | Accurate | None |
| S4 | Intro; §8.3 | Bending Spoons' "Rule-of-40 score in the second quarter of 2026 was about 160 as reported" | **Misattribution.** The company reports no Rule-of-40 score (checked in its Q2 6-K). 160 is the panel's arithmetic on reported growth and GAAP margin | "about 160 computed from its reported revenue growth and GAAP operating margin (the company does not report a Rule-of-40 score)" |
| S5 | Intro; §6; §8.3 | "about 37 on the company's own measure of organic growth" | The number is accurate (3% + 34%). Missing caveat: the measure uses "estimated pre-acquisition revenue", is unaudited, and is not presented as non-GAAP or reconciled. SEC staff treat organic growth as a non-GAAP measure (Barnes Group, 7 Oct 2024) | See change 6 |
| S6 | §6, Table 9 | Company-adjusted score of 141.6 for 2025 | Accurate (424B4 reconciliation) | Name C&DI 100.01 when explaining why it lies further from R^A_X |
| S7 | Table 2 notes; §4.4 | E2 uses "the ASC 805 pro forma revenue of the original filings" | Accurate as a research input. ASC 805 pro forma revenue is a supplemental footnote disclosure built on the hypothesis that each deal closed at the start of the comparable period. It is required only of public business entities, for business combinations that are material individually or in aggregate, and can be omitted when impracticable | One sentence in §4.3 |
| S8 | §6 | Vimeo pre-close revenue and purchase-price multiples from the Article 11 pro forma statements | Accurate use. The Article 11 statements are unaudited and, in the company's words, "should not be relied upon" as indicative of results | Add "unaudited, illustrative" |
| S9 | §8.3, §9 | "We suggest computing the score as this paper does, on annual free cash flow after SBC..." | Sound for research. Silent on what follows if an issuer adopts it | See change 4 |
| S10 | Paper-wide | No citation of SEC guidance on metrics | Missing. Release 33-10751 is the governing guidance for any Rule-of-40-type KPI in MD&A | Cite in §8.3 |

### 3.2 Misuse and compliance risk if an issuer cited the paper's metrics

1. **The FCF-after-SBC score as a reported metric.** It is a non-GAAP measure built on a liquidity measure. It needs:
   - a reconciliation to the most directly comparable GAAP measure (net cash from operating activities);
   - a GAAP-based counterpart at equal or greater prominence, such as revenue growth plus GAAP operating margin (C&DI 102.10(a) on ratios);
   - clear labeling (C&DI 100.05);
   - no suggestion that it is cash available for discretionary use (C&DI 102.07).

   Subtracting a non-cash item (SBC) from a cash measure gives a hybrid that needs its own explanation.
2. **The "annuity-charged" score of Remark 3.** It spreads acquisition outflows over T_life = −1/ln NRR, a life the company chooses from an operating metric. That is a tailored measurement method of the kind C&DI 100.04 warns about, and the paper itself shows that "the charging convention, not the data, decides the sign". An issuer presenting the favorable convention would be cherry-picking a method the paper calls a scenario.
3. **Organic score.** Organic growth is a non-GAAP measure in the staff's view and must be reconciled. For an FPI on U.S. GAAP listed only in the U.S., Regulation G applies to its 6-K releases: the Rule 100(c) exemption fails because its measures derive from U.S. GAAP.
4. **Excluding acquisition and reorganization costs as "non-recurring" in a serial acquirer's score.** These are normal, recurring cash operating expenses of the strategy (C&DI 100.01). The paper's own analysis (§6) is the staff's argument.
5. **Durable score, transient surplus, ceiling, decision weight and horizon ranges as KPIs or targets.** They depend on unobserved α, the share of S&M that buys growth, the compute share and the life of acquired revenue. The paper's transient share runs from −2% to 39% on the same data. As KPIs they would need every assumption disclosed (Release 33-10751), and C&DI 100.06 warns that extensive disclosure does not cure a misleading measure. As targets they are forward-looking statements. The PSLRA safe harbor does not apply to forward-looking statements made in connection with an IPO (§27A(b)(2)(D)), the setting in which a newly listed serial acquirer would most want to cite them.
6. **"The dip is the J-curve of transitions in flight" (§8.2) as MD&A narrative.** Item 303 requires known trends and uncertainties to be grounded in the company's facts. Quoting the paper's scenario dip of 3.0 to 3.9 points as the reason for a weak quarter would be unsupported.
7. **Peer benchmarks.** The 95th percentiles (44 in 2023–25) are statistics of a research sample with stated filters, not peer-group benchmarks. Using them in proxy-statement compensation benchmarking needs the E1 and E2 distinction explained.
8. **License.** CC BY-NC-ND bars reproducing the paper's tables in commercial materials without permission. Facts and ideas are free to cite; figures and tables reproduced in an investor deck are not. A one-line note helps readers comply.

### 3.3 Missing caveats

A short "Use in filings" paragraph in §8.3 (change 4); S4, S5 and S8 wording; a citation of Release 33-10751.

### 3.4 Protocol appendix (SEC view)

Not a securities-law matter, but the paper draws on filings retrieved by an agent through the author's browser. The browser script (`code/retrieval_browser.js`) ran four concurrent workers with a 150 ms pause and could not declare a contact user agent. Its peak rate could exceed the SEC's 10 requests a second, depending on latency. About 662 requests is small, but say in Appendix D that retrieval was a single session of about 662 requests. The replication instructions should point to `fetch_companyfacts.py`, which declares a user agent and is sequential at about 6.7 requests a second.

---

## 4. Competition-authority economist (mergers, roll-ups, pass-through)

### 4.1 Accuracy

| # | Location | Statement | Verdict | Fix |
|---|---|---|---|---|
| K1 | Assumption 1 (`ass:market`) | "the cap s̄ ∈ (0, 1) reflects antitrust limits and customer heterogeneity" | **Inaccurate for organic growth.** Neither U.S. nor EU law caps share won on the merits. Merger control limits share that is bought (Clayton Act §7), and conduct rules govern how share is gained or kept | "reflects customer heterogeneity and, for share bought by acquisition, merger control" |
| K2 | Prop. 14(e) (`prop:acquired-score`); §6 intuition | "each acquisition buys a fresh budget of share headroom at k^acq per dollar" | True only for targets outside markets where the firm already competes. In-market deals draw on the same headroom and face the structural presumption (2023 Merger Guidelines, Guideline 1). A series of deals is assessed cumulatively (Guideline 8), and national call-in powers reach deals below thresholds (Italy, Art. 16(1-bis), Law 287/1990, relevant to an Italian acquirer). The FTC's January 2025 consent with Welsh Carson (USAP) shows roll-ups being policed | Add the scope condition; see change 7 |
| K3 | §6 | "a high score sustained by acquisition is evidence of access to targets and capital" | Accurate but incomplete | "...access to targets, capital and regulatory clearance" |
| K4 | §7.2, third conclusion | "in a competitive market, essentially all of a high score must be rent" | Imprecise and quotable against firms. In Proposition 8 (`prop:entry`) "rent" means the scarcity rent ρ on a non-replicable input. The model elsewhere also attributes excess scores to transient growth surplus. Accounting margins are not reliable measures of market power (Fisher and McGowan, *AER* 73(1), 1983) | See change 7 |
| K5 | Lemma 3 (`lem:prices`) | ϕ := d ln p / d ln u; "under monopoly with constant-elasticity demand ... ϕ = u/ĉ ≤ 1" | Accurate as an elasticity. Merger analysis usually means the pass-through *rate* dp/dc, which under constant-elasticity monopoly is ε/(ε − 1) > 1 | One sentence distinguishing elasticity from rate |
| K6 | Prop. 8, Remark 8 | Cournot with entry at date 0; Bertrand; contestability | Accurate; simplifications stated | None |
| K7 | §7.4, lever 4 | "Pricing that captures value ... so that falling unit costs raise γ rather than being passed through to customers" | Correct economics, poor framing. Strategy documents that quote "keep cost savings from customers" are discoverable in a merger review or conduct case. Where competition is effective the lever does not exist; where it does, it reflects differentiation or switching costs | See change 7 |
| K8 | §2.5; §7.4, lever 1 | Data rents, tipping markets, network effects | Accurate citations; missing that tipping digital markets are now the object of ex ante regulation (EU Digital Markets Act, including Art. 14 notification of all gatekeeper acquisitions; UK DMCC Act strategic-market-status regime) | One sentence |
| K9 | §6 Bending Spoons | No discussion of pricing after acquisitions | Gap. The case extract records post-acquisition repricing and layoffs from secondary sources, none verified. The score cannot separate cost efficiency from pricing to an installed base with switching costs, which matters for any efficiency claim. NRR of 91 to 95% is consistent with either | A caveat, not an assertion: "the score does not distinguish cost reductions from price increases to retained customers" |

### 4.2 Misuse and compliance risk

- **Firms.** Board papers that adopt levers 1 and 4 verbatim ("build a non-replicable input; data that tips the market; capture falling costs rather than pass them through") read as intent evidence. A serial acquirer that cites Prop. 14(e) ("each acquisition buys a fresh budget") to justify in-market roll-ups invites Guideline 8 scrutiny.
- **Authorities and complainants.** "In a competitive market, essentially all of a high score must be rent" (K4) can be quoted to argue that a high Rule-of-40 score proves market power. The model does not support that: the score mixes growth G, return on capital (r − G)k, scarcity rents and transient surplus, each on an accounting basis.
- **Efficiency defences.** Using the paper's full-automation ceiling to claim merger efficiencies fails the agencies' tests, which require efficiencies to be specific to the merger, verifiable and passed through. Scenario ceilings are none of these.

### 4.3 Missing caveats

K1, K2, K4, K7, K8, K9. One further point: in Assumption 6 the scarce input's supply grows at the market rate (stated as knife-edge). Under slower supply growth the rent rises, which is the dynamic competition authorities watch in data and compute markets. Worth half a sentence in §7.4.

### 4.4 Protocol appendix (economist view)

The review council included an "industrial-organization economist" agent (Table 16), whose critique is AI-generated. The antitrust statements in K1 and K2 survived it, which illustrates E.7's warning about shared blind spots. Say in E.7 that legal-institutional statements were not reviewed by a human competition lawyer or economist.

---

## 5. AI governance and model-risk lead (NIST AI RMF, ISO/IEC 42001, EU AI Act, SR 11-7-style model risk)

### 5.1 Accuracy

| # | Location | Statement | Verdict | Fix |
|---|---|---|---|---|
| G1 | Definition 3(ii); Table 13 (`tab:fullcost`) | "AI-specific compliance"; "AI compliance at $1 billion of revenue: vendor estimates for security attestation and ISO/IEC 42001, flagged; AI risk-framework staff, red-teaming and privacy assessments for 48 processes" | Plausible as a scenario, correctly flagged; scope unstated. Excludes EU AI Act obligations for providers and deployers of high-risk systems (conformity assessment, technical documentation, post-market monitoring), whose dates moved under Regulation (EU) 2026/1744: Annex III from 2 Dec 2027, Annex I from 2 Aug 2028. Fines for high-risk breaches reach €15 million or 3% of worldwide turnover. A software firm whose product is used in employment or credit decisions falls in Annex III | State that the line excludes high-risk AI Act obligations and penalties; see change 8 |
| G2 | Definition 3, §7.4 lever 5, Corollary 4 | "model-risk validation" as a component of a_min | Under-specified and now without a supervisory anchor. SR 11-7 and OCC 2011-12 were superseded on 17 April 2026 by SR 26-2 and OCC Bulletin 2026-13, which put generative and agentic AI models outside their scope | See change 8 |
| G3 | Lemma 4(e) (`lem:fullcost`), Table 13 | Common-mode cost rises with H_cm, the Herfindahl of exposure across providers | Directionally right; understates correlation. Kim et al. (ICML 2025): models agree on 60% of their errors on one leaderboard; larger models are highly correlated even across architectures and providers. Providers also share cloud regions, base models (fine-tunes of one base) and retrieval corpora | Call H_cm a lower bound on effective concentration |
| G4 | Prop. 10(a) | Diversity of types removes common-mode failure | Same as C5. Human-over-AI layers are not independent of AI errors (automation bias) | Change 2 |
| G5 | Table 13 | T_up = 0.99 to 1.75 years from vendor retirement dates | Accurate as grounded. The interval is partly a control choice: pinned model versions with planned upgrades turn an exogenous regression into a scheduled change | Note it |
| G6 | §2.4; Definition 3(ii) | PQC dates via NIST IR 8547 | Final version exists (27 Oct 2026); the deprecation dates were not re-read in the final text | Confirm the dates in the final IR |
| G7 | Paper-wide | No reference to NIST AI RMF or ISO/IEC 42001 structure | Missing. Practitioners will want the four floors mapped to a framework: c_mnt to Measure/Manage (revalidation); c_sec to Manage (security, injection); c_err to Measure (error, confabulation, misbehavior); c_anc to Govern (AI spend, legal, incident response); a_min to Govern (accountability). NIST says AI RMF 1.0 is being revised under the AI Action Plan; the Generative AI Profile (AI 600-1, July 2024) is the current GenAI overlay | One sentence and a citation in Definition 3 |
| G8 | Definition 3 | "whatever human review and sign-off regulation ... requires" | Accurate, and correctly avoids a numeric human-oversight floor (the AI Act sets none; errors log B1) | None |

### 5.2 Misuse and compliance risk

- **Budget anchoring.** Citing "AI compliance of 0.10 to 0.40% of revenue" (Table 13) as a governance budget. It is a class-d scenario for 48 processes at $1 billion and excludes high-risk AI Act obligations.
- **Risk-factor language.** "Multi-provider diversity eliminates common-mode risk" would be inaccurate given G3; under Item 105 it would be a misleadingly reassuring risk factor.
- **Financial institutions.** Citing "SR 11-7-style validation" as the governance standard for GenAI. Since April 2026 the banking agencies say GenAI and agentic AI are outside their model-risk guidance and fall under broader risk management. A bank that claims SR 11-7 compliance for an LLM control is citing superseded guidance with no current analogue.
- **Workforce transitions.** Using the paper's change-capacity framing (10 to 20% of employees' work changed a year) to plan AI-driven task allocation or performance monitoring without noting that such systems are Annex III high-risk under the AI Act, with deployer duties including informing workers.

### 5.3 Missing controls and caveats

G1, G2, G3, G7. Also: version pinning and testing before release as the primary control over common-mode regression (C8, G5); least-privilege caps on tool permissions, which the paper uses as Ȳ in Lemma 4(d) and should name as a control; and logging of prompts, outputs and model versions as the audit trail.

### 5.4 Protocol appendix (governance view)

The research itself used an AI system with three notable permissions: browser control on the author's computer, file-system access and web search. A governance reviewer would ask for:

1. the model identifier and run dates (given), and the tools each agent could use (not given);
2. whether the logged-in browser session gave agents access to accounts beyond the SEC sites (state the scope and that it was limited);
3. whether full session transcripts are retained (the appendix cites the agent log and errors log, which are summaries written by the lead agent).

Retain the transcripts, or a hashed archive, with the replication package. The appendix records the author's direction well. It records no control over the lead agent's summaries to the author, which were the only channel (E.1).

---

## 6. Protocol appendix (Appendix E): research-integrity review

**Strengths.** Above the norm.
- arXiv's policy is cited correctly: report significant use; AI is not an author; authors are responsible.
- The appendix names agents and roles, records the author's decisions (Table 17) and tabulates errors by the safeguard that caught them (Table 18).
- Two forking-path episodes are disclosed openly: the reversed flat frontier, and the switch of estimand after the robustness results were known.
- E.7 states the main limitation (shared model, shared blind spots).

**Accuracy and adequacy problems.**

| # | Location | Issue | Evidence | Fix |
|---|---|---|---|---|
| P1 | Table 16, E.2, E.6, Table 17 | "Referee panel", "referee round", "a referee who re-derived the results", "referee and practitioner panels" | All are AI agents (agent log rows "Referee panel (3)" and "Paper 1 review panels, round 1 (8 agents)"). Readers will take "referee" to mean human peer review | Use "AI referee agents" and "AI practitioner-role agents" throughout; add to E.1: "No human referee or practitioner reviewed this version." |
| P2 | E.3 (`app:protocol-panels`) | Placeholder in the release candidate | Text: "[Placeholder, to be completed...]" | Fill it before posting, including changes declined and why, and state that the panels were AI agents of the same model |
| P3 | E.1 | "Where independence mattered, an agent was given a distinct role and no access to the others' outputs" | Agents shared one file system; this panel could read the agent log, errors log and other agents' notes | "...was not given the others' outputs as inputs; all agents worked in one shared file system and could have read them" |
| P4 | E.1, E.2 | No timeline | Agent log: Phase 1 on 28 to 29 Oct; Phase 2 from 06:33 on 29 Oct; title chosen 12:03; review panels started 12:46. The 81-page paper, its data and the companion were produced in about two days | State the dates and the time the author spent reviewing; a reader judges the depth of human review from this |
| P5 | E.4, E.7 | "The author's review is the final check" does not say what the author checked | Not in any log | Add a short list: which numbers the author checked against filings, whether the author read the proofs and `verify_theory.py`, and which sections the author read in full |
| P6 | E.1 | Who wrote what | Table 16 shows agents drafted the model, proofs, data, empirics, horizons, abstract, introduction, discussion, conclusion and the appendix | Say plainly: "All text, code, derivations and data processing were produced by AI agents; the author directed the work, made the decisions in Table 17 and reviewed the result." |
| P7 | Title footnote, Table 17 | No competing-interests statement | Agent log, 10:50: the author decided on "no disclosure statement" and that the employer is not named. Errors log B1b: a conflict-of-interest risk with the author's employer was caught and corrected in the companion paper | The employer can stay unnamed while interests are still disclosed. Suggested: "The author is employed in the software industry. This research was done independently, without employer resources, data or review, and the views are the author's own. [The author has no financial interest in any company named in the paper.] [Disclose any venture or advisory role in AI compliance or agentic-AI products.]" Confirm the bracketed parts. Paper 1's claims about AI-run controls and the accountability floor are where a reader would look for an interest |
| P8 | Footnote; Appendix D | "Data and code are available from the author" versus "part of the replication package" | Unclear whether the package is public | Deposit the package with a DOI at posting, or state the access terms |
| P9 | Appendix D; references | "read in the author's browser" (F-1, 424B4, 6-Ks); "Retrieval ... through a browser on the author's computer" | The lead agent operated the browser (case extract: "The lead agent retrieved it in the author's built-in browser") | "retrieved by the lead agent through a browser session on the author's computer" |
| P10 | Appendix D | EDGAR fair-access compliance | See §3.4 | One sentence |
| P11 | Table 18 | Errors list ends before this review round | Expected | Add this round's errors (C10, C11, S4, K1) under "Review panels (AI, this version)" |

**Adequacy verdict.** For arXiv, the disclosure already exceeds the requirement. For a journal's research-integrity reviewer, it is adequate once P1 to P7 are fixed. P1, P3 and P7 are accuracy issues, not style.

---

## 7. Consolidated top 10 changes, with text

**1. Turn the accountability floor into a constrained minimum** (Prop. 10 `prop:amin`, Remark 10 `rem:amin-values`, §8.5). Add after Proposition 10:

> "The minimum in (28) compares the cost of designs; it is not a control-design standard. Management may not conclude that internal control over financial reporting is effective if a material weakness exists (Item 308(a)(3)), that is, if there is a reasonable possibility that a material misstatement will not be prevented or detected on a timely basis (AS 2201.A7). The relevant floor is therefore the cheapest design whose annual probability of an undetected material misstatement, 1 − (1 − P_mm)^{N_mm}, is remote. A design on one AI provider with N_mm p^cm_j that is more than remote cannot meet the standard however many layers it uses, which sharpens part (b)."

In Remark 10 add:

> "In this example the best all-AI and all-human designs leave about 0.12 and 0.05 undetected material misstatements a year, so neither would meet the standard; the mixed design leaves 0.007. Because the human common-mode term alone gives 0.048, these parameters are illustrative and not calibrated to an effective-ICFR baseline. L_mm is the consequence cost of an undetected misstatement (restatement, remediation, audit fees, cost of capital, litigation, clawback), not its amount."

**2. Qualify independence and make ITGCs count** (Assumption 7 `ass:layers`, Prop. 10(a), Lemma 4(e)). Add:

> "Failures of different types are treated as independent. In practice, management override, defects in shared source data or in information produced by the entity, and failures of IT general controls defeat human and AI layers together; reviewers of AI output are subject to automation bias (Parasuraman and Manzey, 2010); and errors of models from different providers are strongly correlated, with models agreeing on 60% of their errors on one benchmark (Kim et al., 2025). The value of diversity in (a), and the provider-concentration term in Lemma 4(e), are therefore upper and lower bounds respectively. The IT general controls in C^itgc_g (pinned model versions, testing before release, rollback) are the control over the model-update failures that p^cm_j prices; treating p^cm_j as fixed while charging for them makes the floor conservative."

**3. Bring the audit-reliance facts into Paper 1** (§8.5, last paragraph). Add:

> "Auditors may reduce testing of entirely automated application controls that are unchanged since a baseline and supported by effective general controls (AS 2201.B28 to .B31). In our judgment a control performed by a model that its vendor updates, or whose output varies from run to run, does not qualify, so it is tested each year like a manual control, and its outputs are information produced by the company (AS 1105.10). Assurance from a model provider is useful for ICFR only if it addresses controls relevant to financial reporting (a SOC 1 Type 2 report; AS 2601); otherwise the auditor tests user-entity controls and outputs directly. As of October 2026 no PCAOB standard or staff guidance addresses AI-performed controls, and the Board's 2026 request for comment on its strategic priorities makes AI in financial reporting a central focus. The direct audit and Section 404 cost of about 0.14% at $1 billion uses an S&P 500 fee ratio and is likely understated for firms of that size."

Also fix C2 and C3: "accelerated or large accelerated filer that is not an emerging growth company ... opinion on the effectiveness of ICFR (AS 2201.03)", and add 18 U.S.C. §1350.

**4. Add a "Use in filings" paragraph** (§8.3, after the recommendation to compute on FCF after SBC):

> "Use in filings. A score computed on adjusted margins, free cash flow, organic growth or acquisition-charged bases is a non-GAAP financial measure, and any Rule-of-X score discussed in MD&A is a key performance indicator. An issuer presenting one would need a reconciliation to the most directly comparable GAAP measure and a GAAP-based counterpart of equal or greater prominence (Regulation G; Item 10(e) of Regulation S-K; C&DI 102.10). It should avoid implying that free cash flow is discretionary cash (C&DI 102.07), and should not exclude acquisition and reorganization costs that recur in an acquisitive strategy (C&DI 100.01). It would also owe the definition, purpose, use, assumptions and consistent method that Release 33-10751 expects, under disclosure controls. The ceiling, durable score, transient surplus, decision weight and horizon ranges rest on unobserved parameters and scenario values and are not suitable as reported metrics or targets; stated as expectations they are forward-looking statements, for which the statutory safe harbor is unavailable in an initial public offering."

**5. Correct the "reported" score attributions** (Intro, §6, §8.3). Replace "the Rule-of-40 score in the second quarter of 2026 was about 160 as reported" with "its Rule-of-40 score in the second quarter of 2026, computed from reported revenue growth and GAAP operating margin, was about 160 (the company does not report the score)". In §8.3 change "adjusted margins exclude SBC" to "adjusted margins exclude stock-based compensation (and, at Palantir, related employer payroll taxes)", and add: "Palantir presents the score as a defined term, not as a non-GAAP measure; its adjusted margin is reconciled."

**6. Fix the acquisition accounting and add reliability caveats to the case** (Remark 3 `rem:acquired-bounds`, §6, Table 9 `tab:acquired-score`).
- Replace "On the GAAP basis it touches the score only through the amortization of acquired finite-lived intangibles, since goodwill is not amortized" with: "On the GAAP basis it touches the score through the amortization and impairment of acquired intangibles, transaction costs, which are expensed (ASC 805-10-25-23), and post-combination restructuring and compensation; goodwill itself is not amortized (Deloitte, 2026)."
- Relabel the Table 9 row "Amortization and impairment of acquired intangibles".
- Add to §6: "The company's organic growth uses estimated pre-acquisition revenue, is unaudited and is not presented as a non-GAAP measure, although SEC staff treat organic growth as one. Its registration statement discloses material weaknesses in internal control over financial reporting, its first-quarter 2026 cash flows are restated, and it has not yet been subject to a Section 404 assessment. Staff guidance also lets an issuer exclude an acquired business from its assessment for up to a year, so a serial acquirer's assessed control scope lags its revenue. The pro forma statements we use are unaudited and illustrative."

**7. Correct the antitrust statements and reframe the levers** (Assumption 1 `ass:market`, Prop. 14(e), §7.2, §7.4).
- Assumption 1: "...where the cap s̄ ∈ (0, 1) reflects customer heterogeneity and, for share bought by acquisition, merger control."
- Prop. 14(e) intuition, add: "This holds for acquisitions outside the markets the firm already serves. Acquisitions inside them draw on the same headroom and are subject to merger review, which presumes harm above an HHI of 1,800 with an increase of more than 100 or a share above 30% (2023 Merger Guidelines, Guideline 1). The agencies assess a series of acquisitions cumulatively (Guideline 8), and national authorities can call in deals below the thresholds. Regulatory clearance, as well as targets and capital, limits ḡ^acq."
- §7.2: replace "in a competitive market, essentially all of a high score must be rent" with "in a competitive market, a durable high score requires a rent on an input rivals cannot replicate; the score does not distinguish such rents from market power, and accounting margins are not a reliable measure of market power (Fisher and McGowan, 1983)."
- Lever 4: "Pricing power: the share of falling unit costs the firm retains, 1 − ϕ in Lemma 3, which depends on differentiation, switching costs and the intensity of competition."
- Lemma 3: add "ϕ is an elasticity; the pass-through rate dp/du equals ϕp/u and exceeds one under constant-elasticity monopoly."

**8. Update the AI-governance anchors** (Definition 3 `def:fullcost`, Table 13 `tab:fullcost`, §7.4 lever 5). Add to Definition 3:

> "Model-risk validation here means the firm's own validation: the U.S. banking agencies' revised model risk guidance of 17 April 2026 (SR 26-2; OCC Bulletin 2026-13), which superseded SR 11-7, places generative and agentic AI models outside its scope. The AI-compliance line of Table 13 covers security attestation, an ISO/IEC 42001 management system and framework staff; it excludes the obligations and penalties of the EU AI Act for high-risk systems, which apply from 2 December 2027 for Annex III systems and 2 August 2028 for Annex I (Regulation (EU) 2026/1744). The four floors map to the NIST AI RMF functions (Govern, Map, Measure, Manage); AI RMF 1.0 is under revision and its Generative AI Profile (NIST AI 600-1) is the current overlay."

In Table 13 notes, mark the common-mode Herfindahl H_cm as a lower bound on effective concentration (Change 2).

**9. Tax and capitalization precision** (Remark 1 `rem:taxes`, §7.2, §8.3).
- §7.2: replace "runs from the 15% corporate alternative minimum tax to the 21% federal rate" with "is a scenario range of 15 to 21%. The 15% corporate alternative minimum tax applies only to corporations with average annual adjusted financial statement income above $1 billion. Because it is levied on book income, deductions under §174A do not reduce it, so ψ < 1 for development when it binds."
- Remark 1, add: "The 100% allowance does not extend to property used predominantly outside the United States, and deductions are worth less to loss-making firms with limited loss offset."
- §8.3, after the sentence on capitalized software, add: "From fiscal years beginning after 15 December 2027, or earlier on adoption, ASU 2025-06 removes the project stages of ASC 350-40 and defers capitalization while significant development uncertainty remains, so novel AI builds will be expensed for longer, and GAAP scores before and after adoption are not comparable."

**10. Make the protocol appendix accurate** (Appendix E `app:protocol`, Tables 16 to 18).
- E.1, add: "All text, code, derivations and data processing were produced by AI agents; the author directed the work, made the decisions in Table 17 and reviewed the result. The project ran on 28 and 29 October 2026. [State the author's review time and what the author checked personally.] The review agents described as referees and practitioner panels are AI agents of the same model; no human referee or practitioner reviewed this version."
- Replace "no access to the others' outputs" with "was not given the others' outputs as inputs; all agents shared one file system".
- Replace "read in the author's browser" with "retrieved by the lead agent through a browser session on the author's computer".
- Fill E.3. Add a competing-interests statement (P7 text). Deposit the replication package with a DOI. Add one sentence in Appendix D on EDGAR fair access.

---

## Appendix: Remark 10 computations (panel's arithmetic)

Parameters as in Remark 10: N_mm = 24; L_mm = $10 million; human p = 0.05, p^cm = 0.002, c = $500,000; AI p = 0.02, p^cm = 0.005, c = $50,000; ITGC $350,000.

| Design | P_mm per opportunity | Expected undetected a year (N_mm P_mm) | Annual probability of at least one | Cost (paper) |
|---|---|---|---|---|
| All-human, 3 layers | 0.002 + 0.998(0.05)^3 = 0.002125 | 0.051 | 5.0% | $2.01M |
| All-AI, 3 layers | 0.005 + 0.995(0.02)^3 = 0.005008 | 0.120 | 11.4% | $1.70M |
| 1 human + 2 AI | 0.0519 × 0.005398 = 0.000280 | 0.0067 | 0.7% | $1.02M |
| Any all-human (limit) | ≥ 0.002 | ≥ 0.048 | ≥ 4.7% | n/a |
| Any all-AI on one provider (limit) | ≥ 0.005 | ≥ 0.120 | ≥ 11.3% | n/a |

The paper's costs reproduce exactly. The compliance reading changes the interpretation, not the arithmetic.
