# Specialist B first report: econometrics, frontier estimation and empirical IO

**Frozen first report; no current specialist report or external model critique read.** Sources: `work/frozen/paper1_nov_2.pdf` (SHA-256 bd87f45fed9c45587eec3d41b3b6dc3b08bbb73ef794773fe8fbbb74a5c6f9cf), `work/frozen/supplement_nov2.pdf` (acf9d62bb96961a45400f2e52013cb4da79ed0d34d8cf0574ec7553226de02c2). Main has 82 PDF pages, supplement 57. At the locators below, printed pages equal one-based PDF pages; zero-based PDF indices are one less. This is a separate agent context in the same Codex GPT-6-family environment and shared filesystem as the coordinator and other agents. No exact provider model version was exposed to this agent; no independence across model families or human expertise is claimed.

## Assessment

The empirical component is potentially useful as a descriptive accounting panel and choice-distribution study. It does not identify a technological frontier, the weight firms place on growth, a spend elasticity, saturation, AI's causal effect, or the cause of the historical upper-tail decline. The paper now explicitly recognizes most of those limits. Its strongest defensible findings are measurement-basis sensitivity, a broadly negative point-estimated historical P95 change, differences between pooled dominance-cone and local quantile summaries, and an accounting decomposition of margin differences. Publication as an empirical economics article requires a usable frozen replication package, a historically credible population definition, and inference appropriate to a clearly stated superpopulation. A practitioner working paper can retain descriptive evidence with those limits prominently stated. My recommendation within this remit is **major revision**, chiefly to correct a surviving common-frontier identification argument and make the empirical result independently reproducible. This is not a rejection of Proposition 3's non-identification result; that result is sound in its stated setting.

## Reconstructed estimands and dependence

* A firm's technological frontier `m_i*(g)` contains feasible choices conditional on its technology, market and share.
* `Phi(g)=sup_i m_i*(g)` is the possibility envelope, assuming common market growth and the paper's feasible domains.
* `Psi(g)=sup{m_i^c:g_i^c>=g}` is the free-disposal envelope of chosen points, a different object.
* `Psi_chi(g)=Q_chi(m^c | g^c>=g)` is a pooled conditional quantile over a changing set of faster growers. It is a partial frontier/choice-distribution statistic, not a local conditional quantile or, at fixed chi<1, a consistent estimator of the full boundary merely because sample density grows.
* The primary estimated slope is an equally weighted LS projection of that quantile on 13 thresholds `0,.05,...,.60`, not the marginal cost of growth of a firm.
* The local linear quantile-regression coefficient is another projection, not generally the derivative of a true conditional-quantile curve.
* Period P95 changes are descriptive changes in the distribution of qualifying firm-years. Firms with longer observed histories receive more total mass in pooled periods; that is compatible with the stated firm-year estimand.
* The 2028-2036 anchor is a selected group of 13 firm-years belonging to seven firms, not 13 independent firms and not a population of all software firms.

Dependency: raw filing vintages/tags -> measured annual growth and accounting margins -> inclusion/acquisition flags -> E1/E2/imputed distributions -> cone/score/anchor statistics -> descriptive historical claims and scenario anchor. The growth-weight and technology claims additionally require optimization and precise spend/excess-growth measurement, which the paper correctly says are not established.

## Major finding B1: density does not justify the common-frontier slope mapping

**Location.** Main §3.7 opening, p23; supplement §S2.3, p7. The supplement first correctly expresses `Psi_chi` as the common frontier evaluated at a conditional growth quantile, then claims its slope approximates the frontier slope when growth is dense. Main p23 uses that approximation to map the observed slope to technology and infer that firms' weights cannot exceed a multiple of the estimated slope under a common frontier.

**Classification.** Demonstrated error in the slope-transport/inference argument; missing distributional condition for an approximation. Not a refutation of Proposition 3 or a claim that its proofs are missing.

**Independent analytic evidence.** Let growth have continuous strictly increasing CDF F and positive density at the evaluation points. With strictly decreasing common frontier m*,

`Psi_chi(g) = m*(q(g)),  q(g)=F^{-1}(1-chi+chi F(g))`,

and

`Psi_chi'(g)=m*'(q(g)) chi f(g)/f(q(g))`.

