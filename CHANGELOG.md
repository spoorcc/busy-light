# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Scope: the changelog covers the product as a whole (software, hardware, mechanical and user-visible documentation).
Hardware and mechanical revisions are named in the entries (for example "hardware rev A").

## [Unreleased]

### Changed
- Zephyr pin in `sw/west.yml` moved from v4.2.0 to v4.5.0 (owner approval 2026-11-03).

### Added
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
