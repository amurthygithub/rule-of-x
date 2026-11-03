# Literature pass, revision v2 (Paper 1)

Literature agent, 29 October 2026. Accuracy rule: no reference was written to the .bib unless its bibliographic record was read at a registry, publisher, working-paper series, preprint server or issuer page on 29 October 2026. No existing .tex or .bib file was edited.

Deliverables (all new files):
- `paper1/refs_additions_v2.bib` (89 entries).
- `sections/tables/tab_param_sources.tex` (longtable, 44 rows, five columns; needs `\usepackage{longtable}`; `\input` it in an appendix).
- this note.

Scratch compile (table plus both bib files, `\nocite{*}`, plainnat): no LaTeX errors; BibTeX reports only the 8 "Repeated entry" messages for the 8 corrected keys, which is the intended behavior when the additions file is listed first.

Route codes used below: CR = Crossref works record (registry); RePEc = EconPapers or IDEAS page (aggregator; a second source, and the only one for Dixit-Stiglitz); NBER, arXiv, PMLR, AEA, OUP, SD (ScienceDirect), INFORMS, Springer, OSTI = series, preprint or publisher page; official = regulator, statute, issuer or agency page; PUB = web page of a survey sponsor, vendor or consultancy. "[record only]" means I verified the bibliographic record but did not read the abstract or text, so the relation sentence rests on the title and on the referee's description. All read dates are 29 Oct 2026.

Counts (details in section f):
- 89 references verified and written to the .bib: 8 corrected (same key, `note` says what changed) and 81 added (59 new to every bib file, 22 already present in part2 under the same key).
- 21 corrections of source claims, at 16 distinct .tex lines (section a; four corrections share sections/literature.tex:27 and two share each of horizons.tex:6 and horizons.tex:13).
- 6 references and about 30 specific figures or details could not be verified (section c).

---

## a. Corrections

### A1. Demirer, Fradkin, Tadelis, Peng: a within-model substitution elasticity used as a demand elasticity (most consequential)

Sources read: NBER w34608 page (abstract); author PDF dated 12 December 2025 (mertdemirer.com/Papers/Demirer_LLM_demand.pdf; no version number); AEA page for the JEP article.

What the source says:
- Abstract (NBER): "Fifth, we estimate preliminary short-run price elasticities just above one, suggesting limited scope for Jevons-Paradox effects." Also: open-source models 90% cheaper than comparable closed-source models.
- Section 7.2: unit is daily total tokens for provider i offering model m on date t; fixed effects for date-by-model and provider-model; price variation is entry and exit of providers of the same model and price changes by existing providers; "Our data for this estimation comprises just open-source models".
- Section 7.3, Table 2, specification (3) (preferred): log price coefficient -1.11, standard error 0.22, 32,539 observations. Specification (2): -1.08 (0.19). Specification (1), date fixed effects only: -0.55 (0.09). Footnote 19: some price sensitivity may reflect OpenRouter's routing rather than user choice.
- Section 7.1: "Model-provider level elasticities are larger in magnitude than the corresponding aggregate elasticity."
- Section 7.3: "Since aggregate demand elasticities are substantially smaller, we interpret our findings as going against the Jevons paradox in the short-run." And: "This, however, does not preclude from Jevons effects operating on longer-run horizons."
- JEP article (40(3):23-46, doi 10.1257/jep.20261506): the AEA abstract reports supply growth, a roughly thousandfold fall in the price of intelligence, 90% cheaper open models, turnover and differentiation. It does not mention an elasticity. I did not read the full text.

Accurate characterization: about -1.1 is a preliminary elasticity of a provider's tokens with respect to its own price, among providers of the same open-weight model. It measures substitution between providers of an identical model. It is not firm demand or market demand for inference, and the authors say aggregate elasticities are substantially smaller. With an aggregate elasticity below one, spending on inference falls when its price falls, which is the opposite of "spending stays roughly constant". At the provider level an elasticity near one does mean a provider's token revenue is roughly insensitive to its own price; that is the only sense in which "roughly constant" is true. The source gives no basis for "the compute share need not fall"; that outcome would have to come from rising token volume per task (Gundlach et al., Section 5), which is a scenario.

Why it matters: the elasticity sentence was the paper's textual argument for keeping the compute share c_c high. Round 2 (`notes/assumptions_round2.md` lines 122, 133 and 137) already concludes that "R4-F1 is right", lowers c_c and moves the headline threshold G* from 42.3% to about 32.5-35.7%, the single largest mover of the round. The text and the citations still say the opposite, so these five locations must change together with the parameters.

Bib: `demirer2025emerging` and `demirer2026emerging` replaced (notes added). Cite the NBER paper for the elasticity (labelled preliminary and within-model); cite the JEP article for market facts only.

Locations, old to new:

| File:line | Old | New |
|---|---|---|
| sections/literature.tex:27 | "while short-run price elasticities of demand for inference just above one \citep{demirer2025emerging,demirer2026emerging} mean that spending on inference, and the compute share of our ceiling, need not fall." | "The estimate we cite for the price elasticity of demand for inference, a preliminary $-1.1$ across providers of the same open model, measures substitution between providers, and its authors report that aggregate elasticities are substantially smaller \citep{demirer2025emerging}; whether spending on inference, and the compute share of our ceiling, rise or fall is therefore a scenario, not an implication of a measured elasticity." (The sentence also carries the Gundlach correction A3; a combined sentence is given there.) |
| sections/horizons.tex:6 | "and with a short-run price elasticity of demand for inference just above one \citep{demirer2025emerging}, spending on inference stays roughly constant as its price falls, so the compute share need not decline." | "and whether the compute share declines depends on how fast the volume of inference per task grows against the fall in its price, for which there is no market-level estimate: the preliminary elasticity of about $-1.1$ across providers of the same open model \citep{demirer2025emerging} measures substitution between providers, and its authors report that aggregate elasticities are substantially smaller." |
| part2/literature_modern.tex:21 | "and short-run price elasticities just above one \citep{demirer2025emerging,demirer2026emerging}. With an elasticity near one, spending on inference stays roughly constant as prices fall, so the compute share of Part I need not decline." | "and a preliminary within-model price elasticity of about $-1.1$ across providers of the same open model \citep{demirer2025emerging}, which measures substitution between providers; the authors report that aggregate elasticities are substantially smaller, so whether spending on inference, and with it the compute share of Part I, falls with its price is open." Keep `demirer2026emerging` only on the market facts (price fall, 90% cheaper open models). |
| part2/theory_core.tex:76 | "With a price elasticity of inference demand just above one, as measured in API data \citep{demirer2025emerging}, inference spend $\pi N(\pi)$ is roughly constant as prices fall, so Part I's compute share $c_c$ need not decline with $\pi$." | "If the price elasticity of inference demand is near one, inference spend $\pi N(\pi)$ is roughly constant as prices fall and Part I's compute share $c_c$ need not decline with $\pi$; if it is below one, spend falls with the price. The only API-data estimate, a preliminary $-1.1$ across providers of identical open models \citep{demirer2025emerging}, measures substitution between providers, and its authors report that aggregate elasticities are substantially smaller, so the near-one case is a scenario." |
| part2/theory_product.tex:162 | "with short-run price elasticities of inference demand just above one \citep{demirer2025emerging}, spending on inference barely falls as prices do." | "the preliminary cross-provider elasticity of about $-1.1$ for identical open models \citep{demirer2025emerging} does not show how spending on inference moves with its price, because the authors report that aggregate elasticities are substantially smaller." |

Unchanged and correct: part2/theory_product.tex:158 ("Open models currently sell for about 90% less than comparable closed ones", abstract of the NBER paper). Round-2 note `notes/assumptions_round2.md:181` uses the -1.11 only as support for near-full pass-through between identical models, which the source supports; line 279 ("no per-firm aggregate elasticity") is right.

### A2. ICONIQ 2026 State of AI: scope of the sample and of the margin; internal spend; projections

Source read: iconiq.com/growth/reports/state-of-ai-2026 (two reads).

What the source says:
- "2026 State of AI Report: The Builder's Economy", July 2026 edition, third in the series. Proprietary Q2 2026 survey of about 300 executives at "software companies building AI products" (CEOs, heads of engineering, AI, product; revenue from $1-5M to over $1B; 87% North America, 13% Europe). Some question samples are below 300.
- AI product gross margin: "jumping from 45% in 2025 to a projected 53% in 2026, and 59% in 2027". These are average gross margins on AI products, not company-wide margins. The report calls its figures forward-looking and illustrative.
- "Spending on AI for internal productivity, including direct and indirect spend, is projected to rise from 11% of revenue in 2025 to 16% in 2026, heading toward 19% in 2027." "And many companies underestimate the true cost." The page does not define direct or indirect and does not say what the spend contains.
- "Talent ... the largest cost category but declining as products scale" is the chart text for customer-facing AI product costs, not for internal spend.

