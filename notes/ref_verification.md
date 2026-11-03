# Reference verification log

Checked on 2026-10-28. Direct API access (Crossref, doi.org, arXiv API, OpenAlex) was blocked by the session proxy, so each item was verified by web search and by fetching a landing page: RePEc/EconPapers/IDEAS, publisher pages (Cambridge, Springer, INFORMS), arXiv abstract pages, university repositories, scilit, or the originating firm's own page. DOIs marked "via RePEc handle" come from the hdl.handle.net/10.xxxx link on the RePEc record, which mirrors the DOI.

Status key: **verified** = all bibliographic fields confirmed. **corrected** = the item exists but details differ from the task brief or from common citation; the BibTeX holds the corrected version. **dropped** = not included.

Final (29 Oct 2026): thorp2023chatgpt and mohapatra2026expectations removed from refs.bib as uncited; 71 entries, all cited (62 verified, 9 corrected); sec2026xbrlapi now points to the companyfacts endpoint.

Totals (referee round, 29 Oct 2026): 73 entries in refs.bib (64 verified, 9 corrected). Added this round: solow1971some, odagiri1981theory, vidale1957operations, nerlove1962optimal, dorfman1954optimal, dechow2004implied, arxiv2026policy; logged arxiv2023policy and sec2026xbrlapi (added by the lead agent). Removed: markowitz1952portfolio (no longer cited). 5 items dropped earlier: 4 verified but not used, 1 unverifiable (Cronin 2022). Two entries (thorp2023chatgpt, mohapatra2026expectations) remain in refs.bib but are no longer cited after the AI-research subsection was shortened; plainnat omits uncited entries, so they do not print.

## (a) Rule of 40: practitioner and academic

| key | full citation | URL/DOI checked | status | relevance |
|---|---|---|---|---|
| feld2015rule | Feld, B. (2015). "The Rule of 40% For a Healthy SaaS Company." Feld Thoughts, 3 Feb 2015. | feld.com/archives/2015/02/rule-40-healthy-saas-company/ | verified | Popularizing source: "growth rate + profit should add up to 40%"; Feld credits an unnamed late-stage investor. Wikipedia dates it 2 Feb; the page itself shows 3 Feb. |
| bessemer2024rulex | Deeter, B. & Bondy, S. (2024). "The Rule of X." Bessemer Venture Partners Atlas, 2 Jan 2024. | bvp.com/atlas/the-rule-of-x | verified | Two authors (Deeter and Bondy). Formula: growth x multiplier + FCF margin; multiplier about 2x private, about 2-3x public. A TechCrunch version by Deeter appeared 17 Dec 2023. |
| roche2021saas | Roche, P. & Tandon, S. (2021). "SaaS and the Rule of 40: Keys to the critical value creation metric." McKinsey, 3 Aug 2021. | mckinsey.com/.../saas-and-the-rule-of-40-keys-to-the-critical-value-creation-metric | verified | 200+ firms over 2011-2021; firms beat the rule about 16% of the time; valuation premium. Wikipedia lists a different author and date; the McKinsey page itself gives Roche and Tandon. |
| depeyrot2018hacking | Depeyrot, T. & Heap, S. (2018). "Hacking Software's Rule of 40." Bain Brief, 20 Dec 2018. | bain.com/insights/hacking-softwares-rule-of-40/ | verified | 16% of 86 firms beat the rule every year 2013-2017; about 2x EV/revenue premium. |
| bosche2022sixty | Bosche, A., Heap, S., Narayen, R. & Schorling, C. (2022). "Is 60 the New (Rule of) 40? Setting a New Standard of Software Excellence." Bain Technology Report 2022, 19 Sep 2022. | bain.com/insights/new-rule-of-40-setting-software-excellence-standard-tech-report-2022/ | verified | Added. Raises the target to 60 or more for "superperformers"; earlier "Rule of 60" than Vista. |
| lipman2026ai | Lipman, D., Callahan, G., Goetz, D. & Sunderland, G. (2026). "AI Brings Headwinds and Tailwinds to the Rule of 40." Bain, 8 Apr 2026. | bain.com/insights/ai-brings-headwinds-and-tailwinds-to-the-rule-of-40/ | verified | "Bain on the Rule of 40 and AI": inference costs squeeze margins; suggests a temporary "Rule of 30." |
| vista2026rethinking | Vista Equity Partners (2026). "Rethinking Software Benchmarks in an AI-Driven Market." 8 Jan 2026. | vistaequitypartners.com/insights/rethinking-software-benchmarks-in-an-ai-driven-market/ | verified | Rule of 60 for AI-enabled software, described as "an emerging aspiration, not a universal baseline." Page metadata names Ellie Cottrill, but no byline is shown, so the entry uses a corporate author. |
| lee2024evaluating | Lee, K. F. (2024). "Evaluating Stock Selection in the SaaS Industry: The Effectiveness of the Rule of 40." Applied Finance Letters 13, 168-185. | ojs.aut.ac.nz/applied-finance-letters/article/view/761; MPRA 121568 | verified | **The only peer-reviewed academic study of the Rule of 40 found.** Tests it as a stock screen on 1,756 SaaS firms (2003-2022); proposes a "Rule of 65." Empirical only, with no model of the feasible set. No DOI found. |

