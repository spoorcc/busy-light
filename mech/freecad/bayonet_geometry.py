# SPDX-License-Identifier: Apache-2.0
"""Shared bayonet geometry: groove with lock lips in the base, lugs on the accessory.

Traces to MECH-007 and ADR-0014.

Library for housing.py, coupons.py and accessory.py (run alone it does nothing).
Per 120 degrees of the base: entry sector (groove fully open), lock sector (groove
narrowed by a lip at the back face), then a solid stop.
The accessory lug enters at the entry sector and turns BAY_TURN_DEG into the lock sector,
where the head sits behind the lip.
Angles are measured from +X, counter-clockwise. Sector k starts at 90 + 120 k degrees.
"""

import sys

import FreeCAD as App
import Part

sys.path.insert(0, "mech/analysis")
import housing_params as p  # noqa: E402

V = App.Vector
LOCK_DEG = p.BAY_LUG_ARC_DEG + p.BAY_TURN_DEG


def sector(r_out, r_in, dims, start_deg, span_deg):
    """Annular sector r_in..r_out; dims = (height, z); from start_deg over span_deg."""
    h, z = dims
    outer = Part.makeCylinder(r_out, h, V(0, 0, z), V(0, 0, 1), span_deg)
    if r_in > 0:
        outer = outer.cut(Part.makeCylinder(r_in, h, V(0, 0, z)))
    outer.rotate(V(0, 0, 0), V(0, 0, 1), start_deg)
    return outer


def start_of(k):
    return 90.0 + 120.0 * k


def groove_cut():
    """Solid to remove from the base: the groove minus the lock lips."""
    groove = sector(p.BAY_R_OUT, p.BAY_R_IN, (p.BAY_DEPTH, 0.0), 0.0, 360.0)
    for k in range(p.BAY_LUGS):
        a0 = start_of(k) + p.BAY_ENTRY_DEG
        for r_a, r_b in (
            (p.BAY_R_IN + p.BAY_LIP_W, p.BAY_R_IN),
            (p.BAY_R_OUT, p.BAY_R_OUT - p.BAY_LIP_W),
        ):
            groove = groove.cut(sector(r_a, r_b, (p.BAY_LIP_T, 0.0), a0, LOCK_DEG))
        # stop: the rest up to the next entry sector is solid, so the ring cannot turn on
        a_stop = a0 + LOCK_DEG
        groove = groove.cut(
            sector(
                p.BAY_R_OUT,
                p.BAY_R_IN,
                (p.BAY_DEPTH, 0.0),
                a_stop,
                120.0 - p.BAY_ENTRY_DEG - LOCK_DEG,
            )
        )
        # detent ridge: material left in the groove below the ceiling, the lug head has to pass it
        ridge = sector(
            p.BAY_R_OUT,
            p.BAY_R_IN,
            (p.DETENT_H, p.BAY_DEPTH - p.DETENT_H),
            start_of(k) + p.DETENT_START_DEG,
            p.DETENT_SPAN_DEG,
        )
        groove = groove.cut(ridge)
    return groove


def accessory_ring(r_inner=14.0, r_outer=None, thick=3.0):
    """Ring-shaped accessory blank: body under the back face (z -thick..0), three T-lugs above z 0.
    Placed in the entry position (lugs in the entry sectors)."""
    r_outer = r_outer if r_outer is not None else p.D_OUT / 2.0
    body = sector(r_outer, r_inner, (thick, -thick), 0.0, 360.0)
    r_in_n = p.BAY_R_IN + p.BAY_LIP_W + p.BAY_CLEAR
    r_out_n = p.BAY_R_OUT - p.BAY_LIP_W - p.BAY_CLEAR
    r_in_h = p.BAY_R_IN + p.BAY_CLEAR
    r_out_h = p.BAY_R_OUT - p.BAY_CLEAR
    z_head = p.BAY_LIP_T + p.BAY_CLEAR_Z
    h_head = p.BAY_DEPTH - p.BAY_CLEAR_Z - z_head
    for k in range(p.BAY_LUGS):
        a0 = start_of(k) + 0.5 * (p.BAY_ENTRY_DEG - p.BAY_LUG_ARC_DEG)
        body = body.fuse(sector(r_out_n, r_in_n, (z_head + 0.01, 0.0), a0, p.BAY_LUG_ARC_DEG))
        body = body.fuse(sector(r_out_h, r_in_h, (h_head, z_head), a0, p.BAY_LUG_ARC_DEG))
    return body.removeSplitter()


def turned(shape, deg, dz=0.0):
    s = shape.copy()
    s.rotate(V(0, 0, 0), V(0, 0, 1), deg)
    s.translate(V(0, 0, dz))
    return s
