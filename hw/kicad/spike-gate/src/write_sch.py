# SPDX-License-Identifier: Apache-2.0
"""Spike: deterministic KiCad schematic writer (ADR-0012).

Reads a KiCad s-expression netlist (the SKiDL generate_netlist output, gate.net) and writes
gate.kicad_sch: one part per grid cell, every pin gets a short wire stub that ends in a net label
(or a power symbol for rails, or a no-connect marker). No routing. Same input gives the same bytes:
no random numbers, no clock, UUIDs are uuid5 of a stable key.

Usage: write_sch.py <gate.net> <output.kicad_sch>
Limits: single-unit symbols only; symbols from the KiCad system library; one sheet.
Traces to ADR-0012 (own writer instead of the SKiDL schematic router).
"""
import copy
import math
import os
import re
import sys
import uuid
from functools import lru_cache

from kiutils.items.common import Effects, Font, Justify, Position, Property, Stroke
from kiutils.items.schitems import (Connection, LocalLabel, NoConnect, SchematicSymbol,
                                    SymbolProjectInstance, SymbolProjectPath)
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib

SYMDIR = os.environ.get("KICAD_SYMBOL_DIR", "/usr/share/kicad/symbols")
NS = uuid.UUID("5d0b6f64-0a1c-5c52-9c2e-2f0f8a5b7e11")  # fixed namespace for uuid5
PROJECT = "gate"
STUB = 5.08            # wire stub length, mm
CELL_W, CELL_H = 88.9, 50.8
COLS = 5
ORIGIN = (25.4, 25.4)
RAIL_SYMBOLS = {"GND": "GND", "+3V3": "+3V3"}  # other rails: +5V symbol, value set to the net name
DEFAULT_RAIL_SYMBOL = "+5V"


def uid(key: str) -> str:
    return str(uuid.uuid5(NS, key))


def r(v: float) -> float:
    return round(v, 4)


def parse_netlist(text: str):
    """Return (components, nets): components = list of dicts, nets = {name: [(ref, pin)]}."""
    comps = []
    head, _, nets_txt = text.partition("\n  (nets")
    for blk in re.split(r"\n    \(comp\b", head)[1:]:
        ref = re.search(r'\(ref "([^"]+)"\)', blk).group(1)
        value = re.search(r'\(value "([^"]*)"\)', blk).group(1)
        fp = re.search(r'\(footprint "([^"]*)"\)', blk)
        lib = re.search(r'\(libsource\s*\(lib "([^"]+)"\)\s*\(part "([^"]+)"\)', blk)
        comps.append({"ref": ref, "value": value, "footprint": fp.group(1) if fp else "",
                      "lib": lib.group(1), "part": lib.group(2)})
    nets = {}
    for blk in re.split(r"\n    \(net\b", nets_txt)[1:]:
        name = re.search(r'\(name "([^"]*)"\)', blk).group(1)
        nets[name] = re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', blk)
    return comps, nets


@lru_cache(maxsize=None)
def _lib(lib: str) -> SymbolLib:
    return SymbolLib.from_file(os.path.join(SYMDIR, lib + ".kicad_sym"))


def load_symbol(lib: str, part: str):
    """Library symbol flattened (extends resolved) and named lib:part for lib_symbols."""
    syms = {s.entryName: s for s in _lib(lib).symbols}
    sym = syms[part]
    if sym.extends:
        parent = copy.deepcopy(syms[sym.extends])
        parent.properties = copy.deepcopy(sym.properties)
        parent.entryName = part
        for u in parent.units:  # unit names carry the entry name
            u.entryName = part
        parent.extends = None
        sym = parent
    sym = copy.deepcopy(sym)
    sym.libraryNickname = lib
    return sym


def sym_pins(sym):
    """Pins of unit 1 (and common unit 0), body style 0/1: list of (number, x, y, angle, type)."""
    out = []
    for u in sym.units:
        if u.unitId in (0, 1) and u.styleId in (0, 1):
            for p in u.pins:
                out.append((p.number, p.position.X, p.position.Y, p.position.angle or 0,
                            p.electricalType))
    return sorted(out, key=lambda t: (len(t[0]), t[0]))


def natural(ref: str):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", ref)]


def transform(x, y, rot):
    """Library (y up) to relative schematic (y down) with CCW rotation rot degrees."""
    c, s = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
    return r(x * c - y * s), r(-(x * s + y * c))


def outward(angle, rot):
    """Unit vector (schematic coords) pointing away from the body at a pin with lib angle."""
    dx, dy = -round(math.cos(math.radians(angle))), -round(math.sin(math.radians(angle)))
    return transform(dx, dy, rot)


def eff(justify=None, hide=False, size=1.27):
    return Effects(font=Font(height=size, width=size), justify=justify or Justify(), hide=hide)


def prop(key, value, x, y, idx, hide=False, just=None, ang=0):
    return Property(key=key, value=value, id=idx, position=Position(x, y, ang),
                    effects=eff(Justify(horizontally=just) if just else None, hide))


