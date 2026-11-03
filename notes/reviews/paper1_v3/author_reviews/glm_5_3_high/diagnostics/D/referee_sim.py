# D_referee_sim.py — Independent re-implementation of the execution-scenario (Prop 6/7, main §7.3)
# and control-standard arithmetic (Prop 5, Remark S10), from the paper's STATED parameters only.
# No repo imports. Fixed seeds. Python 3, numpy.
#
# Parameters as stated in the paper (main §7.3 "Pace"/"Embedding", S2.7, S2.9, Table S11):
#   change capacity rho = 0.10/yr of the program (5-22% range; WEF survey bracket), binds
#   varpi = 0.70 (share of attempts creating value; BCG outcome survey, rounded down) -> read as
#           the embedding probability per attempt (p_emb = varpi, nu_D = 0: no second application
#           of the disruption hazard, because the survey shares already include disruptions)
#   bbar  = 0.67 (realized share of targeted savings; Bucy et al. 2021, successful transformations)
#   T_emb = T_pb = 1.25 yr (embedding time = payback time; Salesforce/McKinsey analogies)
#   T_par = 0.17 yr (wave length; AI shadow-mode bracket)
#   nu_R = 0.46/yr, T_frz = 0.25 yr -> uniform clock 1 + nu_R*T_frz = 1.115
#   nu_D = nu_L(1-k_keep) + nu_V = 0.204*0.4 + 0.15 = 0.2316/yr (kept but NOT applied centrally)
#   dM(horizon) = full-cost margin term at the horizon's compute share minus the anchor intercept
#   targets m0F: 2028 62.4, 2031 65.8, 2036 68.3 (cc path 12/8/5%); anchor m0A = 30.60 (median, netted)
#   G = 12.7%; r = 9.34% (discount); fast case: rho 0.22, varpi 0.80, bbar 0.85, T_emb=T_pb=1.0,
#     T_par 0.08, nu_R 0.30, T_frz 0.08 (clock 1.024)
import json
import math
import numpy as np

rng = np.random.default_rng(20261103)
H0 = 2025.0
R_DISC = 0.0934

CASES = {
    'central': dict(rho=0.10, varpi=0.70, bbar=0.67, Temb=1.25, Tpb=1.25, Tpar=0.17,
                    nuR=0.46, Tfrz=0.25, nuD=0.0,          # nu_D = 0 per §7.3 (no double count)
                    nuD_available=0.2316),
    'fast':    dict(rho=0.22, varpi=0.80, bbar=0.85, Temb=1.0, Tpb=1.0, Tpar=0.08,
                    nuR=0.30, Tfrz=0.08, nuD=0.0, nuD_available=0.15*0.85 and 0.15*(1-0.85)+0.05),
}
# fix fast nuD properly: nu_L(1-k_keep)+nu_V = 0.15*(1-0.85)+0.05
CASES['fast']['nuD_available'] = 0.15 * (1 - 0.85) + 0.05
# anchor and targets (from Table 5 / calibration; targets at each horizon's compute share)
M0A = 0.3059752696881738
TARGETS = {2028: 0.624, 2031: 0.658, 2036: 0.683}
G_MKT = 0.127
HZ = [2028, 2031, 2036]


def clock(p):
    return 1.0 + p['nuR'] * p['Tfrz']


