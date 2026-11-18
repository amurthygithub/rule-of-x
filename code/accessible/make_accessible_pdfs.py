#!/usr/bin/env python3
"""Build accessible PDF editions of Paper 1 and its Supplementary Appendix (5 Nov 2026).

Works on a scratch copy, never on the repository: `git archive` of HEAD into <scratch>/<variant>/src, a few changes to
the preamble and the two document classes there, then code/build_paper1.sh with PAPER_ROOT set to that copy and
NO_COPY=1, so paper1/*.pdf are never touched. The text, numbers, tables, equations and figures are the same as in the
standard build; only the presentation changes.

Variants
  dyslexia  12 pt sans-serif text (Helvetica clone, with math letters in the same face), line spacing 1.5, space
            between paragraphs instead of indents, ragged right (no justification), no hyphenation, lines of about
            70 characters, slightly wider letter spacing, no ligatures, theorem statements upright, emphasis in bold
            rather than italics, a cream page. Follows the British Dyslexia Association's style guide where pdfLaTeX can.
  tagged    EXPERIMENTAL; DOES NOT COMPLETE ON TEX LIVE 2023. The standard layout as a tagged PDF (LaTeX's tagging
            project): a structure tree with headings, paragraphs and figures with alternative text, so that a screen
            reader can announce them. On TeX Live 2023 (the version installed here) the tagging code is a test phase:
            its float, bib, block, text, minipage and table modules stop on this source, longtable needs tagging paused
            (done below), and with the remaining modules pdfLaTeX still stops in Section 6 with "required tag missing".
            Kept for a newer TeX Live (2025 or later), where tagging and MathML (LuaLaTeX) are more complete; untested
            there. Until then the easy-read web edition (build_web_reader.py) is the screen-reader edition: real headings,
            figure descriptions, table markup and MathML equations.
Both variants write a Unicode map for every glyph and the document language, so that copied or read-aloud text has no
broken ligatures or math symbols.

Usage: python3 code/accessible/make_accessible_pdfs.py <scratch dir> [dyslexia|tagged ...]
Output: <scratch>/out/{paper1,supplement}_{variant}.pdf
"""
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCR = os.path.abspath(sys.argv[1])
VARIANTS = sys.argv[2:] or ['dyslexia', 'tagged']
# Tagging modules of TeX Live 2023 that this paper compiles with: paragraphs, sections, contents and graphics. The float,
# bib, block, text and minipage modules of phase-III, and the separate table module, stop with errors on this source.
TAG_MODULES = os.environ.get('TAG_MODULES', 'phase-II,sec,toc,graphic')

ALT = {  # the same descriptions as the web edition (build_web_reader.py)
    'fig_frontier_tangency': "Diagram: a curved frontier of the growth and margin a company can reach, with straight lines "
                             "of equal score. The highest score is where a line just touches the curve.",
    'fig_saturation': "Line chart: the highest Rule-of-40 score falls as a company's market share rises toward its limit. "
                      "With no capital needs it falls from about 124 to 70; with capital needs of 0.3 from about 97 to 64; "
                      "with 0.6 from about 73 to 58. All three stay above the Rule of 40.",
    'fig_spec_curve': "Specification curve: the value of each headline empirical claim over every combination of the "
                      "paper's analysis choices.",
    'fig_stress': "Two histograms from one million draws of the stress test. Left: the 2036 central score, mostly between "
                  "about 41 and 67, with the central path at 58. Right: the market growth needed for a cash score of 100, "
                  "mostly between about 28% and 40% a year with computing at 6% of revenue, with a long tail when the cost "
                  "of computing varies.",
}

