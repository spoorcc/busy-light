# SPDX-License-Identifier: Apache-2.0
"""Spike: PCB design-rule numbers that need no KiCad module (testable with any Python)."""


def ipc2221_width_mm(current_a, rise_k=10.0, oz=1.0, internal=False):
    """Minimum trace width in mm from IPC-2221 (the curve fit, not a measurement): I = k * dT^0.44 * A^0.725,
    A in square mil, k = 0.048 for an external layer (0.024 internal). 1 oz copper is 1.378 mil thick."""
    k = 0.024 if internal else 0.048
    area_mil2 = (current_a / (k * rise_k ** 0.44)) ** (1.0 / 0.725)
    width_mil = area_mil2 / (1.378 * oz)
    return width_mil * 0.0254


# Highest current the TPS2553 limit may pass in the top step: 1577 mA (HW-010 / analysis-ilim-steps, E192 0.1 % set).
I_TOP_STEP_MAX_A = 1.577
# Net widths in mm used by the spike. IPC-2221 external layer, 1 oz, 10 K rise: 1.5 A -> 0.53 mm, 1.577 A -> 0.56 mm,
# 2.0 A -> 0.78 mm. The spike uses 0.6 mm (>= 0.56 mm for the highest allowed current limit); the earlier run used
# 0.8 mm (2.0 A) and left the VBUS_IC net unrouted.
NET_WIDTH = {"VBUS_IC": 0.6, "+5V": 0.6, "+3V3": 0.4}
