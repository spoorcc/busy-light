# SPDX-License-Identifier: Apache-2.0
"""Tests for the finishing geometry (pcb_finish.py): silkscreen designators and fiducial spots; no pcbnew."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import pcb_finish as F  # noqa: E402


class Rects(unittest.TestCase):
    def test_overlap_with_margin(self):
        a = (0.0, 0.0, 2.0, 1.0)                              # x0, y0, x1, y1
        self.assertTrue(F.overlap(a, (1.5, 0.5, 3.0, 2.0), 0.0))
        self.assertFalse(F.overlap(a, (2.1, 0.0, 3.0, 1.0), 0.0))
        self.assertTrue(F.overlap(a, (2.1, 0.0, 3.0, 1.0), 0.2))      # a 0.1 mm gap is inside a 0.2 mm margin

    def test_text_box_grows_with_the_number_of_characters(self):
        w1, h1 = F.text_size("C1", 1.0)
        w2, _ = F.text_size("R_ILIM1", 1.0)
        self.assertGreater(w2, w1)
        self.assertEqual(h1, 1.0)


class Texts(unittest.TestCase):
    def test_text_goes_beside_the_part_and_avoids_obstacles(self):
        part = (0.0, 0.0, 2.0, 1.0)
        pos = F.place_text("C1", part, obstacles=[], inside=lambda r: True, height=1.0)
        self.assertIsNotNone(pos)
        box = F.text_box("C1", pos, 1.0)
        self.assertFalse(F.overlap(box, part, 0.0))
        blocked = [F.text_box("C1", pos, 1.0)]
        pos2 = F.place_text("C1", part, obstacles=blocked, inside=lambda r: True, height=1.0)
        self.assertNotEqual(pos, pos2)

    def test_no_room_gives_none(self):
        self.assertIsNone(F.place_text("C1", (0, 0, 2, 1), obstacles=[], inside=lambda r: False, height=1.0))

    def test_the_nearest_free_candidate_wins(self):
        part = (0.0, 0.0, 2.0, 1.0)
        pos = F.place_text("C1", part, obstacles=[], inside=lambda r: True, height=1.0)
        d = abs(pos[0] - 1.0) + abs(pos[1] - 0.5)
        self.assertLess(d, 3.0)


class Findings(unittest.TestCase):
    def test_refs_named_in_silkscreen_findings(self):
        drc = {"violations": [
            {"type": "silk_overlap", "items": [{"description": "Segment of U9 on F.Silkscreen"}, {"description": "Reference field of C4"}]},
            {"type": "silk_edge_clearance", "items": [{"description": "Arc on Edge.Cuts"}, {"description": "Reference field of D3"}]},
            {"type": "clearance", "items": [{"description": "Reference field of R1"}]}]}
        self.assertEqual(F.refs_in_silk_findings(drc), {"C4", "D3"})

    def test_keep_out_rect_blocks_points_near_it(self):
        self.assertTrue(F.in_rects(1.0, 1.0, [(0.0, 0.0, 2.0, 2.0)], 0.0))
        self.assertTrue(F.in_rects(2.5, 1.0, [(0.0, 0.0, 2.0, 2.0)], 1.0))
        self.assertFalse(F.in_rects(5.0, 1.0, [(0.0, 0.0, 2.0, 2.0)], 1.0))


class Fiducials(unittest.TestCase):
    def test_free_spot_keeps_the_clearance_to_every_item_and_the_edge(self):
        items = [(5.0, 5.0, 1.0)]                              # x, y, radius of copper
        spot = F.free_spot(items, inside=lambda x, y: 0 <= x <= 10 and 0 <= y <= 10, clearance=2.0, step=0.5, far_from=[])
        self.assertIsNotNone(spot)
        self.assertGreaterEqual(((spot[0] - 5) ** 2 + (spot[1] - 5) ** 2) ** 0.5, 3.0)

    def test_second_spot_is_far_from_the_first(self):
        s = F.free_spot([], inside=lambda x, y: 0 <= x <= 20 and 0 <= y <= 20, clearance=1.0, step=1.0, far_from=[(1.0, 1.0)], min_far=10.0)
        self.assertGreaterEqual(((s[0] - 1) ** 2 + (s[1] - 1) ** 2) ** 0.5, 10.0)

    def test_none_when_no_space(self):
        self.assertIsNone(F.free_spot([(5, 5, 20.0)], inside=lambda x, y: 0 <= x <= 10 and 0 <= y <= 10, clearance=1.0, step=1.0, far_from=[]))


if __name__ == "__main__":
    unittest.main()
