"""GPT-M1: exact cone-to-frontier multiplier evaluated at the E1 growth values, both bases. Reads only the g column of data/panel_v3.csv."""
import json, numpy as np, pandas as pd
from scipy import optimize
g = pd.read_csv('/home/claude/paper/data/panel_v3.csv', usecols=['g']).g.values
FS = json.load(open('/home/claude/paper/notes/frontier_slope_v3.json'))['central']
grid = np.round(np.arange(0, 0.6001, 0.05), 10); chi = 0.9; W = 0.6
ls = lambda x, y: float(np.polyfit(x, y, 1)[0])
def cone_slope(ell, beta):
    m = 0.8 - (np.maximum(g, 0)/ell)**beta
    c = np.array([np.quantile(m[g >= g0], chi) for g0 in grid]); return ls(grid, c)
rows = []
for basis in ['op', 'cash']:
    b = abs(FS[basis]['E1']['est'])
    for a in (0.25, 0.30, 0.35, 0.45):
        be = 1/a
        ell = optimize.brentq(lambda l: cone_slope(l, be) + b, 0.2, 6)
        steep = be*W**(be-1)/ell**be
        S = ls(grid, grid**be); own_map = be*W**(be-1)*b/S
        rows.append((basis, a, b, ell, steep, steep/b, own_map, own_map/b))
for r in rows:
    print(f'{r[0]:4s} alpha={r[1]:.2f} b={r[2]:.4f}: ell via E1 F {r[3]:.4f}; steepest {r[4]:.3f} = {r[5]:.3f} b | paper exact-LS map (ell_psi) steepest {r[6]:.3f} = {r[7]:.3f} b')
st = [r[4] for r in rows if r[1] in (0.25, 0.45)]
print('E1-F implied steepest slope range over alpha .25-.45 and both bases:', round(min(st), 2), '-', round(max(st), 2), ' (paper PsiSteepLo/Hi 0.36-1.02, unused in text)')
