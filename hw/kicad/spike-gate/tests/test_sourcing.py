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

    def test_every_reference_has_an_mpn_and_the_missing_check_reports_an_empty_one(self):
        # J1 (GCT USB4085-GF-A) and TVS1, TVS2 (PESD parts) are listed since 2026-11-09
        for ref, mpn in (("J1", "USB4085-GF-A"), ("TVS1", "PESD5V0S1BA,115"), ("TVS2", "PESD3V3L1BA,115")):
            self.assertEqual(self.fields(ref)["MPN"].value, mpn, ref)
        row = {"MPN": "", "Manufacturer": "", "LCSC": ""}
        self.assertEqual(pcb_fabreview.missing_mpn([("X1", row)]), ["X1"])

    def test_bias_analysed_capacitors_carry_fields(self):
        # HW-014/015: C2, C3, C5, C6 follow hw/sim/scripts/dc_bias_caps.py
        for ref, mpn in (("C2", "CL10A475KO8NNNC"), ("C3", "CL21A106KAYNNNE"),
                         ("C5", "CL10A225KO8NNNC"), ("C6", "CL10A106KP8NNNC")):
            self.assertEqual(self.fields(ref)["MPN"].value, mpn, ref)

    def test_passive_carries_fields(self):
        self.assertEqual(self.fields("R1")["MPN"].value, "0603WAF1003T5E")
        self.assertEqual(self.fields("R_ILIM1")["MPN"].value, "TD03G4702BT")
        self.assertEqual(self.fields("U9")["MPN"].value, "ESP32-C3-MINI-1-N4")

    def test_power_symbols_have_no_fields(self):
        for s in self.sch.schematicSymbols:
            if s.libraryNickname == "power":
                self.assertNotIn("MPN", {p.key for p in s.properties})


if __name__ == "__main__":
    unittest.main()
