# SPDX-License-Identifier: Apache-2.0
"""Regression for sim/ilim_steps.py: TPS2553 limit steps against the HW-010 numbers (analysis-ilim-steps.md)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
sys.path.insert(0, str(HERE.parent / "sim"))
import ilim_steps as il  # noqa: E402
import layout_full  # noqa: E402


def ohms(s):
    s = s.split()[0]   # a value string may carry a tolerance, e.g. "47k 0.1%"
    return float(s[:-1]) * 1e3 if s.endswith("k") else float(s)


class Equations(unittest.TestCase):
    def test_equations_enclose_the_datasheet_table(self):
        # SLVS841G section 6.5 points (min, nom, max); the equations are the wider (conservative) envelope
        for r, (lo, nom, hi) in ((15.0, (1610, 1700, 1800)), (20.0, (1200, 1295, 1375)),
                                 (49.9, (475, 520, 565)), (210.0, (110, 130, 150))):
            self.assertAlmostEqual(il.ios_min(r), lo, delta=0.01 * lo)
            self.assertAlmostEqual(il.ios_max(r), hi, delta=0.04 * hi)
            self.assertLessEqual(il.ios_min(r), lo * 1.005)
            self.assertGreaterEqual(il.ios_max(r), hi * 0.995)
            self.assertAlmostEqual(il.ios_nom(r), nom, delta=0.015 * nom)


class AdrFinding(unittest.TestCase):
    def test_adr_0010_values_exceed_623_at_one_percent(self):
        # ADR-0010 lists 623 mA as the step 1 maximum; with the resistor at -1 % the equation gives about 629 mA
        mx = il.limits(46.4, 0.01, (), 0, leak_a=0.0)[2]
        self.assertGreater(mx, il.STEP1_MAX_MA)
        self.assertLess(mx, 631.0)


class Search(unittest.TestCase):
    def test_no_one_percent_pair_meets_hw010(self):
        for ser in (il.e96, il.e192):
            self.assertIsNone(il.search(il.TOL_1PCT, ser, leak_a=0.0))

    def test_e96_does_not_meet_even_at_point_one_percent(self):
        self.assertIsNone(il.search(il.TOL_01PCT, il.e96, leak_a=0.0))

    def test_candidate_a_meets_with_thin_margin(self):
        r1, r2, r3 = il.candidate_a()
        self.assertEqual((r1, r3), (47.0, 27.7))
        mg = il.margins(r1, r2, r3, il.TOL_01PCT, leak_a=0.0)
        self.assertTrue(all(v > 0 for v in mg.values()), mg)
        self.assertLess(min(mg.values()), 10.0)   # thin: recorded in the report, not a comfortable margin

    def test_leakage_budget_is_small(self):
        b = il.leakage_budget_a(*il.candidate_a(), il.TOL_01PCT)
        self.assertGreater(b, 50e-9)
        self.assertLess(b, 200e-9)

    def test_both_select_mosfets_on_exceed_top_limit(self):
        r1, r2, r3 = il.candidate_a()
        self.assertGreater(il.three_steps(r1, r2, r3, il.TOL_01PCT, leak_a=0.0)["both"][2], il.STEP3_MAX_MA)

    def test_rds_has_negligible_effect(self):
        r1, _, r3 = il.candidate_a()
        a = il.limits(r1, il.TOL_01PCT, (r3,), 1, leak_a=0.0, rds_max=0.0)[0]
        b = il.limits(r1, il.TOL_01PCT, (r3,), 1, leak_a=0.0, rds_max=15.0)[0]
        self.assertLess(a - b, 2.0)

    def test_deterministic(self):
        self.assertEqual(il.candidate_a(), il.candidate_a())
        self.assertEqual(il.candidate_b(), il.candidate_b())


class TmuxCandidate(unittest.TestCase):
    """Owner decisions 2026-11-05: R_ILIM 47.0 k, 56.2 k, 27.4 k + 301 ohm (0.1 %) and TMUX1101 select switches."""

    def test_candidate_values(self):
        r1, r2, r3 = il.candidate_c()
        self.assertEqual((r1, r2), (47.0, 56.2))
        self.assertAlmostEqual(r3, 27.701, places=6)

    def test_switch_numbers_are_the_datasheet_limits(self):
        # TMUX1101 SCDS410D tab. 6.6: off leakage 0.2 nA to 85 degC; ron 9.5 ohm to 85 degC
        self.assertEqual(il.TMUX_LEAK_A, 0.2e-9)
        self.assertEqual(il.TMUX_RDS_ON_MAX_OHM, 9.5)

    def test_windows_of_the_three_steps(self):
        w = il.step_windows(*il.candidate_c(), il.TOL_01PCT, leak_a=il.TMUX_LEAK_A, rds_max=il.TMUX_RDS_ON_MAX_OHM)
        self.assertAlmostEqual(w["1"][0], 504.2, delta=0.6)
        self.assertAlmostEqual(w["1"][1], 616.6, delta=0.6)
        self.assertAlmostEqual(w["2"][0], 935.0, delta=2.0)
        self.assertAlmostEqual(w["2"][1], 1092.0, delta=2.0)
        self.assertAlmostEqual(w["3"][0], 1381.0, delta=1.0)
        self.assertAlmostEqual(w["3"][1], 1567.0, delta=1.0)

    def test_hw010_numbers_met(self):
        mg = il.margins(*il.candidate_c(), il.TOL_01PCT, leak_a=il.TMUX_LEAK_A, rds_max=il.TMUX_RDS_ON_MAX_OHM)
        self.assertTrue(all(v > 0 for v in mg.values()), mg)
        self.assertLess(min(mg.values()), 10.0)   # still thin

    def test_step_2_inside_the_proposed_window(self):
        w = il.step_windows(*il.candidate_c(), il.TOL_01PCT, leak_a=il.TMUX_LEAK_A, rds_max=il.TMUX_RDS_ON_MAX_OHM)
        self.assertGreaterEqual(w["2"][0], il.STEP2_BAND_MA[0])
        self.assertLessEqual(w["2"][1], il.STEP2_BAND_MA[1])
        self.assertEqual(il.STEP2_BAND_MA, (850.0, 1150.0))

    def test_series_pair_keeps_the_tolerance_band(self):
        # two 0.1 % parts in series: the sum is within 0.1 % of the nominal sum
        r3 = 27.4 + 0.301
        hi = 27.4 * 1.001 + 0.301 * 1.001
        self.assertAlmostEqual(hi / r3, 1.001, places=9)

    def test_both_on_is_still_above_the_top_limit(self):
        # the extra state must be excluded by the gate logic (U13), the resistors alone do not exclude it
        r1, r2, r3 = il.candidate_c()
        both = il.three_steps(r1, r2, r3, il.TOL_01PCT, leak_a=il.TMUX_LEAK_A, rds_max=il.TMUX_RDS_ON_MAX_OHM)["both"]
        self.assertGreater(both[2], il.STEP3_MAX_MA)


class Generator(unittest.TestCase):
    def test_generator_values_are_the_checked_set(self):
        P = layout_full.PARTS
        self.assertEqual((P["R_ILIM1"][-1], P["R_ILIM2"][-1], P["R_ILIM3"][-1], P["R20"][-1]),
                         ("47.0k 0.1%", "56.2k 0.1%", "27.4k 0.1%", "301 0.1%"))
        r1, r2 = ohms(P["R_ILIM1"][-1]) / 1e3, ohms(P["R_ILIM2"][-1]) / 1e3
        r3 = (ohms(P["R_ILIM3"][-1]) + ohms(P["R20"][-1])) / 1e3
        self.assertEqual((r1, r2), il.candidate_c()[:2])
        self.assertAlmostEqual(r3, il.candidate_c()[2], places=6)
        mg = il.margins(r1, r2, r3, il.TOL_01PCT, leak_a=il.TMUX_LEAK_A, rds_max=il.TMUX_RDS_ON_MAX_OHM)
        self.assertTrue(all(v >= 0 for v in mg.values()), mg)


if __name__ == "__main__":
    unittest.main()
