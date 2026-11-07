"""Tests for ilim_switch_leakage.py (analysis support for HW-010)."""

import math
import unittest

import ilim_switch_leakage as m


class LeakageModelTest(unittest.TestCase):
    def test_parallel(self) -> None:
        self.assertAlmostEqual(m.parallel(100.0, 100.0), 50.0)

    def test_step_resistances(self) -> None:
        s = m.steps()
        self.assertAlmostEqual(s["step 1 (Q2, Q3 off)"][0], 47_000.0)
        self.assertAlmostEqual(s["step 2 (Q2 on, Q3 off)"][0], 47_000 * 56_900 / 103_900, places=3)
        self.assertAlmostEqual(s["step 3 (Q3 on, Q2 off)"][0], 47_000 * 27_700 / 74_700, places=3)

    def test_relative_error_hand_calculation(self) -> None:
        # 2 switches x 100 nA x 47 kohm / 1 V = 0.94 %
        self.assertAlmostEqual(m.relative_error(47_000.0, 2, 100e-9, 1.0), 0.0094)

    def test_limit_and_error_are_inverse(self) -> None:
        limit = m.max_leak_for_error(47_000.0, 2, 1.0, 0.001)
        self.assertTrue(math.isclose(m.relative_error(47_000.0, 2, limit, 1.0), 0.001))

    def test_error_grows_with_leakage_and_falls_with_voltage(self) -> None:
        self.assertGreater(
            m.relative_error(47e3, 2, 1e-6, 1.0), m.relative_error(47e3, 2, 1e-7, 1.0)
        )
        self.assertGreater(
            m.relative_error(47e3, 2, 1e-7, 0.5), m.relative_error(47e3, 2, 1e-7, 2.0)
        )


if __name__ == "__main__":
    unittest.main()
