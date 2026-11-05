# SPDX-License-Identifier: Apache-2.0
"""Spike: hand-laid-out schematic of the ADR-0016 gate fragment, written by script (ADR-0012).

Same deterministic approach as write_sch.py (kiutils, uuid5, no randomness), but with an explicit
layout: signal flow left to right, real wires for local connections, net labels for the rest,
power symbols, section captions. Coordinates are in this file; the netlist (SKiDL gate.net) is the
source of values, footprints and library symbols, and check_gate.py proves that the drawn wiring
matches it (ERC + net parity). The two placeholder ICs get generated box symbols with named pins.

Usage: layout_sch.py <gate.net> <output.kicad_sch>
"""
import sys

from kiutils.items.common import Position, Stroke, TitleBlock
from kiutils.items.schitems import (Connection, Junction, LocalLabel, NoConnect, SchematicSymbol,
                                    SymbolProjectInstance, SymbolProjectPath, Text)
from kiutils.schematic import Schematic
from kiutils.symbol import Symbol
from kiutils.utils import sexpr

import lib_tables
import write_sch as w

NS_LIB = "busylight_gate"
SIZE = 1.27
BUSX = 259.08   # x of the ILIM bus in the gate fragment frame


def box_symbol(name, pins, half_w=7.62, half_h=10.16, ref="U", hide_numbers=False):
    """Library symbol text: rectangle body and pins (number, name, side, offset, etype).

    side is top/bottom/left/right; offset (mm) is along the side; pins are 5.08 mm long and their
    outer end lies half_w + 5.08 (or half_h + 5.08) from the centre.
    """
    out = []
    for num, pname, side, off, etype in pins:
        x, y, ang = {"top": (off, -(half_h + 5.08), 270), "bottom": (off, half_h + 5.08, 90),
                     "left": (-(half_w + 5.08), off, 0), "right": (half_w + 5.08, off, 180)}[side]
        # lib coordinates are y up: top pins have positive y
        if side == "top":
            y, ang = half_h + 5.08, 270
        if side == "bottom":
            y, ang = -(half_h + 5.08), 90
        out.append(f'(pin {etype} line (at {x} {y} {ang}) (length 5.08) '
                   f'(name "{pname}" (effects (font (size {SIZE} {SIZE})))) '
                   f'(number "{num}" (effects (font (size {SIZE} {SIZE})))))')
    hn = " (pin_numbers hide)" if hide_numbers else ""
    txt = f'''(symbol "{name}"{hn} (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
 (property "Reference" "{ref}" (at 0 0 0) (effects (font (size {SIZE} {SIZE}))))
 (property "Value" "{name}" (at 0 0 0) (effects (font (size {SIZE} {SIZE}))))
 (property "Footprint" "" (at 0 0 0) (effects (font (size {SIZE} {SIZE})) hide))
 (property "Datasheet" "" (at 0 0 0) (effects (font (size {SIZE} {SIZE})) hide))
 (symbol "{name}_0_1" (rectangle (start {-half_w} {half_h}) (end {half_w} {-half_h})
   (stroke (width 0.254) (type default)) (fill (type background))))
 (symbol "{name}_1_1" {' '.join(out)}))'''
    sym = Symbol.from_sexpr(sexpr.parse_sexp(txt))
    sym.libraryNickname = NS_LIB
    sym.libId = f"{NS_LIB}:{name}"
    return sym


CC_IC = box_symbol("CC_DETECT_IC", [
    ("1", "VDD", "top", 0, "power_in"), ("2", "GND", "bottom", 0, "power_in"),
    ("3", "OUT1_N", "right", 5.08, "open_collector"), ("4", "OUT2_N", "right", 0, "open_collector"),
    ("5", "RES", "right", -5.08, "passive")])
SUPERVISOR = box_symbol("SUPERVISOR", [
    ("2", "VDD", "top", 0, "power_in"), ("3", "GND", "bottom", 0, "power_in"),
    ("1", "RESET", "right", 2.54, "open_collector"), ("5", "CT", "right", -5.08, "passive"),
    ("4", "MR", "left", 0, "passive")])
