#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Finish a routed run for storing (plan 08 section 4.4 and step R3; RV-019 G3): three pcb_finish.py passes, each from the unfinished
# board; pass 2 with the silkscreen findings of the DRC of pass 1, pass 3 with those of passes 1 and 2 merged; the strict DRC after each.
# Usage: run_finish.sh <a dir of the chosen run> <netlist dir written by run_full.sh> <work dir (new or removed first)>
# <a dir> is <out dir>/<name in best/chosen_run.txt>/a (it holds final.*, busy_light_spike.placement.json, run_meta.json and, after a second
# router pass, repass/run_meta.json). The work dir ends up with exactly the files that hw/kicad/spike-gate/board-p1/ holds (store_p1.sh copies
# them): busy_light_spike.{kicad_pcb,kicad_pro,kicad_dru,kicad_prl,kicad_sch,placement.json}, run_meta.json, repass_meta.json (when a second
# pass ran), the libraries, and drc1.json to drc3.json with their texts. The silkscreen identification is "busy-light P1 <git commit>" unless
# BOARD_ID is set. Needs pcbnew (the KiCad container); env PCB_PYTHON (default python3).
# Exit 0 when the finished board's strict DRC prints no FAIL line, 1 otherwise, 2 on a usage error.
set -e
A=$1; NETDIR=$2; W=$3
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PCB_PYTHON:-python3}
[ -n "$A" ] && [ -n "$NETDIR" ] && [ -n "$W" ] || { sed -n 3,14p "$0"; exit 2; }
for f in final.kicad_pcb final.kicad_pro final.kicad_dru final.kicad_prl busy_light_spike.placement.json run_meta.json; do
  [ -f "$A/$f" ] || { echo "run_finish: no $f in $A"; exit 2; }
done
for f in full.kicad_sch sym-lib-table fp-lib-table busylight_gate.kicad_sym; do
  [ -f "$NETDIR/$f" ] || { echo "run_finish: no $f in $NETDIR"; exit 2; }
done
[ -d "$NETDIR/CUSTOM.pretty" ] || { echo "run_finish: no CUSTOM.pretty in $NETDIR"; exit 2; }
rm -rf "$W"; mkdir -p "$W"
for e in kicad_pcb kicad_pro kicad_dru kicad_prl; do cp "$A/final.$e" "$W/busy_light_spike.$e"; done
cp "$A/busy_light_spike.placement.json" "$W/"
cp "$NETDIR/full.kicad_sch" "$W/busy_light_spike.kicad_sch"
cp -r "$NETDIR/CUSTOM.pretty" "$NETDIR/fp-lib-table" "$NETDIR/sym-lib-table" "$NETDIR/busylight_gate.kicad_sym" "$W/"
cp "$A/run_meta.json" "$W/run_meta.json"
[ -f "$A/repass/run_meta.json" ] && cp "$A/repass/run_meta.json" "$W/repass_meta.json"
B="$W/busy_light_spike.kicad_pcb"
cp "$B" "$W/unfinished.kicad_pcb"
drc() { "$PY" "$HERE/src/kicad_strict.py" drc "$B" stitched-4l --out "$W/drc$1.json" > "$W/drc$1.txt" 2>&1 || true; }
"$PY" "$HERE/src/pcb_finish.py" "$B" | tail -2
drc 1
cp "$W/unfinished.kicad_pcb" "$B"
"$PY" "$HERE/src/pcb_finish.py" "$B" "$W/drc1.json" | tail -2
drc 2
"$PY" "$HERE/src/merge_drc.py" "$W/drc1.json" "$W/drc2.json" "$W/drc12.json"
cp "$W/unfinished.kicad_pcb" "$B"
"$PY" "$HERE/src/pcb_finish.py" "$B" "$W/drc12.json" | tail -2
drc 3
rm -f "$W/unfinished.kicad_pcb" "$W/drc12.json"
for i in 1 2 3; do echo "pass $i:"; grep -E "FAIL|tolerated" "$W/drc$i.txt" | cut -c1-90 || true; done
if grep -q "FAIL" "$W/drc3.txt"; then echo "run_finish: the finished board has FAIL lines (drc3.txt)"; exit 1; fi
echo "run_finish: finished board in $W"
