# Reliability-Engineering / ICFR Audit — "The Rule of 40 as a Price Line"

**Auditor:** reliability-auditor (referee team)
**Scope:** Proposition 5 ("accountability floor"), Assumption 7, Definition 3, Section 8.5, and the supplement's S2.6, Proof of Proposition 5, and Remark S10 (Tables S15/S16).
**Verdict summary:** The paper's regulatory citations are **accurate**; the model is **mathematically correct**; the core common-mode claim is **logically valid as a conditional/structural result**; the illustrative numbers **reproduce exactly**; and the "accountability floor" is **sound as a stylized construct**, with the paper correctly separating regulatory fact from modeling assumption from scenario value. Two minor flags (one pinpoint imprecision, one loose phrase) are noted and are not material.

---

## 1. Regulatory accuracy

### 1(i) AS 2201 A7 — material-weakness definition — **CORRECT (verbatim, correct paragraph)**

PCAOB AS 2201, Appendix A, paragraph **A7** states (verified against the archived PCAOB standard text):

> "A material weakness is a deficiency, or a combination of deficiencies, in internal control over financial reporting, such that there is a reasonable possibility that a material misstatement of the company's annual or interim financial statements will not be prevented or detected on a timely basis."

This is an **exact match** to the paper's quote, and the paragraph number **A7** is correct. (Note: in the predecessor AS 5 the definition sat at A4/A5; the recodified AS 2201 numbers it A7. The paper's cite is right for the standard it names.)

### 1(ii) Regulation S-K Item 308(a)(3) — **CORRECT (verbatim)**

Verified against 17 C.F.R. § 229.308(a)(3):

> "Management is not permitted to conclude that the registrant's internal control over financial reporting is effective if there are one or more material weaknesses in the registrant's internal control over financial reporting."

Exact match. AS 2201 itself cross-references this exact provision (footnote 2 of Appendix A cites "17 C.F.R. §§ 228.308(a)(3) and 229.308(a)(3)").

### 1(iii) "Reasonable possibility" ↔ FAS 5 / ASC 450 — **CORRECT (verbatim mapping)**

AS 2201 Appendix A attaches the following note to A7 (verified):

> "There is a reasonable possibility of an event, as used in this standard, when the likelihood of the event is either 'reasonably possible' or 'probable,' as those terms are used in Financial Accounting Standards Board Statement No. 5, Accounting for Contingencies ('FAS 5')."

The standard's footnote 3 reads "See FAS 5, paragraph 3." FAS 5 ¶3 (retained in ASC 450-20-20 Glossary) defines the three likelihood categories **qualitatively, with no numbers**:

- **Probable** — "The future event or events are likely to occur."
- **Reasonably possible** — "The chance of the future event or events occurring is more than remote but less than likely."
- **Remote** — "The chance of the future event or events occurring is slight."

The paper's statement that "reasonable possibility means the event is 'reasonably possible' or 'probable' in the terms of FAS 5" is therefore **correct**, and the paper's mapping is the standard one, not an invention.

### 1(iv) Section 404(b) attestation scope — **CORRECT**

Verified against 17 C.F.R. § 229.308(b): the registrant must provide the auditor's attestation report if it "other than a registrant that is an **emerging growth company** … is an **accelerated filer or a large accelerated filer**." The paper's statement (accelerated/large-accelerated, excluding EGCs) is **correct**, as is its additional claim that a newly public company's first annual report need not contain management's assessment (Item 308 Instruction 1: a registrant need not comply with ¶¶(a),(b) until it has filed for the prior fiscal year).

*Minor pinpoint note (not an error):* Section 8.5 cites "AS 2201, paragraph .03" for the sentence about *who must be audited in an integrated audit*. AS 2201 .03 states the auditor's **objective** (express an opinion on effectiveness), not the *scope* of the 404(b) obligation, which comes from SOX 404(b)/Item 308(b) — both of which the paper also cites in the same sentence. The substance is correct; only the paragraph pinpoint is slightly loose.

### Does the paper invent a "regulator-endorsed probability threshold"? — **NO**

