# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""The lever map (spec 28; notes/playbook_engine_spec.md Section 2; part2/theory_playbook.tex sec:playbook): for each
ownership regime, the value of every lever at a common proportion, the switch thresholds with the firm's distance
to each, the binding constraint (position and setup) and the levers that do not pay, with the rule that excludes
them. The position is calibrated so that the observed growth spend is optimal (lem:playbook-calib) unless the firm
gives an EV/revenue multiple or market growth."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

from . import formulas as F
from .economics import A, H, O

GAP_BANDS = Path(__file__).resolve().parent / "priors" / "frontier_gap_bands.csv"


def state(firm, p, rd_expansion_share: float | None = None, basis: str | None = None) -> dict:
    """The position vector (spec 2.1) with the calibration of 2.2. rd_expansion_share None uses the engine's
    setting; 0 gives Paper 1's S&M-only growth spend. basis None uses finance.sm_basis (netted, central since the
    author's decision of 2 Nov 2026): growth spend is S&M above the maintenance base, which is a cost line a_SM."""
    fin, pt = firm.fin, firm.part1
    S = float(pt["S"])
    th = float(p.finance.rd_expansion_share if rd_expansion_share is None else rd_expansion_share)
    bs = str(p.finance.sm_basis if basis is None else basis)
    gs = F.growth_spend_split(float(fin["sm"]) / S, float(fin["rnd"]) / S, th, bs, float(p.finance.sm_maint_base))
    sigma = gs["sigma"]
    a_GA = float(fin["ga"]) / S
    a_RD = (1 - th) * float(fin["rnd"]) / S
    a_SM = gs["sm_maint"]
    k, alpha, g = float(pt["k"]), float(pt["alpha"]), float(pt["g"])
    X_in = fin.get("ev_revenue_multiple")
    G_in = fin.get("market_growth")
    r_sig = float(p.finance.spend_ratio_netted if bs == "netted" else p.finance.spend_ratio)
    cal = F.playbook_calibration(g, sigma, k, alpha, r_sig, X_in, G_in)
    if sigma <= 1e-6:      # no growth spend on this basis: no demand pull to calibrate (growth-engine levers are zero)
        cal = dict(cal, ell=0.0, Delta=0.0, G_i=g, source=cal["source"] + "; no growth spend above the maintenance base")
    # FCF-basis a, as Part I; part1's a_gaap carries the maintenance S&M of the engine's own basis, so the other
    # operating items (a - a_gaap) are basis-free
    m0 = float(pt["gamma"]) - (a_GA + a_RD + a_SM) - (float(pt["a"]) - float(pt["a_gaap"]))
    return {"S": S, "g": g, "m_cash": float(pt["m_cash"]), "sigma": sigma, "sm_share": float(fin["sm"]) / S, "a_GA": a_GA,
            "a_RD": a_RD, "a_SM": a_SM, "a": a_GA + a_RD + a_SM, "sm_basis": bs,
            "gamma": float(pt["gamma"]), "c_h": float(pt["c_h"]), "c_c": float(pt["c_c"]), "k": k, "alpha": alpha, "m0": m0,
            "rd_expansion_share": th, **cal}


def sm_basis_bounds(firm, p, st: dict) -> dict:
    """Paper 1 round 2, author decisions 4 and 7 (2 Nov 2026): maintenance-netted growth spend is the central basis
    everywhere (sigma = max(S&M share - finance.sm_maint_base, 0)), the lever map's calibration included; all S&M and no
    S&M are bounds. At the weight the firm's own spending reveals, the growth engine outranks overhead iff sigma > a_GA
    (prop:playbook-rank(b), (a_GA/sigma)^(1-alpha) < 1), whatever the spend ratio; the maintenance share of S&M is then a
    cost line like overhead."""
    S = float(st["S"])
    sm = float(firm.fin["sm"]) / S
    th_rd = float(st["rd_expansion_share"]) * float(firm.fin["rnd"]) / S
    b = float(p.finance.sm_maint_base)
    out = {"sm_share": sm, "maint_base": b, "maintenance_sm": min(sm, b)}
    for basis, sig in (("all", sm + th_rd), ("netted", max(sm - b, 0.0) + th_rd), ("none", th_rd)):
        out[basis] = {"sigma": sig, "growth_engine_ahead_of_overhead_at_revealed_weight": bool(sig > st["a_GA"]),
                      "ratio": (st["a_GA"] / sig) ** (1 - st["alpha"]) if sig > 0 else float("inf")}
    out["central"] = str(p.finance.sm_basis)
    out["note"] = ("central basis: finance.sm_basis (maintenance-netted by default, Paper 1's central basis); all S&M and no "
                   "S&M are the bounds")
    return out


