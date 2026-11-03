# Paper 1: response to the round-1 reviews

*The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation*, version 2. Prepared for the round-2 reviewers and for the author.

Documents: main paper `paper1/paper1.pdf` (77 pages) and Supplementary Appendix `paper1/supplement.pdf` (44 pages). Locations are written M (main paper) or S (supplement), with section, label or table, and page; supplement sections, tables, equations and results carry an S prefix. Numbers are those of the v2 build and are conditional on their scenario inputs; "a -> b" means the round-1 value a became b.

Actions: **Fixed** (the finding is addressed in full), **Partly** (some of it is addressed; the row says what is not), **Declined** (deliberately not done; the row gives the reason), **Not done** (accepted or open, but not addressed in this round).

## One-page summary

### Counts by action

| Report | Findings | Fixed | Partly | Declined | Not done |
|---|---:|---:|---:|---:|---:|
| IB: Investors and bankers panel | 8 | 1 | 6 | 1 | 0 |
| IM: Investment management panel | 10 | 4 | 5 | 0 | 1 |
| EX: Executives panel | 18 | 0 | 8 | 0 | 10 |
| RA: Risk, audit and regulatory panel | 9 | 4 | 4 | 0 | 1 |
| R1: Referee 1, theory | 26 | 23 | 3 | 0 | 0 |
| R2: Referee 2, finance and accounting | 14 | 6 | 4 | 1 | 3 |
| R3: Referee 3, econometrics, Opus | 19 | 17 | 1 | 0 | 1 |
| R4: Referee 4, IO and AI | 19 | 9 | 8 | 0 | 2 |
| FR: Cross-model finance referee, Fable | 14 | 10 | 3 | 0 | 1 |
| FI: Cross-model IO/AI referee, Fable | 19 | 9 | 7 | 0 | 3 |
| FE: Cross-model econometrics referee, Fable | 11 | 7 | 4 | 0 | 0 |
| FT: Cross-model theory referee, Fable | 25 | 23 | 2 | 0 | 0 |
| **All 12 reports** | **192** | **113** | **55** | **2** | **22** |
| Revision-plan items (A1-E7, counted separately) | 41 | 31 | 8 | 1 | 1 |

Of the 192 findings, 113 (59%) are fixed, 55 (29%) partly addressed, 2 declined and 22 (11%) not done. The referee reports (R1-R4, FR, FI, FE, FT) are mostly fixed. Of the 22 findings not done, 10 come from the executives panel (EX): presentation requests (an executive summary, a box on how not to use the numbers, more rows in the ceiling table) and practitioner extensions (seat compression, labor-law timelines, regulatory dates) that this round did not take up. Several rows marked Partly contain a declined component; its reason is in the row and in the list of declines below.

### The five changes that matter most

1. **The growth weight of 7 to 13 is withdrawn; the decision weight is conditional.** The spend ratio is robust (3.0 to 3.5), but the alpha(X - k) it should reveal ranges from 0.05 to 10.1 across methods, so the data do not identify the weight firms act on (M §5.4 p.40). The marginal-value result holds under a stated verification hypothesis (H), in the proposition and in the abstract (M prop:dynamic p.18); existence of the HJB solution is not proved. (IB-2, R1-5, R2-1, FE-1, FT-5, FT-11; plan A1, C4.)
2. **The sample and the inference are rebuilt, and claims that did not survive are withdrawn.** panel_v3 (292 firms in the baseline) applies rules R1, R3 and R4 in full and R2 and R5 in part. The theory's frontier, Psi_chi, is primary: slopes -0.22 (GAAP) and -0.16 (after SBC), negative in all four views (E1, E2 and the imputation bounds M = 4 and 8) but not significant after the familywise correction (Holm, Romano-Wolf; 999-replication firm-cluster bootstrap). The P95 decline (11.9 to 12.7 points) is kept and read as composition. The E1-E2 differences and T(40%) under E2 are withdrawn; the capital-intensity gap is now an accounting effect, and the decline of the upper tail with scale weak and not robust. (IM-1, IM-3, R2-2, R2-5, R3-1 and other R3 and FE rows; plan A2-A8, B1-B7; M §4-5 p.33-42; S6.)
3. **The horizon upper ends of 156 and 123 are dropped for a central path with a tornado.** The central maximal score is 56, 60 and 66 in 2028, 2031 and 2036 if all selling and marketing buys growth, and 40, 45 and 55 if none does; market growth gives the largest 2036 swing (58 to 83). Pass-through scenarios are added. The realized share of benefits by 2036 is 41% (23% in v1) and the embedded share 61%, now kept apart; the revealed 2022-24 pace (8.2 points of GAAP margin) is reported beside the path. (R2-4, R4-F5, R1-17, EX-4, FI-2; plan A9, D2, D3, D5; M §7.3 p.52-56, Tables 5 and 6.)
4. **The compute share is re-grounded, and the full-automation threshold falls from 42.3% to 31.0%.** c_c moves from 20% flat to 6% of revenue at 2025 prices (12/8/5% in 2028/2031/2036), and error losses use no-review rates at full automation (FI-5). The threshold is 27 to 51% over the credible range of c_c, 36.0/32.6/30.1% by horizon, and 36.3% or 38.5% with pass-through of 0.5 or 0.7. The ceiling is a bound at its cost structure, not a law. (R4-F2, R4-F3, FI-5, R1-3, FT-10, in part FI-1; plan D1, C3; M §7.2 p.49-52, Table 4.)
5. **The theory is corrected where the referees found errors or gaps.** prop:expected takes the uniform clock as an assumption and adds a divisible version (e) and random freezes (f); partial realization is part of the definition. The accountability floor is a pass/fail ICFR constraint (AS 2201 A7; Item 308(a)(3)) with a cross-type common mode. Its remote threshold is 5% a year, grounded in adverse SOX 404(b) attestations (4.6% for fiscal 2020, 5.8% for 2021; Audit Analytics), with 1% as a sensitivity. No all-AI design on one provider passes at either threshold, and the cheapest admissible design is one human over one AI layer (0.090% of revenue at $1 billion; over two AI layers, 0.095%, at 1%). Free entry has customer capital and a full-cost bound; one psi convention is used throughout; the score budget holds within one market at given retention. (R1-1 to R1-4, R1-15, FT-1 to FT-10, FT-20, RA-1, RA-2, R4-F4; plan C1-C7; M §3, App. A; S2-S3.)

## Declines and open items

### Declines and their reasons

- **Existence of the HJB solution (R1-5, FT-5, plan C4; Partly).** Not proved. The result is stated under verification hypothesis (H), and a new part (e) covers the case with no root. A proof of existence for the general state space is beyond this revision.
- **Full rule R2, software-only classification (B1, IB-5, R2 rows; Partly).** Applying the rule to the whole panel needs every registrant's business description. v2 applies it as a classifier to the 16 named firms only: 4 are classed as non-software (38 firm-years). The classifier misses THQ, Take-Two, Roblox, Unity and CoreWeave, so the paper reports it as a partial check.
- **Foreign filers under rule R5 (B1; Partly).** Not tested for listing status, because their cover pages report shares outstanding rather than float. R5 is a flag and a sensitivity: 26 firm-years of 7 firms.
- **The a_min upper end (R2-10, D8; Declined).** Kept at 4.6%, the value of the cross-paper params commit for Papers 1 to 3, which is drawn from the wider software and internet universe. The core-sample 5th percentile of G&A, 5.8%, is disclosed in M §7.2. Changing the value needs a params decision across the three papers, and it would raise the conservative threshold.
- **Score-to-multiple bridge, screening recipe and market test (IB-2; Declined).** The market test is moot because the 7-to-13 weight is withdrawn. A bridge from score to multiple needs price data, which the panel does not hold; it is listed as future work.
- **Competing-interests statement (EX-9; part of a Partly row).** Declined by the author; the decision is recorded in M Appendix B.3, Table 9.
- **Renames (FT-22, R1-23; part of Partly rows).** The price p and the process index p are kept. Each is local and listed in Table S1.

### Open items (not done in this round)

- **Practitioner presentation (EX-6, EX-8, EX-10, IM-7).** No executive summary or glossary, no 'how not to use these numbers' box, no typical-firm row or negative-k column in the ceiling table, and no holdout or returns test.
- **Use in filings (RA-3, plan E2).** The sources (Reg G, Item 10(e), the 2022 C&DIs, Release 33-10751) are verified and listed in Table S7, but the paragraph is not written.
- **Netting of AI channels (R4-F7, FI-13, EX-11, EX-15).** There are no rows in Table 1 for seat compression or AI-native entry, and no business-stealing remark.
- **Decomposition of G* (R4-F19).** The tornado ranks the parameters, but the additive decomposition is not stated.
- **Element and disclosure details (FR-11, R2-9, R2-11, R2-13, FI-16, R3-18).** Not addressed: the cash-flow element choices, ASC 606 timing, the CAMT threshold, fee grounding, and deferred revenue. The text does not say that E2 pairs organic growth with consolidated margins.
- **Go/no-go threshold for execution (EX-4, plan D2).** Not given. The revealed 2022-24 pace (8.2 points of GAAP margin) is reported beside the path.
- **Companion-paper dependence (EX-9, R4-F11).** The ITGC and dip-budget derivations still cite the unpublished Paper 2.
- **Wording (FI-17).** 'Mature asset-light firm' is kept.

