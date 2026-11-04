#!/usr/bin/env python3
"""Data files of the business dashboard "Rule of 40 and AI: business guide" (3 November 2026).

Reads only committed outputs; runs no model:
  notes/mc_results_2026-11-03_1m/mc_claims.json            stress test, seed 20261102 (claims, levels, Sobol, swings, sub-box)
  notes/mc_results_2026-11-03_1m/seed2/mc_claims.json      seed 20261104, with its comparison against seed 1
  notes/mc_results_2026-11-03_1m/draws_lhs.csv.gz          the 1,000,000 Latin-hypercube draws of seed 1
  notes/playbook_results.json                              the four-lever ranking at six positions (companion paper, cited
                                                           by Paper 1 Section 7.5) and the six positions of Table 7
  paper1/macros.tex, paper1/stress_macros.tex, sections/tables/*macros*.tex   every number the paper prints
and writes CSV files to notes/mc_results_2026-11-03_1m/dashboard/:
  facts.csv      one row per number quoted in the page's text, as the paper prints it, with its macro and section
  positions.csv  the six positions of Table 7 with their cost lines and the lever ranking on each spend basis
  levers.csv     score points from a 10% saving in each of four cost lines, by position and spend basis
  levels.csv     the central path by year and spend basis: central, the paper's anchor interval, 5-95% of draws, range
  hist.csv       histograms over all 1,000,000 draws (2036 score, G*, payback, realized share)
  bands.csv      quantiles of one output within bins of one input (G* by compute share; 2036 score by change capacity)
  sobol.csv      Sobol total and first-order indices by input group, with 95% intervals
  swings.csv     one-group-at-a-time swings of G* and of the 2036 score (all other inputs central)
  pace.csv       share of the program's benefits realized and embedded by year, central and fast execution
  claims.csv     the 18 rows of Supplement Table S18, with a plain-language reading
  amin.csv       the accountability sub-box tests
Every number on the page comes from one of these files; code/biz_dashboard_page.py builds the page from its template.
Run from anywhere:  python3 code/biz_dashboard_data.py && python3 code/biz_dashboard_page.py
"""
import csv
import glob
import json
import os
import re

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MC = os.path.join(BASE, 'notes', 'mc_results_2026-11-03_1m')
OUT = os.path.join(MC, 'dashboard')
os.makedirs(OUT, exist_ok=True)
J = json.load(open(os.path.join(MC, 'mc_claims.json')))
J2 = json.load(open(os.path.join(MC, 'seed2', 'mc_claims.json')))
PB = json.load(open(os.path.join(BASE, 'notes', 'playbook_results.json')))

# ---------------------------------------------------------------------------------------------------- macros
_FILES = [os.path.join(BASE, 'paper1', f) for f in ('macros.tex', 'stress_macros.tex', 'spec_macros.tex')]
_FILES += sorted(glob.glob(os.path.join(BASE, 'sections', 'tables', '*macros*.tex')))
MAC = {}
for f in _FILES:
    if os.path.exists(f):
        for m in re.finditer(r'\\(?:newcommand|renewcommand|providecommand)\*?\{?\\([A-Za-z]+)\}?(?:\[\d\])?\{((?:[^{}]|\{[^{}]*\})*)\}',
                             open(f).read()):
            MAC[m.group(1)] = m.group(2)


def mac(name):
    """The macro's value as the paper prints it, in plain text."""
    v = MAC[name]
    v = re.sub(r'\\([A-Za-z]+)(?:\{\})?', lambda m: mac(m.group(1)) if m.group(1) in MAC else m.group(0), v)
    return v.replace('{,}', ',').replace('$-$', '\u2212').replace('$+$', '+').replace('\\%', '%').strip()


def num(s):
    return float(s.replace(',', '').replace('\u2212', '-').replace('%', '').replace('+', ''))


def write(name, rows, cols):
    with open(os.path.join(OUT, name), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, '') for c in cols})
    print(f'wrote {name}: {len(rows)} rows')


def r1(x):
    return float(f'{x:.1f}')


# -------------------------------------------------------------------------------------------- sections cited
P1 = 'Paper 1'
SUP = 'Supplementary Appendix'
S = {  # label -> section number in the built paper (paper1.aux / supplement.aux of 3 Nov 2026)
    'sec:intro': f'{P1}, Section 1', 'sec:model-statics': f'{P1}, Section 3.5', 'sec:model-entry': f'{P1}, Section 3.8',
    'sec:model-ai': f'{P1}, Section 3.9', 'sec:data': f'{P1}, Section 4', 'sec:empirics': f'{P1}, Section 5',
    'sec:acquired-growth': f'{P1}, Section 6', 'sec:horizons-ceiling': f'{P1}, Section 7.2',
    'sec:horizons-ranges': f'{P1}, Section 7.3', 'sec:levers-position': f'{P1}, Section 7.5 and Table 7',
    'sec:discussion': f'{P1}, Section 8', 'sec:discussion-exec': f'{P1}, Section 8.2',
    'sec:discussion-measure': f'{P1}, Section 8.3', 'sec:discussion-track': f'{P1}, Section 8.4',
    'sec:discussion-acc': f'{P1}, Section 8.5', 'sec:discussion-limits': f'{P1}, Section 8.6',
    'sec:conclusion': f'{P1}, Section 9', 'supp:stress': f'{SUP}, Section S10',
    'cor:priorities': f'{P1}, Corollary 3', 'prop:entry': f'{P1}, Proposition 4', 'prop:amin': f'{P1}, Proposition 5',
    'prop:levers': f'{P1}, Proposition 9', 'companion': 'Companion paper ranking (notes/playbook_results.json), cited in Paper 1, Section 7.5',
}

