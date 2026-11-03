# Referee report 4: industrial organization, economics of AI and digital markets

**Paper.** "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation" (Paper 1, v1; arXiv q-fin.GN, cross-list econ.GN).
**Materials read.** `notes/reviews/paper1_v1/paper1_v1.pdf` and `.txt`; `source_v1.tar.gz`, whose `sections/*.tex`, `paper1/refs_paper1.bib`, `paper1/macros.tex`, `code/calibrate_horizons.py` and `notes/calibration_results.json` are byte-identical to the working tree; `notes/partI_revision_memo.md`, `notes/assumptions_register.md`, `notes/assumptions_memo.md`, `data/tasks/params_reliability.yaml`, `notes/data_sources_reliability.md`, `notes/case_bending_spoons_f1_extract.md`.
**Focus.** The mapping of AI automation onto the frontier's parameters, the 2028/2031/2036 horizon ranges, the AI-and-firms literature, and the acquired-growth illustration (sec:acquired-growth).
**Date.** 29 October 2026. Every external claim below was checked at the source on this date (Section 4). Numbers marked "reviewer's arithmetic" were computed from the paper's own formulas and inputs, by a script kept outside the repository.

---

## 1. Summary

The paper models a firm's attainable (growth, FCF margin) set when growth is bought with expensed spend at diminishing returns (ass:growth). Rule-of-X lines are price lines whose tangency gives a closed-form maximal score (prop:score). Saturation and a log-share-headroom budget make extreme scores transient (prop:saturation, prop:budget, cor:transient). The firm's own growth weight is the marginal q of revenue (prop:dynamic), and the Rule of X is restated as a rule of economic profit (prop:general). On AI, the paper maps automation effects onto (m0, k, λ, G) (tab:ai-map, prop:ai, cor:priorities). It adds full-cost floors for running AI (def:fullcost, lem:fullcost, tab:fullcost) and an accountability floor with a common-mode misstatement term (prop:amin). It closes the full-automation ceiling at fixed prices (cor:ceiling, tab:ceiling), with Cournot free entry and a scarce-input rent as the competitive limit (prop:entry). It derives an attainable frontier under capacity and transition risk (prop:attainable, prop:expected) and calibrates horizon ranges for an "exceptional" firm (tab:calib). Finally it shows how acquired growth enters the score, with Bending Spoons as the illustration (prop:acquired-score, rem:acquired-bounds, tab:acquired-score).

The theory is clean, transparent and carefully proved. The acquired-growth measurement is a useful practitioner contribution. The "scenario, not forecast" labeling is consistent. My concerns are with the economics that link AI to the parameters and with the calibration built on them:

1. A key demand-elasticity source is misread.
2. The compute share, which sets the headline threshold, is grounded more weakly than the paper says, and evidence in the paper's own sources contradicts its "no measured analog" claim.
3. Every calibrated number holds output prices fixed, although the paper derives a pass-through lemma.
4. The free-entry conclusion rests on homogeneous Cournot, and the numerical rent example is infeasible under the paper's own costs.
5. One branch of the horizon calibration has no basis in the model.

## 2. Recommendation

**Major revision.** The core theory (sec:model-frontier to sec:model-industry, prop:general) can stand. The AI mapping and the horizon calibration need the changes in F1 to F7. The literature needs the additions in Section 5. None of the fixes requires new data beyond sources already in the replication package or verified below.

Severity counts: **5 major, 7 moderate, 7 minor** (19 findings).

---

## 3. Findings

### F1. [Major] The cited LLM demand elasticity does not imply a constant compute share

- **Location.** sec:lit, subsection "AI, automation and firms" ("short-run price elasticities of demand for inference just above one \citep{demirer2025emerging,demirer2026emerging} mean that spending on inference, and the compute share of our ceiling, need not fall"). sec:horizons, "How AI enters the parameters" ("spending on inference stays roughly constant as its price falls, so the compute share need not decline").
- **Issue.** The elasticity in the source is not a market or firm-level demand elasticity, so it cannot support the conclusion drawn from it.
- **Evidence.** In Demirer, Fradkin, Tadelis and Peng (NBER WP 34608, Dec 2025), the preferred estimate (about −1.11) comes from log daily tokens regressed on log price at the provider-model-day level. Identification uses within-model price differences across providers of the same open-source model on OpenRouter, with model×provider and date×model fixed effects. This is a substitution elasticity between providers of an identical model. The authors state that aggregate demand elasticities are "substantially smaller" and that their findings go against a Jevons effect in the short run (author PDF, mertdemirer.com). With an aggregate elasticity below one, inference spending falls as prices fall. The JEP article cited alongside it (demirer2026emerging, JEP 40(3), Summer 2026) states no elasticity in its abstract; it reports a roughly thousandfold fall in the price of intelligence and open models about 90% cheaper than closed ones.
- **Required change.** Rewrite both sentences. The source implies falling short-run spending, with long-run Jevons effects an open question. If a non-declining c_c is wanted, ground it elsewhere: the frontier price rise in Gundlach et al. (F2), the token intensity of agentic workflows, or ICONIQ's rising internal AI spend. Cite demirer2026emerging only for what it states.

### F2. [Major] The compute share is the headline parameter, and its grounding is weaker than stated

