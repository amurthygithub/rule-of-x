# Round 2 pressure-test: quantitative investment management panel

**Paper:** Paper 1 v2, "The Rule of 40 as a Price Line: Efficient Frontiers, Economic Profit and the Limits of AI Automation" (`notes/reviews/paper1_v2/paper1_v2.pdf`, `.txt`; supplement `supplement_v2.pdf`, `.txt`)
**Response under review:** `notes/reviews/paper1_v2/response_to_reviewers.md` (IM rows)
**Round-1 report:** `notes/reviews/paper1_v1/panel_investment_management.md`
**Date:** 2 November 2026
**Panel roles:** quant researcher (QR); fundamental analyst who builds screens (FA); risk manager (RM)
**Data and code used (read only):** `data/panel_v3.csv`, `data/panel_v3_all.csv`, `data/panel_v3_core_full.csv`, `data/sic_universe.json`, `data/frames_universe.json`, `data/frames_extra.json`, `notes/empirics_v3.json`, `notes/inference_v3.md`, `notes/sample_audit.md`, `notes/assumptions_register.md`, `code/estimate_v3.py`, `code/estimate_organic.py`, `code/build_panel_v3.py`. Nothing in the repository was edited. All new scripts and their outputs are in `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/` (Section 5). I did not read any `r2_*` report.

**Independence caveat.** One AI agent played all three roles in sequence, on the same model family as the agents that drafted the paper. The roles share test results. This is structured self-critique, not an independent panel, which is the same status Appendix B.2 and S7.3 of the paper give to the practitioner panels. Every number below comes from a script listed in Section 5 or from a file named in the text. Where my bootstrap draws differ from the paper's (different seeds, B = 400 to 1,500 against 999), I say so; point estimates were checked against the paper's and match to the printed digit.

---

## 0. Summary and verdict

**Verdict: major revision on the empirical sections; not usable as a screen or factor in its present form.** Round-1 fixes on data hygiene are real and verified. The open problems moved from the sample to the interpretation and to the precision of the headline numbers.

**What is resolved.** The backfill problem is gone: rule R1 removes 140 firm-years, no kept row has a source period later than its own, and the P95 decline is now 11.9 (GAAP) and 12.7 (cash) points. It holds among the 80 firms present in both periods and with a constant-real size threshold. The capital-intensity result is correctly demoted to an accounting effect. The E1-versus-E2 "changed conclusions" are withdrawn. Protocol disclosure of the single-agent panels is in the paper. The captive filer (Exzeo 2025) is excluded and the unflagged acquirer (Xunlei 2025) is flagged.

**What is not.** Three results the abstract and Sections 5.2, 5.10, 7.4 and 9 rest on do not stand as written:

1. "The best margins attainable at a given growth rate showed no detectable change" rests on percentile intervals. The frontier point at 20% growth fell by 10.2 points (GAAP, E1), the same size as the P95 decline, and its basic, normal and bias-corrected 90% intervals all exclude zero. The "compositional" reading is therefore not separated from a fall in the margins of fast growers (N1).
2. The reweighting decomposition behind "because fast growers became scarcer" changes sign of its within-bin term with the number of bins (composition share from 25% to 145%), and the whole score distribution shifted down, not only its top (N2).
3. The headline path score of 66 (56 in 2028) rests on an anchor of 13 firm-years from 7 firms, with no interval on the intercept. Reconstructing Table 5, the anchor's sampling error alone gives roughly 62 to 72 for 2036 and 49 to 66 for 2028. The headline also uses the "all selling and marketing buys growth" bound, which the paper's own maintenance-spend evidence contradicts (N6, N7).

**Screening use.** The paper has no returns, valuation, holdout or point-in-time screen test (IM-7 is "Not done" in the response). Its conclusion nevertheless tells practitioners to "use the Rule of 40 to screen firms". That sentence is unsupported by anything in the paper (Section 3).

**Counts.**

| | Resolved | Partly | Not resolved |
|---|---:|---:|---:|
| Round-1 items IM-1 to IM-6 | 3 (IM-1, IM-3, IM-6) | 3 (IM-2, IM-4, IM-5) | 0 |

| New findings | High | Medium | Low | Total |
|---|---:|---:|---:|---:|
| Section 2 (N1 to N12) | 3 | 6 | 3 | 12 |

