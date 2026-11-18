# SPDX-License-Identifier: Apache-2.0
"""Add KiKit tab annotations to a copy of a round board for the P1 panel (plan 08 4.5; HW-008).

Usage (KiCad Python with pcbnew and KiKit 1.8.1):
  panel_tabs.py <board.kicad_pcb> <out.kicad_pcb> [--azimuths 45,120,215,325] [--width 3]
                [--min-cap-mm 3] [--report tabs.json]

The input board is not changed. The copy gets one `kikit:Tab` footprint per azimuth; `kikit
panelize` with `tabs.type = annotation` (scripts/panel_p1.json) then makes each tab from that point
to the nearest rail.

Tab type (KiKit 1.8.1 source read: panelize_ui_impl.buildTabs, Panel._buildTabAnnotations,
Substrate.tab):
- annotation (chosen): the position and the width of every tab are set here, so the tabs can be
  kept away from the edge features below and checked against the capacitors.
- fixed and spacing: KiKit spreads the tabs evenly along each side of the bounding box. The
  bounding box of this board includes the J1 tab, so the azimuth of a tab on the round edge is not
  controlled.
- corner: tabs from the bounding-box corners towards its centre; the azimuth again follows the J1
  tab.
- full: the whole side that faces a rail is joined to it; no mouse bites on the round edge.
- plugin: own Python inside KiKit; more code to review than one footprint per tab.

Geometry: mechanical azimuth (0 deg = +X, counter-clockwise seen from the top), as in
hw/kicad/spike-gate/src/mech_outline.py; KiCad y points down. The board centre and radius come
from the Edge.Cuts arcs with the largest radius. Each tab is vertical (perpendicular to the top
and bottom rails of `railstb`): azimuths between 0 and 180 deg go to the top rail, the others to
the bottom rail. The annotation origin is 0.5 mm outside the board bounding box (KiKit uses
footprints whose origin is within 1 mm of it).

Checks (exit 1 when one fails; the board copy is written in any case):
- every tab is at least EDGE_CLEARANCE_MM along the edge from each feature of EDGE_FEATURES;
- no capacitor pad (C<number>, both sides) is within --min-cap-mm of the tab cut on the board edge
  (flex cracking of MLCCs at depaneling; plan 08 section 4.5).
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Features on the board edge that a tab must keep clear of: (name, mechanical azimuth in deg,
# half-width in mm along the edge). The two housing models disagree on the hook azimuths (plan 08
# R11), so both are listed. Sources:
#   J1 tab: mech_outline V1_TAB_W 12 mm; its sides meet the R 23 circle at +-15.1 deg (6.1 mm).
#   notch: mech_outline NOTCH_AZ, NOTCH_R.
#   hook/post 30, 150, 270: mech_outline POST_AZ, POST_TANG 4 mm.
#   hook/post 60, 180, 300: mech/freecad/housing.py (snap hooks at 120 k + 60 deg, HOOK_W 4 mm)
#     and housing_params POST_DEG (posts, POST_PAD_W 4 mm).
#   button 240: mech_outline BTN_AZ, housing_params BTN_DEG and BTN_D 7 mm.
EDGE_FEATURES: tuple[tuple[str, float, float], ...] = (
    ("J1 tab", 0.0, 6.1),
    ("notch", 90.0, 1.5),
    ("hook/post 30 (mech_outline)", 30.0, 2.0),
    ("hook/post 150 (mech_outline)", 150.0, 2.0),
    ("hook/post 270 (mech_outline)", 270.0, 2.0),
    ("hook/post 60 (housing.py)", 60.0, 2.0),
    ("hook/post 180 (housing.py)", 180.0, 2.0),
    ("hook/post 300 (housing.py)", 300.0, 2.0),
    ("button 240", 240.0, 3.5),
)
# Assumption of this script: 2 mm keeps the nub that the mouse bites leave off a feature.
EDGE_CLEARANCE_MM = 2.0
DEFAULT_AZIMUTHS = (45.0, 120.0, 215.0, 325.0)
ORIGIN_OUTSIDE_MM = 0.5
MIN_SIN = math.sin(math.radians(20.0))  # a vertical tab needs an edge that is not close to vertical
CUT_STEP_MM = 0.05
KIID_SEED = 42


@dataclass(frozen=True)
class Tab:
    azimuth: float
    rail: str
    origin: tuple[float, float]
    orientation: float
    width: float
    cut: tuple[tuple[float, float], ...]


def circle_from_points(
    p1: tuple[float, float], p2: tuple[float, float], p3: tuple[float, float]
) -> tuple[float, float, float]:
    """Centre x, centre y and radius of the circle through three points."""
    (ax, ay), (bx, by), (cx, cy) = p1, p2, p3
    d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:  # noqa: PLR2004
        raise ValueError("the three points are on one line")
    ux = (
        (ax * ax + ay * ay) * (by - cy)
        + (bx * bx + by * by) * (cy - ay)
        + (cx * cx + cy * cy) * (ay - by)
    ) / d
    uy = (
        (ax * ax + ay * ay) * (cx - bx)
        + (bx * bx + by * by) * (ax - cx)
        + (cx * cx + cy * cy) * (bx - ax)
    ) / d
    return ux, uy, math.hypot(ax - ux, ay - uy)


def board_circle(
    arcs: Iterable[tuple[tuple[float, float], tuple[float, float], tuple[float, float]]],
    tol: float = 0.01,
) -> tuple[float, float, float]:
    """Centre and radius of the outline circle: the largest arcs, which must share one centre."""
    circles = [circle_from_points(*a) for a in arcs]
    if not circles:
        raise ValueError("no Edge.Cuts arc on the board")
    r_max = max(c[2] for c in circles)
    big = [c for c in circles if c[2] > r_max - tol]
    cx, cy = big[0][0], big[0][1]
    if any(math.hypot(c[0] - cx, c[1] - cy) > tol for c in big):
        raise ValueError("the largest Edge.Cuts arcs do not share one centre")
    return cx, cy, r_max


def edge_gap(az: float, width: float, radius: float, feature: tuple[str, float, float]) -> float:
    """Distance along the edge between the tab and a feature (negative when they overlap)."""
    d = abs((az - feature[1] + 180.0) % 360.0 - 180.0)
    return radius * math.radians(d) - width / 2.0 - feature[2]


def make_tab(
    centre: tuple[float, float, float], az: float, width: float, bbox_y: tuple[float, float]
) -> Tab:
    """Vertical tab at mechanical azimuth az (deg); bbox_y: board (top, bottom) y in KiCad mm."""
    cx, cy, r = centre
    s, c = math.sin(math.radians(az)), math.cos(math.radians(az))
    if abs(s) < MIN_SIN:
        raise ValueError(
            f"azimuth {az} deg: the edge is too steep for a tab to the top or bottom rail"
        )
    px = cx + r * c
    if px - width / 2 <= cx - r or px + width / 2 >= cx + r:
        raise ValueError(f"azimuth {az} deg: the tab is wider than the board at that point")
    sign = -1.0 if s > 0 else 1.0  # upper half (mechanical +y) is KiCad -y
    n = max(2, math.ceil(width / CUT_STEP_MM))
    cut = tuple(
        (x, cy + sign * math.sqrt(r * r - (x - cx) ** 2))
        for x in (px - width / 2 + width * k / n for k in range(n + 1))
    )
    if s > 0:
        return Tab(az, "top", (px, bbox_y[0] - ORIGIN_OUTSIDE_MM), -90.0, width, cut)
    return Tab(az, "bottom", (px, bbox_y[1] + ORIGIN_OUTSIDE_MM), 90.0, width, cut)


def box_distance(px: float, py: float, box: tuple[float, float, float, float]) -> float:
    """Distance from a point to an axis-aligned box (x0, y0, x1, y1); 0 inside."""
    x0, y0, x1, y1 = box
    return math.hypot(max(x0 - px, 0.0, px - x1), max(y0 - py, 0.0, py - y1))


def nearest_pads(
    cut: Sequence[tuple[float, float]], pads: dict[str, list[tuple[float, float, float, float]]]
) -> list[tuple[str, float]]:
    """(ref, distance from the cut to the nearest pad box of that ref), nearest first."""
    out = [
        (ref, min(box_distance(x, y, b) for b in boxes for x, y in cut))
        for ref, boxes in pads.items()
        if boxes
    ]
    return sorted(out, key=lambda t: t[1])


def check_tabs(
    tabs: Sequence[Tab],
    radius: float,
    cap_pads: dict[str, list[tuple[float, float, float, float]]],
    min_cap_mm: float,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Report entries per tab and the list of failures."""
    report: list[dict[str, Any]] = []
    fails: list[str] = []
    for t in tabs:
        gaps = sorted((edge_gap(t.azimuth, t.width, radius, f), f[0]) for f in EDGE_FEATURES)
        caps = nearest_pads(t.cut, cap_pads)
        fails += [
            f"tab {t.azimuth:g} deg: {g:.2f} mm from {name} (< {EDGE_CLEARANCE_MM} mm)"
            for g, name in gaps
            if g < EDGE_CLEARANCE_MM
        ]
        fails += [
            f"tab {t.azimuth:g} deg: capacitor {ref} at {d:.2f} mm (< {min_cap_mm} mm)"
            for ref, d in caps
            if d < min_cap_mm
        ]
        entry = asdict(t)
        entry.pop("cut")
        entry["cut_ends"] = [t.cut[0], t.cut[-1]]
        entry["nearest_edge_feature"] = {"name": gaps[0][1], "gap_mm": round(gaps[0][0], 2)}
        entry["nearest_capacitors"] = [{"ref": r, "mm": round(d, 2)} for r, d in caps[:3]]
        report.append(entry)
    return report, fails