def expectation_path(p, dM_by_year):
    """Prop 7(e) upper bound under the greedy plan: E(t) = min(1, p_emb * cw * n(t_R))."""
    ck = clock(p)
    cw = p['rho'] * p['Tpar']
    pemb = p['varpi']                      # nu_D = 0 centrally
    out = {}
    for h in HZ:
        tR = (h - H0) / ck
        n = 0 if tR < p['Temb'] else math.floor((tR - p['Temb']) / p['Tpar'] + 1e-12) + 1
        raw = pemb * cw * n
        att = p['rho'] / ck               # attempt mass per calendar year
        dM = dM_by_year[h]
        out[h] = dict(
            n_waves=n, embedded=min(1.0, raw), realized=p['bbar'] * min(1.0, raw),
            m0=M0A + p['bbar'] * min(1.0, raw) * (TARGETS[h] - M0A),
            Rinf=M0A + p['bbar'] * min(1.0, raw) * (TARGETS[h] - M0A) + G_MKT,
            dip=(0.0 if raw >= 1.0 else att * p['Tpb'] * dM),
            fills_waves=(cw * (1 + p['varpi'] * (n - 1)) <= 1.0),
        )
    step = pemb * cw
    n_full = math.ceil(1 / step - 1e-9)
    out['complete_year'] = H0 + ck * (p['Temb'] + (n_full - 1) * p['Tpar'])
    n_cross = math.floor(att * p['Tpb'] / (p['bbar'] * step)) + 1
    out['cross_years'] = ck * (p['Temb'] + (n_cross - 1) * p['Tpar']) if n_cross < n_full else None
    return out


def payback(p, dM_by_year, r=R_DISC, dt=1 / 365, T=200.0):
    """Flow crossing, cumulative payback (undiscounted and discounted), NPV, PV ratio."""
    ck = clock(p)
    cw = p['rho'] * p['Tpar']
    pemb = p['varpi']
    step = pemb * cw
    att = p['rho'] / ck
    t = np.arange(0.0, T, dt)
    tR = t / ck
    n = np.where(tR < p['Temb'], 0, np.floor((tR - p['Temb']) / p['Tpar'] + 1e-12) + 1)
    raw = step * n
    yrs = sorted(dM_by_year)
    dm = np.interp(H0 + t, yrs, [dM_by_year[y] for y in yrs])
    gain = p['bbar'] * np.minimum(1.0, raw) * dm
    dip = np.where(raw < 1.0, att * p['Tpb'] * dm, 0.0)
    net = gain - dip
    disc = (1.0 + r) ** (-t)
    cu = np.cumsum(net) * dt
    cd = np.cumsum(net * disc) * dt
    first = lambda m: float(t[np.argmax(m)]) if m.any() else None
    neg = cu < 0
    pb_u = first((cu >= 0) & (np.cumsum(neg) > 0))
    pb_d = first((cd >= 0) & (np.cumsum(cd < 0) > 0))
    pv_gain = float(np.sum(gain * disc) * dt)
    pv_dip = float(np.sum(dip * disc) * dt)
    return dict(cross_flow=first((gain >= dip) & (raw < 1.0) & (raw > 0)),
                payback_undisc=pb_u, payback_disc=pb_d,
                npv_points_years=pv_gain - pv_dip, ratio=pv_gain / pv_dip,
                complete_year=float(t[np.argmax(raw >= 1.0)]),
                cum3=float(cu[int(3 / dt) - 1]), cum5=float(cu[int(5 / dt) - 1]))


def dM_map():
    return {h: TARGETS[h] - M0A for h in HZ}


