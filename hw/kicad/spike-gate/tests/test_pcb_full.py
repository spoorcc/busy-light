# SPDX-License-Identifier: Apache-2.0
"""PCB spike (ADR-0012 spike, exploratory): the generated board matches the schematic netlist, builds
deterministically, and keeps the placement rules. Needs KiCad's pcbnew module (system python3 on this machine);
without it the board tests are skipped and only the pure-Python rule tests run.

Run: cd hw/kicad/spike-gate && PYTHONPATH=src python3 -m unittest tests.test_pcb_full
"""
import json
import re
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
class RuleMisses(unittest.TestCase):
    """RV-016 row 11: the placer keeps its best seed when no seed meets the rules; pcb_full records the misses."""
    def test_a_miss_is_listed_with_its_distance(self):
        st = {"C1": (0.0, 0.0, 0, "F"), "U5": (6.0, 8.0, 0, "F"), "R2": (0.0, 0.0, 0, "F"), "U14": (3.0, 0.0, 0, "F")}
        self.assertEqual(pcb_full.rule_misses(st, (("C1", "U5", 8.0), ("R2", "U14", 6.0), ("X9", "U5", 1.0))),
                         [["C1", "U5", 8.0, 10.0]])

    def test_a_fixed_partner_counts_its_nearest_point(self):
        st = {"TVS1": (5.0, 3.0, 0, "F")}
        pts = ((0.0, 0.0), (20.0, 0.0))
        self.assertEqual(pcb_full.rule_misses(st, (("TVS1", pts, 6.0),)), [])
        self.assertEqual(pcb_full.rule_misses(st, (("TVS1", pts, 5.0),)), [["TVS1", "fixed", 5.0, 5.83]])

    def test_input_path_rules_resolve_to_the_j1_vbus_pads(self):
        """RV-016 row 12: the plan 08 input-path rules reach the placer; "J1:VBUS" becomes J1's VBUS pad points."""
        nets = {"VBUS": [("J1", "A4"), ("J1", "B9"), ("TVS1", "1"), ("R22", "1")], "GND": [("J1", "A1")]}
        fixed_pins = {("J1", "A4"): (1.0, 2.0), ("J1", "B9"): (3.0, 4.0), ("J1", "A1"): (9.0, 9.0)}
        comps = {r: None for r in ("J1", "TVS1", "U6", "R22", "U7")}
        rules = pcb_full.resolve_rules(pcb_full.INPUT_PATH_RULES, nets, fixed_pins, comps)
        self.assertIn(("TVS1", ((1.0, 2.0), (3.0, 4.0)), 6.0), rules)
        self.assertIn(("R22", "U7", 6.0), rules)
        self.assertEqual(len(rules), 4)
        self.assertEqual(pcb_full.resolve_rules(pcb_full.INPUT_PATH_RULES, nets, fixed_pins, {"J1": None}), [])

    def test_hw016_rule_keeps_the_spare_pads_within_10_mm(self):
        """7.0 mm part centres + 1.48 mm (U7 pad 6 from its origin) + 1.475 mm (1206 pad centre) <= 10 mm (HW-016)."""
        lim = {(a, b): v for a, b, v in pcb_full.LAYOUT_RULES}
        for ref in ("C4", "C32"):
            self.assertLessEqual(lim[(ref, "U7")] + 1.48 + 1.475, 10.0)


