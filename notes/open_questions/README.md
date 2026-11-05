# Open questions: new analyses for the business dashboard (3 November 2026)

Answers to questions Paper 1 did not address, built for the dashboard "Rule of 40 and AI: business guide" at the
author's request ("let us try to answer all the types and sub types of questions"; 18:13). Whether to add them to the
paper was left to be decided after review ("lets build the dashboard, lets see if we should include it in the paper");
on 4 November 2026 the author added three of them to Paper 1's Supplementary Appendix, Section S12
(`sections/supp_extensions.tex`, formatted and checked by `code/supp_extensions.py`): S12.1 is `valuation.json`
(`code/biz_valuation.py`), S12.2 the do-nothing paths of `paths.json` (`code/biz_open_questions.py`) and S12.3 the
payback grid of the million-draw stress test. The valuation interval was revised on 5 November 2026 (outside
re-review, GPT F08): percentiles over the bootstrap samples with a positive margin coefficient, with the share of the
others reported beside them.

| Question | File | Method |
|---|---|---|
| What happens if we don't automate? | `paths.json` | `code/biz_open_questions.py`: Paper 1's pass-through scenario (calibrate_horizons.central_path, phi > 0) with the firm's own automation set to zero; rivals at the central or fast pace; phi = 0, 0.5, 0.7 |
| What about a typical company? | `paths.json` | The same program, target and pace from the paper's typical $1-5 billion company (block B8), its own growth, k = 0 and own k |
| Does the market pay for a higher score? | `valuation.json` | `code/biz_valuation.py`: public float (SEC frames, retrieved 3 Nov 2026 with the author's approval; `data/v3_inputs/README_retrieval.md`) over revenue against growth and margin, year fixed effects, firm clusters, bootstrap of the implied weight |
| Heatmaps (19:21 request: "can we show some data as 4x4 or 6x6 or whatever matrices? what about heamaps?") | `../mc_results_2026-11-03_1m/dashboard/matrices.csv` | `code/biz_matrices.py`: medians of the million stress-test draws in 6 x 6 equal-width bins of two inputs (2036 score by change capacity and market growth; payback by change capacity and share of changes that create value); Paper 1's Rule-of-100 growth threshold (G100_central / (1 - k)) on a grid of compute share and capital per dollar of new revenue and the cost of doing nothing by pass-through and rivals' pace (both from the `grids` block of `paths.json`); median float-to-revenue multiple by quintile of growth and of margin, on the sample of `biz_valuation.py` |

The company calculator on the dashboard applies Paper 1's formulas (Proposition prop:levers-position (a), Table
tab:levers-position, Table tab:ceiling) to the reader's own inputs. Questions answered only in the companion paper are
listed on the dashboard as pending its audit (the author chose to wait for it); questions no available data answer
are listed with what would answer them.

The scripts read committed inputs and write only here and to `notes/mc_results_2026-11-03_1m/dashboard/`.
