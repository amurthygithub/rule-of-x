# Referee report 1 (theory): "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation"

Scope of this report: the model (`sections/model.tex`), the appendices of results and proofs (`sections/appendix_proofs.tex`, `sections/appendix_proofs_acquired.tex`), the proof checks (`code/verify_theory.py`, and section E of `code/verify_part2_acquirer.py`), the parts of `sections/horizons.tex` and `code/calibrate_horizons.py` that apply the theory, and the match between the abstract, introduction and conclusion and what is proved. Empirical estimation is left to the other referees except where the model section quotes it.

All references are to section labels, result labels and equation labels. Every numerical claim below was re-derived by hand or recomputed; the scripts I used are short and their outputs are quoted in the evidence lines.

---

## 1. Summary of the contribution

The paper models a firm that buys revenue growth in excess of market growth with discretionary spend, $g=G+\lambda\sigma^{\alpha}h(s)$ with $h(s)=1-s/\bar s$, and pays for growth capital at $k$ per dollar of new revenue, so that the FCF margin is $m=m_0-\sigma-kg$ (Assumptions `ass:market` to `ass:capital`). From this it derives:

1. a concave efficient frontier $m^*(g)=m_0-kg-\kappa(g-G)^{\beta}$ (Prop. `prop:frontier`), on which the Rule of $X$, $R_X=Xg+m$, is a linear objective whose maximum is a tangency with closed form $R_X^*=m_0+(X-k)G+C_\alpha[\lambda h(X-k)]^{1/(1-\alpha)}$ (Prop. `prop:score`, eq. `eq:Rstar`);
2. saturation and demand-pull thresholds (Prop. `prop:saturation`), a log-share-headroom "score budget" that bounds the time integral of any excess over the saturated score (Prop. `prop:budget`, Cor. `cor:transient`, Prop. `prop:budget-sharp`), and envelope comparative statics (Prop. `prop:envelope`, Cors. `cor:capital`, `cor:priorities`);
3. a dynamic problem whose HJB equation makes the firm maximize a Rule-of-$X$ score at each date with weight equal to the marginal value of revenue $v'(s)$ (Prop. `prop:dynamic`), contrasted with an investor's "screening weight" derived from a two-stage DCF (Lemma `lem:valuation2`);
4. a cross-sectional envelope and non-identification result (Props. `prop:industry`, `prop:industry-full`), a Cournot free-entry result with a scarce input (Prop. `prop:entry`), price channels and AI comparative statics (Lemma `lem:prices`, Props. `prop:ai`, `prop:ai-shift`), and taxes (Remark `rem:taxes`);
5. an accounting of the recurring costs of running AI (Def. `def:fullcost`, Lemma `lem:fullcost`), an accountability floor with common-mode control failures (Prop. `prop:amin`) and a full-automation ceiling on the saturated score (Cor. `cor:ceiling`);
6. an "attainable frontier" for a transformation program run in waves under capacity limits and transition risk (Props. `prop:attainable`, `prop:expected`);
7. a restatement of the objective in economic-profit and ROIC coordinates (Prop. `prop:general`) and a treatment of acquired growth (Prop. `prop:acquired-score`).

The static algebra is correct throughout and carefully checked. The main contributions that are new to me in this setting are the score budget, the non-identification argument applied to growth-margin frontiers, the measurement of acquired growth, and the framing of the Rule of $X$ as a linear objective whose weight should be the marginal value of revenue. Much of the rest consists of closed forms of a one-dimensional concave problem, monotonicity statements about a packing problem, and accounting identities.

## 2. Recommendation: major revision

Reasons:

1. **The core static results are correct.** I re-derived every closed form in Sections `sec:model-frontier` to `sec:model-statics`, and `verify_theory.py` passes 168 of 168 checks (run time 7 min 36 s, not "about two minutes").
2. **Four results or statements are wrong as written** (Findings 1 to 4): the program-clock construction in Prop. `prop:expected`; the claim that partial realization of benefits lowers the level to which the firm converges; the reading of Cor. `cor:ceiling` as a ceiling on observed scores; and the statement that $\alpha<1/2$ is "exactly" the range in which capex timing matters. Each is fixable, and none changes the calibrated magnitudes much, but each is repeated in the introduction, discussion or conclusion.
3. **One headline claim rests on an unproved hypothesis** (Finding 5). The decision weight of Prop. `prop:dynamic` is a verification result: it assumes, and does not prove, that a bounded $C^1$ solution of the HJB exists.
4. **Several abstract and introduction claims go beyond what is proved** (Findings 6 to 10): two weights that are said to be "different objects"; a weight of 7 to 13 presented as a finding; Rule-of-$X$ lines called "iso-value lines"; an "economic-profit generalization"; and the "$1/\alpha$" ranking of automation levers.
5. **The theory leans on precedents it does not cite** (Finding 19), and its generality relative to the isoelastic functional form is not delineated (Finding 11). For a top field journal in theoretical IO and corporate finance, the theoretical contribution in its current form would not clear the novelty bar. It needs to be repositioned as an applied framework whose new elements are the budget, the non-identification result, the decision-weight argument (once Finding 5 is closed) and the measurement results.

## 3. Findings

Severity counts: error 4; gap 6; overclaim 6; unclear 3; minor 7 (26 findings).

---

### Finding 1 (error). The program clock $t_R=t/(1+\nu^{\rm R}T_{\rm frz})$ is not implied by random reorganizations, and Prop. `prop:expected`(a) and (c) fail under the paper's own description

**Location.** Def. `def:attainable`(b); Prop. `prop:expected`(a), (b) (freezes), (c); proof of Prop. `prop:expected`, observation (ii); intuition after Prop. `prop:expected`; `code/calibrate_horizons.py::pace`.

**Issue.** Definition `def:attainable`(b) says that reorganizations "arrive at rate $\nu^{\rm R}$ and freeze the program for $T_{\rm frz}$ each, which slows its clock by the factor $1+\nu^{\rm R}T_{\rm frz}$". With random arrivals, program time at calendar date $t$, $\tau(t)=t-(\text{time frozen by }t)$, is a random variable. The factor $1+\nu^{\rm R}T_{\rm frz}$ is its long-run mean slowdown (renewal-reward), not a pathwise identity. The proof asserts, in observation (ii), that "for every plan the law of $\vartheta_t$ is the law, in the model without freezes, of $\vartheta_{t_R}$". That is true only if freezes are a deterministic duty cycle. Under Poisson arrivals the upper bound $\bar R_X(t)\le R^{\rm att}_X(t_R)$ in (a) is false, and so is the equality case in (c).

A second inconsistency concerns the leadership and strategy hazards $\nu_D$. If they run in calendar time, as turnover data do, a transition in flight during a freeze is exposed for longer than $T_{\rm emb}$, so $p^{\rm emb}<\varpi e^{-\nu_DT_{\rm emb}}$. If they run in program time, no leader can change during a freeze. The paper uses calendar-time rates (leader turnover per year) together with the program-time formula.

