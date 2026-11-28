#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Second Freerouting pass over a cleaned-up board (2026-11-20, after batches p1b4 to p1b12 ended at 1 to 3 open connections).
# Every track and via of <a dir>/final.kicad_pcb is locked; Freerouting routes only what is still open; then the stitch, the
# clean-up of src/pcb_fix.py and the strict DRC run again, as in run_pcb.sh.
# Usage: run_repass.sh <a dir written by run_pcb.sh> [layers, default 4] [planes, default inner]
# Works in <a dir>/repass/. When repass/final.kicad_pcb has fewer unconnected items than <a dir>/final.kicad_pcb, it takes its
# place: the first-pass board is kept as final_pass1.*, and repass/run_meta.json records the second router run.
# Exit 0 when the board in <a dir>/final.* has no unconnected item afterwards, 1 otherwise, 2 on a usage error.
# Env: FREEROUTING_JAR (required; one of the jars pinned in run_pcb.sh), FR_PASSES (default 60), FR_THREADS (default 4),
#      OUTER_ONLY and KEYFIRST as run_pcb.sh, PCB_PYTHON (default python3).
set -e
A=$1; LAYERS=${2:-4}; PLANES=${3:-inner}
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PCB_PYTHON:-python3}
[ -n "$A" ] || { sed -n 3,11p "$0"; exit 2; }
[ -f "$A/final.kicad_pcb" ] && [ -f "$A/drc_final.json" ] || { echo "no final.kicad_pcb and drc_final.json in $A"; exit 2; }
unconnected() { "$PY" -c 'import json, sys; print(len(json.load(open(sys.argv[1])).get("unconnected_items", [])))' "$1"; }
N1=$(unconnected "$A/drc_final.json")
if [ "$N1" = 0 ]; then echo "second pass: nothing open"; exit 0; fi
# the pinned jars: the one list in run_pcb.sh (plan 06 T5)
JAR_SHAS=$(sed -n 's/^ *JAR_SHAS="\(.*\)"$/\1/p' "$HERE/run_pcb.sh")
[ -n "$JAR_SHAS" ] || { echo "no JAR_SHAS line in run_pcb.sh"; exit 2; }
[ -n "$FREEROUTING_JAR" ] && [ -f "$FREEROUTING_JAR" ] || { echo "FREEROUTING_JAR: no such file: $FREEROUTING_JAR"; exit 1; }
JAR_HAVE=$(sha256sum "$FREEROUTING_JAR" | cut -d' ' -f1)
case " $JAR_SHAS " in *" $JAR_HAVE "*) ;; *) echo "FREEROUTING_JAR: sha256 is not the pinned $JAR_SHAS"; exit 1;; esac
export PYTHONPATH="$HERE/src${PYTHONPATH:+:$PYTHONPATH}"   # keep the packages that run_in_kicad.sh adds (KC_PYTHONPATH)
filter() { grep -v 'PROPERTY_ENUM' || true; }
R="$A/repass"
rm -rf "$R"; mkdir -p "$R"
for f in busy_light_spike.kicad_pro busy_light_spike.kicad_dru busy_light_spike.kicad_sch busy_light_spike.placement.json fp-lib-table; do
  \cp -f "$A/$f" "$R/"
