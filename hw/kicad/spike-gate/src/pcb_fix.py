# SPDX-License-Identifier: Apache-2.0
"""Spike: post-route clean-up. Connects the pairs that the DRC reports as `unconnected_items` after Freerouting and the
stitcher, with a small deterministic A* grid router on four layers.

Each pair is routed on its own: obstacles are the copper of other nets (pads, tracks, vias, board edge, slot, rule areas)
grown by the clearance plus half the track width; the copper of the same net is free. Vias are through vias and keep the
hole-to-hole distance. New copper is added to the obstacle maps before the next pair. No random numbers; pairs in report
order. The result is checked by `kicad-cli pcb drc`, which this script does not replace.

Usage: python3 pcb_fix.py <in.kicad_pcb> <drc.json> <out.kicad_pcb>            route the unconnected pairs
       python3 pcb_fix.py auto <folder>                                        rounds of ripup, route and DRC on <folder>/stitched.kicad_pcb
       python3 pcb_fix.py ripup <in.kicad_pcb> <drc.json> <out.kicad_pcb>      remove a track at each clearance finding
Exit code 1 when a pair could not be routed.
"""
import heapq
import json
import math
import re
import sys

import numpy as np
import pcbnew
from scipy import ndimage

import mech_outline as MO
import pcb_full as P
import pcb_rules as R

RES = 0.05                    # grid step, mm
SIGHT = 0.06                  # extra margin against grid rounding and diagonal moves, mm (about 1.2 grid steps)
VIA_COST = 24.0               # in grid steps (1.2 mm)
INNER_COST = 2.5              # cost factor on In1 and In2 (the planes): the outer layers are preferred
WINDOW = 8.0                  # mm around the two end points that the search may use
LAYERS = ("F.Cu", "In1.Cu", "In2.Cu", "B.Cu")
LAYER_ID = {"F.Cu": pcbnew.F_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu, "B.Cu": pcbnew.B_Cu}
COST = {"F.Cu": 1.0, "In1.Cu": INNER_COST, "In2.Cu": INNER_COST, "B.Cu": 1.0}


def mmf(v):
    return pcbnew.ToMM(v)


def seg_points(x0, y0, x1, y1, step):
    n = max(1, int(math.ceil(math.hypot(x1 - x0, y1 - y0) / step)))
    return [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n + 1)]


def via_dia(via):
    """Via diameter in mm (the SWIG binding takes a layer argument or none, depending on the KiCad build)."""
    try:
        return mmf(via.GetWidth(pcbnew.F_Cu))
    except TypeError:
        return mmf(via.GetWidth())


def parse_item(desc):
    """('pad', ref, number, net, layer) | ('track', net, layer) | ('via', net) from a DRC item description."""
    m = re.match(r"(?:PTH |SMD )?[Pp]ad (\S+) \[(.*?)\] of (\S+)(?: on (\S+))?", desc)
    if m:
        return ("pad", m.group(3), m.group(1), m.group(2), m.group(4))
    m = re.match(r"Track \[(.*?)\] on (\S+?),", desc)
    if m:
        return ("track", m.group(1), m.group(2))
    m = re.match(r"Via \[(.*?)\]", desc)
    if m:
        return ("via", m.group(1))
    return None


