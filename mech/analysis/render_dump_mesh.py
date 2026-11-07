# SPDX-License-Identifier: Apache-2.0
"""Write triangle meshes of the housing parts to JSON for the README views (FreeCAD, headless).

Run: scripts via mech/render_readme_images.sh (needs the build folder from scripts/ci_mech.sh).
Reads the STEP files of the generators, writes <out>/mesh.json. Nothing is edited by hand.
"""

import json
import os

import Part

BUILD = os.environ.get("MECH_BUILD_DIR", "build/mech")
OUT = os.environ.get("MECH_RENDER_DIR", "build/mech-render")
PARTS = {"base": "base.step", "lid": "lid.step", "accessory": "coupon_accessory_ring.step"}
TOL = 0.05  # mm


def main():
    os.makedirs(OUT, exist_ok=True)
    mesh = {}
    for name, f in PARTS.items():
        shape = Part.read(os.path.join(BUILD, f))
        verts, tris = shape.tessellate(TOL)
        mesh[name] = {"v": [[v.x, v.y, v.z] for v in verts], "t": [list(t) for t in tris]}
        print(f"render: {name} {len(verts)} vertices, {len(tris)} triangles")
    with open(os.path.join(OUT, "mesh.json"), "w") as fh:
        json.dump(mesh, fh)


main()
