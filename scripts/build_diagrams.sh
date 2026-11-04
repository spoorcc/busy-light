#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Render diagram sources (docs/diagrams/{plantuml,mermaid,wavedrom}) to SVG in docs/diagrams/generated/.
#   scripts/build_diagrams.sh          render all
#   scripts/build_diagrams.sh --check  render to a temp dir and fail if committed outputs differ (CI)
# Tools: plantuml (system), mmdc + wavedrom-cli (npm ci --prefix scripts/diagrams).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/docs/diagrams"
CHECK=0; [[ "${1:-}" == "--check" ]] && CHECK=1
OUT="$SRC/generated"; [[ $CHECK -eq 1 ]] && OUT="$(mktemp -d)" && trap 'rm -rf "$OUT"' EXIT
NPXBIN="$ROOT/scripts/diagrams/node_modules/.bin"
fail=0

need() { command -v "$1" >/dev/null 2>&1 || [[ -x "$NPXBIN/$1" ]] || { echo "ERROR: '$1' not found. $2" >&2; exit 2; }; }
bin()  { if [[ -x "$NPXBIN/$1" ]]; then echo "$NPXBIN/$1"; else command -v "$1"; fi; }

shopt -s nullglob
puml=("$SRC"/plantuml/*.puml); mmd=("$SRC"/mermaid/*.mmd); wd=("$SRC"/wavedrom/*.json)

if ((${#puml[@]})); then
  need plantuml "Install PlantUML (e.g. pacman -S plantuml)."
  mkdir -p "$OUT/plantuml"
  plantuml -tsvg -nometadata -o "$OUT/plantuml" "${puml[@]}"
fi
if ((${#mmd[@]})); then
  need mmdc "Run: npm ci --prefix scripts/diagrams"
  mkdir -p "$OUT/mermaid"
  for f in "${mmd[@]}"; do "$(bin mmdc)" -q -i "$f" -o "$OUT/mermaid/$(basename "${f%.mmd}").svg"; done
fi
if ((${#wd[@]})); then
  need wavedrom-cli "Run: npm ci --prefix scripts/diagrams"
  mkdir -p "$OUT/wavedrom"
  for f in "${wd[@]}"; do "$(bin wavedrom-cli)" -i "$f" -s "$OUT/wavedrom/$(basename "${f%.json}").svg"; done
fi

if [[ $CHECK -eq 1 ]]; then
  # Compare structure and text, not coordinates: text widths depend on the machine's font metrics
  # (scripts/svg_normalize.py replaces numbers inside attribute values).
  stale=0
  while IFS= read -r -d '' f; do
    rel="${f#"$SRC/generated/"}"
    if [[ ! -f "$OUT/$rel" ]] || ! diff -q <(python3 -I "$ROOT/scripts/svg_normalize.py" "$f") \
         <(python3 -I "$ROOT/scripts/svg_normalize.py" "$OUT/$rel") >/dev/null; then
      echo "stale: $rel"; stale=1
    fi
  done < <(find "$SRC/generated" -name '*.svg' -print0)
  while IFS= read -r -d '' f; do
    [[ -f "$SRC/generated/${f#"$OUT/"}" ]] || { echo "missing committed output: ${f#"$OUT/"}"; stale=1; }
  done < <(find "$OUT" -name '*.svg' -print0)
  if [[ $stale -eq 0 ]]; then echo "diagrams: up to date"
  else echo "ERROR: generated diagrams are stale. Run scripts/build_diagrams.sh" >&2; fail=1; fi
else
  echo "diagrams: rendered to ${OUT#"$ROOT"/}"
fi
exit $fail
