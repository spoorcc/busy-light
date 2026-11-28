# Mechanical Requirements

- **Status:** Approved (MECH-001 to MECH-009, owner, 2026-11-07, in two steps; bracketed values stay open); MECH-015 is Draft (proposed 2026-11-28, not approved)
- **Version:** 0.2 (2026-11-07, assistant redraft after ADR-0003 and ADR-0011 Accepted, ADR-0014 Proposed, RV-004, RV-007; all entries stay Draft; only the owner approves)
- **Owner:**

Entries use IDs `MECH-nnn` and follow `docs/templates/requirement.md`.
Process rules: `docs/process/README.md`.

### MECH-001 Housing size

- **Statement:** The printed housing with the board fitted, without cable and plug, shall have a largest outer dimension from 48 mm to 65 mm.
- **Rationale:** SYS-028: size between a table-tennis ball and a tennis ball. Working value in plan 05: diameter [53.0] mm, height [16.5] mm (17.45 mm with feet); the values are redone for horizontal and vertical mounting (RV-004 A1). The cable and its plug are excluded (RV-004).
- **Parent:** SYS-028
- **Acceptance criteria:** A caliper measurement of [3] printed housings gives a largest dimension within the range.
- **Verification method:** Test
- **Verified by:** TC-301
- **Category:** Functional
- **Regulatory:** none
- **Priority:** Must
- **Status:** Approved (owner, Ben Spoor, 2026-11-07, in the working session; recorded by the assistant; values in square brackets stay open until measured)
- **Approved amendment (owner, Ben Spoor, 2026-11-22, decision 8 in the working session; recorded by the assistant, `docs/journal/2026-11-22-owner-decisions-p1-rework.md`):** the upper limit is 60 mm (was 58 mm). Reason: with the USB-C connector at the edge of the 46 mm board the housing is 59.24 mm (`placement.json` of board-p1 and of the spike board; RV-016 row 22); the LED ring blocks moving the connector inwards. Still within SYS-028 (smaller than a tennis ball). The placer limit `MAX_DIM_MECH001` follows.
- **Approved amendment (owner, Ben Spoor, 2026-11-27, in the working session: "Raise to 65mm"; recorded by the assistant, `docs/journal/2026-11-27-owner-decision-housing-limit-65.md`):** the upper limit is 65 mm (was 60 mm). Reason: the placement of the 22 rules cannot be met on the 12 mm tab at the USB-C connector (`docs/verification/reports/p1-placement-feasibility.md`); the owner chose a droplet-shaped board nose with more room around J1, and the nose needs length as well as width. 65 mm is 0.4 mm below the smallest ITF tennis ball (65.4 mm), so "smaller than a tennis ball" (SYS-028 rationale) holds with a small margin. The generator guard `MAX_DIM_SPIKE_MM` is the limit minus 0.2 mm (print tolerance). SYS-028 (Draft) carries the same change.

### MECH-002 Light diffuser

- **Statement:** The housing shall diffuse the light of the 16 LEDs so that no single LED is visible as a point at 1 m and the ring looks like a closed band of colour.
- **Rationale:** SYS-001: the ring is read from desk distance. Points of light make the status harder to read. Owner decision 2026-11-07 (ADR-0011): a wide glow or band, not a sharp ring; concept B (opaque base, one translucent lid) is the working concept and concept A is the fallback only if TC-302 fails.
- **Parent:** SYS-001
- **Acceptance criteria:** Coupon test first: lid coupons of [0.8], [1.2] and [1.6] mm over a ring of 16 LEDs at [4], [6] and [8] mm distance; then the finished lid. A photo test at 1 m under office light shows no point source; the luminous intensity at 0.5 m of SYS-001 is measured through the diffuser.
- **Verification method:** Test
- **Verified by:** TC-302
- **Category:** Functional
- **Regulatory:** none
- **Priority:** Should
- **Approved amendment (owner, Ben Spoor, 2026-11-28, in the working session: "Do a split ring ensure by the mechanical design that the edges are sharp"; recorded by the assistant, `docs/journal/2026-11-28-owner-decision-split-ring.md`):** the ring is two arcs separated by two gaps (the USB-C connector in one, the antenna at the board edge in the other), not a closed band, and the ends of the arcs are sharp (MECH-015). The count of LEDs (16 in the statement) is open until the owner chooses it ([24] is the working value of ADR-0027, Proposed). The decision of 2026-11-07 (wide glow along the band, concept B) is read as still valid along each arc; the construction that makes the ends sharp is ADR-0027 (Proposed) and may replace concept B.
- **Status:** Approved (owner, Ben Spoor, 2026-11-07, in the working session; recorded by the assistant; values in square brackets stay open until measured)

