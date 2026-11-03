# Labor law, talent and jurisdiction (spec 24.5 and 24.6): notes for the engine and the lead author

Status on 29 October 2026. Deliverables:
- `part2/theory_labor.tex` (Section `sec:labor`, about 6 pages in the test build);
- `part2/proofs_labor.tex` (Appendix `app:proofs-labor`);
- `code/verify_part2_labor.py` (43/43 PASS);
- `part2/refs_labor.bib` (58 entries);
- this file;
- `notes/ref_verification_labor.md`.

The rules below are model constraints, as they stood at their primary sources on 29 October 2026. They are not legal advice. Every statutory number in this file was read at the source logged in `notes/ref_verification_labor.md`, unless it is marked **unverified**. The calculators in Section L0 of the verify script follow Section 3.1 line for line.

The test build ran in the session scratchpad: `theory_core` + `theory_ext` + `theory_labor` + `proofs_labor`, with `refs`, `refs_part2`, `refs_modern`, `refs_reliability` and `refs_labor`, under plainnat. It produced 0 LaTeX errors and no undefined citations. The only undefined references are the Part I labels that live outside the harness.

## 1. Results and labels

| label | content | verify checks |
|---|---|---|
| `ass:labor-proc`, `tab:labor-rules` | jurisdictions, establishments, collective-procedure triggers, legal lead `T^leg = T^proc + T^not`, technology consultation `T^tech`; the table of rules for U.S. federal, CA/NY/NJ, EU minimum, DE, FR, UK and IN | L0a to L0g |
| `prop:labor-lead` | (a) cutover `t^dis = max{t^gate, t^A + T^leg}`; (b) cutover streams are intervals in `t^dis` order, and a split pays iff the forgone saving exceeds `O_w`; (c) the window bound for sub-threshold pacing; (d) when to start the procedure: at `(t^gate - T^leg)_+` or at the gate, with cutoff `varpi^A` (eq:labor-ann) and the contemplation constraint; (e) a free parallel run up to `T^hold` (eq:labor-freerun) | L1a to L1j |
| `ass:labor-survivor`, `prop:labor-survivor` | (a) backfill quits and their cost `C^surv`; (b) tranches never lower excess quits, and the per-wave charge `O_s`; (c) knowledge-holder success factor (eq:labor-success); (d) the retention-award rule; (e) the redeployment bound on `u_d` | L2a to L2j |
| `ass:labor-talent`, `prop:labor-talent` | (a) wage premium on build cost and minimum horizon; (b) maintenance ceiling `Gamma/e_mnt` and time to scope (eq:labor-TGamma); (c) hiring path with lead; (d) hire or contract | L3a to L3f |
| `lem:labor-location` | site wage index and the adoption lag `>= ln(1/w)/delta_pi`; never if `w c-bar <= c^fx` | L4a to L4c |
| `ass:labor-residency`, `prop:labor-residency` | (a) readiness cap `(1 - omega^res) iota` and permissibility; (b) process threshold `omega-bar^res = 1 - iota*/iota`, continuous or with a jump; (c) choice of region (eq:labor-region) and the residency premium in `B_j` | L5a, L5b, L5e (L5c and L5d support the engine rules in 3.6) |
| `cor:labor-pace` | the pace bound combining change capacity, bandwidth with wave length `T^eff`, and talent | L6a, L6b |

## 2. Where the results connect to other sections

- `prop:labor-lead`(a) replaces `T_par` in `prop:ext-waves` and `prop:ext-bandwidth` with the effective wave length `T^eff = max_c t^dis_c`. This is `cor:labor-pace`.
- `prop:labor-lead`(e) modifies `eq:tasks-tpar` (`prop:tasks-transition`) when dismissals are legally barred for `T^hold` after the run starts.
- `prop:labor-survivor`(a) adds `C^surv` to `C^str` in `ass:tasks-transition`. Part (b) adds `O_s` to `O_w` (`ass:ext-program`). Part (c) gives a structural form of the affected-headcount driver in `eq:tasks-success`. Part (d) uses `Y_s`, `Y_f` of `prop:tasks-pilot`.
- `prop:labor-talent`(a) feeds the minimum horizon of `prop:tasks-transition`(b). The capacity `Gamma` is the AI engineering line `l_AI F/(w^AI t_FTE)` of `def:ext-org`.
- `lem:labor-location` is `prop:ext-timing`(d)(ii) with a site wage index.
- `prop:labor-residency`(a) adds a constraint to `prop:ext-feasible` and `def:ext-universe` (`J^per`). Part (b) uses `prop:tasks-readiness`. Part (c) changes `c_A` inside `B_j` of `def:ext-effcost`.

## 3. Formulas for the engine

### 3.1 Statutory calculators (`tab:labor-rules`; verify L0)

The inputs are per site `e` and per displaced employee: tenure (years), age, monthly pay, and full-time or part-time status. Each calculator returns three things:
- `triggered` (a collective procedure is required);
- `T^leg` (years from procedure start to the earliest effective dismissal);
- `floor` (statutory cash per displaced FTE, in months of pay).

The engine then sets severance per FTE to `max(floor, negotiated plan)` and adds pay in lieu of any notice that is not worked.

