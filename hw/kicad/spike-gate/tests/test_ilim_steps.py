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


class TrimT1(unittest.TestCase):
    """Plan 08 trim T1 (owner rule of 2026-11-17 in HW-010): one 27.7 k 0.1 % part replaces 27.4 k + 301 ohm."""

    def test_value_is_e192(self):
        self.assertIn(2.77, il.E192_M)
        self.assertEqual(il.candidate_p1(), (47.0, 56.2, 27.7))

    def test_windows_stay_inside_hw010(self):
        kw = dict(leak_a=il.TMUX_LEAK_A, rds_max=il.TMUX_RDS_ON_MAX_OHM)
        mg = il.margins(*il.candidate_p1(), il.TOL_01PCT, **kw)
        self.assertTrue(all(v > 0 for v in mg.values()), mg)
        w = il.step_windows(*il.candidate_p1(), il.TOL_01PCT, **kw)
        self.assertGreaterEqual(w["3"][0], il.STEP3_MIN_MA)
        self.assertLessEqual(w["3"][1], il.STEP3_MAX_MA)
        self.assertGreaterEqual(w["2"][0], il.STEP2_BAND_MA[0])
        self.assertLessEqual(w["2"][1], il.STEP2_BAND_MA[1])

    def test_margins_within_0p1_ma_of_the_series_pair(self):
        kw = dict(leak_a=il.TMUX_LEAK_A, rds_max=il.TMUX_RDS_ON_MAX_OHM)
        old = il.margins(*il.candidate_c(), il.TOL_01PCT, **kw)
        new = il.margins(*il.candidate_p1(), il.TOL_01PCT, **kw)
        for k in old:
            self.assertLessEqual(abs(new[k] - old[k]), 0.1, k)   # within 0.1 mA in both directions (plan 08 4.1)


class BothOnStep3(unittest.TestCase):
    """ADR-0023 (owner 2026-11-18): step 3 = both select switches on; R_ILIM3 = R_ILIM2 = 56.2 k (0.1 %)."""
    KW = dict(leak_a=il.TMUX_LEAK_A, rds_max=il.TMUX_RDS_ON_MAX_OHM)

    def test_values(self):
        self.assertEqual(il.candidate_both_on(), (47.0, 56.2, 56.2))

    def test_every_state_inside_the_hw010_limits(self):
        w = il.both_on_windows(*il.candidate_both_on(), il.TOL_01PCT, **self.KW)
        self.assertGreaterEqual(w["1"][0], il.STEP1_MIN_MA)
        self.assertLessEqual(w["1"][1], il.STEP1_MAX_MA)
        self.assertGreaterEqual(w["2"][0], il.STEP2_BAND_MA[0])
        self.assertLessEqual(w["2"][1], il.STEP2_BAND_MA[1])
        self.assertGreaterEqual(w["3"][0], il.STEP3_MIN_MA)
        self.assertLessEqual(w["3"][1], il.STEP3_MAX_MA)
        # EN3 alone is a legal state too: it must stay at or below the step 3 maximum (no over-limit state exists)
        self.assertLessEqual(w["en3_only"][1], il.STEP3_MAX_MA)

    def test_numbers_of_the_owner_question(self):
        w = il.both_on_windows(*il.candidate_both_on(), il.TOL_01PCT, **self.KW)
        self.assertAlmostEqual(w["3"][0], 1368.8, delta=0.2)
        self.assertAlmostEqual(w["3"][1], 1553.5, delta=0.2)

    def test_the_old_over_limit_state_is_gone(self):
        # exclusive design: both switches on gave 1817 to 2020 mA (only the NOR gate prevented it)
        old = il.three_steps(*il.candidate_p1(), il.TOL_01PCT, **self.KW)["both"]
        self.assertGreater(old[2], il.STEP3_MAX_MA)
        new = il.both_on_windows(*il.candidate_both_on(), il.TOL_01PCT, **self.KW)
        self.assertLessEqual(max(v[1] for v in new.values()), il.STEP3_MAX_MA)


class Generator(unittest.TestCase):
    def test_generator_values_are_the_checked_set(self):
        P = layout_full.PARTS
        self.assertEqual((P["R_ILIM1"][-1], P["R_ILIM2"][-1], P["R_ILIM3"][-1]),
                         ("47.0k 0.1%", "56.2k 0.1%", "56.2k 0.1%"))     # ADR-0023: step 3 = both switches on
        self.assertNotIn("R20", P)
        r1, r2 = ohms(P["R_ILIM1"][-1]) / 1e3, ohms(P["R_ILIM2"][-1]) / 1e3
        r3 = ohms(P["R_ILIM3"][-1]) / 1e3
        self.assertEqual((r1, r2, r3), il.candidate_both_on())
        w = il.both_on_windows(r1, r2, r3, il.TOL_01PCT, leak_a=il.TMUX_LEAK_A, rds_max=il.TMUX_RDS_ON_MAX_OHM)
        self.assertGreaterEqual(w["1"][0], il.STEP1_MIN_MA)
        self.assertLessEqual(w["1"][1], il.STEP1_MAX_MA)
        self.assertGreaterEqual(w["3"][0], il.STEP3_MIN_MA)
        self.assertLessEqual(max(v[1] for v in w.values()), il.STEP3_MAX_MA)


