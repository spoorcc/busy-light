# SPDX-License-Identifier: Apache-2.0
"""Tests for button_light.py (plan 09 section 4.4; MECH-002)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import button_light as bl  # noqa: E402

CENTRE_LOW = 0.17
CENTRE_HIGH = 0.20
RING_R = 20.0
TIGHT = 1e-12


def test_centre_gets_about_a_fifth_of_the_value_above_an_led() -> None:
    assert CENTRE_LOW < bl.ring_irradiance(0.0) < CENTRE_HIGH


def test_reference_point_is_one() -> None:
    assert abs(bl.ring_irradiance(RING_R, azimuth_deg=0.0) - 1.0) < TIGHT


def test_irradiance_grows_towards_the_ring() -> None:
    vals = [bl.ring_irradiance(r) for r in (0.0, 5.0, 10.0, 13.0, 16.0, 20.0)]
    assert vals == sorted(vals)


def test_the_centre_value_does_not_depend_on_the_azimuth() -> None:
    assert abs(bl.ring_irradiance(0.0, azimuth_deg=10.0) - bl.ring_irradiance(0.0)) < TIGHT


def test_main_prints_the_table(capsys: pytest.CaptureFixture[str]) -> None:
    bl.main()
    assert "0.182" in capsys.readouterr().out
