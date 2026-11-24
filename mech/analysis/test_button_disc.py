# SPDX-License-Identifier: Apache-2.0
"""Tests for button_disc.py (plan 09; MECH-004, MECH-002)."""

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import button_disc as bd  # noqa: E402

TIGHT = 1e-9
LOOSE = 1e-6
MILLI = 0.001
SW_FORCE = 1.6  # N, the plan 09 section 3.2 matrix (TL3342, assumed 0.25 mm)
SW_TRAVEL = 0.25  # mm
R_USE = 13.0
FIVE_PCT = 0.05
STRESS_LOW = 50.0  # MPa
STRESS_HIGH = 56.0
M3_MIN_N = 1.427  # edge press of three TL3342 (1.6 N, 0.25 mm) at r = 11 mm
M3_TRAVEL_MM = 0.435
BAND_TOL = 0.03


def _points() -> list[tuple[float, float]]:
    return bd.sample_points(R_USE, 600, 48, 7, extra=[(0.0, 0.0)])


def test_equilibrium_residual_is_zero() -> None:
    sup = [(3.0, 1.0, 2.0), (-4.0, 5.0, 3.0), (1.0, -6.0, 1.5), (7.0, 7.0, 0.5)]
    load = (2.0, -3.0)
    f = 5.0
    a, b, c = bd.solve_plane(sup, load, f)
    fz = sum(k * (a + b * x + c * y) for x, y, k in sup)
    mx = sum(k * (a + b * x + c * y) * x for x, y, k in sup)
    my = sum(k * (a + b * x + c * y) * y for x, y, k in sup)
    assert abs(fz - f) < TIGHT
    assert abs(mx - f * load[0]) < TIGHT
    assert abs(my - f * load[1]) < TIGHT


def test_three_equal_supports_load_at_the_centroid() -> None:
    k = 2.0
    sup = bd.bridges(14.0, k)
    plane = bd.solve_plane(sup, (0.0, 0.0), 6.0)
    assert abs(bd.displacement(plane, (0.0, 0.0)) - 6.0 / (3 * k)) < TIGHT
    assert abs(plane[1]) < TIGHT
    assert abs(plane[2]) < TIGHT


def test_centroid_rule_gives_equal_plunger_travel_everywhere() -> None:
    ang = math.degrees(math.acos(0.2))
    arms = [
        (15.0 * math.cos(math.radians(a)), 15.0 * math.sin(math.radians(a)), 3.0)
        for a in (0.0, ang, -ang)
    ]
    centroid_x = sum(x for x, _, _ in arms) / 3
    assert abs(centroid_x - 7.0) < TIGHT
    sup = [*arms, (7.0, 0.0, 6.4)]
    pts = _points()
    travels = [bd.displacement(bd.solve_plane(sup, p, 1.0), (7.0, 0.0)) for p in pts]
    assert max(travels) - min(travels) < TIGHT


def test_s2_rows_are_position_independent_and_analytic() -> None:
    ks = SW_FORCE / SW_TRAVEL
    for k in (1.0, 2.0, 3.0, 4.0):
        m = bd.press_metrics(bd.bridges(14.0, k), [(0.0, 0.0, ks)], SW_TRAVEL, _points())
        expect = SW_TRAVEL * (3 * k + ks)
        assert abs(m.force_min_n - expect) < TIGHT
        assert abs(m.force_max_n - expect) < TIGHT
        assert m.lift_points == 0


def test_s2_matrix_rows_within_five_percent_of_the_plan() -> None:
    ks = SW_FORCE / SW_TRAVEL
    plan = {1.0: 1.60, 2.0: 1.14, 3.0: 0.99, 4.0: 0.91}
    for k, travel in plan.items():
        m = bd.press_metrics(bd.bridges(14.0, k), [(0.0, 0.0, ks)], SW_TRAVEL, _points())
        assert abs(m.travel_max_mm - travel) < FIVE_PCT * travel


