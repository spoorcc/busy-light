# SPDX-License-Identifier: Apache-2.0
"""Tests of the BOM sourcing fields (HW-008): table and schematic properties (needs kiutils)."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
import pcb_fabreview  # noqa: E402
import sourcing  # noqa: E402
from kiutils.schematic import Schematic  # noqa: E402


class SourcingTableTest(unittest.TestCase):
    def test_every_entry_has_mpn_and_evidence(self):
        for value, e in sourcing.SOURCING.items():
            self.assertTrue(e.get("MPN"), value)
            self.assertTrue(e.get("Evidence"), value)

    def test_lcsc_numbers_have_the_shop_format(self):
        for value, e in sourcing.SOURCING.items():
            if e.get("LCSC"):
                self.assertRegex(e["LCSC"], r"^C\d{3,9}$", value)

    def test_unknown_part_gets_empty_fields(self):
        empty = {"MPN": "", "Manufacturer": "", "LCSC": ""}
        self.assertEqual(sourcing.sourcing_fields("no such part"), empty)


class SchematicFieldsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # fresh process: a second layout_full.build() in one process draws extra symbols
        # (existing defect, not fixed here)
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "full.kicad_sch")
            script = str(HERE.parent / "src" / "layout_full.py")
            subprocess.run([sys.executable, script, out], check=True)
            cls.sch = Schematic.from_file(out)

    def fields(self, ref):
        for s in self.sch.schematicSymbols:
            if any(p.key == "Reference" and p.value == ref for p in s.properties):
                return {p.key: p for p in s.properties}
        self.fail("no symbol " + ref)

    def test_listed_part_carries_fields(self):
        f = self.fields("U14")
        self.assertEqual(f["MPN"].value, "TMUX1101DCKR")
        self.assertEqual(f["LCSC"].value, "C2673506")
        self.assertTrue(f["MPN"].effects.hide)

    def test_unlisted_part_has_empty_mpn_and_is_reported(self):
        f = self.fields("R1")
        self.assertEqual(f["MPN"].value, "")
        row = {k: v.value for k, v in f.items()}
        self.assertEqual(pcb_fabreview.missing_mpn([("R1", row)]), ["R1"])

    def test_power_symbols_have_no_fields(self):
        for s in self.sch.schematicSymbols:
            if s.libraryNickname == "power":
                self.assertNotIn("MPN", {p.key for p in s.properties})


if __name__ == "__main__":
    unittest.main()
