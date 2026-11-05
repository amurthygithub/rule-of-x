# Independent mathematical re-review notes

Reviewed November 4, 2026 (America/Los_Angeles). Sources: supplied main PDF (87 pages), supplied supplement (72 pages), and RESPONSE.md. The PDFs are the authority. No restricted reviewer folders, joint response, or other response letters were read. No repository, author verification script, or Lean build was available to this reviewer. These notes do not certify the formalization or the committed numeric multipliers.

## Assessment of the mathematical revisions

The central static power-model results survive direct checking. The frontier, tangency optimum, growth-spend identity, score decomposition, convexity in capital intensity, capital-for-labor bracket and instantaneous-vs-annual acquisition identity are consistent with their stated assumptions. I re-evaluated the static first-order condition, tangency and score decomposition on 1,000 independent parameter draws (seed 20261104); the maximum relative discrepancy was 5.13e-15. This is arithmetic evidence, not a substitute for a proof or for the author's reproduction suite.

The population dominance-cone repair is correct when the growth distribution is continuous: for a strictly decreasing common frontier, its chi margin quantile among g>=t is m*(F^{-1}(1-chi+chi F(t))). Differentiation gives the density-ratio factor printed in S2.3 (supplement p7). Dense sampling alone does not remove it. A deterministic uniform-distribution check independently recovers the displayed chain rule. The empirical 2.1–4.0 multipliers cannot be reproduced without the E1 growth values and the exact estimator implementation. The main-text numerical interpretation needs the same assumptions as the supplement, as discussed below.

The HJB correction in S3 (supplement p16) has the right forcing coefficient. Writing z=s/sbar, u=vhat/s, w=u-v0 and a=(r-G)/Delta0-1 gives z w'=a w+(v0-k)z+higher-order terms. Thus the particular linear contribution is (v0-k)z/(1-a), and at a=1 the resonant term is +(v0-k)z log z. The free homogeneous coefficient remains and the small-share limit alone does not select a global solution. Proposition 2 now states (H) explicitly and does not claim its existence has been proved. The written verification argument on supplement pp15–16 is coherent: boundedness supplies transversality, the measurable-control comparison produces an upper bound, and feedback admissibility supplies equality. The positive simple-root argument, its Gordon identity and the no-root blow-up argument are also coherent under the stated sign assumptions. A proof of (H) would strengthen the paper but is not a missing proof of a theorem that currently claims (H) unconditionally.

The tax correction is substantive and correctly labeled. Main Remark 2, p29, and the Table 4 note, p60, distinguish a purchase-date PV equivalent from period cash and explain a steady-growth tax-deduction ratio. My independent evaluations are psi5(.10)=.796065, psi15(.10)=.532426 and psi15(.30)=.250563. They reproduce the rounded numbers printed. The distinction remains important for any capital-owning scenario or payback calculation; a PV charge must not be silently reused as an annual cash flow.

Definition 5 (main p51) now correctly distinguishes acquired run-rate growth normalized by current revenue from annual recognized acquired revenue normalized by prior revenue. Its annual identity C_t/S_t=k_acq*g_acq_t/(1+g_t) is correct when the acquisition multiple is defined per dollar of revenue recognized in that year, as the text now says. Such a multiple is not automatically the quoted transaction multiple per acquired revenue run-rate; the definition's conditional wording is essential.

The Lean claims are scoped sensibly in S4 (supplement pp26–27): static Sections 3.1–3.5, except Corollary 3(iv), with numerical examples excluded, and no claim to formalize the dynamic, competition, control or execution results. The discussion of Caratheodory paths versus everywhere-differentiable paths and the difference between kernel correctness and correspondence to prose is appropriate. Its 35-theorem/no-sorry/standard-axiom claims remain unverified without the formal/ files and an actual build. They should be recorded as author-reported, not as verified in this re-review.

## New findings

### T1 — Minor: abstract decomposition can count growth capital twice

Locator: main p1 abstract, compared with Assumption 3 p14, Lemma 2(b) p16, and the saturated-score definition on p17.

