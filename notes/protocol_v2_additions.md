# Protocol appendix, v2: content for the P1 editor

Source records: notes/agent_log.md (times are UTC−7), notes/research_errors_log.md (B1k, B1l), notes/reviews/paper1_v1/ (all 12 reports, issue_log.md, revision_plan.md), and notes/estimand_notes.md §1. Every statement below must be checked against those files when it is written into sections/appendix_protocol.tex.

## 1. Corrections to the existing appendix text
- **Models.** "All AI work was done by agents … configured for the model identifier claude-opus-5-5; subagents inherited it" is no longer true. Two other models were used:
  - the four cross-model referees and the second assumptions auditor ran on `fable`;
  - the v2 literature agent ran on `sonnet`.

  The author asked for this on 29 Oct at 13:08: "Use different models." Give each agent's model in Table tab:agents (from agent_log), and say the model was chosen per agent.
- **"The first draft's flat cross-sectional frontier did not survive the rebuilt data, and the paper reports the reversal."** This is wrong (referee 3, R3-9). The flat frontier survives the data rebuild under the original dominance-cone estimator. The "reversal" came from switching to a local conditional quantile, as the first-round econometrician recommended. Rewrite the sentence, and the "Referee round" paragraph's "a finding (the flat frontier reversed)", to say so.
- **The estimand switch.** It is not an "error … caught by reversing course openly"; it was a researcher degree of freedom (R3-11c). Move it out of the errors paragraph into a separate "Choices made after results were seen" paragraph (§3 below).
- **"Choice of estimand" paragraph.** Its claims that three conclusions changed (the steeper GAAP slope on the organic frontier, the size gradient, the cash steepening) and that the anchor moved are withdrawn (research_errors_log B1k). Replace them with the v2 policy (§3, D-3).
- **"What the protocol does not establish."** Keep the shared-blind-spot caveat. Add that cross-model review reduces this risk but does not remove it, because all the models come from one developer. Report the agreement factually: the Opus and Fable econometrics referees, working without sight of each other's reports, reached the same main findings by different routes.

## 2. Review panels on this version (fills the placeholder in app:protocol-panels)
- **Snapshot.** All reviews ran on a frozen snapshot (notes/reviews/paper1_v1/paper1_v1.pdf, 81 pages, with source tarball) from 12:46 on 29 Oct.
- **Panels, by model.**
  - Opus: four academic referees (economic theory; finance and accounting; econometrics; IO and the economics of AI). Also four practitioner panels: corporate executives; investors and bankers; investment management; risk, audit and regulation. Each practitioner panel was a single agent playing several named roles (IM-6). Say this explicitly; it is structured self-critique, not a set of independent human experts.
  - Fable, a different model, from 13:09: four cross-model referees in the same four fields. They were told not to read the other reports.
  - Fable, from 13:10: a second assumptions auditor, a read-only audit that re-grounded the parameters the panels challenged.
- **Outcome.** All 12 recommended major revision. No referee found a false theorem in the static model, and the theory referees re-derived every result. Number checks: 73 of 80 match and 6 match with caveats (finance, Opus); 56 of 58 match (finance, Fable); the econometrics referees reproduced every point estimate except one solver approximation.
- **Main findings, and the changes made.** Use revision_plan.md sections A to E:
  - the growth weight was withdrawn and bounds reported (D-1);
  - the E1–E2 contrasts were withdrawn;
  - T(40%) was withdrawn;
  - the capital-intensity gap is now reported as an accounting effect;
  - anchor intervals were added;
  - the decline is explained as a change in composition;
  - the horizon upper ends were dropped;
  - the theory's assumptions are stated (C1 to C9);
  - the round-2 parameters were adopted (D-4);
  - the citations were corrected.
- **Declined, with reasons.**
  - A competing-interests statement (RA-6): the author decided against one.
  - A market test of the 7–13 weight against valuation multiples (IB-2): moot once the weight was withdrawn; noted as future work.
  - Anything else the editor declines is listed with its reason.

