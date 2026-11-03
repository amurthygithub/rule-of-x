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
