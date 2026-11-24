# SPDX-License-Identifier: Apache-2.0
"""Centre button zone geometry of plan 09 (pure Python, reads the stored board-p1 text; MECH-004, MECH-003)."""
import io
import math
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import button_zone as bz  # noqa: E402
import mech_outline as MO  # noqa: E402

PCB = bz.BOARD_P1.read_text(encoding="utf-8")
LEDS = bz.led_squares()


def size(poly):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return max(xs) - min(xs), max(ys) - min(ys)


class Outlines(unittest.TestCase):
    def test_sw1_body_and_courtyard_of_the_stored_board(self):
        w, h = size(bz.read_footprint_outline(PCB, "SW1"))
        self.assertAlmostEqual(w, 6.4, places=3)
        self.assertAlmostEqual(h, 5.2, places=3)
        cw, ch = size(bz.read_footprint_outline(PCB, "SW1", layer="F.CrtYd"))
        self.assertAlmostEqual(cw, 8.5, places=3)
        self.assertAlmostEqual(ch, 6.0, places=3)

    def test_u9_body_is_rotated_and_centred_on_the_board_centre(self):
        body = bz.read_footprint_outline(PCB, "U9")
        w, h = size(body)
        self.assertAlmostEqual(w, 16.6, places=3)
        self.assertAlmostEqual(h, 13.2, places=3)
        self.assertAlmostEqual(min(p[0] for p in body), -13.4, places=3)
        self.assertAlmostEqual(max(p[0] for p in body), 3.2, places=3)

    def test_unknown_reference_or_layer_raises(self):
        with self.assertRaises(ValueError):
            bz.read_footprint_outline(PCB, "U99")
        with self.assertRaises(ValueError):
            bz.read_footprint_outline(PCB, "SW1", layer="B.Fab")

    def test_antenna_strip_is_4p6_mm_from_the_min_x_end(self):
        body = bz.read_footprint_outline(PCB, "U9")
        strip = bz.antenna_strip(body)
        self.assertAlmostEqual(size(strip)[0], 4.6, places=6)
        self.assertAlmostEqual(min(p[0] for p in strip), -13.4, places=3)
        far = bz.antenna_strip(body, end="max_x")
        self.assertAlmostEqual(max(p[0] for p in far), 3.2, places=3)
        with self.assertRaises(ValueError):
            bz.antenna_strip(body, end="top")

    def test_led_squares(self):
        self.assertEqual(len(LEDS), 16)
        for k, led in enumerate(LEDS):
            cx, cy = bz._centre(led)
            self.assertAlmostEqual(math.hypot(cx, cy), 20.0, places=6)
            az = math.degrees(math.atan2(cy, cx)) % 360
            self.assertAlmostEqual(az, (3.75 + 22.5 * k) % 360, places=6)
            self.assertAlmostEqual(math.dist(led[0], led[1]), 2.0, places=6)


class Baseline(unittest.TestCase):
    def test_stored_board_baseline_is_5p06_mm(self):
        strip = bz.antenna_strip(bz.read_footprint_outline(PCB, "U9"))
        self.assertAlmostEqual(bz.nearest_led_distance(strip, LEDS), 5.06, delta=0.1)

    def test_mech_outline_baseline_is_6p07_mm(self):
        x0, y0, x1, y1 = MO.module_rect()
        body = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        self.assertAlmostEqual(bz.nearest_led_distance(bz.antenna_strip(body), LEDS), 6.07, delta=0.1)

    def test_distance_helpers(self):
        a = bz.rect(0, 0, 2, 2, 0)
        b = bz.rect(5, 0, 2, 2, 0)
        self.assertAlmostEqual(bz.poly_distance(a, b), 3.0, places=9)
        self.assertEqual(bz.poly_distance(a, bz.rect(1, 0, 2, 2, 0)), 0.0)
        self.assertAlmostEqual(bz.point_poly_distance((4, 0), a), 3.0, places=9)
        self.assertEqual(bz.point_poly_distance((0, 0), a), 0.0)