# ------------------------------------------------------------------------------------------------ positions
POS = {p['code']: p for p in PB['paper1_positions']}
RB = PB['ranking_by_basis']
BASES = [('netted', 'Central'), ('all', 'All S&M buys growth'), ('none', 'No S&M buys growth')]
LEVER_LABEL = {'engineering (R&D)': 'Engineering (R&D)', 'overhead (G&A)': 'Back office (G&A)',
               'growth engine': 'Growth engine (S&M)', 'cost of revenue': 'Cost of revenue'}
pos_rows, lev_rows = [], []
for code in ['A1', 'A2', 'A3', 'A4', 'A5', 'A6']:
    p, rb = POS[code], RB['positions'][code]
    row = {'code': code, 'position': p['name'], 'firm_years': p['n'], 'growth': r1(100 * p['g']), 'margin': r1(100 * p['m']),
           'sm': r1(100 * p['sm']), 'growth_spend': r1(100 * p['sigma']), 'ga': r1(100 * p['ga']), 'rd': r1(100 * p['rd']),
           'k': f"{p['k']:.2f}", 'cap_hurdle': f"{p['cap_hurdle']:.2f}"}
    for b, _ in BASES:
        rk = [LEVER_LABEL[x] for x in rb[b]['ranking']]
        row[f'first_{b}'], row[f'second_{b}'] = rk[0], rk[1]
    pos_rows.append(row)
    for b, blabel in BASES:
        vals = rb[b]['values']
        order = rb[b]['ranking']
        for lv in ['engineering (R&D)', 'overhead (G&A)', 'growth engine', 'cost of revenue']:
            lev_rows.append({'id': f'{code}|{b}|{lv}', 'code': code, 'position': p['name'], 'basis': blabel, 'lever': LEVER_LABEL[lv],
                             'points': f'{100 * vals[lv]:.2f}', 'rank': order.index(lv) + 1})
write('positions.csv', pos_rows, ['code', 'position', 'firm_years', 'growth', 'margin', 'sm', 'growth_spend', 'ga', 'rd', 'k',
                                  'cap_hurdle', 'first_netted', 'second_netted', 'first_all', 'second_all', 'first_none', 'second_none'])
write('levers.csv', lev_rows, ['id', 'code', 'position', 'basis', 'lever', 'points', 'rank'])
second_ga_net = sum(r['second_netted'] == 'Back office (G&A)' for r in pos_rows)
third_cor_net = sum(LEVER_LABEL['cost of revenue'] == [LEVER_LABEL[x] for x in RB['positions'][c]['netted']['ranking']][2]
                    for c in POS)
hurdles = [float(r['cap_hurdle']) for r in pos_rows]
eng_pts = [float(r['points']) for r in lev_rows if r['basis'] == 'Central' and r['lever'] == 'Engineering (R&D)']
ga_pts = [float(r['points']) for r in lev_rows if r['basis'] == 'Central' and r['lever'] == 'Back office (G&A)']
cor_pts = [float(r['points']) for r in lev_rows if r['basis'] == 'Central' and r['lever'] == 'Cost of revenue']
gc = [r for r in lev_rows if r['code'] == 'A1' and r['basis'] == 'Central']
gc_pts = {r['lever']: r['points'] for r in gc}

# ---------------------------------------------------------------------------------------------- the draws
D = pd.read_csv(os.path.join(MC, 'draws_lhs.csv.gz'))
N = len(D)
assert N == J['design']['n_lhs'] == 1_000_000


def hist(metric, series, col, lo, hi, step, clip=True):
    v = D[col].to_numpy(float)
    v = v[np.isfinite(v)]
    n = len(v)
    edges = np.round(np.arange(lo, hi + step / 2, step), 6)
    w = np.clip(v, lo, hi - 1e-9) if clip else v
    cnt, _ = np.histogram(w, bins=edges)
    return [{'id': f'{metric}|{series}|{i}', 'metric': metric, 'series': series, 'bin_lo': f'{edges[i]:g}', 'bin_hi': f'{edges[i + 1]:g}',
             'share': f'{c / n:.6f}', 'count': int(c), 'n': n, 'open_top': int(clip and i == len(cnt) - 1)} for i, c in enumerate(cnt)]


H = []
H += hist('score2036', 'All inputs move', 'R2036_net', 20, 100, 2)
H += hist('gstar', 'All inputs move', 'Gstar_2025', 15, 75, 1.5)
H += hist('gstar', 'Compute held at 6%', 'Gstar_2025_cc6', 15, 75, 1.5)
H += hist('payback', 'All inputs move', 'payback_years', 3, 20, 0.5)
H += hist('payback', 'Central execution', 'payback_years_central_exec', 3, 20, 0.5)
H += hist('realized', 'All inputs move', 'realized_share_2036', 0, 90, 2.5)
write('hist.csv', H, ['id', 'metric', 'series', 'bin_lo', 'bin_hi', 'share', 'count', 'n', 'open_top'])


