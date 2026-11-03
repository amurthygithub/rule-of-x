#!/usr/bin/env bash
# Regenerate all three papers from one parameter set (params commit of 29 Oct 2026; notes/integration_todo.md "Freeze
# regeneration order", corrected for the dependencies listed below).
#
#   P1  The Rule of 40 as a Price Line            sections/, paper1/        (code/*.py)
#   P2  The Economics of AI Transformation        part2/                    (code/examples, code/verify_part2_*.py)
#   P3  the autofrontier engine                   engine/, code/playbook/
#
# Usage:  bash code/regenerate_all.sh [--from STAGE] [--to STAGE] [--keep-going] [--list]
#   --from STAGE   start at STAGE (earlier stages are assumed done)
#   --to STAGE     stop after STAGE
#   --keep-going   a failing check stage (verify scripts, engine tests) is recorded and the build continues; a failing
#                  generation stage always stops the build. Without it the first failure stops the build.
#   --list         print the stages and exit
# Every stage writes build_logs/<NN>_<stage>.log (sub-steps build_logs/<NN>_<stage>__<script>.log) and a line to
# build_logs/summary.txt. The repository root is the parent of this script's folder, so the script also runs in a
# scratch copy of the repository (PAPER_ROOT is exported for code/data_part2, whose scripts default to
# /home/claude/paper).
#
# Order and why it differs from the to-do list (engine defaults -> params -> invoice_chain.py -> make_labor_macros.py ->
# verify scripts -> backtest.py -> calibrate_horizons.py -> estimate_organic.py -> paper1_macros.py -> run_archetypes.py):
#   * estimate_organic.py writes notes/calibration_anchor_E2.json, which calibrate_horizons.py read until revision v2
#     (referee 3, R3-17; it now reads notes/calibration_anchor_v3.json), so it runs first. It checks its E1 anchor, on
#     the v2 sample, only against a record on the same sample: notes/calibration_results.json if its anchor is on that
#     sample, else the v2 anchor of notes/empirics_v2_exact.json (estimate_v3.py with V3_PANEL=v2). With neither (a
#     first run) it skips the check and says so in the anchor file ("passed": null); stage calibrate then reruns it.
#   * verify_part2_acquirer.py writes part2/tables/acquirer_macros.tex, which verify_part2_regimes.py reads, and
#     sections/tables/acquired_macros.tex, which paper1_macros.py and paper1.tex read: acquirer runs first.
#   * verify_part2_labor.py reads invoice_macros.tex and labor_macros.tex: after invoice_chain.py and make_labor_macros.py.
#   * verify_theory.py reads notes/calibration_results.json: after calibrate_horizons.py.
#   * stage stress_report (round 3) runs code/mc_report_tex.py, which formats the committed output of the joint-parameter
#     stress test (notes/mc_results_2026-11-03/mc_claims.json, draws_lhs.csv) into sections/tables/tab_stress.tex,
#     paper1/stress_macros.tex and figures/fig_stress.pdf. It does not re-run the Monte Carlo (about a minute on four
#     cores; command in code/REPLICATION_README.md). It runs after calibrate so the table sits beside the calibration's
#     tables, and before paper1_macros.py, which inputs stress_macros.tex from paper1/macros.tex.
#   * verify_part2_playbook.py reads notes/playbook_results.json and part2/tables/playbook_macros.tex, both written by
#     run_archetypes.py: after it.
#   * backtest.py and run_archetypes.py read data/panel_v2_all.csv (and run_archetypes data/panel.csv), and the P1
#     estimates read the panels: the panel and empirics stages (the sample audit's scripts) run before them.
#   * paper1_macros.py reads notes/{calibration_results,paper_stats,empirics_revised,gap_decomposition,
#     empirics_organic}.json, notes/calibration_anchor_v3.json, data/panel*.csv and sections/tables/acquired_macros.tex.
#   * estimate_v3.py (stage empirics_v3) runs after build_panel_v3.py and estimate_organic.py (it reads
#     notes/empirics_organic.json) and before calibrate_horizons.py, which is to read its anchor file
#     notes/calibration_anchor_v3.json and notes/frontier_slope_v3.json (Paper 1 revision v2). Its v2 run
#     (V3_PANEL=v2, notes/empirics_v2_exact.json) comes first, because the v3 notes compare against it
#     (code/REPLICATION_README.md). paper1_macros.py also reads notes/{empirics_v3,frontier_slope_v3,empirics_v2_exact,
#     panel_v3_build}.json and data/panel_v3.csv, and writes the Paper 1 copies of the v3 tables.
#   * The engine tests read code/verify_part2_*.py, data/examples/invoice_chain.{yaml,json}, code/calibrate_horizons.py
#     and code/paper1_macros.py, so they run after the generators.
#   * The LaTeX builds come last. Paper 2 has no main file yet (notes/cross_paper_impacts.md: "P2 main file ... open
#     (assembly)"); set P2_MAIN=part2/<file>.tex once it exists. Without it the stage fails with that message.
# Environment passed through: ORGANIC_PANEL (v2 | v3; estimate_organic.py), ORGANIC_FAST, V3_FAST, V3_JOBS.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
export PYTHONHASHSEED=0
export PYTHONDONTWRITEBYTECODE=1
export PAPER_ROOT="$ROOT"
export MPLBACKEND=Agg
PY="${PYTHON:-python3}"
LOGDIR="$ROOT/build_logs"

