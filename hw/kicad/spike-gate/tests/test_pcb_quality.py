# SPDX-License-Identifier: Apache-2.0
"""Tests for the layout quality numbers (pcb_quality.py): geometry only, no pcbnew."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import pcb_quality as Q  # noqa: E402

MM = 1_000_000.0


def seg(a, b, net="N", layer=0):
    return (net, layer, (a[0] * MM, a[1] * MM), (b[0] * MM, b[1] * MM))


class Angles(unittest.TestCase):
    def test_multiples_of_45_are_on_grid(self):
        for d in ((1, 0), (0, 1), (-1, 0), (1, 1), (-1, 1), (1, -1), (0, -3)):
            self.assertFalse(Q.off_grid_angle(*d), d)

    def test_other_angles_are_off_grid(self):
        self.assertTrue(Q.off_grid_angle(2, 1))
        self.assertTrue(Q.off_grid_angle(10, 1))

    def test_zero_length_is_on_grid(self):
        self.assertFalse(Q.off_grid_angle(0, 0))

    def test_corner_angle(self):
        self.assertAlmostEqual(Q.corner_angle((1, 0), (0, 1)), 90.0)
        self.assertAlmostEqual(Q.corner_angle((1, 0), (1, 1)), 45.0)
        self.assertAlmostEqual(Q.corner_angle((1, 0), (-1, 0)), 180.0)


class Metrics(unittest.TestCase):
    def test_clean_staircase_has_no_findings(self):
        m = Q.metrics_of([seg((0, 0), (5, 0)), seg((5, 0), (8, 3)), seg((8, 3), (8, 9))], vias=2)
        self.assertEqual((m["off45_segments"], m["sharp_corners"], m["vias"]), (0, 0, 2))
        self.assertAlmostEqual(m["track_mm"], 5 + 3 * 2 ** 0.5 + 6, places=1)

    def test_off_grid_segment_is_counted_with_its_length(self):
        m = Q.metrics_of([seg((0, 0), (4, 2))], vias=0)
        self.assertEqual(m["off45_segments"], 1)
        self.assertAlmostEqual(m["off45_mm"], 20 ** 0.5, places=1)

    def test_sharp_corner_needs_the_same_net_and_layer(self):
        sharp = [seg((0, 0), (5, 0)), seg((5, 0), (0, 5))]       # 45 degrees at (5, 0)
        self.assertEqual(Q.metrics_of(sharp, 0)["sharp_corners"], 1)
        other_net = [seg((0, 0), (5, 0)), seg((5, 0), (0, 5), net="M")]
        self.assertEqual(Q.metrics_of(other_net, 0)["sharp_corners"], 0)
        other_layer = [seg((0, 0), (5, 0)), seg((5, 0), (0, 5), layer=1)]
        self.assertEqual(Q.metrics_of(other_layer, 0)["sharp_corners"], 0)

    def test_right_angle_corner_is_not_sharp(self):
        self.assertEqual(Q.metrics_of([seg((0, 0), (5, 0)), seg((5, 0), (5, 5))], 0)["sharp_corners"], 0)

    def test_rank_key_orders_looks_before_vias_before_length(self):
        tidy = {"vias": 90, "track_mm": 900, "off45_mm": 0, "off45_segments": 0, "sharp_corners": 0}
        wobbly = {"vias": 10, "track_mm": 100, "off45_mm": 5, "off45_segments": 3, "sharp_corners": 0}
        fewer_vias = dict(tidy, vias=80)
        self.assertLess(Q.rank_key(tidy), Q.rank_key(wobbly))
        self.assertLess(Q.rank_key(fewer_vias), Q.rank_key(tidy))


class Placement(unittest.TestCase):
    def test_even_ring_has_no_spread(self):
        import math
        ring = [(10 * math.cos(math.radians(22.5 * i)), 10 * math.sin(math.radians(22.5 * i))) for i in range(16)]
        self.assertEqual(Q.ring_unevenness(ring), 0.0)
        ring[3] = (ring[3][0] * 0.9, ring[3][1] * 0.9)
        ring[4] = (ring[4][0], ring[4][1] + 2)
        self.assertGreater(Q.ring_unevenness(ring), 0.0)

    def test_aligned_share(self):
        self.assertEqual(Q.aligned_share([(0, 0), (5, 0), (9, 3)]), 0.667)
        self.assertEqual(Q.aligned_share([(0, 0), (1, 1)]), 0.0)
        self.assertEqual(Q.aligned_share([]), 0.0)

    def test_orthogonal_share(self):
        self.assertEqual(Q.orthogonal_share([0, 90, -90, 180, 45]), 0.8)
        self.assertEqual(Q.orthogonal_share([]), 0.0)

    def test_partner_distance_skips_ground_and_itself(self):
        passives = {"C1": (0.0, 0.0, ["GND", "V"])}
        pads = {"GND": [("U1", 1.0, 0.0)], "V": [("C1", 0.0, 0.0), ("U1", 3.0, 4.0)]}
        self.assertEqual(Q.mean_partner_distance(passives, pads), 5.0)
        self.assertEqual(Q.mean_partner_distance({"C2": (0, 0, ["GND"])}, pads), 0.0)

    def test_block_spread_is_the_mean_member_distance_beyond_nothing(self):
        pos = {"A": (0.0, 0.0), "M": (3.0, 4.0), "N": (0.0, 2.0)}
        self.assertEqual(Q.mean_block_distance([("A", "M", 9), ("A", "N", 9)], pos), 3.5)
        self.assertEqual(Q.mean_block_distance([("A", "X", 9)], pos), 0.0)          # unplaced member is skipped

    def test_same_orientation_share_counts_the_majority_axis(self):
        rot = {"A": 0, "B": 180, "C": 90, "D": 0}
        self.assertEqual(Q.same_orientation_share([("A", "B", "C", "D")], rot), 0.75)    # 3 of 4 along one axis
        self.assertEqual(Q.same_orientation_share([("A", "B")], rot), 1.0)
        self.assertEqual(Q.same_orientation_share([], rot), 0.0)


if __name__ == "__main__":
    unittest.main()