**Evidence.**
- *Counterexample.* One wave holds the whole program; $T_{\rm emb}=T_{\rm par}=1$; $\varpi=1$; $\nu_D=0$; $\nu^{\rm R}=0.5$; $T_{\rm frz}=2$, so $\nu^{\rm R}T_{\rm frz}=1$. At $t=1.5$, $t_R=0.75<T_{\rm emb}$, so $R^{\rm att}_X(t_R)=R_X^*(\vartheta_0)$. But with probability $e^{-\nu^{\rm R}\cdot 1}=0.607$ no freeze starts during the first unit of program time, and the program then embeds at calendar time 1. Hence $\bar R_X(1.5)\ge R_0+0.607(R_1-R_0)>R^{\rm att}_X(t_R)$. Monte Carlo (200,000 paths): $P(\tau(1.5)\ge 1)=0.6072$.
- *Monotonicity.* Under random arrivals the law of $\tau(t)$ depends on $\nu^{\rm R}$ and $T_{\rm frz}$ separately (rare long freezes and frequent short ones with the same product give different laws). The monotonicity "in $\nu^{\rm R}T_{\rm frz}$" in (b) is therefore an artifact of the deterministic clock.
- *Size of the hazard inconsistency in the calibration* (central case: $\varpi=0.54$, $\nu_D=0.2316$, $T_{\rm emb}=2$, $\nu^{\rm R}T_{\rm frz}=0.115$). A flight of $2\times1.115=2.23$ calendar years gives $p^{\rm emb}=0.54e^{-0.2316\times2.23}=0.322$, against the 0.340 used: about 5% lower.

**Required change.** Either (i) state as an assumption that freezes occupy a deterministic fraction $\nu^{\rm R}T_{\rm frz}/(1+\nu^{\rm R}T_{\rm frz})$ of calendar time, and say in which clock $\nu_D$ runs; or (ii) define $\tau(t)$ as random and restate the results:
- (a): $\bar R_X(t)\le\mathbb E\,R^{\rm att}_X(\tau(t))$;
- (c): $\mathbb E|E_t|\le p^{\rm emb}n_{\rm cap}\,\mathbb E\,n(\tau(t))$;
- in both, $p^{\rm emb}_p=\varpi_p\,\mathbb E\exp\{-\nu_D\,(\text{calendar length of the flight})\}$ if $\nu_D$ runs in calendar time.

Then report the calibrated pace under the corrected $p^{\rm emb}$. The intuition sentence "risks act like a cut in capacity by the factor $p^{\rm emb}/(1+\nu^{\rm R}T_{\rm frz})$" should become "approximately, for programs with many waves", because the freeze dilates time (including the embedding lag $T_{\rm emb}$); it does not scale capacity.

---

### Finding 2 (error). "Partial realization of benefits lowers the level to which the firm converges" is false for the optimal plan under the paper's own definitions

**Location.** Def. `def:attainable`(b) (shares $b_p$ drawn per attempt; "the firm may revert any process at any time"); Prop. `prop:expected`(d); intuition after Prop. `prop:expected`; Introduction, paragraph 2 ("while partial realization of benefits lowers the level to which the firm converges"); Section `sec:discussion`.

**Issue.** The proof of (c) confirms that $b_\iota$ is "the share drawn on the success of attempt $\iota$". Each attempt therefore draws a fresh share, outcomes are revealed by the end of the wave, reversion is free, and in the long run capacity is not scarce. The optimal plan reverts low draws and retries, so $\lim_{t\to\infty}\bar R_X(t)=R_X^*(\vartheta_0+\sum_p b_p^{\max}\delta\vartheta_p)$, where $b_p^{\max}$ is the essential supremum of the share distribution. This equals $R^{\rm att}_X(\infty)$ when that supremum is 1.

Prop. `prop:expected`(d) is correctly stated for "the plan that retries reverted processes" (never reverting voluntarily). But the shortfall $(1-\bar b)N\Delta R$ belongs to that plan, not to $\bar R_X$, which is a supremum over plans. The finite-time bound in (c) does hold under selective reversion, as the paper notes.

**Evidence.** I simulated the `verify_theory.py` design ($N=30$, $n_{\rm cap}=4$, $\varpi=0.5$, $p_{\rm dis}=0.3$, $b\sim\mathrm{Beta}(4,1)$ with $\bar b=0.8$, 2,000 waves, 300 runs), reverting embedded processes with $b$ below a threshold:

| Reversion threshold | Mean $\sum b$ | Reference |
|---|---|---|
| none | 23.92 | $N\bar b=24$ |
| 0.5 | 24.82 | |
| 0.9 | 28.59 | |
| 0.97 | 29.55 | $N=30$ |

The long-run level is set by the supremum of $b$, not its mean. `verify_theory.py` check 22d tests only the non-selective plan.

**Required change.** Choose one of the following:
- (i) Make the share a fixed attribute of the process, drawn once at its first success (for instance, a property of the process revealed by migration). Then (d) holds for every plan and the claim stands.
- (ii) Keep per-attempt draws, add a cost of reverting and retrying (parallel-run premia, the dip), and restate (d) as a statement about $\lim_t\bar R_X(t)$.
- (iii) Delete the convergence-level claim from the intuition, the introduction and the discussion.

The calibration uses $\bar b=0.85$ in the central case, so the interpretation of $\bar b$ matters for the statement "lowers the level".

---

### Finding 3 (error). Cor. `cor:ceiling` bounds the saturated score of a firm at the full-automation cost structure, not observed scores; automation is not monotone in the score

**Location.** Cor. `cor:ceiling` and the intuition after it ("Observed scores above $R_{\max}$ must therefore reflect one of three things"); Section `sec:horizons-ceiling` ("even complete automation does not carry a mature firm past..."); Section `sec:discussion` ("push a reported score above the ceiling ... without any change in economics").

**Issue.** The bound $R_\infty\le R_{\max}$ uses $a\ge a_{\min}+c_{\rm full}+\delta_Kk$, with $c_c$ set at its full-automation scenario value (20% central). A firm that is not fully automated has a lower compute share and no $c_{\rm full}$, so $R_\infty\le R_{\max}$ holds only if
$$c_h+(a-a_{\min})+c_c^{\rm actual}\;\ge\;c_c^{\rm full}+c_{\rm full}+\delta_Kk,$$
that is, only if full automation would raise the score. Two consequences follow. A lean firm today can legitimately sit above $R_{\max}$ with no growth surplus, no rent and no generous margin concept. And the limit of the score over automation choices is $R^{\rm att}_X(\infty)=\max_{\mathcal Z\subseteq\mathcal P}R_X^*(\vartheta_{\mathcal Z})$ (Def. `def:attainable`(a)), which equals the full-program value only if every process is $X$-improving at the scenario parameters.

**Evidence.**
- A firm with gross margin 90% and $a=8\%$ at $\tau=0.18$ has a saturated after-tax margin term of $0.82\times0.82=0.672$, above the central base of $0.82\times(1-0.20-0.025-0.03-0.0409)=0.5774$ (which I reproduced).
- In the paper's own anchor (Section `sec:horizons-ranges`), monday.com's upper-bound intercept "exceeds even the central full-cost margin term". The paper attributes this to mismeasured growth spend. The corollary as written would forbid it.

