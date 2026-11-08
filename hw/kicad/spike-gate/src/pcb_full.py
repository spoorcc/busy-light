# SPDX-License-Identifier: Apache-2.0
"""Spike: generate a placed (not routed) PCB of the full board from the schematic netlist.

Exploratory, not a product design (ADR-0012 is Proposed; mechanics, LED count and peg azimuth are open,
so the outline and the LED field are provisional). The board file is written only by this script
(KiCad pcbnew Python API); it is never edited by hand.

Usage: python3 pcb_full.py <netlist.net> <out dir> [name] [layers 2|4]
  writes <out dir>/<name>.kicad_pcb (default name busy_light_spike) and <name>.kicad_pro

The netlist comes from `kicad-cli sch export netlist` on the output of run_full.sh, so every ref, value
and net is the schematic's. Where the schematic names a footprint that the system KiCad libraries do not
have, or a pin name that is not a pad number, the tables below say what was substituted (all PROVISIONAL).
"""
import json
import math
import os
import re
import sys
import uuid
from pathlib import Path

import pcbnew

import custom_fp
import lib_tables

FP_ROOT = os.environ.get("KICAD_FOOTPRINT_DIR", "/usr/share/kicad/footprints/")
_IO = pcbnew.PCB_IO_KICAD_SEXPR()      # one plugin object for the whole run (a temporary one breaks pcbnew.FootprintLoad)
CUSTOM_DIR = ""                   # set by build(): the output directory that holds CUSTOM.pretty

# ----------------------------------------------------------------------------- board parameters
J1_MOUTH_R = 29.85                        # V1: receptacle mouth radius of the mech spike (mech_outline.USB_MOUTH_R)
J1_LED_GAP = 0.45                         # mm between the rear J1 pad edge and the nearest LED pad
J1_COURT_GAP = 0.05                       # mm between the J1 courtyard and the nearest LED courtyard
J1_TAB_BEHIND_MOUTH = 0.85                # mech: tab ends 0.85 mm before the mouth (29.0 vs 29.85)
from pcb_rules import CLEARANCE, TRACK, VIA_DIA, VIA_DRILL, EDGE_CLEARANCE   # noqa: E402  (rule values: pcb_rules.py)
# Net classes by net name: width in mm. IPC-2221 external layer, 1 oz (35 um), 10 K rise:
# 1.5 A -> 0.53 mm, 2.0 A -> 0.78 mm (see report). The power nets are routed at 0.8 mm where space allows.
import pcb_rules                  # noqa: E402
from pcb_rules import NET_WIDTH   # noqa: E402  (shared with the tests; values and basis in pcb_rules.py)
GND = "GND"
from pcb_rules import NET_TRACK   # noqa: E402  (signal nets at the 0.4 mm pitch pads of U1 use the minimum width)
import pcb_rules                  # noqa: E402
# Star nets: every pad is routed straight to the named pad, so the branch point is at that pad.
# ADR-0016 layout rule: the step 3 switch control pin (U15 SEL) is the tap point of U13 pin 2, R3, R19 and the readback R15.
STAR = {"/ILIM_STEP3_EN": ("U15", "4")}

# ----------------------------------------------------------------------------- provisional substitutions
# ref -> footprint (lib:name) used instead of the schematic's footprint field
FOOTPRINT_OVERRIDE = {
    "U1": "CUSTOM:X2QFN-12_RWB",                      # Package_X2QFN does not exist in the system libraries
    "C3": "Capacitor_SMD:C_0805_2012Metric",          # 10 uF tbd
    "C4": "Capacitor_SMD:C_1206_3216Metric",          # bulk tbd
}

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


_SEEN = {}


def id_counter(ref, num):
    """Counter for pads that share a number (U9 pad 49, U8 pad 2)."""
    k = (ref, num)
    _SEEN[k] = _SEEN.get(k, -1) + 1
    return _SEEN[k]


U9_NAME = "ESP32-C3-MINI-1"


