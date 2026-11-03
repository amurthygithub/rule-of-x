# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Command line.

    autofrontier --version
    autofrontier init <folder>                        write input templates (CSV, XLSX and a README per file)
    autofrontier run <input_folder> --out <folder> [--regime R] [--scenario S] [--seed N] [--set key=value ...] [--quick]
    autofrontier params [--grounding d]               list parameters with their grounding class and range
    autofrontier scenarios                            list the named scenarios
    autofrontier synthetic <folder> [--employees N] [--regime R] [--seed N]

Exit codes: 0 success; 2 usage or parameter error; 3 input validation error; 4 runtime or solver error;
5 refused output path. The engine runs locally with no network calls and no telemetry, and writes only to the
chosen output folder (it also turns off Python's bytecode cache so nothing is written next to the code)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

EXIT_OK, EXIT_USAGE, EXIT_INPUT, EXIT_RUNTIME, EXIT_PATH = 0, 2, 3, 4, 5


def _parser() -> argparse.ArgumentParser:
    from . import __version__
    ap = argparse.ArgumentParser(prog="autofrontier", description="AI transformation vision, roadmap and people plan from firm data.")
    ap.add_argument("--version", action="store_true", help="print the version and the Required Notice")
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("init", help="write input templates to a folder")
    a.add_argument("folder")
    r = sub.add_parser("run", help="run the engine on an input folder")
    r.add_argument("input_folder")
    r.add_argument("--out", required=True, help="output folder (created if needed); nothing is written anywhere else")
    r.add_argument("--regime", choices=["public", "private_family", "pe", "vc", "hybrid", "permanent_capital"], default=None)
    r.add_argument("--scenario", default=None, help="a named scenario; see `autofrontier scenarios`")
    r.add_argument("--seed", type=int, default=None)
    r.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="override a parameter, e.g. finance.r=0.09")
    r.add_argument("--data", default=None, help="folder with params.yaml and priors (default: AUTOFRONTIER_DATA or the repository)")
    r.add_argument("--quick", action="store_true", help="fewer scenarios and draws, no global sensitivity (for a first look)")
    r.add_argument("--quiet", action="store_true")
    pp = sub.add_parser("params", help="list parameters")
    pp.add_argument("--grounding", default=None, help="a, b, c, d, setting or policy")
    pp.add_argument("--data", default=None)
    sub.add_parser("scenarios", help="list the named scenarios")
    sy = sub.add_parser("synthetic", help="write a synthetic firm's input files (fictional)")
    sy.add_argument("folder")
    sy.add_argument("--employees", type=int, default=3200)
    sy.add_argument("--regime", default="public")
    sy.add_argument("--seed", type=int, default=0)
    sy.add_argument("--data", default=None)
    ap.epilog = f"autofrontier {__version__}"
    return ap


def main(argv=None) -> int:
    sys.dont_write_bytecode = True
    from . import REQUIRED_NOTICE, __version__
    ap = _parser()
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return EXIT_USAGE if e.code not in (0, None) else EXIT_OK
    if args.version:
        print(f"autofrontier {__version__}")
        print(REQUIRED_NOTICE)
        return EXIT_OK
    if args.cmd is None:
        ap.print_help()
        return EXIT_USAGE
    from .config import ConfigError
    from .ingest import InputError
    from .safeio import UnsafePathError
    try:
        if args.cmd == "init":
            from .schema import write_templates
            written = write_templates(args.folder)
            print(f"wrote {len(written)} files to {args.folder}; start with README.md")
            return EXIT_OK
        if args.cmd == "scenarios":
            from .config import load_params
            from .scenarios import scenario_set

            class _F:
                base_year = 2027
            for k, v in scenario_set(load_params(), _F()).items():
                print(f"{k:22s} {v['desc']}")
            return EXIT_OK
        if args.cmd == "params":
            from .config import find_data_dir, load_params
            p = load_params(Path(args.data) if args.data else find_data_dir())
            for row in p.table():
                if args.grounding and row["grounding"] != args.grounding:
                    continue
                print(f"{row['key']:45s} {str(row['value'])[:24]:24s} {str(row['range'])[:28]:28s} {row['grounding']}")
            return EXIT_OK
        if args.cmd == "synthetic":
            from .synthetic import generate
            out = generate(args.folder, employees=args.employees, seed=args.seed, regime=args.regime, data_dir=args.data)
            print(f"wrote {len(out['files'])} input files for a fictional firm of {out['fte']:,.0f} FTE to {args.folder}")
            return EXIT_OK
        if args.cmd == "run":
            inp, out = Path(args.input_folder).resolve(), Path(args.out).expanduser().resolve()
            if not inp.is_dir():
                print(f"error: input folder {inp} does not exist", file=sys.stderr)
                return EXIT_USAGE
            if out == inp or inp in out.parents:
                print("error: choose an output folder outside the input folder, so inputs are never overwritten", file=sys.stderr)
                return EXIT_PATH
            from .pipeline import run
            res = run(inp, out, regime=args.regime, scenario=args.scenario, seed=args.seed, overrides=args.set, data_dir=args.data,
                      quick=args.quick, echo=None if args.quiet else (lambda m: print(m, file=sys.stderr)))
            print(f"report written to {out} (report.md, report.json and CSV tables) in {res['seconds_wall']:.0f} s")
            print(REQUIRED_NOTICE)
            return EXIT_OK
    except InputError as e:
        print(f"input error: {e}", file=sys.stderr)
        return EXIT_INPUT
    except ConfigError as e:
        print(f"parameter error: {e}", file=sys.stderr)
        return EXIT_USAGE
    except UnsafePathError as e:
        print(f"refused: {e}", file=sys.stderr)
        return EXIT_PATH
    except (RuntimeError, ArithmeticError, ValueError) as e:
        print(f"runtime error: {type(e).__name__}: {e}", file=sys.stderr)
        return EXIT_RUNTIME
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
