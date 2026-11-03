"""Non-software industry priors (spec Section 24.10): industry_benchmarks.csv, xw_damodaran_naics.csv, and the
non-software rows of industry_function_shares.csv.

Inputs (untrusted downloads; run this script with `python3 -I`):
  data/raw/damodaran_2026/margin.xls, wacc.xls, roe.xls   Damodaran, US industry datasets, data dated 2026-01-05
  data/raw/damodaran_2026/roc_html.csv                     roc.html's table saved from the author's browser (percent
                                                           strings); unadjusted, lease and lease+R&D ROIC; roc.xls is
                                                           used instead if present (full precision)
  data/raw/damodaran_2026/mgnroc.xls                       OPTIONAL (Margin/ROIC by Sector, US); cross-check of k
  data/tasks/industry_staffing.csv, occupations.csv, function_occ.csv, functions.csv (OEWS May 2025, built earlier)
  data/raw/bls_oews_2025/oesm25in4.zip                     only for NAICS 5- and 6-digit titles (nat5d_6d file)
  data/panel_v2_all.csv                                    SEC XBRL panel (software sanity check; dispersion precedent)

Method (details and limits in notes/data_sources_nonsoftware.md):
1. Parse sheet 'Industry Averages' of each file. The header row is the first row whose first cell is 'Industry Name';
   every expected column is located by its normalised header text, so a renamed column stops the script.
   Checks: same industry names and firm counts in every file; SG&A/Sales equals (EBITDA+SG&A)/Sales minus
   EBITDA/Sales and R&D/Sales equals (EBITDA+R&D)/Sales minus EBITDA/Sales (the FAQ defines both as EBITDA with the
   item added back); cost of capital recomputed from its parts.
2. Invested capital per dollar of sales (Part I's k) = after-tax operating margin / after-tax ROC, on matching
   adjustments (both are EBIT(1-t) over sales or over invested capital, variable.htm). fundgrEB.xls gives one ROC,
   which matches the lease- and R&D-adjusted variant, so it is paired with the lease- and R&D-adjusted margin;
   the ROC table (roc_html.csv, or roc.xls) adds the unadjusted and lease-adjusted variants; the unadjusted one is the
   default, as in Part I, and the table re-establishes fundgrEB's basis on every run.
   Cross-check: reinvestment per dollar of sales = reinvestment rate x margin (same basis); with histgr.xls
   (optional), marginal capital per dollar of growth = that over the 5-year revenue CAGR.
3. Crosswalk CROSSWALK below: Damodaran's groups are his own classification, so each group is mapped by name and
   NAICS 2022 scope to (a) engine match prefixes and (b) OEWS industries for staffing. Precedent class (b).
4. Function shares: bucket shares of revenue from Damodaran (COGS, R&D, SG&A). Within a bucket, function f gets
   W_f / W_pool, where W_f = sum over SOC of OEWS May 2025 employment in the mapped NAICS x national mean wage x
   alloc(f, soc), alloc from function_occ.csv (the constructed FUNC_SOC table of 05_function_priors.py). Employment
   not allocated to any function (1 - sum of alloc) goes to a core function by SOC major group (RESIDUAL_RULE,
   assumed). Pools follow functions.csv cost_bucket: cogs, rnd, and sm + ga for SG&A. A pool whose Damodaran bucket
   is below 0.5% of sales (banks' COGS, R&D outside technology) is merged into the SG&A pool.
"""
import sys
sys.path.insert(0, '/home/claude/paper/code/data_part2')
import csv
import hashlib
import io
import os
import re
import zipfile

import numpy as np
import pandas as pd
import xlrd
from common import BASE, RAW, OUT, OEWS_DIR, norm, sha256, write_csv, save_meta, read_sec_panel

DAM = f'{RAW}/damodaran_2026'
REQUIRED = ['margin.xls', 'wacc.xls', 'roe.xls']
if not all(os.path.exists(f'{DAM}/{f}') for f in REQUIRED):
    print('Damodaran files missing in data/raw/damodaran_2026/: non-software priors not built')
    save_meta('nonsoftware_priors', dict(mode='missing', needed=REQUIRED))
    sys.exit(0)

# ---------------------------------------------------------------- column specs (normalised header -> output column)
MARGIN = {'numberoffirms': 'n_firms', 'grossmargin': 'gross_margin', 'netmargin': 'net_margin',
          'pretaxprestockcompensationoperatingmargin': 'op_margin_pretax_pre_sbc',
          'pretaxunadjustedoperatingmargin': 'op_margin_pretax', 'aftertaxunadjustedoperatingmargin': 'op_margin_aftertax',
          'pretaxleaseadjustedmargin': 'op_margin_pretax_lease', 'aftertaxleaseadjustedmargin': 'op_margin_aftertax_lease',
          'pretaxleaserdadjmargin': 'op_margin_pretax_lease_rnd', 'aftertaxleaserdadjmargin': 'op_margin_aftertax_lease_rnd',
          'ebitdasales': 'ebitda_sales', 'ebitdasgasales': 'ebitda_plus_sga_sales', 'ebitdardsales': 'ebitda_plus_rnd_sales',
          'cogssales': 'cogs_sales', 'rdsales': 'rnd_sales', 'sgasales': 'sga_sales',
          'stockbasedcompensationsales': 'sbc_sales', 'leaseexpensesales': 'lease_sales'}
WACC = {'numberoffirms': 'n_firms_wacc', 'beta': 'beta', 'costofequity': 'cost_of_equity', 'ede': 'e_over_de',
        'stddevinstock': 'sd_stock', 'costofdebt': 'cost_of_debt', 'taxrate': 'tax_rate_wacc_sheet',
        'aftertaxcostofdebt': 'after_tax_cost_of_debt', 'dde': 'd_over_de', 'costofcapital': 'cost_of_capital'}
ROE = {'numberoffirms': 'n_firms_roe', 'roeunadjusted': 'roe_unadj', 'roeadjustedforrd': 'roe_rnd_adj'}
# roc.xls headers as listed on roc.html (read 29 Oct 2026); matched exactly first, then by keywords (roc_columns)
ROC_OUT = {('pretax', 'unadj'): 'roic_pretax', ('pretax', 'lease'): 'roic_pretax_lease',
           ('pretax', 'leaserd'): 'roic_pretax_lease_rnd', ('aftertax', 'unadj'): 'roic_aftertax',
           ('aftertax', 'lease'): 'roic_aftertax_lease', ('aftertax', 'leaserd'): 'roic_aftertax_lease_rnd',
           ('normalized', ''): 'roic_normalized_10y'}
ROC_HTML_HEADERS = ['Industry Name', 'Number of firms', 'Unadjusted pre-tax ROIC', 'Lease Adjusted pre-tax ROIC',
                    'Lease & R&D adjusted pre-tax ROIC', 'Unadjusted after-tax ROIC', 'Lease Adjusted after-tax ROIC',
                    'Lease & R&D adjusted after-tax ROIC', 'Normalized ROIC (last 10 years)']
FUNDGR = {'numberoffirms': 'n_firms_fundgr', 'roc': 'roc_fundgr', 'reinvestmentrate': 'reinvestment_rate',
          'expectedgrowthinebit': 'expected_growth_ebit'}
HISTGR = {'numberoffirms': 'n_firms_histgr', 'cagrinrevenueslast5years': 'revenue_cagr_5y'}   # headers per histgr.html
MGNROC = {'numberoffirms': 'n_firms_mgnroc', 'aftertaxoperatingmargin': 'mgnroc_aftertax_margin',
          'salesinvestedcapitalltm': 'sales_to_ic_ltm', 'returnoncapital': 'mgnroc_roc'}


def read_book(path):
    """All cells of 'Industry Averages' and 'Variables & FAQ', plus the 'Date updated' cell as a date."""
    book = xlrd.open_workbook(path, on_demand=True)
    sh = book.sheet_by_name('Industry Averages')
    rows = [[sh.cell_value(r, c) for c in range(sh.ncols)] for r in range(sh.nrows)]
    date = None
    for r in rows[:6]:
        if norm(r[0]).startswith('dateupdated') and isinstance(r[1], float):
            date = xlrd.xldate_as_datetime(r[1], book.datemode).date().isoformat()
    faq = []
    if 'Variables & FAQ' in book.sheet_names():
        fs = book.sheet_by_name('Variables & FAQ')
        faq = [[str(fs.cell_value(r, c)).strip() for c in range(min(3, fs.ncols))] for r in range(fs.nrows)]
    return rows, date, faq


def header_index(rows):
    for i, r in enumerate(rows):
        if norm(r[0]) == 'industryname':
            return i
    raise ValueError('no header row starting with "Industry Name"')


def table(rows, colmap, name):
    """Data rows under the header, with columns located by normalised header text; excel_row is 1-based."""
    h = header_index(rows)
    hdr = [norm(x) for x in rows[h]]
    idx = {}
    for key, out in colmap.items():
        hits = [i for i, x in enumerate(hdr) if x == key]
        if len(hits) != 1:
            raise ValueError(f'{name}: header {key!r} found {len(hits)} times; headers are {rows[h]}')
        idx[out] = hits[0]
    recs = []
    for i in range(h + 1, len(rows)):
        nm = str(rows[i][0]).strip()
        if not nm:
            break
        rec = {'damodaran_industry': nm, f'excel_row_{name}': i + 1}
        for out, j in idx.items():
            v = rows[i][j]
            rec[out] = float(v) if isinstance(v, (int, float)) and v != '' else np.nan
        recs.append(rec)
    return pd.DataFrame(recs)


def roc_columns(header_cells):
    """Map roc.xls headers to output columns: exact roc.html names first, then keywords (pre-tax / after-tax;
    unadjusted / lease / lease and R&D; normalized). Raises if any expected column is missing or ambiguous."""
    out = {}
    for j, c in enumerate(header_cells):
        n = norm(c)
        if not any(k in n for k in ('roic', 'roc', 'returnoncapital')):
            continue
        if 'normali' in n:
            key = ('normalized', '')
        else:
            tax = 'aftertax' if 'aftertax' in n else 'pretax' if 'pretax' in n else None
            adj = 'leaserd' if ('lease' in n and 'rd' in n.replace('ord', '')) else 'lease' if 'lease' in n else \
                'unadj' if 'unadj' in n else None
            if tax is None or adj is None:
                continue
            key = (tax, adj)
        if key in ROC_OUT:
            if ROC_OUT[key] in out:
                raise ValueError(f'roc.xls: two columns map to {ROC_OUT[key]}: {header_cells}')
            out[ROC_OUT[key]] = j
    miss = [v for v in ROC_OUT.values() if v not in out]
    if miss:
        raise ValueError(f'roc.xls: columns not found {miss}; headers are {header_cells}')
    return out


