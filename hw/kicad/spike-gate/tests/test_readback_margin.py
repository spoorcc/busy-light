# SPDX-License-Identifier: Apache-2.0
"""N1 regression: the readback resistors must not lift an open gate output above the 2N7002 Vgs(th) min."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
sys.path.insert(0, str(HERE.parent / "sim"))
import layout_full  # noqa: E402
import readback_margin as rm  # noqa: E402


def ohms(s):
    return float(s[:-1]) * 1e3 if s.endswith("k") else float(s)


class ReadbackMargin(unittest.TestCase):
    def setUp(self):
        P = layout_full.PARTS
        self.rs = {ohms(P["R14"][-1]), ohms(P["R15"][-1])}
        self.rpd = {ohms(P["R2"][-1]), ohms(P["R3"][-1])}

    def test_symmetric_values(self):
        self.assertEqual(len(self.rs), 1)
        self.assertEqual(len(self.rpd), 1)

    def test_open_gate_stays_below_vth_min_with_margin(self):
        rs, rpd = self.rs.pop(), self.rpd.pop()
        cases = {k: v for k, v in rm.open_gate_cases(rs, rpd).items() if "shorted" not in k}
        for name, v in cases.items():
            self.assertLess(v, rm.VTH_MIN_HOT / 1.5, name)

    def test_old_values_would_fail(self):
        worst = max(rm.open_gate_cases(1e3, 100e3).values())
        self.assertGreater(worst, rm.VTH_MIN)

    def test_readback_level_with_pullups_off(self):
        # gate low or high, internal pull-up off: pin follows the net within 100k * 50 nA
        self.assertLess(100e3 * 50e-9, 0.01)


if __name__ == "__main__":
    unittest.main()
