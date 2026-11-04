"""Spike: build a board from the KiCad netlist and params.toml with pcbnew."""
import math
import sys
import tomllib
from pathlib import Path

import pcbnew
from pcbnew import VECTOR2I, FromMM
from sexpr import find, parse

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
b = pcbnew.CreateEmptyBoard()
ec = pcbnew.PCB_SHAPE(b)
ec.SetShape(pcbnew.SHAPE_T_CIRCLE)
ec.SetLayer(pcbnew.Edge_Cuts)
ec.SetCenter(VECTOR2I(0, 0))
ec.SetEnd(VECTOR2I(FromMM(P["board"]["outline_diameter_mm"] / 2), 0))
ec.SetWidth(FromMM(0.1))
b.Add(ec)
b.GetDesignSettings().SetBoardThickness(FromMM(P["stackup"]["pcb_thickness_mm"]))
for az in P["mounting"]["peg_azimuths_deg"]:
    h = pcbnew.PCB_SHAPE(b)
    h.SetShape(pcbnew.SHAPE_T_CIRCLE)
    h.SetLayer(pcbnew.Edge_Cuts)
    cx = P["mounting"]["peg_radius_mm"] * math.cos(math.radians(az))
    cy = -P["mounting"]["peg_radius_mm"] * math.sin(math.radians(az))
    h.SetCenter(VECTOR2I(FromMM(cx), FromMM(cy)))
    h.SetEnd(VECTOR2I(FromMM(cx + P["mounting"]["hole_diameter_mm"] / 2), FromMM(cy)))
    h.SetWidth(FromMM(0.1))
    b.Add(h)
n_led, radius = P["ring"]["led_count"], P["ring"]["radius_mm"]
fps, k = {}, 0
for c in comps:
    lib, name = find(c, "footprint")[0][1].split(":")
    fp = pcbnew.FootprintLoad(f"/usr/share/kicad/footprints/{lib}.pretty", name)
    fp.SetReference(ref(c))
    fp.SetValue(find(c, "value")[0][1])
    if ref(c).startswith("D"):
        deg = 90 - 360 * k / n_led
        a = math.radians(deg)
        fp.SetPosition(VECTOR2I(FromMM(radius * math.cos(a)), FromMM(-radius * math.sin(a))))
        fp.SetOrientationDegrees(-deg + 90)
        k += 1
    else:
        fp.SetPosition(VECTOR2I(FromMM(-6 if ref(c).startswith("U") else 0), 0))
    b.Add(fp)
    fps[ref(c)] = fp
for n in nets:
    ni = pcbnew.NETINFO_ITEM(b, find(n, "name")[0][1])
    b.Add(ni)
    for node in find(n, "node"):
        r = find(node, "ref")[0][1]
        if r in fps:
            fps[r].FindPadByNumber(find(node, "pin")[0][1]).SetNet(ni)
b.Save(out)
print("pcb saved", len(fps), "footprints")
