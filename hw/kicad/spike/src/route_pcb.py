"""Spike: scripted routing with pcbnew. Chains each net's pads in order; GND via-in-pad plus B.Cu pour (spike only)."""
import sys

import pcbnew
from pcbnew import VECTOR2I, FromMM

src, out = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(src)
by_net: dict[str, list] = {}
for fp in b.GetFootprints():
    for pad in fp.Pads():
        n = pad.GetNetname()
        if n:
            by_net.setdefault(n, []).append(pad)
stats = {"tracks": 0, "vias": 0}


def track(net, a, c, layer=pcbnew.F_Cu, width=0.25):
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(a)
    t.SetEnd(c)
    t.SetLayer(layer)
    t.SetWidth(FromMM(width))
    t.SetNet(net)
    b.Add(t)
    stats["tracks"] += 1


for name, pads in sorted(by_net.items()):
    net = pads[0].GetNet()
    pads = sorted(pads, key=lambda p: (p.GetParentAsString(), p.GetNumber()))
    if name == "/GND":
        for p in pads:
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(p.GetPosition())
            v.SetNet(net)
            v.SetWidth(FromMM(0.6))
            v.SetDrill(FromMM(0.3))
            b.Add(v)
            stats["vias"] += 1
        continue
    for p, q in zip(pads, pads[1:], strict=False):
        track(net, p.GetPosition(), q.GetPosition(), width=0.5 if name == "/+5V" else 0.25)
zone = pcbnew.ZONE(b)
zone.SetLayer(pcbnew.B_Cu)
zone.SetNet(b.FindNet("/GND"))
ol = zone.Outline()
ol.NewOutline()
for k in range(64):
    import math

    a = 2 * math.pi * k / 64
    ol.Append(FromMM(22 * math.cos(a)), FromMM(22 * math.sin(a)))
b.Add(zone)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(out)
print("routed", stats)
