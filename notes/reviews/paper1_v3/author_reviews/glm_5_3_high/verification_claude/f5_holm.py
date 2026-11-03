"""GLM-F5 and GLM-M1: Holm counterfactuals recomputed from our stored p-values.

Inputs: notes/empirics_v3.json (family headline14B and the per-statistic bootstrap p-values) and
notes/calibration_anchor_v3.json (the anchor's p-values, the source code/paper1_macros.py uses).
Holm is applied per interval type (normal, percentile, basic). Romano-Wolf cannot be recomputed from
stored p-values (it needs the bootstrap draws), so it is not shown. Run from the repository root.
"""
import json

E = json.load(open('notes/empirics_v3.json'))
A = json.load(open('notes/calibration_anchor_v3.json'))['bootstrap']['E1']['Pi_lb_med']
fam = E['families']['headline14B']['contrasts']
EST = E['estimates']
TYPES = ('normal', 'percentile', 'basic')


def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for r, i in enumerate(o):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        adj[i] = run
    return adj


def p_est(stat, t, view='E1'):
    v = EST[stat][view].get('p_' + t)
    return 1.0 if v is None else v


keys = [c['key'] for c in fam]
STEEP, P95 = keys.index('psi_op_E1_2020_25_minus_2010_19'), keys.index('p95chg_op_E1')
# (0) the stored family uses 14 tests (the non-estimable T40 cash change counted at p = 1)
for t in TYPES:
    ps = [c['p_' + t] if c.get('p_' + t) is not None else 1.0 for c in fam]
    dev = max(abs(a - c['holm_' + t]) for a, c in zip(holm(ps), fam))
    print(f'(0) {t}: stored holm_* reproduced with 14 tests, max deviation {dev:.2e}')
# (1) M1: the anchor added to the family, two counts
print('\n(1) anchor Pi_lb added to family B')
print('    raw anchor p: ' + ', '.join(f"{t} {A['p_' + t]:.4g}" for t in TYPES)
      + '; from estimates: ' + ', '.join(f"{t} {p_est('anchor_p95_Pi_lb_med', t):.4g}" for t in TYPES))
for t in TYPES:
    p13 = [c['p_' + t] for c in fam if c.get('p_' + t) is not None] + [A['p_' + t]]
    p15 = [c['p_' + t] if c.get('p_' + t) is not None else 1.0 for c in fam] + [A['p_' + t]]
    print(f'    {t}: 13 estimable + anchor (14 tests, the printed macros) {holm(p13)[-1]:.3f};'
          f' 14 + anchor (15 tests, the family\'s own count) {holm(p15)[-1]:.3f}')
# (2) F5: the reviewer's counterfactual families
extra = {'anchor': None, 'T20_op': 'T_op_g20_change', 'T20_cash': 'T_cash_g20_change', 'T0_cash': 'T_cash_g00_change',
         'spend_ratio': 'spend_ratio', 'gap_slow_gm': 'gap_slow_gm', 'T0_op': 'T_op_g00_change'}
scen = [('published 14', []), ('+anchor (15)', ['anchor']), ('+anchor +T20 op/cash +T0 cash (18)', ['anchor', 'T20_op', 'T20_cash', 'T0_cash']),
        ('reviewer 20: +T20 op/cash +T0 cash +spend ratio +anchor +gap_slow_gm', ['T20_op', 'T20_cash', 'T0_cash', 'spend_ratio', 'anchor', 'gap_slow_gm']),
        ('+T20 op/cash +T0 op/cash (18, without the anchor)', ['T20_op', 'T20_cash', 'T0_op', 'T0_cash'])]
print('\n(2) Holm-adjusted p of the 2020-25 steepening and of the GAAP p95 decline (normal / percentile / basic)')
for name, add in scen:
    rows = {}
    for t in TYPES:
        ps = [c['p_' + t] if c.get('p_' + t) is not None else 1.0 for c in fam]
        ps += [A['p_' + t] if k == 'anchor' else p_est(extra[k], t) for k in add]
        h = holm(ps)
        rows[t] = (h[STEEP], h[P95], {k: h[14 + j] for j, k in enumerate(add)})
    print(f'    {name}: steepening ' + '/'.join(f'{rows[t][0]:.3f}' for t in TYPES)
          + '; p95 GAAP ' + '/'.join(f'{rows[t][1]:.3f}' for t in TYPES)
          + ('; anchor ' + '/'.join(f"{rows[t][2]['anchor']:.3f}" for t in TYPES) if 'anchor' in add else ''))
print('\n    raw p of the added statistics: ' + '; '.join(
    f"{k} " + '/'.join(f'{p_est(s, t):.4f}' for t in TYPES) for k, s in extra.items() if s))
# the reviewer's script reads the 'anchor' entry of the 20-member family from position 14, which there holds T20_op
for t in TYPES:
    ps = [c['p_' + t] if c.get('p_' + t) is not None else 1.0 for c in fam]
    order = ['T20_op', 'T20_cash', 'T0_cash', 'spend_ratio', 'anchor', 'gap_slow_gm']
    ps += [A['p_' + t] if k == 'anchor' else p_est(extra[k], t) for k in order]
    h = holm(ps)
    print(f'    20-member, {t}: position 14 (T20_op) {h[14]:.3f}; anchor (position 18) {h[18]:.3f}')
