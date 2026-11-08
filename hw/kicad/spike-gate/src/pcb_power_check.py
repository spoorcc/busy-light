# SPDX-License-Identifier: Apache-2.0
"""DC resistance and voltage drop of the supply nets of a routed board, and the cuts in the two plane layers.

Usage: python3 pcb_power_check.py <board.kicad_pcb> [out.json]
Method: per net, the copper of the net (tracks, pads, vias, zone fills) is rasterised at 0.1 mm per layer and turned
into a resistor network (sheet resistance of copper 0.5 mOhm/square at 35 um outer, 1.0 mOhm/square at 17.5 um inner;
via barrel 1 mOhm); the effective resistance between the source pads and the load pads follows from one sparse solve.
The drop is R x the stated current. The currents and the 50 mV target are the analyst's assumptions, not requirements.
Plane cut: the number of separate pieces and the share of the board area removed from the In1 (GND) and In2 (+5V) fills.
Not covered: temperature, copper thickness tolerance, current crowding at pads (the grid resolves 0.1 mm), AC behaviour.
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np
import pcbnew
from PIL import Image, ImageDraw
from scipy import sparse
from scipy.sparse.linalg import spsolve

RES = 0.1
RS_OUTER = 0.0005        # ohm per square, 35 um copper (rho 1.72e-8 ohm m)
RS_INNER = 0.001         # 17.5 um (half ounce inner layers assumed; the stack-up is not fixed yet)
R_VIA = 0.001
TARGET_V = 0.050
# net: (source (ref, pad or None for all pads of the ref), load (ref, pad), current A, basis)
CASES = {
    "VBUS_IC": (("J1", None), ("U7", "1"), 1.5, "J1 VBUS pins to the TPS2553 input; 1.5 A step limit, requirement text HW-010"),
    "+5V": (("U7", "6"), ("U8", "1"), 1.0, "TPS2553 output to the 3V3 regulator input; analyst assumption 1.0 A"),
    "+3V3": (("U8", "5"), ("U9", "3"), 0.5, "regulator output to the module; analyst assumption 0.5 A"),
}


def via_width(t, lid):
    try:
        return t.GetWidth(lid)
    except TypeError:                       # builds where the via width needs no layer
        return t.GetWidth()


def mm(v):
    return pcbnew.ToMM(v)


class Raster:
    def __init__(self, board):
        bb = board.GetBoardEdgesBoundingBox()
        self.x0, self.y0 = mm(bb.GetX()) - 1, mm(bb.GetY()) - 1
        self.nx = int((mm(bb.GetWidth()) + 2) / RES) + 1
        self.ny = int((mm(bb.GetHeight()) + 2) / RES) + 1

    def img(self):
        im = Image.new("L", (self.nx, self.ny), 0)
        return im, ImageDraw.Draw(im)

    def px(self, x, y):
        return ((x - self.x0) / RES, (y - self.y0) / RES)


def layer_masks(board, ras, net, layers):
    """{layer name: bool array} copper of `net`; tracks, pads and zone fills."""
    out = {}
    for L in layers:
        lid = board.GetLayerID(L)
        im, d = ras.img()
        tr = board.Tracks()
        for i in range(tr.size()):
            t = tr[i]
            if t.GetNetname() != net:
                continue
            if t.GetClass() == "PCB_VIA":
                p = ras.px(mm(t.GetPosition().x), mm(t.GetPosition().y))
                r = mm(via_width(t, lid)) / 2 / RES
                d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=1)
            elif t.GetLayer() == lid:
                a, b = ras.px(mm(t.GetStart().x), mm(t.GetStart().y)), ras.px(mm(t.GetEnd().x), mm(t.GetEnd().y))
                w = max(1, int(round(mm(t.GetWidth()) / RES)))
                d.line([a, b], fill=1, width=w)
                for p in (a, b):
                    d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=1)
        for f in board.GetFootprints():
            for p in f.Pads():
                if p.GetNetname() == net and p.IsOnLayer(lid):
                    bbx = p.GetBoundingBox()
                    d.rectangle([ras.px(mm(bbx.GetX()), mm(bbx.GetY())), ras.px(mm(bbx.GetRight()), mm(bbx.GetBottom()))], fill=1)
        for z in board.Zones():
            if z.GetIsRuleArea() or z.GetNetname() != net or not z.IsOnLayer(lid):
                continue
            polys = z.GetFilledPolysList(lid)
            for k in range(polys.OutlineCount()):
                o = polys.Outline(k)
                d.polygon([ras.px(mm(o.CPoint(j).x), mm(o.CPoint(j).y)) for j in range(o.PointCount())], fill=1)
                for h in range(polys.HoleCount(k)):
                    ho = polys.Hole(k, h)
                    d.polygon([ras.px(mm(ho.CPoint(j).x), mm(ho.CPoint(j).y)) for j in range(ho.PointCount())], fill=0)
        out[L] = np.array(im, dtype=bool)
    return out


def pad_cells(board, ras, ref, num, layers):
    cells = []
    for f in board.GetFootprints():
        if f.GetReference() != ref:
            continue
        for p in f.Pads():
            if num is None or p.GetNumber() == num:
                bbx = p.GetBoundingBox()
                x0, y0 = ras.px(mm(bbx.GetX()), mm(bbx.GetY()))
                x1, y1 = ras.px(mm(bbx.GetRight()), mm(bbx.GetBottom()))
                for L in layers:
                    if p.IsOnLayer(board.GetLayerID(L)):
                        cells += [(L, int(round((x0 + x1) / 2)), int(round((y0 + y1) / 2)))]
    return cells


def effective_resistance(board, ras, net, src, dst, layers):
    masks = layer_masks(board, ras, net, layers)
    idx, n = {}, 0
    for L in layers:
        ys, xs = np.nonzero(masks[L])
        for y, x in zip(ys, xs):
            idx[(L, x, y)] = n
            n += 1
    rows, cols, vals = [], [], []

    def link(a, b, g):
        rows.extend((a, b, a, b)); cols.extend((a, b, b, a)); vals.extend((g, g, -g, -g))
    for L in layers:
        g = 1.0 / (RS_INNER if "In" in L else RS_OUTER)           # square cells: conductance = 1 / Rs
        ys, xs = np.nonzero(masks[L])
        for y, x in zip(ys, xs):
            a = idx[(L, x, y)]
            for dx, dy in ((1, 0), (0, 1)):
                b = idx.get((L, x + dx, y + dy))
                if b is not None:
                    link(a, b, g)
    tr = board.Tracks()
    for i in range(tr.size()):
        t = tr[i]
        if t.GetClass() == "PCB_VIA" and t.GetNetname() == net:
            x, y = ras.px(mm(t.GetPosition().x), mm(t.GetPosition().y))
            ids = [idx[(L, int(round(x)), int(round(y)))] for L in layers if (L, int(round(x)), int(round(y))) in idx]
            for a, b in zip(ids, ids[1:]):
                link(a, b, 1.0 / R_VIA)
    s = [idx[c] for c in pad_cells(board, ras, *src, layers) if c in idx]
    t_ = [idx[c] for c in pad_cells(board, ras, *dst, layers) if c in idx]
    if not s or not t_ or n == 0:
        return None
    G = sparse.coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsr()
    from scipy.sparse.csgraph import connected_components
    _, lab = connected_components(abs(G), directed=False)
    if not set(lab[s]) & set(lab[t_]):
        return float("inf")                                       # the pads are not joined by the copper of the net
    inc = np.isin(lab, list(set(lab[s]) | set(lab[t_])))
    new = -np.ones(n, dtype=int)
    new[inc] = np.arange(int(inc.sum()))
    G = G[inc][:, inc]
    s, t_, n = [int(new[a]) for a in s if inc[a]], [int(new[a]) for a in t_ if inc[a]], int(inc.sum())
    g_short = 1e6                                                 # source and sink pads held at a node each
    extra_r, extra_c, extra_v = [], [], []
    S, T = n, n + 1
    for a in s:
        extra_r += [a, S, a, S]; extra_c += [a, S, S, a]; extra_v += [g_short, g_short, -g_short, -g_short]
    for a in t_:
        extra_r += [a, T, a, T]; extra_c += [a, T, T, a]; extra_v += [g_short, g_short, -g_short, -g_short]
    G = sparse.coo_matrix((np.concatenate([G.tocoo().data, extra_v]),
                           (np.concatenate([G.tocoo().row, extra_r]), np.concatenate([G.tocoo().col, extra_c]))),
                          shape=(n + 2, n + 2)).tocsc()
    # ground the sink, inject 1 A at the source: R = voltage at the source
    keep = [i for i in range(n + 2) if i != T]
    Gk = G[keep][:, keep]
    rhs = np.zeros(n + 1)
    rhs[S] = 1.0
    try:
        v = spsolve(Gk.tocsc(), rhs)
    except Exception:
        return None
    r = float(v[S])
    return r if r > 0 else None


def plane_cuts(board, net, layer):
    """(pieces, removed share of the board area) of the filled zone of `net` on `layer`."""
    lid = board.GetLayerID(layer)
    z = next((z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetname() == net and z.IsOnLayer(lid)), None)
    if z is None:
        return None
    polys = z.GetFilledPolysList(lid)
    pieces = polys.OutlineCount()
    area = 0.0
    for k in range(pieces):
        o = polys.Outline(k)
        pts = [(mm(o.CPoint(j).x), mm(o.CPoint(j).y)) for j in range(o.PointCount())]
        a = abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))) / 2
        for h in range(polys.HoleCount(k)):
            ho = polys.Hole(k, h)
            hp = [(mm(ho.CPoint(j).x), mm(ho.CPoint(j).y)) for j in range(ho.PointCount())]
            a -= abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(hp, hp[1:] + hp[:1]))) / 2
        area += a
    outline = z.Outline().Outline(0)
    full = abs(sum(
        (mm(outline.CPoint(j).x) * mm(outline.CPoint((j + 1) % outline.PointCount()).y)
         - mm(outline.CPoint((j + 1) % outline.PointCount()).x) * mm(outline.CPoint(j).y))
        for j in range(outline.PointCount()))) / 2 if outline.PointCount() else 0
    return pieces, (1 - area / full) if full else None


def main(path, out=None):
    board = pcbnew.LoadBoard(path)
    ras = Raster(board)
    layers = [board.GetLayerName(l) for l in board.GetEnabledLayers().CuStack()]
    res = {"nets": {}, "planes": {}}
    for net, (src, dst, amps, basis) in CASES.items():
        r = effective_resistance(board, ras, net, src, dst, layers)
        res["nets"][net] = {"resistance_mohm": None if r is None else round(r * 1000, 2), "current_a": amps,
                            "drop_mv": None if r is None else round(r * amps * 1000, 1), "basis": basis,
                            "within_50mv": None if r is None else r * amps <= TARGET_V}
    for net, layer in (("GND", "In1.Cu"), ("+5V", "In2.Cu")):
        c = plane_cuts(board, net, layer)
        res["planes"][layer] = {"net": net, "pieces": None if c is None else c[0],
                                "removed_share": None if c is None or c[1] is None else round(c[1], 3)}
    for L in ("In1.Cu", "In2.Cu"):                              # tracks of other nets on the plane layers
        lid = board.GetLayerID(L)
        per = {}
        tr = board.Tracks()
        for i in range(tr.size()):
            t = tr[i]
            if t.GetClass() != "PCB_VIA" and t.GetLayer() == lid:
                per[t.GetNetname()] = per.get(t.GetNetname(), 0.0) + mm(t.GetLength())
        res["planes"][L]["track_length_mm_by_net"] = {k: round(v, 1) for k, v in sorted(per.items())}
    text = json.dumps(res, indent=1, sort_keys=True)
    print(text)
    if out:
        open(out, "w", encoding="utf-8").write(text + "\n")
    return res


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
