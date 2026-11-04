# SPDX-License-Identifier: Apache-2.0
"""Spike: ADR-0016 gate fragment (CC detection IC output ANDed with firmware select lines).

Generic parts only: no part number is fixed (ADR-0016 item 3). Placeholder reference
designators. Output: gate.net and gate.kicad_sch in the output directory.
Traces to HW-010 (Approved 2026-11-04), HW-003 (Approved 2026-11-04), ADR-0016.
Version 2: IC supplied from VBUS, start-up hold-off timer, 3-input AND (spike finding F8, F9).
"""
import os
import sys

os.environ.setdefault("KICAD9_SYMBOL_DIR", "/usr/share/kicad/symbols")
os.environ.setdefault("KICAD_SYMBOL_DIR", "/usr/share/kicad/symbols")
os.environ.setdefault("KICAD10_SYMBOL_DIR", "/usr/share/kicad/symbols")
from skidl import (Net, Part, Pin, SKIDL, TEMPLATE, generate_netlist,  # noqa: E402
                   generate_schematic, set_default_tool, KICAD9, ERC)

set_default_tool(KICAD9)

V3 = Net("+3V3")
GND = Net("GND")
VBUS = Net("VBUS_IC")   # 5 V from the USB connector: supply of the CC IC (TUSB321: VDD 4.5 to 5.5 V)
V3.drive = GND.drive = VBUS.drive = 1  # power nets

# Power flags: the rails come from the rest of the board (not in this fragment).
for _n in (V3, VBUS, GND):
    Part("power", "PWR_FLAG", ref="#FLG", footprint="Virtual:PWR_FLAG")[1] += _n

# CC detection IC placeholder: open-drain outputs, low = at least 1.5 A advertised (ADR-0016, E14).
ccic = Part("Connector_Generic", "Conn_01x05", ref="U1", value="CC_DETECT_IC_PLACEHOLDER",
            footprint="Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical")
ccic[1] += VBUS        # VDD (from VBUS, not 3.3 V)
ccic[2] += GND         # GND
out1_n = Net("CC_OUT1_N")   # low: >= 1.5 A
ccic[3] += out1_n
ccic[4] += Net("CC_OUT2_N")  # low: 3 A (not used by the gate)
ccic[5] += Net("CC_RESERVED")

# Pull-up so an unpowered or open IC output reads "not advertised".
r_pu = Part("Device", "R", ref="R1", value="100k", footprint="Resistor_SMD:R_0603_1608Metric")
r_pu[1] += V3
r_pu[2] += out1_n

# Active-low output to active-high "ok" (inverter).
inv = Part("74xGxx", "74LVC1G04", ref="U2", footprint="Package_TO_SOT_SMD:SOT-23-5")
ok = Net("CC_OK_1A5")
inv[5] += V3
inv[3] += GND
inv[2] += out1_n
inv[4] += ok

# Start-up hold-off (HW-010): RC from the IC supply into a Schmitt buffer, so the gate stays
# closed while the CC IC debounces. The diode empties C when VBUS goes away (new plug-in = new hold-off).
hold_rc, hold_ok = Net("HOLD_RC"), Net("HOLD_OK")
r_h = Part("Device", "R", ref="R6", value="1M 1%", footprint="Resistor_SMD:R_0603_1608Metric")
c_h = Part("Device", "C", ref="C1", value="510n X7R 10%", footprint="Capacitor_SMD:C_0603_1608Metric")
d_h = Part("Device", "D", ref="D1", value="Schottky small signal",
           footprint="Diode_SMD:D_SOD-323")
sch = Part("74xGxx", "74LVC1G17", ref="U5", footprint="Package_TO_SOT_SMD:SOT-23-5")
r_h[1] += VBUS
r_h[2] += hold_rc
c_h[1] += hold_rc
c_h[2] += GND
d_h["A"] += hold_rc
d_h["K"] += VBUS
sch[5] += VBUS
sch[3] += GND
sch[2] += hold_rc
sch[4] += hold_ok

# One 3-input AND per gated step (select line AND ok AND hold-off done). Single-gate parts, because
# the SKiDL schematic writer dropped a pin of the second unit of a dual part (spike finding F3).
# Pin numbers are those of the KiCad symbol 74LVC1G11 (A=1, B=3, C=6, Y=4); check against the datasheet.
sel2, sel3 = Net("SEL_STEP2_GPIO"), Net("SEL_STEP3_GPIO")
en2, en3 = Net("ILIM_STEP2_EN"), Net("ILIM_STEP3_EN")
for ref, sel, en in (("U3", sel2, en2), ("U4", sel3, en3)):
    g = Part("74xGxx", "74LVC1G11", ref=ref, footprint="Package_TO_SOT_SMD:SOT-23-5")
    g[5] += V3
    g[2] += GND
    g[1] += ok
    g[3] += sel
    g[6] += hold_ok
    g[4] += en

# Pull-downs: an open or unpowered gate output or input resolves to the lowest step.
for ref, net in (("R2", en2), ("R3", en3), ("R4", sel2), ("R5", sel3)):
    r = Part("Device", "R", ref=ref, value="100k", footprint="Resistor_SMD:R_0603_1608Metric")
    r[1] += net
    r[2] += GND

# Limit-resistor switches (ILIM network of ADR-0010 option A; values are placeholders).
for tag, en in (("2", en2), ("3", en3)):
    q = Part("Transistor_FET", "2N7002", ref=f"Q{tag}", footprint="Package_TO_SOT_SMD:SOT-23")
    rl = Part("Device", "R", ref=f"R_ILIM{tag}", value="PLACEHOLDER",
              footprint="Resistor_SMD:R_0603_1608Metric")
    ilim = Net("ILIM")
    q["G"] += en
    q["S"] += GND
    q["D"] += rl[1]
    rl[2] += ilim

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    os.chdir(out)
    ERC()
    generate_netlist(file_="gate.net")
    for attempt in range(5):  # the router is not deterministic (spike finding F4)
        try:
            generate_schematic(filepath=".", top_name="gate", flatness=0.0, retries=6)
            break
        except Exception as exc:  # noqa: BLE001
            print("schematic attempt", attempt, "failed:", type(exc).__name__)
    else:
        sys.exit("no schematic after 5 attempts")
    print("netlist written")
