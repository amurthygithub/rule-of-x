# Acquirer section: notes for the engine, the other owners and the lead

Owner: corporate-finance and IO theorist (acquirer section). Written 29 October 2026.
Question answered: "One take-private-and-transform use case to keep in mind would be Bending Spoons and its IPO. What lessons are to be learned from an AI transformation perspective, and how does it inform/update the models?"

## 1. Files and labels

| file | paper | contents |
|---|---|---|
| part2/theory_acquirer.tex | 2 | `sec:acquirer`; subsections `sec:acq-owner`, `sec:acq-replace`, `sec:acq-pc`, `sec:acq-retention`, `sec:acq-limits`, `sec:acq-case`; `ass:acq-owner`, `ass:acq-replace`, `ass:acq-pc`, `ass:acq-limits`; `prop:acq-owner`, `prop:acq-replace`, `prop:acq-pc`, `prop:acq-retention`, `prop:acq-limits`; `eq:acq-Wo`, `eq:acq-channels`, `eq:acq-pmax`, `eq:acq-replace`, `eq:acq-method`, `eq:acq-pmaxbound`, `eq:acq-reprice`; `tab:acq-case`, `tab:acq-levers` |
| part2/proofs_acquirer.tex | 2 | `app:proofs-acquirer`: proofs of the five propositions |
| sections/measurement_acquired.tex | 1 | `sec:acquired-growth`; `def:acquired-growth`, `prop:acquired-score` (a)-(f), `eq:acquired-Rstar`, `rem:acquired-bounds`, `eq:acquired-bounds`, `tab:acquired-score`. Uses Part I labels only; the companion paper is mentioned in words, with no `\ref` |
| sections/appendix_proofs_acquired.tex | 1 | `app:proofs-acquired`: proof of `prop:acquired-score` and of the inequalities in `rem:acquired-bounds` |
| code/verify_part2_acquirer.py | both | 63 checks (all pass, about 5 s). Reads the F-1 extract, `data/examples/invoice_chain.json`, `sections/data.tex`, `sections/empirics.tex` and `paper1/macros.tex` at run time. Writes `part2/tables/acquirer_macros.tex` (all macros) and `sections/tables/acquired_macros.tex` (those Paper 1 uses) |
| part2/refs_acquirer.bib | both | 56 entries; audit trail in notes/ref_verification_acquirer.md |

Every F-1 figure in the four .tex files comes through an `\acq...` macro; check G3 fails if one is typed. Check G5 fails if the Paper 1 files reference a label outside `sections/`. Check E9 parses Part I's acquisition flag from `sections/data.tex` (expanding `paper1/macros.tex` first), so it fails loudly if that sentence changes form.

## 2. Notation added (checked against all Part I and Part II files for clashes)