- **Location.** sec:horizons-ceiling, "Taxes, fees and compute" ("The compute share c_c has no measured analog"); the "Compute share" bullet; tab:ceiling; abstract, intro and conclusion thresholds; `notes/assumptions_register.md` Section 3 (rank 1).
- **Issue.** There are four problems. (a) The "no measured analog" claim is contradicted by the paper's own source. (b) The credible bounds of 1% and 55% measure different objects. (c) c_c does not depend on the horizon: neither tab:ceiling nor tab:calib carries an inference-price path, although the text discusses price declines at length. (d) One inference-price source is cited selectively.
- **Evidence.**
  - ICONIQ (iconiq2026state, the source the paper cites for AI gross margins) reports "spending on AI for internal productivity, including direct and indirect spend". It was 11% of revenue in 2025 and is projected at 16% in 2026 and 19% in 2027, all at partial adoption. This is an imperfect but measured analog for the internal-automation part of c_c, and it suggests that the central 20% at full automation is not conservative.
  - In the other direction, Stevens (2026, arXiv:2602.00139, preprint) finds about $0.03 of AI spend per $1 of displaced online-labor spend among the most exposed firms, which supports the low end.
  - The 1% lower bound comes from METR Time Horizon run costs (`code/data_part2/08_params.py`). These are 50%-success agent runs on software tasks. METR reports 80%-success horizons about 5× shorter than 50% horizons, and lower success on "messier" tasks (Kwa et al. 2025). ICONIQ reports an agentic workflow budgeted at $0.10 a run that exceeded $1.50 with retries. METR is not cited anywhere in Paper 1.
  - The 55% upper bound treats the entire cost of revenue of AI products as compute. ICONIQ says talent remains "the largest cost category".
  - Gundlach et al. (v2, 23 Mar 2026) state that price at fixed performance falls about 5–10× a year, and also that "the price of running frontier models is rising" 3–18× a year. The paper reports only the first.
  - dG*/dc_c = 1 − τ = 0.82, so the headline "about 42%" restates the scenario c_c. Over the stated bounds G* runs from 26% to 72%.
- **Required change.**
  - Write c_c as (labor-cost share automated) × (compute cost per dollar of labor replaced), and ground the second factor with the analogs above, including production overheads (retries, verification, orchestration).
  - Give c_c(t) for 2028, 2031 and 2036 from an explicit path of price and intensity, or state that it is horizon-invariant by assumption.
  - Cite METR and report Gundlach's frontier-price finding.
  - Delete "no measured analog", and plot G* against c_c in place of a single headline.

### F3. [Major] Every calibrated number holds output prices fixed, and the pass-through lemma is never used

- **Location.** cor:ceiling and its intuition; tab:ceiling; sec:horizons-ranges and tab:calib; the horizon sentences of the intro and conclusion (which do not restate "at fixed prices"); lem:prices; cor:priorities(iv); tab:ai-map.
- **Issue.** The ceiling and all horizon ranges assume zero pass-through. lem:prices is derived but not applied in any calibration. The paper does not distinguish a firm-specific cost shock from an industry-wide one. AI automation is a common technology rented from a handful of providers, so its cost savings are close to an industry-wide shock, for which pass-through is high.
- **Evidence.**
  - Weyl and Fabinger (2013) give the framework.
  - Ganapati, Shapiro and Walker (2020) find that 70% of energy-driven input-cost changes pass through to consumers in U.S. manufacturing.
  - Reviewer's arithmetic, using the paper's own linear-Cournot structure (ass:entry, A = 1, unit cost falling from 0.30 to 0.10): with n = 4 the price falls from 0.44 to 0.28 and the firm keeps 71% of the fixed-price gross-margin gain (31.8% to 64.3%, against 77.3% at a fixed price). With n = 10 the price halves and the firm keeps 50%.
  - Price declines of this size also lower nominal G while the transition runs whenever demand is inelastic (lem:prices(b)).
  - The paper's own practitioner source (lipman2026ai) argues that AI makes basic features easier to copy.
- **Required change.**
  - Add a pass-through dimension to tab:ceiling and tab:calib for variable-cost savings (c_h and compute), for example φ ∈ {0, 0.5, n/(n+1)}.
  - Separate savings in non-discretionary cost a, which Cournot does not pass through in the short run but which entry exposes (F4).
  - Distinguish idiosyncratic from industry-wide cost changes in lem:prices and cor:priorities(iv).
  - Add "at fixed prices" to every horizon sentence in the abstract, intro and conclusion.

### F4. [Major] The free-entry limit is specific to homogeneous Cournot, and the rent example is infeasible

- **Location.** prop:entry, rem:bertrand, the intuition of sec:model-entry, the third conclusion in sec:horizons-ceiling, the intro, and the last sentences of the abstract and conclusion ("Where entry is free, the limit is set by what stays scarce, not by what is automated"); the "Markups, rents and concentration" subsection of sec:lit.
- **Issue and evidence.**
  - **(a) Differentiated products.** L → 0 as F → 0 holds under homogeneous Cournot and contestability. Under differentiated-product monopolistic competition (Dixit and Stiglitz 1977; similarly logit), free entry dissipates profit through the number of varieties while the Lerner index stays at the level set by substitutability.
  - **(b) Endogenous sunk costs.** Under endogenous sunk costs (Sutton 1991), lower exogenous replication cost leads firms to escalate advertising and R&D. Those outlays are exactly this model's σ, and concentration need not fall.
  - **(c) Switching costs and network effects.** These are the main sources of rent in enterprise software (Farrell and Klemperer 2007). The model excludes network effects (rem:assumptions(d)) and has no switching costs.
  - **(d) Omitted evidence from a cited source.** Babina et al. (2024) find that AI-driven growth is concentrated among larger firms and associated with higher industry concentration; the paper does not mention this.
  - **(e) Rents may accrue upstream.** Foundation-model supply shows strong economies of scale and a tendency to tip (Korinek and Vipra 2025). The scarce input may therefore belong to the model provider and appear as a markup inside c_c (υ_c in rem:owncompute), not as the software firm's ρ.
  - **(f) The rent example is infeasible.** "Reaching 100 would require a rent ρ of 92.5 points of revenue" ignores the paper's own cost floors and taxes. With the central c_c, f, a_min and c_full of tab:ceiling, the margin term is 70.4 points before tax and 57.7 after. At G = 5% and k = 0.5 the score therefore cannot exceed 72.9 before tax or 60.2 after, whatever the rent (reviewer's arithmetic). A score of 100 is unattainable, not attainable with a 92.5-point rent.
