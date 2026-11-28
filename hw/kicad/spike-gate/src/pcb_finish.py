# SPDX-License-Identifier: Apache-2.0
"""Finish a routed spike board for assembly (HW-010): reference designators on the silkscreen and fiducials.

Usage: python3 pcb_finish.py <board.kicad_pcb> [drc.json of a first pass: its silkscreen findings leave those texts off]     (needs pcbnew; rewrites the file; no track, via or part moves)
Silkscreen: every reference text moves from the Fab layer to the silkscreen of its side, in free space beside its part
(clear of every part box, the board edge and the other texts); a part with no room keeps no silkscreen text and is listed.
Fiducials: three round 1.0 mm pads with a 2.0 mm mask opening on each side, in copper-free spots far from each other.
Bottom map (owner answer 13 of 2026-11-17, plan 08 section 4.4; RV-016 row 15): the reference of every top part as mirrored
1.0 mm text on B.SilkS at the part's position, moved in 0.5 mm steps up to 2 mm to clear bottom pads, vias, the edge and
other texts, else left out and listed. Identification (RV-016 row 18): one B.SilkS text "busy-light P1 <commit>" (or
$BOARD_ID) in the first free place.
The geometry is in pure functions (tests/test_pcb_finish.py); the DRC of the finished board is the check.
"""
from __future__ import annotations

import math
import sys

CHAR_W = 0.8                       # character advance as a share of the text height (KiCad stroke font, with spacing)
MARGIN = 0.25                      # mm between a text and anything else
Rect = tuple[float, float, float, float]


def overlap(a: Rect, b: Rect, margin: float) -> bool:
    return not (a[2] + margin <= b[0] or b[2] + margin <= a[0] or a[3] + margin <= b[1] or b[3] + margin <= a[1])


def in_rects(x: float, y: float, rects: list[Rect], margin: float) -> bool:
    return any(r[0] - margin <= x <= r[2] + margin and r[1] - margin <= y <= r[3] + margin for r in rects)


def refs_in_silk_findings(drc: dict) -> set[str]:
    """References whose text is named in a silkscreen finding of a kicad-cli DRC report (these texts get no silkscreen place)."""
    out = set()
    for v in drc.get("violations", []):
        if v["type"].startswith("silk"):
            for it in v["items"]:
                d = it["description"]
                if d.startswith("Reference field of "):
                    out.add(d[len("Reference field of "):].strip())
    return out


def text_size(s: str, height: float) -> tuple[float, float]:
    return (len(s) * CHAR_W * height, height)


def text_box(s: str, pos: tuple[float, float], height: float) -> Rect:
    w, h = text_size(s, height)
    return (pos[0] - w / 2, pos[1] - h / 2, pos[0] + w / 2, pos[1] + h / 2)


def place_text(ref: str, part: Rect, obstacles: list[Rect], inside, height: float):
    """Centre of the nearest free spot for the text of `ref` beside its part box, or None. Horizontal text only."""
    w, h = text_size(ref, height)
    cx, cy = (part[0] + part[2]) / 2, (part[1] + part[3]) / 2
    cands = []
    for d in (0.15, 0.35, 0.7, 1.2, 2.0):
        for dx, dy in ((0, -1), (0, 1), (1, 0), (-1, 0), (1, -1), (-1, -1), (1, 1), (-1, 1)):
            x = cx + dx * ((part[2] - part[0]) / 2 + w / 2 * (1 if dx else 0) + d) if dx else cx
            y = cy + dy * ((part[3] - part[1]) / 2 + h / 2 + d) if dy else cy
            cands.append((abs(x - cx) + abs(y - cy), x, y))
    for _, x, y in sorted(cands):
        box = text_box(ref, (x, y), height)
        if overlap(box, part, MARGIN) or not inside(box):
            continue
        if any(overlap(box, o, MARGIN) for o in obstacles):
            continue
        return (x, y)
    return None


def free_spot(items: list[tuple[float, float, float]], inside, clearance: float, step: float, far_from: list,
              min_far: float = 0.0, bounds: tuple = (-100.0, -100.0, 100.0, 100.0)):
    """A point at least `clearance` from the edge of every copper item (x, y, radius), accepted by `inside` and at least
    `min_far` from the points in far_from; the one farthest from those points (the first one when there are none)."""
    best, best_d = None, -1.0
    nx = int((bounds[2] - bounds[0]) / step) + 1
    ny = int((bounds[3] - bounds[1]) / step) + 1
    for i in range(nx):
        x = bounds[0] + i * step
        for j in range(ny):
            y = bounds[1] + j * step
            if not inside(x, y):
                continue
            if any(math.hypot(x - ix, y - iy) < r + clearance for ix, iy, r in items):
                continue
            d = min((math.hypot(x - fx, y - fy) for fx, fy in far_from), default=1e9)
            if d < min_far:
                continue
            if not far_from:
                return (x, y)
            if d > best_d:
                best, best_d = (x, y), d
    return best


