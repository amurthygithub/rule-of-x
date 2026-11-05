#!/usr/bin/env python3
"""
verify_part2_acquirer.py

Symbolic (sympy) and numerical (numpy/scipy) checks of every closed form, threshold and number in
  part2/theory_acquirer.tex   (Section "The Owner as Transformer", label sec:acquirer)
  part2/proofs_acquirer.tex   (Appendix "Proofs for Section sec:acquirer", label app:proofs-acquirer)
  sections/measurement_acquired.tex      (Paper 1: "Measuring the Score When Growth Is Bought", sec:acquired-growth)
  sections/appendix_proofs_acquired.tex  (Paper 1: proofs, app:proofs-acquired)
Section E checks the Paper 1 file; the other sections check Paper 2 (part2/).

Run:  python3 code/verify_part2_acquirer.py        (about half a minute)
Exit code 0 iff every check passes. Check names cite the LaTeX labels of the results.

Single sources, read at run time (nothing from them is typed here):
  notes/case_bending_spoons_f1_extract.md   every F-1 number (tables parsed, text figures by regular expression)
  data/examples/invoice_chain.json          the core's running example (theory_core.tex), for prop:acq-owner
The script writes part2/tables/acquirer_macros.tex (Paper 2) and sections/tables/acquired_macros.tex (Paper 1, the
subset that file uses); the .tex files quote only those macros for F-1 numbers and
example values. A lint check (G) fails if an F-1 figure is typed into the .tex files.

Typed constants are (i) presets of other sections, named with their label, so that their examples are reproduced
(sec:regimes take-private, sec:ext program, sec:labor leads, sec:accounting cutover), (ii) secondary-source facts
verified on 29 October 2026 (notes/ref_verification_acquirer.md), and (iii) scenario values (class d), marked.

Notation (notes/acquirer_notes.md): u_F platform reuse share; N_pl businesses on the platform; C_pool, C_spec poolable
and business-specific run costs; reb rebuild indicator; varpi_o owner's success probability; frak i (here `irr`)
continuously compounded IRRs; r_tv terminal-value rate of the IRR method; LTV cap; ND_rep repayment capacity;
g_org, g_acq organic and acquired growth; k_acq price per dollar of acquired revenue; c_fin interest share;
nu_rv cohort revenue hazard; g_in growth of new-customer revenue; S_sw survival of switching-cost ratios.
"""
import math
import json
import re
import sys
from pathlib import Path

import numpy as np
import sympy as sp
from scipy import integrate, optimize

ROOT = Path(__file__).resolve().parents[1]
EXTRACT = ROOT / "notes" / "case_bending_spoons_f1_extract.md"
INVOICE = ROOT / "data" / "examples" / "invoice_chain.json"
MACROS = ROOT / "part2" / "tables" / "acquirer_macros.tex"
MACROS_P1 = ROOT / "sections" / "tables" / "acquired_macros.tex"
TEXFILES_P2 = [ROOT / "part2" / "theory_acquirer.tex", ROOT / "part2" / "proofs_acquirer.tex"]
TEXFILES_P1 = [ROOT / "sections" / "measurement_acquired.tex", ROOT / "sections" / "appendix_proofs_acquired.tex"]
TEXFILES = TEXFILES_P2 + TEXFILES_P1

RNG = np.random.default_rng(20261029)
# XBOUNDS: placeholder values of a firm's decision weight on growth X (or an owner's X^o). The author withdrew the
# 7-to-13 estimate (revision plan A1, decision D-1); every example that needs X is evaluated at these values until the
# replacement bounds are in. To swap in the final bounds, edit this tuple, rerun, and check the "% XBOUNDS" sentences.
XBOUNDS = (2.5, 5.0, 9.0)
RESULTS = []
MAC = {}


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ::  {detail}" if detail else ""))


def header(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol * (1 + abs(b))


def mac(name, value):
    assert re.fullmatch(r"acq[A-Za-z]+", name), name
    assert name not in MAC, f"duplicate macro {name}"
    MAC[name] = value
    return value


def minus(t):
    """a leading minus sign that typesets as a minus in text and in math"""
    return "\\ensuremath{-}" + t[1:] if t.startswith("-") else t


def pct(x, d=1):
    return minus(f"{100 * x:.{d}f}\\%")


def num(x, d=1):
    s = f"{x:,.{d}f}"
    return minus(s.replace(",", "{,}"))


def musd(x_thousands, d=1):
    """USD thousands -> '$1{,}306.4 million'"""
    return f"\\${num(x_thousands / 1000.0, d)} million"


# ==============================================================================================
header("A. The F-1 extract: tables parsed, text figures extracted, arithmetic recomputed")
# ==============================================================================================
TXT = EXTRACT.read_text(encoding="utf-8")


def cell(c):
    c = c.replace(",", "").strip()
    neg = c.startswith("(") and c.endswith(")")
    c = c.strip("()")
    v = float(c.rstrip("%")) / 100 if c.endswith("%") else float(c)
    return -v if neg else v


def table(heading):
    lines = TXT.splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith(heading))
    rows, started = [], False
    for l in lines[i + 1:]:
        if l.startswith("|"):
            rows.append(l)
            started = True
        elif started:
            break
    cols = [c.strip() for c in rows[0].strip().strip("|").split("|")][1:]
    out = {}
    for r in rows[2:]:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        out[cells[0]] = dict(zip(cols, [cell(c) for c in cells[1:]]))
    return cols, out


def grab(pattern, conv=float):
    m = re.search(pattern, TXT)
    if not m:
        raise SystemExit(f"extract pattern not found: {pattern}")
    return [conv(g.replace(",", "")) for g in m.groups()]


COLS, IS = table("## Consolidated income statement")
_, CFS = table("## Cash flows")
_, BS = table("## Balance sheet")
check("A0 extract tables parsed: income statement (5 periods, 12 lines), cash flows (3 lines), balance sheet (4 items)",
      COLS == ["2023", "2024", "2025", "Q1 2025", "Q1 2026"] and len(IS) == 12 and len(CFS) == 3 and len(BS) == 4)
REV = IS["Revenue"]
OPI = IS["Operating income (loss)"]
INT = IS["Interest expense"]
NI = IS["Net income (loss)"]
OCF = CFS["Net cash from operating activities"]
CFI = CFS["Net cash from investing activities"]
CFF = CFS["Net cash from financing activities"]

# internal consistency of the extract's income statement (gross profit, operating income, pre-tax, net)
ok = True
for c in COLS:
    gp = REV[c] - IS["Cost of revenue"][c]
    oi = gp - IS["R&D"][c] - IS["Sales and marketing"][c] - IS["G&A"][c]
    pbt = oi - INT[c] - IS["Other expense (income)"][c]
    ni = pbt - IS["Income tax expense (benefit)"][c]
    ok &= abs(gp - IS["Gross profit"][c]) <= 2.5 and abs(oi - OPI[c]) <= 2.5 \
        and abs(pbt - IS["Income (loss) before tax"][c]) <= 2.5 and abs(ni - NI[c]) <= 2.5
check("A1 extract income statement adds up in every period (gross profit, operating income, pre-tax, net; "
      "rounding of $2 thousand in the F-1's figures)", ok)
ok = abs(BS["Total assets"]["USD thousands"] - BS["Total liabilities"]["USD thousands"]
         - BS["Total shareholders' equity"]["USD thousands"]) < 1.0
check("A2 extract balance sheet 31 Mar 2026: assets = liabilities + equity", ok)

g24 = REV["2024"] / REV["2023"] - 1
g25 = REV["2025"] / REV["2024"] - 1
gq1 = REV["Q1 2026"] / REV["Q1 2025"] - 1
mop = {c: OPI[c] / REV[c] for c in COLS}
cfin = {c: INT[c] / REV[c] for c in COLS}
m_after_int = {c: (OPI[c] - INT[c]) / REV[c] for c in COLS}
mocf = {c: OCF[c] / REV[c] for c in COLS}
cfi_share = {c: -CFI[c] / REV[c] for c in COLS}
R25_gaap = g25 + mop["2025"]
R25_int = g25 + m_after_int["2025"]
R25_ocf = g25 + mocf["2025"]
R25_allinv = g25 + (OCF["2025"] + CFI["2025"]) / REV["2025"]
R24_gaap, R24_int = g24 + mop["2024"], g24 + m_after_int["2024"]
Rq1_gaap, Rq1_int = gq1 + mop["Q1 2026"], gq1 + m_after_int["Q1 2026"]
print(f"  -> growth 2024 {g24:.4f}, 2025 {g25:.4f}, Q1 2026 YoY {gq1:.4f}; log 2025 {math.log(1+g25):.4f}")
print(f"  -> op margin 2025 {mop['2025']:.4f}; interest {cfin['2025']:.4f} (Q1 2026 {cfin['Q1 2026']:.4f}); "
      f"after interest {m_after_int['2025']:.4f}; OCF margin {mocf['2025']:.4f}; investing outflow {cfi_share['2025']:.4f}")
print(f"  -> Rule-of-40 2025: GAAP {100*R25_gaap:.1f}, after interest {100*R25_int:.1f}, OCF {100*R25_ocf:.1f}, "
      f"charging all net investing {100*R25_allinv:.1f}; 2024 {100*R24_gaap:.1f} / {100*R24_int:.1f}; "
      f"Q1 2026 {100*Rq1_gaap:.1f} / {100*Rq1_int:.1f}")
check("A3 brief's 2025 numbers recomputed from the table: growth 94.7%, GAAP operating margin 21.3%, score 116, after "
      "interest 105, operating-cash-flow margin 22.2%, interest 10.9% (2025) and 15.5% (Q1 2026) of revenue",
      round(100 * g25, 1) == 94.7 and round(100 * mop["2025"], 1) == 21.3 and round(100 * R25_gaap) == 116
      and round(100 * R25_int) == 105 and round(100 * mocf["2025"], 1) == 22.2
      and round(100 * cfin["2025"], 1) == 10.9 and round(100 * cfin["Q1 2026"], 1) == 15.5)

ocf_g = grab(r"(\d+)% in 2024, (\d+)% in 2025 and (\d+)% in Q1 2026; CAGR (\d+)%")
calc = [OCF["2024"] / OCF["2023"] - 1, OCF["2025"] / OCF["2024"] - 1, OCF["Q1 2026"] / OCF["Q1 2025"] - 1,
        math.sqrt(OCF["2025"] / OCF["2023"]) - 1]
check("A4 the extract's stated operating-cash-flow growth (246%, 42%, 254%; CAGR 122%) matches its own table",
      all(round(100 * c) == s for c, s in zip(calc, ocf_g)), str([round(100 * c, 1) for c in calc]))

ttm_rev = REV["2025"] + REV["Q1 2026"] - REV["Q1 2025"]
ttm_ni = NI["2025"] + NI["Q1 2026"] - NI["Q1 2025"]
scoop_rev, scoop_loss = grab(r"trailing-twelve-month revenue to March 2026 of \$([\d.]+) billion and a net loss of \$([\d.]+) million")
kucoin = grab(r"\$([\d.]+) billion in revenue for 2025")[0]
print(f"  -> TTM to Mar 2026: revenue {ttm_rev:.0f}k (IPOScoop {scoop_rev}B), net income {ttm_ni:.0f}k "
      f"(IPOScoop: loss {scoop_loss}M); KuCoin {kucoin}B vs {REV['2025']/1e6:.3f}B")
check("A5 caught secondary errors: IPOScoop TTM revenue matches (1.65B) but its TTM net loss does not (table gives "
      "+139.5M); KuCoin's 2025 revenue is about ten times the F-1's",
      round(ttm_rev / 1e6, 2) == scoop_rev and ttm_ni > 0 and abs(ttm_ni / 1000 - 139.5) < 0.05
      and 9.5 < kucoin / (REV["2025"] / 1e6) < 10.5)

hurL, hurU = grab(r"hurdles of (\d+)% levered and (\d+)% unlevered")
ltv_pct = grab(r"lower of (\d+)% of enterprise value")[0]
words = {"five": 5.0}
rep_years = words[re.search(r"could repay within (\w+) years", TXT).group(1)]
irr_years = words[re.search(r"\*\*IRR method:\*\*\n  - (\w+) years of free cash flow", TXT).group(1)]
cov, lev25, levq1 = grab(r"covenant of at most ([\d.]+); the ratio was ([\d.]+) at end-2025 and ([\d.]+) at end-Q1 2026")
dep_q1, dep_23 = grab(r"\$([\d.]+) billion in Q1 2026, against \$(\d+) million in all of 2023")
targets = grab(r"More than (\d+) targets")[0]
eq_raised, eq_share, dilution = grab(r"\$(\d+) million of primary equity raised in total, (\d+)% of it since 2023; dilution averaged ([\d.]+)%")
spo, spo_share = grab(r"(\d+) FTE at end-Q1 2026, (\d+)% of all FTE team members")
spo_tech = grab(r"(\d+)% are in technical roles")[0]
apps, hires, talent, talent_share = grab(r"about ([\d,]+) applications and (\d+) hires in 2025\. The Talent team has (\d+) FTE Spooners, (\d+)% of Spooners")
remini_fte = grab(r"about (\d+) FTE Spooners allocated")[0]
aol_emp = grab(r"about (\d+) direct employees")[0]
pr_lo, pr_hi, pr_solo = grab(r"from under (\d+)% in Q1 2025 to over (\d+)% by end-Q1 2026; about (\d+)%")
rps23, rps25, rpsq1 = grab(r"\$([\d.]+) million in 2023, \$([\d.]+) million in 2025, and \$([\d.]+) million in Q1 2026")
nrr23, nrr24, nrr25, nrrq1 = [x / 100 for x in grab(r"Portfolio: (\d+)% \(2023\), (\d+)% \(2024\), (\d+)% \(2025\) and (\d+)% \(Q1 2026\)")]
nrr_aol, nrr_ev, nrr_rem, nrr_sy = [x / 100 for x in grab(r"AOL (\d+)%, Evernote (\d+)%, Remini (\d+)%, StreamYard (\d+)%")]
ten5, ten10, tenmean = grab(r"(\d+)% of subscription revenue came from customers with tenure of at least five years and (\d+)% from at least ten\. Revenue-weighted average tenure was ([\d.]+) years")
ten5, ten10 = ten5 / 100, ten10 / 100
org23, org24, org25, orgq1 = grab(r"organic channels brought (\d+)% \(2023\), (\d+)% \(2024\), (\d+)% \(2025\) and (\d+)% \(Q1 2026\)")
geo_na, geo_eu = grab(r"(\d+)% of revenue from North America and (\d+)% from Europe")
ipo_px_x, ipo_raise_x = grab(r"priced at \$([\d.]+), raising about \$([\d.]+) billion")
check("A6 text figures extracted by pattern (hurdles, debt policy, covenant, team, NRR, tenure, AI, IPO)",
      all(v is not None for v in [hurL, hurU, ltv_pct, cov, spo, nrr25, ten5, pr_hi, ipo_px_x]) and rep_years == 5
      and irr_years == 5)

# implied counts
fte_total = spo / (spo_share / 100)
spo_tech_n = spo * spo_tech / 100
avg_spo23, avg_spo25, spo_q1_implied = REV["2023"] / 1000 / rps23, REV["2025"] / 1000 / rps25, REV["Q1 2026"] / 1000 / rpsq1
check("A7 revenue per Spooner is consistent with the team count: Q1 2026 revenue / $0.97M = 620 vs 621 at quarter end; "
      "implied average Spooners 346 (2023) and 508 (2025); total FTE about 2,300; Talent team 8.9% of Spooners (stated 9%)",
      abs(spo_q1_implied - spo) / spo < 0.01 and abs(fte_total - 2300) < 1 and round(100 * talent / spo) == talent_share,
      f"{spo_q1_implied:.1f}, {avg_spo23:.1f}, {avg_spo25:.1f}, {fte_total:.1f}")
max_concurrent = spo / remini_fte
hire_rate = hires / apps
liab_share = BS["Total liabilities"]["USD thousands"] / BS["Total assets"]["USD thousands"]
dep_ratio = dep_q1 * 1000 / dep_23
print(f"  -> Spooners {spo:.0f}, technical {spo_tech_n:.0f}; Remini-sized transformations at once <= {max_concurrent:.1f}; "
      f"hire rate {100*hire_rate:.4f}%; liabilities/assets {liab_share:.3f}; capital deployed Q1 2026 / 2023 {dep_ratio:.1f}")
check("A8 capital deployed in acquisitions (F-1 measure) exceeds the net investing outflow in Q1 2026 ($2.01B vs $1.65B) "
      "and in 2023 ($194M vs $170M): the two measure different things",
      dep_q1 * 1e6 > -CFI["Q1 2026"] and dep_23 * 1e3 > -CFI["2023"])

for k, v in {
    "acqRevTwentyThree": musd(REV["2023"]), "acqRevTwentyFour": musd(REV["2024"]), "acqRevTwentyFive": musd(REV["2025"]),
    "acqRevQOneFive": musd(REV["Q1 2025"]), "acqRevQOneSix": musd(REV["Q1 2026"]),
    "acqGrowthTwentyFour": pct(g24), "acqGrowthTwentyFive": pct(g25), "acqGrowthQOne": pct(gq1),
    "acqLogGrowthTwentyFive": pct(math.log(1 + g25)),
    "acqOpmTwentyFour": pct(mop["2024"]), "acqOpmTwentyFive": pct(mop["2025"]), "acqOpmQOne": pct(mop["Q1 2026"]),
    "acqIntTwentyFour": pct(cfin["2024"]), "acqIntTwentyFive": pct(cfin["2025"]), "acqIntQOne": pct(cfin["Q1 2026"]),
    "acqIntAbsTwentyFive": musd(INT["2025"]), "acqIntAbsQOne": musd(INT["Q1 2026"]),
    "acqMaiTwentyFour": pct(m_after_int["2024"]), "acqMaiTwentyFive": pct(m_after_int["2025"]),
    "acqMaiQOne": pct(m_after_int["Q1 2026"]),
    "acqOcfmTwentyFive": pct(mocf["2025"]), "acqCfiTwentyFive": pct(cfi_share["2025"]),
    "acqOcfmTwentyFour": pct(mocf["2024"]), "acqCfiTwentyFour": pct(cfi_share["2024"]),
    "acqOcfmQOne": pct(mocf["Q1 2026"]), "acqCfiQOne": pct(cfi_share["Q1 2026"]),
    "acqOcfCfiTwentyFour": pct((OCF["2024"] + CFI["2024"]) / REV["2024"]),
    "acqOcfCfiQOne": pct((OCF["Q1 2026"] + CFI["Q1 2026"]) / REV["Q1 2026"]),
    "acqTirr": f"{irr_years:.0f}", "acqTrep": f"{rep_years:.0f}",
    "acqOcfCfiTwentyFive": pct((OCF["2025"] + CFI["2025"]) / REV["2025"]),
    "acqRGaapQOne": num(100 * Rq1_gaap, 1), "acqRIntQOne": num(100 * Rq1_int, 1),
    "acqROcfQOne": num(100 * (gq1 + mocf["Q1 2026"]), 1),
    "acqRAllInvQOne": num(100 * (gq1 + (OCF["Q1 2026"] + CFI["Q1 2026"]) / REV["Q1 2026"]), 1),
    "acqOcfTwentyFive": musd(OCF["2025"]), "acqCfiAbsTwentyFive": musd(-CFI["2025"]),
    "acqNiTwentyFive": musd(NI["2025"]), "acqTtmRev": f"\\${num(ttm_rev / 1e6, 2)} billion",
    "acqTtmNi": musd(ttm_ni), "acqScoopLoss": f"\\${num(scoop_loss, 1)} million", "acqKucoin": f"\\${num(kucoin, 1)} billion",
    "acqOcfGrowth": f"{ocf_g[0]:.0f}\\%, {ocf_g[1]:.0f}\\% and {ocf_g[2]:.0f}\\%", "acqOcfCagr": f"{ocf_g[3]:.0f}\\%",
    "acqHurL": f"{hurL:.0f}\\%", "acqHurU": f"{hurU:.0f}\\%", "acqLtv": f"{ltv_pct:.0f}\\%",
    "acqCov": f"{cov:.2f}", "acqLevTwentyFive": f"{lev25:.2f}", "acqLevQOne": f"{levq1:.2f}",
    "acqDepQOne": f"\\${dep_q1:.2f} billion", "acqDepTwentyThree": f"\\${dep_23:.0f} million",
    "acqDepRatio": num(dep_ratio, 0), "acqTargets": f"{targets:.0f}",
    "acqEqRaised": f"\\${eq_raised:.0f} million", "acqEqShare": f"{eq_share:.0f}\\%", "acqDilution": f"{dilution:.1f}\\%",
    "acqSpo": f"{spo:.0f}", "acqSpoShare": f"{spo_share:.0f}\\%", "acqSpoTech": f"{spo_tech:.0f}\\%",
    "acqFteTotal": num(fte_total, 0), "acqApps": num(apps, 0), "acqHires": f"{hires:.0f}",
    "acqHireRate": f"{100 * hire_rate:.3f}\\%", "acqTalent": f"{talent:.0f}", "acqTalentShare": f"{talent_share:.0f}\\%",
    "acqReminiFte": f"{remini_fte:.0f}", "acqMaxConcurrent": f"{math.floor(max_concurrent):.0f}",
    "acqAolEmp": f"{aol_emp:.0f}", "acqPrLo": f"{pr_lo:.0f}\\%", "acqPrHi": f"{pr_hi:.0f}\\%", "acqPrSolo": f"{pr_solo:.0f}\\%",
    "acqRpsTwentyThree": f"\\${rps23:.2f} million", "acqRpsTwentyFive": f"\\${rps25:.2f} million",
    "acqRpsQOne": f"\\${rpsq1:.2f} million", "acqSpoAvgTwentyThree": num(avg_spo23, 0), "acqSpoAvgTwentyFive": num(avg_spo25, 0),
    "acqNrrTwentyThree": pct(nrr23, 0), "acqNrrTwentyFour": pct(nrr24, 0), "acqNrrTwentyFive": pct(nrr25, 0),
    "acqNrrQOne": pct(nrrq1, 0), "acqNrrAol": pct(nrr_aol, 0), "acqNrrEvernote": pct(nrr_ev, 0),
    "acqNrrRemini": pct(nrr_rem, 0), "acqNrrStreamyard": pct(nrr_sy, 0),
    "acqTenFive": pct(ten5, 0), "acqTenTen": pct(ten10, 0), "acqTenMean": f"{tenmean:.1f}",
    "acqOrgTwentyFive": f"{org25:.0f}\\%", "acqOrgQOne": f"{orgq1:.0f}\\%", "acqOrgTwentyFour": f"{org24:.0f}\\%",
    "acqGeoNa": f"{geo_na:.0f}\\%", "acqGeoEu": f"{geo_eu:.0f}\\%", "acqLiabShare": pct(liab_share, 0),
    "acqTotalAssets": f"\\${num(BS['Total assets']['USD thousands'] / 1e6, 2)} billion",
    "acqEquityBs": f"\\${num(BS[chr(84) + 'otal shareholders' + chr(39) + ' equity']['USD thousands'] / 1e6, 2)} billion",
}.items():
    mac(k, v)

