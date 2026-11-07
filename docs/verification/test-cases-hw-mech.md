# Hardware and mechanical test cases

- **Status:** Draft (stubs; procedures are written when the requirements are approved)

### TC-201 LED ring layout

- **Verifies:** HW-001
- **Level:** Inspection
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of HW-001
- **Automated:** TBD
- **Evidence:** TBD

### TC-202 LED data drive

- **Verifies:** HW-002
- **Level:** Analysis
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of HW-002
- **Automated:** TBD
- **Evidence:** TBD

### TC-203 USB-C power input

- **Verifies:** HW-003
- **Level:** Prototype
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of HW-003
- **Automated:** TBD
- **Evidence:** TBD

### TC-204 Power budget and supply margin

- **Verifies:** HW-004
- **Level:** Analysis and prototype
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of HW-004
- **Automated:** TBD
- **Evidence:** TBD

### TC-205 Antenna keep-out

- **Verifies:** HW-005
- **Level:** Inspection
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of HW-005
- **Automated:** TBD
- **Evidence:** TBD

### TC-206 Test points and programming access

- **Verifies:** HW-006
- **Level:** Prototype
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of HW-006
- **Automated:** TBD
- **Evidence:** TBD

### TC-207 Button input

- **Verifies:** HW-007
- **Level:** Analysis
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of HW-007
- **Automated:** TBD
- **Evidence:** TBD

### TC-208 Shop manufacturability

- **Verifies:** HW-008
- **Level:** Inspection
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of HW-008
- **Automated:** TBD
- **Evidence:** TBD

### TC-209 Design checks

- **Verifies:** HW-009
- **Level:** Inspection
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of HW-009
- **Automated:** TBD
- **Evidence:** TBD

### TC-301 Housing size

- **Verifies:** MECH-001
- **Level:** Prototype
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of MECH-001
- **Automated:** TBD
- **Evidence:** TBD

### TC-302 Light diffuser

- **Verifies:** MECH-002
- **Level:** Prototype
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of MECH-002
- **Automated:** TBD
- **Evidence:** TBD

### TC-303 Antenna clearance

- **Verifies:** MECH-003
- **Level:** Inspection
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of MECH-003
- **Automated:** TBD
- **Evidence:** TBD

### TC-304 Access to USB-C and button

- **Verifies:** MECH-004
- **Level:** Prototype
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of MECH-004
- **Automated:** TBD
- **Evidence:** TBD

### TC-305 Thermal and material

- **Verifies:** MECH-005
- **Level:** Prototype
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of MECH-005
- **Automated:** TBD
- **Evidence:** TBD

### TC-306 Label area

- **Verifies:** MECH-006
- **Level:** Inspection
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of MECH-006
- **Automated:** TBD
- **Evidence:** TBD

### TC-210 Hardware current limit on the USB input

- **Verifies:** HW-010
- **Level:** Prototype
- **Procedure:** see the draft procedure below. Scope: scope of the IC supply, the IC output and each gate enable at plug-in on a default source and on a 1.5 A source; the hold-off time of at least [200] ms; the IC output forced low during the hold-off; repeated plug-in and a brown-out of the IC supply; a VBUS dip to about 3.5 V for 10 to 100 ms after the hold-off is done (the full hold-off must start again; measure the discharge time of the delay capacitor of the supervisor, RISK-044); a shorted and an open delay capacitor and a supervisor output forced high (the gate must be shown to lose the hold-off, to size RISK-044)
- **Draft procedure (2026-11-07, written by the assistant after the owner approvals; not reviewed by a goldfish, not run; values in brackets are the open values of the requirement):** Equipment: adjustable USB-C source simulator or lab supply with Rp resistors for default, 1.5 A and 3 A advertisement; electronic load; 4-channel scope with a 10x probe and one high-impedance probe; thermal chamber or hot plate for the 70 degC runs; at least [10] built units; a log sheet per unit. Steps: (1) Static: with the gate enabled by a bench override, measure each ILIM step with the electronic load and compare with the windows of HW-010 (step 1 at most 623 mA, step 2 850 to 1150 mA, step 3 1366 to 1577 mA), at 25 degC and at 70 degC. (2) Exclusive steps: apply every pattern of the two select inputs and record that Q2 and Q3 are never on together in steady state; scope the change from step 2 to step 3 for overlap. (3) Hold-off: ramp VBUS in at most [10] ms; record the time from VBUS_IC through [4.3] V to each enable output through [1.65] V, [10] repeats per unit; pass limits are 203.2 to 553.2 ms widened by the measurement uncertainty of the scope setup (state it). Compare the minimum with the CC IC debounce measured at plug-in and at a source change; the margin is [20] ms or more (HW-010 criterion 1; the datasheet gives no maximum debounce, so this is the only evidence). (4) Scope capture for DEV-001 (criterion 4): VBUS_IC, +5V, 3V3 and the ILIM node at plug-in and at VBUS dropout; record the time with 3V3 below 0.5 V, the peak of ILIM minus 3V3 (must stay at or below VBUS_IC + 0.5 V), the limit error, and the TVS1 clamp voltage (below 6 V). (5) Sag band M4: ramp VBUS_IC from 3.5 V to 5 V with a default source, then a loaded source that sags to 4.2 V and to 4.4 V; no enable output may rise. Record the result either way; a fail opens a design change and does not edit the pass limit. (6) Advertisement change and cable wobble with VBUS up: no raised step before the CC IC has settled (criterion 6). (7) VBUS dip to about 3.5 V for 10 to 100 ms after the hold-off: the full hold-off starts again; record the discharge time of the delay capacitor (RISK-044). (8) Fault injection, one row per fault, expected state written before the run: CC IC unpowered; IC output shorted high and low; gate input open; GPIO stuck high; both select GPIOs high; supervisor output stuck high and low; delay capacitor open and short; IC supply between 4.0 and 4.5 V; 3V3 absent with VBUS present. The shorted select switch and the stuck-high AND output are not covered (RISK-029) and are listed as such. (9) Unplug: record VBUS_IC, +5V, 3V3 and FAULT_N decay (criterion 8). (10) First boot with a scope on GPIO21 during the ROM print: the readback never shows a valid high (criterion 9). Records: scope captures and the log sheet go to `docs/verification/reports/`, unit serial numbers and instrument IDs included. Pass: criteria 1 to 9 of the HW-010 approved revision; results that are only recorded (step 5, the fault table rows not covered) are marked as such. Not run.
- **Expected result / pass criteria:** see acceptance criteria of HW-010
- **Automated:** TBD
- **Evidence:** TBD
- **Proposed procedure outline (Draft, 2026-11-05, owner decision; proposal P6 of `docs/verification/reports/analysis-sw005-holdoff-timing.md`; it belongs to the Proposed amendment of HW-010 and is not Approved; "Procedure: TBD" above stays until the owner approves the amendment):** Add to the points listed in the procedure above: (a) hold-off measured as the time from VBUS_IC passing [4.3] V to the rise of each enable output through [1.65] V, with a VBUS ramp of at most [10] ms, on at least [10] units or [10] repeats, against the window 203.2 to 553.2 ms of the capacitor set 6 x 100 nF C0G 5 % (owner choice 2026-11-06, HW-010 Proposed revision, table of current values; the set 220 + 220 + 100 + 68 nF gave 205.9 to 560.6 ms), and against the CC IC debounce (scope on the CC IC outputs at plug-in and at a source change; margin of at least [20] ms); (b) each limit step measured with an electronic load: step 1 at most 623 mA, step 2 within 850 to 1150 mA, step 3 within 1366 to 1577 mA (calculated: 504.2 to 616.6, 934.9 to 1091.7 and 1381.2 to 1566.6 mA), also at 70 C ambient if the setup allows (leakage of the select switches); (c) truth table of the exclusive steps: no input pattern turns Q2 and Q3 on together; (d) with a scope, VBUS_IC, +5V, 3V3 and the ILIM node (one high-impedance probe) at plug-in and at VBUS dropout, for each build: time with 3V3 below 0.5 V, peak of the ILIM node minus 3V3, and the limit error in that window (evidence for DEV-001 and RISK-045; fallback TS5A3166 if not acceptable); (e) ramp VBUS_IC slowly from 3.5 V to 5 V with a default-current source: no enable output rises; (f) VBUS_IC, +5V, 3V3 and FAULT_N during the unplug decay and with 5 V on TP1 only; (g) the VBUS dip of 10 us to 100 ms and the full-restart question (RISK-044). Not run: nothing was measured.

