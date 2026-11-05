# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""The economic core: unit costs of the five modes for every activity unit, readiness level and year, with
feasibility, permissibility and the Section 18 run and risk costs (spec Sections 3 to 6, 13.1, 18).

Shapes: U units, L readiness levels (level 0 is today's readiness), T plan years (year y is calendar
base_year + y + 0.5). Modes are indexed H, O, U, A, N as in formulas.MODES.

Two cost views are kept:
  choice costs  `ct`   pre-tax-equivalent effective costs used for mode choice and the universe (ext 3.1): own
                       labor at the effective wage w_hat, capital and builds at the tax wedge Ups, penalties
                       grossed up by 1/(1 - tau);
  cash costs    `cash` operating cash cost per unit, without build amortization or capital charges (those enter
                       the cash flows as spending), used for transitions, the score path and NPV.
Every formula comes from formulas.py; this module only assembles arrays."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from . import formulas as F
from .config import Params
from .impute import Firm

H, O, U, A, N = F.H, F.O, F.U, F.A, F.N
NM = 5
CLASS_RANK = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}


@dataclass
class Econ:
    firm: Firm
    p: Params
    T: int
    L: int
    years: np.ndarray            # (T,) calendar mid-year
    vf: np.ndarray               # (T,) volume factor (1 + g)^y
    unit_proc: np.ndarray        # (U,) process index of each unit
    iota: np.ndarray             # (P, L) process readiness by level
    iota_u: np.ndarray           # (U, L) effective readiness (context-adjusted)
    level_ok: np.ndarray         # (P, L)
    feas: np.ndarray             # (U, L, T, NM) bool
    ct: np.ndarray               # (U, L, T, NM) choice cost per unit ($)
    cash: np.ndarray             # (U, L, T, NM) operating cash cost per unit ($)
    base_mode: np.ndarray        # (U,) H or O
    F_build: np.ndarray          # (U, T, NM) one-time build cost if the switch happens in year y ($)
    K: np.ndarray                # (U, L, T, NM) capital per unit of annual volume ($)
    run: np.ndarray              # (U, T, NM) annual run cost of the unit in that mode ($/yr), not per unit
    C_inc: np.ndarray            # (U, NM) expected incident loss without security ($/yr)
    eps: np.ndarray              # (U, L, T) residual error rate under A
    xi: np.ndarray               # (U, L, T) review share under A
    e_raw: np.ndarray            # (U, L, T) raw AI error rate
    log_margin: np.ndarray       # (U, L, T) ln(Hcal kappa / (d_eff chi(r_A)))
    T_F: np.ndarray              # (U, L) feasibility date of A (calendar)
    res_hours: np.ndarray        # (U, L, T, NM) own hours per unit left in each mode (for FTE and people)
    inference: np.ndarray        # (U, L, T, NM) inference spend per unit ($)
    exposure_sec: np.ndarray     # (U, NM) security exposure Omega_j(x)
    perm: np.ndarray             # (U, NM) permissible
    tech: np.ndarray             # (U, L, T, NM) technically feasible (capability and readiness), before rules
    data_allowed: np.ndarray     # (U,) risk appetite allows AI on the unit's data class
    rates: dict
    info: dict = field(default_factory=dict)

    @property
    def nU(self) -> int:
        return self.ct.shape[0]


def resolved_role_wages(data_dir=None, p=None) -> dict:
    """The transformation roles' median annual wages as the engine resolves them (impute.role_wages from the
    occupations table, OEWS vintage recorded), and their loaded annual cost (role_rates). For the paper example and
    other callers that need the same values as the engine."""
    from .config import find_data_dir, load_params
    from .impute import ROLE_SOCS, role_wages
    from .priors import load_priors
    p = p or load_params(data_dir)
    occ = load_priors(data_dir or find_data_dir()).occupations.set_index("soc")
    wages, src = role_wages(occ, p)

    class _F:
        fin = {"_role_wages": wages}
    rates = role_rates(_F(), p)
    return {"wages": wages, "socs": dict(ROLE_SOCS), "source": src,
            "loaded_annual": {k[:-5]: v for k, v in rates.items() if k.endswith("_year")}}


def unit_regulated(Ut) -> np.ndarray:
    """Regulated status of each activity unit (spec 5, 24.4): the explicit `regulated` attribute set by impute from
    the regulated class, EU AI Act high-risk status, licensed sign-off, ICFR scope or a firm input. For units built
    without it, the regulated class alone. Never the reliability target."""
    if "regulated" in Ut.columns:
        return Ut.regulated.fillna(0).values.astype(bool)
    return (Ut.regulated_class.astype(str).values != "none")


def role_rates(firm: Firm, p: Params) -> dict:
    """Loaded annual and monthly cost of the transformation roles (spec 7 sizing rules)."""
    w = dict(firm.fin.get("_role_wages") or {})
    if len(w) < 7:                     # a firm built without impute: read the occupations table (OEWS medians)
        from .config import find_data_dir
        from .impute import role_wages
        from .priors import load_priors
        w = {**role_wages(load_priors(find_data_dir()).occupations.set_index("soc"), p)[0], **w}
    load = 1.0 + p.labor.tau_L
    base_ai = float(w.get("ai_engineer") or p.build.ai_engineer_base_wage)
    annual = {
        "ai_engineer": base_ai * p.build.ai_engineer_premium * load,
        "data_engineer": w["data_engineer"] * 1.1 * load,
        "process_owner": w["process_owner"] * load,
        "change_manager": w["change_manager"] * load,
        "risk_governance": w["risk_governance"] * 1.2 * load,
        "security_reviewer": w["security_reviewer"] * load,
        "program_manager": w["program_manager"] * load,
    }
    out = {f"{k}_year": v for k, v in annual.items()}
    out.update({f"{k}_month": v / 12.0 for k, v in annual.items()})
    out.update({f"{k}_hour": v / p.labor.hours_per_fte for k, v in annual.items()})
    return out


