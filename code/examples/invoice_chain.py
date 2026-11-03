#!/usr/bin/env python3
"""
invoice_chain.py: the running example of part2/theory_core.tex from its single source of truth.

Reads   data/examples/invoice_chain.yaml (every input names its source: an engine default, a params.yaml key,
        an engine prior, a data CSV or an explicit example setting) and resolves the sources with the engine's
        own parameter loader (autofrontier.config.load_params), so that the example and the engine agree.
Writes  data/examples/invoice_chain.json   every number the text quotes, plus the resolved inputs and sources
        part2/tables/invoice_macros.tex   \\newcommand macros, one per quoted number (the text types none)

Model: the core model of Section sec:tasks (unit costs, stakes-targeted review with detection, process value with
handoffs, O-ring and overhead, readiness, transition, pilot, run costs and security). Engine features outside it
are listed in the YAML under meta.not_modeled. Run:  python3 code/examples/invoice_chain.py
"""
from __future__ import annotations

import csv
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml
from scipy import integrate, optimize

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "engine" / "src"))
from autofrontier import formulas as EF  # noqa: E402
from autofrontier.config import DEFAULTS_PATH, find_data_dir, load_params, sha256_file  # noqa: E402

YAML_PATH = ROOT / "data" / "examples" / "invoice_chain.yaml"
JSON_PATH = ROOT / "data" / "examples" / "invoice_chain.json"
MACRO_PATH = ROOT / "part2" / "tables" / "invoice_macros.tex"
PRIORS = ROOT / "engine" / "src" / "autofrontier" / "priors"
DATA = ROOT / "data" / "tasks"


# ==============================================================================================================
# Resolution of sources
# ==============================================================================================================
def _csv_lookup(path: Path, key_col: str, key: str, col: str):
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if str(row[key_col]) == str(key):
                v = row[col]
                try:
                    return float(v)
                except ValueError:
                    return v
    raise KeyError(f"{path.name}: no row {key_col}={key}")


def _params_lookup(dotted: str):
    tree = yaml.safe_load(open(DATA / "params.yaml", encoding="utf-8"))
    path, _, pick = dotted.partition("|")
    node = tree
    for k in path.split("."):
        node = node[k]
    if isinstance(node, dict) and "value" in node:
        node = node["value"]
    if pick:
        node = node[pick]
    return node


def source_hashes() -> dict:
    """sha256 of the files the example's inputs come from (engine defaults first)."""
    files = {"engine/src/autofrontier/defaults.yaml": DEFAULTS_PATH,
             "data/tasks/params.yaml": DATA / "params.yaml",
             "data/tasks/params_reliability.yaml": DATA / "params_reliability.yaml",
             "data/examples/invoice_chain.yaml": YAML_PATH,
             "engine/src/autofrontier/priors/activity_attributes.csv": PRIORS / "activity_attributes.csv"}
    return {k: (sha256_file(v) if Path(v).exists() else None) for k, v in files.items()}


class Resolver:
    def __init__(self):
        self.hashes = source_hashes()          # taken before the load, compared again after the run (main)
        self.p = load_params(find_data_dir())
        self.log = {}

    def value(self, spec: dict, name: str):
        src = spec.get("source", "setting")
        if src == "setting":
            val = spec["value"]
        elif src.startswith("default:"):
            val = self.p.get(src.split(":", 1)[1])
            if spec.get("pick") == "max":
                val = max(val)
        elif src.startswith("range_low:") or src.startswith("range_high:"):
            kind, key = src.split(":", 1)
            rng = self.p.range(key)
            val = rng[0] if kind == "range_low" else rng[1]
        elif src.startswith("params:"):
            val = _params_lookup(src.split(":", 1)[1])
        elif src.startswith("prior:"):
            _, fname, rid, col = src.split(":")
            key_col = "gwa_id" if fname == "activity_attributes" else "function_id"
            val = _csv_lookup(PRIORS / f"{fname}.csv", key_col, rid, col)
        elif src.startswith("csv:"):
            _, fname, kv, col = src.split(":")
            k, v = kv.split("=")
            val = _csv_lookup(DATA / f"{fname}.csv", k, v, col)
        else:
            raise ValueError(f"unknown source {src} for {name}")
        note = None
        if spec.get("transform") == "log1p":
            # annual rate to the continuous rate of the model. Guarded so that it is right whether or not the engine
            # has already converted its default: apply only if the resolved value is still the annual source value.
            key = src.split(":", 1)[1]
            leaf = self.p.meta(key) if src.startswith("default:") else {}
            link = leaf.get("params")
            annual = _params_lookup(link) if link else None
            if leaf.get("transform") in ("log1p", "annual_to_continuous") or (annual is not None and abs(float(val) - float(annual)) > 1e-12):
                note = "engine value already continuous; log1p not applied"
            else:
                val = math.log1p(float(val))
                note = "log1p applied to the annual rate"
        self.log[name] = {"value": val, "source": src, **({"basis": spec["basis"]} if "basis" in spec else {}),
                          **({"transform": spec["transform"], "transform_note": note} if note else {})}
        return val


def load_inputs(path: Path = YAML_PATH, overrides: dict | None = None) -> dict:
    """Resolve every input of the YAML. Returns a flat dict P (parameters), the steps list and the source log."""
    spec = yaml.safe_load(open(path, encoding="utf-8"))
    R = Resolver()
    P = {}
    for k, s in spec["firm"].items():
        P[k] = R.value(s, k)
    for k, s in spec["parameters"].items():
        P[k] = R.value(s, k)
    P["high_rel_gwas"] = R.value(spec["high_rel_gwas"], "high_rel_gwas")
    sens = {}
    for k, s in spec["sensitivity"].items():
        sens[k] = {"low": R.value({"source": s["low"]}, f"{k}_low"), "high": R.value({"source": s["high"]}, f"{k}_high")}
    steps = []
    for st in spec["steps"]:
        s = {"id": st["id"], "name": st["name"], "t": R.value(st["t_hours"], f"t_{st['id']}"),
             "gwa": R.value(st["gwa"], f"gwa_{st['id']}")}
        g = s["gwa"]
        for col in ("r_bar", "L_mult", "iota_star", "separable", "eliminable"):
            s[col] = R.value({"source": f"prior:activity_attributes:{g}:{col}"}, f"{col}_{st['id']}")
        # regulated status of the process (a setting with its reason); absent, the engine rule (target >= 0.99) applies
        s["regulated_set"] = bool(R.value(st["regulated"], f"regulated_{st['id']}")) if "regulated" in st else None
        steps.append(s)
    cap = {}
    for k, s_ in spec["capital"].items():
        cap[k] = R.value(s_, k)
    for k, s_ in spec.get("parameters_extra", {}).items():
        P[k] = R.value(s_, k)
    if overrides:
        P.update(overrides)
    return {"P": P, "steps": steps, "sensitivity": sens, "capital": cap, "log": R.log, "meta": spec["meta"],
            "hashes": R.hashes}


# ==============================================================================================================
# Model (core Section sec:tasks with engine parameter values)
# ==============================================================================================================
def _startswith_any(g, prefixes):
    return any(str(g).startswith(str(x)) for x in prefixes)


def class_mult(g, cm):
    for k in sorted(cm, key=len, reverse=True):
        if str(g).startswith(k):
            return cm[k]
    return 1.0


