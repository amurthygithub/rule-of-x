# Code-evidence addendum: controls and compute-cost units

This is new evidence obtained after Part B was frozen. It does not modify the independent Part B assessment. Inspection was read-only against the exact pinned snapshot at commit `eb7537bee7585f2902304f62a722edea6ced8539`, supplied by root at `pinned_snapshot/`. No full author jobs were run by this reviewer. No `notes/reviews/` files, other-review responses or joint response were opened. Selected source hashes and deterministic normalized calculations are in `results/controls_code_units.json`.

## 1. CS-1 ownership calibration is confirmed; no retraction

The source agrees with the PDF, including the problematic conversion:

- `sections/appendix_proofs.tex:86–87` defines at-cost annual TCO, server share and life, sets `k_c=s_srv L_srv TCO`, treats the remaining share as running cost, cites Epoch for60%, then inserts5.5-year life and the3.3 coefficient.
- `code/verify_theory.py:1755–1768` checks the own-minus-buy algebra. In particular, line1763 **defines** `kc = ssrv * L * TCO`; line1764 then charges `kc/L` as annual replacement. This is a check conditional on that definition, not independent evidence that Epoch's annualized server share is a replacement-cash share.
- `code/verify_theory.py:1769–1777` hardcodes3.3,16.5%/49.5% and33%/74%; lines1778–1780 check agreement with printed macros.
- `code/paper1_macros.py:211–214` likewise hardcodes3.3 and the tax sensitivity.

Thus code/PDF numerical agreement does not repair the external-source unit mismatch. The conditional algebra can pass while the empirical conversion is wrong. Epoch's CRF includes WACC; an annualized server cost `A=CRF*K` implies `K=A/CRF`, not `K=L*A`. The paper effectively needs `CRF=1/L`, which the cited source does not assume. Its source IT life is5years, and the displayed0.24CRF differs from1/5 and1/5.5. See original CS-1 and the source's numerical tables. Numerical replacement of just3.3 without rebuilding the cash/economic denominator remains inappropriate.

The same source construction appears in a companion-engine parameter:

- `data/tasks/params.yaml:670–680`: capital per annual compute dollar, central3.0,range2–4; source text says derived from60%of annualized data-center TCO times5–6-year server life, though flagged assumed/classd.
- `engine/src/autofrontier/defaults.yaml:487–491`: owned-share0, capital factor3, owned running cost0.3 of rental price, economic replacement rate0.25 (line485), book life5.5.

This propagation does not make the parameter a measured estimate; its classd label helps. Its stated source derivation should still be corrected.

## 2. CS-2 failed-attempt adjustment is confirmed; no retraction

Code does not calculate failure-inclusive cost for the low bound:

- `code/data_part2/08_params.py:136–140` filters the TH1.1 frontier set to successful runs for token-per-human-hour calculations.
- Lines149–161 read TH1.0 cost data and keep only `generation_cost>0` and `score_binarized==1` (line152), then report median successful-run cost shares by agent.
- `code/calibrate_horizons.py:98–108` explicitly bases the low bound on successful-run cost0.01 and a **fixed** success rate0.50 from the time-horizon definition, then divides them. Lines1312–1323 repeat the calculation and store it as `compute_credible`.
- `code/data_part2/08_params.py:1634–1638` duplicates the fixed0.01/0.50 construction; lines1706–1715 describe the bounds and successful-run source.
- `code/paper1_macros.py:1691–1695` gates the multiplication by labor share and the successful-cost/success-rate identity. It does not gate an all-attempt cost estimator.

Correct units are confirmed: `c_c = s_L*kappa`, so0.60*0.02=0.012. The remaining missing assumption is about `c_failure` and the task/model mix. For independent repetitions with success probabilityp, mean total cost per completed task is `c_success + (1-p)/p*c_failure`. Dividing conditional-success mean cost byp is equivalent only if failure and success costs have the same mean. An empirical50%-horizon definition also does not supply the meanp for the successful-cost sample. The recommended fix remains explicit scenario qualification or direct all-attempt costing, not rejection of1.2%as a possible scenario.

