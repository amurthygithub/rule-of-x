# Round 3 macro contract (coding agent -> editor)

Status: complete for round 3 (2-3 Nov 2026); every macro listed is defined now (all checks pass and the build is clean). Names are final.
Format: `\Name` = value — meaning — source (generator; stored output). Percent macros print without the % sign.

## Changed printed numbers (old -> new)

| Macro | Old | New | Why | Where printed |
|---|---|---|---|---|
| `\CcLo` | 1 | 2 | GLM-M11 / GPT-22: low credible compute share per completed process (successful-run cost 1% at a 50% success rate) | intro.tex:13, horizons.tex:13, supp_model.tex:37 |
| `\GstarCcLo` | 28 | 29 | same (threshold at a 2% compute share, 29.2%) | abstract, intro, exec_summary, conclusion |
| `\GstarAccCcLo` | 23 | 24 | same, accountability-only threshold | horizons.tex:43 |

Text consequence (editor): supp_model.tex:37 says METR's runs "cost 0.4 to 1.1% of it, rounded to 1% ... this sets the
lower credible bound of \CcLo\%" — with `\CcLo` = 2 that sentence must say that successful runs cost `\CcLoRuns`\% and
that, at a `\CcSuccessRate`\% success rate, the cost per completed process is about `\CcLo`\%, the low end.
Old values stay available: `\CcLoRuns` = 1, `\GstarCcLoRuns` = 28, `\GstarAccCcLoRuns` = 23.

Not changed, but flagged (GPT-4): under the exact recurrence the fast case's NPV and PV ratio round differently from the
printed bound-based values (`\PayNpvFast` 212 vs exact `\PayNpvExactFast` 213; `\PayRatioFast` 6.9 vs exact
`\PayRatioExactFast` 7.0). The printed central numbers (payback 7.5, discounted 8.5, NPV 98, ratio 3.9, the 2042 and 2032
dates) do not move at their printed rounding (CLAIMS check). No printed number was changed for GPT-4.

## Macros in paper1/macros.tex (code/paper1_macros.py; calibrate_horizons.py block `r3` of notes/calibration_results.json)

### GPT-M1 frontier-slope multiplier (model.tex:277, supp_model.tex:18) (live)
- `\PsiMultLo` = 2.1 — exact multiplier (steepest frontier slope / |Psi slope|) at alpha = 0.45, E1 growth values, both bases — r3.ell_psi_cone
- `\PsiMultHi` = 4.0 — same at alpha = 0.25
- `\PsiSteepConeOpLo` / `\PsiSteepConeOpHi` = 0.45 / 0.86 — implied steepest slope, GAAP basis, alpha 0.45 / 0.25
- `\PsiSteepConeCashLo` / `\PsiSteepConeCashHi` = 0.33 / 0.64 — same, after SBC
- `\PsiSteepConeLo` / `\PsiSteepConeHi` = 0.33 / 0.86 — both bases
- `\PsiMultApproxLo` / `\PsiMultApproxHi` = 2.3 / 5.0 — the old approximation (beta+1)(beta+2)/6 at alpha 0.45 / 0.25 (the "2.3 to 5" now typed in the text)
- CLAIMS: steepest slope below one on both bases for every alpha in [0.25, 0.45]; exact multiplier below the approximation at every alpha.
- Unchanged and still unused: `\PsiSteepLo`/`\PsiSteepHi` (0.36/1.02, the least-squares-identity map) and `\PsiEllLo`/`\PsiEllHi`.

### GPT-M2 PV tax shield vs period cash (horizons.tex:37, :46) (live)
- `\KcapLossForCash` = 43 — ceiling loss at k = 1.5, G = 30%, development abroad, period cash on a steady growth path, tau = 0.18 — r3.psi_period_cash
- `\KcapLossForCashLo` / `\KcapLossForCashHi` = 43 / 43 — same over tau 0.21 / 0.15 (one decimal: `\KcapLossForCashLoOne` 42.6, `\KcapLossForCashHiOne` 43.3)
- `\PsiFifteenCashThirty` = 0.25 — psi_15 evaluated at g = 30% (the period-cash factor; `\PsiFifteen` = 0.53 stays the PV factor)
- `\KcapLossForLo` / `\KcapLossForHi` = 40 / 41 unchanged (PV-equivalent)
- CLAIMS: period-cash loss exceeds the PV loss at every tax rate.

