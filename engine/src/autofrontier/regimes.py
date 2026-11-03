# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Ownership regimes (spec 16; theory_regimes.tex; notes/theory_regimes_notes.md Sections 3 and 4).

Presets switch the optimizer's objective and constraints: discount rate r_o (continuous: survey rates enter as
ln(1 + r)), horizon T_o, terminal rule (going concern, EBITDA exit with the capitalized share h_x of seasoned
run-rate, or the market rule frakA_T for a VC exit), myopia weight on GAAP dips beyond the guided slack, covenant
and budget. Regime outputs: the program value V_o, the PE capital hurdle zeta_pe, deal metrics with the
waterfall (MOIC, gross and net IRR) at h_x = 0.5 and 1, the EPS path against guidance, the dip budget and the
fastest wave ramp, the growth weight X_o, the take-private break-even, hybrids, and value by stakeholder.

Permanent capital (theory_acquirer.tex sec:acq-pc; notes/acquirer_notes.md Section 3): a never-selling owner that
holds internal decisions to its unlevered hurdle as a going concern (prop:acq-pc(d)) and buys at the method-IRR
hurdle with the disclosed debt policy; and the limits to buying growth (prop:acq-limits), each off at its neutral
value unless a scenario or an override sets it."""
from __future__ import annotations

import math

import numpy as np

from . import formulas as F
from .optimize import Regime

REGIMES = ("public", "private_family", "pe", "vc", "hybrid", "permanent_capital")


def _frakA(r, g, T, Ginf, theta):
    """Part I Lemma valuation2: marginal value of a margin dollar per dollar of revenue at T, A_T(eta) + theta eta^T
    (1 + G_inf)/(r - G_inf) with eta = (1 + g)/(1 + r)."""
    eta = (1 + g) / (1 + r)
    if r <= Ginf:
        return math.inf
    return sum(eta ** t for t in range(1, int(T) + 1)) + theta * eta ** T * (1 + Ginf) / (r - Ginf)


def make_regime(name: str, p, firm) -> Regime:
    """Preset for one regime (notes 4), with the firm's own inputs (tier3_regime, tier0) overriding presets. Rates
    are continuous: annual presets enter as ln(1 + r)."""
    rg, fn = p.regime, p.finance
    ri = firm.regime or {}
    bm = rg.budget_mult
    c = lambda x: x                    # presets are continuous at load (config.to_continuous)
    ann = math.expm1
    common = dict(g_tv=fn.terminal_growth, tv_cap=fn.terminal_multiple_cap)
    slack = float(ri.get("guided_slack") or rg.g_slack)
    info = {"h_x": rg.h_x, "T_sea": rg.T_sea, "g_slack": slack, "r_debt": c(rg.debt_rate), "c_tx": rg.c_tx,
            "Y_m": int(rg.Y_m), "annual_rate": None}
    if name == "public":
        reg = Regime("public", c(rg.public_r), None, "going_concern", None, rg.public_myopia, int(rg.Y_m), None, None,
                     rg.public_latency_mult, bm["public"] * (1 - 0.5 * float(ri.get("dividend_payout") or 0)), 0.0, **common)
        info["annual_rate"] = ann(rg.public_r)
    elif name == "private_family":
        reg = Regime("private_family", c(rg.public_r + rg.family_r_spread), None, "going_concern", None, 0.0, 0, None, None,
                     rg.family_latency_mult, bm["private_family"], rg.family_employment_pref, **common)
        info.update(annual_rate=ann(rg.public_r + rg.family_r_spread), horizon_years_file=rg.family_horizon)
    elif name == "pe":
        hold = float(ri.get("hold_years_total") or rg.pe_hold) - float(ri.get("hold_years_elapsed") or 0.0)
        target = F.cont_rate(float(ri["target_irr"])) if ri.get("target_irr") else rg.pe_irr_target   # firm input is annual
        M_exit = float(ri.get("exit_multiple") or rg.pe_M_exit)
        reg = Regime("pe", c(target), max(hold, 1.0), "ebitda_multiple", M_exit, 0.0, 0,
                     float(ri.get("covenant_max_leverage") or rg.pe_covenant), rg.pe_entry_leverage, rg.pe_latency_mult,
                     bm["pe"], 0.0, **common)
        # entry multiple = exit multiple (no multiple expansion) unless the firm supplies both
        EB0 = float(firm.fin.get("ebitda") or 0.0) or None
        M_entry = M_exit
        if ri.get("entry_ev") and ri.get("exit_multiple") and EB0:
            M_entry = float(ri["entry_ev"]) / EB0
        info.update(annual_rate=ann(target), M_entry=M_entry, pref=rg.pe_pref, carry=rg.pe_carry, fee=rg.pe_fee)
    elif name == "vc":
        g = float(firm.part1["g"])
        A = _frakA(ann(rg.public_r), min(g, 0.3), 10, float(firm.part1["G"]) * 0.5, rg.vc_theta)
        reg = Regime("vc", c(rg.vc_r), rg.vc_horizon, "ebitda_multiple", min(A, fn.terminal_multiple_cap * 2), 0.0, 0, None, None,
                     rg.pe_latency_mult * 1.2, bm["vc"], 0.0, **common)
        info.update(annual_rate=ann(rg.vc_r), terminal_rule="market (frakA_T)", frakA=A)
    elif name == "hybrid":
        reg = Regime("hybrid", c(rg.public_r), None, "going_concern", None, rg.hybrid_myopia, int(rg.Y_m),
                     None, None, 1.0, bm["hybrid"], 0.0, **common)
        info.update(annual_rate=ann(rg.public_r), kind="dual class", minority_board_weight=rg.minority_board_weight)
    elif name == "permanent_capital":
        # ass:acq-pc: never sells (going concern, no exit term); internal decisions at the unlevered hurdle
        # (prop:acq-pc(d)); debt ND_0 = min{LTV P, ND^rep}; covenant on consolidated leverage
        reg = Regime("permanent_capital", c(rg.pc_irr_unlevered), None, "going_concern", None, rg.pc_myopia,
                     int(rg.Y_m) if rg.pc_myopia > 0 else 0, float(ri.get("covenant_max_leverage") or rg.pc_covenant), None,
                     rg.pe_latency_mult, bm.get("permanent_capital", bm["pe"]), 0.0, **common)
        info.update(annual_rate=ann(rg.pc_irr_unlevered), irr_levered=rg.pc_irr_levered, irr_window=rg.pc_window_years,
                    ltv=rg.pc_ltv, repay_years=rg.pc_repay_years, r_tv=rg.pc_r_tv, r_debt=rg.pc_debt_rate,
                    kind="permanent capital (never sells)")
    else:
        raise ValueError(f"unknown regime '{name}'; choose one of {', '.join(REGIMES)}")
    reg.info.update(info)
    return reg


def firm_regime_name(p, firm) -> str:
    ri = firm.regime or {}
    name = ri.get("ownership_regime") or firm.fin.get("ownership_regime") or p.regime.default
    name = str(name).lower().strip()
    return {"private": "private_family", "family": "private_family", "pe_backed": "pe", "vc_backed": "vc", "pc": "permanent_capital",
            "permanent": "permanent_capital"}.get(name, name)


# -------------------------------------------------------------------------------------------------
# Regime-specific outputs (prop:reg-metrics, prop:reg-weight, prop:reg-dip, prop:reg-lbo, prop:reg-hybrid)
# -------------------------------------------------------------------------------------------------
def pe_returns(firm, reg: Regime, path: dict, h_values=(0.5, 1.0)) -> dict:
    """Deal metrics with and without the plan (prop:reg-metrics): entry at the exit multiple unless the firm gives
    both; debt lev0 x EBITDA0 accruing at r_debt, paid down by free cash flow; exit equity M_exit (EB^sq_T + h_x
    dEB_T) - ND_T, with dEB_T the run-rate seasoned T_sea before exit; MOIC, gross IRR, LP and net IRR after the
    waterfall. Reported at h_x = 0.5 and 1."""
    T_years = len(path["ebitda_base"])
    hold = int(min(max(round(reg.horizon or 5), 1), T_years))
    EB0 = float(path["ebitda_base"][0])
    ri = firm.regime or {}
    i = reg.info
    lev0 = float(firm.fin.get("net_debt")) / max(EB0, 1e-9) if firm.fin.get("net_debt") is not None and firm.fin["net_debt"] > 0 \
        else (reg.leverage or 0.0)
    times = np.arange(hold) + 0.5
    ys = int(max(hold - 1 - round(i["T_sea"]), 0))
    out = {"hold_years": hold, "entry_multiple": i["M_entry"], "exit_multiple": reg.M_exit, "entry_leverage": lev0,
           "note": "entry multiple equals the exit multiple (no multiple expansion) unless the firm supplies both"}
    for hx in h_values:
        for case, dEB, fcf in (("without_plan", 0.0, path["fcf_base"][:hold]),
                               ("with_plan", float(path["ebitda_delta"][ys]), path["fcf_base"][:hold] + path["cash_delta"][:hold])):
            m = F.pe_metrics(EB0, float(path["ebitda_base"][hold - 1]), dEB, fcf, times, hold, reg.M_exit, i["M_entry"], lev0,
                             i["r_debt"], hx, 0.0, i["c_tx"], i["pref"], i["carry"], i["fee"])
            out[f"{case}_hx{hx:g}"] = m
    # covenant path
    nd = lev0 * EB0 - np.cumsum(path["fcf_base"][:hold] + path["cash_delta"][:hold])
    eb = path["ebitda_base"][:hold] + path["ebitda_delta"][:hold]
    out["max_leverage_with_plan"] = float(np.max(nd / np.maximum(eb, 1e-9)))
    out["covenant"] = reg.covenant
    out["covenant_breach"] = bool(out["max_leverage_with_plan"] > (reg.covenant or np.inf))
    return out


def public_path(firm, path: dict, p, reg: Regime | None = None) -> dict:
    """EPS path against guidance (prop:reg-metrics): dEPS_y = (1 - tau) dOI_y / shares; guidance gap dOI_y + slack;
    first accretion year; Rule-of-40 path on cash and GAAP bases."""
    ri = firm.regime or {}
    tau = float(firm.fin.get("tax_rate") or p.finance.tau)
    shares = firm.fin.get("shares_outstanding")
    dOI = np.asarray(path["gaap_delta"], float)
    S = np.asarray(path["revenue"], float)
    slack = (reg.info.get("g_slack", 0.0) if reg is not None else p.regime.g_slack) * S
    out = {"delta_operating_income": dOI, "guidance_gap": dOI + slack}
    if shares:
        out["delta_eps"] = (1 - tau) * dOI / float(shares)
    neg = np.flatnonzero(dOI < 0)
    acc = [y for y in range(len(dOI)) if dOI[y] >= 0 and (len(neg) == 0 or y > neg.max())]
    out["accretion_year"] = int(path["years"][acc[0]]) if acc else None
    gr = ri.get("guidance_r40")
    if gr is not None:
        out["guidance_r40"] = float(gr)
        out["years_below_r40_guidance_gaap"] = [int(path["years"][y]) for y in np.flatnonzero(path["r40_gaap"] < float(gr))]
        out["years_below_r40_guidance_cash"] = [int(path["years"][y]) for y in np.flatnonzero(path["r40_cash"] < float(gr))]
    out["max_gaap_dip_points"] = float(path["dip_gaap_points"])
    return out


def growth_weight(firm, reg: Regime, p) -> dict:
    """The regime's growth weight X_o (prop:reg-weight): going concern v0 at r_o (smallest root of the Gordon
    equation), myopic X^my, hold-and-exit X^x at entry, VC with the market rule."""
    pt = firm.part1
    k, G = float(pt["k"]), float(pt["G"])
    v0 = F.gordon_v0(pt["m0"], G, k, pt["ell"], reg.r, pt["alpha"])
    X_gc = v0 if v0 is not None else float(pt["X"])
    out = {"X_going_concern": v0, "unbounded_at_small_share": v0 is None}
    X_in = firm.fin.get("ev_revenue_multiple")
    if X_in and float(firm.fin.get("multiple_is_net_of_pressure") or 0) >= 0.5:
        # the input multiple is a public filer's revealed weight, already net of earnings pressure (prop:reg-weight(b)
        # read backwards; synthesis theorist W14): the going-concern weight is k + (1 + w)(X_in - k)
        w_pub = float(p.regime.public_myopia)
        X_gc = k + (1 + w_pub) * (float(X_in) - k)
        out["X_going_concern_from_net_multiple"] = X_gc
    # the margin a marginal permanent dollar of revenue earns (prop:reg-weight(c) with prop:dynamic(a)): m0 - k G, not
    # the firm's current cash margin, which is net of today's growth spend (both are reported)
    m_perm = float(pt["m0"]) - k * G
    out["m_hat"] = m_perm
    out["m_hat_basis"] = "m0 - k G (prop:dynamic(a))"
    if reg.name == "permanent_capital":
        # prop:acq-pc(d): X^G = m_hat/(i_bar_U - G) for a permanent owner at its unlevered hurdle
        # defined only when G < i_U (prop:acq-pc(d)); None otherwise (W15)
        X = F.pc_growth_weight(m_perm, reg.r, G)
        out["X_permanent_capital"] = X
        out["X_permanent_capital_at_m_cash"] = F.pc_growth_weight(float(pt["m_cash"]), reg.r, G)
        if reg.myopia > 0:
            out["X_myopic"] = F.myopic_weight(X, k, reg.myopia)
            X = out["X_myopic"]
    elif reg.myopia > 0:
        out["X_myopic"] = F.myopic_weight(X_gc, k, reg.myopia)
        X = out["X_myopic"]
    elif reg.terminal == "ebitda_multiple" and reg.horizon:
        # the EBITDA a permanent dollar of revenue adds at exit is m0 (W15), not the whole firm's m_op + D&A
        mE = float(pt["m0"])
        X_T = reg.info.get("h_x", 1.0) * reg.M_exit * mE if reg.name == "pe" else reg.M_exit * mE
        out["X_exit_at_entry"] = F.exit_weight(m_perm, reg.r, G, float(reg.horizon), X_T)
        out["X_exit_at_entry_at_m_cash"] = F.exit_weight(float(pt["m_cash"]), reg.r, G, float(reg.horizon), X_T)
        X = out["X_exit_at_entry"]
    else:
        X = X_gc
    if reg.info.get("minority_board_weight"):
        X = F.hybrid_weight(X_gc, X, reg.info["minority_board_weight"])
        out["X_hybrid_minority"] = X
    out["X_o"] = X
    return out


def dip_ramp(sol, prog, econ, reg: Regime, p) -> dict:
    """Dip budget and the fastest wave ramp (prop:reg-dip) for the plan's processes, with a linear dip per process:
    PE: Dhat(n) = T_1 n + w_cov levbar D n, shat = w_cov levbar s - T_1, B = (levbar - lev0) EB_0; public: Dhat = D,
    shat = s, B = guided slack x S. Waves start small and grow as savings from earlier waves fund later dips."""
    cols = prog.cols
    sel = list(sol.sel.values())
    if not sel:
        return {"applicable": False}
    D = float(np.median([max(-(cols.gaap0[c][min(int(cols.start[c]), econ.T - 1)] + sol.varpi[c] * cols.gaap1[c][min(int(cols.start[c]), econ.T - 1)]), 0.0)
                         for c in sel]))
    s = float(np.median([max(cols.detail[c]["W"][min(cols.detail[c]["y0"] + 1, econ.T - 1)], 0.0) * float(sol.varpi[c]) for c in sel]))
    T1 = float(np.median([cols.detail[c]["F"] + cols.detail[c]["I"] for c in sel]))
    N = len(sel)
    S0 = float(econ.firm.part1["S"])
    if reg.name == "pe":
        EB0 = float(prog.ebitda_base[0])
        lev0 = reg.leverage or 0.0
        B = (float(reg.covenant or 0) - lev0) * EB0
        wc = p.regime.w_cov
        Dhat = lambda n: T1 * n + wc * (reg.covenant or 0) * D * n
        shat = wc * (reg.covenant or 0) * s - T1
    else:
        B = reg.info.get("g_slack", 0.0) * S0
        Dhat = lambda n: D * n
        shat = s
    ramp = F.fastest_ramp(Dhat, max(shat, 0.0), B, N) if B > 0 else []
    deadline = None
    if reg.horizon and reg.terminal == "ebitda_multiple":
        Tp = float(np.median([cols.detail[c]["T_par"] for c in sel]))
        deadline = int(math.floor((float(reg.horizon) - reg.info.get("T_sea", 1.0)) / max(Tp, 0.25)))
    return {"applicable": True, "processes": N, "dip_per_process": D, "saving_per_process": s, "one_time_cash_per_process": T1,
            "budget": B, "fastest_ramp": ramp, "waves_needed": len(ramp) if ramp and sum(ramp) >= N else None,
            "wave_deadline": deadline, "plan_launches_by_year": np.bincount([int(cols.start[c]) for c in sel], minlength=econ.T).tolist(),
            "note": "no dip budget: the soft myopia penalty applies instead" if B <= 0 else ""}


def capital_hurdle(sol, prog, econ, reg: Regime, p) -> list[dict]:
    """PE capital hurdle zeta_pe (prop:reg-value(c)) against each capital-using switch's Dc/DK, with the flag for
    switches that pass the sponsor's test but fail the public value test (r_w + delta_K), or the reverse."""
    out = []
    if reg.name != "pe" or not reg.horizon:
        return out
    r_w = p.regime.public_r
    for c in sol.sel.values():
        d = prog.cols.detail[c]
        if d["K"] <= 0:
            continue
        y = min(d["y0"] + 1, econ.T - 1)
        ratio = max(d["W"][y], 0.0) / d["K"]
        rows = {"process_id": econ.firm.processes.process_id.iat[int(prog.cols.proc[c])], "dc_over_dK": ratio,
                "public_hurdle": r_w + d["dK"]}
        for hx in (0.5, 1.0):
            z = F.zeta_pe(reg.r, float(reg.horizon), reg.M_exit, d["dK"], hx)
            rows[f"zeta_pe_hx{hx:g}"] = z
            rows[f"sponsor_adopts_hx{hx:g}"] = bool(ratio > z)
        rows["regimes_disagree"] = bool((ratio > rows["zeta_pe_hx1"]) != (ratio > rows["public_hurdle"]))
        out.append(rows)
    return out


