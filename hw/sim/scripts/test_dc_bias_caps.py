"""Tests for dc_bias_caps.py: the arithmetic and the requirement checks, not the assumed retention."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import dc_bias_caps as d  # noqa: E402


def test_low_and_high_factors_by_hand():
    assert d.LOW == pytest.approx(0.9 * 0.85)
    assert d.HIGH == pytest.approx(1.1 * 1.15)


def test_c2_meets_the_usb_minimum_at_the_maker_retention():
    # 4.7 uF x 0.4705 x 0.765 = 1.692 uF
    assert d.hw015_low() == pytest.approx(1.692e-6, rel=0.002)
    assert d.hw015_low() >= d.USB_MIN


def test_c2_fails_below_its_break_even_retention():
    be = d.break_even(d.CAPS["C2"][1], d.USB_MIN)
    assert be == pytest.approx(0.278, abs=0.002)
    assert d.hw015_low(be * 0.99) < d.USB_MIN


def test_a_nominal_1uf_would_fail_the_usb_minimum():
    # the finding of the analysis: the old "1u" C2 cannot reach 1.0 uF at 5.25 V
    assert d.c_low(1e-6, d.RETENTION["C2"]) < d.USB_MIN


def test_vbus_sum_at_0v_is_inside_the_usb_maximum_with_room_for_protection_parts():
    assert d.hw015_high() == pytest.approx(6.33e-6, rel=0.005)
    assert d.USB_MAX - d.hw015_high() > 3e-6


def test_c5_meets_the_regulator_minimum_effective_value():
    assert d.hw014_ldo_input() == pytest.approx(0.6737e-6, rel=0.005)
    assert d.hw014_ldo_input() > d.LDO_EFFECTIVE_MIN


def test_c5_fails_below_its_break_even_retention():
    be = d.break_even(d.CAPS["C5"][1], d.LDO_EFFECTIVE_MIN)
    assert d.hw014_ldo_input(be * 0.99) < d.LDO_EFFECTIVE_MIN


def test_populated_5v_sum_and_spare_headroom():
    # (10 + 2.2 + 16 x 0.1) uF x 1.265 = 17.47 uF
    assert d.hw014_sum_at_0v() == pytest.approx(17.47e-6, rel=0.002)
    assert d.spare_headroom() == pytest.approx(82.5e-6, rel=0.002)


def test_start_up_bound_is_above_the_populated_sum_plus_zero_spares():
    assert d.start_up_bound() > d.hw014_sum_at_0v()


def test_100n_x7r_keeps_its_value_at_5v():
    # 0.1 uF x 0.9983 x 0.765 = 76.4 nF
    assert d.c_100n_low_5v() == pytest.approx(76.4e-9, rel=0.002)
    assert d.RETENTION_100N > 0.99


def test_spare_nominal_room_follows_the_headroom():
    # 82.5 uF / 1.265 = 65.2 uF nominal for C4 and C32 together
    assert d.spare_nominal_max_at_0v() == pytest.approx(65.2e-6, rel=0.005)
    assert d.spare_nominal_max_at_0v() * d.HIGH == pytest.approx(d.spare_headroom())


def test_protection_parts_fit_in_the_usb_maximum_with_three_orders_of_margin():
    # 3 x 300 pF + 35 pF + 45 pF = 0.98 nF
    assert d.protection_total() == pytest.approx(0.98e-9, rel=1e-6)
    assert d.hw015_high_with_protection() < d.USB_MAX
    assert (d.USB_MAX - d.hw015_high()) / d.protection_total() > 1000


def test_u6_vbus_pin_capacitance_would_need_to_be_microfarads_to_matter():
    # 10 uF - 6.33 uF - (0.98 nF - 35 pF) = 3.67 uF
    assert d.u6_vbus_break_even() == pytest.approx(3.67e-6, rel=0.005)
    assert d.u6_vbus_break_even() / d.PROTECTION["U6"] > 1e4
