# C: Finance, accounting, tax and acquisition measurement — preserved first specialist report

Review date: 2 November 2026 (America/Los_Angeles). Reviewed frozen main SHA-256 bd87f45fed9c45587eec3d41b3b6dc3b08bbb73ef794773fe8fbbb74a5c6f9cf and supplement acf9d62bb96961a45400f2e52013cb4da79ed0d34d8cf0574ec7553226de02c2. PDF page index here is 1-based and equals the printed page on these cited pages. Model: the inherited agent environment identifies this as GPT-6-based Codex, but exposes no precise serving model identifier to this specialist. This is a separate agent context with the same underlying model family, tools, host, frozen evidence and shared filesystem as the other specialists. It is not independent human or independent-model-family evidence.

## Evidence and blinding boundary

No other specialist report or externally authored referee critique was opened. A broad initial search of main_all.txt unintentionally displayed snippets from main Appendix A (including statements about earlier panels and changes); the specialist did not use these as arguments or instructions and did not open the full prior-critique record. This is partial exposure and precludes a claim of fully blind review. Main pp37 and 47 themselves necessarily disclose earlier review-driven sample changes; their present measurement rules were assessed on their merits. Supplement S7 was not opened.

Targeted full text: main pp5,12–18,24–28,35–39,47–54,57–62,64–68; supplement pp1–3,6,8–10,18–20,24–28,36–37. Complete relevant proofs: Lemma S1; Remark 2; Remark 3; Proposition 8; related Remark S1 and S11. Page images actually inspected: main 13,27,28,35,48,50,54 and supplement 3,20. Not an all-pages finance reread; primary-source retrieval inspected relevant financial-statement/note sections rather than all prospectus pages. Neither author code nor raw panel was available to this specialist; the script below is independently written. The root was still resolving repository availability at this report's freeze.

## Strongest defensible finance contribution

For a firm whose capital stock is k times revenue, with an explicit timing convention and growth purchased through expensed spend, the cash-score growth weight is X−k. This is a useful explanation of why a cash Rule of 40 may penalize value-creating growth. The economic-margin and ROIC transformations in Remark 3 are correct algebra under the stated capital definition, and the paper appropriately says they are identities rather than new valuation theory. They do not identify empirical invested capital or justify applying one fixed k to a lumpy, depreciating or lease-financed firm.

The paper correctly distinguishes annual simple growth from continuous rates in Table 3, unlevered from after-interest scores, and valuation from screening weights. It explicitly warns that acquisition-life brackets, organic company measures, missing older acquisition vintages and fixed-price automation scenarios limit interpretation. The acquisition case is a valuable worked measurement example, not a general demonstration that acquirers destroy value.

## Finding C1 — Tax deductions' PV is not a period cash tax shield

**Locator.** Main Remark 2, pp27–28, especially the after-tax FCF formula following (27); supplement proof pp19–20. Corollary 4 and capital/tax scenario extensions inherit it.

**Classification.** Demonstrated cash-timing error in the asserted general interpretation; correct as a present-value equivalent. Not a refutation of the untaxed static theorems.

**Evidence.** Let investment I be paid now, fully deductible one year later, with full loss offset and tax rate τ. Its actual capital cash flows are −I now and +τI next year. Discounting at annual r yields −(1−τ/(1+r))I. Thus ψ=1/(1+r) correctly gives the capital outlay's PV. Booking −(1−τψ)I as today's *cash* outlay gives the same PV but a different period margin. For I=1, τ=.2, r=.1, actual date-0 cash is −1, future tax cash +.2, and PV-equivalent date-0 cost −.8181818. Linear full-loss-offset taxation does not move the deduction date.

For a history of capital vintages, actual cash deductions at t are D_t=Σ_a w_a I_{t−a}. If investment/revenue grows at simple g and I_t/S_t=kg under the manuscript's lead-installation convention, then D_t/S_t=kg Σ_a w_a(1+g)^(−a), not kg Σ_a w_a(1+r)^(−a). Under exactly (27)'s half-year 15-year schedule, at g=.30,k=1.5,τ=.18,r=.10, the cash-schedule factor is .2505629 versus ψ(r)=.5324256, raising the modeled cash score by 2.2831 points. At g=.15 the gap is .4591 points, and at g=.05 it reverses sign (−.2387 points). Startup deductions depend additionally on initial vintages. No randomness or estimation enters these examples.