## (b) Growth-profitability trade-off theory

| key | full citation | URL/DOI checked | status | relevance |
|---|---|---|---|---|
| penrose1959theory | Penrose, E. T. (1959). The Theory of the Growth of the Firm. Oxford: Basil Blackwell. 4th ed. OUP 2009. | CiNii BA03680608; RePEc oxp:obooks:9780199573844 | verified | Managerial limit on the rate of growth. |
| marris1963model | Marris, R. (1963). "A Model of the 'Managerial' Enterprise." QJE 77(2), 185-209. | doi:10.2307/1884399 (via RePEc handle) | verified | Growth-valuation frontier: the direct precursor of our frontier. |
| marris1964economic | Marris, R. (1964). The Economic Theory of 'Managerial' Capitalism. London: Macmillan. | CiNii BA49424752 | verified | The book version of the growth-valuation frontier. The catalogue record is the 1966 reprint ("c1964"). |
| uzawa1969time | Uzawa, H. (1969). "Time Preference and the Penrose Effect in a Two-Class Model of Economic Growth." JPE 77(4, Pt 2), 628-652. | doi:10.1086/259554 (scilit) | verified | Formal Penrose effect: concave relation between investment and growth. |
| lucas1967adjustment | Lucas, R. E., Jr. (1967). "Adjustment Costs and the Theory of Supply." JPE 75(4), 321-334. | doi:10.1086/259289 (EconPapers; jioinstitute record shows pp. 321-334) | verified | Convex adjustment costs. |
| hayashi1982tobin | Hayashi, F. (1982). "Tobin's Marginal q and Average q: A Neoclassical Interpretation." Econometrica 50(1), 213-224. | doi:10.2307/1912538 (scilit); IDEAS | verified | Conditions under which marginal q equals average q. |
| higgins1977how | Higgins, R. C. (1977). "How Much Growth Can a Firm Afford?" Financial Management 6(3), 7-16. | JSTOR 3665251 (from CAS library record ID); vol/pages from two independent citations | verified | Sustainable growth rate links margin and feasible growth. JSTOR page itself not fetchable; given as a URL, not a DOI. |
| mueller1969theory | Mueller, D. C. (1969). "A Theory of Conglomerate Mergers." QJE 83(4), 643-659. | doi:10.2307/1885454 (via RePEc handle) | verified | Brief said "Mueller" without detail. Managerial growth motive. |
| mueller1972life | Mueller, D. C. (1972). "A Life Cycle Theory of the Firm." Journal of Industrial Economics 20(3), 199-219. | EconPapers RePEc:bla:jindec:v:20:y:1972:i:3:p:199-219 | verified | Growth opportunities decline with maturity, which supports our saturation result. No DOI found. |
| solow1971some | Solow, R. M. (1971). "Some Implications of Alternative Criteria for the Firm." In R. Marris & A. Wood (eds.), The Corporate Economy: Growth, Competition, and Innovative Potential, London: Macmillan (also Harvard University Press), pp. 318-342. | doi:10.1007/978-1-349-01110-0_10 (IDEAS chapter record and book TOC); CiNii BA01021484 (Macmillan, London, 1971, xxvi+453 pp.); Business History Review notice confirms Harvard UP edition | verified | Referee round. Compares firm objectives (value vs growth) in a Marris-type growth-valuation setting; the referee's tangency antecedent. Chapter content verified only from the abstract. |
| odagiri1981theory | Odagiri, H. (1981). The Theory of Growth in a Corporate Economy: Management, Preference, Research and Development, and Economic Growth. Cambridge University Press. | doi:10.1017/CBO9780511895609 (Cambridge Core book page) | verified | Referee round. Managerial growth model of the firm embedded in an economy-wide growth model. Content characterization rests on the referee's description and the book's framing; full text not accessed. |