**U.S. federal WARN** (29 U.S.C. 2101 to 2104; 20 C.F.R. 639.3).
- Coverage: the employer has 100+ employees excluding part-time (or 100+ including part-time working 4,000+ hours a week in aggregate).
- Trigger, plant closing: 50+ employment losses at a single site in 30 days.
- Trigger, mass layoff: 500+, or 50+ that are at least 33% of active full-time employees at the site.
- Aggregation: losses at a site over any 90 days are counted together, unless the employer shows separate and distinct causes (s.2102(d)).
- Lead: `T^not` = 60 days, `T^proc` = 0.
- Floor: none.
- Violation: back pay and benefits for up to 60 days, plus a civil penalty of up to $500 a day (s.2104).

**California** (Lab. Code 1400.5, 1401). A covered establishment has 75+ persons in the preceding 12 months. A mass layoff is 50+ in 30 days, with no percentage test. Notice is 60 days.

**New York** (DOL fact sheet P483). The employer has 50+ full-time employees in NY. A mass layoff is 25+ that are 33% of the site, or 250+. Notice is 90 days.

**New Jersey** (NJES-997, rev. 2/26). The employer has 100+, with 50+ terminated at or reporting to an NJ establishment. Floor: 1 week of pay for each full year, plus 4 weeks if notice is under 90 days. The engine treats NJ notice as 90 days, the benchmark the form uses.

**EU minimum** (Directive 98/59/EC).
- Thresholds over 30 days, for establishments of over 20:
  - 10+ where the establishment has 21 to 99 workers;
  - 10%+ where it has 100 to 299;
  - 30+ where it has 300+.
- Or, the Member State's alternative: 20+ over 90 days, at any size.
- Consultation starts "in good time" (Art. 2), from when redundancies are contemplated (Akavan, C-44/08).
- Dismissals take effect no earlier than 30 days after notifying the authority (Art. 4), extendable to 60.
- National law sets everything above this minimum.

**Germany.**
- Notification thresholds (KSchG s.17(1), within 30 calendar days):
  - more than 5, at 21 to 59 employees;
  - 10% or more than 25, at 60 to 499;
  - 30 or more, at 500+.
- Waiting period (KSchG s.18): dismissals take effect only after 1 month from the agency's receipt of the notification; the agency can extend this to 2 months.
- Works council (BetrVG):
  - s.111: inform and consult on a Betriebsänderung (in firms of more than 20 eligible employees). Nr. 5 covers fundamentally new work methods.
  - s.112(4) and (5): if there is no agreement on a social plan, the conciliation board decides. This is enforceable for pure staff reductions only above the s.112a(1) thresholds:
    - under 60 employees: 20% and at least 6;
    - 60 to 249: 20% or 37;
    - 250 to 499: 15% or 60;
    - 500+: 10% and at least 60.
  - s.102: hearing before each dismissal, with one week to object.
  - s.90(1) Nr. 3: information and consultation on planning work processes, including the use of AI.
  - s.87(1) Nr. 6: co-determination on technical systems suited to monitoring, decided by the conciliation board if the parties do not agree.
- Notice (BGB s.622(2), employer notice): 1 month at 2 years, 2 at 5, 3 at 8, 4 at 10, 5 at 12, 6 at 15 and 7 at 20 years. Below 2 years, the basic four weeks.
- Floor: none in general. KSchG s.1a gives 0.5 month a year if the employer offers it in the notice. A social plan is negotiated.
- Engine lead: `T^leg_DE = T^proc_DE + max(1 month, notice(tenure))`, where `T^proc_DE` (consultation on the reconciliation of interests) has no statutory length. It is a scenario parameter (Section 5).
- Engine technology lead: `T^tech_DE` (s.87(1) Nr. 6 and s.90 consultation) is also a scenario parameter.

**France** (Code du travail).
- PSE (job-protection plan): required at a firm of 50+ with 10+ dismissals in 30 days (L1233-61).
- CSE opinion period (L1233-30): 2 months for under 100 dismissals, 3 for 100 to 249, 4 for 250+.
- Administration (L1233-57-4): validation of an agreement in 15 days, or homologation of a unilateral document in 21 days.
- Notice (L1234-1): 1 month at 6 months to 2 years of tenure, 2 months at 2+ years.
- Floor (R1234-2): 1/4 month a year up to 10 years, 1/3 beyond.
- Reclassification leave (L1233-71): at firms of 1,000+, up to 12 months.
- Technology consultation (L2312-8, R2312-6): periods of 1, 2 or 3 months (2 with an expert).
- Engine lead: `T^leg_FR = CSE(d) + admin + notice(tenure)`.

**United Kingdom.**
- Trigger (TULRCA s.188): 20+ at one establishment within 90 days. From ERA 2025 s.29 (new s.195A), a threshold number set by regulations, never below 20, also triggers; it is not yet set.
- Consultation: at least 30 days (20 to 99) or 45 days (100+) before the first dismissal. HR1 notification (s.193) uses the same periods.
- Protective award: up to 180 days' pay from 6 April 2026 (s.189(4) as amended by ERA 2025 s.30(2)).
- Floor (ERA 1996 s.162): counting back from the relevant date, 1.5 weeks for each year aged 41+, 1 week aged 22 to 40, and 0.5 week otherwise, with at most 20 years counted. The week is capped at £751 from 6 April 2026 (GB).
- Engine lead: `T^leg_UK = consultation period`. Individual notice is assumed to run concurrently (**unverified**: ERA s.86 minimum notice was not read).

