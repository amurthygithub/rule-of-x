#!/usr/bin/env python3
"""Shareable copies of the business dashboard "Rule of 40 and AI: business guide" (4 November 2026).

Writes to notes/mc_results_2026-11-03_1m/dashboard/export/:
  rule40_ai_business_guide.html  one self-contained file: the published page, its data files inlined, d3 inlined and a
                                 small local stand-in for the dashboard runtime, so every chart, button, tooltip and the
                                 calculator work offline in any current browser, in light and dark themes;
  rule40_ai_business_guide.pdf   the same page printed (US Letter) with every toggle state drawn as its own labelled
                                 chart, section links and PDF bookmarks (code/biz_dashboard_export_pdf.js, Playwright).

Inputs are the committed dashboard files only (index.html and the CSV files next to it); nothing is recomputed, so the
numbers are those of the live dashboard on the day of export.
Run:  python3 code/biz_dashboard_export.py          (HTML and PDF)
      python3 code/biz_dashboard_export.py --html   (HTML only)
"""
import csv
import datetime
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASH = os.path.join(BASE, 'notes', 'mc_results_2026-11-03_1m', 'dashboard')
OUT = os.path.join(DASH, 'export')
NAME = 'rule40_ai_business_guide'
D3_CANDIDATES = [os.environ.get('D3_JS', ''), os.path.join(BASE, 'code', 'vendor', 'd3.v7.9.0.min.js'),
                 '/opt/npm-tools/node_modules/d3/dist/d3.min.js']
EXPORT_DATE = os.environ.get('EXPORT_DATE', datetime.date.today().strftime('%-d %B %Y'))

page = open(os.path.join(DASH, 'index.html'), encoding='utf-8').read()
ids = sorted({w for v in __import__('re').findall(r'data-source="([a-z_ ]+)"', page) for w in v.split()})
data = {}
for i in ids:
    with open(os.path.join(DASH, i + '.csv'), encoding='utf-8', newline='') as fh:
        data[i] = list(csv.DictReader(fh))
d3 = next((open(p, encoding='utf-8').read() for p in D3_CANDIDATES if p and os.path.exists(p)), None)
assert d3 and 'v7.' in d3[:80], 'd3 v7 not found: set D3_JS to a copy of d3.min.js (v7)'

# design tokens of the dashboard runtime, light and dark (the page refers to these by name)
TOK_LIGHT = """
  --color-bg: #ffffff; --color-panel: #faf9f7; --color-fg: #1f1e1d; --color-fg-muted: #6b6a66; --color-border-line: #e3e1dc;
  --color-ok: #2f7d4f; --color-warn: #a3591a; --color-bad: #b42318;
  --cds-text-secondary: #6b6a66; --cds-surface-popover: #ffffff; --cds-border: #e3e1dc; --cds-shadow-popover: 0 4px 16px rgba(0,0,0,.12);
  --cds-chart-axis: #b5b2aa; --cds-chart-grid: #eceae5; --cds-chart-reference: #8a877f; --cds-chart-muted: #c9c6bf;
  --cds-chart-status-critical: #b42318;"""
TOK_DARK = """
  --color-bg: #1c1b1a; --color-panel: #242321; --color-fg: #ecebe7; --color-fg-muted: #a3a09a; --color-border-line: #3a3936;
  --color-ok: #6cc28f; --color-warn: #e3a157; --color-bad: #f07a6e;
  --cds-text-secondary: #a3a09a; --cds-surface-popover: #2a2927; --cds-border: #3a3936; --cds-shadow-popover: 0 4px 16px rgba(0,0,0,.5);
  --cds-chart-axis: #5f5d58; --cds-chart-grid: #33322f; --cds-chart-reference: #8f8c85; --cds-chart-muted: #5a5853;
  --cds-chart-status-critical: #f07a6e;"""
TOK_FIXED = """
  --font-anthropic-sans: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  --font-anthropic-serif: Charter, "Bitstream Charter", Georgia, "Times New Roman", serif;
  --cds-font-size-caption: 12px; --cds-font-size-body: 14px; --cds-font-size-heading: 17px; --cds-font-size-title: 28px;
  --cds-font-weight-medium: 500;
  --cds-gap-xs: 4px; --cds-gap-sm: 8px; --cds-gap-md: 12px; --cds-gap-lg: 16px; --cds-gap-xl: 28px;
  --cds-pad-xs: 4px; --cds-pad-sm: 8px; --cds-pad-md: 12px; --cds-pad-lg: 16px;
  --cds-radius: 8px; --cds-dur-slow: 300ms; --cds-ease-out: cubic-bezier(.2,.8,.2,1);"""
COLORS_LIGHT = ['#2c6bd6', '#d9822b', '#3a9d6e', '#9b59c9']
COLORS_DARK = ['#5b93f0', '#eea25a', '#5cc292', '#bb86e8']