class Chain:
    """Activity- and process-level quantities of the invoice chain for given inputs."""

    def __init__(self, inp: dict):
        self.inp = inp
        P = self.P = inp["P"]
        # own copies: the per-step attributes below depend on this chain's parameters (q_cap, d_R), so chains built
        # from one input set must not share step dicts (a shared list let a later chain overwrite an earlier one's
        # targets; fixed in the P2 theory pass v2, 29 Oct 2026)
        self.S = [dict(s) for s in inp["steps"]]
        self.J = len(self.S)
        self.v = float(P["volume"])
        self.w = P["wage_annual"] * (1 + P["tau_L"]) / P["hours_per_fte"]
        self.a = float(EF.capital_recovery_factor(P["r"], P["T_A"]))
        self.reval_f = float(EF.revalidation_factor(P["r"], P["T_up"]))
        hr = bool(P["high_reliability"])
        for s in self.S:
            g = s["gwa"]
            s["qbar"] = max(s["r_bar"], P["r_bar_high"]) if (hr and g in P["high_rel_gwas"]) else s["r_bar"]
            s["qbar_policy"] = s["qbar"]
            if P.get("q_cap") is not None:      # conditional case: the firm accepts more residual error (a policy choice)
                s["qbar"] = min(s["qbar"], P["q_cap"])
            s["Lm"] = max(s["L_mult"], P["L_mult_regulated"]) if (hr and g in P["high_rel_gwas"]) else s["L_mult"]
            s["iota_min"] = s["iota_star"]
            s["task_type"] = ("decision" if _startswith_any(g, P["decision_gwas"]) else
                              "creation" if _startswith_any(g, P["creation_gwas"]) else "other")
            s["gui"] = _startswith_any(g, P["computer_use_gwas"])
            s["cm"] = class_mult(g, P["class_multiplier"])
            s["outsourceable"] = s["separable"] >= P["separable_threshold"]
            s["eliminable_ok"] = bool(s["eliminable"])
            # regulated status comes from the process (YAML setting); the engine's rule (target >= 0.99) is the fallback
            s["regulated"] = s["regulated_set"] if s.get("regulated_set") is not None else (s["qbar"] >= 0.99)
            t = s["t"]
            s["wt"] = self.w * t
            s["L"] = s["Lm"] * self.w * t
            s["w_tR"] = P["wage_premium"] * self.w * P["rho_rev"] * t
            s["d_eff"] = float(EF.effective_task_length(t, P["exposure"], P["transfer"], P["xi_exposure"], P["exposure_floor"]))
            # builds (engine build formula, spec 3)
            hours = self.v * t
            scope = max(hours / P["hours_per_fte"], 0.05) ** P["scope_elasticity"]
            months = P["em_base"] * (1 + t) ** P["xi_d"] * (P["regulated_mult"] if s["regulated"] else 1.0) * scope
            ai_month = P["ai_engineer_wage"] * P["ai_engineer_premium"] * (1 + P["tau_L"]) / 12.0
            s["FA"] = months * ai_month * (1 + P["vendor_share"])
            s["FU"] = P["U_share"] * s["FA"]
            # augmentation
            betaU = P["beta_U"] * P["exposure"] / P["exposure_ref"]
            s["tU"] = t / (1 + betaU)
            eU = float(EF.augment_quality_error(P["e_H"], s["task_type"], P["u_decision"], P["u_creation"]))
            s["deU"] = eU - P["e_H"]
            s["piU"] = P["pi_h0"] * s["cm"] * t * P["u_tok"]
        self.edges = [(j, j + 1) for j in range(self.J - 1)]
        self.E = sum(self.v * s["wt"] for s in self.S)                    # in-house labor-equivalent spend
        self.Lp = P["lambda_out"] * sum(s["wt"] for s in self.S)          # loss per failed output
        self.Xi = P["Xi_share"] * self.E

    # ---- activity level ---------------------------------------------------------------------------------------
    def e_cap(self, s, iota):
        P = self.P
        kap = float(EF.kappa_ctx(iota, P["context_coverage"], P["xi_context"]))
        if s["gui"] and iota < P["api_readiness"]:
            kap *= P["computer_use_mult"]
        return float(EF.capability_error(s["d_eff"], P["H0"] * kap, P["b_logistic"], P["chi_form"]))

    def e_raw(self, s, iota):
        P = self.P
        e_ctx = float(EF.raw_error_readiness(iota, P["e0"], P["e1"]))
        return float(EF.combine_errors(e_ctx, self.e_cap(s, iota)))

    def pin(self, s, iota):
        P = self.P
        retry = 1.0 / (1.0 - min(self.e_cap(s, iota), P["retry_cap"]))
        return P["pi_h0"] * s["cm"] * s["t"] * retry * (1 + P["finops_share"])

    def review(self, s, iota, d=None):
        d = self.P["d_R"] if d is None else d
        e = self.e_raw(s, iota)
        epsb = 1 - s["qbar"]
        feasible = e * (1 - d) <= epsb + 1e-12
        xiE = math.exp(-s["w_tR"] / (d * e * s["L"]))
        xiR = (1 - epsb / e) / d
        xi = min(1.0, max(xiE, xiR, self.P["xi_min"]))
        term = xi * (1 + math.log(1 / xi)) if xi > 0 else 0.0
        cQ = s["w_tR"] * xi + e * s["L"] * (1 - d * term)
        eps = e * (1 - d * xi)
        return dict(e=e, xi=xi, cQ=cQ, eps=eps, feasible=bool(feasible), d_star=max(1 - epsb / e, 0.0))

    def feasible_A(self, s, iota, d=None):
        return (iota >= s["iota_min"] - 1e-12) and self.review(s, iota, d)["feasible"]

    def cost_A(self, s, iota, d=None, include_build=True):
        rv = self.review(s, iota, d)
        return self.pin(s, iota) + rv["cQ"] + (s["FA"] * self.a / self.v if include_build else 0.0)

    def costs_alt(self, s, iota):
        """Non-automated modes: H, O (if separable), U, N (if eliminable and iota >= iota_N)."""
        P = self.P
        c = {"H": s["wt"]}
        if s["outsourceable"]:
            c["O"] = (P["rho_O"] + P["kappa_O"] + P["zeta_O"]) * s["wt"]
        c["U"] = self.w * s["tU"] + s["piU"] + s["deU"] * s["L"] + s["FU"] * self.a / self.v
        if s["eliminable_ok"] and iota >= P["iota_N"]:
            FN = P["redesign_months"] * P["process_owner_wage"] * (1 + P["tau_L"]) / 12.0
            c["N"] = P["delta_N"] * s["wt"] + FN * self.a / self.v
        return c

    def best_alt(self, s, iota):
        c = self.costs_alt(s, iota)
        m = min(c, key=c.get)
        return m, c[m]

    # ---- process level -----------------------------------------------------------------------------------------
    def eta(self, yi, yj, iota):
        P, w = self.P, self.w
        if yi == "A" and yj == "A":
            return P["h_AA0"] * (1 - iota) * w
        if yi == "A" or yj == "A":
            return P["h_AM"] * w
        return P["h_MM"] * w

    def W(self, Z, iota, require_feasible=True, d=None, run_costs=False):
        """Value of automating the set Z (Assumption ass:tasks-process): C_p(empty) - C_p(Z)."""
        Z = set(Z)
        if require_feasible and not all(self.feasible_A(self.S[j], iota, d) for j in Z):
            return -np.inf
        val = 0.0
        qA, qM = [], []
        for j, s in enumerate(self.S):
            if j in Z:
                val += self.v * (self.best_alt(s, iota)[1] - self.cost_A(s, iota, d))
        for (i, j) in self.edges:
            yi, yj = ("A" if i in Z else "M"), ("A" if j in Z else "M")
            val += self.v * (self.eta("M", "M", iota) - self.eta(yi, yj, iota))
        Q0 = self.P["q_M"] ** self.J
        QZ = np.prod([1 - self.review(self.S[j], iota, d)["eps"] if j in Z else self.P["q_M"] for j in range(self.J)])
        val += self.v * self.Lp * (QZ - Q0)
        if len(Z) == self.J:
            val += self.Xi
        if run_costs and Z:
            val -= self.ancillary(Z)["total"]
        return val

    def C_manual(self, iota):
        """Annual cost of the cheapest manual configuration, including handoffs (the legacy cost C_0)."""
        return sum(self.v * self.best_alt(s, iota)[1] for s in self.S) + sum(self.v * self.eta("M", "M", iota) for _ in self.edges)

    def subsets(self):
        for r in range(self.J + 1):
            for Z in itertools.combinations(range(self.J), r):
                yield frozenset(Z)

    def dividends(self, iota, d=None):
        Z = range(self.J)
        unit = sum(self.v * (self.best_alt(s, iota)[1] - self.cost_A(s, iota, d)) for s in self.S)
        coord = sum(self.v * (self.eta("M", "M", iota) - self.eta("A", "A", iota)) for _ in self.edges)
        QJ = np.prod([1 - self.review(s, iota, d)["eps"] for s in self.S])
        Q0 = self.P["q_M"] ** self.J
        rel = self.v * self.Lp * (QJ - Q0)
        return dict(unit=unit, coord=coord, rel=rel, overhead=self.Xi, total=unit + coord + rel + self.Xi, Q_A=QJ, Q_M=Q0)

    # ---- run costs and security (Section sec:tasks-ancillary) --------------------------------------------------
    def exposure(self, mode):
        P = self.P
        sens = P["class_sensitivity"][P["data_class"]]
        reach = min(max(P["n_systems"] / max(P["n_systems_ref"] * 2, 1.0), 0.0), 1.0)
        aut = P["autonomy_A"] if mode == "A" else P["autonomy_U"]
        if mode == "U":
            reach *= 0.5
        return float(EF.exposure_score(sens, aut * P["write_access"], reach, P["external_inputs"]))

    def ancillary(self, Z):
        P = self.P
        Z = sorted(set(Z))
        N_int = float(np.clip(round(P["n_systems"]), 1, 4))
        maint = sum(P["delta_M"] * self.S[j]["FA"] for j in Z)
        reval = sum(P["reval_share"] * self.S[j]["FA"] * self.reval_f for j in Z)
        tint = P["c_int"] * N_int * len(Z)
        tcpl = sum(P["c_cpl"] * N_int * N_int for (i, j) in self.edges if i in Z and j in Z)
        L_inc = P["L_inc_class"][P["data_class"]] * P["breach_avg"] * P["per_process_share"] * P["L_inc_scale"]
        Om = self.exposure("A")
        Cinc = sum(Om * (P["h_f"] + P["h_u"] * self.v) * L_inc for _ in Z)
        risk = float(EF.risk_cost(Cinc, P["C_s"])) if Z else 0.0
        spend = float(EF.security_spend(Cinc, P["C_s"])) if Z else 0.0
        redteam = P["redteam_cost"] if (Z and Om > 0.6) else 0.0
        total = maint + reval + tint + tcpl + risk + redteam
        return dict(maintenance=maint, revalidation=reval, integrations=tint, coupling=tcpl, tech_debt=tint + tcpl,
                    C_inc=Cinc, risk=risk, security_spend=spend, residual=risk - spend, redteam=redteam,
                    exposure_A=Om, L_inc=L_inc, N_int=N_int, total=total)


# ==============================================================================================================
# Transition (Assumption ass:tasks-transition, Prop prop:tasks-transition) with engine conventions
# ==============================================================================================================
def ramp_lin(u):
    return u


def transition_npv(T, Tpar):
    r, Th = T["r"], T["Th"]
    A = (1 - math.exp(-r * Tpar)) / r
    rampPV = integrate.quad(lambda tt: math.exp(-r * tt) * tt / Tpar, 0, Tpar)[0] if Tpar > 0 else 0.0
    tailPV = (math.exp(-r * Tpar) - math.exp(-r * Th)) / r
    pu = math.exp(-Tpar / T["Tdet"]) if Tpar > 0 else 1.0
    om = T["pis"]
    return (-(T["F"] + T["I"] + T["CJ"]) - T["Cpar"] * A + om * T["bbar"] * T["W"] * (rampPV + tailPV)
            - math.exp(-r * Tpar) * ((om + (1 - om) * pu) * T["Cstr"] + (1 - om) * pu * T["Lroll"]))


def T_par_star(T):
    chat = T["Cpar"] + T["pis"] * T["bbar"] * T["W"] * 0.5
    Rr = (1 - T["pis"]) * (T["Cstr"] + T["Lroll"])
    return T["Tdet"] * math.log(Rr / (T["Tdet"] * chat)) if Rr > T["Tdet"] * chat else 0.0, chat


def T_par_policy(T):
    """Optimal undiscounted parallel run clipped to the engine's bounds for regulated, ICFR-scope processes."""
    Ts, _ = T_par_star(T)
    return min(max(Ts, T["Tpar_min"]), T["Tpar_max"]), Ts


def Ys_Yf(T, Tpar):
    r = T["r"]
    A = (1 - math.exp(-r * Tpar)) / r
    ramp = integrate.quad(lambda tt: math.exp(-r * tt) * tt / Tpar, 0, Tpar)[0]
    tail = (math.exp(-r * Tpar) - math.exp(-r * T["Th"])) / r
    pu = math.exp(-Tpar / T["Tdet"])
    base = -(T["F"] + T["I"] + T["CJ"]) - T["Cpar"] * A
    Ys = base + T["bbar"] * T["W"] * (ramp + tail) - math.exp(-r * Tpar) * T["Cstr"]
    Yf = base - math.exp(-r * Tpar) * pu * (T["Cstr"] + T["Lroll"])
    return Ys, Yf