Both a shifted evaluation point and a density ratio remain in the exact population. A dense sample does not remove either. The paper's LS formula for a power frontier projected on an equally spaced grid is useful when the grid values are the frontier itself. It cannot be applied to the cone-quantile slope without deriving the quantile transformation.

**Counterexample satisfying the stated common-frontier alternative.** Use alpha=.3, beta=10/3, G=k=0, m0=.8, ell=.721826999314566, spend cap=1. Let all firms share `m*(g)=.8-(g/ell)^beta`, and choose growth in `[0,W]`, W=.6, by acting on heterogeneous weights `X(g)=beta g^(beta-1)/ell^beta`. These choices are exact unique score optima (apart from the harmless zero-growth corner), with spend at most .54<1, margins in [.26,.8], and weights in [0,3]. Give growth CDF `F(g)=(g/W)^p`, p=14.833990914027952, continuous and strictly increasing on the full interval. Then `q(g)=W[.1+.9(g/W)^p]^(1/p)` for chi=.9. The exact cone LS slope on the author's grid is -.2200000000, while the true frontier's steepest slope is -3. The proposed multiplier yields .8474074 as its magnitude, underestimating it by a factor 3.54. Firms commonly act on weights above one in this common-frontier example. Thus a flat cone slope alone cannot rule out a common frontier with high decision weights.

**Computational check.** `outputs/review_bundle/B/diagnostics.py` and `inputs.json` produce `results.json`, `population_grid.csv`, and `optimization_checks.json`. No author panel/code was used. Bounded scalar optimization independently checked 101 positive-growth choices on spend [0,1], x tolerance 1e-13, maximum score discrepancy 6.66e-16, all converged. Four central finite differences (h=1e-6) match the derived cone derivatives within 6.74e-11. Dense deterministic weighted support meshes of 1,001/10,001/100,001 points yield cone slopes -.2192177/-.2198698/-.2199902, converging to -.22 while the true maximum slope remains 3. No randomness or symbolic-engine verification is claimed. The distribution power was chosen by Brent root finding on [10,20] with SciPy defaults to make the illustration match -.22; this is a counterexample construction, not a fitted empirical population.

**Strongest author defense.** The paper explicitly distinguishes choices from possibilities, correctly states that growth quantiles enter, and Proposition 3(iv) concludes non-identification. Section S2.3's second paragraph gives a valid selection-by-quality example. The approximation might be intended only for a nearly identity quantile map or chi approaching one with suitable derivative regularity.

**Why the finding survives/narrows.** Those defenses preserve the broad non-identification conclusion, but contradict the positive identification claim made under dense common-frontier choices. Fixed chi=.9, density alone and the power frontier do not ensure a nearly identity map. No common-frontier distributional condition is supplied. The counterexample does not challenge the abstract's reported descriptive slope or the finite-budget/static-frontier theory.

**Smallest repair and acceptance test.** Delete the current parameter/maximum-weight inference based only on observed cone slopes, or state conditions controlling both q(g)-g and q'(g)-1 and derive the corrected projection through F. Retain Proposition 3(iv). Run the corrected method on the exact population above and on uniform/exponential/uneven-support alternatives. It must not report .847 as the true maximum weight in this example. Rename the empirical statistic consistently as a pooled choice quantile where "a point of growth costs..." could otherwise imply a firm's marginal trade-off.

## Important replication and inference questions (not demonstrated invalid estimates)

### B2. No accessible panel/code means empirical tables are not reproduced

**Location.** Main §§4-5 and Table 2 pp36-47; supplement S6 pp28-43; main footnote p1 says data and code available from author. Supplement p43 lists retrieval/build/estimation/calibration/theory scripts and regeneration commands.

**Classification.** Unresolved replication question. The coordinator's GitHub connector returned 404 and its web fetch failed at this point in the first pass; no author script or raw panel is available to this specialist. This is not evidence that the repository or data never exist.

**Evidence and defense.** The text supplies detailed tag lists, filing-vintage choices, seeds, bootstrap rules, sensitivity tables and withdrawal of unsupported earlier interpretations. Those are unusually helpful and permit internal checks. They do not substitute for actual data and executable code.

**Resolution needed.** Freeze the repository commit and environment; distribute the companyfacts extract/accession/year/tag/unit records, universe and exclusion/inclusion decisions, both panel vintages, all derived result files and random seeds, plus exact commands. Reproduce every entry of Table 2, S4-S10 and S12 and the figure/text macros; compare to independently written extraction/estimators. Include structured reasons for every discarded fact and every missing margin. Author-code execution and independent re-estimation must be labeled separately.

