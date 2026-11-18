# Accessible editions of Paper 1

These scripts build other editions of the paper and its Supplementary Appendix from the LaTeX sources at `HEAD`. Each
works on a scratch copy and never writes into the repository; the text, numbers, tables and equations are the same as
in the standard build.

| Edition | Script | What it gives |
|---|---|---|
| Easy-read web edition | `make_web_source.py`, then `build_web_reader.py` | One self-contained HTML page: reading settings (typeface, size, line spacing, line length, letter spacing, background), read-aloud by section through the browser's speech engine, a key-points box under every section title, a skim mode, foldable equations, a table of contents, figure descriptions, and equations as MathML. Also the edition for screen readers. |
| Dyslexia-friendly PDF | `make_accessible_pdfs.py <scratch> dyslexia` | 12 pt sans-serif, line spacing 1.5, ragged right, no hyphenation, space between paragraphs, about 70 characters a line, wider letter spacing, emphasis in bold, a cream page; document language and a Unicode map for read-aloud tools. |
| Tagged PDF | `make_accessible_pdfs.py <scratch> tagged` | Experimental: does not complete on TeX Live 2023 (see the script's docstring). |

```
python3 code/accessible/make_web_source.py <scratch>
python3 code/accessible/build_web_reader.py <scratch>/out/paper.html <scratch>/out/figures <out.html>
python3 code/accessible/make_accessible_pdfs.py <scratch> dyslexia
```

Requirements: LaTeXML 0.8.8 (Debian package `latexml`), poppler-utils, BeautifulSoup 4 with lxml, and the TeX Live of
`code/build_paper1.sh` (the dyslexia edition also uses helvet, mathastext, ragged2e, microtype and adjustbox).

The key points and figure descriptions in `build_web_reader.py` are the only words these editions add to the paper.
In the dyslexia edition, tables wider than the line may use part of the side margins; eleven tall tables are scaled to
fit a page (to between 74% and 100%), so the web edition, where tables keep their size and scroll, reads them more easily.
