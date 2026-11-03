# Theory product notes (Part II, spec Section 17: AI product strategy)

Files:
- `part2/theory_product.tex`: `\section{AI in the Product: Pricing, Seats and Margins}\label{sec:product}`. About 10.5 pages in the test build, including three tables (notation, combined plan, breakpoints).
- `part2/proofs_product.tex`: `\section{Proofs for Section~\ref{sec:product}}\label{app:proofs-product}`. About 6 pages.
- `code/verify_part2_product.py`: 92 checks, all passing (`python3 code/verify_part2_product.py`, about 40 s, exit code 0). Every number quoted in the text is printed with `->` and asserted.

Test build: the harness includes Part I's model and appendix, theory_core, theory_ext, theory_product and all three proof files, with `\bibliography{refs,part2/refs_part2,part2/refs_modern,part2/refs_product}` (plus refs_reliability and refs_competition, which the other sections now cite). Result: no errors, no overfull boxes in my files, no undefined citations, no duplicate labels. The only undefined references are Part I sections outside the harness (sec:empirics, sec:horizons). The build needs `amssymb`, which is already loaded, for `\mathfrak`, `\mathbb` and `\mathsf`.

## 1. Results and labels

| Label | Content | Spec 17.3 item |
|---|---|---|
| ass:prod-value | customer saving per outcome V = cbar - c^res (best alternative from prop:tasks-modes(c); residual = quality cost of prop:tasks-review + integration); power-law adoption frictions give D = (1 - kappa_cap)^eps | 1 |
| ass:prod-entry | AI-native entrants price at (1 + ups_E) chat_E; rent per outcome rho_u = V_I - V_E + p_sw; cap pbar = (1 + ups_E) chat_E + rho_u | 1 |
| prop:prod-price | (a) monopoly capture share kappa^m = (1 + eps c_I)/(1 + eps); (b) competitive price min{p^m, pbar}, viability chat_I < pbar; (c) pass-through eps/(1+eps) unconstrained, 0 own / 1 entrant when capped; (d) free-entry limit, Part I rho = rho_u/(c_E^inf + rho_u); (e) rent sources; data rent bounded by L a_e (D_E^-b - D_I^-b), vanishes under a constant proportional data lead, concave where the review floor binds; (f) heterogeneous switching premia: sales D(p) S_sw(p - pbar0), price in [min{p^m, pbar0}, p^m], root of ell(p) = h_sw(p - pbar0) for log-concave premia, partial pass-through both ways, exponential premia earn nothing below a mean of 1/ell(pbar0), gamma premia converge to (b) as cv -> 0 | 1, 6 (price floor) |
| ass:prod-seats, prop:prod-seats | seats = residual FTE (def:ext-org); seat revenue grows at g_v - nu; customer-side operations version of X(t); Bass reduced form: tipping t*_B, peak compression, single-peaked seat-loss rate with closed-form peak Bhat; capability-limited probit form | 2, 6 (tipping point) |
| ass:prod-migrate, prop:prod-migrate | migration value V_k(T); derivative; seat-compression threshold nu*_k; optimal date = first crossing; monotone in (delta, omega, e, varpi); target tariff menu (usage, two-part, seat-fee hybrid) | 2, 6 (seat-compression threshold) |
| prop:prod-portfolio | feature score flow and NPV at the firm's own weight; platform rule; knapsack ranking and shadow value of engineering capacity; retention outweighs margin; screening-weight bias | 3 |
| prop:prod-model | API, open weights, own model: volume ladder; falling API prices raise build thresholds; long-run "rent covers unit cost" condition; capital and growth (prop:tasks-capital); revenue-share partner | 3 |
| prop:prod-margin | gross-margin path with pass-through and cost floor; crossover date T_x and existence; limit-pricing margin rho_u/(u + rho_u); blended-margin trough | 4, 6 (margin crossover) |
| prop:prod-cannibal | replacement effect as an extra unit cost (seat margin per unit of work); entry removes it; Poisson preemption: launch now iff V > c_eff; threshold nu_E*; launch price | 7 |
| prop:prod-aggregate | mapping into gamma, G_i, lambda, k, G (market conversion), phi by tariff; first-order Delta R*; exact linearity in (gamma, G_i); bounded transient growth; complementarity of value pricing and COGS automation (Topkis) | 5 |
| cor:prod-dilution | margin dilution for growth: Delta R* = -D_m + (X - k) Delta G exactly; frontier rotation with unique crossing and dual-weight bracket | 5 |
| prop:prod-breaks | price floor and binding date T_C, Bass tipping point, pointers to the other thresholds | 6 |
| tab:prod-notation, tab:prod-plan, tab:prod-breaks | notation; combined plan scorecard (year 3); breakpoint values | |

## 2. Notation and deviations from the spec

Part I's reserved symbols keep their meanings. Renames:

| Spec | Used here | Reason |
|---|---|---|
| theta_cap (capture share) | kappa_cap | theta is reserved (margin persistence); theory_ext now uses vartheta for altruism. Subscripted kappa follows the share convention of kappa_O, kappa_keep, kappa_doc |
| features f | sans-serif f in blackboard F | f is Part I's fee share |
| product lines i | l | i indexes firms (Part I) and initiatives (theory_ext); G_i is Part I's firm-level zero-spend growth |
| Bass p, q | fraktur p, fraktur q; curve sans-serif B(t) | p indexes processes; theory_core uses sans-serif p (Pareto index) and q (CVaR level) |
| labor saving per outcome (unnamed) | sans-serif V_I, V_E | value per outcome; cbar is the core's best alternative |
| rents rho | rho_u (rent per outcome); Part I's rho is recovered as rho_u/(c_E^inf + rho_u) | rho is rent per dollar of revenue |
| seat compression (unnamed) | calligraphic X(t) compressed seat share; nu(t) = Xdot/(1 - X) seat-loss rate | x is the core's mode |
| "cost-plus floor" | (1 + ups_E) chat_E; ups_E = 0 is the free-entry limit | literature finding 20: the floor is a limit, not a default |
| migration cost, risk, dip | delta_k (permanent concession), omega_k (one-time cost in years of gross profit), varpi_k (success), e_k (share of the new bill still per seat) | matches varpi_p (success) and omega_par (duplication share) conventions |
| r - g in proofs | r_v := r - g_v | rho is reserved |
| labor-to-seat ratio (new) | sans-serif W = V t_FTE/(t p_seat) | theory_core uses sans-serif L for the normal loss function |

