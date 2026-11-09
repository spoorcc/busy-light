# SPDX-License-Identifier: Apache-2.0
"""Tests of the spare-capacitor tool (HW-016): free-spot search and schematic text readers (pure functions)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import pcb_spare_caps as S  # noqa: E402

SCH = """
  (symbol (lib_id "Device:C") (at 1 2 0) (uuid 11111111-1111-1111-1111-111111111111)
    (property "Reference" "C32" (at 0 0 0))
    (property "Value" "DNP spare" (at 0 0 0))
    (property "MPN" "" (at 0 0 0))
    (property "LCSC" "C123" (at 0 0 0))
  )
  (symbol (lib_id "Device:R") (at 1 2 0) (uuid 22222222-2222-2222-2222-222222222222)
    (property "Reference" "R1" (at 0 0 0))
    (property "Value" "100k" (at 0 0 0))
  )"""


class Spot(unittest.TestCase):
    def inside(self, r):
        return r[0] >= 0 and r[1] >= 0 and r[2] <= 20 and r[3] <= 20

    def test_empty_board_gives_the_target(self):
        self.assertEqual(S.find_spot((2, 1), (10, 10), [], self.inside, 0.4), (10.0, 10.0))

    def test_obstacle_moves_the_spot_by_the_margin(self):
        x, y = S.find_spot((2, 1), (10, 10), [(9, 9, 11, 11)], self.inside, 0.4)
        self.assertGreaterEqual(max(abs(x - 10) - 1 - 1, abs(y - 10) - 0.5 - 1), 0.4 - 1e-9)

    def test_spot_stays_inside_and_clear(self):
        obs = [(5, 5, 15, 15)]
        x, y = S.find_spot((2, 1), (10, 10), obs, self.inside, 0.4)
        r = (x - 1, y - 0.5, x + 1, y + 0.5)
        self.assertTrue(self.inside(r))
        self.assertFalse(S.rect_hit(r, obs[0], 0.4))

    def test_none_when_full(self):
        self.assertIsNone(S.find_spot((2, 1), (10, 10), [(-1, -1, 21, 21)], self.inside, 0.4, radius=5))

    def test_segment_boxes_follow_a_diagonal(self):
        boxes = S.segment_boxes(0, 0, 4, 4, 0.2)
        self.assertGreater(len(boxes), 8)
        self.assertTrue(all(abs(b[2] - b[0] - 0.2) < 1e-9 for b in boxes))


class SchematicText(unittest.TestCase):
    def test_uuid_and_value(self):
        self.assertEqual(S.schematic_uuid(SCH, "C32"), "11111111-1111-1111-1111-111111111111")
        self.assertEqual(S.schematic_value(SCH, "C32"), "DNP spare")
        self.assertIsNone(S.schematic_uuid(SCH, "C99"))

    def test_sourcing_fields_only_for_symbols_that_have_them(self):
        f = S.schematic_fields(SCH)
        self.assertEqual(f["C32"], {"MPN": "", "LCSC": "C123"})
        self.assertNotIn("R1", f)


if __name__ == "__main__":
    unittest.main()
