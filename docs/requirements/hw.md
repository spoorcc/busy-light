# Hardware Requirements

- **Status:** Draft
- **Version:** 0.1
- **Owner:**

Entries use IDs `HW-nnn` and follow `docs/templates/requirement.md`.
Process rules: `docs/process/README.md`.

### HW-001 LED ring layout

- **Statement:** The board shall carry 16 single-wire addressable RGB LEDs, at equal angular spacing of 22.5 degrees on one circle of at least [38] mm diameter, all on the same side of the board.
- **Rationale:** SYS-001 and SYS-028 set count, spacing and ring size; ADR-0004 chooses the single-wire LED type. One side keeps assembly at the prototype shop simple (SYS-022).
- **Parent:** SYS-001, SYS-028
- **Acceptance criteria:** In the KiCad layout the LED centres lie on one circle within [0.2] mm of the nominal radius and [1] degree of the nominal angle; all LEDs are on the same side; the circle diameter is at least the limit.
- **Verification method:** Inspection
- **Verified by:** TC-201
- **Category:** Functional
- **Regulatory:** none
- **Priority:** Must
- **Status:** Draft

### HW-002 LED data drive

- **Statement:** The LED data line shall pass from the processor through a 5 V buffer with a TTL-compatible input, a series resistor of about [330] ohm near the first LED, and a pull-down resistor on the processor side of the buffer, unless spike 7.3 shows that the LED accepts 3.3 V data over the temperature range and the buffer is removed.
- **Rationale:** LED data input thresholds depend on the LED supply and are above a 3.3 V output (ADR-0004 item 2). The pull-down holds the line low at reset (SYS-011).
- **Parent:** SYS-001, SYS-011
- **Acceptance criteria:** The schematic shows the parts and values, or a recorded spike 7.3 result that removes the buffer. A simulation in `hw/sim/` shows valid logic levels at the first LED input at minimum supply and at the highest temperature in the shop's parts data.
- **Verification method:** Analysis
- **Verified by:** TC-202
- **Category:** Reliability
- **Regulatory:** none
- **Priority:** Must
- **Status:** Draft

### HW-003 USB-C power input

- **Statement:** The board shall take 5 V from a USB-C connector as a sink, with the two CC pull-down resistors of 5.1 kohm, ESD protection on VBUS and the data lines, and a design input current of at most [1500] mA (the source-advertised maximum of SYS-020). A CC detection IC (TUSB321, owner choice 2026-11-04, ADR-0016) that carries the 5.1 kohm resistors reports the advertised current on open-drain outputs; the firmware reads them on two processor inputs, and the same outputs go to the gate of HW-010 (ADR-0016, Accepted). The IC's resistors are the only load on the CC lines, with an ESD and clamp part and a series resistor value to be chosen from its datasheet (RV-006 S8).
- **Rationale:** SYS-020 sets the supply and the current limit and (owner, 2026-11-04) allows a higher current if the source advertises it, which the firmware can only know if it can read the CC voltage. Without CC resistors some USB-C chargers deliver no power. Connector, track and fuse ratings must cover the highest allowed current.
- **Parent:** SYS-020
- **Acceptance criteria:** The schematic shows the 5.1 kohm Rd on CC1 and CC2 inside the CC detection IC and no discrete Rd in parallel, an ESD device on VBUS, D+ and D-, and the power budget in `hw/sim/` shows the worst-case input current at or below the limit. The schematic shows the CC detection IC, its outputs to the processor and to the gate of HW-010, and the CC protection. The connector, tracks and any protection device are rated for at least [1500] mA with a margin (calculation in `hw/sim/`). The PORT pin of the IC is tied to GND, and the IC ambient temperature on the prototype at full LED load is recorded against its 70 C limit. A prototype powers up from a USB-C to USB-A cable and from a USB-C charger, and the firmware reports the advertised current of three different sources (default, 1.5 A, 3 A) from the two IC outputs (OUT1 low for 1.5 A or 3 A, OUT2 low for 3 A). A PD-capable charger, an e-marked cable, a non-compliant cable (bad Rp) and band-edge Rp (0.61 V and 0.70 V) are also tested; the non-compliant cable is not protected by the gate (RV-008).
- **Verification method:** Test
- **Verified by:** TC-203
- **Category:** Safety
- **Regulatory:** none
- **Priority:** Must
- **Status:** Approved
- **Approval:** the owner (Ben Spoor), 2026-11-04, by instruction in the session; recorded by the assistant. The bracketed values stay open until set.

### HW-004 Power budget and supply margin