def bands(name, xcol, ycol, edges, xscale=1.0):
    x = D[xcol].to_numpy(float) * xscale
    y = D[ycol].to_numpy(float)
    out = []
    for i in range(len(edges) - 1):
        m = (x >= edges[i]) & (x < edges[i + 1]) & np.isfinite(y)
        if m.sum() < 200:
            continue
        q = np.quantile(y[m], [0.05, 0.25, 0.5, 0.75, 0.95])
        out.append({'id': f'{name}|{i}', 'band': name, 'x_lo': f'{edges[i]:.4g}', 'x_hi': f'{edges[i + 1]:.4g}',
                    'x_mid': f'{float(np.median(x[m])):.4g}', 'p05': f'{q[0]:.2f}', 'p25': f'{q[1]:.2f}', 'p50': f'{q[2]:.2f}',
                    'p75': f'{q[3]:.2f}', 'p95': f'{q[4]:.2f}', 'n': int(m.sum())})
    return out


B = bands('gstar_by_compute', 'compute_share_2025', 'Gstar_2025', np.geomspace(1.0, 66.0, 25))
B += bands('score_by_capacity', 'kappa_abs', 'R2036_net', np.round(np.arange(5, 22.01, 1), 3), 100.0)
write('bands.csv', B, ['id', 'band', 'x_lo', 'x_hi', 'x_mid', 'p05', 'p25', 'p50', 'p75', 'p95', 'n'])
below30 = float((D['Gstar_2025'] < 30).mean())
assert abs(100 * below30 - num(mac('StGstarBelowThirty'))) < 0.5

# ------------------------------------------------------------------------------------------------- levels
LV = []
BASIS = {'net': 'Central', 'ub': 'All S&M buys growth', 'lb': 'No S&M buys growth'}
for key, v in J['levels'].items():
    b, y = key.split('.R_')
    LV.append({'id': f'{BASIS[b]}|{y}', 'basis': BASIS[b], 'year': y, 'central': f"{100 * v['central']:.1f}",
               'paper_lo': f"{100 * v['paper_anchor_interval_90'][0]:.1f}", 'paper_hi': f"{100 * v['paper_anchor_interval_90'][1]:.1f}",
               'p05': f"{100 * v['lhs_p05']:.1f}", 'p95': f"{100 * v['lhs_p95']:.1f}", 'box_min': f"{100 * v['box_min']:.1f}",
               'box_max': f"{100 * v['box_max']:.1f}", 'share_in_paper': f"{v['share_in_paper_interval_uniform']:.3f}"})
write('levels.csv', LV, ['id', 'basis', 'year', 'central', 'paper_lo', 'paper_hi', 'p05', 'p95', 'box_min', 'box_max', 'share_in_paper'])

# --------------------------------------------------------------------------------------------- Sobol, swings
GROUP = {'execution': 'Execution: pace and success of change', 'market_growth': 'Market growth', 'anchor': 'Starting margin (anchor firms)',
         'capital': 'Capital needs', 'pass_through': 'Savings passed to customers', 'compute': 'AI compute cost',
         'tax': 'Cash tax rate', 'accountability': 'Accountability floor (audit, SOX)', 'ai_failure': 'AI errors and failures',
         'maintenance': 'Upkeep of AI builds', 'security': 'Security', 'fees': 'Payment fees', 'ancillary': 'Other AI running costs',
         'surplus': 'Growth surplus (all S&M bound only)', 'discount': 'Discount rate', 'maint_base': 'Maintenance level of selling spend'}
SO = []
for out_key, out_label in [('net.R_2036', '2036 score'), ('Gstar_2025', 'Rule-of-100 growth threshold')]:
    for g, v in J['sobol']['outputs'][out_key]['groups'].items():
        if g == 'fullcost_target':      # the union of the cost groups below it; shown through its parts
            continue
        SO.append({'id': f'{out_label}|{g}', 'output': out_label, 'group': GROUP[g], 'st': f"{max(v['ST'], 0):.3f}",
                   'st_lo': f"{max(v['ST_ci'][0], 0):.3f}", 'st_hi': f"{max(v['ST_ci'][1], 0):.3f}", 's1': f"{v['S1']:.3f}"})
write('sobol.csv', SO, ['id', 'output', 'group', 'st', 'st_lo', 'st_hi', 's1'])

SW = []
cen_g = J['group_swings']['Gstar_2025']
cen_r = J['group_swings']['net.R_2036']
for g in ['compute', 'tax', 'ai_failure', 'accountability', 'security', 'maintenance', 'fees', 'ancillary']:
    a, b = cen_g[g], cen_r[g]
    SW.append({'id': g, 'group': GROUP[g], 'kind': 'compute' if g == 'compute' else 'cost floor',
               'gstar_low': f"{100 * a['low']:.2f}", 'gstar_high': f"{100 * a['high']:.2f}", 'gstar_swing': f"{100 * a['swing']:.2f}",
               'score_low': f"{100 * b['low']:.2f}", 'score_high': f"{100 * b['high']:.2f}", 'score_swing': f"{100 * b['swing']:.2f}"})
write('swings.csv', SW, ['id', 'group', 'kind', 'gstar_low', 'gstar_high', 'gstar_swing', 'score_low', 'score_high', 'score_swing'])

