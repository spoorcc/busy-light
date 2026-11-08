# SPDX-License-Identifier: Apache-2.0
"""Generated footprint library CUSTOM of the spike (plan 06 A-11): the TUSB321 RWB X2QFN-12 land pattern.

The KiCad system libraries have no X2QFN footprint. The land pattern is read from the TI drawing RWB0012A, "Example
board layout" (tusb321.pdf SLLSEZ, drawing page 23, read as an image 2026-11-07): pads 1, 2 (left) and 7, 8 (right) are
0.7 x 0.2 at x = -/+0.65, y = -/+0.2 (pitch 0.4); pads 3 to 6 (bottom) and 9 to 12 (top) are 0.2 x 0.5 at y = +/-0.75,
x = -0.6 to +0.6 (pitch 0.4). Numbering runs counter-clockwise from the top of the left side. The drawing is an
example, not a mandatory pattern; the board house and the paste stencil are not checked. Pure Python, deterministic (uuid5 of fixed keys). Used by the schematic generators (footprint link
check of ERC) and by pcb_full (the board loads this file, so board and library cannot differ).
"""
from __future__ import annotations

import uuid
from pathlib import Path

NICK = "CUSTOM"
NAME = "X2QFN-12_RWB"
_NS = uuid.UUID("5b0c2f0e-0000-4000-8000-00000000c0f9")
COURTYARD = 1.15      # pads reach 1.0 mm from the centre; 0.15 mm margin


def pads() -> list[tuple[str, float, float, float, float]]:
    """(number, x, y, width, height) in mm, in file order."""
    p = [("1", -0.65, -0.2, 0.7, 0.2), ("2", -0.65, 0.2, 0.7, 0.2)]
    p += [(str(3 + i), x, 0.75, 0.2, 0.5) for i, x in enumerate((-0.6, -0.2, 0.2, 0.6))]
    p += [("7", 0.65, 0.2, 0.7, 0.2), ("8", 0.65, -0.2, 0.7, 0.2)]
    p += [(str(9 + i), x, -0.75, 0.2, 0.5) for i, x in enumerate((0.6, 0.2, -0.2, -0.6))]
    return p


def _id(key: str) -> str:
    return str(uuid.uuid5(_NS, key))


def kicad_mod() -> str:
    L = [f'(footprint "{NAME}"', "\t(version 20240108)", '\t(generator "busy-light-custom_fp")', '\t(layer "F.Cu")',
         '\t(descr "TUSB321 RWB X2QFN-12, land pattern of drawing RWB0012A")']
    for key, val, layer, hide in (("Reference", "REF**", "F.SilkS", False), ("Value", NAME, "F.Fab", False)):
        L.append(f'\t(property "{key}" "{val}"\n\t\t(at 0 0 0)\n\t\t(layer "{layer}")\n\t\t(uuid "{_id(key)}")\n'
                 '\t\t(effects (font (size 1.27 1.27)))\n\t)')
    L.append("\t(attr smd)")
    c = COURTYARD
    L.append(f'\t(fp_rect (start {-c} {-c}) (end {c} {c}) (stroke (width 0.05) (type default)) (fill no) '
             f'(layer "F.CrtYd") (uuid "{_id("crtyd")}"))')
    for num, x, y, w, h in pads():
        L.append(f'\t(pad "{num}" smd rect (at {x} {y}) (size {w} {h}) (layers "F.Cu" "F.Mask" "F.Paste") '
                 f'(uuid "{_id("pad" + num)}"))')
    L.append(")")
    return "\n".join(L) + "\n"


U9_NAME = "ESP32-C3-MINI-1"


def _drop_blocks(text: str, head: str) -> str:
    """Remove every s-expression that starts with `head` (balanced parentheses, quotes respected)."""
    out, i = [], 0
    while True:
        j = text.find(head, i)
        if j < 0:
            out.append(text[i:])
            return "".join(out)
        k, depth, quoted = j, 0, False
        while True:
            c = text[k]
            if quoted:
                quoted = c != '"' or text[k - 1] == "\\"
            elif c == '"':
                quoted = True
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        cut = j
        while cut > i and text[cut - 1] in " \t":      # the indent of the removed block
            cut -= 1
        out.append(text[i:cut])
        i = k + 1
        if text[i:i + 1] == "\n":
            i += 1


def u9_mod(stock_text: str) -> str:
    """The ESP32-C3-MINI-1 footprint text: the stock ESP32-C6-MINI-1 footprint (same land pattern, datasheet figure 11-1
    of the C3 module) without its keep-out zone and 3D model, renamed."""
    t = stock_text.replace("ESP32-C6-MINI-1", U9_NAME)
    return _drop_blocks(_drop_blocks(t, "(zone"), "(model")


J1_STOCK = "USB_C_Receptacle_GCT_USB4085"
J1_NAME = "USB_C_Receptacle_GCT_USB4085_edge"
# the silk lines of the connector front (local coordinates): the front of the receptacle lies at the board edge of the tab,
# so these three lines are clipped by the edge (silk_edge_clearance, 2026-11-08); the owner declined a silk waiver (DEV-006)
J1_SILK_DROP = (((-1.62, 6.0), (-1.62, 8.73)), ((7.57, 6.0), (7.57, 8.73)), ((-1.62, 8.73), (7.57, 8.73)))


def j1_mod(stock_text: str) -> str:
    """The J1 footprint text: the stock GCT USB4085 footprint without the three silk lines of J1_SILK_DROP, renamed."""
    import re
    t = stock_text.replace('"%s"' % J1_STOCK, '"%s"' % J1_NAME)
    pos = 0
    while True:
        i = t.find("(fp_line", pos)
        if i < 0:
            break
        depth, k = 0, i
        while True:                                        # end of the balanced block
            depth += (t[k] == "(") - (t[k] == ")")
            if depth == 0:
                break
            k += 1
        blk = t[i:k + 1]
        m = re.search(r"\(start ([-\d.]+) ([-\d.]+)\)\s*\(end ([-\d.]+) ([-\d.]+)\)", blk)
        a, e = (float(m.group(1)), float(m.group(2))), (float(m.group(3)), float(m.group(4)))
        if '"F.SilkS"' in blk and any((a, e) == pair or (e, a) == pair for pair in J1_SILK_DROP):
            cut = i
            while cut > 0 and t[cut - 1] in " \t":
                cut -= 1
            end = k + 1 + (t[k + 1:k + 2] == "\n")
            t = t[:cut] + t[end:]
            pos = cut
        else:
            pos = k + 1
    return t


def write_library(outdir, fp_root="/usr/share/kicad/footprints/") -> Path:
    """Write <outdir>/CUSTOM.pretty/X2QFN-12_RWB.kicad_mod and ESP32-C3-MINI-1.kicad_mod; return the .pretty directory."""
    pretty = Path(outdir) / f"{NICK}.pretty"
    pretty.mkdir(parents=True, exist_ok=True)
    (pretty / f"{NAME}.kicad_mod").write_text(kicad_mod(), encoding="utf-8")
    stock = Path(fp_root) / "RF_Module.pretty" / "ESP32-C6-MINI-1.kicad_mod"
    if stock.exists():
        (pretty / f"{U9_NAME}.kicad_mod").write_text(u9_mod(stock.read_text(encoding="utf-8")), encoding="utf-8")
    j1 = Path(fp_root) / "Connector_USB.pretty" / f"{J1_STOCK}.kicad_mod"
    if j1.exists():
        (pretty / f"{J1_NAME}.kicad_mod").write_text(j1_mod(j1.read_text(encoding="utf-8")), encoding="utf-8")
    return pretty