def derive_u9_footprint(outdir):
    """Write CUSTOM.pretty/ESP32-C3-MINI-1 from the stock RF_Module footprint ESP32-C6-MINI-1 without its own keep-out
    zone (the board has its own rule areas) and without its 3D model reference. KiCad has no C3-MINI-1 footprint. The
    land pattern of both modules is the one of datasheet figure 11-1 (ESP32-C3-MINI-1 datasheet v2.2: 48 pads 0.8 x 0.4,
    four 0.7 mm corner pads, 3 x 3 grid of 1.45 mm ground pads); tests/test_pcb_full.py compares the numbers. A named
    project footprint instead of a silent change of the stock one (no lib_footprint_mismatch)."""
    fp = _IO.FootprintLoad(FP_ROOT + "RF_Module.pretty", "ESP32-C6-MINI-1")
    for z in list(fp.Zones()):
        fp.Remove(z)
    fp.SetFPID(pcbnew.LIB_ID("", U9_NAME))
    fp.SetLibDescription("ESP32-C3-MINI-1 module, land pattern of datasheet v2.2 figure 11-1 (derived from the KiCad ESP32-C6-MINI-1 footprint, same pads)")
    fp.Models().clear()
    pretty = os.path.join(outdir, custom_fp.NICK + ".pretty")
    os.makedirs(pretty, exist_ok=True)
    _IO.FootprintSave(pretty, fp)
    mod = os.path.join(pretty, U9_NAME + ".kicad_mod")
    normalise_uuids(mod)


def load_fp(spec):
    lib, name = spec.split(":", 1)
    if lib == custom_fp.NICK:       # generated library in the project directory (custom_fp.write_library)
        fp = _IO.FootprintLoad(CUSTOM_DIR + "/" + lib + ".pretty", name)
    else:
        fp = _IO.FootprintLoad(FP_ROOT + lib + ".pretty", name)
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


# ----------------------------------------------------------------------------- placement (mechanical frame)
# Origin of the housing axis on the board sheet. KiCad y points down, the mechanical frame has y up (seen from
# above), so KiCad (x, y) = (CX + mx, CY - my). All numbers of the envelope are in mech_outline.py with sources.
CX, CY = 40.0, 40.0
BOARD_W, BOARD_H = 2 * CX, 2 * CY       # sheet extent only (the router grid and the checks use it)
import mech_outline as MO   # noqa: E402
import pcb_place            # noqa: E402

SW1_POS = (13.0, 240.0)       # (radius, azimuth): inside the LED ring; a side-actuated switch would sit at the edge
MODULE_ROT = 90               # antenna end towards -X (footprint antenna is at the top, rotation 90 turns it left)
MARGIN_EXT = 0.25             # extent = pads + this margin (stands in for the courtyard)
# ADR-0016 proximity rules (centre distance, mm); the placer rejects a seed that breaks one, the test checks the board
LAYOUT_RULES = (("R3", "U15", 6.0), ("R2", "U14", 6.0), ("R18", "U14", 6.0), ("R19", "U15", 6.0),
                ("C24", "U14", 6.0), ("C25", "U15", 6.0),         # bypass capacitor at the switch supply pin
                ("R_ILIM1", "U7", 15.0), ("R_ILIM2", "U7", 15.0), ("R_ILIM3", "U7", 15.0), ("R_ILIM3B", "U7", 15.0),
                ("C1", "U5", 8.0), ("C1B", "U5", 12.0), ("C1C", "U5", 14.0), ("C1D", "U5", 14.0),
                ("C1E", "U5", 14.0), ("C1F", "U5", 14.0))
PLACE_MARGIN = 0.27           # extents already include the courtyard; this only keeps rounding off the DRC line
R_MOVE = 17.3                 # movable parts stay inside this radius (the LED ring pads start at about 17.8; was 16.6, loosened 2026-11-07 by owner choice)
SA_ITERS = 160000
_SEED0 = int(os.environ.get("PLACE_SEED_START", "1"))    # run_best.sh gives every run its own placement seeds
SA_SEEDS = tuple(range(_SEED0, _SEED0 + 16))