class S2(unittest.TestCase):
    """Coarse grid (1 mm, 6 degrees) keeps the test fast; the report uses 0.5 mm and 3 degrees."""

    @classmethod
    def setUpClass(cls):
        args = (bz.MODULE_SIZE,)
        cls.tl = bz.s2_poses(*args, bz.SWITCH_TL3342, 1.0, 0.5, 19.5, 14.0, 1.0, 6.0)
        cls.b3u = bz.s2_poses(*args, bz.SWITCH_B3U, 1.0, 0.5, 19.5, 14.0, 1.0, 6.0)
        strip = bz.antenna_strip(bz.read_footprint_outline(PCB, "U9"))
        cls.base = bz.nearest_led_distance(strip, LEDS)

    def test_no_pose_overlaps_the_switch_or_an_led(self):
        sw = bz.rect(0, 0, *bz.SWITCH_TL3342, 0)
        for x, y, ang in self.tl:
            body = bz.rect(x, y, *bz.MODULE_SIZE, ang)
            self.assertGreaterEqual(bz.poly_distance(body, sw), 1.0 - 1e-6)
            for led in LEDS:
                self.assertGreaterEqual(bz.poly_distance(body, led), 0.5 - 1e-6)

    def test_best_distance_is_below_the_baseline_and_the_small_switch_is_better(self):
        d_tl = bz.best_antenna_distance(self.tl, leds=LEDS)
        d_b3u = bz.best_antenna_distance(self.b3u, leds=LEDS)
        self.assertLess(d_tl, self.base)
        self.assertLess(d_b3u, self.base)
        self.assertGreater(d_b3u, d_tl)
        self.assertGreater(len(self.b3u), len(self.tl))

    def test_no_pose_gives_zero(self):
        self.assertEqual(bz.best_antenna_distance([]), 0.0)

    def test_gap_zero_means_no_overlap(self):
        courtyard = bz.s2_poses(bz.MODULE_SIZE, bz.SWITCH_TL3342_COURTYARD, 0.0, 0.5, 19.5, 14.0, 1.0, 6.0)
        sw = bz.rect(0, 0, *bz.SWITCH_TL3342_COURTYARD, 0)
        for x, y, ang in courtyard:
            self.assertGreater(bz.poly_distance(bz.rect(x, y, *bz.MODULE_SIZE, ang), sw), 0.0)


class S3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = bz.read_footprint_outline(PCB, "U9")
        cls.strip = bz.antenna_strip(cls.body)

    def test_the_real_switch_body_barely_fits_and_the_courtyard_does_not(self):
        ok, total, _, _ = bz.s3_scan(11.0, bz.SWITCH_TL3342, 0.0, self.body, self.strip, LEDS)
        self.assertEqual(total, 480)
        self.assertLessEqual(ok, 20)
        ok_c, _, gb, gs = bz.s3_scan(11.0, bz.SWITCH_TL3342_COURTYARD, 0.0, self.body, self.strip, LEDS)
        self.assertEqual(ok_c, 0)
        self.assertEqual((gb, gs), (0.0, 0.0))

    def test_the_small_switch_fits_more_often(self):
        ok_tl, *_ = bz.s3_scan(11.0, bz.SWITCH_TL3342, 0.0, self.body, self.strip, LEDS)
        ok_b3u, _, gb, gs = bz.s3_scan(11.0, bz.SWITCH_B3U, 0.0, self.body, self.strip, LEDS)
        self.assertGreater(ok_b3u, ok_tl)
        self.assertGreater(gb, 0.0)
        self.assertGreater(gs, 0.0)

    def test_conflict_strings(self):
        led0 = bz._centre(LEDS[0])
        msgs = bz.s3_conflicts([(-2.4, 0.0), led0], bz.SWITCH_B3U, 0.0, self.body, self.strip, LEDS, 0.0)
        self.assertIn("SW0 overlaps module", msgs)
        self.assertIn("SW1 overlaps LED0", msgs)
        self.assertNotIn("SW1 overlaps module", msgs)
        self.assertEqual(bz.s3_conflicts([(10.0, 0.0)], bz.SWITCH_B3U, 0.0, self.body, self.strip, LEDS, 0.0), [])


class Fill(unittest.TestCase):
    def test_fill_fraction_reproduces_the_plan_figures(self):
        self.assertAlmostEqual(bz.fill_fraction(430.0, 650.0), 0.6615, places=3)
        self.assertAlmostEqual(bz.fill_fraction(430.0, 650.0, extra_movable_mm2=102.0), 0.8185, places=3)
        self.assertAlmostEqual(bz.fill_fraction(430.0, 650.0, fixed_delta_mm2=14.0 - 51.0), 0.6259, places=3)


class Report(unittest.TestCase):
    def test_main_prints_the_s2_and_s3_results(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            bz.main()
        out = buf.getvalue()
        self.assertIn("antenna strip to nearest LED centre 5.06 mm", out)
        self.assertIn("S2:", out)
        self.assertIn("S3:", out)
        self.assertIn("7 of 480 feasible", out)


if __name__ == "__main__":
    unittest.main()