- **Required change.**
  - State prop:entry(b) as a homogeneous-Cournot result.
  - Add a remark with differentiated products (CES or logit: the markup floor is set by substitutability) and one on endogenous sunk costs.
  - Note that rents can be captured upstream.
  - Restate the 92.5-point example on the after-tax, full-cost basis of tab:ceiling.
  - Qualify the abstract's last sentence, for example "where entry is free and products are close substitutes".

### F5. [Major] The lower-bound branch of the horizon calibration has no basis in the model

- **Location.** sec:horizons-ranges ("Anchor", "Ranges"); tab:calib notes; `code/calibrate_horizons.py` (`Pi_scaled`, `horizon()`, the `lower_bound` branch).
- **Issue.** In the case where "no selling and marketing expense buys growth" (σ = 0), the anchor residual R − R∞ (median 20, interquartile range 12 to 28 points) is labeled a growth surplus Π and scaled by μ^{1/(1−α)}. With σ = 0, however, eq:growth gives g = G. Excess growth without spend is firm-specific zero-spend growth G_i − G (rem:assumptions(b)), not the spend-bought surplus of prop:score(e). The elasticity μ^{1/(1−α)} follows from eq:Rstar only at optimal positive spend.
- **Evidence.** The 2028 and 2031 upper ends of the headline ranges (156 and 123, quoted in the intro and conclusion) come from this case: in 2028, 28 × 2^{1/0.55} ≈ 99 transient points. The upper-bound branch has a related problem. A quarter of the anchor firm-years have residuals of −17 points or less, which the paper reads as firms acting on X > 1. For those firms the observed R_1 is not R*_1, and the residual floored at zero is not Π_1, so scaling it by the comparative static of prop:score does not give the model's maximal score either.
- **Required change.** In the σ = 0 case, model excess growth as zero-spend growth G_i with its own scenario path, in the place rem:assumptions(b) assigns it, or drop the μ-scaling. In the σ > 0 case, invert each firm's opportunity, ℓ = Δ/σ^α, and compute Π_1 = C_α[ℓ(1−k)]^{1/(1−α)} rather than scaling an observed residual. Until this is fixed, quote headline ranges from the upper-bound case and say which case sets each end.

### F6. [Moderate] Horizon ranges: framing, attribution and technology held fixed

- **Location.** sec:horizons-ranges ("Pace", "Ranges", "Ownership"); tab:calib; intro and conclusion; sec:discussion, "Execution sets the pace".
- **Issue and evidence.**
  - **(a) The ranges are not bounds.** The "scenario bounds, not forecasts" label appears consistently, which I credit. But the ranges pair the low and high ends of independent scenario values, so neither end bounds anything. μ can exceed 2, the fastest-growing AI firms are private and outside the anchor, and pass-through and entry (F3, F4) are absent.
  - **(b) The low ends are misattributed.** The text says "the lower ends are set by central execution". In fact the low end is flat at 46 in every year in the upper-bound case, and falls from 40 to 35 to 31 in the lower-bound case, because G is assumed to fall (10%, 8%, 5%) and μ to fall (1, 0.75, 0.5) while Π is floored at zero. Central execution adds only 0.5 to 5 points of intercept (from 36 to 41). The 2028 upper end (156) exceeds the 2036 one (122) only because μ is assumed to decline; the text does not explain this. The G and μ paths are class-d values with no stated rationale (assumptions_register Section 3).
  - **(c) Technology is held fixed.** The 48-process program is assumed feasible from 2026, and the success probabilities (0.54, 0.80) and realized shares are constant to 2036. METR's 50% time horizons doubled about every seven months over 2019 to 2025 (Kwa et al. 2025). Under Time Horizon 1.1 (29 Jan 2026) the doubling time is about 131 days since 2023 and 89 days since 2024. The statement in sec:discussion that the difference between central and fast execution "lies in the success rate of transitions and the stability of their sponsorship, not in technology" is true by construction.
  - **(d) The pace sources measure different things.** The value 0.54 is one minus the share of AI proofs of concept that S&P Global found the average firm scrapped (46%), which is a screening outcome. The value 0.80 is BCG's success rate for whole digital transformations that meet six factors (30% overall; 825 executives; 2020), which is a program-level outcome. Both are used as per-process transition success probabilities, and neither is cited in Paper 1.
- **Required change.**
  - Call them "scenario ranges" and add a central path.
  - Add a tornado chart showing which assumption sets each end.
  - Motivate the G and μ paths, or derive μ from a share path through h(s).
  - Date the program's feasibility against a capability measure (for example, METR 80% horizons against process task lengths), or state that technology is non-binding by assumption and drop the "not in technology" sentence.
  - Cite the pace sources and discuss the mismatch between what they measure and what the parameters mean.

### F7. [Moderate] The growth-engine channel is partial equilibrium, and the AI map omits channels with a negative sign