**Required change.**
- Restate the corollary as an upper bound on $R_\infty$ at the full-automation cost structure, and define the automation limit as $\max_{\mathcal Z}R_X^*(\vartheta_{\mathcal Z})$.
- State when the two coincide: every process is $X$-improving under Def. `def:attainable`(c).
- Add a fourth explanation to the intuition: "a cost structure leaner than the scenario, in particular a compute share below $c_c$".
- In the abstract, keep "complete automation ... keeps ... below 100" (which is correct), but do not suggest that partial automation cannot do better.

---

### Finding 4 (error). "$\alpha<1/2$ is exactly the range in which the timing convention for growth capital matters" is false

**Location.** Section `sec:model-setup`, paragraph "Calibration of $\alpha$" (second feature); Lemma `lem:timing`(c).

**Issue.** Lemma `lem:timing`(c) gives a sufficient condition: if $\alpha<1/2$ and $k>0$, the contemporaneous frontier $\tilde m$ is convex near $G$. It is not necessary. Since $\tilde m''(g)=2k/(1+g)^3-\beta(\beta-1)\kappa(g-G)^{\beta-2}$, the first term dominates on an interval whenever $k$ is large relative to $\kappa$, for any $\alpha$.

**Evidence.** Numerical scan of $\tilde m''$:
- $\alpha=0.5$, $k=1$, $\ell=3$, $G=0.1$: $\tilde m$ is convex on $(0.100,1.08)$. At $X=0.45$, $Xg+\tilde m$ has a corner maximum at $G$ and an interior local maximum at $g\approx1.16$.
- $\alpha=0.6$, $k=2$, $\ell=5$: convex on $[0.10,3.1]$.
- $\alpha=0.7$, $k=1.5$, $\ell=6$: convex on $[0.10,3.1]$.

**Required change.** Replace the sentence with: "For $\alpha<1/2$ the contemporaneous convention makes the feasible set non-convex for every $k>0$; for $\alpha\ge1/2$ it does so when $k$ is large relative to $\kappa=(\lambda h)^{-1/\alpha}$." For asset-light firms the non-convex region is negligible: with $k=0.05$, $\alpha=0.3$ and $\ell=0.86$ it ends about 2 points of excess growth above $G$. Saying so would reassure readers.

---

### Finding 5 (gap). Prop. `prop:dynamic`(b) to (d) are verification results; the existence of a bounded $C^1$ solution of the HJB, on which the decision-weight claim rests, is not proved

**Location.** Prop. `prop:dynamic`(b), (c), and the last sentence of (d) ("If a function $\hat v$ as in (b) exists"); the abstract ("the weight a value-maximizing firm puts on growth is the marginal value of revenue"); the introduction; Section `sec:discussion`.

**Issue.** Part (c), "a firm that follows the optimal feedback therefore maximizes, at every date, the Rule-of-$X$ score ... with weight $X^{\rm dyn}(s)=v'(s)$", holds under the conditions of (b). Those conditions are: (1) a bounded $C^1$ solution exists; and (2) the feedback generates a share path. Neither is shown. The value function $v$ is not shown to be differentiable.

**Evidence.**
- Where spend is positive, the HJB is equivalent to the explicit ODE
$$v'(s)=k+\frac{1}{\ell(s)}\Bigl[\frac{(r-G)v(s)/s-(m_0-kG)}{C_\alpha}\Bigr]^{1-\alpha}.$$
- *At $s=0$.* With $u=v/s$ this becomes $s\,u'=\Phi(u,s)-u$, which has a singular point at $(0,v_0)$. There, $\partial\Phi/\partial u=(r-G)/\Delta^\circ>1$ by the simple-root condition of (d). So $u-v_0\approx Cs^{a}$ with $a=(r-G)/\Delta^\circ-1>0$ for every $C$. The boundary behaviour $v/s\to v_0$ is therefore automatic and does not pin down the solution.
- *At $s=\bar s$.* Uniqueness must come from this end, where $\ell\to0$ makes the problem singular again.
- `verify_theory.py` 15g to 15m solve a discretized dynamic program backward from $v(\bar s)=\bar s(m_0-kG)/(r-G)$. That supports existence numerically but does not prove it.

**Required change.** Either:
- prove existence and regularity: for example, show that the ODE has a solution through the terminal singular point with $(r-G)v/s>m_0-kG$ on $(0,\bar s)$ and bounded $v$; or show that the value function is $C^1$ (semiconvexity plus a strictly convex Hamiltonian in $p$ for $p>k$); or
- restate (c) using Pontryagin's maximum principle, which needs only an optimal control. Along an optimal path the control maximizes $R_{X(t)}$ with $X(t)$ the costate (shadow value of revenue), which coincides with $v'(s_t)$ where $v$ is differentiable.

In either case qualify the abstract and introduction until the result is unconditional.

---

### Finding 6 (overclaim). The screening weight and the decision weight are the same marginal rate of substitution evaluated for perturbations of different persistence, not "different objects"

**Location.** Section `sec:model-valuation` ("The two weights turn out to be different objects"; "They coincide approximately only when the current growth rate and margin both persist forever (part (d))"); Lemma `lem:valuation2`; Section `sec:discussion`, "Two weights on growth"; the abstract ("not the screening weights of two to three").

**Issue.** Lemma `lem:valuation2`(a) nests the decision weight. With $T=1$ and $\theta=0$ (growth raised for one period, margin cut for one period), eq. `eq:X2` gives exactly
$$X^{\rm scr}=\frac{m+\bar m\mathcal M_\infty}{1+g}=\frac{V}{S_0}\frac{1+r}{(1+g)^2},$$
which is the discrete-time counterpart of $X^{\rm dyn}=v'(s)$ in the non-saturating limit (Prop. `prop:dynamic`(d)). It is also the same expression as the persistent-forever limit of part (d). So "coincide approximately only when ... persist forever" is false.

Over $(T,\theta)$ the screening weight spans more than an order of magnitude. "Consistent with the weights of two to three" is therefore a choice of parameters ($T=10$, $\theta=1/2$), not a prediction.

The decision weight is "far larger" only when revenue multiples are high. With saturation $v'(s)<v(s)/s$ (worked example: 9.1/9.4, 7.2/8.1 and 5.4/6.5), so a firm trading near 3 times revenue has a decision weight near or below 3.

**Evidence.**
- At $r=0.10$, $g=0.25$, $G_\infty=0.03$, $\bar m=0.25$, $m=0.10$: eq. `eq:X2` with $T=1$, $\theta=0$ gives 3.0229; $(V/S_0)(1+r)/(1+g)^2=3.0229$; and a finite-difference one-period MRS of a direct DCF gives 3.0229.
- At $m=0.25$, $X^{\rm scr}$ is 0.20, 0.38 and 3.14 for $(T,\theta)=(1,1)$, $(1,\tfrac12)$ and $(1,0)$; it is 0.93, 1.53 and 4.39 for $T=5$. The paper's own examples, which I reproduced, are 1.78/2.79 at $\theta=\tfrac12$ and 5.42/6.20 at $\theta=0$.