STAGES=(engine_defaults params invoice_chain labor_macros verify_part2 panel empirics empirics_v3 backtest calibrate
        stress_report verify_theory paper1_macros playbook verify_playbook engine_tests latex_p1 latex_p2)

FROM="" TO="" KEEP_GOING=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --from) FROM="$2"; shift 2 ;;
    --to) TO="$2"; shift 2 ;;
    --keep-going) KEEP_GOING=1; shift ;;
    --list) printf '%s\n' "${STAGES[@]}"; exit 0 ;;
    -h|--help) sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "unknown option $1 (see --help)" >&2; exit 2 ;;
  esac
done
valid() { local s; for s in "${STAGES[@]}"; do [[ "$s" == "$1" ]] && return 0; done; return 1; }
[[ -z "$FROM" ]] || valid "$FROM" || { echo "unknown stage '$FROM'; stages: ${STAGES[*]}" >&2; exit 2; }
[[ -z "$TO" ]] || valid "$TO" || { echo "unknown stage '$TO'; stages: ${STAGES[*]}" >&2; exit 2; }

mkdir -p "$LOGDIR"
SUMMARY="$LOGDIR/summary.txt"
FAILED_CHECKS=()
{ echo "regenerate_all.sh started $(date -u +%Y-%m-%dT%H:%M:%SZ) in $ROOT (from=${FROM:-start}, to=${TO:-end}, keep_going=$KEEP_GOING)"
  echo "engine defaults sha256 $(sha256sum "$ROOT/engine/src/autofrontier/defaults.yaml" | cut -c1-16)," \
       "params.yaml $(sha256sum "$ROOT/data/tasks/params.yaml" | cut -c1-16)," \
       "params_reliability.yaml $(sha256sum "$ROOT/data/tasks/params_reliability.yaml" | cut -c1-16)"; } >> "$SUMMARY"

N=0 CUR="" STAGE_LOG=""
# run LABEL KIND CMD...: KIND is gen (failure stops the build) or check (failure stops it unless --keep-going)
run() {
  local label="$1" kind="$2"; shift 2
  local log="$LOGDIR/$(printf '%02d' "$N")_${CUR}__${label}.log" t0=$SECONDS rc=0
  echo "[$CUR] $label: $*" | tee -a "$STAGE_LOG"
  ( cd "$ROOT" && "$@" ) > "$log" 2>&1 || rc=$?
  local msg="[$CUR] $label: exit $rc after $((SECONDS - t0)) s (log $(basename "$log"))"
  echo "$msg" | tee -a "$STAGE_LOG" >> "$SUMMARY"
  if [[ $rc -ne 0 ]]; then
    tail -n 25 "$log" | sed 's/^/    | /' >> "$STAGE_LOG"
    if [[ "$kind" == check && $KEEP_GOING -eq 1 ]]; then
      FAILED_CHECKS+=("$CUR/$label"); echo "    (check failed; continuing because of --keep-going)" | tee -a "$STAGE_LOG"
    else
      echo "STOPPED at stage $CUR, step $label (exit $rc). See $log" | tee -a "$SUMMARY" >&2
      exit "$rc"
    fi
  fi
}

latex() {   # latex MAIN.tex OUTNAME DEST.pdf: pdflatex, bibtex, pdflatex twice in a private scratch folder
  local main="$1" name="$2" dest="$3" out
  out="$(mktemp -d "${TMPDIR:-/tmp}/regen_${name}_XXXXXX")"
  export TEXINPUTS="$ROOT:" BIBINPUTS="$ROOT:$ROOT/paper1:$ROOT/part2:"
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$out" -jobname="$name" "$main"
  ( cd "$out" && bibtex "$name" )
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$out" -jobname="$name" "$main"
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$out" -jobname="$name" "$main"
  local extra=0   # page numbers can still move after the third pass: at most two more passes
  while [ "$extra" -lt 2 ] && grep -q "Rerun to get cross-references right" "$out/$name.log"; do
    pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$out" -jobname="$name" "$main"
    extra=$((extra + 1))
  done
  grep -E "Warning: (Citation|Reference).*undefined" "$out/$name.log" | sort -u | head -40 || true
  cp "$out/$name.pdf" "$dest"
  echo "wrote $dest (build folder $out)"
}