- **Location.** tab:ai-map ("Cheaper customer acquisition", "Labor budgets shift to software"); prop:ai; cor:priorities(ii) and (iii); the intro sentence "Fast growers gain most from automating the growth engine"; the conclusion; Levers 2.
- **Issue.**
  - **Business stealing.** Shares within a market sum to at most one, so an industry-wide gain in acquisition productivity mostly reallocates share. The gain (X−k)Δ*dλ/λ holds for one firm only if rivals' λ is fixed. Under symmetric adoption in a contest model, spend can rise and margins fall.
  - **Negative channels.** Customers that automate shrink seat counts and net revenue retention for seat-priced vendors (G_i falls). AI-native entrants lower incumbents' λ and s̄.
  - **Unsupported channel.** "Labor budgets shift to software: G up" is asserted without evidence.
- **Required change.**
  - Qualify cor:priorities(ii) and tab:ai-map as gains relative to rivals.
  - Add a remark with symmetric adoption (for example, λ_i depending on σ_i/Σσ_j).
  - Add rows for seat compression and AI-native entry with sign "down".
  - Label the G channel as a scenario or give evidence for it.

### F8. [Moderate] Costs of errors, hallucination and misbehavior

- **Location.** def:fullcost(iii); lem:fullcost(c) to (e); rem:fullcost-values; tab:fullcost; the "AI failure" bullet of sec:horizons-ceiling.
- **Issue and evidence.**
  - **(a) Losses are scaled to labor cost.** The loss per undetected error is set at 0.25, 0.5 or 1 times the in-house labor cost of the unit. Losses from errors scale with the value at stake (a contract, a payment, a customer, a liability), not with the wage of the person replaced. Tying L_err to labor cost makes c_err small relative to labor savings by construction.
  - **(b) The conservative case is inconsistent.** It holds error rates at central values because worse rates "fail the scope test", while still imposing c_h = 0. A consistent conservative case leaves those activities human (c_h > 0) and lowers the ceiling. The 7.8-point case appears only as a sensitivity.
  - **(c) Units do not match.** The omission rate of 0.0345 is per transcript sentence in clinical summarization (Asgari et al. 2025, per `notes/data_sources_reliability.md`), but it is applied per unit of business work.
  - **(d) Only the cost channel is modeled.** Errors raise a, but do not affect demand (λ, net revenue retention) or liability.
  - **(e) Relevant field evidence is missing.** Human–AI combinations do worse than the better of human or AI alone (Hedges' g = −0.23 across 106 experiments; Vaccaro et al. 2024). AI use on tasks outside the "jagged frontier" lowered correctness by 19 percentage points (Dell'Acqua et al.). Both support the paper's low catch rates but are not cited in Paper 1.
- **Required change.** Parametrize L_err as value at stake per unit, with a sensitivity. Make the conservative case consistent. State the units of each rate. Add the demand-side error channel, at least as a remark. Cite the field evidence.

### F9. [Moderate] The accountability floor is well modeled but weakly connected to the calibrated band

- **Location.** prop:amin; rem:amin-values; the "Accountability floor" paragraph of sec:horizons-ceiling; sec:discussion, "The accountability floor".
- **Issue and evidence.**
  - **(a) The band is not derived from the proposition.** prop:amin is correct and its common-mode insight is useful. The central (3%) and conservative (4.6%) values, however, are residual G&A shares of lean large firms, 12 to 19 times the bottom-up floor of about 0.24% at $1 billion (0.14% direct audit and Section 404 costs plus 0.10% for the best design). The proposition grounds the lower end, as the paper says; the central value is not an estimate of accountability cost.
  - **(b) Loss per misstatement.** L_mm is fixed in dollars, but materiality scales with firm size. With L_mm proportional to S, the common-mode term per dollar of revenue in prop:amin(c) is constant, which strengthens "does not fall with scale". Say so.
  - **(c) Unsupported scarce-input claim.** sec:discussion says that "firms that can bear accountability credibly and cheaply hold a scarce input". In prop:entry(c) a scarce input is in fixed supply per unit of output, and accountability capacity is not shown to be.
  - **(d) Sourcing.** The example values (N_mm = 24, L_mm = $10M, p^cm = 0.005) are illustrative and are sourced to an unavailable companion paper.
  - **(e) Small effect on the headline.** Over the band, G* moves only from 40% to 44%.
- **Required change.** Present the central a_min as residual G&A, or derive it from sourced audit-fee and SOX-cost data and cite them in Paper 1; the register already has $343 of audit fees per $1M of revenue for the S&P 500 in FY2022 and a SOX 404 median of $1.04M. Formalize the scarce-input claim or drop it. Connect the floor to the economics of judgment (Agrawal, Gans and Goldfarb 2019) and to O-ring complementarity (Gans and Goldfarb 2026).

### F10. [Moderate] Security, maintenance and ancillary floors

- **Location.** lem:fullcost(a) and (b); tab:fullcost; rem:owncompute; sec:model-ai ("security ... grows only with the logarithm of exposure").
- **Issue and evidence.**
  - **(a) Log growth is assumed, not found.** That security cost grows with the log of exposure follows from the exponential breach function assumed in lem:fullcost(b) (Gordon–Loeb class II). For agents with write and transact rights, prompt injection has no complete defense, so residual loss may grow with exposure.
  - **(b) The security baseline is weakly matched and uncited.** The IANS figure (0.69% of revenue; 587 CISOs; 2025; verified) is a cross-industry average of current spend, not software firms and not agent exposure, and it is not in Paper 1's bibliography. The code uses a central security share of IT spend of 9.9%; IANS 2025 reports 10.9%.
  - **(c) The build stock is a scenario value that sets c_mnt in proportion.** It is 48 processes × $0.5M at $1 billion of revenue (2.4% of revenue), which looks small against the labor it replaces (W_A = 30% of revenue).
  - **(d) Asset lives are mismatched.** rem:owncompute pairs Epoch's 60% server share, computed for a 1 GW AI data center with a 5-year IT life, with a 5.5-year book life that is not sourced.