DYSLEXIA_PREAMBLE = r'''
% ---- dyslexia-friendly edition (code/accessible/make_accessible_pdfs.py) ----
\usepackage[scaled=0.97]{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage[italic]{mathastext}              % math letters and digits in the text face
\usepackage[document]{ragged2e}              % ragged right: even word spacing
\hyphenpenalty=10000 \exhyphenpenalty=10000  % no hyphenation
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.7em plus 0.2em minus 0.1em}
\usepackage[tracking=true]{microtype}
\SetTracking{encoding=T1}{30}                % slightly wider letter spacing in the text face
\DisableLigatures{encoding=T1}
\pagecolor[HTML]{FBF6E9}                     % cream page
\let\origemph\emph
\renewcommand{\emph}[1]{\textbf{#1}}         % emphasis in bold, not italics
\usepackage{etoolbox}
\AtBeginEnvironment{thebibliography}{\renewcommand{\emph}[1]{#1}}
\AtBeginEnvironment{longtable}{\setstretch{1.2}}
\tolerance=9999 \emergencystretch=3em        % ragged lines never run into the margin
% The sans face is wider and the type larger than in the standard edition, so a few tables would no longer fit:
% a table wider than the line may use up to 0.8 in of each side margin, and is scaled down only beyond that; a float
% taller than the page is scaled to the page. Tables inside tables are left alone.
\usepackage{adjustbox}
\makeatletter
\newcount\dys@depth
\def\dys@open{\begin{adjustbox}{max width=\dimexpr\linewidth+1.6in\relax,center}}
\def\dys@close{\end{adjustbox}}
\BeforeBeginEnvironment{tabular}{\ifnum\dys@depth=0 \let\dys@next\dys@open\else\let\dys@next\relax\fi
  \global\advance\dys@depth by 1 \dys@next}
\AfterEndEnvironment{tabular}{\global\advance\dys@depth by -1 \ifnum\dys@depth=0 \let\dys@next\dys@close\else
  \let\dys@next\relax\fi\dys@next}
\renewenvironment{abstract}{\par\medskip\noindent{\large\bfseries\abstractname}\par\smallskip}{\par\medskip}
\newsavebox{\dys@float}
\renewenvironment{table}[1][tbp]{\@float{table}[#1]\begin{lrbox}{\dys@float}\begin{minipage}{\linewidth}}
  {\end{minipage}\end{lrbox}\centering
   \ifdim\dimexpr\ht\dys@float+\dp\dys@float\relax>0.97\textheight
     \resizebox*{!}{0.97\textheight}{\usebox{\dys@float}}%
     \typeout{dyslexia edition: float scaled to the page from \the\dimexpr\ht\dys@float+\dp\dys@float\relax}%
   \else\usebox{\dys@float}\fi\end@float}
\makeatother
'''


def sub1(text, old, new, what):
    assert text.count(old) == 1, f'{what}: expected one "{old}", found {text.count(old)}'
    return text.replace(old, new)