def _gap_binding(st: dict) -> dict:
    """Position binding constraint (spec 2.5(1)): the cost line with the largest gap to the top decile of GAAP
    operating margin in the firm's growth band (Paper 1 Table tab:gap)."""
    if not GAP_BANDS.is_file():
        return {"line": None, "note": "priors/frontier_gap_bands.csv missing"}
    b = pd.read_csv(GAP_BANDS)
    g = min(max(st["g"], 0.0), 0.5999)
    row = b[(b.g_low <= g) & (g < b.g_high)]
    if not len(row):
        return {"line": None, "note": "growth outside the table's bands"}
    r = row.iloc[0]
    sm = st["sm_share"]                                                  # the S&M share itself, on any basis
    gaps = {"gross margin": float(r.top_gm) - st["gamma"], "S&M": sm - float(r.top_sms),
            "R&D": st["a_RD"] - float(r.top_rds), "G&A": st["a_GA"] - float(r.top_gas)}
    line = max(gaps, key=gaps.get)
    return {"line": line, "gaps_to_top_decile": gaps, "band": f"{r.g_low:.0%} to {r.g_high:.0%}",
            "source": "Paper 1 Table tab:gap (priors/frontier_gap_bands.csv)"}


def _setup_binding(util: pd.DataFrame, book: dict | None) -> dict:
    """Setup binding constraint (spec 2.5(2)): the scarcest capacity in the first plan year and the gate that most
    often binds automation across in-house hours."""
    out = {"capacity": None, "gate": None}
    if util is not None and len(util):
        u0 = util.iloc[0]
        r = {"change capacity": u0.change_capacity_used / max(u0.change_capacity, 1e-9),
             "decision bandwidth": u0.decision_load / max(u0.load_breakpoint * u0.decision_bandwidth, 1e-9),
             "security reviews": u0.security_reviews / max(u0.review_capacity, 1e-9),
             "budget": u0.budget_used / max(u0.budget, 1e-9), "dual running": u0.dual_running_used / max(u0.dual_running_budget, 1e-9)}
        k = max(r, key=r.get)
        out["capacity"], out["capacity_use"], out["capacity_uses"] = k, float(r[k]), {a: float(b) for a, b in r.items()}
    acts = (book or {}).get("activities")
    if acts is not None and len(acts):
        w = acts[acts.mode_plan != "A"].groupby("binding_target").fte_in_house.sum()
        if len(w):
            out["gate"] = str(w.idxmax())
            out["gate_fte_shares"] = (w / w.sum()).round(4).to_dict()
    return out


def _capital_activities(econ, hurdle: float) -> int:
    """Activities whose opex saved per dollar of capital, dc/dK, exceeds the hurdle (cor:capital; prop:tasks-capital)."""
    l, y = econ.L - 1, min(2, econ.T - 1)
    K = econ.K[:, l, y, A]
    alt = np.minimum(econ.cash[:, l, y, H], econ.cash[:, l, y, O])
    dc = alt - econ.cash[:, l, y, A]
    ok = np.isfinite(K) & (K > 0) & np.isfinite(dc)
    return int(np.sum(ok & (dc / np.where(ok, K, 1.0) > hurdle)))


def eval_points(firm, p) -> tuple[list[float], str]:
    """Growth weights at which X-dependent recommendations are reported (D-1): the firm's range (low, midpoint, high)
    when it gives one, else finance.X_eval_points (2.5, 5, 9)."""
    fin = firm.fin or {}
    lo, hi = fin.get("growth_weight_low"), fin.get("growth_weight_high")
    if lo is not None and hi is not None and float(hi) >= float(lo):
        lo, hi = float(lo), float(hi)
        return [lo, (lo + hi) / 2, hi], "firm range (tier0 growth_weight_low, growth_weight_high)"
    return [float(v) for v in p.finance.X_eval_points], "finance.X_eval_points (Papers 1 and 2 evaluation points; not estimates)"


