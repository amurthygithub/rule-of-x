# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Rate conventions (spec 18; notes/theory_regimes_notes.md): the engine discounts in continuous time, every rate
parameter is tagged annual or continuous, and annual sources are converted once at load with to_continuous()."""
import math
import re

import pytest

from autofrontier import config

DISCOUNT = re.compile(r"(^r$|_r$|^r_|irr|wacc|discount|debt_rate|interest|cost_of_capital|hurdle)")


def test_every_rate_is_tagged(params):
    untagged = []
    for k in params.keys():
        name = k.split(".", 1)[1]
        m = params.meta(k)
        if DISCOUNT.search(name) and isinstance(m.get("value"), (int, float)) and not name.startswith(("r_A", "r_U", "r_bar", "eta_")):
            if m.get("rate") not in ("annual", "continuous"):
                untagged.append(k)
        if "rate" in m:
            assert m["rate"] in ("annual", "continuous"), f"{k}: rate tag {m['rate']}"
    assert not untagged, f"rate parameters without an annual/continuous tag: {untagged}"


def test_to_continuous_applied_once(params):
    for k in params.keys():
        m = params.meta(k)
        if m.get("transform") == "to_continuous":
            assert m.get("rate") == "continuous", k
            lo, hi = m["range"]
            assert lo <= m["value"] <= hi and m["value"] < 1.0


def test_finance_r_is_continuous_wacc(params):
    assert params.finance.r == pytest.approx(math.log1p(0.0934), abs=2e-4)
    lo, hi = params.range("finance.r")
    assert lo == pytest.approx(0.0677, abs=1e-3) and hi == pytest.approx(0.1013, abs=1e-3)
    assert "continuous" in str(params.meta("finance.r").get("basis", "")) or params.meta("finance.r").get("rate") == "continuous"


def test_tau_documented():
    """tau is the marginal statutory rate (0.21); Part I's ceiling uses an average effective rate (0.18)."""
    p = config.load_params()
    assert p.finance.tau == 0.21
    assert "average effective" in str(p.meta("finance.tau").get("note", ""))