# ----------------------------------------------------------------------------------------------
# A9-A14: the final prospectus (424B4) and the post-IPO Form 6-K exhibits, as extracted by the lead agent
# ----------------------------------------------------------------------------------------------
_, NG = table("### Non-GAAP reconciliation")
AMZ = NG["Amortization and impairment of acquired intangibles"]
TRX = NG["Transaction-related expense"]
REORG = NG["Reorganization-related expense"]
OTH = NG["Other items"]
AOI = NG["Adjusted Operating Income"]
AOIM = NG["Adjusted Operating Income margin"]
ok = all(abs(NG["Operating income (loss)"][c] - OPI[c]) < 0.5 for c in COLS)
ok &= all(abs(OPI[c] + AMZ[c] + TRX[c] + REORG[c] + OTH[c] - AOI[c]) < 2.5 for c in COLS)
ok &= all(abs(round(AOI[c] / REV[c], 2) - AOIM[c]) < 0.006 for c in COLS)
check("A9 424B4 non-GAAP reconciliation: its operating income equals the F-1 table in every period, the add-backs sum to "
      "Adjusted Operating Income (rounding of $2 thousand), and the stated adjusted margins match", ok)
reorg_sh = {c: REORG[c] / REV[c] for c in COLS}
trx_sh = {c: TRX[c] / REV[c] for c in COLS}
amz_sh = {c: AMZ[c] / REV[c] for c in COLS}
R25_adj = g25 + AOI["2025"] / REV["2025"]
print(f"  -> reorganization share of revenue {', '.join(f'{c}: {v:.4f}' for c, v in reorg_sh.items())}; transaction 2025 "
      f"{trx_sh['2025']:.4f}; amortization 2025 {amz_sh['2025']:.4f}; score on the adjusted margin 2025 {100*R25_adj:.1f}")
check("A10 the coordinator's figures: reorganization 6.0% of revenue in 2025 and 12.6% in Q1 2026, transaction 6.5% in "
      "2025, a score on the adjusted margin of about 142 in 2025",
      round(100 * reorg_sh["2025"], 1) == 6.0 and round(100 * reorg_sh["Q1 2026"], 1) == 12.6
      and round(100 * trx_sh["2025"], 1) == 6.5 and round(100 * R25_adj) == 142)
# Article 11 pro forma, FY2025
pf_bs, pf_eb, pf_aol, pf_vim, pf_tot = grab(r"Bending Spoons historical ([\d,]+), plus Eventbrite ([\d,]+), AOL ([\d,]+) and "
                                            r"Vimeo \(1 Jan to 23 Nov 2025\) ([\d,]+), gives a pro forma combined total of ([\d,]+)")
pf_oi = grab(r"\*\*Operating income:\*\* pro forma combined ([\d,]+)")[0]
pf_oi_parts = grab(r"Historical ([\d,]+); Eventbrite −([\d,]+) \(adjustment −([\d,]+)\); AOL ([\d,]+) \(adjustment −([\d,]+)\); "
                   r"Vimeo −([\d,]+) \(adjustment −([\d,]+)\)")
pf_int, pf_fin_adj = grab(r"\*\*Interest expense:\*\* pro forma combined ([\d,]+) .*?financing adjustment of ([\d,]+)")
px_aol, px_eb, px_vim = grab(r"AOL \(completed 2 Jan 2026, purchase price \$([\d,]+)M\), Eventbrite \(10 Mar 2026, \$([\d,]+)M\) "
                             r"and Vimeo \(24 Nov 2025, \$([\d,]+)M\)")
import datetime as _dt
vim_days = (_dt.date(2025, 11, 23) - _dt.date(2025, 1, 1)).days + 1
k_deal = {"AOL": px_aol * 1000 / pf_aol, "Eventbrite": px_eb * 1000 / pf_eb, "Vimeo": px_vim * 1000 / (pf_vim * 365 / vim_days)}
h_, e1, e2, a1, a2_, v1, v2 = pf_oi_parts
ok = abs(pf_bs - REV["2025"]) < 0.5 and abs(pf_bs + pf_eb + pf_aol + pf_vim - pf_tot) < 1.5
ok &= abs(h_ - OPI["2025"]) < 0.5 and abs(h_ - e1 - e2 + a1 - a2_ - v1 - v2 - pf_oi) < 1.5
ok &= vim_days == 327 and abs(k_deal["AOL"] - 2.30) < 0.005 and abs(k_deal["Eventbrite"] - 1.73) < 0.005 \
    and abs(k_deal["Vimeo"] - 3.2) < 0.05
pf_ratio = pf_tot / REV["2025"]
print(f"  -> pro forma 2025: revenue {pf_tot:.0f}k ({pf_ratio:.3f} x actual), operating margin {pf_oi/pf_tot:.4f}, interest "
      f"{pf_int/pf_tot:.4f}; price / revenue AOL {k_deal['AOL']:.3f}, Eventbrite {k_deal['Eventbrite']:.3f}, Vimeo "
      f"{k_deal['Vimeo']:.3f} (annualized from {vim_days} days)")
check("A11 424B4 Article 11 pro forma for 2025: components add to the combined revenue and operating income (rounding of "
      "$1 thousand); purchase price over annual revenue AOL 2.30, Eventbrite 1.73, Vimeo about 3.2 (327 days annualized)", ok)
K_LO, K_HI_D = min(k_deal.values()), max(k_deal.values())
# Q2 2026 (6-K of 13 Aug 2026)
q2_rev, q2_rev_py = grab(r"Revenue ([\d,]+), against ([\d,]+) in Q2 2025")
q2_org = grab(r"Organic revenue growth was (\d+)% in Q2 2026")[0] / 100
q2_oi, q2_aoi, q2_ni = grab(r"Operating income ([\d,]+) \(\d+% of revenue\)\. Adjusted Operating Income ([\d,]+) \(\d+%\)\. "
                            r"Net income ([\d,]+)")
q2_reorg_cor, q2_reorg_opex = grab(r"reorganization-related expense was \$(\d+)M in cost of revenue and \$(\d+)M in operating")
q2_nd, q2_ltd, q2_cash, q2_lev = grab(r"Net debt \$([\d.]+)B \(long-term debt \$([\d.]+)B, cash \$([\d.]+)M\)\. Leverage ratio ([\d.]+)×")
q2_g = q2_rev / q2_rev_py - 1
q2_m = q2_oi / q2_rev
R_q2_rep, R_q2_org = q2_g + q2_m, q2_org + q2_m
q2_reorg_sh = (q2_reorg_cor + q2_reorg_opex) * 1000 / q2_rev
print(f"  -> Q2 2026: growth {q2_g:.4f}, operating margin {q2_m:.4f}, adjusted {q2_aoi/q2_rev:.4f}; reported score "
      f"{100*R_q2_rep:.1f}, organic score {100*R_q2_org:.1f}; reorganization {q2_reorg_sh:.4f} of revenue; net debt "
      f"{q2_ltd - q2_cash/1000:.3f}B vs {q2_nd}B; EBITDA implied by the 2.4x ratio {q2_nd/q2_lev:.2f}B")
check("A12 6-K Q2 2026: growth 126%, GAAP operating margin 34%, reported score about 160 and organic score about 37 (the "
      "company's 3% organic growth); net debt = long-term debt - cash ($4.09B)",
      round(100 * q2_g) == 126 and round(100 * q2_m) == 34 and round(100 * R_q2_rep) == 160 and round(100 * R_q2_org) == 37
      and abs(q2_ltd - q2_cash / 1000 - q2_nd) < 0.005)
# financing, deals and shares
nt_usd, nt_usd_c, nt_eur, nt_eur_c, nt_due = grab(r"\$([\d.]+)B at ([\d.]+)% and €(\d+)M at ([\d.]+)%, due (\d{4})")
tlb_usd, tlb_eur = grab(r"\$([\d.]+)B on the USD TLB and €(\d+)M on the EUR TLB")
trac_ev, trac_wiki = grab(r"enterprise value of \$(\d+)M \(6-K\)\. Wikipedia's table gives \$(\d+)M")
ipo_net = grab(r"\*\*IPO net proceeds:\*\* \$([\d.]+)B")[0]
air_ev, air_eq = grab(r"Airtable:\*\* definitive agreement at an EV of \$([\d.]+)B and an equity value of about \$([\d.]+)B")
miro_ev, miro_eq, miro_reinv = grab(r"Miro:\*\* definitive agreement at an EV of \$([\d.]+)B and an equity value of about "
                                    r"\$([\d.]+)B, all cash\. Certain Miro shareholders reinvest \$(\d+)M")
brk1, brk2, brk_st = grab(r"invested \$(\d+)M at the IPO, then a further \$(\d+)M .*?total stake of (\d+)%")
sh_off, sh_new = grab(r"([\d,]+) ordinary shares offered, of which ([\d,]+) were new shares")
ipo_px_p = grab(r"IPO price \$([\d.]+) per share")[0]
gross_new = sh_new * ipo_px_p / 1e9
print(f"  -> notes ${nt_usd}B at {nt_usd_c}% and EUR{nt_eur:.0f}M at {nt_eur_c}% due {nt_due:.0f}; Tractive EV {trac_ev:.0f}M "
      f"(Wikipedia {trac_wiki:.0f}M); new shares {sh_new:,.0f} -> gross ${gross_new:.3f}B vs net proceeds ${ipo_net}B; "
      f"Berkshire ${brk1+brk2:.0f}M for {brk_st:.0f}% -> implied equity ${(brk1+brk2)/brk_st*100/1000:.1f}B")
ovr_co, ovr_sell = grab(r"up to ([\d,]+) more shares from the company and ([\d,]+) from the selling shareholders")
net_est, net_full = grab(r"Estimated net proceeds to the company:\*\* \$([\d,]+)M, or \$([\d,]+)M if the option")
gross_full = (sh_new + ovr_co) * ipo_px_p / 1e6
print(f"  -> over-allotment {ovr_co:,.0f} company shares: gross with full exercise ${gross_full:.0f}M; estimated net "
      f"${net_est:.0f}M / ${net_full:.0f}M; 6-K net ${ipo_net*1000:.0f}M leaves ${ipo_net*1000 - net_full:.0f}M unexplained")
check("A13 424B4 offering terms match the secondary IPO figures used (57.97M shares at $29.00; 34.4M new); the 6-K's net "
      "proceeds ($1.10B) exceed the gross value of the new shares ($0.998B) but fit the over-allotment option on 5,244,026 "
      "company shares (estimated net $1,079M with full exercise, gross $1,150M), leaving about $21M unexplained and unused; "
      "Wikipedia's Tractive figure ($900M) is not the 6-K's EV ($759M)",
      abs(sh_off / 1e6 - 57.97) < 0.005 and abs(sh_new / 1e6 - 34.4) < 0.05 and ipo_px_p == 29.0
      and ipo_net > gross_new and net_est < net_full <= ipo_net * 1000 < gross_full
      and abs(ipo_net * 1000 - net_full - 21) < 1 and trac_wiki != trac_ev)
R_DEBT_NOTES = math.log(1 + nt_usd_c / 100)
# ----------------------------------------------------------------------------------------------
# A14-A16 (round 2): the Q2 2026 6-K exhibits (Ex. 99.1 results, Ex. 99.2 interim statements) read on sec.gov, the
# basis of each score (U.S. GAAP: operating cash flow is after interest paid), and the material-weakness wording
# ----------------------------------------------------------------------------------------------
_, Q2IS = table("### Q2 2026 income statement")
_, Q2NG = table("### Q2 2026 non-GAAP add-backs")
_, H1CF = table("### Six-month cash flows")
Q2 = {k: v["Q2 2026"] for k, v in Q2IS.items()}
q2_int, q2_amz = Q2["Interest expense"], Q2NG["Amortization and impairment of acquired intangible assets"]["Q2 2026"]
q2_trx, q2_reorg = Q2NG["Transaction-related expense"]["Q2 2026"], Q2NG["Reorganization-related expense"]["Q2 2026"]
q2_aoi_t = Q2NG["Adjusted Operating Income"]["Q2 2026"]
ok = abs(Q2["Revenue"] - q2_rev) < 0.5 and abs(Q2IS["Revenue"]["Q2 2025"] - q2_rev_py) < 0.5 and abs(Q2["Operating income"] - q2_oi) < 0.5
ok &= all(abs(v["Operating income"] - v["Interest expense"] - v["Other expense (income)"] - v["Income before tax"]) < 2.5
          and abs(v["Income before tax"] - v["Income tax expense (benefit)"] - v["Net income"]) < 2.5
          for v in ({k: Q2IS[k][c] for k in Q2IS} for c in ("Q2 2025", "Q2 2026")))
ok &= abs(q2_reorg - (q2_reorg_cor + q2_reorg_opex) * 1000) < 500 and abs(q2_aoi_t - q2_aoi) < 0.5
ok &= abs(Q2["Net income"] - q2_ni) < 0.5
q2_cfin, q2_reorg_x, q2_trx_sh, q2_amz_sh = q2_int / q2_rev, q2_reorg / q2_rev, q2_trx / q2_rev, q2_amz / q2_rev
R_q2_rep_int = R_q2_rep - q2_cfin                                    # reported growth, GAAP margin, after interest
R_q2_org_int = R_q2_org - q2_cfin                                    # organic, after interest
R_q2_org_xr = R_q2_org + q2_reorg_x                                  # organic, reorganization treated as an acquisition cost
R_q2_org_int_xr = R_q2_org_int + q2_reorg_x
R_q2_adj = q2_g + q2_aoi_t / q2_rev
print(f"  -> Q2 2026 (6-K Ex. 99.1 tables): interest {q2_cfin:.4f}, reorganization {q2_reorg_x:.4f}, transaction {q2_trx_sh:.4f}, "
      f"amortization {q2_amz_sh:.4f} of revenue; reported score {100*R_q2_rep:.1f}, after interest {100*R_q2_rep_int:.1f}; organic "
      f"{100*R_q2_org:.1f}, after interest {100*R_q2_org_int:.1f}, before reorganization {100*R_q2_org_xr:.1f}, after interest and "
      f"before reorganization {100*R_q2_org_int_xr:.1f}; adjusted {100*R_q2_adj:.1f}")
check("A14 6-K Q2 2026 tables (Ex. 99.1): they match the figures quoted earlier in the extract and add up; interest is 15.5% "
      "and reorganization 7.2% of revenue (RA-4, Fable IO/AI F12), so the organic score of about 37 is about 22 after interest "
      "(IB-4's estimate) and about 44 before the reorganization charge (29 with both)",
      ok and round(100 * q2_cfin, 1) == 15.5 and round(100 * q2_reorg_x, 1) == 7.2 and round(100 * R_q2_org_int) == 22
      and round(100 * R_q2_org_xr) == 44 and round(100 * R_q2_org_int_xr) == 29 and round(100 * R_q2_rep_int) == 145)
H1 = {c: {k: H1CF[k][c] for k in H1CF} for c in ("H1 2025", "H1 2026")}
h1_int_exp = {"H1 2025": INT["Q1 2025"] + Q2IS["Interest expense"]["Q2 2025"], "H1 2026": INT["Q1 2026"] + q2_int}
int_paid_ratio = {c: H1[c]["Interests paid"] / h1_int_exp[c] for c in H1}
capex_sh = {c: -H1[c]["Purchase of property, plant, and equipment"] / -H1[c]["Net cash from investing activities"] for c in H1}
acq_sh = {c: -H1[c]["Acquisitions of businesses, net of cash acquired"] / -H1[c]["Net cash from investing activities"] for c in H1}
gaap_basis = re.search(r"\"prepared in conformity with U\.S\. generally accepted accounting principles\"", TXT) is not None
mw_quote = re.search(r"\"(We have identified material weaknesses in our internal control over financial reporting, and we may "
                     r"not be able to remediate these material weaknesses or otherwise maintain effective internal control over "
                     r"financial reporting\.)\"", TXT)
TAU_IRES = grab(r"\"(\d+)% for IRES\"")[0] / 100                    # Italy's corporate income tax rate (PwC, 13 Jul 2026)
irap_excl = re.search(r"interest income and expense \.\.\. are excluded for the purposes of the IRAP taxable base", TXT) is not None
print(f"  -> H1 interest paid / interest expense: {int_paid_ratio}; PP&E / investing outflow {capex_sh}; acquisitions / "
      f"investing outflow {acq_sh}; IRES {TAU_IRES}")
check("A15 6-K Ex. 99.2: U.S. GAAP basis, so operating cash flow is after interest paid (ASC 230-10-45-17(d)); interest paid "
      "was 90% and 80% of interest expense in H1 2025 and H1 2026; capital spending is negligible (PP&E under 0.5% of the "
      "investing outflow, acquisitions over 99.5%); interest saves tax at Italy's IRES rate of 24% at most (it is outside "
      "the IRAP base)",
      gaap_basis and 0.85 < int_paid_ratio["H1 2025"] < 0.95 and 0.75 < int_paid_ratio["H1 2026"] < 0.85
      and all(capex_sh[c] < 0.005 and acq_sh[c] > 0.995 for c in H1) and TAU_IRES == 0.24 and irap_excl)
check("A16 RA-4: the F-1 and 424B4 summary risk factor on material weaknesses is quoted verbatim in the extract; the 6-K "
      "presents organic growth among unaudited operating results, outside its non-GAAP measures, with estimated "
      "pre-acquisition revenue, and reports no Rule-of-40 score",
      mw_quote is not None and "(including estimated pre-acquisition revenue, where applicable)" in TXT
      and "does not mention a Rule of 40 score" in TXT and "not presented as a non-GAAP measure" in TXT)
for k, v in {"acqQTwoInt": pct(q2_cfin, 1), "acqQTwoIntAbs": musd(q2_int), "acqQTwoReorgX": pct(q2_reorg_x, 1),
             "acqQTwoReorgAbs": musd(q2_reorg), "acqQTwoTrx": pct(q2_trx_sh, 1), "acqQTwoAmz": pct(q2_amz_sh, 1),
             "acqQTwoGx": pct(q2_g, 1), "acqQTwoMx": pct(q2_m, 1), "acqQTwoAdjMx": pct(q2_aoi_t / q2_rev, 1),
             "acqRQTwoRepX": num(100 * R_q2_rep, 1), "acqRQTwoRepInt": num(100 * R_q2_rep_int, 1),
             "acqRQTwoOrgX": num(100 * R_q2_org, 1), "acqRQTwoOrgInt": num(100 * R_q2_org_int, 1),
             "acqRQTwoOrgNoReorg": num(100 * R_q2_org_xr, 1), "acqRQTwoOrgIntNoReorg": num(100 * R_q2_org_int_xr, 1),
             "acqRQTwoAdj": num(100 * R_q2_adj, 1), "acqRQTwoRepIntR": num(100 * R_q2_rep_int, 0),
             "acqRQTwoOrgIntR": num(100 * R_q2_org_int, 0), "acqRQTwoOrgNoReorgR": num(100 * R_q2_org_xr, 0),
             "acqRQTwoOrgIntNoReorgR": num(100 * R_q2_org_int_xr, 0),
             "acqIntPaidHOneSix": musd(H1["H1 2026"]["Interests paid"]),
             "acqIntPaidRatioHOneFive": pct(int_paid_ratio["H1 2025"], 0), "acqIntPaidRatioHOneSix": pct(int_paid_ratio["H1 2026"], 0),
             "acqCapexHOneSix": musd(-H1["H1 2026"]["Purchase of property, plant, and equipment"]),
             "acqAcqHOneSix": musd(-H1["H1 2026"]["Acquisitions of businesses, net of cash acquired"], 0),
             "acqCapexShareHOneFive": pct(capex_sh["H1 2025"], 2), "acqCapexShareHOneSix": pct(capex_sh["H1 2026"], 1),
             "acqAcqShareHOneFive": pct(acq_sh["H1 2025"], 1), "acqAcqShareHOneSix": pct(acq_sh["H1 2026"], 1),
             "acqTauIres": pct(TAU_IRES, 0), "acqIpoNetEst": f"\\${num(net_est, 0)} million",
             "acqIpoNetFull": f"\\${num(net_full, 0)} million"}.items():
    mac(k, v)
for k, v in {"acqAmzTwentyFive": pct(amz_sh["2025"], 1), "acqAmzTwentyFour": pct(amz_sh["2024"], 1),
             "acqTrxTwentyFour": pct(trx_sh["2024"], 1), "acqTrxQOne": pct(trx_sh["Q1 2026"], 1),
             "acqTrxTwentyFive": pct(trx_sh["2025"], 1), "acqReorgTwentyFive": pct(reorg_sh["2025"], 1),
             "acqReorgTwentyFour": pct(reorg_sh["2024"], 1), "acqReorgQOne": pct(reorg_sh["Q1 2026"], 1),
             "acqReorgAbsTwentyFive": musd(REORG["2025"]), "acqAoimTwentyFive": pct(AOIM["2025"], 0),
             "acqRAdjTwentyFive": num(100 * R25_adj, 1),
             "acqRAdjTwentyFour": num(100 * (g24 + AOI["2024"] / REV["2024"]), 1),
             "acqRAdjQOne": num(100 * (gq1 + AOI["Q1 2026"] / REV["Q1 2026"]), 1),
             "acqAoimTwentyFour": pct(AOI["2024"] / REV["2024"], 1), "acqAoimTwentyFiveX": pct(AOI["2025"] / REV["2025"], 1),
             "acqAoimQOne": pct(AOI["Q1 2026"] / REV["Q1 2026"], 1), "acqAmzQOne": pct(amz_sh["Q1 2026"], 1),
             "acqPfRev": musd(pf_tot), "acqPfRatio": num(pf_ratio, 1), "acqPfOpm": pct(pf_oi / pf_tot, 1),
             "acqPfInt": pct(pf_int / pf_tot, 1), "acqPxAol": f"\\${num(px_aol, 0)} million",
             "acqPxEb": f"\\${num(px_eb, 0)} million", "acqPxVim": f"\\${num(px_vim, 0)} million",
             "acqKAol": num(k_deal["AOL"], 1), "acqKEb": num(k_deal["Eventbrite"], 1), "acqKVim": num(k_deal["Vimeo"], 1),
             "acqKLo": num(K_LO, 1), "acqKHi": num(K_HI_D, 1), "acqVimPre": musd(pf_vim), "acqVimDays": f"{vim_days}",
             "acqQTwoRev": musd(q2_rev), "acqQTwoG": pct(q2_g, 0), "acqQTwoOrg": pct(q2_org, 0), "acqQTwoM": pct(q2_m, 0),
             "acqQTwoAdjM": pct(q2_aoi / q2_rev, 0), "acqRQTwoRep": num(100 * R_q2_rep, 0),
             "acqRQTwoOrg": num(100 * R_q2_org, 0), "acqRQTwoGap": num(100 * (R_q2_rep - R_q2_org), 0),
             "acqQTwoReorg": f"\\${q2_reorg_cor + q2_reorg_opex:.0f} million", "acqQTwoReorgSh": pct(q2_reorg_sh, 1),
             "acqNetDebt": f"\\${q2_nd:.2f} billion", "acqLevQTwo": f"{q2_lev:.1f}",
             "acqNotesUsd": f"\\${nt_usd:.2f} billion", "acqNotesUsdC": f"{nt_usd_c:.3f}\\%",
             "acqNotesEur": f"EUR {nt_eur:.0f} million", "acqNotesEurC": f"{nt_eur_c:.3f}\\%",
             "acqNotesDue": f"{nt_due:.0f}", "acqTlbUsd": f"\\${tlb_usd:.2f} billion",
             "acqTlbEur": f"EUR {tlb_eur:.0f} million", "acqTractive": f"\\${trac_ev:.0f} million",
             "acqTractiveWiki": f"\\${trac_wiki:.0f} million", "acqIpoNet": f"\\${ipo_net:.2f} billion",
             "acqAirEv": f"\\${air_ev:.3f} billion", "acqAirEq": f"\\${air_eq:.2f} billion",
             "acqMiroEv": f"\\${miro_ev:.3f} billion", "acqMiroEq": f"\\${miro_eq:.2f} billion",
             "acqMiroReinv": f"\\${miro_reinv:.0f} million", "acqBrkOne": f"\\${brk1:.0f} million",
             "acqBrkTwo": f"\\${brk2:.0f} million", "acqBrkStake": f"{brk_st:.0f}\\%",
             "acqIpoSharesP": f"{sh_off / 1e6:.2f} million", "acqIpoNewP": f"{sh_new / 1e6:.2f} million"}.items():
    mac(k, v)
