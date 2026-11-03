# Theory of ownership regimes (Part II, spec Section 16): notes

Files:
- `part2/theory_regimes.tex`: `\section{Ownership, Returns and the Pace of Transformation}\label{sec:regimes}`.
- `part2/proofs_regimes.tex`: `\section{Proofs for Section~\ref{sec:regimes}}\label{app:proofs-regimes}`.
- `code/verify_part2_regimes.py`: 80 checks, all passing (no skips: the core's single source `data/examples/invoice_chain.json` is now read). About 40 s.
- `part2/refs_regimes.bib` (new, coordinator request 3): axelson2013borrow, gompers2016what, gompers2020how, damodaran2026cost, silverpeak2026software.

Test build (scratch harness with Part I's model and appendix, theory_core, theory_ext, both proof appendices, and `\bibliography{refs,part2/refs_part2,part2/refs_modern}`): no errors, no overfull boxes in my files, every citation key in my files resolves. Other files have undefined keys and references (core and ext cite keys not yet in any bib, and `prop:prod-*`); none are mine. The section runs about 9.5 pages (two tables included) and the proofs about 5. Building `paper.tex` needs `part2/refs_modern.bib` and `part2/refs_regimes.bib` in `\bibliography`, and `part2/tables/` (theory_core now inputs `invoice_macros.tex`). The section runs about 9.6 pages after the added citations.

All examples are labeled "illustrative" and stated as conditional on the assumed presets (assumptions memo items 6 to 8, coordinator note).

---

## 1. Results (labels)

| Label | Content |
|---|---|
| `ass:reg-regime` | Regime = (rate r_o, horizon T_o, terminal rule (EBITDA rule with h_x, M_exit, T_sea; market rule with frakA_T, X^scr), myopia (frak w, window Y_m, guided slack frak g), financing (lev_0, covenant levbar, w_cov; cash budget net of payouts), stakeholder terms (b_fam via omega_h, pass-through, equity pay at fair value), latency factor lat_o) |
| `def:reg-value`, `eq:reg-value` | Regime value of any plan: PV at r_o on [0, T_o) + e^{-r_o T_o} E[TV] - myopia penalty on the planned GAAP path |
| `tab:reg-presets` | Presets with S/Sp/Ss/Sc/A status |
| `prop:reg-value` (`eq:reg-trans`, `eq:reg-K`, `eq:reg-zeta`) | (a) core NPV at (r_o, min(T_h, T_o)) + terminal term; (b) capitalization of a run-rate dollar; exit owner more patient than a going concern at the same rate iff M~ > 1/r, cliff at T - T_sea; (c) single crossing r^dagger between quick and slow designs; (d) PE capital hurdle zeta^pe (EBITDA rule credits capital-heavy automation) |
| `tab:reg-rank` | Archetypes Q, P, K valued by public, family, PE (h_x = 1 and 0.5) and VC |
| `prop:reg-weight` (`eq:reg-Xmy`, `eq:reg-Xexit`, `eq:reg-Xdag`) | (a) X_o = v'(s; r_o), v_0 decreasing in r; (b) myopia: X^my = k + (X - k)/(1 + frak w), factors and loss; (c) hold-and-exit weight X^x(tau); (d) frontier ordering; (e) growth engine vs cost-out threshold X^dagger |
| `prop:reg-speed` | (a) hurdle raises v*, make-or-buy volume, capital test, adoption date; single sign change -> IRR rule, T_h*(r) nondecreasing; (b) hold caps time to run-rate plus seasoning; bang-bang start (cash yield vs hurdle); payback cap only if h_x = 0; (c) program deadline n_w <= floor((T - T_sea)/T_par); latency raises the load breakpoint |
| `ass:reg-dip`, `prop:reg-dip` | (a) covenant arithmetic (exact, linear); (b) common budget form Dhat(n_k) - shat N_{k-1} <= frak B; (i) fastest ramp dominates every feasible plan; (ii) linear case: geometric waves, closed-form k-hat, ramp optimal; (iii) quadratic: KKT decrements, rising plan after a binding wave; (c) myopia as an exact penalty, threshold max mu*/T_par, monotone in frak w; (d) PE squeeze (deadline x covenant) |
| `lem:reg-waterfall` | LP distributions under preferred return, full catch-up and carry; fees |
| `prop:reg-metrics` | (a) PE entry/exit equity, MOIC, IRR, leverage amplification (with h_x); (b) EPS and guidance path; (c) Delta R*_o and Delta value_o for every regime; (d) stakeholder split |
| `ass:reg-lbo`, `prop:reg-lbo` (`eq:reg-lbo`, `eq:reg-exec`) | (a) sponsor NPV identity, maximum premium, break-even hurdle = continuous IRR; (b) frictionless benchmark: p_max P0 = Delta V^exec - C_tx - distress; (c) Delta V^exec nondecreasing in frak w; growth-weight loss; (d) decomposition with valuation wedge frak D and leverage term frak L |
| `prop:reg-hybrid` | (a) dual class / controller; (b) PIPE or minority (budget shift; weighted weight); (c) carve-out (shared rebuild lowers the breakpoint); (d) VC: exit-date Rule-of-X^scr objective |

Mapping to the brief: (1) prop:reg-value, tab:reg-rank; (2) prop:reg-speed; (3) lem:reg-waterfall, prop:reg-metrics; (4) prop:reg-dip; (5) prop:reg-lbo; (6) prop:reg-weight; (7) prop:reg-hybrid.

---

## 2. Notation (new symbols) and deviations from the spec

| Spec | Used here | Reason |
|---|---|---|
| regime varrho_own | sans-serif o in {pub, fam, pe, vc} | varrho is the core's ramp |
| r_own | r_o (r_w for the public WACC) | r keeps its Part I meaning as a discount rate; subscript marks the regime |
| myopia weight theta_my | frak w (`\mathfrak w`; frak w_o, frak w_pub, frak w_dc, frak w_pc) | theta is reserved (margin persistence, Part I) and vartheta is theory_ext's altruism, so the regimes section uses frak w, which no other Part I or Part II file uses (verify I3 guards this). Renamed from vartheta on 29 Oct 2026 at the coordinator's request; theory_acquirer.tex still writes vartheta_pc and vartheta_dc in ass:acq-pc(iv) and tab:acq-levers and should switch to frak w_pc and frak w_dc |
| covenant "cov" | levbar (cap), lev_0 (entry), frak B^cov = (levbar - lev_0) EB_0 (headroom), w_cov (weight of current wave flow in tested EBITDA) | readable; Lambda, curly H, curly B are taken |
| M_exit | kept | subscript distinguishes it from Part I's market size M |
| debt rate | r_debt | theory_ext uses r_D := r + nu_D |
| pi_p (success) | varpi_p (core's) | pi is the inference price |
| EBITDA, net debt, operating income | EB, ND, OI (upright) | E_j is labor-equivalent spend, Pi is reserved |
| (none) | h_x: share of new seasoned run-rate a buyer capitalizes; T_sea: seasoning; M~ = h_x M_exit W^E/W or frakA_T: capitalization at exit; frakA_T := A_T(eta) + theta eta^T Gamma (Part I Lemma valuation2) | terminal rules |
| (none) | W^E = W + delta_K I: run-rate EBITDA saving | EBITDA adds back replacement capex |
| (none) | frak K_o(t): PV of a run-rate dollar from t; zeta^pe: PE capital hurdle; r^dagger: switch rate | |
| (none) | Y_m: myopia window; frak g: guided slack (share of revenue) | needed to define a "dip penalty" |
| (none) | X^my, X^x(tau), X^G = mhat/(r - G), X_T, mhat, mhat^E (marginal FCF and EBITDA margins), X^dagger | growth weights (Part I's m-bar is reserved, hence mhat) |
| (none) | t_run, t_0, tau, nbar_w | timing and deadline |
| (none) | T_1 (curly): one-time cash per process; Dhat, shat, frak B; nbar(x); N^g_k; k-hat; mu_k | dip budgets |
| (none) | r_pref, c_cy, c_fee, Lambda_T = (1 + r_pref)^T; MOIC, IRR | waterfall (h is reserved: headroom h(s)) |
| (none) | frak p (premium), frak p^max, frak p^req, c_tx, C_tx, frak L (leverage term), frak D (valuation wedge), V^sp, V^sq, V^prog(Pi), Pi^pub, Pi^pe, p_b, L_b | take-private |
| (none) | lat_o (latency factor), b_fam (omega_h = (1 - tau) b_fam w_j), omega_m (board weight), C_P (new equity), C^sep, C^par,sh (carve-out) | hybrids |

Other modeling choices:
- Rates are continuously compounded (as in Part I). Every annual preset is converted with r = ln(1 + r_annual), in the engine and in the examples: WACC 9.34% -> 8.93%; family 8.34% -> 8.01%; PE 22% -> 19.89%; VC 31% -> 27.00%; debt 8% -> 7.70%. The 8% preferred return enters the waterfall as 1.08^T (= e^{0.0770 T}), so it needs no further conversion. IRRs are reported annually compounded; a break-even hurdle from the continuous NPV is converted back with e^r - 1.
- Myopia window and guided slack are scenario parameters: the examples use Y_m = 2 years, guided slack 0 for a single transition (A11) and 0.01 of revenue for the twelve-process program (D6 to D10).
- The myopia penalty is evaluated on the planned (success) GAAP path, b = 1, as guidance is set on the plan.
- The terminal value under the EBITDA rule credits only seasoned run-rate on the success branch; failure branches have zero run-rate at exit.
- The market rule applies frakA_T to the FCF run-rate W (not W^E), because the market values FCF margins.
- Family horizon: the parameter file's 30 years without terminal value makes the family impatient; examples use T = infinity at r_fam and report the 30-year variant (ranking unchanged).

---

## 3. Formulas the engine must implement

Units: dollars and dollars a year; years; rates continuously compounded.

### 3.1 Regime preset (input `regime`)
```
r_o = ln(1 + r_annual) for every annual preset (WACC, family, PE, VC, debt), T_o (inf for going concerns),
terminal_rule in {none, ebitda, market}, M_exit, h_x, T_sea,
frakA_T (market rule; from Part I Lemma valuation2 with buyer's r, g, T, G_inf, theta), X_scr,
frak w, Y_m, g_slack (frak g, share of revenue), lev0, levbar, w_cov, r_debt, c_tx, premium_req,
r_pref, carry c_cy, fee c_fee, b_fam, lat_o, cash_budget (net of required payouts)
```

### 3.2 Value of a transition by regime (prop:reg-value)
- W^E = W + delta_K I.
- V_o = NPV_core(r = r_o, T_h = min(T_h, T_o), T_par, ...) + exp(-r_o T_o) * varpi_p bbar_p * Mtilde * W - P_o, valid if T_par + T_sea <= T_o.
  - Mtilde = h_x M_exit W^E / W (EBITDA rule); frakA_T (market rule); 0 (going concern, T_o = inf).
  - NPV_core is eq:tasks-npv (core reference implementation `transition_npv`).
  - P_o = frak w sum_{y=1}^{Y_m} exp(-r_o y) max(0, -dOI_y - g_slack S), dOI_y = S * GAAP score path of prop:tasks-scorepath(b) with b = 1 (core `annual_dm(..., "gaap")`).
- If T_par + T_sea > T_o: terminal term is 0 (only interim flows).
- Family: replace W by W - b_fam (1 - u_d) C_disp.
- Step capitalization: K_gc(t) = e^{-rt}/r; K_x(t) = (e^{-rt} - e^{-rT})/r + e^{-rT} Mtilde for t <= T - T_sea, else (e^{-rt} - e^{-rT})^+/r.
- Rankings: rank by V_o (mutually exclusive designs) or by PI_o = W K_o(t)/C (budget-constrained). Report r^dagger = root of V_l(r) - V_q(r) (unique when C_l >= C_q, t_l > t_q, W_l > W_q).
- PE capital hurdle: zeta_pe = [1 + delta_K A_r(T)] / [A_r(T) + e^{-rT} h_x M_exit], A_r(T) = (1 - e^{-rT})/r at r = r_pe, T = T_hold; adopt a capital switch iff Dc/DK > zeta_pe (value test for public: Dc/DK > r_w + delta_K). Flag switches in (zeta_pe, r_w + delta_K).

### 3.3 Growth weight by regime (prop:reg-weight)
- Going concern: X_o = v'(s; r_o); small-share: v_0(r_o) = smallest positive root of (r_o - G) v = m_0 - kG + C_alpha [lambda (v - k)^+]^{1/(1 - alpha)} (core `gordon_root` with r = r_o). If no root exists, report "unbounded at small share" and use the HJB solution at the firm's share (Part I).
- Myopic public: X^my = k + (X_o - k)/(1 + frak w). Delta* scales by (1 + frak w)^{-alpha/(1-alpha)}, sigma* by (1 + frak w)^{-1/(1-alpha)}; loss = Pi(X)[1 - (rho - alpha rho^{1/alpha})/(1 - alpha)], rho = (1 + frak w)^{-alpha/(1-alpha)}.
- Hold and exit: X^x(tau) = (1 - w) mhat/(r_o - G) + w X_T, w = e^{-(r_o - G) tau}; X_T = h_x M_exit mhat^E (EBITDA rule) or (V/S)_T (market rule). Recompute at each date of the plan (tau = time to exit).
- Frontier at X_o: Part I eqs Dstar, sigstar, Rstar (core `partI`).
- Growth engine vs cost-out: X^dagger = k + (1/ell) [da / (C_alpha ((1 - delta_sigma)^{-alpha/(1-alpha)} - 1))]^{1 - alpha}.

### 3.4 Pace (prop:reg-speed)
- Use a(r_o, T_A) = r_o/(1 - e^{-r_o T_A}) everywhere the core uses a(r, T) (crossover, volume, make-or-buy), and (r_o + delta_K) in capital tests; ext timing with r_o.
- Check the single-sign-change condition (C_par >= varpi bbar W); if it holds, report IRR (root of NPV(r)) and T_h*(r_o); otherwise report NPV at r_o only (IRR may be non-unique).
- Exit rule start date: t_bar = T - t_run - T_sea; if W e^{-r t_run}/C >= r_o start at 0, else at t_bar (if V(t_bar) >= 0), else never. With h_x = 0: require C/W <= tau - t_run.
- Wave deadline: n_w <= floor((T_o - T_sea)/T_par) for exit regimes.
- Latency: kappa_hat = 1 + c/2 - sqrt(c + c^2/4), c = r_d l_0 lat_o (ext bandwidth block); pace bound N e T_par/(kappa_hat Phi).

### 3.5 Dip budgets and waves (prop:reg-dip)
- Covenant (exact): dND_t + levbar * (-dEB_t) <= (levbar - lev0) EB_0 at every test date (quarterly), with dEB_t = w_cov (s N_{k-1} - D(n_k)) during wave k and dND_t = cumulative one-time cash + cumulative dual-running cash - cumulative savings (+ interest at r_debt). The engine must use this exact test; the closed forms use the first-order form below.
- First-order forms: public Dhat = D, shat = s, B = g_slack S; PE Dhat(n) = T_1 n + w_cov levbar D(n), shat = w_cov levbar s - T_1, B = (levbar - lev0) EB_0.
- Fastest ramp: N_0 = 0; N_k = min(N, N_{k-1} + floor(Dhat^{-1}(B + shat N_{k-1}))). k_hat = first k with N_k = N; infeasible if a cap is 0.
- Linear D: N_k = (B/shat)[(1 + shat/dhat)^k - 1]; k_hat = ceil(ln(1 + shat N/B)/ln(1 + shat/dhat)); the ramp is optimal.
- General D: minimize sum_k [T_par (s k n_k + D(n_k)) + O_w] subject to the budget per wave (hard) or plus frak w T_par sum_k (D(n_k) - s N_{k-1} - g_slack S)^+ (soft). Exact enumeration of compositions for N <= 20; otherwise convex relaxation (SLSQP) and rounding plus local search. Report the multipliers mu_k and the exact-penalty threshold max_k mu_k / T_par.
- Squeeze: if N^g_{nbar_w} < N, report the processes that miss the exit and their lost terminal value h_x M_exit s^E e^{-r T} each; report the cure that completes the program (smallest B increase with N^g_{nbar_w} = N).
- Shadow value of headroom: sum_k mu_k (continuous relaxation).

### 3.6 Metrics (lem:reg-waterfall, prop:reg-metrics)
- PE: Eq_0 = (1 + premium + c_tx) P_0 - lev0 EB_0 (for a buyout of a private firm, P_0 = entry multiple x EB_0, premium 0); ND_T = ND_0 e^{r_debt T} - int_0^T e^{r_debt (T - t)} FCF(t) dt; Eq_T = M_exit (EB^sq_T + h_x dEB_T) - ND_T; MOIC = Eq_T/Eq_0; gross IRR = MOIC^{1/T} - 1 (annual). Baseline: entry multiple = exit multiple (no multiple expansion); never pair the historical 7.6x entry multiple with the 2025 software exit multiple. Report h_x in {0.5, 1} at least.
- Waterfall: pref = (1 + r_pref)^T; LP = MOIC if MOIC <= pref; pref if MOIC <= 1 + (pref - 1)/(1 - c_cy); else 1 + (1 - c_cy)(MOIC - 1). Net multiple = LP/(1 + c_fee T); net IRR = net^{1/T} - 1 (fees at entry; compute the exact annual-fee IRR numerically as well).
- Public: dEPS_y = (1 - tau) dOI_y / N_sh; guidance gap dOI_y + g_slack S; accretion year = first y with dOI_y >= 0; Rule-of-40 cash and GAAP paths (core).
- Every regime: dR*_o = -(1 - phi)(dc_h + dc_c) - da - (g*(X_o) + delta_K) dk + sigma*(X_o) delta_sigma + (X_o - k) dG_i; d value_o = V_o of the program (3.2 applied to the program's flows); small-share going concern: S dR*_{X_o}/(r_o - g0_o) - PV(one-time costs).
- Stakeholders: customers phibar W_cogs; taxes tau [(1 - phibar) W_cogs + W_op]; owners the rest; displaced employees (1 - u_d) T_sev C_disp once; lenders: covenant headroom path.

### 3.7 Take-private (prop:reg-lbo)
- NPV_sp = V_sp - (1 + p) P_0 - c_tx P_0 + frakL - e^{-r_pe T} p_b L_b, V_sp = e^{-r_pe T}[M_exit (EB^sq_T + h_x dEB_T) + FV_{r_debt}(FCF)], frakL = ND_0 [1 - e^{-(r_pe - r_debt) T}].
- p_max = [V_sp + frakL - c_tx P_0 - e^{-r_pe T} p_b L_b]/P_0 - 1; pays iff p_max >= premium_req; break-even hurdle = ln(E Eq_T/Eq_0)/T.
- Frictionless benchmark (report always): Delta V_exec = V_prog(Pi_pe; r_w) - V_prog(Pi_pub; r_w); p_max_frictionless = (Delta V_exec - C_tx - distress)/P_0. Pi_pub is the public owner's plan under its dip budget/penalty; Pi_pe the sponsor's under covenant and deadline.
- Decomposition: p_max P_0 = Delta V_exec + frakD + frakL - C_tx - risk, frakD = V_sp - [V_sq + V_prog(Pi_pe)] at r_w.
- Growth-weight loss: rho = ((X_pe - k)/(X - k))^{alpha/(1-alpha)}; loss per year = Pi(X)[1 - (rho - alpha rho^{1/alpha})/(1 - alpha)] in score units; capitalize at the public weight.
- Baseline exit multiple = the multiple paid (no expansion); report h_x in {0.5, 1}.

### 3.8 Hybrids (prop:reg-hybrid)
- Dual class: frak w_dc in [0, frak w_pub]; rerun 3.3 and 3.5 with it.
- PIPE / equity cure: B_cov += C_P (or cash budget += C_P); GAAP budget unchanged.
- Minority with board weight omega_m: X = omega_m X_inv + (1 - omega_m) X_pub.
- Carve-out: incremental NPV = NPV_core + C_sep + C_par_sh A_r(T_par); undiscounted T_h* falls by (C_sep + C_par_sh T_par)/(varpi bbar W).
- VC: X^x(tau) with r_vc, X_T = (V/S)_T; terminal objective frakA_T S_T (dm_T + X_scr dg_T).

---

## 4. Presets (sourced or assumed)

| Parameter | Value (range) | Status | params.yaml key / source |
|---|---|---|---|
| public r_w | 9.34% annual = 8.93% continuous (7.0 to 10.66%) | sourced, practitioner data set (damodaran2026cost; on disk) | ownership_regimes.public.r_own_wacc |
| family r | r_w - 1 pt annual = 8.01% continuous (-3 to +2) | assumed | private_family.r_own_spread_over_public_wacc |
| family horizon | 30 yr (10 to 100) in file; infinite in examples | assumed | private_family.horizon_years |
| family employment preference b_fam | 0.10 (0 to 0.3) of loaded wage | assumed | private_family.employment_preference_b_share_of_wage |
| PE target gross IRR | 22% annual average (median 25%) = 19.9% continuous (20 to 25) | sourced, survey (gompers2016what; flagged) | pe_backed.target_gross_irr |
| PE target MOIC | 2.5 (2.5 to 2.85) | sourced, survey | pe_backed.target_moic |
| hold | 6 yr (4 to 7) | sourced (Kaplan and Strömberg 2009) | pe_backed.hold_period_T_hold_years |
| entry leverage | 5.2x total debt (net 5.1; quartiles 4.2 to 6.1) | sourced (axelson2013borrow) | pe_backed.entry_leverage_debt_to_ebitda |
| covenant | 7.0x (6 to 8) | floor sourced (supervisory 6x, SR 13-3; grounding b), central assumed | pe_backed.covenant_max_net_debt_to_ebitda |
| exit multiple | 14x (10 to 17; reported band 12 to 17) | practitioner, small sample, restricted republication (silverpeak2026software, accessed 29 Oct 2026; flagged) | pe_backed.exit_multiple_M_exit_software_ev_to_ebitda |
| entry multiple (examples) | = exit multiple | rule (assumptions memo item 7) | (do not use entry_ev_to_ebitda_historical with the 2025 exit multiple) |
| carry, fee | 20%, 2% | sourced (Kaplan and Strömberg 2009) | pe_backed.carried_interest, management_fee |
| preferred return | 8% (6 to 8) | secondary (practitioner statement) | pe_backed.preferred_return_hurdle |
| control premium | 30% (15 to 50) | range sourced, central assumed | hybrid_take_private_control_premium |
| VC target IRR | 31% annual average = 27.0% continuous (late stage 28 to 29) | sourced, survey (gompers2020how; flagged) | vc_backed.target_irr |
| VC horizon | 7 yr (5 to 10) | assumed | vc_backed.horizon_years |
| myopia frak w | 0.30 (0 to 0.6) | assumed (direction: Stein; Graham et al. survey; Terry 2023) | public.myopia_weight_theta_my |
| dual-class frak w | 0.15 (0 to 0.3) | assumed | hybrid_dual_class_myopia_weight |
| latency factors | public 1.0, family 0.7, PE 0.5 | assumed (VC not set) | *.decision_latency_multiplier |
| debt rate | 8% annual = 7.70% continuous (6 to 11) | assumed (floor: 2-yr Treasury 3.80%) | regime.debt_rate (engine), pe_backed.debt_rate_reference |
| h_x | 1 (0 to 1); report 0.5 and 1 | assumed, class d | new (engine regime parameter) |
| T_sea | 1 yr | assumed, new | new |
| Y_m, guided slack | 2 yr; 0 (single transition) or 0.01 of revenue (program) in examples | scenario parameters, new | new |
| w_cov | 1 (annualized test) | assumed, new | new |
| transaction costs c_tx | 2% of price | assumed, new | new |
| permanent capital (row of tab:reg-presets) | horizon infinite, no exit; hurdles 25% unlevered and 65% levered annual = 22.3% and 50.1% continuous on the 5-year method IRR, flows after year 5 at r_tv = r_w; ND_0 = min(85% of EV paid, debt repaid by 5 years of FCF); covenant ND <= 4.0 EBITDA; debt rate ln(1 + 9.625%) = 9.19% continuous (`\acqRdebt`), the coupon on the USD 1.25bn senior secured notes priced 28 Oct 2026 (EUR 500m tranche 8.625%; a coupon, not a yield); frak w_pc in [0, frak w_dc] | F-1 policy (bendingspoons2026f1) and 6-K (bendingspoons2026sixk), both in part2/refs_acquirer.bib; r_tv and frak w_pc assumed. The sponsor's debt preset stays 8% (7.7%) | owned by the acquirer section (ass:acq-pc, prop:acq-pc; macros in part2/tables/acquirer_macros.tex); the engine builder's `permanent_capital` block |

Parameters added by this section that are not in params.yaml: h_x (the auditor added it as an engine key), T_sea, Y_m, guided slack, w_cov, c_tx, VC latency. All assumed.

---

## 5. Problems with the spec and the brief

1. **Notation clashes (spec 16.1):** varrho_own (core's ramp), theta_my (reserved), "cov", M_exit vs Part I's M; renamed as in Section 2. r_D is taken by theory_ext (r + nu_D), so the debt rate is r_debt.
2. **"A short hold caps the payback of waves the owner will fund" (brief, spec 16.2) is right only if buyers capitalize none of the recent run-rate (h_x = 0).** If they do, the hold caps the time to run-rate plus seasoning, the admissible payback can far exceed the hold, and within the hold the start date is bang-bang in the cash yield versus the hurdle (prop:reg-speed(b)).
3. **"PE capitalizes run-rate savings at M_exit, which favors fast cost-outs with payback inside T_hold" is incomplete.** With M~ > 1/r the exit owner is more patient than a going concern at its rate within the hold (prop:reg-value(b)); what an EBITDA multiple distinctively favors is capital-heavy automation, because EBITDA ignores replacement capital (zeta^pe < r_w + delta_K). Evidence: richards2024managing finds PE cost-outs through staffing and vendors, not technology; there is no verified study of AI adoption by ownership regime (modern map, item 10), so regime pace is a model implication.
4. **"A hurdle above WACC raises the breakpoint thresholds"** holds for thresholds built on fixed or capital costs and for transitions whose net cash flow changes sign once (stated condition C_par >= varpi bbar W); with several sign changes the IRR may not be unique.
5. **Myopia weight theta_my is underdetermined:** the spec needs a window (Y_m), a reference (guided slack), and a unit (per dollar of shortfall). I use one parameter in two consistent ways: linear at the margin (gives X^my) and kinked at the guided slack (gives a budget). Its value is not identified by any source.
6. **PE dip budget:** the spec does not say which transition costs covenant EBITDA adds back. I parametrize w_cov and treat one-time costs as cash-only (added back); the first-order form omits interim dual-running cash, so the engine must use the exact test (in the example the exact test peaks at $34.1M of $40M and leaves the optimum unchanged).
7. **"When a change of ownership pays" (spec 16.2):** earning the exit multiple is a gain only if it exceeds fair value (a transfer, frak D); in the frictionless benchmark the condition is execution gain >= premium + costs + distress. Speeding up a program the public owner would do anyway does not pay a 30% premium in the example; avoiding a blocked program does.
8. **Family horizon of 30 years with no terminal value** contradicts the "patient, dynastic" intent and makes the family less patient than an infinite-horizon owner; use T = infinity at r_fam or add a terminal value.
9. **Survey hurdles are annual averages and are targets for portfolios** (VC targets embed failure rates; the PE median target is 25%, the average 22%); they are not discount rates for a single project's cash flows. Flagged; the engine and the examples convert them with ln(1 + r) and treat them as scenario values.
10. **Brief listed Axelson et al. 2013 as an available bib key.** It is not in refs.bib, refs_part2.bib or refs_modern.bib. See Section 7.
11. **Spec 16.1 items not modeled beyond parameters:** state and nonprofit ownership (optional, not treated); reputational and regulatory exposure to layoffs (enters only through b_fam-type preferences); dividend and buyback expectations (only as reductions in the cash budget); SBC and dilution tolerance (equity pay at fair value in w_j).
12. **Small-share weight can be unbounded at low rates.** With Part I's worked-example firm (v_0 = 10 at r = 0.10), eq:gordon has no root below r of about 9.1%, so at the continuous WACC of 8.93% v_0 is infinite. The example therefore uses a lower demand pull (lambda = 0.0535, v_0 = 8 at the WACC, 10.8 at the family rate). The engine must handle "no root" (use the HJB at the firm's share).

---

## 6. Dependencies and coordination

- **Invoice chain voided (coordinator, mid-task).** No number in theory_regimes.tex or the verify script uses the core's invoice chain now. The transition examples use **Case R**, stated with its inputs in the text (T_par = 0.17 yr from params `parallel_run_T_par_years.ai_agent_shadow_mode`, grounding b; T_A = 4 from `amortization_years_T_A`, grounding b; omega_par 0.8 and nu_rec 0.1 from params, grounding d; the rest assumed). The capital-switch example is my own case ($0.60 per unit on $1.50 of capital, delta_K = 1/3, 120,000 units), not the core's.
- **Single source now read.** Verify section H reads `data/examples/invoice_chain.json`, block `transition` (W, F, I, C_J, C_par, C_str, C_wo, varpi_p, bbar_p, T_det, L_roll, T_par, T_h, r), at run time; nothing is hard-coded. H0 checks that eq:tasks-npv as implemented here reproduces the core's NPV; H1 evaluates the chain under every regime (closed form against the outcome tree) and asserts that no regime values it above zero whenever its run-rate saving is negative. If the JSON is missing the loader prints `[SKIP] H1`. No sentence in theory_regimes.tex quotes the chain, so no `\ic` macro is needed. Last run (2026-10-29 11:47 -0700): JSON version 2026-10-29b, file mtime 11:35:56, r = 0.08929 (continuous), W = -212,586, F = 2,807,916, T_h = 4; core NPV -3,904,756 reproduced exactly (H0). H1 regime values: public -3,904,756, family -3,912,606, PE at h_x = 1 -4,312,667, PE at h_x = 0.5 -4,067,577, VC -4,615,529. SUMMARY 83/83. Every earlier state of the JSON on the same day (W from -176,292 to -217,578) gave the same sign and the same ordering (public > family > PE at h_x = 0.5 > PE at h_x = 1 > VC), so no regime result depends on which version is current; a later revision needs only a rerun.
- **For the core theorist:** the single source was regenerated at r = 0.0893 (continuous), consistent with the conversion rule.
- **Acquirer section (coordinator, 29 Oct 2026).** tab:reg-presets has a permanent-capital row cross-referencing ass:acq-pc and prop:acq-pc; ass:reg-lbo and prop:reg-lbo now state that the buyer transforms with the target's own capability, relaxed by prop:acq-owner, whose eq:acq-pmax adds Delta V^cap_o / P_0 to p^max. Verify I1 checks the row's numbers and conversions; I2 checks them against part2/tables/acquirer_macros.tex (skipped if the file is missing); the row's debt rate uses `\acqRdebt`, `\acqNotesUsdC`, `\acqNotesEurC` and `\acqNotesUsd`/`\acqNotesEur`, so theory_regimes.tex now inputs part2/tables/acquirer_macros.tex at its top (all `\providecommand`). The compiled document needs part2/refs_acquirer.bib in the bibliography and theory_acquirer.tex for these labels. Open item for the acquirer owner: replace vartheta_pc and vartheta_dc with frak w_pc and frak w_dc.
- **Assumptions memo items 6 to 8:** entry multiple = exit multiple in every IRR (14x in and out for the metrics example; the multiple paid, 18.2x, for the take-private); h_x shown at 0.5 and 1 in tab:reg-rank, prop:reg-metrics and prop:reg-lbo examples; every example labeled illustrative and conditional; covenant status updated to the supervisory floor.
- **For the lead author:** at h_x = 0.5 the archetype flip for K disappears (K = -0.33) and P turns negative for the sponsor (-0.26); the capital-switch example (ratio 0.40) survives, because zeta^pe = 0.385 at the converted hurdle (it did not at the unconverted 22%). State these as conditional on buyers capitalizing seasoned run-rate.

---

## 7. Literature

Cited (keys exist): kaplan2005private, harris2014private, kaplan2009leveraged, guo2011do, bharath2014do, bernstein2016operational, stein1989efficient, graham2005economic (survey, flagged in text), asker2015corporate, villalonga2006how, chava2008how, cochrane2005risk, korteweg2010risk, babina2024artificial (refs.bib), and from `part2/refs_modern.bib`: eisfeldt2023generative (WP, labeled), terry2023macro, richards2024managing (WP), davis2019heterogenous (WP). From `part2/refs_regimes.bib` (new): axelson2013borrow, gompers2016what, gompers2020how, damodaran2026cost (data set), silverpeak2026software (practitioner, flagged).

Modern pairing: stein1989efficient and graham2005economic with terry2023macro; kaplan2009leveraged and guo2011do with davis2019heterogenous; bernstein2016operational with richards2024managing; AI and firm values: eisfeldt2023generative and babina2024artificial. Unpaired older keys, kept as canonical: chava2008how (covenants), villalonga2006how (family firms), cochrane2005risk and korteweg2010risk (venture returns), asker2015corporate (public versus private investment). The modern map reports no verified study of AI adoption by ownership regime or of public versus private investment in AI; the text says so. herkenhoff2025private is relevant (efficient reallocation by PE) but not cited, for space.

Added and verified (29 Oct 2026) in `part2/refs_regimes.bib`, cited in the presets paragraph and Table tab:reg-presets:
- **axelson2013borrow**: J. Finance 68(6), 2223-2267, doi 10.1111/jofi.12082 (EconPapers record). Figures read in the authors' final version (personal.lse.ac.uk/axelson/ulf_files/AJSWfinalversioncombined.pdf): 1,157 buyouts 1980-2008; Table III, all LBOs, total debt/EBITDA mean 5.6, median 5.2 (N = 1,142); EV/EBITDA median 7.6; D/EV median 0.70. Table IV (net debt) gives a median of 5.1 and quartile medians 6.1 to 4.2 by high-yield spread. **Flag:** 5.2 is total debt; for a net-debt covenant the net median 5.1 is the matching figure (the example keeps the parameter file's 5.2; the difference is 0.1 turn).
- **gompers2016what**: JFE 121(3), 449-476, doi 10.1016/j.jfineco.2016.06.003. Read in NBER w21133: "PE investors typically target a 22% internal rate of return on their investments on average"; median target IRR 25%; "the vast majority of target rates of return between 20 and 25%"; median target MOIC 2.5, mean 2.85; almost 96% use a five-year forecast horizon. Survey of 79 investors. The abstract adds that investors expect to add value "with a greater focus on increasing growth than on reducing costs"; the text now says so in prop:reg-weight's intuition.
- **gompers2020how**: JFE 135(1), 169-190, doi 10.1016/j.jfineco.2019.06.011. Read in the NBER conference version: "The average required IRR is 31%"; late-stage and larger VCs 28 to 29%; median required multiple 5, mean 5.5; 889 respondents (the published abstract says 885 VCs at 681 firms), surveyed November 2015 to March 2016.
- **damodaran2026cost**: on disk, `data/raw/damodaran_2026/wacc.xls`, sheet "Industry Averages", date updated Excel serial 46027 = 5 January 2026; Software (System & Application), 309 firms, cost of capital 0.09344; Information Services 0.06996; Software (Internet) 0.10659; total market 0.06964. Practitioner data set (annual rates).
- **silverpeak2026software**: the PDF is reachable at the URL in the data log, but its disclaimer says it "does not carry any right of publication". Verified quote: EV/EBITDA "remain within the historical 12-17x band". The 14.9x average in the data log could not be confirmed (the chart labels are ambiguous). Kept as flagged practitioner data with access date 29 Oct 2026; the preset 14 (10 to 17) is described as within the 12 to 17 band, with the lower bound 10 assumed for a stressed exit.

Still missing (not added): Interagency Guidance on Leveraged Lending, SR 13-3 (2013), for the covenant floor (the data agent read it; the text only says "supervisory precedent"); an exact-penalty reference for prop:reg-dip(c) (the proof is self-contained).

---

## 8. Changes after converting annual presets to continuous rates (coordinator follow-up 1)

| Item | Before (annual used as continuous) | After (ln(1 + r)) | Conclusion |
|---|---|---|---|
| Archetypes Q, P, K: public / family / PE (h_x 1) / PE (0.5) / VC | Q 8.22/8.12/4.60/2.73/5.88; P 8.74/9.12/2.82/-0.92/6.09; K -0.93/-0.55/1.72/-0.71/-1.64 | Q 8.71/8.55/5.27/3.15/7.93; P 9.67/9.95/3.98/-0.26/9.90; K -0.79/-0.40/2.43/-0.33/-1.02 | rankings unchanged (P > Q > K except PE: Q > P > K); K positive only for PE at h_x = 1 |
| r^dagger vs WACC | 9.9% vs 9.34% | 9.9% vs 8.93% | flip now about one point above WACC |
| zeta^pe (h_x 1; 0.5) vs r_w + delta_K | 0.30; 0.41 vs 0.43 | 0.28; 0.385 vs 0.42 | **changed:** the 0.40 capital switch now pays the sponsor even at h_x = 0.5 (+$15k; +$168k at h_x = 1; -$46k at WACC) |
| Growth weights (fam, pub, myopic, PE mid-hold) | 11.5, 8, 6.15, 2.55 | 10.8, 8, 6.15, 2.70 (lambda recalibrated to 0.0535) | ordering unchanged |
| X^dagger (growth engine vs 1-point cost-out) | 5.81 (myopic 6.15 above) | 6.85 (myopic 6.15 below; gain 0.86 < 1) | **changed:** the assumed earnings pressure now reverses the public firm's ranking |
| Case R | IRR 15.0%; NPV +357k / -306k; T_h* 7.1 yr | IRR 15.0% (16.2% annual); NPV +388k / -226k; T_h* 7.0 yr | unchanged: clears WACC, fails the hurdle |
| Volume threshold over straight line (T_A = 4) | +19.8% / +50.4% | +18.9% / +45.0% | |
| Start timing (P) | yield 0.14 < 0.22; 2.82 -> 3.26 | yield 0.15 < 0.199; 3.98 -> 4.24 | unchanged (bang-bang) |
| Buyout 14x in and out (h_x 1; 0.5) | 2.46 (16.2%), LP 1.93 (11.6%); 2.14 (13.6%) | 2.47 (16.2%), LP 1.94 (11.7%); 2.16 (13.7%), LP 1.72 (9.4%) | small change (debt 7.7%) |
| Take-private (exit at the multiple paid) | 16.5x; p_max -4.8% / -11.8%; break-even 14.0% / 11.7% continuous; frakL 295, frakD -825 | 18.2x (firm now 14.0x at 8.93%); p_max -0.4% / -8.3%; break-even 13.5% / 11.3% continuous (14.4% / 11.9% annual) vs 19.9% (22% annual); frakL 270, frakD -798 | unchanged: fails at the survey hurdle at both h_x |
| Frictionless take-private | -0.4% (slower), 37% (blocked) | -0.5%, 37% | unchanged |
| Growth-weight loss of the ownership change | 3.28 points | 2.41 points | |
| VC weight X^x(7) | 6.11 | 7.93 | |
| Carve-out (Case R) | +735k; T_h* 7.1 -> 2.8 | +735k; 7.0 -> 2.8 | |
| Myopia penalty (Case R year 1) | $79k | $80k | |
| Dip budgets, waves, covenant, EPS | unchanged (no discount rates) | unchanged | |

## 9. Verification summary

`python3 code/verify_part2_regimes.py` -> `SUMMARY: 83/83 checks passed`.

- A (15) regime value: symbolic capitalization and patience; outcome-tree identity on fixed and 100 random transitions; single crossing; archetype table at h_x = 1 and 0.5; family 30-year variant; r^dagger; zeta^pe sign test (3,000 draws) and examples; myopia penalty on Case R.
- B (12) growth weights: v_0 decreasing in r (300 draws); no root at the continuous WACC for Part I's worked-example firm (roots only above about 9.1%); myopic reformulation (symbolic) and argmax (300 draws); factors and loss; X^x(tau) (sympy integral); frontier ordering and numbers; X^dagger.
- C (13) pace: a(r,T) monotone; volume-threshold ratio; single-sign-change monotonicity (500 draws); Case R IRR, NPVs, T_h*; adoption date; bang-bang start (symbolic and 500 draws); payback bound (2,000 draws); kappa_hat; deadline.
- D (18) dip budgets: covenant equivalence (3,000 draws); fastest-ramp dominance against all compositions (150 instances); linear closed form (symbolic) and optimality (150 instances); public and covenant examples by enumeration; KKT multipliers and exact-penalty threshold (continuous); integer switch points; revealed-preference monotonicity (200 instances); exact covenant with interim cash; squeeze and cures.
- E (7) metrics: waterfall against sequential distribution (3,000 draws); LBO identity (200 draws); 14x-in-and-out example at h_x = 1 and 0.5; amplification; EPS paths; first-order Delta R*_o at each regime weight.
- F (7) take-private: frictionless benchmark (both cases, 100 draws); example at the multiple paid, h_x = 1 and 0.5; decomposition; revealed preference (300 plan sets); growth-weight loss.
- G (6) hybrids: dual class; PIPE versus GAAP budget; weighted weight (300 draws); carve-out on Case R; Lemma valuation2 derivative identity (symbolic); VC weight.
- H (2) single source: H0 reproduces the core's NPV; H1 regime values of the invoice chain (closed form = outcome tree; none positive).
- I (3) permanent-capital row: values and ln(1+r) conversions in the tex row (I1); agreement with the acquirer macros (I2); symbol guard, no vartheta in the regimes files and frak w in no other Part II file except the acquirer section (I3).
