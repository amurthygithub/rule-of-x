# R-C2 — Citations & prior-art re-review (round 2, 4 Nov build)

Referee E (prior art, citation verification, parameter-source transport), second round.
Working copy: repo_v4 @ eb7537b, PDFs as in rereview MANIFEST (paper1.pdf 87pp, supplement.pdf 72pp).

**Model-identity disclosure:** I am a separate conversation context of the same LLM family (GLM glm-5.3 via DeepSeek Harness) as the Lead and the other panel members; the author addressed the panel as "GLM 5.3 (high effort)". Not independent human experts and not independent model-family evidence. Web verifications below are mechanical (quoted strings, DOIs, dates) and reproducible; their selection and interpretation come from one model.

**Status: IN PROGRESS — appended incrementally per unit.**

---

## Work units (updated as I go)

- [x] Unit 0: read PROMPT.md, RESPONSE.md (claims), author's issue_log.md rows for my findings
- [x] Unit 1 (Part A): GLM-F3 — Nei et al. (2026) now cited; "only" dropped
- [x] Unit 2 (Part A): GLM-M13 — AS 2201 ".03 and .06"
- [x] Unit 3 (Part A): GLM-M14 — Lee 1,756 vs 1,771 (author: NOT VALID)
- [x] Unit 4 (Part A): GLM-M16 — Vista URL; Svanberg a_min sensitivity
- [x] Unit 5 (Part A): GLM-15 — Ge & Huang 2014 citation
- [x] Unit 6 (Part A): GLM-17 — Roche & Tandon, ref_verification.md
- [x] Unit 7 (Part A): GLM-18 — Dell'Acqua published version
- [x] Unit 8 (Part B.a): legal/tax citations spot-check (≥5 load-bearing)
- [x] Unit 9 (Part B.b): new citations S10–S12 sample verification
- [x] Unit 10 (Part B.c): new abstract factual claims
- [x] Unit 11 (Part B.d): A.6 search-protocol sentence
- [x] Unit 12: what I could not check; summary

---

## Unit 0 — Context read (PROMPT.md, RESPONSE.md, issue_log.md rows)

RESPONSE.md and the issue-log rows for GLM-F3, GLM-M13, GLM-M14, GLM-15, GLM-16, GLM-17, GLM-18, GLM-20 were read as author claims. Restricted material (paper1_v4/, author_reviews/ outside glm_5_3_high/, response_to_outside_reviews.md) was not opened. New-PDF locators below use the current numbering (printed page == PDF page, per rereview MANIFEST).

---

## Unit 1 — GLM-F3 (Nei, Ruus and Indov 2026 now cited; "only" dropped)

**Author claim:** M 1 and M 2.2 cite Nei et al. (2026), drop "only"; bib entry from Crossref; only record+abstract read, and text+bib say so.

**Verification:**
- **M 1, printed p.5** (extraction paper_full.txt:259-261): "The peer-reviewed academic studies of the rule we are aware of evaluate it as an investment screen (Lee, 2024) or relate it to enterprise value (Nei et al., 2026); neither estimates the frontier." — "only" dropped, plural phrasing, both studies named. ✓
- **M 2.2, printed p.9** (paper_full.txt:418-423): "The peer-reviewed academic studies of the rule we located are Lee (2024)… and Nei et al. (2026), who relate the growth of enterprise value of listed SaaS firms to revenue growth, EBITDA margin and the rule across growth stages (we have read its published record and abstract, not the article). Neither estimates a growth–profitability frontier, and we found no modern peer-reviewed study that does." ✓
- **Accuracy of the description vs the source:** the Crossref abstract (I retrieved it in round 1, api.crossref.org/works/10.61093/fmir.10(3).130-168.2026) says the study "assesses how revenue growth and EBITDA margin, independently and jointly, are associated with annual enterprise value growth across revenue-defined groups and whether the Rule of 40 provides a consistent valuation-related indicator." The paper's paraphrase ("relate the growth of enterprise value … to revenue growth, EBITDA margin and the rule across growth stages") matches; "Neither estimates a growth–profitability frontier" matches the abstract's regression/quartile design (no frontier). ✓
- **Bibliography entry** (paper_full.txt:3947-3949): "Lembit Nei, Aime Ruus, and Matis Indov. Enterprise value dynamics in publicly traded SaaS firms: Revenue growth, EBITDA margin, and the Rule of 40 across revenue-defined growth stages. Financial Markets, Institutions and Risks, 10(3):130–168, 2026. doi: 10.61093/fmir.10(3).130-168.2026. Crossref record and abstract only; the article itself was not read." — every field matches the Crossref record I verified in round 1 (authors, journal, 10(3):130–168, 2026, DOI), and the access level is disclosed in the entry itself. ✓
- The issue log's proposed next step ("Read the article (author's browser) before finalizing the description") was not done; it does not need to be, because the description is abstract-faithful and the access level is disclosed on its face.

