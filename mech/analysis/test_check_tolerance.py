# SPDX-License-Identifier: Apache-2.0
"""Tests for check_tolerance.py (MECH-004, MECH-007, MECH-009)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_tolerance as ct  # noqa: E402
import housing_params as p  # noqa: E402

EXPECTED_WC_GAP = 1.38
EPS = 0.01


def test_working_geometry_passes() -> None:
    _, fail = ct.run()
    assert fail == []


def test_pcb_gap_matches_concept_report() -> None:
    assert abs(ct.pcb_gap()["wc"] - EXPECTED_WC_GAP) < EPS


def test_small_window_fails(monkeypatch) -> None:
    monkeypatch.setattr(p, "WIN_W", 13.2)
    monkeypatch.setattr(p, "WIN_H", 7.3)
    _, fail = ct.run()
    assert any("USB-C" in f for f in fail)


def test_thin_floor_skin_fails(monkeypatch) -> None:
    monkeypatch.setattr(p, "BAY_DEPTH", 1.5)
    _, fail = ct.run()
    assert any("skin" in f for f in fail)


def test_label_outside_ring_fails(monkeypatch) -> None:
    monkeypatch.setattr(p, "LABEL_CIRCLE_D", 36.0)
    _, fail = ct.run()
    assert any("label" in f for f in fail)


def test_big_board_binds(monkeypatch) -> None:
    monkeypatch.setattr(p, "D_PCB", 49.0)
    _, fail = ct.run()
    assert any("PCB binds" in f for f in fail)


def test_window_has_reserve_at_worst_case() -> None:
    u = ct.usb_window()
    assert u["slack"] - u["need_wc"] >= 0.1 - 1e-9


def test_spigot_binds_when_clearance_small(monkeypatch) -> None:
    monkeypatch.setattr(p, "SPIGOT_CLEAR", 0.25)
    _, fail = ct.run()
    assert any("spigot" in f for f in fail)


def test_thin_skirt_fails(monkeypatch) -> None:
    monkeypatch.setattr(p, "SKIRT_T", 0.6)
    _, fail = ct.run()
    assert any("skirt" in f for f in fail)


def test_steep_ledge_fails(monkeypatch) -> None:
    monkeypatch.setattr(p, "LEDGE_Z", 13.6)
    _, fail = ct.run()
    assert any("ledge" in f for f in fail)


# Centre button chains (plan 09 section 3.4, informational)
BUTTON_VERTICAL_WC = 1.41
BUTTON_VERTICAL_RSS = 0.6017
BUTTON_LATERAL_WC = 3.05
BUTTON_LATERAL_RSS = 2.0402
NOMINAL_RECESS = 0.30
RECESS_WC = 0.10


def test_button_vertical_chain_matches_hand_values() -> None:
    chain = ct.button_vertical_chain(ct.BUTTON_VERTICAL)
    assert abs(chain["wc"] - BUTTON_VERTICAL_WC) < EPS / 10
    assert abs(chain["rss"] - BUTTON_VERTICAL_RSS) < EPS / 10


def test_button_lateral_chain_matches_hand_values() -> None:
    chain = ct.button_lateral_chain(ct.BUTTON_LATERAL)
    assert abs(chain["wc"] - BUTTON_LATERAL_WC) < EPS / 10
    assert abs(chain["rss"] - BUTTON_LATERAL_RSS) < EPS / 10


def test_nominal_lateral_gap_value_is_the_housing_value() -> None:
    assert abs(ct.BUTTON_LATERAL["pcb_wall_gap"] - ct.pcb_gap()["nominal"]) < EPS / 10
    assert abs(ct.BUTTON_LATERAL["spigot_play"] - ct.spigot()["play_max"]) < EPS / 10


def test_button_values_are_tied_to_the_housing_tolerances() -> None:
    v = ct.BUTTON_VERTICAL
    assert abs(v["pcb_post"] - (p.TOL_FDM_FINE + p.TOL_PCB_T)) < EPS / 10
    assert v["lid_ledge"] == p.TOL_FDM
    assert v["lid_plate"] == p.TOL_FDM_FINE
    assert v["disc_plunger"] == p.TOL_FDM_FINE
    assert ct.BUTTON_LATERAL["plunger_tip"] == p.TOL_PLACE


def test_recess_ignores_the_ledge_that_moves_disc_and_band_together() -> None:
    tol = dict(ct.BUTTON_VERTICAL)
    base = ct.recess_worst_case(NOMINAL_RECESS, tol)
    tol["lid_ledge"] = 5.0
    assert ct.recess_worst_case(NOMINAL_RECESS, tol) == base


def test_recess_worst_case_keeps_the_nominal_step_minus_the_plate_term() -> None:
    assert abs(ct.recess_worst_case(NOMINAL_RECESS, ct.BUTTON_VERTICAL) - RECESS_WC) < EPS / 10


def test_button_chains_need_every_key() -> None:
    partial = {k: v for k, v in ct.BUTTON_VERTICAL.items() if k != "switch_height"}
    try:
        ct.button_vertical_chain(partial)
    except KeyError as exc:
        assert "switch_height" in str(exc)
    else:
        raise AssertionError("a missing key must raise KeyError")


def test_button_chains_are_not_part_of_run() -> None:
    out, fail = ct.run()
    assert fail == []
    assert not any("button" in line.lower() for line in out)
