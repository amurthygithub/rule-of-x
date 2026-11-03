# Stress-test dashboard data

Data files and page source of the Claude dashboard "Rule of 40 stress test" (2 November 2026).

- `draws_lhs.csv` (in the parent folder): one row per Latin-hypercube draw, taken from the run's checkpoint on the author's machine.
- `amin_points.csv` (in the parent folder): the accountability-floor sub-box, re-evaluated point by point with the run's design and seed. It matches the run's summary: 873 and 1,805 of 2,032 points with no admissible design, at the 5% and 1% thresholds.
- `mc_*.csv`: summaries derived from `mc_claims.json`.
- `index.html`: the dashboard page.
