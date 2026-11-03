# Round-2 practitioner panel: investors and bankers, Paper 1 (v2)

Paper: "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation" (v2, October 2026; `paper1_v2.pdf`, `.txt`, `supplement_v2.pdf`, `.txt`, `response_to_reviewers.md`).
Round-1 baseline: `notes/reviews/paper1_v1/panel_investors_bankers.md` (seven roles). Round 2 adds two roles: stewardship lead and pension/endowment CIO.
Evidence gathered 29 October 2026; report written 2 November 2026. The panel did not read any other round-2 report and did not edit any repository file.

Conventions
- `txt:NNN` is a line of `paper1_v2.txt`; `supp:NNN` is a line of `supplement_v2.txt`; section and table numbers are the paper's.
- "Panel computation" means a read-only calculation on `data/panel_v3.csv` (1,788 firm-years, 292 firms) or on filing figures, run in this session. It is not in the paper. Scripts: scratchpad `r2_calc1.py`, `r2_calc3.py`, `r2_size.py`, `r2_bridge.py`, `r2_v0.py`, `r2_pltr.py`.
- Independence caveat (as in round 1 and Appendix B): all nine roles are played by one agent. Agreement among them is weaker evidence than a human practitioner panel.

---

## 1. Verdict

**Better and safer to quote; still not a pricing tool; and the owner-type claims practitioners most want are not in this paper.**

What changed since round 1 (verified in the paper, not only in the response):
- The unsupported decision weight of 7 to 13 is gone. The abstract, §1, §5.4 and §8.1 now say the data do not identify it (txt:22-23, 102-104, 1966-1971, 2900-2901).
- The Bending Spoons arithmetic is repaired: US GAAP operating cash flow is treated as after interest, capex is shown to be negligible, charges are against a margin before interest, the organic score is shown after interest, the NRR sentence is correct, and the fully charged figures are out of the abstract and introduction (txt:2175-2215, 2245-2312, Table 3).
- The 0.54 success rate is relabelled as pilot attrition (supp: Table S7).
- Four bases are shown side by side for 2023-25 (txt:1736-1743).

What still stops it changing how anyone screens or values:
1. No route from a score to a multiple. The reason given for declining the bridge (no price data) does not apply to the analytical bridge or to published bucket data (N2).
2. The "price line" in the title reads as a valuation line; the "iso-score, not iso-value" caveat sits in one clause and a remark (N1).
3. The decision weight is still shown at one discount rate, with a one-sided sentence on the direction of the error (N3), and the withdrawn weight re-enters through four conditional statements that a board or sponsor can quote (N4).
4. The abstract's headline decline in the top of the distribution has no basis named, and on the basis practitioners quote the decline is smaller (N5).
5. The Bending Spoons case stops at the 13 August results while the references list 6-Ks through 29 October as "exhibits used" (N6).

Counts
- Round-1 items checked: 30. Resolved 8, partly resolved 8, not resolved 14 (Section 3).
- New findings: 25. High 7, Medium 13, Low 5 (Section 4).
- Response-to-reviewers status claims for IB-1 to IB-8: the panel agrees with seven. It disagrees with the reason given for IB-2 (declined), not with the status (Section 3).

### Role verdicts

**1. Long-only growth PM.** Would use: the basis ladder (§4.6), the durable versus transient split of a top score (§7.3, Table 5), and the organic estimand. The withdrawal of 7-13 removes my main objection. Does not change my process: nothing maps a score to EV/revenue, so I cannot compare the paper's weights with the regression I already run (Bessemer's FV/NTM regression, Meritech's 3.8). My 2026 problem is the de-rating, which the paper never mentions. Misuse risk I see: "accept a lower Rule-of-40 score" in the conclusion (N4), and "41% by 2036" (N8). Asks: a bridge box (N2), named anchor firms (N14).

**2. Short-seller.** v2 is harder to lift than v1. The fully charged number is labelled a lower bound in the row and the text, the interest double count is gone, the NRR sentence is accurate. I would still use Table 3: uncharged 125.2 against charged 87 to 114, and the Q2 gap between a reported 160.5 and an organic 22 to 44. The paper is stale where it matters to me: since the Q2 results the company has raised a SACE-backed term loan, term loan B add-ons, and $1.25B 9.625% plus EUR 500M 8.625% notes "to fund future acquisitions" (N6). That is continued reliance on acquisition capital, the paper's "access to targets and capital" point, in the company's own press release, and the paper has not seen it (it does not by itself show a shrinking base). The paper also protects the target: at X of 2.5, 5 and 9 acquired growth raises the charged score (txt:2299-2303), so no honest short can cite it to say the deals destroy value.

**3. Sell-side software analyst.** The four-basis table helps, but it hides what I need: the same 2023-25 sample passes at 9.7% on GAAP and 29.0% on FCF before SBC, and among $1-5B firms 51.5% pass before SBC against 9.7% after (panel computation, N13). I cannot place the paper's frontier against SEG's weighted-score buckets (12.7x, 7.9x, 5.2x, 3.4x, 1.6x) because no mapping is offered (N2). The universe is still SIC 7372 "the industry to which the Rule of 40 is usually applied" (txt:1626), not the SaaS indices I publish against (N14). The best practitioner-observable number is buried in Table S7: the CAC-ratio baseline gives a growth weight of 2.9 to 5.2 (N10).

**4. PE operating partner.** The paper has nothing on private-equity ownership beyond one sentence that "a sponsor's faster decisions change nothing in these cases" (txt:2734-2736), and I would not let that sentence stand: sponsors change capacity by replacing people and by taking dips that are sized to covenant headroom, not to a guided one point of revenue (N7). The central pace of 10% of employees a year is a public-company number. The paper's own example gives a decision weight of about 2 at a 22% hurdle (panel computation, N3), so a sponsor would not act on the withdrawn 7-13; good that it is gone. Levers by position (§7.5) give the right direction (growth engine for fast growers, overhead for mature ones). The after-interest score of a levered buyout (about 23 points of revenue at 7x and 9.5%, round-1 B7) is not in the paper (N20).

**5. Growth-stage VC.** The score budget (Proposition 1, Corollary 1) is the useful formal statement of how long hypergrowth can last. The sample starts at $100M of prior revenue and is public only; §8.6 says the sample "likely understates the current frontier at high growth" but gives no number (R28). At a 31% hurdle the paper's example gives a decision weight of 1.35 (panel computation), so founders and late-stage investors act on different weights; the paper's two-weight framework could name that tension. The CAC-ratio and payback figures in Table S7 are what I would actually check (N10). Misuse risk: founders citing the conclusion's "accept a lower score" to defend burn (N4).

**6. Credit analyst / leveraged-finance banker.** The score is not a credit metric. The paper now gets the one thing I needed right: under US GAAP interest paid is inside operating cash flow, so an annuity at a cost of capital on top double counts (txt:2175-2181, 2276-2277). Missing: the post-Q2 capital structure (N6), the point that an after-interest score measures capital structure (N20), coverage and FCF/debt beside the score, and the fact that the company's 2.4x leverage uses adjusted EBITDA (round-1 V11; not in the paper). The paper's charge rate of 9.34% is below the issuer's own USD secured coupon of 9.625% (N21).

**7. M&A banker (software take-privates).** Section 6 gives me usable language: organic growth from ASC 805 pro forma (E2), net weight X - k^acq, bang-bang acquisition, "charge interest or a cost of capital, not both". The round-1 complaint that X = 1 was used as a decision rule is largely fixed: the sign is now evaluated at X of 2.5, 5 and 9 against prices of 1.7 to 3.2 times revenue (txt:2299-2303). Still one case, selected because it listed (txt:2397); no long-record second acquirer; no EBITDA basis; no treatment of contingent consideration. A fairness opinion could borrow the 87-114 bracket without its conventions; add a convention box. A board book could cite "price line" as valuation (N1). A new primary data point is available: Miro at an enterprise value of $1.355B on about $600M of ARR, 2.3x (N16).

**8. Stewardship lead (new role).** Would use: the after-SBC basis (it treats SBC as the cost it is); the organic-growth definition and the price of acquired growth as engagement questions for serial acquirers; the warning that a Rule-of-40 target in a pay plan is basis-dependent (txt:1736-1743). Worry: the conclusion tells management that a firm "should accept a lower Rule-of-40 score while its growth spending earns more than it costs" (txt:3063-3065). That sentence will be quoted in proxy season to lower pay-plan thresholds. It is conditional on an unproved hypothesis (H) and on a test the paper does not supply (N4). Governance of the paper itself: the AI-agent protocol is disclosed (Appendix B), which I credit; competing interests are recorded as "No statement" (txt:3793; N19); the licence makes commercial use subject to written permission, which is unclear for an asset manager's internal use (N19); the accountability-floor results (§8.5, Proposition 5) read as a good question set for audit committees (diversity of control design, IT general controls), but the numbers are illustrative scenarios and should not be taken as a standard.

