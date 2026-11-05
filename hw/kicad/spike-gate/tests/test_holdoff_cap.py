# SPDX-License-Identifier: Apache-2.0
"""N4: the parallel C0G hold-off set must keep tD inside 200 to 600 ms. Uses the netlist for the value present."""
import os
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "sim"))
import holdoff_cap as hc  # noqa: E402


class HoldoffCap(unittest.TestCase):
    def test_temperature_term(self):
        self.assertAlmostEqual(hc.temp_frac(), 0.003, places=6)      # 30 ppm x 100 K

    def test_recommended_set(self):
        p = hc.SETS["470+150 (2 parts)"]
        self.assertAlmostEqual(hc.c_window(p)[2], 620e-9, delta=1e-12)
        a, b = hc.td_window(p)
        self.assertAlmostEqual(a * 1e3, 620e-9 * 357.6e3 * (1 - 0.053) * 1e3, delta=0.01)
        self.assertGreater(a, 0.200)
        self.assertLess(b, 0.600)
        self.assertTrue(hc.fits(p, 0.006))                           # also with the earlier 0.6 % allowance

    def test_all_sets_match_earlier_table(self):
        # earlier N4 table (0.6 % temperature): 4-part sets in window, 3x220 nF over
        self.assertTrue(hc.fits(hc.SETS["220+220+150+33 (4 parts)"], 0.006))
        self.assertTrue(hc.fits(hc.SETS["220+220+100+68 (4 parts)"], 0.006))
        self.assertFalse(hc.fits(hc.SETS["3x220 (3 parts)"], 0.006))

    def test_tolerance_matters(self):
        p = [(620e-9, .10, "x")]
        self.assertFalse(hc.fits(p))

    def test_selected_set_window(self):
        p = hc.SETS["220+220+100+68 (4 parts)"]
        self.assertAlmostEqual(hc.c_window(p)[2], 608e-9, delta=1e-12)
        a, b = hc.td_window(p)
        self.assertAlmostEqual(a * 1e3, 205.9, delta=0.3)
        self.assertAlmostEqual(b * 1e3, 560.6, delta=0.3)
        self.assertTrue(hc.fits(p))

    def test_netlist_set_is_the_selected_set(self):
        """The hold-off capacitors in the netlist (C1, C1B, C1C, C1D) are the set the window was computed for."""
        net = Path(os.environ.get("GATE_NET", HERE / "data" / "gate.net"))
        txt = net.read_text()
        vals = {}
        for ref in ("C1", "C1B", "C1C", "C1D"):
            blk = txt[txt.index('(ref "%s")' % ref):][:400]
            m = re.search(r'\(value "(\d+)n C0G 5% (\d+)V"\)', blk)
            self.assertIsNotNone(m, ref)
            vals[ref] = int(m.group(1)) * 1e-9
            self.assertIn("C_1206", blk)
        self.assertEqual(sorted(round(v * 1e9) for v in vals.values()), [68, 100, 220, 220])
        parts = [(c, .05, ref) for ref, c in vals.items()]
        self.assertTrue(hc.fits(parts))
        self.assertNotIn('(ref "C1B")\n      (value "150n', txt)


if __name__ == "__main__":
    unittest.main()
