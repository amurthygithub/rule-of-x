#!/usr/bin/env python3
"""Responses to the four outside reviews of the third version, one letter per reviewing model (4 November 2026).

Source of every disposition: notes/reviews/paper1_v3/response_to_outside_reviews.md (verified item by item against the
issue logs in notes/reviews/paper1_v3/author_reviews/*/issue_log.md). Locations there use the numbering of the build of
2-3 November; _locmap.convert() rewrites supplement section numbers to the build of 4 November (main-paper numbers,
theorem, remark, equation and table numbers did not change; checked label by label against the .aux files of the
reviewed build 62e574b, the response build be86d24 and the current build). The stress-test rows are restated with the
values of the million-draw run now in the paper (paper1/stress_macros.tex).
Run from the repository root:  python3 notes/reviews/paper1_v4/make_letters.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
from _locmap import convert  # noqa: E402

RESP = open(os.path.join(ROOT, 'notes', 'reviews', 'paper1_v3', 'response_to_outside_reviews.md'), encoding='utf-8').read()
ST = dict(re.findall(r'\\newcommand\{\\(St[A-Za-z]+)\}\{([^\n]*)\}', open(os.path.join(ROOT, 'paper1', 'stress_macros.tex')).read()))
EX = dict(re.findall(r'\\newcommand\{\\(Ex[A-Za-z]+)\}\{([^\n]*)\}', open(os.path.join(ROOT, 'paper1', 'ext_macros.tex')).read()))
tx = lambda v: v.replace('{,}', ',').replace('$-$', '−').replace('$+$', '+')
MAC = {}
for _f in ('macros.tex', 'stress_macros.tex', 'spec_macros.tex', 'ext_macros.tex'):
    MAC.update(re.findall(r'\\newcommand\{\\([A-Za-z]+)\}\{([^\n]*)\}', open(os.path.join(ROOT, 'paper1', _f)).read()))
P1 = {k: tx(MAC[k]) for k in ('VFirmsEone', 'PsiOpEone', 'PsiCashEone', 'TopFallOpEone', 'TopFallCashEone', 'AnchorN', 'CenRSix',
                               'CenRSixNet', 'HolmTopRW')}


def current_numbers(t):
    """A number quoted just before a macro name, '173% ... (\\PayExitFiveCen)', is set to the macro's current value."""
    def sub(m):
        mac = m.group(3)
        if mac not in MAC:
            return m.group(0)
        v = tx(MAC[mac])
        return m.group(1) + v + m.group(2) + '(\\' + mac + m.group(4)
    return re.sub(r'(^|[^\d.])[-−]?\d[\d.,]*((?:%|\b)[^|()]{0,60}?)\(\\([A-Za-z]+)(\*?\))', lambda m: sub(m), t)


def section_rows(title_start):
    sec = [s for s in re.split(r'\n## ', RESP) if s.startswith(title_start)]
    assert len(sec) == 1, title_start
    rows = []
    for line in sec[0].split('\n'):
        if not line.startswith('| ') or line.startswith('| ID') or line.startswith('|---'):
            continue
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        rows.append(c)
    return rows


ROWFIX = {   # rows whose numbers predate the re-estimation of 3 November (A.4 item 7)
    'call 59 the durable score': 'call the central 2036 score (58 after the re-estimation of 3 November) the durable score',
    'the stored net 2036 score is 54, which GPT-9 now reports': 'the stored net 2036 score (53 after the re-estimation of 3 November) is what GPT-9 now reports',
}


def clean(t):
    for a, b in ROWFIX.items():
        t = t.replace(a, b)
    t = re.sub(r'\s*\.\.\.\s*$', '…', t)
    return current_numbers(convert(t))


STATUS_ORDER = ['Fixed', 'Fixed (3 Nov)', 'Partly', 'Declined', 'Not valid', 'Already handled']


def table(rows):
    out = ['| ID | Your finding (short) | Our assessment | Status | What changed, and where (current numbering) |', '|---|---|---|---|---|']
    for c in rows:
        out.append('| ' + ' | '.join(clean(x).replace('|', '/') for x in c[:5]) + ' |')
    return '\n'.join(out)


def counts(rows):
    n = {}
    for c in rows:
        k = 'Fixed' if c[3].startswith('Fixed') else c[3]
        n[k] = n.get(k, 0) + 1
    return n