## (c) Empirical growth-profit links

| key | full citation | URL/DOI checked | status | relevance |
|---|---|---|---|---|
| coad2007testing | Coad, A. (2007). "Testing the Principle of 'Growth of the Fitter': The Relationship between Profits and Firm Growth." SCED 18(3), 370-386. | doi:10.1016/j.strueco.2007.05.001 (Waseda Pure) | verified | Small positive effect of profit on subsequent growth (French manufacturing). Not to be confused with Coad's panel-VAR papers (ICC 2010). |
| davidsson2009growing | Davidsson, P., Steffens, P. & Fitzsimmons, J. (2009). "Growing Profitable or Growing from Profits: Putting the Horse in Front of the Cart?" JBV 24(4), 388-406. | doi:10.1016/j.jbusvent.2008.04.003 (FORRT) | corrected | Brief gave the title as "Growth first, profit later?"; the actual title is above. Profitable low-growth firms do better later. |
| goddard2009sources | Goddard, J., Tavakoli, M. & Wilson, J. O. S. (2009). "Sources of Variation in Firm Profitability and Growth." JBR 62(4), 495-508. | doi:10.1016/j.jbusres.2007.10.007 (St Andrews portal) | verified | Brief said "Goddard et al." Firm effects dominate the variance of profit and growth. |
| federico2015heterogeneous | Federico, J. & Capelleras, J.-L. (2015). "The Heterogeneous Dynamics between Growth and Profits: The Case of Young Firms." SBE 44(2), 231-253. | doi:10.1007/s11187-014-9598-9 (EconPapers) | verified | Growth raises profits in young firms; profits do not drive growth. |
| lee2014relationship | Lee, S. (2014). "The Relationship between Growth and Profit: Evidence from Firm-Level Panel Data." SCED 28, 1-11. | doi:10.1016/j.strueco.2013.08.002 (IDEAS) | verified | Added. Korean data: profit reduces later growth; growth raises profit only in old firms. |

## (d) Valuation of growth

| key | full citation | URL/DOI checked | status | relevance |
|---|---|---|---|---|
| gordon1959dividends | Gordon, M. J. (1959). "Dividends, Earnings, and Stock Prices." REStat 41(2), 99-105. | doi:10.2307/1927792 (scilit; Wikipedia-derived citation) | verified | Constant-growth valuation. |
| gordon1962investment | Gordon, M. J. (1962). The Investment, Financing, and Valuation of the Corporation. Homewood, IL: Irwin. | TUM library BV011896819 | verified | Book version of the Gordon model. |
| miller1961dividend | Miller, M. H. & Modigliani, F. (1961). "Dividend Policy, Growth, and the Valuation of Shares." Journal of Business 34(4), 411-433. | doi:10.1086/294442 (scilit); pp. from Arden library | verified | Growth creates value only if return exceeds cost of capital. |
| schwartz2000rational | Schwartz, E. S. & Moon, M. (2000). "Rational Pricing of Internet Companies." FAJ 56(3), 62-75. | doi:10.2469/faj.v56.n3.2361 (EconPapers) | verified | Real-options valuation of high-growth, loss-making firms. |
| macaulay1938some | Macaulay, F. R. (1938). Some Theoretical Problems Suggested by the Movements of Interest Rates, Bond Yields and Stock Prices in the United States since 1856. NBER. | EconPapers RePEc:nbr:nberbk:maca38-1 | verified | Origin of duration, used for the Rule-of-X weight. |
| mccarthy2017valuing | McCarthy, D. M., Fader, P. S. & Hardie, B. G. S. (2017). "Valuing Subscription-Based Businesses Using Publicly Disclosed Customer Data." Journal of Marketing 81(1), 17-35. | doi:10.1509/jm.15.0519 (author PDF via CORE) | verified | Added. Customer-based valuation of subscription firms. |
| dechow2004implied | Dechow, P. M., Sloan, R. G. & Soliman, M. T. (2004). "Implied Equity Duration: A New Measure of Equity Risk." Review of Accounting Studies 9(2-3), 197-228. | doi:10.1023/B:RAST.0000028186.44328.3f (Deep Blue; IDEAS lists issue 2) | verified | Referee round. Equity duration from financial statements; book-to-market is a crude proxy. Connects to our growth weight as a duration. |

