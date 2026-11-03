"""Firm-years with growth >= 40% in 2023-25 behind T(40%), E1 and E2."""
import sys; sys.path.insert(0, '.')
import lib
for vn in ['E1', 'E2']:
    v = lib.V[vn]; d = v[(v.period == '2023-25') & (v.g >= .4)][['name', 'year', 'g', 'm_op', 'm_fcf_sbc', 'flag25']].sort_values('m_op', ascending=False)
    print(vn); print(d.round(3).to_string())
