# SPDX-License-Identifier: Apache-2.0
"""Tests of the strict ERC/DRC judge: a finding fails unless it is listed with a large enough maximum."""

import collections
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import kicad_strict as K  # noqa: E402


def drc_report(**kw):
    return {
        "violations": [{"severity": s, "type": t} for (s, t), n in kw.get("v", {}).items() for _ in range(n)],
        "unconnected_items": [{"severity": "error", "type": "unconnected_items"}] * kw.get("u", 0),
        "schematic_parity": 0,
        "ignored_checks": kw.get("ignored", 0),
    }


class Judge(unittest.TestCase):
    def test_clean_report_passes_strict(self):
        c = K.tally(drc_report(), "drc")
        self.assertEqual(K.judge(c, {}, True)[0], 0)

    def test_any_finding_fails_strict(self):
        c = K.tally(drc_report(v={("warning", "silk_overlap"): 1}), "drc")
        self.assertEqual(K.judge(c, {"silk_overlap": {"max": 5, "reason": "x"}}, True)[0], 1)

    def test_unlisted_type_fails_in_allow_mode(self):
        c = K.tally(drc_report(v={("error", "clearance"): 1}), "drc")
        bad, lines = K.judge(c, {"silk_overlap": {"max": 5, "reason": "x"}}, False)
        self.assertEqual(bad, 1)
        self.assertIn("not in allow-list", lines[0])

    def test_count_above_maximum_fails(self):
        c = K.tally(drc_report(v={("warning", "silk_overlap"): 6}), "drc")
        self.assertEqual(K.judge(c, {"silk_overlap": {"max": 5, "reason": "x"}}, False)[0], 1)

    def test_count_within_maximum_is_tolerated_and_printed(self):
        c = K.tally(drc_report(v={("warning", "silk_overlap"): 5}), "drc")
        bad, lines = K.judge(c, {"silk_overlap": {"max": 5, "reason": "spike"}}, False)
        self.assertEqual(bad, 0)
        self.assertIn("tolerated", lines[0])

    def test_unconnected_items_and_ignored_checks_count(self):
        c = K.tally(drc_report(u=3, ignored=5), "drc")
        self.assertEqual(c[("error", "unconnected_items")], 3)
        self.assertEqual(c[("ignored", "ignored_checks")], 5)

    def test_erc_ignored_checks_is_a_list(self):
        rep = {"sheets": [{"violations": [{"severity": "warning", "type": "lib_symbol_issues"}]}], "ignored_checks": [1, 2]}
        c = K.tally(rep, "erc")
        self.assertEqual(c, collections.Counter({("warning", "lib_symbol_issues"): 1, ("ignored", "ignored_checks"): 2}))

    def test_allow_list_entries_have_reason_and_max(self):
        import json

        data = json.loads(K.ALLOW_FILE.read_text())
        for kind in ("erc", "drc"):
            for profile, types in data[kind].items():
                for typ, entry in types.items():
                    self.assertIsInstance(entry["max"], int, f"{kind}/{profile}/{typ}")
                    self.assertTrue(entry["reason"], f"{kind}/{profile}/{typ}")


if __name__ == "__main__":
    unittest.main()
