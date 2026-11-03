# Mechanical Requirements

- **Status:** Draft
- **Version:** 0.1
- **Owner:**

Entries use IDs `MECH-nnn` and follow `docs/templates/requirement.md`.
Process rules: `docs/process/README.md`.

### MECH-001 Housing size

- **Statement:** The printed housing with the board fitted shall have a largest outer dimension from 48 mm to 58 mm.
- **Rationale:** SYS-028: size between a table-tennis ball and a tennis ball.
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

- **Statement:** The housing shall keep the antenna area of the module free of metal, conductive filament and metallised paint, to the distance given in ADR-0003.
- **Rationale:** RISK-011: detuning of the antenna by nearby conductive material.
- **Parent:** SYS-038
- **Acceptance criteria:** The housing drawing shows the clearance; the range test of SYS-038 passes with the finished housing.
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

- **Statement:** The housing shall have a flat area of at least [20] x [20] mm for the unit label (identifier, passphrase, QR code) and the "prototype, not for sale" mark, which a user can read and which is not hidden when the unit stands on a desk.
- **Rationale:** ADR-0006 puts the passphrase on a label. Regulatory labelling is a tight fit on a 53 mm housing (AS4).
- **Parent:** SYS-013
- **Acceptance criteria:** The drawing shows the area. A printed label of the stated size fits and stays readable after [100] cycles of opening and closing the housing. The label sits on a part that does not move when the housing opens.
- **Verification method:** Inspection
- **Verified by:** TC-306
- **Category:** Usability
- **Regulatory:** none
- **Priority:** Should
- **Status:** Draft

