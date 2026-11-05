#!/usr/bin/env bash
# Regenerate all three papers from one parameter set (params commit of 29 Oct 2026; stage order of 3 Nov 2026, below).
#
#   P1  The Rule of 40 as a Price Line            sections/, paper1/        (code/*.py)
#   P2  The Economics of AI Transformation        part2/                    (code/examples, code/verify_part2_*.py)
#   P3  the autofrontier engine                   engine/, code/playbook/
#
# Usage:  bash code/regenerate_all.sh [--from STAGE] [--to STAGE] [--keep-going] [--skip-raw] [--list]
#   --from STAGE   start at STAGE (earlier stages are assumed done)
#   --to STAGE     stop after STAGE
#   --keep-going   a failing check stage (verify scripts, engine tests) is recorded and the build continues; a failing
#                  generation stage always stops the build. Without it the first failure stops the build.
#   --skip-raw     skip the three stages that read third-party files in data/raw/ (params, backtest, playbook) and keep
#                  their committed outputs; for a run without the third-party downloads (Paper 1's stages need none)
#   --list         print the stages and exit
# Third-party data: data/raw/ is not redistributed. Before the first stage runs, the script checks with
# `python3 code/fetch_raw_data.py --check` that the data/raw folders the selected stages read are present and match
# data/raw/CHECKSUMS.sha256, and stops (exit 4) naming the missing files if not. Fetch them with
# `python3 code/fetch_raw_data.py` (see data/raw/README.md), or use --skip-raw.
# Every stage writes build_logs/<NN>_<stage>.log (sub-steps build_logs/<NN>_<stage>__<script>.log) and a line to
# build_logs/summary.txt. The repository root is the parent of this script's folder, so the script also runs in a
# scratch copy of the repository (PAPER_ROOT is exported for code/data_part2, whose scripts default to the
# repository that contains them).
#
# Stages, what each reads from earlier stages, and the folders of data/raw it reads (the order of 3 Nov 2026 puts every
# stage after the stages whose outputs it reads; the three reads of an output of a later stage are marked BACK and
# handled as described):
#   panel           SEC extract (data/companyfacts_extract.json, frames_*.json, sic_universe.json) and data/v3_inputs/
#                   -> data/panel*.csv, notes/panel_v3_build.json
#   params          data/panel_v2_all.csv (panel); data/raw/metr_eval_analysis (code/data_part2/08_params.py reads both
#                   runs.jsonl files); the shipped derived files data/tasks/*.csv -> data/tasks/params.yaml
#   engine_defaults data/tasks/params.yaml (params) -> engine/TRACEABILITY.md; notes lock check
#   invoice_chain   engine defaults, params.yaml -> data/examples/invoice_chain.json, part2/tables/invoice_macros.tex
#   labor_macros    invoice_chain.json -> part2/tables/labor_macros.tex
#   empirics        panels -> notes/{empirics_results,empirics_revised,gap_decomposition,paper_stats,empirics_organic,
#                   calibration_anchor_E2}.json and tables. BACK: estimate_organic.py checks its E1 anchor, on the v2
#                   sample, only against a record on the same sample: notes/calibration_results.json if its anchor is on
#                   that sample, else the v2 anchor of notes/empirics_v2_exact.json (stage empirics_v3). With neither (a
#                   first run) it skips the check and says so in the anchor file ("passed": null); stage calibrate then
#                   reruns it. (calibrate_horizons.py read calibration_anchor_E2.json until revision v2, R3-17; it now
#                   reads notes/calibration_anchor_v3.json.)
#   empirics_v3     panels, notes/empirics_organic.json -> notes/empirics_v3.json, calibration_anchor_v3.json,
#                   frontier_slope_v3.json, bootstrap_draws_v3.npz, the v3 tables. Its v2 run (V3_PANEL=v2,
#                   notes/empirics_v2_exact.json) comes first, because the v3 notes compare against it.
#   calibrate       empirics_v3 outputs, panels, params.yaml -> notes/calibration_results.json, tab_calib.tex
#   backtest        params.yaml, data/panel_v2_all.csv, engine; data/raw/{gpts_are_gpts, bls_oews_2019, bls_oews_2020,
#                   bls_oews_2021, bls_oews_2025, bls_soc, onet_31_0 (job_zones.csv)} -> notes/backtest_results.json,
#                   part2/tables/backtest_*.tex (read by nothing but Paper 2's text)
#   playbook        engine defaults, params.yaml, panels, notes/empirics_v3.json, notes/gap_decomposition.json;
#                   data/raw/onet_31_0 (task_statements.csv, for the task examples of data/playbook/*.csv) ->
#                   notes/playbook_results.json, data/playbook/*, part2/tables/playbook_*.tex,
#                   sections/tables/levers_position_macros.tex and tab_levers_position.tex (Paper 1's lever table)
#   verify_playbook the playbook's outputs, notes/empirics_v3.json, empirics_revised.json, engine defaults
#   stress_report   notes/calibration_results.json and the stored stress test (notes/mc_results_2026-11-03/) ->
#                   sections/tables/tab_stress.tex, paper1/stress_macros.tex, figures/fig_stress.pdf; it does not re-run
#                   the Monte Carlo (about a minute on four cores; command in code/REPLICATION_README.md). BACK: it also
#                   reads paper1/macros.tex, only to assert that \CcLo and \CcHi equal the calibration's range.
#   acquired_macros code/verify_part2_acquirer.py, first run: notes/case_bending_spoons_f1_extract.md, invoice_chain.json
#                   -> sections/tables/acquired_macros.tex (read by paper1_macros.py: \acqGiTwentyFour, ...Five, which
#                   come from the extract alone) and part2/tables/acquirer_macros.tex. BACK: it also reads
#                   paper1/macros.tex, to expand the sentences of sections/data.tex and empirics.tex it checks (E9, the
#                   \acqFlag* and \acqPninetyfive* macros); the authoritative run is the one in stage verify_part2.
#   paper1_macros   everything above that Paper 1 quotes: notes/{calibration_results,paper_stats,empirics_revised,
#                   gap_decomposition,empirics_organic,empirics_v3,empirics_v2_exact,frontier_slope_v3,panel_v3_build}.json,
#                   calibration_anchor_v3.json, bootstrap_draws_v3.npz, data/panel*.csv, params.yaml, the playbook's
#                   levers_position_macros.tex and playbook_results.json (\lpRatio is checked against \AlphaNet),
#                   paper1/stress_macros.tex, sections/tables/acquired_macros.tex; and paper1/spec_macros.tex, written by
#                   code/spec_curve.py, which is not a stage (run it separately; it reads paper1/macros.tex)
#                   -> paper1/macros.tex, notes/amin_r2.json
#   verify_theory   notes/calibration_results.json, frontier_slope_v3.json, data/panel_v3.csv and paper1/macros.tex
#                   (its [text] checks compare with the printed numbers)
#   verify_part2    invoice_chain.json, invoice_macros.tex, labor_macros.tex, engine defaults; verify_part2_acquirer.py
#                   (second run) reads the new paper1/macros.tex and rewrites both acquirer macro files;
#                   verify_part2_regimes.py reads part2/tables/acquirer_macros.tex, so acquirer runs before it
#   engine_tests    code/verify_part2_*.py, data/examples/invoice_chain.{yaml,json}, code/calibrate_horizons.py,
#                   code/paper1_macros.py and notes/amin_r2.json: after the generators
#   latex_p1        every Paper 1 input above (code/build_paper1.sh)
#   latex_p2        Paper 2 has no main file yet (notes/cross_paper_impacts.md: "P2 main file ... open (assembly)");
#                   set P2_MAIN=part2/<file>.tex once it exists. Without it the stage fails with that message.
# The BACK reads: a first run of stress_report or acquired_macros that fails is logged (kind "pre") and the build goes
# on; stage paper1_macros then reruns the failed script against the new paper1/macros.tex (now a failure of
# mc_report_tex.py stops the build and one of the acquirer's checks counts as a failed check) and runs paper1_macros.py
# again, so that it reads the rerun's output. Their outputs that paper1_macros.py reads do not
# depend on paper1/macros.tex, so one rerun reaches the fixed point.
# Changes of 3 Nov 2026 to the order (engine_defaults params invoice_chain labor_macros verify_part2 panel empirics
# empirics_v3 backtest calibrate stress_report verify_theory paper1_macros playbook verify_playbook engine_tests latex_p1
# latex_p2): panel first, since params reads data/panel_v2_all.csv; engine_defaults after params, since it loads
# params.yaml; verify_part2 after paper1_macros, since the acquirer reads paper1/macros.tex, with a first acquirer run
# (acquired_macros) before paper1_macros; playbook and verify_playbook before paper1_macros, which reads the lever table
# and \lpRatio; verify_theory after paper1_macros, whose macros it checks; backtest (which reads params.yaml, data/tasks,
# the engine, the v2 panel and data/raw, nothing of Paper 1's) moved beside the playbook, the other stage that reads data/raw.
# Paper 1's own stages (panel, empirics, empirics_v3, calibrate, stress_report, paper1_macros, verify_theory, latex_p1)
# read nothing in data/raw. Besides the SEC extract and data/v3_inputs they read shipped files that other stages write:
# data/tasks/params.yaml (params, which reads data/raw/metr_eval_analysis), the playbook's lever table and results
# (playbook, which reads data/raw/onet_31_0/task_statements.csv), sections/tables/acquired_macros.tex (acquired_macros),
# the stored stress test and paper1/spec_macros.tex. With --skip-raw the committed params.yaml and playbook outputs are
# used, and every other stage runs.
# Environment passed through: ORGANIC_PANEL (v2 | v3; estimate_organic.py), ORGANIC_FAST, V3_FAST, V3_JOBS, P2_MAIN.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
export PYTHONHASHSEED=0
export PYTHONDONTWRITEBYTECODE=1
export PAPER_ROOT="$ROOT"
export MPLBACKEND=Agg
PY="${PYTHON:-python3}"
LOGDIR="$ROOT/build_logs"

