# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""AI product strategy (spec 17; theory_product.tex; notes/theory_product_notes.md Section 3).

For each product line: the price of a labor-substituting agent as a capture share of customer value, capped at
the entrants' price plus rent (prop:prod-price); seat revenue at risk from customers' own automation
(prop:prod-seats); the pricing-migration threshold and value for usage, two-part and seat-fee hybrid tariffs
(prop:prod-migrate); the gross-margin path and its crossover (prop:prod-margin); cannibalization and preemption
(prop:prod-cannibal); model sourcing (prop:prod-model); and the line's breakpoints (prop:prod-breaks). Across
lines: the feature portfolio at the firm's own weight and at the investor screening weight (prop:prod-portfolio),
and the mapping into Part I's parameters with the dilution test and the complementarity of value pricing and
operations COGS automation (prop:prod-aggregate, cor:prod-dilution).

Seat elasticity and every migration cost are class d scenario parameters: every result that depends on them is
reported over their ranges (low, central, high), never as a point alone."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from . import formulas as F
from .config import find_data_dir, read_yaml

T_FTE = 2080.0


def _rng3(p, key):
    """(low, central, high) of a parameter."""
    v = float(p.get(key))
    r = p.range(key) or [v, v]
    lo, hi = (float(r[0]) if r[0] is not None else v), (float(r[1]) if r[1] is not None else v)
    return min(lo, v), v, max(hi, v)


PRICE_VENDORS = ("freshworks", "intercom", "salesforce", "hubspot")   # spec 26: vendor price examples use these four only


def vendor_price_range(data_dir: Path | None, vendors=PRICE_VENDORS) -> dict:
    """Multi-vendor list prices per outcome, read from params.yaml product.outcome_and_usage_list_prices (never
    hard-coded): per-outcome, per-resolution and per-conversation prices of the vendors spec 26 allows (Freshworks,
    Intercom, Salesforce, HubSpot). Sessions are not resolutions and are left out (product notes Section 6), so
    Freshworks enters the seat price (product.seat_price_default) but not the outcome range."""
    out = {"prices": {}, "low": None, "high": None, "source": None}
    dd = data_dir or find_data_dir()
    if dd is None or not (Path(dd) / "params.yaml").is_file():
        return out
    raw = read_yaml(Path(dd) / "params.yaml")
    node = ((raw.get("product") or {}).get("outcome_and_usage_list_prices") or {})
    for k, v in node.items():
        val = v.get("value") if isinstance(v, dict) else v
        if isinstance(val, (int, float)) and any(w in k for w in ("outcome", "resolution", "conversation")) \
                and any(k.startswith(vn) for vn in vendors):
            out["prices"][k] = float(val)
    if out["prices"]:
        out["low"], out["high"] = min(out["prices"].values()), max(out["prices"].values())
        out["source"] = "data/tasks/params.yaml: product.outcome_and_usage_list_prices (list prices, not transaction prices)"
    return out


def _occ_exposure(data_dir: Path | None) -> pd.DataFrame | None:
    dd = data_dir or find_data_dir()
    if dd is None or not (Path(dd) / "occ_exposure.csv").is_file():
        return None
    return pd.read_csv(Path(dd) / "occ_exposure.csv", dtype={"soc": str})


def lines_frame(firm, p) -> tuple[pd.DataFrame, bool]:
    """Product lines from tier3_products, scaled to Tier 0 revenue; without it one aggregate seat-priced line whose
    results are a wide illustrative band (flagged)."""
    S = float(firm.part1["S"])
    gm0 = 1.0 - float(firm.fin.get("cogs") or 0.0) / max(S, 1e-9)
    if firm.products is not None and len(firm.products):
        df = firm.products.copy()
        tot = float(df.revenue.sum())
        df["revenue"] = df.revenue * (S / tot if tot > 0 and abs(tot / S - 1) > 0.1 else 1.0)
        df["gross_margin"] = df.gross_margin.fillna(gm0) if "gross_margin" in df else gm0
        return df.reset_index(drop=True), True
    df = pd.DataFrame([{"product_line": "all products (no product data)", "revenue": S, "pricing_model": "seat", "seats": None,
                        "price_per_seat": None, "gross_margin": gm0, "labor_substituting": None, "proprietary_data": None}])
    return df, False


