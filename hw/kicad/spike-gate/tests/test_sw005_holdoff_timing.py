# SPDX-License-Identifier: Apache-2.0
"""SW-005 / SYS-020 timing chain arithmetic (interval arithmetic, assumptions as stated in the module)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "sim"))
import sw005_holdoff_timing as t  # noqa: E402


class Timing(unittest.TestCase):
    def test_reads_vs_window(self):
        self.assertEqual(t.reads_needed(5, 500, 100), 6)     # 5 reads at 100 ms span only 400 ms
        self.assertEqual(t.reads_needed(5, 500, 125), 5)
        self.assertEqual(t.reads_needed(5, 500, 1), 501)     # the 500 ms term then dominates
        self.assertEqual(t.stable_window_ms(5, 500, 100), 500)

    def test_spec_window_exceeds_one_second(self):
        lo, hi = t.raise_time(t.W_SPEC)
        self.assertAlmostEqual(lo, 200.1 + 500 + 0, delta=0.5)
        self.assertGreater(hi, t.SYS020_LIMIT_MS)             # 600 + 500 + 100 + ...
        self.assertAlmostEqual(hi, 10 + 0.35 + 600 + 100 + 500 + 10 + 2, delta=0.01)

    def test_budget_limits(self):
        self.assertAlmostEqual(t.max_holdoff_for_budget(), 1000 - (10 + 0.35 + 100 + 500 + 10 + 2), places=6)
        self.assertEqual(t.window_for_budget(600.0), 200.0)   # 300 ms would give 1022.35 ms > 1000

    def test_tps3840_ratio(self):
        self.assertGreater(t.min_max_for_min(200), 540.0)     # min 200 forces max >= about 545 ms
        self.assertLess(t.min_max_for_min(200), 600.0)

    def test_rail_holdup(self):
        self.assertAlmostEqual(t.rail_holdup_ms(100, 1.35, 0.623), 0.0688, delta=0.0005)   # microseconds, not ms
        self.assertAlmostEqual(t.min_cap_uf(50, 1.35, 0.623), 72700.0, delta=1.0)   # 72.7 mF


if __name__ == "__main__":
    unittest.main()
