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



def keepout_ring(board, cx, cy, r_in, r_out, name):
    """Copper keep-out rule area (annulus): tracks, vias and pads forbidden; passes to the router through the DSN."""
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(True)
    z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(pcbnew.LSET.AllCuMask())
    z.SetZoneName(name)
    ol = z.Outline()
    ol.NewOutline()
    n = 72
    for k in range(n):
        a = 2 * math.pi * k / n
        ol.Append(FromMM(cx + r_out * math.cos(a)), FromMM(cy + r_out * math.sin(a)))
    hole = pcbnew.SHAPE_LINE_CHAIN()
    for k in range(n):
        a = 2 * math.pi * k / n
        hole.Append(FromMM(cx + r_in * math.cos(a)), FromMM(cy + r_in * math.sin(a)))
    hole.SetClosed(True)
    ol.AddHole(hole, 0)
    board.Add(z)


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
    keepout_ring(b, cx, cy, P["mounting"]["hole_diameter_mm"] / 2, P["mounting"]["hole_diameter_mm"] / 2 + P["rules"]["edge_keepout_mm"], f"keepout_peg_{az:g}")
keepout_ring(b, 0, 0, P["board"]["outline_diameter_mm"] / 2 - P["rules"]["edge_keepout_mm"], P["board"]["outline_diameter_mm"] / 2 + 1.0, "keepout_edge")
n_led, radius = P["ring"]["led_count"], P["ring"]["radius_mm"]
fps, k = {}, 0
for c in comps:
    lib, name = find(c, "footprint")[0][1].split(":")
    fp = pcbnew.FootprintLoad(f"/usr/share/kicad/footprints/{lib}.pretty", name)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    fields = {x[1][1]: (x[2] if len(x) > 2 else "") for fl in find(c, "fields") for x in find(fl, "field")}
    if fields.get("HW_REQ"):
        fp.SetField("HW_REQ", fields["HW_REQ"])
        fp.GetField("HW_REQ").SetVisible(False)
    fp.SetReference(ref(c))
    fp.SetValue(find(c, "value")[0][1])
    if ref(c).startswith("D"):
        deg = P["ring"]["phase_deg"] + 360 * k / n_led
        a = math.radians(deg)
        fp.SetPosition(VECTOR2I(FromMM(radius * math.cos(a)), FromMM(-radius * math.sin(a))))
        fp.SetOrientationDegrees(deg - 90)
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

# Explicit two-layer stackup so that the board is 1.6 mm thick (the KiCad default sums to 1.51 mm; spike finding).
text = Path(out).read_text()
cu = P["stackup"]["copper_thickness_mm"]
core = P["stackup"]["pcb_thickness_mm"] - 2 * cu
stackup = (
    "\t\t(stackup\n"
    f'\t\t\t(layer "F.Cu" (type "copper") (thickness {cu}))\n'
    f'\t\t\t(layer "dielectric 1" (type "core") (thickness {core:.3f}) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))\n'
    f'\t\t\t(layer "B.Cu" (type "copper") (thickness {cu}))\n'
    '\t\t\t(copper_finish "None")\n\t\t\t(dielectric_constraints no)\n\t\t)\n'
)
marker = "\t(setup\n"
assert marker in text and "(stackup" not in text
Path(out).write_text(text.replace(marker, marker + stackup, 1))

