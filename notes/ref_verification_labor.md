# Reference verification log: labor law, talent and jurisdiction (part2/refs_labor.bib)

Checked on 2026-10-29.

**Method.** As for the other Part II logs, direct API access was blocked: curl is blocked, and WebFetch accepts only URLs that a WebSearch has surfaced. So each item was found with web search and verified by fetching the page it surfaced. Three kinds of page were used:
- For statutes and official decisions:
  - official portals: govinfo.gov, EUR-Lex, gesetze-im-internet.de, legislation.gov.uk, indiacode.nic.in, cac.gov.cn, commission.europa.eu, dol.ny.gov, nj.gov;
  - government agencies: BLS, DBT, DSIT, PIB, VVGNLI;
  - where the official page could not be reached, a faithful reproduction (Cornell LII, FindLaw, california.public.law, gesetze.legal, buzer.de, lexetius.com, Code du travail numérique, Indian Kanoon, CNPD Luxembourg, the Luxembourg maritime authority's copy of the Official Journal) or a law-firm or court summary. These are flagged as such.
- For peer-reviewed work: RePEc/IDEAS/EconPapers, library catalogues (SUFE academic newsletter records, Fundación Mapfre, BVB, CRDCN, Penn repository) and author or university copies. Wiley, Sage, ResearchGate, Semantic Scholar and econbiz returned errors or bot pages.

**Status key.**
- **verified**: every field in the BibTeX entry was confirmed on a page listed in the row. Fields that could not be confirmed were left out.
- **corrected**: the item exists, but a field differs from the brief or from common citation; the BibTeX holds the corrected version.
- **flagged**: the item is confirmed, but a number or detail used in the text could not be confirmed at a primary page; see the note in the row.

All statutory items are `@misc` with the official citation. Titles are double-braced, because plainnat otherwise lowercases `\S` to `\s` and breaks the build.

**Totals.**
- 58 entries in `refs_labor.bib`: 49 verified, 2 corrected, 7 flagged.
- 57 are cited in `theory_labor.tex` (62 keys cited in all, including 5 reused). `dbt2024impact` is kept for the engine notes and is uncited.
- Six keys are reused from existing bibs and were not duplicated: `eu2016regulation`, `eu2024regulation` and `park2013turnover` (refs_part2.bib), `eu2026regulation` (refs_modern.bib), `acemoglu2022artificial` (refs.bib) and `dessaint2017employment` (refs_acquirer.bib).
- Two entries were removed as uncited after verification: `de2026mitbestg` and `de2026drittelbg`.
- Test build (pdflatex + bibtex, plainnat, scratchpad harness): no BibTeX warnings from `refs_labor.bib` and no undefined labor citations.

## (a) United States: WARN and state mini-WARN laws

| key | citation | URL checked | status | what it shows |
|---|---|---|---|---|
| us2023warn | Worker Adjustment and Retraining Notification Act, 29 U.S.C. 2101 to 2109; Pub. L. 100-379, 102 Stat. 890 (1988); U.S. Code 2023 ed. | govinfo.gov USCODE-2023-title29 chap23 sec2104 (fetched); sec2102 (fetched on the second attempt) | verified | s.2102: 60 days' notice, with reductions and 90-day aggregation unless causes are separate and distinct; s.2104: back pay and benefits for up to 60 days, and a civil penalty of up to $500 a day. |
| cfr2026warn | 20 C.F.R. 639.3 (Definitions) | law.cornell.edu/cfr/text/20/639.3 (eCFR itself not on the allowlist) | verified (reproduction) | Employer: 100+ employees excluding part-time, or 100+ including part-time working 4,000 hours a week in aggregate; plant closing 50+ at a site; mass layoff 33% and 50+, or 500+. |
| ca2026warn | Cal. Lab. Code 1400.5, 1401 | codes.findlaw.com (text current as of 1 Jan 2026); california.public.law s.1401 | flagged | Covered establishment of 75+ in the preceding 12 months; mass layoff of 50+ in 30 days; 60 days' notice. Read only on reproductions; the official leginfo.legislature.ca.gov page was not fetched. |
| nydol2026warn | NY DOL, WARN Act Fact Sheet (P483) | dol.ny.gov/warn-act-fact-sheet-p483 | verified | 50+ full-time employees in NY; 90 days' notice; mass layoff of 33% (at least 25) or 250; civil penalty of $500 a day, and back pay for 60 days. |
| njdol2026warn | NJ DOL, NJES-997 (rev. 2/26) | nj.gov/labor/.../NJES-997 (2-26).pdf | verified | Employers of 100+; 50+ terminated at or reporting to the establishment; severance of 1 week per full year, plus 4 weeks if notice is under 90 days. |
| bls2026jolts | BLS, The Economics Daily, 13 Oct 2026; JOLTS Table 4 | bls.gov/opub/ted/2026/...august-2026.htm; bls.gov/news.release/jolts.t04.htm | verified | Quits rates in Aug 2026 (preliminary, seasonally adjusted): total nonfarm 1.9%, information 1.1%, finance and insurance 1.0%, professional and business services 2.1%. |
| bls2026oewsdev | BLS, OEWS May 2025 national estimates (oesm25nat.zip) | file supplied by the author, logged in notes/data_sources_part2.md | verified (c) | SOC 15-1252 median annual wage $135,980. The key was renamed from `bls2026oews`, which `refs_product.bib` also defines for the same dataset with a different note. The lead may merge the two. |

## (b) European Union: collective redundancies and AI at work

| key | citation | URL checked | status | what it shows |
|---|---|---|---|---|
| eu1998directive | Council Directive 98/59/EC of 20 July 1998, OJ L 225, 12.8.1998, p. 16 | eur-lex.europa.eu/eli/dir/1998/59/oj/eng; maritime.public.lu copy of the OJ text | verified | Art. 1(1)(a) thresholds (10 at 21 to 99, 10% at 100 to 299, 30 at 300+ over 30 days; or 20 over 90 days); Art. 2 consultation in good time; Art. 4: 30 days after notification, extendable. |
| cjeu2009akavan | CJEU, 10 Sep 2009, Akavan Erityisalojen Keskusliitto AEK ry and Others v Fujitsu Siemens Computers Oy, C-44/08 | eu.vlex.com/vid/838727377; faegredrinker.com summary (BAILII returned a bot page) | verified (reproduction) | The duty to consult arises once strategic decisions compel the employer to contemplate or plan collective redundancies. |
| eu2024regulation (reused) and eu2026regulation (reused) | AI Act, Regulation (EU) 2024/1689; Digital Omnibus on AI, Regulation (EU) 2026/1744 | artificialintelligenceact.eu/article/26; eur-lex.europa.eu/eli/reg/2026/1744/oj; gibsondunn.com | verified | Art. 26(7): deployers inform workers' representatives before using a high-risk AI system at the workplace; Annex III high-risk obligations deferred to 2 Dec 2027. |

## (c) Germany

| key | citation | URL checked | status | what it shows |
|---|---|---|---|---|
| de2026kschg | Kündigungsschutzgesetz, ss.1a, 17, 18 | gesetze-im-internet.de/kschg/__18.html; gesetze.legal/bund/kschg/17 | verified | s.17(1) thresholds (more than 5 at 21 to 59; 10% or more than 25 at 60 to 499; 30 at 500+; 30 days); s.17(2) works-council information; s.18: dismissals take effect only after 1 month, extendable to 2; s.1a: 0.5 month per year. |
| de2026betrvg | Betriebsverfassungsgesetz, ss.87, 90, 102, 111, 112, 112a | gesetze-im-internet.de/betrvg/__111.html; buzer.de s.90; lexetius.com s.87; gesetze.legal ss.102, 112, 112a | verified | s.111 Nr. 5 (new work methods); s.90(1) Nr. 3 (planning of work processes, including AI); s.87(1) Nr. 6 (technical monitoring systems, conciliation board); s.102 hearing; s.112(4) and (5) conciliation board on the social plan; s.112a(1) thresholds. |
| de2026bgb | BGB s.622 | gesetze-im-internet.de/bgb/__622.html | verified | Employer notice of 1 to 7 months by length of employment. |
| (removed) de2026mitbestg, de2026drittelbg | MitbestG s.1; DrittelbG s.1 | gesetze-im-internet.de/mitbestg/__1.html; .../drittelbg/BJNR097410004.html | verified, then removed | Board co-determination at more than 2,000 (parity) and more than 500 (one third) employees. Not a timing constraint, so uncited. |

## (d) France

| key | citation | URL checked | status | what it shows |
|---|---|---|---|---|
| fr2026codetravail | Code du travail, arts L1233-30, L1233-57-4, L1233-61, L1233-71, L1234-1, L2312-8, R1234-2, R2312-6 | code.travail.gouv.fr/code-du-travail/{l1233-30, l1233-57-4, l1233-61, l1233-71, l1234-1, l2312-8, r1234-2, r2312-6} (Ministry of Labour, reproducing Légifrance) | verified | CSE opinion periods of 2, 3 or 4 months; validation in 15 days and homologation in 21; PSE at 50+ employees and 10+ dismissals; reclassification leave at 1,000+; notice of 1 or 2 months; indemnity of 1/4 month a year to 10 years and 1/3 beyond; consultation on new technologies, 1 to 3 months. |

## (e) United Kingdom

| key | citation | URL checked | status | what it shows |
|---|---|---|---|---|
| uk2026tulrca | TULRCA 1992 c.52, ss.188, 189, 193 | legislation.gov.uk/ukpga/1992/52/section/188/data.htm (revised to 25 Oct 2026); .../section/189/data.htm | verified | 20+ at one establishment within 90 days; consultation 30 or 45 days before the first dismissal; protective award up to 180 days from 6 Apr 2026. |
| uk2025era | Employment Rights Act 2025 c.36, ss.29, 30 | legislation.gov.uk/ukpga/2025/36/section/29 and /section/30/data.html | verified | s.29 inserts s.195A: a threshold number set by regulations, never below 20, in force for specified purposes from 6 Jan 2026 (S.I. 2026/3); s.30(2) raises the protected period to 180 days. |
| uk2026era1996 | ERA 1996 c.18, s.162 | legislation.gov.uk/ukpga/1996/18/section/162/data.htm | verified | 0.5, 1 or 1.5 weeks' pay per year by age; at most 20 years. |
| cipp2026limits | CIPP, "Statutory Redundancy Rates Announced for 2026/27", 24 Mar 2026 | cipp.org.uk/resources/news/statutory-redundancy-rates-announced-for-2026-27.html | verified (professional body) | Weekly cap of £751 from 6 Apr 2026 (GB), up from £719. The Increase of Limits Order itself was not fetched. |
| dbt2026threshold | DBT, Threshold for Triggering Collective Redundancy Obligations: Options Assessment, 26 Mar 2026 | assets.publishing.service.gov.uk/media/69c55ab5.../options-assessment-threshold-....pdf | verified | Preferred option: a fixed organization-wide threshold of 250 to 1,000, to be set in secondary legislation. |
| dbt2024impact | DBT, Strengthening Collective Redundancy Rights: Final Stage Impact Assessment, 21 Oct 2024, DBT-038-24-CMRR | assets.publishing.service.gov.uk/media/671259a6.../impact-assessment-strengthening-collective-redundancy-rights.pdf | verified (uncited) | 279,006 potential redundancies (GB, year to May 2024); average consultation of 36.9 days (20 to 99) and 55.5 days (100+); administrative cost £33.48 and £66.97 per employee consulted. |

## (f) India

| key | citation | URL checked | status | what it shows |
|---|---|---|---|---|
| in2020irc | Industrial Relations Code, 2020 (Act No. 35 of 2020) | indiacode.nic.in/bitstream/123456789/22040/1/aa202035.pdf (read to s.73); future.indiankanoon.org/doc/172435200 and /141247093 (s.77) | flagged | s.2(zr): supervisory staff drawing over Rs 18,000 a month are excluded; s.70: 1 month's notice, 15 days' average pay per completed year of continuous service (in excess of six months), and notice to government; s.77: Chapter X at 300+ workers, in factories, mines and plantations. **Not read:** ss.79 and 83 in the official text (s.83 is confirmed by VVGNLI), the s.79 notice length, and the 15/26 convention. |
| vvgnli2020irc | V.V. Giri National Labour Institute, summary of the IR Code 2020 | vvgnli.gov.in/sites/default/files/Industrial Relations Code, 2020.pdf | verified (government institute) | Prior-permission threshold raised to 300; re-skilling fund of 15 days' last drawn wages per retrenched worker. Its worker-definition salary figure (Rs 15,000) differs from the enacted s.2(zr) (Rs 18,000); the enacted text is used. |
| pib2025codes | PIB, New India Samachar, 16 to 31 Dec 2025, p. 40 | newindiasamachar.pib.gov.in/.../page40.html | verified | The four labour codes were implemented on 21 November 2025. |

## (g) Data residency

| key | citation | URL checked | status | what it shows |
|---|---|---|---|---|
| eu2016regulation (reused) | GDPR, Regulation (EU) 2016/679, Chapter V | cnpd.public.lu/.../rgpd/chapitre-5.html | verified | Art. 45 adequacy; Art. 46 safeguards (SCCs, BCRs); Art. 49 derogations. |
| eu2021scc | Commission Implementing Decision (EU) 2021/914 of 4 Jun 2021 | eur-lex.europa.eu/eli/dec_impl/2021/914/oj | verified | Standard contractual clauses; in force 27 Jun 2021. |
| eu2023dpf | Commission Implementing Decision (EU) 2023/1795 of 10 Jul 2023 | eur-lex.europa.eu/eli/dec_impl/2023/1795/oj/eng | verified | EU-U.S. Data Privacy Framework adequacy decision. |
| eugc2025latombe | General Court, 3 Sep 2025, Latombe v Commission, T-553/23 | business.cch.com/.../cjeulatomberelease.pdf (press release 106/25); lewissilkin.com; digitalpolicyalert.org; wilmerhale.com; gawel.ch (2 Jul 2026) | verified | Action dismissed. Appeal C-703/25 P lodged 31 Oct 2025, pending at 2 Jul 2026 (practitioner sources). |
| cjeu2015schrems | CJEU, 6 Oct 2015, Schrems, C-362/14 | cms.law summary (curia.europa.eu failed) | verified (summary) | Safe Harbour decision of 26 Jul 2000 invalid. |
| cjeu2020schrems | CJEU (Grand Chamber), 16 Jul 2020, Facebook Ireland and Schrems, C-311/18 | statewatch.org copy of the operative part | verified (reproduction) | Privacy Shield (2016/1250) invalid; SCC decision 2010/87 valid; authorities must suspend transfers where the clauses cannot be complied with. |
| ec2026adequacy | European Commission, Adequacy decisions page | commission.europa.eu/.../adequacy-decisions_en | verified | 17 entries (the U.S. only for DPF participants; UK renewed Dec 2025); China and India absent. |
| us2026slaughter | Trump v. Slaughter, No. 25-332 (U.S. 29 Jun 2026) | mayerbrown.com, 29 Jun 2026 | flagged | 6 to 3; FTC for-cause removal protection unconstitutional; Humphrey's Executor overruled. Slip opinion not fetched. The paper uses it only to say it raises a question about the oversight the DPF relies on; no court has applied it to the DPF. |
| cn2021pipl | Personal Information Protection Law of the PRC (2021) | cac.gov.cn/2021-08/20/c_1631050028355286.htm (Chinese text) | verified | Arts 38 to 40: assessment, certification or standard contract for exports; local storage for CIIOs and above volumes set by the CAC. |
| cn2024flows | CAC, Provisions on Promoting and Regulating Cross-Border Data Flows, 22 Mar 2024 | cac.gov.cn/2024-03/22/c_1712776612187994.htm (CAC release) | verified (release, not the full text) | Exemptions (trade, contract performance, HR management, small volumes) and volume thresholds; effective on publication. |
| cn2025certification | CAC and SAMR, Measures for the Certification of Outbound Transfers of Personal Information | cac.gov.cn/2025-10/17/c_1762449728518762.htm | verified | Certification for non-CIIOs transferring 100,000 to under 1 million people's PI (non-sensitive), or under 10,000 sensitive; no splitting; effective 1 Jan 2026. |
| in2023dpdp | Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023) | indiacode.nic.in/bitstream/123456789/22037/2/a2023-22.pdf | verified | s.16(1): the Central Government may restrict transfers to notified countries; s.16(2): stricter laws prevail; assent 11 Aug 2023. |
| in2025dpdprules | DPDP Rules, 2025, G.S.R. 846(E), 13 Nov 2025 | scconline.com blog, 14 Nov 2025; mirvolegal.com (20 Sep 2026); ssrana.in (13 Feb 2026); sflc.in | flagged | Rules 1, 2 and 17 to 21 in force on notification; rule 4 after a year; the rest from 13 May 2027. The Gazette text, and so the G.S.R. number, was not fetched (the number is from practitioner sources). A January 2026 proposal to shorten the timetable had not been notified by September 2026. |

