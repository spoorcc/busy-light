# SPDX-License-Identifier: Apache-2.0
"""Layout quality numbers of a routed board (read only; HW-010 spike). The gate says "legal", these say "tidy".

Usage: python3 pcb_quality.py <board.kicad_pcb>      (needs KiCad's pcbnew module)
Numbers: vias, track length (mm), length of segments whose angle is not a multiple of 45 degrees, number of such
segments, number of sharp corners (two same-net segments meeting at less than 90 degrees). Lower is tidier.
`rank_key` is the tie-break of pcb_pick.py: it only compares boards that have the same gate score.
"""
from __future__ import annotations

import math
import re
import sys

NM_PER_MM = 1_000_000.0
ANGLE_TOL_DEG = 0.5


def off_grid_angle(dx: float, dy: float) -> bool:
    """True when the segment direction is not a multiple of 45 degrees (zero length counts as on grid)."""
    if dx == 0 and dy == 0:
        return False
    a = abs(math.degrees(math.atan2(dy, dx))) % 45.0
    return min(a, 45.0 - a) > ANGLE_TOL_DEG


def corner_angle(u: tuple[float, float], v: tuple[float, float]) -> float:
    """Interior angle in degrees between two segments that leave the same point in directions u and v."""
    nu, nv = math.hypot(*u), math.hypot(*v)
    if nu == 0 or nv == 0:
        return 180.0
    c = max(-1.0, min(1.0, (u[0] * v[0] + u[1] * v[1]) / (nu * nv)))
    return math.degrees(math.acos(c))


def metrics_of(segments: list[tuple[str, int, tuple[float, float], tuple[float, float]]], vias: int) -> dict:
    """segments: (net, layer, start, end) in nm. Returns the quality numbers."""
    length = off_len = 0.0
    off_n = 0
    ends: dict[tuple, list[tuple[float, float]]] = {}
    for net, layer, a, b in segments:
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        length += ln
        if off_grid_angle(dx, dy):
            off_len += ln
            off_n += 1
        ends.setdefault((net, layer, a), []).append((dx, dy))
        ends.setdefault((net, layer, b), []).append((-dx, -dy))
    sharp = 0
    for dirs in ends.values():
        if len(dirs) == 2 and corner_angle(dirs[0], dirs[1]) < 89.5:
            sharp += 1
    return {"vias": vias, "track_mm": round(length / NM_PER_MM, 1), "off45_mm": round(off_len / NM_PER_MM, 1),
            "off45_segments": off_n, "sharp_corners": sharp}


def rank_key(m: dict) -> tuple:
    """Lower is better: sharp corners and off-45 length (not the count: most are 0.1 mm pad jogs) first (they look wrong), then vias, then length."""
    return (m["sharp_corners"], m["off45_mm"], m["vias"], m["track_mm"])


def ring_unevenness(points: list[tuple[float, float]]) -> float:
    """Spread (max gap - min gap, degrees) of the angular gaps of points around their centroid; 0 = even ring."""
    if len(points) < 3:
        return 0.0
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    ang = sorted(math.degrees(math.atan2(p[1] - cy, p[0] - cx)) % 360.0 for p in points)
    gaps = [(ang[(i + 1) % len(ang)] - ang[i]) % 360.0 for i in range(len(ang))]
    return round(max(gaps) - min(gaps), 2)


def aligned_share(points: list[tuple[float, float]], tol: float = 0.05) -> float:
    """Share of points that sit in a row or column (same x or same y within tol mm) with another point."""
    if not points:
        return 0.0
    hit = 0
    for i, p in enumerate(points):
        if any(i != j and (abs(p[0] - q[0]) <= tol or abs(p[1] - q[1]) <= tol) for j, q in enumerate(points)):
            hit += 1
    return round(hit / len(points), 3)


def orthogonal_share(angles: list[float], tol: float = 0.5) -> float:
    """Share of rotations (degrees) that are a multiple of 90."""
    if not angles:
        return 0.0
    ok = sum(min(abs(a) % 90.0, 90.0 - abs(a) % 90.0) <= tol for a in angles)
    return round(ok / len(angles), 3)


