# Removal of one registrant at the author's request (2 Nov 2026)

The author asked that every piece of data about one SEC registrant be removed from the repository. The registrant (SIC 7374) was
in the broad universe only, not in the 292-firm core sample. This note does not name it or give its CIK; the code identifies it
only by the SHA-256 digest of its decimal CIK (`code/exclusions.py`).

## 1. Exclusion in code

- `code/exclusions.py` defines `EXCLUDED_CIK_SHA256` once ("registrant excluded at the author's request"), with `is_excluded(cik)`
  (int, integral float or decimal string, zero-padded or not) and `drop_excluded(df)`.
- Applied in every script that fetches or builds a universe or panel:
  - `code/fetch_companyfacts.py`: the fetch list;
  - `code/retrieval_browser.js`: the embedded CIK list was re-encoded without the registrant, and the script drops any CIK whose
    digest is in a copy of the set before making a request; `purge_excluded.py --check` checks that the copy equals the Python set;
  - `code/extract_browser_payload.py`: CIK-keyed payloads;
  - `code/growth_from_filings.py`, `code/build_panel.py`, `code/build_panel_v2.py`, `code/build_panel_v3.py`: companyfacts,
    SIC universe, frames and panels;
  - `code/data_part2/common.py` gained `read_sec_panel()`, which `05_function_priors.py`, `08_params.py` and `11_nonsoftware_priors.py`
    now use to read `data/panel_v2_all.csv`;
  - `code/validation/backtest.py`: the firm panel;
  - `code/playbook/archetypes.py`: `load_core_panel_v2`, which rebuilds the v2 core sample from `panel_v2_all.csv`;
  - `code/make_arxiv.py`: ships `exclusions.py` and `purge_excluded.py` in the replication package, and purges the copied data.
- `code/purge_excluded.py` removes the registrant from the data files on disk, editing each file in its own structure, and with
  `--check` reports anything left. It checks CSV rows, JSON keys and list entries, CIK lists, the delta-encoded base-36 lists, the
  hexadecimal growth-fetch list, the list in the browser script, and the data members of `dist/replication_package.zip`. Each JSON
  file is re-serialized with the setting that reproduces its original bytes; the script stops if none does.
- The rebuild cannot bring it back, as two tests show:
  - In a scratch copy, every panel was rebuilt from the pre-removal inputs, the registrant included. The rebuilt files are
    byte-identical to the purged ones: `growth_filing.csv`, `panel_all.csv`, `panel_v2_all.csv`, `panel_broad.csv`, `panel.csv`,
    `panel_v3_all.csv`, `panel_v3_core_full.csv`, `panel_v3.csv` and `notes/panel_v3_build.json`. A rebuild from the purged inputs
    gives the same files.
  - The browser script was run under node with its CIK added back to the list and a stub fetch. It made 661 requests, none of them
    for that CIK.

## 2. What was removed

| File | Removed | Before → after |
|---|---|---|
| `data/sic_universe.json` | 1 list entry | 3,641 → 3,640 entries |
| `data/frames_universe.json` | 165 inner entries (one per concept-year frame) | 126,333 → 126,168 entries; every frame key kept |
| `data/frames_extra.json` | 27 inner entries | 14,558 → 14,531 |
| `data/companyfacts_ciks.txt` | 1 line | 662 → 661 |
| `data/companyfacts_extract.json` | 1 key (9 filings, 414 facts) | 662 → 661 firms; 240,732 → 240,318 facts |
| `data/companyconcept_revenue.json` | 2 keys | 789 → 787 |
| `data/growth_filing.csv` | 9 rows | 4,136 → 4,127 |
| `data/panel_all.csv` | 10 rows | 9,517 → 9,507 |
| `data/panel_v2_all.csv` | 10 rows | 5,688 → 5,678 |
| `data/panel_broad.csv` | 7 rows (FY2015–21) | 3,626 → 3,619 |
| `data/panel_v3_all.csv` | 10 rows | 5,688 → 5,678 |
| `data/cik_delta_b36.txt` (delta-encoded base 36) | 1 entry | 3,641 → 3,640 |
| `data/cf_fetch_list.txt` (delta-encoded base 36) | 1 entry | 662 → 661 |
| `data/growth_fetch_list.txt` (hexadecimal) | 1 entry | 579 → 578 |
| `code/retrieval_browser.js` (embedded list) | 1 entry | 662 → 661 |
| `dist/replication/data/`: `sic_universe.json`, `companyfacts_ciks.txt`, `companyfacts_extract.json`, `panel_v2_all.csv`, `panel_broad.csv` | 1, 1, 1, 10, 7 | as in `data/` (byte-identical to the purged `data/` files) |
| `dist/replication/code/retrieval_browser.js` | 1 entry | 662 → 661 |
| `dist/replication_package.zip` | the same 5 data members and the browser script; code members synced with `dist/replication/code` (the code/ versions of `build_panel_v2.py`, `fetch_companyfacts.py`, `retrieval_browser.js`, which were identical before), `exclusions.py` and `purge_excluded.py` added, README member updated | other members and their metadata unchanged |