def _line_xbar(line, firm, p, occx) -> tuple[float, float, float, str]:
    """Customer-side exposure of the seat holders (low, central, high): central = min(Eloundou beta, Tomlinson
    applicability), low = xbar_low_mult x central, high = max of the two (notes 3.2)."""
    po = firm.product_occupations
    if po is not None and occx is not None:
        rows = po[po.product_line == line.product_line]
        if len(rows):
            ex = occx.set_index("soc")
            c, lo, hi, wsum = 0.0, 0.0, 0.0, 0.0
            for r in rows.itertuples():
                if r.soc not in ex.index:
                    continue
                b = float(ex.at[r.soc, "eloundou_gpt4_beta"]) if "eloundou_gpt4_beta" in ex else np.nan
                tm = float(ex.at[r.soc, "tomlinson_ai_applicability"]) if "tomlinson_ai_applicability" in ex else np.nan
                vals = [x for x in (b, tm) if np.isfinite(x)]
                if not vals:
                    continue
                cc = min(vals)
                c += r.seat_share * cc
                lo += r.seat_share * cc * p.product.xbar_low_mult
                hi += r.seat_share * max(vals)
                wsum += r.seat_share
            if wsum > 0:
                return lo / wsum, c / wsum, hi / wsum, "customer occupations (occ_exposure.csv: Eloundou beta, Tomlinson applicability)"
    lo, c, hi = _rng3(p, "product.xbar_default")
    return lo, c, hi, "default exposure (customer-service example), class d"


def _customer_cost(line, firm, p) -> tuple[float, float, str]:
    """In-house cost per outcome and hours per outcome of the line's customers."""
    hrs = float(line.customer_hours_per_outcome) if pd.notna(getattr(line, "customer_hours_per_outcome", np.nan)) else p.product.outcome_hours
    po = firm.product_occupations
    if po is not None and len(po[po.product_line == line.product_line]):
        rows = po[po.product_line == line.product_line]
        wages = firm.fin.get("_occ_wages") or {}
        w = [wages.get(s) for s in rows.soc]
        if all(x is not None for x in w):
            wage_h = float(np.average(w, weights=rows.seat_share)) * (1 + p.labor.tau_L) / p.labor.hours_per_fte
            return wage_h * hrs, hrs, "customer occupations' median wage x (1 + tau_L) x hours per outcome"
    cH = p.product.c_H_outcome * hrs / 0.588
    return cH, hrs, "params.yaml human cost per resolution, scaled by hours per outcome"


def line_pricing(line, firm, p, ups_E=None) -> dict:
    """prop:prod-price for one line: customer value, rent decomposition, competitive price and viability."""
    pr = p.product
    cH, hrs, src = _customer_cost(line, firm, p)
    cO = pr.outsource_ratio * cH
    cU = (1 - pr.aug_gain) * cH
    cbar = min(cH, cO, cU)
    L = pr.L_outcome_mult * cH
    wtR = pr.tR_ratio * cH
    cq = lambda e: float(F.quality_cost(F.review_share(e, L, wtR, 0.0, 0.0), e, L, wtR))
    eta_I, eta_E = pr.eta_I_share * cH, pr.eta_E_share * cH
    V_I = cbar - (cq(pr.e_I) + eta_I)
    V_E = cbar - (cq(pr.e_E) + eta_E)
    p_sw = pr.p_sw_share * cH
    rho = float(F.agent_rent(V_I, V_E, p_sw))
    chat_I = float(line.agent_unit_cost) if pd.notna(getattr(line, "agent_unit_cost", np.nan)) else pr.chat_share * cH
    chat_E = float(line.entrant_unit_cost) if pd.notna(getattr(line, "entrant_unit_cost", np.nan)) else chat_I
    if pd.notna(getattr(line, "competitor_price", np.nan)) and getattr(line, "pricing_model", "") in ("outcome", "usage"):
        chat_E = min(chat_E, float(line.competitor_price) / (1 + (ups_E if ups_E is not None else pr.ups_E)))
    ue = pr.ups_E if ups_E is None else ups_E
    cp = F.competitive_price(V_I, chat_I, chat_E, rho, pr.eps_ad, ue)
    c_E_inf = pr.c_E_inf_share * cH
    long_run = min(cp["p_m"], c_E_inf + rho) if cp["viable"] else math.nan
    T_C = None
    ddag = cp["chat_E_ddag"]
    if cp["viable"] and np.isfinite(ddag) and ddag > c_E_inf and chat_E > ddag:
        T_C = math.log((chat_E - c_E_inf) / (ddag - c_E_inf)) / p.prices.delta_pi
    return {"cH": cH, "hours_per_outcome": hrs, "cost_source": src, "cO": cO, "cU": cU, "cbar": cbar, "V_I": V_I, "V_E": V_E,
            "rent": rho, "rent_parts": {"data": cq(pr.e_E) - cq(pr.e_I), "workflow": eta_E - eta_I, "switching": p_sw},
            "chat_I": chat_I, "chat_E": chat_E, **cp, "kap_of_cH": cp["p"] / cH if cp["viable"] else math.nan,
            "long_run_price": long_run, "partI_rho": rho / (c_E_inf + rho) if rho > 0 else 0.0, "binding_date_years": T_C,
            "pass_through_own": F.pass_through(chat_I, V_I, pr.eps_ad, cp["capped"], "own") if cp["viable"] else None,
            "pass_through_entrant": F.pass_through(chat_I, V_I, pr.eps_ad, cp["capped"], "entrant") if cp["viable"] else None,
            "agent_gross_margin": F.gross_margin(cp["p"], chat_I).item() if cp["viable"] else None, "ups_E": ue}