# --------------------------------------------------------------------------------------- KiCad glue
def _mm(v: Any) -> float:
    return float(v) / 1e6


def _pt(v: Any) -> tuple[float, float]:
    return _mm(v.x), _mm(v.y)


def _pcbnew() -> Any:
    import pcbnew  # type: ignore[import-not-found]  # noqa: PLC0415

    return pcbnew


def _add_annotations(board: Any, tabs: Sequence[Tab]) -> None:
    import kikit  # type: ignore[import-not-found]  # noqa: PLC0415

    pcbnew = _pcbnew()
    lib = str(Path(kikit.__file__).parent / "resources" / "kikit.pretty")
    for i, t in enumerate(tabs, 1):
        fp = pcbnew.FootprintLoad(lib, "Tab")
        if fp is None:
            raise RuntimeError(f"kikit:Tab not found in {lib}")
        fp.SetFPID(pcbnew.LIB_ID("kikit", "Tab"))
        board.Add(fp)
        fp.SetReference(f"KIKIT_TAB{i}")
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(t.origin[0]), pcbnew.FromMM(t.origin[1])))
        fp.SetOrientationDegrees(t.orientation)
        texts = [
            x for x in fp.GraphicalItems() if str(getattr(x, "GetText", str)()).startswith("KIKIT:")
        ]
        if len(texts) != 1:
            raise RuntimeError("kikit:Tab footprint without one KIKIT: text")
        texts[0].SetText(f"KIKIT: width: {t.width}mm")