# TMUX1101DCK (SCDS410D tab. 5-1): 1 D, 2 S, 3 GND, 4 SEL, 5 VDD. SEL left, D right, VDD top, S and GND bottom.
TMUX1101 = box_symbol("TMUX1101", [
    ("5", "VDD", "top", 0, "power_in"), ("3", "GND", "bottom", -2.54, "power_in"),
    ("2", "S", "bottom", 2.54, "passive"), ("4", "SEL", "left", 0, "input"),
    ("1", "D", "right", 0, "passive")], half_w=5.08, half_h=7.62)
BOX = {"U1": CC_IC, "U5": SUPERVISOR, "U14": TMUX1101, "U15": TMUX1101}

# (x, y, rotation) of every part; pin ends are derived from the library symbols.
PLACE = {
    "U1": (50.8, 71.12, 0), "R1": (76.2, 62.23, 0), "U2": (104.14, 66.04, 0), "U13": (121.92, 40.64, 0),
    "U3": (162.56, 50.8, 0), "R4": (137.16, 59.69, 0), "R2": (198.12, 54.61, 0),
    "U14": (223.52, 50.8, 0), "R18": (208.28, 54.61, 0), "C24": (228.6, 38.1, 0),
    "R_ILIM2": (250.19, 50.8, 90),
    "U4": (162.56, 91.44, 0), "R5": (137.16, 100.33, 0), "R3": (198.12, 95.25, 0),
    "U15": (223.52, 91.44, 0), "R19": (208.28, 95.25, 0), "C25": (228.6, 78.74, 0),
    "R_ILIM3B": (241.3, 91.44, 90), "R_ILIM3": (250.19, 91.44, 90),
    "U5": (50.8, 137.16, 0), "R6": (76.2, 130.81, 0), "C1": (78.74, 146.05, 0), "C1B": (86.36, 146.05, 0),
    "C1C": (93.98, 146.05, 0), "C1D": (101.6, 146.05, 0),
}
# where the reference and value text goes: (dx, dy, justify) relative to the part
TEXT = {"U1": (-2.54, -13.97, "right"), "U5": (-2.54, -13.97, "right"),
        "U2": (3.81, 7.62, "left"), "U13": (7.62, -6.35, "left"), "U3": (3.81, 8.89, "left"), "U4": (3.81, 8.89, "left"),
        "U14": (-6.35, -8.89, "right"), "U15": (-6.35, -8.89, "right"),
        "R_ILIM2": (-2.54, -5.08, "left"), "R_ILIM3": (-2.54, -5.08, "left"), "R_ILIM3B": (-2.54, 2.54, "left")}
DEFAULT_TEXT = (2.54, -1.27, "left")


