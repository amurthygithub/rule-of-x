# Citation & Prior-Art Ledger — "The Rule of 40 as a Price Line" (Murthy, Nov 2026)

**Auditor:** citation-auditor (referee team)
**Date:** 3 Nov 2026
**Method & honesty note:** I opened primary sources directly via `web_fetch` (the `web_search` backend returned only irrelevant/commercial noise, so I located known URLs from `refs.bib`, the paper's reference list, and standard repository/DOI endpoints, then fetched them). For each entry below, "Access level" states exactly what I opened. Where I did **not** open a source I say so explicitly and do not claim verification beyond bibliographic correctness. I did **not** read anything under `notes/reviews/` (per the blind-pass rule); I read `refs.bib`, the paper text, the supplement text, and the authors' own `ref_verification*.md` files were *available* but my conclusions below are from primary sources, not from those notes.

---

## Part A — High-priority numerical and novelty references

### (a) Lee (2024) — "Evaluating Stock Selection in the SaaS Industry: The Effectiveness of the Rule of 40"

1. **Found:** King Fuei Lee, *Evaluating Stock Selection in the SaaS Industry: The Effectiveness of the Rule of 40*, **Applied Finance Letters**, vol. 13 (2024), pp. 168–185. Confirmed via two independent records: MPRA Paper No. 121568 ("Forthcoming in Applied Finance Letters, Vol. 13 (July 2024): pp. 168–185") and Crossref (`DOI 10.24135/afl.v13i.761`, issued 2024-07-24, journal = Applied Finance Letters).
2. **Access:** abstract (MPRA full abstract + Crossref metadata). Full PDF is downloadable (797 kB) but I read the abstract only.
3. **Does it report the attributed result?** Yes. Abstract: "This paper investigates the effectiveness of the Rule of 40 as a stock selection criterion… analyses a sample of **1771** SaaS companies worldwide spanning the period 2003–2022… A modified rule, the SaaS Investing **Rule of 65**, is proposed and found to outperform the Rule of 40." This matches the paper's claim that Lee "evaluates it as an investment screen … and proposes a 'Rule of 65.'"
4. **Parameter identification:** Sample = 1771 (abstract) worldwide SaaS firms, 2003–2022; outcome = stock-selection performance (Sharpe ratio, relative winners/losers). It is an *investment-screen* test, **not** a model of the growth–profitability frontier.
5. **Judgment:** **valid transport / minor citation discrepancy.** The paper writes "**1,756** SaaS firms" (paper1.txt L379–380) whereas the MPRA abstract says **1,771**. This is a 15-firm discrepancy (likely a transcription slip, or the published AFL version differs from the preprint). Flag for correction against the published PDF.

**"Only peer-reviewed study" claim.** I ran a Crossref title search (`query.title="Rule of 40"`, 30 rows). The **only** peer-reviewed journal article about the SaaS "Rule of 40" was the Lee (2024) item above; every other hit was unrelated (Olympic "Rule 40", a "40 per cent rule" in UK politics, cellular-automaton "Rule 40", the 60/40 pension rule, etc.). This corroborates — but cannot prove — the claim. See Part C for the bounded-search caveat.

### (b) Ganapati, Shapiro & Walker (2020) — "Energy Cost Pass-Through in US Manufacturing"

1. **Found:** Sharat Ganapati, Joseph S. Shapiro, Reed Walker, *Energy Cost Pass-Through in US Manufacturing: Estimates and Implications for Carbon Taxes*, **American Economic Journal: Applied Economics**, 12(2):303–42, April 2020. DOI 10.1257/app.20180474.
2. **Access:** full abstract (AEA article page); full text is paywalled.
3. **Does it report the attributed result?** Yes, verbatim. Abstract: "For the several industries we study, **70 percent of energy price-driven changes in input costs get passed through to consumers in the short to medium run**."
4. **Parameter identification:** The measured quantity is pass-through of **energy-price-driven input-cost changes to consumers**, in **US manufacturing**, "several industries", **short to medium run**. It is *not* software, *not* AI/compute, and the 70% is an aggregate over a few manufacturing industries (the abstract flags cross-industry heterogeneity).
5. **Judgment:** **valid transport, flagged by the authors themselves.** The paper uses it as ϕ=0.7 for an industry-wide AI cost shock and its own Table S11 records "A different industry; the right concept for an industry-wide AI cost change." This is the single most load-bearing numerical assumption (it sets the pass-through scenario), and it is transported across sector (manufacturing→software) and shock (energy→compute). The paper is honest about this; the reviewer should treat ϕ=0.7 as an assumption, not a measured software fact.

### (c) Kim, Garg, Peng & Garg (2025) — "Correlated Errors in Large Language Models"

1. **Found:** Elliot Kim, Avi Garg, Kenny Peng, Nikhil Garg, *Correlated Errors in Large Language Models*, **ICML 2025** (PMLR v267:30038–30066), arXiv:2506.07962 (submitted 9 Jun 2025).
2. **Access:** full abstract (arXiv); full text is available via arXiv HTML/PDF.
3. **Does it report the attributed result?** Yes at headline level. Abstract: "We find substantial correlation in model errors — on one leaderboard dataset, **models agree 60% of the time when both models err**." The paper's supplement (S2.6) gives the fuller numbers: "across 71 models on 14,042 four-option MMLU questions from HELM … 60% of the time on average, against one third for uniformly random wrong answers" and adds the second dataset (HF Open LLM Leaderboard, 349 models, 42.3%, baseline 12.7%).
4. **Parameter identification:** The figure is **P(same wrong answer | both models wrong)** on academic MMLU multiple-choice and resume-screening tasks. The paper states the caveat *correctly and explicitly*: "That figure is the probability of the same wrong answer given that both models are wrong; **it is not the probability that one model errs given that the other does, which it does not measure**." This is the correct reading of the source.
5. **Judgment:** **valid transport.** The 0.60 [0.42, 0.60] range used in Table S11 is correctly sourced. The paper does not overstate what the number measures. (The abstract alone does not contain the "71 models / 14,042 questions / HELM" detail — that lives in the body — but the 60% headline is confirmed.)

### (d) Deeter & Bondy (2024) — Bessemer "The Rule of X"

1. **Found:** Byron Deeter & Sam Bondy, *The Rule of X*, Bessemer Venture Partners Atlas, published **Jan 2, 2024**.
2. **Access:** full text (BVP page).
3. **Does it report the attributed result?** Yes, verbatim. "multiplier on growth rate **which today is ~2x for private companies and ~2-3x for public companies**"; "We recommend … a ratio of **~2x growth over profitability for late stage private businesses; public companies … ~2-3x multiple**." Formula: Rule of X = (Growth Rate × Multiplier) + FCF margin.
4. **Parameter identification:** The multiplier applies to *revenue growth* (added to FCF margin); weights are "today"/normalized-market recommendations for *late-stage/cloud* companies.
5. **Judgment:** **valid.** The paper's "multiplying growth by about 2 for private firms and 2 to 3 for public firms before adding free cash flow margin" is an exact match.

### (e) Feld (2015) — "The Rule of 40%"

1. **Found:** Brad Feld, *The Rule of 40% For a Healthy SaaS Company*, Feld Thoughts (blog), **Feb 3, 2015**.
2. **Access:** full text.
3. **Does it report the attributed result?** Yes. "The 40% rule is that your growth rate + your profit should add up to 40%." Feld writes he "heard something I've not heard before from a late stage investor. He described what his firm called the 40% rule."
4. **Parameter identification:** growth = YoY MRR growth; "profit" = EBITDA (Feld's preferred baseline), for SaaS firms "at scale" (≥$50M revenue). The paper's "revenue growth plus profit margin" is a fair paraphrase (Feld says "profit", prefers EBITDA).
5. **Judgment:** **valid.** Attribution ("Feld popularized it after hearing it from a late-stage investor") is accurate.

### (f) Vista Equity Partners (2026) — "Rethinking Software Benchmarks"

1. **Found:** The paper's URL (`…/insights/rethinking-software-benchmarks-in-an-ai-driven-market/`) **resolves (HTTP 200)**. The live page's canonical URL/title has been changed to the slug **`ai-rule-of-60-software-benchmarks`**, which directly corroborates the "Rule of 60" subject. (The article body is JS-rendered; the canonical slug 404s on a direct fetch, and the Wayback snapshots show only navigation.)
2. **Access:** URL exists + canonical title/slug evidence only; **body text not retrieved**.
3. **Does it report the attributed result?** **Not directly confirmed.** The "Rule of 60" phrasing is corroborated by the retitled canonical slug ("ai-rule-of-60-software-benchmarks"), but I did not read the sentence describing it.
4. **Parameter identification:** n/a (body not opened).
5. **Judgment:** **not fully verified / likely valid.** The claim "Vista … describe a Rule of 60 as an emerging aspiration for AI-enabled software firms" is *strongly* supported by the retitling but should be pinned to the live page text. Note: the paper's title "Rethinking Software Benchmarks in an AI-Driven Market" appears **stale** — the piece has since been retitled to reference "Rule of 60".

### (g) Cazals, Florens & Simar (2002) and Aragon, Daouia & Thomas-Agnan (2005)

1. **Found (bibliographic):** Cazals, Florens & Simar, *Nonparametric Frontier Estimation: A Robust Approach*, **Journal of Econometrics** 106(1):1–25, 2002, DOI 10.1016/S0304-4076(01)00080-X (= **order-m** frontier). Aragon, Daouia & Thomas-Agnan, *Nonparametric Frontier Estimation: A Conditional Quantile-Based Approach*, **Econometric Theory** 21(2):358–389, 2005, DOI 10.1017/S0266466605050206 (= **order-α / conditional-quantile** frontier).
2. **Access:** bibliographic only (correct canonical DOIs in refs.bib); full text paywalled, not opened.
3. **Does it report the attributed result?** These **are** the canonical citations for the partial-frontier estimators. The paper's mapping is correct: order-m = expected maximum of *m* draws (Cazals et al. 2002); conditional-quantile/order-α (Aragon et al. 2005). The paper's empirical section uses both as robustness (order-m with m=25; Ψ₀.₉₀ conditional quantile).
4. **Parameter identification:** n/a (method citations).
5. **Judgment:** **valid (bibliographic).** Correct attribution of partial-frontier estimators; not opened full text.

### (h) Marris (1964), Solow (1971), Odagiri (1981)

1. **Found (bibliographic):** Marris, *The Economic Theory of 'Managerial' Capitalism*, Macmillan 1964 (and Marris 1963, QJE 77(2):185–209, DOI 10.2307/1884399); Solow, "Some Implications of Alternative Criteria for the Firm", in Marris & Wood (eds), *The Corporate Economy*, Macmillan 1971, pp. 318–342 (DOI 10.1007/978-1-349-01110-0_10); Odagiri, *The Theory of Growth in a Corporate Economy*, Cambridge UP 1981 (DOI 10.1017/CBO9780511895609).
2. **Access:** bibliographic only (standard citations, correct DOIs); not opened.
3. **Does it report the attributed result?** These are genuine antecedents of a growth–profitability/valuation tangency for the managerial firm (growth-maximization vs. valuation/other criteria). The paper's claim ("the tangency between a growth–profit transformation curve and a valuation line goes back to Marris, Solow and Odagiri") is a fair and standard characterization.
4. **Parameter identification:** n/a (antecedents).
5. **Judgment:** **valid (bibliographic).** Correct, appropriate antecedents; not opened full text.

### (i) Arkolakis (2010) — "Market Penetration Costs…"

1. **Found:** Costas Arkolakis, *Market Penetration Costs and the New Consumers Margin in International Trade*, **Journal of Political Economy** 118(6):1151–1199, December 2010, DOI 10.1086/657949 (NBER WP 14214, Aug 2008).
2. **Access:** full abstract (NBER page).
3. **Does it report the attributed result?** Yes, verbatim: "a firm … pays an **increasing marginal cost to access additional consumers**." This is exactly the "rising marginal penetration costs" the paper cites.
4. **Parameter identification:** increasing marginal cost of reaching *additional consumers* (the new-consumers margin), calibrated to French exporter data — a trade/industrial-organization setting, used by the paper as a reduced-form microfoundation.
5. **Judgment:** **valid transport** (used only as a reduced-form precedent, not a number).

### (j) Gourio & Rudanko (2014) — "Customer Capital"

1. **Found:** Francois Gourio & Leena Rudanko, *Customer Capital*, **Review of Economic Studies** 81(3):1102–1136, 2014, DOI 10.1093/restud/rdu007.
2. **Access:** full abstract (EconPapers).
3. **Does it report the attributed result?** Yes, verbatim: "Introducing search frictions generates long-term customer relationships, **rendering the customer base a state variable for firms, which is sluggish to adjust**." Matches the paper's "customer base as a slow-moving state variable."
4. **Parameter identification:** customer base = a state variable built via selling/marketing spend, sluggish to adjust; affects investment, profits, value, markups, Tobin's q.
5. **Judgment:** **valid** (used as reduced-form precedent).

### (k) Vidale & Wolfe (1957) and Nerlove & Arrow (1962)

1. **Found (bibliographic):** Vidale & Wolfe, *An Operations-Research Study of Sales Response to Advertising*, **Operations Research** 5(3):370–381, 1957, DOI 10.1287/opre.5.3.370 (= sales-response model). Nerlove & Arrow, *Optimal Advertising Policy under Dynamic Conditions*, **Economica** 29(114):129–142, 1962, DOI 10.2307/2551549 (= goodwill model).
2. **Access:** bibliographic only; not opened.
3. **Does it report the attributed result?** These are the canonical classics; the paper's characterization ("sales-response model … spend converts the unsaturated part of the market"; "goodwill model") is accurate.
4. **Parameter identification:** n/a (method citations).
5. **Judgment:** **valid (bibliographic).**

### (l) Dorfman & Steiner (1954)

1. **Found (bibliographic):** Dorfman & Steiner, *Optimal Advertising and Optimal Quality*, **American Economic Review** 44(5):826–836, 1954 (JSTOR 1807704).
2. **Access:** bibliographic only; not opened.
3. **Does it report the attributed result?** The paper's optimal-spend condition — "spend equals the spend elasticity times the net score value of the growth it buys" (L309–310, L726–727) — is a correct restatement of the Dorfman–Steiner optimal-advertising condition (advertising-to-sales ratio = ad-elasticity ÷ price-elasticity; equivalently, marginal revenue product of advertising = marginal cost). The attribution is appropriate.
4. **Parameter identification:** the paper's condition uses "spend elasticity" (elasticity of growth w.r.t. spend) × "value of growth" — a generalized version of Dorfman–Steiner.
5. **Judgment:** **valid (bibliographic).** Loose-but-recognizable paraphrase of a classic result; not opened.

### (m) Brynjolfsson, Li & Raymond (2025) — "Generative AI at Work"

1. **Found:** Erik Brynjolfsson, Danielle Li, Lindsey Raymond, *Generative AI at Work*, **Quarterly Journal of Economics** 140(2):889–942, 2025, DOI 10.1093/qje/qjae044 (confirmed via NBER w31161 "Published Versions").
2. **Access:** abstract (NBER) + published-version metadata.
3. **Does it report the attributed result?** Yes. "increases productivity … by **14% on average**, including a **34% improvement for novice and low-skilled workers** but with minimal impact on experienced and highly skilled workers" — matches the paper's "document productivity gains from a generative AI assistant for customer-support agents."
4. **Parameter identification:** 5,179 customer-support agents; staggered introduction of a conversational assistant; issues-resolved-per-hour; heterogeneity by skill.
5. **Judgment:** **valid.** (Note: Semantic Scholar returned 404 for this DOI; that is an indexing gap, not a citation error — the NBER page confirms DOI and pages.)

### (n) Acemoglu (2025) — "The Simple Macroeconomics of AI"

1. **Found:** Daron Acemoglu, *The Simple Macroeconomics of AI*, **Economic Policy** 40(121):13–58, 2025, DOI 10.1093/epolic/eiae042 (confirmed via NBER w32487 "Published Versions": "Economic Policy, vol 40(121), pages 13-58").
2. **Access:** abstract (NBER) + published-version metadata. (OUP page is Cloudflare-gated → 403.)
3. **Does it report the attributed result?** Yes. "aggregate productivity effects over the next decade are likely to be modest" = NBER abstract "no more than a 0.66% increase in TFP over 10 years … predicted TFP gains … less than 0.53%."
4. **Parameter identification:** task-based model; TFP gain over 10 years; driven by task exposure × task-level cost savings (Hulten-type); caveats on hard-to-learn tasks.
5. **Judgment:** **valid.** Citation exists exactly as cited (journal, vol/issue, pages, DOI all correct).

### (o) Svanberg et al. (2024) — "Beyond AI Exposure"

1. **Found:** Maja S. Svanberg, Wensu Li, Martin Fleming, Brian C. Goehring, Neil Thompson, *Beyond AI Exposure: Which Tasks are Cost-Effective to Automate with Computer Vision?*, **MIT FutureTech / SSRN working paper**, Feb 8, 2024.
2. **Access:** full abstract (MIT FutureTech page; SSRN abstract 6691902).
3. **Does it report the attributed result?** Yes, with a small nuance. Source: "at today's costs U.S. businesses would choose not to automate most vision tasks that have 'AI Exposure', and that **only 23% of worker wages being paid for vision tasks would be attractive to automate**." The paper says "only 23% of the wages paid for **exposed tasks** would be economical to automate."
4. **Parameter identification:** the 23% is **wages paid for *vision* tasks** (computer-vision exposure specifically), not all AI-exposed tasks; at "today's costs"; US businesses.
5. **Judgment:** **valid transport with minor imprecision.** The paper's "exposed tasks" slightly over-generalizes: the source's denominator is *vision-task wages* (computer-vision only). The paper's surrounding sentence does say "on computer vision," so it is not misleading, but the phrase "exposed tasks" should ideally read "vision-exposed tasks."

### (p) ICONIQ (2026) — "2026 State of AI Report"

1. **Found:** ICONIQ, *2026 State of AI Report: The Builder's Economy*, ICONIQ Venture & Growth, July 2026.
2. **Access:** full text (ICONIQ web page, incl. downloadable PDF link).
3. **Does it report the attributed result?** Yes, verbatim. "**Gross margins are improving, jumping from 45% in 2025 to a projected 53% in 2026, and 59% in 2027.**" Also matches the paper's other parameters: "surveys of **over 300 executives at software companies building AI products**" and "Spending on AI for internal productivity … projected to rise from **11% of revenue in 2025 to 16% in 2026, heading toward 19% in 2027**. And many companies underestimate the true cost."
4. **Parameter identification:** gross margin of *AI products sold to customers* (incl. talent and hosting), 2025 actual → 2026/2027 projected; survey of ~300 software executives building AI products. The paper correctly notes this is the cost structure of *products sold to customers*, not the cost of a firm automating its own work — a correct and important conditioning.
5. **Judgment:** **valid.** The paper's numbers (45/53/59; 300 executives; 11/16/19) match the source exactly.

### (q) Kwa et al. (2025) — METR "Measuring AI Ability to Complete Long Software Tasks"

1. **Found:** Thomas Kwa et al., *Measuring AI Ability to Complete Long Software Tasks*, arXiv:2503.14499 (v4 10 Jul 2026), **NeurIPS 2025**.
2. **Access:** abstract only (arXiv). Full text available via arXiv HTML but I read the abstract only.
3. **Does it report the attributed result?** **Partially.** The paper exists and is the correct citation, but the abstract (about the "50% time horizon" metric and a ~7-month doubling time) **does not contain** the ">80% of successful runs cost <10% of human cost at $143.61/hour" figure. That figure appears to live in the paper body/appendix or in METR's companion public run data. The paper's supplement is transparent: it attributes ">80% of successful runs <10% of human cost" to Kwa et al. (2025) and separately flags that the tighter 0.4–1.1% figure is "**our computation** from METR's public run data (METR, n.d.)".
4. **Parameter identification:** cost per *successful run* relative to *human cost at $143.61/hr*, software tasks, 50% success threshold — but I could not verify the exact ">80%/<10%" from the abstract.
5. **Judgment:** **valid citation / figure not independently confirmed in what I opened.** Needs a precise pin-cite to the METR appendix or data file.

---

## Part B — The five claimed "new" results (novelty assessment)

The paper (L232–238) claims as new: (1) the **score budget**; (2) the **firm's decision weight vs. screening weight**; (3) **non-identification of firm frontiers from chosen points**; (4) the **accountability floor as a control standard under common-mode failure**; (5) the **attainable and expected frontiers**.

- **Not a Rule-of-40 novelty question for (1)/(2).** The tangency itself is explicitly and correctly credited to Marris (1964)/Solow (1971)/Odagiri (1981); the "sustainable growth" logic echoes Higgins (1977) and the Penrose effect (Uzawa 1969). What appears genuinely new is the *mapping onto the Rule of 40/Rule of X score* (the "price line" reading, the score budget as a finite share-headroom budget, and the decision-vs-screening weight distinction). I found **no** prior work that derives the Rule of 40 from a frontier, and my Crossref title search found **no** other peer-reviewed Rule-of-40 paper besides Lee (2024), which is purely an empirical investment-screen test. The theoretical treatment appears novel.
- **(3) Non-identification from chosen points** is a standard revealed-preference/econometric caveat in the frontier-estimation literature (observing endogenous choices does not identify the frontier); the paper's application to the growth–profitability frontier is likely a new *statement* but rests on a well-known principle.
- **(4) Accountability floor under common-mode failure** is the strongest novelty candidate. The beta-factor common-cause-failure model is standard (Hokstad & Rausand 2008; Mosleh et al. 1989), and correlated ML errors are now documented (Kim et al. 2025). I found **no** prior work that ties AI common-mode failure to the SOX-404/"no reasonable possibility of material misstatement" control standard and derives the "no number of layers on one provider passes" result. Plausibly novel; the paper's own framing ("What is new is the use of the term to set the composition and cost of a control design…", L1400) is accurate.
- **(5) Attainable vs. expected frontier** is a reasonable extension in the spirit of stochastic/robust frontier analysis; likely incremental rather than groundbreaking, but I found no direct predecessor in the Rule-of-40 context.

**Caveat (stated as required):** a bounded web search cannot prove no predecessor exists. My novelty assessment relies on (i) a Crossref *title* search (which would miss studies that discuss the Rule of 40 without naming it in the title), (ii) the paper's own antecedent citations, and (iii) my domain knowledge of the frontier/marketing/economics literatures. I did not find a direct predecessor for the five specific results, and the novelty claims appear **reasonable and honestly scoped**, but I cannot rule out adjacent work not surfaced by these tools.

---

## Part C — Most likely errors / items to correct

1. **Lee (2024) sample size:** paper says "1,756 SaaS firms"; MPRA abstract says **1,771**. Reconcile against the published AFL PDF. (Likely a transcription slip.)
2. **Ganapati ϕ=0.7 transport:** the most load-bearing numerical assumption is imported from *energy-cost pass-through in US manufacturing*, not software/AI. The abstract's 70% is "short to medium run" and "several industries." The paper flags the sector mismatch, but reviewers should treat ϕ=0.7 as an assumption, not a software measurement.
3. **Kwa/METR ">80% of successful runs <10% of human cost":** not in the arXiv abstract; needs a pin-cite to the METR paper appendix or public data file. (The paper's tighter 0.4–1.1% is honestly labeled "our computation.")
4. **Svanberg "23%":** source says "23% of worker wages being paid for **vision** tasks"; the paper writes "exposed tasks." Minor over-generalization (computer-vision exposure, not all AI exposure).
5. **Vista (2026) title is stale:** the piece has been retitled to an "AI Rule of 60" slug; the paper's "Rethinking Software Benchmarks in an AI-Driven Market" title no longer matches the live page. Body text not retrieved to confirm the "Rule of 60" sentence.
6. **Brynjolfsson DOI (10.1093/qje/qjae044)** is correct — Semantic Scholar's 404 is an indexing gap, not an error; do not "fix" it.

## Summary of verification counts
- **Fully verified against a primary source I opened (≥ abstract):** Ganapati 2020, Kim 2025, Lee 2024, Svanberg 2024, Feld 2015, Deeter & Bondy 2024, Acemoglu 2025, Brynjolfsson 2025, Kwa 2025 (paper exists; specific figure not in abstract), ICONIQ 2026, Arkolakis 2010, Gourio & Rudanko 2014, plus Lee 2024 uniqueness via Crossref. **(13)**
- **Bibliographically verified only (correct canonical DOI/citation; full text not opened):** Cazals et al. 2002, Aragon et al. 2005, Marris 1964, Solow 1971, Odagiri 1981, Vidale & Wolfe 1957, Nerlove & Arrow 1962, Dorfman & Steiner 1954. **(8)**
- **Partially verified (URL/canonical-title evidence only):** Vista 2026. **(1)**
