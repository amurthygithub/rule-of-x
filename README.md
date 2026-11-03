# Rule of X: growth, profitability and the limits of AI automation

Code, data and manuscripts for three papers by Akshaya Bangalore Sreenivasa Murthy (independent researcher).

| Paper | Status | Where |
|---|---|---|
| 1. *The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation* | final review before arXiv (q-fin.GN, cross-listed econ.GN) | `paper1/paper1.pdf`, `paper1/supplement.pdf`; source `paper1/*.tex`, `sections/` |
| 2. *The Economics of AI Transformation* | in preparation (sections and checks; no main document yet) | `part2/` |
| 3. The autofrontier engine | in preparation | `engine/` (see `engine/README.md`) |

The papers were produced in a documented collaboration between the author and AI research agents. Paper 1's Appendix A describes the protocol and the author's decisions; the agent log, every review report, the issue logs and the responses to reviewers are in `notes/` and `notes/reviews/`.

## Reproducing the results

```bash
python3 -m pip install -r requirements-lock.txt   # exact versions used for the committed outputs (requirements.txt: direct dependencies only)
python3 code/fetch_raw_data.py         # third-party data into data/raw/ (not redistributed), verified against CHECKSUMS.sha256
bash code/regenerate_all.sh            # every stage, in order; logs in build_logs/
bash code/regenerate_all.sh --skip-raw # or: without the three stages that read data/raw/ (their committed outputs are kept)
```

`code/regenerate_all.sh` rebuilds the panels from the SEC extract, reruns the estimation (999-replication firm-cluster bootstraps; a full run takes about an hour), the calibration, the macros that supply every number quoted in Paper 1, the verification scripts and the engine tests, and builds Paper 1 with `code/build_paper1.sh`. Three stages (`params`, `backtest`, `playbook`) read third-party files in `data/raw/`; the script verifies them before its first stage and stops, naming `code/fetch_raw_data.py`, if any is missing. Paper 1's own stages read only the SEC extract and other shipped files. With `data/raw/` fetched and the packages of `requirements-lock.txt`, a fresh checkout reproduces the committed outputs byte for byte, apart from run timings, PDF creation dates and file paths printed in warnings (tested from a fresh clone of commit 3998b33 on 3 November 2026; `notes/reviews/paper1_v3/audit_2026-11-03_revision.md`). Other versions of the indirect dependencies, such as the font libraries matplotlib uses, can move figure elements by a fraction of a point; text and data are unchanged. The last stage (Paper 2's LaTeX) stops until Paper 2 has a main document. Details: `code/REPLICATION_README.md` and `data/raw/README.md`.

Quick checks (minutes):

```bash
python3 code/paper1_macros.py           # regenerates paper1/macros.tex; stops if any sentence of the text is no longer supported (CLAIMS)
python3 code/verify_theory.py           # symbolic and numerical checks of Paper 1's derivations
for f in code/verify_part2_*.py; do python3 "$f"; done
(cd engine && python3 -m pytest -q)
```

## Data

- **SEC EDGAR XBRL** (`data/`): the extract retrieved on 28-29 October and 2 November 2026 and the panels built from it; retrieval scripts `code/retrieval_browser.js` and `code/fetch_companyfacts.py`. One registrant is excluded from all data and code at the author's request; `code/exclusions.py` drops it by a one-way hash, so a fresh retrieval cannot restore it.
- **Third-party datasets** used to build Paper 2's and the engine's priors (O*NET, BLS OEWS and SOC, the Anthropic Economic Index, GPTs-are-GPTs, Microsoft's working-with-ai, METR's eval-analysis-public, Damodaran) are not redistributed; the derived files are included. `code/fetch_raw_data.py` fetches them from their official addresses and verifies every file (`--check` verifies offline); some hosts need a browser, and the script says which. See `data/raw/README.md`.

## Licences

Software: PolyForm Noncommercial 1.0.0 or, at your option, PolyForm Internal Use 1.0.0. Papers and the author's data compilations: CC BY-NC-ND 4.0. See `LICENSE.md`.

Funding: none. Competing interests: none declared.