class PlacementWeights(unittest.TestCase):
    """The gate and bypass rules are enforced by weights in the annealer, not left to chance."""

    def test_rule_tables(self):
        self.assertGreater(pcb_rules.NET_WEIGHT["/ILIM_STEP3_EN"], 1.0)
        bypass = {"tie:C24-U14", "tie:C25-U15"}
        regulator = {"tie:C5-U8", "tie:C6-U8"}              # TLV757P: input capacitor at pin 1, output capacitor at pin 5
        paths = {"tie:J1A4-U7", "tie:J1B9-U7", "tie:C2-U7", "tie:U8-U9"}      # current paths of the power check
        spares = {"tie:C4-U7", "tie:C32-U7"}                                    # HW-016: spares at U7 pin 6
        self.assertEqual(set(pcb_rules.PIN_TIES), bypass | regulator | paths | spares)
        for name in spares:
            self.assertEqual(pcb_rules.PIN_TIES[name][1], ("U7", "6"))
        for name, (a, b, w) in pcb_rules.PIN_TIES.items():
            if name in bypass:
                self.assertEqual(b[1], "5")          # TMUX1101 pin 5 = VDD
            if name in regulator:
                self.assertEqual((a[0], b[0]), (name[4:6], "U8"))
                self.assertIn(b[1], ("1", "5"))
            self.assertGreater(w, 1.0)

    def test_blocks_and_twins_name_real_parts_of_the_same_kind(self):
        comps, _ = pcb_full.read_netlist(str(NETLIST))
        anchors = {a for a, _, _ in pcb_rules.BLOCKS}
        self.assertTrue(anchors <= set(comps), anchors - set(comps))
        for a, m, rad in pcb_rules.BLOCKS:
            self.assertIn(m, comps, m)
            self.assertGreater(rad, 0.0)
            self.assertNotEqual(a, m)
        self.assertEqual(len({(a, m) for a, m, _ in pcb_rules.BLOCKS}), len(pcb_rules.BLOCKS))     # no repeats
        for a, b in pcb_rules.TWINS:
            self.assertEqual(comps[a][1], comps[b][1], (a, b))       # same footprint

    def test_families_group_movable_parts_by_kind(self):
        comps, _ = pcb_full.read_netlist(str(NETLIST))
        fams = pcb_full.part_families(comps, fixed={"U9", "J1", "SW1"})
        flat = [r for f in fams for r in f]
        self.assertEqual(len(flat), len(set(flat)))                  # a part is in one family only
        self.assertFalse({"U9", "J1", "SW1"} & set(flat))
        self.assertFalse([r for r in flat if r.startswith("TP")])
        for f in fams:
            self.assertGreaterEqual(len(f), 2)
            self.assertEqual(len({(comps[r][1], re.match("[A-Z]+", r).group(0)) for r in f}), 1)

    def test_ic_families_and_the_test_point_row(self):
        comps, _ = pcb_full.read_netlist(str(NETLIST))
        fixed = {"U9", "J1", "SW1"}
        ics = pcb_full.ic_families(comps, fixed)
        self.assertTrue(ics)
        self.assertTrue(all(r.startswith("U") for f in ics for r in f))
        self.assertTrue(any({"U14", "U15"} <= set(f) for f in ics))     # same footprint family (U11 joins it in SC-70, ADR-0023)
        self.assertTrue(all(len({comps[r][1] for r in f}) == 1 for f in ics))
        row = pcb_full.test_point_row(comps, fixed)
        self.assertEqual(len(row), 1)
        self.assertEqual(len(row[0]), 6)                      # TP1 to TP6
        self.assertEqual(pcb_full.test_point_row({"TP1": ("", "")}), [])

    def test_strict_ic_rule_is_a_switch_and_ics_stay_in_the_soft_families_without_it(self):
        comps, _ = pcb_full.read_netlist(str(NETLIST))
        fixed = {"U9", "J1", "SW1"}
        soft, strict = pcb_full.orientation_families(comps, fixed, strict_ics=False)
        self.assertEqual(strict, [])
        self.assertTrue(any(f[0].startswith("U") for f in soft))      # the ring12 setup
        soft2, strict2 = pcb_full.orientation_families(comps, fixed, strict_ics=True)
        self.assertTrue(strict2)
        self.assertFalse(any(f[0].startswith("U") for f in soft2))
        self.assertEqual(sorted(soft + strict), sorted(soft2 + strict2))      # same parts, other rule

    def test_weight_scales_the_wire_length_cost(self):
        import pcb_place
        parts = {"A": {"w": 1, "h": 1, "pads": {"1": (0, 0)}}, "B": {"w": 1, "h": 1, "pads": {"1": (0, 0)}}}
        nets = {"n": [("A", "1"), ("B", "1")]}
        plain = pcb_place.Placer(parts, nets, {}, [], lambda *a: True)
        heavy = pcb_place.Placer(parts, nets, {}, [], lambda *a: True, weights={"n": 4.0})
        for pl in (plain, heavy):
            pl.state = {"A": (0, 0, 0, "F"), "B": (3, 4, 0, "F")}
        self.assertAlmostEqual(heavy.cost_of("A", plain.state["A"], 0.0), 4 * plain.cost_of("A", plain.state["A"], 0.0))


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
        self.assertEqual(len(self.comps), 97)      # ADR-0023: U13, U10, R6, R13 out
        self.assertEqual(len([n for n in self.nets if not n.startswith("unconnected-")]), 52)
        for ref in ("C27", "C28", "C29", "C30", "C31", "U14", "U15", "R22", "R18", "R19", "C24", "C25", "R3", "R15",
                    "C32"):
            self.assertIn(ref, self.comps)
        for ref in ("Q2", "Q3", "R20", "U13", "U10", "R6", "R13"):
            self.assertNotIn(ref, self.comps)

    def test_board_matches_netlist(self):
        res, _ = pcb_check.compare(str(NETLIST), self.pcb)
        self.assertEqual(res["missing_refs"], [])
        self.assertEqual(res["extra_refs"], [])
        self.assertEqual(res["pad_net_differences"], [])
        self.assertEqual(res["netlist_pins_without_pad"], [])
        self.assertEqual(res["nets_named"], 52)        # ADR-0023: -CC_OK_NOT_S3, -HOLD_OK, -FAULT_N (wired into GATE_OK_RB)

    def test_two_builds_are_identical(self):
        again = pcb_full.build(str(NETLIST), self.tmp.name + "/b")
        self.assertEqual(Path(self.pcb).read_bytes(), Path(again).read_bytes())
        self.assertEqual(Path(self.pcb).with_suffix(".kicad_pro").read_bytes(),
                         Path(again).with_suffix(".kicad_pro").read_bytes())

    def test_substitutions_are_the_documented_ones(self):
        # the remaining substitutions: bulk and input capacitor sizes (values still open); U1, U8, U9 and the LEDs
        # use their own footprints (schematic field, generated library) since 2026-11-07
        self.assertEqual(sorted(pcb_full.FOOTPRINT_OVERRIDE), ["U1"])
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

    def test_module_pads_start_outside_the_antenna_strip(self):
        """The module pad rows (36 to 48 side) lie at or beyond the strip end: no module pad inside the strip."""
        ax0, ay0, ax1, ay1 = mech_outline.antenna_strip()
        for p in self.fps["U9"].Pads():
            bb = p.GetBoundingBox()
            x0 = pcbnew.ToMM(bb.GetX()) - pcb_full.CX
            self.assertGreaterEqual(x0, ax1 - 0.01, "U9 pad %s starts at %.2f, strip ends at %.2f" % (p.GetNumber(), x0, ax1))

    def test_slot_is_cut_and_kept_clear(self):
        sx0, sy0, sx1, sy1 = mech_outline.slot_rect()
        self.assertLess(sx1, mech_outline.module_rect()[0])          # between the antenna end and the ring
        self.assertGreater(sx0, -mech_outline.R_PCB)                  # inside the board
        for ref, f in self.fps.items():
            for p in f.Pads():
                bb = p.GetBoundingBox()
                x0, x1 = (pcbnew.ToMM(v) - pcb_full.CX for v in (bb.GetX(), bb.GetRight()))
                y0, y1 = (pcb_full.CY - pcbnew.ToMM(v) for v in (bb.GetBottom(), bb.GetY()))
                self.assertFalse(x1 > sx0 - 0.3 and x0 < sx1 + 0.3 and y1 > sy0 - 0.3 and y0 < sy1 + 0.3, "%s pad %s" % (ref, p.GetNumber()))

    def test_module_antenna_points_to_minus_x(self):
        u9 = self.fps["U9"]
        mx, _ = pcb_full.mech_of(pcbnew.ToMM(u9.GetPosition().x), pcbnew.ToMM(u9.GetPosition().y))
        ax1 = mech_outline.antenna_strip()[2]
        self.assertGreater(mx, ax1)                         # the pad area starts at the end of the antenna strip
        self.assertLess(mx, ax1 + 7.0)
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

    def test_without_p1_the_two_sided_rules_stay(self):
        """Plan 08 step 5: P1 unset keeps the old sides and move radius, and no part is marked do-not-populate."""
        self.assertIs(self.info["p1"], False)
        self.assertEqual(self.info["r_move"], pcb_full.R_MOVE)
        self.assertNotIn("led_caps", self.info)
        self.assertTrue(any(f.GetLayer() == pcbnew.B_Cu for r, f in self.fps.items() if not r.startswith("TP")))
        self.assertFalse(self.fps["C4"].IsDNP() or self.fps["C32"].IsDNP())

    def test_star_net_is_the_q3_gate(self):
        net = self.nets["/ILIM_STEP3_EN"]
        self.assertIn(("U15", "4"), net)
        self.assertEqual(pcb_full.STAR["/ILIM_STEP3_EN"], ("U15", "4"))
        for ref in ("R3", "R15", "U4"):     # U13 removed by ADR-0023
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