## (e) Portfolio frontier

| key | full citation | URL/DOI checked | status | relevance |
|---|---|---|---|---|
| markowitz1952portfolio | Markowitz, H. (1952). "Portfolio Selection." Journal of Finance 7(1), 77-91. | doi:10.1111/j.1540-6261.1952.tb01525.x (via RePEc handle) | verified; removed from refs.bib | Referee round: the tangency is now framed as a transformation curve with a price line, and the Markowitz mention was dropped. |

## (f) Frontier estimation

| key | full citation | URL/DOI checked | status | relevance |
|---|---|---|---|---|
| aigner1977formulation | Aigner, D., Lovell, C. A. K. & Schmidt, P. (1977). "Formulation and Estimation of Stochastic Frontier Production Function Models." J. Econometrics 6(1), 21-37. | doi:10.1016/0304-4076(77)90052-5 (scilit) | verified | Founding SFA paper. |
| meeusen1977efficiency | Meeusen, W. & van den Broeck, J. (1977). "Efficiency Estimation from Cobb-Douglas Production Functions with Composed Error." IER 18(2), 435-444. | doi:10.2307/2525757 (scilit); end page from RePEc handle "p435-44" | verified | Co-founding SFA paper. |
| koenker1978regression | Koenker, R. & Bassett, G., Jr. (1978). "Regression Quantiles." Econometrica 46(1), 33-50. | doi:10.2307/1913643 (ScienceOpen); Econometric Society page | verified | Quantile regression for the upper frontier. |
| charnes1978measuring | Charnes, A., Cooper, W. W. & Rhodes, E. (1978). "Measuring the Efficiency of Decision Making Units." EJOR 2(6), 429-444. | doi:10.1016/0377-2217(78)90138-8 (scilit) | verified | DEA. |
| cazals2002nonparametric | Cazals, C., Florens, J.-P. & Simar, L. (2002). "Nonparametric Frontier Estimation: A Robust Approach." J. Econometrics 106(1), 1-25. | doi:10.1016/S0304-4076(01)00080-X (UT Capitole repository; MaRDI) | verified | Order-m partial frontier. |
| aragon2005nonparametric | Aragon, Y., Daouia, A. & Thomas-Agnan, C. (2005). "Nonparametric Frontier Estimation: A Conditional Quantile-Based Approach." Econometric Theory 21(2), 358-389. | doi:10.1017/S0266466605050206 (Cambridge Core) | verified | Order-alpha partial frontier. |
| daraio2007advanced | Daraio, C. & Simar, L. (2007). Advanced Robust and Nonparametric Methods in Efficiency Analysis: Methodology and Applications. Springer. | doi:10.1007/978-0-387-35231-2 (Springer) | verified | Reference text for partial frontiers. |
| kumbhakar2000stochastic | Kumbhakar, S. C. & Lovell, C. A. K. (2000). Stochastic Frontier Analysis. Cambridge University Press. | doi:10.1017/CBO9781139174411 (Cambridge Core) | verified | Reference text for SFA. |

## (g) Diffusion

