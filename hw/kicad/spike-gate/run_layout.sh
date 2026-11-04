#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Netlist with SKiDL, hand-laid-out schematic with layout_sch.py, then ERC + parity, then a
# determinism check (second run must be byte-identical). Usage: run_layout.sh <python> <out dir>
PY=$1; OUT=$2; HERE=$(dirname "$0")
rm -rf "$OUT"; mkdir -p "$OUT"
"$PY" "$HERE/src/gen_gate.py" "$OUT" --netlist-only >"$OUT/gen.log" 2>&1 || { echo "netlist FAIL"; exit 1; }
"$PY" "$HERE/src/layout_sch.py" "$OUT/gate.net" "$OUT/gate.kicad_sch" || exit 1
"$PY" "$HERE/src/check_gate.py" "$OUT" || exit 1
"$PY" "$HERE/src/layout_sch.py" "$OUT/gate.net" "$OUT/second.kicad_sch" || exit 1
cmp "$OUT/gate.kicad_sch" "$OUT/second.kicad_sch" && echo "deterministic: identical" || exit 1
