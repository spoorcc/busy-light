# SPDX-License-Identifier: Apache-2.0
"""Placement rules measured on a placed or routed board (plan 08 sections 4.2 and 4.3; RV-016 rows 11 and 12; ADR-0016,
HW-003, HW-016, HW-017).

The placer keeps its best seed when no seed meets the rules (`pcb_place.place`), so a rule miss could reach a stored board
without a message (board-p1: 5 of 15 `LAYOUT_RULES` and all 4 `INPUT_PATH_RULES` missed). This check measures the rules on
the board file itself. A part position is the centre of the placer's part extent (`pcb_full.pad_extent_mm` with
`MARGIN_EXT`), the same point the placer moves. A partner written "J1:VBUS" is the nearest pad centre of J1 on net VBUS.

Usage: python3 pcb_layout_check.py <board.kicad_pcb> [--json <out>]
Exit: 0 every rule met, 1 a rule missed, 2 usage error or a rule part missing from the board.
"""
import json
import math
import sys

import pcbnew

import pcb_full


def part_centre(fp):
    """Centre (mm) of the part extent that the placer positions (pcb_full.centre_at)."""
    x0, y0, x1, y1 = pcb_full.pad_extent_mm(fp, pcb_full.MARGIN_EXT)
    return (x0 + x1) / 2.0, (y0 + y1) / 2.0


def partner_point(fps, spec, near):
    """Point (mm) of a rule partner: a part centre, or for "REF:NET" the pad centre of REF on NET nearest to `near`."""
    if ":" not in spec:
        return part_centre(fps[spec])
    ref, net = spec.split(":", 1)
    pads = [p for p in fps[ref].Pads() if p.GetNetname() == net]
    if not pads:
        raise KeyError(spec)
    pts = [(pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)) for p in pads]
    return min(pts, key=lambda q: math.dist(q, near))


def measure(board, rules):
    """One dict per rule: part, partner, limit_mm, distance_mm (None if a part is missing), met (None if missing)."""
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    out = []
    for a, b, lim in rules:
        row = {"part": a, "partner": b, "limit_mm": lim, "distance_mm": None, "met": None}
        if a in fps and b.split(":", 1)[0] in fps:
            try:
                ca = part_centre(fps[a])
                d = math.dist(ca, partner_point(fps, b, ca))
            except KeyError:
                d = None
            if d is not None:
                row["distance_mm"] = round(d, 2)
                row["met"] = d <= lim
        out.append(row)
    return out


def all_rules():
    return tuple(pcb_full.LAYOUT_RULES) + tuple(pcb_full.INPUT_PATH_RULES)


def main(argv):
    if len(argv) not in (1, 3) or (len(argv) == 3 and argv[1] != "--json"):
        print(__doc__, file=sys.stderr)
        return 2
    rows = measure(pcbnew.LoadBoard(argv[0]), all_rules())
    missing = [r for r in rows if r["met"] is None]
    missed = [r for r in rows if r["met"] is False]
    doc = {"rules": rows, "missed": len(missed), "missing": len(missing)}
    text = json.dumps(doc, indent=1)
    print(text)
    if len(argv) == 3:
        with open(argv[2], "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    for r in missed:
        print("MISSED %s to %s: %.2f mm (rule %.1f mm)" % (r["part"], r["partner"], r["distance_mm"], r["limit_mm"]),
              file=sys.stderr)
    return 2 if missing else (1 if missed else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
