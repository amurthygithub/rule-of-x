# Referee Report

**Manuscript:** *The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation*
**Author:** Akshaya Bangalore Sreenivasa Murthy (independent researcher)
**Date of review:** 3 November 2026
**Reviewer:** Independent referee team (Lead + four specialist auditors: mathematical economics/optimal control; econometrics/empirical IO; corporate finance/accounting; reliability & ICFR; prior art/citations)

---

## 0. Bottom line up front

**No demonstrated error was found** — in the theory, the empirical estimation, the Bending Spoons case study, or the regulatory/accounting claims. The paper is one of the most carefully caveated, transparently documented, and independently *reproducible* working papers of its kind. Every headline number I re-derived or re-ran reproduced exactly; all 191 symbolic/numerical checks in the author's verification script pass on a fresh run; four specialist audits returned "no error found" independently of one another.

The paper's genuine limitations are **all disclosed by the paper itself**, and they are substantive rather than cosmetic: (i) the central "decision-weight" result is conditional on an **unproved** verification hypothesis (H); (ii) the headline "32.5% market-growth threshold" is a **scenario bound** resting on an unmeasured compute share; (iii) the empirical section is **descriptive, not structural** (the paper proves the cross-section identifies no firm's own trade-off); and (iv) the paper was drafted, proved and coded by **AI agents**, and its "peer review" was performed by AI referees on the same model family — there has been **no human independent verification**.

**Recommendation:** accept for release as a working paper (arXiv) with minor corrections. For a peer-reviewed journal, the appropriate verdict is **minor revision** at a specialist field journal, contingent on (a) resolving or honestly re-scoping the unproved hypothesis (H), and (b) human specialist sign-off on the tax/regulatory and scenario-parameter claims that the AI agents could not fully verify.

---

## A. Editorial assessment

### A.1 Recommendation and the standards by contribution type

