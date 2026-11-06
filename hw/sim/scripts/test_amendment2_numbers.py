"""Tests for amendment2_numbers.py (HW-010, ADR-0016 Amendment 2). Run: cd hw/sim/scripts && python3 -m unittest."""

import unittest

import amendment2_numbers as m


class Amendment2Test(unittest.TestCase):
    def test_holdoff_window_matches_adr(self) -> None:
        lo, hi = m.holdoff_window_ms()
        self.assertAlmostEqual(lo, 203.2, places=1)
        self.assertAlmostEqual(hi, 553.2, places=1)

    def test_holdoff_inside_hw010_proposal(self) -> None:
        lo, hi = m.holdoff_window_ms()
        self.assertGreaterEqual(lo, m.HOLDOFF_MIN_MS)
        self.assertLessEqual(hi, m.HOLDOFF_MAX_MS)

    def test_step_windows_match_adr(self) -> None:
        w = m.step_windows_ma()
        self.assertAlmostEqual(w["1"][0], 504.2, places=1)
        self.assertAlmostEqual(w["1"][1], 616.6, places=1)
        self.assertAlmostEqual(w["2"][0], 934.9, places=1)
        self.assertAlmostEqual(w["2"][1], 1091.7, places=1)
        self.assertAlmostEqual(w["3"][0], 1381.2, places=1)
        self.assertAlmostEqual(w["3"][1], 1566.6, places=1)

    def test_steps_inside_hw010_limits(self) -> None:
        w = m.step_windows_ma()
        self.assertGreaterEqual(w["1"][0], 500.0)
        self.assertLessEqual(w["1"][1], 623.0)
        self.assertGreaterEqual(w["3"][0], 1366.0)
        self.assertLessEqual(w["3"][1], 1577.0)


if __name__ == "__main__":
    unittest.main()
