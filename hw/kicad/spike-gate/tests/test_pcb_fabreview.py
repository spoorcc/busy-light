# SPDX-License-Identifier: Apache-2.0
"""Tests for the assembly and documentation checks of a board (pcb_fabreview.py): pure functions, no pcbnew."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import pcb_fabreview as R  # noqa: E402


class Bom(unittest.TestCase):
    def test_unannotated_refs_end_with_a_question_mark(self):
        self.assertEqual(R.unannotated(["C1", "C1B?", "R_VD?"]), ["C1B?", "R_VD?"])

    def test_bom_and_board_differ_by_name_not_by_part_and_test_points_are_ignored(self):
        d = R.bom_vs_board(["C1", "C2?", "R1"], ["C1", "C2", "R1", "TP1"])
        self.assertEqual(d["only_bom"], ["C2?"])
        self.assertEqual(d["only_board"], ["C2"])           # TP1 is out of the BOM on purpose

    def test_open_values_are_tbd_or_empty(self):
        rows = [("C2", "1u tbd"), ("C5", "tbd"), ("R1", "10k"), ("U1", "")]
        self.assertEqual(R.open_values(rows), ["C2", "C5", "U1"])

    def test_missing_part_numbers(self):
        self.assertEqual(R.missing_mpn([("R1", {"MPN": "x"}), ("R2", {}), ("R3", {"MPN": ""})]), ["R2", "R3"])


class Board(unittest.TestCase):
    def test_refs_on_silkscreen_are_counted_by_layer_name(self):
        layers = ["F.Fab", "F.SilkS", "B.Fab", "B.Silkscreen"]
        self.assertEqual(R.refs_on_silk(layers), 2)

    def test_fiducials_are_footprints_with_fiducial_in_the_name(self):
        self.assertEqual(R.fiducials(["R_0603", "Fiducial_1mm_Mask2mm", "FIDUCIAL"]), 2)

    def test_verdict_lists_every_finding(self):
        v = R.verdict({"unannotated": ["C1?"], "no_fiducials": True, "refs_on_silk": 0, "open_values": []})
        self.assertEqual(v["status"], "FINDINGS")
        self.assertEqual(len(v["findings"]), 3)
        self.assertEqual(R.verdict({"unannotated": [], "no_fiducials": False, "refs_on_silk": 5, "open_values": []})["status"], "OK")


if __name__ == "__main__":
    unittest.main()