# --------------------------------------------------------------------------------------------------- pace
PACE = [{'year': y, 'central_realized': mac(f'PaceCen{s}'), 'fast_realized': mac(f'PaceFast{s}'), 'central_embedded': mac(f'CenEmb{s}')}
        for y, s in [('2028', 'Eight'), ('2031', 'One'), ('2036', 'Six')]]
write('pace.csv', PACE, ['year', 'central_realized', 'fast_realized', 'central_embedded'])

# ------------------------------------------------------------------------------------------------- claims
TESTS = {t['tid']: t for c in J['claims'] for t in c['tests']}
AMIN = {a['tid']: a for a in J['amin']['tests']}
CLAIMS = [  # (test id, the claim in plain words, conditions held, unit kind, what the result means for a reader)
    ('C1.full', 'A cash score of 100 needs market growth above 30% a year', 'All inputs move', 'pct',
     'Usually true, not always: very cheap compute or favorable costs together can bring the threshold below 30%.'),
    ('C1.cond', 'The same, with compute at 6% of revenue', 'Compute 6%, fixed prices, no capital', 'pct',
     'Below 30% only when tax, the accountability floor and AI failure costs are all near their favorable ends.'),
    ('C2.full', 'The threshold stays above 30% in 2028, 2031 and 2036', 'All inputs move', 'pct',
     'As for the first row: it depends on the compute path.'),
    ('C3.full.net', 'Passing savings to customers raises every threshold', 'All inputs move', 'pts',
     'Not where compute costs nearly as much as the labor it replaces; there full automation costs more than today.'),
    ('P1.full.net', 'No Rule of 100 on the central path by 2036', 'All inputs move', 'pts',
     'Holds in every world tested: the best score found is below 100.'),
    ('P2b.full.net', 'Even a completed program stays below 100 in 2036', 'All inputs move', 'pts',
     'Crosses 100 only at the top of market growth with the most favorable costs.'),
    ('P3.full', 'Less than half the program realized by 2036', 'All inputs move', 'pct',
     'True at the central pace; a firm that changes faster can realize much more.'),
    ('P3b.full', 'The program is still running in 2036', 'All inputs move', 'year',
     'Fast execution can finish before 2036, as the paper\'s fast case does.'),
    ('P4.full.net', 'The central path rises from 2028 to 2036', 'All inputs move', 'pts',
     'Can dip between horizons if frontier-only work grows over time.'),
    ('P6.full', 'The central path lies between its two spend-basis bounds', 'All inputs move', 'pts', 'Holds in every world tested.'),
    ('B1.full.net', 'Yearly gains overtake transition costs before payback', 'All inputs move', 'yrs', 'Holds in every world tested.'),
    ('B2.full.net', 'No payback within five years', 'All inputs move', 'yrs',
     'Fast execution or favorable compute paths can pay back sooner.'),
    ('B2.B.net', 'The same, at central execution', 'Central execution, fixed prices, no capital', 'yrs',
     'Below five years only on compute paths that start high and fall steeply.'),
    ('B4.full.net', 'Lifetime gains are worth more than the transition costs', 'All inputs move', 'x',
     'Slow execution can leave the gains below the costs, as the paper\'s slow case does.'),
    ('B4.B.net', 'The same, at central execution', 'Central execution, fixed prices, no capital', 'x', 'Holds in every world tested.'),
    ('R1.full', 'A Rule of 1000 is not a steady state', 'All inputs move', 'x', 'Holds in every world tested.'),
    ('L1.full.net', 'The growth engine beats the back-office cut at one of six positions', 'Maintenance level drawn', 'int',
     'Zero or one position, depending on the maintenance level of selling spend; the back office leads elsewhere.'),
    ('A1.Five', 'No AI-only control design on one provider passes', 'Accountability sub-box, 5% threshold', 'pct',
     'Holds in every world tested: shared failures of one model never fall far enough.'),
]


def fmtk(x, kind):
    if kind in ('pct', 'pts'):
        return f'{100 * x:.1f}' + ('%' if kind == 'pct' else '')
    if kind == 'year':
        return f'{x:.1f}'
    if kind in ('yrs', 'x'):
        return f'{x:.2f}'
    return f'{x:.0f}'


CL = []
for tid, claim, cond, kind, means in CLAIMS:
    if tid in AMIN:
        a = AMIN[tid]
        thr = float(a['threshold'].rstrip('%')) / 100
        ok, cen, lo, hi, share = a['holds_everywhere'], thr + a['margin_central'], a['quantity']['min'], a['quantity']['max'], a['share_holds_uniform']
    else:
        t = TESTS[tid]
        q = t['quantity']
        ok, cen, lo, hi, share = t['holds_everywhere'], q['central'], q['min'], q['max'], t['share_holds_uniform']
    agree = J2['seed_comparison']['tests'].get(tid, {}).get('agree')
    CL.append({'test_id': tid, 'claim': claim, 'conditions': cond, 'result': 'Holds everywhere' if ok else 'Fails somewhere',
               'central': fmtk(cen, kind), 'lowest': fmtk(lo, kind), 'highest': fmtk(hi, kind),
               'share_holding': f'{share:.3f}', 'second_seed_agrees': {True: 'yes', False: 'no', None: 'not compared'}[agree], 'meaning': means})
