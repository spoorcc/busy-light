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


class Grid(unittest.TestCase):
    def test_snap_rounds_to_the_grid_and_zero_is_off(self):
        self.assertAlmostEqual(P.snap(1.26, 0.5), 1.5)
        self.assertAlmostEqual(P.snap(-0.74, 0.5), -0.5)
        self.assertEqual(P.snap(1.234, 0.0), 1.234)

    def test_every_centre_of_a_run_is_on_the_grid(self):
        old = P.GRID
        P.GRID = 0.5
        try:
            parts = {r: {"w": 1.0, "h": 1.0, "pads": {"1": (0.0, 0.0)}, "sides": "F"} for r in ("A", "B", "C")}
            nets = {"N": [("A", "1"), ("B", "1"), ("C", "1")]}
            pl = P.Placer(parts, nets, {}, [], lambda *a: True, seed=3)
            pl.run(iters=2000)
            for x, y, _, _ in pl.state.values():
                self.assertAlmostEqual(x / 0.5, round(x / 0.5), places=6)
                self.assertAlmostEqual(y / 0.5, round(y / 0.5), places=6)
        finally:
            P.GRID = old


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



class Blocks(unittest.TestCase):
    """Functional blocks (layout experiment ring12): a member costs BLOCK_W per mm beyond its radius from the anchor."""

    def make(self, blocks=(), families=(), twins=()):
        parts = {r: {"w": 1.0, "h": 1.0, "pads": {"1": (0.0, 0.0)}, "sides": "F"} for r in ("A", "M", "N")}
        pl = P.Placer(parts, {}, {}, [], lambda *a: True, blocks=blocks, families=families, twins=twins)
        pl.state = {"A": (0.0, 0.0, 0, "F"), "M": (3.0, 0.0, 0, "F"), "N": (0.0, 9.0, 0, "F")}
        return pl

    def test_member_cost_is_zero_within_radius_and_grows_beyond(self):
        old = P.BLOCK_W
        P.BLOCK_W = 10.0
        try:
            pl = self.make(blocks=(("A", "M", 4.0), ("A", "N", 4.0)))
            self.assertEqual(pl.cost_of("M", pl.state["M"], 1.0), 0.0)
            self.assertAlmostEqual(pl.cost_of("N", pl.state["N"], 1.0), 10.0 * 5.0)
            self.assertAlmostEqual(pl.cost_of("A", pl.state["A"], 1.0), 10.0 * 5.0)      # the anchor feels its members too
        finally:
            P.BLOCK_W = old

    def test_off_by_default(self):
        pl = self.make(blocks=(("A", "N", 4.0),))
        self.assertEqual(pl.cost_of("N", pl.state["N"], 1.0), 0.0)


class Orientation(unittest.TestCase):
    """Like parts share one orientation (ORIENT_W per member that differs); twins must match exactly."""

    def make(self, rots, **kw):
        parts = {r: {"w": 1.0, "h": 1.0, "pads": {"1": (0.0, 0.0)}, "sides": "F"} for r in ("A", "B", "C")}
        pl = P.Placer(parts, {}, {}, [], lambda *a: True, **kw)
        pl.state = {r: (5.0 * i, 0.0, rot, "F") for i, (r, rot) in enumerate(zip("ABC", rots))}
        return pl

    def test_family_cost_counts_members_with_another_axis(self):
        old = P.ORIENT_W
        P.ORIENT_W = 2.0
        try:
            pl = self.make((0, 180, 90), families=(("A", "B", "C"),))
            self.assertEqual(pl.cost_of("B", pl.state["B"], 1.0), 2.0)       # 180 looks like 0, 90 does not
            self.assertEqual(pl.cost_of("C", pl.state["C"], 1.0), 4.0)
            same = self.make((0, 180, 0), families=(("A", "B", "C"),))
            self.assertEqual(same.cost_of("A", same.state["A"], 1.0), 0.0)
        finally:
            P.ORIENT_W = old

    def test_twins_need_the_same_rotation_and_side(self):
        old = P.ORIENT_W
        P.ORIENT_W = 2.0
        try:
            pl = self.make((0, 180, 0), twins=(("A", "B"),))
            self.assertEqual(pl.cost_of("A", pl.state["A"], 1.0), 4.0)       # twins weigh double
            pl.state["B"] = (5.0, 0.0, 0, "F")
            self.assertEqual(pl.cost_of("A", pl.state["A"], 1.0), 0.0)
            pl.state["B"] = (5.0, 0.0, 0, "B")
            self.assertGreater(pl.cost_of("A", pl.state["A"], 1.0), 0.0)
        finally:
            P.ORIENT_W = old

    def test_off_by_default(self):
        pl = self.make((0, 90, 0), families=(("A", "B", "C"),), twins=(("A", "B"),))
        self.assertEqual(pl.cost_of("B", pl.state["B"], 1.0), 0.0)



