# SPDX-License-Identifier: Apache-2.0
"""Spike: Specctra DSN export and SES import, for routing the placed board with an external router
(for example Freerouting). The external router is not run by run_pcb.sh; see the PCB spike report.

Usage: python3 pcb_dsn.py export <in.kicad_pcb> <out.dsn> [planes: B (default) | F | FB | none | inner] [keyonly]
         keyonly: only the nets of pcb_rules.ROUTE_FIRST stay nets in the DSN; the other pads become obstacles (stage 1)
       python3 pcb_dsn.py branchwidth <in.dsn> <out.dsn>   set the track width of the VBUS_IC class to BRANCH_WIDTH (stage 2)
       python3 pcb_dsn.py outer <in.dsn> <out.dsn>         add use_layer rules: outer layers for pcb_rules.OUTER_ONLY, no In1 for the other nets except GND
       python3 pcb_dsn.py lock <in.kicad_pcb> <out.kicad_pcb>    lock every track and via (stage 2 keeps them)
       python3 pcb_dsn.py unlock <in.kicad_pcb> <out.kicad_pcb>
       python3 pcb_dsn.py import <in.kicad_pcb> <in.ses> <out.kicad_pcb>
"""
import os
import sys

import pcbnew

import pcb_full as P
import pcb_ring
import pcb_rules

if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "export":
        b = pcbnew.LoadBoard(sys.argv[2])
        # planes option: see pcb_rules.router_keeps_zone (none | inner | B | F | FB); other zones are removed for the router
        planes = sys.argv[4] if len(sys.argv) > 4 else "B"
        lname = {pcbnew.F_Cu: "F", pcbnew.B_Cu: "B"}
        for z in list(b.Zones()):
            if z.GetIsRuleArea():
                continue
            lay = z.GetLayer()
            if not pcb_rules.router_keeps_zone(planes, lname.get(lay, b.GetLayerName(lay).split(".")[0]), z.GetNetname()):
                b.Remove(z)
        if len(sys.argv) > 5 and sys.argv[5] == "keyonly":
            for f in b.GetFootprints():
                for pad in f.Pads():
                    net = pad.GetNetname()
                    if not pcb_rules.is_key_net(net) or not pcb_rules.is_main_path_pad(net, f.GetReference(), pad.GetNumber()):
                        pad.SetNetCode(0)
        if os.environ.get("RING", "1") == "1":             # the ring cells reach +5V through the In2 plane: the router leaves those pads alone
            ring = {r for d, c in pcb_ring.cells() for r in (d, c)}
            for f in b.GetFootprints():
                if f.GetReference() in ring:
                    for pad in f.Pads():
                        if pad.GetNetname() == "+5V":
                            pad.SetNetCode(0)
        ok = pcbnew.ExportSpecctraDSN(b, sys.argv[3])
        print("export", "ok" if ok else "FAILED", sys.argv[3])
        sys.exit(0 if ok else 1)
    if len(sys.argv) >= 4 and sys.argv[1] == "branchwidth":
        import re
        txt = open(sys.argv[2], encoding="utf-8").read()
        name = pcb_rules.net_class_name(pcb_rules.MAIN_PATH_NET)
        i = txt.index("(class %s " % name)
        j = txt.find("(class ", i + 1)
        j = len(txt) if j < 0 else j
        blk, n = re.subn(r"\(width \d+\)", "(width %d)" % round(pcb_rules.BRANCH_WIDTH * 1000), txt[i:j], count=1)
        assert n == 1, "no width rule in the class block"
        open(sys.argv[3], "w", encoding="utf-8").write(txt[:i] + blk + txt[j:])
        print("branch width", pcb_rules.BRANCH_WIDTH, "mm for class", name)
        sys.exit(0)
    if len(sys.argv) >= 4 and sys.argv[1] == "outer":
        txt = open(sys.argv[2], encoding="utf-8").read()
        done = []
        # class name -> layers; kicad_default holds GND and the signals (GND tracks on In1 are not needed: the plane is there)
        rules = {pcb_rules.net_class_name(n): pcb_rules.OUTER_LAYERS for n in pcb_rules.OUTER_ONLY}
        if not pcb_rules.IN1_SIGNALS:
            rules[pcb_rules.net_class_name("+5V")] = pcb_rules.NOT_IN1_LAYERS
            rules["kicad_default"] = pcb_rules.NOT_IN1_LAYERS
        for name, lay in rules.items():
            key = "(class %s " % name
            if key not in txt:
                continue
            i = txt.index(key)
            k = txt.index("(circuit", i) + len("(circuit")
            txt = txt[:k] + "\n        (use_layer %s)" % " ".join(lay) + txt[k:]
            done.append(name)
        assert done, "no class of a restricted net in the DSN"
        open(sys.argv[3], "w", encoding="utf-8").write(txt)
        print("layer rules for classes", ",".join(done))
        sys.exit(0)
    if len(sys.argv) >= 4 and sys.argv[1] in ("lock", "unlock"):
        b = pcbnew.LoadBoard(sys.argv[2])
        tr = b.Tracks()
        for item in [tr[i] for i in range(tr.size())]:
            item.SetLocked(sys.argv[1] == "lock")
        pcbnew.SaveBoard(sys.argv[3], b)
        P.normalise_uuids(sys.argv[3])
        print(sys.argv[1] + "ed", tr.size(), "tracks and vias")
        sys.exit(0)
    if len(sys.argv) >= 5 and sys.argv[1] == "import":
        b = pcbnew.LoadBoard(sys.argv[2])
        if not pcbnew.ImportSpecctraSES(b, sys.argv[3]):
            sys.exit("import failed")
        tr = b.Tracks()
        for item in [tr[i] for i in range(tr.size())]:           # the router may write 0.10 or 0.12 mm wires at tight spots
            if item.GetClass() == "PCB_TRACK" and item.GetWidth() < P.mm(pcb_rules.MIN_TRACK):
                item.SetWidth(P.mm(pcb_rules.clamp_track_width(pcbnew.ToMM(item.GetWidth()))))
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        pcbnew.SaveBoard(sys.argv[4], b)
        P.normalise_uuids(sys.argv[4])
        print("imported", sys.argv[4])
        sys.exit(0)
    sys.exit(__doc__)