**India** (Industrial Relations Code 2020, in force 21 November 2025).
- Scope: a worker with at least 1 year of continuous service. Supervisory staff drawing over Rs 18,000 a month, and managerial or administrative staff, are not "workers" (s.2(zr)).
- s.70: 1 month's notice in writing, or wages in lieu.
- s.70: compensation of 15 days' average pay for every completed year of continuous service, and any part in excess of six months.
- s.70: notice to the appropriate government.
- s.83: 15 days of last drawn wages to the worker re-skilling fund.
- Chapter X (s.77): industrial establishments (factories, mines, plantations) with 300+ workers on average in the preceding 12 months need prior permission.
- Engine floor: `0.5 x round_half_up(tenure) + 0.5` months; with the 1 month of notice, 3.5 months in total at 5 years.
- **Unverified:** the 15/26 convention for monthly-rated pay (it would give 0.577 rather than 0.5 month a year); the s.79 notice length; and state Shops and Establishments Acts.

**Floors at 5 years of tenure** (verify L0f; age 35 for the UK):

| | U.S. federal | NJ | UK | DE (s.1a) | FR | IN |
|---|---|---|---|---|---|---|
| months of pay | 0 | 1.15 | 1.15 | 2.5 | 1.25 | 3.0 |

**Example leads for 150 dismissals at 5 years** (verify L0g, in years):

| | U.S. | NY/NJ | UK | IN | DE | FR |
|---|---|---|---|---|---|---|
| `T^leg` | 0.164 | 0.247 | 0.123 | 0.083 | 0.417 | 0.474 |
| basis | | | | | assumed 3 months of consultation | 3 + 0.7 + 2 months |

### 3.2 Lead times and wave timing (`prop:labor-lead`; L1)

- `T^st_c = (T^tech_c - T^bld)_+`, `t^gate_c = T^st_c + T_par`, and `t^dis_c = max{t^gate_c, t^A_c + T^leg_c}`.
- **Aggregation rule (engine default).** The engine counts all program dismissals at an establishment within each jurisdiction's window together. Sub-threshold pacing is allowed only if the user turns it on, and then only with a span of at least `(ceil(N^dis/(N^thr - 1)) - 1) T^win` (part c). For example, 200 UK redundancies kept below 20 per 90 days take 900 days.
- **Streams.** Sort jurisdictions by `t^dis`. Choose the interval partition that minimizes `sum_groups sum_{c in group} W_c (max_group t^dis - t^dis_c) + (#groups - 1) O_w`, by dynamic programming over the sorted list (`O(n^2)`).
- **Procedure start.** Let `T^ov = min{T^leg, t^gate}` and `varpi^A = (c^ann T^ov + C^wd)/(W T^ov + c^ann T^ov + C^wd)`. Start at the gate if `varpi < varpi^A`, otherwise at `(t^gate - T^leg)_+`.
  - If the law fixes a start by the contemplation date `t^cont < t^gate`, evaluate the cost at 0, at `t^cont`, and at `t^gate - T^leg` if that lies between them.
  - Engine default: `t^cont = 0` for EU and UK sites, because the decision to automate is when redundancies are contemplated (Akavan). The user can override this.
  - The cost function is `ann_cost` in L1.
- **Free parallel run.** `T^hold = t^A + T^leg - T^st` (time from run start to the earliest dismissal), and `T^opt_par = min{T**, max{T^hold, T*}}`. Here:
  - `T* = T_det ln(R/(T_det c-hat))`, with `R = (1 - varpi)(C^str + L_roll)` (eq:tasks-tpar);
  - `T**` is the same with `c-hat' = nu_rec E_p + C^dup`.
- **Cash.**
  - Severance per displaced FTE: `max(floor_c, plan_c)` times monthly pay.
  - Notice pay in lieu: where the notice exceeds the time to cutover, or the firm releases staff early.
  - `C^proc_c`: advisers, experts and social-plan negotiation (scenario).
  - Protective awards and WARN back pay enter only in a noncompliance scenario. They are never a planned cost.

### 3.3 Survivors and knowledge holders (`prop:labor-survivor`; L2)

- `N^q = N^sv e^{-nu^q T_s}(1 - e^{-nu^s(d) T_s})` and `C^surv = w (c^rep N^q + N^sv delta^eff(d) T_s)`. These are added to `C^str` and to the hiring plan: `N^q` backfills a year.
- Per-wave charge: `O_s = w N^sv T_s (c^rep eta_0 + delta_0)`, for `nu^s(x) = eta_0 1{x>0} + eta_1 x` and `delta^eff(x) = delta_0 1{x>0} + delta_1 x`. Add it to `O_w` in the wave optimizer.
  - The default fit uses the Sajjadiani et al. announcement effect, with `eta_1 = 0`: `eta_0 T_s = 0.0235` of survivors per announced wave.
- Success: `varpi_p = varpi^0_p [kappa_doc + (1 - kappa_doc) e^{-(1 - kappa_ret) nu^x tau^ann}]^{n_K}`.
  - `tau^ann = t^gate - max(t^A, T^st)` is the overlap of the announced period with the run.
  - `nu^x = nu^D - nu^q` for holders who are to be displaced, and `nu^s(d)` for those who stay.
- Retention awards pay iff `[varpi_p(kappa_ret) - varpi_p(0)](Y_s - Y_f) > n_K C^ret q_stay`, with `q_stay = exp(-(nu^q + (1 - kappa_ret) nu^x) tau^ann)`.
- Redeployment cap: `u_d <= min{1, varpi^rd nu^q N^oth T^w / N^dis}`, with `T^w = t^dis - t^A`. The engine caps the user's `u_d` (params `transition.u_d`) at this bound and reports when the cap binds.

### 3.4 Engineering talent (`prop:labor-talent`; L3)