- **Required change.** Add a sensitivity with a class I (power) breach function. Cite IANS. Source the build stock or widen its range. Reconcile the asset lives.

### F11. [Moderate] Sourced parameters lack citations in Paper 1, and some sourcing depends on an unavailable companion paper

- **Location.** sec:horizons ("Taxes, fees and compute", "Full-cost floors", "Pace"); tab:fullcost; rem:fullcost-values; rem:amin-values; sec:model-attainable; the bibliography.
- **Issue.** Parameters labeled "sourced" or "grounded by precedent" have no citation in Paper 1. These include the IANS survey, the S&P Global proof-of-concept survey, BCG's six factors, JOLTS layoffs and restructuring filings, Korn Ferry tenure, METR run costs, card fees, and GAO-23-105384 and 26 U.S.C. 11(b), which are named in the text but absent from the bibliography. The horizons section has only 10 citations. Several numbers rest on murthy2026transformation, which is "in preparation", while the paper says it does not depend on it.
- **Required change.** Add a bibliography entry for every class a or b source used in Paper 1. Either post the companion paper or move the sourcing Paper 1 needs into an appendix.

### F12. [Moderate] Missing literature

- **Location.** sec:lit, especially the "AI, automation and firms" and "Markups, rents and concentration" subsections.
- **Issue.** An AI-economics audience will expect several papers that are absent: the canonical task-based framework, AI as prediction and judgment, the market structure of AI, data competition, adoption measurement, capability measurement, field evidence on realized gains, pass-through, and the IO of entry with differentiation. Several of these already sit in the companion bibliographies (`notes/ref_verification_*.md`), so adding them costs little.
- **Required change.** See Section 5 for verified references and where each one belongs.

### F13. [Minor] The adoption series splices two different survey questions

- **Location.** sec:lit: "firm use rose from 3.7% of firms in September 2023 \citep{bonney2024tracking} to 18% by early 2026 \citep{bonney2026microstructure}".
- **Evidence.** In November 2025 the Census Bureau broadened the BTOS AI question from use "in producing goods or services" to use in any business function. The new series reads higher in every industry examined, by 47% to 159% (FEDS Notes, "Monitoring AI Adoption in the U.S. Economy", 3 April 2026).
- **Required change.** State the break, or compare like with like.

### F14. [Minor] A conclusion does not follow from the ICONIQ gross margins

- **Location.** sec:horizons, "How AI enters the parameters": "... so automation shifts cost from operating expense into cost of revenue rather than removing it".
- **Issue.** ICONIQ's margins are for AI products sold to customers. Automating internal G&A and R&D moves cost within operating expense, not into cost of revenue.
- **Required change.** Restrict the claim to automated service delivery, or cite evidence for it.

### F15. [Minor] Bending Spoons: the figures are accurate, but the framing needs balance

- **Location.** The intro paragraph "Measurement matters ..."; sec:acquired-growth ("The company's own split", "Worked numbers"); prop:acquired-score(d) and (f); sec:discussion.
- **Accuracy.** I recomputed every figure in tab:acquired-score and the text from the F-1 extract: growth of 73.4% and 94.7%; margins of 19.0% and 21.3%; interest of 4.9% and 10.9%; scores of 92.3, 115.9, 105.0, 116.9 and −24.8; CRF from 10.8% to 14.6%; T_life from 10.6 to 19.5 years; price multiples of 1.7 to 3.2. All match. The Q2 2026 6-K figures (+126% revenue growth, 3% organic growth, 34% operating margin) match the SEC exhibit. The Nasdaq listing in July 2026 matches Dealroom, and the 9.34% cost of capital matches Damodaran (January 2026).
- **Fairness and accuracy fixes.**
  - **(a) The treadmill framing omits positive organic growth.** The intro says that "absent new customers, standing still requires acquiring revenue at that rate". The company reports +3% organic growth in Q2 2026, and 76% to 83% of its new-customer revenue came from organic channels. New customers therefore more than offset the NRR decay in that quarter. NRR also covers only subscription revenue, so AOL advertising and Eventbrite fees fall outside it. Put the +3% next to the treadmill sentence.
  - **(b) Log versus simple rates.** "Shrinks by 5.1 to 9.4% a year" uses log rates, −ln NRR. The simple rates are 5% to 9%.
  - **(c) "Only through amortization" is wrong.** rem:acquired-bounds says that on the GAAP basis acquired growth reaches the score "only through the amortization of acquired finite-lived intangibles". Acquisition-related costs are also expensed (ASC 805), as is impairment; the paper's own worked numbers show transaction expense of 6.5% of revenue.
- **Required change.** Make these edits.

### F16. [Minor] The annuity charge is inconsistent with the rule that sets its life

