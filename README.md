# Rule of X: growth, profitability and the limits of AI automation

What can AI do for a software company's growth and margins, and where does it stop? This repository holds Part 1 of a planned three-part research series on that question by Akshaya Bangalore Sreenivasa Murthy (independent researcher), with the code and data behind every number. Parts 2 and 3 are not written yet.

## Read the paper

**Part 1: *The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation*** (working paper, November 2026)

- [The paper (PDF, 89 pages)](papers/Rule-of-40-as-a-Price-Line.pdf)
- [Supplementary Appendix (PDF, 73 pages)](papers/Rule-of-40-as-a-Price-Line-Supplementary-Appendix.pdf)

Download both into one folder: the links between them work by file name.

## What Part 1 finds

The paper measures "moving the needle" with the Rule of 40 score: revenue growth plus profit margin. It places 284 software companies on that score from their SEC filings (2010 to 2025), then uses an economic model to ask what AI automation can change, with scenarios out to 2036. The AI results are scenarios, not forecasts.

**What AI can move**

- **Costs.** Automating G&A, support, maintenance engineering and human service delivery raises margins.
- **Growth.** Cheaper customer acquisition buys more growth per dollar.
- **Market size.** If labor budgets shift to software, the market grows. If customers need fewer seats, it can shrink.

**Where it stops**

1. **AI has its own cost floor.** Computing, vendor fees, controls, security, maintenance and errors do not go to zero.
2. **Full automation does not make a mature company a Rule of 100 company.** At the paper's central costs and fixed prices, a mature, asset-light company's score on a cash basis stays below 100 unless its market grows more than 32.5% a year. The bar is 28% to 78% depending on what computing costs, and 36% if half the savings go to customers as lower prices (Section 7.2).
3. **Competition takes the savings.** If rivals can enter freely and sell the same product, lower costs become lower prices. Only a company with something rivals cannot copy earns more than a normal return (Proposition 4).
4. **It costs before it pays.** In the central scenario, a top company captures 41% of its program's benefits by 2036, and the program pays back after 7.5 years. Its cumulative effect is negative at three and at five years at all but a few points of the stress test. Execution, not market growth, moves the 2036 result most (Section 7.3).
5. **Accountability stays.** Internal control over financial reporting is pass-fail. In the paper's illustrative example, no control design built only from AI on a single model provider passes, because those AI layers can fail together (Proposition 5).

**Where to start.** Counting as growth spend only selling and marketing above a maintenance level, cutting G&A cost outranks automating the growth engine at 5 of the 6 company positions examined (Section 7.5).

**The yardstick itself.** The Rule of 40 is a pass mark, not a measure of value: when growth lasts, a point of growth is worth more than a point of margin. The margin used changes who passes: in 2023 to 2025, 29% of company-years cleared 40 on free cash flow before stock-based pay, and 9% after it. On operating margin, the score that only the top 5% reach fell about 12 points from 2016–19 to 2023–25, because fewer companies grew fast.

Nothing here is investment advice.

## The series

| Part | Status | Where |
|---|---|---|
| 1. *The Rule of 40 as a Price Line* | working paper, November 2026 | `papers/`; source `paper1/*.tex`, `sections/` (the pipeline's copies are `paper1/paper1.pdf` and `paper1/supplement.pdf`, same text) |
| 2. *The Economics of AI Transformation* (planned) | not written yet; early working material only | `part2/` |
| 3. A software engine that applies the series to a company's own data (planned) | not written yet; early working code only | `engine/` (see `engine/README.md`) |

## How it was made

The author directed the research and made its decisions; AI agents drafted the text, code and proofs, and four AI models from other developers reviewed it. Part 1's Appendix A describes the protocol and the author's decisions; the agent log, every review report, the issue logs and the responses to reviewers are in `notes/` and `notes/reviews/`.

## Reproducing the results

```bash
python3 -m pip install -r requirements-lock.txt   # exact versions used for the committed outputs (requirements.txt: direct dependencies only)
python3 code/fetch_raw_data.py         # third-party data into data/raw/ (not redistributed), verified against CHECKSUMS.sha256
bash code/regenerate_all.sh            # every stage, in order; logs in build_logs/
bash code/regenerate_all.sh --skip-raw # or: without the three stages that read data/raw/ (their committed outputs are kept)
```

`code/regenerate_all.sh` rebuilds the panels from the SEC extract, reruns the estimation (999-replication firm-cluster bootstraps; a full run takes about an hour), the calibration, the macros that supply every number quoted in Paper 1, the verification scripts and the engine tests, and builds Paper 1 with `code/build_paper1.sh`. Three stages (`params`, `backtest`, `playbook`) read third-party files in `data/raw/`; the script verifies them before its first stage and stops, naming `code/fetch_raw_data.py`, if any is missing. Paper 1's own stages read only the SEC extract and other shipped files. With `data/raw/` fetched and the packages of `requirements-lock.txt`, a fresh checkout reproduces the committed outputs byte for byte, apart from run timings, PDF creation dates and file paths printed in warnings (tested from a fresh clone of commit 3998b33 on 3 November 2026 and of commit 05a58c4 on 5 November 2026; `notes/reviews/paper1_v3/audit_2026-11-03_revision.md`, `notes/reviews/paper1_v4/fresh_clone_reproduction_2026-11-05.md`). The specification curve, which is not a stage, reproduces with `SC_BOOT_K=206 python3 code/spec_curve.py`. Other versions of the indirect dependencies, such as the font libraries matplotlib uses, can move figure elements by a fraction of a point; text and data are unchanged. The last stage (Paper 2's LaTeX) stops until Paper 2 has a main document. Details: `code/REPLICATION_README.md` and `data/raw/README.md`.

Machine-checked proofs: `formal/` formalizes Paper 1's static model in Lean 4 with Mathlib (`cd formal && lake build`; see `formal/README.md`).

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