def map_spot(ref: str, centre: tuple[float, float], obstacles: list[Rect], inside, height: float,
             step: float = 0.5, reach: float = 2.0):
    """Centre for a bottom-map text of `ref`: the part's own position, else the nearest point of a `step` grid within
    `reach` whose text box clears every obstacle by MARGIN and is accepted by `inside`; None when there is none."""
    n = int(round(reach / step))
    cands = sorted(((i * step) ** 2 + (j * step) ** 2, i * step, j * step)
                   for i in range(-n, n + 1) for j in range(-n, n + 1) if math.hypot(i * step, j * step) <= reach + 1e-9)
    for _, dx, dy in cands:
        pos = (centre[0] + dx, centre[1] + dy)
        box = text_box(ref, pos, height)
        if inside(box) and not any(overlap(box, o, MARGIN) for o in obstacles):
            return pos
    return None


def first_free_box(text: str, height: float, obstacles: list[Rect], inside, bounds: tuple, step: float = 0.5,
                   margin: float = MARGIN):
    """Centre of the first free place (row by row over `bounds`) for a text box, `margin` from every obstacle, or None."""
    nx, ny = int((bounds[2] - bounds[0]) / step) + 1, int((bounds[3] - bounds[1]) / step) + 1
    for j in range(ny):
        for i in range(nx):
            pos = (bounds[0] + i * step, bounds[1] + j * step)
            box = text_box(text, pos, height)
            if inside(box) and not any(overlap(box, o, margin) for o in obstacles):
                return pos
    return None


def box_points(r: Rect, step: float = 0.5) -> list[tuple[float, float]]:
    """Points on a grid over a box (corners and edges included), so a slot inside the box is found."""
    nx, ny = max(1, int((r[2] - r[0]) / step)), max(1, int((r[3] - r[1]) / step))
    return [(r[0] + (r[2] - r[0]) * i / nx, r[1] + (r[3] - r[1]) * j / ny) for i in range(nx + 1) for j in range(ny + 1)]


def board_id() -> str:
    import os  # noqa: PLC0415
    import subprocess  # noqa: PLC0415
    if os.environ.get("BOARD_ID"):
        return os.environ["BOARD_ID"]
    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True,
                             cwd=os.path.dirname(os.path.abspath(__file__))).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        rev = ""
    return ("busy-light P1 " + rev).strip()


NM = 1e6