class Fixer:
    def __init__(self, board, tab_r):
        self.b = board
        self.tab_r = tab_r
        bb = board.GetBoardEdgesBoundingBox()
        self.x0, self.y0 = mmf(bb.GetX()) - 1.0, mmf(bb.GetY()) - 1.0
        self.nx = int(round((mmf(bb.GetRight()) - self.x0 + 1.0) / RES)) + 1
        self.ny = int(round((mmf(bb.GetBottom()) - self.y0 + 1.0) / RES)) + 1
        self.nets = {}                                    # name -> id
        for nm, _ in sorted(board.GetNetsByName().items(), key=lambda kv: str(kv[0])):
            if str(nm):
                self.nets[str(nm)] = len(self.nets) + 1
        self.cu = {L: np.zeros((self.ny, self.nx), dtype=np.int32) for L in LAYERS}
        self.hard = {L: np.zeros((self.ny, self.nx), dtype=bool) for L in LAYERS}   # keep-outs: nothing may enter
        self.via_pts = []
        self.segs = []                                    # (layer, x0, y0, x1, y1, w, net)
        self.pads = {}
        self.added = []
        self._load()

    # ----------------------------------------------------------------- raster
    def cell(self, x, y):
        return int(round((x - self.x0) / RES)), int(round((y - self.y0) / RES))

    def xy(self, ix, iy):
        return self.x0 + ix * RES, self.y0 + iy * RES

    def stamp_rect(self, arr, x0, y0, x1, y1, val, grow=0.0):
        ix0 = max(0, int(math.floor((x0 - grow - self.x0) / RES)))
        ix1 = min(self.nx - 1, int(math.ceil((x1 + grow - self.x0) / RES)))
        iy0 = max(0, int(math.floor((y0 - grow - self.y0) / RES)))
        iy1 = min(self.ny - 1, int(math.ceil((y1 + grow - self.y0) / RES)))
        if ix1 >= ix0 and iy1 >= iy0:
            sl = arr[iy0:iy1 + 1, ix0:ix1 + 1]
            if val is True:
                sl[:] = True
            else:
                sl[sl == 0] = val

    def stamp_disc(self, arr, cx, cy, r, val):
        rc = int(math.ceil(r / RES)) + 1
        ix, iy = self.cell(cx, cy)
        for dy in range(-rc, rc + 1):
            for dx in range(-rc, rc + 1):
                x, y = ix + dx, iy + dy
                if 0 <= x < self.nx and 0 <= y < self.ny:
                    px, py = self.xy(x, y)
                    if math.hypot(px - cx, py - cy) <= r + 1e-9:
                        if val is True:
                            arr[y, x] = True
                        elif arr[y, x] == 0:
                            arr[y, x] = val

    def stamp_seg(self, arr, x0, y0, x1, y1, w, val):
        for px, py in seg_points(x0, y0, x1, y1, RES / 2):
            self.stamp_disc(arr, px, py, w / 2, val)

    def _load(self):
        b = self.b
        for f in b.GetFootprints():
            for p in f.Pads():
                bb = p.GetBoundingBox()
                x0, y0, x1, y1 = mmf(bb.GetX()), mmf(bb.GetY()), mmf(bb.GetRight()), mmf(bb.GetBottom())
                nm = p.GetNetname()
                nid = self.nets.get(nm, 0) or -1
                tht = p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
                layers = [L for L in LAYERS if (tht or p.IsOnLayer(LAYER_ID[L]))]
                npth = p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH
                for L in layers:
                    self.stamp_rect(self.cu[L], x0, y0, x1, y1, -1 if npth else nid)
                pos = p.GetPosition()
                self.pads[(f.GetReference(), p.GetNumber())] = (mmf(pos.x), mmf(pos.y), nm)
        tr = b.Tracks()
        for it in [tr[i] for i in range(tr.size())]:
            nid = self.nets.get(it.GetNetname(), 0) or -1
            if it.GetClass() == "PCB_VIA":
                x, y = mmf(it.GetPosition().x), mmf(it.GetPosition().y)
                self.via_pts.append((x, y))
                for L in LAYERS:
                    self.stamp_disc(self.cu[L], x, y, via_dia(it) / 2, nid)
            elif it.GetClass() == "PCB_TRACK":
                L = b.GetLayerName(it.GetLayer())
                if L in self.cu:
                    s, e = it.GetStart(), it.GetEnd()
                    self.segs.append((L, mmf(s.x), mmf(s.y), mmf(e.x), mmf(e.y), mmf(it.GetWidth()), it.GetNetname()))
                    self.stamp_seg(self.cu[L], mmf(s.x), mmf(s.y), mmf(e.x), mmf(e.y), mmf(it.GetWidth()), nid)
        for z in b.Zones():                                # rule areas: bounding boxes (conservative)
            if z.GetIsRuleArea() and z.GetDoNotAllowTracks():
                bb = z.GetBoundingBox()
                for L in LAYERS:
                    if z.IsOnLayer(LAYER_ID[L]):
                        self.stamp_rect(self.hard[L], mmf(bb.GetX()), mmf(bb.GetY()), mmf(bb.GetRight()), mmf(bb.GetBottom()), True)

    def inside_mask(self, margin):
        """Boolean map: cell centre inside the PCB outline (circle, tab, minus the slot), `margin` from the edge."""
        xs = self.x0 + np.arange(self.nx) * RES - P.CX
        ys = P.CY - (self.y0 + np.arange(self.ny) * RES)
        X, Y = np.meshgrid(xs, ys)
        hw = MO.m("V1_TAB_W") / 2.0
        circle = np.hypot(X, Y) <= MO.R_PCB - margin
        tab = (X >= MO.R_PCB - MO.m("V1_TAB_ROOT")) & (X <= self.tab_r - margin) & (np.abs(Y) <= hw - margin)
        sx0, sy0, sx1, sy1 = MO.slot_rect()
        slot = (X > sx0 - margin) & (X < sx1 + margin) & (Y > sy0 - margin) & (Y < sy1 + margin)
        ax0, ay0, ax1, ay1 = MO.antenna_strip()
        return (circle | tab) & ~slot

    # ----------------------------------------------------------------- one connection
    def route(self, net, p0, l0, p1, l1, width, sight=SIGHT, window=WINDOW):
        """Route net from p0 (layer l0) to p1 (layer l1). Returns list of ('seg', layer, a, b) / ('via', xy) or None."""
        nid = self.nets[net]
        clr = R.CLEARANCE + sight
        ok, via_ok = {}, None
        inside_t = self.inside_mask(R.EDGE_CLEARANCE + width / 2 + sight)
        inside_v = self.inside_mask(R.EDGE_CLEARANCE + R.VIA_DIA / 2 + sight)
        def disc(r):
            n = int(math.ceil(r / RES))
            yy, xx = np.mgrid[-n:n + 1, -n:n + 1]
            return (xx * xx + yy * yy) * RES * RES <= r * r + 1e-9
        for L in LAYERS:
            other = (self.cu[L] != 0) & (self.cu[L] != nid)
            dist = ndimage.distance_transform_edt(~other, sampling=RES) if other.any() else np.full((self.ny, self.nx), 1e9)
            hard_t = ndimage.binary_dilation(self.hard[L], structure=disc(width / 2 + sight)) if self.hard[L].any() else self.hard[L]
            hard_v = ndimage.binary_dilation(self.hard[L], structure=disc(R.VIA_DIA / 2 + sight)) if self.hard[L].any() else self.hard[L]
            ok[L] = (dist >= clr + width / 2) & inside_t & ~hard_t
            if L not in R.layers_allowed(net, LAYERS):          # plane layers are closed to the outer-only nets
                ok[L] = np.zeros_like(ok[L])
            vo = (dist >= clr + R.VIA_DIA / 2) & inside_v & ~hard_v
            via_ok = vo if via_ok is None else (via_ok & vo)
        hole = np.zeros((self.ny, self.nx), dtype=bool)
        for vx, vy in self.via_pts:                            # hole-to-hole: centre distance
            self.stamp_disc(hole, vx, vy, R.VIA_DRILL + R.HOLE_TO_HOLE + sight, True)
        via_ok &= ~hole
        s = self.cell(*p0) + (LAYERS.index(l0),)
        g = self.cell(*p1) + (LAYERS.index(l1),)
        for lay in (s, g):                                     # the end points are on same-net copper: always free
            ok[LAYERS[lay[2]]][lay[1], lay[0]] = True
        wx0, wx1 = sorted((s[0], g[0]))
        wy0, wy1 = sorted((s[1], g[1]))
        m = int(window / RES)
        wx0, wy0, wx1, wy1 = max(0, wx0 - m), max(0, wy0 - m), min(self.nx - 1, wx1 + m), min(self.ny - 1, wy1 + m)
        dirs = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
                (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]

        def h(x, y):
            dx, dy = abs(x - g[0]), abs(y - g[1])
            return (dx + dy) + (1.414 - 2.0) * min(dx, dy)
        openq = [(h(s[0], s[1]), 0.0, s)]
        best = {s: 0.0}
        came = {}
        while openq:
            f, cost, cur = heapq.heappop(openq)
            if cur == g:
                break
            if cost > best.get(cur, 1e18):
                continue
            x, y, li = cur
            L = LAYERS[li]
            for dx, dy, c in dirs:
                nx_, ny_ = x + dx, y + dy
                if not (wx0 <= nx_ <= wx1 and wy0 <= ny_ <= wy1) or not ok[L][ny_, nx_]:
                    continue
                if dx and dy and not (ok[L][y, nx_] and ok[L][ny_, x]):      # no corner cutting
                    continue
                st = (nx_, ny_, li)
                nc = cost + c * COST[L]
                if nc < best.get(st, 1e18):
                    best[st] = nc
                    came[st] = cur
                    heapq.heappush(openq, (nc + h(nx_, ny_), nc, st))
            if via_ok[y, x]:
                for lj, L2 in enumerate(LAYERS):
                    if lj != li and ok[L2][y, x]:
                        st = (x, y, lj)
                        nc = cost + VIA_COST
                        if nc < best.get(st, 1e18):
                            best[st] = nc
                            came[st] = cur
                            heapq.heappush(openq, (nc + h(x, y), nc, st))
        if g not in came and s != g:
            return None
        path = [g]
        while path[-1] != s:
            path.append(came[path[-1]])
        path.reverse()
        return path

    def commit(self, net, path, p0, p1, width):
        """Add tracks and vias for a path; merge collinear steps; extend to the exact end points."""
        nid = self.nets[net]
        ni = self.b.GetNetsByName()[net]
        pts = [(self.xy(x, y), LAYERS[li]) for x, y, li in path]
        pts[0] = (p0, pts[0][1])
        pts[-1] = (p1, pts[-1][1])
        i = 0
        while i < len(pts) - 1:
            (a, la), (c, lb) = pts[i], pts[i + 1]
            if la != lb:                                       # layer change at the same point: a via
                v = pcbnew.PCB_VIA(self.b)
                v.SetPosition(P.vec(*a))
                v.SetViaType(pcbnew.VIATYPE_THROUGH)
                v.SetWidth(pcbnew.PADSTACK.ALL_LAYERS, P.mm(R.VIA_DIA)) if hasattr(pcbnew, "PADSTACK") else v.SetWidth(P.mm(R.VIA_DIA))
                v.SetDrill(P.mm(R.VIA_DRILL))
                v.SetNet(ni)
                v.SetUuid(P.det_uuid("fix:via:%s:%d:%d" % (net, len(self.added), i)))
                self.b.Add(v)
                self.via_pts.append(a)
                for L in LAYERS:
                    self.stamp_disc(self.cu[L], a[0], a[1], R.VIA_DIA / 2, nid)
                self.added.append(("via", net, a))
                i += 1
                continue
            j = i + 1                                          # extend along one direction
            d = (round(c[0] - a[0], 6), round(c[1] - a[1], 6))
            while j < len(pts) - 1 and pts[j + 1][1] == la:
                e = (round(pts[j + 1][0][0] - pts[j][0][0], 6), round(pts[j + 1][0][1] - pts[j][0][1], 6))
                if e != d:
                    break
                j += 1
            end = pts[j][0]
            t = pcbnew.PCB_TRACK(self.b)
            t.SetStart(P.vec(*a))
            t.SetEnd(P.vec(*end))
            t.SetWidth(P.mm(width))
            t.SetLayer(LAYER_ID[la])
            t.SetNet(ni)
            t.SetUuid(P.det_uuid("fix:trk:%s:%d:%d" % (net, len(self.added), i)))
            self.b.Add(t)
            self.stamp_seg(self.cu[la], a[0], a[1], end[0], end[1], width, nid)
            self.segs.append((la, a[0], a[1], end[0], end[1], width, net))
            self.added.append(("track", net, la, a, end))
            i = j

    # ----------------------------------------------------------------- items of the report
    def locate(self, item, other_pt):
        """(point, layer, net) of a DRC item: a pad centre, or the nearest point of the item's track."""
        kind = parse_item(item["description"])
        if kind is None:
            return None
        pos = (item["pos"]["x"], item["pos"]["y"])
        if kind[0] == "pad":
            _, ref, num, net, lname = kind
            x, y, nm = self.pads[(ref, num)]
            lay = lname if lname in LAYERS else "F.Cu"
            return (x, y), lay, net
        if kind[0] == "track":
            _, net, lname = kind
            best, bp = 1e9, None
            for L, x0, y0, x1, y1, w, n in self.segs:
                if n != net or L != lname:
                    continue
                for px, py in seg_points(x0, y0, x1, y1, RES):
                    d = math.hypot(px - pos[0], py - pos[1])
                    if d < best:
                        best, bp = d, (px, py)
            return (bp, lname, net) if bp and best < 1.0 else None
        if kind[0] == "via":                               # a through via: any layer; the caller takes the other end's layer
            best, bp = 0.5, None
            for vx, vy in self.via_pts:
                d = math.hypot(vx - pos[0], vy - pos[1])
                if d < best:
                    best, bp = d, (vx, vy)
            return (bp, None, kind[1]) if bp else None
        return None