# ==============================================================================================
header("B. Owner capability (Assumption ass:acq-owner, Proposition prop:acq-owner)")
# ==============================================================================================
J = json.loads(INVOICE.read_text())
TR, ANC = J["transition"], J["ancillary"]


def lin_ramp_pv(r, Tpar):
    return integrate.quad(lambda t: math.exp(-r * t) * t / Tpar, 0, Tpar)[0] if Tpar > 0 else 0.0


def S_r(r, Tpar, Th):
    tail = (math.exp(-r * Tpar) - (math.exp(-r * Th) if math.isfinite(Th) else 0.0)) / r
    return lin_ramp_pv(r, Tpar) + tail


def npv_core(F, W, varpi, Cpar, CJ, Cstr, Lroll, r, Th, Tpar, Tdet, bbar, I=0.0):
    """eq:tasks-npv with a linear ramp (the core's reference implementation)"""
    A = (1 - math.exp(-r * Tpar)) / r
    pu = math.exp(-Tpar / Tdet)
    return (-(F + I + CJ) - Cpar * A + varpi * bbar * W * S_r(r, Tpar, Th)
            - math.exp(-r * Tpar) * ((varpi + (1 - varpi) * pu) * Cstr + (1 - varpi) * pu * Lroll))


BASE = dict(F=TR["F"], W=TR["W"], varpi=TR["varpi_p"], Cpar=TR["C_par"], CJ=TR["C_J"], Cstr=TR["C_str"],
            Lroll=TR["L_roll"], r=TR["r"], Th=TR["T_h"], Tpar=TR["T_par"], Tdet=TR["T_det"], bbar=TR["bbar_p"],
            I=TR["I"])
npv_sa = npv_core(**BASE)
check("B0 core's invoice transition reproduced from data/examples/invoice_chain.json (eq:tasks-npv)",
      close(npv_sa, TR["results"]["NPV"], 1e-9), f"{npv_sa:,.0f}")

# (a) exact decomposition, symbolic
F, Fo, W, Wo, vp, vo, bb, Sr, r_, Tp, Td, Cs, Lr, Cp, CJ_, I_ = sp.symbols("F F_o W W_o varpi varpi_o b S r T_p T_d C_s L C_p C_J I")
pu_ = sp.exp(-Tp / Td)
def NPVs(F_, W_, v_):
    return -(F_ + I_ + CJ_) - Cp * (1 - sp.exp(-r_ * Tp)) / r_ + v_ * bb * W_ * Sr - sp.exp(-r_ * Tp) * ((v_ + (1 - v_) * pu_) * Cs + (1 - v_) * pu_ * Lr)
lhs = NPVs(Fo, Wo, vo) - NPVs(F, W, vp)
rhs = (F - Fo) + bb * Sr * (vo * Wo - vp * W) - sp.exp(-r_ * Tp) * (vo - vp) * ((1 - pu_) * Cs - pu_ * Lr)
check("B1 prop:acq-owner(a): NPV^o - NPV = (F - F^o) + b S_r (varpi^o W^o - varpi W) - e^{-rT_par}(varpi^o - varpi)"
      "[(1 - p_u) C^str - p_u L_roll] (symbolic)", sp.simplify(lhs - rhs) == 0)

# run-cost split of the example (Assumption ass:tasks-ancillary as implemented by the core)
W0 = TR["W_before_run"]
C_run = ANC["total"]
C_spec = ANC["tech_debt"]                 # integrations and coupled pairs: business specific unless rebuilt
C_mr = ANC["maintenance"] + ANC["revalidation"]
C_inc = ANC["C_inc"]
C_s = ANC["residual"]                     # exponential residual: residual loss at the optimum = C_s
def C_risk(x):
    return x if x <= C_s else C_s * (1 + math.log(x / C_s))
check("B2 run costs split exactly into maintenance + revalidation + technical debt + risk cost C_s[1 + ln(C^inc/C_s)] "
      "(prop:tasks-security(b)); technical debt = integrations + coupled pairs",
      close(C_run, C_mr + C_spec + C_risk(C_inc), 1e-9) and close(C_spec, ANC["integrations"] + ANC["coupling"], 1e-12)
      and close(C_risk(C_inc), ANC["risk"], 1e-9) and close(TR["W"], W0 - C_run, 1e-9))


def W_owner(N, reb):
    pool = C_mr + (C_spec if reb else 0.0)
    return W0 - pool / N - C_risk(N * C_inc) / N - (0.0 if reb else C_spec)


def F_owner(uF, i=1, epsL=0.0):
    return (1 - uF) * (TR["F_build"] + TR["F_int"]) * i ** (-epsL) + TR["F_other"]


def npv_owner(uF=0.0, N=1, reb=False, varpi=None, Th=None, i=1, epsL=0.0):
    b = dict(BASE)
    b.update(F=F_owner(uF, i, epsL), W=W_owner(N, reb), varpi=TR["varpi_p"] if varpi is None else varpi,
             Th=TR["T_h"] if Th is None else Th)
    return npv_core(**b)


check("B3 W^o(N_pl = 1, no rebuild) = W and NPV^o(standalone capability) = NPV",
      close(W_owner(1, False), TR["W"], 1e-9) and close(npv_owner(), npv_sa, 1e-9))
# (b) monotone in N_pl; pooling alone bounded by W0 - C_spec; rebuild threshold
ok = all(W_owner(n + 1, rb) >= W_owner(n, rb) - 1e-9 for n in range(1, 200) for rb in (False, True))
lim_noreb = W0 - C_spec
Nmin = optimize.brentq(lambda n: W_owner(n, True), 1.0001, 1e6)
print(f"  -> W0 {W0:,.0f}; C_run {C_run:,.0f}; C_spec {C_spec:,.0f}; pooling-only limit W0 - C_spec {lim_noreb:,.0f}; "
      f"N_pl^min with rebuild {Nmin:.2f} (linear approximation C_run/W0 = {C_run/W0:.2f})")
# since the params commit (b_bar, r_bar_high, q_M) and the redesigned conditional case, W0 exceeds C^spec: pooling alone
# can make the process save money, up to W0 - C^spec a year, once enough businesses share its other run costs
Nmin_nr = optimize.brentq(lambda n: W_owner(n, False), 1.0001, 1e9) if W_owner(1e9, False) > 0 else math.inf
print(f"  -> without a rebuild: W^o > 0 once N_pl > {Nmin_nr:.2f}; limit {lim_noreb:,.0f} a year")
check("B4 prop:acq-owner(b): W^o is nondecreasing in N_pl; without a rebuild W^o < W0 - C^spec for all N_pl; in the "
      "example C^spec < W0, so pooling alone makes the process save money once enough businesses share it, but never "
      "more than W0 - C^spec a year, and fewer businesses are needed with a rebuild",
      ok and all(W_owner(n, False) <= lim_noreb + 1e-9 for n in (1, 10, 1e3, 1e6)) and C_spec < W0
      and math.isfinite(Nmin_nr) and W_owner(Nmin_nr * 1.001, False) > 0 > W_owner(Nmin_nr * 0.999, False)
      and Nmin < Nmin_nr and lim_noreb > 0, f"W0 {W0:,.0f}, C_spec {C_spec:,.0f}, N without rebuild {Nmin_nr:.2f}, with {Nmin:.2f}")
check("B5 prop:acq-owner(b): with a rebuild W^o > 0 iff N_pl exceeds the root of W0 = [C^pool + C^spec + C^risk(N C^inc)]/N",
      W_owner(Nmin * 1.001, True) > 0 > W_owner(Nmin * 0.999, True) and Nmin > C_run / W0)
# (c) the transition-cost floor
floor4 = npv_owner(uF=1.0, N=1e12, reb=True)
floorinf = npv_owner(uF=1.0, N=1e12, reb=True, Th=math.inf)
vbe = optimize.brentq(lambda v: npv_owner(uF=1.0, N=1e12, reb=True, Th=math.inf, varpi=v), 0.01, 1.0)
v4_one = npv_owner(uF=1.0, N=1e12, reb=True, varpi=1.0)
print(f"  -> floor NPV (all build and integration reused, rebuilt, unlimited scale): T_h = 4: {floor4:,.0f}; "
      f"T_h = inf: {floorinf:,.0f}; break-even success at T_h = inf {vbe:.3f}; at T_h = 4 with varpi = 1: {v4_one:,.0f}")
# Since the invoice example's regeneration of 2 Nov 2026 (engine success logits calibrated to varpi 0.70 for the
# reference process, Paper 1 round 2), the standalone varpi_p is 0.82, above the break-even varpi at T_h = infinity
# (0.73), so the floor with an unlimited horizon is positive at the firm's own varpi (it was negative at 0.62)
check("B6 prop:acq-owner(c): the floor bounds NPV^o for every capability (2,000 random capabilities) and is negative at "
      "the build's life T_h = 4 even with certain success; at T_h = infinity it is negative below the break-even varpi "
      "and positive above it, and the standalone varpi (0.82 since the invoice example's regeneration) is above it",
      all(npv_owner(uF=RNG.uniform(0, 1), N=RNG.uniform(1, 1e4), reb=bool(RNG.integers(0, 2)),
                    varpi=v, Th=th) <= npv_owner(uF=1.0, N=1e12, reb=True, varpi=v, Th=th) + 1e-6
          for v, th in zip(RNG.uniform(0.05, 1, 2000), RNG.choice([4.0, 10.0, math.inf], 2000)))
      and floor4 < 0 and v4_one < 0 and vbe < TR["varpi_p"] < 1 and (floorinf > 0) == (TR["varpi_p"] > vbe)
      and npv_owner(uF=1.0, N=1e12, reb=True, Th=math.inf, varpi=0.99 * vbe) < 0)
# monotonicity of the flip set (upper set) and the success condition
def dnpv_dvarpi(Wv, Th):
    pu = math.exp(-TR["T_par"] / TR["T_det"])
    return TR["bbar_p"] * Wv * S_r(TR["r"], TR["T_par"], Th) - math.exp(-TR["r"] * TR["T_par"]) * ((1 - pu) * TR["C_str"] - pu * TR["L_roll"])
ok = True
for _ in range(400):
    uF, N, v = RNG.uniform(0, 1), RNG.uniform(1, 1e3), RNG.uniform(0.2, 1)
    base_v = npv_owner(uF=uF, N=N, reb=True, varpi=v, Th=math.inf)
    ok &= npv_owner(uF=min(1, uF + 0.05), N=N, reb=True, varpi=v, Th=math.inf) >= base_v - 1e-9
    ok &= npv_owner(uF=uF, N=N * 1.5, reb=True, varpi=v, Th=math.inf) >= base_v - 1e-9
    if dnpv_dvarpi(W_owner(N, True), math.inf) >= 0:
        ok &= npv_owner(uF=uF, N=N, reb=True, varpi=min(1, v + 0.05), Th=math.inf) >= base_v - 1e-9
check("B7 prop:acq-owner(c): NPV^o is nondecreasing in u_F and N_pl, and in varpi^o where the success condition "
      "b W^o S_r >= e^{-rT_par}[(1 - p_u)C^str - p_u L_roll] holds, so the flipping capabilities form an upper set (400 draws)", ok)
# break-evens of single levers, the others at their most favorable value (certain success, full reuse, unlimited
# scale, permanent horizon): each is a condition, not a claim about any owner
floor_v1 = npv_owner(uF=1.0, N=1e12, reb=True, varpi=1.0, Th=math.inf)
N_be = optimize.brentq(lambda n: npv_owner(uF=1.0, N=n, reb=True, varpi=1.0, Th=math.inf), Nmin * 1.0001, 1e9)
uF_be = optimize.brentq(lambda u: npv_owner(uF=u, N=1e12, reb=True, varpi=1.0, Th=math.inf), 0.0, 1.0) \
    if npv_owner(uF=0.0, N=1e12, reb=True, varpi=1.0, Th=math.inf) < 0 else 0.0
Th_be = optimize.brentq(lambda th: npv_owner(uF=1.0, N=1e12, reb=True, varpi=1.0, Th=th), TR["T_par"] + 0.01, 500.0)
print(f"  -> with the other levers at their best: break-even varpi {vbe:.3f}; minimum N_pl {N_be:.1f}; minimum u_F "
      f"{uF_be:.3f}; minimum horizon {Th_be:.1f} years; floor at varpi = 1, T_h = inf: {floor_v1:,.0f}")
check("B8 prop:acq-owner(c): with certain success and a permanent horizon the floor is positive, and each single lever has "
      "a finite break-even (success, platform scale, reuse share, horizon) beyond the build's life",
      floor_v1 > 0 and Nmin < N_be < 1e9 and 0 <= uF_be < 1 and TR["T_h"] < Th_be < 500)
# (d) frictionless premium: p_max_o - p_max_pe = Delta V^cap / P0 (regime example firm, sec:regimes)
R_W = math.log(1 + 0.0934)          # sec:regimes public WACC preset, continuous
G_LBO, CFR, TAX, CTX, EB0 = 0.05, 0.55, 0.21, 0.02, 100.0     # prop:reg-lbo example (sec:regimes)
WE_P, C_P = 30.0, 40.0


def dEB(t, Tr, we=WE_P):
    return we * math.exp(G_LBO * t) * (min(t / Tr, 1.0) if Tr > 0 else 1.0)


def dCF(t, Tr, we=WE_P, cp=C_P):
    return (1 - TAX) * (dEB(t, Tr, we) - (cp / Tr if (Tr > 0 and t < Tr) else 0.0))


def Vprog(Tr, r=R_W, we=WE_P, cp=C_P):
    if not math.isfinite(Tr):
        return 0.0
    a = integrate.quad(lambda t: math.exp(-r * t) * dCF(t, Tr, we, cp), 0, Tr)[0] if Tr > 0 else -(1 - TAX) * cp
    return a + (1 - TAX) * we * math.exp((G_LBO - r) * Tr) / (r - G_LBO)


V_SQ = CFR * EB0 / (R_W - G_LBO)
check("B9 sec:regimes take-private firm reproduced: status quo 1,399.8 and program 551.1 at r_w (prop:reg-lbo example)",
      abs(V_SQ - 1399.8) < 0.05 and abs(Vprog(2.0) - 551.1) < 0.05, f"{V_SQ:.2f}, {Vprog(2.0):.2f}")
ok = True
for _ in range(100):
    P0 = V_SQ + RNG.uniform(0, 1) * Vprog(5.0)
    Vpe = Vprog(2.0)
    Vo = Vprog(2.0, we=WE_P * RNG.uniform(1.0, 2.0), cp=C_P * RNG.uniform(0.3, 1.0))
    def npv_fr(p, Vplan):       # frictionless: common rate, fair exit => value of the firm under the plan - outlay
        return V_SQ + Vplan - (1 + p + CTX) * P0
    p_pe = optimize.brentq(lambda p: npv_fr(p, Vpe), -5, 5)
    p_o = optimize.brentq(lambda p: npv_fr(p, Vo), -5, 5)
    ok &= abs((p_o - p_pe) * P0 - (Vo - Vpe)) < 1e-6 * P0
check("B10 prop:acq-owner(d): in the frictionless benchmark the owner's maximum premium exceeds the sponsor's by "
      "Delta V^cap / P0 exactly (100 draws)", ok)
# (e) learning: capability gain nondecreasing in the deal count when u_F, N_pl and varpi^o are
ok = True
for _ in range(200):
    epsL = RNG.uniform(0, 0.5)
    seq = [npv_owner(uF=min(1, 0.3 + 0.05 * i), N=1 + i, reb=True, varpi=min(1, 0.6 + 0.02 * i), Th=math.inf,
                     i=i, epsL=epsL) for i in range(1, 15)]
    ok &= all(b >= a - 1e-9 for a, b in zip(seq, seq[1:]))
check("B11 prop:acq-owner(e): with reuse, platform scale and success nondecreasing in the deal count (and the success "
      "condition), NPV^o of the i-th business is nondecreasing in i (200 draws)", ok)
mac("acqIcNpv", f"$-\\${num(-npv_sa / 1e6, 2)}$ million")
mac("acqIcWzero", f"\\${num(W0 / 1000, 1)} thousand")
mac("acqIcCrun", f"\\${num(C_run / 1000, 1)} thousand")
mac("acqIcCspec", f"\\${num(C_spec / 1000, 1)} thousand")
mac("acqIcCpool", f"\\${num((C_run - C_spec) / 1000, 1)} thousand")
mac("acqIcW", f"$-\\${num(-TR['W'] / 1000, 1)}$ thousand")
mac("acqIcF", f"\\${num(TR['F'] / 1e6, 2)} million")
mac("acqIcFreuse", f"\\${num((TR['F_build'] + TR['F_int']) / 1e6, 2)} million")
mac("acqIcVarpi", f"{TR['varpi_p']:.2f}")
mac("acqIcTh", f"{TR['T_h']:.0f}")
mac("acqIcNmin", f"{Nmin:.1f}")
mac("acqIcNminNoReb", f"{Nmin_nr:.1f}")
mac("acqIcLimNoReb", f"\\${num(lim_noreb / 1000, 1)} thousand")
mac("acqIcFloorFour", f"$-\\${num(-floor4 / 1000, 0)}$ thousand")
mac("acqIcFloorFourCertain", f"$-\\${num(-v4_one / 1000, 0)}$ thousand")
mac("acqIcFloorInf", (f"$-\\${num(-floorinf / 1000, 0)}$" if floorinf < 0 else f"\\${num(floorinf / 1000, 0)}") + " thousand")
mac("acqIcVarpiBe", f"{vbe:.2f}")
mac("acqIcNbe", f"{N_be:.0f}")
mac("acqIcUFbe", f"{uF_be:.2f}")
mac("acqIcThbe", f"{Th_be:.0f}")
mac("acqIcFloorVone", f"\\${num(floor_v1 / 1000, 0)} thousand")
mac("acqMaxConcurrentExact", f"{max_concurrent:.1f}")

# ==============================================================================================
header("C. Replace or transform in place (Assumption ass:acq-replace, Proposition prop:acq-replace)")
# ==============================================================================================
# program example of prop:ext-waves (sec:ext): 12 processes, $1M a year each, waves of T_par = 0.5; change capacity
# (320 affected FTE a year, 40 per process) caps waves at 4: plan 4, 4, 4 over 1.5 years
N_P, W_P, TPW, NCAP = 12, 1.0, 0.5, 4
r_c = R_W


def inplace_dates(N, ncap, T=TPW, Temb=TPW):
    out, k, left = [], 1, N
    while left > 0:
        n = min(ncap, left)
        out.append((n, Temb + (k - 1) * T))
        left -= n
        k += 1
    return out


def speed_gain(trpl, N=N_P, ncap=NCAP, W=W_P, r=r_c, T=TPW):
    return (W / r) * sum(n * (math.exp(-r * trpl) - math.exp(-r * t)) for n, t in inplace_dates(N, ncap, T, T))


# closed form for full waves
ok = True
for _ in range(300):
    r, T, K, n = RNG.uniform(0.02, 0.3), RNG.uniform(0.1, 1.5), int(RNG.integers(1, 12)), int(RNG.integers(1, 9))
    s_num = sum(math.exp(-r * (T + (k - 1) * T)) for k in range(1, K + 1))
    s_cf = math.exp(-r * T) * (1 - math.exp(-r * K * T)) / (1 - math.exp(-r * T))
    ok &= close(s_num, s_cf, 1e-10)
check("C1 prop:acq-replace(c): sum_k e^{-r t_k} = e^{-r T_emb}(1 - e^{-rKT})/(1 - e^{-rT}) for full waves (300 draws)", ok)
ok = all(speed_gain(t + 0.01) < speed_gain(t) for t in np.linspace(0.05, 2, 60)) and \
    all(speed_gain(0.5, ncap=c) >= speed_gain(0.5, ncap=c + 1) - 1e-12 for c in range(1, 12))
check("C2 prop:acq-replace(b): the speed gain falls with the replacement date and with in-place capacity", ok)
# legal leads of the labor example (prop:labor-lead example: 150 redundancies, five years' tenure)
LEADS = {"US": 0.16, "UK": 0.12, "IN": 0.08, "DE": 0.42, "FR": 0.47}
SEV_M = {"US": 3.0, "DE": 2.0, "FR": 1.0, "UK": 0.9}       # params.yaml severance_s_w_months (grounding b)
WAGE = 0.100                                                # $100,000 loaded wage of the labor example, $ millions
S_FIRM = 500.0                                              # prop:ext-waves example revenue, $ millions
gains = {}
for Tb in (0.25, 0.5):
    for c, L in LEADS.items():
        gains[(Tb, c)] = speed_gain(max(Tb, L))
