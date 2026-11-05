"""GLM-M5: present value of gains over the transition dip, truncated at program completion.

code/calibrate_horizons.py writes notes/ and sections/tables/ when run, so run this ONLY on a scratch copy:
  git archive HEAD | tar -x -C <copy>;  python3 m5_payback_truncated.py <copy>
It executes <copy>/code/calibrate_horizons.py and re-evaluates its payback() for the central case with the
horizon T cut at the completion date (the stored ratio uses T = 200 years).
"""
import os, sys, runpy
import numpy as np
copy = sys.argv[1]
path = os.path.join(copy, 'code', 'calibrate_horizons.py')
sys.path.insert(0, os.path.join(copy, 'code'))
os.chdir(copy)
ns = runpy.run_path(path, run_name='__main__')
pb = ns['R2']['payback']['central']
print('stored-style central: ratio', pb['ratio'], 'complete_years', pb['complete_years'], 'npv', pb['npv_points_years'])
# re-evaluate gain and dip flows and truncate the PV integrals at completion
payback, central_path, PACE = ns['payback'], ns['central_path'], ns['PACE']
for T in [pb['complete_years'], 10.0, 20.0, 50.0, 200.0]:
    r = payback(central_path(pace_case='central'), PACE['central'], T=T)
    print(f'T={T:.2f}: pv_gain {r["pv_gain"]:.4f} pv_dip {r["pv_dip"]:.4f} ratio {r["ratio"]:.3f}')
