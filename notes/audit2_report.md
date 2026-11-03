# Pre-submission audit 2: "The Efficient Frontier of Growth and Profitability"

Snapshot audited: sources as of 29 Oct 2026, 00:45 PDT. `paper.tex` changed at 00:34:59 (`\date{\today}` became `\date{October 2026}`) while this audit was running. All other sources are unchanged since 00:30. No file under `/home/claude/paper` was edited except this report. The scratch build (pdflatex, bibtex, pdflatex x3) was run in the session scratchpad.

Method. Every number in the prose of the nine listed files was checked against the `\input` tables, the four notes JSONs, `panel_build_log.txt`, `verify_theory_output.txt` and `tab:ceiling`. Where a number could be recomputed from `data/panel.csv`, `data/panel_broad.csv` or `data/companyfacts_extract.json`, it was. Line numbers refer to each file on its own.

Counts: **4 ERROR, 13 INCONSISTENT, 5 OVERCLAIM, 6 UNSUPPORTED, 5 STYLE (33 findings).**

---

## Findings, most severe first

**1. ERROR: intro.tex:11, 2036 scenario ranges are left over from an earlier draft.**
- *Problem:* The intro says "55 to 120 in 2036, of which ... 55 to 97 points would be durable".
- *Evidence:* `tab_calib.tex:9` gives R\* = 55–122 and R∞ = 55–99. `calibration_results.json` "2036" gives R = [0.55, 1.2243] and Rinf = [0.55, 0.99275]. horizons.tex:15 correctly says "55 to 122 ... 55 to 99". The old values match a margin cap of 67: 67 + 30 = 97, and 97 + 23 = 120. That cap is still named in the docstring of `calibrate_horizons.py` ("favorable case 67"), but the table now uses 69.3.
- *Fix:* In intro.tex:11, write "55 to 122 in 2036, of which 50 to 82, 53 to 85 and 55 to 99 points would be durable". Also correct the docstring.

