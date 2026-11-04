#!/usr/bin/env bash
# Mechanical checks. Same script locally and in CI.
# Runs every mech/freecad/*.py generator headless and then every mech/analysis/check_*.py.
# Needs: FreeCAD 1.x (`freecad` command). Missing input is reported as NOT RUN, never as a pass.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
shopt -s nullglob
gen=(mech/freecad/*.py); chk=(mech/analysis/check_*.py)
((${#gen[@]})) || { echo "mech: NOT RUN - no generator in mech/freecad"; exit 0; }
command -v freecad >/dev/null || { echo "ERROR: freecad not found" >&2; exit 2; }
export QT_QPA_PLATFORM=offscreen
for f in "${gen[@]}"; do
  echo "== generate $f"
  echo "exec(open('$f').read())" | timeout 600 freecad -c
done
if ((${#chk[@]})); then
  for f in "${chk[@]}"; do echo "== check $f"; python3 -I "$f"; done
else
  echo "mech: interference/tolerance checks NOT RUN - no mech/analysis/check_*.py"
fi