Accurate characterization:
- The 45/53/59% margins are the cost structure of AI products sold to customers by AI-building software firms (talent, hosting and inference). They are not the compute cost of a firm automating its own operations. 2025 is presented as realized; 2026 and 2027 are projections.
- The 11% (16%, 19%) internal AI spend is not itemized; whether it contains compute alone or tools, people and infrastructure is not stated, so it bounds an internal compute share from above only if it contains more than compute. It is the closest ICONIQ number to an internal share and sits far below 55%.
- Round-2 notes (`notes/assumptions_round2.md:117`) say the spend is "all-in (tools, people, infrastructure)" and that "talent is the largest category" of it. Neither statement is in the report for internal spend.

Bib: `iconiq2026state` replaced (sample, projections, scope in the note; url without "www").

Locations:

| File:line | Old | New |
|---|---|---|
| sections/horizons.tex:6 | "Survey evidence puts gross margins on AI products near 45% in 2025 and projects 53% in 2026 and 59% in 2027 \citep{iconiq2026state}, below the median gross margin of \MedGrossMargin% in our core sample in 2023--25, so automation shifts cost from operating expense into cost of revenue rather than removing it." | "A survey of about 300 executives at software companies building AI products puts the gross margin on those products near 45% in 2025 and projects 53% in 2026 and 59% in 2027 \citep{iconiq2026state}. That is the cost structure of AI products sold to customers, including talent and hosting, not the cost of automating a firm's own work; it is below the median gross margin of \MedGrossMargin% in our core sample in 2023--25, consistent with automation shifting cost from operating expense into cost of revenue rather than removing it." |
| sections/horizons.tex:13 (\CcHi clause) | "to \CcHi% (the 2025 cost of revenue of AI products, \citealp{iconiq2026state})" | "to \CcHi% (the 2025 cost of revenue of AI products sold to customers, \citealp{iconiq2026state}, which includes talent and hosting and so overstates the compute cost of a firm's own automation; the same survey puts spending on AI for internal productivity at 11% of revenue in 2025, projected at 16% in 2026, direct and indirect and not itemized)". Treat \CcHi as an upper bound. |
| sections/horizons.tex:13 (\CcHigh clause) | "roughly the cost of revenue implied by the gross margins projected for AI products in 2027" | Unchanged in substance (100 - 59 = 41 against \CcHigh = 40, and "projected" is already there). |
| part2/theory_product.tex:177 | "AI product gross margins of 45% in 2025, 53% in 2026 and a projected 59% in 2027 \citep{iconiq2026state}" | "AI product gross margins of 45% in 2025 and projected values of 53% in 2026 and 59% in 2027 \citep{iconiq2026state}" |

Also fix `notes/assumptions_round2.md:117` (not a .tex file): "talent largest" belongs to customer-facing products; the internal spend is not itemized.

### A3. Gundlach, Lynch, Mertens, Thompson: scope of the 5-10x and the 3-18x

Sources read: arxiv.org/abs/2511.23455 (v2 of 23 March 2026; first submitted 28 November 2025); arxiv.org/html/2511.23455 (Section 2.3, Tables 1 and 2, Section 5, Figure 9, Section 7). Preprint.

What the source says:
- Abstract: price at fixed performance "has decreased remarkably fast, around 5x to 10x per year" for frontier models; "the price of running frontier models is rising between 3x to 18x per year".
- Section 2.3: "with prices reducing annually by a factor of 5-10x for models on the cost-performance Pareto-frontier" (April 2024 to November 2025; Artificial Analysis prices times Epoch AI token counts). Table 1 (Pareto sample, not hardware-adjusted): GPQA-Diamond 5.315 (90% interval 2.449 to 11.534, n = 53); AIME 11.664 (5.250 to 25.911, n = 42); SWE-bench Verified 4.675 (0.680 to 32.156, n = 13). All-model estimates are smaller (GPQA-Diamond 3.769, AIME 6.988). Table 2, hardware-adjusted: 3.720, 8.165, 3.273. Section 7 says the SWE-bench data "are consistent with there having been no progress at all".
- Section 5, Figure 9: the cost of running the record (best-performing) model on each benchmark "increased at an approximately exponential rate, on the order of 3-18x per year". It is total benchmark cost (tokens times price), not per-token price. Only the combined range is given; no interval or regression table.

Accurate characterization: the 5-10x is a price at fixed performance for frontier-sample models (rounded; AIME 11.7 is above the range; SWE-bench is statistically uninformative). The 3-18x is a different object: the cost of reaching record performance, rising because token volume per task rises.

Bib: `gundlach2025price` replaced (note carries the numbers above).

Locations:

| File:line | Old | New |
|---|---|---|
| sections/literature.tex:27 | "or about 5 to 10 times per year at fixed performance \citep{gundlach2025price}" | "or about 5 to 10 times per year at fixed performance for models on the cost-performance frontier, while the cost of running the best-performing model on a benchmark rose 3 to 18 times per year as token volumes grew \citep{gundlach2025price}" |
| part2/theory_ext.tex:214 (first sentence) | "about 5 to 10 times a year \citep{gundlach2025price}" | add "for models on the cost-performance frontier" |
| part2/theory_ext.tex:214 (second sentence) | "The price of the frontier model itself has risen \citep{gundlach2025price}, so an activity that has only just become feasible starts at the frontier price." | "The cost of running the frontier model on a benchmark has risen \citep{gundlach2025price}, because the tokens used per task have risen, not because per-token prices have, so an activity that has only just become feasible starts at the frontier cost." |
| part2/literature_part2.tex:11 | "who also find that the price of running the frontier model rose by 3 to 18 times a year" | "who also find that the cost of running the record-performance model on each benchmark rose by 3 to 18 times a year" |

Combined replacement for the cost sentence at sections/literature.tex:27 (A1 and A3 together):

"On costs, the price of reaching fixed benchmark performance fell between roughly 9 and 900 times per year depending on the task \citep{epoch2025inference}, and by about 5 to 10 times per year for models on the cost-performance frontier \citep{gundlach2025price}, while the cost of running the best-performing model on a benchmark rose 3 to 18 times per year as token volumes grew \citep{gundlach2025price}. The estimate we cite for the price elasticity of demand for inference, a preliminary $-1.1$ across providers of the same open model, measures substitution between providers, and its authors report that aggregate elasticities are substantially smaller \citep{demirer2025emerging}; whether spending on inference, and the compute share of our ceiling, rise or fall is therefore a scenario."

Unchanged and correct: part2/theory_product.tex:162 first clause ("far below delta_pi when products move to newer models and use more tokens per task"); the table row in `tab_param_sources.tex` already states both.

### A4. Bonney et al.: two series, a question change, and an association

Sources read: NBER w32319 and w35141 (abstracts); census.gov/hfp/btos/downloads/AI Question Wording Updates.pdf; Federal Reserve FEDS Note (Allen, 3 April 2026, doi 10.17016/2380-7172.4032).

What the sources say:
- w32319 (April 2024): BTOS bi-weekly estimates of AI use rose "from 3.7% to 5.4%" from September 2023 to February 2024, with about 6.6% expected by early fall 2024.
- Census wording page: old question "In the last two weeks, did this business use Artificial Intelligence (AI) in producing goods or services?"; new question, fielded from 17 November 2025, "... in any of its business functions?". A level shift appeared, so Census created a separate time series (data released 4 December 2025).
- Allen (FEDS Notes): "In November 2025, the Census Bureau broadened the AI-related questions"; the jump between the new and legacy series across five industries "ranged from 47 percent (10.6 percentage points) for professional services" to "159 percent (7.5 percentage points) for manufacturing"; adoption "stood at about 18 percent of firms at the end of 2025" (four-period moving average); the legacy series had grown 68% (3.9 points) over the prior year. The note says the move from the legacy level to 18% should not be read as a clean before-and-after comparison.
- w35141 (April 2026): "During Nov 2025-Jan 2026, 18% of firms used AI in at least one function (32%, employment-weighted)"; "Among adopters, scope remains limited: 57% use AI in three or fewer functions"; "Most firms (66%) use AI for task augmentation, while employment reductions are rare (2%)"; "Regression results show a positive relationship between firm performance and AI integration breadth"; "functional deployment and operational investment are associated with employment declines". The abstract does not state the base of the 66% and 2%. The old `note` on a Census CES working paper number (26-25) could not be confirmed and is dropped.

