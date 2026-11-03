# Theory extension notes (Part II, spec Sections 5, 6, 7, the program parts of 13 and 14, 15, the gating part of 18, the portfolio and governance part of 23, and the plateau scenario of 24.2)

Files:
- `part2/theory_ext.tex`: `\section{Constraints, Dynamics and Organization}\label{sec:ext}`.
- `part2/proofs_ext.tex`: `\section{Proofs for Section~\ref{sec:ext}}\label{app:proofs-ext}`.
- `code/verify_part2_ext.py`: 141 checks, all passing (H0 added 29 Oct for the support example and tax text; BASE ψ rebased to 1) (`python3 code/verify_part2_ext.py`, about 20 s, exit code 0 iff all pass). Every number quoted in the text is printed with `->` and asserted. Check H1 parses Table `tab:ext-tornado` directly from `theory_ext.tex`, and H2 and H3 look for the quoted waterfall and Shapley strings in the tex, so the table and text cannot drift from the script.

Build status (29 Oct, scratch build with Part I's `paper.tex` preamble, `sections/model.tex`, `part2/theory_core.tex`, this section, `sections/appendix_proofs.tex`, `part2/proofs_core.tex`, `part2/proofs_ext.tex`, `\bibliography{refs,part2/refs_part2}`): no errors, no undefined citations, no overfull boxes, no multiply defined labels. The only undefined references are Part I sections outside the harness (`sec:empirics`, `sec:horizons`, `app:protocol`). The section runs about 25 pages (pp. 35 to 60 of the test build) and the proofs about 11.

The slot for the IO theorist's adoption game (`part2/theory_competition.tex`, `\label{sec:ext-game}`) is a commented `\input` at the end of Section `sec:ext-competition` in `theory_ext.tex`. Uncomment it once the file exists (do not also input it from `paper.tex`, or its labels will be defined twice).

---

## 1. Results (labels)

**Setting and universe (spec 5)**
- `ass:ext-cost` (mode cost split; mode A at the core's quality cost c^Q, and under the failure taxonomy also approval hours and misbehavior loss), `ass:ext-theta` (Θ: taxes, regulation, ethics and religion, altruism, customer preference), `def:ext-effcost` (effective unit cost, automation advantage B_j).
- `def:ext-universe` (four nested layers), `lem:ext-nested` (nesting, waterfall, preferred layer independent of AI prices).
- `prop:ext-statics` (monotone statics; τ_L, ϑ, τ derivatives; payroll tax, altruism and displacement-tax equivalence), `tab:ext-statics`.
- `prop:ext-margin` (spend share fragile, value robust; envelope; density formula; convexity).
- `prop:ext-customer` (customer penalty weighted by the marginal q of revenue).
- `cor:ext-floor` (activity-level accountability floor).
- `def:ext-tornado`, `prop:ext-shapley`, `tab:ext-tornado`.

**Dynamics (spec 6, 24.2)**
- `ass:ext-capability` (horizon, reliability, context, physical lag, prices; plateau scenario H(t) = H(min{t, t_p})).
- `prop:ext-feasible` (a) to (e) feasibility dates, reliability lag, context, probit S-curve, scaling; (f) plateau.
- `prop:ext-energy` (energy and fusion), `prop:ext-agi` (unbounded capability; failure-rate caveat and c_err).
- `prop:ext-timing` (a) to (f) adoption date, option value, closed forms, lock-in, parallel run and break fees; (g) plateau.

**Competition (spec 6, 24.2)**
- `lem:ext-retained`, `ass:ext-entrant`, `def:ext-motives`, `prop:ext-should` (a) to (e); (f) plateau. Slot for `sec:ext-game` after the intuition paragraph.

**Organization (spec 7)**
- `ass:ext-team`, `prop:ext-team`; `ass:ext-hierarchy`, `prop:ext-hierarchy`; `def:ext-org`, `lem:ext-staffing`.

**Program (spec 13, program level)**
- `ass:ext-program`, `prop:ext-waves` (order, front-loading, square-root rule, change capacity, big bang, score path).

**Portfolio, common mode and bandwidth (spec 14 program level, 18 gating, 23 portfolio and governance)**
- `ass:ext-portfolio`, `prop:ext-portfolio` (a) learning on the process factor ϖ^c, (b) common platform, (c) correlation, (d) heavy tails, (e) provider concentration.
- `ass:ext-commonmode`, `prop:ext-commonmode` (a) concentration, (b) diversity and redundancy, (c) scale against diversification (`eq:ext-providers`), (d) staged updates and rollback, (e) kill switches and decision rights.
- `ass:ext-bandwidth`, `prop:ext-bandwidth` (load breakpoint, pace, value of bandwidth, AI-assisted analysis, delegation, waves with congestion).
- `rem:ext-seccap`: decision bandwidth Φ, security review Φ_sec (core `prop:tasks-secreview`, `eq:tasks-secvalue`) and change capacity: binding constraint and shadow value of each, smooth and hard-cap cases.

**Regime shocks (spec 15)**
- `ass:ext-shocks`, `prop:ext-shocks` (value under hazards, tenure breakpoint, sequencing, vision-agnostic investment), `prop:ext-continuity` (context continuity, commitment devices, bandwidth and capacity under freezes, waves under freezes and decoupled streams).

**Breakpoints (spec 8 items 6, 7, 9 and the program, tenure, freeze, provider and staging thresholds)**
- `prop:ext-breaks` (a) to (i), `tab:ext-limits`.

Spec 15.3 coverage: program value under hazards and the payback-heavy loss (prop:ext-shocks(a)); tenure breakpoint and front-loading of quick, durable wins (prop:ext-shocks(b), (c)); value of robustness and vision-agnostic investment (prop:ext-shocks(d)); value of context continuity (prop:ext-continuity(a)); commitment devices as options, binding and gated (prop:ext-continuity(b)); interaction with decision bandwidth, change capacity and wave structure, including the condition under which freezes favor fewer waves and the value of decoupled streams (prop:ext-continuity(c), (d)). Each has a proof and checks I1 to I16.

---

## 2. Notation and deviations from the spec

| Spec symbol | Used here | Reason |
|---|---|---|
| μ (mode) | x ∈ M = {H, O, A, U, N}; AI modes {A, U, N}; non-AI modes {H, O} | μ is reserved (pull multiplier); x as in the core |
| θ (parameter vector) | Θ; a scalar component is θ or θ_k | θ is reserved (margin persistence) |
| b (altruism per job) | ϑ, after-tax $ per own employee hour retained | b is Part I's capital per unit of output; ϖ is now success probability; ω is used for ethics penalties and by the core (ω_par); ϑ was the only Greek letter unused in Part I, the core and this section |
| ψ_A (review fraction), ψ_min | ξ_j (core), ξ^min(c_j) by firm-mapped class c ∈ {0,1,2,3} | ψ is Part I's deductibility; the EU AI Act has no numeric review share |
| ψ_A w t + ε_A L in c_A | the core's quality cost c^Q_j (prop:tasks-review), split into review hours t_A = ξ*_j t^R_j and loss c^ext_A; with the failure taxonomy, c^Q of prop:tasks-halluc plus approval hours t_j(a*) and misbehavior loss c^m_j(a*) (prop:tasks-autonomy) | the core's harmonized form; the split is needed because payroll taxes and altruism act on own hours only |
| π_p (success) | ϖ_p, ϖ_pj, ϖ^c_p, ϖ^0_p (core), ϖ^gate; wave-level ϖ_k; initiative-level ϖ^0_i | π is the inference price only |
| H(t) κ_ctx ≥ d χ(r̄) | 𝓗 ≥ d̄_j, 𝓗 := H(t − L_W ph_j), d̄_j := d_j χ(q̄^A_j)/κ_ctx,j | as in the core; note the core writes χ(r̄^A_j) in the paragraph after eq:tasks-success, which should read q̄^A_j (r is the discount rate) |
| ξ (context share) | s^ctx_j | ξ is the review share |
| p_fail | (1 − ϖ_p) e^{−T_par/T_det} (core rollback model) | |
| A(θ), S_A(θ) | 𝔸(t,Θ) = J^eco; shares Σ^fea ≥ Σ^per ≥ Σ^pre ≥ Σ^eco; value 𝒱^eco | 𝒜_T is Part I's annuity factor; S is revenue; Σ^eco extends the core's S_A(π) to all AI modes and to Θ |
| δ_H | δ^G (retention) and δ^λ (demand pull), weighted by X̂ = [X − (1−ψτ)k]/(1−τ) | maps to Part I's envelope |
| F_A/(v T_A) | F a(r,T)/v with a(r,T) = r/(1 − e^{−rT}) | allowed by the core; tends to 1/T as r → 0 |
| τ_A "on c_A" | excise on AI spend and AI capital, deductible | review labor should not bear an automation tax |
| χ (team), χ(r̄) | χ(q̄) for reliability; χ_h, χ_a per human and agent pair | spec uses χ twice |
| y in Y(n) | scope 𝒲_0 in unaided person-years | y = X − k in Part I |
| n | n humans, n_a agents, n_c Cournot firms, n_w waves, n_k wave size | |
| D(n) dual-running cost; d_1, d_2 | C^dr(n) = c^dr_1 n + c^dr_2 n² | D is reserved (Macaulay duration); d_j is task length |
| s_p, s (savings) | W_p, W (the core's annual saving W); timing uses the savings flow W(t) = v(t)[c_0(t) − c^var_A(t)] | s is reserved (market share), S is revenue |
| wave duration D_k | T_k | D reserved |
| Lagrange multipliers μ_k | ζ_k | μ reserved |
| h_L, h_V, h_R, h_K | ν^L, ν^V, ν^R, ν^K; disruption rate ν_D = ν^L(1 − κ_keep) + ν^V; r_D = r + ν_D | h is reserved (headroom) |
| ϑ_reuse | s^reuse | ϑ is altruism here |
| C_replan, T_freeze | C^rep, T_frz | |
| Φ_sec, latency | the core's Φ_sec, ν (deployments a year), V_dep, D_sec, p_sec; Q_sec(n) := (Φ_sec − ν)/(Φ_sec − ν + r_d) with ν = n/T_par | core prop:tasks-secreview |
| common-mode failure (23.1 iv) | ν^cm (event rate per provider), exposure x_p, X, X_m, concentration H := Σ(X_m/X)², fallback capacity Y_f, T_con = T_mon + T_resp, failover residual κ_fo, kill-switch response T_ks, providers M, per-provider fixed cost F_M, volume-discount elasticity b_v, single-provider inference spend C^inf, staged-release share η_c, delay cost δ_c, update value B_up, soundness p_g, rebuild time T_reb | new |
| Φ (decision bandwidth), ℓ_dec, b_p | kept as the spec and core write them | Φ clashes with Part I's envelope Φ(g) and ℓ is reserved; flagged |

Other symbols: ŵ = w⁰(1+τ_L) − ϑ/(1−τ); Υ = (1−ψτ)/(1−τ); 𝒞_{x,j} customer penalty; t̄_x total own hours; ĉ^Q_j quality cost at the wage ŵ; n^dbl_j doublings still needed; ς_dbl their dispersion; L_W world-model lag; ph_j physical flag; s_E, ε_E, δ_en, δ_hw energy; p_sw, rep, φ̄ (level pass-through), 𝓔^eq, 𝓔^priv(n_r), 𝒦, 𝒟 (viability deficit), 𝓡_ι, 𝓡_leg, 𝒯_j, Y_I, T_M competition; A_g = t/t^U, ν̄_a, ν_a, Λ, 𝒲, ξ^t = ξ t^R/t teams; z, z_w, z_m, c_K, κ_c, sp*, z_A, ζ_P hierarchy; O_w, K_chg, n_cap program; υ_L, E_k (experience; not the spend E_j), δ_E, η_tr, p_P, ζ_T, H_n portfolio; Q(ϰ) = q(ϰ) e^{−r_d ℓ_dec(ϰ)}, ϰ̂, ε_Q, A_Φ, e^appr, e^prep, p_Φ bandwidth; n̂_2, ν̂_sec, n̄ remark; V^pay(τ), V^rec, T_emb, 𝔪 (context stock), κ_doc, η_K, L^ctx, n_K, P_V, p_inf, V^+, V^−, O^re_w, n_s shocks.

---

## 3. Where the spec, or a request, is wrong or underdetermined

1. **Adoption rule (spec 6).** "Adopt when the savings flow exceeds (r + δ_F) F_A + the expected cost decline" holds only under vintage lock-in. When AI is paid as used, the rule is savings flow ≥ (r + δ_F) F_A (prop:ext-timing(b), (e)).
2. **Capability plateau (spec 24.2, coordinator request).** "The option value of waiting falls" holds under vintage lock-in (prop:ext-timing(g)(ii)) but not under pay-as-you-go pricing. There, early adoption loses as much from a plateau as adoption at t_p, so the plateau delays adoption (or prevents it) and the measured gain from waiting, max_T O(T) − O(0), weakly rises (prop:ext-timing(g)(i); checks K2 and K3). A plateau also does not by itself make a non-viable incumbent viable: viability depends on its readiness and legacy gaps relative to the entrant at the same capability (prop:ext-should(f)(iii)). What the plateau does do is delay or remove the market flip, so defensive automation may become unnecessary.
3. **Team objective (spec 7).** Y(n) = n A_g y − χ n(n−1)/2 has no objective. With a fixed scope the solo 10x result follows; with unlimited demand the profit-maximizing team grows with A_g (prop:ext-team(f)). The pairwise form n(n−1)/2 is an assumption, motivated by, not taken from, Becker and Murphy and Brooks.
4. **"The incumbent keeps only (1 − φ) of its savings."** Savings that rivals replicate pass through; after an AI-native entrant sets the price the incumbent keeps all of its own savings and it is the margin level that collapses (lem:ext-retained, prop:ext-should(b)).
5. **Payroll taxes and altruism (spec 5).** Their sign is not determined: it depends on whether the best non-AI mode is in-house work or outsourcing. In the synthetic population a higher τ_L lowers Σ^eco but raises 𝒱^eco.
6. **ψ_min by risk class.** A modeling device for Article 14 oversight; the classes are the firm's mapping; Art. 6(3) puts a boundary between modes U and A (to be confirmed on EUR-Lex by the literature agent).
7. **"Preferred" layer** was undefined; defined as "an AI mode wins if inference and integration were free".
8. **Spec 13, dual-running budget.** A hard budget per period is a cap on wave size, n_k ≤ C^dr^{-1}(budget), and enters like n_cap.
9. **Spec 14 and 18, notation.** Φ clashes with Part I's Φ(g); ℓ_dec with reserved ℓ; b_p with Part I's b. Kept as written by the spec and the core; the lead author should decide.
10. **Spec 15.5.** Myers and Majd (1990) could not be verified; Berger, Ofek and Swary (1996) and Trigeorgis (1996) are cited instead. No evidence links reorganizations to initiatives in flight, so T_frz and O^re_w are assumptions.
11. **Spec 23.1 (iv) and the core's c_err.** c_err (eq:tasks-cerr) counts expected losses that are independent across activities. The expected common-mode cost of prop:ext-commonmode(a), divided by revenue, is a further cost of the same kind in Part I's ceiling; the Part I integration theorist should add it next to c_err.
12. **Section 18 gating.** With smooth congestion (queues), decision bandwidth and security review are not Leontief: each lowers the other's breakpoint, and both have positive shadow values whether or not change capacity binds. Only with hard caps does a single scarcest capacity carry all the value (rem:ext-seccap).

---

## 4. Formulas the engine must implement

Units: dollars per unit of work unless stated; volumes in units a year; time in years; rates per year; FTE; probabilities in [0,1]. The verify script contains reference implementations: `review`, `quality_cost`, `loss_frac`, `mode_costs`, `advantage`, `layers`, `shares`, `shapley`, `W_path`/`O_payg`/`O_lock` (timing with a plateau), `Epriv`/`Eeq`, `nnum` (team size), `wave_cost`, `Cstar` (relaxed wave problem with caps), `EV2`/`opt2`/`Qsec`/`eps_sec`/`nu_hat_sec` (two review capacities), `cm_mean`/`cm_var`/`J_cost`/`M_rule`/`ev_stage`/`eta_star` (common mode), `Vshock`, `seq_value`, `sim_m`. Core formulas that these use are in `notes/theory_core_notes.md` Section 4 and are referenced, not repeated.

### 4.1 Effective unit cost and the universe (module `universe`)

Inputs per activity j: v, t, w⁰, w^{L0}, lic, t^L, class c ∈ {0,1,2,3}, customer-facing flag; O: p_O, κ_O, ζ_O; A: πn, t^R, e (raw error rate, from readiness and capability, 4.2), L, ε̄ = 1 − q̄, F_A, T_A, K_A, δ_K; with the failure taxonomy also e^o, e^h, d^o, d^h, autonomy levels with t_j(a), e^m_j(a), d^m_j(a), L^m_j(a), L^cap_j(a), tail index p (core 4.13); U: t^U, πn_U, F_U, K_U; N: L^N, F_N; exclusion flags per AI mode; penalties ω_x. Per firm: X (= v'(s) from Part I), k, Δ*, S, r. Θ: τ_L, τ, ψ, τ_A, ξ^min(c), ϑ, δ^G_{x,j}, δ^λ_{x,j}.

```
w_hat   = w0*(1+tau_L) - vartheta/(1-tau)          # same form for the licensed wage w_hat_L
Ups     = (1 - psi*tau)/(1 - tau)
psi_SL  = (1 - exp(-r*T_R))/(r*T_R)                # straight-line deductions over T_R years (continuous)
psi_mid = [1 + (1+r)^-T]/(2T) + [1 - (1+r)^-(T-1)]/(rT) # statutory midpoint convention; psi_15 = 0.532 at r = 0.10
psi     = 1 - s_for (1 - psi_15)                    # software development with foreign share s_for (174A domestic, 174 foreign)
a(r,T)  = r/(1 - exp(-r*T))
cK_x    = (r + delta_K)*K_x + F_x*a(r,T_x)/v        # AI modes only
X_hat   = (X - (1 - psi*tau)*k)/(1 - tau)
C_x     = X_hat*(delta_G_x + Delta_star*delta_lam_x)*S/v      # AI modes, customer-facing only
# mode A quality cost at the effective wage (core eq:tasks-xi and prop:tasks-review), base case:
xi_E    = exp(-w_hat*tR/(e*L));  xi_R = max(0, 1 - epsbar/e);  xi = min(1, max(xi_E, xi_R, ximin[c]))
cQ_hat  = w_hat*tR*xi + e*L*(1 - xi*(1 + ln(1/xi)))      # (1 - xi(1+ln(1/xi))) = 1 at xi = 0
h_A     = xi*tR  [+ t_j(a*) under the taxonomy]           # own hours of mode A (envelope: d cQ_hat/d w_hat = h_A)
#   with the taxonomy: cQ from core prop:tasks-halluc (catchable rate, review-proof floor) and
#   + c^m_j(a*) from core prop:tasks-autonomy, both at w_hat; choose a* and xi jointly at w_hat
ct_H = w_hat*t
ct_O = p_O + zeta_O + w_hat*kappa_O*t
ct_A = cQ_hat [+ w_hat*t_j(a*) + c^m_j(a*)] + lic*w_hat_L*t_L + (1+tau_A)*(pi*n + Ups*cK_A) + omega_A/(1-tau) + C_A
ct_U = w_hat*tU + (1+tau_A)*(pi*n_U + Ups*cK_U) + omega_U/(1-tau) + C_U
ct_N = L_N + (1+tau_A)*Ups*cK_N + omega_N/(1-tau) + C_N          # not permitted if lic = 1
Class 3: drop A and U. Exclusions: drop the listed (j, x). Displacement tax T_D per displaced hour: add T_D*(t - own hours)
  to every mode and choose xi at w_hat - T_D (equivalent to vartheta = (1-tau) T_D).
B_j   = min_{x in {H,O} ∩ M_j} ct_x - min_{x in {A,U,N} ∩ M_j} ct_x     (-inf if no AI mode)
B0_j  = same with pi*n, pi*n_U and every cK set to 0 for the AI modes
```

Layers (all with M_j the feasible and permitted modes): fea (some AI mode feasible: capability test 4.2 and ι ≥ ι_min, the core's feasibility floor); per (some AI mode feasible and permitted); pre (per and B0 > 0); eco (per and B > 0). Spend weights E_j = v_j w_j t_j, fixed. Outputs Σ^• = Σ_{j∈•} E_j/Σ E_j; 𝒱^eco = Σ v_j max(B_j, 0) a year; waterfall (1 − Σ^fea, Σ^fea − Σ^per, Σ^per − Σ^pre, Σ^pre − Σ^eco).

Diagnostics at unique minimizers x0 (non-AI) and x1 (AI), with own hours t_x (mode A: h_A at its optimal share):
- ∂B/∂τ_L = w⁰(t_x0 − t_x1) + w^{L0}(t^L_x0 − t^L_x1); ∂B/∂ϑ = −(t̄_x0 − t̄_x1)/(1−τ);
- ∂B/∂τ = −[(1+τ_A)(1−ψ)cK_x1 + ω_x1 + ϑ(t̄_x0 − t̄_x1) + δ_x1 (S/v)(X − (1−ψ)k)]/(1−τ)²;
- oversight floor at which j leaves: root of cQ_hat(ξ) − cQ_hat(ξ*) = B_j on (ξ*, 1]; report the bound ξ* + B_j/(ŵ t^R) beside it (exact if the loss does not fall with review); d cQ/d ξ_min = ŵ t^R − eL ln(1/ξ_min) where the floor binds;
- class move c → c': J_j = cQ_hat(ξ^min(c')) − cQ_hat(ξ*) (if positive) + (1+τ_A)Υ c^K_conf; where U is exempt, value loss min{J_j, ct_U − ct_A};
- customer breakeven δ^{G*} = B_j v_j/(X̂ S).

Tornado: for each parameter k, (Σ^eco, 𝒱^eco) at (θ_k^lo, Θ⁰_{−k}) and (θ_k^hi, Θ⁰_{−k}); sort by the range of 𝒱^eco and show the share range beside it.

Shapley over n_g parameter groups (2^{n_g} evaluations; n_g ≤ 10): Sh_k = Σ_{T ⊆ G∖{k}} |T|!(n_g−|T|−1)!/n_g! [f(T∪{k}) − f(T)], f = Σ^eco or 𝒱^eco. The Sh_k add up to the total change exactly.

Activity-level floor (cor:ext-floor): per revenue dollar, [Σ_{j∈per} v_j(w_j ξ^min(c_j) t^R_j + lic_j w^L_j t^L_j [+ w_j t_j(a*)]) + Σ_{j∉per} v_j c_{x0,j}]/S, split by function into c_h^min (cost of revenue) and the a_min part; ∂R_max/∂ξ^min(c) = −(1−τ) Σ_{j: c_j = c, floor binds} v_j w_j t^R_j/S. Any remaining c_err (core eq:tasks-cerr) and the common-mode cost of 4.8 enter the ceiling separately.

### 4.2 Capability, prices, energy (module `dynamics`)

```
H(t)      = H0 * 2**((min(t, t_p) - t0)/T_d)          # t_p = +inf without a plateau; T_d range 143-240 days
chi(q)    = (q/(1-q))**eta_r                          # eta_r in [1.00, 1.29], default ln5/ln4 = 1.161
kappa_ctx = 1/(1 - s_ctx*iota*C)
dbar_j    = d_j*chi(qbar_A_j)/kappa_ctx_j
Hcal_j(t) = H(t - L_W*ph_j)
feasible_A(j,t) iff Hcal_j(t) >= dbar_j (and iota_j >= iota_min_j)       # U: same test with sub-task length
e_j(t)    = 1 - 1/(1 + (d_j/(kappa_ctx_j*Hcal_j(t)))**(1/eta_r))         # raw error rate fed to 4.1
n_dbl_j   = log2(dbar_j/H0);  T_F_j = max(t_now, t0 + T_d*n_dbl_j + L_W*ph_j)
plateau:  ever feasible iff dbar_j <= H(t_p); otherwise needs kappa_ctx multiplied by dbar_j/H(t_p)
reliability lag (years) = eta_r*T_d*log2(odds(q')/odds(q))
feasible share(t) = sum_g E_g * F_g((min(t - L_W*ph_g, t_p) - t0)/T_d)     # F_g: spend-weighted CDF of n_dbl
capability margin for the core's logit: ln(Hcal/dbar_j)
AI spend at fixed difficulty: c_mach_j(t) = c_mach_j(T_F_j)*exp(-delta_pi*(t - T_F_j)), starting at the frontier price
energy: c_mach = c_en + c_hw; s_E = c_en/c_mach;  eps_E fall in electricity price -> c_mach *= (1 - s_E*eps_E)
  equivalent years of trend = -ln(1 - s_E*eps_E)/delta_pi;  ds_E/dt = s_E(1-s_E)(delta_hw - delta_en)
  dR_max = (1-tau)*s_E*eps_E*c_c  (at given prices; competed away under free entry)
AGI limit cost of A: w_hat*ximin[c]*tR + lic*w_hat_L*t_L + (1+tau_A)*(c_mach_inf + Ups*cK_A) + omega/(1-tau) + C_A
  [+ review-proof and misbehavior losses if those failure rates do not vanish with capability]
```

A process becomes feasible at the latest T_F_j on its critical path (the core's percolation uses it).

### 4.3 Adoption timing (module `timing`), per process

Inputs: v(t), c_0(t) (best non-AI cost; falls if the vendor adopts AI), c^var_A(t) = c^Q(t) + π(t) n; transition components 𝒯_i(T) with decline rates δ_i (F_A at δ_F, capex K_A v, PV of the parallel run, expected stranded and rollback terms of core eq:tasks-npv with p_fail = (1 − ϖ_p) e^{−T_par/T_det}, break fee b_0(1 − T/T_c)_+); ramp ϱ over T_par; r; lock-in flag; plateau date t_p.

```
W(t)        = v(t)*(c0(t) - cvar_A(t))       # risk-adjusted: multiply by varpi_p*bbar_p
rho_bar     = int_0^{T_par} e^{-r tau} d rho(tau)          (linear ramp: (1 - e^{-r T_par})/(r T_par))
hurdle(T)   = r*T(T) - T'(T) = sum_i (r + delta_i) T_i(T)  [+ b0/T_c for T < T_c]
net(T)      = int_0^{T_par} e^{-r tau} W(T+tau) d rho(tau) - hurdle(T)    (constant W: rho_bar*W - hurdle)
  lock-in: net(T) -= v(T)*|d cvar_A/dT|/(r - g_v)    (after t_p only the price part of the decline)
T* = 0 if net(0) >= 0; else first T with net(T) >= 0 (grid plus bisection; check jumps at contract expiries); never if none
option value = O(T*) - O(0) = int_0^{T*} e^{-rt}(-net(t)) dt
closed forms: constant W: T* = max(0, ln((r+delta_F)F0/Wbar)/delta_F)
              delta_F = 0, cvar_A = c^Q + pi0 e^{-delta_pi t}: T* = max(0, ln(pi0/(c0 - c^Q - r F0/v))/delta_pi) if c0 - c^Q > r F0/v
plateau: from t_p, c^Q and feasibility stay at their t_p values (prices may keep falling); recompute W_p and rerun.
  Report both contract types: pay as you go (T* weakly later; never if W_p < (r+delta_F)F_A at all dates) and
  lock-in (option value of waiting weakly lower).
competition deadline for defensive processes: T*_def = min(T*, T_M - lead time)
```

### 4.4 Competition (module `competition`)

```
retained share when n_r of n_c - 1 rivals replicate: 1 - phi_bar = (n_c - n_r)/(n_c + 1) -> 1 - rep
commodity automation (unit margin mg, saving delta_c, annualized fixed cost K, slope B; need mg >= (n_c-1)delta_c/(n_c+1)):
  a = delta_c/(n_c+1);  E_eq = a(2 mg + a)/B;  E_priv(n_r) = n_c a (2 mg + (n_c - 2 n_r) a)/B
  value-creating if K < E_eq; defensive if E_eq <= K < E_priv(n_c-1); contested if E_priv(n_c-1) <= K < E_priv(0);
  not worth doing if K >= E_priv(0)
AI-native entrant: c_E(t) = full unit cost from module universe with iota = 1, no legacy, no stranded costs
  (under a plateau, recompute with capability frozen at t_p)
flip date T_M = first t with P_I > c_E(t) + p_sw (never if none: then no automation is defensive)
viability: c_I* <= c_E + p_sw;  gaps R_iota = sum_j [c*_j(iota_j^I) - c*_j(1)] v_j/Y_I, R_leg = legacy unit cost
NPV_j = (1 - phi_bar_j) B_j v_j/(r - G) - T_j   (with a path for B_j, discount the path)
defensive set if Def = c_I^vc - (c_E + p_sw) > 0: min sum(-NPV_j) s.t. sum B_j v_j/Y_I >= Def over j with B_j > 0
  (greedy by (-NPV_j)/(B_j v_j/Y_I), then integer repair); defend iff cost < franchise value
labels: value-creating | defensive | could-not-should (feasible, not VC, not in D*, or impermissible) | not feasible
  (above the plateau: not feasible for good)
```

### 4.5 Organization (module `org`)

```
team: W = W0*((1 - nu_a)/A_g + nu_a*xi_t),  A_g = t/t^U,  xi_t = xi*tR/t
  agents take all feasible work iff p_a/Y_a < w*(1/A_g - xi_t); else minimize C(nu) = w*n*(W(nu)) + p_a*nu*W0/Y_a on [0, nu_bar]
  n*(W) = W if W <= 1 else ((1+chi_h/2) - sqrt((1+chi_h/2)^2 - 2*chi_h*W))/chi_h; infeasible (split) if W > (1+chi_h/2)^2/(2 chi_h)
  coordination-adjusted wage w/(1 - chi_h*(n - 1/2)); leverage Lambda = 1/((1-nu_a)/A_g + nu_a*xi_t); solo iff W0 <= Lambda
  solo date: root of W(t) = 1 along the paths of nu_bar(t), A_g(t), xi_t(t); agent-pod cap (Y_a + chi_a/2)^2/(2 chi_a)
  unlimited scope: n_pi = 1/2 + (A_g - w/P)/chi_h
hierarchy: z_w* = ln(kappa_c (w_m + c_K z_m)/c_K); span sp* = (w_m + c_K z_m)/c_K
  AI layer at z_A: human workers per problem x e^{-z_A}; span (w_m + c_K (z_m - z_A))/c_K
  Pareto task lengths: e^{-z_A} = (H(t)/d_min)^{-zeta_P}; layers ~ ln N_w/ln sp*; calibrate c_K/w_m from the observed span
residual organization (t_FTE = 2080):
  production FTE = sum v_j t_prod/t_FTE (H: t; U: t^U); review FTE (senior) = sum_A v_j xi* tR/t_FTE [+ v_j t_j(a*)/t_FTE]
  sign-off FTE = sum v_j lic t_L/t_FTE; vendor management FTE = sum_O v_j kappa_O t/t_FTE; managers = workers/sp*
transformation team in wave k (duration T_k):
  DI engineers = l_DI*I_int_k/(w_DE*t_FTE*T_k); AI engineers = l_AI*F_k/(w_AI*t_FTE*T_k) + e_mnt*N_A_before_k
  process owners = e_PO*n_redesign_k; change managers = A_aff_k/(T_k*N_CM); risk/governance/audit = e_RG*n_regulated_k
  SMEs = e_SME*n_build_k; parallel-run staff = sum_{p in wave}(omega_par*FTE0_p + nu_rec*FTE_H_p)
  in-house headcount at ramp point tau: base - sum_done(FTE0 - FTE1) + sum_wave[omega_par FTE0 + nu_rec FTE_H - rho(tau)(FTE0 - FTE1)] + team
change capacity K_chg = min(kappa_abs*FTE_base, N_CM*FTE_CM_max)   (affected FTE a year)
```

### 4.6 Program and waves (module `roadmap`)

Inputs: processes p with W_p (annual saving once migrated), a_p (affected FTE), release dates T*_p from 4.3, precedence (data platform first); T_par; C^dr(n) = c^dr_1 n + c^dr_2 n² (includes the core's C^par per process and congestion); O_w; K_chg.

```
first-order cost  C = sum_k [T_par*k*sum_{p in wave k} W_p + T_par*C_dr(n_k) + O_w]   (engine: discounted version)
ordering: decreasing W_p (W_p/a_p when capacity binds), subject to precedence and release dates
given n_w (identical processes): n_k = N/n_w + (W/(2 c_dr2))((n_w+1)/2 - k), capped at n_bar (4.9) and at >= 0
C(n_w) = T_par[W N (n_w+1)/2 + c_dr1 N + c_dr2 N^2/n_w - W^2 n_w (n_w^2-1)/(48 c_dr2)] + n_w O_w   (while n_{n_w} >= 0)
square-root start: n* = sqrt((W N/2 + O_w/T_par)/c_dr2); search integer n_w around N/n* (exact enumeration for N <= 20)
capped waves: KKT T_par(W k + C_dr'(n_k)) + zeta_k = lambda; -dC*/dn_cap = sum_k zeta_k (shadow value of capacity)
duration lower bound: T_prog >= max(N a/K_chg, N T_par/n_hat_2)            (n_hat_2 from 4.9; without security review n_hat_dec)
score path: during wave k, dm = [sum_{earlier} W_p - C_dr(n_k)]/S - (core per-process transition flows)/S - capex that year/S
```

The engine reports the depth (wave 1), the number of waves below baseline and the final uplift Σ W_p/S, and feeds Δm into Part I's R*_X path.

### 4.7 Portfolio risk (module `risk`)

```
wave payoffs: V_k on success, C_k on failure with varpi_k V_k - (1 - varpi_k) C_k = core eq:tasks-npv
  C_k = F + I + C_J + C_par*A_r(T_par) + e^{-r T_par}*p_u*(C_str + L_roll),  p_u = e^{-T_par/T_det}
learning on the process factor: logit varpi_c(E_k) = logit varpi_c(0) + upsilon_L ln(1 + E_k);
  E_{k+1} = (1 - delta_E) E_k + eta_tr * successes_k;  varpi_p = R_p * varpi_c with R_p = q(L/Phi) prod varpi_pj (core)
  first-order gain dvarpi = varpi (1 - varpi_c) upsilon_L ln(1 + eta_tr)
order of two processes: EV(1->2) - EV(2->1) = (1-delta_d)(varpi1 V1 - varpi2 V2) + delta_d(varpi1 Dvarpi2 V2 - varpi2 Dvarpi1 V1)
platform shock: platform sound w.p. p_P; if not, every wave on it fails; continue after a failure iff EV_2(p') > 0,
  p' = p_P(1 - varpi)/(1 - p_P varpi); EV^seq - EV^sim = delta_d(1 - p_P varpi)(-EV_2(p'))_+ - (1 - delta_d) EV_1
provider concentration: waves on M providers with n^w_m waves each, H_n = sum (n^w_m/n_w)^2:
  Var(successes) = p_P n_w varpi(1-varpi) + n_w^2 varpi^2 p_P(1-p_P) H_n;  Pr(no success) >= (1 - p_P)^M
cost overrun ratio R = actual/estimate: tail Pr(R > x | R > 2) = (x/2)^(-2.3); body below 2 assumed (defaults, 5.)
Monte Carlo (>= 10,000 draws): provider and platform shocks first, then independent wave outcomes (core Bernoulli/Beta),
  overruns, regime shocks (4.10); report P10/P50/P90 of NPV and of the R40 path, and Pr(meet target)
```

### 4.8 Common-mode failure, diversity and governance (module `risk`, section "AI failure modes and controls")

Inputs: x_p (loss a year of disruption per process: savings forgone, manual fallback, errors in flight), the provider of each process (or model version), ν^cm (events a year per provider), T_mon, T_resp, Y_f (fallback capacity, $ a year), κ_fo (residual share with failover), F_M, C^inf, b_v, T_ks, model-update parameters B_up, p_g, δ_c, η_min, T_reb, business-unit exposures x_u.

```
X = sum x_p; X_m = exposure on provider m; H = sum (X_m/X)^2; T_con = T_mon + T_resp
event cost (exposure y disrupted for T_con): T_con*(y + y^2/(2 Y_f))
annual cost: mean = nu_cm*T_con*(X + H X^2/(2 Y_f));  variance = nu_cm*T_con^2*sum_m (X_m + X_m^2/(2 Y_f))^2
diversity (M equal providers vs one): saves nu_cm T_con X^2 (1 - 1/M)/(2 Y_f) a year; variance / M at least
redundancy (failover): value = nu_cm T_con [(1 - k_fo) X + (1 - k_fo^2) H X^2/(2 Y_f)] a year
number of providers: J(M) = C_inf M^{b_v} + M F_M + nu_cm T_con [X + X^2/(2 Y_f M)]
  M* = smallest M >= 1 with nu_cm T_con X^2/(2 Y_f) <= M(M+1)[F_M + C_inf((M+1)^{b_v} - M^{b_v})]
  one provider iff nu_cm T_con X^2/(4 Y_f) <= F_M + C_inf(2^{b_v} - 1); b_v = 0: M* in {floor, ceil} of sqrt(nu_cm T_con X^2/(2 Y_f F_M))
staged model update: EV(eta) = p_g B_up [1 - (1-eta) delta_c] - (1-p_g) T_con [eta X + (eta X)^2/(2 Y_f)]
  eta* = min(1, max(eta_min, (Y_f/X)[p_g B_up delta_c/((1-p_g) T_con X) - 1]));
  full release iff p_g B_up delta_c >= (1-p_g) T_con X (1 + X/Y_f)
  value of a rollback path per update = (1-p_g)(T_reb - T_con)[eta X + (eta X)^2/(2 Y_f)]
kill switch: value = nu_cm (T_resp - T_ks)[X + H X^2/(2 Y_f)] a year (rises with H; substitutes with diversity)
decision rights: unit wedge on provider m = nu_cm T_con (X_m - x_u)/(2 Y_f) per unit of exposure;
  internal charge at the firm optimum (many small units: nu_cm T_con X_m/(2 Y_f)), added to the expected loss in the
  core's autonomy choice (prop:tasks-autonomy(b)) and to the delegation rule (4.9); or centralize provider and autonomy limits
ceiling: report the expected common-mode cost / S next to the core's c_err (eq:tasks-cerr)
```

Activity-level failure modes (hallucination, automation bias, autonomy and misbehavior, pipelines, c_err, effect on ϖ_p) are the core's (`prop:tasks-halluc`, `prop:tasks-bias`, `prop:tasks-autonomy`, `prop:tasks-pipeline`, `eq:tasks-cerr`, `cor:tasks-failure-success`); see core notes 4.13.

### 4.9 Decision bandwidth, security review and change capacity (module `risk`)

```
load x = L/Phi; Q(x) = q(x) exp(-r_d l_dec(x)); defaults l_dec = l0/(1-x), q = exp(-eta_q (x-1)_+), r_d = r + delta_V
  breakpoint x_hat: -x Q'(x)/Q(x) = 1  (queue only: x_hat = 1 + c/2 - sqrt(c + c^2/4), c = r_d l0)
  optimal concurrency: max_n n varpi0 V Q(n e/Phi) - C_dr(n); value of a decision unit p_Phi = (n* varpi0 V Q(x*)/Phi) eps_Q(x*)
  AI analysis: e = e_appr + e_prep/(1 + A_Phi); gain cap (e_appr + e_prep)/e_appr
  delegate i iff (varpi_top - varpi_del) V_i < p_Phi e_i (plus the common-mode wedge of 4.8 in the delegated loss),
    except approvals reserved to accountable officers (regulated, licensed)
security review (core prop:tasks-secreview): nu = n/T_par deployments a year; Q_sec(n) = (Phi_sec - nu)/(Phi_sec - nu + r_d)
  EV(n) = n varpi0 V Q(n e/Phi) Q_sec(n) - C_dr(n), n < T_par Phi_sec, n <= n_cap = K_chg T_par/a
  eps_sec(n) = nu r_d/((Phi_sec - nu)(Phi_sec - nu + r_d)); security-only breakpoint nu_hat = Phi_sec + r_d - sqrt(r_d^2 + r_d Phi_sec)
  combined breakpoint n_hat_2: eps_Q(n e/Phi) + eps_sec(n) = 1 (bisection); n_hat_2 <= min(x_hat Phi/e, T_par nu_hat)
  shadow values at n*: dEV/dPhi = [n* varpi0 V Q Q_sec/Phi] eps_Q(x*);
    per year dEV/dPhi_sec / T_par = core eq:tasks-secvalue at nu = n*/T_par, V_dep = varpi0 V Q(x*)
      (optimal Phi_sec given n*: core square-root rule nu - r_d + sqrt(nu V_dep r_d/p_sec));
    per affected FTE a year of change capacity: zeta T_par/a, zeta = varpi0 V Q Q_sec(1 - eps_Q - eps_sec) - C_dr'(n_cap) if binding
  hard caps (no congestion below capacity): n_bar = min(K_chg T_par/a, Phi/e, T_par Phi_sec); only the minimizing capacity has
    value: sum zeta_k * (T_par/a | 1/e | T_par); report which one binds and the next one
pace: T_prog >= max(N a/K_chg, N T_par/n_hat_2)
```

### 4.10 Regime shocks (module `risk`, Monte Carlo over shock arrivals)

Inputs (Tier 3 organizational): ν^L (default 0.16 a year for a CEO, Kaplan and Minton; CIO, CDO, CAIO practitioner data, flagged), κ_keep, ν^V (with a jump after a leadership change), ν^R, T_frz, O^re_w, n_K key people, ν^K, κ_doc, η_K, L^ctx, s^reuse per investment, C^rep, P_V, p_inf, V^+, V^−.

```
nu_D = nu_L (1 - kappa_keep) + nu_V;  r_D = r + nu_D;  V_rec = s_reuse (F + I) - C_rep
process value: V(nu_D) = -(F+I) + W[(e^{-r_D T_par} - e^{-r_D T_emb})/r_D + e^{-r_D T_emb}/r] + V_rec (nu_D/r_D)(1 - e^{-r_D T_emb})
  (W risk-adjusted; T_emb = payback including the parallel run, core prop:tasks-transition(c))
first-order loss: -nu_D * int_0^{T_emb} [V_pay(inf) - V_pay(tau)] d tau
tenure breakpoint: r_D T_emb = 1 (with r, nu_V small: tenure 1/nu_L = (1 - kappa_keep) T_emb); split programs into wins embedding within 1/r_D
sequencing: run in decreasing V_emb,i/(e^{r_D tau_i} - 1); switch rate r_D* where V_q g(r_D) = V_l, g = (e^{r tau_l}-1)/(e^{r tau_q}-1)
vision-agnostic value: dV/ds_reuse = (F+I)(nu_D/r_D)(1 - e^{-r_D T_emb})
context stock: E[m] = 1 - nu_K (1 - kappa_doc)/eta_K; Var = nu_K (1 - kappa_doc)^2/(2 eta_K n_K);
  value of documentation per Delta kappa: L_ctx nu_K Delta kappa/(eta_K r)
commitment devices: P_V = 1 - e^{-nu_V tau}; binding = P_V[(1-p_inf)(V+ - V_rec) - p_inf(V- + V_rec)]; gated = P_V(1-p_inf)(V+ - V_rec)
  (same with nu_L(1 - kappa_keep) in place of nu_V for devices that raise kappa_keep)
freezes: Phi, K_chg (and Phi_sec if security review also freezes) divided by 1 + nu_R T_frz;
  extra program cost nu_R T_frz (C_prog - n_w O_w) + nu_R T_par n_w O_re;
  equal-wave optimum n* = sqrt([W N/2 + (O_w + nu_R T_par O_re)/((1 + nu_R T_frz) T_par)]/c_dr2);
  fewer waves iff T_par O_re > T_frz O_w; with n_s decoupled streams the freeze cost is 1/n_s
```

### 4.11 Breakpoint report

Each item as a distance to its threshold, per activity, process or program:
- organizational: 𝒲_0 − Λ and the solo date;
- market: c_E(t) + p_sw − P_I and T_M (with and without a plateau);
- regulatory: B_j − J_j for each class move; oversight floor: ξ^min* − ξ^min (exact root and bound);
- timing: T^F_j (plateau: never), T*_p and contract expiries;
- program: n_1* − n_cap; load x* − x̂; concurrency n* − n̂_2; which hard cap attains n̄;
- tenure: r_D T_emb − 1 and r_D*; freezes: T_par O^re_w − T_frz O_w;
- providers: F_M + C^inf(2^{b_v} − 1) − ν^cm T_con X²/(4Y_f); staging: (1−p_g) T_con X(1 + X/Y_f) − p_g B_up δ_c.

---

## 5. Default parameters (S = sourced, A = assumed)

| Parameter | Default | Range | Status and source |
|---|---|---|---|
| τ_L payroll loading | 0.43 | 0.25 to 0.55 | S: BLS ECEC June 2026, private industry, benefits $14.07 vs wages $32.82 an hour. Range A. Needs a bib entry (literature agent). |
| τ profit tax | 0.21 | 0.15 to 0.30 | S: U.S. federal statutory rate; range A |
| ψ deductibility of AI capital | 1 for domestic software development (26 U.S.C. §174A(a), (d)(3): deducted when paid or incurred, taxable years beginning after 31 Dec 2024) and for qualified property acquired after 19 Jan 2025 (100% allowance, IRS Notice 2026-11); ψ_15 = 0.532 for foreign research (§174(a): 15 years from the midpoint, r = 0.10); split ψ = 1 − ς_for(1 − ψ_15) | ψ_15 to 1 | S: statute (usc2026sec174a, usc2026sec174, irs2026notice202611 in part2/refs_accounting.bib). The support example uses ψ = 1 (c_A = $4.12, B = $4.91). The synthetic population of tab:ext-tornado is rebased to current law (ψ = 1, coordinator decision 29 Oct); its ψ row spans the foreign share from 1 to 0 (ψ_15 = 0.532 to 1). Rebase effects: baseline Σ^eco 0.735 → 0.742 (Σ^fea, Σ^per, Σ^pre and value 25.0% unchanged); Shapley scenario total +1.5 → +0.8 points, one-at-a-time sum 6.9 → 5.1; Shapley attributions (points) taxes +1.08 → +0.85, regulation −0.07 → −0.07, ethics −2.19 → −2.19, altruism +2.45 → +2.28, customers −1.55 → −1.58, AI prices +1.75 → +1.56; tornado ranking unchanged. |
| τ_A | 0 | 0 to 0.5 | A (hypothetical) |
| ξ^min by class | 0, 0, 0.10, prohibited | class 2: 0.05 to 1.0 | A (modeling device for Art. 14; eu2024regulation) |
| t^L/t; w^L/w | 0.05 to 0.25; 1.6 | | A |
| ϑ altruism | 0 | 0 to 15 $ an hour after tax | A (set by the firm) |
| ω penalties, exclusions | 0, none | set by the firm | A |
| δ^G per customer-facing AI mode | 0 | −0.002 to 0.005 | A (direction: dietvorst2015algorithm, longoni2019resistance, luo2019machines) |
| X growth weight | 9 | 7 to 13 | S: Part I; use the firm's v'(s) |
| r | 0.10 | 0.08 to 0.12 | A |
| T_A build life | 3 years | 2 to 5 | A |
| δ_K compute | 0.25 | 0.20 to 0.33 | A (Part I Remark rem:assumptions(c)) |
| t^U/t (support) | 1/1.15 | task-specific | S: brynjolfsson2025generative (15% more issues resolved per hour) |
| H0, t0 | about 1 hour in early 2025 (example) | | S, dated: refresh from METR releases; usage-based horizons are longer |
| T_d | 207 days | 143 to 240 days | S: kwa2025measuring (95% CI 166 to 240; 143 days since 2024); software tasks only |
| t_p plateau date | none | scenario | A (spec 24.2 scenario) |
| η_r | 1.16 | 1.00 to 1.29 | S at 80% (horizons 4 to 6 times shorter); A above 80% |
| s^ctx context share; C coverage | 0.5; firm input | 0.3 to 0.8 | A |
| L_W world-model lag | 5 years | 2 to 15 | A |
| ς_dbl dispersion of doublings | from d_j data; fallback 3 | 2 to 4 | A |
| δ_π fixed-performance price decline | ln 5 = 1.61 a year | ln 5 to ln 10 (Gundlach); ln 9 to ln 900 (Epoch) | S: gundlach2025price; epoch2025inference. The frontier price rises 3 to 18 times a year |
| s_E energy share of AI cost | 0.07 | 0.03 to 0.10 | S: michael2026servers ($0.6bn of $8.5bn annualized; our ratio); range A |
| δ_en, δ_hw | 0.5, 1.0 a year | | A |
| δ_F decline of integration cost | 0.3 | 0 to 0.5 | A |
| χ_h coordination per human pair | 0.03 person-years a year | 0.01 to 0.06 | A (form motivated by becker1992division, brooks1975mythical) |
| χ_a, p_a, Y_a | firm or vendor input | | A |
| ζ_P tail of task lengths | 0.5 | 0.3 to 1.0 | A |
| t_FTE | 2,080 | | S: BLS OES convention (data agent to confirm) |
| l_DI, l_AI | 0.6, 0.6 | 0.4 to 0.8 | A |
| e_mnt, e_PO, e_RG, e_SME (FTE) | 0.25, 0.5, 0.5, 0.25 | | A |
| N_CM affected FTE per change manager a year | 100 | 50 to 200 | A |
| κ_abs absorbable share of workforce a year | 0.10 | 0.05 to 0.20 | A |
| T_par, ω_par, ν_rec, C^str, T_det, L_roll | from core and data agents | | |
| c^dr_2 congestion; O_w overhead per wave | 0.25 × savings per process; 1% of program budget | | A |
| υ_L learning slope | 1.0 per log experience | 0.5 to 1.5 | A |
| δ_E experience decay per wave | 0.3 | 0.1 to 0.5 | A (direction: argote1990persistence, darr1995acquisition) |
| η_tr transfer across units | 0.5 (1 within a unit) | 0.2 to 1 | A (darr1995acquisition: transfer within a franchisee, not across) |
| p_P platform soundness | 0.9 | 0.7 to 0.97 | A |
| overrun tail | index 2.3 above ratio 2.0 | 2.0 to 2.6 | S: flyvbjerg2022empirical |
| tail probability | 1/6 | | S: flyvbjerg2011why (average 200% among the tail); samples differ from the 2022 study; treat the body as A |
| ϖ and b̄ (benefit realization) | from core | | A (Flyvbjerg measures cost, not benefits) |
| Φ decision bandwidth | firm input | | A; default: current concurrent major initiatives ÷ 0.7 |
| ℓ_0 base latency; δ_V erosion | 0.25 years; 0.4 a year (r_d = 0.5) | 0.1 to 0.5; 0.1 to 1.0 | A |
| η_q quality congestion | 1.0 | 0.5 to 2 | A |
| e^appr/e | 0.3 | 0.2 to 0.5 | A |
| Φ_sec, p_sec | firm input; core defaults | | core prop:tasks-secreview; A |
| ν^cm common-mode events per provider | 2 a year (example) | 0.5 to 6 | A (needs the reliability-evidence agent: provider incident and status-page data, flagged) |
| T_mon, T_resp, T_ks | 0.002, 0.008, 0.001 years (example) | | A |
| Y_f fallback capacity | firm input; example $10 million a year | | A |
| κ_fo failover residual | firm input | 0 to 1 | A |
| F_M per extra provider | $150,000 a year (example) | | A (overlaps the core's maintenance and revalidation run costs) |
| b_v volume-discount elasticity | 0.1 (example) | 0 to 0.3 | A (vendor price sheets, flagged, if sought) |
| p_g, δ_c, B_up, T_reb (updates) | 0.9, 0.1, firm input, 0.05 years (example) | | A |
| ν^L sponsor hazard | 0.16 a year (CEO) | | S: kaplan2012how; other executives practitioner, flagged |
| κ_keep, ν^V, ν^R, T_frz, O^re_w | 0.5, 0.05 to 0.25, firm input, firm input | | A (no evidence links reorganizations to initiatives in flight) |
| n_K, ν^K, κ_doc, η_K, L^ctx | firm input; 0.15; 0.2; 1.0; firm input | | A |

---

## 6. Literature

Cited, all keys present in `refs.bib` or `part2/refs_part2.bib` and verified in `notes/ref_verification_part2.md`: kwa2025measuring, michael2026servers, gundlach2025price, epoch2025inference, eu2024regulation, becker1992division, brooks1975mythical, garicano2000hierarchies, garicano2006organization, rosen1981economics, dellacqua2026cybernetic, mcdonald1986value, dixit1994investment, farzin1998optimal, acemoglu2020does, milgrom1994monotone, dietvorst2015algorithm, longoni2019resistance, luo2019machines, brynjolfsson2025generative, argote1990persistence, darr1995acquisition, flyvbjerg2011why, flyvbjerg2022empirical, simon1971designing, ocasio1997towards, sah1986architecture, kaplan2012how, jenter2015ceo, quigley2012when, walsh1991organizational (cited for the concept only; its typology was not read), staw1976knee, staw1981escalation, berger1996investor, trigeorgis1996real, korinek2025concentrating.

Wanted, not cited until keys exist: user cost of capital (Jorgenson 1963; Hall and Jorgenson 1967); Shapley (1953); Amdahl (1967); Klemperer (1995) on switching costs; a subexponential-tails text (Embrechts, Kluppelberg and Mikosch 1997); Hardy, Littlewood and Polya or Marshall and Olkin on majorization (used in prop:ext-commonmode(a)); Campbell's theorem (any Poisson-process text); BLS ECEC June 2026 and the BLS OES 2,080-hour convention; EU AI Act Art. 6(3) on EUR-Lex; evidence on provider outages and post-update regressions (reliability-evidence agent, refs_reliability.bib).

---

## 7. Verification summary

`python3 code/verify_part2_ext.py` → `SUMMARY: 140/140 checks passed`.

- A, universe (32): derivation of the effective cost, Υ, ψ and the capital recovery factor; derivative formulas; envelope d c^Q/d ŵ = t_A across review regimes (A5b); floor derivative and convexity of c^Q (A6); monotone statics on 500 synthetic activities (mode A at the core's c^Q); payroll-tax sign reversal; altruism, payroll and displacement-tax equivalence with re-optimized review; nesting; density formula exact and by Monte Carlo; envelope and convexity of 𝒱; small-share value derivative against Part I's eq:gordon; support example (c^Q = 3.15, floor breakpoint 0.55 against the bound 0.49); Shapley efficiency and non-additivity; tornado.
- B, dynamics (22): reliability inverse and η_r; lags; context; probit S-curve and scaling; energy share and fusion numbers; AGI limit (review share to the floor, human cost to ŵ ξ^min t^R + sign-off); timing FOCs, closed forms, lock-in, parallel run, break fees.
- C, competition (7). D, organization (14). E, program (7).
- F, portfolio, bandwidth and the security remark (17): learning on ϖ^c and the exact sign result (F2b); V_k and C_k against the core's NPV (F2c); platform sequencing; variance; load breakpoints; value of bandwidth; AI cap; delegation; pace; two-capacity breakpoint below both single breakpoints (F10); envelope shadow values matching eq:tasks-secvalue and the square-root rule (F11); quoted example (F11b); change-capacity multiplier (F12); hard caps, convexity of C*, binding-capacity shadow values and ties (F13).
- G, breakpoints (2), with the class-boundary jump at the core's c^Q.
- H, consistency (13): the tornado table parsed from the tex; waterfall and Shapley strings found in the tex; learning decay; capacity-weighted ordering; contested equilibria; capped waves; agent pods; power-law sums; tenfold condition; dip monotonicity; after-tax envelope; convexity of C̃^dr.
- I, regime shocks (16): closed form against quadrature and Monte Carlo; monotonicity; first-order loss; tenure breakpoint; sequencing by brute force; switch rate; reuse derivative; context stock by simulation; commitment devices; freeze availability by renewal simulation; freeze costs; freeze-adjusted square-root rule; decoupled streams.
- J, common mode (6): provider-concentration variance and no-success bound (Monte Carlo); compound-Poisson mean and variance and Schur-convexity; diversity, variance ratio and redundancy; provider-count rule against brute force (500 draws) and the single-crossing lemma; staged release against a grid (400 draws); kill switch, cross-partial, decision-rights wedge, Nash over-exposure and the restoring charge.
- K, plateau (4): frozen feasible share and the context factor; pay-as-you-go timing (equal loss up to t_p − T_par, later adoption, weakly higher gain from waiting, never-adopt case); lock-in (option value weakly falls); entry flip later or never, viability unchanged with a constant gap.

---

## 8. Open items for the lead author

1. The plateau result differs from the brief's wording under pay-as-you-go pricing (Section 3, item 2).
2. The core writes χ(r̄^A_j) after eq:tasks-success; it should be χ(q̄^A_j).
3. Φ, ℓ_dec and b_p clash with Part I symbols; ϑ (altruism) looks like θ, but was the only free Greek letter.
4. Add the common-mode cost next to c_err in Part I's ceiling (Section 3, item 11).
5. Parameters for ν^cm, Y_f, b_v and the update model are assumptions until the reliability-evidence agent sources them.
6. Uncomment the `\input{part2/theory_competition.tex}` slot once the IO theorist's file exists.
7. Length: about 25 pages plus 11 pages of proofs.
