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


@pytest.mark.parametrize("part,r", [("TMUX1101", 1000.0), ("TUSB321", 470.0)])
@pytest.mark.parametrize("bv", s.VZ_CORNERS)
def test_chosen_values_hold_at_every_zener_voltage_corner(part, r, bv):
    for shape in s.SURGES.values():
        assert s.run_case(r, WORST_C, s.LOADS[part], shape, bv=bv) <= LIMIT


def test_dc_drop_of_chosen_values():
    assert s.dc_drop(470.0, s.LOADS["TUSB321"]) == pytest.approx(0.047)
    assert s.dc_drop(1000.0, s.LOADS["TMUX1101"]) == pytest.approx(0.001)


def test_sustained_9v_power_within_half_rating():
    for r in (470.0, 1000.0):
        _, p_r, p_z = s.dc_s3(r)
        assert p_r <= MAX_R_POWER_W
        assert p_z <= MAX_Z_POWER_W


# Plan 08 option T2 (NOT applied: it changes Approved HW-010 text, so it is the owner's call; RV-014): U14 and U15 would
# share one 1 kohm resistor and one zener (net VDD_SW);
# each supply pin keeps its own 100 nF. Conservative model: the node carries both loads and only ONE worst-case capacitor
# (as if the second were far away); the real node has two.
TMUX_VDD_MIN_V = 1.08  # TMUX1101 SCDS410D recommended supply minimum (quoted in the script docstring)
VBUS_MIN_V = 4.5


@pytest.mark.parametrize("bv", s.VZ_CORNERS)
def test_shared_tmux_supply_stays_below_limit(bv):
    two_loads = 2 * s.LOADS["TMUX1101"]
    for shape in s.SURGES.values():
        assert s.run_case(1000.0, WORST_C, two_loads, shape, bv=bv) <= LIMIT


def test_shared_tmux_supply_dc_drop_and_minimum_supply():
    drop = s.dc_drop(1000.0, 2 * s.LOADS["TMUX1101"])
    assert drop == pytest.approx(0.002)
    assert VBUS_MIN_V - drop >= TMUX_VDD_MIN_V


def test_shared_tmux_supply_sustained_power_unchanged():
    # one resistor and one zener carry the same S3 current as each did before (the load current is negligible)
    _, p_r, p_z = s.dc_s3(1000.0)
    assert p_r <= MAX_R_POWER_W
    assert p_z <= MAX_Z_POWER_W
