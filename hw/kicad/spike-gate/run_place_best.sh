#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Placements only, no router (plan 08 R2a; RV-019 pass 3, S4): N placements in parallel with the seed groups of run_best.sh, then a
# table of their placement-rule misses. A placement with a miss is not routed (plan 08 R2). Needs pcbnew (the KiCad container).
# Usage: run_place_best.sh <dir written by run_full.sh> <out dir> [runs, default 4] [layers, default 4]
# Env: as run_pcb.sh and pcb_full.py (P1, PLACE_*, SEED_OFFSET, PLACE_RULE_PEN); PCB_PYTHON (default python3).
# Each placement is in <out dir>/placeI/ (the dir that run_pcb.sh would call a/). Exit 0 when at least one has no overlap and no miss.
IN=$1; OUT=$2; N=${3:-4}; LAYERS=${4:-4}
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PCB_PYTHON:-python3}
[ -n "$IN" ] && [ -n "$OUT" ] || { sed -n 3,8p "$0"; exit 2; }
[ -f "$IN/kicad.net" ] || { echo "no $IN/kicad.net (run run_full.sh first)"; exit 1; }
export PYTHONPATH="$HERE/src${PYTHONPATH:+:$PYTHONPATH}"
mkdir -p "$OUT"
i=1
while [ "$i" -le "$N" ]; do
  PLACE_SEED_START=$(( (i - 1) * 16 + 1 + ${SEED_OFFSET:-0} )) "$PY" "$HERE/src/pcb_full.py" "$IN/kicad.net" "$OUT/place$i" busy_light_spike "$LAYERS" > "$OUT/place$i.log" 2>&1 &
  i=$((i + 1))
done
wait
dirs=""
i=1
while [ "$i" -le "$N" ]; do dirs="$dirs $OUT/place$i"; i=$((i + 1)); done
# shellcheck disable=SC2086
"$PY" "$HERE/src/place_table.py" $dirs