def success_probability(ch: Chain, iota1):
    """Engine success logits (lem:tasks-success; engine plans.py) without the failure-taxonomy terms."""
    P = ch.P
    chi = float(EF.chi_reliability(P["r_A"], P["eta_r"], P["chi_form"]))
    acts = []
    for s in ch.S:
        kap = float(EF.kappa_ctx(iota1, P["context_coverage"], P["xi_context"]))
        if s["gui"] and iota1 < P["api_readiness"]:
            kap *= P["computer_use_mult"]
        lm = float(np.clip(math.log(P["H0"] * kap / (s["d_eff"] * chi)), -5, 5))
        z = P["a0"] + P["a_iota"] * iota1 + P["a_H"] * lm - P["a_R"] * float(s["regulated"])
        acts.append(dict(id=s["id"], log_margin=lm, logit=z, varpi=1 / (1 + math.exp(-z))))
    return acts


def transition_terms(ch: Chain, iota0, iota1, int_cost=None, run_costs=True, Th=None):
    P = ch.P
    Z = range(ch.J)
    v, w = ch.v, ch.w
    # savings at full realization: cash, excluding amortized builds, net of run costs (engine W)
    W_proc = ch.W(Z, iota1, require_feasible=False)
    W = W_proc + sum(s["FA"] for s in ch.S) * ch.a - sum(s["FU"] * ch.a for s in ch.S if ch.best_alt(s, iota1)[0] == "U")
    anc = ch.ancillary(Z)
    if run_costs:
        W -= anc["total"]
    C0 = ch.C_manual(iota0)
    E_p = ch.E
    n_sys = P["n_systems"]
    lic = P["license_cost_per_system"]
    C_dup = P["retire_fraction"] * n_sys * lic
    C_par = P["omega_par"] * C0 + P["nu_rec"] * E_p + C_dup
    # displaced in-house hours (U or H baseline -> A residual review hours)
    disp_h, fte_ch_in, fte_ch_out, vend_leave = 0.0, 0.0, 0.0, 0.0
    for s in ch.S:
        m, cm_ = ch.best_alt(s, iota0)
        h_new = ch.review(s, iota1)["xi"] * P["rho_rev"] * s["t"]
        fte_unit = v * s["t"] / P["hours_per_fte"]
        if m in ("H", "U"):
            h_old = s["t"] if m == "H" else s["tU"]
            disp_h += max(h_old - h_new, 0.0) * v
            fte_ch_in += fte_unit
        else:
            fte_ch_out += fte_unit
            if m == "O":
                vend_leave += v * P["rho_O"] * s["wt"]
    C_disp = disp_h * w
    fte_removed = disp_h / P["hours_per_fte"]
    affected = fte_ch_in + 0.25 * fte_ch_out
    C_brk = P["break_months_O"] / 12.0 * vend_leave + P["break_months_license"] / 12.0 * P["retire_fraction"] * n_sys * lic
    # survivors (prop:labor-survivor, theory_labor.tex), with the engine's functions: the firm's own staff on the changed
    # steps are the unit (N^hc), the displaced FTE leave it, the rest survive. (a) C^surv, the part of the excess quits
    # that grows with the displacement share, enters C^str (engine plans.py); with labor.survivor_quits_per_share = 0
    # and no share-dependent productivity loss it is zero. (b) The announcement jump eta_0 = survivor_excess_quits/T_s
    # (and delta_0 = delta_eff) is the per-wave charge O_s, which enters the wave problem like O_w, not C^str.
    w_year = w * P["hours_per_fte"]
    N_hc = fte_ch_in
    N_sv = max(N_hc - fte_removed, 0.0)
    x_share = fte_removed / max(N_hc, 1e-9)
    C_surv = float(EF.survivor_cost(N_sv, w_year, P["nu_q"], P["survivor_quits_per_share"] * x_share / max(P["T_s"], 1e-9),
                                    P["T_s"], P["c_rep"], 0.0)) * (fte_removed > 0)
    O_s = float(EF.survivor_wave_charge(N_sv, w_year, P["T_s"], P["c_rep"],
                                        P["survivor_excess_quits"] / max(P["T_s"], 1e-9), P["delta_eff"])) * (fte_removed > 0)
    C_sev = (1 - P["u_d"]) * P["severance_months"] / 12.0 * C_disp
    C_redeploy = P["u_d"] * P["redeploy_months"] / 12.0 * C_disp
    C_str = C_sev + C_brk + C_redeploy + C_surv
    C_wo = P["retire_fraction"] * n_sys * P["legacy_book_value_per_system"]
    C_J = P["dip_share"] * C0 * P["dip_years"]
    # one-time costs: builds and engine one-time ancillaries (plans.py F_tot)
    F_build = sum(s["FA"] for s in ch.S)
    po_month = P["process_owner_wage"] * (1 + P["tau_L"]) / 12.0
    rg_month = P["risk_governance_wage"] * 1.2 * (1 + P["tau_L"]) / 12.0
    regulated = any(s["regulated"] for s in ch.S)
    F_redesign = P["redesign_months"] * po_month
    F_onetime = (P["legal_review_cost"] + P["eval_data_cost"] + affected * P["change_mgmt_cost_per_fte"]
                 + P["training_hours_per_fte"] * (fte_ch_in + fte_ch_out) * (w + P["training_cost_per_hour"])
                 + (rg_month if regulated else 0.0) + P["icfr_redesign_cost"])
    cps = P["int_cost_per_system"] if int_cost is None else int_cost
    F_int = float(EF.integration_cost(iota0, iota1, n_sys, cps, P["int_convexity"])) if iota1 > iota0 else 0.0
    F_total = F_build + F_redesign + F_onetime + F_int
    # success probability
    acts = success_probability(ch, iota1)
    exc = 1.0 - P["exposure"]
    proc_logit = (P["c0"] - P["c_exc"] * exc - P["c_fte"] * math.log1p(affected / 50.0)
                  + P["c_team"] * (P["team_prior"] - 0.5) + P["c_sponsor"] * (P["sponsor_prior"] - 0.5))
    varpi = float(np.clip((1 / (1 + math.exp(-proc_logit))) * np.prod([a["varpi"] for a in acts]), 1e-4, 0.9999))
    T = dict(r=P["r"], Th=P["T_h"] if Th is None else Th, W=W, F=F_total, I=0.0, CJ=C_J, Cpar=C_par, Cstr=C_str,
             Cwo=C_wo, pis=varpi, bbar=P["b_bar"], Tdet=P["T_det"], Lroll=P["L_roll_mult"] * C0,
             Tpar_min=max(P["T_par_min_regulated"], P["icfr_min_parallel"]), Tpar_max=P["T_par_max"])
    detail = dict(W_process=W_proc, run_costs=anc["total"] if run_costs else 0.0, C0=C0, E_p=E_p, C_dup=C_dup,
                  C_disp=C_disp, C_sev=C_sev, C_brk=C_brk, C_redeploy=C_redeploy, C_surv=C_surv, O_s=O_s, N_hc=N_hc,
                  N_sv=N_sv, x_share=x_share, w_year=w_year, fte_removed=fte_removed,
                  affected_fte=affected, F_build=F_build, F_redesign=F_redesign, F_onetime=F_onetime, F_int=F_int,
                  int_cost_per_system=cps, proc_logit=proc_logit, process_factor=1 / (1 + math.exp(-proc_logit)),
                  activity_success=acts)
    return T, detail


def npv_opt(T):
    """Risk-adjusted NPV at the engine's parallel-run policy (optimal, clipped to its bounds)."""
    Tp, _ = T_par_policy(T)
    return transition_npv(T, Tp)


def evaluate_transition(T):
    Tp, Ts = T_par_policy(T)
    npv = transition_npv(T, Tp)
    det = transition_npv(dict(T, pis=1.0, bbar=1.0), Tp)
    Ys, Yf = Ys_Yf(T, Tp)
    chat = T["Cpar"] + T["pis"] * T["bbar"] * T["W"] * 0.5
    resid = (1 - T["pis"]) * math.exp(-Tp / T["Tdet"])
    payback = (T["F"] + T["I"] + T["CJ"] + T["Cstr"]) / T["W"] if T["W"] > 0 else math.inf
    ext = 0.5 * (0.5 + T["Cpar"] / T["W"]) if T["W"] > 0 else math.inf
    out = dict(T_par=Tp, T_par_star=Ts, NPV=npv, NPV_certain=det, Y_s=Ys, Y_f=Yf, residual_risk=resid,
               payback=payback, payback_extension_6m=ext)
    # break-evens
    f_F = lambda F_: npv_opt(dict(T, F=F_))
    out["F_breakeven"] = optimize.brentq(f_F, -5e7, 5e7) if f_F(-5e7) * f_F(5e7) < 0 else None
    f_T = lambda th: npv_opt(dict(T, Th=th))
    out["NPV_unlimited"] = f_T(1e4)
    out["T_h_breakeven"] = optimize.brentq(f_T, 0.6, 1e4) if f_T(0.6) < 0 < f_T(1e4) else None
    f_p = lambda pp: npv_opt(dict(T, pis=pp))
    out["NPV_varpi_one"] = f_p(0.9999)
    out["varpi_breakeven"] = optimize.brentq(f_p, 1e-4, 0.9999) if f_p(1e-4) < 0 < f_p(0.9999) else None
    return out


# ==============================================================================================================
# Run everything the text quotes
# ==============================================================================================================
def iota_first_feasible(ch: Chain, s, d=None):
    """Lowest readiness at which step s can be automated (readiness floor and detection threshold)."""
    if ch.feasible_A(s, 1.0, d) is False:
        return None
    lo, hi = 0.0, 1.0
    if ch.feasible_A(s, 0.0, d):
        return 0.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if ch.feasible_A(s, mid, d):
            hi = mid
        else:
            lo = mid
    return hi


