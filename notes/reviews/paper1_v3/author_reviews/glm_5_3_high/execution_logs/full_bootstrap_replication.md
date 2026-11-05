# Execution log: full replication pipeline run (Lead-supervised)

## Background
- The author's `code/estimate_v3.py` (repo clone at commit 62e574b) was started by referee B's
  predecessor at 2026-11-03 05:14 UTC in a fresh copy of the repo
  (`/root/tmp/ruleof40/diagnostics/econometrics-empirics/repo_run/`), writing outputs locally
  (`nohup python3 code/estimate_v3.py > ../estimate_v3_run.log 2>&1`).
- Run completed at ~5258 s (~88 min) on 2026-11-03, regenerating all committed bootstrap-dependent
  outputs with B=999 firm-cluster bootstrap replications.
- Environment: Python 3.12.3 (main, Aug 31 2026), numpy 2.5.2, scipy 1.18.1, pandas 3.0.3,
  statsmodels 0.15.0, sympy 1.14.0, mpmath 1.3.0, matplotlib 3.11.1 (see
  diagnostics/econometrics-empirics/env.txt). Panel data hashes unchanged before/after runs
  (c44416b1… panel_v3.csv etc.), i.e., the pipeline did not mutate its inputs.

## Regenerated vs committed outputs (diff by Lead, 2026-11-03)
| File (repo notes/ or sections/tables/) | Result |
|---|---|
| calibration_anchor_v3.json | BYTE-IDENTICAL |
| paper_stats.json | BYTE-IDENTICAL |
| tab_estimands_v3.tex | BYTE-IDENTICAL |
| tab_yearly_v3.tex | BYTE-IDENTICAL |
| tab_bridge_v3.tex | BYTE-IDENTICAL |
| frontier_slope_v3.json | max numeric diff 8.3e-16 (machine epsilon; formatting-level differences only) |
| empirics_v3.json | max numeric diff 2.0e-3, at an SFA basic-interval p-value (/sfa_cash_balanced_jlms_2016_19/E1_minus_E2/p_basic); all non-SFA fields ≤ 1e-15 |
| bootstrap_draws_v3.npz | 65/65 arrays present; max numeric diff 9.4e-4, in the `sfa` array (all non-SFA arrays effectively identical) |
| inference_v3.md | differs only in SFA-related digits consistent with the above |

Interpretation: the full empirical pipeline — point estimates, 999-replication firm-cluster
bootstrap, familywise corrections, table generation — reproduces end-to-end in a fresh environment.
The only deviations are at the 1e-3 level on stochastic-frontier-analysis (SFA) maximum-likelihood
interval endpoints, consistent with MLE optimizer path-dependence (referee B2 independently found
the same 120 SFA point-estimate fields differing by ≤2.3e-8 in its smoke-override run). No headline
number in the paper is affected.

## Other supervised runs (see first-reports for details)
- Author's `code/calibrate_horizons.py` rerun by referee D: reproduces every §7.3 number (pace
  7.18/19.93/40.66% by 2028/31/36, payback 7.526/8.507, NPV 0.98, PV ratio 3.868, cum3/5 −8.8/−8.6).
  D restored the committed notes/calibration_results.json afterwards (workspace hygiene).
- Author's `code/verify_part2_acquirer.py`: 82/82 checks pass (referee C).
- Author's `code/verify_theory.py`: read and cataloged by referee A2 (26 sections; section 15 = the
  Prop 2 numerical evidence); not fully rerun — superseded by the panel's own independent checks
  (76 inherited + 40+ new symbolic/numeric checks, plus Lead's 15).
- Panel's own scripts: /root/outputs/rule-of-40-review/diagnostics/ (all seeded; seeds recorded
  in scripts; base seed 20261103).

## Note on workspace hygiene
All author-code reruns were performed inside copies under diagnostics/econometrics-empirics/
(repo_run, repo_build) or with restoration of committed files afterwards (D). The frozen source
PDFs under "/root/Paper Review/sources/" were never modified (hashes re-verified below at
packaging time).