- `w^AI = (1 + p) w^SE (1 + tau_L,annual) x wage_index(site)`.
  - `w^SE` is the OEWS median for SOC 15-1252.
  - `tau_L,annual = 0.2896` (params `payroll_loading.tau_L_on_annual_wage`).
  - Example: `w^AI = $194,649` at `p = 0.11`.
- Build cost `F = F_0 (1 + l_AI p)`. The minimum horizon rises by `l_AI p F_0/(varpi_p b-bar_p W)`.
- Capacity dynamics: `e_bld dN/dt = Gamma(t) - e_mnt N`.
  - With constant `Gamma`: `N(t) = (Gamma/e_mnt)(1 - e^{-e_mnt t/e_bld})`.
  - Time to scope: `T_Gamma(N) = (e_bld/e_mnt) ln(N-bar/(N-bar - N))`, infinite if `N >= N-bar = Gamma/e_mnt`.
  - With hiring, the engine integrates the ODE numerically, with `Gamma(t) = Gamma_0 +` the hires made at the rate `dot-Gamma^hire` that have started (requisitions older than `T^lead`), each counted at `1 - delta^rp` in its first `T^rp` years.
- Build-only closed form (L3e): cumulative person-years by `T` are `Gamma_0 T + dot-Gamma^hire [U^2/2 - delta^rp(min(U, T^rp)^2/2 + T^rp (U - T^rp)_+)]`, with `U = (T - T^lead)_+`. With `Gamma_0 = 0` and no ramp, `e_bld N` arrive at `T^lead + sqrt(2 e_bld N/dot-Gamma^hire)`.
- Hire or contract, for a gap `Delta Gamma` lasting `T^need >= T^rp`: contract iff `T^need < [delta^rp T^rp + c^hire + W-hat (T^lead - T^ct)/(Delta Gamma w^AI)]/u_ct`.
  - Reskilling is the same rule, with `T^lead` = training time, `c^hire` = training cost, and a larger `delta^rp`.

### 3.5 Location (`lem:labor-location`; L4)

- Wage index `w_c`: the roster wage divided by the U.S. median for the same SOC, where the roster has it (class c). Otherwise, the OECD average-wage ratio below (class a, all employees, not occupation-specific).
- Adoption lag `T*_c - T*_1 = ln[(c-bar - c^fx)/(w_c c-bar - c^fx)]/delta_pi`, with `c-bar = c_0 - c^Q_lab` and `c^fx = c^Q_loss + r F_0/v`. Automation never pays at the site if `w_c c-bar <= c^fx`.
- O*NET transfer. Outside the United States, the engine widens the dispersion of activity time shares by the scenario factor `onet_transfer_widening`. It uses country task surveys (PIAAC- or STEP-based routine task measures) where the firm supplies them. Within-occupation task content differs substantially across 47 countries, and occupational structure explains only about one fifth of cross-country variation in routine task intensity (Lewandowski et al. 2022). The ISCO-08 to SOC 2010 crosswalk has one-to-many and weak matches (BLS 2012).

### 3.6 Residency (`prop:labor-residency`; L5)

- `omega^res_j(g)` is the share of activity `j`'s input volume that cannot be used at region `g`. It is computed from three things:
  - each input's data class (`impute.DATA_CLASSES`: public, internal, confidential, restricted) and personal-data flag;
  - the data subjects' jurisdiction;
  - the firm's transfer mechanisms.
- Rule table (model constraints):
  - **EU or EEA personal data to `g` outside the EEA** (GDPR Arts 45, 46 and 49):
    - free if `g` is on the Commission's adequacy list (17 entries on 29 Oct 2026; the U.S. only for recipients certified under the DPF);
    - "mechanism" if SCCs or BCRs are in place (cost `F^tr`, which includes a transfer impact assessment);
    - otherwise unusable. Art. 49 derogations are not a basis for systematic processing.
  - **Chinese personal information to `g` outside China** (PIPL Arts 38 to 40; CAC 2024 provisions; certification measures from 1 Jan 2026):
    - security assessment ("mechanism" with a long lead) if the processor is a CIIO, the data include important data, or the transfer covers over 1 million people (non-sensitive) or over 10,000 (sensitive) since 1 January;
    - standard contract or certification for 100,000 to under 1 million (non-sensitive) or under 10,000 (sensitive);
    - exempt below 100,000 non-sensitive, and for necessary HR management or contract performance;
    - local storage for CIIOs.
  - **Indian personal data**:
    - free unless `g` is a country the Central Government notifies (DPDP Act s.16(1)); no list was found;
    - sectoral laws with stricter rules prevail (s.16(2)). Sectoral localization, such as payments, is a firm input; it is **unverified** here.
    - Most obligations of the DPDP Rules apply from 13 May 2027.
- Feasibility: `iota-bar_j(g) = (1 - omega^res_j(g)) iota_j`. An AI mode is feasible at `g` iff `iota-bar_j(g) >= iota_floor_j` and the capability test holds at `t - T^lag_g`. The activity is permissible iff some region passes.
- Process threshold: `omega-bar^res_p = 1 - iota*_p/iota_p`.
- Region cost: `c_A,j(g) = (1 + p^reg_g) pi n_j + c-hat^Q_j(iota-bar_j(g)) + (F^tr_g + nu^inv_g C^sw)/v_j`. The engine chooses the minimum and reports `Delta c^res_j`.
- **Regional instances (engine rule; cut from the paper for length; verify L5c).** Running `R` regional instances, each at its own readiness, beats one global instance at the weakest readiness iff `sum_c [W_c(iota_c) - W_c(iota_min)] > (R - 1) F a(r, T_A)`, where `a(r, T_A)` is the annuity factor for one more build.
- Mechanism hazard: `nu^inv = 0.089` a year for EU to U.S. transfers resting on a framework. The basis is two invalidations in 22.5 framework-years:
  - Safe Harbour, 26 Jul 2000 to 6 Oct 2015;
  - Privacy Shield, 12 Jul 2016 to 16 Jul 2020;
  - DPF, 10 Jul 2023 to 29 Oct 2026, still in force.
  This is a crude rate from two events; scenario range in Section 5.