## (h) Survivors, downsizing, hiring and retraining (peer-reviewed)

| key | citation | URL checked | status | what it shows |
|---|---|---|---|---|
| trevor2008keeping | Trevor, C. O. and Nyberg, A. J. (2008). AMJ 51(2), 259-276. doi:10.5465/amj.2008.31767250 | academicnewsletter.sufe.edu.cn/info/361794 (pages, DOI, abstract); documentacion.fundacionmapfre.org/.../101041.do (vol. 51, no. 2) | flagged | Downsizing predicts higher voluntary turnover, mediated by commitment and moderated by HR practices. The "1% downsizing, 31% more turnover" figure appears only in press coverage (wisc.edu clipsheet), so it is not used. |
| kim2025preventing | Kim, Y., Kim, A., Park, T.-Y., Oh, E.-J., Eo, S. S. and Song, K. (2025). HRMJ 35(1), 64-90. doi:10.1111/1748-8583.12552 | bvbvf1.bib-bvb.de PrimoRecord (authors, volume, pages); ilr.cornell.edu (DOI) | corrected | The ILR page cites it as "Park et al. (2024)" (online first). The catalogue gives first author Kim and the 2025 issue. 317 firms; an attenuated positive downsizing-turnover relationship, weaker under collective pay for performance. |
| sajjadiani2023who | Sajjadiani, S., Kammeyer-Mueller, J. and Benson, A. (2023). AMJ, 1929-1953. doi:10.5465/amj.2021.1327 | academicnewsletter.sufe.edu.cn/info/359433; phys.org; theglobeandmail.com | flagged | 1,620 stores over 22 months: 2.2 quits following a layoff announcement, 0.17 after a dismissal, 0.23 after a quit. The volume and issue were not shown, so they are omitted. The store size (93.6 workers) is from press coverage. |
| schwerdt2011labor | Schwerdt, G. (2011). Labour Economics 18(1), 93-101 | ideas.repec.org/a/eee/labeco/v18y2011i1p93-101.html | verified | Turnover before plant closure: early leavers are positively selected ("leaving the sinking ship"). No DOI on the record. |
| lengermann2002abandoning | Lengermann, P. A. and Vilhuber, L. (2002). CES Technical Paper 2002-11 | ideas.repec.org/p/cen/tpaper/2002-11.html | verified | Worker flows before displacement: higher-quality workers leave first. |
| drzensky2016hidden | Drzensky, F. and Heinz, M. (2016). Economic Journal 126(598), 2324-2341. doi:10.1111/ecoj.12216 | ideas.repec.org/a/wly/econjl/v126y2016i598p2324-2341.html; academicnewsletter.sufe.edu.cn/info/327881 | verified | In a laboratory experiment, layoffs of co-workers reduce survivors' performance substantially (43%). |
| friebel2021downsizing | Friebel, G., Heinz, M., Weller, I. and Zubanov, N. (2021). In Research in Labor Economics 49, 179-205. Emerald. doi:10.1108/S0147-912120210000049007 | econpapers.repec.org/RePEc:eme:rleczz:s0147-912120210000049007; IZA DP 9739 (econpapers) | corrected | Published version used. The 2016 IZA paper has another title and reports 6% and 21%. The chapter reports sales down 26% after closure announcements and 7% after sale announcements, in 193 bakery shops. |
| zatzick2006high | Zatzick, C. D. and Iverson, R. D. (2006). AMJ 49(5), 999-1015. doi:10.5465/AMJ.2006.22798180 | crdcn.ca/?p=20164; academicnewsletter.sufe.edu.cn/info/362160 | verified | High-involvement work practices offset the productivity loss from workforce reductions where they are kept. |
| guthrie2008dumb | Guthrie, J. P. and Datta, D. K. (2008). Organization Science 19(1), 108-123. doi:10.1287/orsc.1070.0298 | ideas.repec.org/a/inm/ororsc/v19y2008i1p108-123.html | verified | Downsizing is followed by lower profitability, more so in R&D-intensive, high-growth, low capital-intensity industries. |
| dessaint2017employment (reused from refs_acquirer.bib) | Dessaint, O., Golubov, A. and Volpin, P. (2017). Journal of Financial Economics 125(2), 369-388. doi:10.1016/j.jfineco.2017.05.005 | econpapers.repec.org/RePEc:eee:jfinec:v:125:y:2017:i:2:p:369-388; openaccess.city.ac.uk/id/eprint/16503 | verified | Difference-in-differences: major increases in employment protection reduce takeover activity by 14-27% and synergies by over half, more in deals with greater scope for workforce restructuring. Added at the acquirer section's request (29 Oct). |
| park2013turnover (reused) | Park, T.-Y. and Shaw, J. D. (2013). JAP | in refs_part2.bib | verified there | Meta-analysis: turnover rates are negatively related to organizational performance. |
| blatter2012costs | Blatter, M., Muehlemann, S. and Schenker, S. (2012). EER 56(1), 20-35. doi:10.1016/j.euroecorev.2011.08.001 | ideas.repec.org/a/eee/eecrev/v56y2012i1p20-35.html | verified | Average hiring costs of 10 to 17 weeks of wages for skilled workers (Switzerland), with marginal costs up to 24 weeks. |
| bidwell2011paying | Bidwell, M. (2011). ASQ 56(3), 369-407. doi:10.1177/0001839211433562 | repository.upenn.edu/mgmt_papers/65; wpa.wharton.upenn.edu author copy; maaw.info ASQ index (volume, issue, pages) | verified | External hires are paid about 18% more, get lower performance ratings for about two years, and have higher exit rates. |
| card2018what | Card, D., Kluve, J. and Weber, A. (2018). JEEA 16(3), 894-931. doi:10.1093/jeea/jvx028 | econpapers.repec.org/RePEc:oup:jeurec:v:16:y:2018:i:3:p:894-931 | verified | Active labor market programs: effects near zero in the short run and positive 2 to 3 years after completion, larger for training and human-capital programs. |
| katz2022why | Katz, L. F., Roth, J., Hendra, R. and Schaberg, K. (2022). JOLE 40(S1), S249-S291. doi:10.1086/717932 | econpapers.repec.org/RePEc:ucp:jlabec:doi:10.1086/717932 | verified | Sectoral programs with screening and employer links raise earnings by 12% to 34%. |

