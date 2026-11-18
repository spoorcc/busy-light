#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Build the P1 order package from a board (plan 08 sections 4.5 and 4.6; HW-008, HW-009).
#   scripts/fab_p1.sh <board.kicad_pcb> <out dir>
# Needs: kicad-cli and KiCad's Python (pcbnew) 10.0.x, KiKit 1.8.1 (scripts/requirements-fab.txt), git.
# The schematic <board>.kicad_sch must be next to the board (strict ERC, assembly BOM fields, full BOM).
# Every step runs even when an earlier one fails, so the package shows all findings. Exit codes: 0 every gate
# passed; 1 a gate failed (strict ERC or DRC, pcb_fabcheck, panel tab check, fab_check); 2 a tool or an
# input is missing, or the panel or the order files could not be made. The out dir must be empty or new.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STRICT="$ROOT/hw/kicad/spike-gate/src/kicad_strict.py"
FABCHECK="$ROOT/hw/kicad/spike-gate/src/pcb_fabcheck.py"
PRESET="$ROOT/scripts/panel_p1.json"
MISSING_LCSC="$ROOT/scripts/fab_missing_lcsc.txt"
# Mechanical azimuths of the panel tabs (scripts/panel_tabs.py explains the choice and the checks).
# P1: equal to hw/kicad/spike-gate/src/pcb_rules.py P1_TAB_AZIMUTHS (the placer keeps the LED capacitors away from these).
TAB_AZIMUTHS="${TAB_AZIMUTHS:-105,217.5,285,330}"