### MECH-003 Antenna clearance

- **Statement:** The housing shall have only non-conductive plastic inside a box of [15] mm around the antenna area of the module (no metal, magnet, screw, insert, conductive or metallic filament, metallic or conductive paint, metallised label), and the range test with the finished housing shall show a loss of at most [6] dB against a bare module (the criterion of ADR-0003 spike 7.2). The 15 mm distance from the antenna edge to the nearest wall is a goal, not a pass criterion: it is 14.3 mm at the corners in the working geometry (ADR-0003 finding of 2026-11-04).
- **Rationale:** RISK-011: detuning of the antenna by nearby conductive material. The vendor guideline (15 mm in all directions) also covers LEDs, tracks and ground near the antenna and the centred module: that is a PCB layout matter, recorded in ADR-0003 and HW-005, not a housing requirement. The 15 mm cannot be met literally in a 53 mm unit (plan 05 section 4.6); ADR-0003 (Accepted 2026-11-07) puts the module off-centre toward the rim and lets the spike 7.2 loss decide. DEV-004 covers the keep-out overlap on the PCB spike.
- **Parent:** SYS-038
- **Acceptance criteria:** The housing drawing shows the plastic-only box and the wall distance; the range test of SYS-038 passes with the finished housing, with and without an accessory mounted on the back (RV-007), at three distances.
- **Verification method:** Inspection
- **Verified by:** TC-303
- **Category:** Performance
- **Regulatory:** none
- **Priority:** Must
- **Status:** Approved (owner, Ben Spoor, 2026-11-07, in the working session; recorded by the assistant; values in square brackets stay open until measured)

### MECH-004 Access to USB-C and button

- **Statement:** The housing shall give access to the USB-C connector with a standard cable whose plug overmold fits the Type-C envelope of 12.35 x 6.5 mm, through a window of [14.2] x [8.2] mm, and to the button with a finger, without tools.
- **Rationale:** SYS-017 and SYS-020: the user needs both. Window raised from [14.0] x [8.0] to [14.2] x [8.2] mm by the owner on 2026-11-07: the tolerance check (`mech-housing-first-model.md`) showed zero reserve at worst case with 14.0 x 8.0.
- **Parent:** SYS-017, SYS-020
- **Acceptance criteria:** Fit check with [3] common USB-C cables (including one with an overmolded plug at the envelope limit) and with a finger on the button in the fitted housing, on [3] printed housings; the window is checked at the worst-case tolerance stack (`mech-concept-analysis.md`).
- **Verification method:** Demonstration
- **Verified by:** TC-304
- **Category:** Usability
- **Regulatory:** none
- **Priority:** Must
- **Status:** Approved (owner, Ben Spoor, 2026-11-07, in the working session; recorded by the assistant; values in square brackets stay open until measured)

### MECH-005 Thermal and material

- **Statement:** The housing material (PETG for the prototype, ADR-0011) shall keep its shape at the highest temperature that the analysis or the measurement gives on the housing near the LEDs and the module, with a margin of at least [15] K below the material's heat deflection temperature.
- **Rationale:** RISK-005: printed plastic softens near LEDs and the module.
- **Parent:** SYS-020, SYS-028
- **Acceptance criteria:** The measured temperature at the top current step in the closed housing at [35] C ambient (the run of HW-013 and TC-213, same setup) stays below the heat deflection temperature of the named PETG by the margin; the PETG data (65 to 78 C at 0.45 MPa across brands, ADR-0011 E2) gives a working limit of about [50] C at the housing wall, to be replaced by the data of the actual filament. Orientation: horizontal and vertical. The material and its data sheet are named in the drawing.
- **Verification method:** Test
- **Verified by:** TC-305
- **Category:** Safety
- **Regulatory:** EN 62368-1 *(verify)*
- **Priority:** Must
- **Status:** Approved (owner, Ben Spoor, 2026-11-07, in the working session; recorded by the assistant; values in square brackets stay open until measured)