Accurate characterization: 3.7% (September 2023) to 5.4% (February 2024) is use in producing goods or services; 18% (Nov 2025 to Jan 2026) is use in any business function under a broader question. Neither the 3.7%-to-18% sequence nor any growth rate across the break is a measured change in adoption. The performance result is a regression association.

Bib: `bonney2024tracking` and `bonney2026microstructure` replaced (doi added to the second; CES note dropped); new `census2025btoswording` and `allen2026monitoring`.

Locations:

| File:line | Old | New |
|---|---|---|
| sections/literature.tex:27 | "firm use rose from 3.7% of firms in September 2023 \citep{bonney2024tracking} to 18% by early 2026, most adopters use AI in three or fewer business functions, and performance rises with the breadth of integration \citep{bonney2026microstructure}." | "firm use of AI in producing goods or services rose from 3.7% of firms in September 2023 to 5.4% in February 2024 \citep{bonney2024tracking}; the Census Bureau then broadened the question to use in any business function, which raised measured adoption by 47% to 159% in each of five industries \citep{allen2026monitoring,census2025btoswording}, and under the new question 18% of firms (32% weighted by employment) used AI in November 2025 to January 2026, 57% of these adopters in three or fewer functions, with firm performance positively associated with the breadth of integration \citep{bonney2026microstructure}." |
| part2/literature_modern.tex:19 | "Firm use rose from 3.7 percent of firms in September 2023 \citep{bonney2024tracking} to 18 percent, or 32 percent weighted by employment, by early 2026. Two-thirds of adopters mainly augment, 2 percent report cutting employment, and performance rises with the breadth of integration \citep{bonney2026microstructure}." | "Under the original question, use in producing goods or services rose from 3.7 percent of firms in September 2023 to 5.4 percent in February 2024 \citep{bonney2024tracking}. Under the broader question introduced in November 2025 (use in any business function), which is a separate series, 18 percent of firms, or 32 percent weighted by employment, used AI in November 2025 to January 2026 \citep{bonney2026microstructure,allen2026monitoring,census2025btoswording}. Most firms (66 percent) use AI for task augmentation, employment reductions are rare (2 percent), and firm performance is positively associated with the breadth of integration \citep{bonney2026microstructure}." (The base of the 66 and 2 percent is not stated in the abstract.) |
| part2/theory_core.tex:182 | "performance rises with the breadth of AI integration across business functions \citep{bonney2026microstructure}, as the integration premium predicts." | "firm performance is positively associated with the breadth of AI integration across business functions \citep{bonney2026microstructure}, an association rather than an effect, consistent with the integration premium." |
| part2/theory_core.tex:224 | "by early 2026, 18% of US firms used AI, most of them in three or fewer business functions and two-thirds mainly to augment work \citep{bonney2026microstructure}." | "in November 2025 to January 2026, 18% of US firms used AI in at least one business function, 57% of adopters in three or fewer functions, and 66% of firms used AI for task augmentation \citep{bonney2026microstructure}." |

### A5. Terry (2023): lower R&D growth, not cuts in R&D spending

Sources read: IDEAS page for Econometrica 91(5):1881-1912 (abstract); Crossref works record doi 10.3982/ECTA15420 (given name "Stephen J.").

What the source says: "In the data, firms just meeting Wall Street forecasts have lower R&D growth and subsequent innovation, while managers just missing receive lower pay." An estimated quantitative endogenous growth model: short-termism boosts firm value modestly but slows aggregate growth (the IDEAS summary gives about 5 basis points a year and about 1% of welfare; I read that figure in a paraphrase, so check it in the article before quoting it).

Accurate characterization: firms that just meet forecasts have lower R&D growth and subsequent innovation. The abstract does not say they cut R&D spending.

Bib: `terry2023macro` replaced (author "Terry, Stephen J.").

Locations:

| File:line | Old | New |
|---|---|---|
| sections/literature.tex:13 | "firms that just meet analyst forecasts cut research spending, and in an estimated growth model short-termism slows growth \citep{terry2023macro}" | "firms that just meet analyst forecasts have lower R&D growth and subsequent innovation, and in an estimated growth model short-termism slows growth \citep{terry2023macro}" |
| part2/literature_modern.tex:23 | "Short-termism cuts R&D and slows growth \citep{terry2023macro}" | "Short-termism goes with lower R&D growth and, in an estimated model, slows growth \citep{terry2023macro}" |
| part2/theory_regimes.tex:132 | "managing to forecasts cuts R&D and slows growth \citep{terry2023macro}" | "managing to forecasts goes with lower R&D growth and, in an estimated model, slows growth \citep{terry2023macro}" |

### A6. Hampole, Papanikolaou, Schmidt, Seegmiller: employment share within firms, and an instrumented growth effect

Sources read: NBER w33509 page; NBER PDF (introduction, Sections 1.2, 3.2, 3.3, the measurement section). Working paper, "not peer-reviewed" (NBER), issued February 2025, revised September 2025.

What the source says:
- Abstract: "Two variables summarize the impact of AI on within-firm labor demand: the mean exposure of an occupation's tasks" (and the concentration of exposure); "overall employment effects are modest, as reduced demand in exposed occupations is offset by productivity-driven increases in labor demand at AI-adopting firms". The abstract does not say firms "grow".
- Introduction: "a one-standard deviation increase in mean task exposure reduces the occupation's within-firm employment share ... by about 14.5 percent over five years, while a similar increase in concentration raises it by about 7.5 percent." Also: "Using our instrument, we find that adoption of AI by firms leads to higher growth in revenue, measured productivity, profits, and employment."
- Section 3.2, Table 4 (IV, five-year growth, one standard deviation): +9.7 percentage points in revenue growth, +7.5 in total factor productivity growth, +6.8 in employment (IV estimates "about 30 percent larger than OLS"). AI adoption is the count of internally developed AI applications extracted from resumes (Revelio Labs), Compustat firms, 2014 to 2023; the authors note that only internally developed applications are captured. Instrument: shift-share built on university hiring.

Accurate characterization: the occupation-level result is about employment share within a firm, not labor demand in aggregate; and the firm-growth result sits in the body (instrumented, Table 4), not the abstract. Add the working-paper status where the claim is made.

Bib: `hampole2025artificial` replaced (doi 10.3386/w33509, revision, measurement in the note).

Locations:

| File:line | Old | New |
|---|---|---|
| sections/literature.tex:27 | "task-level exposure lowers labor demand while adopting firms grow \citep{hampole2025artificial}; both are working papers." | "within firms, an occupation's employment share falls with the mean exposure of its tasks (about 14.5% over five years per standard deviation) and rises with the concentration of exposure (about 7.5%), while firms that adopt AI, instrumented by a university-hiring shift-share, grow faster in revenue, productivity and employment \citep{hampole2025artificial}; both are working papers." |
| part2/literature_modern.tex:17 | "Task-level exposure lowers labor demand, but concentrated exposure lets workers shift their effort, and adopting firms grow \citep{hampole2025artificial}." | "Within firms, occupations whose tasks are on average more exposed lose employment share, while concentrated exposure offsets part of that loss, and firms that adopt AI (instrumented) grow faster \citep{hampole2025artificial}." ("lets workers shift their effort" is not in the abstract or the passages read.) |

### A7. METR: run-cost bound and time-horizon figures (used but uncited)

Sources read: arxiv.org/abs/2503.14499 (versions: v1 18 Mar 2025, v2 30 Mar 2025, v3 25 Feb 2026, v4 10 Jul 2026; NeurIPS 2025) and the v4 PDF; metr.org/blog/2026-01-29-time-horizon-1-1/ (Time Horizon 1.1); github.com/METR/eval-analysis-public (README).

