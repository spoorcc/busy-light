# SPDX-License-Identifier: Apache-2.0
"""Spike: add vias that connect pads of plane nets (GND, +5V) to the copper pours after the router has run.

Freerouting treats a net with a copper pour as a plane net and leaves it to the pour; it writes no vias for it,
so the pads stay unconnected in KiCad. This script reads the unconnected pads of the plane nets from the DRC report,
and for each one places a via near the pad (checked against pads, tracks and vias of other nets, the board edge and
the antenna strip) with a short track from the pad to the via. Deterministic. Exploratory.

Usage: python3 pcb_stitch.py <in.kicad_pcb> <drc.json> <out.kicad_pcb> [nets, default GND,+5V]
"""
import json
import math
import re
import sys

import pcbnew

import mech_outline as MO
import pcb_full as P

import pcb_rules as R       # noqa: E402  (rule values: pcb_rules.py)
from pcb_rules import stitch_width   # noqa: E402

VIA_D, VIA_DRILL = R.VIA_DIA, R.VIA_DRILL
CLR = R.CLEARANCE + R.STITCH_MARGIN            # DRC clearance plus a margin
DIST = (0.8, 1.0, 1.25, 1.6, 2.0, 2.5, 3.2)
ANG = [i * 22.5 for i in range(16)]


def seg_dist(px, py, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / L2))
    return math.hypot(px - (x0 + t * dx), py - (y0 + t * dy))


def read_copper(pcb_path):
    """Segments and vias from the saved board text (the SWIG track iterator does not work with this Python)."""
    t = open(pcb_path, encoding="utf-8").read()
    segs = [(float(a), float(b), float(c), float(d), float(w), n) for a, b, c, d, w, n in re.findall(
        r'\(segment\s+\(start ([-\d.]+) ([-\d.]+)\)\s+\(end ([-\d.]+) ([-\d.]+)\)\s+\(width ([\d.]+)\).*?\(net "([^"]*)"\)', t, re.S)]
    vias = [(float(x), float(y), float(s), n) for x, y, s, n in re.findall(
        r'\(via\s+(?:\(blind[^)]*\)\s*)?\(at ([-\d.]+) ([-\d.]+)\)\s+\(size ([\d.]+)\).*?\(net "([^"]*)"\)', t, re.S)]
    return segs, vias


