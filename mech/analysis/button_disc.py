#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Statics of a rigid centre disc on springs and switches (plan 09, MECH-004, MECH-010 proposal).

Model: a rigid disc moves as a plane w(x, y) = a + b x + c y on linear supports; every support i has
the stiffness k_i (N/mm) at (x_i, y_i); a load F at (x, y) gives the plane that solves the three
equilibrium equations sum_i k_i v_i v_i^T [a b c]^T = F [1 x y]^T with v_i = [1, x_i, y_i]. Supports
act both ways (bilateral). Units: mm, N, N/mm, MPa. Standard library only.

Run: python3 -I mech/analysis/button_disc.py (prints the matrix of plan 09 section 3.2 and the
bands).

Analysis only. The switch click values come from datasheets (hw/evidence/parts/sw-*.yaml); the
PETG modulus and the bridge geometry are assumptions. Nothing is measured.
"""

import math
import random
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

Support = tuple[float, float, float]  # x mm, y mm, stiffness N/mm
Plane = tuple[float, float, float]  # a mm, b, c with w(x, y) = a + b x + c y
Point = tuple[float, float]

SINGULAR_EPS = 1e-12
LIFT_EPS = 1e-9
BRIDGE_ANGLES_DEG = (90.0, 210.0, 330.0)
K_SEARCH_LOW = 0.1  # N/mm, lower end of the bridge stiffness search
K_SEARCH_HIGH = 20.0  # N/mm, upper end of the bridge stiffness search
BISECT_STEPS = 80
N_BRIDGES = 3


def _det3(m: Sequence[Sequence[float]]) -> float:
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def solve_plane(supports: Sequence[Support], load_xy: Point, force_n: float) -> Plane:
    """Plane [a, b, c] of the disc for a load force_n at load_xy (Cramer's rule); ValueError if
    singular."""
    a = [[0.0] * 3 for _ in range(3)]
    for x, y, k in supports:
        v = (1.0, x, y)
        for i in range(3):
            for j in range(3):
                a[i][j] += k * v[i] * v[j]
    rhs = (force_n, force_n * load_xy[0], force_n * load_xy[1])
    det = _det3(a)
    if abs(det) < SINGULAR_EPS:
        raise ValueError("the supports do not hold the disc (singular stiffness matrix)")
    out: list[float] = []
    for col in range(3):
        m = [row[:] for row in a]
        for i in range(3):
            m[i][col] = rhs[i]
        out.append(_det3(m) / det)
    return out[0], out[1], out[2]


def displacement(plane: Plane, point: Point) -> float:
    """Displacement of the disc at a point."""
    return plane[0] + plane[1] * point[0] + plane[2] * point[1]


def sample_points(
    radius_mm: float,
    n_random: int,
    n_boundary: int,
    seed: int,
    extra: Sequence[Point] = (),
) -> list[Point]:
    """Press points: n_random uniform in the disc (u first, then v, from random.Random(seed)), then
    extra, then n_boundary equally spaced on the boundary starting at angle 0."""
    rng = random.Random(seed)  # noqa: S311 - deterministic sampling, not security
    pts: list[Point] = []
    for _ in range(n_random):
        u = rng.random()
        v = rng.random()
        r = radius_mm * math.sqrt(u)
        pts.append((r * math.cos(2 * math.pi * v), r * math.sin(2 * math.pi * v)))
    pts.extend(extra)
    for i in range(n_boundary):
        ang = 2 * math.pi * i / n_boundary
        pts.append((radius_mm * math.cos(ang), radius_mm * math.sin(ang)))
    return pts


@dataclass(frozen=True)
class PressMetrics:
    """Result of a press sweep. Lift points are not in the force and travel ranges."""

    force_min_n: float
    force_max_n: float
    travel_max_mm: float
    lift_points: int


def press_metrics(
    supports: Sequence[Support],
    switches: Sequence[Support],
    click_travel_mm: float,
    points: Sequence[Point],
) -> PressMetrics:
    """For each press point: the load at which the first switch plunger reaches click_travel_mm (F),
    and the press-point travel at that load. A point whose plunger travel is not positive counts as
    a lift point. If every point lifts, the forces are inf and the travel is 0."""
    allsup = [*supports, *switches]
    forces: list[float] = []
    travels: list[float] = []
    lift = 0
    for p in points:
        plane = solve_plane(allsup, p, 1.0)
        w = max(displacement(plane, (sx, sy)) for sx, sy, _ in switches)
        if w <= LIFT_EPS:
            lift += 1
            continue
        f = click_travel_mm / w
        forces.append(f)
        travels.append(f * displacement(plane, p))
    if not forces:
        return PressMetrics(math.inf, math.inf, 0.0, lift)
    return PressMetrics(min(forces), max(forces), max(travels), lift)


def bridges(radius_mm: float, stiffness: float) -> list[Support]:
    """Three equal bridges at 90, 210 and 330 degrees."""
    return [
        (
            radius_mm * math.cos(math.radians(a)),
            radius_mm * math.sin(math.radians(a)),
            stiffness,
        )
        for a in BRIDGE_ANGLES_DEG
    ]


def s2_click_force(
    switch_force_n: float, bridge_k: float, n_bridges: int, click_travel_mm: float
) -> float:
    """Click force of the centred switch (S2). The disc moves rigidly at the centre switch, so the
    force is the same at every press point: F = switch force + n k x."""
    return switch_force_n + n_bridges * bridge_k * click_travel_mm


def click_force_extremes(  # noqa: PLR0913, PLR0917
    switch_force_n: float,
    force_tol_n: float,
    click_travel_min_mm: float,
    click_travel_max_mm: float,
    bridge_k: float,
    n_bridges: int,
) -> tuple[float, float]:
    """(F - tol + n k x_min, F + tol + n k x_max)."""
    return (
        switch_force_n - force_tol_n + n_bridges * bridge_k * click_travel_min_mm,
        switch_force_n + force_tol_n + n_bridges * bridge_k * click_travel_max_mm,
    )


def _max_travel(  # noqa: PLR0913, PLR0917
    switch_force_n: float,
    click_travel_mm: float,
    k: float,
    points: Sequence[Point],
    bridge_r_mm: float,
) -> float:
    ks = switch_force_n / click_travel_mm
    m = press_metrics(bridges(bridge_r_mm, k), [(0.0, 0.0, ks)], click_travel_mm, points)
    return m.travel_max_mm


def bridge_band(  # noqa: PLR0913, PLR0917
    switch_force_n: float,
    force_tol_n: float,
    click_travel_mm: float,
    window_n: tuple[float, float],
    travel_limit_mm: float,
    points: Sequence[Point],
    bridge_r_mm: float = 14.0,
) -> tuple[float, float]:
    """(k_low, k_high) in N/mm of three bridges that meet the force window and the travel limit.

    The window is met with the switch force tolerance added, the travel limit at the largest
    press-point travel. ValueError if the travel limit is not met up to 20 N/mm or k_low > k_high.
    """

    def excess(k: float) -> float:
        return (
            _max_travel(switch_force_n, click_travel_mm, k, points, bridge_r_mm) - travel_limit_mm
        )

    if excess(K_SEARCH_HIGH) > 0:
        raise ValueError(f"travel limit not met up to {K_SEARCH_HIGH:g} N/mm")
    lo, hi = K_SEARCH_LOW, K_SEARCH_HIGH
    if excess(lo) <= 0:
        k_travel = lo
    else:
        for _ in range(BISECT_STEPS):
            mid = (lo + hi) / 2
            if excess(mid) > 0:
                lo = mid
            else:
                hi = mid
        k_travel = hi
    unit = N_BRIDGES * click_travel_mm
    k_force_low = (window_n[0] - (switch_force_n - force_tol_n)) / unit
    k_high = (window_n[1] - (switch_force_n + force_tol_n)) / unit
    k_low = max(k_travel, k_force_low)
    if k_low > k_high:
        raise ValueError(f"no stiffness meets both limits (low {k_low:.2f} > high {k_high:.2f})")
    return k_low, k_high


def guided_beam_stiffness(e_mpa: float, w_mm: float, t_mm: float, length_mm: float) -> float:
    """Fixed-guided beam, N/mm: E w t^3 / L^3."""
    return e_mpa * w_mm * t_mm**3 / length_mm**3


def arm_stress(e_mpa: float, t_mm: float, length_mm: float, stroke_mm: float) -> float:
    """Peak bending stress (MPa) of a fixed-guided beam at a stroke: 3 E t stroke / L^2."""
    return 3.0 * e_mpa * t_mm * stroke_mm / length_mm**2


def guide_jam_length(e_mm: float, mu: float) -> float:
    """Shortest guide length (mm) that does not jam for a load offset e: 2 mu e."""
    return 2.0 * mu * e_mm


def plate_deflection(  # noqa: PLR0913, PLR0917
    radius_mm: float,
    thickness_mm: float,
    e_mpa: float,
    nu: float,
    force_n: float,
    edge: Literal["simply_supported", "clamped"],
) -> float:
    """Central deflection (mm) of a round plate under a central load (edge presses not covered)."""
    d = e_mpa * thickness_mm**3 / (12.0 * (1.0 - nu**2))
    if edge == "simply_supported":
        return force_n * radius_mm**2 * (3.0 + nu) / (16.0 * math.pi * d * (1.0 + nu))
    return force_n * radius_mm**2 / (16.0 * math.pi * d)


# Working values for the report. Click force and pre-travel are datasheet values except the TL3342
# travel
# (not published: assumed). Name, force N, tolerance N, click travel mm.
SWITCHES = (
    ("TL3342F160QG (travel assumed)", 1.57, 0.49, 0.25),
    ("B3U-1000P", 1.50, 0.49, 0.15),
    ("KSC221JLFS", 2.00, 0.50, 0.35),
)
WINDOW_N = (2.0, 5.0)
TRAVEL_LIMIT_MM = 1.0
R_USE_MM = 13.0
N_RANDOM = 600
N_BOUNDARY = 48
SEED = 7
B3U_PRETRAVEL_MM = (0.05, 0.35)  # 0.15 +0.2/-0.1 mm, typeset table of the Omron catalogue
B3U_PRETRAVEL_TEXT_MM = (0.05, 0.25)  # the PDF text layer reads 0.15 +- 0.1


def main() -> None:
    pts = sample_points(R_USE_MM, N_RANDOM, N_BOUNDARY, SEED, extra=[(0.0, 0.0)])
    print("S2: switch at the centre, three bridges at r = 14 mm; press points inside R_use = 13 mm")
    for name, f, tol, x in SWITCHES:
        print(f"{name}: {f} N +- {tol} N, click travel {x} mm, switch {f / x:.1f} N/mm")
        for k in (1.0, 2.0, 3.0, 4.0, 6.0):
            m = press_metrics(bridges(14.0, k), [(0.0, 0.0, f / x)], x, pts)
            print(
                f"   k = {k:g} N/mm: F {m.force_min_n:.2f} to {m.force_max_n:.2f} N, "
                f"press-point travel {m.travel_max_mm:.2f} mm, lift points {m.lift_points}"
            )
        try:
            lo, hi = bridge_band(f, tol, x, WINDOW_N, TRAVEL_LIMIT_MM, pts)
            print(f"   band: k from {lo:.2f} to {hi:.2f} N/mm (ratio {hi / lo:.1f})")
        except ValueError as exc:
            print(f"   band: no band ({exc})")
    name, f, tol, _ = SWITCHES[1]
    for label, (xa, xb) in (("typeset", B3U_PRETRAVEL_MM), ("text layer", B3U_PRETRAVEL_TEXT_MM)):
        lo_f, hi_f = click_force_extremes(f, tol, xa, xb, 3.0, N_BRIDGES)
        print(
            f"{name}, k = 3 N/mm, pre-travel {xa} to {xb} mm ({label} reading): "
            f"click force {lo_f:.2f} to {hi_f:.2f} N against the window {WINDOW_N}"
        )
    sws = [
        (11.0 * math.cos(math.radians(a)), 11.0 * math.sin(math.radians(a)), 1.6 / 0.25)
        for a in BRIDGE_ANGLES_DEG
    ]
    m3 = press_metrics([], sws, 0.25, pts)
    print(
        f"M3: three TL3342 switches at r = 11 mm, rigid disc: F {m3.force_min_n:.2f} to "
        f"{m3.force_max_n:.2f} N, press-point travel {m3.travel_max_mm:.2f} mm"
    )


if __name__ == "__main__":
    main()
    sys.exit(0)