# ---------------- Monte Carlo of the discrete (lumpy) program, greedy plan ----------------
def mc_program(p, N=4800, reps=200, horizon_years=25.0, nuD=None, seed_off=0, capacity_stock=False,
               random_freezes=False):
    """Discrete unit-mass program. Greedy: attempt min(cw*N, available) each wave.
    Attempt of a unit succeeds w.p. varpi; if nuD > 0 a working unit's calendar flight is hit by a
    Poisson(nuD) shock -> reverts. Optional variants:
      capacity_stock=True  -> in-flight (working, not embedded) units also consume wave capacity
      random_freezes=True   -> reorganizations as Poisson(nuR) in program time, freeze T_frz each
    Returns embedded share by calendar year (mean, p5, p50, p95) and per-rep completion years.
    """
    r = np.random.default_rng(20261103 + seed_off)
    rng2 = np.random.default_rng(555 + seed_off)
    ck = clock(p)
    cwN = p['rho'] * p['Tpar'] * N
    if nuD is None:
        nuD = 0.0          # paper's central case: no disruption haircut (nu_D = 0 in part (e))
    nuD_eff = nuD
    grid = np.arange(0.0, horizon_years + 1e-9, 0.25)
    emb_paths = np.zeros((reps, len(grid)))
    real_paths = np.zeros((reps, len(grid)))
    complete = []
    payback_rep = []
    for rep in range(reps):
        status = np.zeros(N)             # 0 available, 1 working-in-flight, 2 embedded
        b_u = rng2.random(N) * 0.0 + 0.67   # persistent realized share, mean bbar (no distribution stated)
        embed_t = np.full(N, np.inf)      # calendar embedding time
        tR = 0.0
        t_cal = 0.0
        freeze_time = 0.0
        frz_r = np.random.default_rng(777 + seed_off + rep) if random_freezes else None
        next_frz = (frz_r.exponential(1.0 / p['nuR']) if frz_r is not None else np.inf)
        while (status == 0).any() and t_cal < horizon_years:
            # wave w starts at program time tR; attempts last the wave; flights last Temb program time
            avail = np.where(status == 0)[0]
            if capacity_stock:
                # stock reading: at most rho*N units (10% of the program) in flight at once
                inflight = int(np.sum(status == 1))
                room = min(int(cwN), max(0, int(p['rho'] * N) - inflight))
            else:
                room = int(cwN)
            take = avail[:room]
            succ = r.random(len(take)) < p['varpi']
            new_work = take[succ]
            status[new_work] = 1
            # disruptions during the calendar flight (nuD per calendar year, flight = ck*Temb)
            if nuD_eff > 0:
                surv = r.random(len(new_work)) >= -np.expm1(-nuD_eff * ck * p['Temb'])
                status[new_work[~surv]] = 0
                new_work = new_work[surv]
            # newly working units embed ck*Temb of calendar time after their wave start
            embed_t[new_work] = t_cal + ck * p['Temb']
            # advance clock
            tR += p['Tpar']
            t_cal += ck * p['Tpar']
            # embed units whose flight has ended
            done = np.where((status == 1) & (embed_t <= t_cal + 1e-12))[0]
            status[done] = 2
        # record embedded share over calendar time
        emb_paths[rep] = [np.mean(embed_t <= (g + 1e-9)) for g in grid]
        # realized share with persistent b_p = 0.67 (mean bbar; distribution not stated in the paper)
        real_paths[rep] = [np.sum(0.67 * (embed_t <= (g + 1e-9))) / N for g in grid]
        fin = embed_t[embed_t < np.inf]
        complete.append(fin.max() if len(fin) == N else np.nan)
        # per-rep sample-path payback (dip flow = attempt_rate*Tpb*dM(t) while incomplete)
        att = p['rho'] / ck
        dMyrs = sorted(TARGETS)
        dMv = [TARGETS[y] - M0A for y in dMyrs]
        dm = np.interp(H0 + grid, dMyrs, dMv)
        gain = real_paths[rep] * dm
        comp_t = embed_t.max() if len(fin) == N else np.inf
        dip = np.where(grid < comp_t, att * p['Tpb'] * dm, 0.0)
        cu = np.cumsum((gain - dip) * 0.25)
        neg = cu < 0
        idx = np.argmax((cu >= 0) & (np.cumsum(neg) > 0)) if ((cu >= 0) & (np.cumsum(neg) > 0)).any() else None
        payback_rep.append(float(grid[idx]) if idx is not None else np.nan)
    mean = emb_paths.mean(axis=0)
    p5, p50, p95 = np.percentile(emb_paths, [5, 50, 95], axis=0)
    return dict(grid=grid, mean=mean, p5=p5, p50=p50, p95=p95, complete=complete,
                real_mean=real_paths.mean(axis=0), payback_rep=payback_rep,
                embedded_by={h: float(np.mean(embed_t <= (h - H0) + 1e-9)) for h in HZ})


