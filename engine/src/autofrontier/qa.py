# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Quality assurance helpers shared by the tests and tools (spec 19.1): the golden firms and run settings, the
snapshot of a run that golden tests compare, and the comparison itself."""
from __future__ import annotations

import math
from pathlib import Path

GOLDEN_FIRMS = {
    "synthetic": dict(employees=3200, seed=0),
    "small": dict(employees=250, seed=1, tiers=(0, 2), products=False),
    "pe": dict(employees=1800, seed=2, regime="pe"),
}
GOLDEN_RUN = dict(quick=True, n_imp=6, n_out=60, scenario_list=["central", "capability_slow"], seed=20261029)


def snapshot(res: dict) -> dict:
    """The numbers a golden test pins: the plan, its value, the risk quantiles, the score path and the people totals."""
    mc = res["mc"]
    plan = res["plan"]
    pr = res["product"]["lines"]
    return {
        "regime": res["regime"],
        "processes": sorted(map(str, plan.process_id)) if len(plan) else [],
        "plan_value": float(res["solution"]["value"]),
        "value_P10": float(mc["value"]["P10"]), "value_P50": float(mc["value"]["P50"]), "value_P90": float(mc["value"]["P90"]),
        "r40_cash_final": float(res["score_path"]["r40_cash"][-1]),
        "fte_after": float(res["people"]["residual"]["totals"]["fte_after"]),
        "regime_values": {k: float(v["value"]) for k, v in res["regimes"].items()},
        "seat_revenue_at_risk_central": float(pr[0]["seats"]["revenue_at_risk_full"]["central"]) if pr else 0.0,
        "universe_economical_share": float(res["universe_year3"]["shares"]["economical"]),
    }


def compare(new: dict, old: dict, rel: float = 1e-6) -> list[str]:
    """Differences between two snapshots (empty if they agree)."""
    out = []
    for k in sorted(set(new) | set(old)):
        a, b = new.get(k), old.get(k)
        if isinstance(a, dict) and isinstance(b, dict):
            out += [f"{k}.{d}" for d in compare(a, b, rel)]
        elif isinstance(a, float) and isinstance(b, (int, float)):
            if not math.isclose(a, float(b), rel_tol=rel, abs_tol=1e-6):
                out.append(f"{k}: {b} -> {a}")
        elif a != b:
            out.append(f"{k}: {b} -> {a}")
    return out


def golden_path(name: str) -> Path:
    return Path(__file__).resolve().parents[2] / "tests" / "golden" / f"{name}.json"