g_in_place_bound = speed_gain(0.0)
print("  -> speed gains ($M):", {k: round(v, 2) for k, v in gains.items()}, " (t = 0 bound", round(g_in_place_bound, 2), ")")
gUS, gDE, gFR = gains[(0.25, "US")], gains[(0.25, "DE")], gains[(0.25, "FR")]
g_half = gains[(0.5, "US")]
check("C3 prop:acq-replace example: with a three-month build the gain is largest where leads are shortest (U.S., U.K., "
      "India at the build date) and smaller in Germany and France; with a six-month build every lead is slack",
      gains[(0.25, "US")] == gains[(0.25, "UK")] == gains[(0.25, "IN")] > gDE > gFR
      and len({round(gains[(0.5, c)], 12) for c in LEADS}) == 1)
be_fte = {c: gains[(0.25, c)] / (SEV_M[c] / 12 * WAGE) for c in SEV_M}
be_cust = {X: gUS / (X * S_FIRM) for X in (1.0, 8.0) + XBOUNDS}     # 8.0 kept only for the record (withdrawn weight)
print(f"  -> break-even extra displaced FTE (US gain): "
      f"{ {c: round(v) for c, v in be_fte.items()} }; break-even permanent revenue loss share at X = 1: {be_cust[1.0]:.4f}; "
      f"at the XBOUNDS placeholders " + ", ".join(f"X = {X:g}: {be_cust[X]:.4f}" for X in XBOUNDS))
check("C4 prop:acq-replace example: break-even extra displaced FTE = gain/(T^sev w) and break-even revenue share lost = "
      "gain/(X S) are computed from the same gain; the second scales as 1/X, so its sign never flips with X (evaluated at "
      "the XBOUNDS placeholders)",
      close(be_cust[1.0] / be_cust[8.0], 8.0, 1e-12) and all(v > 0 for v in be_fte.values())
      and all(close(be_cust[1.0] / be_cust[X], X, 1e-12) and be_cust[X] > 0 for X in XBOUNDS))
# (d) material weaknesses: bunching vs spreading (eq:acct-pmw with the accounting section's illustrative values)
T_OP, T_CL, P_DEF, P_MW, T_DC, T_REM = 0.25, 1 / 6, 0.3, 0.3, 0.25, 0.25   # prop:acct-cutover example (sec:accounting)
H_after = 1 - T_CL
P1 = P_DEF * P_MW * min(1.0, math.exp(-(H_after - T_REM - T_OP) / T_DC))
n_fin = 4
bunch = 1 - (1 - P1) ** n_fin
spread = n_fin * P1
P_cross = 1 - (1 - spread) ** (1 / n_fin)
print(f"  -> P_mw right after the close {P1:.4f}; four at once {bunch:.4f} vs four years {spread:.4f}; "
      f"bunching is worse if congestion lifts the per-cutover risk above {P_cross:.4f} (+{100*(P_cross/P1-1):.1f}%)")
ok = all(1 - (1 - p) ** n <= n * p + 1e-15 for p in np.linspace(0, 1, 101) for n in range(1, 30))
check("C5 prop:acq-replace(d): without congestion bunching n cutovers into one year never raises expected weakness-years "
      "(1 - (1 - P)^n <= nP); with P(n) the bunching cost exceeds spreading iff P(n) > 1 - (1 - nP(1))^{1/n}",
      ok and bunch < spread and abs(1 - (1 - P_cross) ** n_fin - spread) < 1e-12 and P_cross > P1)


# the date channel (accounting notes 4.8; verify_part2_accounting.py check 6k): replacement fixes the cutover date
def Pmw_H(H, pdef=P_DEF, pmw=P_MW, Tdc=T_DC, Trem=T_REM, Top=T_OP):
    return pdef * pmw * min(1.0, math.exp(-(H - Trem - Top) / Tdc))


P_late = Pmw_H(0.5)                                   # half a year or less to go: at the cap p_def p_mw
bunch_late = 1 - (1 - P_late) ** n_fin
H_x = T_REM + T_OP + T_DC * math.log(P_DEF * P_MW / P_cross)
z_x = 1 - H_x                                         # bunching at one date is worse once that date is later than z_x
ok = abs(P1 - 0.0237) < 1e-4 and abs(P_late - 0.09) < 1e-12 and abs(bunch_late - 0.3143) < 1e-4 and abs(z_x - 0.176) < 1e-3
# general condition: bunched at z (any congestion in p_def, T_dc, T_rem) vs spread right after closes
for _ in range(500):
    z = RNG.uniform(T_CL, 1 - T_OP)
    pdef_n, Tdc_n, Trem_n = P_DEF * RNG.uniform(1, 1.5), T_DC * RNG.uniform(1, 1.5), T_REM * RNG.uniform(1, 1.5)
    Pb = Pmw_H(1 - z, pdef_n, P_MW, Tdc_n, Trem_n)
    worse = 1 - (1 - Pb) ** n_fin > n_fin * P1
    ok &= worse == (Pb > 1 - (1 - n_fin * P1) ** (1 / n_fin))
    ok &= Pmw_H(1 - z, pdef_n, P_MW, Tdc_n, Trem_n) >= Pmw_H(1 - z) - 1e-15      # congestion raises P_mw
# per-weakness cost (cor:acct-npv): equal without congestion, bunching costlier with it
ok &= abs(n_fin * P1 - spread) < 1e-15
print(f"  -> date channel: P right after the close {P1:.4f}, with half a year or less to go {P_late:.4f}; four bunched late "
      f"{bunch_late:.4f} vs {spread:.4f} spread; bunching at one date is worse once it is later than z = {z_x:.3f} "
      f"({365 * (z_x - T_CL):.1f} days after the earliest open date); crossover P {P_cross:.4f} vs {P1:.4f}")
check("C7 prop:acq-replace(d) corrected: bunched at position z^rpl, bunching is worse iff P_mw(1 - z^rpl; congested) > "
      "1 - [1 - n P_mw(1 - T_cl)]^{1/n} (500 draws); with the accounting values 2.37% after a close, 9.0% with half a "
      "year or less to go, 31.4% for four bunched late against 9.5% spread; the date alone reverses the ranking after "
      "z = 0.176 (verify_part2_accounting.py check 6k)", ok)
# the cost of the replace path, calibrated on the company's reorganization-related expense
reorg_usd_ex = reorg_sh["2025"] * S_FIRM
reorg_ratio = reorg_usd_ex / gUS
check("C8 prop:acq-replace calibration: 2025's reorganization-related expense (6.0% of revenue) scaled to the example's "
      "$500M is $30.1M, about 3.6 times the U.S. speed gain of the twelve-process program",
      abs(reorg_usd_ex - 30.1) < 0.05 and abs(reorg_ratio - 3.57) < 0.02, f"{reorg_usd_ex:.2f}, {reorg_ratio:.3f}")
