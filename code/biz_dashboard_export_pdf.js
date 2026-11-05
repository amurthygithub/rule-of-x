#!/usr/bin/env node
// Print the standalone dashboard file to a PDF (US Letter), with every toggle state drawn as its own chart, section links
// and bookmarks from the page's headings. Called by code/biz_dashboard_export.py:  node biz_dashboard_export_pdf.js IN.html OUT.pdf
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const [inp, out] = process.argv.slice(2);
  if (!inp || !out) { console.error('usage: node biz_dashboard_export_pdf.js IN.html OUT.pdf'); process.exit(2); }
  const browser = await chromium.launch();
  // 7.5 in of printable width at 96 px per inch, so charts are drawn at the size they print
  const page = await browser.newPage({ viewport: { width: 720, height: 1000 }, colorScheme: 'light' });
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.addInitScript(() => { window.__XP_PRINT__ = true; });
  await page.goto('file://' + path.resolve(inp));
  await page.waitForFunction(() => window.__XP_DONE__ === true, null, { timeout: 15000 });
  await page.waitForTimeout(300);
  const left = await page.evaluate(() => document.querySelectorAll('.dash-skeleton').length);
  if (left) errors.push(`${left} charts still empty`);
  if (errors.length) { console.error('page errors:\n  ' + errors.join('\n  ')); await browser.close(); process.exit(1); }
  // heading texts, so the caller can restore spaces Chromium drops from bookmarks at line breaks
  const heads = await page.evaluate(() => Array.from(document.querySelectorAll('h1, h2, h3, h4')).map((h) => h.textContent.replace(/\s+/g, ' ').trim()));
  require('fs').writeFileSync(out + '.headings.json', JSON.stringify(heads));
  await page.emulateMedia({ media: 'print', colorScheme: 'light' });
  await page.pdf({
    path: out, format: 'Letter', printBackground: true, preferCSSPageSize: true, outline: true, tagged: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;font-size:8px;color:#888;font-family:Inter,Arial,sans-serif;padding:0 0.5in;display:flex;justify-content:space-between"><span>Rule of 40 and AI: business guide</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
  });
  await browser.close();
  console.log('wrote ' + path.relative(process.cwd(), out));
})();
