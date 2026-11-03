#!/usr/bin/env bash
# Million-draw stress test of Paper 1 (Supplement S10), run natively on this Mac. 3 November 2026.
#
#   bash ~/workspace/stress_runs_2026-11-03/run_stress.sh
#
# What it does, all inside this folder (nothing else on the Mac is changed; safe to rerun, it resumes):
#   1. installs uv (astral.sh), Python 3.13 and the pinned packages (those of the sandbox run) into ./.uv, ./venv
#   2. unpacks the code and inputs of commit 06a6338 (../_transfer/rox_06a6338.tar.gz, sha256 checked)
#   3. seed 2 (20261104): the 1,000,000 Latin-hypercube draws and 100,000 corners, on every core
#   4. waits until seed 1's draws (run in the Claude sandbox into ./mc_1m_s1) are complete
#   5. seed 1: searches, Sobol indices (65,536 base samples), sub-box, analysis, outputs
#   6. seed 2: the same, compared with seed 1
#   7. gzips the per-draw files and writes DONE
# Keeps the Mac awake while it runs (caffeinate). Log: ./run_stress.log
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"
LOG="$D/run_stress.log"
exec > >(tee -a "$LOG") 2>&1
say() { printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }
say "start in $D"
command -v caffeinate >/dev/null && { caffeinate -dims -w $$ & }

# --- the run's settings: they set the checkpoint key, so they must not change ---------------------------------
ARGS=(--n 1000000 --corners 100000 --sobol-n 65536 --amin-n 100000 --search-budget 6000)
KEY1=e291b0637f62          # seed 1's checkpoint key (made in the sandbox)
KEY2=2feadf083557          # seed 2's checkpoint key for these settings
NCHUNK=5501                # 1,100,002 points in chunks of 200
TARBALL="$D/../_transfer/rox_06a6338.tar.gz"
TARSHA=577a983329980e50d7f21a4aeec2d853db043f3a0a76b48f01edfe725d4eccfc
CODE="$D/rox_06a6338"

# --- 0. machine ------------------------------------------------------------------------------------------------
NCPU=$( (sysctl -n hw.ncpu 2>/dev/null || nproc) )
MEMGB=$(( $( (sysctl -n hw.memsize 2>/dev/null || awk '/MemTotal/ {print $2*1024}' /proc/meminfo) ) / 1073741824 ))
FREEGB=$(df -Pk "$D" | awk 'NR==2 {print int($4/1048576)}')
say "cores $NCPU, memory ${MEMGB} GB, free disk ${FREEGB} GB"
[ "$MEMGB" -ge 8 ] || { say "STOP: needs at least 8 GB of memory"; exit 2; }
[ "$FREEGB" -ge 10 ] || { say "STOP: needs at least 10 GB of free disk"; exit 2; }
WORKERS=$(( NCPU > 2 ? NCPU - 1 : 1 ))     # leave one core for the main process

# --- 1. Python and packages (inside this folder) ---------------------------------------------------------------
export UV_INSTALL_DIR="$D/.uv/bin" UV_NO_MODIFY_PATH=1 UV_PYTHON_INSTALL_DIR="$D/.uv/python" UV_CACHE_DIR="$D/.uv/cache"
find_uv() { for c in "$D/.uv/bin/uv" "$D/.uv/bin/bin/uv"; do [ -x "$c" ] && { echo "$c"; return; }; done; }
if [ -z "$(find_uv)" ]; then
  say "installing uv into $D/.uv (download from astral.sh)"
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
UV="$(find_uv)"; [ -n "$UV" ] || { say "STOP: uv did not install"; exit 2; }
if [ ! -x "$D/venv/bin/python" ]; then
  say "creating Python 3.13 environment in $D/venv"
  "$UV" venv --python 3.13 "$D/venv"
fi
PY="$D/venv/bin/python"

# --- 2. code and inputs ----------------------------------------------------------------------------------------
if [ ! -f "$CODE/COMMIT" ]; then
  [ -f "$TARBALL" ] || { say "STOP: $TARBALL not found"; exit 2; }
  GOT=$( (shasum -a 256 "$TARBALL" 2>/dev/null || sha256sum "$TARBALL") | cut -c1-64)
  [ "$GOT" = "$TARSHA" ] || { say "STOP: tarball sha256 $GOT, expected $TARSHA"; exit 2; }
  mkdir -p "$CODE" && tar -xzf "$TARBALL" -C "$CODE"
