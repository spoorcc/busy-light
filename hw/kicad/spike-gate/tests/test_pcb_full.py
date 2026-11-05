# SPDX-License-Identifier: Apache-2.0
"""PCB spike (ADR-0012 spike, exploratory): the generated board matches the schematic netlist, builds
deterministically, and keeps the placement rules. Needs KiCad's pcbnew module (system python3 on this machine);
without it the board tests are skipped and only the pure-Python rule tests run.

Run: cd hw/kicad/spike-gate && PYTHONPATH=src python3 -m unittest tests.test_pcb_full
"""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
import mech_outline  # noqa: E402
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

    def test_power_nets_cover_the_highest_current_limit(self):
        need = pcb_rules.ipc2221_width_mm(pcb_rules.I_TOP_STEP_MAX_A)       # about 0.56 mm
        self.assertGreater(need, pcb_rules.ipc2221_width_mm(1.5))
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
        cls.info = json.loads(Path(cls.pcb).with_suffix(".placement.json").read_text())
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
        self.assertEqual(sorted(pcb_full.FOOTPRINT_OVERRIDE),
                         sorted(["C1", "C1B", "C3", "C4", "U1", "U8", "U9"] + ["D%d" % i for i in range(1, 17)]))
        for ref in pcb_full.FOOTPRINT_OVERRIDE:
            self.assertIn(ref, self.comps)

    def test_every_pad_is_inside_the_mech_outline(self):
        """Pads inside the V1 envelope (circle D46 plus tab); the USB-C shell front may leave the tab."""
        info = self.info
        for ref, f in self.fps.items():
            for p in f.Pads():
                if ref == "J1" and p.GetNumber() == "SH":
                    continue
                mx, my = pcb_full.mech_of(pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y))
                self.assertTrue(mech_outline.inside_pcb(mx, my, 0.0, info["tab_r"]), "%s pad %s" % (ref, p.GetNumber()))

    def test_led_ring_follows_the_mech_numbers(self):
        for i in range(16):
            f = self.fps["D%d" % (i + 1)]
            mx, my = pcb_full.mech_of(pcbnew.ToMM(f.GetPosition().x), pcbnew.ToMM(f.GetPosition().y))
            self.assertAlmostEqual(math.hypot(mx, my), mech_outline.R_RING, places=1)
            az = math.degrees(math.atan2(my, mx)) % 360.0
            self.assertAlmostEqual(az, mech_outline.led_azimuths()[i], places=1)
            self.assertEqual(f.GetLayer(), pcbnew.F_Cu)
            self.assertEqual(self.fps["C%d" % (i + 8)].GetLayer(), pcbnew.B_Cu)

    LED_FP = "LED_SMD:LED_WS2812B-2020_PLCC4_2.0x2.0mm"

    def test_t1_led_footprint_and_pin_order(self):
        """T1 (plan 06): D1 to D16 use the 2020 stand-in; DOUT (pad 2) of D(k) faces DIN (pad 4) of D(k+1)."""
        for i in range(16):
            d = self.fps["D%d" % (i + 1)]
            self.assertEqual("%s:%s" % (d.GetFPID().GetLibNickname(), d.GetFPID().GetLibItemName()), self.LED_FP)
        res, _ = pcb_check.compare(str(NETLIST), self.pcb)
        self.assertEqual(res["pad_net_differences"], [])

        def pad(ref, num):
            p = [q for q in self.fps[ref].Pads() if q.GetNumber() == num][0]
            return pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)
        for i in range(1, 15):
            ox, oy = pad("D%d" % (i + 1), "2")
            nxt = math.hypot(ox - pad("D%d" % (i + 2), "4")[0], oy - pad("D%d" % (i + 2), "4")[1])
            prv = math.hypot(ox - pad("D%d" % i, "4")[0], oy - pad("D%d" % i, "4")[1])
            self.assertLess(nxt, prv, "DOUT of D%d faces D%d" % (i + 1, i + 2))
            self.assertLess(nxt, 7.0)

    def test_t2_led_ring_tolerance(self):
        """T2: radius within 0.2 mm and azimuth within 1 degree of 3.75 + 22.5 k (mech spike constraint)."""
        for i in range(16):
            p = self.fps["D%d" % (i + 1)].GetPosition()
            mx, my = pcb_full.mech_of(pcbnew.ToMM(p.x), pcbnew.ToMM(p.y))
            self.assertLessEqual(abs(math.hypot(mx, my) - 20.0), 0.2)
            d = (math.degrees(math.atan2(my, mx)) - (3.75 + 22.5 * i) + 180.0) % 360.0 - 180.0
            self.assertLessEqual(abs(d), 1.0)

    def test_t3_courtyards_of_led_cap_and_j1_do_not_overlap(self):
        """T3: no LED, bypass cap or J1 courtyard overlaps another courtyard on the same side (U9 keep-out excepted)."""
        refs = ["D%d" % (i + 1) for i in range(16)] + ["C%d" % (i + 8) for i in range(16)] + ["J1"]
        bad = []
        for a in refs:
            fa = self.fps[a]
            la = fa.GetLayer()
            ca = fa.GetCourtyard(la)
            for b, fb in self.fps.items():
                if b == a or fb.GetLayer() != la or (b in refs and b < a):
                    continue
                if b == "U9":        # the module's library courtyard is its antenna keep-out: known conflict, plan 06 G1/G5
                    continue
                cb = fb.GetCourtyard(la)
                if ca.OutlineCount() and cb.OutlineCount():
                    inter = pcbnew.SHAPE_POLY_SET(ca)
                    inter.BooleanIntersection(cb)
                    if inter.Area() > 0:
                        bad.append((a, b))
        self.assertEqual(bad, [])

    def test_t12_largest_dim_is_computed_and_limited(self):
        """T12: the housing size comes from the board and must not exceed the old 59.8 mm."""
        self.assertLessEqual(self.info["largest_dim_mm"], mech_outline.MAX_DIM_SPIKE_MM)
        mouth = pcbnew.ToMM(self.fps["J1"].GetBoundingBox(False).GetRight()) - pcb_full.CX
        self.assertAlmostEqual(mech_outline.largest_dim_mm(mouth), self.info["largest_dim_mm"], places=1)
        with self.assertRaises(ValueError):
            mech_outline.check_largest_dim(32.3)                 # 59.9 mm

    def test_usb_c_on_the_tab_facing_plus_x(self):
        b = self.fps["J1"].GetBoundingBox(False)
        mouth = pcbnew.ToMM(b.GetRight()) - pcb_full.CX
        self.assertAlmostEqual(mouth, self.info["j1_mouth_r"], places=1)
        self.assertGreaterEqual(self.info["j1_mouth_r"], pcb_full.J1_MOUTH_R)

    def test_mouth_against_the_mech_limit_is_recorded(self):
        """Plan 06 D2: the limit MAX_DIM_MECH001 (58 mm) is reported; the spike limit is the old 59.8 mm."""
        self.assertLessEqual(self.info["largest_dim_mm"], mech_outline.MAX_DIM_SPIKE_MM)

    def test_antenna_strip_is_free(self):
        ax0, ay0, ax1, ay1 = mech_outline.antenna_strip()
        for ref, f in self.fps.items():
            if ref == "U9":
                continue
            for p in f.Pads():
                bb = p.GetBoundingBox()
                x0, x1 = (pcbnew.ToMM(v) - pcb_full.CX for v in (bb.GetX(), bb.GetRight()))
                y0, y1 = (pcb_full.CY - pcbnew.ToMM(v) for v in (bb.GetBottom(), bb.GetY()))
                self.assertFalse(x1 > ax0 and x0 < ax1 and y1 > ay0 and y0 < ay1, "%s pad %s" % (ref, p.GetNumber()))

    def test_module_antenna_points_to_minus_x(self):
        u9 = self.fps["U9"]
        mx, _ = pcb_full.mech_of(pcbnew.ToMM(u9.GetPosition().x), pcbnew.ToMM(u9.GetPosition().y))
        self.assertAlmostEqual(mx, 1.0, places=0)          # MOD_OFF
        self.assertEqual(round(u9.GetOrientationDegrees()) % 360, pcb_full.MODULE_ROT)

    def test_no_overlap_among_movable_parts(self):
        self.assertEqual(self.info["overlap_mm2"], 0.0)

    def test_no_mounting_holes(self):
        # the mech spike holds the PCB with edge pegs and hooks, there are no mounting holes
        self.assertFalse([r for r in self.fps if r.startswith("H")])

    def test_gate_layout_rules(self):
        """ADR-0016 layout rules: R3 and the readback R15 at the Q3 gate; the ILIM parts next to U7."""
        def centre(ref):
            p = self.fps[ref].GetPosition()
            return pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)

        def dist(a, b):
            ax, ay = centre(a)
            bx, by = centre(b)
            return ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5

        for r1, r2, lim in pcb_full.LAYOUT_RULES:
            self.assertLessEqual(dist(r1, r2), lim, "%s %s" % (r1, r2))

    def test_star_net_is_the_q3_gate(self):
        net = self.nets["/ILIM_STEP3_EN"]
        self.assertIn(("Q3", "1"), net)
        self.assertEqual(pcb_full.STAR["/ILIM_STEP3_EN"], ("Q3", "1"))
        for ref in ("U13", "R3", "R15", "U4"):
            self.assertIn(ref, [r for r, _ in net])


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class Stitch(unittest.TestCase):
    def test_segment_distance(self):
        import pcb_stitch
        self.assertAlmostEqual(pcb_stitch.seg_dist(1, 1, 0, 0, 2, 0), 1.0)
        self.assertAlmostEqual(pcb_stitch.seg_dist(-3, 0, 0, 0, 2, 0), 3.0)

    def test_unconnected_pad_parser(self):
        import pcb_stitch
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "drc.json"
            f.write_text(json.dumps({"unconnected_items": [{"items": [
                {"description": "Pad 3 [GND] of U11 on F.Cu"}, {"description": "Zone [GND] on B.Cu, priority 1"}]},
                {"items": [{"description": "PTH pad A5 [/CC1] of J1"}, {"description": "Pad 1 [+5V] of C8 on B.Cu"}]}]}))
            got = pcb_stitch.unconnected_pads(str(f), ("GND", "+5V"))
        self.assertEqual(got, {("U11", "3"): ("GND", "F.Cu"), ("C8", "1"): ("+5V", "B.Cu")})


if __name__ == "__main__":
    unittest.main()