### B3. Qualify inferential scope, tail support and borderline Monte Carlo decisions

**Location.** Main §5.1 p42 and §5.3 p44; supplement S6 p29; Table S5 p31.

**Classification.** Missing inferential assumptions and unresolved robustness question, not proof that cluster bootstrap intervals fail.

**Evidence.** Firm resampling preserves serial dependence but does not resample calendar-level common shocks. E2's highest primary cone has only 37 firm-years, so its 90th percentile has about 3.7 nominal observations above it, potentially fewer independent firms. The draw threshold drops from 30 to 10 firm-years; 16.8% (GAAP) and 13.0% (cash) of E2 draws miss the sample's 30-firm-year rule. The manuscript discloses this and reports similar intervals on draws satisfying the strict rule. It withholds the 40%-growth period frontier where support is insufficient, correctly withdrawing that claim. The anchor has seven independent firm identities at most. With 999 replications, a resampling p-value .097 has an illustrative binomial Monte Carlo standard error about .00936; its exact value depends on the implemented stepdown algorithm.

**Strongest defense.** The historical comparison can target the cross-section of firm trajectories conditional on realized macro history. Under conditional independent firm clusters and positive quantile densities, a cluster bootstrap is reasonable. Fixed partial quantiles are not maximum-boundary estimators, so it would be incorrect to reject ordinary bootstrapping merely by citing generic FDH bootstrap problems. A lower draw threshold avoids artificial undefined estimates, and strict-rule sensitivity is disclosed.

**Narrowed surviving issue.** State the target of inference and dependence assumptions; do not interpret firm-bootstrap precision as uncertainty over alternative macro histories. Report unique firm counts, tail-support firms and leave-one-firm sensitivity at every consequential cone cell and anchor. Report unrounded adjusted p-values plus Monte Carlo intervals, and use substantially more draws for claims resting on .097 versus .100. A time-block/common-shock sensitivity would clarify the reach of period claims; 16 years are too few to promise robust asymptotics from two-way clustering without examination.

**Acceptance test.** Re-run the prespecified estimator with identical sample/draw eligibility, missing-draw treatment and full max-t joint null centering documented; retain primary results only when tail/support and resampling sensitivity are reported. Record both conditional-on-years and any broader claims separately. Current .054-.208 type sensitivity should remain visible; do not turn it into universal significance or universal insignificance.

## Minor or narrowly scoped repairs

* **Unreconciled two-row sample flow.** Main p38 and Table 2 p41 give E1=1,788, flagged=466, adjusted retained=58, rejected affected=408, E2=1,378. The displayed arithmetic gives 1,380. Supplement Table S8 p34 gives exclusion-only=1,320 rather than 1,788-466=1,322; imputation totals are 1,786. This pattern could reflect the same two additional complete-case/filter losses. Classify as an unresolved flow omission, not wrong observations. Add the two rows and reasons to a machine-readable flow table. Main sample 1,929-140 R1-1 R3=1,788 and period counts 465+418+458+447=1,788 do reconcile.
* **Failure to reject is not no change.** Table 2 note p41 explicitly calls an interval including zero a "no change" claim for T(0), T(20) and the upper-bound anchor surplus. Those are compatibility/failure-to-reject statements, not equivalence tests. Main pp43,46-48 mostly uses appropriate uncertainty language. Change the table note to "interval includes zero; no directional conclusion" or prespecify an equivalence margin and test it.
* **E2 naming and generalization.** Main p38 openly admits that 87.6% of acquisition-affected years are dropped and 58 adjusted years pair organic growth with consolidated margin. Supplement p29 openly admits current SIC, a latest-filed historical revenue universe screen, partial business/captive/listed-equity checks and nominal thresholds. These are real scope restrictions, not newly discovered errors. Call E2 a partial acquisition-adjusted selected sample, and do not equate it with a clean organic technology frontier. Current SIC coverage of inactive firms does not by itself establish coverage of every historical software firm. No particular observation is demonstrated wrong here.
* **Projection language.** §5.3 p44 explains why the local quantile is steeper in the sample, but pooling faster growers does not mathematically guarantee that ordering in every population. Present it as the observed ordering; do not attach a universal estimator comparison.

## Defenses accepted: candidate objections not sustained

