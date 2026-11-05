# SPDX-License-Identifier: Apache-2.0
"""Spike: small deterministic grid router (fallback when Freerouting cannot be run).

Reads the placed board written by pcb_full.py, routes every net with an A* search on a 0.05 mm grid
(two copper layers, through vias), writes tracks and vias into the board and saves it.
Rules: clearance, track width and via size are the ones in pcb_full.py. Clearance is checked on a raster of the
other nets' copper with an exact Euclidean distance transform plus half a grid step of margin, so the result
is conservative; the real check is `kicad-cli pcb drc`, which this script does not replace.

GND: the back layer carries a GND pour; every SMD GND pad is connected to the pour with a short track and a via.
Power nets are searched at 0.25 mm and widened afterwards where the copper around the path allows it (IPC-2221
width for 1.5 A / 2 A is in pcb_full.py), so the width falls back to 0.25 mm near fine-pitch pads (neck-down).

Usage: python3 route_grid.py <in.kicad_pcb> <out.kicad_pcb> [report.json]
Deterministic: no random numbers, nets in a fixed order, ties broken by index.
"""
import heapq
import json
import math
import sys
import time

import numpy as np
import pcbnew
from scipy import ndimage

import pcb_full as P

RES = 0.05                # mm grid
VIA_COST = 50             # grid steps
BACK_FACTOR = 1.3         # cost multiplier on the back layer (keeps signals on top)
SEARCH_W_POWER = 0.25     # mm, search width of the wide nets
MARGIN = 0.03             # mm, raster margin
FINE = ('U1',)            # fine-pitch parts: pad edges on the grid, no extra raster margin
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
COSTS = [1.0, 1.0, 1.0, 1.0, math.sqrt(2), math.sqrt(2), math.sqrt(2), math.sqrt(2)]


def mmf(v):
    return pcbnew.ToMM(v)


