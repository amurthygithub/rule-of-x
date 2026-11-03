# Referee 3 report: econometrics of the empirical frontier

**Summary.** Section 5 estimates order-alpha/order-m "Pareto" frontiers of margin on growth (3,842 firm-years) and reports a flat frontier, a frontier score of 85 to 130 that falls steeply with size and has not shifted since 2016, alpha of 0.2 to 0.45 and rising inefficiency; these feed the Section 6 calibration. The data work is careful and transparent. But the headline statistic is an extreme order statistic whose value depends on sample size, so the scale gradient, "no measurable shift" and the capital-intensity "halving" do not hold up, and alpha is not identified under the model's own assumptions. Scripts and outputs: `notes/referee3/` (check1 to check9).

**Recommendation: major revision.** Every fix below uses the existing data.

## MAJOR

**1. The frontier score is not a well-behaved estimand (Section 5.1, Table frontier).**
- **What it measures.** phi_0.95 is roughly flat, so g + phi(g) rises with g and the argmax sits at the last grid point with N≥30 in 16 of 16 cells. The score is in effect "growth of about the 30th-fastest firm-year plus the second-highest margin among the top 30". Two firm-years pin it: Meta 2011 and Baidu 2010 (2010-15). In 2023-25, Exzeo 2025 pins it alone (GAAP).
- **It depends on MIN_N.** GAAP score by MIN_N (a 0.01 grid adds up to 10 points):

  | MIN_N | 15 | 30 | 50 | 100 |
  |---|---|---|---|---|
  | 2010-15 | 129 | 129 | 102 | 86 |
  | 2023-25 | 123 | 89 | 74 | 49 |

- **The bootstrap is invalid.** Bootstrapping an extreme order statistic maximised over a non-smooth grid is a known failure case (Bickel-Freedman; Andrews 2000; Fang-Santos 2019). Here duplicated firms push the edge outward, the bootstrap argmax lands at the edge in 71 to 98% of draws, and the bootstrap mean is 1 to 8 points below the estimate in all 8 cells. The [-40, +31] shift interval reflects zero power, not evidence of no shift.
- **Fix.** Headline statistics that do not depend on sample size: fixed thresholds g0 + phi_0.95(g0), an edge at a fixed sample share, or upper quantiles of R. Use subsampling or an m-out-of-n bootstrap for any extreme-type statistic.
- **My results.** Change from 2016-19 to 2023-25 (firm-cluster bootstrap, 1,000 draws), 90% interval in brackets:

  | Statistic | GAAP | FCF after SBC |
  |---|---|---|
  | P90 of R | -9 [-13, -5] | -10 [-14, -6] |
  | P95 of R | -15 [-22, -7] | -13 [-23, -6] |
  | Firm-mean P95 of R | -18 [-33, -4] | -17 [-31, -8] |
  | T20: 0.2 + phi(0.2) | -5 [-12, +11] | -3 [-8, +5] |
  | T30: 0.3 + phi(0.3) | -4 [-18, +29] | +1 [-10, +28] |

  Top margins at a given growth rate are stable (T20, T30), but the top of the score distribution fell significantly, by 9 to 18 points, as fewer firms grow fast. This fits the growth-supply story but contradicts "not measurably moved".

**2. The scale result is mostly a sample-size artefact (Section 5.4, Table and Figure scale).**
- With MIN_N=30, the edge sits at the 1.6% upper growth quantile in the smallest class (N=1,882) but at the 22% quantile in the largest (N=139).
- **Equal-N subsampling** (firm clusters drawn to 139 firm-years; 157 for FCF after SBC). The gradient disappears:

  | Size class | GAAP, paper | GAAP, equal N | FCF after SBC, paper | FCF after SBC, equal N |
  |---|---|---|---|---|
  | $0.1-0.5B | 126 | 56 | 134 | 60 |
  | $0.5-2B | 116 | 54 | 109 | 53 |
  | $2-10B | 77 | 50 | 69 | 49 |
  | >$10B | 60 | 60 | 48 | 48 |

