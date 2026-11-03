# Part I revision memo: Part II constraints on the Part I frontier (spec Section 22)

Date: 29 October 2026. Author: Part I integration theorist (AI), for the lead author.

Status: all deliverables done. `code/verify_theory.py` passes 159/159 checks in place (exit 0; it was 154 before the
tax and accountability-floor checks of section 25 were added). Run `code/calibrate_horizons.py` first, because sections
20 and 25 of the verifier read `notes/calibration_results.json`. A full-paper scratch build (Part I plus Part II core,
ext, regimes, product and accounting sections and proofs, all Part II bibliographies) compiles to 202 pages with no
errors, no undefined references or citations, and no multiply defined labels. The only overfull boxes are the notation
table in model.tex (31 pt, present before this revision) and two long bibliography URLs (Svanberg, SEC FAQ), which
`\usepackage{xurl}` in paper.tex would fix.

Every number below is under our scenario assumptions. The compute share c_c is a scenario value with no measured analog;
the full-cost floors rest partly on scenario (class d) values; output prices are held fixed. Horizon ranges are scenario
bounds, not forecasts.

## 1. Headline numbers, old and new

### 1.1 Full-automation ceiling (Corollary cor:ceiling, Table tab:ceiling, equation eq:Rmax)

Conditions for every row: Rule of 40 (X = 1), after-tax FCF after SBC, saturated share, no growth spend, prices fixed,
k = 0 for the thresholds, psi = 0 and delta_K = 0 in the table. Case values (c_c, f, a_min, tau, c_full):
favorable (0.15, 0.02, 0.015, 0.15, 1.6 points), central (0.20, 0.025, 0.03, 0.18, 4.1), conservative (0.25, 0.03,
0.046, 0.21, 11.0), high compute (0.40, 0.025, 0.03, 0.18, 4.7). c_c and the class d parts of c_full are scenario values.

| Quantity | Old (accountability costs only, a_min conservative 6%) | New (full cost, a_min conservative 4.6%) |
|---|---|---|
| Market growth needed for R_max = 100, central | 39% | 42% (42.3) |
| favorable | 31% | 32% (32.1) |
| conservative | 48% | 55% (55.4) |
| high compute | 55% | 59% (59.2) |
| Same, accountability costs only, new a_min band | n/a | 39, 31, 47, 55% (48% with a 6% floor) |
| Margin term (ceiling at G = 0), central / fav / cons / high compute | 61.1 / 69.3 / 52.1 / 44.7 | 57.7 / 67.9 / 44.6 / 40.8 |
| Central ceiling at G = 5, 15, 30% (k = 0) | 66, 76, 91 | 63, 73, 88 |
| Favorable | 74, 84, 99 | 73, 83, 98 |
| Conservative | 57, 67, 82 | 50, 60, 75 |
| High compute | 50, 60, 75 | 46, 56, 71 |

Sensitivities of the central threshold (full cost; accountability-only in brackets):
- c_c over its credible bounds [0.01, 0.55]: 26 to 72% (23 to 68%). Condition: all other central values. This is the
  dominant uncertainty; the wording in the text is "if compute absorbs 20% of revenue at full automation, a scenario
  value".
- tau: 40 to 44% over 15 to 21% (the 15% CAMT to the 21% federal rate, 26 U.S.C. 11(b), state taxes excluded); 36% at
  tau = 9% (32%), the low end of the GAO-23-105384 effective-rate range of 9 to 16%.
- a_min over its band [0.005, 0.046]: 40 to 44%. The central 3% equals the p10 G&A share of firms above $10 billion, so
  it assumes no G&A automation at the leanest large firms.
- c_err from its favorable (0.18 points) to its conservative value (3.75): 41 to 44%; with today's highest measured
  error rates and losses equal to the in-house cost of the work (7.8 points), 48%.
