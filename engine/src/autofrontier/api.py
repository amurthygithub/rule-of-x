# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Any other commercial use requires prior written permission from the copyright holder.
"""Public API for programs that call the engine (for example an archetype runner). These names are stable within a
minor version; everything else in the package may change.

    from autofrontier import api
    res = api.run("my_firm", out_folder=None, regime="permanent_capital", quick=True)
    book = api.playbook(res)              # {"activities", "steps", "dictionary", "summary", "task_map", ...}
    levers = api.lever_map(res)           # per regime: lever values, thresholds, binding constraint, excluded levers
    api.write_playbook(res, "out")        # playbook_steps.csv and playbook_activities.csv only
    api.synthetic_firm("demo", employees=3200, seed=0)

The engine runs locally, makes no network calls and writes only to the folders named here."""
from __future__ import annotations

from pathlib import Path

from . import REQUIRED_NOTICE, __version__, pipeline, regimes, synthetic
from .safeio import OutputDir

REGIMES = regimes.REGIMES


def run(input_folder, out_folder=None, regime: str | None = None, scenario: str | None = None, overrides: list[str] | None = None,
        seed: int | None = None, quick: bool = False, data_dir=None, n_imp: int | None = None, n_out: int | None = None,
        scenario_list: list[str] | None = None) -> dict:
    """Run the engine on an input folder. With out_folder, the full report is written there; without it nothing is
    written. Returns the result dict (keys include plan, waves, playbook, regimes, regimes_extra, mc, people)."""
    return pipeline.run(input_folder, out_folder, regime=regime, scenario=scenario, seed=seed, overrides=overrides,
                        data_dir=data_dir, quick=quick, write=out_folder is not None, n_imp=n_imp, n_out=n_out,
                        scenario_list=scenario_list)


def playbook(result: dict) -> dict:
    """The playbook of a run: per process step and per DWA activity (roadmap.playbook)."""
    return result["playbook"]


def write_playbook(result: dict, folder) -> list[str]:
    """Write playbook_steps.csv, playbook_activities.csv and playbook_data_dictionary.csv to folder (created if needed)
    and return their paths."""
    out = OutputDir(folder)
    bk = result["playbook"]
    names = ["playbook_steps.csv", "playbook_activities.csv", "playbook_data_dictionary.csv"]
    out.write_csv(names[0], bk["steps"])
    out.write_csv(names[1], bk["activities"])
    out.write_csv(names[2], bk["dictionary"])
    if bk.get("task_map") is not None and len(bk["task_map"]):
        names.append("firm_tasks_mapping.csv")
        out.write_csv(names[-1], bk["task_map"])
    return [str(Path(folder) / n) for n in names]


def lever_map(result: dict) -> dict:
    """The lever map of a run (levers.lever_map): lever values, switch thresholds with distances, the binding
    constraint and the excluded levers, per regime."""
    return result["lever_map"]


def synthetic_firm(folder, employees: int = 3200, seed: int = 0, **kw) -> dict:
    """Write a fictional firm's input files to folder (keywords as synthetic.generate: regime, tiers, products)."""
    return synthetic.generate(folder, employees=employees, seed=seed, **kw)


def version() -> dict:
    return {"version": __version__, "notice": REQUIRED_NOTICE}