mac("acqMwOneExact", pct(P1, 2))
mac("acqMwLate", pct(P_late, 1))
mac("acqMwBunchLate", pct(bunch_late, 1))
mac("acqMwZ", num(z_x, 3))
mac("acqMwZdays", num(365 * (z_x - T_CL), 0))
mac("acqReorgUsdEx", f"\\${num(reorg_usd_ex, 1)} million")
mac("acqReorgRatio", num(reorg_ratio, 1))
# (e) attainable frontier: replacement dominates from t_rpl if no permanent penalty, and is overtaken otherwise
ok = True
for _ in range(300):
    dR, N, ncap = RNG.uniform(0.001, 0.02), int(RNG.integers(2, 30)), int(RNG.integers(1, 10))
    trpl, pen = RNG.uniform(0.1, 1.0), RNG.uniform(0, 0.05)
    T = TPW
    def R_ip(t):
        n = 0 if t < T else int((t - T) // T) + 1
        return dR * min(N, n * ncap)
    def R_rp(t, pen=pen):
        return (N * dR - pen) if t >= trpl else 0.0
    ts = np.linspace(0, 20, 400)
    if pen == 0:
        ok &= all(R_rp(t, 0.0) >= R_ip(t) - 1e-12 for t in ts if t >= trpl)
    cross = [t for t in ts if t >= trpl and R_ip(t) > R_rp(t) + 1e-12]
    if pen > 0 and N * dR - pen < N * dR:
        ok &= len(cross) > 0 and all(R_ip(t) >= R_rp(t) - 1e-12 for t in ts if t >= cross[0])
check("C6 prop:acq-replace(e): with additive process gains, replacement's attainable score dominates in-place from t^rpl "
      "when it carries no permanent penalty, and a permanent penalty creates a crossing after which in place dominates "
      "(300 draws)", ok)
for k, v in {"acqRpGainUS": num(gUS, 2), "acqRpGainDE": num(gDE, 2), "acqRpGainFR": num(gFR, 2),
             "acqRpGainHalf": num(g_half, 2), "acqRpGainBound": num(g_in_place_bound, 2),
             "acqRpFteUS": num(be_fte["US"], 0), "acqRpFteDE": num(be_fte["DE"], 0), "acqRpFteFR": num(be_fte["FR"], 0),
             "acqRpFteUK": num(be_fte["UK"], 0), "acqRpCustOne": pct(be_cust[1.0], 2), "acqRpCustEight": pct(be_cust[8.0], 2),
             "acqRpCustXbOne": pct(be_cust[XBOUNDS[0]], 2), "acqRpCustXbTwo": pct(be_cust[XBOUNDS[1]], 2),
             "acqRpCustXbThree": pct(be_cust[XBOUNDS[2]], 2),
             "acqXbOne": f"{XBOUNDS[0]:g}", "acqXbTwo": f"{XBOUNDS[1]:g}", "acqXbThree": f"{XBOUNDS[2]:g}",
             "acqMwOne": pct(P1, 1), "acqMwBunch": pct(bunch, 1), "acqMwSpread": pct(spread, 1),
             "acqMwCross": pct(P_cross, 2), "acqMwCrossRise": pct(P_cross / P1 - 1, 0)}.items():
    mac(k, v)

# ==============================================================================================
header("D. Permanent-capital serial acquirer (Assumption ass:acq-pc, Proposition prop:acq-pc)")
# ==============================================================================================
IRR_U = math.log(1 + hurU / 100)
IRR_L = math.log(1 + hurL / 100)
R_PE = math.log(1.22)
RDEBT_REG = math.log(1.08)        # sec:regimes debt preset, 8% annual: reproduces the sponsor of prop:reg-lbo
RDEBT = R_DEBT_NOTES              # the company's marginal cost of debt: coupon of its first secured notes (USD), 28 Oct 2026
LTV = ltv_pct / 100
T_IRR, T_REP = irr_years, rep_years
R_TV = R_W                        # illustrative: the F-1's own WACC is not in the extract (class b, practitioner WACC)
print(f"  -> hurdles continuous: unlevered {IRR_U:.4f}, levered {IRR_L:.4f}; PE 22% -> {R_PE:.4f}")
check("D0 annual hurdles converted with ln(1 + r): 25% -> 22.31%, 65% -> 50.08%, 22% -> 19.89%",
      round(IRR_U, 4) == 0.2231 and round(IRR_L, 4) == 0.5008 and round(R_PE, 4) == 0.1989)


def pv(fcf, rho, a, b, pts=None):
    return integrate.quad(lambda t: math.exp(-rho * t) * fcf(t), a, b, points=pts, limit=400)[0]


def tv_at(fcf, w, T, horizon=600.0, pts=None):
    return integrate.quad(lambda t: math.exp(-w * (t - T)) * fcf(t), T, T + horizon, points=pts, limit=400)[0]


def method_value(fcf, rho, w=R_TV, T=T_IRR, pts=None):
    return pv(fcf, rho, 0, T, pts) + math.exp(-rho * T) * tv_at(fcf, w, T)


def perp_value(fcf, rho, pts=None, horizon=600.0):
    return pv(fcf, rho, 0, horizon, pts)


def irr_of(valfun, P, lo=-0.5, hi=5.0):
    return optimize.brentq(lambda x: valfun(x) - P, lo, hi)


def levered_method_irr(fcf, P, w=R_TV, T=T_IRR, rd=RDEBT, ltv=LTV, Trep=T_REP, pts=None):
    ndrep = pv(fcf, rd, 0, Trep, pts)
    nd0 = min(ltv * P, ndrep)
    cum = lambda t: pv(fcf, rd, 0, t, pts)
    if cum(T) < nd0 - 1e-9:
        TD = None
    elif abs(nd0 - ndrep) < 1e-12 and Trep == T:
        TD = T
    else:
        TD = optimize.brentq(lambda t: cum(t) - nd0, 1e-12, T)
    resid = max(math.exp(rd * T) * (nd0 - cum(T)), 0.0)
    E0 = P - nd0
    def eqv(rho):
        a = pv(fcf, rho, TD, T, pts) if TD is not None and TD < T else 0.0
        return a + math.exp(-rho * T) * (tv_at(fcf, w, T) - resid)
    return irr_of(eqv, E0, -0.5, 50.0), nd0, ndrep, TD, E0


# (a) method vs perpetual IRR, and (b) price bounds, on random piecewise-exponential FCF paths
okA, okB, okC = True, True, True
for _ in range(150):
    f0, f1 = RNG.uniform(0, 0.2), RNG.uniform(0.1, 0.6)
    Gx, trun = RNG.uniform(-0.15, 0.05), RNG.uniform(0, 3)
    w = RNG.uniform(0.06, 0.14)
    fcf = (lambda f0, f1, Gx, trun: (lambda t: math.exp(Gx * t) * (f0 if t < trun else f1)))(f0, f1, Gx, trun)
    pts = [trun] if 0 < trun < T_IRR else None
    P = RNG.uniform(0.3, 1.5) * method_value(fcf, w, w, pts=pts)
    im = irr_of(lambda x: method_value(fcf, x, w, pts=pts), P, w - 0.3, 5)
    ip = irr_of(lambda x: perp_value(fcf, x, pts=pts), P, Gx + 1e-3, 5)
    okA &= (im >= ip - 1e-7) == (ip >= w - 1e-7)
    rb = RNG.uniform(w, 0.6)
    Pm, Vw = method_value(fcf, rb, w, pts=pts), method_value(fcf, w, w, pts=pts)
    okB &= math.exp(-(rb - w) * T_IRR) * Vw - 1e-9 <= Pm <= Vw + 1e-9
    il, nd0, ndrep, TD, E0 = levered_method_irr(fcf, P, w, pts=pts)
    okC &= (il > im) == (im > RDEBT) or abs(im - RDEBT) < 1e-6
check("D1 prop:acq-pc(a): method IRR >= permanent IRR iff permanent IRR >= r_tv (150 random cash-flow paths)", okA)
check("D2 prop:acq-pc(b): e^{-(i - r_tv)T} V^tv <= P^max(i) <= V^tv for every hurdle i >= r_tv (150 paths)", okB)
check("D3 prop:acq-pc(c)(i): levered IRR > unlevered IRR iff unlevered IRR > r_debt, under the disclosed debt policy "
      "(150 paths)", okC)
# (c)(iii) closed form when the repayment cap binds
ok = True
for _ in range(60):
    f1, Gx = RNG.uniform(0.1, 0.6), RNG.uniform(-0.12, 0.05)
    fcf = (lambda f1, Gx: (lambda t: f1 * math.exp(Gx * t)))(f1, Gx)
    P = 2.0 * pv(fcf, RDEBT, 0, T_REP) / LTV      # makes LTV P > ND_rep, so the repayment cap binds
    il, nd0, ndrep, TD, E0 = levered_method_irr(fcf, P)
    cf = math.log(tv_at(fcf, R_TV, T_IRR) / (P - ndrep)) / T_IRR
    ok &= abs(nd0 - ndrep) < 1e-9 and abs(il - cf) < 1e-7
check("D4 prop:acq-pc(c)(iii): when ND^rep binds and T^rep = T^IRR, the levered method IRR is ln[TV/(P - ND^rep)]/T", ok)

# (d) the regime example firm of prop:reg-lbo, bought at the take-private price
PREM, M_ENT = 0.30, 1.30 * V_SQ / EB0
P_TP = (1 + PREM + CTX) * V_SQ
def fcf_firm(t, Tr=2.0, we=WE_P, cp=C_P):
    return CFR * EB0 * math.exp(G_LBO * t) + dCF(t, Tr, we, cp)
ptsF = [2.0]
im_tp = irr_of(lambda x: method_value(lambda t: fcf_firm(t), x, pts=ptsF), P_TP, 0.051, 3)
ip_tp = irr_of(lambda x: perp_value(lambda t: fcf_firm(t), x, pts=ptsF), P_TP, 0.051, 3)
il_tp = levered_method_irr(lambda t: fcf_firm(t), P_TP, pts=ptsF)
# the sponsor's deal of prop:reg-lbo: levered break-even (regimes) and its unlevered IRR (exit at the multiple paid)
LEV0, T_HOLD = 5.2, 6.0
def sponsor_npv(rpe, hx=1.0):
    ND0 = LEV0 * EB0
    EBT = EB0 * math.exp(G_LBO * T_HOLD) + hx * dEB(T_HOLD, 2.0)
    FV = integrate.quad(lambda t: math.exp(RDEBT_REG * (T_HOLD - t)) * fcf_firm(t), 0, T_HOLD, points=[2.0])[0]
    EqT = M_ENT * EBT - (ND0 * math.exp(RDEBT_REG * T_HOLD) - FV)
    return math.exp(-rpe * T_HOLD) * EqT - ((1 + PREM + CTX) * V_SQ - ND0)
rbe = optimize.brentq(sponsor_npv, -0.5, 1.0)
EBT1 = EB0 * math.exp(G_LBO * T_HOLD) + dEB(T_HOLD, 2.0)
iu_sp = irr_of(lambda x: pv(lambda t: fcf_firm(t), x, 0, T_HOLD, [2.0]) + math.exp(-x * T_HOLD) * M_ENT * EBT1, P_TP, -0.2, 2)
check("D5 sec:regimes reproduced: multiple paid 18.2x and the sponsor's levered break-even hurdle 13.5% continuous "
      "(14.4% annual) at h_x = 1", abs(M_ENT - 18.20) < 0.005 and abs(rbe - 0.1346) < 0.0005 and abs(math.exp(rbe) - 1 - 0.144) < 0.0005)
Pmax_m = method_value(lambda t: fcf_firm(t), IRR_U, pts=ptsF)
Pmax_p = perp_value(lambda t: fcf_firm(t), IRR_U, pts=ptsF)
Vtv_plan = method_value(lambda t: fcf_firm(t), R_TV, pts=ptsF)
bound_fac = math.exp(-(IRR_U - R_TV) * T_IRR)
we_need = optimize.brentq(lambda we: method_value(lambda t: fcf_firm(t, 2.0, we), IRR_U, pts=ptsF) - P_TP, 0, 3000)
we_need_fast = optimize.brentq(lambda we: method_value(lambda t: fcf_firm(t, 0.5, we), IRR_U, pts=[0.5]) - P_TP, 0, 3000)
print(f"  -> at the take-private price ({P_TP/EB0:.2f}x EBITDA with costs): method IRR {im_tp:.4f} ({math.exp(im_tp)-1:.4f}), "
      f"permanent {ip_tp:.4f}, levered under the policy {il_tp[0]:.4f}; sponsor's deal unlevered {iu_sp:.4f}, levered "
      f"break-even {rbe:.4f}")
print(f"  -> P^max at the 25% hurdle: method {Pmax_m/EB0:.2f}x EBITDA ({Pmax_m/Vtv_plan:.3f} of V^tv; bound {bound_fac:.3f}), "
      f"permanent {Pmax_p/EB0:.2f}x; uplift needed at the price: {we_need/EB0:.2f} of EBITDA (t_run = 2), "
      f"{we_need_fast/EB0:.2f} (t_run = 0.5) vs 0.30 in the program")
check("D6 prop:acq-pc example: at the take-private price the permanent-capital owner's unlevered method IRR is below the "
      "sponsor's levered break-even and far below 25%; the hurdle needs an entry multiple of at most P^max/EB0 or a run-rate "
      "uplift several times the program's",
      im_tp < rbe < IRR_U and ip_tp < im_tp and iu_sp < rbe and Pmax_m < P_TP and we_need > 3 * WE_P
      and bound_fac <= Pmax_m / Vtv_plan <= 1)
# revenue-based grid: a business bought after its growth phase (no FCF before t_run = 1, FCF margin f1 after)
GRID = {}
for nrr in (nrr24, nrr25):
    Gx = math.log(nrr)
    for f1 in (0.3, 0.4, 0.5):
        fcf = (lambda f1, Gx: (lambda t: 100.0 * math.exp(Gx * t) * (0.0 if t < 1.0 else f1)))(f1, Gx)
        Pm = method_value(fcf, IRR_U, pts=[1.0])
        Pp = perp_value(fcf, IRR_U, pts=[1.0])
        il = levered_method_irr(fcf, Pm, pts=[1.0])
        GRID[(nrr, f1)] = (Pm / 100, Pp / 100, il[0])
for k, v in GRID.items():
    print(f"  -> NRR {k[0]:.2f}, f1 {k[1]:.1f}: P^max/S0 method {v[0]:.2f}, permanent {v[1]:.2f}; levered IRR at P^max {v[2]:.4f}")
lev_at_hurdle = [v[2] for v in GRID.values()]
check("D7 prop:acq-pc grid: P^max/S0 rises with the post-transformation margin and with retention; at the unlevered hurdle "
      "the levered method IRR is below the levered hurdle in every cell",
      all(GRID[(n, 0.3)][0] < GRID[(n, 0.4)][0] < GRID[(n, 0.5)][0] for n in (nrr24, nrr25))
      and all(GRID[(nrr24, f)][0] < GRID[(nrr25, f)][0] for f in (0.3, 0.4, 0.5)) and max(lev_at_hurdle) < IRR_L)
# the unlevered method IRR implied by the levered hurdle, flat-margin businesses
UNL_FOR_L = {}
for nrr in (nrr24, nrr25, 1.0):
    Gx = math.log(nrr)
    fcf = (lambda Gx: (lambda t: math.exp(Gx * t)))(Gx)
    Pl = optimize.brentq(lambda P: levered_method_irr(fcf, P)[0] - IRR_L, 0.6, 30)
    UNL_FOR_L[nrr] = irr_of(lambda x: method_value(fcf, x), Pl, -0.3, 3)
print("  -> unlevered method IRR at the levered hurdle:", {k: round(v, 4) for k, v in UNL_FOR_L.items()})
check("D8 prop:acq-pc(c): for flat-margin businesses the levered hurdle implies an unlevered method IRR above the "
      "unlevered hurdle, so the levered hurdle binds (NRR 91%, 95%, 100%)", min(UNL_FOR_L.values()) > IRR_U)
# the 424B4 purchase prices against the grid's admissible prices (no FCF in year 1, margin f1 afterwards)
grid_max = max(v[0] for v in GRID.values())
aol_opm = a1 / pf_aol                                  # AOL's pre-acquisition operating margin in the pro forma (2025)
check("D10 prop:acq-pc grid against the 424B4 prices: Eventbrite (1.7x revenue) lies inside the grid's admissible range "
      "(up to 1.82x at f1 = 0.5 and NRR 95%), AOL (2.3x) and Vimeo (3.2x) above it; AOL's own 2025 operating margin in the "
      "pro forma is 53%",
      k_deal["Eventbrite"] < grid_max < k_deal["AOL"] < k_deal["Vimeo"] and abs(aol_opm - 0.527) < 0.001,
      f"grid max {grid_max:.2f}, AOL margin {aol_opm:.4f}")
mac("acqGridMax", num(grid_max, 2))
mac("acqAolOpm", pct(aol_opm, 0))
# Brightcove (reported): price over 2024 revenue guidance midpoint
BC_PRICE, BC_REV_LO, BC_REV_HI = 233.0, 197.7, 198.7       # StreamingMedia blog, 25 Nov 2024 (secondary)
bc_ps = BC_PRICE / ((BC_REV_LO + BC_REV_HI) / 2)
# growth weights at the hurdle versus a public owner (prop:reg-weight(c), tau -> infinity)
Gi25 = math.log(nrr25)
xg_ratio = (R_W - Gi25) / (IRR_U - Gi25)
check("D9 prop:acq-pc(e) / prop:acq-retention(d): X^G(r_pc)/X^G(r_w) = (r_w - G_i)/(r_pc - G_i) (symbolic) and its value "
      "at G_i = ln NRR(2025)",
      sp.simplify(sp.Symbol("m") / (sp.Symbol("rp") - sp.Symbol("G")) / (sp.Symbol("m") / (sp.Symbol("rw") - sp.Symbol("G")))
                  - (sp.Symbol("rw") - sp.Symbol("G")) / (sp.Symbol("rp") - sp.Symbol("G"))) == 0 and 0 < xg_ratio < 1,
      f"{xg_ratio:.3f}")
for k, v in {"acqIrrU": pct(IRR_U, 1), "acqIrrL": pct(IRR_L, 1), "acqIrrPe": pct(R_PE, 1),
             "acqRtv": pct(R_TV, 2), "acqRdebt": pct(RDEBT, 2), "acqRdebtReg": pct(RDEBT_REG, 1), "acqTpPrice": num(P_TP / EB0, 1),
             "acqTpMult": num(M_ENT, 1), "acqTpIm": pct(im_tp, 1), "acqTpImAnn": pct(math.exp(im_tp) - 1, 1),
             "acqTpIp": pct(ip_tp, 1), "acqTpIl": pct(il_tp[0], 1), "acqTpBe": pct(rbe, 1), "acqTpBeAnn": pct(math.exp(rbe) - 1, 1),
             "acqTpIuSp": pct(iu_sp, 1), "acqTpPmaxM": num(Pmax_m / EB0, 1), "acqTpPmaxP": num(Pmax_p / EB0, 1),
             "acqTpPmaxShare": pct(Pmax_m / Vtv_plan, 0), "acqBoundFac": num(bound_fac, 2),
             "acqTpUplift": pct(we_need / EB0, 0), "acqTpUpliftFast": pct(we_need_fast / EB0, 0),
             "acqGridMthreeA": num(GRID[(nrr25, 0.3)][0], 2), "acqGridMfourA": num(GRID[(nrr25, 0.4)][0], 2),
             "acqGridMfiveA": num(GRID[(nrr25, 0.5)][0], 2), "acqGridPfourA": num(GRID[(nrr25, 0.4)][1], 2),
             "acqGridMfourB": num(GRID[(nrr24, 0.4)][0], 2), "acqGridPfourB": num(GRID[(nrr24, 0.4)][1], 2),
             "acqGridLevMin": pct(min(lev_at_hurdle), 0), "acqGridLevMax": pct(max(lev_at_hurdle), 0),
             "acqUnlForLMin": pct(min(UNL_FOR_L.values()), 0), "acqUnlForLMax": pct(max(UNL_FOR_L.values()), 0),
             "acqBcPs": num(bc_ps, 1), "acqXgRatio": num(xg_ratio, 2),
             "acqGiTwentyFive": pct(Gi25, 1)}.items():
    mac(k, v)

# ==============================================================================================
header("E. Paper 1: growth that is bought (Definition def:acquired-growth, Proposition prop:acquired-score)")
# ==============================================================================================
X, go, ga, m, kacq, cf = sp.symbols("X g_o g_a m k_acq c_fin")
RA = X * (go + ga) + m - kacq * ga
check("E1 prop:acquired-score(a): R^A_X = (X g^org + m) + (X - k^acq) g^acq (symbolic)",
      sp.simplify(RA - ((X * go + m) + (X - kacq) * ga)) == 0)
check("E2 prop:acquired-score(a): acquired growth raises the cash score iff k^acq < X; for the Rule of 40 iff k^acq < 1",
      sp.diff(RA, ga) == X - kacq)
# (b) bang-bang: maximize over spend (Part I technology, eq:Rstar) and g_acq in [0, abar]
ALPHA_ = 0.3
CA_ = (1 - ALPHA_) * ALPHA_ ** (ALPHA_ / (1 - ALPHA_))
def Rstar_I(Xw, m0, k, G, lam):
    y = max(Xw - k, 0.0)
    return m0 + (Xw - k) * G + CA_ * (lam * y) ** (1 / (1 - ALPHA_))
ok = True
for _ in range(300):
    Xw, m0, k, G, lam = RNG.uniform(0.5, 10), RNG.uniform(0.1, 0.6), RNG.uniform(0, 0.4), RNG.uniform(-0.1, 0.2), RNG.uniform(0.02, 0.6)
    ka, abar = RNG.uniform(0.3, 12), RNG.uniform(0, 0.5)
    sig = np.linspace(0, 3, 3001)
    org = (m0 - sig - k * (G + lam * sig ** ALPHA_)) + Xw * (G + lam * sig ** ALPHA_)
    best = max(org.max() + (Xw - ka) * a for a in np.linspace(0, abar, 51))
    cf_ = Rstar_I(Xw, m0, k, G, lam) + max(Xw - ka, 0.0) * abar
    ok &= abs(best - cf_) < 2e-3 * (1 + abs(cf_)) and best <= cf_ + 1e-9
check("E3 prop:acquired-score(b): max over spend and acquisitions = R*_X + (X - k^acq)^+ abar (eq:acquired-Rstar; "
      "300 draws, grid search against the closed form)", ok)
# (d) the existing base under NRR (Fable theory F21): the base contributes (S_sub/S)(NRR - 1) + (1 - S_sub/S) gamma_ns to
# annual organic growth before new customers, so its continuously compounded zero-spend growth is
# G_i = ln[1 + (S_sub/S)(NRR - 1) + (1 - S_sub/S) gamma_ns]: ln NRR only if all revenue is subscription revenue
base_25 = nrr25 - 1
needed_25 = g25 - base_25
sg, nr, gm_ = sp.symbols("sigma NRR gamma_ns", real=True)
Gi_s = sp.log(1 + sg * (nr - 1) + (1 - sg) * gm_)
ok = sp.simplify(Gi_s.subs(sg, 1) - sp.log(nr)) == 0 and sp.simplify(Gi_s.subs(gm_, nr - 1) - sp.log(nr)) == 0
for _ in range(2000):
    n_, s_ = RNG.uniform(0.80, 0.999), RNG.uniform(0, 1)
    gmv = RNG.uniform(n_ - 1, 0.0)
    gi_v = math.log(1 + s_ * (n_ - 1) + (1 - s_) * gmv)
    ok &= math.log(n_) - 1e-12 <= gi_v <= 1e-12
    # the annual change of a two-part base, compounded, equals exp(G_i): the referee's conversion with ln(1 + r)
    S0s, S0n = s_, 1 - s_
    ok &= close(math.exp(gi_v), S0s * n_ + S0n * (1 + gmv), 1e-12)
# treadmill in continuous time: dS/dt = (g_acq - d_org) S, so holding g needs g_acq = g + d_org
tt, a_s, d_s = sp.symbols("t a d", real=True)
Sfun = sp.Function("S")
sol = sp.dsolve(sp.Eq(Sfun(tt).diff(tt), (a_s - d_s) * Sfun(tt)), Sfun(tt)).rhs
ok &= sp.simplify(sp.diff(sp.log(sol), tt) - (a_s - d_s)) == 0
check("E4 prop:acquired-score(d) and (f) after Fable F21: G_i = ln[1 + (S_sub/S)(NRR - 1) + (1 - S_sub/S) gamma_ns] equals "
      "ln NRR when all revenue is subscription revenue (or the rest also retains at NRR) and lies in [ln NRR, 0] when NRR < 1 "
      "and gamma_ns in [NRR - 1, 0] (2,000 draws); exp(G_i) is the annual ratio of the base; with acquisitions at a and "
      "organic decay d revenue grows at a - d, so holding g needs g^acq = g + d^org (symbolic); in 2025 the subscription base "
      "fell by 1 - NRR = 5% before new customers",
      ok and abs(base_25 + 0.05) < 1e-12 and needed_25 > g25)
# (c) score after interest on the operating-margin basis
check("E5 prop:acquired-score(c): the operating-margin score exceeds the score after interest by the interest share "
      "(2025 and Q1 2026)", abs((R25_gaap - R25_int) - cfin["2025"]) < 1e-12 and abs((Rq1_gaap - Rq1_int) - cfin["Q1 2026"]) < 1e-12)
# (e) per-business share budget: the firm's budget is a sum over acquired businesses (prop:budget with rem:assumptions(b))
ok = True
for _ in range(200):
    nb = int(RNG.integers(1, 6))
    budgets = [(RNG.uniform(0.2, 5), RNG.uniform(1e-4, 0.3), RNG.uniform(-0.1, 0.1), RNG.uniform(1, 10)) for _ in range(nb)]
    terms = [y * (math.log(0.5 / s0) + dG * T) for y, s0, dG, T in budgets if dG >= 0]
    ok &= all(t >= 0 for t in terms) and (sum(terms) >= max(terms) - 1e-12 if terms else True)
check("E6 prop:acquired-score(e): each acquired business adds a nonnegative budget (X - k)[ln(s_bar/s_b) + (G - G_i)T] "
      "when its retention lags the market, so the firm's budget is a sum over acquisitions (200 draws)", ok)
mac("acqBaseTwentyFive", pct(-base_25, 0))
mac("acqNeededTwentyFive", pct(needed_25, 1))
mac("acqGiTwentyFour", pct(math.log(nrr24), 1))

# Bounds on the score when growth is bought (rem:acquired-bounds). Upper: the price of acquisitions is left out (GAAP,
# after interest, operating cash flow). Lower: every net investing outflow is charged in the year it is paid. Middle:
# each year's outflow since 2023 is charged as a level annuity at the continuous public WACC preset r_w over the mean
# life of revenue decaying at -ln NRR, with NRR at the low and high ends of the portfolio's reported range (scenario).
YRS = ["2024", "2025"]
g_y = {"2024": g24, "2025": g25}
R_gaap = {y: g_y[y] + mop[y] for y in YRS}
R_int = {y: g_y[y] + m_after_int[y] for y in YRS}
R_ocf = {y: g_y[y] + mocf[y] for y in YRS}
R_full = {y: g_y[y] + (OCF[y] + CFI[y]) / REV[y] for y in YRS}
target = {"2024": (92.3, 87.5, 103.9, -28.7, 132.6), "2025": (115.9, 105.0, 116.9, -24.8, 141.8)}
ok = all(round(100 * R_gaap[y], 1) == target[y][0] and round(100 * R_int[y], 1) == target[y][1]
         and round(100 * R_ocf[y], 1) == target[y][2] and round(100 * R_full[y], 1) == target[y][3]
         and round(100 * cfi_share[y], 1) == target[y][4] for y in YRS)
print("  -> bounds (points): " + "; ".join(f"{y}: GAAP {100*R_gaap[y]:.1f}, after interest {100*R_int[y]:.1f}, "
                                          f"OCF {100*R_ocf[y]:.1f}, fully charged {100*R_full[y]:.1f}" for y in YRS))
check("E7 rem:acquired-bounds: the coordinator's bounds recomputed from the tables: GAAP 92.3 / 115.9, after interest "
      "87.5 / 105.0, operating cash flow 103.9 / 116.9, fully charged after interest -28.7 / -24.8 (2024 / 2025; round-1 "
      "basis, operating cash flow after interest paid less the net investing outflow, kept as a regression check; Table 3 "
      "uses the before-interest -25.0 / -16.5 of acqRAllInvU*); net investing outflow 132.6% / 141.8% of revenue", ok)


def crf(r, L):
    """continuous capital recovery factor: level annual charge per dollar repaying it at rate r over L years"""
    return r / (1.0 - math.exp(-r * L))


NRR_RANGE = sorted([nrr23, nrr24, nrr25, nrrq1])
nrr_lo, nrr_hi = NRR_RANGE[0], NRR_RANGE[-1]
LIFE = {n: 1.0 / -math.log(n) for n in (nrr_lo, nrr_hi)}          # mean life of revenue decaying at -ln NRR (scenario)
CRF = {n: crf(R_W, LIFE[n]) for n in LIFE}
OUT = {c: -CFI[c] for c in ["2023", "2024", "2025"]}
CUM = {"2024": OUT["2023"] + OUT["2024"], "2025": OUT["2023"] + OUT["2024"] + OUT["2025"]}
R_ann = {(y, n): R_ocf[y] - CRF[n] * CUM[y] / REV[y] for y in YRS for n in LIFE}
ann_lo = {y: min(R_ann[(y, n)] for n in LIFE) for y in YRS}
ann_hi = {y: max(R_ann[(y, n)] for n in LIFE) for y in YRS}
print(f"  -> NRR range {nrr_lo:.2f}-{nrr_hi:.2f}: mean life {LIFE[nrr_lo]:.1f}-{LIFE[nrr_hi]:.1f} years, CRF at r_w "
      f"{CRF[nrr_lo]:.4f}-{CRF[nrr_hi]:.4f}; annuity-charged score " +
      "; ".join(f"{y}: {100*ann_lo[y]:.1f} to {100*ann_hi[y]:.1f}" for y in YRS))
# symbolic: CRF -> 1/L as r -> 0, -> r as L -> inf, and CRF(r, L) * PV-annuity(r, L) = 1
rs, Ls = sp.symbols("r L", positive=True)
crf_s = rs / (1 - sp.exp(-rs * Ls))
ok = (sp.simplify(sp.limit(crf_s, rs, 0) - 1 / Ls) == 0
      and sp.simplify(crf_s * sp.integrate(sp.exp(-rs * sp.Symbol("t")), (sp.Symbol("t"), 0, Ls)) - 1) == 0)
ok &= all(R_full[y] < ann_lo[y] <= ann_hi[y] < R_ocf[y] for y in YRS) and all(CRF[n] < 1 for n in LIFE)
ok &= all(CRF[n] * CUM[y] < OUT[y] for y in YRS for n in LIFE)
check("E8 rem:acquired-bounds middle case: CRF(r, L) = r / (1 - e^{-rL}) repays a dollar at r over L (symbolic; 1/L as "
      "r -> 0); with the NRR range as a scenario the annuity-charged score lies strictly between the bounds in both years, "
      "because the annuity on all outflows since 2023 is below the current year's outflow", ok)
for n, tag in ((nrr_lo, "Lo"), (nrr_hi, "Hi")):
    mac(f"acqNrr{tag}", pct(n, 0))
    mac(f"acqLife{tag}", num(LIFE[n], 1))
    mac(f"acqCrf{tag}", pct(CRF[n], 1))
for y, w in (("2024", "TwentyFour"), ("2025", "TwentyFive")):
    mac(f"acqRGaap{w}", num(100 * R_gaap[y], 1))
    mac(f"acqRInt{w}", num(100 * R_int[y], 1))
    mac(f"acqROcf{w}", num(100 * R_ocf[y], 1))
    mac(f"acqRAllInv{w}", num(100 * R_full[y], 1))
    mac(f"acqRAnnLo{w}", num(100 * ann_lo[y], 1))
    mac(f"acqRAnnHi{w}", num(100 * ann_hi[y], 1))
    mac(f"acqCumOut{w}", num(CUM[y] / REV[y], 2))
mac("acqRw", pct(R_W, 2))
mac("acqRwAnnual", pct(math.exp(R_W) - 1, 2))

# ----------------------------------------------------------------------------------------------
# E12-E14 (round 2, IB-4 and the Fable finance referee): the charges at a cost of capital set against a margin BEFORE
# interest, so that financing is not charged twice. Operating cash flow is after interest paid under U.S. GAAP (A15);
# the margin before financing adds back interest net of the tax it saves, at tau = 0 or Italy's IRES rate (A15).
# Interest paid for 2025 is not in the documents read: interest expense stands in for it (interest paid was 80-90% of
# interest expense in the first halves of 2025 and 2026), so the add-back is if anything too large.
# Conventions: (A) level annuity CRF(r, T^life) on every outlay since 2023 for the full year (the earlier middle case);
# (B) user cost (r + d) on capital decayed at d = -ln NRR, at year-end (Hall and Jorgenson 1967; rem:assumptions(c));
# (C) the same on the time-weighted average of decayed capital over the year; (D) the level annuity charged only from
# the date of each outlay. Timing: 2023 and 2024 outlays at mid-year; 2025 by quarter and half from the extract (Q1
# 2025 and H1 2025 investing outflows), the second-half outflow between mid-H2 and Vimeo's close (24 Nov 2025).
# ----------------------------------------------------------------------------------------------
TAUS = (0.0, TAU_IRES)
m_unlev = {(c, tau): mocf[c] + (1 - tau) * cfin[c] for c in ("2024", "2025", "Q1 2026") for tau in TAUS}
R_ocf_u = {(c, tau): {"2024": g24, "2025": g25, "Q1 2026": gq1}[c] + m_unlev[(c, tau)] for c, tau in m_unlev}
R_full_u = {(c, tau): R_ocf_u[(c, tau)] + CFI[c] / REV[c] for c, tau in m_unlev}
q1_25_out = -CFI["Q1 2025"]
h1_25_out = -H1["H1 2025"]["Net cash from investing activities"]
VIM_T = vim_days / 365.0                                            # Vimeo closed on 24 Nov 2025, after 327 days of the year
H2_TIMES = (0.75, VIM_T)


def flows_for(y, h2):
    """(outlay, date within year y) pairs; dates <= 0 are outlays of earlier years"""
    if y == "2024":
        return [(OUT["2023"], -0.5), (OUT["2024"], 0.5)]
    return [(OUT["2023"], -1.5), (OUT["2024"], -0.5), (q1_25_out, 0.125), (h1_25_out - q1_25_out, 0.375),
            (OUT["2025"] - h1_25_out, h2)]


def capital(y, d, h2):
    fl = flows_for(y, h2)
    cum = sum(c for c, _ in fl)
    end = sum(c * math.exp(-d * (1 - t)) for c, t in fl)
    avg_d = sum(c * (math.exp(d * t) * (1 - math.exp(-d)) / d if t <= 0 else (1 - math.exp(-d * (1 - t))) / d) for c, t in fl)
    avg_0 = sum(c * (1.0 if t <= 0 else 1 - t) for c, t in fl)
    return cum, end, avg_d, avg_0


# symbolic: the time average over [0, 1] of c e^{-d(s - t)} is c e^{dt}(1 - e^{-d})/d for t <= 0 and c(1 - e^{-d(1-t)})/d
s_, t_, dd_ = sp.symbols("s t d", positive=True)
okS = sp.simplify(sp.integrate(sp.exp(-dd_ * (s_ + t_)), (s_, 0, 1)) - sp.exp(-dd_ * t_) * (1 - sp.exp(-dd_)) / dd_) == 0
okS &= sp.simplify(sp.integrate(sp.exp(-dd_ * (s_ - t_)), (s_, t_, 1)) - (1 - sp.exp(-dd_ * (1 - t_))) / dd_) == 0
CONV = ("laFull", "ucEnd", "ucAvg", "laAvg")
GRID2 = {}
for y in YRS:
    for n in (nrr_lo, nrr_hi):
        d = -math.log(n)
        for h2 in (H2_TIMES if y == "2025" else (0.75,)):
            cum, end, avg_d, avg_0 = capital(y, d, h2)
            ch = {"laFull": CRF[n] * cum, "ucEnd": (R_W + d) * end, "ucAvg": (R_W + d) * avg_d, "laAvg": CRF[n] * avg_0}
            for tau in TAUS:
                for cv in CONV:
                    GRID2[(y, n, h2, tau, cv)] = (R_ocf_u[(y, tau)] - ch[cv] / REV[y], R_ocf[y] - ch[cv] / REV[y], ch[cv])
                ret = m_unlev[(y, tau)] * REV[y] / avg_d
                GRID2[(y, n, h2, tau, "ret")] = (ret, ret - d, avg_d / REV[y], end / REV[y])
conv_rng = {(y, cv, tau): (min(v[0] for k, v in GRID2.items() if k[0] == y and k[4] == cv and k[3] == tau),
                           max(v[0] for k, v in GRID2.items() if k[0] == y and k[4] == cv and k[3] == tau))
            for y in YRS for cv in CONV for tau in TAUS}
all25 = [v[0] for k, v in GRID2.items() if k[0] == "2025" and k[4] in CONV]
lev25 = [v[1] for k, v in GRID2.items() if k[0] == "2025" and k[4] in CONV]
ret25 = [v[0] for k, v in GRID2.items() if k[0] == "2025" and k[4] == "ret"]
retn25 = [v[1] for k, v in GRID2.items() if k[0] == "2025" and k[4] == "ret"]
kcap25 = [v[2] for k, v in GRID2.items() if k[0] == "2025" and k[4] == "ret"] + \
         [v[3] for k, v in GRID2.items() if k[0] == "2025" and k[4] == "ret"]
dbl = {tau: (1 - tau) * cfin["2025"] for tau in TAUS}
print("  -> margins before interest (tau 0 / IRES): " + "; ".join(
    f"{c}: {100*m_unlev[(c, 0.0)]:.1f}% / {100*m_unlev[(c, TAU_IRES)]:.1f}%" for c in ("2024", "2025", "Q1 2026")))
for y in YRS:
    print(f"  -> {y} charged as capital before interest, tau = IRES: " + "; ".join(
        f"{cv} {100*conv_rng[(y, cv, TAU_IRES)][0]:.1f} to {100*conv_rng[(y, cv, TAU_IRES)][1]:.1f}" for cv in CONV))
print(f"  -> 2025 over all conventions, lives, timings and tau: {100*min(all25):.1f} to {100*max(all25):.1f} before interest; "
      f"the same charges after interest (double-charged) {100*min(lev25):.1f} to {100*max(lev25):.1f}; double charge "
      f"{100*dbl[TAU_IRES]:.1f} (IRES) to {100*dbl[0.0]:.1f} (tau 0) points; return on time-weighted acquisition capital "
      f"{100*min(ret25):.1f}% to {100*max(ret25):.1f}%, after decay {100*min(retn25):.1f}% to {100*max(retn25):.1f}%; capital / "
      f"revenue {min(kcap25):.2f} to {max(kcap25):.2f}")
# E12: the double charge is exactly the after-tax interest share; the earlier levered middle case is reproduced
ok = all(close(v[1] - v[0], -(1 - k[3]) * cfin[k[0]], 1e-12) for k, v in GRID2.items() if k[4] in CONV)
ok &= all(round(100 * GRID2[("2025", n, h2, 0.0, "laFull")][1], 1) in (84.4, 92.8) for n in (nrr_lo, nrr_hi) for h2 in H2_TIMES)
ok &= round(100 * dbl[TAU_IRES], 1) == 8.3 and round(100 * dbl[0.0], 1) == 10.9
check("E12 rem:acquired-bounds after IB-4: set against operating cash flow after interest paid, a charge at a cost of capital "
      "charges the debt-financed share twice, by exactly (1 - tau) c_fin: 8.3 points of 2025 revenue at Italy's 24% IRES rate "
      "(the Fable finance referee's 'about 8'), 10.9 at tau = 0; the earlier middle case 84.4-92.8 is the double-charged "
      "level annuity", ok)
# E13: every charged score lies between the fully charged and uncharged scores (before interest); ordering of conventions
ok = okS
for k, v in GRID2.items():
    if k[4] in CONV:
        ok &= R_full_u[(k[0], k[3])] < v[0] < R_ocf_u[(k[0], k[3])] and 0 < v[2] < OUT[k[0]]
for y in YRS:
    for n in (nrr_lo, nrr_hi):
        for h2 in (H2_TIMES if y == "2025" else (0.75,)):
            for tau in TAUS:
                gget = lambda cv: GRID2[(y, n, h2, tau, cv)][0]
                ok &= gget("ucEnd") < gget("laFull") and gget("ucEnd") < gget("ucAvg") and gget("laFull") < gget("laAvg")
check("E13 charged as capital on margins before interest: in both years every convention (level annuity or user cost "
      "(r + d), on year-end or time-weighted capital, NRR 91-95%, tau 0 or 24%, second-half 2025 outlays between mid-H2 and "
      "Vimeo's close) lies strictly between the fully charged and uncharged scores; the user cost on year-end capital is the "
      "lowest and the time-weighted charges score higher; 2025 range 87 to 114 (79 to 103 if double-charged); the time "
      "average of decayed capital is exact (symbolic)",
      ok and round(100 * min(all25)) == 87 and round(100 * max(all25)) == 114)
# E14: return on acquisition capital (prop:general(b) in Part I): before interest, on time-weighted capital
ok = all(v[1] > R_W for k, v in GRID2.items() if k[4] == "ret") and all(v[0] > v[1] for k, v in GRID2.items() if k[4] == "ret")
check("E14 return on acquisition capital (IB-4): unlevered operating cash flow over the time-weighted capital deployed since "
      "2023 is 22% to 28% in 2025, 14% to 22% after economic depreciation at d = -ln NRR, above the 8.93% cost of capital in "
      "every cell (NRR, tau, timing)",
      ok and round(100 * min(ret25)) == 22 and round(100 * max(ret25)) == 28 and round(100 * min(retn25)) == 14
      and round(100 * max(retn25)) == 22)
TAG = {"2024": "TwentyFour", "2025": "TwentyFive"}
for y in YRS:
    for cv, nm in (("laFull", "LaFull"), ("ucEnd", "UcEnd"), ("ucAvg", "UcAvg"), ("laAvg", "LaAvg")):
        lo_, hi_ = conv_rng[(y, cv, TAU_IRES)]
        mac(f"acqR{nm}Lo{TAG[y]}", num(100 * lo_, 1))
        mac(f"acqR{nm}Hi{TAG[y]}", num(100 * hi_, 1))
for c, w in (("2024", "TwentyFour"), ("2025", "TwentyFive"), ("Q1 2026", "QOne")):
    mac(f"acqMcfU{w}", pct(m_unlev[(c, TAU_IRES)], 1))
    mac(f"acqROcfU{w}", num(100 * R_ocf_u[(c, TAU_IRES)], 1))
    mac(f"acqRAllInvU{w}", num(100 * R_full_u[(c, TAU_IRES)], 1))
mac("acqROcfUZeroTwentyFive", num(100 * R_ocf_u[("2025", 0.0)], 1))
mac("acqDoubleTwentyFive", num(100 * dbl[TAU_IRES], 1))
mac("acqDoubleZeroTwentyFive", num(100 * dbl[0.0], 1))
mac("acqConvLo", num(100 * min(all25), 0))
mac("acqConvHi", num(100 * max(all25), 0))
mac("acqConvLevLo", num(100 * min(lev25), 0))
mac("acqConvLevHi", num(100 * max(lev25), 0))
ret25t = [v for k, v in GRID2.items() if k[0] == "2025" and k[4] == "ret" and k[3] == TAU_IRES]
mac("acqRetTauLo", pct(min(v[0] for v in ret25t), 1))
mac("acqRetTauHi", pct(max(v[0] for v in ret25t), 1))
mac("acqRetNetTauLo", pct(min(v[1] for v in ret25t), 1))
mac("acqRetNetTauHi", pct(max(v[1] for v in ret25t), 1))
mac("acqRetLo", pct(min(ret25), 0))
mac("acqRetHi", pct(max(ret25), 0))
mac("acqRetNetLo", pct(min(retn25), 0))
mac("acqRetNetHi", pct(max(retn25), 0))
mac("acqKcapLo", num(min(kcap25), 1))
mac("acqKcapHi", num(max(kcap25), 1))
mac("acqDeclLo", pct(1 - nrr_hi, 0))
mac("acqDeclHi", pct(1 - nrr_lo, 0))

# Part I's acquisition flag (sections/data.tex) read from the file, not typed, and applied to the extract
P1_MACROS = {}
_p1m = ROOT / "paper1" / "macros.tex"                    # Paper 1's generated macros, if its text uses them
if _p1m.exists():
    P1_MACROS = dict(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}\{([^}]*)\}", _p1m.read_text(encoding="utf-8")))


