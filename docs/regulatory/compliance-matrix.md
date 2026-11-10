# Compliance Matrix

- **Status:** Draft

Maps every applicable legal requirement or standard clause to a project requirement and evidence. No row may stay
uncovered at the release gate. Example row format:

| Legal / standard reference | Requirement (what must be met) | Project requirement ID | Verification (TC) | Evidence file | Status |
|----------------------------|--------------------------------|------------------------|-------------------|---------------|--------|
| CRA Annex I Part I (2)(a) | No known exploitable vulnerabilities at placing on market | SW-000 | TC-000 | `technical-file/05-cybersecurity/...` | Open |
| CRA Annex I Part II (1) | SBOM in machine-readable format | SW-000 | TC-000 | `technical-file/05-cybersecurity/sbom/` | Open |
| EMCD Annex I 1(a) | Emissions limited so radio/telecom equipment can operate as intended | HW-000 | TC-000 | test report | Open |
| RoHS Art. 4 | No restricted substances above limits | HW-000 | -- (supplier declarations) | `07-supplier-declarations/` | Open |

## Rows from the system design (author's first draft, 2026-11-03; none verified, no evidence exists yet)
Legal clause numbers marked *(verify)* are from memory and must be checked against the legal text. Requirements are Draft.

| Legal / standard reference | Requirement (what must be met) | Project requirement ID | Verification (TC) | Evidence file | Status |
|----------------------------|--------------------------------|------------------------|-------------------|---------------|--------|
| CRA Annex I Part I (2)(b) *(verify)* | Secure by default configuration, no default password | SYS-013, SYS-016, SYS-039 | TC-013 | -- | Open |
| CRA Annex I Part I (2)(c) *(verify)* | Security updates, automatic where applicable | SYS-029 | TC-029 | -- | Open |
| CRA Annex I Part I (2)(d) *(verify)* | Protection from unauthorised access (authentication, access control) | SYS-004, SYS-016, SYS-039 | TC-004, TC-016, TC-039 | -- | Open |
| CRA Annex I Part I (2)(e), (f) *(verify)* | Confidentiality and integrity of stored and transmitted data | SYS-034, SYS-035, SYS-013, SYS-043 | TC-034, TC-035, TC-043 | -- | Open (prototype flash not protected, RISK-013) |
| CRA Annex I Part I (2)(h)-(j) *(verify)* | Minimise attack surface, resilience, limit impact of an incident | SYS-005, SYS-012, SYS-027, SW-001, SW-002, SW-003 | TC-005, TC-012, TC-027, TC-101, TC-102, TC-103 | -- | Open |
| CRA Annex I Part II (1) *(verify)* | SBOM in machine-readable format | SYS-044 | TC-044 | `technical-file/05-cybersecurity/sbom/` | Open |
| CRA Annex I Part II (2)-(8) *(verify)* | Vulnerability handling, disclosure policy, contact, update distribution | SYS-045 | TC-045 | `technical-file/05-cybersecurity/` | Open |
| RED Art. 3(3)(d), (e), (f) / DA 2022/30 *(verify)* | Network protection, personal data and privacy, fraud protection | SYS-013, SYS-016, SYS-034, SYS-035 | TC-013, TC-034 | -- | Open |
| EN 18031-1 *(verify harmonisation)* | Internet-connected radio equipment: cyber essential requirements | SYS-004, SYS-013, SYS-016, SYS-029, SYS-034, SYS-035 | -- | gap analysis to write | Open |
| RED Art. 3(2) / EN 300 328 *(verify)* | Efficient use of the 2.4 GHz spectrum | SYS-038 | TC-038 (range only; radio test is separate) | module test report plus product test | Open |
| RED Art. 3(1)(a) / EN 62368-1, EN 62311 *(verify)* | Safety and RF exposure | SYS-020, SYS-028 | TC-020 | -- | Open |
| RED Art. 3(1)(b) / EN 301 489-1, -17 *(verify)* | EMC | none yet (HW requirement to write) | -- | test report | Open |
| EN 62471 | Photobiological safety of the LED ring | SYS-001, SYS-020 | TC-001, TC-020 | `technical-file/03-risk-and-safety/` | Open, assessment after spike 7.5 |
| RoHS Art. 4, REACH Art. 33, WEEE | Substances, SVHC information, marking | none yet | -- | `technical-file/07-supplier-declarations/` | Open |
| CRA Art. 13 / Annex II *(verify)* | User information incl. support period | SYS-024 (manual requirement missing) | -- | `technical-file/06-user-information-and-labelling/` | Open |