## 3. Accountability example code supports the printed local arithmetic

- `code/verify_theory.py:2247–2266` implements the common-mode control probability, layer cost and finite design search.
- `code/verify_theory.py:2256` computes the in-scope application ITGC line as `$2k*15 + $2.5k*24 + $24k/1.22 + $55k + $10k*4`, approximately$204,672.
- Lines2274–2289 select onehuman+oneAI at5%,onehuman+twoAI at1%, with the published3.1%/0.7%annual escape probabilities, and add a$1.492375m audit fee plus$1.5m SOX budget (line2284).
- Lines2589–2605 construct the bottom-up one-objective floor and application-count sensitivities. `code/paper1_macros.py:350–385` emits floor/sensitivity macros.
- `code/paper1_macros.py:376–382` computes the period-persistent state probability as `p_ca+(1-p_ca)*(1-(1-p_a**3)**N)`, consistent with S2.6 and my independent arithmetic.

These observations strengthen “resolved” for GPT7/GPT8's disclosed scope and temporal-dependence issues. They do not establish that the input rates, external audit fee, objective count or application cost is valid for a whole enterprise. CS-3 remains a wording/scope issue in executive summary item9: the code still models a single objective, whereas the summary sentence sounds firm-wide.

No new demonstrated double counting was established from this targeted inspection. Older comments still mention$350k, but the active line and calculations use$204,672; do not report the stale comment as an active numerical defect.

## 4. Rented/owned/mixed engine accounting: what is actually implemented

This engine is companion material; these observations are not an assertion that the main paper provides an empirically priced enterprise deployment calculator.

`engine/src/autofrontier/economics.py:298–315` constructs inference cost in dollars per human-equivalent task unit. For owned shareu, running inference is multiplied by `(1-u)+u*owned_opex_share` (line307). Capital is `u*compute_capital_per_annual_dollar*piA_n` (line313), with physical capital added separately. At line399, annual economic capital charge is added to running cost. `code/examples/invoice_chain.py:847–854` separately reports `dc`, `dK`, value savings `dc-(r+delta_K)dK`, cash savings `dc-(g+delta_K)dK` and GAAP savings `dc-delta_K*dK`.

At defaults owned running share0.3, capital factor3 and replacement rate0.25, normalize the annual reference rental bill to1, ignore taxes/fees/physical assets and hold requirements equal:

| Owned share | Annual running bill | Installed capital | Annual replacement | Running plus replacement | Economic running plus capital at r0.0893 |
|---|---:|---:|---:|---:|---:|
|0|1.000|0.000|0.000|1.000|1.00000|
|0.5|0.650|1.500|0.375|1.025|1.15895|
|1|0.300|3.000|0.750|1.050|1.31790|

This is arithmetic conditional on scenario inputs, not evidence that ownership is generally cheaper. A growth cash requirement adds `g*3u`. Mixing is linear in this portion; coordinating two environments, reservation/fallback contracts, capacity utilization and option value are not newly estimated by these formulas. The source factor in S11 is per at-cost TCO dollar, whereas this engine factor is applied to the reference rental-price dollar. Those denominators must not be silently conflated.

An implementation issue of limited companion scope: line306 uses `firm.fin.get('owned_compute_share') or default`, which treats an explicit0.0 as missing. `impute.py:608` correctly preserves explicit0.0, so economics can override the requested fully rented case when a nonzero default is configured. The shipped default is0, so this does not change the default baseline. A robust fix is an explicit `None` check. This is a minor configuration defect, not a demonstrated main-paper table error.

## Evidence limits

This addendum reviews source definitions and selected arithmetic. Root owns full program execution, committed-output comparison and the repository-wide verdict. No claim that all code is correct follows from these selected reads. No restricted materials were needed for these conclusions.