def main(argv: list[str]) -> int:
    import pcbnew  # noqa: PLC0415
    b = pcbnew.LoadBoard(argv[1])
    # a later pass replaces the bottom texts of an earlier one: every board-level text on B.SilkS is this script's
    old_texts = [d for d in b.GetDrawings() if d.GetClass() == "PCB_TEXT" and d.GetLayer() == pcbnew.B_SilkS]
    if old_texts:
        for d in old_texts:
            b.Delete(d)
        b.Save(argv[1])
        b = pcbnew.LoadBoard(argv[1])
    outline = pcbnew.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(outline, False)

    def in_board(x, y, m):
        return all(outline.Contains(pcbnew.VECTOR2I(int((x + dx) * NM), int((y + dy) * NM)))
                   for dx, dy in ((m, 0), (-m, 0), (0, m), (0, -m), (m, m), (-m, -m), (m, -m), (-m, m)))

    fps = list(b.GetFootprints())

    def part_box(f) -> Rect:
        bb = f.GetBoundingBox(False)
        return (bb.GetLeft() / NM, bb.GetTop() / NM, bb.GetRight() / NM, bb.GetBottom() / NM)

    def obstacle_boxes(g) -> list[Rect]:
        """Boxes a text must avoid: the whole box of a small part; only the pads of a large one (the module box covers its antenna area)."""
        bx = part_box(g)
        if max(bx[2] - bx[0], bx[3] - bx[1]) <= 8.0:
            return [bx]
        pl = g.Pads()
        out = []
        for i in range(len(pl)):
            q = pl[i].GetBoundingBox()
            out.append((q.GetLeft() / NM, q.GetTop() / NM, q.GetRight() / NM, q.GetBottom() / NM))
        return out

    # fiducials first: their spots depend only on copper and the outline; the designators then avoid them (board p1b13:
    # placed after the texts, a fiducial took the spot of a designator in each of three passes)
    bb = b.GetBoardEdgesBoundingBox()
    bounds = (bb.GetLeft() / NM, bb.GetTop() / NM, bb.GetRight() / NM, bb.GetBottom() / NM)
    keep_out = [part_box(g) for g in fps if g.GetReference() in ("U9", "J1")]
    za = b.Zones()
    for i in range(len(za)):
        if za[i].GetIsRuleArea():
            zb = za[i].GetBoundingBox()
            keep_out.append((zb.GetLeft() / NM, zb.GetTop() / NM, zb.GetRight() / NM, zb.GetBottom() / NM))
    fid_count = 0
    for side, copper in (("F", pcbnew.F_Cu), ("B", pcbnew.B_Cu)):
        items = []
        for f in fps:
            pl = f.Pads()
            for i in range(len(pl)):
                p = pl[i]
                if p.IsOnLayer(copper):
                    items.append((p.GetPosition().x / NM, p.GetPosition().y / NM, max(p.GetSizeX(), p.GetSizeY()) / 2 / NM))
        tr = b.Tracks()
        for i in range(tr.size()):
            t = tr[i]
            if t.GetClass() == "PCB_VIA" or t.GetLayer() == copper:
                s, e = t.GetStart(), t.GetEnd()
                n = max(1, int(math.hypot(e.x - s.x, e.y - s.y) / (0.5 * NM)))
                w = (pcbnew.Cast_to_PCB_VIA(t).GetWidth(copper) if t.GetClass() == "PCB_VIA" else t.GetWidth()) / 2 / NM
                for k in range(n + 1):
                    items.append(((s.x + (e.x - s.x) * k / n) / NM, (s.y + (e.y - s.y) * k / n) / NM, w))
        mine = []
        for k in range(3):
            spot = free_spot(items + [(x, y, 0.5) for x, y in mine], lambda x, y: in_board(x, y, 2.5) and not in_rects(x, y, keep_out, 2.5), 1.6, 0.5, mine,
                             min_far=12.0 if mine else 0.0, bounds=bounds)
            if spot is None:
                break
            mine.append(spot)
            fid = pcbnew.FOOTPRINT(b)
            fid.SetReference("FID%d" % (len(mine) + (3 if side == "B" else 0)))
            fid.SetValue("Fiducial")
            fid.SetAttributes(pcbnew.FP_BOARD_ONLY | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM)
            pad = pcbnew.PAD(fid)
            pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
            pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            pad.SetSize(pcbnew.VECTOR2I(int(1.0 * NM), int(1.0 * NM)))
            pad.SetLayerSet(pcbnew.LSET())
            pad.SetLocalSolderMaskMargin(int(0.5 * NM))
            pad.SetNumber("")
            fid.Add(pad)
            cy = pcbnew.PCB_SHAPE(fid)
            cy.SetShape(pcbnew.SHAPE_T_CIRCLE)
            cy.SetLayer(pcbnew.F_CrtYd)
            cy.SetStart(pcbnew.VECTOR2I(0, 0))
            cy.SetEnd(pcbnew.VECTOR2I(int(1.0 * NM), 0))
            cy.SetWidth(int(0.05 * NM))
            fid.Add(cy)
            fid.Reference().SetVisible(False)
            fid.Value().SetVisible(False)
            b.Add(fid)
            fid.SetPosition(pcbnew.VECTOR2I(int(spot[0] * NM), int(spot[1] * NM)))
            if side == "B":
                fid.Flip(fid.GetPosition(), False)
            ls = pcbnew.LSET()
            ls.AddLayer(pcbnew.B_Cu if side == "B" else pcbnew.F_Cu)
            ls.AddLayer(pcbnew.B_Mask if side == "B" else pcbnew.F_Mask)
            pad.SetLayerSet(ls)
            fid_count += 1
    fps_all = list(b.GetFootprints())                     # the parts and the new fiducials: obstacles for the texts
    import json  # noqa: PLC0415
    skip = refs_in_silk_findings(json.load(open(argv[2], encoding="utf-8"))) if len(argv) > 2 else set()
    placed, missing = {"F": [], "B": []}, []
    for f in sorted(fps, key=lambda f: -((part_box(f)[2] - part_box(f)[0]) * (part_box(f)[3] - part_box(f)[1]))):
        side = "B" if f.GetLayerName() == "B.Cu" else "F"
        ref = f.GetReference()
        if f.GetAttributes() & pcbnew.FP_BOARD_ONLY:
            continue
        boxes = [x for g in fps_all if g is not f and (g.GetLayerName() == f.GetLayerName() or g.GetReference() == "J1") for x in obstacle_boxes(g)]
        own = part_box(f) if max(part_box(f)[2] - part_box(f)[0], part_box(f)[3] - part_box(f)[1]) <= 8.0 else None
        if own is None:
            pads = obstacle_boxes(f)
            own = (min(q[0] for q in pads), min(q[1] for q in pads), max(q[2] for q in pads), max(q[3] for q in pads))
        pos = None
        for h, t in (() if ref in skip else ((1.0, 0.15), (0.8, 0.12))):
            pos = place_text(ref, own, boxes + placed[side], lambda r: in_board((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, 0.0)
                             and in_board(r[0], r[1], 0.5) and in_board(r[2], r[3], 0.5), h)
            if pos:
                break
        t_ = f.Reference()
        if pos is None:
            missing.append(ref)
            t_.SetVisible(False)
            continue
        placed[side].append(text_box(ref, pos, h))
        t_.SetLayer(pcbnew.B_SilkS if side == "B" else pcbnew.F_SilkS)
        t_.SetTextSize(pcbnew.VECTOR2I(int(h * NM), int(h * NM)))
        t_.SetTextThickness(int(t * NM))
        t_.SetKeepUpright(False)
        t_.SetTextAngleDegrees(0)
        t_.SetMirrored(side == "B")
        t_.SetPosition(pcbnew.VECTOR2I(int(pos[0] * NM), int(pos[1] * NM)))
        t_.SetVisible(True)

    n_designators = len(placed["F"]) + len(placed["B"])
    # bottom map of the top parts and the identification text (B.SilkS, mirrored); the texts of an earlier pass were
    # removed when the board was loaded

    def bottom_text(s, pos, h):
        txt = pcbnew.PCB_TEXT(b)
        txt.SetText(s)
        txt.SetLayer(pcbnew.B_SilkS)
        txt.SetTextSize(pcbnew.VECTOR2I(int(h * NM), int(h * NM)))
        txt.SetTextThickness(int(0.15 * NM))
        txt.SetMirrored(True)
        txt.SetPosition(pcbnew.VECTOR2I(int(pos[0] * NM), int(pos[1] * NM)))
        b.Add(txt)
        placed["B"].append(text_box(s, pos, h))

    def inside_box(r):        # every grid point of the box 0.5 mm inside the outline (slots and cut-outs included)
        return all(in_board(x, y, 0.5) for x, y in box_points(r))

    bottom_obst = [x for g in fps_all if g.GetLayerName() == "B.Cu" for x in obstacle_boxes(g)]
    bottom_obst += [x for g in fps_all if g.GetReference() == "J1" for x in obstacle_boxes(g)]
    tr = b.Tracks()
    for i in range(tr.size()):
        if tr[i].GetClass() == "PCB_VIA":
            vb = tr[i].GetBoundingBox()
            bottom_obst.append((vb.GetLeft() / NM, vb.GetTop() / NM, vb.GetRight() / NM, vb.GetBottom() / NM))
    map_missing = []
    for f in sorted(fps_all, key=lambda g: g.GetReference()):
        ref = f.GetReference()
        if f.GetLayerName() != "F.Cu" or f.GetAttributes() & pcbnew.FP_BOARD_ONLY or ref.startswith(("FID", "TP")):
            continue
        bx = part_box(f)
        pos = map_spot(ref, ((bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2), bottom_obst + placed["B"], inside_box, 1.0)
        if pos is None:
            map_missing.append(ref)
        else:
            bottom_text(ref, pos, 1.0)
    ident, id_pos = board_id(), None
    for text, h in ((ident, 1.0), (ident, 0.8), (ident.replace("busy-light ", ""), 0.8)):
        id_pos = first_free_box(text, h, bottom_obst + placed["B"], inside_box, bounds, margin=1.0)   # the box is an estimate
        if id_pos is not None:
            ident = text
            bottom_text(text, id_pos, h)
            break

    b.Save(argv[1])
    print("silkscreen designators: %d placed, %d without room %s; fiducials: %d" % (
        n_designators, len(missing), missing, fid_count))
    print("bottom map: %d of the top parts left out %s; identification %r: %s" % (
        len(map_missing), map_missing, ident, "placed" if id_pos else "NO ROOM"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
