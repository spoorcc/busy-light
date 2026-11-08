"""Tests for bulk_cap_bounds.py (HW-014 draft): the bound arithmetic only, not the assumptions."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import bulk_cap_bounds as b  # noqa: E402

PROPOSED_UPPER_BOUND = 100e-6  # F, the bracket of the analysis


def test_ios_min_matches_the_datasheet_table_point():
    # SLVS841G section 6.5 (ADR-0010 E2): RILIM 49.9 kohm gives 475 mA minimum over temperature.
    assert b.ios_min(49.9) * 1000 == pytest.approx(475, abs=3)


def test_step1_lowest_limit_is_about_504_ma():
    assert b.i_limit_step1() * 1000 == pytest.approx(504, abs=2)


def test_c_max_by_hand():
    # (1.5 ms x (0.5043 - 0.10) A - 10 uF x 3.3 V) / 5.5 V = (606.5 - 33) uC / 5.5 V = 104.3 uF
    assert b.c_max() == pytest.approx(104.3e-6, rel=0.005)


def test_time_in_limit_is_the_inverse_of_c_max():
    assert b.time_in_limit(b.c_max()) == pytest.approx(b.T_DEGLITCH_MIN * b.DEGLITCH_MARGIN)


def test_more_3v3_capacitance_or_start_load_lowers_the_maximum():
    # RV-013 finding 8: 22 uF on 3V3 breaks the [100] uF bracket
    assert b.c_max(c_3v3=22e-6) < PROPOSED_UPPER_BOUND
    assert b.c_max(i_start=0.2) < b.c_max(i_start=0.1)


def test_no_budget_raises():
    with pytest.raises(ValueError):
        b.c_max(i_start=0.6)
    with pytest.raises(ValueError):
        b.c_max(c_3v3=1e-3)


def test_ldo_input_minimum():
    assert b.ldo_input_ok(1e-6, 0.6e-6)
    assert not b.ldo_input_ok(1e-6, 0.47e-6)  # must be above 0.47 uF
    assert not b.ldo_input_ok(0.47e-6, 0.47e-6)


def test_sensitivity_table_has_every_corner_and_marks_no_budget():
    rows = b.sensitivity()
    assert len(rows) == 2 + len(b.I_START_CASES)
    assert "none" not in rows[3]


def test_report_lines():
    assert len(b.report()) == 5 + len(b.sensitivity())