def expand_p1(t):
    """replace Paper 1 macros by their values so that its sentences can be parsed whichever form they take"""
    return re.sub(r"\\([A-Za-z]+)(?:\{\})?", lambda mm: P1_MACROS.get(mm.group(1), mm.group(0)), t)


DATA_TEX = expand_p1((ROOT / "sections" / "data.tex").read_text(encoding="utf-8"))
EMP_TEX = expand_p1((ROOT / "sections" / "empirics.tex").read_text(encoding="utf-8"))
fm = re.search(r"at least (\d+)\\% of prior-year revenue, or when reported pro forma revenue exceeds actual revenue by "
               r"at least (\d+)\\%.*?covers (\d+)\\% of core firm-years and (\d+)\\% of those with growth above (\d+)\\%",
               DATA_TEX, re.S)
em = re.search(r"95th percentile falls by (\d+) to (\d+) points", EMP_TEX)
flag_cash, flag_pf, flag_cov, flag_cov_fast, flag_g = [float(x) / 100 for x in fm.groups()] if fm else [None] * 5
p95_lo, p95_hi = (float(em.group(1)), float(em.group(2))) if em else (None, None)
prev = {"2024": REV["2023"], "2025": REV["2024"]}
out_prev = {y: OUT[y] / prev[y] for y in YRS}
need_share = {y: flag_cash * prev[y] / OUT[y] for y in YRS} if fm else {}
dep_prev_q1 = dep_q1 * 1e6 / REV["2025"]
corr_at_flag = 100 * flag_cash / (1 + flag_g) if fm else None
print(f"  -> Part I flag read from data.tex: {fm.groups() if fm else None}; empirics p95 fall {p95_lo}-{p95_hi}; outflow / "
      f"prior-year revenue {out_prev['2024']:.2f}, {out_prev['2025']:.2f}; acquisitions needed for the flag "
      f"{need_share.get('2024', 0):.3f}, {need_share.get('2025', 0):.3f} of the outflow; Q1 2026 capital deployed / 2025 "
      f"revenue {dep_prev_q1:.2f}; full-charge correction at the threshold and g = {flag_g}: {corr_at_flag:.1f} points")
check("E9 Part I's acquisition flag (read from sections/data.tex): net investing outflows were "
      f"{out_prev['2024']:.1f} and {out_prev['2025']:.1f} times prior-year revenue, so 2024 and 2025 carry the flag unless "
      "acquisitions were under about a ninth and an eleventh of them; capital deployed in Q1 2026 alone exceeds the "
      "threshold on 2025 revenue; at the threshold the fully charged correction is at least 25/(1+g) points",
      fm is not None and em is not None and all(out_prev[y] > flag_cash for y in YRS)
      and all(need_share[y] < 0.12 for y in YRS) and dep_prev_q1 > flag_cash)
mac("acqFlagCash", pct(flag_cash, 0))
mac("acqFlagPf", pct(flag_pf, 0))
mac("acqFlagCov", pct(flag_cov, 0))
mac("acqFlagCovFast", pct(flag_cov_fast, 0))
mac("acqFlagG", pct(flag_g, 0))
mac("acqFlagCorr", num(corr_at_flag, 0))
mac("acqPninetyfiveLo", f"{p95_lo:.0f}")
mac("acqPninetyfiveHi", f"{p95_hi:.0f}")
mac("acqOutPrevTwentyFour", num(out_prev["2024"], 1))
mac("acqOutPrevTwentyFive", num(out_prev["2025"], 1))
mac("acqNeedTwentyFour", pct(need_share["2024"], 0))
mac("acqNeedTwentyFive", pct(need_share["2025"], 0))
mac("acqDepPrevQOne", num(dep_prev_q1, 1))

# the 424B4 and the Q2 2026 6-K in Paper 1: net weight of bought growth under the two charging conventions
full_pts = (K_LO - 1, K_HI_D - 1)                                   # points lost per point of acquired growth, X = 1
ann_pts = (min(CRF.values()) * K_LO, max(CRF.values()) * K_HI_D)     # annuity charge per point of acquired growth
ok = full_pts[0] > 0 and ann_pts[1] < 1 and pf_ratio - 1 > flag_pf
ok &= abs((R_q2_rep - R_q2_org) - (q2_g - q2_org)) < 1e-12           # prop:acquired-score(a) with k^acq = 0: the gap is g^acq
print(f"  -> X = 1 at prices {K_LO:.2f}-{K_HI_D:.2f}x revenue: full charge loses {full_pts[0]:.2f}-{full_pts[1]:.2f} points per "
      f"point of acquired growth; the annuity charges {ann_pts[0]:.2f}-{ann_pts[1]:.2f}; pro forma revenue exceeds actual by "
      f"{pf_ratio - 1:.3f} (flag {flag_pf}); Q2 2026 reported minus organic score {100*(R_q2_rep - R_q2_org):.1f} points")
check("E11 prop:acquired-score(a) on the 424B4 prices: at 1.7 to 3.2 times revenue acquired growth lowers the fully "
      "charged Rule-of-40 score and raises the annuity-charged one; the pro forma flag of Part I fires (revenue doubled); "
      "in Q2 2026 the gap between reported and organic scores is the acquired growth credited without its price", ok)
mac("acqFullPtsLo", num(full_pts[0], 1))
mac("acqFullPtsHi", num(full_pts[1], 1))
mac("acqAnnPtsLo", num(ann_pts[0], 2))
mac("acqAnnPtsHi", num(ann_pts[1], 2))
mac("acqPfExcess", pct(pf_ratio - 1, 0))
# E15 (round 2): the user cost per point of acquired growth, and the sign of part (a) at the firm's own decision weight X,
# evaluated at the XBOUNDS placeholders (the data do not identify X; revision plan A1, decision D-1)
uc_pts_hi = max(R_W - math.log(n) for n in (nrr_lo, nrr_hi)) * K_HI_D
raises = {X: sorted(nm for nm, kk in k_deal.items() if X > kk) for X in XBOUNDS}
flip_ok = all((X > kk) == (X - kk > 0) for X in XBOUNDS for kk in k_deal.values())
ok = flip_ok and uc_pts_hi < 1 and all(X - max(CRF.values()) * K_HI_D > 0 and X - uc_pts_hi > 0 for X in XBOUNDS)
ok &= raises[XBOUNDS[0]] == ["AOL", "Eventbrite"] and all(raises[X] == sorted(k_deal) for X in XBOUNDS[1:])
print(f"  -> user cost per point of acquired growth up to {uc_pts_hi:.2f}; at the XBOUNDS placeholders the full charge raises "
      f"R^A_X for: " + "; ".join(f"X = {X:g}: {raises[X]}" for X in XBOUNDS) + f"; sign flips at X = k^acq in "
      f"[{K_LO:.2f}, {K_HI_D:.2f}]")
check("E15 prop:acquired-score(a) at the firm's own weight (XBOUNDS placeholders 2.5, 5, 9): charged in full, acquired growth "
      "raises R^A_X iff X > k^acq, so at X = 2.5 for Eventbrite (1.7) and AOL (2.3) but not Vimeo (3.2), and at 5 and 9 for "
      "all three; the sign flips at X = k^acq, between 1.7 and 3.2; spread as an annuity or a user cost (at most 0.59 points "
      "per point) it raises the score at every placeholder", ok)
mac("acqUcPtsHi", num(uc_pts_hi, 2))

# (f) treadmill: holding growth at g with the base shrinking needs acquired growth above g itself
gs, gos, kas, ms = sp.symbols("g g_o k_a m")
RA_tread = gs + ms - kas * (gs - gos)
check("E10 prop:acquired-score(f): with g^acq = g + d^org (d^org = -g^org) the charged Rule-of-40 score is "
      "g + m - k^acq (g + d^org), falling by k^acq per unit of organic decay (dR/dg^org = k^acq; symbolic) and, at the 2025 "
      "NRR with no new customers and all revenue on subscription, acquisitions must supply more than the measured growth",
      sp.diff(RA_tread, gos) == kas and g25 - math.log(nrr25) > g25)

# ==============================================================================================
header("F. Repricing and retention (Proposition prop:acq-retention)")
# ==============================================================================================
x, xb, nu, gin, tau, a_ = sp.symbols("x xbar nu g_in tau a", positive=True)
# (a) exponential switching-cost ratios: revenue (1 + x) e^{-x/xbar} is maximized at x* = xbar - 1
rev_x = (1 + x) * sp.exp(-x / xb)
crit = sp.solve(sp.diff(rev_x, x), x)
check("F1 prop:acq-retention(a): inverse-hazard condition; with exponential switching-cost ratios the revenue-maximizing "
      "repricing is xbar - 1 (symbolic)", len(crit) == 1 and sp.simplify(crit[0] - (xb - 1)) == 0)
# homogeneous ratios give a step: retention 1 + x below the ratio and 0 above
xbar_h = 0.3
ret_h = [(1 + xx) * (1.0 if xx <= xbar_h else 0.0) for xx in np.linspace(0, 1, 101)]
check("F2 prop:acq-retention(a): with one switching-cost ratio, retention after a repricing is 1 + x or 0, never strictly "
      "between 0 and 1", all(v == 0 or v >= 1 for v in ret_h))
# (c) steady-state tenure shares
sh = sp.integrate(sp.exp(-(nu + gin) * a_), (a_, tau, sp.oo)) / sp.integrate(sp.exp(-(nu + gin) * a_), (a_, 0, sp.oo))
mean_ten = sp.integrate(a_ * (nu + gin) * sp.exp(-(nu + gin) * a_), (a_, 0, sp.oo))
check("F3 prop:acq-retention(c): steady-state share of revenue with tenure >= tau is e^{-(nu + g_in) tau} and mean tenure "
      "1/(nu + g_in) (symbolic)", sp.simplify(sh - sp.exp(-(nu + gin) * tau)) == 0 and sp.simplify(mean_ten - 1 / (nu + gin)) == 0)
h5, h10, hmean = -math.log(ten5) / 5, -math.log(ten10) / 10, 1 / tenmean
nu_rv = {"2025": -math.log(nrr25), "2024": -math.log(nrr24)}
gin_rng = (min(h5, h10, hmean) - nu_rv["2025"], max(h5, h10, hmean) - nu_rv["2025"])
gin_rng24 = (min(h5, h10, hmean) - nu_rv["2024"], max(h5, h10, hmean) - nu_rv["2024"])
print(f"  -> tenure-implied nu + g_in: 5y {h5:.4f}, 10y {h10:.4f}, mean {hmean:.4f}; nu from NRR 2025 {nu_rv['2025']:.4f}, "
      f"2024 {nu_rv['2024']:.4f}; implied g_in {gin_rng} (2025) {gin_rng24} (2024)")
check("F4 prop:acq-retention(c): Sh(10) > Sh(5)^2 rejects a single constant hazard (the revenue hazard falls with tenure), "
      "and the tenure-implied rates exceed the NRR-implied decay", ten10 > ten5 ** 2 and min(h5, h10, hmean) > nu_rv["2025"])
def mix_eqs(p):
    w, a1, a2 = p
    return [w * math.exp(-5 * a1) + (1 - w) * math.exp(-5 * a2) - ten5,
            w * math.exp(-10 * a1) + (1 - w) * math.exp(-10 * a2) - ten10, w / a1 + (1 - w) / a2 - tenmean]
sols = set()
for guess in [(0.3, 0.5, 0.08), (0.5, 0.3, 0.06), (0.2, 1.0, 0.1), (0.4, 0.2, 0.05), (0.1, 2.0, 0.11)]:
    s, info, ier, msg = optimize.fsolve(mix_eqs, guess, full_output=True)
    if ier == 1 and 0 < s[0] < 1 and s[1] > s[2] > 0 and max(abs(e) for e in mix_eqs(s)) < 1e-9:
        sols.add(tuple(round(v, 6) for v in s))
wmix, a_fast, a_slow = sorted(sols)[0]
nrr_mix = wmix * math.exp(-a_fast) + (1 - wmix) * math.exp(-a_slow)
print(f"  -> two-type stationary fit: {wmix:.3f} of revenue at hazard {a_fast:.3f}, {1-wmix:.3f} at {a_slow:.3f}; "
      f"implied one-year revenue retention {nrr_mix:.3f} vs NRR {nrr25:.2f}")
check("F5 prop:acq-retention(c): a unique two-type stationary fit matches the three tenure moments, and its implied one-year "
      "revenue retention is below the reported NRR (so the moments are consistent only with non-stationary inflows)",
      len(sols) == 1 and nrr_mix < min(nrr23, nrr24, nrr25, nrrq1))
Gi = {k: math.log(v) for k, v in {"AOL": nrr_aol, "Evernote": nrr_ev, "Remini": nrr_rem, "StreamYard": nrr_sy}.items()}
check("F6 prop:acq-retention(b): business-level zero-spend growth of subscription revenue, ln NRR (G_i of an all-subscription "
      "business, prop:acquired-score(d)), spans [ln 0.87, ln 0.99]",
      abs(min(Gi.values()) - math.log(0.87)) < 1e-12 and abs(max(Gi.values()) - math.log(0.99)) < 1e-12)
for k, v in {"acqHazFive": num(h5, 3), "acqHazTen": num(h10, 3), "acqHazMean": num(hmean, 3),
             "acqNuTwentyFive": num(nu_rv["2025"], 3), "acqNuTwentyFour": num(nu_rv["2024"], 3),
             "acqGinLo": num(min(gin_rng[0], gin_rng24[0]), 2), "acqGinHi": num(max(gin_rng[1], gin_rng24[1]), 2),
             "acqMixW": pct(wmix, 0), "acqMixFast": num(a_fast, 2), "acqMixSlow": num(a_slow, 2),
             "acqMixNrr": pct(nrr_mix, 0), "acqGiRemini": pct(Gi["Remini"], 1), "acqGiEvernote": pct(Gi["Evernote"], 1),
             "acqGiAol": pct(Gi["AOL"], 1), "acqGiStreamyard": pct(Gi["StreamYard"], 1),
             "acqTenSqFive": pct(ten5 ** 2, 0)}.items():
    mac(k, v)

# ==============================================================================================
header("H. Limits to buying growth (Assumption ass:acq-limits, Proposition prop:acq-limits)")
# ==============================================================================================
# (a) treadmill: uses k (g - g_o) + r_d nd  <=  sources m + nd g  (net debt held at nd per dollar of revenue)
g_, go_, k_, m_, nd_, rd_ = sp.symbols("g g_o k m nd r_d", real=True)
gmax_s = (m_ - rd_ * nd_ + k_ * go_) / (k_ - nd_)
slack = (m_ + nd_ * g_) - (k_ * (g_ - go_) + rd_ * nd_)
ok = sp.simplify(slack.subs(g_, gmax_s)) == 0 and sp.simplify(sp.diff(slack, g_) + (k_ - nd_)) == 0
ok &= sp.simplify(sp.diff(gmax_s, k_) + (m_ - rd_ * nd_ + nd_ * go_) / (k_ - nd_) ** 2) == 0
ok &= sp.simplify(gmax_s.subs(nd_, 0) - (go_ + m_ / k_)) == 0
check("H1 prop:acq-limits(a): with k^acq > nd the owner finances growth g without new equity iff g <= g^max = "
      "(m - r_debt nd + k^acq g^org)/(k^acq - nd); g^org + m/k^acq without debt; dg^max/dk^acq = -(m - r_debt nd + nd g^org)"
      "/(k^acq - nd)^2 (symbolic)", ok)
stand = {n: -math.log(n) for n in (nrr_lo, nrr_hi)}                    # acquired growth needed to stand still
stand_usd = {n: stand[n] * REV["2025"] / 1000 for n in stand}          # $ million of run-rate a year at 2025 revenue
stand_cash_lo = K_LO * stand[nrr_hi]                                   # cash per dollar of revenue at the 424B4 multiples
stand_cash_hi = K_HI_D * stand[nrr_lo]
cff_share = CFF["2025"] / REV["2025"]
M_GRID = (0.2, 0.3)                                                  # scenario values (class d); k^acq from the 424B4
gmax_nodebt = {(mm, kk): math.log(nrr25) + mm / kk for mm in M_GRID for kk in (K_LO, K_HI_D)}
mac("acqMgridLo", f"{M_GRID[0]:.1f}")
mac("acqMgridHi", f"{M_GRID[1]:.1f}")
print(f"  -> standing still with no new customers: acquired growth {stand[nrr_hi]:.4f}-{stand[nrr_lo]:.4f} a year, "
      f"${stand_usd[nrr_hi]:.0f}-{stand_usd[nrr_lo]:.0f}M of run-rate at 2025 revenue; cash {stand_cash_lo:.3f}-"
      f"{stand_cash_hi:.3f} of revenue at {K_LO:.2f}-{K_HI_D:.2f}x; 2025 financing inflow {cff_share:.3f} of revenue; "
      f"g^max without debt at 2025 NRR: " + ", ".join(f"m={a}, k={b:.2f}: {v:.3f}" for (a, b), v in gmax_nodebt.items()))