## (i) AI talent, wages and vacancies

| key | citation | URL checked | status | what it shows |
|---|---|---|---|---|
| alekseeva2021demand | Alekseeva, L., Azar, J., Giné, M., Samila, S. and Taska, B. (2021). Labour Economics 71, 102002. doi:10.1016/j.labeco.2021.102002 | ideas.repec.org/a/eee/labeco/v71y2021ics0927537121000373.html | verified | AI-skill postings offer an 11% wage premium within the firm and 5% within the job title (U.S., 2010 to 2019). |
| stephany2024what | Stephany, F. and Teutloff, O. (2024). Research Policy 53(1), 104898. doi:10.1016/j.respol.2023.104898 | econpapers.repec.org/RePEc:eee:respol:v:53:y:2024:i:1:s0048733323001828; arxiv.org/pdf/2210.01535 | verified | A 21% premium for AI skills on an online freelancing platform (49,884 projects, 2014 to 2022). |
| acemoglu2022artificial (reused) | Acemoglu, D., Autor, D., Hazell, J. and Restrepo, P. (2022). JOLE 40(S1), S293-S340 | econpapers (RePEc:ucp:jlabec:doi:10.1086/718327); academicnewsletter.sufe.edu.cn/info/276618 | verified (in refs.bib) | AI-exposed establishments cut non-AI hiring. |
| lightcast2025beyond | Lightcast, press release, 23 Jul 2025 | lightcast.io/resources/blog/beyond-the-buzz-press-release-2025-07-23 | flagged (practitioner) | A 28% salary premium for postings with AI skills, from 1.3 billion postings; method and comparison group not stated. Used only as an upper bound. |
| davis2013establishment | Davis, S. J., Faberman, R. J. and Haltiwanger, J. C. (2013). QJE 128(2), 581-622. doi:10.1093/qje/qjt002 | econpapers.repec.org/RePEc:oup:qjecon:v:128:y:2013:i:2:p:581-622; econ.umd.edu author copy | verified | Mean vacancy duration of 20 days (nonfarm); about 29 to 35 days in information, FIRE, health and education, and government; longer at large establishments. |
| dsit2025ai | Gardiner & Theobald LLP for DSIT (2025). AI Labour Market Survey 2025 | assets.publishing.service.gov.uk/media/6960ef38.../AI_Labour_Market_Survey_2025_report.pdf; gov.uk 2020 key findings | verified (self-selected survey) | 35% of organizations had a hard-to-fill AI vacancy (69% in 2020); 119 respondents of 3,940 invited (about 3%). |