write('claims.csv', CL, ['test_id', 'claim', 'conditions', 'result', 'central', 'lowest', 'highest', 'share_holding',
                         'second_seed_agrees', 'meaning'])
n_hold = sum(r['result'] == 'Holds everywhere' for r in CL)
assert str(n_hold) == mac('StClaimsHold') and str(len(CL)) == mac('StClaimsRows')

AM = []
for tid, a in AMIN.items():
    q = a['quantity']
    AM.append({'test_id': tid, 'threshold': a['threshold'], 'claim': a['claim'], 'result': 'Holds everywhere' if a['holds_everywhere'] else 'Fails somewhere',
               'share_holding': f"{a['share_holds_uniform']:.3f}", 'points': a['n_points'], 'no_design_points': q.get('n_inf', '')})
write('amin.csv', AM, ['test_id', 'threshold', 'claim', 'result', 'share_holding', 'points', 'no_design_points'])
no_design = {AMIN[t]['threshold']: AMIN[t]['quantity'].get('n_inf') for t in ('A4.Five', 'A4.One')}

# --------------------------------------------------------------------------------------------------- meta
sc = J2['seed_comparison']['tests']
n_agree = sum(v['agree'] for v in sc.values())
META = [{'draws_per_seed': N, 'corners': J['design']['n_corners'], 'points_per_seed': N + J['design']['n_corners'],
         'dimensions': len(J['dims']), 'sobol_base': J['sobol']['N'], 'sobol_evaluations': J['sobol']['n_evaluations'],
         'search_budget': J['meta']['args']['search_budget'], 'amin_points': AMIN['A1.Five']['n_points'],
         'reproduction_checks': len(J['reproduction']['checks']), 'reproduction_passed': int(J['reproduction']['all_passed']),
         'seed_tests': len(sc), 'seed_tests_agree': n_agree, 'seed1': J['design']['seed'], 'seed2': J2['design']['seed'],
         'cores': J['meta']['cpu_count'], 'run_date': J['meta']['created'][:10], 'config': J['meta']['config_hash']}]
# meta: the run's size is quoted through facts.csv

# -------------------------------------------------------------------------------------------------- facts
F = []


def fact(key, display, src, note='', macro=''):
    F.append({'key': key, 'display': display, 'macro': macro, 'source': src, 'note': note})


def fm(key, name, src, suffix='', note=''):
    fact(key, mac(name) + suffix, src, note, '\\' + name)


# levers and positions (Paper 1 Section 7.5; the companion paper's four-lever ranking)
fact('n_positions', mac('lpNPositions'), S['sec:levers-position'], macro='\\lpNPositions')
fact('eng_first', str(RB['n_eng_first_netted']), S['companion'], 'positions where engineering ranks first, central basis')
fact('ga_second', str(second_ga_net), S['companion'], 'positions where the back-office (G&A) cut ranks second, central basis')
fact('cor_third', str(third_cor_net), S['companion'], 'positions where cost of revenue ranks third, central basis')
fm('ga_over_ge', 'lpNGACutFirstNet', S['sec:levers-position'])
fm('ge_first_all', 'lpNGEFirstAllSM', S['sec:levers-position'])
fm('ge_first_none', 'lpNGEFirstNoSM', S['sec:levers-position'])
fm('ge_lead_lo', 'StLeverMin', S['supp:stress'])
fm('ge_lead_hi', 'StLeverMax', S['supp:stress'])
fm('lever_count_share', 'StLeverOneShare', S['supp:stress'], '%')
fact('lever_x', '10%', S['companion'], 'the proportional saving at which the four levers are compared (code/playbook/run_archetypes.py)')
fm('sm_maint', 'lpMaintBase', S['sec:levers-position'], '%')
fm('ratio_lo', 'lpRatioMin', S['sec:levers-position'])
fm('ratio_hi', 'lpRatioMax', S['sec:levers-position'])
fact('eng_pts_lo', f'{min(eng_pts):.2f}', S['companion'], 'points from a 10% saving in engineering, lowest of six positions')
fact('eng_pts_hi', f'{max(eng_pts):.2f}', S['companion'], 'highest of six positions')
fact('ga_pts_lo', f'{min(ga_pts):.2f}', S['companion']); fact('ga_pts_hi', f'{max(ga_pts):.2f}', S['companion'])
fact('cor_pts_lo', f'{min(cor_pts):.2f}', S['companion']); fact('cor_pts_hi', f'{max(cor_pts):.2f}', S['companion'])
fact('gc_eng', gc_pts['Engineering (R&D)'], S['companion'], 'growth corner'); fact('gc_ge', gc_pts['Growth engine (S&M)'], S['companion'])
fact('gc_ga', gc_pts['Back office (G&A)'], S['companion'])
fact('cap_hurdle_lo', f'{min(hurdles):.2f}', S['sec:levers-position'], 'g + delta at delta = 0.25, Table 7')
fact('cap_hurdle_hi', f'{max(hurdles):.2f}', S['sec:levers-position'])
fact('cap_delta', '0.25', S['sec:levers-position'], 'replacement rate of compute capital in Table 7')
# the path (Section 7.3)
for k, nme in [('r28', 'CenREight'), ('r31', 'CenROne'), ('r36', 'CenRSix'), ('r36_net', 'CenRSixNet'), ('r36_all', 'CenRSixAllSM'),
               ('r36_none', 'CenRSixNoSM'), ('target36', 'CenTargetSix'), ('r36_phi5', 'CenRPhiHalfSix'), ('r36_phi7', 'CenRPhiSevenSix'),
               ('dip28', 'CenDipEight'), ('dip36', 'CenDipSix'), ('dip_fast', 'PaceDipFast'), ('m0_36', 'CenMzeroSix'),
               ('rise28', 'CenRiseEight')]:
    fm(k, nme, S['sec:horizons-ranges'])
