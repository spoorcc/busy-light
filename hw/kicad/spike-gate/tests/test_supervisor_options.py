# SPDX-License-Identifier: Apache-2.0
"""ADR-0025: threshold windows of the U5 supervisor options (sim/supervisor_options.py)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sim"))
import supervisor_options as so  # noqa: E402


class Thresholds(unittest.TestCase):
    def test_tps3840dl40_matches_the_hw010_table(self):
        # HW-010 approved table: release 4.115 to 4.285 V
        _, _, rel_lo, rel_hi = so.tps3840(4.0)
        self.assertAlmostEqual(rel_lo, 4.115, places=3)
        self.assertAlmostEqual(rel_hi, 4.285, places=3)

    def test_push_pull_43_can_release_above_the_vbus_minimum(self):
        self.assertGreater(so.tps3840(4.3)[3], so.VBUS_MIN_ASSUMED)
        self.assertLess(so.tps3840(4.2)[3], so.VBUS_MIN_ASSUMED)

    def test_tps3808_divider_window(self):
        a, b, c, d = so.tps3808_divider(931.0, 100.0)
        self.assertAlmostEqual(a, 3.996, delta=0.002)
        self.assertAlmostEqual(b, 4.360, delta=0.002)
        self.assertLess(d, so.VBUS_MIN_ASSUMED)
        self.assertEqual(a, c)   # no hysteresis minimum in the datasheet: the lower release edge equals the falling edge

    def test_sense_current_moves_the_threshold(self):
        with_i = so.tps3808_divider(931.0, 100.0)
        without = so.tps3808_divider(931.0, 100.0, i_sense=0.0)
        self.assertAlmostEqual(with_i[1] - without[1], 25e-9 * 90.6e3 * 10.5, delta=0.003)


if __name__ == "__main__":
    unittest.main()