### GPT-M4 exit value (horizons.tex:71, intro.tex:13, discussion.tex:9) (live)
- `\PayExitFiveCen` = 165 — value at year 5 of the program's later net benefits, % of a year's revenue (buyer at r = 9.34%) — r3.exit_value
- `\PayExitBreakCen` = 7.4 — share of that value a sale must recover for a five-year owner to fund the program
- `\PayExitFiveCenTen` = 150, `\PayExitBreakCenTen` = 8.3 — same at r = 10%
- `\PayExitFiveFast` = 332, `\PayExitBreakFast` = 0.0; `\PayExitFiveSlow` = 9, `\PayExitBreakSlow` = none (NPV < 0)
- `\PayNpvSlow` = $-$2 (existing) — slow-execution NPV, % of a year's revenue; `\PayNpvCen` = 98 (existing); `\PayNpvCenTen` = 86 (new, r = 10%)
- CLAIMS: fails the five-year cash test, positive value at year 5, break-even below one at 9.34% and 10%, slow NPV < 0.

### GPT-9 net 2036 score (abstract, exec_summary, intro, conclusion) (live)
- `\CenRSixNet` = 54 — central path 2036, durable score less the dip of transitions in flight (R_net) — central_path.path.net.2036.R_net
- `\CenROneNet` = 46 (2031), `\CenREightNet` = 42 (2028)
- CLAIMS: net below durable.

### GPT-4 completion dates (horizons.tex:69, :71, conclusion.tex:5) (live)
- `\PaceFastDone` = 2032, `\PayDoneCen` = 2042 (existing): dates at which the capped upper bound reaches the whole program
- `\PaceFastDoneExact` = 2032, `\PayDoneExactCen` = 2042, `\PayDoneExactFast` = 2032, `\PayDoneExactSlow` = 2087 — year in which the exact recurrence has embedded `\PayDoneShare`\% (99%) — r3.exact_recurrence
- `\PayEmbAtBoundCen` = 99.9, `\PayEmbAtBoundFast` = 99.9 — exact embedded share at the date the bound reaches one
- Exact-recurrence payback etc.: `\PayBackExactCen` 7.5, `\PayBackDiscExactCen` 8.5, `\PayNpvExactCen` 98, `\PayRatioExactCen` 3.9; fast 4.7 / 5.0 / 213 / 7.0; slow 24.7 / never / $-$2 / 0.9
- CLAIMS: 99% year equals the bound's year (central, fast); central payback, discounted payback, NPV and ratio unchanged at printed rounding.

### GLM-M5 PV ratio truncated at completion (horizons.tex:71) (live)
- `\PayRatioDoneCen` = 2.1 — PV of gains / PV of the dip counting gains only until 2042 (`\PayRatioCen` = 3.9 counts all) — r3.payback_to_completion

### GLM-F1 / GPT-2 shape of v'(s), worked example of S2.2 (supp_model.tex:9, model.tex:204, :243, horizons.tex:91) (live)
- `\VpOnePct` / `\VpTenPct` / `\VpFiftyPct` = 9.1 / 7.2 / 5.4 — v' at 1, 10, 50% of the cap (the numbers now typed) — r3.vprime_shape
- `\VsOnePct` / `\VsTenPct` / `\VsFiftyPct` = 9.4 / 8.1 / 6.5 — revenue multiples v/s at the same shares (typed now)
- `\VpMin` = 5.1 (two decimals `\VpMinTwo` 5.08) — minimum of v'; `\VpMinAt` = 80 — its location, % of the cap
- `\VpLimit` = 5.8 (`\VpLimitTwo` 5.83) — the never-spend multiple (m0 - kG)/(r - G), the limit at the cap
- `\VpSatLo` / `\VpSatHi` = 5.08 / 5.70 — retention gain per point near saturation (k = 0): minimum to 99.9% of the cap
- `\VpEighty` 5.08, `\VpNinety` 5.14, `\VpNinetyFive` 5.25, `\VpNinetyNine` 5.50, `\VpThreeNines` 5.70, `\VpFourNines` 5.78
- `\VpGainShare` = 56 — near-cap retention gain as % of the small-share gain (5.08/9.07); `\VpSigmaOnePct` = 9.2, `\VpSigmaNinetyFive` = 0.06 — optimal growth spend, % of revenue, at 1% and 95% of the cap
- CLAIMS: falls 1% -> 10% -> 50%; interior minimum at 70-90% of the cap; within 1% of the limit at 99.99%; v'(0.99) > v'(0.5); below its 1% value from 50% on; below v/s everywhere; near-cap gain more than half the small-share gain while spend falls below a tenth.
- verify_theory.py checks 15l-15p (on its own grid): see "New checks".

