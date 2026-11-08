# Spike board: assembly and fabrication review (HW-010)

- **Date:** 2026-11-08. **Author:** assistant. **Status:** Draft evidence. Not an approval; only the owner approves a design.
- **Subject:** `hw/kicad/spike-gate/board/busy_light_spike.kicad_pcb` (ring14 run 9, 4 layers, 1.6 mm, 53.9 x 46.1 mm, 100 parts, 59 on the bottom side).
- **Tool and tests:** `hw/kicad/spike-gate/src/pcb_fabreview.py`, `tests/test_pcb_fabreview.py` (7 pass).
- **Basis:** KiCad 10.0.6 `kicad-cli` exports and DRC; JLCPCB numbers of ADR-0020 (Proposed) in `pcb_fabcheck.py`.

## What was run
| Check | Result |
|---|---|
| DRC, all severities, all track errors | 0 unconnected, 0 schematic parity findings; findings only courtyards_overlap 8 and items_not_allowed 1 (U9 antenna keep-out, DEV-004). No silkscreen, solder-mask or edge finding was reported. |
| Fabricator minimums (`pcb_fabcheck.py`) | PASS; via ring at the 0.15 mm absolute minimum on all 131 vias |
| Gerber export (12 files: 4 copper, 2 mask, 2 paste, 2 silkscreen, edge cuts, job), Excellon drill (`.drl`) | files written; not opened in a second viewer |
| Position file (`pos.csv`), BOM (`bom.csv`) | written; see findings |
| `pcb_fabreview.py` (BOM against board, references, fiducials, silkscreen, tbd values) | **4 findings** |

## Findings
| # | Finding | Evidence | Effect |
|---|---|---|---|
| 1 | The schematic BOM has 7 unannotated references: C1B? to C1F?, R_ILIM3B?, R_VD?. The board has them as C1B to C1F, R_ILIM3B, R_VD. | `pcb_fabreview.py` `unannotated`, `bom_vs_board` | The BOM from the schematic does not match the board. Fix in the schematic generator; not investigated. |
| 2 | No reference designators on the silkscreen: all 100 reference texts are on F.Fab or B.Fab. | `refs_on_silk` 0 | Hand assembly, rework and probing have no marks. |
| 3 | No fiducials. | `fiducials` 0 | Pick-and-place machines align on fiducials; JLCPCB assembly may add its own or reject the panel. Not checked with the fabricator. |
| 4 | Five parts still have a tbd value: C2, C3, C4, C5, C6 (HW-014, HW-015, HW-016 are Draft). | `open_values` | The BOM cannot be ordered. |
| 5 | The BOM has no manufacturer part number or supplier number field. | `has_mpn_field` false | No sourcing or availability check is possible. |
| 6 | Two-sided assembly: 41 parts on top, 59 on the bottom; the USB-C receptacle (20 through-hole pads) is edge-mounted. | `pos.csv`, pcbnew | Costs more and needs a second reflow pass; the through-hole part needs hand or selective soldering. |

## Not run
Opening the Gerbers in an independent viewer, a fabricator's own DFM check (JLCPCB online), part availability and lifecycle, 3D fit against the housing (MECH), panelisation, test-point access for a test fixture, RF and antenna, thermal, bench. The 3D render shows the copper only faintly, so solder-mask appearance was not judged.

## Reading
The board file is clean for the DRC and the fabricator minimums. It is **not ready to order**: findings 1 to 5 would stop or slow an assembly order. None of this makes the board "DFx approved" or "fully functional"; both statements need the owner's review, a built board and the bench tests (TC list in the HW-010 verification plan).

## Update after the fixes (2026-11-08, owner choice "all three, including renaming")
| # | Change | Evidence |
|---|---|---|
| 1 | Seven parts renamed to numbered names (KiCad reads a reference without a trailing number as unannotated): C1B to C1F to **C27 to C31**, R_ILIM3B to **R20**, R_VD to **R21**. Generators, rules, tests, evidence files and current reports use the new names; journals, the CHANGELOG and the earlier ring sections keep the old names as history. The schematic was regenerated (`run_full.sh`: ERC 0, intent equal, deterministic) and the board renamed by script (`pcb_rename.py`, 5 tests); one auto-named net (`Net-(R_ILIM3-Pad1)`, now `Net-(R20-Pad2)`) was renamed with it. | BOM has no `?`; BOM and board refs agree; schematic parity shows only the two known C3 and C4 mismatches |
| 2 | Reference designators on the silkscreen by script (`pcb_finish.py`, 12 tests): 73 of 100 parts have one (1.0 mm text, 0.8 mm where tight). 27 parts have none because the DRC found no free place: SW1, D3, DZ14, DZ15, C4, C25 to C27, U1, U14, U15, TP5, R1 to R3, R5, R11 to R15, R17, R18, R20, R_ILIM1, R_ILIM3, R_SU15. | DRC with all severities: no silkscreen finding; render checked by eye (top and bottom) |
| 3 | Four fiducials (two per side, 1.0 mm pad, 2.0 mm mask opening), outside the U9 antenna area, the connector and the rule area. A third per side found no free spot. | `pcb_fabreview.py` counts 4 |

Checks on the finished stored board: strict gate (tolerated classes only: courtyards_overlap 8, items_not_allowed 1, symbol mismatch 2), fab-minimum check PASS, power drops 13.5, 18.0 and 22.7 mV, 131 vias and 1369.9 mm of track (no routing change), 0 unconnected. `pcb_fabreview.py` still reports FINDINGS: 26 parts without a silkscreen designator (the 27th, TP5, is a test point), tbd values C2 to C6, and the BOM has no part-number field. The fiducials are not checked against a fabricator's rules (JLCPCB asks for its own); their count of 4 is below the usual 3 per side.

Name map for the older documents: C1B to C1F = C27 to C31, R_ILIM3B = R20, R_VD = R21.