def main(argv: Sequence[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("board")
    p.add_argument("out")
    p.add_argument("--azimuths", default=",".join(f"{a:g}" for a in DEFAULT_AZIMUTHS))
    p.add_argument("--width", type=float, default=3.0)
    p.add_argument("--min-cap-mm", type=float, default=3.0)
    p.add_argument("--report", default=None)
    args = p.parse_args(argv)
    pcbnew = _pcbnew()
    board = pcbnew.LoadBoard(args.board)
    edges = [d for d in board.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
    arcs = [
        (_pt(d.GetStart()), _pt(d.GetArcMid()), _pt(d.GetEnd()))
        for d in edges
        if d.GetShape() == pcbnew.SHAPE_T_ARC
    ]
    centre = board_circle(arcs)
    bbox = board.GetBoardEdgesBoundingBox()
    bbox_y = (_mm(bbox.GetTop()), _mm(bbox.GetBottom()))
    azimuths = [float(a) for a in args.azimuths.split(",") if a.strip()]
    tabs = [make_tab(centre, az, args.width, bbox_y) for az in azimuths]
    cap_pads: dict[str, list[tuple[float, float, float, float]]] = {}
    for fp in board.GetFootprints():
        if re.fullmatch(r"C\d+", fp.GetReference()):
            cap_pads[fp.GetReference()] = [
                (_mm(b.GetLeft()), _mm(b.GetTop()), _mm(b.GetRight()), _mm(b.GetBottom()))
                for b in (pad.GetBoundingBox() for pad in fp.Pads())
            ]
    report, fails = check_tabs(tabs, centre[2], cap_pads, args.min_cap_mm)
    # Fixed ids: KiCad saves footprints in id order and KiKit numbers the mouse bites in that order,
    # so random ids would make the panel and its Gerbers differ from build to build.
    pcbnew.KIID.SeedGenerator(KIID_SEED)
    _add_annotations(board, tabs)
    pcbnew.SaveBoard(args.out, board)
    doc = {
        "board": args.board,
        "centre_mm": [round(centre[0], 4), round(centre[1], 4)],
        "radius_mm": round(centre[2], 4),
        "edge_clearance_mm": EDGE_CLEARANCE_MM,
        "min_cap_mm": args.min_cap_mm,
        "tabs": report,
        "failures": fails,
        "verdict": "FAIL" if fails else "PASS",
    }
    text = json.dumps(doc, indent=1)
    if args.report:
        Path(args.report).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
