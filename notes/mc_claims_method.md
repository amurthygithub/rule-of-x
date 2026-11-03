# Joint-parameter stress test of Paper 1's headline claims: method

Script: `code/mc_claims.py`. Outputs: `<out>/mc_claims.json` and `<out>/mc_claims_report.md`, both written by the
script (default `<out>` = `notes/mc/`). A labelled small-N test run (n = 500) is in `notes/mc_smalln_test/`.

## 1. Question and framing

Paper 1 treats parameter uncertainty one parameter at a time: the tornado of Table 6 (`TORNADO_ITEMS` in
`code/calibrate_horizons.py`) and named bounds (the S&M basis, pass-through 0/0.5/0.7, slow/fast execution, the
compute-share range, the 1%/5% remote threshold). It never varies parameters jointly. This test asks whether each
headline claim survives joint variation over the ranges the paper itself states.

It is not a forecast. Most parameters are scenario values (class d) with ranges but no measured distribution, so:

- **Primary result (distribution-free).** For each claim: does its test hold at every point of the parameter box, the
  minimum and maximum of the tested quantity over the box, and, where it fails, the failure region in plain words.
- **Secondary result.** The share of draws in which the claim holds, always labelled "uniform over the stated ranges
  (an assumption, not a measured distribution)". The three anchor dimensions are estimates with a firm-cluster
  bootstrap; they follow that bootstrap distribution within its 90% interval, so a share that depends only on them
  (the lever count L1) is a bootstrap probability.

## 2. How the script uses the paper's code without touching it

1. `code/calibrate_horizons.py` is executed unchanged into a namespace whose `__file__` points at a scratch tree,
   `<out>/_shadow/` (its inputs are symlinked read-only; `sections/appendix_proofs.tex`, which the script rewrites, is
   copied). Every file the script writes lands in the shadow. The shadow's `notes/calibration_results.json`,
   `tab_calib.tex` and `tab_tornado.tex` are compared byte for byte with the committed ones; when library versions
   change the last digit of some floats, the report gives the number of differing leaves, the largest relative
   difference and the blocks. Under Python 3.13 with numpy 2.5 the outputs are byte-identical. Under Python 3.11 with
   numpy 2.2, 41 leaves differed by at most 1.4e-15 (relative): the frontier-slope mapping (`ell_psi`), and the last
   digit of the payback sums and iso-score values in `r2`, because numpy builds sum floats in different orders. Within
   one process the mirror is exact; against the committed JSON the checks use a relative tolerance of 1e-12, and the
   macros must match exactly.
