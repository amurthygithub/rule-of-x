# Lead-author integration to-do (Part II and III)

- **Core, Gordon–Loeb:** theory_core.tex has a LaTeX comment marking where the Gordon–Loeb citation goes, in prop:tasks-security. The key is now in refs_part2.bib.
  - Insert the citation with the caveat that the 1/e bound holds only for two classes of breach function.
  - Remove the comment.
- **Merge bibliographies:** refs.bib, part2/refs_part2.bib and part2/refs_modern.bib. Deduplicate keys, and use \bibliography{refs,part2/refs_part2,part2/refs_modern}, or merge into a single file.
- **Paper structure:**
  - Part I: sections 3 to 6.
  - Part II: core (sec:tasks), ext (sec:ext), regimes (sec:regimes), product (sec:product).
  - Part III: engine and validation.
  - Appendices: proofs for each part, Part II data, engine spec, traceability, test program, protocol.
- **Literature:** literature_part2.tex and literature_modern.tex go into Section 2 as subsections, or Part II gets its own related-work section.
- **Protocol appendix:** add the Part II team, the six-agent restart after the interrupt, the author's requests by time, the data downloads, the O*NET MySQL conversion and the IWA/DWA renumbering issue.
- **Title:** propose a new one to the author.
- **Licenses:** CC BY-NC-ND notice in paper.tex (done). PolyForm Noncommercial for the engine (LICENSE.md and NOTICE.md done). The replication package needs NOTICE.md and LICENSE.md at build time.
- **Abstract:** must stay at or under 1,920 characters after adding Parts II and III.
- **Part I:** check its literature against the modern theory map.
- **Protocol appendix, rebuilt from notes/agent_log.md** (author request 08:21):
  - full agent roster by phase, with roles, inputs, outputs, status and the usage figures reported;
  - the author's interventions, with timestamps;
  - the interrupt and restart;
  - verification statistics: checks passed, references verified, corrected and dropped, audit findings and their dispositions, QA pass counts, pressure-test findings and dispositions;
  - the model identifier;
  - what the agents did not do (the author decided X, Y, Z);
  - limits of agent review.
  A short paragraph in the introduction, plus a sentence in the abstract if space allows, points to it.
- **Core Section 23:** the examples are illustrative pending part2/refs_reliability.bib and data/tasks/params_reliability.yaml. When those land, ground the examples and insert the automation-bias citation, which is marked by a comment in theory_core.tex. The Gordon-Loeb comment should be handled the same way. Then remove all placeholder comments.
- **Compile check:** run the whole paper with the mathptmx font package. Macros it does not provide, such as \jmath, break the build.
- **Final auditor, priority spot-checks:** recent facts the agents state as verified but the lead agent has not re-checked at the primary source:
  - Executive Order 14412 and OMB M-26-15 (post-quantum cryptography deadlines);
  - the final NIST IR 8547 (October 2026), with deprecation after 2030 and disallowance after 2035;
  - OMB's $7.1B estimate;
  - Bick, Blandin and Deming (Management Science 2026);
  - Acemoglu and Restrepo (QJE 2026);
  - Gans and Goldfarb (2026);
  - Ide and Talamas (JPE 2025);
  - the IBM 2026 breach cost of $4.99M;
  - the 2025 FASB ASU and Section 174 status, once the accounting agent reports.
- **Bibliography:** merge refs_modern.bib (81 entries).
- **Literature placement:** literature_modern.tex goes into Section 2 or a Part II related-work section.
- **Global notation pass, after all the theory is in.** Clashes the extension theorist found:
  - Φ, decision bandwidth in Part II, clashes with Φ, Part I's possibility envelope in Prop industry.
  - ℓ_dec, decision latency, clashes with ℓ, Part I's opportunity.
  - b_p clashes with b, Part I's capital per unit of output in Prop entry.
  - ϑ, altruism, is visually close to θ.
  Rename on the Part II side, and build a notation table for the whole paper.
- **Length:** the extension section alone is about 25 pages, plus 11 pages of proofs. Expected total: Part I about 60 pages and Part II theory about 75 pages before Part III. Restructure the paper as a main text with condensed statements and the full results in appendices; the author will decide on a split (blind spot 10).
- **Assumptions audit, second round, after the engine is stable.** 323 engine defaults are still class d, and 100 params.yaml blocks are class d.
  - Rerun the auditor on the engine's defaults.yaml.
  - Link defaults to grounded params where possible.
  - Replace the rest with firm-supplied inputs or scenario dimensions.
  - Then run engine sensitivity (Morris and Sobol), re-rank the parameters and ground the top-ranked ones.
- **Headline wording:** the abstract, introduction and conclusion must state the 39% threshold as conditional on c_c (range about 23 to 68%), and the horizon ranges as "under scenario assumptions" (assumptions_memo.md, Section 2).