**2. INCONSISTENT: the "after 2022" decline is measured from 2016–19, not from 2020–22 (abstract.tex:2; intro.tex:9; empirics.tex:8 heading; empirics.tex:69 (v); conclusion.tex:3; horizons.tex:34).**
- *Problem:* Every quoted change ("fell by 12 to 15 points", "did not change") compares 2016–19 with 2023–25 (tab_top, tab_threshold, empirics.tex:18 and 22). "After 2022" leads the reader to compare 2020–22 with 2023–25.
- *Evidence:* On that comparison the P95 changes are −12.0 (GAAP, 56.1 to 44.1) and −17.6 (cash, 62.4 to 44.8) (`empirics_revised.json` top/*/q95). So the cash figure would be 18, not 15.
- *Fix:* Say "between 2016–19 and 2023–25" in the abstract, intro, summary and conclusion. In the abstract this adds about 17 characters (1,891 to about 1,908; the limit is 1,920). Alternatively, report the 2020–22 base explicitly.

**3. OVERCLAIM: "a weight on growth of about 7 or more" is not a lower bound, even on the paper's own account (abstract.tex:2; intro.tex:9; empirics.tex:39 and 69 (ii); discussion.tex:6; model.tex:267).**
- *Problem:* X − k = 3.3/α. That is 7.3 only at the assumed upper end α = 0.45, and α is assumed, not estimated.
- *Problem:* empirics.tex:39 itself says that S&M includes maintenance spend, "which biases the ratio upward". The implied X is therefore overstated at each α, which undercuts "or more".
- *Problem:* The model's σ also includes expansion R&D (Assumption ass:growth), and the proxy omits it. That bias runs the other way, so the net sign is unknown.
- *Evidence:* Median ratio 3.31, IQR 1.88–7.40 (`empirics_revised.json` spend_ratio). This gives X − k from 4.2 (1.88/0.45) to 29.6 (7.40/0.25).
- *Fix:* "implies a weight on growth of roughly 7 to 13 for α in the calibration range (biases of uncertain net sign)", or "well above the screening weights of two to three". In the abstract, delete "or more".

**4. OVERCLAIM: "the best margins attainable at a given growth rate did not change" and "because fewer firms grew fast" (abstract.tex:2; intro.tex:9; empirics.tex:22, "were stable"; empirics.tex:69 (v); conclusion.tex:3; horizons.tex:34, "the binding constraint is the supply of growth opportunity ... not willingness to trade margin for growth").**
- *Problem:* The evidence is non-rejection with wide intervals. At g0 = 40% the intervals are [−20, +31] (GAAP) and [−7, +25] (cash). At g0 = 20% the GAAP change is −9 [−14, +4] (tab_threshold).
- *Problem:* T(0.40) for 2023–25 rests on 18 firm-years, so its "95th percentile" is essentially the sample maximum. It equals the edge statistic the paper rejects as unreliable: tab_edge, GAAP, minimum 15, 2023–25 = 74 = tab_threshold GAAP 40% 2023–25 = 74 (both 0.7418 in `empirics_revised.json`).
- *Problem:* "Because" attaches a causal reading to a descriptive decomposition.
- *Related:* intro.tex:9 says the statistics "do not depend on sample size". empirics.tex:6 says, more accurately, that their *meaning* does not. intro.tex:9 "not at all on the GAAP basis" (slope +0.7, SE 1.3) has the same absence-of-evidence problem.
- *Fix:* "showed no detectable change (wide intervals)"; "coincided with a fall in the number of fast growers"; drop or soften "the binding constraint is". Flag the n = 18 cell, or report g0 = 40% only for periods with at least 30 firm-years.

**5. UNSUPPORTED: the full-automation ceiling rests on unsourced parameters that conflict with the paper's own cited evidence (model.tex:392–402 and tab:ceiling; horizons.tex:18; the abstract's "about 39%").**
- *Problem:* No source or argument is given for c_c ∈ {0.15, 0.20, 0.25}, τ ∈ {0.15, 0.18, 0.21} or f ∈ {0.02, 0.025, 0.03}. Only a_min is calibrated (discussion.tex:17).
- *Problem:* horizons.tex:6 cites ICONIQ gross margins on AI products of 45% (2025), 53% (2026) and 59% (2027). Those margins imply compute shares near 0.4, not 0.2, for an automated firm.
- *Evidence:* The headline threshold is driven by c_c. With c_c = 0.40 and the other central values, the margin term is 0.82 × 0.545 = 44.7 points, and the k = 0 threshold for 100 becomes about 55% rather than 39%.
- *Fix:* Justify c_c, τ and f with sources: falling inference prices (epoch2025inference, gundlach2025price) and cash tax rates of software firms. Add a high-compute row (for example c_c = 0.35–0.40) or state the dependence.

**6. OVERCLAIM: "the best scores of 2023–25 were mostly durable, with a median growth surplus near zero" (intro.tex:11; horizons.tex:11).**
- *Problem:* The inversion sets σ to the S&M share, which the paper itself calls an upper bound. Then Π = (1 − k)Δ − σ, so a spend ratio above 1 makes Π negative by construction.
- *Evidence:* With the lower bound σ = 0 (`m0_lb` in `calibrate_horizons.py`), the 23 top-tail firm-years have median R∞ = 36 (IQR 26–44) and median Π = +25 points (IQR +14 to +30), against 57 and −3 under the upper bound. The conclusion therefore depends on the bound chosen.
- *Knock-on:* With the lower-bound upper-quartile Π (0.296), the implied λh is 0.70–1.02. "10 to 22 times the demand pull" (intro.tex:11; horizons.tex:20) becomes about 7 to 13 times.
- *Also:* The anchor treats Exzeo's missing S&M as σ = 0, a lower bound and not the stated upper bound. It includes 8 acquisition-flagged firm-years, although data.tex:21 says purchased growth "is not the growth the model describes". And it adds pre-tax σ to an after-tax margin, which inflates the after-tax m0 by τσ.
- *Fix:* Report both bounds: "between −3 and +25 points depending on how much S&M is growth spend". Drop "mostly durable" from the intro, or qualify it.

**7. ERROR: empirics.tex:63, Baidu is not in the broad sample.**
- *Evidence:* Baidu (CIK 1329099) appears in `panel_v2_all.csv`, but every row has `rev_lag` and g missing, so it never enters `panel_broad.csv` (0 rows). Meta (SIC 7370) and AppLovin (SIC 7370) are present.
- *Fix:* Replace Baidu with a firm that is in `panel_broad.csv` (for example "Meta and AppLovin").

**8. UNSUPPORTED: data.tex:6, "come from the original filing in 88 to 99.6% of firm-years".**
- *Problem:* No log, JSON or script output contains these figures. `panel_build_log.txt` reports only "items from a later filing 0.351" for any of about 30 items.
- *Evidence:* Re-implementing the fallback rule of `build_panel_v2.py` item by item on `panel.csv` gives the share of core firm-years taken from the original filing:

| Item | Share of all firm-years | Share of firm-years reporting it |
|---|---|---|
| Operating income | 99.5% | 99.8% |
| Operating cash flow | 96.5% | 96.5% |
| Capex | 96.3% | 98.4% |
| SBC | 98.1% | 99.2% |

All four together come from the original filing in 91.0% of firm-years.
- *Fix:* Compute the four shares in `build_panel_v2.py`, write them to the log, and quote them (on this reconstruction, "96 to 99.5%").

**9. INCONSISTENT: horizons.tex:6, "automation raises the full-automation ceiling one for one with the cost it removes".**
- *Problem:* model.tex:348 says the ceiling "rises by 1−τ points for every point of human cost or overhead removed". On the after-tax basis used throughout Section 6, the gain is (1 − τ), not one for one.
- *Problem:* R_max (eq. Rmax) does not depend on c_h or a at all. What rises is R∞, toward R_max. Only lowering a_min, c_c or f moves R_max.
- *Fix:* In both places, write "At given prices, automation raises the saturated score by 1−τ points per point of cost removed, up to the ceiling of Corollary ceiling".

**10. INCONSISTENT: tab_calib.tex:6 (2025 anchor row) against horizons.tex:11 and the table's own note.**
- *Problem:* The text gives a durable score of "57 (49 to 64)", which is the IQR of firm-level R∞ (`calibration_results.json` anchor.Rinf = [0.489, 0.570, 0.643]). The table row gives "Durable R∞ 49–66", which is m0 IQR + G (0.3655 + 0.129, 0.5277 + 0.129).
- *Problem:* R\* 49–81 is R∞ high + Π high and lies above the actual IQR of top-tail scores (50–63, anchor.R).
- *Problem:* The note says "ranges are interquartile ranges", which is true only for the m0 and Π columns.
- *Fix:* Either print the actual IQRs (R∞ 49–64, R 50–63) in the anchor row, or change the note: "m0 and Π are IQRs; R∞ and R\* pair their ends".

**11. INCONSISTENT: empirics.tex:27, firm-period-mean slopes "−0.63 and −0.35" against tab_robust.tex:8 "−0.60, −0.43".**
- *Evidence:* Both come from `empirics_revised.json`. local/*/slopes/firm_means averages after dropping g < 0 (n = 593/580, iid SE). robust/"One observation..." averages all firm-years (n = 649/636).
- *Fix:* Use one definition in both places. Quote the table values in the text, or explain the difference.

**12. OVERCLAIM / UNSUPPORTED: empirics.tex:52, "it appeared as software firms began to build or buy computing capacity for AI".**
- *Problem:* The split is at the 2023–25 median capex intensity of only 2.07% of revenue. The top of the "capital-intensive" half is Clear Secure (2023, 2025), BILL, Cellebrite, CrowdStrike and Paylocity, none of them AI-compute builders. Referee 2 (`referee2_report.md`:54) raised the same point.
- *Problem:* Splitting on capex and comparing FCF-after-capex scores is partly mechanical, because the sorting variable is subtracted from the outcome.
- *Fix:* Delete the AI-compute clause, or support it (for example, show which firms drive the gap). Note that the cash-basis gap is partly an accounting identity.

**13. UNSUPPORTED: appendix_protocol.tex:32, "Every number in the revised paper was regenerated by the scripts in the replication package".**
- *Problem:* No script computes several quoted numbers: the G&A medians 20/12/7% and the Microsoft/Oracle 2.4–3.6% (discussion.tex:17); the 74% median gross margin (horizons.tex:6); the 88% U.S. share and 37% (data.tex:8 and 21); the "88 to 99.6%" (finding 8); the Palantir rank and the CoreWeave and AppLovin figures (data.tex:6 and 24; empirics.tex:69).
- *Evidence:* The values I could recompute are correct: 19.8/12.2/7.3%; 2.40–3.57%; 74.0%; 88.4%; 36.5%; Palantir third (CoreWeave 167, Exzeo 111, Palantir 88).
- *Fix:* Add them to a script, or soften to "regenerated by the scripts or recomputable from the distributed panels".

**14. INCONSISTENT: appendix_data.tex:26, the reproducibility list omits `decompose_gap.py` (writes tab_gap) and `frontier_figures.py` (writes fig_frontier_tangency and fig_saturation).**
- *Problem:* "Running the scripts in that order regenerates every table and figure" is therefore false as written. `make_arxiv.py` REPL_CODE does include both scripts.
- *Fix:* Add both to the list and to the order.

**15. INCONSISTENT: appendix_data.tex:14, "Used only for statistics quoted in Sections horizons and discussion: GeneralAndAdministrativeExpense; GrossProfit...".**
- *Problem:* Gross profit and G&A also drive Table tab:gap in Section 5, which is also quoted in the abstract.
- *Problem:* `ResearchAndDevelopmentExpense`, used for the R&D column of tab:gap, is missing from the element list.
- *Fix:* "Used for Table gap and for statistics quoted in Sections 5–7: ...", and add `ResearchAndDevelopmentExpense`.

**16. ERROR: appendix_protocol.tex:9, "Of the 73 entries in the final bibliography".**
- *Evidence:* The printed bibliography (`paper.bbl`) has 71 items. `thorp2023chatgpt` and `mohapatra2026expectations` sit in `refs.bib` uncited (`ref_verification.md`, Totals).
- *Fix:* "Of the 73 entries in the bibliography file (71 cited) ...", or delete the two uncited entries and recount.

**17. INCONSISTENT (basis): abstract.tex:2, "firms near the frontier earn about 35 points more margin".**
- *Problem:* The 34.6 is GAAP operating margin (tab_gap), while the abstract's other results and the calibration use the cash basis. The intro says "operating margin".
- *Fix:* "about 35 points more operating margin". This adds 10 characters; check the 1,920 limit together with finding 2 (about 1,918).

**18. INCONSISTENT: intro.tex:9, "among firms growing 40 to 60% a year, 28 of those points come from lower selling and marketing expense".**
- *Problem:* "Those points" refers to the 35-point average, but 28.2 is out of that band's own 39.5-point gap.
- *Fix:* "28 of that band's 40-point gap".

**19. INCONSISTENT: intro.tex:13, "The paper builds on three literatures", against literature.tex:3, "five bodies of work".**
- *Fix:* Make them match.

**20. INCONSISTENT: intro.tex:13, "The only academic study of the rule we are aware of", against literature.tex:15, "the only peer-reviewed academic study ... we located".**
- *Evidence:* `ref_verification.md` records an on-topic, non-peer-reviewed academic thesis (Barnds 2025, Princeton) that the authors are aware of.
- *Fix:* Add "peer-reviewed" in the intro.

**21. ERROR (rounding): horizons.tex:20 and intro.tex:11, "a rent of about 90 points".**
- *Evidence:* ρ = 1 − [G + (r − G)k] = 1 − 0.075 = 92.5 points.
- *Fix:* "about 92 points" (or "more than 90").

**22. INCONSISTENT: empirics.tex:39, "the median such firm spent 41% of revenue to grow 11.4 points faster".**
- *Problem:* These are two separate medians (spend_ratio med_sm = 0.412, med_excess = 0.114), not one firm. Their ratio is 3.6, not the reported median ratio of 3.3.
- *Fix:* "the median S&M share was 41% and median excess growth 11.4 points".

**23. INCONSISTENT: refs.bib:817–823, sec2026xbrlapi.**
- *Problem:* `howpublished` reads "XBRL frames endpoint at data.sec.gov/api/xbrl/frames" and the note reads "Data retrieved 28 October 2026". The data now come from the `companyfacts` interface, retrieved on 28 and 29 October (appendix_data.tex:3).
- *Problem:* The frames API returns the last-filed fact (`ref_verification.md`), the opposite of the paper's as-first-reported design.
- *Fix:* Point the entry to companyfacts and use "Data retrieved 28–29 October 2026". Then regenerate `paper.bbl`.

**24. UNSUPPORTED: factual claims about the world without a citation.**
- discussion.tex:6: "For software firms that ratio [EV/revenue] is often well above three". Cite a source, or use depeyrot2018hacking's multiples.
- horizons.tex:15: "reflecting the current surge in demand for AI products". Cite, or say "allowing for".
- empirics.tex:55: "many of them recent listings". This is unverified; give a count or delete it.
- data.tex:14, "the convention behind most company-reported scores", and data.tex:24, "typically combine quarterly year-over-year growth with an adjusted quarterly margin". These rest on one firm (Palantir). Say "as Palantir does", or cite.

**25. UNSUPPORTED: literature.tex:9, "the link between growth and later profit is weak (coad2007testing, davidsson2009growing, ...)".**
- *Evidence:* `ref_verification.md` records Coad (2007) as profit → subsequent growth and Davidsson et al. as profitable firms growing later, which is the opposite direction.
- *Fix:* "the link between growth and profit, in either direction, is weak and varies across samples".

**26. UNSUPPORTED (cross-reference): empirics.tex:58, "It agrees ... with the ordering of Corollary priorities: ... cost of revenue and overhead matter most for slow growers".**
- *Problem:* Corollary cor:priorities (model.tex:218–227) ranks non-discretionary cost (i) and the growth engine (ii). It treats cost of revenue only as worth (1 − φ) of its size (iv), and it ranks nothing for slow growers on cost of revenue.
- *Fix:* "... and overhead matters most for slow growers; the corollary values cost-of-revenue savings only to the extent pricing lets the firm keep them".

**27. INCONSISTENT: model.tex:130, "the Rule of 40 ... accepts an interval of frontier points, some of which may be dominated".**
- *Problem:* Frontier points are undominated by Definition def:frontier. Remark rem:r40 correctly says that a *point that passes* (a feasible point) may be dominated.
- *Fix:* "accepts an interval of frontier points and also dominated points below them".

**28. OVERCLAIM: literature.tex:33, "we model its origin and limits".**
- *Problem:* The paper does not model the rule's origin.
- *Fix:* "we model the frontier it is applied to, and its limits".

**29. STYLE: imprecise cross-references.**
- empirics.tex:6, "which Proposition prop:industry calls the observed frontier Ψ". Ψ is defined in Definition def:industry.
- discussion.tex:8, "exceeds the saturated level R∞". Eq. (Rinf) defines R∞ = m0 + (X − k)G for weight X, but the comparison here is with the Rule-of-40 level m0 + (1 − k)G. Write that expression.

**30. STYLE: printed endpoints do not difference to the printed changes.**
- tab_threshold GAAP 0%: 28 → 31 shown as +2. GAAP 40%: 62 → 74 shown as +13.
- tab_top GAAP P90: 47 → 40 shown as −8. Cash median: 24 → 15 shown as −8.
- tab_robust "means": 71 → 44 = 27, while empirics.tex:63 says "10 to 26".
- tab_calib 2036, k = 0.5: 52.5 is printed as 52 but 92.5 as 93 (half-even against half-up).
- *Fix:* Add a table note ("changes computed before rounding") and use consistent half-rounding.

**31. STYLE: LaTeX comments and a stale arXiv package.**
- model.tex:1–10 has a header comment ("Alias labels kept for other sections ...") and appendix_proofs.tex:1–5 has a header comment. Both are visible if the root sources are uploaded. `make_arxiv.py` strips them in `dist/arxiv`.
- `dist/arxiv` was built at 00:34, before `paper.tex` changed at 00:34:59, so `dist/arxiv/paper.tex` still has `\date{\today}`. `paper.pdf` (00:30) also prints "October 29, 2026".
- *Fix:* Rebuild `dist/` and `paper.pdf` after the last edit, and upload only `dist/arxiv_source.tar.gz`. Optionally delete the two header comments.

**32. STYLE: overfull boxes (scratch build).**
- literature.tex:13, 4.85pt (the Gordon / Miller–Modigliani sentence).
- appendix_proofs.tex:272–274, 1.21pt (inline math).
- The final pass has no undefined references or citations and no rerun warning. BibTeX reports no warnings.

**33. STYLE: miscellaneous.**
- tab_desc uses hyphens in the period labels ("2010-15"); the other tables use en-dashes.
- The PDF has empty Title and Author metadata (add `\hypersetup{pdftitle=...,pdfauthor=...}`).
- The tab_calib note breaks badly after "with the" (Table 12, p. 31).
- horizons.tex:3 quotes "if AI can automate everything, is the limit a Rule of 100 or a Rule of 1000?", which reads as quoting the original prompt. Rephrase it as the paper's own question.
- appendix_protocol.tex:18 says "four scoping questions, recorded in Table decisions", but the table has seven rows and does not mark which four.
- empirics.tex:58 "the 76% of firm-years" should carry the table's qualifier, "with growth of 0 to 60%".
- conclusion.tex:3 "U.S.-listed software": 12% of core firm-years have non-U.S. addresses, so use "SEC-registered".

---

## Checked and found correct

- **Abstract length:** 1,891 characters without markup (limit 1,920; leave room for the fixes in findings 2 and 17).
- **Sample counts:**
  - Core sample 1,929 firm-years and 293 firms, by period 517/458/496/458. Broad sample 3,626 and 541.
  - 662 registrants, 3,641-registrant universe, 35 elements, 240,732 facts. Seven duplicates and three predecessor–successor pairs.
  - Capex missing 2.2%; acquisition flag 24% (36.5% among g > 50%); discontinued operations 6%; U.S. address 88.4%; S&M reported 90%.
  - Filters g ∈ (−0.9, 5) and margins in [−3, 1]; Compustat year convention.
- **Named firms:**
  - AppLovin: restated 2023 revenue $1,841.8M against $2,817.1M is −34.6%, and growth as first reported is +16.5%.
  - CoreWeave: g = 167.9%, m_op = −0.9%, GAAP score 167, cash margin −153.6%, cash score 14.
  - Palantir: FY2025 56%/32%/88, third-highest in 2023–25, highest above $1B apart from CoreWeave.
  - Gen Digital, Clear Secure and Descartes are in the top tail.
- **Pass rates:** 14.8%, 16.9%, 26.7% and 30.9%.
- **Tables recomputed from panel.csv, all matching:** tab_desc (every cell); tab_threshold (every cell and count); tab_local (every cell and n); tab_scale (n, median g, P95); capital-intensity P95 (38 against 53, −15; GAAP −2).
- **Tables matching the JSON:** tab_top, tab_edge, tab_robust, tab_gap (every cell, against `gap_decomposition.json`), tab_calib (2028–2036 rows), the leave-one-out ranges and the SFA shortfalls.
- **Fixed-effects regressions:** +0.08 (0.07) and −0.02 (0.04).
- **Other quoted figures:** spend ratio 3.3 (IQR 1.9–7.4); G&A medians and Microsoft/Oracle; 74% gross margin; edge range 26–50; robust slopes −0.24 to −0.60.
- **Model figures (against `verify_theory_output.txt`, 119/119 checks pass):**
  - Ceiling values, thresholds 31/39/48%, 45-point and 36–38-point capital effects.
  - Λ = 8.71 and 6.8–9.3; λh 0.43–0.71; transience bounds 1.8, 9.6 and 5.0.
  - Screening weights 1.8/2.8 and 5.4/6.2; worked HJB example; quality-condition example; ℓ ≈ 0.86/1.14 and slopes 0.9–1.6.
  - 1/α = 2.2–4; depreciation hurdles 7.5/3.5; free-entry score 7.5; Discussion's −23 points.
- **Anchor values:** 45 (37–53), 57 (49–64), −3 (−13 to +15), and "8 of 23".
- **Figure annotations** match the stated parameters.
- **Cross-references:**
  - Every `\ref` resolves.
  - These match what the citing sentences claim: prop:score(b), prop:industry(i)–(v) and prop:industry-full(iv)–(v), prop:saturation(d), prop:budget, cor:transient, cor:ceiling, cor:capital/cor:substitution, prop:entry, lem:valuation2, prop:dynamic, lem:prices, rem:taxes, and the protocol's prop:industry and prop:capital.
- **Outside sources (against `ref_verification.md` and `audit_report.md`):** Palantir Q2 2026 (93/47/62/155); ICONIQ 45/53/59; Epoch 9–900x; Gundlach 5–10x; Bessemer 2 / 2–3 "if growth is efficient"; Vista; Bain Rule of 30; Bain 16% of 86; Lee 1,756 firms and Rule of 65; arXiv policy wording; SOX 302/906.
- **Protocol claims** match the three referee reports (three major-revision recommendations, the data, statistics, identification and theory points).
- **Hygiene:** no em-dashes or `---` in any .tex file; no TODOs, placeholders or AI meta-comments in the rendered text; the earlier %REFEREEROUND and %FINALDECISIONS placeholders are gone; the PDF has no "??".

---

## Re-audit

Snapshot: sources as of 29 Oct 2026, 01:10 PDT. A scratch rebuild (pdflatex, bibtex, pdflatex ×3) gives 60 pages and no undefined references or citations. The text is identical to `/home/claude/paper/paper.pdf`, and `paper.bbl` is identical to the root copy. `dist/arxiv` matches the comment-stripped sources file by file. `verify_theory_output.txt` reports 120/120.

I re-checked the following against the rebuilt panel (01:02), `calibration_results.json`, `paper_stats.json`, `verify_theory_output.txt` and my own recomputation from `panel.csv`: every number in the changed text listed by the coordinator, tab_calib (every cell) and tab:ceiling (including the new row). The re-run left the table values unchanged.

Abstract length: 1,911 characters without markup with "--" counted as two characters, 1,908 with it counted as one. Both are under the 1,920 limit, but only 9 to 12 characters remain.

### Status of the 33 findings

| # | Status | Reason |
|---|---|---|
| 1 | RESOLVED | The intro's 2028/2031/2036 ranges (49–162 / 45–125 / 42–126 total; 32–82 / 35–85 / 37–99 durable) match the union of the two bounds in `calibration_results.json`. |
| 2 | RESOLVED | "Between 2016–19 and 2023–25" now appears in the abstract, intro, empirics heading and summary, conclusion and horizons:34. |
| 3 | RESOLVED | "Roughly 7 to 13", with "biases of uncertain net sign", in the abstract, intro, empirics:39/69, discussion:6 and model:257. |
| 4 | PARTLY | Fixed everywhere except appendix_protocol.tex:26, which still says the statistics "do not depend on sample size". Change to "whose meaning does not depend on sample size". |
| 5 | RESOLVED | τ, f and c_c are now justified (model.tex:392) and a high-compute row was added (values check). See new finding N1. |
| 6 | RESOLVED | Both bounds, after-tax inversion, acquisition-affected firm-years excluded (n = 15), Exzeo's missing S&M disclosed. The figures check: 42 (35–50), 54 (47–61), +7 (−10 to +18); 24, 36, 25 (17–28); 7–19×. See N2 and N4. |
| 7 | RESOLVED | Baidu removed. |
| 8 | RESOLVED | "96.5 to 99.8%" matches `paper_stats.json` and my reconstruction. |
| 9 | PARTLY | horizons:6 is fixed. model.tex:338 (free-entry intuition) still says "the full-automation ceiling ... rises by 1−τ points for every point of human cost or overhead removed". R_max does not depend on c_h or a; the saturated score rises toward it. |
| 10 | RESOLVED | The anchor row prints actual IQRs (R∞ 47–61, R\* 50–62), and the note says so. |
| 11 | RESOLVED | The text now quotes −0.60 / −0.43 (Table robust). |
| 12 | RESOLVED | Mechanical link and non-AI composition stated. The supporting numbers are unscripted (see 13). |
| 13 | PARTLY | `paper_stats.py` covers the Section 4–7 text statistics. Not written to any output: the firm-level inversion claims (horizons:11: Clear Secure, Palantir/Exzeo 23–48, monday.com more than 20 below); the 2% capex-split threshold and "ordinary software and services firms" (empirics:52). |
| 14 | RESOLVED | `decompose_gap.py`, `paper_stats.py` and `frontier_figures.py` are listed. |
| 15 | RESOLVED | The element list and its uses are corrected, and R&D is added. |
| 16 | RESOLVED | 71 references (62 verified + 9 corrected), 8 dropped; `paper.bbl` has 71 items. |
| 17 | RESOLVED | "Operating margin" in the abstract. |
| 18 | RESOLVED | "28 points of that band's 40-point gap". |
| 19 | RESOLVED | "Several literatures". |
| 20 | RESOLVED | "Peer-reviewed" added. |
| 21 | RESOLVED | "About 92 points" in the intro and horizons:20. |
| 22 | RESOLVED | Separate medians stated. |
| 23 | RESOLVED | The bib entry and `paper.bbl` now cite companyfacts, retrieved 28–29 October. |
| 24 | RESOLVED | EV/revenue claim replaced by the worked example; "current surge" and "recent listings" removed; data.tex now cites Palantir. |
| 25 | RESOLVED | "In either direction". |
| 26 | RESOLVED | The empirics:58 sentence is reworded. |
| 27 | RESOLVED | model.tex:120 reworded. |
| 28 | RESOLVED | "We model the frontier it is applied to, and its limits". |
| 29 | RESOLVED | "Definition~def:industry"; discussion:8 writes m0 + (1 − k)G. |
| 30 | RESOLVED | The tab_top and tab_threshold notes and empirics:63 say "computed before rounding"; tab_calib rounds half up. |
| 31 | RESOLVED | Header comments removed; dist rebuilt at 01:09 and current; `\date{October 2026}`. |
| 32 | OPEN | The two overfull boxes remain: literature.tex:13 (4.85pt) and appendix_proofs.tex:267–269 (1.21pt). |
| 33 | RESOLVED | En-dashes in tab_desc; PDF title and author metadata set; horizons:3 rephrased; the four scoping questions named; the 0–60% qualifier added; "SEC-registered". |

### New findings in changed text

**N1. INCONSISTENT: intro.tex:14, horizons.tex:18 and horizons.tex:20 describe the high-compute case as compute "as costly as in today's AI products".**
- model.tex:392 describes c_c = 0.40 as the cost of revenue implied by the gross margins *projected for 2027* (59%).
- The case's cost of revenue (c_c + f = 42.5%) is well below today's level: ICONIQ puts gross margins at 45% in 2025, so cost of revenue is about 55%, and 47% for 2026.
- *Fix:* "if compute stays as costly as projected for AI products in 2027". Alternatively, add a case at today's level: with c_c ≈ 0.53 the margin term is about 34 points and the threshold about 66%.

**N2. OVERCLAIM (minor): horizons.tex:11, "Clear Secure's scores for 2024 and 2025 were durable under either bound".**
- Under the lower bound, the 2024 surplus is 12 of 58 points, about 21% of the score, which is more than the "eighth" the paper calls the low end. The 2025 surplus is 3 points.
- *Fix:* "mostly durable under either bound (surplus at most 12 points)".

**N3. STYLE: horizons.tex:9 uses two different sets of "8 firm-years".**
- "8 of the 23 ... had cash margins above the 95th-percentile margin" and "leaving out the 8 firm-years affected by acquisitions" are different sets, of which 3 overlap.
- *Fix:* Say so, or give the second set in other words ("the acquisition-affected firm-years, also 8").

**N4. UNSUPPORTED (note): the upper bound on σ is not credible for the heaviest S&M spenders.**
- monday.com's upper-bound intercept is 64–65 points and its durable score 76–78. That exceeds the central full-automation margin term (61) and the central ceiling at G = 12.9% (74), which by Corollary cor:ceiling bound m0 and R∞.
- The text's conditional statement (horizons:11) is correct as worded.
- *Fix:* Add a clause noting that for such firms the upper bound exceeds the model's own ceiling and is therefore an overstatement.

Counts for this round: 1 OPEN, 3 PARTLY, 29 RESOLVED; 4 new findings (1 INCONSISTENT, 1 OVERCLAIM, 1 STYLE, 1 UNSUPPORTED).
