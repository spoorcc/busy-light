# SPDX-License-Identifier: Apache-2.0
"""Capacitor values and the second spare footprint on a stored spike board (HW-014, HW-016, HW-010).

Usage: python3 pcb_spare_caps.py <in.kicad_pcb> <out.kicad_pcb> <full.kicad_sch>      (needs pcbnew; routing is done afterwards by pcb_fix.py)
1. The value text of C2 to C6 and of the spares follows the generator table (`layout_full.PARTS`).
2. C4 and C32 are marked do-not-populate. C32 is a copy of C4 (same footprint, +5V on pad 1, GND on pad 2) on the
   nearest copper-free spot to U7 pin 6, found by the pure function `find_spot`.
Geometry is in pure functions (tests/test_pcb_spare_caps.py); the DRC of the result is the check.
"""
from __future__ import annotations

import math
import re
import sys

Rect = tuple[float, float, float, float]


def rect_hit(a: Rect, b: Rect, margin: float) -> bool:
    return not (a[2] + margin <= b[0] or b[2] + margin <= a[0] or a[3] + margin <= b[1] or b[3] + margin <= a[1])


def find_spot(size: tuple[float, float], target: tuple[float, float], obstacles: list[Rect], inside,
              margin: float, step: float = 0.5, radius: float = 14.0):
    """Nearest centre to `target` (searched on a grid of `step` mm, rings outward) where a box of `size` has
    `margin` to every obstacle and lies inside; `inside(rect)` says whether a rectangle is on the board. Returns
    (x, y) or None."""
    w, h = size
    n = int(radius / step)
    cands = sorted(((target[0] + i * step, target[1] + j * step) for i in range(-n, n + 1) for j in range(-n, n + 1)),
                   key=lambda p: math.hypot(p[0] - target[0], p[1] - target[1]))
    for x, y in cands:
        r = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        if inside(r) and not any(rect_hit(r, o, margin) for o in obstacles):
            return (round(x, 3), round(y, 3))
    return None


def segment_boxes(x0: float, y0: float, x1: float, y1: float, width: float, step: float = 0.4) -> list[Rect]:
    """A track segment as small boxes along its length (a diagonal track has a huge bounding box)."""
    n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
    h = width / 2
    return [(x0 + (x1 - x0) * i / n - h, y0 + (y1 - y0) * i / n - h,
             x0 + (x1 - x0) * i / n + h, y0 + (y1 - y0) * i / n + h) for i in range(n + 1)]


def schematic_uuid(sch_text: str, ref: str) -> str | None:
    """uuid of the symbol with the given reference in a .kicad_sch text (None when it is not there)."""
    for blk in re.split(r"\n  \(symbol\b", sch_text)[1:]:
        if re.search(r'\(property "Reference" "%s"' % re.escape(ref), blk):
            m = re.search(r"\(uuid ([0-9a-f-]{36})\)", blk)
            return m.group(1) if m else None
    return None


def schematic_value(sch_text: str, ref: str) -> str | None:
    """Value text of the symbol with the given reference in a .kicad_sch text."""
    for blk in re.split(r"\n  \(symbol\b", sch_text)[1:]:
        if re.search(r'\(property "Reference" "%s"' % re.escape(ref), blk):
            m = re.search(r'\(property "Value" "([^"]*)"', blk)
            return m.group(1) if m else None
    return None


SOURCING_FIELDS = ("MPN", "Manufacturer", "LCSC")


def schematic_fields(sch_text: str) -> dict[str, dict[str, str]]:
    """Reference -> the sourcing fields of its symbol, for every symbol that has them."""
    out: dict[str, dict[str, str]] = {}
    for blk in re.split(r"\n  \(symbol\b", sch_text)[1:]:
        ref = re.search(r'\(property "Reference" "([^"]*)"', blk)
        if not ref:
            continue
        got = {k: m.group(1) for k in SOURCING_FIELDS
               if (m := re.search(r'\(property "%s" "([^"]*)"' % k, blk))}
        if got:
            out[ref.group(1)] = got
    return out