CSS = f"""
:root {{ color-scheme: light dark; {TOK_FIXED} {TOK_LIGHT} }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ {TOK_DARK} }} }}
:root[data-theme="dark"] {{ {TOK_DARK} }}
html, body {{ background: var(--color-bg); color: var(--color-fg); }}
body {{ margin: 0; padding: 24px 16px 48px; font-family: var(--font-anthropic-sans); -webkit-text-size-adjust: 100%; }}
.dash-skeleton {{ min-height: 6rem; border-radius: var(--cds-radius); background: var(--color-panel); }}
.xp-banner {{ max-width: 72rem; margin: 0 auto 20px; font-size: 12px; line-height: 1.5; color: var(--color-fg-muted);
  border: 1px solid var(--color-border-line); border-radius: var(--cds-radius); padding: 8px 12px; }}
.xp-banner b {{ color: var(--color-fg); font-weight: 500; }}
.xp-state {{ font-size: var(--cds-font-size-caption); font-weight: 500; color: var(--color-fg); margin: 8px 0 2px; }}
.xp-print-note, .xp-only-print {{ display: none; }}
html.xp-print .xp-only-print {{ display: inline; }}
html.xp-print .xp-only-html {{ display: none; }}
html.xp-print .xp-print-note {{ display: block; font-size: var(--cds-font-size-caption); color: var(--color-fg-muted); margin: 0; }}
@media print {{
  @page {{ size: Letter; margin: 0.5in 0.5in 0.55in; }}
  html, body {{ background: #fff; }}
  body {{ padding: 0; }}
  svg, .xp-fig, .st-step, tr, .st-tile, .st-qa {{ break-inside: avoid; }}
  h2, h3, .xp-state {{ break-after: avoid; }}
  .st-tt, #st-claim-search {{ display: none !important; }}
  .st-tablebox {{ max-height: none !important; overflow: visible !important; }}
  .st-table th {{ position: static !important; white-space: normal !important; }}
  .st-table {{ font-size: 10px !important; }}
  .st-table td.st-wide {{ min-width: 0 !important; }}
  .st-gloss div, .xp-keep {{ break-inside: avoid; }}
  a {{ color: inherit; }}
}}
"""

SHIM = """
(function () {
  const DATA = __DATA__;
  const LIGHT = __LIGHT__, DARK = __DARK__;
  const PRINT = !!window.__XP_PRINT__;
  if (PRINT) document.documentElement.classList.add('xp-print');   // before the page draws, so charts are sized for paper
  const mq = window.matchMedia ? matchMedia('(prefers-color-scheme: dark)') : { matches: false, addEventListener() {} };
  const isDark = () => !PRINT && (document.documentElement.dataset.theme === 'dark' || (mq.matches && document.documentElement.dataset.theme !== 'light'));
  const reg = {}, order = [], subs = [];
  const dash = {
    colors: (isDark() ? DARK : LIGHT).slice(),
    data: (id) => (DATA[id] ? { status: 'ok', data: DATA[id] } : { status: 'missing' }),
    draw(name, fn) {
      if (fn) { if (!reg[name]) order.push(name); reg[name] = fn; }
      const f = reg[name]; if (!f) return;
      document.querySelectorAll('[data-draw="' + name + '"]').forEach((el) => { try { f(el); } catch (e) { console.error(name, e); } });
    },
    onData(cb) { subs.push(cb); setTimeout(cb, 0); },
    setLink(id) { try { history.replaceState(null, '', '#' + id); } catch (e) { /* file: URLs in some browsers */ } },
  };
  window.dash = dash;
  const redrawAll = () => order.forEach((n) => { if (n !== 'calc_preset') dash.draw(n); });
  const retheme = () => { dash.colors = (isDark() ? DARK : LIGHT).slice(); redrawAll(); subs.forEach((cb) => cb()); };
  try { mq.addEventListener('change', retheme); } catch (e) { /* old browsers */ }
  let w = window.innerWidth, t = 0;
  window.addEventListener('resize', () => { if (Math.abs(window.innerWidth - w) < 8) return; w = window.innerWidth; clearTimeout(t); t = setTimeout(redrawAll, 150); });
  window.__xpRedrawAll = redrawAll;
})();
"""

