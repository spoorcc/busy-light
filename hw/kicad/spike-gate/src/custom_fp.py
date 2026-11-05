# SPDX-License-Identifier: Apache-2.0
"""Generated footprint library CUSTOM of the spike (plan 06 A-11): the TUSB321 RWB X2QFN-12 land pattern.

The KiCad system libraries have no X2QFN footprint. The land pattern is PROVISIONAL: read from a text extract of the
TI drawing RWB0012A (pads 0.2 wide; 8 side pads at 0.5 pitch, 4 end pads at 0.4 pitch); verify against the drawing
before any use. Pure Python, deterministic (uuid5 of fixed keys). Used by the schematic generators (footprint link
check of ERC) and by pcb_full (the board loads this file, so board and library cannot differ).
"""
from __future__ import annotations

import uuid
from pathlib import Path

NICK = "CUSTOM"
NAME = "X2QFN-12_RWB"
_NS = uuid.UUID("5b0c2f0e-0000-4000-8000-00000000c0f9")
COURTYARD = 1.05


def pads() -> list[tuple[str, float, float, float, float]]:
    """(number, x, y, width, height) in mm, in file order."""
    p = [("1", 0.2, -0.7, 0.2, 0.4), ("2", -0.2, -0.7, 0.2, 0.4)]
    p += [(str(3 + i), -0.65, y, 0.4, 0.2) for i, y in enumerate((-0.75, -0.25, 0.25, 0.75))]
    p += [("7", -0.2, 0.7, 0.2, 0.4), ("8", 0.2, 0.7, 0.2, 0.4)]
    p += [(str(9 + i), 0.65, y, 0.4, 0.2) for i, y in enumerate((0.75, 0.25, -0.25, -0.75))]
    return p


def _id(key: str) -> str:
    return str(uuid.uuid5(_NS, key))


def kicad_mod() -> str:
    L = [f'(footprint "{NAME}"', "\t(version 20240108)", '\t(generator "busy-light-custom_fp")', '\t(layer "F.Cu")',
         '\t(descr "TUSB321 RWB X2QFN-12, provisional land pattern, spike")']
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


def write_library(outdir) -> Path:
    """Write <outdir>/CUSTOM.pretty/X2QFN-12_RWB.kicad_mod and return the .pretty directory."""
    pretty = Path(outdir) / f"{NICK}.pretty"
    pretty.mkdir(parents=True, exist_ok=True)
    (pretty / f"{NAME}.kicad_mod").write_text(kicad_mod(), encoding="utf-8")
    return pretty
