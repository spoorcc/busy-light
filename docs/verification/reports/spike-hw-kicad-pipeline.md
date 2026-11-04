# Spike ADR-0012: can KiCad 10 and Python generate and check a board? (PC only)

- **Status:** Draft
- **Date:** 2026-11-04
- **Author:** Claude (exploratory spike for the owner). Not reviewed. Nothing here is Approved or Accepted.
- **Related:** ADR-0012, ADR-0004, HW-001
- **Code:** branch `spike/hw-kicad`, folder `hw/kicad/spike/` (`gen_schematic.py`, `gen_pcb.py`, lib tables). Exploratory only. It cannot be merged without Approved HW requirements (rule 1). The circuit is a stand-in (16 LEDs and one buffer, no requirements traced), not the product design.
- **Labels:** every result is marked **run** or **not run**.

## 1. Purpose
Show that the flow chosen in ADR-0012 works with the tools installed on 2026-11-04: KiCad 10.0.6, SKiDL 3.0.0, ngspice 47, Python 3.14.

## 2. Results
| Step | Result | Label |
|------|--------|-------|
| SKiDL generates a netlist and a `.kicad_sch` (16x SK6812MINI, 74AHCT1G125) using KiCad 10 libraries | Works. Needs `KICAD10_SYMBOL_DIR`. | run |
| KiCad 10 opens the SKiDL schematic: `kicad-cli sch erc`, `export netlist`, `export bom`, `export pdf` | All work. | run |
| ERC on the generated schematic | 50 violations without project library tables, 33 with them. Left: 17 `lib_symbol_mismatch`, 5 unconnected pins, 3 undriven input pins, 4 undriven power pins, 2 isolated labels. | run |
| Python (`pcbnew`) builds a PCB from the netlist: 16 LEDs on a 20 mm radius ring, 46 mm round outline, nets assigned | Works (17 footprints, 24 nets). Render: `docs/verification/reports/images/spike-hw-kicad-render.png`. | run |
| `kicad-cli pcb drc --schematic-parity` | Runs. 42 violations, 51 parity issues. Expected: no routing, silk and copper over the edge, footprint text differs from the symbol. | run |
| Gerber, STEP, SVG and 3D render export | All work. | run |
| ngspice | Installed (v47). No simulation was run in this spike. | not run |
| Routing (scripted or Freerouting) | Not attempted. Freerouting is not installed. | not run |
| Real part set, USB-C, ESP32-C3 module, antenna keep-out, current-limit part | Not attempted. | not run |

## 3. Findings
1. **Generated output is not reproducible.** SKiDL places symbols in a different order on each run, and the placement positions differ. Part order in the netlist changes with it. `pcbnew` writes footprints in an order that depends on random UUIDs, so two runs differ even with UUIDs removed. ADR-0012 item "regenerating gives byte-identical files" cannot be met as written. Options: a canonical post-processing step (sort by reference designator, normalise UUIDs), or compare a semantic dump (parts, nets, positions) instead of bytes. I recommend the semantic dump in CI plus fixed `tag=` and refdes values in the generator.
2. **Project library tables are needed.** Without `sym-lib-table` and `fp-lib-table`, ERC reports library errors. The spike tables use absolute `/usr/share/kicad` paths. A real project needs relative paths or the `${KICAD10_...}` variables, and project-local libraries in `hw/kicad/libs/` (pinned).
3. **SKiDL schematics are a layout of convenience.** The KiCad format version written is 20250114 (KiCad 9 format). KiCad 10 reads it. A reviewer will not find the schematic pleasant to read; sheet layout and net labels need work. Whether a professional-grade, human-reviewable schematic is possible with SKiDL is not shown.
4. **Symbol mismatch warnings** (17) mean the embedded symbol copy differs from the library. Cause not investigated.
5. **Stale tooling risk is real:** SKiDL 3.0.0 has no KiCad 10 writer; it writes KiCad 9 format and the netlist or schematic writers may break on later KiCad releases.
6. `pcbnew` prints a harmless `PROPERTY_ENUM` assert on start.