stage_engine_defaults() {
  run load_params gen "$PY" -c "import sys; sys.path.insert(0, 'engine/src'); from autofrontier import config; \
p = config.load_params(); bad = [l for l in p.params_log if l['status'].startswith('missing')]; \
print(len(p.keys()), 'parameters,', len(p.params_log), 'linked'); assert not bad, bad"
  run traceability gen bash -c "cd engine && $PY tools/traceability.py"
  run notes_lock check bash -c "cd engine && $PY tools/check_sync.py"
}
stage_params() {
  run 08_params gen "$PY" -I code/data_part2/08_params.py
  run 10_validate check "$PY" -I code/data_part2/10_validate.py
}
stage_invoice_chain() { run invoice_chain gen "$PY" code/examples/invoice_chain.py; }
stage_labor_macros() { run make_labor_macros gen "$PY" code/make_labor_macros.py; }
stage_verify_part2() {
  local s
  for s in accounting acquirer regimes core ext labor product competition; do
    run "verify_part2_$s" check "$PY" "code/verify_part2_$s.py"
  done
}
stage_panel() {
  run build_panel_v2 gen "$PY" code/build_panel_v2.py
  run build_panel_v3 gen "$PY" code/build_panel_v3.py
}
stage_empirics() {
  run estimate_frontier gen "$PY" code/estimate_frontier.py
  run estimate_revised gen "$PY" code/estimate_revised.py
  run decompose_gap gen "$PY" code/decompose_gap.py
  run paper_stats gen "$PY" code/paper_stats.py
  run estimate_organic gen "$PY" code/estimate_organic.py
}
stage_backtest() { run backtest gen "$PY" code/validation/backtest.py; }
stage_calibrate() {
  run calibrate_horizons gen "$PY" code/calibrate_horizons.py
  if grep -q '"passed": null' "$ROOT/notes/calibration_anchor_E2.json" 2>/dev/null; then   # first run: do the E1 check now
    run estimate_organic_recheck gen "$PY" code/estimate_organic.py
  fi
}
stage_empirics_v3() {
  run estimate_v3_on_v2 gen env V3_PANEL=v2 "$PY" code/estimate_v3.py
  run estimate_v3 gen "$PY" code/estimate_v3.py
}
stage_stress_report() { run mc_report_tex gen "$PY" code/mc_report_tex.py; }   # reads the committed MC outputs only
stage_verify_theory() {
  run verify_theory check bash -c "$PY code/verify_theory.py > notes/verify_theory_output.txt 2>&1; rc=\$?; \
tail -n 5 notes/verify_theory_output.txt; exit \$rc"
}
stage_paper1_macros() { run paper1_macros gen "$PY" code/paper1_macros.py; }
stage_playbook() { run run_archetypes gen "$PY" code/playbook/run_archetypes.py; }
stage_verify_playbook() { run verify_part2_playbook check "$PY" code/verify_part2_playbook.py; }
stage_engine_tests() { run pytest check bash -c "cd engine && $PY -m pytest -q -p no:cacheprovider -rf"; }
stage_latex_p1() { run paper1 gen bash code/build_paper1.sh; }   # main paper and Supplementary Appendix (two PDFs, xr-hyper)
stage_latex_p2() {
  local main="${P2_MAIN:-}"
  if [[ -z "$main" ]]; then
    main="$(cd "$ROOT" && grep -l '\\documentclass' part2/*.tex 2>/dev/null | head -n 1 || true)"
  fi
  if [[ -z "$main" || ! -f "$ROOT/$main" ]]; then
    run paper2_main gen bash -c "echo 'no Paper 2 main file: part2/ has no \\documentclass file and P2_MAIN is not set' \
'(notes/cross_paper_impacts.md: P2 main file needs longtable, the two playbook inputs and validation_backtest.tex; open, assembly)'; exit 3"
  fi
  run paper2 gen latex "$main" paper2 "$ROOT/part2/$(basename "${main%.tex}").pdf"
}

started=0
[[ -z "$FROM" ]] && started=1
for s in "${STAGES[@]}"; do
  [[ "$s" == "$FROM" ]] && started=1
  N=$((N + 1))
  if [[ $started -eq 1 ]]; then
    CUR="$s"; STAGE_LOG="$LOGDIR/$(printf '%02d' "$N")_${s}.log"; : > "$STAGE_LOG"
    echo "== $(printf '%02d' "$N") $s" | tee -a "$SUMMARY"
    "stage_$s"
  fi
  [[ -n "$TO" && "$s" == "$TO" ]] && break
done
if [[ ${#FAILED_CHECKS[@]} -gt 0 ]]; then
  echo "finished with failing checks: ${FAILED_CHECKS[*]}" | tee -a "$SUMMARY"
  exit 1
fi
echo "finished $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$SUMMARY"
