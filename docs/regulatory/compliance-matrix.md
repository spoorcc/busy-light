# Compliance matrix

- **Document:** Mapping of legal requirements and standard clauses to project requirements, verification and evidence
- **Status:** Draft -- no row is covered; no accredited test and no supplier declaration exists
- **Version:** 0.3   **Date:** 2026-11-10
- **Author:** the assistant   **Owner / approver:** Ben Spoor   **Reviewers:** none yet

## 1. How to read this matrix

Each row links one legal requirement to the project requirement that carries it, the test case or automated rule that checks it, and the evidence. The applicability of each act is argued in `applicability.md`; the standards and their editions are in `technical-file/04-standards-and-testing/standards-list.md`; the tests are planned in `technical-file/04-standards-and-testing/conformity-test-plan.md`.

- Legal references and clause numbers are from secondary sources and memory and are all *(verify)*; the mark is not repeated in every cell.
- **Verification** names test cases (`TC-`) and automated rules (`HWC-`, `SWC-`, `DOC-`; catalogue in `automated-checks.md`). An automated rule checks a design rule; it supports a row but never covers it alone.
- **Status:** `Open` = no evidence. `Partial` = some evidence exists and is named. `Covered` = the evidence is complete, filed and reviewed for the released revision. No row may stay below `Covered` at the release gate.
- Most project requirements cited here are `Draft`. A row cannot be `Covered` on a Draft requirement.
- `scripts/check_compliance_matrix.py` (rule DOC-001) fails CI if a row cites an ID that does not exist, or if a requirement with a `Regulatory:` reference has no row here.

## 2. Radio Equipment Directive 2014/53/EU

### 2.1 Art. 3(1)(a): health and safety

| Reference | What must be met | Requirement | Verification | Evidence | Status |
|-----------|------------------|-------------|--------------|----------|--------|
| EN IEC 62368-1 cl. 5 | Electrical energy sources classified; no shock hazard | SYS-050 | TC-050 | classification table (none yet) | Open |
| EN IEC 62368-1 cl. 6, Annex B | No fire under normal, abnormal and single-fault conditions; power sources classified and limited | SYS-050, HW-010, SYS-020 | TC-050, TC-210, TC-020 | -- | Open |
| EN IEC 62368-1 cl. 6.4 | Board material V-1 or better | HW-021 | TC-221 | fabrication notes (none) | Open |
| EN IEC 62368-1 cl. 6.4.8, Annex S | Housing material class as the fire classification asks | MECH-010 | TC-310 | -- | Open (prototype material is unrated) |
| EN IEC 62368-1 cl. 6, 9 | Current-carrying tracks and parts do not overheat | HW-003, HW-013 | TC-203, TC-213; HWC-010 | CI artefact `hw-compliance.json` | Open (HWC-010 lists narrow segments on the spike) |
| EN IEC 62368-1 cl. 9 | Accessible surfaces within the touch temperature limits | SYS-051, MECH-005 | TC-051, TC-305 | -- | Open |
| EN IEC 62368-1 cl. 8.7 | Mounting means hold the load | MECH-011 | TC-311 | -- | Open |
| EN IEC 62368-1 cl. 10.4 / EN 62471 | LED optical radiation within the limits of the declared risk group | SYS-001, SYS-020 | TC-001, TC-020 (assessment test case to add) | `technical-file/03-risk-and-safety/` | Open, after spike 7.5 |
| GPSR Art. 6 / WCAG 2.3.1 | No flashing pattern that can trigger seizures | SYS-053 | TC-053 | -- | Open |
| EN 50663 or EN IEC 62311; Recommendation 1999/519/EC | Radio-frequency exposure within the public limits | SYS-052 | TC-052 | -- | Open |
| RED Annex II, V; GPSR Art. 9(2) | Risk analysis and assessment in the technical documentation | -- | review | `technical-file/03-risk-and-safety/risk-assessment.md` (Draft) | Partial |

### 2.2 Art. 3(1)(b): electromagnetic compatibility

| Reference | What must be met | Requirement | Verification | Evidence | Status |
|-----------|------------------|-------------|--------------|----------|--------|
| EN 301 489-1, -17; EN 55032 class B | Emission limits | SYS-049 | TC-049 | test report (none) | Open |
| EN 301 489-1, -17; EN 55035 | Immunity with the stated performance criteria | SYS-049 | TC-049 | test report (none) | Open |
| EN 61000-4-2 through EN 301 489-1 | Electrostatic discharge: a clamp on every external interface net | HW-018, HW-003 | TC-218, TC-203; HWC-001, HWC-002 | CI artefact `hw-compliance.json` | Open (spike: CC1, CC2 without clamp, DEV-007) |