class TableAnchor(unittest.TestCase):
    """RV-017 row 6: the equation minimum lies above the SLVS841G table at 15 and 20 kohm; the anchored limits take the
    conservative side of both."""

    def test_interpolation_hits_the_table_points(self):
        for r, lo, nom, hi in il.IOS_TABLE:
            self.assertAlmostEqual(il.table_interp(r, 1), lo, places=6)
            self.assertAlmostEqual(il.table_interp(r, 2), nom, places=6)
            self.assertAlmostEqual(il.table_interp(r, 3), hi, places=6)

    def test_outside_the_table_is_none(self):
        self.assertIsNone(il.table_interp(14.9, 1))
        self.assertIsNone(il.table_interp(232.0, 3))

    def test_anchored_minimum_is_the_lower_of_both(self):
        for r in (15.0, 17.61, 20.0, 30.0, 49.9, 100.0):
            self.assertLessEqual(il.ios_min_anchored(r), il.ios_min(r))
            self.assertLessEqual(il.ios_min_anchored(r), il.table_interp(r, 1))
            self.assertGreaterEqual(il.ios_max_anchored(r), il.ios_max(r))
            self.assertGreaterEqual(il.ios_max_anchored(r), il.table_interp(r, 3))

    def test_reviewer_figure_at_the_step_3_resistance(self):
        # RV-017 row 6: log-log interpolation of the table minima at 17.61 k gives 1367.0 mA (reviewer, rounded)
        self.assertAlmostEqual(il.table_interp(17.61, 1), 1366.6, delta=0.5)

    def test_anchoring_off_by_default(self):
        kw = dict(leak_a=il.TMUX_LEAK_A, rds_max=il.TMUX_RDS_ON_MAX_OHM)
        self.assertEqual(il.both_on_windows(47.0, 56.2, 56.2, il.TOL_01PCT, **kw),
                         il.both_on_windows(47.0, 56.2, 56.2, il.TOL_01PCT, anchored=False, **kw))


class DriftBudget(unittest.TestCase):
    """Owner decision 3 of 2026-11-22: resistor TCR, soldering and life drift in the model before R_ILIM3 is decided."""
    KW = dict(leak_a=il.TMUX_LEAK_A, rds_max=il.TMUX_RDS_ON_MAX_OHM, anchored=True)

    def test_stack_of_each_drift_set(self):
        self.assertAlmostEqual(il.tol_eff(**il.DRIFT_SETS["tolerance_only"]), 0.001, places=9)
        self.assertAlmostEqual(il.tol_eff(**il.DRIFT_SETS["yageo_rt_guaranteed"]), 0.0125, places=9)   # 0.1 + 0.15 + 0.5 + 0.5 %
        self.assertAlmostEqual(il.tol_eff(**il.DRIFT_SETS["vishay_mct_class025"]), 0.0040, places=9)   # 0.1 + 0.15 + 0.05 + 0.1 %
        self.assertAlmostEqual(il.tol_eff(0.001, 25.0, 0.0, 0.0), 0.0025, places=9)                    # tolerance + TCR over 60 K

    def test_budget_is_the_edge_of_the_margins(self):
        b = il.drift_budget(47.0, 56.2, 54.9, **self.KW)
        self.assertGreaterEqual(min(il.both_on_margins(47.0, 56.2, 54.9, b, **self.KW).values()), 0.0)
        self.assertLess(min(il.both_on_margins(47.0, 56.2, 54.9, b * 1.001, **self.KW).values()), 0.0)

    def test_56k2_fails_with_tolerance_and_tcr_alone(self):
        b = il.drift_budget(47.0, 56.2, 56.2, **self.KW)
        self.assertAlmostEqual(b, 0.00171, delta=0.00002)
        self.assertLess(b, il.tol_eff(0.001, 25.0, 0.0, 0.0))

    def test_54k9_holds_up_to_the_step_1_budget(self):
        b3 = il.drift_budget(47.0, 56.2, 54.9, keys=("s3_min", "s3_max"), **self.KW)
        b1 = il.drift_budget(47.0, 56.2, 54.9, keys=("s1_min", "s1_max"), **self.KW)
        self.assertAlmostEqual(b3, 0.00913, delta=0.00002)
        self.assertAlmostEqual(b1, 0.00931, delta=0.00002)
        self.assertGreater(b3, il.tol_eff(**il.DRIFT_SETS["vishay_mct_class025"]))

    def test_guaranteed_rt_drift_exceeds_every_budget(self):
        # the in-stock Yageo RT parts: the datasheet limits do not prove HW-010 for any R_ILIM3 value, nor step 1
        stack = il.tol_eff(**il.DRIFT_SETS["yageo_rt_guaranteed"])
        for r3 in (56.2, 54.9):
            self.assertLess(il.drift_budget(47.0, 56.2, r3, **self.KW), stack)

    def test_54k9_is_the_best_e192_value(self):
        r3, b = il.best_r3_for_budget(47.0, 56.2, **self.KW)
        self.assertEqual(r3, 54.9)
        self.assertAlmostEqual(b, 0.00913, delta=0.00002)

    def test_margins_of_both_values_with_anchoring(self):
        m56 = il.both_on_margins(47.0, 56.2, 56.2, il.TOL_01PCT, **self.KW)
        m549 = il.both_on_margins(47.0, 56.2, 54.9, il.TOL_01PCT, **self.KW)
        self.assertAlmostEqual(m56["s3_min"], 1.0, delta=0.1)
        self.assertAlmostEqual(m549["s3_min"], 11.3, delta=0.1)
        self.assertAlmostEqual(m549["s3_max"], 12.7, delta=0.1)


if __name__ == "__main__":
    unittest.main()
