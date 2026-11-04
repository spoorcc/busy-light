# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Scope: the changelog covers the product as a whole (software, hardware, mechanical and user-visible documentation).
Hardware and mechanical revisions are named in the entries (for example "hardware rev A").

## [Unreleased]

### Added
- ADR-0015 (licensing corrected and completed) and ADR-0016 (independent hardware gate for the high current step) Accepted by the owner 2026-11-04; ADR-0013 and ADR-0009 are Superseded. Applied: `.claude/` under Apache-2.0, `NOTICE` file, SPDX headers on code files, `LICENSE.md` with the purchased-unit grant, the non-commercial reading, name, patents and authorship points (not legal advice).
- Options sheet for the back layout (five options with the accessory mounted); `scripts/check_license_map.py` (fails when a code file falls under the documentation licence, in CI); HW-003 and HW-010 drafted for the CC detection IC gate of ADR-0016; NEED-012 renamed with an acceptance criterion. Owner instruction to follow the recommended options recorded in ADR-0015 and ADR-0016 (status stays Proposed).
- Review actions: spike report on the layout of the back (annular bayonet proposed; spike code on `spike/mech-back-layout`), ADR-0015 (licensing corrected and completed; would supersede ADR-0013), ADR-0016 (independent hardware gate for the high current step; recommends a CC detection IC ANDed with the firmware GPIO).
- Goldfish reviews RV-005 (ADR-0013 licensing), RV-006 (ADR-0009 and ADR-0010 USB power) and RV-007 (ADR-0014 and the orientation and mounting requirements); RISK-035 to RISK-041; outside contributions paused until the contributor terms have a legal check; REUSE code globs extended.
- Diagram check (`scripts/build_diagrams.sh --check`) compares structure, labels and colours, not coordinates, because text widths depend on the machine's font metrics (`scripts/svg_normalize.py`, with tests).
- Diagrams use an explicit font (Noto Sans) and CI installs it, so box sizes do not depend on the machine's default font.
- README gallery: architecture block diagram, stand-in KiCad board render and placeholder housing concept preview (image of the mechanical spike under `docs/verification/reports/images/`).
- CI docs job: PlantUML 1.2026.8 pinned by SHA-256 (the Ubuntu package draws differently); block diagram uses the built-in layout engine so Graphviz versions cannot change it.
- Draft requirements NEED-020 to NEED-022 (orientation, clock mode later, mounting), SYS-047, HW-011, MECH-007, MECH-008 and test-case stubs TC-047, TC-211, TC-307, TC-308; MECH-006 rewritten for the label on the back.
- ADR-0014 (mounting interface on the back; Proposed: printed bayonet, fallback dovetail). Owner decisions recorded 2026-11-04: unit mounted horizontal and vertical, label on the back, orientation sensor added, clock mode in a later release.
- Goldfish review RV-004 of plan 05 and ADR-0011 (housing): not ready for approval; 30 findings with resolutions and owner decisions listed. Plan 05 section 3 scores corrected to the ADR values.
- CI fixes after the first GitHub run: npm lockfile for the diagram tools, root user in the KiCad container, pinned FreeCAD AppImage, virtual environment for the software job.
- Risk register: RISK-027 to RISK-030 (hardware current limit band, 5 V rail collapse, limit step stuck high, limit switch availability) from ADR-0010.
- Continuous integration (`.github/workflows/ci.yml`): documentation checks, Python tool checks, hardware (`scripts/ci_hw.sh`), mechanical (`scripts/ci_mech.sh`) and software (`scripts/ci_sw.sh`) jobs; `pyproject.toml` for the tool environment. Hardware and mechanical jobs report NOT RUN until sources exist.
- README rewritten as a project front page (honest status, planned features, roadmap); licences added: Apache-2.0 for code, CC BY-NC-SA 4.0 for documentation, hardware and mechanics (`LICENSE.md`, `LICENSES/`, `REUSE.toml`, `reuse lint` in CI); ADR-0013 (licensing, Accepted by the owner 2026-11-04); draft contribution terms in `CONTRIBUTING.md`.
- ADR-0012 (hardware design flow, Proposed) with goldfish review RV-003, a KiCad feasibility spike report (Draft) and RISK-032 to RISK-034.

### Changed
- Zephyr pin in `sw/west.yml` moved from v4.2.0 to v4.5.0 (owner approval 2026-11-03).