check("H2 prop:acq-limits(a) worked numbers: standing still needs acquired revenue of -ln NRR a year (5.1% to 9.4% at the "
      "portfolio's NRR range); 2025 growth exceeded every self-financing limit of the scenario grid and came with a "
      "financing inflow above revenue",
      abs(stand[nrr_hi] - 0.0513) < 1e-3 and abs(stand[nrr_lo] - 0.0943) < 1e-3 and cff_share > 1
      and all(v < g25 for v in gmax_nodebt.values()))
for n, tag in ((nrr_lo, "Lo"), (nrr_hi, "Hi")):
    mac(f"acqStand{tag}", pct(stand[n], 1))
    mac(f"acqStandUsd{tag}", f"\\${stand_usd[n]:.0f} million")
mac("acqCffShare", pct(cff_share, 0))
mac("acqStandCashLo", pct(stand_cash_lo, 1))
mac("acqStandCashHi", pct(stand_cash_hi, 1))
mac("acqCffTwentyFive", musd(CFF["2025"]))
mac("acqGmaxLo", pct(min(gmax_nodebt.values()), 0))
mac("acqGmaxHi", pct(max(gmax_nodebt.values()), 0))
# H6 (round 2, Fable F21 carried into prop:acq-limits(a)): required acquired growth = target growth + organic decay, in
# continuously compounded rates; decay -G_i from NRR 91-95% with no new customers and all revenue on subscription (an
# upper bound on the decay if the rest of revenue shrinks no faster), and the company's own Q2 2026 organic growth
g25c = math.log(1 + g25)
org_q2_c = math.log(1 + q2_org)
req = {n: g25c - math.log(n) for n in (nrr_lo, nrr_hi)}
req_cash = (K_LO * min(req.values()), K_HI_D * max(req.values()))
req_org = g25c - org_q2_c
gmax_org = [org_q2_c + mm / kk for mm in M_GRID for kk in (K_LO, K_HI_D)]
ok = all(close(req[n], g25c + stand[n], 1e-12) for n in req) and req_org < g25c < min(req.values())
ok &= all(close(-math.log(n), -math.log(1 + 1.0 * (n - 1)), 1e-12) for n in req)     # G_i at S_sub = S
ok &= all(-math.log(1 + 0.6 * (n - 1)) < -math.log(n) for n in req)                    # less decay if part of revenue is flat
print(f"  -> holding 2025's growth ({g25c:.4f} continuously compounded) needs acquired growth {min(req.values()):.4f} to "
      f"{max(req.values()):.4f} with no new customers (cash {req_cash[0]:.3f} to {req_cash[1]:.3f} of revenue at the 424B4 "
      f"prices), {req_org:.4f} at the company's Q2 2026 organic growth ({org_q2_c:.4f}); g^max without debt there "
      f"{min(gmax_org):.3f} to {max(gmax_org):.3f}")
check("H6 prop:acq-limits(a) after F21: holding growth g needs acquired growth g + d^org; at 2025's growth (66.6% continuously "
      "compounded) that is 71.7% to 76.0% of revenue a year from NRR 91-95% with no new customers and all revenue on "
      "subscription (less if part of revenue does not decay), and 63.7% at the company's reported 3% organic growth", ok
      and round(100 * min(req.values()), 1) == 71.7 and round(100 * max(req.values()), 1) == 76.0 and round(100 * req_org, 1) == 63.7)
mac("acqReqLo", pct(min(req.values()), 1))
mac("acqReqHi", pct(max(req.values()), 1))
mac("acqReqCashLo", pct(req_cash[0], 0))
mac("acqReqCashHi", pct(req_cash[1], 0))
mac("acqOrgLogQTwo", pct(org_q2_c, 1))
mac("acqReqOrg", pct(req_org, 1))
mac("acqGmaxOrgLo", pct(min(gmax_org), 0))
mac("acqGmaxOrgHi", pct(max(gmax_org), 0))

# (b) deal size: at most n_dl deals a year; hurdle headroom H(S_tg) = H0 (S_tg / S0)^(-eps); S_max = n_dl S_tg_max / (g - g_o)
ok = True
for _ in range(300):
    H0, eps, S0 = RNG.uniform(1.0, 3.0), RNG.uniform(0.05, 1.5), RNG.uniform(10, 200)
    ndl, gg, go = RNG.uniform(1, 20), RNG.uniform(0.05, 1.0), RNG.uniform(-0.1, 0.05)
    if gg <= go:
        continue
    zmax = S0 * H0 ** (1 / eps)
    Smax = ndl * zmax / (gg - go)
    for S in np.linspace(0.1 * Smax, 3 * Smax, 41):
        z_need = (gg - go) * S / ndl
        clears = H0 * (z_need / S0) ** (-eps) >= 1 - 1e-12
        ok &= clears == (S <= Smax * (1 + 1e-12))
        gcap = go + ndl * zmax / S
        ok &= (gcap >= gg - 1e-12) == (S <= Smax * (1 + 1e-12))
check("H3 prop:acq-limits(b): with at most n^dl deals a year and hurdle headroom falling with target size at elasticity "
      "eps_sz, growth g is attainable iff S <= S^max = n^dl S^tg_max / (g - g^org), and beyond it at most "
      "g^org + n^dl S^tg_max / S (300 draws)", ok)
# (c) series review: stopping rule with convex challenge probability; FDI delay multiplier
ok = True
for _ in range(300):
    ds, Lch, nv = RNG.uniform(0.01, 0.1), RNG.uniform(1, 10), RNG.uniform(0.05, 1.0)
    a2 = RNG.uniform(0.5, 5)
    pch = lambda s: min(1.0, a2 * s ** 2)                               # convex, nondecreasing
    stop_series = next((n for n in range(1, 400) if nv < pch(n * ds) * Lch), 400)
    stop_alone = next((n for n in range(1, 400) if nv < pch(ds) * Lch), 400)
    ok &= stop_series <= stop_alone
    costs = [pch(n * ds) * Lch for n in range(1, 30)]
    ok &= all(b >= a - 1e-15 for a, b in zip(costs, costs[1:]))
pf, Tf, rr = sp.symbols("p_f T_f r", positive=True)
mult = (1 - pf) + pf * sp.exp(-rr * Tf)
ok &= sp.simplify(mult - (1 - pf * (1 - sp.exp(-rr * Tf)))) == 0
check("H4 prop:acq-limits(c): with a convex challenge probability in cumulative niche share, the expected regulatory cost "
      "of the n-th deal rises with n and series review stops the owner no later than deal-by-deal review (300 draws); an "
      "FDI delay T^fdi with probability p^fdi scales the deal's net value by 1 - p^fdi(1 - e^{-r T^fdi}) (symbolic)", ok)
# (d) consumer-protection cap: switching costs scaled by h_cp; cap ub_cp
hh = sp.symbols("h", positive=True)
rev_h = (1 + x) * sp.exp(-x / (hh * xb))
crit_h = sp.solve(sp.diff(rev_h, x), x)
ok = len(crit_h) == 1 and sp.simplify(crit_h[0] - (hh * xb - 1)) == 0
for _ in range(200):
    xbv, hv, cap = RNG.uniform(1.05, 4), RNG.uniform(0.2, 1), RNG.uniform(0, 3)
    grid = np.linspace(0, 5, 50001)
    revs = (1 + grid) * np.exp(-grid / (hv * xbv))
    feasible = grid <= cap
    best = grid[feasible][np.argmax(revs[feasible])]
    ok &= abs(best - min(max(hv * xbv - 1, 0.0), cap)) < 2e-4
    ok &= all((1 + u) * math.exp(-u / (hv * xbv)) <= (1 + u) * math.exp(-u / xbv) + 1e-15 for u in (0.1, 0.5, 1.0))
check("H5 prop:acq-limits(d): scaling switching costs by h^cp moves the exponential optimum to h^cp xbar - 1 (symbolic); "
      "with a cap the optimum is min{(h^cp xbar - 1)^+, cap}, and retained revenue at any repricing falls (200 draws)", ok)

# ==============================================================================================
header("G. Secondary sources (verified 29 Oct 2026) against the extract, and lint of the .tex files")
# ==============================================================================================
SEC = dict(ipo_price=29.00, ipo_shares_m=57.97, ipo_total_b=1.68, ipo_company_shares_m=34.4, ipo_selling_m=23.6,
           close_px=40.50, day1=0.397, cap_close_b=25.7, cap_open_b=18.4, private_round_b=11.0,
           wetransfer_planned=0.75, wetransfer_staff=350, brightcove_cut=198, brightcove_staff=600, komoot_max=0.85,
           komoot_staff=150, mosaic=330, aol_warn=108, harvest_old=130.0, harvest_new=2110.0, vimeo_px=7.85,
           vimeo_b=1.38, vimeo_prem=0.91, brightcove_px=4.45, eventbrite_px=4.50, eventbrite_m=500.0, aol_b=1.5,
           aol_debt_b=2.8)
check("G1 extract's IPO figures match the verified sources ($29.00, about $1.68B; first day about 40% vs 39.7%)",
      ipo_px_x == SEC["ipo_price"] and ipo_raise_x == SEC["ipo_total_b"]
      and abs(SEC["ipo_shares_m"] * SEC["ipo_price"] / 1000 - SEC["ipo_total_b"]) < 0.005
      and abs(SEC["close_px"] / SEC["ipo_price"] - 1 - SEC["day1"]) < 0.001)
company_proceeds = SEC["ipo_company_shares_m"] * SEC["ipo_price"]
harvest_rise = SEC["harvest_new"] / SEC["harvest_old"] - 1
check("G2 derived secondary figures: primary proceeds about $1.0B (34.4M shares at $29); the reported Harvest example is "
      "a 1,523% rise ('roughly 1,500%'); Brightcove's cut is 33% of 'over 600'",
      abs(company_proceeds - 997.6) < 0.1 and abs(harvest_rise - 15.23) < 0.01
      and abs(SEC["brightcove_cut"] / SEC["brightcove_staff"] - 0.33) < 0.001)
# lint: no F-1 figure typed into the .tex files (every one must come through a macro)
raw = []
for f in TEXFILES:
    if f.exists():
        t = f.read_text(encoding="utf-8")
        t = re.sub(r"(?m)%.*$", "", t)
        for pat in [r"1{,}306", r"1,306", r"94\.7", r"21\.3\\%", r"10\.9\\%", r"15\.5\\%", r"22\.2\\%", r"142{,}601",
                    r"\b621\b", r"\b65\\%", r"\b25\\% unlevered", r"85\\%", r"\b4\.00\b", r"2\.24", r"2\.19",
                    r"\b87\\%", r"\b99\\%", r"\b91\\%", r"\b95\\%", r"\b48\\%", r"\b28\\%", r"8\.0 years", r"800{,}000",
                    r"\b286\b", r"\$549", r"\$2\.01", r"\$194", r"108{,}970", r"\b21\.6\b", r"\b145\.0\b",
                    r"\b44\.3\b", r"161\.2", r"\b7\.2\\%", r"\b125\.2\b", r"\b116\.9\b", r"\b115\.9\b"]:
            if re.search(pat, t):
                raw.append((f.name, pat))
check("G3 lint: no F-1 figure is typed into the four .tex files of either paper (all come from macros)",
      not raw and all(f.exists() for f in TEXFILES), str(raw))
for k, v in {"acqIpoPx": f"\\${SEC['ipo_price']:.2f}", "acqIpoShares": f"{SEC['ipo_shares_m']:.2f} million",
             "acqIpoTotal": f"\\${SEC['ipo_total_b']:.2f} billion", "acqIpoCompany": f"\\${num(company_proceeds / 1000, 1)} billion",
             "acqIpoCompanyShares": f"{SEC['ipo_company_shares_m']:.1f} million", "acqDayOne": pct(SEC["day1"], 1),
             "acqCapClose": f"\\${SEC['cap_close_b']:.1f} billion", "acqCapOpen": f"\\${SEC['cap_open_b']:.1f} billion",
             "acqHarvestRise": pct(harvest_rise, 0).replace("1523", "1{,}523"),
             "acqHarvestOld": f"\\${SEC['harvest_old']:.0f}", "acqHarvestNew": f"\\${num(SEC['harvest_new'], 0)}",
             "acqHarvestMult": num(harvest_rise, 1),
             "acqWetPlanned": pct(SEC["wetransfer_planned"], 0), "acqWetStaff": f"{SEC['wetransfer_staff']}",
             "acqBcCut": f"{SEC['brightcove_cut']}", "acqBcStaff": f"{SEC['brightcove_staff']}",
             "acqKomootMax": pct(SEC["komoot_max"], 0), "acqKomootStaff": f"{SEC['komoot_staff']}",
             "acqMosaic": f"{SEC['mosaic']}", "acqAolWarn": f"{SEC['aol_warn']}",
             "acqVimeoPx": f"\\${SEC['vimeo_px']:.2f}", "acqVimeoB": f"\\${SEC['vimeo_b']:.2f} billion",
             "acqVimeoPrem": pct(SEC["vimeo_prem"], 0), "acqBcPx": f"\\${SEC['brightcove_px']:.2f}",
             "acqBcPrice": f"\\${BC_PRICE:.0f} million", "acqEbPx": f"\\${SEC['eventbrite_px']:.2f}",
             "acqEbM": f"\\${SEC['eventbrite_m']:.0f} million", "acqAolB": f"\\${SEC['aol_b']:.1f} billion",
             "acqAolDebt": f"\\${SEC['aol_debt_b']:.1f} billion", "acqPrivRound": f"\\${SEC['private_round_b']:.0f} billion"}.items():
    mac(k, v)

# ==============================================================================================
header("Write macros")
# ==============================================================================================
# ==============================================================================================
header("F. Round 2 (D3; IB2-N6, F2-5, F2-other): interest paid, run-rate interest after the post-IPO debt, marginal coupon")
# ==============================================================================================
# Inputs read on sec.gov in the author's browser on 2 Nov 2026 (data/v3_inputs/README_retrieval.md section 4):
# data/v3_inputs/bending_spoons_cash_interest.json (424B4 F-34/F-35 and F-6/F-7; Ex. 99.2 of the 13 Aug 6-K), and the
# 6-K texts through 29 Oct 2026 (data/v3_inputs/raw/bending_spoons_6k_2026-11-02.json). Every 6-K figure below is
# matched in those texts by a regular expression, so a missing or changed sentence stops the check.
BSCI = json.loads((ROOT / "data" / "v3_inputs" / "bending_spoons_cash_interest.json").read_text(encoding="utf-8"))
SIXK = json.loads((ROOT / "data" / "v3_inputs" / "raw" / "bending_spoons_6k_2026-11-02.json").read_text(encoding="utf-8"))
SIXK_TXT = {v["url"]: re.sub(r"\s+", " ", v.get("text", "")) for v in SIXK.values()}


def sixk(pattern, acc):
    """first match of pattern in the Ex. 99.1 text of the 6-K with accession folder acc; returns the groups"""
    txt = [t for u, t in SIXK_TXT.items() if f"/{acc}/" in u and "ex99" in u][0]
    m = re.search(pattern, txt)
    if not m:
        raise SystemExit(f"6-K {acc}: pattern not found: {pattern}")
    return m.groups()


nt_u_amt, nt_u_c, nt_e_amt, nt_e_c = sixk(r"\$([\d.]+) billion aggregate principal amount of ([\d.]+)% U\.S\. dollar-denominated senior "
                                         r"secured notes and €(\d+) million aggregate principal amount of ([\d.]+)% euro", "000200471126000021")
nt_tot = float(sixk(r"aggregate principal amount equivalent to approximately \$([\d.]+) billion", "000200471126000021")[0])
nt_use = sixk(r"(net proceeds from the Offerings are intended to fund future acquisitions)", "000200471126000021")[0]
tlb_u, tlb_e = sixk(r"priced a \$([\d.]+) billion add-on to its existing US dollar-denominated senior secured term loan B, due 2031, "
                    r"and a €(\d+) million add-on", "000200471126000016")
tlb_use = sixk(r"(intends to use the proceeds to finance the agreed-upon Miro acquisition, repay the currently drawn portion of its "
               r"euro revolving credit facility)", "000200471126000016")[0]
sace = float(sixk(r"entered into a new €(\d+) million medium-long-term financing", "000110465926087587")[0])
arr_air = float(sixk(r"annual recurring revenue growing over 20% YoY to approximately \$(\d+) million", "000200471126000009")[0])
arr_miro = float(sixk(r"Miro has grown to around \$(\d+) million in annual recurring revenue", "000200471126000015")[0])
nt_u_amt, nt_u_c, nt_e_amt, nt_e_c = float(nt_u_amt), float(nt_u_c), float(nt_e_amt), float(nt_e_c)
tlb_u, tlb_e = float(tlb_u), float(tlb_e)
usd_per_eur = (nt_tot - nt_u_amt) * 1000 / nt_e_amt               # implied by the 6-K's "approximately $1.8 billion"
assert abs(nt_u_c - 100 * (math.exp(R_DEBT_NOTES) - 1)) < 1e-9 and nt_u_amt == 1.25 and nt_e_amt == 500
IPd = BSCI["annual_cash_flow_supplemental"]["interests_paid"]
IP = {**{y: float(IPd[y]) for y in ("2023", "2024", "2025")}, "Q1 2026": float(BSCI["q1_cash_flow_supplemental"]["interests_paid"]["Q1 2026"])}
H1J = BSCI["h1_2026"]
assert H1J["interests_paid"]["H1 2026"] == H1["H1 2026"]["Interests paid"]           # same figure as the extract (A15)
assert abs(H1J["interest_expense_income_statement"]["H1 2026"] - h1_int_exp["H1 2026"]) < 1.5
cfin_paid = {c: IP[c] / REV[c] for c in IP}
paid_to_exp = {c: IP[c] / INT[c] for c in IP}
# (a) the before-interest charged scores with interest PAID added back (the cash basis), instead of interest expense
m_unlev_p = {(c, tau): mocf[c] + (1 - tau) * cfin_paid[c] for c in ("2024", "2025", "Q1 2026") for tau in TAUS}
R_ocf_up = {(c, tau): {"2024": g24, "2025": g25, "Q1 2026": gq1}[c] + m_unlev_p[(c, tau)] for c, tau in m_unlev_p}


def grid_scores(rw, y="2025"):
    crf_ = {n: crf(rw, LIFE[n]) for n in LIFE}
    out_ = []
    for n in (nrr_lo, nrr_hi):
        d = -math.log(n)
        for h2 in (H2_TIMES if y == "2025" else (0.75,)):
            cum, end, avg_d, avg_0 = capital(y, d, h2)
            ch = {"laFull": crf_[n] * cum, "ucEnd": (rw + d) * end, "ucAvg": (rw + d) * avg_d, "laAvg": crf_[n] * avg_0}
            for tau in TAUS:
                for cv in CONV:
                    out_.append((R_ocf_up[(y, tau)] - ch[cv] / REV[y], R_ocf_u[(y, tau)] - ch[cv] / REV[y]))
    return out_


g_wacc, g_coupon = grid_scores(R_W), grid_scores(R_DEBT_NOTES)
paid25 = [a for a, _ in g_wacc]
exp25 = [b for _, b in g_wacc]
coupon25 = [a for a, _ in g_coupon]
# (b) run-rate interest after the post-IPO debt: H1 2026 interest expense annualized (Ex. 99.2) plus the coupons of the
# notes priced on 28 Oct 2026, the only new debt whose coupon a 6-K states; the term loan B add-ons (whose proceeds also
# repay a drawn revolver, amount not stated) and the SACE-backed loan carry no stated rate, so they are left out of the
# central figure and charged at the notes' USD coupon in the upper case
int_h1_ann = 2 * H1J["interest_expense_income_statement"]["H1 2026"] / 1000           # $M a year
notes_coupon = (nt_u_c / 100 * nt_u_amt * 1000 + nt_e_c / 100 * nt_e_amt * usd_per_eur)  # $M a year
unpriced = tlb_u * 1000 + (tlb_e + sace) * usd_per_eur                                  # $M of principal without a stated rate
run_rate = int_h1_ann + notes_coupon
run_rate_hi = run_rate + nt_u_c / 100 * unpriced
rev_q2_ann = 4 * Q2["Revenue"] / 1000
rev_pf = rev_q2_ann + arr_air + arr_miro
print(f"  -> interest paid / revenue: " + ", ".join(f"{c} {100*cfin_paid[c]:.1f}% (expense {100*cfin[c]:.1f}%; paid/expense "
      f"{paid_to_exp[c]:.2f})" for c in IP))
print(f"  -> 2025 charged scores before interest, all conventions: interest paid {100*min(paid25):.1f} to {100*max(paid25):.1f} "
      f"(interest expense {100*min(exp25):.1f} to {100*max(exp25):.1f}); charged at the notes' coupon {100*(math.exp(R_DEBT_NOTES)-1):.3f}%: "
      f"{100*min(coupon25):.1f} to {100*max(coupon25):.1f}")
print(f"  -> run-rate interest: H1 2026 annualized ${int_h1_ann:.0f}M + notes ${notes_coupon:.1f}M = ${run_rate:.0f}M; with "
      f"${unpriced:.0f}M of unpriced new principal at {nt_u_c}%: ${run_rate_hi:.0f}M; share of Q2-annualized revenue "
      f"${rev_q2_ann:.0f}M: {100*run_rate/rev_q2_ann:.1f}% to {100*run_rate_hi/rev_q2_ann:.1f}%; with the acquired ARR "
      f"(${arr_air:.0f}M + ${arr_miro:.0f}M): {100*run_rate/rev_pf:.1f}% to {100*run_rate_hi/rev_pf:.1f}% (EUR at {usd_per_eur:.3f})")
check("F1 (D3) interest paid replaces interest expense on the cash basis: 424B4 interests paid 16.6, 19.2 and 130.9 $M "
      "(2023-25) and 89.0 (Q1 2026) are 59-97% of interest expense; the before-interest charged 2025 scores move by "
      "(1 - tau)(paid - expense)/revenue",
      all(abs(a - b - (1 - k[3]) * (cfin_paid["2025"] - cfin["2025"])) < 1e-12 for (a, b), k in
          zip(g_wacc, [(None, None, None, tau) for n in (nrr_lo, nrr_hi) for h2 in H2_TIMES for tau in TAUS for cv in CONV]))
      and IP["2025"] == 130881 and IP["2023"] == 16581 and IP["2024"] == 19168)