| key | full citation | URL/DOI checked | status | relevance |
|---|---|---|---|---|
| bass1969new | Bass, F. M. (1969). "A New Product Growth for Model Consumer Durables." Management Science 15(5), 215-227. | doi:10.1287/mnsc.15.5.215 (IDEAS) | verified | Diffusion dynamics behind the saturation result. |
| vidale1957operations | Vidale, M. L. & Wolfe, H. B. (1957). "An Operations-Research Study of Sales Response to Advertising." Operations Research 5(3), 370-381. | doi:10.1287/opre.5.3.370 (EconPapers; INFORMS) | verified | Referee round. Sales response to spend limited by the unsaturated market. Authors appear with initials only in all records checked. |
| nerlove1962optimal | Nerlove, M. & Arrow, K. J. (1962). "Optimal Advertising Policy under Dynamic Conditions." Economica 29(114), 129-142. | doi:10.2307/2551549 (SCIRP reference record and Taylor & Francis reference list, consistent across four independent citations) | verified | Referee round. Advertising as goodwill capital. No publisher or RePEc landing page was reachable; DOI taken from two independent reference lists. |
| dorfman1954optimal | Dorfman, R. & Steiner, P. O. (1954). "Optimal Advertising and Optimal Quality." American Economic Review 44(5), 826-836. | JSTOR 1807704 (from CAS library record ID); vol/pages from MPRA 10565 and T&F reference list; JSTOR issue i331366 is Vol. 44, No. 5, Dec. 1954 | verified | Referee round. Optimal spend condition. One reference list gives issue 4; the December 1954 issue is No. 5 per JSTOR's issue listing, so No. 5 is used. Pre-1999 AER has no DOI. |

## (h) AI economics and growth

| key | full citation | URL/DOI checked | status | relevance |
|---|---|---|---|---|
| aghion2019artificial | Aghion, P., Jones, B. F. & Jones, C. I. (2019). "Artificial Intelligence and Economic Growth." In Agrawal, Gans & Goldfarb (eds.), The Economics of Artificial Intelligence: An Agenda, Univ. of Chicago Press, 237-282. | nber.org/chapters/c14015 (chapter PDF cover gives pp. 237-282) | verified | Automation with Baumol-type limits. NBER page's suggested citation says 2018, but the book was published 2019. |
| acemoglu2025simple | Acemoglu, D. (2025). "The Simple Macroeconomics of AI." Economic Policy 40(121), 13-58. | doi:10.1093/epolic/eiae042 (via RePEc handle) | corrected | Brief said "2024/2025": the NBER WP (w32487) is 2024; the journal version is 2025. Cite the journal version. |
| brynjolfsson2025generative | Brynjolfsson, E., Li, D. & Raymond, L. R. (2025). "Generative AI at Work." QJE 140(2), 889-942. | doi:10.1093/qje/qjae044 (via RePEc handle) | verified | Micro productivity evidence. |
| eloundou2024gpts | Eloundou, T., Manning, S., Mishkin, P. & Rock, D. (2024). "GPTs are GPTs: Labor Market Impact Potential of LLMs." Science 384(6702), 1306-1308. | doi:10.1126/science.adj0998 (EurekAlert; CiteDrive gives issue and pages; SCIRP gives vol. 384) | corrected | Science title differs from the arXiv preprint ("...An Early Look at the Labor Market Impact Potential of Large Language Models," arXiv:2303.10130). Use the Science title. |
| babina2024artificial | Babina, T., Fedyk, A., He, A. & Hodson, J. (2024). "Artificial Intelligence, Firm Growth, and Product Innovation." JFE 151, 103745. | doi:10.1016/j.jfineco.2023.103745 (IDEAS) | verified | AI investment raises firm growth. |
| trammell2023economic | Trammell, P. & Korinek, A. (2023). "Economic Growth under Transformative AI." NBER WP 31815 (rev. Apr 2026). | doi:10.3386/w31815 (NBER) | verified | Growth theory under transformative AI. Still a working paper as of the check. |
| davidson2021could | Davidson, T. (2021). "Could Advanced AI Drive Explosive Economic Growth?" Open Philanthropy, 25 Jun 2021. | coefficientgiving.org/research/could-advanced-ai-drive-explosive-economic-growth/ | corrected | Open Philanthropy has since renamed itself Coefficient Giving; the report is now hosted there. |
| erdil2023explosive | Erdil, E. & Besiroglu, T. (2023). "Explosive Growth from AI Automation: A Review of the Arguments." arXiv:2309.11690. | arxiv.org/abs/2309.11690 | verified | Explosive growth arguments. |
| epoch2025gate | Erdil, E., Potlogea, A., Besiroglu, T., Roldan, E., Ho, A., Sevilla, J., Barnett, M., Vrzla, M. & Sandler, R. (2025). "GATE: An Integrated Assessment Model for AI Automation." arXiv:2503.04941. | arxiv.org/abs/2503.04941 | verified | Epoch AI GATE model (econ.GN). Nine authors. |
| baumol1967macroeconomics | Baumol, W. J. (1967). "Macroeconomics of Unbalanced Growth: The Anatomy of Urban Crisis." AER 57(3), 415-426. | JSTOR 1812111 (from JSTOR cover page of a hosted PDF) | verified | Cost disease. AER pre-1999 has no DOI; JSTOR URL given. |

