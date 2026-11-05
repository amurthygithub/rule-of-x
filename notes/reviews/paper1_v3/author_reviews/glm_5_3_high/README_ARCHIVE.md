# Archive note: GLM 5.3 (high effort) review bundle, redacted copy

This folder holds a **redacted copy** of the review bundle `rule-of-40-review/` that GLM 5.3 (high effort) returned on 2 to 3 November 2026. It was archived on 2 November 2026.

## Redaction (made at the author's instruction)

One registrant is excluded from all data at the author's request (`code/exclusions.py`). The reviewers inverted the stored digest and named the registrant and its CIK in three files: `referee_report.md`, `adversarial_audit/F_audit.md` and `first_reports/B_econometrics.md`. In this copy:

- every occurrence of the registrant's name, matched case-insensitively, reads `[excluded registrant]` (11 occurrences);
- every occurrence of its CIK, decimal or zero-padded, reads `[CIK]` (7 occurrences).

The strings were derived in memory from the bundle and never written down. After redaction, `rg -i` for the name, the decimal CIK and the zero-padded CIK over this folder (text, binary and compressed files) returns no match. No other file in the bundle contained either string. That includes the Bending Spoons filing texts, which were scanned before they were kept. No unredacted copy is kept under the repository.

## Files left out (14 of 111)

| Bundle path | Reason |
|---|---|
| `diagnostics/accounting/tickers.json` | SEC company-ticker list: third-party bulk data |
| `diagnostics/prior-art/bs_f1.txt` | byte-identical duplicate of `diagnostics/accounting/bs_f1.txt` |
| `diagnostics/prior-art/bs_q2_ex991.txt` | byte-identical duplicate of `diagnostics/accounting/bs_q2_ex991.txt` |
| `diagnostics/prior-art/palantir_q2.txt` | byte-identical duplicate of `diagnostics/accounting/pltr_q2_pr.txt` |
| `diagnostics/prior-art/bain_bosche.txt`, `bain_depeyrot.txt`, `bain_lipman.txt` | full text of third-party copyrighted web articles (Bain & Company) |
| `diagnostics/prior-art/becker2025.txt`, `cottier2024.txt`, `gundlach2025.txt` | full text of third-party papers (arXiv 2507.09089, 2405.21015, 2511.23455) |
| `diagnostics/prior-art/dellacqua_wp.txt`, `lee2024.txt` | full text of third-party papers (HBS WP 24-013; MPRA 121568) |
| `diagnostics/prior-art/cottier_inf2.txt`, `cottier_inference.txt` | third-party web pages (Epoch AI; the second is a 404 page) |

The third-party texts were left out as a copyright precaution; they are not needed to check any finding, and each can be fetched again from the identifier above. The original bundle, which still names the excluded registrant, should be kept outside the repository and treated as sensitive.

## Kept

The rest of the bundle is unchanged apart from the redaction: the report, the first reports, the F audit, the diagnostics (scripts, outputs, the copies of our own `notes/` outputs under `diagnostics/econometrics-empirics/baseline/`), and the public SEC filing texts for Bending Spoons (`bs_f1.txt`, `bs_424b4.txt`, `bs_q2_ex991.txt`, `bs_q2_ex992.txt`, `bs_6k.txt`, `bs_q2.txt`), Palantir and CoreWeave. The bundle's own `README.md` and `SOURCE_MANIFEST.md` describe the original layout. Some files that the reports cite were never shipped in the bundle, for example `nei_article.html` and `vista_20260118.html` (both named in `adversarial_audit/F_audit.md`).

## Added by us (not part of the bundle)

- `issue_log.md`: the verification of every finding.
- `verification_claude/`: our scripts and their outputs. They read the bundle's filing texts and the repository's own code and data, and they never import the reviewers' code.
