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
                flat = {k: v for k, v in types.items() if k != "strict_allow"}
                flat.update({"strict_allow/" + k: v for k, v in types.get("strict_allow", {}).items()})
                for typ, entry in flat.items():
                    self.assertIsInstance(entry["max"], int, f"{kind}/{profile}/{typ}")
                    self.assertTrue(entry["reason"], f"{kind}/{profile}/{typ}")


def parity_item(typ, ref, text=None):
    return {"severity": "warning", "type": typ, "description": "x",
            "items": [{"description": text or "Footprint " + ref}]}


class RefAllowList(unittest.TestCase):
    """Plan 06 T14: a class with a `refs` list tolerates only items whose refs are all listed."""

    ALLOW = {"footprint_symbol_mismatch": {"max": 9, "reason": "x", "refs": ["U1", "D1", "TP*", "H*"]},
             "net_conflict": {"max": 9, "reason": "x", "refs": ["U1", "TP*"]}}

    def report(self, *items):
        r = drc_report()
        r["schematic_parity"] = list(items)
        return r

    def test_listed_refs_pass(self):
        r = self.report(parity_item("footprint_symbol_mismatch", "U1"), parity_item("footprint_symbol_mismatch", "TP12"),
                        parity_item("footprint_symbol_mismatch", "H3"))
        self.assertEqual(K.foreign_refs(r, "drc", self.ALLOW), {})

    def test_foreign_ref_fails(self):
        r = self.report(parity_item("footprint_symbol_mismatch", "R7"))
        self.assertEqual(K.foreign_refs(r, "drc", self.ALLOW), {"footprint_symbol_mismatch": {"R7"}})

    def test_net_conflict_on_another_ref_fails(self):
        r = drc_report()
        r["violations"] = [parity_item("net_conflict", "", "Pad 1 [/CC1] of U2 on F.Cu")]
        self.assertEqual(K.foreign_refs(r, "drc", self.ALLOW), {"net_conflict": {"U2"}})

    def test_item_with_several_refs_needs_all_listed(self):
        v = parity_item("net_conflict", "", "Pad 1 [/CC1] of U1 on F.Cu")
        v["items"].append({"description": "Pad 2 [GND] of U2 on F.Cu"})
        r = drc_report()
        r["violations"] = [v]
        self.assertEqual(K.foreign_refs(r, "drc", self.ALLOW), {"net_conflict": {"U2"}})

    def test_class_without_refs_key_is_number_only(self):
        r = self.report(parity_item("lib_footprint_issues", "ZZ9"))
        self.assertEqual(K.foreign_refs(r, "drc", {"lib_footprint_issues": {"max": 1, "reason": "x"}}), {})

    def test_refs_any_needs_one_listed_ref(self):
        allow = {"courtyards_overlap": {"max": 9, "reason": "x", "refs_any": ["U9"]}}
        ok = self.report(parity_item("courtyards_overlap", "D8"))
        ok["schematic_parity"][0]["items"].append({"description": "Footprint U9"})
        self.assertEqual(K.foreign_refs(ok, "drc", allow), {})
        bad = self.report(parity_item("courtyards_overlap", "D8"))
        bad["schematic_parity"][0]["items"].append({"description": "Footprint D9"})
        self.assertEqual(K.foreign_refs(bad, "drc", allow), {"courtyards_overlap": {"D8", "D9"}})

    def test_pattern_matches_only_with_star_suffix(self):
        self.assertTrue(K.ref_ok("TP7", ["TP*"]))
        self.assertFalse(K.ref_ok("TPX", ["TP"]))
        self.assertFalse(K.ref_ok("D17", ["D1"]))

    def test_strict_mode_reads_only_strict_allow(self):
        entry = {"x": {"max": 5, "reason": "r"}, "strict_allow": {"y": {"max": 5, "reason": "r"}}}
        self.assertEqual(K.allowed_for(entry, True), {"y": {"max": 5, "reason": "r"}})
        self.assertEqual(K.allowed_for({"x": {"max": 1, "reason": "r"}}, True), {})
        self.assertIn("x", K.allowed_for(entry, False))

    def test_standin_allow_list_in_file(self):
        import json

        data = json.loads(K.ALLOW_FILE.read_text())
        want = ["U1", "U8", "U9", "C1", "C1B", "C3", "C4"] + ["D%d" % i for i in range(1, 17)] + ["TP*", "H*"]
        for prof in ("placed-4l", "routed-4l"):
            e = data["drc"][prof]["footprint_symbol_mismatch"]
            self.assertEqual(sorted(e["refs"]), sorted(want))
            self.assertRegex(e["dev"], r"^DEV-\d{3}$")


if __name__ == "__main__":
    unittest.main()
