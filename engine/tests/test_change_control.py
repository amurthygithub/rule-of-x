# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Change control (spec 19.1): the notes the engine implements match the hashes the engine was last checked
against (src/autofrontier/NOTES_LOCK.json), and the change log and issue list exist."""
import importlib.util
import re
from pathlib import Path

from autofrontier import __version__

ENGINE = Path(__file__).resolve().parents[1]


def test_notes_unchanged_since_engine_update():
    spec = importlib.util.spec_from_file_location("check_sync", ENGINE / "tools" / "check_sync.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    d = mod.diff()
    assert not d, ("notes changed without an engine update: " + "; ".join(d)
                   + ". Re-check the engine, record it in CHANGELOG.md, then run python tools/check_sync.py --accept")


def test_changelog_and_issues():
    log = (ENGINE / "CHANGELOG.md").read_text(encoding="utf-8")
    assert re.search(rf"^## {re.escape(__version__)}\b", log, re.M), "CHANGELOG.md has no entry for the current version"
    assert (ENGINE / "QA" / "ISSUES.md").is_file()
    assert (ENGINE / "MODEL_RISK.md").is_file()