- **Format.** Every other byte of each file was kept: CSV lines were dropped, and JSON was re-serialized with the setting that
  reproduces the original. The rest of each file was checked to equal the original minus the registrant.
- **Checked and not present:**
  - `data/panel.csv`, `panel_v3.csv` and `panel_v3_core_full.csv`;
  - every file in `data/v3_inputs/` (the raw frames files decoded from base 36);
  - `data/tasks/`, `data/examples/`, `data/playbook/` and `data/raw/`;
  - `engine/examples/` and the engine test fixtures and golden files;
  - `notes/`, including `bootstrap_draws_v3.npz` and the review tarballs;
  - `dist/arxiv/` and `arxiv_source.tar.gz`;
  - every PDF.
- **Documents edited:**
  - `code/REPLICATION_README.md` and `dist/replication/README.md`: 661 registrants, 240,318 facts, the exclusion files;
  - `data/v3_inputs/README_retrieval.md`: a note that one of the 654 registrants of the 29 Oct retrieval was later removed and had no
    rows in those files;
  - `notes/data_sources_part2.md`: the new sha256 of `data/panel_v2_all.csv` (`d073bbfe…`; before `4cc3352e…`).

## 3. Stages rerun, in order

1. **data_part2.** `05_function_priors.py`, `11_nonsoftware_priors.py`, `08_params.py` and `10_validate.py`. The outputs are
   identical, except that 08 does not reproduce the committed `params.yaml` (section 6, item 1). The committed file was restored.
2. **invoice_chain.** `code/examples/invoice_chain.py`, then the `verify_part2_*` scripts (section 6, item 3).
3. **Panel builds.** `build_panel_v2.py` and `build_panel_v3.py` in place (they reproduce the purged files). `growth_from_filings.py`
   and `build_panel.py` (v1) were run in a scratch copy, because `build_panel.py` would overwrite `data/panel.csv` with the v1 sample.
   Both reproduce the purged files.
4. **Empirics.**
   - `estimate_revised.py` and `paper_stats.py`;
   - `estimate_organic.py`: in a scratch copy (section 6, item 2), outputs installed;
   - `V3_PANEL=v2 estimate_v3.py`, then `estimate_v3.py` with 999 replications, which also runs `estimate_v3_report.py`.
5. **The rest.**
   - `code/validation/backtest.py`;
   - `calibrate_horizons.py`;
   - `verify_theory.py`;
   - `paper1_macros.py`;
   - `code/playbook/run_archetypes.py` and `verify_part2_playbook.py`;
   - the engine pytest;
   - `bash code/build_paper1.sh`.
6. **Not rerun.** `estimate_frontier.py` and `decompose_gap.py` read only `data/panel.csv`, which did not change.

## 4. Values that moved (old → new)

### Paper 1

- **PDFs.** `paper1.pdf` and `supplement.pdf` were rebuilt. Their text is identical to a build from the pre-removal sources
  (`pdftotext` diff empty). Nothing that is printed moved: abstract, summary box, Table 2, Table S4 (`tab_robust_v3`), the a_min band,
  the v3 tables and the calibration.
- **Macros** (`paper1/macros.tex`, 3 of 1,564; none is used in any .tex file):
  - `\NFirmsBroad` 541 → 540;
  - `\NFirmYearsBroad` 3,626 → 3,619;
  - `\EoneScaleCashSe` 2.8 → 3.1 (an RNG-stream effect; see the next block).
- **Broad universe** (`notes/panel_build_log.txt`):
  - firms with any fiscal year: 661 → 660; firm-years: 5,751 → 5,741;
  - broad sample: 3,626 → 3,619 firm-years and 541 → 540 firms;
  - by period: 2010–15 1,080 → 1,079; 2016–19 868 → 864; 2020–22 875 → 873; 2023–25 803 (unchanged).
  - registrants retrieved and kept: 662 → 661; facts 240,732 → 240,318; SIC universe file 3,641 → 3,640.
