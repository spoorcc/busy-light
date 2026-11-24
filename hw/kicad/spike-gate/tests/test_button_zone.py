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

    def test_the_stored_module_pose_reproduces_the_baseline_through_the_pose_functions(self):
        body = bz.read_footprint_outline(PCB, "U9")
        cx = (min(p[0] for p in body) + max(p[0] for p in body)) / 2
        # rotated 90 degrees, the local -y antenna end points to +x; flipped it points to -x as on the board
        self.assertAlmostEqual(bz.antenna_distance((cx, 0.0, 90.0), True, leds=LEDS), 5.0628, delta=0.005)
        self.assertGreater(bz.antenna_distance((cx, 0.0, 90.0), False, leds=LEDS), 5.0628)

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

    def test_distance_of_rotated_squares_and_crossing_bars(self):
        d = bz.poly_distance(bz.rect(0, 0, 2, 2, 45), bz.rect(5, 0, 2, 2, 45))
        self.assertAlmostEqual(d, 5.0 - 2 * math.sqrt(2.0), places=9)
        # a plus sign: no corner of either bar lies inside the other, the edges cross
        self.assertEqual(bz.poly_distance(bz.rect(0, 0, 10, 1, 0), bz.rect(0, 0, 1, 10, 0)), 0.0)


class S2(unittest.TestCase):
    """Full grid (0.5 mm, 3 degrees) as in the report; pins the pose counts and the best distances."""

    @classmethod
    def setUpClass(cls):
        def poses(switch, gap, corner=19.5):
            return bz.s2_poses(bz.MODULE_SIZE, switch, gap, 0.5, corner, 14.0, 0.5, 3.0)

        cls.tl = poses(bz.SWITCH_TL3342, 1.0)
        cls.yard = poses(bz.SWITCH_TL3342_COURTYARD, 0.0)
        cls.b3u = poses(bz.SWITCH_B3U, 1.0)
        cls.b3u_pad = poses((4.0, 3.5), 1.0)
        cls.yard_free = poses(bz.SWITCH_TL3342_COURTYARD, 0.0, corner=1e9)
        cls.yard_19 = poses(bz.SWITCH_TL3342_COURTYARD, 0.0, corner=19.0)

    def test_pose_counts_are_pinned(self):
        self.assertEqual(
            [len(self.tl), len(self.yard), len(self.b3u), len(self.b3u_pad)], [10, 58, 1330, 428]
        )
        self.assertEqual([len(self.yard_free), len(self.yard_19)], [134, 12])

    def test_best_distances_are_pinned(self):
        for poses, expect in ((self.tl, 2.51), (self.yard, 3.04), (self.b3u, 3.90), (self.b3u_pad, 3.64)):
            self.assertAlmostEqual(bz.best_antenna_distance(poses, leds=LEDS), expect, delta=0.006)
        self.assertAlmostEqual(bz.best_antenna_distance(self.yard_free, leds=LEDS), 3.57, delta=0.006)
        self.assertAlmostEqual(bz.best_antenna_distance(self.yard_19, leds=LEDS), 2.86, delta=0.006)

    def test_the_metal_switch_rule_lowers_the_b3u_result(self):
        away = bz.best_antenna_distance(self.b3u, leds=LEDS, switch_size=bz.SWITCH_B3U, away_from_switch=True)
        far = bz.best_antenna_distance(self.b3u, leds=LEDS, switch_size=bz.SWITCH_B3U, min_switch_strip_mm=3.0)
        self.assertAlmostEqual(away, 3.64, delta=0.006)
        self.assertAlmostEqual(far, 3.55, delta=0.006)
        self.assertLess(far, away)
        self.assertLess(away, bz.best_antenna_distance(self.b3u, leds=LEDS))
        self.assertEqual(
            bz.best_antenna_distance(self.tl, leds=LEDS, switch_size=bz.SWITCH_TL3342, min_switch_strip_mm=3.0), 0.0
        )

    def test_every_pose_keeps_the_gaps_and_the_corner_limit(self):
        for poses, switch, gap in (
            (self.tl, bz.SWITCH_TL3342, 1.0),
            (self.yard, bz.SWITCH_TL3342_COURTYARD, 0.0),
            (self.b3u, bz.SWITCH_B3U, 1.0),
        ):
            sw = bz.rect(0, 0, *switch, 0)
            for x, y, ang in poses:
                body = bz.rect(x, y, *bz.MODULE_SIZE, ang)
                d = bz.poly_distance(body, sw)
                self.assertGreaterEqual(d, gap - 1e-6)
                self.assertGreater(d, 0.0)
                self.assertLessEqual(max(math.hypot(*p) for p in body), 19.5 + 1e-6)
                self.assertTrue(0.0 <= ang <= 177.0)
                for led in LEDS:
                    self.assertGreaterEqual(bz.poly_distance(body, led), 0.5 - 1e-6)

    def test_poses_cover_the_angles_and_both_ends_matter(self):
        angles = {a for _, _, a in self.b3u}
        self.assertGreater(max(angles), 90.0)  # rotation is not limited to a quarter turn
        flipped_better = any(
            bz.antenna_distance(p, True, leds=LEDS) > bz.antenna_distance(p, False, leds=LEDS) for p in self.b3u
        )
        self.assertTrue(flipped_better)

    def test_best_over_no_poses_is_zero(self):
        self.assertEqual(bz.best_antenna_distance([]), 0.0)