## (i) AI inference cost trends

| key | full citation | URL/DOI checked | status | relevance |
|---|---|---|---|---|
| gundlach2025price | Gundlach, H., Lynch, J., Mertens, M. & Thompson, N. (2025). "The Price of Progress: Price Performance and the Future of AI." arXiv:2511.23455 (v2, 23 Mar 2026). | arxiv.org/abs/2511.23455 | corrected | Brief gave only "The Price of Progress." Current (v2) full title above. An aggregator lists the v1 subtitle as "Algorithmic Efficiency and the Falling Cost of AI Inference" (unconfirmed on arXiv, so not used). Price at fixed performance falls about 5-10x/yr; frontier price rises 3-18x/yr. |
| epoch2025inference | Cottier, B., Snodin, B., Owen, D. & Adamczewski, T. (2025). "LLM Inference Prices Have Fallen Rapidly but Unequally across Tasks." Epoch AI Data Insight, 12 Mar 2025. | epoch.ai/data-insights/llm-inference-price-trends | corrected | Brief said "LLM inference price trends"; that is the URL slug, not the title. Declines of 9x-900x per year depending on milestone. |

## (j) Markups and intangibles

| key | full citation | URL/DOI checked | status | relevance |
|---|---|---|---|---|
| deloecker2020rise | De Loecker, J., Eeckhout, J. & Unger, G. (2020). "The Rise of Market Power and the Macroeconomic Implications." QJE 135(2), 561-644. | doi:10.1093/qje/qjz041 (via RePEc handle) | verified | Rising markups. |
| haskel2017capitalism | Haskel, J. & Westlake, S. (2017). Capitalism without Capital: The Rise of the Intangible Economy. Princeton University Press. | ABIE catalogue; ISBN 9780691175034 | verified | Scalability of intangibles. No DOI. |
| crouzet2023rents | Crouzet, N. & Eberly, J. (2023). "Rents and Intangible Capital: A Q+ Framework." Journal of Finance 78(4), 1873-1916. | doi:10.1111/jofi.13231 (published PDF header); pages from Kellogg page | corrected | Brief said "2019 or later" for intangibles and investment; this is the published 2023 JF article. The DOI suffix is 13231, not 13249 as one search snippet suggested. |
| peters2017intangible | Peters, R. H. & Taylor, L. A. (2017). "Intangible Capital and the Investment-q Relation." JFE 123(2), 251-272. | doi:10.1016/j.jfineco.2016.03.011 (EconPapers) | verified | Added. Intangibles in q theory. |

## (k) Non-GAAP and stock-based compensation

| key | full citation | URL/DOI checked | status | relevance |
|---|---|---|---|---|
| bradshaw2002gaap | Bradshaw, M. T. & Sloan, R. G. (2002). "GAAP versus The Street: An Empirical Assessment of Two Alternative Definitions of Earnings." JAR 40(1), 41-66. | doi:10.1111/1475-679X.00038 (EconPapers) | verified | Gap between GAAP and Street earnings. |
| barth2012why | Barth, M. E., Gow, I. D. & Taylor, D. J. (2012). "Why Do Pro Forma and Street Earnings Not Reflect Changes in GAAP? Evidence from SFAS 123R." RAST 17(3), 526-562. | doi:10.1007/s11142-012-9192-9 (IDEAS) | verified | Exclusion of SBC from non-GAAP earnings. (The 2010 Stanford WP "Non-GAAP and Street Earnings: Evidence from SFAS 123R" is the earlier version and is not cited separately.) |
| mohanram2020stock | Mohanram, P., White, B. & Zhao, W. (2020). "Stock-Based Compensation, Financial Analysts, and Equity Overvaluation." RAST 25(3), 1040-1077. | doi:10.1007/s11142-020-09541-0 (Springer) | verified | Analysts excluding SBC issue biased price targets. |

