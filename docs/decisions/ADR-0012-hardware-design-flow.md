# ADR-0012: Hardware design flow (generated from code or drawn in the KiCad GUI)

- **Status:** Proposed (only the owner sets Accepted)
- **Date:** 2026-11-04
- **Deciders / reviewers:** Ben Spoor (owner); goldfish review RV-003 (comprehension plus two antagonistic reviews, findings resolved in this text)
- **Related:** RV-003, RISK-032, RISK-033, RISK-034, HW-001, HW-010, MECH-001, ADR-0003, ADR-0010, ADR-0011; `docs/standards/design-hw.md`, `docs/standards/design-mech.md`; CLAUDE.md rule 12

## Context and problem
Owner goal (2026-11-04): the AI assistant does as much CAD work as possible, in a formal, professional way.
CLAUDE.md rule 12 forbids hand-editing `.kicad_*` files and says the owner makes CAD changes. Taken literally, the assistant could only write specifications.
KiCad 10.0.6 and ngspice 47 are installed on the development machine (checked 2026-11-04). No HW requirement is Approved (rule 1).
A feasibility spike ran on branch `spike/hw-kicad` (`docs/verification/reports/spike-hw-kicad-pipeline.md`, Draft).

What the flow must give: files that a reviewer can diff, a link from every part and net to a HW requirement, one source for dimensions shared with the housing (ring diameter, outline, USB-C position, antenna keep-out), and checks that run from a script (ERC, DRC, BOM).
Shown by the spike (2026-11-04): SKiDL 3.0.0 (latest release) writes a netlist and a KiCad 9 format schematic that KiCad 10 opens; `pcbnew` Python builds outline, ring placement and nets; `kicad-cli` runs ERC, DRC, BOM and the exports. The spike output was not reproducible byte for byte (SKiDL placement and UUIDs, `pcbnew` footprint order); with fixed tags and `PYTHONHASHSEED=0` the SKiDL netlist was identical over two runs except for the source path and date, but its schematic placement still differed (spike report, section 6).
Not known: whether scripted placement and routing reach the layout quality needed near the antenna and the USB-C input (ADR-0011 keep-out, RISK-031); how stable the KiCad scripting interface is between major versions; whether routing reaches a clean DRC with defined rules (Freerouting 2.5.0 left 3 of 53 connections unrouted on the stand-in with no design rules defined, spike report section 7); whether a schematic that a person can review comfortably can be generated (the SKiDL placement is not reproducible; round 2 of the spike answered this for the stand-in circuit: an own `kiutils` writer gives an ERC-clean, byte-reproducible schematic when it writes KiCad 8 syntax).

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

Gates, applied before scoring (pass or fail, not weighted): an alternative must keep the antenna, USB-C and ESD layout reviewable against numeric rules (RED, `docs/regulatory/`), and its tools must be pinned and qualified (CRA, process rule 7). B and C pass these gates only with the conditions in items 3, 4 and 9.

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

Not evaluated: other code-based tools than the ones in the spike and the KiCad IPC API. The scripting-interface stability named under "Not known" is a risk of B and C alike; the mitigation is the pinned version in item 4 and the fixture in item 11.

## Comparison
Scores 0 to 5, my judgement, updated after the spike and RV-003. Evidence: schematic, netlist, BOM, placement, checks and a FreeCAD fit check were run on a stand-in; Freerouting routed all but 3 of 53 connections; no RF evidence exists, so the layout-quality scores remain guesses. "One source with mechanics" was lowered for B (5 to 3) and C (4 to 3), because the housing script does not yet read the parameter file (today a consistency check only).

| Criterion (weight) | A | B | C |
|--------------------|---|---|---|
| Assistant does the work (5) | 1 | 5 | 3 |
| Reproducible and traceable (5) | 3 | 5 | 4 |
| Layout quality (4) | 5 | 3 | 5 |
| One source with mechanics (3) | 2 | 3 | 3 |
| Tool maturity (3) | 5 | 3 | 4 |
| Owner review effort (3) | 2 | 3 | 3 |
| Survives a tool change (2) | 5 | 3 | 4 |
| **Weighted sum (max 125)** | 77 | 95 | 93 |

B leads C by 2 points, which is inside my scoring error. Sensitivity (recomputed): layout quality of B 3 to 2 gives B 91 against C 93; tool maturity and tool-change survival of B each lowered by one more gives B 86. The ranking of B over C is therefore not robust, and the decision rests on the owner goal (weight 5) and on the reproducibility rows. That is stated here so that it is not mistaken for an evidence-based win.

