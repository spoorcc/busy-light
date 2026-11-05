#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Spike: build the placed PCB (mech V1 envelope) from the full-board netlist, route it with Freerouting, run DRC
# and the net comparison.
# Usage: run_pcb.sh <dir written by run_full.sh> <out dir> [layers 2|4] [planes]
#   layers  2 (default) or 4
#   planes  what the router sees as GND pour: 2 layers: B (default), FB or none; 4 layers: none (default) or inner
# Env: FREEROUTING_JAR  path of freerouting-2.5.0.jar (v2.5.0, sha256 f6f51bb0...e3c7, a pinned release downloaded
#      from the official GitHub releases; not part of the repository). Without it the board is built and checked
#      unrouted. PCB_PYTHON (default python3) must have KiCad's pcbnew module (KiCad 10). FR_PASSES (default 60).
# The outputs (.kicad_pcb, .kicad_pro, DSN, SES, reports) stay in <out dir> and are not committed.
# src/route_grid.py (the earlier own grid router) is not run here: it knows only the old rectangular board.
set -e
IN=$1; OUT=$2; LAYERS=${3:-2}; PLANES=${4:-}
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PCB_PYTHON:-python3}
mkdir -p "$OUT"
export PYTHONPATH="$HERE/src"
NET="$IN/kicad.net"
[ -f "$NET" ] || { echo "no $NET (run run_full.sh first)"; exit 1; }
filter() { grep -v 'PROPERTY_ENUM' || true; }
if [ -z "$PLANES" ]; then [ "$LAYERS" = 4 ] && PLANES=none || PLANES=B; fi

rm -rf "$OUT/a" "$OUT/b"
"$PY" "$HERE/src/pcb_full.py" "$NET" "$OUT/a" busy_light_spike "$LAYERS" 2>&1 | filter
"$PY" "$HERE/src/pcb_full.py" "$NET" "$OUT/b" busy_light_spike "$LAYERS" 2>&1 | filter
cmp "$OUT/a/busy_light_spike.kicad_pcb" "$OUT/b/busy_light_spike.kicad_pcb" \
  && echo "placement build: identical" || { echo "placement build: DIFFERENT"; exit 1; }
cmp "$OUT/a/busy_light_spike.kicad_pro" "$OUT/b/busy_light_spike.kicad_pro"
rm -rf "$OUT/b"
cp -f "$IN/full.kicad_sch" "$OUT/a/busy_light_spike.kicad_sch"

# Strict DRC (no `| tail`): a finding that is not in known-open-violations.json fails the script.
# SPIKE_ALLOW_KNOWN_OPEN=0 (plan 06 T8): the waiver list is ignored except the `strict_allow` key of the profile.
export SPIKE_ALLOW_KNOWN_OPEN=${SPIKE_ALLOW_KNOWN_OPEN:-1}
"$PY" "$HERE/src/kicad_strict.py" drc "$OUT/a/busy_light_spike.kicad_pcb" "placed-${LAYERS}l" --out "$OUT/a/drc_placed.json"

if [ -n "$FREEROUTING_JAR" ]; then
  "$PY" "$HERE/src/pcb_dsn.py" export "$OUT/a/busy_light_spike.kicad_pcb" "$OUT/a/b.dsn" "$PLANES" 2>&1 | filter
  java -jar "$FREEROUTING_JAR" -de "$OUT/a/b.dsn" -do "$OUT/a/b.ses" -mp "${FR_PASSES:-60}" -mt 4 > "$OUT/a/freerouting.log" 2>&1
  grep -E "Auto-routing stage completed" "$OUT/a/freerouting.log" | tail -1 | cut -c1-300
  "$PY" "$HERE/src/pcb_dsn.py" import "$OUT/a/busy_light_spike.kicad_pcb" "$OUT/a/b.ses" "$OUT/a/routed.kicad_pcb" 2>&1 | filter
  cp -f "$OUT/a/busy_light_spike.kicad_pro" "$OUT/a/routed.kicad_pro"
  cp -f "$OUT/a/busy_light_spike.kicad_dru" "$OUT/a/routed.kicad_dru"
  cp -f "$IN/full.kicad_sch" "$OUT/a/routed.kicad_sch"
  "$PY" "$HERE/src/kicad_strict.py" drc "$OUT/a/routed.kicad_pcb" "routed-${LAYERS}l" --out "$OUT/a/drc_routed.json"
  "$PY" "$HERE/src/pcb_check.py" "$NET" "$OUT/a/routed.kicad_pcb" "$OUT/a/drc_routed.json" > "$OUT/a/check_routed.json" 2>/dev/null \
    || { echo "pad-net comparison (M3) FAILED: see $OUT/a/check_routed.json"; exit 1; }
  echo "wrote $OUT/a/check_routed.json"
fi