def _class_multiplier(gwa_ids, cm: dict) -> np.ndarray:
    out = np.ones(len(gwa_ids))
    keys = sorted(cm, key=len, reverse=True)
    for i, g in enumerate(gwa_ids):
        for k in keys:
            if str(g).startswith(k):
                out[i] = cm[k]
                break
    return out


def owned_compute_share(fin: dict, default: float) -> float:
    """The firm's owned share of compute: the firm file's value when it gives one, an explicit 0 included, else the
    configured default (an `or` here replaced an explicit 0 by the default; outside re-review of Paper 1, 5 Nov 2026)."""
    v = fin.get("owned_compute_share")
    return float(default if v is None else v)


def effective_psi(p: Params, firm) -> float:
    """Tax deductibility of AI development (prop:acct-tax): finance.psi if set, else the domestic share at sec. 174A
    (psi = 1) and the foreign share amortized over 15 years (psi_15)."""
    if p.finance.psi is not None:
        return float(p.finance.psi)
    share = firm.org.get("domestic_dev_share") if firm is not None else None
    share = float(p.finance.domestic_dev_share if share is None else share)
    return float(F.tax_psi(math.expm1(p.finance.r), share, p.finance.psi_domestic, p.finance.psi_foreign_years))   # annual r for the sec. 174 schedule


def effective_psi_equipment(p: Params, firm) -> dict:
    """Tax deductibility of owned servers (prop:acct-tax(d)): finance.psi_equipment (current law for domestic servers:
    1) unless the firm reports a bonus election or a foreign server share, in which case formulas.psi_equipment."""
    fin = (firm.fin if firm is not None else {}) or {}
    el, fs = fin.get("bonus_election"), fin.get("foreign_server_share")
    if el is None and fs is None:
        v = float(p.finance.psi_equipment)
        return {"psi": v, "basis": "finance.psi_equipment (domestic servers, 100 percent allowance)" if v == 1.0 else "finance.psi_equipment"}
    out = F.psi_equipment(math.expm1(p.finance.r), str(el or "none"), float(fs or 0.0))
    out["basis"] = f"firm inputs: bonus election {el or 'none'}, foreign server share {float(fs or 0.0):.0%}"
    return out


def context_stock_mean(firm: Firm, p: Params) -> float:
    """E[m] of the context stock (prop:ext-continuity(a)), with documentation and context-engine coverage."""
    sh = p.shocks
    kdoc = firm.org.get("coverage", sh.kappa_doc)
    n_K = max(firm.org.get("key_persons_per_function", sh.key_persons_per_function) * len(firm.functions), 1.0)
    m, _ = F.context_stock(sh.nu_K, kdoc, sh.eta_K, n_K)
    return float(np.clip(m, 0.0, 1.0))