- Capital: k = 1.5 lowers the ceiling at G = 30% by 45 points if the capital is not deductible (psi = 0), by 36 to 38
  points if it is deducted when incurred (psi = 1, current law for domestic development and 100%-allowance equipment),
  and by 40 to 41 points for development abroad (psi_15 = 0.53). Replacement at delta_K = 0.25 with k = 0.5 subtracts a
  further 10.25 points (central).
- Owning compute (Remark rem:owncompute): raises the cash ceiling only if the vendor markup exceeds 3.3G/(1 - tau):
  20% at G = 5% and 60% at G = 15% (tau = 0.18, servers 60% of compute cost, 5.5-year life).

Unchanged: Rule of 1000 needs lambda h of 6.8 to 9.3 (alpha 0.45 to 0.25), 7 to 19 times the pull implied by today's
best firms; the duration bound (1 year from 1% share, 5 from 0.001%); free entry gives 7.5 points and needs a rent of
about 92 points for a score of 100.

### 1.2 Full-cost floors (Definition def:fullcost, Appendix Remark rem:fullcost-values, Table tab:fullcost)

c_full = 1.57 / 4.09 / 10.95 points (favorable / central / conservative), 4.69 in the high-compute case:
c_sec 1.00 / 1.57 / 2.78 (risk cost by Prop. tasks-security(b) from security spend of 0.69% of revenue, PQC 0.04 / 0.10
/ 0.24 scaled by IT spend, AI compliance 0.10 / 0.20 / 0.40); c_mnt 0.15 / 0.60 / 2.89; c_err 0.18 / 1.30 / 3.75
(errors and hallucination, misbehavior, provider common mode, Prop. tasks-cerr, tasks-autonomy(a), ext-commonmode(a));
c_anc 0.23 / 0.61 / 1.52. Conditions: fixed costs at $1 billion of revenue (they fall with scale); conservative error
rates held at today's central rates (scope test, Prop. tasks-halluc(b)); class d composites halved and doubled. Each cost
counted once: injected-instruction and attacker losses in c_sec; operational losses that survive review in c_err;
review and sign-off floors and expected misstatement losses of financial controls in a_min (Prop. acct-amin); upkeep and
revalidation of builds in c_mnt; one-time costs in the transition, not the ceiling.

### 1.3 Horizons (Table tab:calib, Section sec:horizons)

Conditions: X = 1, FCF after SBC, alpha in [0.25, 0.45], G and pull mu as before, intercept now moving from the anchor
quartiles (35, 50) toward the central and favorable full-cost margin terms (58, 68) at the pace of Prop. expected(c);
low ends pair central execution with the central term, high ends fast execution with the favorable term; k = 0 unless
stated; capital not deductible (psi = 0) in the table.

| Range | Old | New |
|---|---|---|
| Upper bound on growth spend, maximal score 2028 / 2031 / 2036 | 50-145 / 53-122 / 55-126 | 46-138 / 45-120 / 45-125 |
| of which durable | 50-82 / 53-85 / 55-99 | 46-75 / 45-83 / 45-98 |
| k = 0.5, capital not deductible | 45-90 / 49-87 / 53-94 | 41-83 / 41-85 / 43-92 |
| k = 0.5, capital deducted when incurred (psi = 1) | n/a | 42-91 / 42-90 / 43-98 |
| Lower bound on growth spend, maximal score | 49-162 / 45-125 / 42-123 | 45-156 / 37-123 / 32-122 |
| of which durable | 32-64 / 35-67 / 37-81 | 28-57 / 28-65 / 28-80 |
| Combined, as quoted in the introduction | roughly 50-160 / 45-125 / 42-126; durable about 32-82 / 35-85 / 37-99 | roughly 45-156 / 37-123 / 32-125; durable about 28-75 / 28-83 / 28-98 |
| Dip of a firm still transforming | none | 3.5 to 4 points while the program runs |