## (l) AI-assisted research and disclosure

| key | full citation | URL/DOI checked | status | relevance |
|---|---|---|---|---|
| lu2024ai | Lu, C., Lu, C., Lange, R. T., Foerster, J., Clune, J. & Ha, D. (2024). "The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery." arXiv:2408.06292. | arxiv.org/abs/2408.06292 | verified | Automated research pipeline. |
| si2025can | Si, C., Yang, D. & Hashimoto, T. (2025). "Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers." ICLR 2025. | iclr.cc/virtual/2025/poster/29961; openreview.net/forum?id=M23dTGWCZy | verified | LLM ideas rated more novel, slightly less feasible. |
| gottweis2026accelerating | Gottweis, J., Weng, W.-H., Daryin, A., Tu, T., et al. (2026). "Accelerating Scientific Discovery with Co-Scientist." Nature 655(8122), 487-496. | doi:10.1038/s41586-026-10644-y (HUJI CRIS; CEU repository; Nature Asia press release) | corrected | Brief said Google "AI co-scientist" 2025 (arXiv:2502.18864, "Towards an AI co-scientist"). Now published in Nature (19 May 2026) under a new title; cite the journal version. Over 30 authors, abbreviated with "others." |
| korinek2023generative | Korinek, A. (2023). "Generative AI for Economic Research: Use Cases and Implications for Economists." JEL 61(4), 1281-1317. | doi:10.1257/jel.20231736 (EconPapers) | verified | Added. AI use in economics research. |
| thorp2023chatgpt | Thorp, H. H. (2023). "ChatGPT Is Fun, but Not an Author." Science 379(6630), 313. | doi:10.1126/science.adg7879 (CVTISR record; openresearch.amsterdam) | verified | Added. Authorship policy for AI. |
| mohapatra2026expectations | Mohapatra, A. & Pruthi, D. (2026). "Expectations and Practices around AI Disclosure in CS Research." arXiv:2608.23271. | arxiv.org/abs/2608.23271 | verified | Added. Disclosure norms vs practice. |
| arxiv2023policy | arXiv (2023). "arXiv Announces New Policy on ChatGPT and Similar Tools." arXiv blog, 31 Jan 2023 (edited 7 Feb 2023), by Kat Boboris. | blog.arxiv.org/2023/01/31/arxiv-announces-new-policy-on-chatgpt-and-similar-tools | verified | Original policy announcement. The post itself says the moderation page holds the current version, so cite arxiv2026policy for current policy and keep this entry only for history. |
| arxiv2026policy | arXiv (2026). "arXiv Moderation: Policy for Authors' Use of Generative AI Language Tools." arXiv help pages. Accessed 29 Oct 2026. | info.arxiv.org/help/moderation/index.html#policy-for-authors-use-of-generative-ai-language-tools | verified | Current policy wording: authors must "report in their work any significant use of sophisticated tools", including "text-to-text generative AI"; "generative AI language tools should not be listed as an author"; authors "take full responsibility for all its contents, irrespective of how the contents were generated." No last-updated date on the page. Note: the one-year-ban rule reported in May 2026 (hallucinated references or other "incontrovertible evidence" of unchecked LLM output) is NOT on this page; it was announced by arXiv's CS section chair on X and in press coverage, so do not attribute it to arxiv2026policy. |

## Primary sources cited by other sections (added to keep keys resolvable)

Keys `bessemer2024rulex`, `epoch2025gate` and `epoch2025inference` were already in use in sections/discussion.tex and sections/horizons.tex; the entries verified above were renamed to those keys (formerly deeter2024rulex, erdil2025gate, cottier2025llm) so that every \cite in the paper resolves.

