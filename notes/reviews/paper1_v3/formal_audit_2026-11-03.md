# Audits of the Lean formalization of the static model (3 November 2026)

- **Request:** the author, 09:27: "Formalize the static core in Lean 4" (agent log). Toolchain approval about 09:45.
- **Formalization:** an agent on `claude-fable-5-1`, in `formal/` (Lean 4.35.0, Mathlib v4.35.0, built from source because no Mathlib cache was reachable). Scope: Sections 3.1 to 3.5 of Paper 1 (Assumptions ass:market to ass:capital, def:frontier, eq:constants, prop:frontier, prop:score, prop:saturation, prop:envelope, prop:budget, cor:transient, cor:capital, cor:priorities).
- **Auditor:** an agent on `claude-opus-5-5` that did not write the formalization, told to edit nothing under `formal/`, to read the paper's statements before the formalizer's README, and to instantiate the hypotheses at paper-like values. Two rounds. The lead agent checked each build from a clean `.lake/build` and the axioms output itself.
- **Supplement:** Section supp:formal (S4). Mapping of every statement to its Lean theorems: `formal/README.md`.

## Round 1 (after the first delivery: 26 theorems)

| # | Finding | Disposition |
|---|---|---|
| 1 | The continuous-time theorems (prop:budget (a), (c); cor:transient (b)) assumed a share path differentiable at every date, so they said nothing about spend paths with jumps, which the paper's statement covers; proved with a step spend path (`step_vacuous`). The README understated this. | Fixed: restated for absolutely continuous share paths that solve the share equation almost everywhere (Carathéodory); round 3 adds the construction of the induced path. |
| 2 | cor:transient (b), second claim (static-optimum policy), missing; the README's reason (out of scope) was wrong. | Fixed: `cor_transient_b_optimum`. |
| 3 | Envelope, capital and priorities theorems stated for the closed form, with the link to the maximal score only in a separate lemma. | Fixed: `IsGreatest` conjuncts; the link holds for every real k. |
| 4 | prop:score (d) in its literal "unique maximizer" form, weaker than the paper's proof. | Fixed: strong form added. |
| 5 | Integrability of the integrand proved but not stated (a non-integrable integrand integrates to 0 in Lean). | Fixed: conjunct added. |
| 6 | Coverage gaps not listed: the numerical example of cor:transient (arithmetic checked: 1.81, 9.65, 5.01, 0.425, 0.298), eq:constants facts, parts of cor:priorities (ii). | Fixed in the README and Axioms.lean; the example is checked numerically by `verify_theory.py` (check 5e). |
| 7 | Some conjuncts are true for trivial reasons. | Marked as such in the README. |
| 8 | Paper: continuous-time prop:budget (c) needs a measurable moving intercept. | Paper corrected (model.tex). |
| 9 | README errors (a lemma name; where k >= 0 is used). | Fixed. |

## Round 2 (after the fixes: 30 theorems)

All nine fixed, nothing new wrong. The auditor proved that the restated theorems apply to a step spend path with its induced path (constant, then logistic), which is not differentiable at the jump, and that `cor_transient_b_optimum` is not vacuous. Remaining: the existence of the induced path was assumed, not derived; four theorems lacked the maximal-score link; two cosmetic points. All four addressed in round 3: `induced_isPath` constructs the path from the logistic formula for any measurable spend path with integrable sigma^alpha and proves it absolutely continuous, in (0, s_bar), starting at s0 and solving the share equation almost everywhere; corollaries `*_induced` state prop:budget (a), (c) and cor:transient (b) with no other share-path hypothesis. The auditor's instances are in `formal/Checks/` (library `RuleOfXChecks`).

## Final state (checked by the lead agent)

- `lake build` from a clean `.lake/build`: success; `lake build RuleOfXChecks`: success, no new Mathlib modules.
- 35 theorems printed by `formal/RuleOfX/Axioms.lean`, each depending only on `propext`, `Classical.choice`, `Quot.sound`; no `sorry`, `admit`, `axiom` or `native_decide`.
- Not formalized: cor:priorities (iv) (rests on lem:prices and prop:entry), the numerical examples, uniqueness of the induced share path (not needed: the bounds hold for every solution), and everything after Section 3.5.
- Paper statements changed because of the check: the cap condition of prop:score (sigma* = 0 when X <= k) and the measurable moving intercept of prop:budget (c). None was false.
- Round 3 (the induced path and the four links) was read by the lead agent but not audited a third time.