**9. Pension / endowment CIO (new role).** I would use the paper in manager due diligence, not in allocation: ask any manager or GP who quotes a Rule-of-40 number to state the basis (GAAP, adjusted, FCF before or after SBC), whether growth is organic, and whether interest is deducted. The paper gives that checklist. It does not test whether any score predicts multiples or returns (it cites Lee, 2024, who does), and the 2028/2031/2036 path is a firm-level scenario for an "exceptional" asset-light firm, not an asset-class view (N15, N18). Software de-rating and AI disruption of seat-based revenue are the portfolio risks I care about; the paper models a pass-through variant but no seat-compression case (R24).

### Investor use: direct answers to the brief

**Does the paper change how an investor reads a Rule-of-40 score?** Yes, at the level of measurement; not yet at the level of value. Four changes: (i) quote the basis, because the same firm-year can pass at 9.7% or 29% (§4.6); (ii) separate organic from acquired growth and charge acquired growth at what it cost (Proposition 8); (iii) treat a very high score as partly transient, because it draws on a finite budget of share headroom (Proposition 1, §7.3); (iv) show a levered firm's score after interest, never beside unlevered peers without saying so (Definition 5, with the missing caveat in N20).

**Is the "price line" reading clear and correct?** Correct: a Rule-of-X line has slope -X (the margin points traded for one point of growth), and tangency with a concave frontier gives the maximal score (§3.3). Not clear: to an investor "price" means market price, and two firms on the same Rule-of-40 line have different values. Remark 3(c) shows this (only one line in the family is an iso-value line) but the abstract and introduction do not (N1). Panel computation of the Lemma 5 value, at r = 9.34%, T = 10, G_inf = 3% and a persistent margin: (g, m) = (30, 10) gives 12.1 times revenue; (20, 20) gives 11.7; (10, 30) gives 8.3; (0, 40) gives 5.2. All four score exactly 40. At r = 12% the same four are 7.6, 7.5, 5.6 and 3.7.

**Are the acquired-growth claims sound from a deal perspective?** Mostly yes: the net weight X - k^acq, the bang-bang result, the treadmill and the E2 pro forma method match deal practice. Qualifiers the paper should carry: ARR is not GAAP revenue; enterprise value should be net of acquired cash; the constant-price supply assumption of Proposition 8(b) fails in practice as volume rises (the text concedes this at txt:2172-2174); one case. The paper does not give the buyer's own X, which is why a reader cannot tell whether the acquisitions "pay" (the paper's own machinery says they do at X of 2.5 and above).

**Are the PE and permanent-capital owner claims, and the levers by owner type, sound?** There are almost none to test. Owner type enters only through Remark S8 (no numbers; the companion paper "derives" them), the Ownership paragraph (public versus an unspecified "sponsor", txt:2728-2741) and the weight X in §7.5. The one concrete statement, that a sponsor's faster decisions change nothing, is likely to be misread (N7).

---

## 2. Reading guide to the status in Section 3

Status words: Resolved (the paper itself does what round 1 asked); Partly resolved (some of it, with a stated gap); Not resolved. "Response" is the status the authors claim in `response_to_reviewers.md`.

---

## 3. Round-1 points: status in the paper

