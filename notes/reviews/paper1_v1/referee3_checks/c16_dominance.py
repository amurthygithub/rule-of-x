"""Dominance-cone quantile frontier phi_chi(g) = chi-quantile of margin among firm-years with growth >= g (Section 5.1's
definition; Psi_chi of Definition 2), least-squares slope over the grid g in {0, 0.05, ..., 0.6}."""
import sys; sys.path.insert(0, '.')
import numpy as np, lib
grid = np.round(np.arange(0, 0.61, 0.05), 2)
for vn in ['E1', 'E2']:
    for m in ['m_op', 'm_fcf_sbc']:
        d = lib.V[vn][['g', m]].dropna()
        for chi in [0.9, 0.95]:
            phi = np.array([np.quantile(d.loc[d.g >= g0, m], chi) for g0 in grid]); n = [int((d.g >= g0).sum()) for g0 in grid]
            print(vn, m, 'chi', chi, 'phi at g=0,.2,.4,.6:', [round(100 * phi[i], 1) for i in [0, 4, 8, 12]], 'n:', [n[i] for i in [0, 4, 8, 12]],
                  'LS slope %.2f' % np.polyfit(grid, phi, 1)[0])
