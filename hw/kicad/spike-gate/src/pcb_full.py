# SPDX-License-Identifier: Apache-2.0
"""Spike: generate a placed (not routed) PCB of the full board from the schematic netlist.

Exploratory, not a product design (ADR-0012 is Proposed; mechanics, LED count and peg azimuth are open,
so the outline and the LED field are provisional). The board file is written only by this script
(KiCad pcbnew Python API); it is never edited by hand.

Usage: python3 pcb_full.py <netlist.net> <out dir> [name]
  writes <out dir>/<name>.kicad_pcb (default name busy_light_spike) and <name>.kicad_pro

The netlist comes from `kicad-cli sch export netlist` on the output of run_full.sh, so every ref, value
and net is the schematic's. Where the schematic names a footprint that the system KiCad libraries do not
have, or a pin name that is not a pad number, the tables below say what was substituted (all PROVISIONAL).
"""
import json
import os
import re
import sys
import uuid

import pcbnew

FP_ROOT = os.environ.get("KICAD_FOOTPRINT_DIR", "/usr/share/kicad/footprints/")

# ----------------------------------------------------------------------------- board parameters
BOARD_W, BOARD_H = 136.0, 64.0          # provisional: electronics zone x < 64, LED field x >= 64
CLEARANCE = 0.15                          # mm, default net class (J1 pad gap is 0.15 mm)
TRACK = 0.2                               # mm, default signal width
VIA_DIA, VIA_DRILL = 0.6, 0.3             # mm
EDGE_CLEARANCE = 0.3                      # mm
# Net classes by net name: width in mm. IPC-2221 external layer, 1 oz (35 um), 10 K rise:
# 1.5 A -> 0.53 mm, 2.0 A -> 0.78 mm (see report). The power nets are routed at 0.8 mm where space allows.
from pcb_rules import NET_WIDTH   # noqa: E402  (shared with the tests; values and basis in pcb_rules.py)
GND = "GND"
# Signal nets that touch the 0.4 mm-pitch pads of U1 use the minimum width (0.15 mm).
NET_TRACK = {"/CC1": 0.15, "/CC2": 0.15}
# Star nets: every pad is routed straight to the named pad, so the branch point is at that pad.
# ADR-0016 layout rule: the Q3 gate pin is the tap point of U13 pin 2, R3 and the readback R15.
STAR = {"/ILIM_STEP3_EN": ("Q3", "1")}

# ----------------------------------------------------------------------------- provisional substitutions
# ref -> footprint (lib:name) used instead of the schematic's footprint field
FOOTPRINT_OVERRIDE = {
    "U1": "CUSTOM:X2QFN-12_RWB",                      # Package_X2QFN does not exist in the system libraries
    "U8": "Package_TO_SOT_SMD:SOT-223-3_TabPin2",     # schematic field empty (REG_3V3 placeholder)
    "U9": "RF_Module:ESP32-C6-MINI-1",                # ESP32-C3-MINI-1 not in the libraries; same 13.2x16.6 module family
    "C1": "Capacitor_SMD:C_1206_3216Metric",          # 470 nF C0G, N4 addendum
    "C1B": "Capacitor_SMD:C_1206_3216Metric",         # 150 nF C0G, N4 addendum
    "C3": "Capacitor_SMD:C_0805_2012Metric",          # 10 uF tbd
    "C4": "Capacitor_SMD:C_1206_3216Metric",          # bulk tbd
}
# schematic pin name -> pad number, where the schematic box symbol uses names (datasheet pin tables)
PADMAP = {
    "U1": {"CC1": "1", "CC2": "2", "PORT": "4", "VBUS_DET": "5", "GND": "10", "VDD": "12"},   # TUSB321 SLLSEZ? pin table
    "U8": {"GND": "1", "OUT": "2", "IN": "3"},                                                  # PROVISIONAL (AMS1117-style)
    "U9": {"GPIO0": "12", "GPIO1": "13", "GPIO2": "5", "GPIO3": "6", "GPIO4": "18", "GPIO5": "19",
           "GPIO6": "20", "GPIO7": "21", "GPIO8": "22", "GPIO9": "23", "GPIO10": "16",
           "GPIO18": "26", "GPIO19": "27", "GPIO20": "30", "GPIO21": "31", "3V3": "3", "EN": "8",
           "GND": ("1", "2", "11", "14", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46",
                   "47", "48", "49", "50", "51", "52", "53")},   # ESP32-C3-MINI-1 datasheet v2.2 table 3-1
}

