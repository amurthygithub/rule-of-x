# Paper 1 round 2: code changes (calibration and econometrics coder)
Written 2 Nov 2026 by the calibration and econometrics coder. Scope: revision_plan_r2.md items B1–B13, C1–C3, the CLAIMS part of A2, and D1–D3 (added by the lead agent). Files changed: `code/calibrate_horizons.py`, `code/paper1_macros.py`, `code/verify_theory.py` (checks whose numbers legitimately moved), `code/estimate_v3.py` (DFL quantile, B13), `code/verify_part2_acquirer.py` (D3). Generated: `notes/calibration_results.json` (new block `r2`), `notes/amin_r2.json`, `paper1/macros.tex`, `paper1/claim_checks.txt`, `sections/tables/tab_calib.tex`, `sections/tables/tab_tornado.tex`, `sections/appendix_proofs.tex` (generated rows of tab:fullcost only), new `sections/tables/tab_isoscore.tex` and `sections/tables/tab_amin_pcc.tex`. No prose was edited. All numbers below come from the code as run on 2 Nov 2026, unless a source is quoted.

Rounding: macros round half up. "old" = the frozen v2 macros (paper1/macros.tex before this pass).

## Two decisions that move many numbers (the editor should know these first)
1. **Error-loss base W_A = s_L = 0.60 (B4, IO2-6).** The ceiling charged compute on 60% of revenue of automated labor and error, misbehavior and common-mode losses on 30%, with no source for the 30%. One base is now used for both (`FC['A_auto'] = 0.60`). Effect: c_full central 4.3 → 6.2 points; margin term 69.0 → 67.5; **G\* central 31.0% → 32.5%** (`\GstarCenOne`; `\GstarCen` 31 → 33); favorable 21.9 → 22.3; conservative 45.5 → 49.5; high compute 59.7 → 61.3. By horizon (central, fixed prices): 2028 36.0 → 37.6, 2031 32.6 → 34.2, 2036 30.1 → 31.7. Target m0F of the central path: 64/67/70 → 62/66/68. The referee's figure for this change alone was 32.5%; it reproduces.
2. **Central basis: maintenance-netted S&M (author decision 4).** Growth spend σ = max(S&M share − b_M, 0) with b_M = 25.1% (`\MaintBase`), the paper's own maintenance base (`spend_maint_base`, E1, notes/empirics_v3.json: median lagged S&M share of firm-years growing at or below the year median; the statistic behind the netted spend ratio 0.99). All-S&M and no-S&M are bounds. Anchor median intercept: netted 30.6 (IQR 24.1–33.8), all 42.0, none 24.1. 5 of 13 anchor firm-years have S&M above the base (`\AnchorSmAboveBase`).

## Item by item