def build_econ(firm: Firm, p: Params, horizon: int | None = None, overrides: dict | None = None) -> Econ:
    """Assemble every unit cost. `overrides` may carry scenario arrays (for example an energy-price path)."""
    ov = overrides or {}
    Ut = firm.units.reset_index(drop=True)
    Pr = firm.processes.reset_index(drop=True)
    T = int(horizon or p.constraints.horizon_years)
    nU = len(Ut)
    pidx = {pid: i for i, pid in enumerate(Pr.process_id)}
    up = Ut.process_id.map(pidx).values.astype(int)
    part1 = firm.part1
    tau = float(firm.fin.get("tax_rate") or p.finance.tau)
    r = p.finance.r                                           # continuous (to_continuous at load)
    psi = effective_psi(p, firm)
    Ups = F.tax_wedge_capital(psi, tau)
    psi_eq = effective_psi_equipment(p, firm)
    Ups_K = F.tax_wedge_capital(psi_eq["psi"], tau)          # servers: bonus allowance, election or ADS (prop:acct-tax(d))
    hpf = p.labor.hours_per_fte
    g = float(part1["g"])
    years = firm.base_year + np.arange(T) + 0.5
    yidx = np.arange(T)
    vf = (1.0 + g) ** yidx
    rates = role_rates(firm, p)
    cap, pr, rv, sec = p.capability, p.prices, p.review, p.security

    # ---- unit attributes -----------------------------------------------------------------------
    w = Ut.wage_h.values.astype(float)                       # loaded $/h
    w_hat = F.effective_wage(w, p.permissibility.omega_h, tau)
    t = Ut.t.values.astype(float)
    v = Ut.v.values.astype(float)
    d = Ut.d.values.astype(float)
    ex = Ut.exposure.values.astype(float)
    phys = (Ut.physical.values >= cap.physical_threshold).astype(float)
    qbar = Ut.r_bar.values.astype(float)
    regc = Ut.regulated_class.values.astype(str)
    lic = Ut.licensed_share.values.astype(float)
    base_O = (Ut.baseline == "O").values
    cogs = (Ut.cost_bucket == "cogs").values
    L_err = Ut.L_mult.values * w * t                          # loss per undetected error
    cf = Ut.customer_facing.values > 0
    eth = Ut.ethics_sensitive.values > 0
    proc = Pr.iloc[up]
    data_class = proc.data_class.astype(str).values
    sens_map = sec.class_sensitivity
    sens = np.array([sens_map.get(c, 0.3) for c in data_class])
    writes = proc.write_access.astype(float).values
    ext_in = proc.external_inputs.astype(float).values
    n_sys = proc.n_systems_p.astype(float).values
    N_int = Ut.N_int.values.astype(float) if "N_int" in Ut else np.ones(nU)

    # ---- readiness levels ----------------------------------------------------------------------
    iota0 = Pr.iota0.values.astype(float)
    targets = list(p.readiness.targets)
    lv = [iota0] + [np.maximum(iota0, tg) for tg in targets]
    iota = np.stack(lv, axis=1)                               # (P, L)
    L = iota.shape[1]
    level_ok = np.ones((len(Pr), L), bool)
    for l in range(1, L):
        level_ok[:, l] = iota[:, l] > iota[:, l - 1] + 1e-6
    m_ctx = context_stock_mean(firm, p)
    iu = iota[up] * m_ctx ** p.shocks.ctx_iota_loss           # lost context lowers effective readiness
    iu = np.where((Ut.personal_data.values > 0)[:, None], np.minimum(iu, p.readiness.personal_data_cap), iu)
    # data residency (prop:labor-residency(a)): personal data that cannot be used in the vendor's region caps
    # readiness at (1 - omega^res) iota, omega^res the restricted share of the function's sites
    byf = (firm.org.get("jurisdiction") or {}).get("by_function") or {}
    omega_res = np.array([float((byf.get(str(fid)) or {}).get("omega_res", 0.0)) for fid in Ut.function_id.astype(str)])
    omega_res = omega_res * (Ut.personal_data.values > 0)
    in_region = np.array([float((byf.get(str(fid)) or {}).get("in_region", 0.0)) for fid in Ut.function_id.astype(str)])
    iu = F.residency_readiness(iu, omega_res[:, None])
    if "iota_scale" in ov:
        iu = np.clip(iu * ov["iota_scale"], 0, 1)
    if "iota_fixed" in ov:
        iu = np.full_like(iu, ov["iota_fixed"])

    # ---- capability (ext 3.2; modern map change 4) ------------------------------------------------
    agi = cap.agi_year
    plateau = cap.plateau_year
    t_now = float(firm.base_year)
    form = cap.chi_form
    slow_phys = cap.physical_mode == "slow_doubling"
    Hc = F.capability_horizon(years, cap.H0_hours, cap.t0, cap.Td_years, agi, plateau)                     # (T,)
    if slow_phys:
        Hp = F.capability_horizon_physical(years, cap.H0_hours, cap.t0, cap.Td_years, cap.L_W, cap.Td_physical_years, plateau)
        H0_phys = cap.H0_hours * 2.0 ** (-cap.L_W / cap.Td_years)
    else:
        Hp = F.capability_horizon(years - cap.L_W, cap.H0_hours, cap.t0, cap.Td_years, None, plateau)
        H0_phys = cap.H0_hours
    Hcal = np.where(phys[:, None] > 0, Hp[None, :], Hc[None, :])                               # (U, T)
    coverage = float(firm.fin.get("context_engine") or 0.0)
    coverage = max(coverage, float(firm.org.get("context_engine_coverage") or 0.0), cap.context_coverage)
    kap = F.kappa_ctx(iu, coverage, cap.xi_context)                                            # (U, L)
    gui = _gwa_match(Ut.gwa_id.astype(str).values, cap.computer_use_gwas) & (phys < 1)
    if cap.domain_mode == "domain":
        # work done through user interfaces (no API at this readiness) runs at the computer-use horizon
        kap = kap * np.where(gui[:, None] & (iu < cap.api_readiness), cap.computer_use_mult, 1.0)
    d_eff = F.effective_task_length(d, ex, cap.transfer, cap.xi_exposure, cap.exposure_floor)  # (U,)
    chiA = float(F.chi_reliability(cap.r_A, cap.eta_r, form))
    chiU = float(F.chi_reliability(cap.r_U, cap.eta_r, form))
    H0_u = np.where(phys > 0, H0_phys, cap.H0_hours)
    Td_u = np.where((phys > 0) & slow_phys, cap.Td_physical_years, cap.Td_years)
    calH = F.doublings_needed(d_eff[:, None], chiA, H0_u[:, None], kap)                       # (U, L)
    T_F = F.feasibility_date(t_now, cap.t0, Td_u[:, None], calH, 0.0 if slow_phys else cap.L_W,
                             phys[:, None], plateau)                                           # (U, L)
    if agi is not None:
        T_F = np.where(phys[:, None] > 0, T_F, np.minimum(T_F, max(agi, t_now)))
    capA = years[None, None, :] >= T_F[:, :, None]                                             # (U, L, T)
    with np.errstate(divide="ignore", invalid="ignore"):
        lm = np.log(np.where(np.isinf(Hcal[:, None, :]), 1e6, Hcal[:, None, :] * kap[:, :, None])
                    / np.maximum(d_eff[:, None, None] * chiA, 1e-12))
    log_margin = np.clip(lm, -20, 20)
    capU = (np.where(np.isinf(Hcal), np.inf, Hcal)[:, None, :] * kap[:, :, None]) >= (d_eff * chiU)[:, None, None]
    e_cap = F.capability_error(d_eff[:, None, None], Hcal[:, None, :] * kap[:, :, None], cap.logistic_slope_b, form)
    e_ctx = F.raw_error_readiness(iu, cap.e0, cap.e1)                                          # (U, L)
    e_raw = F.combine_errors(e_ctx[:, :, None], e_cap)                                         # (U, L, T)
    read_ok = iu >= Ut.iota_min.values[:, None] - 1e-12                                        # (U, L)

    # ---- permissibility (spec 5; ext 3.1) -------------------------------------------------------
    pm = p.permissibility
    excluded = Ut.activity_id.isin(set(pm.ethics_exclusions)).values | Ut.gwa_id.isin(set(pm.ethics_exclusions)).values
    if pm.exclude_sensitive:
        excluded |= eth
    licensed = (lic >= pm.licensed_share_threshold) | (regc == "licensed")
    allowed_rank = CLASS_RANK.get(str(firm.security.get("risk_appetite_max_class") or pm.risk_appetite_max_class), 3)
    data_allowed = np.array([CLASS_RANK.get(c, 1) <= allowed_rank for c in data_class])
    permA = ~excluded & ~(licensed & bool(pm.licensed_blocks_A)) & (regc != "prohibited") & data_allowed
    permU = ~excluded & (regc != "prohibited") & data_allowed
    permN = ~excluded & ~licensed
    permO = ~((Ut.personal_data.values > 0) & bool(pm.offshore_block_personal_data))
    xi_min = np.where(regc == "high_risk_eu", rv.xi_min_high_risk,
                      np.where(regc == "licensed", rv.xi_min_licensed, rv.xi_min_none))

    # ---- inference prices (ext 3.2) -------------------------------------------------------------
    energy = np.asarray(ov.get("energy_path", np.full(T, pr.energy_index)), dtype=float)[:T]
    cmult = _class_multiplier(Ut.gwa_id.values, pr.class_multiplier)
    TF_eff = np.where(np.isfinite(T_F), np.maximum(T_F, t_now), np.inf)
    price_at_TF = pr.pi_h0 * pr.frontier_factor ** np.maximum(np.where(np.isfinite(TF_eff), TF_eff, t_now) - pr.t_ref, 0.0)
    price = F.inference_price(years[None, None, :], TF_eff[:, :, None], price_at_TF[:, :, None], pr.delta_pi,
                              pr.floor_share * pr.pi_h0, pr.s_E, energy[None, None, :])        # (U, L, T) $/human-hour
    retry = 1.0 / (1.0 - np.minimum(e_cap, pr.retry_cap))
    own = owned_compute_share(firm.fin, p.capital.owned_compute_share)
    rent_fac = (1.0 - own) + own * p.capital.owned_opex_share
    piA_n = price * cmult[:, None, None] * t[:, None, None] * retry                            # market value of inference
    infA = piA_n * rent_fac * (1.0 + pr.tau_A) * (1.0 + sec.finops_share)                    # cash spend per unit
    priceU = F.inference_price(years[None, :], np.full((nU, 1), t_now), pr.pi_h0, pr.delta_pi,
                               pr.floor_share * pr.pi_h0, pr.s_E, energy[None, :])           # mature tools
    infU = priceU * cmult[:, None] * t[:, None] * pr.u_tok * rent_fac * (1.0 + pr.tau_A)     # (U, T)
    K_A = own * p.capital.compute_capital_per_annual_dollar * piA_n + \
        (phys * p.capital.robot_capital_per_fte * t / hpf)[:, None, None]                     # (U, L, T)
    dK_A = np.where(phys[:, None, None] > 0, p.capital.delta_K_robot, p.capital.delta_K_compute)

    # ---- review and quality (core 4.2 with detection rate; core 4.13 when the failure taxonomy is on) --------
    rl = p.reliability
    w_rev = w * rv.wage_premium                                   # expertise-adjusted review wage w^R >= w
    w_tR = w_rev * rv.rho_rev * t
    w_hat_rev = F.effective_wage(w_rev, pm.omega_h, tau)
    rel = failure_model(Ut, p, e_raw, e_cap, iu, d_eff, ext_in, writes, L_err, w_rev, w_hat_rev, t, qbar, xi_min,
                        regc, firm) if rl.enabled else None
    if rel is not None:
        xi, eps, cQ, cQ_hat = rel["xi"], rel["resid"], rel["cost_cash"], rel["cost_choice"]
    else:
        xi = F.review_share(e_raw, L_err[:, None, None], w_tR[:, None, None], qbar[:, None, None], xi_min[:, None, None], rl.d_e)
        cQ = F.quality_cost(xi, e_raw, L_err[:, None, None], w_tR[:, None, None], rl.d_e)
        eps = F.residual_error(e_raw, xi, rl.d_e)
        cQ_hat = F.quality_cost(xi, e_raw, L_err[:, None, None], (w_hat_rev * rv.rho_rev * t)[:, None, None], rl.d_e)
    # data residency: in-region deployment premium on inference for sensitive data where residency applies
    # in-region deployment (prop:labor-residency(c)): the regional price premium p^reg on the in-region share of
    # personal-data units
    p_reg = float(firm.org.get("vendor_region_premium") if firm.org.get("vendor_region_premium") is not None else p.residency.p_reg)
    resid_prem = 1.0 + p_reg * in_region * (Ut.personal_data.values > 0)
    infA = infA * resid_prem[:, None, None]
    piA_n = piA_n * resid_prem[:, None, None]

    # ---- builds (spec 3; core 4.1) ----------------------------------------------------------------
    bd = p.build
    scope = np.maximum(Ut.hours.values / hpf, 0.05) ** bd.scope_elasticity
    reg_any = unit_regulated(Ut)        # explicit attribute (class, ICFR, high-risk, licensed), not the reliability target
    months = bd.em_base * (1.0 + d) ** bd.xi_d * np.where(reg_any, bd.regulated_mult, 1.0) * \
        np.where(phys > 0, bd.physical_mult, 1.0) * scope
    FA0 = months * rates["ai_engineer_month"] * (1.0 + bd.vendor_share)
    decline = (1.0 - bd.delta_F) ** yidx                                                    # (T,)
    FA = FA0[:, None] * decline[None, :]                                                     # (U, T)
    FU = bd.U_share * FA
    FN = (bd.redesign_months * rates["process_owner_month"]) * np.ones(nU)[:, None] * decline[None, :]
    a_crf = float(F.capital_recovery_factor(r, bd.T_A))
    reval_f = float(F.revalidation_factor(r, sec.T_up))
    run_A = sec.delta_M * FA + sec.reval_share * FA * reval_f + sec.c_int * N_int[:, None]   # (U, T) $/yr
    run_U = sec.delta_M * FU + sec.reval_share * FU * reval_f

    # ---- security exposure and incidents (core 4.12) ---------------------------------------------------
    reach = np.clip(n_sys / max(p.readiness.n_systems_ref * 2, 1.0), 0, 1)
    Om_A = F.exposure_score(sens, sec.autonomy_A * writes, reach, ext_in)
    Om_U = F.exposure_score(sens, sec.autonomy_U * writes, reach * 0.5, ext_in)
    L_inc = np.array([sec.L_inc.get(c, 0.15) for c in data_class]) * sec.breach_avg * sec.per_process_share * sec.L_inc_scale
    Cinc_A = F.incident_cost(Om_A, sec.h_f, sec.h_u, v, L_inc)
    Cinc_U = F.incident_cost(Om_U, sec.h_f, sec.h_u, v, L_inc)
    # stand-alone risk cost of U (augmentation is secured per activity); A's risk is pooled per process in plans.py
    risk_U = F.risk_cost(Cinc_U, sec.C_s)

    # ---- penalties (spec 5; ext 3.1) ----------------------------------------------------------------
    X = float(part1["X"])
    Xh = F.X_hat(X, psi, tau, float(part1["k"]))
    Cc = np.where(cf, F.customer_penalty(Xh, pm.delta_G, part1["Delta_star"], pm.delta_lambda, part1["S"], np.maximum(v, 1e-9)), 0.0)
    om = np.where(eth, pm.omega * w * t, 0.0)

    # ---- mode costs -----------------------------------------------------------------------------------
    vt = np.maximum(v, 1e-9)
    ct = np.full((nU, L, T, NM), np.inf)
    cash = np.full((nU, L, T, NM), np.inf)
    o = p.outsourcing
    fn_rho = firm.functions.set_index("function_id").rho_O
    rho_O = Ut.function_id.map(fn_rho).astype(float).values
    rho_O = np.where(np.isfinite(rho_O), rho_O, o.rho_O_default)
    vend_u = np.where(base_O, Ut.vendor_spend.values / vt, 0.0)
    pO = np.where(base_O[:, None], vend_u[:, None] * (1 - o.delta_O) ** yidx[None, :],
                  F.vendor_price(rho_O[:, None], w[:, None], t[:, None], o.delta_O, yidx[None, :]))      # (U, T)
    cO_cash = F.cost_O(pO, o.kappa_O, w[:, None], t[:, None], o.zeta_O * w[:, None] * t[:, None])
    cO_ct = F.cost_O(pO, o.kappa_O, w_hat[:, None], t[:, None], o.zeta_O * w[:, None] * t[:, None])
    cH_cash = F.cost_H(w, t)
    cH_ct = F.cost_H(w_hat, t)
    betaU = p.augment.beta_U * ex / p.augment.exposure_ref
    tU = F.augment_hours(t, np.maximum(betaU, -0.5))
    # augmentation quality term (modern map change 2): blended work errs more on decision tasks, less on creation
    ag = p.augment
    gw = Ut.gwa_id.astype(str).values
    ttype = Ut["task_type"].astype(str).values if "task_type" in Ut else np.where(
        _gwa_match(gw, ag.decision_gwas), "decision", np.where(_gwa_match(gw, ag.creation_gwas), "creation", "other"))
    e_U = F.augment_quality_error(ag.e_H, ttype, ag.u_decision, ag.u_creation)
    dqU = (e_U - ag.e_H) * L_err                                   # change in expected error loss per unit vs in house
    cU_cash = F.cost_U(w[:, None], tU[:, None], infU) + (run_U + risk_U[:, None]) / vt[:, None] + dqU[:, None]
    cU_ct = (F.cost_U(w_hat[:, None], tU[:, None], 0.0) + (1 + pr.tau_A) * infU + Ups * FU * a_crf / vt[:, None]
             + (run_U + risk_U[:, None]) / vt[:, None] + 0.3 * om[:, None] / (1 - tau) + 0.2 * Cc[:, None] + dqU[:, None])
    cA_cash = infA + cQ                                                                       # run and risk costs: process level
    cA_ct = (infA + cQ_hat + Ups_K * F.capital_charge(K_A, r, dK_A)
             + Ups * (FA * a_crf)[:, None, :] / vt[:, None, None] + (om / (1 - tau) + Cc)[:, None, None])
    cN_cash = F.cost_N(p.eliminate.delta_N * w * t)
    cN_ct = cN_cash + Ups * FN[:, 0] * a_crf / vt + om / (1 - tau) + Cc

    for l in range(L):
        ct[:, l, :, H] = np.where(base_O[:, None], np.inf, cH_ct[:, None])
        cash[:, l, :, H] = np.where(base_O[:, None], np.inf, cH_cash[:, None])
        ct[:, l, :, O] = cO_ct
        cash[:, l, :, O] = cO_cash
        ct[:, l, :, U] = cU_ct
        cash[:, l, :, U] = cU_cash
        ct[:, l, :, N] = cN_ct[:, None]
        cash[:, l, :, N] = cN_cash[:, None]
    ct[:, :, :, A] = cA_ct
    cash[:, :, :, A] = cA_cash

    # ---- feasibility -------------------------------------------------------------------------------
    sep_ok = Ut.separable.values >= o.separable_threshold
    tech = np.zeros((nU, L, T, NM), bool)
    tech[:, :, :, H] = ~base_O[:, None, None]
    tech[:, :, :, O] = (base_O | sep_ok)[:, None, None]
    tech[:, :, :, U] = capU & ((ex > 0.05) & (phys < 1))[:, None, None] & (betaU > 0)[:, None, None]
    relA = eps <= (1 - qbar)[:, None, None] + 1e-12 if rel is None else rel["ok"]
    if rel is None:
        rel_floor = e_raw * (1 - rl.d_e) > (1 - qbar)[:, None, None]      # detection threshold (modern map change 1)
    else:
        rel_floor = ~rel["review_feasible"]
    tech[:, :, :, A] = capA & read_ok[:, :, None] & relA
    tech[:, :, :, N] = ((Ut.eliminable.values > 0)[:, None] & (iu >= p.readiness.iota_N))[:, :, None]
    perm = np.stack([np.ones(nU, bool), permO, permU, permA, permN], axis=1)              # (U, NM)
    feas = tech & perm[:, None, None, :]
    feas[:, :, :, O] |= base_O[:, None, None]                                              # the baseline stays available
    ct = np.where(feas, ct, np.inf)
    cash = np.where(feas, cash, np.inf)

    # ---- residual own hours per unit (people module) --------------------------------------------------
    res = np.zeros((nU, L, T, NM))
    res[:, :, :, H] = t[:, None, None]
    res[:, :, :, O] = (o.kappa_O * t)[:, None, None]
    res[:, :, :, U] = tU[:, None, None]
    res[:, :, :, A] = xi * rv.rho_rev * t[:, None, None] + (lic * t * 0.1)[:, None, None]
    res[:, :, :, N] = 0.0
    inference = np.zeros((nU, L, T, NM))
    inference[:, :, :, A] = infA
    inference[:, :, :, U] = infU[:, None, :]
    Kfull = np.zeros((nU, L, T, NM))
    Kfull[:, :, :, A] = K_A
    Fb = np.zeros((nU, T, NM))
    Fb[:, :, A] = FA
    Fb[:, :, U] = FU
    Fb[:, :, N] = FN
    runm = np.zeros((nU, T, NM))
    runm[:, :, A] = run_A
    runm[:, :, U] = run_U
    Cinc = np.zeros((nU, NM))
    Cinc[:, A] = Cinc_A
    Cinc[:, U] = Cinc_U
    Om = np.zeros((nU, NM))
    Om[:, A] = Om_A
    Om[:, U] = Om_U
    cm = p.competition
    hhi = float(firm.fin.get("market_hhi") or cm.hhi)
    phi_ind = firm.fin.get("industry_pass_through") if firm.fin.get("industry_pass_through") is not None else cm.phi_ind
    game = F.game_shares(hhi, phi_ind, cm.curvature_e, cm.rep)
    # the derived homogeneous-Cournot pass-through, reported as a benchmark beside the central value (Paper 2,
    # calibration of the industry pass-through; it lies above the scenario set {0, 0.5, 0.7})
    bench = F.game_shares(hhi, None, cm.curvature_e, cm.rep)
    game["cournot"] = {"phi_ind": bench["phi_ind"], "dur": bench["dur"], "dur_rep": bench["dur_rep"], "priv": bench["priv"]}
    game["phi_ind_source"] = ("firm input industry_pass_through" if firm.fin.get("industry_pass_through") is not None else
                              ("derived (Cournot)" if cm.phi_ind is None else "competition.phi_ind"))
    # Part I round 2 (B1; notes/r2_code_changes.md): phi_ind is the industry pass-through RATE of a unit-cost saving every
    # rival makes, and margins are computed at the post-cut price, so to first order a replicated saving keeps the share
    # 1 - phi C0 of its margin gain, C0 = 1 - f - m0 today's non-fee unit cost per dollar of price (the elasticity of Part I
    # lem:prices is phi C0). HHI does not enter the margin share; dur = 1 - phi (1 - HHI) (cor:ext-game-engine(a)) is the
    # share of the DOLLAR saving a Cournot firm keeps once its volume gain is counted, and values plans in dollars only.
    pt1 = firm.part1
    pt_rate = F.passthrough_terms(float(pt1["m0"]), float(pt1.get("f") or 0.0), float(game["phi_ind"]) * float(cm.rep),
                                   float(p.finance.pass_through_phi))
    info = {"omega_res": omega_res, "in_region": in_region, "durable_share": float(game["dur_rep"]), "pass_through": pt_rate,
            "game": game, "psi_tax": psi, "psi_equipment": psi_eq, "Ups_K": Ups_K, "Hc": Hc, "Hp": Hp, "kap": kap, "d_eff": d_eff, "chiA": chiA, "e_cap": e_cap, "cQ": cQ, "piA_n": piA_n,
            "price": price, "w": w, "t": t, "v": v, "tau": tau, "Ups": Ups, "a_crf": a_crf, "reval_f": reval_f,
            "FA0": FA0, "L_err": L_err, "w_tR": w_tR, "xi_min": xi_min, "cogs": cogs, "m_ctx": m_ctx, "coverage": coverage,
            "permA": permA, "permU": permU, "excluded": excluded, "licensed": licensed, "read_ok": read_ok,
            "capA": capA, "sens": sens, "data_class": data_class, "L_inc": L_inc, "risk_U": risk_U, "dK_A": dK_A,
            "betaU": betaU, "N_int": N_int, "Cc": Cc, "om": om, "w_hat": w_hat, "reliability": rel,
            "writes": writes, "ext_in": ext_in, "task_type": ttype, "dqU": dqU, "gui": gui, "not_automatable_review": rel_floor,
            "chi_form": form, "e_ctx": e_ctx}
    return Econ(firm=firm, p=p, T=T, L=L, years=years, vf=vf, unit_proc=up, iota=iota, iota_u=iu, level_ok=level_ok,
                feas=feas, ct=ct, cash=cash, base_mode=np.where(base_O, O, H), F_build=Fb, K=Kfull, run=runm,
                C_inc=Cinc, eps=eps, xi=xi, e_raw=e_raw, log_margin=log_margin, T_F=T_F, res_hours=res,
                inference=inference, exposure_sec=Om, perm=perm, tech=tech, data_allowed=data_allowed,
                rates=rates, info=info)