**Required change.**
- Rewrite Section `sec:model-valuation`: the weight is the MRS between growth and margin in value; the investor's regression weight corresponds to persistent cross-sectional differences in growth and margin (large $T$, $\theta$ near 1); the firm's decision concerns a one-period trade ($T=1$, $\theta=0$).
- Delete "coincide approximately only when".
- Change the abstract to "the weight a value-maximizing firm puts on growth is the marginal value of revenue, which exceeds the screening weights of two to three when its revenue multiple does".

---

### Finding 7 (overclaim). The "weight on growth of 7 to 13" is $3.3/\alpha$ over an unsourced range of $\alpha$, and the grounding of that range is circular

**Location.** Abstract ("growth spending implies a weight on growth of 7 to 13", from the macros \WeightLo and \WeightHi); introduction (second finding); Section `sec:model-setup`, "Calibration of $\alpha$"; "Implication" after Prop. `prop:dynamic`; `notes/assumptions_register.md` (row "alpha (ALPHAS) [0.25, 0.45] ... c: Part I empirics (S&M ratio 3.3)").

**Issue.** The spend ratio identifies $\alpha(X-k)$ only, as the paper says itself (Section `sec:empirics`: a log-log slope is one whatever $\alpha$ is). The register grounds $\alpha\in[0.25,0.45]$ in the very ratio it is then used to invert. No external source for $\alpha$ is given. The 7 to 13 is a mapping of an assumption, not a finding. The paper's qualitative point, that the weight is far above 2 to 3, does not need $\alpha$ at all: since $\alpha<1$, $X-k=3.3/\alpha>3.3$ for every admissible $\alpha$.

**Evidence.**
- $X-k=3.3/\alpha$: 33 at $\alpha=0.1$; 13.2 at 0.25; 7.3 at 0.45; 5.5 at 0.6.
- `verify_theory.py` 15n only checks this arithmetic.
- The marketing-response literature measures the elasticity of the sales level with respect to advertising, not of excess growth with respect to the spend share (for example, the meta-analysis of Sethuraman, Tellis and Briesch, 2011, *Journal of Marketing Research* 48(3)). Any external grounding needs a mapping to the paper's $\alpha$.

**Required change.**
- Report the $\alpha$-free bound $X-k>\sigma/\Delta\approx3.3$ as the finding.
- Present 7 to 13 as conditional on $\alpha\in[0.25,0.45]$.
- Either source the range with an explicit mapping or label it a scenario value (class d), and remove "growth spending implies a weight of 7 to 13" from the abstract's list of findings.

---

### Finding 8 (overclaim). Rule-of-$X$ lines are iso-score lines; under the paper's own valuation they are not iso-value lines

**Location.** Introduction, paragraph 3 ("The Rule of 40 and the Rule of X are iso-value lines, not frontiers"); compare Prop. `prop:general`(c).

**Issue.** By Prop. `prop:general`(c), constant-growth iso-value lines in $(g,m)$ are $m=c(r-g)$: a fan through $(r,0)$ with slope $-c$ depending on the value level. A family of parallel lines of slope $-X$ contains exactly one iso-value line, the one with score $Xr$ (value $X$ times revenue).

**Evidence.** On the Rule-of-40 line $g+m=0.40$ with $r=0.10$, $V/S=(0.40-g)/(0.10-g)$ is 4.0 at $g=0$, 7.0 at $g=0.05$ and 16 at $g=0.08$.

**Required change.** Write "iso-score lines" or "linear objectives (price lines)". Note that the tangency with an iso-value line holds only at the small-share point of Prop. `prop:general`(c).

---

### Finding 9 (overclaim). The "generalization to economic profit" is an exact change of variables and reproduces the Marris–Gordon valuation ratio; it does not extend the model's domain

**Location.** Abstract ("In value terms the Rule of X is a rule of economic profit"); introduction ("so the frontier applies to any firm whose growth is bought with expensed spend at diminishing returns"); Section `sec:model-general`; Prop. `prop:general`; Section `sec:lit` (Higgins "generalize").

**Issue.**
- (b) is the identity $R_X=(X-k)g+e+rk$, since $rk$ is a constant.
- (c) is the constant-growth valuation $V/(kS)=(\mathrm{ROIC}-g)/(r-g)$, the steady-state valuation ratio of the Marris (1964) and Gordon (1962) models (dividends equal profit less retained investment), which the paper cites only for the tangency.
- The "so" in the introduction is a non sequitur. The model's domain is set by Assumptions `ass:market` to `ass:capital`, including the isoelastic technology. The reparametrization adds nothing to the domain.
- In (d), "for $k\ge1$ it penalizes growth whatever its return" is wrong at $k=1$, where the weight $1-k$ is zero (neutral).
- In (b), calling $q_K=X/k$ "the marginal value of a dollar of invested capital" is right only when $X=X^{\rm dyn}=\partial V/\partial S$. For the Rule of 40 ($X=1$) it is a label.

**Evidence.** The proof of Prop. `prop:general`(b) is two lines of algebra. The proof of (c) is the Gordon formula.

**Required change.**
- Present Prop. `prop:general` as a restatement and cite Marris's valuation ratio explicitly.
- Replace the introduction's sentence with a list of which results need only concave growth technology (Finding 11).
- Correct "$k\ge1$" to "$k>1$".
- Qualify $q_K$ as "when $X$ is the firm's own weight".

---

### Finding 10 (overclaim). The "$1/\alpha$" advantage of improving the growth engine in Cor. `cor:priorities`(ii) is an artifact of measuring productivity by $\lambda$; the stage ranking in (iii) does not hold at a fixed weight

**Location.** Cor. `cor:priorities`(ii), (iii) and the intuition after it; Section `sec:horizons` "Levers"; Section `sec:conclusion` ("For a fast grower the first target is the productivity of the growth engine and retention").

**Issue.**
- *Part (ii).* A proportional rise $x$ in $\lambda$ raises $R_X^*$ by $x\sigma^*/\alpha$ to first order. A proportional rise $x$ in the efficiency of spend, meaning the same growth for spend $\sigma/(1+x)$, maps to $\lambda\mapsto\lambda(1+x)^{\alpha}$ and raises $R_X^*$ by exactly $x\sigma^*$. That is the same as cutting a cost line of size $\sigma^*$ by $x$. "A percentage gain in the productivity of growth spend is worth $1/\alpha$ times the same percentage cut in an equally large cost line" therefore depends on the definition of productivity, which the corollary does not give.
- *Part (iii).* The retention gain $(X-k)dG$ does not depend on $g^*$ or $s$ at a fixed $X$. "Fast growers gain most from ... retention" requires $X=X^{\rm dyn}(s)$ decreasing in $s$, which is not part of the corollary.

**Evidence.** At $\alpha=0.3$, $\ell=0.8$, $y=1$: $\partial\Pi/\partial x=0.434=\sigma^*/\alpha$ for $\lambda\mapsto\lambda(1+x)$, and $0.130=\sigma^*$ for $\lambda\mapsto\lambda(1+x)^{\alpha}$. `verify_theory.py` 18b only checks that $1/0.45=2.22$ and $1/0.25=4$.