class Router:
    def __init__(self, board):
        self.b = board
        self.nx = int(round(P.BOARD_W / RES)) + 1
        self.ny = int(round(P.BOARD_H / RES)) + 1
        self.n = self.nx * self.ny
        self.cu = [np.zeros((self.ny, self.nx), dtype=np.int32) for _ in range(2)]
        self.netid = {}
        self.netname = {}
        for nm, ni in sorted(board.GetNetsByName().items(), key=lambda kv: str(kv[0])):
            if str(nm) == "":
                continue
            self.netid[str(nm)] = len(self.netid) + 1
            self.netname[self.netid[str(nm)]] = str(nm)
        self.pads = {}          # net id -> list of dicts
        self.tracks = []        # (net id, layer, x0, y0, x1, y1, w)
        self.vias = []          # (net id, x, y)
        self.failed = []
        self.margin = MARGIN
        self._load_pads()
        self.fine_nets = {p['net'] for lst in self.pads.values() for p in lst if p['ref'] in FINE}
        self._keepouts()

    # ---------------------------------------------------------------- raster helpers
    def cell(self, x, y):
        return int(round(x / RES)), int(round(y / RES))

    def _rect(self, layer, x0, y0, x1, y1, val, grow=0.0):
        ix0 = max(0, int(math.ceil((x0 - grow) / RES - 1e-9)))
        ix1 = min(self.nx - 1, int(math.floor((x1 + grow) / RES + 1e-9)))
        iy0 = max(0, int(math.ceil((y0 - grow) / RES - 1e-9)))
        iy1 = min(self.ny - 1, int(math.floor((y1 + grow) / RES + 1e-9)))
        if ix1 >= ix0 and iy1 >= iy0:
            sl = self.cu[layer][iy0:iy1 + 1, ix0:ix1 + 1]
            if val == -1:
                sl[:] = -1
            else:
                sl[sl == 0] = val
        return ix0, iy0, ix1, iy1

    def _load_pads(self):
        for fp in self.b.GetFootprints():
            for p in fp.Pads():
                bb = p.GetBoundingBox()
                x0, y0, x1, y1 = mmf(bb.GetX()), mmf(bb.GetY()), mmf(bb.GetRight()), mmf(bb.GetBottom())
                pos = p.GetPosition()
                layers = [0, 1] if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) else [0]
                nm = p.GetNetname()
                nid = self.netid.get(nm, 0)
                npth = p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH
                if nid == 0:
                    # copper without a net (or a hole): hard obstacle for everybody
                    for L in layers:
                        self._rect(L, x0, y0, x1, y1, -1, grow=0.25 if npth else 0.0)
                    continue
                d = {"ref": fp.GetReference(), "num": p.GetNumber(), "net": nid, "layers": layers,
                     "bbox": (x0, y0, x1, y1), "cx": mmf(pos.x), "cy": mmf(pos.y),
                     "tht": len(layers) == 2}
                self.pads.setdefault(nid, []).append(d)
                for L in layers:
                    self._rect(L, x0, y0, x1, y1, nid, grow=0.0 if fp.GetReference() in FINE else RES / 2)

    def _keepouts(self):
        for fp in self.b.GetFootprints():
            for z in fp.Zones():
                if z.GetIsRuleArea() and z.GetDoNotAllowTracks():
                    bb = z.GetBoundingBox()
                    for L in (0, 1):
                        self._rect(L, mmf(bb.GetX()), mmf(bb.GetY()), mmf(bb.GetRight()), mmf(bb.GetBottom()), -1)

    def stamp_disc(self, layer, cx, cy, r, nid):
        ix, iy = self.cell(cx, cy)
        rc = int(math.ceil(r / RES))
        for dy in range(-rc, rc + 1):
            for dx in range(-rc, rc + 1):
                if (dx * RES) ** 2 + (dy * RES) ** 2 <= r * r + 1e-9:
                    x, y = ix + dx, iy + dy
                    if 0 <= x < self.nx and 0 <= y < self.ny and self.cu[layer][y, x] == 0:
                        self.cu[layer][y, x] = nid

    def stamp_seg(self, layer, x0, y0, x1, y1, w, nid):
        n = max(1, int(math.ceil(math.hypot(x1 - x0, y1 - y0) / (RES / 2))))
        for i in range(n + 1):
            t = i / n
            self.stamp_disc(layer, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, w / 2, nid)

    # ---------------------------------------------------------------- per-net maps
    def maps(self, nid, w):
        """ok_track[L] (uint8 flat), dist[L] (mm to other copper), ok_via (flat)."""
        dist = []
        for L in (0, 1):
            other = (self.cu[L] != 0) & (self.cu[L] != nid)
            dist.append(ndimage.distance_transform_edt(~other, sampling=RES) if other.any()
                        else np.full((self.ny, self.nx), 1e9))
        yy, xx = np.mgrid[0:self.ny, 0:self.nx]
        edge = np.minimum(np.minimum(xx, P.BOARD_W / RES - xx), np.minimum(yy, P.BOARD_H / RES - yy)) * RES
        c = P.CLEARANCE
        ok = []
        for L in (0, 1):
            m = (dist[L] >= c + w / 2 + self.margin) & (edge >= P.EDGE_CLEARANCE + w / 2 + self.margin)
            # own pad copper is always passable (a track leaves its own pad)
            m |= (self.cu[L] == nid)
            ok.append(m)
        okv = (dist[0] >= c + P.VIA_DIA / 2 + MARGIN) & (dist[1] >= c + P.VIA_DIA / 2 + MARGIN) \
            & (edge >= P.EDGE_CLEARANCE + P.VIA_DIA / 2 + MARGIN)
        # a via may not sit on a pad copper of any net (no via-in-pad)
        okv &= (self.cu[0] == 0) & (self.cu[1] == 0)
        return ([np.ascontiguousarray(m).astype(np.uint8).ravel().tobytes() for m in ok],
                dist, np.ascontiguousarray(okv).astype(np.uint8).ravel().tobytes())

    # ---------------------------------------------------------------- search
    def astar(self, ok, okv, starts, tree, target_xy, win):
        """ok: [bytes,bytes]; starts: [(L,ix,iy)]; tree: [bytes,bytes] of goal cells.
        win: (ix0,iy0,ix1,iy1) search window. Returns list of (L,ix,iy) from start to goal, or None."""
        nx = self.nx
        n = self.n
        ix0, iy0, ix1, iy1 = win
        tx, ty = target_xy
        g = {}
        parent = {}
        pdir = {}
        heap = []
        cnt = 0
        for L, x, y in starts:
            k = L * n + y * nx + x
            g[k] = 0.0
            pdir[k] = -1
            h = self.h(x, y, tx, ty)
            heapq.heappush(heap, (h, cnt, k))
            cnt += 1
        expanded = 0
        while heap:
            f, _, k = heapq.heappop(heap)
            gk = g[k]
            L, r = divmod(k, n)
            y, x = divmod(r, nx)
            if f - self.h(x, y, tx, ty) > gk + 1e-9:
                continue   # stale entry
            if tree[L][r] and parent.get(k) is not None:
                path = []
                while k is not None:
                    L2, r2 = divmod(k, n)
                    y2, x2 = divmod(r2, nx)
                    path.append((L2, x2, y2))
                    k = parent.get(k)
                return path[::-1]
            expanded += 1
            if expanded > 6000000:
                return None
            okL = ok[L]
            mult = 1.0 if L == 0 else BACK_FACTOR
            d0 = pdir.get(k, -1)
            for di in range(8):
                dx, dy = DIRS[di]
                x2, y2 = x + dx, y + dy
                if x2 < ix0 or x2 > ix1 or y2 < iy0 or y2 > iy1:
                    continue
                r2 = y2 * nx + x2
                if not okL[r2]:
                    continue
                if di >= 4 and not (okL[y * nx + x2] and okL[y2 * nx + x]):
                    continue
                c = COSTS[di] * mult + (0.02 if (d0 != -1 and d0 != di) else 0.0)
                k2 = L * n + r2
                ng = gk + c
                if ng < g.get(k2, 1e18):
                    g[k2] = ng
                    parent[k2] = k
                    pdir[k2] = di
                    heapq.heappush(heap, (ng + self.h(x2, y2, tx, ty), cnt, k2))
                    cnt += 1
            if okv[r]:
                L2 = 1 - L
                if ok[L2][r]:
                    k2 = L2 * n + r
                    ng = gk + VIA_COST
                    if ng < g.get(k2, 1e18):
                        g[k2] = ng
                        parent[k2] = k
                        pdir[k2] = -1
                        heapq.heappush(heap, (ng + self.h(x, y, tx, ty), cnt, k2))
                        cnt += 1
        return None

    @staticmethod
    def h(x, y, tx, ty):
        dx, dy = abs(x - tx), abs(y - ty)
        return (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)

    def window(self, pts, margin_mm):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        m = int(margin_mm / RES)
        return (max(0, min(xs) - m), max(0, min(ys) - m), min(self.nx - 1, max(xs) + m), min(self.ny - 1, max(ys) + m))

    # ---------------------------------------------------------------- one net
    def route_net(self, nid, width, star=None):
        pads = self.pads.get(nid, [])
        if len(pads) < 2:
            return
        if nid in self.fine_nets and width <= P.TRACK:
            width = 0.15
            self.margin = 0.0
        w_search = min(width, SEARCH_W_POWER) if width > P.TRACK else width
        ok, dist, okv = self.maps(nid, w_search)
        okw = None
        if width > w_search:
            okw = [(dist[L] >= P.CLEARANCE + width / 2 + self.margin) for L in (0, 1)]
        tree = [bytearray(self.n), bytearray(self.n)]

        def add_pad_to_tree(pd):
            x0, y0, x1, y1 = pd["bbox"]
            for L in pd["layers"]:
                ix0, iy0 = int(math.ceil(x0 / RES - 1e-9)), int(math.ceil(y0 / RES - 1e-9))
                ix1, iy1 = int(math.floor(x1 / RES + 1e-9)), int(math.floor(y1 / RES + 1e-9))
                for iy in range(max(0, iy0), min(self.ny - 1, iy1) + 1):
                    base = iy * self.nx
                    for ix in range(max(0, ix0), min(self.nx - 1, ix1) + 1):
                        tree[L][base + ix] = 1

        # start with the pad closest to the centroid of the pads
        cx = sum(p["cx"] for p in pads) / len(pads)
        cy = sum(p["cy"] for p in pads) / len(pads)
        pads = sorted(pads, key=lambda p: (round(math.hypot(p["cx"] - cx, p["cy"] - cy), 6), p["ref"], p["num"]))
        remaining = pads[1:]
        connected = [pads[0]]
        if star:
            centre = [p for p in pads if (p["ref"], p["num"]) == star][0]
            connected = [centre]
            remaining = [p for p in pads if p is not centre]
        add_pad_to_tree(connected[0])
        while remaining:
            remaining.sort(key=lambda p: (min(abs(p["cx"] - q["cx"]) + abs(p["cy"] - q["cy"]) for q in connected),
                                          p["ref"], p["num"]))
            pd = remaining.pop(0)
            q = min(connected, key=lambda q: (abs(pd["cx"] - q["cx"]) + abs(pd["cy"] - q["cy"]), q["ref"], q["num"]))
            sx, sy = self.cell(pd["cx"], pd["cy"])
            starts = [(L, sx, sy) for L in pd["layers"]]
            tgt = self.cell(q["cx"], q["cy"])
            path = None
            for mg in (12.0, 40.0, 400.0):
                win = self.window([(sx, sy), tgt] + [self.cell(p["cx"], p["cy"]) for p in connected], mg)
                path = self.astar(ok, okv, starts, tree, tgt, win)
                if path:
                    break
            if not path:
                self.failed.append((self.netname[nid], pd["ref"] + "." + pd["num"]))
                continue
            self.commit(nid, path, width, w_search, okw, tree, extend=not star)
            if not star:
                add_pad_to_tree(pd)
                connected.append(pd)
        self.margin = MARGIN

    def commit(self, nid, path, width, w_search, okw, tree, extend=True):
        """Turn a cell path into tracks and vias, widen where allowed, stamp copper, extend the goal tree."""
        wid = []
        for L, x, y in path:
            if okw is not None and okw[L][y, x]:
                wid.append(width)
            else:
                wid.append(w_search)
        i = 0
        segs = []
        while i < len(path) - 1:
            L, x, y = path[i]
            L2, x2, y2 = path[i + 1]
            if L != L2:
                self.vias.append((nid, x * RES, y * RES))
                self.stamp_disc(0, x * RES, y * RES, P.VIA_DIA / 2, nid)
                self.stamp_disc(1, x * RES, y * RES, P.VIA_DIA / 2, nid)
                i += 1
                continue
            # extend the run along the same direction, layer and width
            d = (x2 - x, y2 - y)
            w = min(wid[i], wid[i + 1])
            j = i + 1
            while j < len(path) - 1:
                L3, x3, y3 = path[j + 1]
                if L3 != L or (x3 - path[j][1], y3 - path[j][2]) != d or min(wid[j], wid[j + 1]) != w:
                    break
                j += 1
            segs.append((L, path[i][1], path[i][2], path[j][1], path[j][2], w))
            i = j
        for L, ax, ay, bx, by, w in segs:
            self.tracks.append((nid, L, ax * RES, ay * RES, bx * RES, by * RES, w))
            self.stamp_seg(L, ax * RES, ay * RES, bx * RES, by * RES, w, nid)
        if extend:
            for L, x, y in path:
                tree[L][y * self.nx + x] = 1

    def retry(self, failed):
        """Second pass for connections that failed: no raster margin, goal = any copper of the same net."""
        again = []
        self.margin = 0.0
        for name, what in failed:
            nid = self.netid[name]
            ref, num = what.split()[0].rsplit(".", 1)
            pd = [p for p in self.pads[nid] if p["ref"] == ref and p["num"] == num][0]
            width = P.NET_TRACK.get(name, P.TRACK)
            if name in self.fine_nets:
                width = 0.15
            ok, dist, okv = self.maps(nid, width)
            tree = [bytearray(((self.cu[L] == nid).ravel()).astype(np.uint8).tobytes()) for L in (0, 1)]
            x0, y0, x1, y1 = pd["bbox"]
            for L in pd["layers"]:     # the pad itself is not a goal
                ix0, iy0 = int(math.ceil(x0 / RES - 1e-9)), int(math.ceil(y0 / RES - 1e-9))
                ix1, iy1 = int(math.floor(x1 / RES + 1e-9)), int(math.floor(y1 / RES + 1e-9))
                for iy in range(iy0, iy1 + 1):
                    for ix in range(ix0, ix1 + 1):
                        tree[L][iy * self.nx + ix] = 0
            others = [p for p in self.pads[nid] if p is not pd]
            q = min(others, key=lambda q: (abs(pd["cx"] - q["cx"]) + abs(pd["cy"] - q["cy"]), q["ref"], q["num"]))
            sx, sy = self.cell(pd["cx"], pd["cy"])
            tgt = self.cell(q["cx"], q["cy"])
            path = None
            for mg in (12.0, 400.0):
                win = self.window([(sx, sy), tgt], mg)
                path = self.astar(ok, okv, [(L, sx, sy) for L in pd["layers"]], tree, tgt, win)
                if path:
                    break
            if path:
                self.commit(nid, path, width, width, None, tree)
            else:
                again.append((name, what))
        self.margin = MARGIN
        self.failed = again

    # ---------------------------------------------------------------- GND vias
    def gnd_vias(self, nid):
        ok, dist, okv = self.maps(nid, P.TRACK)
        none_tree = [bytearray(self.n), bytearray(self.n)]
        for pd in sorted(self.pads.get(nid, []), key=lambda p: (p["ref"], p["num"])):
            if pd["tht"]:
                continue   # through-hole pad meets the back pour directly
            sx, sy = self.cell(pd["cx"], pd["cy"])
            x0, y0, x1, y1 = pd["bbox"]
            ex0, ey0, ex1, ey1 = [int(round(v / RES)) for v in (x0 - 0.3, y0 - 0.3, x1 + 0.3, y1 + 0.3)]
            goal = [bytearray(self.n), bytearray(self.n)]
            win = self.window([(sx, sy)], 6.0)
            for iy in range(win[1], win[3] + 1):
                for ix in range(win[0], win[2] + 1):
                    r = iy * self.nx + ix
                    if okv[r] and not (ex0 <= ix <= ex1 and ey0 <= iy <= ey1) and ok[0][r]:
                        goal[1][r] = 1      # via position; the path ends there on the back layer after the via
            # search on the front layer to a via-legal cell, then place the via
            path = self.astar_to_via(ok, okv, (0, sx, sy), goal, win)
            if not path:
                self.failed.append(("GND", pd["ref"] + "." + pd["num"] + " (via)"))
                continue
            L, vx, vy = path[-1]
            path = [(0, x, y) for (_, x, y) in path[:-1]] + [(0, vx, vy)]
            wid = [P.TRACK] * len(path)
            segs = []
            for i in range(len(path) - 1):
                segs.append((0, path[i][1], path[i][2], path[i + 1][1], path[i + 1][2], P.TRACK))
            # merge collinear
            merged = []
            for s in segs:
                if merged and merged[-1][0] == s[0] and merged[-1][5] == s[5]:
                    a = merged[-1]
                    d1 = (a[3] - a[1], a[4] - a[2])
                    d2 = (s[3] - s[1], s[4] - s[2])
                    if d1[0] * d2[1] - d1[1] * d2[0] == 0 and d1[0] * d2[0] + d1[1] * d2[1] > 0:
                        merged[-1] = (a[0], a[1], a[2], s[3], s[4], a[5])
                        continue
                merged.append(s)
            for L2, ax, ay, bx, by, w in merged:
                if (ax, ay) != (bx, by):
                    self.tracks.append((nid, L2, ax * RES, ay * RES, bx * RES, by * RES, w))
                    self.stamp_seg(L2, ax * RES, ay * RES, bx * RES, by * RES, w, nid)
            self.vias.append((nid, vx * RES, vy * RES))
            self.stamp_disc(0, vx * RES, vy * RES, P.VIA_DIA / 2, nid)
            self.stamp_disc(1, vx * RES, vy * RES, P.VIA_DIA / 2, nid)
            # refresh maps for the next pad (own copper stays passable, others see the new copper)
            ok, dist, okv = self.maps(nid, P.TRACK)

    def astar_to_via(self, ok, okv, start, goal, win):
        """Dijkstra on the front layer from `start` to the nearest cell flagged in goal[1] (via-legal)."""
        nx, n = self.nx, self.n
        ix0, iy0, ix1, iy1 = win
        L0, sx, sy = start
        k0 = sy * nx + sx
        g = {k0: 0.0}
        parent = {k0: None}
        heap = [(0.0, 0, k0)]
        cnt = 1
        okL = ok[0]
        while heap:
            gk, _, k = heapq.heappop(heap)
            if gk > g[k] + 1e-9:
                continue
            y, x = divmod(k, nx)
            if goal[1][k]:
                path = []
                while k is not None:
                    yy, xx = divmod(k, nx)
                    path.append((0, xx, yy))
                    k = parent[k]
                path = path[::-1]
                return path
            for di in range(8):
                dx, dy = DIRS[di]
                x2, y2 = x + dx, y + dy
                if x2 < ix0 or x2 > ix1 or y2 < iy0 or y2 > iy1:
                    continue
                k2 = y2 * nx + x2
                if not okL[k2]:
                    continue
                if di >= 4 and not (okL[y * nx + x2] and okL[y2 * nx + x]):
                    continue
                ng = gk + COSTS[di]
                if ng < g.get(k2, 1e18):
                    g[k2] = ng
                    parent[k2] = k
                    heapq.heappush(heap, (ng, cnt, k2))
                    cnt += 1
        return None

    # ---------------------------------------------------------------- write back
    def write(self):
        items = {n: self.b.FindNet(name) for n, name in self.netname.items()}
        for i, (nid, L, x0, y0, x1, y1, w) in enumerate(self.tracks):
            t = pcbnew.PCB_TRACK(self.b)
            t.SetUuid(P.det_uuid("trk:%d" % i))
            t.SetStart(P.vec(x0, y0))
            t.SetEnd(P.vec(x1, y1))
            t.SetWidth(P.mm(w))
            t.SetLayer(pcbnew.F_Cu if L == 0 else pcbnew.B_Cu)
            t.SetNet(items[nid])
            self.b.Add(t)
        for i, (nid, x, y) in enumerate(self.vias):
            v = pcbnew.PCB_VIA(self.b)
            v.SetUuid(P.det_uuid("via:%d" % i))
            v.SetPosition(P.vec(x, y))
            v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetWidth(P.mm(P.VIA_DIA))
            v.SetDrill(P.mm(P.VIA_DRILL))
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            v.SetNet(items[nid])
            self.b.Add(v)