def run_of(seg, same, stop):
    """The chain of track segments around `seg` (same net and layer) up to junctions, vias and pads.
    same: segments of that net and layer as (item, a, b) with rounded end points; stop: rounded points that end a run."""
    pts = {}
    for it, a, b in same:
        pts.setdefault(a, []).append(it)
        pts.setdefault(b, []).append(it)
    chain, todo = [seg], [seg]
    ends = {id(it): (a, b) for it, a, b in same}
    while todo:
        cur = todo.pop()
        for p in ends[id(cur)]:
            if p in stop or len(pts[p]) != 2:
                continue
            for other in pts[p]:
                if other is not cur and all(other is not c for c in chain):
                    chain.append(other)
                    todo.append(other)
    return chain


def ripup_clearance(src, drc, dst):
    """Remove the whole track run (up to junctions, vias and pads) of one track for each `clearance` finding, so that
    `main` routes the connection again by its own rules. Prefers the net that is not GND. Returns the count of segments."""
    board = pcbnew.LoadBoard(src)
    rep = json.load(open(drc, encoding="utf-8"))
    tr = board.Tracks()
    items = [tr[i] for i in range(tr.size())]
    rnd = lambda v: round(mmf(v), 3)              # noqa: E731
    stop = set()
    for it in items:
        if it.GetClass() == "PCB_VIA":
            stop.add((rnd(it.GetPosition().x), rnd(it.GetPosition().y)))
    for f in board.GetFootprints():
        for p in f.Pads():
            stop.add((rnd(p.GetPosition().x), rnd(p.GetPosition().y)))
    removed, gone = 0, []
    for v in rep["violations"]:
        if v["type"] not in RIPUP_KINDS:
            continue
        for vi in [i for i in v["items"] if i["description"].startswith("Via")]:     # a via at fault goes with its tracks
            vx, vy = vi["pos"]["x"], vi["pos"]["y"]
            for it in items:
                if all(it is not g for g in gone) and (
                        (it.GetClass() == "PCB_VIA" and math.hypot(mmf(it.GetPosition().x) - vx, mmf(it.GetPosition().y) - vy) < 0.02)
                        or (it.GetClass() == "PCB_TRACK" and any(math.hypot(mmf(e.x) - vx, mmf(e.y) - vy) < 0.02
                                                                  for e in (it.GetStart(), it.GetEnd())))):
                    gone.append(it)
                    board.Remove(it)
                    removed += 1
        cand = [i for i in v["items"] if i["description"].startswith("Track")]
        cand.sort(key=lambda i: i["description"].startswith("Track [GND]"))
        if not cand:
            continue
        kind = parse_item(cand[0]["description"])
        same = [(it, (rnd(it.GetStart().x), rnd(it.GetStart().y)), (rnd(it.GetEnd().x), rnd(it.GetEnd().y)))
                for it in items if it.GetClass() == "PCB_TRACK" and it.GetNetname() == kind[1]
                and board.GetLayerName(it.GetLayer()) == kind[2] and all(it is not g for g in gone)]
        best, bit = 0.2, None
        for it, a, b in same:
            d = min(math.hypot(px - cand[0]["pos"]["x"], py - cand[0]["pos"]["y"])
                    for px, py in seg_points(a[0], a[1], b[0], b[1], 0.05))
            if d < best:
                best, bit = d, it
        if bit is None:
            continue
        for it in run_of(bit, same, stop):
            gone.append(it)
            board.Remove(it)
            removed += 1
    _KEEP.extend(gone)
    pcbnew.SaveBoard(dst, board)
    P.normalise_uuids(dst)
    print(json.dumps({"ripped_up_segments": removed}))
    return removed