die() { echo "fab_p1: $*" >&2; exit 2; }
(($# == 2)) || die "usage: scripts/fab_p1.sh <board.kicad_pcb> <out dir>"
[[ -f "$1" && "$1" == *.kicad_pcb ]] || die "board not found: $1"
board="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
sch="${board%.kicad_pcb}.kicad_sch"
[[ -f "$sch" ]] || die "schematic not found next to the board: $sch"
if [[ -e "$2" && -n "$(ls -A "$2")" ]]; then die "out dir is not empty: $2"; fi
mkdir -p "$2"
out="$(cd "$2" && pwd)"
for tool in kicad-cli python3 git; do command -v "$tool" >/dev/null || die "$tool not found"; done
python3 -c 'import pcbnew, kikit' 2>/dev/null || die "pcbnew or kikit is not importable by python3"
cd "$ROOT"
rel() { realpath --relative-to="$ROOT" "$1"; } # repository-relative paths in reports and the manifest
board_rel="$(rel "$board")"
sch_rel="$(rel "$sch")"
stem="$(basename "${board%.kicad_pcb}")"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

failed=()
blocked=()
# run NAME LOG CMD...: run a step, keep its output in LOG (in the package) and on the console.
run() {
  local name="$1" log="$2" rc=0
  shift 2
  echo "== $name"
  "$@" >"$log" 2>&1 || rc=$?
  cat "$log"
  if ((rc != 0)); then
    echo "   -> $name: exit $rc"
    failed+=("$name")
  fi
  return $rc
}
kikit() { python3 -m kikit.ui "$@" 2>&1 | grep -v -e 'Debug: Adding duplicate image handler' -e 'swig/python detected a memory leak'; return "${PIPESTATUS[0]}"; }

kicad_version="$(kicad-cli version)"
kikit_version="$(python3 -c 'import kikit; print(kikit.__version__)')"
git_describe="$(git describe --always --dirty)"
echo "fab_p1: board $board_rel, KiCad $kicad_version, KiKit $kikit_version, source $git_describe"

# 1. Strict gate of the board (profile and waivers as in scripts/ci_hw.sh) and the fabricator minimums.
run "strict ERC" "$out/erc.txt" env SPIKE_ALLOW_KNOWN_OPEN=0 python3 "$STRICT" erc "$sch_rel" full --out "$out/erc.json" || true
run "strict DRC" "$out/drc.txt" env SPIKE_ALLOW_KNOWN_OPEN=0 python3 "$STRICT" drc "$board_rel" stitched-4l --out "$out/drc.json" || true
echo "== pcb_fabcheck"
rc=0
python3 "$FABCHECK" "$board_rel" >"$out/pcb_fabcheck.json" || rc=$?
cat "$out/pcb_fabcheck.json"
((rc == 0)) || { echo "   -> pcb_fabcheck: exit $rc"; failed+=("pcb_fabcheck"); }

# 2. Panel: tab annotations on a copy of the board, then KiKit (scripts/panel_p1.json).
mkdir -p "$work/tabbed" "$work/panel" "$work/fab"
for ext in kicad_pro kicad_dru; do
  if [[ -f "${board%.kicad_pcb}.$ext" ]]; then cp "${board%.kicad_pcb}.$ext" "$work/tabbed/"; fi
done
echo "== panel tabs ($TAB_AZIMUTHS deg)"
rc=0
python3 scripts/panel_tabs.py "$board_rel" "$work/tabbed/$stem.kicad_pcb" --azimuths "$TAB_AZIMUTHS" \
  --report "$out/panel_tabs.json" >/dev/null || rc=$?
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["verdict"]); [print("  " + f) for f in d["failures"]]' \
  "$out/panel_tabs.json" || rc=2
((rc == 0)) || { echo "   -> panel tabs: exit $rc"; failed+=("panel tabs"); }
cp "$PRESET" "$out/panel_p1.json"
if run "kikit panelize" "$work/panelize.log" kikit panelize -p "$PRESET" "$work/tabbed/$stem.kicad_pcb" "$work/panel/panel.kicad_pcb"; then
  cp "$work/panel/panel.kicad_pcb" "$out/panel.kicad_pcb"
  # 3. Order files from the panel, so Gerbers, drill, BOM and CPL share one origin.
  ignore="$(python3 scripts/fab_package.py ignore-refs "$board_rel")"
  if run "kikit fab jlcpcb" "$work/fab.log" kikit fab jlcpcb --no-drc --assembly --schematic "$sch_rel" --field LCSC \
    --ignore "$ignore" "$work/panel/panel.kicad_pcb" "$work/fab"; then
    cp "$work/fab/gerbers.zip" "$out/gerbers.zip"
    cp "$work/fab/bom.csv" "$out/jlcpcb_bom.csv"
    cp "$work/fab/pos.csv" "$out/jlcpcb_cpl.csv"
    grep -e WARNING "$work/fab.log" >"$out/kikit_fab_warnings.txt" || true
  else
    blocked+=("kikit fab jlcpcb")
  fi
else
  blocked+=("kikit panelize")
fi

# 4. Assembly drawing (top side, scaled to the page, values left out for legibility, DNP parts crossed out)
#    and full BOM of the board (every part, DNP marked).
run "assembly PDF" "$work/pdf.log" kicad-cli pcb export pdf --layers F.Fab,F.SilkS,Edge.Cuts --mode-single \
  --scale 0 --exclude-value --crossout-DNP-footprints-on-fab-layers -o "$out/assembly.pdf" "$board_rel" ||
  blocked+=("assembly PDF")
# shellcheck disable=SC2016 # ${DNP} and ${QUANTITY} are kicad-cli field names, not shell variables
if run "full BOM" "$work/bom.log" kicad-cli sch export bom -o "$work/bom_full_raw.csv" \
  --fields 'Reference,Value,Footprint,${DNP},MPN,Manufacturer,LCSC,${QUANTITY}' \
  --labels 'Refs,Value,Footprint,DNP,MPN,Manufacturer,LCSC,Qty' \
  --group-by 'Value,Footprint,${DNP},MPN,Manufacturer,LCSC' --ref-range-delimiter '' "$sch_rel"; then
  python3 scripts/fab_package.py full-bom "$work/bom_full_raw.csv" "$out/bom_full.csv"
else
  blocked+=("full BOM")
fi

# 5. Order checks (missing LCSC numbers: the committed list, printed in the release notes).
cp "$MISSING_LCSC" "$out/fab_missing_lcsc.txt"
if [[ -f "$out/jlcpcb_bom.csv" ]]; then
  run "fab_check" "$out/fab_check.txt" python3 scripts/fab_check.py "$out" "$board_rel" \
    --missing-lcsc-file "$(rel "$MISSING_LCSC")" || true
fi

# 6. Manifest last: it hashes every file of the package.
python3 scripts/fab_package.py manifest "$out" --git-describe "$git_describe" \
  --tool "kicad=$kicad_version" --tool "kikit=$kikit_version" \
  --input "board=$board_rel" --input "schematic=$sch_rel" --input "panel_json=$(rel "$PRESET")" \
  --input "missing_lcsc_list=$(rel "$MISSING_LCSC")"

echo "== fab_p1 summary: package in $out"
if ((${#blocked[@]})); then
  echo "NOT MADE: ${blocked[*]}"
  exit 2
fi
if ((${#failed[@]})); then
  echo "FAILED: ${failed[*]}"
  exit 1
fi
echo "all gates passed"