| # | Round-1 point (item) | Response | Panel | Where in v2 | What remains |
|---|---|---|---|---|---|
| R1 | Screening weight is a range, not 2 to 3: Bessemer's regression implies about 2 to 9, Meritech 3.8, Lemma 1 spans 0.7 to 6.2 (IB-1, D1) | Partly | **Partly resolved** | Lemma 5 and discussion (txt:966-979: "a weight of 2 to 3 reflects a choice of persistence, not a prediction"); S2.2 numbers 1.8, 2.8, 5.4, 6.2 (supp:281-304); Table S7 "2 to 9" (supp:1848-1855) | Definition 1 still says "Bessemer's Rule of X uses weights X of about 2 to 3" (txt:491); §8.1 says "close to the weights of two to three that Deeter and Bondy recommend" (txt:2894-2896); the 2-9 range and Meritech's 3.8 appear only in the supplement or nowhere (N9) |
| R2 | Abstract: replace "not the screening weights of two to three" (D1) | Partly | **Resolved** | Abstract txt:18-19: "exceeds the screening weights of two to three when its revenue multiple does" | none |
| R3 | Show the decision weight by owner's discount rate (panel B3) (IB-1) | Partly | **Not resolved** | S2.2 uses r = 0.10 only (supp:281-290); §8.1 says a constant rate "if anything, understates" the weight (txt:2902-2903) | Panel B3 recomputed: 14.6, 10.0, 5.8, 3.7, 2.1, 1.35 at r of 9.34, 10, 12, 15, 22, 31% (N3) |
| R4 | The decision weight of 7 to 13 is not identified; withdraw it (D2) | Withdrawn (A1; cited under IB-2) | **Resolved** | §5.4 txt:1949-1971 ("we withdraw the first version's statement that it lies between 7 and 13"); abstract txt:22-23; §1 txt:102-104; §8.1 txt:2900-2901; Proposition 2 labelled conditional on (H), txt:891-898 | Four conditional re-entries remain (N4) |
| R5 | Test the 7-13 against published multiples (SEG, Meritech) (IB-2, D2) | Declined | **Not resolved** | Supp protocol record: "moot once the weight was withdrawn; noted as future work" (supp:2219-2225) | Moot for 7-13, but the same published multiples are the missing level anchor for the surviving statement "decision weight exceeds screening weight when the revenue multiple does" (N10) |
| R6 | Score-to-multiple bridge (analytical, Lemma 5 values on iso-score points) (IB-2, D3) | Declined | **Not resolved** | None. The decline is not mentioned in the main text or §8.6; the supplement log mentions only the market test | The reason given (no price data) does not apply (N2) |
| R7 | Screening recipe (six steps) (D3) | Declined | **Not resolved** | None; §9 gives three of the six steps in prose (basis, charge acquired growth, show interest) | A one-box recipe would cost half a page (N2) |
| R8 | State that "the Rule of 40 line is not an iso-value line" (D3) | not listed | **Partly resolved** | §3.3 txt:538-540 ("iso-score lines, not iso-value lines (Remark 3(c))"); Remark 3(c) txt:1573-1578; conclusion txt:3030-3031 ("a price at which growth is traded for margin") | Absent from the title framing, abstract and introduction; no numbers (N1) |
| R9 | Report scores on FCF before SBC by period (IB-3, D4) | Partly | **Partly resolved** | §4.6 txt:1736-1743 (2023-25 medians 12.0, 26.4, 29.2, 15.3; pass rates 9.7, 24.8, 29.0, 9.2; median SBC 12.3% of revenue); pass rates for the whole sample 14.3, 26.6, 30.5, 15.9% | No by-period series, no P95 change on FCF before SBC, no SBC trend (panel computation: P95 fell 8.6 on FCF before SBC against 12.7 after; median SBC rose from 6.8% to 12.3%) (N5, N13) |
| R10 | Qualify the abstract's "fell 12 to 15 points" with the basis (D4) | not listed | **Not resolved** | Abstract txt:19-22: "the 95th percentile of the score fell by 11.9 to 12.7 points" with no basis | Both ends are bases that deduct SBC (N5) |
| R11 | Sample: game publishers, casino gaming, CoreWeave, Xunlei (IB-5, D5) | Partly | **Partly resolved** | Rule R2 (txt:1655-1665) applied as a classifier to 16 named firms, 4 classed non-software; Table S2 rows "without all 16" and "without the named firms" (supp:1492-1495) | Take-Two, Roblox, Unity, THQ, CoreWeave stay in the main sample; txt:1626 still says SIC 7372 is "the industry to which the Rule of 40 is usually applied"; no SaaS-index row. Panel computation: dropping 13 registrants (games, casino, CoreWeave, Xunlei, Mobileye) leaves the P95 decline at -11.5 (GAAP), -11.7 (after SBC) and -7.4 (FCF before SBC), so the headline survives (N14) |
| R12 | Exzeo (captive revenue) must not anchor the top tail (D5) | IB-5: Exzeo 2025 excluded (R3) | **Resolved** | Rule R3 excludes Exzeo 2025 on filing text (txt:1655-1658); the 2025 anchor is 13 firm-years of 7 firms without acquisition-affected years (txt:2586-2588) | none on Exzeo |
| R13 | Name the anchor firms; ticker list; NTM basis (C3) | not listed | **Not resolved** | The anchor firms are not named in the paper or supplement; "Data and code are available from the author" (txt:39) | Panel reconstruction of the 13 firm-years: Palantir (2025), Clear Secure (2023-25), Duolingo (2023-25), monday.com (2023-24), Global-E (2024-25), Cellebrite (2024), CrowdStrike (2023) (N14) |
| R14 | Bending Spoons conventions: US GAAP, OCF after interest, capex negligible, unlevered margin, decay-consistent and time-weighted charges, show the grid (IB-4, D6) | Fixed | **Resolved** | Remark 4 txt:2175-2215; worked numbers txt:2245-2312; Table 3 txt:2339-2393 (87 to 114 on margin before interest; 79 to 103 on levered OCF and "charge the debt-financed share twice"); capex 0.05% and 0.2% of investing outflow (txt:2260-2263) | Staleness (N6), not arithmetic |
| R15 | Report return on acquisition capital (D6) | Fixed | **Resolved** | txt:2282-2287: 22 to 28% before and 14 to 22% after economic depreciation, against 8.93% | Text and Table 3 differ in the range (N23) |
| R16 | Sensitivity at r of 11-12% (D6) | Partly | **Partly resolved** | txt:2280-2281: "Each point added to r lowers a user-cost score by 1.2 to 2.1 points" | No r row; issuer's marginal coupon is now public (N21) |
| R17 | NRR sentence; organic score after interest; fully charged figures out of abstract and introduction (IB-6, D7) | Partly | **Resolved** | NRR txt:2304-2312 (5 and 9% a year before new customers, subscription only, +3% organic offsets); organic after interest 21.6, range 22 to 44 (txt:2227-2235); abstract and intro give 87 to 114 (txt:149-152); fully charged -25.0 and -16.5 only in §6 and Table 3, labelled "lower bound" in the row | Organic range omits two items (N22) |
| R18 | Second serial acquirer (Constellation) and the company's own IRR hurdle (IB-6, D7) | Partly | **Not resolved** | None. Constellation and IRR hurdle do not appear in the paper | One case "selected because it reached a listing" (txt:2397) |
| R19 | Separate the measurement lens from the decision rule; leveraged-buyout illustration (IB-7, D8) | Partly | **Partly resolved** | Sign of acquired growth evaluated at X of 2.5, 5, 9 against k^acq of 1.7 to 3.2 (txt:2299-2303); "charge interest or a cost of capital, not both" (txt:2179); Proposition 8(c) | No levered-buyout caveat on the score after interest (N20) |
| R20 | 0.54 success rate measures pilot attrition (IB-5, D9) | Partly | **Resolved** | Table S7: "slow case ... Pilot attrition, not failure of a funded migration; ... the S&P report was not read" (supp:1719-1725); main text txt:2736-2738 uses 0.54 only for slow execution | none |
| R21 | Re-ground central and fast success rates (IB-5, D9) | Partly | **Partly resolved** | 0.70 and 0.80 from Forth et al. (2020), class b (supp:1726-1732); txt:2618-2626 | Definition mismatch and a headline that moved from 23% to 41% without a bridge (N8) |
| R22 | Relabel central execution as a public-company case; add an owner-led row; state the buyout-weight result in Remark 2 (D9) | EX-4 Partly | **Not resolved** | "exceptional firm" retained (txt:26-27, 2576, 3053); ownership paragraph txt:2728-2741 | N7, N15 |
| R23 | Pass-through variant (IB-8, D10) | Partly | **Resolved** | txt:2549-2556 (phi 0.5 and 0.7: thresholds 36.3% and 38.5%); txt:2717-2719; Table 6 | none |
| R24 | Seat-compression scenario (IB-8, D10) | Partly | **Not resolved** | Only lever 4 mentions customers' seat counts (txt:2756-2757) | No scenario on G or revenue per seat |
| R25 | "How not to use these results" box (IB-8, D10) | Partly | **Not resolved** | None; limitations §8.6 are technical (txt:3012-3026) | N17 |
| R26 | State that the ceiling is not a cap on valuation; address the 2026 de-rating (D10) | not listed | **Partly resolved** | §8.3 txt:2950-2952: "The ceiling itself is a bound at a stated cost structure, not on observed scores" | Nothing on valuation or the 2026 de-rating (N17) |
| R27 | Credit overlays: coverage and FCF/debt beside the score; note that the company's leverage ratio uses adjusted EBITDA (C6) | not listed | **Not resolved** | None | N20 |
| R28 | Private-company frontier in numbers; burn multiple mapping (C5) | not listed | **Not resolved** | §8.6 txt:3013-3015 says the sample likely understates the frontier at high growth | No numbers |
| R29 | Value-creation bridge and covenant-linked dip budget for sponsors (C4) | not listed | **Not resolved** | "guided dip" of 1 or 2 points (txt:2728-2735) | N7 |
| R30 | NTM-basis growth; SBC as dilution (C1) | not listed | **Not resolved** | Lemma 5 notes it ignores "dilution from stock-based compensation" (txt:978-979) | A one-sentence scope note would do |

Totals: **Resolved 8** (R2, R4, R12, R14, R15, R17, R20, R23); **Partly resolved 8** (R1, R8, R9, R11, R16, R19, R21, R26); **Not resolved 14** (R3, R5, R6, R7, R10, R13, R18, R22, R24, R25, R27, R28, R29, R30).

Response status claims for IB-1 to IB-8 against the panel's reading
- IB-1 Partly: agree (R1, R3).
- IB-2 Declined: agree it was declined; disagree that "no price data" is adequate (N2).
- IB-3 Partly: agree; add the abstract basis (R9, R10).
- IB-4 Fixed: agree on the arithmetic; the case is stale after Q2 (N6) and has no r row (R16).
- IB-5 Partly: agree (R11, R21).
- IB-6 Partly: agree (R17 resolved; R18 not).
- IB-7 Partly: agree (R19).
- IB-8 Partly: agree (R23 resolved; R24, R25 not; R26 partly).

---

## 4. New findings (round 2)

Severity: High = a reader acting on the text could be materially misled, or a core round-1 point stays open with consequences. Medium = clarity or overclaim that a practitioner would quote or misread. Low = polish or a small inconsistency.

### High

**N1. "Price line" reads as a valuation line.**
- Severity: High.
- Location: title; abstract txt:13-15; §1 txt:61-62; §3.3 txt:538-540; Remark 3(c) txt:1573-1578; conclusion txt:3030-3031.
- Issue: to an investor a price line is a line of equal market price. The paper's price is the relative price of growth in margin points. Only one line in a family of parallel Rule-of-X lines is an iso-value line (Remark 3(c)). The caveat is one clause in §3.3 and an identity in a remark, in the (g, e) plane. A board book or an activist letter can quote the title to argue that a target below the line is mispriced. Panel computation (Lemma 5 value, r = 9.34%, T = 10, G_inf = 3%, persistent margin): (30, 10), (20, 20), (10, 30) and (0, 40) all score 40 and are worth 12.1, 11.7, 8.3 and 5.2 times revenue.
- Suggested change: in the abstract and at the first use in §1: "Rule-of-40 and Rule-of-X lines are price lines in the sense that their slope is the number of margin points traded for one point of growth. They are lines of equal score, not of equal value: firms on the same line can be worth very different multiples of revenue." Add the four-point table from N2 in §3.3 or §8.1.

**N2. The score-to-multiple bridge is declined for a reason that does not apply, and the main text does not say it is missing.**
- Severity: High.
- Location: `response_to_reviewers.md` IB-2; supp:2219-2225; absent from §8.6 (txt:3012-3026).
- Issue: the response says a bridge "needs price data, which the panel does not hold". (a) The analytical bridge needs none: it is the paper's own Lemma 5 (txt:932-937), V = S0[m N_T(eta) + m_LR eta^T M_inf], evaluated on points of an iso-score line (numbers in N1). (b) The empirical anchor is published and citeable: SEG's 3Q25 report gives median EV/TTM revenue of 12.7x, 7.9x, 5.2x, 3.4x and 1.6x for weighted Rule-of-40 buckets above 40, 30-40, 20-30, 10-20 and below 10 (weighted score = 1.33 x growth + 0.67 x EBITDA margin); Bessemer reports a regression R-squared of 62% for Rule of X and 50% for Rule of 40 on FV/NTM revenue. (c) The supplement log (supp:2219-2225) records only the market test of 7-13 as "future work", not the bridge, and the main text does not tell the reader that no mapping from score to multiple is offered. A reader will either assume the paper has one or supply their own.
- Suggested change: add a half-page box to §8.1: (i) the four-point table from N1 at two discount rates; (ii) the SEG buckets as practitioner data, with the SEG weights stated; (iii) a six-step recipe (annual and NTM score on FCF before and after SBC; organic growth; screen at X of 2 to 3; flag acquisition years, related-party revenue, deferred-revenue-driven FCF and SBC above 15% of revenue; split durable from transient for flagged high scorers; show the score after interest only beside unlevered peers). If the authors still decline, add to §8.6: "The paper does not map scores to multiples; no statement here is a valuation statement."