Top five issues: N1 (frontier-point change at 20% growth and interval type), N2 (unstable composition decomposition and cyclical alternative), N6 (anchor of 13 firm-years from 7 firms; headline precision), N7 (selling-and-marketing bound against the paper's own maintenance base), N5 (multiplicity statements and tautological members of the testing family). The missing returns evidence behind "use it to screen" is the top issue for practitioners (Section 3).

---

## 1. Round-1 items: status and evidence

### 1.1 Status table

| ID | Round-1 item | Response says | Panel status | Evidence (panel_v3 unless stated) |
|---|---|---|---|---|
| IM-1 | Backfilled years; restate the decline | Fixed | **Resolved** | R1 excludes 140 firm-years of `panel_v3_core_full.csv` (98 before first annual report, 40 fiscal-2010, 2 later vintage; by period 52 / 40 / 38 / 10). Kept sample: 0 of 1,788 rows with `src_period_end` after `fy_end`; filing lag median 57 days, P99 119, maximum 343. In the v2 core, backfilled years were 2 of 23 (GAAP) and 5 of 23 (cash) of the 2016-19 top 5% and 0 of 23 in 2023-25; they are now out. P95 change: GAAP -11.9, cash -12.7 (round 1: cash -15.2). Stayers (80 firms in both periods): GAAP -10.7 [-19.4, -4.1], cash -14.4 [-21.5, -8.0]. Constant-real $100M threshold (2010 dollars): -12.4 and -13.2. Dropping each firm's first panel year: -11.6 and -12.0. Leave-one-firm-out range: GAAP -12.4 to -11.2, cash -13.4 to -11.4. The text now says "first reported" with R1 stated. |
| IM-2 | Yearly series and slope regimes | Fixed | **Partly** | Table S5 gives the yearly P95 and within-year slopes; Section 5.3 gives period slopes and the steepening (GAAP Psi slope 2010-19 -0.22, 2020-25 -0.60; difference -0.38 (0.13), Holm 0.037 to 0.060). I reproduce -0.215, -0.596 and 2020-24 -0.626. Not fixed: (i) the abstract and Section 5.10 still quote the pooled "about a fifth of a point", an average over the break the paper documents (N4); (ii) "recovered in 2025" is an E1-only statement and the abstract omits it (N3); (iii) the 2025 within-year slope is +0.11, so the "steepened after 2020" regime ended in the last year of data (N3). |
| IM-3 | Multiple testing; capital-intensity identity | Fixed | **Resolved** (with residuals in N5) | Capital intensity, 2023-25 cash P95 gap, E1: same-year sort -12.5 [-20.1, -3.5] (paper -12.5); with capital spending added back -4.6 [-14.9, +5.4] (paper -4.6 [-14.6, +6.0]); prior-year sort -8.6 [-17.1, -1.0], added back -1.9 [-11.3, +6.4]; firm-median sort -4.8 [-14.3, +4.2]. E2 proxy: same-year -7.1, added back -0.2, prior-year -4.6 [-14.6, -0.4] and +0.1 added back. The text calls the gap an accounting effect and removes it from the abstract: correct. The 38 E1-E2 contrasts fail Holm at 5% under every interval type (`inference_v3.md` section 5), and the abstract no longer states any E1-E2 difference. |
| IM-4 | Anchor uncertainty; captive and unflagged-acquirer firms | Partly | **Partly** | Exzeo 2025 is excluded (`v3_exclude` = R3) and Xunlei 2025 is flagged (`acq_reason_v3` = cheap_acquisition). Firm-cluster intervals are reported for the surplus: Pi_ub -1.3 [-18.2, +16.4] (mine -1.3 [-17.3, +16.0]). Not fixed: two-year average margins (declined in the response); the anchor shrank to 13 firm-years from 7 firms, with 6 of 13 from two firms (Clear Secure 3, Duolingo 3); no interval is reported on the intercept m0 that drives the headline path (N6); few-cluster bootstrap reliability (N6). Round-1 winner's-curse worry is partly mitigated on v3: for the 9 anchor firm-years with a next year, the median cash margin is unchanged (22.4 to 22.4) and the median score falls from 54.1 to 50.7. |
| IM-5 | Growth weight 7 to 13 and the alpha label | Partly | **Partly** | The weight is withdrawn in the abstract, Section 5.4 and Section 8.1; alpha is class d in Table S7. `notes/assumptions_register.md` still lists alpha as class c, "S&M ratio 3.3" (lines 62 and 243). The spend ratio is kept as a "robust statistic of its own" (3.0 to 3.5), but it is robust only across the four sample views. By year it runs 2.14 to 4.72 (2021: 2.47; 2025: 4.72), by period 2.61, 2.75, 2.78, 4.25, and a within-year permutation of selling and marketing shares gives 2.50 [2.38, 2.62] against the actual 3.02 (N9). Section 8.1 still builds a policy sentence on the gross 3.02 (N9). |
| IM-6 | Protocol: each panel is one agent playing several roles | Fixed | **Resolved** | Appendix B.2: "Each practitioner panel was a single agent playing several named roles, so the panels are structured self-critique, not a set of independent human experts"; same text in S7.3; B.6 adds that same-model agreement is weak evidence. (The response row for IM-6 has an empty notes cell, but the paper is correct.) |

Out of scope but recorded: IM-7 (holdout and returns test) is "Not done"; IM-8 to IM-10 are "Partly". I re-ran the holdout myself (1.2) because the screen question depends on it.

### 1.2 Round-1 checks re-run on panel_v3

| # | Round-1 test | Round 1 | Round 2 (v3) | Bearing |
|---|---|---|---|---|
| T1 | Backfilled years in the "first reported" panel | 141 core firm-years, 138 in first panel year | 0 remaining; 140 excluded by R1 | Fixed |
| T2 | P95 change 2016-19 to 2023-25 | GAAP -11.5, cash -12.0 without late years (baseline cash -15.2) | GAAP -11.9, cash -12.7; stayers -10.7 and -14.4; real threshold -12.4 and -13.2 | Survives |
| T3 | Annual series and slope regimes | 2025 GAAP P95 54.6; slope -0.25 then -0.8 | 2025 GAAP P95 51.4 (E1), 45.1 without acquisition-flagged firm-years, 44.8 in E2; local slope 2025 +0.11; Psi slope 2010-19 -0.22, 2020-25 -0.60 | Reported; headline still pooled (N3, N4) |
| T4 | Capital-intensity gap | prior-year sort -2.9 on E2 proxy | E1 same-year -12.5, prior-year -8.6, added back -4.6 and -1.9; E2 proxy prior-year -4.6, added back +0.1 | Identity confirmed |
| T5 | Calibration anchor | 20 firm-years, 12 firms; intercept median 44.6 [34.1, 52.3] | 13 firm-years, 7 firms; intercept median 42.0 [34.1, 52.4], Q3 51.8 [42.0, 63.7] (my 2,000-draw firm-cluster bootstrap) | Thinner; interval not in paper (N6) |
| T6 | Spend ratio by period | 3.11, 2.84, 2.98, 4.21; 2021: 2.28 | 2.61, 2.75, 2.78, 4.25; 2021: 2.47; 2025: 4.72 | Time variation persists (N9) |
| T7 | Out-of-sample content of the durable/transient split (train 2011-18, test 2019-24, next-year change in cash score) | R2 0.153 / 0.180 / 0.182 / 0.177 | 0.166 / 0.182 / 0.190 / 0.187 (same specification: score; score + surplus; g and m; g, m + surplus) | Unchanged: the split adds 0.016 over the score and nothing over g and m |
| T8 | Interval type on E1-E2 contrasts | percentile excluded zero where basic did not | Paper now withdraws the contrasts; same interval-type issue appears in the other direction for T(20%) (N1) | |
| T9 | Multiplicity | 14 contrasts, Holm | Paper adopts Holm and Romano-Wolf; see N5 for what the statements say | Partly |
| T10 | Acquisition-affected share of the E1 top bucket (cash score, v3 flag) | 46%, 30%, 46%, 35% | top 5%: 43%, 38%, 59%, 41% (10/23, 8/21, 13/22, 9/22); top quintile 46%, 40%, 43%, 23% | Membership effect remains large; E2 still cannot be a screen (Section 3) |

---

## 2. New findings

Severity: **High** = changes a claim in the abstract or leaves it unsupported; **Medium** = changes the strength or wording of a stated result; **Low** = presentation, hygiene or robustness note.

### N1. High. The "no detectable change in margins at a given growth rate" claim rests on percentile intervals; the frontier point at 20% growth fell by about 10 points
*Role: QR. Location:* intro, finding five (p.3); Section 5.2 (p.38 to 39); Section 5.10 (v); Section 7.4 (p.56, inference that "the supply of growth opportunity" binds); Section 9; Table 2 rows "Change in T (0%)" and "T (20%)"; D-3 column.

**Issue.** The abstract and Sections 5.10 and 9 attribute the P95 fall to composition "with no detectable change in the best margins at a given growth rate". The evidence is T(0) (GAAP +0.8) and T(20%) (GAAP -10.2 [-15.1, +1.1], percentile). Section 7.4 then uses this to say that the constraint on firms is the supply of growth opportunity, not willingness to trade margin. But T(20%) fell by as much as the P95 itself (-11.9), and the interval excludes zero under every type except the percentile type, which is the type with the largest bootstrap bias here (+2.2 points). D-3 treats "interval includes zero in all four views" as support for "no change". Absence of significance at the percentile level is not evidence of no change, and the paper says itself that the intervals are wide.

**Evidence** (`notes/empirics_v3.json`, `estimates.T_op_g20_change`; script `t15_json_extract.py`; 90% intervals, points):

| View | Estimate | Percentile | Basic | Normal | Bias-corrected | p (pct / basic / normal) |
|---|---:|---|---|---|---|---|
| E1 | -10.2 | [-15.1, +1.1] | [-21.5, -5.4] | [-18.3, -2.2] | [-16.7, -2.9] | 0.132 / 0.004 / 0.037 |
| E2 | -9.7 | [-15.1, +3.0] | [-22.4, -4.3] | [-18.7, -0.6] | [-17.7, -1.7] | 0.250 / 0.006 / 0.078 |
| E2 + M = 4 | -7.2 | [-12.8, +4.2] | [-18.7, -1.6] | [-15.7, +1.3] | [-14.4, +1.3] | 0.280 / 0.050 / 0.163 |
| E2 + M = 8 | -6.3 | [-12.0, +3.7] | [-16.2, -0.5] | [-13.9, +1.3] | [-13.1, +1.5] | 0.254 / 0.078 / 0.175 |

My own bootstrap (1,500 draws from all 292 firms): E1 -10.2, percentile [-14.7, -0.2], basic [-20.3, -5.8], two-sided p about 0.10 (percentile) and 0.004 or less (basic); the percentile bound sits on zero, so which side it falls on is bootstrap noise. Margin quantiles by growth group (GAAP, 2016-19 to 2023-25; `t3_composition.py`): P90 margin for g in [0.4, 5): 17.0 to 5.8 (n 64 to 16); g in [0.2, 0.4): 18.1 to 12.5 (n 127 to 108); g in [0.1, 0.2): 26.1 to 28.7; g in [0, 0.1): 28.0 to 25.9. The fall is concentrated among firms growing 20% or more, which is also where the Psi slope steepened. The T(0) "stability" is carried by slow growers with high margins (for example Microsoft, Adobe, Cadence in 2023-24).

**Suggested change.** Report T(g0) for g0 = 10, 20, 30% with percentile, basic, normal and bias-corrected intervals, as the paper does for E1-E2 contrasts. State: "the data cannot distinguish a change in the growth mix from a fall of about 10 points in the best margins of firms growing 20% or more". Remove "no detectable change" from the abstract-level summaries (5.10 (v), Section 9, intro), and restate the Section 7.4 inference as conditional. Drop the causal "because" in the intro and "as fast growers became scarcer" in the abstract, or replace by "alongside fewer fast growers". Apply one interval type consistently to claims of "no change" and claims of change.

### N2. High. The composition decomposition is unstable in the bin choice; the whole distribution fell; a cyclical alternative is not tested
*Role: QR, RM. Location:* Section 5.2 (p.38); abstract ("as fast growers became scarcer"); Section 7.4; S7.3 ("explained as a change in composition").

**Issue.** (a) The paper's 10-bin result is reproduced exactly (direction A composition -7.9 with within -4.1; direction B -7.2 and -4.7), but it is one point of a path that changes sign. (b) R = g + m contains g, so a reweighting on growth bins attributes all within-bin growth shifts (the top bin runs from about 45% to 500%) to "within", and fewer fast growers is close to a restatement of a lower upper tail of g. (c) The score fell across the distribution (below), so "the top" is not special. (d) Cyclical and entry-window explanations fit the same facts and are not addressed.

**Evidence** (`t3_composition.py`, `t2_yearly.py`, `t11_jackknife.py`, `t7_stayers.py`):

- GAAP P95 change -12.0 (own weighted-quantile definition; paper -11.9 with the standard P95). Composition / within, quantile bins, direction A (2023-25 reweighted to the 2016-19 growth mix): 4 bins -3.1 / -8.8; 5 bins -4.3 / -7.7; 8 bins -7.2 / -4.8; 10 bins -7.2 / -4.7; 15 bins -16.3 / +4.3; 20 bins -17.4 / +5.4; 40 bins -17.4 / +5.4. Equal-width bins, 5 / 10 / 20: composition -10.7 / -17.9 / -9.6. Direction B (2016-19 reweighted to the 2023-25 mix): composition -4.9 to -8.0, within -4.0 to -7.0 for every bin count. So the composition share runs from about 25% to above 140% and the within term from -8.8 to +5.9. Cash basis, 8 to 40 bins, direction A: composition -14.7 to -18.3 and within +1.9 to +5.5.
- Bootstrap (500 draws, GAAP, direction A): 10 bins composition [-22.3, -1.4], within [-14.8, +11.5]; 20 bins composition [-39.8, -2.4], within [-12.1, +26.3]. The two terms cannot be separated.
- GAAP score change by quantile, 2016-19 to 2023-25: P10 -19.9, P25 -9.3, P50 -6.9, P75 -4.3, P90 -8.3, P95 -11.9, P99 -53.9. Cash: -13.0, -7.2, -8.3, -7.8, -8.8, -12.7, -55.1. Growth quantiles: median 16.4 to 12.7; P75 31.5 to 21.4; P90 46.6 to 29.8; P95 58.2 to 35.8; share with g at least 40%: 15.3% to 3.6%. Median growth was 20.3% in 2020-22, so 2016-19 is a mid-cycle base and 2020-22 a peak.
- Entry window: firm-years in a firm's first panel year (2011 onwards) fell from 83 in 2020-22 to 18 in 2023-25; 91 of the 171 firms in 2023-25 were absent in 2016-19 and carry 229 of 447 firm-years (P95 39.5 against 45.1 for incumbents). The public-only sample's top tail depends on the IPO window; the 2023 to 2024 trough coincides with the rate shock and closed window. The decline survives among stayers (-10.7 and -14.4), which rules out pure cohort replacement but not a cycle.
- Single-firm influence is small (range -12.4 to -11.2 GAAP), but dropping the three firms whose removal shrinks the decline most gives -9.6 (GAAP) and -7.4 (cash) (SS&C, Check Point, Shopify).

**Suggested change.** Report the decomposition for 5, 10 and 20 bins and both directions, with intervals, or replace it by a decomposition that treats g and m|g separately (for example a Machado-Mata or RIF quantile decomposition on margin given growth, with g added back). Say that the fall is general across quantiles. Add the cyclical reading as an alternative (post-2021 growth normalisation, rate shock, IPO window), and add year-of-entry cohort controls. Reword "reflects a change in composition" to "is accompanied by".

### N3. Medium. "The top recovered in 2025" is an E1-only statement driven by acquisition-flagged firm-years; the 2025 slope reverses the regime
*Role: QR. Location:* intro (p.3); Section 5.2 (p.38); Section 5.10 (v); Section 9; Table S5.

**Issue.** D-3 requires claims to hold in all four views. The recovery does not. The abstract omits it and still quotes the 2016-19 to 2023-25 fall.

**Evidence.** GAAP P95 by year (E1): 2023 42.9, 2024 41.5, 2025 51.4 (SE 6.4; 144 firm-years, P95 set by the 8th highest value). The five highest 2025 GAAP scores: CoreWeave 167.0 (acquisition-flagged; compute infrastructure that the panels named but the R2 classifier missed), Palantir 87.8, Gen Digital 69.5 (flagged), GCL Global 62.6 (flagged), Clearwater Analytics 60.8 (flagged). Excluding flagged firm-years: 2025 GAAP P95 45.1 against 42.3 for 2023-24 (recovery 2.8 points, not 9.3); cash 43.6. Table S5 E2: 44.8 (GAAP), 43.6 (cash), against 42.1 and 42.4 in 2023, 41.8 and 42.3 in 2024. Change from 2016-19 to 2025: E1 GAAP -4.5 [-17.7, +8.7]; E2 GAAP -9.4 [-18.6, +1.1]; E2 cash -10.3 [-18.3, -1.2]. Within-year local slope (E1 GAAP): 2023 -0.83, 2024 -0.86, 2025 +0.11 (0.39).

**Suggested change.** State that the 2025 rebound is confined to E1 and to acquisition-affected or compute-infrastructure firm-years, give the E2 and ex-flagged values beside it, and add the 2025 slope reversal next to the "steepening" statement in Section 5.3. Add one sentence to the abstract: the 2023-24 trough is partly reversed in E1 in 2025.

### N4. Medium. The abstract's "about a fifth of a point" pools a documented break, has no interval, and its sign fails the familywise test
*Role: QR. Location:* abstract; intro; Section 5.3; Section 5.10 (i); Section 9; Table 2.

**Issue.** The pooled Psi0.90 slope over 0 to 60% growth is -0.22 (0.11) on GAAP and -0.16 (0.10) after SBC. The paper itself shows (a) that the GAAP slope was -0.22 before 2020 and -0.60 after (difference -0.38, Holm 0.037 to 0.060), (b) that the window matters (0 to 40%: -0.31 and -0.27), (c) that the sign does not survive Holm (0.26 to 0.45 GAAP, 0.35 to 0.62 cash). The abstract nevertheless states the pooled point estimate as a result.

**Evidence** (`t4_slopes.py`, 400 draws): GAAP pooled 0 to 60% -0.215 (SE 0.112), 90% [-0.422, -0.047]; 2010-19 -0.215; 2020-25 -0.596 [-0.794, -0.413]; 2020-24 -0.626 [-0.790, -0.429]; 2023-25 (window 0 to 30%) -0.572. Cash: pooled -0.161 [-0.304, +0.008]; 2020-25 -0.347. The 2020-25 GAAP slope lies 3.6 standard errors from -1 and 5.3 from 0, so the post-2020 relation is closer to a 0.6-for-1 trade than to the "fifth" quoted. The only supported statement is that the slope is far above -1 (Holm 0.028 for the pooled E1 test, a strawman since Proposition 3 already says the cross-section does not identify a firm's slope).

**Suggested change.** Quote the slope with its interval and period: "-0.2 before 2020 and -0.6 from 2020 on, GAAP; the sign does not survive a familywise correction". Remove "about a fifth of a point less margin" from the abstract and conclusion.

### N5. Medium. Multiplicity statements overstate the familywise result; the 14-member family contains tautological tests
*Role: QR. Location:* Section 5.2 (p.38); abstract (11.9 to 12.7); Section 5.1 and `notes/inference_v3.md` section 5 (family B).

**Issue.** (a) Section 5.2 says the Holm-adjusted p-value of the GAAP decline is "0.054 to 0.208 across interval types (Romano-Wolf 0.097), so it survives at a familywise level of 10% but not 5%". The top of that range, 0.208 (basic), fails 10%. `inference_v3.md` line 276 confirms that the basic-interval Holm survivor list at 10% omits `p95chg_op_E1`. (b) The abstract gives the cash decline (12.7) the same standing as the GAAP decline, but its Holm p is 0.154 (percentile), 0.155 (normal), 0.336 (basic) and Romano-Wolf 0.154: it fails even at 10%. (c) Of the five Holm survivors at 5% under the normal type in family B, two are tests against a slope of -1 (a null nobody holds), two are the "near-frontier margin gap" and its selling-and-marketing component (the top decile of margin minus the 40th to 60th percentile of the same margin is positive by construction, and the component is an accounting identity of operating margin), and one is the steepening. (d) The family of 14 is chosen after the fact; the real denominator includes 22 samples, four views, two bases, the chi-by-window grid, interval types and period splits.

**Evidence.** `notes/inference_v3.md` lines 258 to 276 (rows "Change in P95, GAAP, E1" Holm normal 0.054, percentile 0.060, basic 0.208, RW 0.097; "FCF after SBC" 0.155, 0.154, 0.336, RW 0.154); survivor lists lines 275 to 276.

**Suggested change.** Correct the 10% sentence ("under the normal, percentile and Romano-Wolf procedures, not the basic one"). State the cash decline's familywise p beside the GAAP one in the abstract or drop the "to 12.7". Remove the tautological members from the family and count the remaining ones; pre-state P95 change as the single confirmatory test and the rest as exploratory, with the full denominator of variants in a table.

### N6. High. The anchor is 13 firm-years from 7 firms, no interval is given on the intercept, and the headline score inherits it
*Role: RM, QR. Location:* abstract ("scores about 66"); Section 5.8; Section 7.3 (p.53 to 55), Table 5, Table 6; Section 9.

**Issue.** The anchor now rests on 13 firm-years of 7 firms (round 1: 20 and 12). Clear Secure (3) and Duolingo (3) supply 6 of the 13; Global-E and monday.com 2 each; Cellebrite, CrowdStrike and Palantir 1 each. The rule drops 9 of the 22 firm-years in the E1 tail (41%) as acquisition-affected, so "the top tail" is the non-acquisitive remainder. The paper puts a firm-cluster interval on the surplus Pi but not on the intercept m0, which is the quantity that drives Table 5 (m0 = 42 in 2025, 53 in 2036). Tornado row "anchor intercept: lower and upper quartile" (63 to 72) is the dispersion across firm-years, not the sampling error of the median. With 7 clusters a bootstrap draw contains on average 4.6 distinct firms.

**Evidence** (`t6_anchor.py`, 2,000 firm-cluster draws): median m0 (all selling and marketing buys growth) 42.0, 90% [34.1, 52.4]; third-quartile m0 51.8 [42.0, 63.7]; median Pi_ub -1.3 [-17.3, +16.0] (paper -18.2 to +16.4). Using the paper's Table 5 mechanics (m0(t) = m0A + realised share x (m0F - m0A) + G; 2036: share 0.41, m0F 70, G 12.7; 2028: share 0.07, m0F 64): 2036 score 66 becomes about 61.5 at the lower bound and 72.3 at the upper; 2028 score 56 becomes 49 to 66. These are my reconstructions of the table's formula, not paper figures. Leave-one-firm-out median Pi_ub in the paper's JSON: -0.095 to -0.012.

**Suggested change.** Add the firm-cluster interval for the median and quartile intercepts and carry it into Table 5 and the abstract ("about 66, with an anchor-sampling range of roughly 62 to 72"). Use a wild or small-cluster-corrected bootstrap, or report the leave-one-firm-out range beside the interval. Say how many of the 13 are two firms.

### N7. Medium. The headline uses the "all selling and marketing buys growth" bound, which the paper's own maintenance-spend evidence contradicts
*Role: FA. Location:* Section 7.3 (Table 5 "All selling and marketing buys growth" columns); abstract (66); Section 5.4 (maintenance netting gives 0.99).

**Issue.** The upper-bound intercept adds back 0.82 of the whole selling-and-marketing share to the margin, as if the firm could cut it to zero while growing with its market. Section 5.4 shows that firm-years growing at or below the year's median already spend a large share on selling and marketing, and that netting that out cuts the spend ratio to 0.99. The abstract uses the bound that this evidence undermines, and the 55 (no S&M buys growth) is only in the table.

**Evidence** (`t13_maint.py`): median selling and marketing share of revenue among firm-years growing at or below the year median, 2023-25: 25.1% (all years 24.9%). Anchor median share 19.8%; only 5 of 13 anchor firm-years (38%) exceed the base. Median anchor intercept: all-S&M bound 42.0; netted of the maintenance base 30.6; none 24.1. Implied 2036 durable score on the Table 5 mechanics: 66.2, 59.5 and 55.7.

**Suggested change.** Put the maintenance-netted case in Table 5 as the middle column, and quote the abstract score as a range across the three, or use the netted case as central. Say in the abstract that the 66 is the upper of the paper's two bounds.

### N8. Medium. The cash-basis intercept carries non-operating and billing-timing inflows that the model's margin does not contain
*Role: RM, FA. Location:* Section 4.3 (cash margin definition); Section 4.6; Section 7.3 anchor; response rows R3-18 and FR-11 ("not addressed", deferred revenue and cash-flow elements).

**Issue.** The cash margin is operating cash flow less capital spending and SBC. Operating cash flow includes interest received and the growth in deferred revenue. The B5 bridge adds back interest paid and cash taxes but nothing for interest income or billing timing. The anchor intercept m0 is built on this margin. The model's intercept is the operating margin at market growth, and billing inflows grow with billings, so they scale with g, not G. The panel has no interest income, deferred revenue or D&A column, so I could not decompose the wedge; this is a data request.

**Evidence** (`t6_anchor.py`): the wedge (FCF-after-SBC margin minus GAAP operating margin) has a median of 13.4 points over the 13 anchor firm-years (Clear Secure 2023 23.2; Global-E 2024 26.0; monday.com 19.6 and 19.3). Median wedge in the top 5% by cash score: 4.3 (2010-15), 3.7 (2016-19), 11.8 (2020-22), 13.0 (2023-25); the all-firm median wedge rose only from 2.6 to 3.9. The tail wedge tripled between the two periods the paper compares, so the cash-basis fall of 12.7 points nets a rising non-operating component.

**Suggested change.** Add interest income received and the change in deferred revenue to the extract (the existing InterestPaid retrieval path in `data/v3_inputs/` would serve). Report the P95 change and the anchor intercept on cash flow before interest income and billing timing, as a bridge row next to Table S6.

### N9. Medium. The spend ratio is mostly the ratio of two marginals, and the Section 8.1 illustration uses its high end
*Role: QR, FA. Location:* Section 5.4; Section 8.1 (p.59); Section 9 ("a firm ... should accept a lower Rule-of-40 score"); Table 2 spend row.

**Issue.** The statistic is the median over firm-years with g above the year median of (lagged selling and marketing share) / (g minus that median). It is large when excess growth is small and falls with excess growth by construction. It would be about 2.5 with no link between spending and growth. Section 8.1 then says that at a ratio of 3.02 "an asset-light firm growing 10 points faster than its market scores about 20 points below the score it would earn with no growth spend", and concludes that "a fixed threshold ... marks down firms whose growth spending earns more than it costs". The 3.02 is the gross ratio; the paper's own net-of-maintenance ratio is 0.99, for which the same formula gives 10 x (1 - 0.99) = about 0 points.

**Evidence** (`t8_spend.py`): 3.02 reproduced (n = 836). By tercile of excess growth: 10.09, 3.04, 1.46 (median excess 3.5, 12.2, 29.0 points; median S&M share 0.32, 0.40, 0.47). Spearman correlation between S&M share and excess growth among g above median: 0.21. Within-year permutation of S&M shares across firm-years (500 draws): median ratio 2.50, 5 to 95% [2.38, 2.62], against 3.02. By year: 2.14 (2017) to 4.72 (2025); by period 2.61, 2.75, 2.78, 4.25.

**Suggested change.** Report the permutation benchmark beside the ratio and drop "robust"; state the by-period values. In Section 8.1, replace the 20-point illustration by the range implied by the bounds (about 0 at 0.99, 10 x (1 - 3.02) = -20 at 3.02, positive for the regression slopes 0.05 to 0.24), or remove the sentence that a threshold "marks down firms whose growth spending earns more than it costs".

### N10. Low. The four D-3 views are not independent checks, and the imputation "bounds" are not bounds for the cheap acquisitions that rule R4(b) targets
*Role: QR. Location:* Section 4.5; Table 2 last column; Section 5.9.

**Issue.** E1 (1,788 firm-years), E2 plus imputation at M = 4 and at M = 8 (1,786 each) differ only in the growth of the 466 acquisition-affected firm-years; E2 (1,378) is a subset of E1 that drops 88% of those. "Holds in all four" is close to "holds in E1 and in two adjustments of E1". The imputation removes acquired revenue equal to price / M, half in each of two years. Rule R4(b) flags acquisitions with price at most one times revenue; at M = 4 or 8 the imputed acquired growth is at most a quarter or an eighth of that implied by price / 1, so the imputation understates, not bounds, acquired growth for those years (13 new acquisition years and 7 following years). Section 6 itself reports serial-acquirer multiples of 1.7 to 3.2.

**Suggested change.** Present D-3 as a sensitivity set, not a four-fold replication. Add M = 1 and M = 2 columns, or label M = 4 and 8 as scenarios. Report the number of firm-years each view shares with E1.

### N11. Low. Universe selection: current SIC, a latest-filed revenue screen, R2 only on named firms; numerically small, but the SIC 7372 restriction matters for how far the decline generalises
*Role: QR, FA. Location:* Section 4.1; Section 8.6; S6 first paragraph.

**Evidence.** Survivorship passes: 60 of the 140 firms in 2016-19 (43%) have no firm-year after 2022, including 6 of the 15 firms in the top 5% by cash score; the last observed firm-year of an exiting firm has a median cash margin of -0.8% against 3.7% for other firm-years; the decline holds among 80 stayers (N2). Frames look-ahead is numerically negligible: on all 1,788 rows the latest-filed frames revenue equals the first-reported revenue to the digit in more than 95% of rows (median ratio 1.000), 10 firm-years (0.6%) are below 70% of the first-reported value (discontinued-operations restatements: Gen Digital, Progress, Nuance, McAfee, Moatable, i3 Verticals), and 2.3% of rows have a growth rate that differs by more than 5 points; substituting latest-filed growth leaves the P95 change at -11.9. The remaining exposures: the 662-firm universe is cut at "ever reports at least $50 million" using frames (latest-filed) revenue; SIC codes are current; R2 can be applied only to the 16 named firms (CoreWeave, Take-Two, Roblox and Unity stay in); R3 relies on XBRL elements retired for 2024 to 2026. Among the 3,641 EDGAR registrants, MicroStrategy (CIK 1050446), Fair Isaac (814547) and Digital Turbine (317788) are absent from `sic_universe.json` and Aspen Technology is SIC 7371; I could not check their EDGAR SIC (sec.gov is not reachable from this sandbox), so I cannot say that this is drift. The P95 change in the other four SIC codes of the same universe (247 firms, same rules) is GAAP -4.8 [-19.0, +10.6] and cash -9.4 [-18.9, +0.6], against -11.9 and -12.7 for SIC 7372; the 7372-minus-others difference, -7.1 [-25.7, +8.1] on GAAP, is not distinguishable from zero (`t14_sic_2025.py`).

**Suggested change.** Say in Section 4.1 that the $50 million universe screen and the SIC code use data later than the observation date, and that the decline is not shown to be specific to SIC 7372 or to software. Add the broader-universe P95 change to Table S2.

### N12. Low. Bookkeeping: the assumptions register still lists alpha as class c; the response's IM-6 row is empty; the "5 to 15" decision weight echoes the withdrawn 7 to 13
*Role: RM. Location:* `notes/assumptions_register.md` lines 62 and 243; `response_to_reviewers.md` IM-6 row; Section 8.1.

**Issue.** The paper (Table S7) and the register disagree on alpha's class, and the register is part of the package. The IM-6 notes cell is blank. Section 8.1 states "the worked example gives 5 to 15" for the decision weight; this is a valuation-multiple example, but a reader will take it as the successor of the withdrawn figure.

**Suggested change.** Update the register line to class d; fill the response cell; in Section 8.1 write "a decision weight equal to the revenue multiple, 5 to 15 in the example; not an estimate from the data".

---

## 3. Screening use

**Can the paper be used to build a screen or a factor? Not as it stands.** The paper's usable contributions to a screen are definitional: the cash score after SBC and capital spending including capitalised software; the organic versus charged treatment of acquired growth (Remark 3, Section 6); and the red-flag list in Section 8.3. None is tested as a signal.

**Evidence from the panel on usability** (`t9_screen.py`, `t16_t7_t10_v3.py`):

- Breadth is low: 94 to 168 firm-years per fiscal year after 2015, so a top quintile is 19 to 33 names. The sample is public SIC 7372 firms with prior-year revenue of at least $100M.
- Persistence and turnover: mean year-to-year rank autocorrelation of the cash score 0.68 and top-quintile turnover 43%; at a growth weight of 2 and 3 the rank autocorrelation is 0.64 and turnover 50% and 52%; margin alone 0.84 and 26%; growth alone 0.67 and 47%. Higher growth weight means more turnover.
- Predictive content (train 2011-18, test 2019-24): next-year cash score on the current cash score R2 0.49, on growth and margin entered separately 0.51; next-year growth on the cash score 0.03, on growth alone 0.42. The sum adds nothing over its components, and the split into durable and transient parts adds 0.016 over the score and nothing over growth and margin (T7 above).
- Growth versus margin persistence: in a regression of next-year cash score on current growth and margin the coefficients are 0.54 and 0.70 (ratio 0.77). Nothing in the paper estimates the weight of 2 to 3 that Lemma 5 maps to a ten-year runway; with persistence this low for growth, a screen weight above 1 needs its own evidence.
- Timing: the first-reported annual data are filed a median 57 days after fiscal year end (P90 77, P99 119), so an annual score is stale by up to about 14 months. The panel carries `filed`, which is good; it carries no quarterly data.
- E2 cannot be implemented in a screen. It drops 88% of acquisition-affected firm-years (408 of 466), and that share of the E1 top-5% cash bucket is 38 to 59% by period (T10). Acquisitions paid in stock or tagged only on a business-combination axis are undetected, so the flag has false negatives in real time.
- Licence: CC BY-NC-ND 4.0 and PolyForm Noncommercial prevent commercial factor use of the text and code without permission.

**What is missing for a screen or factor.**
1. Prices, returns, market capitalisation, delisting returns and point-in-time share counts, so that the score can be tested against forward returns and against valuation multiples (the response declines the score-to-multiple bridge, IB-2; IM-7 is not done).
2. A holdout and a rolling out-of-sample design: signal formed from filings public by date t, with the 57-day typical and 119-day tail lags, tested on returns after the filing date.
3. Quarterly and trailing-twelve-month data, since the annual score is too slow for a signal.
4. Point-in-time industry classification (SIC is current) and a rule-based software classifier for all registrants (R2 exists for 16 firms only).
5. Cross-sectional breadth and size controls: a test within size terciles, since the paper's own size gradient is weak and unstable, and a long-short spread net of transaction costs and turnover.
6. A pre-registered screen definition: the weight X, the basis (GAAP, adjusted, cash), the organic treatment, and a multiplicity budget for the variants.

**Statements a quant would consider unsupported.**

| Statement (location) | Why unsupported | Fix |
|---|---|---|
| "Use the Rule of 40 to screen firms, not to set growth spending" (Section 9; also Section 8.1) | No returns, valuation or holdout evidence in the paper; the response lists IM-7 as not done; the only cited study is Lee (2024) | State plainly that the paper does not test the score as a screen; delete or soften |
| "the 95th percentile ... fell ... as fast growers became scarcer ... with no detectable change in the margins attainable at a given growth rate" (abstract, intro, 5.10, 7.4, 9) | See N1 and N2 | See N1 and N2 |
| "among the best performers a point of growth came with about a fifth of a point less margin" (abstract, intro, 5.3, 9) | Pooled over a break; sign fails Holm; no interval | N4 |
| "the top recovered in 2025" (intro, 5.2, 5.10, 9) | E1 only, ex-flagged recovery 2.8 points | N3 |
| "scores about 66" (abstract); "56 in 2028, 60 in 2031 and 66 in 2036" (Section 7.3, 9) | Anchor of 13 firm-years from 7 firms, no interval on the intercept, upper S&M bound | N6, N7 |
| A fixed threshold "marks down firms whose growth spending earns more than it costs" (Section 8.1) | Rests on the gross spend ratio 3.02; net ratio 0.99; the ratio is about 2.5 under random pairing | N9 |
| "We suggest computing the score ... on annual free cash flow after SBC and after capital expenditure including capitalized software" (Section 8.3, 9) | A definitional preference; no evidence it ranks firms better than the other bases; the cash margin carries a rising non-operating wedge in the tail | N8; add a comparison of bases against forward outcomes |
| "Execution sets the pace ... not technology" (abstract, 8.2) | Rests on scenario values (class d) the paper itself lists; the abstract does not carry the class | Add "under scenario values" to the abstract sentence |

---

## 4. Recommendation

**Major revision of the empirical sections; do not release to practitioners as a screening or factor reference until the items below are done.** The data and inference layer is much improved: the sample is first-reported, survivorship and backfill are controlled, the interval work is documented, and several round-1 claims were correctly withdrawn. What the next version needs:

1. Replace "no detectable change in margins at a given growth rate" by a statement that the data cannot separate composition from a roughly 10-point fall in the best margins of 20%+ growers, with all four interval types (N1). Report the decomposition across bin counts and directions, state that the score fell across the distribution, and add the cyclical and IPO-window alternative (N2). Qualify the 2025 recovery (N3).
2. Put intervals on the anchor intercept and on the Table 5 headline, add the maintenance-netted case, and quote the 66 and 56 as ranges (N6, N7). Add interest income and deferred revenue to the extract and show a bridge (N8).
3. Fix the multiplicity statements and drop tautological tests from the family (N5). Stop quoting the pooled slope without period and interval (N4). Add the permutation benchmark to the spend ratio and correct the Section 8.1 illustration (N9).
4. Say that the paper does not test the score as a screen, and either remove "use the Rule of 40 to screen firms" or add a returns and holdout section (Section 3). If the author wants a screen, the minimum is a point-in-time panel with prices, a rolling holdout and an organic or charged-acquisition variant that a screen can compute in real time.
5. Housekeeping: register class for alpha, response cell for IM-6, D-3 wording (N10, N11, N12).

---

## 5. Scripts run

All scripts are in `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/` and read only the repository files named above (run with `python3 -I`). Bootstrap draws are firm-cluster, with seeds fixed in each script; they will differ in the last digit from the paper's 999-draw runs.

| Script | Purpose | Used for |
|---|---|---|
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/common.py` | Loader (E1 = `panel_v3.csv`, scores R_op and R_cash), quantile and bootstrap helpers | all |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/fastlib.py` | Dominance-cone Psi slope and numpy cluster bootstrap (replicates `estimate_v3.py` `cone_mat`, `wslope`) | N4, N6, N11 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t0_reproduce.py` | Reproduces P95 levels and changes, sample counts | IM-1 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t1_backfill.py` | R1 exclusions, residual backfill check, filing lags, entry-year effect | IM-1, N2 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t1b_universe.py` | SIC 7370-7374 universe comparison, exits and exit-year margins | N11 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t1c_coverage.py`, `t1d_coverage2.py`, `t1e_cik.py` | Universe coverage spot checks by name and CIK | N11 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t2_yearly.py` | Annual P95, top names by year, growth quantiles by period | IM-2, N2, N3 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t3_composition.py` | Reweighting decomposition across bin counts and directions, bootstrap; margin by growth group | N1, N2 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t3b_frontier_points.py`, `t3c_frontier_points_allfirms.py` | Change in the chi-quantile of margin among g at least g0; bootstrap drawing from all E1 firms | N1 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t4_slopes.py` | Psi0.90 slopes by period, SEs, distance from -1 | IM-2, N4 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t5_capint.py` | Capital-intensity gap: same-year, prior-year, firm-median sorts; add-back; E1 and E2 proxy | IM-3 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t6_anchor.py` | Anchor firm-years, intercept intervals, wedge, next-year check | IM-4, N6, N8 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t7_stayers.py` | Stayers, real threshold, entrant versus incumbent, firm-average P95 (its line labelled "real $100M (2025$)" is not a valid test and is not used) | IM-1, N2 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t8_spend.py` | Spend ratio by period, year, tercile; within-year permutation | IM-5, N9 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t9_screen.py` | Breadth, rank persistence, turnover, out-of-sample R2, filing lags | Section 3 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t10_frames.py` | Latest-filed frames versus first-reported revenue and growth | N11 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t11_jackknife.py` | Leave-one-firm-out P95 change; quantile-process changes | N2 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t12_trim.py` | Growth and margin trimming bounds; eligibility gaps | hygiene (no effect found) |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t13_maint.py` | Maintenance-netted anchor intercept | N7 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t14_sic_2025.py` | SIC 7372 versus other SIC P95 change with bootstrap; 2025 P95 excluding flagged firm-years | N3, N11 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t15_json_extract.py` | Reads `notes/empirics_v3.json`: interval types for T(g0) and P95 changes; anchor block | N1, N5, N6 |
| `/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/r2_im/t16_t7_t10_v3.py` | Round-1 T7 and T10 specifications on panel_v3 | Section 1.2 |

**Limits of these checks.** (i) My bootstraps use B = 400 to 2,000 against the paper's 999, and some draw only from firms present in the periods compared; the paper draws from all 292 E1 firms. I used the paper's own JSON for the interval-type comparisons (N1, N5). (ii) The Table 5 reconstructions in N6 and N7 assume the table's stated formula and the printed inputs (realised share, m0F, G); they were not re-run through `calibrate_horizons.py`. (iii) I could not retrieve EDGAR SIC codes or any interest-income or deferred-revenue series (N8, N11); those need a data request. (iv) No price or return data were available, so nothing here bears on expected returns.
