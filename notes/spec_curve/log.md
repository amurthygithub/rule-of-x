# Specification curve: work log

All times UTC, 3 November 2026. The pre-specification (`design.md`) was written first and has not been edited since;
deviations found later are recorded here.

## Timeline

- 14:36 `notes/spec_curve/design.md` written (claims, choices, options with sources, invalid combinations, summary
  statistics, bootstrap subset rule, reviewer variants, reproduction check). No estimate of this analysis existed.
- 14:40 first run of `code/spec_curve.py`, reproduction check only: at the 21 published samples in the grid, 929 stored
  statistics of `notes/empirics_v3.json` reproduced with a largest absolute difference of 0 (bit-identical), and 48 printed
  macros of `paper1/macros.tex` after rounding, including the paper's leave-one-firm values of the anchor.
- 14:44 timing probe on the baseline sample: about 30 ms per sample for the point estimates and 26 ms per bootstrap draw
  (all claims), so a bootstrap of all 720 samples at B = 199 would need about 30 minutes on 2 free cores; the
  pre-specified subset rule applies.
- 14:45 grid without the bootstrap (`SC_B=0`): 116,496 specifications and 103,680 forward-paired ones in 38 s; leave
  one firm out in 20 s.
- 14:47-15:02 first full run (937 s; bootstrap 869 s, within the 15-minute budget). Another agent's run of
  `code/estimate_v3.py` shared the 2 cores; a draw cost 40 ms and the rule gave K = 169 samples (the 21 published ones and
  148 drawn at random).
- 15:03 outputs written from that run's results (`SC_FROM_CACHE=1`); figure and text revised.
- 15:07-15:20 final full run, `SC_BOOT_K=169` (750 s; bootstrap 679 s). It read the data at 15:07, before the panel was
  rebuilt at 15:19 (see below); its reproduction check passed (929 statistics, difference 0; 48 macros). Every
  specification's estimate and bootstrap interval, the leave-one-firm-out and the forward-pairing results are identical
  to the first run's (determinism check). All 35 qualitative statements of the draft section pass `check_text_claims`.
  The reported outputs are this run's.

## Deviations from design.md

1. Sections 5 and 7 of design.md say "22" published samples. Table tab:robust has 22 rows, but one of them, the first
   test run's E2 rule, is excluded from the grid by section 3; the list in section 7 names the 21 that are in the grid.
   The reproduction check and the bootstrap subset use those 21. A counting error, with no effect on any choice or test.
2. Figure: panel B is shaded by the sign test (C3b), since every specification also passes C3a; the option rows show
   every family of acquisition treatment and, for the other choices, only the options other than the paper's.
   Presentation only.
3. `n_without_interval` in results.json counted undefined specifications in the first run; corrected before the final
   run (0 defined specifications lack an interval). No reported number used it.
4. `SC_BOOT_K` added so that the reported run is reproducible exactly: only the size of the bootstrap subset depends on
   the machine (the timing rule); the subset itself is seeded. Under the final run's load the rule alone would have given
   K = 264; K = 169 was fixed to repeat the first run.

## The panel rebuilt after the reported run (for the lead)

At 15:19-15:21 another agent rebuilt `data/panel_v3*.csv` (commit c3c48af, "R2 applied and capitalized software
corrected in the panel; estimates not yet regenerated") and changed `code/build_panel_v3.py` and `code/estimate_v3.py`.
The reported results are for the panel of the initial import (f5d12f7), on which every printed number of the paper
rests. On the rebuilt panel the script's reproduction check fails until `notes/empirics_v3.json` is regenerated (it
compares against the stale JSON and stops, as designed).

After `estimate_v3.py` and `paper1_macros.py` have been rerun, rerun `python3 code/spec_curve.py` (about 15 minutes) to
refresh every output. On the rebuilt panel rule R2's options change by rule, not by hand: the classifier's firms are
already outside the main sample, so that option drops out, and the two independent readers' classifications enter
("both" and "either"). The R2 choice then has 4 options (main sample; all 16 named firms dropped; firms both readers
class as not software dropped; firms either reader classes as not software dropped), the grid has 960 samples, and the
reproduction check covers 23 published variants (E1r2named and E2r2named, now equal to E1 and E2, leave the grid; the four
reader variants enter). This is a change of design.md's choice C, forced by the author's decision to apply R2 to the
main sample; it should be noted with the rerun. A dry run on the rebuilt panel (grid construction and the statistics of
40 samples, no reproduction claim) runs cleanly. The capitalized-software correction changes every cash margin, so the
cash results will change; `check_text_claims` stops the script and names any sentence of the draft that the new results
no longer support.

## Rerun on the re-estimated sample (3 Nov, after commit 805e1e0)

The lead re-estimated the paper with rule R2 applied to the main sample by the pre-set rule (E1: 1,732 firm-years of 284
firms, against 1,788 of 292), capitalized software corrected from the filings, and the two independent R2 readings as
sensitivities (variants E1r2both, E1r2either and their E2 versions). The design of design.md was kept: the same claims,
tests, choices and options, except where the sample rule itself changed.

