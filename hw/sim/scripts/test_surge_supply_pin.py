"""Tests for surge_supply_pin.py (HW-010 proposed amendment). Skipped when ngspice is missing."""

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import surge_supply_pin as s  # noqa: E402

pytestmark = pytest.mark.skipif(shutil.which("ngspice") is None, reason="ngspice not installed")
LIMIT = s.V_ABS_MAX - s.MARGIN
MAX_R_POWER_W = 0.05  # half of a 100 mW 0603 resistor
MAX_Z_POWER_W = 0.15  # half of a 300 mW zener class
WORST_C = 50e-9


@pytest.mark.parametrize("part,r", [("TMUX1101", 1000.0), ("TUSB321", 470.0)])
def test_chosen_values_stay_below_limit_in_both_surges(part, r):
    for shape in s.SURGES.values():
        assert s.run_case(r, WORST_C, s.LOADS[part], shape) <= LIMIT


def test_220_ohm_fails_s1_at_worst_case_capacitor():
    assert s.run_case(220.0, WORST_C, s.LOADS["TUSB321"], s.SURGES["S1 8/20us 15V"]) > LIMIT


def test_dc_drop_of_chosen_values():
    assert s.dc_drop(470.0, s.LOADS["TUSB321"]) == pytest.approx(0.047)
    assert s.dc_drop(1000.0, s.LOADS["TMUX1101"]) == pytest.approx(0.001)


def test_sustained_9v_power_within_half_rating():
    for r in (470.0, 1000.0):
        _, p_r, p_z = s.dc_s3(r)
        assert p_r <= MAX_R_POWER_W
        assert p_z <= MAX_Z_POWER_W