## Status notes of 2026-11-10 (assistant; from secondary sources, the official texts could not be opened, see `technical-file/04-standards-and-testing/standards-list.md`)
- RED Art. 3(3)(d), (e), (f) cybersecurity: Delegated Regulation (EU) 2022/30 applies from 1 August 2025 and is repealed with effect from the date the CRA applies in full (11 December 2027) by Delegated Regulation (EU) 2026/339 *(verify)*. Units placed on the market before that date: RED cyber rows above apply (EN 18031-1, harmonised with a restriction on password-less use, Implementing Decision (EU) 2025/138 *(verify)*). Units placed on the market after it: the CRA rows apply.
- CRA reporting duty (Art. 14, actively exploited vulnerabilities and severe incidents) applies from 11 September 2026 to products already on the market *(verify)*. No unit is on the market yet (applicability, owner answer of 2026-11-03).
- No CRA harmonised standard was cited in the Official Journal as of the sources read *(verify)*.

## Rows added 2026-11-10 (assistant; requirements are Draft unless stated; "HWC-/SWC-" are automated rules of `automated-checks.md`)

| Legal / standard reference | Requirement (what must be met) | Project requirement ID | Verification (TC) | Evidence file | Status |
|----------------------------|--------------------------------|------------------------|-------------------|---------------|--------|
| RED Art. 3(1)(b) / EN 301 489-1, -17, EN 55032, EN 55035 *(verify)* | EMC: emission limits and immunity | SYS-049 | TC-049 | test report (none yet) | Open (replaces the "none yet" row above) |
| RED Art. 3(1)(b) / EN 61000-4-2 via EN 301 489-1 *(verify)* | ESD clamp on every external interface net | HW-018, HW-003 | TC-218, TC-203; HWC-001, HWC-002 | CI artefact `hw-compliance.json` | Open (spike: CC1, CC2 without clamp, DEV-007) |
| RED Art. 3(2) / EN 300 328 *(verify)* | Radio performance not degraded by the board around the module antenna | HW-005 | TC-205 | module test report plus product test | Open |
| RED Art. 3(1)(a) / EN 62368-1 *(verify)* | Current limit and fault behaviour of the USB input (energy source class, fire) | HW-010 | TC-210 | -- | Open |
| RED Art. 3(1)(a) / EN 62368-1 *(verify)* | Temperature of parts and accessible surfaces in the closed housing | HW-013, MECH-005 | TC-213, TC-305 | -- | Open |
| RoHS Art. 4, 7 / EN IEC 63000; REACH Art. 33 *(verify)* | Restricted substances; SVHC information; technical documentation per part | HW-008, HW-019 | TC-208, TC-219; HWC-006, HWC-007, HWC-008 | `07-supplier-declarations/`, `hw/compliance/materials.yaml` | Open (0 of 33 part numbers declared) |
| RED Art. 10(6), GPSR Art. 9 *(verify)* | Type, batch or serial identification | HW-020, SYS-048 | TC-220, TC-048; HWC-005 | -- | Open (spike: no board text, DEV-007) |
| RED Art. 10, 17-19; WEEE Art. 14 / EN 50419; GPSR Art. 9; CRA Art. 13, Annex II *(verify)* | CE marking, WEEE symbol, manufacturer, frequency band and power, user information, support end date | SYS-048, SYS-045 | TC-048, TC-045 | `06-user-information-and-labelling/labelling-and-user-information.md` | Open (manufacturer not decided) |
| CRA Annex I Part I (2)(j), (k) *(verify)* | Limit attack surface; exploitation mitigation in the firmware configuration | SW-011 | TC-111; SWC-001, SWC-002 | CI artefact `sw-static` | Open (5 hardening options not set in the gate firmware) |
| CRA Annex I Part I (2)(a), Part II (3) *(verify)* | No known exploitable defects; regular tests and reviews | SW-012, SW-003 | TC-112, TC-103; SWC-006, SWC-007, SWC-008 | CI artefact `sw-static` | Open |
| CRA Annex I Part I (2)(b), (d); EN 18031-1; ETSI EN 303 645 5.1 *(verify)* | No hard-coded or universal default credentials | SYS-013, SYS-039 | TC-013, TC-039; SWC-003 | CI log (python-tools) | Open (scan clean on 2026-11-10; no product credentials exist yet) |
| CRA Annex I Part II (1) *(verify)* | SBOM; control of build-tool supply chain | SYS-044 | TC-044; SWC-009, SWC-004, SWC-005 | CI artefact `sw-static/spdx/` | Open (SPDX made; licence fields empty in the local run, see TC-112 notes) |
| CRA Annex I Part I (2)(j); SYS-043 *(verify)* | Debug and programming access disabled or protected in production units | SYS-043 | TC-043; HWC-009 (inventory) | CI artefact `hw-compliance.json` | Open (USB-Serial-JTAG, EN and BOOT test points listed) |
| Regulatory README 1 | Compliance matrix consistent and complete | -- | DOC-001 | CI log (python-tools) | Automated |