### 3.7 Pace (`cor:labor-pace`; L6)

`T_prog >= max{N a/K_chg, N e T^eff/(x-hat Phi), T_Gamma_max(N)}`, with the symbols of `prop:ext-waves` and `prop:ext-bandwidth`. It is finite only if `N < Gamma_max/e_mnt`. The engine reports which constraint binds. In the example, talent binds: six engineers at `e_mnt` = 0.48 need 10.1 years (ceiling 12.5 processes), against 1.5 for change capacity and 1.28 for bandwidth. At `e_mnt` = 0.25 talent still binds, at 4.16 years.

## 4. Inputs the engine should request

| input | level | type | used by | if missing |
|---|---|---|---|---|
| headcount by country and site (normal, and maximum in the preceding 12 months), full-time vs part-time | site | int | all trigger tests (WARN 100/50/33%/500; CA 75; NY 50; EU and KSchG size bands; UK 20 per establishment; IN 300) | roster count by `location`; flag |
| employer headcount by country | firm x country | int | WARN coverage, NY 50, NJ 100, FR PSE 50, reclassification leave 1,000 | sum of sites |
| subnational unit (U.S. state; Indian state) | site | str | CA/NY/NJ rules; Indian state law (not modeled) | federal or national rules only; flag |
| Indian site type (factory, mine or plantation, or not) | site | enum | Chapter X prior permission | not Chapter X; flag |
| tenure distribution (mean and bands) and age distribution | role x site | dist | statutory floors (UK by age; DE, FR, IN by tenure), notice (BGB 622, L1234-1) | U.S. median tenure 3.9 years (params); age 40 |
| monthly pay and supervisory or managerial flag | role x site | float, bool | IN worker definition (Rs 18,000), UK week cap | roster wage |
| works-council presence (DE Betriebsrat, group-level Gesamtbetriebsrat; FR CSE and central CSE) | site, firm | bool | `T^proc`, `T^tech`, social plan, s.87 co-determination | present for DE sites of 5+ and FR sites of 50+ employees (statutory thresholds for election; **unverified**); flag |
| union recognition and coverage, collective agreements (notice, severance, consultation terms) | site | bool, terms | UK consultation with union representatives; negotiated plans `plan_c` | country coverage (BLS 2025: 11.2% represented in the U.S.; ETUI: DE in the 40 to 65% band, FR 70%+) as a flag only |
| negotiated severance plans or a social-plan framework | firm x country | formula | `plan_c` | statutory floor plus params `transition.severance_months_*` |
| contemplation date `t^cont`, announcement policy, waves by process and site | program | dates | `prop:labor-lead`(d), aggregation | `t^cont = 0` in EU and UK |
| build length `T^bld` per process | process | years | `s_c` | engine build estimate |
| critical knowledge holders `n_K`, whether they are to be displaced, documentation coverage `kappa_doc` | process | int, bool, share | `eq:labor-success` | `n_K` = 0 (no adjustment); flag |
| AI and agent engineers `Gamma_0` by site, hiring capacity `h`, open requisitions, contractor access | firm x site | FTE | `prop:labor-talent`, `cor:labor-pace` | roster SOC 15-1252/15-2051 counts |
| data-residency classes per system: data class, personal-data flag, special categories or sensitive PI, data-subject jurisdictions (shares), counts of Chinese data subjects a year, CIIO status, important-data flag, sectoral localization | system x activity | enums, shares | `omega^res_j(g)` | `impute.DATA_CLASSES` default by function; subjects' jurisdiction = site country; flag |
| transfer mechanisms in place (recipient DPF certification, SCCs, BCRs, PIPL standard-contract filing or certification) | firm x vendor | bool | "mechanism" share, `F^tr` | none |
| deployment regions offered by the AI vendor, regional price premium, model availability lag | vendor x region | list, %, years | `p^reg`, `T^lag` | one global region, `p^reg` = 0, `T^lag` = 0; flag |
| roster wages and `wage_index` | role x location | float | `lem:labor-location` | OECD ratios (Section 5) |

The schema already has `RosterRow.location` and `RosterRow.wage_index` (`engine/src/autofrontier/schema.py`), and `impute.DATA_CLASSES`. The rest are new fields.

## 5. Parameters (spec 21.1 grounding classes: a sourced, b precedent, c calibrated or firm input, d scenario)