The paper explicitly states "The standard sets no number for 'remote', so π̄ is a judgment and a scenario value" and reports 5% and 1% side by side "treat[ing] neither as central." This is **true and correctly attributed**: FAS 5/ASC 450 define "remote" qualitatively ("slight"); AS 2201 uses "reasonable possibility" via the FAS 5 categories; SEC Item 308 sets no numeric probability. The paper does **not** fabricate any regulator-set number — π̄ is plainly labeled a scenario value, and the paper does not claim otherwise.

---

## 2. Model correctness (Proposition 5(a) and the admissibility equivalence)

**Formula — CORRECT.** For one opportunity of objective *o*,

> P_o(D) = p_cc + (1−p_cc) ∏_j [ p_cm_j + (1−p_cm_j) p_j^{n_j} ]

is the correct probability that every layer fails: the cross-type common cause defeats all layers with probability p_cc; otherwise (1−p_cc), each type *j* fails its *n_j* layers via the type common mode (p_cm_j) or, failing that, all *n_j* layers failing independently (p_j^{n_j}), and types fail independently so the factors multiply. Independent hand-check and the paper's own Monte Carlo (`verify_theory.py` §27a) both confirm the closed form.

**Admissibility equivalence — CORRECT.** π_o(D) = 1 − (1−P_o)^{N_o} ≤ π̄ ⟺ P_o ≤ P̄_o := 1 − (1−π̄)^{1/N_o} is exact algebra. (§27b confirms this over 300 random draws.)

**Caveats — adequate and honestly disclosed.** The three caveats in the task map to text the paper states explicitly:

1. **"Independence of types apart from p_cc FAVORS diversity → diversity value is an upper bound"** — correct and stated in Assumption 7 and S2.6. Positive cross-provider correlation (Kim et al. 2025) means the true P_o is *higher* than the product form, so the model's diversity benefit is *optimistic*; the paper reads it as an upper bound. This is the right direction and is disclosed.
2. **Shared infrastructure/tooling dependence omitted** — explicitly disclosed in S2.6 (identity provider, endpoint security agent, cloud region). The paper notes the diversity rule addresses *model* failures, not *availability/tooling* risk, and that the full-cost floor does not price keeping a second provider ready.
3. **No automation-bias parameter** — explicitly disclosed (§8.5; Assumption 7 says "p_cc is the only channel for automation bias"), citing Vaccaro et al. (2024) that human+AI combinations underperform the better of the two alone. The paper further does a numerical break-even on it (Remark S10, below).

