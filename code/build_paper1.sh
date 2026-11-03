#!/usr/bin/env bash
# Build Paper 1: the main paper (paper1/paper1.tex) and its Supplementary Appendix (paper1/supplement.tex), two PDFs
# that read each other's cross-references through xr-hyper. Run from anywhere; the repository root is the parent of
# this script's folder (or $PAPER_ROOT). Both documents are compiled in one scratch folder, in which each finds the
# other's .aux file, with bibtex for each and up to six alternating passes until no reference changes.
# The PDFs are copied to paper1/ only if neither log reports an undefined reference or citation, a multiply defined
# label, a float too large for its page or a LaTeX error; otherwise the script exits 1 and leaves paper1/*.pdf untouched.
# Usage: bash code/build_paper1.sh [OUT_DIR]   (OUT_DIR: scratch folder to use; default a new temporary folder)
# NO_COPY=1 builds and checks without copying the PDFs to paper1/.
set -uo pipefail
ROOT="${PAPER_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
OUT="${1:-$(mktemp -d "${TMPDIR:-/tmp}/build_paper1_XXXXXX")}"
mkdir -p "$OUT"
export TEXINPUTS="$ROOT:" BIBINPUTS="$ROOT:$ROOT/paper1:" BSTINPUTS="$ROOT/paper1:"
cd "$OUT" || exit 2
rm -f paper1.aux supplement.aux

pass() {   # pass NAME: one pdflatex run of paper1/NAME.tex in $OUT
  pdflatex -interaction=nonstopmode -halt-on-error -jobname="$1" "$ROOT/paper1/$1.tex" > "$1.stdout" 2>&1
  local rc=$?
  if [[ $rc -ne 0 ]]; then
    echo "pdflatex failed on $1 (exit $rc); last lines of $OUT/$1.log:" >&2
    tail -n 30 "$1.log" >&2
    exit 1
  fi
}
for d in paper1 supplement; do pass "$d"; done
for d in paper1 supplement; do bibtex "$d" > "$d.bibtex.out" 2>&1 || { cat "$d.bibtex.out" >&2; exit 1; }; done
for i in 1 2 3 4 5 6; do
  for d in paper1 supplement; do pass "$d"; done
  if ! grep -q "Rerun to get\|Label(s) may have changed\|undefined" paper1.log supplement.log; then
    break
  fi
done

status=0
for d in paper1 supplement; do
  bad="$(grep -E "Warning: (Citation|Reference) .*undefined|multiply defined|There were undefined|There were multiply|Float too large" "$d.log" | sort -u)"
  if [[ -n "$bad" ]]; then
    echo "== $d: unresolved items" >&2; echo "$bad" | head -40 >&2; status=1
  fi
  grep -E "^Warning--|^I couldn't|error message" "$d.blg" > /dev/null 2>&1 && { echo "== $d: bibtex warnings" >&2; grep -E "^Warning--|^I couldn't" "$d.blg" >&2; }
  pages="$(pdfinfo "$d.pdf" 2>/dev/null | awk '/^Pages:/ {print $2}')"
  echo "$d.pdf: ${pages:-?} pages (build folder $OUT)"
done
if [[ $status -ne 0 ]]; then
  echo "not copied: fix the items above (PDFs left in $OUT)" >&2
  exit 1
fi
if [[ "${NO_COPY:-0}" == 1 ]]; then
  echo "clean; NO_COPY=1, so the PDFs stay in $OUT"
  exit 0
fi
cp paper1.pdf "$ROOT/paper1/paper1.pdf"
cp supplement.pdf "$ROOT/paper1/supplement.pdf"
echo "wrote $ROOT/paper1/paper1.pdf and $ROOT/paper1/supplement.pdf"
