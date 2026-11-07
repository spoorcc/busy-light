# SPDX-License-Identifier: Apache-2.0
"""Accessory ring blank and lock-action check for the annular bayonet.

Traces to MECH-007, MECH-008 and ADR-0014.

Builds the ring with three T-lugs and checks, on the base back face of the housing model:
  1. entry position: ring pushes in and out without touching the base;
  2. after the turn of BAY_TURN_DEG the ring cannot be pulled off (the lugs hit the lips);
  3. the turned ring does not touch the base (it can move);
  4. at half the turn the lugs are partly under the lips (reported, not asserted);
  5. the stop ends the turn.
NOT modelled: detent, release tab, retention force (MECH-008 value [X] N is still open).
Output goes to the build folder (not committed).
"""

import os
import sys

import FreeCAD as App
import Part

sys.path.insert(0, "mech/analysis")
sys.path.insert(0, "mech/freecad")
import bayonet_geometry as bg  # noqa: E402
import housing_params as p  # noqa: E402

BUILD = os.environ.get("MECH_BUILD_DIR", "build/mech")
os.makedirs(BUILD, exist_ok=True)
EPS_MM3 = 1e-6
PULL_MM = 0.5


def overlap(a, b):
    return a.common(b).Volume


def main():
    base = Part.makeCylinder(p.D_OUT / 2.0, p.FLOOR).cut(bg.groove_cut())
    acc = bg.accessory_ring()
    assert acc.isValid()
    assert len(acc.Solids) == 1, f"accessory: {len(acc.Solids)} solids, expected 1"
    # 1. entry position: no contact, and the ring can be pushed to the face and pulled back
    assert overlap(base, acc) < EPS_MM3, "entry position: ring touches the base"
    assert overlap(base, bg.turned(acc, 0.0, -PULL_MM)) < EPS_MM3, (
        "entry position: pull-off blocked"
    )
    print("accessory: entry position free, ring moves in and out")
    # 3. locked position: free to move, no contact
    locked = bg.turned(acc, p.BAY_TURN_DEG)
    assert overlap(base, locked) < EPS_MM3, "locked position: ring touches the base"
    # 2. locked position: pull-off is blocked by the lips
    blocked = overlap(base, bg.turned(locked, 0.0, -PULL_MM))
    assert blocked > EPS_MM3, "locked position: the lips do not hold the lugs"
    print(
        f"accessory: locked after {p.BAY_TURN_DEG:.0f} deg, "
        f"pull-off blocked (overlap {blocked:.2f} mm3)"
    )
    # 4. half turn: the lugs are still under the lips, no pull-off
    half = bg.turned(acc, p.BAY_TURN_DEG / 2)
    held_half = overlap(base, bg.turned(half, 0.0, -PULL_MM)) > EPS_MM3
    # 5. the stop: lug end is at 25 deg + turn, the lock sector ends at entry + LOCK_DEG = 80 deg
    lug_end = 0.5 * (p.BAY_ENTRY_DEG + p.BAY_LUG_ARC_DEG)
    over = bg.turned(acc, p.BAY_ENTRY_DEG + bg.LOCK_DEG - lug_end + 5.0)
    assert overlap(base, over) > EPS_MM3, "no stop: the ring turns past the lock sector"
    print("accessory: the stop ends the turn")
    print(f"accessory: at half the turn pull-off is {'blocked' if held_half else 'free'}")
    doc = App.newDocument("busy_light_accessory")
    obj = doc.addObject("Part::Feature", "accessory_ring")
    obj.Shape = acc
    acc.exportStep(os.path.join(BUILD, "coupon_accessory_ring.step"))
    doc.recompute()
    doc.saveAs(os.path.join(BUILD, "busy_light_accessory.FCStd"))
    print("accessory: OK, written to", BUILD)


main()