# self-test of the roc.xls header mapping on the column names published on roc.html (no numbers involved)
_m = roc_columns(ROC_HTML_HEADERS)
assert _m == {'roic_pretax': 2, 'roic_pretax_lease': 3, 'roic_pretax_lease_rnd': 4, 'roic_aftertax': 5,
              'roic_aftertax_lease': 6, 'roic_aftertax_lease_rnd': 7, 'roic_normalized_10y': 8}, _m

books, dates, faqs, hashes = {}, {}, {}, {}
for f in ['margin', 'wacc', 'roe', 'fundgrEB', 'roc', 'mgnroc', 'histgr']:
    p = f'{DAM}/{f}.xls'
    if os.path.exists(p):
        books[f], dates[f], faqs[f] = read_book(p)
        hashes[f] = sha256(p)
assert len({dates['margin'], dates['wacc'], dates['roe']}) == 1, dates
DATA_DATE = dates['margin']

mg = table(books['margin'], MARGIN, 'margin')
wc = table(books['wacc'], WACC, 'wacc')
re_ = table(books['roe'], ROE, 'roe')
for other, col in [(wc, 'n_firms_wacc'), (re_, 'n_firms_roe')]:
    assert list(other.damodaran_industry) == list(mg.damodaran_industry), 'industry names differ across files'
    assert (other[col].values == mg.n_firms.values).all(), f'firm counts differ ({col})'
bm = mg.merge(wc, on='damodaran_industry').merge(re_, on='damodaran_industry')

# wacc.xls global inputs (cells beside their labels)
def labelled(rows, pattern, col=None):
    for i, r in enumerate(rows):
        if re.search(pattern, str(r[0]), re.I):
            vals = [(j, v) for j, v in enumerate(r[1:], 1) if isinstance(v, float)]
            if col is not None:
                vals = [(j, v) for j, v in vals if j == col]
            return (vals[0][1], i + 1, vals[0][0]) if vals else (np.nan, i + 1, None)
    return (np.nan, None, None)


W = books['wacc']
rf = labelled(W, r'^Long Term Treasury bond rate')
erp = labelled(W, r'^Risk Premium to Use for Equity')
gspread = labelled(W, r'^Global Default Spread')
mtax = labelled(W, r'^If yes, enter the marginal tax rate', col=5)
wacc_inputs = dict(riskfree=rf, equity_risk_premium=erp, global_default_spread=gspread, marginal_tax_rate=mtax)

# ---------------------------------------------------------------- checks and derived columns
bm['sga_sales_derived'] = bm.ebitda_plus_sga_sales - bm.ebitda_sales
bm['sga_identity_gap'] = bm.sga_sales_derived - bm.sga_sales
bm['rnd_identity_gap'] = (bm.ebitda_plus_rnd_sales - bm.ebitda_sales) - bm.rnd_sales
bm['gross_cogs_identity_gap'] = bm.gross_margin + bm.cogs_sales - 1
bm['da_sales_implied'] = bm.ebitda_sales - bm.op_margin_pretax
bm['other_opex_sales_residual'] = 1 - bm.cogs_sales - bm.sga_sales - bm.rnd_sales - bm.op_margin_pretax
bm['unbucketed_opex_sales'] = bm.other_opex_sales_residual - bm.da_sales_implied.clip(lower=0)
bm['sbc_identity_gap'] = (bm.op_margin_pretax_pre_sbc - bm.op_margin_pretax) - bm.sbc_sales
bm['tax_rate_implied'] = np.where(bm.op_margin_pretax.abs() > 1e-9, 1 - bm.op_margin_aftertax / bm.op_margin_pretax, np.nan)
coe_re = wacc_inputs['riskfree'][0] + bm.beta * wacc_inputs['equity_risk_premium'][0]
wacc_re = bm.cost_of_equity * bm.e_over_de + bm.after_tax_cost_of_debt * bm.d_over_de
atcod_re = bm.cost_of_debt * (1 - wacc_inputs['marginal_tax_rate'][0])
checks = dict(
    sga_identity_max_abs=float(bm.sga_identity_gap.abs().max()),
    rnd_identity_max_abs=float(bm.rnd_identity_gap.abs().max()),
    gross_cogs_identity_max_abs=float(bm.gross_cogs_identity_gap.abs().max()),
    sbc_identity_max_abs=float(bm.sbc_identity_gap.abs().max()),
    cost_of_equity_recompute_max_abs=float((coe_re - bm.cost_of_equity).abs().max()),
    wacc_recompute_max_abs=float((wacc_re - bm.cost_of_capital).abs().max()),
    after_tax_cost_of_debt_recompute_max_abs=float((atcod_re - bm.after_tax_cost_of_debt).abs().max()),
    e_plus_d_max_dev=float((bm.e_over_de + bm.d_over_de - 1).abs().max()),
    groups_ebitda_below_ebit=sorted(bm.loc[bm.da_sales_implied < -1e-4, 'damodaran_industry']),
    groups_negative_bucket=sorted(bm.loc[(bm[['cogs_sales', 'rnd_sales', 'sga_sales']] < 0).any(axis=1), 'damodaran_industry']),
    groups_zero_operating_margin=sorted(bm.loc[bm.op_margin_pretax.abs() < 1e-4, 'damodaran_industry']),
)
assert checks['sga_identity_max_abs'] < 1e-6 and checks['rnd_identity_max_abs'] < 1e-6, checks

FINANCIAL = ['Bank (Money Center)', 'Banks (Regional)', 'Brokerage & Investment Banking',
             'Financial Svcs. (Non-bank & Insurance)', 'Insurance (General)', 'Insurance (Life)', 'Insurance (Prop/Cas.)',
             'Investments & Asset Management', 'Reinsurance']
TOTALS = ['Total Market', 'Total Market (without financials)']
assert set(FINANCIAL) <= set(bm.damodaran_industry), set(FINANCIAL) - set(bm.damodaran_industry)
n_tot = bm.set_index('damodaran_industry').n_firms
checks['financial_groups_firms'] = int(n_tot[FINANCIAL].sum())
checks['total_minus_nonfinancial_firms'] = int(n_tot['Total Market'] - n_tot['Total Market (without financials)'])
checks['sum_of_industry_firms'] = int(n_tot.drop(TOTALS).sum())
bm['financial_group'] = bm.damodaran_industry.isin(FINANCIAL).astype(int)
bm['is_total'] = bm.damodaran_industry.isin(TOTALS).astype(int)
bm['small_sample'] = (bm.n_firms < 20).astype(int)
bm['data_date'] = DATA_DATE

# ---------------------------------------------------------------- invested capital per dollar of sales (Part I's k)
# fundgrEB.xls (supplied 29 Oct 2026): FAQ "ROC: Aggregated after-tax Operating Income, across all firms in group, using
# trailing 12 month data/ Aggregated Invested Capital, across all firms in group, using most recent balance sheet." Its
# values equal roc.html's "Lease & R&D adjusted after-tax ROIC" in every row compared (notes/data_sources_nonsoftware.md),
# not the unadjusted column, so its ROC is paired with the lease- and R&D-adjusted after-tax margin. When roc.xls is
# present the basis is re-established from the data (FUNDGR_BASIS is replaced by the closest roc.xls column).
FUNDGR_BASIS = 'lease_rnd'
MARGIN_FOR = {'unadj': 'op_margin_aftertax', 'lease': 'op_margin_aftertax_lease', 'lease_rnd': 'op_margin_aftertax_lease_rnd'}
ROIC_FOR = {'unadj': 'roic_aftertax', 'lease': 'roic_aftertax_lease', 'lease_rnd': 'roic_aftertax_lease_rnd'}
roc_status = 'neither roc.xls nor roc_html.csv on disk (optional): unadjusted and lease-adjusted ROIC and k are missing'
ROC_SRC = ''
ROC_HTML = f'{DAM}/roc_html.csv'


def pct(x):
    """'61.83%' -> 0.6183; '52' -> 52.0; 'NA' or '' -> NaN."""
    t = str(x).strip().replace(',', '')
    if t in ('', 'NA', 'N/A'):
        return np.nan
    return float(t[:-1]) / 100 if t.endswith('%') else float(t)


for c in list(ROC_OUT.values()) + ['excel_row_roc']:
    bm[c] = np.nan
if 'roc' in books:
    rows = books['roc']
    h = header_index(rows)
    cmap = roc_columns(rows[h])
    cmap = {'n_firms_roc': [i for i, x in enumerate(rows[h]) if norm(x) == 'numberoffirms'][0], **cmap}
    rc = table(rows, {norm(rows[h][j]): out for out, j in cmap.items()}, 'roc')
    assert list(rc.damodaran_industry) == list(mg.damodaran_industry), 'roc.xls industry names differ from margin.xls'
    assert (rc.n_firms_roc.values == mg.n_firms.values).all(), 'roc.xls firm counts differ'
    bm = bm.drop(columns=list(ROC_OUT.values()) + ['excel_row_roc']).merge(rc, on='damodaran_industry')
    roc_status = f'roc.xls present (data date {dates["roc"]}, sha256 {hashes["roc"]})'
    if dates['roc'] != DATA_DATE:
        roc_status += f'; WARNING: data date differs from margin.xls ({DATA_DATE})'
    ROC_SRC = 'roc.xls'