def line_seats(line, firm, p, occx, T: int) -> dict:
    """prop:prod-seats: seat revenue at risk and the seat-loss path, over eps_seat and two diffusion cases."""
    pr = p.product
    seat_share = float(line.seat_share_of_bill) if pd.notna(getattr(line, "seat_share_of_bill", np.nan)) else \
        (1.0 if line.pricing_model == "seat" else 0.5 if line.pricing_model in ("hybrid", "two_part") else 0.0)
    R0 = float(line.revenue) * seat_share
    xlo, xc, xhi, xsrc = _line_xbar(line, firm, p, occx)
    elo, ec, ehi = _rng3(p, "product.eps_seat")
    diff = {"durables": (pr.bass_frak_p, pr.bass_frak_q), "fast": (pr.fast_frak_p, pr.fast_frak_q)}
    yrs = np.arange(T) + 0.5
    out = {"seat_revenue": R0, "seat_share_of_bill": seat_share, "xbar_h": {"low": xlo, "central": xc, "high": xhi},
           "xbar_source": xsrc, "eps_seat": {"low": elo, "central": ec, "high": ehi}, "cases": {}}
    out["revenue_at_risk_full"] = {"low": float(F.revenue_at_risk(R0, elo, xlo)), "central": float(F.revenue_at_risk(R0, ec, xc)),
                                   "high": float(F.revenue_at_risk(R0, ehi, xhi))}
    lag = pr.seat_lag_years
    for name, (pp, qq) in diff.items():
        case = {}
        for tag, eps, xb in (("low", elo, xlo), ("central", ec, xc), ("high", ehi, xhi)):
            X = eps * xb * F.bass_B(np.maximum(yrs - lag, 0.0), pp, qq)
            nu = F.nu_seat(np.maximum(yrs - lag, 0.0), eps * xb, pp, qq)
            th, numax = F.nu_peak(eps * xb, pp, qq)
            case[tag] = {"X": X, "nu": nu, "nu0": float(eps * xb * pp), "nu_peak": numax, "t_peak": th + lag,
                         "rar_by_year": R0 * X}
        case["tipping_years"] = F.bass_tipping(pp, qq) + lag
        out["cases"][name] = case
    return out


