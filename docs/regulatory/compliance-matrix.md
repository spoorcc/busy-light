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
