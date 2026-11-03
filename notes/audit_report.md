# Claims audit: "The Efficient Frontier of Growth and Profitability"

Auditor scope: numbers, external claims, citations and style in abstract, intro, data, empirics, horizons, discussion and conclusion (plus cross-checks into model.tex, the appendices and the tables). No paper file was edited.

Internal sources used: sections/tables/*.tex, notes/empirics_results.json, notes/calibration_results.json, notes/panel_build_log.txt, notes/verify_theory_output.txt, tab:ceiling in model.tex, and recomputation from data/panel.csv where the JSON has no stored value.

Most numbers check out. Every value in tab_desc, tab_envelope, tab_frontier, tab_organic, tab_qreg, tab_scale and tab_calib matches the JSON once rounded. The ceiling values in the text match tab:ceiling and verify_theory_output.txt. The findings below are the exceptions.

---

## A. NUMBER MISMATCH (internal numbers and cross-section consistency)

1. **empirics.tex, "Frontier scores are 93 to 129 on the GAAP basis".** The GAAP frontier scores are 129, 93, 100 and 89 (tab:frontier; JSON 2023-25 = 88.8). **Fix:** "89 to 129".

2. **abstract.tex and intro.tex, "the attainable score (85 to 130)" / "85 to 130 depending on period and margin definition".** Across the four definitions in tab:frontier the range is 85 to 132 (adjusted, 2010-15 = 132.1). **Fix:** either "85 to 132", or keep 85 to 130 and say "on the GAAP and FCF-after-SBC bases" (85 to 129).

3. **data.tex, "202 facts fail this test and are dropped".** panel_build_log.txt says "flow facts dropped for non-annual duration: 214". **Fix:** 214, or rerun the build and reconcile.

4. **horizons.tex, "A capital intensity of 1.5 lowers the ceiling at 30% market growth by 35 to 45 points".** Under psi=0 (the basis of tab:ceiling) the drop is k·G = 45.0 points in all three cases (97.1 to 52.1, 87.8 to 42.8, 79.0 to 34.0). With full expensing it is 35.5 to 38.3. **Fix:** "by 45 points (36 to 38 with full expensing of growth capital)".

5. **horizons.tex and intro.tex, "A score near 100 requires a rent rho of 60 to 80 points of revenue".** With the stated example (G=0.10, k=0.5, r=0.09), the competitive score is 0.095, so reaching 100 needs rho = 1 - 0.095, about 90 points. The 60 to 80 figure holds only for G = 20 to 40% with k = 0. **Fix:** "about 90 points in this example", or state the parameters that give 60 to 80.

6. **horizons.tex, free-entry example, "With G=0.10, k=0.5 and a cost of capital of 9%".** This breaks Assumption ass:entry (r > G); the entrant NPV pi/(r-G) is undefined at r < G. **Fix:** use model.tex's own example (G=0.05, r=0.10, k=0.5, giving 7.5 points), or keep G=0.10 and set r >= 0.11 (r=0.12 gives 11). Update intro.tex "about 10 in our example" to match.

7. **empirics.tex, SFA: "the implied mean shortfall rose from 16 to between 26 and 30 margin points".** JSON mean_ineff for GAAP is 15.8, 25.5, 30.0 and 27.3. **Fix:** "between 25 and 30". The after-SBC figures (13 to between 21 and 27) are correct.

8. **tab_calib.tex note, "Typical demand pull is lambda h=0.25, the pooled estimate for growing firms".** empirics_results.json stores no such estimate, and empirics.tex gives a range of 0.15 to 0.25. Recomputing from panel.csv on the alpha-regression sample (n=1,354) gives a median implied lambda h of 0.17 at alpha=0.25 (IQR 0.08 to 0.32). **Fix:** "0.25, the upper end of the 0.15 to 0.25 range implied for typical growers", and store the estimate in the results JSON. This value drives the "Typical pull" column and the "40 to 60 times" claim.

9. **horizons.tex, Rule-of-1000 paragraph: parameter sets are mixed.** The lambda h >= 9.3 threshold uses m0=0.5, G=0.2, alpha=0.25 (calibrate_horizons.py). The next sentence, "can score 1,000 in at most one year and 140 in at most nine", uses Corollary cor:transient with m0=0.6 (R_inf=0.8). At m0=0.5 the 140-point bound is 8 years (ln50/ln(1+0.7/1.2) = 8.5). model.tex also gives a different Rule-of-1000 threshold (8.71 at alpha=0.3, m0=0.6). **Fix:** use one parameter set throughout, or state the corollary's parameters inline.

10. **intro.tex "elasticity ... of about 0.2 to 0.45"; empirics.tex summary "alpha approx 0.2-0.45"; empirics.tex "beta ... between about 2.3 and 5" vs model.tex "beta in [2.2,5]".** The estimates are 0.20 and 0.43 (JSON alpha_est). **Fix:** "0.20 to 0.43" and beta "2.3 to 5" everywhere, or say explicitly that [0.2, 0.45] is a rounded working range.

11. **empirics.tex, "The 90th percentile moved much less, and the 99th percentile stayed near or above 100 in most years".** In points the GAAP P90 fell more than the median (57.4 to 40.4 is -17.0, against -12.1 for the median); it fell less only in relative terms (-30% vs -51%). After SBC, P90 fell 18.4 points against 9.8 for the median. P99 by period fell from 119 to 84 (GAAP) and from 115 to 68 (after SBC). By year it was 80, 65 and 65 in 2022 to 2024. **Fix:** report the P90 and P99 changes in points. Note that "held at the top" applies to the frontier score, not to the upper percentiles.

12. **horizons.tex, "85 to 119, which brackets the empirical frontier score of 85 for 2023-25 and 96 to 121 in earlier periods".** 121 (2010-15) lies above 119, so the range does not bracket it. **Fix:** "spans the 2023-25 frontier score of 85 and most of the earlier range (96 to 121)".

13. **horizons.tex, "the estimated growth-spend elasticity alpha=0.25".** 0.25 is not an estimate; it lies between the pooled estimate (0.20) and the FE estimate (0.43). **Fix:** "alpha=0.25, within the estimated range".

14. **empirics.tex, "Excluding acquisition-driven firm-years lowers frontier scores by up to 14 points".** The changes run from -13.7 to +2.1. In 2023-25 the organic score is higher on both bases (GAAP 91 vs 89; after SBC 87 vs 85). **Fix:** "changes frontier scores by -14 to +2 points".

15. **empirics.tex, "the 95th-percentile margin is about 25 to 45 points whether g is zero or 70%".** Across periods and the two bases, phi_0.95(g) spans 19.3 (GAAP 2020-22) to 48.8 (GAAP 2023-25). **Fix:** "about 20 to 50 points".

16. **calibration_results.json, "ceiling" block: stale and inconsistent with tab:ceiling.** calibrate_horizons.py computes the ceiling with c_c=0.15 and a_min=0.05 ("central") and c_c=0.10 ("opt"). That gives 68.6/78.6/93.6 and 76.4/86.4/101.4, while tab:ceiling and the text use verify_theory.py values (62.8/72.8/87.8; favorable max 97.1). The JSON "opt" value of 101.4 contradicts "at most 97". **Fix:** align calibrate_horizons.py with verify_theory.py before shipping the replication package.

17. **appendix_protocol.tex, "the theory agent ... added Proposition~\ref{prop:envelope} to reconcile model and data".** The flat-frontier reconciliation is prop:industry. prop:envelope is the comparative-statics proposition (aliased prop:capital). **Fix:** \ref{prop:industry}.

18. **abstract.tex, "the Rule of 40 and its growth-weighted variants are iso-value lines tangent to it".** Only the iso-score line at R* is tangent. The line g+m=0.4 is a pass mark (Remark rem:r40), and intro.tex states this correctly. **Fix:** "are iso-value lines, and the maximal score is reached where one of them is tangent to the frontier".

19. **appendix_protocol.tex, "it checked 65 references ... corrected 8 and dropped 5".** refs.bib now has 67 entries. arxiv2023policy and sec2026xbrlapi are missing from ref_verification.md. **Fix:** log both and update the count.

20. **data.tex, "margins between -300% and 100%" (reads as a sample filter) vs appendix_data.tex, "sets margins outside [-3,1] to missing".** **Fix:** use one description. If margins are set to missing, the 3,842 count is not conditioned on margins; say so.

---

## B. EXTERNAL CLAIM

21. **Palantir Q2 2026 (discussion.tex, intro.tex): VERIFIED.** Source: 8-K Ex. 99.1, 3 Aug 2026. The release gives revenue growth of 93% y/y, GAAP operating margin of 47%, adjusted operating margin of 62% and "Rule of 40 score of 155%". It defines the score as y/y revenue growth plus adjusted operating margin. 93 + 47 = 140 checks.

22. **Palantir Q1 2026: VERIFIED.** The Q1 release (8-K 000132165526000026) gives 85% growth, 46% GAAP margin, 60% adjusted margin and "Rule of 40 score of 145%". empirics.tex says "company-reported quarterly score exceeded 140 in 2026", which is consistent. If you name a specific number, cite the Q1 release.

23. **Palantir FY2025 (empirics.tex: 56% growth, 32% GAAP margin, score 88): CONSISTENT** with the panel (g=0.562, m_op=0.316) and with reported FY2025 revenue of $4.475B.

24. **CoreWeave FY2025 (data.tex, empirics.tex: 168% growth, near-zero margin, 167 to 14): VERIFIED.** Source: BusinessWire release, 26 Feb 2026. Revenue was $5,131M vs $1,915M; the GAAP operating loss was $46M (-0.9%); capex was $10.3B and OCF $3.06B. These figures are consistent with an FCF-after-SBC margin of -154%.

25. **AppLovin FY2025 (empirics.tex: 70% growth, 76% operating margin, score 146): PARTLY VERIFIED.** The 70% growth to $5.48B is confirmed. The 76% GAAP operating margin could not be checked (the 10-K fetch was truncated). Separate data note: AppLovin sold its Apps business in June 2025, and the frames API returns restated continuing-operations revenue for 2023 and 2024 but original totals for 2022. The panel therefore shows a spurious 2023 growth rate of -34.6% (reported: about +17%). The text does not cite that row, but it undercuts the "spot checks of the panel" safeguard; check other divestiture cases.

26. **ICONIQ 2026 (horizons.tex: 45% in 2025, 53% projected for 2026, 59% projected for 2027): VERIFIED,** quoting the July 2026 edition. **INACCURATE attribution:** "well below the 75-80% of classic subscription software" is not in ICONIQ (checked on the report page and the SaaStr summary). **Fix:** cite a separate SaaS gross-margin source for 75-80%, or drop the comparison.

27. **Epoch AI (horizons.tex: "fallen by a median of about 50 times a year across benchmarks"): UNVERIFIED at the primary source.** The data insight (Cottier et al., 12 Mar 2025) headlines "ranging from 9x to 900x per year" depending on the performance milestone, with a 40x/yr GPQA example. Repeated fetches of the page did not surface a median. A secondary source quotes Epoch as "a median decline of 50x per year, jumping to 200x per year" since Jan 2024, so the figure probably sits in a collapsed section. **Fix:** confirm and quote Epoch's exact wording, say "across performance thresholds" rather than "across benchmarks", and give the 9-900x range alongside, as literature.tex already does.

28. **Gundlach et al. (horizons.tex: "by 5 to 10 times a year for frontier models"): VERIFIED,** with a wording fix. The abstract (v2, 23 Mar 2026) says the price "for a given level of benchmark performance" fell "around 5x to 10x per year, for frontier models on knowledge, reasoning, math, and software engineering benchmarks". The literature claim that the price of running frontier models rises is confirmed on the v2 arXiv page. **Fix:** "the price of reaching a given benchmark score with frontier models fell 5 to 10 times a year".

29. **Bessemer Rule of X (model.tex, discussion.tex, literature.tex: weights of 2-3x): VERIFIED.** Deeter and Bondy, 2 Jan 2024. Their wording is "~2x for private companies", "~2-3x for public companies" and "(if growth is efficient)".

30. **Vista Rule of 60, January 2026: VERIFIED.** Published 8 Jan 2026 for "AI-enabled software companies"; Vista calls it "an emerging aspiration, not a universal baseline".

31. **Bain 2026 Rule of 30: VERIFIED in literature.tex. OVERSTATED in intro.tex.** Lipman et al. (8 Apr 2026) say firms that reinvest in AI to compete "may need to risk spending some time with a less ambitious benchmark, the Rule of 30". That is a temporary concession driven by reinvestment plus inference cost. Intro's "the costs of AI inference may push the benchmark down toward 30" drops both points. **Fix:** "suggest that firms reinvesting in AI may need to accept a Rule of 30 for a time".

32. **arXiv generative-AI policy (appendix_protocol.tex): VERIFIED** against the Jan 2023 blog: AI tools "should not be listed as an author", authors must "report ... any significant use", and signers "take full responsibility for all its contents". The blog calls itself the initial policy. **Fix:** also cite the current arXiv policy page.

33. **SOX Sections 302 and 906 (discussion.tex): VERIFIED** for officer certifications. Section 302 (15 U.S.C. 7241) requires the principal executive and financial officers to certify periodic reports, including controls. Section 906 (18 U.S.C. 1350) requires a CEO/CFO written statement with criminal penalties. **INACCURATE as phrased:** in "Under Sections 302 and 906 ..., named officers certify financial reports, and auditors sign opinions on them", auditor opinions are not a 302/906 requirement. **Fix:** split the sentence and attribute auditor opinions to the Exchange Act and PCAOB standards (ICFR attestation to Section 404(b)).

34. **Epoch GATE as used (horizons.tex: "a rate that only the explosive-growth scenarios of \citet{epoch2025gate} deliver"; conclusion.tex: "market growth that only explosive-growth scenarios provide"): INACCURATE.** GATE models aggregate output growth, which Epoch's announcement puts at 2 to 20 times the ~3% historical rate during automation. It does not model the growth of a software market G. Nothing supports "only", since segment markets can grow above 33% without aggregate explosive growth. **Fix:** "a rate comparable to aggregate output growth in the most aggressive automation scenarios of GATE", or cite erdil2023explosive or davidson2021could for the explosive-growth definition, and remove "only" from both sentences.

35. **data.tex, "Company-reported quarterly scores, which usually use adjusted margins and annualized quarters": INACCURATE for the cited case.** Palantir's score is quarterly y/y growth plus the quarterly adjusted margin, with no annualization. **Fix:** "quarterly year-over-year growth and adjusted quarterly margins".

36. **discussion.tex, "compute that a firm owns is capitalized and depreciated, so it never enters EBITDA or adjusted operating margin": INACCURATE.** Depreciation is deducted in operating income, and so in the paper's adjusted margin (operating income + SBC) and in Palantir's adjusted operating income. Only EBITDA excludes it. **Fix:** "it enters operating margins only through depreciation spread over its assigned useful life, never enters EBITDA, and appears in full only in free cash flow".

37. **abstract.tex "the most widely used performance benchmark for software firms"; intro.tex "the most widely cited single-number benchmark", "levels the rule's originators did not contemplate", "as is now widely claimed": UNVERIFIABLE** superlatives with no citation. **Fix:** soften ("a widely used benchmark") or cite roche2021saas or depeyrot2018hacking.

38. **literature.tex, roche2021saas ("more than 200 software firms over 2011 to 2021"): UNVERIFIABLE this session** (McKinsey blocks fetching). It relies on ref_verification.md.

---

## C. CITATION

39. **Key resolution: PASS.** All 67 cited keys exist in refs.bib, all 67 entries are cited, and BibTeX reports no warnings.

40. **iconiq2026state is cited for a figure it does not contain** (75-80% classic SaaS gross margin). See item 26.

41. **epoch2025gate is mischaracterized** as delivering software-market growth above 33% (horizons.tex). See item 34.

42. **lipman2026ai is overstated in intro.tex.** See item 31.

43. **epoch2025inference: "median ... across benchmarks"** does not match the source's headline (a 9-900x range across performance thresholds). See item 27.

44. **bass1969new, literature.tex "Our saturation result uses the diffusion dynamics of \citet{bass1969new}": overstated.** The model uses a logistic headroom term h(s)=1-s/s_bar with spend-driven growth and no innovation or imitation coefficients; model.tex says only "familiar from Bass-type diffusion". **Fix:** "resembles the saturation dynamics of".

45. **markowitz1952portfolio, "borrows its geometry": decorative.** Acceptable in a literature review but carries no content; keep or drop.

46. **bessemer2024rulex, discussion.tex "the weights of two to three that \citet{bessemer2024rulex} report for public cloud companies".** Bessemer recommends the weights (a normative base assumption, "if growth is efficient"); it does not report an estimate. **Fix:** "recommend".

47. **Intro contribution sentence citing \citep{aghion2019artificial,acemoglu2025simple,epoch2025gate}: decorative bundle.** None of the three concerns firm-level metrics. Acceptable as positioning.

48. **Spot-checked as fairly characterized** (abstract or summary fetched this session): feld2015rule, depeyrot2018hacking (16% of 86 firms in all five years 2013-17; EV/revenue double), bosche2022sixty, vista2026rethinking, lee2024evaluating (1,756 firms per the journal page; the MPRA version says 1,771), davidsson2009growing, federico2015heterogeneous (Spain), lee2014relationship (Korea; growth raises profit only in old firms), goddard2009sources, aghion2019artificial (Baumol), acemoglu2025simple (at most 0.66% TFP over 10 years), brynjolfsson2025generative (14% overall, 34% for novices), babina2024artificial, gundlach2025price, si2025can, gottweis2026accelerating (Nature, 19 May 2026), mohapatra2026expectations, barth2012why, mohanram2020stock, crouzet2023rents, palantir2026q2, arxiv2023policy. That is 22 citations.

49. **Not verifiable this session:** coad2007testing (no abstract retrievable) and roche2021saas. The gottweis2026accelerating volume and pages (655(8122), 487-496) are also unconfirmed. Re-check before submission.

50. **ref_verification.md has no entries for arxiv2023policy or sec2026xbrlapi.** See item 19.

---

## D. STYLE

51. **Em-dashes: NONE.** There are no "—" characters or LaTeX "---" in any .tex file. The "--" occurrences are en-dashes in compounds (growth--margin, Sarbanes--Oxley, human--AI, normal--half-normal) and ranges, which is correct usage.

Forecasts stated as fact rather than as conditional scenarios:

52. **intro.tex: "For exceptional asset-light firms, the calibrated maximal score is 121 to 220 in 2028, 95 to 194 in 2031 and 69 to 175 in 2036, converging toward 50 to 94 as their markets fill."** **Fix:** "Under our scenario assumptions, ... would be ..., and would converge toward ...".

53. **horizons.tex: "The maximal score for an asset-light firm with exceptional pull is then 121 to 220"; "Exceptional asset-light firms then score 95 to 194 in 2031 and 69 to 175 in 2036"; "the score converges to the saturated values of 48 to 75 in 2031 and 50 to 94 in 2036".** **Fix:** "would be / would score / would converge under these assumptions".

54. **horizons.tex: "but competition passes much of that decline to customers".** This is an uncited empirical assertion. **Fix:** "competition may pass much of that decline to customers".

55. **horizons.tex: "AI raises demand pull lambda h for firms whose products substitute for labor".** **Fix:** "can raise".

56. **horizons.tex, condition 5: "...remain human-accountable costs, and they scale with the damage a single automated failure can cause rather than with headcount".** This is an argument stated as fact. **Fix:** "we argue that they scale ...".

57. **discussion.tex: "Unlike most operating costs, they do not fall with automation and may rise with it".** **Fix:** "they need not fall with automation and may rise with it".

58. **discussion.tex, heading "What to track as headcount falls".** This presumes the forecast. **Fix:** "What to track if headcount falls".

59. **conclusion.tex: "market growth that only explosive-growth scenarios provide".** This states a forecast-dependent claim as fact; see item 34.

60. **appendix_protocol.tex:** the placeholder comments %REFEREEROUND and %FINALDECISIONS remain. The referee panel is described but its round and outcomes are not reported, and notes/referee2/ is empty. Fill these in before submission.

61. **Redundancy:** the CoreWeave sentence ("score falls from 167 to 14") appears three times (data.tex, empirics.tex capital-intensity subsection, empirics.tex summary). Keep one full statement and refer back to it.

---

## Counts

| Group | Items | Needing a text change |
|---|---|---|
| NUMBER MISMATCH | 20 | 20 |
| EXTERNAL CLAIM | 18 | 10 (items 25-27, 31, 33-38; 21-24, 28-30 and 32 are verified, 28 and 32 with optional wording or extra-citation fixes) |
| CITATION | 12 | 6 (items 40-44, 46) |
| STYLE | 11 | 10 (item 51: no em-dashes found) |

## Five most important fixes

1. **Free-entry example (horizons.tex, intro.tex).** r=0.09 < G=0.10 violates the model's r > G assumption, and the stated parameters need a rent of about 90 points, not 60 to 80. Re-parameterize and recompute both numbers.
2. **Frontier-score ranges (empirics.tex, abstract.tex, intro.tex).** The GAAP range is 89 to 129, not 93 to 129, and the four-definition range is 85 to 132, not 85 to 130. Fix it in the body and make the abstract and intro match.
3. **GATE (horizons.tex, conclusion.tex).** GATE does not model software-market growth, and "only explosive-growth scenarios" is unsupported. Rephrase as an aggregate-growth comparison and drop "only".
4. **Depreciation of owned compute (discussion.tex).** It does enter operating income and adjusted operating margin; only EBITDA excludes it. Correct the first measurement mechanism.
5. **AI-cost paragraph (horizons.tex).** The 75-80% SaaS comparison is attributed to ICONIQ, which does not contain it, and Epoch's "median 50x" could not be confirmed on the primary page. Add a SaaS-margin source and quote Epoch's exact wording with the 9-900x range.
