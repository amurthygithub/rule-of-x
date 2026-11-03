# Executive pressure-test panel, round 2: Paper 1, v2

**Paper:** "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation", v2, October 2026 (`paper1_v2.pdf`, 77 pages; `supplement_v2.pdf`, 44 pages; `response_to_reviewers.md`).
**Round 1:** `notes/reviews/paper1_v1/panel_executives.md` (read first).
**Panel date:** 29 October 2026. No repository file was edited; this report is the only file written.

**Method.** The same eight roles, each argued from its own incentives. I read the whole main text except the reference list and the literature review (skimmed), and in the supplement Remark S1, Section S2, S5, the S6 limitations, Tables S5 to S7. Locations are M (main paper) or S (supplement) with the printed page. Three practical facts were checked on the web (Appendix B); every other number is the paper's own, or my arithmetic from the paper's tables, marked "reviewer arithmetic". The panel is one agent playing eight roles, so it is structured self-critique, not eight independent executives.

**Status labels for round-1 points.** *Resolved*: the paper does what the round-1 report asked or something equivalent. *Partly resolved*: part of it is done; the row says what is left. *Not resolved*: no change in the paper. "Matters?" is my judgement of whether the open part matters to a practitioner reader.

---

## 0. Overall verdict

v2 is a more honest paper than v1 and a better research paper. The 7-to-13 weight is withdrawn, the 40-to-156 horizon is gone, the Bending Spoons double charge is fixed, the own-versus-rent compute threshold is corrected (16.5% at 5% market growth, 49.5% at 15%), and the accountability floor is now a pass-fail standard with a diversity rule that a board can follow.