RIPUP_KINDS = ("clearance", "copper_edge_clearance", "hole_clearance", "track_not_centered_on_via")
_KEEP = []     # removed items stay referenced (the Python wrapper would free them twice)


def reroute_nets(board, nets, tab_r):
    """Rip up every track and via of the given nets (a list; the first is routed first; never the plane nets) and route each
    net again from its pads: a minimum spanning tree over the pad centres, each link by the A* router.
    Returns (routed nets, failed nets)."""
    gone = []
    tr = board.Tracks()
    for it in [tr[i] for i in range(tr.size())]:
        if it.GetNetname() in nets:
            gone.append(it)
            board.Remove(it)
    _KEEP.extend(gone)
    fx = Fixer(board, tab_r)
    ok, bad = [], []
    for net in nets:
        pads = sorted((ref, num, x, y) for (ref, num), (x, y, n) in fx.pads.items() if n == net)
        layer = {}
        for f in board.GetFootprints():
            for p in f.Pads():
                if p.GetNetname() == net:
                    layer[(f.GetReference(), p.GetNumber())] = "B.Cu" if (p.IsOnLayer(pcbnew.B_Cu) and not p.IsOnLayer(pcbnew.F_Cu)) else "F.Cu"
        if len(pads) < 2:
            continue
        w = width_for(net, None)
        done, todo, failed = [pads[0]], pads[1:], False
        while todo:                                         # Prim: the nearest unconnected pad to the connected set
            d, a, b = min((math.hypot(p[2] - q[2], p[3] - q[3]), q, p) for q in done for p in todo)
            path = fx.route(net, (a[2], a[3]), layer[(a[0], a[1])], (b[2], b[3]), layer[(b[0], b[1])], w)
            if path is None:
                path = fx.route(net, (a[2], a[3]), layer[(a[0], a[1])], (b[2], b[3]), layer[(b[0], b[1])], w, window=2 * WINDOW)
            if path is None:
                failed = True
                break
            fx.commit(net, path, (a[2], a[3]), (b[2], b[3]), w)
            done.append(b)
            todo.remove(b)
        (bad if failed else ok).append(net)
    return ok, bad