def test_s1_centroid_row_within_five_percent_of_the_plan() -> None:
    ang = math.degrees(math.acos(0.2))
    arms = [
        (15.0 * math.cos(math.radians(a)), 15.0 * math.sin(math.radians(a)), 3.0)
        for a in (0.0, ang, -ang)
    ]
    pts = bd.sample_points(R_USE, 600, 48, 7, extra=[(0.0, 0.0), (7.0, 0.0)])
    m = bd.press_metrics(arms, [(7.0, 0.0, SW_FORCE / SW_TRAVEL)], SW_TRAVEL, pts)
    assert abs(m.force_min_n - 3.85) < FIVE_PCT * 3.85
    assert abs(m.travel_max_mm - 5.6) < FIVE_PCT * 5.6


def test_m3_maximum_is_the_analytic_centre_value() -> None:
    ks = SW_FORCE / SW_TRAVEL
    sws = [
        (11.0 * math.cos(math.radians(a)), 11.0 * math.sin(math.radians(a)), ks)
        for a in bd.BRIDGE_ANGLES_DEG
    ]
    m = bd.press_metrics([], sws, SW_TRAVEL, _points())
    assert abs(m.force_max_n - 3 * ks * SW_TRAVEL) < TIGHT
    assert abs(m.force_max_n - 4.80) < LOOSE
    assert m.force_min_n < m.force_max_n


def test_a_singular_support_set_raises() -> None:
    with pytest.raises(ValueError, match="singular"):
        bd.solve_plane([(0.0, 0.0, 1.0), (1.0, 0.0, 1.0), (2.0, 0.0, 1.0)], (0.0, 0.0), 1.0)


def test_a_press_on_the_far_side_lifts_the_plunger() -> None:
    # supports on the left, switch on the right: a far left load lifts the plunger
    sup = [(-10.0, 0.0, 1.0), (0.0, 10.0, 1.0), (0.0, -10.0, 1.0)]
    sw = [(10.0, 0.0, 1.0)]
    lifted = bd.press_metrics(sup, sw, 0.2, [(-14.0, 0.0)])
    assert lifted.lift_points == 1
    assert lifted.force_min_n == math.inf
    assert lifted.travel_max_mm == 0.0
    mixed = bd.press_metrics(sup, sw, 0.2, [(-14.0, 0.0), (0.0, 0.0)])
    assert mixed.lift_points == 1
    assert abs(mixed.force_min_n - 0.8) < TIGHT  # the lift point is left out of the force range
    assert abs(mixed.force_max_n - 0.8) < TIGHT


def test_bridge_band_refuses_a_band_with_lift_points(monkeypatch: pytest.MonkeyPatch) -> None:
    real = bd.press_metrics

    def lifting(*args: object, **kwargs: object) -> bd.PressMetrics:
        m = real(*args, **kwargs)  # type: ignore[arg-type]
        return bd.PressMetrics(m.force_min_n, m.force_max_n, m.travel_max_mm, 1)

    monkeypatch.setattr(bd, "press_metrics", lifting)
    with pytest.raises(ValueError, match="lifts"):
        bd.bridge_band(1.5, 0.49, 0.15, bd.WINDOW_N, bd.TRAVEL_LIMIT_MM, _points())


def test_sample_points_is_deterministic_and_holds_the_extra_points() -> None:
    a = bd.sample_points(R_USE, 10, 8, 3, extra=[(1.0, 2.0), (0.0, 0.0)])
    b = bd.sample_points(R_USE, 10, 8, 3, extra=[(1.0, 2.0), (0.0, 0.0)])
    assert a == b
    assert len(a) == 10 + 2 + 8
    assert a[10] == (1.0, 2.0)
    assert a[11] == (0.0, 0.0)
    assert a[12] == (R_USE, 0.0)
    assert all(math.hypot(*p) <= R_USE + TIGHT for p in a)


def test_beam_plate_and_helpers_have_analytic_values() -> None:
    assert abs(bd.guided_beam_stiffness(1500.0, 1.2, 1.2, 25.0) - 0.199) < MILLI
    ss = bd.plate_deflection(15.0, 1.2, 1500.0, 0.4, 1.0, "simply_supported")
    cl = bd.plate_deflection(15.0, 1.2, 1500.0, 0.4, 1.0, "clamped")
    assert abs(ss - 0.042) < MILLI
    d = 1500.0 * 1.2**3 / (12 * (1 - 0.4**2))
    assert abs(cl - 15.0**2 / (16 * math.pi * d)) < TIGHT
    assert cl < ss
    assert abs(bd.arm_stress(1500.0, 1.2, 10.0, 1.0) - 3 * 1500.0 * 1.2 / 100.0) < TIGHT
    assert abs(bd.guide_jam_length(13.0, 0.3) - 7.8) < TIGHT


