# SPDX-License-Identifier: Apache-2.0
"""Fabricator-minimum check (pcb_fabcheck.py): the pure gap arithmetic and the direct checks on a small in-memory board."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import pcb_fabcheck as F  # noqa: E402

try:
    import pcbnew
    import pcb_full
except ImportError:
    pcbnew = None


class Gaps(unittest.TestCase):
    def test_edge_to_edge_gap_of_two_holes(self):
        # centres 1.0 mm apart, diameters 0.2 and 0.4: gap 1.0 - 0.1 - 0.2 = 0.7
        self.assertAlmostEqual(F.hole_gap((0, 0, 0.2), (1.0, 0, 0.4)), 0.7)

    def test_slot_is_a_capsule_not_a_circle_of_its_long_side(self):
        # a 2.0 mm long, 0.4 mm wide slot along x from x=-1 to x=1 and a 0.4 mm hole 0.8 mm above its middle:
        # centre distance to the slot axis 0.8, minus half widths 0.2 + 0.2 = 0.4
        slot = (-1.0, 0.0, 1.0, 0.0, 0.4)
        hole = (0.0, 0.8, 0.0, 0.8, 0.4)
        self.assertAlmostEqual(F.hole_gap(slot, hole), 0.4)
        # a hole in line with the slot end: 0.5 mm beyond it, so 0.5 - 0.2 - 0.2 = 0.1
        self.assertAlmostEqual(F.hole_gap(slot, (1.5, 0.0, 1.5, 0.0, 0.4)), 0.1)
        self.assertAlmostEqual(F.hole_gap(slot, (0.0, 0.0, 0.0, 0.0, 0.4)), -0.4)     # inside: overlapping

    def test_pairs_below_the_limit_are_found_once(self):
        holes = [(0, 0, 0.2), (0.5, 0, 0.2), (5, 5, 0.2)]
        bad = F.holes_too_close(holes, 0.4)
        self.assertEqual(len(bad), 1)
        self.assertAlmostEqual(bad[0][2], 0.3)

    def test_nothing_close_gives_an_empty_list(self):
        self.assertEqual(F.holes_too_close([(0, 0, 0.2), (3, 0, 0.2)], 0.2), [])

    def test_dru_text_names_the_pad_rule_and_the_value(self):
        t = F.pad_rule_dru(0.15)
        self.assertIn('(rule "fab_pad_to_pad"', t)
        self.assertIn("(min 0.15mm)", t)
        self.assertIn("A.Type == 'Pad' && B.Type == 'Pad'", t)

    def test_verdict_is_fail_when_any_check_fails(self):
        self.assertEqual(F.verdict({"a": {"ok": True}, "b": {"ok": True}}), "PASS")
        self.assertEqual(F.verdict({"a": {"ok": True}, "b": {"ok": False}}), "FAIL")


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class Direct(unittest.TestCase):
    def board(self, width=0.1, dia=0.5, drill=0.2):
        b = pcbnew.BOARD()
        net = pcbnew.NETINFO_ITEM(b, "N")
        b.Add(net)
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcb_full.vec(10, 10))
        v.SetDrill(pcb_full.mm(drill))
        v.SetWidth(pcb_full.mm(dia))
        v.SetNet(net)
        b.Add(v)
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(pcb_full.vec(0, 0))
        t.SetEnd(pcb_full.vec(5, 0))
        t.SetLayer(pcbnew.F_Cu)
        t.SetWidth(pcb_full.mm(width))
        t.SetNet(net)
        b.Add(t)
        return b

    def test_fine_rules_pass_and_report_the_ring_below_the_recommendation(self):
        r = F.direct_checks(self.board())
        self.assertTrue(all(c["ok"] for c in r["checks"].values()), r)
        self.assertAlmostEqual(r["min_annular_mm"], 0.15, places=3)
        self.assertEqual(r["vias_below_recommended_ring"], 1)

    def test_a_thin_track_and_a_small_via_fail(self):
        r = F.direct_checks(self.board(width=0.08, dia=0.3, drill=0.2))
        self.assertFalse(r["checks"]["track_width"]["ok"])
        self.assertFalse(r["checks"]["annular_ring"]["ok"])


if __name__ == "__main__":
    unittest.main()
