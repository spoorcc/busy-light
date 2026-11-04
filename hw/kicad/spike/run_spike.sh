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
  PYTHONPATH="$HERE/src" "$PY" "$HERE/src/dump_design.py" "$1/spike.net" "$1/spike.kicad_pcb" "$1/spike.kicad_pro" 2>/dev/null > "$1/dump.json"
}
G1=0
A="$(mktemp -d)"; B="$(mktemp -d)"
run "$A"; run "$B"
echo "== ERC"; kicad-cli sch erc --severity-all --exit-code-violations --output "$A/erc.rpt" "$A/spike.kicad_sch"
echo "== requirement fields"; PYTHONPATH="$HERE/src" "$PY" "$HERE/src/check_req_fields.py" "$A/dump.json"
echo "== semantic equality of two runs"; diff -q "$A/dump.json" "$B/dump.json" && echo "semantic dumps identical"
echo "== schematic byte equality of two runs"; cmp "$A/spike.kicad_sch" "$B/spike.kicad_sch" && echo "schematic bytes identical" || echo "schematic bytes differ"
echo "== DRC (run only; routing not done)"; kicad-cli pcb drc --severity-all --schematic-parity --output "$A/drc.rpt" "$A/spike.kicad_pcb" | tail -2
dump_routed() { PYTHONPATH="$HERE/src" "$PY" "$HERE/src/dump_design.py" "$1/spike.net" "$1/routed.kicad_pcb" "$1/routed.kicad_pro" 2>/dev/null > "$2"; }
finish() { cp "$1/spike.kicad_sch" "$1/routed.kicad_sch"; cp "$HERE/libs/spike.kicad_pro" "$1/routed.kicad_pro"; }
if [[ -n "${FREEROUTING_JAR:-}" ]]; then
  echo "== Freerouting (scripted) and DRC of the routed board"
  PYTHONPATH="$HERE/src" "$PY" "$HERE/src/route_freerouting.py" "$A/spike.kicad_pcb" "$A/routed.kicad_pcb" "$FREEROUTING_JAR" "$FREEROUTING_SHA256" 2>&1 | grep -v assert
  finish "$A"; dump_routed "$A" "$A/routed.dump.json"
  kicad-cli pcb drc --severity-all --schematic-parity --output "$A/routed-drc.rpt" "$A/routed.kicad_pcb" | tail -3
  grep "^\[" "$A/routed-drc.rpt" | sed 's/\].*//' | sort | uniq -c || true
  N="$(grep -c "^\[" "$A/routed-drc.rpt" || true)"
  echo "G1 routed DRC: ${N} violation lines (criterion: 0)"; [[ "$N" == "0" ]] || G1=1
  echo "== second router run (information: Freerouting is not deterministic)"
  PYTHONPATH="$HERE/src" "$PY" "$HERE/src/route_freerouting.py" "$B/spike.kicad_pcb" "$B/routed.kicad_pcb" "$FREEROUTING_JAR" "$FREEROUTING_SHA256" 2>&1 | grep -v assert
  finish "$B"; dump_routed "$B" "$B/routed.dump.json"
  diff -q "$A/routed.dump.json" "$B/routed.dump.json" >/dev/null && echo "two router runs: identical" || echo "two router runs: DIFFER (the stored session is the input, not the router run)"
  if [[ "${UPDATE_EXPECTED:-0}" == "1" ]]; then
    cp "$A/routed.kicad_pcb.ses" "$HERE/expected/routed.ses"; cp "$A/routed.dump.json" "$HERE/expected/routed.dump.json"; echo "expected session and dump updated"
  fi
fi
if [[ -f "$HERE/expected/routed.ses" ]]; then
  echo "== regeneration gate: import the stored session, dump must equal the committed dump"
  C="$(mktemp -d)"; cp "$A"/spike.* "$A"/*lib-table "$C/"
  PYTHONPATH="$HERE/src" "$PY" "$HERE/src/route_freerouting.py" "$C/spike.kicad_pcb" "$C/routed.kicad_pcb" "" "" "$HERE/expected/routed.ses" 2>&1 | grep -v assert || true
  finish "$C"; dump_routed "$C" "$C/routed.dump.json"
  diff -q "$C/routed.dump.json" "$HERE/expected/routed.dump.json" && echo "matches committed dump" || { echo "DIFFERS from committed dump"; G1=1; }
  kicad-cli pcb drc --severity-all --schematic-parity --output "$C/gate-drc.rpt" "$C/routed.kicad_pcb" | tail -3
else
  echo "== regeneration gate NOT RUN (no expected/routed.ses)"
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
