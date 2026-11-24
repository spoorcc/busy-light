#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Centre button zone geometry for plan 09 (MECH-004, MECH-003; analysis only, no board is changed).

Reads the stored board-p1 text (no pcbnew), builds the LED squares and the antenna strip, and runs two
searches: S2 (module moved so that the switch sits at the board centre) and S3 (three switches around the
module). Pure standard library. Frames: board centre at the origin. The LED ring and the searches use the
mechanical frame (y up); the footprint outlines keep KiCad's y (down). The antenna strip is symmetric about
the module long axis, so the y flip does not change any distance.

Run: python3 -I hw/kicad/spike-gate/src/button_zone.py   (prints the S2 and S3 results for the report)
Outside ruff while it is in spike-gate (pyproject.toml excludes the folder); the exception is recorded in
docs/verification/reports/analysis-button-disc.md.
"""

import math
import re
import sys
from collections.abc import Sequence
from pathlib import Path

Point = tuple[float, float]
Poly = list[Point]
Pose = tuple[float, float, float]  # x mm, y mm, angle degrees (counter-clockwise, antenna end at -y local)

HERE = Path(__file__).resolve().parent
BOARD_P1 = HERE.parent / "board-p1" / "busy_light_spike.kicad_pcb"
EPS = 1e-9
ANT_STRIP_MM = 4.6
MODULE_SIZE = (13.2, 16.6)  # width, length (ESP32-C3-MINI-1), antenna at the -y end of the local frame
SWITCH_TL3342 = (6.4, 5.2)  # F.Fab body of the stored footprint
SWITCH_TL3342_COURTYARD = (8.5, 6.0)
SWITCH_B3U = (3.0, 2.5)  # Omron catalogue headline, the land pattern is not read


def _balanced(text: str, start: int) -> str:
    """The parenthesised block that starts at text[start] == '('."""
    depth = 0
    for j in range(start, len(text)):
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                return text[start : j + 1]
    raise ValueError("unbalanced parentheses in the board text")


def _blocks(text: str, head: str) -> list[str]:
    out: list[str] = []
    i = text.find(head)
    while i >= 0:
        blk = _balanced(text, i)
        out.append(blk)
        i = text.find(head, i + len(blk))
    return out


def read_footprint_outline(
    pcb_text: str,
    ref: str,
    layer: str = "F.Fab",
    board_centre: Point = (40.0, 40.0),
) -> Poly:
    """Bounding rectangle of the fp_line items of one layer of a footprint, in board-centred KiCad coordinates.

    KiCad rotation: X = x + lx cos t + ly sin t and Y = y - lx sin t + ly cos t for the footprint angle t.
    The corners are returned as (x0, y0), (x1, y0), (x1, y1), (x0, y1); exact for rotations of 0, 90, 180
    and 270 degrees.
    """
    key = f'(property "Reference" "{ref}"'
    k = pcb_text.find(key)
    if k < 0:
        raise ValueError(f"reference {ref} not found")
    s = pcb_text.rfind("(footprint", 0, k)
    fp = _balanced(pcb_text, s)
    at = re.search(r"\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)", fp)
    if at is None:
        raise ValueError(f"no position for {ref}")
    x, y = float(at.group(1)), float(at.group(2))
    t = math.radians(float(at.group(3) or 0.0))
    xs: list[float] = []
    ys: list[float] = []
    for b in _blocks(fp, "(fp_line"):
        if f'(layer "{layer}")' not in b:
            continue
        m = re.search(r"\(start ([-\d.]+) ([-\d.]+)\)\s*\(end ([-\d.]+) ([-\d.]+)\)", b)
        if m is None:
            continue
        for lx, ly in ((float(m.group(1)), float(m.group(2))), (float(m.group(3)), float(m.group(4)))):
            xs.append(x + lx * math.cos(t) + ly * math.sin(t) - board_centre[0])
            ys.append(y - lx * math.sin(t) + ly * math.cos(t) - board_centre[1])
    if not xs:
        raise ValueError(f"no {layer} lines for {ref}")
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def rect(cx: float, cy: float, w: float, h: float, angle_deg: float) -> Poly:
    """Rectangle w x h centred at (cx, cy), rotated counter-clockwise (y up)."""
    a = math.radians(angle_deg)
    c, s = math.cos(a), math.sin(a)
    return [
        (cx + px * c - py * s, cy + px * s + py * c)
        for px, py in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))
    ]


def led_squares(
    r_mm: float = 20.0, n: int = 16, phase_deg: float = 3.75, size_mm: float = 2.0
) -> list[Poly]:
    """LED k is at phase_deg + 360 k / n on the ring radius, a square with its sides along the tangent."""
    out: list[Poly] = []
    for k in range(n):
        az = phase_deg + 360.0 * k / n
        out.append(
            rect(
                r_mm * math.cos(math.radians(az)),
                r_mm * math.sin(math.radians(az)),
                size_mm,
                size_mm,
                az,
            )
        )
    return out


def antenna_strip(
    body: Sequence[Point], strip_mm: float = ANT_STRIP_MM, end: str = "min_x"
) -> Poly:
    """The strip of the bounding rectangle of body that lies strip_mm from the stated end (min_x or max_x)."""
    xs = [p[0] for p in body]
    ys = [p[1] for p in body]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    if end == "min_x":
        x1 = x0 + strip_mm
    elif end == "max_x":
        x0 = x1 - strip_mm
    else:
        raise ValueError("end must be min_x or max_x")
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _centre(poly: Sequence[Point]) -> Point:
    return (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))


def _cross(o: Point, a: Point, b: Point) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _inside(p: Point, poly: Sequence[Point]) -> bool:
    signs = [_cross(poly[i], poly[(i + 1) % len(poly)], p) for i in range(len(poly))]
    return all(v >= -EPS for v in signs) or all(v <= EPS for v in signs)


def _seg_dist(p: Point, a: Point, b: Point) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    ll = dx * dx + dy * dy
    t = 0.0 if ll == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / ll))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))


def point_poly_distance(p: Point, poly: Sequence[Point]) -> float:
    """Distance from a point to a convex polygon (0 inside)."""
    if _inside(p, poly):
        return 0.0
    return min(_seg_dist(p, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))


def poly_distance(a: Sequence[Point], b: Sequence[Point]) -> float:
    """Distance between two convex polygons (0 if they touch or overlap)."""
    if any(_inside(p, b) for p in a) or any(_inside(p, a) for p in b):
        return 0.0
    na, nb = len(a), len(b)
    for i in range(na):
        for j in range(nb):
            p1, p2, q1, q2 = a[i], a[(i + 1) % na], b[j], b[(j + 1) % nb]
            if _cross(p1, p2, q1) * _cross(p1, p2, q2) < 0 and _cross(q1, q2, p1) * _cross(q1, q2, p2) < 0:
                return 0.0
    best = math.inf
    for i in range(na):
        for p in b:
            best = min(best, _seg_dist(p, a[i], a[(i + 1) % na]))
    for j in range(nb):
        for p in a:
            best = min(best, _seg_dist(p, b[j], b[(j + 1) % nb]))
    return best


def nearest_led_distance(strip: Sequence[Point], leds: Sequence[Sequence[Point]]) -> float:
    """Smallest distance from an LED centre to the strip."""
    return min(point_poly_distance(_centre(led), strip) for led in leds)


def _conflict(distance: float, gap: float) -> bool:
    """A distance below the gap conflicts; touching or overlapping always conflicts (also for gap 0)."""
    return distance < gap - EPS or distance <= EPS


def s2_poses(  # noqa: PLR0913, PLR0917
    module_size: tuple[float, float],
    switch_size: tuple[float, float],
    switch_gap_mm: float,
    led_gap_mm: float,
    corner_radius_mm: float,
    extent_mm: float,
    step_mm: float,
    step_deg: float,
) -> list[Pose]:
    """Module poses (x, y, angle) with the switch at the origin (axis-aligned, long side along x).

    module_size is (width, length); the module is the local rectangle width along x and length along y,
    rotated by the angle and centred at (x, y). x and y run from -extent to +extent in step_mm, the angle
    from 0 to 177 degrees in step_deg (the full circle doubles every count). A pose is valid when all
    module corners are within corner_radius_mm of the origin, the distance to the switch is at least
    switch_gap_mm and the distance to every LED square at least led_gap_mm. One entry per (x, y, angle);
    the antenna end is chosen later (best_antenna_distance tries both ends).
    """
    width, length = module_size
    leds = led_squares()
    led_centres = [_centre(p) for p in leds]
    sw = rect(0.0, 0.0, switch_size[0], switch_size[1], 0.0)
    n = round(2 * extent_mm / step_mm) + 1
    coords = [-extent_mm + i * step_mm for i in range(n)]
    angles = [i * step_deg for i in range(int(177.0 / step_deg + EPS) + 1)]
    reach = math.hypot(width, length) / 2 + led_gap_mm + 2.0
    out: list[Pose] = []
    for ang in angles:
        for x in coords:
            for y in coords:
                body = rect(x, y, width, length, ang)
                if max(math.hypot(px, py) for px, py in body) > corner_radius_mm + EPS:
                    continue
                if _conflict(poly_distance(body, sw), switch_gap_mm):
                    continue
                ok = True
                for led, c in zip(leds, led_centres, strict=True):
                    if math.hypot(c[0] - x, c[1] - y) > reach + 1.0:
                        continue
                    if _conflict(poly_distance(body, led), led_gap_mm):
                        ok = False
                        break
                if ok:
                    out.append((x, y, ang))
    return out


def best_antenna_distance(
    poses: Sequence[Pose],
    module_size: tuple[float, float] = MODULE_SIZE,
    strip_mm: float = ANT_STRIP_MM,
    leds: Sequence[Sequence[Point]] | None = None,
) -> float:
    """Largest over the poses and both antenna ends of the antenna-strip to nearest-LED-centre distance.

    The antenna end is the -y end of the local frame, or the +y end when flipped. Returns 0 for no pose.
    """
    leds = led_squares() if leds is None else leds
    width, length = module_size
    best = 0.0
    for x, y, ang in poses:
        a = math.radians(ang)
        for sign in (-1.0, 1.0):
            off = sign * (length / 2 - strip_mm / 2)
            cx = x - off * math.sin(a)
            cy = y + off * math.cos(a)
            strip = rect(cx, cy, width, strip_mm, ang)
            best = max(best, nearest_led_distance(strip, leds))
    return best


def _gap(a: Sequence[Point], b: Sequence[Point]) -> float:
    return poly_distance(a, b)


def s3_conflicts(  # noqa: PLR0913, PLR0917
    switch_centres: Sequence[Point],
    switch_size: tuple[float, float],
    switch_rotation_deg: float,
    module_body: Sequence[Point],
    antenna_strip_poly: Sequence[Point],
    leds: Sequence[Sequence[Point]],
    clearance_mm: float,
) -> list[str]:
    """One string per conflict of a switch with the module, the antenna strip or an LED."""
    out: list[str] = []
    for i, (cx, cy) in enumerate(switch_centres):
        r = rect(cx, cy, switch_size[0], switch_size[1], switch_rotation_deg)
        if _conflict(_gap(r, module_body), clearance_mm):
            out.append(f"SW{i} overlaps module")
        if _conflict(_gap(r, antenna_strip_poly), clearance_mm):
            out.append(f"SW{i} overlaps antenna strip")
        for j, led in enumerate(leds):
            if _conflict(_gap(r, led), clearance_mm):
                out.append(f"SW{i} overlaps LED{j}")
    return out


S3_ORIENTATIONS_DEG = (0.0, 45.0, 90.0, 135.0)  # absolute rotation of the switch long axis


def s3_scan(  # noqa: PLR0913, PLR0917
    r_mm: float,
    switch_size: tuple[float, float],
    clearance_mm: float,
    module_body: Sequence[Point],
    antenna_strip_poly: Sequence[Point],
    leds: Sequence[Sequence[Point]],
) -> tuple[int, int, float, float]:
    """Three switches at 120 degrees on the radius r_mm, azimuths 90 + rot + 120 k, rot 0 to 119 degrees
    in 1 degree steps, with the four absolute switch orientations (all three switches share it).

    Returns (feasible, total, best gap to the body, best gap to the strip). A configuration is feasible
    without conflict (clearance_mm as in s3_conflicts). The best gap is the largest, over the feasible
    configurations, of the smallest gap of the three switches (the two maxima are independent).
    """
    feasible = 0
    total = 0
    best_body = 0.0
    best_strip = 0.0
    for rot in range(120):
        centres = [
            (
                r_mm * math.cos(math.radians(90 + rot + 120 * k)),
                r_mm * math.sin(math.radians(90 + rot + 120 * k)),
            )
            for k in range(3)
        ]
        for orient in S3_ORIENTATIONS_DEG:
            total += 1
            if s3_conflicts(
                centres, switch_size, orient, module_body, antenna_strip_poly, leds, clearance_mm
            ):
                continue
            feasible += 1
            rs = [rect(cx, cy, switch_size[0], switch_size[1], orient) for cx, cy in centres]
            best_body = max(best_body, min(_gap(r, module_body) for r in rs))
            best_strip = max(best_strip, min(_gap(r, antenna_strip_poly) for r in rs))
    return feasible, total, best_body, best_strip


def fill_fraction(
    movable_mm2: float,
    available_mm2: float,
    extra_movable_mm2: float = 0.0,
    fixed_delta_mm2: float = 0.0,
) -> float:
    """Fill of the ring interior: (movable + extra) courtyards over the available area.

    available_mm2 is the interior left after the module, its strip and the fixed parts (plan 08 A3: about
    650 mm2 at r = 17.3 mm, movable courtyards about 430 mm2). fixed_delta_mm2 is the change of the fixed
    courtyards (negative when SW1 gets smaller), which changes the available area by the opposite amount.
    """
    return (movable_mm2 + extra_movable_mm2) / (available_mm2 - fixed_delta_mm2)


def main() -> None:
    pcb = BOARD_P1.read_text(encoding="utf-8")
    leds = led_squares()
    body = read_footprint_outline(pcb, "U9")
    strip = antenna_strip(body)
    sw1 = read_footprint_outline(pcb, "SW1")
    sw1_yard = read_footprint_outline(pcb, "SW1", layer="F.CrtYd")
    print(f"U9 body {_size(body)} mm, SW1 body {_size(sw1)} mm, SW1 courtyard {_size(sw1_yard)} mm")
    base = nearest_led_distance(strip, leds)
    print(f"Stored board: antenna strip to nearest LED centre {base:.2f} mm")
    cases = (
        ("TL3342 body 6.4 x 5.2, gap 1.0", SWITCH_TL3342, 1.0),
        ("TL3342 courtyard 8.5 x 6.0, gap 0", SWITCH_TL3342_COURTYARD, 0.0),
        ("B3U body 3.0 x 2.5, gap 1.0", SWITCH_B3U, 1.0),
        ("B3U body + 0.5 mm each side 4.0 x 3.5, gap 1.0", (4.0, 3.5), 1.0),
    )
    print("S2: module moved, switch at the centre (0.5 mm and 3 degree grid, rotation 0 to 177):")
    for name, size, gap in cases:
        poses = s2_poses(MODULE_SIZE, size, gap, 0.5, 19.5, 14.0, 0.5, 3.0)
        best = best_antenna_distance(poses, MODULE_SIZE, ANT_STRIP_MM, leds)
        pct = 100 * best / base
        print(f"   {name}: {len(poses)} poses, best strip to LED {best:.2f} mm ({pct:.0f} % of {base:.2f})")
    print("S3: three switches at r = 11 mm around the stored module:")
    for name, size in (
        ("TL3342 body 6.4 x 5.2", SWITCH_TL3342),
        ("TL3342 courtyard 8.5 x 6.0", SWITCH_TL3342_COURTYARD),
        ("B3U body 3.0 x 2.5", SWITCH_B3U),
    ):
        ok, tot, gb, gs = s3_scan(11.0, size, 0.0, body, strip, leds)
        print(f"   {name}: {ok} of {tot} feasible, best gap to body {gb:.2f} mm, to strip {gs:.2f} mm")
    print("Fill of the ring interior (plan 08 A3 figures: 430 mm2 movable, 650 mm2 available, not recomputed):")
    today = fill_fraction(430.0, 650.0)
    s2_b3u = fill_fraction(430.0, 650.0, fixed_delta_mm2=4.0 * 3.5 - 8.5 * 6.0)
    s3_tl = fill_fraction(430.0, 650.0, extra_movable_mm2=2 * 8.5 * 6.0)
    print(f"   today {100 * today:.0f} %, S2 with the B3U courtyard (4.0 x 3.5) {100 * s2_b3u:.0f} %,")
    print(f"   S3 with two more TL3342 courtyards {100 * s3_tl:.0f} %")


def _size(poly: Sequence[Point]) -> str:
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return f"{max(xs) - min(xs):.2f} x {max(ys) - min(ys):.2f}"


if __name__ == "__main__":
    main()
    sys.exit(0)
