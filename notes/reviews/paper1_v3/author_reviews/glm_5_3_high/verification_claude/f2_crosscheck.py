"""GLM-F2: (1) cross-check the reviewer's filing texts against our own extract before using them;
(2) quote the passages the reviewer cites; (3) recompute the proposed Table 3 fills.

Inputs: the reviewer's filing texts in ../diagnostics/accounting/ (bs_f1.txt, bs_424b4.txt, bs_q2_ex991.txt,
bs_q2_ex992.txt) and our own files notes/case_bending_spoons_f1_extract.md and
data/v3_inputs/bending_spoons_cash_interest.json. Run from the repository root.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ACC = os.path.join(HERE, '..', 'diagnostics', 'accounting')


def norm(p):
    t = open(p, encoding='utf-8', errors='replace').read().replace('​', ' ').replace('\xa0', ' ')
    t = re.sub(r'\s+', ' ', t)
    return re.sub(r'\$ ', '$', t)


T = {k: norm(os.path.join(ACC, f)) for k, f in
     [('f1', 'bs_f1.txt'), ('424b4', 'bs_424b4.txt'), ('ex991', 'bs_q2_ex991.txt'), ('ex992', 'bs_q2_ex992.txt')]}

# --- (1) rows of our extract / json, searched as contiguous rows in the reviewer's texts
ours = json.load(open('data/v3_inputs/bending_spoons_cash_interest.json'))
cf = ours['annual_cash_flow_supplemental']
rows = [
    ('extract: revenue 2023-25, Q1 25/26', '424b4', 'Revenue $387,067 $671,053 $1,306,404 $258,946 $601,321'),
    ('extract: operating income 2023-25, Q1 25/26', '424b4', 'Operating income (loss) $84,267 $127,352 $277,851 $(4,615) $120,171'),
    ('extract: interest expense 2023-25, Q1 25/26', '424b4', 'Interest expense $17,173 $32,605 $142,601 $19,316 $93,184'),
    ('extract: operating cash flow 2023-25', '424b4', 'Net cash from operating activities $59,154 $204,895 $290,600'),
    ('extract: investing cash flow 2023-25', '424b4', 'Net cash from investing activities $(170,294) $(889,654) $(1,851,874)'),
    ('json: interests paid 2023-25 (F-34/35)', '424b4',
     'Interests paid $%s $%s $%s' % tuple(f"{cf['interests_paid'][y]:,}" for y in ('2023', '2024', '2025'))),
    ('json: income taxes paid 2023-25', '424b4',
     'Income taxes paid $%s $%s $%s' % tuple(f"{cf['income_taxes_paid'][y]:,}" for y in ('2023', '2024', '2025'))),
    ('json: interests paid Q1 25/26 (F-6/7)', '424b4', 'Interests paid $%s $%s' % tuple(
        f"{ours['q1_cash_flow_supplemental']['interests_paid'][q]:,}" for q in ('Q1 2025', 'Q1 2026'))),
    ('extract: reorganization expense 2023-25, Q1 25/26', '424b4', 'Reorganization-related expense $13,514 $51,792 $78,607 $44,610 $75,759'),
    ('extract: adjusted operating income 2023-25', '424b4', '$137,441 $299,481 $613,247'),
    ('extract: pro forma revenue components and total', '424b4', 'Revenue $1,306,404 $291,843 $633,365 $376,883 $2,608,496'),
    ('extract: purchase prices AOL/Eventbrite/Vimeo', '424b4', '$1,454 million, $505 million, and $1,359 million'),
    ('extract: pro forma operating income 508,758', '424b4', '$(21,262) $508,758'),
    ('json: H1 interests paid', 'ex992', '%s' % f"{ours['h1_2026']['interests_paid']['H1 2025']:,}"),
    ('json: H1 2026 interests paid', 'ex992', '%s' % f"{ours['h1_2026']['interests_paid']['H1 2026']:,}"),
    ('extract: H1 acquisitions of businesses', 'ex992', '(575,228)'),
    ('extract: H1 2026 acquisitions of businesses', 'ex992', '(2,286,259)'),
    ('extract: H1 net investing', 'ex992', '(575,563)'),
    ('extract: H1 2026 net investing', 'ex992', '(2,290,228)'),
    ('extract: Q2 revenue 704,155 vs 311,100', 'ex991', '704,155'),
    ('extract: Q2 operating income 240,251', 'ex991', '240,251'),
    ('json: Q2 2026 interest expense 108,970', 'ex991', '108,970'),
    ('extract: Q2 reorganization 50,799', 'ex991', '50,799'),
    ('extract: Q2 organic growth 3% (footnote marker between "growth" and "was")', 'ex991', 'was 3% in Q2 2026'),
]
print('(1) Our extract versus the reviewer\'s texts')
ok = 0
for label, doc, s in rows:
    hit = s in T[doc]
    hit_f1 = s in T['f1'] if doc == '424b4' else None
    ok += hit
    print(f"  {'OK ' if hit else 'MISSING'} {label} [{doc}]" + ('' if hit_f1 is None else f"; also in F-1 text: {hit_f1}"))
print(f'  {ok}/{len(rows)} found')

# --- (2) passages the reviewer cites (short windows)
def win(doc, pat, n=170):
    m = re.search(pat, T[doc])
    return None if m is None else T[doc][m.start():m.start() + n]

print('\n(2) Passages')
for doc in ('f1', '424b4'):
    print(f'  [{doc}] organic 2024:', win(doc, r'Organic revenue growth \d* ?was 7% in 2024', 60))
    print(f'  [{doc}] organic 2025:', win(doc, r'Organic revenue growth was 13% in 2025', 60))
    print(f'  [{doc}] subscription share:', win(doc, r'Subscriptions accounted for 95% of our revenue', 95))
    print(f'  [{doc}] equity compensation (cash-flow statement):', win(doc, r'Equity compensation expense \$14,900 \$25,855 \$55,523', 60))
    print(f'  [{doc}] investing split:', win(doc, r'Acquisitions of businesses net of cash and cash equivalents acquired \$\(170,586\)', 330))
fn = re.search(r'30 Organic revenue growth|Organic revenue growth is defined|organic revenue growth as', T['424b4'])
print('  [424b4] definition of the footnoted measure:', None if fn is None else T['424b4'][fn.start():fn.start() + 330])

# --- (3) recomputation (USD thousands)
REV = {2023: 387_067, 2024: 671_053, 2025: 1_306_404}
OPI = {2024: 127_352, 2025: 277_851}
INTX = {2024: 32_605, 2025: 142_601}
REORG = {2024: 51_792, 2025: 78_607}
OCF = {2024: 204_895, 2025: 290_600}
SBC = {2023: 14_900, 2024: 25_855, 2025: 55_523}
PPE = {2024: 604, 2025: 501}
ORG = {2024: 0.07, 2025: 0.13}
ACQ = {2024: 726_574, 2025: 1_851_307}
INTANG = {2024: 162_476, 2025: 67}
NETINV = {2024: 889_654, 2025: 1_851_874}
TAU = 0.24
print('\n(3) Recomputation (points of revenue)')
for y in (2024, 2025):
    g = REV[y] / REV[y - 1] - 1
    m = OPI[y] / REV[y]
    i = INTX[y] / REV[y]
    ro = REORG[y] / REV[y]
    print(f'  {y}: growth {100*g:.2f}; GAAP op margin {100*m:.2f}; interest expense {100*i:.2f}; reorganization {100*ro:.2f}')
    print(f'        organic + GAAP margin: {100*(ORG[y]+m):.2f} before interest, {100*(ORG[y]+m-i):.2f} after interest expense')
    print(f'        with reorganization added back: {100*(ORG[y]+m+ro):.2f} before, {100*(ORG[y]+m+ro-i):.2f} after')
    print(f'        same with after-tax interest (tau=24%): {100*(ORG[y]+m-(1-TAU)*i):.2f} / {100*(ORG[y]+m+ro-(1-TAU)*i):.2f}')
    print(f'        SBC {100*SBC[y]/REV[y]:.2f}% of revenue; PP&E {100*PPE[y]/REV[y]:.3f}%')
    cash_after = 100 * (g + OCF[y] / REV[y])
    print(f'        cash score after interest paid g+OCF/S = {cash_after:.2f}; minus SBC = {cash_after-100*SBC[y]/REV[y]:.2f};'
          f' minus SBC and PP&E = {cash_after-100*(SBC[y]+PPE[y])/REV[y]:.2f}')
    print(f'        investing split: acquisitions {100*ACQ[y]/NETINV[y]:.1f}%, intangibles {100*INTANG[y]/NETINV[y]:.1f}%,'
          f' PP&E {100*PPE[y]/NETINV[y]:.2f}% of the net outflow')
print(f'  pro forma ratio 2,608,496 / 1,306,404 = {2_608_496/1_306_404:.3f}')
print(f'  k_acq: Eventbrite {505_000/291_843:.3f}, AOL {1_454_000/633_365:.3f}, Vimeo {1_359_000/(376_883*365/327):.3f}'
      f' (Vimeo annualized from 327 days, 1 Jan to 23 Nov 2025)')