class P1Switch(unittest.TestCase):
    """Plan 08 section 4.2 (HW-008): the P1 switch and the pure geometry of the LED capacitor search."""

    def test_switch_is_read_from_the_environment_and_off_by_default(self):
        self.assertFalse(pcb_full.p1_enabled({}))
        self.assertFalse(pcb_full.p1_enabled({"P1": "0"}))
        self.assertTrue(pcb_full.p1_enabled({"P1": "1"}))

    def test_sides_of_movable_parts(self):
        self.assertEqual(pcb_full.part_sides("TP1", True), "B")
        self.assertEqual(pcb_full.part_sides("TP1", False), "B")
        self.assertEqual(pcb_full.part_sides("R1", True), "F")
        self.assertEqual(pcb_full.part_sides("R1", False), "FB")
        self.assertAlmostEqual(pcb_full.R_MOVE_P1, 18.4)

    def test_convex_clear(self):
        a = pcb_full.rect_poly(0, 0, 1, 1)
        self.assertTrue(pcb_full.convex_clear(a, pcb_full.rect_poly(1.1, 0, 2, 1), 0.05))
        self.assertFalse(pcb_full.convex_clear(a, pcb_full.rect_poly(1.03, 0, 2, 1), 0.05))   # closer than the gap
        self.assertFalse(pcb_full.convex_clear(a, pcb_full.rect_poly(0.5, 0.5, 2, 2)))       # overlap
        diamond = [(2.0, 0.5), (2.5, 1.0), (2.0, 1.5), (1.5, 1.0)]                         # rotated square, 0.5 mm away
        self.assertTrue(pcb_full.convex_clear(a, diamond, 0.4))
        self.assertFalse(pcb_full.convex_clear(a, diamond, 0.6))


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class P1Board(unittest.TestCase):
    """Plan 08 step 5 (HW-008, HW-016, RV-014 readiness B1 and B3): a board built with P1=1 in a subprocess (the switch is
    read at build time), with a reduced annealing run. The placement is not asserted overlap-free: one side on 46 mm is
    known not to fit (plan 08 A3, R1); the placement gate of section 4.3 is a separate step."""

    SA_ITERS = 4000

    @classmethod
    def setUpClass(cls):
        import os
        import subprocess
        cls.tmp = tempfile.TemporaryDirectory()
        out = cls.tmp.name + "/p1"
        code = ("import sys; sys.path.insert(0, %r); import pcb_full; pcb_full.build(%r, %r, sa_iters=%d, layers=4)"
                % (str(HERE.parent / "src"), str(NETLIST), out, cls.SA_ITERS))
        subprocess.run([sys.executable, "-c", code], env=dict(os.environ, P1="1"), check=True, capture_output=True)
        cls.pcb = out + "/busy_light_spike.kicad_pcb"
        cls.board = pcbnew.LoadBoard(cls.pcb)
        cls.fps = {f.GetReference(): f for f in cls.board.GetFootprints()}
        cls.info = json.loads(Path(cls.pcb).with_suffix(".placement.json").read_text())

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_no_movable_part_touches_the_u9_courtyard(self):
        """Owner decision 2026-11-18 (ADR-0023): with P1 the full U9 courtyard is an obstacle for movable parts. The fixed ring
        parts (LEDs, their capacitors), J1, SW1, fiducials and test points are placed by rule and are not checked here."""
        import re
        u9 = self.fps["U9"].GetCourtyard(pcbnew.F_CrtYd)
        fixed = re.compile(r"^(U9|J1|SW1|FID\d+|TP\d+|D\d+|C(8|9|1\d|2[0-3]))$")
        hits = [r for r, f in self.fps.items() if not fixed.match(r) and f.GetLayer() == pcbnew.F_Cu
                and f.GetCourtyard(pcbnew.F_CrtYd).OutlineCount() and f.GetCourtyard(pcbnew.F_CrtYd).Collide(u9)]
        self.assertEqual(hits, [])

    def centre(self, ref):
        p = self.fps[ref].GetPosition()
        return pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)

    def overlap_mm2(self, a, b):
        ca, cb = self.fps[a].GetCourtyard(pcbnew.F_CrtYd), self.fps[b].GetCourtyard(pcbnew.F_CrtYd)
        self.assertTrue(ca.OutlineCount() and cb.OutlineCount(), (a, b))
        inter = pcbnew.SHAPE_POLY_SET(ca)
        inter.BooleanIntersection(cb)
        return inter.Area() / 1e12

    def test_every_assembled_footprint_is_on_top(self):
        """HW-008 one side: the test points and the do-not-populate HW-016 spares (not assembled) are on the bottom."""
        self.assertIn("J1", self.fps)
        bottom = lambda r: r.startswith("TP") or r in pcb_full.DNP_REFS_P1      # noqa: E731
        bad = [r for r, f in self.fps.items() if f.GetLayer() != (pcbnew.B_Cu if bottom(r) else pcbnew.F_Cu)]
        self.assertEqual(bad, [])
        self.assertEqual(len([r for r in self.fps if r.startswith("TP")]), 6)
        self.assertTrue(all(self.fps[r].IsDNP() for r in pcb_full.DNP_REFS_P1))

    def test_dnp_spares_have_no_solder_paste(self):
        """RV-016 row 17: paste on the DNP spares on the bottom made the bottom paste Gerber non-empty (HW-008)."""
        for ref in pcb_full.DNP_REFS_P1:
            for pad in self.fps[ref].Pads():
                layers = pad.GetLayerSet()
                self.assertFalse(layers.Contains(pcbnew.B_Paste) or layers.Contains(pcbnew.F_Paste), (ref, pad.GetNumber()))
                self.assertTrue(layers.Contains(pcbnew.B_Cu), (ref, pad.GetNumber()))

    def test_spares_are_1206_on_the_rule_that_keeps_them_at_u7(self):
        """HW-016 (Approved): two 1206 footprints; the placer rule keeps their centres within 7.0 mm of U7 (pad centres
        then within [10] mm of pin 6; RV-016 row 19). The reduced annealing run of this test is not asserted to meet the
        rule; the batch board is (tests/test_board_p1.py)."""
        for ref in pcb_full.DNP_REFS_P1:
            self.assertEqual(str(self.fps[ref].GetFPID().GetLibItemName()), "C_1206_3216Metric", ref)
            self.assertIn((ref, "U7", 7.0), pcb_full.LAYOUT_RULES)

    def test_led_capacitors_keep_out_of_the_tab_boxes(self):
        """Plan 08 section 4.5: no LED capacitor courtyard meets the box around a P1 panel tab cut."""
        boxes = pcb_full.tab_keepouts()
        self.assertEqual(len(boxes), len(pcb_full.pcb_rules.P1_TAB_AZIMUTHS))
        bad = [(c, name) for _, c, _ in pcb_full.led_ring_refs() for name, box in boxes
               if not pcb_full.convex_clear(pcb_full.court_poly_mm(self.fps[c]), box, pcb_full.LED_CAP_GAP)]
        self.assertEqual(bad, [])

    def test_tab_azimuths_equal_the_order_script_default(self):
        import re
        txt = (HERE.parents[3] / "scripts" / "fab_p1.sh").read_text(encoding="utf-8")
        got = re.search(r'TAB_AZIMUTHS="\$\{TAB_AZIMUTHS:-([0-9.,]+)\}"', txt).group(1)
        self.assertEqual(tuple(float(a) for a in got.split(",")), pcb_full.pcb_rules.P1_TAB_AZIMUTHS)

    def test_led_capacitors_sit_beside_their_led_on_top(self):
        for d, c, _ in pcb_full.led_ring_refs():
            self.assertEqual(self.fps[c].GetLayer(), pcbnew.F_Cu, c)
            self.assertLessEqual(math.dist(self.centre(c), self.centre(d)), 3.5, c)
            self.assertIn(c, self.info["led_caps"])

    def test_led_capacitor_long_axis_is_radial(self):
        for d, c, _ in pcb_full.led_ring_refs():
            pads = {p.GetNumber(): p.GetPosition() for p in self.fps[c].Pads()}
            vx, vy = pcbnew.ToMM(pads["1"].x - pads["2"].x), pcbnew.ToMM(pads["1"].y - pads["2"].y)
            rx, ry = self.centre(d)[0] - pcb_full.CX, self.centre(d)[1] - pcb_full.CY
            self.assertGreater(abs(vx * rx + vy * ry) / (math.hypot(vx, vy) * math.hypot(rx, ry)), 0.99, c)

    def test_led_capacitors_clear_j1_the_leds_and_each_other(self):
        """RV-014 readiness B3: no capacitor courtyard meets J1 (courtyard or pad extent), an LED or another capacitor."""
        caps = [c for _, c, _ in pcb_full.led_ring_refs()]
        leds = [d for d, _, _ in pcb_full.led_ring_refs()]
        jx0, jy0, jx1, jy1 = pcb_full.pad_extent_mm(self.fps["J1"], 0.0)
        bad = []
        for c in caps:
            bad += [(c, o) for o in leds + ["J1"] + [x for x in caps if x > c] if self.overlap_mm2(c, o) > 0.0]
            poly = pcb_full.court_poly_mm(self.fps[c])
            if not pcb_full.convex_clear(poly, pcb_full.rect_poly(jx0, jy0, jx1, jy1)):
                bad.append((c, "J1 pads"))
        self.assertEqual(bad, [])

    def test_placement_json_records_the_switch(self):
        self.assertIs(self.info["p1"], True)
        self.assertAlmostEqual(self.info["r_move"], 18.4)
        self.assertEqual(self.info["sa_iters"], self.SA_ITERS)

    def test_sourcing_fields_on_every_footprint(self):
        import sourcing
        self.assertEqual(self.fps["U7"].GetField("LCSC").GetText(), "C55266")
        self.assertEqual(sourcing.sourcing_fields(self.fps["U7"].GetValue())["LCSC"], "C55266")
        for ref, f in self.fps.items():
            want = sourcing.sourcing_fields(f.GetValue(), str(f.GetFPID().GetLibItemName()))
            for k in sourcing.FIELDS:
                fld = f.GetField(k)
                self.assertIsNotNone(fld, (ref, k))
                self.assertEqual(fld.GetText(), want[k], (ref, k))
                self.assertFalse(fld.IsVisible(), (ref, k))

    def test_spare_capacitors_are_dnp_and_out_of_the_bom(self):
        for ref in ("C4", "C32"):
            self.assertTrue(self.fps[ref].IsDNP(), ref)
            self.assertTrue(self.fps[ref].IsExcludedFromBOM(), ref)
        self.assertFalse(self.fps["C2"].IsDNP() or self.fps["C2"].IsExcludedFromBOM())

    def test_ring_links_follow_the_capacitor_layer(self):
        import pcb_ring
        self.assertEqual({pcb_ring.cap_link_layer(self.board, c) for _, c in pcb_ring.cells()}, {"F.Cu"})


