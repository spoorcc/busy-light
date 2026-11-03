# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Scope: the changelog covers the product as a whole (software, hardware, mechanical and user-visible documentation).
Hardware and mechanical revisions are named in the entries (for example "hardware rev A").

## [Unreleased]

### Added
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