## Decision
Choose **B** for schematic, netlist, outline, placement, checks and exports, with C as the defined fallback for layout. **Do not accept before gate G1 of item 9 passes** (recommendation; the owner decides).
1. **Source of truth:** generator code and a shared parameter file under `hw/kicad/src/`. There is one connectivity source: the own deterministic schematic writer (`kiutils`). The netlist is exported from that schematic by `kicad-cli`. SKiDL is not used (the spike showed its placement is not reproducible and a second generator could drift); it is removed from the tool environment. Generated `.kicad_*` files are committed because reviewers must open them. This is a recorded exception to "do not commit build output" (CLAUDE.md rule 12), because the board files are deliverables. Every generated file carries a "GENERATED, DO NOT EDIT" marker and the generator commit in its title block. Hand-maintained files (project file, library tables, design rules, waiver file) are listed in `hw/kicad/README` and are reviewed by hand.
2. **Traceability:** every part carries a `HW_REQ` field. Nets are traced through a mapping file `hw/kicad/src/nets.toml` (net, HW IDs). A script checks that every ID exists and is `Approved` in `docs/requirements`, and that every HW requirement with a design effect has at least one part or net.
3. **Checks run from scripts** in CI and locally; results are stored in `hw/sim/` and `docs/verification/`: ERC, DRC with schematic parity, BOM, 3D STEP for the FreeCAD interference check, rendered schematic (readable PDF sheets) and layout images, and an ngspice flow from the generated schematic (not evidenced yet; ngspice was not run in the spike). **Acceptance** is zero unwaived ERC and DRC violations and zero parity issues, against **defined design rules** (net classes, track width for the LED and USB-C current, clearances, stackup of 1.6 mm). Waivers live in `hw/kicad/waivers.toml` (rule, reference, rationale, approver = owner) and the checker fails on a waiver without an entry. The antenna keep-out of the module vendor and ADR-0011 is a KiCad rule area, enforced by DRC and passed to the router. A check that was not run is stated as not run.
4. **Libraries and tools are pinned and qualified.** KiCad 10.0.6 (installed and tested on 2026-11-04). The CI image is pinned by digest, Python packages by exact version and hash (`--require-hashes`), apt packages by version or replaced by a pinned image, and CI fails if `kicad-cli version` differs from the recorded pin. Project-local symbols and footprints are copied into `hw/kicad/libs/` and reviewed against the datasheets (USB-C receptacle, ESP32-C3 module, ESD part, current-limit part); stock libraries are not used for those parts. A tool-qualification table (tool, version, hash, licence, maintainer activity, whether it can change the product) is kept in the technical file and the build tools enter the SBOM. If Freerouting is used: version 2.5.0, jar pinned by hash in the repository or cache (not downloaded unchecked in CI), and a pinned Java runtime. A Freerouting digest published next to the artefact proves little; the hash is checked against a second source when the pin is made. The pins are completed before the ADR is accepted, not "when the first file is generated".
5. **Review:** goldfish review of the generator diff, plus a human review set signed by the owner: a rendered schematic (PDF), a checklist-based review of the netlist against the datasheets (power path, USB-C CC and ESD, boot straps, antenna, current limit), and the layout in the KiCad viewer. Viewer review is not RF evidence. On the first board: range test and a pre-compliance radiated emission scan, filed in the technical file (`regulatory-check`, RED articles 3.1b and 3.2). A generated-file edit is detected by the regeneration gate (item 11).
6. **Fallback to C:** triggered when, with defined design rules, the router leaves any connection unrouted or any unwaived DRC violation, or the layout review checklist fails. The owner routes in the GUI. That state is recorded as `DEV-nnn`; the GUI file becomes the source for the layout and the schematic stays generated. After the hand-over the parameter link to FreeCAD is kept by the fit check (item 10), not by regeneration.
7. **Rule 12 wording (proposed, applied only after the owner accepts this ADR):** "Never hand-edit generated `.kicad_*` files. Change the generator source under `hw/kicad/src/` and regenerate. A GUI edit needs a `DEV-nnn` record (ADR-0012). `.FCStd` files are never hand-edited; FreeCAD changes are made by the owner unless a generator exists under `mech/freecad/`." FreeCAD generation was not evaluated in the spike; the second sentence keeps the human gate for it.
8. **Prerequisites:** KiCad and ngspice are installed (done 2026-11-04); HW requirements Approved (rule 1); the owner decides the open items (current-limit part, cap value, antenna topology of ADR-0003, which sets the keep-out in the parameter file).
9. **Gates.** **G1, before the ADR is accepted and before any product file is generated**, on the stand-in with numeric criteria: (a) ERC 0, parity 0, DRC 0 unwaived with defined design rules; (b) 100 percent of connections routed; (c) two runs give identical dumps including tracks, vias and zones (item 11); (d) the Freerouting steps run from a script in CI. **Status 2026-11-04 (spike report section 8):** on the stand-in with the pegs moved to 15, 150 and 285 degrees, (a) is met (ERC 0, parity 0, DRC 0), (b) is met (0 of 53 unrouted), (d) is met locally (scripted, jar hash checked), and (c) is not met (the dump does not yet cover tracks, vias and zones). With the housing peg azimuths of 30, 150 and 270 degrees, (a) and (b) are not met: the mounting holes fall on the pads of LED D2 and D13. That is a housing or LED-count decision for the owner. **G2, on the first product board:** the same criteria on the real design, the review set of item 5, and the fit check of item 10 with zero unexplained interference. If G1(a) fails for the schematic, the schematic is drawn in the GUI (variant of C, `DEV-nnn`).
10. **Board and housing are checked together:** the KiCad STEP export is imported into FreeCAD and checked against the housing STEP files. Allowed interference is 0 mm3 except declared contact surfaces (board on the posts); the minimum clearance to the lid is a number set by MECH requirements. Today the shared parameter file is read only by the KiCad scripts; the housing script is compared with it (consistency check). The spike found a board stackup of 1.51 mm against 1.6 mm (stackup must be defined explicitly) and one overlap of 3.378 mm3 at azimuth 90 degrees near a housing notch (cause not verified); both are open.
11. **Reproducibility is defined as semantic equality and regeneration is a CI gate.** A script dumps parts, values, footprints, nets, tracks (net, layer, width, endpoints), vias, zones, rule areas, stackup, design rules and net classes per object, UUID-free and sorted, and CI fails if the dump of a regenerated design differs from the committed one. Negative tests: a changed net, value, footprint swap, track edit and a changed design rule must each fail. The routed result (the `.ses` session) is stored as a reviewed input and is not regenerated on every build, because the router result depends on its version and on search; a placement change therefore requires a new routing run and a diff review of the RF-critical nets. The stand-in board stays in the repository as a regression fixture for KiCad upgrades.
12. **Tool change procedure:** a KiCad or dependency upgrade must regenerate a semantically identical board. If it does not, it is a new board revision under change control with a regulatory re-check. Python and Java versions in CI and in the development environment are aligned before G1.

