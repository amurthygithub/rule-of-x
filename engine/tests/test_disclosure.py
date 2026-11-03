# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Publication rules (spec 26): one vendor is never named in the engine or its outputs, and vendor price examples
come only from the four vendors the spec allows (Freshworks, Intercom, Salesforce, HubSpot)."""
from pathlib import Path

from autofrontier import config
from autofrontier.product import PRICE_VENDORS, vendor_price_range

ENGINE = Path(__file__).resolve().parents[1]
NAME = "zen" + "desk"


def test_name_absent_from_engine_files():
    hits = []
    for f in list((ENGINE / "src").rglob("*")) + list((ENGINE / "tools").rglob("*.py")) + [ENGINE / "TRACEABILITY.md"]:
        if f.is_file() and f.suffix in (".py", ".yaml", ".csv", ".md", ".json") and "__pycache__" not in f.parts:
            if NAME in f.read_text(encoding="utf-8", errors="ignore").lower():
                hits.append(str(f.relative_to(ENGINE)))
    assert not hits, hits


def test_name_absent_from_parameter_text(params):
    bad = [r["key"] for r in params.table() if NAME in (str(r["source"]) + str(r.get("note", "")) + str(r.get("section", ""))).lower()]
    assert not bad, bad


def test_vendor_prices_from_allowed_vendors_only():
    vp = vendor_price_range(config.find_data_dir())
    assert all(any(k.startswith(v) for v in PRICE_VENDORS) for k in vp["prices"])
    if vp["prices"]:
        assert vp["low"] == 0.5 and vp["high"] == 2.0
        assert not any("session" in k for k in vp["prices"])       # a session is not a resolution


def test_allowed_vendors_match_spec_26():
    assert set(PRICE_VENDORS) == {"freshworks", "intercom", "salesforce", "hubspot"}


def test_name_absent_from_outputs(golden_run):
    res, out = golden_run("synthetic")
    for f in out.rglob("*"):
        if f.is_file():
            assert NAME not in f.read_text(encoding="utf-8", errors="ignore").lower(), f.name