if __name__ == "__main__":
    unittest.main()


def test_project_switches_on_default_ignored_drc_checks(tmp_path):
    import json

    import pcb_full

    pro = tmp_path / "x.kicad_pro"
    pcb_full.write_project(str(pro), "x")
    sev = json.loads(pro.read_text())["board"]["design_settings"]["rule_severities"]
    assert set(sev) == set(pcb_full.DRC_ON) and set(sev.values()) == {"warning"}


def test_project_switches_on_default_ignored_erc_checks(tmp_path):
    """The strict ERC counts every ignored check, so the board project of a stored board must switch them on."""
    import json

    import lib_tables
    import pcb_full

    pro = tmp_path / "x.kicad_pro"
    pcb_full.write_project(str(pro), "x")
    sev = json.loads(pro.read_text())["erc"]["rule_severities"]
    assert set(sev) == set(lib_tables.ERC_ON) and set(sev.values()) == {"warning"}


def test_u9_footprint_is_the_datasheet_land_pattern(tmp_path):
    """ESP32-C3-MINI-1 datasheet v2.2 figure 11-1: 48 pads 0.8 x 0.4, 4 corner pads 0.7, 3 x 3 ground pads 1.45;
    pad rows 11.9 mm apart (x) and 9.9 mm apart (y)."""
    import re

    pcb_full.derive_u9_footprint(str(tmp_path))
    text = (tmp_path / "CUSTOM.pretty" / "ESP32-C3-MINI-1.kicad_mod").read_text()
    pads = re.findall(r'\(pad "(\w+)" \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+)[^)]*\)\s*\(size ([\d.]+) ([\d.]+)\)', text)
    sizes = sorted((float(p[3]), float(p[4])) for p in pads)
    assert sizes.count((0.4, 0.8)) + sizes.count((0.8, 0.4)) == 48
    assert sizes.count((0.7, 0.7)) == 4 and sizes.count((1.45, 1.45)) == 9
    assert "(zone " not in text and "(model" not in text
    corners = [(float(p[1]), float(p[2])) for p in pads if p[0] in ("50", "51", "52", "53")]
    assert sorted({abs(x) for x, _ in corners}) == [5.95] and sorted({abs(y) for _, y in corners}) == [4.95]


