# SPDX-License-Identifier: Apache-2.0
"""Tests for the reference rename of a stored board (pcb_rename.py): the name logic only, no pcbnew."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import pcb_rename as N  # noqa: E402


class Rename(unittest.TestCase):
    def test_whole_token_only(self):
        self.assertEqual(N.rename("C1B", N.MAP), "C27")
        self.assertEqual(N.rename("C1", N.MAP), "C1")
        self.assertEqual(N.rename("C1BX", N.MAP), "C1BX")

    def test_net_names_with_a_reference_inside(self):
        self.assertEqual(N.rename("Net-(R_VD-Pad1)", N.MAP), "Net-(R21-Pad1)")
        self.assertEqual(N.rename("Net-(C1F-Pad1)", N.MAP), "Net-(C31-Pad1)")
        self.assertEqual(N.rename("/CC1", N.MAP), "/CC1")

    def test_auto_net_name_that_changes_with_the_pad_order(self):
        self.assertEqual(N.NETS["Net-(R_ILIM3-Pad1)"], "Net-(R20-Pad2)")       # KiCad names the net after its first pad

    def test_new_names_end_in_a_number_so_kicad_sees_them_as_annotated(self):
        for new in N.MAP.values():
            self.assertTrue(new[-1].isdigit(), new)

    def test_map_has_no_collision(self):
        self.assertEqual(len(set(N.MAP.values())), len(N.MAP))
        self.assertFalse(set(N.MAP) & set(N.MAP.values()))


if __name__ == "__main__":
    unittest.main()