- Choice C (rule R2) follows the panel by the rule written in the script (`R2_LEVELS`): the classifier's firms are now
  outside the main sample, so that option drops out, and the paper's two reader sensitivities enter. Options: main
  sample (R2 applied) / without all 16 named firms / without the firms both readers class as not software / without the
  firms either reader so classes. The grid has 960 samples (was 720) and 155,328 specifications (was 116,496); the
  forward-paired grid 138,240.
- Reproduction check: 1,009 stored statistics of the re-estimated `notes/empirics_v3.json` at 23 published variants
  (E1r2named and E2r2named, now equal to E1 and E2, leave the grid; the four reader variants enter), largest absolute
  difference 0; 48 printed macros of the regenerated `paper1/macros.tex`.
- Bootstrap: B = 199 as before; the timing rule gave K = 206 samples (33 ms per draw). Runtime 515 s (grid 46 s).
- The C7 test stays the pre-registered 2.95 <= ratio < 3.55 ("3.0 to 3.5"), although the paper's four-view range is now
  printed as 3.1 to 3.5.
- Seven statements of the draft section no longer held on the new results (window -> R2 as the most influential choice
  of the slope; GAAP steepening negative in 91.9%, not above 95%; netted anchor positive in 99.7%, not all; the E2 cash
  difference no longer changes sign when one firm is removed, the M = 4 one does; under E1 the literal pairing turns
  the cash difference positive; Pi_lb interval above zero in 99.2%, not all; the GAAP decline's interval at the paper's
  definition below zero in 62.6% of the bootstrapped samples, not all). The sentences and their checks were revised
  (16:00-16:10 UTC); all 36 checks pass. Outputs were then rewritten from this run's results (`SC_FROM_CACHE=1`).

Results, old sample -> new sample (share of specifications holding; interval share on the bootstrapped subset):

| Claim | Point, old | Point, new | Interval, old | Interval, new | Median, old -> new | Most influential, new |
|---|---|---|---|---|---|---|
| C1 P95 decline, GAAP | 97.1% | 94.3% | 40.7% | 29.0% | -6.0 -> -4.9 | upper quantile |
| C2 P95 decline, cash | 100% | 100% | 48.9% | 42.2% | -7.3 -> -7.2 | end period |
| C3 Psi GAAP > -1 / < 0 / > -0.5 | 100 / 100 / 84.6% | 100 / 100 / 65.5% | 100 / 96.6% | 100 / 96.1% | -0.39 -> -0.43 | rule R2 (was window) |
| C4 Psi cash > -1 / < 0 / > -0.5 | 100 / 100 / 96.3% | 100 / 100 / 87.9% | 100 / 99.4% | 100 / 99.2% | -0.32 -> -0.37 | rule R2 (was window) |
| C5 GAAP steepening | 96.8% | 91.9% | 31.9% | 18.4% | -0.26 -> -0.24 | frontier estimator |
| C6 cash no steepening | 58.2% | 74.4% | 97.5% | 99.0% | +0.05 -> +0.12 | acquired growth |
| C7 spend ratio in 3.0-3.5 | 73.1% | 32.5% | - | - | 3.41 -> 3.65 | acquired growth |
| C8a anchor Pi_lb > 0 | 100% | 100% | 100% | 99.2% | +17.2 -> +16.4 | cut-off |
| C8b anchor Pi_net > 0 | 100% | 99.7% | 60.9% | 38.4% | +12.3 -> +9.8 | cut-off |

At the paper's definition of the decline, the fall across the sample choices runs from 6.3 to 12.9 points (GAAP) and 6.8
to 12.7 (cash), against 6.9 to 12.8 and 6.6 to 12.8 before; its interval excludes zero in 62.6% (GAAP, was 100%) and
56.3% (cash, was 55.0%) of the bootstrapped samples.

## Reading of the forward-pairing request

The request describes the forward pairing as "growth of year t paired with the margin of year t+1"; reviewer GLM-M9 and
the paper's lead regressions (empirics.tex:33) pair this year's margin with next year's growth (g_{t+1} + m_t). These
are different pairings. Both are computed: F1 (g_{t+1} + m_t, indexed by the margin year; the reviewer's and the
model's timing; also over the whole grid), F1' (the same pairs indexed by the growth year) and F2 (g_t + m_{t+1}, the
literal wording). F1 is the one the draft section leads with. Pairing was checked on one firm's rows by hand.

## Commands

    python3 code/spec_curve.py                      # full run: reproduction check, grid, bootstrap, variants, outputs
    SC_BOOT_K=169 python3 code/spec_curve.py        # the reported run exactly (on the panel it was run on)
    SC_B=0 python3 code/spec_curve.py               # without the bootstrap
    SC_FROM_CACHE=1 python3 code/spec_curve.py      # rewrite outputs from the last full run (SC_CACHE, outside the repo)
