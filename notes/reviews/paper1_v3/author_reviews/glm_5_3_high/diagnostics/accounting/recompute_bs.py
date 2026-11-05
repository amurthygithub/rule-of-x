import math, json, itertools
# Bending Spoons figures verified from filings (USD thousands)
rev = {2023: 387067.0, 2024: 671053.0, 2025: 1306404.0}
oi  = {2023: 84267.0, 2024: 127352.0, 2025: 277851.0}
ie  = {2023: 17173.0, 2024: 32605.0, 2025: 142601.0}   # interest expense
ip  = {2023: 16581.0, 2024: 19168.0, 2025: 130881.0}   # interest paid (424B4 F-34/35)
ocf = {2023: 59154.0, 2024: 204895.0, 2025: 290600.0}
inv = {2023: -170294.0, 2024: -889654.0, 2025: -1851874.0}  # net cash investing
adj_oi = {2024: 299481.0, 2025: 613247.0}
q2 = dict(rev25=311100.0, rev26=704155.0, oi26=240251.0, ie26=108970.0, reorg26=50799.0, txn26=6553.0, amort26=82310.0, adj26=381149.0)
out = {}
def pct(x): return 100*x
# 1 GAAP scores
for y in (2024, 2025):
    g = rev[y]/rev[y-1]-1
    m = oi[y]/rev[y]
    out[f'GAAP {y}'] = (g*100, m*100, (g+m)*100)
    out[f'GAAP-after-int {y}'] = (g+m)*100 - ie[y]/rev[y]*100
    out[f'cash-after-int {y}'] = (g + ocf[y]/rev[y])*100
    for tau in (0.24, 0.0):
        mcash = (ocf[y] + (1-tau)*ie[y])/rev[y]
        out[f'cash-before-int tau={tau} {y}'] = (g+mcash)*100
# adjusted margin score 2025
g25 = rev[2025]/rev[2024]-1
out['adj score 2025'] = (g25 + adj_oi[2025]/rev[2025])*100
# fully charged (before interest, cash margin, interest-expense add-back, tau .24 and 0)
for tau in (0.24, 0.0):
    mcash = (ocf[2025] + (1-tau)*ie[2025])/rev[2025]
    out[f'fully charged tau={tau} 2025'] = (g25 + mcash - (-inv[2025])/rev[2025])*100
    mcash4 = (ocf[2024] + (1-tau)*ie[2024])/rev[2024]
    out[f'fully charged tau={tau} 2024'] = (rev[2024]/rev[2023]-1 + mcash4 - (-inv[2024])/rev[2024])*100
# Q2 2026
gq2 = q2['rev26']/q2['rev25']-1
mq2 = q2['oi26']/q2['rev26']
out['Q2 reported score'] = (gq2+mq2)*100
out['Q2 organic 3%'] = (0.03+mq2)*100
out['Q2 organic after int'] = (0.03+mq2)*100 - q2['ie26']/q2['rev26']*100
out['Q2 org +reorg'] = (0.03+mq2+q2['reorg26']/q2['rev26'])*100
out['Q2 org +reorg after int'] = (0.03+mq2+q2['reorg26']/q2['rev26'])*100 - q2['ie26']/q2['rev26']*100
out['Q2 reported after int'] = (gq2+mq2)*100 - q2['ie26']/q2['rev26']*100
out['Q2 int %'] = q2['ie26']/q2['rev26']*100
out['Q2 reorg %'] = q2['reorg26']/q2['rev26']*100
out['Q2 adj margin'] = q2['adj26']/q2['rev26']*100
# ---- charged-as-capital 2025 ----
# outlays (positive), timing t in years since 2023-01-01
t_end = 3.0
flows = [(170294.0, 0.5), (889654.0, 1.5), (485746.0, 2.125), (89817.0, 2.375)]
H2_2025 = 1851874.0 - 575563.0   # 1,276,311
assert abs(H2_2025-1276311.0)<1
r = math.log(1.0934)
res = []
for nrr in (0.95, 0.91):
    d = -math.log(nrr); T = 1/d; CRF = r/(1-math.exp(-r*T))
    for tau in (0.24, 0.0):
        mcash = (ocf[2025] + (1-tau)*ie[2025])/rev[2025]
        base = (g25 + mcash)*100
        for h2pos in (2.75, 2.75+327/365.0*0 + 327/365.0):  # Oct 1 .. Vimeo close (t=3-327/365? no: close on 24 Nov 2025 -> position 2+327/365)
            pass
        for h2v in (2.75, 2+327/365.0):  # Oct 1 mid-of-half, Vimeo close 24 Nov (day 328 of 2025; 24 Nov is day 328) -> 327/365 from start
            fl = flows + [(H2_2025, h2v)]
            # (a) level annuity, year-end capital: all outlays within life
            s_year = sum(c for c,v in fl)
            ch_ann_ye = CRF*s_year/rev[2025]*100
            # (b) level annuity, time-weighted: outlays at v<=2 weight 1; v in (2,3] weight (3-v)
            s_tw = sum(c*(1 if v<=2 else (3-v)) for c,v in fl)
            ch_ann_tw = CRF*s_tw/rev[2025]*100
            # (c) user cost, year-end decayed capital
            Kd_ye = sum(c*math.exp(-d*(3-v)) for c,v in fl)
            ch_uc_ye = (r+d)*Kd_ye/rev[2025]*100
            # (d) user cost, time-weighted decayed capital (avg over year 2..3)
            def tw_weight(v):
                if v<=2: return math.exp(-d*(2-v))*(1-math.exp(-d))/d
                else: return (1-math.exp(-d*(3-v)))/d
            Kd_tw = sum(c*tw_weight(v) for c,v in fl)
            ch_uc_tw = (r+d)*Kd_tw/rev[2025]*100
            for name, ch in [('ann-YE',ch_ann_ye),('ann-TW',ch_ann_tw),('uc-YE',ch_uc_ye),('uc-TW',ch_uc_tw)]:
                res.append((nrr, tau, round(h2v,3), name, base-ch, base-ch-116.947))
            # return on TW acquisition capital (undecayed)
            roic_gross = (ocf[2025]+(1-tau)*ie[2025])/s_tw*100
            roic_dep  = ((ocf[2025]+(1-tau)*ie[2025]) - d*Kd_tw)/Kd_tw*100
            res.append((nrr, tau, round(h2v,3), 'ROIC-gross%', roic_gross, None))
            res.append((nrr, tau, round(h2v,3), 'ROIC-dep%', roic_dep, None))
            res.append((nrr, tau, round(h2v,3), 'Kd/S (pts per pt of r)', Kd_ye/rev[2025]*100, None))
            res.append((nrr, tau, round(h2v,3), 'KdTW/S', Kd_tw/rev[2025]*100, None))