STAGES=(panel params engine_defaults invoice_chain labor_macros empirics empirics_v3 calibrate backtest playbook
        verify_playbook stress_report extensions acquired_macros paper1_macros verify_theory verify_part2 engine_tests latex_p1
        latex_p2)

# folders of data/raw/ (code/fetch_raw_data.py sources) that a stage reads; every other stage reads none
raw_needs() {
  case "$1" in
    params) echo "metr_eval_analysis" ;;
    backtest) echo "gpts_are_gpts bls_oews_2019 bls_oews_2020 bls_oews_2021 bls_oews_2025 bls_soc onet_31_0" ;;
    playbook) echo "onet_31_0" ;;
    *) echo "" ;;
  esac
}

FROM="" TO="" KEEP_GOING=0 SKIP_RAW=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --from) FROM="$2"; shift 2 ;;
    --to) TO="$2"; shift 2 ;;
    --keep-going) KEEP_GOING=1; shift ;;
    --skip-raw) SKIP_RAW=1; shift ;;
    --list) printf '%s\n' "${STAGES[@]}"; exit 0 ;;
    -h|--help) sed -n '2,23p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "unknown option $1 (see --help)" >&2; exit 2 ;;
  esac
done
valid() { local s; for s in "${STAGES[@]}"; do [[ "$s" == "$1" ]] && return 0; done; return 1; }
[[ -z "$FROM" ]] || valid "$FROM" || { echo "unknown stage '$FROM'; stages: ${STAGES[*]}" >&2; exit 2; }
[[ -z "$TO" ]] || valid "$TO" || { echo "unknown stage '$TO'; stages: ${STAGES[*]}" >&2; exit 2; }