1. **Wrong cone orientation:** withdrawn. The cited input/output estimators use different economic labels, but the paper explicitly adapts them to two desirable outcomes. On the empirical domain one can take cost `x=1-m` and output `y=g>=0`; conditioning y>=g and minimizing x corresponds to maximizing m among faster growers. This establishes a mathematical transformation; it does not transform fixed partial quantiles into technology or import iid sampling assumptions automatically.
2. **Quantile frontier must be monotone:** withdrawn as a general objection. Main Proposition 3(ii) explicitly constructs increasing partial quantiles while the possibility envelope decreases. Aragon et al. also require an extra stochastic-order assumption to guarantee fixed-quantile monotonicity. The observed chosen-point partial quantile is not obligated to be a full Pareto boundary.
3. **Cash score decline universally significant:** not alleged; pp42-43 explicitly report that it fails familywise correction under every procedure even at 10%, and the abstract agrees. GAAP is significant at 10% under most procedures, not all. Significance is method sensitive.
4. **Capital intensity provides structural evidence:** not alleged; pp45-46 explicitly call the gap an accounting effect and show add-back sensitivity.
5. **Growth weight empirically estimated at 7-13:** not alleged for this version; §5.4 p45 expressly withdraws it and reports measurement sensitivity from .05 to10.1 for the spend ratio interpretation.
6. **E1/E2 differences prove acquisitions cause flattening:** not alleged; §5.9 p47 withdraws such interpretation, reports imputation-selection sensitivity and paired multiplicity correction.
7. **Current main P95 values subtract to exactly 11.9 using rounded levels:** not an error. 55.9 and43.9 can be compatible with a11.9 change using unrounded estimates.

## Claim audit matrix

| Claim | Location | Status | Evidence/limit |
|---|---|---|---|
| Possibility envelope nonincreasing, strict if supremum attained | Main P3(i) p24; S3 p17 | Checked by hand | Same common G ensures a firm feasible at g2 is feasible at g1; strict individual frontier and attained supremum give strictness. |
| Choice quality selection can flatten observed envelope and raise quantiles | Main P3(ii) p24; S3 p17 | Checked by hand | Monotone intercept/opportunity and condition23; not a claim actual firms satisfy it. |
| Same chosen locus is compatible with arbitrary admissible elasticity/weights | Main P3(iv) p24; S3 pp17-18 | Checked by hand | Constructed ell'(Delta), m0'(Delta), cap condition explicit; supports non-identification. |
| Small-shock within-firm covariance formula | P3(v), S3 p4; proof pp17-18 | Checked by hand | Bounded shocks permit uniform Taylor remainder; independence restrictions and positive denominator are stated. Not a causal interpretation of FE coefficient. |
| Common-frontier cone slope approximates technology as observations densify | Main p23; S2.3 p7 | Corrected | Exact q' density ratio/counterexample above. |
| Primary slope -.22 GAAP /-.16 cash | Main pp42-44, Table2 pp40-41; S5 p31 | Internally checked, not re-estimated | Correctly different from local quantile; cash interval includes0 in E1. |
| GAAP slope steepened by -.38 after2020 | Main p44; Table2 p40 | Internally consistent, conditional inference | E2 interval includes0; multiplicity10% support disclosed. |
| P95 fell11.9/12.7 points | Main pp42-43, Table2 p41, S9 p35 | Internally checked, not reproduced | Point signs robust; corrected significance differs by basis/type. |
| Scale tests saturation | Main p45 | Not asserted as identified | Explicitly weak/noisy, current size not share. |
| Lower cash scores prove capital mechanism | Main pp45-46 | Correctly limited | Add-back removes support; described as accounting. |
| SFA cohort shortfall identifies inefficiency | Main p46 | Correctly not asserted | Parametric distributional separation; survival caveat explicit. |
| Data determine transient fraction of top score | Main pp46-47 | Correctly not asserted | Seven-firm anchor and spend mapping; bounds overlapzero on upper spend basis. |
| "No change" from interval spanning0 | Table2 note p41 | Corrected wording required | Not equivalence. |
| Every empirical number regenerated from distributed extracts | S6 p43 | Untested | No author code/panel accessed. |

## Primary-source verification ledger

