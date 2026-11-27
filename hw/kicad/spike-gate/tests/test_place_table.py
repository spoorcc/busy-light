# SPDX-License-Identifier: Apache-2.0
"""place_table.py: the table of placement-only runs (plan 08 R2a; RV-019 pass 3, S4)."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import place_table as T  # noqa: E402


def write(root, name, misses, seed=1, overlap=0.0):
    d = Path(root) / name
    d.mkdir()
    info = {"seed": seed, "overlap_mm2": overlap, "layout_rule_misses": misses, "hpwl_mm": 1000.0}
    (d / "busy_light_spike.placement.json").write_text(json.dumps(info), encoding="utf-8")
    return str(d)


class Table(unittest.TestCase):
    def test_counts_misses_and_names_the_worst_rules(self):
        with tempfile.TemporaryDirectory() as t:
            run = write(t, "p1", [["TVS1", "fixed", 6.0, 17.9], ["R22", "U7", 6.0, 9.5]], seed=12)
            lines, clean = T.table([run])
        self.assertFalse(clean)
        self.assertIn("seed 12", lines[0])
        self.assertIn("2 misses", lines[0])
        self.assertIn("TVS1 17.9/6.0", lines[0])

    def test_clean_when_one_run_has_no_miss_and_no_overlap(self):
        with tempfile.TemporaryDirectory() as t:
            a = write(t, "a", [["TVS1", "fixed", 6.0, 17.9]])
            b = write(t, "b", [])
            self.assertTrue(T.table([a, b])[1])

    def test_an_overlap_is_never_clean(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertFalse(T.table([write(t, "a", [], overlap=0.4)])[1])

    def test_main_exit_code(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(T.main(["x", write(t, "a", [])]), 0)
            self.assertEqual(T.main(["x", write(t, "b", [["A", "B", 1.0, 2.0]])]), 1)
            self.assertEqual(T.main(["x"]), 2)
