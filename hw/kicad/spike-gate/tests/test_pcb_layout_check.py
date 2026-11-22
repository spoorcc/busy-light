# SPDX-License-Identifier: Apache-2.0
"""Placement-rule check on a board file (pcb_layout_check.py; plan 08 sections 4.2 and 4.3; RV-016 rows 11 and 12).

A small in-memory board with known part positions: a centre-to-centre rule, a rule to the nearest pad of a net on a fixed
part ("J1:VBUS"), a miss, and a missing part."""
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

try:
    import pcbnew

    import pcb_full
    import pcb_layout_check as L
except ImportError:      # pragma: no cover
    pcbnew = None


def add_part(board, ref, pads):
    """A footprint with square 1 x 1 mm SMD pads at the given (number, x mm, y mm, net name) points."""
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetPosition(pcb_full.vec(0, 0))
    for num, x, y, net in pads:
        p = pcbnew.PAD(fp)
        p.SetNumber(num)
        p.SetShape(pcbnew.PAD_SHAPE_RECT)
        p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        ls = pcbnew.LSET()
        ls.AddLayer(pcbnew.F_Cu)
        p.SetLayerSet(ls)
        p.SetSize(pcb_full.vec(1.0, 1.0))
        p.SetPosition(pcb_full.vec(x, y))
        ni = board.FindNet(net)
        if ni is None:
            ni = pcbnew.NETINFO_ITEM(board, net)
            board.Add(ni)
        p.SetNet(ni)
        fp.Add(p)
    board.Add(fp)
    return fp


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class Measure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = pcbnew.BOARD()
        # J1: two VBUS pads at x 0 and x 20, a GND pad at x 4 (must not count for "J1:VBUS")
        add_part(b, "J1", [("A4", 0.0, 0.0, "VBUS"), ("B4", 20.0, 0.0, "VBUS"), ("A1", 4.0, 0.0, "GND")])
        add_part(b, "TVS1", [("1", 4.0, 3.0, "VBUS"), ("2", 6.0, 3.0, "GND")])         # centre (5, 3)
        add_part(b, "U7", [("1", 30.0, 0.0, "VBUS_IC"), ("2", 32.0, 0.0, "GND")])      # centre (31, 0)
        cls.board = b

    def test_centre_to_centre_rule(self):
        (row,) = L.measure(self.board, [("TVS1", "U7", 30.0)])
        self.assertAlmostEqual(row["distance_mm"], round(((31 - 5) ** 2 + 3**2) ** 0.5, 2))
        self.assertIs(row["met"], True)

    def test_partner_is_the_nearest_pad_of_the_named_net(self):
        # TVS1 centre (5, 3): VBUS pads at (0, 0) -> 5.83 mm and (20, 0) -> 15.30 mm; the GND pad at (4, 0) is 3.16 mm
        (row,) = L.measure(self.board, [("TVS1", "J1:VBUS", 6.0)])
        self.assertAlmostEqual(row["distance_mm"], 5.83)
        self.assertIs(row["met"], True)

    def test_a_miss_is_reported_not_hidden(self):
        (row,) = L.measure(self.board, [("TVS1", "J1:VBUS", 5.0)])
        self.assertIs(row["met"], False)

    def test_a_missing_part_or_net_gives_no_verdict(self):
        rows = L.measure(self.board, [("R22", "J1:VBUS", 8.0), ("TVS1", "J1:VBUS_IC", 8.0)])
        self.assertEqual([(r["distance_mm"], r["met"]) for r in rows], [(None, None), (None, None)])

    def test_the_rule_set_holds_the_adr0016_and_input_path_rules(self):
        rules = L.all_rules()
        self.assertIn(("C1", "U5", 8.0), rules)
        self.assertIn(("TVS1", "J1:VBUS", 6.0), rules)
        self.assertIn(("R22", "U7", 6.0), rules)


if __name__ == "__main__":
    unittest.main()