## 4. Conclusion for ADR-0012
The flow B is technically feasible for schematic, netlist, BOM, placement, outline, checks and exports. It is not shown to be feasible for routing or for human-quality schematics. Changes proposed for ADR-0012 (owner decides): replace "byte-identical regeneration" by "semantic equality of the regenerated design" and add Freerouting or scripted routing as a follow-up spike before ADR acceptance.

## 5. Not covered
No requirement traceability on parts (custom fields were not added), no ngspice test, no routing, no electrical correctness of the stand-in circuit, no EMC or RF layout, no run on the CI runner.

## 6. Round 2 (2026-11-04): own schematic writer, reproducibility, requirement fields, scripted routing
Code: `hw/kicad/spike/` on branch `spike/hw-kicad` (`src/schematic_writer.py`, `gen_schematic.py`, `gen_pcb.py`, `route_pcb.py`, `dump_design.py`, `check_req_fields.py`, `params.toml`, `run_spike.sh`). Stand-in circuit as in section 2, plus one 4-pin connector and two power flags.

| Step | Result | Label |
|------|--------|-------|
| Own schematic writer (`kiutils` 1.4.8, `uuid5` IDs, fixed reference designators) | KiCad 10 loads the file only when the format version is set to 20231120 (KiCad 8). With version 20250114 `kicad-cli` fails with "Failed to load schematic", because kiutils writes the older syntax. Derived symbols must be flattened and unit names renamed. | run |
| ERC of the written schematic | 0 violations (after a project file and library tables are present; without them ERC reports library errors). | run |
| Reproducibility, two runs | Schematic bytes identical. Semantic dumps (parts, nets, positions) identical. | run |
| Negative tests of the checks | A part without `HW_REQ` is reported (exit 1). A moved footprint changes the dump (diff exit 1). | run |
| `HW_REQ` field per part | Survives the KiCad netlist and the dump; check script works. | run |
| One parameter file (`params.toml`) feeding the PCB script | Works for the PCB script. The FreeCAD side was not connected. | run (PCB), not run (FreeCAD) |
| Scripted routing (`route_pcb.py`: pad-to-pad tracks, GND vias and a B.Cu pour) | Every net is connected (0 unconnected items) but DRC reports 16 shorting items, 10 crossing tracks, 7 clearance and 34 solder-mask bridge violations. Naive routing is not sufficient. | run |
| Freerouting | Not installed, not tried. | not run |
| Schematic-to-board parity | 36 parity issues remain (footprint-to-symbol link and fields); cause not investigated. | run, not fixed |
| SKiDL netlist with fixed `tag=` values and `PYTHONHASHSEED=0`, two runs | Identical except the source path and date. SKiDL schematic placement still differed between runs (symbol positions). Observed in the session scratchpad; no log archived. | run |
| Net names | `pcbnew` net names carry a `/` prefix (`/GND`); scripts must account for it. | run |
| ngspice, FreeCAD side of the parameter file, Docker run of the CI image | Not run. | not run |

Conclusion of round 2: the schematic path (ERC-clean, reproducible, traceable fields) is feasible with an own writer on KiCad 8 syntax. The routing path is not shown. A real router (Freerouting) or a rule-based router is needed; this is the main remaining risk of ADR-0012 option B. The KiCad 8 syntax dependency (kiutils) is a pin risk: KiCad 10 upgrades the file on first save in the GUI.

## 7. Round 3 (2026-11-04): Freerouting and the FreeCAD fit check
Code: `hw/kicad/spike/src/freecad_fit.py`, `run_spike.sh`, `params.toml` on branch `spike/hw-kicad` (commit 1fcc888). The Freerouting commands were run by hand in the session scratchpad and are not yet in a script.