def mean_partner_distance(passives: dict, pads: dict, skip_nets: tuple = ("GND",)) -> float:
    """Mean distance (mm) of each passive to the nearest pad of another part on one of its non-skipped nets.
    passives: ref -> (x, y, [nets]); pads: net -> [(ref, x, y)]."""
    ds = []
    for ref, (x, y, nets) in passives.items():
        best = None
        for n in nets:
            if n in skip_nets:
                continue
            for r, px, py in pads.get(n, []):
                if r != ref:
                    d = math.hypot(px - x, py - y)
                    best = d if best is None else min(best, d)
        if best is not None:
            ds.append(best)
    return round(sum(ds) / len(ds), 2) if ds else 0.0


def mean_block_distance(blocks, pos: dict) -> float:
    """Mean distance (mm) of the block members from their anchors. blocks: (anchor, member, radius); pos: ref -> (x, y)."""
    ds = [math.hypot(pos[m][0] - pos[a][0], pos[m][1] - pos[a][1]) for a, m, _ in blocks if a in pos and m in pos]
    return round(sum(ds) / len(ds), 2) if ds else 0.0


def same_orientation_share(families, rot: dict) -> float:
    """Share of family members that point along the majority axis of their family (rotation modulo 180 degrees)."""
    total = hit = 0
    for fam in families:
        axes = [round(rot[r] % 180.0) % 180 for r in fam if r in rot]
        if axes:
            total += len(axes)
            hit += max(axes.count(a) for a in set(axes))
    return round(hit / total, 3) if total else 0.0


def placement_metrics(path: str) -> dict:
    import pcbnew  # noqa: PLC0415
    b = pcbnew.LoadBoard(path)
    import pcb_rules  # noqa: PLC0415
    leds, passives, pads, orient = [], {}, {}, []
    pos, rot, kinds = {}, {}, {}
    for f in b.GetFootprints():
        ref, p = f.GetReference(), f.GetPosition()
        x, y = p.x / NM_PER_MM, p.y / NM_PER_MM
        if ref.startswith("TP"):
            continue
        pos[ref], rot[ref] = (x, y), f.GetOrientationDegrees()
        is_led = ref[0] == "D" and ref[1:].isdigit()
        led_cap = f.GetLayerName() == "B.Cu" and ref[0] == "C" and ref[1:].isdigit() and 8 <= int(ref[1:]) <= 23
        if is_led:
            leds.append((x, y))
        if not (is_led or led_cap):
            orient.append(f.GetOrientationDegrees())
        pl = f.Pads()
        nets = sorted({pl[i].GetNetname() for i in range(len(pl)) if pl[i].GetNetname()})
        if ref[0] in "CR" and ref[1:2] != "P" and len(pl) == 2 and not led_cap:
            passives[ref] = (x, y, nets)
        if not (is_led or led_cap) and ref not in ("U9", "J1", "SW1"):
            kinds.setdefault((re.match("[A-Z]+", ref).group(0), str(f.GetFPID().GetLibItemName())), []).append(ref)
        for i in range(len(pl)):
            q = pl[i].GetPosition()
            pads.setdefault(pl[i].GetNetname(), []).append((ref, q.x / NM_PER_MM, q.y / NM_PER_MM))
    return {"led_ring_gap_spread_deg": ring_unevenness(leds),
            "passives_in_rows": aligned_share([(v[0], v[1]) for v in passives.values()]),
            "parts_on_90deg": orthogonal_share(orient),
            "passive_to_partner_mm": mean_partner_distance(passives, pads),
            "block_member_mm": mean_block_distance(pcb_rules.BLOCKS, pos),
            "like_parts_same_axis": same_orientation_share([v for v in kinds.values() if len(v) >= 2], rot)}


def board_metrics(path: str) -> dict:
    import pcbnew  # noqa: PLC0415 (KiCad's module, only here)
    board = pcbnew.LoadBoard(path)
    segs, vias = [], 0
    tr = board.Tracks()                     # index loop: the SWIG iterator is broken on Python 3.14
    for i in range(tr.size()):
        t = tr[i]
        if t.GetClass() == "PCB_VIA":
            vias += 1
        elif t.GetClass() == "PCB_TRACK":
            s, e = t.GetStart(), t.GetEnd()
            segs.append((t.GetNetname(), t.GetLayer(), (float(s.x), float(s.y)), (float(e.x), float(e.y))))
    return {**metrics_of(segs, vias), **placement_metrics(path)}


if __name__ == "__main__":
    import json
    print(json.dumps(board_metrics(sys.argv[1])))
