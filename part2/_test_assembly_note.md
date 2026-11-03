# Part II test assembly (P2 theory pass v2, 29 October 2026)

Temporary build used to check that every Part II file compiles together with no undefined references or citations. It is not a release master. Built in a fresh scratch directory (/tmp/claude-0/-home-claude/4bf09440-69e8-5b18-ac88-c305bd8d97f5/scratchpad/p2build_v2_164615) holding symbolic links to `part2/`, `sections/`, `paper1/`, `figures/`, `data/` and `refs.bib`, so that `\input` paths resolve as they do from the repository root and no stale copies are read.

## Steps

1. Part I label donor: compile `paper1/paper1.tex` (copied to `p1m.tex`; pdflatex, bibtex, pdflatex twice). Keep only its `\newlabel` lines: `grep '^\\newlabel' p1m.aux > p1labels.aux` (143 labels). Importing the full aux would also import Part I's `\bibcite` lines and produce "Citation multiply defined" warnings for keys both parts cite.
2. Part II assembly (below): pdflatex, bibtex, pdflatex, pdflatex (one more pass if LaTeX asks to rerun).

## Result (about 16:52 system time, 29 October 2026)

- 240 pages; 0 LaTeX errors; 0 undefined references; 0 undefined citations; no multiply defined labels or citations; BibTeX: no warnings, 457 entries.
- Loaded: every `part2/theory_*.tex` (with `theory_competition.tex` through `theory_ext.tex`), the three literature files, `validation_backtest.tex` and its seven tables, every `part2/proofs_*.tex`, and the playbook tables, including the two playbook inputs `part2/tables/playbook_processes.tex` and `part2/tables/playbook_steps_full.tex` (longtable, through `proofs_playbook.tex`), plus all generated macro files in `part2/tables/`.
- Three overfull boxes of at most 4.3pt (playbook Lemma on the calibrated firm, playbook Proposition (a), one display in the labor proofs).
- Fixed on the way: Part~II cited Part~I's Table `tab:gap`, which the current Part~I no longer contains; `part2/theory_playbook.tex`, `part2/tables/playbook_table.tex` and its generator `code/playbook/run_archetypes.py` now describe the bands and sample directly (growth bands with edges at 0, 10, 20, 30, 40 and 60%; `code/decompose_gap.py`).

## Assembly file (`p2_test_assembly.tex`, preamble inlined)

```latex
% Test assembly of Part II (P2 theory pass v2, 29 Oct 2026). Temporary: compiled in the session scratchpad only.
% Part I labels are imported with xr-hyper from p1labels.aux, the \newlabel lines of paper1/paper1.tex as built.
\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{mathptmx}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{xurl}
\usepackage{graphicx}
\usepackage{array}
\usepackage{enumitem}
\usepackage[authoryear,round]{natbib}
\usepackage{xcolor}
\usepackage{xr-hyper}
\usepackage[colorlinks=true,linkcolor=blue!50!black,citecolor=blue!50!black,urlcolor=blue!50!black]{hyperref}
\usepackage{setspace}
\setstretch{1.08}
\setlist{itemsep=2pt,topsep=4pt}

\newtheorem{proposition}{Proposition}
\newtheorem{lemma}{Lemma}
\newtheorem{corollary}{Corollary}
\theoremstyle{definition}
\newtheorem{definition}{Definition}
\newtheorem{assumption}{Assumption}
\theoremstyle{remark}
\newtheorem{remark}{Remark}

\externaldocument{p1labels}
\IfFileExists{paper1/macros.tex}{\input{paper1/macros.tex}}{}
\begin{document}
\title{The Economics of AI Transformation (Part II): test assembly}
\date{29 October 2026}
\maketitle
\input{part2/theory_core.tex}
\input{part2/theory_ext.tex}
\input{part2/theory_accounting.tex}
\input{part2/theory_labor.tex}
\input{part2/theory_product.tex}
\input{part2/theory_regimes.tex}
\input{part2/theory_acquirer.tex}
\input{part2/theory_playbook.tex}
\section{Related work and validation}\label{sec:p2-test-related}
\input{part2/literature_part2.tex}
\input{part2/literature_modern.tex}
\input{part2/literature_reliability.tex}
\input{part2/validation_backtest.tex}
\bibliographystyle{plainnat}
\bibliography{refs,part2/refs_part2,part2/refs_modern,part2/refs_reliability,part2/refs_accounting,part2/refs_labor,part2/refs_product,part2/refs_regimes,part2/refs_acquirer,part2/refs_competition}
\appendix
\input{part2/proofs_core.tex}
\input{part2/proofs_ext.tex}
\input{part2/proofs_competition.tex}
\input{part2/proofs_accounting.tex}
\input{part2/proofs_labor.tex}
\input{part2/proofs_product.tex}
\input{part2/proofs_regimes.tex}
\input{part2/proofs_acquirer.tex}
\input{part2/proofs_playbook.tex}
\end{document}
```