## Point-by-point responses

### IB. Investors and bankers panel (panel_investors_bankers.md). IB-1 to IB-5 are the issue-log IDs; IB-6 to IB-8 are the panel's top-10 changes 7, 8 and 10, which the log did not number.

| ID | Finding | Action | Where in v2 | Numbers and notes |
|---|---|---|---|---|
| IB-1 | Screening weight drawn too sharply: Bessemer's regression implies about 2 to 9; decision weight should be shown by owner's discount rate | Partly | M §3.6 lem:valuation2 p.19 and S2.2 p.5 (screening weight as a duration, 1.8 to 6.2 over persistence; 'a weight of 2 to 3 reflects a choice of persistence'); M §8.1 p.59; Table S7 p.30 lists Bessemer's 2 to 9 | Decision weight by owner's discount rate (panel B3) not added. |
| IB-2 | Add a score-to-multiple bridge, a screening recipe and a market test of 7 to 13 | Declined | - | Market test is moot: the 7-to-13 weight is withdrawn (A1, D-1). The score-to-multiple bridge and recipe were not added: no price data in the panel; listed as future work. |
| IB-3 | Report scores on FCF before SBC, the practitioners' basis, by period | Partly | M §4.6 p.36 (2023-25 medians and pass rates on GAAP, adjusted, FCF before SBC and after SBC; median SBC 12.3% of revenue) | The FCF-before-SBC basis is reported for 2023-25 only, not by period; the P95 change on that basis is not reported. |
| IB-4 | Bending Spoons annuity charges financing twice (OCF is after interest under US GAAP); report return on acquisition capital; organic score after interest | Fixed | M §6 rem:acquired-bounds p.44, case p.45-47, Table 3 tab:acquired-score p.48; M §1 p.4; M §8.3 p.60 | 2025 charged-as-capital range 84.4-92.8 (v1) -> 87-114, against a margin before interest; return on time-weighted acquisition capital 22-28% before and 14-22% after depreciation; Q2 2026 organic score 37 -> 22 to 44 depending on interest and reorganization. |
| IB-5 | Sample includes game publishers, casino gaming, CoreWeave and a captive firm (Exzeo); the 0.54 success rate measures pilot attrition | Partly | M §4.2 sec:data-rules p.33 (rules R2, R3); M §7.3 p.52 (pace); Table S7 p.30 | Exzeo 2025 excluded (R3). R2 classifies only the 16 named firms (4 non-software: Activision, Bally, EA, PLAYSTUDIOS); it misses THQ, Take-Two, Roblox, Unity, CoreWeave, so game publishers stay in the main sample except in sensitivities. Success rate re-grounded: central 0.70 and fast 0.80 from outcome surveys (BCG 2020); 0.54 now the slow case. |
| IB-6 | Make the Bending Spoons illustration even-handed: NRR sentence, organic score after interest, a second serial acquirer, the company's own IRR hurdle, move fully charged figures out of abstract and intro | Partly | M §6 p.45-47; M §1 p.4 | NRR sentence rewritten (5-9% a year before new customers; new customers more than offset it in Q2 2026); organic after interest given; fully charged figures out of abstract and intro. No second acquirer (Constellation) and no IRR hurdle in Paper 1. |
| IB-7 | Separate the measurement lens from the decision rule for acquisitions and leverage | Partly | M §6 p.47 (charged in full, acquired growth raises R^A_X iff X > k^acq; 'charge interest or a cost of capital, not both') | The leveraged-buyout illustration (interest of about 23% of revenue) was not added. |
| IB-8 | 2026 price regime: pass-through variant, seat-compression scenario, 'how not to use' box | Partly | M §7.2 p.52 (pass-through phi = 0.5 and 0.7); M §7.3 p.54-55 (central path with pass-through); Table 6 p.55 | No seat-compression scenario and no 'how not to use' box. |

### IM. Investment management panel (panel_investment_management.md). IM-1 to IM-6 are the issue-log IDs; IM-7 to IM-10 are the panel's top-10 changes 7 to 10.

