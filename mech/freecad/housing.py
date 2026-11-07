# SPDX-License-Identifier: Apache-2.0
"""Housing generator, concept B (opaque base + translucent lid), prototype geometry.

Run headless: scripts/ci_mech.sh (it pipes exec(open(this file).read()) into freecad -c).
Traces to MECH-001, MECH-004, MECH-006, MECH-007, MECH-009 (ADR-0011, ADR-0014).
Dimensions come from mech/analysis/housing_params.py (one source, also used by the checks).
Scope of this first version: base with USB-C window, annular bayonet recess with lugs,
three PCB snap hooks, and the lid. NOT modelled yet: lid spigot, release tab and detent of the
bayonet, button access, posts under the board. Output goes to the build folder (not committed).
"""

import math
import os
import sys

import FreeCAD as App
import Part

sys.path.insert(0, "mech/analysis")
import housing_params as p  # noqa: E402

BUILD = os.environ.get("MECH_BUILD_DIR", "build/mech")
os.makedirs(BUILD, exist_ok=True)

V = App.Vector
EPS_MM3 = 1e-6
R_OUT = p.D_OUT / 2.0
R_IN = R_OUT - p.WALL
H_TOTAL = p.Z_PCB_BOT + p.T_PCB + p.H_LED + p.D_LED + p.LID_T


def cyl(r, h, z=0.0):
    return Part.makeCylinder(r, h, V(0, 0, z))


def rot_z(shape, deg):
    s = shape.copy()
    s.rotate(V(0, 0, 0), V(0, 0, 1), deg)
    return s


def build_base():
    base = cyl(R_OUT, p.H_JOINT).cut(cyl(R_IN, p.H_JOINT - p.FLOOR, p.FLOOR))
    # USB-C window through the wall at azimuth 0 (+X)
    win = Part.makeBox(
        p.WALL * 3, p.WIN_W, p.WIN_H, V(R_IN - p.WALL, -p.WIN_W / 2, p.WIN_ZC - p.WIN_H / 2)
    )
    base = base.cut(win)
    # annular bayonet recess in the back (z = 0 side), lugs stay as ribs
    ring = cyl(p.BAY_R_OUT, p.BAY_DEPTH).cut(cyl(p.BAY_R_IN, p.BAY_DEPTH))
    for k in range(p.BAY_LUGS):
        rib = Part.makeBox(
            p.BAY_R_OUT - p.BAY_R_IN, p.BAY_LUG_W, p.BAY_DEPTH, V(p.BAY_R_IN, -p.BAY_LUG_W / 2, 0)
        )
        ring = ring.cut(rot_z(rib, 360.0 / p.BAY_LUGS * k + 90.0))
    base = base.cut(ring)
    # PCB snap hooks: arm on the wall, lip over the board edge. Azimuth 0 is the USB-C window.
    z_top = p.Z_PCB_BOT + p.T_PCB
    for k in range(p.HOOK_COUNT):
        az = 120.0 * k + 60.0
        arm = Part.makeBox(
            R_IN - p.HOOK_R - 0.2 + 0.4,
            p.HOOK_W,
            z_top + 0.4 - p.FLOOR,
            V(p.HOOK_R + 0.2, -p.HOOK_W / 2, p.FLOOR),
        )
        lip = Part.makeBox(
            p.HOOK_LIP + 0.5, p.HOOK_W, 0.8, V(p.HOOK_R - p.HOOK_LIP, -p.HOOK_W / 2, z_top + 0.4)
        )
        base = base.fuse(rot_z(arm, az)).fuse(rot_z(lip, az))
    return base.removeSplitter()


def build_lid():
    lid = cyl(R_OUT, H_TOTAL - p.H_JOINT, p.H_JOINT).cut(
        cyl(R_IN, H_TOTAL - p.H_JOINT - p.LID_T, p.H_JOINT)
    )
    return lid.removeSplitter()


def main():
    doc = App.newDocument("busy_light_housing")
    parts = {"base": build_base(), "lid": build_lid()}
    for name, shape in parts.items():
        assert shape.isValid(), f"{name}: invalid shape"
        assert shape.Volume > 0, f"{name}: no volume"
        assert len(shape.Solids) == 1, f"{name}: {len(shape.Solids)} solids, expected 1"
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        bb = shape.BoundBox
        print(
            f"housing: {name} volume {shape.Volume:.0f} mm3, "
            f"box {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f}"
        )
    common = parts["base"].common(parts["lid"])
    assert common.Volume < EPS_MM3, "base and lid overlap"
    # the board (D 46, 1.6 thick) must fit between floor, hooks and wall without touching them
    board = cyl(p.D_PCB / 2.0, p.T_PCB, p.Z_PCB_BOT)
    clash = parts["base"].common(board).Volume
    assert clash < EPS_MM3, f"board interferes with the base: {clash:.2f} mm3"
    print("housing: board/base interference volume 0 mm3")
    box = parts["base"].BoundBox.XLength
    assert math.isclose(box, p.D_OUT, abs_tol=1e-3), "outer diameter differs from the parameter"
    doc.recompute()
    for name, shape in parts.items():
        shape.exportStep(os.path.join(BUILD, f"{name}.step"))
    doc.saveAs(os.path.join(BUILD, "busy_light_housing.FCStd"))
    print("housing: OK, written to", BUILD)


main()
