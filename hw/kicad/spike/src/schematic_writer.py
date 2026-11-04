"""Spike: deterministic KiCad 10 schematic writer (kiutils). Parts and nets from a plain Python description."""
import copy, uuid
from kiutils.schematic import Schematic
from kiutils.items.schitems import SchematicSymbol, LocalLabel, SymbolProjectInstance, SymbolProjectPath
from kiutils.items.common import Position, Property, Effects, Font
from kiutils.symbol import SymbolLib
NS = uuid.UUID("7026fcc6-e1a0-409e-aaf4-6a17ea82654f")
def u(*k): return str(uuid.uuid5(NS, "/".join(map(str, k))))
SYM = "/usr/share/kicad/symbols"
_libs = {}
def libsym(lib, name):
    if lib not in _libs: _libs[lib] = SymbolLib.from_file(f"{SYM}/{lib}.kicad_sym")
    s = next(x for x in _libs[lib].symbols if x.entryName == name)
    if s.extends:  # flatten a derived symbol: parent graphics and pins, child properties
        parent = next(x for x in _libs[lib].symbols if x.entryName == s.extends)
        flat = copy.deepcopy(parent); flat.extends = None
        for un in flat.units: un.entryName = un.entryName.replace(parent.entryName, s.entryName, 1)
        flat.entryName = s.entryName
        by = {p.key: p for p in flat.properties}
        for p in s.properties: by[p.key] = copy.deepcopy(p)
        flat.properties = list(by.values())
        return flat
    return s
def build(parts, out, title):
    """parts: list of dict(ref, lib, sym, value, footprint, nets{pin_name_or_num: net}, at=(x,y))"""
    sch = Schematic.create_new(); sch.version = 20231120; sch.generator = "busy-light-gen"; sch.generator_version = "0"
    sch.uuid = u("sheet"); sch.paper.paperSize = "A3"; from kiutils.items.common import TitleBlock; sch.titleBlock = TitleBlock(title=title)
    done = set()
    for p in parts:
        ls = libsym(p["lib"], p["sym"])
        if (p["lib"], p["sym"]) not in done:
            c = copy.deepcopy(ls); c.libraryNickname = p["lib"]; sch.libSymbols.append(c); done.add((p["lib"], p["sym"]))
        x, y = p["at"]
        ss = SchematicSymbol(libraryNickname=p["lib"], entryName=p["sym"], position=Position(x, y, 0), unit=1, inBom=not p.get("power"), onBoard=not p.get("power"), uuid=u(p["ref"]))
        ss.properties = [Property(k, v, id=i, position=Position(x, y + 5 + 2 * i, 0), effects=Effects(font=Font(height=1.27, width=1.27), hide=(k in ("Footprint", "HW_REQ"))))
                         for i, (k, v) in enumerate([("Reference", p["ref"]), ("Value", p["value"]), ("Footprint", p["footprint"]), ("HW_REQ", p.get("req", ""))])]
        ss.pins = {}
        ss.instances = [SymbolProjectInstance(name="busy_light", paths=[SymbolProjectPath(sheetInstancePath="/" + sch.uuid, reference=p["ref"], unit=1)])]
        sch.schematicSymbols.append(ss)
        pins = [pin for unit in ls.units for pin in unit.pins]
        for pin in pins:
            key = pin.name if pin.name in p["nets"] else pin.number
            if key not in p["nets"]: continue
            px, py = pin.position.X, pin.position.Y
            ang = {0: 180, 90: 270, 180: 0, 270: 90}[int(pin.position.angle or 0)]
            sch.labels.append(LocalLabel(text=p["nets"][key], position=Position(round(x + px, 4), round(y - py, 4), ang),
                                         effects=Effects(font=Font(height=1.27, width=1.27)), uuid=u(p["ref"], "lbl", pin.number)))
    sch.to_file(out)
