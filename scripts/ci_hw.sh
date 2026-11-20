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
# The generated spike boards (hw/kicad/spike-gate/board and board-p1) have known, waived findings: the antenna keep-out overlaps (DEV-004,
# ADR-0003). Its checks go through the strict wrapper, which fails on every
# finding outside the waiver list (hw/kicad/spike-gate/known-open-violations.json). Every other file keeps the raw check.
STRICT=hw/kicad/spike-gate/src/kicad_strict.py
is_spike_board() { [[ "$1" == hw/kicad/spike-gate/board/* || "$1" == hw/kicad/spike-gate/board-p1/* ]]; }   # board-p1: plan 08
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
    if [[ "$f" == hw/kicad/spike-gate/board-p1/* ]]; then   # plan 08: no via in an SMD pad (owner answer 9), supply paths
      echo "== fab check and power check $f"
      python3 hw/kicad/spike-gate/src/pcb_fabcheck.py --no-via-in-pad "$f" > "$OUT/$(basename "$f").fabcheck.json"
      python3 hw/kicad/spike-gate/src/pcb_power_check.py "$f" "$OUT/$(basename "$f").power.json" > /dev/null
      python3 - "$OUT/$(basename "$f").power.json" <<'PY'
import json
import sys

nets = json.load(open(sys.argv[1], encoding="utf-8"))["nets"]
bad = [n for n, v in sorted(nets.items()) if not v["within_50mv"] or v.get("full_width_path") is False]
for n, v in sorted(nets.items()):
    print("   %-8s %s mV, full-width path %s" % (n, v["drop_mv"], v.get("full_width_path")))
sys.exit("power check FAILED: " + ", ".join(bad) if bad else 0)
PY
    fi
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
