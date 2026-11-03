# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Accept intended changes to the golden snapshots (spec 19.1).

Run from engine/:   python tools/accept_golden.py            (all three firms)
                    python tools/accept_golden.py small pe   (some of them)

It regenerates the synthetic, small and PE-owned firms, runs the engine with the golden settings and rewrites
tests/golden/<name>.json. Commit the new files with a CHANGELOG entry that says why the numbers changed."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from autofrontier import pipeline, synthetic  # noqa: E402
from autofrontier.qa import GOLDEN_FIRMS, GOLDEN_RUN, golden_path, snapshot  # noqa: E402


def main(names):
    names = names or list(GOLDEN_FIRMS)
    with tempfile.TemporaryDirectory() as tmp:
        for nm in names:
            folder = Path(tmp) / nm
            synthetic.generate(folder, **GOLDEN_FIRMS[nm])
            res = pipeline.run(folder, None, write=False, **GOLDEN_RUN)
            out = golden_path(nm)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(snapshot(res), indent=1, sort_keys=True) + "\n", encoding="utf-8")
            print(f"accepted {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
