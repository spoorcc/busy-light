# SPDX-License-Identifier: Apache-2.0
"""Spike: ADR-0016 gate fragment (CC detection IC output ANDed with firmware select lines).

Generic parts only: no part number is fixed (ADR-0016 item 3). Placeholder reference
designators. Output: gate.net and gate.kicad_sch in the output directory.
Traces to HW-010 (Draft), HW-003 (Draft), ADR-0016.
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
V3.drive = GND.drive = 1  # power nets

# Power flags: the 3V3 and GND rails come from the rest of the board (not in this fragment).
for _n in (V3, GND):
    Part("power", "PWR_FLAG", ref="#FLG", footprint="Virtual:PWR_FLAG")[1] += _n

# CC detection IC placeholder: open-drain outputs, low = at least 1.5 A advertised (ADR-0016, E14).
ccic = Part("Connector_Generic", "Conn_01x05", ref="U1", value="CC_DETECT_IC_PLACEHOLDER",
            footprint="Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical")
ccic[1] += V3          # VDD
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

# One 2-input AND per gated step (select line AND ok). Single-gate parts, because the SKiDL
# schematic writer dropped a pin of the second unit of a dual part (spike finding F3).
sel2, sel3 = Net("SEL_STEP2_GPIO"), Net("SEL_STEP3_GPIO")
en2, en3 = Net("ILIM_STEP2_EN"), Net("ILIM_STEP3_EN")
for ref, sel, en in (("U3", sel2, en2), ("U4", sel3, en3)):
    g = Part("74xGxx", "74LVC1G08", ref=ref, footprint="Package_TO_SOT_SMD:SOT-23-5")
    g[5] += V3
    g[3] += GND
    g[1] += ok
    g[2] += sel
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
