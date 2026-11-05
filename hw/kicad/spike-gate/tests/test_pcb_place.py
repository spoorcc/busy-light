# SPDX-License-Identifier: Apache-2.0
"""Placement cost tests (pure Python): plan 06 T13."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pcb_place as P  # noqa: E402


def make_placer():
    parts = {"X": {"w": 2.0, "h": 2.0, "pads": {"1": (0.0, 0.0)}, "sides": "F"}}
    nets = {"N": [("X", "1"), ("F", "1")]}
    return P.Placer(parts, nets, {("F", "1"): (30.0, 0.0)}, [("F", 20.0, -10.0, 29.5, 10.0)], lambda *a: True)


class OverlapPenaltyFloor(unittest.TestCase):
    def cost(self, pl, x, pen):
        st = (x, 0.0, 0, "F")
        pl.state["X"] = st
        return pl.cost_of("X", st, pen)

    def test_clean_longer_placement_beats_small_overlap_at_old_pen0(self):
        pl = make_placer()
        overlapping = self.cost(pl, 19.0, 2.0)  # small overlap, short wire
        clean = self.cost(pl, 15.0, 2.0)  # no overlap, longer wire
        self.assertGreater(pl.part_overlap("X", (19.0, 0.0, 0, "F")), 0.0)
        self.assertEqual(pl.part_overlap("X", (15.0, 0.0, 0, "F")), 0.0)
        self.assertLess(clean, overlapping)

    def test_floor_constant_value(self):
        self.assertEqual(P.OVERLAP_PEN_FLOOR, 2000.0)


if __name__ == "__main__":
    unittest.main()