2. The functions the claims use are mirrored line by line in `code/mc_claims.py` (`fullcost_v`, `pt_margin_v`,
   `rates_v`, `pace_v`, `central_path_v`, `payback_v`, `cc_path_v`, the lever ranking of
   `code/playbook/run_archetypes.py`, and the accountability-floor example of `code/paper1_macros.py`, whose constants
   are read from that file's source with `ast`, without executing it).
3. **Before any sampling** (`verify_mirror`, `reproduce_paper`), 87 checks run (82 before the compute-share fix of 3 Nov 2026):
   - each mirror equals the executed original, with exact float equality, on every ceiling case and horizon, every
     pace case (including the pre-commit cases and the BCG-win case), all 27 central-path cases of the tornado and
     the basis-by-pass-through grid, and the slow, central and fast paybacks plus the payback at r = 10%;
   - at the centre of the box, the 2036 central score, G* and the levers counts match
     `notes/calibration_results.json` within a relative 1e-12 and the macros exactly: `CenRSix` 59, `GstarCenOne`
     32.5, `lpNGEFirstNet` 1, `lpNGACutFirstNet` 5;
   - the same holds for every central-path level on all three bases, the targets, dips, realized and embedded shares,
     G* by horizon and with pass-through, every payback macro, the lever ratios, the companion paper's
     `ranking_by_basis` counts, the accountability floors and designs, `PullMultLo` and `PullMultHi`, and two tornado
     rows rebuilt from the box's own dimensions.

   If any check fails, the script stops without sampling.

## 3. The parameter box

Every range below is one the paper or its code states. Where the code models a range as discrete cases (slow,
central and fast execution; favorable, central and conservative full cost), the underlying continuous parameters
vary over the span of the cases. The compute share by horizon comes from its path drivers. Table: default mode,
`--cc-mode path`, 51 dimensions.

**Compute share at 2025 prices (round 3, 3 Nov 2026).** The text, the calibration (`CC['prices2025']`), params.yaml
and the box use one range for c_c = s_L x kappa: kappa from 0.02 (METR's cost per completed task: 1% of the human
cost per successful run at a 50% success rate) to 1 (the value test), times s_L. In path mode the box draws kappa_2025
log-uniform on [0.02, 1] (it spans a factor of 50; value = lo (hi/lo)^u, central 0.10 at the NaN coordinate) and s_L
uniform on [0.50, 0.65], so c_c at 2025 prices runs from 1.0 to 65% of revenue, which contains the scenario range of
1.2 to 60%. The run of 2 Nov 2026 (`notes/mc_results_2026-11-02/`) drew kappa uniform on [0.01, 0.35], so its c_c ran
from 0.5 to 23% only. Every design works in unit coordinates and maps them through `dim_value`; `dim_unit` inverts
the uniform and log-uniform laws (used to place phi = 0.5 and 0.7 in the reproduction checks). Five reproduction checks
were added (82 -> 87): the kappa box ends equal the calibration's, the macros `KappaLo`, `CcLo` and `CcHi` at the box
ends, and the law's inverse at the central value.

**Sobol intervals and seeds (round 3).** Sobol indices carry 95% intervals: for the factors, SALib `analyze`
(`conf_level=0.95`, 200 resamples; `S1_conf`/`ST_conf` half-widths and `S1_ci`/`ST_ci` intervals), or, without SALib,
a nonparametric bootstrap of the N base rows (200 resamples, 2.5th-97.5th percentiles); for the groups always the
bootstrap. `--seed` sets every random design; `--compare-to DIR` records a comparison with a run of another seed
(block `seed_comparison`: per test the holds-everywhere verdicts, margins and box extremes; quantities, levels and the
two sensitivity rankings). Each run also writes `draws_lhs.csv` (one row per LHS draw), which `code/mc_report_tex.py`
reads. Classes follow `notes/assumptions_register.md`: (a) sourced, (b) grounded by
precedent, (c) calibrated from our own data, (d) scenario value. "Law" is the sampling law used for the secondary
shares and the Sobol indices; the primary result does not depend on it.

| # | Dimension | Group | Low | Central | High | Law | Class | Source | Note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `f` Payment fees f | fees | 0.02 | 0.025 | 0.03 | uniform | d | code/calibrate_horizons.py:132 (FC; Appendix Table tab:fullcost); data/tasks/params.yaml:3435 | favorable end low |
| 2 | `tau` Cash tax rate tau | tax | 0.15 | 0.18 | 0.21 | uniform | b | code/calibrate_horizons.py:132 (FC; Appendix Table tab:fullcost); data/tasks/params.yaml:3288 | favorable end low |
| 3 | `a_min` Accountability floor a_min (band) | accountability | 0.005 | 0.03 | 0.046 | uniform | b | code/calibrate_horizons.py:389; data/tasks/params.yaml:3304; macros AminLo/AminHi | band of the text (Sec. 7.2) and params.yaml; the favorable case uses 0.015 |
| 4 | `L0` Control effectiveness L_sec | security | 1 | 2 | 4 | uniform | d | code/calibrate_horizons.py:136 (FC; Appendix Table tab:fullcost) | favorable end high |
| 5 | `Me` Exposure multiplier at full automation | security | 1 | 2 | 3 | uniform | d | code/calibrate_horizons.py:137 (FC; Appendix Table tab:fullcost) | favorable end low |
| 6 | `sec_it` Security share of IT spend | security | 0.086 | 0.109 | 0.119 | uniform | a | code/calibrate_horizons.py:140 (FC; Appendix Table tab:fullcost) | favorable end high |
| 7 | `phi_pqc` Post-quantum migration (share of IT spend a year) | security | 0.0075 | 0.015 | 0.03 | uniform | d | code/calibrate_horizons.py:141 (FC; Appendix Table tab:fullcost) | favorable end low |
| 8 | `aic_fixed` AI compliance fixed cost ($ a year) | security | 43k | 117k | 369k | uniform | d | code/calibrate_horizons.py:142 (FC; Appendix Table tab:fullcost) | favorable end low |
| 9 | `aic_pp` AI compliance per-process factor | security | 0.5 | 1 | 2 | uniform | d | code/calibrate_horizons.py:145 (FC; Appendix Table tab:fullcost) | favorable end low |
| 10 | `delta_M` Upkeep rate of builds delta_M | maintenance | 0.1 | 0.17 | 0.4 | uniform | b | code/calibrate_horizons.py:147 (FC; Appendix Table tab:fullcost) | favorable end low |
| 11 | `kappa_rv` Revalidation cost per build | maintenance | 0.05 | 0.1 | 0.2 | uniform | d | code/calibrate_horizons.py:148 (FC; Appendix Table tab:fullcost) | favorable end low |
| 12 | `T_up` Model-upgrade interval T_up (years) | maintenance | 0.99 | 1.22 | 1.75 | uniform | c | code/calibrate_horizons.py:149 (FC; Appendix Table tab:fullcost) | favorable end high |
| 13 | `B` Build stock per revenue | maintenance | 0.012 | 0.024 | 0.048 | uniform | d | code/calibrate_horizons.py:150 (FC; Appendix Table tab:fullcost) | favorable end low |
| 14 | `u_rev` Error rate with no review | ai_failure | 0.0495 | 0.0845 | 0.0845 | uniform | b | code/calibrate_horizons.py:160 (FC; Appendix Table tab:fullcost) | favorable end low |
| 15 | `ell_e` Loss per undetected error | ai_failure | 0.25 | 0.5 | 1 | uniform | d | code/calibrate_horizons.py:161 (FC; Appendix Table tab:fullcost) | favorable end low |
| 16 | `mu_m` Consequential misbehavior per task | ai_failure | 0.0005 | 0.001 | 0.002 | uniform | d | code/calibrate_horizons.py:162 (FC; Appendix Table tab:fullcost) | favorable end low |
| 17 | `d_m` Monitor recall | ai_failure | 0.42 | 0.6 | 0.95 | uniform | a | code/calibrate_horizons.py:163 (FC; Appendix Table tab:fullcost) | favorable end high |
| 18 | `p_tail` Pareto tail index of misbehavior losses | ai_failure | 1.15 | 1.5 | 2.3 | uniform | b | code/calibrate_horizons.py:165 (FC; Appendix Table tab:fullcost) | favorable end high |
| 19 | `nu_cm` Provider incidents a year (day-equivalents) | ai_failure | 0.5 | 2 | 6 | uniform | b | code/calibrate_horizons.py:166 (FC; Appendix Table tab:fullcost) | favorable end low |
| 20 | `s_fin` Management of AI spend (share of c_c) | ancillary | 0.015 | 0.03 | 0.06 | uniform | d | code/calibrate_horizons.py:169 (FC; Appendix Table tab:fullcost) | favorable end low |
| 21 | `anc_fixed` Incident-response and legal fixed cost ($ a year) | ancillary | 62k | 125k | 250k | uniform | d | code/calibrate_horizons.py:170 (FC; Appendix Table tab:fullcost) | favorable end low |
| 22 | `s_L` Labor cost automated, share of revenue s_L (also the error base W_A) | compute | 0.5 | 0.6 | 0.65 | uniform | c | code/calibrate_horizons.py:91; data/tasks/params.yaml:3375 | A_auto = s_L (code comment: same base as the compute share) |
| 23 | `kappa_2025` Compute per $ of labor replaced at 2025 prices | compute | 0.02 | 0.1 | 1 | log-uniform | b | code/calibrate_horizons.py `KAPPA_LO`-`KAPPA_HI`; data/tasks/params.yaml `kappa_2025_range` | per completed task to the value test (c_c = s_L x kappa); log-uniform, central 0.10. Until 3 Nov 2026 (run of 2 Nov): 0.01 to 0.35, uniform |
| 24 | `D` Fall of the fixed-performance price, x a year | compute | 3 | 5 | 10 | uniform | a | code/calibrate_horizons.py:92; data/tasks/params.yaml:3383 |  |
| 25 | `kappa_front` Compute per $ of labor at the frontier | compute | 0.1 | 0.33 | 0.5 | uniform | d | code/calibrate_horizons.py:92; data/tasks/params.yaml:3388 |  |
| 26 | `omega_2028` Share of automated labor in frontier tasks, 2028 | compute | 0.3 | 0.6 | 0.9 | uniform | d | data/tasks/params.yaml:3395 (2028) |  |
| 27 | `omega_2031` Share of automated labor in frontier tasks, 2031 | compute | 0.2 | 0.4 | 0.7 | uniform | d | data/tasks/params.yaml:3395 (2031) |  |
| 28 | `omega_2036` Share of automated labor in frontier tasks, 2036 | compute | 0.1 | 0.25 | 0.5 | uniform | d | data/tasks/params.yaml:3395 (2036) |  |
| 29 | `kappa_abs` Change capacity (share of the program a year) | execution | 0.05 | 0.1 | 0.22 | uniform | b | code/calibrate_horizons.py:255 (slow/fast span); data/tasks/params.yaml:1956 | fast end high |
| 30 | `varpi` Share of attempts that create value varpi | execution | 0.54 | 0.7 | 0.8 | uniform | b | code/calibrate_horizons.py:255 (slow/fast span); data/tasks/params.yaml:1095 | fast end high |
| 31 | `bbar` Share of targeted value realized bbar | execution | 0.37 | 0.67 | 0.85 | uniform | a | code/calibrate_horizons.py:255 (slow/fast span); data/tasks/params.yaml:1114 | fast end high |
| 32 | `nuR` Reorganization hazard nu_R | execution | 0.3 | 0.46 | 0.6 | uniform | b | code/calibrate_horizons.py:255 (slow/fast span); data/tasks/params.yaml:1392 | fast end low |
| 33 | `Tfrz` Reorganization freeze T_frz (years) | execution | 0.08 | 0.25 | 1 | uniform | b | code/calibrate_horizons.py:255 (slow/fast span); data/tasks/params.yaml:1405 | fast end low |
| 34 | `Tpar` Wave length / parallel run T_par (years) | execution | 0.08 | 0.17 | 0.42 | uniform | b | code/calibrate_horizons.py:255 (slow/fast span); data/tasks/params.yaml:825 | fast end low |
| 35 | `Temb` Embedding time T_emb (years) | execution | 1 | 1.25 | 2 | uniform | b | code/calibrate_horizons.py:255 (slow/fast span); data/tasks/params.yaml:1975 | fast end low |
| 36 | `Tpb` Transition cost in years of savings T_pb | execution | 1 | 1.25 | 2 | uniform | d | code/calibrate_horizons.py:255 (slow/fast span); data/tasks/params.yaml:1975 | fast end low |
| 37 | `Phi` Concurrent initiatives Phi | execution | 3 | 5 | 10 | uniform | d | code/calibrate_horizons.py:255 (slow/fast span); data/tasks/params.yaml:1217 | fast end high |
| 38 | `e` Decision units per initiative e | execution | 0.5 | 1 | 2 | uniform | d | code/calibrate_horizons.py:255 (slow/fast span); data/tasks/params.yaml:1226 | fast end low |
| 39 | `sec` Security reviews a year (reviewer-quarters x 4 x 2) | execution | 40 | 80 | 160 | uniform | d | code/calibrate_horizons.py:255 (slow/fast span); data/tasks/params.yaml:3139 | fast end high |
| 40 | `G` Market growth G | market_growth | 0.0544 | 0.1272 | 0.2143 | uniform | c | code/calibrate_horizons.py:676; macros GBandLo/GBandHi, CenG | central = anchor median growth |
| 41 | `phi` Pass-through rate phi | pass_through | 0 | 0 | 0.7 | uniform | b | code/calibrate_horizons.py:221; code/calibrate_horizons.py:692 |  |
| 42 | `k_pre` Capital per dollar of new revenue k | capital | 0 | 0 | 0.5 | uniform | d | code/calibrate_horizons.py:693 |  |
| 43 | `psi` Tax deductibility of capital psi | capital | 0 | 0 | 1 | uniform | a | code/calibrate_horizons.py:72 (Remark taxes) | enters only with k > 0 |
| 44 | `alpha` Spend elasticity alpha | surplus | 0.25 | 0.35 | 0.45 | uniform | d | code/calibrate_horizons.py:73; code/calibrate_horizons.py:629; data/tasks/params.yaml:3447 | enters only through a positive surplus (ub stratum) |
| 45 | `mu_2028` Demand pull relative to 2025, 2028 | surplus | 1 | 1.5 | 2 | uniform | d | code/calibrate_horizons.py:426 (2028); central = midpoint (CEN) | enters only through a positive surplus (ub stratum) |
| 46 | `mu_2031` Demand pull relative to 2025, 2031 | surplus | 0.75 | 1.12 | 1.5 | uniform | d | code/calibrate_horizons.py:426 (2031); central = midpoint (CEN) | enters only through a positive surplus (ub stratum) |
| 47 | `mu_2036` Demand pull relative to 2025, 2036 | surplus | 0.5 | 0.875 | 1.25 | uniform | d | code/calibrate_horizons.py:426 (2036); central = midpoint (CEN) | enters only through a positive surplus (ub stratum) |
| 48 | `Pi_ub` Median anchor surplus, all S&M buys growth | surplus | -0.1821 | -0.01279 | 0.1636 | bootstrap 5-95% | c | notes/calibration_anchor_v3.json bootstrap E1 Pi_ub_med; macros AncPiUbEoneLo/Hi | ub stratum only; floored at 0 as in central_path; drawn independently of the intercept (conservative) |
| 49 | `r` Discount rate (payback, NPV) | discount | 0.07 | 0.0934 | 0.1066 | uniform | b | code/calibrate_horizons.py:883; data/tasks/params.yaml:1514 |  |
| 50 | `m0A` Anchor intercept (median firm-year), net/ub/lb | anchor | 0.2413/0.3406/0.181 | 0.306/0.4198/0.2413 | 0.3474/0.5238/0.3166 | bootstrap 5-95% | c | code/calibrate_horizons.py:840 (999 firm-cluster draws in notes/bootstrap_draws_v3.npz); macros AnchorMzeroNetCiLo/Hi | bootstrap law within its 90% interval; central = point estimate |
| 51 | `b_M` Maintenance base of S&M b_M | maint_base | 0.2337 | 0.2506 | 0.2744 | bootstrap 5-95% | c | code/calibrate_horizons.py:879 (bootstrap of the anchor block) | enters the lever counts only |

**`--cc-mode bounds` (49 dimensions).** The compute-path drivers (rows 23 to 28) are replaced by the compute share
itself: `cc_2025` from 0.012 to 0.60 (the text's scenario range at 2025 prices, macros `CcLo`/`CcHi`, read from
`CC['prices2025']` of `code/calibrate_horizons.py`: s_L x kappa from the cost per completed task to the value test)
and `cc_2028`, `cc_2031`, `cc_2036` over the CC credible bounds (0.02-0.30, 0.01-0.25, 0.01-0.20;
`code/calibrate_horizons.py:111`, params.yaml `c_c_compute_share.by_horizon`). In this mode `s_L` enters only the error
base.

**Strata, not sampled.** The S&M basis: `net` (central: S&M above the maintenance base buys growth), `ub` (all of it does,
the upper bound) and `lb` (none does, the lower bound). Each draw is evaluated on all three strata. The anchor dimension
maps one unit coordinate to each stratum's own bootstrap quantile, so the same draw is the same quantile rank on every
basis.

**Couplings and choices, as in the code unless stated.**
- Compute-path rescaling. In path mode the drivers give c_c(h) through `cc_path`, rescaled by the paper's rounded
  central over the path's central value (0.12/0.119, 0.08/0.0794, 0.05/0.0497, 0.06/0.06). The code asserts that these
  agree within 0.005; the rescaling makes the centre reproduce the paper exactly.
- Error base. `A_auto` (the error base W_A) equals `s_L`, as the code comment at `FC['A_auto']` states.
- Tax rate in the anchor. The anchor inversion and the capital deduction use the code's fixed tau = 0.18, whatever the
  drawn tau, as the code does. The report states the omitted coupling: at tau = 0.15 or 0.21 the median netted
  intercept would move by 0.00 points, and the all-S&M intercept by +0.22 or -0.18.
- Median surplus `Pi_ub`. It is drawn independently of the intercept (a product box, wider than the joint bootstrap)
  and floored at 0, as in `central_path`. It enters only the ub stratum, so it cannot affect the central (netted)
  results.
- Maintenance base `b_M`. A separate dimension that enters the lever counts only. The netted intercept's bootstrap
  draws already carry their own b_M.
- Horizon-specific dimensions. omega and mu are drawn independently by horizon. The box therefore contains paths whose
  frontier share or demand pull rises over time, which the paper's own path does not (omega 0.6, 0.4, 0.25).
- `T_emb` and `T_pb` are separate dimensions over the same [1, 2]; the paper ties them at the centre and moves T_pb
  alone in a sensitivity.

**Not dimensions (and why).**
- `nuL`, `kkeep`, `nuV`: they enter only the disruption haircut, which the params commit switched off.
- Haircut on/off: a model choice, not a range.
- Sponsor latency `kap` = 0.78: a regime variant, not a range.
- `floor_share`, `s0`, `ell_m`, `Zcap`, `XY`: single-valued in the code.
- The tornado's "anchor sample" row (E1all, E2, M = 4, M = 8): alternative estimands, not a parameter range.
- The "dip" row: a different quantity, reported separately.
- The tornado's anchor-quartile row (a different firm type): available with `--anchor-range iqr`.
- The BCG-win row (varpi = 0.30, outside varpi's stated range of 0.54-0.80): available with `--bcg-win`.
- The S&M attribution row: the strata.

## 4. Claims and the tests encoded

The claims were collected from the abstract, Section 1, Sections 7 and 8, the conclusion and the summary box: every
headline claim that depends on calibrated parameters. The empirical estimates have their own bootstrap and are not
re-tested. Each test is a margin m(x) that is positive (or non-negative for >= tests) exactly when the claim's text
holds.

Variants hold a claim's own named conditions at their central values, separating "fails because a stated condition is
relaxed" from "fails within its stated conditions":
- `full`: the whole box.
- `A`: fixed prices (phi = 0) and k = 0, the central path's stated conditions.
- `B`: central execution, fixed prices and k = 0, the condition of the payback statements.
- `C`: compute at 6% of revenue at 2025 prices, the condition of the headline G*.

Payback tests have a domain: the target lies above the anchor intercept at every horizon, so that the program raises
the margin. Outside the domain the payback quantities are meaningless; such points are counted and reported, not
treated as failures.

| Test | Text (where) | Quantity | Test | Variants | Strata |
|---|---|---|---|---|---|
| C1.cond / C1.full | "complete automation keeps a mature asset-light firm's cash score below 100 unless its market grows faster than 32.5% ... 72 to 97 points for market growth of 5 to 30%" (abstract, Sec. 1, Sec. 7.2, summary 5, conclusion) | G* = 1 - base, 2025 prices | G* > 30%, i.e. the ceiling stays below 100 up to 30% growth | C (c_c = 6%), full | none |
| C1.fav | same | G* | G* >= 22.3%, the favorable case and the lowest threshold the paper states | full | none |
| C1.iqr | "a market growing at a rate few markets sustain" (conclusion) | G* | G* > 21.4%, the upper quartile of 2023-25 growth | full | none |
| C2 | "38, 34 and 32% in 2028, 2031 and 2036" (Sec. 1, 7.2) | min over horizons of G* | > 30% | full | none |
| C3 | "pass-through raises every threshold" (abstract, 7.2, conclusion) | min over 2025 prices and horizons of G*(phi) - G*(0), at the stratum anchor's saving | >= 0 | full | net/ub/lb |
| P1 | "No single input in the table lifts the 2036 central score to 100"; path 46, 50, 59 (Sec. 7.3) | max(R_2028, R_2031, R_2036) | < 100 | full, A | net/ub/lb |
| P2a | "Even a completed program would bring the durable score only to the target plus market growth" (7.3) | target(2036) - m0(2036) | >= 0 | full | net/ub/lb |
| P2b | same, "about 68 plus 12.7 points" | target(2036) + (1-k) G | < 100 | full, A | net/ub/lb |
| P3 | "the central firm has realized less than half of its program by 2036" (7.3; abstract 41%) | bbar E(2036) | < 0.5 (execution dimensions only; fixed at 0.41 under central execution) | full | none |
| P3b | "the program ... completes in 2042" (7.3) | expected completion year | > 2036 (execution only) | full | none |
| P4 | "the intercept rises from 31 to 33, 38 and 46" (7.3) | min(R_2031 - R_2028, R_2036 - R_2031) | >= 0 | full, A | net/ub/lb |
| P5 | "pass-through lowers only the target" (7.3) | min over horizons of R(phi = 0) - R(phi) | >= 0 | full | net/ub/lb |
| P6 | "59 [54, 62] (55 to 65 as none or all selling spend buys growth)" (abstract) | min over horizons of min(R_net - R_lb, R_ub - R_net) | >= 0 | full, A | across strata |
| B1 | "Annual gains first exceed the costs of transitions in flight after about 4.0 years ... That flow crossing is not payback" (7.3) | payback - flow crossing | > 0 | full, B | net/ub/lb |
| B2 | "repays those costs only after 7.5 years ... an owner with a horizon of five years or less would not fund the whole program under central execution" (1, 7.3, 8.2, conclusion) | undiscounted payback | > 5 years | full, A, B | net/ub/lb |
| B3 | "at three and at five years its cumulative effect is still negative" (1, 7.3, summary 6) | max(cum3, cum5, NPV3, NPV5) | < 0 | full, B | net/ub/lb |
| B4 | "gains are worth 3.9 times the dip in present value" (7.3) | PV(gains) / PV(dip) | > 1 | full, B | net/ub/lb |
| R1 | "A Rule of 1000 ... requires 9 to 20 times the demand pull of today's best public software firms" (1, 7.2) | `rule1000_multiple['ub']` | > 1 (varies with alpha only) | full | none |
| L1 | "cutting G&A outranks automating the growth engine at 5 of 6 positions"; all S&M: growth engine 6 of 6; none: 0 (7.4, Table 7 from `code/playbook/run_archetypes.py` `paper1_positions`, `levers_position_macros.tex`) | count of positions with sigma > a_GA | equals 1 / 6 / 0 on net / ub / lb | full | net/ub/lb |
| L2 | "ranks engineering above both at all 6 positions on the central basis" (7.4, summary 7, conclusion) | count with R&D > max(sigma, a_GA) | = 6 | full | net |
| L3 | engineering first of the four levers at 6 of 6 (`ranking_by_basis`, cost of revenue at the drawn phi) | count with R&D first | = 6 | full | net |
| S1 | "execution, not market growth, moves the 2036 score most" (summary 6, Sec. 1) | group swing (others central) and Sobol group ST of R_2036 (net) | execution > market growth, and execution the largest group | n/a | net |
| S2 | "[the compute share] is the dominant uncertainty" (7.2) | group swing and Sobol group ST of G* | compute the largest group | n/a | none |
| A1-A5 | accountability floor (Sec. 7.2, 8.5, summary 9): no all-AI design passes; all-human passes only at 5%; cheapest designs 1H+1AI (5%) and 1H+2AI (1%); floor 0.37-0.38% (0.26-0.76% over audit fees); floor below the a_min band's 0.5% (informational) | see report | see report | own sub-box | eps 1%, 5% |

The lever counts depend only on b_M (and, for L3, on phi). They are analysed exactly on a 401 x 71 grid. The lead at the
revealed weight does not depend on alpha: the growth engine leads iff sigma > a_GA.

**Accountability-floor sub-box.** The example of Remark rem:amin-values has its own parameters and depends on no
parameter of `calibrate_horizons.py`. Its five dimensions are the ranges the paper tabulates:
- audit fee: $343k to $5.33m (central $1.49m);
- p_cc: 0 to 0.0025 (the grid of Table tab:amin-pcc);
- human miss rate on AI-missed items: 0.05 to 0.5 (same table);
- p_ca: 0.005 to 0.01;
- opportunities a year: 24 to 48.

All 2^5 corners are evaluated, plus 2,000 LHS draws, at each threshold. Table tab:amin-pcc already reports the
break-evens beyond which no design is admissible, so failures driven by p_cc or the miss rate restate that table
jointly.

## 5. Design

- **Latin hypercube:** `--n` draws (default 10,000) over the 51 unit coordinates, seed 20261102. Each draw is
  evaluated on all strata and variants. The combined band also uses a replicate index into the 999 bootstrap draws.
- **Corners:** k = 51 > 14, so not all 2^k corners. The stated subset is:
  - the all-low and all-high vertices;
  - 2,048 random vertices (seed 20261103);
  - for every tested quantity, both extremes found by a vertex search. The search goes as follows:
    1. one-at-a-time ends at the centre give each free dimension's direction;
    2. start from that directional vertex and from the two most extreme sampled points;
    3. flip single coordinates while that improves the quantity;
    4. try the interior values (central, 1/4, 1/2, 3/4) of each coordinate;
    5. repeat the flips.

  The budget is 600 evaluations per search, and the search respects the claim's domain. Because most quantities are
  monotone in most dimensions, the directional vertex is usually the exact extreme. The search is not a proof.
- **Holds everywhere:** the minimum of the margin over all LHS draws, corners and search points is positive (>= -1e-12
  for non-strict tests).
- **Failure region:** for a test that fails, the report gives four things:
  1. the share of draws failing (labelled);
  2. a depth-2 classification tree (Gini) on the dimensions the margin depends on (a one-at-a-time effect, or a rank
     correlation with the margin above 3/sqrt(n));
  3. univariate scans on 21 points along the top three dimensions, with every other dimension first at its central
     value and then at the least favorable point found, giving the interval of the dimension on which the claim fails;
  4. the least favorable point, described by its five most influential dimensions.
- **Sobol:** a Saltelli design on a scrambled Sobol sequence (`scipy.stats.qmc`; plain pseudo-random if scipy is
  missing). N = `--sobol-n` (default 1024) for A and B, AB_j for every factor and AB_g for every group, plus the coarse
  group `fullcost_target` (all full-cost and compute dimensions, matching the tornado's target row). The estimators are
  Saltelli (2010) first-order and Jansen (1999) total, with 200 bootstrap resamples for 95% intervals. If SALib is
  installed, `--sobol-backend auto` uses it for the factor indices (its own sample of N(k+2) rows); group indices always
  come from the numpy estimators. Outputs are R_2028, R_2031 and R_2036 (netted) and G* (2025 prices). The report sets
  the group indices and the distribution-free group swings beside Table 6's ranking.
- **Combined band (labelled conditional):** for each LHS draw, the central path is re-evaluated with the anchor
  intercept taken from a random one of all 999 bootstrap draws (not truncated) and every other dimension from the
  draw. The 5-95% band is shown beside the paper's anchor-only 90% interval (`r2.anchor_interval.*.ci90_joint`).

## 6. Parallelism, checkpoints, memory

- **Pool:** a `multiprocessing` pool with the spawn start method, guarded by `if __name__ == "__main__":`, using
  top-level task functions (no lambdas). `--workers` defaults to `os.cpu_count()`. The draws, corners, searches,
  failure scans and Sobol rows all run in the pool.
- **Threads:** `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS` and
  `NUMEXPR_NUM_THREADS` are set to 1 at the top of the module, before numpy is imported. Spawned workers re-import the
  module, so every worker is pinned. The model does no linear algebra.
- **Initialization:** the main process executes the calibration once and passes a small plain-data snapshot to each
  worker's pool initializer. Workers never read the panel or import pandas.
- **Checkpoints:** results go to `<out>/ckpt/<hash>/` after every chunk of `--chunk` draws (default 200; written
  atomically), after every 10 searches, and after every Sobol block. Timing and memory are kept in `timing.json`. The
  hash covers the options, the box, the calibration snapshot and the source of every function that changes results,
  so a resumed run never mixes outputs of different code or inputs. Rerunning the same command resumes; `--fresh`
  discards the checkpoint. An interrupted run (SIGTERM during the draws) resumed correctly in testing, with no orphaned
  workers.
- **Memory (container, x86_64):** the main process peaks at about 190 MB (pandas and the calibration load) and each
  worker at about 50 MB. With 4 workers that is about 400 MB in all, far under the 2 GB budget of a 4-core, 3-4 GB
  machine.

## 7. Runtime (measured in the container: 2 cores, x86_64, Python 3.13)

| Workers | Draws / s | s per 1,000 draws |
|---|---|---|
| 1 | 46 | 21.6 |
| 2 | 83 | 12.0 |
| 4 (on 2 cores: oversubscribed) | 81 | 12.4 |

Per draw the cost is about 22 ms of one core. Nine paybacks (three strata x full, A and B) account for about 21 ms of
it, because each uses the code's 73,000-point daily grid. The central path and ceiling take 0.16 ms. The n = 500 test
took 69 s of wall time on 2 cores:
- calibration load: 5 s;
- 2,550 draws: 28 s;
- 142 searches: 26 s;
- Sobol: 72k evaluations, 4 s;
- analysis and scans: the rest.

On the 4-core aarch64 target, assume a per-core speed 0.5-1x the container's. The full run then takes about 1.5-3 min
for 12,050 draws, about 1 min for searches and under 1 min for the rest: 3-6 min in all.

**Vectorization.** The central-path and ceiling code (0.16 ms per draw) is easy to vectorize across draws in numpy, but
it is under 1% of the cost. The payback is already vectorized over its 73,000-point time grid, so vectorizing across
draws would mostly add memory (about 0.6 MB per draw per array) for little gain, perhaps 1.2-1.5x. A larger speed-up,
about 5-10x, would come from an exact closed form for the payback (piecewise-constant waves and piecewise-linear
targets) in place of the daily grid. That would change floating-point summation order, so the payback would no longer
match the paper's to the last bit. It is not needed at this size. No GPU path.

## 8. Run commands

```
# full analysis (default box: path-mode compute share, bootstrap anchor, varpi 0.54-0.80), results in notes/mc/
python3 code/mc_claims.py --n 10000 --workers 4 --out notes/mc

# options
python3 code/mc_claims.py --verify-only                 # the 82 reproduction checks only (about 10 s)
python3 code/mc_claims.py --print-dims                  # the dimension table
python3 code/mc_claims.py --n 10000 --workers 4 --cc-mode bounds --out notes/mc_ccbounds   # compute share on its stated bounds
python3 code/mc_claims.py --n 10000 --workers 4 --bcg-win --out notes/mc_bcgwin           # varpi down to 0.30
python3 code/mc_claims.py --n 10000 --workers 4 --anchor-range iqr --out notes/mc_iqr      # anchor quartiles
python3 code/mc_claims.py --n 400 --corners 40 --workers W --stop-after draws --out /tmp/mc_bench_W   # throughput
```

Requirements: Python 3.10-3.13 with numpy, pandas and PyYAML (as for `calibrate_horizons.py`); scipy is optional (Sobol
sequence); SALib is optional (factor indices). Tested on Python 3.13 (numpy 2.5, pandas 3.0, scipy 1.18) and on
Python 3.11 (numpy 2.2, pandas 2.2, scipy 1.14). The syntax was checked against the 3.10 grammar (`ast` with
`feature_version=(3, 10)`). The SALib 1.6 backend was tested from the wheel in `notes/`.

## 9. Small-N test (n = 500), for orientation only

Full outputs: `notes/mc_smalln_test/mc_claims_report.md` and `mc_claims.json`. These are small-N numbers; the full run
supersedes them. Holds everywhere (yes/no) uses the LHS draws, the 2,050 corners and the searches, so the primary
verdicts are less sensitive to n than the shares are.

- **Hold everywhere:**
  - P1 (no Rule of 100 on the path) on the netted and none-buys-growth bases; the netted 2036 score ranges 27-95.
  - P2a (m0 below the target) on net and lb.
  - P5 and C3 (pass-through lowers scores and raises thresholds) on net and lb.
  - P6 (basis ordering).
  - B1 (crossing before payback).
  - R1.
  - L2 and L3 (engineering above both, and first).
  - S1 and S2, by group swing and by Sobol.
  - A1 (no all-AI design passes).
- **Fail somewhere, and where:**
  - C1: G* ranges 19-59% over the box (24-45% with compute held at 6%), against 30%. It fails when tau, a_min and the
    full-cost floors are at their favorable ends; with the compute share free, mainly when kappa_2025 < about 0.065.
  - P2b: a completed program plus market growth reaches 102 when G is at 21.4% and the 2036 target is favorable.
  - P3 and P3b: they depend on execution only and fail under fast execution (kappa_abs > about 0.13-0.17).
  - P4: the path can dip by up to 5 points between horizons when the frontier share rises over time (independent
    omega).
  - The ub basis claims (P1, P4, P2a, C3, P5): the surplus `Pi_ub` at the top of its interval combined with high
    demand pull, or an all-S&M intercept above the full-cost target.
  - B2 and B3 under central execution fail narrowly: payback as short as 4.8 years and a 5-year cumulative of +0.1
    point-years, both on compute paths that start high in 2028 and fall steeply.
  - B4 (PV ratio > 1) fails only under slow-end execution, consistent with the paper's own slow case.
  - L1: the count of 1 holds only for b_M in [0.2384, 0.2605), against its 90% interval [0.2337, 0.2744]; the share
    of all bootstrap draws inside that interval is 0.63.
  - A2-A5: these restate the p_cc and human-miss break-evens of Table tab:amin-pcc.
- **Levels:**
  - netted 2036 path: 5-95% of draws 40-66 (uniform over the stated ranges, an assumption, not a measured
    distribution); combined band 40-67; paper's anchor-only interval 54-62.
- **Sensitivity:** Sobol total indices for R_2036 (netted) are execution 0.61, market growth 0.21 and anchor 0.10. For
  G*, compute is 0.88.

## 10. Limitations

- Holds-everywhere is established by dense sampling and a directed vertex search, not by proof. Non-monotone
  interactions could hide a violation in the interior; the interior coordinate pass and the 12,050 sampled points limit
  that risk.
- The box is a product of the stated ranges. Combinations the paper would consider inconsistent are inside it, for
  example a rising frontier share, or a high median surplus together with a high intercept.
- Shares and Sobol indices depend on the sampling law. Uniform is an assumption for every class d parameter.
- The script re-tests the calibrated claims, not the empirical estimates.
