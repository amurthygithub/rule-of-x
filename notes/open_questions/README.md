# Open questions: new analyses for the business dashboard (3 November 2026)

Answers to questions Paper 1 does not address, built for the dashboard "Rule of 40 and AI: business guide" at the
author's request ("let us try to answer all the types and sub types of questions"; 18:13). They are not part of
Paper 1; whether to add them is to be decided after review ("lets build the dashboard, lets see if we should include it
in the paper").

| Question | File | Method |
|---|---|---|
| What happens if we don't automate? | `paths.json` | `code/biz_open_questions.py`: Paper 1's pass-through scenario (calibrate_horizons.central_path, phi > 0) with the firm's own automation set to zero; rivals at the central or fast pace; phi = 0, 0.5, 0.7 |
| What about a typical company? | `paths.json` | The same program, target and pace from the paper's typical $1-5 billion company (block B8), its own growth, k = 0 and own k |
| Does the market pay for a higher score? | `valuation.json` | `code/biz_valuation.py`: public float (SEC frames, retrieved 3 Nov 2026 with the author's approval; `data/v3_inputs/README_retrieval.md`) over revenue against growth and margin, year fixed effects, firm clusters, bootstrap of the implied weight |

The company calculator on the dashboard applies Paper 1's formulas (Proposition prop:levers-position (a), Table
tab:levers-position, Table tab:ceiling) to the reader's own inputs. Questions answered only in the companion paper are
listed on the dashboard as pending its audit (the author chose to wait for it); questions no available data answer
are listed with what would answer them.

Both scripts read committed inputs and write only here and to `notes/mc_results_2026-11-03_1m/dashboard/`.
