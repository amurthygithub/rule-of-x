#!/usr/bin/env python3
"""New analyses for the business dashboard's open questions (3 November 2026). Not part of Paper 1.

Two score paths computed with Paper 1's own calibration, executed unchanged in a shadow tree (as code/mc_claims.py does;
nothing in the repository is overwritten):

(1) The do-nothing path. Paper 1's pass-through scenario (central_path, phi > 0) lets the industry realize the same
    share s of its automation program as the firm and pass the share phi of every unit-cost saving to price:
    p = 1 - phi s S_h, with S_h = C0 - K_h the anchor's unit-cost saving at horizon h. A firm that does not automate
    keeps its unit cost C0 and faces the same price, so its after-tax intercept is
        m0_none(h) = (1 - tau) [1 - f - C0 / (1 - phi s_r S_h)],
    the paper's formula with the firm's own share set to zero and the rivals' share s_r in the price. At s_r = 0 it is
    the anchor intercept. Its durable score is m0_none + (1 - k) G, with no in-flight dip. Rivals execute at the central
    or the fast pace; phi takes the paper's scenario values 0, 0.5 and 0.7. Demand and market growth are held as in the
    paper's path.
(2) The path of a typical company. The paper's path starts from the top tail (firm-years at or above the 95th
    percentile of the 2023-25 cash score). The typical company here is the paper's own typical $1-5 billion company
    (Section 7.2; calibrate_horizons.py block B8: medians of 2023-25 core firm-years with revenue of $1-5 billion), with
    its netted intercept and its own median growth, on the same program, target, pace and fixed prices; k = 0 as in the
    paper's path, and at its own capital intensity as a sensitivity.

Writes notes/open_questions/paths.json and notes/mc_results_2026-11-03_1m/dashboard/paths.csv.
Run from anywhere:  python3 code/biz_open_questions.py
"""
import csv
import importlib.util
import json
import os
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('mc_claims', os.path.join(BASE, 'code', 'mc_claims.py'))
mc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc)
g = mc.load_calibration(os.path.join(tempfile.mkdtemp(prefix='biz_shadow_'), 'tree'))
assert all(g['_mc_byte_identical'][k] for k in ('sections/tables/tab_calib.tex', 'sections/tables/tab_tornado.tex'))

central_path, CEIL_H, HZ, anchor, TYP = g['central_path'], g['CEIL_H'], g['HZ'], g['anchor'], g['R2']['typical_1to5bn']
payback, PACE = g['payback'], g['PACE']
B = g['CENTRAL_BASIS']
H = ['2028', '2031', '2036']
PHI = [0.0, 0.5, 0.7]
m0A = anchor['m0_' + B][1]

# reproduce the paper's central path first (Section 7.3: 44, 49, 58; net of the dip 40, 45, 53)
ref = central_path()
for h, want in zip(H, (0.44111016596875363, 0.4907068747867224, 0.5776651526469216)):
    assert abs(ref[h]['R'] - want) < 1e-12, (h, ref[h]['R'])


def do_nothing(phi, rival_pace):
    rivals = central_path(pace_case=rival_pace)
    out = {}
    for h in H:
        c = CEIL_H[h]['central']
        C0 = 1 - c['f'] - m0A / (1 - c['tau'])
        S_h = C0 - (1 - c['f'] - c['base'] / (1 - c['tau']))
        s_r = rivals[h]['s']
        m0 = (1 - c['tau']) * (1 - c['f'] - C0 / (1 - phi * s_r * S_h))
        G = rivals[h]['G']
        out[h] = dict(rival_share=s_r, price=1 - phi * s_r * S_h, m0=m0, R=m0 + G)
    return out


def adopt_vs_rivals(phi, rival_pace):
    """A firm that automates at the central pace while rivals realize their share at rival_pace:
    m0 = (1 - tau)[1 - f - (C0 - s_own S_h) / (1 - phi s_r S_h)], less its own in-flight dip, taken from the paper's
    pass-through path at the same phi (the dip is the cost of transitions toward the target net of pass-through)."""
    own, rivals = central_path(phi=phi), central_path(pace_case=rival_pace)
    out = {}
    for h in H:
        c = CEIL_H[h]['central']
        C0 = 1 - c['f'] - m0A / (1 - c['tau'])
        S_h = C0 - (1 - c['f'] - c['base'] / (1 - c['tau']))
        m0 = (1 - c['tau']) * (1 - c['f'] - (C0 - own[h]['s'] * S_h) / (1 - phi * rivals[h]['s'] * S_h))
        out[h] = dict(R=m0 + own[h]['G'], R_net=m0 + own[h]['G'] - own[h]['dip'])
    return out


