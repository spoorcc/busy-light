#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Generate the gate fragment and check it. Usage: run_gate.sh <python> <out dir>
# The SKiDL schematic writer is not deterministic and sometimes drops a pin: regenerate until
# the ERC and parity checks pass (at most 10 tries) and report how many tries it needed.
PY=$1; OUT=$2; HERE=$(dirname "$0")
n=0
while [ $n -lt 10 ]; do
  n=$((n+1)); rm -rf "$OUT"; mkdir -p "$OUT"
  "$PY" "$HERE/src/gen_gate.py" "$OUT" >"$OUT/gen.log" 2>&1 || continue
  [ -f "$OUT/gate.kicad_sch" ] || continue
  if "$PY" "$HERE/src/check_gate.py" "$OUT"; then echo "pass after $n generation(s)"; exit 0; fi
done
echo "FAIL after $n generations"; exit 1
