# Spike board result (HW-010)

The routed 4-layer spike board: ring14 run 9, picked from 12 runs (Freerouting 2.5.0 is not deterministic, so this is one run, not a recipe).
Made by `run_best.sh` with `SPIKE_PROFILE=fine`, `PLACE_GRID=1.0`, `PLACE_ANT_KEEPOUT=1`, `PLACE_BLOCKS=3`, `PLACE_ORIENT=1.5`, `SEED_OFFSET=200`, input netlist `full8` (not in the repo; regenerate with `run_full.sh`). Report: `docs/verification/reports/spike-pcb-placement-routing.md`.

Files: `busy_light_spike.kicad_pcb`, `.kicad_pro`, `.kicad_sch`, `.kicad_dru` (rules), `.placement.json`, `fp-lib-table` and `CUSTOM.pretty` (open the board next to them). Script output, never edited by hand.

Checks run on this file (2026-11-08):
- strict gate `SPIKE_ALLOW_KNOWN_OPEN=0 python3 src/kicad_strict.py drc board/busy_light_spike.kicad_pcb stitched-4l`: 0 open items, only the tolerated classes: courtyards_overlap 8 (max 14, U9 antenna, DEV-004), items_not_allowed 1 (DEV-004), footprint_symbol_mismatch 2 (C3, C4; HW-014 Draft);
- `src/pcb_fabcheck.py`: PASS against the JLCPCB numbers of ADR-0020, with the via ring at the absolute minimum (0.15 mm) on all 131 vias;
- `src/pcb_power_check.py`: 13.5 mV (VBUS_IC, 1.5 A), 18.0 mV (+5V, 1.0 A), 22.7 mV (+3V3, 0.5 A); the 50 mV target is an analyst assumption, not a requirement.

Not run: antenna/RF, thermal, a full fab review (Gerber, silkscreen, solder mask, assembly), bench. Open: ADR-0020 (fine rules) is Proposed; HW-014 to HW-016 are Draft. The test points are not in a row and the IC rotations are mixed. This is a spike result, not a reviewed or approved board; it is not "DFx approved" and not "fully functional".
