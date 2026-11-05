# Check of the dashboard's open-questions analyses (3 November 2026)

- **Checked:** `code/biz_open_questions.py` (do-nothing and typical-company paths), `code/biz_valuation.py` (valuation test
  on SEC public float), the open-questions section and calculator of `notes/mc_results_2026-11-03_1m/dashboard/index.src.html`.
- **Checker:** an agent on `claude-fable-5-1` that did not write them (written on `claude-opus-5-5`); it reran all three
  scripts (outputs byte-identical) and edited nothing.
- **Found correct:** the do-nothing formula (the paper's pass-through intercept with the firm's own share at zero, reducing
  to the anchor at phi = 0); the typical path and its payback; the merge, regressions, within-R2 and bootstrap of the
  valuation test; the calculator's hurdle, threshold and growth-engine formulas; section references; the
  companion-paper list.

| # | Finding | Disposition |
|---|---|---|
| 1 | Error: the calculator's cost-of-revenue lever used the pass-through rate; Prop 9(a) uses the elasticity, implemented in the companion ranking as keep = 1 - phi C0. | Fixed: keep = 1 - phi max(1 - f - m0, 0), m0 = m + sigma + k g. |
| 2 | Lever points are pre-tax while the margin input is after-tax cash. | Fixed: labelled pre-tax, with the after-tax factor (0.82) in the calculator and the lever chart note. |
| 3 | Four-lever ranking and the R&D lever attributed to Prop 9; transience and own-optimum assumptions missing. | Fixed: attributed to the companion ranking with Prop 9's formulas; caveats added. |
| 4 | Adopter-vs-fast-rivals path took the phi = 0 dip. | Fixed: dip from the paper's path at the same phi (44.3 -> 44.7, 39.2 -> 39.9; gap 15.8 -> 16.2); asserted against the paper's path for R and R_net. |
| 5 | 41.7 and 33.3 are durable scores, not reported scores. | Fixed: "durable score", with the median reported scores (53.5, 23.9). |
| 6 | "Trimmed" for winsorized. | Fixed: "capped". |
| 7 | Sample counts by basis; unmatched firm-years not explained. | Fixed: 1,247 (cash) and 1,272 (GAAP); 191 without any float (foreign filers) and 132 fiscal-2025 years not yet filed. |
| 8 | "SEC filings carry no prices" contradicts the use of float. | Fixed: "one market value a year, not a price series". |
| 9 | One reading of the weight given. | Fixed: both of the paper's benchmarks (screening weight 1.8-2.8, decision weight 5-15) and the caution that a cross-firm ratio is neither. |
| 10 | Top-40 R2 is lowered by range restriction. | Fixed: clause added. |
| 11 | Threshold slope omits a small compute-linked cost. | Fixed: "about" in the output; caveat says approximate. |
| 12 | Table header; completed-check sentence. | Header fixed; the sentence stands now that the findings are fixed. |
| 13 | Non-adopter keeps volume at lower prices. | Fixed: stated in the method note. |
