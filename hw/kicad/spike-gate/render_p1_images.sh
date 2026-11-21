#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Export the README images of the stored P1 board and of its KiKit panel (plan 08; HW-008).
# Usage: render_p1_images.sh <board dir> <panel.kicad_pcb> <out dir>
#   <board dir>         hw/kicad/spike-gate/board-p1 (busy_light_spike.kicad_pcb, .kicad_sch and .kicad_pro)
#   <panel.kicad_pcb>   the panel of the order package: scripts/fab_p1.sh <board> <package dir> writes it
# Writes p1-schematic-gate-power.png, p1-schematic-mcu-leds.png, p1-pcb-layers.png, p1-pcb-top3d.png,
# p1-pcb-bottom3d.png and p1-panel-top3d.png.
# Needs kicad-cli (KiCad 10), pdftoppm (poppler) and ImageMagick (convert, montage) with the DejaVu Sans font.
# Images are tool exports; nothing is edited by hand. The 3D views have no component models for most parts and
# are not a fit check. Each 3D render takes about one minute.
set -eu
[ $# -eq 3 ] || { echo "usage: render_p1_images.sh <board dir> <panel.kicad_pcb> <out dir>" >&2; exit 2; }
IN=$1; PANEL=$2; OUT=$3
PCB="$IN/busy_light_spike.kicad_pcb"; SCH="$IN/busy_light_spike.kicad_sch"
for f in "$PCB" "$SCH" "$PANEL"; do [ -f "$f" ] || { echo "not found: $f" >&2; exit 2; }; done
for t in kicad-cli pdftoppm convert montage; do command -v "$t" >/dev/null || { echo "$t not found" >&2; exit 2; }; done
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
mkdir -p "$OUT"
FONT="-font DejaVu-Sans"

# Schematic: one A3 sheet, cut in two (power and gate above, MCU, button and LEDs below) in the middle of the white
# band of at least 40 pixel rows (4 mm) that is closest to 55 % of the drawing's height.
kicad-cli sch export pdf --exclude-drawing-sheet --no-background-color --exclude-pdf-property-popups \
  --exclude-pdf-metadata \
  -o "$T/sch.pdf" "$SCH" >/dev/null
pdftoppm -r 250 -png -singlefile "$T/sch.pdf" "$T/sch"
convert "$T/sch.png" -trim +repage "$T/sch_trim.png"
H=$(convert "$T/sch_trim.png" -format '%h' info:)
CUT=$(convert "$T/sch_trim.png" -colorspace Gray -scale "1x$H!" -depth 8 txt:- | awk -F'[,:() ]+' -v h="$H" '
  function band(e) { if (s >= 0 && e - s >= 40) { m = int((s + e) / 2); d = m - h * 0.55; if (d < 0) d = -d
                     if (best == "" || d < best) { best = d; cut = m } } }
  BEGIN { s = -1 }
  NR > 1 { if ($4 == 255) { if (s < 0) s = $2 } else { band($2); s = -1 } }
  END { band(h); print (cut == "" ? int(h * 0.55) : cut) }')
convert "$T/sch_trim.png" -crop "x$CUT+0+0" +repage -trim +repage -bordercolor white -border 20 -resize 3000x -strip \
  "$OUT/p1-schematic-gate-power.png"
convert "$T/sch_trim.png" -crop "x$((H - CUT))+0+$CUT" +repage -trim +repage -bordercolor white -border 20 \
  -resize 3000x -strip \
  "$OUT/p1-schematic-mcu-leds.png"

# Copper layers, each with the board outline, seen from the top; KiCad's default layer colours; 2 x 2 tiles.
kicad-cli pcb export pdf --mode-separate --layers F.Cu,In1.Cu,In2.Cu,B.Cu --common-layers Edge.Cuts \
  -o "$T/layers" "$PCB" >/dev/null
for l in F_Cu:F.Cu In1_Cu:"In1.Cu (GND plane)" In2_Cu:"In2.Cu (+5V plane)" B_Cu:"B.Cu (seen from the top)"; do
  f=${l%%:*}; label=${l#*:}
  pdftoppm -r 600 -png -singlefile "$T/layers/busy_light_spike-$f.pdf" "$T/$f"
  # shellcheck disable=SC2086
  convert "$T/$f.png" -trim +repage -bordercolor white -border 30 -gravity north -background white -splice 0x70 \
    $FONT -pointsize 44 -fill '#222222' -annotate +0+18 "$label" "$T/$f.l.png"
done
montage "$T/F_Cu.l.png" "$T/In1_Cu.l.png" "$T/In2_Cu.l.png" "$T/B_Cu.l.png" -tile 2x2 -geometry +10+10 \
  -background white "$T/layers.png"
convert "$T/layers.png" -resize 2000x -strip "$OUT/p1-pcb-layers.png"

# 3D views (raytraced), on white.
render() { # render <board> <side> <out>
  kicad-cli pcb render --side "$2" --width 2400 --height 2400 --quality high --background transparent \
    -o "$T/r.png" "$1" >/dev/null
  convert "$T/r.png" -background white -flatten -trim +repage -bordercolor white -border 20 -resize 1400x -strip "$3"
}
render "$PCB" top "$OUT/p1-pcb-top3d.png"
render "$PCB" bottom "$OUT/p1-pcb-bottom3d.png"
render "$PANEL" top "$OUT/p1-panel-top3d.png"
ls -l "$OUT"/p1-schematic-gate-power.png "$OUT"/p1-schematic-mcu-leds.png "$OUT"/p1-pcb-layers.png \
  "$OUT"/p1-pcb-top3d.png "$OUT"/p1-pcb-bottom3d.png "$OUT"/p1-panel-top3d.png
