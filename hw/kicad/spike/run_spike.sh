#!/usr/bin/env bash
# Spike: generate schematic and PCB twice into temp dirs, check ERC, DRC-run, requirement fields, reproducibility.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PY:-python3}"
run() {  # $1 = output dir
  mkdir -p "$1"; cp "$HERE/libs/"*-lib-table "$HERE/libs/spike.kicad_pro" "$1/"
  "$PY" "$HERE/src/gen_schematic.py" "$1"
  kicad-cli sch export netlist --format kicadsexpr --output "$1/spike.net" "$1/spike.kicad_sch" >/dev/null
  PYTHONPATH="$HERE/src" "$PY" "$HERE/src/gen_pcb.py" "$1/spike.net" "$1/spike.kicad_pcb" 2>&1 | grep -v assert
  cp "$HERE/libs/spike.kicad_pro" "$1/"   # pcbnew overwrites the project file when it saves a board: restore the reviewed rules
  PYTHONPATH="$HERE/src" "$PY" "$HERE/src/dump_design.py" "$1/spike.net" "$1/spike.kicad_pcb" 2>/dev/null > "$1/dump.json"
}
G1=0
A="$(mktemp -d)"; B="$(mktemp -d)"
run "$A"; run "$B"
echo "== ERC"; kicad-cli sch erc --severity-all --exit-code-violations --output "$A/erc.rpt" "$A/spike.kicad_sch"
echo "== requirement fields"; PYTHONPATH="$HERE/src" "$PY" "$HERE/src/check_req_fields.py" "$A/dump.json"
echo "== semantic equality of two runs"; diff -q "$A/dump.json" "$B/dump.json" && echo "semantic dumps identical"
echo "== schematic byte equality of two runs"; cmp "$A/spike.kicad_sch" "$B/spike.kicad_sch" && echo "schematic bytes identical" || echo "schematic bytes differ"
echo "== DRC (run only; routing not done)"; kicad-cli pcb drc --severity-all --schematic-parity --output "$A/drc.rpt" "$A/spike.kicad_pcb" | tail -2
if [[ -n "${FREEROUTING_JAR:-}" ]]; then
  echo "== Freerouting (scripted) and DRC of the routed board"
  PYTHONPATH="$HERE/src" "$PY" "$HERE/src/route_freerouting.py" "$A/spike.kicad_pcb" "$A/routed.kicad_pcb" "$FREEROUTING_JAR" "$FREEROUTING_SHA256" 2>&1 | grep -v assert
  cp "$A/spike.kicad_sch" "$A/routed.kicad_sch"; cp "$A/spike.kicad_pro" "$A/routed.kicad_pro"
  kicad-cli pcb drc --severity-all --schematic-parity --output "$A/routed-drc.rpt" "$A/routed.kicad_pcb" | tail -3
  grep "^\[" "$A/routed-drc.rpt" | sed 's/\].*//' | sort | uniq -c || true
  N="$(grep -c "^\[" "$A/routed-drc.rpt" || true)"
  echo "G1 routed DRC: ${N} violation lines (criterion: 0)"; [[ "$N" == "0" ]] || G1=1
else
  echo "== Freerouting NOT RUN (set FREEROUTING_JAR and FREEROUTING_SHA256)"
fi
if [[ -n "${HOUSING_DIR:-}" ]]; then
  echo "== FreeCAD fit check (board STEP vs housing STEP)"
  KICAD10_3DMODEL_DIR=/usr/share/kicad/3dmodels kicad-cli pcb export step --subst-models --output "$A/board.step" "$A/spike.kicad_pcb" >/dev/null
  echo "import sys; sys.argv=['x','$A/board.step','$HOUSING_DIR','$HERE/src/params.toml','$HOUSING_SCRIPT','$A/fit.json']; exec(open('$HERE/src/freecad_fit.py').read())" \
    | QT_QPA_PLATFORM=offscreen timeout 300 freecad -c 2>&1 | grep -E "PASS|FAIL|RESULT|board bbox" || true
else
  echo "== FreeCAD fit check NOT RUN (set HOUSING_DIR and HOUSING_SCRIPT)"
fi
echo "outputs: $A"
exit "$G1"
