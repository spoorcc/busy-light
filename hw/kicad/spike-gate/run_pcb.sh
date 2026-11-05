#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Spike: build the placed PCB from the full-board netlist, route it, run DRC and the net comparison.
# Usage: run_pcb.sh <dir written by run_full.sh> <out dir>
# Needs system python3 with KiCad's pcbnew module (KiCad 10), numpy, scipy, and kicad-cli. The outputs
# (.kicad_pcb, .kicad_pro, reports) stay in <out dir> and are not committed (same rule as the schematic spike).
# Routing: src/route_grid.py (own deterministic grid router). Freerouting is an optional alternative, see
# docs/verification/reports/spike-pcb-placement-routing.md; it is NOT run here.
set -e
IN=$1; OUT=$2; HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PCB_PYTHON:-python3}
mkdir -p "$OUT"
export PYTHONPATH="$HERE/src"
NET="$IN/kicad.net"
[ -f "$NET" ] || { echo "no $NET (run run_full.sh first)"; exit 1; }
filter() { grep -v 'PROPERTY_ENUM' || true; }

rm -rf "$OUT/a" "$OUT/b"
"$PY" "$HERE/src/pcb_full.py" "$NET" "$OUT/a" busy_light_spike 2>&1 | filter
"$PY" "$HERE/src/pcb_full.py" "$NET" "$OUT/b" busy_light_spike 2>&1 | filter
cmp "$OUT/a/busy_light_spike.kicad_pcb" "$OUT/b/busy_light_spike.kicad_pcb" \
  && echo "placement build: identical" || { echo "placement build: DIFFERENT"; exit 1; }
cmp "$OUT/a/busy_light_spike.kicad_pro" "$OUT/b/busy_light_spike.kicad_pro"
rm -rf "$OUT/b"

"$PY" "$HERE/src/route_grid.py" "$OUT/a/busy_light_spike.kicad_pcb" "$OUT/a/routed.kicad_pcb" "$OUT/a/route.json" 2>&1 | filter
cp -f "$OUT/a/busy_light_spike.kicad_pro" "$OUT/a/routed.kicad_pro"
cp -f "$IN/full.kicad_sch" "$OUT/a/routed.kicad_sch"
cp -f "$IN/full.kicad_sch" "$OUT/a/busy_light_spike.kicad_sch"
for n in busy_light_spike routed; do
  kicad-cli pcb drc --format json --severity-all --schematic-parity --refill-zones \
    -o "$OUT/a/drc_$n.json" "$OUT/a/$n.kicad_pcb" 2>&1 | tail -3
done
"$PY" "$HERE/src/pcb_check.py" "$NET" "$OUT/a/routed.kicad_pcb" "$OUT/a/drc_routed.json" > "$OUT/a/check_routed.json" 2>/dev/null || true
echo "wrote $OUT/a/check_routed.json"
