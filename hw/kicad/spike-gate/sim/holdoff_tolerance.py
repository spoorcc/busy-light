# SPDX-License-Identifier: Apache-2.0
"""Worst-case hold-off of an RC from a rail: t = R*C*ln(1/(1-k)), k = threshold / rail.

This is the SUPERSEDED RC alternative (version 3 uses a supervisor, whose delay accuracy must come
from its own datasheet, not read yet). Thresholds for the Schmitt row are from the SN74LVC1G17
datasheet (SCES351Y, Table 5-1): VT+ 2.65 to 3.33 V at 5.5 V and 2.19 to 2.74 V at 4.5 V; the ratio
extremes are 2.65/5.5 and 2.74/4.5. Leakage and DC-bias loss of the capacitor are NOT included.
Tolerances are assumptions. Run: python3 -I holdoff_tolerance.py
"""
import math

T_MIN, T_MAX = 0.200, 0.600   # s, HW-010 window


def run(label, kmin, kmax, r_tol, c_tol):
    lo, hi = math.log(1 / (1 - kmin)), math.log(1 / (1 - kmax))
    tau = T_MIN / (lo * (1 - r_tol) * (1 - c_tol))          # smallest nominal RC that meets T_MIN
    t_max = tau * (1 + r_tol) * (1 + c_tol) * hi
    print(f"{label:46s} R {r_tol:.0%} C {c_tol:.0%}: nominal RC {tau*1e3:5.0f} ms -> {T_MIN*1e3:.0f} to "
          f"{t_max*1e3:4.0f} ms, ratio {t_max/T_MIN:.2f} ({'fits' if t_max <= T_MAX else 'too long'})")


for r_tol, c_tol in ((0.01, 0.10), (0.01, 0.20)):
    run("Schmitt, datasheet ratios 0.482 to 0.609", 2.65 / 5.5, 2.74 / 4.5, r_tol, c_tol)
    run("Schmitt, assumed ratios 0.40 to 0.60", 0.40, 0.60, r_tol, c_tol)