# the stages this run executes, in order
SELECTED=()
started=0
[[ -z "$FROM" ]] && started=1
for s in "${STAGES[@]}"; do
  [[ "$s" == "$FROM" ]] && started=1
  [[ $started -eq 1 ]] && SELECTED+=("$s")
  [[ -n "$TO" && "$s" == "$TO" ]] && break
done
if [[ ${#SELECTED[@]} -eq 0 ]]; then
  echo "no stage selected: --to ${TO} comes before --from ${FROM} (see --list)" >&2; exit 2
fi

# third-party raw data: verify, before anything runs, every data/raw folder a selected stage reads
RAW_SOURCES=() RAW_STAGES=()
if [[ $SKIP_RAW -eq 0 ]]; then
  for s in "${SELECTED[@]}"; do
    need="$(raw_needs "$s")"
    [[ -z "$need" ]] && continue
    RAW_STAGES+=("$s ($need)")
    for src in $need; do
      [[ " ${RAW_SOURCES[*]-} " == *" $src "* ]] || RAW_SOURCES+=("$src")
    done
  done
fi
if [[ ${#RAW_SOURCES[@]} -gt 0 ]]; then
  rc=0
  out="$(cd "$ROOT" && "$PY" code/fetch_raw_data.py --check --quiet "${RAW_SOURCES[@]}" 2>&1)" || rc=$?
  if [[ $rc -ne 0 ]]; then
    {
      echo "STOPPED before the first stage: stages that read third-party files in data/raw/ are selected, and some of"
      echo "those files are missing or differ from data/raw/CHECKSUMS.sha256 (data/raw/ is not redistributed)."
      printf '  %s\n' "${RAW_STAGES[@]}"
      echo
      printf '%s\n' "$out" | sed 's/^/  | /'
      echo
      echo "Fetch and verify them with:   python3 code/fetch_raw_data.py ${RAW_SOURCES[*]}"
      echo "(files from hosts that refuse scripts: it prints how to save them from a browser; data/raw/README.md)."
      echo "Or run without these stages:  bash code/regenerate_all.sh --skip-raw ...   (keeps their committed outputs)"
    } >&2
    exit 4
  fi
fi

mkdir -p "$LOGDIR"
SUMMARY="$LOGDIR/summary.txt"
FAILED_CHECKS=() PRE_FAILED=()
{ echo "regenerate_all.sh started $(date -u +%Y-%m-%dT%H:%M:%SZ) in $ROOT (from=${FROM:-start}, to=${TO:-end}, keep_going=$KEEP_GOING, skip_raw=$SKIP_RAW)"
  echo "engine defaults sha256 $(sha256sum "$ROOT/engine/src/autofrontier/defaults.yaml" | cut -c1-16)," \
       "params.yaml $(sha256sum "$ROOT/data/tasks/params.yaml" | cut -c1-16)," \
       "params_reliability.yaml $(sha256sum "$ROOT/data/tasks/params_reliability.yaml" | cut -c1-16)"
  if [[ ${#RAW_SOURCES[@]} -gt 0 ]]; then echo "data/raw verified for: ${RAW_SOURCES[*]}"; fi; } >> "$SUMMARY"

N=0 CUR="" STAGE_LOG=""
# run LABEL KIND CMD...: KIND is gen (failure stops the build), check (failure stops it unless --keep-going) or pre
# (the first run of a script that also reads an output of a later stage: a failure is logged and the script is rerun
# after that stage; see the header)
run() {
  local label="$1" kind="$2"; shift 2
  local log="$LOGDIR/$(printf '%02d' "$N")_${CUR}__${label}.log" t0=$SECONDS rc=0
  echo "[$CUR] $label: $*" | tee -a "$STAGE_LOG"
  ( cd "$ROOT" && "$@" ) > "$log" 2>&1 || rc=$?
  local msg="[$CUR] $label: exit $rc after $((SECONDS - t0)) s (log $(basename "$log"))"
  echo "$msg" | tee -a "$STAGE_LOG" >> "$SUMMARY"
  if [[ $rc -ne 0 ]]; then
    tail -n 25 "$log" | sed 's/^/    | /' >> "$STAGE_LOG"
    if [[ "$kind" == pre ]]; then
      PRE_FAILED+=("$label")
      echo "    (first run failed; it reads paper1/macros.tex of the previous run and is rerun in stage paper1_macros)" \
        | tee -a "$STAGE_LOG" >> "$SUMMARY"
    elif [[ "$kind" == check && $KEEP_GOING -eq 1 ]]; then
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

stage_panel() {
  run build_panel_v2 gen "$PY" code/build_panel_v2.py
  run build_panel_v3 gen "$PY" code/build_panel_v3.py
}
stage_params() {
  run 08_params gen "$PY" -I code/data_part2/08_params.py
  run 10_validate check "$PY" -I code/data_part2/10_validate.py
}
stage_engine_defaults() {
  run load_params gen "$PY" -c "import sys; sys.path.insert(0, 'engine/src'); from autofrontier import config; \
p = config.load_params(); bad = [l for l in p.params_log if l['status'].startswith('missing')]; \
print(len(p.keys()), 'parameters,', len(p.params_log), 'linked'); assert not bad, bad"
  run traceability gen bash -c "cd engine && $PY tools/traceability.py"
  run notes_lock check bash -c "cd engine && $PY tools/check_sync.py"
}
stage_invoice_chain() { run invoice_chain gen "$PY" code/examples/invoice_chain.py; }
stage_labor_macros() { run make_labor_macros gen "$PY" code/make_labor_macros.py; }
stage_empirics() {
  run estimate_frontier gen "$PY" code/estimate_frontier.py
  run estimate_revised gen "$PY" code/estimate_revised.py
  run decompose_gap gen "$PY" code/decompose_gap.py
  run paper_stats gen "$PY" code/paper_stats.py
  run estimate_organic gen "$PY" code/estimate_organic.py
}
stage_empirics_v3() {
  run estimate_v3_on_v2 gen env V3_PANEL=v2 "$PY" code/estimate_v3.py
  run estimate_v3 gen "$PY" code/estimate_v3.py
}
stage_calibrate() {
  run calibrate_horizons gen "$PY" code/calibrate_horizons.py
  if grep -q '"passed": null' "$ROOT/notes/calibration_anchor_E2.json" 2>/dev/null; then   # first run: do the E1 check now
    run estimate_organic_recheck gen "$PY" code/estimate_organic.py
  fi
}
stage_backtest() { run backtest gen "$PY" code/validation/backtest.py; }
stage_playbook() { run run_archetypes gen "$PY" code/playbook/run_archetypes.py; }
stage_verify_playbook() { run verify_part2_playbook check "$PY" code/verify_part2_playbook.py; }
stage_stress_report() { run mc_report_tex pre "$PY" code/mc_report_tex.py; }   # reads the committed MC outputs only
stage_extensions() {   # Supplement S12 (added 4 Nov 2026): reads the calibration, the panel, the float file and the stored MC run
  run biz_open_questions gen "$PY" code/biz_open_questions.py
  run biz_valuation gen "$PY" code/biz_valuation.py
  run supp_extensions gen "$PY" code/supp_extensions.py
}
stage_acquired_macros() { run verify_part2_acquirer pre "$PY" code/verify_part2_acquirer.py; }
stage_paper1_macros() {
  run paper1_macros gen "$PY" code/paper1_macros.py
  if [[ ${#PRE_FAILED[@]} -gt 0 ]]; then        # a first run that read the previous paper1/macros.tex failed: rerun it
    local l
    for l in "${PRE_FAILED[@]}"; do
      case "$l" in
        mc_report_tex) run mc_report_tex_rerun gen "$PY" code/mc_report_tex.py ;;
        verify_part2_acquirer) run verify_part2_acquirer_rerun check "$PY" code/verify_part2_acquirer.py ;;
      esac
    done
    PRE_FAILED=()
    run paper1_macros_rerun gen "$PY" code/paper1_macros.py
  fi
}
stage_verify_theory() {
  run verify_theory check bash -c "$PY code/verify_theory.py > notes/verify_theory_output.txt 2>&1; rc=\$?; \
tail -n 5 notes/verify_theory_output.txt; exit \$rc"
}
stage_verify_part2() {
  local s
  for s in accounting acquirer regimes core ext labor product competition; do
    run "verify_part2_$s" check "$PY" "code/verify_part2_$s.py"
  done
}
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

for s in "${STAGES[@]}"; do
  N=$((N + 1))
  [[ " ${SELECTED[*]} " == *" $s "* ]] || continue
  CUR="$s"; STAGE_LOG="$LOGDIR/$(printf '%02d' "$N")_${s}.log"; : > "$STAGE_LOG"
  if [[ $SKIP_RAW -eq 1 && -n "$(raw_needs "$s")" ]]; then
    echo "== $(printf '%02d' "$N") $s: skipped (--skip-raw; it reads data/raw/: $(raw_needs "$s")); committed outputs kept" \
      | tee -a "$SUMMARY" | tee -a "$STAGE_LOG"
    continue
  fi
  echo "== $(printf '%02d' "$N") $s" | tee -a "$SUMMARY"
  "stage_$s"
done
if [[ ${#PRE_FAILED[@]} -gt 0 ]]; then   # the run stopped (--to) before stage paper1_macros could rerun them
  echo "first runs failed and were not rerun because the run ended before stage paper1_macros: ${PRE_FAILED[*]}" \
    | tee -a "$SUMMARY"
  exit 1
fi
if [[ ${#FAILED_CHECKS[@]} -gt 0 ]]; then
  echo "finished with failing checks: ${FAILED_CHECKS[*]}" | tee -a "$SUMMARY"
  exit 1
fi
echo "finished $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$SUMMARY"
