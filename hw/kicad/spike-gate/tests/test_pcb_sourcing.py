# SPDX-License-Identifier: Apache-2.0
"""pcb_sourcing.py: the schematic's sourcing fields reach the footprints of a stored board (plan 08 O2; HW-008).
2026-11-18: U6 got LCSC C15999 after board-p1 was routed; the order check failed on it until the fields were copied."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

import pcb_sourcing  # noqa: E402

try:
    import pcbnew
except ImportError:      # pragma: no cover
    pcbnew = None

BOARD_P1 = HERE.parent / "board-p1"


class Changes(unittest.TestCase):
    def test_only_differing_fields_of_refs_on_the_board(self):
        sch = {"U6": {"MPN": "USBLC6-2P6", "LCSC": "C15999"}, "X9": {"LCSC": "C1"}, "R1": {"LCSC": "C25741"}}
        board = {"U6": {"MPN": "USBLC6-2P6", "Manufacturer": "ST", "LCSC": ""}, "R1": {"LCSC": "C25741"}}
        self.assertEqual(pcb_sourcing.changes(sch, board), [("U6", "LCSC", "", "C15999")])

    def test_missing_board_field_counts_as_empty(self):
        self.assertEqual(pcb_sourcing.changes({"U5": {"MPN": "M"}}, {"U5": {}}), [("U5", "MPN", "", "M")])

    def test_no_change_when_equal(self):
        f = {"MPN": "A", "Manufacturer": "B", "LCSC": "C1"}
        self.assertEqual(pcb_sourcing.changes({"U1": dict(f)}, {"U1": dict(f)}), [])


@unittest.skipIf(pcbnew is None or not (BOARD_P1 / "busy_light_spike.kicad_pcb").exists(), "pcbnew or board-p1 missing")
class StoredBoard(unittest.TestCase):
    def test_board_p1_fields_equal_its_schematic(self):
        """The committed board-p1 carries the sourcing fields of its committed schematic (run the script after a
        sourcing change)."""
        with tempfile.TemporaryDirectory() as t:
            pcb = Path(t) / "b.kicad_pcb"
            shutil.copy(BOARD_P1 / "busy_light_spike.kicad_pcb", pcb)
            out = subprocess.run([sys.executable, str(HERE.parent / "src" / "pcb_sourcing.py"), str(pcb),
                                  str(BOARD_P1 / "busy_light_spike.kicad_sch")], capture_output=True, text=True, check=True)
            rep = json.loads([line for line in out.stdout.splitlines() if line.startswith("{")][-1])
            self.assertEqual(rep["changed"], [])

    def test_script_writes_a_changed_field(self):
        with tempfile.TemporaryDirectory() as t:
            pcb, sch = Path(t) / "b.kicad_pcb", Path(t) / "b.kicad_sch"
            shutil.copy(BOARD_P1 / "busy_light_spike.kicad_pcb", pcb)
            text = (BOARD_P1 / "busy_light_spike.kicad_sch").read_text(encoding="utf-8")
            sch.write_text(text.replace('(property "LCSC" "C15999"', '(property "LCSC" "C999999"', 1), encoding="utf-8")
            subprocess.run([sys.executable, str(HERE.parent / "src" / "pcb_sourcing.py"), str(pcb), str(sch)],
                           capture_output=True, text=True, check=True)
            b = pcbnew.LoadBoard(str(pcb))
            self.assertEqual(b.FindFootprintByReference("U6").GetField("LCSC").GetText(), "C999999")


if __name__ == "__main__":
    unittest.main()
