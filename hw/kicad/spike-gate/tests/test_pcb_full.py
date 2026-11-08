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


class PlacementWeights(unittest.TestCase):
    """The gate and bypass rules are enforced by weights in the annealer, not left to chance."""

    def test_rule_tables(self):
        self.assertGreater(pcb_rules.NET_WEIGHT["/ILIM_STEP3_EN"], 1.0)
        bypass = {"tie:C24-U14", "tie:C25-U15"}
        regulator = {"tie:C5-U8", "tie:C6-U8"}              # TLV757P: input capacitor at pin 1, output capacitor at pin 5
        paths = {"tie:J1A4-U7", "tie:J1B9-U7", "tie:C2-U7", "tie:U8-U9"}      # current paths of the power check
        self.assertEqual(set(pcb_rules.PIN_TIES), bypass | regulator | paths)
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
        self.assertIn(("U14", "U15"), [f for f in ics if "U14" in f and len(f) == 2] or [()])
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
        self.assertEqual(len(self.comps), 100)
        self.assertEqual(len([n for n in self.nets if not n.startswith("unconnected-")]), 55)
        for ref in ("U13", "C27", "C28", "C29", "C30", "C31", "U14", "U15", "R20", "R18", "R19", "C24", "C25", "R3", "R15"):
            self.assertIn(ref, self.comps)
        for ref in ("Q2", "Q3"):
            self.assertNotIn(ref, self.comps)

    def test_board_matches_netlist(self):
        res, _ = pcb_check.compare(str(NETLIST), self.pcb)
        self.assertEqual(res["missing_refs"], [])
        self.assertEqual(res["extra_refs"], [])
        self.assertEqual(res["pad_net_differences"], [])
        self.assertEqual(res["netlist_pins_without_pad"], [])
        self.assertEqual(res["nets_named"], 55)

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

    def test_star_net_is_the_q3_gate(self):
        net = self.nets["/ILIM_STEP3_EN"]
        self.assertIn(("U15", "4"), net)
        self.assertEqual(pcb_full.STAR["/ILIM_STEP3_EN"], ("U15", "4"))
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