def blockers(board, net, pairs, fx, margin=2.5, limit=5):
    """Small nets (not plane nets, not the main VBUS path) with copper near the failed connection, nearest first."""
    pts = []
    for p in pairs:
        for d in p[1:]:
            pass
    lo = [1e9, 1e9]
    hi = [-1e9, -1e9]
    for (ref, num), (x, y, n) in fx.pads.items():
        if n == net:
            lo = [min(lo[0], x), min(lo[1], y)]
            hi = [max(hi[0], x), max(hi[1], y)]
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    near = {}
    for L, x0, y0, x1, y1, w, n in fx.segs:
        if n == net or n in R.PLANE_NETS or n == R.MAIN_PATH_NET or not n:
            continue
        if min(x0, x1) - margin <= hi[0] and max(x0, x1) + margin >= lo[0] and min(y0, y1) - margin <= hi[1] and max(y0, y1) + margin >= lo[1]:
            d = math.hypot((x0 + x1) / 2 - cx, (y0 + y1) / 2 - cy)
            near[n] = min(near.get(n, 1e9), d)
    return [n for n, _ in sorted(near.items(), key=lambda kv: (kv[1], kv[0]))][:limit]


def prune_stubs(board, tol=0.01):
    """Remove track segments with a free end until none is left: an end is held when a via, a pad of the same net (its box),
    or another segment of the same net and layer (end or middle) is there. Returns the count removed."""
    total = 0
    while True:
        tr = board.Tracks()
        items = [tr[i] for i in range(tr.size())]
        vias = [(mmf(i.GetPosition().x), mmf(i.GetPosition().y)) for i in items if i.GetClass() == "PCB_VIA"]
        segs = [(i, i.GetNetname(), board.GetLayerName(i.GetLayer()),
                 (mmf(i.GetStart().x), mmf(i.GetStart().y)), (mmf(i.GetEnd().x), mmf(i.GetEnd().y)))
                for i in items if i.GetClass() == "PCB_TRACK"]
        pads = [(p.GetNetname(), mmf(p.GetBoundingBox().GetX()), mmf(p.GetBoundingBox().GetY()),
                 mmf(p.GetBoundingBox().GetRight()), mmf(p.GetBoundingBox().GetBottom()))
                for f in board.GetFootprints() for p in f.Pads()]

        def held(seg, pt):
            for vx, vy in vias:
                if math.hypot(vx - pt[0], vy - pt[1]) < 0.3:
                    return True
            for n, x0, y0, x1, y1 in pads:
                if n == seg[1] and x0 - tol <= pt[0] <= x1 + tol and y0 - tol <= pt[1] <= y1 + tol:
                    return True
            for o in segs:
                if o[0] is seg[0] or o[1] != seg[1] or o[2] != seg[2]:
                    continue
                (ax, ay), (bx, by) = o[3], o[4]
                L2 = (bx - ax) ** 2 + (by - ay) ** 2
                t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((pt[0] - ax) * (bx - ax) + (pt[1] - ay) * (by - ay)) / L2))
                if math.hypot(pt[0] - (ax + t * (bx - ax)), pt[1] - (ay + t * (by - ay))) < tol:
                    return True
            return False
        dead = [s for s in segs if not held(s, s[3]) or not held(s, s[4])]
        if not dead:
            return total
        for s in dead:
            _KEEP.append(s[0])
            board.Remove(s[0])
            total += 1