| Step | Result | Label |
|------|--------|-------|
| Freerouting 2.5.0 (`freerouting-2.5.0.jar` from the GitHub release; SHA-256 equals the digest published with the release; run headless on OpenJDK 27) | Runs. DSN export and SES import work through `pcbnew` (`ExportSpecctraDSN`, `ImportSpecctraSES`). | run |
| Routing of the stand-in board | 14.4 s. 53 unrouted connections at the start, 3 unrouted at the end, 0 violations reported by the router. | run |
| KiCad DRC after the SES import | 3 unconnected items. No shorting, crossing or clearance violations (the naive script gave 16, 10 and 7). Remaining: 32 copper-to-edge, 20 track-width, 12 dangling-via and 29 silk-to-edge violations. No design rules or net classes are defined yet, and the stand-in puts the connector and the buffer on top of each other near the board centre. Not investigated further. | run |
| Parameter consistency with the housing model (D_PCB, T_PCB, Z_PCB_BOT, N_LED, D_RING, R_POST, PEG_RAD, POST_AZ) | All pass. This compares `params.toml` with constants in the housing script. It is a consistency check, not a single source: the housing script does not read the file. | run |
| KiCad STEP of the board imported into FreeCAD, placed at Z_PCB_BOT, checked against the V1 housing STEP files | Outline diameter 46.000 mm matches. No interference with the lid. Tallest part (stand-in pin header) top at z 15.14 mm, below the lid top at 16.45 mm. | run |
| Same check, failures | (1) The board solid is 1.51 mm thick, not 1.6 mm: the KiCad default stackup sums to 1.51 mm, so the stackup must be defined explicitly (not fixed). (2) One overlap of 3.378 mm3 between the board and the base, near x 0, y 22.4, z 5.0 to 6.5 mm (about 2.4 x 1.2 mm), at azimuth 90 degrees on the board edge. The housing model has a notch there (NOTCH_R, NOTCH_AZ); the board has none. Cause not verified. | run, not fixed |
| Mounting holes for the three pegs | Added to the board from `params.toml`. Only the one overlap above remains. | run |
| Interference check with the real board, real parts, real housing | Not possible yet: the housing uses placeholders, the board is a stand-in. | not run |

Conclusion of round 3: a real router closes most of the routing gap, and the board-to-housing check finds real mismatches (stackup, notch) from files alone. Routing with defined design rules, the stackup and the notch are the next items.

## 8. Round 4 (2026-11-04): gate G1 work (scripted routing, rules, parity, stackup, mechanical conflict)
Code: `hw/kicad/spike/` on branch `spike/hw-kicad` (commit daa78d7), `run_spike.sh` runs the whole chain. Freerouting is called from `src/route_freerouting.py`, which checks the jar hash before use and stores the routing session as `routed.kicad_pcb.ses` next to the output.

| Step | Result | Label |
|------|--------|-------|
| Schematic-to-board parity | 0 issues. Cause of the 36: footprints had no library name in their identifier (`SetFPID` with the library nickname) and no `HW_REQ` field. | run |
| Footprint choice | LED symbol and footprint changed from 3535 (SK6812MINI) to 2020 (WS2812B-2020) to match the housing placeholder (LED_SIZE 2.0 mm). LED phase 3.75 degrees now comes from `params.toml` and is checked against the housing constant. | run |
| Design rules | Net classes Default (0.25 mm track) and Power (0.5 mm on +5V and GND), minimum track 0.15 mm, copper-to-edge 0.5 mm, in the hand-maintained `libs/spike.kicad_pro`. The values are placeholders for a prototype shop and must become HW requirements. | run |
| Tool overwrite finding | `pcbnew` overwrites the project file (`.kicad_pro`) when it saves a board, and `kicad-cli` rewrites it too. The reviewed rules file must be copied back after each generation step; otherwise net classes and rules are silently lost. | run |
| Edge keep-out as rule areas | Copper keep-out rings (0.5 mm) along the board edge and around the mounting holes, built from `params.toml`. The router honours them through the DSN. | run |
| Mechanical conflict found | With the housing peg azimuths 30, 150 and 270 degrees at R 21 mm, the 2.8 mm holes fall on the pads of LED D2 and D13 (LEDs at 3.75 + 22.5 k degrees, R 20 mm). That caused the edge-clearance violations and the unrouted connections. A hole fits only within about 3 degrees of a midpoint between two LEDs, and three pegs 120 degrees apart cannot all sit at midpoints. A what-if with 15, 150 and 285 degrees (uneven spacing) routes completely. This is a housing or LED-count decision for the owner. | run |
| Routing with the what-if pegs | Freerouting: 53 connections, 0 unrouted, 2 s. KiCad DRC of the routed board: 0 violations, 0 unconnected, 0 parity issues. The router's own score line reports 16 violations; KiCad DRC is the reference used here and the difference is not explained. | run |
| Routing with the housing pegs | 5 to 6 unrouted connections and 7 to 10 copper-to-edge violations, all at D2 and D13. | run |
| Stackup | Explicit two-layer stackup written into the board; the STEP board is now 1.600 mm including copper. The earlier 1.51 mm came from the KiCad default stackup. | run |
| FreeCAD fit check | Outline 46.000 mm and thickness 1.600 mm pass; no lid interference. Still failing: POST_AZ differs (the what-if, expected) and a 3.4 mm3 overlap with the base near the board edge at about 90 degrees, probably the missing board notch. Not fixed. | run, not fixed |
| Reproducibility | Dumps and schematic bytes identical over two runs. Two Freerouting runs were not compared. | run (design), not run (router) |
| ngspice, CI image run, tool-qualification table, pins by digest | Not done. | not run |