**Verdict: RESOLVED.** The fix is exactly what my round-1 finding (E-1) proposed as the acceptance test, including the disclosure.

---

## Unit 2 — GLM-M13 (AS 2201 ".03" → "paragraphs .03 and .06")

**Author claim (= DS-50's fix):** ".03 fits the clause it is attached to, and 308(b) is already cited in the same sentence"; text now reads "paragraphs .03 and .06".

**Verification:**
- **New text, M 8.5, printed p.70** (paper_full.txt:3456-3460): "the auditor of an accelerated or large accelerated filer that is not an emerging growth company must express an opinion on the effectiveness of internal control over financial reporting in an integrated audit performed under PCAOB Auditing Standard 2201, paragraphs .03 and .06". The sentence separately cites the statutory/rule sources ("United States Congress, 2026b; …; U.S. Securities and Exchange Commission, 2026a"), so the obligation's legal source is cited beside the standard.
- **Against the standard's text** (pcaobus.org AS 2201 page, fetched via Wayback snapshot 2021-04-12; live page Cloudflare-blocked; paragraph text stable since adoption, amended 2016):
  - **.03:** "The auditor's objective in an audit of internal control over financial reporting is to express an opinion on the effectiveness of the company's internal control over financial reporting…" — supports "express an opinion on the effectiveness."
  - **.06:** "The audit of internal control over financial reporting should be integrated with the audit of the financial statements." — supports "in an integrated audit."
  So ".03 and .06" is now precise: .03 supplies the opinion-on-effectiveness objective, .06 the integrated-audit character. ✓
- **New citation added by the same fix** (Prop 5(b), printed p.30, paper_full.txt:1478-1480): "The equivalence with the standard requires O to include every combination of deficiencies that could together constitute a material weakness (AS 2201, second note to paragraph .65)". Verified against the standard: the **second Note to .65** reads "Multiple control deficiencies that affect the same financial statement account balance or disclosure increase the likelihood of misstatement and may, in combination, constitute a material weakness, even though such deficiencies may individually be less severe. Therefore, the auditor should determine whether individual control deficiencies … collectively result in a material weakness." — the citation is apt for the admissibility-equivalence clause. ✓
- **Residual defect (minor, introduced/incompletely applied):** the printed bibliography note for AS 2201 (paper_full.txt:3977-3979) still enumerates "Paragraphs .03, .16 to .19, .36, .44 to .47, .49, .52, .53, .55, .69, .A7, .A11, .B17 to .B22 and .B28 to .B31" — it does **not** include .06 or .65, which the text now cites (repo bib identical: repo_v4/paper1/refs_paper1.bib:1061-1068). The paragraph-relied-on list is stale relative to the new citations.
  - Severity: minor presentation issue. Fix: add .06 and .65 to the note (one-line bib edit). Evidence: locators above.

**Verdict: RESOLVED** (the substance my row pointed at is fixed accurately and precisely), with one new minor inconsistency (stale bib paragraph list) that should be repaired.


---

## Unit 3 — GLM-M14 (Lee 1,756 vs 1,771) — **I accept the author's "Not valid (reviewer error)" classification**

**Author claim:** the AFL published article page (ojs.aut.ac.nz/.../article/view/761, fetched 2 Nov) says "a sample of 1756 SaaS companies worldwide"; 1,771 is the MPRA preprint's number; the paper cites the published version.

**My independent verification (decisive):**
- In round 1 I could not open the AFL page (old URL form 404'd; the tuwhera redirect was Cloudflare-blocked), so I verified only the MPRA preprint — which says **1,771** in every occurrence (abstract, §"The study examines 1771 SaaS firms", §"final sample… 1771 SaaS companies").
- This round I fetched the AFL article page at the corrected URL form now used in the paper's bibliography, `https://ojs.aut.ac.nz/applied-finance-letters/1/article/view/761` (HTTP 200; saved: `diag/rereview-prior-art/afl_new.html`). The published abstract reads: **"Our study analyses a sample of 1756 SaaS companies worldwide spanning the period 2003-2022."** — "Archives / Vol. 13 (2024)", author King Fuei Lee, affiliation Schroder Investment Management, DOI 10.24135/afl.v13i.761.
- Corroboration in the repo (allowed paths): the author's **v1-era** verification note `notes/reviews/paper1_v1/fable_referee_io_ai.md:127` had already recorded "1,756 SaaS firms 2003-2022 … OK (volume and pages not shown on page)" from ojs.aut.ac.nz — i.e., the 1,756 reading predates my round-1 report and is not a post-hoc rationalization. `notes/ref_verification.md:22` likewise records 1,756 (status "verified").
- The new bibliography entry (printed p.~80; repo `paper1/refs_paper1.bib` `lee2024evaluating`) now carries the DOI 10.24135/afl.v13i.761 and the working URL, both of which match the live AFL page, and keeps "Also circulated as MPRA Paper 121568."
- The paper's sentence (M 2.2, printed p.9): "evaluates it as an investment screen on 1,756 SaaS firms over 2003 to 2022" — **matches the cited (published) version exactly.**

**Verdict: I ACCEPT "Not valid (reviewer error)".** My round-1 finding was mistaken in substance: I treated the preprint's 1,771 as the published record and asked the author to correct toward it; in fact the published version — the one the paper cites — says 1,756. My round-1 report did hedge ("pending a check of the published AFL text"; access level "MPRA full text; published AFL page not accessed"), so the defect was an unverified suspicion stated too strongly, not a fabrication. The author's evidence chain (working URL, page text, pre-existing v1 note) is consistent and reproducible; I reproduced it myself.
- Access level of my verification: **full text of the AFL article landing page** (abstract + metadata) plus round-1 full text of the MPRA preprint. I did not read the AFL article body (paywall-free PDF not needed for this point).
- Residual (optional, not a defect): the preprint and published version differ in the sample count (1,771 vs 1,756). A one-line bib note ("the MPRA preprint reports 1,771") would prevent future readers from repeating my round-1 confusion; this is polish, not an error. Severity: none.
- Lesson for the panel recorded: when two versions of a source disagree, the cited version controls; my round-1 report should have labeled the 1,756-vs-1,771 question "unresolved replication question" rather than "evidence-transport problem."


---

## Unit 4 — GLM-M16 (Vista URL; Svanberg a_min sensitivity)

**Author claim:** Vista bib URL loads the cited article (WebFetch 2 Nov), so no change; the optional a_min sensitivity over δ_M is covered by the S10 joint stress test varying δ_M over 0.10–0.40; no separate row.

**Verification (a) Vista URL:** I re-tested the bib URL exactly as printed (`https://www.vistaequitypartners.com/insights/rethinking-software-benchmarks-in-an-ai-driven-market/`, repo bib unchanged from round 1): it now returns **HTTP 200 with no redirect** and the live page contains the article ("Rethinking Software Benchmarks", "Rule of 60", "emerging aspiration" — saved `diag/rereview-prior-art/vista_new.html`). In round 1 (3 Nov) the same URL redirected to `/insights/ai-rule-of-60-software-benchmarks`, which 404'd. The defect I reported no longer reproduces; the author's "no change" is factually right today.
- Residual observation (severity: minor/optional): the URL's behavior changed between 3 and 5 November (404 → live), which is precisely the volatility my suggestion addressed. Citing the Wayback snapshot (2026-01-18, verified in round 1) beside the live URL remains good practice for practitioner pages, but with the link live I do not press the point.

**Verification (b) Svanberg/δ_M sensitivity:** The new supplement covers δ_M in two printed places:
- **Table S17 (full-cost floors), printed p.~56** (supp_full.txt:3274-3280): "Upkeep δM … 0.10 / 0.17 / 0.40 (b) Svanberg et al. (2024); software support fees", with the resulting maintenance cost **c_mnt = 0.15 / 0.60 / 2.89** via Lemma S4(a) — i.e., the marginal dependence of the maintenance floor component on δ_M over exactly the range I proposed is in the printed robustness table, including the ~19× span.
- **S10 joint stress test, printed p.~57-58** (supp_full.txt:3317-3360): the 51-dimension box explicitly includes "the band of a_min" and "the security, maintenance, AI-failure and other full-cost inputs"; the accountability claim is tested in its own sub-box ("No all-AI design on one provider admissible … accountability sub-box, π̄ = 5%", Table S18 last row), and ST-1 reports that the threshold falls below 30% only "when the tax rate, the accountability floor and the AI-failure losses are all near their favorable ends" — i.e., the a_min band's effect on headline claims is surfaced, not hidden.
- The underlying disclosure limitation I flagged in round 1 is still printed: Table S17 keeps "Svanberg et al. (2024); software support fees" for upkeep (the central 0.17's support-fee rates remain unverified), and the S11-style source table keeps "Integration cost per system 60,000 dollars [20,000, 200,000] … An upper bound only … No source found for the value itself" (supp_full.txt:2464-2465).

**Assessment of adequacy:** The joint box subsumes a one-at-a-time sensitivity row for the purpose my row cared about — whether the paper's conclusions survive the upkeep uncertainty (S10 is a stronger test: it asks whether any headline claim fails anywhere in the box). The component-level marginal (c_mnt vs δ_M) is available in Table S17. What is still not printed anywhere is a_min itself as a function of δ_M alone at other inputs central — but a_min's band is a stress-test dimension and its consumers (threshold G*, payback, 2036 score) are all stress-tested. I judge the substitute **adequate**.

**Verdict: PARTLY RESOLVED, and the part not applied was reasonably declined.** The Vista dead-link is cured (verified live); the Svanberg sensitivity is adequately covered by Table S17 + S10; the residual (single computer-vision case study behind the upkeep precedent; unsourced $60k integration cost, both disclosed) remains a disclosed limitation of the paper, not an unaddressed review point.


---

## Unit 5 — GLM-15 (Ge and Huang 2014 cited in M 2.3)

**Author claim:** M 2.3 now cites Ge and Huang (2014) as "a stochastic frontier of SaaS firms' economies of scale, not a growth-margin frontier"; bibliography verified at the IEEE index record and the second author's list.

**Verification:**
- **Text, M 2.3, printed p.9-10** (paper_full.txt:442-444): "We have not found prior applications of these estimators to the growth-margin plane of software firms; Ge and Huang (2014) estimate the economies of scale of SaaS firms with a stochastic frontier, not a growth–margin frontier." ✓ exists, placed exactly where my round-1 open question asked for it.
- **Bibliography** (repo `paper1/refs_paper1.bib` `ge2014analyzing`): Ge, Chunmian and Huang, Ke-Wei; "Analyzing the Economies of Scale of Software as a Service Software Firms: A Stochastic Frontier Approach"; IEEE Transactions on Engineering Management 61(4):610–622, 2014; doi 10.1109/TEM.2014.2359975.
- **Against the primary record** (Crossref DOI 10.1109/tem.2014.2359975, fetched this round): title, authors (Chunmian Ge; Ke-Wei Huang), journal, 61(4):610–622, published Nov 2014 — **every field matches**. (In my round-1 report the title was truncated to "…A Stochastic Frontier Analysis" — the true title ends "Approach"; the paper's bib has it right.)
- **Characterization:** "estimate the economies of scale of SaaS firms with a stochastic frontier" matches the title; "not a growth–margin frontier" is consistent with an economies-of-scale (cost) SFA. The hedge "these estimators" (order-m / conditional-quantile partial frontiers) also survives, since Ge and Huang used parametric SFA, not partial frontiers.
- **Access-level disclosure:** the bib note says "Index record and a summary of the abstract only; the article itself was not read. Details from the publisher's index record and the second author's publication list, 2 November 2026" — honest, and sufficient for the narrow role the citation plays (acknowledging adjacent prior frontier work, not carrying a number).

**Verdict: RESOLVED.** The citation is accurate at the primary record, correctly characterized, and access-disclosed. My round-1 open question 7(i) is answered exactly as proposed.


---

## Unit 6 — GLM-17 (Roche and Tandon 2021 content unverifiable — "Already handled" claim)

**Author claim:** "Recorded as verified in notes/ref_verification.md. No change."

**What the file actually records** (`repo_v4/notes/ref_verification.md:17`, checked 2026-10-28/29):
- Status "**verified**", which the file's key defines as "all bibliographic fields confirmed"; the verification method (file header) was "web search and by fetching a landing page".
- The relevance column records **content facts**, not just metadata: "200+ firms over 2011-2021; firms beat the rule about 16% of the time; valuation premium. Wikipedia lists a different author and date; the McKinsey page itself gives Roche and Tandon."
- So the author's pass evidently saw the article's content (the 200+/16%/premium trio is not bibliographic metadata), and the authorship was resolved against the McKinsey page's own byline over Wikipedia's listing.

**My attempt to reproduce (both rounds):** mckinsey.com returns Akamai 403 at every route available to me — direct curl (HTTP 000 connection reset), web_fetch, reader proxy (403), and the page is not in the Wayback Machine (CDX: no snapshot of either URL form). **I still cannot independently verify the paper's sentence** (M 2.2, printed p.8-9): "Roche and Tandon (2021) reach similar conclusions for more than 200 software firms over 2011 to 2021."

**Assessment of adequacy:**
- The verification record is specific, internally consistent, and pre-dates my round-1 report (28 Oct), so it is not a post-hoc rationalization. It is the kind of private evidence a careful author keeps.
- Against that: (i) it is not reproducible by this referee (page unreachable from my environment in both rounds); (ii) no archived copy of the fetched page exists in the repo (I searched: the AFL fetch evidence for M14 exists indirectly via the v1 note, but nothing for the McKinsey page); (iii) the printed bib entry for Roche & Tandon carries only "Published 3 August 2021" — unlike the Nei and Ge & Huang entries, it does not disclose an access level, so a reader cannot tell whether the article or only its metadata was read; (iv) the sentence asserts "similar conclusions", a substantive summary of an analysis I have never seen.
- Load: low (one supporting sentence in §2.2; nothing downstream depends on it). A normal browser user can presumably reach the McKinsey page; my 403 is an environment artifact, which lowers the practical severity.

**Verdict: PARTLY RESOLVED.** The author's "already handled" is accurate in that a specific, dated verification record exists; the residual weakness is that the paper's one substantive claim from this source ("similar conclusions for more than 200 software firms over 2011-2021") remains the only §2.2 practitioner fact I could not check at a primary source across two rounds.
- Proposed fix (severity: minor): add to the bib note the article's own summary numbers as the author's log records them (e.g., ">200 firms, 2011-2021; ~16% of firm-years above the line; valuation premium"), and/or archive a copy of the fetched page in the repo. This makes the claim auditable without relying on the private log.


---

## Unit 7 — GLM-18 (Dell'Acqua et al.: published-version check)

**Author claim:** figures match the working paper and secondary summaries of the 2026 article; the publisher's page could not be read, so the check against the published version "is not complete." No change.

**My verification (this round):** The publisher's page is CAPTCHA-blocked at all my routes (direct, reader proxy), but INFORMS deposits the published abstract with Crossref. The Crossref record for DOI **10.1287/orsc.2025.21838** (fetched this round) carries the published abstract, which states: "subjects using AI outperformed those not using AI, completing **12.2% more tasks** and completing them **25.1% more quickly** on average… for a complex managerial task selected to be outside the frontier, subjects using AI were **19% less likely** to produce correct solutions compared with those without AI." (758 knowledge workers, preregistered, three conditions — also matching the WP's design.)
- The paper's sentence (M 2.4, printed p.10, paper_full.txt:465-466): "inside the frontier of AI capability, knowledge workers completed 12.2% more tasks 25.1% faster, while on a task outside it AI lowered performance (Dell'Acqua et al., 2026)" — **verified against the published version's abstract**, field by field.
- The published abstract says "19% less likely" where the 2023 WP said "19 percentage points less likely"; the paper's deliberately coarse phrasing ("AI lowered performance") is compatible with both, so no issue arises.

**Verdict: RESOLVED — and better than the author's own claim.** The author called the published-version check "not complete"; I completed it. All three transported figures (12.2% more tasks, 25.1% faster, performance decline outside the frontier) survive into the published Organization Science version. The publisher-page inaccessibility that stopped the author is circumvented by the Crossref-deposited abstract, which is the publisher's own record. My round-1 open question 5 is closed. (The bib's Crossref-derived bibliographic data was already verified in round 1.)


---

## Unit 8 — Part B(a): legal/tax citation spot-checks (primary sources, this round)

Author's claim: every legal/tax citation checked at primary source; "none incorrect, eight imprecise, all eight fixed." I checked the following load-bearing items myself (all fetched this round unless noted; access level: full statutory text via Cornell LII unless stated).

1. **26 U.S.C. §174A (R&E expensing)** — M 3.11 Remark 2, printed p.28; bib at refs_paper1.bib. LII full text: (a) "there shall be allowed as a deduction any domestic research or experimental expenditures which are paid or incurred… during the taxable year" (✓ "deducted when incurred"); (c)(1)(B) "amortization deduction… ratably over such period of **not less than 60 months** as may be selected by the taxpayer" (✓ "at least 60 months"); LII effective-date note: P.L. 119-21 applicable to amounts "paid or incurred in taxable years beginning after December 31, 2024" (✓ the bib's applicability note). **Verdict: accurate and precise.**
2. **26 U.S.C. §168(k) (100% bonus depreciation + exceptions)** — same Remark 2. Verified: LII amendment notes show P.L. 119-21, title VII, §70301 substituted "100 percent" for "the applicable percentage"; §70301(c) effective-date note: "the amendments made by this section… shall apply to **property acquired after January 19, 2025**" (✓ the paper's "acquired after 19 January 2025"); (k)(7) heading is "Election out," operative by class of property (✓ elect-out); (g)(1)(A): ADS applies to "any tangible property which during the taxable year is **used predominantly outside the United States**" (✓); (k)(2)(D): "Exception for alternative depreciation property" — qualified property excludes ADS property (✓). **Verdict: accurate and precise** — a four-cite chain (168(k), (k)(7), (g)(1)(A), (k)(2)(D)) all verified verbatim.
3. **26 CFR 1.168(k)-2(b)(2)(ii)(B)** — LII full text: paragraph (b)(2)(ii) "Property not eligible for additional first year depreciation deduction," item **(B)** "Required to be depreciated under the alternative depreciation system of section 168(g) pursuant to section **168(g)(1)(A)**, (B), (C), (D), (F), or (G)…" — the regulation paragraph letter is correct for the foreign-property exclusion. **Verdict: accurate and precise.**
4. **IRS Notice 2026-11** — fetched from irs.gov/pub/irs-drop/n-26-11.pdf: "Interim Guidance on Additional First Year Depreciation Deduction under § 168(k)," Notice 2026-11 (interim guidance pending proposed regulations). Title and subject match the bib entry. **Verdict: accurate.**
5. **CAMT cites (26 U.S.C. §55(b)(2)(A), §59(k), §11(b))** — supp tax-parameter table (printed p.~50). LII: §55(b)(2)(A): "the tentative minimum tax… shall be the excess of (i) **15 percent of the adjusted financial statement income** for the taxable year (as determined under section 56A)" (✓); §59(k)(1)(B)(i): AFSI average for the 3-taxable-year period "exceeds **$1,000,000,000**" (✓); §59(k)(1)(B)(ii)(II): for a corporation described in paragraph (2) (foreign-parented multinational group), own average AFSI "**$100,000,000 or more**" (✓ — the supp's "$100 million for a US member of a foreign-parented group whose group income exceeds $1 billion" is exactly this). §11(b) 21% standard (bib note; not re-fetched). **Verdict: accurate and precise.**
6. **SOX §404 (15 U.S.C. 7262)** — M 8.5, printed p.70. LII: (a) Commission rules require an annual-report internal-control report containing **management's assessment** (✓); (b) auditor attestation, with Pub. L. 112-106 (JOBS Act) §103 having inserted "other than an issuer that is an **emerging growth company**" (✓); (c) "Exemption for smaller issuers" — (b) does not apply to issuers that are neither "large accelerated filer" nor "accelerated filer" (✓ — so the paper's "accelerated or large accelerated filer that is not an emerging growth company" is precisely supported). **Not verified by me:** the "newly public company's first annual report need not contain management's assessment" clause (the SEC transition rule was not identified/accessible in my fetches; low load). **Verdict: accurate; one sub-claim access-limited.**
7. **GAO-23-105384 (9% effective-rate sensitivity case)** — supp tax table. GAO's own "What GAO Found" (direct fetch 403; retrieved via reader proxy): "The effective tax rates based on actual tax liability was **as high as 16 percent in 2014 and as low as 9 percent in 2018**" among profitable large corporations — the supp row quotes this verbatim. **Verdict: accurate.**
8. **Italy 24% (PwC Worldwide Tax Summaries)** — M 6 interest add-back. Fetched the cited PwC page: "The standard rates are as follows: **24% for IRES. 3.9% for IRAP**." — matches the bib note and the paper's 24%. (The page also notes a conditional FY-2025 IRES reduction to 20% for profits reinvested in fixed assets; the paper's 24%-standard/0%-variant treatment is unaffected. Minor, optional nit only.) **Verdict: accurate.**
9. **AS 2201 / Reg S-K Item 308** — done in Unit 2 (resolved; stale bib paragraph list flagged). NIST IR 8547 — verified in round 1, unchanged in the build.
10. **ASC 230-10-45-17(c) and (d)** — M 5.2/§6 (interest paid and income taxes paid as operating cash flows). The substantive proposition is standard US GAAP and correct. **I could not verify the sub-letters this round:** asc.fasb.org requires login; Deloitte DART (the paper's cited secondary source, whose bib note records "(d)" for interest paid) is now subscription-walled; the Wayback CDX API was offline at check time. Access level: bibliographic record + author's Deloitte-sourced note only. **Verdict: substance correct; letter-level precision unverified by me — flagged for an auditor with FASB codification access.**

Net for Unit 8: of the items I could check, **all were accurate and, where the author had tightened them, precise** (§174A, §168(k) chain, CFR letter, CAMT, SOX scope, GAO figures, Italy, NIST, AS 2201). Nothing incorrect found. One item (ASC 230 sub-letters) and one sub-claim (first-annual-report grace) remain access-limited for me.

---

## Unit 9 — Part B(b): new citations added this round (sampled at primary sources)

1. **Nei, Ruus & Indov (2026)** — new bib entry; verified field-by-field against the Crossref record (Unit 1). RESOLVED.
2. **Wood (1975) "A Theory of Profits" (CUP) and Wood (2025) "A theory of profits fifty years on" (CJE 49(5):1073–1103)** — new in M 1/M 2.1 (tangency lineage). Crossref DOI 10.1093/cje/beaf036 verified exactly (title, journal, 49(5), pages, 2025, author Wood). The 1975 book's bib note records catalog verification ("viii and 184 pages"); I did not re-check the catalog. The M 2.1 use ("Wood (2025) revisits Wood's frontier… its value-maximizing point… sets the frontier's slope equal to value per dollar of sales") is a content claim about a paper I have not read (access: Crossref record only) — plausible given the title, but **not verified**; low load (one lineage sentence). No nonexistent-work or misattribution signs.
3. **Hokstad & Rausand (2008)** — now carries DOI 10.1007/978-1-84800-131-2_39; Crossref verified ("Common Cause Failure Modeling: Status and Trends", Handbook of Performability Engineering, 621–640, Springer) and the printed bib note now states the abstract's beta-factor claim — a strengthening over round 1, where I had this entry at "bibliographic record only."
4. **dei:EntityPublicFloat (S12.1)** — the XBRL element name verified against the SEC's own frames API (taxonomy `dei`, tag `EntityPublicFloat`, "Entity Public Float"; the frames query returns data, e.g. 4,357 entities for CY2024Q2I). The retrieval description (SEC XBRL frames, 3 Nov 2026, cover-page float) is consistent with how that element works.
5. **Bending Spoons 424B4 cite (printed bib "2026b")** — verified on EDGAR: 424B4 filed 2026-07-01, accession 0001104659-26-079884 (tm2613674-14_424b4.htm) — matches the printed URL fragments. F-1/F-1/A verified in round 1.
6. **Stress-test methodology (S10)** — Latin hypercube, vertex search, Sobol indices are used without bibliographic citations (the method detail lives in notes/mc_claims_method.md). This is standard simulation vocabulary; the absence of method cites (e.g., McKay et al. 1979; Sobol 2001) is a **minor completeness note, not an error** — nothing is attributed to a source that does not support it.
7. No nonexistent works or misattributions found in the sampled set. Items I could not check: Wood (1975) catalog data; Wood (2025) content claims (abstract not retrieved this round); Deloitte DART quotes inside the three Deloitte bib notes (subscription-walled).

---

## Unit 10 — Part B(c): new abstract's source-touched claims

The rewritten abstract (main p.1) contains **no named companies** (no Palantir, Bending Spoons, CoreWeave) and no named practitioner sources. Its only source-adjacent claims are: "the two to three points of margin investors' screens use" — consistent with the BVP Rule of X record I verified live this round (≈2–3× long-run; ~2× private, 2–3× public) — and the sample description ("SEC filings as first reported by 284 software companies, 2010–25"), which R-C's number checks cover. The Palantir 155 and Bending-Spoons examples now live in the body, where I verified them in round 1 against the SEC exhibits. **Verdict: abstract is clean on sources; no new factual source claims introduced.**

---

## Unit 11 — A.6 search-protocol sentence (accuracy assessment; row GLM-20 belongs to R-B)

New A.6 (printed p.~81): "The statements that we found no prior study of a kind (Sections 2 and 1) rest on web searches by the literature agents and the outside reviewers, with each candidate checked at Crossref, RePEc or the publisher; **no log of databases and queries was kept, so they are bounded by those searches**."
- Accurate? Yes as a description: the method class, the verification route, and the no-log limitation are all stated, and my own round-1 experience corroborates the picture (my searches that found Nei et al. were Crossref-based; the author's log shows landing-page checks). The sentence does **not** state the date(s) of the searches — the one component of my round-1 acceptance test still missing.
- Adequate? The hedge "bounded by those searches" is the honest load-bearing part, and the Nei et al. episode is a live demonstration of why it is needed. With the disclosure, the negative-existence claims are properly bounded claims rather than assertions. **Assessment: accurate and adequate; minor residual (no search date).** GLM-20's row verdict is R-B's to render.

---

## Unit 12 — Coverage, access levels, what I could not check

**Verified this round (access levels):** full statutory/regulatory text — 26 U.S.C. §§174A, 168, 55, 59 and 15 U.S.C. 7262, 26 CFR 1.168(k)-2, IRS Notice 2026-11 (all via Cornell LII/irs.gov, full text); AS 2201 (Wayback of the PCAOB page, full standard text); AFL published abstract page (full landing page); Vista article (live, full); McKinsey **blocked** (all routes, both rounds); INFORMS/Deloitte DART/FASB ASC **login-walled**; GAO "What GAO Found" (reader proxy of the primary page); PwC Italy (live, full); Crossref records (Nei, Wood 2025, Hokstad & Rausand, Dell'Acqua abstract deposit, Ge & Huang); SEC EDGAR (Bending Spoons 424B4/F-1/6-Ks; dei:EntityPublicFloat frames API); new PDFs (M 1, M 2.1–2.4, M 8.5, supp S9/S10/S12.1 tables, A.6, bibliography).

**Could not check:** (i) McKinsey Roche & Tandon content (blocked both rounds — Unit 6); (ii) ASC 230-10-45-17 sub-letters and the newly-public-company §404(a) grace rule (paywalled; flagged); (iii) Wood (2025) content and Wood (1975) catalog details; (iv) Svanberg et al. full text (SSRN, unchanged from round 1); (v) Deloitte DART quoted texts inside bib notes; (vi) Lean-formalization claims (S4) and all numbers (other specialists).

**Part A verdicts:** F3 resolved; M13 resolved (+stale AS 2201 bib paragraph list, minor, new); M14 — I accept the author's "not valid (reviewer error)" classification (my own AFL fetch reproduces the author's evidence; the paper's 1,756 matches the published version); M16 partly resolved (Vista link now live — verified; δ_M sensitivity adequately covered by Table S17 + S10 joint box); GLM-15 resolved; GLM-17 partly resolved (verification record exists and is specific but not independently checkable by me; proposal to put the article's own numbers in the bib note); GLM-18 resolved (I completed the published-version check via the Crossref-deposited abstract — all three figures survive).

**Part B:** legal/tax spot-checks — 9 items verified accurate (most precise where the author tightened them); nothing incorrect found; two items access-limited. New citations sampled — none nonexistent or misattributed; minor completeness notes (no method cites for Latin hypercube/Sobol; Wood 2025 content unverified). Abstract clean of company claims. A.6 search-protocol sentence accurate and adequate.

**Model-identity disclosure:** repeated from the top of this report — all panel members and the author's drafting agents are LLMs; I am a separate context of the same LLM family as the Lead (GLM glm-5.3 via DeepSeek Harness; the author addressed the panel as "GLM 5.3 (high effort)"). Not independent human experts; not independent model-family evidence. Restricted materials (paper1_v4/ outside response_glm.md, author_reviews/ outside glm_5_3_high/, response_to_outside_reviews.md) were not opened; the excluded registrant was not named.