**N3. The decision weight is shown at one discount rate, and the sentence on the direction of the error is one-sided.**
- Severity: High.
- Location: S2.2 supp:281-290 (r = 0.10); Proposition 2 worked example txt:910-914; §8.1 txt:2898 ("the worked example gives 5 to 15") and txt:2902-2903.
- Issue: §8.1 says "a constant discount rate, if anything, understates the decision weight" because long-duration cash flows earn lower expected returns. That is true for the market's rate and says nothing about an owner's hurdle. Panel computation on the paper's own example (m0 = 0.35, G = 0.04, alpha = 0.3, k = 0; demand pull calibrated so v0 = 10 at r = 10%): v0 is 14.6 at 9.34% (Damodaran software WACC), 10.0 at 10%, 5.8 at 12%, 3.7 at 15%, 2.1 at 22% (a typical buyout target return) and 1.35 at 31% (a typical venture target). An owner who discounts at a buyout hurdle acts on a weight inside the screening range. Caveats: infinite horizon, constant rate, same growth technology for every owner; a finite-hold owner who values revenue at an exit multiple would differ and was not computed. The statement "5 to 15" is a statement about an owner who discounts at about 10% and whose firm has a small-share revenue multiple of 10 to 15 (weights of 5.4 to 9.1 across share at a multiple of 10).
- Suggested change: add one table to S2.2 and one sentence to §8.1: "At the paper's own parameters the weight is 14.6 at a 9.34% cost of capital and 2.1 at 22%; whether it exceeds the screening weight is as much a statement about the owner's discount rate as about the firm's revenue multiple." Delete or qualify "if anything, understates" so it is not read as a one-way bias for all owners.

**N4. The withdrawn weight re-enters through four conditional statements that can be quoted as cover for burn.**
- Severity: High.
- Location: (a) §8.1 txt:2905-2915; (b) §7.5 and Table 7 txt:2863-2865, 2877-2879; (c) conclusion txt:3063-3065; (d) §8.1 txt:2898.
- Issue: (a) "If its spend ratio equals the median of 3.02 and it is optimal, an asset-light firm growing 10 points faster than its market scores about 20 points below the score it would earn with no growth spend, even though the spending creates value at its own weight." Both conditions are exactly what §5.4 says the data cannot supply (alpha(X - k) from 0.05 to 10.1). The next sentence says a fixed threshold "marks down firms whose growth spending earns more than it costs". (b) Txt:924-925 says "Where an example below needs a weight, we evaluate it at X in {2.5, 5, 9}", but Table 7 uses the proxy alpha(X-hat - k) = 3.3, X-hat - k = 11 (txt:2863-2865), and reports switch weights of 5.7 to 9.1 "above the screening weights, so ranked at a screening weight overhead comes first everywhere" (txt:2877-2879). The paper does say it is "one calibration, not an estimate" (txt:2864-2865) and that over the full range the switch weight can lie on either side of the screening weights (txt:2879-2880); but the table body and the headline sentence use the 11, which is the withdrawn 7-13 by another route. (c) "A firm that values a dollar of revenue at its marginal value should accept a lower Rule-of-40 score while its growth spending earns more than it costs." Conditional on (H), which the paper says (txt:897-898) every such statement is. (d) The worked example's 5 to 15. A founder, a sponsor in an ARR-loan negotiation, or a board will cite (a) or (c) and omit the condition; the paper supplies no test of "earns more than it costs".
- Suggested change: (a) restate as arithmetic, not a finding: "For any firm that spends sigma* = alpha(X - k) Delta* the score exceeds the saturated score by Delta*(1 - k - alpha(X - k)); the sign depends on a product the data do not identify." Drop "about 20 points below" or label it as an example at an assumed spend ratio. (b) Recompute Table 7 at X in {2.5, 5, 9} as promised, or state in the table title that 11 is a proxy and that conclusions switch below the weights shown. (c) Add the test: "and it can show, from cohort payback and retention at a stated discount rate, that its marginal growth spend earns more than it costs". (d) State the owner's discount rate beside every weight.

**N5. The abstract's headline decline has no basis, no familywise caveat, and is smaller on the basis practitioners quote.**
- Severity: High.
- Location: abstract txt:19-22; §1 txt:106-108; §5.2 txt:1875-1881; §9 txt:3038-3040; Table S6 supp:1665-1676.
- Issue: "the 95th percentile of the score fell by 11.9 to 12.7 points between 2016-19 and 2023-25" is quoted without a basis. The two ends are the GAAP operating-margin basis and FCF after SBC; both deduct SBC. Panel computation on the same 1,788 firm-years: -11.5 on the adjusted basis (SBC added back) and -8.6 on FCF before SBC (P95 65.8 to 57.2), the basis in McKinsey, Bessemer and Meritech; the median on that basis moved from 30.7 to 29.2 and the pass rate from 32.6% to 29.0%. Median SBC rose from 6.8% to 12.3% of revenue (share of firm-years above 15%: 13.2% to 38.0%). The paper's own §5.2 says the GAAP decline survives a familywise correction at 10% but not 5% (Holm 0.054-0.208, Romano-Wolf 0.097) and that the 2025 value recovered (to 2025 alone: -4.5, interval -17.7 to +8.7). None of that is in the abstract. A reader will quote "12 points" for "the Rule of 40 at the top".
- Suggested change: abstract: "the 95th percentile of the score fell by 11.9 points on the GAAP basis and 12.7 after stock-based compensation (8.6 on free cash flow before it), a decline that survives a familywise correction at 10% but not 5% and partly reversed in 2025." Add the by-period FCF-before-SBC series and the SBC trend to Table S6.