class StrictFamiliesAndRows(unittest.TestCase):
    """Ring13: ICs of one kind point the same way (pin 1 too); test points line up in a row."""

    def make(self, states, **kw):
        parts = {r: {"w": 1.0, "h": 1.0, "pads": {"1": (0.0, 0.0)}, "sides": "FB"} for r in states}
        pl = P.Placer(parts, {}, {}, [], lambda *a: True, **kw)
        pl.state = dict(states)
        return pl

    def test_strict_family_counts_a_flipped_part_that_the_axis_rule_accepts(self):
        old = P.ORIENT_W
        P.ORIENT_W = 2.0
        try:
            st = {"A": (0.0, 0.0, 0, "F"), "B": (5.0, 0.0, 180, "F"), "C": (9.0, 0.0, 0, "F")}
            soft = self.make(st, families=(("A", "B", "C"),))
            strict = self.make(st, strict_families=(("A", "B", "C"),))
            self.assertEqual(soft.cost_of("A", st["A"], 1.0), 0.0)
            self.assertEqual(strict.cost_of("A", st["A"], 1.0), 2.0)           # B points the other way
            st2 = dict(st, B=(5.0, 0.0, 0, "B"))
            self.assertEqual(self.make(st2, strict_families=(("A", "B", "C"),)).cost_of("A", st2["A"], 1.0), 2.0)   # side counts
        finally:
            P.ORIENT_W = old

    def test_row_cost_is_the_offset_from_a_common_line_and_zero_in_a_row(self):
        old = P.ROW_W
        P.ROW_W = 3.0
        try:
            st = {"A": (0.0, 0.0, 0, "B"), "B": (4.0, 0.0, 0, "B"), "C": (8.0, 1.5, 0, "B")}
            pl = self.make(st, rows=(("A", "B", "C"),))
            self.assertAlmostEqual(pl.cost_of("C", st["C"], 1.0), 3.0 * 1.5 * 2)        # off the line of A and B
            st["C"] = (8.0, 0.0, 0, "B")
            self.assertEqual(pl.cost_of("C", st["C"], 1.0), 0.0)
            st["C"] = (0.0, 6.0, 0, "B")                                                # a column is a line too
            pl.state["B"] = (0.0, 3.0, 0, "B")
            self.assertEqual(pl.cost_of("C", st["C"], 1.0), 0.0)
        finally:
            P.ROW_W = old

    def test_off_by_default(self):
        st = {"A": (0.0, 0.0, 0, "F"), "B": (5.0, 2.0, 180, "F")}
        pl = self.make(st, strict_families=(("A", "B"),), rows=(("A", "B"),))
        self.assertEqual(pl.cost_of("A", st["A"], 1.0), 0.0)


class ProximityRules(unittest.TestCase):
    """A proximity rule (ref, ref, limit) adds a cost for the distance beyond the limit (ADR-0016 rules in the cost)."""

    def make(self):
        parts = {"A": {"w": 2.0, "h": 2.0, "pads": {"1": (0.0, 0.0)}, "sides": "F"},
                 "B": {"w": 2.0, "h": 2.0, "pads": {"1": (0.0, 0.0)}, "sides": "F"}}
        return P.Placer(parts, {}, {}, [], lambda *a: True, rules=(("A", "B", 6.0),))

    def test_no_cost_within_limit_and_cost_beyond(self):
        pl = self.make()
        pl.state["B"] = (0.0, 0.0, 0, "F")
        near, far = (5.0, 0.0, 0, "F"), (10.0, 0.0, 0, "F")
        self.assertEqual(pl.cost_of("A", near, 2.0), 0.0)
        self.assertGreater(pl.cost_of("A", far, 2.0), 0.0)
        self.assertGreater(pl.cost_of("A", (20.0, 0.0, 0, "F"), 2.0), pl.cost_of("A", far, 2.0))

    def test_rule_with_unplaced_partner_costs_nothing(self):
        pl = self.make()
        self.assertEqual(pl.cost_of("A", (50.0, 0.0, 0, "F"), 2.0), 0.0)


if __name__ == "__main__":
    unittest.main()