def prepare(variant):
    base = os.path.join(SCR, variant)
    src = os.path.join(base, 'src')
    shutil.rmtree(base, ignore_errors=True)
    os.makedirs(src)
    subprocess.run(f'git -C "{ROOT}" archive HEAD sections paper1 figures | tar -x -C "{src}"', shell=True, check=True)
    pre_p = os.path.join(src, 'paper1', 'p1_preamble.tex')
    pre = open(pre_p).read()
    pre = sub1(pre, '\\usepackage[T1]{fontenc}', '\\usepackage[T1]{fontenc}\n\\input{glyphtounicode}\\pdfgentounicode=1',
               'fontenc')
    pre = sub1(pre, '\\usepackage{setspace}', '\\hypersetup{pdflang=en-US,pdfdisplaydoctitle=true}\n\\usepackage{setspace}',
               'pdflang')
    docs = {}
    for d in ('paper1', 'supplement'):
        docs[d] = open(os.path.join(src, 'paper1', f'{d}.tex')).read()
    other = {'paper1': 'supplement', 'supplement': 'paper1'}
    for d in docs:
        o = other[d]
        docs[d] = sub1(docs[d], f'\\externaldocument[][nocite]{{{o}}}[{o}.pdf]',
                       f'\\externaldocument[][nocite]{{{o}}}[{o}_{variant}.pdf]', f'{d} externaldocument')
    if variant == 'dyslexia':
        pre = sub1(pre, '\\usepackage[margin=1in]{geometry}', '\\usepackage[margin=1.1in]{geometry}',
                   'geometry')
        pre = sub1(pre, '\\setstretch{1.08}', '\\setstretch{1.5}', 'setstretch')
        pre = sub1(pre, '\\usepackage{amsmath,amssymb,amsthm}',
                   '\\usepackage{amsmath,amssymb,amsthm}\n\\makeatletter\\def\\th@plain{\\normalfont}'
                   '\\def\\th@remark{\\thm@headfont{\\bfseries}\\normalfont}\\makeatother'
                   '  % theorem statements upright, remark titles bold', 'amsthm')
        pre = sub1(pre, '\\setlist{itemsep=2pt,topsep=4pt}', '\\setlist{itemsep=4pt,topsep=4pt}' + DYSLEXIA_PREAMBLE,
                   'setlist')
        for d in docs:
            docs[d] = sub1(docs[d], '\\documentclass[11pt]{article}', '\\documentclass[12pt]{article}', f'{d} class')
        # the one display equation that no longer fits the line: its two limits on two lines, same text
        mp = os.path.join(src, 'sections', 'model.tex')
        m = open(mp).read()
        m = sub1(m, '\\label{eq:Rrent}\nR_X', '\\label{eq:Rrent}\n\\begin{gathered}R_X', 'eq:Rrent start')
        m = sub1(m, '\\text{(input owners)},\\qquad R_X', '\\text{(input owners)},\\\\ R_X', 'eq:Rrent break')
        m = sub1(m, '\\text{(other firms)}.\n\\end{equation}', '\\text{(other firms)}.\\end{gathered}\n\\end{equation}',
                 'eq:Rrent end')
        open(mp, 'w').write(m)
    elif variant == 'tagged':
        # longtable is not yet compatible with paragraph tagging in this release: its four tables are left untagged
        pre = sub1(pre, '\\usepackage{longtable}', '\\usepackage{longtable}\n\\usepackage{etoolbox}'
                   '\\BeforeBeginEnvironment{longtable}{\\tagstop}\\AfterEndEnvironment{longtable}{\\tagstart}',
                   'longtable')
        for d in docs:
            docs[d] = sub1(docs[d], '\\documentclass[11pt]{article}',
                           f'\\DocumentMetadata{{testphase={{{TAG_MODULES}}},lang=en-US,pdfversion=1.7}}\n'
                           '\\documentclass[11pt]{article}', f'{d} class')
        # alternative text for the four figures
        for dirpath, _, files in os.walk(os.path.join(src, 'sections')):
            for f in files:
                p = os.path.join(dirpath, f)
                t = open(p).read()
                n = re.sub(r'\\includegraphics\[([^\]]*)\]\{figures/(fig_[a-z_]+)\.pdf\}',
                           lambda m: f'\\includegraphics[{m.group(1)},alt={{{ALT[m.group(2)].replace("%", r"\%")}}}]'
                                     f'{{figures/{m.group(2)}.pdf}}', t)
                if n != t:
                    open(p, 'w').write(n)
    else:
        sys.exit(f'unknown variant {variant}')
    open(pre_p, 'w').write(pre)
    for d in docs:
        open(os.path.join(src, 'paper1', f'{d}.tex'), 'w').write(docs[d])
    return base, src


os.makedirs(os.path.join(SCR, 'out'), exist_ok=True)
status = 0
for v in VARIANTS:
    base, src = prepare(v)
    build = os.path.join(base, 'build')
    env = dict(os.environ, PAPER_ROOT=src, NO_COPY='1')
    r = subprocess.run(['bash', os.path.join(ROOT, 'code', 'build_paper1.sh'), build], env=env,
                       capture_output=True, text=True)
    print(f'== {v}\n{r.stdout.strip()}\n{r.stderr.strip()}'.strip())
    for d in ('paper1', 'supplement'):
        pdf = os.path.join(build, f'{d}.pdf')
        if os.path.exists(pdf):
            shutil.copy(pdf, os.path.join(SCR, 'out', f'{d}_{v}.pdf'))
        log = os.path.join(build, f'{d}.log')
        if os.path.exists(log):
            lt = open(log, errors='replace').read()
            print(f'{d}: {lt.count("Overfull \\hbox")} overfull hboxes')
    status |= r.returncode
sys.exit(status)
