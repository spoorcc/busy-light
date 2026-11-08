# SPDX-License-Identifier: Apache-2.0
"""Spike: hand-laid-out schematic of the whole board (ADR-0012 spike, exploratory, not a product design).

Sections: USB-C input, CC detection and the ADR-0016 gate, hold-off supervisor, current-limit switch
(TPS2553), 3.3 V regulator, ESP32-C3 module, button, buffers, test points, 16 LED chain.
Every connection that is drawn is also recorded as intent (bind); run_full.sh compares the intent
with the netlist that kicad-cli exports from the drawn sheet. Placeholders and facts not read from a
datasheet are labelled in the sheet and in docs/verification/reports/spike-full-board-schematic.md.

Usage: layout_full.py <output.kicad_sch> [<intent.json>]
"""
import json
import sys

from kiutils.items.common import Position, TitleBlock
from kiutils.items.schitems import SchematicSymbol, SymbolProjectInstance, SymbolProjectPath

import layout_sch as L
import lib_tables
import write_sch as w

GRID = 1.27


def g(v):
    """Snap to the 1.27 mm connection grid (KiCad's default), so ERC has no off-grid endpoints."""
    return round(round(v / GRID) * GRID, 4)


DX = 55.0   # the gate fragment of layout_sch.py is drawn shifted right by this much


def gx(x):
    return round(x + DX, 4)


BUSX_FULL = g(gx(L.BUSX))   # x of the ILIM bus (grid-snapped, as the parts are)


# ------------------------------------------------------------------ part table
R = ("Device", "R", "Resistor_SMD:R_0603_1608Metric")
C = ("Device", "C", "Capacitor_SMD:C_0603_1608Metric")
C1206 = ("Device", "C", "Capacitor_SMD:C_1206_3216Metric")
TVS = ("Device", "D_TVS", "Diode_SMD:D_SOD-323")
G04 = ("74xGxx", "74LVC1G04", "Package_TO_SOT_SMD:SOT-23-5")
G02 = ("74xGxx", "74LVC1G02", "Package_TO_SOT_SMD:SOT-23-5")
G11 = ("74xGxx", "74LVC1G11", "Package_TO_SOT_SMD:SOT-23-6")
G08 = ("74xGxx", "74LVC1G08", "Package_TO_SOT_SMD:SOT-23-5")
ZENER = ("Diode", "BZX84Cxx", "Package_TO_SOT_SMD:SOT-23")
AHCT125 = ("74xGxx", "74AHCT1G125", "Package_TO_SOT_SMD:SOT-23-5")
TP = ("Connector", "TestPoint", "TestPoint:TestPoint_Pad_D1.5mm")
# pin numbers of the KiCad symbol LED:WS2812B-2020 (the 5050 symbol has other numbers: 1 VDD, 2 DOUT, 3 VSS, 4 DIN)
LED_DOUT, LED_VSS, LED_DIN, LED_VDD = "1", "2", "3", "4"
LED = ("LED", "WS2812B-2020", "LED_SMD:LED_WS2812B-2020_PLCC4_2.0x2.0mm")   # 2020 package per ADR-0004; the part number is still open

PARTS = {  # ref: (lib, part, footprint, value)
    "J1": ("Connector", "USB_C_Receptacle_USB2.0_16P", "CUSTOM:USB_C_Receptacle_GCT_USB4085_edge", "USB-C receptacle"),
    "TVS1": (*TVS, "TVS"), "U6": ("Power_Protection", "USBLC6-2P6", "Package_TO_SOT_SMD:SOT-666", "USBLC6-2P6"),
    "U1": (None, None, "CUSTOM:X2QFN-12_RWB", "TUSB321"),   # generated footprint, no X2QFN footprint in the KiCad libraries
    "R_VD": (*R, "887k"), "R1": (*R, "100k"),
    "U2": (*G04, "74LVC1G04"),
    "U13": (*G02, "74LVC1G02"),
    "U3": (*G11, "74LVC1G11"), "U4": (*G11, "74LVC1G11"),
    "R4": (*R, "100k"), "R5": (*R, "100k"), "R2": (*R, "10k"), "R3": (*R, "10k"),
    "U14": (None, None, "Package_TO_SOT_SMD:SOT-353_SC-70-5", "TMUX1101DCKR"),
    "U15": (None, None, "Package_TO_SOT_SMD:SOT-353_SC-70-5", "TMUX1101DCKR"),
    "R18": (*R, "100k"), "R19": (*R, "100k"), "C24": (*C, "100n"), "C25": (*C, "100n"),
    # owner decision 2026-11-05 (b): 0.1 % 0603; step 3 is 27.4 k + 301 ohm in series (27.701 k)
    "R_ILIM2": (*R, "56.2k 0.1%"), "R_ILIM3": (*R, "27.4k 0.1%"), "R_ILIM3B": (*R, "301 0.1%"),
    "R_ILIM1": (*R, "47.0k 0.1%"),
    "U5": (None, None, "Package_TO_SOT_SMD:SOT-23-5", "TPS3840DL40"),
    "R6": (*R, "150k"), "C1": (*C1206, "100n C0G 5% 50V"), "C1B": (*C1206, "100n C0G 5% 50V"),
    "C1C": (*C1206, "100n C0G 5% 50V"), "C1D": (*C1206, "100n C0G 5% 50V"),
    "C1E": (*C1206, "100n C0G 5% 50V"), "C1F": (*C1206, "100n C0G 5% 50V"),   # six 100 nF, owner decision 2026-11-06
    "U7": (None, None, "Package_TO_SOT_SMD:SOT-23-6", "TPS2553"),
    "C2": (*C, "1u tbd"), "C3": (*C, "10u tbd"), "R8": (*R, "100k"),
    "U8": (None, None, "Package_TO_SOT_SMD:SOT-23-5", "TLV75733PDBV"),   # ADR-0019 option A
    "C5": (*C, "tbd"), "C6": (*C, "tbd"),
    "U9": (None, None, "CUSTOM:ESP32-C3-MINI-1", "ESP32-C3-MINI-1"),    # no such footprint in the KiCad libraries; pcb_full.derive_u9_footprint writes it
    "R9": (*R, "10k"), "C7": (*C, "1u"),
    "SW1": ("Switch", "SW_Push", "Button_Switch_SMD:SW_SPST_TL3342", "Button"),
    "R12": (*R, "1k"), "R13": (*R, "10k"), "TVS2": (*TVS, "ESD diode"),
    "U10": (*G08, "74LVC1G08"), "U11": (*AHCT125, "74AHCT1G125"),
    "R10": (*R, "330"), "R11": (*R, "10k"), "C4": (*C, "bulk tbd"),
    # supply-pin protection (HW-010 amendment, owner 2026-11-07): series resistor, 100 nF and 5.1 V zener per 6 V pin
    "R_SU1": (*R, "470"), "R_SU14": (*R, "1k"), "R_SU15": (*R, "1k"),
    "C26": (*C, "100n"),
    "DZ1": (*ZENER, "BZX84C5V1"), "DZ14": (*ZENER, "BZX84C5V1"), "DZ15": (*ZENER, "BZX84C5V1"),
}
for i in range(1, 17):
    PARTS[f"D{i}"] = (*LED, "WS2812B")
    PARTS[f"C{7 + i}"] = (*C, "100n")