| ID | Finding | Action | Where in v2 | Numbers and notes |
|---|---|---|---|---|
| IM-1 | Backfilled years: 138 firm-years not first reported; restate the decline | Fixed | M §4.2 rule R1 p.33; M §4.1 p.33 | Rule R1 excludes 140 firm-years (98 pre-listing comparatives, 40 fiscal-2010 years, 2 later-vintage); P95 decline now 11.9 (GAAP) and 12.7 (cash) points, was 12 and 15. |
| IM-2 | Report the yearly series; the decline is a 2023-24 trough; the slope averages two regimes | Fixed | M §5.2 p.38; Table S5 tab:yearly_v3 p.28; M §5.3 p.39 (period slopes) | GAAP P95 low 41.5 in 2024, 51.4 in 2025; 2016-19 to 2025 change -4.5 [-17.7, +8.7]. GAAP Psi slope steepened after 2020 (difference -0.38 [-0.60, -0.16]); cash did not. |
| IM-3 | Multiple testing: E1-E2 differences fail a familywise correction; capital-intensity gap is an accounting identity | Fixed | M §5.1 p.36-38 (Holm, Romano-Wolf); M §5.6 p.40; M §5.9 p.42; Table S4 p.28 | 38 E1-E2 contrasts: none survives Holm at 5% under any interval type; no difference claimed. Capital-intensity gap -12.5 [-20.1, -3.9] after SBC but -4.6 [-14.6, +6.0] with capital spending added back; reported as an accounting effect. |
| IM-4 | Calibration anchor: 20 firm-years from 12 firms, includes captive Exzeo and an unflagged Xunlei acquisition; report firm-cluster intervals | Partly | M §5.8 p.42; M §7.3 p.52; Table 5 tab:calib p.54 (lower panel) | Anchor now E1 calibration rule: 13 firm-years of 7 firms, Exzeo excluded (R3), Xunlei 2025 flagged (R4(b)); firm-cluster 90% intervals: Pi_ub -1.3 [-18.2, +16.4], Pi_lb +19.5 [+8.1, +26.5]. Two-year average margins not adopted. |
| IM-5 | Growth weight 7 to 13 rests on an unidentified elasticity; register label circular | Partly | M §5.4 p.40; M §3.6 p.18-19; M §8.1 p.59; Table S7 p.30 | Withdrawn. alpha(X - k) ranges 0.05 to 10.1 across methods, X - k about 0.1 to 40 for alpha in [0.25, 0.45]; spend ratio 3.0 to 3.5 reported as a statistic. alpha reclassified as a scenario value (class d) in Table S7; notes/assumptions_register.md still lists it as class c (not changed in this round). |
| IM-6 | Protocol must say each panel is one AI agent playing several roles | Fixed | M App. B.2 p.74; S7.3 p.38 |  |
| IM-7 | Add a holdout and a screen test; say the paper does not test returns | Not done | - | No out-of-sample or returns test was run. The text cites Lee (2024) as the only study of the rule as a screen (M §1 p.3, §2 p.4). |
| IM-8 | Discipline scenario headlines: no upper end alone, co-headline high compute, pass-through row, tornado of the embedded share | Partly | M abstract; M §7.2-7.3 p.49-56; Tables 4-6 | Ranges replaced by a central path and a tornado; pass-through thresholds given. The high-compute case is reported in M §7.2 and labelled infeasible at full automation, not co-headlined. The tornado is on the score, not on the embedded share. |
| IM-9 | Bring the assumptions register into line: precedent column, reclassify alpha and change capacity, list G and S&M as assumptions | Partly | Table S7 p.30 (grounding class per parameter); M §7 p.49 | Paper-side: classes shown in Table S7; alpha class d there. The register file itself was not edited in this round (not the editor's file). |
| IM-10 | Add a practitioner box and coverage limits | Partly | M §8.6 p.61; S6 p.24 (known limitations) | Coverage limits stated (private AI firms absent; $100 million nominal threshold). No practitioner box. |

### EX. Executives panel (panel_executives.md). EX-1 to EX-10 are the panel's top-10 changes (the issue log numbered 1 to 5 and 9); EX-11 to EX-18 are its further changes.

| ID | Finding | Action | Where in v2 | Numbers and notes |
|---|---|---|---|---|
| EX-1 | Add budgetable decision rules with a worked median $1-5B firm | Partly | M §7.5 sec:levers-position p.57, Proposition 9 prop:levers-position, Table 7 p.58 | Lever rankings by position, with a ratio test that does not need the level of the decision weight. Not the seven finance-unit rules, and no worked $1-5B firm. Table 7 is regenerated on panel_v3. |
| EX-2 | Decision weight conditional on attribution; translate into payback | Partly | M §5.4 p.40 | The weight is withdrawn and the bounds by method are reported (zero baseline, netting maintenance, fixed G of 5, 8, 12%: alpha(X - k) 2.1 to 2.7). No payback translation. |
| EX-3 | Lead with a score bridge on the basis practitioners use | Partly | M §4.6 p.36; Table S6 tab:bridge_v3 p.29 | Bridge GAAP -> adjusted -> FCF before SBC -> after SBC (2023-25 medians and pass rates), and a bridge before interest and cash taxes: adding them back lifts the P95 by 4.8 to 5.2 points in both periods and leaves the decline in place (-11.0 against -11.4 on the same firm-years). Not shown for $1-5B firms; no KPI card. |
| EX-4 | Re-ground execution pace and state its decision implication (go/no-go) | Partly | M §7.3 p.53-54; Table 6 p.55 | Re-grounded in the params commit: success 0.70/0.80, realized share 0.67, embedding 1.25 years, change capacity 10% [5, 22]; disruption haircut removed (double count). Realized share by 2036 23% -> 41% (embedded 61%); dip crossed after 9 -> 4 years; revealed 2022-24 pace (8.2 points of GAAP margin) reported beside the path; slow execution in text and tornado. No payback or go/no-go threshold. |
| EX-5 | Central case plus tornado; firm-specific market growth; Rule of 1000 to an appendix | Partly | M §7.3 p.52-56, Tables 5-6; S5 supp:rule1000 p.24 | Central path 56/60/66 (2028/31/36); tornado over G, execution, surplus, attribution, anchor, target, capital, pass-through, dip, sample. Rule of 1000 moved to S5. Market growth is held at the sample median (12.7%) and varied in the tornado; firm-specific G was not used. |
| EX-6 | Make Table 10 usable: typical-firm row, k = -0.3 column, tax and fee grounding, security baseline | Not done | M §7.2 p.49-51, Table 4 | Table inputs are now generated, but no typical-firm row, no negative-k column, and the CAMT threshold, fee and security-baseline caveats were not added. |
| EX-7 | Ground the accountability floor in disclosed fees and control failures; add a guardrail | Partly | M Proposition 5 prop:amin p.26; Remark 6 rem:amin-values p.72; M §8.5 p.61 | The floor is now a pass/fail constraint, and no all-AI design on one provider passes (the guardrail in substance). The remote threshold is now grounded in adverse auditor attestations (4.6% of SOX 404(b) attestations for fiscal 2020, 5.8% for 2021; Audit Analytics). Audit-fee grounding (Dropbox) and ITGC scaling by agents were not added. |
| EX-8 | Add a 'how not to use these numbers' box | Not done | - | Scenario caveats appear throughout M §7 and §8.6, but there is no box. |
| EX-9 | Fix the licence, add a competing-interests statement, remove dependence on unpublished work | Partly | Title-page footnote; M App. B.3 Table 9 p.75 | Licences clarified: they cover the text and the software, not the ideas. Competing-interests statement declined by the author (decision recorded in Table 9). Some numbers (ITGC lines, dip budgets) are still sourced to the companion paper. |
| EX-10 | Plain-language pass, executive summary and glossary | Not done | - | Not done in this round. |
| EX-11 | Seat compression as a negative G channel in the AI map | Not done | M Table 1 tab:ai-map p.24 | Lever 4 (M §7.4 p.56) mentions shrinking seat counts; Table 1 has no row. |
| EX-12 | Common mode beyond model providers (identity, EDR, cloud region) | Not done | - | Assumption 7 still treats common mode across model providers only; identity, EDR and cloud-region dependencies not added. |
| EX-13 | Labor-law minimum timelines (WARN, EU 98/59/EC) as lower bounds on embedding time | Not done | - | No labor-law lower bound on embedding time; the central embedding time stays 1.25 years. |
| EX-14 | Regulatory dates in Definition 3 (EU AI Act Annex III, Product Liability Directive) | Not done | Table S7 p.30 records the AI Act dates | Not in the text of Definition 3. |
| EX-15 | Competition: an entrant's surplus is drawn from incumbents' headroom | Not done | - | No business-stealing remark (see R4-F7). |
| EX-16 | Leadership and strategy hazard: range and sensitivity row | Partly | M Table 6 p.55 (slow and fast execution) | No separate hazard sensitivity. |
| EX-17 | Hallucination rates vary tenfold with the judge | Not done | - | The range of hallucination rates is not qualified by the judge used. |
| EX-18 | Spend ratio with S&M plus a share of R&D | Not done | - | The spend ratio still uses selling and marketing only (M §5.4 p.40). |

### RA. Risk, audit and regulatory panel (panel_risk_audit_regulatory.md). RA-1 to RA-6 are the issue-log IDs; RA-7 to RA-9 are the panel's top-10 changes 3, 7 and 9.

| ID | Finding | Action | Where in v2 | Numbers and notes |
|---|---|---|---|---|
| RA-1 | Accountability floor must be a pass/fail ICFR constraint, not a cost trade-off | Fixed | M Proposition 5 prop:amin(b)-(c) p.26-27; Remark 6 rem:amin-values p.72; M §7.2 p.49-50; M §8.5 p.61 | Floor = cost of the cheapest admissible design (AS 2201 A7; Item 308(a)(3)). Remote threshold: central 5% a year, grounded in adverse auditor attestations (4.6% of SOX 404(b) attestations for fiscal 2020 and 5.8% for 2021, Audit Analytics, cited), with 1% as a stricter sensitivity. No all-AI design passes at either threshold. Cheapest admissible design: one human over one AI layer at 5% ($0.90 million, 0.090% of revenue); one human over two AI layers at 1% ($0.95 million, 0.095%). Bottom-up floor 0.24 -> 0.23% at $1 billion, the same at either threshold. |
| RA-2 | Independence assumption: common shocks (override, shared data, ITGC failure, automation bias); verify Kim et al. | Fixed | M Assumption 7 ass:layers p.26; S2.6 supp:model-commonmode p.7 | Cross-type term p^cc added; ITGC quality lowers p^cc and p^cm; Kim et al. read correctly (0.60 = same wrong answer given both wrong); value of diversity read as an upper bound. |
| RA-3 | Add a 'Use in filings' paragraph (Reg G, Item 10(e), 2022 C&DIs, Release 33-10751, IPO safe harbor) | Not done | - | The sources are verified and listed in Table S7 (p.30), but the paragraph was not written. |
| RA-4 | Bending Spoons wording: the company does not report the score; organic growth unaudited and estimated; material weaknesses | Fixed | M §6 p.45-47; M §1 p.4; M §8.3 p.60 | 'Computed from reported revenue growth and GAAP operating margin; the company does not report the score'; company organic measure described as unaudited and estimate-based; material-weakness sentence quoted; transaction and reorganization costs in the GAAP channels. |
| RA-5 | Regulatory anchors: antitrust cap, SR 11-7 superseded, EU AI Act dates | Fixed | M Assumption 1 ass:market p.10; S2.5 p.6 (SR 26-2, OCC 2026-13); Table S7 p.30 | Paper 1's text does not use the AI Act dates; they are recorded in Table S7. |
| RA-6 | Protocol: panels are AI agents, two-day timeline, competing-interests statement | Partly | M App. B p.74-77; S7 p.36-40 | AI panels and timeline stated. Competing-interests statement declined by the author (decision of 10:50, recorded in Table 9). |
| RA-7 | Audit-reliance facts (AS 2201 B28-B31, AS 1105) and filer-status precision | Partly | M §8.5 p.61 | Emerging-growth exemption and first-report exemption stated. AS 2201 B28-B31, AS 1105 and 18 U.S.C. 1350 not added. |
| RA-8 | Antitrust statements and lever framing (merger review, rents versus market power) | Partly | M Assumption 1 p.10; M Proposition 8(e) p.43; M §7.2 p.52 | 'Merger control' in the share cap; acquisitions in markets already served draw on the same headroom; 'the score does not distinguish such a rent from market power'. No Merger Guidelines or Fisher-McGowan citation. |
| RA-9 | Tax and capitalization precision: CAMT threshold, foreign property, ASU 2025-06 | Partly | M Remark 2 rem:taxes p.24 | The 100% allowance exclusion for property used abroad (psi < 1) is stated. The CAMT threshold sentence and ASU 2025-06 were not added. |

### R1. Referee 1, theory (referee1_theory.md). IDs are the report's finding numbers; the issue log's labels R1-4 and R1-5 refer to the report's Findings 5 and 6/7. Detail: notes/theory_fixes_v2.md, Sections 1-2.

| ID | Finding | Action | Where in v2 | Numbers and notes |
|---|---|---|---|---|
| R1-1 | Error: random reorganizations do not give the fixed program clock; the upper bound of prop:expected fails (counterexample) | Fixed | M Definition 4 def:attainable(b) p.29; Proposition 7 prop:expected(c), (e), (f) p.30-31; S3 p.8ff (proof); S2.7 p.7 | Uniform clock stated as an assumption; disruptions in calendar time; random freezes handled in part (f) with corrected bounds; divisible-program version (e) is what the calibration computes. |
| R1-2 | Error: 'partial realization lowers the converged level' is false under free retry | Fixed | M Definition 4(b) p.29 (realized share fixed per process, an assumption with grounding); M §3.10 intuition p.31 | Stated as an assumption (a second migration does not change the share). |
| R1-3 | Error: cor:ceiling bounds only a firm at the full-automation cost structure | Fixed | M Corollary 4 cor:ceiling(a)-(c) p.28; M §7.2 p.49; M §8.3 p.60 | 'A bound at that cost structure, not on observed scores; a firm with leaner costs can score above it.' |
| R1-4 | Error: 'alpha < 1/2 is exactly the range where the timing convention matters' is false | Fixed | S1 Lemma S1 lem:timing(c)-(d) p.3; M §3.1 p.11 | For alpha < 1/2 the contemporaneous convention is non-convex for every k > 0; for alpha >= 1/2 only when k is large relative to kappa. |
| R1-5 | Gap: prop:dynamic(b)-(d) assume a bounded C^1 solution of the HJB | Partly | M Proposition 2 prop:dynamic(b) p.18 (hypothesis (H)); abstract; M §1 p.2; M §8.1 p.59; M §8.6 p.61 | Declined to prove existence: the problem is singular at both ends (shown in the proof) and a proof is beyond this revision. Stated as verification hypothesis (H); every claim that a firm acts on the marginal value of revenue is conditional on (H), including the abstract's. |
| R1-6 | Overclaim: the screening and decision weights are one marginal rate of substitution at different persistence | Fixed | M §3.6 p.18-20, Lemma 5 lem:valuation2(e) p.19; S2.2 p.5 | 'Both weights are marginal rates of substitution ... for perturbations of different persistence.' |
| R1-7 | Overclaim: '7 to 13' is 3.3/alpha over an unsourced range of alpha | Fixed | M §3.6 'Implication for measurement' p.19; M §5.4 p.40; abstract; M §1; Table S7 | Withdrawn; spend data bound X - k from below only for a given proxy, and the proxies give 0.05 to 10.1 for alpha(X - k). |
| R1-8 | Overclaim: Rule-of-X lines are iso-score lines, not iso-value lines | Fixed | M §3.3 p.12-13; Remark 3 prop:general(c) p.32; M §1 p.2 |  |
| R1-9 | Overclaim: the economic-profit generalization is a change of variables (Marris-Gordon) | Fixed | M §3.11 p.32-33; Remark 3 prop:general p.32; S1 Remark S4 rem:general-phi p.3 | Stated as an identity that 'adds no result'; the conditions for carrying results beyond software listed. |
| R1-10 | Overclaim: the 1/alpha advantage of the growth engine is an artifact of measurement | Fixed | M Corollary 3 cor:priorities(ii)-(iii) p.17; M §7.4 p.56; M §9 p.62 | Stage ranking stated as conditional on a decision weight that falls with share. |
| R1-11 | Gap: results that need only concavity are not separated from isoelastic ones | Fixed | S1 Remark S4 rem:general-phi p.3 |  |
| R1-12 | Gap: the score budget needs zero-spend growth of at least G | Fixed | M Proposition 1 prop:budget p.15; S1 Remark S1(b), (d) p.1; abstract ('within one market') |  |
| R1-13 | Gap: hidden assumptions in the setup and the attainable frontier | Fixed | M Assumption 2 p.10; Assumption 8 ass:program p.29; Definition 4 p.29; M §7.3 p.52 ('describes one firm type') |  |
| R1-14 | Unclear: the growth-rate convention matters at extreme scores | Fixed | S2.1 supp:model-rates p.5; M §3.1 p.10 |  |
| R1-15 | Gap: taxes: replacement capital deducted at once, growth capital not; rem:owncompute uses psi = 0 | Fixed | M Remark 2 rem:taxes p.24; Remark 7 rem:owncompute p.72; M §7.2 p.51 | One psi convention. Owning compute pays iff the vendor markup exceeds 3.3G at psi = 1: 20.1%/60.4% (v1) -> about 17%/49% (exactly 16.5%/49.5%) at G = 5%/15%; 33%/74% at psi = 0. |
| R1-16 | Unclear: the model section hard-codes E1 slopes although E2 was model-facing | Fixed | M §3.7 p.20; S2.3 p.6 | Superseded by D-2: the section uses the Psi_chi slopes -0.22 (GAAP) and -0.16 (after SBC) from generated macros. |
| R1-17 | Unclear: 'embeds about 23%' is the benefit-weighted share | Fixed | M §7.3 p.54; Table 5 tab:calib p.54 (column 'Realized b-bar E'); abstract; M §1; M §8.2; M §9 | Realized and embedded shares now distinguished: realized 41% by 2036, embedded 61%. |
| R1-18 | verify_theory.py does not test several claims the text says it checks | Fixed | code/verify_theory.py (sections 28a-28s); M §3 opening p.9 | 189 checks. Live run 180/189 before the coordinator's fix of the script's own u_rev line; 189/189 in a scratch copy with that fix (the coordinator is rerunning it on the live repo). |
| R1-19 | Overclaim: novelty; uncited precedents (Sethi, Gourio-Rudanko, Arkolakis, common-cause reliability, Marris) | Partly | M §3 opening p.9; M §2 p.4-9; M §1 p.3 | Positioned against customer capital, market penetration, optimal advertising, q-theory of advertising and common-cause failure; immediate results demoted to lemmas and remarks; contribution list narrowed. Declined: Baumol-Panzar-Willig (1982) and Sutton, not in the verified bibliography, so the contestability sentence stays uncited. |
| R1-20 | Minor: prop:acquired-score(d) G_i = ln NRR inconsistent with the stated annual contribution | Fixed | M Proposition 8(d), (f) p.43-44; S4 p.23 | Zero-spend growth G_i = ln(1 + a), equal to ln NRR only if all revenue is subscription revenue (acquirer agent). |
| R1-21 | Minor: undefined symbol in lem:prices(a) | Fixed | S1 Lemma S2 lem:prices p.5 | b -> k_u. |
| R1-22 | Minor: draft residue in proofs and code | Fixed | S3 (proof of cor:ceiling) p.8ff |  |
| R1-23 | Minor: notation clashes | Partly | S1 Table S1 tab:notation p.2 | Most renamed; kept, with reasons: theta vs vartheta, process index p beside price p, xi beside xi_exp, bar m_0 local to one proof, mu as demand pull (each local and listed in the notation table). |
| R1-24 | Minor: small overstatements in the attainable-frontier results | Fixed | M §3.10 p.31; S2.8 Remark S8 rem:regimes p.7 |  |
| R1-25 | Minor: the score budget is sharp only for slow growth; sharper bound for extreme scores | Fixed | M Corollary 1 cor:transient(b) p.16 |  |
| R1-26 | Minor: abstract and introduction wording (intercept, concavity) | Fixed | abstract; M §1 p.2 | 'Margin at market growth'; 'plus market growth net of the capital it requires'; 'concave when capacity is installed ahead of the revenue it serves'. |

### R2. Referee 2, finance and accounting (referee2_finance_accounting.md). R2-n is the report's finding Fn.

| ID | Finding | Action | Where in v2 | Numbers and notes |
|---|---|---|---|---|
| R2-1 | Major: the 7 to 13 weight is not identified; a levels FOC gives about 0.3 to 2 | Fixed | M §5.4 p.40 | Withdrawn; levels regressions give alpha(X - k) of 0.05 to 0.24, reported among the bounds. |
| R2-2 | Major: the capital-intensity gap is driven by capitalized software | Fixed | M §5.6 p.40 | Reported as an accounting effect: -12.5 after SBC, -4.6 [-14.6, +6.0] with the deduction added back, -4.5 on a firm-median sort; growth interaction negative in only two of four views. |
| R2-3 | Major: the cash score is after interest and cash taxes in a window of interest-rate and tax-law changes | Partly | M §4.3 p.34-35; M §4.6 p.36; Table S6 tab:bridge_v3 p.29; S6 p.24-25 | Basis stated (ASC 230-10-45-17). Bridge adds back interest paid and income taxes paid (SEC frames, latest filed, not first reported): P95 up 4.8 to 5.2 points, decline -11.0 against -11.4 on the same firm-years; interest alone moves the P95 by at most 0.6. Interest income and the section 174 episode are not sized separately. |
| R2-4 | Major: pull inferred at X = 1 while firms act on X of 2 to 5; 156 from an incoherent lower-bound case | Fixed | M §7.3 p.52-55; S5 p.24 | Upper ends dropped; the lower-bound surplus is no longer scaled; the Rule-of-1000 pull multiple now uses the upper bound only (7-21 in v1 -> 9-20); the text states that a negative upper-bound surplus means a weight above one or overstated growth spend. |
| R2-5 | Moderate: pre-listing years backfilled | Fixed | M §4.2 rule R1 p.33 | See IM-1. |
| R2-6 | Moderate: the annuity middle case is a timing allocation; level annuity not matched to decay | Fixed | M Remark 4 rem:acquired-bounds p.44; Table 3 p.48 | User cost (r + d) on decayed capital added beside the level annuity, each on year-end and time-weighted capital; every row labelled before or after interest; 2025 range 87 to 114 (acquirer agent). |
| R2-7 | Moderate: SIC 7372 is not the Rule-of-40 population | Partly | M §4.1-4.2 p.33-34; Table S2 p.26 | R2 run on the 16 named firms only, as a sensitivity; no index-based sample; the broad sample is no longer used. |
| R2-8 | Moderate: E2 is mostly an exclusion sample; flag gaps | Partly | M §4.4-4.5 p.35-36; M §5.9 p.42 | Imputation bounds added; following-year flag matched by fiscal year; causal wording withdrawn. Absolute value of payments and intangible-asset purchases as flag criteria not added. |
| R2-9 | Minor: ASC 606 adoption inside the first-reported windows | Not done | - | No check of ASC 606 adoption dates against the first-reported windows. |
| R2-10 | Minor: the a_min upper end of 4.6% does not reproduce; audit cost mis-scaled | Declined | M §7.2 p.49-50 | Band kept at 0.5-4.6% (the cross-paper params commit); the text now names the source (wider software and internet universe) and discloses the core-sample 5th percentile, 5.8%, so the conservative case is below 95% of today's $1-10B firms. Size-matched audit fees not added. |
| R2-11 | Minor: tax range (CAMT threshold, state taxes) and fees by revenue channel | Not done | M §7.2 p.50 | Text still gives 15-21% federal and card-processing fees of 2-3%. |
| R2-12 | Minor: accounting statements in the acquired-growth section | Fixed | M Remark 4 p.44; Proposition 8 p.43 | GAAP channels: amortization and impairment, expensed transaction costs, restructuring (acquirer agent). |
| R2-13 | Minor: score-definition details (deferred revenue, element precedence) | Not done | - | Deferred revenue appears only as negative k in S1 Remark S1(c). |
| R2-14 | Minor: text-code inconsistencies | Partly | various | Most items are moot after the rewrite (realized vs embedded; '(r - G)k' wording; a_min = 0.06 residue removed; table notes regenerated). Not checked item by item: the T(0) sample definition and the acqCrf macro names. |

### R3. Referee 3, econometrics, Opus (referee3_econometrics.md).

| ID | Finding | Action | Where in v2 | Numbers and notes |
|---|---|---|---|---|
| R3-1 | E2 measures selection, not acquired growth; imputation returns E1 values | Fixed | M §4.5 p.35-36; Table 2 tab:estimands_v3 p.37; M §5.9 p.42 | Imputation bounds (M = 4, 8) reported as two further views; claims stand only if they hold in all four. |
| R3-2 | Interval method and bootstrap bias | Fixed | M §5.1 p.38; Tables S2-S4 | Percentile, basic, normal and bias-corrected intervals; claims checked against each. |
| R3-3 | Multiple comparisons | Fixed | M §5.1 p.38; M §5.9 p.42; Table S4 | Holm and Romano-Wolf in two families (38 contrasts; 14 headline statistics). |
| R3-4 | Weight counts maintenance S&M as growth spend | Fixed | M §5.4 p.40 | Netting maintenance S&M gives 0.99; weight withdrawn. |
| R3-5 | Capital-intensity gap mechanical; growth interaction not detected | Fixed | M §5.6 p.40 | See R2-2. |
| R3-6 | T(40%) bootstrap invalid | Fixed | M §5.2 p.39 | Withdrawn: 16 firm-years under E1, 9 under E2; 59% of E2 draws undefined. |
| R3-7 | E2 GAAP slope -0.59 is a solver approximation (-0.564) | Fixed | M §5.1 p.38; S6 p.25 | All quantile regressions solved exactly as linear programs (primal and dual agree). |
| R3-8 | tau = 0.90 and the 0-60% window unjustified | Fixed | M §5.1 p.36; Table S3 tab:grid_v3 p.27 | Grid chi 0.80-0.95 and windows 0-40%, 0-60%; wider windows undefined (only 25 firm-years grow 80% or more). Slopes -0.52 to -0.09 across views and bases. |
| R3-9 | Estimated object differs from the defined frontier; order-m unused; 'reversal' from estimator switch | Fixed | M §5.1 p.36; M §5.3 p.39; M §3.7 p.20; M App. B.4 p.75 | Psi_chi primary (-0.22 GAAP, -0.16 after SBC under E1); local quantile descriptive (-0.41, -0.35); order-m -0.22, -0.15; the protocol records that the reversal came from the estimator switch. |
| R3-10 | Size gradient without period effects; 'disappears' accepts the null | Fixed | M §5.5 p.40 | -4.1 (SE 3.4) per tenfold under E1, -1.8 with period effects; interval includes zero in every view; 'weak and not robust'. |
| R3-11 | Post hoc estimand switch disclosed incompletely | Partly | M App. B.4 p.75; Table S2 p.26 (test-run rule) | Timing and the two post-test-run rules disclosed in the protocol, and E2 reported under the test-run rule; reclassified as a researcher degree of freedom. The one-sentence disclosure in the data section itself was not added. |
| R3-12 | Anchor without sampling uncertainty | Fixed | M §5.8 p.42; Table 5 p.54 | See IM-4. |
| R3-13 | Stochastic frontier: no inference, cohort frontiers, survivorship | Fixed | M §5.7 p.41 | Common frontier per period, conditional-mean shortfall (Jondrow et al.), bootstrap intervals, balanced panel: entrant gap +13.8 [8.8, 19.4] GAAP; balanced change -2.4 [-7.5, +3.5]; survivorship caveat. |
| R3-14 | Period slope differences untested; 'never with a full point' | Fixed | M §5.3 p.39 | GAAP steepening -0.38 [-0.60, -0.16], Holm-adjusted p 0.037-0.060; cash no steepening; phrase dropped. |
| R3-15 | Within-firm timing and E2 version | Fixed | M §5.3 p.39-40 | Margin on next year's growth: -0.03 (0.05) E1, -0.15 (0.07) E2; reading softened. |
| R3-16 | Bootstrap design and reporting | Fixed | M §5.1 p.38; S6 p.25 | 999 replications, firm-cluster, seeds stated per block, splits re-estimated in draws, NaN shares reported. |
| R3-17 | Replication package does not regenerate the paper | Fixed | code/regenerate_all.sh; code/build_paper1.sh; code/REPLICATION_README.md | estimate_organic.py in the run order; one script rebuilds both PDFs. |
| R3-18 | E2 pairs organic growth with consolidated margins | Not done | - | Stated for the Bending Spoons case (M §6 p.47) but not for the E2 estimand in M §4.5. |
| R3-19 | Documentation mismatches | Fixed | M §5.5; S6 | Tables regenerated; size regression drops growth above 150%. |

### R4. Referee 4, IO and AI (referee4_io_ai.md). R4-Fn is the report's finding.

| ID | Finding | Action | Where in v2 | Numbers and notes |
|---|---|---|---|---|
| R4-F1 | Demirer et al. elasticity is within-model; it does not imply a constant compute share | Fixed | M §7.1 p.49; M §2.4 p.7-8 | Characterized as a preliminary cross-provider elasticity; aggregate elasticities smaller; the compute-share path is a scenario. |
| R4-F2 | Compute share poorly grounded and constant across horizons | Fixed | M §7.2 p.50-52; Table 4 p.51; Table S7 | c_c 20% (v1) -> 6% at 2025 prices (credible 1-30%), path 12/8/5% in 2028/31/36; METR, ICONIQ (with scope), Gundlach both sides, Stevens cited. Central threshold G* 42.3% -> 31.0%; credible range 26-72% -> 27-51%; by horizon 36.0/32.6/30.1%. |
| R4-F3 | Prices fixed in every calibrated number | Fixed | M §7.2 p.52; M §7.3 p.54; Table 6 | Pass-through phi in {0, 0.5, 0.7}: G* 36.3% (phi 0.5) and 38.5% (0.7) at 2025 prices; central path 64/63 in 2036 against 66. |
| R4-F4 | Free entry specific to Cournot; 92.5-point rent example infeasible | Fixed | M Proposition 4 prop:entry(a)-(d) p.23; S2.4 p.6; M §7.2 p.52 | Assumptions stated; example withdrawn; a rent cannot lift the score above the full-cost ceiling (part (d)); competitive score 7.5 at G = 5%, r = 10%, k = 0.5. |
| R4-F5 | Lower-bound branch of the horizon calibration has no basis | Fixed | M §7.3 p.52-56 | Dropped; central path and tornado. |
| R4-F6 | Horizon ranges: framing, misattributed low ends, technology held fixed, pace sources | Partly | M §7.3 p.52-56; Table 6 | Central path and tornado; pace sources cited and re-grounded. Capability feasibility is not dated against METR horizons, and M §8.2 still says the difference between paces lies 'not in technology'. |
| R4-F7 | Growth-engine channel is partial equilibrium; AI map omits negative channels | Not done | M Table 1 p.24 | No business-stealing remark and no seat-compression or AI-native-entry rows. |
| R4-F8 | Costs of errors: losses scaled to labor, inconsistent conservative case, units, demand channel, field evidence | Partly | M Lemma 6 lem:fullcost(c) p.71; Table 8 p.73 | FI-5 no-review rates adopted (central c_err +0.6 points). Loss severity still a multiple of the unit's labor cost; conservative-case consistency, units and the demand channel not addressed; Vaccaro et al. not cited. |
| R4-F9 | Accountability floor weakly connected to the calibrated band | Partly | M §7.2 p.49-50; M §8.5 p.61 | The central value is described as residual G&A ('assumes that none of that expense is automated'), with the bottom-up floor beside it. The 'scarce input' sentence in M §8.5 remains unformalized; L_mm scaling not discussed. |
| R4-F10 | Security, maintenance and ancillary floors: log exposure assumed, baseline uncited, build stock, asset lives | Partly | Table S7 p.30 (IANS cited) | Citation added; no class-I breach sensitivity, build stock unchanged, asset lives not reconciled. |
| R4-F11 | Sourced parameters lack citations; dependence on the companion paper | Partly | Table S7 tab:param-sources p.30-35; M §7 p.49-56 | Every external parameter source is cited in Table S7 and at the main points of use. ITGC and dip-budget derivations still cite the unpublished companion paper. |
| R4-F12 | Missing literature | Fixed | M §2 p.4-9; bibliography | Verified references added (literature pass v2). |
| R4-F13 | Adoption series splices two survey questions | Fixed | M §2.4 p.8 | Question change and the 47-159% revision stated (Allen 2026). |
| R4-F14 | ICONIQ margins do not show cost moving into cost of revenue | Partly | M §7.1 p.49 | Scope stated (AI products sold to customers, including talent and hosting); the sentence still reads 'consistent with automation shifting cost into cost of revenue'. |
| R4-F15 | Bending Spoons framing: treadmill, log vs simple rates, 'only through amortization' | Fixed | M §6 p.45-47 | See IB-4, IB-6, RA-4. |
| R4-F16 | Annuity inconsistent with the decay that sets its life | Fixed | M Remark 4 p.44; Table 3 | User cost (r + d) added. |
| R4-F17 | Under central execution the program is close to break-even; report NPV | Partly | M §7.3 p.54 | With the round-2 parameters gains first exceed the dip after about 4 years (9 in v1). No NPV reported. |
| R4-F18 | Characterizations of cited sources | Partly | M §2 p.7-9 | Lemma S2 symbol fixed; Gundlach and Demirer corrected. Not changed: 'optimal adoption' for Acemoglu-Lensman (social optimum not stated), 'valued mainly for their data' (Farboodi-Veldkamp review), 'the only quantified migration cost' (OMB), server asset lives. |
| R4-F19 | The 42% threshold is mostly taxes and compute; state the decomposition | Not done | M §7.2 p.52 | The sensitivities rank the parameters, but the additive decomposition of G* is not stated. |

### FR. Cross-model finance referee, Fable (fable_referee_finance.md). FR-n is the report's finding n.

| ID | Finding | Action | Where in v2 | Numbers and notes |
|---|---|---|---|---|
| FR-1 | Bending Spoons annuity double-charges financing (OCF after interest) | Fixed | M Remark 4 p.44; Table 3 p.48 | Double charge (1 - tau) c_fin = 8.3 points of 2025 revenue at 24%; charges now against a margin before interest. See IB-4. |
| FR-2 | Captive registrant (Exzeo) tops the anchor and the 2023-25 ranking | Fixed | M §4.2 rule R3 p.33-34; M §5.8 p.42 | Exzeo 2025 excluded by filing text; XBRL test applied (no firm-year at 50%; largest SINA 2015, 26.9%). |
| FR-3 | Cash score is levered and after tax; debt-only filers; tau = 0.18 in the inversion | Partly | M §4.3 p.34; M §4.2 rule R5 p.34; Table S6 p.29; M §7.3 p.53 | Basis stated and bridged. Debt-only filers flagged by R5 (26 firm-years of 7 firms) and dropped in a sensitivity, not excluded. The inversion still applies tau = 0.18 to every anchor firm. |
| FR-4 | 'As first reported' fails for 139 firm-years | Fixed | M §4.2 rule R1 p.33 | See IM-1. |
| FR-5 | Flag misses cheap acquisitions; use the ASC 805 acquiree-revenue tag | Fixed | M §4.2 rule R4 p.34 | R4(b) cheap-acquisition criterion (flag 469 -> 485 firm-years; Xunlei 2025 caught); R4(c) applied with the ASC 805-10-50-2(h) element, which adds no core flag (coverage thin: dimensional facts are not in the frames). |
| FR-6 | '7 to 13' set by the choice of G and of the proxy | Fixed | M §5.4 p.40 | Withdrawn; fixed G of 5, 8, 12% give 2.1 to 2.7 for alpha(X - k). |
| FR-7 | GAAP channels of acquisitions incomplete | Fixed | M Remark 4 p.44-45 | See R2-12. |
| FR-8 | Anchor surplus read as the X = 1 surplus while firms act on X > 1 | Fixed | M §7.3 p.53 | A negative upper-bound surplus is stated to mean a weight above one or overstated growth spend; the surplus is no longer scaled into upper ends. |
| FR-9 | a_min grounding cites 'our panel' but 4.6% is from the broad sample | Fixed | M §7.2 p.49-50 | Source named; core-sample 5.8% disclosed. See R2-10 for the band itself. |
| FR-10 | Small text-output mismatches | Fixed | M §1; M §6; M §5.3 | Rates now simple where stated (5-9%), within-firm coefficients from generated macros, C^acq defined as a share of current revenue. |
| FR-11 | Cash-flow element choices to disclose | Not done | S6 p.24-25 | Continuing-operations OCF with total capex, possible double count of productive assets and software, ASC 842-only lease element and the contemporaneous pairing are not disclosed. |
| FR-12 | Sample composition under current SIC 7372 | Partly | M §4.2 p.33-34 | R2 on named firms, R5 flag; Block, 3D Systems, DIRTT, Mobileye, Xperi and PRC 20-F filers remain. |
| FR-13 | NRR covers subscription revenue only; scenario life | Fixed | M §6 p.46 | 'NRR also covers subscription revenue only.' |
| FR-14 | Quarterly Q2 2026 score: repeat the comparability caveat | Partly | M §6 p.45-47; M §4.6 p.36 | Caveat in §6 ('one quarter, on the company's measure') and §4.6; the intro's first mention (p.4) does not repeat it. |

### FI. Cross-model IO/AI referee, Fable (fable_referee_io_ai.md). FI-n is the report's finding Fn; the issue log's FI-1, FI-5, FI-6 match.

| ID | Finding | Action | Where in v2 | Numbers and notes |
|---|---|---|---|---|
| FI-1 | Horizon ranges are envelopes; capability and price paths not modeled | Partly | M §7.3 p.52-56; M §7.2 p.52 | Central path with one-at-a-time sensitivities; explicit compute-share (price) path by horizon. Capability feasibility (METR horizons) is not modeled and the text does not say so. |
| FI-2 | Success probability sourced from objects it does not measure | Partly | M §7.3 p.54; Table S7 p.30 | Central 0.70 and fast 0.80 now from transformation-outcome surveys (BCG 2020), class b, cited; 0.54 (S&P Global PoC attrition) only for slow execution. Still self-reported survey outcomes, not committed-migration data. |
| FI-3 | Change capacity grounded in layoff rates | Partly | M §7.3 p.54; Table S7 | Re-grounded on a survey of how much work changes a year (WEF 2025), single restructurings and exit rates; range 5-22%; sensitivity only through slow and fast execution. |
| FI-4 | Compute share: wrong elasticity; bounds measure different objects | Fixed | M §7.1-7.2 p.49-52 | See R4-F1, R4-F2; the 55% is labelled the cost of revenue of AI products, an upper bound that includes talent and hosting. |
| FI-5 | c_err uses human catch rates for a firm with no humans | Fixed | M Lemma 6 lem:fullcost(c) p.71; Table 8 p.73 | No-review rates at full automation (central error rate 0.042 -> 0.085); c_full central 4.1 (stale v1 JSON) -> 4.3; threshold +0.6 points. L_err up to 10 not reported. |
| FI-6 | Free-entry benchmark assumes costless customer acquisition | Fixed | M Assumption 6 ass:entry p.22; Proposition 4 p.23 | Customer capital k_a added; customer capital earns a normal return, not a rent. |
| FI-7 | Pass-through derived but unused; undefined b in Lemma 3(a) | Fixed | M §7.2 p.52; S1 Lemma S2 p.5 | See R4-F3. |
| FI-8 | Central and conservative a_min are residual G&A, not accountability costs | Partly | M §7.2 p.49-50 | Text says the central value assumes none of that expense is automated, and shows the bottom-up floor (0.23% at $1 billion) separately. Not renamed 'residual G&A floor'. |
| FI-9 | Security floor: favorable xi_exp = 1; Gordon-Loeb optimality assumed | Partly | Table 8 p.73; Table S7 | IANS cited. Favorable xi_exp still 1; no L_sec sensitivity. |
| FI-10 | Horizon calibration holds headroom fixed while scaling the surplus above 100% growth | Fixed | M §7.3 p.52, p.55-56 | Rows describe one firm type at fixed share; the scaled surplus enters only the tornado, labelled 'an order of magnitude for one firm type, not a path'. |
| FI-11 | Sources behind pace, security and reliability parameters uncited | Fixed | Table S7 p.30-35; M §7 p.49-56 | Every external source cited, with what it measures and its grounding class. |
| FI-12 | Bending Spoons framings | Fixed | M §6 p.45-47; M §1 p.4 | See IB-6, RA-4. |
| FI-13 | AI map and G scenario do not net the channels the paper lists | Not done | M Table 1 p.24 | No signs by incumbent and entrant; G bands not tied to a decomposition. |
| FI-14 | Disruption and realization parameters remove 66% of attempts | Partly | M §7.3 p.54 | Disruption haircut removed as a double count (embedding probability 0.34 -> 0.70); nu_D kept for timing. No nu_D sensitivity and no partial retention of reverted builds. |
| FI-15 | Citation precision (Terry, Hampole, Demirer, Gundlach, Lee) | Fixed | M §2 p.4-9 | Literature pass v2. |
| FI-16 | Fees f = 2-3% are card-processing fees | Not done | M §7.2 p.50 | Text still gives card-processing fees of 2-3% (M §7.2 p.50); see R2-11. |
| FI-17 | 'Mature firm' at 42% market growth | Not done | abstract; M §7.2 | Wording kept ('mature asset-light firm'). |
| FI-18 | Notation reuse; time-invariant c_full across sizes | Partly | S1 Lemma S2; Table 8 note | b fixed; floors evaluated at $1 billion of revenue (stated in Table 8). The revenue at which m_0F applies is not stated in Table 5. |
| FI-19 | E2 anchor is 20 firm-years from 12 firms | Fixed | M §5.8 p.42; Table 5 p.54 | Firm-cluster bootstrap; central anchor 13 firm-years of 7 firms, with four alternative samples. |

### FE. Cross-model econometrics referee, Fable (fable_referee_econometrics.md).

| ID | Finding | Action | Where in v2 | Numbers and notes |
|---|---|---|---|---|
| FE-1 | '7 to 13' is an artifact of the proxy (terciles 10.5 to 1.8) | Fixed | M §5.4 p.40; abstract; M §1; M §8.1 | Withdrawn; terciles now 10.1, 3.0, 1.5; across methods 0.05 to 10.1. |
| FE-2 | E1-E2 contrasts not robust to interval type or familywise correction | Fixed | M §5.9 p.42; Table S4 tab:contrasts_v3 p.28 | 3 of 38 percentile intervals exclude zero (3.8 expected by chance); none survives Holm at 5%; at 10% only the spend ratio (percentile, adjusted p 0.076). Statements that E2 removes or explains findings withdrawn. |
| FE-3 | T(40%) under E2 rests on an invalid bootstrap | Fixed | M §5.2 p.39 | Withdrawn. |
| FE-4 | Capital-intensity gap mostly the capex deduction; not a test of Prop. 5 | Fixed | M §5.6 p.40 | See R2-2. |
| FE-5 | Anchor noise-dominated; transient share not determined | Fixed | M §5.8 p.42; M §7.3 p.53; abstract and intro no longer quote a transient share | Transient share -14% to +40% across bounds and views: not determined. Only Pi_lb > 0 is stated as a conclusion (all four views). |
| FE-6 | E2 switch and pro forma rules disclosed only in the appendix | Partly | M App. B.4 p.75; Table S2 (test-run rule) | Disclosed in the protocol with times; E2 reported under the first test run's rule (Psi GAAP -0.283 against -0.287). Not repeated in the empirics section. |
| FE-7 | 2025 is back near 2016-19; the decline is compositional | Fixed | M §5.2 p.38; Table S5 | Reweighting: composition -7.9 [-17.2, -2.7], within-bin -4.1 [-9.7, +2.8] (GAAP, B direction); 2025 alone -4.5 [-17.7, +8.7]. |
| FE-8 | Inference details: interval type, replication counts, non-convergence | Fixed | M §5.1 p.38; S6 p.25 | 999 replications throughout; interval types stated; exact LP solver, so no iteration cap. |
| FE-9 | Linear slope averages a kinked frontier; state window and quantile dependence | Partly | Table S3 p.27; M §5.1 p.36 | Slopes by chi and window reported. The sentence that the trade-off is concentrated between 10% and 30% growth was not added. |
| FE-10 | Report the growth-spend elasticity regression (pooled 0.39, within-firm 1.09) | Partly | M §3.1 p.11 (log-log slope one under optimization); M §5.4 p.40 (levels regressions) | The log-log estimates themselves are not reported. |
| FE-11 | Smaller code and presentation points | Partly | M §4.4 p.35 (flag matched by fiscal year); M §5.7 p.41 (shortfall intervals) | Fiscal-year adjacency fixed; stochastic-frontier results now have bootstrap intervals. The later-filing source of 64 pro forma gaps is not footnoted. |

### FT. Cross-model theory referee, Fable (fable_referee_theory.md). Detail: notes/theory_fixes_v2.md, Section 3.

| ID | Finding | Action | Where in v2 | Numbers and notes |
|---|---|---|---|---|
| FT-1 | Error: undefined symbol b in lem:prices(a) | Fixed | S1 Lemma S2 p.5 | b -> k_u. |
| FT-2 | Error: model section quotes E1 slopes and calibrates ell to them | Fixed | M §3.7 p.20; S2.3 p.6 | Psi_chi slopes (D-2) and the exact mapping ell = (S_beta/b)^alpha; no estimate hard-coded. |
| FT-3 | Error: rem:owncompute uses psi = 0 for servers but deducts replacement in full | Fixed | M Remark 7 p.72; M §7.2 p.51 | One convention (psi = 1 in the text): markup bar 17% (5-year) and 49% (15-year) at psi = 1, 33% and 74% at psi = 0. |
| FT-4 | Error: the script does not check every inequality claim | Fixed | code/verify_theory.py (28i, 28j, 28q); M §3 opening p.9 |  |
| FT-5 | Gap: prop:dynamic assumes a bounded C^1 HJB solution | Partly | M Proposition 2(b)-(e) p.18-19; abstract | Existence not proved (declined; see R1-5); stated as hypothesis (H); new part (e) for the no-root case. |
| FT-6 | Gap: deterministic clock replaces the Poisson freeze process; proof treats it as derived | Fixed | M Definition 4(b) p.29; Proposition 7(f) p.31 | See R1-1. |
| FT-7 | Gap: the calibration uses a fluid relaxation the proposition does not cover | Fixed | M Proposition 7(e) p.30-31; M §7.3 p.53-54 | Divisible-program version proved; the calibration uses its upper bound, attained by the greedy plan while every wave can be filled (central execution through 2036). |
| FT-8 | Gap: the score budget assumes one exogenous market | Fixed | M Proposition 1 p.15 and its intuition; abstract | 'Within one market and at given retention'; new markets open new budgets. |
| FT-9 | Gap: free entry assumes date-0 entry, rental capital and input growth at G | Fixed | M Proposition 4 p.23; S2.4 p.6 | Scope stated; see R4-F4. |
| FT-10 | Gap: cor:ceiling intuition lists rents as a way to exceed R_max | Fixed | M Corollary 4 p.28 | See R1-3. |
| FT-11 | Overclaim: '7 to 13' rests on alpha, all S&M as growth spend and median-based Delta | Fixed | M §3.6 p.19; M §5.4 p.40 | Withdrawn; the G-proxy bias is listed. |
| FT-12 | Overclaim: 'penalizes capital-intensive growth whatever its return' holds for k > 1 | Fixed | M Remark 3(d) p.32-33; M §1 p.2 | 'For capital intensity above one it penalizes growth whatever its return.' |
| FT-13 | Overclaim: 'a rule of economic profit' drops the growth term | Fixed | abstract; M §1; M §9 | 'Economic profit plus growth at its net value.' |
| FT-14 | Overclaim, novelty: customer capital, market penetration, q-theory of advertising uncited; immediate results as propositions | Fixed | M §3 opening p.9; M §1 p.3; M §2 | Positioning added; frontier, score, saturation and envelope results are lemmas, the AI map and the general objective remarks; contribution list narrowed to five. |
| FT-15 | Overclaim: 'a firm cannot spend the budget twice' | Fixed | M Proposition 1 intuition p.15-16 | 'Within one market and at given retention.' |
| FT-16 | Unclear: two 'intercepts' | Fixed | M §3.1 p.11; abstract | m_0 is the margin intercept; m_0 - kG 'the margin at market growth'. |
| FT-17 | Unclear: prop:score(b) interiority at sigma* = sigma-bar | Fixed | M Lemma 2(b) p.12 |  |
| FT-18 | Unclear: prop:myopic reference | Fixed | M §3.4 p.14-15 |  |
| FT-19 | Unclear: prop:amin(b) wording against a_min as a minimum | Fixed | M Proposition 5(b) p.26 |  |
| FT-20 | Unclear: possible double count of the ITGC retest and c_mnt revalidation | Fixed | S2.5 p.6-7; Remark 6 p.72 | Revalidation in c_mnt, control testing in a_min; the retest is now priced at control testing only: $24,000 per upgrade (10 controls x 16 hours per control test, KPMG 2025 SOX Survey, x $150 an hour), down from $100,000, as in Paper 2 and the engine. The double count (at most $41,000 a year per application under the old value) is removed. |
| FT-21 | Unclear: prop:acquired-score(d), G_i = ln NRR | Fixed | M Proposition 8(d) p.43 | See R1-20. |
| FT-22 | Minor: notation reuse (y, f, p) | Partly | S1 Table S1 | y and f renamed; price p and process index p kept (each local; listed). |
| FT-23 | Minor: needless X >= k in prop:attainable(d) | Fixed | M Proposition 6(d) p.30 |  |
| FT-24 | Minor: G > -1 belongs in prop:budget(b) | Fixed | M Proposition 1(b) p.15 |  |
| FT-25 | Minor: 'falls' should be 'nonincreasing' in prop:amin | Fixed | M Proposition 5(d) p.27 |  |

### Revision plan. Revision-plan items (notes/reviews/paper1_v1/revision_plan.md).

| Item | Plan item | Action | Where in v2 | Numbers and notes |
|---|---|---|---|---|
| A1 | Withdraw '7 to 13'; report bounds by method (D-1) | Fixed | M §5.4 p.40 | alpha(X - k) 0.05 to 10.1; spend ratio 3.0 to 3.5. |
| A2 | Withdraw 'acquired growth flattens the slope' and the size-gradient and cash-steepening attributions (D-3) | Fixed | M §5.9 p.42 |  |
| A3 | Withdraw T(40%) under E2 | Fixed | M §5.2 p.39 |  |
| A4 | Capital-intensity gap as an accounting effect | Fixed | M §5.6 p.40 |  |
| A5 | Anchor intervals; transient share not determined | Fixed | M §5.8 p.42 |  |
| A6 | Size gradient: interval, not 'disappears' | Fixed | M §5.5 p.40 |  |
| A7 | Drop 'never with a full point'; test period differences | Fixed | M §5.3 p.39 |  |
| A8 | Keep the P95 decline; explain as composition; yearly series and decomposition | Fixed | M §5.2 p.38; Table S5 | 11.9 (GAAP) and 12.7 (cash) points; 8 to 13 across 22 variants; Holm-adjusted p 0.054-0.208 (survives at 10%, not 5%). |
| A9 | Drop the horizon upper ends 156 and 123; central path plus tornado | Fixed | M §7.3 p.52-56 | Central path 56/60/66 (55 in 2036 if no S&M buys growth). |
| A10 | Add the conditions: k > 1; growth at the net weight; within one market; conditional on the cost structure | Fixed | M §1; abstract; M Remark 3; Proposition 1; Corollary 4 |  |
| B1 | panel_v3 sample rules | Partly | M §4.2 p.33-34 | R1, R3, R4 applied; R5 a flag and sensitivity; R2 a sensitivity on the 16 named firms only (needs every registrant's business description); foreign filers not tested for listing (their cover pages report shares outstanding, not float). |
| B2 | Estimand policy: E1 baseline; claims under E1, E2 and both bounds; disclose the switch and post-test-run rules | Fixed | M §4.5 p.35-36; M App. B.4 p.75; Table S2 |  |
| B3 | Frontier object: Psi_chi primary; local quantile descriptive; ell to the object that maps to Psi_chi (D-2) | Fixed | M §5.1, §5.3, §3.7 |  |
| B4 | Inference: exact LP, grid of tau and windows, B >= 999 with seeds, interval types, Holm, NaN shares | Fixed | M §5.1; S6 |  |
| B5 | Score definitions and bridge, including after interest | Fixed | M §4.3, §4.6; Table S6 | Bridge before interest and cash taxes uses latest-filed SEC frames values. |
| B6 | Stochastic frontier: common frontier, JLMS, bootstrap, balanced panel, caveat | Fixed | M §5.7 p.41 |  |
| B7 | Within-firm regression on g_{t+1} under E1 and E2 | Fixed | M §5.3 p.39-40 |  |
| C1 | prop:expected: clock as an assumption; fluid version | Fixed | M Definition 4, Proposition 7 |  |
| C2 | Partial realization: assumption or correction | Fixed | M Definition 4(b) |  |
| C3 | cor:ceiling conditional on its cost structure | Fixed | M Corollary 4 |  |
| C4 | prop:dynamic: verification hypothesis in the proposition and the abstract, or prove existence | Partly | M Proposition 2; abstract | Hypothesis (H) stated; existence not proved. |
| C5 | Accountability floor as a pass/fail ICFR constraint | Fixed | M Proposition 5; Remark 6 |  |
| C6 | Common mode: ITGC quality; Kim et al. reading; AI-review error rates | Fixed | M Assumption 7, Lemma 6(c); S2.6 |  |
| C7 | Free entry: costly customer acquisition; 92.5 example; assumptions | Fixed | M Proposition 4; S2.4 |  |
| C8 | Errors and notation (FT-1, FT-3, FT-4, FT-16 to FT-25) | Partly | see FT rows | Some renames declined (FT-22, R1-23). |
| C9 | Novelty: positioning, demotions, narrowed contribution list | Partly | M §3 opening; M §1; M §2 | Baumol-Panzar-Willig and Sutton not cited (not verified). |
| D1 | Compute share 0.20 flat -> 0.06 at 2025 prices with horizon path | Fixed | M §7.2 p.50-52 | G* 42.3% -> 31.0% (30.4% before FI-5); 36.0/32.6/30.1% by horizon. |
| D2 | Execution pace re-grounded; revealed-pace reference; go/no-go threshold | Partly | M §7.3 p.53-54 | Shares by 2036: 23% -> 41% realized (61% embedded); crossing 9 -> 4 years; revealed pace 8.2 points reported. No go/no-go threshold. |
| D3 | Pass-through scenarios {0, 0.5, 0.7} | Fixed | M §7.2 p.52; M §7.3 p.54-55 |  |
| D4 | Capability and inference-price paths as explicit inputs | Partly | M §7.2 p.52 | Price path explicit (compute share by horizon); capability path not modeled. |
| D5 | Central case plus tornado; firm-specific G; Rule of 1000 to an appendix | Partly | M §7.3; S5 | Firm-specific G not used. |
| D6 | Reliability and ICFR parameters | Partly | Remark 6 p.72; Table S7 | r-bar 0.98, q_M 0.995 adopted; ITGC line per application $266,967 -> $204,672 a year (0.027% -> 0.020% of revenue at $1 billion) with the retest at KPMG test effort; still above the $80,000 reference of Table S7. The floor reaches 0.5% at 15 in-scope AI applications (11 before), or 8 with close fallbacks (7 before). Remote threshold: central 5% with 1% as a sensitivity (lead decision; see RA-1). |
| D7 | Bending Spoons: drop the double charge; return on acquisition capital; organic score after interest; reword | Fixed | M §6 |  |
| D8 | a_min upper end: 4.6% (broad sample) -> core-panel value | Declined | M §7.2 p.49-50 | Kept at 4.6% because the band is a cross-paper parameter of the params commit; the core-sample value (5.8%) is disclosed. Changing it needs a params decision for Papers 1 to 3 (it would raise the conservative threshold). |
| E1 | Decision-rules section (prop:levers-position) at the end of horizons | Fixed | M §7.5 p.57-58; Table 7 p.58 | Placed and rewritten around the ratio test. Table 7 and its macros are regenerated on panel_v3 (cell definitions unchanged). At the revealed weight automating the growth engine still outranks cutting G&A at all six positions, and every switch weight (5.7 to 9.1) is above screening weights of 2 to 3 (CLAIMS lpGEFirstAll and lpScreenBelowAll pass). The text now says that the table ranks G&A only, not R&D. The archetype playbook regenerated on panel_v3 (notes/playbook_results.json), which adds R&D as a lever, ranks R&D first for the near-frontier elite (A6) under public ownership, so there the growth engine leads at five of the six positions. |
| E2 | 'Use in filings' paragraph (Reg G, Item 10(e), C&DIs, Release 33-10751, safe harbor) | Not done | - | See RA-3. |
| E3 | Regulatory facts (SR 26-2, OCC 2026-13; Reg. (EU) 2026/1744) | Fixed | S2.5 p.6; Table S7 |  |
| E4 | Citations corrected; parameter-source table; missing literature | Fixed | Table S7; M §2 |  |
| E5 | Protocol appendix: AI panels, models, timeline, estimand switch, E.5 reclassified, licences | Fixed | M App. B p.74-77; S7 p.36-40 |  |
| E6 | Length: about 75 pages | Fixed | main paper 77 pages; Supplementary Appendix 44 pages | Proofs, supporting results, the Rule of 1000, data and robustness tables, parameter sources and protocol records moved to the supplement. |
| E7 | Replication: estimate_organic.py in the README and run order; regenerate_all.sh rebuilds all papers | Fixed | code/REPLICATION_README.md; code/regenerate_all.sh; code/build_paper1.sh |  |

## Checks behind this document

- Every number in the v2 paper comes from generated macros (`code/paper1_macros.py` writes `paper1/macros.tex`). The CLAIMS check, run by the same script, tests each verbal claim of the text against those numbers. Numbers in this document are copied from the same build; the summary section reads them from `paper1/macros.tex` directly.
- Theory checks: `code/verify_theory.py` (189 checks), with the no-review error rates (FI-5) in its full-cost block. When this document was written, check 27d still used the old control retest ($100,000) and the 1% floor; with those two values updated to the ones above, all 189 checks pass.
- Build: `code/build_paper1.sh` builds the main paper and the supplement. It checks for undefined references, undefined citations and multiply defined labels, and the build is clean.
- Page references are to the v2 build named above. Where a page range is given, the item starts on its first page.
