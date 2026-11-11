# CRA Annex I mapping (essential cybersecurity requirements)

- **Status:** Draft (assistant, 2026-11-10; not reviewed)
- **Applies:** to units placed on the market from 11 December 2027; the reporting duty of Art. 14 applies from 11 September 2026 *(verify)*. Before 11 December 2027 the RED cyber rules apply instead (`../04-standards-and-testing/standards-list.md` section 4).
- **Product class:** default; conformity route: internal control *(verify)*.

The clause letters below are as the author remembers the regulation text; check each one against the Official Journal text (the session could not open eur-lex.europa.eu) *(verify)*. "Automated" names a rule of `../../automated-checks.md`. A clause is covered only when its evidence column names an existing file; none is covered today.

## Part I: properties of the product

| Clause | Requirement (short) | Project requirements | Automated | Evidence today | Gap |
|--------|---------------------|----------------------|-----------|----------------|-----|
| (1) | Level of cybersecurity based on the risks | SYS-013, SYS-016, SYS-034, SYS-043 | -- | risk register entries (RISK-013 and others) | no cyber risk assessment document per Art. 13(2); write it per release |
| (2)(a) | No known exploitable vulnerabilities at placing on the market | SW-012, SYS-045 | SWC-006, SWC-007 | static analysis of the gate firmware only | dependency vulnerability check of the Zephyr version and the Wi-Fi blobs against advisories before each release |
| (2)(b) | Secure by default configuration, with a reset to the original state | SYS-013, SYS-039, SYS-041 | SWC-001, SWC-003 | -- | per-unit passphrase (ADR-0006) not implemented |
| (2)(c) | Vulnerabilities fixed by security updates; automatic updates by default with an opt-out | SYS-029, ADR-0007 | -- | -- | automatic-update default and user opt-out not specified in SYS-029 |
| (2)(d) | Protection from unauthorised access (authentication, identity and access management) | SYS-004, SYS-016, SYS-039 | SWC-003 | -- | -- |
| (2)(e) | Confidentiality of stored and transmitted data (encryption) | SYS-034, SYS-035, SYS-043 | -- | -- | prototype flash not encrypted (RISK-013); secure boot and flash encryption before sale (owner answer 2026-11-03) |
| (2)(f) | Integrity of data, programs and configuration | SYS-029, SYS-043 | -- | -- | signed images (MCUboot) not yet in the build (SWC-002 report) |
| (2)(g) | Data minimisation | applicability item 10 | SWC-001 (no network log backend) | -- | written statement of the data the device stores |
| (2)(h) | Availability of essential functions, resilience against denial of service | SYS-005, SYS-027, SW-001, SW-002 | -- | -- | -- |
| (2)(i) | Minimise negative impact on other devices and networks | SYS-033, SW-002 | -- | -- | -- |
| (2)(j) | Limit attack surfaces, including external interfaces | SYS-012, SW-011, SYS-043 | SWC-001, HWC-009 | HWC-009 inventory (USB-Serial-JTAG, EN, BOOT test points) | production state of USB-Serial-JTAG and the ROM download mode not decided |
| (2)(k) | Reduce the impact of an incident (exploitation mitigation) | SW-011 | SWC-002 | -- | 5 hardening options not set in the gate firmware |
| (2)(l) | Security-relevant information by recording and monitoring internal activity, with an opt-out | -- | -- | -- | no requirement yet: security event log (failed logins, update results) to write |
| (2)(m) | Secure and easy removal of all data and settings | SYS-041 | -- | -- | -- |

## Part II: vulnerability handling (manufacturer process)

| Clause | Requirement (short) | Project requirements | Automated | Evidence today | Gap |
|--------|---------------------|----------------------|-----------|----------------|-----|
| (1) | Identify and document components and vulnerabilities, including a machine-readable SBOM | SYS-044 | SWC-009, SWC-004, SWC-005 | SPDX from `west spdx` in CI (artefact `sw-static`) | licence fields empty in the local run; Wi-Fi blob hashes not in the native_sim SBOM (no blobs there) |
| (2) | Fix vulnerabilities without delay; security updates separate from feature updates where possible | SYS-045 | -- | `vulnerability-handling.md` (Draft) | -- |
| (3) | Regular tests and reviews of security | SW-003, SW-012 | SWC-006, SWC-007 | -- | fuzz tests (SW-003) not written |
| (4) | Publish information on fixed vulnerabilities | SYS-045 | -- | -- | advisory channel not chosen |
| (5) | Coordinated vulnerability disclosure policy | SYS-045 | -- | `SECURITY.md`, `vulnerability-handling.md` | -- |
| (6) | Contact address for vulnerability reports | SYS-045 | -- | `SECURITY.md` | `security.txt` on the device web interface not specified |
| (7) | Secure distribution of updates | SYS-029, ADR-0007 | -- | `key-management.md` (Draft) | -- |
| (8) | Security updates without delay and free of charge, with advisory messages | SYS-045 | -- | -- | -- |

## Other CRA duties that touch the design

- Art. 13(8) support period: 5 years (owner, 2026-11-03), stated to the user at purchase (SYS-048).
- Art. 14 reporting: early warning in 24 h, notification in 72 h, final report for actively exploited vulnerabilities and severe incidents, through the ENISA single reporting platform *(verify)*; procedure to add to `vulnerability-handling.md`.
- Annex II user information and Annex VII technical documentation: `../06-user-information-and-labelling/labelling-and-user-information.md` and `../INDEX.md`.