fm('g_central', 'CenG', S['sec:horizons-ranges'], '%')
fm('r36_lo', 'CenRSixLo', S['sec:horizons-ranges']); fm('r36_hi', 'CenRSixHi', S['sec:horizons-ranges'])
for k, nme in [('p05', 'StNetSixPFive'), ('p95', 'StNetSixPNinetyFive'), ('r36_min', 'StNetSixMin'), ('r36_max', 'StNetSixMax')]:
    fm(k, nme, S['supp:stress'])
fm('in_paper', 'StNetSixInPaper', S['supp:stress'], '%')
fm('p95_ci_lo', 'StNetSixPNinetyFiveCiLo', S['supp:stress']); fm('p95_ci_hi', 'StNetSixPNinetyFiveCiHi', S['supp:stress'])
fm('g_band_lo', 'GBandLo', S['sec:horizons-ranges'], '%'); fm('g_band_hi', 'GBandHi', S['sec:horizons-ranges'], '%')
fm('torn_g_lo', 'TornGSixLo', S['sec:horizons-ranges']); fm('torn_g_hi', 'TornGSixHi', S['sec:horizons-ranges'])
fm('torn_slow', 'TornPaceSixLo', S['sec:horizons-ranges']) if 'TornPaceSixLo' in MAC else None
fm('torn_fast', 'TornPaceSixHi', S['sec:horizons-ranges']) if 'TornPaceSixHi' in MAC else None
# pace and execution
for k, nme in [('pace28', 'PaceCenEight'), ('pace31', 'PaceCenOne'), ('pace36', 'PaceCenSix'), ('fast28', 'PaceFastEight'),
               ('fast31', 'PaceFastOne'), ('fast36', 'PaceFastSix'), ('emb36', 'CenEmbSix'), ('cap_cen', 'PaceCapCen'),
               ('cap_slow', 'PaceCapSlow'), ('cap_fast', 'PaceCapFast'), ('dip1_share', 'VarDipOneShare'), ('dip2_share', 'VarDipTwoShare')]:
    fm(k, nme, S['sec:horizons-ranges'], '%')
fm('fast_done', 'PaceFastDone', S['sec:horizons-ranges'])
fm('n_proc', 'PaceNproc', S['sec:horizons-ranges'])
fm('real_lo', 'StRealMin', S['supp:stress'], '%'); fm('real_hi', 'StRealMax', S['supp:stress'], '%')
fm('cap_half', 'StCapHalf', S['supp:stress'], '%')
fm('yield', 'YieldModel', S['sec:horizons-ranges'])
# payback
for k, nme in [('pay_cross', 'PayCrossCen'), ('pay_back', 'PayBackCen'), ('pay_disc', 'PayBackDiscCen'), ('pay_fast', 'PayBackFast'),
               ('pay_fast_disc', 'PayBackDiscFast'), ('pay_hold3', 'PayHoldThreeCen'), ('pay_hold5', 'PayHoldFiveCen'),
               ('pay_ratio', 'PayRatioCen'), ('pay_done', 'PayDoneCen')]:
    fm(k, nme, S['sec:horizons-ranges'])
for k, nme in [('pay_npv', 'PayNpvCen'), ('pay_npv_slow', 'PayNpvSlow'), ('pay_exit5', 'PayExitFiveCen'), ('pay_exit_break', 'PayExitBreakCen')]:
    fm(k, nme, S['sec:horizons-ranges'], '%')
fm('disc_rate', 'acqRwAnnual', S['sec:horizons-ranges'])
fm('pay_cen_lo', 'StPayCenMin', S['supp:stress']); fm('pay_cen_hi', 'StPayCenMax', S['supp:stress'])
fm('pay_lo', 'StPayMin', S['supp:stress']); fm('pay_hi', 'StPayMax', S['supp:stress'])
fm('npv_lo', 'StNpvMin', S['supp:stress'], '%'); fm('npv_hi', 'StNpvMax', S['supp:stress'], '%')
fm('cum_max_cen', 'StCumMaxCen', S['supp:stress'])
qd = {q['key']: q for q in J['quantities']}
pb_full = [q for q in J['quantities'] if q['label'].startswith('Payback, full box')][0]
fact('pay_p05', f"{pb_full['lhs_p05']:.1f}", S['supp:stress'], 'payback over the whole box, 5th percentile of draws')
fact('pay_p95', f"{pb_full['lhs_p95']:.1f}", S['supp:stress'], '95th percentile')
# ceiling (Section 7.2)
for k, nme in [('gstar', 'GstarCenOne'), ('gstar_phi5', 'GstarPhiHalfOne'), ('gstar_phi7', 'GstarPhiSevenOne'),
               ('gstar28', 'GstarCenTwentyEight'), ('gstar31', 'GstarCenThirtyOne'), ('gstar36', 'GstarCenThirtySix'),
               ('cc_lo', 'CcLo'), ('cc_hi', 'CcHi'), ('cc_cen', 'CcCen'), ('gstar_cc_lo', 'GstarCcLo'), ('gstar_cc_hi', 'GstarCcHi'),
               ('cc28', 'CcCenTwentyEight'), ('cc31', 'CcCenThirtyOne'), ('cc36', 'CcCenThirtySix'), ('labor', 'CcLaborShare'),
               ('own5', 'OwnMarkupFive'), ('own15', 'OwnMarkupFifteen'), ('gstar_kdef', 'GstarKdefMedCen'),
               ('amin_lo', 'AminLo'), ('amin_hi', 'AminHi'), ('gstar_tau_lo', 'GstarTauLo'), ('gstar_tau_hi', 'GstarTauHi')]:
    fm(k, nme, S['sec:horizons-ceiling'], '%')
