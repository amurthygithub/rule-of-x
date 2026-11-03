# Paper 1 revision plan (round 1 → v2)

Consolidates the 12 round-1 reports and the second assumptions round:
- Opus: referees 1–4 and the four practitioner panels;
- Fable: four cross-model referees;
- the Fable assumptions round (notes/assumptions_round2.md).

Item IDs refer to issue_log.md. Each item's effect on Papers 2 and 3 is tracked in notes/cross_paper_impacts.md, and an item is closed only when every affected paper is regenerated.

**Verdict.** All 12 reports recommend major revision. No report finds a false theorem in the static model, and verify_theory.py passes 168/168. The descriptive core holds:
- the 95th-percentile score fell between 2016–19 and 2023–25 in every variant;
- the upper tail slopes downward;
- the gap decomposition holds;
- the numbers reproduce (73/80, 56/58 and 46 of 46 citations checked by different referees).

The inferential layer built on that core does not hold, and several headline numbers rest on parameters the panels re-grounded.

## A. Claims withdrawn or restated

| # | Claim now | Evidence | Revision |
|---|---|---|---|
| A1 | "Growth spending implies a weight on growth of 7 to 13" (abstract, intro, 5.4, discussion) | Eight reports: IM-5, IB-1, EX-2, R1-5, R2-1, FE-1, R3-4, FT-11. Excess-growth terciles give 10.5 to 1.8 (FE-1); netting out maintenance S&M gives 2.5–4.5 (R3-4); the CAC baseline gives 2.9–5.2 (assumptions round 2); a levels FOC gives 0.3–2 (R2-1); the G proxy is biased (FT-11) | Withdraw as an estimate. State that the data do not identify the decision weight. Report the bounds from each proxy and keep the theoretical distinction between screening and decision weights. **Decision D-1** |
| A2 | "Acquired growth flattens the GAAP slope"; "the size gradient and the cash steepening reflect acquired growth" | FE-2, R3-1 to R3-3, IM-3. The contrasts depend on the interval type and fail Holm (best adjusted p 0.66). E2 drops 410 of 469 affected firm-years, and imputing them returns E1's values | Withdraw. Report E1, E2 and the imputation bounds side by side, without claiming they differ. **Decision D-3** |
| A3 | T(40%) under E2 | FE-3, R3-6: 30–35% of bootstrap draws fail | Withdraw |
| A4 | The capital-intensity gap as evidence for Prop. 5 | IM-3, R2-2, FE-4, R3-5: the gap comes mostly from the capex and capitalized-software deduction (−3 to −6 with wide intervals once these are added back) | Withdraw as evidence for Prop. 5. Report it as an accounting effect |
| A5 | Anchor surplus Π and "up to 39% transient"; "the conclusion changed from 7 to −1" | IM-4, FE-5, R3-12: the firm-cluster interval is [−16, +16] | Report the intervals and say the transient share is not determined by the data |
| A6 | Size gradient "disappears" under E2 | R3-10: with period effects, E1 cash is −2.8 and E2 −0.9 | Weak and not robust under either estimand; replace "disappears" with an interval |
| A7 | "Never with a full point" | R3-14: the E2 2020–25 GAAP slope's 95% interval includes −1 | Drop; test period differences formally |
| A8 | "The 95th percentile fell" read as a shift in the frontier | IM-2, FE-7, R3 reweighting. The decline survives every variant, but reweighting to the 2016–19 growth mix removes it in E1; 2025 is back near 2016–19 | Keep the decline. Explain it as a change in composition (fast growers became scarcer); add the yearly series and the decomposition |
| A9 | Horizon upper ends of 156 (2028) and 123 (2031) | R4-F5, R2-4, FI: these come from an incoherent lower-bound case | Drop. Replace with a central path plus a tornado (EX-5) |
| A10 | "The cash Rule of 40 penalizes capital-intensive growth whatever its return"; "the Rule of X is a rule of economic profit"; "a firm cannot spend the budget twice"; "scores above R_max must reflect one of three things" | FT-12, FT-13, FT-15, R1-3, FT-10 | Add the conditions: k ≥ 1; "plus growth at the net weight"; "within one market at given retention"; "conditional on the cost structure" |

## B. Estimation

