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

- **Statement:** The board shall provide test points for 5 V, 3.3 V, ground, the LED data line, and the reset and boot signals, and shall allow programming and the production self-test through the USB-C connector alone.
- **Rationale:** SYS-023: low-cost production testing. Test points make faults findable (design for test). UART transmit and receive test points were removed in the prototype (owner choice 2026-11-04, session): the two processor pins are used for the gate-enable readbacks of HW-010, and programming and self-test use the USB-C connector alone.
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
- **Proposed amendment (2026-11-04, from the second goldfish review of the gate; the Approved text above is unchanged until the owner confirms):** Add to the statement: "The board shall give the processor a readback input for the hold-off state and one for the gate enable of each gated step, at levels that the processor input accepts (3.3 V logic, no more than the processor rating at any power order), so that the firmware can reduce its load when the gate closes (SW-009)." Add to the acceptance criteria: "Each readback input shows the real state of the gate in the hold-off, with the gate open and with the gate closed; with VBUS at 0 V and 3V3 present, no readback pin exceeds the processor rating." Rationale: the gate closes alone for [200] to [600] ms after a VBUS dip while the processor keeps its full load (RISK-044, SW-009). The 5 V hold-off signal needs a level step before the processor pin; the full-board spike draws it as a 74LVC1G125 buffer on 3V3 (HOLD_OK_RB on GPIO6; spike only, not a decision; its 5 V input tolerance is not read from a datasheet). Pin budget (full-board spike, F1): the eight usable GPIOs are used, so the two gate-enable readbacks (EN2, EN3) take GPIO20 and GPIO21, which frees them by dropping the UART test points (HW-006, owner choice 2026-11-04). Module datasheet read (ESP32-C3-MINI-1): pin 30 is GPIO20 (U0RXD) and pin 31 is GPIO21 (U0TXD), both I/O/T, neither a strapping pin (those are GPIO2, 8, 9). Two points remain: the ROM boot messages go to UART0 by default, so GPIO21 is an output at start-up (a readback driver on it needs a series resistor or the eFuse print control set; not decided); the module datasheet gives only VDD33 as absolute maximum, and VIH is 0.75 x VDD, so keep every readback at 3.3 V logic. Open point from the spike (M1): the ESP32-C3 D+ pull-up is enabled after reset (TRM v1.4, 2.2 or 1.1 kohm) and the ESD part (USBLC6-2) has steering diodes from the data pins to its VBUS pin, which sits on VBUS_IC; with VBUS gone and 3V3 up, VBUS_IC would sit near 2.7 V (estimate, 1.2 to 2.5 mA). Loaded, VBUS_IC is about 2.0 to 2.6 V (analysis), which is below the CC IC and supervisor thresholds, so the gate stays closed; the TPS2553 UVLO (2.35 to 2.45 V) may be crossed, but its reverse-voltage protection keeps the switch off because +5V stays above VBUS_IC in this loop. Proposed: accept for the prototype, and add the bench measurement "VBUS_IC, +5V, 3V3 and FAULT_N with the cable unplugged (decay after unplug, and 5 V on the +5V test point only)" to the acceptance criteria; the owner confirms. Open point from the spike (M4): the hold-off timer starts when VBUS_IC passes the supervisor release voltage (4.115 to 4.285 V for a 4.0 V part), but the CC IC is specified from 4.5 V. A source that stays between about 4.3 V and 4.5 V for the whole hold-off would leave the CC IC outside its supply range with no stated output state. A higher supervisor threshold does not fix this (a 4.4 V part releases at up to 4.691 V, above the 4.5 V VBUS minimum assumed). Proposed: keep the 4.0 V part and add the bench check "ramp VBUS_IC slowly from 3.5 V to 5 V with a default-current source: no enable output rises" to the acceptance criteria; the owner confirms. Open point from the spike (M2/M3): CC_OK_1A5 and CC_OK_3A read high when VBUS is gone and 3V3 is up, because the open-drain CC IC outputs are low without VBUS and the inverters on 3V3 invert them. Proposed SW-009 amendment (status Proposed, Approved and Draft text unchanged): "The firmware shall treat the CC_OK inputs as valid only while HOLD_OK_RB is high, and otherwise assume the lowest step." Also, the Zephyr default console for the ESP32-C3 boards drives GPIO21 (UART0 TX) and the ROM boot message goes to UART0 by default (TRM v1.4 section 7.3, eFuse UART_PRINT_CONTROL, GPIO8 pulled up), so the application must disable the UART console, and the ROM print needs a series resistor on the GPIO21 readback or the eFuse set; the spike draws 100 kohm on the readbacks with 10 kohm enable pull-downs (analysis-n1-n2-readback-backfeed.md; proposed, not decided). The owner decides; the analysis is in the spike report. **Owner-confirmed proposals (2026-11-05; not Approved, the Approved text above is unchanged):** (1) Current limit: use 0.1 % E192 resistors for the prototype, R_ILIM 47.0 kohm, 56.9 kohm and 27.7 kohm (analysis-ilim-steps.md), and keep the HW-010 numbers; the stock at JLCPCB is not yet checked. (2) The middle step is about 1.0 A, with a proposed window of 850 to 1150 mA. (3) Step 1 has a maximum only (623 mA) and no minimum in the requirement; 500 mA is a nominal target in a note. (4) The steps are exclusive: the hardware shall not allow Q2 and Q3 on together, and the step 3 enable forces step 2 off. (6) Hold-off capacitor: a parallel set of C0G capacitors in 1206 or 1210, for example 220 nF + 220 nF + 150 nF + 33 nF at 5 %; the stock is not yet checked. (7) M4: keep the TPS3840DL40 supervisor for the prototype and accept it with the bench ramp check above. (8) M1: accept the D+ back-feed with the bench check above (VBUS_IC, +5V, 3V3 and FAULT_N during the unplug decay and with 5 V on TP1 only); the firmware ignores FAULT_N while HOLD_OK_RB is low (SW-009 proposal). (10) M3: disable the UART0 console and use USB-Serial-JTAG for console and logs (the Zephyr node usb_serial exists in the ESP32-C3 devicetree; the exact Kconfig is not verified); tolerate the ROM print on GPIO21 through the 100 kohm series resistor of the readback; the eFuse is not burnt for the prototype. The 2N7002 is to be replaced by a part with stated low-voltage leakage (open). Record: owner-decisions-2026-11-05.md in the spike.
- **Proposed amendment (2026-11-05, owner decision; the Approved/Draft text above is unchanged until the owner approves):** This paragraph records owner decisions and, where it differs from the earlier proposed paragraph above (items 1 and 6 of the owner-confirmed proposals of 2026-11-05), replaces those items in the proposal; nothing here is Approved. (a) ILIM select switch: Q2 and Q3 are replaced by an analog switch TMUX1101DCKR (LCSC C2673506, SC70-5, off leakage 0.2 nA maximum to 85 degC, `analysis-ilim-switch-replacement.md`), supply pin on 3V3, active-high control, a 100 kohm pull-down on each control pin. Fallback: TS5A3166DBVR (LCSC C353035). The TMUX1101 datasheet does not state the signal-pin behaviour with the signal above VDD + 0.5 V; the ILIM node (about 1 V, assumed) can be above that while 3V3 is below about 0.5 V at every power-up (the TPS2553 is enabled from VBUS_IC and 3V3 comes from its output). This is recorded as deviation DEV-001 (abs. max. rating of a signal pin exceeded for a short time, until the bench check shows the effect), with RISK-045. (b) ILIM resistors, all 0.1 % 0603 thin film: step 1 R_ILIM1 47.0 kohm; step 2 R_ILIM2 56.2 kohm (replaces 56.9 kohm); step 3 R_ILIM3 27.4 kohm plus a series resistor of 301 ohm (replaces 27.7 kohm; the sum 27.701 kohm gives the same limits as 27.7 kohm). Calculation with the existing `ilim_steps.py` (Rds 0 to 9.5 ohm, leakage 0.2 nA, V_ILIM 1.0 V assumed): step 1 504.2 to 616.6 mA (maximum 623, margin 6.4 mA); step 2 934.9 to 1091.7 mA (inside the proposed 850 to 1150 mA window; margin 84.9 mA to the lower edge, 58.3 mA to the upper edge); step 3 1381.2 to 1566.6 mA (window 1366 to 1577; margins 15.2 mA and 10.4 mA); Q2 and Q3 both on 1817 to 2020 mA, which the exclusive gate of the earlier proposal prevents. Without the 301 ohm the step 3 maximum is 1576.8 mA, a margin of 0.2 mA, which is why the series resistor is added. The values are not checked for stock; temperature coefficient and ageing are not modelled. (c) Hold-off capacitor C1: four C0G capacitors in parallel, 220 nF + 220 nF + 100 nF + 68 nF, 5 % (replaces the 220 + 220 + 150 + 33 nF example). Calculated hold-off window with the datasheet constants of the TPS3840 and the temperature range of the parts: 205.9 to 560.6 ms (script `holdoff_cap.py`; 205.2 to 562.2 ms with the 0.6 % allowance of the N4 report). This is inside [200] to [600] ms. The 68 nF C0G part is not checked for availability. (d) Statement of the hold-off measurement (for the acceptance criteria): the hold-off is the time from VBUS_IC passing [4.3] V to the rise of each enable output through [1.65] V, with a VBUS ramp of at most [10] ms; the parenthesis "(the upper value keeps the limit change inside the [1] s of SYS-020)" is replaced by "(the upper value, with the stable reading time of SW-005, is within the time that SYS-020 gives for the raise of the limit)"; the minimum measured hold-off exceeds the maximum CC debounce of the CC IC by at least [20] ms (the maximum debounce is not found in the datasheet read; if it is 200 ms or more, the hold-off minimum needs a new decision). (e) Bench checks to add to the acceptance criteria (TC-210): the measured hold-off against the window of item (c); each limit step measured with a load against the numbers of item (b); with a scope, VBUS_IC, +5V, 3V3 and the ILIM node at plug-in and at VBUS dropout, with the time that 3V3 is below 0.5 V and the peak of ILIM node minus 3V3, and the limit error in that window (closes or confirms DEV-001; if the effect is not acceptable the fallback of item (a) is used and its 5 uA powered-off leakage is reviewed). Not run: no bench, no SPICE; the 1 V ILIM voltage is an assumption; the stock of the TMUX1101, the 0.1 % resistors and the 68 nF part is not checked; a part change on a safety-relevant limit needs an ADR-0016 or ADR-0010 amendment (not written here, the owner decides).

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

### HW-012 Datasheet evidence for analysed part values

- **Statement:** Every value that a hardware analysis in `hw/sim/` or a schematic or PCB check takes from a vendor document shall be recorded as a claim in `hw/evidence/parts/`, with the document hash, page, and a quote of at most one sentence or one table row, and shall have status `verified` (checked by a human or by an agent other than the extractor) before the analysis result supports a released design.
- **Rationale:** Analyses of the USB current-limit chain (HW-010) and the hold-off gate depend on datasheet numbers, and earlier reports copied them by hand and could not show where each came from. A checked record per value makes the source auditable (process rule 11) and keeps vendor documents out of the public repository (ADR-0015 item 8). Proposed by the assistant, not Approved.
- **Parent:** SYS-020, SYS-022
- **Acceptance criteria:** `python3 -I scripts/check_part_evidence.py --netlist <board netlist>` exits 0 with the datasheets folder present; every reference designator of the netlist has an evidence file; no analysis script reads a claim with status other than `verified` unless it prints that it did so; claims without a document have status `source-missing` and no number.
- **Verification method:** Inspection
- **Verified by:** TC-212
- **Category:** Auditability
- **Regulatory:** none
- **Priority:** Should
- **Status:** Draft