# ----------------------------------------------------------------------------- placement (mm, rotation deg)
# x right, y down, origin top-left of the board. Rule: USB-C at the left edge, power path left to right
# along the lower half, CC IC beside J1, gate cluster in the middle, hold-off capacitors at U5, ILIM resistors
# beside U7, module antenna at the top edge (its keep-out must stay free), LED field right.
PLACE = {
    "J1": None,   # placed by rule (mating face at the left edge)
    "TVS1": (14.0, 22.0, 90), "U6": (14.0, 40.5, 0),
    "U1": (19.0, 31.0, 0), "R_VD": (23.5, 26.0, 0), "R1": (23.5, 36.0, 0),
    "U2": (30.0, 26.0, 0), "U12": (30.0, 34.0, 0), "U13": (36.5, 26.0, 0), "R7": (33.0, 30.0, 0),
    "U3": (42.0, 26.0, 0), "U4": (42.0, 34.0, 0), "R4": (37.0, 30.0, 0), "R5": (37.0, 38.0, 0),
    "R2": (40.0, 37.8, 0), "R3": (53.0, 36.0, 0), "R14": (47.0, 26.0, 0), "R15": (47.0, 34.0, 0),
    "R16": (52.0, 26.0, 0), "R17": (52.0, 30.0, 0),
    "Q2": (44.0, 40.0, 0), "Q3": (49.0, 40.0, 0),
    "R_ILIM2": (44.0, 44.5, 0), "R_ILIM3": (49.0, 44.5, 0),
    "U5": (21.0, 47.0, 0), "R6": (26.0, 44.0, 0), "C1": (22.0, 53.0, 0), "C1B": (28.5, 53.0, 0),
    "U7": (37.0, 50.5, 0), "R_ILIM1": (42.0, 48.5, 0), "C2": (33.0, 55.5, 0), "C3": (42.0, 55.5, 0), "R8": (42.5, 52.5, 0),
    "U8": (53.0, 52.0, 0), "C5": (47.0, 58.5, 0), "C6": (59.0, 58.5, 0), "C4": (59.0, 44.0, 0),
    "U9": (31.0, 11.3, 0),
    "C7": (22.0, 9.0, 0), "R9": (22.0, 12.5, 0), "SW1": (13.5, 11.0, 0), "R12": (13.5, 16.0, 0), "R13": (17.5, 16.0, 0),
    "TVS2": (44.5, 10.0, 0), "U10": (55.0, 14.0, 0), "U11": (60.0, 30.0, 0), "R10": (60.0, 34.0, 0), "R11": (55.0, 18.0, 0),
}
LED_X0, LED_DX = 69.0, 8.5
LED_ROW_Y = (18.0, 46.0)
TP_Y = 61.0


# ----------------------------------------------------------------------------- netlist parsing
def parse_sexpr(text):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack = [[]]
    for t in toks:
        if t == "(":
            stack.append([])
        elif t == ")":
            x = stack.pop()
            stack[-1].append(x)
        else:
            stack[-1].append(t[1:-1].replace('\\"', '"') if t[0] == '"' else t)
    return stack[0][0]


