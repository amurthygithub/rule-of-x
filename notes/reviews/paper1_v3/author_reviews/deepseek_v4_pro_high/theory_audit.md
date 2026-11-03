# Theorem Audit — "The Rule of 40 as a Price Line" (Nov 2026)

**Auditor:** theory-adversary (referee team)
**Date:** 2026-11-03
**Method:** independent hand re-derivation + independent numpy/scipy/sympy scripts in `/root/tmp/theory_audit/` (NOT the author's `code/verify_theory.py`). All equations re-derived from Assumptions 1–8 and Definition 1 directly. Blind-pass rule honored (did not read `repo/rule-of-x/notes/reviews/`).

---

## 0. Summary verdict

| # | Result | Classification | Key condition / caveat |
|---|--------|----------------|------------------------|
| 1 | Lemma 2 (max score, eq. 5–7) | **CORRECT** | interior iff `X > k`; corner iff `X ≤ k` |
| 2 | Proposition 1 (score budget, eq. 11–12) | **CORRECT** (sharp) | **conditional on `g ≥ G`** ("no share lost without spend") |
| 3 | Proposition 2 (dynamic optimality, HJB 17, root 19) | **CORRECT** | parts (b),(c) conditional on **unproved hypothesis (H)**; (a),(d),(e) unconditional |
| 4 | Proposition 4 (free entry) | **CORRECT** | standard Cournot; entry at date 0 only |
| 5 | Proposition 5 (accountability floor) | **CORRECT** | — |
| 6 | Proposition 6 (attainable frontier) | **CORRECT** | — |
| 7 | Proposition 7 (expected frontier) | **CORRECT** | — |

**No errors found.** All central propositions are correct under their stated assumptions. Four places are *conditional* and the paper is transparent about each (see §7):

- Lemma 1(a),(c) — "frontier is the graph of `m*`" and "strictly decreasing" require `k ≥ 0`.
- Proposition 1 — finiteness of the budget requires zero-spend growth `≥ G`.
- Proposition 2(b),(c) — conditional on hypothesis (H), which is explicitly **not proved**.
- Convexity of the feasible set — requires the "capital installed one period ahead" timing convention (Lemma S1).

---

## 1. Lemma 2 (maximal Rule-of-X score), eq. (5)–(7)

### 1.1 Hand derivation

Setup: `g = G + ℓ σ^α`, `ℓ = λ h(s)`, `h = 1 − s/s̄`, `α ∈ (0,1)`, `β = 1/α`, `κ = ℓ^(−β)`, `y = X − k`, `Cα = (1−α) α^{α/(1−α)}`.

Frontier (Lemma 1): `m*(g) = m0 − k g − κ (g−G)^β`. Score along frontier, with `Δ = g − G`:

```
R_X = X g + m*(g) = m0 + (X−k)(G+Δ) − κ Δ^β = m0 + y G + S(Δ),   S(Δ) = y Δ − κ Δ^β .
```

FOC `S′(Δ) = y − β κ Δ^{β−1} = 0`:

```
β κ (Δ*)^{β−1} = y
  =>  Δ* = (y/(βκ))^{1/(β−1)} = (y α ℓ^{1/α})^{α/(1−α)} = ℓ^{1/(1−α)} (α y)^{α/(1−α)} .   (5) ✓
```

(used `β−1 = (1−α)/α`, `κ = ℓ^{−β} = ℓ^{−1/α}`.)

Spend: `σ* = κ (Δ*)^β = Δ* · κ(Δ*)^{β−1} = Δ* · y/β = α y Δ*`. Substituting (5), `σ* = (α ℓ y)^{1/(1−α)}`. **(6) ✓**

Surplus: `S(Δ*) = y Δ* − κ(Δ*)^β = y Δ* − Δ*(y/β) = (1−α) y Δ*`, hence

```
R*_X = m0 + y G + (1−α) y Δ* = m0 + (X−k)G + Cα (ℓ (X−k))^{1/(1−α)} .   (7) ✓
```

Margin at optimum: `m*(g*) = m0 − k g* − σ* = m0 − k g* − α y Δ*`.

**Tangency:** `m*′(g) = −k − β κ (g−G)^{β−1}`, so at `g*`: `m*′(g*) = −k − βκ(Δ*)^{β−1} = −k − y = −X`. ✓

**Duality:** `X(g) = −m*′(g) = k + β κ (g−G)^{β−1}`; `g = G` is the maximizer iff right-derivative `R_X′(G+) = X − k ≤ 0`. ✓

### 1.2 Independent numeric check (sympy + numpy)

Parameters from Figure 1 (`m0=.45, G=.10, k=.10, α=.3, ℓ=.6`):

```
X=1: Δ*=0.2672, g*=0.3672, σ*=0.0721, R*=0.7083, m(g*)=0.3411,  m*′(g*)=−1.0000
X=2: Δ*=0.3681, g*=0.4681, σ*=0.2098, R*=1.1295, m(g*)=0.1934,  m*′(g*)=−2.0000
```

Matches Figure 1 exactly (g*=38%, m=34%, R1*=71; g*=48%, m=19%, R2*=114). Tangency condition `m*′(g*)=−X` holds to machine precision.

**Verdict: CORRECT.** (Sympy re-derivation of `m*`, `m*′`, `m*″`, `S′`, `S″`, and the FOC reproduce (4)–(7) exactly.)

---

## 2. Proposition 1 (score budget), eq. (11)–(12) — the "novel" result

### 2.1 Hand derivation

Given: single market growing at `G`, cap `s̄`, growth `≥ G` whatever spend, margin `m ≤ m0 − σ − kg`, `X > k`, `R∞ = m0 + (X−k)G`.

```
R_X = X g + m ≤ X g + m0 − σ − k g = m0 + (X−k) g − σ = R∞ + y Δ − σ ≤ R∞ + y Δ ,
```

using `Δ = g − G ≥ 0` and `σ ≥ 0`. Hence pointwise

```
(R_X − R∞)^+ ≤ y Δ .                                                        (P1-pointwise)
```

Integrating with `ṡ/s = Δ` (so `∫₀^T Δ dt = ln s(T)/s0`):

```
∫₀^T (R_X − R∞)^+ dt ≤ y ln s(T)/s0 < y ln s̄/s0 .                            (11) ✓
```

**Discrete** (period rates, `G > −1`): `s_{t+1} = s_t (1+g_t)/(1+G)`, `g_t ≥ G`, `m_t ≤ m0 − k g_t`. Then `R_{X,t} − R∞ ≤ y(g_t − G)`, so

```
1 + (R_{X,t}−R∞)^+ / [y(1+G)] ≤ 1 + (g_t−G)/(1+G) = (1+g_t)/(1+G) = s_{t+1}/s_t .
```

Logging and summing: `Σ ln(1 + (R_{X,t}−R∞)^+/[y(1+G)]) ≤ ln s_T/s0 ≤ ln s̄/s0`. **(12) ✓**

### 2.2 Critical examination (the task's four questions)

1. **Is the bound correct?** Yes. It is a *one-line* consequence of three things: (a) margin can only be **wasted downward** (`m ≤ m0 − σ − kg`, the top of the feasible set); (b) `σ ≥ 0`; (c) `Δ ≥ 0`. None can be relaxed.
2. **Can margins be "wasted upward"?** **No.** In Definition 1 the feasible set is `m ≤ m0 − σ − kg`; "waste" strictly *lowers* `m`, hence *lowers* `R_X`. There is no way to raise `m` above the frontier within the model, so the pointwise bound cannot be violated by margin choice.
3. **Can `Δ` be negative?** **No**, under Assumption 2 (zero spend delivers `G`, and growth cannot be traded below `G` for margin). This is exactly the condition the budget's finiteness rests on — see §7(i).
4. **Is it genuinely sharp?** **Yes.** Proposition S2 constructs, for any `Δ↓0`, a path holding excess growth constant at `Δ` up to `s₁→s̄`; `σ̄₁ = (Δ/(λh(s₁)))^{1/α}` and `σ̄₁/Δ = Δ^{β−1}(λh(s₁))^{−β} → 0`, giving `∫(R_X−R∞)^+ ≥ y ln(s₁/s0)(1 − σ̄₁/(yΔ)) → y ln(s̄/s0)`. The supremum equals `y ln(s̄/s0)`; it is **approached but not attained** (only by `Δ→0`, i.e. arbitrarily slow spending). The constant cannot be improved.

### 2.3 Example numbers (Corollary 1) — verified

With `X=1, k=0, m0=0.6, G=0.2` (`R∞=0.8, y=1, 1+G=1.2, s̄=0.5`):

```
R̄=10, s0=0.01  :  T ≤ ln50 / ln(1+9.2/1.2) = 3.912/2.159 = 1.812  → 1 year   (paper: 1.8)  ✓
R̄=1.4, s0=0.01 :  T ≤ 3.912/0.4055 = 9.648 → 9 years                              (paper: 9.6)  ✓
R̄=10, s0=1e-5  :  T ≤ 10.820/2.159 = 5.010 → 5 years                              (paper: 5.0)  ✓
continuous      :  y ln(s̄/s0)/(R̄−R∞) = 3.912/9.2 = 0.4252 yr                     (paper: 0.43) ✓
static optimum  :  (1−α)·0.4252 = 0.2977 yr                                        (paper: 0.30) ✓
```

Independent simulation of the *myopic static-optimum* path (σ*(ℓ(s),X) at every date) gives `∫(R_X−R∞)^+ = 2.738 ≤ ∫ yΔ = 3.911 ≈ y ln(s̄/s0) = 3.912`, bound satisfied.

**Verdict: CORRECT and sharp**, conditional on `g ≥ G` (stated explicitly; see §7(i)).

---

## 3. Proposition 2 (dynamic optimality): HJB (17), verification (b), root (19)

### 3.1 HJB re-derivation (17) — CORRECT

With `V(S,M) = M v(s)`, `V_S = v′(s)`, `V_M = v(s) − s v′(s)`, `ṡ = s Δ`, `Ṁ = G M`, `m = m0 − σ − kG − kΔ`:

```
dV/dt = v′(s)·S(Δ+G) + (v(s) − s v′(s))·GM = M[v′(s) s Δ + G v(s)].
```

`r M v(s) = max_σ [ m·sM + M(v′(s) sΔ + G v(s)) ]` ⇒ divide by `M` and subtract `G v(s)`:

```
(r−G) v(s) = max_σ [ (m0 − σ − kG) s + (v′(s) − k) s Δ ]
           = s · max_σ [ m0 − σ − kG + (v′(s) − k) ℓ(s) σ^α ] .                   (17) ✓
```

### 3.2 Verification argument (b) — CORRECT (standard)

`J_t = e^{−(r−G)t} v̂(s_t)` is absolutely continuous; using HJB `(r−G)v̂(s) ≥ s[m + v̂′(s)Δ]` and `ṡ = sΔ`:

```
J̇ = e^{−(r−G)t}[v̂′(s)ṡ − (r−G)v̂(s)] ≤ −e^{−(r−G)t} s m ,
```

so `∫₀^T e^{−(r−G)t} s_t m_t dt ≤ v̂(s0) − e^{−(r−G)T}v̂(s_T)`, last term → 0 (bounded `v̂`, `r>G`). Hence `v ≤ v̂`; equality when the feedback `σ̂(s) = [αℓ(s)(v̂′(s)−k)_+]^{1/(1−α)}` attains the max and generates an admissible path. No error found. The only non-trivial content is hypothesis (H), which the paper correctly labels **unproved**.

### 3.3 Small-share root (19) — CORRECT

Root equation `(r−G)v0 = m0 − kG + Cα λ (v0−k)_+^{1/(1−α)}`. Write `H(v) = (r−G)v − (m0−kG) − Π_λ(v)`. Identity (verified exactly):

```
H(v) = (r − g(v)) v − m(v),   g(v) = G + Δ*(λ,v),  m(v) = m0 − k g(v) − σ*(λ,v).
```

At the smallest simple root, `H′(v0) = (r−G) − Δ° > 0`, so `g° < r`, and `v0 = m°/(r−g°)` (Gordon identity). Numeric check (`r=.1, G=.05, m0=.3, k=0, λ=.06`): root `v0 = 10.0665`, `g°=.0789<r`, `m°/(r−g°) = 10.0665` — **match to 1e−6**. ✓

### 3.4 ODE singularity at `s=0` — CORRECT

Where spend is positive, (17) ⇔ `v̂′ = k + ℓ(s)^{-1}[( (r−G)v̂/s − (m0−kG) )/Cα]^{1−α}`. Writing `u = v̂/s`, `Φ(u,s) = k + ℓ(s)^{-1}[((r−G)u − (m0−kG))/Cα]^{1−α}`, one gets `s u′ = Φ(u,s) − u`. At the singular point `(0,v0)`:

```
∂Φ/∂u = (r−G)/Δ° > 1   (numeric: 1.7328 = 0.05/0.0289, exact).
```

Linearizing: `u − v0 ∝ s^{(r−G)/Δ° − 1}` (exponent `0.7328 > 0`), so **every** nearby solution has `v̂/s → v0` — the boundary condition does **not** pin down a unique solution. The paper's statement "the boundary behavior … does not pin one down" is **correct**. ✓

### 3.5 Part (e): "no root ⇒ v(s)/s → ∞" — CORRECT

Characterization (verified numerically): a positive root exists iff `m(v₁) < 0` where `g(v₁) = r`, i.e. iff `σ*(λ,v₁) > m0 − kr`, equivalently `λ < (r−G)/(m0−kr)^α`. In the no-root case (`m(v₁) > 0`), the constant policy `σ ≡ σ*(λ,v)` with `v↑v₁` yields `m(v) > 0`, `g(v) < r`, so the Gordon multiple `m(v)/(r−g(v)) → ∞`; the logistic lower-bound argument of part (d) then gives `liminf v(s)/s ≥ m(v)/(r−g(v))`, hence `v(s)/s → ∞`. Numeric: at `λ ∈ {0.3, 1.2, 3.0}` there is no root and the Gordon multiple near `v₁` is `≈ 2.4×10⁶, 2.3×10⁴, 1.1×10¹⁶` (diverging). ✓

*Minor precision note (not an error):* the paper's parenthetical "which uses only `g(υ) < r` and `m(υ) > 0`" slightly understates the argument — it also uses `k ≥ 0` to conclude `m_t ≥ m(v)` along the path (`m_t − m(v) = k(Δ(v) − Δ_t) ≥ 0`). Since `k ≥ 0` is Assumption 4, the argument is valid as stated in the model.

### 3.6 Honest admission of (H)

**Confirmed.** The paper states verbatim: "We have not proved (H). It is the hypothesis of a verification theorem, and we state it as an assumption." The singular-ODE discussion and the terminal singularity at `s = s̄` (`ℓ → 0`) are correctly characterized. Every "value-maximizing firm acts on weight `v′(s)`" statement is flagged conditional on (H).

**Verdict: CORRECT.** (a),(d),(e) unconditional; (b),(c) conditional on unproved (H); verification argument sound; ODE singularity analysis sound.

---

## 4. Proposition 4 (free entry) — CORRECT

Hand re-derivation reproduces every item (independent numeric run with `A=2, B=1, G=.05, r=.1, u=.4, ku=.5, ac=.6`, so `ĉ = .51`):

- **(a)** `P_n = (A + n ĉ)/(n+1)`, flow profit `π_n = (A−ĉ)²/[B(n+1)²]`, NPV `π_n/(r−G) − F`, Lerner `L_n = (A−ĉ)/(A + n ĉ)`. Operating margin `m_op = L_n + r k_n + (r−G) k_{a,n}`; FCF `m = (r−G)(k_n + k_{a,n}) + L_n`; score `XG + (r−G)(k_n+k_{a,n}) + L_n`. Numeric (n=1,2,3): Lerner `0.594, 0.493, 0.422`. ✓
- **(b)** `n* = ⌊N_F⌋ − 1`, `N_F = (A−ĉ)/√(BF̂)`. As `F→0`: `n*→∞`, `L→0`, `P→ĉ`, score `→ XG + (r−G)(ku+ac)/ĉ`; for `X=1` equals `G(1−k̂) + r k̂`. Numeric: `F=0.1 → n*=20; 0.02 → 46; 1e−3 → 209; 1e−5 → 2106`, limit score `0.1578` (= `G(1−k̂)+r k̂`). ✓
- **(c)** Scarce input: `w_n = A − ĉ − BZ(n+1)/n > 0` (needs `Z < (A−ĉ)/(2B)`), `P = A − BZ`, `ρ_n = w_n/P`, `L_n^{net} = BZ/(nP)`; entry `n* = ⌊Z√(B/F̂)⌋`; `F→0` gives `ρ → 1 − ĉ/(A−BZ)`. Owner vs buyer margins and limit scores (25) reproduce. ✓
- **(d)** Full-cost bound: `ρ ≤ 1 − cc − f − amin − cfull − r(k+ka)` and owner limit score `≤ 1 − cc − f − amin − cfull + XG − G(k+ka)`, matching Corollary 4 with `τ=0, δK=0`, capital `k+ka`. ✓

**Verdict: CORRECT** (special case of the Mankiw–Whinston integer free-entry model, as the paper states).

---

## 5. Proposition 5 (accountability floor) — CORRECT

- **Depth/diversity:** `P_o(D) = p_cc + (1−p_cc) ∏_j [p_cm_j + (1−p_cm_j) p_j^{n_j}]` — verified by direct probability: undetected ⇔ every layer fails; cross-type common cause defeats all; else types fail independently, each type's layers failing via common mode or independent failure. ✓
- **Admissibility equivalence:** `π_o ≤ π̄ ⟺ (1−P_o)^{N_o} ≥ 1−π̄ ⟺ P_o ≤ 1−(1−π̄)^{1/N_o} =: P̄_o`. Numeric check (N_o=100, π̄=.05 ⇒ P̄_o = .000513) confirms exact equivalence (the displayed `pi_o ≤ pibar` "False" at `P_o = P̄_o` is float rounding of `0.05` vs `0.0500…`; the algebra is exact). ✓
- **All-AI-single-provider inadmissibility:** `P_o(D) > p_cc + (1−p_cc) p_cm_j` for finite depth (limit from above), so if `p_cc + (1−p_cc) p_cm_j ≥ P̄_o` the design is inadmissible at any depth. Numeric: provider floor `0.2160` vs `P̄_o = 0.0005`; `P_o` at depths 1,2,10,1000 = `.2787, .2210, .2160, .2160`, all `> P̄_o`. ✓ (The claim's condition `≥` is even slightly conservative: inadmissibility actually needs only `floor > P̄_o` for finite depth; at exact equality the limit still never attains `P̄_o` because `p_j < 1, p_cm_j < 1`, so the "≥" statement is safe.) ✓

**Verdict: CORRECT.**

---

## 6. Propositions 6 & 7 (attainable / expected frontier) — CORRECT

- **P6(a) monotonicity, (b) convergence, (c) speed limit:** straightforward set-monotonicity of `Z_{n(t)}` and the per-wave capacity bound `Σ_{p∈Z} c_ip ≤ n(t)Γ_i`. Verified. ✓
- **P6(d) LP bound:** `R*_X(ϑ_Z) = R*_X(ϑ0) + Σ_{p∈Z} ΔR_p` when increments hit only `m0, G` (since `Π` depends only on `λh, X−k`); `V_i(C)` concave piecewise-linear knapsack. Numeric knapsack check: `ΔR=[.5,.4,.3,.2]`, `c=[1,.5,1,2]`, `V(C=3)=1.25`, greedy in decreasing `ΔR_p/c_ip`. ✓
- **P7(a)–(d):** coupling arguments for the monotonicities and the `E|Z_t^e| ≤ p_emb n_cap n(t_R)` bound are standard and correct.
- **P7(e) divisible program:** `E(t) ≤ min{1, p_emb c_w n(t_R)}` (each wave attempts `≤ c_w`, fraction `p_emb` embeds). Fluid check with `ν_D=0` (`p_emb=ϖ`), `c_w=.25, ϖ=.7`: `E(n) = 1−U_n` with `U_w = U_{w−1} − ϖ min{c_w, U_{w−1}}`; bound holds at every `n`, shortfall `< c_w` once `U_{w−1} < c_w`, and `E→1`. Greedy fills all waves when `c_w[1+ϖ(n−1)] ≤ 1`. ✓

**Verdict: CORRECT** (careful set-theoretic / stochastic-dominance arguments; no gaps found).

---

## 7. Counterexample stress-tests (task 7)

### (i) Proposition 1 with `g < G` (negative excess growth)

Under **Assumption 2** the model *never* allows `g < G` (zero spend delivers `G`; "no share is lost without spend"). So no counterexample exists **within** the model. The finiteness of the budget genuinely hinges on this. **Remark S1(b)** relaxes it to `g = G_i + ℓσ^α` with `G_i < G`, and then the bound becomes

```
∫(R_X − R∞)^+ ≤ (X−k)[ ln s(T)/s0 + (G − G_i) T ],
```

which grows **linearly in `T`** — the budget is no longer finite (a firm whose retention lags the market sheds share for free and buys it back repeatedly). Numeric: with `G_i=.02, G=.05`, the bound grows `3.94 → 4.21 → 6.91` as `T = 1→10→100`. **The paper states this correctly.** Classification of Proposition 1: **CONDITIONAL on `g ≥ G`** (explicit in the proposition's setup).

### (ii) Lemma 2 with `X < k` (corner)

`y = X−k ≤ 0 ⇒ S(Δ) = yΔ − κΔ^β ≤ 0 = S(0)` for all `Δ>0`, so the unique maximizer is `g*=G, σ*=0, R*_X = m0 + (X−k)G`. Numeric: `X=.2 (y=−.1)` and `X=.3 (y=0)` give argmax `Δ*=0`; `X=.31 (y=.01)` gives interior `Δ*=.031`. **Lemma 2(c) is correct; no gap.**

### (iii) Convexity of the feasible set

`F = {(g,m): m ≤ m*(g)}` is the hypograph of the **concave** function `m* = m0 − kg − κ(g−G)^β` (concave for every real `k`), hence convex. **Correct under the paper's timing convention** (capital installed one period *ahead*, eq. (2)). Lemma S1 (independently re-derived) shows the *contemporaneous* convention `I_t = k(S_t − S_{t−1})` gives `m̃″(g) = 2k/(1+g)³ − β(β−1)κ(g−G)^{β−2}`, which is **positive near `G`** for `α<1/2` (any `k>0`), destroying convexity. The paper is transparent about this. Classification: **CONDITIONAL on the installed-ahead convention** (explicitly stated).

### (iv) `k < 0` (deferred revenue): does the frontier stay "concave"?

Precise finding (the paper's Remark S1(c) is **correct**; the task's phrasing "the paper admits concavity doesn't survive" slightly misstates it):

- **Concavity survives.** `m*″(g) = −β(β−1)κ(g−G)^{β−2} < 0` for all `g>G`, **independent of `k`**. Numeric: all second derivatives negative for `k=−0.3`. ✓
- **Strict monotonicity fails.** `m*′(g) = −k − βκ(g−G)^{β−1}` is `> 0` for `g−G < Δ0 = [(−k)/(βκ)]^{1/(β−1)}` when `k<0`. Numeric: `k=−0.3` gives slope `+0.30` near `G`, `Δ0 = 0.132`. Hence Lemma 1(c) "strictly decreasing" **fails**, and Lemma 1(a) "efficient frontier is the graph of `m*`" / "dominated iff `m<m*(g)`" **fails** (the point `(G, m*(G))` is dominated by `(G+Δ0, m*(G+Δ0))`; numeric `m*(G)=.43 < m*(G+Δ0)=.458`).
- **Proposition 3(i) fails** for a single `k<0` firm (`Φ = m*` becomes increasing on `[G, G+Δ0]`).

The paper's Remark S1(c) states all of this correctly ("strict concavity is unaffected"; "every point with `g < G+Δ0` is dominated"; "Proposition 3(i) can fail"). It also correctly notes that for `X ≥ 0 > k` one always has `y = X−k > 0`, so Lemma 2(b)'s interior optimum applies and the maximizer lies on the *restricted* undominated frontier. **No error; correct caveat.**

---

## 8. Minor observations (not errors)

1. **Prop 2(e) parenthetical imprecision** (§3.5 above): the lower-bound argument also uses `k ≥ 0`. Harmless (Assumption 4).
2. **Root-existence characterization** for Prop 2: `(19)` has a positive root iff `σ*(λ,v₁) ≥ m0 − kr`, where `g(v₁) = r` (equivalently `H(v₁) = −m(v₁) ≥ 0`). Concretely, if `m0 − kr > 0` this is `λ ≤ (r−G)/(m0−kr)^α`, and if `m0 − kr ≤ 0` a root always exists; otherwise (generic for large `λ` or small `r−G`) there is no root and `v(s)/s → ∞`. The paper's (d) assumes existence (simple root) and (e) covers the complement — complete and correct, but the "revenue multiple = 10" worked example sits in the root-existence regime, which is thin when `λ` is large.
3. **Proposition 1 sharpness is a supremum, not a maximum** (approached by `Δ→0`, `s₁→s̄`, neither limit attained). The paper's "sharp" wording is accurate.

---

## 9. Reproducibility

Independent scripts (all in `/root/tmp/theory_audit/`, not in the repo):

| Script | What it checks | Result |
|--------|----------------|--------|
| `lemma2_symbolic.py` | sympy re-derivation of `m*`, `m*′`, `m*″`, FOC, (5)–(7), tangency, duality | ✓ matches Fig 1 |
| `prop1_numeric.py` | (11)–(12), Corollary 1 numbers, myopic-path integral bound, Prop S2 sharpness | ✓ 1.81/9.65/5.01/0.43/0.30 |
| `prop2_hjb.py` | root (19), Gordon identity, `∂Φ/∂u=(r−G)/Δ°`, no-root divergence | ✓ exact |
| `prop4_prop5_counter.py` | Cournot free entry, scarce input, full-cost bound; `P_o(D)`, admissibility, AI-floor | ✓ |
| `prop6_prop7.py` | `E(t) ≤ min{1, p_emb c_w n(t_R)}`, fluid greedy, knapsack concavity | ✓ |
| `prop4_prop5_counter.py` (§7) | `X≤k` corner, `k<0` concavity/monotonicity, `G_i<G` budget growth | ✓ |

**Overall: the paper's central theoretical propositions are correct. No counterexample satisfying all stated assumptions was found. The results that carry hidden conditions — `k ≥ 0` (Lemma 1 monotonicity/frontier-as-graph), `g ≥ G` (Proposition 1 finiteness), installed-ahead capital timing (convexity), and unproved hypothesis (H) (Proposition 2(b),(c)) — are each disclosed by the paper in the corresponding Remark/Lemma.**