## (j) Wages by country and the transfer of O*NET

| key | citation | URL checked | status | what it shows |
|---|---|---|---|---|
| oecd2025pensions | OECD (2025). Pensions at a Glance 2025, Table 7.5 | oecd-ilibrary.org/.../average-wage_da2c17cc (oecd.org version had no table) | verified | 2024 gross average wage, USD at market rates: US 70,627; DE 65,856; UK 64,379; FR 46,793; JP 34,600; PL 23,471; CN 16,955 and IN 2,959 (ILO); MX 9,657. |
| lewandowski2022technology | Lewandowski, P., Park, A., Hardy, W., Du, Y. and Wu, S. (2022). WBER 36(3), 687-708. doi:10.1093/wber/lhac005 | econpapers.repec.org/RePEc:oup:wbecrv:v:36:y:2022:i:3:p:687-708; openknowledge.worldbank.org | verified | Survey-based routine task intensity for 47 countries: substantial differences within occupations, and occupational structure explains about a fifth of cross-country variation. |
| delarica2020job | De La Rica, S., Gortazar, L. and Lewandowski, P. (2020). Labour Economics 65, 101845. doi:10.1016/j.labeco.2020.101845 | ideas.repec.org/a/eee/labeco/v65y2020ics092753712030049x.html | verified | Task prices vary across 19 countries with development and institutions (union coverage, employment protection). |
| handel2016onet | Handel, M. J. (2016). Journal for Labour Market Research 49(2), 157-176. doi:10.1007/s12651-016-0199-8 | ideas.repec.org/a/iab/iabjlr/v49i2p157-176.html | verified | O*NET's scope is impressive, but it has gaps, duplication and vague constructs. |
| bls2012isco | BLS (2012). Crosswalk between ISCO-08 and the 2010 SOC | bls.gov/soc/ISCO_SOC_Crosswalk_process.pdf | verified | One-to-many and weak matches documented; approved July 2012; maps to SOC 2010, not 2018. |
| pizzinelli2023labor | Pizzinelli, C., Panton, A. J., Mendes Tavares, M., Cazzaniga, M. and Li, L. (2023). IMF WP 2023/216 | imf.org/en/publications/wp/issues/2023/10/04/...-539656; econpapers.repec.org/RePEc:imf:imfwpa:2023/216 (number) | verified | Unadjusted AI exposure varies across countries; differences shrink after adjusting for complementarity. |