def lbo(firm, econ, sides: dict, p) -> dict:
    """Take-private break-even (prop:reg-lbo) for a public firm: sponsor value of the PE plan, frakL, the largest
    premium the sponsor can pay and whether it covers the required control premium; and the frictionless benchmark
    (value of the sponsor's program minus the public owner's, at the public rate)."""
    if "pe" not in sides or "public" not in sides:
        return {"applicable": False}
    pe = sides["pe"]
    reg = pe["regime"]
    path = pe["path"]
    T = int(min(max(round(reg.horizon or 5), 1), len(path["ebitda_base"])))
    EB0 = float(path["ebitda_base"][0])
    ev_mult = firm.fin.get("ev_revenue_multiple")
    P0 = float(ev_mult) * float(firm.part1["S"]) if ev_mult else reg.M_exit * EB0
    ND0 = (reg.leverage or 0.0) * EB0
    rd = reg.info["r_debt"]
    t = np.arange(T) + 0.5
    fcf = path["fcf_base"][:T] + path["cash_delta"][:T]
    FV = float(np.sum(np.exp(rd * (T - t)) * fcf))
    out = {"applicable": True, "price": P0}
    for hx in (0.5, 1.0):
        ys = int(max(T - 1 - round(reg.info["T_sea"]), 0))
        V_sp = math.exp(-reg.r * T) * (reg.M_exit * (float(path["ebitda_base"][T - 1]) + hx * float(path["ebitda_delta"][ys])) + FV)
        out[f"hx{hx:g}"] = F.lbo_breakeven(V_sp, P0, ND0, reg.r, rd, T, reg.info["c_tx"], 0.0, 0.0, p.regime.control_premium)
    out["frictionless_gain"] = float(pe["sol"].value - sides["public"]["sol"].value)
    return out


