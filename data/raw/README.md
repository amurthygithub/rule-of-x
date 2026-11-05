# Third-party raw data (not included)

The files in this folder are third-party datasets. Except for two O*NET 31.0 files (`onet_31_0/job_titles.csv` and `onet_31_0/occupation_data.csv`, CC BY 4.0, unmodified), which the engine reads to match job titles, they are not redistributed here: their licences differ, and one source (METR's run-level results) has no licence at the commit used. `CHECKSUMS.sha256` records every file as used (sha256, path relative to this folder, bytes; 220 files).

## Getting the files

```bash
python3 code/fetch_raw_data.py                 # fetch every missing file, then verify all 220 against CHECKSUMS.sha256
python3 code/fetch_raw_data.py --check         # verify only (offline; writes nothing)
python3 code/fetch_raw_data.py metr_eval_analysis gpts_are_gpts     # some sources only (folder names)
python3 code/fetch_raw_data.py --from-dir ~/Downloads               # place files saved from a browser, verified
python3 code/fetch_raw_data.py --list          # sources, URLs, and the stages that read each folder
```

The script downloads each source from its official address (GitHub repositories at the recorded commit, file by file), installs a file only if its sha256 matches, never overwrites a file that is present (a present file that differs is reported and left alone), needs no credentials, and prints the folders still missing with instructions for the sources that have to be saved from a browser. The O*NET CSV files are converted from the MySQL archive by `code/data_part2/00_onet_mysql_to_csv.py`. Exit code 0 means every required file is present and verified.

| Folder | Source | Terms | How the script gets it | Read by |
|---|---|---|---|---|
| `onet_31_0` | O*NET 31.0 Database (August 2026), USDOL/ETA: `db_31_0_mysql.zip`, and 14 CSV files converted from it | CC BY 4.0 | onetcenter.org archive, then conversion | stages `backtest` (`job_zones.csv`), `playbook` (`task_statements.csv`); the engine (the two shipped files); `code/data_part2` |
| `bls_oews_2019`, `_2020`, `_2021`, `_2025`, `bls_soc` | U.S. Bureau of Labor Statistics, OEWS (May 2019, 2020, 2021 and 2025) and the SOC 2010 to 2018 crosswalk | U.S. government work, public domain | bls.gov file links (bls.gov often refuses scripts: save from a browser, then `--from-dir`) | stage `backtest`; `code/data_part2` (2025 files) |
| `anthropic_aei` | Anthropic Economic Index, releases of 27 March 2025 and 26 June 2026 (Hugging Face) | CC BY | huggingface.co links, main branch (no revision recorded) | `code/data_part2` (03) |
| `aieconindex_r` | Charles Coverdale, github.com/charlescoverdale/aieconindex (R package; read only for the list of releases) | MIT | GitHub, commit 5967b34 | no script |
| `gpts_are_gpts` | Eloundou, Manning, Mishkin and Rock, github.com/openai/GPTs-are-GPTs | MIT | GitHub, commit 0471612 | stage `backtest`; `code/data_part2` |
| `ms_working_with_ai` | Tomlinson, Jaffe, Wang, Counts and Suri, github.com/microsoft/working-with-ai | CC BY 4.0 | GitHub, commit 550c00c | `code/data_part2` |
| `metr_eval_analysis` | Kwa et al. (2025), github.com/METR/eval-analysis-public | no licence file; only fitted summary parameters are used | GitHub, commit 52cb829 | stage `params` (`code/data_part2/08_params.py`); `code/data_part2` (06) |
| `damodaran_2026` | Aswath Damodaran, NYU Stern industry datasets (January 2026) | publicly posted; cited, not redistributed here | stern.nyu.edu file links; `roc_html.csv` is the page's table saved from a browser | `code/data_part2` (11) |

Two files cannot be downloaded: `anthropic_aei/release_2026_06_26/data_documentation_SUMMARY.md` is a paraphrase written by the lead author (no script reads it, and the script does not count it as missing), and `damodaran_2026/roc_html.csv` was saved from a browser (instructions in the script's output). Damodaran replaces his files every January, so the January 2026 vintage has to come from his archive after January 2027. Tested on 3 Nov 2026 from a sandbox whose network allowed GitHub only: the 189 GitHub files downloaded and verified, and the params stage reproduced `data/tasks/params.yaml` byte for byte from them; huggingface.co, bls.gov, onetcenter.org and stern.nyu.edu were refused there, so those links are as recorded in `notes/data_sources_part2.md` and `notes/data_download_requests.md`, and the placement of hand-saved files and the O*NET conversion were tested with copies of the files as used.

## What needs these files

Every derived file that the papers and the engine read is included elsewhere in `data/` (`data/tasks/` holds the Part II data contract, including `params.yaml`). Three stages of `code/regenerate_all.sh` read this folder: `params` (METR), `backtest` (GPTs-are-GPTs, the BLS files and O*NET job zones) and `playbook` (O*NET task statements, for the task examples in `data/playbook/*.csv`). The script verifies the folders a run needs before its first stage and stops, naming this script, if any file is missing; `--skip-raw` skips those three stages and keeps their committed outputs. Paper 1's own stages (`panel`, `empirics`, `empirics_v3`, `calibrate`, `stress_report`, `paper1_macros`, `verify_theory`, `latex_p1`) read nothing here: they need the shipped SEC extract, `data/v3_inputs/` and shipped files written by other stages (`data/tasks/params.yaml`, the playbook's lever table). The full rebuild of the Part II data, `code/data_part2/`, needs every source.

Exact URLs, versions, retrieval dates and transformations are in `notes/data_sources_part2.md` (Section 2) and `notes/data_sources_nonsoftware.md`. See also `engine/NOTICE.md`.
