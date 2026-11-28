# SPDX-License-Identifier: Apache-2.0
"""Tests of the arc-end luminance model (ADR-0027, MECH-014 proposal)."""

import light_edge as le
import pytest

TABLE_ROWS = 3  # header, absorbing, mirror
PLATEAU_TOLERANCE = 1.05  # the far end of the probe range is within 5 % of the plateau


def test_point_source_is_one_on_axis_and_falls_with_distance():
    assert le.point_source(0.0, 8.0) == pytest.approx(1.0 / 64.0)
    assert le.point_source(5.0, 8.0) < le.point_source(0.0, 8.0)


def test_led_positions_start_half_a_pitch_from_the_wall():
    assert le.led_positions(4, 5.0) == [2.5, 7.5, 12.5, 17.5]


@pytest.mark.parametrize(("n", "pitch"), [(3, 5.0), (12, 0.0), (12, -1.0)])
def test_led_positions_reject_degenerate_arcs(n, pitch):
    with pytest.raises(ValueError, match="at least"):
        le.led_positions(n, pitch)


def test_absorbing_wall_gives_half_the_plateau_at_the_wall():
    assert le.edge_ratio(0.0, 12, 5.2, "absorbing") == pytest.approx(0.50, abs=0.02)


def test_absorbing_wall_table_of_adr_0027():
    assert le.edge_ratio(2.6, 12, 5.2, "absorbing") == pytest.approx(0.71, abs=0.02)
    assert le.edge_ratio(5.2, 12, 5.2, "absorbing") == pytest.approx(0.84, abs=0.02)
    assert le.distance_to_fraction(0.9, 12, 5.2, "absorbing") == pytest.approx(7.0, abs=0.3)


def test_absorbing_ratio_rises_from_the_wall_to_the_plateau():
    ratios = [le.edge_ratio(s, 12, 5.2, "absorbing") for s in (0.0, 1.0, 2.6, 5.2, 7.8, 10.4)]
    assert ratios == sorted(ratios)
    assert ratios[-1] < PLATEAU_TOLERANCE


def test_mirror_wall_is_flat_up_to_the_wall():
    for s in le.PROBES_MM:
        assert le.edge_ratio(s, 12, 5.2, "mirror") == pytest.approx(1.0, abs=0.03)
    assert le.distance_to_fraction(0.9, 12, 5.2, "mirror") == 0.0


def test_edge_ratio_at_the_wall_does_not_depend_on_pitch_or_count():
    for n, pitch in ((12, 4.0), (12, 6.6), (24, 5.2)):
        assert le.edge_ratio(0.0, n, pitch, "absorbing") == pytest.approx(0.50, abs=0.03)


def test_table_has_a_row_per_wall():
    rows = le.table()
    assert len(rows) == TABLE_ROWS
    assert rows[1].startswith("absorbing")
    assert rows[2].startswith("mirror")
