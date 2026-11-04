# Business dashboard data

Data files and page source of the Claude dashboard "Rule of 40 and AI: business guide" (3 November 2026), the
plain-language reading of Paper 1 and its million-draw stress test. It replaced the "Rule of 40 stress test" page of
2 November (`notes/mc_results_2026-11-02/dashboard/`), which showed the 10,000-draw run.

- `facts.csv`: every number quoted in the page text, as the paper prints it (`macro`) or as the run or the lever ranking
  gives it, with its section (`source`). The page fills each number from this file; none is typed into the page.
- `levers.csv`, `positions.csv`: the four-lever ranking (engineering, back office, growth engine, cost of revenue) at the
  six positions of Paper 1 Table 7, in score points per 10% saving, on the three spend bases (`notes/playbook_results.json`,
  `ranking_by_basis`; cited in Paper 1 Section 7.5).
- `levels.csv`, `hist.csv`, `bands.csv`, `sobol.csv`, `swings.csv`, `claims.csv`, `amin.csv`: from `../mc_claims.json`,
  `../seed2/mc_claims.json` and `../draws_lhs.csv.gz` (histograms and quantile bands over all 1,000,000 draws of seed 1).
- `pace.csv`: realized and embedded shares of the program by year (Paper 1 Section 7.3 macros).
- `index.src.html`: the page with `{{key}}` for each number; `index.html`: the page as published.

Build: `python3 code/biz_dashboard_data.py && python3 code/biz_dashboard_page.py` (reads committed outputs only).
