# SPDX-License-Identifier: Apache-2.0
"""Print coupons (test pieces) for the diffuser and the bayonet floor.

Traces to MECH-002 (diffuser coupons: lid thickness 0.8 / 1.2 / 1.6 mm over a ring of 16 LEDs at
4 / 6 / 8 mm) and MECH-007 (bayonet floor skin, ADR-0014 coupon gate). Dimensions from
mech/analysis/housing_params.py. Output goes to the build folder (not committed).

Diffuser set: 3 plates (one per thickness) and 3 spacer rings (one per LED distance). A plate on a
spacer ring on the LED board gives 9 combinations, so 6 prints cover the whole matrix.
Bayonet set: one disc with the annular groove, the lock lips and the 0.8 mm floor skin of the
housing, and the mating accessory ring from accessory.py (print both to test the lock action).
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

V = App.Vector
R_OUT = p.D_OUT / 2.0
R_IN = R_OUT - p.WALL
PLATE_T = (0.8, 1.2, 1.6)
SPACER_H = (4.0, 6.0, 8.0)
EPS_MM3 = 1e-6
SKIN_TOL = 1e-4


def cyl(r, h, z=0.0):
    return Part.makeCylinder(r, h, V(0, 0, z))


def plate(t):
    return cyl(R_OUT, t)


def spacer(h):
    return cyl(R_OUT, h).cut(cyl(R_IN, h))


def bayonet_disc():
    return cyl(R_OUT, p.FLOOR).cut(bg.groove_cut())


def main():
    doc = App.newDocument("busy_light_coupons")
    parts = {f"diffuser_plate_{t:.1f}mm": plate(t) for t in PLATE_T}
    parts.update({f"diffuser_spacer_{h:.0f}mm": spacer(h) for h in SPACER_H})
    parts["bayonet_floor_disc"] = bayonet_disc()
    for name, shape in parts.items():
        assert shape.isValid(), f"{name}: invalid shape"
        assert len(shape.Solids) == 1, f"{name}: {len(shape.Solids)} solids, expected 1"
        assert shape.Volume > EPS_MM3, f"{name}: no volume"
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        shape.exportStep(os.path.join(BUILD, f"coupon_{name}.step"))
        print(
            f"coupons: {name} volume {shape.Volume:.0f} mm3, height {shape.BoundBox.ZLength:.2f} mm"
        )
    skin = p.FLOOR - p.BAY_DEPTH
    bb = parts["bayonet_floor_disc"]
    # probe the material left under the groove in an entry sector, at the ring mid radius
    mid = (p.BAY_R_IN + p.BAY_R_OUT) / 2.0
    probe = Part.makeBox(0.2, 0.2, p.FLOOR, V(mid, 5.0, 0.0))
    left = probe.common(bb)
    assert abs(left.Volume - 0.2 * 0.2 * (p.FLOOR - p.BAY_DEPTH)) < 1e-6 * 100, (
        "floor skin differs from the parameters"
    )
    print(f"coupons: bayonet floor skin {skin:.2f} mm confirmed in the model")
    doc.recompute()
    doc.saveAs(os.path.join(BUILD, "busy_light_coupons.FCStd"))
    print("coupons: OK, written to", BUILD)


main()