elif os.path.exists(ROC_HTML):
    # HTML table of roc.html saved by the author's browser (29 Oct 2026): percentage strings, 'NA' for financials
    with open(ROC_HTML, newline='', encoding='utf-8') as fh:
        rows = [r for r in csv.reader(fh)]
    hashes['roc_html'] = sha256(ROC_HTML)
    h = header_index(rows)
    cmap = roc_columns(rows[h])
    cmap = {'n_firms_roc': [i for i, x in enumerate(rows[h]) if norm(x) == 'numberoffirms'][0], **cmap}
    rows = rows[:h + 1] + [[r[0]] + [pct(x) for x in r[1:]] if r and r[0].strip() else [''] for r in rows[h + 1:]]
    rc = table(rows, {norm(rows[h][j]): out for out, j in cmap.items()}, 'roc')
    assert list(rc.damodaran_industry) == list(mg.damodaran_industry), 'roc_html.csv industry names differ from margin.xls'
    assert (rc.n_firms_roc.values == mg.n_firms.values).all(), 'roc_html.csv firm counts differ'
    bm = bm.drop(columns=list(ROC_OUT.values()) + ['excel_row_roc']).merge(rc, on='damodaran_industry')
    ROC_SRC = 'roc_html.csv'
    roc_status = ('roc_html.csv present: HTML table of roc.html (Return on Capital by Sector, US) saved from the author\'s '
                  f'browser, sha256 {hashes["roc_html"]}; the page says "Data used is as of January 2026" but its footer says '
                  '"Last updated January 2025"; values are rounded to 0.01 percentage points')

fg_status = 'fundgrEB.xls not on disk: k from fundgrEB and the reinvestment cross-check are missing'
for c in ['roc_fundgr', 'reinvestment_rate', 'expected_growth_ebit', 'excel_row_fundgr']:
    bm[c] = np.nan
bm['fundgr_suspect'] = 0
if 'fundgrEB' in books:
    fgt = table(books['fundgrEB'], FUNDGR, 'fundgr')
    assert list(fgt.damodaran_industry) == list(mg.damodaran_industry), 'fundgrEB.xls industry names differ from margin.xls'
    assert (fgt.n_firms_fundgr.values == mg.n_firms.values).all(), 'fundgrEB.xls firm counts differ'
    bm = bm.drop(columns=['roc_fundgr', 'reinvestment_rate', 'expected_growth_ebit', 'excel_row_fundgr']).merge(
        fgt.drop(columns=['n_firms_fundgr']), on='damodaran_industry')
    fg_status = f'fundgrEB.xls present (data date {dates["fundgrEB"]}, sha256 {hashes["fundgrEB"]})'
    checks['fundgr_growth_identity_max_abs'] = float((bm.expected_growth_ebit - bm.roc_fundgr * bm.reinvestment_rate).abs().max())
    # a group whose ROC equals another row's to all digits is treated as a source error (see notes: Utility (Water))
    dup = bm[bm.roc_fundgr.notna() & bm.roc_fundgr.duplicated(keep=False)]
    checks['fundgr_roc_identical_rows'] = dup[['damodaran_industry', 'roc_fundgr']].values.tolist()
    bm['fundgr_suspect'] = (bm.damodaran_industry.isin(dup.damodaran_industry) & ~bm.damodaran_industry.isin(TOTALS)).astype(int)
    checks['fundgr_rows_na'] = sorted(bm.loc[bm.roc_fundgr.isna(), 'damodaran_industry'])
    if ROC_SRC:                                        # establish the basis of fundgrEB's ROC from the ROC table
        ok_ = bm.fundgr_suspect == 0
        dev = {b: float((bm.roc_fundgr - bm[c])[ok_].abs().max()) for b, c in ROIC_FOR.items()}
        checks['fundgr_roc_vs_roc_table_max_abs'] = dev
        checks['fundgr_roc_vs_roc_table_n_rows'] = int((ok_ & bm.roc_fundgr.notna() & bm.roic_aftertax_lease_rnd.notna()).sum())
        checks['fundgr_suspect_rows_vs_roc_table'] = {
            r_.damodaran_industry: dict(fundgr=r_.roc_fundgr, unadj=r_.roic_aftertax, lease=r_.roic_aftertax_lease,
                                        lease_rnd=r_.roic_aftertax_lease_rnd) for r_ in bm[bm.fundgr_suspect == 1].itertuples()}
        best = min(dev, key=dev.get)
        if dev[best] < 1e-4:                           # the table is rounded to 0.01 points, i.e. at most 5e-5
            FUNDGR_BASIS = best
        else:
            fg_status += f'; WARNING: fundgrEB ROC matches no {ROC_SRC} after-tax column'
checks['fundgr_basis'] = FUNDGR_BASIS


def k_ratio(margin, roic):
    """Invested capital per dollar of sales = EBIT(1-t)/Sales over EBIT(1-t)/IC; undefined for |ROIC| < 0.02 or
    opposite signs (negative invested capital)."""
    with np.errstate(divide='ignore', invalid='ignore'):
        k = margin / roic
    bad = (roic.abs() < 0.02) | (np.sign(margin) != np.sign(roic)) | roic.isna() | margin.isna()
    return k.where(~bad)


nonfin = bm.financial_group == 0
bm['k_ic_per_sales_unadj'] = k_ratio(bm.op_margin_aftertax, bm.roic_aftertax).where(nonfin)
bm['k_ic_per_sales_lease'] = k_ratio(bm.op_margin_aftertax_lease, bm.roic_aftertax_lease).where(nonfin)
bm['k_ic_per_sales_fundgr'] = k_ratio(bm[MARGIN_FOR[FUNDGR_BASIS]], bm.roc_fundgr).where(nonfin & (bm.fundgr_suspect == 0))
bm['k_ic_per_sales_lease_rnd'] = k_ratio(bm.op_margin_aftertax_lease_rnd, bm.roic_aftertax_lease_rnd).where(nonfin)
if FUNDGR_BASIS == 'lease_rnd':
    bm['k_ic_per_sales_lease_rnd'] = bm.k_ic_per_sales_lease_rnd.fillna(bm.k_ic_per_sales_fundgr)
# default k: unadjusted (R&D expensed, as in Part I's margin) when the ROC table gives it; else the best available variant
bm['k_ic_per_sales'], bm['k_variant'] = np.nan, ''
for v, c in [('unadj', 'k_ic_per_sales_unadj'), ('lease', 'k_ic_per_sales_lease'), ('lease_rnd', 'k_ic_per_sales_lease_rnd')]:
    take = bm.k_ic_per_sales.isna() & bm[c].notna()
    bm.loc[take, 'k_ic_per_sales'] = bm.loc[take, c]
    bm.loc[take, 'k_variant'] = v
bm['roic_basis'] = np.where(bm.roic_aftertax.notna(), f'unadj ({ROC_SRC})', np.where(bm.roc_fundgr.notna(), f'{FUNDGR_BASIS} (fundgrEB.xls)', ''))
bm['roic_minus_wacc'] = bm.roic_aftertax.fillna(bm.roc_fundgr.where(bm.fundgr_suspect == 0)) - bm.cost_of_capital
bm['k_flag'] = np.where(bm.financial_group == 1, 'financial: invested capital not meaningful',
               np.where(bm.fundgr_suspect.astype(bool) & bm.roic_aftertax.isna(), 'fundgrEB ROC duplicates another row (source error suspected)',
               np.where(bm.roic_aftertax.isna() & bm.roc_fundgr.isna(), 'no ROC on disk',
               np.where(bm.k_ic_per_sales.isna(), 'undefined (ROC near zero, negative or sign mismatch)',
               np.where(bm.k_variant == 'lease_rnd', 'ok, lease and R&D adjusted only (includes capitalized R&D and lease debt)', 'ok')))))
# reinvestment cross-check: reinvestment per dollar of sales, on the same basis as the ROC
bm['reinvestment_sales'] = (bm.reinvestment_rate * bm[MARGIN_FOR[FUNDGR_BASIS]]).where(bm.fundgr_suspect == 0)
bm['reinvestment_flag'] = np.where(bm.reinvestment_rate.isna(), 'missing',
                          np.where(bm.reinvestment_rate < 0, 'negative net reinvestment',
                          np.where(bm.reinvestment_rate > 1, 'reinvestment exceeds after-tax operating income', 'ok')))
bm['revenue_cagr_5y'] = np.nan
hg_status = 'histgr.xls not on disk (optional): marginal capital per dollar of growth not computed'
if 'histgr' in books:
    hgt = table(books['histgr'], HISTGR, 'histgr')
    assert list(hgt.damodaran_industry) == list(mg.damodaran_industry), 'histgr.xls industry names differ'
    bm = bm.drop(columns=['revenue_cagr_5y']).merge(hgt[['damodaran_industry', 'revenue_cagr_5y', 'excel_row_histgr']],
                                                    on='damodaran_industry')
    hg_status = f'histgr.xls present (sha256 {hashes["histgr"]})'
okg = (bm.revenue_cagr_5y > 0.01) & (bm.reinvestment_sales > 0) & nonfin
bm['k_marginal_implied'] = (bm.reinvestment_sales / bm.revenue_cagr_5y).where(okg)
bm['sales_to_ic_ltm'] = np.nan
bm['k_ic_per_sales_mgnroc'] = np.nan
mgn_status = 'mgnroc.xls not on disk (optional cross-check)'
if 'mgnroc' in books:
    mr = table(books['mgnroc'], MGNROC, 'mgnroc')
    assert list(mr.damodaran_industry) == list(mg.damodaran_industry), 'mgnroc.xls industry names differ'
    bm = bm.drop(columns=['sales_to_ic_ltm']).merge(mr[['damodaran_industry', 'sales_to_ic_ltm', 'excel_row_mgnroc']],
                                                   on='damodaran_industry')
    bm['k_ic_per_sales_mgnroc'] = 1 / bm.sales_to_ic_ltm.where(bm.sales_to_ic_ltm > 0)
    mgn_status = f'mgnroc.xls present (sha256 {hashes["mgnroc"]})'
    if bm.k_ic_per_sales_lease.notna().any():
        checks['k_lease_vs_mgnroc_max_rel_dev'] = float(
            ((bm.k_ic_per_sales_lease - bm.k_ic_per_sales_mgnroc) / bm.k_ic_per_sales_mgnroc).abs().max())

bm['source_rows'] = [f'margin.xls row {a}; wacc.xls row {b}; roe.xls row {c}' + (f'; fundgrEB.xls row {int(e)}' if pd.notna(e) else '')
                     + (f'; {ROC_SRC} {"row" if ROC_SRC.endswith("xls") else "line"} {int(d)}' if pd.notna(d) else '')
                     for a, b, c, d, e in zip(bm.excel_row_margin, bm.excel_row_wacc, bm.excel_row_roe, bm.excel_row_roc,
                                              bm.excel_row_fundgr)]