for i, n in enumerate(("TP_5V", "TP_3V3", "TP_GND", "TP_LED", "TP_EN", "TP_BOOT"), 1):
    PARTS[f"TP{i}"] = (*TP, n)
PARTS["R16"] = (*R, "10k")
PARTS["R17"] = (*R, "10k")
PARTS["R14"] = (*R, "100k")
PARTS["R15"] = (*R, "100k")

S = L.SIZE
# Pad numbers of the pins that the layout code names (the box symbols carry these numbers, so the schematic and the
# board use the same pad numbers and the DRC schematic parity check covers U1 and U9). Sources, read 2026-11-08 from the
# local datasheet folder (not committed, ADR-0015 item 8):
#   U1 TUSB321 RWB package: TI SLLSEO6C (revised August 2018), section 5 Pin Functions.
#   U9 ESP32-C3-MINI-1: Espressif datasheet v2.2, table 3-1 (page 11); the nine centre pads are all pin 49 (figure 3-1).
U9_GND = ("1", "2", "11", "14") + tuple(str(n) for n in range(36, 54))
PAD = {
    "U1": {"CC1": "1", "CC2": "2", "PORT": "4", "VBUS_DET": "5", "GND": "10", "VDD": "12"},
    "U9": {"GPIO0": "12", "GPIO1": "13", "GPIO2": "5", "GPIO3": "6", "GPIO4": "18", "GPIO5": "19",
           "GPIO6": "20", "GPIO7": "21", "GPIO8": "22", "GPIO9": "23", "GPIO10": "16",
           "GPIO18": "26", "GPIO19": "27", "GPIO20": "30", "GPIO21": "31", "3V3": "3", "EN": "8", "GND": U9_GND},
}


def pads(ref, pin):
    """Pad numbers (tuple) of a pin given by name or number."""
    p = PAD.get(ref, {}).get(str(pin), str(pin))
    return p if isinstance(p, tuple) else (p,)


def _numbered(ref, pins):
    """Box pins with the datasheet pad number; a multi-pad pin (GND) becomes stacked pins, extra ones passive."""
    out = []
    for num, name, side, off, etype in pins:
        for k, p in enumerate(pads(ref, num)):
            out.append((p, name, side, off, etype if k == 0 else "passive"))
    return out


BOXES = {
    "U1": L.box_symbol("CC_IC_TUSB321", _numbered("U1", [
        ("VDD", "VDD", "top", -2.54, "power_in"), ("VBUS_DET", "VBUS_DET", "top", 2.54, "passive"),
        ("GND", "GND", "bottom", -2.54, "power_in"), ("PORT", "PORT", "bottom", 2.54, "passive"),
        ("CC1", "CC1", "left", 2.54, "passive"), ("CC2", "CC2", "left", 0, "passive"),
        ("7", "OUT1_N", "right", 5.08, "open_collector"), ("8", "OUT2_N", "right", 0, "open_collector"),
        ("3", "CURRENT_MODE", "right", -5.08, "passive"), ("6", "VCONN_FAULT", "right", -7.62, "open_collector"),
        ("9", "ID", "right", -10.16, "open_collector"), ("11", "DIR", "right", -12.7, "open_collector")]), half_h=15.24),
    "U5": L.SUPERVISOR,
    "U14": L.TMUX1101, "U15": L.TMUX1101,
    "U7": L.box_symbol("TPS2553_BOX", [
        ("1", "IN", "top", -2.54, "power_in"), ("3", "EN", "top", 2.54, "input"),
        ("2", "GND", "bottom", 0, "power_in"), ("5", "ILIM", "left", 5.08, "passive"),
        ("6", "OUT", "right", 2.54, "passive"), ("4", "FAULT", "right", -2.54, "open_collector")]),
    "U8": L.box_symbol("TLV75733P_DBV", [
        ("1", "IN", "left", 0, "power_in"), ("3", "EN", "left", -2.54, "input"),
        ("5", "OUT", "right", 0, "passive"), ("4", "NC", "right", -2.54, "no_connect"),
        ("2", "GND", "bottom", 0, "power_in")]),
    "U9": L.box_symbol("ESP32_C3_MINI_1", _numbered("U9", [
        ("3V3", "3V3", "top", 0, "power_in"), ("GND", "GND", "bottom", 0, "power_in"),
        ("GPIO18", "GPIO18 USB_D-", "left", 27.94, "bidirectional"),
        ("GPIO19", "GPIO19 USB_D+", "left", 22.86, "bidirectional"),
        ("GPIO21", "GPIO21 U0TXD", "left", 12.7, "bidirectional"),
        ("GPIO20", "GPIO20 U0RXD", "left", 7.62, "bidirectional"),
        ("EN", "EN", "left", -7.62, "input"), ("GPIO9", "GPIO9 (boot)", "left", -22.86, "bidirectional"),
        ("GPIO2", "GPIO2 (strap)", "left", -27.94, "bidirectional"),
        ("GPIO8", "GPIO8 (strap)", "left", -30.48, "bidirectional"),
        ("GPIO0", "GPIO0", "right", 17.78, "bidirectional"), ("GPIO1", "GPIO1", "right", 12.7, "bidirectional"),
        ("GPIO3", "GPIO3", "right", 7.62, "bidirectional"), ("GPIO10", "GPIO10", "right", 2.54, "bidirectional"),
        ("GPIO4", "GPIO4", "right", -2.54, "bidirectional"), ("GPIO5", "GPIO5", "right", -7.62, "bidirectional"),
        ("GPIO6", "GPIO6", "right", -12.7, "bidirectional"), ("GPIO7", "GPIO7", "right", -17.78, "bidirectional")]),
        half_w=22.86, half_h=33.02, hide_numbers=True),
}
BOX_LIB = {"U1": "CC_IC_TUSB321", "U5": "SUPERVISOR", "U14": "TMUX1101", "U15": "TMUX1101", "U7": "TPS2553_BOX", "U8": "TLV75733P_DBV",
           "U9": "ESP32_C3_MINI_1"}

