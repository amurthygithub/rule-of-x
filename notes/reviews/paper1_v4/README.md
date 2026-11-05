# Paper 1, revised third version (4 November 2026): responses to the outside reviews and the re-review

- `paper1_v4.pdf`, `supplement_v4.pdf`: the build sent for re-review (main paper 87 pages, supplement 72 pages).
- `response_deepseek.md`, `response_gpt.md`, `response_glm.md`, `response_mistral.md`: one response per reviewing model
  (DeepSeek V4 Pro, GPT-6.1 Sol, GLM 5.3, Mistral Large 4), written by `make_letters.py` from the dispositions of
  `../paper1_v3/response_to_outside_reviews.md`, with supplement section numbers rewritten to this build (`_locmap.py`;
  checked label by label against the .aux files of the reviewed build 62e574b, the response build be86d24 and this one),
  the stress-test rows restated with the million-draw values, and numbers tagged with a macro set to its current value.
- Model label: `response_gpt.md` and the GPT package, as sent on 4 November, call the reviewer GPT-6.2 Sol and point to
  `paper1_v3/author_reviews/gpt_6_2_sol_xhigh/`. On 5 November the author stated that both GPT reviews ran on GPT-6.1 Sol;
  the folder is now `paper1_v3/author_reviews/gpt_6_1_sol_xhigh/`, and the sent letter and packages are kept unchanged.
- `rereview_prompt.md`: the prompt for the re-review, with placeholders `{MODEL}`, `{KEY}`, `{FOLDER}` and `{COMMIT}`;
  `make_package.py` fills them and writes one package per reviewer to `dist/rereview/`.
- Changes since the reviews: Supplement S4 (Lean formalization), S10 (stress test, a million draws per seed), S11
  (specification curve), S12 (three analyses added after the round, at the author's decision of 4 November), R2 on the
  whole main sample, the data audit, the compute-share units fix, the reproduction from a fresh clone, the legal and tax
  primary-source pass, and an abstract in plain language (4 November).
