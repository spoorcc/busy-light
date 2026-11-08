#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
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
# The generated spike board (hw/kicad/spike-gate/board) has known, waived findings: the antenna keep-out overlaps (DEV-004,
# ADR-0003) and the C3/C4 footprint mismatch (HW-014 Draft). Its checks go through the strict wrapper, which fails on every
# finding outside the waiver list (hw/kicad/spike-gate/known-open-violations.json). Every other file keeps the raw check.
STRICT=hw/kicad/spike-gate/src/kicad_strict.py
is_spike_board() { [[ "$1" == hw/kicad/spike-gate/board/* ]]; }
for f in "${sch[@]}"; do
  echo "== ERC $f"
  if is_spike_board "$f"; then
    SPIKE_ALLOW_KNOWN_OPEN=0 python3 "$STRICT" erc "$f" full --out "$OUT/$(basename "$f").erc.json"
  else
    kicad-cli sch erc --severity-all --exit-code-violations --output "$OUT/$(basename "$f").erc.rpt" "$f"
  fi
  kicad-cli sch export bom --output "$OUT/$(basename "$f" .kicad_sch).bom.csv" "$f"
done
for f in "${pcb[@]}"; do
  echo "== DRC $f"
  if is_spike_board "$f"; then
    SPIKE_ALLOW_KNOWN_OPEN=0 python3 "$STRICT" drc "$f" stitched-4l --out "$OUT/$(basename "$f").drc.json"
  else
    kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity \
      --output "$OUT/$(basename "$f").drc.rpt" "$f"
  fi
done
if [[ -f hw/kicad/src/generate.py ]]; then
  echo "== regeneration check (committed files must equal generator output)"
  python3 hw/kicad/src/generate.py --check
else
  echo "hw: regeneration check NOT RUN - no hw/kicad/src/generate.py"
fi
echo "hw: reports in $OUT"
