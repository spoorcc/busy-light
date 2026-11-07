# Evidence: first housing model and tolerance check (MECH-001, MECH-004, MECH-006, MECH-007, MECH-009)

- **Date:** 2026-11-07. **Author:** assistant. **Status:** Evidence of an analysis and a model run. Nothing printed, nothing measured. Not a verification of the requirements.
- **Code:** `mech/freecad/housing.py` (FreeCAD 1.1.4 generator), `mech/analysis/housing_params.py` (dimensions), `mech/analysis/check_tolerance.py`, tests in `mech/analysis/test_check_tolerance.py`.

## What was run
- `scripts/ci_mech.sh` with the FreeCAD 1.1.4 AppImage (sha256 as in CI). The generator built base and lid, each one valid solid. Observed: base 6804 mm3 (53.0 x 53.0 x 14.0), lid 2970 mm3 (2.4 high), base and lid do not overlap, the board (D 46, 1.6 thick) does not touch the base (interference volume 0).
- `check_tolerance.py`: PASS. Observed: PCB gap to wall nominal 1.90, worst case 1.38, RSS 1.56 mm; hook lip 0.80 mm leaves +0.58 mm at worst case; USB-C window 14.0 x 8.0 has slack 1.20 mm against a worst-case need of 1.20 mm (no reserve); bayonet ring 4.70 mm wide; floor skin under the bayonet 0.80 mm (2.0 print lines); turn travel 9.8 mm; label circle D 21 mm fits inside the ring with 5.8 mm margin.
- `pytest mech/analysis`: 6 passed (7 after the window change) (including 4 cases that must fail when a dimension is made wrong).

## Findings
1. With 14.0 x 8.0 mm the USB-C window passed at worst case with zero reserve. The owner chose 14.2 x 8.2 mm on 2026-11-07 (MECH-004 updated, `housing_params.py` updated). With it the slack is 1.40 mm against a need of 1.20 mm, so 0.20 mm reserve. The tolerance check and the 7 tests were rerun with 14.2 x 8.2 and pass; the FreeCAD generator was rerun with it as well. The window figures in "What was run" are from the first run with 14.0 x 8.0.
2. The floor skin under the bayonet is exactly 2 print lines. It is the thinnest part of the base and sits on a bridge on the bed side. The coupon test (TC-307) has to show it holds.
3. The check does not yet cover: lid spigot clearance, release tab and detent, posts under the board, button access. These are not in the model.

## Not run
No print, no fit test with cables, no FEM, no heat run. FDM tolerances (+-0.3 mm, +-0.2 mm fine) are assumptions from the concept report, not measured on the printer.

## Coupon generator (MECH-002, MECH-007)
- `mech/freecad/coupons.py` builds 7 print pieces: 3 diffuser plates (0.8, 1.2, 1.6 mm), 3 spacer rings (4, 6, 8 mm) that give the 9 combinations of MECH-002 on the real LED board, and a bayonet floor disc with the recess, the lugs and the 0.8 mm floor skin.
- Observed: every piece is one valid solid; the floor skin measured in the model is 0.80 mm. Run through `scripts/ci_mech.sh` together with the housing.
- Not done: the mating accessory ring is not designed, so the bayonet coupon tests print quality of recess, lugs and skin, not the lock action. The procedures of TC-302 and TC-307 are still "TBD" and need the owner's approval once written. Nothing is printed.