done
[ -d "$A/CUSTOM.pretty" ] && \cp -rf "$A/CUSTOM.pretty" "$R/"
# KiCad reads the net classes of a board from the project file of the same name: without it the DSN has no power classes
proj() { for e in kicad_pro kicad_dru kicad_sch placement.json; do \cp -f "$R/busy_light_spike.$e" "$R/$1.$e"; done; }
T0=$(date +%s)
\cp -f "$A/final.kicad_pcb" "$R/in.kicad_pcb"
proj in
"$PY" "$HERE/src/pcb_dsn.py" lock "$R/in.kicad_pcb" "$R/in_locked.kicad_pcb" 2>&1 | filter
proj in_locked
"$PY" "$HERE/src/pcb_dsn.py" export "$R/in_locked.kicad_pcb" "$R/b.dsn" "$PLANES" 2>&1 | filter
if [ "${OUTER_ONLY:-1}" = 1 ]; then "$PY" "$HERE/src/pcb_dsn.py" outer "$R/b.dsn" "$R/b2.dsn" 2>&1 | filter && mv "$R/b2.dsn" "$R/b.dsn"; fi
if [ "${KEYFIRST:-0}" = 1 ]; then "$PY" "$HERE/src/pcb_dsn.py" branchwidth "$R/b.dsn" "$R/b2.dsn" 2>&1 | filter && mv "$R/b2.dsn" "$R/b.dsn"; fi
java -jar "$FREEROUTING_JAR" -de "$R/b.dsn" -do "$R/b.ses" -mp "${FR_PASSES:-60}" -mt "${FR_THREADS:-4}" > "$R/freerouting.log" 2>&1
WALL=$(( $(date +%s) - T0 ))
grep -E "Auto-routing stage completed" "$R/freerouting.log" | tail -1 | cut -c1-300
"$PY" "$HERE/src/pcb_dsn.py" import "$R/in_locked.kicad_pcb" "$R/b.ses" "$R/routed_locked.kicad_pcb" 2>&1 | filter
"$PY" "$HERE/src/pcb_dsn.py" unlock "$R/routed_locked.kicad_pcb" "$R/routed.kicad_pcb" 2>&1 | filter
proj routed
"$PY" - "$R/run_meta.json" "$(sha256sum "$R/in.kicad_pcb" | cut -d' ' -f1)" "$(sha256sum "$R/b.dsn" | cut -d' ' -f1)" "$(kicad-cli version)" \
  "$JAR_HAVE" "${FR_PASSES:-60}" "${FR_THREADS:-4}" "$(java -version 2>&1 | head -1)" "$WALL" "$PLANES" <<'PYEOF'
import sys
import pcb_replay
a = sys.argv[1:]
pcb_replay.write_meta(a[0], placed_board_sha256=a[1], dsn_sha256=a[2], kicad_version=a[3], jar_sha256=a[4],
                      fr_passes=int(a[5]), fr_threads=int(a[6]), java_version=a[7], wall_time_s=float(a[8]), planes=a[9])
PYEOF
"$PY" "$HERE/src/kicad_strict.py" drc "$R/routed.kicad_pcb" "routed-${LAYERS}l" --out "$R/drc_routed.json" > /dev/null 2>&1 || true
"$PY" "$HERE/src/pcb_stitch.py" "$R/routed.kicad_pcb" "$R/drc_routed.json" "$R/stitched.kicad_pcb" 2>&1 | filter | grep -E '^\{' || true
proj stitched
"$PY" "$HERE/src/kicad_strict.py" drc "$R/stitched.kicad_pcb" "stitched-${LAYERS}l" --out "$R/drc_stitched.json" > /dev/null 2>&1 || true
FINAL=$("$PY" "$HERE/src/pcb_fix.py" auto "$R" 2>&1 | filter | sed -n 's/.*"cleanup_final_board": "\(.*\)".*/\1/p' | tail -1)
FINAL=${FINAL:-stitched}
for e in kicad_pcb kicad_pro kicad_dru kicad_sch placement.json; do \cp -f "$R/$FINAL.$e" "$R/final.$e"; done
"$PY" "$HERE/src/kicad_strict.py" drc "$R/final.kicad_pcb" "stitched-${LAYERS}l" --out "$R/drc_final.json" > /dev/null 2>&1 || true
N2=$(unconnected "$R/drc_final.json")
echo "second pass: unconnected $N1 -> $N2 (from $FINAL)"
if [ "$N2" -lt "$N1" ]; then
  for e in kicad_pcb kicad_pro kicad_dru kicad_sch placement.json; do
    \cp -f "$A/final.$e" "$A/final_pass1.$e"; \cp -f "$R/final.$e" "$A/final.$e"
  done
  \cp -f "$A/drc_final.json" "$A/drc_final_pass1.json"; \cp -f "$R/drc_final.json" "$A/drc_final.json"
  echo "second pass: taken as $A/final.kicad_pcb"
fi
[ "$(unconnected "$A/drc_final.json")" = 0 ]
