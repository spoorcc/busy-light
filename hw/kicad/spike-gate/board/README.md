# Spike board result (HW-010)

The routed 4-layer spike board: ring14 run 9, picked from 12 runs (Freerouting 2.5.0 is not deterministic, so this is one run, not a recipe).
Made by `run_best.sh` with `SPIKE_PROFILE=fine`, `PLACE_GRID=1.0`, `PLACE_ANT_KEEPOUT=1`, `PLACE_BLOCKS=3`, `PLACE_ORIENT=1.5`, `SEED_OFFSET=200`, input netlist `full8` (not in the repo; regenerate with `run_full.sh`). Report: `docs/verification/reports/spike-pcb-placement-routing.md`.

Files: `busy_light_spike.kicad_pcb`, `.kicad_pro`, `.kicad_sch`, `.kicad_dru` (rules), `.placement.json`, `fp-lib-table` and `CUSTOM.pretty` (open the board next to them). Script output, never edited by hand.

Finishing (2026-11-08): the seven unannotated parts were renamed (`src/pcb_rename.py`: C1B to C1F are now C27 to C31, R_ILIM3B is R20, R_VD is R21), and silkscreen designators and four fiducials were added (`src/pcb_finish.py`; 27 parts have no free place for a designator). Routing did not change.

Checks run on this file (2026-11-08):
- strict gate `SPIKE_ALLOW_KNOWN_OPEN=0 python3 src/kicad_strict.py drc board/busy_light_spike.kicad_pcb stitched-4l`: 0 open items, only the tolerated classes: courtyards_overlap 8 (max 14, U9 antenna, DEV-004), items_not_allowed 1 (DEV-004);
- `src/pcb_fabcheck.py`: PASS against the JLCPCB numbers of ADR-0020, with the via ring at the absolute minimum (0.15 mm) on all 131 vias;
- `src/pcb_power_check.py`: 13.5 mV (VBUS_IC, 1.5 A), 18.0 mV (+5V, 1.0 A), 22.7 mV (+3V3, 0.5 A); the 50 mV target is an analyst assumption, not a requirement.

Capacitor values and spare (2026-11-08, owner decisions in `docs/verification/reports/proposal-tbd-capacitor-values.md`): C2 4.7u, C3 10u (0805), C5 2.2u, C6 10u; C4 and C32 are 1206 spares, not fitted (HW-016). `src/pcb_spare_caps.py` set the values, added C32 (bottom side, 24 mm from U7 pin 6 because the top side has no free place; C4 is 8.2 mm away, so the [5] mm of HW-016 is not met by either), marked both do-not-populate and wrote the sourcing fields to the footprints; `pcb_fix.py` routed C32 (one via, 13.7 mm of track, nothing else moved). The strict gate has no footprint mismatch any more; power drops unchanged (13.5, 18.0, 22.7 mV).

Not run: antenna/RF, thermal, a full fab review (Gerber, silkscreen, solder mask, assembly), bench. Open: ADR-0020 (fine rules) is Proposed; HW-014 to HW-016 are Draft. The test points are not in a row and the IC rotations are mixed. This is a spike result, not a reviewed or approved board; it is not "DFx approved" and not "fully functional".