def K(mx, my):
    x, y = MO.kicad_xy(mx, my, CX, CY)
    return x, y


def mech_of(x_mm, y_mm):
    return x_mm - CX, CY - y_mm


def court_bbox_mm(fp):
    """Bounding box of the footprint courtyard on its own side, or None when the footprint has none."""
    layer = pcbnew.B_CrtYd if fp.GetLayer() == pcbnew.B_Cu else pcbnew.F_CrtYd
    cy = fp.GetCourtyard(layer)
    if cy.OutlineCount() == 0:
        return None
    b = cy.BBox()
    return pcbnew.ToMM(b.GetX()), pcbnew.ToMM(b.GetY()), pcbnew.ToMM(b.GetRight()), pcbnew.ToMM(b.GetBottom())


def pad_extent_mm(fp, margin=0.0):
    """Pads plus margin, widened to the courtyard (plan 06 G1: DRC counts courtyard overlaps). U9 is excluded:
    its library courtyard is the antenna keep-out, which the board treats as rule areas."""
    x0, y0, x1, y1 = pad_bbox_mm(fp)
    c = None if fp.GetReference() == "U9" else court_bbox_mm(fp)
    if c:
        x0, y0, x1, y1 = min(x0, c[0] + margin), min(y0, c[1] + margin), max(x1, c[2] - margin), max(y1, c[3] - margin)
    return x0 - margin, y0 - margin, x1 + margin, y1 + margin


def centre_at(fp, cx, cy, margin=MARGIN_EXT):
    """Move fp so the centre of its pad extent is at (cx, cy) mm."""
    x0, y0, x1, y1 = pad_extent_mm(fp, margin)
    p = fp.GetPosition()
    fp.SetPosition(pcbnew.VECTOR2I(p.x + mm(cx - (x0 + x1) / 2), p.y + mm(cy - (y0 + y1) / 2)))


def orient(fp, rot, side):
    """Set side and rotation (the rotation as seen on the board sheet, counter-clockwise)."""
    if side == "B":
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    fp.SetOrientationDegrees(rot)


def led_ring_refs():
    return [("D%d" % (i + 1), "C%d" % (i + 8), i) for i in range(16)]


def polar_rect_to_bbox(az, r0, r1, half_w, cx, cy):
    """Bounding box (KiCad mm) of a polar rectangle: radial r0..r1, tangential +-half_w at azimuth az."""
    pts = []
    for r in (r0, r1):
        for t in (-half_w, half_w):
            a = math.radians(az)
            mx = r * math.cos(a) - t * math.sin(a)
            my = r * math.sin(a) + t * math.cos(a)
            pts.append((cx + mx, cy - my))
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys), pts


def corner_points(az, r0, r1, half_w):
    out = []
    for r, t in ((r0, -half_w), (r1, -half_w), (r1, half_w), (r0, half_w)):
        a = math.radians(az)
        out.append(K(r * math.cos(a) - t * math.sin(a), r * math.sin(a) + t * math.cos(a)))
    return out


# ----------------------------------------------------------------------------- build
def add_rule_area(board, name, layers, pts, tracks=True, vias=True, pours=True, footprints=False):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetZoneName(name)
    ls = pcbnew.LSET()
    for l in layers:
        ls.AddLayer(l)
    z.SetLayerSet(ls)
    z.SetDoNotAllowTracks(tracks)
    z.SetDoNotAllowVias(vias)
    z.SetDoNotAllowZoneFills(pours)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(footprints)
    z.SetUuid(det_uuid("rule:" + name))
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        ol.Append(mm(x), mm(y))
    board.Add(z)
    return z


