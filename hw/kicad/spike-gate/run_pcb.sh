#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Spike: build the placed PCB (mech V1 envelope) from the full-board netlist, route it with Freerouting, run DRC
# and the net comparison.
# Usage: run_pcb.sh <dir written by run_full.sh> <out dir> [layers 2|4] [planes]
#   layers  2 (default) or 4
#   planes  what the router sees as GND pour: 2 layers: B (default), FB or none; 4 layers: none (default) or inner
# Env: FREEROUTING_JAR  path of freerouting-2.5.0.jar (v2.5.0, sha256 f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7, a pinned release downloaded
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
if [ -n "$FREEROUTING_JAR" ]; then      # pinned release; a missing or different file stops the run (plan 06 T5)
  JAR_SHA=f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7
  [ -f "$FREEROUTING_JAR" ] || { echo "FREEROUTING_JAR: no such file: $FREEROUTING_JAR"; exit 1; }
  [ "$(sha256sum "$FREEROUTING_JAR" | cut -d' ' -f1)" = "$JAR_SHA" ] \
    || { echo "FREEROUTING_JAR: sha256 is not the pinned $JAR_SHA"; exit 1; }
fi
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
PLACED_RC=0      # a failing strict DRC step does not stop the run: all numbers of the run must exist; the exit code says it failed
export SPIKE_ALLOW_KNOWN_OPEN=${SPIKE_ALLOW_KNOWN_OPEN:-1}
"$PY" "$HERE/src/kicad_strict.py" drc "$OUT/a/busy_light_spike.kicad_pcb" "placed-${LAYERS}l" --out "$OUT/a/drc_placed.json" || PLACED_RC=1

STATUS=$PLACED_RC
if [ -n "$FREEROUTING_JAR" ]; then
  A="$OUT/a"
  PLACED_SHA=$(sha256sum "$A/busy_light_spike.kicad_pcb" | cut -d' ' -f1)
  "$PY" "$HERE/src/pcb_dsn.py" export "$A/busy_light_spike.kicad_pcb" "$A/b.dsn" "$PLANES" 2>&1 | filter
  T0=$(date +%s)
  java -jar "$FREEROUTING_JAR" -de "$A/b.dsn" -do "$A/b.ses" -mp "${FR_PASSES:-60}" -mt 4 > "$A/freerouting.log" 2>&1
  WALL=$(( $(date +%s) - T0 ))
  grep -E "Auto-routing stage completed" "$A/freerouting.log" | tail -1 | cut -c1-300
  "$PY" "$HERE/src/pcb_dsn.py" import "$A/busy_light_spike.kicad_pcb" "$A/b.ses" "$A/routed.kicad_pcb" 2>&1 | filter
  \cp -f "$A/busy_light_spike.kicad_pro" "$A/routed.kicad_pro"
  \cp -f "$A/busy_light_spike.kicad_dru" "$A/routed.kicad_dru"
  \cp -f "$IN/full.kicad_sch" "$A/routed.kicad_sch"
  # every strict DRC step runs; a failing step sets STATUS so that all numbers of the run exist
  "$PY" "$HERE/src/kicad_strict.py" drc "$A/routed.kicad_pcb" "routed-${LAYERS}l" --out "$A/drc_routed.json" || STATUS=1
  "$PY" "$HERE/src/pcb_check.py" "$NET" "$A/routed.kicad_pcb" "$A/drc_routed.json" > "$A/check_routed.json" 2>/dev/null \
    || { echo "pad-net comparison (M3) FAILED: see $A/check_routed.json"; STATUS=1; }
  echo "wrote $A/check_routed.json"
  echo "M1 unrouted (routed board, plane nets excluded): $("$PY" "$HERE/src/pcb_check.py" m1 "$A/drc_routed.json")"
  "$PY" - "$A/run_meta.json" "$PLACED_SHA" "$(sha256sum "$A/b.dsn" | cut -d' ' -f1)" "$(kicad-cli version)" \
    "$(sha256sum "$FREEROUTING_JAR" | cut -d' ' -f1)" "${FR_PASSES:-60}" 4 "$(java -version 2>&1 | head -1)" "$WALL" "$PLANES" <<'PYEOF'
import sys
import pcb_replay
a = sys.argv[1:]
pcb_replay.write_meta(a[0], placed_board_sha256=a[1], dsn_sha256=a[2], kicad_version=a[3], jar_sha256=a[4],
                      fr_passes=int(a[5]), fr_threads=int(a[6]), java_version=a[7], wall_time_s=float(a[8]), planes=a[9])
PYEOF
  # stitching completes the plane nets (non-zero exit when a pad cannot be stitched)
  "$PY" "$HERE/src/pcb_stitch.py" "$A/routed.kicad_pcb" "$A/drc_routed.json" "$A/stitched.kicad_pcb" || STATUS=1
  \cp -f "$A/routed.kicad_pro" "$A/stitched.kicad_pro"
  \cp -f "$A/routed.kicad_dru" "$A/stitched.kicad_dru"
  \cp -f "$A/routed.kicad_sch" "$A/stitched.kicad_sch"
  \cp -f "$A/busy_light_spike.placement.json" "$A/stitched.placement.json"
  "$PY" "$HERE/src/kicad_strict.py" drc "$A/stitched.kicad_pcb" "stitched-${LAYERS}l" --out "$A/drc_stitched.json" || STATUS=1
  echo "M2 unconnected (stitched board, all nets): $("$PY" "$HERE/src/pcb_check.py" m2 "$A/drc_stitched.json")"
fi
exit $STATUS