### GLM-F5 Holm counterfactual families (empirics.tex:15) (live)
- `\FamEighteenN` = 18, `\FamTwentyN` = 20
- 18 tests (family B + anchor + T(20%) both bases + T(0) after SBC): steepening `\HolmEighteenDiffNormal` / `Percentile` / `Basic` = 0.048 / 0.084 / 0.052; GAAP P95 decline `\HolmEighteenTopNormal` / `Percentile` / `Basic` = 0.072 / 0.084 / 0.260; anchor `\HolmEighteenAnchorNormal` / `Percentile` / `Basic` = 0.008 / 0.132 / 0.036
- 20 tests (the reviewer's): steepening `\HolmTwentyDiffNormal` / `Percentile` / `Basic` = 0.052 / 0.090 / 0.052; P95 `\HolmTwentyTop...` = 0.078 / 0.090 / 0.260; anchor `\HolmTwentyAnchor...` = 0.008 / 0.144 / 0.040
- CLAIMS: steepening below 10% under every type in both; below 5% only normal with 18; anchor above 10% under percentile in both.
- Existing (GLM-M1): `\HolmAnchorFifteenNormal` / `Percentile` / `Basic` = 0.006 / 0.096 / 0.030 (15 tests), `\FamBN` = 14, `\FamBNPlus` = 14.

### GPT-14 Romano-Wolf Monte Carlo error (empirics.tex:20) (live)
- `\HolmTopRWSe` = 0.009 (`\HolmTopRWSeTwo` = 0.01) — sqrt(p(1-p)/999) at p = `\HolmTopRW` (0.097); `\BootB` = 999
- `\HolmTopRWDist` = 0.3 — distance of 0.097 from 0.10 in standard errors
- CLAIMS: p below 0.10 but within one MC standard error of it.

### GLM-M3 after-tax k_a slack (horizons.tex:52) (live)
- `\KaSlack` = 0.84 — tau (1 - psi_15) k_a G at the Prop. 4 illustration (k_a = 2, G = 5%), points

### DS-57 (appendix_proofs.tex:31) (live)
- `\AminPhmTot` = 8.6 (= `\AminPhmTotFive`; `\AminPhmTotOne` = 1.7) — human miss rate on AI-missed items including the common mode 0.002; `\AminPhmFive` = 8.4 unchanged (apart from it)

### GPT-26 wave length (tab_param_sources.tex, execution pace row) (live)
- `\PaceTparCen` / `\PaceTparFast` / `\PaceTparSlow` = 0.17 / 0.08 / 0.42 years

### GPT-12 (data.tex:38)
- `\VUnverified` (existing) — the unflagged firm-years with growth of 100% or more and neither acquisition payments nor goodwill data (2)

### GPT-8 persistent bad state (supp_model.tex:29) (live; editor's request)
- `\PersistEscapeThree` = 0.5 (`\PersistEscapeThreeTwo` = 0.52) — annual escape probability with three AI layers when a provider's bad state lasts the whole period (p_ca = 0.005, layer miss 0.02, 24 opportunities), %
- `\PersistIidFloor` = 11.3 — the i.i.d. single-provider floor 1 - 0.995^24, % (same value as `\AminAiLim`)

## Acquired-growth macros (sections/tables/acquired_macros.tex, code/verify_part2_acquirer.py; inputs data/v3_inputs/bending_spoons_annual_2024_2025.json, read from the sec.gov copies in data/v3_inputs/raw/) (all live)

These are always written to acquired_macros.tex (they are in REQUIRED_P1), so the text can use them at once.

### GLM-F2 Table 3 annual organic rows (measurement_acquired.tex, Table tab:acquired-score) — cells to fill
Exact lines for the editor (2024 & 2025 columns; Q1 2026 stays --):
- `Organic growth (company measure, unaudited) & \acqOrgGTwentyFour & \acqOrgGTwentyFive & -- & \acqQTwoOrg\\`  (7% / 13%)
- `Organic, before interest: $g^{\rm org}+m_{op}$ & \acqROrgTwentyFour & \acqROrgTwentyFive & -- & \acqRQTwoOrgX\\`  (26.0 / 34.3)
- `Organic, after interest & \acqROrgIntTwentyFour & \acqROrgIntTwentyFive & -- & \acqRQTwoOrgInt\\`  (21.1 / 23.4)
- `Organic, before interest and reorganization & \acqROrgNoReorgTwentyFour & \acqROrgNoReorgTwentyFive & -- & \acqRQTwoOrgNoReorg\\`  (33.7 / 40.3)
- optional row: `Organic, after interest, before reorganization & \acqROrgIntNoReorgTwentyFour & \acqROrgIntNoReorgTwentyFive & -- & \acqRQTwoOrgIntNoReorg...` (28.8 / 29.4; the Q2 one-decimal macro does not exist yet, only the rounded `\acqRQTwoOrgIntNoReorgR` = 29 — ask if you want it)
- new after-SBC cash row: `Cash, after interest paid and SBC (panel basis): $g+$ FCF after SBC / revenue & \acqROcfSbcTwentyFour & \acqROcfSbcTwentyFive & -- & --\\`  (100.0 / 112.6)
Rounded for prose: `\acqROrgIntTwentyFiveR` = 23, `\acqROrgNoReorgTwentyFiveR` = 40 (the 2025 annual organic range "about 23 to 40", GLM-5).

### GLM-F2 the other disclosures
- `\acqSubsTwentyThree` / `\acqSubsTwentyFour` / `\acqSubsTwentyFive` = 95\% / 92\% / 93\% — subscription share of revenue (424B4 pp. 7, 108)
- `\acqSbcTwentyThree` / `\acqSbcTwentyFour` / `\acqSbcTwentyFive` = 3.8\% / 3.9\% / 4.3\% of revenue (`\acqSbcTwentyFiveTwo` = 4.25\%); `\acqSbcUsdTwentyFive` = \$55.5 million — equity compensation (F-35)
- `\acqROcfSbcOnlyTwentyFive` = 112.7 — cash score after interest paid less SBC only (without capex); the panel basis is `\acqROcfSbcTwentyFive` = 112.6
- `\acqAcqShareTwentyFour` = 81.7\% — acquisitions of businesses / net investing outflow, 2024; `\acqIntangShareTwentyFour` = 18.3\% — purchases of intangible assets (includes the Mosaic asset deal; GLM-6), `\acqIntangTwentyFour` = \$162.5 million
- `\acqAcqShareTwentyFiveTwo` = 99.97\% — same, 2025 (use this one; the one-decimal `\acqAcqShareTwentyFive` prints 100.0\%)
- `\acqCapexRevTwentyFour` / `\acqCapexRevTwentyFive` = 0.09\% / 0.04\% — purchases of property and equipment / revenue (so free cash flow is within 0.1 point of operating cash flow)
- `\acqOrgPage` = 80, `\acqPfPage` = 143 — 424B4 pages of the organic-growth passage and the pro forma revenue row (F-1: 79 and 142). NB the GLM log's "p. 142" for the pro forma is the F-1's page; the 424B4's is 143.
- DS-69: re-verified against the sec.gov 424B4 (check I3); `\acqPfRev`, `\acqPfRatio`, `\acqKEb`-`\acqKVim` unchanged.

### GPT-M3 annual units (measurement_acquired.tex:7, :26, :50)
- `\acqAnnFactor` = 0.51 — 1/(1 + g_2025): the average full charge per point of simple annual acquired growth is k^acq times this
- `\acqFullAnnEb` / `\acqFullAnnAol` / `\acqFullAnnVim` = $+$0.11 / $-$0.18 / $-$0.66 — net effect on the annual score at X = 1 per point of simple annual acquired growth, full-year recognition, 2025 growth (Eventbrite 1.73, AOL 2.30, Vimeo 3.23). DEVIATION FROM THE LOG: the GPT log's -0.64 uses k = 3.2 rounded; at the unrounded 3.23 it is -0.66.
- `\acqAnnPtsAnnLo` = 0.10 and `\acqUcPtsAnnHi` = 0.30 — the annual-unit versions of "0.19 to 0.59" (`\acqAnnPtsLo`, `\acqUcPtsHi`, per point of run-rate revenue)
- `\acqFullPtsLo` / `\acqFullPtsHi` = 0.7 / 2.2 unchanged (per point of run-rate revenue)

### GLM-M6 coupon variant on interest expense (measurement_acquired.tex:50)
- `\acqChCouponExpLo` / `\acqChCouponExpHi` = 86.7 / 113.7 — charged at the notes' coupon, interest expense added back (the basis of 87-114); `\acqChCouponLo`/`Hi` = 86.0 / 112.8 unchanged (interest paid)

### DS-65
- check E7 of verify_part2_acquirer.py relabelled (after interest, round-1 basis); notes/acquirer_notes.md section 4 updated (the engine's change-control lock re-accepted for that file, engine/CHANGELOG.md).

## GLM-M10 element list (appendix_data.tex S6): what the code actually uses (checked in code/build_panel_v2.py)
- `OperatingIncomeLoss` is used (build_panel_v2.py lines 131 and 147: the GAAP operating margin). The discontinued-operations
  elements (`IncomeLossFromDiscontinuedOperationsNetOfTax` and its `...AttributableToReportingEntity` variant) are used for
  `disc_flag` (lines 115-116, 155).
- `NetIncomeLoss`, `PropertyPlantAndEquipmentNet`, `DepreciationDepletionAndAmortization`, `DepreciationAndAmortization`,
  `FinanceLeasePrincipalPayments` and `SellingGeneralAndAdministrativeExpense` are among the 35 retrieved elements
  (fetch_companyfacts.py and the CON list of build_panel_v2.py) but no script uses them to build any variable. If S6 lists
  them, it should say "retrieved but not used", not give them a role (the GLM log's proposed wording assigns roles).

## Generated file the editor also edits
- `sections/appendix_proofs.tex`: code/calibrate_horizons.py rewrites only the block between `% BEGIN ROWS GENERATED` and
  `% END ROWS GENERATED` (Table tab:fullcost). For GPT-21 its row "Error rate with no review" now reads "(d) scenario value: an
  omission rate per source sentence plus a hallucination rate per output sentence (favorable) or per summary or answer
  (central, conservative), which have different denominators, from source-grounded summarization and retrieval-based legal
  research; ..." (was "(a, b) omission and hallucination rates of retrieval-grounded work"). Please do not edit inside the
  markers; your edits elsewhere in the file are preserved (the script reads the current file).
- `sections/tables/tab_param_sources.tex`: yours (I do not edit it). GPT-21's grade there is yours.

## Stress-test supplement (code/mc_report_tex.py; paper1/stress_macros.tex, input at the end of paper1/macros.tex) (all live)

Lines for the editor to place in the new supplement section (they compile now):
- table: `\input{sections/tables/tab_stress.tex}`  (label `tab:stress`; 18 rows; notes included)
- figure:
  ```
  \begin{figure}[t]\centering
  \includegraphics[width=\linewidth]{figures/fig_stress.pdf}
  \caption{...}\label{fig:stress}
  \end{figure}
  ```
  Left panel: the 2036 central score (maintenance-netted) over the `\StDraws` draws, with the paper's 90% anchor-sampling
  interval shaded, the central path and the 5th/95th percentiles of the draws (dashed). Right panel: the growth threshold
  G* at 2025 prices over the draws, compute share on its range (filled) and compute at 6% (outline), with the 30% line.

Macros (St prefix; percent without the % sign; "box" = every evaluated point: LHS draws, corners and the vertex search):
- `\StDraws` = 10{,}000, `\StCorners` = 2{,}050, `\StDims` = 51, `\StSeed` = 20261102; accountability sub-box `\StAminDraws` = 2{,}000, `\StAminCorners` = 32, `\StAminDims` = 5
- `\StClaimsRows` = 18, `\StClaimsHold` = 7 — rows of Table tab:stress and how many hold everywhere
- 2036 netted score: `\StNetSixPFive` / `\StNetSixPNinetyFive` = 40.7 / 67.1 (5th/95th percentile of draws, uniform laws); `\StNetSixMin` / `\StNetSixMax` = 27.4 / 95.3 (box); `\StNetSixCen` = 59; combined 90% band `\StNetSixBandLo` / `\StNetSixBandHi` = 40.4 / 67.2; `\StNetSixInPaper` = 28 (% of draws inside the paper's [54, 62])
- G* (2025 prices): `\StGstarMin` / `\StGstarMax` = 19.2 / 59.2 (box); with compute at 6% `\StGstarCcSixMin` / `\StGstarCcSixMax` = 24.0 / 45.1; draws 5-95% `\StGstarPFive` / `\StGstarPNinetyFive` = 28.1 / 44.9; lowest over the horizons `\StGstarHorMin` = 19.2; `\StGstarBelowThirty` = 12 (% of draws with G* at or below 30%)
- payback (undiscounted, years): central execution `\StPayCenMin` / `\StPayCenMax` = 4.81 / 9.36; full box `\StPayMin` / `\StPayMax` = 3.40 / 29.17; `\StPayCen` = 7.5
- PV ratio lowest: `\StRatioCenMin` = 2.57 (central execution), `\StRatioMin` = 0.50 (full box); NPV range `\StNpvMin` / `\StNpvMax` = $-$36 / 395 (% of a year's revenue)
- levers: `\StLeverMin` / `\StLeverMax` = 0 / 2 (positions at which the growth engine leads the G&A cut); `\StLeverOneShare` = 70.4 (% of draws at the stated 1)
- Sobol total indices: `\StSobolExec` = 0.61 and `\StSobolG` = 0.21 (2036 netted score: execution, market growth); `\StSobolCc` = 0.88 (compute share, for G*)
- realized share by 2036: `\StRealMin` / `\StRealMax` = 4.9 / 85.0 (%); expected completion `\StCompleteMin` / `\StCompleteMax` = 2032 / 2087
- accountability: `\StAiOnlyMin` = 11.3 (lowest annual miss probability of any all-AI single-provider design, %); floor where a design exists `\StFloorMin` / `\StFloorMax` = 0.26 / 0.99 (% of revenue, 5% threshold; at 1%: `\StFloorOneMin` / `\StFloorOneMax` = 0.26 / 1.01)
- Rule of 1000: `\StPullMin` / `\StPullMax` = 9.0 / 20.0; completed program plus G in 2036, highest `\StCompletedMax` = 102.2; highest path score `\StPathMax` = 95.3

- S9 requests (3 Nov): `\StReproChecks` = 82 (reproduction checks passed before sampling); `\StCumMaxCen` = $+$0.1 and `\StCumMax` = $+$11.7 (ST-4: largest cumulative or discounted effect at three and five years, points of revenue times years, under central execution and over the full box); `\StCapHalf` = 13 (`\StCapHalfOne` = 12.7; ST-5: change capacity, % of the program a year, above which the realized share by 2036 exceeds one half with the other inputs central). Placed in sections/supp_stress.tex by the coding agent at the coordinator's request (three phrases replaced; nothing else in the prose changed).

Table tab:stress rows (holds everywhere / central / lowest to highest): G* > 30% full box no / 32.5% / 19.2-59.2%; with compute 6% no / 32.5% / 24.0-45.1%; G* > 30% at every horizon no / 31.7% / 19.2-53.8%; pass-through raises every threshold yes / 0.0 / 0.0-9.5; no Rule of 100 on the central path yes / 58.7 / 27.4-95.3; completed program below 100 no / 81.0 / 41.5-102.2; under half realized by 2036 no / 40.7% / 4.9-85.0%; still running in 2036 no / 2042.3 / 2031.5-2087.4; path rises 2028-36 no / 4.7 / $-$5.2-21.4; netted between bounds yes / 3.8 / 0.3-6.9; crossing before payback yes / 3.48 / 0.52-16.07; no payback within five years no / 7.53 / 3.40-29.17 (central execution no / 4.81-9.36); gains above dip no / 3.87 / 0.50-85.25 (central execution yes / 2.57-9.79); Rule of 1000 not steady yes / 13.44 / 9.01-20.04; growth engine at 1 of 6 no / 1 / 0-2; no all-AI design yes / 11.3% / 11.3-45.3%.

Reproduction: `python3 code/mc_claims.py --n 10000 --workers 4 --out notes/mc` (code/REPLICATION_README.md); regenerate_all stage `stress_report` formats the committed output only.

## Editor notes and requests (editor-author agent; appended, not part of the coder's sections)

- The editor is editing `sections/tables/tab_param_sources.tex` (hand-written, not generated) for GPT-20, GPT-21 (grade a -> d
  and the construction of the 0.05 term), GPT-22/GLM-M11 (successful runs; 2% per completed task) and GPT-26 (new T_par row
  with `\PaceTpar*`). Please do not edit that file in parallel; tell me if you need a change in it.
- Request (GPT-8, supp_model.tex:29): `\PersistEscapeThree` = annual escape probability with three AI layers when a provider's
  bad state lasts the whole period, per-challenge marginal 0.005 (issue log: 0.5191%, print 0.5), and `\PersistIidFloor` = the
  i.i.d. floor 1 - 0.995^24 (11.3; may already exist as `\AminAiLim`).
- Request (GLM-6 note, if the acquired-growth macros do not already carry it): the 2024 purchase of intangible assets as a
  share of the net investing outflow (`\acqIntangShareTwentyFour`, 18.3).
- Request (stress test, decision 7; for S9 and the six conditional wordings). If you have not named these yet, these names would
  let me write the text now (values from notes/mc_results_2026-11-02/mc_claims_report.md; rename freely and tell me):
  - run: `\StressN` 10,000 draws; `\StressCorners` 2,050; `\StressDims` 51; `\StressChecks` 82
  - ST-1 G*: `\StressGstarCondLo`/`Hi` 24.0 / 45.1 (compute at 6%); `\StressGstarLo`/`Hi` 19.2 / 59.2 (compute free);
    `\StressGstarCondShare` 90 (% of draws above 30, uniform law)
  - ST-2 2036 bracket: `\StressRSixLo`/`Hi` 41 / 67 (5-95% of draws, netted); `\StressRSixBandLo`/`Hi` 40 / 67 (combined band);
    `\StressRSixInCi` 28 (% of draws inside [54, 62]); `\StressRSixMin`/`Max` 27 / 95 (box range, netted)
  - ST-3 payback: `\StressPayCenLo`/`Hi` 4.8 / 9.4 (central execution); `\StressPayLo`/`Hi` 3.4 / 29.2 (full box)
  - ST-4 cumulative/NPV at 3 and 5 years: `\StressCumCenMax` 0.1 (central execution, max of the four, point-years);
    `\StressCumMax` 11.7 (full box)
  - ST-5 realized share by 2036: `\StressRealLo`/`Hi` 4.9 / 85 (execution ranges); `\StressRealCapCut` 13 (change capacity, % of
    the program a year, above which more than half is realized, others central: 12.65)
  - ST-6 lever count: `\StressGEFirstLo`/`Hi` 0 / 2 (growth engine first, over the 90% bootstrap interval of b_M);
    `\StressGACutLo`/`Hi` 4 / 6 (G&A cut first); `\StressLeverShare` 63 (% of bootstrap draws of b_M giving the stated count)
  - also, if cheap: `\StressCompletedMax` 102 (P2b: target plus market growth in 2036, max over the box)
- Editor note: `paper1/p1_preamble.tex` now has `\IfFileExists{paper1/stress_macros.tex}{\input{paper1/stress_macros.tex}}{}`
  after the acquired-growth macros, so the file is read as soon as it exists. `sections/supp_stress.tex` (S9) carries
  temporary `\providecommand` fallbacks for the requested names, to be removed once the real macros are live.
  S9 inputs `sections/tables/tab_stress.tex` and `figures/fig_stress.pdf` if they exist (I write the figure environment and
  caption; please tell me what the figure shows, or give me its caption).
- Editor (stress test): I use your `\St*` names (thank you). Four quantities my text still needs, if you can add them to
  stress_macros.tex: `\StChecks` (82, reproduction checks before sampling, all passed); `\StCumCenMax` (B3.B.net: largest of
  cum3, cum5, NPV3, NPV5 under central execution, +0.1 point-years) and `\StCumMax` (B3.full.net, +11.7); `\StRealCapCut`
  (P3: change capacity, % of the program a year, above which more than half is realized by 2036 with the other inputs
  central: 12.65, print 13). Until they exist S9 carries `\providecommand` fallbacks for these four only. I removed my own
  duplicate `\input{paper1/stress_macros.tex}` from p1_preamble.tex (macros.tex already inputs it).
- Editor note (CLAIMS labels): the text no longer says the GAAP P95 decline is significant "under most procedures"; it says
  "under two of four procedures, and at the boundary under a third" (Romano-Wolf 0.097 with MC SE 0.009). The CLAIMS check
  itself still holds; only its label in paper1_macros.py quotes the old phrase, if you want to update it.
- Editor (withdrawn): the four requested macros (`\StChecks`, `\StCumCenMax`, `\StCumMax`, `\StRealCapCut`) are no longer
  needed; S9 now states those four points without numbers, and its temporary `\providecommand` fallbacks are removed. If you
  add them anyway, tell the lead and I (or the lead) can put the numbers back.