def test_arm_stress_agrees_with_the_beam_force_formula() -> None:
    e, w, thick, length, stroke = 1500.0, 1.2, 1.2, 10.1, 1.0
    force = bd.guided_beam_stiffness(e, w, thick, length) * stroke
    assert (
        abs(bd.arm_stress(e, thick, length, stroke) - 3 * force * length / (w * thick**2)) < LOOSE
    )
    assert STRESS_LOW < bd.arm_stress(e, thick, length, stroke) < STRESS_HIGH  # the 3 N/mm arm


def test_random_points_are_uniform_in_area() -> None:
    pts = bd.sample_points(R_USE, 600, 0, 7)
    mean_r2 = sum(x * x + y * y for x, y in pts) / len(pts)
    assert abs(mean_r2 - R_USE**2 / 2) < FIVE_PCT * R_USE**2 / 2


def test_s2_click_force_and_extremes() -> None:
    assert abs(bd.s2_click_force(1.6, 3.0, 3, 0.25) - 3.85) < TIGHT
    assert abs(bd.s2_click_force(1.5, 2.0, 3, 0.15) - 2.40) < TIGHT
    lo, hi = bd.click_force_extremes(1.5, 0.49, 0.05, 0.35, 3.0, 3)
    assert abs(lo - 1.46) < TIGHT
    assert abs(hi - 5.14) < TIGHT


def test_no_stiffness_holds_the_window_over_the_b3u_pre_travel_tolerance() -> None:
    lo, hi = bd.tolerance_band(1.50, 0.49, 0.05, 0.35, bd.WINDOW_N)
    assert abs(lo - 6.60) < MILLI * 10
    assert abs(hi - 2.87) < MILLI * 10
    assert lo > hi
    lo2, hi2 = bd.tolerance_band(1.50, 0.49, 0.05, 0.25, bd.WINDOW_N)
    assert abs(hi2 - 4.013) < MILLI * 10
    assert lo2 > hi2
    # a tight click travel (no tolerance) gives a band again
    lo3, hi3 = bd.tolerance_band(1.50, 0.49, 0.15, 0.15, bd.WINDOW_N)
    assert lo3 < hi3


def test_bridge_band_for_the_tl3342_and_the_b3u() -> None:
    pts = _points()
    tl = bd.bridge_band(1.57, 0.49, 0.25, bd.WINDOW_N, bd.TRAVEL_LIMIT_MM, pts)
    b3u = bd.bridge_band(1.50, 0.49, 0.15, bd.WINDOW_N, bd.TRAVEL_LIMIT_MM, pts)
    assert abs(tl[0] - 2.83) < BAND_TOL * 2.83
    assert abs(tl[1] - 3.92) < BAND_TOL * 3.92
    assert abs(b3u[0] - 2.20) < BAND_TOL * 2.20
    assert abs(b3u[1] - 6.69) < BAND_TOL * 6.69
    assert b3u[1] / b3u[0] > tl[1] / tl[0]


def test_bridge_band_raises_when_no_band_exists() -> None:
    pts = _points()
    with pytest.raises(ValueError, match="travel limit"):
        bd.bridge_band(2.0, 0.5, 0.35, bd.WINDOW_N, bd.TRAVEL_LIMIT_MM, pts)
    with pytest.raises(ValueError, match="no stiffness"):
        bd.bridge_band(1.5, 0.49, 0.15, (2.0, 2.2), bd.TRAVEL_LIMIT_MM, pts)


def test_main_prints_the_bands(capsys: pytest.CaptureFixture[str]) -> None:
    bd.main()
    out = capsys.readouterr().out
    assert "band: k from 2.20 to 6.69" in out
    assert "no band" in out
    assert "M3: three B3U-1000P" in out
    assert "S1 (switch 7 mm off the centre" in out
    assert "plate in series" in out