# print mode: every toggle state as its own labelled chart; section buttons become links
PRINT_JS = """
(function () {
  if (!window.__XP_PRINT__) return;
  document.documentElement.classList.add('xp-print');
  const groups = [
    { sel: '.st-basis', btn: 'button[data-basis]', targets: ['#levers-chart', '[data-draw="lever_heat"]'] },
    { sel: '.st-vbasis', btn: 'button[data-vbasis]', targets: ['[data-draw="val_deciles"]'] },
    { sel: '.st-scen', btn: 'button[data-scen]', targets: ['[data-draw="paths_chart"]'] },
  ];
  groups.forEach((g) => {
    const grp = document.querySelector(g.sel); if (!grp) return;
    const btns = Array.from(grp.querySelectorAll(g.btn));
    const shots = g.targets.map(() => []);
    btns.forEach((b) => {
      b.click();
      g.targets.forEach((ts, i) => { const el = document.querySelector(ts); if (el) shots[i].push({ label: b.textContent.trim(), html: el.innerHTML }); });
    });
    g.targets.forEach((ts, i) => {
      const el = document.querySelector(ts); if (!el) return;
      const box = document.createElement('div'); box.className = 'xp-figs';
      shots[i].forEach((s) => {
        const f = document.createElement('div'); f.className = 'xp-fig';
        const h = document.createElement('div'); h.className = 'xp-state'; h.textContent = s.label;
        const c = document.createElement('div'); c.className = el.className.replace('dash-skeleton', ''); c.innerHTML = s.html;
        c.querySelectorAll('.st-tt').forEach((n) => n.remove());
        f.append(h, c); box.appendChild(f);
      });
      el.replaceWith(box);
    });
    const note = document.createElement('p'); note.className = 'xp-print-note';
    note.textContent = 'Each option is drawn below in turn.';
    grp.replaceWith(note);
  });
  // section buttons become links the PDF keeps
  document.querySelectorAll('.st-nav button[data-go]').forEach((b) => {
    const a = document.createElement('a'); a.href = '#' + b.dataset.go; a.className = b.className; a.textContent = b.textContent;
    a.style.textDecoration = 'none'; b.replaceWith(a);
  });
  // the claim filter and table sorting do nothing on paper
  document.querySelectorAll('.st-table th button[data-sort]').forEach((b) => { const s = document.createElement('span'); s.textContent = b.textContent; b.replaceWith(s); });
  document.querySelectorAll('.st-role').forEach((r) => r.remove());
  // keep cards of up to two thirds of a page on one page; longer ones break where they must
  document.querySelectorAll('.st-card').forEach((c) => { if (c.getBoundingClientRect().height < 620) c.classList.add('xp-keep'); });
  window.__XP_DONE__ = true;
})();
"""


def build_html():
    banner = (f'<div class="xp-banner"><b>Rule of 40 and AI: business guide.</b> Shareable copy exported on {EXPORT_DATE} from '
              'the live dashboard; the numbers are fixed as of that day. Material marked "New analysis, not in the paper" is not '
              'part of Paper 1. <span class="xp-only-html">Every chart, button, tooltip and the calculator work in this file without a '
              'connection.</span><span class="xp-only-print">In this PDF each option of a button group is drawn in turn; the '
              'calculator shows its first preset. For tooltips and your own numbers, open the HTML copy.</span></div>')
    shim = (SHIM.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
            .replace('__LIGHT__', json.dumps(COLORS_LIGHT)).replace('__DARK__', json.dumps(COLORS_DARK)))
    body = page.replace('<meta name="dash-one-writer">', '')
    # the page's own script runs first; the print step must run after it
    html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<title>Rule of 40 and AI: business guide</title>\n'
            '<meta name="description" content="Plain-language guide to Paper 1, The Rule of 40 as a Price Line, and its stress test.">\n'
            f'<style>{CSS}</style>\n<script>{d3}</script>\n<script>{shim}</script>\n</head>\n<body>\n{banner}\n{body}\n'
            f'<script>{PRINT_JS}</script>\n</body>\n</html>\n')
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, NAME + '.html')
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(html)
    print(f'wrote {os.path.relpath(path, BASE)}: {len(html.encode()):,} bytes, {len(data)} datasets inlined')
    return path


def fix_bookmarks(pdf):
    """Chromium drops the space at each line break of a wrapped heading from its bookmark; restore the heading text."""
    import pypdf
    from pypdf.generic import NameObject, TextStringObject
    hj = pdf + '.headings.json'
    heads = {''.join(t.split()): t for t in json.load(open(hj, encoding='utf-8'))}
    os.remove(hj)
    w = pypdf.PdfWriter(clone_from=pdf)
    fixed = 0
    node = w._root_object['/Outlines'].get_object().get('/First') if '/Outlines' in w._root_object else None
    stack = [node] if node is not None else []
    while stack:
        it = stack.pop().get_object()
        t = str(it.get('/Title', ''))
        full = heads.get(''.join(t.split()))
        if full and full != t:
            it[NameObject('/Title')] = TextStringObject(full); fixed += 1
        if '/First' in it: stack.append(it['/First'])
        if '/Next' in it: stack.append(it['/Next'])
    w.add_metadata({'/Title': 'Rule of 40 and AI: business guide', '/Subject': 'Plain-language guide to Paper 1 and its stress test'})
    with open(pdf, 'wb') as fh:
        w.write(fh)
    print(f'bookmarks: {fixed} titles restored')


if __name__ == '__main__':
    h = build_html()
    if '--html' not in sys.argv:
        pdf = os.path.join(OUT, NAME + '.pdf')
        subprocess.run(['node', os.path.join(BASE, 'code', 'biz_dashboard_export_pdf.js'), h, pdf], check=True)
        fix_bookmarks(pdf)