| key | full citation | URL/DOI checked | status | relevance |
|---|---|---|---|---|
| palantir2026q2 | Palantir Technologies Inc. (2026). "Palantir Reports Q2 2026 U.S. Comm Revenue Growth of 149% Y/Y and Revenue Growth of 93% Y/Y; ..." Press release, Ex. 99.1 to Form 8-K, 3 Aug 2026. | sec.gov/Archives/edgar/data/0001321655/000132165526000039/a2026q2ex991pressrelease.htm | verified | Confirms figures used in discussion.tex: revenue growth 93%, GAAP operating margin 47%, adjusted operating margin 62%, company-reported "Rule of 40 score of 155%". |
| iconiq2026state | ICONIQ (2026). "2026 State of AI Report: The Builder's Economy." ICONIQ Venture & Growth, July 2026. | iconiq.com/growth/reports/state-of-ai-2026 | verified | Confirms figures used in horizons.tex: AI product gross margins "from 45% in 2025 to a projected 53% in 2026, and 59% in 2027." |
| sec2026xbrlapi | U.S. Securities and Exchange Commission (2026). "EDGAR Application Programming Interfaces (APIs)." SEC.gov; XBRL frames endpoint at data.sec.gov/api/xbrl/frames. | sec.gov/search-filings/edgar-application-programming-interfaces (also reachable via sec.gov/page/sec-api-documentation) | corrected | Added by the lead agent. Page exists and documents the frames API ("aggregates one fact for each reporting entity that is last filed"). Title corrected from "EDGAR Application Programming Interfaces: XBRL Frames" to the page's actual title; URL moved from howpublished to url. |

## Dropped or not used

| item | status | reason |
|---|---|---|
| "Growth first, profit later?" (Davidsson et al. 2009, JBV) | corrected, not dropped | No paper with this title exists in JBV 2009; the intended paper is "Growing profitable or growing from profits..." (see davidsson2009growing). |
| He & Bu (2025), "Academic journals' AI policies fail to curb the surge in AI-assisted academic writing," arXiv:2512.06705 | dropped | Verified to exist, but left out to keep the disclosure cluster short; Mohapatra & Pruthi is more directly on disclosure statements. Add if wanted. |
| Barnds (2025), "Improving the Rule of 40...," Princeton senior thesis | dropped | Exists (Princeton DataSpace) and is directly on topic (regresses EV/revenue on growth and margin, 2015-2025), but it is an undergraduate thesis, not peer-reviewed. Mention in a footnote if desired. |
| Iregbulem (2022), "Breaking Apart the Rule of 40," Substack | dropped | Practitioner blog regression (finds growth and FCF margin roughly equally weighted after fixed effects). Useful context, not citable as evidence. |
| Cronin (2022), "The Rule of 40 and the New SaaS Reality," Kellogg | dropped | Cited on Wikipedia, but the PDF could not be located or verified. |
| Goddard, Tavakoli & Wilson (2005), Applied Financial Economics 15(18), 1269-1282 | dropped | Verified (doi:10.1080/09603100500387139) but about profitability determinants, not the growth-profit link; the 2009 JBR paper is the better fit. |

## Notes for the authors

1. **Positioning.** The academic literature on the Rule of 40 is very thin. Lee (2024, Applied Finance Letters) is the only peer-reviewed study found; it is an empirical return-predictability test with no theory. No paper was found (SSRN, RePEc, arXiv, Google-indexed journals) that models the feasible growth-margin set or derives the Rule-of-X weight. The nearest theoretical precursor is Marris (1963, 1964), whose growth-valuation frontier should be credited explicitly.
2. **Practitioner priority on "Rule of 60".** Bain (Bosche et al. 2022) asked "Is 60 the new 40?" more than three years before Vista (2026). Cite both.
3. **Counterpoint.** Bain (Lipman et al. 2026) argues AI may lower attainable scores (a "Rule of 30") because of inference costs. This is useful for the AI comparative-statics section.
4. **Pages without DOIs** (Higgins 1977, Baumol 1967, Mueller 1972, Lee 2024, Penrose, Haskel & Westlake, Gordon 1962, Macaulay) carry stable URLs or ISBNs instead.