STRESS = f"""| ID | Claim as the third version stated it | What the stress test found, and what the text now says |
|---|---|---|
| ST-1 | A cash score of 100 needs market growth above 32.5% a year | Holds at the central cost inputs only. With compute at 6% of revenue and the other costs moved jointly the threshold runs {ST['StGstarCcSixMin']} to {ST['StGstarCcSixMax']}%; over the whole box, {ST['StGstarMin']} to {ST['StGstarMax']}%. The condition is stated wherever the 32.5% appears: "at central costs" in the abstract, "at the central cost inputs" in M 1 and the summary box, "the central cost structure" in M 7.2. S10, Table S18, Figure S1. |
| ST-2 | The 2036 score: 59, interval [54, 62] | [54, 62] is the anchor-sampling interval alone. With every scenario input moved jointly, nine in ten draws lie between {ST['StNetSixPFive']} and {ST['StNetSixPNinetyFive']}, and {ST['StNetSixInPaper']}% fall inside [54, 62]. M 1, the summary box and M 9 say the interval comes "from anchor sampling alone"; the abstract, "from sampling alone". S10, Figure S1. |
| ST-3 | No payback within five years (7.5 years) | Under central execution the payback runs {ST['StPayCenMin']} to {ST['StPayCenMax']} years as the other inputs move; it is below five years only on compute paths that start high and fall steeply. Over the whole box, {ST['StPayMin']} to {ST['StPayMax']} years. The text says "under central execution", with the range (M 1, M 7.3, M 9). New in S12.3: what sets the payback. |
| ST-4 | Cumulative effect negative at three and five years | Under central execution the largest of the four effects is positive only at a few points, by at most {tx(ST['StCumMaxCen'])} point-years; over the whole box by up to {tx(ST['StCumMax'])}. M 1 and M 7.3 say "at all but a few points" and that the statement is for central execution. S10. |
| ST-5 | Less than half of the program realized by 2036 (41%) | 41% under central execution; over the stated execution ranges {ST['StRealMin']} to {ST['StRealMax']}%, above half once change capacity exceeds about {ST['StCapHalf']}% of the program a year. M 1 and M 7.3 say "under central execution", with the range. S10. |
| ST-6 | The growth engine leads the G&A cut at 1 of 6 positions | Holds at the central maintenance base only: over its 90% bootstrap interval the growth engine leads at {ST['StLeverMin']} to {ST['StLeverMax']} positions, and the stated count holds in {ST['StLeverOneShare']}% of the draws. M 7.5 says "at the central maintenance level", with the range. S10. |"""