The abstract says the best score is 'the margin it earns growing with its market, plus that market's growth net of the capital growth needs'. The setup expressly distinguishes the margin at market growth, m0-kG, from the operating intercept m0 (p14). On that reading the sentence gives (m0-kG)+(1-k)G+Pi, while the correct Rule-of-40 decomposition is m0+(1-k)G+Pi, or equivalently (m0-kG)+G+Pi. This is an ambiguity in the plain-language summary, not a counterexample to Lemma 2.

Fix: say 'its margin before growth investment, plus market growth net of the capital it requires, plus a temporary gain from taking share'; alternatively start with the cash margin at market growth and add market growth without a second capital deduction.

### T2 — Minor, but important to the abstract: free entry need not eliminate an improvement in the accounting score

Locator: main p1 final abstract sentence, compared with Proposition 4(b) p26, Remark S6 supplement p5, and Corollary 3(iv) main p21.

The abstract says free entry means automation lifts only companies with an input others cannot copy. The exact competitive-limit score in Proposition 4(b) is XG+(r-G)(ku+ac)/c_hat, where c_hat=u+r(ku+ac). Even with zero Lerner rent and no scarce input, a fall in u can raise the capital-per-revenue normal-return component. A valid counterexample within its assumptions is X=1, G=.10, r=.15, ku=1, ac=0: u=.85 gives c_hat=1 and score .15; u=.35 gives c_hat=.5 and score .20. The score rises with no uncopyable input. The main Corollary already recognizes this effect. Moreover, Remark S6 distinguishes Cournot, homogeneous Bertrand, contestability and differentiated monopolistic competition; 'with free entry' by itself does not identify the limiting competition model.

Fix: distinguish durable economic rents from the accounting score, and state the homogeneous-product/vanishing-replication-cost conditions. A suitable plain-language sentence is: 'With close substitutes and vanishing replication costs, competition removes the operating rent; a persistent rent requires a scarce input, while the cash score can still include normal returns on capital.'

### T3 — Minor: common-frontier weight bound needs interior and support qualifications

Locator: main Section 3.7 p24; supplement S2.3 p7 and Table S5 note p33; compare Lemma 2(b),(d), main pp16–17, and Remark S2, supplement p3.

The corrected cone identity is right. However, the claim that common-frontier firms must act on weights 'none above' the steepest frontier slope in the estimation window needs qualifications. A firm at a binding common financing cap can maximize any weight above the endpoint tangent weight. For example alpha=.3, ell=1, k=G=0, cap sigma=1 and X=10 gives uncapped sigma=4.804, so the capped optimum is g=1 even though the common frontier's largest slope magnitude is only beta=3.333. An additional lower-weight interior firm gives different chosen points on exactly the same frontier. Also the cone at thresholds up to 60% includes firm-years above 60% (Table S5 note), so a bound within the threshold window is not automatically a bound on the weights of all firms entering the cone. Finally S2.3's numerical calculation explicitly assumes k=0 and reads the window as excess growth; those qualifiers are not repeated in the main numerical inference.

Fix: restrict the statement to slack-cap firms whose chosen growth lies in the specified frontier window, carry k=0 and the growth-origin convention into the main statement, and avoid asserting that a window-specific slope bounds every firm in the cone. This does not invalidate the broad non-identification result of Proposition 3(iv).

### T4 — Minor: the general-concave-growth remark needs a finite optimum assumption

Locator: supplement Remark S4(a), p3.

The remark generalizes to every continuous strictly increasing concave phi on [0,infinity), phi(0)=0, then states that Lemma 4's envelope derivatives are unchanged. Under unbounded financing the optimized score need not be finite for that class: phi(sigma)=sigma, ell=1, X=2, k=G=m0=0 gives R=sigma and R*=infinity. Even strict concavity alone would not repair this: phi(sigma)=sigma+log(1+sigma) is strictly concave but has the same unbounded-score problem at these inputs. A derivative of finite maximal value is unavailable. The power technology itself has sublinear growth and is unaffected.