def hybrids(firm, p, sides: dict) -> dict:
    """Hybrid variants (prop:reg-hybrid): dual-class myopia (the hybrid preset), a minority investor's weight, and the
    covenant or cash budget an equity cure would add."""
    out = {"dual_class_myopia": p.regime.hybrid_myopia}
    if "public" in sides and "pe" in sides:
        Xp = growth_weight(firm, sides["public"]["regime"], p)["X_o"]
        Xi = growth_weight(firm, sides["pe"]["regime"], p)["X_o"]
        out["minority_weight_examples"] = {f"omega_{w:g}": F.hybrid_weight(Xi, Xp, w) for w in (0.25, 0.5)}
    return out


def stakeholder_values(firm, econ, sol_detail: dict, p, reg: Regime) -> dict:
    """Value by stakeholder group, PV at the regime's rate over the plan horizon (prop:reg-metrics; spec 16.3):
    customers get the price cut on cost-of-revenue savings at the industry pass-through rate (Part I round 2: a rate,
    not 1 - durable share, which is the firm's dollar share with its volume gain), government the tax on the extra profit less an
    approximate payroll-tax loss, displaced employees lose wages net of severance once, vendors lose outsourced
    spend, owners keep the rest (the plan's risk-adjusted value)."""
    T = econ.T
    yrs = np.arange(T) + 0.5
    D = np.exp(-reg.r * yrs)
    tau = econ.info["tau"]
    phi = float(econ.info["pass_through"]["phi"])          # industry rate (and any entrant rate) on the replicated saving
    fte = sol_detail["fte_removed"]
    wage = sol_detail["avg_wage_removed"]
    sev = sol_detail["severance"]
    u_d = p.transition.u_d
    emp = -float(np.sum((fte * (1 - u_d) * wage - sev) * D))
    cust = float(np.sum(phi * sol_detail["cogs_savings"] * D))
    gov = float(np.sum((tau * sol_detail["gaap_delta"] - p.labor.tau_L / (1 + p.labor.tau_L) * 0.5 * fte * (1 - u_d) * wage) * D))
    vend = -float(np.sum(sol_detail["vendor_spend_removed"] * D))
    return {"owners": float(sol_detail["value"]), "employees": emp, "customers": cust, "government": gov, "vendors": vend,
            "customer_pass_through": phi,
            "note": "employees: displaced wages net of severance, before re-employment elsewhere; customers: the price cut on "
                    "cost-of-revenue savings at the industry pass-through rate (overhead is a fixed cost the incumbents' "
                    "prices do not pass through over the plan horizon); government: corporate tax on the extra "
                    "profit less an approximate payroll-tax loss"}