**Required change.**
- Define "productivity of growth spend" explicitly in (ii), state both versions, and drop the ranking unless it is restated in spend-efficiency terms.
- In (iii), make the stage claim conditional on the firm acting on $X^{\rm dyn}(s)$, and cite the numerical fall of $v'(s)$ with $s$.

---

### Finding 11 (gap). The paper does not separate results that hold for any concave growth technology from those specific to the isoelastic form

**Location.** Assumption `ass:growth`; Section `sec:model-general` ("Every result in this section is proved from Assumptions..."); Remark `rem:assumptions`.

**Issue.** Several results survive with a general increasing concave $\phi(\sigma)$ in $g=G+\ell\phi(\sigma)$:
- concavity of the frontier, tangency, duality, the score budget, non-identification and the free-entry results;
- the spend-ratio inversion, with $\alpha$ read as the local elasticity at the optimum: $(X-k)\ell\phi'(\sigma^*)=1$ gives $\sigma^*/\Delta^*=(X-k)\,\varepsilon(\sigma^*)$ with $\varepsilon=\sigma\phi'/\phi$.

The closed forms with $C_\alpha$, the threshold $\Lambda$ (eq. `eq:Lambda`), the $t^{-1/\alpha}$ decay (Prop. `prop:myopic`), the factor $1/\alpha$ (Finding 10) and the constancy of $\sigma/\Delta$ across firms are specific to $\phi=\sigma^{\alpha}$.