def build(netlist, outdir, name="busy_light_spike", sa_iters=None, layers=2):
    global CUSTOM_DIR
    os.makedirs(outdir, exist_ok=True)
    CUSTOM_DIR = os.path.abspath(outdir)
    custom_fp.write_library(outdir)
    derive_u9_footprint(outdir)
    comps, nets = read_netlist(netlist)
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(layers)
    ds = board.GetDesignSettings()
    ds.m_MinClearance = mm(CLEARANCE)
    ds.m_CopperEdgeClearance = mm(EDGE_CLEARANCE)

    netitems = {}
    for n in nets:
        ni = pcbnew.NETINFO_ITEM(board, short_net(n))
        board.Add(ni)
        netitems[n] = ni

    pad_net = {}
    for n, nodes in nets.items():
        for ref, pin in nodes:          # schematic pin numbers are the pad numbers (layout_full.PAD)
            pad_net[(ref, pin)] = n

    # ---- load all footprints
    fps = {}
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
            fp.SetPath(pcbnew.KIID_PATH("/" + sym_uuid))
        fp.Reference().SetLayer(pcbnew.F_Fab)
        fp.Value().SetLayer(pcbnew.F_Fab)
        fp.SetUuid(det_uuid("fp:" + ref))
        for p in fp.Pads():
            p.SetUuid(det_uuid("pad:%s:%s:%d" % (ref, p.GetNumber(), id_counter(ref, p.GetNumber()))))
            key = (ref, p.GetNumber())
            if key in pad_net:
                p.SetNet(netitems[pad_net[key]])
        board.Add(fp)                       # Flip() needs the footprint on a board
        fps[ref] = fp

    # the module's own keep-out zone (43 x 20 mm) is replaced by the board-level rule areas below (the footprint
    # of U9 is the library one without that zone, written to CUSTOM.pretty by derive_u9_footprint)
    assert not list(fps["U9"].Zones())

    fixed = set()
    fixed_pins = {}          # (ref, pad) -> (x, y) in the SA frame (KiCad axes, origin at the housing axis)
    fixed_rects = []         # (side, x0, y0, x1, y1) in the SA frame

    def note_fixed(ref, side, margin=MARGIN_EXT):
        fixed.add(ref)
        fp = fps[ref]
        x0, y0, x1, y1 = pad_extent_mm(fp, margin)
        fixed_rects.append((side, x0 - CX, y0 - CY, x1 - CX, y1 - CY))
        for p in fp.Pads():
            fixed_pins[(ref, p.GetNumber())] = (pcbnew.ToMM(p.GetPosition().x) - CX, pcbnew.ToMM(p.GetPosition().y) - CY)

    # ---- LED ring (top) and bypass caps (bottom), mech ring radius and phase
    for k, (dref, cref, i) in enumerate(led_ring_refs()):
        az = MO.led_azimuths()[i]
        x, y = K(*MO.polar(MO.R_RING, az))
        rot = MO.led_rotation_deg(az)
        d = fps[dref]
        d.SetPosition(vec(0, 0))
        orient(d, rot, "F")
        centre_at(d, x, y, 0.0)
        # centre on the LED body centre rather than the pad extent: pads are symmetric, so they coincide
        note_fixed(dref, "F")
        shift = MO.led_cap_shift_mm(i, az)
        r_cap = MO.R_RING
        a2 = az + math.degrees(shift / r_cap)
        cx_, cy_ = K(*MO.polar(r_cap, a2))
        c = fps[cref]
        c.SetPosition(vec(0, 0))
        orient(c, rot, "B")
        # the cap pad axis stays tangential and the +5V pad of the cap sits under the +5V pad of the LED (same for GND):
        # the four rotations are tried, the tangential ones are ranked by the distance of the equal-net pads
        tang = (math.cos(math.radians(az)), -math.sin(math.radians(az)))   # radial in KiCad axes
        best = None
        for tr in (rot, (rot + 180) % 360, (rot + 90) % 360, (rot + 270) % 360):
            c.SetOrientationDegrees(tr)
            c.SetPosition(vec(0, 0))
            pp = {q.GetNumber(): q.GetPosition() for q in c.Pads()}
            vx, vy = pcbnew.ToMM(pp["1"].x - pp["2"].x), pcbnew.ToMM(pp["1"].y - pp["2"].y)
            n = math.hypot(vx, vy) or 1.0
            if abs((vx * tang[0] + vy * tang[1]) / n) >= 0.3:          # pad axis not tangential
                continue
            # LED pads in the same frame: pad 4 is +5V and pad 2 is GND (KiCad symbol LED:WS2812B-2020); the LED sits at the origin here
            lp = {q.GetNumber(): q.GetPosition() for q in d.Pads()}
            lx = {k: (pcbnew.ToMM(v.x - d.GetPosition().x), pcbnew.ToMM(v.y - d.GetPosition().y)) for k, v in lp.items()}
            cx = {k: (pcbnew.ToMM(v.x), pcbnew.ToMM(v.y)) for k, v in pp.items()}
            cost = math.hypot(lx["4"][0] - cx["1"][0], lx["4"][1] - cx["1"][1]) + math.hypot(lx["2"][0] - cx["2"][0], lx["2"][1] - cx["2"][1])
            if best is None or cost < best[0] - 1e-9:
                best = (cost, tr)
        c.SetOrientationDegrees(best[1] if best else rot)
        centre_at(c, cx_, cy_, 0.0)
        note_fixed(cref, "B")

    # ---- USB-C receptacle (variant V1: on the tab, mating face towards +X, outside the LED ring)
    j1 = fps["J1"]
    j1.SetPosition(vec(0, 0))
    for rot in (90, 270):
        j1.SetOrientationDegrees(rot)
        shell = [p for p in j1.Pads() if p.GetNumber() == "SH"]
        a1 = [p for p in j1.Pads() if p.GetNumber() == "A1"][0]
        if min(s.GetPosition().x for s in shell) > a1.GetPosition().x:     # shell (front) is right of the pad grid
            break
    x0, y0, x1, y1 = bbox_mm(j1)
    px0, py0, px1, py1 = pad_bbox_mm(j1)
    # The mech spike places the mouth at R 29.85 (receptacle body R 22.5..29.85, placeholder LEDs 2 mm). The real
    # LED pads (WS2812B-2020 stand-in) reach R 22.3 and the footprint pads start 9.5 mm behind the mouth, so the mouth is
    # moved out until the rear pad edge clears the nearest LED pads by J1_LED_GAP. Both numbers go in the report.
    led_pad_x = max(pcbnew.ToMM(p.GetBoundingBox().GetRight()) for r in ("D1", "D16") for p in fps[r].Pads()) - CX
    rear = (x1 - px0)                                   # mouth to rear pad edge, mm
    mouth_r = max(J1_MOUTH_R, led_pad_x + J1_LED_GAP + rear)
    # the courtyards of J1 and the nearest LEDs must not overlap either (plan 06 G1)
    jc, lc = court_bbox_mm(j1), [court_bbox_mm(fps[r]) for r in ("D1", "D16")]
    if jc and all(lc):
        mouth_r = max(mouth_r, max(c[2] for c in lc) - CX + J1_COURT_GAP + (x1 - jc[0]))
    tab_r = mouth_r - J1_TAB_BEHIND_MOUTH
    j1.SetPosition(vec(CX + mouth_r - x1, CY - (py0 + py1) / 2))
    note_fixed("J1", "F", 0.3)
    # through-hole shell pins also occupy the bottom side
    fixed_rects.append(("B",) + tuple(v - c for v, c in zip(pad_extent_mm(j1, 0.3), (CX, CY, CX, CY))))

    # ---- module (top, centre of the PCB, antenna end towards -X)
    u9 = fps["U9"]
    u9.SetPosition(vec(0, 0))
    orient(u9, MODULE_ROT, "F")
    mx0, my0, mx1, my1 = MO.module_rect()
    ax0, ay0, ax1, ay1 = MO.antenna_strip()
    # the pad area starts at the end of the antenna strip (datasheet fig 11-1: antenna area beyond the pad rows);
    # the pad area is not centred in the module body, so the pads are centred on the strip end plus half their length
    ex0, _, ex1, _ = pad_extent_mm(u9, 0.0)
    mcx, mcy = K(ax1 + (ex1 - ex0) / 2, (my0 + my1) / 2)
    centre_at(u9, mcx, mcy, 0.0)
    note_fixed("U9", "F", 0.0)
    # module body as a top-side obstacle
    kx0, ky0 = K(mx0, my1)
    kx1, ky1 = K(mx1, my0)
    fixed_rects.append(("F", kx0 - CX - 0.3, ky0 - CY - 0.3, kx1 - CX + 0.3, ky1 - CY + 0.3))

    # ---- button
    sw = fps["SW1"]
    sw.SetPosition(vec(0, 0))
    orient(sw, 0, "F")
    sx, sy = K(*MO.polar(*SW1_POS))
    centre_at(sw, sx, sy)
    note_fixed("SW1", "F")

    # ---- keep-out rectangles from the base posts (bottom) and hook lugs (top)
    for az, r0, r1, hw in MO.post_keepouts():
        bx0, by0, bx1, by1, _ = polar_rect_to_bbox(az, r0, r1, hw, CX, CY)
        fixed_rects.append(("B", bx0 - CX, by0 - CY, bx1 - CX, by1 - CY))

    # ---- movable parts: simulated annealing
    parts = {}
    for ref, fp in fps.items():
        if ref in fixed:
            continue
        fp.SetPosition(vec(0, 0))
        orient(fp, 0, "F")
        x0, y0, x1, y1 = pad_extent_mm(fp, MARGIN_EXT)
        ox, oy = (x0 + x1) / 2, (y0 + y1) / 2
        pads = {}
        for p in fp.Pads():
            pads.setdefault(p.GetNumber(), (pcbnew.ToMM(p.GetPosition().x) - ox, pcbnew.ToMM(p.GetPosition().y) - oy))
        parts[ref] = {"w": x1 - x0 - 2 * MARGIN_EXT, "h": y1 - y0 - 2 * MARGIN_EXT, "pads": pads}
        if ref.startswith("TP"):
            parts[ref]["sides"] = "B"
    sa_nets = {}
    for n, nodes in nets.items():
        if n == GND or n.startswith("unconnected-"):
            continue
        lst = list(nodes)
        if len(lst) >= 2:
            sa_nets[n] = lst

    weights = {n: w for n, w in pcb_rules.NET_WEIGHT.items() if n in sa_nets}
    for tie, (a, b, w) in pcb_rules.PIN_TIES.items():      # bypass capacitor at the supply pin (pseudo-net, not on the board)
        if a[0] in comps and b[0] in comps:
            sa_nets[tie] = [a, b]
            weights[tie] = w

    def region_ok(side, x0, y0, x1, y1):       # SA frame (y down) -> mechanical frame (y up)
        return MO.region_rect_ok(side, x0, -y1, x1, -y0, R_MOVE, tab_r)

    def layout_rules_ok(st):
        return all(math.hypot(st[a][0] - st[b][0], st[a][1] - st[b][1]) <= lim
                   for a, b, lim in LAYOUT_RULES if a in st and b in st)

    state, seed, wl, ov = pcb_place.place(parts, sa_nets, fixed_pins, fixed_rects, region_ok,
                                          seeds=SA_SEEDS, iters=sa_iters or SA_ITERS, margin=PLACE_MARGIN,
                                          accept=layout_rules_ok, weights=weights, rules=LAYOUT_RULES)
    for ref, (x, y, rot, side) in sorted(state.items()):
        fp = fps[ref]
        fp.SetPosition(vec(0, 0))
        orient(fp, rot, side)
        centre_at(fp, CX + x, CY + y)
    placement_info = {"seed": seed, "hpwl_mm": round(wl, 1), "overlap_mm2": round(ov, 3)}

    # ---- outline (mechanical V1 envelope)
    for i, seg in enumerate(MO.outline_segments(tab_r)):
        if seg[0] == "arc":
            s = pcbnew.PCB_SHAPE(board)
            s.SetShape(pcbnew.SHAPE_T_ARC)
            s.SetArcGeometry(vec(*K(*seg[1])), vec(*K(*seg[2])), vec(*K(*seg[3])))
        else:
            s = pcbnew.PCB_SHAPE(board)
            s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetStart(vec(*K(*seg[1])))
            s.SetEnd(vec(*K(*seg[2])))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        s.SetUuid(det_uuid("edge:%d" % i))
        board.Add(s)

    # ---- slot between the antenna end and the LED ring (Edge.Cuts)
    for i, seg in enumerate(MO.slot_segments()):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(vec(*K(*seg[1])))
        s.SetEnd(vec(*K(*seg[2])))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        s.SetUuid(det_uuid("edge:slot:%d" % i))
        board.Add(s)

    # ---- GND pours on both layers (the outline polygon; the fill keeps its own edge clearance)
    hw, xj = MO.tab_half_intersection()
    poly = []
    b = math.degrees(math.asin(hw / MO.R_PCB))
    n_arc = 120
    for k in range(n_arc + 1):
        a = b + (360.0 - 2 * b) * k / n_arc
        poly.append(K(*MO.polar(MO.R_PCB - 0.01, a)))
    poly.append(K(tab_r - 0.01, -hw + 0.01))
    poly.append(K(tab_r - 0.01, hw - 0.01))
    if layers == 2:
        pours = ((pcbnew.B_Cu, "B", GND), (pcbnew.F_Cu, "F", GND))
    else:       # 4 layers: In1 = GND plane, In2 = +5V plane, +3V3 and signals routed on the outer layers
        pours = ((pcbnew.In1_Cu, "In1", GND), (pcbnew.In2_Cu, "In2", "+5V"))
    for k, (layer, lname, pnet) in enumerate(pours):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetUuid(det_uuid("zone:%s:%s" % (pnet, lname)))
        z.SetNet(netitems[pnet])
        z.SetMinThickness(mm(0.2))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(mm(0.3))
        z.SetThermalReliefSpokeWidth(mm(0.3))
        z.SetAssignedPriority(len(pours) - k)
        ol = z.Outline()
        ol.NewOutline()
        for x, y in poly:
            ol.Append(mm(x), mm(y))
        board.Add(z)

    # ---- rule areas: antenna strip (no copper on either layer), hooks (top) and posts (bottom)
    ap = [K(ax0, ay0), K(ax1, ay0), K(ax1, ay1), K(ax0, ay1)]
    add_rule_area(board, "antenna_strip", (pcbnew.F_Cu, pcbnew.B_Cu) + ((pcbnew.In1_Cu, pcbnew.In2_Cu) if layers == 4 else ()), ap, footprints=False)   # U9 itself sits here
    # keep-out around the slot: copper at least EDGE_CLEARANCE plus 0.2 mm from its edge (the router does not see Edge.Cuts slots)
    sx0, sy0, sx1, sy1 = MO.slot_rect()
    g = pcb_rules.EDGE_CLEARANCE + 0.2
    add_rule_area(board, "slot_keepout", (pcbnew.F_Cu, pcbnew.B_Cu) + ((pcbnew.In1_Cu, pcbnew.In2_Cu) if layers == 4 else ()),
                  [K(sx0 - g, sy0 - g), K(sx1 + g, sy0 - g), K(sx1 + g, sy1 + g), K(sx0 - g, sy1 + g)], footprints=False)
    for az, r0, r1, hw_ in MO.hook_keepouts():
        add_rule_area(board, "hook_%d" % az, (pcbnew.F_Cu,), corner_points(az, r0, r1, hw_),
                      tracks=False, vias=False, pours=False, footprints=True)
    for az, r0, r1, hw_ in MO.post_keepouts():
        add_rule_area(board, "post_%d" % az, (pcbnew.B_Cu,), corner_points(az, r0, r1, hw_),
                      tracks=False, vias=False, pours=False, footprints=True)

    os.makedirs(outdir, exist_ok=True)
    pcb = os.path.join(outdir, name + ".kicad_pcb")
    pcbnew.SaveBoard(pcb, board)
    normalise_uuids(pcb)
    write_project(os.path.join(outdir, name + ".kicad_pro"), name)
    used = sorted({str(fp.GetFPID().GetLibNickname()) for fp in board.GetFootprints()})
    lib_tables.write_text(Path(outdir) / "fp-lib-table", lib_tables.fp_lib_table(used))
    pcb_rules.write_dru(os.path.join(outdir, name + ".kicad_dru"), layers)
    with open(os.path.join(outdir, name + ".placement.json"), "w", encoding="utf-8") as f:
        json.dump(dict(placement_info, sa_iters=sa_iters or SA_ITERS, cx=CX, cy=CY, j1_mouth_r=round(mouth_r, 2), tab_r=round(tab_r, 2), largest_dim_mm=round(MO.check_largest_dim(mouth_r), 2)), f, indent=1, sort_keys=True)
        f.write("\n")
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