CHANGES = f"""These are the changes to the paper since the build you read (2 November: main paper 82 pages, supplement 57 pages, repository commit 62e574b). The paper you are asked to look at again is the build of 4 November: main paper 87 pages, supplement 72 pages; the prompt gives the commit.

1. **Hypothesis (H).** Every statement that a value-maximizing firm acts on the marginal value of revenue now says "under (H)" (16 places, including the title of Proposition 2). (H) itself is still not proved; the global qualifier of M 3.6 stays.
2. **Compute share.** The floor of the compute-share range had been set in the wrong units (a cost per dollar of labor used as a share of revenue). It is now stated in revenue units: the cost per completed task times the labor share, 1.2% of revenue. One range, 1.2% to 60% at 2025 prices, is used in the text, the calibration and the stress test. The resulting range of the Rule-of-100 growth threshold is 28% to 78% (M 7.2, Table 4).
3. **Joint-parameter stress test (new S10).** {tx(ST['StDraws'])} Latin-hypercube draws per seed over a box of {ST['StDims']} dimensions, {tx(ST['StCorners'])} corners, a vertex search, Sobol indices on {tx(ST['StSobolN'])} base samples and a second seed. It was run on the author's computer. Of its {ST['StClaimsRows']} tests of headline statements (Table S18), {ST['StClaimsHold']} hold at every evaluated point. Six headline claims hold only under conditions, which the text now states wherever each claim appears (rows ST-1 to ST-6 below). Figure S1 shows the distributions.
4. **Specification curve (new S11).** Each headline empirical claim is tested over all combinations of the paper's analysis choices, written down before any estimate. Also: forward pairing of growth and margin, and leave-one-firm-out.
5. **Sample rule R2 on the whole main sample.** Business descriptions of all 293 core registrants were retrieved, and R2 was applied by the keyword rule fixed in advance: 8 firms and 56 firm-years leave the main sample. Two blind readings on other models serve as a sensitivity (Cohen's kappa 0.95). Every headline statistic was re-estimated with this sample and the corrected capitalized software (item 6); A.4 item 7 lists the values before and after. Among them: {P1['VFirmsEone']} firms (was 292); the slope Ψ0.90 {P1['PsiOpEone']} on GAAP and {P1['PsiCashEone']} on cash (was −0.22 and −0.16); the fall of the 95th percentile {P1['TopFallOpEone']} points on GAAP (unchanged) and {P1['TopFallCashEone']} on cash (was 12.7); the anchor {P1['AnchorN']} firm-years (was 13); the central 2036 score {P1['CenRSix']} (was 59), {P1['CenRSixNet']} after the cost of changes in flight; and the Romano-Wolf p-value of the GAAP decline {P1['HolmTopRW']} (was 0.097). Numbers quoted in the point-by-point rows below that predate this re-estimation can therefore differ from the paper by these amounts.
6. **Data audit.** 40 seeded firm-years were checked against the face statements of the filings the panel used. Capitalized software was read from the filings where company-specific XBRL elements hid it, after a scan of 1,213 firm-years (S7).
7. **Machine-checked proofs (new S4).** The static model is formalized in Lean 4 with Mathlib: 35 theorems, standard axioms only. The formalization found two statements to tighten, both now in the text: σ* = 0 for X ≤ k inside the cap condition of Lemma prop:score, and a measurable moving intercept in Proposition prop:budget (c).
8. **Reproduction from a fresh clone.** The whole pipeline was rerun from a fresh clone (commit 3998b33) in a fresh environment, with the new `code/fetch_raw_data.py` placing the third-party raw data. Data, tables, macros and the main paper matched. Two stale records and four figures whose layout depended on the Python environment were regenerated; the versions are in `requirements-lock.txt`.
9. **Legal and tax citations.** Every legal and tax citation was checked at its primary source: none was incorrect, eight were imprecise, and all eight were fixed.
10. **New S12: three further analyses added after this review round.** These were added at the author's decision on 4 November and answer questions readers asked. (a) How valuations weight growth and margin: public float over revenue on growth and margin, with year effects, firm clusters and a bootstrap of the implied weight. One point of growth is worth about {EX['ExWCash']} points of margin on the cash basis (90% interval {EX['ExWCashLo']} to {EX['ExWCashHi']}), and equal weights are rejected. (b) The cost of not automating, in the paper's pass-through scenario. (c) What sets the payback: change capacity drops out while the program runs, and the share of changes that create value sets it. The one main-text change is the limitations sentence of M 8.6, which now points to S12.1. The public float was retrieved on 3 November with the author's approval (S7).
11. **Abstract.** Rewritten on 4 November in plain language for business readers, at the author's request. The numbers and conditions are the same: the verification hypothesis, the central costs and fixed prices, the compute share and its range, pass-through, a central scenario and not a forecast, the score after the cost of changes in flight, and the anchor-only interval. The selling-spend range of the 2036 score moved out of the abstract and stays in M 1 and M 7.3.
12. **Records.** The four outside reviews and their verification are recorded in A.2 and S8.4 (Table S14). The author's decisions are in Table 8."""

KEY = """| Section | In the build you read | Now |
|---|---|---|
| Further theoretical results; the model; proofs | S1, S2, S3 | S1, S2, S3 (unchanged) |
| Machine-checked proofs of the static model | (none) | S4 (new) |
| Proofs and details for Section 6 (acquired growth) | S4 | S5 |
| The Rule of 1000 | S5 | S6 |
| Data construction and inference | S6 | S7 |
| Protocol records (outside reviews: S8.4, new) | S7 | S8 |
| Full-cost floors and the accountability floor | S8 | S9 |
| Joint-parameter stress test | (none) | S10 (new) |
| Specification curve | (none) | S11 (new) |
| Further analyses added after the third review round | (none) | S12 (new) |
| Glossary | S9 | S13 |
| Supplement tables | S1 to S13 unchanged; errors S14, full-cost floors S16 | errors S15, full-cost floors S17; new S14 (outside-review counts), S18 (stress test), S19 (specification curve), S20 to S22 (S12) |
| Main paper | Sections 1 to 9, Appendix A (A.1 to A.6), Tables 1 to 8 | Same numbers; Table 8 has new rows for the decisions taken since |

Main-paper section, table, theorem, remark and equation numbers are unchanged, and so are the supplement's theorem, remark and equation numbers."""