def main(argv: list[str]) -> int:
    import pcbnew  # noqa: PLC0415
    src, dst, sch = argv[1], argv[2], argv[3]
    b = pcbnew.LoadBoard(src)
    mm = pcbnew.ToMM
    text = open(sch, encoding="utf-8").read()
    for ref in ("C2", "C3", "C4", "C5", "C6"):
        b.FindFootprintByReference(ref).SetValue(schematic_value(text, ref))
    for ref in ("C4",):
        b.FindFootprintByReference(ref).SetDNP(True)
    if b.FindFootprintByReference("C32") is None:
        c4 = b.FindFootprintByReference("C4")
        u7 = b.FindFootprintByReference("U7")
        pin6 = [p for p in u7.Pads() if p.GetNumber() == "6"][0].GetPosition()
        outline = pcbnew.SHAPE_POLY_SET()
        b.GetBoardPolygonOutlines(outline, False)

        def inside(r: Rect) -> bool:
            pts = [(r[0], r[1]), (r[2], r[1]), (r[0], r[3]), (r[2], r[3])]
            return all(outline.Collide(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)), pcbnew.FromMM(1.0))
                       for x, y in pts)

        def box(bb) -> Rect:
            return (mm(bb.GetX()), mm(bb.GetY()), mm(bb.GetRight()), mm(bb.GetBottom()))

        bb = c4.GetBoundingBox(False)
        size = (mm(bb.GetWidth()), mm(bb.GetHeight()))
        margin = float(__import__("os").environ.get("SPARE_MARGIN", "0.4"))
        radius = float(__import__("os").environ.get("SPARE_RADIUS", "30"))
        tr = b.Tracks()                 # index access: iterating the SWIG container fails on Python 3.14
        tracks = [tr[i] for i in range(tr.size())]
        spot, bottom = None, False
        for bottom in (False, True):                       # the top side first, then the bottom side
            lay, silk = (pcbnew.B_Cu, "B.Silk") if bottom else (pcbnew.F_Cu, "F.Silk")
            obstacles: list[Rect] = []
            for f in list(b.GetFootprints()):
                t = f.Reference()                          # silkscreen designators (DRC: silk_overlap); no copper margin
                if t.IsVisible() and silk in t.GetLayerName():
                    tb = t.GetBoundingBox()
                    obstacles.append((mm(tb.GetX()) + margin, mm(tb.GetY()) + margin,
                                      mm(tb.GetRight()) - margin, mm(tb.GetBottom()) - margin))
                if f.GetLayer() == lay or any(p.HasHole() for p in f.Pads()):
                    obstacles.append(box(f.GetBoundingBox(False)))
            for t in tracks:
                if t.GetClass() == "PCB_VIA":
                    obstacles.append(box(t.GetBoundingBox()))
                elif t.GetLayer() == lay:
                    obstacles.extend(segment_boxes(mm(t.GetStart().x), mm(t.GetStart().y), mm(t.GetEnd().x),
                                                   mm(t.GetEnd().y), mm(t.GetWidth())))
            for i in range(b.GetAreaCount()):
                z = b.GetArea(i)
                if z.GetIsRuleArea():
                    obstacles.append(box(z.GetBoundingBox()))
            spot = find_spot(size, (mm(pin6.x), mm(pin6.y)), obstacles, inside, margin=margin, radius=radius)
            if spot is not None:
                break
        if spot is None:
            print("no free spot for C32")
            return 1
        c32 = pcbnew.FOOTPRINT(c4)
        c32.SetReference("C32")
        c32.SetValue(schematic_value(text, "C32"))
        c32.SetDNP(True)
        c32.Reference().SetLayer(pcbnew.F_Fab)           # no silkscreen place is searched for the spare
        c32.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(spot[0]), pcbnew.FromMM(spot[1])))
        c32.SetUuid(pcbnew.KIID())
        uid = schematic_uuid(text, "C32")
        if uid:
            c32.SetPath(pcbnew.KIID_PATH("/" + uid))
        for p in c32.Pads():
            p.SetUuid(pcbnew.KIID())
        b.Add(c32)
        if bottom:                                  # Flip() needs the footprint on a board
            c32.Flip(c32.GetPosition(), False)
        print("C32 at", spot, "distance to U7 pin 6 %.2f mm" % math.hypot(spot[0] - mm(pin6.x), spot[1] - mm(pin6.y)))
    for ref, fields in schematic_fields(text).items():     # DRC parity compares these fields with the symbol
        f = b.FindFootprintByReference(ref)
        if f is not None:
            for k, v in fields.items():
                f.SetField(k, v)
                fld = f.GetField(k)
                fld.SetVisible(False)                       # a new field is visible on the silkscreen by default
                fld.SetLayer(pcbnew.B_Fab if f.IsFlipped() else pcbnew.F_Fab)
    b.Save(dst)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