| symbol | proposed engine key | value | range | class | source or precedent | used in |
|---|---|---|---|---|---|---|
| statutory thresholds, notice, waiting periods, floors | `labor.rules.<country>` | Section 3.1 | | a | statutes in `refs_labor.bib` | tab:labor-rules, prop:labor-lead |
| `T^proc_DE` (consultation on the reconciliation of interests) | `labor.T_proc.DE` | 3 months | 1 to 6 months | d | no statutory length; OECD Germany EPL note not reachable (robots) | prop:labor-lead example |
| `T^tech_DE` | `labor.T_tech.DE` | 3 months | 0 to 6 months | d | s.87(1) Nr. 6 and s.90 have no time limit | prop:labor-lead example |
| `T^tech_FR` | `labor.T_tech.FR` | 2 months | 1 to 3 months | a | R2312-6 (2 months with an expert) | prop:labor-lead example |
| UK consultation in practice | `labor.T_proc.UK_obs` | 36.9 days (20 to 99), 55.5 days (100+) | | a | DBT 2024 impact assessment (government estimate) | check on the 30/45-day minimum |
| FR delay before notice can start | | about 37 days | 16 to 47.5 days | a | OECD EPL France 2019 | cross-check |
| `c^ann` (cost flow of the announced state) | `labor.c_ann` | example $0.3M a year | | d | none | prop:labor-lead(d) |
| `C^wd` (withdrawal cost) | `labor.C_wd` | example $0.2M | | d | none | prop:labor-lead(d) |
| `C^proc_c` | `labor.C_proc` | | | d | none | ass:labor-proc |
| `nu^q` (baseline quit hazard) | `labor.nu_q` | 0.132 a year (information) | 0.12 (finance) to 0.25 (professional and business services) | a | JOLTS, Aug 2026, monthly rates x 12 | prop:labor-survivor |
| `nu^s` per announcement (`eta_0 T_s`) | `labor.survivor_excess_quits` | 0.0235 of survivors | 0.01 to 0.05 | b | Sajjadiani et al. 2023: 2.2 induced quits per store of about 93.6 (store size from press coverage); retail stores, so the range is widened for transfer | prop:labor-survivor(a,b) |
| `T_s` | `labor.T_s` | 1 year | 0.5 to 2 | b | Sajjadiani et al. (most quits in the first six months; 22-month panel) | prop:labor-survivor |
| `delta^eff` | `labor.delta_eff` | 0 | 0 to 0.10 | d | direction: Drzensky and Heinz (lab, 43%), Friebel et al. (26% and 7% in shops under announcement); size does not transfer | prop:labor-survivor(a) |
| `c^rep` | `labor.c_rep` | 0.56 years of wages | 0.29 to 0.76 | b | hiring 10 to 17 weeks, marginal up to 24 (Blatter et al., Swiss skilled hires) plus a shortfall of `delta^rp T^rp` | prop:labor-survivor(a) |
| `nu^D` (quits of staff to be displaced) | `labor.nu_D` | | `nu^q` to `nu^q` + 1.0 | d | direction: Schwerdt 2011, Lengermann and Vilhuber 2002 (better workers leave first); no rate | prop:labor-survivor(c) |
| `nu^x` | `labor.nu_x` | example 0.5 | 0 to 1.0 | d | derived from `nu^D` or `nu^s` | eq:labor-success |
| `kappa_doc` | `labor.kappa_doc` | example 0.2 | 0 to 0.5 | d | none | eq:labor-success |
| `kappa_ret`, `C^ret` | `labor.kappa_ret`, `labor.C_ret` | example 0.8, $60k | 0.5 to 0.9 | d | none found | prop:labor-survivor(d) |
| `varpi^rd` (placement probability per vacancy) | `labor.varpi_rd` | example 0.3 | 0.1 to 0.5 | d | none found; retraining effects turn positive after 2 to 3 years (Card et al. 2018), larger in screened sectoral programs (Katz et al. 2022) | prop:labor-survivor(e) |
| `u_d` | `transition.u_d` | 0.25 | 0.1 to 0.5, capped by 3.3 | d | params; bound from part (e) | ass:tasks-transition |
| `p` (AI wage premium) | `talent.premium` | 0.11 | 0.05 to 0.28 | a (0.05, 0.11); b (0.21); practitioner (0.28) | Alekseeva et al. 2021 (11% within firm, 5% within title, U.S. postings 2010 to 2019); Stephany and Teutloff 2024 (21%, freelance platform, 2014 to 2022); Lightcast 2025 (28%, method not stated) | prop:labor-talent(a) |
| agent-engineering premium | `talent.premium_agent` | = `p` | 0.05 to 0.40 | d | no measure | prop:labor-talent |
| `w^SE` | `talent.w_SE` | $135,980 | | a | OEWS May 2025, SOC 15-1252 median | prop:labor-talent |
| `tau_L,annual` | `payroll_loading.tau_L_on_annual_wage` | 0.2896 | 0.2791 to 0.3359 | a | params (BLS ECEC, June 2026) | w^AI |
| `T^vac` | `talent.T_vac` | 32 days | 29 to 35 days (information, FIRE); 39 at 5,000+ establishments | b | Davis, Faberman and Haltiwanger 2013 (JOLTS, 2001 to 2006, all vacancies); AI roles likely longer: 35% of U.K. organizations had a hard-to-fill AI vacancy in 2025 (DSIT, self-selected survey of 119) | prop:labor-talent(c) |
| `T^cn` (candidate notice) | `talent.T_cn` | 1 month | 0.5 to 3 months | d | country practice; German employee notice is 4 weeks under BGB 622(1) unless the contract extends it | prop:labor-talent(c) |
| `T^lead` | `talent.T_lead` | 0.25 years | 0.1 to 0.5 | b/d | `T^vac + T^cn` | prop:labor-talent(c) |
| `delta^rp`, `T^rp` | `talent.delta_rp`, `talent.T_rp` | 0.15, 2 years | 0.05 to 0.3; 1 to 3 | d / b | Bidwell 2011: external hires underperform insiders for about two years; no percentage | prop:labor-talent(c,d) |
| `c^hire` | `talent.c_hire` | 13.5 weeks of wages | 10 to 24 weeks | b | Blatter et al. 2012 | prop:labor-talent(d), c^rep |
| `u_ct`, `T^ct` | `talent.u_ct`, `talent.T_ct` | 0.5, 1 month | 0.3 to 1.0; 0 to 2 months | d | none verified | prop:labor-talent(d) |
| `e_bld` | `org.e_bld` | 1.5 person-years per process | | d | example | prop:labor-talent(b) |
| `e_mnt` | `org.e_mnt` | 0.48 | 0.29 to 1.14; sensitivity 0.25 | b | engine default, linked to `organization.ai_engineers_per_automated_process_run` (assumptions register row 14) | prop:labor-talent(b), cor:labor-pace |
| `w_c` (wage index, market exchange rates, 2024, U.S. = 1) | `location.wage_index_default` | DE 0.932, UK 0.912, FR 0.663, JP 0.490, PL 0.332, CN 0.240, MX 0.137, IN 0.042 | | a | OECD Pensions at a Glance 2025, Table 7.5 (OECD Taxing Wages; ILO for CN and IN); averages over all employees | lem:labor-location |
| `onet_transfer_widening` | `location.onet_widening` | 1.5 | 1 to 2 | d | direction: Lewandowski et al. 2022; De La Rica et al. 2020; Handel 2016 | engine time shares |
| `nu^inv` (EU to U.S.) | `residency.nu_inv.EU_US` | 0.089 a year | 0.04 to 0.15 | b | two invalidations in 22.5 framework-years; DPF appeal C-703/25 P pending | prop:labor-residency(c) |
| `nu^inv` (SCC route) | `residency.nu_inv.SCC` | 0 | 0 to 0.05 | d | SCCs were upheld in Schrems II, but supervisory authorities may suspend them case by case | prop:labor-residency(c) |
| `C^sw` | `residency.C_sw` | example $0.5M | | d | none | prop:labor-residency(c) |
| `F^tr` | `residency.F_tr` | | | d/c | firm input (legal and TIA cost) | prop:labor-residency(c) |
| `p^reg`, `T^lag` | `residency.p_reg`, `residency.T_lag` | 0, 0 | 0 to 0.3; 0 to 1 year | d/c | vendor price lists and availability (not verified) | prop:labor-residency(a,c) |
| PIPL volume thresholds | `residency.cn_thresholds` | 1,000,000 / 10,000 sensitive / 100,000 | | a | CAC 2024 provisions; certification measures 2025 | 3.6 |
| union representation | `labor.union_cov.US` | 11.2% (10.0% membership), 2025 | | a | BLS union release, Feb 2026 | flag |

