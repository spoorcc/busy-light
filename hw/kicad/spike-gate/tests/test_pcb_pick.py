# SPDX-License-Identifier: Apache-2.0
"""Tests for the best-of-N choice of routing runs."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import pcb_pick as K  # noqa: E402


def drc(unconnected=0, **kinds):
    return {"unconnected_items": [{}] * unconnected,
            "violations": [{"type": k} for k, n in kinds.items() for _ in range(n)]}


def make(tmp, name, report):
    a = Path(tmp, name, "a")
    a.mkdir(parents=True)
    (a / "final.kicad_pcb").write_text("x")
    if report is not None:
        (a / "drc_final.json").write_text(json.dumps(report))
    return a.parent


class Pick(unittest.TestCase):
    def test_score_counts_kinds(self):
        self.assertEqual(K.score(drc(2, clearance=1, courtyards_overlap=14, track_dangling=3)), (2, 1, 3))

    def test_fewest_unconnected_wins_then_hard_findings(self):
        with tempfile.TemporaryDirectory() as t:
            runs = [make(t, "r1", drc(1)), make(t, "r2", drc(0, clearance=2)), make(t, "r3", drc(0, courtyards_overlap=14)),
                    make(t, "r4", None)]
            best, rows = K.pick(runs)
            self.assertEqual(best.name, "r3")
            self.assertIsNone(dict(rows)[runs[3]])

    def test_main_copies_winner_and_reports_success(self):
        with tempfile.TemporaryDirectory() as t:
            runs = [make(t, "r1", drc(3)), make(t, "r2", drc(0))]
            self.assertEqual(K.main(["x", t] + [str(r) for r in runs]), 0)
            self.assertEqual(Path(t, "best", "chosen_run.txt").read_text().strip(), "r2")
            self.assertTrue(Path(t, "best", "final.kicad_pcb").exists())

    def test_main_fails_when_every_run_has_open_items(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(K.main(["x", t, str(make(t, "r1", drc(1)))]), 1)


if __name__ == "__main__":
    unittest.main()
