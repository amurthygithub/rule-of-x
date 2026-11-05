# Mathematical and formal-source addendum after repository access

This addendum was written after the independent Part B was frozen. It does not replace or modify that frozen assessment. It inspects the copy of commit `eb7537bee7585f2902304f62a722edea6ced8539` at `pinned_snapshot/`. No `notes/reviews/` file, joint response, or other reviewer response was read. No source file was modified. Root is responsible for the Lean installation/build attempt and the complete author verification runs; the conclusions below distinguish source inspection from kernel execution.

## M1 numerical reconstruction now completed

I independently reconstructed the cone slope using the pinned `data/panel_v3.csv`, the recorded baseline slopes from `notes/frontier_slope_v3.json`, and a centered covariance formula for the regression slope on the grid 0,.05,...,.60. For each alpha in {.25,.30,.35,.45}, I transformed the growth data to the hypothetical common-frontier margin before taking the type-7 .90 quantile in each cone cell. This is the correct empirical calculation: applying a nonlinear margin function to a linearly interpolated growth quantile would not generally produce the same finite-sample value.

All eight reconstructed multiplier/steepest-slope pairs matched the committed calibration to 1e-10. Endpoints:

| Basis | Multiplier range | Largest frontier slope magnitude at growth .60 |
|---|---:|---:|
| GAAP | 2.07623 to 4.00621 | .415489 to .801711 |
| Cash after SBC | 2.07189 to 3.99392 | .351097 to .676799 |

This upgrades the prior 'not rerun' limitation on GPT-M1: the mapping correction and its printed rounded multipliers are now reproduced. It does not remove the remaining interpretation qualifier in finding T3. The code explicitly imposes `k=0` and treats the raw growth window as excess growth (`code/calibrate_horizons.py:1137–1145`, implementation `1149–1174`). The exact cone uses 1,726 GAAP-complete and 1,683 cash-complete growth observations, of which 64 and 65 respectively exceed .60. Maximum growth is 3.12797. The same hypothetical common frontier, calibrated to its cone slope, has slope magnitude at that maximum of 3.126–113.593 on GAAP and 2.642–95.894 on cash. These are hypothetical derivatives, not estimates of actual firm decision weights. They demonstrate why the slope bound within the .60 threshold window cannot be applied to all firms entering the cone.

The author's independent-root-solve check is also visible in `code/verify_theory.py:3164–3211`; it solves for ell with brentq rather than relying on the calibration's scale identity. Root's execution of that complete script is separate evidence.

Own deterministic reproduction: `scripts/theory_pinned_source_checks.py`; results `results/theory_pinned_source_checks.json`, including input SHA-256 hashes. No random seed is needed.

## Lean correspondence: source inspection supports the stated restricted scope

I found no source-level gap that changes the assessment of the static power model. The following checks concern the actual definitions and theorem types, not the README's assertions alone:

* `formal/RuleOfX/Defs.lean:44–60` defines growth, admissible spending, feasibility, dominance and the efficient frontier from undominated feasible points. Thus the frontier characterization is not merely made true by defining the frontier to equal the proposed graph.
* `formal/RuleOfX/Frontier.lean:94–130` proves dominated-iff-below and derives `frontier_eq`; the combined Lemma 1 type at `152–161` includes the graph characterization, feasible hypograph, convexity, dominance equivalence and unique spend. Sign and power-domain assumptions are present.
* `formal/RuleOfX/Score.lean:380–397` includes uniqueness, positive excess growth, tangency, cap-equality endpoint handling, both spend/score forms and the margin identity. The nonbinding cap is an actual hypothesis (`381`), not an unchecked informal note. The X<=k corner is separately proved at `443–449`.
* The dual weight-identification type explicitly restricts growth to the interior of its feasible interval (`formal/RuleOfX/Score.lean:508–514`, with its Fermat step at `471–482`). That is appropriate and reinforces the need for the corresponding interior qualification when the prose infers decision weights from slopes.
* `formal/RuleOfX/Saturation.lean:165–168` proves that the closed-form `Rst` is the greatest feasible score. The maximal-score relationship is included in the saturation theorem (`199–208`) and in the envelope theorem (`formal/RuleOfX/Envelope.lean:312–335`). The calculus claims therefore concern the maximized economic score, rather than an unrelated function that happens to share its formula.
* `formal/RuleOfX/Capital.lean:71–87` contains the exact finite-change bracket and the directional derivative interpretation of 'to first order'. It does not replace the exact finite-change bracket by an unjustified iff. The growth-efficiency mapping and derivative gains appear at `141–162`; the capital-for-labor interpretation appears at `252–265`.
* The continuous-time theorem types use absolutely continuous paths and an almost-everywhere share equation, not everywhere differentiable paths (`formal/RuleOfX/BudgetCont.lean:186–198`, `225–236`). They explicitly conclude integrability of the positive score excess. This avoids the pitfall of a nonintegrable Lean integral defaulting to zero.
* The induced logistic path is genuinely constructed and proved to be absolutely continuous, in the share interval, initialized at s0 and to satisfy the ODE almost everywhere (`formal/RuleOfX/BudgetCont.lean:399–420`). The induced-path budget corollaries (`424–462`) remove the earlier hypothetical path-existence limitation. The static-optimum induced-path theorem correctly retains the feedback policy equation as a hypothesis (`480–487`). Uniqueness of the ODE is not formalized, as the README discloses, but the bounds have both general-path and constructed-path versions; uniqueness is not needed for those bounds.

The default root imports the axioms module (`formal/RuleOfX.lean:1–10`), whose `#print axioms` directives cover 35 named results (`formal/RuleOfX/Axioms.lean:18–52`). A nested-comment-aware scan of all 17 Lean files found no source declarations of new axioms/opaque constants and no `sorry`, `admit` or `sorryAx` tokens outside comments. This is useful source evidence but cannot establish the elaborated dependency axioms without a successful build and the resulting `#print axioms` output.

The independent-check library is a separate non-default target in `formal/lakefile.toml:12–15`. A main-library success alone should not be reported as execution of `RuleOfXChecks`; the second target needs its own command and outcome. The toolchain pins Lean v4.35.0 (`formal/lean-toolchain:1`) and Mathlib v4.35.0 (`formal/lakefile.toml:4–7`).

## Small documentation correction

Editorial: the introductory docstring of `formal/RuleOfX/BudgetCont.lean:22–25` still says path existence is not formalized and that the cap condition is assumed. That description predates `induced_isPath` and the induced-path corollaries later in the same file (`399–462`). It should be updated to distinguish the general-path versions from the subsequently constructed induced path. The README and supplement describe the newer implementation accurately; this is a stale module comment, not a proof failure.

## Effect on the original findings

* GPT-M1's exact identity and reported numerical calibration are now independently reproduced. Retain T3 only for the cap/support/parameter interpretation in main p24, not as a computational failure.
* No new static theorem error was found in the source correspondence review. Final 'machine checked here' status still depends on root's Lean build and axiom output.
* T1 (abstract cash-margin wording), T2 (free-entry statement), T3 (weight-bound qualification), and T4 (general concave technology needs finite optimum) survive this inspection. The latter three concerns involve statements outside the claimed Lean proof scope or an inference made from an interior theorem; a successful static Lean build would not settle them.
