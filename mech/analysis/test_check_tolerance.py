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