- **N-invariant statistics.** The table's own P95 of R is not monotone (GAAP 69/63/54/64; FCF after SBC 68/61/52/57). The top-5%-edge score declines on cash (102/94/79/63), not on GAAP (95/97/85/81). The tau=0.95 log-size slope is -0.030 (cluster SE 0.013), about 7 points per tenfold revenue, and insignificant on GAAP.
- **Fix.** Restate "falls steeply with firm size" (abstract, introduction) as a modest decline on the cash basis only.

**3. The flat frontier survives in shape, not at the stated strength (Sections 5.3 and 5.5, Tables envelope and qreg).**
- **One observation per firm** (firm-period means, medians or a random single year): slopes stay between -0.36 and +0.06, so "not one-for-one" holds. Scores fall 20 to 45 points (firm means: 64 to 86).
- **Bootstrap slope SEs** are 0.09 to 0.15 in 2010-22 but 0.37 to 0.53 in 2023-25, so the "rising" 2023-25 slopes (+0.24, +0.31) are noise.
- **Upper-set phi hides a decline in the bulk of the data.** Pooled GAAP local q90 falls from 0.29 (g 0-10%) to 0.20 (30-40%), then rises to 0.26 above 60%. Quantile regressions agree:
  - on g in [0, 1]: g = -0.62 (SE 0.24 to 0.31), g² = +0.77 to +0.89;
  - linear on [0, 0.6]: slope -0.13 to -0.21 (SE about 0.10).

  The current specification includes shrinking firms (g<0), outside the model, and its collinear g and g² terms are informative only jointly. Log size is a bad control under saturation; without it, GAAP g² is -0.139 (0.095).
- **Composition.** Excluding SIC 7370 (Meta, Baidu, AppLovin, Trade Desk) cuts scores by 15 to 30 points and turns slopes to -0.33 to +0.05.
- **The post-2022 rotation** rests on 13 firm-years. Dropping AppLovin and Palantir moves post×g from 0.32 to 0.19 (FCF), 0.22 to 0.14 (FCF after SBC) and 0.13 to 0.00 (GAAP).
- **Fix.** Report local conditional quantiles, restrict to g ≥ 0 and report marginal effects. Confine "complements" to the extreme growth tail. Describe the rotation as driven by a few firms.

**4. Alpha is not a structural elasticity (Section 5.3; Section 6 uses alpha=0.25).**
- **Why the regression cannot recover alpha.** Under Proposition optimum, sigma* = alpha(X−k)Delta*. With optimizing firms, log Delta moves one-for-one with log sigma, so the slope is 1 for any alpha (my simulation: 1.00 at both 0.25 and 0.45). The selection used (g above the median, log(g − median)) raises it to 1.7 to 1.9. Measurement error in sigma lowers it. The estimate of 0.20 mostly measures attenuation from a noisy S&M proxy (residual SD 1.18 log points).
- **The levels contradict the model.**
  - Median sigma/Delta among the selected firm-years is 2.53, which implies alpha of about 2.5 at X=1.
  - The calibrated optimum is sigma* = 2.5% of revenue, against an observed median S&M share of 34%.
  - Unrestricted NLS in levels on all organic firm-years gives alpha of 1.57 to 1.72 (90% CI 1.41 to 2.04).
  - Binned excess growth is convex in S&M share.
- **Fix.** Present "strongly diminishing returns, alpha 0.2 to 0.45" (Summary ii, abstract, introduction) as an assumption, not an estimate; the 0.43 (0.23) firm-effects figure includes 94 singleton firms out of 387. Identification needs spend variation unrelated to opportunity (financing shocks, lockup timing).