### 2.3 Art. 3(2): radio spectrum

| Reference | What must be met | Requirement | Verification | Evidence | Status |
|-----------|------------------|-------------|--------------|----------|--------|
| EN 300 328 | Radio parameters of the 2.4 GHz transmitter and receiver in the product | SYS-038, HW-005 | TC-038 (range only), TC-205 | module test report plus product spot checks (none on file) | Open |
| EN 300 328 | Power and channels stay within the approved values | SW-013 | TC-113 | -- | Open |

### 2.4 Art. 3(3)(d), (e), (f): cybersecurity (for units placed on the market before 11 December 2027)

| Reference | What must be met | Requirement | Verification | Evidence | Status |
|-----------|------------------|-------------|--------------|----------|--------|
| Delegated Regulation (EU) 2022/30; EN 18031-1 | Network protection: access control, authentication, secure update, secure storage and communication | SYS-004, SYS-013, SYS-016, SYS-029, SYS-034, SYS-035 | TC-004, TC-013, TC-016, TC-029, TC-034, TC-035 | gap analysis to write | Open |
| EN 18031-2 | Protection of personal data | not applicable by design | -- | statement to write | Open |
| EN 18031-3 | Protection from fraud | not applicable | -- | statement to write | Open |

### 2.5 Art. 10 and 17 to 21: marking, information, documentation

| Reference | What must be met | Requirement | Verification | Evidence | Status |
|-----------|------------------|-------------|--------------|----------|--------|
| RED Art. 10(6), (7), 19, 20; WEEE Art. 14; GPSR Art. 9 | CE marking, type and serial number, manufacturer name and address, crossed-out bin | SYS-048, HW-020 | TC-048, TC-220; HWC-005 | `technical-file/06-user-information-and-labelling/labelling-and-user-information.md` (item list) | Open (manufacturer not decided; spike board has no identification, DEV-007) |
| RED Art. 10(8), (9), (10) | Instructions, frequency band and power, declaration of conformity with each unit | SYS-048 | TC-048 | as above | Open |
| RED Art. 21, Annex V | Technical documentation | -- | review | `technical-file/INDEX.md` | Open |
| RED Art. 18, Annex VI | EU declaration of conformity | -- | review | `technical-file/09-declaration-of-conformity/DoC-template.md` | Open |

## 3. Cyber Resilience Act (EU) 2024/2847 (for units placed on the market from 11 December 2027)

Detail and gaps per clause: `technical-file/05-cybersecurity/cra-annex-i-mapping.md`.

### 3.1 Annex I Part I: properties of the product

| Reference | What must be met | Requirement | Verification | Evidence | Status |
|-----------|------------------|-------------|--------------|----------|--------|
| Part I (1); Art. 13(2), (3) | Cybersecurity based on a risk assessment | SYS-013, SYS-016, SYS-034, SYS-043 | review | risk register; risk assessment section 4.4 (summary only) | Open |
| (2)(a) | No known exploitable vulnerabilities | SW-012, SYS-045 | TC-112, TC-045; SWC-006, SWC-007, SWC-008 | CI artefact `sw-static` | Partial (static analysis of the gate firmware only) |
| (2)(b) | Secure by default; reset to the original state | SYS-013, SYS-039, SYS-041 | TC-013, TC-039, TC-041; SWC-003 | CI log | Open |
| (2)(c) | Security updates, automatic by default with an opt-out | SYS-029 | TC-029 | -- | Open (automatic-update default not specified) |
| (2)(d) | Protection from unauthorised access | SYS-004, SYS-016, SYS-039 | TC-004, TC-016, TC-039; SWC-003 | -- | Open |
| (2)(e), (f) | Confidentiality and integrity of stored and transmitted data and of the firmware | SYS-034, SYS-035, SYS-043, SYS-029 | TC-034, TC-035, TC-043, TC-029 | -- | Open (prototype flash not protected, RISK-013) |
| (2)(g) | Data minimisation | no requirement; no logs leave the device | SWC-001 | statement to write | Open |
| (2)(h), (i) | Availability and resilience; no negative impact on other devices | SYS-005, SYS-027, SYS-033, SW-001, SW-002, SW-003 | TC-005, TC-027, TC-033, TC-101, TC-102, TC-103 | -- | Open |
| (2)(j) | Limited attack surface, including external interfaces | SYS-012, SW-011, SYS-043 | TC-012, TC-111, TC-043; SWC-001, HWC-009 | CI artefacts `sw-static`, `hw-compliance.json` | Partial (policy check runs; production debug state not decided) |
| (2)(k) | Exploitation mitigation | SW-011 | TC-111; SWC-002 | CI artefact `sw-static` | Open (5 hardening options not set in the gate firmware) |
| (2)(l) | Recording of security-relevant events | no requirement yet | -- | -- | Open (gap) |
| (2)(m) | Secure removal of data and settings | SYS-041 | TC-041 | -- | Open |

