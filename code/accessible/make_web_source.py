#!/usr/bin/env python3
"""Prepare the LaTeX sources of Paper 1 for the easy-read web edition and convert them with LaTeXML (5 Nov 2026).

Works on a scratch copy, never on the repository: `git archive` of HEAD into <scratch>/src, then
  - the main paper and the Supplementary Appendix in one document, so that cross-references between them resolve
    (the supplement's sections, tables, figures, equations and results keep their S numbers);
  - minipages as plain paragraphs and the summary box unwrapped (LaTeXML cannot size them for HTML);
  - figures as PNG at 220 dpi (pdftoppm), since browsers do not show PDF images;
  - xr-hyper dropped (one document needs no external references).
Then `perl -X latexmlc --format=html5` (Perl's deep-recursion warning on two long table notes is otherwise fatal).
Requires LaTeXML 0.8.8 (Debian package `latexml`) and poppler-utils.

Usage: python3 code/accessible/make_web_source.py <scratch dir>
       python3 code/accessible/build_web_reader.py <scratch>/out/paper.html <scratch>/out/figures <out html>
"""
import glob
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCR = os.path.abspath(sys.argv[1])
SRC = os.path.join(SCR, 'src')
shutil.rmtree(SRC, ignore_errors=True)
os.makedirs(SRC)
subprocess.run(f'git -C "{ROOT}" archive HEAD sections paper1 figures | tar -x -C "{SRC}"', shell=True, check=True)
os.chdir(SRC)

for f in sorted(set(re.findall(r'figures/(fig_[a-z_]+)\.pdf', ' '.join(open(p).read() for p in glob.glob('sections/**/*.tex', recursive=True))))):
    subprocess.run(['pdftoppm', '-r', '220', '-png', '-singlefile', f'figures/{f}.pdf', f'figures/{f}'], check=True)
for p in glob.glob('sections/**/*.tex', recursive=True):
    t = open(p).read()
    n = re.sub(r'\\begin\{minipage\}(\[[^\]]*\])?\{[^}]*\}', r'\\par ', t).replace('\\end{minipage}', '\\par ')
    n = re.sub(r'(includegraphics(\[[^\]]*\])?\{figures/fig_[a-z_]+)\.pdf\}', r'\1.png}', n)
    if p.endswith('exec_summary.tex'):
        n = n.replace('\\begin{center}\n', '').replace('\\end{center}', '')
        n = n.replace('\\fbox{\\par \\small\\setstretch{1.0}', '').replace('\\par }', '')
    if n != t:
        open(p, 'w').write(n)
pre = 'paper1/p1_preamble.tex'
pre_t = open(pre).read()
open(pre, 'w').write(pre_t.replace('\\usepackage{xr-hyper}', '% xr-hyper: not needed in the combined web build'))

main = open('paper1/paper1.tex').read()
sup = open('paper1/supplement.tex').read()
body = lambda t: t.split('\\begin{document}', 1)[1].rsplit('\\end{document}', 1)[0]
mb = re.sub(r'\{\\footnotesize\\setstretch\{1\.0\}\s*\\setlength\{\\bibsep\}\{1pt plus 1pt\}\s*\\bibliographystyle\{plainnat_p1\}'
            r'\s*\\bibliography\{paper1/refs_paper1\}\s*\}', '', body(main))
sb = body(sup).replace('\\maketitle', '')
reset = r'''
\clearpage
\section*{Supplementary Appendix}
\setcounter{section}{0}\setcounter{table}{0}\setcounter{figure}{0}\setcounter{equation}{0}
\setcounter{proposition}{0}\setcounter{lemma}{0}\setcounter{corollary}{0}\setcounter{remark}{0}\setcounter{definition}{0}\setcounter{assumption}{0}
\renewcommand{\thesection}{S\arabic{section}}\renewcommand{\thetable}{S\arabic{table}}
\renewcommand{\thefigure}{S\arabic{figure}}\renewcommand{\theequation}{S\arabic{equation}}
\renewcommand{\theproposition}{S\arabic{proposition}}\renewcommand{\thelemma}{S\arabic{lemma}}
\renewcommand{\thecorollary}{S\arabic{corollary}}\renewcommand{\theremark}{S\arabic{remark}}
\renewcommand{\thedefinition}{S\arabic{definition}}\renewcommand{\theassumption}{S\arabic{assumption}}
'''
head = main.split('\\begin{document}', 1)[0].replace('\\externaldocument[][nocite]{supplement}[supplement.pdf]', '')
assert not re.search(r'^[^%\n]*\\externaldocument', head, re.M), 'externaldocument left in the preamble'
open('web_combined.tex', 'w').write(head + '\\begin{document}\n' + mb + reset + sb + '\\end{document}\n')

out = os.path.join(SCR, 'out')
shutil.rmtree(out, ignore_errors=True)
log = os.path.join(SCR, 'latexml.log')
with open(log, 'w') as fh:
    r = subprocess.run(['perl', '-X', '/usr/bin/latexmlc', '--format=html5', f'--dest={out}/paper.html', '--path=.', '--path=paper1',
                        '--nocomments', 'web_combined.tex'], stdout=fh, stderr=subprocess.STDOUT)
summary = [l for l in open(log) if l.startswith(('Conversion complete', 'Post-processing complete', 'Fatal'))]
print(''.join(summary).strip())
if r.returncode != 0 or any(l.startswith('Fatal') for l in summary):
    sys.exit(f'latexmlc failed (exit {r.returncode}); see {log}')
