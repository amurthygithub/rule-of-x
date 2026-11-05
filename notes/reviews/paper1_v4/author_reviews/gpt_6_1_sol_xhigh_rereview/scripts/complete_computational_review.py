"""Publish the post-access review without changing the frozen independent Part B."""
from pathlib import Path
from collections import Counter
import csv, hashlib, json, shutil
from zipfile import ZipFile, ZIP_DEFLATED

R=Path(__file__).resolve().parents[1]
O=R/'output';O.mkdir(exist_ok=True)
FROZEN='85de8d0a40cb04f00202c73bf11b5e83f9b692618bfda30d1c328e2cf3c3e327'
b=(R/'part_b_frozen.md').read_bytes()
assert hashlib.sha256(b).hexdigest()==FROZEN
rows=json.loads((R/'audit_verdicts.json').read_text())
assert len(rows)==49
statuses={}
for line in (R/'RESPONSE.md').read_text().splitlines():
    if line.startswith('| GPT-'):
        p=[x.strip() for x in line.strip().strip('|').split('|')];statuses[p[0]]=p[3]
for i in range(1,7):statuses[f'ST-{i}']='Conditional qualification supplied'
audits=[dict(zip(['id','our_status','your_verdict','evidence','locator'],[i,statuses[i],v,e,l])) for i,v,e,l in rows]
counts=Counter(x['your_verdict'] for x in audits)
with (R/'response_audit.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['id','our_status','your_verdict','evidence','locator']);w.writeheader();w.writerows(audits)
author_runs=[]
for p in sorted((R/'results/computational').glob('*/run.json')):
    author_runs.append(json.loads(p.read_text()))
assert all(x['status']=='completed' for x in author_runs), 'Do not publish while a recorded job is running.'
minimum=['verify_theory','paper1_macros','supp_extensions_complete','build_paper1']
assert all(any(x['name']==n and x['exit_code']==0 for x in author_runs) for n in minimum)
snapshot=json.loads((R/'results/computational/snapshot_integrity.json').read_text())
assert not snapshot['bad']
computational=(R/'computational_addendum.md').read_text()
original=(R/'rereview_report.md').read_text()
sources=original[original.index('## Primary sources and access record'):]
sources=sources.split('\n## Post-access')[0]

verdict=f'''**Recommendation: targeted major revision before public release; not yet ready for a specialist journal.** The repository-access objection is resolved. All four required commands now pass on the pinned unmerged code, and their regenerated text outputs match the committed files; rebuilt PDFs have identical extracted text. The review sustains three major and fourteen minor manuscript findings, chiefly overbroad necessity/rent claims, the ownership-cost source conversion, and local inference/counterfactual defects. Of 49 response/stress-test rows, {counts['resolved']} are resolved and {counts['partly resolved']} partly resolved; no row remains unresolved solely for lack of repository access. Reproducing a numerical output does not validate its interpretation or external calibration. The expanded computational outcomes and remaining limits are stated in Part C; the original independently frozen Part B is retained with a clearly marked evidence update.'''
intro='''# Re-review: The Rule of 40 as a Price Line

Revised third version supplied 4 November 2026 | Review and computational update: 4 November 2026 America/Los_Angeles (5 November UTC)

## Scope, evidence and independence

The attached main paper (87 pages) and supplement (72 pages) remain authoritative for claims. The private repository is now accessible through the personal connection. This review uses commit `eb7537bee7585f2902304f62a722edea6ced8539`, named in the re-review prompt, on branch `review-round-3`; it does not review an older default-branch build. The observed branch head `786228da26e12235a9d0c7aa53f2ef1fde3c07bf` is one commit ahead and changes only `notes/reviews/paper1_v4/rereview_prompt.md`. Its program/data contents therefore equal the pinned revision. That comparison inspected file metadata, not restricted review contents. Nothing was merged or written to GitHub.

Four AI specialists reviewed mathematical theory/formalization, empirical methods, execution/stress tests, and controls/finance units/primary sources, followed by root adjudication. They use the same inherited backend and are not independent human or cross-model referees. Runtime disclosure: Codex, GPT-6-based per session instructions; exact serving build and configured effort are not exposed. The prompt's GPT-6.2 Sol (extra-high) address is not asserted as runtime fact.

The independent PDF-based Part B was completed and frozen before code became accessible. Its SHA-256 remains `85de8d0a40cb04f00202c73bf11b5e83f9b692618bfda30d1c328e2cf3c3e327`. No other-reviewer folders, other response letters or joint response were read before or after the freeze. The subsequent source inspections and reruns are separately identified, preserving the original record rather than silently rewriting it. No attempt was made to identify the excluded registrant. Author programs ran only on an isolated working copy; an independently hashed baseline was retained.

## Part A. Response audit, updated after code access

All 43 point-by-point rows and ST-1–ST-6 are included below and in response_audit.csv. “Resolved” applies to the specific objection and evidence level in that row; it does not certify every stronger use of the result. The author's status is preserved. ST rows have no status field in the response, so they are marked “Conditional qualification supplied”.

The response warns that some numbers predate the final run. The reviewed PDFs use 1,732 / 1,330 firm-years and p_RW = .075 with three of four GAAP comparisons significant at 10%; old counts and .097 are not treated as current errors.

'''
table='| ID | Author status | Verdict | Evidence | Locator |\n|---|---|---|---|---|\n'
for a in audits:
    table+='| '+' | '.join(str(a[k]).replace('|','/') for k in ['id','our_status','your_verdict','evidence','locator'])+' |\n'
letter='''
### Broader response claims

| Claim | Independent assessment |
|---|---|
| Mathematical repairs and (H) | Written proof review supports the repairs; M1's eight numerical pairs now reproduce to 1e-10. Dynamic existence/regularity is still assumed and disclosed. Static formal scope is assessed separately from dynamic existence. |
| R2 applied to the whole main sample | Code does apply the keyword rule to all covered descriptions. That partial rule does not establish that all 284 retained registrants principally sell software; F17 remains. |
| Bootstrap, deletion and specification sensitivity | The actual source implements firm-cluster resampling and all-firm deletion. Published counts reconcile. Full-bootstrap and specification-grid execution scopes are distinguished in Part C; source inspection alone is not called a rerun. |
| Joint stress test rerun | The stored million-draw inputs are now accessible and feed a successful S12 rebuild; the stress mirror check runs here. Fresh million-draw/corner/Sobol/search execution is not claimed. F05 concerns precision justification, not a demonstrated change in the central scenario band. |
| S12 added and audited | Valuation and do-nothing analyses are rerun here, and the supplement generator passes. The valuation NaN/censoring chain and price-growth omission are confirmed by actual code; a passing gate does not resolve them. |
| Fresh-clone build matches | Our pinned file bytes were independently checked against Git blob IDs. Source PDFs equal the supplied attachments. The four required commands pass and the rebuilt PDF text matches. This is our evidence, separate from the author's earlier reproduction claim. |
| Lean: 35 theorems / standard axioms | Source correspondence and build results are reported separately in the addendum and Part C. No author/reviewer assertion substitutes for those checks. |
| Capitalized-software and filing audit | Committed audit inputs/results are accessible and the empirical program uses them. We do not claim a fresh re-extraction of every SEC filing or a complete independent audit of all 234 compared values. |
| Legal/tax/citation repairs | Targeted primary-source checks support the repaired characterizations and qualifications, subject to access limits below. This is not an exhaustive bibliography audit. |
| Abstract preserves every condition | It retains many key conditions, but F01/F15/F17 remain. The conclusion's necessity claims and ownership conversion require substantive revision. |
| Rejected GPT-36/GPT-37 | Accept the narrow current-text and rounding responses. Reporting 450 generated pairs does not itself assert 450 independent transcripts; rounded inputs cannot refute an exact net score. Old-build historical provenance remains distinct from this current-build reproduction. |

'''
frozen_banner='''
**Preserved independent assessment.** The following Part B is the exact text frozen before repository access. Its statements about unavailable code describe that stage of the review and are superseded by the post-access addendum and current Part C. Its hash has not changed.

'''
c='\n## Part C. Computational reproduction\n\n'
c+='| Run | Seconds | Exit | Scope |\n|---|---:|---:|---|\n'
for x in author_runs:
    scope='Author program, isolated pinned copy'
    if x['name']=='supp_extensions':scope='Initial partial materialization; optional heatmap comparison absent; superseded by complete rerun'
    if x['name']=='mc_verify_only':scope='Stress/calibration mirrors; no fresh million draws'
    if x['name'].startswith('lean_'):scope='Pinned Lean target; see compatibility disclosure'
    c+=f"| {x['name']} | {x['elapsed_seconds']:.3f} | {x['exit_code']} | {scope} |\n"
c+='''
Exact commands, environments, UTC timestamps, stdout/stderr and exit codes are in results/computational/<run>/run.json and companion logs. Review programs and seeds are bundled under scripts/ and results/. Detailed comparisons, numerical tolerances and remaining limits follow in the post-access addendum; no unrun stage is inferred successful from a different stage.

'''
c+=computational
d='''
## Part D. Verdict and ranked revision sequence

### arXiv working paper

Hold this build for targeted major corrections, then release as conditional research. Repository access and the minimum computational suite are no longer release blockers. Required revisions, ranked:

1. Correct the rent-versus-accounting-score and technology-necessity claims (F01/F02), preserving homogeneous-product, cost, capital, growth and replication assumptions across abstract, executive summary and conclusion. Repair abstract capital/sample wording (F15/F17).
2. Rebuild ownership costs on consistent asset-stock, replacement-cash, running-cost and value units, or remove the unsupported numerical ownership hurdles (F03). A source-to-capital conversion is not validated by checking algebra conditional on that conversion.
3. Reconcile the S12 price–quantity–revenue counterfactual and its score levels; define valid weak-denominator ratio inference, reject NaN, and revise the LHS/QMC precision claims (F04/F08/F05). The all-year descriptive valuation association is not overturned by our diagnostic.
4. Repair interest-interval levels, non-steepening/completion/payback language and the remaining parameter/support/control/failure-cost qualifications (F06/F07/F09–F14/F16). Publish distinct-firm counts; our E1 counts do not show reliance on only a handful of clusters.
5. Rebuild and rerun the gates after these scientific changes, then compare all affected outputs. Extend the computation to the full specification/stress/raw-source pipeline if claiming independent reproduction of those stages. State each remaining scope limit accurately.

### Specialist field journal

Major revision remains; the present evidence is not submission-ready. The static conditional synthesis and descriptive growth–margin evidence may be useful, but the contribution should be positioned against prior growth–profit frontier and valuation theory. Decide whether the empirical section describes chosen operating points, tests a structural mechanism or estimates actual attainable limits. The current design principally supports the first. Specification curves and broader simulations do not identify a structural weight, a causal automation payoff or a real enterprise minimum cost.

For stronger claims, prioritize validated business-population classification; outcome-blind acquisition/capitalized-software measurement; adequate independent tail support; a well-defined valuation estimand and ratio confidence set; and representative accepted-task, failure/recovery, maintenance, oversight and utilization costs. Distinguish a conditional scenario from an estimated enterprise/economy forecast. These requirements concern stronger scientific claims, not a demand that a working paper forecast individual firms precisely.

'''
report=verdict+'\n\n'+intro+table+letter+frozen_banner+b.decode()+'\n'+c+d+sources
(R/'rereview_report.md').write_text(report)
inputs=[]
for name in ['paper1.pdf','supplement.pdf','RESPONSE.md','PROMPT.md','MANIFEST.txt']:
    p=R/name;inputs.append(f'|{name}|{p.stat().st_size}|{hashlib.sha256(p.read_bytes()).hexdigest()}|')
uploaded_archive=R.parent/'upload/rereview_gpt.zip'
if uploaded_archive.is_file():
    inputs.append(f'|upload/rereview_gpt.zip|{uploaded_archive.stat().st_size}|{hashlib.sha256(uploaded_archive.read_bytes()).hexdigest()}|')
readme=f'''# Re-review package: computational update

Review date 4 November 2026 America/Los_Angeles (5 November UTC). Parts A–D and all 49 audit rows are included. All four minimum author commands pass on the pinned unmerged code. See Part C for optional runs, exact limits and differences.

## Contents

- rereview_report.md: verdict, updated response audit, preserved independent Part B, computational addendum, ranked recommendations and source-access record.
- response_audit.csv: exact requested columns; {dict(counts)}.
- part_b_frozen.md: immutable pre-access assessment, SHA-256 {FROZEN}.
- scripts/ and results/: our reproducible checks, execution wrappers, seeds, output comparisons and full command logs.
- expert_notes/: complementary specialist notes, clearly distinguishing PDF review, code inspection and root-run evidence.
- source/audit_verdicts.json and source/computational_addendum.md: inputs used to assemble the current report.

## Inputs and provenance

|Input|Bytes|SHA256|\n|---|---:|---|\n{chr(10).join(inputs)}

The four member hashes match MANIFEST.txt. Pinned repository PDFs equal the supplied PDFs byte for byte. Requested repository commit: eb7537bee7585f2902304f62a722edea6ced8539, branch `review-round-3`. Observed unmerged head 786228da26e12235a9d0c7aa53f2ef1fde3c07bf changes only the prompt, not code/data. {snapshot['verified_count']} selected repository files were validated against their Git blob IDs; this is a selected source/data snapshot, not a claim to have downloaded all 1,015 tree entries. The separately named repository.zip was not supplied and its archive hash is not asserted. No remote repository was modified or merged.

## Independence and runtime

Part B freeze metadata: results/part_b_freeze.json. Original hash remains {FROZEN}. No restricted other-reviewer folders, response letters or joint response were read, even after freezing. No attempt was made to identify the excluded registrant. Four AI subreviews share the inherited backend; they are not external human/cross-model peer review. Codex is GPT-6-based per session instructions; exact serving build/effort is not exposed.

Python 3.12.14 is used here versus the author's 3.13.18. All 35 versions in requirements-lock.txt match; results/computational/package_versions.json records them. The formal build uses pinned Lean 4.35.0 / Mathlib and an openly supplied host-path compatibility shim, described in the report and scripts/lean_proc_compat.c. It changes no proof statements or kernel logic. Do not confuse successful gates with validation of every sentence or empirical calibration.

## Rerunning

Obtain the same pinned repository independently and work on a copy. The exact author commands are recorded per run in results/computational/. Recreate the pinned Python dependencies; use the repository's REPLICATION_README for stage dependencies. The included review scripts read a sibling pinned_snapshot/ (not bundled). run_author_command.py expects a sibling work_pinned/; optional REVIEW_COMMAND_CWD selects its formal/subfolder. compare_reproduced.py compares those snapshots with NaN/array semantics. Our own scripts record deterministic checks or their explicit seeds. export_author_mc_draws.py is an optional wrapper, not evidence that the million-draw job ran here.

complete_computational_review.py checks the frozen Part B hash and requires successful minimum commands before publication. Its inputs, original prompt/response and repository copies must be restored in their recorded relative locations for a full rebuild. Large repository/raw inputs, Lean binaries/dependency caches, capability URLs and downloaded third-party articles are not bundled.

## Scope limits

Read Part C for actual executed stages. A fresh million-draw joint stress test, the entire specification-curve bootstrap, and raw SEC / third-party re-extraction are not automatically established by loading committed outputs or rebuilding tables. Scientific issues survive exact numerical reproduction when they concern source transport, estimands or accounting identities.
'''
(R/'README.md').write_text(readme)
bundle=O/'Rule_of_40_ReReview_20261104.zip'
with ZipFile(bundle,'w',ZIP_DEFLATED) as z:
    prefix='Rule_of_40_ReReview_20261104/'
    for n in ['rereview_report.md','response_audit.csv','README.md','part_b_frozen.md']:
        z.write(R/n,prefix+n)
    for folder in ['scripts','results','expert_notes']:
        for p in sorted((R/folder).rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and not any(part.startswith('pdf_build') for part in p.parts):
                z.write(p,prefix+str(p.relative_to(R)))
    for n in ['audit_verdicts.json','part_b_draft.md','computational_addendum.md']:
        z.write(R/n,prefix+'source/'+n)
with ZipFile(bundle) as z:assert z.testzip() is None
shutil.copy2(R/'rereview_report.md',O/'Rule_of_40_ReReview_20261104.md')
shutil.copy2(R/'response_audit.csv',O/'Rule_of_40_Response_Audit_20261104.csv')
print(json.dumps({'audit_counts':dict(counts),'report_words':len(report.split()),'bundle_bytes':bundle.stat().st_size,'frozen_hash':FROZEN},indent=2))