BM_COLS = ['damodaran_industry', 'n_firms', 'small_sample', 'financial_group', 'is_total', 'data_date',
           'gross_margin', 'net_margin', 'op_margin_pretax_pre_sbc', 'op_margin_pretax', 'op_margin_aftertax',
           'op_margin_pretax_lease', 'op_margin_aftertax_lease', 'op_margin_pretax_lease_rnd', 'op_margin_aftertax_lease_rnd',
           'ebitda_sales', 'ebitda_plus_sga_sales', 'ebitda_plus_rnd_sales', 'cogs_sales', 'rnd_sales', 'sga_sales',
           'sbc_sales', 'lease_sales', 'sga_sales_derived', 'sga_identity_gap', 'rnd_identity_gap', 'da_sales_implied',
           'other_opex_sales_residual', 'unbucketed_opex_sales', 'tax_rate_implied', 'beta', 'cost_of_equity', 'e_over_de', 'sd_stock',
           'cost_of_debt', 'tax_rate_wacc_sheet', 'after_tax_cost_of_debt', 'd_over_de', 'cost_of_capital',
           'roe_unadj', 'roe_rnd_adj'] + list(ROC_OUT.values()) + \
          ['roc_fundgr', 'reinvestment_rate', 'expected_growth_ebit', 'fundgr_suspect', 'roic_basis',
           'k_ic_per_sales', 'k_variant', 'k_ic_per_sales_unadj', 'k_ic_per_sales_lease', 'k_ic_per_sales_lease_rnd',
           'k_ic_per_sales_fundgr', 'k_flag', 'roic_minus_wacc', 'reinvestment_sales', 'reinvestment_flag', 'revenue_cagr_5y',
           'k_marginal_implied', 'sales_to_ic_ltm', 'k_ic_per_sales_mgnroc', 'source_rows']
write_csv(bm[BM_COLS], 'industry_benchmarks.csv')

# ---------------------------------------------------------------- crosswalk (precedent class b; method in the notes)
# name: (engine match prefixes, OEWS staffing codes, confidence, match type, note). Empty match = not emitted.
CROSSWALK = {
    'Advertising': (['5418'], ['5418'], 'high', 'one_to_one', ''),
    'Aerospace/Defense': (['3364', '336992', '334511'], ['3364'], 'medium', 'many_to_one',
                          'defense vehicles (336992) and search/navigation instruments (334511) added; staffing from aerospace only'),
    'Air Transport': (['481'], ['481'], 'high', 'one_to_one', ''),
    'Apparel': (['315', '3169'], ['315'], 'medium', 'subset',
                'listed apparel firms are mostly brand owners that outsource production; US apparel-manufacturing staffing may not represent them'),
    'Auto & Truck': (['3361', '3362'], ['3361', '3362'], 'high', 'one_to_one', ''),
    'Auto Parts': (['3363'], ['3363'], 'high', 'one_to_one', ''),
    'Bank (Money Center)': ([], ['5220A1'], 'low', 'by_size',
                            'NAICS does not separate money-center from regional banks; a bank firm is matched to Banks (Regional)'),
    'Banks (Regional)': (['5221'], ['5220A1'], 'medium', 'one_to_one',
                         'OEWS staffing is the BLS aggregate of 5221 and 5223 (activities related to credit intermediation)'),
    'Beverage (Alcoholic)': (['31212', '31213', '31214'], ['3121'], 'medium', 'subset', 'staffing from all beverage manufacturing'),
    'Beverage (Soft)': (['31211'], ['3121'], 'medium', 'subset', 'staffing from all beverage manufacturing'),
    'Broadcasting': (['5161'], ['5161'], 'high', 'one_to_one', ''),
    'Brokerage & Investment Banking': (['5231'], ['5230'], 'medium', 'subset', 'staffing from all of NAICS 523'),
    'Building Materials': (['327', '3219'], ['3270', '3219'], 'low', 'many_to_one',
                           'group scope (building products) not verifiable without the firm list; cement and concrete (3273) assigned to Construction Supplies'),
    'Business & Consumer Services': (['561', '812'], ['561', '812'], 'low', 'many_to_one',
                                     'heterogeneous group; NAICS 561 administrative and support plus 812 personal services is a judgment'),
    'Cable TV': ([], ['5170'], 'low', 'shared_code',
                 'cable operators are wired telecommunications carriers (517111), the same code as Telecom. Services'),
    'Chemical (Basic)': (['3251', '3252', '3253'], ['3250A1'], 'medium', 'many_to_one',
                         'OEWS aggregate 3250A1 also contains 3259 (other chemical products)'),
    'Chemical (Diversified)': (['325'], ['325'], 'low', 'conglomerate',
                               'reached only by a 3-digit NAICS input, since every 4-digit chemical code is assigned to another group'),
    'Chemical (Specialty)': (['3255', '3259'], ['3250A1', '3250A2'], 'medium', 'many_to_one',
                             'staffing pools both chemical aggregates (all of 325 except pharmaceuticals)'),
    'Coal & Related Energy': (['2121'], ['2121'], 'high', 'one_to_one', ''),
    'Computer Services': ([], ['5415'], 'high', 'overlaps_software',
                          'NAICS 5415 is covered by the SEC XBRL panel rows (SIC 7371 and 7373)'),
    'Computers/Peripherals': (['3341'], ['3341'], 'high', 'one_to_one', ''),
    'Construction Supplies': (['2123', '3273'], ['2123', '3270'], 'low', 'many_to_one',
                              'aggregates quarrying and cement/concrete; staffing for 3273 from all of 327'),
    'Diversified': ([], [], 'low', 'conglomerate', 'conglomerates have no NAICS counterpart'),
    'Drugs (Biotechnology)': (['325414', '541714'], ['3254', '5417'], 'medium', 'many_to_one',
                              'biological products and biotechnology R&D; staffing pools pharmaceutical manufacturing and all scientific R&D services'),
    'Drugs (Pharmaceutical)': (['3254'], ['3254'], 'high', 'one_to_one', 'in-vitro diagnostics (325413) and biologics (325414) go to other groups'),
    'Education': (['611'], ['6113', '6114', '6115', '6116', '6117'], 'medium', 'subset',
                  'listed education firms are private post-secondary and training providers; staffing excludes K-12 and junior colleges, but the engine prefix 611 matches them'),
    'Electrical Equipment': (['335'], ['335'], 'high', 'one_to_one', 'household appliances (3352) included'),
    'Electronics (Consumer & Office)': (['3343'], ['3343'], 'low', 'subset', 'eight firms; scope not verifiable without the firm list'),
    'Electronics (General)': (['3344', '3345', '3346'], ['3344', '3345', '3346'], 'medium', 'many_to_one',
                              'semiconductors (334413), electromedical (334510) and navigation instruments (334511) go to other groups'),
    'Engineering/Construction': (['237', '2362', '238', '5413'], ['237', '2362', '238', '5413'], 'medium', 'many_to_one',
                                 'listed E&C firms include engineering firms and large specialty and utility contractors; most NAICS 238 employment is in small private firms'),
    'Entertainment': (['512', '5162', '7111', '7112', '7113', '7114'], ['512', '5162', '7111', '7112', '7113', '7114'], 'medium',
                      'many_to_one', 'NAICS 5162 also contains social networks'),
    'Environmental & Waste Services': (['562'], ['562'], 'high', 'one_to_one', ''),
    'Farming/Agriculture': (['111', '112', '115'], ['115'], 'low', 'many_to_one',
                            'OEWS does not cover crop and animal production (111-112); staffing from support activities (115) only'),
    'Financial Svcs. (Non-bank & Insurance)': (['5222', '5223'], ['5222'], 'medium', 'many_to_one',
                                               'credit cards, consumer and mortgage lending, payments; staffing from nondepository credit only'),
    'Food Processing': (['311'], ['311'], 'high', 'one_to_one', ''),
    'Food Wholesalers': (['4244'], ['4240A1'], 'high', 'one_to_one', 'OEWS aggregate 4240A1 also contains 4248 (beer, wine and spirits wholesalers)'),
    'Furn/Home Furnishings': (['337', '3141'], ['337', '3141'], 'medium', 'many_to_one', ''),
    'Green & Renewable Energy': (['221114', '221115', '221116', '221117'], ['2211'], 'low', 'by_technology',
                                 'defined by technology; solar and wind equipment makers are in manufacturing codes and are not captured; staffing from all electric power'),
    'Healthcare Products': (['3391', '334510', '325413'], ['3391'], 'medium', 'many_to_one',
                            'medical devices, electromedical equipment and in-vitro diagnostics; staffing from 3391 only'),
    'Healthcare Support Services': (['524114', '4242'], ['5241', '4240A2'], 'low', 'inferred',
                                    'composition not verifiable without the firm list; the 12% gross margin points to managed care and drug distribution, so health insurers and drug wholesalers are mapped here; staffing from insurance carriers and the 4242/4246 wholesale aggregate'),
    'Heathcare Information and Technology': ([], [], 'low', 'overlaps_software',
                                             'healthcare software and IT firms carry software and IT NAICS codes (5132, 5415, 5182) already covered by the SEC panel rows'),
    'Homebuilding': (['2361'], ['2361'], 'high', 'one_to_one', ''),
    'Hospitals/Healthcare Facilities': (['622', '623', '621'], ['622', '623', '621'], 'medium', 'many_to_one',
                                        'hospitals and nursing facilities (high); ambulatory providers 621 (low: physician and dental practices are mostly private)'),
    'Hotel/Gaming': (['7211', '7132'], ['7211', '7132'], 'high', 'one_to_one', ''),
    'Household Products': (['3256', '322291'], ['3250A2', '3222'], 'medium', 'many_to_one',
                           'soaps, cleaners and toiletries plus sanitary paper; OEWS 3250A2 also contains paints (3255)'),
    'Information Services': (['519'], ['5192'], 'low', 'subset', 'NAICS 519 includes web search portals'),
    'Insurance (General)': (['5241', '5242'], ['5241', '5242'], 'medium', 'superset',
                            'catch-all for carriers not matched at 5-6 digits (including health insurers 524114, mapped to Healthcare Support Services) and for brokers'),
    'Insurance (Life)': (['524113'], ['5241'], 'medium', 'one_to_one', 'staffing from all insurance carriers'),
    'Insurance (Prop/Cas.)': (['52412'], ['5241'], 'medium', 'superset',
                              '52412 also contains title and other direct insurance; staffing from all insurance carriers'),
    'Investments & Asset Management': (['5239', '525'], ['5230', '525'], 'medium', 'many_to_one', 'staffing from all of NAICS 523 and 525'),
    'Machinery': (['333'], ['333'], 'high', 'one_to_one', 'office machinery (3333), semiconductor machinery (333242) and oilfield machinery (333132) go to other groups'),
    'Metals & Mining': (['2122', '3313', '3314', '3315'], ['2122', '3313', '3314', '3315'], 'medium', 'many_to_one',
                        'gold and silver mining (21222) goes to Precious Metals'),
    'Office Equipment & Services': (['3333'], ['3333'], 'low', 'subset', '14 firms; 3333 is commercial and service industry machinery'),
    'Oil/Gas (Integrated)': (['324'], ['2111', '324'], 'low', 'many_to_one',
                             'four firms; refiners may sit in this group or another, not verifiable without the firm list'),
    'Oil/Gas (Production and Exploration)': (['211'], ['2111'], 'high', 'one_to_one', ''),
    'Oil/Gas Distribution': (['486', '2212'], ['486', '2212'], 'medium', 'many_to_one', 'pipelines and gas distribution'),
    'Oilfield Svcs/Equip.': (['2131', '333132'], ['2131'], 'high', 'one_to_one', '2131 also contains support for non-oil mining'),
    'Packaging & Container': (['32221', '332431', '327213', '32616'], ['3222', '3261', '3320A2', '3270'], 'low', 'many_to_one',
                              'paperboard containers, metal cans, glass containers and plastic bottles; staffing from the broader parent industries'),
    'Paper/Forest Products': (['321', '3221', '113'], ['321', '3221', '113'], 'medium', 'many_to_one', ''),
    'Power': (['2211'], ['2211'], 'medium', 'one_to_one', 'renewable generation (221114-221117) goes to Green & Renewable Energy'),
    'Precious Metals': (['21222'], ['2122'], 'medium', 'subset', 'staffing from all metal ore mining'),
    'Publishing & Newspapers': (['5131'], ['5131'], 'high', 'one_to_one', ''),
    'R.E.I.T.': (['5311'], ['5310'], 'low', 'by_legal_form',
                 'REIT is a tax status; NAICS classifies lessors by activity; staffing from all real estate'),
    'Real Estate (Development)': (['2372'], ['2372'], 'medium', 'subset', ''),
    'Real Estate (General/Diversified)': (['531'], ['5310'], 'low', 'superset', 'reached only by a 3-digit NAICS input'),
    'Real Estate (Operations & Services)': (['5312', '5313'], ['5310'], 'medium', 'many_to_one', 'staffing from all real estate'),
    'Recreation': (['713', '7121'], ['713', '7121'], 'medium', 'many_to_one',
                   'gambling (7132) goes to Hotel/Gaming; recreational vehicle and boat makers not captured'),
    'Reinsurance': (['52413'], ['5241'], 'medium', 'one_to_one', 'one firm: the ratios are that firm\'s'),
    'Restaurant/Dining': (['722'], ['722'], 'high', 'one_to_one', ''),
    'Retail (Automotive)': (['441'], ['441'], 'high', 'one_to_one', ''),
    'Retail (Building Supply)': (['444'], ['444'], 'high', 'one_to_one', ''),
    'Retail (Distributors)': (['423', '424', '425'], ['423', '424', '425'], 'medium', 'many_to_one',
                              'wholesale distributors; food (4244) and drug (4242) wholesalers go to other groups'),
    'Retail (General)': (['455'], ['4550'], 'high', 'one_to_one', ''),
    'Retail (Grocery and Food)': (['445'], ['445'], 'high', 'one_to_one', ''),
    'Retail (REITs)': ([], ['5310'], 'low', 'by_legal_form',
                       'retail property REITs are lessors of nonresidential buildings, the same code as other REITs'),
    'Retail (Special Lines)': (['449', '456', '457', '458', '459'], ['449', '456', '457', '458', '459'], 'medium', 'many_to_one',
                               'NAICS 2022 classifies online retailers by product line'),
    'Rubber& Tires': (['3262'], ['3262'], 'high', 'one_to_one', ''),
    'Semiconductor': (['334413'], ['3344'], 'medium', 'subset', 'staffing from all electronic components'),
    'Semiconductor Equip': (['333242'], ['3330A1'], 'medium', 'subset', 'staffing from the BLS machinery aggregate 3330A1 (3331, 3332, 3334, 3339)'),
    'Shipbuilding & Marine': (['3366', '483'], ['3366', '483'], 'medium', 'many_to_one', 'ship and boat building plus water transportation'),
    'Shoe': (['3162'], ['3162'], 'medium', 'one_to_one', 'listed footwear brands outsource most production'),
    'Software (Entertainment)': ([], ['5132'], 'medium', 'overlaps_software', 'video game publishers are NAICS 5132, covered by the SEC panel rows'),
    'Software (Internet)': ([], ['5132', '5182', '5192'], 'low', 'overlaps_software', 'software; used only for the sanity check against the SEC panel'),
    'Software (System & Application)': ([], ['5132'], 'high', 'overlaps_software', 'covered by the SEC panel rows (SIC 7372 -> 5132)'),
    'Steel': (['3311', '3312'], ['3311', '3312'], 'high', 'one_to_one', ''),
    'Telecom (Wireless)': (['517112'], ['5170'], 'medium', 'subset', 'staffing from all telecommunications'),
    'Telecom. Equipment': (['3342'], ['3342'], 'high', 'one_to_one', ''),
    'Telecom. Services': (['517'], ['5170'], 'medium', 'superset', 'includes cable operators (517111)'),
    'Tobacco': (['3122'], ['3122'], 'high', 'one_to_one', ''),
    'Transportation': (['485', '488', '492', '493'], ['485', '488', '492', '493'], 'medium', 'many_to_one',
                       'logistics, couriers, warehousing and ground passenger transport'),
    'Transportation (Railroads)': (['482'], ['482'], 'high', 'one_to_one', ''),
    'Trucking': (['484'], ['4840'], 'high', 'one_to_one', ''),
    'Utility (General)': (['221'], ['221'], 'medium', 'superset', 'multi-utilities; reached only by a 3-digit NAICS input'),
    'Utility (Water)': (['2213'], ['2213'], 'high', 'one_to_one', ''),
    'Total Market': ([], [], 'n/a', 'total', 'benchmark only'),
    'Total Market (without financials)': ([], ['ALL_EXCEPT_52_99'], 'n/a', 'total',
                                          'generic non-financial prior: emitted with an empty naics so the engine reaches it only on request'),
}
names = list(bm.damodaran_industry)
assert set(CROSSWALK) == set(names), (set(names) - set(CROSSWALK), set(CROSSWALK) - set(names))