def process_ranks(sides: dict, econ) -> list[dict]:
    """Value of each process (its best column under the central regime's plan) under every regime's valuation, with
    ranks: rankings can flip between regimes (prop:reg-value)."""
    rows = {}
    for nm, sd in sides.items():
        prog, sol = sd["prog"], sd["sol"]
        for pr, c in sol.sel.items():
            pid = econ.firm.processes.process_id.iat[pr]
            rows.setdefault(pid, {"process_id": pid})[f"value_{nm}"] = float(prog.pv0[c] + sol.varpi[c] * prog.pv1[c])
    out = list(rows.values())
    for nm in sides:
        vals = sorted([r.get(f"value_{nm}", -np.inf) for r in out], reverse=True)
        for r in out:
            v = r.get(f"value_{nm}")
            r[f"rank_{nm}"] = (vals.index(v) + 1) if v is not None else None
    return out


# -------------------------------------------------------------------------------------------------
# Permanent capital (ass:acq-pc, prop:acq-pc) and the limits to buying growth (prop:acq-limits)
# -------------------------------------------------------------------------------------------------
def pc_returns(firm, reg: Regime, path: dict, p) -> dict:
    """A permanent-capital owner buying the firm (prop:acq-pc): the price P (the firm's entry_ev, else the market
    price of prop:reg-lbo times one plus the control premium and transaction costs), the unlevered and levered method
    IRRs with and without the plan against the hurdles, the permanent IRR, P^max at the unlevered hurdle with its
    bounds (eq:acq-pmaxbound), the debt policy ND_0 = min{LTV P, ND^rep} and the covenant at entry. Annual flows are
    constant within a plan year and grow at the terminal growth after the plan."""
    i = reg.info
    rg, fn = p.regime, p.finance
    ri = firm.regime or {}
    T_irr, r_tv, r_d = float(i["irr_window"]), float(i["r_tv"]), float(i["r_debt"])
    iU, iL = float(reg.r), float(i["irr_levered"])
    g_tail = min(float(fn.terminal_growth), r_tv - 0.01)
    EB0 = float(path["ebitda_base"][0])
    S0 = float(firm.part1["S"])
    ev_mult = firm.fin.get("ev_revenue_multiple")
    P_mkt = float(ev_mult) * S0 if ev_mult else float(rg.pe_M_exit) * EB0
    prem = float(rg.control_premium)
    P = float(ri["entry_ev"]) if ri.get("entry_ev") else (1 + prem + float(rg.c_tx)) * P_mkt
    out = {"applicable": EB0 > 0 and P > 0, "price": P, "price_basis": "firm entry_ev" if ri.get("entry_ev") else
           "market price times one plus the control premium and transaction costs", "market_price": P_mkt, "control_premium": prem,
           "hurdle_unlevered": iU, "hurdle_levered": iL, "irr_window_years": T_irr, "r_tv": r_tv, "r_debt": r_d,
           "ltv_cap": float(i["ltv"]), "repayment_years": float(i["repay_years"]), "covenant": reg.covenant}
    if not out["applicable"]:
        return out
    pts = [float(k) for k in range(1, int(math.ceil(T_irr)) + 1)]
    for case, arr in (("without_plan", path["fcf_base"]), ("with_plan", np.asarray(path["fcf_base"]) + np.asarray(path["cash_delta"]))):
        f = F.annual_flow(arr, g_tail)
        im = F.pc_method_irr(f, P, r_tv, T_irr, pts)
        ip = F.pc_permanent_irr(f, P, pts, lo=g_tail + 1e-3)
        lev = F.pc_levered_irr(f, P, r_tv, T_irr, r_d, float(i["ltv"]), float(i["repay_years"]), pts)
        bnd = F.pc_price_bounds(f, iU, r_tv, T_irr, pts)
        out[case] = {"method_irr": im, "method_irr_annual": None if im is None else math.expm1(im),
                     "permanent_irr": ip, "levered_irr": lev["irr"],
                     "levered_irr_annual": None if lev["irr"] is None else math.expm1(lev["irr"]),
                     "clears_unlevered": bool(im is not None and im >= iU),
                     "clears_levered": bool(lev["irr"] is not None and lev["irr"] >= iL),
                     "P_max": bnd["P_max"], "P_max_over_price": bnd["P_max"] / P, "P_max_ebitda_multiple": bnd["P_max"] / EB0,
                     "V_tv": bnd["V_tv"], "P_max_share_of_V_tv": bnd["share_of_V_tv"], "bound_share": bnd["bound_share"],
                     "ND_0": lev["ND_0"], "ND_rep": lev["ND_rep"], "debt_binding": "repayment" if lev["ND_rep"] <= float(i["ltv"]) * P else "LTV",
                     "entry_leverage": lev["ND_0"] / EB0, "covenant_breach_at_entry": bool(reg.covenant and lev["ND_0"] / EB0 > reg.covenant)}
    out["program_uplift_needed"] = F.pc_hurdle_conditions(prem, iU, r_tv, T_irr)
    w = out["with_plan"]["V_tv"] / max(out["without_plan"]["V_tv"], 1e-9) - 1
    out["program_uplift"] = w
    return out


