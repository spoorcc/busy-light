"""Spike: board-in-housing check in FreeCAD (headless). Reads params.toml, imports the KiCad STEP and the
housing STEP files, places the board and checks interference and clearances.
usage (repo root):  echo "import sys; sys.argv=['x', BOARD_STEP, HOUSING_DIR, PARAMS, HOUSING_SCRIPT]; exec(open('hw/kicad/spike/src/freecad_fit.py').read())" | freecad -c
"""
import json
import math
import re
import sys
import tomllib

import Part
from FreeCAD import Vector as V

board_step, housing_dir, params_file, housing_script = sys.argv[1:5]
P = tomllib.load(open(params_file, "rb"))
res = {"checks": {}}


def check(name, ok, detail):
    res["checks"][name] = {"pass": bool(ok), "detail": detail}
    print(("PASS " if ok else "FAIL ") + name + ": " + detail)


# 1. Consistency of the shared parameters with the constants in the housing model
src = open(housing_script).read()
def const(n):
    return float(re.search(rf"\b{n}=([0-9.]+)", src).group(1))
pairs = [
    ("D_PCB", P["board"]["outline_diameter_mm"]),
    ("T_PCB", P["stackup"]["pcb_thickness_mm"]),
    ("Z_PCB_BOT", P["stackup"]["z_pcb_bottom_mm"]),
    ("N_LED", P["ring"]["led_count"]),
    ("D_RING", 2 * P["ring"]["radius_mm"]),
    ("LED_PHASE", P["ring"]["phase_deg"]),
    ("R_POST", P["mounting"]["peg_radius_mm"]),
    ("PEG_RAD", P["mounting"]["hole_diameter_mm"] / 2 - 0.2),
]
az = re.search(r"POST_AZ=\(([^)]*)\)", src).group(1)
check("param POST_AZ", [float(x) for x in az.split(",") if x.strip()] == P["mounting"]["peg_azimuths_deg"], f"housing ({az}) vs params")
for n, v in pairs:
    check(f"param {n}", abs(const(n) - v) < 1e-9, f"housing {const(n)} vs params {v}")

# 2. Import shapes
board = Part.read(board_step)
base = Part.read(f"{housing_dir}/base.step")
lid = Part.read(f"{housing_dir}/lid.step")
# The bare board is the solid with the largest volume; parts and pins may extend below it.
pcb = max(board.Solids, key=lambda x: x.Volume)
CU = P["stackup"]["copper_thickness_mm"]
board.translate(V(0, 0, P["stackup"]["z_pcb_bottom_mm"] + CU - pcb.BoundBox.ZMin))  # STEP board = dielectric core; copper bottom at Z_PCB_BOT
solids = board.Solids
pcb = max(solids, key=lambda x: x.Volume)
bb = board.BoundBox
res["board_bbox"] = [bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax]
print("board bbox", [round(x, 2) for x in res["board_bbox"]])

# 3. Outline from KiCad equals the parameter (bare board solid)
dia = max(pcb.BoundBox.XLength, pcb.BoundBox.YLength)
check("KiCad outline diameter", abs(dia - P["board"]["outline_diameter_mm"]) < 0.01, f"{dia:.3f} mm")
check("PCB thickness (core + 2 x copper)", abs(pcb.BoundBox.ZLength + 2 * CU - P["stackup"]["pcb_thickness_mm"]) < 0.01, f"{pcb.BoundBox.ZLength + 2 * CU:.3f} mm")

# 4. Interference of every board solid with the housing parts (the bare board rests on the posts: touching is allowed)
for i, sol in enumerate(solids):
    for name, house in (("base", base), ("lid", lid)):
        vol = sol.common(house).Volume
        if vol > 1e-3:
            b2 = sol.BoundBox
            check(f"interference solid {i} vs {name}", False,
                  f"common volume {vol:.3f} mm3; solid bbox z {b2.ZMin:.1f}..{b2.ZMax:.1f}, xy {b2.XMin:.1f}..{b2.XMax:.1f}, {b2.YMin:.1f}..{b2.YMax:.1f}")
check("no interference with the lid", all(sol.common(lid).Volume < 1e-3 for sol in solids), f"{len(solids)} solids tested")
check("no interference with the base", all(sol.common(base).Volume < 1e-3 for sol in solids), f"{len(solids)} solids tested")

# 5. Top of the tallest part versus the lid underside
top = max(sol.BoundBox.ZMax for sol in solids)
res["max_part_top_z"] = top
check("tallest part below the lid top", top < lid.BoundBox.ZMax, f"tallest part top z {top:.2f}; lid z {lid.BoundBox.ZMin:.2f}..{lid.BoundBox.ZMax:.2f}")
json.dump(res, open(sys.argv[5] if len(sys.argv) > 5 else "/dev/null", "w"), indent=1)
failed = [k for k, v in res["checks"].items() if not v["pass"]]
print("RESULT", "FAIL" if failed else "PASS", failed)
