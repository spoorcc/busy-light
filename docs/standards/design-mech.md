# Mechanical Design Standard (FreeCAD) -- DFx

- **Status:** Draft

References (informative): ISO 1101 / ASME Y14.5 (GD&T), ISO 286 (limits and fits), ISO 2768 (general tolerances),
IEC 60529 (IP rating), UL 94 (flammability), RoHS/REACH.

## 1. Process-driven design (DFM)
- Select the manufacturing process **per ADR** (FDM, SLA, SLS, injection moulding, CNC...) before detailed design; rules follow the process:
  - 3D printing: min wall/feature sizes, overhang/support strategy, orientation, shrinkage compensation, test coupons for fits.
  - Injection moulding: uniform walls, draft angles, no undercuts without slides, ribs/bosses ratios, gate/ejector marks.
- Every dimension that matters has a tolerance; default general tolerance stated (e.g. ISO 2768-m). Critical fits identified and analysed.
- Material specified (grade, colour, UV/thermal/flammability) with datasheet; RoHS compliance recorded.

## 2. Design for Assembly (DFA)
- Minimise part count and fastener types; prefer snap-fits/screws into bosses over adhesive; self-locating, poka-yoke (cannot assemble wrongly); assemble from one direction; tool access clearances modelled.
- Fastener standard: ISO metric, thread-forming or heat-set inserts specified with hole sizes and torque.

## 3. Design for Testability (DFT)
- Programming/debug port and test points reachable **without destroying** the enclosure, or via defined fixture openings; fixture/jig concept documented.
- Light path (indicator) verifiable optically: defined diffuser/lens geometry, luminous uniformity and visibility requirement with measurement method (`TC-nnn`).
- Dimensional inspection plan for critical features (what, tool, frequency); first-article inspection recorded.

## 4. Design for Serviceability, Reliability & Sustainability
- Reopenable enclosure, replaceable parts, no permanent bonding without justification; strain relief for cables; material creep/fatigue considered for snap-fits; thermal expansion and temperature limits stated.
- Environmental targets (IP rating, drop, temperature) are SYS requirements, each verified by test or analysis.
- Recyclability/marking of plastics; part numbers and revision permanently marked for traceability.

## 5. Thermal, EMC & optical
- Heat path from LEDs/regulators to ambient analysed; vent/heatsink needs justified.
- Conductive/shielding features coordinated with hardware; antenna keep-out zones (if radio) enforced in both CAD domains.
- Optical: LED position vs diffuser distance, colour/brightness uniformity, ambient-light visibility.

## 5a. Regulatory design rules (CE) -- see `docs/regulatory/`
Flammability class of enclosure/materials (UL 94 V-x or EN 60695 as applicable); ingress/IP claims verified by test; accessible parts temperature limits;
no accessible hazardous parts; label area and legibility/durability for rating/CE/WEEE/type-serial markings; RoHS/REACH material declarations;
user/installation instructions consistent with the mechanical design; plastic marking for recycling (ISO 11469 / 1043) where applicable.

## 6. ECAD/MCAD integration
- Board outline and mounting holes derived from one controlled source; KiCad exports **STEP**, imported in FreeCAD for interference and clearance check each revision; result recorded.
- Connector, button, LED, and port positions have named datum references; tolerance stack-up (worst-case and RSS) for PCB-to-enclosure alignment documented.

## 7. CAD practice (auditability)
- Parametric models: key dimensions in a spreadsheet/named parameters, no magic numbers; clear body/part naming; one part per file or documented assembly structure.
- Release package `mech/exports/<rev>/`: STEP, STL (or process-specific), 2D drawings with tolerances/materials/revision, BOM with hardware (fasteners), checksums.
- `.FCStd` is binary: commit only at meaningful states with a message citing `MECH-nnn`; exports are the review artefacts.

## 8. Review checklist (use in `design-review`)
Process chosen by ADR and rules applied? Tolerances and fits analysed? Assembly order and tool access verified? Test/programming
access without destruction? Serviceable? Material data + flammability? Thermal path? STEP interference check against current PCB?
Marking/traceability? Drawings complete? Each MECH requirement has a verification?
