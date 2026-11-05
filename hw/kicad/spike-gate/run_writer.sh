#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Netlist with SKiDL, schematic with the own deterministic writer, then ERC + parity.
# Usage: run_writer.sh <python> <out dir>   (no retry loop needed: the writer is deterministic)
PY=$1; OUT=$2; HERE=$(dirname "$0")
rm -rf "$OUT"; mkdir -p "$OUT"
"$PY" "$HERE/src/gen_gate.py" "$OUT" --netlist-only >"$OUT/gen.log" 2>&1 || { echo "netlist FAIL"; exit 1; }
"$PY" "$HERE/src/write_sch.py" "$OUT/gate.net" "$OUT/gate.kicad_sch" && "$PY" "$HERE/src/check_gate.py" "$OUT"