class Sheet:
    def __init__(self, comps):
        self.comps = {c["ref"]: c for c in comps}
        self.sch = Schematic.create_new()
        self.sch.version = 20231120
        self.sch.generator = "busy-light-layout_sch"
        self.sch.uuid = w.uid("layout-root")
        self.sch.paper.paperSize = "A3"
        self.root = "/" + self.sch.uuid
        self.sch.sheetInstances = []
        self.syms, self.wires, self.labels, self.ncs, self.juncs, self.texts = [], [], [], [], [], []
        self.libs = {}
        self.pins = {}
        self.n = 0

    def lib(self, lib, part):
        if (lib, part) not in self.libs:
            sym = w.load_symbol(lib, part)
            if lib == "power":
                sym.hidePinNumbers = True   # the number of a power symbol pin only clutters the part pin
            self.libs[(lib, part)] = sym
        return self.libs[(lib, part)]

    def uid(self, *k):
        self.n += 1
        return w.uid(f"layout.{self.n}." + ".".join(map(str, k)))

    def place(self, ref, x, y, rot, text=DEFAULT_TEXT):
        c = self.comps[ref]
        if ref in BOX:
            sym = BOX[ref]
            lib, part = NS_LIB, sym.entryName
            self.libs[(lib, part)] = sym
        else:
            lib, part = c["lib"], c["part"]
            sym = self.lib(lib, part)
        pins = w.sym_pins(sym)
        for number, lx, ly, _a, _t in pins:
            ox, oy = w.transform(lx, ly, rot)
            self.pins[(ref, number)] = (w.r(x + ox), w.r(y + oy))
        dx, dy, just = text
        self.syms.append(SchematicSymbol(
            libraryNickname=lib, entryName=part, position=Position(x, y, rot), unit=1,
            inBom=True, onBoard=True, uuid=w.uid("lsym" + ref),
            properties=[w.prop("Reference", ref, x + dx, y + dy, 0, False, just),
                        w.prop("Value", c["value"], x + dx, y + dy + 2.54, 1, False, just),
                        w.prop("Footprint", c["footprint"], x, y, 2, True),
                        w.prop("Datasheet", "", x, y, 3, True)],
            pins={p[0]: w.uid(f"lpin{ref}.{p[0]}") for p in pins},
            instances=[SymbolProjectInstance(w.PROJECT, [SymbolProjectPath(self.root, ref, 1)])]))

    def pin(self, ref, number):
        return self.pins[(ref, str(number))]

    def wire(self, *pts):
        for a, b in zip(pts, pts[1:]):
            self.wires.append(Connection(type="wire", points=[Position(*a), Position(*b)],
                                         stroke=Stroke(0, "default"), uuid=self.uid("w")))

    def junction(self, x, y):
        self.juncs.append(Junction(position=Position(x, y), diameter=0, uuid=self.uid("j")))

    def label(self, net, x, y, ang=0):
        just = w.Justify(horizontally="right" if ang == 180 else "left")
        self.labels.append(LocalLabel(net, Position(x, y, ang), w.eff(just), self.uid("l", net)))

    def nc(self, x, y):
        self.ncs.append(NoConnect(Position(x, y), self.uid("nc")))

    def power(self, net, x, y):
        """Power symbol whose pin is at (x, y)."""
        part = w.RAIL_SYMBOLS.get(net, w.DEFAULT_RAIL_SYMBOL)
        self.lib("power", part)
        ref = f"#PWR{self.n + 1:03d}"
        self.syms.append(SchematicSymbol(
            libraryNickname="power", entryName=part, position=Position(x, y, 0), unit=1,
            inBom=False, onBoard=False, uuid=self.uid("pwr", net), mirror=None,
            properties=[w.prop("Reference", ref, x, y - 2.54, 0, hide=True),
                        w.prop("Value", net, x + 1.27, y + (3.81 if part == "GND" else -3.81), 1,
                               False, "left")],
            pins={"1": self.uid("pwrpin")},
            instances=[SymbolProjectInstance(w.PROJECT, [SymbolProjectPath(self.root, ref, 1)])]))

    def flag(self, x, y, k):
        self.lib("power", "PWR_FLAG")
        ref = f"#FLG{k:02d}"
        self.syms.append(SchematicSymbol(
            libraryNickname="power", entryName="PWR_FLAG", position=Position(x, y, 0), unit=1,
            inBom=False, onBoard=False, uuid=self.uid("flag", k), mirror=None,
            properties=[w.prop("Reference", ref, x, y - 2.54, 0, hide=True),
                        w.prop("Value", "PWR_FLAG", x, y - 5.08, 1, hide=True),
                        w.prop("Footprint", "", x, y, 2, True)],
            pins={"1": self.uid("flagpin")},
            instances=[SymbolProjectInstance(w.PROJECT, [SymbolProjectPath(self.root, ref, 1)])]))

    def text(self, msg, x, y, size=1.8):
        self.texts.append(Text(msg, Position(x, y, 0),
                               w.Effects(font=w.Font(height=size, width=size),
                                         justify=w.Justify(horizontally="left")), self.uid("t")))

    def finish(self):
        for (lib, part), s in sorted(self.libs.items()):
            s.libId = f"{lib}:{part}"
            self.sch.libSymbols.append(s)
        self.sch.schematicSymbols = self.syms
        self.sch.labels = self.labels
        self.sch.noConnects = self.ncs
        self.sch.junctions = self.juncs
        self.sch.graphicalItems = self.wires
        self.sch.texts = self.texts
        self.sch.titleBlock = TitleBlock(
            title="ADR-0016 gate fragment (spike, version 3b)", date="2026-11-04", revision="spike",
            company="busy-light", comments={1: "Exploratory, not a product schematic (ADR-0012 Proposed)",
                                            2: "Generated by layout_sch.py; placeholders: U1, U5"})
        return self.sch


