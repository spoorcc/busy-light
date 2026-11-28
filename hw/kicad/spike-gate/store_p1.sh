#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Store a finished board as board-p1 (plan 08 step R5; RV-019 G3). Usage: store_p1.sh <work dir of run_finish.sh> [target dir]
# The target (default: board-p1 next to this script; env BOARD_P1_DIR overrides) keeps its README.md; every other file of the old board is
# replaced by the files of the work dir (the board, project, rules, schematic, placement json, libraries, run_meta.json, and repass_meta.json
# when it exists). The DRC reports of the finishing passes are copied as drc_pass1.json to drc_pass3.json (HW-009). Exit 2 on a missing file.
set -e
W=$1
HERE=$(cd "$(dirname "$0")" && pwd)
T=${2:-${BOARD_P1_DIR:-$HERE/board-p1}}
[ -n "$W" ] || { sed -n 3,6p "$0"; exit 2; }
for f in busy_light_spike.kicad_pcb busy_light_spike.kicad_pro busy_light_spike.kicad_dru busy_light_spike.kicad_sch \
         busy_light_spike.placement.json run_meta.json fp-lib-table sym-lib-table busylight_gate.kicad_sym drc1.json drc2.json drc3.json; do
  [ -f "$W/$f" ] || { echo "store_p1: no $f in $W"; exit 2; }
done
[ -d "$W/CUSTOM.pretty" ] || { echo "store_p1: no CUSTOM.pretty in $W"; exit 2; }
mkdir -p "$T"
for f in "$T"/*; do [ -e "$f" ] || continue; [ "$(basename "$f")" = README.md ] || rm -rf "$f"; done
for f in busy_light_spike.kicad_pcb busy_light_spike.kicad_pro busy_light_spike.kicad_dru busy_light_spike.kicad_sch \
         busy_light_spike.placement.json run_meta.json fp-lib-table sym-lib-table busylight_gate.kicad_sym; do cp "$W/$f" "$T/"; done
[ -f "$W/busy_light_spike.kicad_prl" ] && cp "$W/busy_light_spike.kicad_prl" "$T/"   # git-ignored KiCad side file; optional
[ -f "$W/repass_meta.json" ] && cp "$W/repass_meta.json" "$T/"
cp -r "$W/CUSTOM.pretty" "$T/"
for i in 1 2 3; do cp "$W/drc$i.json" "$T/drc_pass$i.json"; done
echo "store_p1: stored $W in $T"