Pace (Prop. attainable, Prop. expected): central execution (change capacity 10% of employees a year, success 0.54,
q = 0.34) embeds 2.5%, 10% and 23% of the program by 2028, 2031 and 2036 (3.0% a year); fast execution (20%, 0.80,
q = 0.74) embeds 30%, 73% and all of it, completing in 2033 (14.5% a year). Change capacity binds in both. Under central
execution embedded gains first exceed the dip after about ten years. Variants: a public firm holding a guided dip of one
point embeds 8% by 2036 instead of 23% (intercept +2 points instead of +5); two points gives 16%; a sponsor's faster
decisions change nothing here (change capacity binds); slow execution embeds less than 1% by 2036. Survey rates, the
capacity range and turnover and reorganization rates are sourced or grounded by precedent; program size, embedding times,
realized shares, keep and strategy-change rates and transition costs are scenario values.

Anchor (unchanged method, firm-by-firm inversion, 15 firm-years): median top-tail intercept 42 points (IQR 35 to 50)
under the upper bound on growth spend, 24 under the lower; durable score 54; surplus 7 (-10 to 18) or 25 (17 to 28).
The gap to the central margin term is now 16 points (58) and to the favorable 26 (68); it was 19 (61) and 27 (69).
With current-law deductions for capital each anchor intercept would be lower by tau k g, less than one point at the
quartiles (35.2, 42.0, 49.9 become 34.7, 41.6, 49.2).

## 2. Coordinator inputs addressed

- c_err (spec 23): built from params_reliability.yaml rates times labeled loss ranges; distinct from c_sec; thresholds
  reported across its range (Section 1.1).
- Common-mode cost (prop:ext-commonmode) folded into c_err as a separate row; no overlap with eq:tasks-cerr, which covers
  independent failures.
- Generalization (spec 24.3): Prop. prop:general, about one page.
- Modern theory: PQC as a labeled range scaled by IT spend (only public-sector estimates exist, omb2024report; windows
  from moody2026transition); Marris, Solow and Odagiri paired with fitzgerald2024how, argente2025how and
  afrouzi2023concentration; duration with weber2018cash and gormsen2023duration.
- Assumptions auditor: c_c scenario-only with bounds; a_min band [0.005, 0.046], conservative capped at 4.6%; tau
  grounded; "under our scenario assumptions" on horizon statements; this memo gives conditions with each number.
- psi (accounting agent): Part I did not use the 2022-2024 five-year regime. It used psi = 0 (no deduction) as the
  table convention. Remark rem:taxes now gives the current-law split with citations to part2/refs_accounting.bib:
  psi = 1 for domestic development (usc2026sec174a) and equipment with the 100% allowance (irs2026notice202611),
  psi_15 = 0.53 for foreign development (usc2026sec174), psi = 0 for working capital, psi_5 = 0.80 for 2022-2024.
  The table keeps psi = 0 as a lower bound that fits working capital; the text reports the psi = 1 and psi_15 variants.
  The k = 0 thresholds do not depend on psi.
- a_min (prop:acct-amin): used to ground the band. In the illustrative example at $1 billion of revenue, the best
  control design adds 0.10% of revenue (about 0.11% with twice the opportunities or twice the common-mode rate), and
  the all-AI common-mode floor of 0.12% does not fall with scale. With direct audit and 404 costs of about 0.14% the
  floor is about 0.25%, below the band's lower end of 0.5%, so the band stands. Misstatement losses are in a_min only,
  not in c_err or its common-mode term.

## 3. New results and labels (main text, model.tex)

def:fullcost; cor:ceiling (revised) with eq:Rmax and tab:ceiling; subsection sec:model-attainable with ass:program,
def:attainable, prop:attainable, prop:expected, rem:regimes; subsection sec:model-general with prop:general. Notation
table rows for c_mnt, c_sec, c_err, c_anc, A_t, R^att_X, e, ROIC, R-bar_X, q. Appendix (appendix_proofs.tex):
rem:fullcost-values, tab:fullcost, rem:owncompute, lem:expected-frontier, and proofs of cor:ceiling, prop:attainable,
prop:expected, lem:expected-frontier, rem:regimes, prop:general, rem:owncompute. Main-text growth of the model section
is about 5 pages, of which about 1 is the generalization the coordinator added.

