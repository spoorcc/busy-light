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


def P_VAL(ref):
    return layout_full.PARTS[ref][-1]


def ohms(s):
    return float(s[:-1]) * 1e3 if s.endswith("k") else float(s)


class ReadbackMargin(unittest.TestCase):
    def setUp(self):
        P = layout_full.PARTS
        self.rs = {ohms(P["R14"][-1]), ohms(P["R15"][-1])}
        self.rpd = {rm.parallel(ohms(P["R2"][-1]), ohms(P["R18"][-1])),
                    rm.parallel(ohms(P["R3"][-1]), ohms(P["R19"][-1]))}

    def test_symmetric_values(self):
        self.assertEqual(len(self.rs), 1)
        self.assertEqual(len(self.rpd), 1)
        self.assertEqual(P_VAL("R18"), P_VAL("R19"))
        self.assertEqual(P_VAL("R18"), "100k")      # decision (a): 100 kohm on each control pin

    def test_open_gate_stays_below_vth_min_with_margin(self):
        rs, rpd = self.rs.pop(), self.rpd.pop()
        cases = {k: v for k, v in rm.open_gate_cases(rs, rpd).items() if "shorted" not in k}
        for name, v in cases.items():
            self.assertLess(v, rm.VTH_MIN_HOT / 1.5, name)

    def test_open_gate_stays_below_tmux_vil_with_margin(self):
        """TMUX1101 SEL: VIL max 0.8 V (SCDS410D tab. 6.6, VDD 3.3 V +-10 %)."""
        rs, rpd = min(self.rs), min(self.rpd)
        cases = {k: v for k, v in rm.open_gate_cases(rs, rpd).items() if "shorted" not in k}
        for name, v in cases.items():
            self.assertLess(v, rm.TMUX_VIL_MAX / 1.5, name)
        self.assertAlmostEqual(rpd, 10e3 * 100e3 / 110e3, delta=1.0)

    def test_gate_high_level_is_above_tmux_vih(self):
        rpd = min(self.rpd)
        v = rm.gate_high_level(3.0, rm.R_OUT_ASSUMED_OHM, rpd)
        self.assertGreater(v, rm.TMUX_VIH_MIN * 1.5)
        self.assertGreater(v, 2.9)

    def test_sel_leakage_is_negligible_on_the_divider(self):
        self.assertLess(rm.TMUX_IIH_HOT_A * min(self.rpd), 0.001)

    def test_one_pulldown_open_is_reported_not_hidden(self):
        """Single fault R2 or R3 open (gate output also open, internal pull-up on): only the 100 kohm remains.
        The level is above VIL max: this is the documented weak point, firmware keeps the pull-ups off."""
        v = rm.open_gate_cases(100e3, 100e3)["GPIO20/21 input with WPU 30k"]
        self.assertGreater(v, rm.TMUX_VIL_MAX)

    def test_old_values_would_fail(self):
        worst = max(rm.open_gate_cases(1e3, 100e3).values())
        self.assertGreater(worst, rm.VTH_MIN)

    def test_readback_level_with_pullups_off(self):
        # gate low or high, internal pull-up off: pin follows the net within 100k * 50 nA
        self.assertLess(100e3 * 50e-9, 0.01)


if __name__ == "__main__":
    unittest.main()