## Consequences
- Positive: the assistant can author schematic, placement, checks and BOM; one parameter source removes hand-copied dimensions; reviews are code diffs.
- **Negative / trade-offs accepted:** routing quality may need the fallback; generator code is itself code and needs tests (rule 6); a discipline rule (no GUI edits) must be enforced; scripting interface changes can force generator updates on a KiCad upgrade.
- New risks (registered as RISK-032, RISK-033, RISK-034): generated layout fails RF or EMC review late; generator tools compromised or abandoned; generated and committed files drift apart (GUI edit), KiCad or library upgrade changes the output.
- Requirements created or changed: none now (the `nets.toml` mapping, design rules and waiver file need HW requirements before use); HW requirements are drafted before any generator code. `design-hw.md` and `design-mech.md` need an update after acceptance.

## Verification and revisit
- Gates G1 and G2 of item 9, with the numeric criteria there. Metric for the owner goal: the share of design artefacts generated (schematic, netlist, outline, placement, routing input, checks, exports) is reported at each gate.
- Interference and clearance check of item 10 in CI, with the numbers of item 10.
- Revisit when: G1 fails after two attempts (switch to C for layout), the KiCad scripting interface changes incompatibly, a tool in the qualification table is abandoned, or the owner prefers the GUI.

## Critical review notes
Strongest objection: "Generated layout of a Wi-Fi and USB board will be worse than a hand layout, and the risk lands on the antenna, which is a compliance matter (RED)."
Answer: valid, and RV-003 rated it High. The keep-out is a DRC-enforced rule area passed to the router (item 3), a pre-compliance scan and range test are required on the first board (item 5), and item 6 gives a recorded way out with a numeric trigger. The first board is a 10-unit internal prototype, so the cost of finding this out is low.
Second objection: "This rewrites rule 12 so that the assistant can do more; the rule existed to keep a human on the CAD." Answer: the human review points (item 5) and the Accepted status remain with the owner; only the authoring moves to code.

Third objection (RV-003): "The decision is scored toward the owner goal and the lead over C is inside the error." Answer: accepted and stated in the comparison; the gates (item 9) make acceptance depend on evidence, not on the score.