**5. Calibration (Section 6, Table calib).**
- **lambda·h=0.25** is reported nowhere in Section 5. It equals the smeared arithmetic mean (smearing factor 1.74) from a sample of above-median growers. The geometric mean is 0.14 to 0.15 and the median 0.17. Call 0.15 "typical".
- **"Exceptional" pull has no anchor.** The implied lambda·h has p90=0.56, p95=0.78, p99=1.36. The 2025 range of 1.0 to 1.5 sits at about p97 to p99.5; the 2028 range of 1.5 to 2.5 lies outside the sample. The 2025 "bracketing" is also circular: it targets a frontier score that ranges from 49 to 123 depending on MIN_N.
- **Sensitivity to alpha** from 0.20 to 0.45, lambda·h fixed (exceptional, k=0):

  | Horizon | alpha=0.20 | alpha=0.45 |
  |---|---|---|
  | 2025 | 91-127 | 67-98 |
  | 2028 | 129-228 | 100-211 |
  | 2031 | 101-202 | 77-176 |
  | 2036 | 72-183 | 58-154 |

  Typical pull in 2025 moves from 47 to 40; the lambda·h needed for R*=1000 moves from 9.8 to 6.8. If lambda·h is re-solved to keep 2025 at 85 to 119, the 2028 range runs from 120-211 to 130-287.
- **Fix.** Publish this sensitivity table. Use one consistent (alpha, lambda·h) pair. Report g* (73 to 118% in 2025, against an empirical growth support of 40%).

**6. Capital intensity (Section 5.6; Summary iv; abstract).**
- **Uncertainty.** The 2023-25 frontier-score gap (capital-intensive minus capital-light) is -42 [-64, -8] on FCF after SBC and -41 [-67, +2] on GAAP; only 12 or 13 capital-intensive firm-years grow 40% or more. On P95 of R it is -14 [-21, -9] (cash) and -4 [-16, +4] (GAAP).
- **The gap reflects composition, not capex.** The GAAP gap (89 vs 48) matches the cash gap, yet GAAP margins exclude capex.
- **Fix.** Drop "halved". Report the P95 gap and treat it as a difference in which firms fall in each half.

**7. Stochastic frontier (Section 5.7).**
- Each period is a pooled cross-section that ignores the panel. The bootstrap confirms the overall rise (GAAP +11.5 [6.8, 17.0]; FCF after SBC +7.8 [3.2, 13.9]).
- **New entrants drive it.** For firms in the sample before 2019, 2023-25 inefficiency is 18 (GAAP) and 9 (FCF after SBC), against 14 in 2010-15. 79% of 2023-25 firm-years with GAAP margin below -20% belong to 2019-or-later entrants. For firms present in both periods, the 2023-25 FCF-after-SBC residual skew is +0.55 and sigma_u collapses to 0.001.
- **Fix.** Use a panel SFA (true fixed or random effects) with cohort controls, or reword as "the median moved away as new firms entered".

## MINOR
1. The acquisition flag misses DXC 2017 (g=186%, merger) and RideNow 2019 (reverse merger). For 13.7% of g≥50% firm-years, both acquisition variables are missing.
2. Foreign private issuers filing under US GAAP (Baidu, JOYY, Weibo, Hello Group, Yalla, Qihoo) supply many edge points, and their growth includes currency effects. "U.S. public software" (conclusion) is inaccurate.
3. Unlike FDH, order-alpha is not monotone; a rising phi_alpha describes the growth tail's composition, and Aragon et al. asymptotics do not cover 30-observation conditioning sets.
4. Use cluster SEs, not iid, for the capital-intensity and scale quantile regressions.
5. The within-firm effect survives excluding acquisitions (GAAP 0.129, SE 0.040); say so.

## ERRORS
1. Section 5.3 says GAAP frontier scores are "93 to 129"; Table frontier gives 89 to 129.
2. Section 5.2 says "the 90th percentile moved much less". From 2010-15 to 2023-25, GAAP P90 fell 17.0 points against 12.1 for the median; on FCF after SBC, 18.4 against 9.8.
3. Section 5.7 calls sigma_u a standard deviation. It is the half-normal scale; SD = 0.60 sigma_u. The GAAP mean shortfall series is 16, 25, 30, 27.
4. The Table calib note calls lambda·h=0.25 "the pooled estimate", but no such estimate is reported.
5. The abstract, introduction and Summary (i)-(v) overstate the evidence ("falls steeply with size", "not measurably moved", "halved", "strongly diminishing returns"). Reword them to match Issues 1 to 6.