# NAICS titles from the OEWS May 2025 files on disk (2-4 digit and BLS aggregates; 5-6 digit list in nat5d_6d)
st = pd.read_csv(f'{OUT}/industry_staffing.csv', dtype={'naics': str, 'soc': str})
titles = st.drop_duplicates('naics').set_index('naics').naics_title.to_dict()
agg_components = {}
for c, t in titles.items():
    if not c.isdigit() and '-' not in c:
        agg_components[c] = re.findall(r'\b(\d{4})\b', t.split('(')[-1]) if '(' in t else []
t56 = {}
for z in [f'{OEWS_DIR}/oesm25in4.zip']:
    if os.path.exists(z):
        with zipfile.ZipFile(z) as zf:
            m = [n for n in zf.namelist() if re.search(r'nat5d_6d_M2025_dl\.xlsx$', n)]
            if m:
                d56 = pd.read_excel(io.BytesIO(zf.read(m[0])), usecols=['NAICS', 'NAICS_TITLE'])
                t56 = dict(zip(d56.NAICS.astype(str), d56.NAICS_TITLE))


def naics_title(p):
    """Title of an engine match prefix from an OEWS file on disk, or '' if the code is not listed there."""
    if p in titles:
        return titles[p]
    if len(p) == 5 and p + '0' in t56:
        return t56[p + '0']
    if p in t56:
        return t56[p]
    if len(p) == 3 and p + '0' in titles:
        return titles[p + '0']
    for a, comps in agg_components.items():
        if p in comps:
            return f'component of BLS aggregate {a} ({titles[a]})'
    return ''


SOFT_PREFIXES = ['5132', '5415', '5182']           # SEC panel rows (SIC 7370-7374); also the pooled '51/54' row
xw = []
for nm in names:
    match, oews, conf, mtype, note = CROSSWALK[nm]
    tl = [naics_title(p) for p in match]
    for o in oews:
        assert o == 'ALL_EXCEPT_52_99' or o in titles, f'{nm}: OEWS code {o} not in industry_staffing.csv'
    for a in oews:
        for b in oews:
            assert a == b or not (a.isdigit() and b.isdigit() and b.startswith(a)), f'{nm}: nested OEWS codes {a}, {b}'
    xw.append(dict(damodaran_industry=nm, n_firms=int(n_tot[nm]), naics_match='/'.join(match),
                   naics_match_titles=' | '.join(t if t else 'not listed in OEWS files (NAICS 2022 code; title unverified)' for t in tl),
                   naics_match_verified=str(int(all(tl))) if match else '',
                   naics_oews='/'.join(oews),
                   naics_oews_titles=' | '.join(titles.get(o, 'all OEWS sectors except 52 and 99') for o in oews),
                   match_type=mtype, confidence=conf,
                   emit_function_shares=int(bool(match)) if nm not in TOTALS else int(nm == 'Total Market (without financials)'),
                   financial_group=int(nm in FINANCIAL), small_sample=int(n_tot[nm] < 20), notes=note, grounding='b'))
xw = pd.DataFrame(xw)
emitted = xw[(xw.emit_function_shares == 1) & (xw.naics_match != '')]
allp = [p for s in emitted.naics_match for p in s.split('/')]
assert len(allp) == len(set(allp)), 'a match prefix is used by two emitted groups'
for p in allp:
    assert p not in ('51', '54') and not any(p.startswith(s) for s in SOFT_PREFIXES), f'prefix {p} collides with software rows'
write_csv(xw, 'xw_damodaran_naics.csv')