LED_X0, LED_PITCH, LED_Y = 218.0, 22.86, (190.0, 232.0)
PLACE = {
    "J1": (30, 78.74, 0), "TVS1": (57.15, 63.5, 0), "U6": (68, 118, 0),
    "U1": (gx(50.8), 71.12, 0), "R_VD": (gx(50.8) + 2.54, 49.53, 0), "R1": (gx(76.2), 62.23, 0),
    "U2": (gx(104.14), 66.04, 0), "U13": (gx(121.92), 40.64, 0),
    "U3": (gx(162.56), 50.8, 0), "R4": (gx(137.16), 59.69, 0), "R2": (gx(198.12), 54.61, 0),
    "U14": (gx(223.52), 50.8, 0), "R18": (gx(208.28), 54.61, 0), "C24": (gx(228.6), 38.1, 0),
    "R_ILIM2": (gx(250.19), 50.8, 90),
    "U4": (gx(162.56), 91.44, 0), "R5": (gx(137.16), 100.33, 0), "R3": (gx(198.12), 95.25, 0),
    "U15": (gx(223.52), 91.44, 0), "R19": (gx(208.28), 95.25, 0), "C25": (gx(228.6), 78.74, 0),
    "R_ILIM3B": (gx(241.3), 91.44, 90), "R_ILIM3": (gx(250.19), 91.44, 90),
    "U5": (gx(50.8), 137.16, 0), "R6": (gx(76.2), 130.81, 0), "C1": (gx(78.74), 146.05, 0), "C1B": (gx(86.36), 146.05, 0),
    "C1C": (gx(93.98), 146.05, 0), "C1D": (gx(101.6), 146.05, 0), "C1E": (gx(109.22), 146.05, 0),
    "C1F": (gx(116.84), 146.05, 0),
    "U7": (330.0, 38.1, 0), "R_ILIM1": (BUSX_FULL, 25.4, 180), "C2": (296.0, 20.0, 0),
    "C3": (350.5, 24.0, 0), "R8": (364.0, 36.83, 0),
    "U8": (335.0, 100.0, 0), "C5": (317.0, 103.81, 0), "C6": (353.0, 103.81, 0),
    "U9": (85.0, 222.0, 0), "R9": (48.0, 225.81, 0), "C7": (43.0, 233.43, 0),
    "R13": (148.0, 186.19, 0), "TVS2": (148.0, 193.81, 90), "R12": (158.0, 190.0, 90),
    "SW1": (174.0, 190.0, 0),
    "U10": (158.0, 232.0, 0), "U11": (158.0, 266.0, 0), "R11": (138.0, 269.81, 0),
    "R10": (203.0, 190.0, 90), "C4": (206.0, 205.0, 0),
    "R_SU1": (290.0, 143.0, 90), "C26": (306.0, 149.0, 0), "DZ1": (316.0, 149.0, 270),
    "R_SU14": (330.0, 143.0, 90), "DZ14": (346.0, 149.0, 270),
    "R_SU15": (356.0, 143.0, 90), "DZ15": (372.0, 149.0, 270),
}
TEXT = {
    "J1": (-7.62, 26.0, "left"), "TVS1": (-3.81, -5.5, "left"), "U6": (6.0, 8.0, "left"),
    "U1": (-7.62, 20.5, "left"), "U5": (-5.08, 19.5, "left"), "U7": (-7.62, 17.0, "left"),
    "U8": (-7.62, 15.0, "left"), "U9": (-22.86, -40.0, "left"),
    "U2": (3.81, 7.62, "left"), "U13": (7.62, -6.35, "left"), "U3": (3.81, 8.89, "left"),
    "U4": (3.81, 8.89, "left"), "U10": (3.81, 8.89, "left"), "U11": (3.81, 8.89, "left"),
    "U14": (-6.35, -8.89, "right"), "U15": (-6.35, -8.89, "right"),
    "R_ILIM2": (-2.54, -5.08, "left"), "R_ILIM3": (-2.54, -5.08, "left"), "R_ILIM3B": (-2.54, 2.54, "left"),
    "R_ILIM1": (-2.54, -1.27, "right"),
    "R12": (-3.81, -4.5, "left"), "TVS2": (2.54, 3.0, "left"), "SW1": (-5.08, -7.5, "left"),
    "R10": (-3.81, -4.5, "left"), "R13": (-2.54, -1.27, "right"),
}
HIDE_VALUE = {f"D{i}" for i in range(1, 17)} | {f"C{7 + i}" for i in range(1, 17)}
for i in range(1, 17):
    TEXT[f"D{i}"] = (2.54, -10.5, "left")
    TEXT[f"C{7 + i}"] = (-1.9, -1.27, "right")
for i in range(1, 7):
    TEXT[f"TP{i}"] = (1.5, 1.0, "left")
for i in (5, 6):
    TEXT[f"TP{i}"] = (-2.5, -1.0, "right")