## 3. Choices made after results were seen
Each choice gets a time and a reason.
1. **Primary sample for the model-facing results switched to the organic frontier.** Decision at 11:19, after the exclusion-only robustness row was known; estimand_notes §1 gives what was known.
2. **Two pro forma rules added at 11:44**, three minutes after a test run's E2 estimates were seen: the adjustment applies to flagged years only, and the ambiguity exclusion (AMBIG_TOL of one point). Report E2 without these rules: −0.547 GAAP (exact) and −0.431 cash, against −0.564 and −0.432.
3. **v2 estimand policy (D-3), author decision at 13:53.** E1 is the baseline. A model-facing claim stands only if it holds under E1, E2 and the two imputation bounds. This choice was made after the round-1 referees showed the E1–E2 contrasts were selection artifacts.
4. **Frontier object (D-2), at 13:53.** The author asked the lead agent for the right call. The lead agent set the theory's object, Ψ_χ (the order-χ frontier among firm-years with growth at least g), as primary for the model-facing claims and the ℓ calibration, with the local conditional quantile reported as a labeled descriptive statistic. The choice was fixed before any panel_v3 estimate was computed, and the sample-audit agent records a dated line in its results notes saying so.
5. **Growth weight (D-1), at 13:53.** The "7 to 13" claim was withdrawn after eight reports disputed it. The bounds from each method are reported.
6. **Parameters (D-4), at 13:53.** All round-2 values were adopted in one commit, before the v2 numbers were computed.

## 4. Additions to the decisions table (tab:decisions)

| Decision | Choice |
|---|---|
| Review independence | Asked for different models to be used (13:08); round-1 cross-model referees on a second model |
| Revision decisions (13:53) | Withdraw the 7–13 growth weight and report bounds; claims must hold under every estimand view; adopt the re-grounded parameters in one commit; on the frontier object, asked for the lead agent's call |
| Title | "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation" (12:03) |
| Competing interests | No statement (10:50) |
| Practical outcome | Strategy by Rule-of-X level and organization setup (11:40), down to the process step (11:58); P1 carries a short section, P2 the full playbook |

## 5. Additions to the errors table (tab:errors)
- **Round-1 econometrics referees (Opus and Fable):**
  - E1–E2 contrasts reported as significant on 90% percentile intervals, with no familywise correction (none survives Holm);
  - E2 as an exclusion sample;
  - T(40%) with silently dropped bootstrap draws;
  - an IRLS slope reported as the quantile-regression solution;
  - the anchor without sampling uncertainty;
  - a size gradient without period effects;
  - the estimated object not matching the defined frontier;
  - a replication order that could not rebuild Section 7.
- **Round-1 finance referees and panels:**
  - an annuity that charged financing twice, because operating cash flow is already after interest;
  - 139 backfilled firm-years;
  - a captive firm in the anchor;
  - misclassified firms;
  - debt-only filers;
  - the cash score not stated as after interest and cash taxes;
  - an a_min percentile taken from the broad sample.
- **Round-1 IO and AI referees:**
  - Demirer et al. misread;
  - a compute share without measured grounding;
  - prices held fixed despite the paper's own pass-through result;
  - an infeasible free-entry example;
  - horizon upper ends from an incoherent case;
  - parameter sources used but not cited.
- **Round-1 theory referees:**
  - an upper bound in prop:expected that fails under random reorganizations;
  - a partial-realization claim that is false under free retry;
  - the ceiling's scope;
  - the HJB existence assumption not stated;
  - the calibration using a fluid relaxation the proposition does not cover;
  - an undefined symbol;
  - an inconsistent ψ convention for owned compute.
- **Risk panel:**
  - the accountability floor treated as a cost trade-off rather than a pass/fail ICFR constraint;
  - common-mode shocks;
  - regulatory anchors superseded after the knowledge cutoff (SR 11-7 by SR 26-2 and OCC 2026-13; EU AI Act dates moved by Reg. (EU) 2026/1744), verified at primary sources.
- **Lead agent:**
  - reported the E2 "changed conclusions" to the author as findings before the referees showed they were noise (B1k);
  - recorded log times in two clocks (B1l).

## 5a. Software and process
- "Data and code are available from the author" (title footnote) must match the replication package that is actually released.
- Licenses: add that the CC BY-NC-ND and PolyForm Noncommercial licenses cover the text and the software, not the ideas. Firms may apply the ideas; commercial use of the text or the engine needs the author's written permission (EX-9).