1. **Aragon, Daouia and Thomas-Agnan, 2005, Nonparametric Frontier Estimation: A Conditional Quantile-based Approach**, Econometric Theory21,358-389, DOI10.1017/S0266466605050206. Author version dated10Sept2003,26PDFpages: https://www.tse-fr.eu/sites/default/files/medias/doc/by/daouia/adt1202.pdf . **Relevant-section access**, §§1-3 and propositions2.4-2.5 read through parsed full PDF. Conditional output distribution uses X<=x; a fixed partial quantile is not the full boundary, and monotonicity needs stochastic order. Appropriate antecedent after explicit transformation; no proof of software-technology identification.
2. **Cazals, Florens and Simar,2002, Nonparametric Frontier Estimation: A Robust Approach**, Journal of Econometrics106,1-25, DOI10.1016/S0304-4076(01)00080-X. **Relevant-section access to2000 working-paper precursor**,13PDFpages: https://research.dial.uclouvain.be/bitstreams/2493fc61-fb6b-47d0-befd-8ec74da019ca/download ; journal metadata verified at https://research.dial.uclouvain.be/entities/publication/62fc3b55-9ee3-4990-9b5d-f2bd5dda21a4 . Precursor §§2-3 use expected minimum cost conditional on Y>=y, with iid sampling; finite order is a benchmark, not full frontier. Journal final text/proofs not inspected; do not overstate precursor access as final proof verification.
3. **Romano and Wolf,2005, Exact and Approximate Stepdown Methods for Multiple Hypothesis Testing**, JASA100,94-108, DOI10.1198/016214504000000539. **Relevant-section access**, full15-page PDF available, §4.2 and AssumptionB2/Theorem6 read: https://www.econ.uzh.ch/dam/jcr:ffffffff-935a-b0d6-ffff-ffffd823d949/jasa.pdf . Strong familywise control depends on valid joint resampling; this does not certify the paper's particular implementation or ex-post family choice. Full proofs not audited.
4. **Koenker and Bassett,1978, Regression Quantiles**, Econometrica46,33-50, DOI10.2307/1913643. **Relevant-section access**, §3 p38 and computational appendix available in19-page original article scan: https://www.maths.usyd.edu.au/u/jchan/GLM/Koenker%26Bassett1978QuantileReg.pdf . Definition is asymmetric absolute-residual optimization; LP formulation appropriate. This supports estimator definition, not frontier/causal interpretation; author primal-dual results not reproduced.
5. **Jondrow, Lovell, Materov and Schmidt,1982, On the Estimation of Technical Inefficiency in the Stochastic Frontier Production Function Model**, Journal of Econometrics19,233-238, DOI10.1016/0304-4076(82)90004-5. **Relevant-section access to author-uploaded original article text**, introduction/half-normal derivation: https://www.researchgate.net/publication/247037552_On_the_Estimation_of_Technical_Ineciency_in_Stochastic_Frontier_Production_Model . Conditional expectation of one-sided residual component is source-supported under its distribution assumptions. No measurement of managerial inefficiency or cohort causal effect follows without those assumptions.

The initial Toulouse repository PDFs timed out and a journal scan on CiteSeer returned403; alternative primary author/institution copies above were successfully inspected. No claim is made that every cited estimator proof has been rederived.

## Coverage, exposure and uncertainty

Read extracted main pp23-24,36-48,69-70; supplement pp4,7,17-18,28-35 and the reproducibility paragraph on43; relevant empirical reference entries. Inspected rendered images of main23,40-41 and supplement7,17,30-31; consequential claims/formulas checked against those images. Other roles cover the remaining paper. Main Table2 and S4-S10 were internally compared, but raw-data tables, confidence intervals and author code were not reproduced. No private accounts or unrelated folders inspected.

Unavoidable exposure: current §4-5 contains descriptions of prior reviewer concerns, withdrawn earlier claims and methodological revisions. A broad initial search also exposed brief protocol snippets. Reading the last S6 reproducibility paragraph on supplement43 also exposed the S7 opening and first agent-list rows on that same page, including the lead model label and descriptions of review roles. **No actual previous critique/report or other current agent report was read.** Therefore the first assessment is report-blinded but not wholly unaware of prior review history.

The narrow common-frontier mapping error is analytically established and independently checked. Most empirical limitations are already disclosed; absent the extract/code, I cannot determine the numerical magnitude of extraction/selection/common-shock problems, and do not infer a specific observation is incorrect. Preserve this first report before any cross-specialist exchange or adversarial review.