MODELS = {
    'deepseek': dict(
        name='DeepSeek V4 Pro (high effort)', sec='DeepSeek V4 Pro', folder='deepseek_v4_pro_high',
        verdict='"No demonstrated error was found"; accept for release as a working paper with minor corrections, and minor revision at a specialist field journal contingent on (a) proving or re-scoping hypothesis (H) and (b) human specialist sign-off on the tax, regulatory and scenario-parameter claims.',
        intro="""Your review reproduced every headline number you re-derived, confirmed the theory you checked and found no error in the theorems, the estimates, the case study or the regulatory claims. We verified each of your 70 findings, plus two defects (X-1, X-2) found during that verification that no review had raised. Your two conditions are where the paper moved most:

- **(H):** We took your option (ii). "Under (H)" now appears at each of the 16 decision-weight statements (DS-17). (H) is still not proved, and the paper says so in M 3.6.
- **Specialist sign-off:** No human specialist has read the paper. In its place, every legal and tax citation was checked at its primary source (item 9 below), the scenario parameters were stress-tested jointly (S10), and the static theory was machine-checked in Lean 4 (S4). A human specialist's reading before journal submission is still advisable, and A.6 says what the protocol does not establish.

Six of your findings we classify as not valid; each is explained in the table. Please contest any of them you think we have wrong.""",
        recheck=['DS-17: "under (H)" at the 16 places itemised in the row (count them in the current sources)',
                 'DS-35, DS-37, DS-38: the bibliography and citation fixes',
                 'DS-65, DS-67, DS-68: the acquirer case against the filings now in `data/v3_inputs/raw/` (hashes in `README_retrieval.md`, section 5)',
                 'DS-13, DS-21, DS-34, DS-39, DS-40, DS-59: our reasons for classifying these as not valid',
                 'X-1, X-2: the two defects found during verification',
                 'The new S4 (machine-checked proofs) against the theorems you checked by hand, and S12']),
    'gpt': dict(
        name='GPT-6.2 Sol (extra-high effort)', sec='GPT-6.2 Sol', folder='gpt_6_2_sol_xhigh',
        verdict='Major revision: "a promising analytical synthesis ... rather than an identified estimate of the economic limits of AI", with six majors (M1 to M6) and narrow proof, wording, citation and transport items.',
        intro="""Your six major findings shaped this revision more than any other review's. We verified each of your 43 findings. All six majors led to changes:

- **M1:** The exact mapping of the cone statistic through the growth distribution replaces the "dense sample" approximation (M 3.7, S2.3).
- **M2:** The tax shield is labelled as a present-value equivalent, not period cash (Remark 2, Table 4).
- **M3:** The acquired-growth identity is stated in run-rate units, with annual rates under their own symbols (M 6, Definition 5).
- **M4:** "Would not fund" became "fails a five-year cash-payback test", with the value of the remaining benefits to an owner who sells (M 1, M 7.3, M 8.2).
- **M5:** The execution path is now bounded jointly by the stress test (S10).
- **M6:** Two of its parts are only partly met:
  - **Tail support:** We added leave-one-firm-out for the consequential cells, the P95 changes, the slopes and the anchor (S11).
  - **Replication access:** Last time the repository was private and returned 404 to you, so no table could be reproduced (GPT-34). This time the package includes a frozen archive of the repository at the commit named in the prompt, so you can run the pipeline yourself.

Two of your findings we classify as not valid (GPT-36, GPT-37); each is explained in the table.""",
        recheck=['M1 to M6 against the rows below; in particular whether M1\'s exact mapping and its multiplier range (2.1 to 4.0 under E1) are right',
                 'GPT-34 and the rest of M6: you can now run the pipeline (`code/regenerate_all.sh`, `code/REPLICATION_README.md`); please reproduce at least the empirical tables and the stress-test table',
                 'GPT-16: the leave-one-firm-out results in S11',
                 'GPT-24 and the stress test (S10): whether the conditional wording of ST-1 to ST-6 is now right everywhere it appears',
                 'GPT-36, GPT-37: our reasons for classifying these as not valid',
                 'S12, new: in particular the valuation regression in S12.1 and its comparison with the paper\'s screening weight']),
    'glm': dict(
        name='GLM 5.3 (high effort)', sec='GLM 5.3', folder='glm_5_3_high',
        verdict='Major revision, "with acceptance expected once the four must-fix items and the Phase-2 one-liners are executed": five majors (F1 to F4 must-fix, F5 should-fix) and eighteen minors; "No theorem is false; no number in any table is wrong".',
        intro="""Your review was the one that re-ran the full pipeline, including the 999-replication bootstrap, and its confirmations of the static theory, the Proposition 2 numerics and all 164 cells of Table 2 stand. We verified each of your 46 findings.

All four must-fix items and the should-fix item are fixed:

- **F1:** Six sentences now describe the worked decision weight as U-shaped.
- **F2:** The availability sentences of Section 6 are corrected to what the acquirer's filings disclose, and Table 3's annual organic rows are filled.
- **F3:** Nei, Ruus and Indov (2026) is cited, and "only" is dropped.
- **F4:** The leftover marker in A.6 is gone.
- **F5:** M 5.1 now states the consequence of the post hoc family, with 18-test Holm values.

Three items were declined:

- **GLM-M17:** The author decided to keep the unsalted digest, and the paper states that the excluded registrant can be identified from it.
- **GLM-11:** The stock-constrained fast case was not computed. The stress test varies change capacity over its range, and the new S12.3 adds a related result: change capacity drops out of the payback while the program runs.
- **GLM-16:** No AI-auditing citation was added, because no specific antecedent was proposed.

Three items were only partly met (GLM-M16, GLM-10, GLM-18), and two we classify as not valid (GLM-M14, GLM-22). Each is explained in the table.""",
        recheck=['F1 to F5 against the rows below',
                 'GLM-M9: the forward-pairing variant now computed in S11',
                 'GLM-M11: the compute-share floor, now in revenue units (item 2 below), which you flagged',
                 'The declined and partly met items: whether our reasons hold',
                 'A rerun of your full bootstrap replication on the current commit: R2 now applies to the main sample, and capitalized software was corrected, so several values moved (A.4 item 7 lists them)',
                 'S12, new']),
    'mistral': dict(
        name='Mistral Large 4 (high effort)', sec=None, folder='mistral_large_4_high',
        verdict='Accept with minor revisions for the working-paper track: "technically sound in everything I could check"; eight findings (none an error in the paper), minor items, five editorial repairs and an eight-step revision sequence.',
        intro="""Your review arrived a day after the other three and set the acceptance tests that drove several of the changes:

- **Classify every registrant by its business description:** done (F-2).
- **Run a solver-independent check of the HJB profile:** done, as a lower bound (F-6, Ed-4).
- **Reproduce the whole pipeline independently:** done from a fresh clone in a fresh environment (RS-7).
- **Check the legal and tax citations at their primary sources:** done (M-8, Ed-5, RS-6).

We verified each of your findings. Two we classify as not valid, though each still led to a change:

- **F-6:** The solvers that returned the no-spend solution discount at r rather than r − G and stop after about six years of horizon. A simple admissible spend policy beats no-spend (v/s 9.02 against 5.83), and that bound is now a check in `code/verify_theory.py` (check 15q).
- **Empirical 7:** The paper's own specification reproduces the printed within-firm slopes from the shipped panel. The trim of growth at 150% that the code applies is now stated in Section 5.""",
        recheck=['F-2: R2 on the whole main sample, its two blind readings, and the re-estimated headline values (A.4 item 7)',
                 'F-6 and Ed-4: check 15q of `code/verify_theory.py` and whether it settles your concern',
                 'RS-7: a reproduction of your own on the current commit, if you can run it',
                 'RS-2: the caption of Table 4 and the 28 to 78% range',
                 'S4, S10, S11 and S12, all new since your review']),
}

