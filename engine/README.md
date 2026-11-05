# autofrontier

The engine of the third paper in this series (formerly Part III of "The Efficient Frontier of Growth and Profitability"); Paper 1 is "The Rule of 40 as a Price Line" and Paper 2 "The Economics of AI Transformation". It takes a firm's financial and
organizational data and returns an AI transformation vision, a phased roadmap and a people plan, scored with Part
I's Rule-of-X frontier. The report is decision support, not a decision (see MODEL_RISK.md).

The engine runs locally. It makes no network calls, sends no telemetry and writes only to the output folder you
name.

## Install

    pip install -e .            # Python 3.11 or later; numpy, pandas, scipy, pydantic, pyyaml, openpyxl, pulp

## Use

    autofrontier init my_firm                      # input templates (CSV, XLSX) with a README per file
    autofrontier run my_firm --out my_report       # report.md, report.json and CSV tables
    autofrontier run my_firm --out r2 --regime pe --scenario capability_slow --set finance.r=0.09
    autofrontier params --grounding d              # every scenario parameter with its range
    autofrontier scenarios                         # the named scenarios
    autofrontier synthetic demo --employees 3200   # a fictional firm's input files
    autofrontier --version                         # version and the Required Notice

From Python (the public API; other modules may change):

    from autofrontier import api
    res = api.run("my_firm", quick=True)           # nothing is written without out_folder
    book = api.playbook(res)                       # activities (decisions), steps (execution), dictionary, summary
    levers = api.lever_map(res)                    # lever values, switch thresholds, binding constraint, excluded levers
    api.write_playbook(res, "my_playbook")         # playbook_steps.csv, playbook_activities.csv, playbook_data_dictionary.csv

Exit codes: 0 success; 2 usage or parameter error; 3 input validation error (the message says what to fix);
4 runtime error; 5 refused output path (for example an output folder inside the input folder).

Inputs come in tiers. Tier 0 (financial statements and headcount) is enough for a first run with wide ranges;
Tier 1 (operating cost by cost center), Tier 2 (roster), Tier 3 (systems, volumes, organization, jurisdictions,
products, security, ownership) and Tier 4 (time studies) narrow them. The value-of-information table in the report
says which tier pays most for your firm.

## What the engine computes

- Mode choice for each unit of work (human, outsourced, augmented, automated, eliminated) with review, detection,
  failure modes and reliability (theory_core, Sections 4.1 to 4.13).
- Plans by process, readiness level, start year and pilot, optimized under budget, change capacity, decision
  bandwidth, security review capacity and covenants for the firm's ownership regime: public, private or family,
  PE, VC, dual class, or permanent capital (theory_ext, theory_regimes, theory_acquirer), with the limits to buying
  growth (each off at its neutral value until a scenario sets it).
- Scenarios, minimax regret, Monte Carlo over data and class b and d parameters, Morris then Sobol sensitivity.
- An executable playbook: decisions per O*NET detailed work activity, executed per process step, with the mode now
  and at target readiness, the binding constraint, preconditions, gates, wave, roles and FTE, KPIs, controls,
  evidence keys with grounding classes and O*NET task statements, a confidence tier and the distance to each switch
  threshold (spec 29); the firm's own task list (tier3_tasks) and acceptance values (tier3_policy) override the
  defaults. The lever map ranks levers by position and setup for every ownership regime (spec 28), with growth
  spend on Paper 1's central basis, S&M above a maintenance base of 25.7 percent of revenue (finance.sm_basis =
  netted), and all S&M and no S&M as bounds stated in the report.
- Product strategy (theory_product), accounting path (prop:acct-path), labor law, talent and jurisdiction
  (theory_labor), competition (should versus could), ICFR scope and controls (spec 25).

## Layout

    src/autofrontier/   the package: formulas.py (every formula, with its paper label), config.py and defaults.yaml
                        (parameters, linked to data/tasks/params.yaml), ingest, impute, economics, plans, optimize,
                        regimes, scenarios, risk, roadmap, playbook, levers, product, people, labor, industry, security,
                        report, cli, api (the public API)
    tests/              unit, cross-implementation, property, regression, paper-sync, privacy, validation, golden
    tools/              traceability.py, accept_golden.py, check_sync.py, sync_icfr_priors.py, sync_gap_bands.py
    examples/           synthetic_run/: the synthetic firm's inputs and full report
    TRACEABILITY.md     formulas and parameters with labels, sources and grounding classes (generated)
    MODEL_RISK.md       intended use, limits, validation, monitoring, change control, human decision rights
    CHANGELOG.md, QA/ISSUES.md

## Tests

    pytest -m "not slow"        # about two minutes
    pytest                      # includes the end-to-end and golden runs

Intended changes to the golden numbers: `python tools/accept_golden.py`, with a CHANGELOG entry. Notes that change
without an engine update fail tests/test_change_control.py; after re-checking the engine, run
`python tools/check_sync.py --accept`. After editing formulas.py or defaults.yaml run `python tools/traceability.py`.

## Authorship and declarations

The author directed the research and made its decisions; AI agents drafted the text, code and proofs.

Funding: the author received no funding for this work. Competing interests: the author declares no competing interests.

## License

PolyForm Noncommercial License 1.0.0 (LICENSE.md) or, at your option, the PolyForm Internal Use License 1.0.0 (LICENSE-INTERNAL-USE.md), which lets a company run and modify the engine for its own internal business operations but not distribute it or offer it as a service; see NOTICE.md for the Required Notice and third-party data. The
report uses O*NET 31.0 (USDOL/ETA, CC BY 4.0), modified by the author. METR run-level data is not distributed; only
fitted parameters are used, with citation.
