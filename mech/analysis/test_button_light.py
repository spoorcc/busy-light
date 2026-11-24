# SPDX-License-Identifier: Apache-2.0
"""Tests for button_light.py (plan 09 section 4.4; MECH-002)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import button_light as bl  # noqa: E402

CENTRE_LOW = 0.15
CENTRE_HIGH = 0.20
RING_R = 20.0
TIGHT = 1e-12
PIN = 0.002


def test_centre_gets_about_a_fifth_of_the_value_above_an_led() -> None:
    assert CENTRE_LOW < bl.ring_irradiance(0.0) < CENTRE_HIGH


def test_reference_point_is_one() -> None:
    assert abs(bl.ring_irradiance(RING_R, azimuth_deg=0.0) - 1.0) < TIGHT


def test_irradiance_grows_towards_the_ring() -> None:
    vals = [bl.ring_irradiance(r) for r in (0.0, 5.0, 10.0, 13.0, 16.0, 20.0)]
    assert vals == sorted(vals)


def test_the_centre_value_does_not_depend_on_the_azimuth() -> None:
    assert abs(bl.ring_irradiance(0.0, azimuth_deg=10.0) - bl.ring_irradiance(0.0)) < TIGHT


def test_values_at_the_disc_edge_are_pinned() -> None:
    for r, expect in ((13.0, 0.500), (15.0, 0.672), (16.0, 0.771)):
        assert abs(bl.ring_irradiance(r) - expect) < PIN


def test_a_single_led_has_the_analytic_value() -> None:
    h, ring = bl.HEIGHT_MM, bl.RING_R_MM
    expect = (h**2 / (ring**2 + h**2)) ** 2
    assert abs(bl.ring_irradiance(0.0, n=1) - expect) < TIGHT


def test_rotating_ring_and_point_together_changes_nothing() -> None:
    a = bl.ring_irradiance(10.0, azimuth_deg=0.0, phase_deg=0.0)
    b = bl.ring_irradiance(10.0, azimuth_deg=3.75, phase_deg=3.75)
    assert abs(a - b) < TIGHT
    assert bl.ring_irradiance(20.0, azimuth_deg=3.75, phase_deg=3.75) == pytest.approx(1.0)


def test_a_taller_gap_spreads_the_light() -> None:
    assert bl.ring_irradiance(0.0, height_mm=12.0) > bl.ring_irradiance(0.0, height_mm=6.0)


def test_main_prints_the_table(capsys: pytest.CaptureFixture[str]) -> None:
    bl.main()
    assert "0.165" in capsys.readouterr().out