The contribution is assessed as an **interdisciplinary economics–finance–technology working paper** (author's stated target: arXiv q-fin.GN, cross-listed econ.GN; no peer-reviewed outlet was specified). It is best read as three contributions in one document:

1. **A theory paper** (Section 3 + Supplement S3): a growth–profitability frontier on which the Rule of 40 / Rule of X are *price lines*, with closed-form optima, a score budget, a decision-vs-screening weight distinction, a free-entry limit, and an accountability-floor control model. This part is **correct and rigorously verified**.
2. **An empirical/measurement paper** (Sections 4–6): a first-reported-vintage SEC panel of 292 prepackaged-software firms (2010–2025), partial-frontier estimation, and an acquisition-adjusted scoring method applied to Bending Spoons. This part is **careful, honest about non-identification, and reproducible**.
3. **A calibration/scenario paper** (Section 7): a full-automation ceiling and a central path to 2036. This part is **transparently scenario-driven** and must be read as conditional, which the paper insists on.

By contribution type, publication standards differ:
- As a *theory paper*, the standard is theorem correctness. **Passed** — but the unproved hypothesis (H) means the flagship "a value-maximizing firm acts on a weight equal to the marginal value of revenue" is a *conjecture with numerical evidence*, not a theorem. A top theory journal would require a proof of (H) or a credible existence/regularity result.
- As an *empirical paper*, the standard is estimand clarity and reproducibility. **Passed** — but the paper's own Proposition 3 proves the cross-section is non-identifying, so the empirical section is description, not causal/structural inference. This is a scope limitation, not a defect.
- As a *measurement/case paper*, the standard is arithmetic and accounting accuracy. **Passed** — the Bending Spoons case reproduces exactly and the ASC citations are correct.

### A.2 The defensible contribution

The following survive this review as genuine, defensible contributions (the paper's own novelty list is, if anything, conservative):

1. **The score budget (Proposition 1).** This is the cleanest and most original result. It is *correct and sharp*: within one market, with zero-spend growth at least equal to market growth, the total excess of a Rule-of-X score over its saturated level is bounded by `(X−k)·ln(s̄/s₀)` — a finite budget of share headroom. The bound is a one-line consequence of `R_X ≤ R_∞ + (X−k)Δ − σ ≤ R_∞ + (X−k)Δ` and `∫Δ dt = ln(s_T/s₀)`, and Proposition S2 proves it is approached (not attained) by arbitrarily slow spending. Extreme scores are therefore *necessarily transient* — **conditional on retention ≥ market growth**, a condition the paper states and whose failure (Remark S1(b)) it correctly diagnoses.
2. **The accountability floor as a control standard under common-mode failure (Proposition 5).** The strongest novelty candidate. It is a correct application of the beta-factor common-cause-failure model to the SOX-404 "no reasonable possibility of a material misstatement" standard, yielding the precise result that **no number of layers on a single AI provider passes** once the provider's common-mode failure exceeds the "remote" threshold. The paper correctly separates regulatory fact (AS 2201 A7; S-K Item 308(a)(3); "reasonable possibility" = FAS 5 "reasonably possible or probable") from modeling assumption (the beta-factor layer model) from scenario value (π̄ = 5%/1%). All four regulatory assertions were verified verbatim against primary sources by the reliability auditor.
3. **The decision-weight vs. screening-weight distinction (Proposition 2 + Lemma 5).** Correct *given* hypothesis (H); the screening weight as a Macaulay-duration-scaled margin is a clean, correct derivation. The two-weights distinction (firm acts on marginal value of revenue ≈ revenue multiple; investors screen on a duration weight of 2–3) is a real clarification of practitioner confusion, and the paper correctly notes the cross-section identifies neither.
4. **A first-reported-vintage, acquisition-flagged empirical description of the software growth–margin frontier.** The construction (items "as first reported," fiscal-year convention, five pre-registered sample rules, four estimands E1/E2/M4/M8) is unusually careful, and the headline numbers reproduce exactly.
5. **An acquisition-adjusted scoring method (Proposition 8, Remark 4, Bending Spoons).** Correct and genuinely useful: acquired growth enters at net weight `X − k_acq`, and the "charge interest *or* cost of capital, not both" point is pinned quantitatively (double-count = exactly `(1−τ)·c_fin`).

What the paper does **not** establish (and does not claim to): any mapping from scores to valuation multiples; any causal effect; any identification of the spend elasticity α or the decision weight from the data; any forecast. These are correctly disclaimed.

### A.3 The single most important editorial consideration

The manuscript was **produced in a documented collaboration between the author and AI research agents** (Appendix A): AI agents on Claude models drafted the text, wrote the proofs, built the panel, ran the estimation, and — critically — served as the *referee panel* that reviewed the paper. The paper's own Appendix A.6 states the limit correctly: "Independent agents built on the same underlying model may share blind spots, so their agreement is weaker evidence than agreement among human experts would be." The paper's claim that "no referee found a false theorem in the static model" refers to **AI referees on the same model family**, not independent human experts.

This is **not a defect in the content** — I found no error that the AI process missed — but it is a material fact for an editor: the work has had **no independent human verification** before this review. The author discloses this fully, which is to her credit, but the disclosure does not substitute for the verification. Any acceptance decision should treat the paper as un-peer-reviewed in the human sense and weigh it accordingly.

---

## B. Claim / theorem audit matrix

Status codes: **OK** = verified correct; **COND** = correct but conditional (condition stated); **AMBIG** = notation/scope ambiguity needing clarification; **UNTESTED** = not independently testable in this environment.

| # | Claim | Locator | Status | Notes / condition |
|---|-------|---------|--------|-------------------|
| 1 | Efficient frontier `m*(g) = m0 − kg − κ(g−G)^β`, concave, convex feasible set | Lemma 1; §3.2 | OK | `k ≥ 0` required for "frontier = graph of m*, strictly decreasing"; installed-ahead capital timing required for convexity (Lemma S1). Both disclosed. |
| 2 | Max Rule-of-X score, eq. (5)–(7): `Δ*`, `σ*`, `R*`; tangency `m*′(g*)=−X`; duality | Lemma 2 | OK | Interior iff `X > k`; corner at `X ≤ k` (part c) verified. |
| 3 | Saturation, small-base bound, demand-pull threshold | Lemma 3 | OK | — |
| 4 | **Score budget** `∫(R_X−R_∞)⁺ ≤ (X−k)ln(s̄/s₀)` | Prop 1 | **COND** | Correct and sharp; **finiteness requires `g ≥ G`**. Fails if retention < market (Remark S1(b)) — disclosed. |
| 5 | Extreme scores transient | Cor 1 | OK | Example numbers 1.81→1, 9.65→9, 5.01→5, 0.43 yr, 0.30 yr all confirmed. |
| 6 | Envelope results `∂R*/∂(m0,G,k,X,λ)` | Lemma 4 | OK | — |
| 7 | Capital-for-labor substitution | Cor 2 | OK | Bracket (15) exact by convexity. |
| 8 | Automation priorities | Cor 3 | OK | — |
| 9 | **Dynamic optimality: firm's weight = marginal q of revenue** | Prop 2 | **COND** | Parts (a),(d),(e) unconditional and correct; (b),(c) conditional on **unproved (H)**. HJB (17), verification argument, root (19), Gordon identity `v0 = m°/(r−g°)`, ODE singularity `∂Φ/∂u = (r−G)/Δ° > 1` all re-derived correctly. |
| 10 | Investor's screening weight (duration) | Lemma 5 | OK | — |
| 11 | Industry frontier as upper envelope; **non-identification** | Prop 3 | OK | Non-identification (Prop S3(iv)) correct: cross-section identifies neither slope nor curvature. |
| 12 | Free entry & replication | Prop 4 | OK | Special case of Mankiw–Whinston; n*, Lerner, F→0 limit, scarce input, full-cost bound all reproduce. |
| 13 | **Accountability floor as control standard** | Prop 5 | OK | Formula, admissibility equivalence, single-provider inadmissibility all verified. |
| 14 | Full-automation ceiling `R_max` | Cor 4 | OK (as bound) | Tax substitutions (Remark 2) verified against 26 U.S.C. §174A (real, Pub. L. 119-21). |
| 15 | Attainable frontier | Prop 6 | OK | — |
| 16 | Expected frontier | Prop 7 | OK | — |
| 17 | Value-based restatement (economic profit, ROIC) | Remark 3 | OK | Identities. |
| 18 | Score when growth is bought | Prop 8 | OK | Net weight `X − k_acq` exact. |
| 19 | Levers by position | Prop 9 | OK | — |
| 20 | Empirical: Ψ₀.₉₀ slope −0.22/−0.16; P95 decline −11.9/−12.7 | §5; Table 2 | OK | **Reproduced exactly.** Descriptive, not structural (Prop 3). |

---

## C. Major findings (author-defense structure)

### C.1 — MAJOR — Hypothesis (H) is unproved

- **Location:** Proposition 2(b)–(c), §3.6; §8.6; Appendix A.6; Supplement Proof of Proposition 2.
- **Finding:** The paper's flagship normative result — "a value-maximizing firm maximizes a Rule-of-X score at every date, with weight equal to the marginal value of revenue `v′(s)`" — is conditional on a verification hypothesis (H) that the paper **explicitly does not prove**. (H) requires the existence of a bounded C¹ solution of the HJB equation (17) on (0, s̄) whose feedback generates admissible paths. The paper shows (H) holds in two special cases and provides a numerical dynamic-programming solution for the worked example, and it correctly analyzes the singular ODE to show the boundary behavior `v̂/s → v0` does *not* select a unique solution.
- **Classification:** missing hypothesis (acknowledged, not concealed). This is the paper's own honest admission ("We have not proved (H). It is the hypothesis of a verification theorem, and we state it as an assumption.").
- **Strongest defense:** (a) The verification argument (b) is standard and correct; (b) parts (a), (d), (e) hold unconditionally; (c) the numerical solution is "evidence for (H) at those parameters, not a proof," which is exactly what the paper claims; (d) the decision-weight interpretation is used for *comparative statics and discussion*, not for any headline number.
- **Why it survives / is narrowed:** the finding is **confirmed and narrowed to its true scope**. It is not an error; it is a correctly-disclosed scope limit. The theory-adversary independently re-derived the HJB, the verification argument, the root (19), and the singularity `∂Φ/∂u = (r−G)/Δ° > 1` (numeric 1.73), and confirmed part (e).
- **Affected conclusions:** every sentence asserting that a value-maximizing firm *acts on* the marginal-value weight (the discussion §8.1, the practical implication that "a fixed threshold marks down firms whose marginal growth spend earns more than it costs," the lever ranking §7.5 at the "firm's own weight").
- **Smallest correction / decisive test:** Either (i) prove (H) for a parameter class — the paper's own analysis shows the natural approach is to select the solution through the terminal singular point `v̂(s̄) = (m0−kG)s̄/(r−G)` and show boundedness/C¹, or (ii) re-state all decision-weight claims as "conditional on (H), which we do not prove." (The paper already does (ii); a journal would want (i).)

### C.2 — MAJOR — The "32.5% threshold" is a scenario bound, not an estimate

- **Location:** §7.2, Table 4, Corollary 4; abstract.
- **Finding:** The headline "complete automation keeps a mature firm's cash score below 100 unless its market grows faster than ~32.5%/yr" rests on a **compute share of 6% of revenue that is an explicitly unmeasured scenario value**, with a stated credible range of 1–60% mapping to thresholds of **28–78%**. Pass-through of cost savings to customers raises it to 36.2% (ϕ=0.5) or 38.3% (ϕ=0.7). The full-cost floors (cfull = 2.1/6.2/16.5 points) are themselves built from scenario loss severities.
- **Classification:** evidence-transport / unsupported-as-point-estimate — but **fully disclosed**. The paper says "Every threshold is conditional on the scenario compute share"; the abstract itself carries "(28 to 78% over its credible range; 36 or 38% if half or 70% of savings pass to customers)."
- **Strongest defense:** the ceiling is correctly *labeled* a bound at a stated cost structure, not a forecast or target; a firm with leaner costs can exceed it (Corollary 4(a)); the pass-through is a scenario spanning evidence (Choi 2025 ~0 for differentiated software; Ganapati 2020 ~0.7 for an industry-wide shock).
- **Why it survives / is narrowed:** the *logic* is correct; the *number* is soft. The finding is narrowed to: the precise "32.5%" should never be quoted without its conditioning, which the paper already insists on ("How not to use these numbers," items 1–2).
- **Affected conclusions:** the "Rule of 100 is not a steady state" conclusion (which is robust — it does not depend on the precise threshold); the specific threshold number (which does).
- **Smallest correction:** none required beyond what the paper already does; a stricter editor would demote the 32.5% from the abstract to the scenario section.

### C.3 — MAJOR — The empirical section is descriptive, not structural

- **Location:** §5; Proposition 3(iv); §8.6.
- **Finding:** The paper's own Proposition 3(iv)/S3(iv) proves the cross-section of chosen points identifies **neither the slope nor the curvature of any firm's frontier**, and Section 5 confirms the spend data identify neither the spend elasticity α nor the decision weight (α(X−k) ranges 0.05–10.1 across methods). So the headline "−0.22 slope" is a description of *chosen points*, not an estimate of any structural parameter, and "the sign is not statistically firm."
- **Classification:** unsupported-as-structural — but the paper never claims structure; it says "these are choices across firms, not the trade-off any one firm faces," and it *proves* the non-identification.
- **Strongest defense:** the paper's discipline is to state a model-facing claim only where it holds under all four views (E1, E2, M=4, M=8), and it withholds any claim that would require identification.
- **Why it survives:** no error; the empirical contribution is a *careful description* plus a *proof of what the description cannot reveal* — the latter is a genuine, if negative, contribution.
- **Affected conclusions:** none stated; the risk is only that a reader over-reads "frontier" as structural.

### C.4 — MAJOR — Statistical strength of the headline results is modest

- **Location:** §5.2–5.3; Table 2.
- **Finding:** (i) the −0.22 slope's *negative sign* does **not** survive the familywise correction (Holm p = 0.26–0.45 GAAP); only "far above −1" survives; (ii) the cash-basis P95 decline (−12.7) survives the correction **under no procedure**; (iii) the GAAP decline (−11.9) survives at 10% under most (not all) procedures.
- **Classification:** correctly-reported statistical fragility. The abstract states this precisely ("significant at 10% … under most procedures" / "not significant").
- **Strongest defense:** the paper treats "far above −1" (which *does* survive) as the robust claim and demotes the sign; it reports every procedure; it does not oversell.
- **Why it survives:** not an error; a referee should simply read the abstract with the correction in mind.
- **Affected conclusions:** the "about a fifth of a point less margin" is a point estimate with a fragile sign, not a robust finding; the "top fell 11.9 points" is robust on GAAP at 10%, not 5%.

### C.5 — MAJOR — No human independent peer review (AI provenance)

- **Location:** Appendix A; Supplement S7; title-page footnote.
- **Finding:** the manuscript and its *internal review* were both produced by AI agents (Claude family models). The "referee panels" that returned "major revision" / "minor revision" verdicts were AI agents. No human reviewer (other than the author's own reading, and this external review) has examined the work.
- **Classification:** provenance/verification gap — fully disclosed.
- **Strongest defense:** the author directed the work, made every material decision (Table 8), took full responsibility, and commissioned *outside* LLM reviews; the disclosure exceeds arXiv norms.
- **Why it survives:** this is not a content error, but it is the decisive fact for an editor. My independent verification found no error the AI process missed — which is itself evidence that the process was competent — but it does not change that the "peer review" recorded in the paper is not peer review in the human sense.
- **Affected conclusions:** none of the paper's content; but the *status* of the paper (un-human-reviewed working paper).
- **Smallest correction:** none; the disclosure is adequate. An editor should simply not treat Appendix A's review rounds as peer review.

### C.6 — Minor items (citation/notation precision; no substantive effect)

1. **Lee (2024) sample size.** The paper says "1,756 SaaS firms." My own fetch of the *published* Applied Finance Letters abstract confirms "1756 SaaS companies." (The citation-auditor's "1,771" was from the MPRA *preprint*; the paper correctly uses the published figure.) **No error.** (The cited URL in the reference list lacks the `/1/` path segment and 404s; the DOI 10.24135/afl.v13i.761 is correct — fix the URL.)
2. **Svanberg et al. (2024).** "23% of the wages paid for exposed tasks" should read "23% of wages paid for **vision** tasks" (computer-vision exposure only). The surrounding sentence says "on computer vision," so it is not misleading, but the phrase "exposed tasks" over-generalizes. **Minor.**
3. **Ganapati et al. (2020) ϕ=0.7.** Imported from *energy-price* pass-through in *US manufacturing* — the single most load-bearing scenario parameter, applied to an AI cost shock in software. The paper flags the sector mismatch (Table S11). Treat ϕ=0.7 as an assumption, not a software measurement. **Minor (but load-bearing).**
4. **Kwa et al. (2025) METR figure.** ">80% of successful runs cost <10% of human cost" is **not** in the arXiv abstract; needs a pin-cite to the paper body/appendix or METR's run data. The tighter 0.4–1.1% is honestly labeled "our computation." **Minor.**
5. **Vista Equity Partners (2026) title is stale.** The piece has been retitled to an "AI Rule of 60" slug; the body was not retrievable (JS-rendered). **Minor.**
6. **§8.5 cites "AS 2201 ¶.03" for 404(b) attestation scope.** ¶.03 states the auditor's *objective*; the *scope* is SOX 404(b)/Item 308(b), both cited in the same sentence. **Cosmetic re-pin.**
7. **Stale verification-code check E7** still labels the fully-charged score −28.7/−24.8 (pre-round-2 after-interest convention); the paper correctly uses −25.0/−16.5 (before interest). **Code/notes housekeeping, not a paper error.**
8. **Remark S10 "8.4% of items the AI missed."** Computed as a *marginal* human miss rate (retaining the 0.002 common mode); a literal conditional reading gives ~8.6%. **Immaterial phrasing.**
9. **Mosleh et al. "1989" year** — plausible; substantive attribution (beta-factor common-cause modeling) correct regardless. **Optional bibliographic check.**

---

## D. Empirical assessment — what was and was not reproduced

### D.1 Reproduced exactly (independent of the author's pipeline)

I loaded the committed panel (`data/panel_v3.csv`) and computed the headline statistics with my own script (`independent_empirics.py`, saved alongside this report). Results match the paper digit-for-digit on:

| Statistic | Paper | My recomputation |
|---|---|---|
| Firm-years / firms | 1,788 / 292 | 1,788 / 292 ✓ |
| Period counts 2010-15/16-19/20-22/23-25 | 465/418/458/447 | 465/418/458/447 ✓ |
| Ψ₀.₉₀ slope, 2010–25, 0–60% (GAAP / cash) | −0.22 / −0.16 | −0.215 / −0.161 ✓ |
| Ψ₀.₉₀ slope, 0–40% (GAAP / cash) | −0.31 / −0.27 | −0.308 / −0.273 ✓ |
| Ψ₀.₉₀ slope, 2010–19 0–40% / 2020–25 0–40% (GAAP) | −0.22 / −0.60 | −0.215 / −0.596 ✓ |
| Change in P95 score, 2016–19 → 2023–25 (GAAP / cash) | −11.9 / −12.7 | −11.9 / −12.7 ✓ |
| Within-firm FE slope, margin on growth (GAAP / cash) | +0.06 / −0.03 | +0.059 / −0.032 ✓ |
| Median scores 2023–25 (GAAP / adj / FCF / FCF−SBC) | 12.0 / 26.4 / 29.2 / 15.3 | 12.0 / 26.4 / 29.2 / 15.3 ✓ |
| Margin-gap decomposition (total / S&M / R&D / G&A / gross) | 34.5 / 16.0 / 7.1 / 5.5 / 5.7 | 34.5 / 16.0 / 7.1 / 5.5 / 5.7 ✓ |
| 40–60% band (total / S&M / R&D) | 41.3 / 29.4 / 11.9 | 41.3 / 29.4 / 11.9 ✓ |
| Bending Spoons Table 3 (GAAP 92.3/115.9; after interest 87.5/105.0; OCF 103.9/116.9; charged 87–114; fully charged −25.0/−16.5) | — | all reproduce ✓ (acquirer-auditor) |

### D.2 Author pipeline runs clean on a fresh checkout

- `code/verify_theory.py` — **191/191 checks pass** (exit 0), covering the symbolic closed forms, first-order conditions, envelope derivatives, concavity/limit/inequality/probability claims, and the "arithmetic" checks of the calibration numbers.
- `code/paper1_macros.py` — regenerates 1,577 macros and passes the CLAIMS gate (every sentence of the text is supported by a pipeline output).
- `code/verify_part2_acquirer.py` — **82/82 checks pass**, reproducing the Bending Spoons case.

### D.3 What was NOT reproduced / could not be independently verified

1. **The full 999-replication firm-cluster bootstrap was not re-run** (≈35 minutes). I verified the *point estimates* independently and confirmed the committed bootstrap artifacts (`notes/bootstrap_draws_v3.npz`, `notes/empirics_v3.json`) are present and consistent with Table 2's intervals. The seeded design (one generator per block, seed = 20261030 + CRC-32 of the block name) is documented and would reproduce; I did not execute the full bootstrap in this session.
2. **The raw SEC source documents are not in the replication package.** The Bending Spoons F-1/424B4 and the Q2/H1 6-K financial exhibits exist only as the author's markdown extract (`notes/case_bending_spoons_f1_extract.md`) plus small JSON extracts. A direct EDGAR fetch returned **HTTP 403 ("undeclared automated tool")**, so the ultimate source filings could not be independently retrieved in this session. The paper repeatedly discloses this ("not in our extract"; "the pro forma … not re-verified"). **This is the single most important replication-package gap** for the case study.
3. **Paywalled full texts** of several method/theory references (Cazals 2002; Aragon 2005; Marris 1964; Solow 1971; Odagiri 1981; Vidale & Wolfe 1957; Nerlove & Arrow 1962; Dorfman & Steiner 1954) were verified bibliographically (correct DOIs) but not read in full.

---

## E. Citation / parameter-source ledger

Compiled from my own fetches plus the citation-auditor's independent verification. Access levels: **FT** = full text; **ABS** = abstract; **BIB** = bibliographic (correct DOI) only; **URL** = URL/title evidence only; **N/A** = not opened.

| Reference | Access | Does it report the attributed result? | Transport judgment |
|---|---|---|---|
| Lee (2024) AFL 13:168–185, Rule of 65 | ABS (published) | Yes — "1756 SaaS companies… Rule of 65" | **Valid.** "Only peer-reviewed study" claim corroborated by Crossref title search (no other peer-reviewed Rule-of-40 paper). |
| Ganapati, Shapiro, Walker (2020) AEJ:App | ABS | Yes — "70 percent … passed through" | **Valid but transported** energy→manufacturing→software; flagged by author. |
| Kim et al. (2025) ICML, correlated LLM errors | ABS | Yes — "models agree 60% when both err" | **Valid.** Paper's caveat (P(same-wrong|both-wrong), not P(err|other-errs)) is correct. |
| Deeter & Bondy (2024) Bessemer Rule of X | FT | Yes — "~2x private, ~2–3x public" | **Valid.** |
| Feld (2015) Rule of 40% | FT | Yes | **Valid.** |
| Vista (2026) Rule of 60 | URL | Title/slug corroborates "Rule of 60"; body not retrieved | **Likely valid; title stale.** |
| Cazals (2002); Aragon et al. (2005) | BIB | Correct canonical partial-frontier citations | **Valid (bibliographic).** |
| Marris (1964); Solow (1971); Odagiri (1981) | BIB | Genuine growth–valuation tangency antecedents | **Valid (bibliographic).** |
| Arkolakis (2010) JPE | ABS | Yes — "increasing marginal cost to access additional consumers" | **Valid.** |
| Gourio & Rudanko (2014) REStud | ABS | Yes — "customer base … sluggish to adjust" | **Valid.** |
| Vidale & Wolfe (1957); Nerlove & Arrow (1962) | BIB | Canonical classics | **Valid.** |
| Dorfman & Steiner (1954) | BIB | Correct restatement of optimal-advertising condition | **Valid.** |
| Brynjolfsson, Li, Raymond (2025) QJE | ABS | Yes — "14% productivity… 34% novices" | **Valid.** |
| Acemoglu (2025) Econ. Policy 40(121):13–58 | ABS | Yes — "modest aggregate effects" | **Valid.** |
| Svanberg et al. (2024) MIT FutureTech | ABS | Yes — "23% of worker wages … vision tasks" | **Valid; "exposed tasks" slightly over-generalizes.** |
| ICONIQ (2026) State of AI | FT | Yes — "45% → 53% → 59% gross margin"; "11% → 16% → 19%" | **Valid; numbers match exactly.** |
| Kwa et al. (2025) METR (NeurIPS 2025) | ABS | Paper exists; ">80% runs <10% cost" **not** in abstract | **Valid citation; figure needs pin-cite.** |
| 26 U.S.C. §174A (my own fetch) | FT (LII) | Yes — domestic R&E expensed from tax years after 31 Dec 2024, added by Pub. L. 119-21 §70302(a) | **Valid.** Paper's tax claims are accurate. |
| AS 2201 A7; S-K Item 308(a)(3); FAS 5; Item 308(b) (reliability auditor) | FT (archived primary) | All verbatim-accurate | **Valid.** No fabricated regulatory threshold. |

**Novelty assessment (with the required caveat):** a bounded search cannot prove no predecessor exists, but a Crossref title search found no other peer-reviewed "Rule of 40" study besides Lee (2024), and no direct predecessor was found for the five claimed new results. The score budget and the accountability floor are the strongest novelty candidates; the "price line" reading and the non-identification are correct but trace to Marris/Solow/Odagiri and Marschak–Andrews respectively, which the paper credits.

---

## F. Independent scripts, execution log, environment

**Environment:** Python 3.12.3; numpy 2.5.2, scipy 1.18.1, pandas 3.0.3, matplotlib 3.11.1, sympy 1.14.0, mpmath 1.3.0, statsmodels 0.15.0 (installed `--break-system-packages` in a container without venv/ensurepip). Working tree: `work/repo/rule-of-x/` (clean checkout of github.com/amurthygithub/rule-of-x, 586 files).

**Commands run (Lead):**
- `python3 code/verify_theory.py` → exit 0, **191/191 PASS** (log saved).
- `python3 code/paper1_macros.py` → exit 0, 1,577 macros; abstract 1,912 chars.
- `python3 code/verify_part2_acquirer.py` → exit 0, **82/82 PASS**.
- `python3 /root/tmp/independent_empirics.py` → reproduced Table 2 headline statistics (saved).

**Independent scripts (theory-adversary, saved with this report):** `lemma2_symbolic.py`, `prop1_numeric.py`, `prop2_hjb.py`, `prop4_prop5_counter.py`, `prop6_prop7.py` — all in `/root/outputs/rule-of-40-referee/`, all passing against the paper's claims.

**Fixed seeds:** the paper's bootstrap seeds (documented in Table 2 notes) were not altered; point estimates are seed-independent.

---

## G. Revision sequence and claim-level corrections

**Required before release (minor, non-blocking):**
1. Fix the Lee (2024) reference URL (add the `/1/` path segment; DOI is correct). No change to the "1,756" figure (it matches the published abstract).
2. "23% of the wages paid for **exposed** tasks" → "…for **vision** tasks" (Svanberg et al. 2024).
3. Re-pin §8.5's "AS 2201 ¶.03" to Item 308(b) / SOX 404(b) for the attestation *scope*.
4. Update the Vista (2026) title to the current "Rule of 60" slug.
5. Pin-cite the METR ">80% of successful runs <10% of human cost" figure to the paper appendix or run data.
6. Housekeeping: update `verify_part2_acquirer.py` check E7 and `notes/acquirer_notes.md` from the stale −28.7/−24.8 to the paper's correct −25.0/−16.5.

**Recommended before journal submission (substantive):**
7. Either prove hypothesis (H) for a parameter class, or insert a one-sentence downgrade at every decision-weight assertion ("conditional on (H), which we state but do not prove") so the reader cannot miss it.
8. State in the abstract's second sentence (not only in "How not to use these numbers") that the 32.5% threshold is a scenario bound conditional on a compute share of 6% of revenue, with credible range 28–78%.
9. Add to the replication package either the raw F-1/424B4 and 6-K financial exhibits for the Bending Spoons case, or a signed checksum of the extracted figures against the SEC originals, so the case study is independently verifiable without an EDGAR session.

**Not required:** no theorem, estimate, table, or case-study number needs correction. No claim was found to be overstated beyond what the paper already qualifies.

---

## H. Uncertainty statement and coverage ledger

### H.1 What limits this review

1. **Raw SEC filings inaccessible.** EDGAR returned 403; the Bending Spoons source documents are not in the repo (author's extract only). The case study's *ultimate* inputs rest on the author's transcription, guarded only by in-repo self-consistency checks.
2. **web_search unreliable in this environment** (returned irrelevant commercial results); verification relied on targeted `web_fetch` of known URLs. Broad "does any other peer-reviewed Rule-of-40 study exist?" checks are therefore weaker than ideal (mitigated by the citation-auditor's Crossref title search).
3. **Paywalled full texts** of 8 method/theory references were verified bibliographically only.
4. **Full bootstrap not re-run** (point estimates and committed bootstrap artifacts verified instead).
5. **Some 2025–2026 sources** (Palantir Q2 2026 press release; Vista 2026 body; the "Rule of 60/30" practitioner pieces) were not independently read in full.

### H.2 Blind-pass status (honest disclosure)

This review **did not read** the authors' AI referee reports under `notes/reviews/` (paper1_v1/v2/v3), and none of the four specialist auditors did either. However, the review **is not fully blinded** in two respects: (i) the main paper's Appendix A and Supplement S7.1–S7.2 — which describe the AI-collaboration protocol, the review rounds, and the high-level outcomes ("the eight referee reports recommended major revision") — are *part of the submitted material* and were read; and (ii) the environment's web search surface partially overlapped with the paper's own citation-verification trail. The detailed AI referee findings in S7.3 and `notes/reviews/` were **not** inspected. This report was therefore prepared independently of, and prior to consulting, any prior critique.

### H.3 Confidence summary

- **Theory:** high confidence — independently re-derived by two parties (Lead + theory-adversary) with distinct scripts; no error found.
- **Empirical:** high confidence on the point estimates (reproduced exactly); moderate confidence on the bootstrap intervals (not re-run).
- **Case study (Bending Spoons):** high confidence on arithmetic/accounting; moderate confidence on the ultimate source figures (raw filings not in repo).
- **Regulatory/accounting/tax claims:** high confidence (verified verbatim against primary sources by two parties).
- **Citations:** high confidence on 13 load-bearing references; moderate on the 8 bibliographic-only and the few 2025–2026 practitioner sources.

---

*Report prepared by the Team Lead, integrating the independent first reports of four specialist auditors (theory, acquirer, reliability, citations), each of which is reproduced in full alongside this report in `/root/outputs/rule-of-40-referee/`.*
