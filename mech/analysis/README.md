# Mechanical analysis

Tolerance stack-ups, interference checks (against KiCad STEP), FEM setups and results. Reproducible scripts preferred.

| File | Content |
|------|---------|
| `housing_params.py` | Working dimensions of the housing (concept B); one source for the FreeCAD generator and the checks |
| `check_tolerance.py` | Tolerance stack and fit checks (MECH-004, MECH-006, MECH-007, MECH-009); `scripts/ci_mech.sh` runs it |
| `test_check_tolerance.py` | Unit tests of the checks (`pytest`), including the informational centre button chains |
| `button_disc.py`, `test_button_disc.py` | Rigid disc on springs and switches, bridge stiffness bands, beam, plate and guide formulas (plan 09, analysis only) |
| `button_light.py`, `test_button_light.py` | Light spill of the LED ring onto the centre disc (plan 09 section 4.4) |
| `render_dump_mesh.py`, `render_views.py` | README views of the housing model (`mech/render_readme_images.sh`) |

The S2 and S3 zone search of the centre button is `hw/kicad/spike-gate/src/button_zone.py` (tests in `hw/kicad/spike-gate/tests/test_button_zone.py`);
results in `docs/verification/reports/analysis-button-disc.md`.

Not done: an interference check of the P1 board (`hw/kicad/spike-gate/board-p1/`) against the housing, FEM, and any
print or fit test. All dimensions are working values, not measured.
