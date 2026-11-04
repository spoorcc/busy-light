# Mechanical Requirements

- **Status:** Draft
- **Version:** 0.1
- **Owner:**

Entries use IDs `MECH-nnn` and follow `docs/templates/requirement.md`.
Process rules: `docs/process/README.md`.

### MECH-001 Housing size

- **Statement:** The printed housing with the board fitted shall have a largest outer dimension from 48 mm to 58 mm.
- **Rationale:** SYS-028: size between a table-tennis ball and a tennis ball. Working value in plan 05: diameter [53.0] mm, height [16.5] mm.
- **Parent:** SYS-028
- **Acceptance criteria:** A caliper measurement of [3] printed housings gives a largest dimension within the range.
- **Verification method:** Test
- **Verified by:** TC-301
- **Category:** Functional
- **Regulatory:** none
- **Priority:** Must
- **Status:** Draft

### MECH-002 Light diffuser

- **Statement:** The housing shall diffuse the light of the 16 LEDs so that no single LED is visible as a point at 1 m and the ring looks like a closed band of colour.
- **Rationale:** SYS-001: the ring is read from desk distance. Points of light make the status harder to read.
- **Parent:** SYS-001
- **Acceptance criteria:** A photo test at 1 m under office light shows no point source; the luminous intensity at 0.5 m of SYS-001 is measured through the diffuser.
- **Verification method:** Test
- **Verified by:** TC-302
- **Category:** Functional
- **Regulatory:** none
- **Priority:** Should
- **Status:** Draft

### MECH-003 Antenna clearance

- **Statement:** The housing shall have only non-conductive plastic inside a box of [15] mm around the antenna area of the module (no metal, magnet, screw, insert, conductive or metallic filament, metallic or conductive paint, metallised label), and its nearest wall shall be at least [15] mm from the antenna edge.
- **Rationale:** RISK-011: detuning of the antenna by nearby conductive material. The vendor guideline (15 mm in all directions) also covers LEDs, tracks and ground near the antenna and the centred module: that is a PCB layout matter, recorded in ADR-0003 and HW-005, not a housing requirement. The 15 mm cannot be met literally in a 53 mm unit (plan 05 section 4.6); the range test decides.
- **Parent:** SYS-038
- **Acceptance criteria:** The housing drawing shows the plastic-only box and the wall distance; the range test of SYS-038 passes with the finished housing.
- **Verification method:** Inspection
- **Verified by:** TC-303
- **Category:** Performance
- **Regulatory:** none
- **Priority:** Must
- **Status:** Draft

### MECH-004 Access to USB-C and button

- **Statement:** The housing shall give access to the USB-C connector with a standard cable and to the button with a finger, without tools.
- **Rationale:** SYS-017 and SYS-020: the user needs both.
- **Parent:** SYS-017, SYS-020
- **Acceptance criteria:** Fit check with [3] common USB-C cables and with a finger on the button in the fitted housing.
- **Verification method:** Demonstration
- **Verified by:** TC-304
- **Category:** Usability
- **Regulatory:** none
- **Priority:** Must
- **Status:** Draft

### MECH-005 Thermal and material

- **Statement:** The housing material shall keep its shape at the highest temperature that the analysis or the measurement gives inside the housing, with a margin of at least [15] K below the material's heat deflection temperature.
- **Rationale:** RISK-005: printed plastic softens near LEDs and the module.
- **Parent:** SYS-020, SYS-028
- **Acceptance criteria:** The measured temperature rise at full limited power in a closed housing at [25] C ambient, plus the highest expected room temperature, stays below the material limit by the margin. The material and its data sheet are named in the drawing.
- **Verification method:** Test
- **Verified by:** TC-305
- **Category:** Safety
- **Regulatory:** EN 62368-1 *(verify)*
- **Priority:** Must
- **Status:** Draft

### MECH-006 Label area

- **Statement:** The housing shall have a flat area of at least [20] x [20] mm on the back of the base, outside the mounting recess of MECH-007, for the unit label (identifier, passphrase, QR code) and the "prototype, not for sale" mark, which an accessory on the back does not cover.
- **Rationale:** ADR-0006 puts the passphrase on a label. Owner decision 2026-11-04: the unit is mounted horizontal and vertical and the label is on the back (assumption A1 of plan 05 is withdrawn). The label stays on the base, which does not move when the lid opens, and never on a swappable accessory. The label is inside the 15 mm antenna box of MECH-003, so it must not be metallised. Regulatory labelling is a tight fit on a 53 mm housing (AS4).
- **Parent:** SYS-013
- **Acceptance criteria:** The drawing shows the label area on the back, outside the recess of MECH-007. A printed label of the stated size fits, is not metallised, and stays readable after a wipe test of [20] cycles and after the heat soak of MECH-005. A locked accessory does not cover the label.
- **Verification method:** Inspection and Test
- **Verified by:** TC-306
- **Category:** Usability
- **Regulatory:** none
- **Priority:** Should
- **Status:** Draft

### MECH-007 Back mounting interface

- **Statement:** The back of the housing shall have a round recess of [30] mm diameter with [3] lugs that takes an accessory (stand, clip or blank plate) by a turn of about [30] degrees, without tools, and shall have no metal, magnet or insert in or on the back.
- **Rationale:** NEED-022 and ADR-0014 (Proposed): a printed bayonet is plastic only, so it respects the antenna box of MECH-003. Whether it fits the 2 mm floor and next to the label is not shown (RV-007 findings G1, G2). A printed thread and a tripod socket were rejected.
- **Parent:** NEED-022
- **Acceptance criteria:** The drawing shows the recess, the lugs and the detent with tolerances. A test accessory fits and locks on [3] printed housings by one hand in under [10] s, and detaches again. No metal part is in the back (inspection).
- **Verification method:** Inspection and Test
- **Verified by:** TC-307
- **Category:** Functional
- **Regulatory:** none
- **Priority:** Should
- **Status:** Draft

### MECH-008 Accessory retention

- **Statement:** An accessory locked to the back shall hold the unit against a pull-off force of at least [10] N, before and after [100] attach and detach cycles and after a heat soak at the highest internal temperature of MECH-005.
- **Rationale:** The unit hangs on a wall clip or stands on an accessory. FDM lugs and detents in warm PETG or ASA can creep (plan 05 section 4.8; no strain limit found). The force value is a working figure that must come from the mass and leverage of the planned accessories.
- **Parent:** NEED-022
- **Acceptance criteria:** On [3] housings, the pull-off force is at least [10] N before the cycles, after [100] cycles, and after the heat soak; no lug is cracked; the accessory does not release by itself in a hanging test of [24] h at the soak temperature.
- **Verification method:** Test
- **Verified by:** TC-308
- **Category:** Safety
- **Regulatory:** none
- **Priority:** Should
- **Status:** Draft