MISTRAL_ROWS = [
    ['F-1', '(H) is unproved and carries the "firm\'s own weight" claim; correctly disclosed', 'Valid; already handled', 'Already handled', '"Under (H)" at the 16 decision-weight statements (round 3, DS-17); the abstract says "under a verification hypothesis".'],
    ['F-2, Ed-3, RS-4', 'R2 applied only to the 16 named firms; acceptance test: classify all registrants by business description and rerun the headline statistics', 'Partly valid', 'Fixed', 'Descriptions of all 293 core registrants retrieved (3 Nov; `data/v3_inputs/README_retrieval.md`, section 6); R2 applied to the main sample by the keyword rule fixed in advance (8 firms, 56 firm-years out); two blind readings on other models as a sensitivity (Cohen\'s kappa 0.95), rows of Table S4; every headline value re-estimated, before and after in A.4 item 7; M 4.2, S7.'],
    ['F-3, M-1, Ed-1, RS-5', 'The abstract\'s 2036 sentence lacks the scenario caveat', 'Already handled', 'Already handled', 'The abstract says "On a central scenario, not a forecast".'],
    ['F-4, M-2, Ed-2, RS-3', '`data/panel_v3.csv` carries the v2 flag `acq_flag` and the v3 flag `acq_flag_v3`; reusing `acq_flag` gives a different anchor', 'Valid', 'Fixed', 'The column to use is named in S7 (Reproducibility) and `code/REPLICATION_README.md`. After the re-estimation the anchor has 15 firm-years (8 firms) with `acq_flag` and 14 (7) with `acq_flag_v3`.'],
    ['F-5', 'The accountability floor operationalizes a legal standard with a scenario probability; arithmetic exact', 'Valid; no change', 'Already handled', 'The paper calls the threshold a judgment and a scenario value and reports both 5% and 1%.'],
    ['F-6', 'The reviewer\'s solvers could not reproduce the HJB profile (v\' 9.1, 7.2, 5.4) and returned the no-spend solution', 'Not valid (reviewer\'s solvers); the request for a solver-independent check is reasonable', 'Not valid', 'One solver discounts at r instead of r − G and stops after about six years; the other returns the no-spend value everywhere. A policy spending 5% of revenue until the share reaches 0.4 is worth v/s 9.02 at s0 = 0.01 and 7.33 at s0 = 0.1, against 5.83 for no spend, so no-spend is not optimal. Added: check 15q of `code/verify_theory.py` (202/202 pass) and a note in `code/REPLICATION_README.md`.'],
    ['F-7', 'Growth-rate conventions in the extreme-score passages', 'Valid; no change', 'Already handled', 'The conventions are labelled where it matters (S2.1).'],
    ['F-8', 'The four estimands share most firm-years; keep the "292 software firms" phrasing', 'Valid; already handled', 'Already handled', 'The paper calls them a sensitivity set, not four independent replications.'],
    ['M-3', 'The familywise families contain uninformative members', 'Already handled', 'Already handled', 'M 5.1 adds the 18-test family (GLM-F5) and says such survivals say little.'],
    ['M-4', 'Interest and taxes paid come from SEC frames (latest filed)', 'Already handled', 'Already handled', 'Disclosed in S7.'],
    ['M-5, M-6, M-7', 'Process candour; macros idempotent; exclusion irreversible and disclosed', 'Valid; no change', 'Already handled', 'None needed.'],
    ['M-8, Ed-5, RS-6', 'Citations not re-verifiable from the reviewer\'s environment; primary-source pass of the 2025-26 legal and tax items', 'Partly valid', 'Fixed', 'Primary-source pass of every legal and tax citation (`notes/legal_primary_source_pass_2026-11-03.md`): none incorrect, eight imprecise, all fixed; the IRS release number and date confirmed. A specialist\'s reading before journal submission is still advisable.'],
    ['Empirical 7', 'Within-firm slopes: reviewer +0.083 / lead −0.112 / cash −0.009 against printed +0.06 / −0.03 / −0.03', 'Not valid (reviewer\'s specification)', 'Not valid', 'The paper\'s specification reproduces the printed values from the shipped panel (+0.059, −0.034, −0.032). The trim of growth at 150% that the code applies was not stated; it now is (Section 5). Dropping it changes little (+0.068, −0.038, −0.019).'],
    ['Ed-4, RS-1', 'The grid solution may be one of several solutions of the singular ODE; add a solver-independent check', 'Partly valid', 'Fixed', 'The singular point and the free constant are stated (S3, proof of Proposition 2); the policy bound of F-6 is the solver-independent check.'],
    ['RS-2', 'Compute-share caveat in the abstract and on the ceiling table; "28 to 78"', 'Partly valid', 'Fixed', 'The caption of Table 4 says the compute share is a scenario value that no source measures; the floor\'s units are corrected (1.2% of revenue, not 2%), so the threshold range is 28 to 78%. The abstract already states the condition on the compute share.'],
    ['RS-7', 'Independent full-pipeline reproduction', 'Valid', 'Fixed', 'Done (3 Nov) from a fresh clone of commit 3998b33 in a fresh environment, with the third-party raw data placed by the new `code/fetch_raw_data.py`; data, tables, macros and the main paper matched; two stale records and four environment-dependent figures were regenerated; `requirements-lock.txt` (`notes/reviews/paper1_v3/audit_2026-11-03_revision.md`, F1).'],
    ['RS-8', 'Keep the post hoc choices in Appendix A', 'Valid; no change', 'Already handled', 'A.4 lists them.'],
]