class S3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = bz.read_footprint_outline(PCB, "U9")
        cls.strip = bz.antenna_strip(cls.body)

    def test_the_real_switch_body_barely_fits_and_the_courtyard_does_not(self):
        ok, total, gb, gs = bz.s3_scan(11.0, bz.SWITCH_TL3342, 0.0, self.body, self.strip, LEDS)
        self.assertEqual((ok, total), (7, 480))
        self.assertAlmostEqual(gb, 0.33, delta=0.01)
        self.assertAlmostEqual(gs, 0.34, delta=0.01)
        ok_c, _, gbc, gsc = bz.s3_scan(11.0, bz.SWITCH_TL3342_COURTYARD, 0.0, self.body, self.strip, LEDS)
        self.assertEqual((ok_c, gbc, gsc), (0, 0.0, 0.0))

    def test_the_small_switch_fits_more_often_and_one_mm_clearance_costs_most_of_them(self):
        ok0, _, gb, gs = bz.s3_scan(11.0, bz.SWITCH_B3U, 0.0, self.body, self.strip, LEDS)
        ok1, _, gb1, gs1 = bz.s3_scan(11.0, bz.SWITCH_B3U, 1.0, self.body, self.strip, LEDS)
        self.assertEqual((ok0, ok1), (92, 22))
        self.assertAlmostEqual(gb, 1.68, delta=0.01)
        self.assertAlmostEqual(gs, 2.97, delta=0.01)
        self.assertAlmostEqual(gs1, 2.50, delta=0.01)
        self.assertAlmostEqual(gb1, 1.68, delta=0.01)

    def test_conflict_strings(self):
        led0 = bz._centre(LEDS[0])
        msgs = bz.s3_conflicts([(-2.4, 0.0), led0], bz.SWITCH_B3U, 0.0, self.body, self.strip, LEDS, 0.0)
        self.assertIn("SW0 overlaps module", msgs)
        self.assertIn("SW1 overlaps LED0", msgs)
        self.assertNotIn("SW1 overlaps module", msgs)
        near = bz.s3_conflicts([(-11.0, 0.0)], bz.SWITCH_B3U, 0.0, self.body, self.strip, LEDS, 0.0)
        self.assertIn("SW0 overlaps antenna strip", near)
        self.assertEqual(bz.s3_conflicts([(10.0, 0.0)], bz.SWITCH_B3U, 0.0, self.body, self.strip, LEDS, 0.0), [])


class Fill(unittest.TestCase):
    def test_fill_fraction_reproduces_the_plan_figures(self):
        self.assertAlmostEqual(bz.fill_fraction(430.0, 650.0), 0.6615, places=3)
        self.assertAlmostEqual(bz.fill_fraction(430.0, 650.0, extra_movable_mm2=102.0), 0.8185, places=3)
        self.assertAlmostEqual(bz.fill_fraction(430.0, 650.0, fixed_delta_mm2=14.0 - 51.0), 0.6259, places=3)
        self.assertAlmostEqual(bz.fill_fraction(430.0, 650.0, fixed_delta_mm2=42.0 - 51.0), 0.6525, places=3)
        self.assertAlmostEqual(bz.fill_fraction(430.0, 650.0, fixed_delta_mm2=153.0 - 51.0), 0.7847, places=3)


class Report(unittest.TestCase):
    def test_main_prints_the_s2_and_s3_results(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            bz.main()
        out = buf.getvalue()
        self.assertIn("antenna strip to nearest LED centre 5.06 mm", out)
        self.assertIn("1330 poses", out)
        self.assertIn("antenna end away from the switch 3.64 mm", out)
        self.assertIn("clearance 1: 22 of 480", out)
        self.assertIn("7 of 480 feasible", out)
        self.assertIn("S3 with three B3U: 65 %", out)


if __name__ == "__main__":
    unittest.main()