def line_migration(line, firm, p, seats: dict, r: float) -> dict:
    """prop:prod-migrate: threshold nu*_k, first crossing T1_k and value V_k(T1_k) for each target tariff, over the
    class-d ranges of eps_seat and of the migration costs (reported as min, central and max)."""
    pr = p.product
    gam = float(line.gross_margin) if pd.notna(getattr(line, "gross_margin", np.nan)) else pr.gamma_seat
    R0 = seats["seat_revenue"]
    if R0 <= 0:
        return {"applicable": False, "reason": "no seat-priced revenue"}
    g = min(pr.g_v, r - 0.02)                 # volume growth of the line's installed base (class d), not revenue growth
    pp, qq = pr.bass_frak_p, pr.bass_frak_q
    xs = seats["xbar_h"]
    es = seats["eps_seat"]
    res = {}
    for k, tgt in pr.migration_targets.items():
        base = dict(delta=tgt["delta"], omega=tgt["omega"], varpi=tgt["varpi"], e=tgt.get("e", 0.0))
        grid = []
        for eps_tag in ("low", "central", "high"):
            xb = es[eps_tag] * xs[eps_tag]
            for var in ("central", "delta_low", "delta_high", "omega_low", "omega_high", "varpi_low", "varpi_high"):
                prm = dict(base)
                if var != "central":
                    key, side = var.split("_")
                    rr = p.range(f"product.mig_{key}_range")
                    prm[key] = rr[0] if side == "low" else rr[1]
                ns = F.migration_threshold(r, g, prm["delta"], prm["e"], prm["omega"], prm["varpi"])
                Xf = lambda t, xb=xb: xb * F.bass_B(np.maximum(np.asarray(t, float), 0.0), pp, qq)
                T1 = None if ns is None else F.first_crossing(lambda t: F.nu_seat(t, xb, pp, qq), ns, t_max=40.0)
                V = None if T1 is None else F.migration_value(T1, Xf, R0, gam, r, g, prm["delta"], prm["e"], prm["omega"], prm["varpi"])
                grid.append({"eps_seat": eps_tag, "variation": var, "nu_star": ns, "T1": T1, "value": V,
                             "pays": bool(V is not None and V > 0)})
        cen = next(x for x in grid if x["eps_seat"] == "central" and x["variation"] == "central")
        # revenue the migration protects (central case): varpi [R_k(t) - R_S(t)] after T1, and the one-time cost
        # omega gamma R_S(T1) spread over the migration period (renewals)
        T = int(firm.part1.get("T_plan") or p.constraints.horizon_years)
        prot = np.zeros(T)
        cost = np.zeros(T)
        if cen["T1"] is not None and (cen["value"] or 0) > 0:
            xb = es["central"] * xs["central"]
            T1 = float(cen["T1"])
            yrs = np.arange(T) + 0.5
            X = xb * F.bass_B(np.maximum(yrs, 0.0), pp, qq)
            XT = float(xb * F.bass_B(np.array([T1]), pp, qq)[0])
            RS = R0 * np.exp(g * yrs) * (1 - X)
            RS_T = R0 * math.exp(g * T1) * (1 - XT)
            Rk = (1 - base["delta"]) * RS_T * np.exp(g * (yrs - T1)) * (1 - base["e"] + base["e"] * (1 - X) / max(1 - XT, 1e-9))
            prot = np.where(yrs >= T1, base["varpi"] * (Rk - RS), 0.0)
            span = max(float(p.product.migration_years), 0.5)
            cost = np.clip(np.minimum(np.arange(T) + 1, T1 + span) - np.maximum(np.arange(T), T1), 0, None) / span * base["omega"] * gam * RS_T
        vals = [x["value"] if x["value"] is not None else 0.0 for x in grid]
        res[k] = {"central": cen, "value_min": float(min(vals)), "value_max": float(max(vals)),
                  "protected_revenue_path": prot, "one_time_cost_path": cost,
                  "share_of_scenarios_paying": float(np.mean([x["pays"] for x in grid])), "grid": grid,
                  "dip_share_of_revenue": tgt["omega"] * gam * R0 / max(float(firm.part1["S"]), 1e-9)}
    best = max(res, key=lambda k: (res[k]["central"]["value"] or -1e30))
    return {"applicable": True, "targets": res, "best_target": best, "gross_margin": gam, "g_v": g,
            "note": "conditional on scenario values of the concession, one-time cost, success and seat elasticity (class d)"}