The premium example of `prop:labor-talent`(a) reads the running invoice example (`data/examples/invoice_chain.json`, version 2026-10-29b, through the `\ic...` macros): `F` = $2.81M, `F_build` = $622k, `F_int` = $2.00M, `W` = -$213k (values of 29 Oct, latest JSON), and premium 0.11 (engine `build.ai_engineer_premium`). The other example values that the labor section borrows from `theory_ext` are labeled illustrative there: `O_w` = 0.5, `c^dr_2` = 0.25, `T_par` = 0.5, the bandwidth breakpoint, `K_chg`, `Phi` and `a`.

## 6. Notation added

No reserved Part I symbol (spec Section 1) is reused. The first draft used bare `s`, `G`, `D`, `m`, `h`, `a`, `R`, `Q`, `s-bar` and, in the proofs, `f`, `g`, `k`, `X` and `beta`. All were renamed on 29 October (the verify script keeps its short names; its docstring maps them).

- **Jurisdictions and procedures:**
  - `\mathfrak c in \mathfrak C` (jurisdiction); `\mathfrak e` (establishment);
  - headcounts `N^hc_e` and `N^dis_e`; threshold `N^thr`;
  - durations `T^win`, `T^proc`, `T^not`, `T^leg`, `T^tech`, `T^bld`, `T^st_c` (run-start delay), `T^ov`, `T^hold`;
  - dates `t^gate_c` (gate), `t^A` (procedure start), `t^dis` (earliest effective dismissal), `t^cont`;
  - costs and cutoffs `c^ann`, `C^wd`, `C^proc`, `T^sev_c`, `varpi^A`, `c-hat'`;
  - streams `\mathfrak C_1, ..., \mathfrak C_q`.
- **Survivors:**
  - `\mathsf d` (displacement share), `N^sv` (survivors), `N^q` (extra quits), `N^oth`;
  - hazards `nu^q`, `nu^s`, `nu^D`, `nu^x`, with `eta_0`, `eta_1`;
  - `T_s`, `c^rep`, `delta^eff` (with `delta_0`, `delta_1`), `O_s`, `C^surv`;
  - knowledge holders `n_K`, `kappa_doc`, `kappa_ret`, `C^ret`, `q_stay`, `tau^ann`;
  - redeployment `varpi^rd`, `T^w`;
  - proof-only: `N^pl`, `\mathfrak b`, `\mathfrak u`, `n^b`, `i^b`.
- **Talent:**
  - `Gamma` (engineering FTE), `dot-Gamma^hire` (hiring rate), `e_bld`, `N-bar_Gamma`, `T_Gamma`;
  - `T^lead`, `T^vac`, `T^cn`, `delta^rp`, `T^rp`, `T^need`, `W-hat`;
  - wages and costs `\mathsf p`, `w^SE`, `w^AI`, `c^hire`, `u_ct`, `T^ct`.