def test_u1_footprint_is_the_ti_drawing():
    """TI RWB0012A example board layout: 0.7 x 0.2 side pads, 0.2 x 0.5 end pads, pitch 0.4, pad 1 top left."""
    import custom_fp

    pads = {n: (x, y, w, h) for n, x, y, w, h in custom_fp.pads()}
    assert len(pads) == 12
    assert pads["1"] == (-0.65, -0.2, 0.7, 0.2) and pads["2"] == (-0.65, 0.2, 0.7, 0.2)
    assert pads["3"][:2] == (-0.6, 0.75) and pads["6"][:2] == (0.6, 0.75)
    assert pads["7"][:2] == (0.65, 0.2) and pads["8"][:2] == (0.65, -0.2)
    assert pads["9"][:2] == (0.6, -0.75) and pads["12"][:2] == (-0.6, -0.75)
    assert all((w, h) == (0.2, 0.5) for n, (x, y, w, h) in pads.items() if n in "3456" or n in ("9", "10", "11", "12"))


def test_j1_footprint_has_no_silk_at_the_board_edge():
    """The three silk lines of the connector front are dropped (silk_edge_clearance); the rest of the stock footprint stays."""
    import custom_fp

    t = Path("/usr/share/kicad/footprints/Connector_USB.pretty/USB_C_Receptacle_GCT_USB4085.kicad_mod").read_text()
    u = custom_fp.j1_mod(t)
    assert t.count("(fp_line") - u.count("(fp_line") == 3
    assert u.count("(pad ") == t.count("(pad ") and u.count("(") == u.count(")")
    assert '"%s"' % custom_fp.J1_NAME in u and '"%s"' % custom_fp.J1_STOCK not in u


