"""Tests for regulator_heat.py."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import regulator_heat as h  # noqa: E402


def test_average_current_all_sleep_is_sleep_plus_other():
    assert h.avg_current(0.0, 0.0) == pytest.approx(h.I_SLEEP + h.I_OTHER)


def test_full_tx_current():
    assert h.avg_current(1.0, 0.0) == pytest.approx(h.I_TX + h.I_OTHER)


def test_power_is_dropout_times_current_plus_ground_term():
    assert h.power(0.1, 5.0) == pytest.approx(1.7 * 0.1 + 5.0 * h.I_GND)


def test_junction_adds_ambient_case_rise_and_rth_times_power():
    assert h.tj(0.5, 100.0, 10.0) == pytest.approx(h.T_AMB + 10.0 + 50.0)


def test_push_model_is_cool_on_the_worst_package():
    i = h.avg_current(0.01, 0.05)
    assert h.tj(h.power(i), 231.1, 40.0) <= h.TJ_MAX - h.TJ_MARGIN


def test_tx_bound_exceeds_limit_on_the_worst_package():
    i = h.avg_current(1.0, 0.0)
    assert h.tj(h.power(i), 231.1, 0.0) > h.TJ_MAX
