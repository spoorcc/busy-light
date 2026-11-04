# SPDX-License-Identifier: Apache-2.0
"""Tests for back_layout: the findings of RV-007 G1 are reproduced by the script."""

import back_layout as b


def test_as_written_puts_the_label_inside_the_recess() -> None:
    # MECH-006 wants the label outside the recess; centred, it lies inside (corner R 14.8 < 15.0).
    assert not b.v0_as_written().ok
    assert b.square_corner_radius(0.0, 0.0, b.LABEL) < b.RECESS_D / 2


def test_label_does_not_fit_beside_centred_recess() -> None:
    assert b.max_square_beside_circle(b.RECESS_D / 2) < b.LABEL
    assert not b.v1_label_beside_recess().ok


def test_annular_bayonet_fits_on_paper() -> None:
    check, geo = b.v2_annular_bayonet()
    assert check.ok
    assert geo["inner"] < geo["outer"]
    assert b.foot_clearance_v2(geo) >= b.CLEAR


def test_dovetail_rail_leaves_no_room_for_a_21_mm_label() -> None:
    assert not b.v4_dovetail_rail().ok


def test_offset_recess_fits_but_is_off_axis() -> None:
    check, geo = b.v5_offset_recess()
    assert check.ok
    assert geo["cx"] < 0  # the recess is off the axis, so the accessory load is off the axis