# =================================================================================================
# AI failure modes and autonomy (spec 23)
# =================================================================================================

def _gwa_match(ids, prefixes) -> np.ndarray:
    """Element-wise prefix match of activity ids (vectorized over the unique ids)."""
    pre = tuple(str(x) for x in prefixes)
    ids = np.asarray(ids, dtype=object)
    if not pre or not len(ids):
        return np.zeros(len(ids), bool)
    uniq, inv = np.unique(ids.astype(str), return_inverse=True)
    hit = np.fromiter((u.startswith(pre) for u in uniq), bool, len(uniq))
    return hit[inv]


def failure_model(Ut, p, e_raw, e_cap, iu, d_eff, ext_in, writes, L_err, w_rev, w_hat_rev, t, qbar, xi_min, regc, firm) -> dict:
    """Failure taxonomy of mode A and the autonomy choice (core 4.13; spec 23.1). Ordinary errors e_o (from
    readiness and capability) and hallucinations e_h are caught at rates d_o and d_h (d_h lower on open-ended
    tasks), with complacency lowering both as AI accuracy rises (params_reliability.yaml automation_bias) and a
    vigilance cap exp(-eps_d) on the review share (prop:tasks-bias). For each automated level, act with approval
    (2: every action approved at the approval thoroughness) and act autonomously (3: stakes-targeted review),
    the cost per unit is w t(a) + c_Q(a) + c_m(a), with misbehavior c_m(a) = e_m(a)(1 - d_m(a)) L_m E min{Z, L_cap/L_m}
    under least privilege, monitoring and a kill switch. A level is feasible if review can meet the reliability
    target (prop:tasks-halluc(b)) and the event CVaR is within the risk appetite (prop:tasks-autonomy(a)).
    Irreversible actions need approval when the firm's policy says so, and always when level 3 breaks the
    appetite (prop:tasks-autonomy(d)). Shapes follow e_raw (U, L, T)."""
    rl = p.reliability
    gwa = Ut.gwa_id.astype(str).values
    act = Ut.activity_id.astype(str).values
    open_ended = _gwa_match(gwa, rl.open_ended_gwas)
    irreversible = _gwa_match(gwa, rl.irreversible_gwas) | _gwa_match(act, rl.irreversible_gwas)
    high_stakes = (L_err >= rl.high_stakes_mult * (w_rev / max(p.review.wage_premium, 1e-9)) * t) | (regc != "none")
    h_type = np.where(open_ended, rl.h_open, rl.h_retrieval)
    e_o = np.clip(e_raw, 0, 1)
    e_h = F.hallucination_rate(h_type[:, None, None], iu[:, :, None], rl.grounding, e_cap, p.capability.r_A, rl.h_floor_share)
    e_h = np.minimum(e_h, 1 - e_o)
    acc = 1.0 - e_o - e_h
    d_h0 = np.where(open_ended, rl.d_h * rl.d_h_open_mult, rl.d_h)[:, None, None]
    d_o = F.catch_rate(rl.d_e, acc, rl.b_ab, rl.acc0)
    d_h = F.catch_rate(d_h0, acc, rl.b_ab, rl.acc0)
    Lb = L_err[:, None, None]
    qb = qbar[:, None, None]
    # misbehavior severity: Pareto scale and cap under least privilege, monitoring and a kill switch
    L_m = rl.sev_mult * L_err * (1 - rl.lp_cut * (writes > 0)) * (1 - rl.mon_cut)
    L_cap = rl.kill_cap_mult * L_m
    sec_in = firm.security or {}
    L_max = float(sec_in.get("max_tolerable_loss") or rl.L_max_event)
    cvar_ev = F.event_cvar(L_m, rl.alpha_tail, rl.cvar_q, L_cap)                 # (U,)
    appetite_ok = cvar_ev <= L_max
    shape = e_o.shape
    out = {}
    for name, code in (("act_with_approval", 2), ("act_autonomously", 3)):
        e_m = F.misbehavior_rate(rl.m0, rl.autonomy_mult[name], d_eff, rl.kappa_h, ext_in, rl.injection_mult, rl.guard_cut)
        e_m = np.broadcast_to(e_m[:, None, None], shape)
        if code == 2:
            th = rl.approval_thoroughness
            wtr, wtr_hat = (w_rev * rl.rho_appr * t)[:, None, None], (w_hat_rev * rl.rho_appr * t)[:, None, None]
            xi_k, rev_ok, und = F.review_share_tax(e_o, e_h, d_o * th, d_h * th, Lb, wtr, qb, 1.0)
            cq = F.quality_cost_tax(xi_k, e_o, e_h, d_o * th, d_h * th, Lb, wtr)
            cq_hat = cq - wtr * xi_k + wtr_hat * xi_k
            d_m = np.full(shape, rl.d_m_approval)
        else:
            wtr, wtr_hat = (w_rev * p.review.rho_rev * t)[:, None, None], (w_hat_rev * p.review.rho_rev * t)[:, None, None]
            xi_k, rev_ok, und = F.review_share_tax(e_o, e_h, d_o, d_h, Lb, wtr, qb, xi_min[:, None, None], rl.eps_d)
            cq = F.quality_cost_tax(xi_k, e_o, e_h, d_o, d_h, Lb, wtr)
            cq_hat = cq - wtr * xi_k + wtr_hat * xi_k
            d_m = 1.0 - (1.0 - rl.d_mon) * (1.0 - rl.d_m_review * xi_k)
        c_m = F.misbehavior_cost(e_m, d_m, L_m[:, None, None], L_cap[:, None, None], rl.alpha_tail)
        ok = rev_ok & appetite_ok[:, None, None]
        out[name] = dict(code=code, xi=xi_k, cost=cq + c_m, cost_hat=cq_hat + c_m, resid=und, ok=ok, rev_ok=rev_ok,
                         c_m=c_m, e_m=e_m, m_esc=e_m * (1 - d_m), cq=cq)
    a2, a3 = out["act_with_approval"], out["act_autonomously"]
    must_approve = irreversible & bool(getattr(rl, "irreversible_requires_approval", True))
    ok3 = a3["ok"] & ~must_approve[:, None, None]
    costs = np.stack([a2["cost_hat"], a3["cost_hat"]], axis=-1)
    feas = np.stack([a2["ok"], ok3], axis=-1)
    pick3 = feas[..., 1] & (~feas[..., 0] | (costs[..., 1] < costs[..., 0]))
    sel = lambda k: np.where(pick3, a3[k], a2[k])
    xi_s, resid_s, c_m_s = sel("xi"), sel("resid"), sel("c_m")
    d_o_s = np.where(pick3, d_o, d_o * rl.approval_thoroughness)
    d_h_s = np.where(pick3, d_h, d_h * rl.approval_thoroughness)
    c_err = F.error_floor_cost(xi_s, e_o, e_h, d_o_s, d_h_s, Lb, c_m_s)
    caught_share = np.where(e_o + e_h > 0, (e_o * d_o_s + e_h * d_h_s) * F.stakes_coverage(xi_s) / np.maximum(e_o + e_h, 1e-12), 0.0)
    Lam_unit = sel("m_esc")
    return {"autonomy": np.where(pick3, 3, 2), "xi": xi_s, "cost_cash": sel("cost"), "cost_choice": sel("cost_hat"),
            "resid": resid_s, "ok": a2["ok"] | ok3, "review_feasible": a2["rev_ok"] | a3["rev_ok"], "appetite_ok": appetite_ok,
            "m_esc": Lam_unit, "c_m": c_m_s, "EL_misbehavior": c_m_s, "cvar_event": cvar_ev, "h": e_h, "e_o": e_o,
            "d_o": d_o, "d_h": d_h, "sev_x": L_m, "cap": L_cap, "mean_sev": F.pareto_mean(rl.alpha_tail, L_m, L_cap),
            "c_err": c_err, "irony": F.irony_flag(caught_share, rl.eps_d), "irreversible": irreversible,
            "high_stakes": high_stakes, "open_ended": open_ended, "must_approve": must_approve, "levels": out}


