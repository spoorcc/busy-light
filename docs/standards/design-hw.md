# Hardware Design Standard (KiCad / PCB) -- DFx

- **Status:** Draft

References (informative): IPC-2221/2222 (design), IPC-7351 (land patterns), IPC-A-600/610 (acceptability),
IPC-7711/7721 (rework), IPC-D-356 (netlist test), IEC 62368-1 (safety), IEC 61000 series (EMC), RoHS/REACH.

## 1. Design for Testability (DFT) -- mandatory
- Programming/debug access (SWD/JTAG) on every board revision, reachable in the **enclosed** product or via fixture; pogo-pin footprint option.
- Test points on all power rails, key signals, reset, boot-mode, and communication lines; >= 1.0 mm pad, labelled on silkscreen, on one side for fixture access, 2.54 mm grid where possible.
- Ability to power-cycle, isolate, and measure current per rail (0 ohm links / sense resistors where justified).
- Production test strategy defined **before layout** (ICT / flying probe / functional test) with a `TC-nnn` per check; self-test and manufacturing-test firmware mode specified as SW requirements.
- Unique identification: serial number, board revision readable by firmware (strap resistors / ID EEPROM) -- supports auditability.

## 2. Design for Manufacturing & Assembly (DFM/DFA)
- Design to the chosen fab's **published capabilities** (record fab + stackup in `hw/fabrication/README`); stay >= 20 % inside minimum limits.
- IPC-7351 land patterns, verified against datasheet (second-person check recorded); 3D models attached.
- Fiducials, panelisation/depaneling plan, tooling holes, keep-outs for pick-and-place; single-side SMT preferred; consistent component orientation; polarity and pin-1 marking.
- Minimise unique parts and package types; avoid parts that need special processes (BGA, hand-solder) without justification.
- Silkscreen: board name, revision, date code area, reference designators legible, no silk on pads.

## 3. Design for Reliability & Safety (DFR)
- Component derating (voltage <= 80 %, power <= 50-60 % of ratings; document exceptions); worst-case and thermal analysis.
- Protection: reverse polarity, over-current, over-voltage, ESD (IEC 61000-4-2) at every external interface.
- Power-up sequencing, brown-out, reset behaviour analysed; defined fail-safe states; LED drive current limits and thermal derating (photobiological safety considered).
- Creepage/clearance per applicable safety standard if mains/high voltage involved (otherwise state "SELV only").

## 4. Design for EMC / Compliance (DFEMC)
- Solid return paths, continuous reference plane where possible, decoupling per IC guidance, controlled loop areas, filtering on interfaces.
- Pre-compliance plan (near-field probing, conducted/radiated scan) in the verification plan; regulatory scope (CE/FCC, radio module certification) stated in SYS requirements.

## 4a. Regulatory design rules (CE) -- see `docs/regulatory/`
- Decide power source early: **SELV-only (e.g. USB-C) or certified external PSU** avoids mains design; mains inside the product brings LVD/EN 62368-1/EN 60598-1 creepage, clearance, insulation, fusing, flammability.
- EMC by design: pre-compliance plan, ESD/EFT/surge protection at ports, filtering, return paths, spread-spectrum/slew control for LED drivers, switching regulator layout. Keep margin >= 6 dB to limits in pre-scan.
- Radio: prefer pre-certified module with documented antenna/layout constraints (keep-outs, ground plane); retain grants/certificates in the technical file.
- Debug ports: secure or disable in production (CRA); document test-access trade-off with DFT.
- Labelling space reserved on PCB/enclosure for type/serial/rev; RoHS/REACH material declarations per BOM line; SVHC tracking.
- Photobiological safety of LEDs (EN 62471) assessed and limited by design (current, optics, diffuser).

## 5. Design for Cost / Supply chain (DFC)
- Every BOM line: MPN, manufacturer, lifecycle status (not NRND/EOL), >= 2 sources or a recorded risk acceptance (`RISK-nnn`), alternates listed.
- RoHS/REACH status recorded; open-source-friendly, widely available parts preferred.

## 6. Design for Serviceability / Repair (DFS)
- Accessible connectors, socketed/ replaceable parts where justified, documented rework notes, no hidden single-use fasteners on the PCB.

## 7. Design process and quality gates
- Schematic: hierarchical, ERC clean (zero unexplained warnings), net names meaningful, notes for non-obvious choices referencing `HW-nnn`/`ADR`.
- Layout: DRC clean with fab rules loaded; length/impedance rules where relevant; peer review of schematic **before** layout and of layout **before** release.
- Release package per revision `hw/fabrication/<rev>/`: Gerbers, drill, BOM, PnP, schematic PDF, ERC/DRC reports, STEP, assembly drawing, checksums.
- Bring-up plan and first-article inspection recorded in `docs/verification/reports/`.
- Libraries: project-local symbols/footprints in `hw/kicad/libs/`, each part with datasheet link, MPN, lifecycle fields.

## 7a. Automated rule checks
`scripts/check_hw_compliance.py` checks rules of sections 1, 2, 4a and 5 on every change (catalogue `docs/regulatory/automated-checks.md`):
clamp on every external interface net, test points on rails and reset/boot, board name and revision on the silkscreen, MPN and
manufacturer per BOM part, RoHS/REACH register entries, lifecycle, and a debug-access inventory. Board settings and waivers:
`hw/compliance/boards.yaml`; materials register: `hw/compliance/materials.yaml`.

## 8. Review checklist (use in `design-review`)
DFT hooks present? Test coverage by TC? Fab limits respected? Footprints verified? Derating done? Protection at interfaces?
Second sources? ERC/DRC clean? Revision/serial identifiable? Mechanical fit checked against STEP (see mechanical standard)?