# ---------------------------------------------------------------- OEWS wage bill by function
occ = pd.read_csv(f'{OUT}/occupations.csv', dtype={'soc': str}).set_index('soc')
wage = occ.wage_mean.fillna(occ.wage_median)
fo = pd.read_csv(f'{OUT}/function_occ.csv', dtype={'soc': str})
alloc = fo.pivot_table(index='soc', columns='function_id', values='alloc_assumed', aggfunc='first').fillna(0)
fn = pd.read_csv(f'{OUT}/functions.csv')
FIDS = list(fn.function_id)
alloc = alloc.reindex(columns=FIDS, fill_value=0)
PRIMARY = dict(zip(fn.function_id, fn.cost_bucket))
POOL = {f: ('sga' if b in ('sm', 'ga') else b) for f, b in PRIMARY.items()}   # cogs, rnd, sga


def residual_function(soc):
    """ASSUMED rule for employment no FUNC_SOC function claims: by SOC major group."""
    major = soc[:2]
    if major in ('17', '19'):
        return 'F02'                                   # architecture, engineering and science -> product and engineering
    if major == '41':
        return 'F04'                                   # sales occupations -> sales
    if major in ('45', '47', '49', '51', '53'):
        return 'F09'                                   # farming, construction, repair, production, transport -> supply chain
    return 'F08'                                       # everything else -> service delivery and operations


RESID = {s: residual_function(s) for s in occ.index}
sec = st[st.naics_level == 'sector']


def staffing(codes):
    if codes == ['ALL_EXCEPT_52_99']:
        g = sec[~sec.naics.isin(['52', '99'])]
    else:
        g = st[st.naics.isin(codes)]
    return g.groupby('soc').employment.sum()


def industry_wages():
    """Robustness only: OEWS May 2025 industry-specific annual mean wage (A_MEAN) for the same (industry, occupation,
    ownership) rows as industry_staffing.csv, matched on employment. Returns a Series indexed by (naics, soc)."""
    z = f'{OEWS_DIR}/oesm25in4.zip'
    if not os.path.exists(z):
        return None
    fr = []
    with zipfile.ZipFile(z) as zf:
        for m in zf.namelist():
            if re.search(r'nat(sector|3d|4d)_M2025_dl\.xlsx$', m):
                fr.append(pd.read_excel(io.BytesIO(zf.read(m)), dtype=str,
                                        usecols=['NAICS', 'I_GROUP', 'OCC_CODE', 'O_GROUP', 'TOT_EMP', 'A_MEAN']))
    d = pd.concat(fr)
    d = d[d.O_GROUP.str.lower() == 'detailed']
    nd = d.I_GROUP.str.lower().map({'sector': 2, '3-digit': 3, '4-digit': 4})
    d['naics'] = [r if ('-' in r or not r.isdigit()) else r[:int(n)] for r, n in zip(d.NAICS.str.strip(), nd)]
    d['emp'] = pd.to_numeric(d.TOT_EMP.str.replace(',', ''), errors='coerce')
    d['w'] = pd.to_numeric(d.A_MEAN.str.replace(',', ''), errors='coerce')
    m = st[['naics', 'soc', 'employment']].merge(d[['naics', 'OCC_CODE', 'emp', 'w']].rename(columns={'OCC_CODE': 'soc'}),
                                                 left_on=['naics', 'soc', 'employment'], right_on=['naics', 'soc', 'emp'])
    return m.drop_duplicates(['naics', 'soc']).set_index(['naics', 'soc']).w.dropna()


def function_wagebill(codes, ind_wage=None):
    emp = staffing(codes)
    w = wage.reindex(emp.index)
    if ind_wage is not None and codes != ['ALL_EXCEPT_52_99']:
        g_ = st[st.naics.isin(codes)][['naics', 'soc', 'employment']].copy()
        g_['w'] = [ind_wage.get((a, b), np.nan) for a, b in zip(g_.naics, g_.soc)]
        g_['w'] = g_.w.fillna(g_.soc.map(wage))
        g_ = g_[g_.w.notna()]
        w = (g_.employment * g_.w).groupby(g_.soc).sum() / g_.groupby('soc').employment.sum()
        w = w.reindex(emp.index)
    no_wage = float(emp[w.isna()].sum() / emp.sum())
    emp, w = emp[w.notna()], w[w.notna()]
    bill = emp * w
    a = alloc.reindex(bill.index).fillna(0)
    res = (1 - a.sum(axis=1)).clip(lower=0)
    assert (a.sum(axis=1) <= 1 + 1e-9).all()
    wf = a.mul(bill, axis=0).sum()
    rf = pd.Series(0.0, index=FIDS)
    for s, v in (res * bill).items():
        rf[RESID[s]] += v
    return (wf + rf).reindex(FIDS).fillna(0), rf.reindex(FIDS).fillna(0), no_wage, float(bill.sum())


# cross-firm dispersion precedent (class b): coefficient of variation of firm-mean bucket shares in the SEC software
# panel, same filters as 05_function_priors.py
p = read_sec_panel('panel_v2_all.csv')          # without excluded registrants (code/exclusions.py)
q = p[(p.year >= 2023) & (p.year <= 2025) & (p.rev > 0)].copy()
q['cogs'], q['rnd'], q['sga'] = 1 - q.gp / q.rev, q.rd / q.rev, (q.sm + q.ga) / q.rev
q['sm_s'], q['ga_s'] = q.sm / q.rev, q.ga / q.rev
q = q.dropna(subset=['cogs', 'rnd', 'sm_s', 'ga_s'])
q = q[q[['cogs', 'rnd', 'sm_s', 'ga_s']].apply(lambda c: c.between(0, 2)).all(axis=1)]
fm = q.groupby('cik')[['cogs', 'rnd', 'sga']].mean()
CV = (fm.std() / fm.mean()).to_dict()
SPLIT_REL_SD = 0.25                                    # ASSUMED relative sd of a wage-bill split (class d)
MIN_BUCKET = 0.005                                     # bucket below 0.5% of sales -> pool merged into SG&A

ifs_path = f'{OUT}/industry_function_shares.csv'
old = pd.read_csv(ifs_path, dtype=str, keep_default_na=False)
ORIG_COLS = ['sic', 'naics', 'size_band', 'function_id', 'cost_bucket', 'share_of_revenue_prior', 'share_of_revenue_sd',
             'bucket_share_mean', 'bucket_share_sd', 'bucket_share_median', 'within_bucket_split', 'within_bucket_range',
             'within_bucket_assumed', 'n_firms', 'years', 'source']
sw = old[old.source.str.startswith('SEC XBRL panel')][ORIG_COLS].copy()
assert len(sw) == len(old[~old.source.str.startswith('Damodaran')]), 'unexpected rows in industry_function_shares.csv'
sw_hash = hashlib.sha256(sw.to_csv(index=False).encode()).hexdigest()

g = lambda x: f'{x:.6g}'
IND_WAGE = industry_wages()
new_rows, diag = [], {}
bmi = bm.set_index('damodaran_industry')
for r in xw[xw.emit_function_shares == 1].itertuples():
    b = bmi.loc[r.damodaran_industry]
    codes = r.naics_oews.split('/')
    W_f, R_f, no_wage, bill_tot = function_wagebill(codes)
    W_i = function_wagebill(codes, IND_WAGE)[0] if IND_WAGE is not None else None
    raw = {'cogs': b.cogs_sales, 'rnd': b.rnd_sales, 'sga': b.sga_sales}
    clipped = [k for k, v in raw.items() if v < 0]
    bucket = {k: max(v, 0.0) for k, v in raw.items()}
    pool = dict(POOL)
    moved, merged = {}, {}
    small = [k for k in ('cogs', 'rnd', 'sga') if bucket[k] < MIN_BUCKET]
    keep = [k for k in ('sga', 'cogs', 'rnd') if k not in small] or [max(bucket, key=bucket.get)]
    for pb in small:                                   # ASSUMED merge rule: small COGS or R&D -> SG&A; small SG&A -> COGS
        if pb in keep:
            continue
        order = ['sga', 'cogs', 'rnd'] if pb != 'sga' else ['cogs', 'rnd']
        tgt = next(t for t in order + keep if t in keep)
        merged[pb] = tgt
        bucket[tgt] += bucket[pb]
        bucket[pb] = 0.0
        for f in FIDS:
            if pool[f] == pb:
                pool[f], moved[f] = tgt, pb
    d = dict(oews=r.naics_oews, wagebill_usd=bill_tot, employment_without_wage_share=no_wage, moved=moved,
             merged_buckets=merged, negative_buckets_clipped=clipped,
             residual_share_of_wagebill=float(R_f.sum() / W_f.sum()))
    unb = b.other_opex_sales_residual - max(b.da_sales_implied, 0)
    for pb in ('cogs', 'rnd', 'sga'):
        fs = [f for f in FIDS if pool[f] == pb]
        if not fs:
            continue
        Wp = W_f[fs].sum()
        d[f'wagebill_share_{pb}_pool'] = float(Wp / W_f.sum())
        assert Wp > 0, f'{r.damodaran_industry}: empty {pb} pool'
        mb = bucket[pb]
        sb = CV[pb] * mb
        if W_i is not None:
            dif = (W_f[fs] / Wp - W_i[fs] / W_i[fs].sum()).abs()
            d['robust_max_abs_split_diff'] = max(d.get('robust_max_abs_split_diff', 0.0), float(dif.max()))
            d['robust_max_abs_share_diff'] = max(d.get('robust_max_abs_share_diff', 0.0), float(dif.max() * mb))
        for f in fs:
            s = W_f[f] / Wp
            ss = SPLIT_REL_SD * s
            sd = np.sqrt(sb ** 2 * s ** 2 + ss ** 2 * mb ** 2 + sb ** 2 * ss ** 2)
            cb = pb if pb != 'sga' else (PRIMARY[f] if PRIMARY[f] in ('sm', 'ga') else 'ga')
            method = ('single function in pool (definitional)' if len(fs) == 1 else
                      'OEWS May 2025 wage bill: employment x national mean wage x FUNC_SOC allocation, residual employment by SOC major group')
            new_rows.append(dict(
                sic='', naics=r.naics_match if r.damodaran_industry not in TOTALS else '', size_band='all', function_id=f,
                cost_bucket=cb, share_of_revenue_prior=g(mb * s), share_of_revenue_sd=g(sd), bucket_share_mean=g(mb),
                bucket_share_sd=g(sb), bucket_share_median='', within_bucket_split=g(s), within_bucket_range=g(2 * ss),
                within_bucket_assumed='False', n_firms=str(int(b.n_firms)), years=f'Damodaran data dated {DATA_DATE}',
                source=f'Damodaran margin.xls ({DATA_DATE}) bucket shares; OEWS May 2025 wage-bill split (11_nonsoftware_priors.py)',
                damodaran_industry=r.damodaran_industry, prior_basis='damodaran_oews', source_bucket=pb,
                bucket_reassigned_from=moved.get(f, ''), within_bucket_method=method,
                residual_share_of_function_wagebill=g(R_f[f] / W_f[f]) if W_f[f] > 0 else '',
                negative_bucket_clipped='/'.join(clipped), unbucketed_cost_share=g(unb),
                unbucketed_cost_flag=str(int(unb > 0.05)),
                crosswalk_confidence=r.confidence, small_sample=str(r.small_sample), financial_group=str(r.financial_group),
                grounding_bucket='a', grounding_within='c' if len(fs) > 1 else 'c (definitional)',
                grounding_sd='b (bucket CV from SEC software panel) + d (split sd 25%)', grounding_naics='b'))
    diag[r.damodaran_industry] = d

