#!/usr/bin/env bash
# Spike: generate schematic and PCB twice into temp dirs, check ERC, DRC-run, requirement fields, reproducibility.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PY:-python3}"
run() {  # $1 = output dir
  mkdir -p "$1"; cp "$HERE/libs/"*-lib-table "$1/"; echo '{}' > "$1/spike.kicad_pro"
  "$PY" "$HERE/src/gen_schematic.py" "$1"
  kicad-cli sch export netlist --format kicadsexpr --output "$1/spike.net" "$1/spike.kicad_sch" >/dev/null
  PYTHONPATH="$HERE/src" "$PY" "$HERE/src/gen_pcb.py" "$1/spike.net" "$1/spike.kicad_pcb" 2>&1 | grep -v assert
  PYTHONPATH="$HERE/src" "$PY" "$HERE/src/dump_design.py" "$1/spike.net" "$1/spike.kicad_pcb" 2>/dev/null > "$1/dump.json"
}
A="$(mktemp -d)"; B="$(mktemp -d)"
run "$A"; run "$B"
echo "== ERC"; kicad-cli sch erc --severity-all --exit-code-violations --output "$A/erc.rpt" "$A/spike.kicad_sch"
echo "== requirement fields"; PYTHONPATH="$HERE/src" "$PY" "$HERE/src/check_req_fields.py" "$A/dump.json"
echo "== semantic equality of two runs"; diff -q "$A/dump.json" "$B/dump.json" && echo "semantic dumps identical"
echo "== schematic byte equality of two runs"; cmp "$A/spike.kicad_sch" "$B/spike.kicad_sch" && echo "schematic bytes identical" || echo "schematic bytes differ"
echo "== DRC (run only; routing not done)"; kicad-cli pcb drc --severity-all --schematic-parity --output "$A/drc.rpt" "$A/spike.kicad_pcb" | tail -2
echo "outputs: $A"
