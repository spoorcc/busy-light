#!/usr/bin/env python3
"""Worst-case error of the TPS2553 current limit from off-state leakage of the ILIM select MOSFETs.

Model (HW-010, ADR-0010 E4, ADR-0016): the limit is set by the total resistance from ILIM to GND.
The TPS2553 holds a regulated voltage V_ILIM on the pin and the limit is proportional to the current
sourced out of ILIM. A select MOSFET that is off adds a leakage current I_L from the ILIM node to
GND in parallel with the resistor network. With n off switches:

    I_pin = V_ILIM / R_total + n * I_L
    relative increase of the sourced current = n * I_L * R_total / V_ILIM

The limit rises by about the same fraction (IOS is proportional to 1 / R^~1, ADR-0010 E3).

Assumptions (stated, not verified):
  A1. The datasheet IDSS maximum is measured at a high VDS (30 V or 50 V). Leakage at the low VDS
      on the ILIM pin is assumed to be at or below that value. This is an upper bound, not a
      prediction.
  A2. V_ILIM is NOT stated numerically in the TPS2553 datasheet (SLVS841G, text: "a regulated
      voltage on the ILIM pin"). The result is therefore given for a range of V_ILIM.
  A3. The ILIM resistors are R1 = 47.0 kohm, R2 = 56.9 kohm, R3 = 27.7 kohm (owner-confirmed
      proposal of 2026-11-05, not Approved). Steps are exclusive: step 2 = R1||R2 with Q2 on,
      step 3 = R1||R3 with Q3 on and Q2 off.
"""

from __future__ import annotations

R1 = 47_000.0
R2 = 56_900.0
R3 = 27_700.0

# (label, IDSS max in A, condition, datasheet)
PARTS = (
    ("BSS138 (onsemi)", 100e-9, "VDS = 30 V, 25 C", "onsemi BSS138-D"),
    ("BSS138 (onsemi), 50 V row", 0.5e-6, "VDS = 50 V, 25 C", "onsemi BSS138-D"),
    ("AO3400A (AOS)", 1e-6, "VDS = 30 V, 25 C", "AOS AO3400A Rev 3.1"),
)

V_ILIM_RANGE = (0.5, 1.0, 2.0)  # volts, assumed (A2)


def parallel(*rs: float) -> float:
    """Return the parallel resistance of the given resistors."""
    return 1.0 / sum(1.0 / r for r in rs)


def steps() -> dict[str, tuple[float, int]]:
    """Return {step: (R_total in ohm, number of switches that are off)}."""
    return {
        "step 1 (Q2, Q3 off)": (R1, 2),
        "step 2 (Q2 on, Q3 off)": (parallel(R1, R2), 1),
        "step 3 (Q3 on, Q2 off)": (parallel(R1, R3), 1),
    }


def relative_error(r_total: float, n_off: int, i_leak: float, v_ilim: float) -> float:
    """Return the relative increase of the ILIM current for n_off leaking switches."""
    return n_off * i_leak * r_total / v_ilim


def max_leak_for_error(r_total: float, n_off: int, v_ilim: float, error: float) -> float:
    """Return the largest per-switch leakage that keeps the error at or below `error`."""
    return error * v_ilim / (n_off * r_total)


def main() -> None:
    print("Resistor tolerance reference: 0.1 % (HW-010 proposal 1)")
    print()
    print("Largest per-switch leakage for an error of 0.1 % (nA):")
    for name, (r, n) in steps().items():
        cells = ", ".join(
            f"V_ILIM {v:g} V: {max_leak_for_error(r, n, v, 0.001) * 1e9:.1f}" for v in V_ILIM_RANGE
        )
        print(f"  {name}, R = {r / 1e3:.2f} kohm: {cells}")
    print()
    print("Error if the leakage equals the datasheet IDSS maximum (percent, upper bound, A1):")
    for label, idss, cond, _ in PARTS:
        print(f"  {label} ({cond}), IDSS max {idss * 1e9:.0f} nA")
        for name, (r, n) in steps().items():
            cells = ", ".join(
                f"{v:g} V: {relative_error(r, n, idss, v) * 100:.2f} %" for v in V_ILIM_RANGE
            )
            print(f"    {name}: {cells}")


if __name__ == "__main__":
    main()