new = pd.DataFrame(new_rows)
NEW_COLS = [c for c in new.columns if c not in ORIG_COLS]
sw_out = sw.copy()
for c in NEW_COLS:
    sw_out[c] = ''
sw_out['prior_basis'] = 'sec_panel'
sw_out['source_bucket'] = sw_out.cost_bucket
sw_out['within_bucket_method'] = 'assumed split (05_function_priors.py WITHIN)'
sw_out['grounding_bucket'] = 'c'
sw_out['grounding_within'] = 'd'
sw_out['grounding_sd'] = 'c (bucket sd) + d (split range)'
sw_out['grounding_naics'] = 'b (SIC to NAICS by description)'
out = pd.concat([sw_out, new[ORIG_COLS + NEW_COLS]], ignore_index=True)[ORIG_COLS + NEW_COLS]
out.to_csv(ifs_path, index=False, encoding='utf-8')
print(f'wrote {ifs_path}  rows={len(out)} (software {len(sw_out)}, non-software {len(new)})')
chk = pd.read_csv(ifs_path, dtype=str, keep_default_na=False)
chk_sw = chk[chk.prior_basis == 'sec_panel'][ORIG_COLS]
assert hashlib.sha256(chk_sw.to_csv(index=False).encode()).hexdigest() == sw_hash, 'software rows changed'
nn = chk[chk.prior_basis == 'damodaran_oews'].copy()
for c in ['share_of_revenue_prior', 'within_bucket_split']:
    nn[c] = nn[c].astype(float)
tot = nn.groupby('damodaran_industry').share_of_revenue_prior.sum()
exp = bmi.loc[tot.index, ['cogs_sales', 'rnd_sales', 'sga_sales']].clip(lower=0).sum(axis=1)
assert ((tot - exp).abs() < 1e-4).all(), 'function shares do not add up to the buckets'
assert (nn.groupby(['damodaran_industry', 'source_bucket']).within_bucket_split.sum().sub(1).abs() < 1e-4).all()
assert not nn.duplicated(['damodaran_industry', 'function_id']).any(), 'a function appears twice in one industry'

# ---------------------------------------------------------------- column dictionary with grounding classes (spec 21.1)
# a sourced; b precedent; c calibrated or computed by us; d scenario or assumed. 'prov' = provenance only.
A_COLS = ['n_firms', 'data_date', 'gross_margin', 'net_margin', 'op_margin_pretax_pre_sbc', 'op_margin_pretax',
          'op_margin_aftertax', 'op_margin_pretax_lease', 'op_margin_aftertax_lease', 'op_margin_pretax_lease_rnd',
          'op_margin_aftertax_lease_rnd', 'ebitda_sales', 'ebitda_plus_sga_sales', 'ebitda_plus_rnd_sales', 'cogs_sales',
          'rnd_sales', 'sga_sales', 'sbc_sales', 'lease_sales', 'beta', 'cost_of_equity', 'e_over_de', 'sd_stock',
          'cost_of_debt', 'tax_rate_wacc_sheet', 'after_tax_cost_of_debt', 'd_over_de', 'cost_of_capital', 'roe_unadj',
          'roe_rnd_adj', 'roc_fundgr', 'reinvestment_rate', 'expected_growth_ebit', 'revenue_cagr_5y', 'sales_to_ic_ltm'] + \
         list(ROC_OUT.values())
DICT = [('industry_benchmarks.csv', 'damodaran_industry', 'a', 'Damodaran industry group name, verbatim')]
DICT += [('industry_benchmarks.csv', c, 'a', 'Damodaran Jan 2026 value as published (practitioner_dataset_disclosed); '
          'file and row in source_rows') for c in A_COLS]
DICT += [('industry_benchmarks.csv', c, 'c', d) for c, d in [
    ('small_sample', 'n_firms < 20'), ('financial_group', 'the nine financial groups (their firm counts sum to 1,173; '
     'Total Market minus non-financials is 1,172)'), ('is_total', 'Total Market rows'),
    ('sga_sales_derived', '(EBITDA+SG&A)/Sales - EBITDA/Sales'), ('sga_identity_gap', 'sga_sales_derived - sga_sales'),
    ('rnd_identity_gap', '(EBITDA+R&D)/Sales - EBITDA/Sales - rnd_sales'), ('da_sales_implied', 'EBITDA/Sales - pre-tax operating margin'),
    ('other_opex_sales_residual', '1 - COGS - SG&A - R&D - pre-tax operating margin (costs outside the three buckets)'),
    ('unbucketed_opex_sales', 'other_opex_sales_residual - max(da_sales_implied, 0)'),
    ('tax_rate_implied', '1 - after-tax / pre-tax unadjusted operating margin'),
    ('fundgr_suspect', '1 if the fundgrEB ROC equals another row to all digits (Utility (Water) = Total Market)'),
    ('roic_basis', 'which ROC the k and spread use; fundgrEB = lease and R&D adjusted (matched to roc.html, see notes)'),
    ('k_ic_per_sales', 'default invested capital per dollar of sales: unadjusted when a ROC table is on disk, else lease_rnd (variant in k_variant)'),
    ('k_variant', 'variant behind k_ic_per_sales'), ('k_ic_per_sales_unadj', 'after-tax unadjusted margin / unadjusted ROIC (roc.xls)'),
    ('k_ic_per_sales_lease', 'lease-adjusted margin / lease-adjusted after-tax ROIC (roc_html.csv or roc.xls)'),
    ('k_ic_per_sales_lease_rnd', 'lease and R&D adjusted margin / matching after-tax ROIC (roc_html.csv or roc.xls, else fundgrEB)'),
    ('k_ic_per_sales_fundgr', 'margin on fundgrEB basis / fundgrEB ROC'), ('k_flag', 'usability of k'),
    ('roic_minus_wacc', 'ROC on roic_basis - cost_of_capital'), ('reinvestment_sales', 'reinvestment rate x margin on the ROC basis'),
    ('reinvestment_flag', 'negative or above-100% reinvestment rates'), ('k_marginal_implied', 'reinvestment_sales / revenue_cagr_5y (histgr.xls)'),
    ('k_ic_per_sales_mgnroc', '1 / Sales-to-invested-capital (mgnroc.xls)')]]
DICT += [('industry_benchmarks.csv', 'source_rows', 'prov', 'Excel rows (1-based) in each source file')]
DICT += [('xw_damodaran_naics.csv', c, g_, d) for c, g_, d in [
    ('damodaran_industry', 'a', 'group name'), ('n_firms', 'a', 'Damodaran firm count'),
    ('naics_match', 'b', 'NAICS 2022 prefixes the engine matches a firm to (precedent-class mapping by name and scope)'),
    ('naics_match_titles', 'a', 'titles from OEWS May 2025 files on disk; unverified where marked'),
    ('naics_match_verified', 'c', '1 if every prefix is listed in an OEWS file on disk'),
    ('naics_oews', 'b', 'OEWS May 2025 industries whose staffing splits the buckets'), ('naics_oews_titles', 'a', 'OEWS titles'),
    ('match_type', 'b', 'one_to_one, subset, superset, many_to_one, by_size, by_legal_form, by_technology, shared_code, conglomerate, inferred, overlaps_software, total'),
    ('confidence', 'b', 'high, medium, low (rules in notes)'), ('emit_function_shares', 'c', '1 if rows are written to industry_function_shares.csv'),
    ('financial_group', 'c', 'as in benchmarks'), ('small_sample', 'c', 'n_firms < 20'), ('notes', 'b', 'reasoning'),
    ('grounding', 'b', 'class of the mapping'),
    ('oews_employment_matched', 'c', 'OEWS May 2025 jobs in industries the engine matches to the group (aggregates split equally across components)')]]