**Strongest defense.** The text explicitly defines ψ as a PV and the proof explicitly calls ψτkg a PV tax shield. This is a standard and useful investment-valuation reduction; the substitution preserves present values when each vintage's future tax shields are assigned to the investment date. Full expensing (ψ=1) and genuinely nondeductible investment (ψ=0) eliminate the timing mismatch.

**Disposition.** Survives but narrowed: the problem is calling the PV-equivalent flow a period FCF margin, then carrying all score conclusions across as if cash timing were preserved. It does not alter the k=0 headline automation threshold, nor invalidate the ψ=0 table arithmetic. It matters to delayed-deduction, positive-k score extensions and period-by-period empirical comparison.

**Smallest repair / acceptance test.** Label the formula a tax-PV-equivalent score and keep it apart from reported cash scores; alternatively retain a tax-basis/vintage state and compute actual deductions. Demonstrate equality of total discounted cash value while explicitly reporting the period-margin differences for startup and balanced-growth histories. Identify cases in which the period formulas coincide.

## Finding C2 — The acquisition net-weight identity needs a separate finite-year bridge

**Locator.** Main Definition 5 and Proposition 8(a)–(b), p48; interpretation pp49–50,52; supplement S4 proof p26.

**Classification.** Ambiguity / missing measurement condition. The instantaneous theorem is not refuted. The annual numerical bridge as currently worded is inconsistent without redefining its variables.

**Evidence.** Definition 5 initially makes acquired growth a current-revenue-normalized run-rate flow, for which C/S=k_acq g_acq is coherent in continuous time. It then assigns g_acq=ln(1+S_ac/S_cn) to a measured year and also describes the simple annual component S_ac/S_prior. Neither is generally the same current-normalized acquired revenue flow.

Concrete annual example: S_prior=100, S_cn=100, S_ac=100, S_current=200 and cash consideration C=300. With price per dollar of recognized acquired revenue k_acq=3, actual acquisition cash margin charge C/S_current=1.5. Using the simple acquired growth component 1 gives k_acq g_acq=3; using its log component ln2 gives 2.07944. The correct simple annual cash charge is k_acq g_acq/(1+g_total)=1.5. If the price multiple instead uses acquired *run-rate* revenue, another realization fraction/close-date bridge is required.

**Strongest defense.** Proposition 8's algebra is exact for the instantaneous definition and its independently variable acquisition flow. The text acknowledges partial-year revenue recognition and calls fully charged year-of-purchase scores bounds. Table 3 deducts measured C/S directly; its arithmetic is not using the mistaken annual substitution.

**Disposition.** Narrowed to a measurement-definition repair; do not call Proposition 8 false. The annual interpretation “every acquisition above one times revenue lowers a Rule-of-40 score” is not universal with a prior-year-normalized growth numerator and a current-revenue-normalized margin. Under the corrected annual bridge the local coefficient is X−k_acq/(1+g_total), if holding the other annual quantities as defined; if total growth changes with the acquisition, the entire denominator must be differentiated. The instantaneous X−k_acq rule stays valid on its own domain.

**Smallest repair / acceptance test.** Use distinct symbols for instantaneous purchased revenue/run rate, annual recognized acquired revenue, log decomposition and simple annual decomposition. Derive C/S from actual annual consideration and close dates, then state which annual decision comparison, if any, follows. Test the example above, a late-year acquisition, and one with organic decline. Describe the 123-point reported-minus-company-organic gap as that gap; without a business-level bridge, company organic growth need not equal Definition 5 organic growth. The present text already discloses this definitional difference, so this is an overexact attribution, not an allegation of manipulated figures.

## Finding C3 — Cash payback alone does not determine a short-horizon owner's decision

**Locator.** Main p5 and Section 7.3 p61: negative cumulative program cash at 3/5 years, followed by “would therefore not fund”; also p66 interpretation.