check("F2 (D3) the run-rate interest uses only coupons and amounts stated in the 6-Ks (notes $1.25B at 9.625% and EUR 500M "
      "at 8.625%, about $1.8B in all; term loan B add-ons $1.25B and EUR 395M and the EUR 500M SACE loan without a stated "
      "rate); charging acquisitions at the notes' coupon instead of the 9.34% WACC lowers every charged score",
      run_rate_hi > run_rate > int_h1_ann and max(coupon25) < max(paid25) and min(coupon25) < min(paid25)
      and 1.05 < usd_per_eur < 1.20 and nt_use and tlb_use)
for k, v in {"acqIntPaidShTwentyThree": pct(cfin_paid["2023"]), "acqIntPaidShTwentyFour": pct(cfin_paid["2024"]),
             "acqIntPaidShTwentyFive": pct(cfin_paid["2025"]), "acqIntPaidShQOne": pct(cfin_paid["Q1 2026"]),
             "acqIntPaidTwentyFive": musd(IP["2025"]),
             "acqChPaidLo": num(100 * min(paid25), 1), "acqChPaidHi": num(100 * max(paid25), 1),
             "acqChCouponLo": num(100 * min(coupon25), 1), "acqChCouponHi": num(100 * max(coupon25), 1),
             "acqRunRateInt": f"{run_rate:,.0f}".replace(",", "{,}"), "acqRunRateIntHi": f"{run_rate_hi:,.0f}".replace(",", "{,}"),
             "acqRunRateIntHOne": f"{int_h1_ann:.0f}", "acqNotesCoupon": f"{notes_coupon:.0f}",
             "acqRunRateShQ": pct(run_rate / rev_q2_ann), "acqRunRateShQHi": pct(run_rate_hi / rev_q2_ann),
             "acqRunRateShPf": pct(run_rate / rev_pf), "acqRunRateShPfHi": pct(run_rate_hi / rev_pf),
             "acqUnpricedDebt": f"{unpriced:,.0f}".replace(",", "{,}"), "acqCouponMarg": f"{nt_u_c:g}",
             "acqCouponEur": f"{nt_e_c:g}"}.items():
    mac(k, v)

# ----------------------------------------------------------------------------------------------
# I (round 3, 2 Nov 2026; GLM-F2, GLM-M6, GLM-5, GLM-6, GPT-M3, GPT-17, DS-67 to DS-69): the raw filings. The final
# prospectus and the F-1, downloaded from sec.gov (data/v3_inputs/raw/*.htm.gz, README_retrieval.md section 5), are
# decompressed, their SHA-256 checked, split into printed pages and searched for every figure that
# data/v3_inputs/bending_spoons_annual_2024_2025.json lists, on the page it gives; the annual organic rows of
# Table tab:acquired-score, the cash score on the panel's basis and the annual investing split follow from them.
# ----------------------------------------------------------------------------------------------
import gzip
import hashlib
from html.parser import HTMLParser

BSA = json.loads((ROOT / "data" / "v3_inputs" / "bending_spoons_annual_2024_2025.json").read_text(encoding="utf-8"))
README5 = (ROOT / "data" / "v3_inputs" / "README_retrieval.md").read_text(encoding="utf-8")
README5 = README5[README5.index("## 5."):]
README_SHA = dict(re.findall(r"\| `raw/([^`]+)` \|[^\n]*\| ([0-9a-f]{64}) \|", README5))


class _PageText(HTMLParser):
    """text of an EDGAR HTML document split at its page-break rules; each page labelled by its last line"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pages, self.skip = [[]], 0

    def handle_starttag(self, tag, attrs):
        st = (dict(attrs).get("style") or "").replace(" ", "").lower()
        if "page-break-after:always" in st or "page-break-before:always" in st:
            self.pages.append([])
        self.skip += tag in ("script", "style")
        if tag in ("p", "div", "tr", "br", "table", "li", "td", "th"):
            self.pages[-1].append("\n" if tag not in ("td", "th") else " ")

    def handle_endtag(self, tag):
        self.skip -= tag in ("script", "style")

    def handle_data(self, d):
        if not self.skip:
            self.pages[-1].append(d)


def raw_document(rel):
    """(sha256 of the decompressed bytes, [(printed page, normalized text)]) of a gzip'd raw filing"""
    raw = gzip.decompress((ROOT / rel).read_bytes())
    p = _PageText()
    p.feed(raw.decode("utf-8", errors="replace"))
    out = []
    for pg in p.pages:
        t = "".join(pg).replace("​", " ").replace("\xa0", " ")
        lines = [ln.strip() for ln in t.split("\n") if ln.strip() and ln.strip() != "Table of Contents"]
        out.append((lines[-1] if lines else "", re.sub(r"\s+", " ", t)))
    return hashlib.sha256(raw).hexdigest(), out


DOCS = {k: raw_document(v["file"]) for k, v in BSA["documents"].items()}
ex99 = {f: hashlib.sha256(gzip.decompress((ROOT / "data" / "v3_inputs" / "raw" / f).read_bytes())).hexdigest()
        for f in ("bsp_ex99-1_2026-08-13.htm.gz", "bsp_ex99-2_2026-08-13.htm.gz")}
ok = all(DOCS[k][0] == v["sha256_uncompressed"] == README_SHA[Path(v["file"]).name] for k, v in BSA["documents"].items())
ok &= all(ex99[f] == README_SHA[f] for f in ex99) and len(README_SHA) == 4
check("I1 raw filings: the final prospectus and the F-1 (and the 6-K exhibits 99.1 and 99.2) decompress to the SHA-256 "
      "recorded in data/v3_inputs/README_retrieval.md section 5 and in the figures file", ok,
      "; ".join(f"{k} {DOCS[k][0][:12]}" for k in DOCS))


def find_figure(key, doc):
    """values of figure `key` read from document `doc` on the pages the JSON gives, in the JSON's order"""
    f = BSA["figures"][key]
    pg = [(lab, t) for lab, t in DOCS[doc][1] if re.search(f.get("page_anchor", ""), t)]
    vals = []
    for rx in f["regex"]:
        hits = [(lab, m) for lab, t in pg for m in [re.search(rx, t)] if m]
        if not hits:
            return None, None
        vals += [(0.0 if g == "—" else float(g.replace(",", ""))) for g in hits[0][1].groups()]
    pages = sorted({lab for rx in f["regex"] for lab, t in pg if re.search(rx, t)})
    return [v * f["scale"] for v in vals], pages


ok, bad = True, []
FIG = {}
for key, f in BSA["figures"].items():
    for doc in BSA["documents"]:
        vals, pages = find_figure(key, doc)
        want = [float(v) for v in f["values"].values()]
        good = vals is not None and all(abs(a - b) < 1e-9 for a, b in zip(vals, want)) and len(vals) == len(want) \
            and pages == sorted(f["pages"][doc])
        ok &= good
        if not good:
            bad.append(f"{key}/{doc}: {vals} on {pages}")
    FIG[key] = {k: float(v) for k, v in f["values"].items()}
_, _org_pages = find_figure("organic_revenue_growth", "424b4")
org_def = all(re.search(BSA["figures"]["organic_revenue_growth"]["definition_regex"], t) for lab, t in DOCS["424b4"][1]
              if lab in _org_pages)
check("I2 every figure of the figures file is found in both the final prospectus and the F-1, with the same values, on the "
      "printed pages it gives: organic growth 7% (2024) and 13% (2025) with the company's definition (estimated "
      "pre-acquisition revenue) on the same page, subscriptions 95/92/93%, equity compensation, the investing lines, interest "
      "paid, the 2025 pro forma revenue row and the three purchase prices", ok and org_def, "; ".join(bad))
org = {y: FIG["organic_revenue_growth"][y] for y in YRS}
SBC = FIG["equity_compensation_expense"]
PPE = FIG["purchase_of_property_plant_and_equipment"]
ACQ = FIG["acquisitions_of_businesses_net_of_cash_acquired"]
INTG = FIG["purchase_of_intangible_assets"]
OTHI = FIG["proceeds_from_other_investments"]
NINV = FIG["net_cash_from_investing_activities"]
SUBS = FIG["subscription_share_of_revenue"]
PFR = FIG["pro_forma_revenue_2025"]
PXS = FIG["acquisition_prices_usd_million"]
_i3 = dict(
    cash=all(abs(FIG["net_cash_from_operating_activities"][y] - OCF[y]) < 0.5 and abs(NINV[y] - CFI[y]) < 0.5
             for y in ("2023",) + tuple(YRS)),
    interest_paid=all(abs(FIG["interests_paid"][y] - IP[y]) < 0.5 for y in ("2023", "2024", "2025")),
    investing_adds_up=all(abs(ACQ[y] + INTG[y] + PPE[y] + OTHI[y] - NINV[y]) < 1.5 for y in ("2023",) + tuple(YRS)),
    pro_forma=sorted([PFR["column_2"], PFR["column_3"], PFR["vimeo_2025-01-01_to_2025-11-23"]]) == sorted([pf_eb, pf_aol, pf_vim])
    and PFR["historical"] == pf_bs and PFR["pro_forma_combined"] == pf_tot and PFR["vimeo_2025-01-01_to_2025-11-23"] == pf_vim,
    prices=(PXS["AOL"], PXS["Eventbrite"], PXS["Vimeo"]) == (px_aol, px_eb, px_vim))
ok = all(_i3.values())
check("I3 the raw filings reproduce the extract and the cash-interest file: operating and investing cash flows 2023-25, "
      "interest paid, the investing lines adding up to the net investing outflow (rounding of $1 thousand in 2023 and 2025), and (DS-69) the 2025 pro forma revenue "
      "components, total ($2,608.5 million) and the three purchase prices behind acqPfRev, acqPfRatio and acqKEb to acqKVim", ok,
      ", ".join(k for k, v in _i3.items() if not v))
# Table tab:acquired-score, annual organic rows on the company's organic growth (method of the Q2 column, A12/A14)
R_org = {y: org[y] + mop[y] for y in YRS}
R_org_int = {y: R_org[y] - cfin[y] for y in YRS}
R_org_xr = {y: R_org[y] + reorg_sh[y] for y in YRS}
R_org_int_xr = {y: R_org_int[y] + reorg_sh[y] for y in YRS}
sbc_sh = {y: SBC[y] / REV[y] for y in ("2023",) + tuple(YRS)}
ppe_rev = {y: -PPE[y] / REV[y] for y in YRS}
R_ocf_sbc = {y: g_y[y] + (OCF[y] - SBC[y]) / REV[y] for y in YRS}                      # after interest paid and SBC
R_fcf_sbc = {y: g_y[y] + (OCF[y] - SBC[y] + PPE[y]) / REV[y] for y in YRS}            # and capex: the panel's FCF after SBC
acq_sh_y = {y: ACQ[y] / NINV[y] for y in YRS}
intg_sh_y = {y: INTG[y] / NINV[y] for y in YRS}
ppe_sh_y = {y: PPE[y] / NINV[y] for y in YRS}
print("  -> annual organic scores (company measure): " + "; ".join(
    f"{y}: g_org {org[y]:.2f}, before interest {100*R_org[y]:.2f}, after {100*R_org_int[y]:.2f}, before reorganization "
    f"{100*R_org_xr[y]:.2f}, after interest and before reorganization {100*R_org_int_xr[y]:.2f}" for y in YRS))
print("  -> SBC / revenue " + ", ".join(f"{y} {v:.4f}" for y, v in sbc_sh.items()) + "; cash score after interest paid and SBC "
      + ", ".join(f"{y} {100*R_ocf_sbc[y]:.2f}" for y in YRS) + "; and capex (panel basis) "
      + ", ".join(f"{y} {100*R_fcf_sbc[y]:.2f}" for y in YRS) + "; acquisitions / intangibles / PP&E share of the net investing "
      "outflow " + ", ".join(f"{y} {acq_sh_y[y]:.4f} / {intg_sh_y[y]:.4f} / {ppe_sh_y[y]:.5f}" for y in YRS))
check("I4 (GLM-F2) Table 3 annual organic rows, the company's organic growth plus the GAAP operating margin: 26.0 / 34.3 before "
      "interest, 21.1 / 23.4 after interest expense, 33.7 / 40.3 with reorganization added back and 28.8 / 29.4 after interest "
      "with it added back (2024 / 2025); every 2025 organic score lies inside the Q2 2026 range (21.6 to 44.3)",
      [round(100 * R_org[y], 1) for y in YRS] == [26.0, 34.3] and [round(100 * R_org_int[y], 1) for y in YRS] == [21.1, 23.4]
      and [round(100 * R_org_xr[y], 1) for y in YRS] == [33.7, 40.3]
      and [round(100 * R_org_int_xr[y], 1) for y in YRS] == [28.8, 29.4]
      and all(R_q2_org_int <= v["2025"] <= R_q2_org_xr for v in (R_org, R_org_int, R_org_xr, R_org_int_xr)))
check("I5 (GLM-F2, GPT-17) the 2025 cash score on the panel's basis (free cash flow after SBC, after interest paid): operating "
      "cash flow less equity compensation (4.25% of revenue) and purchases of property and equipment gives 112.6 (100.0 in "
      "2024), 4.29 points below Table 3's 116.9; capex is under 0.1% of revenue in both years",
      round(100 * R_fcf_sbc["2025"], 1) == 112.6 and round(100 * R_fcf_sbc["2024"], 1) == 100.0
      and round(100 * (R_ocf["2025"] - R_fcf_sbc["2025"]), 2) == 4.29 and round(100 * sbc_sh["2025"], 2) == 4.25
      and max(ppe_rev.values()) < 0.001)
check("I6 (GLM-F2, GLM-6) the annual investing split: acquisitions of businesses were 81.7% of the 2024 net investing outflow "
      "and purchases of intangible assets (including the Mosaic asset deal) 18.3%; in 2025 acquisitions were 99.97%",
      round(100 * acq_sh_y["2024"], 1) == 81.7 and round(100 * intg_sh_y["2024"], 1) == 18.3
      and round(100 * acq_sh_y["2025"], 2) == 99.97 and abs(acq_sh_y["2024"] + intg_sh_y["2024"] + ppe_sh_y["2024"] - 1) < 1e-12)
# GPT-M3: the instantaneous charge per point of run-rate revenue (k^acq) against the annual score, which divides growth by
# last year's revenue: with full-year recognition the average charge per point of simple annual growth is k^acq/(1 + g_t)
ann_f = 1 / (1 + g25)
full_ann = {nm: 1 - kk * ann_f for nm, kk in k_deal.items()}                  # net effect per point at X = 1, 2025 growth
ann_ann = (ann_pts[0] * ann_f, ann_pts[1] * ann_f)
uc_ann_hi = uc_pts_hi * ann_f
print(f"  -> GPT-M3 annual units at 2025 growth ({g25:.4f}): average charge factor 1/(1+g) {ann_f:.3f}; net effect per point "
      "of simple annual growth at X = 1: " + ", ".join(f"{nm} {v:+.3f}" for nm, v in full_ann.items())
      + f"; annuity {ann_ann[0]:.3f}-{ann_ann[1]:.3f}, user cost up to {uc_ann_hi:.3f}")
check("I7 (GPT-M3) per point of simple annual acquired growth with full-year recognition at 2025 growth, the full charge is "
      "k^acq/(1+g): the net effect at X = 1 is +0.11 (Eventbrite), -0.18 (AOL) and -0.66 (Vimeo, at its unrounded 3.23; the "
      "review's -0.64 uses 3.2) instead of -0.7 to -2.2 per point of run-rate revenue; the annual identity holds on the "
      "review's example (C/S 1.5 = k g_simple/(1+g))",
      [round(full_ann[nm], 2) for nm in ("Eventbrite", "AOL", "Vimeo")] == [0.11, -0.18, -0.66]
      and abs((300 / 100) * (100 / 100) / (1 + 1.0) - 300 / 200) < 1e-12 and ann_f < 0.52)
# GLM-M6: the coupon variant on the interest-expense basis (the basis of the 87-114 range) beside the interest-paid one
coupon25_exp = [b for _, b in g_coupon]
check("I8 (GLM-M6) charged at the notes' coupon, the 2025 charged scores are 86.0 to 112.8 with interest paid added back and "
      "86.7 to 113.7 with interest expense added back, the basis of the 87-114 range",
      (round(100 * min(coupon25), 1), round(100 * max(coupon25), 1)) == (86.0, 112.8)
      and (round(100 * min(coupon25_exp), 1), round(100 * max(coupon25_exp), 1)) == (86.7, 113.7)
      and min(coupon25_exp) > min(coupon25))
R3_MACROS = {
    "acqOrgGTwentyFour": pct(org["2024"], 0), "acqOrgGTwentyFive": pct(org["2025"], 0),
    "acqROrgTwentyFour": num(100 * R_org["2024"], 1), "acqROrgTwentyFive": num(100 * R_org["2025"], 1),
    "acqROrgIntTwentyFour": num(100 * R_org_int["2024"], 1), "acqROrgIntTwentyFive": num(100 * R_org_int["2025"], 1),
    "acqROrgNoReorgTwentyFour": num(100 * R_org_xr["2024"], 1), "acqROrgNoReorgTwentyFive": num(100 * R_org_xr["2025"], 1),
    "acqROrgIntNoReorgTwentyFour": num(100 * R_org_int_xr["2024"], 1),
    "acqROrgIntNoReorgTwentyFive": num(100 * R_org_int_xr["2025"], 1),
    "acqROrgIntTwentyFiveR": num(100 * R_org_int["2025"], 0), "acqROrgNoReorgTwentyFiveR": num(100 * R_org_xr["2025"], 0),
    "acqSubsTwentyThree": pct(SUBS["2023"], 0), "acqSubsTwentyFour": pct(SUBS["2024"], 0), "acqSubsTwentyFive": pct(SUBS["2025"], 0),
    "acqSbcTwentyThree": pct(sbc_sh["2023"]), "acqSbcTwentyFour": pct(sbc_sh["2024"]), "acqSbcTwentyFive": pct(sbc_sh["2025"]),
    "acqSbcTwentyFiveTwo": pct(sbc_sh["2025"], 2), "acqSbcUsdTwentyFive": musd(SBC["2025"]),
    "acqROcfSbcTwentyFour": num(100 * R_fcf_sbc["2024"], 1), "acqROcfSbcTwentyFive": num(100 * R_fcf_sbc["2025"], 1),
    "acqROcfSbcOnlyTwentyFive": num(100 * R_ocf_sbc["2025"], 1),
    "acqAcqShareTwentyFour": pct(acq_sh_y["2024"]), "acqAcqShareTwentyFive": pct(acq_sh_y["2025"]),
    "acqAcqShareTwentyFiveTwo": pct(acq_sh_y["2025"], 2),
    "acqIntangShareTwentyFour": pct(intg_sh_y["2024"]), "acqIntangTwentyFour": musd(-INTG["2024"]),
    "acqCapexRevTwentyFour": pct(ppe_rev["2024"], 2), "acqCapexRevTwentyFive": pct(ppe_rev["2025"], 2),
    **{f"acqFullAnn{nm_}": ("\\ensuremath{+}" if full_ann[full_] > 0 else "") + minus(f"{full_ann[full_]:.2f}")
       for nm_, full_ in (("Eb", "Eventbrite"), ("Aol", "AOL"), ("Vim", "Vimeo"))},
    "acqAnnFactor": num(ann_f, 2), "acqAnnPtsAnnLo": num(ann_ann[0], 2), "acqUcPtsAnnHi": num(uc_ann_hi, 2),
    "acqChCouponExpLo": num(100 * min(coupon25_exp), 1), "acqChCouponExpHi": num(100 * max(coupon25_exp), 1),
    "acqPfPage": BSA["figures"]["pro_forma_revenue_2025"]["pages"]["424b4"][0],
    "acqOrgPage": BSA["figures"]["organic_revenue_growth"]["pages"]["424b4"][0],
}
for k, v in R3_MACROS.items():
    mac(k, v)

MACROS.parent.mkdir(parents=True, exist_ok=True)
MACROS_P1.parent.mkdir(parents=True, exist_ok=True)
stamp = ("% Generated by code/verify_part2_acquirer.py from notes/case_bending_spoons_f1_extract.md and "
         "data/examples/invoice_chain.json (version " + str(J["meta"]["version"]) + "); do not edit.\n")
def used_in(files):
    u = set()
    for f in files:
        if f.exists():
            u |= set(re.findall(r"\\(acq[A-Za-z]+)", f.read_text(encoding="utf-8")))
    return u
P1_ALL = sorted(set(TEXFILES_P1) | set((ROOT / "sections").glob("*.tex")) | set((ROOT / "paper1").glob("*.tex")))
used_p1, used_p2 = used_in(P1_ALL), used_in(TEXFILES_P2)       # Paper 1's other sections also quote these macros
with open(MACROS, "w", encoding="utf-8") as fh:
    fh.write(stamp)
    for k in sorted(MAC):
        fh.write(f"\\providecommand{{\\{k}}}{{{MAC[k]}}}\n")
REQUIRED_P1 = {"acqGiTwentyFour", "acqGiTwentyFive"}          # read by code/paper1_macros.py (AcqTreadLo/Hi)
REQUIRED_P1 |= set(R3_MACROS)       # round 3: written before the editor's text uses them (notes/r3_macro_contract.md)
with open(MACROS_P1, "w", encoding="utf-8") as fh:
    fh.write(stamp)
    for k in sorted((used_p1 | REQUIRED_P1) & set(MAC)):
        fh.write(f"\\providecommand{{\\{k}}}{{{MAC[k]}}}\n")
print(f"  -> wrote {len(MAC)} macros to {MACROS.relative_to(ROOT)} and {len(used_p1 & set(MAC))} to {MACROS_P1.relative_to(ROOT)}")
check("G4 every \\acq macro used in either paper's .tex files is generated by this script",
      (used_p1 | used_p2) <= set(MAC), str(sorted((used_p1 | used_p2) - set(MAC))))
p1_text = "".join(f.read_text(encoding="utf-8") for f in TEXFILES_P1 if f.exists())
p1_refs = set(re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", p1_text))
p1_labels = set(re.findall(r"\\label\{([^}]+)\}", p1_text))
part1_labels = set()
for f in list((ROOT / "sections").glob("*.tex")) + list((ROOT / "sections" / "tables").glob("*.tex")):
    part1_labels |= set(re.findall(r"\\label\{([^}]+)\}", f.read_text(encoding="utf-8")))
check("G5 Paper 1 file references only Paper 1 labels (sections/*.tex), none from part2/",
      p1_refs <= part1_labels | p1_labels and all(f.exists() for f in TEXFILES_P1), str(sorted(p1_refs - part1_labels - p1_labels)))

n_pass = sum(ok for _, ok in RESULTS)
print(f"\nSUMMARY: {n_pass}/{len(RESULTS)} checks passed")
sys.exit(0 if n_pass == len(RESULTS) else 1)