What the sources say:
- Run cost (Kwa et al. v4, discussion paragraph "More use of inference compute"; Figure 14, Appendix G): "When assuming that the human expert is compensated at $143.61/hour (average L4 Engineer salary at Google divided by 2,000 hours), more than 80% of successful runs cost less than 10% of what it would cost for a human to perform the same task." This is a bound, not a share. The paper reports no median or mean cost share.
- The public repository README describes the DVC pipeline and `runs.jsonl` (key fields task_id, task_family, alias, score_binarized, score_cont, human_minutes, invsqrt_task_weight) and lists no cost field; the full schema is not shown, so I cannot confirm where a cost share would come from. The 0.44% (Claude Opus 4.5), 1.1% (Claude 4.1 Opus) and 1.0% (o3) shares in `notes/assumptions_round2.md:119` are therefore not confirmed at the source; treat as our computation.
- Time horizon, Kwa et al. v4 (abstract): the 50% time horizon "has been doubling approximately every seven months since 2019" (the authors say the trend "may have accelerated in 2024"). Section 3.2: "time horizon has doubled every 207 days", 95% bootstrapped interval 166 to 240 days. Section 4.1: "the doubling time predicted by HCAST + SWAA + RE-bench using 2024 models is 143 days" (no interval; this is a prediction from 2024 models, not an estimate for models released since 2024). Section 3.2.1: "models' 80% time horizons are 4-6x shorter". Part2's figures match v4.
- Time Horizon 1.1 (METR, 29 January 2026): suite enlarged from 170 to 228 tasks; 50% horizon doubling time 130.8 days since 2023 (interval 107 to 161) and 88.6 days since 2024 under TH1.1, against 165.3 days (129 to 211) and 108.9 days under TH1.0. The post says nothing about run cost and does not report 80% horizons.

Accurate characterization: cite `kwa2025measuring` for the bound and `metr2026evalanalysis` for the data; say that the 1% central value is our computation from METR's public run data; do not attribute a median share to the paper.

Bib: `kwa2025measuring` (note corrected: it reports the bound), new `metr2026th11`, `metr2026evalanalysis`.

Locations:

| File:line | Old | New |
|---|---|---|
| sections/horizons.tex:13 | "Its credible bounds run from \CcLo% (labor replaced at today's observed inference cost)" (no citation; no other METR mention in P1) | "Its credible bounds run from \CcLo% (labor replaced at the cost of today's agent runs: on METR's software tasks more than 80% of successful runs cost less than 10% of the human cost at $143.61 an hour \citep{kwa2025measuring}; the 1% is our computation from METR's public run data \citep{metr2026evalanalysis})" |

Optional sentence for `sec:horizons-ranges` if the editors answer the referee's objection that the horizons are not tied to METR: "METR's 50 percent time horizon doubled every 207 days (95 percent bootstrap interval 166 to 240) between 2019 and early 2025 \citep{kwa2025measuring} and every 131 days since 2023 and 89 days since 2024 in METR's January 2026 update \citep{metr2026th11}; horizons at 80 percent success are 4 to 6 times shorter \citep{kwa2025measuring}. These measure software tasks at 50 percent success, not the pace of organizational change."

### A8. Other characterizations corrected in the .bib or the table (no P1 text change needed)

- Stevens (2026): the 0.03 is dollars of additional AI spending per dollar of decline in online-labor-marketplace spending, among the most exposed firms (arXiv:2602.00139, 28 January 2026). New key `stevens2026payrolls`.
- Foster-Haltiwanger-Syverson is in Economica 83(329):91-129 (2016), not the AER.
- Ge-Koester-McVay: the $388M, $719M and $935M are aggregates for exempt firms over 2007-2014, not a per-firm attestation cost.
- Benedek-de Mooij-Wingender: the IMF working-paper page lists three authors; round 2 lists four. A later version with a fourth author (Keen) was not read.
- Humlum-Vestergaard: retitled "Still Waters, Rapid Currents: Early Labor Market Transformation under Generative AI" (earlier "Large Language Models, Small Labor Market Effects"; NBER w33777, revised March 2026).
- Sethuraman et al. (2011): mean elasticities 0.12 (short term) and 0.24 (long term) are elasticities of the sales level, so they cannot ground alpha (the table row says so).

---

## b. New references