## (k) Items consulted, not in the bib

- OECD EPL France 2019 country file (t4.oecd.org/els/emp/France.pdf), used for the cross-check in labor_notes Section 5:
  - severance of 0.19, 1 and 6.87 months at 9 months, 4 years and 20 years of tenure;
  - a delay of about 37 days before notice can start in a collective dismissal.
  - The Germany file was blocked by robots.txt.
- BLS union release (18 Feb 2026), used as an engine flag: 10.0% membership and 11.2% represented in 2025.
- ETUI worker-participation.eu: bargaining coverage of about 40 to 65% in Germany and 70% or more in France.
- Grund (2003), IZA DP 875 (German severance payments) and Green (2024), OECD AI Paper 14. Consulted, not cited.

## (l) Not verified, and therefore not used as numbers in the paper

1. Trevor and Nyberg's 31% figure (press only).
2. German social-plan amounts and the typical length of works-council consultation. The OECD Germany EPL note was not reachable, so `T^proc_DE` is a scenario parameter.
3. India: the 15/26 convention for monthly-rated pay, the s.79 notice length, and state Shops and Establishments Acts.
4. UK individual statutory notice (ERA s.86); the paper assumes notice runs concurrently with consultation.
5. The Gazette text of the DPDP Rules, 2025, including the G.S.R. number. Dates come from SCC Online and practitioners.
6. The Trump v. Slaughter slip opinion (Mayer Brown summary only).
7. The official California Legislature page for Cal-WARN (FindLaw and california.public.law reproductions only).
8. The Employment Rights (Increase of Limits) Order 2026 itself (the £751 cap is from CIPP).
9. Works-council election thresholds (DE 5+, FR 11+ and 50+), used only as engine defaults and marked unverified in labor_notes.

## (m) Duplicate check

- Every key and DOI in `refs_labor.bib` was compared with `refs.bib` and every other `part2/*.bib`: accounting, competition, modern, part2, product, regimes and reliability.
- There are no DOI or title duplicates.
- One key collided: `bls2026oews` is also defined in `refs_product.bib`, for the same OEWS dataset with a different note. The labor entry was renamed `bls2026oewsdev`.
- Search for the same statutes and works under other keys (98/59, WARN, Schrems, the DPF, SCC, PIPL, DPDP, IR Code, TULRCA, ERA, JOLTS, Pensions at a Glance, Alekseeva, Stephany, Davis et al., Blatter, Bidwell, Card, Lightcast) found nothing outside `refs_labor.bib`.