DRC_ON = ("missing_courtyard", "track_not_centered_on_via", "tuning_profile_track_geometries",
          "footprint_filters_mismatch", "footprint_type_mismatch")


def write_project(path, name):
    """Design rules and net classes (spike values, provisional; numbers from pcb_rules.py). Written by script, never
    by hand. The .kicad_dru of the same stem is written next to it by pcb_rules.write_dru (see build)."""
    R = pcb_rules
    power = sorted(NET_WIDTH)
    widths = R.net_class_widths()
    classes = [
        {"name": "Default", "clearance": R.CLEARANCE, "track_width": widths["Default"], "via_diameter": R.VIA_DIA,
         "via_drill": R.VIA_DRILL, "priority": 2147483647, "pcb_color": "rgba(0, 0, 0, 0.000)",
         "schematic_color": "rgba(0, 0, 0, 0.000)", "wire_width": 6, "bus_width": 12,
         "diff_pair_width": 0.2, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "line_style": 0,
         "microvia_diameter": 0.3, "microvia_drill": 0.1},
    ]
    for i, n in enumerate(power):
        c = dict(classes[0])
        c.update({"name": R.net_class_name(n), "track_width": widths[R.net_class_name(n)], "priority": i})
        classes.append(c)
    patterns = [{"netclass": R.net_class_name(n), "pattern": n} for n in power]
    pro = {
        "board": {"design_settings": {"rules": {
            "min_clearance": R.CLEARANCE, "min_track_width": R.MIN_TRACK, "min_via_diameter": R.MIN_VIA_DIA,
            "min_through_hole_diameter": R.MIN_THROUGH_HOLE, "min_via_annular_width": R.ANNULAR,
            "min_copper_edge_clearance": R.EDGE_CLEARANCE,
            "min_hole_clearance": R.HOLE_CLEARANCE, "min_hole_to_hole": R.HOLE_TO_HOLE, "min_connection": 0.1,
            "min_silk_clearance": 0.0,
            "min_text_height": 0.8, "min_text_thickness": 0.08, "min_resolved_spokes": 2},
            # checks KiCad ignores by default; the strict gate counts ignored checks, so they are on (2026-11-07)
            "rule_severities": {k: "warning" for k in DRC_ON}}},
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
    out = build(sys.argv[1], sys.argv[2], *(sys.argv[3:4] or ["busy_light_spike"]), layers=int(sys.argv[4]) if len(sys.argv) > 4 else 2)
    print("wrote", out)
