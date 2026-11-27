# SPDX-License-Identifier: Apache-2.0
"""Requirement checks on the stored P1 board `board-p1/` (plan 08 section 5; HW-008, HW-016, HW-017; TC-216, TC-217 board part).

These read the committed board file. The strict gate (DRC and ERC) runs in `scripts/ci_hw.sh` and `scripts/fab_p1.sh`, the fab
check and the power check in `scripts/fab_p1.sh` (the power check since 2026-11-19); this file holds the checks that no gate
makes (sides, the spare footprints at the TPS2553 output, the damping link nets, the panel tab clearance) and runs the power
check too, so the spike test suite fails on a thin supply path. Skipped without pcbnew or without the board."""
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
        dnp_bottom = ("C4", "C32")      # HW-016 spares, do-not-populate (RV-016 row 41: no other DNP part may sit on B)
        bad = [r for r, f in self.fps.items() if f.IsFlipped() and not r.startswith(bottom_ok) and r not in dnp_bottom]
        self.assertEqual(bad, [])
        self.assertTrue(all(self.fps[r].IsDNP() for r in dnp_bottom))

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

    def test_supply_drops_and_full_width_paths(self):
        """pcb_power_check on the stored board: every supply case within the analyst's 50 mV and without a thin track in its
        current path (batch p1b7: a board whose +5V current ran through 0.15 mm track passed every other check)."""
        res = subprocess.run([sys.executable, str(HERE.parent / "src" / "pcb_power_check.py"), str(BOARD)],
                             capture_output=True, text=True, check=True)
        nets = json.loads(res.stdout[res.stdout.index("{"):])["nets"]
        for net, v in nets.items():
            self.assertTrue(v["within_50mv"], (net, v["drop_mv"]))
            self.assertIs(v["full_width_path"], True, net)
        ip = json.loads(res.stdout[res.stdout.index("{"):])["input_path"]
        self.assertIs(ip["within_budget"], True, ip)              # HW-017: J1 to U7 <= 100 mV at 1.5 A, R22 at 10 mohm

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

    def test_housing_size_within_mech001(self):
        """MECH-001 (amended 2026-11-22 to 60 mm, 2026-11-27 to 65 mm; RV-016 row 22: the 59.24 mm was not reported against the limit)."""
        import mech_outline
        self.assertLessEqual(self.info["largest_dim_mm"], mech_outline.m("MAX_DIM_MECH001"))
        self.assertEqual(mech_outline.m("MAX_DIM_MECH001"), 65.0)

    def test_known_u9_courtyard_overlaps_only(self):
        """The strict DRC tolerates 14 courtyard overlaps with U9 (DEV-004) and checks only that U9 takes part. The owner
        decisions of 2026-11-18 (U9 courtyard as an obstacle, module 5 mm towards the edge) leave exactly the fixed ring
        parts D6 to D12, C13 to C18 and SW1 in it; a movable part in their place must fail (RV-016 row 20)."""
        import kicad_strict
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / "drc.json"
            kicad_strict.run_cli("drc", BOARD, out)
            report = json.loads(out.read_text(encoding="utf-8"))
        pairs = [kicad_strict.item_refs(v) for v in report.get("violations", []) if v["type"] == "courtyards_overlap"]
        self.assertTrue(all("U9" in p and len(p) == 2 for p in pairs), pairs)
        expected = {"D%d" % i for i in range(6, 13)} | {"C%d" % i for i in range(13, 19)} | {"SW1"}
        self.assertEqual(sorted(r for p in pairs for r in p - {"U9"}), sorted(expected))

    @unittest.expectedFailure
    def test_placement_rules_met(self):
        """Plan 08 section 4.3 placement gate: every ADR-0016 proximity rule and every input-path rule of section 4.2 met
        (pcb_layout_check.py). Expected to fail on board-p1 (RV-016 rows 11 and 12: C1, C27, C30, C31 to U5, R19 to U15
        and all four input-path rules missed); the next placement must pass, and then this marker goes."""
        import pcb_layout_check
        missed = [r for r in pcb_layout_check.measure(self.board, pcb_layout_check.all_rules()) if r["met"] is not True]
        self.assertEqual(missed, [])

    @unittest.expectedFailure
    def test_board_carries_identification_text_and_fiducials(self):
        """Plan 08 R4 (i), RV-019 pass 2 finding 8 (RV-016 row 18): the finishing step put the board identification
        "busy-light P1 <commit>" on B.SilkS and at least three fiducials on the board. Expected to fail on the board stored
        before the re-placement (no text, since pcb_finish.py had no identification then); the stored new board must pass,
        and then this marker goes."""
        texts = [d.GetText() for d in self.board.GetDrawings()
                 if d.GetClass() == "PCB_TEXT" and d.GetLayer() == pcbnew.B_SilkS]
        self.assertTrue(any(s.startswith("busy-light P1") for s in texts), texts)
        fids = sorted(r for r in self.fps if r.startswith("FID"))
        self.assertGreaterEqual(len(fids), 3, fids)

    @unittest.expectedFailure
    def test_main_path_is_0_6_mm_wide(self):
        """Plan 08 step 9 and TC-217: the J1-R22-U7 main path has a copper path of tracks at least 0.6 mm wide
        (pcb_rules.NET_WIDTH) on both nets. Expected to fail on board-p1 (RV-016 row 13: 0.45 mm segments on VBUS and
        VBUS_IC); the next routing must pass, and then this marker goes."""
        import pcb_power_check as P
        import pcb_rules
        ras = P.Raster(self.board)
        layers = [self.board.GetLayerName(lid) for lid in self.board.GetEnabledLayers().CuStack()]
        thin = []
        for net in ("VBUS", "VBUS_IC"):
            src, dst = P.CASES[net][0], P.CASES[net][1]
            r = P.effective_resistance(self.board, ras, net, src, dst, layers, pcb_rules.NET_WIDTH[net] - 0.001)
            if r is None or r == float("inf"):
                thin.append(net)
        self.assertEqual(thin, [])


if __name__ == "__main__":
    unittest.main()