## Added 09:05
- Competing-interests statement: the author's employer sells customer-service AI, and the product section uses customer-service pricing. Ask the author whether to add a disclosure line; the affiliation is currently "Independent". This is the author's decision.
- Product section bib: vendor list-price @misc entries with access dates, BLS OEWS May 2025, and Gilbert–Newbery (1982). The product theorist is adding them now.
- The product section runs about 10.5 pages; include it in the length review (item 10).
- ICONIQ margin crossover (2030, 2033 or never, depending on the fit): report it only as conditional on the fit.

## Added 09:15
- Backtest: rerun code/validation/backtest.py once the engine defaults and params.yaml are frozen. It reads both live, and the headline result depends on rho_rev.
- Abstract, intro and conclusion may claim only that the feasibility filters predict occupation-level employment change beyond exposure, conditional on rho_rev. They may not claim validation of the cost-crossover step, the automate-versus-augment choice, or firm-level predictions; the firm-level test is null.
- paper.tex bibliography must include all of refs, part2/refs_part2, part2/refs_modern and part2/refs_reliability, plus the product, accounting, labor and competition bibs once they exist.
- theory_core is about 21 pages and theory_product about 10.5; include both in the length review.
- oesm21in4.zip has been requested from the author. When it arrives, the backtest adds the occupation × industry test.
- Product section now uses refs_product.bib; the final bibliography line must also include it.

## Added 09:40
- Running example: the invoice chain is being moved to one source of truth (data/examples/invoice_chain.yaml, .json, part2/tables/invoice_macros.tex). Regimes, accounting and engine regression tests read from it. At grounded inputs the example's NPV is negative. Its sign depends on int_cost_per_system and the ι/(1−ι) convexity, both class d.
- Second assumptions round, first priority: ground int_cost_per_system ($60k, range $20k–200k) and the readiness convexity, because they decide the sign of the main worked example.
- Merge: uncomment the \input of theory_competition in theory_ext.tex; add refs_competition to \bibliography.
- Decision taken: the engine uses durable share dur = 1 − φ̄^ind(1 − HHI) from cor:ext-game-engine in place of def:ext-motives. The latter ignores the volume response and understates the durable gain by half under linear demand; checked as 2/(n+1) under symmetric linear Cournot. Update the def:ext-motives text at assembly to point to the corollary.
- Bibliography must also include part2/refs_accounting.bib (theory_ext now cites its tax keys) and part2/refs_regimes.bib once created. Tornado baseline in theory_ext is being rebased to ψ = 1 (current law); decided by the lead agent at 10:00.
- theory_ext Shapley 'taxes' scenario: its move to ψ = 1 is now in the baseline (rebased 10:05), so the scenario's +0.85 reflects only its other components. At assembly, check that the scenario's text describes what it still changes, or redefine it (for example, a reversion to amortization or an automation tax τ_A).
- Backtest headline (superseded 11:05; for Paper 2 and Paper 3). Across occupations, the model's automatable share predicts the change in employment from 2021 to 2025, and the result survives controls for 2016–2019 and 2019–2021 trends (−0.050 and −0.055 per sd; both survive a 28-test correction). Four qualifications must appear wherever the result is cited:
  (a) A pre-COVID placebo (2016–2019) also shows the model share predicting employment, at 58% of the post-2021 slope per year. The filters therefore partly capture a trend that predates generative AI.
  (b) In occupation × industry cells weighted by cell, exposure fits best and the model adds nothing; with each occupation weighted equally the model share keeps −0.045. The result depends on weighting.
  (c) The cost-crossover step adds nothing (it is inert at the sourced review ratio, and the within-occupation wage test is uninformative), and no firm-level test survives.
  (d) The result depends on the review ratio: the model share loses significance above about 0.61–0.71.
  Describe the evidence as consistent with the feasibility filters, not as validation of the engine's mode choice or of its firm-level plans.

## Added 10:15 (Part I integration done)
- Apply partI_revision_memo.md Section 4 at assembly:
  - abstract: 42% central, conditional on compute share 20% (range 26 to 72%);
  - intro: 63 to 88; 42/32/59%; full running costs; horizons 45–156 / 37–123 / 32–125, durable 28–75 / 28–83 / 28–98; a sentence on execution pace;
  - conclusion: running costs and execution capacity;
  - discussion: a_min 1.5/3/4.6%, the p10 G&A wording, prop:acct-amin, the 404(b) EGC exemption, the upward GAAP bias under capitalization.