| # | Change | Source | Owner |
|---|---|---|---|
| B1 | panel_v3 sample rules: first-reported years only (139 backfilled); misclassified firms (game publishers, casino gaming, CoreWeave); captives (Exzeo); debt-only and private filers; the ASC 805 acquiree-revenue tag; Xunlei's missed acquisition | IM-1, IB-5, IM-4, R2-5, FR-3, FR-5 | sample audit (running) |
| B2 | Estimand policy. E1 is the descriptive baseline. E2 is reported with imputation bounds. A model-facing claim stands only if it holds under E1, E2 and the bounds. The timing of the switch and the two pro forma rules added after a test run are disclosed in 4.4 and App. E; E2 is also reported without those rules | FE-6, R3-1, R3-11, R3-18 | sample audit, then the P1 editor. **Decision D-3** |
| B3 | Frontier object. Report the dominance-cone order-α frontier φ(g), the object of Def. 2 and Prop. 7 (slope about −0.2 to −0.3), together with the local quantile (−0.45 to −0.56) and order-m. Calibrate ℓ to the object that maps to Ψ_χ | R3-9, FT-2 | sample audit, the core theorist and the P1 editor. **Decision D-2** |
| B4 | Inference: an exact LP solver (−0.564, not −0.59); a grid of τ (0.80–0.95) and windows (0–40% to 0–100%); B ≥ 999 with stated seeds; percentile, basic and BC intervals; Holm across the family; NaN shares reported | R3-2, R3-7, R3-8, R3-16, FE-2 | sample audit |
| B5 | Score definitions and bridge. State that the cash score is after interest and cash taxes. Report scores before SBC and after interest. Add a bridge from GAAP to FCF before SBC, after SBC, organic, and after interest | IB-3, EX-3, R2-3, FR-3, IB-2 | sample audit and the P1 editor |
| B6 | Stochastic frontier: a common frontier with JLMS, bootstrap, survivor-balanced panel, and an interpretive caveat | R3-13 | sample audit |
| B7 | Within-firm regression on g_{t+1}, under E1 and E2, with a softer interpretation | R3-15 | sample audit |

## C. Theory

| # | Change | Source |
|---|---|---|
| C1 | prop:expected: state the deterministic reorganization clock as an assumption. Prove a fluid version that covers the calibration (n_cap = 0 at 0.82 processes per wave), or relabel the pace numbers | R1-1, FT-6, FT-7 |
| C2 | Partial realization: add a stated and grounded no-retry or reversion-cost assumption, or correct the claim (retrying converges to the best draw) | R1-2 |
| C3 | cor:ceiling holds conditional on its cost structure; remove the scarce-input rent contradiction | R1-3, FT-10 |
| C4 | prop:dynamic: state the bounded C¹ HJB solution as a verification hypothesis in the proposition and the abstract, or prove its existence | R1-4, FT-5 |
| C5 | Accountability floor becomes a pass/fail ICFR constraint (Item 308(a)(3), AS 2201.A7), with cost minimized subject to it | RA-1 |
| C6 | Common mode: ITGC quality lowers the common-mode probability. Correct the reading of Kim et al. (0.60 is P(same wrong answer \| both wrong)). The full-automation error cost uses AI-review error rates with common-mode failure | RA-2, FI-5 |
| C7 | Free entry: fix the benchmark (costly customer acquisition) and the 92.5-point example; state the Cournot, date-0 entry and input-growth assumptions | R4-F4, FI-6, FT-9 |
| C8 | Errors and notation: FT-1 (b → k_u); FT-3 (one ψ convention for owned compute; the thresholds become 16.5% and 49.5% under ψ = 1); FT-4; FT-16 to FT-25; FT-20 (possible ITGC double count); FT-21 (G_i = ln NRR) | FT |
| C9 | Novelty: position against customer capital and market penetration (Arkolakis 2010; Gourio and Rudanko 2014; Drozd and Nosal 2012; Foster, Haltiwanger and Syverson 2016), the q-theory of advertising (Vitorino 2014; Belo et al. 2022), Sethi, Marris, and common-cause reliability. Demote the results that follow immediately from the functional form to remarks. Narrow the contribution list | FT-14, R1 novelty, FI |

## D. Calibration: adopt the second assumptions round in one params commit

