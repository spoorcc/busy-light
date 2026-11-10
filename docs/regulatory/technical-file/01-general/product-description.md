# General product description

- **Document:** Technical file section 01, general description
- **Status:** Draft
- **Version:** 0.1   **Date:** 2026-11-10
- **Author:** the assistant   **Owner / approver:** Ben Spoor (not reviewed)
- **Design state described:** concept and spike board (`hw/kicad/spike-gate`, not a product board); no product revision exists yet

This document describes the product for the technical file. It states only facts that exist in the requirements, the architecture and the accepted decisions, and names the source of each. Values in square brackets are working values that the requirements leave open. It is the common input of the applicability assessment (`../../applicability.md`), the risk assessment (`../03-risk-and-safety/risk-assessment.md`) and the test plan (`../04-standards-and-testing/conformity-test-plan.md`).

## 1. Identification

| Item | Value | Source |
|------|-------|--------|
| Product name | busy-light | repository |
| Type / model designation | not assigned | to decide before the first supply (SYS-048) |
| Hardware revision | none released; spike board only | `hw/kicad/spike-gate/board/` |
| Firmware version | none released; gate-logic firmware under development | plan 07 |
| Manufacturer (legal person, postal address) | not decided | applicability assessment, open decision D1 |
| Variants | one; accessories for the back mount are separate printed parts | NEED-022, ADR-0014 |

## 2. Intended use

The busy-light is a small status light for a desk. A ring of coloured LEDs shows the state of an external system, first of all the build status of a Jenkins server, so that people nearby see it at a glance (NEED-003 to NEED-006). The device receives its data over Wi-Fi, by events pushed to it or by polling a REST endpoint. The user sets it up through the device's own Wi-Fi access point and a web interface (NEED-001, NEED-002), and controls it with one button (NEED-008).

| Aspect | Description | Source |
|--------|-------------|--------|
| Users | Software teams now (professional users); non-technical people later (NEED-016). Because the product can reach consumers, the assessment treats it as a consumer product | NEED-016, applicability section 2 |
| Environment | Indoor, office or home, on a desk, or on a stand, clip or rack adapter; ambient up to [35] degC in the thermal requirements | NEED-022, HW-013 |
| Not intended for | Illumination of a room; outdoor or wet locations; safety signalling or any use where a wrong or missing indication can cause harm; use as a toy | this document; RISK-001 |
| Supply | A USB-C source that the user provides; no power supply and no cable are part of the product | SYS-020 |
| Expected lifetime | Support period of 5 years (owner, 2026-11-03) | SYS-045 |

## 3. Construction

| Part | Description | Source |
|------|-------------|--------|
| Housing | Two printed parts, a base and a translucent lid that is the diffuser; largest outer dimension [53] mm; PETG for the prototypes; the material for sold units is open | SYS-028, MECH-001, ADR-0011, MECH-010 |
| Back interface | Annular bayonet for a stand, clip, rack adapter or blank plate; no metal in the back | MECH-007, ADR-0014 |
| Board | One 4-layer board inside the housing, with the LED ring around the module | ADR-0003, ADR-0020 |
| Light source | Ring of [16] single-wire addressable RGB LEDs (WS2812B-2020 on the spike) | SYS-001, HW-001, ADR-0004 |
| Radio | Espressif ESP32-C3-MINI-1 module with its own PCB antenna, Wi-Fi in the 2.4 GHz band; Bluetooth is not used by any requirement | ADR-0002, ADR-0003 |
| User controls | One push button; a label on the base with the identifier and the unit passphrase | SYS-017, MECH-006, ADR-0006 |
| Sensor | Orientation sensor for the ring | HW-011, SYS-047 |

## 4. Electrical characteristics

| Characteristic | Value | Source |
|----------------|-------|--------|
| Supply | 5 V DC from USB-C, as a sink only; no Power Delivery negotiation | SYS-020, HW-003 |
| Input current | [500] mA by default; up to [1500] mA when the source advertises 1.5 A or more on the CC lines | SYS-020 |
| Input power | about 2.5 W by default, up to about 7.5 W at the top step (5 V times the current above) | derived |
| Hardware current limit | Load switch in the VBUS path with three steps; at most 1577 mA | HW-010, ADR-0016 |
| Internal rails | +5 V for the LEDs, 3.3 V for the module and logic | HW-004, ADR-0019 |
| Highest internal voltage | 5 V nominal; no converter raises the voltage | schematic of the spike board |
| Battery | none | NEED-015 (later release) |
| External ports | One USB-C receptacle (power; the data lines go to the module for programming and the production test) | HW-006 |

## 5. Radio characteristics

| Characteristic | Value | Source |
|----------------|-------|--------|
| Technology and band | Wi-Fi 4 (IEEE 802.11 b/g/n) in the 2.4 GHz band | ADR-0002; exact band edges and modes from the module test report (not read) |
| Maximum output power | to take from the module test report; EN 300 328 limits the e.i.r.p. to 20 dBm *(verify)* | open |
| Antenna | PCB antenna on the module; placement inside the LED ring with a keep-out | HW-005, ADR-0003 (DEV-004 open on the spike) |
| Module approvals | Espressif's RED test reports for the module, to obtain and file | `../07-supplier-declarations/` (none on file) |

## 6. Software and connectivity

| Aspect | Description | Source |
|--------|-------------|--------|
| Operating system | Zephyr RTOS, pinned release (v4.5.0 in the manifest) | `sw/west.yml` |
| Network functions | Wi-Fi station; own access point for provisioning; web interface on the device; push input; REST polling; no cloud service of the manufacturer | SYS-003, SYS-006, SYS-012, SYS-014 |
| Update | Firmware update over the network with signed images | SYS-029, ADR-0007 |
| Security functions | Per-unit passphrase, web login, transport protection, secure boot and flash encryption for units that leave the owner | ADR-0006, ADR-0008, SYS-043 |
| Data stored | Wi-Fi credentials, device name, source addresses and tokens, certificates; no personal data by design | applicability section 2 |

## 7. Documents that complete this description

Block diagram and interfaces: `docs/architecture/blocks.md`. Requirements: `docs/requirements/`. Decisions: `docs/decisions/`. Schematic, layout and drawings of a release: `hw/fabrication/<rev>/` and `mech/exports/<rev>/` (none yet). Photographs and the label drawing: to add with the first product revision.