def activity_rows(ch: Chain, i0, i1):
    P = ch.P
    rows = []
    for s in ch.S:
        r0, r1 = ch.review(s, i0), ch.review(s, i1)
        m0, c0 = ch.best_alt(s, i0)
        m1, c1 = ch.best_alt(s, i1)
        f0, f1 = ch.feasible_A(s, i0), ch.feasible_A(s, i1)
        rows.append(dict(id=s["id"], name=s["name"], gwa=s["gwa"], t=s["t"], task_type=s["task_type"], qbar=s["qbar"],
                         L=s["L"], L_mult=s["Lm"], iota_min=s["iota_min"], c_H=s["wt"], alt_low=m0, c_M_low=c0,
                         alt_high=m1, c_M_high=c1, costs_alt_high=ch.costs_alt(s, i1), pi_n_high=ch.pin(s, i1),
                         e_low=r0["e"], e_high=r1["e"], e_cap_low=ch.e_cap(s, i0), e_cap_high=ch.e_cap(s, i1),
                         d_star_high=r1["d_star"], max_reliability_high=1 - r1["e"] * (1 - P["d_R"]),
                         feasible_low=f0, feasible_high=f1,
                         c_A_low=ch.cost_A(s, i0) if f0 else None, c_A_high=ch.cost_A(s, i1) if f1 else None,
                         xi_low=r0["xi"] if f0 else None, xi_high=r1["xi"] if f1 else None,
                         eps_high=r1["eps"] if f1 else None, F_A=s["FA"], F_U=s["FU"], w_tR=s["w_tR"],
                         iota_feasible=iota_first_feasible(ch, s), e_full=ch.e_raw(s, 1.0),
                         max_reliability_full=1 - ch.e_raw(s, 1.0) * (1 - P["d_R"])))
    return rows


def process_results(ch: Chain, i0, i1):
    J = ch.J
    full = frozenset(range(J))
    lo_feas = max(iota_first_feasible(ch, s) for s in ch.S)
    out = dict(iota_chain_feasible=lo_feas)
    Wf = lambda io: ch.W(full, io)
    out["W_full_low"] = Wf(i0) if np.isfinite(Wf(i0)) else None
    out["W_full_high"] = Wf(i1)
    # readiness threshold
    if Wf(1.0) > 0:
        if Wf(lo_feas + 1e-9) >= 0:
            istar = lo_feas
        else:
            istar = optimize.brentq(lambda io: ch.W(full, io), lo_feas + 1e-9, 1.0, xtol=1e-12)
    else:
        istar = None
    out["iota_star_p"] = istar
    # proper subsets: first readiness at which some proper subset has positive value
    grid = np.linspace(0.3, 1.0, 1401)
    fp = None
    for io in grid:
        if any(ch.W(Z, io) > 0 for Z in ch.subsets() if 0 < len(Z) < J):
            fp = float(io)
            break
    out["first_positive_proper"] = fp
    out["aon_low"] = max(lo_feas, istar - 0.1) if istar is not None else None
    # dividends and stand-alone values at i1
    out["dividends_high"] = ch.dividends(i1)
    out["singles_high"] = {ch.S[j]["id"]: ch.W(frozenset([j]), i1) for j in range(J)}
    vals = {Z: ch.W(Z, i1) for Z in ch.subsets()}
    best = max(vals, key=vals.get)
    out["best_set_high"] = sorted(ch.S[j]["id"] for j in best)
    piece = frozenset(j for j in range(J) if np.isfinite(vals[frozenset([j])]) and vals[frozenset([j])] > 0)
    out["piecemeal_set"] = sorted(ch.S[j]["id"] for j in piece)
    out["piecemeal_value"] = vals[piece] if piece else 0.0
    out["C_manual_low"] = ch.C_manual(i0)
    out["C_manual_high"] = ch.C_manual(i1)
    out["E_inhouse"] = ch.E
    out["W_by_iota"] = {f"{x:.2f}": (ch.W(full, x) if np.isfinite(ch.W(full, x)) else None) for x in (0.8, 0.85, 0.9, 0.95)}
    iN = ch.P["iota_N"]
    # the benchmark changes at iota_N, where elimination of capture becomes feasible: W(full) just below and above it
    wb, wa = ch.W(full, iN - 1e-9), ch.W(full, iN + 1e-9)
    out["W_below_N"] = wb if np.isfinite(wb) else None
    out["W_above_N"] = wa if np.isfinite(wa) else None
    try:
        out["iota_star_above_N"] = optimize.brentq(lambda io: ch.W(full, io), iN + 1e-9, 1.0, xtol=1e-12)
    except ValueError:
        out["iota_star_above_N"] = None
    out["best_value_high"] = vals[best]
    # first readiness at which the best (nonempty) set of steps pays
    lows = [x for x in (iota_first_feasible(ch, s_) for s_ in ch.S) if x is not None]
    g2 = np.linspace(min(lows + [1.0]), 1.0, 2001)

    def first_pay(Z):
        Wz = [ch.W(Z, x) for x in g2]
        k = next((i for i, w_ in enumerate(Wz) if np.isfinite(w_) and w_ > 0), None)
        if k is None:
            return None
        if k == 0 or not np.isfinite(Wz[k - 1]):
            a_ = max(iota_first_feasible(ch, ch.S[j]) for j in Z)
            if ch.W(Z, a_ + 1e-9) > 0:
                return a_
            return optimize.brentq(lambda x: ch.W(Z, x), a_ + 1e-9, g2[k], xtol=1e-12)
        return optimize.brentq(lambda x: ch.W(Z, x), g2[k - 1], g2[k], xtol=1e-12)
    fps = {Z: first_pay(Z) for Z in ch.subsets() if len(Z) > 0}
    fps = {Z: v_ for Z, v_ in fps.items() if v_ is not None}
    if fps:
        Zf = min(fps, key=fps.get)
        out["best_first_pays_iota"] = fps[Zf]
        out["best_first_pays_set"] = sorted(ch.S[j]["id"] for j in Zf)
    else:
        out["best_first_pays_iota"], out["best_first_pays_set"] = None, []
    out["any_set_pays_high"] = bool(vals[best] > 0)
    pair = frozenset(j for j in range(J) if ch.S[j]["id"] in ("exceptions", "approval"))
    out["pair_exc_appr_high"] = vals[pair]
    xis = [ch.review(s_, i1)["xi"] for s_ in ch.S if ch.feasible_A(s_, i1)]
    out["xi_high_min"], out["xi_high_max"] = (min(xis), max(xis)) if xis else (None, None)
    out["Xi"] = ch.Xi
    out["L_p"] = ch.Lp
    return out


def augment_exceptions(ch: Chain, i1):
    s = next(x for x in ch.S if x["id"] == "exceptions")
    cU = ch.costs_alt(s, i1)["U"]
    sweep = {}
    for d in (1.0, 0.9, 0.85, ch.P["d_R"], 0.455):
        sweep[f"{d:.3f}"] = ch.cost_A(s, i1, d) if ch.review(s, i1, d)["feasible"] else None
    d_inf = ch.review(s, i1)["d_star"]
    # detection rate at which automation ties augmentation at i1
    try:
        d_tie = optimize.brentq(lambda d: ch.cost_A(s, i1, d) - cU, max(d_inf, 1e-3) + 1e-9, 1.0)
    except ValueError:
        d_tie = None
    # activity threshold iota*_3
    lo = iota_first_feasible(ch, s)
    f = lambda io: ch.cost_A(s, io) - ch.costs_alt(s, io)["U"]
    if lo is None:
        ist = None
    elif f(lo + 1e-9) <= 0:
        ist = lo
    elif f(1.0) > 0:
        ist = None
    else:
        ist = optimize.brentq(f, lo + 1e-9, 1.0)
    return dict(c_U=cU, c_A_high=ch.cost_A(s, i1) if ch.feasible_A(s, i1) else None, sweep=sweep, d_infeasible=d_inf,
                d_tie=d_tie, iota_star=ist)


def score_path(T, Tpar, S, years, T_A, basis):
    out = []
    for y in range(1, years + 1):
        lo, hi = y - 1, y
        f = lambda tt: (T["bbar_path"] * T["W"] * (tt / Tpar) - T["Cpar"]) if tt < Tpar else T["bbar_path"] * T["W"]
        val = integrate.quad(f, lo, hi, points=[Tpar] if lo < Tpar < hi else None)[0]
        if y == 1:
            val -= T["CJ"] + (T["F"] + T["I"] if basis == "cash" else 0)
        if lo <= Tpar < hi:
            val -= T["Cstr"] + (T["Cwo"] if basis == "gaap" else 0)
        if basis == "gaap":
            val -= T["F"] / T_A * max(0, min(hi, T_A) - lo)
        out.append(val / S)
    return out


def pilot_results(T, Tpar, F_pil, T_pil):
    Ys, Yf = Ys_Yf(T, Tpar)
    om = T["pis"]
    d = math.exp(-T["r"] * T_pil)
    vp = lambda dd: dd * (om * max(Ys, 0) + (1 - om) * max(Yf, 0)) - F_pil - max(0.0, om * Ys + (1 - om) * Yf)
    out = dict(F_pil=F_pil, T_pil=T_pil, Y_s=Ys, Y_f=Yf, VP=vp(1.0), VP_delay=vp(d))
    if Ys > 0:
        out.update(gate=abs(Yf) / (Ys + abs(Yf)), band_low=F_pil / Ys, band_high=1 - F_pil / abs(Yf),
                   band_low_delay=F_pil / (d * Ys), band_high_delay=(abs(Yf) - F_pil) / (abs(Yf) + (1 - d) * Ys))
    return out


