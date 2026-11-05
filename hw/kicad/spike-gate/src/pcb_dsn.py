# SPDX-License-Identifier: Apache-2.0
"""Spike: Specctra DSN export and SES import, for routing the placed board with an external router
(for example Freerouting). The external router is not run by run_pcb.sh; see the PCB spike report.

Usage: python3 pcb_dsn.py export <in.kicad_pcb> <out.dsn> [planes: B (default) | F | FB | none]
       python3 pcb_dsn.py import <in.kicad_pcb> <in.ses> <out.kicad_pcb>
"""
import sys

import pcbnew

import pcb_full as P

if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "export":
        b = pcbnew.LoadBoard(sys.argv[2])
        # option: leave a GND pour on the listed layers only (default B.Cu): a pour on both layers blocks the router
        planes = (sys.argv[4] if len(sys.argv) > 4 else "B").upper()      # outer layers that keep a GND pour: F, B, FB
        keep_inner = planes != "NONE"                                       # NONE removes every pour (router sees none)
        for z in list(b.Zones()):
            if z.GetIsRuleArea():
                continue
            lay = z.GetLayer()
            if lay == pcbnew.F_Cu and "F" not in planes or lay == pcbnew.B_Cu and "B" not in planes:
                b.Remove(z)
            elif lay not in (pcbnew.F_Cu, pcbnew.B_Cu) and not keep_inner:
                b.Remove(z)
        ok = pcbnew.ExportSpecctraDSN(b, sys.argv[3])
        print("export", "ok" if ok else "FAILED", sys.argv[3])
        sys.exit(0 if ok else 1)
    if len(sys.argv) >= 5 and sys.argv[1] == "import":
        b = pcbnew.LoadBoard(sys.argv[2])
        if not pcbnew.ImportSpecctraSES(b, sys.argv[3]):
            sys.exit("import failed")
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        pcbnew.SaveBoard(sys.argv[4], b)
        P.normalise_uuids(sys.argv[4])
        print("imported", sys.argv[4])
        sys.exit(0)
    sys.exit(__doc__)
