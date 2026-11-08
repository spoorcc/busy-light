#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Several routing runs in parallel, then keep the best (Freerouting is not deterministic; see src/pcb_pick.py).
# Usage: run_best.sh <dir written by run_full.sh> <out dir> [runs, default 6] [layers, default 4] [planes, default inner]
# Env: as run_pcb.sh (FREEROUTING_JAR, PCB_PYTHON, SPIKE_ALLOW_KNOWN_OPEN, ...); KEYFIRST defaults to 1 here.
# The winner is in <out dir>/best/ (final.kicad_pcb, drc_final.json, chosen_run.txt). Exit 0 when it has no
# unconnected item and no hard DRC finding.
IN=$1; OUT=$2; N=${3:-6}; LAYERS=${4:-4}; PLANES=${5:-inner}
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PCB_PYTHON:-python3}
[ -n "$IN" ] && [ -n "$OUT" ] || { sed -n 3,8p "$0"; exit 2; }
export KEYFIRST=${KEYFIRST:-1}
mkdir -p "$OUT"
i=1
while [ "$i" -le "$N" ]; do
  sh "$HERE/run_pcb.sh" "$IN" "$OUT/run$i" "$LAYERS" "$PLANES" > "$OUT/run$i.log" 2>&1 &
  i=$((i + 1))
done
wait
runs=""
i=1
while [ "$i" -le "$N" ]; do runs="$runs $OUT/run$i"; i=$((i + 1)); done
# shellcheck disable=SC2086
"$PY" "$HERE/src/pcb_pick.py" "$OUT" $runs
