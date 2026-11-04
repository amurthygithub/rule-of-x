# Independent check of the dashboard heatmaps (3 November 2026, 19:45)

Checker: a separate model (Fable), read-only, given the code and data but not the author's conclusions. It recomputed
all cells of `matrices.csv` from `draws_lhs.csv.gz`, `paths.json` and the matched valuation sample; every cell and every
`hm_*` fact reproduced.

| # | Finding | Action |
|---|---|---|
| 1 | Stress-test cells run below the paper's central case (58 in 2036; 7.5-year payback) because each cell averages over all other inputs of the box, with no explanation | Both card notes now say so and give the whole-box medians (52; 10.2 years) |
| 2 | Valuation grid: "cell by cell" and "heavier weight on growth" overstate; the fastest-growth column reverses; the grid pools years while the regressions remove year effects | Text now says four of five growth bands, names the exception, gives the 2020-21 share of the top cell (37% against 18%) and the year-relative corners (2.0x against 0.8x of the year median); public float defined on the card |
| 3 | Payback card said faster execution shortens the wait; the heatmap shows change capacity alone barely does | Reworded: the paper's fast case shortens payback mainly through its higher success rate |
| 4 | Fade threshold read from facts while the element declared only matrices | `data-source="matrices facts"` |
| 5 | New-analysis badge missing on the two new-analysis heatmaps; the quarter pass-through row is not a paper case | Badges added; the note says the quarter row is added |
| 6 | Score grid did not say which score | "Median durable 2036 score (before the cost of changes in flight)" |
| 7 | Lever map colours rescaled with the spend basis | Fixed domain over all bases |
| 8 | Tooltips lacked axis names; lever tooltip lacked basis and rank | Added |
| 9 | Row labels needing three lines lost words | Remainder joined onto the second line |
| 10 | Never-pay-back draws (inf) would silently drop from medians | `biz_matrices.py` asserts none and records the count (0) in `matrices_meta.json` |
| 11 | Threshold grid assumes capital is not deductible | Stated on the card |

Also fixed in this round, from the dashboard's own check (`labels_overlap`, 2): the typical-company line-end labels and
the deciles axis title; and clipped bar and axis labels at phone width. A scan of every chart at ten widths from 360 to
1440 pixels finds no overlapping or clipped labels.