### MECH-006 Label area

- **Statement:** The housing shall have a flat area of at least [20] x [20] mm on the back of the base, outside the bayonet ring of MECH-007 (in its open centre if ADR-0014 variant V2 is accepted: a circle of [21] mm), for the unit label (identifier, passphrase, QR code) and the "prototype, not for sale" mark, which an accessory on the back does not cover.
- **Rationale:** ADR-0006 puts the passphrase on a label. Owner decision 2026-11-04: the unit is mounted horizontal and vertical and the label is on the back (assumption A1 of plan 05 is withdrawn). The label stays on the base, which does not move when the lid opens, and never on a swappable accessory. The label is inside the 15 mm antenna box of MECH-003, so it must not be metallised. Regulatory labelling is a tight fit on a 53 mm housing (AS4).
- **Parent:** SYS-013
- **Acceptance criteria:** The drawing shows the label area on the back, outside the recess of MECH-007. A printed label of the stated size fits, is not metallised, and stays readable after a wipe test of [20] cycles and after the heat soak of MECH-005. A locked accessory does not cover the label.
- **Verification method:** Inspection and Test
- **Verified by:** TC-306
- **Category:** Usability
- **Regulatory:** none
- **Priority:** Should
- **Status:** Approved (owner, Ben Spoor, 2026-11-07, in the working session, after ADR-0014 was accepted; recorded by the assistant; values in square brackets stay open until the coupon test; [X] N is derived from the heaviest accessory)

### MECH-007 Back mounting interface

- **Statement:** The back of the housing shall have an annular bayonet (ring from radius [16.3] to [21.0] mm, depth [1.2] mm in the 2.0 mm floor, [3] T-shaped lugs of [1.2] mm engagement height behind a lock lip, [3] lock positions) that takes a ring-shaped accessory (stand, clip, rack-mount adapter or blank plate) by a turn of about [30] degrees, with a detent and a release tab, without tools, leaving the centre open, and shall have no metal, magnet or insert in or on the back.
- **Rationale:** NEED-022 and ADR-0014 (Accepted 2026-11-07): a printed bayonet is plastic only, so it respects the antenna box of MECH-003. The annular variant keeps the 21 mm label readable in the open centre (`spike-mech-back-layout.md`, V2); widths are multiples of 0.4 mm (4.4 or 4.8 mm for the ring). The floor skin, print orientation (the recess on the bed side is a bridge), release against a knock and the loads are not shown (RV-007). A printed thread and a tripod socket were rejected. Lock concept confirmed by the owner on 2026-11-07: entry sector, lock sector with a [0.4] mm lip, solid stop (`mech-housing-first-model.md`; `bayonet_geometry.py`).
- **Parent:** NEED-022
- **Acceptance criteria:** The drawing shows the ring, the lugs, the detent and the release tab with tolerances and the print orientation. A test accessory fits and locks on [3] printed housings by one hand in under [10] s, and detaches again; a knock test does not release it. No metal part is in the back (inspection).
- **Verification method:** Inspection and Test
- **Verified by:** TC-307
- **Category:** Functional
- **Regulatory:** none
- **Priority:** Should
- **Status:** Approved (owner, Ben Spoor, 2026-11-07, in the working session, after ADR-0014 was accepted; recorded by the assistant; values in square brackets stay open until the coupon test; [X] N is derived from the heaviest accessory)

### MECH-008 Accessory retention