DICT += [('industry_function_shares.csv (non-software rows)', c, g_, d) for c, g_, d in [
    ('naics', 'b', 'engine match prefixes from the crosswalk (empty for the generic Total Market row)'),
    ('size_band', 'c', "'all': Damodaran has no size bands"), ('cost_bucket', 'c', 'pool the share is drawn from (sm/ga = parts of SG&A)'),
    ('share_of_revenue_prior', 'c', 'bucket_share_mean x within_bucket_split; a x c, valid for the NAICS firm by precedent (b)'),
    ('share_of_revenue_sd', 'b+d', 'bucket sd (CV of the SEC software panel, b) combined with a 25% relative split sd (d)'),
    ('bucket_share_mean', 'a', 'Damodaran COGS, R&D or SG&A over sales (negatives clipped at 0; small pools merged, d)'),
    ('bucket_share_sd', 'b', 'CV of firm-mean bucket shares in the SEC software panel x bucket_share_mean'),
    ('bucket_share_median', 'n/a', 'empty: Damodaran publishes aggregates only'),
    ('within_bucket_split', 'c', 'OEWS May 2025 wage bill share within the pool (FUNC_SOC allocation and residual rule are d)'),
    ('within_bucket_range', 'd', '2 x assumed split sd (same convention as the software rows)'),
    ('within_bucket_assumed', 'c', 'False: the split is computed from OEWS data, not assumed'),
    ('n_firms', 'a', 'Damodaran firm count'), ('years', 'prov', 'data date'), ('source', 'prov', 'sources'),
    ('damodaran_industry', 'b', 'group the row comes from'), ('prior_basis', 'prov', 'sec_panel or damodaran_oews'),
    ('source_bucket', 'c', 'Damodaran bucket the pool belongs to (cogs, rnd, sga)'),
    ('bucket_reassigned_from', 'd', 'pool merged because its bucket is below 0.5% of sales'),
    ('within_bucket_method', 'prov', 'method text'), ('residual_share_of_function_wagebill', 'c', 'share of the function wage bill assigned by the SOC residual rule (d)'),
    ('negative_bucket_clipped', 'c', 'buckets negative in the source'), ('unbucketed_cost_share', 'c', 'unbucketed_opex_sales of the group'),
    ('unbucketed_cost_flag', 'c', '1 if unbucketed_cost_share > 0.05'), ('crosswalk_confidence', 'b', 'from the crosswalk'),
    ('small_sample', 'c', 'n_firms < 20'), ('financial_group', 'c', 'financial group flag'),
    ('grounding_bucket', 'prov', 'class of bucket_share_mean'), ('grounding_within', 'prov', 'class of within_bucket_split'),
    ('grounding_sd', 'prov', 'class of share_of_revenue_sd'), ('grounding_naics', 'prov', 'class of the NAICS link')]]
dct = pd.DataFrame(DICT, columns=['file', 'column', 'grounding', 'definition'])
missing_cols = (set(BM_COLS) - set(dct[dct.file == 'industry_benchmarks.csv'].column)) | \
               (set(xw.columns) - set(dct[dct.file == 'xw_damodaran_naics.csv'].column)) | \
               (set(NEW_COLS) - set(dct[dct.file.str.startswith('industry_function')].column))
assert not missing_cols, f'columns without a grounding tag: {missing_cols}'
write_csv(dct, 'nonsoftware_column_grounding.csv')

# ---------------------------------------------------------------- coverage of US employment (OEWS May 2025)
d4 = st[st.naics_level == '4-digit'].groupby('naics').agg(emp=('employment', 'sum'), cov=('coverage', 'first'))
d4['total'] = d4.emp / d4['cov']
three = set(st[st.naics_level == '3-digit'].naics)
dam_p = [p for s in emitted[emitted.damodaran_industry != 'Total Market (without financials)'].naics_match for p in s.split('/')]


def status(code, prefixes):
    if any(code.startswith(p) for p in prefixes):
        return 'full'
    if any(p.startswith(code) and len(p) > len(code) for p in prefixes):
        return 'partial'
    return 'none'


def comps_of(c):
    """NAICS components of an OEWS 4-digit-level code ('3270' = all of 327; BLS aggregates list their parts)."""
    if c.isdigit():
        return [c[:3]] if (c.endswith('0') and c[:3] in three and titles.get(c) == titles.get(c[:3])) else [c]
    return agg_components.get(c, []) or [c[:4]]


def classify(c):
    comps = comps_of(c)
    sd_ = [status(x, dam_p) for x in comps]
    ss_ = [status(x, SOFT_PREFIXES) for x in comps]
    if all(x == 'full' for x in sd_):
        return 'damodaran_full'
    if all(x == 'full' for x in ss_):
        return 'sec_software'
    if any(x != 'none' for x in sd_):
        return 'damodaran_partial'
    if c[:2] in ('51', '54'):
        return 'pooled_software_51_54'
    return 'generic'


d4['class'] = [classify(c) for c in d4.index]
# OEWS employment the engine matches to each emitted group (longest prefix; an aggregate's employment is split equally
# across its component codes, an approximation)
pre2grp = {p_: g_ for g_, s_ in zip(emitted.damodaran_industry, emitted.naics_match) if s_
           and g_ != 'Total Market (without financials)' for p_ in s_.split('/')}
grp_emp = {}
for c, tot_ in d4.total.items():
    cs = comps_of(c)
    for x_ in cs:
        ps = [p_ for p_ in pre2grp if x_.startswith(p_)]
        if ps:
            g_ = pre2grp[max(ps, key=len)]
            grp_emp[g_] = grp_emp.get(g_, 0.0) + tot_ / len(cs)
xw['oews_employment_matched'] = xw.damodaran_industry.map(grp_emp).round(0)
write_csv(xw, 'xw_damodaran_naics.csv')
cov = (d4.groupby('class').total.sum() / d4.total.sum()).round(4).to_dict()
nongov = d4[~d4.index.str.startswith('99')]
cov_nongov = (nongov.groupby('class').total.sum() / nongov.total.sum()).round(4).to_dict()
top_generic = d4[d4['class'] == 'generic'].sort_values('total', ascending=False).head(8)
top_generic = [(c, titles.get(c, ''), int(v)) for c, v in top_generic.total.items()]

# ---------------------------------------------------------------- sanity check: Damodaran software vs SEC panel FY2025
US = set('AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR '
         'PA RI SC SD TN TX UT VT VA WA WV WI WY'.split())
y = p[(p.year == 2025) & (p.rev > 0)].copy()
y['sga'] = y.sm + y.ga
y['op_pre_sbc'] = y.op_inc + y.sbc
METRICS = {'gross_margin': ('gp', 'gross_margin'), 'op_margin_pretax': ('op_inc', 'op_margin_pretax'),
           'op_margin_pretax_pre_sbc': ('op_pre_sbc', 'op_margin_pretax_pre_sbc'), 'rnd_sales': ('rd', 'rnd_sales'),
           'sga_sales': ('sga', 'sga_sales'), 'sbc_sales': ('sbc', 'sbc_sales')}
cuts = {'SIC 7372': y.sic == 7372, 'SIC 7370+7372': y.sic.isin([7370, 7372]), 'SIC 7370-7374': y.sic.between(7370, 7374),
        'SIC 7370+7372, US-located': y.sic.isin([7370, 7372]) & y['loc'].isin(US),
        'SIC 7370-7374, US-located': y.sic.between(7370, 7374) & y['loc'].isin(US)}
san = []
for cname, mask in cuts.items():
    z = y[mask]
    for mname, (col, dcol) in METRICS.items():
        zz = z[z[col].notna()]
        agg = float(zz[col].sum() / zz.rev.sum()) if len(zz) else np.nan
        med = float((zz[col] / zz.rev).median()) if len(zz) else np.nan
        row = dict(panel_cut=cname, metric=mname, n_firms=len(zz), panel_aggregate=agg, panel_median=med)
        for dn in ['Software (System & Application)', 'Software (Internet)']:
            row[f'damodaran_{dn}'] = float(bmi.loc[dn, dcol])
        row['gap_sysapp_minus_panel_aggregate'] = row['damodaran_Software (System & Application)'] - agg
        san.append(row)
san = pd.DataFrame(san)
san.to_csv(f'{OUT}/_build/software_sanity_check.csv', index=False, float_format='%.4f')
# reinvestment cross-check for software: marginal capital per dollar of growth at the panel's realised revenue growth
rx = {}
for cname, sics in [('SIC 7372', [7372]), ('SIC 7370+7372', [7370, 7372])]:
    z = y[y.sic.isin(sics) & y.rev_lag.notna() & (y.rev_lag > 0)]
    g1 = float(z.rev.sum() / z.rev_lag.sum() - 1)
    a, b_ = p[(p.year == 2020) & p.sic.isin(sics)].set_index('cik').rev, y[y.sic.isin(sics)].set_index('cik').rev
    both = a.index.intersection(b_.index)
    g5 = float((b_[both].sum() / a[both].sum()) ** (1 / 5) - 1)
    sa = bmi.loc['Software (System & Application)']
    rs = float(sa.reinvestment_rate * sa[MARGIN_FOR[FUNDGR_BASIS]]) if pd.notna(sa.reinvestment_rate) else np.nan
    rx[cname] = dict(panel_revenue_growth_fy2025_aggregate=g1, n_fy2025=int(len(z)), panel_revenue_cagr_fy2020_25=g5,
                     n_cagr=int(len(both)), damodaran_reinvestment_sales=rs,
                     k_marginal_at_fy2025_growth=rs / g1, k_marginal_at_5y_cagr=rs / g5,
                     k_average_fundgr=float(sa.k_ic_per_sales_fundgr) if pd.notna(sa.k_ic_per_sales_fundgr) else np.nan)

save_meta('nonsoftware_priors', dict(
    mode='full', data_date=DATA_DATE, sha256=hashes, file_dates=dates, roc_status=roc_status, mgnroc_status=mgn_status,
    fundgr_status=fg_status, histgr_status=hg_status, fundgr_basis=FUNDGR_BASIS, roc_source=ROC_SRC, reinvestment_crosscheck_software=rx,
    wacc_inputs={k: dict(value=v[0], excel_row=v[1], excel_col=v[2]) for k, v in wacc_inputs.items()},
    checks=checks, faq={k: v for k, v in faqs.items()}, n_industries=int(len(bm) - len(TOTALS)),
    crosswalk_counts=dict(confidence=xw.confidence.value_counts().to_dict(), emitted=int(xw.emit_function_shares.sum()),
                          unverified_prefixes=sorted({p for s, t in zip(xw.naics_match, xw.naics_match_titles)
                                                      for p, tt in zip(s.split('/'), t.split(' | ')) if s and 'unverified' in tt})),
    dispersion_cv_sec_software=CV, split_rel_sd_assumed=SPLIT_REL_SD, min_bucket=MIN_BUCKET,
    software_rows_sha256=sw_hash, n_software_rows=int(len(sw_out)), n_nonsoftware_rows=int(len(new)),
    coverage_oews_employment=cov, coverage_oews_employment_excl_government=cov_nongov,
    oews_total_employment_4digit=float(d4.total.sum()), largest_generic_industries=top_generic, industry_diagnostics=diag))
print('checks', checks)
print(roc_status, '|', fg_status, '|', hg_status, '|', mgn_status)
print('coverage', cov, '\nexcl. government', cov_nongov)
print(san[san.panel_cut.isin(['SIC 7372', 'SIC 7370+7372', 'SIC 7370-7374'])].round(3).to_string())