# summary of charged scores
charged = [(a,b,c,d,e) for (a,b,c,d,e,f) in res if d in ('ann-YE','ann-TW','uc-YE','uc-TW')]
vals = sorted(set(round(x[4],1) for x in charged))
print('charged-as-capital 2025 scores, min/max over grid:', vals[0], vals[-1])
for name in ('ann-YE','ann-TW','uc-YE','uc-TW'):
    v = sorted(x[4] for x in charged if x[3]==name)
    print(f'  {name}: {v[0]:.1f} to {v[-1]:.1f}')
dbl = [(x[3], x[5]) for x in res if x[3] in ('ann-YE','ann-TW','uc-YE','uc-TW')]
v = sorted(x[1] for x in dbl)
print('same charges against OCF after interest: %.1f to %.1f' % (v[0], v[-1]))
# tau-split of charged range
for tau in (0.24, 0.0):
    v = sorted(x[4] for x in charged if x[1]==tau)
    print(f'  tau={tau}: {v[0]:.1f} to {v[-1]:.1f}')
# ROIC
g = sorted(x[4] for x in res if x[3]=='ROIC-gross%'); print('ROIC gross: %.1f%% to %.1f%%' % (g[0],g[-1]))
for tau in (0.24,0.0):
    g = sorted(x[4] for x in res if x[3]=='ROIC-gross%' and x[1]==tau); print(f'  ROIC gross tau={tau}: {g[0]:.1f} to {g[-1]:.1f}')
dp = sorted(x[4] for x in res if x[3]=='ROIC-dep%'); print('ROIC after depreciation: %.1f%% to %.1f%%' % (dp[0],dp[-1]))
kd = sorted(x[4] for x in res if x[3]=='Kd/S (pts per pt of r)'); print('decayed capital/revenue: %.2f to %.2f points' % (kd[0],kd[-1]))
# 9.625% coupon variant
r2 = math.log(1.09625)
ch2=[]
for nrr in (0.95,0.91):
    d=-math.log(nrr); T=1/d; CRF=r2/(1-math.exp(-r2*T))
    for tau in (0.24,0.0):
        mcash=(ocf[2025]+(1-tau)*ie[2025])/rev[2025]; base=(g25+mcash)*100
        for h2v in (2.75, 2+327/365.0):
            fl = flows + [(H2_2025,h2v)]
            s_tw = sum(c*(1 if v<=2 else (3-v)) for c,v in fl)
            Kd_ye = sum(c*math.exp(-d*(3-v)) for c,v in fl)
            def tw(v):
                if v<=2: return math.exp(-d*(2-v))*(1-math.exp(-d))/d
                return (1-math.exp(-d*(3-v)))/d
            Kd_tw = sum(c*tw(v) for c,v in fl)
            ch2 += [base-CRF*s_tw/rev[2025]*100, base-CRF*sum(c for c,_ in fl)/rev[2025]*100,
                    base-(r2+d)*Kd_ye/rev[2025]*100, base-(r2+d)*Kd_tw/rev[2025]*100]
print('charged at 9.625%% coupon: %.1f to %.1f' % (min(ch2),max(ch2)))
print()
print(json.dumps({k: round(v,2) for k,v in out.items()}, indent=1))