def remove_stubs(board, drc):
    """Remove the track segments that the DRC reports as `track_dangling` (a free end) and the vias it reports as
    `via_dangling` when `joins_nothing` holds. Returns the count."""
    n = 0
    tr = board.Tracks()
    items = [tr[i] for i in range(tr.size())]
    for v in drc.get("violations", []):
        if v["type"] != "track_dangling":
            continue
        for i in v["items"]:
            kind = parse_item(i["description"])
            if not kind or kind[0] != "track":
                continue
            best, bit = 0.3, None
            for it in items:
                if it.GetClass() != "PCB_TRACK" or it.GetNetname() != kind[1] or board.GetLayerName(it.GetLayer()) != kind[2]:
                    continue
                d = min(math.hypot(px - i["pos"]["x"], py - i["pos"]["y"])
                        for px, py in seg_points(mmf(it.GetStart().x), mmf(it.GetStart().y), mmf(it.GetEnd().x), mmf(it.GetEnd().y), 0.05))
                if d < best:
                    best, bit = d, it
            if bit is not None and all(bit is not g for g in _KEEP):
                _KEEP.append(bit)
                board.Remove(bit)
                n += 1
    return n


def count(drc_path, kinds):
    d = json.load(open(drc_path, encoding="utf-8"))
    return sum(1 for v in d.get("violations", []) if v["type"] in kinds) + (len(d["unconnected_items"]) if "unconnected_items" in kinds else 0)