def margin_path(p, years: np.ndarray, base_year: int) -> dict:
    """prop:prod-margin with the two ICONIQ fits of notes 3.6 (fit 1: no floor, log-linear; fit 2: floor)."""
    pr = p.product
    f = p.finance.fees_f
    g0 = pr.ai_gm_2025
    t = years - 2025.0
    # fit 2: 1 - gamma = u_h + u_c exp(-0.288 t) with u_h = 0.23 at constant price (phi = 0)
    u_h, u_c = pr.u_h_share, (1 - g0) - pr.u_h_share
    fit2 = 1.0 - (u_h + u_c * np.exp(-0.288 * t))
    T2, ginf2 = (None, 1 - u_h)
    if 1 - u_h > pr.gamma_sub and u_c > 0:
        T2 = math.log(u_c / ((1 - pr.gamma_sub) - u_h)) / 0.288 if (1 - pr.gamma_sub) > u_h else None
    # fit 1: (1 - phi) delta_u = 0.147 a year, no floor
    rate1 = 0.147
    fit1 = 1.0 - (1 - g0) * np.exp(-rate1 * t)
    T1 = math.log((1 - g0) / (1 - pr.gamma_sub)) / rate1
    # theory path with the firm's pass-through and cost decline
    Tx, ginf = F.margin_crossover(g0, 0.0, pr.u_h_share, (1 - g0) - pr.u_h_share, pr.delta_u, pr.phi_margin, pr.gamma_sub)
    th = F.gross_margin_path(t, g0, 0.0, pr.u_h_share, (1 - g0) - pr.u_h_share, pr.delta_u, pr.phi_margin)
    return {"years": years, "fit1": fit1, "fit2": fit2, "theory": th, "crossover_fit1": 2025.0 + T1,
            "crossover_fit2": None if T2 is None else 2025.0 + T2, "crossover_theory": None if Tx is None else 2025.0 + Tx,
            "gamma_inf_theory": ginf, "gamma_sub": pr.gamma_sub,
            "note": "three points (two projected) do not identify the pass-through; both fits are reported (notes 3.6)"}


def features_portfolio(firm, p, lines: pd.DataFrame, X_own: float, k: float, r: float, g: float) -> dict:
    """prop:prod-portfolio: NPV of each AI feature at the firm's own weight X = v0 and at the screening weight,
    the knapsack over engineering capacity and the value of a retention point."""
    pr = p.product
    S = float(firm.part1["S"])
    Dstar = float(firm.part1.get("Delta_star") or 0.05)
    rg = max(r - p.product.g_v, 0.03)        # r - g of the installed base (notes 3.4)
    feats = []
    if firm.ai_features is not None and len(firm.ai_features):
        for f in firm.ai_features.itertuples():
            ln = lines[lines.product_line == f.product_line]
            share = float(ln.revenue.sum()) / S if len(ln) else 1.0 / max(len(lines), 1)
            feats.append({"feature": f.feature, "line": f.product_line, "kind": f.kind,
                          "F": float(f.dev_cost) if pd.notna(f.dev_cost) else pr.feature_dev_share * S * share,
                          "ups": (float(f.price_uplift_share) if pd.notna(f.price_uplift_share) else pr.uplift_share) * share,
                          "c0": pr.feature_cost_share * share, "dG": (float(f.retention_gain) if pd.notna(f.retention_gain) else pr.retention_dG) * share,
                          "dlam": 0.0, "p": float(f.bass_p) if pd.notna(f.bass_p) else pr.feature_frak_p,
                          "q": float(f.bass_q) if pd.notna(f.bass_q) else pr.feature_frak_q, "source": "tier3_ai_features"})
    else:
        for ln in lines.itertuples():
            share = float(ln.revenue) / S
            feats.append({"feature": f"copilot for {ln.product_line}", "line": ln.product_line, "kind": "copilot",
                          "F": pr.feature_dev_share * S * share * 0.5, "ups": pr.uplift_share * 0.3 * share,
                          "c0": pr.feature_cost_share * 0.4 * share, "dG": pr.retention_dG * 2 * share, "dlam": 0.0,
                          "p": pr.feature_frak_p, "q": pr.feature_frak_q, "source": "defaults (class d)"})
            if (ln.labor_substituting or 0) >= 0.5:
                feats.append({"feature": f"agent for {ln.product_line}", "line": ln.product_line, "kind": "agent",
                              "F": pr.feature_dev_share * S * share, "ups": pr.uplift_share * share,
                              "c0": pr.feature_cost_share * share, "dG": pr.retention_dG * share, "dlam": 0.0,
                              "p": pr.feature_frak_p, "q": pr.feature_frak_q, "source": "defaults (class d)"})
    rows = []
    for f in feats:
        nE = f["F"] / 1e6 * pr.engineer_years_per_musd
        v_own = F.feature_npv(S, X_own, k, Dstar, rg, f["ups"], f["c0"], pr.delta_u, f["dG"], f["dlam"], f["F"], f["p"], f["q"])
        v_scr = F.feature_npv(S, pr.screening_weight, k, Dstar, rg, f["ups"], f["c0"], pr.delta_u, f["dG"], f["dlam"], f["F"], f["p"], f["q"])
        ret_val = (X_own - k) * (f["dG"] + Dstar * f["dlam"])
        rows.append({**f, "engineer_years": nE, "npv_own_weight": v_own, "npv_screening_weight": v_scr,
                     "retention_point_value": ret_val,
                     "retention_outweighs_margin": bool(F.retention_breakeven(X_own, k, f["dG"], Dstar, f["dlam"], f["c0"], f["ups"]))})
    df = pd.DataFrame(rows)
    rnd_fte = float(firm.functions.loc[firm.functions.cost_bucket == "rnd", "fte"].sum()) if "fte" in firm.functions else 0.0
    cap = max(rnd_fte * pr.engineer_capacity_share, 5.0)
    plat = pr.platform_cost_share * S
    if len(df):
        chosen, val, shadow = F.knapsack(df.npv_own_weight.values, df.engineer_years.values, cap, plat)
        chosen_scr, val_scr, _ = F.knapsack(df.npv_screening_weight.values, df.engineer_years.values, cap, plat)
        df["chosen"] = [i in chosen for i in range(len(df))]
        df["chosen_at_screening_weight"] = [i in chosen_scr for i in range(len(df))]
    else:
        val = val_scr = shadow = 0.0
    # the portfolio at the growth-weight evaluation points (D-1): the decision weight is not identified, so the chosen
    # set is reported at each point and a change between points is flagged (theory_product.tex: agent and copilot ranks
    # flip with X)
    from .levers import eval_points
    pts, pts_basis = eval_points(firm, p)
    at_pts = []
    for Xp in pts:
        if not len(df):
            break
        v_p = [F.feature_npv(S, Xp, k, Dstar, rg, f["ups"], f["c0"], pr.delta_u, f["dG"], f["dlam"], f["F"], f["p"], f["q"]) for f in feats]
        ch_p, val_p, _ = F.knapsack(np.asarray(v_p, float), df.engineer_years.values, cap, plat)
        at_pts.append({"X": Xp, "chosen": sorted(str(df.feature.iat[i]) for i in ch_p), "value": float(val_p),
                       "rank": [str(df.feature.iat[i]) for i in np.argsort(-np.asarray(v_p, float))]})
    sets = [tuple(a["chosen"]) for a in at_pts]
    ranks = [tuple(a["rank"]) for a in at_pts]
    return {"features": df, "value": val, "value_screening": val_scr if len(df) else 0.0, "engineer_capacity": cap,
            "platform_cost": plat, "shadow_value_per_engineer_year": shadow, "X_own": X_own,
            "X_screening": pr.screening_weight, "at_eval_points": at_pts, "eval_points_basis": pts_basis,
            "chosen_set_flips": F.sign_flips(pts[:len(sets)], sets), "rank_flips": F.sign_flips(pts[:len(ranks)], ranks)}


