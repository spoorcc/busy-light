# SPDX-License-Identifier: Apache-2.0
"""Housing generator, concept B (opaque base + translucent lid), prototype geometry.

Run headless: scripts/ci_mech.sh (it pipes exec(open(this file).read()) into freecad -c).
Traces to MECH-001, MECH-004, MECH-006, MECH-007, MECH-009 (ADR-0011, ADR-0014).
Dimensions come from mech/analysis/housing_params.py (one source, also used by the checks).
Scope: base with USB-C window, button hole, annular bayonet groove (lips, stop, detent), PCB
posts and snap hooks, lid spigot with grooves; lid with skirt and snap bumps. NOT modelled: the
release tab of the bayonet, the switch and the PCB itself (a board cylinder is used for the
interference check). Output goes to the build folder (not committed).
"""

import math
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


def box_at(size, corner, az):
    """Box of size (dx, dy, dz) with its corner at (x, y, z), turned by az degrees about Z."""
    return rot_z(Part.makeBox(*size, V(*corner)), az)


def build_base():
    # wall with a chamfered inner ledge from LEDGE_Z to H_JOINT so that the spigot has support
    r_spig_out = R_OUT - p.SKIRT_T - p.SPIGOT_CLEAR
    r_spig_in = r_spig_out - p.SPIGOT_T
    base = cyl(R_OUT, p.H_JOINT)
    cavity = cyl(R_IN, p.LEDGE_Z - p.FLOOR, p.FLOOR).fuse(
        Part.makeCone(R_IN, r_spig_in, p.H_JOINT - p.LEDGE_Z, V(0, 0, p.LEDGE_Z))
    )
    base = base.cut(cavity)
    # lid spigot above the joint plane, with grooves for the lid snap bumps on its outer face
    spigot = cyl(r_spig_out, p.Z_SPIGOT_TOP - p.H_JOINT, p.H_JOINT).cut(
        cyl(r_spig_in, p.Z_SPIGOT_TOP - p.H_JOINT, p.H_JOINT)
    )
    base = base.fuse(spigot)
    z0, z1 = p.H_JOINT + 0.4, p.Z_SPIGOT_TOP - 0.25
    for az in p.LID_HOOK_DEG:
        groove = box_at(
            (p.LID_BUMP + 0.1, p.LID_HOOK_W, z1 - z0),
            (r_spig_out - p.LID_BUMP, -p.LID_HOOK_W / 2, z0),
            az,
        )
        base = base.cut(groove)
    # USB-C window through the wall at azimuth 0 (+X)
    base = base.cut(
        Part.makeBox(
            p.WALL * 3, p.WIN_W, p.WIN_H, V(R_IN - p.WALL, -p.WIN_W / 2, p.WIN_ZC - p.WIN_H / 2)
        )
    )
    # button hole through the wall (working values: the switch is not chosen, plan 05)
    z_btn = p.Z_PCB_BOT + p.T_PCB + p.BTN_Z_ABOVE_PCB
    btn = Part.makeCylinder(p.BTN_D / 2.0, p.WALL * 3, V(R_IN - p.WALL, 0, z_btn), V(1, 0, 0))
    base = base.cut(rot_z(btn, p.BTN_DEG))
    # annular bayonet groove with lock lips, stop and detent in the back (z = 0 side)
    base = base.cut(bg.groove_cut())
    # PCB posts under the board, none at the USB-C azimuth
    for az in p.POST_DEG:
        post = box_at(
            (p.POST_PAD_R, p.POST_PAD_W, p.POST_H + 0.2),
            (p.POST_R - p.POST_PAD_R / 2, -p.POST_PAD_W / 2, p.FLOOR - 0.2),
            az,
        )
        base = base.fuse(post)
    # PCB snap hooks: arm on the wall, lip over the board edge. Azimuth 0 is the USB-C window.
    z_top = p.Z_PCB_BOT + p.T_PCB
    for k in range(p.HOOK_COUNT):
        az = 120.0 * k + 60.0
        arm = box_at(
            (R_IN - p.HOOK_R - 0.2 + 0.4, p.HOOK_W, z_top + 0.4 - p.FLOOR),
            (p.HOOK_R + 0.2, -p.HOOK_W / 2, p.FLOOR),
            az,
        )
        lip = box_at(
            (p.HOOK_LIP + 0.5, p.HOOK_W, 0.8),
            (p.HOOK_R - p.HOOK_LIP, -p.HOOK_W / 2, z_top + 0.4),
            az,
        )
        base = base.fuse(arm).fuse(lip)
    return base.removeSplitter()


def build_lid():
    """Plate on the spigot top, skirt around the spigot with the clearance, three snap bumps."""
    r_skirt_in = R_OUT - p.SKIRT_T
    lid = cyl(R_OUT, H_TOTAL - p.Z_SPIGOT_TOP, p.Z_SPIGOT_TOP)
    skirt = cyl(R_OUT, p.Z_SPIGOT_TOP - p.H_JOINT, p.H_JOINT).cut(
        cyl(r_skirt_in, p.Z_SPIGOT_TOP - p.H_JOINT, p.H_JOINT)
    )
    lid = lid.fuse(skirt)
    z0, z1 = p.H_JOINT + 0.4, p.Z_SPIGOT_TOP - 0.25
    r_tip = R_OUT - p.SKIRT_T - p.SPIGOT_CLEAR - p.LID_BUMP + 0.05
    for az in p.LID_HOOK_DEG:
        bump = box_at(
            (r_skirt_in + 0.1 - r_tip, p.LID_HOOK_W, z1 - z0),
            (r_tip, -p.LID_HOOK_W / 2, z0),
            az,
        )
        lid = lid.fuse(bump)
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