def auto(folder, stem="stitched", profile="stitched-4l", rounds=5):
    """Rounds of clean-up in `folder` starting from <stem>.kicad_pcb and <stem> DRC json: remove the track runs at clearance
    findings, route the unconnected pairs, check again. Writes fix<N>.kicad_pcb (+ project files, drc_fix<N>.json) and
    returns the stem of the last board. Stops when no clearance finding and no unconnected item is left."""
    import shutil
    import subprocess
    here = __file__.rsplit("/", 1)[0]

    def drc(board, out):
        subprocess.run([sys.executable, here + "/kicad_strict.py", "drc", board, profile, "--out", out],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

    def aux(name):
        for ext in ("kicad_pro", "kicad_dru", "kicad_sch", "placement.json"):
            shutil.copyfile("%s/%s.%s" % (folder, stem, ext), "%s/%s.%s" % (folder, name, ext))

    cur = stem
    for n in range(1, rounds + 1):
        js = "%s/drc_%s.json" % (folder, cur)
        if count(js, ("unconnected_items", "track_dangling", "via_dangling") + RIPUP_KINDS) == 0:
            break
        src = "%s/%s.kicad_pcb" % (folder, cur)
        if count(js, RIPUP_KINDS):
            rip = "fix%dr" % n
            ripup_clearance(src, js, "%s/%s.kicad_pcb" % (folder, rip))
            aux(rip)
            drc("%s/%s.kicad_pcb" % (folder, rip), "%s/drc_%s.json" % (folder, rip))
            cur, src, js = rip, "%s/%s.kicad_pcb" % (folder, rip), "%s/drc_%s.json" % (folder, rip)
        name = "fix%d" % n
        main(src, js, "%s/%s.kicad_pcb" % (folder, name))
        aux(name)
        drc("%s/%s.kicad_pcb" % (folder, name), "%s/drc_%s.json" % (folder, name))
        cur = name
    print(json.dumps({"cleanup_final_board": cur}))
    return cur


def width_for(net, refs):
    if net == R.MAIN_PATH_NET:
        return R.BRANCH_WIDTH
    return R.NET_TRACK.get(net, R.TRACK)


def main(src, drc, dst, tab_r=None):
    board = pcbnew.LoadBoard(src)
    if tab_r is None:
        tab_r = json.load(open(src.rsplit("/", 1)[0] + "/busy_light_spike.placement.json"))["tab_r"]
    rep = json.load(open(drc, encoding="utf-8"))
    fx = Fixer(board, tab_r)
    done, failed = [], []
    for v in rep["unconnected_items"]:
        if len(v["items"]) != 2:
            continue
        a, b = (fx.locate(i, None) for i in v["items"])
        if a is None or b is None or a[2] != b[2] or a[2] not in fx.nets:
            nets_of = [k[3] if k[0] == "pad" else k[1] for k in (parse_item(i["description"]) for i in v["items"]) if k]
            failed.append([nets_of[0] if nets_of else ""] + [i["description"][:60] for i in v["items"]])
            continue
        net = a[2]
        if a[1] is None or b[1] is None:                   # a via end takes the layer of the other end
            a = (a[0], a[1] or b[1] or "F.Cu", a[2])
            b = (b[0], b[1] or a[1], b[2])
        w = width_for(net, None)
        path = fx.route(net, a[0], a[1], b[0], b[1], w)
        if path is None:                                   # second try: wider window, same clearance margin
            path = fx.route(net, a[0], a[1], b[0], b[1], w, window=2 * WINDOW)
        if path is None:
            failed.append([net] + [i["description"][:50] for i in v["items"]])
            continue
        fx.commit(net, path, a[0], b[0], w)
        done.append(net)
    rerouted = []
    if failed:                                             # rip up and reroute the small nets that still fail
        nets = sorted({f[0] for f in failed if f[0] in fx.nets and f[0] not in R.PLANE_NETS})
        for net in nets:                                   # a net, then the nets that block it; all or nothing
            pcbnew.SaveBoard(dst, board)
            for group in ([net], [net] + blockers(board, net, [f for f in failed if f[0] == net], fx)):
                ok, bad = reroute_nets(board, group, tab_r)
                if not bad:
                    rerouted.append(net)
                    break
                board = pcbnew.LoadBoard(dst)
        failed = [f for f in failed if f[0] not in rerouted]
    stubs = prune_stubs(board)
    import pcb_stitch
    stubs += pcb_stitch.remove_dangling_vias(board, rep)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(dst, board)
    P.normalise_uuids(dst)
    out = {"pairs": len(rep["unconnected_items"]), "routed": len(done), "rerouted_nets": rerouted, "failed": failed,
           "added": len(fx.added), "stubs_removed": stubs}
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "auto":
        auto(sys.argv[2])
        sys.exit(0)
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    if sys.argv[1] == "ripup":
        ripup_clearance(sys.argv[2], sys.argv[3], sys.argv[4])
        sys.exit(0)
    res = main(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(1 if res["failed"] else 0)
