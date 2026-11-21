# Mechanical analysis

Tolerance stack-ups, interference checks (against KiCad STEP), FEM setups and results. Reproducible scripts preferred.

| File | Content |
|------|---------|
| `housing_params.py` | Working dimensions of the housing (concept B); one source for the FreeCAD generator and the checks |
| `check_tolerance.py` | Tolerance stack and fit checks (MECH-004, MECH-006, MECH-007, MECH-009); `scripts/ci_mech.sh` runs it |
| `test_check_tolerance.py` | Unit tests of the checks (`pytest`) |
| `render_dump_mesh.py`, `render_views.py` | README views of the housing model (`mech/render_readme_images.sh`) |

Not done: an interference check of the P1 board (`hw/kicad/spike-gate/board-p1/`) against the housing, FEM, and any
print or fit test. All dimensions are working values, not measured.