New symbols: eps_ad (adoption elasticity), sans-serif c_I = chat_I/V_I, sans-serif C_ad = eps^eps/(1+eps)^(1+eps), ups_E (entrant markup), pbar (cap), chat_E^ddag (binding threshold), p_seat, pbar_seat = p_seat t/t_FTE, gamma_seat, gamma_AI, gamma_sub, xbar (exposure), Bhat (peak of nu), T_C (binding date), V_k(T), nu*_k, upsilon_f (uplift), n_f (inference per dollar of base revenue), n^E_f, N^E (engineer-years), F^plat, c^var_m, c^h_m, K_m, Ftilde_m, rho_{u,m}, chat^net_m, Q_{m m'}, kappa_par, u_h, u_c, delta_u, T_x, w(t) (AI revenue share), sans-serif s = gamma_seat/W, nu_E (entry hazard), p_L, c_eff, M_seat, k_def (Part I Remark (c)), D_m, Delta G, ghat, script D (data stock), a_e, b_e, e_inf.

Modeling choices to note:
- Vendors are labeled I (incumbent) and E (entrant). Activity readiness iota_j keeps its activity subscript.
- Adoption frictions are common to all agents, so the incumbent sells to every adopter up to the cap. The switching premium p_sw applies to the incumbent's installed customers.
- Migration: the new tariff is accepted at a permanent concession of the current bill; the share 1 - e_k of the new bill is protected from compression; the cost T_k = omega_k gamma R_S(T) scales with the revenue migrated; failure reverts to seats after paying T_k.
- Feature value uses the firm's own weight X = v_0 and discounting at r - g°, the small-share limit, extended to time-varying flows by superposition (proof of prop:prod-portfolio(a)).
- Cannibalization (c): the first mover keeps p_sw on its pre-entry base after entry (a reduced form); entry is Poisson; the launch is a commitment; customers do not delay purchases (the Moorthy and Png caveat is stated in the text).

## 3. Formulas the engine must implement

Units: dollars per outcome unless stated; Q in outcomes a year; revenue in dollars a year; rates a year; probabilities and shares in [0, 1]. The functions `quality_cost`, `adoption`, `kap_monopoly`, `price_competition`, `bass_B`, `bass_f`, `bass_t_of_B`, `nu_seat`, `Bhat_peak`, `nu_star`, `V_mig`, `first_crossing`, `feat_npv`, `net_unit`, `Qthr` in `code/verify_part2_product.py` are reference implementations for cross-implementation tests (spec 19.1).

### 3.1 Customer value and price (module `product.pricing`; prop:prod-price)
Inputs per product scope: customer modes (from the customer-side run of the core module, or defaults): cH, cO, cU ($/outcome); agent error rates e_I, e_E; loss per undetected error L ($); review cost w t_R ($/reviewed unit); review floor ximin; integration cost eta_I, eta_E ($/outcome); p_sw ($/outcome); chat_I, chat_E(t) ($/outcome); ups_E (default 0; scenario > 0 for concentration); eps_ad (default 1).
```
cbar   = min(cH, cO, cU)                                  # best alternative, not cH
cres_k = cQ(e_k) + eta_k                                   # cQ from core prop:tasks-review (economic share or floor)
V_I, V_E = cbar - cres_I, cbar - cres_E
rho_u  = V_I - V_E + p_sw                                  # report the three parts: data cQ(e_E)-cQ(e_I), workflow eta_E-eta_I, p_sw
cI     = chat_I / V_I
kap_m  = (1 + eps*cI)/(1 + eps);  p_m = (V_I + eps*chat_I)/(1 + eps)     # if cI < 1, else no profitable agent
pbar   = (1 + ups_E)*chat_E + rho_u
viable = pbar > chat_I
p_star = min(p_m, pbar);  kap_star = p_star/V_I;  D_star = (1 - kap_star)**eps
margin per outcome = p_star - chat_I;  agent gross margin = 1 - u_I/p_star  (u_I = variable part of chat_I)
profit per in-scope outcome = (p_star - chat_I)*D_star;  monopoly: V_I*C_ad*(1-cI)**(1+eps), C_ad = eps**eps/(1+eps)**(1+eps)
binding threshold chat_E_ddag = p_m - rho_u   (competition binds iff (1+ups_E)*chat_E < chat_E_ddag)
pass-through: unconstrained phi = eps*chat_I/(V_I + eps*chat_I) (level eps/(1+eps)); capped: 0 for own cost, 1+ups_E for entrants'
long run (ups_E -> 0, costs -> c_E_inf): p -> min(p_m, c_E_inf + rho_u); Part I rho = rho_u/(c_E_inf + rho_u)
data rent with e(D) = e_inf + a_e*D**(-b_e): rent = cQ(e(D_E)) - cQ(e(D_I)) <= L*a_e*(D_E**-b_e - D_I**-b_e)
# heterogeneous switching premia (prop:prod-price(f)); default: single premium (cv_sw = 0), which is (b)
pbar0  = (1 + ups_E)*chat_E + V_I - V_E                    # cap without switching costs
S_sw(x) = Pr{p_sw >= x} (1 for x <= 0); default family gamma(mean pbar_sw, coefficient of variation cv_sw <= 1)
ell(p) = 1/(p - chat_I) - eps/(V_I - p);  h_sw = -S_sw'/S_sw
p_star = pbar0 if ell(pbar0) <= h_sw(0) else root of ell(p) = h_sw(p - pbar0) on (pbar0, p_m)   # needs chat_I < pbar0 < p_m
         (if pbar0 >= p_m: p_star = p_m; otherwise maximize (p - chat_I)*D(p)*S_sw(p - pbar0) numerically)
switching rent = p_star - pbar0;  share of the incumbent's customers lost to entrants = 1 - S_sw(p_star - pbar0)
pass-through (interior): dp/dchat_I = (p-chat_I)**-2 / G, dp/dchat_E = (1+ups_E) h_sw' / G, G = (p-chat_I)**-2 + eps (V_I-p)**-2 + h_sw'
exponential (cv_sw = 1): p_star = pbar0 unless pbar_sw > 1/ell(pbar0); interior price independent of chat_E
```
Report: kap^m, kap*, p*, adoption, margin, whether capped, distance (1+ups_E) chat_E / chat_E^ddag - 1, viability margin pbar - chat_I, rent decomposition; with heterogeneous premia also the switching rent, the share lost to entrants and the result at cv_sw = 0 (single premium) for comparison.

### 3.2 Seat compression (module `product.seats`; prop:prod-seats)
Inputs: p_seat ($/seat-year), seats N_0 or seat revenue R_0, t (h/unit), t_FTE (2,080), g_v, seat elasticity eps_seat (scenario: default 1, range 0.25 to 1; no precedent); either the customer-side activity list (time shares by DWA for the seat occupations, from occ_activity.csv, with customer mode changes and dates T_j) or a reduced form (xbar, Bass p, q).
```
pbar_seat = p_seat*t/t_FTE
customer-side seat-hours: X_h(t) = sum_j omega_seat_j*(1 - tseat(x1_j)/tseat(x0_j))*B(t - T_j),  T_j = max(feasibility date, crossover date)
compressed seat share: X(t) = eps_seat*X_h(t)      # report every seat result over the eps_seat range
   seat-hours per unit: H: t; U: t_U; A: xi*t_R; N: 0; O: t if the vendor's staff use the customer's seats, else 0 (input flag)
reduced form: X(t) = xbar*B(t) with xbar = eps_seat*xbar_h,  B(t) = (1 - exp(-(p+q)t))/(1 + (q/p)exp(-(p+q)t)),  Bdot = (p + q*B)(1 - B)
capability-limited: X(t) = xbar*N((t - t_m)/(sig_dbl*T_d))
nu(t) = Xdot/(1 - X);  seat revenue R_S(t) = R_0*exp(g_v t)*(1 - X(t));  line zero-spend growth G_l = g_v - nu(t)
RaR(t) = p_seat*N_0*eps_seat*X_h(t) (constant volume);  full-adoption RaR = eps_seat*xbar_h*R_0, reported as a band over eps_seat
tipping t*_B = ln(q/p)/(p+q) if q > p; B(t*) = (q-p)/(2q); peak Xdot = xbar*(p+q)**2/(4q)
nu(0) = xbar*p;  if q > p(1-xbar): Bhat = [1 - sqrt((1-xbar)(1 + xbar*p/q))]/xbar, t_hat = ln((1 + q*Bhat/p)/(1 - Bhat))/(p+q), nu_max = nu(t_hat); else nu decreasing
probit peak Xdot = xbar/(sqrt(2 pi)*sig_dbl*T_d) at t_m;  seat loss per doubling of the horizon = T_d*nu(t)
```
Default exposure: xbar_h from occupational exposure (occ_exposure.csv: Eloundou beta, Tomlinson applicability) times a time-saving share; marked assumed with a range (CSR example: 0.40, range 0.28 to 0.57). Seat elasticity eps_seat is class d (assumptions memo item 13): the engine must show revenue at risk, nu(t), the migration date and the migration value over its range, never at a point alone. AI agent revenue and the market multiplier use xbar_h (work automated), not eps_seat.

### 3.3 Pricing-model migration (module `product.migration`; prop:prod-migrate)
Inputs per target tariff k in {usage, two-part, seat-fee hybrid, other}: delta_k (permanent concession, share of bill), e_k (share of new bill still per seat), omega_k (one-time cost in years of the line's gross profit; add k_def/gamma if billing moves to arrears), varpi_k; gamma (line gross margin), r, g_v.
```
nu_star_k = (r - g_v)*(varpi*delta + omega*(r - g_v)) / (varpi*(1 - delta)*(1 - e) - omega*(r - g_v))   # None (never) if denominator <= 0
V_k(T) = varpi*gamma*Int_T^inf exp(-r t)[R_k(t) - R_S(t)] dt - exp(-r T)*omega*gamma*R_S(T)
   R_k(t) = (1 - delta)*R_S(T)*exp(g_v (t-T))*[1 - e + e*(1 - X(t))/(1 - X(T))]
V_k'(T) = exp(-rT)*gamma*R_S(T)*{varpi*[delta - (1-delta)(1-e)*nu(T)/(r-g_v)] + omega*(r - g_v + nu(T))}
T1_k = first t with nu(t) >= nu_star_k (0 if nu(0) >= nu_star_k); migrate at T1_k iff V_k(T1_k) > 0, else never
best target = argmax_k V_k(T1_k);  one-time dip in Rule-of-40 points = omega*gamma*R_S(T)/S (spread over renewals if phased)
```
Report: nu*_k, nu(t) now and at peak, T1_k, V_k per target, the dip, and the k_def change in Part I's k. All of delta_k, omega_k, varpi_k and e_k are class d (assumptions memo item 13): label outputs as conditional on scenario values and run them over the ranges in Section 5, jointly with eps_seat.

### 3.4 Feature portfolio (module `product.features`; prop:prod-portfolio)
Inputs per feature: F_f ($), n^E_f (engineer-years), Bass (p_f, q_f) for adoption in the base, upsilon_f (uplift per dollar of base revenue at full adoption), inference cost c0_f (per dollar of base revenue at full adoption) and its decline delta_u,f, delta^G_f (retention points), delta^lambda_f (proportional pull), platform requirements; firm: S, X = v_0 (Part I), k, Delta*, r, g°, capacity N^E, platform costs F^plat.
```
R_f(t)  = B_f(t)*[upsilon_f - c0_f*exp(-delta_u,f t) + (X - k)*(delta^G_f + Delta*delta^lambda_f)]     # score points per $ of revenue
NPV_f   = S*Int_0^inf exp(-(r - g°) t) R_f(t) dt - F_f
portfolio: max sum x_f NPV_f - sum_platforms F^plat*1{platform used} s.t. sum x_f n^E_f <= N^E   (enumerate if <= 20 features; else greedy by NPV_f/n^E_f with integer repair)
shadow value of an engineer-year = NPV/n^E of the marginal (fractional) feature in the relaxation
retention break-even: (X - k)(delta^G + Delta*delta^lambda) > c_f - upsilon_f
```
Report rankings at X = v_0 and at the investor screening weight (2 to 3) side by side.

### 3.5 Model sourcing (module `product.sourcing`; prop:prod-model)
Inputs per option m in {api, open, own, partner}: inference price path pi_m(t) and tokens n_m, hosting/orchestration c^h_m, capital K_m ($ per outcome of annual capacity), delta_K, build F_m and life T_m, maintenance delta_M, revalidation C^reval and T_up (core ass:tasks-ancillary), rent rho_{u,m} (from 3.1 with the option's error rate); partner share kappa_par.
```
c_var_m(t) = pi_m(t)*n_m + c^h_m;   Ftilde_m = F_m*a(r,T_m) + delta_M*F_m + C^reval_m/T_up,  a(r,T) = r/(1 - exp(-rT))
chat_net_m(t) = c_var_m(t) + (r + delta_K)*K_m - rho_{u,m};   partner: c_var = kappa_par*p + c^h, Ftilde = 0
choice at volume Q: argmin_m Q*chat_net_m + Ftilde_m;  thresholds Q_mm' = (Ftilde_m' - Ftilde_m)/(chat_net_m - chat_net_m') on the lower envelope
dates: when the API's net unit cost falls below another option's (vintage-locked options keep fixed unit cost)
long run: option m beats the API at some volume only if rho_m - rho_api > c_var_m + (r + delta_K)K_m - c^h_api
Part I: Delta k = K_m*Q/S; value charge (r + delta_K)K_m, cash-score charge (g + delta_K)K_m
```

### 3.6 Gross-margin path (module `product.margins`; prop:prod-margin)
Inputs: gamma_0, fees f, unit cost u_0 = u_h + u_c, delta_u, pass-through phi (or the pricing regime from 3.1), gamma_sub; AI revenue share path w(t).
```
gamma_AI(t) = 1 - f - (1 - f - gamma_0)*(u(t)/u_0)**(1 - phi),  u(t) = u_h + u_c*exp(-delta_u t)
gamma_inf  = 1 - f - (1 - f - gamma_0)*(u_h/u_0)**(1 - phi)
crossover exists iff gamma_inf > gamma_sub;  T_x = ln{u_c/[u_0*z**(1/(1-phi)) - u_h]}/delta_u,  z = (1-f-gamma_sub)/(1-f-gamma_0)
limit pricing (cap binds, chat_I = chat_E = u, f = 0): gamma_AI = rho_u/(u + rho_u); crossover iff rho_u/u_h > gamma_sub/(1-gamma_sub)
blended: gamma_firm(t) = w(t)*gamma_AI(t) + (1 - w(t))*gamma_sub; trough where wdot*(gamma_sub - gamma_AI) = w*gammadot_AI
```
Calibration: two fits to ICONIQ 2025-2027 (0.45, 0.53, 0.59): (i) u_h = 0, log-linear: (1-phi)*delta_u = 0.147/yr, crossover with 0.74 in 2030.1; (ii) constant price with floor: 1 - gamma = 0.23 + 0.32*exp(-0.288 t), gamma_inf = 0.77, crossover 2033.2. Report both; flag that three points (two projected) do not identify phi.

### 3.7 Cannibalization (module `product.cannibal`; prop:prod-cannibal)
Inputs: V_I, chat_I, eps, p_seat, t, t_FTE, gamma_seat, p_sw (first-mover premium), entry hazard nu_E (or expected years to entry), r, g_v; entrant cap pbar from 3.1.
```
m_seat = gamma_seat*p_seat*t/t_FTE        # seat gross profit per unit of human work; s = m_seat/V_I = gamma_seat/W, W = V_I*t_FTE/(t*p_seat)
no entrants: kap_can = (1 + eps*(cI + s))/(1 + eps); launch iff cI + s < 1; gain = V_I*C_ad*(1 - cI - s)**(1+eps);
             replacement cost = V_I*C_ad*[(1-cI)**(1+eps) - (1-cI-s)**(1+eps)]
entrants with binding cap: price min(kap_can*V_I, pbar); launch gain (pbar - chat_I)*D(pbar)
preemption: c_eff = chat_I + m_seat - nu_E*p_sw/(r - g_v); launch now iff V_I > c_eff;
            nu_E_star = (r - g_v)*(chat_I + m_seat - V_I)/p_sw (if chat_I + m_seat > V_I);  p_L = max(0, (V_I + eps*c_eff)/(1 + eps))
            value of launching now vs at entry = (p_L - c_eff)*D(p_L)/(r - g_v + nu_E) per unit of date-0 scope
```

### 3.8 Aggregation into Part I (module `product.aggregate`; prop:prod-aggregate, cor:prod-dilution)
Inputs: product lines l with S_l, gamma_l, tariff, G_l pieces; outputs of 3.1 to 3.7; operations deltas from core prop:tasks-aggregate.
```
gamma = sum_l w_l*gamma_l;   G_i = sum_l w_l*G_l
   seat line G_l = g_v - nu(t) (+ price growth); non-seat tariff G_l = g_v; outcome line G_l = g_v + Bdot/B + dln(p*D(p))/dt
   features: Delta G_l += sum_f B_f*delta^G_f;  lambda multiplier (1 + sum_f B_f*delta^lambda_f)*(1 - delta_sigma)**(-alpha)
   billing in arrears: Delta k = + k_def * (share of bill moved to arrears) * w_l
market: M = M_seat*[1 + X*(kap*W - 1)], X here = xbar*D(p)*B(t); Delta G = [Xdot*(kap*W - 1) + X*W*kapdot]/M_ratio; conversion iff kap > 1/W
phi by tariff: seat within term 0; capped value price 0; monopoly value price eps*chat/(V + eps*chat); cost-plus 1
Delta gamma from operations COGS saving = (1 - phi)*|Delta u|/p
Delta R*_X = Delta gamma - Delta a - (g* + delta_K)*Delta k + (X - k)*Delta G_i + (X - k)*Delta*·Delta lambda/lambda   (first order)
exact: R*_X = (gamma - a - delta_K k) + (X - k) G_i + C_alpha [lambda h (X - k)]^(1/(1-alpha))
value: permanent changes Delta v_0 = Delta R*_{X°}/(r - g°); transient diffusion growth integrates to ln(revenue gain), report separately
dilution test: Delta R*_X = -D_m + (X - k)*Delta G; frontier crossing ghat solves kappa[(g-G_i)^beta - (g-G_i-Delta G)^beta] = D_m
```
Report the combined scorecard (tab:prod-plan layout) for X = 1 (Rule of 40) and X = v_0, under the firm's tariff and under cost-plus, and flag transient rows.

### 3.9 Breakpoint report (prop:prod-breaks)
Per product line: competition binding (chat_E vs chat_E^ddag, T_C = ln[(chat_E0 - c_E_inf)/(chat_E^ddag - c_E_inf)]/delta_pi), viability (pbar - chat_I), seat-compression (nu(t) vs nu*_k and T1_k), margin crossover (T_x or "none"), Bass tipping (t*_B, and t_hat for the seat-loss peak), market conversion (kap vs 1/W), cannibalization (V_I vs chat_I + m_seat, nu_E vs nu_E*), sourcing (Q vs Q_mm'(t)), dilution weight (D_m/Delta G vs X - k).

## 4. Product-side inputs the engine should request (Tier 1 and Tier 3, product)

1. Revenue by product line and pricing model (seat, usage, outcome, hybrid; share of bill per seat e; billing timing and deferred revenue k_def).
2. Seats by product line and customer segment, seat price list and realized price per seat, contract terms and renewal calendar.
3. The customer occupations behind the seats (SOC codes or role titles), with seat counts per occupation; optionally the customer activities the product supports (DWA level) and the work unit (ticket, document, transaction) with hours per unit.
4. Usage and outcomes per customer (units handled on the platform, AI outcomes), and inference usage per outcome (tokens or agent steps) with the current inference price and model mix.
5. NRR and GRR by line and segment, and seat-count history (to estimate nu and Bass parameters from the firm's own adoption data; literature finding 18).
6. Candidate AI features: build cost, engineer-years, expected uplift, inference cost, expected retention and pull effects, platform dependencies.
7. AI agent unit economics: chat_I components (inference, escalation, hosting, capital), error rates of the agent, integration cost to customers.
8. Model sourcing options: API prices and deprecation cycle, open-weights hosting cost and capital, own-model build cost, partner terms.
9. Competitor and entrant pricing (list prices per seat and per outcome), known entrants and their costs; an expected entry date or hazard.
10. Customer alternatives: outsourcing price per unit, in-house cost per unit (or wage and hours), augmentation gain.
11. Migration history and assumptions: concession by tariff, expected dip, migration cost, success probability.
Defaults with wide ranges where absent (Section 5).

## 5. Default parameters (S = sourced, A = assumed, L = vendor list price)

| Parameter | Default | Range | Status and source |
|---|---|---|---|
| in-house cost per resolution c_H | $18.09 | 9.04 to 27.13 | S (class c): params.yaml product.capture_share.human_cost_per_resolution_usd = OEWS May 2025 median wage (43-4051) x (1 + tau_L) / 1.7 resolutions an hour (brynjolfsson2025generative, never-treated agents) |
| hours per resolution t | 1/1.7 = 0.588 | n/a | S, as above |
| outsourcing price ratio (support) | 0.55 | n/a | A (params.yaml F05) |
| augmentation gain | 0.14 | 0.14 to 0.26 | S: brynjolfsson2025generative (params.yaml) |
| eps_ad | 1 | 0.5 to 3 | A |
| seat elasticity eps_seat | 1 | 0.25 to 1 | class d, scenario only (no filing reports seats against customer headcount; assumptions memo item 13) |
| agent error rates e_I, e_E | 0.04, 0.066 | n/a | A |
| loss per undetected error L | $30 | n/a | A |
| p_sw | $0.20/outcome | 0 to 0.5 | A |
| switching-premium distribution (prop:prod-price(f)) | single premium (cv_sw = 0) | gamma, mean pbar_sw = $0.20, cv_sw in {1, 0.5, 0.2} | class d, scenario only: no measured distribution of switching costs per outcome; heterogeneity motivated by the acquirer section's retention analysis (prop:acq-retention: NRR by business, revenue hazard falling with tenure) |
| ups_E (entrant markup) | 0 (free-entry limit) | 0 to 1 | A; scenario for concentration (korinek2025concentrating) |
| chat_I, chat_E (support agent) | $0.40/outcome | 0.15 to 1.0 | A (params.yaml inference cost per human-hour, frontier to mid tier, times 0.25 h and a 1.5 interaction multiplier gives $0.14 to $0.68 of inference) |
| entrant cost floor c_E_inf | $0.10 | 0.05 to 0.3 | A |
| delta_pi (fixed-capability price decline) | ln 5 a year | ln 5 to ln 10 | S: gundlach2025price |
| delta_u (decline of inference cost actually used) | 0.3 a year | 0 to ln 5 | A; can be far below delta_pi (gundlach2025price; demirer2025emerging elasticity just above one) |
| AI product gross margins | 0.45 (2025), 0.53 (2026), 0.59 (2027, projected) | n/a | S: iconiq2026state |
| subscription gross margin | 0.74 | n/a | S: Part I core-sample median 2023-25 (horizons.tex) |
| seat price | $55 to $100 per agent a month, annual billing ($660 to $1,200 a year); script default for single-point checks $100 | $25 to $550 a month (published span) | L: four vendors' professional tiers, Section 6 |
| seat gross margin | 0.80 | 0.70 to 0.85 | A |
| exposure xbar (CSR) | 0.40 | 0.28 to 0.57 | A, anchored on eloundou2024gpts beta 0.57 and tomlinson2025working applicability 0.41 (occ_exposure.csv) |
| Bass p, q | 0.027, 0.419 | p 0.01 to 0.10, q 0.3 to 0.8 | S for consumer durables only: vandenbulte2004social means (sultan1990meta reports none in its abstract); software values A; calibrate to the firm's adoption data. AI adoption is faster (bick2026rapid; fradkin2025demand) |
| fast-diffusion case | p = 0.10, q = 0.80 | n/a | A |
| r, g_v | 0.10, 0.04 | n/a | A |
| migration: delta, omega, varpi | usage 0.15, 0.25, 0.75; two-part 0.08, 0.25, 0.80; seat-fee hybrid (e = 0.5) 0.04, 0.15, 0.85 | delta 0 to 0.3; omega 0.1 to 1; varpi 0.5 to 0.95 | class d, scenario only (assumptions memo item 13); direction from lambrecht2006paying, sundararajan2004nonlinear, essegaier2002pricing, balasubramanian2015pricing |
| capture share | output of prop:prod-price, not an input | n/a | The example gives kappa* = 0.138 of the net saving V_I, which is 0.085 of in-house cost c_H. That lies inside the list-price-implied range of 0.028 to 0.111 in params.yaml (product.capture_share; the memo suggests a 0.10 [0.03, 0.30] default for theta_cap). The engine must state which denominator it uses: c_H in params, V_I here. |
| k_def | 0.25 | 0 to 0.5 | A (annual prepaid billing gives about a quarter to a half of annual revenue in deferred revenue) |
| data-rent decay exponent b_e | 0.5 | 0.2 to 1 | A, inverse square root motivated by bajari2019impact |
| X (own weight) | 9 | 7 to 13 | S: Part I (spend-based weight) |
| screening weight | 2.5 | 2 to 3 | S: Part I (Bessemer range) |

## 6. Vendor list prices (accessed 29 October 2026; list prices, not transaction prices)

Vendor neutrality (author decision, 29 Oct 2026): no example rests on one vendor's prices, and one vendor is left out of the paper entirely at the author's request (not named here either). The text uses ranges across four vendors and names them only in the source footnote (fn:prod-prices in sec:product-setup), as list prices with access dates, with an explicit statement that nothing compares or recommends products. Vendor names never appear next to a price in the text. Bib entries are in `part2/refs_product.bib`. The ranges were rebuilt from the remaining verified vendors (Intercom, Salesforce, HubSpot) plus Freshworks, verified by WebFetch on 29 Oct 2026. No other input changed.

Middle (professional) seat tiers, per agent (seat) a month, annual billing. These four prices define the example range of $55 to $100:
- Freshworks Freshdesk Pro $55, "billed annually" (freshworks2026pricing, https://www.freshworks.com/freshdesk/pricing/; also Growth $19 and Enterprise $89; the page offers monthly billing but lists no monthly prices). Pro is the middle of three paid plans, the same position as the other vendors' professional tiers.
- Intercom helpdesk Advanced $85 a seat a month billed annually (fin2026pricing, https://www.intercom.com/pricing; also Essential $29, or $19 promotional for new customers, and Expert $132). The company renamed itself Fin in 2026 and is now a Salesforce company: Salesforce agreed to acquire Fin (formerly Intercom) on 15 June 2026 for approximately $3.6 billion (salesforce2026finagree) and completed the acquisition on 10 September 2026; Fin operates within Salesforce AI Labs (salesforce2026finclose). Both releases fetched from investor.salesforce.com on 29 Oct 2026. The helpdesk is still sold as "Intercom helpdesk".
- HubSpot Service Hub Professional $90 annual, $100 monthly (hubspot2026servicepro, https://www.hubspot.com/pricing/service/professional; also Starter $7 or $20, the page does not clearly label which is annual, and Enterprise $150).
- Salesforce Service Cloud Pro Suite $100, "starting price, billed annually, contract required" (salesforce2026servicepricing, https://www.salesforce.com/service/pricing/ ; fetched as https://www.salesforce.com/service/pricing/?bc=HL, because the bare URL was not on the fetch allowlist). Also Starter Suite $25, Core $195 (replaces Enterprise), Advanced $395 (replaces Unlimited) and Max $550 (replaces Agentforce 1), all per user a month.

Common parent: since 10 September 2026 two of the four products (Intercom helpdesk and Salesforce Service Cloud) share a parent. The ranges are ranges of list prices, not of prices set by independent competitors; the footnote says so. The text also states the acquisition as a fact (prop:prod-cannibal intuition), with no inference about motive, and notes that the model treats entrants as independent and has no acquisitions.

Wider published span: under $25 (HubSpot Starter, Freshdesk Growth $19) to $550 (Salesforce Max). The script checks the ends $25 and $550. The $550 edition bundles AI capacity (Agentforce 1 lineage), so its seat margin per resolution overstates the pure seat margin, which makes the $550 check conservative for the cannibalization result and pessimistic for market conversion.

Outcome or conversation prices for AI agents, $0.50 to $2.00 (unchanged by dropping a vendor: both ends come from the remaining vendors):
- HubSpot Customer Agent $0.50 per resolved conversation (50 credits) from 14 April 2026, previously $1.00 per conversation (hubspot2026customeragent; company news dated 13 April 2026).
- Fin AI Agent $0.99 per outcome, 50 outcomes a month minimum (fin2026pricing; https://fin.ai/pricing, fetched 29 Oct 2026). Fin Voice: the coordinator reports $1.99 per voice outcome from the author's browser; my fetch of fin.ai/pricing returned "offered on a custom pricing plan", so it is not verified here and not used.
- Salesforce Agentforce $2 per conversation; Flex Credits $500 per 100,000 credits, 20 credits ($0.10) per action; add-ons $125 per user a month (salesforce2026agentforce, https://www.salesforce.com/agentforce/pricing/).
- Not used: Freshworks Freddy AI Agent $49 per 100 additional sessions, first 500 included (a session is not defined as a resolution); Microsoft Copilot Studio credits (no per-task conversion); Sierra and Decagon (no public price).

Results at the ends of the ranges (every number is a check in the script; seat prices per month):
| Result | $55 | $100 | $25 | $550 |
|---|---|---|---|---|
| W (labor saving per seat / seat price) | 59.5 | 32.7 | 130.9 | 6.0 |
| Market conversion kap* W (holds if > 1) | 8.19 | 4.50 | 18.02 | 0.82 (fails) |
| Market multiple at full diffusion | x3.48 | x2.21 | x6.87 | x0.94 |
| Seat margin per resolution (share of V_I) | $0.149 (1.3%) | $0.271 (2.4%) | $0.068 (0.6%) | $1.493 (13.4%) |
| Cannibalizing capture share kap_can | 0.525 | 0.530 | 0.521 | 0.585 |
| Replacement cost (share of launch gain) | 2.8% | 5.0% | 1.3% | 25.9% |
| Launch now | yes | yes | yes | yes |
| Year-3 AI revenue share | 26.0% | 16.2% | | |
| Rule-of-40 change, value / cost-plus | +22.7 / +19.7 | +16.7 / +13.7 | | |

Where a conclusion changes: market conversion fails above a seat price of $450 a month at the model's capture share 0.138 (unchanged; the threshold does not depend on the vendor range). It also depends on the outcome price: at the lowest outcome list price ($0.50, kap = 0.045) conversion holds at $55 to $100 (kap W = 2.68 to 1.47) but needs seats below $147 a month; at the highest ($2.00, kap = 0.18) it needs seats below $589. The competitive price $1.53 lies inside the $0.50 to $2.00 range (2.8% to 11.1% of in-house cost; capture of V_I 0.045 to 0.18 against the model's 0.138). The replacement cost grows with the seat price, but launch-now holds at every published tier. Migration thresholds, the seat-loss path and revenue at risk are ratios and do not depend on the seat price. Compared with the earlier $85 to $115 range, no conclusion changes its holding range; the new range sits further inside every threshold.

Bass means: vandenbulte2004social (verified by the literature agent). The often-quoted p = 0.03, q = 0.38 for sultan1990meta appear only in secondary sources: Nam (2011), "Demystifying the Bass Diffusion Model", Rutgers working paper, https://web-docs.stern.nyu.edu/marketing/SNamPaper.pdf, and Mahajan, Muller and Bass (1995), Marketing Science 14(3), G79-G88, as cited by Wikipedia. Neither is used in the text.

Wage: bls2026oews. OEWS May 2025 national cross-industry file oesm25nat.zip (received by the data agent; `data/tasks/occupations.csv` row 43-4051, oews_vintage "May 2025"): median annual wage $44,770, mean $46,590, employment 2,595,750. O*NET OnLine (https://www.onetonline.org/link/localwages/43-4051.00) confirms $44,770 and $21.53 an hour from "BLS 2025 wage data". The bls.gov occupation page was not on the fetch allowlist.

Gilbert and Newbery (1982): verified as Gilbert, Richard J. and Newbery, David M. G., "Preemptive Patenting and the Persistence of Monopoly", American Economic Review 72(3), 514-526. Sources: RePEc author listing for Richard J. Gilbert (https://authors.repec.org/pro/pgi285: "by Gilbert, Richard J & Newbery, David M G", vol. 72, issue 3, pp. 514-26, handle aea:aecrev); IDEAS citation page (https://ideas.repec.org/r/aea/aecrev/v72y1982i3p514-26.html); Caltech record of Reinganum's reply, which cites "Gilbert and Newbery (1982), American Economic Review, 72, 514-26". No DOI or JSTOR link was verified, so none is given.

## 7. Literature

Cited (all keys exist in refs.bib, part2/refs_part2.bib, part2/refs_modern.bib or part2/refs_product.bib): arrow1962economic, bajari2019impact, bakos1999bundling, balasubramanian2015pricing, bass1969new, bergemann2025menu, bick2026rapid, brynjolfsson2025canaries, brynjolfsson2025generative, demirer2025emerging, eloundou2024gpts, essegaier2002pricing, farboodi2019big, farboodi2021model, farboodi2023data, fradkin2025demand, gans2024market, gilbert1982preemptive, gundlach2025price, hagiu2023data, freshworks2026pricing, hinterhuber2004towards, hubspot2026customeragent, hubspot2026servicepro, humlum2025still, iconiq2026state, fin2026pricing, jones2020nonrivalry, korinek2025concentrating, lambrecht2006paying, milgrom1994monotone, moorthy1992market, prufer2021competing, salesforce2026agentforce, salesforce2026finagree, salesforce2026finclose, salesforce2026servicepricing, shahidi2025coasean, shapiro1999information, sultan1990meta, sundararajan2004nonlinear, tomlinson2025working, vandenbulte2004social, bls2026oews.

The build therefore needs `\bibliography{refs,part2/refs_part2,part2/refs_modern,part2/refs_product}` (also on the lead author's integration list). New file `part2/refs_product.bib` (29 Oct 2026): gilbert1982preemptive (@article), bls2026oews, freshworks2026pricing, fin2026pricing, salesforce2026finagree, salesforce2026finclose, salesforce2026servicepricing, salesforce2026agentforce, hubspot2026servicepro, hubspot2026customeragent (@misc, accessed 29 October 2026). The HubSpot news URL is too long for one line, so its entry carries the full link in `\href` with a breakable display text (needs hyperref, which the main preamble loads). Compile test: no undefined citations and no overfull boxes from these entries; one overfull box (13.9pt) remains from a refs_modern.bib URL (futuretech.mit.edu, beyond-ai-exposure...), not this file.

Missing references: items 1 to 3 of the earlier list (vendor pricing pages, BLS OEWS May 2025, Gilbert and Newbery 1982) are now verified and cited from `part2/refs_product.bib`. Still optional and not cited: Reinganum (1983) on uncertain innovation and the persistence of monopoly (her reply, AER 74(1), 243-246, 1984, was seen on the Caltech record); a source for deferred-revenue shares in software.

## 8. Problems with the spec, and changes made

1. **17.2, "pricing-model migration protects revenue".** It does so only for the share of the new bill not indexed to seats, and at a concession. No tariff dominates (literature finding 19). I model a menu of target tariffs, including a two-part tariff and a seat-fee hybrid, and select by value. In the example, the two-part tariff wins.
2. **17.2, "competition pushes theta_cap toward the entrant's cost-plus floor".** This holds only as a free-entry limit. The floor is (1 + ups_E) chat_E, with ups_E > 0 for concentrated foundation-model supply (literature finding 20). The incumbent's price is the floor plus rho_u. When the cap binds, the incumbent keeps all of its own cost savings (pass-through 0). It passes through all of the entrants' savings.
3. **17.2, "rents come from proprietary data".** Under diminishing returns to data, a constant proportional data lead yields a vanishing rent, as prop:prod-price(e) proves (literature finding 21). Rents need a widening lead, tipping, workflows or switching costs. Buyer-side agents erode switching costs (shahidi2025coasean).
4. **17.2, "inference-price decline raises margins only to the extent prices are sticky".** Correct, but the relevant decline is that of the inference cost the product actually uses (delta_u). It can be far below the fixed-capability decline delta_pi. ICONIQ's path identifies only (1 - phi) delta_u, so the crossover date is not identified; two fits give 2030 and 2033, and a two-point change in the 2027 projection removes the crossover.
5. **17.3 item 2, "threshold at which migrating pays".** The threshold is on the proportional seat-loss rate nu: approximately (r - g) delta/[(1 - delta)(1 - e)] plus a term of order (r - g)^2. It is small when r - g is small. Its level, and every migration date and value, are conditional on scenario costs (class d) and on the seat elasticity (class d). In the example the two-part migration starts now at eps_seat = 1, waits half a year at 0.5 and never pays at 0.25. Phasing at renewal spreads the dip, which can be large (16% of revenue in the example if all at once).
6. **17.3 item 7, Arrow.** The replacement effect is governed by the seat-to-labor ratio. It is small for labor-substituting agents (2.8% to 5.0% of the launch gain across the professional seat tiers; 1.3% at $25 and 25.9% at $550, where launch-now still holds). The efficiency (preemption) effect is now cited to gilbert1982preemptive. Entry removes it entirely, because the seats are lost either way. Preemption matters only where seats are expensive relative to the work an agent can take. The result assumes commitment and non-strategic customers (literature finding 22, Moorthy and Png).
7. **17.1, "adoption over time using Bass diffusion".** Bass parameters for software and AI features are not in the meta-analyses; the verified means are for consumer durables. Defaults are marked assumed, and the engine should fit p and q to the firm's own seat and feature adoption data.
8. **Spec 17.5, "evidence on seat compression (likely thin)".** It is thin and mixed (brynjolfsson2025canaries vs humlum2025still). The modernization map also found no verified peer-reviewed study of outcome-based pricing of AI agents. The assumptions audit classes the seat elasticity and all migration costs as scenario-only (memo item 13). The text therefore introduces an explicit seat elasticity eps_seat, so that X = eps_seat X_h. It reports revenue at risk as a band ($40M to $160M over eps_seat in [0.25, 1]), labels every example illustrative and states migration results as conditional.
9. **Notation.** The spec's theta_cap clashes with Part I's theta; its f (features) clashes with fees; p, q (Bass) clash with process and reliability symbols and with theory_core's sans-serif p, q. All renamed (Section 2).
10. **Combined plan (17.3 item 5).** The product side moves mostly growth parameters (G_i, G, lambda), which are weighted at X - k. Much of the product-side score gain during diffusion is transient growth. Its integral is bounded (the log of the revenue gain). The engine must not capitalize it as a permanent Delta G_i.
11. **Example calibration changed after the audit.** The first draft assumed a quarter-hour per ticket ($8.01 in house). The examples now use the sourced $18.09 per resolution from params.yaml (1.7 resolutions an hour). The competitive price is then 8.5% of in-house cost, inside the 2.8% to 11.1% range implied by outcome list prices of $0.50 to $2.00; under the old calibration the capture share was 0.32, above that range.

12. **Vendor neutrality (author decision, 29 Oct 2026).** The single seat price and outcome range of the first draft are replaced by ranges across four vendors' list prices: seats $55 to $100 (professional tiers), outcomes $0.50 to $2.00. One vendor is left out entirely. Each example states its conclusion at both ends and where it changes over the published span ($25 to $550). Market conversion fails above $450 a seat-month (and above $147 at the lowest outcome list price). Vendors are named only in the source footnote.

13. **Heterogeneous switching costs (coordinator, 29 Oct 2026).** The lock-in cap used one switching premium. prop:prod-price(f) generalizes it to a distribution S_sw (independent of adoption frictions). The single premium is the degenerate case and the limit cv_sw -> 0 of the gamma family, so every existing number is unchanged. With the same $0.20 mean, gamma premia with cv_sw = 1, 0.5, 0.2 (scenario values) give prices $1.33, $1.37, $1.45 against $1.53, switching rents $0, $0.04, $0.12 against $0.20, and 0, 1.2%, 0.9% of the incumbent's customers lost to entrants; exponential premia earn a rent only above a mean of $1.03. Dispersion lowers the cap, and pass-through becomes partial in both directions (own savings partly passed on, entrants' partly kept), which qualifies the "0 own / 1 entrant" pass-through of part (c) and its use in Lemma prices and prop:prod-aggregate. The example keeps the single premium.

## 9. Coordination notes

- theory_ext now uses vartheta for altruism (it was omega_h). I therefore did not use vartheta for the capture share.
- theory_core uses sans-serif p (Pareto tail index), q (CVaR level), L (normal loss function), g (security residual factor) and k (errors caught). I avoided all of them. theory_regimes uses sans-serif o for the ownership regime.
- prop:prod-model builds on core prop:tasks-fullcost and prop:tasks-buildbuy (run costs favor buying) and prop:tasks-capital (capital charges). It adds rents and falling API prices.
- prop:prod-cannibal(b) and prop:prod-price(c) are the product-market versions of ext prop:ext-should(b): own savings kept, entrants' passed through (with a single switching premium; partial both ways under prop:prod-price(f)).
- theory_acquirer: prop:prod-price(f) uses the survival-function form of prop:acq-retention(a), per outcome instead of per bill; its exponential case matches the acquirer's exponential ratios, where the revenue-maximizing repricing is x-bar - 1.
- prop:prod-portfolio(a) uses ext prop:ext-customer(b) as the first-order value of retention at X = v_0.
- theory_regimes: with an exit-multiple or screening-type weight (prop:reg-weight), the dilution test of cor:prod-dilution and the retention ranking of prop:prod-portfolio(c) change. A PE owner acting on a weight near 2 to 3 would reject margin-dilutive retention features that a value-maximizing public owner at v_0 accepts. The engine should run the product scorecard at the regime's weight.
- Integration: the product engine needs the customer-side core module run on customers' occupations (for X(t)) and the ext capability path (feasibility dates).

## 10. Example parameters (help-desk vendor; all illustrative unless sourced; every quoted number is a check in the script)

All examples are labeled illustrative in the text.
- Customer: cH = $18.09 (sourced), t = 1/1.7 h, loaded w = $30.75/h; cO = $12.36, cU = $15.92; cbar = $12.36; t_R = 0.8 t; L = $30; e_I = 0.04, e_E = 0.066; eta_I = $0.05, eta_E = $0.20; V_I = $11.11, V_E = $10.18; p_sw = $0.20; rho_u = $1.13 (data 0.78, workflow 0.15, switching 0.20).
- Price: chat_I = chat_E = $0.40; eps = 1. kap^m = 0.518, p^m = $5.75 (adoption 48%); cap $1.53 binds, kap* = 0.138, adoption 86%, margin 73.8%; p*/cH = 0.085; chat_E^ddag = $4.63; long run $1.23 (kap 0.111). Pricing on in-house cost would ask $8.72. Data: 5.29x lead; rent $0.78, $0.25 (x10), $0.08 (x100).
- Seats: p_seat = $660 to $1,200/yr ($55 to $100 a month; span $25 to $550); gamma_seat = 0.80; seat revenue $400M of $500M; xbar_h = 0.40; RaR = eps_seat x $160M ($40M to $160M over [0.25, 1]). Durables Bass at eps_seat = 1: t* = 6.15 yr, peak Xdot 4.75%/yr, nu(0) 1.08%, nu peak 5.94% at 6.75 yr; peak 2.63% at eps_seat 0.5, 1.25% at 0.25. Fast: t* 2.31, nu(0) 4.0%, peak 12.5% at 2.62 yr.
- Migration (r = 0.10, g_v = 0.04; scenario costs): nu* = 1.23% (usage), 0.66% (two-part), 0.65% (hybrid). Durables, eps_seat = 1: two-part and hybrid migrate now; usage at 0.32 yr. Values: two-part $745M / $1,033M (fast); usage $415M / $683M; hybrid $415M / $574M. Two-part across eps_seat: 1: now, $745M; 0.5: 0.50 yr, $163M; 0.25: never (V(2.49 yr) = -$110M). Two-part one-time cost 16% of revenue.
- Features (S = $500M, X = 9, r - g° = 0.05, platform $15M, 60 engineer-years): NPVs agent $482M, copilot $272M, QA $99M, voice $108M; per engineer-year 19.3, 22.7, 6.6, 3.6; optimum {agent, copilot, QA}, $838M net; at X = 2.5 copilot $102M.
- Sourcing: api 0.40/0.30 inference, $1M/yr; open 0.22 + K 0.10, $4M/yr, +0.10 rent; own 0.15 + K 0.08, $15M/yr, +0.30 rent; delta_K = 1/3. Thresholds 12.7M and 39.5M; at 20M open; open loses its unit-cost edge at 0.97 yr; long-run build threshold 65M.
- Margins: ICONIQ fit 1: 0.147/yr, crossover 2030.1, phi = 0.91 at delta_u = ln 5, 0.79 at ln 2, 0.51 at 0.30. Fit 2: floor 0.23, decline 0.288, gamma_inf 0.77, crossover 2033.2; with 57% in 2027, gamma_inf 0.61. Limit pricing 73.8% now, 91.9% at floor (rent/floor 11.3 vs 2.85 needed). Blended: w-bar 0.35, Bass (0.08, 0.6): trough 72.5% in year 2.7, back to 74% at 5.1.
- Cannibal: m_seat = $0.149 to $0.271/resolution (s = 1.3% to 2.4%, W = 59.5 to 32.7) at $55 to $100; kap_can 0.525 to 0.530; replacement cost 2.8% to 5.0%; at $25: $0.068, 1.3%; at $550: $1.493, kap_can 0.585, 25.9%; launch now at every tier; c_eff (no entry) $0.55 to $0.67, $1.89 at $550. Professional seats: $6,000/yr, t = 1 h, gamma 0.85: m_seat $2.45; V $2.20, chat $0.50, gap $0.75; p_sw $0.40: nu_E* = 0.113 (8.9 years); at nu_E = 0.25: c_eff $1.29, p_L $1.74.
- Aggregate: D_m = 0.03, Delta G = 0.01: +6.0 pts at X = 9, -0.5 at X = 2.5; frontier crossing at g = 0.57 (Part I figure parameters), dual weight 3.2. TAM x2.21 to x3.48 at $100 to $55 (kap*W = 4.50 to 8.19, 1/W = 3.1% to 1.7%); x6.87 at $25; x0.94 at $550 (kap*W = 0.82, fails); conversion threshold $450 a seat-month ($147 at the $0.50 outcome price, $589 at $2.00). Year-3 scorecard at eps_seat = 1, $100: AI share 0.162, AI margin 0.917 (ICONIQ path 0.647); rows: mix +1.89 (ICONIQ -2.47), features +0.30, ops COGS +3.00/0, opex +2.00, k +8.24 (score -1.24), compression +2.10, AI expansion +8.36, retention +0.17, pull 1.21% (+0.06); Rule of 40 +16.7 (value pricing) / +13.7 (cost-plus); transient growth 10.5 pts. At $55: AI share 0.260; mix +3.04 (ICONIQ -3.97), features +0.27, compression +1.86, AI expansion +13.43, k +7.27 (score -1.09); Rule of 40 +22.7 / +19.7.
- Breakpoints: chat_E^ddag = $4.63; T_C = 0.49 yr for an entrant starting at $10.00.