- Owner capability: `u_F`, `N_pl`, `\mathbb 1^{reb}`, `\varpi^o`, `T^o_h`, `N^core`, `s^tech`, `n^core_i`; costs `F^bi`, `F^rd`, `F^o`, `C^pool`, `C^spec`, `C^risk`, `C^run`, `W^0`, `W^o`; learning `\epsilon_L`.
- Replacement: `\mathsf d^{rpl}`, `t^rpl`, `T^bld` (labor's meaning), `T^leg_c`, `C^ctx`, `C^cu`, `T^cu`, `n_fin`, `L^rpl_fail`, `\varpi^rpl`, `\mathcal G^spd`, `\Delta\mathcal C`.
- Permanent capital (regime `pc`): IRR is fraktur `\mathfrak i` (rho is the rent), `\mathfrak i^m`, `\mathfrak i^\infty`, `\bar{\mathfrak i}_U`, `\bar{\mathfrak i}_L`, `r_tv`, `T^IRR`, `T^rep`, `\overline{LTV}` (upright), `ND^rep`, `r_debt`, `\overline{lev}^pc`, `V^tv`, `P^max`.
- Retention: NRR (upright), `\mathsf S_sw`, `\upsilon_rp`, `\nu^rv`, `g^in`, `Sh(\tau)`.
- Limits: `nd` (upright, net debt per dollar of revenue), `n^dl`, `S^tg`, `\mathsf h` (hurdle headroom; `\mathcal H` is the core's AI capability), `\epsilon_sz`, `p^ch`, `L^ch`, `p^fdi`, `T^fdi`, `\upsilon^cp`, `h^cp`.
- Paper 1: `g^org`, `g^acq`, `k^acq`, `c_fin`, `S^cn`, `S^ac`, `C^acq`, `m^cf`, `CRF`, `T^life` (`L` is Part I's markup and `\ell` its demand pull, so neither is used).

## 3. Engine formulas

Rates are continuous (`ln(1+r)`), as everywhere else.

1. **Owner NPV (eq:acq-channels).** `NPV^o - NPV = (F - F^o) + b_bar (varpi^o W^o S^o_r - varpi W S_r) - e^{-r T_par} (varpi^o - varpi)[(1 - p_u) C_str - p_u L_roll]`, with `F^o = (1 - u_F) F^bi i^{-eps_L} + F^rd` and
   `W^o = W^0 - [C^pool + 1^reb C^spec + C^risk(N_pl C^inc)]/N_pl - (1 - 1^reb) C^spec` (eq:acq-Wo).
   Floor: `NPV^o` at `F^o = F^rd`, `W^o = W^0`. Break-evens solve for one lever at a time with the others at their best (as in the script's B checks).
2. **Maximum premium (eq:acq-pmax).** `p^max_o = p^max_pe + Delta V^cap_o / P_0`, with `Delta V^cap_o = V^prog(Pi^o; U_o) - V^prog(Pi^pe; U_i)`.
3. **Replace or transform in place (eq:acq-replace).** Replace iff `G^spd > Delta C`;
   `G^spd = (W/r) sum_k n_k (e^{-r t^rpl} - e^{-r t_k})`, `t^rpl = max{T^bld, max_c T^leg_c}`;
   `Delta C = Delta C^sev + C^ctx + C^cu + Delta C^mw + S Delta a_min / r + (1 - varpi^rpl) e^{-r t^rpl} L^rpl_fail + Delta F - Delta C^par`;
   `C^ctx = L^ctx (1 - kappa_doc) d^rpl e^{-r t^rpl}/(r + eta_K)`, `C^cu = X^o S (1 - e^{-delta^G T^cu}) e^{-r t^rpl}`.
   Bunching crossover: `P_mw(n) > 1 - [1 - n P_mw(1)]^{1/n}`.
4. **Permanent capital.** Method IRR solves `P = int_0^T e^{-i t} FCF dt + e^{-i T} TV`, `TV = int_T^inf e^{-r_tv (t - T)} FCF dt`; permanent IRR without TV. `e^{-(i_bar - r_tv) T} V^tv <= P^max <= V^tv`. Debt `ND_0 = min{LTV P, ND^rep}`, `ND^rep = int_0^{T_rep} e^{-r_debt t} FCF dt`, cash sweep; at the repayment cap with `T_rep = T_IRR`, `i_L = ln[TV/(P - ND^rep)]/T`. Weight `X^G = m_hat/(i_bar_U - G_i)`.
5. **Retention.** Retained revenue `(1 + upsilon) S_sw(upsilon)`; optimum `S_sw = -(1 + upsilon) S_sw'`, `x_bar - 1` with exponential ratios. `Sh(tau) = e^{-(nu + g_in) tau}`; mean tenure `1/(nu + g_in)`; heterogeneity test `Sh(2 tau) > Sh(tau)^2`.
6. **Limits (prop:acq-limits).** `g^max = (m - r_debt nd + k^acq g^org)/(k^acq - nd)`; holding growth g needs acquired growth `g + d^org` with `d^org = -g^org` (round 2, F21); without new customers `g^org = G_i = ln[1 + s_sub (NRR - 1) + (1 - s_sub) gamma_ns]` (`ln NRR` only if all revenue is subscription); standing still needs `-G_i`. `S^max = n^dl S^tg_max/(g - g^org)`, `S^tg_max = S^tg_0 h_0^{1/eps_sz}`. Series review: deal n proceeds iff `V_n - P_n >= p^ch(n Delta s) L^ch`. FDI multiplier `1 - p^fdi (1 - e^{-r T^fdi})`. Consumer law: retained `(1 + upsilon) S_sw(upsilon/h^cp)`, optimum `min{(h^cp x_bar - 1)^+, upsilon^cp}`.
7. **Paper 1 score (prop:acquired-score, rem:acquired-bounds).** `R^A_X = X g + m - k^acq g^acq = R^org_X + (X - k^acq) g^acq`; `R^{A*}_X = R*_X + (X - k^acq)^+ a_bar`. Bounds: fully charged `g + m^cf - C^acq_t/S_t` <= annuity `g + m^cf - CRF(r, T^life) sum_{t - T^life < v <= t} C^acq_v/S_t` <= uncharged `g + m^cf`, `CRF = r/(1 - e^{-r T^life})`, `T^life = -1/ln NRR` (scenario). Round 2 (IB-4): `m^cf` is BEFORE financing, `(OCF + (1 - tau) interest paid)/S`, because OCF is after interest paid under U.S. GAAP; a cost-of-capital charge against OCF as reported double-charges by `(1 - tau) c_fin`. Second charge: user cost `(r + d) K^d`, `K^d = sum_v C_v e^{-d (t - v)}`, `d = -ln NRR`; both charges on year-end or time-weighted capital. See notes/acquirer_fixes_v2.md.

## 4. Worked numbers (all recomputed by the script; F-1 figures from the extract)

- Scores, 2024 / 2025 (points): GAAP 92.3 / 115.9; after interest 87.5 / 105.0; operating cash flow 103.9 / 116.9; annuity 80.9-86.8 / 84.4-92.8 (r = 8.93%, T^life 10.6-19.5 years from NRR 91-95%, CRF 14.6-10.8%); fully charged -28.7 / -24.8 (net investing outflow 132.6% / 141.8% of revenue).
- Part I's flag: outflows 2.3 and 2.8 times prior-year revenue; flagged unless under 11% / 9% of them paid for acquisitions; Q1 2026 capital deployed 1.5 times 2025 revenue. At the 25% threshold the full-charge correction is at least 25/(1+g) points (17 at 50% growth), the order of the 10-26 point fall in the 95th percentile.
- Treadmill: standing still needs 5.1-9.4% of revenue acquired a year ($67-123M of run-rate at 2025 revenue; 6.0-11.1% of revenue in cash at Brightcove's reported 1.2 times revenue). Self-financing growth without debt 5-20% (scenario grid) against 94.7% actual; 2025 financing inflow $1,935.9M, 148% of revenue.
- Permanent capital on the regimes take-private firm: method IRR 10.1% unlevered (10.6% annual), 10.4% levered; hurdle 22.3% continuous; P^max 10.6 times EBITDA (54% of V^tv; bound 0.51) or a 106% uplift against 30%.
- Invoice chain (core example, values follow the JSON): standalone NPV and floors negative; flips only with success above 0.79, 13 businesses on the platform, reuse 0.89 or a 15-year horizon (other levers at best).

## 5. Grounding classes

- (a) Disclosed in the F-1 extract: hurdles 65% / 25%, the 5-year IRR window, LTV 85%, 5-year repayment, covenant 4.00 and actual 2.24 / 2.19, NRR by year and business, tenure shares and mean, the Spooner counts, all financial statements.
- (b) Sourced presets from other sections or practitioner data: r_w = r_tv = 9.34% annual (damodaran2026cost), severance months and legal leads (labor section, params.yaml), accounting cutover values, the regimes take-private firm and the PE 22% survey hurdle.
- (c) Derived from the F-1 by the model: tenure-implied hazards (0.125-0.147), NRR-implied decay (0.051-0.094), T^life, implied inflow growth, the flag ratios.
- (d) Scenario values, not grounded: u_F, N_pl, eps_L, delta^G, r_debt (8% regimes preset), f1 grid (0.3-0.5), m grid (0.2-0.3), k^acq up to 2, eps_sz, h_0, n^dl, p^ch, L^ch, p^fdi, T^fdi, h^cp, upsilon^cp. The literature signs eps_sz (Fuller 2002; Renneboog and Vansteenkiste 2019; Billett and Qian 2008; Aktas et al. 2009; Karolyi et al. forthcoming) but does not size it.

## 6. Secondary sources

See notes/ref_verification_acquirer.md (56 entries; 44 verified, 3 corrected, 9 flagged). Corrections to the extract: Evernote ("most" staff, not all); Komoot (up to 85% reported, not about three quarters); Harvest (BBC via Subscription Insider, not Bloomberg); IPO ($1.68B total, about $1.0B to the company; first day +39.7%, QuotedData); AOL's NRR average includes pre-ownership quarters (closed 2 Jan 2026). Caught errors used only as such: KuCoin's $13.1B revenue, IPOScoop's trailing net loss. No public record of an agency challenge to any Bending Spoons deal was found. An F-1/A exists on EDGAR (accession 000110465926076487) and was not read.

## 7. Change requests (I have not edited these files)

- **Regimes owner (theory_regimes.tex):** add a `pc` row to `tab:reg-presets` (T = infinity, hurdles 25% / 65% continuous 22.3% / 50.1%, LTV 85%, repayment 5 years, covenant 4.0); note that `prop:reg-lbo` gives the buyer the target's capability, and refer to `eq:acq-pmax`. The symbol vartheta is used for altruism in theory_ext.tex and for myopia in theory_regimes.tex; one should change.
- **Core owner (theory_core.tex):** state that the invoice example is a standalone firm (its sign can flip under an owner's platform, `prop:acq-owner`). The JSON changed three times during this session; my checks are now qualitative so that they survive changes, but please announce changes to the example.
- **Ext owner (theory_ext.tex):** K_chg and team experience can be supplied by an owner (`ass:acq-owner`(iii)); index readiness and success by owner where an owner is named.
- **Labor owner (theory_labor.tex):** cite dessaint2017employment (employment protection cuts takeovers 14-27% and synergies by over half) for the cost of the replacement path.
- **Accounting owner (theory_accounting.tex):** the bunching result `prop:acq-replace`(d) (no extra risk without congestion) uses your P_mw; please confirm the reading. The SEC's relief for acquired businesses in the first year of ICFR (sec2007faq) is relevant to the replace path.
- **Product owner (theory_product.tex):** treat switching costs as a distribution (`prop:acq-retention`(a)); one ratio cannot produce retention strictly between zero and one after a large repricing.
- **Paper 1 integration (sections/, paper1/):** input `sections/measurement_acquired.tex` after horizons and `sections/appendix_proofs_acquired.tex` in the appendix (the horizons and appendix_proofs files already reference them conditionally). Paper 1's bibliography needs bendingspoons2026f1, dealroom2026ipo, fuller2002what, golubov2015extraordinary, laamanen2008performance, fasb2026asc35020 and ifrs2022goodwill (refs_acquirer.bib) and damodaran2026cost (refs_regimes.bib). If the flag sentence in data.tex is reworded, check E9 will fail; tell me and I will adjust the parser. The build currently warns that murthy2026transformation has no bib entry.
- **Engine builder:** implement the formulas in section 3; add a `permanent_capital` block to params.yaml (horizon, hurdles, LTV, repayment years, covenant, r_tv link to public.r_own_wacc, r_debt link to the regimes debt preset) and a `limits` block (nd, n_dl, eps_sz, h_0, p_ch function, L_ch, p_fdi, T_fdi, h_cp, upsilon_cp), all marked scenario except the F-1 values.
- **Lead:** record in the protocol log the extract errors found (section 6) and the stale-scratch-directory problem (stale copies of sections in a reused build directory made pdflatex read old files; fixed by building in a fresh directory).

## 8. F-1 sections needed (verbatim, from the browser)

1. Acquisitions note: dates, consideration, purchase price allocation (goodwill and intangibles by class and life), acquired revenue and earnings since acquisition, ASC 805 pro forma revenue.
2. Pro forma financial statements (AOL, Eventbrite, Vimeo).
3. Revenue by business or segment, and the subscription share.
4. Cash-flow detail: capital expenditure, capitalized software, acquisitions net of cash acquired, interest paid and its classification, SBC; the definition of "capital deployed in acquisitions".
5. Basis of preparation (U.S. GAAP or IFRS) and depreciation and amortization, separating acquired intangibles.
6. Restructuring note (costs, headcount, by year).
7. Material-weakness description and remediation.
8. Debt note: rates, maturities, covenant and leverage-ratio definitions, the $2.8B package.
9. Headcount by year and country, including acquired-business FTE.
10. NRR definition and treatment of acquired businesses (pre-ownership quarters).
11. Exact hurdle wording (minimum or projected IRR), the WACC used for terminal values, the EV/EBITDA multiple, and the passage reported to say that hurdles may fall with scale.
12. Pricing, ARPU and paying customers; the unions sentence in full.
13. Composition of other expense (income) and of the 2025 tax charge; the nature of the Q1 2026 restatement; dual-class voting power.
14. The "primarily driven by new acquisitions" passage in context.
15. Risk factors on antitrust and merger control, foreign-investment review (any CFIUS filing for AOL, any Treasury contact on Eventbrite, Italy's Golden Power), and consumer and subscription law.

## 9. Update of 29 October 2026 (424B4, post-IPO 6-Ks, accounting correction, myopia symbol)

- **Sources added:** bendingspoons2026prospectus (424B4, 1 Jul 2026; non-GAAP reconciliation, Article 11 pro forma) and bendingspoons2026sixk (6-K exhibits, Aug to Oct 2026). Every F-1 figure used is unchanged in the 424B4 (check A9 ties the non-GAAP table to the F-1 operating income). New checks: A9-A13 (filings), C7-C8 (date channel, reorganization calibration), D10 (prices against the grid), E11 (net weight at the 424B4 prices). 72 checks pass.
- **Paper 1:** Q2 2026 reported score about 160 against an organic score of about 37 on the company's 3% organic growth (its definition, one quarter); gap 123 points = acquired growth credited without its price. Score on the company's adjusted margin 141.6 (2025); amortization of acquired intangibles 12.8% / 11.5% of revenue (2024 / 2025). Pro forma 2025 revenue $2,608.5M, 2.0 times actual (flag threshold 10%). Prices 1.7-3.2 times revenue: the full charge loses 0.7-2.2 points per point of acquired growth, the annuity charges 0.19-0.47 (sign set by the convention). Vimeo: closed 24 Nov 2025 for $1,359M, 327 days of its 2025 revenue ($376.9M) before the close.
- **Replace path:** (iv) and (d) corrected per accounting notes 4.8: P_mw(H; n) with congestion in p_def, T_dc, T_rem; condition P_mw(1 - z^rpl; n) > 1 - [1 - n P_mw(1 - T_cl; 1)]^{1/n} (eq:acq-mw); cost per year with a weakness (Item 308(a)(3)) and the per-weakness alternative; 2.37% after a close, 9.0% with half a year or less to go, 31.4% for four bunched late against 9.5% spread; date threshold z = 0.176 (3 days after the earliest open date); congestion threshold 4% of its value (2.37% to 2.46%); correlated deficiencies through shared ITGCs; SEC staff one-year exclusion (sec2007faq, Q3). Calibration: reorganization expense 6.0% of revenue (2025), 12.6% (Q1 2026), $51M (7.2%) in Q2 2026; scaled to the $500M example at least $30.1M, 3.6 times the U.S. speed gain.
- **Permanent capital:** r_debt = ln(1.09625) = 9.19% (coupon of the first USD secured notes, 28 Oct 2026; EUR 8.625%), grounding a; the sponsor reproduction keeps the regimes 8% preset. Changed: levered IRR at the take-private price 10.4% -> 10.2%; levered IRR at P^max on the grid 36-43% -> 34-42%; unlevered IRR implied by the levered hurdle 30% -> 30-31%. Leverage 2.4x at mid-2026 on an EBITDA with expected cost savings (flagged). Eventbrite (1.7x) lies inside the grid's admissible prices (max 1.82x), AOL (2.3x) and Vimeo (3.2x) above it; AOL's own 2025 operating margin was 53%.
- **Limits:** standing still costs 8.9-30.5% of revenue a year at the 424B4 multiples (was 6.0-11.1% at Brightcove's reported 1.2x); self-financed growth without debt 1-12% (was 5-20%). Larger targets after the IPO: Tractive EV $759M (Wikipedia's $900M is wrong), Airtable EV $1.285B, Miro EV $1.355B.
- **Myopia symbol:** vartheta_pc, vartheta_dc renamed mathfrak w_pc, mathfrak w_dc (ass:acq-pc(iv), tab:acq-levers); none in the proofs or the script.
- **Script change:** the Paper 1 macro file now covers every \acq macro used anywhere in sections/ and paper1/ (the integrator quotes them in intro.tex and discussion.tex); G4 checks all of them. Negative values now print with \ensuremath{-}.
- **Change requests:** Paper 1 integrator: add bendingspoons2026prospectus and bendingspoons2026sixk to paper1/refs_paper1.bib (Paper 1 compiles standalone with only these two missing). Regimes owner: the pc row's debt rate can now cite the 6-K (grounding F/K rather than A). The combined build still lacks a bib entry for murthy2026transformation.
- **F-1 sections now answered:** basis of the non-GAAP add-backs, the pro forma, three purchase prices, debt terms (partly), the leverage definition. Still needed: interest paid classification, capex and capitalized software, acquisitions net of cash by year, revenue by business, NRR treatment of acquired businesses, the hurdle wording and "hurdles fall with scale", the risk factors on antitrust, foreign-investment review and consumer law. (Resolved: the 6-K's $1.10B net IPO proceeds fit the over-allotment option on 5,244,026 company shares, estimated net $1,079M with full exercise; about $21M remains unexplained and is not used.)

## 10. Update of 29 October 2026, round 2 (review fixes)

The round-1 review fixes (IB-4, RA-4, Fable F21, the withdrawn growth weight) are documented in notes/acquirer_fixes_v2.md: each change old to new with its filing citation, the recomputed numbers, the XBOUNDS placeholders, the engine changes needed and what could not be verified. Script: 80 checks (A14-A16, E12-E15 and H6 new; C4, E4, E10 and F6 revised). The extract has a new section "Round-2 additions" with the Q2 2026 6-K tables (Ex. 99.1 and 99.2) read on sec.gov.