R = {'anchor_m0': m0A, 'G': ref['2036']['G'], 'do_nothing': {}, 'adopter': {}, 'adopter_rivals_fast': {}, 'typical': {}}
for phi in PHI:
    a = central_path(phi=phi)
    R['adopter'][f'{phi:.1f}'] = {h: dict(R=a[h]['R'], R_net=a[h]['R_net'], dip=a[h]['dip'], s=a[h]['s']) for h in H}
    for rp in ('central', 'fast'):
        R['do_nothing'][f'{phi:.1f}|{rp}'] = do_nothing(phi, rp)
    R['adopter_rivals_fast'][f'{phi:.1f}'] = adopt_vs_rivals(phi, 'fast')
    chk = adopt_vs_rivals(phi, 'central')                     # same pace as rivals: the paper's own path
    assert all(abs(chk[h]['R'] - a[h]['R']) < 1e-12 and abs(chk[h]['R_net'] - a[h]['R_net']) < 1e-12 for h in H)
assert all(abs(R['do_nothing'][f'0.0|{rp}'][h]['m0'] - m0A) < 1e-12 for rp in ('central', 'fast') for h in H)

Gt = {h: TYP['g'] for h in H}
t0 = central_path(m0A=TYP['m0_net'], G=Gt)
tk = central_path(m0A=TYP['m0_net'], G=Gt, k_pre=TYP['k'], psi=0.0)
R['typical'] = dict(m0A=TYP['m0_net'], g=TYP['g'], k=TYP['k'], n=TYP['n'], firms=TYP['firms'],
                    R2025=TYP['m0_net'] + TYP['g'],
                    path={h: dict(R=t0[h]['R'], R_net=t0[h]['R_net'], dip=t0[h]['dip'], target=t0[h]['target']) for h in H},
                    path_own_k={h: dict(R=tk[h]['R'], R_net=tk[h]['R_net']) for h in H},
                    payback=payback(t0, PACE['central']), payback_anchor=payback(ref, PACE['central']))
R['anchor_R2025'] = m0A + ref['2036']['G']
# grids for the dashboard's heatmaps (3 Nov 2026, 19:21 request)
G100 = g['G100_central']
CC_G = [0.012, 0.03, 0.06, 0.12, 0.24, 0.40, 0.60]
K_G = [-0.3, 0.0, 0.25, 0.5, 0.75]
R['grids'] = {
    'gstar_cc_k': {'cc': CC_G, 'k': K_G, 'G': [[G100(cc)[0] / (1 - k_) for k_ in K_G] for cc in CC_G],
                   'note': "Paper 1's threshold at the central full-cost structure, G100_central(cc)[0] / (1 - k) (psi = 0)"},
    'gap_phi_pace': {'phi': [0.0, 0.25, 0.5, 0.7], 'pace': ['slow', 'central', 'fast'],
                     'gap': [[adopt_vs_rivals(ph, rp)['2036']['R_net'] - do_nothing(ph, rp)['2036']['R'] for rp in ('slow', 'central', 'fast')]
                             for ph in (0.0, 0.25, 0.5, 0.7)],
                     'none': [[do_nothing(ph, rp)['2036']['R'] for rp in ('slow', 'central', 'fast')] for ph in (0.0, 0.25, 0.5, 0.7)],
                     'note': '2036: automating at the central pace (net of its dip) minus doing nothing, rivals at each pace'}}
# the same gap with the automating firm's in-flight dip held at its fixed-price value (Supplement S12.2 sensitivity: the
# paper's convention values the transitions at the long-run target with the share passed, whatever the rivals' pace)
_dip0 = central_path(phi=0.0)['2036']['dip']
R['grids']['gap_phi_pace']['gap_dip_fixed'] = [[adopt_vs_rivals(ph, rp)['2036']['R_net'] + central_path(phi=ph)['2036']['dip'] - _dip0
                                                 - do_nothing(ph, rp)['2036']['R'] for rp in ('slow', 'central', 'fast')]
                                                for ph in (0.0, 0.25, 0.5, 0.7)]
gg = R['grids']['gstar_cc_k']['G']
assert abs(gg[CC_G.index(0.06)][K_G.index(0.0)] - 0.325352356655251) < 1e-12          # the paper's 32.5%
assert abs(gg[CC_G.index(0.06)][K_G.index(-0.3)] - 0.325352356655251 / 1.3) < 1e-12     # 25% at k = -0.3 (Section 7.2)
R['anchor_R_observed'] = anchor['R'][1]            # median observed cash score of the top-tail anchor firm-years
R['typical']['R_observed'] = TYP['R_fcf_sbc']       # median observed cash score of the typical firm-years

