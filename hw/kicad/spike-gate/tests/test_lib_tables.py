# SPDX-License-Identifier: Apache-2.0
"""Library tables of the generated spike projects (plan 06 A-9, A-11).

Cause of the ERC and DRC findings "current configuration does not include the (symbol|footprint) library X":
kicad-cli loads a project library table only when a project file (<stem>.kicad_pro) sits next to the schematic, and
the generated directory had neither a project file for the schematic nor library tables. These tests check that the
generators write the project, both tables and the custom libraries, and that kicad-cli then reports no library finding.

Run: cd hw/kicad/spike-gate && GATE_NET=tests/data/gate.net <venv python> -m unittest tests.test_lib_tables
The PCB tests need pcbnew (system python3) and are skipped visibly without it.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
import lib_tables  # noqa: E402
import layout_full  # noqa: E402
import layout_sch  # noqa: E402

try:
    import pcbnew  # noqa: E402,F401
    import pcb_full  # noqa: E402
except ImportError:
    pcbnew = None

SYM_DIR = Path("/usr/share/kicad/symbols")
FP_DIR = Path("/usr/share/kicad/footprints")
HAVE_KICAD = shutil.which("kicad-cli") is not None and SYM_DIR.is_dir() and FP_DIR.is_dir()
LIB_CLASSES = ("lib_symbol_issues", "footprint_link_issues", "lib_footprint_issues", "lib_footprint_mismatch")


def table_entries(path: Path) -> dict:
    return {m.group(1): m.group(2) for m in re.finditer(r'\(name "([^"]+)"\)\s*\(type "[^"]+"\)\s*\(uri "([^"]+)"\)',
                                                        path.read_text(encoding="utf-8"))}


def resolve(uri: str, proj: Path) -> Path:
    return Path(uri.replace("${KIPRJMOD}", str(proj)).replace("${KICAD10_SYMBOL_DIR}", str(SYM_DIR))
                .replace("${KICAD10_FOOTPRINT_DIR}", str(FP_DIR)))


def erc_counts(sch: Path) -> dict:
    out = sch.parent / "erc.json"
    subprocess.run(["kicad-cli", "sch", "erc", "--format", "json", "--severity-all", "-o", str(out), str(sch)],
                   capture_output=True, check=False)
    counts: dict = {}
    for s in json.loads(out.read_text())["sheets"]:
        for v in s["violations"]:
            counts[v["type"]] = counts.get(v["type"], 0) + 1
    return counts


class Names(unittest.TestCase):
    def test_nicknames_are_read_from_the_schematic_text(self):
        text = '(lib_id "Device:R") (lib_id "power:GND") (property "Footprint" "Resistor_SMD:R_0603" (at 0 0 0))' \
               '(property "Footprint" "" (at 0 0 0))'
        self.assertEqual(lib_tables.nicknames(text), ({"Device", "power"}, {"Resistor_SMD"}))

    def test_table_text_lists_every_nickname_once_and_sorted(self):
        t = lib_tables.sym_lib_table({"b", "a"}, {"b"})
        self.assertLess(t.index('"a"'), t.index('"b"'))
        self.assertIn("${KICAD10_SYMBOL_DIR}/a.kicad_sym", t)
        self.assertIn("${KIPRJMOD}/b.kicad_sym", t)
        f = lib_tables.fp_lib_table({"X"}, {"X"})
        self.assertIn("${KIPRJMOD}/X.pretty", f)


class Full(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.sch = cls.dir / "full.kicad_sch"
        layout_full.write(str(cls.sch))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_project_and_tables_are_written(self):
        for n in ("full.kicad_pro", "sym-lib-table", "fp-lib-table", "busylight_gate.kicad_sym"):
            self.assertTrue((self.dir / n).is_file(), n)

    def test_every_used_nickname_resolves(self):
        sym, fp = lib_tables.nicknames(self.sch.read_text(encoding="utf-8"))
        st, ft = table_entries(self.dir / "sym-lib-table"), table_entries(self.dir / "fp-lib-table")
        self.assertEqual(sym - set(st), set())
        self.assertEqual(fp - set(ft), set())
        self.assertEqual(set(st) - sym, set())      # no unused entry
        self.assertEqual(set(ft) - fp, set())
        for n in sym:
            if HAVE_KICAD or n == "busylight_gate":
                self.assertTrue(resolve(st[n], self.dir).is_file(), n)

    @unittest.skipUnless(HAVE_KICAD, "kicad-cli or the KiCad libraries are not available")
    def test_every_footprint_field_names_an_existing_footprint(self):
        text = self.sch.read_text(encoding="utf-8")
        ft = table_entries(self.dir / "fp-lib-table")
        for nick, name in sorted(set(re.findall(r'\(property "Footprint" "([^":]+):([^"]+)"', text))):
            self.assertTrue((resolve(ft[nick], self.dir) / (name + ".kicad_mod")).is_file(), f"{nick}:{name}")

    @unittest.skipUnless(HAVE_KICAD, "kicad-cli is not available")
    def test_erc_reports_no_library_finding(self):
        counts = erc_counts(self.sch)
        for k in LIB_CLASSES:
            self.assertEqual(counts.get(k, 0), 0, f"{k}: {counts}")

    def test_two_writes_are_identical(self):
        other = tempfile.TemporaryDirectory()
        try:
            layout_full.write(str(Path(other.name) / "full.kicad_sch"))
            for n in ("full.kicad_pro", "sym-lib-table", "fp-lib-table", "busylight_gate.kicad_sym"):
                self.assertEqual((self.dir / n).read_bytes(), (Path(other.name) / n).read_bytes(), n)
        finally:
            other.cleanup()

    def test_custom_symbols_are_all_in_the_custom_library(self):
        lib = (self.dir / "busylight_gate.kicad_sym").read_text(encoding="utf-8")
        for part in ("TMUX1101", "SUPERVISOR", "CC_IC_TUSB321", "TPS2553_BOX"):
            self.assertIn(f'(symbol "{part}"', lib)
        self.assertNotIn('"busylight_gate:', lib)


class Gate(unittest.TestCase):
    @unittest.skipUnless(HAVE_KICAD, "kicad-cli is not available")
    def test_gate_layout_erc_reports_no_library_finding(self):
        with tempfile.TemporaryDirectory() as t:
            sch = Path(t) / "gate.kicad_sch"
            layout_sch.write(str(HERE / "data" / "gate.net"), str(sch))
            self.assertTrue((Path(t) / "sym-lib-table").is_file())
            counts = erc_counts(sch)
            for k in LIB_CLASSES:
                self.assertEqual(counts.get(k, 0), 0, f"{k}: {counts}")


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class Pcb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name) / "a"
        cls.pcb = Path(pcb_full.build(str(HERE / "data" / "full.net"), str(cls.dir), layers=4))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_footprint_table_covers_every_placed_footprint(self):
        used = set(re.findall(r'\(footprint "([^":]+):', self.pcb.read_text(encoding="utf-8")))
        ft = table_entries(self.dir / "fp-lib-table")
        self.assertEqual(used - set(ft), set())
        self.assertTrue((self.dir / "CUSTOM.pretty" / "X2QFN-12_RWB.kicad_mod").is_file())

    @unittest.skipUnless(HAVE_KICAD, "kicad-cli is not available")
    def test_drc_reports_no_library_finding(self):
        out = self.dir / "drc.json"
        subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all", "-o", str(out), str(self.pcb)],
                       capture_output=True, check=False)
        found = [v["type"] for v in json.loads(out.read_text())["violations"] if v["type"] in LIB_CLASSES]
        self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