# ---------------- Prop 5 control algebra ----------------
def prop5(N=24, ph=0.05, pch=0.002, pa=0.02, pca=0.005, pcc=0.0,
          ch=5e5, ca=5e4, itgc=204672.0, pibar=(0.05, 0.01), nmax=10):
    def P(nh, na):
        v = 1.0
        if nh:
            v *= pch + (1 - pch) * ph ** nh
        if na:
            v *= pca + (1 - pca) * pa ** na
        return pcc + (1 - pcc) * v if (nh or na) else 1.0
    def cost(nh, na):
        return nh * ch + na * ca + (itgc if na else 0.0)
    res = {}
    for pb in pibar:
        Pbar = 1 - (1 - pb) ** (1 / N)
        adm = [(cost(i, j), i, j) for i in range(nmax) for j in range(nmax)
               if (i or j) and P(i, j) <= Pbar]
        best = min(adm) if adm else None
        res[pb] = dict(Pbar=Pbar, best=best,
                       pi_best=(1 - (1 - P(best[1], best[2])) ** N) if best else None,
                       all_AI_limit=1 - (1 - pca) ** N,
                       all_human_limit=1 - (1 - pch) ** N,
                       pcc_breakeven_1H1AI=None)
        if best == (754672.0, 1, 1) and pb == 0.05:
            res[pb]['pcc_breakeven_1H1AI'] = (Pbar - P(1, 1)) / (1 - P(1, 1))
            # human miss-rate break-even on AI-missed items
            lo, hi = 0.0, 1.0
            for _ in range(200):
                mid = (lo + hi) / 2
                if (0.002 + 0.998 * mid) * (pca + (1 - pca) * pa) <= Pbar:
                    lo = mid          # admissible: the sup of admissible miss rates is the break-even
                else:
                    hi = mid
            res[pb]['human_miss_breakeven'] = lo
    return res