def compute(inp: dict) -> dict:
    P0 = inp["P"]
    i0, i1 = P0["iota_low"], P0["iota_high"]
    # ---------------- default (every input at its source) ----------------
    ch = Chain(inp)
    rows = activity_rows(ch, i0, i1)
    d_req = max(r["d_star_high"] for r in rows)
    sx = next(x for x in ch.S if x["id"] == "exceptions")
    lo_x = iota_first_feasible(ch, sx)
    fx = lambda io: ch.cost_A(sx, io) - ch.costs_alt(sx, io)["U"]
    ist_x = (lo_x if fx(lo_x + 1e-9) <= 0 else optimize.brentq(fx, lo_x + 1e-9, 1.0)) if (lo_x is not None and fx(1.0) < 0) else None
    exc_default = dict(iota_feasible=lo_x, iota_star=ist_x, c_U=ch.costs_alt(sx, i1)["U"])
    default = dict(exceptions=exc_default, wage=ch.w, revenue=ch.v / P0["invoices_per_musd_revenue"] * 1e6, activities=rows,
                   chain_feasible_high=all(r["feasible_high"] for r in rows), d_required_high=d_req,
                   C_manual_low=ch.C_manual(i0), E_inhouse=ch.E)
    # ---------------- conditional case (redesigned 29 Oct 2026, P2 theory pass v2): every empirical input within its
    # measured range, detection at the top of its range; the reliability target, a policy choice, is capped at
    #   q_cap = min(r_bar_high, q*),  q* = the highest level (rounded down to 0.1 point) that every step whose target is
    #   above the chain's lowest can meet at the high readiness target.
    # Since the params commit r_bar_high is human parity (0.98, APQC top performers), so the cap relaxes only the steps
    # whose own prior asks for more than human parity (approval, 0.99 from its activity prior) and never raises a
    # target; the earlier rule q_cap = q* (0.988) exceeded r_bar_high and would have raised the default target
    # (params commit flag 6). If the chain cannot meet human parity, q* < r_bar_high binds instead. ----------------
    d_ill = inp["sensitivity"]["d_R"]["high"]
    ch_hi = Chain(dict(inp, P=dict(P0, d_R=d_ill)))
    q_star_exact = min(1 - ch_hi.e_raw(s_, i1) * (1 - d_ill) for s_ in ch_hi.S if s_["qbar"] > min(x["qbar"] for x in ch_hi.S))
    q_star = math.floor(q_star_exact * 1000 + 1e-9) / 1000
    q_cap = min(P0["r_bar_high"], q_star)
    human_ok = (1 - q_cap) <= P0["e_H"] + 1e-12
    inp_ill = dict(inp, P=dict(P0, d_R=d_ill, q_cap=q_cap))
    ci = Chain(inp_ill)
    relaxed = [dict(id=s_["id"], policy=s_["qbar_policy"], capped=s_["qbar"]) for s_ in ci.S if s_["qbar_policy"] > s_["qbar"] + 1e-12]
    # sensitivity: the earlier design (cap at q* alone, which relaxes approval only to the highest level the chain meets)
    ci_q = Chain(dict(inp, P=dict(P0, d_R=d_ill, q_cap=q_star)))
    pr_q = process_results(ci_q, i0, i1)
    alt_qstar = dict(q_cap=q_star, W_full_high=pr_q["W_full_high"], pair_exc_appr_high=pr_q["pair_exc_appr_high"],
                     any_set_pays_high=pr_q["any_set_pays_high"], best_first_pays_iota=pr_q["best_first_pays_iota"],
                     best_first_pays_set=pr_q["best_first_pays_set"], iota_star_above_N=pr_q["iota_star_above_N"],
                     iota_chain_feasible=pr_q["iota_chain_feasible"])
    ill = dict(d_R=d_ill, q_cap=q_cap, q_star=q_star, q_star_exact=q_star_exact, r_bar_high=P0["r_bar_high"],
               residual_accepted=1 - q_cap, e_H=P0["e_H"], relaxed_steps=relaxed,
               target_above_human_baseline=bool(human_ok),
               rule="detection at the top of its measured range; every target capped at min(r_bar_high, q*), where "
                    "r_bar_high is the human-parity target and q* the highest level, rounded down to 0.1 point, that "
                    "every step can meet at the high readiness target; the cap never raises a target",
               chain_feasible_high=all(ci.feasible_A(s_, i1) for s_ in ci.S),
               activities=activity_rows(ci, i0, i1), process=process_results(ci, i0, i1),
               augment_exceptions=augment_exceptions(ci, i1), alt_qstar=alt_qstar)
    # ---------------- transition: case (a) low readiness, case (b) data already integrated ----------------
    P = ci.P
    cases = {}
    for case, (a0, a1) in {"a": (i0, i1), "b": (i1, i1)}.items():
        cases[case] = {}
        for lvl, cps in (("low", inp["sensitivity"]["int_cost_per_system"]["low"]), ("default", P["int_cost_per_system"]),
                         ("high", inp["sensitivity"]["int_cost_per_system"]["high"])):
            T, det = transition_terms(ci, a0, a1, int_cost=cps)
            ev = evaluate_transition(T)
            cases[case][lvl] = dict(int_cost_per_system=cps, F_int=det["F_int"], F=T["F"], NPV=ev["NPV"],
                                    NPV_certain=ev["NPV_certain"], F_breakeven=ev["F_breakeven"])
    Ta, Da = transition_terms(ci, i0, i1)
    Ea = evaluate_transition(Ta)
    Tb, Db = transition_terms(ci, i1, i1)
    Eb = evaluate_transition(Tb)
    # horizons: 3, 5 and the engine planning horizon
    hz = {f"{h:g}": npv_opt(dict(Ta, Th=h)) for h in (3.0, 5.0, float(P["T_h_engine"]))}
    # the engine's planning horizon as a program: on the success branch the builds are redone every T_A years
    # at the declined build cost F_build (1 - delta_F)^(k T_A) (plans.py, rebuilds in CF1)
    Th_e = float(P["T_h_engine"])
    rebuilds = [k * P["T_A"] for k in range(1, int(Th_e / P["T_A"]) + 2) if k * P["T_A"] < Th_e]
    reb_pv = Ta["pis"] * Da["F_build"] * sum((1 - P["delta_F"]) ** tk * math.exp(-P["r"] * tk) for tk in rebuilds)
    hz["program"] = hz[f"{Th_e:g}"] - reb_pv
    hz["rebuild_years"] = rebuilds
    hz["rebuild_pv"] = reb_pv
    hz_b = {f"{h:g}": npv_opt(dict(Tb, Th=h)) for h in (3.0, 5.0, float(P["T_h_engine"]))}
    transition = dict(case="a", iota_from=i0, iota_to=i1, W=Ta["W"], W_before_run=Ta["W"] + Da["run_costs"], F=Ta["F"], F_build=Da["F_build"],
                      F_int=Da["F_int"], F_other=Da["F_redesign"] + Da["F_onetime"], I=0.0, C_J=Ta["CJ"],
                      C_par=Ta["Cpar"], C_str=Ta["Cstr"], C_brk=Da["C_brk"], C_sev=Da["C_sev"], C_wo=Ta["Cwo"],
                      C_surv=Da["C_surv"], O_s=Da["O_s"], NPV_own_wave=Ea["NPV"] - Da["O_s"],
                      T_par=Ea["T_par"], T_A=P["T_A"], S=default["revenue"], r=Ta["r"], T_h=Ta["Th"],
                      varpi_p=Ta["pis"], bbar_p=Ta["bbar"], T_det=Ta["Tdet"], L_roll=Ta["Lroll"], d_R=d_ill,
                      results=Ea, detail=Da, horizons=hz)
    transition_b = dict(case="b", iota_from=i1, iota_to=i1, W=Tb["W"], F=Tb["F"], F_build=Db["F_build"],
                        F_int=Db["F_int"], results=Eb, horizons=hz_b, varpi_p=Tb["pis"])
    # score path (case a, success path with b = 1, T_par = 0.5 as in Prop prop:tasks-scorepath's example)
    Ssp = dict(Ta, bbar_path=1.0)
    sp_cash = score_path(Ssp, 0.5, default["revenue"], int(round(Ta["Th"])), P["T_A"], "cash")
    sp_gaap = score_path(Ssp, 0.5, default["revenue"], int(round(Ta["Th"])), P["T_A"], "gaap")
    # pilot
    F_pil = P["pilot_cost_share"] * Da["F_build"] + P["pilot_fixed_cost"]
    pil_a = pilot_results(Ta, Ea["T_par"], F_pil, P["T_pil"])
    pil_b = pilot_results(Tb, Eb["T_par"], F_pil, P["T_pil"])
    # ---------------- run costs and security at full automation ----------------
    full = range(ci.J)
    anc = ci.ancillary(full)
    W_run = ci.W(full, i1, run_costs=True)
    lo_feas = ill["process"]["iota_chain_feasible"]
    try:
        ist_run = optimize.brentq(lambda io: ci.W(full, io, run_costs=True), lo_feas + 1e-9, 1.0, xtol=1e-12)
    except ValueError:
        ist_run = None
    vol_factor = 1 + P["delta_M"] * P["T_A"] + P["reval_share"] * P["T_A"] / P["T_up"]
    scope_500k = float(EF.risk_cost(500e3, P["C_s"]))
    ancillary = dict(anc, W_high_before=ill["process"]["W_full_high"], W_high_after=W_run, iota_star_run=ist_run,
                     volume_factor=vol_factor, scope_500k=scope_500k)
    # ---------------- detection break-evens at the high readiness target ----------------
    full_ = frozenset(range(ci.J))
    def W_d(d, run=False):
        c_ = Chain(dict(inp, P=dict(P0, d_R=d)))
        return c_.W(full_, i1, run_costs=run)
    d_feas = d_req
    try:
        d_W0 = optimize.brentq(lambda d: W_d(d), d_feas + 1e-9, 1.0)
    except ValueError:
        d_W0 = None
    detection = dict(d_feasible=d_feas, d_W_zero=d_W0, W_at_d1=W_d(1.0), W_at_d1_run=W_d(1.0, True))
    # ---------------- vendor window (match step, Prop prop:tasks-window) ----------------
    sm = next(x for x in ci.S if x["id"] == "match")
    cQm = ci.review(sm, i1)["cQ"]
    n_m = ci.pin(sm, i1) / P["pi_h0"]                     # inference units per invoice, price normalized to pi_h0
    c0A = cQm + sm["FA"] * ci.a / ci.v
    pO = P["rho_O"] * sm["wt"]
    cVH = pO / (1 + P["ups_O"])
    cV0 = cQm                                             # rule: the vendor bears the same review cost, builds pooled
    extra = (P["kappa_O"] + P["zeta_O"]) * sm["wt"]
    piV = (cVH - cV0) / n_m
    Dv = lambda pp: (1 + P["ups_O"]) * min(cVH, pp * n_m + cV0) + extra - (pp * n_m + c0A)
    D0 = Dv(0.0)
    pplus = ((1 + P["ups_O"]) * cVH + extra - c0A) / n_m
    pminus = 0.0 if D0 >= 0 else -D0 / (P["ups_O"] * n_m)
    brk = (1 + P["ups_O"]) * cV0 + extra - cQm
    vMB = sm["FA"] * ci.a / brk if brk > 0 else None
    vMB_k = sm["FA"] * ci.a / ((1 + P["ups_O"]) * cV0 + 0.5 * P["kappa_O"] * sm["wt"] + P["zeta_O"] * sm["wt"] - cQm)
    vMB_F = 0.5 * sm["FA"] * ci.a / brk if brk > 0 else None
    window = dict(step="match", c_H=sm["wt"], p_O=pO, c_VH=cVH, c_V0=cV0, c0A=c0A, n=n_m, pi_today=P["pi_h0"],
                  pi_V=piV * P["pi_h0"], pi_plus=pplus * P["pi_h0"], pi_minus=pminus * P["pi_h0"],
                  window_nonempty=bool(Dv(piV) >= 0), D_today=Dv(1.0),
                  window_years=(math.log(pplus / pminus) / P_delta_pi(inp)) if (pminus > 0 and pplus > pminus and Dv(piV) >= 0) else None,
                  v_MB=vMB, v_MB_kappa_half=vMB_k, v_MB_F_half=vMB_F, volume=ci.v)
    # ---------------- capital: owning inference capacity for the chain (Prop prop:tasks-capital) ----------------
    pn_tot = sum(ci.pin(x, i1) for x in ci.S)
    p_ = inp["capital"]
    dc = (1 - p_["owned_opex_share"]) * pn_tot
    dK = p_["compute_capital_per_annual_dollar"] * pn_tot
    capital = dict(pi_n_total=pn_tot, dc=dc, dK=dK, delta_K=p_["delta_K_compute"], g=p_["revenue_growth_g"],
                   value=dc - (P["r"] + p_["delta_K_compute"]) * dK, cash=dc - (p_["revenue_growth_g"] + p_["delta_K_compute"]) * dK,
                   gaap=dc - p_["delta_K_compute"] * dK, r=P["r"])
    # ---------------- build or buy (Prop prop:tasks-buildbuy) ----------------
    F_tot_A = sum(x["FA"] for x in ci.S)
    Cfix_b = F_tot_A * ci.a + anc["maintenance"] + anc["revalidation"] + anc["tech_debt"]
    pooled = P["buy_pooled_share"] * sum(x["wt"] for x in ci.S)
    cv_minus = (1 + P["buy_markup"]) * (pn_tot + pooled) - pn_tot
    F_int_b = P["buy_integration_share"] * F_tot_A
    Cfix_v = F_int_b * ci.a
    vBB = (Cfix_b - Cfix_v) / cv_minus
    vBB_norun = (F_tot_A * ci.a - Cfix_v) / cv_minus
    save_buy = Cfix_b - (Cfix_v + ci.v * cv_minus)
    C_sw = P["switching_cost_share"] * F_tot_A
    buildbuy = dict(C_fix_build=Cfix_b, builds_annual=F_tot_A * ci.a, run_annual=Cfix_b - F_tot_A * ci.a,
                    pooled_per_unit=pooled, c_v_minus_pin=cv_minus, F_int=F_int_b, C_fix_buy=Cfix_v, v_BB=vBB,
                    v_BB_no_run=vBB_norun, buy_saving=save_buy, C_sw=C_sw, lock_cap=C_sw / P["contract_years"],
                    markup=P["buy_markup"], contract_years=P["contract_years"])
    # ---------------- coarse data (Prop prop:tasks-ancscale): a cell of five such processes ----------------
    per_proc = anc["maintenance"] + anc["revalidation"]
    Ns = np.array([2, 4, 6, 8, 10.0])
    c_curv = 1000.0
    jensen = 0.5 * c_curv * len(Ns) * Ns.var()
    pool_gap = 5 * float(EF.risk_cost(anc["C_inc"], P["C_s"])) - float(EF.risk_cost(5 * anc["C_inc"], P["C_s"]))
    scaling = dict(P=5, per_process_fixed=per_proc, understatement_fixed=4 * per_proc, N_range=[2, 10],
                   c_curvature=c_curv, jensen=jensen, C_inc_each=anc["C_inc"], pooling_gap=pool_gap)
    # ---------------- failure taxonomy on the approval step (Section sec:tasks-failure), defaults ----------------
    failure = failure_examples(ch, i1)
    out = dict(transition=transition, meta=inp["meta"], default=default, detection=detection, illustration=ill,
               transition_b=transition_b, transition_cases=cases,
               score_path=dict(revenue=default["revenue"], T_par=0.5, cash=sp_cash, gaap=sp_gaap),
               pilot=dict(a=pil_a, b=pil_b), ancillary=ancillary, window=window, capital=capital, build_buy=buildbuy,
               scaling=scaling, failure=failure, inputs=inp["log"], source_sha256=inp["hashes"])
    return out, ci


