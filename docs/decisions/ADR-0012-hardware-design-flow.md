# ADR-0012: Hardware design flow (generated from code or drawn in the KiCad GUI)

- **Status:** Proposed (only the owner sets Accepted)
- **Date:** 2026-11-04
- **Deciders / reviewers:** Ben Spoor (owner); no goldfish review yet
- **Related:** HW-001, HW-010, MECH-001, ADR-0003, ADR-0010, ADR-0011; `docs/standards/design-hw.md`, `docs/standards/design-mech.md`; CLAUDE.md rule 12

## Context and problem
Owner goal (2026-11-04): the AI assistant does as much CAD work as possible, in a formal, professional way.
CLAUDE.md rule 12 forbids hand-editing `.kicad_*` files and says the owner makes CAD changes. Taken literally, the assistant could only write specifications.
KiCad 10.0.6 and ngspice 47 are installed on the development machine (checked 2026-11-04). No HW requirement is Approved (rule 1).
A feasibility spike ran on branch `spike/hw-kicad` (`docs/verification/reports/spike-hw-kicad-pipeline.md`, Draft).

What the flow must give: files that a reviewer can diff, a link from every part and net to a HW requirement, one source for dimensions shared with the housing (ring diameter, outline, USB-C position, antenna keep-out), and checks that run from a script (ERC, DRC, BOM).
Shown by the spike (2026-11-04): SKiDL 3.0.0 (latest release) writes a netlist and a KiCad 9 format schematic that KiCad 10 opens; `pcbnew` Python builds outline, ring placement and nets; `kicad-cli` runs ERC, DRC, BOM and the exports. The spike output was not reproducible byte for byte (SKiDL placement and UUIDs, `pcbnew` footprint order); with fixed tags and `PYTHONHASHSEED=0` the SKiDL netlist was reproducible except for the source path and date.
Not known: whether scripted placement and routing reach the layout quality needed near the antenna and the USB-C input (ADR-0011 keep-out, RISK-031); how stable the KiCad scripting interface is between major versions; whether routing can be scripted (not tried; Freerouting is not installed); whether a schematic that a person can review comfortably can be generated (the SKiDL placement is not reproducible; round 2 of the spike answered this for the stand-in circuit: an own `kiutils` writer gives an ERC-clean, byte-reproducible schematic when it writes KiCad 8 syntax).

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| The assistant can do the work (owner goal) | 5 | owner goal 2026-11-04 |
| Reproducible, diffable, traceable to HW IDs | 5 | process rules 10, 11 |
| Layout quality (RF, USB-C, ESD) | 4 | HW-001, SYS-022 |
| One source with the mechanical parameters | 3 | MECH-001, ADR-0011 |
| Tool maturity and pin risk | 3 | process rule 5 |
| Owner review effort | 3 | process rule 3 |
| Survives a tool change | 2 | CRA support period (5 years) |

## Alternatives considered

### A. Owner draws in the KiCad GUI; the assistant writes specs and checks (status quo of rule 12)
Strongest case: best layout quality and the most mature workflow; no scripting risk; the owner keeps full control.
Cons: the assistant does little of the CAD work (fails the owner goal); dimensions are copied by hand between KiCad and FreeCAD; review is of binary-like files.

### B. Generated from code; no GUI edits
Schematic from Python source (SKiDL or a small in-repo generator), board outline, ring placement and keep-outs from a shared parameter file, routing by script or an autorouter import. `kicad-cli` runs ERC, DRC, BOM and renders. Every change goes through the generator.
Strongest case: fully reproducible and reviewable as a code diff; the assistant does nearly all of the work; one parameter file feeds KiCad and FreeCAD.
Cons: routing and RF-sensitive layout are the weak point; strict discipline is needed so that files do not drift from the code; scripting interfaces change between KiCad versions.

### C. Hybrid: generated schematic, outline and placement; the owner routes in the GUI; the GUI file then becomes the source
Strongest case: best layout quality with a large share of assisted work.
Cons: after the hand-over, the generator no longer reproduces the board, so reproducibility is lost for the layout and parameter changes need manual rework.

### D. Do nothing / defer
Not possible without blocking the schematic.

## Comparison
Scores 0 to 5, my judgement. The spike confirmed feasibility for schematic, netlist, BOM, placement and checks; it gave no evidence on routing, so the layout-quality scores are unchanged guesses.

| Criterion (weight) | A | B | C |
|--------------------|---|---|---|
| Assistant does the work (5) | 1 | 5 | 3 |
| Reproducible and traceable (5) | 3 | 5 | 4 |
| Layout quality (4) | 5 | 3 | 5 |
| One source with mechanics (3) | 2 | 5 | 4 |
| Tool maturity (3) | 5 | 3 | 4 |
| Owner review effort (3) | 2 | 3 | 3 |
| Survives a tool change (2) | 5 | 3 | 4 |
| **Weighted sum (max 125)** | 77 | 101 | 96 |