It is still not a document we would circulate to a board or a CFO team for planning. The practitioner layer was almost untouched: of the 18 executive-panel items, none is resolved, 8 are partly resolved and 10 are not resolved (I agree with the authors' own counts of 0, 8 and 10). Three problems matter most:

1. There is no go/no-go rule. The paper's "gains first exceed the dip after about 4 years" is a flow crossover; cumulative payback is about 7 to 8 years (reviewer arithmetic from Table 5), and the paper never says what a sponsor should do with that.
2. The "central" execution case became more optimistic in v2 through a change of definition. The 0.70 success probability is BCG's 74% of transformations that "created some value"; BCG's own success rate is 30%. It is paired with a 0.67 realized share that the cited source gives only for successful transformations.
3. The levers-by-position section is not a rule a CFO can apply. At the weight the firm's own spending reveals, it ranks "selling cost versus G&A cost", which any CFO already knows; the non-trivial part depends on a weight the paper itself says the data cannot identify.

We add 24 new findings: 5 major, 15 moderate, 4 minor (Section 6).

**Top five issues.** N-1 (no go/no-go; 4 years is not payback), N-2 (central execution inputs), N-3 (levers table not actionable), N-4 (no executive entry point, no typical-firm view), N-5 (no "how not to use these numbers" box).

| Role | Usefulness in round 1 | Usefulness now | One-line reason |
|---|---|---|---|
| CEO / COO | Medium | Medium | Can repeat the 31% threshold and the 56/60/66 path with caveats; still cannot place his own firm or tell which regime applies |
| CFO | Medium | Medium | Weight trap removed, M&A charging fixed; still no payback rule, no worked firm, no deferred-revenue case |
| CHRO | Low | Low to medium | Speed-limit logic grounded and ownership paragraph useful; no definitions, no people plan, no guardrail |
| CIO / CISO | Medium | Medium | Retest double count removed, diversity rule clear; common mode too narrow; ITGC cost out of line with own source |
| Chief product officer | Low | Low | No seat compression, no R&D or support lever, product inference not separated from internal compute |
| Head of transformation | Medium | Medium | Execution model is the best operator content; "central" is optimistic by definition shift; no go/no-go |
| Audit committee chair | Medium | Medium | Framing right; threshold calibration is knife-edge; no KPI card, no misuse box |
| General counsel | Low | Low to medium | Bending Spoons wording much better; licence ambiguity and unpublished dependence remain |

---

## 1. Role verdicts

### 1.1 CEO / COO

I told the board in round 1 that I could use three things: the bridge, the stage priorities and the cap on AI promises. Now I can quote two numbers with a caveat: the full-automation threshold of about 31% market growth (27 to 51% over the credible compute range) and a central path of 56, 60 and 66 for an exceptional firm. The week I would be embarrassed by "Rule of 156 by 2028" is gone.

What I still cannot do is place my firm. Every headline is for an exceptional firm (13 firm-years of 7 firms, M p.53) or for a hypothetical fully automated one (Table 4, M p.51). There is no row for a typical $1 to 5 billion firm, so I cannot see my distance to the ceiling. The ceiling itself is too loose to police a plan: 84 points at 15% market growth will not reject a management plan of 55. What would discriminate is the distance between my intercept and the full-cost target. I also get no test for which world I live in. The paper says my ceiling is 74 at 5% market growth if prices hold, and that free entry pulls the competitive score down to a few points plus rents (M pp.23, 52). That gap is the strategic question, and there are no indicators (gross retention, price realization, win rates against AI-native entrants) to answer it. Seat compression is still missing from the AI map (M Table 1, p.24), and market growth is the largest swing in the paper's own tornado (58 to 83 in 2036, Table 6).

### 1.2 CFO

Credit: the 7-to-13 weight is withdrawn, so I do not have to explain it away. The acquisition section no longer charges financing twice (M Remark 4, p.44), and the own-versus-rent rule is clean. Section 4.6 (M p.36) gives me the four bases for 2023 to 2025: medians of 12.0 (GAAP), 26.4 (adjusted), 29.2 (free cash flow before SBC), 15.3 (after SBC).

What stops me using it:
- **No payback.** I get "gains first exceed the dip after about 4 years" (M p.54). That is when the annual gain passes the annual dip. Cumulative break-even is about year 7 undiscounted and year 8 at 9.34% (reviewer arithmetic from Table 5). No NPV, no P&L-format output, no instruction on what to fund.
- **No worked firm.** I asked for the median $1 to 5 billion firm-year; the bridge is for the whole core sample (median SBC 12.3% of revenue, M p.36, against 14.8% for $1 to 5 billion firms in the round-1 computation).
- **No deferred-revenue case.** Table 4 has k of 0, 0.5 and 1.5 only. With prepaid billing (k = -0.3) the 31% threshold becomes about 24%, reviewer arithmetic (N-11).
- **Accountability floor of 0.23%** looks low against my audit fee plus SOX program; the paper's own KPMG source gives an average program budget of $2.3 million before audit fees (N-13).
- **The levers table** restates two cost lines I already know (N-3).

### 1.3 CHRO

The speed-limit statement, that no program moves faster than its scarcest capacity (M Prop. 6(c), p.30), is now grounded on a survey (WEF 2025), disclosed restructurings and exit rates (S p.30), and the ownership paragraph is useful for a board talk: a public firm holding a one-point dip realizes 32% of the benefits by 2036 instead of 41% (M p.55). The 0.15 strategy-change hazard no longer drives the pace, which removes the weakest number.

Still missing: definitions of "affected employee", "embedded" and "process"; a people plan (roles redesigned, redeployed, exited; reskilling hours); retention grants, which are SBC and hit the paper's own preferred margin; any statement that "full automation" is a bound and not a headcount target, in a paper that has a section titled "What to track if headcount falls" (M §8.4, p.61); and legal minimums for workforce-affecting change. The central 10% a year applied to 48 identical processes makes the 41% mostly the arithmetic of that 10% (N-15, N-16).

### 1.4 CIO / CISO

The retest of IT general controls is now priced at control testing only ($24,000 per model upgrade, M p.72), which removes a double count with revalidation. The diversity rule is stated clearly: stacking layers on one model provider addresses independent failures, not common-mode ones.

Open: common mode is modeled across model providers only (M Assumption 7, p.26); a shared identity provider, EDR agent or cloud region defeats every vendor-diverse layer at once, as the July 2024 CrowdStrike outage showed (N-19). The ITGC line per AI application is $204,672 a year, against a paper reference of $80,000 and a KPMG-derived $16,000 to 57,500 per system (S p.35), and "15 applications take the floor to 0.5%" is quoted in the main text on that basis (N-13). Agent identities and tool permissions do not scale the ITGC term. Table 8 (M p.73) still cannot be read in two minutes; it needs a "what to budget" line per floor.

### 1.5 Chief product officer

The best operator diagnostic in the paper is unchanged and useful: among firms growing 40 to 60% a year, selling and marketing explains 29.4 of the 41.3-point margin gap between top-decile and typical firms (M p.41). Gross profit per dollar of compute (M §8.4) is the right extra metric.

Still missing: seat compression and AI-native entry (the sign of the market-growth effect for a seat-priced vendor is open); pricing power gets one sentence (lever 4, M p.56); the levers table ranks only selling and G&A, with no R&D or engineering-productivity lever and no support cost, which are my two largest AI targets (N-3). The 6% compute share is compute for internal automation. My margin risk is product inference in cost of revenue (ICONIQ: AI product gross margin 45% in 2025), which the paper treats as an infeasible "high-compute" case (N-12).

### 1.6 Head of transformation

The attainable-frontier logic is still the most operator-relevant content: sequence by scarcest capacity, manage the embedding probability because each embedded process costs 1/p attempts, report the in-flight dip so that execution is not read as weakness. The slow case is now in the tornado (Table 6). The central pace was re-grounded.

But the re-grounding changed what "central" means. The 0.70 is not a success rate (N-2). The program is 48 identical processes, so the ramp is linear and prioritization, which the paper's own Proposition 6(d) recommends, never shows (N-15). "Attempt", "works" and "embedded" have no operational definitions (N-16). And there is no go/no-go (N-1). I can use the structure; I cannot use the numbers.

### 1.7 Independent director, audit committee chair

The framing is right: the accountability floor is a pass-fail standard, no all-AI design on one provider passes under the example parameters, and the officers who certify remain people (M §8.5, p.61). That is the guardrail I asked for, in substance.

Concerns: (1) the 5% "remote" threshold is grounded on adverse 404(b) attestation rates, which measure how often controls are judged ineffective, not the probability of an undetected material misstatement; and it is set so that the all-human reference design passes by a hair (4.98% against 5%) (N-14). A director reading "5% a year" will hear a tolerance. (2) The bottom-up example has one control objective. (3) No KPI definition card (SEC Release 33-10751); no statement of which bridge items are audited (none). (4) No "how not to use" box. (5) Numbers still come from a companion paper that is "in preparation".

### 1.8 General counsel

Better: the Bending Spoons text now says the company does not report the score, uses its own unaudited organic measure, quotes the material-weakness risk factor, and labels the fully charged figure a lower bound (M pp.45-48). The raw bibliography key is fixed.

Still open: page 1 says commercial use of the paper or software needs written permission; the sentence that firms may apply the ideas is only in Table 9 on page 75, not in the footnote the response cites (N-20). There is no use-of-paper or forward-looking statement, though §8.3 (M p.60) tells firms to compute the score "as this paper does", which is an invitation to publish a non-GAAP KPI without Reg G or Release 33-10751 guidance (N-5). No competing-interests statement (the author declined, M Table 9); the label "Independent researcher" with no statement invites the question. Numbers in §7.2 and §7.3 are sourced to an unpublished companion paper, while page 4 says the paper "does not depend on it". EU AI Act and Product Liability Directive dates are in Table S7 but not in the cost line they affect (N-18).

---

## 2. Round-1 points: status in v2

### 2.1 Executive-panel items EX-1 to EX-18

| ID | Round-1 ask | Response says | Panel status | What the paper shows (location) | Matters for a practitioner? |
|---|---|---|---|---|---|
| EX-1 | Budgetable decision rules and a worked median $1-5B firm | Partly | **Partly resolved** | Prop. 9 and Table 7 (M pp.57-59) rank four levers by position; hurdle for capital-for-labor is in the last column (g + delta); own-versus-rent in Remark 7 (M pp.72-74); acquisitions in Prop. 8(a) (M p.43). No consolidated rule list, no worked firm; positions are whole-core-sample medians; level-dependent columns use X-hat minus k = 11, which §5.4 says is not identified | **Yes, major.** The largest single gap (N-3, N-4) |
| EX-2 | Decision weight conditional on attribution; payback translation | Partly | **Partly resolved** | Withdrawn and bounds by method reported (M §5.4, p.40): 0.05 to 10.1. That is stronger than asked. But §8.1 (M p.59) re-imports the median ratio 3.02 as if it were the weight, and Table 7 uses X-hat minus k = 11. No payback translation; the CAC-ratio route (1.30 over alpha = 2.9 to 5.2) is only in S Table S7 (p.32) | **Yes, moderate** (N-8) |
| EX-3 | Score bridge on the practitioners' basis | Partly | **Partly resolved** | Bridge of four bases for 2023-25 (M §4.6, p.36), interest and cash-tax bridge (S Table S6, p.29), Palantir 155 to 140 (M §8.3, p.60), Bending Spoons bridge (M Table 3, p.48). Not for $1-5B firms; no organic or acquisition-charged rows for ordinary firms; no KPI definition card | **Yes, moderate.** CFO and audit chair want it for their peer group (N-4, N-5) |
| EX-4 | Re-ground execution pace; state the go/no-go implication | Partly | **Partly resolved** | Re-grounded (M p.53): success 0.70/0.80, realized share 0.67/0.85, capacity 10% [5, 22]; slow case in Table 6 and text (M p.56); revealed 2022-24 pace of 8.2 points reported (M p.54). No go/no-go. The re-grounding is more optimistic than the cited sources (N-2) | **Yes, major** (N-1, N-2) |
| EX-5 | Central case with tornado; firm-specific G; Rule of 1000 out of the main text | Partly | **Partly resolved** | Central path and tornado done (M Tables 5-6, pp.54-55); Rule-of-1000 arithmetic moved to S5 (S p.24), but the Rule of 1000 is still in the abstract, intro (p.3), §7.2 (p.52) and conclusion (p.62). G held at 12.7% for all firms; firm-specific G not used | **Yes, moderate** (N-9) |
| EX-6 | Table 10 (now Table 4): typical-firm row, k = -0.3 column, tax, fee, security-baseline caveats | Not done | **Not resolved** | Table 4 (M p.51) unchanged in structure. §7.2 (M p.50) still says the tax range runs from the 15% CAMT and fees are card-processing fees; GAAP effective-rate sensitivity (GAO, 9 to 16%) added | **Split.** Typical-firm row and k < 0 column: yes (N-4, N-11). Tax, fee, security caveats: threshold moves little (tax 28 to 33%; fees about 0.8 points; floor band 29 to 32%), but each needs one sentence for CFO credibility (N-11) |
| EX-7 | Ground the accountability floor in disclosed fees and observed control failures; add a guardrail | Partly | **Partly resolved** | Floor is pass-fail (M Prop. 5, p.26); remote threshold tied to adverse attestations (M p.72); guardrail in substance (M §8.5, p.61). 0.14% direct audit and 404 cost unchanged (M p.72); ITGC not scaled by agents; Dropbox grounding not added | **Yes, moderate** (N-13, N-14) |
| EX-8 | "How not to use these numbers" box | Not done | **Not resolved** | None. Caveats exist in text (M §7, §8.6) but not in abstract or conclusion | **Yes, major** (N-5) |
| EX-9 | Licence, competing interests, unpublished dependence | Partly | **Partly resolved** | Response cites the title-page footnote, but the footnote (M p.1) has no "ideas are free" sentence; it is in Table 9 (M p.75) only. Competing interests declined. Companion paper still cited for load-bearing numbers (M pp.50, 56; Remark 6) | **Yes, moderate** for GC (N-20) |
| EX-10 | Plain-language pass, executive summary, glossary | Not done | **Not resolved** | None. Title, abstract and Table 4 headers unchanged in style | **Yes, major** (N-4) |
| EX-11 | Seat compression as a negative G channel | Not done | **Not resolved** | Table 1 (M p.24) has no row; lever 4 (M p.56) one clause | **Yes, moderate.** G is the largest 2036 swing (N-10) |
| EX-12 | Common mode beyond model providers | Not done | **Not resolved** | Assumption 7 (M p.26), Lemma 6(e) (M p.71) | **Some.** Matters for the diversity rule's design guidance, little for the ceiling (N-19) |
| EX-13 | Labor-law minimums (WARN, EU 98/59/EC) | Not done | **Not resolved** | None | **Little for the central case** (1.25 years exceeds the legal minimums); some for the fast case (1.0 year) in works-council jurisdictions (N-16, N-18) |
| EX-14 | Regulatory dates in Definition 3 | Not done | **Not resolved** | Dates in S Table S7 (p.35) only | **Some.** The AI-compliance line (0.1 to 0.4%) is built on voluntary attestations (N-18) |
| EX-15 | Competition: entrant surplus draws on incumbents' headroom | Not done | **Not resolved** | Prop. 8(e) (M p.44) covers acquisitions in served markets only | **Yes, moderate.** The free-entry versus fixed-price regime is the decisive question and no test is given (N-10) |
| EX-16 | Leadership hazard: range and sensitivity | Partly | **Partly resolved** | Disruption factor removed from the embedding probability as a double count (M p.53); nu_D kept for timing, still class d (S p.31); no sensitivity row | **Little now.** The dominant unsourced term no longer drives the pace |
| EX-17 | Hallucination rates vary with the judge | Not done | **Not resolved** | Main text silent; S Table S7 (p.33) shows spread by model and task (1.8 to 24.2%; 17 to 33%) but not judge dependence | **Little.** Threshold moves 30 to 36% across the full error range (M p.51) |
| EX-18 | Spend ratio with S&M plus a share of R&D | Not done | **Not resolved** | Ratio still S&M only (M p.40) | **Little for the ratio now the weight claim is withdrawn; yes for Table 7**, which omits R&D (N-3) |

**Count (panel view):** Resolved 0; Partly resolved 8 (EX-1, 2, 3, 4, 5, 7, 9, 16); Not resolved 10 (EX-6, 8, 10, 11, 12, 13, 14, 15, 17, 18).

**On the response's claims.** Two rows describe more than the paper does. EX-9 cites the title-page footnote for the licence clarification, which is not there. EX-1's "ratio test that does not need the level of the decision weight" is true of Prop. 9(b) but not of the Table 7 columns that carry the numbers (switch weights, Gi), which use X-hat minus k = 11.

**The not-done items that matter.** EX-8 and EX-10 (box, summary, glossary): decisive for a practitioner reader. EX-6's typical-firm row and negative-k column: they change the number a CFO would act on. EX-11 and EX-15: they concern the largest sensitivity and the regime question. EX-12, 13, 14, 17, 18: worth a sentence each; none moves a headline.

### 2.2 Role-level checks from the round-1 tables

| ID | Round-1 point (short) | Status | Note (location) |
|---|---|---|---|
| C1 | State the 42% threshold against the served market | Partly resolved | Now 31%; says "its market" (M p.3, p.52); served market not named |
| C2 | Single 12% market growth in the anchor | Partly resolved | 12.7% held, varied in tornado; firm-specific G not used (M p.53) |
| C3, C4, F5 | Palantir 155; Rule of 30; WACC 9.34% | Confirmed in round 1; unchanged | M pp.1, 60; S p.35 |
| C5 | Report the before-SBC basis | Resolved | M §4.6, p.36 |
| C6 | Fall of the top tail has two readings (supply of growth versus cost of capital) | Not resolved | "Interest rate" does not appear in the paper; M p.57 still concludes "supply of growth opportunity, rather than willingness" (N-6) |
| C7 | Central path about ten times slower than revealed pace | Partly resolved | Revealed 8.2 points beside the path (M p.54); explained as "cost programs of every kind"; label unchanged |
| C8 | Entrant surplus drawn from incumbents | Not resolved | N-10 |
| F1, F2 | Weight depends on attribution; net bias sign | Resolved | Withdrawn; netting gives 0.99 (M p.40); but see N-8 |
| F3 | Reconcile with CAC payback | Not resolved in main text | CAC route in S p.32 only |
| F4, F6 | CAMT threshold; card fees | Not resolved | M p.50 |
| F7 | k = -0.3 column | Not resolved | S Remark S1(c), p.1 only (N-11) |
| H1 | Capacity grounded on exits | Resolved in substance | WEF + restructurings + exits bracket (S p.30); WEF measures training need |
| H2 | Capacity exogenous and constant | Not resolved | Assumption 8 unchanged |
| H3, H5 | Legal minimums; AI Act employment uses | Not resolved | N-16, N-18 |
| H4 | Disruption rate mostly class d | Resolved in substance | Factor removed from p_emb (M p.53) |
| S1 | IANS is all-industry | Partly resolved | Scope stated in S p.35; no software adjustment (M p.50) |
| S2 | Common-mode scope too narrow | Not resolved | N-19 |
| S3 | Hallucination judge dependence | Not resolved in main text | S p.33 |
| S5 | "Capacity binds" rests on class d inputs | Partly resolved | Stated as conditional (M p.60); build and run capacity still absent (N-15) |
| P1 | Pass-through of inference cost | Partly resolved | phi = 0.5, 0.7 added (M p.52); consumption pricing not modeled |
| P4 | Seat compression | Not resolved | N-10 |
| T1 | 0.54 measures PoC attrition | Resolved by relabelling as slow case | But see N-2 |
| T2 | 0.80 is a self-reported best case; unconditional 0.30 is the central analog | Not resolved, and worse | Central moved up to 0.70 (N-2) |
| T4 | Decision implication missing | Not resolved | N-1 |
| T5 | "48 processes" undefined | Not resolved | Table 8: $0.5 million each; no FTE or revenue meaning (N-16) |
| A1 | 0.14% direct audit and 404 cost too low | Not resolved | M p.72 (N-13) |
| A3 | 5% orders-of-magnitude check | Adopted as the threshold | N-14 |
| A4 | AS 2201 reading is the author's | Partly resolved | M p.27 says the standard "sets no number" (N-22) |
| A5 | KPI definition card | Not resolved | N-5 |
| L1, L5 | Licence; disclosure completeness | Partly resolved | N-20; Appendix B.3 is complete |
| L2 | AI-washing exposure | Not resolved | No use statement (N-5) |
| L3 | Regulatory dates | Not resolved in main text | N-18 |
| L4 | Named-company phrasing | Partly resolved | Bending Spoons wording corrected (M pp.45-48) |

---

## 3. Can a CFO or transformation lead at a $1-5 billion software firm act on it?

### 3.1 What can be used on Monday

1. **Basis and bridge.** Report the score on one stated basis with the bridge to the published number (M §4.6; the Palantir 155-to-140 and Bending Spoons examples are templates).
2. **Capital-for-labor hurdle.** Automate with owned capital only if opex saved per dollar of capital exceeds growth plus depreciation (M Cor. 2, p.16; Table 7 last column: 0.27 to 0.61 at 25% depreciation).
3. **Own versus rent compute.** Own only if the vendor markup exceeds 3.3 times market growth: 16.5% at 5%, 49.5% at 15% (M Remark 7, p.72).
4. **Acquired growth.** An acquisition enters the score at the weight X minus price per dollar of revenue; any purchase above one times revenue lowers the fully charged Rule of 40 (M Prop. 8(a), p.43).
5. **Cap on AI-margin narratives.** The threshold of about 31% market growth (27 to 51%) is a good reply to "Rule of 100 by 2028", provided it is quoted with its conditions (N-7).
6. **Control design.** At least one human or a second provider on every key control that AI performs, and an ITGC line for each AI application in scope (M Prop. 5, Remark 6).
7. **Execution.** Treat the embedding probability as the program KPI; report the dip separately; launch only what the scarcest capacity can carry (M Props. 6-7).
8. **Screening versus spending.** Use the Rule of 40 to screen firms, not to set growth spend (M p.63).

### 3.2 Levers by position (M §7.5, Prop. 9, Table 7)

This is the section the CFO would turn to for "what do I automate first", and it does not deliver.
- The three value columns of Table 7 are 10% of the S&M share, that share divided by alpha, and 10% of the G&A share. At the revealed weight the ranking is therefore "which cost line is bigger", and S&M exceeds G&A at all six positions.
- The non-trivial result depends on the weight: switch weights of 5.7 to 9.1 sit above screening weights of 2 to 3 (overhead first) and below the revealed weight of 11 (growth engine first), and §5.4 says X minus k ranges from 0.1 to 40 (M p.59 admits this).
- The Gi and switch-weight columns are artifacts of imposing one ratio (3.3) on every position: the near-frontier elite gets Gi = 36 - 20/3.3 = 30%, the stalled firm -7.4%.
- Gains are compared as flows at one date; growth-engine gains vanish at saturation and overhead cuts last, but nothing nets them into value. The conclusion's stage rule (fast grower: growth engine; mature: overhead, M p.63) conflicts with Table 7, which ranks the growth engine first even for the stalled firm (growth 2%).
- R&D and cost of revenue are not in the table, though together they are about half of revenue for a typical software firm and the main places AI is applied.
- Positions are cell medians of the whole core sample, not $1 to 5 billion peers.

What would work: a three-step test on inputs the CFO owns (N-3).

### 3.3 Go/no-go logic for programs

Absent (the response says "No payback or go/no-go threshold"). The paper has the parts: capacity limits, embedding probability, in-flight dip, ownership effect on pace. It never combines them into a decision. Under central execution the whole program does not pay back within a five-year sponsor horizon; the paper should say so and say what follows (fund the waves with the highest gain per affected employee, or raise the embedding probability first). See N-1, N-2, N-15.

### 3.4 Score bridge

Present in pieces, not as a bridge a finance team can reproduce. §4.6 gives four bases for the whole sample and a 4.8 to 5.2 point lift from adding back interest and cash taxes to the 95th percentile (S Table S6). Tables 3 and §8.3 give firm-level bridges for one serial acquirer and for Palantir. Missing: a bridge for the median $1 to 5 billion firm-year; organic and acquisition-charged rows for an ordinary firm; a KPI definition card (definition, calculation, why useful, consistency, recast rule); a statement of which items are audited (none); and treatment of quarterly year-over-year growth, which §4.6 says is not comparable with any annual basis.

### 3.5 Horizon central path (M Tables 5 and 6)

Useful as a scenario, but five things limit its use:
- It is for an exceptional firm. A typical firm's path is not given.
- The abstract's 66 in 2036 is the higher of two attributions (55 if none of selling and marketing buys growth), and §5.8 says only the second statement is a conclusion (N-7).
- Of the 66 points, 42 is the anchor intercept, 12.7 is market growth held at the sample median, and about 11 is automation (0.41 x (70 - 42)); the paper never says so (N-9).
- Market growth is the largest swing (58 to 83) and the paper gives no mapping from a firm's own data to G (N-9, N-10).
- Table 6 prints 117 (2028) and 92 (2036) in a table about the central score (N-7).

### 3.6 What is missing, what is confusing

Missing: a payback rule; a worked firm; a typical-firm row; the regime test; a deferred-revenue case; operational definitions; a KPI card. Confusing: two "central" cases; realized (41%) versus embedded (61%); "maximal score", "durable score", "ceiling", "threshold" and "bound" used for related but different things; the ranking in §7.5 flipping with an unidentified weight. All are covered in Section 6.

---

## 4. Clarity and hedging

**Abstract (M p.1).** Not readable by an executive. The second sentence still reads "Rule-of-40 and Rule-of-X lines are price lines whose tangency with it gives the maximal score: the intercept, plus market growth net of the capital it requires, plus a growth surplus that vanishes as market share saturates and, within one market, draws on a finite budget of share headroom". Further jargon: "verification hypothesis", "screening weights", "marginal value of revenue", "mature asset-light firm", "cash-basis score", "pass-through". The last sentence ("the limit is set by what stays scarce, not by what is automated") is good and should lead.

**Introduction (M pp.1-4).** The first page is clear. From page 2 it cites Propositions 2, 5, 6 and 7 and Remark 3 as if the reader had them, and introduces "decision weight", "screening weight", "growth surplus", "share headroom" and "embedded" without a plain definition. The six empirical findings are well written. The Bending Spoons paragraph (pp.3-4) is dense but fair.

**Conclusion (M pp.62-63).** First paragraph is readable. The "practitioners" paragraph is concrete and mostly right, but it asks the reader to "evaluate AI strategies by the parameters they move: the margin intercept, demand pull, capital intensity, pricing power, the accountability floor, the full-cost floors ... and the capacity to execute" without saying how to measure any of them.

**Jargon and unexplained symbols in executive-facing text.**
- Title: "Price Line" (M p.1); the term recurs on pp.1, 2, 9, 12.
- Abstract and intro: tangency, growth surplus, share headroom, verification hypothesis, screening weight, decision weight, embedded, Rule of 1000.
- §7.4 (M p.56): "R-infinity = m0 + (1 - k)G above 100" in the closing sentence on levers.
- §8.1 (M p.59): "alpha(X - k) > 1 - k" in prose.
- Table 4 (M p.51): column headers cc, f, amin, cfull, tau, G*; Table 5: m0, R*, R-infinity; Table 7: Gi, X0-double-dagger, (a/sigma-hat)^(1-alpha), g + delta.
- Table 8 (M p.73): c_sec, L_sec, xi_exp, H_cm, Y_fb, ū.

**Hedging.**
- *Correct and good:* "scenario, not forecast" on Tables 5 and 6; "conditional on the scenario compute share" next to every threshold; the withdrawal of the 7-to-13 weight; the statement that the cross-section does not identify any firm's own trade-off (intro p.2, §5.10).
- *Needs work:* the causal "because fast growers became scarcer" (N-6); "a fifth of a point less margin" without "across firms" and without the significance caveat in the abstract (N-6); "complete automation keeps a firm below 100" read as a law (N-7); 66 without 55 (N-7); the §8.1 example (N-8); the 5% threshold (N-14).

**What a board would misread.**
1. Table 4's ceiling as a target ("our ceiling is 84, so a plan of 55 is conservative").
2. The central path as a forecast, and Table 6's 117 as an upper end.
3. "5% a year chance of an undetected material misstatement" as an accepted tolerance.
4. "Full automation" as a headcount plan.
5. "The Rule of 40 understates us" (§8.1) as a licence to burn.
6. "The top of the distribution fell 12 points, so 40 is now top-decile and we can lower the bar" (the 2023-25 95th percentile is 43.9).
7. Bending Spoons' organic 22 to 44 and 160, or the lower bound of -16.5 next to 115.9, quoted in a competitor deck.

---

## 5. Practical accuracy: where the paper departs from practice

Items 1 to 9 are details in Section 6; items 10 and 11 were checked and are fine.

1. **Transformation success rates** (N-2): 0.70 is the share of transformations that created some value, not the success rate; BCG's success rate is 30%.
2. **Program shape** (N-15): AI savings are concentrated in a few functions; the central path assumes 48 identical processes and a linear ramp.
3. **Compute** (N-12): internal-automation compute and product-embedded inference in cost of revenue are conflated.
4. **SOX program size** (N-13): a floor built on one control objective, with direct audit and 404 cost below the paper's own source.
5. **"Remote" threshold** (N-14): an adverse-opinion rate is not a probability of undetected misstatement.
6. **Control types** (N-22): deterministic automated controls, the cheapest diverse layer in real SOX programs, are not in the design menu.
7. **Common mode** (N-19): shared identity, EDR and cloud dependencies.
8. **Statutory compliance** (N-18): the AI-compliance line is voluntary attestations; the EU AI Act Annex III and the PLD are outside it.
9. **Own versus rent compute** (N-21): silent on utilization.
10. **Checked, fine:** the US tax statements in Remark 2 (domestic R&E expensing for tax years beginning after 2024; 100% additional first-year depreciation for property acquired after 19 January 2025; 15-year amortization abroad), the AS 2201 paragraph A7 and Item 308(a)(3) readings, the emerging-growth and first-report exemptions, and the Sections 302 and 906 certification statements (M pp.24-25, 27, 61).
11. **Checked, fine:** the corrected Palantir arithmetic (93% growth plus 62% adjusted margin is 155; 140 on the GAAP margin of 47%).

---

## 6. New findings

Severity: **major** (changes what a practitioner should conclude or do, or blocks use); **moderate** (misleads or leaves a gap a specialist would catch); **minor** (presentation or small accuracy).

### N-1. No go/no-go rule, and "4 years" is a flow crossover, not payback
**Severity:** major. **Location:** M §7.3 p.54 (dip row, "gains first exceed that dip after about 4 years"); M §8.2 p.60; Table 5 p.54; response EX-4, D2.
**Issue.** The paper says that under central execution "realized gains first exceed" the in-flight dip after about 4 years. That is the year in which the annual gain passes the annual dip. From Table 5, the realized gain is the realized share times (target intercept minus anchor intercept): 7% of 22, 20% of 25, 41% of 28, that is 1.5, 5.0 and 11.5 points in 2028, 2031 and 2036, against a dip of 2.5, 2.8 and 3.1 points while the program runs. Reviewer arithmetic (piecewise-linear interpolation of those points, dip of 2.2 to 3.1 from year 0 to 11): the annual crossover is at year 4.0, matching the paper; cumulative break-even is at about year 7 undiscounted and year 8 at the paper's 9.34% cost of capital. A sponsor with a three-to-five-year horizon would not fund the whole program, and the paper does not say it (round-1 T4). There is no NPV, no minimum embedding probability for payback, no instruction on which waves to fund, and no P&L-format output (restructuring charges are excluded from non-GAAP margins but still hit the free cash flow after SBC that the paper recommends).
**Suggested change.** Add to Table 5 a payback block for slow, central and fast execution: annual crossover year, cumulative payback year, NPV at 9.34% as a share of revenue. Add the sentence: "Under central execution a sponsor with a five-year horizon would not fund the whole program; it would fund the waves with the highest score gain per affected employee." Compute the minimum embedding probability and capacity at which the whole program pays back within five years. Replace "first exceed" with "annual gains exceed the annual dip". Add a three-year (FY27 to FY29) P&L example for a $2 billion firm with restructuring charges shown separately from run-rate.

### N-2. Central execution inputs are more optimistic than their sources, and mislabeled in the main text
**Severity:** major. **Location:** M §7.3 p.53 ("survey rates of the success of transformations (Forth et al., 2020)"); S Table S7 p.30; M abstract p.1, intro p.3.
**Issue.** Table S7 states that the 0.70 "rounds down the 74% that created value" and lists BCG's zones: 30% win (target met, change sustained), 44% worry (some value, targets missed), 26% woe. I confirmed on the BCG page that its success measure is the 30% (Appendix B). The main text calls 0.70 a "survey rate of the success of transformations". The realized share of 0.67 is McKinsey's figure for successful transformations; "all others" realize 37% (same table). Pairing a probability that includes missed-target cases with a successful-only realized share counts the optimism twice. Like-for-like, 0.30 x 0.67 + 0.44 x 0.37 = 0.36 of targeted benefit per attempt, against 0.70 x 0.67 = 0.47 in the paper. Because the embedded share is linear in the embedding probability below the cap, the realized share by 2036 would be about 32% instead of 41% (reviewer arithmetic; illustrative, since the surveys cover whole digital transformations, not process-level AI attempts). The fast realized share of 0.85 matches no number in the cited row (67, 37, 74). In round 1 (T2) we said the unconditional rate of 0.30 was the closer analog of central execution; v2 moved central up from 0.54 to 0.70 and realized-by-2036 from 23% to 41%.
**Suggested change.** State in the main text what 0.70 and 0.67 are. Either adopt the like-for-like value (about 0.36) as central, or keep 0.70 and 0.67, call the case "favorable survey reading", and add the BCG-success reading (0.30) as a row in Tables 5 and 6. Rerun the 41%, 61% and 66. Source or drop 0.85. Add a sentence that both surveys measure whole transformations.

### N-3. The levers-by-position section is not an actionable rule
**Severity:** major. **Location:** M §7.5 pp.57-59 (Prop. 9, Table 7); M §7.4 p.56; M §9 p.63; S Table S7 p.32.
**Issue.** See Section 3.2: the value columns restate the S&M and G&A shares; the ranking flips on an unidentified weight; Gi and switch weights are artifacts of one imposed ratio; flows are not netted into value, so the conclusion's stage rule and Table 7 point in different directions for the stalled firm; R&D and cost of revenue are missing; positions are not $1 to 5 billion peers. The CFO's usable calibration, the CAC ratio over alpha (1.30/alpha = 2.9 to 5.2), is in Table S7 and not connected to the section.
**Suggested change.** Replace Table 7 with a three-step test: (1) inputs the CFO owns: S&M share, G&A share, R&D share, support cost, own CAC ratio and NRR; (2) the ratio test of Prop. 9(b), with threshold (G&A/S&M)^(1-alpha), and X-hat minus k set from own CAC ratio over alpha; (3) a value comparison that treats the growth-engine gain as transient (gain times its half-life) and overhead as permanent (gain over the discount rate). Add R&D and support rows. Drop the Gi column. Recompute the table for $1 to 5 billion firms.

### N-4. No executive entry point and no typical-firm view
**Severity:** major. **Location:** title and abstract M p.1; Table 4 p.51; Table 5 p.54; Table 7 p.58; response EX-1, EX-6, EX-10.
**Issue.** No summary, glossary or worked firm (EX-10, EX-1). The headline numbers describe an exceptional firm or a hypothetical fully automated firm. A CFO cannot compute her distance to the ceiling; and a ceiling of 84 at 15% growth is too loose to police a plan of 55. The paper's discriminating number is the gap between the firm's own intercept and the full-cost target, and nothing helps the reader compute it (the anchor inversion m0 = m + (1 - tax) x S&M + k x g is described only for the top tail, M p.53).
**Suggested change.** Add the one-page summary of Appendix A.1, a glossary (plain terms for price line, growth surplus, share headroom, decision weight, screening weight, embedded, durable score), and a worked example for the median $1 to 5 billion firm-year on panel_v3: growth, FCF margin before and after SBC, S&M, G&A, R&D, gross margin, SBC, capital spending; then durable score, implied intercept, gap to the central ceiling, capital-for-labor hurdle, and the Table 7 test. Add a row "typical $1-5B firm" to Table 4. Add a plain subtitle to the title.

### N-5. No "how not to use these numbers" box and no use-of-paper statement
**Severity:** major. **Location:** end of M §1 (p.4) and M §9 (p.63); M §8.3 p.60; response EX-8, RA-3.
**Issue.** Every round-1 role named a misuse. None is addressed in a box. v2 adds new misuse routes: 66 read as the central score when 55 is the other bound; the 31% threshold quoted without its 6% compute and k = 0 conditions; Table 6's 117; the §8.1 example on an earnings call; the 5% threshold read as a tolerance. §8.3 tells firms to compute the score "as this paper does", a non-GAAP KPI. The paper has no Reg G, Item 10(e) or Release 33-10751 paragraph (response RA-3: sources verified, paragraph not written).
**Suggested change.** Add the box in Appendix A.2 at the end of §1 and as the last paragraph of §9. Add a KPI definition card (definition, calculation, why useful, how management uses it, consistency, recast rule) and one sentence that nothing in the paper is investment advice or a forward-looking statement for any firm.

### N-6. Empirical headline claims are stated more strongly than the evidence
**Severity:** moderate. **Location:** abstract M p.1; intro p.3 ("Fifth"); §5.2 p.38; §5.3 p.39; §7.4 p.57; §9 p.62.
**Issue.** (a) "Fell ... as fast growers became scarcer" is causal. The reweighting attributes -7.9 [-17.2, -2.7] to composition and -4.1 [-9.7, +2.8] to within-bin change, so zero is inside the within-bin interval; the 95th percentile recovered to 51.4 in 2025; the decline survives a familywise correction at 10% only. §7.4 concludes the binding constraint is "the supply of growth opportunity ... rather than willingness to trade margin for growth". The cost-of-capital channel, which by the paper's own Prop. 2 and Lemma 5 lowers a firm's own weight and growth, is never mentioned: the words "interest rate" do not appear in the paper (round-1 C6). (b) "A point of growth came with about a fifth of a point less margin" appears in the abstract without "across firms, not any firm's own trade-off" and without noting that the sign does not survive the familywise correction (M p.3, p.39). A board will read "growth is cheap". (c) There is no sentence that the fall in the top of the distribution is descriptive and not a case for lowering the bar.
**Suggested change.** "...mostly because fewer firms grew fast; the same years saw a rise in the cost of capital that the model says also lowers growth, and the data cannot separate the two." "Across firms, not any firm's own trade-off; the sign is not statistically firm." "This is a description, not a case for lowering the bar."

### N-7. Headline scenario numbers can be misquoted
**Severity:** moderate. **Location:** abstract M p.1; intro p.3; Table 5 p.54; Table 6 p.55; §7.2 pp.49-52.
**Issue.** (a) "Scores about 66" is the high attribution; the low one is 55 (M pp.54-55), and §5.8 says only that one is a conclusion. (b) "Complete automation ... keeps a mature asset-light firm's score below 100 unless its market grows faster than about 31%" reads as a law on observed scores; M p.49 says it is a bound at a stated cost structure and leaner firms can exceed it. The 31% also depends on k = 0 (N-11). (c) Table 6 prints 117 in 2028 and 92 in 2036 in a table about the "central maximal score", although M p.56 says the 2028 figure is "an order of magnitude for one firm type, not a path". This is the 156 problem again in smaller form. (d) "Realizes 41% having embedded 61%" gives two shares; readers will quote the larger.
**Suggested change.** Abstract: "55 to 66 in 2036, depending on how much selling expense buys growth". Add "at the full-cost structure assumed here; firms with leaner costs can exceed it" and give the 31% with "no capital needs and compute at 6% of revenue". Move the surplus rows of Table 6 to the supplement. Define realized share as embedded share times the share of targeted savings kept (0.67) in one sentence in the abstract.

### N-8. Section 8.1 re-imports the unidentified weight
**Severity:** moderate. **Location:** M §8.1 p.59; M §7.5 p.58; S Table S7 p.32.
**Issue.** "If its spend ratio equals the median of 3.02 and it is optimal, an asset-light firm growing 10 points faster than its market scores about 20 points below the score it would earn with no growth spend." §5.4 says the ratio cannot be read as alpha(X - k); at the netted-maintenance attribution (0.99) the penalty is about 0.1 points. The next sentence, "A fixed threshold ... therefore marks down firms whose growth spending earns more than it costs", is unconditional; round 1 asked for "when". It is the 7-to-13 problem in a new place, and a CFO could quote it on an earnings call.
**Suggested change.** Show the example at three attributions (3.02; 0.99; 2.1 to 2.7 for fixed market growth). Replace "therefore marks down" with "marks down such firms when their marginal return exceeds cost; whether a typical firm's does depends on the attribution". Add the payback translation: at weight X the marginal dollar of growth spend buys 1/(X - k) dollars of annual revenue. Add "this is not a licence to burn cash; the test is marginal payback".

### N-9. The central path has no decomposition and no firm-specific market growth
**Severity:** moderate. **Location:** M §7.3 pp.53-55; Tables 5 and 6.
**Issue.** Of the 66 points in 2036, 42 is today's intercept for the top tail, 12.7 is market growth held at the sample median, and about 11 is automation (0.41 x (70 - 42)); a transformation lead needs this. Market growth is held at 12.7% for every firm and horizon but is the largest swing in Table 6 (58 to 83); the paper has the tool to map a firm's data to G (Gi = ln(1 + a) from NRR and the non-subscription share, Prop. 8(d), p.44) but does not use it. The path raises the intercept by 2 points by 2028 while the median firm raised GAAP margin by 8.2 points in 2022-24 (M p.54); the explanation ("cost programs of every kind") is fair, but the case is still called "central".
**Suggested change.** Add a bridge row to Table 5: anchor, plus automation, plus market growth, equals score. Add a "your G" box: G or Gi from NRR and new-logo growth. Show the median-firm path beside the exceptional-firm path. Put the revealed pace in Table 5 as a row, and show the 40/45/55 lower attribution in Table 5, not only in the text.

### N-10. Seat compression, AI-native entry and pricing are missing, and there is no regime test
**Severity:** moderate. **Location:** M Table 1 p.24; §7.2 p.52; §7.4 lever 4 p.56; Prop. 4 p.23; response EX-11, EX-15.
**Issue.** Table 1 lists "Labor budgets shift to software: G up" and no negative channel. For seat-priced vendors whose customers cut headcount the sign is open; lever 4 mentions shrinking seat counts in a clause. AI-native entry (business stealing) is absent. Pass-through phi is built for cost savings, while pricing is moving toward consumption and outcome models (ICONIQ, round-1 P1). The gap between "prices fixed" (ceiling 74 at 5% growth) and "free entry" (a few points plus rent) is the decisive strategic question and there are no observable indicators. The omitted channel moves G, the largest input in the tornado.
**Suggested change.** Add Table 1 rows: seat compression (G down for seat-priced firms); AI-native entry (growth opportunity and headroom down for incumbents); consumption and outcome pricing (phi and gross margin). Add a half-page regime test (gross retention, price realization, win rate against AI-native entrants, share of revenue in seat-priced contracts). Add one remark that an entrant's transient surplus draws on incumbents' headroom.

### N-11. Table 4 omits deferred revenue; the 31% threshold is overstated for annual-upfront billers
**Severity:** moderate. **Location:** M Table 4 p.51; S Remark S1(c) p.1; response EX-6, R2-13.
**Issue.** Columns are k = 0, 0.5 and 1.5. Prepaid billing makes the cash capital intensity negative (k = k_fix - k_def, S p.1), and the closed forms hold for k < 0. At k = -0.3 the central ceiling is 69.0 + 1.3 G, so the threshold falls from 31% to about 24%, reviewer arithmetic (the full-expensing variant was not recomputed; expect a similar size). Most of a $1 to 5 billion software peer group bills annually upfront; for them the abstract's 31% overstates the market growth needed by about a third. The other EX-6 items move the threshold little (tax 28 to 33%, fees 0.8 points, floor band 29 to 32%) but each is a sentence a CFO will look for: the 15% CAMT applies only above about $1 billion of average adjusted financial statement income, so 15% is not a floor for most $1 to 5 billion firms; 2 to 3% fees are card-billing rates and enterprise invoicing pays less; the IANS 0.69% is an all-industry figure and a software vendor's product security sits partly in cost of revenue and R&D.
**Suggested change.** Add a k = -0.3 column and a threshold-by-k row; add the three one-sentence caveats; quote the 31% with "for k = 0".

### N-12. Compute share conflates internal-automation compute with product inference
**Severity:** moderate. **Location:** M §7.1 p.49; §7.2 p.50; Table 4 p.51; Definition 3 p.26.
**Issue.** The 6% central compute share is the cost of replacing 60% of revenue in labor at a tenth of its cost: compute for internal automation. A $1 to 5 billion vendor's first-order 2026 margin issue is product-embedded inference in cost of revenue (ICONIQ: AI products at 45% gross margin in 2025, 53% and 59% projected; the "Rule of 30" argument the paper cites). It enters only as the "high-compute" case (40%), which the paper calls "not a feasible full-automation cost structure". A board may read that label as "the margin-dilution path is not real". The revenue-weighted gross-margin blend (Def. 3) is stated but not tabulated.
**Suggested change.** Split compute into internal-automation compute (opex) and product inference (cost of revenue) weighted by AI revenue share. Add rows to Table 4 for 10, 25 and 50% of revenue from AI products at 45 to 59% product gross margin. Rename the high-compute case "AI-product mix" and explain that it describes a firm whose revenue comes from AI products.

### N-13. The accountability-floor numbers do not match the paper's own sources or SOX practice
**Severity:** moderate. **Location:** M §7.2 p.50; Remark 6 p.72; S Table S7 pp.34-35.
**Issue.** (i) Remark 6's $1 billion firm has one in-scope control objective with 24 opportunities. The KPMG 2025 survey the paper cites reports 546 key controls and 40 in-scope systems on average, and an average SOX program budget of $2.3 million (fiscal 2024, N=114; 81 of 146 respondents are under $5 billion of revenue; I confirmed the figures on the KPMG PDF, Appendix B) before external audit fees. The text's "direct audit and Section 404 costs about 0.14%" ($1.4 million at $1 billion) is below that program average alone, and below round 1's Dropbox check (audit fees of 0.19% of revenue at 2.5 times the size). Not done (R2-10, EX-7). The survey is not size-matched to $1 billion, so the comparison is directional. (ii) The ITGC line per AI application is $204,672 (0.020%); the paper's own reference is $80,000 [16,000, 350,000] and the KPMG-derived cost per in-scope system is $16,000 to 57,500 (S p.35). "The floor reaches 0.5% at about 15 applications per $1 billion" (M p.50) becomes roughly 35 applications at the reference value (reviewer arithmetic).
**Suggested change.** Restate the bottom-up floor with a size-matched audit fee and the KPMG control count; show the floor as a function of in-scope controls and applications at both the $80,000 reference and $205,000; remove "15 applications" from §7.2 or give "15 to 35".

### N-14. The "remote" threshold is grounded on the wrong object and calibrated to a knife edge
**Severity:** moderate. **Location:** M Prop. 5(b) p.27; Remark 6 p.72; S Table S7 p.35; M §7.2 p.50; §8.5 p.61.
**Issue.** (i) The 5% threshold rests on adverse SOX 404(b) attestation rates (4.6% fiscal 2020 per the paper's citation, 5.8% fiscal 2021, which I confirmed at Audit Analytics). An adverse opinion records a material weakness, defined as a reasonable possibility of undetected misstatement; no actual misstatement is needed. It is an incidence of controls judged ineffective, not the probability that a material misstatement goes undetected, and a base rate of failure is not a tolerance. (ii) The calibration is knife-edge by construction: the three-human design has P = 0.002125 per opportunity against a threshold of 0.002135 (4.98% a year over 24 opportunities); the text says a threshold at which the all-human design fails "would contradict that evidence", and at 1% no human design passes (p.72 admits the parameters are "not calibrated to an effective control environment"). (iii) "No all-AI design on one provider passes" follows from an illustrative AI common-mode probability of 0.005 (class d) exceeding the break-even of about 0.0021 per opportunity at 5% (about 0.0004 at 1%), reviewer arithmetic; if ITGC quality brought it to the human 0.002, an all-AI design would pass. M pp.50 and 61 state the result as a requirement "neither cheaper inference nor scale removes". (iv) A director reading "5% a year chance of an undetected material misstatement" will hear a tolerance.
**Suggested change.** Call 5% "parity with a human design", not a tolerance. Report the break-even AI common-mode probability and the number of opportunities beside the "no all-AI design passes" statement. Cite Audit Analytics as an incidence. State the diversity rule as conditional on that probability.

### N-15. Program structure: identical processes, one binding capacity, concentrated benefits ignored
**Severity:** moderate. **Location:** M §7.3 p.53; §8.2 p.60; Def. 4 and Prop. 7(e) pp.29-31; Table 8 p.73.
**Issue.** (i) The calibration treats the program as a continuum of identical processes, so the realized-benefit path is a straight ramp. Real AI programs are concentrated: a few functions carry most of the savings, and the paper's own Prop. 6(d) says to sequence by gain per unit of the binding capacity. A prioritized program realizes far more than 7% of its benefits by 2028; the path describes an unprioritized one. (ii) "Change capacity, not decision bandwidth or security review, binds" is stated "in our calibration" (M p.60); it follows from class-d inputs (48 processes, decision capacity of 5, ten reviews per reviewer a quarter). Build and run engineering capacity and data readiness, which round 1 flagged, are not resources. (iii) The central 10% a year cites a WEF figure of workers needing training, which S p.30 says is the concept needed but is stated expectations. (iv) 41% realized and 61% embedded by 2036 are mostly the arithmetic of 10% a year applied to a program that covers the whole workforce.
**Suggested change.** Add a concentrated-benefits variant to Table 6 (for example the top fifth of processes carrying 60% of savings) and show the effect on the payback of N-1. State the binding-capacity result as conditional on the listed inputs. Add engineering and data capacity as a fifth resource, or say it is omitted and in which direction that biases the path.

### N-16. Operational definitions and people-side guardrails are missing
**Severity:** moderate. **Location:** Assumption 8 and Def. 4 p.29; M §7.3 p.53; §8.4 p.61; Table 8 p.73.
**Issue.** "Attempt", "works", "embedded (savings durable)", "affected employee" and "process" have no operational meaning (round-1 T and H items). "Full automation" is never said to be a bound and not a headcount target, in a paper with a section "What to track if headcount falls". Retention grants during transformation are SBC and hit the paper's own preferred margin but are absent from the dip. Capacity is exogenous and constant in Assumption 8 (change fatigue; round-1 H2). Legal minimums for workforce-affecting change are absent; a fast case with a one-year embedding is not attainable in works-council jurisdictions.
**Suggested change.** Add a definitions box (for example: embedded = savings sustained for four consecutive quarters at 80% of plan; affected employee = a role whose tasks change by more than a stated share; process = a unit of work with a stated FTE and dollar size, with the $0.5 million build size). Add "full automation is an analytical bound, not a staffing plan". Add retention grants and severance to the dip definition. State WARN and EU collective-consultation timelines as lower bounds for workforce-affecting processes.

### N-17. No acceptance rule or recommended basis for acquisitions
**Severity:** moderate. **Location:** M §6 pp.43-48; Prop. 8; Table 3 p.48; intro p.4.
**Issue.** The section gives several charging conventions and a 2025 range of 87 to 114 and says "the charging convention, not the data, decides the sign" (p.47). An M&A committee needs one basis and a rule. The fully charged sign flips at X = k_acq (1.7 to 3.2 times revenue for the three deals), and X is the unidentified weight. The simple rule that follows from Prop. 2(d) and Prop. 8(a) is not stated: pay less per dollar of acquired revenue than the firm's own marginal value of revenue (near its revenue multiple for a constant-growth firm), after allowing for the acquired base's retention (Prop. 8(f)). The first mention of the Q2 2026 score (about 160) in the intro (p.4) does not repeat the one-quarter caveat (FR-14).
**Suggested change.** State the rule above as R6; recommend the annuity basis for board reporting with the fully charged score as a labeled lower bound (round-1 CFO); apply it to the three deals; repeat the one-quarter caveat at first mention.

### N-18. Statutory compliance and labor-law scope missing from the cost lines
**Severity:** moderate. **Location:** Def. 3(ii) and (iv) p.25; Table 8 p.73; S Table S7 p.35; response EX-13, EX-14.
**Issue.** The AI-compliance line (0.10, 0.20, 0.40% of revenue) is built from "vendor estimates for security attestation and ISO/IEC 42001", which are voluntary. The EU AI Act high-risk obligations for employment uses (Annex III, 2 December 2027 under Regulation (EU) 2026/1744) and the Product Liability Directive for software (9 December 2026) are recorded in Table S7 but not in Definition 3 or the line they affect. Automating recruitment, task allocation or performance monitoring is exactly where Annex III applies. Effect on the ceiling is small (a point of cost is about 0.8 points of score), but these are the lines a GC or CHRO would budget.
**Suggested change.** Add the two dates to Definition 3(ii) and (iv); split AI compliance into voluntary attestations and statutory obligations, with the statutory part triggered by HR, credit, or safety-relevant uses; add one sentence on WARN and works-council timelines (see N-16).

### N-19. Common-mode scope is limited to model providers
**Severity:** moderate. **Location:** M Assumption 7 p.26; Lemma 6(e) p.71; Table 8 p.73; response EX-12.
**Issue.** The cross-type term covers override, shared data and ITGC failure; it omits shared tooling: identity provider, EDR agent, cloud region. The July 2024 CrowdStrike outage defeated every vendor-diverse layer at once. Table 8 prices 0.5, 2 and 6 day-long provider incidents (M p.73). A board told to hold "a human layer or a second provider" will read it as covering availability and tooling risk it does not cover. ITGC does not scale with agent identities and tool permissions (round-1 CIO). The cost of a warm second provider is not in the full-cost floor.
**Suggested change.** Add shared-tooling dependence to the cross-type term or as a separate term; scale the ITGC line with agents and tool permissions; add the cost of keeping a second provider warm to the maintenance floor.

### N-20. Licence, competing interests and unpublished dependence
**Severity:** moderate. **Location:** M p.1 footnote; p.4 ("this paper does not depend on it"); pp.50, 56; Remark 6 p.72; Table 9 p.75; reference list.
**Issue.** Page 1 still says commercial use of the paper or software requires the author's written permission. The "firms may apply the ideas" sentence is only in Table 9 (p.75), not in the footnote the response cites; the practical question (may a CFO use a chart in an internal board deck) is unanswered. Page 4 says the paper "does not depend on" the companion paper, but the 15-application figure (p.50), the dip budgets and ownership paths (p.56) and the ITGC and retest costs (Remark 6, which "follows the companion paper") are sourced to it, and it is "in preparation" (the reference title is still lower-case "ai"). On competing interests: the author declined (Table 9); the author line says "Independent researcher". A reader will ask whether there are employment, consulting or equity interests in software, AI governance or SOX services, and one line, whether "none" or a statement, closes the question. This is the author's decision; the practical cost is a question from every practitioner reader and from any journal or preprint endorser.
**Suggested change.** Put "the ideas are free to apply; internal use of figures with attribution is permitted" in the page-1 footnote. Include in the supplement the derivations behind each number taken from the companion paper, or label them "from unpublished work, not reproduced here". Fix the reference title case. Reconsider a one-line competing-interests statement.

### N-21. Own-versus-rent compute rule is silent on utilization
**Severity:** minor. **Location:** M Remark 7 pp.72-74; §7.2 pp.51-52.
**Issue.** The rule compares the vendor markup with 3.3 times market growth at cost TCO per unit, which implicitly assumes the owned capacity is fully used. If owned capacity is used a share u of the time, owning is cheaper per used unit only if the markup exceeds roughly 1/u - 1 on top of the growth term (reviewer approximation: about 11 points at 90% utilization, 100 points at 50%). Operating staff and power constraints are also absent.
**Suggested change.** Add a utilization term to Remark 7 and one sentence in §7.2.

### N-22. SOX design menu omits deterministic automated controls; the AS 2201 reading is presented as the standard
**Severity:** minor. **Location:** M Assumption 7 and Prop. 5 pp.26-27; Remark 6 p.72.
**Issue.** The design menu has two layer types, human and AI on one provider. Most non-human key controls in SOX programs are deterministic system-enforced controls and IT-dependent manual controls that rely on ITGC; deterministic automated controls can be tested by benchmarking when ITGCs are effective, which non-deterministic AI controls cannot be. A deterministic rule layer is the cheapest diverse layer (its failures are not common with a model's), so "one human over one AI layer" may not be the cheapest admissible design. Also, AS 2201 does not evaluate designs by layer failure probabilities; Prop. 5(b) is the author's operationalization of paragraph A7, and the text says only that "the standard sets no number" (round-1 A4).
**Suggested change.** Add a third type, deterministic automated control, to Assumption 7. Say in one sentence that Prop. 5 is the author's operationalization, not an accepted audit method.

### N-23. Table labels and readability
**Severity:** minor. **Location:** M Table 2 p.37; Table 4 p.51; Table 8 p.73.
**Issue.** Table 4 headers (cc, f, amin, cfull, tau, G*), Table 8 rows (c_sec, L_sec, xi_exp, H_cm, Y_fb) and Table 2 (seven numeric columns) cannot be read in two minutes (round-1 CIO and CFO).
**Suggested change.** Use plain labels in the main-text tables (compute share, fees, accountability floor, cost of running AI, tax rate, threshold market growth); add a "what to budget" line per floor in Table 8; move Table 2 to the supplement and keep a three-column version.

### N-24. Editorial items
**Severity:** minor. **Location:** M p.19; M pp.1, 3, 52, 62; reference list.
**Issue.** (a) "They do not identify the decision weight." appears twice in a row (M p.19, end of §3.6 "Implication for measurement"). (b) "Mature asset-light firm" is never defined (FI-17). (c) The Rule of 1000 is in the abstract, intro, §7.2 and conclusion although the arithmetic moved to S5; no operator runs a Rule-of-1000 company. (d) Reference title "The economics of ai transformation" is lower-case.
**Suggested change.** Delete the duplicate; replace "mature asset-light firm" with "a mature firm with little capital to buy"; cut the Rule of 1000 from the abstract to one clause and from the conclusion to one sentence; fix the title case.

---

## Appendix A. Proposed text

### A.1 One-page summary for operators and boards (numbers are the paper's v2 numbers)

> **What this paper finds.**
> 1. The Rule of 40 is a pass mark, not a frontier. Among the best software firms of 2010-25, a point of extra growth came with about a fifth of a point less margin, not a full point. This describes choices across firms, not the trade-off any one firm faces, and the sign is not statistically firm.
> 2. The basis decides the answer. In 2023-25, 29% of software firm-years cleared 40 on free cash flow before stock-based compensation and 9% after it.
> 3. Growth bought by acquisition enters the score without its price. For one serial acquirer, a 2025 score of 116 becomes 87 to 114 when acquisitions are charged as capital, depending on how the charge is spread.
> 4. The top of the distribution fell about 12 points between 2016-19 and 2023-25, mostly because fewer firms grew fast; the same years saw a rise in the cost of capital, and the data cannot separate the two. It recovered partly in 2025.
> 5. Even complete automation, at the full-cost structure assumed here and at fixed prices, holds the cash score of a mature firm below 100 unless its market grows faster than about 31% a year (27 to 51% over the credible range of compute cost). This is a bound at that cost structure, not a forecast or a target.
> 6. Execution sets the pace. On a central scenario an exceptional firm realizes about 41% of its automation benefits by 2036 and scores 55 to 66, depending on how much selling expense buys growth. Whole programs do not pay back inside five years.
> 7. Where rivals can copy freely, what lasts is what stays scarce: data that renews itself, distribution, licences, and credible accountability.

(Point 6's last sentence is the proposed go/no-go sentence of N-1, which holds on the paper's own central numbers; update it with the author's recomputed payback.)

### A.2 How not to use these numbers

> 1. Table 4's ceiling is an upper bound at a stated full-automation cost structure, not a target and not a limit on observed scores.
> 2. The central path is a scenario, not a forecast. It has two bounds (55 to 66 in 2036); quoting one is quoting a forward-looking statement.
> 3. The 31% threshold depends on compute at 6% of revenue and on no capital needs; with deferred revenue it is lower, with pass-through of savings to customers it is higher.
> 4. The weight on growth is not identified by the data. Use your own marginal return on growth spend, not a ratio from this paper.
> 5. Cross-sectional slopes record choices by firms with different opportunities; they are not any firm's own trade-off.
> 6. The fall of the top of the score distribution since 2016-19 is a description; it is not a case for lowering the bar.
> 7. Scores for named companies are the author's computations from filings under stated assumptions, not the companies' measures; lower bounds are lower bounds.
> 8. Nothing here implies that accountable people or control owners can be removed, or that full automation is a headcount target.
> 9. A 5% annual threshold in the control model is a benchmark of parity with a human design, not a tolerance for misstatement.

### A.3 Replacement sentences for the abstract

> "...among the best performers a point of growth came with about a fifth of a point less margin, across firms (not any firm's own trade-off; the sign is not statistically firm)."
> "...fell by 11.9 to 12.7 points between 2016-19 and 2023-25, mostly because fewer firms grew fast; the data cannot separate this from a rise in the cost of capital."
> "At the full-cost structure assumed here and at fixed prices, complete automation keeps a mature firm's cash-basis score below 100 unless its market grows faster than about 31% a year (27 to 51% over the credible range of compute cost); firms with leaner costs can exceed it."
> "On a central scenario path an exceptional firm realizes 41% of the benefits of its automation program by 2036 and scores 55 to 66 depending on how much selling expense buys growth."

---

## Appendix B. Checks run (accessed 29 October 2026)

**Web.**
- BCG, "If Failure Is Not an Option, Why Is Success So Rare?" (Forth et al., October 2020): win zone 30% (met or exceeded target value and sustainable change), worry zone 44% (created some value, did not meet targets), woe zone 26%; "flips the odds from 30% to 80%" with six factors. https://www.bcg.com/publications/2020/increasing-odds-of-success-in-digital-transformation
- KPMG, 2025 SOX Survey: fiscal-2024 average SOX program budget $2.3 million (N=114), average key controls 546 (N=140), average in-scope systems 40 (N=139), 16 hours per control test (N=83); sample 146, segments under $5 billion (N=81), $5 to 25 billion (N=43), over $25 billion (N=22). https://kpmg.com/kpmg-us/content/dam/kpmg/pdf/2025/the-2025-sox-survey.pdf
- Audit Analytics, SOX 404 Disclosures: An Eighteen-Year Review: 5.8% of SOX 404(b) auditor attestations were adverse for fiscal 2021; the page does not give a fiscal-2020 value (the paper cites Hallas, 2021, for 4.6%; not checked). It does not say that an adverse opinion needs an actual misstatement. https://blog.auditanalytics.com/sox-404-disclosures-an-eighteen-year-review/

**Reviewer arithmetic (from the paper's own tables).**
- Payback (N-1): realized gain = realized share x (target intercept minus anchor intercept) from Table 5: 1.5, 5.0, 11.5 points at 2028, 2031, 2036; dip 2.2 to 3.1 points through the program; piecewise-linear interpolation. Annual crossover at year 4.0; cumulative break-even at year 7 undiscounted and year 8 at 9.34%.
- Like-for-like execution yield (N-2): 0.30 x 0.67 + 0.44 x 0.37 = 0.364 against 0.70 x 0.67 = 0.469; ratio 0.78; 41% x 0.78 = about 32%.
- Deferred revenue (N-11): central ceiling 69.0 + (1 - k)G reaches 100 at G = 31/1.3 = 23.8% for k = -0.3 (taking the 69.0 base as unchanged, which the paper's closed forms allow for k < 0 only approximately; the base itself may move slightly). The full-expensing variant was not recomputed.
- Control threshold (N-14): threshold per opportunity at 5% over 24 opportunities = 1 - 0.95^(1/24) = 0.002135; three-human design = 0.002 + 0.998 x 0.05^3 = 0.002125 (4.98% a year); all-AI break-even common mode at 5% about 0.0021, at 1% about 0.0004.
- Table 7 (N-3): value columns equal 0.1 x S&M, 0.1 x S&M/0.3 and 0.1 x G&A at every position; Gi = g - S&M/3.3 (elite: 36 - 20/3.3 = 30%).
- ITGC (N-13): at $80,000 per application ($0.008% of $1 billion) the floor passes 0.5% at about 34 applications, against 15 at $204,672.

Nothing in this report depends on the author's private information; the competing-interests point in N-20 is a statement about what readers will ask, not about any interest the author may or may not hold.