def _find(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def read_netlist(path):
    """Return (comps, nets): comps {ref: (value, footprint, symbol uuid)}, nets {name: [(ref, pin)]} in file order."""
    with open(path, encoding="utf-8") as f:
        root = parse_sexpr(f.read())
    comps = {}
    for c in _find(_find(root, "components")[0], "comp"):
        ref = _find(c, "ref")[0][1]
        value = _find(c, "value")[0][1] if _find(c, "value") else ""
        fp = _find(c, "footprint")[0][1] if _find(c, "footprint") else ""
        ts = _find(c, "tstamps")
        comps[ref] = (value, fp, ts[0][1] if ts else "")
    nets = {}
    for n in _find(_find(root, "nets")[0], "net"):
        name = _find(n, "name")[0][1]
        nets[name] = [(_find(nd, "ref")[0][1], _find(nd, "pin")[0][1]) for nd in _find(n, "node")]
    return comps, nets


def short_net(name):
    """Net name used on the board: the schematic's own name (root-sheet slash kept, so parity matches)."""
    return name


# ----------------------------------------------------------------------------- footprint helpers
mm = pcbnew.FromMM


def vec(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def x2qfn12_rwb():
    """TUSB321 RWB (X2QFN-12, 1.6 x 1.6 mm). PROVISIONAL land pattern read from a text extract of the TI
    drawing RWB0012A (pads 0.2 wide; 8 side pads at 0.5 pitch, 4 end pads at 0.4 pitch). Verify against the
    drawing before any use: the system KiCad libraries have no X2QFN footprint."""
    fp = pcbnew.FOOTPRINT(None)
    pads = {}
    pads["1"] = (0.2, -0.7, 0.2, 0.4)
    pads["2"] = (-0.2, -0.7, 0.2, 0.4)
    for i, y in enumerate((-0.75, -0.25, 0.25, 0.75)):
        pads[str(3 + i)] = (-0.65, y, 0.4, 0.2)
    pads["7"] = (-0.2, 0.7, 0.2, 0.4)
    pads["8"] = (0.2, 0.7, 0.2, 0.4)
    for i, y in enumerate((0.75, 0.25, -0.25, -0.75)):
        pads[str(9 + i)] = (0.65, y, 0.4, 0.2)
    for num, (x, y, w, h) in pads.items():
        p = pcbnew.PAD(fp)
        p.SetNumber(num)
        p.SetShape(pcbnew.PAD_SHAPE_RECT)
        p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        p.SetLayerSet(p.SMDMask())
        p.SetSize(vec(w, h))
        p.SetPosition(vec(x, y))
        fp.Add(p)
    cy = pcbnew.PCB_SHAPE(fp)
    cy.SetShape(pcbnew.SHAPE_T_RECT)
    cy.SetStart(vec(-1.05, -1.05))
    cy.SetEnd(vec(1.05, 1.05))
    cy.SetLayer(pcbnew.F_CrtYd)
    cy.SetWidth(mm(0.05))
    fp.Add(cy)
    return fp


_SEEN = {}


def id_counter(ref, num):
    """Counter for pads that share a number (U9 pad 49, U8 pad 2)."""
    k = (ref, num)
    _SEEN[k] = _SEEN.get(k, -1) + 1
    return _SEEN[k]


def load_fp(spec):
    lib, name = spec.split(":", 1)
    if lib == "CUSTOM":
        if name == "X2QFN-12_RWB":
            return x2qfn12_rwb()
        raise KeyError(spec)
    fp = pcbnew.FootprintLoad(FP_ROOT + lib + ".pretty", name)
    if fp is None:
        raise FileNotFoundError(spec)
    return fp


def bbox_mm(fp):
    b = fp.GetBoundingBox(False)
    return pcbnew.ToMM(b.GetX()), pcbnew.ToMM(b.GetY()), pcbnew.ToMM(b.GetRight()), pcbnew.ToMM(b.GetBottom())


def pad_bbox_mm(fp):
    xs0, ys0, xs1, ys1 = [], [], [], []
    for p in fp.Pads():
        b = p.GetBoundingBox()
        xs0.append(b.GetX())
        ys0.append(b.GetY())
        xs1.append(b.GetRight())
        ys1.append(b.GetBottom())
    return tuple(pcbnew.ToMM(v) for v in (min(xs0), min(ys0), max(xs1), max(ys1)))


def place_usb_c(fp):
    """Mating face on the left board edge, pads centred on y = BOARD_H/2."""
    pos = vec(0, 0)
    fp.SetPosition(pos)
    for rot in (90, 270):
        fp.SetOrientationDegrees(rot)
        shell = [p for p in fp.Pads() if p.GetNumber() == "SH"]
        a1 = [p for p in fp.Pads() if p.GetNumber() == "A1"][0]
        if min(s.GetPosition().x for s in shell) < a1.GetPosition().x:   # shell (front) is left of the pad grid
            break
    x0, y0, x1, y1 = bbox_mm(fp)
    px0, py0, px1, py1 = pad_bbox_mm(fp)
    fp.SetPosition(vec(0.2 - x0, BOARD_H / 2 - (py0 + py1) / 2))


# ----------------------------------------------------------------------------- build
def build(netlist, outdir, name="busy_light_spike"):
    comps, nets = read_netlist(netlist)
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    ds = board.GetDesignSettings()
    ds.m_MinClearance = mm(CLEARANCE)
    ds.m_CopperEdgeClearance = mm(EDGE_CLEARANCE)

    netitems = {}
    for n in nets:
        ni = pcbnew.NETINFO_ITEM(board, short_net(n))
        board.Add(ni)
        netitems[n] = ni

    # pad -> net lookup: (ref, pad number) -> net name
    pad_net = {}
    for n, nodes in nets.items():
        for ref, pin in nodes:
            m = PADMAP.get(ref, {}).get(pin, pin)
            for pn in (m if isinstance(m, tuple) else (m,)):
                pad_net[(ref, pn)] = n

    for ref in sorted(comps):
        value, fpname, sym_uuid = comps[ref]
        spec = FOOTPRINT_OVERRIDE.get(ref, fpname)
        if not spec:
            raise ValueError("no footprint for " + ref)
        fp = load_fp(spec)
        fp.SetFPID(pcbnew.LIB_ID(*spec.split(":", 1)))
        fp.SetReference(ref)
        fp.SetValue(value)
        if sym_uuid:
            fp.SetPath(pcbnew.KIID_PATH("/" + sym_uuid))   # link to the schematic symbol (parity check)
        fp.Reference().SetLayer(pcbnew.F_Fab)              # reference and value text on the fab layer, not silk
        fp.Value().SetLayer(pcbnew.F_Fab)
        fp.SetUuid(det_uuid("fp:" + ref))
        for p in fp.Pads():
            p.SetUuid(det_uuid("pad:%s:%s:%d" % (ref, p.GetNumber(), id_counter(ref, p.GetNumber()))))
        board.Add(fp)
        if ref == "J1":
            place_usb_c(fp)
        elif ref in PLACE:
            x, y, rot = PLACE[ref]
            fp.SetPosition(vec(x, y))
            fp.SetOrientationDegrees(rot)
        elif re.fullmatch(r"D\d+", ref):
            i = int(ref[1:]) - 1
            row, col = divmod(i, 8)
            col_x = col if row == 0 else 7 - col
            fp.SetPosition(vec(LED_X0 + LED_DX * col_x, LED_ROW_Y[row]))
            fp.SetOrientationDegrees(0 if row == 0 else 180)
        elif re.fullmatch(r"C(\d+)", ref) and 8 <= int(ref[1:]) <= 23:
            i = int(ref[1:]) - 8
            row, col = divmod(i, 8)
            col_x = col if row == 0 else 7 - col
            fp.SetPosition(vec(LED_X0 + LED_DX * col_x + 4.3, LED_ROW_Y[row] + (0 if row == 0 else 0)))
            fp.SetOrientationDegrees(90)
        elif re.fullmatch(r"TP\d+", ref):
            i = int(ref[2:]) - 1
            fp.SetPosition(vec(14.0 + 5.0 * i, TP_Y))
        else:
            raise KeyError("no placement rule for " + ref)
        # nets on pads
        for p in fp.Pads():
            key = (ref, p.GetNumber())
            if key in pad_net:
                p.SetNet(netitems[pad_net[key]])

    # mounting holes (provisional, mechanics open)
    for i, (hx, hy) in enumerate(((4.0, BOARD_H - 4.0), (BOARD_W - 4.0, BOARD_H - 4.0), (BOARD_W - 4.0, 4.0)), 1):
        h = pcbnew.FootprintLoad(FP_ROOT + "MountingHole.pretty", "MountingHole_3.2mm_M3")
        h.SetReference("H%d" % i)
        h.Reference().SetLayer(pcbnew.F_Fab)
        h.Value().SetLayer(pcbnew.F_Fab)
        h.SetValue("MountingHole (provisional)")
        h.SetUuid(det_uuid("fp:H%d" % i))
        h.SetPosition(vec(hx, hy))
        board.Add(h)

    # outline
    r = pcbnew.PCB_SHAPE(board)
    r.SetShape(pcbnew.SHAPE_T_RECT)
    r.SetStart(vec(0, 0))
    r.SetEnd(vec(BOARD_W, BOARD_H))
    r.SetLayer(pcbnew.Edge_Cuts)
    r.SetWidth(mm(0.1))
    r.SetUuid(det_uuid("edge"))
    board.Add(r)

    # GND pour on the back (front GND connects through vias placed by the router)
    z = pcbnew.ZONE(board)
    z.SetLayer(pcbnew.B_Cu)
    z.SetUuid(det_uuid("zone:gnd"))
    z.SetNet(netitems[GND])
    z.SetMinThickness(mm(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.3))
    z.SetThermalReliefSpokeWidth(mm(0.3))
    ol = z.Outline()
    ol.NewOutline()
    for x, y in ((0.3, 0.3), (BOARD_W - 0.3, 0.3), (BOARD_W - 0.3, BOARD_H - 0.3), (0.3, BOARD_H - 0.3)):
        ol.Append(mm(x), mm(y))
    board.Add(z)

    os.makedirs(outdir, exist_ok=True)
    pcb = os.path.join(outdir, name + ".kicad_pcb")
    pcbnew.SaveBoard(pcb, board)
    normalise_uuids(pcb)
    write_project(os.path.join(outdir, name + ".kicad_pro"), name)
    return pcb


_NS = uuid.UUID("5b0c2f0e-0000-4000-8000-00000000b051")


def det_uuid(key):
    """Deterministic KIID from a key, so KiCad's uuid-ordered containers are written in a fixed order."""
    return pcbnew.KIID(str(uuid.uuid5(_NS, key)))


def normalise_uuids(path):
    """KiCad gives every item a random uuid; replace them in file order so two builds are identical."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    ns = _NS
    seen = {}

    def sub(m):
        old = m.group(2)
        if old not in seen:
            seen[old] = str(uuid.uuid5(ns, str(len(seen))))
        return m.group(1) + seen[old] + '"'

    text = re.sub(r'((?:uuid|tstamp) ")([0-9a-fA-F-]{36})"', sub, text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def write_project(path, name):
    """Design rules and net classes (spike values, provisional). Written by script, never by hand."""
    power = sorted(NET_WIDTH)
    classes = [
        {"name": "Default", "clearance": CLEARANCE, "track_width": TRACK, "via_diameter": VIA_DIA,
         "via_drill": VIA_DRILL, "priority": 2147483647, "pcb_color": "rgba(0, 0, 0, 0.000)",
         "schematic_color": "rgba(0, 0, 0, 0.000)", "wire_width": 6, "bus_width": 12,
         "diff_pair_width": 0.2, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "line_style": 0,
         "microvia_diameter": 0.3, "microvia_drill": 0.1},
    ]
    for i, n in enumerate(power):
        c = dict(classes[0])
        c.update({"name": "PWR_" + n.strip("+"), "track_width": NET_WIDTH[n], "priority": i})
        classes.append(c)
    patterns = [{"netclass": "PWR_" + n.strip("+"), "pattern": n} for n in power]
    pro = {
        "board": {"design_settings": {"rules": {
            "min_clearance": CLEARANCE, "min_track_width": 0.15, "min_via_diameter": 0.5,
            "min_through_hole_diameter": 0.3, "min_via_annular_width": 0.1, "min_copper_edge_clearance": EDGE_CLEARANCE,
            "min_hole_clearance": 0.25, "min_hole_to_hole": 0.4, "min_connection": 0.1, "min_silk_clearance": 0.0,
            "min_text_height": 0.8, "min_text_thickness": 0.08, "min_resolved_spokes": 2}}},
        "meta": {"filename": name + ".kicad_pro", "version": 3},
        "net_settings": {"classes": classes, "meta": {"version": 3}, "net_colors": None,
                         "netclass_assignments": None, "netclass_patterns": patterns},
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(pro, f, indent=2, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    out = build(sys.argv[1], sys.argv[2], *(sys.argv[3:4] or []))
    print("wrote", out)