Fix: condition the envelope assertions on a finite attained optimum and the regularity needed for differentiation; a finite cap or a sublinear-at-infinity technology provides an appropriate existence condition. Distinguish unconstrained from binding-cap formulas.

## Relevant Part A row verdicts

| ID | Proposed verdict | Evidence |
|---|---|---|
| GPT-M1 | partly resolved | Exact population mapping fixed in main p24/S2.3 p7. Empirical multiplier not rerun; support/cap/k qualifications remain (T3). |
| GPT-M2 | resolved for the manuscript mathematics | Remark 2 main p29 and Table 4 note p60 clearly label PV-equivalent and period-cash values; independent shield arithmetic agrees. No repository verification. |
| GPT-M3 | resolved for the stated identities | Definition 5 main p51 distinguishes instantaneous and annual measures and prints denominator 1+g_t with the required annual-revenue multiple definition. |
| GPT-1 | resolved | Supplement S3 p16 contains the missing forcing term with correct sign/coefficient and notes resonance. |
| GPT-2 | resolved as a manuscript correction; numeric path unverified | Main p23 and supplement S2.2 p6 now describe minimum near 80% of cap and subsequent rise. Grid solver results not rerun. |
| GPT-3 | resolved / accept already handled | Corollary 2 p20 and the introductory qualification of Corollary 3 pp20–21 say 'to first order'; exact finite-change bracket is separately stated. |
| GPT-5 | resolved as scope correction | Main p18 says the budget is for excess above R_infinity; main Section 7.2 qualifies the Rule-of-1000 claim by historically sustained market growth. The mathematical budget itself does not exclude an arbitrarily large G. |
| GPT-6 | resolved as a conditional mathematical statement | Proposition 5(b), main p31, now requires objectives to include combinations and says narrower coverage is necessary only. Legal sufficiency remains the root legal review's scope. |
| GPT-7 | resolved / accept already-handled mathematical distinction | Proposition 5 thresholds are explicitly per objective. Supplement Remark S10 p55 explicitly converts a firm-wide 5% over ten independent objectives to .51% per objective. |
| GPT-8 | resolved as a conditional manuscript sensitivity | Assumption 7 main p30 expressly assumes independent draws across opportunities; supplement S2.6 p8 contrasts persistence. Independent calculation gives 11.3517% under independent common modes versus .5191% under a period-persistent mode with the stated parameters. No author-code certification. |
| GPT-25 | resolved / accept already-handled transport limitation | Supplement S2.6 p8 explicitly distinguishes observed joint wrong-output agreement from conditional escape probabilities. |
| GPT-28 | resolved as mathematical addition | Main p29 adds elective amortization and retains psi<1; statutory interpretation belongs to root legal audit. |
| GPT-32 | resolved / accept already handled | Proposition 2 p22 and supplement proof p16 expressly do not prove (H). The theorem is a verification theorem conditional on that hypothesis. |
| GPT-35 | resolved as direct-paper confirmations, with scope limit | Direct checking found no core power-model theorem counterexample. This does not certify Lean, implementation, or every numeric table. |

## Reproducible evidence

Own script: scripts/theory_independent_checks.py. Output: results/theory_independent_checks.json. Seed 20261104; 1,000 random checks. Standard-library Python only. Checks include static first-order identities, a synthetic continuous-distribution cone derivative, the cap counterexample, competitive-limit normal-return counterexample, corrected annual acquisition normalization, the tax-shield numbers and temporal common-mode sensitivity. No external article text is copied into these notes. No author's code or theorem-proving environment was run.

## Recommendation within this scope

The paper's central static framework is mathematically coherent and the response made meaningful corrections. The new issues above mainly concern transporting exact propositions into summaries or broader generalizations. They should be fixed before an arXiv release because they affect exactly the conditions the plain-language abstract is intended to preserve. Specialist-journal assessment additionally requires executable replication, an independent Lean-to-prose audit/build, and careful separation of conditional scenario interpretation from empirical identification; none can be inferred from these arithmetic checks.