- **Location.** rem:acquired-bounds; "Worked numbers"; tab:acquired-score.
- **Issue.** T_life = −1/ln NRR is the mean life of revenue that decays exponentially. The user cost consistent with that decay is (r + δ) on each vintage's depreciated value, with δ = −ln NRR. The paper instead charges a level CRF(r, T_life) on undepreciated outlays.
- **Evidence.** Reviewer's arithmetic, using the F-1 outflows of $170.3M (2023), $889.7M (2024) and $1,851.9M (2025), and r = 8.93%. With NRR between 0.91 and 0.95, the user-cost charge is 30.7 to 39.4 points, against the paper's 24.1 to 32.5. The 2025 annuity score is then 77.5 to 86.2 rather than 84.4 to 92.8. A charge consistent with prop:general, where capital does not depreciate, would be r·K instead.
- **Required change.** Report the user-cost version, or justify the CRF convention and state the direction of its bias.

### F17. [Minor] Under central execution the program is close to break-even

- **Location.** sec:horizons-ranges ("Pace"); rem:regimes(ii).
- **Evidence.** Reviewer's fluid approximation with the parameters of `calibrate_horizons.py`: a dip of 3.9 points a year, embedding of 3.05% of the program a year, a 2-year lag and r = 10%, with no revenue growth. The present value of embedded gains is about 0.44 revenue-years, against 0.38 for the in-flight dip. Gains first exceed the dip after about 9 years, as the paper reports. A value-maximizing owner that admits only transitions that pay within its rate and horizon (rem:regimes(ii)) might not run this program at this pace.
- **Required change.** Report the program's NPV under each pace. Note that the low end pairs an "exceptional" firm with a marginal program.

### F18. [Minor] Characterizations of cited sources

- **(a) acemoglu2024regulating.** The paper derives gradual *socially optimal* adoption, not a firm's private adoption under transition risk. Say so.
- **(b) farboodi2023data.** "The largest firms ... are valued chiefly for their data" is an assertion in the abstract of a review, not a finding. Cite it as such.
- **(c) farboodi2021model.** The increasing-then-diminishing-returns result is in the introduction of the June 2026 manuscript, which is hosted on restud.com. Check its publication status and update the entry.
- **(d) omb2024report.** "The only quantified migration cost" is a universal negative. The OMB estimate ($7.1 billion, 2025 to 2035) covers prioritized federal systems, excludes national-security systems, and carries a "high, but expected, level of uncertainty".
- **(e) lem:prices(a).** "with equality if and only if b = 0": b is undefined (presumably k_u).
- **(f) michael2026servers.** Epoch's 60% figure uses a 5-year IT life (see F10(d)).

### F19. [Minor] The 42% threshold is mostly taxes and compute

