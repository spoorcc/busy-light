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
- **Approved revision (consolidated 2026-11-06; approved by the owner, Ben Spoor, 2026-11-07, in the session; recorded by the assistant). Where this block and the text above differ, this block applies.** The debounce margin (the [20] ms criterion below), the M4 sag band (criterion 5) and the unchosen parts (TVS1, 3V3 regulator) stay open and the bracketed values stay open until measured. This block replaces the three earlier Proposed paragraphs of 2026-11-04 and 2026-11-05 (superseded; their facts are kept below, their E192 resistor values and 220+220+150+33 nF and 220+220+100+68 nF capacitor sets are not). It follows the goldfish review RV-010 (finding numbers in brackets). Evidence level: desk analysis only. No bench, no SPICE, no firmware run.
  - **Statement addition:** "The board shall give the processor a readback input for the hold-off state and one for the gate enable of each gated step, at levels that the processor input accepts (3.3 V logic, no more than the processor rating at any power order), so that the firmware can reduce its load when the gate closes (SW-009)."
  - **Current values (one table):**

    | Item | Value | Source and status |
    |---|---|---|
    | ILIM select switches Q2, Q3 | analog switch TMUX1101DCKR (C2673506, SC70-5, off leakage 0.2 nA maximum to 85 degC), supply (VDD) from VBUS_IC with a 100 nF capacitor (owner decision 2026-11-07, removes the abs-max exceedance of DEV-001, `analysis-tmux1101-supply-from-vbus.md`), active-high control from the 3V3 gates. Fallback TS5A3166DBVR (C353035); the fallback needs its own check and its stock is not checked | owner decision 2026-11-06; `analysis-ilim-switch-replacement.md`; DEV-001, RISK-045 |
    | R_ILIM1 (step 1) | 47.0 kohm 0.1 % 0603, Yageo RT0603BRD0747KL (C326725, 17,621 in stock) | owner choice 2026-11-06, live stock, Extended |
    | R_ILIM2 (step 2) | 56.2 kohm 0.1 % 0603, Yageo RT0603BRD0756K2L (C705784, 7,107) | same |
    | R_ILIM3 (step 3) | 27.4 kohm 0.1 % 0603, Yageo RT0603BRD0727K4L (C861274, 14,937) plus 301 ohm 0.1 % 0603, Panasonic ERA-3AEB3010V (C2074494, 5,222) in series | same; without the 301 ohm the step 3 maximum is 1576.8 mA, margin 0.2 mA |
    | Hold-off capacitor C1 | six 100 nF C0G 5 % 50 V 1206 in parallel, Murata GRM31C5C1H104JA01L (C97946, 96,458), 600 nF in total | owner choice 2026-11-06 |
    | Step 1 window | 504.2 to 616.6 mA (maximum 623 mA, margin 6.4 mA) | calculated, `hw/sim/scripts/amendment2_numbers.py` |
    | Step 2 window | 934.9 to 1091.7 mA, inside the proposed 850 to 1150 mA (margins 84.9 and 58.3 mA). Step 2 is a thermal cap (SYS-020 Proposed text, owner decision 2026-11-07); it is built now and may be dropped after TC-213 (RV-010 9) | calculated; owner decision 2026-11-07 |
    | Step 3 window | 1381.2 to 1566.6 mA, inside 1366 to 1577 mA (margins 15.2 and 10.4 mA) | calculated |
    | Q2 and Q3 both on | 1817 to 2020 mA, prevented by the exclusive gate (see below) | calculated |
    | Hold-off window | 203.2 to 553.2 ms (202.5 to 554.8 ms with the 0.6 % allowance); inside [200] to [600] ms; margin to the lower edge 3.2 ms (2.5 ms) | calculated; ageing, DC bias and C0G leakage taken as 0 and not checked |
    | Supervisor | TPS3840DL40, release 4.115 to 4.285 V | owner decision 2026-11-05, kept (M4) |

    Assumptions of these numbers: 1.0 V on the ILIM pin (the TPS2553 datasheet text read states no value), Rds(on) of the switch 0 to 9.5 ohm, leakage 0.2 nA. Temperature coefficient (25 ppm/degC) and ageing of the resistors are not modelled yet (RV-010 13).
  - **Gate behaviour to state in the requirement (RV-010 5, 20):** The steps are exclusive. The step 3 enable forces step 2 off (a NOR in the spike), so Q2 and Q3 are not on together in steady state; at the change from step 2 to step 3 a few gate delays of overlap are possible and are checked with a scope. One pull-down network is stated. Each gate enable net is also the control (SEL) pin of its ILIM switch. It has a 10 kohm pull-down at the gate output (R2, R3) in parallel with a 100 kohm pull-down at the switch pin (R18, R19), 9.1 kohm in total (owner decision 2026-11-05 (a) for the 100 kohm). With one of the two open, only the other remains; with the 100 kohm alone an open gate output with the internal pull-up of GPIO20 or GPIO21 on can exceed the switch VIL, so the firmware keeps those pull-ups off (SW-009). The firmware select lines have 100 kohm pull-downs (R4, R5) and the readbacks have 100 kohm series resistors (R14, R15). The spike schematic matches this network (clarified 2026-11-07 at the owner's request to follow the recommendation; the earlier wording read as if the 100 kohm parts were extra).
  - **Hold-off measurement (RV-010 3, 25):** the hold-off is the time from VBUS_IC passing [4.3] V to the rise of each enable output through [1.65] V, with a VBUS ramp of at most [10] ms. The parenthesis "(the upper value keeps the limit change inside the [1] s of SYS-020)" is replaced by "(the upper value, with the stable reading time of SW-005, is within the time that SYS-020 gives for the raise of the limit)". The minimum measured hold-off shall exceed the maximum CC debounce of the CC IC by at least [20] ms. The maximum debounce is not found in the datasheet read (the evidence report lists 133 ms and 120 ms typical, which also disagree). If it is 200 ms or more, the hold-off minimum needs a new decision. The pass limit includes the measurement uncertainty.
  - **Acceptance criteria to add (bench, TC-210):**
    1. The measured hold-off against the window above.
    2. Each limit step measured with a load against the step windows, also at 70 degC (mandatory, RV-010 13).
    3. The top step limit of 1577 mA is not overload protection for a 1.5 A source. It protects against an advertisement of 500 mA only (RV-010 24).
    4. With a scope: VBUS_IC, +5V, 3V3 and the ILIM node at plug-in and at VBUS dropout. With the switch supply on VBUS_IC (owner decision 2026-11-07), the ILIM node shall stay at or below VBUS_IC + 0.5 V at all times, also during the dropout fall, and the limit error in the window shall be recorded. This closes DEV-001 (its exceedance is removed by design). The VBUS_IC TVS clamp voltage shall be below the 6 V absolute maximum of the switch supply (part to check).
    5. VBUS_IC ramped slowly from 3.5 V to 5 V with a default-current source, and a loaded source that sags to 4.2 V and to 4.4 V: no enable output rises (M4; the hold-off timer starts at 4.115 to 4.285 V but the CC IC is specified from 4.5 V; a 4.4 V supervisor releases at up to 4.691 V, above the 4.5 V assumed VBUS minimum, so it does not fix this) (RV-010 2).
    6. A change of the advertisement (Rp default to 1.5 A) and a cable wobble that leaves VBUS up: the gate must not give a raised step before the CC IC has settled (RV-010 12).
    7. Fault injection table, each row with the expected state: CC IC unpowered; IC output shorted high and low; gate input open; GPIO stuck high; GPIO2 and GPIO3 both high; supervisor output stuck high and low; delay capacitor open and short; IC supply between 4.0 and 4.5 V; 3V3 absent with VBUS present; shorted select switch and stuck-high AND output (not covered, RISK-029) (RV-010 27).
    8. VBUS_IC, +5V, 3V3 and FAULT_N with the cable unplugged (decay after unplug, and 5 V on the +5V test point only) (M1, RV-010 16). The ESP32-C3 D+ pull-up is enabled after reset (TRM v1.4, 1.1 or 2.2 kohm) and the ESD part (USBLC6-2) has steering diodes to VBUS_IC; with VBUS gone and 3V3 up VBUS_IC would sit near 2.7 V (estimate, 1.2 to 2.5 mA), loaded about 2.0 to 2.6 V, below the CC IC and supervisor thresholds, so the gate stays closed; the TPS2553 UVLO (2.35 to 2.45 V) may be crossed but its reverse-voltage protection keeps the switch off while +5V is above VBUS_IC. Accepted for the prototype. The firmware ignores FAULT_N while HOLD_OK_RB is low (SW-009).
    9. First boot, with a scope on GPIO21 during the ROM print: the gate enable readback never shows a valid high (RV-010 18).
  - **Readbacks and pins (spike, not a decision):** HOLD_OK_RB on GPIO6 through a 74LVC1G125 buffer on 3V3 as level step (its 5 V input tolerance is not read from a datasheet). The gate enable readbacks EN2 and EN3 take GPIO20 and GPIO21, which drops the UART test points (HW-006, owner choice 2026-11-04). The module datasheet (ESP32-C3-MINI-1) gives pin 30 as GPIO20 (U0RXD) and pin 31 as GPIO21 (U0TXD), neither a strapping pin (those are GPIO2, 8, 9); it gives only VDD33 as absolute maximum, and VIH is 0.75 x VDD. The ROM boot messages go to UART0 by default, so GPIO21 is an output at start-up; the 100 kohm readback resistor tolerates the print and the eFuse is not burnt for the prototype (owner decision 2026-11-05). The Zephyr UART console is disabled and USB-Serial-JTAG carries console and logs; the Kconfig symbols are not verified by a build. The eight usable GPIOs are all used, so the pin map is to be recorded (RV-010 21). CC_OK_1A5 reads high when VBUS is gone and 3V3 is up (the open-drain IC outputs are low without VBUS and the 3V3 inverters invert them), so the firmware treats the CC_OK inputs as valid only while HOLD_OK_RB is high (SW-009 proposal). The ADR-0016 truth table is to be rewritten for this (RV-010 1).
  - **Open for the owner (RV-010):** Decided by the owner on 2026-11-07 (`docs/journal/2026-11-07-rv010-owner-decisions.md`): (1) the CC_OK_3A readback of the TUSB321 OUT2 (U12, R7, GPIO1) is deleted, so the gate and the firmware use OUT1 only (OUT2 is not a clean 3 A signal, `cc-ic-datasheet-evidence.md` item 5); the spike still draws it until HW-010 is Approved; (2) the middle step stays and SYS-020 defines it (to draft); (3) the TMUX1101 over-voltage window is removed by design: the switch supply comes from VBUS_IC (analysis in `analysis-tmux1101-supply-from-vbus.md`; ADR-0016 amendment text added; DEV-001 stays until the owner approves the change and TC-210 (d) is recorded); (4) the maximum CC debounce was looked up on 2026-11-07: the TUSB321 datasheet SLLSEO6C gives 133 ms typical and no maximum, so the [20] ms margin criterion cannot be shown from the datasheet; the set stays for now, and the window arithmetic is in the journal entry of 2026-11-07 (a robust [20] ms margin over a 200 ms debounce does not fit inside [200] to [600] ms with 5 % capacitors); (5) a DEV entry for the acceptance of ADR-0016 before its review (to draft); (6) the thermal and watchdog requirements for the hung-firmware case are drafted (ADR-0010 open point 4).
  - **Proposed amendment (owner decisions of 2026-11-07, drafted by the assistant; not Approved until the owner approves this text; `docs/journal/2026-11-07-surge-regulator-pins-steps.md`):** (1) Criterion 4 last sentence is replaced by: "The supply pins of the TMUX1101 and the TUSB321 (6 V absolute maximum each, datasheets read) are protected by a series resistor and a 5.1 V zener so that the voltage at each pin stays below 6 V during the hot-plug surge at the clamp of TVS1; values from `analysis-supply-pin-surge.md` (ngspice; zener datasheet not read): 1 kohm for the TMUX1101, 470 ohm for the TUSB321, each with its 100 nF at the pin and a 5.1 V zener; the TUSB321 pin sits up to 47 mV below VBUS_IC, which adds to the M4 question." TVS1 stays a standard 5 V part; a TVS alone clamps at 8 to 15 V (`shortlist-tvs1-3v3-regulator.md`). (2) 3V3 regulator: TLV75733P is the candidate; the Wi-Fi duty-cycle heat estimate is added to HW-013 before it is chosen. (3) GPIO1 and GPIO4 are reserved for the orientation sensor (HW-011); FAULT_N is no longer read by the processor. Not run: no values derived, no bench. **Owner approved the surge values (1 kohm and 470 ohm, each with 100 nF and a 5.1 V zener) on 2026-11-07; the zener datasheet is still to be read and the check rerun before the schematic changes.** The regulator candidate is the TLV75733P in the standard DBV package with a firmware limit on the average 3V3 current (owner choice 2026-11-07, `analysis-regulator-heat.md`; the limit is about [70] mA on the worst board and is not yet a requirement); the remaining parts of this amendment stay Proposed.
  - **Not run:** no bench, no SPICE, no firmware. The 1 V ILIM voltage is an assumption. The live stock of the TMUX1101 (2,258 on 2026-11-06), the three resistor types, the 301 ohm part and the 100 nF part was read. The stock of TS5A3166DBVR and TUSB321 is not checked. A part change on a safety-relevant limit needs an ADR-0016 or ADR-0010 amendment; ADR-0016 Amendment 2 (Proposed) covers the current choice.

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

### HW-013 Thermal limit in the closed housing at the top current step

- **Statement:** With the LEDs at the load that draws the top current step (the advertised value minus the margin of SYS-020, at most [1350] mA at the USB-C connector) for [60] min in the closed housing at an ambient temperature of [35] degC, the temperature of every part of the board shall stay at or below its rated limit, the ambient temperature at the CC detection IC shall stay at or below [70] degC, and the housing surface near the LEDs and the module shall stay below the softening limit of its material (RISK-005).
- **Rationale:** Owner decision of 2026-11-07 (RV-010 finding 14): the hung-firmware case at the top step (ADR-0016 item 5, ADR-0010 open point 4) was deferred to a thermal requirement that did not exist. The CC detection IC is listed for 0 to 70 degC (`cc-ic-datasheet-evidence.md`), and the hardware limit at the top step can reach 1577 mA. Without this requirement neither the top step nor a hung firmware at that step has evidence. The values in brackets are working figures, not derived.
- **Parent:** SYS-020
- **Acceptance criteria:** In a test build and the closed housing, the device runs at the top step with a constant white load for [60] min after thermal equilibrium. Thermocouples or a thermal camera show the temperature of the CC detection IC, the TPS2553, the regulator, the LED driver parts and the housing near the LEDs. No part exceeds its rating, the CC IC ambient is at most [70] degC, and the housing stays below the softening limit named in RISK-005. The same test at the maximum hardware limit (hung firmware, select output high, 1577 mA) is run for [10] min and the result is recorded, not required to pass (it states the hung-firmware margin).
- **Verification method:** Test
- **Verified by:** TC-213
- **Category:** Safety
- **Regulatory:** EN 62368-1 *(verify)*
- **Priority:** Must
- **Status:** Approved (owner, 2026-11-07; the bracketed figures stay open; the TC-213 procedure is to be written; the hung-firmware run is recorded, not required to pass)
