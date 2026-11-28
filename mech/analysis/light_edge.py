#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Luminance at the end of an LED arc behind a light wall (ADR-0027, MECH-015 proposal).

Model: the LEDs of one arc are point sources with a Lambertian pattern at the height d above the
LED plane (the diffuser underside). A source at the lateral distance x from a point of the diffuser
gives E(x) = d^2 / (d^2 + x^2)^2. The arc has n LEDs at the pitch p; the first LED is half a pitch
from the wall at s = 0 and the last half a pitch from the wall at s = n * p. A wall is either
absorbing (only the real LEDs count) or a mirror (the images of the LEDs behind the walls count
too: a white wall face with a reflectance of 1). Units: mm. Standard library only.

Run: python3 -I mech/analysis/light_edge.py (prints the table of ADR-0027).

Analysis only. Nothing is measured: the real reflectance of a white printed or painted face is
below 1 and the real diffuser spreads the light sideways inside the insert; the coupon test of
TC-317 measures both.
"""

import sys
from typing import Literal

Wall = Literal["absorbing", "mirror"]

D_DIFF_MM = 8.0  # LED to diffuser underside, plan 05 (working value)
MIRROR_ORDERS = 3  # reflection orders on each side of the arc (the sum converges fast)
MIN_LEDS = 4  # fewer LEDs have no plateau to compare with
STEP_MM = 0.05  # search step for the 90 % distance
REF_STEP_MM = 0.1  # sampling step for the plateau reference
PROBES_MM = (0.0, 1.0, 2.6, 5.2, 7.8, 10.4, 15.6)  # distances from the wall in the ADR table
NINETY_PERCENT = 0.9


def point_source(x_mm: float, d_mm: float) -> float:
    """Relative illuminance of a Lambertian point source, lateral distance x, height d."""
    return d_mm**2 / (d_mm**2 + x_mm**2) ** 2


def led_positions(n: int, pitch_mm: float) -> list[float]:
    """Positions along the arc from the wall at s = 0: half a pitch, then one pitch apart."""
    if n < MIN_LEDS or pitch_mm <= 0.0:
        raise ValueError(f"an arc needs at least {MIN_LEDS} LEDs and a positive pitch")
    return [pitch_mm / 2.0 + k * pitch_mm for k in range(n)]


def luminance(s_mm: float, n: int, pitch_mm: float, wall: Wall, d_mm: float = D_DIFF_MM) -> float:
    """Relative luminance at s along the arc (0 = first wall, n * pitch = second wall)."""
    length = n * pitch_mm
    total = 0.0
    for x in led_positions(n, pitch_mm):
        total += point_source(s_mm - x, d_mm)
        if wall == "mirror":
            # two parallel mirrors at s = 0 and s = length: images at x + 2 L m and -x + 2 L m
            for m in range(-MIRROR_ORDERS, MIRROR_ORDERS + 1):
                if m != 0:
                    total += point_source(s_mm - (x + 2.0 * length * m), d_mm)
                total += point_source(s_mm - (-x + 2.0 * length * m), d_mm)
    return total


def plateau(n: int, pitch_mm: float, wall: Wall, d_mm: float = D_DIFF_MM) -> float:
    """Mean luminance over the middle third of the arc, the reference for the edge ratios."""
    length = n * pitch_mm
    values = []
    s = length / 3.0
    while s <= 2.0 * length / 3.0:
        values.append(luminance(s, n, pitch_mm, wall, d_mm))
        s += REF_STEP_MM
    return sum(values) / len(values)


def edge_ratio(s_mm: float, n: int, pitch_mm: float, wall: Wall, d_mm: float = D_DIFF_MM) -> float:
    """Luminance at s relative to the plateau of the same arc."""
    return luminance(s_mm, n, pitch_mm, wall, d_mm) / plateau(n, pitch_mm, wall, d_mm)


def distance_to_fraction(
    fraction: float, n: int, pitch_mm: float, wall: Wall, d_mm: float = D_DIFF_MM
) -> float:
    """Smallest distance from the wall where the luminance reaches `fraction` of the plateau."""
    ref = plateau(n, pitch_mm, wall, d_mm)
    s = 0.0
    while s < n * pitch_mm / 2.0:
        if luminance(s, n, pitch_mm, wall, d_mm) / ref >= fraction:
            return s
        s += STEP_MM
    raise ValueError(f"the luminance never reaches {fraction:.2f} of the plateau")


def table(n: int = 12, pitch_mm: float = 5.2) -> list[str]:
    """Rows of the ADR-0027 table: percent of the plateau at the probe distances."""
    head = " ".join(f"{p:5.1f}" for p in PROBES_MM)
    rows = [f"wall      {head}   90 % at (mm)"]
    for wall in ("absorbing", "mirror"):
        ratios = " ".join(f"{100.0 * edge_ratio(p, n, pitch_mm, wall):5.0f}" for p in PROBES_MM)
        d90 = distance_to_fraction(NINETY_PERCENT, n, pitch_mm, wall)
        rows.append(f"{wall:<9} {ratios}   {d90:.1f}")
    return rows


def main() -> int:
    print("Arc of 12 LEDs at 5.2 mm pitch, diffuser 8 mm above the LEDs; percent of the plateau")
    print("\n".join(table()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
