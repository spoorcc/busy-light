# SPDX-License-Identifier: Apache-2.0
"""PCB spike: the mechanical envelope table and the placer (pure Python, no KiCad needed)."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import mech_outline as MO  # noqa: E402
import pcb_place  # noqa: E402


class Table(unittest.TestCase):
    def test_every_number_has_a_source(self):
        for k, (v, src) in MO.MECH.items():
            self.assertTrue(src.strip(), k)

    def test_values_from_the_mech_spike(self):
        self.assertEqual(MO.m("D_PCB"), 46.0)
        self.assertEqual(MO.m("N_LED"), 16)
        self.assertEqual(MO.m("D_RING"), 40.0)
        self.assertEqual(MO.m("POST_AZ"), (30.0, 150.0, 270.0))
        self.assertEqual(MO.m("MOD_OFF"), 1.0)

    def test_antenna_strip_is_the_datasheet_length(self):
        """ESP32-C3-MINI-1 datasheet fig 11-1: 16.6 mm - 11.2 mm pad area - 0.8 mm = 4.6 mm."""
        self.assertAlmostEqual(MO.m("MOD_ANT_L"), 16.6 - 11.2 - 0.8, places=6)
        ax0, _, ax1, _ = MO.antenna_strip()
        self.assertAlmostEqual(ax1 - ax0, 4.6, places=6)

    def test_slot_lies_between_antenna_end_and_the_ring_and_cuts_no_ring_led(self):
        sx0, sy0, sx1, sy1 = MO.slot_rect()
        mx0 = MO.module_rect()[0]
        self.assertLess(sx1, mx0)
        self.assertAlmostEqual(mx0 - sx1, MO.m("SLOT_GAP"))
        self.assertAlmostEqual(sx1 - sx0, MO.m("SLOT_W"))
        self.assertGreater(sy1 - sy0, MO.m("MOD_W"))                       # covers the module width
        r_ring = MO.m("D_RING") / 2.0
        for corner in ((sx0, sy0), (sx0, sy1), (sx1, sy0), (sx1, sy1)):
            self.assertLess(math.hypot(*corner), r_ring - 3.0)           # well inside the ring
        self.assertEqual(len(MO.slot_segments()), 4)

    def test_points_in_or_near_the_slot_are_not_inside_the_pcb(self):
        sx0, sy0, sx1, sy1 = MO.slot_rect()
        cx, cy = (sx0 + sx1) / 2, (sy0 + sy1) / 2
        self.assertFalse(MO.inside_pcb(cx, cy))
        self.assertFalse(MO.inside_pcb(sx1 + 0.2, cy, 0.6))
        self.assertTrue(MO.inside_pcb(sx1 + 1.0, cy, 0.3))

    def test_parts_are_kept_off_the_slot(self):
        sx0, sy0, sx1, sy1 = MO.slot_rect()
        self.assertFalse(MO.region_rect_ok("F", sx0 - 1.5, 0, sx0 - 0.3, 1.0))   # within 0.6 mm of the slot
        self.assertFalse(MO.region_rect_ok("B", sx0 - 0.5, 0, sx1 + 0.5, 1.0))

    def test_mouth_and_largest_dimension_match_the_mech_report(self):
        self.assertAlmostEqual(MO.USB_MOUTH_R, 29.85, places=2)
        self.assertAlmostEqual(MO.largest_dim_mm(MO.USB_MOUTH_R), 57.45, places=2)   # report 4.1: 57.43
        self.assertLess(MO.largest_dim_mm(MO.USB_MOUTH_R), MO.m("MAX_DIM_MECH001"))

    def test_led_azimuths(self):
        az = MO.led_azimuths()
        self.assertEqual(len(az), 16)
        self.assertAlmostEqual(az[0], 3.75)
        self.assertAlmostEqual(az[1] - az[0], 22.5)
        self.assertAlmostEqual(240.0 - az[10], 11.25)       # the button azimuth is the middle of a gap

    def test_outline_is_closed_and_inside_the_limits(self):
        seg = MO.outline_segments(31.3)
        pts = []
        for s in seg:
            pts.append((s[1], s[-1]))
        for a, b in zip(pts, pts[1:] + pts[:1]):
            self.assertAlmostEqual(a[1][0], b[0][0], places=6)
            self.assertAlmostEqual(a[1][1], b[0][1], places=6)

    def test_posts_keepouts_and_cap_shift(self):
        self.assertEqual(len(MO.post_keepouts()), 3)
        self.assertEqual(MO.led_cap_shift_mm(1, MO.led_azimuths()[1]), -2.5)     # LED at 26.25 deg next to the post at 30
        self.assertEqual(MO.led_cap_shift_mm(12, MO.led_azimuths()[12]), 2.5)    # 273.75 next to 270
        self.assertEqual(MO.led_cap_shift_mm(5, MO.led_azimuths()[5]), 0.0)

    def test_region_excludes_module_and_antenna(self):
        self.assertFalse(MO.region_rect_ok("F", 0, -1, 2, 1))
        self.assertFalse(MO.region_rect_ok("B", -5, -1, -3, 1))
        self.assertTrue(MO.region_rect_ok("B", 5, -1, 7, 1))
        self.assertFalse(MO.region_rect_ok("F", 18, 0, 20, 1))       # beyond the move radius


class Placer(unittest.TestCase):
    def test_deterministic_and_overlap_free(self):
        parts = {"A": {"w": 2, "h": 1, "pads": {"1": (-1, 0), "2": (1, 0)}},
                 "B": {"w": 2, "h": 1, "pads": {"1": (-1, 0), "2": (1, 0)}},
                 "C": {"w": 2, "h": 1, "pads": {"1": (-1, 0), "2": (1, 0)}}}
        nets = {"n1": [("A", "2"), ("B", "1")], "n2": [("B", "2"), ("C", "1"), ("F", "1")]}
        fixed_pins = {("F", "1"): (5.0, 0.0)}

        def ok(side, x0, y0, x1, y1):
            return all(math.hypot(x, y) <= 10 for x in (x0, x1) for y in (y0, y1))
        r1 = pcb_place.place(parts, nets, fixed_pins, [], ok, seeds=(1,), iters=4000)
        r2 = pcb_place.place(parts, nets, fixed_pins, [], ok, seeds=(1,), iters=4000)
        self.assertEqual(r1[0], r2[0])
        self.assertEqual(r1[3], 0.0)


if __name__ == "__main__":
    unittest.main()