- **Broad-sample row of the v2 robustness table** (`sections/tables/tab_robust.tex`, `notes/empirics_revised.json`; not used by
  `paper1.tex` or `supplement.tex`):
  - GAAP upper-decile slope −0.31 → −0.30 (−0.3059 → −0.3021). The other printed entries are unchanged (61, 47, 58, 45; cash slope
    −0.24).
  - n: GAAP 3,593 → 3,586; cash 3,508 → 3,501.
  - P95 of R moves in the fourth decimal: GAAP 2016–19 0.6054 → 0.6062; cash 2016–19 0.5758 → 0.5762.
  - Change in P95, 2016–19 to 2023–25: GAAP −0.1340 → −0.1348, 90% interval [−0.211, −0.052] → [−0.199, −0.047]; cash −0.1276 →
    −0.1279, [−0.198, −0.059] → [−0.205, −0.058].
- **Bootstrap intervals moved through the shared random stream** (core sample; no point estimate moved).
  `estimate_revised.py` draws every bootstrap from one seeded generator. The broad-sample robustness bootstrap has one firm fewer
  and runs before the size and capital-intensity blocks, so those blocks get different draws.
  - `sections/tables/tab_scale.tex` (old v2 table, not in P1), 90% intervals of P95 of R:
    - $0.1–0.5B, cash: [55, 69] → [56, 70];
    - $0.5–2B, cash: [49, 61] → [48, 62];
    - $2–10B: GAAP [47, 57] → [47, 58]; cash [46, 64] → [46, 61];
    - >$10B, cash: [44, 59] → [42, 59];
    - standard errors of the slope on log revenue: GAAP 1.3 → 1.4; cash 1.2 → 1.3.
  - `notes/empirics_revised.json` capital-intensity block: the 16 interval bounds of `capint/{op,cash}/{period}/ci90`. Example:
    2023–25 GAAP [−0.096, 0.034] → [−0.104, 0.036].
  - These E1 intervals are copied by `estimate_organic.py`:
    - `notes/empirics_organic.json`: 39 values. These are the E1 `ci90` of capint_gap and scale_p95, and the E1 `se` of scale_slope
      and scale_tenfold. scale_tenfold standard errors: GAAP 0.0292 → 0.0312; cash 0.0281 → 0.0309.
    - `sections/tables/tab_estimands.tex` (old v2 table, not in P1), E1 column: P95 per tenfold revenue, GAAP 1.6 (2.9) → 1.6 (3.1);
      cash −5.7 (2.8) → −5.7 (3.1); capital-intensity gap 2023–25, GAAP −2 [−10, +3] → −2 [−10, +4];
    - `notes/estimand_notes.md`: the same two standard errors;
    - `notes/sample_audit.md`, column "published v2": size gradient SEs 2.9 → 3.1 and 2.8 → 3.1; capital-intensity gap 2023–25,
      GAAP [−9.6, +3.4] → [−10.4, +3.6]; cash [−22.3, −3.4] → [−22.2, −3.5].
- `figures/fig_scale.pdf` was redrawn with the new intervals; it is not in P1. `fig_empirical_frontier.pdf` changed only in its
  creation date.

### Paper 2

