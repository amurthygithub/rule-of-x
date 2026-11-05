# Revision sequence, claim-level corrections, and acceptance evidence

Ordered by leverage. Each item gives: change, claims affected, evidence required to accept.

1. **HJB existence/verification (highest leverage for the theory claim).**
   Change: either prove (H) for an open parameter set (viscosity solution of the singular ODE through sbar, plus feedback admissibility), or add to the text a precise statement of what the numerical solution does and does not establish, including that the ODE's singular point at (0,v0) has dPhi/du>1 so the small-share limit does not select a solution.
   Claims affected: Prop 2(b)-(c), the "weight = marginal q" reading in Sec 3.7/exec summary/discussion.
   Acceptance: two independent solvers agree on v(s) to a stated tolerance, plus a verification theorem; or a counterexample parameter set where (H) fails and the claimed weight interpretation breaks — either would be a publishable result.

2. **Compute share grounding.** Change: keep c_c as scenario (no measurement exists), but add to the abstract/figcaption of tab:ceiling the sentence "no source measures a firm-level full-automation compute share; the threshold range over the credible bound is 28-78%" — currently only in the body.
   Claims affected: all ceiling/horizon thresholds (G* = 32.5% central etc.).
   Acceptance: a measured firm-level inference-cost share at high automation, or an agreed expert bracket; until then the conditional labeling (already present) is the correct form.

3. **Anchor flag column documentation.** Change: one clause in appendix_data and the estimands-table note: "the acquisition flag after rules R1-R5 (column acq_flag_v3 in panel_v3.csv)".
   Claims affected: anchor table (13 firm-years) and any re-use.
   Acceptance: a fresh clone reproduces notes/calibration_anchor_v3.json byte-identically (README claims this; I verified the rule reproduces the printed anchor exactly from the shipped panel).

4. **R2/R3/R5 coverage sentence in the main data section.** Change: one sentence with the counts (16 named firms classified; captive filer caught only via text; 26 firm-years flagged R5 of which...).
   Claims affected: the phrase "the sample is prepackaged software".
   Acceptance: EDGAR business-description classification for all 661 registrants, re-run of the five headline statistics, printed in tab_robust.

5. **Abstract scenario tag on the 2036 path.** Change: append "(scenario path, conditional on the stated compute share and execution inputs)" to the path sentence.
   Claims affected: none beyond clarity.

6. **Regulatory/tax primary-source pass.** Change: human specialist verification of 26 USC 174A/168(k) as amended by P.L. 119-21, IRS Notice 2026-11, PCAOB AS 2201 A7/FAS 5 note, Item 308(a)(3), SR 26-2 / OCC Bulletin 2026-13, Reg (EU) 2026/1744 dates (operative articles, not just recitals — the authors already note only recitals 40/46 were reached).
   Claims affected: remark rem:taxes (psi values), prop:amin's legal framing, levers item 5, supp:model-filings non-GAAP/KPI rules.
   Acceptance: signed verification memo with URLs and access dates, filed with the replication package.

7. **Full-pipeline byte reproduction.** Change: none to the paper; record in the replication README the exact commit and environment that reproduce the committed notes/*.json (README claims byte-for-byte modulo timestamps).
   Acceptance: an independent party runs code/regenerate_all.sh (~1h) and diffs; I verified the quick checks (verify_theory 191/191, verify_part2_acquirer 82/82, paper1_macros idempotent) but not the 35-minute estimation run.

8. **Disclosed post-hoc choices** (estimand policy D-3, frontier object D-2, threshold move 1%->5%->both, netted S&M basis) are already listed with times in Appendix A; keep them there. No change. If the outlet requires pre-registration-style discipline, convert the appendix table into a supplementary CSV.
