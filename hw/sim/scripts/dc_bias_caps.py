#!/usr/bin/env python3
"""Effective capacitance of the spike-board capacitors under DC bias (HW-014, HW-015).

Retention = 1 + dC/100 from the Samsung Electro-Mechanics Component Library (weblib.samsungsem.com,
DC Bias graph, "DC Bias, dC, 25degC, AC1Vrms, 1kHz"), read from the chart data of the page on
2026-11-09 for each chosen part, at the first listed bias point at or above the check voltage:
  C2 CL10A475KO8NNNC at 5.36 V: 2.008 uF of 4.268 uF at 0 V        -> 0.4705
  C3 CL21A106KAYNNNE at 5.48 V: dC -54.613 %                       -> 0.4539
  C5 CL10A225KO8NNNC at 5.48 V: dC -59.973 %                       -> 0.4003
  C6 CL10A106KP8NNNC at 3.34 V: dC -56.229 %                       -> 0.4377
  100n CL10B104KB8NNN (X7R 50 V) at 5.61 V: 0.10187 uF of 0.10204 uF -> 0.9983 (at 5.12 V: 1.0016)
The curves are typical values of the maker at 25 degC, not guaranteed limits. The retention is applied to
the NOMINAL value, then the tolerance (-10 %) and the X5R temperature spread (-15 %, Samsung reference
specification) are applied on top. This is conservative where the maker's 0 V reading is above nominal
(C5: 2.385 uF against 2.2 uF), and it counts the temperature spread twice in part (the curve is at 25 degC
only; the spread is for the zero-bias value). The Samsung curve is the maker's data but is still not a
guaranteed limit: the bench measurement (HW-014 / HW-015 criterion 2) stays open."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bulk_cap_bounds as bcb  # noqa: E402

TOL = 0.10  # K grade
TEMP = 0.15  # X5R and X7R spread
LOW = (1 - TOL) * (1 - TEMP)  # worst case low
HIGH = (1 + TOL) * (1 + TEMP)  # worst case high (taken at 0 V bias: no loss)
RETENTION = {"C2": 0.4705, "C3": 0.4539, "C5": 0.4003, "C6": 0.4377}  # Samsung curves, see the header

# ref: (net, nominal F, MPN, bias V at the check). Prices of detail: docs/verification/reports.
CAPS = {
    "C2": ("VBUS_IC", 4.7e-6, "CL10A475KO8NNNC", 5.25),
    "C3": ("+5V", 10e-6, "CL21A106KAYNNNE", 5.5),
    "C5": ("+5V", 2.2e-6, "CL10A225KO8NNNC", 5.5),
    "C6": ("+3V3", 10e-6, "CL10A106KP8NNNC", 3.3),
}
C_100N = 0.1e-6  # CL10B104KB8NNNC X7R, 50 V
RETENTION_100N = 0.9983  # Samsung curve at 5.61 V (first point at or above 5.5 V), see the header
N_LED_CAPS = 16  # C8 to C23 on +5V
N_VBUS_BEHIND_R = 3  # C24, C25, C26 behind series resistors (HW-015 criterion 1)
USB_MIN, USB_MAX = 1.0e-6, 10.0e-6  # HW-015
HW014_MAX = 100e-6
LDO_NOMINAL_MIN, LDO_EFFECTIVE_MIN = bcb.C_MIN_LDO_NOMINAL, bcb.C_MIN_LDO_EFFECTIVE


def c_low(nominal: float, retention: float) -> float:
    """Effective capacitance at bias, tolerance and temperature at the low end."""
    return nominal * retention * LOW


def c_high(nominal: float) -> float:
    """Highest capacitance at 0 V bias (no loss), tolerance and temperature at the high end."""
    return nominal * HIGH


def break_even(nominal: float, required: float) -> float:
    """Retention at which c_low equals the required value."""
    return required / (nominal * LOW)


def hw015_low(retention: float = RETENTION["C2"]) -> float:
    """VBUS_IC at 5.25 V, only the capacitors on the net itself (C2)."""
    return c_low(CAPS["C2"][1], retention)


def hw015_high() -> float:
    """VBUS_IC at 0 V: C2 plus the three 100 nF behind resistors, without protection parts."""
    return c_high(CAPS["C2"][1]) + N_VBUS_BEHIND_R * c_high(C_100N)


def hw014_ldo_input(retention: float = RETENTION["C5"]) -> float:
    """TLV757P input capacitor C5 only (C3 and the 100 nF are not counted)."""
    return c_low(CAPS["C5"][1], retention)


def hw014_sum_at_0v() -> float:
    """All populated +5V capacitors at 0 V bias, spares not included."""
    return c_high(CAPS["C3"][1]) + c_high(CAPS["C5"][1]) + N_LED_CAPS * c_high(C_100N)


def spare_headroom() -> float:
    return HW014_MAX - hw014_sum_at_0v()


def c_100n_low_5v() -> float:
    """One 100 nF X7R capacitor at 5.5 V, bias, tolerance and temperature at the low end (X7R spread 15 %)."""
    return c_low(C_100N, RETENTION_100N)


def spare_nominal_max_at_0v() -> float:
    """Largest total nominal value of the spares C4 and C32 that keeps the populated sum within HW014_MAX,
    counting the spares at 0 V bias with the high factor (no bias loss)."""
    return spare_headroom() / HIGH


def start_up_bound() -> float:
    """HW-014 upper bound from bulk_cap_bounds with C6 at its high value (module not counted)."""
    return bcb.c_max(c_3v3=c_high(CAPS["C6"][1]))


def main() -> None:
    u = 1e6
    print(f"retention {RETENTION}; low factor {LOW:.3f}; high factor {HIGH:.3f}")
    print(f"HW-015 C2 at 5.25 V: {hw015_low()*u:.2f} uF (need >= {USB_MIN*u:.1f}); "
          f"break-even retention {break_even(CAPS['C2'][1], USB_MIN):.2f}")
    print(f"HW-015 VBUS_IC at 0 V: {hw015_high()*u:.2f} uF (need <= {USB_MAX*u:.1f}, protection parts not counted); "
          f"room {(USB_MAX - hw015_high())*u:.2f} uF")
    print(f"HW-014 C5 effective at 5.5 V: {hw014_ldo_input()*u:.2f} uF (need > {LDO_EFFECTIVE_MIN*u:.2f}); "
          f"break-even retention {break_even(CAPS['C5'][1], LDO_EFFECTIVE_MIN):.2f}")
    print(f"HW-014 populated sum at 0 V: {hw014_sum_at_0v()*u:.1f} uF; room for spares {spare_headroom()*u:.1f} uF")
    print(f"HW-014 start-up bound with C6 high: {start_up_bound()*u:.1f} uF (module capacitance not counted)")
    print(f"100 nF X7R at 5.5 V: {c_100n_low_5v()*u*1000:.1f} nF low case (retention {RETENTION_100N}); "
          f"spares C4 + C32 together at most {spare_nominal_max_at_0v()*u:.0f} uF nominal")
    print(f"C3 effective at 5.5 V (not a requirement): {c_low(CAPS['C3'][1], RETENTION['C3'])*u:.2f} uF; "
          f"C6 effective at 3.3 V: {c_low(CAPS['C6'][1], RETENTION['C6'])*u:.2f} uF")


if __name__ == "__main__":
    main()