def sourcing(p, chat_api: float, rho_u: float, Q: float, r: float) -> dict:
    """prop:prod-model: API, open weights or own model at volume Q, with thresholds and the long-run test."""
    opts = p.product.sourcing
    dK = 1.0 / 3.0
    out, costs = {}, {}
    for m, o in opts.items():
        cv, ci, K = o["cv"] * chat_api, o["ci"] * chat_api, o["K"] * chat_api
        rho = rho_u + o["rho_add"] * chat_api
        net0 = F.sourcing_net_unit(cv, ci, o["dec"], K, rho, r, dK, 0.0)
        net_inf = F.sourcing_net_unit(cv, ci, o["dec"], K, rho, r, dK, 50.0)
        out[m] = {"net_unit_now": net0, "net_unit_long_run": net_inf, "fixed_per_year": o["Ft"]}
        costs[m] = Q * net0 + o["Ft"]
    choice = min(costs, key=costs.get)
    th = {f"{a}->{b}": F.sourcing_threshold(out[a]["net_unit_now"], out[b]["net_unit_now"], out[a]["fixed_per_year"], out[b]["fixed_per_year"])
          for a, b in (("api", "open"), ("open", "own"), ("api", "own")) if a in out and b in out}
    own = opts.get("own")
    test = None
    if own is not None and "api" in opts:
        test = bool(F.own_model_test(rho_u + own["rho_add"] * chat_api, rho_u, own["cv"] * chat_api, own["K"] * chat_api,
                                     (opts["api"]["cv"] - opts["api"]["ci"]) * chat_api, r, dK))
    return {"options": out, "choice": choice, "volume": Q, "thresholds": th, "own_model_pays_long_run": test}


