# Issue log: Mistral Large 4 (high effort) referee review of Paper 1 v3

- **Reviewer:** Mistral Large 4, high effort, run outside the project workflow by the author ("blind first pass"; the reviewer read neither the earlier panel reports nor the other outside reviews, `EVIDENCE_BOUNDARY.md`).
- **Received:** 3 November 2026, 06:10 UTC−8, as `referee-review.zip` (SHA-256 2b61183d…c22b22a). **Verified:** 3 November 2026.
- **Build and commit reviewed:** `paper1 Nov 2.pdf` (82 pp., SHA-256 bd87f45f…) and `Supplement Nov 2.pdf` (57 pp., acf9d62b…), the same 2 November build the other three outside reviews read, and the repository at commit 62e574b. Round 3 (branch `review-round-3`) has since changed the text; the dispositions below say where.
- **Reviewer's verdict:** accept with minor revisions for the working-paper track (arXiv q-fin.GN / econ.GN): "technically sound in everything I could check". Eight findings F-1 to F-8 (none an error in the paper), minor items M-1 to M-8, five editorial repairs and an eight-step revision sequence (RS-1 to RS-8).
- **Archive:** the whole bundle is in this folder (34 files: the reviewer's nine reports, 22 scripts and results). It contains no third-party text and does not name the excluded registrant (scanned for its name and identifier, 3 Nov).
- **Our verification scripts:** `verification_claude/`, not part of the bundle; none imports the reviewer's code. Each output is saved beside its script.
  - `f6_hjb_policy_bound.py`: whether a simple admissible spend policy beats the no-spend value at the worked example's parameters.
  - `f4_acq_flag_columns.py`: the two acquisition-flag columns of `data/panel_v3.csv` and the anchor under each.
  - `fe_within_firm_slopes.py`: the paper's within-firm specification rerun on the shipped panel.
- **Classification:** as in the other logs: Valid; Partly valid; Not valid (reviewer error); Already handled.
- **Dating:** the tables below were written on the morning of 3 November, while the round-3 tests ran; rows that say "Running" are superseded by the section "Status after the round-3 tests" at the end, and the response to the outside reviews (`notes/reviews/paper1_v3/response_to_outside_reviews.md`, Mistral section) gives the final disposition.

## Findings

| ID | Reviewer's point | Classification | Evidence | Action |
|---|---|---|---|---|
| F-1 | (H) is unproved and carries the "firm's own weight" claim; correctly disclosed; optional abstract pointer | Valid; already handled | The abstract says "Under a verification hypothesis"; round 3 added "under (H)" at 16 places (DS-17). | None |
| F-2 | Headline claims are descriptive and rest on partly applied sample rules (R2 for 16 named firms only); acceptance test: classify all registrants by business description and rerun the headline statistics | Partly valid | The coverage counts are in the main text (`data.tex` R2 bullet, macros `\VRtwoFirms` etc.), as the reviewer concedes. The acceptance test has not been run. | Running: Item 1 descriptions of all 293 core-sample firms retrieved from sec.gov (3 Nov), then R2 applied by the pre-set keyword rule of `build_panel_v3.py` (task 48). |
| F-3 / M-1 | The abstract's 2036 sentence lacks the scenario caveat | Already handled | Round 3 abstract: "On a central scenario, not a forecast, a top-tail firm realizes ..." | None |
| F-4 / M-2 | `data/panel_v3.csv` carries the v2 flag `acq_flag` and the v3 flag `acq_flag_v3`; a naive reuse of `acq_flag` gives 14 anchor firm-years, not 13 | Valid | `f4_acq_flag_columns_output.txt`: 15 rows differ; `estimate_organic.py` lines 130 and 195 replace `acq_flag` by `acq_flag_v3` on load; anchor 14 firm-years (8 firms) with `acq_flag`, 13 (7) with `acq_flag_v3`, as printed then. After the re-estimation of 3 November the counts are 15 (8) and 14 (7) (`f4_acq_flag_columns_output_2026-11-03_reestimated.txt`); the notes cite the new counts. | Done (3 Nov): named in `appendix_data.tex` (Reproducibility) and `code/REPLICATION_README.md`. |
| F-5 | The accountability floor operationalizes a legal standard with a scenario probability; arithmetic exact | Valid; no change | The paper calls the threshold "a judgment and a scenario value" and reports 5% and 1%. | None |
| F-6 | The reviewer could not reproduce the numerical HJB profile (v' 9.1 / 7.2 / 5.4); its solvers returned the no-spend solution (v/s = 5.83) | Not valid as a concern about the paper; the request for a solver-independent check is reasonable | `audit_hjb_indep.py` discounts at r instead of r − G and stops after 300 steps of 0.02 years (about 6 years of horizon), so it is neither the paper's problem nor converged. `audit_hjb3.py` returns the no-spend value at every share. A policy that spends 5% of revenue until the share reaches 0.4 is worth v/s = 9.02 at s0 = 0.01 and 7.33 at s0 = 0.1, against 5.83 for no spend (`f6_hjb_policy_bound_output.txt`), so no-spend is not optimal and a solver that converges to it is wrong for this problem. | Done (3 Nov): check 15q of `verify_theory.py` (bound 9.020 / 7.333; the sweep's v/s 9.136 / 7.448; 202/202 pass) and a section of `REPLICATION_README.md`. |
| F-7 | Growth-rate conventions in the extreme-score passages | Valid; no change | Conventions are labelled where it matters (reviewer). | None |
| F-8 | The four estimands share most firm-years; E2 drops 88% of acquisition-affected years; keep "292 software firms" phrasing | Valid; already handled | The paper says they are "a sensitivity set, not four independent replications"; no "software industry's frontier" phrase in `sections/` (grep, 3 Nov). | None |

## Minor items

| ID | Point | Classification | Action |
|---|---|---|---|
| M-3 | The familywise families contain uninformative members | Already handled | Round 3 (GLM-F5) added the 18-test family and the text says such survivals "say little". |
| M-4 | Interest and taxes paid come from SEC frames (latest filed) | Already handled | Disclosed in `appendix_data.tex`. |
| M-5, M-6, M-7 | Process candour; macros idempotent; exclusion irreversible and disclosed | Valid; no change | None |
| M-8 | Citations not re-verifiable from the reviewer's environment | Partly valid | Primary-source pass of the legal and tax citations running (task 49). |
| Empirical 7 | Within-firm slopes: reviewer +0.083 / lead −0.112 / cash −0.009 against printed +0.06 / −0.03 / −0.03 | Not valid (reviewer's specification) | The paper's specification reproduces the printed values from the shipped panel: +0.059 (0.060), lead −0.034 (0.050), cash −0.032 (0.043) (`fe_within_firm_slopes_output.txt`). The trim of growth at 150% that the code applies is not stated in the text; dropping it changes little (+0.068, −0.038, −0.019). Done (3 Nov): the trim is stated in `empirics.tex`. |

## Editorial repairs and revision sequence

| ID | Point | Classification | Action |
|---|---|---|---|
| Ed-1 / RS-5 | Abstract scenario tag | Already handled | See F-3. |
| Ed-2 / RS-3 | Name `acq_flag_v3` | Valid | See F-4. |
| Ed-3 / RS-4 | R2/R3/R5 coverage sentence in the main data section | Already handled; test running | See F-2. |
| Ed-4 / RS-1 | Note that the grid solution may be one of several solutions of the singular ODE; add a solver-independent check | Partly valid | The singular point and the free constant are stated (`supp_proofs.tex` line 173). Done: the policy bound (F-6). |
| Ed-5 / RS-6 | Primary-source pass of the 2025–26 legal and tax items | Partly valid | Running (task 49); a specialist's read before journal submission is advisable. |
| RS-2 | Compute-share caveat in the abstract and the caption of Table tab:ceiling; "28–78" | Partly valid | Done (3 Nov): the caption of Table tab:ceiling says the compute share is a scenario value that no source measures; the floor's units are corrected (1.2% of revenue, not 2%), so the range is 28 to 78%. |
| RS-7 | Independent full-pipeline reproduction | Valid | Running: a fresh clone at be86d24 with a fresh environment (task 50). The first attempt stopped at stage `params` because the third-party raw data are not redistributed; the replication package needs a retrieval script and a clear message (packaging fix). |
| RS-8 | Keep the post-hoc choices in Appendix A | Valid; no change | None |