def letter(key):
    m = MODELS[key]
    rows = MISTRAL_ROWS if key == 'mistral' else section_rows(m['sec'])
    n = counts(rows)
    tally = ', '.join(f"{n[k]} {k.lower()}" for k in ('Fixed', 'Partly', 'Declined', 'Not valid', 'Already handled') if n.get(k))
    rc = '\n'.join(f'{i}. {t}' for i, t in enumerate(m['recheck'], 1))
    first = ("Mistral's findings are numbered as in your report (F, M, Ed, RS); items that repeat one another are grouped in one row."
             if key == 'mistral' else
             'The finding column is the short form of your finding from the issue log; the full text, our evidence and the proposed fix are in the issue log.')
    return f"""# Response to your review of *The Rule of 40 as a Price Line* (third version)

**To:** {m['name']}
**From:** Akshaya Bangalore Sreenivasa Murthy (author), with the lead agent of the research session
**Date:** 4 November 2026
**Your review:** of the build of 2 November 2026 (main paper 82 pages, SHA-256 bd87f45f…; supplement 57 pages, acf9d62b…) and the repository at commit 62e574b
**Your verdict:** {m['verdict']}

Thank you for the review. {m['intro']}

**How we handled it.** Each finding was verified in the research session against the paper's sources, the code (re-run on clean exports of the commit you read), the stored outputs and primary sources. We classified each as valid, partly valid, not valid (a reviewer error) or already handled. The author then adopted every fix the verification supported (2 November, 23:23, and 3 November; Table 8). Our evidence for each finding, including the scripts we ran, is in `notes/reviews/paper1_v3/author_reviews/{m['folder']}/` (`issue_log.md` and `verification_claude/`). The joint response to all four outside reviews is `notes/reviews/paper1_v3/response_to_outside_reviews.md`. This letter is self-contained, but it uses that file's dispositions.

**Your findings, by status:** {tally} ({len(rows)} rows). *Fixed* means changed as the issue log proposes, in the paper, the code, the data or the repository; *Partly* means part of the proposal was applied, and the row says what was not and why; *Declined* means deliberately not applied, with the reason; *Not valid* means we think the finding is mistaken, so nothing changed; *Already handled* means the paper already did what was asked, or the item was a confirmation.

## What we would most like you to check

{rc}

## What changed in the paper since your review

{CHANGES}

## Point by point

{first} Locations: M = main paper, S = Supplementary Appendix, A = the main paper's Appendix A, all in the current numbering (key at the end). Numbers quoted in a row are those of the revision at the time; where a later rerun moved one, the paper is authoritative.

{table(rows)}

## The joint-parameter stress test (ST-1 to ST-6)

The stress test was added in this round, partly in answer to the reviews' requests for a joint envelope of the scenario inputs. Six headline claims hold only under conditions; the text now states each condition where the claim appears. The values below are those of the million-draw run now in the paper.

{STRESS}

## Numbering key

{KEY}
"""


if __name__ == '__main__':
    for k in MODELS:
        p = os.path.join(HERE, f'response_{k}.md')
        open(p, 'w', encoding='utf-8').write(letter(k))
        print('wrote', os.path.relpath(p, ROOT))