class Full(L.Sheet):
    def __init__(self):
        comps = []
        for ref, (lib, part, fp, value) in PARTS.items():
            if lib is None:
                lib, part = L.NS_LIB, BOX_LIB[ref]
            comps.append({"ref": ref, "lib": lib, "part": part, "footprint": fp, "value": value})
        super().__init__(comps)
        self.sch.paper.paperSize = "A3"
        self.intent = {}
        self.flags = 0

    # ---- intent
    def bind(self, net, ref, pin):
        for p in pads(ref, pin):
            self.intent.setdefault(net, set()).add((ref, p))

    def pin(self, ref, pin):
        """Pin position by pad number or, for U1 and U9, by pin name (stacked pads share the first one's position)."""
        return super().pin(ref, pads(ref, pin)[0])

    def at(self, a):
        return self.pin(*a) if isinstance(a[0], str) else (g(a[0]), g(a[1]))

    # everything the layout draws is snapped to the connection grid
    def wire(self, *pts):
        super().wire(*[(g(p[0]), g(p[1])) for p in pts])

    def junction(self, x, y):
        super().junction(g(x), g(y))

    def label(self, net, x, y, ang=0):
        super().label(net, g(x), g(y), ang)

    def flag(self, x, y, k):
        super().flag(g(x), g(y), k)

    def put(self, ref):
        x, y, rot = PLACE[ref]
        x, y = g(x), g(y)
        PLACE[ref] = (x, y, rot)
        self.place(ref, x, y, rot, TEXT.get(ref, L.DEFAULT_TEXT))
        rot = PLACE[ref][2]
        if rot in (90, 270):
            for p in self.syms[-1].properties:
                if p.key in ("Reference", "Value"):
                    p.position.angle = (-rot) % 360
        if ref.startswith("TP"):        # bare test pads: the footprint is excluded from the BOM, so is the symbol
            self.syms[-1].inBom = False
        if ref in HIDE_VALUE:
            for p in self.syms[-1].properties:
                if p.key == "Value":
                    p.effects.hide = True

    def run(self, net, *pts):
        """Wire through points (pins as (ref, pin) or coordinates); pin ends are bound to net."""
        pts = [self.at(p) if not isinstance(p[0], str) else self.pin(*p) for p in pts]
        self.wire(*pts)

    def ends(self, net, *items):
        """Draw a wire through items and bind every pin item to the net."""
        pts = []
        for it in items:
            if isinstance(it[0], str):
                self.bind(net, *it)
                pts.append(self.pin(*it))
            else:
                pts.append((round(it[0], 4), round(it[1], 4)))
        self.wire(*pts)
        return pts

    def pw(self, net, a, hide=False, rot=0, dy=None):
        """Power symbol with its pin at a (pin or point); binds the pin."""
        x, y = self.at(a)
        if isinstance(a[0], str):
            self.bind(net, *a)
        part = w.RAIL_SYMBOLS.get(net, w.DEFAULT_RAIL_SYMBOL)
        self.lib("power", part)
        ref = f"#PWR{self.n + 1:03d}"
        up = (rot == 180)
        off = (-3.81 if (part != "GND") != up else 3.81)
        self.syms.append(SchematicSymbol(
            libraryNickname="power", entryName=part, position=Position(x, y, rot), unit=1,
            inBom=False, onBoard=False, uuid=self.uid("pwr", net), mirror=None,
            properties=[w.prop("Reference", ref, x, y - 2.54, 0, hide=True),
                        w.prop("Value", net, x + 1.27, y + off, 1, hide, "left")],
            pins={"1": self.uid("pwrpin")},
            instances=[SymbolProjectInstance(w.PROJECT, [SymbolProjectPath(self.root, ref, 1)])]))

    def stub(self, net, a, dx, dy, ang):
        """Wire from a pin to a label dx, dy away."""
        x, y = self.at(a)
        self.bind(net, *a)
        e = (round(x + dx, 4), round(y + dy, 4))
        self.wire((x, y), e)
        self.label(net, *e, ang)
        return e

    def j(self, a):
        self.junction(*self.at(a))

    def nc(self, a):
        self.ncs.append(L.NoConnect(Position(*self.at(a)), self.uid("nc")))

    def rail(self, net, x, y):
        self.pw(net, (x, y))
        self.wire((x, y), (x + 10.16, y))
        self.flags += 1
        self.flag(x + 10.16, y, self.flags)

    def tp(self, ref, net, x, y, from_pt=None):
        """Test point whose pin is at (x, y); a wire from from_pt (if any) ends there."""
        px, py = self.at(("%s" % ref, "1")) if False else (None, None)
        if from_pt:
            self.wire(from_pt, (x, y))
        self.bind(net, ref, 1)

    def caption(self, msg, x, y, size=1.8):
        self.text(msg, x, y, size)


def _away(s, ref, pin, other):
    """Stub offset (dx, dy) that points from the other pin of a two-pin part through this pin."""
    (x1, y1), (x0, y0) = s.pin(ref, pin), s.pin(ref, other)
    dx, dy = x1 - x0, y1 - y0
    n = max(abs(dx), abs(dy)) or 1.0
    return round(5.08 * dx / n, 4), round(5.08 * dy / n, 4)


def build():
    saved = dict(L.BOX)
    L.BOX.update(BOXES)
    try:
        return _build()
    finally:
        L.BOX.clear()
        L.BOX.update(saved)