def limit(p, key):
    """A limit parameter (ass:acq-limits): its value and whether the limit is on. A class d limit whose params.yaml
    value is null takes its neutral value (the limit is off) unless a scenario or an override sets it; its
    verified_domain is never used as a range."""
    v = p.get(key)
    meta = p.meta(key)
    neutral = meta.get("neutral_value")
    return v, (v is not None and v != neutral)


def organic_growth(ri: dict, pt: dict) -> dict:
    """Organic growth of the existing base for the limits check (prop:acq-limits(a) after Fable F21), continuously
    compounded: the company's own organic growth ln(1 + reported) when given (company-defined and usually unaudited; it
    counts an acquired business's growth over its estimated pre-deal revenue as organic, unlike Part I Definition 3);
    otherwise, with an NRR, the zero-spend growth with no new customers G_i = ln[1 + s (NRR - 1) + (1 - s) gamma_ns],
    s the subscription share (default 1: all revenue on subscription, the upper bound on decay); otherwise Part I's G."""
    out = {"G_i": None, "g_reported": None}
    if ri.get("nrr"):
        s_ = ri.get("subscription_share")
        gns = ri.get("nonsub_zero_spend_growth")
        out["G_i"] = F.acq_zero_spend_growth(float(ri["nrr"]), 1.0 if s_ is None else float(s_), 0.0 if gns is None else float(gns))
        out["subscription_share"] = 1.0 if s_ is None else float(s_)
        out["G_i_basis"] = ("ln[1 + s (NRR - 1) + (1 - s) gamma_ns] with s = " + (f"{float(s_):.2f}" if s_ is not None else
                            "1 (all revenue subscription: upper bound on decay)") + " and no new customers")
    if ri.get("organic_growth_reported") is not None:
        out["g_reported"] = math.log1p(float(ri["organic_growth_reported"]))
    if out["g_reported"] is not None:
        out["g_org"], out["basis"] = out["g_reported"], ("ln(1 + reported organic growth) (tier3_regime organic_growth_reported; "
                                                          "company-defined, unaudited)")
    elif out["G_i"] is not None:
        out["g_org"], out["basis"] = out["G_i"], out["G_i_basis"]
    else:
        out["g_org"], out["basis"] = float(pt["G"]), "Part I's zero-spend growth G, since no NRR or reported organic growth was supplied"
    return out


