#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Light spill of the LED ring onto the centre disc (plan 09 section 4.4, MECH-002).

Model: n point LEDs on a ring, Lambertian emitters, a planar receiver at the height h above the
LED plane. The irradiance at a point at the horizontal distance d from one LED is proportional to
h^2 / (d^2 + h^2)^2. The LEDs are ideal points and the lid is a clear diffuser, so the result is a
first-order ratio and not a luminance measurement. Standard library only.

Run: python3 -I mech/analysis/button_light.py
"""

import math

RING_R_MM = 20.0
N_LED = 16
HEIGHT_MM = 7.7  # LED top (Z 7.25) to the disc underside (Z 14.95); the lid underside is 8.0 mm


def _irradiance(  # noqa: PLR0913, PLR0917
    r_mm: float, azimuth_deg: float, height_mm: float, ring_r_mm: float, n: int, phase_deg: float
) -> float:
    x = r_mm * math.cos(math.radians(azimuth_deg))
    y = r_mm * math.sin(math.radians(azimuth_deg))
    total = 0.0
    for k in range(n):
        a = math.radians(phase_deg + 360.0 * k / n)
        d2 = (x - ring_r_mm * math.cos(a)) ** 2 + (y - ring_r_mm * math.sin(a)) ** 2
        total += height_mm**2 / (d2 + height_mm**2) ** 2
    return total


def ring_irradiance(  # noqa: PLR0913, PLR0917
    r_mm: float,
    height_mm: float = HEIGHT_MM,
    ring_r_mm: float = RING_R_MM,
    n: int = N_LED,
    azimuth_deg: float = 0.0,
    phase_deg: float = 0.0,
) -> float:
    """Irradiance at radius r_mm and azimuth azimuth_deg, relative to the value above one LED.

    The reference point is on the ring radius at azimuth phase_deg. LED k is at
    phase_deg + 360 k / n.
    """
    ref = _irradiance(ring_r_mm, phase_deg, height_mm, ring_r_mm, n, phase_deg)
    return _irradiance(r_mm, azimuth_deg, height_mm, ring_r_mm, n, phase_deg) / ref


def required_transmission(max_ratio: float, r_mm: float, **kwargs: float) -> float:
    """Largest transmission of the disc (0 to 1) that keeps its luminance at radius r_mm under
    max_ratio of the ring luminance.

    The disc is lit only by spill, so its luminance is the spill ratio times the transmission. The
    ring luminance is the value above an LED (ratio 1). kwargs go to ring_irradiance. Plan 09
    section 4.4 (owner decision D7: the light comes from the ring, not from the centre).
    """
    return min(1.0, max_ratio / ring_irradiance(r_mm, **kwargs))


MAX_DISC_RATIO = 0.03  # working value: the disc shows at most 3 % of the ring luminance


def main() -> None:
    print("Irradiance relative to the value above an LED (LED at azimuth 0):")
    print("  r mm   at an LED azimuth   between two LEDs")
    for r in (0, 5, 10, 13, 15, 16, 18, 20):
        at_led = ring_irradiance(r, azimuth_deg=0.0)
        between = ring_irradiance(r, azimuth_deg=360.0 / N_LED / 2)
        print(f"  {r:4d}   {at_led:15.3f}   {between:15.3f}")
    print(
        f"Disc transmission that keeps the disc under {MAX_DISC_RATIO:.0%} of the ring luminance:"
    )
    for r in (0, 13, 15):
        tr = required_transmission(MAX_DISC_RATIO, float(r))
        print(f"  r = {r:2d} mm: at most {tr:.1%} (optical density at least {-math.log10(tr):.2f})")


if __name__ == "__main__":
    main()