- **Statement:** An accessory locked to the back shall hold the unit against a pull-off force of at least [X] N (derived from the mass and leverage of the heaviest planned accessory, the rack-mount adapter; the earlier [10] N is withdrawn), before and after [100] attach and detach cycles and after a heat soak at the highest internal temperature of MECH-005.
- **Rationale:** The unit hangs on a wall clip or stands on an accessory. FDM lugs and detents in warm PETG or ASA can creep (plan 05 section 4.8; no strain limit found). The force value is open until it is derived from the heaviest planned accessory; a stand or rack mount loads the lugs in moment and shear (RV-007). PETG creeps when warm (ADR-0014 fallback C, a dovetail, if the coupon fails).
- **Parent:** NEED-022
- **Acceptance criteria:** On [3] housings, the pull-off force is at least [X] N before the cycles, after [100] cycles, and after the heat soak; no lug is cracked; the accessory does not release by itself in a hanging test of [24] h at the soak temperature.
- **Verification method:** Test
- **Verified by:** TC-308
- **Category:** Safety
- **Regulatory:** none
- **Priority:** Should
- **Status:** Approved (owner, Ben Spoor, 2026-11-07, in the working session, after ADR-0014 was accepted; recorded by the assistant; values in square brackets stay open until the coupon test; [X] N is derived from the heaviest accessory)

### MECH-009 PCB retention and reopening

- **Statement:** The housing shall hold the board by snap hooks on the board edge, with no screw through the board and no metal near the antenna zone, and shall open and close [100] times without a broken hook or a loose board.
- **Rationale:** Owner decision 2026-11-07 (ADR-0011 point 7): snap hooks on the board edge, no holes. Metal near the antenna zone detunes it (MECH-003). The unit is opened for programming and repair (HW-006), so reopening has to work; PETG hooks can break (ADR-0011 risk c). The PCB spike outline already carries the notches.
- **Parent:** SYS-028
- **Acceptance criteria:** On [3] printed housings, [100] open and close cycles with no cracked hook; the board does not move by more than [0.3] mm in a shake test; the drawing shows the notches and hooks with tolerances (radial gap D 46 mm to the wall 1.38 mm worst case).
- **Verification method:** Test
- **Verified by:** TC-309
- **Category:** Reliability
- **Regulatory:** none
- **Priority:** Should
- **Status:** Approved (owner, Ben Spoor, 2026-11-07, in the working session; recorded by the assistant; values in square brackets stay open until measured)

### MECH-015 Sharp ends of the light arcs

- **Statement:** The housing shall confine the light of each LED arc to its window, so that at each of the four arc ends and along the inner and outer border of each arc and the border of the centre button the luminance 1 mm inside the edge is at least [90] % of the mean luminance of the arc, the luminance 3 mm outside the edge is at most [2] % of it, and the transition from 10 % to 90 % takes at most [1.5] mm.
- **Rationale:** Owner request 2026-11-28 ("ensure by the mechanical design that the edges are sharp"; asked what is meant: "Of the light I mean", so the edges of the lit arcs, ends and borders; the owner then added 4 LEDs under a translucent centre button, 2026-11-28) for the split ring (ADR-0027, Proposed). A hard cut alone is not sharp: with an absorbing wall at the end the luminance at the wall is 50 % of the arc mean and reaches 90 % only about 7 mm inside (`mech/analysis/light_edge.py`, model), so the criterion is on the luminance profile and not on the geometry of the cut. A translucent plate over the gap guides light sideways, so the end cannot be sharp under one plate. Proposed by the assistant; the values in square brackets are working values.
- **Parent:** SYS-001
- **Acceptance criteria:** Coupon test first: a sector coupon of [3] LEDs at the working pitch with light walls of [0.8], [1.2] and [1.6] mm, black and white-faced, measures the optical density of each wall and the luminance profile at the end and across the width of the arc (camera with fixed settings at [0.5] m, raw image, profiles along and across the arc). Then the finished lid: all four ends, both borders of each arc and the border of the centre button meet the three numbers of the statement at the status brightness, and no light is visible in a gap at 1 m in a dark room. Wall and cap materials are non-conductive and non-metallic (MECH-003); the black filament is checked for conductivity.
- **Verification method:** Test
- **Verified by:** TC-317
- **Category:** Performance
- **Regulatory:** none
- **Priority:** Should
- **Status:** Draft (proposed by the assistant, 2026-11-28; not approved; values in square brackets are working values until measured)
