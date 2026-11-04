# Fact check of the business dashboard (3 November 2026)

- **Page:** Claude dashboard "Rule of 40 and AI: business guide" (rebuilt in place of "Rule of 40 stress test");
  source `notes/mc_results_2026-11-03_1m/dashboard/index.src.html`, data `facts.csv` and the other CSVs there.
- **Checker:** an agent on `claude-fable-5-1` that did not write the page (the page was written on `claude-opus-5-5`),
  told to check every number and sentence against the paper's macros, Sections 1 to 9, Supplement S10 and the run
  outputs, and to edit nothing.
- **Checked and correct:** all 160 macro-backed facts equal their macros; every non-macro fact equals the run outputs;
  levels, Sobol, swings, pace, histograms, bands, positions, levers and claims equal their sources; section and
  proposition references; no company named outside the paper titles.

| # | Finding | Disposition |
|---|---|---|
| 1 | Error: "a second seed moved no reported extreme by more than 0.02 point"; S10 limits this to values in percent (the ratio row's highest moved by about 5). | Fixed: "no lowest or highest value in percent in the claims table". |
| 2 | The 0.37 to 0.38% is the whole accountability floor, not the design's cost. | Fixed. |
| 3 | Pass-through thresholds are at 2025 prices. | Fixed in the ceiling note and the CFO answer. |
| 4 | Lede written as directives; the ranking is not a decision rule for a firm. | Fixed: "On the paper's ranking"; tiles say "Ranks first/next". |
| 5 | Rule-of-100 tile dropped asset-light, compute 6% at 2025 prices, central costs, fixed prices. | Fixed. |
| 6 | Payback statements without "under central execution" and "except at a few points"; "as costs and compute move" narrower than the paper. | Fixed. |
| 7 | Swing bars are min-max over the group's vertices; compute spans the box's wider range. | Fixed in the chart note. |
| 8 | "a good investment that takes patience" evaluative; NPV needs "with revenue held constant". | Fixed. |
| 9 | Retention: the paper says cutting customer success may lower retention, no net claim. | Fixed. |
| 10 | Section 7.4 names more scarce inputs than accountability. | Fixed: lists the paper's examples, cites Section 7.4. |
| 11 | "pass the audit": Prop 5 is the paper's operationalization, not an audit method. | Fixed: "the paper's control test". |
| 12 | Two meanings of "basis". | Fixed: "spend basis". |
| 13 | 69 of 69 tests comes from the run's seed comparison, not S10. | Fixed: facts.csv cites the run. |
| 14 | "Capacity to change" heading for the execution group; "Keep accountable people in the loop" a paraphrase. | Fixed. |
| 15 | Step-line legend swatch; unlabelled line at 100 in the levels chart. | Fixed. |
