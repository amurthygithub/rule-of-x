"""GPT-M2 (tax PV vs period cash), GPT-M3 (annual acquisition bridge), GPT-M4 (exit value). Own code."""
import json, math
import numpy as np
# ---------------- M2
def w_sched(T):   # half-year convention: 1/(2T) at a=0, 1/T for a=1..T-1, 1/(2T) at a=T
    w = np.full(T+1, 1/T); w[0] = w[-1] = 1/(2*T); return w
def factor(T, x):  # sum_a w_a (1+x)^-a
    return float((w_sched(T)*(1+x)**-np.arange(T+1)).sum())
psiT = lambda T, r=0.10: (1+(1+r)**-T)/(2*T) + (1-(1+r)**-(T-1))/(r*T)
print('M2: psi15(.10) closed form', round(psiT(15), 6), 'schedule', round(factor(15, .10), 6), '; psi5', round(psiT(5), 6))
# one-dollar, one-year-deferred example
print('  1 dollar deducted next year, tau=.2, r=.1: cash today -1, next year +.2, PV', -1+.2/1.1, '; PV-equivalent cost today', -(1-.2/1.1))
# balanced growth: period cash shield factor = psi_T evaluated at g (mature vintages, lead installation I_t = k g S_t)
for g in [0.05, 0.10, 0.15, 0.30]:
    cash = factor(15, g); pv = psiT(15)
    print(f'  g={g:.2f}: cash factor {cash:.6f} vs PV factor {pv:.6f}; PV-equivalent minus period cash score at k=1.5,tau=.18: {100*0.18*1.5*g*(pv-cash):+.4f} points')
# simulation check of the balanced-growth cash deduction ratio with explicit vintages (start-up and mature)
def sim(g, k=1.5, T=15, years=200):
    S = (1+g)**np.arange(years+1)       # revenue path
    I = k*g*S                           # lead-installation investment, I_t/S_t = k g
    w = w_sched(T); D = np.array([sum(w[a]*I[t-a] for a in range(T+1) if t-a >= 0) for t in range(years+1)])
    return D/S
d = sim(0.30); print('  vintage simulation g=.30: D_t/S_t at t=1,5,15,100 =', [round(x, 5) for x in d[[1, 5, 15, 100]]], ' steady state k g psi_15(g) =', round(1.5*0.30*factor(15, .30), 5))
# reported number exposed: ceiling loss at k=1.5, G=.30 for development abroad
for tau in (0.15, 0.18, 0.21):
    pv_loss = (1-psiT(15)*tau)*1.5*0.30; cash_loss = (1-factor(15, 0.30)*tau)*1.5*0.30
    print(f'  KcapLossFor tau={tau}: PV-equivalent {100*pv_loss:.2f} points (paper 40-41), period cash at mature balanced growth {100*cash_loss:.2f}')
print('  psi15(G=.30) =', round(factor(15, .30), 4), ' (replaces psi15=0.53 in the period-cash reading of the Table 4 note)')
# ---------------- M3
Sp, Scn, Sac, C = 100, 100, 100, 300
St = Scn+Sac; k = C/Sac
g_simple_acq = Sac/Sp; g_log_acq = math.log(1+Sac/Scn); g_tot = St/Sp-1
print(f'\nM3: actual C/S_t={C/St}; k*g_simple={k*g_simple_acq}; k*g_log={k*g_log_acq:.5f}; k*g_simple/(1+g_total)={k*g_simple_acq/(1+g_tot)}')
# case: per point of simple annual acquired growth (full-year recognition), average charge k/(1+g_t) at 2025 growth 94.7%
g25 = 0.947
for nm, kk in [('lowest-priced deal', 1.73), ('middle deal', 2.30), ('highest-priced deal', 3.2)]:
    print(f'  {nm}: k={kk}: instantaneous net effect per point 1-k={1-kk:+.2f}; annual simple-growth units (full-year recognition) 1-k/(1+g)={1-kk/(1+g25):+.3f}')
# marginal version from F audit: score = X(b+a-1) + m - k a/(a+b), d/da = X - k b/(a+b)^2 (m held fixed)
print('  note: the marginal annual derivative X - k*b/(a+b)^2 differs from the average k/(1+g) unless a is small; no single annual coefficient is universal')
# ---------------- M4
r = 0.10
tv5 = math.exp(-r*1)*0.2/r; npv = -1 + math.exp(-r*5)*tv5
print(f'\nM4 toy: continuous flow .2/yr from t=6 at r=.10: TV at 5 = {tv5:.6f}, NPV with exit = {npv:.6f}, full-horizon NPV = {-1+math.exp(-r*6)*0.2/r:.6f}')
ann = lambda n, r: (1-(1+r)**-n)/r
print(f'  D-specialist toy: pay 14, 2/yr for 20y at 10%: cash through 5y {-14+2*5}, TV5 {2*ann(15,.1):.4f}, NPV {-14+2*ann(5,.1)+2*ann(15,.1)/1.1**5:.4f}')
cal = json.load(open('/home/claude/paper/notes/calibration_results.json'))['r2']['payback']
for case in ['central', 'central_r10', 'fast', 'slow']:
    p = cal[case]; npv = p['npv_points_years']; cd5 = p['hold']['5']['cum_disc']; rr = p['r']
    cont_pv0 = npv - cd5                               # PV at t=0 of net flows after year 5
    tv5 = cont_pv0*(1+rr)**5                           # exit value at year 5 if a buyer capitalizes them at r
    breakeven = (-cd5/cont_pv0) if cont_pv0 > 0 else float('nan')
    print(f'  {case:12s} r={rr:.4f}: NPV {100*npv:6.1f}% of a year\'s revenue; disc. cum. cash at 5y {100*cd5:5.1f}; exit value at 5y {100*tv5:6.1f}; '
          f'5-year owner with full exit value: NPV {100*npv:6.1f}; break-even recovery of continuation value {100*breakeven:5.1f}%')
