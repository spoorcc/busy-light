# 2026-11-07: first housing model

FreeCAD 1.1.4 installed locally (download checked against the CI sha256). The assistant wrote the first generator (`mech/freecad/housing.py`) and the tolerance check for the 53 mm geometry, as work under the approved MECH-001 to MECH-009. Build output goes to `build/mech` and is not committed. Result and gaps: `docs/verification/reports/mech-housing-first-model.md`.

Open for the owner: USB-C window reserve (14.0 x 8.0 has none at worst case), and the thin floor skin under the bayonet.

## Hardware evidence (same day)
The owner supplied the BZX84C series datasheet. The assistant wrote the HW-012 evidence for the BZX84C5V1 (candidate) and the SN74LVC1G08 (candidate; inputs accept 5.5 V), and reran the surge analysis with the datasheet corners (see `analysis-supply-pin-surge.md`). The spike schematic is not changed yet: TVS1 is still not chosen.
