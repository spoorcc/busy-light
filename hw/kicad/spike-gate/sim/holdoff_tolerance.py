# SPDX-License-Identifier: Apache-2.0
"""Worst-case hold-off of an RC from a rail: t = R*C*ln(1/(1-k)), k = threshold / rail.

Inputs are assumptions, not datasheet values: tolerances and the threshold span k_min..k_max.
Prints the nominal R*C needed so that the minimum time is at least T_MIN, and the resulting
maximum time. Run: python3 -I holdoff_tolerance.py
"""
import math

T_MIN = 0.200            # s, HW-010 hold-off (Draft)
R_TOL, C_TOL = 0.05, 0.20  # 5 % resistor, 20 % capacitor (X7R over temperature and bias): assumed
for label, kmin, kmax in (("ideal half-rail", 0.5, 0.5),
                          ("CMOS input, 0.30 to 0.70 of rail (assumed)", 0.30, 0.70),
                          ("Schmitt input, 0.40 to 0.60 of rail (assumed)", 0.40, 0.60)):
    lo = math.log(1 / (1 - kmin))     # shortest time factor
    hi = math.log(1 / (1 - kmax))     # longest time factor
    tau_nom = T_MIN / (lo * (1 - R_TOL) * (1 - C_TOL))
    t_max = tau_nom * (1 + R_TOL) * (1 + C_TOL) * hi
    print(f"{label:48s} nominal R*C {tau_nom*1e3:6.0f} ms -> min {T_MIN*1e3:.0f} ms, max {t_max*1e3:6.0f} ms")