for k, nme in [('margin_cen', 'MarginCen'), ('ceil5', 'CeilCenFive'), ('ceil15', 'CeilCenFifteen'), ('ceil30', 'CeilCenThirty'),
               ('cfull_fav', 'CfullFav'), ('cfull_cen', 'CfullCen'), ('cfull_cons', 'CfullCons'), ('gd_tax', 'GdecTax'),
               ('gd_compute', 'GdecCompute'), ('gd_fees', 'GdecFees'), ('gd_acc', 'GdecAcc'), ('gd_full', 'GdecFull'),
               ('gd_mnt', 'GdecMnt'), ('gd_sec', 'GdecSec'), ('gd_err', 'GdecErr'), ('gd_anc', 'GdecAnc'), ('pull_lo', 'PullMultLo'),
               ('pull_hi', 'PullMultHi'), ('cc_year', 'CcYearSix'), ('itgc_apps', 'ItgcApps'), ('entry_score', 'EntryScore')]:
    fm(k, nme, S['sec:horizons-ceiling'])
fact('own_mult', '3.3', S['sec:horizons-ceiling'], 'vendor markup over market growth at which owned compute pays (Remark rem:owncompute)')
for k, nme in [('gstar_box_lo', 'StGstarMin'), ('gstar_box_hi', 'StGstarMax'), ('gstar_p05', 'StGstarPFive'), ('gstar_p95', 'StGstarPNinetyFive'),
               ('gstar_cc6_lo', 'StGstarCcSixMin'), ('gstar_cc6_hi', 'StGstarCcSixMax'), ('gstar_below30', 'StGstarBelowThirty'),
               ('cc_box_lo', 'StCcBoxMin'), ('cc_box_hi', 'StCcBoxMax')]:
    fm(k, nme, S['supp:stress'], '%')
fm('completed_max', 'StCompletedMax', S['supp:stress'])
# drivers (Sobol)
for k, nme in [('so_exec', 'StSobolExec'), ('so_exec_lo', 'StSobolExecLo'), ('so_exec_hi', 'StSobolExecHi'), ('so_g', 'StSobolG'),
               ('so_cc', 'StSobolCc'), ('so_cc_lo', 'StSobolCcLo'), ('so_cc_hi', 'StSobolCcHi')]:
    fm(k, nme, S['supp:stress'])
fact('so_exec_pct', f"{100 * num(mac('StSobolExec')):.0f}%", S['supp:stress'], 'the total-order index as a share')
fact('so_g_pct', f"{100 * num(mac('StSobolG')):.0f}%", S['supp:stress'])
fact('so_cc_pct', f"{100 * num(mac('StSobolCc')):.0f}%", S['supp:stress'])
# accountability (Proposition 5, Section 7.2, Section 8.5)
for k, nme in [('floor5', 'AminFloor'), ('floor1', 'AminFloorOne'), ('floor_lo', 'AminFloorLo'), ('floor_hi', 'AminFloorHi')]:
    fm(k, nme, S['sec:horizons-ceiling'], '%')
fm('ai_only_min', 'StAiOnlyMin', S['supp:stress'], '%')
fact('no_design_5', f"{no_design['5%']:,}", S['supp:stress'], 'points of the accountability sub-box with no admissible design, 5% threshold')
fact('no_design_1', f"{no_design['1%']:,}", S['supp:stress'], '1% threshold')
fact('amin_points', f"{AMIN['A1.Five']['n_points']:,}", S['supp:stress'])
for k, nme in [('ga_small', 'GAsmall'), ('ga_mid', 'GAmid'), ('ga_large', 'GAlarge')]:
    fm(k, nme, S['sec:discussion-acc'], '%')
