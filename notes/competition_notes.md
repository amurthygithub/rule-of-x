# Competition notes: strategic adoption among incumbents (spec 24.7)

Files:
- `part2/theory_competition.tex`: `\subsection{Strategic adoption among incumbents}\label{sec:ext-game}`. It is meant for the commented slot at the end of Section `sec:ext-competition` in `theory_ext.tex` (`% \input{part2/theory_competition.tex}`). Input it there only, not also from `paper.tex`.
- `part2/proofs_competition.tex`: `\subsection{Proofs for Section~\ref{sec:ext-game}}\label{app:proofs-game}`. It is a subsection, so input it at the end of `part2/proofs_ext.tex` (inside `app:proofs-ext`).
- `part2/refs_competition.bib`: 7 new verified entries. Add `part2/refs_competition` to the `\bibliography{...}` list. The log is `notes/ref_verification_competition.md`.
- `code/verify_part2_competition.py`: 43 checks, all passing (`python3 code/verify_part2_competition.py`, about 20 s, exit code 0 iff all pass). Every number quoted in the tex is printed with `->` and asserted, and check T1 confirms that each quoted string appears in the tex. T2 checks the table rows against the script, T3 checks for em-dashes, T4 checks citation keys, and T5 checks the internal labels.

Build status (29 Oct, scratch harness with Part I's preamble, `sections/model.tex`, `theory_core.tex`, `theory_ext.tex`, this subsection, `theory_product.tex`, `sections/appendix_proofs.tex` and the proofs file): there are no LaTeX errors and no overfull boxes in these two files, and all eight citation keys resolve. In the 11pt layout the subsection runs about 5.5 pages, including Table `tab:ext-game-dur`, and the proofs about 3 pages.

---

## 1. Results (labels)

- `ass:ext-game` (Assumption: adoption game). n_c incumbents. One bundle each cuts unit cost by δ_c = Σ_j B_j v_j / Y. Adoption cost F_A(T) = F0 e^{−δ_F T}. Flows e^{Gt} E_a(k). Adoptions are strategic substitutes. Single-firm date T°(E), eq `eq:ext-game-To`.
- `eq:ext-game-values`: the duopoly leader, follower and joint values V^L, V^F, V^J (Fudenberg and Tirole).
- `lem:ext-game-pass` (pass-through and incentives):
  - (a) Linear family. This covers Cournot (Lemma ext-retained) and differentiated Bertrand, parameterized by own, industry and cross pass-through.
  - (b) General Cournot to first order: φ̄^ind = n/(n+1−e), φ̄^own = φ̄^ind/n, and the common and private gains (eq `eq:ext-game-first`). The common gain is the Weyl and Fabinger incidence formula.
  - (c) Constant elasticity: φ = 1. E^eq has the sign of ε − 1 exactly. The private gain is positive iff ε > (2n−1)/(2n²−2n+1).
- `prop:ext-game-preempt`:
  - (a) Precommitment (Reinganum): T_k = T°(E^priv(k−1)), with diffusion among identical firms.
  - (b) Duopoly preemption (Fudenberg and Tirole): the first adoption comes at T^P < T_D < T_1 < T_2, with rent equalization.
- `prop:ext-game-wait`:
  - (a) Late joint adoption: equilibrium iff V^J(T) ≥ V^L(T_1). Existence condition `eq:ext-game-joint`.
  - (b) Learning about ϖ: if ϖ ≤ ϖ̄ = E^priv(1)/[E_1(0) − E_0(1)], the follower is worth more than the leader at every date.
  - (c) War of attrition: asymmetric equilibria at T^W = T°(ϖ E^eq). The symmetric equilibrium uses the hazard ν^W of `eq:ext-game-hazard`.
- `prop:ext-game-pd` (automation prisoner's dilemma):
  - (a) Static window [E^eq, E^priv(n−1)). First-order version `eq:ext-game-window`.
  - (b) Pure dilemma iff φ̄^ind > n/(n−1), equivalently e > 2, or ε < 1 under constant elasticity.
  - (c) Dynamic test `eq:ext-game-dyn`.
  - (d) Rule of X: exact margin identity, revenue and growth effects, and the value effect through Prop dynamic(a).
- `prop:ext-game-entry` (AI-native entry):
  - (a) After T̄_M there is no strategic interaction, and the firm adopts at max{t, T°(δ_c Y)}.
  - (b) Deterrence schedule: the j-th adoption must come by T_M(j−1).
  - (c) Defensive window [(P_E∞ − P_0 + δ_c)Y, δ_c Y).
  - (d) Free-replication limit: the margin is at most p_sw plus any scarce-input advantage.
- `cor:ext-game-engine`:
  - (a) Durable share dur(HHI) (eq `eq:ext-game-dur`), private share priv(HHI), and the partial-replication interpolation.
  - (b) Classification by NPV^dur and NPV^priv.
  - (c) Expected durable gain against concentration.
  - Table `tab:ext-game-dur`.

## 2. Notation and deviations

| Symbol | Meaning | Note |
|---|---|---|
| n_c | number of incumbents (the spec's N) | N(T) is already the net flow of prop:ext-timing; n_c as in Lemma ext-retained |
| HHI | Herfindahl index of incumbents; n_c = 1/HHI for symmetric firms | H is the capability horizon H(t) |
| δ_c | unit-cost cut of the bundle = Σ_j B_j v_j / Y | as in prop:ext-should |
| E_a(k), E^priv(k), E^eq | flow earnings in state a with k rival adopters; private gain; gain when all adopt | 𝓔 as in prop:ext-should(a); profit is not π (π is the inference price) |
| φ̄^own, φ̄^ind, φ̄^× | level pass-through of a unilateral saving, of a common saving, and of one rival's saving | φ̄ as in Lemma ext-retained; φ (no bar) is Lemma prices' elasticity |
| 𝖾 (\mathsf e) | curvature −Q P''/P' of inverse demand | E, κ, ϰ, ε are taken |
| ε (\epsilon) | price elasticity of industry demand | as in Lemma prices(b) |
| T°(E) | single-firm date for gain flow E | eq:ext-game-To |
| V^L, V^F, V^J | leader, follower, joint values | FT's L, F, M; \mathsf L is taken by the product section |
| T_1, T_2, T_D, T^P, T_J, T^W | leader optimum, follower date, peak preemption incentive, preemption date, joint optimum, start of the war of attrition | |
| ϖ, ϖ̄ | probability the bundle works for the industry; threshold for second-mover advantage | ϖ as in the core |
| ν^W(t) | war-of-attrition hazard | h is reserved (headroom); ν is used for hazards in Part II |
| 𝒦 | annualized adoption cost | as in prop:ext-should(a) |
| B_q | earnings scale in the linear family (B for Cournot, 1 for normalized Bertrand) | b is reserved |
| s_B, A_B | Bertrand substitution parameter and intercept (own slope normalized to 1) | α, β, γ are reserved |
| P_E(t), P_E∞, T_M(k), T̄_M | entrants' limit price ĉ_E + p_sw; breakpoint with k adopters; breakpoint whatever incumbents do | extends prop:ext-should(b) |
| dur, priv, rep | durable and private shares of δ_c Y; share of rivals that can replicate | rep as in Lemma ext-retained |

**Report to the lead author (house rule: notation and results changes).**
1. **Definition ext-motives understates the durable gain.** Its retained share, (1 − φ̄) = 1/(n_c + 1) when all rivals replicate, counts the change in unit margin at fixed volume. The first-order durable share also counts the volume response, dur = 1 − φ̄^ind(1 − 1/n_c), which is 2/(n_c + 1) under linear Cournot: twice as large. Recommendation: the engine uses dur (and priv for savings no rival can make) in place of (1 − φ̄_j) in NPV_j. cor:ext-game-engine(b) states the refined classification. The example gives NPV^dur = −12.0, NPV^priv = 12.0 (defensive), against −16.0 under the fixed-volume rule.
2. **"Defensive" now has two cases**, both in the paper already: the strategic case of prop:ext-should(a) (NPV^dur ≤ 0 < NPV^priv) and the viability case of def:ext-motives(ii). The corollary names both. The engine should label them `defensive-strategic` and `defensive-viability`.
3. **Prop entry and the entrant change private incentives.** Once entry binds, the gain from adopting falls from E^priv (which includes business stealing) to δ_c Y. Entry can therefore *delay* a non-adopter's date unless viability binds. The engine should not assume that entry always accelerates adoption: it accelerates adoption only through the viability deadline of prop:ext-should(e).

## 3. Formulas the engine must implement (module `competition`, new submodule `game`)

### 3.1 Inputs

| Input | Tier | Default and source |
|---|---|---|
| number of competitors n_c, or the HHI of the relevant market (n_c = 1/HHI) | Tier 3 market input | **free scenario parameter (grounding class d)**; no default. Report results for n_c ∈ {2, 4, 10} |
| industry pass-through φ̄^ind (level, common cost), if measured | Tier 3 | otherwise derived: n_c/(n_c + 1 − e) |
| curvature e = −QP''/P' | assumed | 0 (linear) as the base case; 1 + 1/ε if constant elasticity is chosen |
| price elasticity of industry demand ε | Tier 3 or assumed | scenario values 0.8 (inelastic) and 2 (elastic) for the constant-elasticity case; linear base case otherwise |
| margin before adoption mg, price P, unit cost ĉ, output Y | Tier 0 to 1 (from the firm's financials) | firm data |
| unit-cost cut δ_c | from the activity model: Σ_j B_j v_j / Y | firm data |
| adoption cost F0, decline δ_F | from prop:ext-timing inputs (F_A, transition costs 𝒯) | firm data |
| success probability ϖ | core eq:tasks-success | firm data |
| share of rivals that can replicate, rep | assumed, default 1 for commodity automation (no scarce input), 0 for data- or context-dependent savings | scenario parameter |
| entrant cost path ĉ_E(t), switching premium p_sw | from prop:ext-should inputs | firm data |
| r, G | Part I | firm data |

### 3.2 Pass-through and the shares (first order; lem:ext-game-pass(b), cor:ext-game-engine(a))

```
H        = HHI  (= 1/n_c for symmetric firms)
phi_ind  = n_c/(n_c + 1 - e)            # if not supplied; requires n_c + 1 - e > 0
phi_own  = phi_ind/n_c
phi      = phi_ind * c/P                # Lemma prices elasticity
dur      = 1 - phi_ind*(1 - H)          # = (2 - e)/(1/H + 1 - e);  linear: 2H/(1+H);  CES: H(eps-1)/(eps-H)
priv     = 2 - H - H*(1 - H)*phi_ind    # linear: 2/(1+H)
dur_rep  = (1 - rep)*priv + rep*dur     # partial replication
pure dilemma flag: phi_ind > n_c/(n_c-1)  (<=> e > 2; CES <=> eps < 1)
CES private-gain check: eps > (2n_c-1)/(2n_c^2-2n_c+1)
```

### 3.3 Exact earnings in the linear family (lem:ext-game-pass(a)); use these when mg, δ_c are known

```
Cournot:   phi_own = 1/(n_c+1), phi_x = 1/(n_c+1), phi_ind = n_c/(n_c+1), B_q = B = mg/Y
Bertrand:  phi_ind = 1/(2-(n_c-1)s_B), phi_x = s_B*phi_ind/(2+s_B), phi_own = 1/(2+s_B) + phi_x, B_q = 1
E1(k) = (mg + (1-phi_own)*d - k*phi_x*d)^2 / B_q
E0(k) = (mg - k*phi_x*d)^2 / B_q                     # need mg > (n_c-1)*phi_x*d
Epriv(k) = E1(k) - E0(k);  Eeq = E1(n_c-1) - E0(0)
```

### 3.4 Timing (prop:ext-game-preempt, prop:ext-game-wait)

```
To(E) = max(0, ln((r+dF)*F0/E)/(G+dF)) if E > 0 else inf          # requires G + dF > 0
open loop (any n_c):   T_k = To(Epriv(k-1)), k = 1..n_c;  compare with To(d*Y) (single firm, given prices)
duopoly (n_c = 2):
  T2 = To(Epriv(1)); T1 = To(Epriv(0)); TD = To(E1(0) - E0(1)); TJ = To(Eeq)
  I(a,b) = (e^{-(r-G)a} - e^{-(r-G)b})/(r-G);  cost(t) = F0 e^{-(r+dF)t}
  VL(t) = E0(0) I(0,t) + E1(0) I(t,T2) + E1(1) I(T2,inf) - cost(t)        (t <= T2)
  VF(t) = E0(0) I(0,t) + E0(1) I(t,T2) + E1(1) I(T2,inf) - cost(T2)       (t <= T2)
  VJ(t) = E0(0) I(0,t) + E1(1) I(t,inf) - cost(t);   VL = VF = VJ for t >= T2
  preemption date TP: root of VL - VF on (0, TD) by bisection (TP = 0 if VL(0) >= VF(0)); rents VL(TP) each
  joint-waiting flag: VJ(TJ) >= VL(T1)  (TJ = inf: E0(0)/(r-G) >= VL(T1)); joint window [T_lo, TJ] with VJ(T_lo) = VL(T1)
learning (success probability varpi):
  varpi_bar = Epriv(1)/(E1(0) - E0(1))                       # sufficient for war of attrition
  exact threshold: max_t [VL_w - VF_w] = 0, with the max over t in {0, T2, To(varpi*(E1(0)-E0(1)))}
  VL_w(t) = varpi VL(t) + (1-varpi)(E0(0)/(r-G) - cost(t));  VF_w(t) = varpi VF(t) + (1-varpi) E0(0)/(r-G)
  TW = To(varpi*Eeq)
  hazard nu_W(t) = (varpi*Eeq*e^{Gt} - (r+dF)F_A(t))/((1-varpi)F_A(t)) for t >= TW
  integrated (TW > 0): Hc(s) = (r+dF)/(1-varpi) * ((e^{(G+dF)s} - 1)/(G+dF) - s)
  P(first adoption later than TW + s) = exp(-2 Hc(s));  mean delay = int_0^inf exp(-2 Hc(s)) ds
report: n_c > 2 -> open-loop dates [T_1, T_n] (flag that closed-loop play can cluster, Argenziano and Schmidt-Dengler 2014);
        n_c = 2 -> TP and T2; joint-waiting flag and window; if varpi <= exact threshold -> TW, mean and median delay
```

### 3.5 Dilemma tests (prop:ext-game-pd)

```
static window: Eeq <= K < Epriv(n_c-1)   (K annualized adoption cost)
dynamic, last adopter: Eeq <= (r-G) e^{-G T_n} F_A(T_n);  for T_n > 0: Eeq <= (r-G)/(r+dF) * Epriv(n_c-1)
  linear first order: n_c >= (r+dF)/(r-G)
Rule of X (b = 0):
  margin change (exact) = (Eeq - K - m0 (S1 - S0))/S1
  revenue change (first order) = -(1-eps)*phi*d/c;  enters measured growth once, weight X
  growth effect of a continuing unit-cost decline delta_u: -(1-eps)*phi*delta_u per year (Lemma prices(b))
  CES: margin change = -K/S1 exactly; value M v(s) scales with M, factor (1 - d/c)^{1-eps}
```

### 3.6 Entry (prop:ext-game-entry)

```
P_k = P0 - k d/(n_c+1);  PE(t) = cE(t) + p_sw;  PE_inf = cE_inf + p_sw
T_M(k) = first t with PE(t) < P_k;  Tbar_M = T_M(n_c)
after Tbar_M: gain = d*Y (no business stealing); non-adopter adopts at max(t, To(d*Y)) unless the viability deadline binds
deterrence: never binds iff the j-th adoption is by T_M(j-1) for j <= kbar = min{k: P_k <= PE_inf}
long run (PE_inf < P_n): adopt vs not = d*Y - K;  vs before AI = (PE_inf - P0 + d)*Y - K
  defensive iff (PE_inf - P0 + d)*Y <= K < d*Y;  all worthwhile adoption defensive if PE_inf <= P0 - d
  needed for viability iff PE_inf < c0;  secures viability iff PE_inf >= c0 - d + K/Y
  dur_E = (PE_inf - P0 + d)/d, priv_E = 1
```

### 3.7 Classification (cor:ext-game-engine(b)); replaces (1 − φ̄_j) in def:ext-motives for replicable savings

```
NPV_dur  = varpi * dur  * d*Y/(r-G) - T_trans
NPV_priv = varpi * priv * d*Y/(r-G) - T_trans
value-creating        if NPV_dur > 0
defensive-strategic   if NPV_dur <= 0 < NPV_priv
defensive-viability   if in the least-cost viability set (prop:ext-should(d))
could-not-should      otherwise (feasible); not feasible as before
date: strategic date of 3.4, capped by T_M - lead time (prop:ext-should(e))
expected durable gain a year = varpi*dur(HHI)*d*Y - K   (rises with concentration iff e < 2)
```

## 4. Default and example parameters

All values in the examples are illustrative (grounding class d, scenario parameters), as house rule 21.1 requires. None is a baseline estimate.

| Parameter | Example value | Grounding |
|---|---|---|
| price, unit cost, cut, volume | 1.00, 0.80, 0.10, 20 million units | illustrative; same per-firm numbers as prop:ext-should(a) (mg = 0.20, δ_c = 0.10, B = 0.01) |
| r, G | 0.10, 0.04 | Part I examples |
| F0, δ_F | $20 million, 0.30 | prop:ext-timing example |
| ϖ | 0.5 (war of attrition), 0.6 (classification) | illustrative; the core's eq:tasks-success supplies the engine value |
| ε | 0.8 and 2 | scenario |
| entrant cost path | 0.70 + 0.50 e^{−0.4t}, p_sw = 0.05 | illustrative, same form as prop:ext-should's example |
| Bertrand s_B | 0.2 | illustrative |

## 5. Key numbers (all asserted by the script)

- Four-firm Cournot: private gains $3.84, 3.52, 3.20, 2.88m a year. Open-loop dates 2.16, 2.41, 2.69, 3.00 years, against the single-firm date of 4.08. The durable gain alone would cover the user cost only after 6.63 years.
- Duopoly: T^P = 0.63, T_D = 1.80, T_1 = 2.78, T_2 = 3.23. Rents are $78.2m each, against $81.1m for an unchallenged leader and a status quo of $66.7m. Joint-waiting window [3.32, 5.03], worth up to $81.8m. Joint waiting exists at every cut with T_2 > 0 in this market. With a cut of 0.31 and F0 = 80 it does not, and preemption at 0.66 years is the outcome. A discrete-time check converges to T^P.
- Learning: ϖ̄ = 0.615, exact threshold 0.893. At ϖ = 0.5, T^W = 7.07, with mean delay 1.52 and median 1.46 years. Each firm is worth $73.4m, against $74.0m for the follower.
- Dilemma: window [0.84, 2.88), against the first-order [0.8, 3.2). The dynamic threshold is 0.15. The ratio is 0.29 with four firms (no dilemma) and 0.125 with ten (the last adopter loses $2.73m). With a constant cost, each of four firms loses $6.0m although the private gain is worth $48m.
- Rule of 40: linear revenue +1.2%. The margin rises from 20.0% to 23.9% before 𝒦 and is 19.8% at 𝒦 = E^eq. CES ε = 0.8: revenue −3.1% with the margin of 31.25% unchanged; a continuing 5% cost decline costs 1 point of growth.
- Entry: T_M(k) = 1.73, 1.94, 2.17, 2.42, 2.70. The post-entry adoption date is 4.08. Non-adopters lose money from 5.76. The long-run margin is 0.05 (against 0.20 before AI). Defensive window [−3.0, 2.0).
- Table tab:ext-game-dur: linear dur 1.00, 0.67, 0.50, 0.40, 0.29, 0.18 for n_c = 1, 2, 3, 4, 6, 10.

## 6. Verification summary (43 checks)

- A1 to A7: closed forms against direct equilibrium solves:
  - linear Cournot and Bertrand on random draws;
  - first-order formulas under five demand curves, by finite differences;
  - a symbolic derivation;
  - constant-elasticity identities;
  - the example values.
- B1 to B6:
  - open-loop best responses, by grid search over deviations in 40 random markets;
  - closed forms against quadrature;
  - the shape and ordering of V^L − V^F on random duopolies;
  - a discrete-time Fudenberg and Tirole limit, solved by backward induction with symmetric stage equilibria.
- C1 to C7:
  - the joint-adoption condition, by brute force over deviations;
  - never adopting when E^eq ≤ 0;
  - the second-mover advantage on 300 random duopolies;
  - the exact learning threshold;
  - war-of-attrition monotonicity, the hazard and the indifference condition by numerical integration;
  - the example numbers.
- D1 to D8 (including D6b):
  - dominance and the window;
  - first-order shares;
  - the pure-dilemma equivalence;
  - the dynamic bound on 200 random markets;
  - duopoly preemption against the status quo;
  - examples;
  - the Rule-of-X identity and first-order terms.
- E1 to E5: the entry breakpoints, post-entry independence, the deterrence schedule on random paths, the defensive window and the free-replication bound.
- F1 to F4:
  - the share formulas (symbolic);
  - partial replication (numerical, four demand curves);
  - the table;
  - the classification example.
- T1 to T5: text consistency, table rows, em-dashes, citation keys and labels.

## 7. Limits and open items for the lead author

- The closed-loop game for n_c > 2 is not characterized. Fudenberg and Tirole state that rent equalization does not carry over to oligopoly, and Argenziano and Schmidt-Dengler (2014) show uniqueness and clustering in a related game. The engine reports precommitment dates for n_c > 2.
- Simplifications:
  - Firms are symmetric, and asymmetric firms are approximated by n_c = 1/HHI.
  - There is one bundle per firm, and adoption costs are deterministic except for the binary learning case.
  - Detection of the leader's outcome is immediate. With a detection lag T_det, as in the core, the follower's advantage is smaller.
- The Rule-of-X results set b = 0. With capital, add (r − G)k to every score as in Prop entry.
- The post-entry installed-base assumption (Assumption ext-entrant) removes business stealing. If incumbents could win new customers after entry, the post-entry private gain would exceed δ_c Y.
- Assumption register entries to add:
  - n_c or HHI, curvature e, ε, rep: class (d) scenario parameters;
  - empirical pass-through: class (a) if the firm supplies a measured value.
- Build note (not in these files): in a scratch build, the statute entries of `part2/refs_labor.bib` (for example `de2026betrvg`) raise "Undefined control sequence \s" errors. The cause is that `plainnat` lowercases titles, turning `\S` into `\s`. Bracing the section signs in those titles (`{\S}`) fixes it. The owner of that file should make the change.