## 4. What the lead author must change outside my files

Abstract: "unless its market grows faster than about 39% a year in a central case" becomes "unless its market grows
faster than about 42% a year in a central scenario in which compute absorbs 20% of revenue (26 to 72% over the credible
range of that share)". Suggested addition: "and how fast a firm approaches that limit is set by its capacity to execute
risky transitions."

Introduction, paragraph beginning "Combining model and estimates": "net of compute costs, fees and an accountability
floor" becomes "net of compute costs, fees, an accountability floor and the recurring costs of maintaining, securing and
supervising AI"; "66 to 91 points" becomes "63 to 88 points"; "39%" becomes "42%"; "(31% with favorable parameters,
55% if compute ...)" becomes "(32% with favorable parameters, 59% if compute stays as costly as projected for AI products
in 2027; every threshold is conditional on a scenario compute share)"; horizon ranges become "roughly 45 to 156 in 2028,
37 to 123 in 2031 and 32 to 125 in 2036, of which about 28 to 75, 28 to 83 and 28 to 98 points would be durable".
Suggested new sentence: "The pace is limited by execution: under central execution an exceptional firm embeds about a
quarter of its automation program by 2036, under fast execution all of it by 2033 (Propositions attainable and
expected)." The contributions paragraph could add the attainable frontier and the value-based generalization
(prop:general: the Rule of X is a rule of economic profit).

Conclusion, second paragraph: after "it adds computing cost" add "and the recurring costs of maintaining, securing and
supervising AI"; add "and capacity to execute risky transitions limits how fast a firm gets there". Third paragraph:
add the full-cost floors and execution capacity to the list of parameters by which to evaluate AI strategies; the
"supplement the score with economic profit" sentence can cite prop:general.

Discussion, accountability paragraph: "1.5%, 3% and 6%" becomes "1.5%, 3% and 4.6%"; replace "the central value is
close to the total general and administrative expense of the leanest large software firms today" with "the central value
equals the tenth-percentile general and administrative share of firms above $10 billion, so it assumes none of that
expense is automated"; add that Proposition acct-amin gives the floor as a minimum over control designs whose
common-mode misstatement term does not vanish under AI. From the accounting notes (items 7 and 8): note that emerging
growth companies are exempt from 404(b) and a newly public company's first annual report has no assessment; and that for
a growing program capitalization biases the GAAP score upward permanently (prop:acct-program).

paper.tex: Part I now cites Part II labels (sec:tasks, sec:ext, sec:regimes, sec:tasks-ancillary, ass:tasks-ancillary,
prop:tasks-*, prop:ext-*, cor:ext-floor, lem:ext-staffing, prop:reg-*, prop:prod-*, prop:acct-tax, prop:acct-amin,
eq:tasks-cerr, eq:tasks-success, eq:acct-amin). The current paper.tex, which inputs no Part II files and has
`\bibliography{refs}`, therefore shows undefined references and citations until the Part II sections (including
theory_accounting.tex) are input and the bibliography line includes at least part2/refs_part2, part2/refs_modern and
part2/refs_accounting (the scratch build used refs, refs_part2, refs_modern, refs_reliability, refs_product,
refs_competition, refs_accounting).

## 5. Files touched

sections/model.tex; sections/appendix_proofs.tex; sections/horizons.tex; sections/tables/tab_calib.tex (regenerated);
code/verify_theory.py; code/calibrate_horizons.py; notes/calibration_results.json (regenerated, new blocks pace,
variants, cc_sensitivity, tau_sensitivity, cerr_sensitivity, amin_sensitivity, psi_sensitivity, previous); this memo.
