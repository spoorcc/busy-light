#!/usr/bin/env python3
"""Surge at the supply pin of a 6 V-limited part on VBUS_IC (HW-010 proposed amendment, ADR-0016).

Circuit per protected pin: VBUS_IC -- R_series -- pin; C_pin (100 nF nominal) and a 5.1 V zener
  from pin to GND;
the part draws I_load from the pin. VBUS_IC is driven by the TVS1-clamped surge, modelled as a
  voltage source
with 0.1 ohm (the TVS clamps and the cable hides the source).

Datasheet facts (read 2026-11-07, TI documents):
  TMUX1101 SCDS410D: VDD abs max 6 V, recommended 1.08 to 5.5 V, IDD 0.003 uA typ, 1 uA max.
  TUSB321 SLLSEO6C table 6.1/6.3/6.5: VDD abs max 6 V, recommended 4.5 to 5.5 V, I_active 100 uA
    max.
Assumptions (NOT from a datasheet; the zener datasheet is not read):
  Z1. Zener 5.1 V, SOD-123 class (BZT52C5V1 type): Vz 4.85 to 5.35 V (+-5 %) at 5 mA, dynamic
    resistance 60 ohm.
  Z2. Surge shapes: S1 8/20 us peak 15 V (highest TVS clamp figure in search snippets,
    `shortlist-tvs1-3v3-regulator.md`);
      S2 hot-plug ring 10 V peak, 1 us decay; S3 sustained 9 V (a PD source after a fault; TVS1
        is assumed to have
      failed open or to be rated above this).
  Z3. C_pin: 100 nF nominal, 50 nF worst case (tolerance and DC bias of an X7R capacitor,
    unverified).
Pass: peak pin voltage at most 5.7 V (0.3 V margin to the 6 V absolute maximum) in S1 and S2, S3
  power at most
half of the part rating (R 0603 100 mW, zener 300 mW class).
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

V_ABS_MAX = 6.0
MARGIN = 0.3
LOADS = {"TMUX1101": 1e-6, "TUSB321": 100e-6}
SURGES = {
    "S1 8/20us 15V": "PWL(0 0 8u 15 20u 7.5 60u 0 200u 0)",
    "S2 ring 10V 1us": "PWL(0 0 50n 10 1u 5.5 3u 5 10u 5 11u 0 200u 0)",
}
ZENER_MODEL = ".model DZ D(IS=1e-14 N=1 RS=60 BV=5.1 IBV=5m CJO=100p)"


def run_case(r_ohm: float, c_f: float, i_load: float, source: str, t_end: str = "300u") -> float:
    """Return the peak pin voltage in volts from one ngspice batch run."""
    net = f"""* surge at supply pin
VS src 0 {source}
RS src vb 0.1
RSER vb pin {r_ohm}
CP pin 0 {c_f}
DZ 0 pin DZ
IL pin 0 {i_load}
{ZENER_MODEL}
.tran 20n {t_end}
.meas tran vmax MAX v(pin)
.end
"""
    with tempfile.TemporaryDirectory() as d:
        cir = Path(d) / "c.cir"
        cir.write_text(net)
        out = subprocess.run(
            ["ngspice", "-b", str(cir)], capture_output=True, text=True, timeout=60, check=False
        )
    m = re.search(r"vmax\s*=\s*([0-9.eE+-]+)", out.stdout + out.stderr)
    if not m:
        tail = out.stdout[-400:] + out.stderr[-400:]
        raise RuntimeError("no vmax in ngspice output: " + tail)
    return float(m.group(1))


def dc_s3(r_ohm: float, v_in: float = 9.0, vz: float = 5.35) -> tuple[float, float, float]:
    """Sustained overvoltage: current, resistor power, zener power (top Vz, rdyn ignored)."""
    i = (v_in - vz) / r_ohm
    return i, i * i * r_ohm, i * vz


def dc_drop(r_ohm: float, i_load: float) -> float:
    return r_ohm * i_load


def table(rs=(100.0, 220.0, 470.0, 1000.0)) -> list[str]:
    rows = [
        "| R (ohm) | part | C | S1 peak (V) | S2 peak (V) | DC drop at max load (mV) "
        "| S3 R power (mW) | S3 zener power (mW) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rs:
        _, p_r, p_z = dc_s3(r)
        for part, il in LOADS.items():
            for c in (100e-9, 50e-9):
                s1 = run_case(r, c, il, SURGES["S1 8/20us 15V"])
                s2 = run_case(r, c, il, SURGES["S2 ring 10V 1us"])
                drop = dc_drop(r, il) * 1e3
                rows.append(
                    f"| {r:.0f} | {part} | {c * 1e9:.0f} nF | {s1:.2f} | {s2:.2f} | {drop:.1f} "
                    f"| {p_r * 1e3:.0f} | {p_z * 1e3:.0f} |"
                )
    return rows


if __name__ == "__main__":
    print("\n".join(table()))