- **Statement:** The 3.3 V supply shall provide at least [1.5] times the worst-case sum of the processor, radio and logic current, and the board shall not reset when the Wi-Fi transmit peak and the LED peak happen together.
- **Rationale:** RISK-004: brown-out when peaks coincide. The USB budget is shared (ADR-0004).
- **Parent:** SYS-020, SYS-027
- **Acceptance criteria:** The power-budget script in `hw/sim/` uses datasheet values and shows the margin. A bench test with the LEDs at the limited maximum and a continuous Wi-Fi transmit shows no reset in [10] min and a 3.3 V minimum above the processor's minimum supply.
- **Verification method:** Analysis
- **Verified by:** TC-204
- **Category:** Reliability
- **Regulatory:** none
- **Priority:** Must
- **Status:** Draft

### HW-005 Antenna keep-out

- **Statement:** The Wi-Fi module shall be placed according to its datasheet keep-out area, with no copper, LED, component or wire inside that area, and with the antenna at the board edge or in the ring centre only as ADR-0003 allows.
- **Rationale:** ADR-0003: an antenna surrounded by LEDs and ground is the main range risk (RISK-011).
- **Parent:** SYS-038, SYS-022
- **Acceptance criteria:** The KiCad design rule check includes a keep-out rule that shows no violation. The range test of SYS-038 passes with the finished housing.
- **Verification method:** Inspection
- **Verified by:** TC-205
- **Category:** Performance
- **Regulatory:** RED Art. 3(2) *(verify)*
- **Priority:** Must
- **Status:** Draft

### HW-006 Test points and programming access

- **Statement:** The board shall provide test points for 5 V, 3.3 V, ground, UART transmit and receive, the LED data line, and the reset and boot signals, and shall allow programming and the production self-test through the USB-C connector alone.
- **Rationale:** SYS-023: low-cost production testing. Test points make faults findable (design for test).
- **Parent:** SYS-023
- **Acceptance criteria:** Each test point is on the layout with a label and at least [1.0] mm pad. A new board is programmed and self-tested using only the USB-C cable.
- **Verification method:** Demonstration
- **Verified by:** TC-206
- **Category:** Testability
- **Regulatory:** none
- **Priority:** Must
- **Status:** Draft

### HW-007 Button input

- **Statement:** The button shall connect to a processor input with a pull resistor, an ESD-safe path and no effect on the boot mode pins at power-up.
- **Rationale:** SYS-017: one button. A button on a boot-mode pin can stop the unit from starting or open download mode.
- **Parent:** SYS-017, SYS-043
- **Acceptance criteria:** The schematic and the processor datasheet table of boot pins show that the button pin is not a boot-mode pin, or that the button state at power-up cannot select an unsafe mode. A prototype starts normally with the button held at power-up.
- **Verification method:** Analysis
- **Verified by:** TC-207
- **Category:** Safety
- **Regulatory:** none
- **Priority:** Must
- **Status:** Draft

### HW-008 Shop manufacturability

- **Statement:** All parts shall be surface-mounted on one side, available in the chosen shop's parts list, and the board outline, drill and trace rules shall meet the shop's published limits. The Wi-Fi module shall be a chip revision of at least v0.3, so that secure boot v2 is supported.
- **Rationale:** SYS-022: no hand soldering. SYS-021: the extended-part fees depend on the choice.
- **Parent:** SYS-022, SYS-021
- **Acceptance criteria:** The shop's design check accepts the files; every BOM line shows stock and price (spike 7.4); the number of extended parts is stated in the BOM; the BOM or the module datasheet names a chip revision of at least v0.3.
- **Verification method:** Inspection
- **Verified by:** TC-208
- **Category:** Manufacturability
- **Regulatory:** RoHS Art. 4 *(supplier declarations)*
- **Priority:** Must
- **Status:** Draft

### HW-009 Design checks

- **Statement:** The released board design shall pass the KiCad electrical rule check and design rule check without unexplained violations, and the results shall be stored with the design revision.
- **Rationale:** Verification strategy: hardware is verified by simulation and analysis wherever feasible.
- **Parent:** SYS-022, SYS-020
- **Acceptance criteria:** Both reports show zero errors; each warning has a written reason; reports are in `hw/sim/` or `docs/verification/reports/`.
- **Verification method:** Inspection
- **Verified by:** TC-209
- **Category:** Auditability
- **Regulatory:** none
- **Priority:** Must
- **Status:** Draft

### HW-010 Hardware current limit on the USB input