So is the slope $-k$ at $G$ (Prop. `prop:frontier`(b)). It is an Inada property ($\phi'(0)=\infty$), which forces every firm with $X>k$ to spend. A fixed cost of selling, or a finite $\phi'(0)$, would create a no-spend region and a kink. If $\varepsilon$ varies with $\sigma$, the range $[0.25,0.45]$ must be a range of local elasticities at observed spend, not a structural constant.

**Required change.** Add a remark (with short proofs) listing the general-$\phi$ versions. State which numerical claims (Rule of 1000 thresholds, horizon surpluses scaled by $\mu^{1/(1-\alpha)}$) depend on isoelasticity.

---

### Finding 12 (gap). The score budget needs zero-spend growth of at least $G$, which the text says it does not need, and the abstract's "finite budget" is conditional on it

**Location.** Text before Prop. `prop:budget` ("It needs neither the functional form ... nor optimal behavior, only the margin bound $m\le m_0-kg$ and share accounting"); Remark `rem:assumptions`(b), (d); proof of Prop. `prop:budget`(a) ("because $y\Delta\ge0$"); abstract; introduction.

**Issue.** The pointwise step $(R_X-R_\infty)^+\le y\Delta$ uses $\Delta\ge0$, which holds because zero-spend growth equals $G$. Remark `rem:assumptions`(b) shows that with zero-spend growth $G_i<G$ the right side becomes $(X-k)[\ln(s(T)/s_0)+(G-G_i)T]$, which grows without bound in $T$: a firm can lose share and buy it back repeatedly. This is exactly the case of Prop. `prop:acquired-score`(d) and (f) (NRR below one). The strict second inequality in eq. `eq:budget` also needs $s(T)<\bar s$, which the cap alone gives only weakly.

**Required change.** Add "and zero-spend growth of at least $G$ (no share loss without spend)" to the sentence before Prop. `prop:budget`, to Remark `rem:assumptions`(d), and to the abstract's "draws on a finite budget of share headroom".

---

### Finding 13 (gap). Hidden assumptions in the setup and the attainable frontier

**Location.** Assumptions `ass:growth`, `ass:costs`; Def. `def:attainable`; Assumption `ass:program`; Section `sec:horizons-ranges`; `code/calibrate_horizons.py::horizon`.

**Issue.**
- (a) *No harvesting.* $g\ge G$ always. A firm cannot trade growth below $G$ for margin, although cutting customer success, support and maintenance R&D (all in $a$) would do exactly that. Retention $G_i$ is treated as exogenous while the spend that sustains it sits in the "non-discretionary" cost $a$. Cor. `cor:priorities`(i) and (iii) then value cutting $a$ and raising $G_i$ as if independent.
- (b) *Fixed share in the attainable frontier.* $\mathcal F(\vartheta)$ is taken at a fixed share, so the frontier ignores the depletion of headroom while the program runs. The calibration absorbs headroom into the scenario multiplier $\mu$ but never checks the horizon rows against Prop. `prop:budget`.
- (c) *Additivity.* Process increments $\delta\vartheta_p$ are additive, with no complementarities.
- (d) *Independent disruptions.* Disruptions are independent across processes, although a leadership change is a firm-level event. This is harmless for expectations but not for the dip or variance.

**Evidence for (b).** At $\alpha=0.45$, the upper-end surpluses of `notes/calibration_results.json` ($\Pi=0.161$ in 2025, 0.568 in 2028, 0.337 in 2031, 0.242 in 2036) imply $\Delta=\Pi/(1-\alpha)=0.29$, 1.03, 0.61 and 0.44. Piecewise-linear integration over 2025 to 2036 gives $\int\Delta\,dt\approx7.1$: a 1,200-fold rise in share, which requires $s_0\le4\times10^{-4}$ at $\bar s=0.5$, if the rows are read as one firm's path.

**Required change.** State (a) to (d) as assumptions. For (b), either say explicitly that each horizon row is a cross-section of possibly different firms, or report the implied $\ln(s_T/s_0)$ and check it against the budget.

---

### Finding 14 (unclear). The growth-rate convention is innocuous at software growth rates but decisive at the extreme scores the paper discusses

**Location.** Section `sec:model-setup` ("The static results can equally be read in period rates"); Prop. `prop:saturation`(d) and its intuition (Rule of 1000: "grows about 1,314 points faster than its market"); Cor. `cor:transient` (period rates); Section `sec:horizons-ceiling` (multiples of demand pull).

**Issue.** The model declares instantaneous rates, while Cor. `cor:transient` uses period rates with the same parameters. Read as a continuously compounded rate, $\Delta^*=13.14$ multiplies revenue by $e^{13.34}\approx6\times10^5$ in a year and exhausts headroom from a 1% share in $\ln 50/13.14=0.30$ years. Read as a period rate, the example is internally consistent with the corollary's "at most one year".

The isoelastic form cannot hold in both conventions at once. If it holds in log rates, then in annual coordinates $g_a=e^{g}-1$ the frontier $m_0-\kappa(\ln(1+g_a)-G)^{\beta}$ has
$$\partial^2m/\partial g_a^2\propto(\ln(1+g_a)-G)-(\beta-1),$$
so it turns convex beyond excess log growth $\beta-1$. Then $Xg_a+m$ is unbounded in the absence of the share cap: the "maximal score" exists only in log rates.

**Required change.** State that the static technology is specified in whichever convention the score uses. Say which convention each extreme-score calculation uses ($\Lambda$, the "7 to 21 times" pull multiple, Cor. `cor:transient`), and note that for scores above roughly 200 the bound that binds is headroom, not the frontier.

---

### Finding 15 (gap). Taxes: replacement capital is deducted at once while growth capital is not, and Remark `rem:owncompute` uses $\psi=0$ against the paper's own statement of current law

**Location.** Remark `rem:taxes`; Cor. `cor:ceiling` ("replacement capital spending $\delta_Kk$ be part of $a$"); Remark `rem:owncompute` and its proof; Remark `rem:assumptions`(c) (depreciation $\delta$); Section `sec:horizons-ceiling` ("Owning the compute ... only if the vendor's markup exceeds" 20% at 5% and 60% at 15% market growth).

**Issue.**
- Because $a$ enters as $(1-\tau)a$, replacement capex is effectively expensed ($\psi=1$), while growth capex carries $(1-\psi\tau)$. With $\psi=0$ the two treatments of the same equipment differ.
- Remark `rem:taxes` says that equipment acquired after 19 January 2025 has $\psi=1$, yet Remark `rem:owncompute` sets $\psi=0$ for servers.
- Capital depreciation has two symbols, $\delta$ (Remark `rem:assumptions`(c), untaxed, in the intercept) and $\delta_K$ (Cor. `cor:ceiling`, in $a$).

**Evidence.** With $\psi=1$, owning minus buying changes the ceiling by $(1-\tau)[\upsilon_c-s_{\rm srv}L_{\rm srv}G]\mathrm{TCO}$. The threshold markups become $3.3G$, that is 16.5% at $G=5\%$ and 49.5% at $G=15\%$, against the 20.1% and 60.4% the paper reports.

**Required change.**
- Write replacement as $(1-\psi_{\rm rep}\tau)\delta_Kk$ outside $a$ (or justify full expensing).
- Make $\psi=1$ the baseline in Remark `rem:owncompute`, with $\psi=0$ as a sensitivity.
- Use one symbol for capital depreciation.

---

### Finding 16 (unclear). The model section quotes the observed-score slopes (E1) and hard-codes them, although the paper designates the organic frontier (E2) as the estimand that confronts the model

**Location.** Section `sec:model-industry`, first paragraph ("$-0.46$ (standard error 0.14) on the GAAP basis and $-0.37$ (0.11)"; "$\ell\approx0.86$ ($\alpha=0.25$) or $\ell\approx1.14$ ($\alpha=0.45$)"; "about 0.9 to 1.6"); introduction (first finding: E2 slopes of $-0.59$ and $-0.43$).

**Issue.** These are the E1 values (`\SlopeOp`=0.46, `\SlopeCash`=0.37). The E2 values are 0.59 (s.e. 0.16) and 0.43 (0.11).

**Evidence.** With the E2 GAAP slope, the fall over $\Delta\in[0,0.6]$ is 35 points. That implies $\ell=0.6/0.354^{\alpha}$, which is 0.78 at $\alpha=0.25$ and 0.96 at $\alpha=0.45$, and a steepest slope $\beta\cdot0.354/0.6$ of 1.3 to 2.4 (against 0.9 to 1.6 in the text).

**Required change.** Use the E2 macros in the model section, recompute $\ell$ and the steepest-slope range, and report E1 as the comparison.

---

### Finding 17 (unclear). "Embeds about 23% of its automation program by 2036" is the benefit-weighted share; the embedded share is 27%

**Location.** Abstract; introduction; Section `sec:horizons-ranges` ("Pace"); Section `sec:discussion`; Section `sec:conclusion`; the note to Table `tab:calib` ("$\mathcal E$ is the expected share of the automation program embedded"); `code/calibrate_horizons.py::pace` (`s=p['bbar']*min(1.0, raw)`).

**Issue.** The code multiplies the expected embedded share by $\bar b=0.85$ (central case). The 23% is therefore the expected share of the program's benefits realized. This is the right input for $m_0(t)$ by Prop. `prop:expected`(c), but it is not "embedded".

**Evidence.** Central case: 2036 value 0.2308, so the raw embedded share is $0.2308/0.85=0.2715$.

**Required change.** Write "realizes about 23% of the benefits of its program (embeds about 27%)", or define $\mathcal E_t$ as $\bar b$ times the embedded share everywhere.

---

### Finding 18 (gap). `verify_theory.py` does not test several claims that the text says it checks

**Location.** Section `sec:model` opening paragraph ("checks every closed form ... and checks the concavity, limit and inequality claims numerically"); `code/verify_theory.py` sections 11, 15, 18, 22.

**Issue.**
- (a) *Expected frontier.* Checks 22a to 22d simulate waves as Bernoulli trials, with no time, no overlap of flights ($T_{\rm emb}>T_{\rm par}$), no freezes and no disruption timing. The program clock, the bound in Prop. `prop:expected`(a), and the monotonicity in $T_{\rm emb}$ and in $\nu^{\rm R}T_{\rm frz}$ are untested (Finding 1).
- (b) *Long-run level.* 22d tests only the non-selective plan. The code's own `revert_low` option, run over many waves, contradicts the convergence-level claim (Finding 2).
- (c) *HJB.* 15g to 15m check a numerical dynamic-programming solution and cannot test the $C^1$ hypothesis (Finding 5).
- (d) *Arithmetic only.* Checks 2f, 7c, 11g, 15n and 18b verify arithmetic, not the claims they are labelled with.
- (e) *Stale content.* Checks 11c and 11e test "the previous Table tab:ceiling" with $a_{\min}=6\%$ (conservative accountability-only threshold 47.9%), whereas the text now uses 4.6% (`\GstarAccCons`=47, from 46.75%; check 20e).
- (f) *Not checked.* Remark `rem:r40`, Remark `rem:cap`, and the monotonicity of $D$ in $r$ in Lemma `lem:valuation2`(b).
- (g) *Header.* The docstring gives the paper's old title and a run time of "about two minutes"; it took 7 min 36 s.

**Evidence.** I ran the full script (168/168 PASS) and read sections 11, 15 and 22. My simulations are quoted under Findings 1 and 2.

**Required change.**
- Add a calendar-time simulation with Poisson freezes and disruptions.
- Add a selective-reversion long-run test.
- Relabel arithmetic checks as such.
- Delete the checks of superseded tables.
- Update the header.
- Soften "checks every ..." to what is actually checked.

---

### Finding 19 (overclaim). The theory relies on precedents it does not cite, so its novelty is overstated

**Location.** Section `sec:lit`, "Our contribution"; Section `sec:model-score`; Prop. `prop:dynamic`; Prop. `prop:amin`; Prop. `prop:entry`; Remark `rem:bertrand`.

**Issue.**
- *Dynamic problem.* The dynamic advertising problem with saturating response and its HJB and Pontryagin analysis are classical: Sethi (1973, *Operations Research* 21(4), optimal control of the Vidale–Wolfe model); Sethi (1977, *SIAM Review* 19(4)); Feichtinger, Hartl and Sethi (1994, *Management Science* 40(2)).
- *Customer acquisition.* Acquisition spend with diminishing returns and a marginal value of a customer is Gourio and Rudanko (2014, *Review of Economic Studies* 81(3), "Customer capital"). A convex cost of reaching the unserved share, the analog of $h(s)$, is Arkolakis (2010, *Journal of Political Economy* 118(6)).
- *Constant-growth valuation.* The valuation ratio in Prop. `prop:general`(c) is Marris's (Finding 9).
- *Control failures.* The failure model of Assumption `ass:layers` is the beta-factor common-cause model of reliability engineering (Fleming, 1974, General Atomic report GA-A13284; Mosleh et al., 1988, NUREG/CR-4780). The "depth versus diversity" result is the coincident-failure analysis of multiversion software: Eckhardt and Lee (1985, *IEEE TSE* 11(12)); Littlewood and Miller (1989, *IEEE TSE* 15(12)); Knight and Leveson (1986, *IEEE TSE* 12(1)).
- *Market structure.* Free entry with sunk costs should cite Mankiw and Whinston (1986, *RAND Journal of Economics* 17(1)). Contestability in Remark `rem:bertrand` should cite Baumol, Panzar and Willig (1982).
- *Elementary results.* Props. `prop:frontier`, `prop:score`, `prop:envelope`, `prop:saturation`, `prop:attainable` and Cor. `cor:ceiling` are elementary consequences of the assumptions. Presenting them as propositions on a par with the budget and the non-identification result overstates the theoretical contribution.

**Required change.**
- Add these references.
- State precisely what is new relative to Marris, Solow and Odagiri (the score budget; non-identification of firm frontiers from chosen points; the decision-weight argument once Finding 5 is closed; the measurement of acquired growth).
- Demote the elementary results to lemmas.

---

### Finding 20 (minor). Prop. `prop:acquired-score`(d): $G_i=\ln\mathrm{NRR}$ is inconsistent with the stated annual contribution, and NRR is not zero-spend growth

**Location.** Prop. `prop:acquired-score`(d) and its proof in `app:proofs-acquired`.

**Issue.** The proof gives the base's annual contribution as $(S_{\rm sub}/S)(\mathrm{NRR}-1)$. The continuous-time zero-spend growth is then $\ln[1+(S_{\rm sub}/S)(\mathrm{NRR}-1)]$, which equals $\ln\mathrm{NRR}$ only if $S_{\rm sub}=S$. NRR is also achieved at the firm's actual customer-success and expansion spend, most of which is in selling and marketing, so it is not zero-spend growth (Finding 13(a)).

**Required change.** Correct the formula and add the caveat.

---

### Finding 21 (minor). Undefined symbol in Lemma `lem:prices`(a)

**Location.** Lemma `lem:prices`(a) ("with equality if and only if $b=0$") and its proof ("that is, $b=0$").

**Issue.** $b$ is the code's name for $k_u$. In the paper, $b$ denotes the benefit share.

**Required change.** Replace with "$k_u=0$".

---

### Finding 22 (minor). Draft residue in proofs and code

**Location.** Proof of Cor. `cor:ceiling` ("the margin terms are those of the earlier form of the corollary, 0.6928, 0.6109, 0.5214 and 0.4469, which require $G\approx0.307$, 0.389, 0.479 and 0.553"); `verify_theory.py` 11c and 11e and the comment "a_min recalibrated (Referee 2)".

**Issue.** These lines refer to a superseded version with conservative $a_{\min}=6\%$. They are inconsistent with the text's 4.6% (conservative accountability-only threshold 46.75%, macro 47).

**Required change.** Delete them or update them to the current parameters.

---

### Finding 23 (minor). Notation clashes

**Location.** Throughout Section `sec:model` and Appendices `app:theory` and `app:proofs`.

**Issue.**
- $g$: growth rate, and index of AI applications ($C^{\rm itgc}_g$, $\sum_g$) in Prop. `prop:amin`.
- $y$: $X-k$, and the "loss rate $y$" in Lemma `lem:fullcost`(e). $Y$: Pareto multiple, $Y_t$ in the proof of Prop. `prop:dynamic`(b), $Y_{\rm fb}$.
- $\nu$: hazard rates ($\nu_D$, $\nu^{\rm L}$, $\nu^{\rm R}$, $\nu_{\rm cm}$), and the growth surprise $\nu_t$ in Prop. `prop:industry-full`(v).
- $\mu$: intercept constant in Prop. `prop:industry-full`(iv), and demand pull relative to 2025 (Table `tab:notation`). $\xi$: slope in (iv), and the exposure multiplier $\xi_{\rm exp}$.
- $p$: price, $p_j$, $p^{\rm cm}_j$, $p_{\rm keep}$, $p^{\rm emb}$, $p_Y$, $p=1/(1-\alpha)$ in the proof of Prop. `prop:myopic`, and the process index $p$ (so $p^{\rm emb}_p$).
- $H$: $H_{\rm cm}$, a distribution function, and $h^{1-p}$, all in the appendix.
- $\bar m$: mature margin (Lemma `lem:valuation2`), and $\bar m_t(g)$, the expected frontier (Def. `def:attainable`). $\bar m_0$: mean intercept in Prop. `prop:industry-full`(v).
- $E$: $E_t$ (set embedded), $\mathcal E_t$, E1/E2 and $\mathbb E$.
- $s$: share, and the start date of an attempt in the proof of Prop. `prop:expected`(b).
- $\theta$ (persistence) and $\vartheta$ (parameter vector) are easily confused. $\delta$ versus $\delta_K$ (Finding 15).
- $a_{\min}$ is defined as a minimum over designs but is used for a restricted design class in Prop. `prop:amin`(b).

**Required change.** Rename the clashing symbols, for example: $j\to\iota$ for applications; $\epsilon_t$ for growth surprises; $\mu_\lambda$ for the pull multiple; $a_{\min}^{\rm AI}$ for the restricted design class.

---

### Finding 24 (minor). Small overstatements in the attainable-frontier results

**Location.** Intuition after Prop. `prop:expected` ("moves out ... at a decreasing rate, because the best processes go first"); Remark `rem:regimes`(iii) ("shrink $\mathcal A_t$ and lower $\bar R_X(t)$"); Prop. `prop:attainable`(d).

**Issue.** Only the upper bound $\mathcal V_i(n(t)\Gamma_i)$ is shown to be concave. Concavity of $R^{\rm att}_X$ in $n(t)$ is not proved: the packing is integer and over several resources. "Lower" should read "weakly lower".

**Required change.** Qualify both statements.

---

### Finding 25 (minor). The score budget is sharp only for slow growth; a sharper bound exists for the extreme scores it is used for

**Location.** Prop. `prop:budget-sharp`; intuition after Prop. `prop:budget` ("A firm can spend the budget quickly, on a high but brief score, or slowly"); Cor. `cor:transient`; model text before Fig. `fig:saturation` ("if the firm spends optimally at each date").

**Issue.** The supremum is approached only as $\Delta\to0$ over unbounded horizons. Any path satisfies $R-R_\infty\le y\Delta-(\Delta/\lambda)^{\beta}$, so fast spending converts at most $y-\sigma/\Delta$ of each unit of headroom. In continuous time, Prop. `prop:budget`(a) gives directly $\mathcal T(\bar R)\le y\ln(\bar s/s_0)/(\bar R-R_\infty)$.

**Evidence.** In the Rule-of-1000 example this is $3.912/9.2=0.43$ years, and at the static optimum $(1-\alpha)\times3.912/9.2=0.30$ years. Prop. `prop:myopic` is about a fixed-weight (static) policy, not the dynamically optimal one, so "optimally at each date" should read "myopically, at a fixed weight".

**Required change.** Add the continuous-time corollary, note the asymmetry, and fix the wording about Prop. `prop:myopic`.

---

### Finding 26 (minor). Abstract and introduction wording

**Location.** Abstract; introduction, paragraph 3.

**Issue.**
- "The intercept plus market growth plus a growth surplus" omits the capital charge: it is $(1-k)G$ on the Rule of 40, net of taxes.
- "Its efficient frontier is concave" holds under the forward capex convention (Lemma `lem:timing`). Reported scores use the contemporaneous convention, under which concavity can fail (Finding 4).

**Required change.** "Plus market growth net of the capital it requires", and "concave when capacity is installed ahead of the revenue it serves".

---

## 4. What I checked and found correct

Re-derived by hand (all correct unless a finding above says otherwise):

- **Frontier and score.** Prop. `prop:frontier`(a) to (d), including the three curvature cases at $g\downarrow G$. Prop. `prop:score`(a) to (e): eqs. `eq:Dstar`, `eq:sigstar`, `eq:Rstar`, the margin at the optimum, the duality in (d) and the surplus characterization in (e). Remarks `rem:cap` and `rem:r40`.
- **Saturation.** Prop. `prop:saturation`(a) to (d), including $dR_X^*/ds=-(X-k)\Delta^*/(\bar s-s)$, eq. `eq:Lambda`, and the Rule-of-1000 numbers ($C_{0.3}=0.418$, $\Lambda\approx8.71$, $\Delta^*\approx13.14$, $\sigma^*\approx3.94$, $m\approx-3.34$).
- **Budget and transience.** Prop. `prop:budget`(a) (logistic solution, $\int\Delta\,dt=\ln(s_T/s_0)$) and (b). Prop. `prop:budget-sharp`. Cor. `cor:transient` and its bounds 1.81, 9.65 and 5.01. Prop. `prop:myopic` (the ODE for $h$, the comparison for $h^{1-p}$, the exponent $-1/\alpha$).
- **Comparative statics.** Prop. `prop:envelope`: all derivatives, $C^1$ at $X=k$, convexity in $k$ and $\lambda$, the cross-partial. Cor. `cor:capital`: the bracket is exact by convexity; 5 and 1 points; 7.5 and 3.5 points with $\delta=0.25$. Cor. `cor:priorities`(i), (iv), (v) and the algebra of (ii) and (iii).
- **Dynamics.** Prop. `prop:dynamic`(a); the verification half of (b) (inequality `eq:verif`, transversality from boundedness and $r>G$); the identity in (c); and in (d), the smallest-root argument giving $g^\circ<r$ from simplicity, the supersolution $v_0s$, the constant-policy lower bound with monotone convergence, and the limit $\hat v'\to v_0$. The worked example: $\lambda\approx0.070$ gives $v_0=10$, $g=7.6\%$, $\sigma=10.7\%$, $m=24.3\%$; $\lambda\approx0.081$ gives $v_0=15$, $g=9.2\%$, $\sigma=23.6\%$, $m=11.4\%$; and $f'(v_0)>0$ in both.
- **Screening weight.** Lemma `lem:valuation2`(a) to (d) and the examples: $D=10.25$ at $T=15$ and 6.53 at $T=10$; $X^{\rm scr}=1.78$ and 2.79 at $\theta=\tfrac12$; 5.42 and 6.20 at $\theta=0$.
- **Heterogeneous firms.** Prop. `prop:industry`(i) to (v) and Prop. `prop:industry-full`(iv), (v): the locus eq. `eq:locus`, the quality condition, the flat $\Psi$, strictly increasing quantile frontiers, the two equalities in (iii), the inverse construction in (iv), and the Taylor argument for $\mathcal W$. The two-type example (chosen points $(0.21,0.27)$ and $(0.53,0.37)$, slope $+0.31$), $\ell\approx0.86$ and 1.14 for a 24-point fall, and the 83% example. Remark `rem:segments`.
- **Competition and AI.** Prop. `prop:entry`(a) to (c): Cournot quantities, price, profit, Lerner index, the free-entry count and bound, the binding scarce input and the limits; the 7.5-point example. Remark `rem:bertrand`. Lemma `lem:prices`(a), (b), apart from the symbol in Finding 21. Props. `prop:ai` and `prop:ai-shift` (both cases of the domination argument).
- **Taxes and full-cost floors.** Remark `rem:taxes`: the substitution, $(\tilde\lambda h)^{-\beta}=(1-\tau)\kappa$, the 5 to 7% pull adjustment, $\psi_5=0.796$ and $\psi_{15}=0.532$. Lemma `lem:fullcost`(a) to (e), the security rows of Table `tab:fullcost` (0.86, 1.27, 2.14; controls removing 98, 86 and 63% of loss) and the Gordon–Loeb $1/e$ benchmark.
- **Accountability floor and ceiling.** Prop. `prop:amin`(a) to (c) and Remark `rem:amin-values`: \$2.01m, \$1.70m (of which \$1.20m common mode) and \$1.02m; the optimal depths (three human layers, three AI layers, one human over two AI); the 48-opportunity and 1% common-mode cases (\$1.084m and \$1.079m); all-AI above all-human in both. The algebra of Cor. `cor:ceiling` (central base 0.5774, $G^*=42.3\%$).
- **Attainable and expected frontiers.** Prop. `prop:attainable`(a) to (d): $n(t)$, nesting of $\mathcal Z_n$, convergence date, speed limit, fractional-knapsack bound. Prop. `prop:expected`(b) couplings for $\varpi_p$, $\nu_D$, $T_{\rm emb}$ and realized shares, given the deterministic clock. The finite-time bound in (c), including under selective reversion. Lemma `lem:expected-frontier`. Remark `rem:regimes`(i) and (ii).
- **Economic profit.** Prop. `prop:general`(a) to (d) and its example ($-7.5$ points; $-0.5$ per point of growth).
- **Owning compute.** The arithmetic of Remark `rem:owncompute` given $\psi=0$ (20.1% and 60.4%).
- **Capex timing.** Lemma `lem:timing`(a) to (c) and its example (corner 0.486; interior maximum 0.595 at $g\approx0.739$).
- **Acquired growth.** Prop. `prop:acquired-score`(a) to (f) and Remark `rem:acquired-bounds` (CRF inequalities).
- **Discussion arithmetic.** At a spend ratio of 3.3, an asset-light firm 10 points above its market scores 23 points below its no-spend score.

Code:
- `code/verify_theory.py`: 168/168 checks pass (7 min 36 s).
- `code/verify_part2_acquirer.py`: 72/72 checks pass, including section E (E1 to E11, Paper 1's acquired-growth results).
- `notes/calibration_results.json` reproduces the ceiling, $\Lambda$, the pull multiples (7 to 21) and the pace parameters quoted in Section `sec:horizons` ($p^{\rm emb}=0.34$ and 0.74; 3.0% and 14.5% a year; completion in 2033 under fast execution).