def P_delta_pi(inp):
    return inp["capital"]["delta_pi"]


def failure_examples(ch: Chain, i1):
    """Hallucination floor, automation bias, autonomy and the loss floor for the approval step at the high
    readiness target, with every reliability input at its engine default (Section sec:tasks-failure)."""
    P = ch.P
    s = next(x for x in ch.S if x["id"] == "approval")
    e_o = ch.e_raw(s, i1)
    e_cap = ch.e_cap(s, i1)
    e_h = float(EF.hallucination_rate(P["h_retrieval"], i1, P["grounding"], e_cap, P["r_A"], P["h_floor_share"]))
    d_o, d_h = P["d_R"], P["d_h"]
    epsb = 1 - s["qbar"]
    floor = e_o * (1 - d_o) + e_h * (1 - d_h)
    floor_dh_hi = e_o * (1 - d_o) + e_h * (1 - 0.6)
    h_open = float(EF.hallucination_rate(P["h_retrieval"] * 0 + 0.15, i1, P["grounding"], e_cap, P["r_A"], P["h_floor_share"]))
    halluc = dict(e_o=e_o, e_h=e_h, d_o=d_o, d_h=d_h, tolerance=epsb, floor=floor, floor_dh_06=floor_dh_hi,
                  feasible=floor <= epsb, floor_ordinary=e_o * (1 - d_o))
    # automation bias (Prop prop:tasks-bias), conditional on the engine's eps_d
    eps_d = P["eps_d"]
    share = lambda d: 0.5 * (1 + math.log(2)) * d
    bias = dict(eps_d=eps_d, peak=math.exp(-eps_d), irony_threshold=1 / (1 + eps_d), caught_top=share(0.85),
                caught_central=share(P["d_R"]), uplift=math.exp(eps_d) / (1 + eps_d), d_top=0.85, d_central=P["d_R"])
    # autonomy (Prop prop:tasks-autonomy): misbehavior scale, cap and rates from the engine
    L = s["L"]
    L_m = P["sev_mult"] * L * (1 - P["lp_cut"] * (P["write_access"] > 0)) * (1 - P["mon_cut"])
    L_cap = P["kill_cap_mult"] * L_m
    em = {lvl: float(EF.misbehavior_rate(P["m0"], P["autonomy_mult"][k], s["d_eff"], P["kappa_h"], P["external_inputs"],
                                          P["injection_mult"], P["guard_cut"]))
          for lvl, k in ((2, "act_with_approval"), (3, "act_autonomously"))}
    xi3 = ch.review(s, i1)["xi"]
    dm = {2: P["d_m_approval"], 3: 1 - (1 - P["d_mon"]) * (1 - P["d_m_review"] * xi3)}
    Zb = L_cap / L_m
    p_ = P["alpha_tail"]
    Emin = 1 + (1 - Zb ** (1 - p_)) / (p_ - 1)
    cm = {k: em[k] * (1 - dm[k]) * L_m * Emin for k in em}
    human = {1: ch.w * s["tU"], 2: P["wage_premium"] * ch.w * P["rho_appr"] * s["t"], 3: 0.0}
    cvar = lambda pp: L_m * pp * (1 - P["cvar_q"]) ** (-1 / pp) / (pp - 1)
    rev3 = ch.review(s, i1)
    autonomy = dict(L=L, L_m=L_m, L_cap=L_cap, e_m=em, d_m=dm, E_min=Emin, c_m=cm, human=human,
                    cvar_uncapped=cvar(p_), cvar_uncapped_low=cvar(P["alpha_tail_low"]), L_max=P["L_max_event"],
                    cvar_q=P["cvar_q"], feasible_level3=rev3["feasible"], d_star=rev3["d_star"])
    cerr_unit = floor * L + cm[3]
    # prop:tasks-cerr(c): full automation without people and without review: no error is caught
    noreview_unit = (e_o + e_h) * L + cm[3]
    cerr = dict(floor_unit=floor * L, misbehavior_unit=cm[3], total_unit=cerr_unit, annual=cerr_unit * ch.v, L=L,
                noreview_unit=noreview_unit, noreview_annual=noreview_unit * ch.v)
    return dict(hallucination=halluc, bias=bias, autonomy=autonomy, cerr=cerr)


# ==============================================================================================================
# Formatting and macros
# ==============================================================================================================
def _thou(x, nd=0):
    s = f"{abs(x):,.{nd}f}"
    return s.replace(",", "{,}")


def usd(x, nd=None):
    """Dollar amount in the paper's style (1.74, 4{,}000, 1.33 million, 1.2 billion; negatives with a minus sign)."""
    if x is None:
        return "n.a."
    ax = abs(x)
    if ax >= 1e9:
        body = f"\\${ax / 1e9:.1f} billion"
    elif ax >= 1e6:
        body = f"\\${ax / 1e6:.2f} million"
    elif ax >= 1000:
        body = f"\\${_thou((round(ax, -3) if ax >= 1e4 else round(ax, -2)) if nd is None else ax, 0)}"
    elif ax >= 100 and nd is None:
        body = f"\\${ax:.0f}"
    else:
        k = 2 if nd is None else nd
        body = f"\\${ax:.{k}f}"
    return ("$-$" + body) if x < 0 else body


def num(x, nd=2):
    return "n.a." if x is None else (("$-$" if x < 0 else "") + f"{abs(x):.{nd}f}")


def pct(x, nd=0):
    return "n.a." if x is None else f"{100 * x:.{nd}f}\\%"