| # | Parameter | Old → new | Expected effect |
|---|---|---|---|
| D1 | Compute share c_c | 0.20 flat → 0.06 (2025 prices), 0.12 (2028), 0.08 (2031), 0.05 (2036), each with ranges | Central threshold 42.3% → about 32–36%, horizon-dependent |
| D2 | Execution pace | ϖ 0.54 → 0.70; b̄ 0.85 → 0.67; disruption haircut dropped (double count); T_emb 2 → 1.25; κ_abs re-grounded; revealed-pace reference added | Embedded share 2.5/10/23% → about 7/20/41%; dip-crossing 9 → about 4 years; plus a go/no-go threshold (EX-4) |
| D3 | Pass-through φ | 0 → scenario {0, 0.5, 0.7} | Lower ceilings and horizons in the pass-through cases (R4-F3) |
| D4 | Capability and inference-price paths | implicit → explicit inputs to the central path | FI-1 |
| D5 | Presentation | ranges → central case plus tornado; firm-specific G; Rule of 1000 moved to an appendix | EX-5 |
| D6 | Reliability and ICFR | r̄ 0.99 → 0.98; q_M 0.998 → 0.995; ICFR line per AI application $347k → $80k; regulated multiplier range narrowed | prop:amin values; P2 invoice example and playbook gates |
| D7 | Bending Spoons | drop the annuity double charge (operating cash flow is after interest); add the return on acquisition capital and the organic score after interest (about 22); include interest and reorganization in the organic score; reword | IB-4, RA-4, FI |
| D8 | a_min upper end | Kept at 4.6% (fifth-percentile G&A share of $1–10B firms in the wider software and internet universe), with the core-sample value (5.8%) disclosed in horizons.tex: the conservative case is therefore below what 95% of sample firms spend on G&A today. Editor's choice in phase B, accepted by the lead agent (no cross-paper parameter change) | R2, FR |

## E. Presentation, citations and protocol

| # | Change | Source |
|---|---|---|
| E1 | Decision rules section: prop:levers-position and tab:levers-position (delivered by the playbook agent), placed at the end of horizons.tex. Regenerate it after D-1, B1 and D1–D2 | EX-1 |
| E2 | Use in filings paragraph: Reg G, Item 10(e), the 2022 non-GAAP C&DIs, Release 33-10751, the IPO safe-harbor exclusion (verified) | RA-3 |
| E3 | Regulatory facts: SR 26-2 / OCC 2026-13 supersede SR 11-7, with generative and agentic AI out of scope; Reg. (EU) 2026/1744 (Annex III from 2 Dec 2027, Annex I from 2 Aug 2028). Both verified at primary sources | RA-5 |
| E4 | Citations: correct Demirer, ICONIQ, Gundlach, Bonney, Terry, Hampole. Add an appendix table citing every parameter source (S&P, BCG, Korn Ferry, JOLTS, IANS, METR and others). Add the missing literature (FI's 14 references, C9) after verification | R4, FI, FT-14 |
| E5 | Protocol appendix: <br>• the panels were AI agents, each playing several roles; <br>• the model used by each agent; <br>• the timeline; <br>• the estimand switch and the post-test-run rules; <br>• reclassify E.5 (a researcher degree of freedom, not an error); <br>• the licenses cover the text and code, not the ideas | IM-6, RA-6, R3-11, EX-9 |
| E6 | Length: trim to about 75 pages, for example by moving the Rule of 1000 to an appendix, demoting the immediate propositions and moving robustness tables to the appendix | editor |
| E7 | Replication: estimate_organic.py goes into the README and the run order; code/regenerate_all.sh rebuilds all three papers | R3-17 |

## Decisions (author, 13:53 UTC−7)
- **D-1, growth weight (A1):** withdraw "7 to 13" and report the bounds from each method. Papers 2 and 3 stop using X = 9 as a central value: every example is evaluated across the bounds, and the text says where the sign of a result flips.
- **D-2, frontier object (B3):** the author asked for the lead agent's call. Model-facing claims and the ℓ calibration use the theory's object, Ψ_χ, the order-χ frontier among firms growing at least g. The local conditional quantile is reported alongside it as a labeled descriptive statistic. The choice was fixed before any Ψ_χ (dominance-cone) estimate on panel_v3 existed. Correction (29 Oct, from the editor's protocol check): the sample-audit agent's superseded IRLS test run had already printed v3 local-quantile slopes and a familywise result at 13:39 UTC−7, 14 minutes before the decision. Neither the author nor the lead agent had seen them, and no cone statistic had been computed. The protocol states this precise version.
- **D-3, estimands (A2, B2):** E1 is the baseline. A model-facing claim stands only if it holds under E1, E2 and the imputation bounds. The timing of the switch and the post-test-run rules are disclosed.
- **D-4, parameters (D):** adopt every round-2 value in one params commit.

## Sequence
1. panel_v3 and the new estimates (the sample audit, running).
2. Then the growth-weight analysis (on the v3 numbers).
3. Then the params commit (D) and regenerate_all.sh.
4. Then the P1 editor rewrite (A, C, E), with P2 and P3 propagation per the register.
5. Round-2 reviews on models different from the drafters'.
6. Final audit.
7. Then the author's own verification before arXiv submission.