def analyze(firm, p, econ, regime, data_dir: Path | None = None, ops_cogs_saving_share: float = 0.0) -> dict:
    """The product strategy for every line, the feature portfolio, sourcing, the aggregate into Part I and the
    combined revenue and gross-profit paths (central and band) for the score path."""
    T = econ.T
    years = econ.years
    r = float(regime.r)
    g = float(firm.part1["g"])
    X_own = float(firm.part1.get("X") or p.finance.X_default)
    k = float(firm.part1.get("k") or 0.0)
    lines, has_data = lines_frame(firm, p)
    occx = _occ_exposure(data_dir)
    vend = vendor_price_range(data_dir)
    out_lines = []
    rev_delta = {"low": np.zeros(T), "central": np.zeros(T), "high": np.zeros(T)}
    gp_delta = {"low": np.zeros(T), "central": np.zeros(T), "high": np.zeros(T)}
    rar_path = {"low": np.zeros(T), "central": np.zeros(T), "high": np.zeros(T)}
    for ln in lines.itertuples():
        entry = {"product_line": ln.product_line, "revenue": float(ln.revenue), "pricing_model": ln.pricing_model,
                 "has_product_data": has_data}
        seats = line_seats(ln, firm, p, occx, T)
        entry["seats"] = seats
        for tag in rar_path:
            rar_path[tag] += seats["cases"]["durables"][tag]["rar_by_year"]
        entry["migration"] = line_migration(ln, firm, p, seats, r) if has_data else {"applicable": False, "reason": "no product data"}
        ls = getattr(ln, "labor_substituting", None)
        if has_data and ls is not None and pd.notna(ls) and float(ls) >= 0.5:
            pr_c = line_pricing(ln, firm, p)
            pr_conc = line_pricing(ln, firm, p, ups_E=p.range("product.ups_E")[1])
            entry["pricing"] = pr_c
            entry["pricing_concentrated"] = {"p": pr_conc["p"], "kap": pr_conc["kap"], "ups_E": pr_conc["ups_E"], "capped": pr_conc["capped"]}
            if vend["low"] is not None and pr_c["viable"]:
                entry["list_price_check"] = {"vendor_low": vend["low"], "vendor_high": vend["high"],
                                             "inside": bool(vend["low"] <= pr_c["p"] <= vend["high"] * 1.5)}
            # in-scope outcomes a year: seat hours x exposure / hours per outcome
            seats_n = float(ln.seats) if pd.notna(getattr(ln, "seats", np.nan)) and ln.seats else \
                seats["seat_revenue"] / max(float(ln.price_per_seat) if pd.notna(getattr(ln, "price_per_seat", np.nan)) and ln.price_per_seat else p.product.seat_price_default, 1.0)
            Q_scope = seats_n * T_FTE * seats["xbar_h"]["central"] / max(pr_c["hours_per_outcome"], 1e-6)
            entry["outcomes_in_scope"] = Q_scope
            if pr_c["viable"]:
                Bf = F.bass_B(np.arange(T) + 0.5, p.product.feature_frak_p, p.product.feature_frak_q)
                agent_rev = pr_c["p"] * pr_c["D"] * Q_scope * Bf
                agent_gp = (pr_c["p"] - pr_c["chat_I"]) * pr_c["D"] * Q_scope * Bf
                for tag in rev_delta:
                    rev_delta[tag] += agent_rev
                    gp_delta[tag] += agent_gp
                entry["agent_revenue_path"] = agent_rev
                entry["sourcing"] = sourcing(p, pr_c["chat_I"], pr_c["rent"], Q_scope * pr_c["D"], r)
                p_seat = float(ln.price_per_seat) if pd.notna(getattr(ln, "price_per_seat", np.nan)) and ln.price_per_seat else p.product.seat_price_default
                entry["cannibalization"] = F.cannibalization(pr_c["V_I"], pr_c["chat_I"], p.product.eps_ad, p_seat,
                                                             pr_c["hours_per_outcome"], T_FTE,
                                                             float(ln.gross_margin) if pd.notna(ln.gross_margin) else p.product.gamma_seat,
                                                             pr_c["rent_parts"]["switching"],
                                                             float(ln.entry_hazard) if pd.notna(getattr(ln, "entry_hazard", np.nan)) else p.product.entry_hazard,
                                                             r, min(p.product.g_v, r - 0.02), cap=pr_c["cap"])
                W_ratio = pr_c["V_I"] * T_FTE / (pr_c["hours_per_outcome"] * p_seat)
                entry["market_conversion"] = {"kap_W": pr_c["kap"] * W_ratio, "threshold_kap": 1.0 / W_ratio,
                                              "expands_market": bool(pr_c["kap"] > 1.0 / W_ratio)}
        # migration revenue effect (central best target; band from the grid)
        mig = entry["migration"]
        if mig.get("applicable"):
            best = mig["targets"][mig["best_target"]]
            if best["central"]["T1"] is not None and (best["central"]["value"] or 0) > 0:
                prot, cost = best["protected_revenue_path"][:T], best["one_time_cost_path"][:T]
                for tag in rev_delta:
                    rev_delta[tag] += prot
                    gp_delta[tag] += mig["gross_margin"] * prot - cost
        # breakpoints (prop:prod-breaks)
        bp = {}
        if "pricing" in entry:
            pc = entry["pricing"]
            bp["competition_binds"] = {"chat_E": pc["chat_E"], "threshold": pc["chat_E_ddag"], "binding": pc["capped"],
                                       "distance": (pc["chat_E"] * (1 + pc["ups_E"]) / pc["chat_E_ddag"] - 1) if pc["viable"] and pc["chat_E_ddag"] else None,
                                       "binding_date_years": pc["binding_date_years"]}
            bp["viability_margin"] = (pc["cap"] - pc["chat_I"])
        dur = seats["cases"]["durables"]
        bp["bass_tipping_years"] = dur["tipping_years"]
        bp["seat_loss_peak_years"] = {t: dur[t]["t_peak"] for t in ("low", "central", "high")}
        if mig.get("applicable"):
            bp["migration_threshold"] = {k: v["central"]["nu_star"] for k, v in mig["targets"].items()}
            bp["migration_date_years"] = {k: v["central"]["T1"] for k, v in mig["targets"].items()}
        if "cannibalization" in entry:
            cn = entry["cannibalization"]
            bp["cannibalization"] = {"launch_now": cn["launch_now"], "nu_E_star": cn["nu_E_star"]}
        if "market_conversion" in entry:
            bp["market_conversion"] = entry["market_conversion"]
        entry["breakpoints"] = bp
        out_lines.append(entry)
    margins = margin_path(p, years, firm.base_year)
    feats = features_portfolio(firm, p, lines, X_own, k, r, g)
    S = float(firm.part1["S"])
    # aggregate into Part I (first order, prop:prod-aggregate); transient diffusion growth is reported, not capitalized
    yi = min(2, T - 1)
    gp3 = gp_delta["central"][yi] / S
    rar3 = {t: float(rar_path[t][yi] / S) for t in rar_path}
    agg = {}
    for Xw, name in ((1.0, "rule_of_40"), (X_own, "own_weight"), (p.product.screening_weight, "screening_weight")):
        agg[name] = {t: float(F.product_delta_R(gp3, 0.0, 0.0, -rar3[t] / max(yi + 0.5, 1.0), 0.0, Xw, k, g, 0.0, 0.0))
                     for t in ("low", "central", "high")}
    comp = F.complementarity_value_pricing(ops_cogs_saving_share, 0.0, 1.0)
    dil = None
    agents = [x for x in out_lines if "pricing" in x and x["pricing"]["viable"]]
    if agents:
        a0 = agents[0]["pricing"]
        D_m = max(float(firm.part1.get("gamma") or 0.75) - (a0["agent_gross_margin"] or 0.0), 0.0) * 0.1
        dil = F.dilution_test(D_m, 0.01, X_own, k)
    return {"lines": out_lines, "has_product_data": has_data, "vendor_list_prices": vend, "margins": margins,
            "features": feats, "aggregate_year3": agg, "complementarity_ops_cogs": comp, "dilution": dil,
            "revenue_delta": rev_delta, "gross_profit_delta": gp_delta, "revenue_at_risk_path": rar_path,
            "class_d": ["product.eps_seat", "product.migration_targets", "product.mig_delta_range", "product.mig_omega_range",
                        "product.mig_varpi_range", "product.ups_E", "product.xbar_default"],
            "note": "seat elasticity and migration costs are scenario parameters; results are shown as low, central and high"}