Status against gate G1 of ADR-0012 (stand-in board, what-if pegs): (a) ERC 0, parity 0, DRC 0: met. (b) 100 percent routed: met. (c) identical dumps including tracks, vias and zones: not met, because the dump covers parts, nets and positions only. (d) Freerouting scripted: met locally, not yet in CI. With the housing pegs, (a) and (b) are not met.

## 9. Round 5 (2026-11-04): widened semantic dump, regeneration gate, negative tests
Code: `hw/kicad/spike/` on branch `spike/hw-kicad` (`src/dump_design.py`, `src/route_freerouting.py`, `run_spike.sh`, `tests/test_dump_design.py`, `expected/`, `fixtures/`).

| Step | Result | Label |
|------|--------|-------|
| Dump scope | Parts, nets, footprint positions, tracks (net, layer, width, endpoints), vias, zones and rule areas, stackup, board thickness, design rules, net classes and net class patterns. UUID-free and sorted, coordinates rounded to 1 um. | run |
| Negative tests (pytest, 10 tests) | A changed net, value, footprint swap, track edit, via edit, zone edit, design-rule edit, net-class edit and stackup edit each change the dump. An unchanged board gives an identical dump. All pass. | run |
| Router determinism | Freerouting gives different tracks and vias in two runs with the same input and the same final score (301 against 318 tracks, 6 against 11 vias in one pair). The router is not deterministic. | run |
| Stored routing session | The session of one run is stored as `expected/routed.ses`. Importing it into a freshly generated board reproduces the committed dump exactly, and KiCad DRC on the result reports 0 violations, 0 unconnected, 0 parity issues. The gate runs without the Freerouting jar. | run |
| Gate failure path | The script exits non-zero if DRC has violations, a dump differs from the committed one, or the stored session is missing. The failing branch was not exercised by a deliberate tamper test. | run (pass path), not run (fail path) |
| `pcbnew` Python interface | `import pcbnew` prints a deprecation warning: "The SWIG-based Python interface to the PCB editor is deprecated and will be removed in a future version of KiCad. Please plan to move to the new IPC API and/or make use of the kicad-cli tool." The generator and the dump use this interface (footprint load, board build, DSN and SES import). The IPC API was not evaluated. Under Python 3.14 the SWIG iterators for tracks and drawings also fail (`GetTracks`, `GetDrawings`), so the dump reads tracks from the board file text. | run |
| CI | Nothing of this runs in CI yet. | not run |

Status against gate G1 of ADR-0012: (c) is met on the stand-in for the dump scope above, with the routed copper restored from the stored session. The routing itself is reproducible only through the stored session.
