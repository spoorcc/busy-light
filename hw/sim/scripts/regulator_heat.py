#!/usr/bin/env python3
"""Heat of the 3V3 linear regulator (TLV75733P) for realistic Wi-Fi use (HW-010 proposal, HW-013).

Loss in a linear regulator: P = (V_in - V_out) * I_out + V_in * I_gnd. The Wi-Fi duty cycles are
ASSUMPTIONS (the datasheets give only 100 % duty, `spike-7-5-power-budget-paper.md` E14 not found).
Module currents (read, same report): modem-sleep with CPU 28 mA (E6), RX 82 mA (E4), TX 350 mA (E1).
Other 3V3 loads (buffer, sensor): 5 mA assumed. TLV757P (SBVS322C, read 2026-11-07):
I_gnd 25 uA typ, R_thJA for DBV 100.8 (EVM board) and 231.1 (JEDEC board), DYD 60.3 and 92.5 degC/W,
T_J max 125 degC. Air temperature at the regulator = ambient + housing rise (unknown, parameter).
"""

from __future__ import annotations

I_SLEEP = 0.028  # A, E6
I_RX = 0.082  # A, E4
I_TX = 0.350  # A, E1
I_OTHER = 0.005  # A, assumed
I_GND = 25e-6  # A, TLV757P typ
V_OUT = 3.3
TJ_MAX = 125.0
TJ_MARGIN = 15.0

# (name, TX duty, RX duty): assumptions
SCENARIOS = (
    ("connected, push model", 0.01, 0.05),
    ("polling every few s", 0.05, 0.20),
    ("firmware download (minutes)", 0.30, 0.50),
    ("bound: TX 100 % (not a real use)", 1.00, 0.00),
)
RTH = (("DBV EVM", 100.8), ("DBV JEDEC", 231.1), ("DYD EVM", 60.3), ("DYD JEDEC", 92.5))
CASE_RISE = (0.0, 20.0, 40.0)  # K, housing air rise over ambient (unknown; HW-013 measures it)
T_AMB = 35.0
V_IN = 5.5  # worst case: the highest rail


def avg_current(tx: float, rx: float) -> float:
    rest = 1.0 - tx - rx
    return I_SLEEP * rest + I_RX * rx + I_TX * tx + I_OTHER


def power(i_out: float, v_in: float = V_IN) -> float:
    return (v_in - V_OUT) * i_out + v_in * I_GND


def tj(p_w: float, rth: float, case_rise: float) -> float:
    return T_AMB + case_rise + rth * p_w


def max_avg_current(rth: float, case_rise: float, v_in: float = V_IN) -> float:
    """Highest average 3V3 current that keeps Tj at or below the limit minus the margin."""
    p_max = (TJ_MAX - TJ_MARGIN - T_AMB - case_rise) / rth
    return (p_max - v_in * I_GND) / (v_in - V_OUT)


def table() -> list[str]:
    rows = [
        "| Scenario | I avg (mA) | P (mW) | Package / board | Tj at +0 K | +20 K | +40 K |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, tx, rx in SCENARIOS:
        i = avg_current(tx, rx)
        p = power(i)
        for label, rth in RTH:
            cells = []
            for cr in CASE_RISE:
                t = tj(p, rth, cr)
                cells.append(f"{t:.0f}" + ("" if t <= TJ_MAX - TJ_MARGIN else " **over**"))
            rows.append(
                f"| {name} | {i * 1e3:.0f} | {p * 1e3:.0f} | {label} | " + " | ".join(cells) + " |"
            )
    return rows


if __name__ == "__main__":
    print("\n".join(table()))
    for label, rth in RTH:
        for cr in CASE_RISE:
            i_max = max_avg_current(rth, cr) * 1e3
            print(f"max average 3V3 current, {label}, +{cr:.0f} K: {i_max:.0f} mA")
