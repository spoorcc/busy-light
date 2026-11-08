#!/usr/bin/env python3
"""Bounds for the capacitance of the +5V rail (HW-014 draft, analysis-5v-bulk-capacitance.md).

Lower bound: the part makers' minimum at the loads (owner decision 2026-11-08 after RV-013). The
derived lower bound of the first draft (load step against the cable inductance) was withdrawn:
RV-013 found it unsound (no cable resistance, LED PWM edges, CC IC minimum of 4.5 V). The prototype
measurement decides more capacitance (HW-016).

Upper bound (start-up): at plug-in the TPS2553 charges the rail. In the worst case the whole charge
flows at the lowest current limit of step 1. The time in current limit must stay well below the
shortest overcurrent FAULT deglitch, or FAULT_N reports a false fault at every plug-in. C_max =
(t_allow * (I_OS,min - I_start) - Q_3V3) / V_max. The 3V3 capacitors are charged through the
regulator in the same window (Q_3V3).

Read values (local datasheets, 2026-11-08):
  TPS2553 SLVS841G: IOS,min = 25230 / R^1.016 mA (R in kohm, eq. 3); overcurrent FAULT deglitch 3 /
    7.5 / 11 ms.
  TLV757P SBVS322C: input capacitor 1 uF or larger; nominal capacitance after derating above 0.47
    uF.
  HW-010 (Approved): R_ILIM1 = 47.0 kohm 0.1 % (step 1, the lowest limit). ASSUMED (to be replaced
    by bench data): the start-up load, the 3V3 capacitance, the deglitch margin and 5.5 V as the
    highest charge voltage (Type-C vSafe5V maximum, not read in this analysis)."""

from __future__ import annotations

# read
IOS_MIN_K, IOS_MIN_EXP = 25230.0, 1.016  # mA, kohm (TPS2553 eq. 3)
T_DEGLITCH_MIN = 3e-3  # s, overcurrent FAULT deglitch, minimum
R_ILIM1 = 47.0  # kohm, HW-010 step 1
R_TOL = 0.001  # 0.1 %
C_MIN_LDO_NOMINAL = 1e-6  # F, TLV757P input, nominal
C_MIN_LDO_EFFECTIVE = 0.47e-6  # F, TLV757P input, after derating (must be above)

# assumed
I_START = 0.10  # A: load during the charge (processor in reset, LEDs dark)
C_3V3 = 10e-6  # F: 3V3 rail (C6 plus module), charged through the regulator
V_3V3 = 3.3
V_MAX = 5.5  # V: highest charge voltage
DEGLITCH_MARGIN = 0.5  # use half of the shortest deglitch

# sensitivity corners (RV-013 finding 8)
I_START_CASES = (0.05, 0.10, 0.20, 0.30)
C_3V3_CASES = (10e-6, 22e-6, 47e-6)


def ios_min(r_kohm: float) -> float:
    """Lowest TPS2553 current limit in A for R_ILIM in kohm (no resistor tolerance)."""
    return IOS_MIN_K / r_kohm**IOS_MIN_EXP / 1000.0


def i_limit_step1() -> float:
    return ios_min(R_ILIM1 * (1.0 + R_TOL))


def c_max(i_start: float = I_START, c_3v3: float = C_3V3, v_max: float = V_MAX) -> float:
    """Largest +5V capacitance (F) that charges within the allowed time; raises if none fits."""
    i_lim = i_limit_step1()
    if i_start >= i_lim:
        raise ValueError("start load at or above the current limit")
    q = T_DEGLITCH_MIN * DEGLITCH_MARGIN * (i_lim - i_start) - c_3v3 * V_3V3
    if q <= 0:
        raise ValueError("the 3V3 charge alone uses the time budget")
    return q / v_max


def time_in_limit(
    c_f: float, i_start: float = I_START, c_3v3: float = C_3V3, v_max: float = V_MAX
) -> float:
    """Worst-case time the switch spends in current limit while it charges the rails."""
    return (c_f * v_max + c_3v3 * V_3V3) / (i_limit_step1() - i_start)


def ldo_input_ok(c_nominal: float, c_effective: float) -> bool:
    """TLV757P input: 1 uF nominal or larger and more than 0.47 uF after derating."""
    return c_nominal >= C_MIN_LDO_NOMINAL and c_effective > C_MIN_LDO_EFFECTIVE


def sensitivity() -> list[str]:
    rows = [
        "| I_start (A) | " + " | ".join(f"C_3V3 {c * 1e6:.0f} uF" for c in C_3V3_CASES) + " |",
        "|---|" + "---|" * len(C_3V3_CASES),
    ]
    for i in I_START_CASES:
        cells = []
        for c in C_3V3_CASES:
            try:
                cells.append(f"{c_max(i, c) * 1e6:.0f} uF")
            except ValueError:
                cells.append("none")
        rows.append(f"| {i:.2f} | " + " | ".join(cells) + " |")
    return rows


def report() -> list[str]:
    out = [
        f"IOS,min step 1 (R_ILIM1 47.0 kohm +0.1 %): {i_limit_step1() * 1000:.0f} mA",
        f"Lower bound: TLV757P input {C_MIN_LDO_NOMINAL * 1e6:.0f} uF nominal, more than "
        f"{C_MIN_LDO_EFFECTIVE * 1e6:.2f} uF effective",
        f"C_max (charge in {T_DEGLITCH_MIN * DEGLITCH_MARGIN * 1e3:.1f} ms, I_start {I_START} A, "
        f"C_3V3 {C_3V3 * 1e6:.0f} uF): {c_max() * 1e6:.0f} uF",
        f"Time in limit at 100 uF: {time_in_limit(100e-6) * 1e3:.2f} ms "
        f"(shortest deglitch {T_DEGLITCH_MIN * 1e3:.0f} ms)",
        "Sensitivity of C_max:",
    ]
    return out + sensitivity()


if __name__ == "__main__":
    print("\n".join(report()))