B leads C by 5 points, which is inside my scoring error. The decision rests on the owner goal and on the reproducibility rows.

## Decision
Choose **B**, with C as the defined fallback.
1. **Source of truth:** generator code (SKiDL for the netlist; the schematic sheets by an own deterministic writer, to be proven in the routing and schematic spike of item 9) and a shared parameter file under `hw/kicad/src/` (to create after the HW requirements are Approved). Generated `.kicad_*` files are committed so reviewers can open them, but they are outputs. Nobody edits them, in the GUI or in a text editor.
2. **Every part and net** carries its HW requirement ID as a field; a script checks that no part lacks one (extends `check_traceability.py`).
3. **Checks run from scripts** and results are stored in `hw/sim/` and `docs/verification/`: ERC and DRC with zero unwaived violations, BOM export, 3D STEP export for the interference check in FreeCAD (`docs/standards/design-mech.md`), and rendered schematic and layout images for review. A check that was not run is stated as not run.
4. **Libraries and tools are pinned:** KiCad 10.0.6 (installed and tested on 2026-11-04; CI uses the `kicad/kicad:10.0` image), the symbol and footprint library commit, and the generator dependencies. The pin is recorded in `hw/kicad/README` when the first file is generated.
5. **Human review:** a goldfish review of the generator diff and the rendered output, plus a visual check by the owner of the antenna area, USB-C and ESD routing in the KiCad viewer. Only the owner approves.
6. **Fallback to C:** if scripted routing fails DRC or the RF and USB layout review for the first board, the owner routes in the GUI. That state is recorded as `DEV-nnn`, the GUI file becomes the source for the layout, and the schematic stays generated.
7. **Rule 12 wording (proposed, applied only after the owner accepts this ADR):** "Never hand-edit generated `.kicad_*` or `.FCStd` files. Change the generator source under `hw/kicad/src/` or `mech/freecad/` and regenerate. A GUI edit needs a `DEV-nnn` record (ADR-0012)."
8. **Prerequisites:** KiCad and ngspice are installed (done 2026-11-04); HW requirements Approved (rule 1); the owner decides the open items (current-limit part, cap value).
9. **Conditions before the first product file is generated:** (a) a reproducible schematic writer whose output KiCad 10 loads and that is ERC-clean: **shown for a stand-in circuit** on 2026-11-04 (KiCad 8 syntax, `kiutils` 1.4.8; spike report section 6), still to be repeated on the real design; and (b) routing of a stand-in board by script or by Freerouting that passes DRC: **not shown**. A naive scripted router connected all nets but gave 16 shorts and 10 crossing tracks. Freerouting or a rule-based router is the open spike. If (a) fails, the schematic is drawn by the owner or assistant in the GUI and only netlist, placement and checks stay generated (a variant of C, `DEV-nnn`). If (b) fails, item 6 applies.
10. **Reproducibility is defined as semantic equality:** a script dumps parts, values, footprints, nets and positions per reference designator from the generated files and compares the dump with the committed one. Generated files are not compared byte for byte, because UUIDs and file order may vary. Generators use fixed reference designators and `uuid5` identifiers. The check was run on the stand-in circuit: schematic bytes and the semantic dump were identical over two runs, and negative tests showed that a missing requirement field and a moved footprint are detected.

## Consequences
- Positive: the assistant can author schematic, placement, checks and BOM; one parameter source removes hand-copied dimensions; reviews are code diffs.
- **Negative / trade-offs accepted:** routing quality may need the fallback; generator code is itself code and needs tests (rule 6); a discipline rule (no GUI edits) must be enforced; scripting interface changes can force generator updates on a KiCad upgrade.
- New risks (to add to risk register): generated layout fails RF or EMC review late; generator and committed files drift apart; KiCad or library upgrade changes the output.
- Requirements created or changed: none now; HW requirements are drafted before any generator code. `design-hw.md` and `design-mech.md` need an update after acceptance.

## Verification and revisit
- First generated board passes `kicad-cli` ERC and DRC; the semantic dump of a regenerated design equals the committed dump (item 10, check in a script).
- Interference check against the FreeCAD housing runs from the shared parameter file.
- Revisit when: scripted routing fails the first-board review (switch to C), the KiCad scripting interface changes incompatibly, or the owner prefers the GUI.

## Critical review notes
Strongest objection: "Generated layout of a Wi-Fi and USB board will be worse than a hand layout, and the risk lands on the antenna, which is a compliance matter (RED)."
Answer: valid. The placement and keep-outs near the antenna are fixed by the parameter file and checked by the owner in the viewer, and item 6 gives a recorded way out. The first board is a 10-unit internal prototype, so the cost of finding this out is low.
Second objection: "This rewrites rule 12 so that the assistant can do more; the rule existed to keep a human on the CAD." Answer: the human review points (item 5) and the Accepted status remain with the owner; only the authoring moves to code.
