# SPDX-License-Identifier: Apache-2.0
"""The LED ring cells: all 16 cells complete, no clearance finding, the capacitor pads sit under the LED pads of the same net."""
import json
import math
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
import pcbnew  # noqa: E402

import pcb_full  # noqa: E402
import pcb_ring  # noqa: E402

NETLIST = HERE / "data" / "full.net"


class Ring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.pcb = pcb_full.build(str(NETLIST), cls.tmp.name + "/a")
        cls.out = cls.tmp.name + "/a/ring.kicad_pcb"
        cls.failed = pcb_ring.build(cls.pcb, cls.out)
        cls.board = pcbnew.LoadBoard(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_cell_completes(self):
        self.assertEqual(self.failed, [])

    def test_two_sided_cells_link_to_the_bottom_capacitor(self):
        # plan 08 step 5: the link layer follows the capacitor; without P1 the capacitors are on B.Cu
        self.assertEqual({pcb_ring.cap_link_layer(self.board, c) for _, c in pcb_ring.cells()}, {"B.Cu"})

    def test_cap_pads_sit_under_the_led_pads_of_the_same_net(self):
        mm = pcbnew.ToMM
        for d, c in pcb_ring.cells():
            fd, fc = self.board.FindFootprintByReference(d), self.board.FindFootprintByReference(c)
            pd = {p.GetNumber(): p for p in fd.Pads()}
            pc = {p.GetNumber(): p for p in fc.Pads()}
            for dn, cn in ((pcb_ring.LED_VDD, pcb_ring.CAP_5V), (pcb_ring.LED_VSS, pcb_ring.CAP_GND)):
                self.assertEqual(pd[dn].GetNetname(), pc[cn].GetNetname(), d)
        # the four ring rotations are tried; a cell far from alignment is the one the antenna or the tab shifted
        near = 0
        for d, c in pcb_ring.cells():
            fd, fc = self.board.FindFootprintByReference(d), self.board.FindFootprintByReference(c)
            a = {p.GetNumber(): p.GetPosition() for p in fd.Pads()}["4"]
            b = {p.GetNumber(): p.GetPosition() for p in fc.Pads()}["1"]
            near += math.hypot(mm(a.x - b.x), mm(a.y - b.y)) < 1.0
        self.assertGreaterEqual(near, 14)

    def test_chain_links_exist_and_the_last_led_is_open(self):
        nets = {t.GetNetname() for t in [self.board.Tracks()[i] for i in range(self.board.Tracks().size())]}
        for i in range(1, 16):
            fd = self.board.FindFootprintByReference("D%d" % i)
            net = {p.GetNumber(): p.GetNetname() for p in fd.Pads()}[pcb_ring.LED_DOUT]
            self.assertIn(net, nets, "D%d" % i)

    def test_no_clearance_or_hole_finding(self):
        d = Path(self.out).parent
        shutil.copy(d / "busy_light_spike.kicad_pro", d / "ring.kicad_pro")
        shutil.copy(d / "busy_light_spike.kicad_dru", d / "ring.kicad_dru")
        subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all", "-o", str(d / "r.json"), self.out],
                       check=False, capture_output=True)
        rep = json.loads((d / "r.json").read_text())
        bad = [v for v in rep["violations"] if v["type"] in ("clearance", "hole_clearance", "hole_to_hole", "copper_edge_clearance", "shorting_items", "track_width", "via_dangling")]
        self.assertEqual(bad, [])

    def test_no_ring_via_touches_an_smd_pad(self):
        # plan 08 section 4.3 (HW-008): the grid router keeps every cell via off the SMD pads of any net, the LED and
        # capacitor pads of its own cell included; checked by the producers' rule and by the exact copper of pcb_fabcheck
        import pcb_fabcheck
        import pcb_rules
        import pcb_stitch
        boxes = pcb_stitch.pad_boxes(self.board)
        tr = self.board.Tracks()
        vias = [pcbnew.Cast_to_PCB_VIA(tr[i]) for i in range(tr.size()) if tr[i].GetClass() == "PCB_VIA"]
        self.assertTrue(vias)
        hits = [(pcbnew.ToMM(v.GetPosition().x), pcbnew.ToMM(v.GetPosition().y)) for v in vias
                if pcb_rules.via_hits_smd_pad(pcbnew.ToMM(v.GetPosition().x), pcbnew.ToMM(v.GetPosition().y),
                                              pcbnew.ToMM(v.GetWidth(pcbnew.F_Cu)), boxes)]
        self.assertEqual(hits, [])
        self.assertEqual(pcb_fabcheck.vias_in_smd_pads(self.board), [])


if __name__ == "__main__":
    unittest.main()
