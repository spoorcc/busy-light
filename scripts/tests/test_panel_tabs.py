# SPDX-License-Identifier: Apache-2.0
"""Tests of the panel tab geometry and checks (scripts/panel_tabs.py; plan 08 section 4.5)."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
from types import ModuleType

import panel_tabs as pt
import pytest

ROOT = Path(__file__).resolve().parents[2]
CENTRE = (40.0, 40.0, 23.0)  # the spike outline: R 23 around (40, 40) in KiCad mm
BBOX_Y = (17.0, 63.0)


def load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_circle_from_three_points() -> None:
    cx, cy, r = pt.circle_from_points((63.0, 40.0), (40.0, 17.0), (17.0, 40.0))
    assert (cx, cy, r) == pytest.approx((40.0, 40.0, 23.0))
    with pytest.raises(ValueError, match="one line"):
        pt.circle_from_points((0.0, 0.0), (1.0, 1.0), (2.0, 2.0))


def test_board_circle_takes_the_largest_concentric_arcs() -> None:
    big1 = ((63.0, 40.0), (40.0, 17.0), (17.0, 40.0))
    big2 = ((17.0, 40.0), (40.0, 63.0), (63.0, 40.0))
    notch = ((38.5, 17.05), (40.0, 18.5), (41.5, 17.05))
    assert pt.board_circle([notch, big1, big2]) == pytest.approx(CENTRE)
    shifted = ((64.0, 40.0), (41.0, 17.0), (18.0, 40.0))
    with pytest.raises(ValueError, match="centre"):
        pt.board_circle([big1, shifted])
    with pytest.raises(ValueError, match="no Edge.Cuts arc"):
        pt.board_circle([])


def test_upper_tab_goes_to_the_top_rail() -> None:
    t = pt.make_tab(CENTRE, 45.0, 3.0, BBOX_Y)
    assert (t.rail, t.orientation) == ("top", -90.0)
    # KiKit direction (cos o, -sin o) points down, into the board
    o = math.radians(t.orientation)
    assert (math.cos(o), -math.sin(o)) == pytest.approx((0.0, 1.0))
    assert t.origin == pytest.approx((40.0 + 23.0 * math.cos(math.radians(45.0)), 16.5))
    cx, cy, r = CENTRE
    assert all(math.hypot(x - cx, y - cy) == pytest.approx(r) and y < cy for x, y in t.cut)
    assert t.cut[-1][0] - t.cut[0][0] == pytest.approx(3.0)


def test_lower_tab_goes_to_the_bottom_rail() -> None:
    t = pt.make_tab(CENTRE, 215.0, 3.0, BBOX_Y)
    assert (t.rail, t.orientation) == ("bottom", 90.0)
    assert t.origin[1] == pytest.approx(63.5)
    assert all(y > CENTRE[1] for _, y in t.cut)


def test_steep_edge_is_refused() -> None:
    for az in (0.0, 10.0, 175.0, 350.0):
        with pytest.raises(ValueError, match="too steep"):
            pt.make_tab(CENTRE, az, 3.0, BBOX_Y)


def test_edge_gap_along_the_circle() -> None:
    # 15 deg on R 23 is 6.02 mm; less half the tab (1.5) and half the hook (2.0)
    gap = pt.edge_gap(45.0, 3.0, 23.0, ("hook", 30.0, 2.0))
    assert gap == pytest.approx(23.0 * math.radians(15.0) - 3.5)
    assert pt.edge_gap(355.0, 3.0, 23.0, ("x", 5.0, 0.0)) == pytest.approx(
        23.0 * math.radians(10.0) - 1.5
    )


def test_default_azimuths_clear_every_edge_feature() -> None:
    tabs = [pt.make_tab(CENTRE, az, 3.0, BBOX_Y) for az in pt.DEFAULT_AZIMUTHS]
    report, fails = pt.check_tabs(tabs, 23.0, {}, 3.0)
    assert fails == []
    assert all(e["nearest_edge_feature"]["gap_mm"] >= pt.EDGE_CLEARANCE_MM for e in report)


def test_tab_at_a_housing_hook_or_the_button_fails() -> None:
    for az, name in (
        (60.0, "hook/post 60 (housing.py)"),
        (240.0, "button 240"),
        (30.0, "hook/post 30"),
    ):
        _, fails = pt.check_tabs([pt.make_tab(CENTRE, az, 3.0, BBOX_Y)], 23.0, {}, 3.0)
        assert any(name in f for f in fails), (az, fails)


def test_capacitor_near_the_tab_cut_fails() -> None:
    # at 90 deg the cut is the top of the circle: a pad right below its middle has a known distance
    t = pt.make_tab(CENTRE, 90.0, 3.0, BBOX_Y)
    x, y = t.cut[len(t.cut) // 2]
    near = {"C10": [(x - 0.4, y + 1.0, x + 0.4, y + 1.8)]}  # pad 1.0 mm inside the edge
    far = {"C11": [(x - 0.4, y + 5.0, x + 0.4, y + 5.8)]}
    _, fails = pt.check_tabs([t], 23.0, near | far, 3.0)
    assert [f for f in fails if "capacitor" in f] == [
        "tab 90 deg: capacitor C10 at 1.00 mm (< 3.0 mm)"
    ]
    report, fails = pt.check_tabs([t], 23.0, far, 3.0)
    assert [f for f in fails if "capacitor" in f] == []
    assert report[0]["nearest_capacitors"] == [{"ref": "C11", "mm": 5.0}]


def test_box_distance() -> None:
    assert pt.box_distance(0.0, 0.0, (1.0, 1.0, 2.0, 2.0)) == pytest.approx(math.sqrt(2.0))
    assert pt.box_distance(1.5, 1.5, (1.0, 1.0, 2.0, 2.0)) == 0.0


def test_edge_features_match_the_housing_models() -> None:
    """The keep-outs come from both housing models (plan 08 R11): mech_outline.py of the spike and
    mech/freecad/housing.py with housing_params.py. A change there must be reflected here."""
    mo = load("mech_outline", ROOT / "hw" / "kicad" / "spike-gate" / "src" / "mech_outline.py")
    hp = load("housing_params", ROOT / "mech" / "analysis" / "housing_params.py")
    feats = {(az, hw) for _, az, hw in pt.EDGE_FEATURES}
    r = mo.R_PCB
    j1 = {name: (az, hw) for name, az, hw in pt.EDGE_FEATURES}["J1 tab"]
    assert j1[0] == 0.0
    assert j1[1] == pytest.approx(r * math.asin(mo.m("V1_TAB_W") / 2 / r), abs=0.1)
    assert (mo.m("NOTCH_AZ"), mo.m("NOTCH_R")) in feats
    assert {(az, mo.m("POST_TANG") / 2) for az in mo.m("POST_AZ")} <= feats
    assert (mo.m("BTN_AZ"), hp.BTN_D / 2) in feats
    assert mo.m("BTN_AZ") == hp.BTN_DEG
    assert {(az, hp.HOOK_W / 2) for az in hp.POST_DEG} <= feats
    assert hp.POST_PAD_W == hp.HOOK_W
    housing = (ROOT / "mech" / "freecad" / "housing.py").read_text(encoding="utf-8")
    assert "az = 120.0 * k + 60.0" in housing  # the snap hooks at 60, 180 and 300 deg
    assert hp.HOOK_COUNT == 3  # noqa: PLR2004