os.makedirs(os.path.join(BASE, 'notes', 'open_questions'), exist_ok=True)
json.dump(R, open(os.path.join(BASE, 'notes', 'open_questions', 'paths.json'), 'w'), indent=1, default=float)

rows = []
def add(scen, label, h, v, note=''):
    rows.append({'id': f'{scen}|{h}', 'scenario': scen, 'label': label, 'year': h, 'score': f'{100 * v:.1f}', 'note': note})

labels = {
    'adopt_fixed': 'Automates (central execution), prices fixed, net of changes in flight',
    'adopt_phi5': 'Automates, half of savings passed to price, net of changes in flight',
    'none_fixed': 'Does nothing, prices fixed',
    'none_phi5_central': 'Does nothing, rivals automate at the central pace, half of savings passed to price',
    'none_phi5_fast': 'Does nothing, rivals automate fast, half of savings passed to price',
    'none_phi7_fast': 'Does nothing, rivals automate fast, seven tenths passed to price',
    'adopt_phi5_rfast': 'Automates at the central pace while rivals automate fast, half passed to price, net of changes in flight',
    'adopt_phi7_rfast': 'Automates at the central pace while rivals automate fast, seven tenths passed to price, net of changes in flight',
    'typical_net': 'Typical $1-5 billion company, central execution, net of changes in flight',
    'typical_durable': 'Typical $1-5 billion company, durable score',
}
for scen in labels:
    if scen.startswith('typical'):
        add(scen, labels[scen], '2025', R['typical']['R2025'])
    else:
        add(scen, labels[scen], '2025', R['anchor_R2025'])
for h in H:
    add('adopt_fixed', labels['adopt_fixed'], h, R['adopter']['0.0'][h]['R_net'])
    add('adopt_phi5', labels['adopt_phi5'], h, R['adopter']['0.5'][h]['R_net'])
    add('none_fixed', labels['none_fixed'], h, R['do_nothing']['0.0|central'][h]['R'])
    add('none_phi5_central', labels['none_phi5_central'], h, R['do_nothing']['0.5|central'][h]['R'])
    add('none_phi5_fast', labels['none_phi5_fast'], h, R['do_nothing']['0.5|fast'][h]['R'])
    add('none_phi7_fast', labels['none_phi7_fast'], h, R['do_nothing']['0.7|fast'][h]['R'])
    add('adopt_phi5_rfast', labels['adopt_phi5_rfast'], h, R['adopter_rivals_fast']['0.5'][h]['R_net'])
    add('adopt_phi7_rfast', labels['adopt_phi7_rfast'], h, R['adopter_rivals_fast']['0.7'][h]['R_net'])
    add('typical_net', labels['typical_net'], h, R['typical']['path'][h]['R_net'])
    add('typical_durable', labels['typical_durable'], h, R['typical']['path'][h]['R'])
with open(os.path.join(BASE, 'notes', 'mc_results_2026-11-03_1m', 'dashboard', 'paths.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=['id', 'scenario', 'label', 'year', 'score', 'note'], lineterminator='\n')
    w.writeheader(); w.writerows(rows)

pp = lambda x: f'{100 * x:.1f}'
print('anchor R2025', pp(R['anchor_R2025']), 'typical R2025', pp(R['typical']['R2025']), 'typical m0', pp(TYP['m0_net']), 'g', pp(TYP['g']), 'k', round(TYP['k'], 3))
for phi in PHI:
    print(f'phi={phi}: adopter R_net', [pp(R['adopter'][f"{phi:.1f}"][h]['R_net']) for h in H],
          '| none central', [pp(R['do_nothing'][f"{phi:.1f}|central"][h]['R']) for h in H],
          '| none fast', [pp(R['do_nothing'][f"{phi:.1f}|fast"][h]['R']) for h in H],
          '| adopter, rivals fast', [pp(R['adopter_rivals_fast'][f"{phi:.1f}"][h]['R_net']) for h in H])
print('typical R', [pp(R['typical']['path'][h]['R']) for h in H], 'net', [pp(R['typical']['path'][h]['R_net']) for h in H],
      'own k', [pp(R['typical']['path_own_k'][h]['R']) for h in H])
print('payback typical', R['typical']['payback'], 'anchor', R['typical']['payback_anchor'])
