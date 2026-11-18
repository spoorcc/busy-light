# SPDX-License-Identifier: Apache-2.0
"""Requirement checks on the stored P1 board `board-p1/` (plan 08 section 5; HW-008, HW-016, HW-017; TC-216, TC-217 board part).

These read the committed board file. The gate (strict DRC and ERC), the fab check and the power check run in
`scripts/ci_hw.sh` and `scripts/fab_p1.sh`; this file holds the checks that no tool makes: sides, the spare footprints at the
TPS2553 output, the damping link nets and the panel tab clearance. Skipped without pcbnew or without the board."""
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BOARD = HERE.parent / "board-p1" / "busy_light_spike.kicad_pcb"
sys.path.insert(0, str(HERE.parent / "src"))

try:
    import pcbnew
except ImportError:      # pragma: no cover
    pcbnew = None


@unittest.skipIf(pcbnew is None or not BOARD.exists(), "pcbnew or board-p1 missing")
class BoardP1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.board = pcbnew.LoadBoard(str(BOARD))
        cls.fps = {f.GetReference(): f for f in cls.board.GetFootprints()}
        cls.info = json.loads(BOARD.with_suffix(".placement.json").read_text(encoding="utf-8"))

    def pad(self, ref, num):
        p = [q for q in self.fps[ref].Pads() if q.GetNumber() == num][0]
        return pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)

    def test_built_with_the_p1_switch(self):
        self.assertIs(self.info["p1"], True)
        self.assertEqual(self.info["overlap_mm2"], 0.0)

    def test_every_assembled_part_is_on_top(self):
        """HW-008 (owner answer 6): one-sided assembly. On the bottom: test points, the not-fitted spares, fiducials."""
        bottom_ok = ("TP", "FID")
        bad = [r for r, f in self.fps.items() if f.IsFlipped() and not r.startswith(bottom_ok) and not f.IsDNP()]
        self.assertEqual(bad, [])
        self.assertTrue(all(not f.IsFlipped() for r, f in self.fps.items() if not f.IsDNP() and not r.startswith(bottom_ok)))

    def test_hw016_spares_at_the_tps2553_output(self):
        """HW-016 acceptance: two 1206 footprints on +5V and GND, do-not-populate and out of the BOM, every pad centre within
        [10] mm of U7 pin 6. Batch p1b3 (the first board-p1) failed this with C4 at 24.8 mm."""
        pin6 = self.pad("U7", "6")
        for ref in ("C4", "C32"):
            f = self.fps[ref]
            self.assertEqual(str(f.GetFPID().GetLibItemName()), "C_1206_3216Metric", ref)
            self.assertEqual({p.GetNumber(): p.GetNetname() for p in f.Pads()}, {"1": "+5V", "2": "GND"}, ref)
            self.assertTrue(f.IsDNP() and f.IsExcludedFromBOM(), ref)
            for num in ("1", "2"):
                self.assertLessEqual(math.dist(self.pad(ref, num), pin6), 10.0, (ref, num))

    def test_hw017_link_between_vbus_and_vbus_ic(self):
        f = self.fps["R22"]
        self.assertEqual({p.GetNumber(): p.GetNetname() for p in f.Pads()}, {"1": "VBUS", "2": "VBUS_IC"})
        self.assertEqual(str(f.GetFPID().GetLibItemName()), "R_1206_3216Metric")
        self.assertFalse(f.IsFlipped())

    def test_panel_tabs_keep_3_mm_from_every_capacitor(self):
        """Plan 08 section 4.5: scripts/panel_tabs.py with the P1 tab azimuths (the order script default) passes."""
        import pcb_rules
        az = ",".join("%g" % a for a in pcb_rules.P1_TAB_AZIMUTHS)
        with tempfile.TemporaryDirectory() as t:
            res = subprocess.run([sys.executable, str(ROOT / "scripts" / "panel_tabs.py"), str(BOARD), t + "/tabs.kicad_pcb",
                                  "--azimuths", az, "--min-cap-mm", str(pcb_rules.P1_TAB_CAP_MM)],
                                 capture_output=True, text=True, check=False)
        doc = json.loads(res.stdout[res.stdout.index("{"):])
        self.assertEqual((res.returncode, doc["failures"]), (0, []))


if __name__ == "__main__":
    unittest.main()