- **Statement:** The board shall limit the current taken from the USB-C connector in hardware, with a current-limited load switch in the VBUS path whose limit is [500] mA at power-up and can be raised by the firmware, in steps, up to the allowed maximum of SYS-020 only after the advertised current has been read, and only while an output of the CC detection IC, independent of the firmware, reports at least 1.5 A and a start-up hold-off has expired (ADR-0016, Accepted).
- **Rationale:** Owner decision of 2026-11-04. A firmware-only limiter (ADR-0004) cannot protect a source that advertises little if the firmware fails or misreads the CC lines (RISK-003, RISK-025). The hardware limit is the backstop that does not depend on the firmware at start-up.
- **Parent:** SYS-020
- **Acceptance criteria:** With the firmware stopped (held in reset), the input current cannot exceed 623 mA (500 mA plus the tolerance of the limit part with a 1 % set resistor, ADR-0010 open point 1), also with a short circuit on the LED supply. With a source that advertises the default current and each firmware select output forced high in turn (every step above the first), the limit stays at or below 623 mA. Start-up hold-off: after the IC supply becomes valid, every enable output of the gate stays low for at least [200] ms and at most [600] ms (the upper value keeps the limit change inside the [1] s of SYS-020) (longer than the 133 ms CC debounce of the TUSB321 type, `docs/verification/reports/cc-ic-datasheet-evidence.md`), also when the IC output is forced low during that time, and the hold-off restarts after every loss of the IC supply. Fault injection: CC detection IC unpowered, IC output shorted high and low, gate input open, select MOSFET shorted, GPIO stuck high; every open or short on the gate path resolves to the lowest step except the shorted select MOSFET and a stuck-high AND output, which are recorded as not covered (RISK-029). After the firmware has read an advertisement of 1.5 A it can raise the limit, and the input current can then reach the advertised value minus the margin. At the top step the limit is at least 1366 mA and at most 1577 mA (ADR-0010 open point 2); the firmware value is 1350 mA. The limit part has an over-temperature and short-circuit behaviour that is stated in its datasheet (kept in `hw/datasheets/`). The added voltage drop and cost are within the budget of SYS-021 (cost of the part is stated in the BOM).
- **Verification method:** Test
- **Verified by:** TC-210
- **Category:** Safety
- **Regulatory:** EN 62368-1 *(verify)*
- **Priority:** Must
- **Status:** Approved
- **Approval:** the owner (Ben Spoor), 2026-11-04, by instruction in the session; recorded by the assistant. Not covered and still open: a fault of the detection IC itself (RISK-042), a stuck gate output or shorted select MOSFET (RISK-029), a non-compliant cable, hung firmware (ADR-0010 open point 4). Bracketed values stay open.
- **Proposed amendment (2026-11-04, from the second goldfish review of the gate; the Approved text above is unchanged until the owner confirms):** Add to the statement: "The board shall give the processor a readback input for the hold-off state and one for the gate enable of each gated step, at levels that the processor input accepts (3.3 V logic, no more than the processor rating at any power order), so that the firmware can reduce its load when the gate closes (SW-009)." Add to the acceptance criteria: "Each readback input shows the real state of the gate in the hold-off, with the gate open and with the gate closed; with VBUS at 0 V and 3V3 present, no readback pin exceeds the processor rating." Rationale: the gate closes alone for [200] to [600] ms after a VBUS dip while the processor keeps its full load (RISK-044, SW-009). The 5 V hold-off signal needs a level step (divider or a gate on 3V3) before the processor pin; this is not drawn yet.

### HW-011 Orientation sensor

- **Statement:** The board shall carry a 3-axis accelerometer that the processor reads, with a range of at least plus or minus [2] g and an angle error of at most [5] degrees in the static case, with its axes fixed relative to the ring, drawing at most [0.2] mA on average, and with a part cost of at most EUR [0.5] at 10 units.
- **Rationale:** SYS-047 needs the direction of gravity. The values are working figures; no part is chosen, and no datasheet was read for this draft. The part cost and current come from the budget in SYS-020 and SYS-021, not from a part.
- **Parent:** SYS-047
- **Acceptance criteria:** On a prototype board in a test jig, the measured angle in 12 positions differs from the jig angle by at most [5] degrees; the added average current is at most [0.2] mA; the part is on the shop's parts list (HW-008) and the second source with the same footprint is named in the BOM. The sensor does not conflict with the antenna keep-out of HW-005.
- **Verification method:** Test
- **Verified by:** TC-211
- **Category:** Functional
- **Regulatory:** none
- **Priority:** Should
- **Status:** Draft
