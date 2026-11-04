#!/usr/bin/env bash
# Hardware checks (ADR-0012). Same script locally and in CI.
#   scripts/ci_hw.sh          run ERC, DRC, BOM export and the regeneration check on hw/kicad
# Needs: kicad-cli (KiCad 10.0.x). The regeneration check needs the venv (see pyproject.toml).
# A missing input is reported as NOT RUN, never as a pass.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
command -v kicad-cli >/dev/null || { echo "ERROR: kicad-cli not found" >&2; exit 2; }
kicad-cli version
OUT="${HW_CI_OUT:-$(mktemp -d)}"; mkdir -p "$OUT"
shopt -s nullglob globstar
sch=(hw/kicad/**/*.kicad_sch); pcb=(hw/kicad/**/*.kicad_pcb)
((${#sch[@]} + ${#pcb[@]})) || { echo "hw: NOT RUN - no .kicad_sch or .kicad_pcb file in hw/kicad"; exit 0; }
for f in "${sch[@]}"; do
  echo "== ERC $f"
  kicad-cli sch erc --severity-all --exit-code-violations --output "$OUT/$(basename "$f").erc.rpt" "$f"
  kicad-cli sch export bom --output "$OUT/$(basename "$f" .kicad_sch).bom.csv" "$f"
done
for f in "${pcb[@]}"; do
  echo "== DRC $f"
  kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity \
    --output "$OUT/$(basename "$f").drc.rpt" "$f"
done
if [[ -f hw/kicad/src/generate.py ]]; then
  echo "== regeneration check (committed files must equal generator output)"
  python3 hw/kicad/src/generate.py --check
else
  echo "hw: regeneration check NOT RUN - no hw/kicad/src/generate.py"
fi
echo "hw: reports in $OUT"