### B1. Pass-through (IO2-1)
**Re-derivation.** Lemma S2(a): γ = 1 − f − u/p and dγ/du = −(1 − φ_e)/p with φ_e = d ln p/d ln u, the elasticity, and dp/du = φ_e p/u. The cited evidence (Ganapati et al. 70%; the DMA study) measures the pass-through **rate** dp/du of a common cost change. The code now uses φ as the rate on the firm's whole unit-cost saving and computes the margin share at the post-cut price:
- non-fee unit cost today C0 = 1 − f − m0A/(1 − τ) (m0A: after-tax intercept of the firm the ceiling or path describes; central: the median anchor firm-year on the netted basis, so C0 = `\PtCzero`% of today's price = 60.2);
- at the full-cost structure K = 1 − f − base/(1 − τ) (= c_c + a_min + c_full);
- saving S = C0 − K; new price p1 = 1 − φS; fees proportional to price, other costs fixed per unit;
- after-tax margin term (1 − τ)(1 − f − K/p1). At φ = 0 it is the fixed-price margin term. First-order elasticity at today's point: φ_e = φ·C0 (`\PtElasHalf` 0.30, `\PtElasSeven` 0.42).
- Central path with pass-through: the industry realizes the same share s as the firm, so m0(h) = (1 − τ)[1 − f − (C0 − sS_h)/(1 − φ s S_h)] (exact; reduces to m0A + s(m0F − m0A) at φ = 0).

**All savings (Prop 4(d)).** Non-discretionary savings are now exposed with the variable ones (Prop 4(d) puts a_min and c_full in the unit cost competition prices). The v2 exposure (cost of revenue only, S = U0 − c_c) is kept as a comparison row.

**Retention rule 1 − φ(1 − H).** Source: the companion paper, Corollary cor:ext-game-engine(a), eq:ext-game-dur (part2/theory_competition.tex), derived from Lemma ext-game-pass(b). Derivation in one line (first order, n = 1/H symmetric Cournot firms, common saving δ per unit): dπ = qδ(1 − φ) + (P − c)dq, and with the Cournot first-order condition (P − c) = |P′|q and dq = φδ/(n|P′|), dπ = qδ[1 − φ + φ/n] = qδ[1 − φ(1 − H)]. Checked numerically in the script (linear Cournot, n = 4: retained share 0.40 = 2/(n+1)). **It is the share of the dollar saving kept once the firm's volume gain is counted; the margin share does not depend on volume when costs are per unit, so H does not enter the score.** The v2 code used 1 − dur as the share of the margin lost at the old revenue; that confused the dollar-profit share with a margin-share loss and ignored the denominator.

**G\* with pass-through, central cost structure (old → new).**
| Reading | φ = 0.5 | φ = 0.7 |
|---|---|---|
| v2 code (dur on variable saving, old revenue), at W_A = 0.30, as published | 36.3 | 38.5 |
| same, at W_A = 0.60 | 37.9 (`\PtGstarOldHalf`) | 40.1 |
| referee's reading: rate φ(1−H), variable saving, post-cut revenue | 33.4 (`\PtGstarRefHalf`) | 33.8 |
| rate φ, variable saving only | 33.7 (`\PtGstarVarHalf`) | 34.3 |
| referee's rate φ(1−H), all savings, all-S&M anchor | 34.2 (`\PtGstarRefAllHalf`) | 35.0 |
| rate φ, all savings, all-S&M anchor | 34.8 (`\PtGstarUbHalf`) | 36.0 |
| **rate φ, all savings, netted anchor (central)** | **36.2** (`\GstarPhiHalfOne`) | **38.3** (`\GstarPhiSevenOne`) |
| rate φ, all savings, no-S&M anchor | 37.0 (`\PtGstarLbHalf`) | 39.9 |
Fixed prices: 32.5. Price cut at the central reading: 22.5% (φ = 0.5, `\PtPriceCutHalf`) and 31.5% (φ = 0.7).
By horizon, central reading, φ = 0.5: 41.8 / 38.1 / 35.2 (`\GstarPhiHalfTwentyEight` 42, `...ThirtyOne` 38, `...ThirtySix` 35); φ = 0.7: 44.2 / 40.3 / 37.2.
Central path with pass-through (netted): φ = 0.5: 45 / 48 / 55 (`\CenRPhiHalfEight`…); φ = 0.7: 45 / 48 / 54; fixed prices 46 / 50 / 59.

**Disagreement with the referee (expected about 32%).** Reproduced: on the referee's own reading (variable saving, rate 0.525 = φ(1−H)) the code gives 33.4/33.8 at W_A = 0.60, which is 31.7/32.1 plus the 1.5-point W_A shift; the referee's "about 33%" with all savings also reproduces (34.2/35.0 here). Our central number is higher for two stated reasons: (i) the price falls by the industry rate φ, not by φ(1 − H), because the (1 − H) factor is the firm's volume gain in dollar profit, which does not enter the margin share; (ii) all savings are exposed (Prop 4(d)), and on the central netted basis today's unit cost includes the maintenance S&M the program removes, so the saving is 45 points of price, not 33. Both choices are visible in the table; the editor can quote the central row and the range.
**Text consequences.** The intro's "36% if half pass through" is now 36% under a different and stated reading (coincidence: 36.3 → 36.2); the description must change from "half of the industry's cost savings" to "a pass-through rate of one half applied to all unit-cost savings, margins at the lower price". Demirer et al. must not be cited for pass-through (A9; not a code item).

### B2. Compute-share range (IO2-3)
**Choice: the value test as stated.** No source documents the factor 0.5 in `CC_VALUE_TEST_CAP = s_L × 0.5`; the assumptions memo (assumptions_round2.md §2, line 127) attributes it to "1 − review share", which the no-review ceiling does not have (Lemma fullcost(c)). So the cap is c_c ≤ s_L = 0.60 (`CC_VALUE_TEST_FACTOR = 1.0`).
- Credible range of c_c at 2025 prices: 1–60% (`\CcLo`–`\CcHi`: 1–30 → 1–60).
- G\* over the range: 27–51% → **28–78%** (`\GstarCcLo` 28, `\GstarCcHi` 78); accountability costs alone 23–72 (`\GstarAccCcHi` 47 → 72). The referee's 27–77 was at W_A = 0.30.
- The old cap 0.30 is kept as a reference point: G\* 52.8 (`\GstarCcOldCap`).
- High-compute case 0.40: G\* 59.7 → 61.3 (`\GstarHigh` 61), now **feasible** (`\CcHighFeasible`); the "infeasible" label must go.
- The by-horizon credible bounds (2028: 2–30%, 2031: 1–25%, 2036: 1–20%) come from the path's own input ranges (ω, κ_front), not from the cap, and are unchanged.

### B3. Compute path (IO2-4)
- Drivers, class d, now named in the JSON (`r2.compute_path`) and as macros: κ_front = 0.33 (`\CcKappaFront`), ω_2028/2031/2036 = 60/40/25% (`\CcOmegaTwentyEight` etc.); κ_fixed(2028) = 0.08% of labor cost (`\CcKappaFixedTwentyEight`), at its floor after, so the path is c_c ≈ 0.2 ω_H.
- **Year the path's compute share reaches the 2025-price headline (6%): 2034.3** (`\CcYearSix` 2034, `\CcYearSixOne`), with ω interpolated linearly between horizons (an assumption; ω is only defined at the three horizons). The referee had "about 2034".
- Sensitivity of the 2028 threshold: ω_2028 = 0.3 → c_c 6.0%, G\* 32.5; ω_2028 = 0.9 → c_c 17.8%, G\* 42.5 (referee: 31 and 41 at W_A = 0.30); κ_front 0.10 → 3.6%, 30.5; κ_front 0.50 → 18.0%, 42.7 (`\GstarOmegaLoTwentyEight`, `\GstarOmegaHiTwentyEight`, `\GstarKfLoTwentyEight`, `\GstarKfHiTwentyEight`).

### B4. Text–code consistency (IO2-5, IO2-7, IO2-10)
- **Error-loss base**: see decision 1 above (`\ErrBase` = 60).
- **Transition cost**: kept at **T_pb = 1.25 years** (`\PaceTpb`). Source: the assumptions register's embedding-time entry (assumptions_round2.md §1.3: "T_emb 1.25 [1, 2] years, class b", Salesforce ~13 months to substantial completion, McKinsey half of value within 18 months), which the params commit of 29 Oct identifies with T_pb (code comment: "T_emb = T_pb, the payback date including the parallel run"); Table S7 row "Embedding time". The "two years" in §7.3 is the pre-commit value and is stale. No source measures transition cost in years of savings directly; say so.
- Dip, central path (netted basis): 3.6 / 3.9 / 4.2 points in 2028/2031/2036 (`\CenDipEight` etc.; old 2.5 / 2.8 / 3.1 on the all-S&M basis; all-S&M basis now 2.3 / 2.7 / 3.0, `\CenDipUbEight`…). The dip scales with the gap m0F − m0A, which is larger on the netted basis.
- Crossing (annual gain > annual dip): **4.0 years** (`\PaceCrossCen` 4, `\PaceCrossCenOne` 4.0), unchanged.
- At T_pb = 2 years (sensitivity): dip 5.7 / 6.3 / 6.8 (`\DipTpbTwoEight`…), crossing 5.6 years (`\CrossTpbTwo`); the referee had 4.0–5.0 and 5.6 on the all-S&M basis.
- **Fast-execution dip on the central path's basis**: 2028 dip 5.1 (old, dropped range basis: upper-quartile anchor, favorable target) → **6.8** on the netted central basis (`\PaceDipFast`), 4.4 on the all-S&M median anchor with the central target (`\PaceDipFastUb`; the referee had about 4.7 at W_A = 0.30). The fast program completes before 2036, so its 2036 dip is zero.
- **"Highest measured error rates"**: now under the ceiling's no-review rule, ε_o + ε_h = 0.18 + 0.20 at unit loss on W_A = 0.60: c_err 7.8 → **22.8 points**, G\* 36 → **48%** (`\CerrHigh`, `\GstarCerrHigh`). With the AI-review bound χ(ε_o + ε_h), χ = 0.60 (Kim et al., P(same wrong answer | both wrong)): 13.7 points, G\* 40.6% (`\CerrHighAi`, `\GstarCerrHighAi`). The old human-catch value 7.8 is kept as `\CerrHighOld`. The referee's 39.3% was the no-review rule at W_A = 0.30 (11.4 points); it reproduces at that base.

### B5. Anchor-sampling interval through the central path (IM2-N6)
Method: the 999 firm-cluster draws of the anchor block of `estimate_v3.py` (`notes/bootstrap_draws_v3.npz`, `anchor__firm_draws`), reconstructed from `data/panel_v3.csv`; the reconstruction reproduces every saved draw of `anchor_p95_m0_ub_med` to 1e-12 (asserted in the script). In each draw the intercept (three bases), the market growth G and the maintenance base are recomputed together; the program share s_h and the target are held fixed (the pace does not depend on the anchor at fixed prices), so R_h = (1 − s_h) m0A + s_h m0F,h + G. 90% percentile intervals.
- Intercept: all-S&M 42.0 [34.1, 52.4] (matches the referee); netted 30.6 [24.1, 34.7]; none 24.1 [18.1, 31.7]. G 12.7 [11.0, 14.8].
- **Central path (netted, central): 2028 46 [39, 50]; 2031 50 [44, 54]; 2036 59 [54, 62]** (`\CenREight`, `\CenREightLo`, `\CenREightHi`, …).
- All-S&M bound: 56 [49, 66]; 59 [53, 68]; 65 [61, 72] (`\CenRUbEight`, `\CenRUbEightLo`…). The referee's 49–66 (2028) and 62–72 (2036) reproduce; with G held fixed (intercept only, as the referee did): 2036 [60.7, 71.6] (`\CenRUbSixIntLo/Hi`).
- No-S&M bound: 40 [34, 47]; 45 [40, 52]; 55 [51, 60] (`\CenRLb…`).
- Table tab:calib now prints the three bases with these intervals.

### B6. S&M basis (IM2-N7; decision 4)
Central path, fixed prices, k = 0, G 12.7 (old → new):
| | 2028 | 2031 | 2036 |
|---|---|---|---|
| all S&M (v2 headline, now a bound) | 56 → 56 | 60 → 59 | 66 → 65 |
| **maintenance-netted (central)** | — → **46** | — → **50** | — → **59** |
| no S&M (bound) | 40 → 40 | 45 → 45 | 55 → 55 |
The referee's 66.2 / 59.5 / 55.7 for 2036 used m0F = 70 (W_A = 0.30); with the new target 68.3 the code gives 65.4 / 58.7 / 54.8. Macros: `\CenR…` is now the netted path; `\CenRUb…` and `\CenRLb…` the bounds; `\CenMzero…` the netted intercept (33 / 38 / 46). Tornado reference is the netted path (2036: 59, 2028: 46).
Under the netted basis the anchor's surplus is positive (median 12.4, `\AnchorPiNetMed`), but the path reports the durable score on every basis (the surplus is scaled only under the upper bound, as before, and enters the tornado). The editor should say so.

### B7. Payback, NPV, decomposition (X2-N1, IO2-other)
Computed on a daily grid from the discrete wave model of `pace()` (same s and dip as Table tab:calib), gap m0F − m0A interpolated linearly between horizons and held after 2036, constant revenue, no growth.
| Execution (netted basis) | flow crossing | cumulative payback, undiscounted | at r = 9.34% | NPV, % of a year's revenue | PV gains / PV dip | cum. at 5 years (points × years) |
|---|---|---|---|---|---|---|
| central | 4.0 y | **7.5 y** | **8.5 y** | 98 | 3.9 | −8.6 |
| fast | 2.4 y | 4.7 y | 5.0 y | 212 | 6.9 | +3.9 |
| slow | 12.6 y | 24.7 y | never | −2 | 0.92 | −9.6 |
Macros: `\PayCrossCen`, `\PayBackCen`, `\PayBackDiscCen`, `\PayNpvCen`, `\PayRatioCen`, `\PayHoldFiveCen`, `\PayHoldThreeCen`, and the same with Fast/Slow; completion year of the central program 2042 (`\PayDoneCen`). The referee's "about 7 and 8" reproduces (7.4 and 8.4 on the all-S&M basis). At r = 10% the ratio is 3.6 (`\PayRatioCenTen`; the referee had 3.3 from a fluid approximation). **Implication for 3–5 year holds:** under central execution the cumulative effect is negative at three and at five years (−8.8 and −8.6 points × years); only fast execution pays back within five years (discounted payback 5.0 years, cumulative discounted ≈ 0 at five years).
**G\* decomposition (central, fixed prices):** G\* = τ + (1 − τ)(c_c + f + a_min + c_full) = 18.0 (tax) + 4.9 (compute) + 2.1 (fees) + 2.5 (accountability floor) + 5.1 (full-cost floors: maintenance 0.5, security 1.3, AI failure 3.2, other 0.2) = 32.5. Macros `\GdecTax`, `\GdecCompute`, `\GdecFees`, `\GdecAcc`, `\GdecFull`, `\GdecMnt`, `\GdecSec`, `\GdecErr`, `\GdecAnc`. The referee's 18.0 + 4.9 + 2.1 + 2.5 + 3.5 = 31.0 reproduces at W_A = 0.30; the floors' share is now 7.6 points.

### B8. Rows for Table 4 (X2-N11, X2-N4)
- **k < 0 (annual upfront billing, deferred revenue)**: G\* = (1 − base)/(1 − k), ψ = 0. At k = −0.3: central **25.0%** (`\GstarKdefCen`), favorable 17.2, conservative 38.1. The referee had 23.8 at the old margin term (69.0); with 67.5 it is 25.0. k = −0.3 is the referee's illustrative value; see D2 for what the data say about deferred-revenue intensity.
- **Typical $1–5 billion firm** (2023–25 core firm-years with revenue $1–5bn: 127 firm-years of 55 firms; medians): growth 15.3%, FCF-after-SBC margin 9.6%, cash score 23.9, GAAP score 20.8; S&M 33.2%, G&A 12.7%, R&D 24.0%, gross margin 77.4%, SBC 15.5%; capex 1.7% of revenue, k = 0.11. Median intercept: netted 18.5, all-S&M 36.3, none 11.6. Gap to the central full-cost margin term (67.5): 49 points (netted), 31 (all-S&M). Durable score at its own growth, netted: 34. Its threshold at its own k: 36.6%. Macros `\Typ…` (`\TypG`, `\TypMargin`, `\TypScore`, `\TypMzeroNet`, `\TypGapNet`, `\TypDurNet`, `\TypGstarK`, `\TypK`, …).

### B9. Pace bridge (X2-N2, IB2-N8)
The realized share by 2036 moved from **21.9%** (pre-commit central; `\PacePrevCenSix`; "23%" in the plan is a rounding of an earlier value) to **40.7%** (`\BridgeOld`, `\BridgeNew`). Shapley decomposition over the three changes (order-free; sums exactly):
- success (ϖ 0.54 → 0.70 and removal of the disruption haircut, q 0.32 → 0.70): **+21.7** points (`\BridgeSucc`), of which ϖ +8.2 and the haircut +13.2 (`\BridgeVarpi`, `\BridgeHaircut`);
- realized share b̄ 0.85 → 0.67: **−7.9** (`\BridgeBbar`);
- embedding time T_emb = T_pb 2.0 → 1.25: **+5.0** (`\BridgeTemb`).
**Does the model give failed attempts zero value?** Yes: s = b̄ × embedded share, and only embedded (successful) transitions realize value. So the calibration target is the per-attempt yield ϖ × b̄ = 0.70 × 0.67 = 0.47 (`\YieldModel`).
- Executives panel's like-for-like 0.30 × 0.67 + 0.44 × 0.37 = 0.36 (`\YieldExec`; the woe zone realizes nothing): realized share by 2036 **31.5%** (`\ShareExec`). The panel's "about 32%" reproduces.
- McKinsey-consistent unconditional yield 0.30 × 0.67 + 0.70 × 0.37 = 0.46 (`\YieldMck`; every non-successful attempt realizes McKinsey's 37%): 39.9% (`\ShareMck`).
- The difference is only whether BCG's woe zone (26%) realizes McKinsey's "all others" 37% or nothing. Mixing BCG's 30% success share with McKinsey's conditional shares is the plan's own construction; McKinsey's success share itself was not read here.
- **BCG win only (0.30 × 0.67), new tornado row**: realized share by 2036 17.4% (`\ShareBcgWin`), 2036 score 50 (`\ScoreBcgWin`; tornado row `\TornBcgWinSixLo` 50).
- Not done: the "owner-led execution row" of the plan (B9 last bullet) was not in my brief; the existing sponsor-latency variant shows no effect because change capacity binds.

### B10. Decision weight by discount rate (IB2-N3)
Supplement S2.2 example (m0 0.35, G 0.04, α 0.3, k 0; λ = 0.0699 set so v0 = 10 at r = 10%), small-share HJB (r − G)v0 = m0 + ((1 − α)/α)(αλv0)^{1/(1−α)}, smaller root: **14.6, 10.0, 5.8, 3.7, 2.1, 1.35** at r = 9.34, 10, 12, 15, 22, 31% (`\WeightWacc`, `\WeightTen`, `\WeightTwelve`, `\WeightFifteen`, `\WeightTwentyTwo`, `\WeightThirtyOne`). The referee's figures reproduce exactly.

### B11. Score to multiple (IB2-N1/N2)
Lemma lem:valuation2, θ = 1, T = 10, G∞ = 3%, r = 9.34%: (g, m) = (30, 10), (20, 20), (10, 30), (0, 40), all scoring 40, are worth **12.1×, 11.7×, 8.3×, 5.2×** revenue (`\IsoThirty`, `\IsoTwenty`, `\IsoTen`, `\IsoZero`); new table `sections/tables/tab_isoscore.tex` (label tab:isoscore). The referee's figures reproduce. At r = 10%: 10.6, 10.4, 7.4, 4.7 (JSON only).

### B12. Tornado G band (IO2-N8)
The 5–30% band had no basis. **Narrowed** to the interquartile range of revenue growth of the 2023–25 core firm-years, 5.4–21.4% (`\GBandLo`, `\GBandHi`; class c, own data, the sample whose median sets the central G), at every horizon. 2036 swing 25 → 16 points (51–67); 2028 10 → 16 (38–54, wider because the old 2028 band was 10–20). With the old band on the new basis the 2036 row would be 51–76 (`\TornGOldSixLo/Hi`). **The largest 2036 swing now comes from execution** (45 to 75; `\TornFirstSix` = "execution"), so the abstract/intro sentence "the largest swing comes from market growth" must change; in 2028 the largest swing is the transient surplus (as before).

### B13. Econometric disclosures
- **"3.8 expected" → 3.6**: `\ContrExpected` now 10% of the 36 estimable contrasts of table38 (was of all 38).
- **Anchor test in family B**: Holm p of the anchor conclusion (Π_lb median > 0, E1), raw p from calibration_anchor_v3.json: normal 0.006, percentile 0.084, basic 0.028 with the 13 estimable family-B tests plus the anchor (`\HolmAnchorNormal`, `\HolmAnchorPercentile`, `\HolmAnchorBasic`; `\FamBNPlus` = 14). Counting the non-estimable T40 test as p = 1 (15 tests, the referee's count): 0.006, 0.096, 0.030 (`\HolmAnchorFifteen…`) — the referee's numbers reproduce on that count. Either way it survives 10% under every type and 5% under normal and basic only.
- **Within-firm lead regressions, bounds**: E2, M = 4 and M = 8 macros added (`\WfEtwoOpLeadRep`, `\WfImpFourOpLeadRep`, `\WfImpEightOpLeadRep`, cash versions, `…LeadSame` for the imputation bounds; from notes/empirics_v3.json `within`).
- **E2 grid-cell minimum inside draws (10 vs 30)**: the cone block of `estimate_v3.py` now records the 60% cell size of every draw (`cone_op_cell60`, `cone_cash_cell60`; sample E2 cells 37 and 38). With the sample's 30-firm-year rule inside draws, 16.8% (GAAP) and 13.0% (cash) of E2 draws are undefined; the defined-draw 90% intervals are **[−0.505, −0.080]** (GAAP; published [−0.508, −0.068]) and **[−0.413, −0.046]** (cash; published [−0.413, −0.041]) (`\DefDrawOpShare`, `\DefDrawOpLo/Hi`, `\DefDrawCash…`, `\DefDrawOpCell`). The referee's figures reproduce. E1 and both imputation bounds are unaffected (at most 0.4% of draws below 30).
- **DFL quantile definition**: `wq()` in `estimate_v3.py` now uses the type-7 (linear) weighted quantile, (cumsum(w) − w)/(Σw − w_last), which equals `np.quantile` for unit weights; v2 used Hazen positions. Effect (E1, point estimates, points): GAAP total −12.0 → −11.9 (now equal to the headline P95 change), composition A −7.2 → −5.6, within A −4.7 → −6.3, composition B −7.9 → −7.6, within B −4.1 → −4.3, size-mix within −13.2 → −13.0; cash total −12.8 → −12.7, composition A −16.8 → −12.5, within A +4.0 → −0.2, composition B −8.2 → −7.9, within B −4.6 → −4.8, size-mix −13.1 → −13.1. The cash composition-A term moves 4.3 points with the quantile definition alone, another sign that the decomposition is not robust (A4). No other statistic in `notes/empirics_v3.json` changed (checked statistic by statistic: only the 22 `rw_*` entries; families, anchor, frontier-slope and the five other v3 tables are byte-identical).

### A2. CLAIMS check
Produced by `code/paper1_macros.py` (writes `paper1/claim_checks.txt`; stops the script on a failure unless P1_CLAIMS_WARN_ONLY=1). Changes:
- New helper `types_pass()` evaluates interval claims under all four 90% interval types (percentile, basic, normal, BC). Holm claims use the three available p-value types (normal, percentile, basic) and Romano–Wolf; the outputs carry no BC p-value (stated in the file).
- Claims rewritten to what holds under every type (these are the statements the text must now make; the editor revises the prose per A1–A4):
  - GAAP P95 decline: survives Holm at 10% under normal, percentile and Romano–Wolf but **not basic** (0.054–0.208); none at 5%.
  - Cash P95 decline: fails Holm at 10% under every type and RW (new claim).
  - T(0) GAAP includes zero under all four types; **T(20%) GAAP excludes zero under basic, normal and BC, not percentile.**
  - T(0) after SBC: excludes zero under E1 with percentile and basic (not normal, BC), and in 2 of 4 views.
  - Composition (B): excludes zero under 3 of 4 types (not basic) on both bases; within-bin (B) includes zero under all four; size mix under all four.
  - GAAP steepening: E1 interval excludes zero under all four types; Holm 10% under every procedure; 3 of 4 views.
  - Cash steepening: E1 interval includes zero under percentile, normal and BC, **not basic**.
  - Gross-margin part of the gap: includes zero in every view under the percentile interval only; **under E1 basic, normal and BC exclude zero** (the v2 text "includes zero in every view" needs the qualifier).
  - Anchor Π_lb > 0 and Π_ub ∋ 0 hold under all four types.
- **Flags**: the two slope-against-−1 tests (psi_op/cash_E1_vs_m1) and the two tautological margin-gap tests (gap_E1, gap_fast_sm_E1) are flagged in their claim text and in a FLAGGED line of claim_checks.txt.
- New horizon and floor claims: the netted path lies between the bounds; the path and its interval upper ends are below 100; payback after crossing; negative cumulative effect at five years; floors at 1% and 5% within 0.01% of revenue; the all-AI condition; the 0.0008 break-even.
- Status: 51/51 → **60/60** (58 after the first pass; two more for the editor's wording, below). The old claim "the floor rounds to the same value at both thresholds" was replaced (0.27 vs 0.28 now) by the 0.01% claim; the old "P95 decline survives Holm at 10% (normal, percentile, RW)" was replaced because it silently omitted the basic type.

### C1. Remote threshold ε̄ (X2-N14, F2-3, RR-N3 to N7)
- No central value in the code: `EPS = {1%, 5%}`, every output at both. (`\AminEpsCen`/`\AminEpsSens` kept as names for the text, but they no longer denote central/sensitivity.)
- Cheapest design: 5%: 1 human over 1 AI, $0.90m, 3.1% a year; 1%: 1 over 2 AI, $0.95m, 0.7%. Three humans: 4.98% a year (`\AminHumanProb`, now two decimals to show the knife edge against 5%).
- **Per-objective reading** (10 objectives, firm-level ε̄ split evenly): 0.51% per objective at 5% (`\AminObjFive`), 0.10% at 1% (`\AminObjOne`); the cheapest admissible design at those levels: 2 humans over 1 AI ($1.40m) and 2 over 2 ($1.45m).
- **Common-mode condition**: no single-provider all-AI design passes iff p^cm ≥ P̄ = 1 − (1 − ε̄)^{1/24}: **0.0021 at 5%** (0.213% per opportunity, `\AminPbarFive`), 0.0004 at 1% (`\AminPbarOne`). In the example p^cm = 0.005 > P̄ at both, so the conclusion is an assumption of the example, as the referees say.

### C2. Break-evens (RR-N1)
Largest cross-type p^cc at which each design stays admissible ((P̄ − P)/(1 − P)):
| Design | ε̄ = 1% | ε̄ = 5% |
|---|---|---|
| 1 human + 1 AI | not admissible at p^cc = 0 | **0.00084** (`\AminPccOneOneFive`) |
| 1 + 2 AI | 0.00014 | 0.0019 |
| 2 + 1 AI | 0.00031 | 0.0020 |
| 2 + 2 AI | 0.00042 | 0.0021 |
| 3 humans | not admissible | 0.00001 |
Human miss rate on AI-missed items (automation bias), one over one at 5%: admissible up to **8.4%** (`\AminPhmFive`); at 10% it fails (the referee's "fails at 10%" reproduces). The cheapest design as a function of p^cc and of that miss rate is the new table `sections/tables/tab_amin_pcc.tex` (tab:amin-pcc). At 5%: 1H+1AI up to p^cc 0.0008, then 1H+2AI ($0.95m) to 0.0019, 2H+1AI ($1.40m) to 0.0020, then none from 0.0025 (the grid's last point). At 1%: none from p^cc 0.0005. The dollar design cost moves 0.090% → 0.145% (as the referee said); the identity of the design moves more. Automation bias is now a parameter (`phm` in `amin_P`), not an exclusion.

### C3. Direct audit and SOX cost (X2-N13, F2-2, RR-N11)
**Source read (with a limitation).** KPMG, *The 2025 SOX survey*, https://kpmg.com/kpmg-us/content/dam/kpmg/pdf/2025/the-2025-sox-survey.pdf, read 2 Nov 2026. A direct download was refused by the egress proxy (403 on kpmg.com), so the only evidence is **WebFetch's extraction of the PDF**. Quoted from that extraction:
- "The results were derived from a web-based survey conducted from Apr'25-Jun'25"; "The experiences of 146 participants".
- "The SOX program's average budget was reported as $2.3 M, with an average time effort of 15,581 hours".
- Budget question: "What was the budget, in dollars, for your SOX program, including both internal and external resources?"
- Chart title: "As revenues increased, the average SOX program budget also rose"; labels "Large size organizations ($25 B+)", "Mid size organizations ($5 B - $25 B)", "Small size organizations (less than $5 B)"; values "$4.7 M, $2.7 M and $1.5 M", which the tool reported "in that order" while saying the extraction "doesn't clearly map each value to its label".
- External audit fees are not named as part of the budget; the survey asks separately about "external audit fee savings".
**Status: the size figures are UNVERIFIED** (WebFetch only; the mapping $1.5M → under $5bn is inferred from the chart title and order). The $2.3M average matches the 29 Oct read recorded in data/tasks/params.yaml (`sox_program_cost_kpmg_2025_reference`). The lead agent should read the chart in the PDF through the browser before the editor cites $1.5M.
**Computation.** Direct cost at $1bn = KPMG SOX program budget for the under-$5bn class ($1.5M, read as including co-source providers but not the auditor's fee) + audit fee at the S&P 500 ratio ($343 per $1M of revenue, Ideagen Audit Analytics FY2022, as before; a lower bound for a $1bn filer, no size-matched fee source read). Old: $343k + SEC 2009 median 404 cost $1.04M.
| | old | new (KPMG small) | KPMG average $2.3M | KPMG mid $2.7M |
|---|---|---|---|---|
| direct cost, % of revenue | 0.14 | **0.18** | 0.26 | 0.30 |
| floor at 5% (+ $0.90m design) | 0.23 | **0.27** | 0.35 | 0.39 |
| floor at 1% (+ $0.95m) | 0.23 | **0.28** | | |
| applications to 0.5%, invoice line $204,672 | 15 | **13** (12 at 1%) | 9 | 7 |
| applications to 0.5%, reference line $80k | — | **30** (29 at 1%) | 20 | 15 |
Macros: `\AminDirect`, `\AminFloor`, `\AminFloorOne`, `\ItgcApps`, `\ItgcAppsOne`, `\ItgcAppsRef`, `\ItgcAppsRefOne`, `\ItgcLineRef` (0.008), `\KpmgSoxSmall/Mid/Avg`, `\AminDirectAvg/Mid`, `\AminFloorAvg/Mid`, `\ItgcAppsAvg/Mid`, `\ItgcAppsRefAvg/Mid`, old values `\AminDirectOld`, `\AminFloorOld`, `\ItgcAppsOld`. **Disagreement with the finance referee (floor 0.34–0.56%, 1–9 applications):** the referee added an audit fee of $1–2M for a $1bn accelerated filer, for which no source is given; with the S&P 500 fee ratio our floor is 0.27–0.39% over KPMG's small-to-mid classes. If a size-matched audit fee of $1–2M is sourced, the floor would be about 0.34–0.54% and 1–9 applications, as the referee says.
**Not changed:** the $350k ITGC-and-revalidation cost inside the design cost (vs the $204,672 line; plan C6, editor/lead). Replacing it lowers the 1H+1AI design to $0.755m (0.0755%).

## Redefined and renamed macros (for the editor; item 1 of the second brief)
The central path is now the maintenance-netted basis. Every macro below keeps its name but changes meaning, unless marked "new".
| Macro | Old meaning (v2) | New meaning | Name for the old meaning |
|---|---|---|---|
| `\CenREight`, `\CenROne`, `\CenRSix` | all-S&M central path (56/60/66) | **maintenance-netted central path (46/50/59)** | `\CenREightAllSM`, `\CenROneAllSM`, `\CenRSixAllSM` (new; 56/59/65), also `\CenRUbEight`… |
| `\CenRLbEight`… | no-S&M bound | unchanged (40/45/55) | also `\CenREightNoSM`, `\CenROneNoSM`, `\CenRSixNoSM` (new, same values) |
| `\CenR{yr}Lo/Hi` | — | new: 90% anchor-sampling interval of the central path | `\CenR{yr}AllSMLo/Hi`, `\CenR{yr}NoSMLo/Hi` (new) for the bounds |
| `\CenMzeroEight/One/Six` | all-S&M intercept (44/47/53) | netted intercept (33/38/46) | `\CenMzero{yr}AllSM` (new; 44/47/52) |
| `\CenDipEight/One/Six` | dip on the all-S&M path (2.5/2.8/3.1) | dip on the netted path (3.6/3.9/4.2) | `\CenDipUb{yr}` (new; 2.3/2.7/3.0) |
| `\CenRiseEight/One/Six` | all-S&M intercept gain | netted intercept gain (2/7/15) | — |
| `\CenRPhiHalf{yr}`, `\CenRPhiSeven{yr}` | all-S&M path with v2 pass-through | netted path with the round-2 pass-through (45/48/55; 45/48/54) | `\CenRPhiHalf{yr}AllSM`, `\CenRPhiSeven{yr}AllSM` (new) |
| `\TornRefSix`, `\TornRefEight` and every `\Torn…` row | all-S&M reference (66, 56) | netted reference (59, 46) | — |
| `\TornAttribution…` | "no S&M buys growth" one-sided row | two-sided row, none vs all S&M (55–65 in 2036) | — |
| `\TornG…` | G band 5–30% (2036) | IQR of 2023–25 growth, 5.4–21.4% | `\TornGOldSixLo/Hi` (old band on the new basis) |
| `\TornFirstSix` | "market growth" | "execution" | — |
| `\TornBcgWin…` | — | new row (BCG win zone only) | — |
| `\PaceDipFast` | fast dip on the dropped range basis (5.1) | fast dip on the netted central basis (6.8) | `\PaceDipFastOld` (5.0 at W_A = 0.60), `\PaceDipFastUb` (4.4) |
| `\VarDipOneMzero`, `\VarCenMzero` | gains from the all-S&M median intercept | from the netted median intercept (10, 15) | — |
| `\VarDipOneShare`, `\VarDipTwoShare`, `\VarDipOneInit` | 32, 39, 41 | 28, 36, 28 (the guided-dip budget binds harder because the gap is larger on the netted basis) | — |
| `\GstarPhiHalf…`, `\GstarPhiSeven…`, `\DurPhi…` | v2 pass-through (dur on variable saving, old revenue) | round-2 mapping (rate on all savings, post-cut price); `\DurPhi…` is now reported only as the dollar-profit share | `\PtGstarOldHalf/Seven` |
| `\CcHi`, `\GstarCcHi`, `\GstarAccCcHi`, `\CcValueTestCap` | cap 30% (51%, 47%) | cap 60% (78%, 72%) | `\CcOldCap`, `\GstarCcOldCap` |
| `\CerrHigh`, `\GstarCerrHigh` | human catch rates (7.8, 36) | no-review rule (22.8, 48) | `\CerrHighOld` |
| `\AminEpsCen`, `\AminEpsSens` | central 5%, sensitivity 1% | 5% and 1%, neither central (names kept) | — |
| `\AminHumanProb` | 5.0 (one decimal) | 4.98 (two decimals, knife edge) | — |
| `\AminDirect`, `\AminFloor`, `\AminFloorOne`, `\ItgcApps`, `\ItgcAppsFb` | 0.14, 0.23, 0.23, 15, 8 | 0.18, 0.27, 0.28, 13, 7 | `\AminDirectOld`, `\AminFloorOld`, `\ItgcAppsOld` |
| `\ContrExpected` | 3.8 | 3.6 | — |
| `\PaceDipCen` | 3.1 | 2.9 (old range basis, moved with W_A; the text should use `\CenDipEight`) | — |
| ceiling macros (`\Gstar…`, `\Margin…`, `\Cfull…`, `\Ceil…`, `\CeilTab…`, by-horizon `\Gstar…TwentyEight` etc.) | W_A = 0.30 | W_A = 0.60 (values move, meaning unchanged) | — |
The abstract currently uses `\CenRSix` for the all-S&M value; with the new meaning it prints the netted value. Use `\CenRSixAllSM` where the all-S&M bound is meant.

## D1–D3 (SEC data retrieved 2 Nov 2026; data/v3_inputs/README_retrieval.md §3–4)
### D2. Deferred revenue and interest income in the cash–GAAP wedge (IM2-N8)
Wedge = FCF-after-SBC margin − GAAP operating margin. Rules (also in `code/calibrate_horizons.py`, block `r2.wedge`):
- Deferred-revenue change: IncreaseDecreaseInContractWithCustomerLiability (CCL) or IncreaseDecreaseInDeferredRevenue (DR). One element present: use it. Both present and equal within 1%: one line under two tags (94 firm-years). Both present and different (46 firm-years): central = CCL (the ASC 606 line), upper = their sum; the medians below are identical under both readings. Missing = missing (coverage 1,660 of 1,788).
- Interest income: InvestmentIncomeInterest, else InvestmentIncomeInterestAndDividend, else InterestIncomeOperating (764 firm-years; InvestmentIncomeInterest alone 696). Not used: InvestmentIncomeNonoperating and InterestAndOtherIncome (may include gains or other income) and InterestIncomeExpenseNonoperatingNet (net of interest expense); hence 764, not the 843 of the README's "any of elements 0–4". After tax at the statutory rate (35% before 2018, 21% after).
- Spot check, anchor firm-years: none reports both deferred-revenue elements (all "one element"); Global-E 2024–25 reports neither; interest income is reported by Palantir, CrowdStrike, Duolingo (3) and Cellebrite only (6 of 13).
Results (medians, points of revenue; `\Wedge…` macros):
| | 2016–19 top 5% | 2023–25 top 5% | anchor (13) |
|---|---|---|---|
| wedge, all firm-years | 3.7 (n 21) | 13.0 (n 22) | 13.4 |
| wedge, firm-years with a deferred-revenue element | 3.5 (19) | 11.5 (18) | 13.1 (11) |
| change in deferred revenue / revenue | 2.8 | 6.5 | 9.4 |
| wedge less the deferred-revenue change | −1.5 | +3.1 | +3.4 |
| after-tax interest income / revenue (firm-years reporting it) | 0.5 (8) | 3.9 (9) | 3.9 (6) |
Reading: on the covered firm-years the median wedge rises by 8.0 points (3.5 → 11.5); net of the deferred-revenue change it rises by 4.6 (−1.5 → +3.1), so roughly 40% of the rise is billing timing (medians are not additive; this is an order of magnitude). Interest income rose from 0.5 to 3.9 points on the few firm-years that tag it. For the anchor, about 9 of its 13-point wedge is deferred revenue, and interest income is about 4 points where reported. All-firm median wedge 2.6 → 3.9.
**Deferred-revenue intensity for B8:** k_def = Δ deferred revenue / Δ revenue, 2023–25 core firm-years with growing revenue: median 0.27 (IQR 0.04–0.53; n = 355) (`\KdefMed`, `\KdefLo`, `\KdefHi`). The central threshold at k = −0.27 is 25.5% (`\GstarKdefMedCen`), close to the referee's illustrative k = −0.3 (25.0%).
### D1. Interest income (F2-1)
- **Anchor sensitivity net of after-tax interest income** (only the 6 anchor firm-years that tag interest income; a missing element is missing): on those firm-years the netted intercept falls from 25.8 to 22.2 (`\AnchorIiMzeroSame`, `\AnchorIiMzero`), and their 2036 central path from about 55.9 to 53.7. On the all-S&M basis the median intercept of those firm-years net of interest income is 37.4. The full anchor cannot be restated: 7 of 13 firm-years have no interest-income element.
- **Bridge row "before net interest"**: added to `code/estimate_v3.py` (bridge bases `cash_bni` and its like-for-like `cash_bnis`) and to the table writer in `code/estimate_v3_report.py` (`sections/tables/tab_bridge_v3.tex` regenerated; the existing rows are relabelled "before interest paid, after tax" and "before interest paid and cash taxes"). Before net interest = FCF after SBC + (interest paid − interest income) × (1 − statutory rate), defined on the 335 E1 firm-years (146 in 2016–19, 189 in 2023–25) that tag interest income. E1, P95 change 2016–19 → 2023–25: before net interest −12.9 [−36.6, +0.2]; the paper's cash basis on the same firm-years −10.8 [−30.1, +4.0]; 2023–25 P95 level 42.4 against 44.3 (`\BridgeChangeBni`, `\BridgeChangeBniLo/Hi`, `\BridgeChangeBnis…`, `\BridgeLateBni`, `\BridgeLateBnis`, `\BridgeNBni`). Removing interest income lowers the 2023–25 top tail by about 2 points and does not remove the decline; on this thin subsample the intervals include or touch zero. The existing rows are unchanged.
### D3. Bending Spoons (IB2-N6, F2-5, F2-other)
`code/verify_part2_acquirer.py`, new section F (checks F1, F2; 80/80 → 82/82). Every 6-K figure is matched by regular expression in `data/v3_inputs/raw/bending_spoons_6k_2026-11-02.json`; sentences relied on:
- 28 Oct (Ex. 99.1, accession 000200471126000021): "The Offerings comprise $1.25 billion aggregate principal amount of 9.625% U.S. dollar-denominated senior secured notes and €500 million aggregate principal amount of 8.625% euro-denominated senior secured notes (collectively, the "Notes"), both due in 2032." "… an upsized dual-currency senior secured notes offering … with an aggregate principal amount equivalent to approximately $1.8 billion." "The net proceeds from the Offerings are intended to fund future acquisitions, to pay costs, fees, expenses, and taxes in connection with the Offerings, and for other general corporate purposes."
- 2 Oct (000200471126000016): "Bending Spoons has successfully syndicated and priced a $1.25 billion add-on to its existing US dollar-denominated senior secured term loan B, due 2031, and a €395 million add-on to its existing euro-denominated senior secured term loan B, due 2031, subject to certain conditions." "Bending Spoons intends to use the proceeds to finance the agreed-upon Miro acquisition, repay the currently drawn portion of its euro revolving credit facility, and for general corporate purposes." "The add-ons are fungible and have terms consistent with certain existing term loan B tranches." (no rate stated)
- 28 Jul (000110465926087587): "… entered into a new €500 million medium-long-term financing …" "The facility, which matures in March 2031, benefits from a guarantee provided by SACE …" (no rate stated); also "€495 million of additional term loan A financing and a €490 million increase in commitments under Bending Spoons' revolving credit facility".
- 4 Aug (000200471126000009): "annual recurring revenue growing over 20% YoY to approximately $480 million as of June 2026" (Airtable). 10 Sep (000200471126000015): "Miro has grown to around $600 million in annual recurring revenue".
- 14 and 29 Oct: Berkshire "will issue 10 million ordinary shares at a purchase price of $33.00 per share"; "total ownership stake … to 4%" (equity; no interest effect).
Cash figures (bending_spoons_cash_interest.json, thousands of USD): interests paid 16,581 / 19,168 / 130,881 (2023–25, 424B4 F-34/F-35), 89,037 (Q1 2026), H1 2026 161,153; H1 2026 interest expense 202,154; principal at 30 Jun 2026 4,983,469.
Results:
- **Interest paid instead of interest expense** (cash basis): interest paid is 4.3, 2.9, 10.0 and 14.8% of revenue in 2023, 2024, 2025 and Q1 2026 (interest expense 4.4, 4.9, 10.9, 15.5; paid/expense 0.97, 0.59, 0.92, 0.96) (`\acqIntPaidShTwentyThree` … `\acqIntPaidShQOne`, `\acqIntPaidTwentyFive`). The 2025 before-interest charged score over all conventions moves from 87.2–114.0 (expense) to **86.6–113.1** (paid) (`\acqChPaidLo/Hi`); the v2 text's "87 to 114" becomes "87 to 113".
- **Run-rate interest after the post-IPO debt**: H1 2026 interest expense annualized $404M + coupons of the 28 Oct notes ($1.25B × 9.625% + €500M × 8.625% at the $1.10/€ implied by the 6-K's "approximately $1.8 billion") $168M = **$572M a year** (`\acqRunRateInt`, `\acqRunRateIntHOne`, `\acqNotesCoupon`). The TLB add-ons and the SACE loan ($2,234M of principal) have no stated rate; priced at the notes' 9.625% as an upper case: $787M (`\acqRunRateIntHi`, `\acqUnpricedDebt`). As a share of Q2 2026 revenue annualized ($2,817M): 20.3% to 27.9%; adding the acquired ARR stated in the 6-Ks (Airtable $480M, Miro $600M; ARR is not revenue): 14.7% to 20.2% (`\acqRunRateShQ`, `\acqRunRateShQHi`, `\acqRunRateShPf`, `\acqRunRateShPfHi`). Limits: part of the TLB add-on repays a drawn revolver (amount not stated), so the upper case overstates; the TLA and RCF increase are not priced.
- **Charging at the marginal coupon** (9.625%, the USD notes, against the 9.34% WACC): 2025 before-interest charged scores **86.0–112.8** (`\acqChCouponLo/Hi`, `\acqCouponMarg`).
- The paper's Bending Spoons basis labels and the SBC note (F2-5) are prose (editor).

## Second brief (2 Nov, after the editor's pass)
- **A4 (IM2-N2)**, point estimates on E1 (data/panel_v3.csv), the f_reweight estimator with the type-7 quantile, 4 to 40 growth bins, both directions: composition term GAAP −16.8 to −2.0 (`\BinCompOpLo/Hi`), cash −17.3 to −6.0 (`\BinCompCashLo/Hi`); within-cell term GAAP −10.0 to +4.9, cash −6.7 to +4.6 (`\BinWithinOpLo/Hi`, `\BinWithinCashLo/Hi`). The referee had −3 to −18 and −8.8 to +5.9 (different bin set); same conclusion, the split is not robust to binning. Quantile shifts 2016–19 → 2023–25 (`\QShift{Op,Cash,Fcf}{Ten,TwentyFive,Fifty,SeventyFive,Ninety,NinetyFive}`): GAAP P10 −19.9, P25 −9.3, P50 −6.9, P75 −4.3, P90 −8.3, P95 −11.9; cash after SBC −13.0, −7.2, −8.3, −7.8, −8.8, −12.7; FCF before SBC −5.5, −0.7, −1.5, −2.9, −6.4, −8.6 (the referee's figures reproduce). First-year firm-years (first year in the panel): 2016–19 55, 2020–22 83, 2023–25 18 (`\FirstYearSixteenNineteen`, `\FirstYearTwentyTwentyTwo`, `\FirstYearTwentyThreeTwentyFive`).
- **A5 (IM2-N3)**: P95 of the GAAP score in 2025 against 2023–24 pooled: E1 +9.2 (`\RecoveryEone`; the referee's 9.3 is the same number, 9.25 before rounding), without acquisition-affected firm-years +2.8 (`\RecoveryNoAcq`). Year on year (2025 vs 2024): +9.9 and +3.2 (`\RecoveryYoyEone`, `\RecoveryYoyNoAcq`); 2024 and 2025 P95 without acquisition years 41.9 and 45.1.
- **Table 7** (`code/playbook/run_archetypes.py`, table writer only; run with `--tables-only`): columns now n, g, m, S&M, G&A, k, (a/σ̂)^{1−α}, which lever ranks first at the position's own weight, g + δ. Dropped: G_i, X̂ and the three "Value per 10%" columns. **X‡_0 is not weight-free** (X‡_0 = k + a^{1−α}/(αℓ) needs demand pull ℓ, which the table can only calibrate from X̂), so it is not shown as a column; the note states that the ratio equals (X‡_0 − k)/(X − k) at the weight at which the position's spending is optimal, and that the G&A cut ranks first at the position's own weight iff the ratio exceeds one (it does not at any position: ratios 0.51–0.81). `notes/playbook_results.json` and `part2/tables/playbook_macros.tex` are byte-identical before and after (sha256 25c49b6a…, b16f0c10…); `sections/tables/levers_position_macros.tex` is unchanged; the `--tables-only` run rewrote `part2/tables/playbook_*.tex` from the same unchanged JSON (deterministic writer; I had no pre-run copies of those files to diff). `verify_part2_playbook.py`: 36/36. The macros `\lpXhat`, `\lpXdagMin/Max`, `\lpScreenBelowAll` still exist (levers_position_macros.tex is written by the same function) and still use X̂; the text should stop quoting them.
- **CLAIMS for the editor's wording**: "significant at 10% after familywise correction under most procedures" (GAAP) is tested as 3 of 4 procedures (Holm normal, Holm percentile, Romano–Wolf; not Holm basic) plus all four interval types excluding zero; "(not significant)" (cash) as Holm normal/percentile/basic and Romano–Wolf all above 10%, with all four unadjusted intervals excluding zero. Both pass. Total 60/60.

## Checks (final, 2 Nov 2026)
- Stages run, in order: `estimate_v3.py` (full 999-replication run in a scratch copy of the repository; outputs copied in after a statistic-by-statistic comparison: only the intended `rw_*` changes and the added `bridge_cash_bni*`, `bridge_cash_bnis*` and `cone_*_cell60` entries), `calibrate_horizons.py`, `paper1_macros.py`, `verify_theory.py`, `verify_part2_acquirer.py`, `run_archetypes.py --tables-only`, `verify_part2_playbook.py`, `verify_part2_accounting.py`, `build_paper1.sh`. `regenerate_all.sh` was not run; engine/ and part2/ sources were not edited.
- `python3 code/verify_theory.py`: **191/191** (was 189/189). Checks updated because their numbers legitimately moved (not loosened): 20 (the duplicated FC inputs: W_A 0.30 → 0.60, c_c credible bound 0.30 → 0.60), 20c (common-mode term 0.33 → 0.66 points at X = 0.6, Y_f = 0.3), 20m (high-error case 7.77 → 22.8 points, no-review rule), 25d (direct cost 0.14% → 0.18%, KPMG), 26d/26e/26f (W_A 0.30 → 0.60 in the c_err parts), 27d (direct cost through the floor). New: 25f (C1–C2 break-evens by bisection, the 0.0021 common-mode condition, printed macros) and 25g (pass-through rate on the post-cut price agrees with the elasticity form of lem:prices(a) to first order; B10 decision weights; B11 iso-score values). `notes/verify_theory_output.txt` holds the run.
- CLAIMS (`paper1/claim_checks.txt`, from `code/paper1_macros.py`): **60/60** (was 51/51), all four interval types, flags written.
- `verify_part2_acquirer.py` 82/82 (was 80/80), `verify_part2_playbook.py` 36/36, `verify_part2_accounting.py` 47/47.
- `NO_COPY=1 bash code/build_paper1.sh`: clean, paper1 80 pages, supplement 49 pages, no undefined references (the new tables tab_isoscore and tab_amin_pcc are generated but not yet \input by the text).

## Open questions for the lead agent
1. **Pass-through central reading.** The round-2 central G* with pass-through is 36.2/38.3% (rate φ on all savings, netted anchor), not the referee's ~32%. The two choices behind the gap (rate vs φ(1−H); all savings from the netted anchor's cost) are argued above; if the lead prefers the variable-only exposure, the macros `\PtGstarVarHalf/Seven` (33.7/34.3) are ready, but Prop 4(d) argues for all savings.
2. **W_A = s_L** raises the headline G* from 31% to 32.5% (`\GstarCen` prints 33). Confirm before the editor rewrites the abstract; the alternative is to state which 30 of the 60 points of automated labor carry consequential errors, for which no source was found.
3. **KPMG size figures** ($1.5M under $5bn) were read only through WebFetch's extraction (kpmg.com refused a direct download, 403). Please confirm the chart in the PDF through the browser before the editor cites it; the $2.3M average is consistent with the 29 Oct read. A size-matched audit-fee source is still missing (the S&P 500 ratio is a lower bound).
4. **X‡_0 is not weight-free** (needs demand pull); Table 7 now shows the ratio test instead. The text's `\lpXhat`, `\lpXdagMin/Max` and `\lpScreenBelowAll` still carry the withdrawn weight.
5. **$350k ITGC-and-revalidation inside the design cost** vs the $204,672 line (plan C6) is unchanged; replacing it lowers the 1H+1AI design to $0.755m.
6. **Owner-led execution row** (plan B9, last bullet) not built: it was not in my brief and the existing sponsor-latency variant shows no effect while change capacity binds.
7. The `--tables-only` run of `run_archetypes.py` rewrote `part2/tables/playbook_*.tex` from an unchanged `notes/playbook_results.json`; the P2 macros file is byte-identical, but I had no pre-run copies of the other P2 tables to diff.
8. Propagation to Paper 2 and the engine (plan step 4): W_A, the value-test cap, the pass-through mapping, ε̄ and the KPMG direct cost are Paper 1 code only so far; `data/tasks/params.yaml` (`part1_ceiling`) and `engine/` were not touched.

## Follow-up 2 Nov (lead-agent rulings)
1. **Pass-through.** The round-2 mapping stays central (36.2 / 38.3). `\PtGstarVarHalf/Seven` (33.7 / 34.3) is the referee-reading alternative. A supplement-ready reconciliation table is written by `code/calibrate_horizons.py` to `sections/tables/tab_passthrough_recon.tex` (label tab:passthrough-recon). It has seven readings, the price cut, the first-order elasticity and the dollar share 1 − φ(1−H). It is not yet \input anywhere.
2. **Error-loss base 60%:** accepted, no change.
3. **KPMG.** Code comments and the `kpmg2025sox` bib entry now cite the archived copy (https://web.archive.org/web/20260318224741/https://kpmg.com/kpmg-us/content/dam/kpmg/pdf/2025/the-2025-sox-survey.pdf, p. 12) with the label "values read from a text extraction, chart layout and labels verified". The entry is updated in both `paper1/refs_paper1.bib` and `paper1/refs_additions_v2.bib`.
4. **Audit fee.**
   - **Central** = Ideagen Audit Analytics accelerated-filer average, $1,492,375. Source: *Audit Fee Trends 2003–2022*, July 2023, p. 14, quoted in the new bib entry `auditanalytics2023fees`.
   - **Low bound** = S&P 500 ratio, $343k. **High case** = large-accelerated average, $5,327,646 (macros only; it fits as the high end of the direct-cost row).
   - The SOX program cost is the KPMG under-$5bn budget, $1.5M, throughout.
   - Macros: `\AuditFeeAccel` 1.49, `\AuditFeeLarge` 5.33, `\AuditFeeSp` 0.34 ($M).
5. **C6.** The design's ITGC-and-revalidation cost is now the sourced line of one in-scope AI application, $204,672 (`ITGC_LINE_DESIGN`). It already contains the revalidation at each model upgrade ($24k / 1.22 years), so it and the $350k described the same object. The change is applied in `paper1_macros.py` and in `verify_theory.py` (`ITGC_LINE25`).
6. **Withdrawn weight.** A comment in `paper1_macros.py`, where it reads levers_position_macros.tex, marks `\lpXhat`, `\lpXdagMin`, `\lpXdagMax` and `\lpScreenBelowAll` "WITHDRAWN UNDER D-1; DO NOT QUOTE". They remain defined.

**Old → new values.** "Previous" is the round-2 first pass; v2 is in brackets where it differs.

| Quantity | Previous | New | Macro |
|---|---|---|---|
| Direct audit + SOX cost at $1bn, % revenue | 0.18 [v2 0.14] | **0.30** (low 0.18, high 0.68) | `\AminDirect`, `\AminDirectLo`, `\AminDirectHi` |
| Cheapest design at 5% (1 human over 1 AI) | $0.90m, 0.090% | **$0.75m, 0.075%** | `\AminCenCost`, `\AminBest` (old `\AminCenCostOld`) |
| Cheapest design at 1% (1 over 2 AI) | $0.95m, 0.095% | **$0.80m, 0.080%** | `\AminSensCost`, `\AminBestOne` (old `\AminSensCostOld`) |
| With 48 opportunities, or an AI common mode of 0.01, at 5% | $0.95m / 1H+1AI | $0.80m / 1H+1AI | `\AminAltNCost` |
| Same at 1% (2 over 1 AI) | $1.40m | **$1.25m** | `\AminAltOneCost`, `\AminAlt` 0.14 → 0.13 |
| Three humans (no AI) | $1.50m, 4.98% | unchanged | `\AminHumanCost` |
| Per-objective designs (10 objectives) | 2H+1AI $1.40m (5%); 2H+2AI $1.45m (1%) | $1.25m; $1.30m | `\AminObjCostFive/One` |
| Floor at 5%, % revenue | 0.27 [v2 0.23] | **0.37** (low 0.26, high 0.76) | `\AminFloor`, `\AminFloorLo`, `\AminFloorHi` |
| Floor at 1% | 0.28 | **0.38** (low 0.26, high 0.76) | `\AminFloorOne`, `\AminFloorLoOne`, `\AminFloorHiOne` |
| Applications to reach 0.5%, invoice line $204,672 (5% / 1%) | 13 / 12 [v2 15] | **8 / 7** (low fee 13 / 13) | `\ItgcApps`, `\ItgcAppsOne`, `\ItgcAppsLo`, `\ItgcAppsLoOne` |
| Applications, reference line $80k (5% / 1%) | 30 / 29 | **17 / 17** (low fee 32 / 31) | `\ItgcAppsRef`, `\ItgcAppsRefOne`, `\ItgcAppsRefLo`, `\ItgcAppsRefLoOne` |
| Applications, invoice line with close fallback | 7 [v2 8] | **4** | `\ItgcAppsFb` |
| KPMG mid ($2.7M) / average ($2.3M) classes, floor at 5% | 0.39 / 0.35 | 0.49 / 0.45 (apps 2 / 4 on the invoice line) | `\AminFloorMid`, `\AminFloorAvg` |

Further consequences:
- At the high case (large-accelerated fee) the floor, 0.76%, is already above the band's 0.5% lower end, so the application count is 0.
- The finance referee's 0.34–0.56% is now matched: their $1–2M audit fee corresponds to the sourced $1.49M.
- Cheapest-design table `tab_amin_pcc.tex`: identities are unchanged; costs fall by $145,328 for every design with AI layers (1H+1AI $0.75m, 1H+2AI $0.80m, 2H+1AI $1.25m, 2H+2AI $1.30m, 4H+2AI $2.30m). The p^cc and miss-rate break-evens depend only on probabilities and are unchanged (0.00084; 8.4%).
- **G\* accountability component: unchanged at 2.5 points.** The ceiling uses a_min = 3% from the register band, not the bottom-up floor. If a_min were set to the bottom-up floor (0.37%), central G\* would be 30.4% instead of 32.5% (`\GstarAminFloor`); the band's low end, 0.5%, gives 30.5% (`\GstarAminLo`).
- The floor sits below the band's 0.5% lower end at the central fee.
- Nothing else downstream uses the direct cost.

**Checks after the follow-up:**
- verify_theory 191/191. Updated: 25d (design costs with the $204,672 line, direct cost 0.30%) and 27d (floor with the new direct cost).
- CLAIMS 60/60. Acquirer 82/82. Accounting 47/47 (Paper 2's own example is unchanged; propagation is pending). Playbook 36/36.
- `NO_COPY=1 build_paper1.sh` clean (80 + 49 pages).

## Follow-up 2 (2 Nov, after the editor's final pass)
1. **tab_calib caption:** "an exceptional firm" → "a top-tail asset-light firm", the term sections/horizons.tex now uses.
2. **tab_tornado:** the label column is now `p{0.62\linewidth}`. The build reports no overfull box for the table, or anywhere else in either document.
3. **tab_passthrough_recon:** the row label is now "Rate on all unit-cost savings (central): margin at the post-cut price, maintenance-netted anchor", and the notes say "The central reading" instead of "The round-2 mapping".
4. **tab_amin_pcc:** ε̄ → π̄ in the header and the notes, matching Remark S10, the glossary and the main text. It is generated by `code/paper1_macros.py`.
5. **IO2-N19, sec_it.**
   - I read the source myself with WebFetch, which returns a summary of the page: IANS, 2025 Security Budget Benchmark Report, page dated 5 Aug 2025, read 2 Nov 2026. Quoted text:
     - "Security budgets averaged 10.9% of IT spending in 2025, a full percentage point below the 11.9% of 2024."
     - "… after the share rose steadily from 8.6% in 2020."
     - The fetch tool reports that 9.9% does not appear on the page.
   - So 0.099 was not a deliberate transformation; it is a value the cited source does not contain. The central is now 0.109; favorable 0.119 (2024) and conservative 0.086 (2020) are unchanged and are on the page. Changed in `FC` and in verify_theory's duplicate.
   - Effect: only the post-quantum line moves (central 0.10 → 0.095 points of revenue). No headline macro moves: G\* central stays 32.5. The only macro that changed is `\CfullHigh` 7.3 → 7.2.
6. **TH2-16:** the verify_theory docstring now reads "about 2.5 to 3 minutes of CPU time; wall clock 3 min 0 s on 2 Nov 2026 here and 5 min 53 s on a referee's copy, so three to six minutes depending on the machine".
7. **IM2-N12, α class.**
   - α is class **d**, which is how it is used. The data identify only α(X − k) (D-1); α is a scenario range bounding the surplus scaling, 0.35 on the central path and 0.3 in the levers table.
   - Changed in three places: `code/data_part2/08_params.py` (alpha_spend_elasticity: grounding d, quality assumed, new source text); `data/tasks/params.yaml`, only that block edited in place; and `notes/assumptions_register.md`.
   - **The register script could not regenerate the whole file faithfully.** I ran the generator (`make_register.py` in the session scratchpad, with `cls.py`) after fixing α in its Part I row and finding text. Against the current live files it first stops on a params path that no longer exists. Once that is tolerated, it rewrites 643 register lines: its "before" baseline (`params.orig.yaml`) and the engine defaults have moved since 29 Oct, so the audit's before/after columns would be wrong.
   - I therefore applied only the script's output for the α rows: the Part I row (c → d), the params row ("c to d"), and the Part I class-count line (c 1 → 0, d 7 → 8). The rest of the register is untouched. The patched script is in the session scratchpad at `work/make_register_r2.py`.
   - **params.yaml was not regenerated from 08_params.py.** I tried it on the live file and restored the backup immediately, because regeneration would have wiped your hand edits since 29 Oct (KPMG by size, the audit-fee references, the varpi notes). 08_params.py does not contain those edits; that drift predates this pass.

**Checks:**
- calibrate_horizons and paper1_macros rerun; CLAIMS 60/60; verify_theory 191/191.
- `NO_COPY=1 bash code/build_paper1.sh` clean: **main paper 80 pages**, supplement 53, no overfull boxes.
- Acquirer, accounting and playbook verifiers were not affected by these changes (last runs 82/82, 47/47, 36/36).

## Follow-up 3 (2 Nov, author decision 7: maintenance-netted S&M central for the levers)
- **Replaced** the CLAIMS entry that asserted `\lpGEFirstAll` = yes. The new entries in `code/paper1_macros.py`:
  - **Recomputed counts (preferred route).** The positions' cell medians come from the playbook's own `archetypes.build_archetypes` on data/panel_v3.csv, A7 excluded. b_M is read from notes/empirics_v3.json and asserted equal to the playbook's `MAINT_BASE`.
  - Rule: at the weight a position's own spending reveals, the growth engine leads the G&A cut iff its growth spend exceeds its G&A share.
  - Recomputed: netted 1 of 6 (Growth corner), all S&M 6 of 6, no S&M 0 of 6; G&A cut first at 5.
  - Asserted equal to `\lpNGEFirstNet`, `\lpGEFirstNetList`, `\lpNGEFirstAllSM`, `\lpNGEFirstNoSM`, `\lpNGACutFirstNet` and `\lpNPositions`; also asserts `\lpGEFirstAll` = no.
  - `\lpRatio` = `\AlphaNet` (0.99) and `\lpBasis` = maintenance-netted.
  - Engineering first at 6 of 6 on the netted basis, and the growth-engine counts of `notes/playbook_results.json` (`ranking_by_basis`) agree with the recomputed counts on all three bases. The engineering count is checked against the JSON only, because the cost-of-revenue lever needs the engine's pass-through state.
  - **Text check:** no sentence of `sections/levers_by_position.tex` (comments stripped) may combine "growth engine" with "every / each position", "all six positions" and similar, plus a lead verb (leads, outranks, ranks above, comes first, ahead of), unless the sentence is negated or bounded ("not", "only", "none", "bound", "all selling and marketing", `\lpNGEFirstNet`).
- **Status:** 62 of 63 pass. **The text check fails on the current prose**: levers_by_position.tex line 32, "At the weight its own spending reveals, every position in Table~\ref{tab:levers-position} ranks automating a share of its growth engine above cutting …". This is expected until the editor's rewrite lands. Until then `paper1_macros.py` stops unless P1_CLAIMS_WARN_ONLY=1. I ran it that way: macros.tex is byte-identical to the previous run.
- `verify_theory.py`: 191/191.
- **Did Follow-up 2 move a headline? No.** The sec_it fix moved central G\* from 32.54 to 32.53 (still `\GstarCenOne` 32.5) and `\CfullHigh` from 7.3 to 7.2. Nothing else changed: the table caption, width, label and symbol edits and the α class are text or labels only.
- Note: the `\lpScreenBelowAll` CLAIMS entry still exists and still passes (`\lpXdagMin` 3.3 > 3). It concerns a withdrawn-weight macro, so it should go once the editor removes the text that uses it.

## Follow-up 4 (final audit)
**M3 (pass-through).**
- New row in Table S2 (`sections/tables/tab_passthrough_recon.tex`): "Rate on all unit-cost savings, saving of a typical $1–5 billion firm". It uses the typical firm's netted median intercept, 18.5, so its unit cost is 75% of price. G\* is **37.8 / 41.5** at φ = 0.5 / 0.7, against the auditor's ≈37.9 / 41.7. The small gap is rounding of the typical firm's intercept; the computation is the same.
- New macros:
  - `\PtCzeroOne` 60.2: the anchor's own non-fee unit cost, % of today's price (`\PtCzero` 60 already existed).
  - `\PtKfull` 15.2: the unit cost at the full-cost structure.
  - `\PtSaving` 45.0: the anchor's saving.
  - `\PtCzeroTyp` 75 and `\PtSavingTyp` 59.7: the same two quantities for the typical firm.
  - `\PtGstarTypHalf` 37.8, `\PtGstarTypSeven` 41.5.
  - `\PtPriceCutTypHalf` 30, `\PtPriceCutTypSeven` 42.
  - `\PtGstarTypGapHalf` 1.7, `\PtGstarTypGapSeven` 3.2: the rise over the central reading, which supports the auditor's "about 2 to 4 points".
- JSON: `r2.pass_through.typical`, `r2.pass_through.unit_costs`.

**m6 (legibility).**
- **Table 2** (`paper1/tab_estimands_v3.tex`, from `paper1_macros.py`): seven columns (Statistic, Basis, E1, E2, M = 4, M = 8, Holds in all four) at `\footnotesize`, no `\resizebox`.
  - Basis "FCF after SBC" is abbreviated "cash", defined in the notes.
  - The table no longer fits one page at that size, so it is **two floats numbered Table 2**: Panel A through the gap rows, then "continued" from the anchor rows through Panels B and C and the notes. The second float decrements the table counter, so the label `tab:estimands_v3` and every reference still point to Table 2.
  - The two dropped columns (E1 − E2, exclusion only 25%) are in a new supplement table, `tab:estimands_v3_more` ("Headline statistics …, continued: E1 − E2 and the exclusion-only sample"). It is appended to `paper1/tab_contrasts_v3.tex`, so it appears without any change to supplement.tex.
  - Switch: `P1_TABLE2_COMPACT=1` writes a single resized seven-column float instead.
- **Table S6** (`tab:contrasts_v3`, 14 columns at about 5.5 pt) is split into two `\footnotesize` tables without `\resizebox`:
  - `tab:contrasts_v3`: estimates, 90% intervals, unadjusted p;
  - new `tab:contrasts_v3b`: 95% intervals, Holm and Romano–Wolf.
- **Table S4** (`tab:robust`, `paper1/tab_robust_v3.tex`): `\footnotesize`, no `\resizebox`, wrapping label column.
- Supplement numbering now runs S6 contrasts, S7 contrasts (continued), S8 Table 2 (continued); later tables shift by two.
- **Page counts:** main paper **82** pages, supplement **57**. The build is clean: no overfull boxes, no float too large, no undefined references.
  - With the compact Table 2 the main paper is also 82, so the two pages over the 80-page limit do not come from Table 2's new format alone. The editor's parallel text pass contributes.
  - The supplement grew by about four pages: S6 split, S8 added, S4 unscaled.
  - **The 80-page limit is currently not met.**

**m13.** New Table 2 row: "Anchor: median Π, maintenance-netted (central)", cash basis. Values: E1 +12.4 [+0.3, +25.7], E2 +12.2 [+0.5, +24.7], M = 4 +13.2 [+3.5, +26.1], M = 8 +13.2 [+3.7, +26.5]. D-3 column: yes/yes (positive and interval above zero in all four views).
- Source: `code/estimate_v3.py` anchor block, new statistics `anchor_p95_{maint_base, m0_net_med, Pi_net_q1, Pi_net_med, Pi_net_q3}` (and the p975 versions). The maintenance base is recomputed in each draw.
- estimate_v3 was rerun in full (999 replications, scratch copy). The comparison confirmed only these 10 statistics were added; no other statistic, family or table changed.
- `notes/calibration_anchor_v3.json` gains the same five bootstrap entries. The E1 netted intercept interval, [24.1, 34.7], matches the reconstruction in calibrate_horizons B5.

**m15.** `\GdecMnt` 0.50, `\GdecSec` 1.28, `\GdecErr` 3.17 and `\GdecAnc` 0.16 are now printed to two decimals. New `\GdecFullTwo` 5.11, so the parts sum visibly: 0.50 + 1.28 + 3.17 + 0.16 = 5.11. `\GdecFull` (5.1) is unchanged.

**Checks:** CLAIMS 63/63 in strict mode; the levers text check now passes on the editor's rewritten prose. verify_theory 191/191. `NO_COPY=1 build_paper1.sh` clean, 82 + 57 pages.

## Follow-up 5 (pipeline regressions)
Written 2 Nov 2026 (UTC−8) by the pipeline-regression agent, which took over from an agent stopped by the workspace restart
of about 17:26 and was itself interrupted by the restart of about 18:18; this section is kept current as the work goes.
Goal: `bash code/regenerate_all.sh`, run on a scratch copy, reproduces the committed outputs. Rule: the committed output
wins; no committed output was edited to match a script, and no check was edited.

**Status: complete.** Script changes reviewed and verified; params.yaml reproduced byte for byte; end-to-end run complete
(every stage through latex_p1 exits 0; latex_p2 stops as documented, no Paper 2 main file); four differences, none of
them a result (below), one of which needs a lead decision; all live-repo checks pass.

### Code changes (all made by the previous agent between 16:52 and 16:56; reviewed, verified and kept unchanged)
1. **`code/data_part2/08_params.py`: round-2 hand edits of `data/tasks/params.yaml` ported.** The yaml says it is built by
   this script, but the round-2 edits of 2 Nov (notes/r2_propagation.md items 1, 2, 4, 5; this file B1, B2, B9, C3) were
   made in the yaml, so a rerun regressed it (notes/r2_exclusion.md section 6, item 1). Ported, in the script's own
   structures (no value is read back from the committed yaml):
   - B9 varpi (`project_outcomes ... transformation_attempt_creates_value_varpi`): unit and note;
   - C3 `compliance.sox_program_cost_kpmg_2025_reference`: comment, new `by_revenue_size` sub-block (under $5B $1.5M,
     $5–25B $2.7M, $25B+ $4.7M; archived KPMG URL, flag, `used_in`, read 2026-11-02);
   - C3 `sox404_...` reference note (superseded), `audit_fee_per_musd_revenue_reference` note (low bound) and the new
     `audit_fee_accelerated_filer_reference` block ($1,492,375; large accelerated $5,327,646; grounding a);
   - C3 `part1_ceiling.a_min_accountability_floor` source text (value 0.03 and band [0.005, 0.046] unchanged);
   - B2 `c_c_compute_share.path.sources` ("kappa < 1, so c_c <= s_L"), `high_compute_case` (`feasible_at_full_automation:
     true`, `value_test_cap: 0.6` = `CC_PATH['s_L']`, note);
   - B1/A9/IO2-2 pass-through: anchor `identical_inference` no longer emitted; unit and note rewritten.
   Hand-set line breaks are reproduced by a `Hand(...)` string type and a `yaml.SafeDumper` subclass (`_Dumper`) that writes
   such strings line by line; every other string is emitted exactly as `yaml.safe_dump(..., width=120)` did. New constant
   `R2_READ = '2026-11-02'` (read date of the round-2 sources). Module docstring updated.
2. **`code/data_part2/10_validate.py`:** `sys.path` pointed at the live folder (`/home/claude/paper/code/data_part2`); it now
   uses the script's own folder, as 08_params.py does, so a scratch copy validates with its own `common.py`. No check changed.
3. **`code/estimate_organic.py`: anchor regression check made sample-aware.** The script computes the E1 anchor on its own
   sample, v2 (458 firm-years in 2023–25, 15 in the anchor) and compared it with `notes/calibration_results.json`, which
   since revision v2 (D-3) holds the v3 anchor (447 and 13), so it stopped although neither number is wrong. New function
   `anchor_reference()` picks a record on the same sample, never across samples:
   (1) `calibration_results.json` (`anchor_E1`, else `anchor`) if its `n_sample_2023_25` equals the script's;
   (2) else `notes/empirics_v2_exact.json` `anchor.blocks.E1`, the v2 calibration anchor written by `estimate_v3.py` with
   `V3_PANEL=v2`, an independent implementation of the same rule; it must state panel v2 and the same 2023–25 size
   (asserted, so a changed sample fails instead of skipping); (3) neither (first run): no check, `passed: null`, and stage
   calibrate reruns the script. Both checks use it: section 6 (10 fields, rtol 1e-9) and the anchor-block check (20 fields,
   rtol 1e-12). Why this choice: it keeps the check meaningful (two implementations must agree on every field, firm list
   included) instead of loosening it, and it does not compare quantities from different samples. The anchor file's
   `regression_check` keeps its committed label ("notes/calibration_results.json anchor") so that
   `notes/calibration_anchor_E2.json` stays byte-identical; the record actually used is printed in the log. Before the
   run, all 20 fields of the committed anchor file's E1 block were confirmed equal to `empirics_v2_exact.json`.
4. **`code/regenerate_all.sh`:** header comments only (how estimate_organic's check picks its reference; paper1_macros.py
   reads `notes/calibration_anchor_v3.json`, not the E2 file). No stage, flag or order changed.

### params.yaml
`PAPER_ROOT=<scratch> python3 -I code/data_part2/08_params.py` on a scratch tree (data/tasks copied, the rest symlinked):
`cmp` with the committed `data/tasks/params.yaml`: **identical** (sha256 144562867d5ca5e8…); the rest of data/tasks also
identical. 277 parameter blocks, 113 assumed; grounding a 94, b 43, c 17, d 112, ref 14.

### End-to-end run (scratch copy of the repository without dist/, __pycache__, .git; a second untouched copy as baseline)
`bash code/regenerate_all.sh --keep-going` with `NO_COPY=1`, in chunks (`--to empirics_v3`, then `--from backtest`, then,
after the restart, `--from verify_theory`). Stages 01–10 all exit 0, timings: engine_defaults 2 s, params 2 s,
invoice_chain 13 s, verify_part2 70 s (accounting 48/48, acquirer 82/82, regimes 85/85, core 158/158, ext 143/143, labor
43/43, product 94/94, competition 44/44), panel 9 s, empirics 469 s (estimate_organic 315 s; "calibration anchor
reproduced (section 6)" and "E1 anchor regression check passed on 20 fields", both against empirics_v2_exact.json;
"reproduction checks passed: 25"), empirics_v3 1,213 s (v2 409 s, v3 804 s), backtest 143 s, calibrate 6 s (the anchor
file says passed: true, so the recheck step did not run), verify_theory 82 s (191/191), paper1_macros 4 s (1,577 macros,
CLAIMS strict), playbook 168 s, verify_playbook 4 s (40/40), engine_tests 130 s (191 passed), latex_p1 6 s
(`build_paper1.sh` with NO_COPY=1: clean, 82 + 57 pages), latex_p2 exit 3 ("no Paper 2 main file", expected).

The run rewrote 96 committed files (by mtime): data/tasks/params.yaml and _build/validation.json, engine/TRACEABILITY.md,
data/examples/invoice_chain.json, the seven panel files and their logs, data/playbook/*.csv (5), notes/*.json and the
generated notes (21), paper1/macros.tex, claim_checks.txt, abstract_plain.txt and the five paper1/tab_*_v3.tex, 22
part2/tables files, 26 sections/tables files, sections/appendix_proofs.tex (tab:fullcost block, calibrate_horizons.py) and
three figures. Not regenerated by any stage, so not tested here: engine golden files and test fixtures,
engine/examples/synthetic_run/report, and the other data_part2 outputs (01–07, 09, 11, 12 are not pipeline stages).

**Regenerated vs committed (baseline: an untouched copy taken with the run copy; the live repo had not changed since):**
1. `part2/tables/labor_macros.tex`: first line only, "(version 2026-10-29b)" → "(version 2026-10-29c)". The committed file
   (29 Oct 11:39) predates the version bump of the committed `data/examples/invoice_chain.json` (now 2026-10-29c, itself
   reproduced exactly); the nine macro values are identical. **Not fixed:** reproducing it would mean hardcoding a false
   input version in `code/make_labor_macros.py`. Lead decision: regenerate the committed file (one comment line moves).
2. `notes/playbook_results.json`: 14 lines, all run metadata: `generated` "2026-11-02 16:14" → "2026-11-02 18:23",
   top-level `seconds` 251.1 → 167.4, and the 12 per-configuration `seconds`. Every result is identical.
3. `notes/verify_theory_output.txt`: one line, the location in a NumPy RuntimeWarning ("…/code/verify_theory.py:2715:
   RuntimeWarning: overflow encountered in exp") names the scratch copy's path instead of /home/claude/paper. Location
   artifact, not a script change; see the live check below.
4. `figures/fig_empirical_frontier.pdf`, `fig_scale.pdf`, `fig_scores_time.pdf`: `/CreationDate` only (matplotlib stamps
   the wall clock). None of the three is included by Paper 1 or Paper 2.

Everything else is byte-identical, including params.yaml, invoice_chain.json, the panels, notes/empirics_{results,revised,
organic,v2_exact,v3}.json, gap_decomposition, paper_stats, panel_v3_build, calibration_anchor_{E2,v3}.json,
bootstrap_draws_v3.npz, frontier_slope_v3, inference_v3.md, sample_audit.md, estimand_notes.md, backtest_results.json,
calibration_results.json, amin_r2.json, paper1/macros.tex and the Paper 1 tables, all part2/tables files other than
labor_macros.tex, data/playbook/*.csv, engine/TRACEABILITY.md and sections/appendix_proofs.tex. No file was added or removed.

### Checks in the live repository (2 Nov, about 18:30 UTC−8; no check edited)
| Check | Result |
|---|---|
| `python3 code/paper1_macros.py` (CLAIMS strict, P1_CLAIMS_WARN_ONLY unset) | exit 0; **64/64** claims ok; 1,577 macros; abstract 1,912 of 1,920 characters |
| `python3 code/verify_theory.py` | **191/191**; its combined output is byte-identical to the committed `notes/verify_theory_output.txt` (so difference 3 above is only the path) |
| `verify_part2_accounting` / `acquirer` / `regimes` / `core` / `ext` | **48/48**, **82/82**, **85/85**, **158/158**, **143/143** |
| `verify_part2_labor` / `product` / `competition` / `playbook` | **43/43**, **94/94**, **44/44**, **40/40** |
| `python3 code/data_part2/10_validate.py` | all contract checks passed |
| `cd engine && python3 -m pytest -q` | **191 passed** (132 s) |

The checks rewrite generated files (paper1/macros.tex and tables, notes/amin_r2.json, sections/tables/tab_amin_pcc.tex and
acquired_macros.tex, part2/tables/*_macros.tex, data/tasks/_build/validation.json). A sha256 manifest of the repository
before and after shows no content change other than this notes file.

### Open (for the lead agent)
- `part2/tables/labor_macros.tex`: regenerate the committed file with `python3 code/make_labor_macros.py` (header line
  29b → 29c, values unchanged), or accept the stale header; the script was deliberately not made to print 29b.
- The run-metadata fields of `notes/playbook_results.json` (`generated`, `seconds`) and the PDF `/CreationDate` of the three
  figures can never reproduce byte for byte. Making them deterministic (for example a fixed `SOURCE_DATE_EPOCH` and dropping
  the timings) would itself change the committed files, so it was not done.
- `regenerate_all.sh` cannot run end to end without stopping at latex_p2 until Paper 2 has a main file (documented).
- Scratch copies (the run copy, its baseline, the build folders and the previous agent's `runA`) were deleted.

## Follow-up 6 (lead agent, 2 Nov, after the exclusion)
- `code/paper1_macros.py`: new macros `\AncPiNetEone`, `\AncPiNetEtwo`, `\AncPiNetImpFour`, `\AncPiNetImpEight` (with Lo and Hi) and `\AncPiNetCount`, which hold the netted anchor surplus (`anchor_p95_Pi_net_med`), for the FA-m13 sentence in Section 5.8. New CLAIMS entry: the netted median surplus is above zero in all four views, and its E1 lower end is under 1 point. Strict CLAIMS now 64/64.
- Table 2: a one-float `\scriptsize` version was tried to save a page and then removed. The float was 283 pt taller than the page, which the build did not report. The two-float `\footnotesize` version (Follow-up 4) is the default again, and the generated file is byte-identical to it.
- `code/build_paper1.sh`: a "Float too large" warning in either log now blocks copying the PDFs, like an undefined reference.
- `part2/tables/labor_macros.tex`: regenerated with `code/make_labor_macros.py` so its header records the current `invoice_chain.json` version, 2026-10-29c instead of 29b (Follow-up 5, item 1). The nine macro values are unchanged.
- Build: main paper 82 pages, supplement 57, clean.