# =================================================================================================
# The universe available to automate (spec 5; ext 3.1)
# =================================================================================================

def universe(econ: Econ, year: int | None = None, level: int | None = None) -> dict:
    """Four nested layers (feasible, permissible, preferred, economical), their spend shares, the value
    V_eco = sum_j v_j max(B_j, 0) a year, and the automation advantage B_j per unit, at plan year `year` and
    readiness `level` (default: three years out, best readiness)."""
    y = min(econ.T - 1, 2 if year is None else year)
    l = econ.L - 1 if level is None else level
    ct = econ.ct[:, l, y, :]
    v = econ.firm.units.v.values * econ.vf[y]
    x = econ.firm.units.base_cost.values * econ.vf[y]
    tech = econ.tech[:, l, y, :]
    perm = econ.perm
    nonai = ct[:, [H, O]]
    ai = ct[:, [U, A, N]]
    B = F.automation_advantage(nonai, ai)
    # preferred: an AI mode wins if machine spend, capital and builds were free (ext lem:ext-nested)
    ct0 = ct.copy()
    i = econ.info
    w_hat, t = i["w_hat"], i["t"]
    tU = F.augment_hours(t, np.maximum(i["betaU"], -0.5))
    ct0[:, U] = np.where(np.isfinite(ct[:, U]), F.cost_U(w_hat, tU, 0.0), np.inf)
    rel = i.get("reliability")
    cq0 = rel["cost_choice"][:, l, y] if rel is not None else F.quality_cost(
        econ.xi[:, l, y], econ.e_raw[:, l, y], i["L_err"], w_hat * econ.p.review.wage_premium * econ.p.review.rho_rev * t,
        econ.p.reliability.d_e)
    ct0[:, A] = np.where(np.isfinite(ct[:, A]), cq0, np.inf)
    ct0[:, N] = np.where(np.isfinite(ct[:, N]), econ.p.eliminate.delta_N * i["w"] * t, np.inf)
    B0 = F.automation_advantage(ct0[:, [H, O]], ct0[:, [U, A, N]])
    fea = tech[:, [U, A, N]].any(1)
    per = (tech[:, [U, A, N]] & perm[:, [U, A, N]]).any(1)
    pre = per & (B0 > 0)
    eco = per & (B > 0)
    wf = F.waterfall(x, fea, per, pre, eco)
    V = float(np.sum(v * np.where(eco, np.maximum(B, 0.0), 0.0)))
    return {"year": int(y), "level": int(l), "shares": wf, "V_eco": V, "B": B, "fea": fea, "per": per, "pre": pre,
            "eco": eco, "spend": x, "spend_total": float(x.sum())}
