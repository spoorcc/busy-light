# SPDX-License-Identifier: Apache-2.0
"""Spike: ADR-0016 gate fragment (CC detection IC output ANDed with firmware select lines).

Generic parts only: no part number is fixed (ADR-0016 item 3). Placeholder reference
designators. Output: gate.net and gate.kicad_sch in the output directory.
Traces to HW-010 (Approved 2026-11-04), HW-003 (Approved 2026-11-04), ADR-0016.
Version 3 (+ exclusive steps via U13): IC supplied from VBUS, supervisor-type hold-off (restarts after a VBUS dip), 3-input AND.
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

# Pull-up so an unpowered or open IC output reads "not advertised". It goes to the IC supply (VBUS_IC),
# not to 3V3: the TUSB321 output pins are rated VDD + 0.3 V at most, so a 3.3 V pull-up that outlives VBUS
# is outside the rating (datasheet-evidence-supervisor.md). The 3.3 V inverter then sees up to 5 V.
r_pu = Part("Device", "R", ref="R1", value="100k", footprint="Resistor_SMD:R_0603_1608Metric")
r_pu[1] += VBUS
r_pu[2] += out1_n

# Active-low output to active-high "ok" (inverter).
inv = Part("74xGxx", "74LVC1G04", ref="U2", footprint="Package_TO_SOT_SMD:SOT-23-5")
ok = Net("CC_OK_1A5")
inv[5] += V3
inv[3] += GND
inv[2] += out1_n
inv[4] += ok

# Start-up hold-off (HW-010): a voltage supervisor with a programmable reset delay (placeholder part,
# part not chosen; delay accuracy comes from its datasheet). RESET is held while VBUS is below the
# threshold and for the delay after VBUS recovers, so a VBUS dip restarts the hold-off (an RC with a
# diode does not: review finding H2). The open-drain output is pulled up to VBUS_IC, not 3V3, so an
# unpowered supervisor reads "hold-off not done" (low).
hold_ok, ct = Net("HOLD_OK"), Net("SUP_CT")
# Pin order of the TPS3840 DBV package (SNVSB03E, p. 4): 1 RESET, 2 VDD, 3 GND, 4 MR/NC, 5 CT.
# MR (pin 4) is left open here; whether it needs a tie-off is NOT read yet (open item).
sup = Part("Connector_Generic", "Conn_01x05", ref="U5", value="TPS3840DL40 (candidate)",
           footprint="Package_TO_SOT_SMD:SOT-23-5")
sup[1] += hold_ok      # open-drain RESET, high = hold-off done
sup[2] += VBUS         # VDD / sense
sup[3] += GND
sup[4] += Net("SUP_MR_NC")
sup[5] += ct           # delay capacitor
# Hold-off capacitor set (owner decision 2026-11-06, HW-010 revision approved 2026-11-07): six 100 nF C0G 5 % 1206
# in parallel (600 nF, window 203.2 to 553.2 ms, sim/holdoff_cap.py, hw/sim/scripts/amendment2_numbers.py).
for _ref, _val in (("C1", "100n C0G 5% 50V"), ("C1B", "100n C0G 5% 50V"), ("C1C", "100n C0G 5% 50V"),
                   ("C1D", "100n C0G 5% 50V"), ("C1E", "100n C0G 5% 50V"), ("C1F", "100n C0G 5% 50V")):
    _c = Part("Device", "C", ref=_ref, value=_val, footprint="Capacitor_SMD:C_1206_3216Metric")
    _c[1] += ct
    _c[2] += GND
r_hp = Part("Device", "R", ref="R6", value="150k", footprint="Resistor_SMD:R_0603_1608Metric")
r_hp[1] += VBUS
r_hp[2] += hold_ok

# One 3-input AND per gated step (select line AND ok AND hold-off done). Single-gate parts, because
# the SKiDL schematic writer dropped a pin of the second unit of a dual part (spike finding F3).
# Pin numbers are those of the KiCad symbol 74LVC1G11 (A=1, B=3, C=6, Y=4); check against the datasheet.
sel2, sel3 = Net("SEL_STEP2_GPIO"), Net("SEL_STEP3_GPIO")
en2, en3 = Net("ILIM_STEP2_EN"), Net("ILIM_STEP3_EN")
# Exclusive steps (owner decision 2026-11-05): step 2 uses ok2 = NOR(CC_OUT1_N, ILIM_STEP3_EN) = CC OK AND
# NOT step 3 enable instead of ok, so step 3 on forces step 2 off. U13 is a 74LVC1G02 (A=1, B=2, GND=3, Y=4, VCC=5).
ok2 = Net("CC_OK_NOT_S3")
nor = Part("74xGxx", "74LVC1G02", ref="U13", footprint="Package_TO_SOT_SMD:SOT-23-5")
nor[5] += V3
nor[3] += GND
nor[1] += out1_n
nor[2] += en3
nor[4] += ok2
for ref, sel, en, okn in (("U3", sel2, en2, ok2), ("U4", sel3, en3, ok)):
    g = Part("74xGxx", "74LVC1G11", ref=ref, footprint="Package_TO_SOT_SMD:SOT-23-6")
    g[5] += V3
    g[2] += GND
    g[1] += okn
    g[3] += sel
    g[6] += hold_ok
    g[4] += en

# Pull-downs: an open or unpowered gate output or input resolves to the lowest step.
for ref, net in (("R2", en2), ("R3", en3), ("R4", sel2), ("R5", sel3)):
    r = Part("Device", "R", ref=ref, value="100k", footprint="Resistor_SMD:R_0603_1608Metric")
    r[1] += net
    r[2] += GND

# Limit-resistor switches (ILIM network of ADR-0010 option A). Owner decision 2026-11-05 (a): TMUX1101DCKR
# (LCSC C2673506, SC70-5) instead of the 2N7002. Pins (SCDS410D tab. 5-1, DCK): 1 D, 2 S, 3 GND, 4 SEL, 5 VDD;
# SEL high = switch on. The gate output drives SEL; a 100 kohm pull-down on SEL makes an open gate output mean "off".
# Decision (b): R_ILIM 0.1 % 0603: step 1 47.0 k (full board only), step 2 56.2 k, step 3 27.4 k + 301 ohm in series.
ilim = Net("ILIM")  # one net for both switched resistors (review finding: it was created twice)
for sw, en, rl, rl_val, cap, rpd in (("U14", en2, "R_ILIM2", "56.2k 0.1%", "C24", "R18"),
                                     ("U15", en3, "R_ILIM3", "27.4k 0.1%", "C25", "R19")):
    q = Part("Connector_Generic", "Conn_01x05", ref=sw, value="TMUX1101DCKR",
             footprint="Package_TO_SOT_SMD:SOT-353_SC-70-5")
    r = Part("Device", "R", ref=rl, value=rl_val, footprint="Resistor_SMD:R_0603_1608Metric")
    q[4] += en         # SEL
    q[2] += GND        # S: the low side of the switched resistor
    q[3] += GND
    q[5] += VBUS       # VDD from VBUS_IC (owner decision 2026-11-07, HW-010 revision; analysis-tmux1101-supply-from-vbus.md)
    if sw == "U15":    # series pair: switch - 301 ohm - 27.4 k - ILIM
        rb = Part("Device", "R", ref="R_ILIM3B", value="301 0.1%", footprint="Resistor_SMD:R_0603_1608Metric")
        q[1] += rb[1]
        rb[2] += r[1]
    else:
        q[1] += r[1]
    r[2] += ilim
    c = Part("Device", "C", ref=cap, value="100n", footprint="Capacitor_SMD:C_0603_1608Metric")
    c[1] += VBUS       # 100 nF at the switch supply pin
    c[2] += GND
    rd = Part("Device", "R", ref=rpd, value="100k", footprint="Resistor_SMD:R_0603_1608Metric")
    rd[1] += en
    rd[2] += GND

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    os.chdir(out)
    ERC()
    generate_netlist(file_="gate.net")
    if "--netlist-only" in sys.argv:  # the own writer (write_sch.py) makes the schematic (ADR-0012)
        print("netlist written")
        sys.exit(0)
    for attempt in range(5):  # the router is not deterministic (spike finding F4)
        try:
            generate_schematic(filepath=".", top_name="gate", flatness=0.0, retries=6)
            break
        except Exception as exc:  # noqa: BLE001
            print("schematic attempt", attempt, "failed:", type(exc).__name__)
    else:
        sys.exit("no schematic after 5 attempts")
    print("netlist written")