fi
say "code at commit $(cat "$CODE/COMMIT")"
# the package versions of the sandbox environment that runs seed 1's draws (SALib for the factor-level Sobol indices)
REQS="PuLP==3.3.0 PyYAML==6.0.3 SALib==1.6.0 annotated-types==0.8.0 contourpy==1.4.0 cycler==0.12.1 dill==0.4.1 et_xmlfile==2.0.0 fonttools==4.68.0 formulaic==1.2.2 interface_meta==2.0.1 kiwisolver==1.5.1 matplotlib==3.11.2 mpmath==1.3.0 multiprocess==0.70.19 narwhals==2.28.0 numpy==2.5.3 openpyxl==3.1.5 packaging==26.3 pandas==3.0.5 patsy==1.0.3 pillow==13.0.0 pydantic==2.13.5 pydantic_core==2.46.5 pyparsing==3.3.3 python-dateutil==4.0.0 scipy==1.18.1 statsmodels==0.15.0 sympy==1.14.0 typing-inspection==0.4.4 typing_extensions==4.16.0 tzdata==2026.6 wrapt==2.5.2 xlrd==2.0.2"
if ! "$PY" -c "import numpy, pandas, scipy, yaml, SALib" 2>/dev/null; then
  say "installing the pinned packages (download from PyPI)"
  "$UV" pip install --python "$PY" $REQS
fi
"$PY" -c "import numpy, pandas, scipy; print('numpy', numpy.__version__, 'pandas', pandas.__version__, 'scipy', scipy.__version__)"

cd "$CODE"
say "reproduction checks"
"$PY" code/mc_claims.py --verify-only --out "$D/_verify" > "$D/_verify.log" 2>&1 || { say "STOP: reproduction checks did not run; see _verify.log"; exit 1; }
if grep -q '^FAIL' "$D/_verify.log"; then say "STOP: a reproduction check failed:"; grep '^FAIL' "$D/_verify.log"; exit 1; fi
say "$(grep -o 'reproduction checks: .*' "$D/_verify.log" | tail -1)"

ndone() { ls "$1"/ckpt/"$2"/ 2>/dev/null | grep -c '^draws_' || true; }
key_of() { grep -o 'config [0-9a-f]*' "$1" | tail -1 | cut -d' ' -f2; }

# --- 3. seed 2: draws ------------------------------------------------------------------------------------------
if [ "$(ndone "$D/mc_1m_s2" "$KEY2")" -lt "$NCHUNK" ]; then
  say "seed 2: draws on $WORKERS workers (resumes if interrupted)"
  "$PY" code/mc_claims.py "${ARGS[@]}" --seed 20261104 --workers "$WORKERS" --stop-after draws \
        --out "$D/mc_1m_s2" > "$D/mc_1m_s2.native.log" 2>&1 || { say "STOP: seed 2 draws failed; see mc_1m_s2.native.log"; tail -20 "$D/mc_1m_s2.native.log"; exit 1; }
  [ "$(key_of "$D/mc_1m_s2.native.log")" = "$KEY2" ] || { say "STOP: seed 2 checkpoint key is not $KEY2"; exit 1; }
fi
say "seed 2: $(ndone "$D/mc_1m_s2" "$KEY2") of $NCHUNK chunks"

# --- 4. wait for seed 1's draws from the sandbox ---------------------------------------------------------------
while [ "$(ndone "$D/mc_1m_s1" "$KEY1")" -lt "$NCHUNK" ]; do
  say "waiting for seed 1's draws: $(ndone "$D/mc_1m_s1" "$KEY1") of $NCHUNK chunks (checking every 2 minutes)"
  sleep 120
done
sleep 30     # let the sandbox finish its last write

# --- 5. seed 1: final phases -----------------------------------------------------------------------------------
if [ ! -f "$D/mc_1m_s1/mc_claims.json" ]; then
  say "seed 1: searches, Sobol, sub-box, analysis"
  "$PY" code/mc_claims.py "${ARGS[@]}" --seed 20261102 --workers "$WORKERS" \
        --out "$D/mc_1m_s1" > "$D/mc_1m_s1.native.log" 2>&1 || { say "STOP: seed 1 final failed; see mc_1m_s1.native.log"; tail -20 "$D/mc_1m_s1.native.log"; exit 1; }
  [ "$(key_of "$D/mc_1m_s1.native.log")" = "$KEY1" ] || { say "STOP: seed 1 checkpoint key is not $KEY1"; exit 1; }
fi

# --- 6. seed 2: final phases, compared with seed 1 -------------------------------------------------------------
if [ ! -f "$D/mc_1m_s2/mc_claims.json" ]; then
  say "seed 2: searches, Sobol, sub-box, analysis, comparison with seed 1"
  "$PY" code/mc_claims.py "${ARGS[@]}" --seed 20261104 --workers "$WORKERS" --compare-to "$D/mc_1m_s1" \
        --out "$D/mc_1m_s2" >> "$D/mc_1m_s2.native.log" 2>&1 || { say "STOP: seed 2 final failed; see mc_1m_s2.native.log"; tail -20 "$D/mc_1m_s2.native.log"; exit 1; }
fi

# --- 7. compress and finish -------------------------------------------------------------------------------------
for s in mc_1m_s1 mc_1m_s2; do
  [ -f "$D/$s/draws_lhs.csv.gz" ] || gzip -k -6 "$D/$s/draws_lhs.csv"
done
ls -l "$D"/mc_1m_s1/mc_claims.json "$D"/mc_1m_s2/mc_claims.json "$D"/mc_1m_s*/draws_lhs.csv.gz
date > "$D/DONE"
say "DONE. You can tell Claude the run has finished."
