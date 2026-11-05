# Independent M5 check: my round-1 payback implementation (no repo imports), truncated at completion.
# Parameters exactly as round 1 / paper M 7.3 (verified then): rho=0.10, varpi=p_emb=0.70, bbar=0.67,
# Temb=Tpb=1.25, Tpar=0.17, clock=1.115, r=9.34%, anchor m0A=0.30597527, targets {2028:0.624,2031:0.658,2036:0.683}
import numpy as np, math
H0, R = 2025.0, 0.0934
clock, rho, varpi, bbar, Temb, Tpb, Tpar = 1.115, 0.10, 0.70, 0.67, 1.25, 1.25, 0.17
M0A = 0.3059752696881738
TARGETS = {2028: 0.624, 2031: 0.658, 2036: 0.683}
att = rho / clock
step = varpi * rho * Tpar
def flows(T, dt=1/365):
    t = np.arange(0.0, T, dt); tR = t / clock
    n = np.where(tR < Temb, 0, np.floor((tR - Temb)/Tpar + 1e-12) + 1)
    raw = step * n
    yrs = sorted(TARGETS)
    dm = np.interp(H0 + t, yrs, [TARGETS[y]-M0A for y in yrs])
    gain = bbar * np.minimum(1.0, raw) * dm
    dip = np.where(raw < 1.0, att*Tpb*dm, 0.0)
    return t, gain, dip, dt
t, g, d, dt = flows(200.0)
disc = (1+R)**(-t)
raw = step*np.where(t/clock < Temb, 0, np.floor((t/clock-Temb)/Tpar+1e-12)+1)
comp = float(t[np.argmax(raw >= 1.0)])
print(f"completion year offset: {comp:.4f} (2042.3)")
pv_g_full, pv_d_full = float(np.sum(g*disc)*dt), float(np.sum(d*disc)*dt)
print(f"full-horizon ratio (paper 3.9): {pv_g_full/pv_d_full:.3f}  pv_gain {pv_g_full:.4f} pv_dip {pv_d_full:.4f}")
for T in [comp, 10.0, 20.0, 50.0]:
    tt, gg, dd, dtt = flows(T)
    dd2 = (1+R)**(-tt)
    pg, pd = float(np.sum(gg*dd2)*dtt), float(np.sum(dd*dd2)*dtt)
    print(f"T={T:6.2f}: pv_gain {pg:.4f} pv_dip {pd:.4f} ratio {pg/pd:.3f}")