def _outlays(text) -> list:
    """Parse tier3_regime acquisition_outlays: 'year:amount[@date]; ...' -> [(year, amount, date)]."""
    out = []
    for part in str(text or "").replace(",", ";").split(";"):
        part = part.strip()
        if not part:
            continue
        y, _, rest = part.partition(":")
        amt, _, dt = rest.partition("@")
        out.append((int(float(y)), float(amt), float(dt) if dt.strip() else 0.5))
    return out


def acquired_growth_report(firm, p, reg: Regime, org: dict) -> dict:
    """The growth-quality block for an owner that buys growth (Part I rem:acquired-bounds after IB-4; acquirer fixes
    v2, item 5.4): every score labelled before or after interest; the cash margin before financing
    (OCF + (1 - tau) interest paid)/S, with a warning that a cost-of-capital charge against OCF as reported charges
    financing twice; the charging-convention grid (level annuity or user cost, year-end or time-weighted capital) at
    NRR; the return on acquisition capital before and after depreciation at d = -ln NRR; the organic score before and
    after interest. A Rule-of-40 score is computed here, not reported by the company, unless the firm reports one."""
    ri = firm.regime or {}
    pt, fin = firm.part1, firm.fin
    S = float(pt["S"])
    g_ann = float(pt["g"])
    m_op = float(pt["m_op"])
    tau = float(ri["interest_tax_rate"]) if ri.get("interest_tax_rate") is not None else float(fin.get("tax_rate") or p.finance.tau)
    out = {"applicable": False, "tau": tau, "tau_basis": "tier3_regime interest_tax_rate" if ri.get("interest_tax_rate") is not None
           else "statutory rate (tier0 tax_rate or finance.tau)", "computed_not_reported": True,
           "scores": {"gaap_before_interest": g_ann + m_op}}
    ip = ri.get("interest_paid")
    if ip is not None:
        out["scores"]["gaap_after_interest"] = g_ann + m_op - float(ip) / S
    if ri.get("operating_cash_flow") is None:
        out["note"] = "needs tier3_regime operating_cash_flow (and interest_paid) for the cash basis and the charging grid"
        return out
    mb = F.margin_before_financing(float(ri["operating_cash_flow"]), float(ip or 0.0), tau, S)
    out.update(applicable=True, margins=mb, interest_paid_given=ip is not None)
    out["scores"]["cash_after_interest"] = g_ann + mb["m_after_interest"]
    out["scores"]["cash_before_interest"] = g_ann + mb["m_before_interest"]
    out["warning"] = ("a cost-of-capital charge set against operating cash flow as reported (after interest paid under U.S. GAAP) "
                      f"charges the debt-financed share twice, by (1 - tau) c_fin = {mb['double_charge']:.4f} of revenue")
    if org.get("g_reported") is not None:
        g_o = math.expm1(org["g_reported"])
        out["scores"]["organic_gaap_before_interest"] = g_o + m_op
        if ip is not None:
            out["scores"]["organic_gaap_after_interest"] = g_o + m_op - float(ip) / S
    fl = _outlays(ri.get("acquisition_outlays"))
    nrr = ri.get("nrr")
    if fl and nrr and float(nrr) < 1:
        y0 = int(firm.base_year) - 1                                 # the fiscal year of the Tier 0 statements
        flows = [(a, (y - y0) + dt) for y, a, dt in fl if y <= y0]
        r_w = float(p.finance.r)
        grid = F.acquisition_charges(flows, S, g_ann, mb["m_before_interest"], mb["m_after_interest"], r_w, float(nrr))
        grid["r"] = r_w
        grid["r_basis"] = "finance.r (the industry cost of capital, continuous)"
        grid["outlays"] = [{"year": y, "outlay": a, "date": dt} for y, a, dt in fl]
        out["charging_grid"] = grid
    else:
        out["charging_grid"] = None
        out["grid_note"] = "the charging grid needs tier3_regime acquisition_outlays and an NRR below 1"
    return out


