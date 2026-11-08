# SPDX-License-Identifier: Apache-2.0
"""LED ring cells, generated and not routed by the autorouter.

Usage: python3 pcb_ring.py <placed.kicad_pcb> <out.kicad_pcb>   (the placement.json of the same stem sits next to the input)

Each ring LED Dn (top) and its bypass capacitor C(n+7) (bottom, under it) form one cell. The cell is the same for all 16:
  +5V  LED pad 4  --track--  via  --track--  capacitor pad 1   (the via also meets the +5V plane In2)
  GND  LED pad 2  --track--  via  --track--  capacitor pad 2   (the via also meets the GND plane In1)
and the data chain: DOUT (pad 1) of Dn on the top layer to DIN (pad 3) of Dn+1 (D8 to D9 included; D16 has no link).
The vias and tracks are found by the grid router of pcb_fix.py, restricted to the two outer layers, so that every cell
keeps its clearances to its neighbours. Returns the list of cells that could not be completed (exit 1 when not empty).
Pin numbers are those of the KiCad symbol LED:WS2812B-2020 (layout_full.LED_*).
"""
from __future__ import annotations

import json
import sys

import pcbnew

import pcb_fix as F
import pcb_full as P
import pcb_rules as R

STUB = 0.25            # power stub width: 20 mA per LED, the plane carries the current
CHAIN = 0.15           # data link width (the default track)
LED_VDD, LED_VSS, LED_DOUT, LED_DIN = "4", "2", "1", "3"
CAP_5V, CAP_GND = "1", "2"


def cells():
    return [("D%d" % i, "C%d" % (i + 7)) for i in range(1, 17)]


def build(src, dst, tab_r=None):
    board = pcbnew.LoadBoard(src)
    if tab_r is None:
        tab_r = json.load(open(src.rsplit("/", 1)[0] + "/busy_light_spike.placement.json"))["tab_r"]
    fx = F.Fixer(board, tab_r)
    fx.only = ["F.Cu", "B.Cu"]
    failed, count = [], 0
    chain_w = R.TRACK if R.TRACK > 0.1 else CHAIN
    def link(net, a, la, b, lb, w, what):
        nonlocal count
        path = fx.route(net, a, la, b, lb, w) or fx.route(net, a, la, b, lb, w, window=2 * F.WINDOW)
        if path is None:
            failed.append(what)
            return
        fx.commit(net, path, a, b, w)
        count += 1
    for d, c in cells():
        for net, dn, cn in (("+5V", LED_VDD, CAP_5V), ("GND", LED_VSS, CAP_GND)):
            (x0, y0, n0), (x1, y1, n1) = fx.pads[(d, dn)], fx.pads[(c, cn)]
            assert n0 == n1 == net, (d, dn, n0, c, cn, n1)
            link(net, (x0, y0), "F.Cu", (x1, y1), "B.Cu", STUB, "%s %s to %s" % (net, d, c))
    for i in range(1, 16):
        d, e = "D%d" % i, "D%d" % (i + 1)
        (x0, y0, n0), (x1, y1, n1) = fx.pads[(d, LED_DOUT)], fx.pads[(e, LED_DIN)]
        assert n0 == n1, (d, e, n0, n1)
        link(n0, (x0, y0), "F.Cu", (x1, y1), "F.Cu", chain_w, "data %s to %s" % (d, e))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(dst, board)
    P.normalise_uuids(dst)
    print(json.dumps({"ring_links": count, "failed": failed}, sort_keys=True))
    return failed


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    sys.exit(1 if build(sys.argv[1], sys.argv[2]) else 0)
