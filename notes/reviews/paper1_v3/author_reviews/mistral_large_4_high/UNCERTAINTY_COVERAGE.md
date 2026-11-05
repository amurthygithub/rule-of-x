# Uncertainty statement and coverage ledger

## Uncertainty
- Math: very low. All static closed forms verified symbolically and numerically to ~1e-13; budget and transience stress-tested; entry model reproduced; floors' closed forms verified. The only unproved element in the whole static-dynamic apparatus is (H), which the paper itself flags.
- Empirics: point estimates exact vs shipped data; intervals consistent under my independent bootstrap but I did not rerun the 999-rep seeded pipeline or the four interval types or the Holm/Romano-Wolf step-downs; the E2/imputation machinery was checked at the count level only.
- Case studies (Bending Spoons, AppLovin, CoreWeave): verified against the author's shipped raw extracts, which I could not independently re-fetch (network restricted); the F-1/prospectus figures themselves are unverified against EDGAR from here.
- Citations: 20 high-leverage items ledgered with access levels; ~15 with DOIs/URLs recorded in the repo's bib and verification notes; 2026-dated regulatory/tax items not re-verifiable from this environment.
- The engine (autofrontier) and companion paper (part2) are out of scope; their claims are not assessed.

## Coverage ledger
- Main PDF: 82/82 pages text-read; image-verified pages 1, 15, 16, 18, 21, 24, 26 (title, equations (5)-(14), budget, envelope, industry prop, entry). Printed page = PDF page throughout (letter, single column).
- Supplement: 57/57 pages text-read (S1-S9 + references); image-verified pages 1, 15, 20, 26.
- LaTeX sources: all sections/*.tex (~4,000 lines), paper1/*.tex preamble/tables.
- Code executed: verify_theory.py, verify_part2_acquirer.py, paper1_macros.py (author's); audit_*.py (mine, 15 scripts in scripts/).
- Data: panel_v3.csv fully re-read; companyfacts_extract.json spot-checked (AppLovin); v3_inputs raw 6-K json structure inspected.
- Deliberately unread (blindness): notes/referee{1,2,3}*/, notes/reviews/*, /root/outputs/rule-of-40-*, /root/outputs/theory-audit/*, prior ChatGPT critique if any. One accidental early peek at the first 40 lines of notes/referee1_report.md occurred before the rule was applied; no finding below uses it.
- Environment: python 3.12, numpy 2.5.2, scipy 1.18.1, sympy 1.14.0, pandas, statsmodels, pypdf 6.19.0, pdftotext/pdftoppm (poppler). No network to SEC/external sites from this sandbox; web_search returned non-relevant results and was not used for verification.