- paper.tex: add \usepackage{xurl}; input every Part II section; bibliography refs, part2/refs_part2, refs_modern, refs_reliability, refs_product, refs_competition, refs_accounting, refs_regimes, refs_labor (when they exist).
- The scratch full build is 202 pages. Raise the length and split decision (blind spot 10) with the author after assembly.
- Rate convention: all theory and engine rates are continuous; annual source values are converted with ln(1+r). τ: the engine default of 0.21 is a marginal rate and Part I's central 0.18 is an average effective rate. Explain this in the notation table.
- Second assumptions round: also ground the regulated build multiplier (1.5) and the 99% reliability target and 10× loss rule. All three are class d, and together with detection and run costs they decide the main example's feasibility and sign.
- Freeze step before assembly: once the engine defaults and params.yaml stop changing, regenerate invoice_chain.json and its macros, the accounting and regimes checks, the backtest macros and calibrate_horizons, and check that each output records the defaults.yaml hash it used. Engine defaults have changed during agent runs, for example ai_engineer_premium moving from 1.3 to 1.11 (Alekseeva et al. 2021).
- Notation pass: cor:labor-pace relies on theory_ext's bare `a` (affected FTE per process), and `a` is a reserved Part I symbol. Rename it in theory_ext.
- Bibliography merge: bls2026oews (refs_product) and bls2026oewsdev (refs_labor) cite the same OEWS May 2025 dataset. Merge them under one key.
- Labor rules still unverified at a primary source: Trevor and Nyberg's 31%, the length of German consultation, India's 15/26 convention and Chapter X notice, the DPDP Rules Gazette text, and the Slaughter slip opinion. Give these to the final auditor.
- Second assumptions round: also ground the new ICFR cost lines, all class d: itgc_setup $25k, access $20k a year, change $15k a year, ops $15k a year, interface setup $15k and $5k a year, close fallback $10k a year, close_delay_loss $250k, close_tolerance 8 hours. Candidate precedents: SOX compliance cost surveys (for example Protiviti's annual SOX survey of hours and cost per control) and the SEC OEA Section 404 study. Verify before use.
- RESOLVED 11:35: the Intercom Advanced price ($85 a seat a month, billed annually) and Fin's $0.99 per outcome were verified on intercom.com/pricing and fin.ai/pricing in the author's browser. Intercom is now Fin, a Salesforce company since 10 Sep 2026 (Salesforce investor release). Two of the four vendors now share a parent.
- Bibliography for Paper 2 must include part2/refs_acquirer.bib, which labor now cites (dessaint2017employment). Every agent compiles in its own scratch subfolder, because the shared build folder was overwritten.
- Freeze regeneration order: engine defaults → params → invoice_chain.py → make_labor_macros.py → the accounting, regimes and acquirer verify scripts → backtest.py → calibrate_horizons.py → estimate_organic.py → paper1_macros.py → playbook run_archetypes.py. Write this as one script, code/regenerate_all.sh, at the freeze.
- Freeze: have the data agent add the exhibit URLs (now listed at the end of notes/case_bending_spoons_f1_extract.md) to the params citations for the permanent_capital keys, and check that refs_acquirer.bib has an entry for each filing cited.
- Paper 2 assembly: Paper 2 cites Paper 1 as a companion paper. Add @misc murthy2026frontier to Paper 2's bibliography, mirroring murthy2026transformation in Paper 1.
- Paper 2 assembly: load every generated macro file (invoice, labor, accounting, acquirer, backtest, playbook) once in the main tex preamble, and remove the per-section \input of macro files (theory_regimes.tex currently inputs acquirer_macros.tex).
- Paper 1 title (author's choice, 12:03): "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation". It is set in paper1.tex. Update dist/arxiv_metadata.txt and the replication README at packaging.
- Paper 1 build: run from the repo root with TEXINPUTS=/home/claude/paper: and BIBINPUTS=/home/claude/paper:/home/claude/paper/paper1:, outputting to a private scratch directory, then copy the PDF back. Add code/build_paper1.sh at the freeze.
- Licensing: every distributed file derived from O*NET (data contract, playbook CSVs, engine reports) must carry the O*NET CC BY 4.0 attribution in notes/data_sources_part2.md §2.9. Our PolyForm Noncommercial license on our own code and data does not override CC BY on the O*NET-derived content. State this in the NOTICE and the replication README.

## Literature methods (from the v2 literature pass, for future agents)
- Reliable verification routes: the Crossref works endpoint (api.crossref.org/works/<doi>) and its query.bibliographic endpoint through WebFetch; EconPapers/IDEAS for aggregator records; NBER, arXiv (abs, html, pdf), PMLR, AEA, SEC, Fed, OCC, EUR-Lex, GovInfo, GAO and Cornell LII pages. doi.org, Wiley, SIAM, Nature and NRC pages often fail. WebFetch's offset reads later slices of long PDFs.
- Recurring citation-error patterns in this project:
  - a number cited for the wrong object (a substitution elasticity used as demand; an aggregate used per firm; a projection used as an actual; two survey series spliced across a question change);
  - wrong journal attribution;
  - retitled working papers;
  - key collisions across companion bib files.
- BibTeX keeps the first of repeated keys. Underscores, & and % in note fields break the LaTeX build.
