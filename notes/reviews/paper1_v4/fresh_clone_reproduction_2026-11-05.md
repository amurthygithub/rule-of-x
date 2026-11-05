# Fresh-clone reproduction of the final commit of review round 3 (5 November 2026)

Requested by the Mistral Large 4 re-review (RS-7: the recorded run, at 3998b33, predated the re-estimation of 3
November). Run by the lead agent; the driver (`run.sh`), logs and comparison script (`compare.py`, the one of 3 November)
are in the session scratchpad, not in the repository.

**Setup.** `git clone` of the repository and checkout of commit 05a58c4 (the head after the audit fixes, the DeepSeek
items and the GPT-6.1 Sol relabel). A new Python 3.13.18 virtual environment from `requirements-lock.txt`; `pip freeze`
equals the lock file. Run 18:47 to 19:47 UTC, under `nice` on two shared cores.

**Raw data.** `code/fetch_raw_data.py` downloaded and verified the four GitHub sources (aieconindex_r 82 files,
gpts_are_gpts 23, ms_working_with_ai 11, metr_eval_analysis 73). The other hosts refused scripted downloads at the
session's proxy (huggingface.co, bls.gov, onetcenter.org, stern.nyu.edu: HTTP 403), so their files were placed with
`--from-dir` from the copies used, verified against `data/raw/CHECKSUMS.sha256` in the same way; `--check` then passed for
all twelve sources.

**Pipeline.** `bash code/regenerate_all.sh`: all 19 stages through `latex_p1` passed in 49 minutes (the bootstraps, the
stress-test report, S12, the macros, verify_theory 203/203, the Part 2 checks, the engine tests and both Paper 1 PDFs).
Stage `latex_p2` stops by design: Paper 2 has no main document yet.

**Comparison with the commit** (git status after the run; text and rendered pixels at 100 dpi for PDFs). Seven tracked
files differed; every other output is byte-identical, including every data file, table and macro file, the plain
abstract and `figures/fig_stress.pdf`, whose layout depended on the environment on 3 November:

| File | Difference | Reading |
|---|---|---|
| `paper1/paper1.pdf` (88 pp.), `paper1/supplement.pdf` (73 pp.) | creation date only; text identical, every page pixel-identical | expected |
| `figures/fig_empirical_frontier.pdf`, `fig_scale.pdf`, `fig_scores_time.pdf` | creation date only; pixel-identical | expected (figures not used by either paper) |
| `notes/playbook_results.json` | run timings and generation time | expected |
| `notes/verify_theory_output.txt` | the script's path in one warning | expected |

**Specification curve** (`code/spec_curve.py`, not a pipeline stage, run afterwards because round 3 had edited a label of
its generated table by hand). A default run sizes the bootstrap subset by the machine's speed: it chose 186 samples
against the reported 206, which moved the bootstrap shares of `tab_spec_curve.tex` and `spec_macros.tex` by up to 0.5
points (for example 29.0 to 29.5% and 42.2 to 42.5%); the specification shares, medians and ranges were identical. With
`SC_BOOT_K=206`, the reported run's size, every number reproduced: `tab_spec_curve.tex` and `specs.csv.gz` byte-identical,
`fig_spec_curve.pdf` pixel-identical, and in `spec_macros.tex` and `results.json` only the run time (`\ScRuntime`, 9
against 11 minutes on this machine), the date and the git head differ. So the hand-edited label equals what the
generator prints. The script's docstring gave `SC_BOOT_K=169`, the size of an earlier run; it now gives 206 and where to
read it, and `code/REPLICATION_README.md` says the same.

**Not covered.** The million-draw stress test (`code/mc_claims.py`; its stored output is what the pipeline formats),
`code/frontier_figures.py`, `code/audit/*`, the Lean build of `formal/` and the SEC retrieval itself (the run starts from
the committed extract).

**Commits after 05a58c4.** The commit that records this run changes only this note, `README.md`,
`code/REPLICATION_README.md`, the docstring of `code/spec_curve.py`, one sentence of Supplement S8.4, the agent log and the
PDFs rebuilt from that sentence; no input of any stage changes.