if __name__ == '__main__':
    print("versions: numpy", np.__version__)
    out = {}
    for name, p in CASES.items():
        dM = dM_map()
        ep = expectation_path(p, dM)
        pbk = payback(p, dM)
        print(f"\n=== case {name} ===")
        print("clock", clock(p), "cw", round(p['rho'] * p['Tpar'], 5),
              "attempt rate/yr", round(p['rho'] / clock(p), 5))
        for h in HZ:
            e = ep[h]
            print(f"  {h}: waves={e['n_waves']} embedded={e['embedded']:.4f} realized={e['realized']:.4f} "
                  f"m0={e['m0']:.3f} Rinf={e['Rinf']:.3f} dip={e['dip']:.4f} fills_waves={e['fills_waves']}")
        print("  complete_year", round(ep['complete_year'], 2), "cross_years", ep['cross_years'])
        print("  payback: cross", round(pbk['cross_flow'], 3), "undisc", round(pbk['payback_undisc'], 3),
              "disc", round(pbk['payback_disc'], 3), "NPV(pt-yr)", round(pbk['npv_points_years'], 3),
              "ratio", round(pbk['ratio'], 3), "cum3", round(pbk['cum3'], 4), "cum5", round(pbk['cum5'], 4))
        out[name] = dict(pace={h: {k: (float(v) if not isinstance(v, bool) else v) for k, v in ep[h].items()} for h in HZ},
                         complete_year=ep['complete_year'], cross_years=ep['cross_years'], payback=pbk)

    # Monte Carlo, central case (nu_D = 0): expectation vs sample path
    print("\n=== MC central (nu_D=0), N=4800 units, 200 reps ===")
    mc = mc_program(CASES['central'], N=4800, reps=200, horizon_years=20.0, seed_off=0)
    for h in HZ:
        i = int((h - H0) / 0.25)
        print(f"  {h}: MC mean embedded={mc['mean'][i]:.4f} p5={mc['p5'][i]:.4f} "
              f"p50={mc['p50'][i]:.4f} p95={mc['p95'][i]:.4f}  (bound "
              f"{expectation_path(CASES['central'], dM_map())[h]['embedded']:.4f})")
    comp = [c for c in mc['complete'] if not math.isnan(c)]
    if comp:
        print("  completion year (max embedding time): mean", round(np.mean(comp) + H0, 2),
              "p5", round(np.percentile(comp, 5) + H0, 2), "p95", round(np.percentile(comp, 95) + H0, 2))
    pr = [x for x in mc['payback_rep'] if not math.isnan(x)]
    print(f"  sample-path payback (b=0.67): mean {np.mean(pr):.2f} p5 {np.percentile(pr,5):.2f} "
          f"p50 {np.percentile(pr,50):.2f} p95 {np.percentile(pr,95):.2f} (expectation-based: 7.53)")

    # MC with the disruption hazard applied ON TOP (what double-counting would look like)
    print("\n=== MC central, disruption hazard applied on top (nu_D = 0.2316) ===")
    mc2 = mc_program(CASES['central'], N=4800, reps=200, horizon_years=45.0, seed_off=1,
                    nuD=CASES['central']['nuD_available'])
    for h in HZ:
        i = int((h - H0) / 0.25)
        print(f"  {h}: MC mean embedded={mc2['mean'][i]:.4f} p50={mc2['p50'][i]:.4f} "
              f"(bound {expectation_path(CASES['central'], dM_map())[h]['embedded']:.4f}; "
              f"pemb*bound = {math.exp(-CASES['central']['nuD_available']*clock(CASES['central'])*CASES['central']['Temb']):.4f} x bound)")

    # MC with in-flight units consuming capacity (stock constraint variant)
    print("\n=== MC central, capacity charged on in-flight stock too (variant) ===")
    mc3 = mc_program(CASES['central'], N=4800, reps=200, horizon_years=20.0, seed_off=2,
                     capacity_stock=True)
    for h in HZ:
        i = int((h - H0) / 0.25)
        print(f"  {h}: MC mean embedded={mc3['mean'][i]:.4f} (paper bound "
              f"{expectation_path(CASES['central'], dM_map())[h]['embedded']:.4f})")

    # Prop 5
    print("\n=== Prop 5 / Remark S10 arithmetic ===")
    p5 = prop5()
    for pb, v in p5.items():
        print(f"  pi_bar={pb}: Pbar/occasion={v['Pbar']:.6f} best={v['best']} "
              f"pi={v['pi_best']:.4f} allAIlimit={v['all_AI_limit']:.4f} allHumanlimit={v['all_human_limit']:.4f}")
        if v.get('pcc_breakeven_1H1AI'):
            print(f"    pcc break-even (1H+1AI) = {v['pcc_breakeven_1H1AI']:.6f}; "
                  f"human miss-rate break-even = {v['human_miss_breakeven']:.4f}")
    direct = 1492375 / 1e9 + 1.5e6 / 1e9
    for pb, v in p5.items():
        floor = direct + v['best'][0] / 1e9
        print(f"  floor at pi_bar={pb}: {floor:.4%} of revenue (direct {direct:.2%} + design {v['best'][0]/1e9:.4%})")
    for fee in (343e3, 1492375.0, 5.327646e6):
        fl = 1.5e6 / 1e9 + fee / 1e9 + 754672.0 / 1e9
        print(f"  direct-cost floor with audit fee ${fee:,.0f}: {fl:.4%}")
    n_apps = 1 + math.ceil((0.005 - (direct + 754672.0 / 1e9)) / (204672.0 / 1e9))
    print(f"  applications to reach 0.5%: {n_apps}; survey line ($80k): {1 + math.ceil((0.005 - (direct + 754672.0/1e9))/0.00008)}")

    out['mc'] = {k: {h: float(v[i]) for h, i in ((h, int((h - H0) / 0.25)) for h in HZ)}
                 for k, v in (('mean', mc['mean']), ('p5', mc['p5']), ('p50', mc['p50']), ('p95', mc['p95']))}
    out['mc_disrupted_mean'] = {h: float(mc2['mean'][int((h - H0) / 0.25)]) for h in HZ}
    out['mc_capstock_mean'] = {h: float(mc3['mean'][int((h - H0) / 0.25)]) for h in HZ}
    out['prop5'] = {str(k): {kk: (vv if not isinstance(vv, tuple) else list(vv)) for kk, vv in v.items()}
                    for k, v in p5.items()}
    json.dump(out, open('/root/tmp/ruleof40/diagnostics/D/referee_sim_results.json', 'w'), indent=1, default=float)
    print("\nsaved results to diagnostics/D/referee_sim_results.json")