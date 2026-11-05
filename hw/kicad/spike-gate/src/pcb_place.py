# SPDX-License-Identifier: Apache-2.0
"""Spike: deterministic simulated-annealing placer for the movable parts (pure Python, no KiCad needed).

Cost = half-perimeter wire length over the nets + a penalty on overlapping rectangles (same side) + rejection of
moves that leave the allowed region. Moves: shift, rotate by 90 degrees, flip to the other side. The random
generator is seeded, so the result is the same on every run with the same inputs.
Exploratory: pad positions are approximated by the rotated pad offsets; the real positions are checked
by the board tests afterwards.
"""
import math
import random


def rot_xy(dx, dy, rot):
    """KiCad rotation by `rot` degrees (multiples of 90), counter-clockwise on screen with y down."""
    r = rot % 360
    if r == 0:
        return dx, dy
    if r == 90:
        return dy, -dx
    if r == 180:
        return -dx, -dy
    return -dy, dx


class Placer:
    def __init__(self, parts, nets, fixed_pins, fixed_rects, region_ok, margin=0.3, seed=1):
        """parts: {ref: {'w','h','pads':{num:(dx,dy) from the rect centre}, 'sides':'FB'|'F'|'B'}}.
        nets: {name: [(ref, pad)]}; fixed_pins: {(ref, pad): (x, y)}; fixed_rects: [(side, x0, y0, x1, y1)].
        region_ok(side, x0, y0, x1, y1) -> bool."""
        self.parts, self.nets, self.fixed_pins = parts, nets, fixed_pins
        self.fixed_rects, self.region_ok, self.margin = fixed_rects, region_ok, margin
        self.rng = random.Random(seed)
        self.refs = sorted(parts)
        self.state = {}
        self.net_of = {}
        for n, nodes in nets.items():
            for ref, pad in nodes:
                self.net_of.setdefault(ref, set()).add(n)
        self.net_of = {r: sorted(v) for r, v in self.net_of.items()}      # fixed order: the float sums must not depend on hash seeds

    # ---- geometry
    def rect(self, ref, st):
        x, y, rot, side = st
        p = self.parts[ref]
        w, h = (p["w"], p["h"]) if rot % 180 == 0 else (p["h"], p["w"])
        return (x - w / 2 - self.margin, y - h / 2 - self.margin, x + w / 2 + self.margin, y + h / 2 + self.margin)

    def pad_xy(self, ref, pad, st):
        x, y, rot, side = st
        dx, dy = self.parts[ref]["pads"][pad]
        if side == "B":
            dx = -dx
        rx, ry = rot_xy(dx, dy, rot)
        return x + rx, y + ry

    def net_hpwl(self, name):
        xs, ys = [], []
        for ref, pad in self.nets[name]:
            if ref in self.state:
                px, py = self.pad_xy(ref, pad, self.state[ref])
            elif (ref, pad) in self.fixed_pins:
                px, py = self.fixed_pins[(ref, pad)]
            else:
                continue
            xs.append(px)
            ys.append(py)
        if len(xs) < 2:
            return 0.0
        return (max(xs) - min(xs)) + (max(ys) - min(ys))

    @staticmethod
    def overlap(a, b):
        w = min(a[2], b[2]) - max(a[0], b[0])
        h = min(a[3], b[3]) - max(a[1], b[1])
        return w * h if w > 0 and h > 0 else 0.0

    def part_overlap(self, ref, st, skip=None):
        r = self.rect(ref, st)
        side = st[3]
        tot = 0.0
        for o in self.refs:
            if o == ref or o == skip or o not in self.state:
                continue
            ost = self.state[o]
            if ost[3] != side:
                continue
            tot += self.overlap(r, self.rect(o, ost))
        for fs, x0, y0, x1, y1 in self.fixed_rects:
            if fs == side:
                tot += self.overlap(r, (x0, y0, x1, y1))
        return tot

    def legal(self, ref, st):
        r = self.rect(ref, st)
        return st[3] in self.parts[ref].get("sides", "FB") and self.region_ok(st[3], *r)

    def cost_of(self, ref, st, pen):
        c = 0.0
        for n in self.net_of.get(ref, ()):
            c += self.net_hpwl(n)
        return c + pen * self.part_overlap(ref, st)

    # ---- annealing
    def init_state(self):
        for ref in self.refs:
            sides = self.parts[ref].get("sides", "FB")
            for _ in range(5000):
                st = (self.rng.uniform(-17, 30), self.rng.uniform(-17, 17), 90 * self.rng.randrange(4),
                      sides[self.rng.randrange(len(sides))])
                if self.legal(ref, st):
                    self.state[ref] = st
                    break
            else:
                raise RuntimeError("no legal start for " + ref)

    def run(self, iters=200000, t0=6.0, t1=0.02, pen0=2.0, pen1=60.0):
        self.init_state()
        for it in range(iters):
            f = it / iters
            temp = t0 * (t1 / t0) ** f
            pen = pen0 * (pen1 / pen0) ** f
            sig = max(0.25, 5.0 * (1 - f))
            ref = self.refs[self.rng.randrange(len(self.refs))]
            old = self.state[ref]
            u = self.rng.random()
            x, y, rot, side = old
            sides = self.parts[ref].get("sides", "FB")
            if u < 0.70:
                new = (x + self.rng.gauss(0, sig), y + self.rng.gauss(0, sig), rot, side)
            elif u < 0.85:
                new = (x, y, (rot + 90 * self.rng.choice((1, 2, 3))) % 360, side)
            elif u < 0.93 and len(sides) > 1:
                new = (x, y, rot, "B" if side == "F" else "F")
            else:
                new = (self.rng.uniform(-17, 30), self.rng.uniform(-17, 17), rot, side)
            if not self.legal(ref, new):
                continue
            c_old = self.cost_of(ref, old, pen)
            self.state[ref] = new
            c_new = self.cost_of(ref, new, pen)
            d = c_new - c_old
            if d > 0 and self.rng.random() >= math.exp(-d / temp):
                self.state[ref] = old
        return self.state

    def total_overlap(self):
        tot = 0.0
        for i, a in enumerate(self.refs):
            tot += self.part_overlap(a, self.state[a], skip=None) / 2.0
        return tot

    def total_hpwl(self):
        return sum(self.net_hpwl(n) for n in self.nets)


def place(parts, nets, fixed_pins, fixed_rects, region_ok, seeds=range(1, 9), iters=200000, margin=0.3, accept=None):
    """Run the annealer for successive seeds; return the first overlap-free result that accept(state) allows
    (else the best), with (state, seed, hpwl, overlap)."""
    best = None
    for s in seeds:
        pl = Placer(parts, nets, fixed_pins, fixed_rects, region_ok, margin=margin, seed=s)
        pl.run(iters=iters)
        ov, wl = pl.total_overlap(), pl.total_hpwl()
        if best is None or (ov, wl) < (best[3], best[2]):
            best = (dict(pl.state), s, wl, ov)
        if ov < 1e-9 and (accept is None or accept(pl.state)):
            return dict(pl.state), s, wl, ov
    return best
