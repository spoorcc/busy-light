#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Draw the full-board sheet, compare the drawn nets with the intent table, ERC, determinism.
# Usage: run_full.sh <python> <out dir>
PY=$1; OUT=$2; HERE=$(dirname "$0")
rm -rf "$OUT"; mkdir -p "$OUT"
"$PY" "$HERE/src/layout_full.py" "$OUT/full.kicad_sch" "$OUT/intent.json" || exit 1
"$PY" "$HERE/src/check_full.py" "$OUT" || exit 1
"$PY" "$HERE/src/layout_full.py" "$OUT/second.kicad_sch" || exit 1
cmp "$OUT/full.kicad_sch" "$OUT/second.kicad_sch" && echo "deterministic: identical" || exit 1
