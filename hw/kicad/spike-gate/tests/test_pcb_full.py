# SPDX-License-Identifier: Apache-2.0
"""PCB spike (ADR-0012 spike, exploratory): the generated board matches the schematic netlist, builds
deterministically, and keeps the placement rules. Needs KiCad's pcbnew module (system python3 on this machine);
without it the board tests are skipped and only the pure-Python rule tests run.

Run: cd hw/kicad/spike-gate && PYTHONPATH=src python3 -m unittest tests.test_pcb_full
"""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
import pcb_rules  # noqa: E402

try:
    import pcbnew  # noqa: E402
    import pcb_check  # noqa: E402
    import pcb_full  # noqa: E402
except ImportError:           # venv python without KiCad
    pcbnew = None

NETLIST = HERE / "data" / "full.net"


class Rules(unittest.TestCase):
    def test_ipc2221_widths(self):
        # 1 oz external, 10 K rise: about 0.53 mm at 1.5 A and 0.78 mm at 2.0 A
        self.assertAlmostEqual(pcb_rules.ipc2221_width_mm(1.5), 0.525, places=2)
        self.assertAlmostEqual(pcb_rules.ipc2221_width_mm(2.0), 0.781, places=2)

    def test_power_nets_are_at_least_the_2a_width(self):
        need = pcb_rules.ipc2221_width_mm(2.0)
        self.assertGreaterEqual(pcb_rules.NET_WIDTH["VBUS_IC"], need)
        self.assertGreaterEqual(pcb_rules.NET_WIDTH["+5V"], need)


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class Board(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.pcb = pcb_full.build(str(NETLIST), cls.tmp.name + "/a")
        cls.board = pcbnew.LoadBoard(cls.pcb)
        cls.fps = {f.GetReference(): f for f in cls.board.GetFootprints()}
        cls.comps, cls.nets = pcb_full.read_netlist(str(NETLIST))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_netlist_facts(self):
        self.assertEqual(len(self.comps), 86)
        self.assertEqual(len([n for n in self.nets if not n.startswith("unconnected-")]), 53)
        for ref in ("U13", "C1B", "Q2", "Q3", "R3", "R15"):
            self.assertIn(ref, self.comps)

    def test_board_matches_netlist(self):
        res, _ = pcb_check.compare(str(NETLIST), self.pcb)
        self.assertEqual(res["missing_refs"], [])
        self.assertEqual(res["extra_refs"], [])
        self.assertEqual(res["pad_net_differences"], [])
        self.assertEqual(res["netlist_pins_without_pad"], [])
        self.assertEqual(res["nets_named"], 53)

    def test_two_builds_are_identical(self):
        again = pcb_full.build(str(NETLIST), self.tmp.name + "/b")
        self.assertEqual(Path(self.pcb).read_bytes(), Path(again).read_bytes())
        self.assertEqual(Path(self.pcb).with_suffix(".kicad_pro").read_bytes(),
                         Path(again).with_suffix(".kicad_pro").read_bytes())

    def test_substitutions_are_the_documented_ones(self):
        # every substituted footprint is a provisional stand-in; the report lists the same refs
        self.assertEqual(sorted(pcb_full.FOOTPRINT_OVERRIDE), ["C1", "C1B", "C3", "C4", "U1", "U8", "U9"])
        for ref in pcb_full.FOOTPRINT_OVERRIDE:
            self.assertIn(ref, self.comps)

    def test_every_part_is_inside_the_outline(self):
        for ref, f in self.fps.items():
            x0, y0, x1, y1 = pcb_full.pad_bbox_mm(f)     # pads only: the module's antenna keep-out may leave the board
            self.assertGreaterEqual(y0, -0.5, ref)
            self.assertLessEqual(y1, pcb_full.BOARD_H + 0.5, ref)
            self.assertLessEqual(x1, pcb_full.BOARD_W + 0.5, ref)
            if ref != "J1":
                self.assertGreaterEqual(x0, -0.5, ref)

    def test_usb_c_on_the_left_edge(self):
        b = self.fps["J1"].GetBoundingBox(False)
        self.assertLess(pcbnew.ToMM(b.GetX()), 1.0)

    def test_antenna_keepout_is_free(self):
        """No part but U9 inside the module's keep-out band (board y < 5.7 mm, x within +-21.6 mm of U9)."""
        ux, uy, _ = pcb_full.PLACE["U9"]
        for ref, f in self.fps.items():
            if ref in ("U9",) or ref.startswith("H"):
                continue
            for p in f.Pads():
                bb = p.GetBoundingBox()
                x0, y0, x1, y1 = (pcbnew.ToMM(v) for v in (bb.GetX(), bb.GetY(), bb.GetRight(), bb.GetBottom()))
                inside = (x1 > ux - 21.6 and x0 < ux + 21.6 and y0 < uy - 5.6)
                self.assertFalse(inside, "%s pad %s inside the antenna keep-out" % (ref, p.GetNumber()))

    def test_gate_layout_rules(self):
        """ADR-0016 layout rules: R3 and the readback R15 at the Q3 gate; the ILIM parts next to U7."""
        def centre(ref):
            p = self.fps[ref].GetPosition()
            return pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)

        def dist(a, b):
            ax, ay = centre(a)
            bx, by = centre(b)
            return ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5

        self.assertLessEqual(dist("R3", "Q3"), 6.0)
        self.assertLessEqual(dist("R2", "Q2"), 6.0)
        for ref in ("R_ILIM1", "R_ILIM2", "R_ILIM3"):
            self.assertLessEqual(dist(ref, "U7"), 15.0, ref)
        self.assertLessEqual(dist("C1", "U5"), 8.0)
        self.assertLessEqual(dist("C1B", "U5"), 12.0)

    def test_star_net_is_the_q3_gate(self):
        net = self.nets["/ILIM_STEP3_EN"]
        self.assertIn(("Q3", "1"), net)
        self.assertEqual(pcb_full.STAR["/ILIM_STEP3_EN"], ("Q3", "1"))
        for ref in ("U13", "R3", "R15", "U4"):
            self.assertIn(ref, [r for r, _ in net])


if __name__ == "__main__":
    unittest.main()