### 3.2 Annex I Part II: vulnerability handling; Art. 13, 14; Annex II

| Reference | What must be met | Requirement | Verification | Evidence | Status |
|-----------|------------------|-------------|--------------|----------|--------|
| Part II (1) | Components identified; machine-readable SBOM | SYS-044 | TC-044; SWC-009, SWC-004, SWC-005 | CI artefact `sw-static/spdx/` | Partial (SPDX is generated; licence data and the target build are open) |
| Part II (2), (4), (7), (8) | Fix and distribute security updates; publish fixed vulnerabilities | SYS-045, SYS-029 | TC-045, TC-029 | `technical-file/05-cybersecurity/vulnerability-handling.md`, `key-management.md` (Draft) | Open |
| Part II (3) | Regular tests and reviews | SW-003, SW-012 | TC-103, TC-112; SWC-006, SWC-007 | CI artefact `sw-static` | Partial |
| Part II (5), (6) | Disclosure policy and contact | SYS-045 | TC-045 | `SECURITY.md` | Partial |
| Art. 13(8) | Support period of at least 5 years, stated to the user | SYS-045, SYS-048 | TC-045, TC-048 | -- | Open |
| Art. 14 | Reporting of exploited vulnerabilities and severe incidents (24 h, 72 h, final report) | no requirement (organisational) | review | procedure to add to `vulnerability-handling.md` | Open |
| Art. 13(18), Annex II | User information | SYS-048, SYS-024 | TC-048, TC-024 | item list (Draft) | Open |
| Art. 31, Annex VII | Technical documentation | -- | review | `technical-file/INDEX.md` | Open |

## 4. Substances, waste and general product safety

| Reference | What must be met | Requirement | Verification | Evidence | Status |
|-----------|------------------|-------------|--------------|----------|--------|
| RoHS Art. 4, 7; EN IEC 63000 | Restricted substances below the limits; technical documentation per part | HW-019, HW-008 | TC-219, TC-208; HWC-006, HWC-007, HWC-008 | `hw/compliance/materials.yaml`; `technical-file/07-supplier-declarations/` | Open (0 of 33 part numbers declared) |
| REACH Art. 33; SCIP | Information on Candidate List substances above 0.1 % | HW-019 | TC-219; HWC-007 | as above | Open |
| WEEE Art. 14; EN 50419 | Marking and user information; producer registration | SYS-048 | TC-048 | -- | Open |
| GPSR Art. 9 | Risk analysis, identification, instructions, complaint handling | SYS-048 | TC-048 | risk assessment (Draft) | Open |
| PPWR (EU) 2025/40 | Packaging requirements and registration | no requirement (organisational) | review | -- | Open |

## 5. Consistency of this matrix

| Reference | What must be met | Requirement | Verification | Evidence | Status |
|-----------|------------------|-------------|--------------|----------|--------|
| Regulatory README section 1 | Matrix complete and consistent with the requirements and the rule catalogue | -- | DOC-001 | CI log (python-tools) | Automated |

## 6. Summary

| Status | Rows |
|--------|------|
| Covered | 0 |
| Partial | 6 |
| Open | 42 |
| Automated (process row) | 1 |

## 7. History

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-11-03 | First rows from the system design |
| 0.2 | 2026-11-10 | Rows for every requirement with a regulatory reference; automated rules |
| 0.3 | 2026-11-10 | One table per act and article; safety rows for fire, materials, touch temperature, mounting, flash rate and exposure; CRA rows per clause; status vocabulary defined |
