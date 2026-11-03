# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Risk (spec Sections 9, 14.1, 15, 23): Monte Carlo outcome distributions of the chosen plan.

Two layers of draws:
  imputation draws  the firm is redrawn from its priors (impute.perturb_firm) and the fixed plan is re-priced:
                    this is the confidence interval from missing data (spec 9);
  outcome draws     for each imputation draw, every process's transition is drawn from the core's outcome tree:
                    a shared platform is sound with probability p_P (ext prop:ext-portfolio(b)); given a sound
                    platform the transition succeeds with probability varpi/p_P; on success the benefit fraction
                    is Beta(b_conc bbar, b_conc (1 - bbar)); a failure is detected during the parallel run with
                    probability 1 - p_u and otherwise cut over and rolled back; build and integration costs
                    overrun with the heavy-tailed mixture (ext; Flyvbjerg et al.), capped by a stage gate;
                    leadership changes (kept with kappa_keep), vision overhauls (raised after a leadership
                    change) and reorganizations arrive as Poisson processes and disrupt or freeze work in flight
                    (ext sec:ext-shocks); agentic misbehavior arrives as a compound Poisson process with Pareto
                    losses, and provider incidents hit every process on the provider at once (spec 23).
Outputs: P10/P50/P90 of value and of the Rule-of-40 path, the probability of meeting the target, CVaR, the value
of finer data per process (core prop:tasks-granularity) and the pilot decisions (core prop:tasks-pilot)."""
from __future__ import annotations

import math
import time

import numpy as np
import pandas as pd

from . import formulas as F
from . import economics as E
from . import impute
from .plans import PlanBuilder, QPY, column_specs, reprice
from .config import Section
from .security import nu_cm_effective


def _pv_matrix(T: int, r: float, horizon: float | None) -> np.ndarray:
    tq = (np.arange(T * QPY) + 0.5) / QPY
    keep = tq <= (horizon or T)
    return np.exp(-r * tq) * keep


def outcome_draws(cols, varpi, prog_r: float, T: int, S: np.ndarray, p, rng: np.random.Generator, n: int,
                  tv_mult: float, horizon: float | None, failure: dict | None = None, platforms=None, shocks=None) -> dict:
    """Outcome draws for fixed columns (built without regime shocks, which are drawn here). `shocks` is the shock
    section to draw from (the run's own; the columns' parameters have shocks switched off so that they are not applied
    twice); None uses p.shocks. Returns arrays over draws: PV of value, the cash and GAAP margin change by year, and
    loss components."""
    C = len(cols)
    sc, ov, sh, pl = p.success, p.overrun, (shocks if shocks is not None else p.shocks), p.pilot
    D = _pv_matrix(T, prog_r, horizon)
    tq = (np.arange(T * QPY) + 0.5) / QPY
    if C == 0:
        z = np.zeros(n)
        return {"value": z, "cash": np.zeros((n, T)), "gaap": np.zeros((n, T)), "success_count": z, "misbehavior": z, "common_mode": z}
    pv0 = cols.cf0 @ D
    pv1 = cols.cf1 @ D + cols.tv1 * tv_mult * math.exp(-prog_r * (horizon or T))
    sr = cols.sr_q @ D
    sav = cols.sav_q @ D
    bld = cols.bld_q @ D
    pu = cols.p_u
    plats = np.unique(cols.platform, return_inverse=True)[1] if platforms is None else platforms
    nP = int(plats.max()) + 1
    sound = rng.random((n, nP)) < sc.p_P
    cond = np.minimum(varpi / max(sc.p_P, 1e-9), 1.0)
    succ = sound[:, plats] & (rng.random((n, C)) < cond[None, :])
    bbar = cols.bbar if cols.bbar is not None else np.full(C, sc.b_bar)
    bbar = np.clip(bbar, 1e-3, 1 - 1e-3)
    b = rng.beta(sc.b_conc * bbar[None, :], sc.b_conc * (1 - bbar)[None, :], (n, C))
    undetected = (~succ) & (rng.random((n, C)) < pu[None, :])
    X = F.sample_overrun(rng, (n, C), ov.tail_prob, ov.tail_alpha, ov.tail_xmin, ov.body_median, ov.body_sigma, cap=pl.overrun_cap)
    # value by branch: success = pv0 + pv1 + (b/bbar - 1) sav; detected failure = pv0 + p_u sr; undetected = pv0 - (1 - p_u) sr
    val = np.where(succ, pv0 + pv1 + (b / bbar - 1) * sav,
                   np.where(undetected, pv0 - (1 - pu) * sr, pv0 + pu * sr))
    val = val - (X - 1.0) * bld                                               # overruns (bld is a positive spend PV)
    # annual margin changes by branch (pre-tax)
    cash = np.where(succ[..., None], cols.cash0 + cols.cash1 + (b / bbar - 1)[..., None] * cols.sav_cash,
                    np.where(undetected[..., None], cols.cash0 - (1 - pu)[:, None] * cols.sr_cash, cols.cash0 + pu[:, None] * cols.sr_cash))
    gaap = np.where(succ[..., None], cols.gaap0 + cols.gaap1 + (b / bbar - 1)[..., None] * cols.sav_cash,
                    np.where(undetected[..., None], cols.gaap0 - (1 - pu)[:, None] * cols.sr_gaap, cols.gaap0 + pu[:, None] * cols.sr_gaap))
    cash = cash - (X - 1.0)[..., None] * cols.bld_cash
    gaap = gaap - (X - 1.0)[..., None] * cols.bld_cash
    # regime shocks (ext sec:ext-shocks): disruptions cancel work in flight; freezes delay it
    in_flight = np.zeros((n, C), bool)
    if sh.enabled:
        horizon_y = float(T)
        s = cols.start.astype(float)
        T_emb = cols.T_emb
        nu_keep_fail = sh.nu_L * (1 - sh.kappa_keep)
        # disruption time of the program: first of (leadership change not kept) and (vision overhaul)
        t_L = rng.exponential(1 / max(sh.nu_L, 1e-9), n)
        keep = rng.random(n) < sh.kappa_keep
        t_V = rng.exponential(1 / max(sh.nu_V, 1e-9), n)
        # after a kept leadership change the vision hazard jumps for two years
        t_V2 = t_L + rng.exponential(1 / max(sh.nu_V * sh.vision_jump, 1e-9), n)
        t_V = np.where(keep & (t_V2 < t_L + 2) & (t_V2 < t_V), t_V2, t_V)
        t_dis = np.minimum(np.where(keep, np.inf, t_L), t_V)                  # (n,)
        if not sh.disruption_haircut:                                         # base case: no cancellation (ISSUES 9)
            t_dis = np.full(n, np.inf)
        in_flight = (t_dis[:, None] >= s[None, :]) & (t_dis[:, None] < (s + T_emb)[None, :])
        # a disrupted process loses its flows after t_dis and recovers V_rec
        cf_s = (cols.cf0 + cols.cf1)                                          # success-branch flows (C, Q)
        lostPV = np.zeros((n, C))
        rec = np.zeros((n, C))
        for c in range(C):
            m = in_flight[:, c]
            if not m.any():
                continue
            post = (tq[None, :] >= t_dis[m, None]).astype(float)
            branch = np.where(succ[m, c][:, None], cf_s[c][None, :], cols.cf0[c][None, :])
            lostPV[m, c] = (branch * post * D[None, :]).sum(1) + np.where(succ[m, c], cols.tv1[c] * tv_mult * math.exp(-prog_r * (horizon or T)), 0.0)
            rec[m, c] = cols.V_rec[c] * np.exp(-prog_r * t_dis[m])
        val = val - lostPV + rec
        # reorganization freezes delay in-flight savings by T_frz (value erodes at r_d meanwhile)
        n_reorg = rng.poisson(sh.nu_R * horizon_y, n)
        r_d = prog_r + p.decisions.delta_V
        freeze_loss = 1 - np.exp(-r_d * sh.T_frz)
        hit_reorg = rng.random((n, C)) < 1 - np.exp(-sh.nu_R * np.maximum(T_emb, 0.25)[None, :])
        val = val - hit_reorg * succ * np.maximum(pv1, 0)[None, :] * freeze_loss * (1 + 0 * n_reorg[:, None])
    # AI failure modes (spec 23): compound Poisson misbehavior losses per process, provider common-mode events
    mis_pc = np.zeros((n, C))
    cm_pc = np.zeros((n, C))
    if failure is not None and failure.get("enabled"):
        lam = failure["Lambda"]                                               # (C,) incidents a year
        xm, cap_, al = failure["x_m"], failure["cap"], failure["alpha"]
        yrs_run = np.clip(T - cols.tau0, 0, T)
        Dbar = np.array([np.mean(np.exp(-prog_r * np.arange(int(math.ceil(y)), T) - 0.5)) if y < T else 0 for y in cols.tau0])
        for c in range(C):
            if lam[c] <= 0:
                continue
            k = rng.poisson(lam[c] * yrs_run[c], n)
            tot = np.zeros(n)
            mk = k > 0
            if mk.any():
                kk = k[mk]
                draws = xm[c] * (1 - rng.random(int(kk.sum()))) ** (-1 / al)
                draws = np.minimum(draws, cap_[c])
                tot[mk] = np.add.reduceat(draws, np.concatenate([[0], np.cumsum(kk)[:-1]]))
            mis_pc[:, c] = tot * Dbar[c] * succ[:, c]
        # common mode: provider incidents hit every process on the provider
        prov = failure["provider"]
        Wc = failure["W_annual"]
        rho = float(failure.get("rho", 1.0))
        # each event degrades this share of a year; change controls remove regressions (fewer events), not their size
        share_ev = failure["cm_days"] / 365.0 * failure["cm_burst"] + failure["downtime_hours"] / 8760.0 / max(failure.get("nu_cm_raw", failure["nu_cm"]), 1e-9)
        for kprov in np.unique(prov):
            on = np.flatnonzero(prov == kprov)
            ev_n = rng.poisson(failure["nu_cm"] * T, n)                         # provider events over the plan
            # each event hits every process on the provider with probability rho, else one at random
            hit_all = rng.binomial(ev_n, rho)
            loss_all = float(np.sum(Wc[on] * Dbar[on])) * share_ev
            loss_one = float(np.mean(Wc[on] * Dbar[on])) * share_ev if len(on) else 0.0
            if not len(on):
                continue
            wts = Wc[on] * Dbar[on]
            wts = wts / max(float(wts.sum()), 1e-12)
            tot = (hit_all * loss_all + (ev_n - hit_all) * loss_one)
            cm_pc[:, on] = tot[:, None] * wts[None, :] * succ[:, on]
        val = val - mis_pc - cm_pc
    mis, cm = mis_pc.sum(1), cm_pc.sum(1)
    return {"value": val.sum(1), "cash": cash.sum(1), "gaap": gaap.sum(1), "success_count": succ.sum(1),
            "misbehavior": mis, "common_mode": cm, "by_process": val, "disrupted": in_flight.sum(1)}


def failure_inputs(econ, cols, p, providers: int | None = None) -> dict:
    """Per-column misbehavior rate, severity and provider assignment for the Monte Carlo (spec 23)."""
    rel = econ.info.get("reliability")
    rl = p.reliability
    C = len(cols)
    if rel is None or not rl.enabled or C == 0:
        return {"enabled": False}
    lam, xm, cap = np.zeros(C), np.zeros(C), np.zeros(C)
    for i in range(C):
        us = np.flatnonzero(econ.unit_proc == cols.proc[i])
        md = cols.modes[i]
        isA = md == E.A
        if not isA.any():
            continue
        y = min(int(cols.tau0[i]), econ.T - 1)
        l = int(cols.level[i])
        v = econ.firm.units.v.values[us] * econ.vf[y]
        lam[i] = float(np.sum(rel["m_esc"][us, l, y] * v * isA))
        wts = np.maximum(rel["m_esc"][us, l, y] * v * isA, 1e-30)
        xm[i] = float(np.average(rel["sev_x"][us], weights=wts))
        cap[i] = float(np.average(rel["cap"][us], weights=wts))
    k = int(providers or rl.providers)
    prov = np.arange(C) % max(k, 1)
    W = np.array([d["W"][min(d["y0"] + 1, econ.T - 1)] for d in cols.detail])
    return {"enabled": True, "Lambda": lam, "x_m": xm, "cap": cap, "alpha": rl.alpha_tail, "provider": prov,
            "W_annual": np.maximum(W, 0), "nu_cm_raw": rl.nu_cm, "nu_cm": nu_cm_effective(econ, p), "cm_days": rl.cm_days, "cm_burst": rl.cm_burst,
            "downtime_hours": rl.downtime_hours, "rho": rl.provider_correlation, "providers": k}


def summarize(x: np.ndarray, q=(0.1, 0.5, 0.9)) -> dict:
    x = np.asarray(x, float)
    out = {f"P{int(round(100 * qq))}": float(np.quantile(x, qq)) for qq in q}
    out["mean"] = float(np.mean(x))
    out["sd"] = float(np.std(x))
    return out


def cvar(x: np.ndarray, level=0.95, lower=True) -> float:
    """Expected value in the worst (1 - level) share of draws (of value: the lower tail)."""
    x = np.sort(np.asarray(x, float))
    k = max(int(math.ceil((1 - level) * len(x))), 1)
    return float(x[:k].mean() if lower else x[-k:].mean())


SKIP_DRAW_SECTIONS = {"mc", "gsa", "constraints", "regime", "pqc"}


def scenario_keys(p, classes=("b", "d")) -> list[str]:
    """Parameters drawn in the Monte Carlo: numeric scalars of grounding class b or d with a usable range, outside
    the numerical settings and the regime presets (the regime is a choice, compared side by side)."""
    return [k for k in p.scenario_parameters(classes) if k.split(".", 1)[0] not in SKIP_DRAW_SECTIONS]


def draw_parameters(p, keys: list[str], rng: np.random.Generator):
    """One draw of the class b and d parameters over their ranges (spec 21.1): triangular with the mode at the
    default when the default lies inside the range, uniform otherwise; integers stay integers."""
    q = p.copy()
    vals = {}
    for k in keys:
        v = p.get(k)
        lo, hi = (float(x) for x in p.range(k))
        if lo > hi:
            lo, hi = hi, lo
        x = float(rng.triangular(lo, min(max(float(v), lo), hi), hi)) if lo <= float(v) <= hi and hi > lo else float(rng.uniform(lo, hi))
        if isinstance(v, int) and not isinstance(v, bool):
            x = int(round(x))
        q.set(k, x, origin="monte carlo parameter draw")
        vals[k] = x
    return q, vals


def run_monte_carlo(point_firm, ing, priors, p, sol, prog, econ, reg, seed: int, n_imp: int | None = None,
                    n_out: int | None = None, param_uncertainty: bool = True) -> dict:
    """Imputation x parameter x outcome Monte Carlo of the chosen plan (fixed modes, readiness and timing). Draw 0
    is the point estimate at default parameters; every later draw redraws the firm's imputed data and, when
    param_uncertainty is on, every class b and d parameter over its range, so the P10 to P90 band covers the
    scenario parameters (spec 21.1, 24.2)."""
    t0 = time.time()
    mc = p.mc
    n_imp = int(n_imp or mc.imputation_draws)
    n_out = int(n_out or mc.outcome_draws)
    rng = np.random.default_rng(seed)
    idx = np.array(sorted(sol.sel.values()), int)
    specs = column_specs(prog.cols, idx)
    T = econ.T
    tv_mult = min(1 / (reg.r - min(reg.g_tv, reg.r - 0.01)), reg.tv_cap) if reg.terminal == "going_concern" else 0.0
    p_ns = p.copy()
    p_ns.set("shocks.enabled", False, origin="monte carlo: shocks drawn explicitly")
    vals, cash_paths, gaap_paths, mis_all, cm_all, by_proc, imp_value = [], [], [], [], [], [], []
    proc_W = {i: [] for i in range(len(idx))}
    S = econ.firm.part1["S"] * econ.vf
    base_r40c = econ.firm.part1["g"] + econ.firm.part1["m_cash"]
    base_r40g = econ.firm.part1["g"] + econ.firm.part1["m_op"]
    keys = scenario_keys(p) if param_uncertainty else []
    param_vals, holds = [], []
    for i in range(n_imp):
        draw = point_firm if i == 0 else impute.perturb_firm(point_firm, ing, priors, p, rng)
        if i > 0 and keys:
            p_i, pv = draw_parameters(p_ns, keys, rng)
        else:
            p_i, pv = p_ns, {k: p.get(k) for k in keys}
        param_vals.append(pv)
        e_i = E.build_econ(draw, p_i)
        b_i = PlanBuilder(e_i)
        cols_i = reprice(b_i, specs)
        keep = np.array(cols_i.keep, int)
        varpi_i = sol.varpi[idx][keep] if len(keep) else np.zeros(0)
        # the experience boost of the solution carries over; the base probability is the draw's own
        if len(keep):
            from scipy.special import expit, logit
            boost = logit(np.clip(sol.varpi[idx][keep], 1e-6, 1 - 1e-6)) - prog.cols.logit0[idx][keep]
            varpi_i = expit(cols_i.logit0 + boost)
        fail = failure_inputs(e_i, cols_i, p_i)
        # the shocks are drawn from the run's own shock settings (p_i has them off for the columns only); before 29 Oct
        # 2026 the draws read p_i and so never ran
        sh_i = Section("shocks", {**p_i.shocks._v, "enabled": p.shocks.enabled, "disruption_haircut": p.shocks.disruption_haircut})
        out = outcome_draws(cols_i, varpi_i, reg.r, T, S, p_i, rng, n_out, tv_mult, reg.horizon, failure=fail, shocks=sh_i)
        h = np.zeros(len(idx), bool)
        if len(keep):
            h[keep] = out["by_process"].mean(0) > 0
        holds.append(h)
        vals.append(out["value"])
        cash_paths.append(out["cash"] / S[None])
        gaap_paths.append(out["gaap"] / S[None])
        mis_all.append(out["misbehavior"])
        cm_all.append(out["common_mode"])
        imp_value.append(float(np.mean(out["value"])))
        for j, k in enumerate(keep):
            proc_W[k].append(float(cols_i.detail[j]["W"][min(cols_i.detail[j]["y0"] + 1, T - 1)]))
    val = np.concatenate(vals)
    cash = np.concatenate(cash_paths)
    gaap = np.concatenate(gaap_paths)
    r40c = base_r40c + cash
    r40g = base_r40g + gaap
    planned = float(sol.value)
    target = p.success.target_share * planned
    q = (0.1, 0.5, 0.9)
    res = {
        "draws": {"imputation": n_imp, "outcome_per_imputation": n_out, "total": int(len(val))},
        "value": summarize(val), "value_cvar95": cvar(val, 0.95),
        "prob_meet_value_target": float(np.mean(val >= target)), "value_target": target,
        "prob_loss": float(np.mean(val < 0)),
        "r40_cash": {f"P{int(100*qq)}": np.quantile(r40c, qq, axis=0) for qq in q},
        "r40_gaap": {f"P{int(100*qq)}": np.quantile(r40g, qq, axis=0) for qq in q},
        "prob_r40_target_final_year_cash": float(np.mean(r40c[:, -1] >= p.success.target_r40)),
        "prob_r40_target_final_year_gaap": float(np.mean(r40g[:, -1] >= p.success.target_r40)),
        "misbehavior_loss": summarize(np.concatenate(mis_all)), "misbehavior_cvar95": cvar(-np.concatenate(mis_all), 0.95),
        "common_mode_loss": summarize(np.concatenate(cm_all)),
        "imputation_value": summarize(np.array(imp_value)),
        "convergence": convergence(val),
        "seconds": time.time() - t0,
        "param_uncertainty": bool(keys), "parameters_drawn": len(keys),
    }
    # robustness (spec 24.2): share of the parameter-and-data draws in which each selected process keeps a positive
    # expected value; and the rank correlation of the draw's mean value with each drawn parameter
    H = np.array(holds) if holds else np.zeros((0, len(idx)))
    res["robustness"] = pd.DataFrame({"process_id": [P_id for P_id in econ.firm.processes.process_id.values[prog.cols.proc[idx]]],
                                      "share_of_draws_value_positive": H.mean(0) if len(H) else np.zeros(len(idx))})
    if keys and n_imp >= 8:
        from scipy.stats import spearmanr
        pv = pd.DataFrame(param_vals)
        corr = {}
        for k in keys:
            col = pv[k].values.astype(float)
            if np.std(col) > 0:
                rr = spearmanr(col, imp_value).correlation
                corr[k] = float(rr) if np.isfinite(rr) else 0.0
        res["param_rank_correlation"] = dict(sorted(corr.items(), key=lambda kv: -abs(kv[1]))[:25])
    # value of finer data per process (core prop:tasks-granularity): posterior mean and sd of the annual saving
    rows = []
    P = econ.firm.processes
    for j, k in enumerate(idx):
        arr = np.array(proc_W[j]) if proc_W[j] else np.array([0.0])
        m, s = float(arr.mean()), float(arr.std())
        rows.append({"process_id": P.process_id.iat[prog.cols.proc[k]], "mean_annual_saving": m, "sd_annual_saving": s,
                     "z": abs(m) / s if s > 0 else math.inf, "decision_loss": float(F.decision_loss(m, s))})
    res["posterior"] = pd.DataFrame(rows)
    return res


def convergence(x: np.ndarray) -> dict:
    """Monte Carlo diagnostics: running mean at half and full sample and the standard error."""
    x = np.asarray(x, float)
    n = len(x)
    half = x[: n // 2]
    return {"n": n, "mean_half": float(half.mean()) if len(half) else float("nan"), "mean_full": float(x.mean()),
            "std_error": float(x.std() / math.sqrt(max(n, 1))),
            "relative_change": float(abs(x.mean() - half.mean()) / max(abs(x.mean()), 1e-9)) if len(half) else float("nan")}


def value_of_information(posterior: pd.DataFrame, p, tier: int) -> pd.DataFrame:
    """Value of the next data tier per process (core prop:tasks-granularity): s_hat L(|m|/s_hat), where the next
    tier cuts the sd by the measurement sd-reduction factor; measure iff that value exceeds the measurement cost
    (per process: event logs or process mining and a time study). Values are per year of the decision and are
    capitalized over the build life."""
    ms = p.measurement
    if posterior is None or posterior.empty:
        return pd.DataFrame(columns=["process_id", "value_of_tier", "measurement_cost", "measure"])
    out = posterior.copy()
    s_new = out.sd_annual_saving * ms.sd_after_measurement
    annual = F.value_of_tier(out.mean_annual_saving.values, out.sd_annual_saving.values, s_new.values)
    out["value_of_tier"] = annual * ms.decision_years
    out["measurement_cost"] = ms.process_mining_cost + ms.time_study_cost
    out["measure"] = out.value_of_tier > out.measurement_cost
    out["decision_loss_bound"] = F.decision_loss_bound(out.mean_annual_saving.values, out.sd_annual_saving.values)
    return out


def pilot_decisions(sol, prog, econ, p) -> pd.DataFrame:
    """Stage gates (core prop:tasks-pilot) for every selected process: value on success Y_s and on failure Y_f of
    the no-pilot plan, the value of a revealing pilot, the band in which piloting pays and the gate threshold."""
    cols = prog.cols
    rows = []
    D = _pv_matrix(econ.T, prog.regime.r, prog.regime.horizon)
    for pr, c in sol.sel.items():
        Ys = float((cols.cf0[c] + cols.cf1[c]) @ D)
        Yf = float(cols.cf0[c] @ D + (cols.p_u[c] * cols.sr_q[c]) @ D - cols.p_u[c] * 0) if cols.pilot[c] == 0 else float(cols.cf0[c] @ D)
        d = math.exp(-prog.regime.r * p.pilot.T_pil)
        Fp = p.pilot.cost_share * cols.detail[c]["F_build"] + p.pilot.fixed_cost
        vp = F.pilot_value(float(sol.varpi[c]), Ys, min(Yf, -1e-9), Fp, d)
        lo, hi, gate = F.pilot_band(Ys, min(Yf, -1e-9), Fp, d)
        rows.append({"process_id": econ.firm.processes.process_id.iat[pr], "pilot_in_plan": bool(cols.pilot[c]),
                     "success_probability": float(sol.varpi[c]), "Y_success": Ys, "Y_failure": Yf, "pilot_cost": Fp,
                     "value_of_pilot": vp, "pilot_band_low": lo, "pilot_band_high": hi, "gate_threshold": gate,
                     "recommendation": "pilot, then scale if the pilot succeeds" if vp > 0 else "skip the pilot"})
    return pd.DataFrame(rows)