These caveats are **adequate**: each is disclosed, each directionally *raises* the floor (so the paper's central "accountability does not vanish" claim is a fortiori true under the omissions), and none undermines the structural conclusion. A referee could reasonably ask for a *parameterized* automation-bias term rather than only a break-even sensitivity, but the paper's treatment is within norms for a stylized model and it flags the omission itself.

---

## 3. The core claim (common-mode floor cannot be reduced by depth)

**Logically correct.** For a single type *j* (all-AI on one provider), P_o(D) = p_cc + (1−p_cc)[p_cm_j + (1−p_cm_j) p_j^{n_j}] is strictly decreasing in n_j but strictly above its limit p_cc + (1−p_cc)p_cm_j at every finite depth. Hence if p_cc + (1−p_cc)p_cm_j ≥ P̄_o, then P_o(D) > P̄_o for all finite n_j → inadmissible however many layers, and neither the layer cost c_j nor the count n_j enters the bound (only θ — IT general controls — or adding another type can lower it). This is verified symbolically in the Proof of Proposition 5 and numerically in §27b (300 draws) and §25e (depth 1–39).

**Important qualifier (correctly flagged by the paper):** the conclusion is a *structural consequence of the beta-factor assumption*, not an empirical fact. The beta-factor model holds β (here p_cm_j) fixed as the redundancy level grows; so "stacking cannot reduce the common-mode term" is *built into* Assumption 7, and the paper says so ("That conclusion is an assumption of the example, and the provider's common-mode probability under the firm's IT general controls is the number to estimate"). The empirical premise — that any single provider's common-mode miss probability exceeds the "remote" threshold P̄_o — is not established; it is the quantity a firm must estimate. The *logic* is airtight; the *empirical force* is conditional.

**Beta-factor precedent — appropriate.** The beta-factor model (common-cause failure of redundant components, with a share β of failures striking every channel at once) is the canonical reliability-engineering framework for exactly this structure; the Hokstad & Rausand (2008) and Mosleh et al. (1989) citations are the standard references. Assumption 7 is a legitimate multi-group generalization (a type-specific beta per type plus a cross-type term p_cc), in the spirit of the Multiple Greek Letter family. Two honest caveats to note: (a) in hardware PRA the beta is applied to failure *rates over a mission time*, whereas the paper applies it *per control opportunity* to miss probabilities — a reasonable translation, and the paper calls the layer model "a reduced form of what auditors test"; (b) the Mosleh et al. year is given as 1989, which is plausible but I could not pin the exact bibliographic entry from primary sources; the *substantive* attribution (beta-factor common-cause modeling) is correct regardless.

**Multiversion analogy — sound and not cherry-picked.** The paper cites the correct, canonical findings: Eckhardt & Lee (1985) and Knight & Leveson (1986) — independently developed versions fail together on the same inputs more often than independence implies (Knight & Leveson 1986 confirmed via the N-version-programming literature: the independence assumption "failed statistically"); Littlewood & Miller (1989) — diversity in construction lowers, but does not eliminate, coincident failure. The paper uses the literature *correctly* on both sides: it takes "independence fails" to motivate a non-negligible common-mode term, **and** it takes "diversity only partially helps" to justify treating the diversity value as an **upper bound** (S2.6, Kim et al. 2025). This is the opposite of cherry-picking.

---

## 4. Numbers (Remark S10) — all reproduce exactly

Independent recomputation (also confirmed by the paper's `verify_theory.py` §25d–25f, §27):

| Quantity | Paper | Recomputed | Verdict |
|---|---|---|---|
| P̄_o at π̄=5%, N=24 | 0.0021 | 1−(0.95)^{1/24} = 0.002135 | ✓ |
| P̄_o at π̄=1%, N=24 | 0.0004 | 1−(0.99)^{1/24} = 0.000419 | ✓ |
| All-AI common-mode bound (p_cm=0.005) vs P̄_o | 0.005 > both | 0.005 > 0.002135, 0.000419 | ✓ inadmissible |
| All-AI annual floor at any depth | ≈ 11.3% | 1−(1−0.005)^24 = 0.1133 | ✓ |
| All-human annual floor at any depth | ≈ 4.7% | 1−(1−0.002)^24 = 0.0469 | ✓ |
| 1 human + 1 AI, π at 5% | 3.1% | (0.0519)(0.0249)=0.001292; 1−(1−P)^24 = 3.06% | ✓ |
| Cheapest admissible at 5% | 1H+1AI, $0.75m (0.075%) | $500k+$50k+$204,672 = $754,672 | ✓ |
| Cheapest admissible at 1% | 1H+2AI, $0.80m (0.080%), 0.7%/yr | P=(0.0519)(0.005398)=0.000280; π=0.67% | ✓ |
| 3 human layers at 5% | 4.98%, $1.50m | P=0.002+0.998·0.05³=0.002125; π=4.98% | ✓ |
| 48 opportunities or p_cm=0.01 at 1% | 2H+1AI, $1.25m | confirmed by code | ✓ |
| Cross-type break-even (1H+1AI @5%) | p_cc ≈ 0.0008 | (P̄−P₀)/(1−P₀) = 0.000844 | ✓ |
| ITGC line | $204,672 | 30,000+60,000+24,000/1.22+55,000+40,000 = 204,672 | ✓ |
| Direct costs | ≈ 0.30% | $1,492,375 + $1.5m = $2.99m = 0.299% | ✓ |
| Floor at $1bn | 0.37% (5%) / 0.38% (1%) | 0.30% + 0.075% = 0.375%; 0.30% + 0.080% = 0.38% | ✓ |
| Floor range of fees | 0.26–0.76% | 0.18%+0.075%=0.26%; 0.68%+0.080%=0.76% | ✓ |

**One minor phrasing imprecision (immaterial):** Remark S10 says the 1H+1AI design at 5% stays admissible "while the human misses at most 8.4% of the items the AI layers missed." The paper's own code computes this break-even as `(0.002 + 0.998·x)·(0.005 + 0.995·0.02)` — i.e., it *replaces the human marginal miss rate 0.05 with x* while retaining the human common-mode 0.002, yielding x ≈ 0.084. Under a strict *conditional* reading (P(human misses | AI missed) = x, which is what the sentence literally says), the break-even would be P̄_o / 0.0249 ≈ 0.086. The difference (8.4% vs ~8.6%) is immaterial, and the point — automation bias raising the reviewer's effective miss rate above a low break-even — is correct and disclosed as a sensitivity. Flagging for precision only.

---

## 5. Judgment — is the "accountability floor" sound?

**Sound as a modeling construct, with the boundaries correctly drawn.** The paper keeps three categories distinct and labels them explicitly:

- **Regulatory fact (verified above):** ICFR is a pass-fail standard; one material weakness bars an effectiveness conclusion (Item 308(a)(3)); "reasonable possibility" = reasonably possible or probable (FAS 5/ASC 450); no numeric "remote" threshold exists.
- **Modeling assumption:** the beta-factor layer model (Assumption 7), and the operationalization of "reasonable possibility" as an annual probability above π̄. The paper calls Proposition 5 "our operationalization of the standard, not an accepted audit method" — **correct**. The real auditor's deficiency evaluation (AS 2201 ¶¶.62–.70) weighs likelihood *and magnitude* of potential misstatements across a combination of deficiencies; it is not a single numeric annual-probability threshold. The paper's π_o(D) ≤ π̄ is a *simplification* of that judgment, and the paper says so.
- **Scenario value:** π̄ = 5%/1%, the layer miss rates, common-mode probabilities, and dollar costs. All are labeled illustrative ("not a control-design recommendation").

**Does it overstate or understate the floor?** The paper likely **understates** the true floor: it omits (and says it omits) entity-level/policy controls, controls at a model provider as a service organization, shared infrastructure/tooling dependence, automation bias, and the extra audit effort AI-performed controls will need (AS 2201 B28–B31 benchmarking is unavailable for vendor-updated model controls). Each of these raises the floor. Because the paper's thesis is that accountability **does not shrink to zero** with automation, an understated floor makes that conclusion *conservative* (a fortiori correct). There is no overstatement risk of consequence: the only way to "lower" the floor would be to pick a looser π̄, and the paper reports 5% and 1% side by side without choosing a central value, and even self-diagnoses (Remark S10) that a 1% threshold would make ineffective control "the norm" among human-run filers — evidence the paper is transparent about the threshold's sensitivity.

**Bottom line on the floor concept:** it is a defensible, transparent stylization of a real pass-fail regulatory constraint. It is not presented as, and should not be read as, an audit methodology or a compliance "safe harbor." The referee's only substantive caveats are (a) the empirical premise that a single AI provider's common-mode failure exceeds the "remote" threshold is unestablished (flagged by the paper itself), and (b) the model's diversity benefit is an upper bound (also flagged). Neither weakens the paper's structural result; both bound its practical calibration.

---

## Flags requiring author action

1. **Pinpoint (cosmetic):** §8.5 cites "AS 2201 ¶.03" for the 404(b) attestation *scope*. The scope is SOX 404(b)/Item 308(b); ¶.03 states the auditor's objective. Correct as a bundle of citations; consider re-pinning.
2. **Phrasing (precision):** Remark S10's "8.4% of the items the AI layers missed" is computed as a *marginal* human miss rate (retaining the 0.002 common mode); a literal conditional reading gives ~8.6%. Immaterial; consider one clarifying phrase.
3. **Optional:** Mosleh et al. "1989" year should be verified against the bibliography entry (substantive attribution is correct).

**No incorrect regulatory claim found.** All four regulatory assertions are verbatim-accurate; no fabricated probability threshold exists; the model is correct; the numbers reproduce; the caveats are adequate and honest.