def x_levels(firm, p, st: dict, x: float, keep_rep: float, keep_own: float, dK: float, product: dict | None, nrr: float | None) -> dict:
    """Recommendations that depend on the level of the growth weight X, at the evaluation points (D-1: the data do not
    identify X; Papers 1 and 2 report such conclusions at X in {2.5, 5, 9} and say where they flip): the lever ranking
    at the common proportion (prop:playbook-rank(a), (b)), whether the growth engine outranks overhead (X > X^ddagger_0),
    the largest price per dollar of acquired revenue that raises the charged score in full, as an annuity and as a user
    cost (prop:acquired-score(a); rem:acquired-bounds), whether the firm's own acquisition price passes, and the AI
    product dilution rule (cor:prod-dilution). Sign flips between points are flagged. Ratio tests against the revealed
    spend weight, (X_o - k)/(X_hat - k), do not depend on the level and are left as they are."""
    pts, basis = eval_points(firm, p)
    k, alpha, ell = st["k"], st["alpha"], st["ell"]
    r = float(p.finance.r)
    ri = firm.regime or {}
    k_acq = float(ri["acquisition_price_to_revenue"]) if ri.get("acquisition_price_to_revenue") else None
    x0 = F.x_dagger_0(k, st["a_GA"], alpha, ell)
    dil = (product or {}).get("dilution") if product else None
    rows = []
    for X in pts:
        row = {"X": X}
        if X > k:
            lv = F.lever_values(st["m0"], st["G_i"], ell, X, k, alpha, x, st["a_GA"], st["a_RD"], st["c_h"], keep_rep, keep_own, r, dK)
            rk = sorted(((kk, vv) for kk, vv in lv.items() if kk in ("growth_automation", "overhead", "engineering", "cost_of_revenue_replicable")),
                        key=lambda kv: -kv[1])
            row["ranking"] = [kk for kk, _ in rk]
            row["top_lever"] = rk[0][0]
        else:
            row["ranking"], row["top_lever"] = None, "none (X <= k: no growth lever pays)"
        row["growth_engine_beats_overhead"] = bool(X > x0)
        row["acquisition_price_bounds"] = F.acquisition_price_bounds(X, r, nrr)
        if k_acq is not None:
            row["acquisition_raises_score_full_charge"] = bool(X > k_acq)
            ab = row["acquisition_price_bounds"]
            if ab["annuity"] is not None:
                row["acquisition_raises_score_annuity"] = bool(k_acq < ab["annuity"])
                row["acquisition_raises_score_user_cost"] = bool(k_acq < ab["user_cost"])
        if dil and np.isfinite(dil.get("break_even_weight", math.inf)):
            row["ai_product_dilution_pays"] = bool(X > float(dil["break_even_weight"]))
        rows.append(row)
    flips = []
    for key, thr, what in (("top_lever", None, "top lever at the common proportion"),
                           ("growth_engine_beats_overhead", x0, "growth engine above overhead (X^ddagger_0, prop:playbook-rank(b))"),
                           ("acquisition_raises_score_full_charge", k_acq, "acquired growth raises the fully charged score (X = k^acq)"),
                           ("acquisition_raises_score_annuity", None, "acquired growth raises the annuity-charged score"),
                           ("acquisition_raises_score_user_cost", None, "acquired growth raises the user-cost-charged score"),
                           ("ai_product_dilution_pays", (dil or {}).get("break_even_weight"), "AI product dilution pays (cor:prod-dilution)")):
        vals = [rw.get(key) for rw in rows]
        if any(v is None for v in vals):
            continue
        fl = F.sign_flips(pts, vals)
        if fl:
            flips.append({"rule": what, "key": key, "threshold_X": thr, "flips": fl})
    thr = {"growth engine above overhead (X^ddagger_0)": x0, "acquired growth raises the fully charged score (k^acq)": k_acq,
           "AI product dilution pays (break-even weight)": (dil or {}).get("break_even_weight")}
    outside = [{"rule": kk, "threshold_X": float(v), "side": "below the lowest point" if v < min(pts) else "above the highest point"}
               for kk, v in thr.items() if v is not None and np.isfinite(v) and (v < min(pts) or v > max(pts))]
    return {"points": pts, "basis": basis, "rows": rows, "flips": flips, "X_dagger_0_overhead": x0, "k_acq": k_acq,
            "thresholds": {kk: (None if v is None else float(v)) for kk, v in thr.items()},
            "thresholds_outside_points": outside,
            "note": "the level of X is not identified by the data (Paper 1 decision D-1); a recommendation is robust only if it "
                    "holds at every point"}


