#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Spike: export the README images (schematic in two crops, board layers, board 3D view) from a routed and stitched spike board.
# Usage: render_readme_images.sh <board dir> <out dir>
#   <board dir> holds stitched.kicad_pcb, stitched.kicad_pro and stitched.kicad_sch. Make it with:
#     run_full.sh (netlist and schematic), run_pcb.sh <full dir> <dir> 4 (placement, Freerouting, DRC), then
#     src/pcb_stitch.py <dir>/a/routed.kicad_pcb <dir>/a/drc_routed.json <dir>/a/stitched.kicad_pcb
#     and copy the .kicad_pro and routed.kicad_sch next to it under the stitched names.
# Needs kicad-cli (KiCad 10), rsvg-convert and ImageMagick. Images are tool exports; nothing is edited by hand.
# The routing is not deterministic (Freerouting), so the numbers in the README captions belong to one run.
set -e
IN=$1; OUT=$2
[ -f "$IN/stitched.kicad_pcb" ] && [ -f "$IN/stitched.kicad_sch" ] || { echo "need stitched.kicad_pcb and .kicad_sch in $IN"; exit 1; }
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
mkdir -p "$OUT"
kicad-cli sch export svg --exclude-drawing-sheet -o "$T/sch" "$IN/stitched.kicad_sch"
rsvg-convert -w 3000 -b white "$T/sch/stitched.svg" -o "$T/sch.png"
kicad-cli pcb export svg --mode-single --layers "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Silkscreen,Edge.Cuts" \
  --exclude-drawing-sheet --page-size-mode 2 -o "$T/layers.svg" "$IN/stitched.kicad_pcb"
rsvg-convert -w 2400 -b white "$T/layers.svg" -o "$T/layers.png"
kicad-cli pcb render --side top --width 2400 --height 1800 --quality high --background opaque \
  -o "$T/top3d.png" "$IN/stitched.kicad_pcb"
# The sheet is one dense A3 page. Two fixed crops (pixel boxes of the 3000 px wide export) keep the text legible in the README:
# gate and power path (USB-C, CC detection, current-step gate, hold-off, regulator) and MCU, button and LED chain.
convert "$T/sch.png" -crop 2700x1160+60+40 +repage -strip "$OUT/spike-schematic-gate-power.png"
convert "$T/sch.png" -crop 2790x820+60+1200 +repage -strip "$OUT/spike-schematic-mcu-leds.png"
convert "$T/layers.png" -strip "$OUT/spike-pcb-4layer-layers.png"
convert "$T/top3d.png" -resize 1600x -strip "$OUT/spike-pcb-4layer-top3d.png"
ls -l "$OUT"/spike-schematic-gate-power.png "$OUT"/spike-schematic-mcu-leds.png "$OUT"/spike-pcb-4layer-layers.png "$OUT"/spike-pcb-4layer-top3d.png