def net_order(r):
    names = sorted(r.netid)
    first = [n for n in ("VBUS_IC", "+5V", "+3V3") if n in r.netid]
    crit = [n for n in ("/ILIM", "/CC1", "/CC2", "/USB_DP", "/USB_DN", "/SUP_CT", "/HOLD_OK", "/ILIM_STEP3_EN",
                        "/ILIM_STEP2_EN", "/LED_DATA") if n in r.netid]
    rest = []
    for n in names:
        if n in first or n in crit or n == "GND":
            continue
        pads = r.pads.get(r.netid[n], [])
        if len(pads) < 2:
            continue
        xs = [p["cx"] for p in pads]
        ys = [p["cy"] for p in pads]
        rest.append(((max(xs) - min(xs)) + (max(ys) - min(ys)), n))
    return first, crit, [n for _, n in sorted(rest)]


def main(src, dst, report=None):
    t0 = time.time()
    board = pcbnew.LoadBoard(src)
    r = Router(board)
    first, crit, rest = net_order(r)
    gnd = r.netid.get("GND")
    log = []
    for n in first:
        r.route_net(r.netid[n], P.NET_WIDTH.get(n, P.TRACK))
        log.append((n, round(time.time() - t0, 1)))
    if gnd:
        r.gnd_vias(gnd)
        log.append(("GND vias", round(time.time() - t0, 1)))
    for n in crit + rest:
        r.route_net(r.netid[n], P.NET_TRACK.get(n, P.TRACK), P.STAR.get(n))
        log.append((n, round(time.time() - t0, 1)))
    if r.failed:
        r.retry(list(r.failed))
        log.append(("retry", round(time.time() - t0, 1)))
    r.write()
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(dst, board)
    P.normalise_uuids(dst)
    rep = {"tracks": len(r.tracks), "vias": len(r.vias), "failed": r.failed,
           "track_length_mm": round(sum(math.hypot(t[4] - t[2], t[5] - t[3]) for t in r.tracks), 1),
           "seconds": round(time.time() - t0, 1), "grid_mm": RES}
    if report:
        json.dump(rep, open(report, "w"), indent=2, sort_keys=True)
    print(json.dumps(rep, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], *(sys.argv[3:4]))
