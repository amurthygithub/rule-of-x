# Post-freeze targeted cross-check A

This note follows the coordinator's explicit challenge of A's first report. It does not modify the frozen report or first diagnostics. No other specialist report was read.

## Physical share cap: use sbar=.5, not literal 1

The first script solves a dimensionless state z in (0,1) but its parameter record labels `sbar=1`. Taken literally that fails Assumption1's strict `sbar in (0,1)`. This metadata/description must be corrected before using A's example as an all-assumptions counterexample.

Set physical `sbar=.5`, `s=.5*z`, and `v_physical(s)=.5*w(z)`, where w is the normalized value function saved by the original script. Then `v_physical'(s)=w'(z)` and `v_physical(s)/s=w(z)/z`. Both the decision weight and revenue multiple are unchanged. The share law becomes `dz/dt=z*lambda*(1-z)*sigma^alpha`, and physical HJB divided by .5 is exactly the normalized HJB. Thus reported relative-share weight values and the full-profile reversal do not change; physical shares for relative shares .01,.1,.5 are .005,.05,.25. The dimensionless local-asymptotic example uses alpha=.5,lambda=.2,r=.1,G=0,m0=.1,k=0,physical sbar=.5. Its root v0=1.12701665379, exponent a=3.43649167310, and forced coefficient -.46255715389 are unchanged in the expansion in z=s/sbar. In physical s the linear coefficient is -.92511430778. All stated Assumptions1-4 now hold literally.

`A_crosscheck.py` executes the rescaling from the saved arrays, checks physical derivatives, and records the scaled HJB residual in `A_crosscheck_results.json`. The numerical residual scales by .5 as it must; any floating-point derivative discrepancy is recorded. No new HJB solve is claimed.

## 'Rule of 1000 is not a steady state': conditional economic statement

Exact locators: main p5 introductory summary; main p58 Section7.2, sentence 'Second, a Rule of1000 is not a steady state'; conclusion main p70; supplement SectionS5 p27. The mathematical budget bounds score **above** `R_infty=m0+(X-k)G`, and Corollary1 explicitly assumes target `barR>R_infty`. Assumptions1-4 impose no upper bound on G. Consequently a universal exclusion of a long-run 1000-point score does not follow.

An all-Assumptions1-4 example is physical sbar=.5,s0=.1,G=9.5,alpha=.3,lambda=.6,k=0,m0=.5,X=1 (set human cost .5, other costs and a=amin=0). With any positive financing cap, the admissible zero-spend policy sigma=0 has g=G=9.5,m=.5,share=.1 and score R1=10 at all dates. If static score maximization is required, its surplus is positive at finite shares and vanishes as share tends to the cap, so its long-run score tends to10. The score-budget inequality holds: it bounds only the transient excess above10. Add r=10 if a discount rate satisfying r>G is wanted; no dynamic optimality claim is needed.

Strongest author defense: G=950% continuously compounded per year is far outside every economically credible scenario in the paper, and the surrounding passage expressly uses 20% market growth and calibrated demand pull. Its shorthand is economically reasonable and does not misstate the actual Proposition1 or Corollary1. This is therefore a scope/qualification correction, not an additional major mathematical defect. Smallest repair: 'At the market growth rates considered, a score of1000 lies above the saturated level and cannot persist within one market.' Acceptance test: retain explicit `barR>R_infty`; all target-score duration statements should condition on it. The plausible-case numerical conclusions are unchanged.