**Classification.** Unsupported investment interpretation / missing terminal-value assumption.

**Evidence.** A holder selling at H maximizes cash received through H plus sale value: NPV_H=∫_0^H e^(−rt)ΔFCF_t dt + e^(−rH)ΔV_H. The manuscript's cash-payback statistic addresses only the first term. Example: pay 1 now; receive a permanent .2 annual flow beginning t=6; r=.10. A five-year holder has cash PV through exit −1, but a sale at year 5 capitalizing the residual flow has terminal value 1.8096748 and total NPV +.0976233. This equals infinite-horizon NPV. Thus the implication is false for ordinary ownership horizons with recoverable continuing value.

**Strongest defense.** An owner may impose a strict realized-cash payback mandate, lack access to buyers who capitalize unfinished work, be unable to sell, or receive no terminal credit. Section S2.11 discusses admission by “rate and horizon,” which can be read as such a mandate, but ownership/holding horizon alone does not imply it.

**Disposition.** Survives as a practical-recommendation error, not a challenge to the 7.5/8.5-year cash payback arithmetic. Those paybacks and positive program NPV can coexist.

**Smallest repair / acceptance test.** Replace “would not fund” with “would fail a five-year cash-payback requirement absent terminal-value recovery.” Report H-year value with a continuation/exit term under one stated capitalization rule, and show the terminal-value haircut at which rejection follows. The independent example is illustrative, not a re-estimate of the manuscript program.

## Case verification and finite corrections

