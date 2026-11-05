# Lead-adjudicated Part A rows (GLM-19, GLM-21, GLM-22) — re-review round 2
Written by the Lead. Evidence bases: round-1 archived materials, the new PDFs, and the repo at eb7537b.

## GLM-19 — Cottier et al. (2025): 9-900× (Epoch insight) vs 10-1,000× (Gundlach's paraphrase)
**Author status:** Already handled ("The number matches its cited source. No change.").
**Verdict: AGREE — already handled (resolved as no action needed).**
Evidence: round-1 referee E's ledger (first_reports/E_prior_art.md, entry #13) verified the
paper's "9x to 900x per year" verbatim against the cited Epoch AI insight (full text fetched),
and noted independently that Gundlach et al.'s abstract paraphrases a Cottier estimate as
"10–1,000×/yr" — a different rounding of a related analysis. The paper cites its own source
correctly; the round-1 item was a versioning observation (E's open question 8), not a finding of
error. The author's disposition is correct. No locator dispute: main §2.4, printed p. 10 (round-1
numbering); unchanged text verified by R-C2's Unit 0 pass.

## GLM-21 — The [54, 62] 2036-score interval reflects anchor resampling only; possible misreading
**Author status:** Fixed (= GPT-24 and GPT-9; see ST-2).
**Verdict: RESOLVED.**
Evidence (new PDFs): the abstract now says "reaches a lasting score of 58 (53 while still paying
for changes under way; 54 to 62 from sampling alone)" (main p. 1); the summary box says
"(about 53 while it still pays for transitions in flight; 54 to 62 from anchor sampling alone)"
and adds the joint range "with every scenario input moved jointly 90% of draws of the score lie
between 40.7 and 66.7 (draws uniform over the stated ranges, log-uniform for compute per dollar
of labor, an assumption)" (main p. 2); §9 carries "from sampling alone" (main p. ~74). The
misreading my round-1 report flagged (quoting [54,62] as if it were total uncertainty) is now
pre-empted on the face of every quoted instance, and the joint-input range is disclosed with its
draw assumptions. ST-2's stored-output verification (R-D) completes the audit.

## GLM-22 — "The supplied PDFs are newer than every PDF committed"; "the committed .tex also lags
the supplied PDFs"; "the repo as committed cannot rebuild the supplied PDFs"
**Author status:** Not valid (reviewer error) — "the reviewed PDFs are older than the committed
sources."
**Verdict: I ACCEPT "Not valid (reviewer error)" — with one preserved caveat.**
Evidence: (i) the supplied round-1 main PDF's CreationDate is 2026-11-03 01:48:59 CET
(= 2026-11-02 15:48 PST; pdfinfo, round-1 §1); (ii) the repo commits at issue are e31c08d
("Paper 1: repository URL in the footnote and S6", 2026-11-02 19:30 PST) and 62e574b (19:55 PST),
with the committed paper1/paper1.pdf created 19:27 PST — all AFTER the supplied build; (iii) the
one visible text difference (footnote "available from the author" vs the repository URL) is
explained by the URL being ADDED at 19:30, after the supplied PDF was built. My round-1 direction
claim ("supplied newer than committed") was therefore reversed, and the inference I drew from the
footnote difference was wrong. Preserved caveat (not in dispute): the hash mismatch itself was
real — the repo at 62e574b could not rebuild the supplied PDFs exactly, which was the actionable
part of the finding; the author's response does not contest it, and the new round states the
pipeline now reproduces from a fresh clone (item 8), which resolves that substance. Lesson
recorded: I inferred file age from content differences instead of checking timestamps first.