Relation labels: special case (P1's result is a case of the cited framework), extends (P1 adds structure or a new object to the cited framework), new (no counterpart found), context (background P1 takes as given). P1's results referred to: growth technology g = G + lambda sigma^alpha h(s) (Assumption growth); Proposition dynamic (the firm's weight is the marginal q of revenue, v'(s)); score budget and non-identification (prop:budget, prop:industry-full); free entry with a scarce input (prop:entry); AI mapping (prop:ai); full-cost floors and the accountability floor with a common-mode term (lem:fullcost, prop:amin); attainable and expected frontiers (prop:attainable, prop:expected); value-based objectives (prop:general). The referee (Fable, io_ai and theory reports) holds that the growth technology is a customer-capital structure and that marginal q of revenue parallels the q-theory of advertising; the sentences below accept that and say what remains new.

### b1. Customer capital, market penetration and the q-theory of advertising

| Key | Citation and route | Relation to P1 |
|---|---|---|
| `arkolakis2010market` | Arkolakis, JPE 118(6):1151-1199 (2010), doi 10.1086/657949. Routes: CR, NBER w14214 (August 2008), RePEc. Abstract read: a firm enters a market if it can profit from reaching a single consumer; reaching more consumers involves rising marginal penetration costs. | Context and extends. Rising marginal cost of reaching additional consumers is the microfoundation that alpha < 1 and the headroom term h(s) stand in for. P1 takes the reduced form as an assumption; it does not model entry into markets or trade. P1's contribution on top of it is the frontier and score reading, not the growth technology. |
| `gourio2014customer` | Gourio and Rudanko, REStud 81(3):1102-1136 (2014), doi 10.1093/restud/rdu007. Routes: CR, OUP page, RePEc. Abstract read: search frictions generate long-term customer relationships; the customer base is a slow-moving state variable; firms spend on marketing and selling to acquire customers; effects on investment, profits, value, sales, markups and the link between investment and Tobin's q; tested on Compustat using cross-industry differences in selling expenses. | Special case in structure. P1's share S is a customer base, sigma is selling spend, and the marginal value of revenue v'(s) is the marginal value of a customer. Proposition dynamic is the customer-capital first-order condition in the revenue-and-market-size normalization. What P1 adds is the reading of the optimum as maximizing a Rule-of-X score at weight v'(s), and the contrast between that weight (a valuation multiple, 5 to 15) and the investor's screening weight (2 to 3). Position as a customer-capital model with the score as a new interpretation. |
| `drozd2012understanding` | Drozd and Nosal, AER 102(1):364-395 (2012), doi 10.1257/aer.102.1.364. Routes: AEA page, RePEc. Abstract read: a capital-theoretic model of marketing in which customer relationships have value; friction calibrated from the gap between short-run and long-run price elasticities of trade flows. | Context. Same asset view of customers (marketing as investment in customer capital). P1 identifies the friction from a different moment: the ratio of growth spend to excess growth, sigma* = alpha (X - k) Delta*, which reveals alpha (X - k). |
| `foster2016slow` | Foster, Haltiwanger and Syverson, Economica 83(329):91-129 (2016), doi 10.1111/ecca.12172. Routes: CR, NBER w17853, Maryland author PDF, RePEc. Abstract read: new plants stay small because of demand-side fundamentals; a dynamic model with a demand accumulation process (building a customer base); "active accumulation driven by plants' past production decisions quantitatively dominates passive demand accumulation". Not in the AER (referee error). | Context and support. Evidence that customer-base accumulation is driven by past spending, which is the assumption behind the sigma-to-growth technology. P1 does not estimate this structure; alpha is calibrated from our panel (class c). |
| `vitorino2014understanding` | Vitorino, Management Science 60(1):227-245 (2014), doi 10.1287/mnsc.2013.1748. Routes: CR (bibliographic query), RePEc. Abstract read: advertising as investment in brand capital, closed-form returns and market value from Euler equations, brand equity about 23% of firm market value. | Special case in structure (q-theory of advertising). The shadow price of brand capital in Vitorino is the analog of P1's marginal q of revenue. P1 applies it to total growth spend and to the Rule-of-X frontier, and compares the weight with investors' screens. |
| `belo2022decomposing` | Belo, Gala, Salomao and Vitorino, JFE 143(2):619-639 (2022), doi 10.1016/j.jfineco.2021.08.007. Routes: NBER w26112, ScienceDirect page, RePEc. Abstract read: a neoclassical investment model with quasi-fixed labor and three heterogeneous capital inputs; shares of firm value 14-21% labor, 30-40% physical, 20-43% knowledge, 6-25% brand, by industry. | Context. Size of the intangible and brand component of value, which supports a revenue multiple above the earnings-based Gordon multiple for growers. P1 does not decompose value. |
| `sethi1973optimal` | Sethi, Operations Research 21(4):998-1013 (1973), doi 10.1287/opre.21.4.998. Routes: CR, INFORMS page. Abstract read: optimal advertising rate in the Vidale-Wolfe model, maximizing the present value of net profit over a finite horizon, solved with Green's theorem and switching-point analysis. Given names from the 1994 survey (the Crossref record gives only the family name). | Special case and extends. P1's growth technology is Vidale-Wolfe-like (vidale1957operations is already cited). In any such control problem the costate is the marginal value of share, which is P1's v'(s). P1 differs in the response (concave, sigma^alpha), the horizon (infinite, with a verification theorem for the HJB equation) and the homogeneity V(S,M) = M v(S/M); the new content is the score interpretation, not the control solution. |
| `sethi1977dynamic` | Sethi, SIAM Review 19(4):685-725 (1977), doi 10.1137/1019106. Routes: CR (bibliographic query), RePEc (described in the 1994 abstract as "the comprehensive survey of the literature by Sethi in 1977"). [Abstract not read.] | Context. Survey of the control-model class; cite with `feichtinger1994dynamic` for positioning. |
| `feichtinger1994dynamic` | Feichtinger, Hartl and Sethi, Management Science 40(2):195-226 (1994), doi 10.1287/mnsc.40.2.195. Routes: CR, RePEc (abstract read: review of developments after the 1977 survey; optimal advertising expenditures over time for a firm or competing firms, subject to dynamics that translate them into sales and profits). | Context. Same as above; also the source for Sethi's given names. |
| `sethuraman2011advertising` | Sethuraman, Tellis and Briesch, JMR 48(3):457-471 (2011), doi 10.1509/jmkr.48.3.457. Routes: CR, first page of an author-hosted copy. Abstract read: mean short-term advertising elasticity 0.12, long-term 0.24; working-paper version 872 estimates from 57 studies. | Context only. These are elasticities of the sales level with respect to advertising, so they do not map onto alpha, the elasticity of excess growth with respect to spend. Cite as a bracket showing diminishing returns to advertising, not as a source for alpha. |

Assessment of novelty after this literature (for the contribution list): the growth technology, the existence of a first-order condition for spend, and the interpretation of the multiplier as a marginal value of a customer are not new. New (no counterpart found in what I read): the score budget, the two weights (firm marginal q versus investor duration weight) and their non-identification from chosen points, the accountability floor with a common-mode term, and the attainable and expected frontiers. I did not find a paper that links an advertising or customer-capital control problem to a screening metric.

### b2. Marris and the valuation ratio (existing keys; no new entry)

- `marris1963model` (QJE 77(2):185-209, doi 10.2307/1884399): DOI confirmed in the Crossref record; the EconPapers record lists section headings from "Managerial utility, 186" to "Maximizing versus satisficing, 207" and no abstract. The DOI 10.2307/1884394 that circulated in the review notes is a different item (Smithies, "Full Employment at Whatever Cost: Comment", QJE 64(4), 1950).
- `marris1964economic` (book): the TAMU library catalog lists Free Press of Glencoe, New York, 1964; the existing entry says Macmillan, London. Both imprints may exist; I could not confirm the London imprint, so the entry is unchanged and flagged in section c.
- Relation: Proposition value-based objectives (c) reproduces the constant-growth valuation ratio V/(kS) = (ROIC - g)/(r - g), the steady-state valuation ratio in the Marris-Gordon tradition. Present it as a restatement (the referee's point) and cite the Marris models for it. I did not read the original definition of Marris's valuation ratio (market value of shares over net assets), only secondary descriptions (a Warwick thesis page and Palgrave chapter abstracts), so do not quote it.

### b3. Entry and market structure

| Key | Citation and route | Relation to P1 |
|---|---|---|
| `mankiw1986free` | Mankiw and Whinston, RAND Journal of Economics 17(1):48-58 (1986), doi 10.2307/2555627. Routes: CR (doi record and bibliographic query), RePEc, author page. Abstract read: with fixed entry costs there can be too many or too few entrants; an entrant that makes incumbents cut output gains more than society does; integer constraint on entry. | Special case. Proposition free entry (a)-(b) is a Cournot free-entry equilibrium with a fixed cost and an integer number of entrants, n* = floor(N_F) - 1. P1 does not make a welfare statement. Its addition is the score limit as F goes to zero, R_X -> XG + (r - G) k_u / c_hat, and the scarce-input rent in (c). |
| `dixit1977monopolistic` | Dixit and Stiglitz, AER 67(3):297-308 (1977). Route: RePEc only (no DOI found; a Crossref query did not return the 1977 article and the DOI 10.2307/1831401 does not resolve). [Abstract not on the page.] | Context. P1's entry model is homogeneous-product Cournot; the differentiated-product alternative is the monopolistic-competition framework. Cite where the paper discusses the mode of competition (rem:bertrand). |
| `farrell2007coordination` | Farrell and Klemperer, chapter 31 in Handbook of Industrial Organization (Elsevier, 2007), pp. 1967-2072, doi 10.1016/S1573-448X(06)03031-7. Route: CR. [Record only.] | Context. Switching costs and network effects are a source of customer lock-in; P1's rent rho in prop:entry(c) is attributed to a non-replicable input, and lock-in is one candidate for that input. |

### b4. Common-cause failure (for the common-mode term p^cm_j of prop:amin)

| Key | Citation and route | Relation to P1 |
|---|---|---|
| `mosleh1989nureg4780` | Mosleh, Fleming, Parry, Paula, Worledge and Rasmuson, NUREG/CR-4780 Vol. 2 (NRC, January 1989). Routes: OSTI record (purl 6564737), NRC reference listing. Abstract read: common cause failures are "that subset of dependent failures for which causes are not explicitly included in the logic model as basic events"; a four-stage framework; Volume 2 holds appendices A to H. | Context and special case. P1's p^cm_j is a common-cause term for layers that share a failure mode; the result P_mm >= product of p^cm_j (prop:amin(a)) restates the standard point of this literature that redundancy does not remove common-cause failure. |
| `mosleh1998nureg5485` | Mosleh, Rasmuson and Marshall, NUREG/CR-5485 (INEEL/EXT-97-01327, November 1998). Route: NRC operating-experience site PDF, title page and early sections only (author names read from a partly garbled scan). The beta-factor text (Section 5.3, Appendix A) was not reached. | Context. Guidelines for modeling common-cause failure in probabilistic risk assessment (multiple Greek letter and alpha-factor models are visible in the sections read). Cite for the method class, not for the beta-factor definition. |
| `hokstad2008common` | Hokstad and Rausand, in Misra (ed.), Handbook of Performability Engineering (Springer, 2008), pp. 621-640, doi 10.1007/978-1-84800-131-2_39. Route: Springer record (abstract read: the beta-factor model is still the most commonly used common-cause failure model; strengths, limits and plant-specific beta factors; newer multiple beta-factor model). | Precedent for the form. The beta-factor form of the common-mode term in prop:amin is the standard one. P1's values (0.002 human, 0.005 AI) are illustrative (class d); the new element is using the term to put a floor on accountability cost and to price diversity of providers. |
| `eckhardt1985theoretical` | Eckhardt and Lee, IEEE TSE SE-11(12):1511-1517 (1985), doi 10.1109/TSE.1985.231895. Route: CR. [Record only.] | Context. Title: coincident errors in multiversion software; the software analog of a common-mode term across independently developed versions. Supports the claim that stacking reviewers built the same way does not deliver independence. |
| `littlewood1989conceptual` | Littlewood and Miller, IEEE TSE 15(12):1596-1614 (1989), doi 10.1109/32.58771. Route: CR. [Record only.] | Context. Title: conceptual modeling of coincident failures in multiversion software; supports the diversity argument (only different types address common-mode failure). |
| `knight1986experimental` | Knight and Leveson, IEEE TSE SE-12(1):96-109 (1986), doi 10.1109/TSE.1986.6312924. Route: CR. [Record only.] | Context. Title: an experimental evaluation of the assumption of independence in multiversion programming; the experimental precedent for testing independence of redundant versions. |

Not verified and left out: Fleming (1974/1975) beta-factor report, and the Rausand-Hoyland textbook (section c).

### b5. The 14 references of `fable_referee_io_ai.md` section 5 (each re-verified independently)

| # | Key | Citation and route | Relation to P1 |
|---|---|---|---|
| 1 | `acemoglu2018race` | Acemoglu and Restrepo, AER 108(6):1488-1542 (2018), doi 10.1257/aer.20160696. Routes: CR, RePEc (abstract read: displacement versus reinstatement; with cheap capital all tasks are automated, otherwise a stable path). | Context. The task-based frame behind Table ai-map; prop:ai is the firm-level counterpart (dR/dzeta nets channels that move margin, growth and capital intensity). P1 does not model reinstatement; say so. |
| 2 | `jones2020nonrivalry` | Jones and Tonetti, AER 110(9):2819-2858 (2020), doi 10.1257/aer.20191330. Routes: AEA page, NBER w26260 (abstract read: data are nonrival; firms may hoard data). | Context. If data are nonrival, a data rent rho needs exclusion; P1 takes the scarce input Z as given in prop:entry(c). |
| 3 | `goldfarb2019digital` | Goldfarb and Tucker, JEL 57(1):3-43 (2019), doi 10.1257/jel.20171452. Routes: CR, RePEc (abstract read: five costs reduced by digitization: search, copying, transport, tracking, verification). | Context. Verification is on the list, and P1's accountability floor is the cost of verifying AI-run controls; the floor qualifies a general fall in verification costs. |
| 4 | `korinek2025concentrating` | Korinek and Vipra, Economic Policy 40(121):225-256 (2025), doi 10.1093/epolic/eiae057 (NBER w33139). Routes: CR, RePEc (abstract read: economies of scale and scope, concentration, tipping, vertical integration in foundation models). | Context. Supports the assumption behind the common-mode term and the fixed-cost paragraph: few model providers. P1 takes concentration as given and prices its consequence. |
| 5 | `kwa2025measuring` | Kwa et al., arXiv:2503.14499 v4 (10 July 2026), NeurIPS 2025. Routes: arXiv abstract and v4 PDF, GitHub README. See A7. | Context. Source of the time-horizon doubling and of the run-cost bound. |
| 6 | `mcelheran2024ai` | McElheran et al., J. Econ. Manag. Strategy 33(2):375-415 (2024), doi 10.1111/jems.12576. Routes: CR, NBER w31788 (abstract read: 2018 Annual Business Survey, about 850,000 firms; fewer than 6% adopted, just over 18% employment-weighted). | Context. Adoption evidence for the pace parameters, but it covers 2018 AI technologies (guided vehicles, machine learning, machine vision, language processing, voice), not generative AI. |
| 7 | `ide2025artificial` | Ide and Talamas, JPE 133(12):3762-3800 (2025), doi 10.1086/737233. Routes: CR, arXiv:2312.05481 (abstract read: hierarchies; autonomous AI benefits the most knowledgeable, non-autonomous AI the least knowledgeable; output higher with autonomous AI). | Context. Bears on who signs: P1 takes the accountability organization as a fixed cost C^acct. Not a result of P1. |
| 8 | `humlum2025still` | Humlum and Vestergaard, NBER w33777 (May 2025, revised March 2026), doi 10.3386/w33777. Route: NBER (abstract read: precise null effects on earnings and hours, ruling out effects larger than 2% two years after ChatGPT; employers absorb AI through task reorganization). The abstract does not quantify time savings. | Context. Consistent with slow realization of benefits (the realized share b-bar); it measures worker earnings and hours, not firm margins. |
| 9 | `brynjolfsson2025canaries` | Brynjolfsson, Chandar and Chen, SIEPR working paper (August 2025). Route: SIEPR page (abstract read: 13% relative employment decline for workers aged 22 to 25 in the most exposed occupations). A November 2025 version listed by the Digital Economy Lab was not read. | Context. Seat-compression channel in lever 4 and in G; early-career evidence only. |
| 10 | `noy2023experimental` | Noy and Zhang, Science 381(6654):187-192 (2023), doi 10.1126/science.adh2586. Routes: CR, Stanford SCALE page (abstract read: 453 professionals; time down about 40%, quality up about 18%). | Context. Core experimental evidence for the human-cost reduction c_h; writing tasks, not firm-level margins. |
| 11 | `dellacqua2026navigating` | Dell'Acqua et al., Organization Science 37(2):403-423 (2026), doi 10.1287/orsc.2025.21838. Routes: CR, HBS page (HBS WP 24-013; abstract read: 758 knowledge workers; inside the frontier 12.2% more tasks, 25.1% faster; a task outside the frontier is where AI hurts performance). | Context. Field evidence behind the error and automation-bias parameters of lem:fullcost(c). |
| 12 | `korinek2024scenarios` | Korinek and Suh, NBER w32255 (March 2024), doi 10.3386/w32255. Route: NBER (abstract read: scenarios for technological progress toward AGI; wages depend on a race between automation and capital accumulation). | Context. Methodological precedent for presenting horizon ranges as scenarios, which P1's horizon section does. |
| 13 | `weyl2013pass` | Weyl and Fabinger, JPE 121(3):528-583 (2013), doi 10.1086/670401. Routes: CR, RePEc (abstract read: five principles of tax incidence under imperfect competition). The referee's "conduct parameter" wording is not on the page. | Context and extends. Lemma prices (pass-through elasticity phi) is a pass-through result of this family; P1 uses phi as a scenario parameter. |
| 14 | `ge2017benefits` | Ge, Koester and McVay, JAE 63(2-3):358-384 (2017), doi 10.1016/j.jacceco.2017.01.001. Routes: CR (bibliographic query), RePEc (abstract read: $388M audit fees saved, $719M lower operating performance, $935M delay in market value decline, all aggregates for exempt firms 2007-2014). | Context. Not a per-firm attestation cost (referee error). Use for the existence of a cost and benefit of attestation, not for the floor's level. |

Extras beyond the 14 that the referees suggested or the corrections needed:

| Key | Citation and route | Relation to P1 |
|---|---|---|
| `autor2020fall` | Autor, Dorn, Katz, Patterson and Van Reenen, QJE 135(2):645-709 (2020), doi 10.1093/qje/qjaa004. Route: CR. [Record only.] | Context. Title: the fall of the labor share and the rise of superstar firms; bears on whether high-score firms keep high margins (prop:entry, prop:industry). |
| `autor2024new` | Autor, Chin, Salomons and Seegmiller, QJE 139(3):1399-1465 (2024), doi 10.1093/qje/qjae008. Route: CR. [Record only.] | Context. New work (new tasks) for the G scenario, suggested by the referee. |
| `agrawal2019exploring` | Agrawal, Gans and Goldfarb, Information Economics and Policy 47:1-6 (2019), doi 10.1016/j.infoecopol.2019.05.001. Route: CR. [Record only.] A different paper from `agrawal2019artificial` (JEP 33(2):31-50) in part2; the review's "AGG 2019" key is ambiguous. | Context. Prediction versus judgment. |
| `agrawal2024artificial` | Agrawal, Gans and Goldfarb, J. Econ. Manag. Strategy 33(2):327-337 (2024), doi 10.1111/jems.12521. Route: CR. [Record only.] | Context. System-wide change; identical to part2. |
| `gans2026market` | Gans, Annual Review of Economics 18(1):417-445 (2026), doi 10.1146/annurev-economics-051624-061832 (NBER w32270). Routes: CR, NBER (abstract read: competition in markets for training data, input data and AI predictions). Supersedes part2's `gans2024market`. | Context. Data markets as the source of persistent market power. |
| `gans2026oring` | Gans and Goldfarb, NBER w34639 (January 2026), doi 10.3386/w34639. Routes: NBER, RePEc (abstract read: automation when tasks are quality complements; decisions are discrete and may need bundled adoption; exposure indices overstate displacement). | Context. Supports the bundled-adoption logic of the attainable frontier (processes migrate in waves). |
| `hagiu2023data` | Hagiu and Wright, RAND J. Econ. 54(4):638-667 (2023), doi 10.1111/1756-2171.12453. Route: CR (bibliographic query). [Record only.] | Context. When a data advantage lasts, i.e. when rho is durable. |
| `vaccaro2024when` | Vaccaro, Almaatouq and Malone, Nature Human Behaviour 8(12):2293-2303 (2024), doi 10.1038/s41562-024-02024-1. Route: CR. [Record only.] The "Hedges' g = -0.23" figure quoted by a referee was not verified. | Context. Human-AI combinations. |
| `flyvbjerg2022empirical` | Flyvbjerg et al., J. Manag. Inf. Syst. 39(3):607-639 (2022), doi 10.1080/07421222.2022.2096544. Route: CR. [Record only.] | Context. IT project outcomes, for the transition-risk parameters. |
| `becker2025measuring` | Becker, Rush, Barnes and Rein, arXiv:2507.09089 (July 2025). Route: arXiv (abstract read: randomized trial, 16 developers, 246 tasks; allowing early-2025 AI tools increased completion time; note carries 19%). | Context. Counter-evidence to uniform speed-ups; sets a limit on reading the realized share b-bar from experiments. |
| `stevens2026payrolls` | Stevens, arXiv:2602.00139 (January 2026). Route: arXiv (abstract read; see A8). | Source for the 0.03 of the table. |

### b6. Sources behind parameters (Task 3; full detail in `tab_param_sources.tex`)

The table has 44 rows and cites 48 distinct keys: 41 are in the additions file and 7 are existing keys (`epoch2025inference`, `michael2026servers`, `svanberg2024beyond`, `moody2026transition`, `omb2024report`, `gordon2002economics`, `bessemer2024rulex`). The rows for the seven existing keys restate `notes/assumptions_round2.md`; I did not re-read those sources. Classes of the 44 rows as used: a 12, b 23, c 2, d 7. Class describes the value as used, not the source's status; the source's status is column 4 of the table.

Status flags for sources (sample and who ran them are in the .bib `note` and in the table):

| Flag | Keys |
|---|---|
| Secondary (read through a report of the source) | `ciodive2025spglobal` (S&P Global Market Intelligence, read via CIO Dive); `fraxion2025apbenchmarks` (APQC figures, tertiary through CFO.com links that could not be located); `meta2025q4release` (read through a filing mirror, capedge.com) |
| Vendor (data published by a vendor about its own product or customers) | `medius2025apaccuracy`, `vectara2026leaderboard`, `stripe2026pricing`, `aleph2026benchmarks` (published by one of the two authors), `iconiq2026state` (proprietary survey of AI-building firms) |
| Sponsor-funded | `choi2025dma` (Analysis Group study funded by Apple; the author states conclusions are her own) |
| Consultancy or advisory survey, self-reported | `bcg2020flipping` (825 executives, period not stated), `mckinsey2021losing` (1,034 participants, 18 May to 29 June 2021), `kpmg2025sox` (146 SOX 404 program owners, April to June 2025), `ians2025budget` (587 CISOs, April to August 2025), `wef2025futurejobs` (over 1,000 employers) |
| Practitioner data | `kornferry2020tenure` (C-suite of the 1,000 largest U.S. companies by revenue, late 2019) |
| Peer reviewed or institutional | `magesh2025hallucination`, `panko1999applying`, `kim2025correlated` (ICML 2025), `ganapati2020energy`, `gao2022effective`, statutes, regulators, SEC filings and releases |
| Preprint or working paper | `gundlach2025price`, `stevens2026payrolls`, `asgari2025framework` (figures read in the medRxiv version), `benedek2015vat` (IMF working paper), `demirer2025emerging` |

Read-through checks on specific rows:
- S&P / CIO Dive: "average organization scrapped 46 percent of AI proofs of concept before production", "42 percent of companies abandoned most AI initiatives, up from 17 percent"; sample over 1,000 in North America and Europe; fielding period not stated; S&P report not read. Used only for the low end of the attempt-success probability (0.54); it measures proof-of-concept attrition, not failure of a funded migration.
- Salesforce: the 8-K of 4 January 2023 (about 10% workforce reduction; charges of about 1.4 to 2.1 billion dollars); the 10-K for fiscal 2024 says the reduction was substantially complete by the end of fiscal 2024. Restructuring charges and margins were not reached in the part of the 10-K that could be read. Meta: headcount 67,317 at 31 December 2023, down 22%; the Q4 2024 release (via mirror) footnote on a 5.5-year useful life lowering 2025 depreciation by about 2.9 billion dollars. The Alphabet 6% in the round-2 notes was not verified.
- Magesh et al.: tools run 22 March to 22 April 2024 (Lexis+ AI, Ask Practical Law AI) and 23 to 27 May 2024 (Westlaw); 17 to 33% hallucination.
- KPMG: the division in the table (16,000 to 57,500 dollars per in-scope system a year) is ours.
- BLS JOLTS: August 2026 layoffs and discharges 1.0%, separations 3.2%. Key renamed to `bls2026joltsnews` because `bls2026jolts` in part2/refs_labor.bib is a different BLS page (TED article on quits rates).
- Regulators: SR 26-2 and OCC Bulletin 2026-13 (17 April 2026) supersede SR 11-7 and exclude generative and agentic AI; Regulation (EU) 2026/1744 recital 40 gives 2 December 2027 (Annex III) and 2 August 2028 (Annex I); the operative Article 113 was not reached.

Parameters with no external source (not in the table): the alpha value and the excess-growth weight X (calibrated from our panel, class c), the pace of cost programs in 2022 to 2024 (our calculation), the accountability-floor band 0.5% to 4.6% (panel shares of G&A, class c), loss severities, tail indices, exposure multipliers, process counts and compliance costs of Table fullcost (class d), the reorganization clock and the monitor recall rates.

---

## c. Unverified items (left out of the .bib; not used as evidence)

References I could not verify:
1. Fleming, K. N. (1974), GA-A13284, the beta-factor report. OSTI pages not readable and doi 10.2172/4206606 not readable; Hokstad-Rausand's reference list (Springer page) has "Fleming KN. A reliability model for common mode failures in redundant safety systems" dated 1975, so the year is also uncertain.
2. Rausand and Hoyland, System Reliability Theory (book): only retailer pages found.
3. Sutton (1991), Sunk Costs and Market Structure.
4. Baumol, Panzar and Willig (1982), Contestable Markets.
5. Albers, Mantrala and Sridhar (2010) (advertising and sales response).
6. Zhong et al., ImpossibleBench, arXiv:2510.20270 (behind the monitor recall values 0.95, 0.60, 0.42).

Sources behind parameters whose primary I could not read (only a secondary report, or a gated page):
7. Gartner 48% / 8 months from prototype to production (secondary).
8. Ardent Partners exception rates (as quoted by Corcentric).
9. APQC percentile values for first-time-error-free disbursements (the page shows N = 2,305 and hides the percentiles; the 98% and 0.8% are tertiary via Fraxion and CFO.com).
10. IOFM 2021 effectiveness benchmarks (values for members only).
11. S&P Global Market Intelligence report (read via CIO Dive).
12. SaaStr's "23% of total AI product costs" (secondary, chart is an image; SaaStr's headline "23% of revenue" is the author's reframing).
13. Meritech multiple of 3.8.

Figures and details not confirmed:
14. METR per-run cost shares 0.44%, 1.1%, 1.0% (the README lists no cost field).
15. SAP upkeep rates of 17% and 22%.
16. Alphabet 6% workforce reduction (January 2023).
17. JOLTS information-industry rate of 2.5%.
18. Section 404 median cost of $1.04 million and audit fees of $343 per $1 million of revenue (register figures).
19. The 2% lower bound for card fees.
20. Gordon-Loeb 1/e bound: seen only in a secondary description, not in the article.
21. 26 U.S.C. 59(k) threshold for the applicable corporation.
22. SEC C&DI 102.07 and the content of the 13 December 2022 update (the announcement says what was updated, not what changed).
23. Article 113 operative text of Regulation (EU) 2026/1744.
24. Fielding periods of the S&P and BCG surveys.
25. Medius sample and method (none given).
26. Svanberg: setup cost $165,000 to $1,765,000 and upkeep $122,840 to $242,840 a year are from the PDF as read by the round-2 agent; the web page lacks them. Not re-read.
27. Acemoglu (2025) journal version (only NBER w32487 seen in the earlier notes).
28. Hampole et al.: journal status.
29. Asgari et al.: figures read in the medRxiv preprint, not in the npj Digital Medicine version.
30. Demirer et al. JEP article: full text.
31. The Marris valuation-ratio definition (primary text), and the London (Macmillan) imprint of Marris (1964).
32. NUREG/CR-5485 beta-factor text; its author initials come from a garbled scan; NUREG/CR-4780 report-number prefix (OSTI prints "ERRI NP-5613").
33. Sethi (1973, 1977): given names (Crossref gives the family name only); taken from the 1994 survey.
34. Bonney et al. (2026) "CES Working Paper 26-25": not confirmed; dropped.
35. Vaccaro et al. "Hedges' g = -0.23": not verified.
36. Referee 4's form of the Kwa "80% vs 50%" claim (the paper's own statement, 4 to 6 times shorter, is verified).
37. Weyl-Fabinger "conduct parameter" wording: not on the abstract page.
38. The Digital Economy Lab "November 2025" version of Canaries.
39. Dixit-Stiglitz DOI: none found.
40. The Terry 5-basis-point and 1% welfare figures: read in a paraphrase of the abstract, not quoted.

Count: 6 references not verifiable; 7 secondary or gated sources behind parameters; 27 specific figures or details not confirmed (items 14 to 40).

---

## d. Duplicate and conflicting keys for the bibliography merge

Analysis run with `scratchpad/bibcheck.py` over `refs.bib`, `paper1/refs_paper1.bib`, `paper1/refs_additions_v2.bib` and the nine part2 bib files: 12 files, 746 entries, 595 unique keys.

1. Corrected keys (replace the old entry; BibTeX keeps the first of a repeated key, so list `refs_additions_v2` first in `\bibliography{...}` or, better, delete the old entries). Locations of the old entries:

| Key | Old entries in |
|---|---|
| demirer2025emerging, demirer2026emerging | paper1/refs_paper1.bib, part2/refs_modern.bib |
| bonney2024tracking, bonney2026microstructure, terry2023macro, hampole2025artificial | paper1/refs_paper1.bib, part2/refs_modern.bib |
| iconiq2026state, gundlach2025price | paper1/refs_paper1.bib, refs.bib |

   Old versus new: terry2023macro "Terry, Stephen" becomes "Terry, Stephen J."; bonney2026microstructure gains a doi and loses the unconfirmed CES working-paper note; hampole2025artificial gains a doi; iconiq and gundlach gain notes (iconiq url without "www"); demirer and bonney2024 gain notes.

2. Same key, different content across files (7 conflicts reported by the script; all differences are additions, none contradicts):

| Key | Files | Difference |
|---|---|---|
| asgari2025framework | additions, part2/refs_reliability.bib | additions adds volume 8, number 1, article 274 |
| bonney2026microstructure | additions, refs_paper1, part2/refs_modern | additions adds doi (see 1) |
| dellacqua2026navigating | additions, part2/refs_part2.bib | additions adds volume 37, number 2, pages 403-423; Crossref spells the fourth author "Lifshitz, Hila" (the working paper has "Lifshitz-Assaf") |
| gans2026oring | additions, part2/refs_modern.bib | additions adds doi 10.3386/w34639 |
| hampole2025artificial | additions, refs_paper1, part2/refs_modern | additions adds doi |
| humlum2025still | additions, part2/refs_part2.bib | additions adds doi and the retitling/revision note |
| korinek2024scenarios | additions, part2/refs_part2.bib | additions adds doi 10.3386/w32255 |

3. Same key, identical core fields in more than one file: 136 keys in all, of which 113 are ordinary copies among refs.bib, refs_paper1.bib and the part2 files and 23 involve the additions file. Of the 89 additions, 30 keys exist in another file (28 in part2, plus `iconiq2026state` and `gundlach2025price` in the P1 files only): 23 have identical core fields and 7 are the additive conflicts of item 2. The 22 part2 keys that are not corrected keys are the 19 entries of section F of the additions file and `asgari2025framework`, `magesh2025hallucination` and `panko1999applying`. Drop section F on merge if part2 is merged first; it is there to make the file self-contained.

4. Same content, different keys:
- `eu2026reg1744` (additions) and `eu2026regulation` (part2/refs_modern.bib): the same regulation; part2 verified it through the European Parliament resolution and the Council document, I read it at EUR-Lex (recital 40, recital 46). Keep one; I suggest part2's key if the OJ citation is added to it, or both if the url differs matters.
- `vectara2026leaderboard` (additions) and `vectara2026hallucination` (part2/refs_reliability.bib): the same GitHub repository.
- `gans2026market` (additions, journal version) and `gans2024market` (part2/refs_part2.bib, NBER only, no doi): the journal version supersedes the NBER-only entry; retarget part2's citations or keep both.
- `bls2026joltsnews` (additions) versus `bls2026jolts` (part2/refs_labor.bib): different BLS pages; the rename avoids a collision.

5. Different papers that look alike: `agrawal2019exploring` (IEP 47, additions) is not `agrawal2019artificial` (JEP 33(2), part2). The referee's "AGG 2019" refers to neither unambiguously.

6. Other differences from part2 entries with the same key: `panko1999applying` (additions adds a url and the experiment description because no DOI was confirmed); `magesh2025hallucination`, `kwa2025measuring`, `mcelheran2024ai`, `ide2025artificial`, `korinek2025concentrating`, `agrawal2024artificial` (additions add notes only). `kwa2025measuring` in part2 is the 26-author, version 4 entry; the additions version carries the run-cost bound in the note.

7. Part2 entries lacking fields the additions file has: `dellacqua2026navigating` (volume, number, pages), `humlum2025still`, `korinek2024scenarios`, `gans2026oring` (doi), `asgari2025framework` (volume, number, article number), `gans2024market` (no doi).

8. Which bib each paper builds from: `paper.tex` uses `refs.bib` and `paper1/paper1.tex` uses `paper1/refs_paper1.bib`; the two have diverged (refs.bib lacks, for example, `demirer2025emerging`, `bonney2024tracking`, `terry2023macro`, `hampole2025artificial`). Decide which one is canonical before merging.

9. `marris1964economic` imprint (Macmillan, London in refs.bib and refs_paper1.bib) is unconfirmed; see section c, item 31.

10. Under `\nocite{*}` the bibliography compiled with plainnat; characters in `note` fields were escaped (`\&`, `\%`); no underscores in notes.

---

## e. Referee and round-2 errors found (for the response letter)

1. Demirer et al.: a within-model, cross-provider substitution elasticity was used as the demand elasticity for inference (A1). The abstract's own reading is "limited scope for Jevons-Paradox effects".
2. ICONIQ: 2026 and 2027 margins are projections (part2/theory_product.tex:177 treated 2026 as realized); the sample is AI-building software firms; "talent is the largest cost category" is about customer-facing AI products, not internal spend.
3. Terry (2023): "cut research spending" is not in the abstract; lower R&D growth is.
4. Foster-Haltiwanger-Syverson is in Economica, not the AER (referee).
5. Humlum-Vestergaard was retitled (referee used the old title).
6. Ge-Koester-McVay figures are aggregates, not a per-firm attestation cost (referee).
7. "AGG 2019" collides with a different part2 key (referee).
8. Weyl-Fabinger "conduct parameter" and the Digital Economy Lab "November 2025" Canaries version could not be confirmed (referee).
9. Marris DOI: 10.2307/1884394 is a Smithies comment; the correct DOI is 10.2307/1884399 (existing entry is right).
10. Bonney et al.: two BTOS series were spliced across a question change (A4); the performance result is an association.
11. Benedek-de Mooij-Wingender: three authors on the working-paper page; round 2 lists four.
12. Kwa et al.: the paper gives a cost bound, not the 0.44/1.1/1.0% shares; the README lists no cost field (A7).
13. Gundlach et al.: "price of the frontier model has risen" in part2 should be the cost of the record-performance run, driven by tokens.

---

## f. Counts for the hand-off

- Verified and written to the .bib: 89 (every entry read at a registry, publisher, series, preprint or issuer page on 29 October 2026).
  - Bibliographic record only (Crossref; abstract not read; marked [record only]): 12 (`agrawal2019exploring`, `agrawal2024artificial`, `autor2020fall`, `autor2024new`, `eckhardt1985theoretical`, `farrell2007coordination`, `flyvbjerg2022empirical`, `hagiu2023data`, `knight1986experimental`, `littlewood1989conceptual`, `sethi1977dynamic`, `vaccaro2024when`).
  - Read through a secondary or mirror page: 3 (`ciodive2025spglobal`, `fraxion2025apbenchmarks`, `meta2025q4release`).
  - Aggregator only (no publisher or registry record): 1 (`dixit1977monopolistic`).
  - The remaining 73 were read at a registry plus a publisher, series, preprint or issuer page, or at the issuer's own page.
- Corrected: 8 .bib entries (7 sources: Demirer has two entries) and 21 source-claim corrections at 16 distinct .tex lines (section a).
- Added: 81 entries beyond the 8 corrected (59 new to every bib, 22 already in part2).
- Not verifiable: 6 references left out, 7 gated or secondary sources behind parameters, 27 specific figures or details (section c).
- Table: `tab_param_sources.tex`, 44 rows, 48 keys, classes a 12, b 23, c 2, d 7.
