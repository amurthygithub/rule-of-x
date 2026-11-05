#!/usr/bin/env python3
"""Easy-read web edition of Paper 1 and its Supplementary Appendix (5 Nov 2026).

Input : the HTML that LaTeXML 0.8.8 writes from a combined source of the main paper and the supplement
        (code/accessible/make_web_source.py prepares that source in a scratch copy and runs latexmlc).
Output: one self-contained page (styles, script, figures as data URIs) with reading settings (typeface, size, line
        spacing, line length, letter spacing, background), read-aloud by section through the browser's speech engine
        (equations skipped, inline math read as words), a key-points box under every section title, a skim mode that
        shows only titles and key points, an option to fold display equations, and a table of contents.
The text, numbers, tables and equations are LaTeXML's rendering of the LaTeX sources: nothing in them is retyped here.
The key points and the figure descriptions below are the only words this script adds.

Usage: python3 code/accessible/build_web_reader.py <latexml html> <figures dir> <out html>
"""
import base64
import html as H
import os
import re
import sys

from bs4 import BeautifulSoup

SRC, FIGDIR, OUT = sys.argv[1:4]

KEY = {
    'S1': ["The Rule of 40 adds revenue growth and profit margin. It draws a line of equal score, not of equal value.",
           "The paper asks which mixes of growth and margin a company can reach, how high the score can go, how AI changes "
           "that over two, five and ten years, and what a company needs to get there.",
           "It answers with a model, the SEC filings of 284 software-classified companies and a calibrated scenario."],
    'S2': ["Earlier work studies growth and profit, values growth by how long it lasts, or tests the rule as a screen.",
           "Few studies ask which mixes a company can reach, or how AI automation changes them."],
    'S3': ["To grow faster than its market, a company must spend, and each extra dollar buys less growth than the one before.",
           "The best score is the margin at zero growth, plus market growth net of the capital it needs, plus a gain from "
           "taking share that does not last.",
           "Under an assumption the paper checks numerically but does not prove, a company should count a point of growth "
           "at the value of an extra dollar of revenue.",
           "With free entry, competition passes automation's savings to customers. Only an input rivals cannot copy keeps "
           "more than a normal return."],
    'S4': ["The data are the SEC filings of 284 software-classified companies, 2010 to 2025, as first reported.",
           "The margin used changes the answer: GAAP operating margin, and free cash flow before and after stock-based pay, "
           "give different scores."],
    'S5': ["The score that only the top 5% reach fell by about 12 points from 2016-19 to 2023-25, as fewer companies grew fast.",
           "At the top, one more point of growth came with about a fifth of a point less margin.",
           "The data cannot show the weight on growth that companies act on."],
    'S6': ["Growth bought through acquisitions enters the score, but its price does not.",
           "For one serial acquirer, a GAAP score of about 116 becomes 87 to 114 on cash before interest when its "
           "acquisitions are charged as capital."],
    'S7': ["AI still costs money: computing, fees, controls, security, maintenance and errors.",
           "At central costs and fixed prices, full automation keeps a mature, asset-light company's cash score below 100 "
           "unless its market grows more than 32.5% a year.",
           "In the central scenario, which is not a forecast, a top company reaches a lasting score of 58 by 2036, and its "
           "program repays its costs in 7.5 years."],
    'S8': ["Investors' screening weight and a company's own decision weight on growth are different numbers.",
           "Execution sets the pace of automation, and accountability for financial reports stays.",
           "The limits: no forecast, no test of returns, one unproved assumption, and reviews by AI models, not by human experts."],
    'S9': ["The conclusion answers the paper's four questions in turn."],
    'A1': ["How the author and the AI agents worked, every decision the author made, and how the paper was reviewed."],
    'A1a': ["Further theoretical results and the notation."],
    'A2': ["Further discussion of the model, including the evidence on the cost of AI computing."],
    'A3': ["The proofs of the main paper's results."],
    'A4': ["The static model, checked by a computer proof assistant (Lean 4)."],
    'A5': ["Proofs and details for the section on acquisitions."],
    'A6': ["Why a \"Rule of 1000\" is possible only briefly, at small share and with very large spending."],
    'A7': ["How the data were built, robustness tables, and the source of every parameter."],
    'A8': ["The records of the research protocol and of the reviews."],
    'A9': ["The full-cost floors and the accountability floor in numbers, and when owning AI servers pays."],
    'A10': ["A stress test that moves all scenario inputs together, and which claims hold everywhere."],
    'A11': ["Each empirical claim tested over every reasonable combination of analysis choices."],
    'A12': ["Three further analyses: how market values weight growth and margin, the cost of not automating, and what sets "
            "the payback."],
    'A13': ["A glossary of the paper's terms in plain language."],
}
ALT = {
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
LABELS = {'tab:decisions': ('8', 'A1'), 'tab:param-sources': ('S11', 'A7'), 'tab:agents': ('S13', 'A8'),
          'tab:errors': ('S15', 'A8')}

soup = BeautifulSoup(open(SRC, encoding='utf-8').read(), 'lxml')
art = soup.find('article')
assert art is not None, 'no article element'
for tag in art.find_all(['script', 'style', 'link']):
    tag.decompose()

# section titles: "Appendix S10 ..." -> "S10 ..."; the appendix of the main paper keeps "Appendix A"
for h in art.find_all(class_='ltx_title_appendix'):
    tag = h.find(class_='ltx_tag')
    if tag and re.match(r'Appendix S\d+', tag.get_text(strip=True)):
        tag.string = tag.get_text(strip=True).replace('Appendix ', '') + ' '

# references LaTeXML could not anchor (labels inside longtable captions)
for t in art.find_all(string=re.compile(r'LABEL:tab:')):
    def rep(m):
        num, sec = LABELS[m.group(1)]
        return f'\u0001{num}\u0002{sec}\u0003'
    t.replace_with(re.sub(r'LABEL:(tab:[a-z-]+)', rep, str(t)))

# figures: data URIs and descriptions
for img in art.find_all('img'):
    src = img.get('src', '')
    stem = os.path.splitext(os.path.basename(src))[0]
    path = os.path.join(FIGDIR, os.path.basename(src))
    if os.path.exists(path):
        img['src'] = 'data:image/png;base64,' + base64.b64encode(open(path, 'rb').read()).decode()
    img['alt'] = ALT.get(stem, img.get('alt') or 'Figure')
    img['loading'] = 'lazy'
    for a in ('width', 'height', 'style'):
        img.attrs.pop(a, None)

# wide tables and display equations scroll inside their own box; equations are skipped when read aloud
for tb in art.find_all('table'):
    if tb.find_parent('table') is not None:
        continue
    cls = tb.get('class', [])
    eq = any(c.startswith('ltx_equation') for c in cls)
    wrap = soup.new_tag('div', attrs={'class': 'scroll' + (' eqbox' if eq else ' tablebox')})
    if eq:
        wrap['data-skip'] = 'equation'
    else:
        wrap['data-skip'] = 'table'
    tb.wrap(wrap)
    if eq:
        btn = soup.new_tag('button', attrs={'class': 'eqshow', 'type': 'button'})
        btn.string = 'Show equation'
        wrap.insert_before(btn)

# key points, section listen buttons and the table of contents
toc = []
for sec in art.find_all('section', class_=['ltx_section', 'ltx_appendix']):
    sid = sec.get('id')
    h2 = sec.find(['h2'], recursive=False) or sec.find('h2')
    if not sid or h2 is None:
        continue
    title = h2.get_text(' ', strip=True)
    supp = sid.startswith('A') and sid != 'A1'
    if sid == 'Ax1':
        supp = True
    toc.append((sid, title, supp))
    bar = soup.new_tag('div', attrs={'class': 'secbar'})
    b = soup.new_tag('button', attrs={'class': 'listen', 'type': 'button', 'data-sec': sid,
                                      'aria-label': f'Listen to {title}'})
    b.string = 'Listen to this section'
    bar.append(b)
    h2.insert_after(bar)
    if sid in KEY:
        box = soup.new_tag('aside', attrs={'class': 'keypoints', 'aria-label': 'Key points'})
        hh = soup.new_tag('p', attrs={'class': 'kp-title'})
        hh.string = 'Key points'
        box.append(hh)
        ul = soup.new_tag('ul')
        for k in KEY[sid]:
            li = soup.new_tag('li')
            li.string = k
            ul.append(li)
        box.append(ul)
        bar.insert_after(box)

body = str(art)
body = re.sub(r'\u0001([^\u0002]+)\u0002([^\u0003]+)\u0003', r'<a class="ltx_ref" href="#\2">\1</a>', body)
body = body.replace('<article', '<article id="doc"', 1)
body = re.sub(r'title="Appendix (S\d+)', r'title="\1', body)   # link tooltips name supplement sections as S1..S13

toc_html = []
for sid, title, supp in toc:
    toc_html.append(f'<li class="{"supp" if supp else "main"}"><a href="#{sid}" data-toc="{sid}">{H.escape(title)}</a></li>')
first_supp = next(i for i, (_, _, s) in enumerate(toc) if s)
toc_html.insert(first_supp, '<li class="toc-head">Supplementary Appendix</li>')
toc_html.insert(0, '<li class="toc-head">Main paper</li>')

tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web_reader_template.html'), encoding='utf-8').read()
page = tpl.replace('<!--TOC-->', '\n'.join(toc_html)).replace('<!--BODY-->', body)
open(OUT, 'w', encoding='utf-8').write(page)
print(f'wrote {OUT}: {len(page) / 1e6:.2f} MB, {len(toc)} sections, '
      f'{body.count("eqbox")} display equations, {body.count("tablebox")} tables, {body.count("<img")} figures')