Independently recomputed from [Bending Spoons F-1, 8 June 2026, F-32/F-35](https://www.sec.gov/Archives/edgar/data/2004711/000110465926071170/tm2613674-7_f1.htm): 2025 GAAP score 115.9481, after interest expense 105.0326; OCF score 116.9240; expense-addback cash score at 24% tax 125.2198. Acquisition-charge scenarios reconstruct 92.70–101.08 (annuity/end capital), 104.45–111.36 (annuity/time-weighted), 87.23–95.25 (user cost/end) and 100.92–107.99 (user cost/time-weighted). Differences below .1 point reflect timing/day conventions, not substantive errors. This independently supports the manuscript's 87–114 bracket on its stated basis.

The [final prospectus, filed 1 July 2026](https://www.sec.gov/Archives/edgar/data/2004711/000110465926079884/tm2613674-14_424b4.htm), F-35, reports 2025 equity compensation 55,523, PPE cash 501, and interest paid 130,881 versus expense 142,601 (USD thousands). With no material development capitalization reported (F-36/F-53), deducting PPE and SBC lowers that cash score 4.2884 points; replacing expense with cash interest at 24% lowers it another .6818. The pre-interest, after-PPE/SBC uncharged score becomes 120.2496; its after-interest counterpart 112.6356. This is a checkable comparable-basis extension. Purchased intangible cash and all acquisition capital must be assigned once. In particular the 2024 intangible payment requires classification before treating all such payments as maintenance capex or acquisition capital.

**Author defense and disposition.** Main p51 and Table 3 explicitly disclose that SBC and annual capex are absent from the author's *extract* and that case scores differ from the panel. This is not a false assertion that the filing lacks the fields. It is an unfinished reconciliation now resolvable from the primary filing. Require the revised case to include the same PPE/capitalized-software/SBC basis as the recommended panel score, and use actual cash interest as primary with tax-shield sensitivity. Do not treat the whole 4–5-point correction as an error in a clearly labeled pre-SBC OCF number.

The [Q2 2026 release](https://www.sec.gov/Archives/edgar/data/2004711/000200471126000011/bsp_ex99-1.htm), operating results and footnote 4, supports growth primarily driven by acquisitions and a company-defined organic growth rate of 3%. The [quarterly financial statements](https://www.sec.gov/Archives/edgar/data/2004711/000200471126000011/bsp_ex99-2.htm), income statement pp3 and cash flows p7, support the Q2 score recomputation: 160.4627 before interest, 144.9874 after. These are quarterly-year-on-year scores; no annualization is inferred.

## Audit matrix (finance subset)

| Claim | Status | Scope / result |
|---|---|---|
| Assumption 4, Eq2 (p13); Lemma S1 (supp3,10) | Checked, conditional | Continuous-time/lead-installation identity correct; contemporary difference kg²/(1+g) correct. No defect alleged merely because convention differs from reported data. |
| Remark 3(a–d), p35; supp24–25 | Checked | Symbolic residuals exactly zero; capital definition and constant g<r required. Does not identify empirical capital or establish that a fixed screen maximizes value. |
| Tax ψ5=.796, ψ15=.532, Eq27 | Checked arithmetic | Exact reproduction of adopted half-year schedule. |
| Remark 2 cash-FCF substitution | Corrected interpretation needed | PV equivalent; delayed deduction requires vintages for cash margins. |
| Proposition 8(a–b) instantaneous algebra | Checked | Additivity/separability and unchanged incumbent technology assumed. |
| Proposition 8 annual bridge | Ambiguous | Current/prior/log/run-rate normalization must be separated. |
| Proposition 8(c), p49 | Checked | Avoid charging financing cost and all-capital charge twice. Actual cash interest differs from expense. |
| Proposition 8(d), NRR→Gi | Conditional | Mathematical weighted-base identity correct for matching annual cohort measure. Filed NRR is an average of quarterly ratios including estimated pre-acquisition data; life derived from it is a scenario, as authors say. |
| Acquisition annuity / user-cost bounds, Eq31 | Checked conditional | Lower relation requires current outlay ≥ annual charge; author explicitly states this. Not a universal lower bound after purchases cease. |
| Table 3 principal 2025 charges | Independently reproduced | Four conventions match within .1 point; not author-code execution. |
| 87–114 case score comparable to panel FCF after SBC | Untested as final number | Paper discloses different basis; available filings permit repair. |
| Five-year owner rejects program from cash payback | Unsupported implication | Add terminal-value condition. |
| WACC transport to acquirer | Scenario | Source rate verified; sector WACC is not an estimated issuer-specific financing rate. |

## Tax/source checks

[IRS Notice 2026-11, Interim Guidance on Additional First Year Depreciation Deduction under §168(k)](https://www.irs.gov/pub/irs-drop/n-26-11.pdf), sections 2.02 and 3, confirms restored 100% bonus treatment for qualifying property acquired and placed in service after 19 January 2025, with eligibility/election conditions. Full relevant section access, not a full tax-opinion review.

[Public Law 119-21 (4 July 2025)](https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf), §70302, 139 Stat190–193 (PDF pp120–123 1-based), confirms domestic development deduction, inclusion of software, foreign 15-year treatment and effective date. Primary official text read in relevant sections. A domestic-amortization election in new §174A(c) is another route to ψ<1; main's two “exceptions” are useful examples, not exhaustive legal advice. No material defect alleged from this omission.

[Damodaran, Cost of Equity and Capital (US), January 2026](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/wacc.html), Software (System & Application), gives 9.34% for 309 firms. The continuous conversion ln(1.0934)=.0892911 is correct. Source verifies a sector average, not Bending Spoons' discount rate, return hurdle or cost of its new debt.

## Artifacts, execution and remaining evidence

Independent artifacts are outputs/review_bundle/C/finance_diagnostics.py, finance_inputs.json, finance_results.json and execution.log. Script uses deterministic arithmetic, exact symbolic simplification (SymPy), analytic integration of vintage capital and no random data. Tolerances: symbolic zero checks exact; arithmetic identity assertion 1e−12; matching published rounded scores assessed at .1 point. No mesh solver or simulation was used. Package versions and platform captured in JSON. No panel statistics were reproduced.

Decisive revision evidence: explicit annual acquisition measurement bridge with close dates/run-rate-to-realization mapping; actual tax deduction schedules and starting vintages or a renamed PV-equivalent metric; primary-data cash/SBC/PPE reconciliation and documented intangible classification; acquisition capital beginning before 2023 or a clear truncated-vintage limitation; issuer-specific cash tax shield sensitivity; horizon NPV including exit value. The narrow finance errors leave the main static screening argument and k=0 fixed-price ceiling intact, but practical decision rules and positive-k cash extensions need repair.