- **Backtest, placebo window FY2016–17 to 2019–20** (the registrant's FY2016–17 and FY2019–20 entered it):
  - placebo n 161 → 160 (main n 206, unchanged);
  - `\btFirmPlB` 2.0 → 2.1, which `part2/validation_backtest.tex:79` uses as a macro;
  - `part2/tables/backtest_firm.tex`, placebo row: COGS 0.00 (1.25), unchanged; S&M 1.71 (1.62) → 1.74 (1.63); G&A 0.03 (0.83) →
    0.01 (0.84); R&D 1.09 (0.67) → 1.11 (0.67); total 2.04 (2.29) → 2.07 (2.30); N (main; placebo) 206; 161 → 206; 160.
  - `notes/backtest_results.json`: the placebo coefficients, standard errors, R², means and standard deviations, and the input hash
    of `panel_v2_all.csv`.
- **P2 priors: unchanged.** These are `data/tasks/` (`industry_function_shares.csv`, function priors, nonsoftware priors) and
  `params.yaml`. The panel inputs use FY2023–25 windows, or SIC 7372 FY2022–24, and the registrant has no year after FY2021. The
  G&A floor of the a_min band is still p5 0.046 and p10 0.063 for 96 firms at $1–10B, and p5 0.029 and p10 0.032 for 12 firms
  above $10B.

### Engine

- No file under `engine/` changed.
- The playbook outputs are unchanged, except refreshed hashes and run times in `notes/playbook_results.json` (section 6).

### Core-sample results that did not move

- **Identical files and frames:**
  - `data/panel.csv`, `panel_v3.csv`, `panel_v3_core_full.csv` and `notes/panel_v3_build.json` are byte-identical;
  - the estimation frames of `estimate_organic.py` (v2 and v3: every variant, core and core_ext) are identical;
  - `notes/empirics_v3.json`, `calibration_anchor_v3.json`, `frontier_slope_v3.json` and `bootstrap_draws_v3.npz` are identical;
  - all `tab_*_v3.tex` files are identical, in `sections/tables/` and in `paper1/`;
  - `notes/calibration_results.json`, `tab_calib.tex`, `notes/verify_theory_output.txt`, `notes/paper_stats.json`,
    `notes/calibration_anchor_E2.json`, the playbook tables and macros, and `part2/tables/*` other than the backtest are identical.
- **`notes/empirics_v2_exact.json`.** No existing value moved. 2,242 entries were added, for 12 statistics that `estimate_v3.py`
  gained after this file was last written (29 Oct): anchor `p95` and `p975`, each with `maint_base`, `m0_net_med`, `Pi_net_q1`,
  `Pi_net_med` and `Pi_net_q3`; also `cone_op_cell60` and `cone_cash_cell60`. This is code drift, not the removal.

## 5. Typed counts in prose that need editing (not edited here)

| File:line | Text | Old → new |
|---|---|---|
| `sections/data.tex:4` | "For the 662 registrants in this universe that ever report at least \$50 million of revenue" | 662 → 661 |
| `sections/appendix_data.tex:3` | "The universe is the 3,641 registrants listed under SIC codes 7370 to 7374 in the EDGAR company index" | 3,641 → 3,640 (the universe file now has 3,640; EDGAR itself still lists the registrant) |
| `sections/appendix_data.tex:3` | "We retrieved \texttt{companyfacts} for the 662 of them" | 662 → 661 |
| `sections/appendix_data.tex:3` | "for 35 US-GAAP elements: 240,732 facts in all" | 240,732 → 240,318 |

`part2/*.tex`: none. The backtest numbers are macros.

## 6. Pre-existing issues found (not caused by the removal)

1. **`08_params.py` does not reproduce the committed `data/tasks/params.yaml`.** Rerunning it drops the round-2 edits of 2 Nov:
   - the KPMG 2025 SOX budget by revenue size;
   - `audit_fee_accelerated_filer_reference`;
   - the B9 unit and note;
   - the B1 pass-through unit and note;
   - the B2 value-test cap and `feasible_at_full_automation`;
   - the source text of `a_min_accountability_floor`;
   - it also restores the removed `identical_inference` anchor.

   I restored the committed file. Its panel-derived values are identical with and without the registrant. `regenerate_all.sh`'s
   params stage would regress the file.
2. **`estimate_organic.py` stops at its calibration-anchor regression check.** The check compares its v2 E1 anchor (n 15) with
   `notes/calibration_results.json`, whose anchor `calibrate_horizons.py` now computes on v3 (n 13). It fails without the removal
   too: the frames are identical, and `calibration_results.json` was not touched.
   - I ran the script in a scratch copy without `calibration_results.json`, the documented first-run path. Its
     `empirics_organic.json`, `tab_estimands.tex` and `estimand_notes.md` are installed.
   - I kept the committed `calibration_anchor_E2.json`, whose content is identical apart from its `regression_check` block. That
     block would become `"passed": null` and make `regenerate_all.sh` rerun the failing check.
3. **`verify_part2_core` check 23y failed before the removal.** `data/examples/invoice_chain.json` recorded a stale sha256 of
   `engine/src/autofrontier/defaults.yaml`. Rerunning `code/examples/invoice_chain.py` changed only that hash
   (`invoice_macros.tex` is unchanged), and the check passes.
4. **Stale input hashes were refreshed by the reruns:** `params.yaml` and `defaults.yaml` in `notes/backtest_results.json`, and
   `defaults.yaml` in `notes/playbook_results.json`.
5. **The committed `paper1.pdf` and `supplement.pdf` predated their sources** (for example, Table S8 is now S10); both were rebuilt.

## 7. Checks

| Check | Result |
|---|---|
| `paper1_macros.py` CLAIMS | pass (1,564 macros; abstract 1,912 characters of 1,920) |
| `verify_theory.py` | 191/191 |
| `verify_part2_accounting` | 48/48 |
| `verify_part2_acquirer` | 82/82 |
| `verify_part2_regimes` | 85/85 |
| `verify_part2_core` | 158/158 (after the invoice_chain rerun, section 6, item 3) |
| `verify_part2_ext` | 143/143 |
| `verify_part2_labor` | 43/43 |
| `verify_part2_product` | 94/94 |
| `verify_part2_competition` | 44/44 |
| `verify_part2_playbook` | 40/40 |
| data_part2 `10_validate.py` | all contract checks passed |
| engine pytest, slow tests included | 191 passed |
| `build_paper1.sh` | built (82 and 57 pages), no unresolved reference |

No check was edited.

## 8. Final scan

The whole repository was scanned, excluding `.git` and `__pycache__`.

| Search | Result |
|---|---|
| Name, any case | none |
| Decimal and zero-padded CIK | none |
| Hexadecimal CIK | none |
| Accession numbers of its filings | none |
| Binary files (zip and xlsx members, tar.gz members, PDF text) | none |
| Decoded CIK lists (`purge_excluded.py --check`) | none |
| Base-36 CIK as a word | none |
| Base-36 CIK as a bare substring | 2 hits, not CIK occurrences |

The two substring hits are inside base64-encoded PNG outputs of two third-party notebooks (`data/raw/gpts_are_gpts/repo/code/gpts_are_gpts_script{1,2}.ipynb`, covered by `data/raw/CHECKSUMS.sha256`). Both were left unchanged.

## 9. Lead-agent follow-up (2 Nov, 16:30–17:00 UTC−8)

- **Prose counts fixed.** Section 4.1 now says that one registrant is excluded from all data at the author's request, that it is outside the estimation sample and that no reported figure depends on it, and gives 661 registrants. Appendix S6 gives 3,641 registrants at retrieval less the excluded one (3,640), 662 retrieved and 661 kept, 240,318 facts, and names `code/exclusions.py` as the reason a fresh retrieval cannot restore it. Table 8 has a row "Data exclusion (2 November, 14:50)".
- **Page count.** The 82 pages of the agent's build come from the final-audit coder's two-float Table 2 (FA-m6), not from the exclusion. A one-page version at `\scriptsize` was tried and rejected: the float was 283 pt taller than the page, which the build script did not catch. `code/build_paper1.sh` now also fails on "Float too large". Two pairs of rows in Table 8 were merged (competing interests; basis of selling and marketing). Build: main paper 82 pages, supplement 57, clean. The main paper is two pages over the editorial target of about 80 pages set for the agents; no external limit applies.
- **FA-m13 text.** Section 5.8 reports the netted (central) anchor surplus from the new macros `\AncPiNet*` and `\AncPiNetCount`, with a CLAIMS entry (above zero in all four views; E1 lower end under one point).
- **Copies outside the repository deleted.** Every scratch copy in the session's scratch folder that contained the registrant's data was deleted: `r2prop`, `base`, `v3run`, `t2`, `t3`, `t4`, `repo`, `r2_econ`, `partI_integ`, `referee_build`, `af`, `repltest`, `repltest2`, `thv2`, `oldparams`, `icfr`, `vt`, `rt`, `r2_im` and seven loose files. A scan of the whole container (repository, scratch folder, `/tmp`, uploads and outputs; text, binary, gzip and zip members) then found no occurrence of the name or the identifier. The connected folder on the author's computer holds no project data. The only remaining copies are inside this session's own conversation records (raw output of the October retrieval), which are not project files and do not ship.
- **Not data, flagged to the author.** Several notes written since 29 October (the agent log, the revision plan, `unified_model_spec.md`, `integration_todo.md`, a round-1 panel report and the final audit) say that the excluded registrant is the author's employer, or describe the employer's business, without naming it. If the agent log and review notes ship with the replication package, as Appendix A says, a reader could infer the company. Redacting those lines before packaging is the author's call. Asked at 16:56, the author decided to keep them as they are (16:57); nothing was redacted.

## 10. Identifiability of the exclusion (2 Nov, 22:44 UTC−8)

The GLM review inverted the digest in `code/exclusions.py`: a SHA-256 of a CIK can be inverted by brute force, because there are only a few million CIKs. The digest therefore hides the registrant only from someone who does not try. The author was offered three options: a keyed hash with the key kept off the repository, dropping the code filter, or leaving it as is. She chose to leave it as is. The data stay purged and the filter stays. Outside reviews that name the registrant are archived in redacted form, and the repository itself still names it nowhere.
