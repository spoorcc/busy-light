# SPDX-License-Identifier: Apache-2.0
"""ADR-0024: levels of the restored HOLD_OK pull-up, the GPIO0 series resistor and the CC series resistors."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sim"))
import gate_rework_levels as g  # noqa: E402


class Levels(unittest.TestCase):
    def test_hold_ok_valid_high_from_the_hw010_reference_voltage(self):
        self.assertGreater(g.hold_ok_high(4.3), g.LVC_VIH)          # 2.04 V: thin margin at the 4.3 V reference
        self.assertAlmostEqual(g.hold_ok_high(4.3), 2.036, delta=0.002)
        self.assertGreater(g.hold_ok_high(4.75) - g.LVC_VIH, 0.45)

    def test_hold_ok_high_with_the_pull_up_on_vdd_u1(self):
        """ADR-0025, owner 2026-11-24: R6 = 100 k on VDD_U1. With the TPS3808 RESET leakage of 300 nA (SBVS050N, RV-019 G9) and
        the worst-case input leakage of the three inputs the level at the 4.399 V release maximum is 2.77 V (VIH 2.0 V). With
        the old 150 k it was 2.0001 V: no margin."""
        v = g.hold_ok_high_vdd_u1(4.399)
        self.assertAlmostEqual(v, 2.77, delta=0.01)
        self.assertGreater(v - g.LVC_VIH, 0.7)
        self.assertAlmostEqual(g.hold_ok_high_vdd_u1(4.399, r6=150e3), 2.0, delta=0.002)   # the rejected value
        self.assertGreater(g.hold_ok_high_vdd_u1(4.0) - g.LVC_VIH, 0.3)                    # even at the release minimum of the divider
        self.assertEqual(g.hold_ok_high_vdd_u1(9.0, n_inputs=0), 5.1 - g.TPS3808_ILKG * 100e3)   # the zener clamps VDD_U1

    def test_r6_meets_the_tps3808_vpor_rule(self):
        self.assertAlmostEqual(g.hold_ok_r6_min_tps3808(), 40e3, delta=1.0)
        self.assertGreater(100e3, g.hold_ok_r6_min_tps3808())

    def test_r6_meets_the_vpor_rule(self):
        self.assertAlmostEqual(g.hold_ok_r6_min(), 133.9e3, delta=100)
        self.assertGreaterEqual(150e3, g.hold_ok_r6_min())

    def test_gpio0_low_needs_the_internal_pull_up_off(self):
        # ADR-0024 finding: at the 30 k pull-up corner the low level equals VIL (0.25 x 3.0 V): no margin, so the firmware
        # keeps the GPIO0 pull-up off (SW-009 proposal); with the typical 45 k it reads low, with the pull-up off it is 0 V
        self.assertAlmostEqual(g.gpio0_pin_with_pullup(rpu=30e3), 0.75, delta=0.001)
        self.assertLess(g.gpio0_pin_with_pullup(rpu=45e3), 0.75 - 0.15)
        self.assertLess(g.gpio0_drive_current(), 0.4e-3)

    def test_cc_shift_is_small(self):
        self.assertAlmostEqual(g.cc_shift(22e3) * 100, -0.37, delta=0.01)
        self.assertGreater(g.cc_shift(10e3), -0.007)
        self.assertEqual(g.rd_seen_by_source(), (4700.0, 5700.0))


if __name__ == "__main__":
    unittest.main()
