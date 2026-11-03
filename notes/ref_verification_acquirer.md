# Reference verification log: acquirer section (part2/refs_acquirer.bib)

Checked on 2026-10-29 by the corporate-finance theorist (acquirer section).

**Method.** sec.gov is not reachable from the tools, so the F-1 itself was not opened here: its entry rests on the lead agent's browser retrieval (URL and CIK in the extract). Every other item was found with WebSearch and verified by fetching a page that the search surfaced. For journal articles this was RePEc (EconPapers or IDEAS), a library catalogue (SUFE academic newsletter, BVB), or a citing paper that gives the full author list. For news items it was the article itself, or a faithful reproduction of a press release. Fields that could not be confirmed are left out of the BibTeX (for example DOIs not shown on the page I reached).

**Status key.** verified: every field confirmed. corrected: the item exists but differs from the brief or the extract. flagged: confirmed, but a detail used in the text rests on a secondary statement.

**Totals.** 56 entries (corrected count: the first round had 34, not 35; the news table has 16 rows, not 17). By type: 1 primary filing; 20 news items and company releases; 8 regulatory documents and law-firm alerts; 2 accounting-standard sources; 24 academic articles (one forthcoming); 1 practitioner study. Of these, 44 are verified, 3 corrected (Evernote's scale, Komoot's scale, the Harvest attribution) and 9 flagged (the F-1 itself, QuotedData, StreamingMedia, Lagaras et al., Karolyi et al., McKinsey, the Guideline 8 page date, the Meetup release date, the Deloitte page for ASC 350-20); the first round's log understated the corrections (3, not 1) and the flags (4, not 3). All 56 are cited: 54 in part2/theory_acquirer.tex and 7 in sections/measurement_acquired.tex (bendingspoons2026f1, dealroom2026ipo, fuller2002what, golubov2015extraordinary, laamanen2008performance, fasb2026asc35020, ifrs2022goodwill; the last two only there), which also cites damodaran2026cost from refs_regimes. No key duplicates another bibliography (checked against all ten). The test build (pdflatex and bibtex, plainnat, all ten bibliographies) gives no BibTeX warning from this file.

## Primary filing