def build(netlist_text):
    comps, _nets = w.parse_netlist(netlist_text)
    s = Sheet([c for c in comps if not c["ref"].startswith("#")])
    for ref, (x, y, rot) in PLACE.items():
        s.place(ref, x, y, rot, TEXT.get(ref, DEFAULT_TEXT))
    P = s.pin

    # captions
    s.text("CC detection (ADR-0016): OUT1_N low = 1.5 A or more advertised", 38.1, 27.0)
    s.text("Gate: step enable = select AND CC OK AND hold-off done; step 2 also AND NOT step 3 enable (U13)", 128.27, 20.0)
    s.text("Current-limit switches (ADR-0010 option A): TMUX1101, step 3 = 27.4 k + 301 ohm", 183.0, 17.78)
    s.text("Hold-off after VBUS returns (HW-010: 200 to 600 ms; supervisor part not chosen)",
           38.1, 111.76)
    s.text("Rails come from the rest of the board", 172.72, 118.11)

    # CC detection IC, pull-up, inverter
    s.power("VBUS_IC", *P("U1", 1))
    s.power("GND", *P("U1", 2))
    o1 = P("U1", 3)
    s.wire(o1, P("U2", 2))
    s.label("CC_OUT1_N", *P("U2", 2), 180)   # same net feeds U13 (exclusive steps)
    s.power("VBUS_IC", *P("R1", 1))
    s.junction(*P("R1", 2))
    s.nc(*P("U1", 4))
    s.nc(*P("U1", 5))
    s.power("+3V3", *P("U2", 5))
    s.power("GND", *P("U2", 3))
    s.nc(*P("U2", 1))
    y2 = P("U2", 4)
    s.wire(y2, (y2[0] + 5.08, y2[1]))
    s.label("CC_OK_1A5", y2[0] + 5.08, y2[1])

    # AND gates, pull-downs, enable nets, TMUX1101 ILIM switches (owner decision 2026-11-05)
    for g, rsel, ren, sw, rpd, cap, sel, en in (("U3", "R4", "R2", "U14", "R18", "C24", "SEL_STEP2_GPIO",
                                                 "ILIM_STEP2_EN"),
                                                ("U4", "R5", "R3", "U15", "R19", "C25", "SEL_STEP3_GPIO",
                                                 "ILIM_STEP3_EN")):
        a, b, c, yo = P(g, 1), P(g, 3), P(g, 6), P(g, 4)
        okn = "CC_OK_1A5" if g == "U4" else "CC_OK_NOT_S3"   # step 2: CC OK AND NOT step 3 enable
        s.wire(a, (a[0] - 7.62, a[1]))
        s.label(okn, a[0] - 7.62, a[1], 180)
        s.wire(c, (c[0] - 7.62, c[1]))
        s.label("HOLD_OK", c[0] - 7.62, c[1], 180)
        bs = P(rsel, 1)
        s.wire(b, bs)
        s.label(sel, *bs, 180)
        s.power("GND", *P(rsel, 2))
        s.power("+3V3", *P(g, 5))
        s.power("GND", *P(g, 2))
        s.wire(yo, P(sw, 4))                      # gate output to SEL; R2 and the 100 kohm pull-down hang on it
        s.junction(*P(ren, 1))
        s.junction(*P(rpd, 1))
        s.label(en, yo[0] + 2.54, yo[1])
        s.power("GND", *P(ren, 2))
        s.power("GND", *P(rpd, 2))
        # switch supply with 0.1 uF, ground pins
        vdd = P(sw, 5)
        ty = P(cap, 1)[1]
        s.wire(vdd, (vdd[0], ty), P(cap, 1))
        s.junction(vdd[0], ty)
        s.power("+3V3", vdd[0], ty)
        s.power("GND", *P(cap, 2))
        s.power("GND", *P(sw, 3))
        s.wire(P(sw, 2), P(sw, 3))
    # step 2: switch - 56.2 k; step 3: switch - 301 ohm - 27.4 k
    for sw, chain in (("U14", ("R_ILIM2",)), ("U15", ("R_ILIM3B", "R_ILIM3"))):
        prev = P(sw, 1)
        for rl in chain:
            lo, hi = sorted((P(rl, 1), P(rl, 2)))
            s.wire(prev, lo)
            prev = hi
        s.wire(prev, (BUSX, prev[1]))
    # exclusive steps: U13 = NOR(CC_OUT1_N, ILIM_STEP3_EN) = CC OK AND NOT step 3 enable
    for pin, net, dx, ang in ((1, "CC_OUT1_N", -5.08, 180), (2, "ILIM_STEP3_EN", -5.08, 180),
                              (4, "CC_OK_NOT_S3", 5.08, 0)):
        x, y = P("U13", pin)
        s.wire((x, y), (x + dx, y))
        s.label(net, x + dx, y, ang)
    s.power("+3V3", *P("U13", 5))
    s.power("GND", *P("U13", 3))
    # ILIM bus: both switched resistors meet and leave to the current-limit part
    y2, y3 = P("R_ILIM2", 1)[1], P("R_ILIM3", 1)[1]
    s.wire((BUSX, y3), (BUSX, y2), (BUSX, y2 - 5.08))
    s.junction(BUSX, y2)
    s.label("ILIM", BUSX, y2 - 5.08, 90)

    # hold-off supervisor
    s.power("VBUS_IC", *P("U5", 2))
    s.power("GND", *P("U5", 3))
    s.nc(*P("U5", 4))
    rs = P("U5", 1)
    s.wire(rs, (101.6, rs[1]))
    s.junction(*P("R6", 2))
    s.power("VBUS_IC", *P("R6", 1))
    s.label("HOLD_OK", 101.6, rs[1])
    ct = P("U5", 5)
    s.wire(ct, P("C1", 1))
    for a_, b_ in (("C1", "C1B"), ("C1B", "C1C"), ("C1C", "C1D")):   # parallel C0G set, one rail wire
        s.wire(P(a_, 1), P(b_, 1))
    for r_ in ("C1", "C1B", "C1C"):
        s.junction(*P(r_, 1))
    s.label("SUP_CT", 68.58, ct[1])
    for r_ in ("C1", "C1B", "C1C", "C1D"):
        s.power("GND", *P(r_, 2))

    # rails (power flags, as in the SKiDL fragment)
    for k, (net, x, y) in enumerate((("VBUS_IC", 180.34, 127.0), ("+3V3", 180.34, 139.7),
                                      ("GND", 180.34, 152.4)), 1):
        s.power(net, x, y)
        s.wire((x, y), (x + 10.16, y))
        s.flag(x + 10.16, y, k)
    return s.finish()


def write(netlist_path, out_path):
    with open(netlist_path, encoding="utf-8") as f:
        build(f.read()).to_file(out_path)
    lib_tables.write_schematic_project(out_path)


if __name__ == "__main__":
    write(sys.argv[1], sys.argv[2])