def lever_map(firm, p, econ, reg_view: dict, util: pd.DataFrame | None = None, book: dict | None = None,
              product: dict | None = None) -> dict:
    """The lever map of one firm: the calibrated position, then per regime the lever values (prop:playbook-rank(a)),
    the switch thresholds with distances (prop:playbook-rank(b)-(f)), and the excluded levers (cor:playbook-nopay)."""
    st = state(firm, p)
    st_sm = state(firm, p, 0.0)
    x = float(p.levers.proportion)
    alpha, k, ell = st["alpha"], st["k"], st["ell"]
    dur = float(econ.info["durable_share"])            # dollar share of a replicated saving (cor:ext-game-engine(a))
    # score values use the round-2 pass-through of Part I (B1): rate phi on the unit-cost saving, margin at the post-cut
    # price, so a replicated cost-of-revenue cut keeps 1 - phi C0 of its margin gain (prop:levers-position(a), (d))
    ptr = econ.info["pass_through"]
    keep_rep, keep_own = float(ptr["keep_replicable"]), float(ptr["keep_own"])
    dK = float(p.capital.delta_K_compute)
    from .regimes import _frakA
    X_scr = _frakA(math.expm1(float(p.finance.r)), min(st["g"], 0.3), 10, 0.5 * st["G_i"], 0.5)
    ri = firm.regime or {}
    nrr = float(ri["nrr"]) if ri.get("nrr") else None
    regimes_out = {}
    for nm, rv in reg_view.items():
        X_o = float(rv["growth_weight"].get("X_o") or 0.0)
        r_o = float(rv["r"])
        if not np.isfinite(X_o) or X_o <= k:
            regimes_out[nm] = {"X_o": X_o, "applicable": False, "note": "growth weight not above k: no growth lever pays"}
            continue
        lv = F.lever_values(st["m0"], st["G_i"], ell, X_o, k, alpha, x, st["a_GA"], st["a_RD"], st["c_h"], keep_rep, keep_own, r_o, dK)
        th = {}
        for line, a in (("overhead", st["a_GA"]), ("engineering", st["a_RD"])):
            x0 = F.x_dagger_0(k, a, alpha, ell)
            xe = F.x_dagger_exact(k, ell, alpha, x, x * a)
            xd = F.x_dagger_demand_pull(k, a, alpha, ell)
            hr = F.headroom_switch(a, lv["sigma_star"], alpha)
            th[line] = {"X_dagger_0": x0, "distance_X_dagger_0": X_o - x0, "X_dagger_exact": xe, "distance_X_dagger_exact": X_o - xe,
                        "X_dagger_demand_pull": xd, "distance_X_dagger_demand_pull": X_o - xd,
                        "identified_lhs": (X_o - k) / max(st["X_hat"] - k, 1e-12), "identified_rhs": (a / st["sigma"]) ** (1 - alpha) if st["sigma"] > 0 else math.inf,
                        "headroom_switch": hr, "headroom_fall_to_flip": 1 - hr,
                        "screening_flip": bool(X_scr < x0 < X_o)}
        cor_vs_ga = keep_rep - st["a_GA"] / max(st["c_h"], 1e-12)     # > 0 iff (1 - phi_e) c_h > a_GA (prop:levers-position(d))
        # capital hurdles are pre-tax; with servers' psi < 1 (election out, ADS abroad) they rise by Upsilon_K
        # (prop:acct-tax(d), cor:capital); Upsilon_K = 1 for domestic servers under current law
        ups_k = float(econ.info.get("Ups_K", 1.0))
        lv["capital_hurdle_tax_wedge"] = ups_k
        lv["capital_hurdle_score"] *= ups_k
        lv["capital_hurdle_value"] *= ups_k
        ncap = _capital_activities(econ, lv["capital_hurdle_score"])
        if "pe" == nm and rv.get("capital_hurdle"):
            zeta = [h.get("zeta_pe_hx1") for h in rv["capital_hurdle"] if h.get("zeta_pe_hx1") is not None]
            lv["capital_hurdle_sponsor"] = float(np.median(zeta)) if zeta else None
        durable = {"overhead": True, "engineering": True, "retention_point": True, "cost_of_revenue_given_demand": True,
                   "growth_automation": False, "demand_pull": False}
        excl = []
        x0_ga = th["overhead"]["X_dagger_0"]
        if X_o <= x0_ga:
            excl.append({"lever": "growth engine (automation and demand pull)", "rule": f"X_o {X_o:.2f} <= X^ddagger_0 {x0_ga:.2f} (prop:playbook-rank(b))"})
        if keep_rep * st["c_h"] < st["a_GA"]:
            excl.append({"lever": "cost-of-revenue automation as a margin lever ahead of overhead",
                         "rule": f"(1 - phi_e) c_h {keep_rep * st['c_h']:.3f} < a_GA {st['a_GA']:.3f}: a replicated cost-of-revenue cut "
                                 f"(pass-through elasticity {ptr['elasticity']:.2f}) raises the score less than the same share of "
                                 "overhead (Part I prop:levers-position(d); Paper 2 prop:playbook-rank(d))"})
        if ncap == 0:
            excl.append({"lever": "AI capital in place of labor (owned compute or robots)", "rule": f"no activity's dc/dK exceeds g*_o + delta_K = {lv['capital_hurdle_score']:.3f} (cor:capital)"})
        if st["G_i"] < 0:
            excl.append({"lever": "acquired growth as a steady state", "rule": f"G_i {st['G_i']:.3f} < 0 and no new customers: holding growth g "
                         "needs acquired growth g + d^org (prop:acq-limits(a))"})
        # the full-charge sign rule depends on the level of X (D-1): conditional on this owner's X_o, with the evaluation
        # points in x_levels and the annuity and user-cost thresholds X/CRF and X/(r + d)
        apb = F.acquisition_price_bounds(X_o, float(p.finance.r), nrr)
        excl.append({"lever": f"acquisitions priced above {X_o:.2f} times revenue (charged in full, at this owner's weight)",
                     "rule": f"charged in full, acquired growth raises R^A_X iff X_o > k^acq (prop:acquired-score(a)); the sign flips at "
                             f"X_o = k^acq and the level of X_o is not identified (see x_levels)"
                             + (f"; spread as a level annuity the bound is {apb['annuity']:.2f}, as a user cost {apb['user_cost']:.2f} "
                                "times revenue (rem:acquired-bounds)" if apb["annuity"] is not None else ""),
                     "conditional_on_X": True, "price_bounds": apb})
        acts = (book or {}).get("activities")
        if acts is not None and len(acts):
            n_rel = int(acts.binding_target.isin(["reliability: detection", "permissibility"]).sum())
            if n_rel:
                excl.append({"lever": f"automation of {n_rel} activity units", "rule": "bound by detection or permissibility: augment or keep"})
        regimes_out[nm] = {"X_o": X_o, "r_o": r_o, "applicable": True, "levers": lv, "durability_raises_R_inf": durable,
                           "thresholds": th, "cost_of_revenue_vs_overhead": cor_vs_ga, "screening_weight": X_scr,
                           "activities_above_capital_hurdle": ncap, "excluded": excl,
                           # prop:playbook-rank(b) compares the four levers at the same proportion x (W16); demand pull,
                           # retention, the product break-even and the capital hurdle are reported separately
                           "ranking": sorted(((k2, v2) for k2, v2 in lv.items() if k2 in ("growth_automation", "overhead", "engineering",
                                                                                          "cost_of_revenue_replicable")),
                                             key=lambda kv: -kv[1]),
                           "reported_separately": {k2: lv[k2] for k2 in ("demand_pull", "demand_pull_exact", "retention_point",
                                                                          "ai_product_breakeven", "capital_hurdle_score", "capital_hurdle_value")}}
    prod_note = None
    if product and product.get("lines"):
        prod_note = "AI products: compare D_m/dG of each line with X_o - k (cor:prod-dilution(i))"
    xl = x_levels(firm, p, st, x, keep_rep, keep_own, dK, product, nrr)
    # owning compute rather than renting it (Part I rem:owncompute): the vendor markup must exceed s_srv L_srv G at psi = 1
    psi_k = float((econ.info.get("psi_equipment") or {}).get("psi", p.finance.psi_equipment))
    tau = float(econ.info.get("tau", p.finance.tau))
    G_mkt = float(firm.part1["G"])
    kc, Ls = float(p.capital.compute_capital_per_annual_dollar), float(p.capital.server_life_years)
    own = {"markup_threshold": F.own_compute_markup_threshold(G_mkt, psi_k, tau, kc, Ls), "G": G_mkt, "psi": psi_k, "tau": tau,
           "k_c": kc, "L_srv": Ls, "rule": "own rather than rent compute iff the vendor markup exceeds the threshold (rem:owncompute)",
           "markup_threshold_psi0": F.own_compute_markup_threshold(G_mkt, 0.0, tau, kc, Ls)}
    return {"state": st, "state_sm_only": {k2: st_sm[k2] for k2 in ("sigma", "a_RD", "X_hat", "G_i", "ell", "Delta", "source")},
            "proportion": x, "durable_share": dur, "pass_through": float(ptr["phi"]), "pass_through_elasticity": float(ptr["elasticity"]),
            "margin_keep_replicable": keep_rep, "margin_keep_own": keep_own, "regimes": regimes_out, "x_levels": xl, "own_compute": own,
            "binding_position": _gap_binding(st_sm), "binding_setup": _setup_binding(util, book), "product": prod_note,
            "sm_basis_bounds": sm_basis_bounds(firm, p, st),
            "check_calibration": float(F.sigma_star(ell, st["X_hat"] - k, alpha)) - st["sigma"]}