- **Location:** `\mathsf w_c`, `c-bar`, `c^fx`.
- **Residency:** `\mathfrak g`, `omega^res`, `omega-bar^res_p`, `iota-bar`, `F^tr`, `nu^inv`, `C^sw`, `p^reg`, `T^lag`, `Delta c^res`.
- **Pace:** `T^eff`.
- **Borrowed from `theory_ext`:** `a` (affected FTE per process), `K_chg`, `e`, `Phi` and `x-hat`, in `cor:labor-pace`. The bare `a` there is the extension section's own reuse of a reserved symbol. **Flag for the lead.**
- Decorated reserved letters appear as elsewhere in Part II (`T_s`, `tau^ann`, `Delta Gamma`, `nu^D`).

## 7. Notes for the lead

1. **Severance in params.yaml.** The regional constants (US 3, DE 2, FR 1, UK 0.9 months) are consistent with the statutory floors at the median U.S. tenure of 3.9 years. The engine should still compute floors from roster tenure and age (Section 3.1), add notice pay in lieu, and take the maximum with any negotiated plan.
   - `severance_months_other` (1 month) understates India: 3.5 months at 5 years, including notice and the re-skilling fund.
   - `severance_months_other` also misses New Jersey's statutory severance.
2. **Payroll loading.** The talent example applies the annual-wage loading 0.2896 to the OEWS annual median, following the params note. `theory_ext` applies 0.43 to an hourly wage, which is consistent with that note. An earlier draft of this section used 0.43 on an annual wage. It was corrected: `w^AI` is $194,649, and the contract threshold is 1.80 years.
3. **Running example (updated 29 Oct, coordinator request).** The talent example no longer uses the voided $920k build and `varpi_p b-bar_p W` = $302k. It now uses the invoice example through its macros, and the verify script reads the JSON (L3a).
   - The build `F_build` ($622k) is engineering time already priced at the premium, so the premium is $61,600 of `F` = $2.81M (`l_AI` = 0.20, `l_AI p` = 2.2%). These derived numbers, the premium rate, the loading, `w^SE`, `w^AI` and the contract threshold (1.80 years) enter the tex only through `part2/tables/labor_macros.tex`, written by `code/make_labor_macros.py` from the JSON; L3a, L3b and L3f recompute them from the JSON and compare them with the macro file.
   - Because `W` = -$209k, the example has no finite minimum horizon. The horizon statement of part (a) therefore applies only where `W > 0`, and the text says so instead of quoting a horizon.
   - If the invoice example changes, rerun `python3 code/make_labor_macros.py`; until then L3a, L3b or L3f fails.
4. **`e_mnt`.** The engine default is 0.48 [0.29, 1.14], class b, and the paper's main values now use it:
   - six engineers sustain at most 12.5 processes, and 12 take 10.1 years;
   - hiring ten a year after a quarter-year lead puts 12 processes live at 2.36 years (2.15 without maintenance);
   - 0.25 is kept only as a sensitivity (ceiling 24, 4.16 years). Talent binds in the pace corollary in both cases.
5. **Scenario parameters behind results.** `nu^D`, `kappa_doc`, `kappa_ret`, `C^ret`, `varpi^rd`, `u_d`, `c^ann`, `C^wd`, the German consultation length and the agent-engineering premium are class d. Every claim that uses them is stated conditionally in the paper.
6. **Not verified, so not used as numbers:**
   - Trevor and Nyberg's "1% downsizing, 31% more voluntary turnover" (press only);
   - the Sajjadiani store size of 93.6 (press coverage, used only to convert per-store quits to a rate);
   - German social-plan amounts;
   - India's 15/26 convention and the Chapter X notice length;
   - UK statutory individual notice (ERA s.86);
   - the DPDP Rules Gazette text (dates from SCC Online and practitioners);
   - the Trump v. Slaughter slip opinion (Mayer Brown summary);
   - the official Cal-WARN page (FindLaw and california.public.law reproductions).
7. **Cut from the paper for length but kept for the engine:**
   - the regional-instances rule (3.6; verify L5c);
   - the hiring path with a ramp (3.4; verify L3e, 2.31 years);
   - the attrition-only time to shed 10% (0.80 years at `nu^q` = 0.132; verify L2i);
   - sub-threshold pacing in Germany (300 days for 300 dismissals at a 500+ establishment; verify L1d).
8. **Bibliography.**
   - `dbt2024impact` is in `refs_labor.bib` but uncited in the tex. It is the source of the UK consultation durations above. Cite it or drop it.
   - MitbestG (over 2,000) and DrittelbG (over 500) were verified and then removed: board co-determination does not constrain timing.
   - Six keys are reused, not duplicated: `eu2016regulation`, `eu2024regulation`, `park2013turnover` (refs_part2), `eu2026regulation` (refs_modern), `acemoglu2022artificial` (refs) and `dessaint2017employment` (refs_acquirer; cited at the acquirer section's request). The paper's bibliography must include `refs_acquirer.bib`.
9. **Rules that will move.**
   - The UK organization-wide threshold is not yet set by regulations; the DBT preferred option is a fixed number from 250 to 1,000.
   - The DPF appeal (C-703/25 P) is pending.
   - India may notify restricted countries under DPDP s.16.
   - The EU AI Act Art. 26(7) duty to inform workers' representatives applies from 2 December 2027 (Regulation (EU) 2026/1744).
   - Store these as dated rule versions in `labor.rules`, with an `as_of` field.