def _build():
    s = Full()
    for ref in PLACE:
        s.put(ref)
    for i in range(1, 17):
        row, col = divmod(i - 1, 8)
        PLACE[f"D{i}"] = (LED_X0 + col * LED_PITCH, LED_Y[row], 0)
        s.put(f"D{i}")
        PLACE[f"C{7 + i}"] = (LED_X0 + col * LED_PITCH + 11.43 + 1.27, LED_Y[row] - 11.43, 0)
        s.put(f"C{7 + i}")
    # test points sit with their pin on the wire end: placed once the end is known
    P = s.pin

    # ------------------------------------------------------------ captions
    s.caption("USB-C input (HW-003)", 18, 12)
    s.caption("CC detection and gate (ADR-0016): OUT1_N low = 1.5 A or more advertised", gx(38.1), 27.0)
    s.caption("Gate: step enable = select AND CC OK AND hold-off done; step 2 also AND NOT step 3 enable (U13)", gx(128.27), 20.0)
    s.caption("Hold-off after VBUS returns (HW-010: 200 to 600 ms)", gx(38.1), 111.76)
    s.caption("Current limit: TPS2553 (ADR-0010 option A); pins per SLVS841G", 262, 8)
    s.caption("3.3 V regulator (part not chosen)", 305, 78)
    s.caption("TUSB321: pins 3, 6, 7, 8, 9, 11 numbered; others named", gx(38.1), 99.0, 1.27)
    s.caption("TPS3840DL40 is a candidate, not chosen", gx(38.1), 164.0, 1.27)
    s.caption("ESP32-C3-MINI-1 module (box uses GPIO names, module pin numbers not drawn)", 15, 172)
    s.caption("Button (HW-007; GPIO5 is not a strapping pin)", 128, 172)
    s.caption("GATE_OK_RB = HOLD_OK AND FAULT_N (ADR-0018 option E); 3.3 V gate, inputs accept 5 V", 128, 211)
    s.caption("OE tied to GND (symbol drawn pointing up)", 160.0, 249.5, 1.0)
    s.caption("LED data: 5 V buffer (HW-002)", 128, 246)
    s.caption("16 LEDs as a chain; the ring geometry is a PCB matter (HW-001)", 200, 172)
    s.caption("Rails (sources are in this sheet):", 18, 20, 1.27)

    # ------------------------------------------------------------ rails with power flags
    for k, net in enumerate(("VBUS_IC", "+5V", "+3V3", "GND")):
        s.rail(net, 20, 28 + 7 * k)

    # ------------------------------------------------------------ USB-C
    for pin in ("A4", "B4", "A9", "B9"):
        s.bind("VBUS_IC", "J1", pin)
    vb = P("J1", "A4")
    s.wire(vb, (53.34, vb[1]))
    s.pw("VBUS_IC", (48.26, vb[1]), True)
    s.junction(48.26, vb[1])
    s.bind("VBUS_IC", "TVS1", 1)
    s.bind("GND", "TVS1", 2)
    s.pw("GND", ("TVS1", "2"), True)
    for pin in ("A1", "B1", "A12", "B12"):
        s.bind("GND", "J1", pin)
    s.pw("GND", P("J1", "A1"))
    s.pw("GND", ("J1", "SH"), True)
    s.nc(P("J1", "A8"))
    s.nc(P("J1", "B8"))
    s.caption("Shield to GND (shield network not drawn)", 14, 113, 1.27)
    # CC lines straight to the CC IC, labelled
    for jp, up, net in (("A5", "CC1", "CC1"), ("B5", "CC2", "CC2")):
        s.ends(net, ("J1", jp), ("U1", up))
        s.label(net, 70, P("J1", jp)[1])
    # data lines: tie both receptacle pins, then to the ESD part
    for pins, net, up, tx in ((("A7", "B7"), "USB_DN_RAW", "1", 55.4), (("A6", "B6"), "USB_DP_RAW", "3", 50.32)):
        a, b = P("J1", pins[0]), P("J1", pins[1])
        s.bind(net, "J1", pins[0])
        s.bind(net, "J1", pins[1])
        ya, yb = a[1], b[1]
        s.wire(a, (50.32, ya), (50.32, yb))
        s.wire(b, (50.32, yb))
        s.junction(50.32, yb)
    u6 = {"1": ("USB_DN_RAW", "6"), "3": ("USB_DP_RAW", "4")}
    s.bind("USB_DN_RAW", "U6", 1)   # pins 1 and 6 (3 and 4) are one channel inside the part, two nets here
    s.bind("USB_DP_RAW", "U6", 3)
    ydn = P("J1", "B7")[1]
    ydp = P("J1", "B6")[1]
    s.wire((50.32, ydn), (55.4, ydn), (55.4, P("U6", "1")[1]), P("U6", "1"))
    s.wire((50.32, ydp), (50.32, P("U6", "3")[1]), P("U6", "3"))
    s.pw("VBUS_IC", ("U6", "5"), True)
    s.pw("GND", ("U6", "2"), True)
    s.stub("USB_DN", ("U6", "6"), 6.6, 0, 0)
    s.stub("USB_DP", ("U6", "4"), 6.6, 0, 0)

    # ------------------------------------------------------------ CC IC, pull-ups, inverters
    s.stub("VDD_U1", ("U1", "VDD"), 0, -5.08, 90)   # supply through R_SU1 (surge protection)
    s.pw("GND", ("U1", "GND"))
    s.pw("GND", ("U1", "PORT"), True)
    for pin in ("3", "6", "9", "11"):  # CURRENT_MODE, VCONN_FAULT, ID, DIR: DFP/VCONN/orientation features, unused (UFP)
        s.nc(P("U1", pin))
    s.ends("VBUS_DET_N", ("R_VD", "2"), ("U1", "VBUS_DET"))
    s.pw("VBUS_IC", ("R_VD", "1"))
    o1 = P("U1", "7")
    s.ends("CC_OUT1_N", ("U1", "7"), ("U2", "2"))
    s.label("CC_OUT1_N", *P("U2", "2"), 180)   # the same net also feeds U13 (exclusive steps)
    s.pw("VBUS_IC", ("R1", "1"))
    s.bind("CC_OUT1_N", "R1", 2)
    s.j(("R1", "2"))
    s.pw("+3V3", ("U2", "5"))
    s.pw("GND", ("U2", "3"))
    s.nc(P("U2", "1"))
    y2 = P("U2", "4")
    s.ends("CC_OK_1A5", ("U2", "4"), (y2[0] + 5.08, y2[1]))
    s.bind("CC_OK_1A5", "U2", 4)
    s.label("CC_OK_1A5", y2[0] + 5.08, y2[1])
    # OUT2 is not used: no 3 A reading (owner decision 2026-11-07, OUT2 is not a clean 3 A signal); the pin is left open
    s.nc(P("U1", "8"))

    # ------------------------------------------------------------ gates and ILIM switches
    for g, rsel, ren, sw, rpd, cap, sel, en in (("U3", "R4", "R2", "U14", "R18", "C24", "SEL_STEP2_GPIO", "ILIM_STEP2_EN"),
                                                ("U4", "R5", "R3", "U15", "R19", "C25", "SEL_STEP3_GPIO", "ILIM_STEP3_EN")):
        a, b, c, yo = P(g, 1), P(g, 3), P(g, 6), P(g, 4)
        okn = "CC_OK_1A5" if g == "U4" else "CC_OK_NOT_S3"   # step 2 sees CC OK AND NOT step 3 enable
        s.wire(a, (a[0] - 7.62, a[1]))
        s.bind(okn, g, 1)
        s.label(okn, a[0] - 7.62, a[1], 180)
        s.wire(c, (c[0] - 7.62, c[1]))
        s.bind("HOLD_OK", g, 6)
        s.label("HOLD_OK", c[0] - 7.62, c[1], 180)
        bs = P(rsel, 1)
        s.wire(b, bs)
        s.bind(sel, g, 3)
        s.bind(sel, rsel, 1)
        s.label(sel, *bs, 180)
        s.pw("GND", (rsel, "2"), True)
        s.pw("+3V3", (g, "5"), True)
        s.pw("GND", (g, "2"), True)
        # owner decision 2026-11-05 (a): the gate output drives SEL of a TMUX1101 (high = on); R2/R3 (10k) and the
        # 100 kohm pull-down R18/R19 hang on the net, so an open gate output means switch off (step 1)
        s.bind(en, g, 4)
        s.bind(en, sw, 4)
        s.wire(yo, P(sw, 4))
        for r_ in (ren, rpd):
            s.bind(en, r_, 1)
            s.junction(*P(r_, 1))
            s.pw("GND", (r_, "2"), True)
        s.label(en, yo[0] + 2.54, yo[1])
        # switch supply with 0.1 uF; S and GND pins to ground
        vdd = P(sw, 5)
        ty = P(cap, 1)[1]
        vnet = f"VDD_{sw}"   # supply through R_SU14 / R_SU15 (surge protection)
        s.bind(vnet, sw, 5)
        s.bind(vnet, cap, 1)
        s.wire(vdd, (vdd[0], ty), P(cap, 1))
        s.junction(vdd[0], ty)
        s.label(vnet, vdd[0], ty, 90)
        s.pw("GND", (cap, "2"), True)
        s.bind("GND", sw, 3)
        s.bind("GND", sw, 2)
        s.pw("GND", (sw, "3"), True)
        s.wire(P(sw, 2), P(sw, 3))
    # step 2: switch - 56.2 k - ILIM; step 3: switch - 301 ohm - 27.4 k - ILIM (decision (b))
    for sw, chain, tag in (("U14", ("R_ILIM2",), "ILIM_D_U14"), ("U15", ("R_ILIM3B", "R_ILIM3"), "ILIM_D_U15")):
        prev, prev_pin = P(sw, 1), (sw, 1)
        for k, rl in enumerate(chain):
            (lo_pin, lo), (hi_pin, hi) = sorted((("1", P(rl, 1)), ("2", P(rl, 2))), key=lambda e: e[1][0])
            net = tag if k == 0 else tag + "_MID"
            s.bind(net, *prev_pin)
            s.bind(net, rl, lo_pin)
            s.wire(prev, lo)
            prev, prev_pin = hi, (rl, hi_pin)
        s.bind("ILIM", *prev_pin)
        s.wire(prev, (BUSX_FULL, prev[1]))
    # exclusive steps (owner decision 2026-11-05): U13 = NOR(CC_OUT1_N, ILIM_STEP3_EN) = CC OK AND NOT step 3
    # enable; it replaces CC OK on the step 2 AND, so step 3 on forces step 2 off. Unpowered -> low -> step 2 off.
    a, b, y = P("U13", 1), P("U13", 2), P("U13", 4)
    s.stub("CC_OUT1_N", ("U13", 1), -5.08, 0, 180)
    s.stub("ILIM_STEP3_EN", ("U13", 2), -5.08, 0, 180)
    s.stub("CC_OK_NOT_S3", ("U13", 4), 5.08, 0, 0)
    s.pw("+3V3", ("U13", "5"), True)
    s.pw("GND", ("U13", "3"), True)
    # ILIM bus: both switched resistor chains meet on a vertical bus that runs up to the TPS2553 ILIM pin
    y2, y3 = P("R_ILIM2", 1)[1], P("R_ILIM3", 1)[1]
    il = P("U7", "5")
    s.wire((BUSX_FULL, y3), (BUSX_FULL, il[1]), il)
    s.junction(BUSX_FULL, y2)
    s.bind("ILIM", "U7", 5)
    s.label("ILIM", BUSX_FULL, il[1] + 5.08 * 2, 90)
    s.bind("ILIM", "R_ILIM1", 1)
    s.wire(P("R_ILIM1", 1), (BUSX_FULL, il[1]))
    s.junction(BUSX_FULL, il[1])
    s.pw("GND", ("R_ILIM1", "2"), True, 180)

    # ------------------------------------------------------------ hold-off supervisor
    s.pw("VBUS_IC", ("U5", "2"), True)
    s.pw("GND", ("U5", "3"))
    s.nc(P("U5", "4"))
    rs = P("U5", "1")
    s.bind("HOLD_OK", "U5", 1)
    s.wire(rs, (gx(101.6), rs[1]))
    s.bind("HOLD_OK", "R6", 2)
    s.junction(*P("R6", "2"))
    s.pw("VBUS_IC", ("R6", "1"))
    s.label("HOLD_OK", gx(101.6), rs[1])
    ct = P("U5", "5")
    s.bind("SUP_CT", "U5", 5)
    s.bind("SUP_CT", "C1", 1)
    s.wire(ct, P("C1", 1))
    s.bind("SUP_CT", "C1B", 1)
    for a_, b_ in (("C1", "C1B"), ("C1B", "C1C"), ("C1C", "C1D"), ("C1D", "C1E"), ("C1E", "C1F")):   # parallel C0G set, one rail wire
        s.bind("SUP_CT", b_, 1)
        s.wire(P(a_, 1), P(b_, 1))
    for r_ in ("C1", "C1B", "C1C", "C1D", "C1E"):
        s.junction(*P(r_, 1))
    s.label("SUP_CT", gx(68.58), ct[1])
    for r_ in ("C1", "C1B", "C1C", "C1D", "C1E", "C1F"):
        s.pw("GND", (r_, "2"), True)

    # ------------------------------------------------------------ TPS2553 and 5 V output
    uin, uen = P("U7", "1"), P("U7", "3")
    s.bind("VBUS_IC", "U7", 1)
    s.bind("VBUS_IC", "U7", 3)
    s.wire(uin, (uin[0], 20.32), (uen[0], 20.32), uen)
    mid = ((uin[0] + uen[0]) / 2, 20.32)
    s.pw("VBUS_IC", mid)
    s.junction(*mid)
    s.pw("GND", ("U7", "2"), True)
    s.bind("VBUS_IC", "C2", 1)
    s.pw("VBUS_IC", ("C2", "1"))
    s.pw("GND", ("C2", "2"), True)
    out = P("U7", "6")
    s.bind("+5V", "U7", 6)
    s.wire(out, (356.0, out[1]))
    s.pw("+5V", (356.0, out[1]))
    s.pw("+5V", ("C3", "1"), True)
    s.pw("GND", ("C3", "2"), True)
    fl = P("U7", "4")
    s.bind("FAULT_N", "U7", 4)
    s.wire(fl, (372.0, fl[1]))
    s.label("FAULT_N", 372.0, fl[1])
    s.bind("FAULT_N", "R8", 2)
    s.junction(*P("R8", "2"))
    s.pw("+3V3", ("R8", "1"))

    # ------------------------------------------------------------ 3.3 V regulator
    rin = P("U8", "1")
    s.bind("+5V", "U8", "1")
    s.wire((312.0, rin[1]), rin)
    s.pw("+5V", (312.0, rin[1]))
    ren = P("U8", "3")                         # EN tied to IN (always on; TLV757P datasheet)
    s.bind("+5V", "U8", "3")
    s.wire(ren, (ren[0] - 3.81, ren[1]))
    s.wire((ren[0] - 3.81, ren[1]), (ren[0] - 3.81, rin[1]))
    s.junction(ren[0] - 3.81, rin[1])
    s.nc(P("U8", "4"))
    s.bind("+5V", "C5", 1)
    s.junction(*P("C5", 1))
    s.pw("GND", ("C5", "2"), True)
    rout = P("U8", "5")
    s.bind("+3V3", "U8", "5")
    s.wire(rout, (362.0, rout[1]))
    s.pw("+3V3", (362.0, rout[1]))
    s.bind("+3V3", "C6", 1)
    s.junction(*P("C6", 1))
    s.pw("GND", ("C6", "2"), True)
    s.pw("GND", ("U8", "2"))
    for k, (net, ref, y) in enumerate((("+5V", "TP1", 112.0), ("+3V3", "TP2", 122.0), ("GND", "TP3", 132.0))):
        x = 372.0
        s.pw(net, (x, y), net != "GND" and False)
        s.wire((x, y), (x + 7.62, y))
        PLACE[ref] = (x + 7.62, y, 0)
        s.put(ref)
        s.bind(net, ref, 1)

    # ------------------------------------------------------------ MCU
    s.pw("+3V3", ("U9", "3V3"))
    s.pw("GND", ("U9", "GND"))
    for pin, net in (("GPIO0", "CC_OK_1A5"), ("GPIO3", "SEL_STEP2_GPIO"),
                     ("GPIO10", "SEL_STEP3_GPIO"), ("GPIO5", "BUTTON"),
                     ("GPIO6", "GATE_OK_RB"), ("GPIO7", "LED_DATA")):
        s.stub(net, ("U9", pin), 5.08, 0, 0)
    s.nc(P("U9", "GPIO4"))   # reserved for the orientation sensor (HW-011); FAULT_N is read through U10
    s.nc(P("U9", "GPIO1"))   # was CC_OK_3A: OUT2 reading deleted (owner decision 2026-11-07)
    s.stub("USB_DN", ("U9", "GPIO18"), -5.08, 0, 180)
    s.stub("USB_DP", ("U9", "GPIO19"), -5.08, 0, 180)
    # test points on the left side
    a = P("U9", "GPIO9")
    s.bind("BOOT", "U9", "GPIO9")
    s.wire(a, (36.0, a[1]))
    PLACE["TP6"] = (36.0, a[1], 0)
    s.put("TP6")
    s.bind("BOOT", "TP6", 1)
    # gate-enable readbacks on GPIO20 / GPIO21 (HW-010 proposed amendment); 100k series resistor
    # because GPIO21 (U0TXD) is an output while the ROM prints boot messages;
    # 100k series with 10k pull-downs R2/R3 keeps an open gate output below the TMUX1101 SEL VIL max (and the old 2N7002 Vgs(th) min) (N1,
    # analysis-n1-n2-readback-backfeed.md); firmware must switch the internal pull-ups of GPIO20/21 off
    for pin, net, rb, ref in (("GPIO20", "ILIM_STEP2_EN", "STEP2_EN_RB", "R14"),
                              ("GPIO21", "ILIM_STEP3_EN", "STEP3_EN_RB", "R15")):
        a = P("U9", pin)
        s.bind(rb, "U9", pin)
        PLACE[ref] = (44.0, a[1], 90)
        s.put(ref)
        near, far = sorted(("1", "2"), key=lambda k: -P(ref, k)[0])
        s.bind(rb, ref, near)
        s.wire(a, P(ref, near))
        s.bind(net, ref, far)
        e = (P(ref, far)[0] - 5.08, a[1])
        s.wire(P(ref, far), e)
        s.label(net, e[0], e[1], 180)
    # strapping pins GPIO2 and GPIO8 float by default (module datasheet Tables 4-1, 4-3): pull both
    # up (GPIO2 against glitches, GPIO8 = 1 for download boot; GPIO8 = 1 also leaves UART0 ROM
    # printing enabled while the eFuse default is unchanged)
    dy = P("R9", "2")[1] - PLACE["R9"][1]
    for pin, ref in (("GPIO2", "R16"), ("GPIO8", "R17")):
        a = P("U9", pin)
        s.bind("PULL_" + pin, "U9", pin)
        PLACE[ref] = (30.0, a[1] - dy, 0)
        s.put(ref)
        s.bind("PULL_" + pin, ref, 2)
        s.wire(a, (30.0, a[1]))
        s.junction(*P(ref, "2"))
        s.bind("+3V3", ref, 1)
        s.pw("+3V3", (ref, "1"))
    # reset: pull-up and capacitor, test point
    en = P("U9", "EN")
    s.bind("CHIP_EN", "U9", "EN")
    s.wire(en, (38.0, en[1]))
    PLACE["TP5"] = (38.0, en[1], 0)
    s.put("TP5")
    s.bind("CHIP_EN", "TP5", 1)
    s.bind("CHIP_EN", "R9", 2)
    s.junction(*P("R9", "2"))
    s.pw("+3V3", ("R9", "1"))
    s.bind("CHIP_EN", "C7", 1)
    s.junction(*P("C7", "1"))
    s.pw("GND", ("C7", "2"), True)

    # ------------------------------------------------------------ button
    bt = (124.0, 190.0)
    s.stub("BUTTON", ("R12", "1"), 0, 0, 0) if False else None
    s.bind("BUTTON", "R12", 1)
    s.wire((134.0, 190.0), P("R12", 1))
    s.label("BUTTON", 134.0, 190.0, 180)
    s.bind("BUTTON", "R13", 2)
    s.junction(148.0, 190.0)
    s.pw("+3V3", ("R13", "1"))
    s.bind("BUTTON", "TVS2", 2)
    s.bind("GND", "TVS2", 1)
    s.pw("GND", ("TVS2", "1"), True)
    s.bind("BTN_SW", "R12", 2)
    s.bind("BTN_SW", "SW1", 1)
    s.wire(P("R12", 2), P("SW1", 1))
    s.bind("GND", "SW1", 2)
    sw2 = P("SW1", 2)
    s.wire(sw2, (sw2[0] + 4.0, sw2[1]))
    s.pw("GND", (sw2[0] + 4.0, sw2[1]))

    # ------------------------------------------------------------ gate OK readback: AND of HOLD_OK and FAULT_N
    # ADR-0018 option E: one input pin on GPIO6 reports "hold-off done AND no load-switch fault"
    a1 = P("U10", 1)
    s.bind("FAULT_N", "U10", 1)
    s.wire(a1, (a1[0] - 6.0, a1[1]))
    s.label("FAULT_N", a1[0] - 6.0, a1[1], 180)
    a = P("U10", 2)
    s.bind("HOLD_OK", "U10", 2)
    s.wire(a, (a[0] - 6.0, a[1]))
    s.label("HOLD_OK", a[0] - 6.0, a[1], 180)
    y = P("U10", 4)
    s.bind("GATE_OK_RB", "U10", 4)
    s.wire(y, (y[0] + 6.0, y[1]))
    s.label("GATE_OK_RB", y[0] + 6.0, y[1])
    s.pw("+3V3", ("U10", "5"), True)
    s.pw("GND", ("U10", "3"), True)

    # ------------------------------------------------------------ supply-pin protection (HW-010 amendment)
    s.caption("Supply pins with 6 V maximum (TUSB321, TMUX1101): series resistor, 100 nF, 5.1 V zener", 288, 132, 1.27)
    for rs, dz, vnet, cap in (("R_SU1", "DZ1", "VDD_U1", "C26"), ("R_SU14", "DZ14", "VDD_U14", None),
                              ("R_SU15", "DZ15", "VDD_U15", None)):
        s.pw("VBUS_IC", (rs, "1"), True)
        away = _away(s, rs, "2", "1")
        s.stub(vnet, (rs, "2"), *away, 0)
        s.pw("GND", (dz, "1"), True)
        e = s.stub(vnet, (dz, "3"), 0, -5.08, 90)
        s.flags += 1
        s.flag(e[0], e[1], s.flags)   # the resistor is passive: the node needs a power flag
        if cap:
            s.stub(vnet, (cap, "1"), 0, -5.08, 90)
            s.pw("GND", (cap, "2"), True)

    # ------------------------------------------------------------ LED data buffer
    a = P("U11", 2)
    s.bind("LED_DATA", "U11", 2)
    s.wire(a, (a[0] - 10.0, a[1]))
    s.label("LED_DATA", a[0] - 10.0, a[1], 180)
    pd = P("R11", 1)
    s.bind("LED_DATA", "R11", 1)
    s.junction(*pd)
    s.pw("GND", ("R11", "2"), True)
    PLACE["TP4"] = (pd[0], a[1] - 6.0, 0)
    s.put("TP4")
    s.bind("LED_DATA", "TP4", 1)
    s.wire(pd, PLACE["TP4"][:2])
    y = P("U11", 4)
    s.bind("LED_BUF", "U11", 4)
    s.wire(y, (y[0] + 6.0, y[1]))
    s.label("LED_BUF", y[0] + 6.0, y[1])
    s.pw("+5V", ("U11", "5"), True)
    s.pw("GND", ("U11", "3"), True)
    oe = P("U11", 1)
    s.bind("GND", "U11", 1)
    s.wire(oe, (oe[0], oe[1] - 4.0))
    s.pw("GND", (oe[0], oe[1] - 4.0), True, 180)

    # ------------------------------------------------------------ LED chain
    s.bind("LED_BUF", "R10", 1)
    r10l = P("R10", 1)
    s.wire((r10l[0] - 2.5, r10l[1]), r10l)
    s.label("LED_BUF", r10l[0] - 2.5, r10l[1], 180)
    s.bind("LED_N0", "R10", 2)
    s.bind("LED_N0", "D1", LED_DIN)
    s.wire(P("R10", 2), P("D1", LED_DIN))
    for i in range(1, 17):
        d, c = f"D{i}", f"C{7 + i}"
        s.pw("+5V", (d, LED_VDD), True)
        s.pw("GND", (d, LED_VSS), True)
        s.pw("+5V", (c, "1"), True)
        s.pw("GND", (c, "2"), True)
        if i % 8:
            nxt = f"D{i + 1}"
            net = f"LED_N{i}"
            s.bind(net, d, LED_DOUT)
            s.bind(net, nxt, LED_DIN)
            s.wire(P(d, LED_DOUT), P(nxt, LED_DIN))
    dout = P("D8", LED_DOUT)
    s.bind("LED_ROW2", "D8", LED_DOUT)
    s.wire(dout, (dout[0] + 4.0, dout[1]))
    s.label("LED_ROW2", dout[0] + 4.0, dout[1])
    din = P("D9", LED_DIN)
    s.bind("LED_ROW2", "D9", LED_DIN)
    s.wire(din, (din[0] - 4.0, din[1]))
    s.label("LED_ROW2", din[0] - 4.0, din[1], 180)
    s.nc(P("D16", LED_DOUT))
    # bulk capacitor on 5 V
    s.pw("+5V", ("C4", "1"))
    s.pw("GND", ("C4", "2"))

    sch = s.finish()
    sch.titleBlock = TitleBlock(
        title="busy-light full board (spike, exploratory)", date="2026-11-04", revision="spike",
        company="busy-light", comments={1: "Not a product schematic: ADR-0012 is Proposed",
                                        2: "Placeholders and unread pins are marked; see spike-full-board-schematic.md"})
    return sch, s.intent


def write(out_path, intent_path=None):
    sch, intent = build()
    sch.to_file(out_path)
    lib_tables.write_schematic_project(out_path)
    if intent_path:
        with open(intent_path, "w", encoding="utf-8") as f:
            json.dump({k: sorted(v) for k, v in sorted(intent.items())}, f, indent=0)


if __name__ == "__main__":
    write(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
