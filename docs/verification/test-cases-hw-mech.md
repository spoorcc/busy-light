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
- **Procedure:** TBD. Must include: scope of the IC supply, the IC output and each gate enable at plug-in on a default source and on a 1.5 A source; the hold-off time of at least [200] ms; the IC output forced low during the hold-off; repeated plug-in and a brown-out of the IC supply; a VBUS dip to about 3.5 V for 10 to 100 ms after the hold-off is done (the full hold-off must start again; measure the discharge time of the delay capacitor of the supervisor, RISK-044); a shorted and an open delay capacitor and a supervisor output forced high (the gate must be shown to lose the hold-off, to size RISK-044)
- **Expected result / pass criteria:** see acceptance criteria of HW-010
- **Automated:** TBD
- **Evidence:** TBD
- **Proposed procedure outline (Draft, 2026-11-05, owner decision; proposal P6 of `docs/verification/reports/analysis-sw005-holdoff-timing.md`; it belongs to the Proposed amendment of HW-010 and is not Approved; "Procedure: TBD" above stays until the owner approves the amendment):** Add to the points listed in the procedure above: (a) hold-off measured as the time from VBUS_IC passing [4.3] V to the rise of each enable output through [1.65] V, with a VBUS ramp of at most [10] ms, on at least [10] units or [10] repeats, against the window 205.9 to 560.6 ms of the capacitor set 220 + 220 + 100 + 68 nF C0G 5 %, and against the CC IC debounce (scope on the CC IC outputs at plug-in and at a source change; margin of at least [20] ms); (b) each limit step measured with an electronic load: step 1 at most 623 mA, step 2 within 850 to 1150 mA, step 3 within 1366 to 1577 mA (calculated: 504.2 to 616.6, 934.9 to 1091.7 and 1381.2 to 1566.6 mA), also at 70 C ambient if the setup allows (leakage of the select switches); (c) truth table of the exclusive steps: no input pattern turns Q2 and Q3 on together; (d) with a scope, VBUS_IC, +5V, 3V3 and the ILIM node (one high-impedance probe) at plug-in and at VBUS dropout, for each build: time with 3V3 below 0.5 V, peak of the ILIM node minus 3V3, and the limit error in that window (evidence for DEV-001 and RISK-045; fallback TS5A3166 if not acceptable); (e) ramp VBUS_IC slowly from 3.5 V to 5 V with a default-current source: no enable output rises; (f) VBUS_IC, +5V, 3V3 and FAULT_N during the unplug decay and with 5 V on TP1 only; (g) the VBUS dip of 10 us to 100 ms and the full-restart question (RISK-044). Not run: nothing was measured.

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