### Added
- FreeCAD spike model results (branch `spike/mech-concept`, not merged): skirt fixed, module offset 1.0 mm gives about 15 mm antenna clearance, USB-C variant V1 (board tab) passes all checks at 57.43 mm.
- RISK-031: the FreeCAD spike model shows the USB-C receptacle collides with the LED ring; options listed in the owner guide.
- Mechanical plan 05 revised (Draft): label on the underside and a flat-lying unit assumed (owner confirms), housing 53.0 x 16.5 mm with PCB 46 mm, antenna rules split between MECH-003 and an ADR-0003 finding; analysis re-run in the concept report (section 8).
- Draft mechanical plan 05, ADR-0011 (housing concept: opaque base plus translucent lid, FDM, PLA excluded) and the concept analysis report (light, thermal, tolerance); no CAD yet.
- Owner input recorded: read USB-C CC with the ADC (ADR-0009) and have a hardware current limit; draft HW-010 and TC-210; ADR-0004 item 4 updated.
- ADR-0010 (Proposed): hardware current limit on the USB input, recommends TPS2553 with a firmware-switched limit resistor (HW-010).
- Draft RISK-024..026 from ADR-0009; ADR-0009 summarised in the owner guide.
- Draft ADR-0009 (Proposed): USB-C power input and detection of the advertised source current; ADC read of the CC lines recommended, dedicated CC IC as fallback; cap value and ADC-or-IC choice left to the owner (SYS-020, HW-003).
- Power budget addendum for 900 and 1350 mA limits; SYS-001 rationale notes that the brightness figure depends on the source's current.
- Owner decision recorded: allow a higher USB current when the source advertises it (SYS-020, HW-003, ADR-0004, RISK-003); default stays [500] mA.
- PC prototype record for the ADR-0004 current limiter (scratchpad only): 41.7 M test frames without failure, 532 B code on rv32imc; proposals for level mode and the below-dark-current case noted in ADR-0004.
- PC prototype of the ADR-0005 extractor and mapper (scratchpad only): 27 tests, 5 million fuzz executions without crash, 4057 B and 512 B stack on rv32imc; document nesting limit and number wording added to SW-001 and ADR-0005 (Draft/Proposed).
- Spike 7.5 paper power budget with datasheet sources: at 500 mA the Wi-Fi TX peak leaves 46 mA (LDO) to 148 mA (buck) for 16 LEDs; USB current-limit decision added to the owner guide.
- Spike 7.1 E12 and E2b follow-up (build only): WPA2-Enterprise costs about +70 KB flash and +6 KB static RAM; the step-7 jump is flash padding; TLS heap can be reduced in builds that link.
- Draft vulnerability handling and disclosure process (`05-cybersecurity/vulnerability-handling.md`); contact and legal entity open.
- Owner review guide (`docs/plans/04-owner-review-guide.md`): approvals waiting, open decisions with recommendations, findings so far, side effects.
- Spike 7.1 E2b size ladder (build only): throw-away product-like image is 792 KB signed (43 % of the default slot), static RAM 285 KB of 360 KB; flash looks less critical than RAM.
- ADR-0007 evidence update and RISK-023: secure boot and flash encryption are not available in the Zephyr sysbuild MCUboot for the C3; the standalone Espressif port with a pinned ESP-IDF HAL is the only route found (owner decision pending).
- Draft spike 7.1 runbook for the first hardware session (read-only kit checks, flashing the two E1 images, log format); not run.
- Consistency pass over ADRs, key-management draft, SYS-036, RISK-006/008/009 and the spike reports (stale text and contradictions fixed after a fresh-reviewer check).
- Consistency pass over plans 02/03, ADR headers and spike reports.
- Spike 7.1 E2a paper flash budget: default 4 MB layout leaves 128 KiB unassigned; image limit at 75 % of a slot is about 1.31 MiB (1.38 MiB with unused areas reclaimed).
- Chip revision >= v0.3 (secure boot) added to HW-008 and ADR-0007; virtual-eFuse rehearsal noted in ADR-0007 and RISK-022.
- Spike 7.1 E11a partial record: ECDSA P-256 build works (bootloader 5 KB smaller than RSA-2048); virtual eFuse option and ESP32-C3 revision >= v0.3 requirement for secure boot found in source; secure boot and encryption not yet built.
- Spike 7.1 E1 build record: hello_world and Wi-Fi shell build for `esp32c3_devkitm` with Zephyr v4.5.0 and SDK 1.0.1 (build only; nothing flashed or run); default 4 MB flash layout and default signing key noted.
- Desk-survey findings applied to the Proposed ADR-0004, 0006, 0007, 0008 and the key-management draft: SPI LED route, radio-first rule for keys and passphrases, PSA key handling, one-client access point, RSA-3072 secure-boot key vs EC256 release key, flash `write-block-size` and swap-mode checks.
- Owner decision recorded: a lost or leaked release key means a recall of locked units (no second key in the bootloader); ADR-0007, key-management document and RISK-006 updated.
- Spike 7.1 E0 pass 2: Zephyr v4.5.0 source read (AP+STA in the driver, WPA2-Enterprise mapped to the Espressif blob, SPI LED route, hardware random source needs the radio on, EC256 signing fits secure boot plus encryption).
- Spike 7.1 E0 desk survey report (documentation only, nothing built): ROM secure boot signs the bootloader with RSA-3072, only an SPI `ws2812` route found for the LEDs, AP+STA, captive-portal DNS and WPA2-Enterprise unconfirmed on the C3.
- Goldfish review RV-002 of plan 03 (spike 7.1); plan 03 revised: desk survey E0, split E2/E11, power experiment E14, secrets handling, kit accounting and evidence rules.
- Draft plan 03 for spike 7.1 (Zephyr on ESP32-C3): 13 experiments with pass rules and fallbacks, shopping list, branch and report rules.
- Draft hardware requirements HW-001..009 and mechanical requirements MECH-001..006 with test case stubs TC-201..209 and TC-301..306 (no CAD work done; values in brackets are proposals).
- Goldfish readiness pass recorded in RV-001: verdict NO-GO with ranked blockers; plan 02 header and ARCH note brought up to date.
- Draft key-management document (`docs/regulatory/technical-file/05-cybersecurity/key-management.md`): key inventory, signing rules, production steps, rotation and recovery; owner review pending.
- Draft requirements SYS-043 (secure boot and flash encryption), SYS-044 (SBOM), SYS-045 (vulnerability handling, 5-year support), SYS-046 (recovery of locked units), SW-001..004 (input limits, session limit, fuzz tests, image confirmation) with test case stubs TC-043..046 and TC-101..104; SYS-026 now says what the 25 % margin refers to.
- Owner input on market (EU), distribution (open source first, sellable later), support period (5 years) and security (secure boot and flash encryption wanted) recorded in the regulatory applicability, ADR-0007 (revised to a staged secure boot and flash encryption plan, still Proposed) and RISK-022.
- Risk register with 21 draft risks (RISK-001..021), architecture blocks ARCH-001..019 in `docs/architecture/blocks.md`, and a first regulatory applicability assessment with open compliance questions and draft compliance-matrix rows (none verified, owner has not reviewed).
- Project structure for Zephyr software (`sw/`), KiCad hardware (`hw/`) and FreeCAD mechanics (`mech/`).
- Engineering process: lifecycle with gates, Elephant-Goldfish planning, document control, verification strategy.
- Standards: C coding (CERT C and MISRA C subset), hardware and mechanical design-for-X, writing (ASD-STE100 based), diagrams as code.
- Regulatory scaffolding for EU market access: applicability assessment, compliance matrix, technical-file index.
- Traceability check (`scripts/check_traceability.py`), documentation style check (`scripts/check_docs_style.py`), diagram build (`scripts/build_diagrams.sh`).
- Stakeholder needs (NEED-001 to NEED-019) and draft system requirements (SYS-001 to SYS-031) for the first release:
  Jenkins status by push and by REST polling, 16-LED RGB ring, Wi-Fi provisioning with web interface, OTA update,
  user-uploaded CA certificates, per-unit password, 3D printed housing.
- Draft user documentation skeleton, `CONTRIBUTING.md` and `SECURITY.md`.
- System design plan 02 with ADR-0002 to ADR-0008 (platform ESP32-C3, antenna, LED drive, mapping model, provisioning, update and boot security, transport protection) and goldfish review record RV-001. All ADRs are Proposed (ADR-0007 was Accepted and set back by the owner after the review).
- Draft system requirements SYS-032 to SYS-042 (level display, push liveness, LAN transport protection, own certificate, WPA2-Enterprise headroom, PC simulation, Wi-Fi range, web password rules, push request format, factory reset scope, device name) with test case stubs.
- Claude Code project instructions and skills (`CLAUDE.md`, `.claude/skills/`).