### TC-211 Orientation sensor

- **Verifies:** HW-011
- **Level:** Prototype
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of HW-011
- **Automated:** TBD
- **Evidence:** TBD

### TC-212 Datasheet evidence for analysed part values

- **Verifies:** HW-012
- **Level:** Inspection
- **Procedure:** TBD (draft: run `python3 -I scripts/check_part_evidence.py --netlist <board netlist>` with the datasheets folder present; list the claims used by each script in `hw/sim/` and their status)
- **Expected result / pass criteria:** see acceptance criteria of HW-012
- **Automated:** `scripts/check_part_evidence.py` and `scripts/test_check_part_evidence.py` (pytest) cover the format checks; the review of claim values is manual
- **Evidence:** TBD

### TC-307 Back mounting interface

- **Verifies:** MECH-007
- **Level:** Prototype
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of MECH-007
- **Automated:** TBD
- **Evidence:** TBD

### TC-308 Accessory retention

- **Verifies:** MECH-008
- **Level:** Prototype
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of MECH-008
- **Automated:** TBD
- **Evidence:** TBD

### TC-213 Thermal limit in the closed housing at the top current step

- **Verifies:** HW-013
- **Level:** Prototype
- **Procedure:** see the draft procedure below
- **Draft procedure (2026-11-07, written by the assistant after the owner approvals; not reviewed by a goldfish, not run; values in brackets are the open values of the requirement):** Equipment: closed housing with the board as built (TC-305 setup), thermocouples (type K, calibrated) on the CC detection IC, the TPS2553, the regulator, the LED driver parts, the module and the housing wall near the LEDs, or a thermal camera with emissivity noted; temperature chamber or a room kept at [35] degC; electronic or LED load that draws the top step; the USB source with 1.5 A advertisement; data logger. Steps: (1) Soak the closed unit at [35] degC ambient until all sensors agree within 1 K. (2) Run constant white at the top step current (advertised value minus the SYS-020 margin, at most [1350] mA at the connector) for [60] min after the first reading of equilibrium (change below 1 K in 10 min); log all channels every 10 s. (3) Record the maximum of each channel, the CC IC ambient and the housing temperature; compare with the part ratings in the evidence files (HW-012) and the softening limit named in RISK-005. (4) Hung-firmware run: a test build holds a select output high at the maximum hardware limit (1577 mA); run [10] min, record the temperatures, abort at any part rating exceeded. (5) Repeat the main run with the unit in the vertical and in the horizontal mounting (ADR-0011, RV-004 A1). Pass: no part above its rating, CC IC ambient at most [70] degC, housing below the softening limit. Step (4) is recorded, not a pass criterion (HW-013). Also record whether the middle step still earns its place (the owner may drop it after this test, RV-010 finding 9). Not run; no hardware exists.
- **Expected result / pass criteria:** see acceptance criteria of HW-013
- **Automated:** TBD
- **Evidence:** TBD