@unittest.skipIf(pcbnew is None, "needs KiCad pcbnew")
class AntennaKeepout(unittest.TestCase):
    """PLACE_ANT_KEEPOUT=1: no movable part in the vendor keep-out (15 mm beyond the module end, module width)."""

    def test_no_movable_part_in_the_vendor_keepout(self):
        import os
        old = os.environ.get("PLACE_ANT_KEEPOUT")
        os.environ["PLACE_ANT_KEEPOUT"] = "1"
        try:
            with tempfile.TemporaryDirectory() as t:
                board = pcbnew.LoadBoard(pcb_full.build(str(NETLIST), t + "/a"))
        finally:
            if old is None:
                os.environ.pop("PLACE_ANT_KEEPOUT")
            else:
                os.environ["PLACE_ANT_KEEPOUT"] = old
        fps = {f.GetReference(): f for f in board.GetFootprints()}
        mb = fps["U9"].GetBoundingBox(False)
        x0, x1 = mb.GetLeft() - 15_000_000, mb.GetLeft()
        y0, y1 = mb.GetTop(), mb.GetBottom()
        fixed = {"U9", "J1", "SW1"}
        for ref, f in fps.items():
            led = (ref[0] == "D" and ref[1:].isdigit()) or (ref[0] == "C" and ref[1:].isdigit() and 8 <= int(ref[1:]) <= 23)
            if ref in fixed or led:
                continue
            b = f.GetBoundingBox(False)
            inside = b.GetRight() > x0 and b.GetLeft() < x1 and b.GetBottom() > y0 and b.GetTop() < y1
            self.assertFalse(inside, ref)
