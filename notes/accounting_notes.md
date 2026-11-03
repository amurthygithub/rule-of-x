# Accounting, controls and reported performance (spec 24.4): notes for the engine and the lead author

Files: `part2/theory_accounting.tex` (`\label{sec:accounting}`), `part2/proofs_accounting.tex` (`\label{app:proofs-accounting}`), `code/verify_part2_accounting.py` (44 checks, all pass, about 2 minutes), `part2/refs_accounting.bib`, `part2/tables/accounting_macros.tex` (generated; do not edit), `notes/ref_verification_accounting.md`.

Build: add `part2/refs_accounting` to `\bibliography{...}`; `\input{part2/theory_accounting.tex}` after the Part II theory sections and `\input{part2/proofs_accounting.tex}` in the appendix. The section inputs `part2/tables/accounting_macros.tex` itself. Test build (with Part I model and discussion, theory_core, theory_ext, all part2 bibs): no errors, no undefined references or citations from these files. One overfull box in the bibliography comes from the long SEC FAQ URL (`sec2007faq`); adding `\usepackage{xurl}` to `paper.tex` would fix it and the similar Svanberg entry. Length in the test build: pages 71 to 80 (about 9.5 pages including Table `tab:acct-map`), of which the scope and ITGC subsection `sec:acct-scope` (added 29 Oct at the coordinator's request) is about 1.8 pages; proofs about 2.5 pages.

## 1. Single source for the running example (coordinator request, 29 Oct)

- The script reads `data/examples/invoice_chain.json` (loader `load_invoice_example`). Keys are found at any depth, case-insensitive, under these spellings: W (W, W_cash, savings), F (or F_build + F_int), F_build (F_build, F_A_total, sum_F_A), F_int (F_int, F_integration, integration), I, CJ (C_J), Cpar (C_par), Cstr (C_str), Cbrk (C_brk), Cwo (C_wo), Tpar (T_par), T_A, S (revenue), r, Th (T_h), pis (varpi_p), bbar (b_bar), Tdet (T_det), Lroll (L_roll). A `{"value": x}` wrapper is accepted.
- **Status (29 Oct, later): the JSON exists (version 2026-10-29b) and the section now reads it.** No key falls back to legacy values. Changes made when it arrived:
  - The score-path examples use `score_path.T_par` = 0.5, the value of the core's own score-path example; the transition examples use `transition.T_par` = 0.25. Check 1e reproduces the core's score path in the JSON (cash and GAAP, years 1 to 4), and check 4f reproduces the core's risk-adjusted NPV (−$3.90 million) from the inputs, so the two scripts agree.
  - The alias list now prefers `varpi_p` over `varpi` (the JSON also has activity-level `varpi` values, which the loader had picked up first) and `bbar_p` over `b_bar`.
  - The ASU 2025-06 example now expenses the $186k of other one-time costs (`F_other`: redesign, legal review, evaluation data, change management, training, control redesign; training under 25-4, the rest by judgment) and treats a quarter of the $2.0 million integration budget as data conversion (illustrative). Capitalized share 0.67 of F.
  - The rebuilt example has negative savings net of run costs (W = −$213k), so later-year score changes are negative; the text says "changes by" with signed macros. The cutover example uses an illustrative delay cost of $500k a year (z* = 50%), since the invoice chain does not pay at the defaults.
  - The prior-law (2022–2024) tax example amortizes only software development (builds plus integration net of data conversion, $2.12 million), since Notice 2023-63 excludes data conversion and training.
  - Pins to the void legacy numbers are retired.
- The section does not input `part2/tables/invoice_macros.tex`, because every invoice number it quotes is a derived accounting quantity. It reads the inputs from the JSON and writes its own macros, so it stays consistent with the core's numbers. Two inputs are needed that the core may not export: **F_build (sum of F_A) and F_int (integration budget)**. If only F is exported, the split falls back to legacy values and a DEPENDENCY line names the missing keys.
- Non-invoice examples are illustrative constants with no other source: the program premium, ψ_T, the cutover parameters, the a_min design example, the ITGC unit costs and the timeliness example. The ITGC example takes T_up (1.22) and the invoice chain's integrations (N_int = 4) from the JSON.

## 2. Check of the engine defaults (coordinator request)

| Default (engine/src/autofrontier/defaults.yaml) | Value | Finding | Recommendation |
|---|---|---|---|
| T_A | 4.0 (3 to 5) | ASC 350-40 prescribes no life. The life reflects obsolescence, technology, competition and other economic factors (350-40-35-5, via PwC Viewpoint). Hosted implementation costs are amortized over the hosting term including reasonably certain renewals (35-13, 35-14). | Keep it as the economic amortization horizon. Add a separate **book life T_B** (default = T_A). For hosted builds, set T_B to the contract term plus reasonably certain renewals. The section uses T_B = T_A. |
| capitalized_share_F | 0.5 (0.3 to 0.7) | No empirical source exists. Under ASU 2025-06 (25-12A), costs incurred while significant development uncertainty exists are expensed, so for novel agentic builds the share can be near 0 until the function is proven. Data conversion and training are always expensed. The rebuilt example (40% of agent builds under uncertainty, a quarter of integration as data conversion, other one-time costs expensed) gives 0.67. The engine's `dc_share` comment still cites the old example's 0.5, and its rule (1 − u)(1 − dc) applies u to all build spending, including integration, which is not novel. | Keep 0.5 as an **assumed** central value, but widen the range to **[0.0, 0.7]**. Better: compute F^cap = (1 − u)F_build + (1 − dc)F_int, with F_other expensed, from inputs u (share of agent builds under uncertainty) and dc (data-conversion share of integration). Flag that the rule changes at the ASU 2025-06 adoption date. |
| capitalized_share_I | 0.5 (0.2 to 0.7), assumed | In the engine (plans.py), I is the **integration and readiness investment**, while in theory_core I is equipment capex (Σ v ΔK). Integration splits into data conversion (expensed, 350-40-25-5) and interface or conversion software (capitalizable, 30-1(d)). Equipment is 100% capitalized (PP&E). | Rename the engine's integration variable or document the clash. Set capitalized_share_I = 1 − (data-conversion share of integration); the range [0.2, 0.7] is reasonable but class d. Equipment capitalization share = 1. |
| psi | 0.787 ("5-year straight line; 174A statute not verified") | Verified at primary source. Since taxable years beginning after 31 Dec 2024, domestic R&E, which includes software development, is deducted when paid or incurred (26 U.S.C. §174A(a), (d)(3)), so ψ = 1. Foreign R&E is amortized over 15 years from the midpoint (§174(a)), so ψ_15 = 0.532 at r = 0.10. Qualified property acquired after 19 Jan 2025 gets the 100% allowance (Notice 2026-11). | ψ = 1 for domestic development and bonus-eligible property; ψ_15 for the foreign share. Replace the single ψ with a domestic/foreign split input. 0.787 matches only the 2022–2024 regime. |

**Engine error (plans.py, about line 509):** `aF = (1 - cap_F)(1 - tau) + cap_F (1 - psi tau)` ties tax deductibility to book capitalization. For tax, R&E is deducted (domestic) or amortized (foreign) regardless of book treatment, and a book-expensed foreign build is still amortized over 15 years for tax. The correct factor is `aF = 1 - tau * psi_tax(location)` on the R&E part of F, whatever cap_F is (Prop prop:acct-tax(d)). Book capitalization should affect only the GAAP path.

**Engine GAAP path (plans.py):**
- (i) amortF starts at tau0 (the transition start) and runs over T_A. Per ASC 350-40-35-6 it should start at go-live (ready for intended use), t_go ∈ [0, T_par], and run over the book life T_B.
- (ii) `wo = atP * Cwo` books the legacy write-off at cutover. Per ASC 360-10-35-47 it is depreciation over the shortened life from commitment to the cease-use date. A cutover lump is right only if an impairment is recognized. Annual totals agree when commitment and cutover fall in the same fiscal year.
- (iii) Severance is booked at cutover. Per ASC 712 (ongoing plan) it is booked when probable and estimable; per ASC 420 at the communication date, or ratably over required service beyond the minimum retention period.

## 3. Results and labels

| Label | Content |
|---|---|
| sec:acct-standards, tab:acct-map | standards statements (ASC 350-40 pre and post ASU 2025-06, ASU 2018-15, ASC 420/712/360/718/740; §174, §174A, Rev. Proc. 2025-28, Notice 2023-63, Notice 2026-11); cost-by-cost mapping |
| ass:acct-books, prop:acct-path | cash invariance; accrual identity eq:acct-accrual; first-year GAAP gap eq:acct-first (generalizes prop:tasks-scorepath(c)); later years; ASU 2025-06 bound |
| prop:acct-program, eq:acct-wedge | permanent GAAP-over-cash premium of a growing capitalization program |
| rem:acct-ebitda | EBITDA and capex-only cash measures favor in-house builds over hosted platforms |
| prop:acct-tax | ψ_T closed form; after-tax first-year dip; foreign-build penalty τ(1 − ψ_15); ψ = 1 for domestic development |
| rem:acct-evidence | AS 2201 benchmarking (.B28 to .B31) and AI-performed controls; SOC 1 vs SOC 2; no PCAOB AI guidance; COSO 2026 |
| ass:acct-controls, prop:acct-cutover, eq:acct-pmw, eq:acct-defer | cutover window, expected delay, material-weakness probability, threshold rule z* |
| cor:acct-npv, eq:acct-npv | transition NPV for an ICFR-scope process |
| ass:acct-layers, prop:acct-amin, eq:acct-amin | layered controls; common-mode floor; diversity rule; optimal depth; scale limit |
| sec:acct-scope, def:acct-scope | what SEC 2007 guidance, AS 2201 (.36 Note, .47, .B29, .B30) and COSO 2026 (pp. 6, 11, 13, 14) say and do not say on scope and ITGCs; ICFR scope by four channels T, S (`in_scope_system`), I (`feeds_in_scope`), P |
| ass:acct-itgc, eq:acct-itgc | per-application ITGC line (access, change, forced-upgrade retest at rate 1/T_up, operations, interfaces); close-window incidents and manual fallback |
| prop:acct-itgc, eq:acct-pvup | (a) scope monotone, automation never removes scope, the agent is an in-scope application; (b) a_min with Σ_g C^itgc_g + C^tml; (c) transition costs, PV of forced-upgrade retests; (d) timeliness cost and fallback threshold ν* |

## 4. Formulas for the engine

Units: dollars, years, shares of revenue S. Annual fiscal periods [y − 1, y), with transition date 0 at the start of fiscal year 1 (generalize with a fiscal offset).

### 4.1 Book versus cash path (prop:acct-path)
Inputs: F split into categories with policies (see 5.1); t_go ∈ [0, T_par] (default T_par if the parallel run counts as testing, 0 if go-live precedes the run: a policy input); T_B; I; C_wo (book value net of salvage in excess of normal depreciation); C_sev, C_brk; recognition: severance basis ∈ {ASC 712 ongoing: date probable, t_712 ≤ 0 allowed; ASC 420 no retention: t_com; ASC 420 retention: ratable on [t_com, T_par)}; break fees at the notice date t_brk.
- cash_y = ∫_{[y−1,y)} flow − (F + I + C_J)·1{0 ∈ year y} − C_str·1{T_par ∈ year y}, with flow = bWϱ(t) − C_par on [0, T_par) and bW after.
- GAAP_y = ∫ flow − (C_J + F_exp)·1{0 ∈ y} − F_cap·|[y−1,y) ∩ [t_go, t_go+T_B)|/T_B − C_wo·|[y−1,y) ∩ [0,T_par)|/T_par − C_sev·(recognition measure in year y) − C_brk·1{t_brk ∈ y}.
- Identity check (report as a QA assertion): S Σ_{y≤Y}(GAAP_y − cash_y) = I + F_cap(1 − A_Y) − L_Y − C_wo·min(Y/T_par, 1).
- Year 1 closed form (T_par ≤ 1 ≤ T_B, linear ramp, restructuring in year 1): GAAP_1 = cash_1 + [I + F_cap(1 − (1 − t_go)/T_B) − C_wo]/S.
- ASU 2025-06 switch: if the fiscal year begins after 15 Dec 2027 (or the firm early-adopts), F_cap = (1 − u)(F − F_dc) with u the share of build spending incurred while significant development uncertainty exists. Before adoption, F_cap = application-development-stage share (default the same formula; flag it).

### 4.2 Program premium (prop:acct-program)
w = (C_cap/S)[1 − e^{−g_F L} A(g_F T_B)], with A(x) = (1 − e^{−x})/x. Report it next to any GAAP-basis score as "GAAP premium from capitalization".

### 4.3 Tax (prop:acct-tax)
- ψ_T = [1 + (1+r)^{−T}]/(2T) + [1 − (1+r)^{−(T−1)}]/(rT).
- Deduction schedule for the R&E part of F: domestic 100% in year 1 (or the §174A(c) election: ratably over ≥ 60 months from when benefits are first realized); foreign 1/30 in year 1, 1/15 in years 2 to 15, 1/30 in year 16.
- Equipment: 100% in year 1 (election to 40% in the first tax year ending after 19 Jan 2025).
- After-tax year 1: (1 − τ) cash_1 − τ F_for (1 − 1/30)/S.
- Full loss offset is assumed (Part I). With NOLs, defer the shield to the year taxable income appears (engine flag: tax-paying status).

### 4.4 Cutover window and MW risk (prop:acct-cutover, cor:acct-npv)
- Open window z ∈ [T_cl, 1 − T_op]; E[delay | uniform ready date] = (T_op + T_cl)²/2.
- P_mw(H) = p_def p_mw min{1, exp[−(H − T_rem − T_op)/T_dc]}.
- Defer iff L_mw[P_mw(1 − z) − P_mw(1 − T_cl)] > ĉ(1 + T_cl − z) (single crossing; find z* by bisection).
- NPV_ICFR = NPV − C_ctl − ϖ ΔC_ctl (e^{−rT_par} − e^{−rT_h})/r − [ϖ + (1 − ϖ)p_u] e^{−rT_par} L_mw P_mw(H).
- Program scheduling: assign ICFR-scope cutovers to the open window, earliest after the close first; non-ICFR processes are unconstrained. Quarter-end freezes are an optional input that removes further intervals (Item 308(c) and Section 302 apply quarterly).

### 4.5 Accountability floor (prop:acct-amin)
- P = Π_x [p_cm,x + (1 − p_cm,x) p_x^{n_x}].
- a_min = [C_acct + 1{AI}(C_itgc + C_val/T_up) + Σ n_x c_x + N_mm L_mm P]/S.
- Enumerate n_x ∈ {0..6} per type (at most 3 types) and pick the minimum; report the common-mode floor N_mm L_mm Π p_cm,x over the types used, and the design's a_min against the human-only design.
- n* (one type) = ln[N L (1 − p_cm) ln(1/p)/c]/ln(1/p).
- Feed the minimized a_min (financial processes) into the Part I ceiling. Do not add N_mm L_mm P to c_err or to the common-mode cost of prop:ext-commonmode (no double count).
- With prop:acct-itgc(b), replace 1{AI}(C_itgc + C_val/T_up) by Σ_{g in scope} C_itgc_g + C_tml (see 4.6). The engine's `amin_design` (formulas.py:2492) takes one C_itgc for the design; it should take the list of in-scope AI applications and a flag for whether the design's AI layers share one application.

### 4.6 Scope, ITGC lines and timeliness (def:acct-scope, prop:acct-itgc)
Engine names (engine builder): `in_scope_system` (per system: holds or processes significant-account data, or a relevant control depends on it), `feeds_in_scope` (per integration: target system is in scope), and one **ITGC cost line** per in-scope AI application.
- Scope of a unit u (activity, step or application): in_scope(u) = T(u) or S(u) or I(u) or P(u), with T = processes significant-account transactions or performs a relevant control; S = reads or writes any system with `in_scope_system`; I = creates or changes an integration with `feeds_in_scope`; P = executes or is governed by an ICFR-relevant policy (revenue recognition, credit and refund authority, delegation of authority, close calendar). Report the channel set per unit, not only the flag.
- Automation rule: an agent that performs an in-scope unit inherits its channels and is itself an in-scope application. Automating never sets in_scope to false. Elimination (mode N) removes the unit, not by automation.
- ITGC line of application g, a year: C_itgc_g = c_acc (n_id + n_perm) + c_chg n_chg + C_val_g / T_up + c_ops_g + c_ifc n_ifc, where n_ifc = number of g's integrations with `feeds_in_scope`. C_val_g is the ICFR retest, on top of the functional revalidation C_reval of ass:tasks-ancillary (already in run costs and W).
- a_min = [C_acct + Σ_g C_itgc_g + C_tml + Σ_x n_x c_x + N_mm L_mm P]/S. Lines are per application: layers in one application share one line; with one application per AI layer use c = c_ai + C_itgc_g in the depth search. Applications in scope only through S, I or P add their line.
- Transition (cor:acct-npv): ΔC_ctl += Σ_{added} C_itgc_g − Σ_{retired} C_itgc_g + ΔC_tml; C_ctl += design of the new ITGCs and interface controls. Forced-upgrade retests: with stationary upgrade dates use the flow C_val/T_up; with the clock starting at cutover, PV_up = C_val e^{−r(T_par+T_up)} (1 − e^{−r n_up T_up})/(1 − e^{−r T_up}), n_up = floor((T_h − T_par)/T_up). Both are verified (6f).
- Timeliness: ν_cw = n_cl ν_out T_cw; C_wait = ν_cw [c_del D̄ + L_late e^{−T_sl/D̄}]; C_fb_total = C_fb + ν_cw D̄ [c_del (1 − e^{−t_sw/D̄}) + c_fb e^{−t_sw/D̄}] (requires t_sw ≤ T_sl); C_tml = min of the two; fallback iff Δ_fb = D̄ e^{−t_sw/D̄}(c_del − c_fb) + L_late e^{−T_sl/D̄} > 0 and ν_out > C_fb/(n_cl T_cw Δ_fb).
- No double count: c_del and c_fb are increments over the ordinary outage loss x_p of ass:ext-commonmode (in c_err's common-mode term); misstatement risk from a compressed close stays in P; C_fb excludes c_ops_g. C_tml goes in a_min only.
- Examples (illustrative unit costs, verified in checks 6c to 6j): invoice application line $347k a year (access $30k, change $120k, retest $82k at T_up = 1.22, operations $55k, interfaces 4 × $15k); NPV of the invoice transition falls by a further $0.69 million to −$4.60 million; refund agent $157k. Separate applications per AI layer: best design 1 human + 1 AI, $1.21M (0.12%); all-AI $2.10M > human $2.01M. Timeliness: 6-hour incidents $25k a year, fallback does not pay (ν* = 155 a year); day-long incidents $616k, fallback $161k (ν* = 2.2).

### 4.7 Change to the a_min band (for the Part I integration theorist)
- Part I (sections/model.tex, calibration of cor:ceiling) builds a bottom-up floor of about 0.25% at $1bn (direct audit and 404, about 0.14%, plus the best design of the prop:acct-amin example, 0.10%) and keeps the band 0.5% to 4.6% with cases 1.5%, 3%, 4.6%.
- prop:acct-itgc(b) adds one ITGC line per in-scope AI application: about 0.035% of revenue at $1bn for a line like the invoice application's, plus about 0.016% if the application needs a close fallback.
- The bottom-up floor reaches the band's lower end (0.5%) at about 9 in-scope AI applications per $1bn of revenue, or 6 with fallbacks (check 6j). At $10bn the lines are a tenth as large per dollar of revenue.
- Recommendation: the favorable, central and conservative values stand. The lower end of the band should be stated as conditional on the number of in-scope AI applications per $1bn of revenue (or raised for firms with many in-scope agents), and the sentence "the floor is about 0.25%" should add "plus about 0.035% per in-scope AI application at $1bn".

### 4.8 For the acquirer section (prop:acq-replace(d) and ass:acq-replace(iv); coordinator request, 29 Oct)

Verdict: the algebra in (d) is right, but the reading of prop:acct-cutover is incomplete. Congestion is not the only way bunching raises material-weakness risk. The cutover date also matters, and replacement fixes that date.

1. **Congestion is the acquirer's assumption, not part of eq:acct-pmw.** Equation (acct-pmw) is per process and has no n. The statement should say how congestion enters. Suggested wording for (iv): "each leaves an unremediated material weakness with probability P_mw(H; n_fin), equation (acct-pmw) evaluated at p_def(n), T_dc(n) and T_rem(n), each nondecreasing in the number of cutovers handled at once when control owners congest." P_mw rises with p_def, T_dc and T_rem, so P_mw is then nondecreasing in n.
2. **The date channel (missing).** P_mw depends on H, the time from cutover to year-end (prop:acct-cutover(b)), and replacement fixes the date at t^rpl = max{T^bld, max T^leg}, set by the build and the legal leads, not by the close calendar. After t^rpl the legacy organization is gone, so the owner cannot wait for the next close (prop:acct-cutover(c)). The in-place waves can be placed right after a close.
   - With the section's values (p_def = p_mw = 0.3, T_dc = T_rem = T_op = 0.25, T_cl = 1/6), each cutover carries 2.4% right after the close but 9% with half a year or less to go.
   - Four cutovers bunched late in the year give a 31% chance of a weakness, against 9.5% expected weakness-years when spread right after four closes.
   - Without any congestion, bunching at one date is already worse than spreading once that date is later than z = 0.176 of the fiscal year, about 3 days after the earliest open date (check 6k).
   - Part (d) holds only when the bunched and spread cutovers sit at the same position in the year.

   Suggested corrected (d): "(Pace and material weaknesses.) At equal positions in the fiscal year and without congestion, bunching n cutovers into one year does not raise the expected number of years with an unremediated weakness, since 1 − (1 − P)^n ≤ nP. Bunching raises it if control owners congest, by the crossover condition, or if the bunched date leaves less time to year-end than the spread ones: P_mw(1 − z^rpl) > 1 − [1 − nP_mw(1 − T_cl)]^{1/n}, where z^rpl is the position of t^rpl in the fiscal year." The intuition sentence should then read: "integration risk needs congested control owners, lost context, or a cutover date that the build and the legal leads place late in the fiscal year."
3. **Cost metric.** "A year with at least one weakness costs L_mw" is defensible because the effectiveness conclusion is binary (Item 308(a)(3): management may not conclude ICFR is effective "if there are one or more material weaknesses"). Still, it is a different, sub-additive cost from the per-process L_mw of cor:acct-npv; remediation and disclosure costs scale with the number of weaknesses. Under the per-weakness cost, bunching and spreading cost the same without congestion (nP either way), and any congestion makes bunching costlier. The text should state which metric it uses. The macro \acqMwCrossRise ("by more than 4%") is a relative rise (2.37% to 2.46%); say "by more than 4% of its value" or "above 2.46%".
4. **Independence.** 1 − (1 − P)^n assumes independent deficiencies. Processes cut over together onto the owner's platform share its ITGCs (prop:acct-itgc(b): one application, one line), so a single ITGC deficiency can make every IT-dependent control on it ineffective. That correlation leaves the direction of (d) unchanged under the any-weakness metric, but it makes the weakness pervasive; under the per-weakness metric it raises the variance, not the mean.
5. **First-year exclusion (relevant to the replace path).** SEC staff allow management to exclude an acquired business from its ICFR assessment for up to one year from the acquisition date (sec2007faq, Q3; staff view, not a rule). A replacement cut over within that year is first assessed at the first year-end after the exclusion ends, so its H can exceed one year and P_mw falls. This favors cutting over early in the first year after an acquisition, if the exclusion is taken and disclosed. A newly public company's first annual report has no assessment (Item 308, Instruction 1).

## 5. Inputs the engine should request

### 5.1 Capitalization and accounting policy
- Reporting framework (US GAAP assumed); ASU 2025-06 adoption date (required for annual periods beginning after 15 Dec 2027; early adoption allowed) and transition method (prospective, modified, retrospective).
- Per build cost category, the treatment: in-house development; hosted implementation (CCA); data conversion and cleansing; labeling; training; purchased data (350-30); model training and fine-tuning. Defaults as in tab:acct-map, each marked judgment where the guidance is silent.
- Share u of each build incurred while significant development uncertainty exists (default 0.4 for novel agentic functions, 0 for routine builds; assumed).
- Go-live convention (t_go = 0 or T_par); book life T_B by asset class (internal-use software, hosted implementation = contract term plus reasonably certain renewals, servers).
- Legacy asset register: carrying amounts, salvage, normal remaining depreciation, and planned cease-use dates.
- Severance arrangement type (ongoing plan or past practice → ASC 712; one-time → ASC 420), retention requirements, legal notification periods (WARN and local law, from the labor agent), and the communication date.
- Contract terms for break fees (notice periods).
- SBC: forfeiture policy (estimate or as occurs) and the unvested awards of affected staff.

### 5.2 Fiscal calendar
- Fiscal year-end; close length T_cl (default 1/6 year; assumed); annual report filing deadline (input; depends on filer status); quarter-end freeze length (default 0).
- Minimum operating period T_op for new controls before an assessment (default 0.25 year; judgment, since no standard sets a minimum).

### 5.3 Auditor and filer status
- Filer category: large accelerated, accelerated, non-accelerated, smaller reporting company; EGC flag; newly public (first annual report) flag; recent acquisitions and their dates (one-year exclusion).
- 404(b) applies: derived from the above (it does not apply to EGCs or non-accelerated filers).
- Auditor; prior-year ICFR opinion; open deficiencies and material weaknesses; L_mw inputs (audit fee, market cap for the cost-of-equity channel; default illustrative $5 million; class d).

### 5.4 Existing control inventory for financial processes (record-to-report, procure-to-pay, order-to-cash, revenue)
- For each key control: process and assertion; type (manual, IT-dependent manual, automated application, AI-performed, AI-assisted); frequency; precision; owner; layer position (preventive or detective); provider and model behind any AI layer; benchmarking status.
- ITGC landscape for each system: change management, logical access, operations; SOC 1 Type 2 reports from service organizations and their period coverage; complementary user entity controls.
- Deficiency history, as the basis for p_def; misstatement opportunities N_mm and severity L_mm (default illustrative).
- AI governance costs: C_itgc and C_val; T_up from the vendors' deprecation policies (security_and_maintenance block).

### 5.6 Scope map and ITGC inputs (prop:acct-itgc)
- System register with `in_scope_system` (and its basis: significant account, relevant control dependency).
- Integration register: source, target, `feeds_in_scope`, owner, and whether the transition creates or changes it.
- ICFR-relevant policy list (revenue recognition, credit and refund authority, delegation of authority, close calendar) and the units each governs.
- Per AI application: service identities n_id, tool permissions n_perm, expected changes a year n_chg, operations cost, integrations feeding in-scope systems n_ifc; unit costs c_acc, c_chg, c_ifc and the ICFR retest cost C_val (defaults illustrative: $2,000, $5,000, $15,000, $100,000; class d); whether control layers share an application.
- Close calendar: closes a year n_cl, close-window length T_cw, slack to the filing deadline T_sl; delay cost c_del, deadline loss L_late; provider incident rate ν_out and mean duration D̄ (from provider status histories; class d); fallback standing cost C_fb, switch time t_sw, running cost c_fb.

### 5.5 Tax profile
- Domestic versus foreign location of development work (share F_for); tax-paying status (NOL carryforwards); §174A(c) election; bonus election-out; small-business status (gross receipts ≤ $31 million for 2025, §448(c), Rev. Proc. 2025-28).

## 6. Notation added (no reserved symbols reused)

𝒴* (in-scope systems), 𝒰* (in-scope units), 𝒰*_AI (in-scope AI applications), channels (T), (S), (I), (P), C^itgc_g, c^acc, n^id_g, n^perm_g, c^chg, n^chg_g, C^val_g, c^ops_g, c^ifc, n^ifc_g, n_cl, T_cw, ν_out, ν_cw, D̄, c_del, T_sl, L_late, C^fb, t_sw, c_fb, Δ^fb, ν*, C^tml, C^tml_wait, C^tml_fb, PV^up_g, n_up (λ, K and 𝒢 avoided: reserved or used elsewhere);
F^cap, F^exp, F^dc, u (share under significant development uncertainty), T_B (book life), t_go, C^sev, C^brk (so C^str = C^sev + C^brk), t_sev, t_com, t_brk, 𝖠_Y, 𝖫_Y (sans-serif, as for the normal functions in theory_core), C^cap(t), g_F, L (lag to go-live), 𝖠(x), c^cap, F^for, ψ_T, ΔR^{c,τ}, z, H, T_op, T_cl, p_def, p_mw, T_dc, T_rem, L_mw, ĉ (as in prop:tasks-transition(d)), C^ctl, ΔC^ctl, N_mm, L_mm, p^cm_x, p_x, c_x, n_x, p^ind, C^itgc, C^val, C^acct, o.
Conflicts to note: the engine's `I` (integration) versus theory_core's I (equipment capex); the section uses theory_core's meaning. `L` (lag) is local to prop:acct-program.

## 7. What in the existing drafts is wrong or incomplete on accounting and controls

1. **prop:tasks-scorepath(b) and its proof (theory_core, proofs_core).** The proposition is stylized and is not wrong as an assumption, but as a description of GAAP:
   - (a) it capitalizes all of F, including readiness and integration spending, much of which is data conversion and must be expensed (ASC 350-40-25-5);
   - (b) it amortizes from date 0, whereas ASC 350-40-35-6 starts amortization when the software is ready for its intended use;
   - (c) it books the write-off at cutover, whereas ASC 360-10-35-47 spreads it from the commitment date as accelerated depreciation;
   - (d) it books severance at cutover, whereas ASC 712 and ASC 420 book it when probable, at communication, or ratably.

   Prop prop:acct-path(c) contains it as the special case F^cap = F, t_go = 0, T_B = T_A. Suggest one sentence in theory_core pointing to Section sec:accounting.
2. **prop:tasks-aggregate(a)** defines the activity part of a_min at e_j = 0. That sets the residual control-failure risk to zero and so omits the expected-misstatement part of the floor, which does not vanish under common-mode failure (prop:acct-amin).
3. **(Fixed 29 Oct by this agent at the coordinator's request: theory_ext lines 20, 46 and 174, verify_part2_ext.py, theory_ext_notes.md; the engine defaults already carry psi_domestic.)** **theory_ext Section ext-setup, line 46, and defaults.yaml psi = 0.787:** "five-year straight-line deductions" is the 2022–2024 regime. Under current law (§174A) ψ = 1 for domestic software development; foreign development has ψ_15 ≈ 0.53 (penalty about 12% at τ = 0.21, not 5.7%).
4. **Engine plans.py:** tax deduction tied to book capitalization (see Section 2 above); GAAP amortization start; write-off and severance timing.
5. **(Fixed 29 Oct: 08_params.py now scopes the 36-month rule to off-the-shelf software, re-sources amortization_years_T_A as a book life, and adds depreciation.rnd_tax_treatment; params.yaml regenerated, 10_validate.py passes.)** **params.yaml `software_tax_life_months: 36`** (26 CFR 1.167(a)-14(b)(1)) applies to off-the-shelf software under §167(f). Internally developed software is R&E under §174/§174A and is not amortized over 36 months. `internal_use_software_book_life_years` cites "ASC 350-40", but the standard prescribes no life.
6. **Spec 13.1** lists "integration and platform builds that are capitalized". Only the software-development part is capitalizable; data conversion is expensed, and so is training.
7. **Part I discussion (accountability floor):** "the auditor of an accelerated filer must attest" omits that emerging growth companies are exempt from 404(b) even when accelerated (15 U.S.C. 7262(b); Item 308(b)), and that the first annual report of a newly public company has no assessment (Item 308, Instruction 1). This is minor and the statement is otherwise correct.
8. **Part I discussion (measurement at the limit):** "capitalizing internally developed software shifts cost between periods". This is true for one project. For a growing program the shift is a permanent upward bias of the GAAP score (prop:acct-program), so the argument for FCF after capitalized software is stronger than stated.
9. **ref_verification_part2.md item 8** (174A "dropped", practitioner-only): now verified at primary sources (26 U.S.C. §174A and §174 via LII, Rev. Proc. 2025-28); the practitioner summary was correct.
