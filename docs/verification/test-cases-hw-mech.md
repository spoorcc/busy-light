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
- **Procedure:** TBD
- **Expected result / pass criteria:** see acceptance criteria of HW-010
- **Automated:** TBD
- **Evidence:** TBD

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