| key | citation | page checked | status | what it supports |
|---|---|---|---|---|
| bendingspoons2026f1 | Bending Spoons S.p.A., Form F-1, filed 8 June 2026, CIK 2004711 | URL in notes/case_bending_spoons_f1_extract.md (lead agent's browser, 29 Oct 2026) | flagged | Every F-1 figure. These come from the extract; I did not open the filing. Amendments and the 424(b) prospectus were not read. |

## News and releases (cited only as "reported by")

| key | page fetched | status | what it shows |
|---|---|---|---|
| dealroom2026ipo | dealroom.co/news/136652 (1 Jul 2026) | verified | 57.97M shares at $29, above the $26 to $28 range; $1.68bn; Nasdaq Global Select, BSP; trading on Wednesday 1 July |
| axios2026ipo | axios.com/2026/07/01/bending-spoons-ipo-pricing | verified | priced at $29; the company was planning 34.4M shares and selling holders about 23.6M; about $1.68bn in total; $11bn valuation in an October equity round |
| quoteddata2026ipo | quoteddata.com, 2 Jul 2026 (G. Lumsden) | flagged | up 39.7% on the debut, closed $40.50; $18.4bn at the start of the day and $25.7bn at the close. The page names no source for the price data. |
| appleinsider2023evernote | appleinsider.com, 10 Jul 2023 | corrected | Workforce in Chile and the U.S. told on July 5 that "most of them" would be laid off; operations centered in Europe. **The extract's "all existing staff" is not supported: the source says "most", and that it is unclear how many were affected.** |
| leach2024mosaic | news.bloomberglaw.com (Bloomberg News, K. Leach, 10 Jan 2024) | verified | "None of Mosaic's 330 employees are expected to join the new company, IAC confirmed"; price "$100 million-plus" |
| techcrunch2024wetransfer | techcrunch.com, 8 Sep 2024 | verified | plan to lay off 75% of WeTransfer staff, confirmed to TechCrunch; Dutch media report over 350 employees; acquired July 2024 |
| tvbeurope2025brightcove | tvbeurope.com, 24 Mar 2025 | verified | 198 redundancies (about 200); over 600 employees worldwide and 300 in the U.S. at end-2023; citing Boston.com |
| streamingmedia2024brightcove | streamingmediablog.com, 25 Nov 2024 | flagged | $4.45 a share, about $233M, close expected 1H 2025; revenue 2024 guidance $197.7 to $198.7M, 2023 $201.1M. This is a blog quoting the release and guidance. Whether $233M is an equity or an enterprise value is not stated. |
| bikeradar2025komoot | bikeradar.com, 15 Sep 2025 (updated 17 Sep) | corrected (scale) | "up to 85 per cent of staff reportedly laid off" of about 150; the company declined to comment on scale. **The extract's "about three quarters" is not what this source says; I report the source.** |
| petapixel2026vimeo | petapixel.com, 23 Jan 2026 | verified | spokesperson: "a layoff was announced at Vimeo on January 20, 2026"; the scale comes from LinkedIn posts; no figure confirmed. I could not find the TechCrunch item of 22 Jan 2026 that the extract mentions. |
| ffxnow2026aol | ffxnow.com, 24 Feb 2026 | verified | 108 workers at the Reston office, under a WARN notice of 17 Feb 2026 (separations of about 94 on 1 March and 14 on 31 May); AOL purchase from Yahoo finalized 2 January |
| subscriptioninsider2026harvest | subscriptioninsider.com, 22 Aug 2026 | corrected (attribution) | per-seat pricing changed to per seat plus usage; one customer from about $130 to $2,110 a month ("roughly 1,500%"); citing **BBC News, 20 Aug 2026**. The extract attributes the figure to Bloomberg via Wikipedia; I did not find or check a Bloomberg article. |
| vimeo2025release | GlobeNewswire release of 10 Sep 2025, reproduced by AAP | verified | $7.85 a share; about $1.38bn; 91% premium to the 60-day VWAP; expected close Q4 2025. Equity or enterprise value is not stated. |
| marketscreener2026eventbrite | marketscreener.com, 10 Mar 2026 | verified | completed 10 March 2026; $4.50 a share; about $500M (agreement of 1 Dec 2025) |
| businesswire2025aol | Business Wire release of 29 Oct 2025, reproduced by mammothtimes | verified | $2.8bn debt financing "to finance the acquisition of AOL as well as future M&A"; no price given |
| techradar2025aol | techradar.com, 30 Oct 2025 (M. Moore) | verified | AOL bought for "around $1.5 billion"; the page attributes the figure to the company's announcement, which I did not see myself |

Items in the extract that I did not use, or could not verify:
- the TechCrunch statement of 1 Jul 2026 ("over $18 billion at the open"): QuotedData's $18.4bn at the start of the day is used instead;
- Wikipedia's account of Bloomberg on the first day: replaced by QuotedData;
- Airtable at $1.285bn (Aug 2026): not checked and not used;
- 500 million monthly active users and 9 million paying customers: not checked and not used;
- the two secondary errors the extract flags, KuCoin's "$13.1 billion" of 2025 revenue and IPOScoop's trailing net loss of $84.5 million, appear only as caught errors. The script checks both against the extract's tables (check A5).

## Academic

| key | page | status | what it supports |
|---|---|---|---|
| fuller2002what | EconPapers RePEc:bla:jfinan:v:57:y:2002:i:4:p:1763-1793 | verified | serial bidders (5 or more deals) gain on private and subsidiary targets and lose on public ones |
| golubov2015extraordinary | IDEAS eee/jfinec v116 i2 p314-330 | verified | acquirer fixed effects explain about as much of returns as all firm and deal characteristics; persistence across CEOs |
| laamanen2008performance | IDEAS bla/stratm v29 i6 p663-672 | verified | a high and variable acquisition rate lowers performance; size, scope and experience mitigate |
| zollo2004deliberate | EconPapers bla/stratm v25 i13 p1233-1256 | verified | codification helps and experience does not; replacing the target's top managers lowers performance (228 bank deals) |
| bloom2012americans | EconPapers aea/aecrev v102 i1 p167-201 | verified | establishments taken over by U.S. multinationals raised IT productivity; people-management practices |
| eliason2020how | EconPapers oup/qjecon v135 i1 p221-267 | verified | acquired dialysis facilities adopt the parent's practices; patient outcomes worsen |
| andrade2001new | EconPapers aea/jecper v15 i2 p103-120 | verified | combined announcement returns positive; operating improvement relative to peers |
| maksimovic2011post | EconPapers eee/jfinec v102 i2 p317-343 | verified | acquirers sell 27% and close 19% of target plants within three years; retained plants gain productivity |
| dessaint2017employment | EconPapers eee/jfinec v125 i2 p369-388 | verified | employment-protection increases cut takeovers by 14 to 27% and synergies by over half |
| lagaras2026mas | Harvard Law School Forum post, 11 Aug 2026 | flagged | forthcoming in the Journal of Finance (volume and pages not yet known); target workers' earnings fall about 6%, displaced workers' by more than 10% |
| doyle2007determinants | EconPapers (volume, issue, pages); SUFE (DOI, abstract) | verified | material-weakness firms are "smaller, younger, financially weaker, more complex, growing rapidly, or undergoing restructuring" |
| ashbaughskaife2007discovery | IDEAS eee/jaecon v44 i1-2 p166-192; SUFE (DOI) | verified | deficiency disclosers have more complex operations and recent organizational changes |
| brown2005corporate | IDEAS oup/rfinst v18 i1 p241-270; SUFE (all authors) | verified | roll-up IPOs deliver poor stock returns |
| tanriverdi2011cross | IDEAS inm/orisre v22 i4 p703-720 | verified | acquirers with cross-business IT integration capability earn higher CARs and operating performance |
| love2009character | SUFE (pages, DOI); BVB catalogue (volume 52, issue 2) | verified | downsizing has a strong negative effect on reputation |
| fracassi2022barbarians | EconPapers bla/jfinan v77 i3 p1439-1488 | verified | PE targets' sales grow 50% more; price increases of about 1% on existing products do not drive this |
| brown1992survivorship | EconPapers (volume, issue, pages); full author list from Carhart et al. (2002), core.ac.uk | verified | survivorship creates spurious performance persistence; no DOI confirmed, so none is given |

Keys reused from other bibliographies, not duplicated: sec2007faq and cfr2026sec229308 (refs_accounting) are cited through the accounting section; damodaran2026cost (refs_regimes) gives the r_w preset.

## Second round (29 October 2026): limits to buying growth, regulation, accounting

Added for sec:acq-limits (Paper 2) and rem:acquired-bounds (Paper 1). Each was checked at the page named.

### Academic and practitioner

| key | page | status | what it supports |
|---|---|---|---|
| renneboog2019failure | EconPapers RePEc:eee:corfin:v:58:y:2019:i:c:p:650-699 | verified | review: acquirers underperform, especially in public takeovers; serial acquisitions among the determinants |
| billett2008overconfident | EconPapers RePEc:inm:ormnsc:v:54:y:2008:i:6:p:1037-1051 | verified | CEOs' first deals have zero announcement effects, later deals negative |
| aktas2009learning | EconPapers RePEc:eee:corfin:v:15:y:2009:i:5:p:543-561 | verified (no DOI on the page, none given) | declining CARs from deal to deal are consistent with rational learning, not only hubris |
| hammer2017inorganic | IDEAS eee/corfin v45 p31-63 | verified | 9,548 buyouts, 4,937 add-ons; add-ons more likely and more productive with experienced sponsors, large platforms, easy financing |
| karolyi2025serial | cfr.ivo-welch.org/forthcoming/papers/karolyi2025serial.pdf | flagged | persistence of U.S. serial acquirers' returns (Golubov et al.) disappears for non-U.S. firms. Version of 4 Sep 2025; "forthcoming in CFR" rests on the URL path and the thanks to Editor Ivo Welch, not on a journal page |
| wollmann2019stealth | IDEAS aea/aerins v1 i1 p77-94 | verified | after the HSR threshold rose, investigations of newly exempt deals fell to nearly zero and competitor mergers rose |
| kepler2023stealth | EconPapers RePEc:bla:jfinan:v:78:y:2023:i:5:p:2837-2900; SUFE (abstract) | verified | about 40% more deals just below review thresholds; afterwards acquirers' and rivals' margins and prices rise |
| mckinsey2019lots | mckinsey.com (Rudnicki, Siegel, West, 12 Jul 2019) | flagged (practitioner) | Global 1,000, 2007-2017: programmatic acquirers earned higher excess TSR than large-deal, selective or organic peers |

Items in the coordinator's list already in the bibliography: fuller2002what, golubov2015extraordinary, brown2005corporate.

### Regulation (law-firm alerts are cited for facts they report, not for legal conclusions)

| key | page fetched | status | what it shows |
|---|---|---|---|
| doj2023guidelines | justice.gov/atr/merger-guidelines/applying-merger-guidelines/guideline-8 | flagged (date) | heading "Guideline 8: When a Merger Is Part of a Series of Multiple Acquisitions, the Agencies May Examine the Whole Series"; the page shows publication 21 Jun 2024, not the December 2023 issue date |
| ferguson2025memo | ftc.gov PDF, memo to FTC staff, subject "Merger Guidelines", 18 Feb 2025 | verified | "the FTC's and DOJ's joint 2023 Merger Guidelines are in effect" |
| thompsonhine2024rfi | thompsonhine.com, 28 May 2024 | verified | FTC and DOJ request for information on serial acquisitions and roll-ups, 23 May 2024 |
| stblaw2025welshcarson | stblaw.com, 27 Jan 2025 | verified | claims against Welsh Carson dismissed 13 May 2024; consent order 17 Jan 2025 (prior approval for anesthesiology acquisitions, board seat cut, notice requirements) |
| insurancejournal2026usap | insurancejournal.com (Reuters, J. Godoy), 24 Apr 2026 | verified | FTC settlement with USAP, terms confidential; FTC resumes the case if USAP does not execute it |
| bakerbotts2026hsr | bakerbotts.com, 20 Mar 2026 | verified | E.D. Tex. vacated the 2024 HSR rule on 12 Feb 2026; Fifth Circuit denied a stay on 19 Mar 2026; filers use the pre-February-2025 form |
| gtlaw2024illumina | gtlaw.com, 12 Sep 2024 | verified | CJEU, 3 Sep 2024, C-611/22 P and C-625/22 P: Article 22 cannot be used at the request of a member state that lacks jurisdiction |
| whitecase2025callin | whitecase.com, 17 Apr 2025 | verified | call-in powers in Cyprus, Denmark, Germany, Hungary, Ireland, Italy, Latvia, Lithuania and Sweden (nine); proposals elsewhere |
| macfarlanes2026draft | macfarlanes.com, 29 May 2026 | verified | Commission draft published 30 Apr 2026; the summary does not mention serial acquisitions or roll-ups. **The text says only that the summary does not mention them, not that the draft does not address them.** |
| reuters2026broadcom | Reuters (Foo Yun Chee), 14 Jul 2026, via The Star 15 Jul 2026 | verified | CISPE, Beltug, Cigref, VOICE and CIO Platform Nederland wrote on 10 Jul 2026 asking for interim measures against Broadcom; "steep price increases" on VMware's platform |

### Company releases and accounting

| key | page fetched | status | what it shows |
|---|---|---|---|
| silicon2024streamyard | silicon.co.uk (release of 9 Apr 2024) | verified | StreamYard, "the leading live-streaming and video-recording platform", acquired from StreamYard Top Corp (Hopin); no price |
| businesswire2024meetup | businesswire.com/news/home/20240124551711 | flagged (date) | completion of the Meetup acquisition; no price, no seller named; date read from the URL |
| fasb2026asc35020 | Deloitte DART, Roadmap: Goodwill and Intangible Assets, 2.1 | flagged (secondary page) | quotes ASC 350-20-35-1, "Goodwill shall not be amortized", except private companies and NFPs electing the alternatives |
| ifrs2022goodwill | ifrs.org news, 24 Nov 2022 | verified | the IASB "voted to retain the impairment-only approach" for goodwill |

### Searched and not used
- An agency challenge to any Bending Spoons acquisition: none found (WebSearch, 29 Oct 2026, several phrasings). The text says exactly that.
- Vimeo's HSR waiting period (reported to have expired on 6 Nov 2025): only an AI-generated page (panabee.com) was reachable; not used.
- Eventbrite's Form 8-K of 13 Feb 2026 (via StreetInsider): mentions no HSR, CFIUS or Treasury review; the "Treasury questions on Eventbrite", the CFIUS notice for AOL and Golden Power were not found in public sources and are requested from the F-1.
- Meetup's seller (AlleyCorp): not confirmed by the release; not used. Built In's article (AI-drafted) not used.
- The F-1/A (accession 000110465926076487) exists on EDGAR; not read (sec.gov unreachable).

## Third round (29 October 2026): final prospectus and post-IPO 6-Ks

| key | source | status | what it supports |
|---|---|---|---|
| bendingspoons2026prospectus | 424B4 of 1 Jul 2026 (Reg. No. 333-296573), read by the lead agent in the author's browser; extract section "Final prospectus" | flagged (read by the lead, not by me) | F-1 figures unchanged; offering terms (57,971,015 shares, 34,398,640 new, $29.00); non-GAAP reconciliation; Article 11 pro forma for 2025 and the three purchase prices |
| bendingspoons2026sixk | 6-K exhibits of 4 Aug, 13 Aug, 10 Sep, 25 Sep, 14 Oct and 28 Oct 2026, read by the lead agent | flagged (read by the lead, not by me) | Q2 2026 results and organic growth (company definition); net debt and leverage definition; Tractive, Airtable and Miro; term loan add-ons; senior secured notes; Berkshire Hathaway |

Totals now 58 entries (44 verified, 3 corrected, 11 flagged). Caught error added: Wikipedia's $900M for Tractive (6-K: EV $759M). The 6-K's net IPO proceeds of $1.10B exceed the gross value of the 34.4M new shares ($0.998B) but fit the over-allotment option on 5,244,026 company shares (424B4: estimated net $933M, or $1,079M with full exercise); about $21M remains unexplained, and the figure is not used in any calculation.

## Fourth round (29 October 2026, acquirer agent, round-1 review fixes): sec.gov read directly with WebFetch

sec.gov is now reachable through WebFetch for reading. The F-1 and the 424B4 are longer than the fetch window (about 124,000 characters of converted text, roughly their first third: cover, letter, summary, summary financial data and the start of the risk factors), so only their summary sections were read; the two Q2 2026 6-K exhibits were read in full.

| key | source read | status | what it supports |
|---|---|---|---|
| bendingspoons2026f1 | F-1 (tm2613674-7_f1.htm), summary sections | verified for the items listed; otherwise still flagged | U.S. GAAP basis; summary risk factor on material weaknesses (verbatim); the letter's sentence on targets' organic growth |
| bendingspoons2026prospectus | 424B4 (tm2613674-14_424b4.htm), summary sections | verified for the items listed; pro forma still flagged (beyond the window) | 2025 revenue, operating income, interest expense, operating and investing cash flows; 2025 and Q1 2026 non-GAAP add-backs; $29.00; estimated net proceeds $933M or $1,079M; the same material-weakness sentence |
| bendingspoons2026sixk | Ex. 99.1 of 13 Aug 2026 (results) and Ex. 99.2 (interim condensed consolidated financial statements), both in full; Ex. 99.1 of 14 Oct, 28 Oct and 29 Oct 2026 | verified | Q2 2026 income statement, interest $108,970k, reorganization $50,799k, transaction $6,553k, amortization $82,310k; organic growth 3% with "estimated pre-acquisition revenue", among unaudited operating results, not a non-GAAP measure, no Rule of 40; H1 cash flows (interest paid $49,737k and $161,153k; PP&E $282k and $3,969k; acquisitions $575,228k and $2,286,259k); notes $1.25B at 9.625% and €500M at 8.625% due 2032 at par, upsized from $1.5B; Berkshire $330M at $33.00 after $600M at the IPO, 4% stake |
| deloitte2026cashflow | Deloitte DART, Roadmap: Comparing IFRS Accounting Standards and U.S. GAAP, 4.3 Statement of Cash Flows | verified | "Interest paid and received should be classified as operating activities" under U.S. GAAP (ASC 230-10). The page does not give the paragraph number; ASC 230-10-45-17(d) is the codification paragraph (the FASB codification itself is behind a login and storage.fasb.org is blocked by the proxy) |
| deloitte2026acqcosts | Deloitte DART, Roadmap: Business Combinations, 5.4 Acquisition-Related Costs | verified | ASC 805-10-25-23 reproduced: acquisition-related costs expensed as incurred, except debt and equity issuance costs |
| pwc2026italy | PwC Worldwide Tax Summaries, Italy, Taxes on corporate income (last reviewed 13 July 2026) | verified | IRES 24%, IRAP 3.9%; interest excluded from the IRAP base of sales and manufacturing companies |
| hall1967tax | Hall and Jorgenson (1967), AER 57(3), 391-414 | flagged | Author, title, journal and volume confirmed (JHU course page on the Hall-Jorgenson model); issue and pages are the standard citation and consistent with Baumol (1967), AER 57(3), 415-426, in the P1 bibliography; JSTOR and EconBiz blocked the fetch, so no URL is given |

Totals now 62 entries in part2/refs_acquirer.bib (47 verified, 3 corrected, 12 flagged). The four new entries are also in paper1/refs_paper1.bib, marked "source: part2/refs_acquirer.bib", and the note of bendingspoons2026sixk now lists Ex. 99.2 in both files.
