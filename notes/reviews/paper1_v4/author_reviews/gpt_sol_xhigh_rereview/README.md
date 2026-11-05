# Re-review package: computational update

Review date 4 November 2026 America/Los_Angeles (5 November UTC). Parts A–D and all 49 audit rows are included. All four minimum author commands pass on the pinned unmerged code. See Part C for optional runs, exact limits and differences.

## Contents

- rereview_report.md: verdict, updated response audit, preserved independent Part B, computational addendum, ranked recommendations and source-access record.
- response_audit.csv: exact requested columns; {'partly resolved': 9, 'resolved': 40}.
- part_b_frozen.md: immutable pre-access assessment, SHA-256 85de8d0a40cb04f00202c73bf11b5e83f9b692618bfda30d1c328e2cf3c3e327.
- scripts/ and results/: our reproducible checks, execution wrappers, seeds, output comparisons and full command logs.
- expert_notes/: complementary specialist notes, clearly distinguishing PDF review, code inspection and root-run evidence.
- source/audit_verdicts.json and source/computational_addendum.md: inputs used to assemble the current report.

## Inputs and provenance

|Input|Bytes|SHA256|
|---|---:|---|
|paper1.pdf|680970|9e986ecac307d445b0f9a636788100d8fc680f3a5508b609b430ab457788c55b|
|supplement.pdf|699953|1da736731466b00d583ee0055480bae7ad809c114edb25ad232a6d8078f2b81f|
|RESPONSE.md|27755|b068918d515709ea3af8d99c1428094cec6ddbd3d85f9b190d5fe888d52845f1|
|PROMPT.md|5909|4fc5f4065ec94a924672d7eedaf65fa6a2dec80298bf29dfa98417e4e80415fc|
|MANIFEST.txt|689|22eb33b10ca4e39b299583c3ab21891b129bbe8b6409841a83cecac28b532e01|
|upload/rereview_gpt.zip|1345377|7f08cbcea2944359d42b28a975780a0ca976eb86c1060996969742e380e0f020|

The four member hashes match MANIFEST.txt. Pinned repository PDFs equal the supplied PDFs byte for byte. Requested repository commit: eb7537bee7585f2902304f62a722edea6ced8539, branch `review-round-3`. Observed unmerged head 786228da26e12235a9d0c7aa53f2ef1fde3c07bf changes only the prompt, not code/data. 295 selected repository files were validated against their Git blob IDs; this is a selected source/data snapshot, not a claim to have downloaded all 1,015 tree entries. The separately named repository.zip was not supplied and its archive hash is not asserted. No remote repository was modified or merged.

## Independence and runtime

Part B freeze metadata: results/part_b_freeze.json. Original hash remains 85de8d0a40cb04f00202c73bf11b5e83f9b692618bfda30d1c328e2cf3c3e327. No restricted other-reviewer folders, response letters or joint response were read, even after freezing. No attempt was made to identify the excluded registrant. Four AI subreviews share the inherited backend; they are not external human/cross-model peer review. Codex is GPT-6-based per session instructions; exact serving build/effort is not exposed.

Python 3.12.14 is used here versus the author's 3.13.18. All 35 versions in requirements-lock.txt match; results/computational/package_versions.json records them. The formal build uses pinned Lean 4.35.0 / Mathlib and an openly supplied host-path compatibility shim, described in the report and scripts/lean_proc_compat.c. It changes no proof statements or kernel logic. Do not confuse successful gates with validation of every sentence or empirical calibration.

## Rerunning

Obtain the same pinned repository independently and work on a copy. The exact author commands are recorded per run in results/computational/. Recreate the pinned Python dependencies; use the repository's REPLICATION_README for stage dependencies. The included review scripts read a sibling pinned_snapshot/ (not bundled). run_author_command.py expects a sibling work_pinned/; optional REVIEW_COMMAND_CWD selects its formal/subfolder. compare_reproduced.py compares those snapshots with NaN/array semantics. Our own scripts record deterministic checks or their explicit seeds. export_author_mc_draws.py is an optional wrapper, not evidence that the million-draw job ran here.

complete_computational_review.py checks the frozen Part B hash and requires successful minimum commands before publication. Its inputs, original prompt/response and repository copies must be restored in their recorded relative locations for a full rebuild. Large repository/raw inputs, Lean binaries/dependency caches, capability URLs and downloaded third-party articles are not bundled.

## Scope limits

Read Part C for actual executed stages. A fresh million-draw joint stress test, the entire specification-curve bootstrap, and raw SEC / third-party re-extraction are not automatically established by loading committed outputs or rebuilding tables. Scientific issues survive exact numerical reproduction when they concern source transport, estimands or accounting identities.