def macros(out: dict, inp: dict) -> list[tuple[str, str]]:
    P = inp["P"]
    D, I = out["default"], out["illustration"]
    A = {r["id"]: r for r in D["activities"]}
    AI = {r["id"]: r for r in I["activities"]}
    pr, ax = I["process"], I["augment_exceptions"]
    T, R = out["transition"], out["transition"]["results"]
    TB = out["transition_b"]
    cs = out["transition_cases"]
    an, bb, sc, cap = out["ancillary"], out["build_buy"], out["scaling"], out["capital"]
    fa = out["failure"]
    m = []
    add = lambda k, v: m.append((k, v))
    # firm and inputs
    add("icVolume", _thou(P["volume"]))
    add("icRevenue", usd(D["revenue"]))
    add("icWage", usd(D["wage"]))
    add("icWageAnnual", "\\$" + _thou(P["wage_annual"]))
    add("icIotaLow", num(P["iota_low"], 1))
    add("icIotaHigh", num(P["iota_high"], 1))
    add("icIotaN", num(P["iota_N"], 1))
    add("icR", pct(P["r"], 2))
    add("icTA", f"{P['T_A']:g}")
    add("icTh", f"{P['T_h']:g}")
    add("icThEngine", f"{P['T_h_engine']:g}")
    add("icDR", num(P["d_R"], 2))
    add("icDRlow", num(inp["sensitivity"]["d_R"]["low"], 2))
    add("icDRhigh", num(inp["sensitivity"]["d_R"]["high"], 2))
    add("icDh", num(P["d_h"], 1))
    add("icRhoO", pct(P["rho_O"]))
    add("icRhoRev", num(P["rho_rev"], 3))
    add("icWagePremium", num(P["wage_premium"], 1))
    add("icBetaU", num(P["beta_U"], 2))
    add("icEzero", num(P["e0"], 2))
    add("icEone", num(P["e1"], 3))
    add("icHzero", f"{P['H0']:.0f}")
    add("icEUdecision", num(P["u_decision"] * P["e_H"] * 100, 1))
    # table rows: Step & t & c_H & c_M, mode (0.9) & pi n & e(0.4) / e(0.9) & qbar & d* (0.9) & c_A (0.9, d_ill) & F_A
    names = {"capture": "Capture", "match": "Match", "exceptions": "Exceptions", "approval": "Approval"}
    for k, nm in names.items():
        r, ri = A[k], AI[k]
        cA = f"{ri['c_A_high']:.2f}" if ri["c_A_high"] is not None else "n.f."
        add(f"icRow{nm}", f"{nm} & {r['t']:.2f} & {r['c_H']:.2f} & {r['c_M_high']:.2f}, ${r['alt_high']}$ & {r['pi_n_high']:.2f} & "
                          f"{r['e_low']:.3f} / {r['e_high']:.3f} & {r['qbar']:.2f} & {r['d_star_high']:.3f} & {cA} & {r['F_A'] / 1e3:.0f}")
        assert abs(r["F_A"] - ri["F_A"]) < 1e-6, "builds must agree across cases (regulated status is set per process)"
        add(f"icL{nm}", usd(r["L"]))
    add("icLmult", "10, 10, 3 and 10")
    add("icEhighMin", pct(min(r["e_high"] for r in A.values()), 1))
    add("icEhighMax", pct(max(r["e_high"] for r in A.values()), 1))
    add("icDstarMin", num(min(r["d_star_high"] for r in A.values()), 3))
    add("icDstarMax", num(max(r["d_star_high"] for r in A.values()), 2))
    hi99 = [r for r in A.values() if r["qbar"] >= P["r_bar_high"] - 1e-12]   # steps at the high-stakes target (0.99 before 29 Oct)
    add("icMaxRelFullMin", pct(min(r["max_reliability_full"] for r in hi99), 1))
    add("icMaxRelFullMax", pct(max(r["max_reliability_full"] for r in hi99), 1))
    add("icMaxRelExcFull", pct(A["exceptions"]["max_reliability_full"], 1))
    add("icEfullMin", pct(min(r["e_full"] for r in A.values()), 1))
    add("icEcapLow", pct(A["capture"]["e_cap_low"]))
    add("icApiReadiness", num(P["api_readiness"], 1))
    add("icPinTotal", usd(sum(r["pi_n_high"] for r in A.values())))
    add("icKappaO", num(P["kappa_O"], 2))
    add("icZetaO", num(P["zeta_O"], 2))
    add("icQMstep", num(P["q_M"], 3))
    add("icOwnedOpex", pct(inp["capital"]["owned_opex_share"]))
    add("icDeltaKcompute", pct(inp["capital"]["delta_K_compute"]))
    add("icCapPerDollar", f"{inp['capital']['compute_capital_per_annual_dollar']:g}")
    add("icDipShare", pct(P["dip_share"]))
    add("icCint", usd(P["c_int"]))
    add("icScaleCurv", usd(out["scaling"]["c_curvature"]))
    add("icQbarHigh", pct(P["r_bar_high"]))
    add("icQbarExc", pct(A["exceptions"]["qbar"]))
    add("icContractYears", f"{P['contract_years']:g}")
    add("icExcIotaFeas", num(D["exceptions"]["iota_feasible"], 3))
    add("icExcIotaStarDefault", num(D["exceptions"]["iota_star"], 2))
    add("icDfeas", num(D["d_required_high"], 2))
    add("icDill", num(I["d_R"], 2))
    pct_s = lambda x: pct(x, 0) if abs(round(100 * x) - 100 * x) < 1e-9 else pct(x, 1)   # 98\% or 98.8\%
    add("icQcap", pct_s(I["q_cap"]))
    add("icQstar", pct_s(I["q_star"]))
    add("icResidCap", pct_s(I["residual_accepted"]))
    add("icResidPolicy", pct(1 - P["r_bar_high"], 0))
    # the steps the conditional case relaxes (their own prior asks for more than human parity): approval
    rel = {x["id"]: x for x in I["relaxed_steps"]}
    assert set(rel) == {"approval"}, f"the text describes a cap on approval only; relaxed: {sorted(rel)}"
    add("icQbarAppr", pct_s(rel["approval"]["policy"]))
    add("icResidAppr", pct_s(1 - rel["approval"]["policy"]))
    add("icLmultReg", f"{P['L_mult_regulated']:g}")
    add("icLmultRegLow", f"{inp['sensitivity']['L_mult_regulated']['low']:g}")
    add("icLmultRegHigh", f"{inp['sensitivity']['L_mult_regulated']['high']:g}")
    add("icRbarHighLow", pct_s(inp["sensitivity"]["r_bar_high"]["low"]))
    add("icRbarHighHigh", pct_s(inp["sensitivity"]["r_bar_high"]["high"]))
    # default verdict: readiness at which the 98% steps reach their target at the default catch rate; approval's best
    add("icCaptureIotaFeas", num(A["capture"]["iota_feasible"], 3))
    add("icMatchIotaFeas", num(A["match"]["iota_feasible"], 3))
    add("icMaxRelApprFull", pct(A["approval"]["max_reliability_full"], 1))
    # sensitivity: the earlier cap at q* alone (approval relaxed only to the highest level the chain meets)
    aq = I["alt_qstar"]
    add("icAltWfull", usd(aq["W_full_high"]))
    add("icAltPair", usd(aq["pair_exc_appr_high"]))
    add("icAltPairLoss", usd(-aq["pair_exc_appr_high"]))
    add("icAltFirstIota", num(aq["best_first_pays_iota"], 3) if aq["best_first_pays_iota"] is not None else "n.a.")
    add("icAltIotaStarN", num(aq["iota_star_above_N"], 3) if aq["iota_star_above_N"] is not None else "n.a.")
    add("icRegMult", num(P["regulated_mult"], 1))
    add("icEHuman", pct(P["e_H"], 0))
    add("icQHuman", pct(1 - P["e_H"], 0))
    add("icIotaStarP", num(pr["iota_star_p"], 2) if pr["iota_star_p"] is not None else "n.a.")
    add("icExcAninety", usd(ax["sweep"]["0.900"]))
    add("icXiMin", num(pr["xi_high_min"], 2))
    add("icXiMax", num(pr["xi_high_max"], 2))
    # modes intuition (matching, conditional case)
    add("icMatchH", usd(A["match"]["c_H"]))
    add("icMatchO", usd(A["match"]["costs_alt_high"]["O"]))
    add("icMatchA", usd(AI["match"]["c_A_high"]))
    add("icMatchVsH", usd(P["volume"] * (A["match"]["c_H"] - AI["match"]["c_A_high"])))
    add("icMatchVsO", usd(P["volume"] * (AI["match"]["c_A_high"] - A["match"]["costs_alt_high"]["O"])))
    add("icWinCzeroA", usd(out["window"]["c0A"]))
    # augmentation of exception handling (conditional case sweep)
    add("icExcU", usd(ax["c_U"]))
    add("icExcAone", usd(ax["sweep"]["1.000"]))
    add("icExcAill", usd(ax["sweep"][f"{I['d_R']:.3f}"]))
    add("icExcAeightyfive", usd(ax["sweep"]["0.850"]))
    add("icExcDtie", num(ax["d_tie"], 2))
    add("icExcDinf", num(ax["d_infeasible"], 3))
    # process (conditional case)
    add("icCmanHigh", usd(pr["C_manual_high"]))
    add("icEinhouse", usd(pr["E_inhouse"]))
    dv = pr["dividends_high"]
    add("icDivUnit", usd(dv["unit"]))
    add("icDivCoord", usd(dv["coord"]))
    add("icDivRel", usd(dv["rel"]))
    add("icDivOver", usd(dv["overhead"]))
    add("icQM", num(dv["Q_M"], 3))
    add("icQA", num(dv["Q_A"], 3))
    add("icWfullHigh", usd(pr["W_full_high"]))
    add("icSingleCapture", usd(pr["singles_high"]["capture"]))
    add("icSingleMatch", usd(pr["singles_high"]["match"]))
    add("icSingleExc", usd(pr["singles_high"]["exceptions"]))
    add("icSingleAppr", usd(pr["singles_high"]["approval"]))
    add("icBestPair", usd(pr["best_value_high"]))
    add("icPairEA", usd(pr["pair_exc_appr_high"]))
    add("icPairEAloss", usd(-pr["pair_exc_appr_high"]))      # the pair's loss as a positive amount ("loses $X")
    add("icBestFirstIota", num(pr["best_first_pays_iota"], 3) if pr["best_first_pays_iota"] is not None else "n.a.")
    add("icIotaChainFeas", num(pr["iota_chain_feasible"], 2))
    add("icWeightyfive", usd(pr["W_by_iota"]["0.85"]))
    add("icWninetyfive", usd(pr["W_by_iota"]["0.95"]))
    add("icWbelowN", usd(pr["W_below_N"]))
    add("icWaboveN", usd(pr["W_above_N"]))
    add("icWdropN", usd(pr["W_below_N"] - pr["W_above_N"]) if (pr["W_below_N"] is not None and pr["W_above_N"] is not None) else "n.a.")
    add("icIotaStarN", num(pr["iota_star_above_N"], 3))
    add("icXiPshare", pct(P["Xi_share"], 1))
    add("icLp", usd(pr["L_p"]))
    add("icEtaMM", usd(P["h_MM"] * D["wage"]))
    add("icEtaAM", usd(P["h_AM"] * D["wage"]))
    add("icEtaAA", usd(P["h_AA0"] * D["wage"]))
    add("icDetWdone", usd(out["detection"]["W_at_d1"]))
    add("icDetWdoneRun", usd(out["detection"]["W_at_d1_run"]))
    add("icDetDWzero", num(out["detection"]["d_W_zero"], 3))
    # transition, case (a)
    add("icW", usd(T["W"]))
    add("icWbeforeRun", usd(T["W_before_run"]))
    add("icRunTotal", usd(an["total"]))
    add("icF", usd(T["F"]))
    add("icFbuild", usd(T["F_build"]))
    add("icFint", usd(T["F_int"]))
    add("icFother", usd(T["F_other"]))
    add("icIntCost", usd(P["int_cost_per_system"]))
    add("icIntLow", usd(inp["sensitivity"]["int_cost_per_system"]["low"]))
    add("icIntHigh", usd(inp["sensitivity"]["int_cost_per_system"]["high"]))
    add("icNsys", f"{P['n_systems']:g}")
    add("icCzero", usd(T["detail"]["C0"]))
    add("icCJ", usd(T["C_J"]))
    add("icCpar", usd(T["C_par"]))
    add("icCdup", usd(T["detail"]["C_dup"]))
    add("icCstr", usd(T["C_str"]))
    add("icCsurv", usd(T["C_surv"]))
    add("icOs", usd(T["O_s"]))
    add("icNsv", num(T["detail"]["N_sv"], 1))
    add("icExcessQuits", pct(P["survivor_excess_quits"], 2))
    add("icCrep", num(P["c_rep"], 2))
    add("icCwo", usd(T["C_wo"]))
    add("icVarpi", num(T["varpi_p"], 2))
    add("icBbar", num(T["bbar_p"], 2))
    add("icTdet", num(T["T_det"], 2))
    add("icLroll", usd(T["L_roll"]))
    add("icOmegaPar", pct(P["omega_par"]))
    add("icNuRec", pct(P["nu_rec"]))
    add("icTpar", num(R["T_par"], 2))
    add("icTparStar", num(R["T_par_star"], 2))
    add("icResid", pct(R["residual_risk"]))
    add("icNPV", usd(R["NPV"]))
    add("icNPVcertain", usd(R["NPV_certain"]))
    add("icNPVunlimited", usd(R["NPV_unlimited"]))
    add("icNPVvarpiOne", usd(R["NPV_varpi_one"]))
    add("icNPVthThree", usd(T["horizons"]["3"]))
    add("icNPVthFive", usd(T["horizons"]["5"]))
    add("icNPVthEngine", usd(T["horizons"][f"{float(P['T_h_engine']):g}"]))
    add("icNPVprogram", usd(T["horizons"]["program"]))
    add("icRebuilds", " and ".join(f"{x:g}" for x in T["horizons"]["rebuild_years"]))
    add("icFbreakeven", usd(R["F_breakeven"]))
    add("icNPVaLow", usd(cs["a"]["low"]["NPV"]))
    add("icNPVaDef", usd(cs["a"]["default"]["NPV"]))
    add("icNPVaHigh", usd(cs["a"]["high"]["NPV"]))
    add("icFintLow", usd(cs["a"]["low"]["F_int"]))
    add("icFintHigh", usd(cs["a"]["high"]["F_int"]))
    add("icNPVb", usd(cs["b"]["default"]["NPV"]))
    add("icNPVbCertain", usd(cs["b"]["default"]["NPV_certain"]))
    add("icFb", usd(TB["F"]))
    # score path
    sp = out["score_path"]
    add("icSPcashOne", num(-100 * sp["cash"][0], 2))
    add("icSPcashLater", num(-100 * sp["cash"][1], 2))
    add("icSPgaapOne", num(-100 * sp["gaap"][0], 2))
    add("icSPgaapLater", num(-100 * sp["gaap"][1], 2))
    # pilot
    pa, pb = out["pilot"]["a"], out["pilot"]["b"]
    add("icYs", usd(pa["Y_s"]))
    add("icYf", usd(pa["Y_f"]))
    add("icYsb", usd(pb["Y_s"]))
    add("icFpil", usd(pa["F_pil"]))
    add("icPilotShare", pct(P["pilot_cost_share"]))
    add("icPilotFixed", usd(P["pilot_fixed_cost"]))
    # run costs
    add("icDeltaM", pct(P["delta_M"]))
    add("icTup", num(P["T_up"], 2))
    add("icRevalShare", pct(P["reval_share"]))
    add("icVolFactor", num(an["volume_factor"], 2))
    add("icMaint", usd(an["maintenance"]))
    add("icReval", usd(an["revalidation"]))
    add("icTechDebt", usd(an["tech_debt"]))
    add("icNint", f"{an['N_int'] * 4:.0f}")
    add("icCcpl", usd(P["c_cpl"] * an["N_int"] ** 2))
    add("icCinc", usd(an["C_inc"]))
    add("icSecSpend", usd(an["security_spend"]))
    add("icSecResid", usd(an["residual"]))
    add("icWrunHigh", usd(an["W_high_after"]))
    add("icScope", usd(an["scope_500k"]))
    add("icCs", usd(P["C_s"]))
    # build or buy
    add("icBBfix", usd(bb["C_fix_build"]))
    add("icBBbuilds", usd(bb["builds_annual"]))
    add("icBBrun", usd(bb["run_annual"]))
    add("icBBpooled", usd(bb["pooled_per_unit"]))
    add("icBBint", usd(bb["F_int"]))
    add("icBBfixv", usd(bb["C_fix_buy"]))
    add("icBBcv", usd(bb["c_v_minus_pin"]))
    add("icBBv", _thou(round(bb["v_BB"], -3)))
    add("icBBvnorun", _thou(round(bb["v_BB_no_run"], -3)))
    add("icBBsave", usd(bb["buy_saving"]))
    add("icBBlock", usd(bb["lock_cap"]))
    add("icBBsw", usd(bb["C_sw"]))
    add("icBBmarkup", pct(bb["markup"]))
    # scaling
    add("icScalePer", usd(sc["per_process_fixed"]))
    add("icScaleFixed", usd(sc["understatement_fixed"]))
    add("icScaleJensen", usd(sc["jensen"]))
    add("icScalePool", usd(sc["pooling_gap"]))
    # capital
    add("icCapDc", usd(cap["dc"]))
    add("icCapDK", usd(cap["dK"]))
    add("icCapG", pct(cap["g"]))
    add("icCapValue", usd(-cap["value"]))
    add("icCapCash", usd(-cap["cash"]))
    add("icCapGaap", usd(-cap["gaap"]))
    add("icCapPin", usd(cap["pi_n_total"]))
    # failure taxonomy
    h, bi, au, ce = fa["hallucination"], fa["bias"], fa["autonomy"], fa["cerr"]
    add("icHalEo", pct(h["e_o"], 1))
    add("icHalEh", pct(h["e_h"], 2))
    add("icHret", pct(P["h_retrieval"]))
    add("icHalFloor", pct(h["floor"], 1))
    add("icHalFloorO", pct(h["floor_ordinary"], 1))
    add("icHalFloorDh", pct(h["floor_dh_06"], 1))
    add("icHalTol", pct(h["tolerance"]))
    add("icEpsd", num(bi["eps_d"], 1))
    add("icBiasPeak", pct(bi["peak"]))
    add("icBiasThr", pct(bi["irony_threshold"]))
    add("icBiasTop", pct(bi["caught_top"]))
    add("icBiasCentral", pct(bi["caught_central"]))
    add("icBiasUplift", pct(bi["uplift"] - 1))
    add("icAutL", usd(au["L"]))
    add("icAutLm", usd(au["L_m"]))
    add("icAutCap", usd(au["L_cap"]))
    add("icAlpha", num(P["alpha_tail"], 1))
    add("icAlphaLow", num(P["alpha_tail_low"], 2))
    add("icAutCmTwo", usd(au["c_m"][2], 3))
    add("icAutCmThree", usd(au["c_m"][3], 3))
    add("icAutHumOne", usd(au["human"][1]))
    add("icAutHumTwo", usd(au["human"][2]))
    add("icAutCvar", usd(au["cvar_uncapped"]))
    add("icAutCvarLow", usd(au["cvar_uncapped_low"]))
    add("icAutCvarQ", pct(au["cvar_q"]))
    add("icAutLmax", usd(au["L_max"]))
    add("icCerrFloor", usd(ce["floor_unit"]))
    add("icCerrMis", usd(ce["misbehavior_unit"], 3))
    add("icCerrAnnual", usd(ce["annual"]))
    add("icCerrNoRev", usd(ce["noreview_unit"]))
    add("icCerrNoRevAnnual", usd(ce["noreview_annual"]))
    return m


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        x = float(o)
        return None if not math.isfinite(x) else x
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def main():
    inp = load_inputs()
    out, ch = compute(inp)
    after = source_hashes()
    if after != inp["hashes"]:
        changed = [k for k in after if after[k] != inp["hashes"].get(k)]
        raise RuntimeError(f"input files changed during the run, nothing written; rerun: {changed}")
    mac = macros(out, inp)
    out["macros"] = dict(mac)
    with open(JSON_PATH, "w", encoding="utf-8") as fh:
        json.dump(_clean(out), fh, indent=1)
    names = [k for k, _ in mac]
    assert len(names) == len(set(names)), "duplicate macro names"
    assert all(k.isalpha() for k in names), "macro names must be letters only"
    with open(MACRO_PATH, "w", encoding="utf-8") as fh:
        fh.write("% Generated by code/examples/invoice_chain.py from data/examples/invoice_chain.yaml; do not edit.\n")
        fh.write("% Every number of the running example in part2/theory_core.tex is one of these macros.\n")
        for k, v in mac:
            fh.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")
    print(f"wrote {JSON_PATH.relative_to(ROOT)} and {MACRO_PATH.relative_to(ROOT)} ({len(mac)} macros)")


if __name__ == "__main__":
    main()
