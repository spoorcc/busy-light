"""Spike: build the board file with kiutils (no pcbnew), KiCad 8 syntax. Same inputs as gen_pcb.py."""
import copy
import math
import sys
import tomllib
import uuid
from pathlib import Path

from kiutils.board import Board
from kiutils.footprint import Footprint
from kiutils.items.fpitems import FpText
from kiutils.items.common import Effects, Font
from kiutils.items.common import Net, Position, Stroke
from kiutils.items.gritems import GrCircle
from kiutils.items.brditems import StackupLayer, Stackup
from kiutils.items.zones import Zone, ZonePolygon, KeepoutSettings, Hatch
from sexpr import find, parse

NS = uuid.UUID("7026fcc6-e1a0-409e-aaf4-6a17ea82654f")


def u(*k) -> str:
    return str(uuid.uuid5(NS, "/".join(map(str, k))))


net_file, out = sys.argv[1], sys.argv[2]
P = tomllib.loads((Path(__file__).parent / "params.toml").read_text())
tree = parse(Path(net_file).read_text())
comps = find(find(tree, "components")[0], "comp")
nets = find(find(tree, "nets")[0], "net")


def ref(c):
    return find(c, "ref")[0][1]


def natural(c):
    r = ref(c)
    return (r.rstrip("0123456789"), int(r[len(r.rstrip("0123456789")):] or 0))


comps = sorted((c for c in comps if not ref(c).startswith("#")), key=natural)
b = Board.create_new()
b.version = 20240108
b.generator = "busy-light-gen"
b.general.thickness = P["stackup"]["pcb_thickness_mm"]
cu = P["stackup"]["copper_thickness_mm"]
b.setup.stackup = Stackup(
    layers=[
        StackupLayer(name="F.Cu", type="copper", thickness=cu),
        StackupLayer(name="dielectric 1", type="core", thickness=round(P["stackup"]["pcb_thickness_mm"] - 2 * cu, 3), material="FR4", epsilonR=4.5, lossTangent=0.02),
        StackupLayer(name="B.Cu", type="copper", thickness=cu),
    ],
    copperFinish="None",
    dielectricContraints="no",
)
b.nets = [Net(number=0, name="")]
netno = {}
for i, n in enumerate(nets, 1):
    name = find(n, "name")[0][1]
    netno[name] = i
    b.nets.append(Net(number=i, name=name))
pin_net = {}
for n in nets:
    for node in find(n, "node"):
        pin_net[(find(node, "ref")[0][1], find(node, "pin")[0][1])] = find(n, "name")[0][1]


def circle(cx, cy, r, key):
    return GrCircle(center=Position(round(cx, 4), round(cy, 4)), end=Position(round(cx + r, 4), round(cy)),
                    layer="Edge.Cuts", width=0.1, tstamp=u(key))


b.graphicItems.append(circle(0, 0, P["board"]["outline_diameter_mm"] / 2, "outline"))
for az in P["mounting"]["peg_azimuths_deg"]:
    cx = P["mounting"]["peg_radius_mm"] * math.cos(math.radians(az))
    cy = -P["mounting"]["peg_radius_mm"] * math.sin(math.radians(az))
    b.graphicItems.append(circle(cx, cy, P["mounting"]["hole_diameter_mm"] / 2, f"hole{az}"))


def ring_zone(cx, cy, r_in, r_out, name):
    n = 72
    outer = [Position(round(cx + r_out * math.cos(2 * math.pi * k / n), 4), round(cy + r_out * math.sin(2 * math.pi * k / n), 4)) for k in range(n)]
    inner = [Position(round(cx + r_in * math.cos(2 * math.pi * k / n), 4), round(cy + r_in * math.sin(2 * math.pi * k / n), 4)) for k in range(n)]
    # one outline with a slit: outer ring then inner ring in reverse, joined at angle 0
    pts = outer + [outer[0]] + list(reversed(inner)) + [inner[0], outer[0]]
    z = Zone(layers=["F.Cu", "B.Cu"], name=name, tstamp=u("zone", name), hatch=Hatch(style="edge", pitch=0.5),
             keepoutSettings=KeepoutSettings(tracks="not_allowed", vias="not_allowed", pads="not_allowed", copperpour="not_allowed", footprints="allowed"),
             polygons=[ZonePolygon(coordinates=pts)])
    return z


k = 0
n_led, radius = P["ring"]["led_count"], P["ring"]["radius_mm"]
for c in comps:
    lib, name = find(c, "footprint")[0][1].split(":")
    fp = Footprint.from_file(f"/usr/share/kicad/footprints/{lib}.pretty/{name}.kicad_mod")
    fp.libraryNickname = lib
    fp.entryName = name
    fp.tstamp = u(ref(c))
    fp.path = f"/{u(ref(c))}"
    if ref(c).startswith("D"):
        deg = P["ring"]["phase_deg"] + 360 * k / n_led
        a = math.radians(deg)
        fp.position = Position(round(radius * math.cos(a), 4), round(-radius * math.sin(a), 4), (deg - 90) % 360)
        k += 1
    else:
        fp.position = Position(-6 if ref(c).startswith("U") else 0, 0, 0)
    # KiCad 8 syntax: reference and value are fp_text items; kiutils drops position and layer of `property` entries.
    fp.properties.pop("Reference", None)
    fp.properties.pop("Value", None)
    fp.graphicItems = [g for g in fp.graphicItems if not (isinstance(g, FpText) and g.type in ("reference", "value"))]
    fp.graphicItems.append(FpText(type="reference", text=ref(c), position=Position(0, -2.2, 0), layer="F.Fab", effects=Effects(font=Font(height=0.8, width=0.8, thickness=0.12)), tstamp=u(ref(c), "ref")))
    fp.graphicItems.append(FpText(type="value", text=find(c, "value")[0][1], position=Position(0, 2.2, 0), layer="F.Fab", hide=True, effects=Effects(font=Font(height=0.8, width=0.8, thickness=0.12)), tstamp=u(ref(c), "val")))
    fields = {x[1][1]: (x[2] if len(x) > 2 else "") for fl in find(c, "fields") for x in find(fl, "field")}
    if fields.get("HW_REQ"):
        fp.properties["HW_REQ"] = fields["HW_REQ"]
    ang = fp.position.angle or 0
    for pad in fp.pads:
        pad.position = Position(pad.position.X, pad.position.Y, ((pad.position.angle or 0) + ang) % 360)  # file format: pad angle is absolute
        nm = pin_net.get((ref(c), pad.number))
        if nm:
            pad.net = Net(number=netno[nm], name=nm)
    for t in fp.graphicItems:
        if hasattr(t, 'position') and hasattr(t, 'text'):
            t.position = Position(t.position.X, t.position.Y, ((t.position.angle or 0) + ang) % 360)
    b.footprints.append(fp)
e = P["rules"]["edge_keepout_mm"]
b.zones.append(ring_zone(0, 0, P["board"]["outline_diameter_mm"] / 2 - e, P["board"]["outline_diameter_mm"] / 2 + 1.0, "keepout_edge"))
for az in P["mounting"]["peg_azimuths_deg"]:
    cx = P["mounting"]["peg_radius_mm"] * math.cos(math.radians(az))
    cy = -P["mounting"]["peg_radius_mm"] * math.sin(math.radians(az))
    b.zones.append(ring_zone(cx, cy, P["mounting"]["hole_diameter_mm"] / 2, P["mounting"]["hole_diameter_mm"] / 2 + e, f"keepout_peg_{az:g}"))
b.to_file(out)
print("board written", len(b.footprints), "footprints")