class Stitcher:
    def __init__(self, board, pcb_path):
        self.b = board
        self.segs, self.vias = read_copper(pcb_path)
        self.pads = []
        for f in board.GetFootprints():
            for p in f.Pads():
                bb = p.GetBoundingBox()
                self.pads.append((pcbnew.ToMM(bb.GetX()), pcbnew.ToMM(bb.GetY()), pcbnew.ToMM(bb.GetRight()),
                                  pcbnew.ToMM(bb.GetBottom()), p.GetNetname()))
        self.netitems = board.GetNetsByName()
        self.added = []
        self.failed = []

    def free(self, x, y, r, net):
        """True when a disc of radius r at (x, y) clears all copper of other nets (all layers, conservative)."""
        mx, my = x - P.CX, P.CY - y
        if not MO.inside_pcb(mx, my, R.STITCH_EDGE_MARGIN, self.tab_r):
            return False
        ax0, ay0, ax1, ay1 = MO.antenna_strip()
        if ax0 - r < mx < ax1 + r and ay0 - r < my < ay1 + r:
            return False
        for x0, y0, x1, y1, n in self.pads:
            if n == net:
                continue
            dx = max(x0 - x, 0.0, x - x1)
            dy = max(y0 - y, 0.0, y - y1)
            if math.hypot(dx, dy) < r + CLR:
                return False
        for a, b, c, d, w, n in self.segs:
            if n != net and seg_dist(x, y, a, b, c, d) < r + w / 2 + CLR:
                return False
        for vx, vy, vs, n in self.vias:
            if n != net and math.hypot(x - vx, y - vy) < r + vs / 2 + CLR:
                return False
        return True

    def put_via(self, ref, num, net, x, y):
        v = pcbnew.PCB_VIA(self.b)
        v.SetPosition(P.vec(x, y))
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetWidth(pcbnew.PADSTACK.ALL_LAYERS, P.mm(VIA_D)) if hasattr(pcbnew, "PADSTACK") else v.SetWidth(P.mm(VIA_D))
        v.SetDrill(P.mm(VIA_DRILL))
        v.SetNet(self.netitems[net])
        v.SetUuid(P.det_uuid("stitch:via:%s:%s" % (ref, num)))
        self.b.Add(v)
        self.vias.append((x, y, VIA_D, net))

    def track_free(self, p0, p1, w, net):
        n = max(2, int(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / 0.2))
        return all(self.free(p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n, w / 2, net)
                   for i in range(1, n + 1))

    def stitch_pad(self, ref, num, net, layer, cx, cy, big=False):
        w = stitch_width(net)
        if big and self.free(cx, cy, VIA_D / 2, net):         # via in a large pad (module ground pad, vendor practice)
            self.put_via(ref, num, net, cx, cy)
            self.added.append((ref, num, net, 0.0))
            return True
        for d in DIST:
            for a in ANG:
                x, y = cx + d * math.cos(math.radians(a)), cy + d * math.sin(math.radians(a))
                if self.free(x, y, VIA_D / 2, net) and self.track_free((cx, cy), (x, y), w, net):
                    ni = self.netitems[net]
                    self.put_via(ref, num, net, x, y)
                    tr = pcbnew.PCB_TRACK(self.b)
                    tr.SetStart(P.vec(cx, cy))
                    tr.SetEnd(P.vec(x, y))
                    tr.SetWidth(P.mm(w))
                    tr.SetLayer(layer)
                    tr.SetNet(ni)
                    tr.SetUuid(P.det_uuid("stitch:trk:%s:%s" % (ref, num)))
                    self.b.Add(tr)
                    self.segs.append((cx, cy, x, y, w, net))
                    self.added.append((ref, num, net, round(d, 2)))
                    return True
        self.failed.append((ref, num, net))
        return False


def unconnected_pads(drc_path, nets):
    d = json.load(open(drc_path, encoding="utf-8"))
    out = {}
    for v in d["unconnected_items"]:
        for it in v["items"]:
            m = re.match(r"(?:PTH |SMD )?[Pp]ad (\S+) \[(.*?)\] of (\S+) on (\S+)", it["description"])
            if m and m.group(2) in nets:
                out[(m.group(3), m.group(1))] = (m.group(2), m.group(4))
    return out


def main(src, drc, dst, nets=R.PLANE_NET_ORDER, tab_r=None):
    board = pcbnew.LoadBoard(src)
    st = Stitcher(board, src)
    info = json.load(open(src.rsplit("/", 1)[0] + "/busy_light_spike.placement.json")) if tab_r is None else {"tab_r": tab_r}
    st.tab_r = info["tab_r"]
    todo = unconnected_pads(drc, nets)
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    for (ref, num), (net, lname) in sorted(todo.items()):
        f = fps[ref]
        for p in f.Pads():
            if p.GetNumber() == num and p.GetNetname() == net:
                layer = pcbnew.B_Cu if lname.startswith("B") else pcbnew.F_Cu
                if not p.IsOnLayer(layer):
                    layer = pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
                big = ref == "U9"          # module ground pads: via in the pad (vendor practice; filled or capped vias needed)
                st.stitch_pad(ref, num, net, layer, pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y), big)
                break
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(dst, board)
    P.normalise_uuids(dst)
    rep = {"pads_to_stitch": len(todo), "vias_added": len(st.added), "failed": st.failed}
    print(json.dumps(rep, sort_keys=True))
    return rep


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3], tuple((sys.argv[4] if len(sys.argv) > 4 else ",".join(R.PLANE_NET_ORDER)).split(",")))
