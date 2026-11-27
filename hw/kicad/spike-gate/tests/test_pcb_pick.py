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


class Tidy(unittest.TestCase):
    def test_tidiness_breaks_ties_after_the_gate_but_never_overrides_it(self):
        with tempfile.TemporaryDirectory() as t:
            runs = [make(t, "r1", drc(0)), make(t, "r2", drc(0)), make(t, "r3", drc(1))]
            key = {"r1": (5, 0, 90, 900.0), "r2": (1, 0, 99, 950.0), "r3": (0, 0, 1, 1.0)}
            best, _ = K.pick(runs, gate=lambda b: 0, tidy=lambda b: key[b.parent.parent.name])
            self.assertEqual(best.name, "r2")               # r3 is tidiest but has an open item


class Power(unittest.TestCase):
    def test_power_failures_rank_after_the_gate_and_before_tidiness(self):
        with tempfile.TemporaryDirectory() as t:
            runs = [make(t, "r1", drc(0)), make(t, "r2", drc(0)), make(t, "r3", drc(1))]
            fails = {"r1": 1, "r2": 0, "r3": 0}                 # r1 is tidier, but a power net misses its target
            best, rows = K.pick(runs, gate=lambda b: 0, power=lambda b: fails[b.parent.parent.name],
                                tidy=lambda b: (0,) if b.parent.parent.name == "r1" else (9,))
            self.assertEqual(best.name, "r2")
            self.assertEqual(dict(rows)[runs[1]], (0, 0, 0, 0, 9))      # unconnected, strict, hard, power, tidy

    def test_power_fails_counts_nets_over_target_and_an_infinite_drop(self):
        out = '{"nets": {"a": {"within_50mv": true}, "b": {"within_50mv": false, "drop_mv": Infinity}}}'
        self.assertEqual(K.power_fails_from(out), 1)
        self.assertEqual(K.power_fails_from("no json"), 99)       # not measured: ranks last among equals

    def test_power_fails_counts_a_path_through_thin_track(self):
        """Batch p1b7: the drop was within target at a fine grid but the current ran through 0.15 mm track."""
        out = '{"nets": {"a": {"within_50mv": true, "full_width_path": false}, "b": {"within_50mv": true}}}'
        self.assertEqual(K.power_fails_from(out), 1)


class Layout(unittest.TestCase):
    def test_placement_rule_misses_rank_after_the_gate_and_before_power_and_tidiness(self):
        """RV-019 G6: the picker ignored the placement rules."""
        with tempfile.TemporaryDirectory() as t:
            runs = [make(t, "r1", drc(0)), make(t, "r2", drc(0)), make(t, "r3", drc(1))]
            miss = {"r1": 2, "r2": 0, "r3": 0}                  # r1 is tidier and has no power failure, but misses two rules
            best, rows = K.pick(runs, gate=lambda b: 0, layout=lambda b: miss[b.parent.parent.name], power=lambda b: 0,
                                tidy=lambda b: (0,) if b.parent.parent.name == "r1" else (9,))
            self.assertEqual(best.name, "r2")                   # r3 meets the rules but has an open item
            self.assertEqual(dict(rows)[runs[1]], (0, 0, 0, 0, 0, 9))   # unconnected, strict, hard, rule misses, power, tidy

    def test_layout_misses_counts_missed_and_unmeasurable_rules_and_is_99_when_unreadable(self):
        self.assertEqual(K.layout_misses(Path("/nonexistent/board.kicad_pcb")), 99)


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
            Path(runs[1], "a", "CUSTOM.pretty").mkdir()
            Path(runs[1], "a", "CUSTOM.pretty", "x.kicad_mod").write_text("x")
            Path(runs[1], "a", "fp-lib-table").write_text("x")
            K.main(["x", t] + [str(r) for r in runs])
            self.assertTrue(Path(t, "best", "CUSTOM.pretty", "x.kicad_mod").exists())
            self.assertTrue(Path(t, "best", "fp-lib-table").exists())

    def test_nominal_width_path_failure_counts_as_a_power_failure(self):
        out = json.dumps({"nets": {"VBUS": {"within_50mv": True, "full_width_path": True, "nominal_width_path": False},
                                   "+5V": {"within_50mv": True, "full_width_path": True}}})
        self.assertEqual(K.power_fails_from(out), 1)      # RV-019 pass 3, S5: the 0.6 mm criterion of plan 08 R4 (e)

    def test_chosen_path_is_the_run_folder_so_two_batches_do_not_clash(self):
        with tempfile.TemporaryDirectory() as t:
            c1, c2 = Path(t, "c1"), Path(t, "c2")
            c1.mkdir()
            c2.mkdir()
            runs = [make(str(c1), "run1", drc(3)), make(str(c2), "run1", drc(0))]
            K.main(["x", t] + [str(r) for r in runs])
            self.assertEqual(Path(t, "best", "chosen_path.txt").read_text().strip(), str(runs[1]))

    def test_main_fails_when_every_run_has_open_items(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(K.main(["x", t, str(make(t, "r1", drc(1)))]), 1)


if __name__ == "__main__":
    unittest.main()