- **Location.** Abstract; intro; sec:horizons-ceiling.
- **Issue.** G* = τ + (1−τ)(c_c + f + a_min + c_full). In the central case the 42.3 points split into 18.0 for taxes, 16.4 for compute, 2.1 for fees, 2.5 for the accountability floor and 3.4 for the full-cost floors (reviewer's arithmetic). The accountability and AI-running floors, which the abstract and intro feature as contributions, move the threshold by under 6 points.
- **Required change.** State this decomposition where the threshold is first quoted.

---

## 4. Citation check

**Method.** Each source was fetched at the publisher, NBER, RePEc, arXiv, SEC or issuer page, or the author's PDF, on 29 Oct 2026. "Verified" means that the bibliographic data and the specific claim match. 31 bibliography entries and 4 sources that Paper 1 uses but does not cite were checked.

| # | Key | Claim in the paper (location) | Source checked | Verdict |
|---|---|---|---|---|
| 1 | epoch2025inference | Price at fixed benchmark performance fell 9–900× a year (sec:lit, sec:horizons) | epoch.ai data insight, 12 Mar 2025 | Verified. No median is given. |
| 2 | gundlach2025price | About 5–10× a year at fixed performance (sec:lit) | arXiv:2511.23455 v2 abstract | **Selective.** The same abstract says frontier prices rise 3–18× a year; omitted (F2). |
| 3 | demirer2025emerging | Elasticity "just above one", so the compute share need not fall (sec:lit, sec:horizons) | NBER w34608; author PDF, Table 2 | **Mischaracterized.** The number is right, but it is a within-model, across-provider elasticity, and the authors say aggregate elasticities are "substantially smaller" (F1). |
| 4 | demirer2026emerging | Same elasticity claim (sec:lit) | JEP 40(3), Summer 2026 contents and abstract | Metadata verified. **The claim is not in the abstract.** |
| 5 | iconiq2026state | AI-product gross margins 45/53/59%; 55% cost of revenue as the c_c upper bound (sec:horizons) | iconiq.com report page | Numbers verified. **Used for a claim it does not support** (F14); the same report's internal AI spend of 11/16/19% of revenue contradicts "no measured analog" (F2). |
| 6 | bick2026rapid | Generative AI assisted 1–5% of work hours; Management Science 72(10) | NBER w32966 | Verified. |
| 7 | bonney2024tracking | 3.7% of firms in September 2023 | NBER w32319 | Verified; this is the narrow BTOS question. |
| 8 | bonney2026microstructure | 18% of firms; most use AI in ≤3 functions; performance rises with breadth | RePEc nberwo 35141 | Verified (57% use ≤3 functions; association only). **Spliced across a change in the question** (F13). |
| 9 | eisfeldt2023generative | 5% excess return in the two weeks after ChatGPT | NBER w31222 | Verified (revised January 2026). |
| 10 | hampole2025artificial | Exposure lowers task-level labor demand; adopting firms grow | NBER w33509 | Verified: productivity-driven labor-demand gains at adopters. |
| 11 | babina2024artificial | AI investors grow through product innovation | RePEc, JFE 151 | Verified. **Omits** the finding that AI growth is concentrated in large firms and linked to higher concentration (F4). |
| 12 | brynjolfsson2025generative | QJE 140(2), 889–942 | OUP page | Metadata verified. |
| 13 | acemoglu2025simple | Modest aggregate effects | NBER w32487 / Economic Policy | Verified: at most 0.66% TFP over 10 years. |
| 14 | acemoglu2024regulating | Optimal adoption is gradual | AEA, AER: Insights 6(3), 359–76 | Verified, with a qualification: the result is for socially optimal adoption (F18). |
| 15 | svanberg2024beyond | 23% of exposed wages economical to automate; upkeep δ_M | MIT FutureTech | 23% verified. The upkeep rate is not in the abstract and was not verified. |
| 16 | cottier2024rising | Amortized training cost grows 2.4× a year | arXiv:2405.21015 | Verified. |
| 17 | farboodi2023data | Largest firms "valued chiefly for their data" | Annual Reviews abstract | Wording verified; it is an assertion, not a finding. |
| 18 | farboodi2021model | Increasing returns to data early, diminishing in the long run | NBER w28427; June 2026 manuscript | Verified in the introduction, not the abstract. Check publication status. |
| 19 | prufer2021competing | Data-driven markets tip | EconPapers, JIE 69(4), 967–1008 | Verified: "tip under very mild conditions". |
| 20 | moody2026transition | Deprecated after 2030, disallowed after 2035; final version October 2026 | NIST CSRC page and the IR 8547 PDF | Verified. Final version dated 27 Oct 2026. |
| 21 | omb2024report | "Only quantified" migration cost, for federal systems | Summary of the OMB report (The Quantum Insider) | $7.1 billion for 2025–2035 verified (secondary). "Only" is unverifiable (F18). |
| 22 | tewari2026pilot | Staged commitment through pilots | arXiv:2609.15919 | Verified (preprint). |
| 23 | michael2026servers | Servers are 60% of total cost of ownership | Epoch data insight, 14 May 2026 | Verified. Epoch assumes a 5-year life; the paper uses 5.5 years. |
| 24 | argente2025how | Entrants reach more customers; no markup differences | AEA, AER: Insights 7(2), 160–76 | Verified (consumer food entrants). |
| 25 | fitzgerald2024how | Flat markups; growth through marketing | EconPapers, REStud 91(4), 2276–2306 | Verified (Irish exporters). |
| 26 | afrouzi2023concentration | Share tied to customer count, markup to sales per customer | NBER w31415 | Verified. |
| 27 | lee2024evaluating | 1,756 SaaS firms, 2003–2022; "Rule of 65" | Journal page | Verified. |
| 28 | lipman2026ai | Inference adds variable cost; a "Rule of 30" for a while | bain.com, 8 Apr 2026 | Verified. |
| 29 | damodaran2026cost | 9.34% cost of capital for software | NYU Stern wacc page, January 2026 | Verified (Software, System & Application). |
| 30 | dealroom2026ipo | Nasdaq listing in July 2026; $1.68bn raised | dealroom.co, 1 Jul 2026 | Verified (Nasdaq Global Select, ticker BSP, $29 a share). |
| 31 | bendingspoons2026sixk | Q2 2026: +126% growth, 3% organic growth, 34% operating margin | SEC 6-K, Exhibit 99.1 (13 Aug 2026) | Verified, including the definition of organic growth. |
| 32 | (uncited) IANS 2025 | Security spend of 0.69% of revenue (tab:fullcost) | ians.com benchmark FAQ | Verified (587 CISOs). **Not in the bibliography.** |
| 33 | (uncited) S&P Global | 46% of AI proofs of concept scrapped, behind the 0.54 success rate (sec:horizons) | CIO Dive report of the survey, 14 Mar 2025 | Verified (secondary). **Not in the bibliography.** |
| 34 | (uncited) BCG 2020 | 80% success with six factors, behind the 0.80 success rate (sec:horizons) | bcg.com, 29 Oct 2020 | Verified (30% overall; 825 executives). **Not in the bibliography.** |
| 35 | (uncited) METR run costs | c_c lower bound of 1% (sec:horizons-ceiling) | metr.org, Time Horizon 1.1, 29 Jan 2026 | **METR is not cited in Paper 1.** |

**Wrong or mischaracterized:** demirer2025emerging and demirer2026emerging (F1); gundlach2025price, by omission (F2); iconiq2026state, used for an unsupported claim while contradicting data in the same report is ignored (F2, F14); bonney2024tracking with bonney2026microstructure, spliced across a question change (F13).
**Qualifications only:** acemoglu2024regulating, farboodi2023data, omb2024report, michael2026servers, babina2024artificial (omission). No bibliographic metadata error was found among the entries checked.

---

## 5. Missing literature (each reference verified on 29 Oct 2026)

**Task-based automation, and AI as prediction and judgment.** These belong in sec:lit "AI, automation and firms" and in the discussion of the accountability floor (F9) and the attainable frontier.

- Acemoglu, D. and Restrepo, P. (2018). "The Race between Man and Machine: Implications of Technology for Growth, Factor Shares, and Employment." *American Economic Review* 108(6), 1488–1542. doi:10.1257/aer.20160696.
- Agrawal, A., Gans, J. and Goldfarb, A. (2019). "Exploring the Impact of Artificial Intelligence: Prediction versus Judgment." *Information Economics and Policy* 47, 1–6. doi:10.1016/j.infoecopol.2019.05.001. Its argument that "not all human judgment will be a complement to AI" bears directly on a_min.
- Agrawal, A., Gans, J. and Goldfarb, A. (2024). "Artificial Intelligence Adoption and System-Wide Change." *Journal of Economics & Management Strategy* 33(2), 327–337. It shows system-level rather than task-by-task adoption, which is the logic of the attainable frontier.
- Gans, J. S. and Goldfarb, A. (2026). "O-Ring Automation." NBER Working Paper 34639. With complementary tasks, adoption is discrete and bundled, and exposure indices overstate displacement.

**Market structure of AI and data.** These belong in prop:entry and the "Markups, rents and concentration" subsection (F4).

- Korinek, A. and Vipra, J. (2025). "Concentrating Intelligence: Scaling and Market Structure in Artificial Intelligence." *Economic Policy* 40(121), 225–256.
- Gans, J. S. (2024). "Market Power in Artificial Intelligence." NBER Working Paper 32270.
- Hagiu, A. and Wright, J. (2023). "Data-Enabled Learning, Network Effects, and Competitive Advantage." *RAND Journal of Economics* 54(4), 638–667. It states when a data rent ρ is durable.

**IO of pass-through, entry and differentiation.** These belong in F3 and F4.

- Weyl, E. G. and Fabinger, M. (2013). "Pass-Through as an Economic Tool: Principles of Incidence under Imperfect Competition." *Journal of Political Economy* 121(3), 528–583. doi:10.1086/670401.
- Ganapati, S., Shapiro, J. S. and Walker, R. (2020). "Energy Cost Pass-Through in US Manufacturing: Estimates and Implications for Carbon Taxes." *American Economic Journal: Applied Economics* 12(2), 303–342. doi:10.1257/app.20180474. It finds 70% pass-through of an industry-wide cost shock.
- Dixit, A. K. and Stiglitz, J. E. (1977). "Monopolistic Competition and Optimum Product Diversity." *American Economic Review* 67(3), 297–308.
- Sutton, J. (1991). *Sunk Costs and Market Structure: Price Competition, Advertising, and the Evolution of Concentration*. MIT Press.
- Farrell, J. and Klemperer, P. (2007). "Coordination and Lock-In: Competition with Switching Costs and Network Effects." In *Handbook of Industrial Organization*, vol. 3, ch. 31. Elsevier.
- Autor, D., Dorn, D., Katz, L. F., Patterson, C. and Van Reenen, J. (2020). "The Fall of the Labor Share and the Rise of Superstar Firms." *Quarterly Journal of Economics* 135(2). These are scale-driven high-margin firms, the population at the top of the score distribution.

**Adoption, realized gains and the reliability of human–AI review.** These belong in sec:lit, the pace parameters (F6) and c_err (F8).

- McElheran, K., Li, J. F., Brynjolfsson, E., Kroff, Z., Dinlersoz, E., Foster, L. and Zolas, N. (2024). "AI Adoption in America: Who, What, and Where." *Journal of Economics & Management Strategy* 33(2), 375–415.
- Federal Reserve Board (2026). "Monitoring AI Adoption in the U.S. Economy." FEDS Notes, 3 April 2026. It documents the BTOS question change (F13).
- Humlum, A. and Vestergaard, E. (2025). "Large Language Models, Small Labor Market Effects." NBER Working Paper 33777 (also BFI Working Paper 2025-56). It finds precise null effects on earnings and hours, evidence for a low realized-benefit share b̄.
- Becker, J., Rush, N., Barnes, E. and Rein, D. (2025). "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity." arXiv:2507.09089. In a randomized trial, AI tools increased completion time by 19%.
- Dell'Acqua, F. et al. (2023). "Navigating the Jagged Technological Frontier: Field Experimental Evidence of the Effects of AI on Knowledge Worker Productivity and Quality." Harvard Business School Working Paper 24-013 (SSRN 4573321). Inside the frontier, users completed 12.2% more tasks and worked 25.1% faster; outside it, correctness fell by 19 percentage points. I could not confirm the journal version.
- Vaccaro, M., Almaatouq, A. and Malone, T. (2024). "When Combinations of Humans and AI Are Useful: A Systematic Review and Meta-Analysis." *Nature Human Behaviour* 8(12), 2293–2303.
- Stevens, R. (2026). "Payrolls to Prompts: Firm-Level Evidence on the Substitution of Labor for AI." arXiv:2602.00139 (preprint). It finds about $0.03 of AI spend per $1 of displaced online-labor spend, an analog for c_c (F2).

**Capability measurement and scenario method.** These belong in F2 and F6.

- Kwa, T., West, B., Becker, J. et al. (2025). "Measuring AI Ability to Complete Long Software Tasks." arXiv:2503.14499 (v4, July 2026). It finds a 7-month doubling time and 80% horizons about 5× shorter than 50% horizons.
- METR (2026). "Time Horizon 1.1." 29 January 2026, metr.org. Doubling time is 131 days since 2023 and 89 days since 2024. This is the source of the run costs behind the c_c lower bound.
- Korinek, A. and Suh, D. (2024). "Scenarios for the Transition to AGI." NBER Working Paper 32255. It is a precedent for presenting AI outcomes as labeled scenarios.

---

## 6. What the paper does well, and should keep

- The supporting-line reading of the Rule of X (prop:score) and the share-headroom budget (prop:budget, cor:transient) are clean, general and new to this literature.
- prop:amin's separation of depth from diversity, and its common-mode floor, is a sharp and portable insight for AI-run controls.
- The acquired-growth decomposition (prop:acquired-score(a), (e) and (f)) and the charging bounds (rem:acquired-bounds) are useful for practice, and the Bending Spoons figures reproduce exactly from the filings.
- The disclosure practices are exemplary and should remain: the assumptions register, the "scenario, not forecast" labels, and stating which parameters are class d.
