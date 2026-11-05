# Re-review deliverables — *The Rule of 40 as a Price Line* (build of 4 November 2026)

## Inputs

| Input | SHA-256 |
|---|---|
| Re-review bundle `rereview_deepseek.zip` | `8e24b60adaefe9ad0ac76b2c176361ee6a0910a7c8075c2136f52e247b456048` |
| `paper1.pdf` (87 pages) | `9e986ecac307d445b0f9a636788100d8fc680f3a5508b609b430ab457788c55b` |
| `supplement.pdf` (72 pages) | `1da736731466b00d583ee0055480bae7ad809c114edb25ad232a6d8078f2b81f` |
| `RESPONSE.md` | `fade47b79f9a69e7475bb1af97e682c517fe785bff01f1fb5025fa8f256a46cb` |
| `PROMPT.md` | `cbcf1348958d883762c89938fe634f4f77e1a724fd39e0717ff31ebe25a427a9` |
| Repository | `github.com/amurthygithub/rule-of-x`, branch `review-round-3`, commit `eb7537bee7585f2902304f62a722edea6ced8539` |

## Independence record

Part B (the fresh assessment) was written and saved **before** I read anything restricted. I did not read, before or after, any of: the other reviewers' folders in `notes/reviews/paper1_v3/author_reviews/`; any file in `notes/reviews/paper1_v4/` other than my own; or `notes/reviews/paper1_v3/response_to_outside_reviews.md`.

Hash of `rereview_report.md` (which contains Part B) as first saved:
`30f70e45ff92fc2d30ea008042db40756313a9c9d429244ae30c5e22a3abfff9`

## Deliverables

- `rereview_report.md` — Parts A–D, one-paragraph verdict first.
- `response_audit.csv` — columns `id, our_status, your_verdict, evidence, locator` (74 rows + 6 stress-test rows).
- `scripts/` — `independent_empirics.py` (my independent re-estimation of the headline statistics).
- `results/` — execution logs: `verify_theory_output.txt` (202/202 pass), `macros_output.txt`, `supp_extensions_output.txt` (27/27), `build_paper1_output.txt` (87+72 pp).

## Environment

DeepSeek V4 Pro (high effort). Python 3.12.3; numpy 2.5.2, pandas 3.0.3, scipy 1.18.1, sympy 1.14.0, mpmath 1.3.0, statsmodels 0.15.0, matplotlib 3.11.1. TeX Live installed via apt (base, recommended, extra, science, fonts-extra) to run `build_paper1.sh`. The lock file `requirements-lock.txt` specifies Python 3.13.18/numpy 2.5.3/pandas 3.0.5; I used the closest available versions and observed no effect on any checked number.

## Not run / not accessed

- `formal/` Lean 4 build (`lake build`) — no Lean 4 toolchain; the formalization was inspected but not executed.
- `regenerate_all.sh` — would re-fetch third-party raw data and run ~1h; committed outputs were verified instead.
- The other outside reviewers' reports and responses (per the independence rule).