def limits_check(firm, p, reg: Regime, pc: dict | None = None) -> dict:
    """Limits to buying growth (prop:acq-limits) for an owner that grows by acquisition: (a) the treadmill and the
    self-financing growth g^max, (b) deal flow and size, (c) series review and foreign-investment review, (d) consumer
    and subscription law. Firm inputs (tier3_regime: nrr, acquisition_price_to_revenue, target_growth,
    reference_target_revenue, switching_cost_ratio_mean; tier0 net_debt) come first; each limit parameter is off at
    its neutral value unless a scenario or an override sets it."""
    ri = firm.regime or {}
    pt = firm.part1
    S = float(pt["S"])
    # growth to hold, continuously compounded (prop:acq-limits(a) is stated in continuous rates)
    g_ann = float(ri["target_growth"]) if ri.get("target_growth") is not None else float(pt["g"])
    g = math.log1p(g_ann)
    org = organic_growth(ri, pt)
    g_org, g_org_basis = org["g_org"], org["basis"]
    m = float(pt["m_cash"])
    k = float(ri["acquisition_price_to_revenue"]) if ri.get("acquisition_price_to_revenue") else None
    nd_v, nd_on = limit(p, "limits.nd")
    if firm.fin.get("net_debt") is not None:
        nd, nd_basis = float(firm.fin["net_debt"]) / S, "balance sheet (tier0 net_debt)"
    else:
        nd, nd_basis = float(nd_v or 0.0), "scenario" if nd_on else "neutral (off)"
    r_d = float(reg.info.get("r_debt", p.regime.pc_debt_rate))
    out = {"g": g, "g_annual": g_ann, "g_org": g_org, "g_org_basis": g_org_basis, "organic": org, "m": m, "k_acq": k, "nd": nd,
           "nd_basis": nd_basis, "r_debt": r_d}
    tread = F.acq_standstill(g_org, k, g)
    tread["g_max"] = F.acq_gmax(m, k, g_org, nd, r_d) if k else None
    tread["financed"] = None if tread["g_max"] is None else bool(g <= tread["g_max"])
    tread["applicable"] = k is not None
    # both cases when both are known (acquirer fixes v2, item 5.2): no new customers (G_i) and the company's own organic growth
    cases = {}
    for nm_, go_ in (("no_new_customers", org.get("G_i")), ("reported_organic", org.get("g_reported"))):
        if go_ is not None:
            c_ = F.acq_standstill(go_, k, g)
            c_["g_org"] = go_
            c_["g_max"] = F.acq_gmax(m, k, go_, nd, r_d) if k else None
            cases[nm_] = c_
    tread["cases"] = cases
    out["treadmill"] = tread
    out["acquired_growth"] = acquired_growth_report(firm, p, reg, org)
    n_dl, on_n = limit(p, "limits.n_dl")
    eps, on_e = limit(p, "limits.eps_sz")
    h0, _ = limit(p, "limits.h_0")
    S_tg0 = float(ri["reference_target_revenue"]) if ri.get("reference_target_revenue") else None
    sz = F.acq_size_limit(g, g_org, S, n_dl if on_n else None, eps if on_e else 0.0, h0, S_tg0)
    sz.update(on=bool(on_n and on_e and h0 is not None and S_tg0 is not None), n_dl=n_dl, eps_sz=eps, h_0=h0, S_tg0=S_tg0)
    out["deal_size"] = sz
    a_ch, on_a = limit(p, "limits.a_ch")
    ds, _ = limit(p, "limits.delta_s")
    Lch, _ = limit(p, "limits.L_ch")
    pfdi, on_f = limit(p, "limits.p_fdi")
    Tfdi, _ = limit(p, "limits.T_fdi")
    nv = None
    if pc and pc.get("applicable") and pc.get("with_plan"):
        nv = pc["with_plan"]["P_max_over_price"] - 1.0
    rev = {"on": bool(on_a and ds is not None and Lch is not None), "a": a_ch, "delta_s": ds, "L_ch": Lch,
           "net_value_per_price": nv, "unit": "net value V - P and L^ch per dollar of price"}
    if rev["on"] and nv is not None:
        rev["stop_series"] = F.series_review_stop(nv, ds, a_ch, Lch, True)
        rev["stop_alone"] = F.series_review_stop(nv, ds, a_ch, Lch, False)
    fm = F.fdi_multiplier(pfdi or 0.0, Tfdi or 0.0, reg.r)
    rev["fdi"] = {"on": bool(on_f and Tfdi), "p_fdi": pfdi, "T_fdi": Tfdi, "multiplier": fm,
                  "net_value_after": None if nv is None else nv * fm}
    out["review"] = rev
    hcp, on_h = limit(p, "limits.h_cp")
    ucp, on_u = limit(p, "limits.upsilon_cp")
    xb = float(ri["switching_cost_ratio_mean"]) if ri.get("switching_cost_ratio_mean") else None
    cl = {"on": bool(on_h or on_u), "h_cp": hcp, "upsilon_cp": ucp, "x_bar": xb, "applicable": xb is not None}
    if xb is not None:
        cl["optimum_without_law"] = F.repricing_optimum(xb)
        cl["optimum"] = F.repricing_optimum(xb, float(hcp if hcp is not None else 1.0), ucp)
        cl["retained_at_optimum"] = F.retained_revenue(cl["optimum"], xb, float(hcp if hcp is not None else 1.0))
    out["consumer_law"] = cl
    out["limits_on"] = [nm for nm, on in (("deal size", sz["on"]), ("series review", rev["on"]), ("foreign-investment review", rev["fdi"]["on"]),
                                          ("consumer law", cl["on"]), ("net debt", nd_on)) if on]
    return out
