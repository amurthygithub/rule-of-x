# Specification curve: work log

All times UTC, 3 November 2026. The pre-specification (`design.md`) was written first and has not been edited since;
deviations found later are recorded here.

## Timeline

- 14:36 `notes/spec_curve/design.md` written (claims, choices, options with sources, invalid combinations, summary
  statistics, bootstrap subset rule, reviewer variants, reproduction check). No estimate of this analysis existed.
- 14:40 first run of `code/spec_curve.py`, reproduction check only: at the 21 published samples in the grid, 929 stored
  statistics of `notes/empirics_v3.json` reproduced with a largest absolute difference of 0 (bit-identical), and 48 printed
  macros of `paper1/macros.tex` after rounding. The anchor's leave-one-firm values of the paper were reproduced as well.
- 14:44 timing probe on the baseline sample: about 30 ms per sample for the point estimates, 26 ms per bootstrap draw
  (all claims), so a bootstrap of all 720 samples at B = 199 would need about 30 minutes on 2 free cores; the
  pre-specified subset rule applies.
- 14:45 grid without bootstrap (`SC_B=0`): 116,496 specifications and 103,680 forward-paired ones in 38 s; leave one
  firm out in 20 s.
- 14:47 full run with the bootstrap started. Under the machine load at that time (load average 2 to 7, other jobs on
  the 2 cores) a draw cost 40 ms, and the rule gave K = 169 samples (the 21 published ones and 148 drawn at random).
- (completion, runtime and the from-cache output run: see below)

## Deviations from design.md

1. design.md, sections 5 and 7, says "22" published samples / variants. Table tab:robust has 22 rows, but one of them,
   the first test run's E2 rule, is excluded from the grid by design.md section 3. The list in section 7 names the 21
   that are in the grid. The reproduction check and the bootstrap subset use those 21. Counting error in the design;
   no effect on any choice or test.
2. Figure, panel B: points are shaded by the sign test (C3b), since every specification also passes C3a; panel A by the
   decline test (C1). Presentation only.
3. The bootstrap ran under heavier load than when K was set, so its wall time exceeded the 15-minute target (actual
   time below). K was not changed after the run started.

## Reading of the forward-pairing request

The request describes the forward pairing as "growth of year t paired with the margin of year t+1"; reviewer GLM-M9 and
the paper's lead regressions (empirics.tex:33) pair this year's margin with next year's growth (g_{t+1} + m_t). These
are different pairings. Both are computed: F1 (g_{t+1} + m_t, indexed by the margin year; the reviewer's and the
model's timing; also over the whole grid), F1' (the same pairs indexed by the growth year) and F2 (g_t + m_{t+1}, the
literal wording). F1 is the one the draft section leads with.

## Commands

    python3 code/spec_curve.py                      # full run: reproduction check, grid, bootstrap, variants, outputs
    SC_B=0 python3 code/spec_curve.py               # without the bootstrap
    SC_FROM_CACHE=1 python3 code/spec_curve.py      # rewrite outputs from notes/spec_curve/_cache.pkl (last full run)