**N6. The Bending Spoons case stops at the 13 August results; the references say the later filings were "used".**
- Severity: High.
- Location: §6 txt:2216-2399; Table 3 txt:2339-2393; references txt:3134-3137 ("Airtable (4 August), Miro (10 September), term loan add-ons (25 September), Berkshire Hathaway (14 October and 29 October) and senior secured notes (28 October 2026)"); none of them is mentioned in the text (a search of the main text and supplement for Miro, Berkshire, 9.625, 8.625, SACE and term loan returns only that reference entry).
- Issue: since the Q2 results the company has: entered a EUR 500M SACE-backed term loan (24 July); priced term loan B add-ons of $1.25B and EUR 395M due 2031 (25 September; proceeds for Miro, repaying the drawn euro revolver and general purposes; Moody's upgraded to Ba3 from B1, S&P to BB- from B+); closed Miro at an enterprise value of $1.355B (26 October); closed a $330M Berkshire Hathaway private placement of 10 million shares at $33, taking Berkshire to about 4% after a $600M purchase at the IPO (14 and 29 October); and priced $1.25B 9.625% and EUR 500M 8.625% senior secured notes due 2032 at par, upsized to about $1.8B equivalent, issued by subsidiaries, "Bending Spoons will not issue or guarantee the notes", proceeds "intended to fund future acquisitions" (28 October; settlement about 4 November). Consequences for the paper: (i) the 15.5% interest-to-revenue ratio behind the after-interest scores is a Q2 figure; Q2 net debt was $4.09B on cash of $793M (gross about $4.88B, panel arithmetic), and the facilities above are up to $4B or more of new gross debt (panel arithmetic, not netted for the revolver repaid or for undrawn amounts; term loan pricing is not in the releases, so no run-rate ratio was computed); (ii) the notes' stated use of proceeds ("future acquisitions") is evidence of continued reliance on acquisition capital, which is the paper's point that a high score is evidence of access to targets and capital; it does not by itself show a shrinking base, so the paper should say so rather than leave a reader to infer a treadmill; (iii) a reader who knows of the Berkshire stake will treat it as counter-evidence to the paper's charged scores, and the paper is silent; (iv) citing exhibits as "used" that the text never uses misleads.
- Suggested change: add a dated paragraph, "Since the second-quarter report", listing the above with the filing dates, and state that the scores in Table 3 are as of the 13 August report and that interest and leverage have risen. Say that the paper takes no view on the company's valuation or on the Berkshire investment. Either use the 6-Ks or remove them from the reference note.

**N7. No owner-type analysis for private-equity or permanent-capital owners, and one quotable sentence that is likely wrong in practice.**
- Severity: High.
- Location: Ownership paragraph txt:2728-2741; §8.2 txt:2930-2933; Remark S8 supp:382-392; §7.5 txt:2786-2792.
- Issue: the paper contains no discussion of PE or permanent capital. Owner type is left to Remark S8 (no numbers) and the companion paper. The only concrete owner statement is "A sponsor's faster decisions change nothing in these cases, because change capacity, not decision bandwidth, binds" (txt:2734-2736). The model's change capacity is 10% of employees a year (range 5 to 22%), calibrated to a public company's surveys (txt:2613-2617). A sponsor changes capacity by replacing staff and management and by accepting a dip sized to covenant headroom, not a guided one to two points of revenue. The case firm illustrates it: Bending Spoons let go "a vast majority" of Vimeo's staff about eight weeks after the 24 November 2025 close (PetaPixel, 23 January 2026; round-1 check, not re-read this round). On the other side of the ledger, permanent-capital owners (a long-hold acquirer, a family or sovereign holder) have lower hurdle rates and longer horizons, which in the paper's own example (N3) raise the decision weight and the dip they tolerate. Read plainly, the paper says that PE ownership does not speed AI transformation and that owner type changes pace but not level; neither is supported.
- Suggested change: (a) replace the sentence with "In these cases a faster decision process changes nothing because change capacity binds; a sponsor can raise change capacity by replacing staff and by accepting a larger dip, which the central case does not model." (b) Add a half-page table of what each owner type changes in the paper's parameters, with direction only (weight X, discount rate, horizon, dip, change capacity, decision speed) for public, PE-sponsored, permanent-capital and founder-controlled owners, and say that magnitudes are in the companion paper and are not tested here. (c) Add an owner-led row to Table 5 or state that the table is a public-firm case (R22).

### Medium

**N8. The success-rate re-grounding mixes definitions, and the pace headline almost doubled without an explanation in the text.**
- Severity: Medium.
- Location: §7.3 txt:2606-2626; Table S7 supp:1719-1735; abstract txt:25-27; §1 txt:125-127; response rows EX-4 and FI-14.
- Issue: (i) 0.70 is Forth et al.'s share of transformations that "created value" (30% win zone plus 44% worry zone, 74% rounded down); the worry zone is "some value, missed targets". The 0.80 is the rate "with all six factors" present, a conditional rate. (ii) The realised share of 67% is Bucy et al.'s figure for "successful" transformations (all others 37%). Applying 67% to a success count that includes the worry zone probably overstates: a crude blend, 0.30 x 0.67 + 0.44 x 0.37, is 0.36 against 0.70 x 0.67 = 0.47 (panel arithmetic; it assumes the worry zone resembles Bucy's "others", which is an assumption). (iii) The text asserts that the outcome rates "already count transitions lost to leadership changes and changes of strategy" (txt:2623-2625) without showing that the surveys do. (iv) The headline realised share by 2036 moved from 23% in v1 to 41% (embedded 61%) because success went from 0.54 to 0.70 and the disruption haircut was removed (embedding probability 0.34 to 0.70, per the response). The main text does not say it moved or why. Both surveys are self-rated by consultancies with the period not stated. Table 6 does show the 2036 range of 56 (slow) to 78 (fast), so the uncertainty is visible.
- Suggested change: state the bridge from v1 in one sentence; present p and b together as one pace parameter with its definition; say the central case is a survey-average transformation, not a measured outcome; label 0.80 as conditional on all six factors.

**N9. The screening-weight range is in the supplement, not the text a reader quotes.**
- Severity: Medium.
- Location: Definition 1 txt:491; §8.1 txt:2894-2896; Table S7 supp:1848-1855; abstract txt:18-19.
- Issue: Bessemer's page (verified this round) says the implied growth-to-profitability ratio ranged from about 2x to 9x over the past handful of years, treats 2020-21 as outliers, offers 2x to 3x "in a normalized period" as a conservative base, applies it to public companies "as long as the growth is efficient" and says the framework is "most relevant for late-stage businesses". Definition 1 and §8.1 give only 2 to 3. Meritech's 14 August 2026 regression (growth 3.8x as strongly correlated with the multiple as FCF margin) is not cited. An investor who knows either source sees the paper as understating the spread of practice, which weakens an otherwise correct statement that a weight of 2 to 3 "reflects a choice of persistence" (txt:975-976).
- Suggested change: Definition 1: "Bessemer's Rule of X weights growth at about 2 to 3 in a normalized period (the implied ratio ranged from about 2 to 9 over 2019-24 and was highest in 2020-21)." §8.1: cite the 2 to 9 and Meritech's 3.8 with the dates.

**N10. The decision-versus-screening weight claim has no level anchor, and the one practitioner-observable proxy is hidden in the supplement.**
- Severity: Medium.
- Location: abstract txt:18-19; txt:913-914; supp:290-292 ("a firm valued near three times revenue would have a decision weight near or below three"); §5.4 txt:1949-1971; Table S7 supp:1839-1846.
- Issue: "exceeds the screening weights ... when its revenue multiple does" is correct and trivial until the reader knows the multiples. Published level data: SEG 3Q25 index median EV/TTM revenue 5.3x; 2.2x for firms growing 10% or less, 6.2x at 10-20%, 8.1x at 20-30%, 10.8x above 30%; Meritech 14 August 2026: 63% of public software companies below 5x NTM revenue and 14 above 10x, median ARR multiple 4.3x. So for most public software firms the multiple, and with it the decision weight in the paper's small-share limit (txt:970-972), is about 5 or lower; only fast growers approach the 10 of the worked example. Separately, Table S7 gives a market-observable weight from CAC data: Aleph and Benchmarkit report a blended CAC ratio of 1.30 dollars of sales and marketing per dollar of new ARR (new names 1.63; median payback 16 months), which at alpha of 0.45 to 0.25 gives X of 2.9 to 5.2. The table itself labels it average, not marginal, cost, from a benchmark of unstated public or private mix. §5.4 lists seven proxies spanning 0.05 to 10.1 and does not list this one.
- Suggested change: add the SEG growth-bucket multiples and Meritech's distribution to §3.6 after the worked example; move the CAC-ratio proxy into §5.4 with its caveats, and translate the §5.7 gap decomposition (29.4 of 41.3 points from lower selling and marketing, txt:2024) into a CAC-payback-style metric investors use.

**N11. "About a fifth of a point" is the flattest specification; the recent GAAP slope is two to three times steeper.**
- Severity: Medium.
- Location: abstract txt:21-22; §1 txt:98-102; §5.3 txt:1905-1940; Table 2 txt:1772-1800 (rows for 2020-25); §9 txt:3035-3038.
- Issue: the abstract and conclusion quote the full-period primary slope (-0.22 GAAP, -0.16 after SBC). §5.3 itself reports -0.60 on the GAAP basis in 2020-25 (-0.22 in 2010-19), a steepening that survives a familywise correction at 10% (Holm 0.037-0.060) but not after SBC (-0.35 in 2020-25), and a local conditional slope of -0.41 and -0.35. The abstract has "the data do not identify the weight firms act on" but not "chosen points, not any firm's trade-off" (the introduction has it, txt:76-77), and the negative sign does not survive a familywise correction (txt:1920-1924). The sell-side risk in round 1 stands: the figure will be put into single-company models.
- Suggested change: abstract: "among the best performers a point of growth came with about a fifth of a point less margin over 2010-25 (about 0.6 on the GAAP basis in 2020-25); these are the points firms chose, not any firm's trade-off, and the sign does not survive a familywise correction."

**N12. "Because fast growers became scarcer" and "no detectable change" are stated more strongly than the intervals allow.**
- Severity: Medium.
- Location: abstract txt:19-22 and §1 txt:106-108; §5.2 txt:1883-1899; Table 2 rows T(0), T(20%).
- Issue: the reweighting attributes -7.9 of the -11.9 GAAP change to composition (interval -17.2 to -2.7) and -4.1 to within-bin change (-9.7 to +2.8): two thirds, with wide intervals, not the whole. The abstract's "in every sample variant, because fast growers became scarcer" drops that. The abstract also says "the best margins attainable at a given growth rate showed no detectable change"; but T(20%), the 95th-percentile margin among firm-years growing at least 20%, fell by 10.2 points on the GAAP basis (-15.1 to +1.1), and T(0) after SBC fell by 3.3 with an interval that excludes zero under E1. §5.2 itself says "an absence of detectable change rather than proof of stability" (txt:1896-1897).
- Suggested change: "largely because"; "no change detectable at these sample sizes, with the margin at 20% growth down by about 10 points on the GAAP basis (interval including zero)".

**N13. Basis comparability: the recommended basis is not the one practitioners quote, and the size split shows how large the gap is.**
- Severity: Medium.
- Location: §4.6 txt:1736-1756; §8.3 txt:2962-2967; §9 txt:3061-3063.
- Issue: the paper says it "treat[s] the latter [FCF after SBC] as the economically relevant one" and suggests "computing the score as this paper does". McKinsey and Bessemer use FCF before SBC; Bain, SEG, Standard Metrics and Vista use EBITDA-type margins (round-1 checks). Panel computation, 2023-25 by prior-year revenue: $1-5B firms (n = 111) pass at 51.5% on FCF before SBC, 14.4% on GAAP and 9.7% after SBC (medians 40.4 and 23.1); $5B and above (n = 39): 43.6%, 23.1% and 12.8%. A large-cap growth investor will therefore see the paper's "9.7%" and the market's "about half" as contradictory unless the basis is on the face of every number.
- Suggested change: put a one-row-per-basis bridge in §4.6 for the median firm (GAAP 12.0 to adjusted 26.4 to FCF before SBC 29.2 to after SBC 15.3), state that scores on the recommended basis are not comparable with quoted ones, and add "(basis stated)" to the conclusion's recommendation. Include the size split.

**N14. Sample framing and the anchor are still opaque to a practitioner.**
- Severity: Medium.
- Location: §4.1 txt:1626-1627; §4.2 R2 txt:1655-1665; §7.3 txt:2583-2604; Table 5 lower panel.
- Issue: "the industry to which the Rule of 40 is usually applied" is asserted, not shown; the practitioner indices (BVP Cloud Index, Meritech, SEG SaaS) are SaaS and cloud, and SIC 7372 includes game publishers, a casino-gaming supplier, an AI-cloud provider and a Chinese download client. The sensitivity rows (Table S2) show the headline survives (also my panel computation: dropping 13 registrants, 94 firm-years, leaves the P95 change at -11.5 and -11.7), so the issue is framing and credibility, not result. The calibration anchor of Table 5 is 13 firm-years of 7 firms, selected on the score, and is not named. Panel reconstruction: Palantir 2025, Clear Secure 2023-25, Duolingo 2023-25, monday.com 2023-24, Global-E 2024-25, Cellebrite 2024, CrowdStrike 2023. Three of the 13 are Clear Secure (round-1 B2: free cash flow about 17 points above operating margin from prepaid subscriptions) and three are Duolingo (prepaid annual subscriptions); the intercept of 42 that drives the 2036 path inherits that. Round 1 asked for a flag on deferred-revenue-driven free cash flow; it is not there.
- Suggested change: say "the industry to which the rule is applied in part"; add a Table S2 row restricted to SaaS-index members or to firms the classifier cannot reject; name the 13 anchor firm-years in the supplement with their ratio of free cash flow margin to operating margin.

**N15. "Exceptional firm" is selected on outcome and given typical execution; the abstract omits "not a forecast".**
- Severity: Medium.
- Location: abstract txt:25-27; §7.3 txt:2576-2579; §9 txt:3053-3060.
- Issue: the firm is defined by being in the top 5% of 2023-25 scores (selection on the outcome, so regression to the mean applies to the anchor), then given survey-average execution (N8). The abstract says "on a central scenario path an exceptional firm realizes 41% ... by 2036 and scores about 66"; "which is not a forecast" appears in §1 (txt:128) and §7.3 but not in the abstract. The tornado's largest 2036 swing is market growth (58 to 83), so the 66 is dominated by an assumption of 12.7% market growth held constant for ten years.
- Suggested change: add "a scenario, not a forecast" to the abstract sentence; replace "exceptional" by "top-tail (95th percentile of 2023-25)" at first use.

**N16. Miro is the first primary post-IPO data point on the price paid for revenue; the constant-price assumption needs a caveat.**
- Severity: Medium.
- Location: §6 txt:2292-2304; Proposition 8(b) txt:2123-2135.
- Issue: the 6-K of 10 September states an enterprise value of $1.355B and about $600M of annual recurring revenue (equity value about $1.79B including net cash), so about 2.3x ARR, closed 26 October with about $295M reinvested by Miro holders in 6.2 million new shares. That sits inside the paper's 1.7 to 3.2 and below X = 2.5. It also shows that the price per dollar of revenue is measured on ARR, not GAAP revenue, and net of cash acquired. Proposition 8(b) assumes a constant price up to a supply limit; the text concedes the supply "need not last" (txt:2172-2174) but the proposition is stated without a price-volume term.
- Suggested change: add Miro as a fourth price (2.3x ARR, enterprise value, 6-K of 10 September) with the ARR caveat; add "or the price rises with volume" to the sentence after Proposition 8.

**N17. No "how not to use" box; the ceiling is not stated to be a cap on valuation.**
- Severity: Medium.
- Location: §8; §8.6 txt:3012-3026; §8.3 txt:2950-2952.
- Issue: round 1 asked for one box. The misuse routes remain: (1) "ceiling below 100" read as a cap on terminal multiples (Table 4 is an after-tax cash score after SBC of a mature asset-light firm at fixed prices at a stated cost structure); (2) the fully charged score as a short headline (now labelled); (3) the chosen-points slope in a company model; (4) the pace as a go/no-go for a plan; (5) a number quoted without its basis.
- Suggested change: add at the end of §8: "How not to use these results. (1) Table 4 bounds a cash score at stated costs and fixed prices; it is neither a forecast of scores nor a cap on valuation. (2) The slopes of §5.3 describe points firms chose; they are not a firm's trade-off. (3) A firm that cites the decision weight to justify a low score must show, from cohort payback and retention at a stated discount rate, that its marginal growth spend earns more than it costs. (4) Fully charged scores are lower bounds. (5) Scenario paths are not forecasts. (6) Quote the margin basis, the growth measure (reported or organic) and whether interest is deducted."

**N18. The paper does not say that it tests nothing about prices or returns.**
- Severity: Medium.
- Location: §1 txt:160-161 (cites Lee, 2024 as the only peer-reviewed study "as an investment screen"); §8.6.
- Issue: nothing in the paper tests whether any basis of the score, the organic score or the durable component predicts multiples, returns or credit outcomes. An allocator will read the practitioner implications (§9) as investment guidance.
- Suggested change: one sentence in §8.6: "We do not test whether any version of the score predicts valuation multiples, returns or default; the implications in §9 concern measurement and firm decisions."

**N19. Stewardship items: competing interests, licence, and how the AI panels are named in the text.**
- Severity: Medium.
- Location: Table 9 txt:3793 ("Competing interests: No statement"); licence note txt:40-42; §4.2 txt:1608-1611, 1663 ("review panels"); Appendix B txt:3757-3762.
- Issue: (i) the paper gives frameworks used to judge firms' AI strategies, alongside a companion paper and software; investors expect either a statement or an explicit "none", and Table 9 records a decision not to state. (ii) The CC BY-NC-ND and PolyForm Noncommercial licence says commercial use "requires the author's prior written permission"; an asset manager cannot tell whether internal use in a research process counts. (iii) §4.2 uses "the review panels" as the source of a sample rule (R2 is applied only to firms "the panels named"); Appendix B says each practitioner panel was "a single agent playing several named roles ... structured self-critique, not a set of independent human experts". The main-text first mention of "panels" should say AI.
- Suggested change: (i) add a one-line competing-interests statement (employment and any commercial interest, or none); (ii) add one sentence on what counts as commercial use; (iii) write "the AI review panels" at first use in §4.2.

**N20. The score after interest measures capital structure; the caveat for levered buyouts is missing, along with coverage.**
- Severity: Medium.
- Location: Definition 5 txt:2111-2112; Proposition 8(c) txt:2136-2141; Table 3.
- Issue: at 7x EBITDA and a 9.5% all-in rate, a 10% grower with a 35% EBITDA margin carries interest of about 23% of revenue and an after-interest score of about 22 against 45 before (round-1 B7; arithmetic, financing terms from round-1 KBRA and Apollo checks not re-read this round). Every leveraged buyout fails the Rule of 40 after interest by construction. A credit memo or covenant could use the after-interest score, which moves with rates, not operations.
- Suggested change: add after Definition 5: "The score after interest measures capital structure as well as operations: a buyout levered seven times EBITDA at a 9.5% coupon carries interest of about 23% of revenue, so its after-interest score sits about 23 points below an unlevered peer with the same operations. Show it beside the unlevered score and with interest coverage."

### Low

**N21. The charging rate is below the issuer's own marginal secured coupon.**
- Severity: Low.
- Location: txt:2265-2268, 2280-2281.
- Issue: r = 8.93% is the continuously compounded value of Damodaran's 9.34% software WACC (round-1: debt weight 5.28%, pre-tax cost of debt 5.29%). On 28 October the company priced USD secured notes at 9.625% (and EUR notes at 8.625%); the ICE BofA single-B effective yield was 7.99% on 28 October and BB 6.67% on 27 October (FRED), so the USD coupon is about 164 basis points over the single-B index. The paper gives the slope (1.2 to 2.1 points per point of r), so the effect at r = 11-12% is about 2.5 to 6.4 points on the user-cost scores (panel arithmetic), small against the 87-114 bracket, but a credit reader will notice.
- Suggested change: add an r = 11-12% row to Table 3 and one sentence naming the secured coupon.

**N22. The organic-score range treats reorganization but not amortization or transaction expense.**
- Severity: Low.
- Location: txt:2227-2235; Table 3 rows for Q2 2026.
- Issue: the range 22 to 44 treats reorganization expense (7.2% of revenue) as a cost of acquiring, but the paper's own text (txt:2256-2258) lists amortization of acquired intangibles (11.7% in Q2; $82.3M) and transaction expense (0.9%) as other channels by which acquisitions reach the GAAP margin. A cash view is available from the filings: H1 2026 operating cash flow was $254.2M and the paper's Q1 figure is 12.6% of $601.3M (restated), so Q2 is about $178M, 25% of revenue, and a cash organic score after interest paid is about 28 (panel computation, approximate because Q1 is restated). It lies inside the paper's range; adding back amortization as well would put the upper end near 56 before interest.
- Suggested change: add the cash organic score as a third reading and state which items each treats as a cost of acquiring.

**N23. Return on acquisition capital: text and table differ.**
- Severity: Low.
- Location: txt:2282-2285 ("22% to 28% ... and 14% to 22% after economic depreciation") against Table 3 (22.3%-25.8% and 13.6%-19.8%, 2025, 24% tax rate).
- Issue: the text range is wider than the table's; presumably the zero-tax variant. Not stated.
- Suggested change: say which variants the text range spans, or use the table's.

**N24. Duplicated sentence.**
- Severity: Low.
- Location: txt:922-923: "The spend data therefore do not identify the decision weight. They do not identify the decision weight."
- Suggested change: delete one.

**N25. References list material the text does not use.**
- Severity: Low.
- Location: txt:3134-3137.
- Issue: besides N6, the Bending Spoons note lists Airtable, Miro, term-loan add-on, Berkshire and notes 6-Ks as exhibits "used" and reads "read in the author's browser and on sec.gov". A reader cannot tell which statement rests on which exhibit.
- Suggested change: cite each exhibit where it supports a number, or drop it.

Findings count: High 7 (N1-N7), Medium 13 (N8-N20), Low 5 (N21-N25), total 25.

---

## 5. Top changes the panel would make (ranked)

1. Add the iso-score caveat to the abstract and a four-point score-to-multiple table with two discount rates and the SEG buckets (N1, N2, N10).
2. Show the decision weight by owner discount rate; fix the one-sided sentence; remove or recompute the four re-entries of the withdrawn weight; add the test for "growth spending earns more than it costs" (N3, N4).
3. Name the basis, the familywise status and the FCF-before-SBC result in the abstract's headline; add the by-period table (N5, N13).
4. Bring the Bending Spoons case to the filings the references already cite (N6, N16, N21, N22).
5. Replace the "sponsor's faster decisions change nothing" sentence; add an owner-type table or say plainly that the paper does not analyse PE and permanent-capital owners (N7); add the how-not-to-use box (N17).

---

## 6. Facts checked

### 6.1 Bending Spoons (primary sources)

Checked 29 October 2026 on sec.gov exhibits (6-K) and the 424B4 text. The F-1 and 424B4 pages were retrieved by a text fetch that stops at about 124,000 characters of a longer page, so several figures could not be read (see "Not verified").

| Item | Source | Result |
|---|---|---|
| IPO terms | 424B4, 1 July 2026 | $29.00 a share; 57,971,015 shares (34,398,640 by the company, 23,572,375 by selling shareholders); gross $1,681.2M; Nasdaq "BSP". Paper: listed July 2026 (Dealroom) consistent |
| FY2024 and FY2025 revenue | 424B4 | $671,053K and $1,306,404K; growth 73.4% and 94.7% (paper: 73.4%, 94.7%). Agrees |
| Operating income | 424B4 | $127,352K and $277,851K; margins 19.0% and 21.3%. Agrees with Table 3 |
| Interest expense | 424B4 | $32,605K and $142,601K; 4.9% and 10.9% of revenue. Agrees |
| Operating cash flow | 424B4 | $204,895K and $290,600K; 30.5% and 22.2%. Agrees |
| Net cash from investing | 424B4 | $(889,654)K and $(1,851,874)K; 132.6% and 141.8% of revenue. Agrees |
| NRR | 424B4 | 2023 93%, 2024 91%, 2025 95%, Q1 2026 94%. Agrees with the paper's 91 to 95% range |
| Adjusted operating margin | 424B4 | 36% (2023), 45%, 47%, 51% (Q1 2026); add-backs: amortization and impairment of acquired intangibles, transaction-related expense, reorganization-related expense, other. Paper's 44.6, 46.9, 51.2 consistent |
| Q2 2026 results | 6-K Ex. 99.1, 13 August | Revenue $704.2M (+126%); organic revenue growth 3% (footnote 4: same businesses a year earlier, including estimated pre-acquisition revenue); operating income $240.3M (34%); interest expense $108.97M (15.5%; up $73M); net income $177.0M; reorganization $50.8M (7.2%); transaction $6.6M (0.9%); amortization of acquired intangibles $82.3M (11.7%); net debt $4.09B; cash $793M; leverage 2.4x net debt/adjusted EBITDA. Agrees with Table 3 and txt:2216-2235 |
| H1 2026 statements | 6-K Ex. 99.2 | US GAAP (Note 1). H1 2026 revenue $1,305.5M; operating income $360.4M; interest expense $202.2M; OCF $254.2M; interest paid $161.2M (80% of expense); PP&E $4.0M; acquisitions $2,286.3M of $2,290.2M net investing (99.8%); SBC $43.0M. H1 2025: revenue $570.0M; interest expense $55.0M; interest paid $49.7M (90%); acquisitions $575.2M of $575.6M (99.9%); PP&E $0.28M. All agree with txt:2253-2263 |
| Subsequent events (Note 15) | Ex. 99.2 | 24 July 2026: new EUR 500M SACE-backed medium-to-long-term term loan; definitive agreement to acquire Formagrid (Airtable). Not in the paper |
| Term loan add-ons | 6-K, 25 September | $1.25B add-on to USD TLB and EUR 395M add-on to EUR TLB, both due 2031 (above the $750M and EUR 250M targets); proceeds for Miro, repaying the drawn euro revolver, general purposes; Moody's Ba3 from B1, S&P BB- from B+. Pricing not stated. Not in the paper |
| Miro signing and closing | 6-K, 10 September and 26 October | All cash; enterprise value $1.355B; equity value about $1.79B including net cash; about $600M ARR; $295M reinvested in about 6.2M new shares; closed 26 October. Not in the paper |
| Berkshire Hathaway | Company release 14 October; 6-K 29 October (closing) | 10M ordinary shares at $33.00 = $330M private placement; Berkshire's total ownership "to 4%"; earlier $600M at the IPO. Not in the paper |
| Senior secured notes | 6-K, 28 October | $1.25B 9.625% due 2032 (Bending Spoons US Inc.) and EUR 500M 8.625% due 2032 (Bending Spoons Operations S.p.A.), at par; upsized from $1.5B to about $1.8B equivalent; "Bending Spoons will not issue or guarantee the notes"; proceeds "intended to fund future acquisitions"; settlement about 4 November; Luxembourg Euro MTF listing. Not in the paper |
| Moody's | Teleborsa report of 27 October (secondary) | Ba3 on the notes, Ba3 CFR, outlook stable; target net debt/EBITDA of 2 to 3x. Secondary; not re-read. The NRR of 97% attributed to Moody's in round 1 is unverified and not used |

Not verified (could not be read in the truncated 424B4/F-1 text): pro forma 2025 revenue of $2,608.5M; purchase prices of AOL, Eventbrite and Vimeo (1.7 to 3.2x); Vimeo's $1,359M price, its 24 November 2025 close and the 327 days and $376.9M of pre-close revenue; the full material-weakness sentence (the summary bullet was found); interest paid for 2024 and 2025 (the paper says it is not in the documents it read). Arithmetic checks that the paper's ratios imply: 2.0x pro forma (2,608.5 / 1,306.4 = 1.997) is internally consistent.

### 6.2 Market and practitioner sources (re-read this round)

| Item | Source | Result |
|---|---|---|
| Bessemer Rule of X | bvp.com/atlas/the-rule-of-x | Multiple regression "over the past ~5-6 years" on the BVP Cloud Index; implied growth-to-profitability ratio "~2x to ~9x in the past handful of years", 2020-21 outliers; 2x to 3x "in a normalized period" as a conservative base; public companies "as long as the growth is efficient"; about 2x for private late-stage; R-squared 50% (Rule of 40) against 62% (Rule of X); "most relevant for late-stage businesses". Paper: matches Table S7; Definition 1 and §8.1 omit the range (N9) |
| Software Equity Group 3Q25 report | sandhill.com PDF | Weighted Rule of 40 (1.33 x growth + 0.67 x EBITDA margin): above 40 12.7x; 30-40 7.9x; 20-30 5.2x; 10-20 3.4x; below 10 1.6x. Index median EV/TTM revenue 5.3x. By growth: 10% or less 2.2x; 10-20% 6.2x; 20-30% 8.1x; above 30% 10.8x (5.6% of the index). Not cited in the paper. SEG's 2Q26 report was not located |
| Meritech Software Pulse, 14 August 2026 | meritech.substack.com | Growth about 3.8x as strongly correlated with the multiple as FCF margin; median ARR multiple 4.3x; 63% below 5x NTM revenue; 14 above 10x. (The 31 July edition used in round 1: 4.1x, 70%, 10 companies.) An October edition was not located. Not cited in the paper |
| FRED | BAMLH0A1HYBBEY, BAMLH0A2HYBEY | BB effective yield 6.67% (27 Oct 2026); single-B 7.99% (28 Oct 2026) |
| Palantir | Panel computation on `panel_v3.csv` | FY2025 GAAP score 87.8 (growth 56.2%, operating margin 31.6%): agrees with "88" at txt:2939; FCF-after-SBC score also 87.8. The Q2 2026 figures of 155 and 140 were verified against the 8-K in round 1 and not re-fetched |

Carried from round 1 and not re-read this round: Bain 2018 and 2026, McKinsey 2021, Vista, ICONIQ, Standard Metrics, KBRA, Apollo, White & Case, Constellation FY2025 release, PetaPixel (Vimeo layoffs), Exzeo release, Damodaran, SaaStr.

### 6.3 Panel computations (not in the paper)

**P1. Score by basis and period** (E1, 1,788 firm-years, `panel_v3.csv`; method reproduces the paper's P95 values of 43.9, 55.9, 44.6 and 57.3 and its 2023-25 medians and pass rates).

| Basis | Statistic | 2010-15 | 2016-19 | 2020-22 | 2023-25 | P95 change 2016-19 to 2023-25 |
|---|---|---|---|---|---|---|
| GAAP operating margin | median / P95 / pass % | 23.2 / 60.8 / 17.2 | 18.9 / 55.9 / 14.1 | 15.1 / 54.6 / 15.8 | 12.0 / 43.9 / 9.7 | -11.9 |
| Adjusted (SBC added back) | median / P95 / pass % | 28.5 / 66.9 / 27.4 | 28.9 / 64.9 / 26.2 | 28.6 / 67.2 / 27.9 | 26.4 / 53.4 / 24.8 | -11.5 |
| FCF before SBC | median / P95 / pass % | 29.6 / 71.0 / 26.4 | 30.7 / 65.8 / 32.6 | 32.2 / 80.3 / 34.2 | 29.2 / 57.2 / 29.0 | -8.6 |
| FCF after SBC (paper) | median / P95 / pass % | 24.0 / 63.0 / 17.0 | 23.6 / 57.3 / 18.8 | 17.9 / 60.2 / 18.7 | 15.3 / 44.6 / 9.2 | -12.7 |
| Median SBC, % of revenue | | 4.1 | 6.8 | 10.7 | 12.3 | |
| Share of firm-years with SBC above 15% of revenue | | 4.7% | 13.2% | 35.8% | 38.0% | |

**P2. Sample sensitivity.** Dropping 94 firm-years of 13 registrants (Activision, Bally, Changyou, CoreWeave, Electronic Arts, Inspired Entertainment, PLAYSTUDIOS, Roblox, Take-Two, THQ, Xunlei, Mobileye B.V. and Mobileye Global; 1,694 firm-years left): P95 change 2016-19 to 2023-25 of -11.5 (GAAP), -11.7 (after SBC), -7.4 (FCF before SBC); 2023-25 pass rates 9.7% (GAAP), 9.2% (after SBC), 29.5% (before SBC). The headline survives.

**P3. Pass rate by prior-year revenue, 2023-25** (n; FCF before SBC / after SBC / GAAP pass rates; median score before / after SBC): $0.1-0.5B (169): 13.9 / 6.0 / 4.8%; 19.0 / 4.7. $0.5-1B (128): 26.0 / 11.8 / 7.8%; 29.7 / 15.4. $1-5B (111): 51.5 / 9.7 / 14.4%; 40.4 / 23.1. $5B and above (39): 43.6 / 12.8 / 23.1%; 37.1 / 29.9.

**P4. Anchor.** The 2023-25 P95 of the cash score after SBC is 44.6. The 22 firm-years at or above it include 9 acquisition-flagged; the remaining 13 are Palantir 2025 (87.8), Clear Secure 2023-25 (66.7, 57.8, 50.7), Duolingo 2023-25 (54.1, 62.6, 61.1), monday.com 2023-24 (54.9, 50.3), Global-E 2024-25 (49.1, 52.9), Cellebrite 2024 (46.6) and CrowdStrike 2023 (46.4). Agrees with the paper's 13 firm-years of 7 firms.

**P5. Decision weight by discount rate** (Proposition 2 worked example: m0 = 0.35, G = 0.04, alpha = 0.3, k = 0; demand pull 0.0698 so that v0 = 10 at r = 10%). v0 = 14.6 (r = 9.34%), 10.0 (10%), 5.8 (12%), 3.7 (15%), 2.1 (22%), 1.35 (31%). Infinite horizon, constant rate.

**P6. Lemma 5 value on iso-score points** (T = 10, G_inf = 3%; EV/revenue = m N_T(eta) + m_LR eta^T M_inf, eta = (1+g)/(1+r)). Persistent margin (theta = 1): r = 9.34%: (30,10) 12.1; (20,20) 11.7; (10,30) 8.3; (0,40) 5.2. r = 12%: 7.6; 7.5; 5.6; 3.7. With half-persistent margin and a mature margin of 25% (theta = 0.5): r = 9.34%: 19.0; 12.7; 7.8; 4.7. r = 12%: 11.4; 8.1; 5.3; 3.5.

**P7. Cash organic score, Q2 2026.** H1 OCF $254.2M less Q1 OCF (12.6% of $601.3M = $75.8M, restated) = $178.5M, 25.3% of Q2 revenue; plus organic growth of 3% gives about 28.

### 6.4 Limits of this panel

- Nine roles, one agent; independence as in round 1.
- No price data: the bridge in N1/N2 is analytical and cites published bucket data; no in-sample regression was run.
- Truncated primary documents (Section 6.1, "Not verified").
- Term loan B pricing is not in the 6-K releases; no run-rate interest ratio was computed.
- Secondary sources used for context only: Moody's via Teleborsa, press reports on the Berkshire price and the company's market value. No finding depends on them alone.
- P5 and P6 use the paper's own parameters and are illustrations of sensitivity, not estimates. P7 uses a restated Q1 cash flow.
- The reading of Forth et al. and Bucy et al. in N8 rests on the descriptions in Table S7; neither source was read.