# measurement and empirics
fm('pass_fcf', 'VBridgePassFcf', S['sec:data'], '%'); fm('pass_cash', 'VBridgePassCash', S['sec:data'], '%')
fm('slope_lo', 'ScPsiOpTypLo', S['sec:empirics']); fm('slope_hi', 'ScPsiOpTypHi', S['sec:empirics'])
fm('top_fall', 'TopFallOpEone', S['sec:empirics']); fm('top_fall_cash', 'TopFallCashEone', S['sec:empirics'])
fm('acq_gaap', 'acqRGaapTwentyFive', S['sec:acquired-growth']); fm('acq_lo', 'acqConvLo', S['sec:acquired-growth'])
fm('acq_hi', 'acqConvHi', S['sec:acquired-growth'])
fm('rev_op', 'RevealedOpMed', S['sec:horizons-ranges'])
# run
fact('draws', f'{N:,}', S['supp:stress'], 'Latin-hypercube draws per seed')
fact('dims', str(len(J['dims'])), S['supp:stress'])
fact('seed_agree', str(n_agree), 'Stress-test run: notes/mc_results_2026-11-03_1m/seed2/mc_claims.json seed_comparison', 'tests with the same verdict under the second seed')
fact('seed_tests', str(len(sc)), 'Stress-test run: notes/mc_results_2026-11-03_1m/seed2/mc_claims.json seed_comparison')
fm('seed_maxdiff', 'StSeedTwoMaxDiff', S['supp:stress'])
fm('mc_se', 'StMcShareSeMax', S['supp:stress'])
fact('claims_hold', str(n_hold), S['supp:stress'], 'rows of Table S18 that hold everywhere')
fact('claims_rows', str(len(CL)), S['supp:stress'])
fm('repro', 'StReproChecks', S['supp:stress'])
fact('sobol_evals', f"{J['sobol']['n_evaluations']:,}", S['supp:stress'])
fact('corners', f"{J['design']['n_corners']:,}", S['supp:stress'])
fact('sobol_base', f"{J['sobol']['N']:,}", S['supp:stress'])
# literals the page's sentences need: periods, references and values the paper writes in words or digits without a macro
for k, v, src, note in [
        ('y25', '2025', S['sec:horizons-ceiling'], 'price year of the ceiling'), ('y28', '2028', S['sec:horizons-ranges'], ''),
        ('y31', '2031', S['sec:horizons-ranges'], ''), ('y36', '2036', S['sec:horizons-ranges'], ''),
        ('y2325', '2023–25', S['sec:levers-position'], 'sample years of the positions and of the top-tail anchor'),
        ('y1619', '2016–19', S['sec:empirics'], ''), ('y1025', '2010–25', S['sec:empirics'], ''),
        ('spec_share', '90%', S['sec:empirics'], 'share of the defensible analysis choices of the specification curve (Supplement S11)'),
        ('pct95', '95th', S['sec:empirics'], 'percentile of the score'),
        ('ref_payback', '5', S['sec:horizons-ranges'], 'the five-year cash-payback test the paper applies'),
        ('ref_g', '30%', S['supp:stress'], 'market growth up to which the claim says the cash ceiling stays below 100'),
        ('rule100', '100', S['sec:horizons-ceiling'], 'a cash-basis Rule-of-40 score of 100'),
        ('rev_1b', '$1 billion', S['sec:horizons-ceiling'], 'revenue of the firm in the accountability-floor example'),
        ('g5', '5%', S['sec:horizons-ceiling'], 'market growth in the own-compute rule'), ('g15', '15%', S['sec:horizons-ceiling'], ''),
        ('metr_days', '131 days', S['sec:discussion-limits'], 'doubling time of the task length agents complete half the time (METR)'),
        ('y22', '2022', S['sec:horizons-ranges'], 'fiscal years of the cost-program comparison'), ('y24', '2024', S['sec:horizons-ranges'], ''),
        ('rev_100m', '$100 million', S['sec:horizons-ranges'], 'revenue floor of that comparison'),
        ('rule40', '40', S['sec:data'], 'the Rule-of-40 bar'), ('sox404', 'Section 404', S['sec:horizons-ceiling'], 'Sarbanes-Oxley Act section on internal control'), ('ci_level', '95%', S['supp:stress'], 'level of the Sobol intervals'),
        ('ref_s1', 'Paper 1, Section 1', '', ''), ('ref_s4', 'Paper 1, Section 4', '', ''), ('ref_s5', 'Paper 1, Section 5', '', ''),
        ('ref_s6', 'Paper 1, Section 6', '', ''), ('ref_s72', 'Paper 1, Section 7.2', '', ''), ('ref_s73', 'Paper 1, Section 7.3', '', ''),
        ('ref_s75', 'Paper 1, Section 7.5 and Table 7', '', ''), ('ref_s74', 'Paper 1, Section 7.4', '', ''), ('ref_s81', 'Paper 1, Section 8.1', '', ''),
        ('ref_s82', 'Paper 1, Section 8.2', '', ''), ('ref_s83', 'Paper 1, Section 8.3', '', ''), ('ref_s84', 'Paper 1, Section 8.4', '', ''),
        ('ref_s85', 'Paper 1, Section 8.5', '', ''), ('ref_s86', 'Paper 1, Section 8.6', '', ''), ('ref_s9', 'Paper 1, Section 9', '', ''),
        ('ref_c3', 'Paper 1, Corollary 3', '', ''), ('ref_p4', 'Paper 1, Proposition 4', '', ''),
        ('ref_p5', 'Paper 1, Proposition 5', '', ''), ('ref_p9', 'Paper 1, Proposition 9', '', ''),
        ('ref_s10', 'Supplementary Appendix, Section S10', '', ''),
        ('ref_comp', 'Companion paper (in preparation), as cited in Paper 1, Section 7.5', '', '')]:
    fact(k, v, src or v, note)
write('facts.csv', F, ['key', 'display', 'macro', 'source', 'note'])
keys = [f['key'] for f in F]
assert len(keys) == len(set(keys)), 'duplicate fact keys'