def build(netlist_text: str) -> Schematic:
    comps, nets = parse_netlist(netlist_text)
    pin_net = {}
    for name, pins in nets.items():
        for ref, pin in pins:
            pin_net[(ref, pin)] = name
    net_size = {n: len(p) for n, p in nets.items()}
    rails = {n for n, pins in nets.items() if any(c[0].startswith("#FLG") for c in pins)}

    sch = Schematic.create_new()
    sch.version = 20231120
    sch.generator = "busy-light-write_sch"
    sch.uuid = uid("root")
    sch.paper.paperSize = "A2"
    root_path = "/" + sch.uuid
    sch.sheetInstances = []
    placed = {}  # (lib, part) -> library symbol
    items_sym, items_conn, items_lbl, items_nc = [], [], [], []
    pwr_n = [0]

    def lib_for(lib, part):
        if (lib, part) not in placed:
            placed[(lib, part)] = load_symbol(lib, part)
        return placed[(lib, part)]

    def add_power(net, x, y):
        """Power symbol whose pin sits at (x, y)."""
        pwr_n[0] += 1
        part = RAIL_SYMBOLS.get(net, DEFAULT_RAIL_SYMBOL)
        lib_for("power", part)
        ref = f"#PWR{pwr_n[0]:02d}"
        s = SchematicSymbol(libraryNickname="power", entryName=part,
                            position=Position(x, y, 0), unit=1, inBom=False, onBoard=False,
                            uuid=uid("sym" + ref), mirror=None,
                            properties=[prop("Reference", ref, x, y - 2.54, 0, hide=True),
                                        prop("Value", net, x, y + (3.81 if part == "GND" else -3.81),
                                             1)],
                            pins={"1": uid("pin" + ref)},
                            instances=[SymbolProjectInstance(PROJECT, [SymbolProjectPath(
                                root_path, ref, 1)])])
        items_sym.append(s)

    # cell order: natural order of the reference, flags last
    order = sorted(comps, key=lambda c: (c["ref"].startswith("#"), natural(c["ref"])))
    for i, comp in enumerate(order):
        ref, lib, part = comp["ref"], comp["lib"], comp["part"]
        sref = ref if not ref.startswith("#") else f"#FLG{i:02d}"
        sym = lib_for(lib, part)
        pins = sym_pins(sym)
        axes = {p[3] % 180 for p in pins}
        rot = 90 if axes == {90} else 0   # vertical two-pin parts lie down so labels run sideways
        cx = ORIGIN[0] + (i % COLS) * CELL_W + CELL_W / 2
        cy = ORIGIN[1] + (i // COLS) * CELL_H + CELL_H / 2
        cx, cy = r(round(cx / 1.27) * 1.27), r(round(cy / 1.27) * 1.27)
        hide_ref = ref.startswith("#")
        items_sym.append(SchematicSymbol(
            libraryNickname=lib, entryName=part, position=Position(cx, cy, rot), unit=1,
            inBom=not hide_ref, onBoard=not hide_ref, uuid=uid("sym" + ref),
            properties=[prop("Reference", sref, cx, r(cy - CELL_H / 2 + 2.54), 0, hide_ref, "left", -rot % 360),
                        prop("Value", comp["value"], cx, r(cy - CELL_H / 2 + 5.08), 1, False, "left", -rot % 360),
                        prop("Footprint", comp["footprint"], cx, cy, 2, True),
                        prop("Datasheet", "", cx, cy, 3, True)],
            pins={p[0]: uid(f"pin{ref}.{p[0]}") for p in pins},
            instances=[SymbolProjectInstance(PROJECT, [SymbolProjectPath(root_path, sref, 1)])]))
        for number, lx, ly, ang, _etype in pins:
            ox, oy = transform(lx, ly, rot)
            px, py = r(cx + ox), r(cy + oy)
            net = pin_net.get((ref, number))
            if net is None or (net not in rails and net_size[net] < 2):
                items_nc.append(NoConnect(Position(px, py), uid(f"nc{ref}.{number}")))
                continue
            dx, dy = outward(ang, rot)
            ex, ey = r(px + dx * STUB), r(py + dy * STUB)
            items_conn.append(Connection(
                type="wire", points=[Position(px, py), Position(ex, ey)],
                stroke=Stroke(0, "default"), uuid=uid(f"w{ref}.{number}")))
            if net in rails:
                add_power(net, ex, ey)
            else:
                lang = {(1, 0): 0, (0, -1): 90, (-1, 0): 180, (0, 1): 270}[(dx, dy)]
                just = Justify(horizontally="left" if lang in (0, 90) else "right")
                items_lbl.append(LocalLabel(net, Position(ex, ey, lang),
                                            eff(just), uid(f"l{ref}.{number}")))

    for (lib, part), s in sorted(placed.items()):
        s.libId = f"{lib}:{part}"
        sch.libSymbols.append(s)
    sch.schematicSymbols = items_sym
    sch.labels = items_lbl
    sch.noConnects = items_nc
    sch.junctions = []
    sch.graphicalItems = items_conn
    return sch


def write(netlist_path: str, out_path: str) -> None:
    with open(netlist_path, encoding="utf-8") as f:
        sch = build(f.read())
    sch.to_file(out_path)


if __name__ == "__main__":
    write(sys.argv[1], sys.argv[2])
