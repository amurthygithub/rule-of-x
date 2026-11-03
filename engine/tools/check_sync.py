# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Change control (spec 19.1): fail when a theory or data note the engine implements has changed since the engine
was last brought in line with it.

    python tools/check_sync.py            report changed notes; exit 1 if any
    python tools/check_sync.py --accept   after re-checking the engine against the changed notes and recording the
                                          change in CHANGELOG.md, write the new hashes to src/autofrontier/NOTES_LOCK.json

tests/test_change_control.py runs the same check."""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE / "src"))
LOCK = ENGINE / "src" / "autofrontier" / "NOTES_LOCK.json"


def current() -> dict:
    from autofrontier.config import NOTES_FILES, REPO_DIR, sha256_file
    return {f: sha256_file(REPO_DIR / f) for f in NOTES_FILES}


def locked() -> dict:
    return json.loads(LOCK.read_text(encoding="utf-8")) if LOCK.is_file() else {"notes": {}}


def diff() -> list[str]:
    cur, lk = current(), locked().get("notes", {})
    out = []
    for f, h in cur.items():
        if f not in lk:
            out.append(f"{f}: not in the lock (new)")
        elif lk[f] != h:
            out.append(f"{f}: changed" if h else f"{f}: missing")
    return out


def accept() -> None:
    from autofrontier import __version__
    LOCK.write_text(json.dumps({"engine_version": __version__, "accepted": dt.date.today().isoformat(), "notes": current()},
                               indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {LOCK}")


def main(argv):
    if "--accept" in argv:
        accept()
        return 0
    d = diff()
    for line in d:
        print(line)
    if d:
        print("Re-check the engine against these notes, record the change in CHANGELOG.md, then run "
              "python tools/check_sync.py --accept")
    return 1 if d else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
