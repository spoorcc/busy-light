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
| Net names | `pcbnew` net names carry a `/` prefix (`/GND`); scripts must account for it. | run |
| ngspice, FreeCAD side of the parameter file, Docker run of the CI image | Not run. | not run |

Conclusion of round 2: the schematic path (ERC-clean, reproducible, traceable fields) is feasible with an own writer on KiCad 8 syntax. The routing path is not shown. A real router (Freerouting) or a rule-based router is needed; this is the main remaining risk of ADR-0012 option B. The KiCad 8 syntax dependency (kiutils) is a pin risk: KiCad 10 upgrades the file on first save in the GUI.
